#!/usr/bin/env python3
r"""THE GOBLIN FACE LADDER'S RULER, AS CODE THIS TIME.

WHY THIS FILE EXISTS. The f/g/h rungs were scored on "white-eye pixels over the
head bounding box" and the numbers (f4 0.097, h1 0.042) live in
`pipeline/work-ladder-0819.md` as a table with NO GENERATOR UNDER IT -- the same
shape as the span deriver that was a docstring with no code, and as
`derive_jerry_face_eyeshape_0821.py`, which the j-series `derivation:` block
cites and which is not in the repo. A ruler you cannot re-run is a ruler the
next lane has to re-invent, and re-inventing it is how two lanes end up
comparing numbers that are not the same number.

WHAT IT MEASURES, and both halves matter because the bar has two clauses.

  T1b AREA -- near-white, low-saturation pixels inside the head box, over the
  box's area. The head box is the largest chartreuse blob in the top half of
  the frame, which on these rungs is the bald dome; it comes out at 170x185
  +/- 3 px across all seven, as it should, since every rung shares the h19
  skeleton and seed 20260823.

  T1b SHAPE -- the per-eye bounding box and its aspect (height/width). This is
  the half the area number cannot see, and it turned out to be the whole
  residual: scaled to a common head height the tile's eye is 28.9 x 15.1 px
  and j2's is 27 x 27. THE RIGHT WIDTH AND TWICE TOO TALL. An area figure alone
  reads that as "getting closer"; the aspect reads it as an axis that is
  buying the wrong dimension.

CALIBRATION IS A TEST, NOT A COMMENT. `--selftest` re-measures the five
published rungs and asserts this code reproduces them. It is dead on for the
h-series (0.042 -> 0.0430, 0.041 -> 0.0419) and reads ~0.014 high on the f/g
series, where a second bright blob sits inside the head box that the original
evidently excluded; the rank order is identical throughout. The tolerances
below encode exactly that and no more, so if someone tightens the threshold and
the h-series drifts, this fails.

ON A JPEG BACKGROUND. `--interior` drops any white component touching the box
edge. The rendered frames have a dark field behind the head and do not need it;
the TILE (adult-b19-0819.jpg) sits on cream sky and does, or the box corners
alone read as 0.16. The tile's true figure is 0.0143.

    python3 pipeline/measure_face_eye_0821.py FRAME.png [...]
    python3 pipeline/measure_face_eye_0821.py --interior --box 196,310,285,432 \
        review/ep2-goblin-design-0819/adult-b19-0819.jpg
    python3 pipeline/measure_face_eye_0821.py --selftest
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np
from PIL import Image

# The dome is chartreuse -- R and G together, B far below both. Sampled at
# (208, 208, 90) on j1; a plain "green" test (G > R) rejects it outright.
SKIN_G_MIN = 120
SKIN_RG_SPREAD = 70
SKIN_B_DROP = 55

# Near-white and low-saturation. The eyes render cream, ~(249, 237, 206), so
# min(RGB) lands just over 200 and max-min just over 40: a 195/40 pair misses
# them entirely and reports 0.000 on a face with two plain white eyes.
WHITE_MIN = 190
WHITE_SPREAD = 60


def head_box(img: np.ndarray):
    """The bald dome: largest chartreuse component in the top half."""
    r, g, b = (img[..., 0].astype(int), img[..., 1].astype(int),
               img[..., 2].astype(int))
    skin = ((g > SKIN_G_MIN) & (abs(g - r) < SKIN_RG_SPREAD)
            & (g > b + SKIN_B_DROP))
    skin[img.shape[0] // 2:, :] = False
    if not skin.any():
        raise ValueError("no chartreuse head found in the top half")
    try:
        from scipy import ndimage
        lab, n = ndimage.label(skin)
        sizes = ndimage.sum(skin, lab, range(1, n + 1))
        skin = lab == int(np.argmax(sizes)) + 1
    except ImportError:
        pass
    ys, xs = np.nonzero(skin)
    return int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())


def _components(mask):
    try:
        from scipy import ndimage
    except ImportError:
        return None
    lab, n = ndimage.label(mask)
    return lab, n


def measure(path: str, box=None, interior: bool = False) -> dict:
    img = np.array(Image.open(path).convert("RGB"))
    x0, x1, y0, y1 = box or head_box(img)
    sub = img[y0:y1 + 1, x0:x1 + 1].astype(int)
    lo, hi = sub.min(2), sub.max(2)
    white = (lo > WHITE_MIN) & ((hi - lo) < WHITE_SPREAD)

    comp = _components(white)
    if interior and comp:
        lab, n = comp
        edge = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
        white = np.isin(lab, [i for i in range(1, n + 1) if i not in edge])
        comp = _components(white)

    head_w, head_h = x1 - x0 + 1, y1 - y0 + 1
    eyes = []
    if comp:
        lab, n = comp
        blobs = sorted(((int((lab == i).sum()), i) for i in range(1, n + 1)),
                       reverse=True)
        for size, i in blobs[:2]:
            ys, xs = np.nonzero(lab == i)
            w, h = int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)
            eyes.append({"px": size, "w": w, "h": h, "aspect": h / w})
    return {"path": path, "box": (x0, x1, y0, y1), "head_w": head_w,
            "head_h": head_h, "white": int(white.sum()),
            "frac": float(white.sum()) / (head_w * head_h), "eyes": eyes}


def fmt(m: dict) -> str:
    eyes = "  ".join("%dx%d a=%.2f" % (e["w"], e["h"], e["aspect"])
                     for e in m["eyes"]) or "-"
    return ("%-46s head=%dx%d  white=%5d  area=%.4f  eyes: %s"
            % (os.path.basename(m["path"]), m["head_w"], m["head_h"],
               m["white"], m["frac"], eyes))


# (frame, published area, tolerance). The h-series is where the j and k rungs
# are scored, so it gets the tight tolerance; f/g are order-only.
BASELINES = [
    ("ep2-jerry-face-f4-0820", 0.097, 0.020),
    ("ep2-jerry-face-g1-0820", 0.090, 0.020),
    ("ep2-jerry-face-g2-0820", 0.085, 0.020),
    ("ep2-jerry-face-h1-0821", 0.042, 0.003),
    ("ep2-jerry-face-h2-0821", 0.041, 0.003),
]
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def selftest(frames_dir: str) -> int:
    got, bad = [], 0
    for task, published, tol in BASELINES:
        arm = "posehint"
        p = os.path.join(frames_dir, task, "%s-%s.png" % (task, arm))
        if not os.path.exists(p):
            print("skip (frame not on disk): %s" % p)
            continue
        m = measure(p)
        ok = abs(m["frac"] - published) <= tol
        bad += not ok
        got.append(m["frac"])
        print("%-26s published %.3f  measured %.4f  tol %.3f  %s"
              % (task, published, m["frac"], tol, "OK" if ok else "!! DRIFT"))
    if got != sorted(got, reverse=True):
        print("!! rank order broken: %s" % got)
        bad += 1
    if not got:
        print("!! no baseline frames found under %s -- pass --frames"
              % frames_dir)
        return 1
    print("selftest: %s" % ("PASS" if not bad else "FAIL (%d)" % bad))
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("frames", nargs="*")
    ap.add_argument("--box", help="x0,x1,y0,y1 head box, instead of detecting")
    ap.add_argument("--interior", action="store_true",
                    help="drop white touching the box edge (needed on the "
                         "tile jpg, whose sky is cream)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--frames-dir", default=os.path.join(REPO, "farm-out"),
                    help="where the baseline rung frames live")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest(a.frames_dir)
    if not a.frames:
        ap.error("give at least one frame, or --selftest")
    box = tuple(int(v) for v in a.box.split(",")) if a.box else None
    for f in a.frames:
        print(fmt(measure(f, box=box, interior=a.interior)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
