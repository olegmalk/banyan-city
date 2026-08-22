#!/usr/bin/env python3
r"""HIS FACE AS PIXELS, HIS LEGS AS A POSE: the masked lower-body pass.

WHAT IS ONE VARIABLE FROM WHAT. The parent, `ep2-b13-i2icnet-s35-0822`, is
img2img-from-canon plus an openpose hint on a FULL-FRAME mask. Its verdict and
the correction to `goblin-twopass-route-0822.md` between them close that route:
whatever denoises enough to move the body also denoises away his face, in every
configuration tried, with and without a LoRA.

This spec changes the MASK, and everything the mask forces along with it. Same
driver, same net, same scale, same base, same seed family, same negative.

    parent   mask = all white          strength 0.35  -> face holds, pose does not
    child    mask = white below y 900  strength 0.95  -> the face is not in the
                                                         pass at all

That is the whole idea and it is not a knob. An SDXL inpaint pipeline on base
weights (unet.in_channels 4) restores the unmasked latent at EVERY timestep:

    latents = (1 - init_mask) * init_latents_proper + init_mask * latents

so a region outside the mask cannot drift no matter how high the strength goes,
and a region inside it is free. Put the founder's ratified head, ears, eye,
collar and placket outside; put the legs, the hem and the ground inside. The
tension the last six rounds all measured -- identity and pose wanting opposite
ends of one knob -- stops existing because they are no longer the same pixels.

NO LoRA IS LOADED. That is deliberate and it is the second half of the design.
`bnyjerry-sdxl-v2` is where the standing prior lives (21 of 21 training frames
stand, pre-registered in `emit_train_jerry_v2_0822.BARS`), and this pass does
not need it: the identity is the init's own pixels, held by the mask. The one
configuration in which the pose net has been observed to DRIVE in this tree is
"no LoRA in the pass" -- four of four postures, correction Sec 3.

WHY IT MATTERS BEYOND ONE FRAME. v3 is blocked on POSED FRAMES OF HIM and pass
one can only pose a stranger. A frame whose head is byte-identical to the
founder's ratified canon and whose legs are seated IS a posed frame of him. If
this lands, four to six stances at $0 is the v3 dataset the lane is waiting on,
and the standing prior is a dataset property with a dataset fix.

  python3 pipeline/derive_jerry_lowerbody_0822.py            # dry
  python3 pipeline/derive_jerry_lowerbody_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec                                          # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77   # noqa: E402
from derive_goblin_i2i_0822 import assert_no_face_terms     # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = "pipeline/jobs/ep2-b13-i2icnet-s35-0822.yaml"
PARENT_DIRTOK = "b13i2icnet-s35-0822"
PARENT_OUTTOK = "b13-i2icnet-s35"
PARENT_SEEDTOK = "s20260823"

SRC_DIR = "farm-out/jerry-lowerbody-src-0822"
INIT = "jerry-seat-init-0822.png"
MASK = "jerry-seat-mask-0822.png"
HINT = "jerry-seat-hint-0822.png"
NET = "xinsir/controlnet-openpose-sdxl-1.0"
SCALE = "1.0"

SEED = 20260823          # the parent's seed, so the two rounds are comparable
SEED_TOK = "s20260823"
STRENGTH = "0.95"
BEAT = 13

NEW_ID = "ep2-b13-lowerbody-0822"
DIRTOK = "b13lowerbody-0822"
OUTTOK = "b13-lowerbody"

# WORDING A, MINUS THE TRIGGER. The correction to goblin-twopass-route-0822.md
# measured that ANY addition to pass one's wording costs the pose -- `+ soft
# overcast daylight` and `+ green skin` each turned a driving seat into a stand,
# on the identical net, scale, mask, seed and skeleton. So the string is the
# lane's fixed one and the only edit is dropping `bnyjerry`, which names a LoRA
# this pass does not load. NO seat noun and no pose word: the skeleton says
# where the body is, and this route's whole claim is that it can.
PROMPT = ("1boy, solo, in tall grass, detailed cinematic anime, masterpiece, "
          "best quality, very aesthetic")

NEGATIVE = ("lowres, worst quality, low quality, text, watermark, "
            "photorealism, 3d render, blurry, 2boys, multiple heads")

BAR = """THREE CLAUSES AND THEY ARE SCORED SEPARATELY, because this route's
whole claim is that they no longer trade against each other.

