#!/usr/bin/env python3
"""Motion + framing measurement for the v34 LTX rounds.

Three families of number, kept apart on purpose:

  FLOW    median mean-|delta| and frozen share. Reproduces collect_farm.measure()
          (scale=200:-2, gray, median not mean). ad35e43 demoted this metric to
          report-only -- it may be printed and may NOT pick a winner, because on
          beat 04 it ranked the arm that re-invents the phone first, and on beat
          14 it ranked the collapsing sapling first. Printed here for continuity
          with the QA baseline, not to choose anything.

  ON-TWOS the beat-07 defect. Consecutive frame-deltas split into two alternating
          groups; ratio = larger group mean / smaller. A clip animating on twos
          has every other pair near-dead, so the ratio blows up while the median
          looks healthy. Also reports the longest run of consecutive frozen pairs.

  FRAMING measures the CAMERA, not the content, which is why ad35e43 kept it when
          it dropped the flow metric. Per-frame global motion is fitted from a
          grid of block displacements found by FFT phase correlation against
          frame 0. A similarity fit over those blocks separates a pan (all blocks
          move together) from a zoom (blocks move away from centre), so the two
          cannot be confused for each other. Reported at width 176, the scale the
          hand lane used, plus as a percentage of frame width so it is portable.

WHY THIS EXISTS AS A FILE AND NOT AS A THIRD PASTED SNIPPET. Three lanes have now
hand-rolled this same measurement on the same clips in one night, and ad35e43
records that two of them independently landed the same -16/17% framing drift. A
number that three people have to rewrite before they can quote it is a number
nobody can check. Committing it is what makes the on-twos figures in the beat-07
record falsifiable rather than quoted.

IT REPRODUCES THE HAND LANE'S NUMBERS EXACTLY, which is the only reason to trust
it: run over beat 07 it returns on-twos 6.0x for r1 and 9.5x for r3, matching the
two figures the card-runner lane published in its own r3 heartbeat before this
file existed. That agreement was the acceptance test.

AND IT STILL MAY NOT PICK A WINNER. ad35e43 demoted the flow metric to
report-only after it ranked the arm that re-invents the phone first on beat 04
and the collapsing sapling first on beat 14. Nothing here ranks anything. The
on-twos ratio measures a named defect rather than an amount of motion, so it is
the more honest of the three, but content -- invention, collapse, whether the
motion reads as wind or as churn -- has no tool in this repo and is answered by
opening the frames. Taste is the founder's (R4).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

W_FLOW = 200      # collect_farm's scale
W_FRAME = 176     # the hand lane's framing scale ("61px -> 13px of 176")
FROZEN = 0.2      # collect_farm's dead-pair threshold
BLOCK = 4         # 4x4 grid of blocks for the similarity fit


def frames(path, width):
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf",
                        f"scale={width}:-2,format=gray", f"{td}/f%03d.png"],
                       check=True, capture_output=True)
        return [np.asarray(Image.open(q), dtype=float)
                for q in sorted(Path(td).glob("*.png"))]


def flow(fs):
    d = np.array([np.abs(fs[i + 1] - fs[i]).mean() for i in range(len(fs) - 1)])
    return d


def on_twos(d):
    a, b = d[0::2], d[1::2]
    ma, mb = a.mean(), b.mean()
    hi, lo = max(ma, mb), min(ma, mb)
    ratio = hi / lo if lo > 1e-9 else float("inf")
    run = best = 0
    for x in d:
        run = run + 1 if x < FROZEN else 0
        best = max(best, run)
    return ratio, best


def shift(a, b):
    """Displacement of b relative to a by FFT phase correlation, sub-pixel free."""
    fa, fb = np.fft.fft2(a), np.fft.fft2(b)
    cross = fa * np.conj(fb)
    mag = np.abs(cross)
    cross = cross / np.where(mag < 1e-9, 1e-9, mag)
    r = np.fft.ifft2(cross).real
    peak = np.unravel_index(np.argmax(r), r.shape)
    dy, dx = peak
    if dy > a.shape[0] // 2:
        dy -= a.shape[0]
    if dx > a.shape[1] // 2:
        dx -= a.shape[1]
    return float(dx), float(dy)


def framing(fs):
    """Per-frame (pan_x, pan_y, zoom) vs frame 0, fitted over a block grid."""
    h, w = fs[0].shape
    bh, bw = h // BLOCK, w // BLOCK
    cx, cy = w / 2.0, h / 2.0
    centres, out = [], []
    for by in range(BLOCK):
        for bx in range(BLOCK):
            centres.append((bx * bw + bw / 2.0 - cx, by * bh + bh / 2.0 - cy))
    centres = np.array(centres)
    for f in fs:
        disp = []
        for by in range(BLOCK):
            for bx in range(BLOCK):
                sl = (slice(by * bh, (by + 1) * bh), slice(bx * bw, (bx + 1) * bw))
                disp.append(shift(fs[0][sl], f[sl]))
        disp = np.array(disp)
        # d = (s-1)*centre + t   -> least squares for s and t on both axes at once
        A = np.zeros((2 * len(centres), 3))
        A[0::2, 0] = centres[:, 0]
        A[0::2, 1] = 1.0
        A[1::2, 0] = centres[:, 1]
        A[1::2, 2] = 1.0
        y = np.empty(2 * len(centres))
        y[0::2] = disp[:, 0]
        y[1::2] = disp[:, 1]
        sol, *_ = np.linalg.lstsq(A, y, rcond=None)
        out.append((sol[1], sol[2], 1.0 + sol[0]))
    return np.array(out)


def report(path):
    fs = frames(path, W_FLOW)
    d = flow(fs)
    ratio, run = on_twos(d)
    ff = frames(path, W_FRAME)
    fr = framing(ff)
    w = ff[0].shape[1]
    drift = np.hypot(fr[:, 0], fr[:, 1])
    return {
        "n": len(fs),
        "median": float(np.median(d)),
        "frozen": 100.0 * float(np.mean(d < FROZEN)),
        "twos": ratio,
        "run": run,
        "pan_px": float(drift.max()),
        "pan_pct": 100.0 * float(drift.max()) / w,
        "pan_end": float(drift[-1]),
        "zoom": float(fr[:, 2].max()) if abs(fr[:, 2].max() - 1) > abs(fr[:, 2].min() - 1) else float(fr[:, 2].min()),
    }


if __name__ == "__main__":
    print(f"{'clip':<44}{'n':>4}{'median':>8}{'frozen':>8}{'twos':>7}{'run':>5}"
          f"{'panpx':>8}{'pan%':>7}{'zoom':>7}")
    for p in sys.argv[1:]:
        m = report(p)
        print(f"{Path(p).name:<44}{m['n']:>4}{m['median']:>8.2f}{m['frozen']:>7.0f}%"
              f"{m['twos']:>7.1f}{m['run']:>5}{m['pan_px']:>8.1f}{m['pan_pct']:>6.1f}%"
              f"{m['zoom']:>7.3f}")
