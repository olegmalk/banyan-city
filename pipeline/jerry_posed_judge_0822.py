#!/usr/bin/env python3
r"""SCORE A POSED FRAME ON THE ROUTE'S OWN BARS, AND CROP IT ON THE ROUTE'S OWN LAW.

WHY THIS IS A PROGRAM AND NOT FIVE NUMPY SNIPPETS IN A TRANSCRIPT.

`goblin-lowerbody-route-0822.md` scores every cell of the lower-body route on the
same five quantities -- head hold above the cut, limb mass by row, limb span by
row, mirror-asymmetry over the limb band, and thigh colour against the canon's
own bare shin -- and each of them was computed by hand, once, in the round that
needed it. Four cells in, the numbers in that document cannot be compared to
each other with confidence, because nobody can prove the same band was sampled
twice. The set this feeds is a TRAINING SET and its admission bar is a number,
so the number gets a single implementation.

THE CROP LAW, AND WHY IT SNAPS TO 64.

Sec 6 of the route: the open defect -- pale thighs, paw feet, an ~82-unit
left/right boot mismatch -- sits at the BOTTOM of the frame, and "a crop at
y 1070 removes every defective pixel and keeps the entire pose signal, because
on a seated chibi the fold is the knees and not the feet." That is free, needs
no sampler, and is the set's own idiom: 8 of the 21 ratified frames are cowboy
shots and 11 are upper-body crops.

But 1070 is not a bucket. `emit_train_jerry_v2_0822.py` runs kohya with
`--enable_bucket --min_bucket_reso 832 --max_bucket_reso 2048` at resolution
832,1216, and kohya buckets on multiples of 64. A 832x1070 frame is resized into
whatever bucket it lands nearest, which resamples the training frame -- and
resampling is the one thing this whole route exists to avoid doing to his face.
So the crop snaps DOWN to a multiple of 64 and this tool refuses anything else.
832x1024 is the natural landing for a seat (knees at y 930-1000 survive whole,
paws at 1080-1120 are gone) and it is 46 px tighter than the law asks for, which
costs nothing the law was protecting.

THE CROP IS PER FRAME AND IS RECORDED PER FRAME. Sec 6 again: "crop the frames
whose extremities are wrong, keep full-body only where the boots came back
right, and record which is which per frame." A kneel whose knees are at y 1055
cannot take the seat's crop -- it would delete the fold the frame exists to
teach -- so the crop line is an argument, the bars are measured on BOTH the full
and the cropped frame, and the manifest carries the number.

    python3 pipeline/jerry_posed_judge_0822.py --frame <restored.png> [--crop 1024]
    python3 pipeline/jerry_posed_judge_0822.py --frame <restored.png> --crop 1024 \
        --out farm-out/jerry-lowerbody-src-0822/jerry-posed-seat-crop-0822.png

$0. No model, no network, no GPU.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(REPO, "taste", "refs", "goblin-canon-founder-0821.png")
INIT = os.path.join(REPO, "farm-out", "jerry-lowerbody-src-0822",
                    "jerry-seat-init-0822.png")
W, H = 832, 1216

# The cut the route masks below, and the identity floor the author script
# asserts nothing bearing identity sits under.
CUT_Y = 900
IDENTITY_FLOOR = 890

# THE CANON'S OWN BARE SHIN, sampled where the route sampled it and stated in
# the route doc so the two agree: RGB 120.4 / 130.0 / 110.4 at x 355..385,
# y 925..945 of `taste/refs/goblin-canon-founder-0821.png`. Read from the file
# rather than pasted, so a canon swap cannot leave a stale constant behind.
SHIN_BOX = (355, 925, 385, 945)

# The band the limb statistics are taken over: everything the pass may redraw,
# down to the frame's own bottom. Fixed here so four cells are comparable.
LIMB_TOP, LIMB_BOT = 900, 1216

# P1's line, declared in the one-knee reseed spec before that cell rendered.
THIGH_LINE = 40.0
# A1's floor, which is the seat's measured mirror-asymmetry.
ASYM_FLOOR = 60.0


def sha256_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def measure(path: str) -> dict:
    """The two things about a posed frame that can be MEASURED rather than seen.

    WHAT IS NOT HERE, AND IT WAS HERE FOR AN HOUR. This tool first carried five
    quantities -- limb mass by row, limb span by row, mirror-asymmetry, a
    feet-inside-knees separator and a per-thigh colour distance -- all of them
    resting on a limb segmentation. Two segmentations were tried. "Differs from
    the init" reports the whole band as leg, because the pass redraws the ground
    too at strength 0.95. "Departs from the row's own margin median" reports the
    grass as leg, because a defocused meadow has more per-row variance than the
    threshold that separates a shin from it. Both produced confident numbers,
    both were wrong, and the second one scored the kneel BELOW the seat on an
    asymmetry axis where the route's hand measurement puts it 11 points above.

    So they are gone rather than tuned. CLAUDE.md: "a metric agreeing with me is
    not a sample." The pose question on this route is answered by the founder's
    own instrument -- the frame at 1:1 -- and a number that cannot be validated
    against the four hand-measured cells already in the route doc would be
    decoration with a decimal point on it. What survives is the head hold, which
    is exact arithmetic on a region the sampler provably cannot touch, and the
    crop, which is a file operation.
    """
    a = np.asarray(Image.open(path).convert("RGB"))
    if a.shape[:2] != (H, W):
        raise SystemExit("!! %s is %dx%d, expected %dx%d"
                         % (path, a.shape[1], a.shape[0], W, H))
    init = np.asarray(Image.open(INIT).convert("RGB"))
    top_a = a[:IDENTITY_FLOOR].astype(np.int32)
    top_b = init[:IDENTITY_FLOOR].astype(np.int32)
    # I2's byte clause: the face core, which jerry_lowerbody_restore_0822.py
    # pastes back from the init and asserts. Re-checked here independently, so
    # the claim "his head is the founder's pixels" is verified by the tool that
    # admits the frame and not only by the tool that made it.
    y0, y1, x0, x1 = 200 + 150, 455 + 150, 330, 510
    return {
        "I1_mean_abs_delta_above_890": float(np.abs(top_a - top_b).mean()),
        "I1_maxdiff_above_890": int(np.abs(top_a - top_b).max()),
        "I2_face_core_byte_identical": bool(np.array_equal(
            a[y0:y1, x0:x1], init[y0:y1, x0:x1])),
    }


def report(path: str, m: dict) -> None:
    print("== %s" % os.path.relpath(path, REPO))
    print("   sha256 %s" % sha256_of(path))
    print("   I1 head hold above y890:  mean |delta| %.3f   maxdiff %d   %s"
          % (m["I1_mean_abs_delta_above_890"], m["I1_maxdiff_above_890"],
             "PASS" if m["I1_mean_abs_delta_above_890"] <= 2.0 else "FAIL"))
    print("   I2 face core byte-identical to the init: %s"
          % ("PASS" if m["I2_face_core_byte_identical"] else "FAIL"))
    print("   POSE IS NOT SCORED HERE. Look at the frame at 1:1 -- see this")
    print("      module's measure() docstring for why no number is offered.")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frame", required=True,
                    help="a RESTORED posed frame (832x1216), i.e. the output of "
                         "jerry_lowerbody_restore_0822.py -- not the raw render")
    ap.add_argument("--crop", type=int, default=0,
                    help="keep rows 0..CROP-1. MUST be a multiple of 64: kohya "
                         "buckets on 64s and a non-bucket size is resampled, "
                         "which is the one thing this route will not do to his "
                         "face. 0 = measure only, no crop written.")
    ap.add_argument("--out", default="",
                    help="where to write the cropped training frame")
    a = ap.parse_args()

    p = a.frame if os.path.isabs(a.frame) else os.path.join(REPO, a.frame)
    if not os.path.isfile(p):
        print("!! no such frame: %s" % a.frame)
        return 2
    report(p, measure(p))

    if not a.crop:
        return 0
    if a.crop % 64:
        print("\n!! --crop %d is not a multiple of 64. kohya buckets on 64s "
              "(--min_bucket_reso 832 --max_bucket_reso 2048 in "
              "emit_train_jerry_v2_0822.py) and would RESAMPLE this frame into "
              "the nearest bucket. Snap down: %d."
              % (a.crop, (a.crop // 64) * 64))
        return 3
    if a.crop <= IDENTITY_FLOOR:
        print("\n!! --crop %d would cut into the protected region (identity "
              "floor y%d). That deletes the head this route exists to keep."
              % (a.crop, IDENTITY_FLOOR))
        return 3

    img = Image.open(p).convert("RGB").crop((0, 0, W, a.crop))
    print("\n   crop 832x%d  (deleted rows %d..%d, %.0f%% of the frame)"
          % (a.crop, a.crop, H - 1, 100.0 * (H - a.crop) / H))
    print("   WHAT THAT DELETED IS A LOOKING QUESTION, not a computed one: open "
          "the\n   cropped file and check the fold is still in it.")
    if not a.out:
        print("   (no --out; nothing written)")
        return 0
    o = a.out if os.path.isabs(a.out) else os.path.join(REPO, a.out)
    os.makedirs(os.path.dirname(o) or ".", exist_ok=True)
    img.save(o)
    print("   WROTE %s  832x%d  %s"
          % (os.path.relpath(o, REPO), a.crop, sha256_of(o)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
