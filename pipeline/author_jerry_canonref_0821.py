#!/usr/bin/env python3
r"""THE IP-ADAPTER REFERENCE BUILT FROM **THE FOUNDER'S OWN GOBLIN**, 2026-08-21.

WHAT CHANGED AND WHY THIS IS A NEW BUILDER AND NOT A FLAG ON THE OLD ONE.
`author_jerry_squareref_0821.py` crops its head out of
`review/ep2-goblin-design-0819/adult-b19-0819.jpg` -- tile B -- which was the
authority until 16:54 on 2026-08-21, when the founder supplied a PICTURE of the
goblin and said "dude, this is how the goblin should look".

    taste/refs/goblin-canon-founder-0821.png   832x1216
    sha256 b62f333644c2f316...  committed b93a70da

Tile B and this image DISAGREE ON EVERY FACIAL AXIS -- ears, pupils, palette,
proportion, costume. A `--tile` flag on the old builder would have let a caller
mix them by forgetting an argument, and the two references are not
interchangeable inputs, they are two different characters. So: new file, new
constants, and the old one is left runnable for reproducing pre-ruling frames.

WHAT IS CARRIED OVER UNCHANGED, because the square builder's two findings were
correct and are the reason it beat k3:

  THE CANVAS IS SQUARE. diffusers' `load_ip_adapter` builds `CLIPImageProcessor()`
  with no arguments; its defaults resize the SHORT edge to 224 and then CENTER
  CROP to 224x224. On a non-square canvas that crop silently eats the ends of
  the long axis -- on k3's 416x608 portrait it ate the entire cranial dome, and
  the model grew horns completing the cut. On a square canvas the resize is
  exact and the crop is a no-op, so the ratio authored is the ratio encoded.

  THE BACKGROUND IS FLOODED FLAT. A hard bright rectangle around the head is,
  at 224x224, a louder feature than the brow it is supposed to carry. Anything
  connected to the crop border and reading as background is replaced by the
  image's own field colour; nothing interior is touched.

  NOTHING TOUCHES AN ENCODER EDGE. Checked, not hoped -- `main` returns 1 if the
  subject bbox reaches row/col 0 or 223 in CLIP's view.

WHAT IS DELIBERATELY DIFFERENT FROM THE SQUARE BUILDER:

  `--head-frac` MEANS THE HEAD, NOT THE CROP. The old builder scaled its whole
  crop to `head_frac * size` and called that the head ratio; its crop was 156x152
  around a head that nearly filled it, so the lie was small. This crop is 490x373
  and must be WIDE, because the ears are canon now and they reach 27% of a skull
  width past the skull on each side. Head height is 337 px of a 373 px crop, so
  crop and head differ by 10% and a builder that conflated them would author
  0.20 and encode 0.18. Here `--head-frac` is the crown-to-chin height as a
  fraction of the square and the crop is scaled by `HEAD_H / CROP_H` to make it
  true. The printed ENCODED line is the check.

MEASURED OFF THE IMAGE AT 1:1 (all constants below are these numbers):

    crown            y = 128        chin            y = 465    -> head 337 px
    skull sides      x = 280 .. 580             -> skull width  300 px
    ear tips         x = 210 .. 659             -> ear span     449 px
    eye line         y ~ 388        sole (far foot) y = 1040
    figure height    1040 - 128 = 912 px        -> 2.71 heads in frame
    head as fraction of standing figure         -> 0.370

    python3 pipeline/author_jerry_canonref_0821.py --head-frac 0.22
    python3 pipeline/author_jerry_canonref_0821.py --head-frac 0.22 --check <sha>
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
CANON = "taste/refs/goblin-canon-founder-0821.png"
OUT_DIR = "farm-out/jerry-canon-assets-0821"

# The head box, measured above, with an 18 px margin on every side so the ear
# tips and the crown's rim-light are inside the crop rather than on its edge.
HEAD_CROP = (187, 110, 677, 483)          # x0, y0, x1, y1  -> 490 x 373
HEAD_TOP_Y, HEAD_CHIN_Y = 128, 465
HEAD_H = HEAD_CHIN_Y - HEAD_TOP_Y         # 337
CROP_H = HEAD_CROP[3] - HEAD_CROP[1]      # 373
HEAD_OF_CROP = HEAD_H / float(CROP_H)     # 0.9035

# Open ground, no figure, no deep shadow. median -> (187, 195, 149).
FIELD_SAMPLE = (600, 1150, 0, 832)        # y0, y1, x0, x1

# THE BACKGROUND TEST, AND BOTH REJECTED VERSIONS OF IT, BECAUSE THE SECOND ONE
# LOOKED RIGHT AND DESTROYED THE FACE.
#
#   v1, the square builder's, inherited unchanged: `min channel > 160 and
#   spread < 50`, connected to the crop border. The tile had ONE background --
#   flat cream sky. This image has THREE behind the head: high-key sky
#   (181,193,198), a blurred dark hill (147,166,167) and lit field
#   (217,225,164). The hill fails `min > 160`, so the first build printed a
#   reference with hard blue-grey wedges touching both ear tips: the exact
#   loud-rectangle defect the flood exists to remove, relocated.
#
#   v2, a gradient walk -- grow from the border into any neighbour within 14 per
#   channel. It crosses a gradient of any depth, which is what the hill needed,
#   and IT ATE THE HEAD. The crown's rim-light is a soft warm ramp into the sky
#   with no ink line under it, so a per-step tolerance walks straight through the
#   skull and fills the face with field green, leaving the ink lines floating on
#   grass. Rendered and looked at before it was believed; that is the only reason
#   it is a paragraph here and not a reference on the box.
#
# v3, below, is a COLOUR test rather than a brightness one, and it is measured
# against every surface in the crop rather than against the sky alone:
#
#   BLUE_OVER_RED   sky +17, hill +20      skin -15, lit crown -28, warm ear rim
#                                          -51, ear interior -4
#   MIN_CHANNEL     lit field 164          skin 109, lit crown 114
#
# Nothing on the creature is bluish and nothing on it is bright in all three
# channels, so either clause alone is decisive and neither can reach the face.
BG_BLUE_OVER_RED = 4
BG_MIN_CHANNEL = 150

DEFAULT_SIZE = 448                        # 2x the encoder's 224


def head_on_field(img: Image.Image):
    """The canon image's head crop with its background replaced by field green."""
    a = np.array(img)
    y0, y1, x0, x1 = FIELD_SAMPLE
    field = np.array([int(v) for v in
                      np.median(a[y0:y1, x0:x1].reshape(-1, 3), axis=0)])

    head = np.array(img.crop(HEAD_CROP)).astype(int)
    r, b = head[:, :, 0], head[:, :, 2]
    bg = ((b - r) >= BG_BLUE_OVER_RED) | (head.min(2) > BG_MIN_CHANNEL)
    lab, n = ndimage.label(bg)
    edge = (set(lab[0, :]) | set(lab[-1, :])
            | set(lab[:, 0]) | set(lab[:, -1])) - {0}
    outside = np.isin(lab, [i for i in range(1, n + 1) if i in edge])
    head[outside] = field
    return Image.fromarray(head.astype("uint8")), field, float(outside.mean())