I. IDENTITY -- AND IT IS A DIFF, NOT A JUDGEMENT. Every pixel above y 890 must
   come back BYTE-IDENTICAL to the init. That is what the mask is for and it is
   measurable rather than tasteable:
     I1 maxdiff over rows 0..889 is 0. Not "small". Zero. A nonzero value means
        the latent blend did not hold and the whole design is wrong.
     I2 read the head at 1:1 against taste/refs/goblin-canon-founder-0821.png
        anyway, as a check on I1: narrow almond eye, tiny dark pupil, broad low
        dome, near-horizontal ears, smooth face, desaturated sage.

II. POSE -- the clause the route exists for.
     P1 IS HE SEATED? Knees UP and OUT, arriving beside the body rather than
        below it; shins descending to a ground plane; feet planted. STILL
        STANDING -- two roughly vertical legs under the hem -- is the null
        result and must be reported as the null result.
     P2 DID IT ADOPT THE SKELETON or merely bend? Compare against
        farm-out/jerry-lowerbody-src-0822/jerry-seat-hint-0822.png. Knees at
        x~275 and x~565 against a hip line only 51 px wide is the adoption
        signature; knees at x~350/490 is a bend and is PARTIAL, not a pass.

III. THE SEAM -- the failure mode this design invents.
     S1 Is the join at y 890..920 legible as a body? The pass sees the shirt
        terminate at the cut and must continue it. A visible horizontal step, a
        second hem, or a torso that does not connect to the hips is a FAIL even
        if P1 passes.
     S2 One figure. A skeleton whose head and shoulders lie over pixels the
        pass may not touch could still make the sampler draw a SECOND small
        body inside the mask. Report it if it happens; it is the most
        interesting way this could fail.

THE VERDICT IS THE CONJUNCTION. I1 and P1 and S1 in the same frame. A seated
frame with a broken seam is not a training frame and is not a pass."""

PREDICTED = """FIRST, AND MOST LIKELY: THE SEAM. Nothing in this design aims at
S1. The pass is handed a shirt cut off at a horizontal line and asked to
continue it into a lap while a skeleton tells it where the hips are. A step, a
double hem or a waistband that does not meet the placket is the expected defect
and it is a COMPOSITOR problem after that -- carry the init's own ink across the
join -- not another sampler rung.

SECOND: THE LEGS ARRIVE BUT NOT HIS LEGS. Bare skin, dark shorts and dark boots
are in the prompt nowhere; they are in the init nowhere either, because the init
below the cut is empty background. The pass may draw trousers, or bare feet, or
the wrong skin value. That is a WORDING fix and the wording lever is the one
thing this spec is holding fixed on purpose, so it would be round two's variable
and not a reason to call the route dead.

THIRD, AND IT WOULD CLOSE THE ROUTE: A SECOND FIGURE. The hint carries head,
neck and shoulder keypoints over pixels the pass cannot redraw. If the sampler
answers them by drawing a whole small person inside the mask, the hint has to be
truncated to its leg joints and that is a different spec.

