#!/usr/bin/env python3
r"""ROUND TWO OF THE MASKED LOWER-BODY PASS, AND THE VARIABLE IS THE WORDING.

WHAT ROUND ONE MEASURED, on the landed frame rather than on its filename.

  * THE MASK DESIGN WORKS AS COMPOSITION. His head, ears, eye, collar and
    placket came back in place, unchanged in content, at strength 0.95 -- a
    strength every previous goblin round measured as destroying his face. The
    latent blend held. Mean |delta| above the cut is 1.4.
  * IT IS NOT BYTE-EXACT, AND THE REASON IS MECHANICAL RATHER THAN A LEAK.
    93.9% of pixels above the cut changed by at least one level and the head box
    reads maxdiff 98 on ink edges. diffusers only pastes the original back in
    PIXEL space inside its `padding_mask_crop` branch (`apply_overlay`), and
    this route sets --pad-crop 0 on purpose, so the unmasked region survives as
    LATENTS and takes one VAE round trip. That is a compositor fix, not a
    sampler one, and it is free: paste the init's own rows back.
  * THE POSE CLAUSE IS NULL AND THE CAUSE IS THE PROMPT. The pass filled the
    whole masked band with TALL GRASS -- row luminance falls 128 -> 73 between
    y 880 and y 1000 -- and drew no legs at all. There is nothing wrong with the
    seat; there is nothing there.

WHY THAT IS THE PROMPT AND NOT THE NET. `ep2-b08-nostrap2-0820` measured this
lever directly and stated it as a rule: THE PROMPT CHOOSES NOUNS. Taking
`goblin` out of a positive took the goblin out of the picture at unchanged
strength, in-mask G-R moving -2.83 -> -16.06. Round one's positive is wording A
and wording A says `in tall grass`. The mask handed the sampler the bottom 27%
of the frame and the only noun the prompt offered for it was grass, so it drew
grass. A skeleton cannot out-vote a noun for a region's CONTENT; it conditions
where a body goes, not whether one is asked for.

THE ONE VARIABLE IS THEREFORE THE WORDING, and it moves in one coherent edit:
the noun that arrived comes out of the positive and goes into the negative, and
the nouns that must arrive -- his legs -- go in. Nothing else moves: same init
sha, same mask sha, same hint sha, same net, same scale 1.0, same --pad-crop 0,
same 40 steps, same cfg 7.5, same strength 0.95, same seed 20260823, no LoRA.

AND THE WORDING-A RULE IS NOT BEING BROKEN, IT IS BEING SCOPED. The correction
to `goblin-twopass-route-0822.md` measured that ANY addition to pass one's
wording costs the pose. That was measured on FULL-FRAME txt2img-with-ControlNet
where the wording was the only thing choosing the composition. Here the
composition above the cut is fixed pixels the pass may not touch and the stance
below it is a hint over a 27% band. If the pose still fails on this cell, the
wording rule has just been shown to hold in a second regime and that is worth
the twenty-five seconds; if it lands, the rule is a property of the unconstrained
case. Either reading is a finding.

  python3 pipeline/derive_jerry_lowerbody_w2_0822.py            # dry
  python3 pipeline/derive_jerry_lowerbody_w2_0822.py --write
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec                                          # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77   # noqa: E402
from derive_goblin_i2i_0822 import assert_no_face_terms     # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = "pipeline/jobs/ep2-b13-lowerbody-0822.yaml"
NEW_ID = "ep2-b13-lowerbody-w2-0822"

# OUT: `in tall grass`, the noun that filled the band.
# IN:  `seated`, and the three nouns his lower body is made of.  They are named
#      because the init below the cut is EMPTY BACKGROUND -- the standing legs
#      were erased by the authoring script -- so the pass has neither pixels nor
#      words telling it what a goblin leg is made of.
PROMPT = ("1boy, solo, seated, bare legs, dark shorts, dark boots, "
          "short grass, detailed cinematic anime, masterpiece, best quality, "
          "very aesthetic")

# `tall grass` and its neighbours are the KIND that arrived. b08 measured that a
# negative removes a KIND cleanly (the goblin went, completely) and cannot
# remove a COUNT; this is a kind.
NEGATIVE = ("tall grass, overgrown, foliage, bushes, "
            "lowres, worst quality, low quality, text, watermark, "
            "photorealism, 3d render, blurry, 2boys, multiple heads")

NOTE = (
    "ROUND TWO OF THE MASKED LOWER-BODY PASS: THE WORDING, AND NOTHING ELSE. "
    "Round one held the head at strength 0.95 -- the mask design works -- and "
    "filled the entire masked band with TALL GRASS, drawing no legs at all. "
    "Row luminance falls 128 to 73 between y 880 and y 1000. The prompt chooses "
    "nouns (ep2-b08-nostrap2-0820) and wording A's only noun for that region "
    "was grass. So `in tall grass` leaves the positive for the negative, and "
    "`seated, bare legs, dark shorts, dark boots` arrives -- the init below the "
    "cut is empty background, so the pass has neither pixels nor words for what "
    "a goblin leg is made of. EVERYTHING ELSE IS BYTE-IDENTICAL TO ROUND ONE: "
    "same init sha, same mask sha, same hint sha, same net, scale 1.0, "
    "--pad-crop 0, 40 steps, cfg 7.5, strength 0.95, seed 20260823, no LoRA. "
    "WHAT TO CHECK ON THE DRY PNG: it must be byte-identical to round one's dry "
    "mask -- white starts at row 890, nowhere above it, full width. If it "
    "differs at all, something other than the wording moved and this job stops "
    "here at $0.")

BAR = """ROUND ONE'S THREE CLAUSES, WITH I1 CORRECTED BY WHAT IT MEASURED.

