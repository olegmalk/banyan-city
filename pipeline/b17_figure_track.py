#!/usr/bin/env python3
"""Beat 17's pre-registered bar, measured rather than eyeballed.

The bar (written before the renders, in every ep2-b17-*-0815 spec):
  "the goblin's hips leave the grass AND his head crosses the frame midline
   while he stays in the same field -- no cut, no scene change, no camera
   move, no second figure."

HOW THE FIGURE IS FOUND, and why this is not a colour guess. The plate is a
seated goblin with VIVID YELLOW-GREEN skin against a BLUE sky, wearing a
purple-grey cloak, on blue-green grass. Above the horizon the only strongly
green thing in frame is the goblin himself:
    sky      B > G        -> excluded by (G > B + 30)
    cloud    R~G~B        -> excluded by both tests
    cloak    B >= R > G   -> excluded by (G > R + 8)
    grass    green, but BELOW the horizon -> excluded by the row cut
So mask = (G > R+8) & (G > B+30) & (row < horizon) isolates head/shoulders/limbs.

Reported per frame:
    head_top_y   smallest masked row  -- a seated->standing rise moves this by
                 hundreds of px; re-inking in place cannot.
    head_cx      centroid x of the masked pixels in the top 18% of the mask's
                 own vertical extent (the head, not the whole body).
    area         masked pixel count, as a sanity/coverage signal.

Nothing here uses camera scale: chained-NCC scale is unreliable (c870f08f) and
is deliberately not computed or quoted.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

FFMPEG = "ffmpeg"
HORIZON_FRAC = 0.62   # rows above this are sky-side; grass starts below it
HEAD_BAND = 0.18      # top slice of the figure's vertical extent = the head
MIN_ROW_PIX = 6       # a row needs this many masked px to count as the figure


def frames_rgb(path, scale=2):
    p = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-vsync", "0",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode()[:300])
    pr = subprocess.run([FFMPEG.replace("ffmpeg", "ffprobe"), "-v", "error",
                         "-select_streams", "v:0", "-show_entries",
                         "stream=width,height", "-of", "csv=p=0", str(path)],
                        capture_output=True)
    w, h = [int(x) for x in pr.stdout.decode().strip().split(",")[:2]]
    buf = np.frombuffer(p.stdout, dtype=np.uint8)
    n = buf.size // (w * h * 3)
    f = buf[:n * w * h * 3].reshape(n, h, w, 3).astype(np.int16)
    return f[:, ::scale, ::scale, :], w // scale, h // scale


def track(path):
    f, w, h = frames_rgb(path)
    hz = int(h * HORIZON_FRAC)
    out = []
    for i in range(len(f)):
        im = f[i]
        R, G, B = im[..., 0], im[..., 1], im[..., 2]
        m = (G > R + 8) & (G > B + 30)
        m[hz:, :] = False
        ys, xs = np.nonzero(m)
        if ys.size < 30:
            out.append((None, None, int(ys.size)))
            continue
        # ROBUST TOP ROW, not ys.min(). A bare min() is set by a handful of
        # speckle pixels -- on ep2-b17-full-s4 frame 0 it reported the head at
        # row 15 of a SEATED goblin whose head is at row 254, and that single
        # false positive silently turned a full stand-up into "rise 0".
        # Require a row to carry real width before it counts as the figure.
        rows = np.bincount(ys, minlength=h)
        solid = np.nonzero(rows >= MIN_ROW_PIX)[0]
        if solid.size == 0:
            out.append((None, None, int(ys.size)))
            continue
        top, bot = int(solid[0]), int(solid[-1])
        keep = (ys >= top)
        ys, xs = ys[keep], xs[keep]
        band = ys <= top + max(4, int((bot - top) * HEAD_BAND))
        out.append((int(top), float(xs[band].mean()), int(ys.size)))
    return out, w, h


def main():
    print("%-12s %5s %8s %8s %8s   %9s %9s %7s"
          % ("clip", "n", "topY_f0", "topY_min", "RISE", "cx_f0", "cx_range",
             "midline"))
    print("-" * 86)
    for p in sys.argv[1:]:
        tr, w, h = track(p)
        tops = [t for t, _, _ in tr if t is not None]
        cxs = [c for _, c, _ in tr if c is not None]
        if not tops:
            print("%-12s  no figure found" % Path(p).stem)
            continue
        mid = w / 2.0
        t0, c0 = tops[0], cxs[0]
        rise = t0 - min(tops)          # +ve = head moved UP the frame
        side0 = c0 < mid
        crossed = any((c < mid) != side0 for c in cxs)
        # express rise as a fraction of frame height for scale-free reading
        print("%-12s %5d %8d %8d %5d(%4.1f%%) %9.1f %9.1f %7s"
              % (Path(p).stem, len(tr), t0, min(tops), rise,
                 100.0 * rise / h, c0, max(cxs) - min(cxs),
                 "YES" if crossed else "no"))
    print("\nframe %dx%d (half-scale), midline x=%.0f" % (w, h, w / 2.0))


if __name__ == "__main__":
    main()
