#!/usr/bin/env python3
r"""THE SIX INITS THE GOBLIN DATASET FACTORY RUNS ON, CUT FROM ONE IMAGE.

WHY THIS FILE EXISTS. `pipeline/goblin-i2i-route-0822.md` closed the pose half
of the img2img-from-canon route and kept the other half: at strength <= 0.40 the
pass re-lights and re-grounds `taste/refs/goblin-canon-founder-0821.png` with the
founder's own face intact, at ~5 s a frame for $0. That makes it a DATASET
FACTORY for the one thing still open -- a LoRA trained on his pixels, which is
the only remaining route that puts his identity into the HIGH-noise steps where
a pose net also lives.

AND A DATASET FACTORY NEEDS MORE THAN ONE CAMERA. img2img at 0.30-0.40 does not
move the composition -- that is the same sentence as "his face survives", and
round two measured it. So FRAMING AND HANDEDNESS CANNOT COME FROM THE PROMPT ON
THIS ROUTE; the words `upper body` and `from the left` are dead letters at this
strength. They have to come from THE INIT, before the model ever sees it. This
script is that step: it cuts the canon image into three framings and mirrors
each, and every cell of the batch then names one of the six.

WHY FRAMING VARIETY IS NOT A NICETY HERE. The sapling v1 verdict
(`pipeline/lora/registry.yaml`) is the argument: 44 of 44 frames were figure-free
and 44 of 44 stood on grass, and BOTH monocultures came back as failed bars --
the trigger learned the field and learned "no figure" as part of the subject. A
goblin set cut from ONE standing full-body photograph at ONE distance would
teach `bnyjerry` = "this man, at this size, in this frame", which is the
pose-locked failure `curation-tile-0820` already refused a dataset for in its
own words: "seven frames in four poses trains a pose, not a character, and a
pose-locked character LoRA is worse than no LoRA because it appears to work on
the beat it was trained on."

THE MIRROR IS THE ONE FREE AXIS AND IT IS TAKEN. His costume has no chirality
that canon fixes -- `pipeline/canon.yaml` names a shirt with a placket, dark
shorts and dark boots, no shoulder patch, no single-side prop -- so a horizontal
flip is a genuinely new view rather than a lie about him. It doubles the set at
zero render cost and zero curation risk, and it is the standard augmentation for
exactly this reason.

THE SQUARE HEAD CROP IS 832x832 AND THE NUMBER IS NOT AESTHETIC. sd-scripts
asserts `min(resolution) >= min_bucket_reso` before it loads a weight, and the
sapling runs train at `--resolution 832,1216 --min_bucket_reso 832`. 832 is
therefore the SHORT SIDE FLOOR of this tree's trainer, an 832x832 frame lands in
a real bucket, and anything smaller would either be upscaled by the bucketer or
stop the run. (`train-sapling-v2b-0822.yaml` line 223 is where that cost a run
once already, at 1024.)

WHAT IT REFUSES TO DO. It reads the canon by sha256 and dies on a mismatch --
the init IS the canon on this route, as `derive_goblin_i2i_0822` says, and the
whole dataset descends from these six files. It never upscales past 1.75x: a
crop magnified further is a soft init, a soft init at strength 0.35 comes back
soft, and a soft frame in a character set teaches softness. The head crop's
1.486x is the largest here and it is printed, not assumed.

  python3 pipeline/lora/build_jerry_inits_0822.py            # dry, prints boxes
  python3 pipeline/lora/build_jerry_inits_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CANON = "taste/refs/goblin-canon-founder-0821.png"
CANON_SHA = "b62f333644c2f3161c0d5933f122f32c46c7608d1a97f758f3c53e4692eb4f00"
OUT_DIR = "farm-out/ep2-goblin-i2i-src-0822"

MAX_MAGNIFICATION = 1.75

# THE FIGURE, MEASURED ON THE CANON IMAGE AND WRITTEN DOWN SO THE BOXES BELOW
# ARE DERIVED RATHER THAN EYEBALLED. 832x1216 frame; head dome top y~130, chin
# y~480 (350 px head), ear span x 215..650, belt y~735, boot sole y~1030. That
# is a 900 px figure at 2.57 heads, consistent with canon.yaml's own measurement
# of the same picture (337 px head, 912 px figure, 2.71 heads, head_frac 0.370).
FIGURE = {"head_top": 130, "chin": 480, "belt": 735, "sole": 1030,
          "cx": 432, "ear_l": 215, "ear_r": 650}

# name -> (crop box (l, t, r, b) on the canon, output size, what it is for)
#
# `full` is the canon itself at 1.000x -- it is in the table rather than special-
# cased so all six inits are produced, hashed and fetched by one mechanism, and
# so the batch's cell table names one thing for every cell.
CUTS = {
    "full": ((0, 0, 832, 1216), (832, 1216),
             "THE CANON, UNCUT. The distance every previous goblin frame was "
             "made at, kept so the set has a control framing and so the LoRA "
             "sees him whole -- boots, shorts, placket and all five costume "
             "clauses of the E-bar in one view."),
    "cowboy": ((132, 40, 732, 917), (832, 1216),
               "COWBOY SHOT -- crown to mid-thigh, the framing most dialogue "
               "beats actually use. 600x877 is 832:1216 to within a pixel, so "
               "the aspect is the trainer's own bucket and nothing is squashed."),
    "headsq": ((155, 80, 715, 640), (832, 832),
               "THE SQUARE HEAD CROP. Both ears (x 215..650) with margin, the "
               "dome, the eyes and the collar. This is the frame that carries "
               "E1-E4 -- the almond eye, the near-horizontal ear, the smooth "
               "face, the sage palette -- at the largest scale the source "
               "supports, which is what a face has to be seen at to be learned."),
}


def boxes():
    """Every init, its box, its magnification and its reason. No file I/O."""
    out = []
    for name, (box, size, why) in CUTS.items():
        cw, ch = box[2] - box[0], box[3] - box[1]
        mag = max(size[0] / cw, size[1] / ch)
        out.append((name, box, size, mag, why))
        out.append((name + "-flip", box, size, mag,
                    "The mirror of `%s`. Free variety: canon fixes no "
                    "chirality on him (shirt with a placket, dark shorts, dark "
                    "boots -- no sided prop, no shoulder patch), so a flip is a "
                    "new view and not a false claim." % name))
    return out


def main() -> int:
    write = "--write" in sys.argv
    canon_path = os.path.join(REPO, CANON)
    raw = open(canon_path, "rb").read()
    have = hashlib.sha256(raw).hexdigest()
    if have != CANON_SHA:
        print("!! the canon image hashes %s, spec says %s" % (have, CANON_SHA))
        return 1
    print("canon %s sha OK" % CANON)

    from PIL import Image
    src = Image.open(canon_path).convert("RGB")
    if src.size != (832, 1216):
        print("!! canon is %s, expected (832, 1216)" % (src.size,))
        return 1

    dst_dir = os.path.join(REPO, OUT_DIR)
    if write:
        os.makedirs(dst_dir, exist_ok=True)

    # THE MASKS. A full-frame WHITE mask is what turns the inpaint pipeline on
    # base weights into plain img2img (round one's finding). There is one per
    # distinct output SIZE, because a mask that is not the frame is not full
    # frame -- and 832x832 is a size this route has never run at.
    sizes = sorted({size for _, _, size, _, _ in boxes()})
    for size in sizes:
        name = "fullframe-mask-%dx%d-0822.png" % size
        img = Image.new("L", size, 255)
        p = os.path.join(dst_dir, name)
        if write:
            img.save(p)
        print("  mask %-34s %dx%d all-white" % (name, size[0], size[1]))

    print()
    for name, box, size, mag, _why in boxes():
        cut = src.crop(box)
        if name.endswith("-flip"):
            cut = cut.transpose(Image.FLIP_LEFT_RIGHT)
        if cut.size != size:
            if mag > MAX_MAGNIFICATION:
                print("!! %s magnifies %.3fx, over the %.2fx ceiling -- a soft "
                      "init teaches softness" % (name, mag, MAX_MAGNIFICATION))
                return 1
            cut = cut.resize(size, Image.LANCZOS)
        out_name = "init-%s-0822.png" % name
        p = os.path.join(dst_dir, out_name)
        if write:
            cut.save(p)
            sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
        else:
            sha = "(dry)"
        print("  %-26s box=%-22s %4dx%-4d  %.3fx  %s"
              % (out_name, str(box), size[0], size[1], mag, sha[:16]))

    if not write:
        print("\n-- dry run, %d init(s) + %d mask(s). re-run with --write."
              % (len(boxes()), len(sizes)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