I. IDENTITY ABOVE THE CUT.
   I1 (CORRECTED) The bar is NOT maxdiff 0. Round one wrote that and the frame
      refuted it: diffusers only pastes the original back in pixel space inside
      the `padding_mask_crop` branch, and this route runs --pad-crop 0, so the
      protected region survives as LATENTS and takes one VAE round trip. Round
      one read mean |delta| 1.425 with head-box maxdiff 98 on ink edges. THE
      BAR IS THAT NUMBER, HELD: mean |delta| above y 890 <= 2.0 and no
      structural change. A rise would mean the blend is leaking; the residual
      is removed for free by a compositor paste and is not a sampler question.
   I2 Read the head at 1:1 against taste/refs/goblin-canon-founder-0821.png:
      narrow almond eye, tiny dark pupil, broad low dome, near-horizontal ears,
      smooth face, desaturated sage. Round one PASSED this.

II. POSE -- and this is the clause the cell exists for, because round one's is
    NULL rather than failed.
   P0 ARE THERE LEGS AT ALL? Round one drew none. This is now the first
      question and a frame with no visible lower limb is a FAIL, not a null.
   P1 IS HE SEATED? Knees up and out, arriving beside the body rather than
      below it; shins descending; feet planted. Two vertical legs is the null.
   P2 DID IT ADOPT THE SKELETON? Knees near x 275 and x 565 against a hip line
      51 px wide is adoption. Knees near x 350 / 490 is a bend and is PARTIAL.
   P3 ARE THEY HIS? Bare sage shins, dark shorts, dark boots. Trousers, bare
      feet or a wrong skin value is a wording defect and gets reported as one.

III. THE SEAM. Round one's grass hid the join entirely, so S1 is UNTESTED and
     arrives for the first time on this cell.
   S1 The join at y 890..920 reads as a body: no horizontal step, no second
      hem, the shirt continuing into a lap.
   S2 One figure.

VERDICT: P0 and P1 and S1 in the same frame, with I1 held."""

PREDICTED = """FIRST, AND MOST LIKELY: THE LEGS ARRIVE AND THE SEAM DOES NOT.
Round one never tested S1 because grass covered it. The pass is handed a shirt
cut off at a horizontal line and must continue it into a lap while a skeleton
says where the hips are. A step, a double hem or a waistband that misses the
placket is the expected defect, and after that it is a COMPOSITOR problem --
carry the init's own ink across the join -- not another sampler rung.

SECOND: THE LEGS ARRIVE AND ARE NOT SEATED. Two vertical legs under the hem
would say the hint does not reach a 27% band at scale 1.0 while the preserved
latent above it holds a standing torso. That is a SCALE question and it has a
cheap next cell (1.4, which round seven of B2 already ran on the full frame),
not a route closure.

THIRD, AND IT WOULD BE THE INTERESTING FAILURE: THE WORDING RULE HOLDS HERE TOO
and adding four nouns costs the stance -- legs arrive, standing, and the frame
looks like round one's with grass swapped for boots. That would make the wording
rule general rather than a property of unconstrained txt2img, and the next move
would be a hint-only lever with wording A restored.