WHAT WOULD SURPRISE ME: a clean seated lower body at the first attempt with a
seam that needs nothing. That would make every remaining goblin beat a masked
derive, and it would make the v3 dataset a day's work rather than an open
research question."""


def sha_of(rel):
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main() -> int:
    write = "--write" in sys.argv

    from PIL import Image
    shas = {}
    for name in (INIT, MASK, HINT):
        rel = "%s/%s" % (SRC_DIR, name)
        p = os.path.join(REPO, rel)
        if not os.path.isfile(p):
            print("!! %s missing -- run "
                  "pipeline/author_jerry_lowerbody_0822.py --write" % rel)
            return 1
        shas[name] = sha_of(rel)
        if Image.open(p).size != (832, 1216):
            print("!! %s is not 832x1216; the driver refuses rc 13 on any "
                  "size disagreement between init, mask and hint." % rel)
            return 1

    np_ = assert_under_clip77("%s prompt" % NEW_ID, PROMPT)
    nn_ = assert_under_clip77("%s negative" % NEW_ID, NEGATIVE)
    assert_no_face_terms(NEW_ID, PROMPT, NEGATIVE)

    farm = lambda n: r"C:\banyan-farm\%s\%s" % (DIRTOK, n)   # noqa: E731

    fetch = '''#!/usr/bin/env python3
"""Fetch the three authored inputs of the masked lower-body pass, by sha256.

  init   his canon frame with the head+torso block moved down 150 px as a rigid
         INTEGER translation (the 180x255 face core is asserted byte-identical
         to taste/refs/goblin-canon-founder-0821.png in the authoring script)
         and the standing legs erased to reconstructed background.
  mask   white below y 900 only. Everything the identity bars score is above it
         and is restored by the inpaint pipeline's latent blend every timestep.
  hint   a COCO-18 skeleton whose head, neck, shoulder, elbow and hip keypoints
         are the CANON'S OWN measurements moved by the same 150 px, and whose
         four leg joints are authored to b13's seat at his measured segment
         lengths (thigh 96 px against his 94, shin+boot 123 against 95-130).

