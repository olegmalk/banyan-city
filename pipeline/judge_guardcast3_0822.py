#!/usr/bin/env python3
r"""Cut every round-3 frame down to the pixels the verdict is actually about.

    python3 pipeline/judge_guardcast3_0822.py [--out DIR]

$0, no GPU, no network. For each rendered `ep2-guardcast3-*` png it writes:

  JUDGE-<cell>-face.png   a 640x880 crop of head AND mouth, AT 1:1 -- NOT resized
  JUDGE-<cell>-full.jpg   the whole 832x1216 frame, for the body/age/style read

WHY THE CROP EXISTS AND WHY IT MUST NOT BE RESIZED. The defect this round is
about is SMALL: a sweat drop is forty pixels on the temple, a drool bead less
than that. Every viewer in the chain downsamples a 832x1216 image on its way to
being looked at, and a downsample is exactly the operation that makes a forty-
pixel bead indistinguishable from a highlight. The bar says "scored AT 1:1" and
this is the tool that makes that literally true rather than aspirational: the
crop is a straight box out of the source array, nearest neighbour to nothing.

The full frame is kept beside it because two of the drop clauses -- child or
female read, and the costume family -- are not visible in a face crop.
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_guardcast3_0822 as r3                                 # noqa: E402

# The head sits high in a 832x1216 head-and-shoulders frame -- but the FIRST
# crop box (y 40..680) was cut off the round-2 sheet and it was too high for
# round 3: these heads tilt, and on cell C the box ended above the mouth corner,
# which is exactly where the liquid trail this round is about was hanging. A
# judging crop that can miss the defect is worse than no crop, because it looks
# like evidence. Widened DOWN to the collarbone; the head still fits.
CROP = (96, 120, 736, 1000)


def cell_of(jid):
    """`ep2-guardcast3-j30-0822` -> `j30`."""
    return jid.split("-")[2]


def main():
    ap = argparse.ArgumentParser()
    # NOT under review/. The first run wrote these into the review directory
    # and build_site would have shipped thirty judging images -- fifteen full
    # frames including every DROPPED one -- to the live site beside the five
    # the founder is meant to choose between. Working images live outside the
    # published tree; only the chosen five get an address.
    ap.add_argument("--out", default=os.path.join(REPO, ".judge-r3-0822"))
    a = ap.parse_args()
    from PIL import Image
    os.makedirs(a.out, exist_ok=True)

    pngs = sorted(glob.glob(os.path.join(
        REPO, "farm-out", "ep2-guardcast3-*", "*-%s.png" % r3.ARM)))
    if not pngs:
        raise SystemExit("!! no round-3 frames in farm-out/ yet")
    for p in pngs:
        jid = os.path.basename(os.path.dirname(p))
        cell = cell_of(jid)
        im = Image.open(p).convert("RGB")
        if im.size != (832, 1216):
            print("!! %s is %dx%d, not 832x1216 -- crop box may miss the head"
                  % (cell, im.size[0], im.size[1]))
        face = im.crop(CROP)
        assert face.size == (CROP[2] - CROP[0], CROP[3] - CROP[1])
        face.save(os.path.join(a.out, "JUDGE-%s-face.png" % cell))
        im.save(os.path.join(a.out, "JUDGE-%s-full.jpg" % cell),
                "JPEG", quality=90, optimize=True)
        print("cut %s  face %dx%d at 1:1" % (cell, face.size[0], face.size[1]))
    print("%d frame(s) -> %s" % (len(pngs), a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