WHAT WOULD SURPRISE ME: seated, jointed and his colours at the first wording
edit. That is the v3 dataset factory and four to six stances follow the same
afternoon."""


def main() -> int:
    write = "--write" in sys.argv
    assert_under_clip77("%s prompt" % NEW_ID, PROMPT)
    assert_under_clip77("%s negative" % NEW_ID, NEGATIVE)
    assert_no_face_terms(NEW_ID, PROMPT, NEGATIVE)

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "the goblin v3 lane, 2026-08-22 -- round two",
            "consumer": (
                "THE v3 DATASET, unchanged. Round one proved the MASK half of "
                "the design -- his head survived a strength that has destroyed "
                "it in every previous round -- and left the POSE half untested, "
                "because the sampler filled the region with grass instead of a "
                "body. This cell asks whether the region can be made to contain "
                "legs. If it can and they are seated, the factory exists and "
                "four to six stances is the v3 set."),
            "success": (
                "ONE 832x1216 png with VISIBLE LOWER LIMBS that are SEATED and "
                "JOINED to the preserved torso, with mean |delta| above y 890 "
                "still at or below 2.0. Round one's null -- no legs -- is a "
                "FAIL of this cell, not a null."),
            "why": (
                "THE PROMPT CHOOSES NOUNS, AND ROUND ONE'S ONLY NOUN FOR THE "
                "MASKED REGION WAS GRASS. Wording A is `1boy, solo, in tall "
                "grass, ...`; the mask handed the sampler the bottom 27% of the "
                "frame; it drew tall grass and no legs, row luminance falling "
                "128 to 73 between y 880 and y 1000. `ep2-b08-nostrap2-0820` "
                "measured this lever and named it: removing `goblin` from a "
                "positive removed the goblin entirely at unchanged strength. A "
                "skeleton conditions WHERE a body goes; it does not ask for "
                "one.\n\n"
                "SO THE NOUN THAT ARRIVED LEAVES THE POSITIVE FOR THE NEGATIVE "
                "AND THE NOUNS THAT MUST ARRIVE GO IN. The init below the cut "
                "is empty background -- the authoring script erased the "
                "standing legs -- so the pass has neither pixels nor words for "
                "what a goblin leg is made of, and `bare legs, dark shorts, "
                "dark boots` supplies the second half of that.\n\n"
                "THE WORDING-A RULE IS SCOPED HERE, NOT BROKEN. The correction "
                "to goblin-twopass-route-0822.md measured that any addition to "
                "pass one's wording costs the pose -- on FULL-FRAME "
                "txt2img-with-ControlNet, where the wording was the only thing "
                "choosing the composition. Here the composition above the cut "
                "is fixed pixels. If the stance still fails, that rule has been "
                "shown to hold in a second regime, which is itself the finding."),
        },
        overrides={
            "key:priority": 2,
            "key:est_minutes": 4,
            "payload:prompt.txt": PROMPT + "\n",
            "payload:negative.txt": NEGATIVE + "\n",
            "argv:--note": NOTE,
        },
        extra={
            "bar": BAR,
            "failure_predicted_in_advance": PREDICTED,
            "the_one_variable": (
                "THE WORDING. Against ep2-b13-lowerbody-0822: same init sha "
                "67ad5c8b, same mask sha 81357e39, same hint sha da14ee0b, same "
                "net, same scale 1.0, same --pad-crop 0, same 40 steps, same "
                "cfg 7.5, same strength 0.95, same seed 20260823, no LoRA in "
                "either. prompt.txt and negative.txt move and nothing else "
                "does."),
            "what_round_one_measured": (
                "MASK HALF PASSES: mean |delta| above the cut 1.425, the head "
                "in place and on model at 1:1, at strength 0.95 -- a strength "
                "the i2i route measured as destroying his face at 0.45. POSE "
                "HALF NULL: the band is tall grass and there are no legs. "
                "SEAM UNTESTED: the grass covered the join, so S1 arrives for "
                "the first time on this cell. AND I1 WAS WRONG AS WRITTEN: it "
                "asked for maxdiff 0 and the frame reads 93.9% of pixels "
                "changed by at least one level with head-box maxdiff 98, "
                "because diffusers only re-pastes in pixel space inside its "
                "padding_mask_crop branch and this route runs --pad-crop 0 on "
                "purpose. The protected region survives as latents and takes "
                "one VAE round trip. The bar is corrected, and the residual is "
                "removed by a $0 compositor paste rather than by a sampler "
                "change."),
        },
        retoken=[("b13lowerbody-0822", "b13lowerbodyw2-0822"),
                 ("b13-lowerbody-s20260823", "b13-lowerbody-w2-s20260823"),
                 ("b13-lowerbody-DRY", "b13-lowerbody-w2-DRY")],
        by="pipeline/derive_jerry_lowerbody_w2_0822.py",
    )

    out = os.path.join(REPO, "pipeline", "jobs", NEW_ID + ".yaml")
    if not write:
        print("DRY -- would write %s" % os.path.relpath(out, REPO))
        print("  positive: %s" % PROMPT)
        print("  negative: %s" % NEGATIVE)
        return 0
    derive_spec.write(child, out)
    print("WROTE %s" % os.path.relpath(out, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
