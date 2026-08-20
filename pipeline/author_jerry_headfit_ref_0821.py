#!/usr/bin/env python3
r"""THE IP-ADAPTER REFERENCE THAT SHOWS THE HEAD AT THE SIZE A HEAD SHOULD BE.

WHY THIS EXISTS. `jerry-tile-head-0821.png` is a 156x152 crop in which the head
IS the whole picture, and both rungs that used it inflated the drawn head:
head_frac 0.181 with no adapter, 0.219 at --ip-scale 0.7, 0.227 at 0.9, against
an authored skeleton that never moved off 0.190. A mask says WHERE the adapter
acts. It does not say how big the thing it draws should be. So the one cause
that covers the oversized head AND the oversized eye is that the reference was
shown a head filling a frame -- and this file builds the control for it: the
SAME head pixels at head-to-frame 19.1%, which is the tile's own measured
standing head_frac.

TWO THINGS THAT ARE NOT COSMETIC.

  THE SKY IS FLOODED, not left alone. The crop carries the tile's cream sky in
  its corners, and pasting it onto a green canvas leaves a hard bright
  rectangle around the head -- at 224x224 through CLIP that rectangle is a
  louder feature than the brow it is supposed to be carrying. It is replaced
  with the tile's own field green, flood-filled from the crop border so nothing
  interior is touched.

  THE CROWN ROW MATCHES THE RENDER. The head is placed at 0.093 of frame
  height, which is where the crown lands in the 832x1216 renders (y=113 on k2).
  A reference whose subject sits somewhere else is testing two variables.

Re-running reproduces the committed reference byte-for-byte; --check asserts it
rather than printing it, and prints the sha the specs pin.

    python3 pipeline/author_jerry_headfit_ref_0821.py [--check]
"""

from __future__ import annotations

import hashlib
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TILE = "review/ep2-goblin-design-0819/adult-b19-0819.jpg"
OUT = "farm-out/jerry-skel-assets-0820/jerry-tile-headfit-0821.png"
EXPECT_SHA = "91087e527189e63c8c6ad95e5000c5c108bf943ac35c485a5659f652098ae7fd"

HEAD_CROP = (176, 280, 332, 432)   # dome, both ear flanges, brow, slits, mouth
FIELD_SAMPLE = (1000, 1200, 60, 620)   # y0,y1,x0,x1 of open grass in the tile
CANVAS = (416, 608)                # the render's 832x1216 at half scale
HEAD_FRAC = 0.190                  # the tile's MEASURED standing head_frac
CROWN_FRAC = 0.093                 # where the renders put the crown

# The tile's sky is pale and desaturated; anything at or above this and inside
# this spread, CONNECTED TO THE CROP BORDER, is background and not the figure.
SKY_MIN = 200
SKY_SPREAD = 45


def build() -> Image.Image:
    tile = Image.open(os.path.join(REPO, TILE)).convert("RGB")
    a = np.array(tile)
    y0, y1, x0, x1 = FIELD_SAMPLE
    field = np.array([int(v) for v in
                      np.median(a[y0:y1, x0:x1].reshape(-1, 3), axis=0)])

    head = np.array(tile.crop(HEAD_CROP)).astype(int)
    lo, hi = head.min(2), head.max(2)
    sky = (lo > SKY_MIN) & ((hi - lo) < SKY_SPREAD)
    lab, n = ndimage.label(sky)
    edge = (set(lab[0, :]) | set(lab[-1, :])
            | set(lab[:, 0]) | set(lab[:, -1])) - {0}
    outside = np.isin(lab, [i for i in range(1, n + 1) if i in edge])
    head[outside] = field
    head_im = Image.fromarray(head.astype("uint8"))

    w, h = CANVAS
    canvas = Image.new("RGB", (w, h), tuple(int(v) for v in field))
    th = int(round(HEAD_FRAC * h))
    tw = int(round(head_im.width * th / head_im.height))
    canvas.paste(head_im.resize((tw, th), Image.LANCZOS),
                 ((w - tw) // 2, int(round(CROWN_FRAC * h))))
    return canvas


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    out = os.path.join(REPO, OUT)
    img = build()
    if "--check" in argv:
        if not os.path.exists(out):
            print("!! %s is not on disk" % OUT)
            return 1
        got = hashlib.sha256(open(out, "rb").read()).hexdigest()
        if got != EXPECT_SHA:
            print("!! %s is %s, the specs pin %s" % (OUT, got, EXPECT_SHA))
            return 1
        print("reference OK: %s  %s" % (OUT, got))
        return 0
    img.save(out, optimize=True)
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print("wrote %s  %dx%d  head %.3f of frame  sha %s"
          % (OUT, img.width, img.height, HEAD_FRAC, sha))
    if sha != EXPECT_SHA:
        print("!! sha differs from the one the k3 spec pins (%s) -- if this "
              "change is intended, re-derive the spec." % EXPECT_SHA)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
