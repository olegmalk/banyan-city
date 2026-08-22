#!/usr/bin/env python3
r"""THE JERRY v3 DATASET: v2'S TWENTY-ONE, BYTE-IDENTICAL, PLUS THE POSED FRAMES.

ONE VARIABLE AGAINST v2, AND THE WHOLE FILE IS BUILT TO MAKE THAT CHECKABLE.

v2 trains a LoRA whose identity bars pass and whose pose cannot be moved by any
instrument this tree owns: words fail (B5), an openpose ladder loses his face
before it bends a knee, a two-pass keeps the seat only in the cell where he is
somebody else. `pipeline/research/posed-dataset-single-ref-0822.md` and
`goblin-lowerbody-route-0822.md` Sec 6 measured why, and the measurement is
smaller than the diagnosis everyone was carrying:

    framing        frames
    upper body     11
    cowboy shot     8
    full body       2      <- `canon-full` and `canon-full-flip`

The two full-body frames are the founder's canon and its mirror, verified
byte-identical to `taste/refs/goblin-canon-founder-0821.png`. **The standing
prior is not twenty-one frames deep. It is ONE FRAME DEEP.** Round seven's
weight ladder and the two-pass's six cells were both hunting for a competing
lower-body configuration to fade toward, and there is no second configuration in
the weights to fade to. There is one picture.

So the fix is not a rebuild. Three posed full-body frames make posed the
MAJORITY of everything the trigger has ever seen below the waist, in a dataset
otherwise unchanged -- and "otherwise unchanged" is enforced here rather than
intended: this file re-reads the v2 manifest, carries its twenty-one frames with
their own image paths, their own sha256s and their own caption STRINGS, and
ASSERTS each caption byte-identical to what v2 shipped. v2b measured that
lengthening the captions of frames that already work costs identity (B1 went
11 -> 9 -> 11 as two clauses were added and taken back). Nothing that passes
gets touched.

THE CAPTION RULE THIS SET IS THE FIRST TO SATISFY, AND IT IS A CORRECTION TO OUR
OWN WRITTEN RULE. `character-lora-sdxl-0820.md` Sec 4 says "keep every tag that is
a variable -- pose, expression, camera framing", and we did: all 21 captions say
`standing`. Pose is mandatory anyway. The same 21 files generalise the SETTING
cleanly out of one meadow. That is a controlled experiment inside one training
run, and the clause it forces is:

    A caption tag keeps an attribute steerable ONLY WHERE THE ATTRIBUTE VARIES
    IN THE DATASET. Naming an attribute the dataset holds constant is a tag with
    nowhere to attach. It is free to write, which is why it reads as insurance
    and is not.

`hazy meadow` had somewhere to attach because the base checkpoint varies
backgrounds for any subject. Nothing outside the LoRA knows what this creature's
legs look like, so the trigger is the only source and it had one picture. In v3
the pose token finally VARIES in pixels -- `standing` on the two frames that show
a standing leg, a stance word on the posed ones -- which is the first time in
this project the tag has had anywhere to attach.

WHERE THE POSED FRAMES COME FROM, AND WHY THEY ARE HIM. Each is his head as
PIXELS and his legs as a POSE: the canon's head+torso block moved by an integer
and held OUTSIDE an SDXL inpaint mask (base weights, unet.in_channels == 4, so
the unmasked latent is restored at every timestep and cannot drift AT ANY
STRENGTH), the legs generated inside at strength 0.95 against an openpose
skeleton in his measured segment lengths, NO LoRA in the pass. Then
`jerry_lowerbody_restore_0822.py` pastes rows 0..883 back byte for byte and
asserts it. So the identity claim is arithmetic, not a resemblance judgement.

THE RISK, NAMED BEFORE THE RUN. Every posed frame shares ONE upper body, byte
for byte -- the canon's, moved by the same integer. Three of them is three copies
of one torso, one pair of arms and one light. If v3's identity bar falls, that is
the first suspect and it has a cheap answer that needs no research: re-crop, or
re-run the pass at more than one DROP so the torso sits at a different height.

  python3 pipeline/lora/build_jerry_v3_0822.py            # dry
  python3 pipeline/lora/build_jerry_v3_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

V2_MANIFEST = "pipeline/lora/manifest-jerry-v2-0822.yaml"
MANIFEST = "pipeline/lora/manifest-jerry-v3-0822.yaml"
CAPTION_DIR = "pipeline/lora/captions/jerry-v3-0822"
POSED_DIR = "farm-out/jerry-lowerbody-src-0822"
TARGET_PASSES = 1200
EPOCHS = 10

# The v2 scheme with the pose promoted from a literal to a slot. Substituting
# `standing` reproduces `derive_goblin_dataset_0822.CAPTION_TMPL` exactly, and
# that is asserted against all 21 inherited captions rather than eyeballed.
CAPTION_TMPL = ("bnyjerry, 1boy, solo, %s, looking at viewer, %s, %s, "
                "%s, anime style, cel shading")

# ---------------------------------------------------------------------------
# THE POSED FRAMES. One entry per landed cell, hand-judged at 1:1, with its crop
# argued per frame -- Sec 6: "crop the frames whose extremities are wrong, keep
# full-body only where the boots came back right, and record which is which."
#
# `crop` is rows kept from the top and MUST be a multiple of 64: kohya buckets on
# 64s (--enable_bucket --min_bucket_reso 832 --max_bucket_reso 2048) and a
# non-bucket size is resampled into the nearest one. Resampling a training frame
# is the one thing this route exists to avoid doing to his face. 0 = no crop.
#
# `pose` is the caption word. `framing` is the caption's framing word and is the
# TRUTH ABOUT THE FILE AS IT SHIPS, not about the pose. Only `posed-crouch` shows
# a foot, so only it is `full body`; the other two are cropped or run off the
# bottom edge and take `cowboy shot`. Writing `full body` on a frame with no foot
# in it would be the same lie the v2 builder refuses when a requested ground did
# not arrive.
# ---------------------------------------------------------------------------
POSED = {
    "posed-seat": {
        "src": "farm-out/ep2-goblin-lowerbody-0822/jerry-posed-seat-w2-0822.png",
        "crop": 1088,
        "pose": "sitting",
        "framing": "cowboy shot",
        "ground": "tall grass",
        "light": "soft daylight",
        "job": "ep2-b13-lowerbody-w2-0822",
        "hint": "jerry-seat-hint-0822.png",
        "why_kept": (
            "ROUND TWO OF THE ROUTE, AND THE FRAME THAT OPENED IT. Knees up and "
            "out past the authored hint, shins descending, feet planted, seam "
            "invisible, one figure. CROPPED, because the extremities are "
            "the route's known open clause -- pale thighs on the lit side and "
            "paw feet at y 1080-1120 -- and on a seated chibi the fold is the "
            "KNEES, which sit at y 930-1000 and survive the crop whole.\n\n"
            "THE LINE IS 1088 AND NOT THE 1070 SEC 6 NAMED, FOR TWO REASONS "
            "THAT PULL OPPOSITE WAYS AND SETTLE HERE. It must be a multiple of "
            "64 or kohya buckets it into the nearest one and RESAMPLES a frame "
            "this route exists to keep unresampled; that allows 1024 or 1088. "
            "1024 was tried first and looked at, and it cuts THROUGH the knees "
            "-- the seated fold is nearly gone and the frame reads as an "
            "upper-body shot with a hint of leg, which teaches the opposite of "
            "what it is here for. 1088 keeps the knees and the dark shins whole "
            "and lands just above the paws. It was chosen by opening both "
            "files, not by arithmetic."),
    },
    "posed-kneel": {
        "src": "farm-out/ep2-goblin-lowerbody-0822/jerry-posed-kneel-0822.png",
        "crop": 0,
        "pose": "kneeling",
        "framing": "cowboy shot",
        "ground": "tall grass",
        "light": "soft daylight",
        "job": "ep2-b13-lowerbody-kneel-0822",
        "hint": "jerry-kneel-hint-0822.png",
        "why_kept": (
            "THE GATE CELL, AND IT IS THE ONE THAT PROVED THE ROUTE MAKES A "
            "POSE RATHER THAN MAKING THE SEAT. Its positive still said `seated` "
            "and only the skeleton changed; the legs knelt anyway -- limb mass "
            "at y 1180 is 245 px against round two's 0. NOT CROPPED, and the "
            "reason is the opposite of round two's: this stance puts the knees "
            "at y 1055 and runs the shins off the bottom edge, so a crop at "
            "1024 would delete the fold the frame exists to teach and there are "
            "no paw feet inside the frame to delete."),
    },
    "posed-crouch": {
        "src": "farm-out/ep2-goblin-lowerbody-0822/jerry-posed-crouch-0822.png",
        "crop": 0,
        "pose": "squatting",
        "framing": "full body",
        "ground": "tall grass",
        "light": "soft daylight",
        "job": "ep2-b13-lowerbody-crouch-0822",
        "hint": "jerry-crouch-hint-0822.png",
        "why_kept": (
            "THE STANCE TWO BEATS ASK FOR. Beat 12 \"crouches low behind the "
            "pencil-thin trunk\" and the fig-pick \"crouches, picks one small "
            "round purple fruit from the grass with both hands\" -- and nothing "
            "in the 21 ratified frames supplies a squat. Chosen over `stride` "
            "on that count and on one more: a frontal stride on a fixed frontal "
            "torso is a knee at hip height with the shin hanging, which the "
            "h240hunch cell already rendered as a standing figure with its feet "
            "apart. Adding a frame that reads as STANDING to a dataset whose "
            "disease is a standing prior has negative expected value.\n\n"
            "IT LANDED AS AUTHORED AND IT IS THE BEST-PAINTED CELL ON THE "
            "ROUTE. The feet come down INSIDE the knees, which is the one "
            "clause that separates a squat from the seat this set already has, "
            "and he sits low. NOT CROPPED, and that decision reverses the one "
            "made for round two on the evidence rather than by symmetry: Sec 6 "
            "says crop the frames whose extremities are wrong and \"keep "
            "full-body only where the boots came back right\", and here they "
            "did -- real dark boots with shape, where round two gave paws. The "
            "planned 1024 crop would also have cut through the knees at "
            "y 975-1045 and deleted the fold. It is the only posed frame in the "
            "set that shows a foot, which is why it carries `full body`."),
    },
}

# THE ONE-KNEE IS NOT IN THE SET, AND THE REASON IS RECORDED RATHER THAN OMITTED.
#
# It was authored as the fourth frame and for the axis the set has never had:
# `seat`, `kneel` and `crouch` are all mirror-symmetric and so are all 21 v2
# frames, so the trigger has never seen this creature's left leg do something its
# right leg is not doing. The hint DROVE -- round one's mirror-asymmetry over the
# limb band is 81.4, the highest of the five cells, against the kneel's 71.4 and
# the seat's 60.0 -- and it is the only cell whose defect a crop cannot reach: an
# 80-unit pink slab at MID-THIGH, inside the fold the frame exists to teach,
# where the kneel's reads 7.
#
# Two draws were budgeted before the first ran and both were spent:
#
#   seed 20260823  asymmetry 81.4, right thigh 80 units off sage. Pose, no paint.
#   seed 20260824  the pink slab is gone AND THE NET SYMMETRISED HIM: both legs
#                  do the same thing. Paint, no pose. The r2 spec pre-registered
#                  exactly this as its third outcome and ruled it in advance --
#                  "a sage thigh bought by the net symmetrising him is not a
#                  pass, it is the seat with extra steps."
#
# THAT IS A FINDING AND NOT A MISS. Two draws bracket a real trade on this
# stance, and it sharpens the route's own sentence: the hint reaches the pose and
# does not reach the paint, and on the one stance that fights the checkpoint's
# bilateral prior, the two cannot presently be had together. A third draw is
# outside the declared budget. Sec 6 asks for "three or four posed full-body
# frames" and the set ships three.
ONEKNEE_EXCLUDED = {
    "cell": "posed-oneknee",
    "draws": {
        20260823: "asymmetry 81.4 (highest in the set); right thigh 80 RGB "
                  "units off the canon's sage as a pink slab at mid-limb, "
                  "which no crop reaches.",
        20260824: "the pink slab is gone and the asymmetry with it -- both legs "
                  "do the same thing. Passes P1 by failing A1, which the spec "
                  "ruled in advance is the seat with extra steps.",
    },
    "ruling": (
        "NOT ADMITTED. The two-draw budget was declared before the first draw "
        "and is spent. The asymmetry axis stays unrepresented in v3 and that is "
        "recorded as a known gap, not papered over: if v3 poses but poses "
        "symmetrically, this is the first place to look."),
    "evidence": [
        "farm-out/ep2-goblin-lowerbody-0822/jerry-posed-oneknee-0822.png",
        "farm-out/ep2-goblin-lowerbody-0822/jerry-posed-oneknee-r2-0822.png",
    ],
}


def sha256_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def carry_v2(write: bool) -> list:
    """The 21, re-read from v2's own manifest and asserted unchanged.

    THE ASSERTIONS ARE THE POINT OF THIS FUNCTION. "byte-identical to v2" is the
    single claim that makes a v3 score attributable to the added frames, and it
    is worth exactly what it is checked with. Three things are checked per
    frame: the image is still on disk, its sha256 still matches what the founder
    ratified, and the caption this file would generate is byte-identical to the
    caption v2 shipped.
    """
    man = yaml.safe_load(open(os.path.join(REPO, V2_MANIFEST), encoding="utf-8"))
    if man.get("count") != len(man["frames"]):
        raise SystemExit("!! v2 manifest count %s != %d frames"
                         % (man.get("count"), len(man["frames"])))
    out = []
    for fr in man["frames"]:
        p = os.path.join(REPO, fr["image"])
        if not os.path.isfile(p):
            raise SystemExit("!! v2 frame missing from disk: %s" % fr["image"])
        have = sha256_of(p)
        if have != fr["sha256"]:
            raise SystemExit(
                "!! %s HAS CHANGED SINCE THE FOUNDER RATIFIED IT.\n"
                "   ratified %s\n   on disk  %s\n"
                "   v3's whole claim is that the 21 are untouched. Stop."
                % (fr["image"], fr["sha256"], have))
        want = CAPTION_TMPL % ("standing", fr["framing"], fr["ground"],
                               fr["light"])
        if want != fr["caption"]:
            raise SystemExit(
                "!! CAPTION DRIFT on %s -- v3 would write a different string "
                "than v2 shipped, and v2b measured that re-captioning working "
                "frames costs identity.\n   v2 %r\n   v3 %r"
                % (fr["cell"], fr["caption"], want))
        row = dict(fr)
        row["caption_file"] = "%s/%s.txt" % (CAPTION_DIR, fr["cell"])
        row["pose"] = "standing"
        row["carried_from_v2"] = True
        out.append(row)
    return out


def build_posed() -> list:
    out = []
    for cell, spec in POSED.items():
        src = os.path.join(REPO, spec["src"])
        if not os.path.isfile(src):
            raise SystemExit(
                "!! %s has not landed yet: %s\n"
                "   Restore it first:\n"
                "     python3 pipeline/jerry_lowerbody_restore_0822.py \\\n"
                "       --init %s/jerry-seat-init-0822.png \\\n"
                "       --render <the landed png> --out %s"
                % (cell, spec["src"], POSED_DIR, spec["src"]))
        from PIL import Image
        img = Image.open(src).convert("RGB")
        if img.size != (832, 1216):
            raise SystemExit("!! %s is %dx%d, expected 832x1216"
                             % (spec["src"], img.size[0], img.size[1]))
        crop = spec["crop"]
        if crop:
            if crop % 64:
                raise SystemExit(
                    "!! %s crop %d is not a multiple of 64. kohya buckets on "
                    "64s and would RESAMPLE this frame into the nearest bucket."
                    % (cell, crop))
            if crop <= 890:
                raise SystemExit(
                    "!! %s crop %d cuts into the protected region (identity "
                    "floor y890)." % (cell, crop))
            rel = "%s/%s-crop%d-0822.png" % (POSED_DIR, cell, crop)
            p = os.path.join(REPO, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            img.crop((0, 0, 832, crop)).save(p)
        else:
            rel = spec["src"]
            p = src
        out.append({
            "cell": cell,
            "image": rel,
            "sha256": sha256_of(p),
            "size": "832x%d" % (crop or 1216),
            "caption_file": "%s/%s.txt" % (CAPTION_DIR, cell),
            "caption": CAPTION_TMPL % (spec["pose"], spec["framing"],
                                       spec["ground"], spec["light"]),
            "pose": spec["pose"],
            "framing": spec["framing"],
            "ground": spec["ground"],
            "light": spec["light"],
            "crop": crop or "none",
            "source_frame": spec["src"],
            "job": spec["job"],
            "hint": spec["hint"],
            "route": (
                "pipeline/goblin-lowerbody-route-0822.md -- his head held "
                "OUTSIDE an SDXL inpaint mask (base weights, in_channels 4, so "
                "the unmasked latent is restored every timestep), legs "
                "generated inside at strength 0.95 against an openpose "
                "skeleton at his measured segment lengths, NO LoRA in the "
                "pass; then jerry_lowerbody_restore_0822.py pastes rows 0..883 "
                "back byte for byte and asserts it."),
            "why_kept": spec["why_kept"],
            "carried_from_v2": False,
        })
    return out


def main() -> int:
    write = "--write" in sys.argv
    carried = carry_v2(write)
    posed = build_posed()
    frames = carried + posed
    N = len(frames)
    repeat = max(1, round(TARGET_PASSES / float(EPOCHS * N)))
    passes = N * repeat * EPOCHS
    steps = passes // 2

    poses = {}
    framings = {}
    for f in frames:
        poses[f["pose"]] = poses.get(f["pose"], 0) + 1
        framings[f["framing"]] = framings.get(f["framing"], 0) + 1

    # THE CLAUSE THIS WHOLE DATASET EXISTS TO SATISFY, CHECKED RATHER THAN HOPED.
    # A pose tag is steerable only where the pose VARIES in pixels, so a v3 whose
    # posed frames all failed to land would be v2 with a longer caption -- which
    # v2b measured is strictly worse than v2. Two or fewer posed frames is not a
    # majority of the lower-body evidence and does not clear Sec 6's own count.
    n_posed = sum(1 for f in frames if not f["carried_from_v2"])
    if n_posed < 3:
        raise SystemExit(
            "!! only %d posed frame(s). The v2 set carries TWO frames that show "
            "a leg (the canon and its mirror), so posed has to reach at least "
            "three to be the majority of the lower-body evidence -- which is "
            "the entire mechanism this dataset is betting on. Land the missing "
            "cell or do not train." % n_posed)

    print("v3: %d frames = %d carried from v2 + %d posed" % (N, len(carried), n_posed))
    print("   poses    %s" % ", ".join("%s %d" % (k, v)
                                       for k, v in sorted(poses.items())))
    print("   framings %s" % ", ".join("%s %d" % (k, v)
                                       for k, v in sorted(framings.items())))
    print("   THE LOWER-BODY VOTE: %d posed vs 2 standing (the canon pair) --"
          % n_posed)
    print("      the 19 others are 11 upper-body crops and 8 cowboy shots and")
    print("      carry no leg at all, so they cannot fight a new one.")
    print("   repeat %d  ->  %d image passes, %d optimizer steps at batch 2 "
          "(target ~%d)" % (repeat, passes, steps, TARGET_PASSES))
    for f in posed:
        print("   + %-14s %-9s %-11s crop %-4s %s"
              % (f["cell"], f["pose"], f["size"], f["crop"], f["sha256"][:16]))

    if not write:
        print("\n-- dry run. re-run with --write.")
        return 0

    cdir = os.path.join(REPO, CAPTION_DIR)
    os.makedirs(cdir, exist_ok=True)
    for f in frames:
        with open(os.path.join(REPO, f["caption_file"]), "w",
                  encoding="utf-8") as fh:
            fh.write(f["caption"] + "\n")

    doc = {
        "subject": "jerry",
        "trigger": "bnyjerry",
        "built_by": "pipeline/lora/build_jerry_v3_0822.py",
        "built_on": "2026-08-22",
        "supersedes": V2_MANIFEST,
        "one_variable_against_v2": (
            "THE ADDED FRAMES, AND NOTHING ELSE. All %d v2 frames are carried "
            "with their own image paths and their own sha256s, each re-verified "
            "against the bytes the founder ratified on 2026-08-22, and each "
            "caption asserted byte-identical to the string v2 shipped. The "
            "recipe, the repeat formula, the epoch count and the caption scheme "
            "are untouched. A v3 score is therefore attributable."
            % len(carried)),
        "founder_ratified": {
            "the_21": (
                "CARRIED. The founder read all 21 at 1:1 against his own image "
                "on 2026-08-22 and ruled `all ok`. Their bytes are unchanged "
                "and re-asserted at build time."),
            "the_posed_frames": (
                "NOT RATIFIED, AND NOT PRESENTED AS RATIFIED. They are "
                "steward-made training frames whose HEAD is byte-identical to "
                "the ratified canon by arithmetic (rows 0..883 pasted back and "
                "asserted) and whose LEGS are generated. Ratifying the input "
                "was never ratifying what is made from it, and a trained v3 "
                "still has to pass the bars at 1:1."),
        },
        "the_diagnosis": (
            "The standing prior is ONE FRAME DEEP, not 21. Of the 21 ratified "
            "frames, 11 are upper-body crops and 8 are cowboy shots; the only "
            "two that show a lower body are the canon and its mirror, verified "
            "byte-identical to taste/refs/goblin-canon-founder-0821.png and to "
            "its mirror. Every knob that failed -- round seven's weight ladder, "
            "the two-pass's six cells -- was hunting for a competing lower-body "
            "configuration to fade toward. There is one picture to fade from."),
        "the_caption_law": (
            "A caption tag keeps an attribute steerable ONLY WHERE THE "
            "ATTRIBUTE VARIES IN THE DATASET. v2 named `standing` on all 21 and "
            "pose stayed unpromptable (B5 fails), while the SETTING generalised "
            "cleanly out of one meadow -- because the base checkpoint varies "
            "backgrounds for any subject and `hazy meadow` had somewhere to "
            "attach outside the LoRA, and nothing outside the LoRA knows what "
            "this creature's legs look like. v3 is the first set in which the "
            "pose token varies in PIXELS."),
        "count": N,
        "repeat": repeat,
        "image_passes": passes,
        "optimizer_steps_at_batch_2": steps,
        "poses": dict(sorted(poses.items())),
        "framings": dict(sorted(framings.items())),
        "lower_body_vote": {
            "posed": n_posed,
            "standing": 2,
            "no_lower_body_at_all": len(carried) - 2,
        },
        "caption_scheme": (
            "v2's scheme with the pose promoted from a literal to a slot. Ten "
            "clauses, identical length on every frame. The 21 carried frames "
            "keep `standing` and their strings are asserted byte-identical to "
            "v2's; the posed frames name their stance. Everything else is v2's, "
            "unchanged, per the v2b dilution finding in registry.yaml."),
        "not_admitted": ONEKNEE_EXCLUDED,
        "known_gap": (
            "NO ASYMMETRIC FRAME. All three posed frames are mirror-symmetric, "
            "as are all 21 carried ones, so the trigger still has never seen "
            "this creature's left leg do something its right leg is not doing. "
            "The one-knee cell was built for exactly that axis and both "
            "budgeted draws traded pose against paint (see not_admitted). If "
            "v3 poses but poses symmetrically, this is the first place to look "
            "and the fix is a third draw or a re-authored asymmetric hint, "
            "neither of which is a research question."),
        "known_defect_carried_into_training": (
            "PALE THIGHS ON THE LIT SIDE, ON ALL THREE POSED FRAMES. This is "
            "the route's standing P3 clause and it is being trained on "
            "deliberately rather than overlooked. It sits at MID-LIMB, so "
            "unlike the paw feet no crop reaches it; the stopping rule against "
            "a fourth wording rung was filed before ep2-b13-lowerbody-w3-0822 "
            "rendered and two cells that moved this clause both traded "
            "something else away. The licensed $0 fix is a palette-transfer "
            "compositor off the canon's own bare shin (RGB 120.4 / 130.0 / "
            "110.4, sampled at 355..385 x 925..945), which has no sampler in it "
            "and is the house tradition -- beat20_fig_recolor.py. It is NOT "
            "applied here because that would be a second variable against v2 "
            "and the whole point of this set is that there is one. If v3 poses "
            "correctly but paints his legs pale, that compositor is the next "
            "step and it costs no card time."),
        "shared_torso_risk": (
            "ALL THREE POSED FRAMES SHARE ONE UPPER BODY, BYTE FOR BYTE -- the "
            "canon's, moved by the same integer DROP of 150. That is three "
            "copies of one torso, one pair of arms and one light. If v3's "
            "identity bar FALLS relative to v2, this is the first suspect, and "
            "the answer is cheap: re-crop, or re-run the masked pass at more "
            "than one DROP so the torso sits at a different height in each."),
        "frames": frames,
    }
    with open(os.path.join(REPO, MANIFEST), "w", encoding="utf-8") as fh:
        fh.write("# THE JERRY v3 DATASET -- GENERATED. Edit "
                 "pipeline/lora/build_jerry_v3_0822.py, not this file.\n"
                 "#\n# v2's twenty-one, byte-identical and re-asserted, plus "
                 "posed frames whose\n# heads are the founder's own pixels and "
                 "whose legs were generated against a\n# skeleton. See "
                 "`one_variable_against_v2`.\n")
        yaml.safe_dump(doc, fh, sort_keys=False, width=88, allow_unicode=True)
    print("\nwrote %s and %d caption(s)" % (MANIFEST, N))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
