"""Saturation-weighted circular-mean HUE across a clip -- luma_drift's sibling.

WHY THIS EXISTS, and it is the same argument luma_drift.py opens with, one
channel over. On 2026-08-19 the beat-12 lane reported the shipped take's fault
as a hue swing of 40.24 degrees across the first second, and settled a rung on
it. That number was computed by a script nobody committed. luma_drift.py was
written the same week precisely because "two lanes measuring 'the same'
quantity two ways is how a recipe property and a beat property get confused" --
and then the colour half of the same verdict was left uninstrumented, so the
one number that names beat 12's shipped fault cannot be reproduced by anyone
who did not write it. This closes that.

WHAT IT MEASURES, precisely, because a mean hue is easy to compute wrongly:

  * HUE IS CIRCULAR. 359 and 1 degree are two degrees apart, not 358. An
    arithmetic mean over a wrap-around quantity is meaningless, so hue is
    averaged as a unit vector: mean of (cos h, sin h), then atan2 back. A clip
    whose hue is genuinely spread all the way round returns a near-zero
    resultant, and `concentration` below is what tells you that happened
    instead of leaving you to read a confident angle off nothing.

  * THE MEAN IS SATURATION-WEIGHTED. A grey pixel has a hue -- whatever
    rounding noise put in the two smallest channels -- and a frame is mostly
    grey-ish pixels. Weighting each pixel's unit vector by its HSV saturation
    is what makes the number describe the COLOUR in the frame rather than the
    noise floor of everything that has none. This is also why the beat-12
    verdict's phrase is "saturation-weighted circular-mean hue" and not "mean
    hue": the weighting is part of the definition, not an optimisation.

  * THE DOMAIN IS THE DECODED MP4, like luma_drift: what a viewer sees after
    the encoder's round trip, not what the sampler emitted. Every colour figure
    on the ladder was read off a published mp4 and a new instrument that
    measured PNGs would not be comparable to any of them.

  * SWING, NOT DRIFT. luma_drift reports first->last because brightness faults
    on this engine are ramps. Colour faults here are TRANSIENTS -- beat 12
    blooms in thirteen frames and then holds for a hundred and seven -- so a
    first->last figure would report this clip as almost clean. The headline
    here is therefore the MAXIMUM PAIRWISE SEPARATION over the sampled frames,
    which is what a transient shows up in, with first->last printed beside it
    so a ramp is still visible.

Same band convention as luma_drift (equal thirds by default, `--bands`), same
`--at` frame list, same `--json`. $0, no GPU, no network.

    python3 pipeline/hue_drift.py [--at 0,6,12,24] [--bands 3] clip.mp4 ...
    python3 pipeline/hue_drift.py --selftest
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hold_period import _ffmpeg, probe  # noqa: E402


def frames_rgb_native(path: str):
    """Every frame of the clip as a native-resolution uint8 RGB array."""
    w, h, _fps = probe(str(path))
    r = subprocess.run(
        [_ffmpeg(), "-v", "error", "-i", str(path), "-vsync", "0",
         "-vf", "format=rgb24", "-f", "rawvideo", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg failed on %s: %s"
                           % (path, r.stderr.decode("utf-8", "replace")[:400]))
    buf = np.frombuffer(r.stdout, dtype=np.uint8)
    n = buf.size // (w * h * 3)
    return buf[:n * w * h * 3].reshape(n, h, w, 3), w, h


def hue_sat(rgb: np.ndarray):
    """HSV hue in degrees and HSV saturation, for an (...,3) uint8 array."""
    a = rgb.astype(np.float64) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn
    h = np.zeros_like(mx)
    # Where d == 0 the hue is undefined; saturation is 0 there, so the weight
    # is 0 and the value never reaches the mean. Left at 0 deliberately.
    nz = d > 0
    ri = nz & (mx == r)
    gi = nz & (mx == g) & ~ri
    bi = nz & ~ri & ~gi
    h[ri] = (60.0 * ((g[ri] - b[ri]) / d[ri])) % 360.0
    h[gi] = 60.0 * ((b[gi] - r[gi]) / d[gi]) + 120.0
    h[bi] = 60.0 * ((r[bi] - g[bi]) / d[bi]) + 240.0
    s = np.zeros_like(mx)
    s[mx > 0] = d[mx > 0] / mx[mx > 0]
    return h, s


def mean_hue(rgb: np.ndarray):
    """(degrees, concentration) -- saturation-weighted circular mean.

    `concentration` is the resultant length in [0,1]. Near 1 the frame has one
    dominant hue and the angle means something; near 0 the colour is spread
    round the wheel and the angle is not worth reporting.
    """
    h, s = hue_sat(rgb)
    rad = np.deg2rad(h)
    wsum = float(s.sum())
    if wsum <= 0:
        return float("nan"), 0.0
    x = float((s * np.cos(rad)).sum()) / wsum
    y = float((s * np.sin(rad)).sum()) / wsum
    return math.degrees(math.atan2(y, x)) % 360.0, math.hypot(x, y)


def sep(a: float, b: float) -> float:
    """Shortest angular separation in degrees, 0..180."""
    d = abs(a - b) % 360.0
    return d if d <= 180.0 else 360.0 - d


def measure_clip(path: str, bands_rows: int, at_frames):
    frames, w, h = frames_rgb_native(path)
    n = len(frames)
    at = [f for f in at_frames if 0 <= f < n] or [0, n - 1]
    if n - 1 not in at:
        at.append(n - 1)
    whole = [(f,) + mean_hue(frames[f]) for f in at]
    edges = [round(h * i / bands_rows) for i in range(bands_rows + 1)]
    bands = []
    for i in range(bands_rows):
        lo, hi = edges[i], edges[i + 1]
        first = mean_hue(frames[at[0]][lo:hi])[0]
        last = mean_hue(frames[at[-1]][lo:hi])[0]
        bands.append((lo, hi, first, last, sep(first, last)))
    angles = [a for _, a, _ in whole if not math.isnan(a)]
    swing = max((sep(x, y) for i, x in enumerate(angles)
                 for y in angles[i + 1:]), default=0.0)
    return {"path": str(path), "frames": n, "w": w, "h": h,
            "whole": whole, "bands": bands,
            "swing_max_pairwise": swing,
            "swing_first_last": sep(whole[0][1], whole[-1][1]),
            "min_concentration": min((c for _, _, c in whole), default=0.0)}


def print_report(r: dict) -> None:
    print("=" * 78)
    print(os.path.basename(r["path"]))
    print("  %d frames, %dx%d" % (r["frames"], r["w"], r["h"]))
    print("  WHOLE  " + "  ".join(
        "f%03d %6.2f" % (f, a) for f, a, _ in r["whole"]))
    print("  WHOLE  max pairwise swing %6.2f deg   first->last %6.2f deg"
          % (r["swing_max_pairwise"], r["swing_first_last"]))
    for lo, hi, first, last, d in r["bands"]:
        print("  rows %-12s %7.2f -> %7.2f   %+6.2f"
              % ("%d-%d" % (lo, hi), first, last,
                 last - first if abs(last - first) <= 180 else d))
    print("  min concentration %.3f%s" % (
        r["min_concentration"],
        "   <- LOW: the angle is not trustworthy at this frame"
        if r["min_concentration"] < 0.15 else ""))


def selftest() -> int:
    # circular mean must wrap: 350 and 10 average to 0, not to 180.
    a = np.zeros((1, 2, 3), dtype=np.uint8)
    # hue 350 (red-magenta) and hue 10 (red-orange), both fully saturated.
    a[0, 0] = (255, 0, 42)
    a[0, 1] = (255, 42, 0)
    m, c = mean_hue(a)
    assert sep(m, 0.0) < 1.0, "circular mean wrapped wrong: %.2f" % m
    # 350 and 10 are 20 deg apart, so the resultant is cos(10 deg) = 0.985,
    # not 1.0. The bound is written from that arithmetic rather than from a
    # round number, because a threshold chosen to make a test pass measures
    # nothing.
    assert c > 0.98, "two near-identical hues must concentrate: %.3f" % c
    # a grey frame has no colour: weight 0 everywhere -> nan, not a confident 0.
    g = np.full((1, 4, 3), 128, dtype=np.uint8)
    m2, c2 = mean_hue(g)
    assert math.isnan(m2) and c2 == 0.0, "grey must not report a hue"
    # opposite hues cancel: the angle is meaningless and concentration says so.
    o = np.zeros((1, 2, 3), dtype=np.uint8)
    o[0, 0] = (255, 0, 0)      # 0 deg
    o[0, 1] = (0, 255, 255)    # 180 deg
    _, c3 = mean_hue(o)
    assert c3 < 0.01, "opposite hues must not concentrate: %.3f" % c3
    # separation is shortest-arc.
    assert abs(sep(359.0, 1.0) - 2.0) < 1e-9
    assert abs(sep(10.0, 200.0) - 170.0) < 1e-9
    print("hue_drift selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("clips", nargs="*")
    ap.add_argument("--bands", type=int, default=3)
    ap.add_argument("--at", default="0,24,48,72,96,120")
    ap.add_argument("--json")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.clips:
        ap.error("give at least one clip, or --selftest")
    at = [int(x) for x in a.at.split(",") if x.strip()]
    out = [measure_clip(c, a.bands, at) for c in a.clips]
    for r in out:
        print_report(r)
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=2, sort_keys=True)
        print("\nwrote %s" % a.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
