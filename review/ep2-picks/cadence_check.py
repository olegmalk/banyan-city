#!/usr/bin/env python3
"""Is this clip really running at its container frame rate, or is it doubled?

Written 2026-08-15 to check a claim rather than repeat it: that our 24fps
clips are 12fps content in a 24fps container, every second frame a near
duplicate of the one before. If true it is a pipeline defect that touches
every clip we have ever made, so it gets measured before it gets ledgered.

WHAT IT MEASURES. Mean absolute luminance difference between EVERY pair of
consecutive frames -- not six samples, all of them, because a sawtooth is
invisible at any sampling interval coarser than the tooth. Then it splits the
pairs into even-indexed and odd-indexed and compares the two medians. In
honest 24fps material the two are about equal. In doubled 12fps material one
set sits near zero while the other carries all the change.

The ratio is (higher median / lower median) computed INSIDE THE MOTION WINDOW
-- the contiguous span from the first to the last pair that clears the floor --
and not over the clip as a whole. That distinction is the whole measurement and
I got it wrong first: filtering pairs individually and taking medians across the
entire clip mixes a frozen head, a moving middle and a frozen tail into one
population, and on beat 02 that reported a ratio of 1.2 when the motion phase
alone reads 4.4. A clip with a dead head and a doubled middle looks honest if
you average the two together.

    cadence_check.py clip.mp4 [more.mp4 ...]

Exit is nonzero if any clip looks doubled, so it can gate a publish step.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

FFMPEG = "/opt/homebrew/bin/ffmpeg"
W, H = 176, 320          # a quarter-scale grey proxy; cadence survives downscaling
FLOOR = 2.0              # below this a pair is "nothing happened", not a beat
DOUBLED = 3.0            # higher/lower median above this reads as doubled


def frames(path: str) -> np.ndarray:
    out = subprocess.run(
        [FFMPEG, "-v", "error", "-i", path, "-vf", f"scale={W}:{H},format=gray",
         "-f", "rawvideo", "-"], capture_output=True)
    if out.returncode != 0:
        sys.exit(f"!! ffmpeg failed on {path}: {out.stderr.decode()[:200]}")
    buf = np.frombuffer(out.stdout, dtype=np.uint8)
    n = buf.size // (W * H)
    return buf[:n * W * H].reshape(n, H, W).astype(np.int16)


def report(path: str) -> bool:
    f = frames(path)
    if len(f) < 8:
        print(f"{Path(path).name}: only {len(f)} frames, skipped")
        return False
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    name = Path(path).name

    # The motion window: first to last pair clearing the floor. Everything
    # outside it is the ramp-in and the dead tail, and including them is what
    # made the first version of this script report a doubled clip as fine.
    live = np.flatnonzero(d > FLOOR)
    if live.size < 8:
        print(f"{name}: {len(f)} frames, too little movement to judge cadence")
        return False
    lo_i, hi_i = int(live[0]), int(live[-1]) + 1
    win = d[lo_i:hi_i]
    even, odd = win[0::2], win[1::2]
    if len(even) < 3 or len(odd) < 3:
        print(f"{name}: {len(f)} frames, motion window too short to judge cadence")
        return False
    hi, lo = max(np.median(even), np.median(odd)), min(np.median(even), np.median(odd))
    ratio = float(hi / lo) if lo > 0 else float("inf")
    verdict = ("DOUBLED -- 12fps content in a 24fps container" if ratio >= DOUBLED
               else "cadence ok")
    print(f"{name}: {len(f)} frames, motion window {lo_i}-{hi_i} ({hi_i - lo_i} pairs), "
          f"alternating medians {hi:.2f} vs {lo:.2f}, ratio {ratio:.1f}  {verdict}")
    print("   window head: " + " ".join(f"{v:.1f}" for v in win[:16]))
    return ratio >= DOUBLED


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clips", nargs="+")
    a = ap.parse_args()
    bad = [c for c in a.clips if report(c)]
    if bad:
        print(f"\n!! {len(bad)} clip(s) are frame-doubled.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