def build(head_frac: float, size: int = DEFAULT_SIZE) -> Image.Image:
    img = Image.open(os.path.join(REPO, CANON)).convert("RGB")
    head_im, field, _ = head_on_field(img)

    canvas = Image.new("RGB", (size, size), tuple(int(v) for v in field))
    # head_frac is the HEAD. The crop is taller than the head by 1/HEAD_OF_CROP.
    th = int(round(head_frac / HEAD_OF_CROP * size))
    tw = int(round(head_im.width * th / head_im.height))
    if tw > size or th > size:
        raise SystemExit("!! head-frac %.3f makes the crop %dx%d on a %d px "
                         "canvas -- it would be cut, and a cut subject is one "
                         "the model completes past the cut" % (head_frac, tw,
                                                               th, size))
    canvas.paste(head_im.resize((tw, th), Image.LANCZOS),
                 ((size - tw) // 2, (size - th) // 2))
    return canvas


def clip_view(img: Image.Image) -> Image.Image:
    """Exactly what CLIPImageProcessor() hands the encoder."""
    w, h = img.size
    s = 224.0 / min(w, h)
    r = img.resize((round(w * s), round(h * s)), Image.BICUBIC)
    left = (r.width - 224) // 2
    top = (r.height - 224) // 2
    return r.crop((left, top, left + 224, top + 224))


def encoded_subject(img: Image.Image):
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
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--head-frac", type=float, required=True,
                    help="CROWN-TO-CHIN height as a fraction of the square")
    ap.add_argument("--size", type=int, default=DEFAULT_SIZE)
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", metavar="SHA256", default=None)
    a = ap.parse_args(argv)

    pct = int(round(a.head_frac * 100))
    out_rel = a.out or "%s/jerry-canon-sq%02d-0821.png" % (OUT_DIR, pct)
    out = os.path.join(REPO, out_rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    img = build(a.head_frac, a.size)
    bb = encoded_subject(img)
    cov = ((bb[2] - bb[0]) * (bb[3] - bb[1]) / (224.0 * 224.0) * 100
           if bb else 0)

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
    print("wrote %s  %dx%d  head %.3f of frame (crop %.3f)"
          % (out_rel, img.width, img.height, a.head_frac,
             a.head_frac / HEAD_OF_CROP))
    print("  ENCODED: subject bbox %s in CLIP's 224x224 = %.1f%% of its pixels"
          % (bb, cov))
    if bb and (bb[1] == 0 or bb[0] == 0 or bb[2] >= 223 or bb[3] >= 223):
        print("  !! the subject TOUCHES an encoder edge -- it is being cut")
        return 1
    print("  sha %s" % sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
