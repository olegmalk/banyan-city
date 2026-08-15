#!/usr/bin/env python3
"""How many frames does this clip hold each picture for? Autocorrelation, not parity.

Written 2026-08-15 to replace `cadence`, which was structurally incapable of
seeing the exact defect we have. The evidence is in
`pipeline/research/ltx23-motion-source.md` §4.1-4.2 (commit dfa87c27).

================================================================================
WHY THE OLD METRIC HAD TO GO -- THE ALIASING TABLE, KEPT HERE SO NOBODY
REINTRODUCES IT
================================================================================
`cadence` was the ratio of the mean per-pair luma difference on EVEN-indexed
pairs to the mean on ODD-indexed pairs. That is a parity-2 detector. Feed it a
synthetic series with one loud pair every N and it reads:

    true hold period   cadence reads
        2                26.67x
        3                 1.00x   <-- BLIND
        4                14.12x
        5                 1.00x   <-- BLIND
        6                 9.56x

Every ODD hold period aliases to exactly 1.00x by construction: the loud pairs
distribute evenly across both parities and the ratio is 1 no matter how frozen
the clip is. `1.00x` was documented as "every frame is new". It was not a noise
problem and not a tuning problem -- the metric could not represent a 3-frame
hold. On 2026-08-15 it reported **1.06x on a clip that holds every picture for
three frames** (ep2-b13-shade-cycle-s2-0815), and a lane read that as clean.
The aliasing table above is reproduced as an executable regression test in
`pipeline/test_pipeline.py` (`test_the_retired_parity_ratio_is_blind_to_odd_holds`)
precisely so this cannot come back quietly.

The same blindness is a known property of frame-difference metrics generally,
not our discovery: VBench's `temporal_flickering` is MAE between consecutive
frames and its README requires static videos be FILTERED OUT before scoring,
because stillness scores well on it. `subject_consistency` (DINO) and
`motion_smoothness` (AMT) both rate a frozen clip as excellent. "A respected
metric likes it" is not evidence of motion.

================================================================================
WHAT THIS MEASURES INSTEAD
================================================================================
Autocorrelation of the per-pair difference series. **The peak lag IS the hold
period**, for any period, odd or even, and it is scale-free -- it does not care
how loud the motion is, only how it repeats.

Estimator: r_k = sum_t (x_t - mu)(x_{t+k} - mu) / sum_t (x_t - mu)^2, the
standard biased estimator. Biased is what we want here: it decays as (N-k)/N,
so a harmonic (lag 6 of a period-3 hold) always reads BELOW its fundamental and
the peak lands on the true period rather than a multiple of it.

Validated read-only on our own clips, 2026-08-15:

    clip                   lag1    lag2    lag3    reading
    0815-b13-AFTER.mp4    -0.42   -0.41    0.97    clean period-3 hold
    0815-b13-BEFORE.mp4    0.20    0.28    0.61    weaker period-3
    0814-b10-candidate     0.16    0.88    0.13    period-2 hold

It is robust to scale: the lag-3 value moves 0.97 -> 0.96 between 352x640 and
88x160. That has a useful side effect. At 1/8 scale the 1-2px line-work churn on
anime line art -- fingers, cuffs, trouser folds re-forming in place -- stops
inflating the difference series. That churn is exactly what made frozen clips
look alive to the old metric AND to the eye on a contact sheet.

Cost: one ffmpeg pipe to grayscale rawvideo plus arithmetic. No model, no
optical flow, no GPU, ~1s, and it writes nothing to disk.

================================================================================
IT REPORTS A PERIOD, NOT A SCORE -- AND IT IS A FILTER, NEVER A VERDICT
================================================================================
"Holds every 3 frames" is checkable: open frames 40, 41, 42 and look. A bare
ratio is not. So the report always carries the period, how many DISTINCT
pictures that implies, and the effective frame rate, which is the number a
viewer actually experiences.

**A metric errs in both directions and is a filter, never a verdict. The cold
read decides.** This tool exists to stop a frozen clip from reaching a human as
"fine", not to pass anything on its own. A high strength on a clip that reads
well is a question to answer by looking, not a rejection; a low strength on a
clip that reads dead is likewise a question. On 2026-08-03 a fifteen-beat batch
was shipped on a steward's own metric and came back "literally just frozen
frames". A metric agreeing with the steward is not a sample.

Two things it cannot do, stated so nobody assumes otherwise:

  - It cannot tell a deliberate animation-on-twos from a sampler that froze.
    Period 2 or 3 is a FACT about the frames; whether it is a defect is taste.
  - It cannot see a clip that moves smoothly to the wrong place. Aperiodic
    wrongness has no peak lag. Strength near zero means "no periodic hold",
    which is not the same as "good".

    python3 pipeline/hold_period.py clip.mp4 [more.mp4 ...]
    python3 pipeline/hold_period.py --json out.json clip.mp4
    python3 pipeline/hold_period.py --scale 8 clip.mp4     # 1/8 is the default

Exit 0 always for a successful measurement, whatever the reading -- this is a
filter and a filter does not get to fail a build. Exit 1 only when a clip could
not be measured at all.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# --- classification bands -----------------------------------------------------
# Deliberately coarse. These are the boundaries between "go look at this first"
# and "look at this later", not between pass and fail. Calibrated on the three
# clips in the table above: 0.97 and 0.88 are unmistakable holds, 0.61 is the
# weaker period-3 that still reads as judder, and our aperiodic control sits
# under 0.30.
STRONG = 0.50   # at or above: the hold is the dominant structure of the clip
WEAK = 0.30     # at or above: periodic but not dominant; partial hold or a ramp
MAX_LAG = 12    # beyond ~12 a "period" is a scene rhythm, not a frame hold
MIN_PAIRS = 24  # fewer pairs than this and any lag estimate is noise


def autocorrelation(series, max_lag: int = MAX_LAG) -> dict:
    """{lag: r} for lag 1..max_lag, biased estimator, mean removed.

    Pure Python on purpose: this runs inside `test_pipeline.py`, which CI runs
    with pyyaml/pillow/markdown and no numpy. A hundred samples times twelve
    lags is nothing.
    """
    x = [float(v) for v in series]
    n = len(x)
    if n < 2:
        return {}
    mu = sum(x) / n
    dev = [v - mu for v in x]
    denom = sum(v * v for v in dev)
    if denom <= 0.0:
        return {}          # a perfectly constant series: see hold_period()
    out = {}
    for k in range(1, min(max_lag, n - 1) + 1):
        num = sum(dev[t] * dev[t + k] for t in range(n - k))
        out[k] = num / denom
    return out


def hold_period(series, max_lag: int = MAX_LAG, fps: float = 24.0) -> dict:
    """The hold period of a per-pair difference series, and what it implies.

    Returns a dict that always carries `period`, `strength`, `reading` and the
    full `lags` table, because the table is what lets a human check the call --
    a period-3 hold shows negative autocorrelation at lags 1, 2, 4 and 5, and a
    peak with no such comb around it is a different animal.

    `period` is None when the series is constant (nothing changed at all) or too
    short to judge. `period == 1` is never returned as a hold; a series with no
    periodic structure reports its peak lag with a `reading` that says so.
    """
    x = [float(v) for v in series]
    n = len(x)
    base = {"pairs": n, "period": None, "strength": None, "lags": {},
            "distinct_pictures": None, "effective_fps": None}

    if n < MIN_PAIRS:
        base["reading"] = ("only %d pairs: too short to judge a hold "
                           "(need %d)" % (n, MIN_PAIRS))
        return base
    if max(x) - min(x) <= 0.0:
        # Every pair identical. Usually every pair is 0.0 -- a clip that never
        # changed a pixel. That is the loudest possible finding and it has no
        # period, so it must not fall through to "no periodic hold".
        base["reading"] = ("FROZEN SOLID: every frame-to-frame difference is "
                           "identical (%.3f); there is no motion to have a "
                           "period" % x[0])
        return base

    lags = autocorrelation(x, max_lag)
    if not lags:
        base["reading"] = "no variation in the difference series"
        return base

    peak = max(lags, key=lambda k: lags[k])
    strength = lags[peak]

    # A true period-p hold also correlates at 2p, 3p...  The biased estimator
    # already puts the fundamental highest, but if noise ever lifts a harmonic
    # above it, prefer the smallest divisor that is within a hair of the peak:
    # the fundamental is the period a human would count by opening frames.
    for d in range(1, peak):
        if peak % d == 0 and lags.get(d, -1.0) >= strength - 0.05:
            peak, strength = d, lags[d]
            break

    base["lags"] = {k: round(v, 3) for k, v in lags.items()}
    base["strength"] = round(strength, 3)

    if peak <= 1:
        # The strongest lag is 1. That is not a repeat, it is the difference
        # series varying smoothly from pair to pair — which is what CONTINUOUS
        # motion looks like. Measured on our genuinely-moving clips
        # (0814-b01-candidate 0.88, 0815-b02-tree 0.85) against 0.96 at lag 3
        # on a frozen one, so this branch is a real discriminator and not a
        # fallthrough. It is still not a pass: see below.
        base["period"] = 1
        base["reading"] = ("no frame hold: the peak is lag 1 (%.2f), i.e. the "
                           "change varies smoothly pair to pair rather than "
                           "repeating. NOT a claim the motion is good — "
                           "aperiodic wrongness has no peak lag either."
                           % strength)
        return base

    if strength < WEAK:
        base["period"] = 1
        base["reading"] = ("no periodic hold (best lag %d at %.2f, under %.2f). "
                           "NOT a claim that the motion is good — aperiodic "
                           "wrongness has no peak lag." % (peak, strength, WEAK))
        return base

    base["period"] = peak
    base["distinct_pictures"] = round((n + 1) / float(peak), 1)
    base["effective_fps"] = round(fps / float(peak), 2)
    band = "HOLD" if strength >= STRONG else "PARTIAL HOLD"
    # Two caveats that must travel with the number, because both were live in
    # the 2026-08-15 re-measurement and either would be misread as a frame hold.
    caveat = ""
    if peak >= 8:
        caveat += (" CAVEAT: %d frames is 0.3s+ — that is a PULSE OR SCENE "
                   "RHYTHM, not a frame hold; do not read it as animation on "
                   "%ds without opening the frames." % (peak, peak))
    if peak == min(max_lag, n - 1):
        caveat += (" CAVEAT: the peak sits at the edge of the lag range "
                   "examined (max_lag=%d), so it is not confirmed to BE the "
                   "maximum. Re-run with a wider --max-lag." % max_lag)
    base["reading"] = (
        "%s: holds every %d frames (lag %d autocorrelation %.2f). "
        "%d frames carry about %.0f distinct pictures -- effective %.1f fps. "
        "Open frames N, N+1, N+2 and look before calling it.%s"
        % (band, peak, peak, strength, n + 1, base["distinct_pictures"],
           base["effective_fps"], caveat))
    return base


def legacy_parity_ratio(series) -> float:
    """RETIRED 2026-08-15. Reproduced ONLY so the blindness stays testable.

    This is `cadence` exactly as `coldread_frames.py` computed it: louder index
    parity mean over quieter index parity mean. It reads 1.00x on EVERY odd hold
    period -- see the aliasing table in this module's docstring. Do not gate on
    it, do not quote it, do not compare two clips with it. It is called from the
    regression test that pins the aliasing, and from `coldread_frames.py` where
    it is printed under a RETIRED label for continuity with older job specs.
    """
    x = [float(v) for v in series]
    ev = [v for i, v in enumerate(x) if i % 2 == 0]
    od = [v for i, v in enumerate(x) if i % 2 == 1]
    if not ev or not od:
        return float("nan")
    me, mo = sum(ev) / len(ev), sum(od) / len(od)
    loud, quiet = (me, mo) if me >= mo else (mo, me)
    return float("inf") if quiet <= 0 else loud / quiet


# --- the clip-reading half; needs ffmpeg and numpy, unlike everything above ----

FFMPEG_CANDIDATES = ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg", "ffmpeg")


def _ffmpeg() -> str:
    for c in FFMPEG_CANDIDATES:
        if c == "ffmpeg" or Path(c).exists():
            return c
    return "ffmpeg"


def probe(path: str):
    """(width, height, fps) from the container, one ffprobe call."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate", "-of", "csv=p=0", path],
        capture_output=True, text=True, encoding="utf-8").stdout.strip()
    w, h, rate = out.split(",")[:3]
    fps = (float(rate.split("/")[0]) / float(rate.split("/")[1])
           if "/" in rate else float(rate))
    return int(w), int(h), fps


