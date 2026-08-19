#!/usr/bin/env python3
"""Camera drift and MOTION-COMPENSATED luminance for a locked-framing beat.

Why this exists, and why it lives beside the artifacts rather than in pipeline/:
`pipeline/luma_drift.py` is the committed brightness instrument and it is blind
to the difference between a fade and a frame that MOVES. On
`ep2-b12-stillmotion-s20260818-0819` it read whole-frame drift -15.45 (a PASS on
that spec's two-sided |drift| >= 20 bar) while the picture had translated 387px
up the frame -- so the -15.45 was a composition change, not a brightness one, and
the number that decided the rung was measuring the wrong thing.

Two readings, deliberately separate:

  DRIFT   per-frame vertical/horizontal translation by phase correlation on
          native-resolution BT.601 gray frames, cumulated. Reported per 3x2
          block as well as whole-frame: a REAL camera move is region-consistent
          (all six blocks inside ~1px), field re-inking is not -- the beat-19
          lane's own test, which caught a [4,4] "camera move" that was a horizon
          band re-inking.

  LUMA    mean luma of the OVERLAP region only: f000 rows [s:] against fN rows
          [:H-s], where s is the measured cumulative shift. Same content in both
          frames, so a fade cannot hide behind a pan and a pan cannot forge a
          fade. Plus a tracked 400-row patch followed by the same shift.

Usage:  python3 b12_camera_drift.py CLIP [CLIP ...]

Needs ffmpeg/ffprobe and numpy. No torch, no network, no GPU. Exit 0 whenever
every clip decoded -- an instrument takes no view on pass or fail.
"""
from __future__ import annotations

import subprocess
import sys

import numpy as np


def gray_frames(path: str) -> np.ndarray:
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True)
    w, h = (int(x) for x in p.stdout.strip().split(",")[:2])
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vsync", "0",
         "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True, check=True)
    a = np.frombuffer(r.stdout, dtype=np.uint8)
    n = a.size // (w * h)
    return a[: n * w * h].reshape(n, h, w).astype(np.float64)


def shift(a: np.ndarray, b: np.ndarray) -> tuple[int, int]:
    """Integer (dy, dx) taking a onto b, by phase correlation. Hann-windowed so
    the frame edge does not dominate; magnitude-normalised so contrast does not."""
    a = a - a.mean()
    b = b - b.mean()
    win = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1]))
    A = np.fft.rfft2(a * win)
    B = np.fft.rfft2(b * win)
    R = A.conj() * B
    R /= np.abs(R) + 1e-9
    c = np.fft.irfft2(R, s=a.shape)
    dy, dx = (int(v) for v in np.unravel_index(int(np.argmax(c)), c.shape))
    if dy > a.shape[0] // 2:
        dy -= a.shape[0]
    if dx > a.shape[1] // 2:
        dx -= a.shape[1]
    return dy, dx


def blocks(f0: np.ndarray, fj: np.ndarray) -> list[tuple[int, int]]:
    h, w = f0.shape
    out = []
    for r0, r1 in ((0, h // 3), (h // 3, 2 * h // 3), (2 * h // 3, h)):
        for c0, c1 in ((0, w // 2), (w // 2, w)):
            out.append(shift(f0[r0:r1, c0:c1], fj[r0:r1, c0:c1]))
    return out


def report(path: str) -> None:
    F = gray_frames(path)
    n, H, W = F.shape
    cum = [0]
    for i in range(1, n):
        dy, _dx = shift(F[i - 1], F[i])
        cum.append(cum[-1] + dy)
    last = n - 1
    s = -cum[last]
    print("=" * 78)
    print(path.split("/")[-1])
    print(f"  {n} frames, {W}x{H}")
    dys = np.diff(np.array(cum))
    print(f"  DRIFT   cumulative dy f000->f{last:03d} {cum[last]:+d}px"
          f"   per-frame dy median {np.median(dys):+.1f} min {dys.min():+d} max {dys.max():+d}")
    mid = n // 2
    print(f"  DRIFT   f000->f{mid:03d} blocks (3 rows x 2 cols): {blocks(F[0], F[mid])}")
    raw = F[last].mean() - F[0].mean()
    if 0 < s < H:
        a = F[0][s:, :].mean()
        b = F[last][: H - s, :].mean()
        print(f"  LUMA    raw whole-frame drift {raw:+7.2f}"
              f"   OVERLAP-COMPENSATED ({H - s} rows) {b - a:+7.2f}")
    else:
        print(f"  LUMA    raw whole-frame drift {raw:+7.2f}"
              f"   OVERLAP-COMPENSATED (no shift to compensate) {raw:+7.2f}")
    base = F[0][500:900, :].mean()
    keys = [k for k in (0, 24, 48, 72, 96, 120) if k < n]
    for j in keys:
        sj = -cum[j]
        r0, r1 = 500 - sj, 900 - sj
        if r0 < 0 or r1 > H:
            print(f"  PATCH   f{j:03d} rows {r0}-{r1} OUT OF FRAME -- the tracked patch has left the picture")
            continue
        v = F[j][r0:r1, :].mean()
        print(f"  PATCH   f{j:03d} rows {r0}-{r1} luma {v:7.2f}  delta from f000 {v - base:+7.2f}")
    d = [np.abs(F[i + 1] - F[i]) for i in range(n - 1)]
    means = np.array([x.mean() for x in d])
    print(f"  MOTION  interframe mean|diff| mean {means.mean():.3f}"
          f"   pairs under 0.5: {(means < 0.5).sum()} of {n - 1}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        report(p)