Authored by pipeline/author_jerry_lowerbody_0822.py. $0, no GPU, no sampler."""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\%s"
UA = {"User-Agent": "banyan-city-lowerbody/1.0 (albert.numbro@gmail.com)"}
# THE URL IS WRITTEN OUT IN FULL, per entry, as ADJACENT string literals.
# pipeline/derive_fetch_guard.py re-reads the EMITTED yaml and resolves every
# raw.githubusercontent URL in it against this working tree; a URL assembled at
# run time from a BASE variable is invisible to that check, and the 404 that
# ep2-b08-nogoblin-0820 paid for is exactly what the check exists to catch.
WANT = {
    "%s": ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
           "%s", "%s"),
    "%s": ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
           "%s", "%s"),
    "%s": ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
           "%s", "%s"),
}

os.makedirs(OUT, exist_ok=True)
for name, (url, want) in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %%s -- refusing.\\n   want %%s\\n   have %%s"
                 %% (name, want, have))
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %%s %%d bytes sha %%s OK" %% (name, len(raw), have), flush=True)
''' % (DIRTOK,
       INIT, "%s/%s" % (SRC_DIR, INIT), shas[INIT],
       MASK, "%s/%s" % (SRC_DIR, MASK), shas[MASK],
       HINT, "%s/%s" % (SRC_DIR, HINT), shas[HINT])

    note = (
        "THE MASKED LOWER-BODY PASS. The mask is WHITE ONLY BELOW y 900 and the "
        "strength is %s, which is the opposite configuration to every goblin "
        "round before it and is the point. On base weights (unet.in_channels 4) "
        "the SDXL inpaint pipeline restores the unmasked latent at every "
        "timestep, so his head, ears, eye, collar and placket cannot drift no "
        "matter how high the strength goes, and the legs are free. NO LoRA is "
        "loaded: bnyjerry v2 is where the 21-of-21 standing prior lives and the "
        "identity here is the init's own pixels. %s at %s carries the stance. "
        "PAD-CROP MUST STAY 0 -- b08-arm-route-0819.md section 28 measured that "
        "padding_mask_crop rescales the hint along with the init and turns the "
        "conditioning into a different instruction; the driver refuses that "
        "combination with rc 15 and at 0 the magnification is 1.0. WHAT TO "
        "CHECK ON THE DRY PNG: white starts at row 890 and NOWHERE above it, "
        "the whole width, and the head box (330..510, 350..605) is pure black."
        % (STRENGTH, NET, SCALE))

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "the goblin v3 lane, 2026-08-22 -- authored by "
                     "pipeline/author_jerry_lowerbody_0822.py",
            "consumer": (
                "THE v3 DATASET, and it has no other consumer. bnyjerry v2 "
                "trains identity well and cannot be posed by any lever this "
                "tree owns, because 21 of 21 of its training frames stand. The "
                "fix everyone converges on is v3 on POSED frames of him, and "
                "the open question is how to MAKE one. This job is that "
                "question as a single frame: if the head comes back byte-"
                "identical and the legs come back seated, the dataset factory "
                "exists and four to six stances at $0 is the v3 set. If it does "
                "not, the answer is outside this repo and the research pass "
                "filed alongside this job is what decides the next move."),
            "success": (
                "ONE 832x1216 png in which rows 0..889 are byte-identical to "
                "the init (maxdiff 0, measured not eyeballed) AND the legs "
                "below the cut are SEATED AND JOINED. All three clauses in "
                "`bar` in the same frame. A seated frame with a broken seam is "
                "not a training frame."),
            "why": (
                "EVERY POSE LEVER THIS TREE OWNS IS CLOSED AND THEY ALL CLOSED "
                "THE SAME WAY. Words: B5 fails, `crouching` returns a standing "
                "figure. openpose + LoRA: 0.80 and 0.65 keep his face and never "
                "bend a knee, 0.50 and 0.35 bend nothing and lose his face -- "
                "the two curves do not cross. The two-pass: six cells on an "
                "init that IS a seat, and the only cell that keeps the seat is "
                "the only cell where he is somebody else. i2i from canon: the "
                "face breaks between 0.40 and 0.45 and the pose has not moved "
                "at 0.40.\n\n"
                "ALL FOUR ARE THE SAME SENTENCE -- identity and pose are being "
                "asked of the SAME PIXELS at the same time. This spec stops "
                "asking. His identity is his head, ears, eye and shirt; his "
                "legs are bare skin, dark shorts and dark boots, and there is "
                "nothing about a goblin leg a base checkpoint cannot draw. The "
                "mask puts the first outside the pass and the second inside "
                "it.\n\n"
                "AND A COMPOSITOR ROUTE WAS TRIED FIRST AND FAILED, which is "
                "why the legs are GENERATED rather than warped. Two rounds cut "
                "his canon figure into limb parts and re-posed them by affine "
                "warp. (1) Every frontal seat foreshortens both thighs about "
                "6:1 -- b13's own skeleton draws a 37 px thigh against a 217 px "
                "standing one -- and a 2-D affine can squash pixels along an "
                "axis but cannot draw a limb pointing at the camera. (2) His "
                "shirt hem falls 38 px BELOW his hip, so a seated lower body "
                "drawn behind the garment is ~90% shirt and round one rendered "
                "as a standing figure. (3) Drawn in FRONT of the torso the legs "
                "read as dark blocks: the canon frame gives 29 px of bare shin "
                "against 65 px of boot and his right leg is unusable at all, "
                "planted on a slope and 30% shorter than the left. The "
                "compositor half that DOES work is used here -- the rigid "
                "integer face move and the background reconstruction are both "
                "from that build."),
        },
        overrides={
            "key:node": "002b-first-citizen",
            "key:beat": BEAT,
            "key:priority": 2,
            "key:est_minutes": 4,
            "key:sample": True,
            "payload:fetch_init.py": fetch,
            "payload:inpaint_fruit.py": open(
                os.path.join(REPO, "pipeline/inpaint_fruit.py"),
                encoding="utf-8").read(),
            "payload:prompt.txt": PROMPT + "\n",
            "payload:negative.txt": NEGATIVE + "\n",
            "argv:--init": farm(INIT),
            "argv:--init-sha256": shas[INIT],
            "argv:--mask-png": farm(MASK),
            "argv:--control": farm(HINT),
            "argv:--control-sha256": shas[HINT],
            "argv:--controlnet": NET,
            "argv:--scale": SCALE,
            "argv:--strength": STRENGTH,
            "argv:--seed": str(SEED),
            "argv:--pad-crop": "0",
            "argv:--note": note,
        },
        retoken=[(PARENT_DIRTOK, DIRTOK),
                 (PARENT_OUTTOK, OUTTOK),
                 ("goblin-canon-founder-0821.png", INIT),
                 ("fullframe-mask-0822.png", MASK),
                 ("jerry-canon-h37fsit-0821.png", HINT)],
        extra={
            "bar": BAR,
            "failure_predicted_in_advance": PREDICTED,
            "the_one_variable": (
                "THE MASK. Against the parent: same driver, same net, same "
                "scale 1.0, same --pad-crop 0, same 40 steps, same cfg 7.5, "
                "same seed %d, same negative, same base. What moves is the mask "
                "(all-white -> white below y 900 only) and the two things the "
                "mask forces with it: the strength, which can now be 0.95 "
                "because the protected region is protected by construction "
                "rather than by denoising less, and the init, which is the "
                "canon with the block moved down and the standing legs erased. "
                "The prompt loses exactly one token, `bnyjerry`, because no "
                "LoRA is loaded." % SEED),
            "no_lora_and_that_is_the_design": (
                "There is no --lora flag anywhere in this spec and it is not an "
                "omission. bnyjerry v2 carries the standing prior that every "
                "closed lever above ran into, and the only configuration in "
                "which the openpose net has been observed to drive a pose in "
                "this tree is with no LoRA in the pass -- four of four postures "
                "in the correction to goblin-twopass-route-0822.md Sec 3. The "
                "identity in this frame is the founder's own pixels, held out "
                "of the pass by the mask, so the LoRA has no job here."),
            "pad_crop_is_zero_and_that_is_load_bearing": (
                "0, and the driver would refuse rc 15 otherwise. This mask is "
                "26.8% of the frame in a single band, so padding_mask_crop "
                "would derive a wide short crop and rescale the FULL-FRAME hint "
                "into it -- the b08 section-28 defect, where an authored "
                "skeleton arrived at 3.07x as a different instruction that the "
                "sampler faithfully obeyed while every automatic clause passed "
                "it."),
            "the_hint": (
                "farm-out/jerry-lowerbody-src-0822/%s, sha %s. NOT a stock "
                "skeleton: its head, neck, shoulder, elbow and hip keypoints "
                "are the CANON'S OWN, measured off the founder's file and moved "
                "by the same 150 px integer as the pixels, so the hint and the "
                "init are the same character in the same place. "
                "`author_jerry_skel_0820.figure()` was NOT used -- mapped onto "
                "this frame by crown and foot line its template puts the hip at "
                "y 677 where the canon's is at 812, and a hint that disagrees "
                "with the pixels it conditions is the b08 defect in a new "
                "costume. Only the four leg joints are authored, because only "
                "they are being drawn, and they are authored at HIS segment "
                "lengths: thigh 96 px against his measured 94, shin+boot 123 "
                "against 95-130. Every leg joint is asserted BELOW the cut in "
                "the authoring script -- a keypoint above it would be "
                "conditioning pixels the pass may not redraw, which is a hint "
                "arguing with a latent blend it cannot win."
                % (HINT, shas[HINT])),
        },
        by="pipeline/derive_jerry_lowerbody_0822.py",
    )

    out = os.path.join(REPO, "pipeline", "jobs", NEW_ID + ".yaml")
    if not write:
        print("DRY -- would write %s" % os.path.relpath(out, REPO))
        for name in (INIT, MASK, HINT):
            print("  %-28s %s" % (name, shas[name]))
        print("  prompt tokens  %s" % np_)
        print("  negative tokens %s" % nn_)
        return 0
    derive_spec.write(child, out)
    print("WROTE %s" % os.path.relpath(out, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
