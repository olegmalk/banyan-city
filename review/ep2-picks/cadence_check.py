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

ONE RATIO FOR A CLIP IS A LIE, AND THIS TOOL TOLD IT TWICE BEFORE SAYING SO.
The same beat 02 clip measures anywhere from 1.3 to 15.2 depending only on which
window you take the medians over:

    whole clip minus the flash      15.2
    first-to-last above the floor   10.6
    the cold read's motion phase     4.4
    the smoothed body window         1.8
    first half of the body           9.5
    second half of the body          1.3

That spread is not noise and it is not a choice of a better window. It is the
structure of the defect: the clip STARTS doubled and ANNEALS SMOOTH as motion
builds, so any single window is really reporting how much ramp it happened to
include. The sweep lane found the same annealing independently, duplicate-side
values climbing 1.41 to 11.67 while the peaks held.

So this reports the trend -- the body's first half against its second -- and
refuses to print one number as the clip's cadence. A clip is flagged when the
EARLY body is doubled, which is the part a viewer sees as judder on the motion
starting, and the report always shows both halves so the annealing is visible
rather than averaged away.

IT ALSO SEGMENTS, because an average over a whole clip grades the wrong thing.
These clips are bimodal: a frozen head, a moving body, a frozen tail. Beat 02
reads 0.47 / 9.14 / 0.38 across those three, and one number for the clip is
none of them. The segmentation is reported alongside the cadence so a take is
judged on how long it takes to start moving and how long it actually moves,
not on a mean that mixes the three.

PAIR 0 IS ALWAYS DROPPED AND REPORTED SEPARATELY. Frame 0 to frame 1 is not
motion: the model redraws the conditioning plate sharper, brighter and with the
eyes open, a one-frame restyle flash measuring around 30 on beat 02, larger than
any real movement in the clip. Averaging it in grades the flash.

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
    d_all = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    name = Path(path).name

    # Pair 0 is the restyle flash, never motion. Everything below works on the
    # rest, and the flash is reported on its own line so it cannot hide.
    flash, d = float(d_all[0]), d_all[1:]

    # The body is the contiguous span carrying the motion: pairs above a
    # quarter of the clip's smoothed peak. Head and tail are what bracket it.
    k = 3
    sm = np.convolve(d, np.ones(k) / k, mode="same")
    live = np.flatnonzero(sm > max(FLOOR, 0.25 * sm.max()))

    if live.size < 8:
        print(f"{name}: {len(f)} frames, too little movement to judge cadence")
        return False
    lo_i, hi_i = int(live[0]), int(live[-1]) + 1
    win = d[lo_i:hi_i]
    even, odd = win[0::2], win[1::2]
    if len(even) < 3 or len(odd) < 3:
        print(f"{name}: {len(f)} frames, motion window too short to judge cadence")
        return False
    def _ratio(seg):
        e, o = seg[0::2], seg[1::2]
        if len(e) < 2 or len(o) < 2:
            return float("nan")
        a, b = np.median(e), np.median(o)
        hi_, lo_ = max(a, b), min(a, b)
        return float(hi_ / lo_) if lo_ > 0 else float("inf")

    mid = len(win) // 2
    r_early, r_late = _ratio(win[:mid]), _ratio(win[mid:])
    hi, lo = max(np.median(even), np.median(odd)), min(np.median(even), np.median(odd))
    ratio = float(hi / lo) if lo > 0 else float("inf")
    verdict = ("DOUBLED at motion onset, annealing" if r_early >= DOUBLED
               else "cadence ok")
    fps = 24.0
    head, tail = d[:lo_i], d[hi_i:]
    print(f"{name}: {len(f)} frames")
    print(f"   restyle flash (pair 0, excluded): {flash:.1f}")
    print(f"   head  {len(head):3d} pairs  mean {head.mean() if len(head) else 0:6.2f}   "
          f"onset at {(lo_i + 1) / fps:.2f}s")
    print(f"   BODY  {len(win):3d} pairs  mean {win.mean():6.2f}   "
          f"{len(win) / fps:.2f}s of movement")
    print(f"   tail  {len(tail):3d} pairs  mean {tail.mean() if len(tail) else 0:6.2f}")
    # Both halves, always. The whole-body figure is printed last and labelled
    # as the misleading one, because it is the number someone will quote.
    print(f"   cadence: body first half {r_early:.1f}, second half {r_late:.1f}   {verdict}")
    print(f"            (whole-body {ratio:.1f} -- window-dependent, do not quote alone)")
    return bool(r_early >= DOUBLED)


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