def pair_differences(path: str, scale: int = 8):
    """Per-pair mean absolute luma difference, read at 1/`scale` resolution.

    `-vsync 0` so nothing is duplicated or dropped on the way out: a decoder
    that helpfully retimes frames would forge the very hold we are measuring.
    Piped as rawvideo, so this writes NOTHING to disk -- the whole clip at 1/8
    scale is a few MB in memory.
    """
    import numpy as np                       # lazy: CI has no numpy

    w, h, fps = probe(path)
    sw, sh = max(8, w // scale), max(8, h // scale)
    sw, sh = sw - (sw % 2), sh - (sh % 2)
    r = subprocess.run(
        [_ffmpeg(), "-v", "error", "-i", path, "-vsync", "0",
         "-vf", "scale=%d:%d,format=gray" % (sw, sh), "-f", "rawvideo", "-"],
        capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg failed on %s: %s"
                           % (path, r.stderr.decode("utf-8", "replace")[:300]))
    buf = np.frombuffer(r.stdout, dtype=np.uint8)
    n = buf.size // (sw * sh)
    if n < 3:
        raise RuntimeError("only %d frames decoded from %s" % (n, path))
    f = buf[:n * sw * sh].reshape(n, sh, sw).astype(np.int16)
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    return [float(v) for v in d], fps, (sw, sh), n


def measure(path: str, scale: int = 8, max_lag: int = MAX_LAG) -> dict:
    """One clip, read end to end. Pair 0 -- the i2v restyle flash -- is dropped.

    The flash is a single enormous pair (around 30 MAD where real motion is 8)
    and leaving it in dominates the mean the autocorrelation is taken about. It
    is reported separately so it cannot hide, the same convention
    `coldread_frames.py` uses.
    """
    d, fps, size, n = pair_differences(path, scale=scale)
    flash, body = d[0], d[1:]
    res = hold_period(body, max_lag=max_lag, fps=fps)
    res.update({
        "clip": str(path),
        "frames": n,
        "fps": round(fps, 3),
        "read_at": "%dx%d (1/%d scale)" % (size[0], size[1], scale),
        "flash_pair0": round(flash, 3),
        "mean_pair_difference": round(sum(body) / len(body), 3) if body else None,
        # Kept only so a reader holding an old job spec can see what the retired
        # number said about THIS clip. It is not a measurement of anything.
        "RETIRED_parity_ratio_blind_to_odd_periods": round(
            legacy_parity_ratio(body), 2),
    })
    return res


def print_report(res: dict) -> None:
    print(Path(res["clip"]).name)
    print("  %d frames @ %.2f fps, read at %s"
          % (res["frames"], res["fps"], res["read_at"]))
    print("  restyle flash (pair 0, excluded) %.2f | mean pair difference %s"
          % (res["flash_pair0"], res["mean_pair_difference"]))
    if res["lags"]:
        print("  autocorrelation  " + "  ".join(
            "lag%d %+.2f" % (k, v) for k, v in sorted(res["lags"].items())[:6]))
    print("  -> %s" % res["reading"])
    print("  (retired `cadence` on this clip: %.2fx -- blind to odd periods, "
          "not a reading)" % res["RETIRED_parity_ratio_blind_to_odd_periods"])
    print("  A FILTER, NOT A VERDICT: the cold read decides.")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--scale", type=int, default=8,
                    help="read at 1/N resolution (default 8; suppresses line-work churn)")
    ap.add_argument("--max-lag", type=int, default=MAX_LAG)
    ap.add_argument("--json", help="write every result to this file")
    a = ap.parse_args()

    results, failed = [], 0
    for c in a.clips:
        try:
            res = measure(c, scale=a.scale, max_lag=a.max_lag)
        except Exception as exc:                       # noqa: BLE001
            print("!! could not measure %s: %s" % (c, exc), file=sys.stderr)
            failed += 1
            continue
        results.append(res)
        print_report(res)
        print()
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(results, fh, indent=2)
        print("WROTE %s" % a.json)
    return 1 if failed and not results else 0


if __name__ == "__main__":
    raise SystemExit(main())
