#!/usr/bin/env python3
r"""THE IP-ADAPTER REFERENCE ON A **SQUARE** CANVAS, AT A CHOSEN HEAD RATIO.

WHY THIS EXISTS, AND IT IS NOT A REFINEMENT OF THE k3 BUILDER -- IT IS A FIX.

`author_jerry_headfit_ref_0821.py` built k3's reference on a 416x608 PORTRAIT
canvas, on the reasoning that the render is 832x1216 and the reference should
match it. That reasoning is wrong, and the pixels say so, because **the
reference is not what the adapter sees.**

diffusers' `load_ip_adapter` constructs its own image processor with NO
arguments::

    feature_extractor = CLIPImageProcessor()
    self.register_modules(feature_extractor=feature_extractor)

    -- diffusers/loaders/ip_adapter.py, v0.29.2

and `CLIPImageProcessor`'s defaults are `size={"shortest_edge": 224}`,
`do_center_crop=True`, `crop_size={"height": 224, "width": 224}`. So every
reference is **resized on its SHORT edge to 224 and then CENTER CROPPED to a
square.** On k3's 416x608 canvas that is:

    416x608  --resize short edge-->  224x327  --center crop-->  rows 51..275

The head was authored at crown 0.093 of frame, i.e. original rows 62..172,
which land at resized rows 33..93. **The crop starts at row 51, so resized rows
33..51 -- the top 30% of the subject, the entire cranial dome -- were cut off
and never reached the encoder.** What did reach it was a 64x42 px subject
occupying **5.4% of the encoder's pixels**, flush against the top edge with its
skull sliced flat and the tile's dark temple flanges running up into the cut.

k1's reference was 156x152, effectively square: the same crop trimmed 3 px a
side, the head filled 99% of the encode, and k1 drew **no horns**. k3 drew two.
A subject truncated at a frame edge is a subject the model completes, and the
direction it was cut is the direction the horns grew.

SO THE CANVAS IS SQUARE HERE, ON PURPOSE, and the head is CENTRED. On a square
canvas the resize is exact and the centre crop is a no-op, which is the only
condition under which `--head-frac` means what it says: the ratio authored is
the ratio encoded. On k3 it did not -- authored 19.1%, encoded 18.7% of a view
that had already thrown the crown away.

WHAT IS CARRIED OVER UNCHANGED from the k3 builder, because both were right:

  THE SKY IS FLOODED. The crop carries the tile's cream sky in its corners and
  a hard bright rectangle around the head is, at 224x224, a louder feature than
  the brow it is supposed to carry. Flood-filled from the crop border with the
  tile's own field green; nothing interior is touched.

  THE HEAD PIXELS ARE THE SAME PIXELS. Same `HEAD_CROP` off the same tile, so
  a rung against k1/k3 moves the framing and nothing else.

WHAT IS DELIBERATELY DIFFERENT, and each is one variable a rung may name:

  `--head-frac`  the head's height as a fraction of the square. This is the
                 swept axis. k1 sat at ~1.00 (no horns, eye 1.87x too big),
                 k3 at 0.191 (horns, eye 1.24x -- the best yet).
  `--size`       the square's side in pixels. 448 is 2x the encoder's 224, so
                 every authored ratio downsamples cleanly and no ratio is
                 resampled up from nothing.

Re-running with the same arguments reproduces the same bytes; `--check SHA`
asserts it rather than printing it, which is what a job spec pins.

    python3 pipeline/author_jerry_squareref_0821.py --head-frac 0.45
    python3 pipeline/author_jerry_squareref_0821.py --head-frac 0.45 --check <sha>
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TILE = "review/ep2-goblin-design-0819/adult-b19-0819.jpg"
OUT_DIR = "farm-out/jerry-skel-assets-0820"

# Identical to the k3 builder. Same dome, ear flanges, brow, slits, mouth.
HEAD_CROP = (176, 280, 332, 432)
FIELD_SAMPLE = (1000, 1200, 60, 620)   # y0,y1,x0,x1 of open grass in the tile
SKY_MIN = 200
SKY_SPREAD = 45

# 2x the CLIP encoder's 224 so no authored ratio is upsampled into the encode.
DEFAULT_SIZE = 448


def head_on_field(tile: Image.Image):
    """The tile's head crop with its sky replaced by the tile's field green."""
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
    return Image.fromarray(head.astype("uint8")), field


def build(head_frac: float, size: int = DEFAULT_SIZE) -> Image.Image:
    tile = Image.open(os.path.join(REPO, TILE)).convert("RGB")
    head_im, field = head_on_field(tile)

    canvas = Image.new("RGB", (size, size), tuple(int(v) for v in field))
    th = int(round(head_frac * size))
    tw = int(round(head_im.width * th / head_im.height))
    if tw > size:
        raise SystemExit("!! head-frac %.3f makes the head %d px wide on a %d "
                         "px canvas -- it would be cropped, which is the whole "
                         "defect this builder exists to remove" % (head_frac,
                                                                   tw, size))
    # CENTRED, both axes. A subject touching an edge is a subject the model
    # completes past it, and completing past the top of a skull is a horn.
    canvas.paste(head_im.resize((tw, th), Image.LANCZOS),
                 ((size - tw) // 2, (size - th) // 2))
    return canvas


def clip_view(img: Image.Image) -> Image.Image:
    """Exactly what CLIPImageProcessor() hands the encoder. See the docstring."""
    w, h = img.size
    s = 224.0 / min(w, h)
    r = img.resize((round(w * s), round(h * s)), Image.BICUBIC)
    left = (r.width - 224) // 2
    top = (r.height - 224) // 2
    return r.crop((left, top, left + 224, top + 224))


def encoded_subject(img: Image.Image):
    """Subject bbox as the ENCODER sees it, which is the number that matters."""
    v = np.array(clip_view(img).convert("RGB")).astype(int)
    bg = v[1, 1]
    m = np.abs(v - bg).sum(2) > 25
    if not m.any():
        return None
    rows = np.where(m.any(1))[0]
    cols = np.where(m.any(0))[0]
    return int(cols[0]), int(rows[0]), int(cols[-1]), int(rows[-1])


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--head-frac", type=float, required=True,
                    help="head height as a fraction of the square canvas")
    ap.add_argument("--size", type=int, default=DEFAULT_SIZE)
    ap.add_argument("--out", default=None,
                    help="default: %s/jerry-tile-sq<PCT>-0821.png" % OUT_DIR)
    ap.add_argument("--check", metavar="SHA256", default=None,
                    help="assert the file on disk has this sha instead of "
                         "writing it")
    a = ap.parse_args(argv)

    pct = int(round(a.head_frac * 100))
    out_rel = a.out or "%s/jerry-tile-sq%02d-0821.png" % (OUT_DIR, pct)
    out = os.path.join(REPO, out_rel)

    img = build(a.head_frac, a.size)
    bb = encoded_subject(img)
    cov = (bb[2] - bb[0]) * (bb[3] - bb[1]) / (224.0 * 224.0) * 100 if bb else 0

    if a.check:
        if not os.path.exists(out):
            print("!! %s is not on disk" % out_rel)
            return 1
        got = hashlib.sha256(open(out, "rb").read()).hexdigest()
        if got != a.check:
            print("!! %s is %s, the spec pins %s" % (out_rel, got, a.check))
            return 1
        print("reference OK: %s  %s" % (out_rel, got))
        return 0

    img.save(out, optimize=True)
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print("wrote %s  %dx%d  head %.3f of frame" % (out_rel, img.width,
                                                   img.height, a.head_frac))
    # The line that would have caught k3 before it burned a GPU minute.
    print("  ENCODED: subject bbox %s in CLIP's 224x224 = %.1f%% of its pixels"
          % (bb, cov))
    if bb and (bb[1] == 0 or bb[0] == 0 or bb[2] >= 223 or bb[3] >= 223):
        print("  !! the subject TOUCHES an encoder edge -- it is being cut, "
              "and a cut subject is one the model completes past the cut")
        return 1
    print("  sha %s" % sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
