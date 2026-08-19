#!/usr/bin/env python3
"""Whole-frame and horizontal-band mean luminance across a clip -- the brightness
instrument the beat-20 verdict asked for.

WHY THIS EXISTS. On 2026-08-19 two verdicts reported progressive darkening in
numbers computed ad hoc, with no committed instrument and no shared band
convention: beat 12 used rows 0-560 / 560-1120 / 1120-1280, beat 20 used equal
thirds of 1280. Neither is wrong, but two lanes measuring "the same" quantity two
ways is how a recipe property and a beat property get confused. The beat-20
verdict closed with "whoever owns the recipe should carry a brightness clause on
every rung from here rather than discovering it per beat"; a clause needs an
instrument, so here is one.

WHAT IT MEASURES, precisely, because the number is easy to misread:
  * Luminance is ITU-R BT.601 luma as ffmpeg's `format=gray` computes it, on the
    DECODED frames -- i.e. what a viewer sees, after the encoder's round trip,
    not what the sampler emitted. That is the right domain for this question:
    every darkening figure on the ladder was read off a published mp4.
  * Frames are decoded at NATIVE resolution with `-vsync 0`. No scaling, because
    band boundaries are quoted in source rows and a scaled decode would silently
    move them; `-vsync 0` for `hold_period`'s reason -- a decoder that retimes
    frames would forge the drift.
  * A band is a row range [lo, hi). Bands default to equal thirds. Rows are
    counted from the TOP of the frame.

WHAT IT DOES NOT MEASURE, stated because a brightness number invites the leap:
  * It cannot tell a global fade from an object moving through the band. Beat
    12's -46.93 on rows 560-1120 was a dark leaf growing across the mid-ground
    while the other two bands held to within 1.8 levels -- a mean over a band is
    blind to that difference by construction. THREE BANDS AGREEING is the signal
    that a drift is global; one band moving alone is an object until proven
    otherwise, and proving it needs eyes on the frames.
  * It says nothing about hue. A clip can hold luma and swing warm-to-cool.

Usage:
    python3 pipeline/luma_drift.py CLIP [CLIP ...] [--bands 0,560,1120,1280]
                                        [--at 0,24,48,72,96,120] [--json OUT]

Exit status is 0 whenever every clip decoded; this is an instrument and it takes
no view on pass or fail.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hold_period import _ffmpeg, probe  # noqa: E402


def frames_gray_native(path: str):
    """Every frame of the clip as a native-resolution float64 gray array."""
    import numpy as np

    w, h, _fps = probe(path)
    r = subprocess.run(
        [_ffmpeg(), "-v", "error", "-i", str(path), "-vsync", "0",
         "-vf", "format=gray", "-f", "rawvideo", "-"],
        capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg failed on %s: %s"
                           % (path, r.stderr.decode("utf-8", "replace")[:300]))
    buf = np.frombuffer(r.stdout, dtype=np.uint8)
    n = buf.size // (w * h)
    if n < 2:
        raise RuntimeError("only %d frames decoded from %s" % (n, path))
    return buf[:n * w * h].reshape(n, h, w).astype("float64"), w, h


def band_series(frames, bands):
    """Per-frame whole-frame mean and per-band means."""
    whole = [float(f.mean()) for f in frames]
    per_band = []
    for lo, hi in bands:
        per_band.append([float(f[lo:hi, :].mean()) for f in frames])
    return whole, per_band


def measure_clip(path: str, bands_rows, at_frames):
    import numpy as np  # noqa: F401

    frames, w, h = frames_gray_native(path)
    n = len(frames)
    if bands_rows is None:
        step = h / 3.0
        edges = [0, int(round(step)), int(round(2 * step)), h]
    else:
        edges = list(bands_rows)
    bands = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]
    bands = [(max(0, lo), min(h, hi)) for lo, hi in bands if lo < h]

    whole, per_band = band_series(frames, bands)
    idx = [i for i in at_frames if i < n]
    if (n - 1) not in idx:
        idx.append(n - 1)

    return {
        "clip": path,
        "frames": n,
        "width": w,
        "height": h,
        "bands": [{"rows": "%d-%d" % (lo, hi)} for lo, hi in bands],
        "sampled_at": idx,
        "whole_frame": {str(i): round(whole[i], 2) for i in idx},
        "whole_frame_drift_first_to_last": round(whole[n - 1] - whole[0], 2),
        "whole_frame_min": round(min(whole), 2),
        "whole_frame_max": round(max(whole), 2),
        "band_drift_first_to_last": [
            round(series[n - 1] - series[0], 2) for series in per_band],
        "band_at_first": [round(series[0], 2) for series in per_band],
        "band_at_last": [round(series[n - 1], 2) for series in per_band],
        "band_series_sampled": [
            {str(i): round(series[i], 2) for i in idx} for series in per_band],
    }


def print_report(r: dict) -> None:
    print("=" * 78)
    print(Path(r["clip"]).name)
    print("  %d frames, %dx%d" % (r["frames"], r["width"], r["height"]))
    cells = "  ".join("f%03d %7.2f" % (int(i), r["whole_frame"][str(i)])
                      for i in r["sampled_at"])
    print("  WHOLE  " + cells)
    print("  WHOLE  drift first->last %+.2f   (min %.2f, max %.2f)"
          % (r["whole_frame_drift_first_to_last"],
             r["whole_frame_min"], r["whole_frame_max"]))
    for b, first, last, d in zip(r["bands"], r["band_at_first"],
                                 r["band_at_last"],
                                 r["band_drift_first_to_last"]):
        print("  rows %-10s %7.2f -> %7.2f   %+.2f" % (b["rows"], first, last, d))
    agree = all(d < 0 for d in r["band_drift_first_to_last"]) or \
        all(d > 0 for d in r["band_drift_first_to_last"])
    print("  bands agree in sign: %s%s" % (
        "YES" if agree else "NO",
        "" if agree else
        "  <- one band moving alone is an OBJECT until eyes say otherwise"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--bands", default=None,
                    help="comma-separated row edges, e.g. 0,560,1120,1280 "
                         "(default: equal thirds of the frame height)")
    ap.add_argument("--at", default="0,24,48,72,96,120",
                    help="frame indices to report (last frame always added)")
    ap.add_argument("--json", default=None, help="write results as JSON here")
    a = ap.parse_args(argv)

    bands = [int(x) for x in a.bands.split(",")] if a.bands else None
    at = [int(x) for x in a.at.split(",") if x.strip()]

    out = []
    rc = 0
    for c in a.clips:
        try:
            r = measure_clip(c, bands, at)
        except Exception as e:  # noqa: BLE001 -- an unreadable clip is a result
            r = {"clip": c, "error": str(e)}
            rc = 1
            print("=" * 78)
            print("%s\n  ERROR %s" % (Path(c).name, e))
        else:
            print_report(r)
        out.append(r)

    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=2) + "\n")
        print("\nwrote %s" % a.json)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
