#!/usr/bin/env python3
r"""ROUND THREE: THE ROUTE IS PROVEN AND THIS IS ITS ONE REMAINING CLAUSE.

WHAT ROUND TWO LANDED, judged at 1:1 on the frame.

    I1 PASS   mean |delta| above the cut 1.247 against a 2.0 bar, no structural
              change, at strength 0.95.
    I2 PASS   his dome, his near-horizontal ears, his narrow almond eye.
    P0 PASS   there are legs.
    P1 PASS   HE IS SEATED. Knees up and out to both sides, occluding the
              torso, shins descending, feet planted.
    P2 PASS   adopted, and slightly past the hint -- knees near x 230 and 640
              against the authored 275 and 565.
    S1 PASS   the seam is INVISIBLE. The shirt continues into a lap with no
              step, no second hem. This clause was untested in round one
              because grass covered the join, and it is the failure mode the
              design was predicted most likely to have.
    S2 PASS   one figure.
    P3 FAIL   and it is the only one. His thighs come back PALE CREAM, not
              desaturated sage, and his feet are rounded dark paws with a white
              cuff rather than boots.

So the route works and the mechanism is settled: a mask splits identity from
pose, and the two stop trading. What is left is a wording defect on a route
whose wording lever has now moved exactly once and moved the entire result --
round one drew no legs at all because wording A's only noun for that region was
grass.

THE ONE VARIABLE IS AGAIN THE WORDING, aimed at P3 and nothing else. Same init
sha, same mask sha, same hint sha, same net, scale 1.0, --pad-crop 0, 40 steps,
cfg 7.5, strength 0.95, seed 20260823, no LoRA.

AND THE COLOUR WORD IS THE RISKY HALF, WHICH IS WHY IT IS PRE-REGISTERED. The
correction to `goblin-twopass-route-0822.md` measured `+ green skin` on a
FULL-FRAME pass turning him saturated kelly with green hair AND deleting the
pose, and recorded "Sage is not one tag". This cell says `bare sage green legs`
rather than a skin term -- `skin` is on the route closure's FACE_TERMS list and
the guard refuses it -- and the pose here is anchored by a mask rather than by
the wording, so the pose half of that failure should not be reachable. If the
legs come back saturated anyway, THE COMPOSITOR TAKES IT: a palette transfer
from the canon's own bare shin onto the rendered thigh is $0, has no sampler in
it and is the house tradition (`beat20_fig_recolor.py`). This is the last
wording rung on P3 either way.

  python3 pipeline/derive_jerry_lowerbody_w3_0822.py            # dry
  python3 pipeline/derive_jerry_lowerbody_w3_0822.py --write
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec                                          # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77   # noqa: E402
from derive_goblin_i2i_0822 import assert_no_face_terms     # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = "pipeline/jobs/ep2-b13-lowerbody-w2-0822.yaml"
NEW_ID = "ep2-b13-lowerbody-w3-0822"

# `bare legs`      -> `bare sage green legs`   (the pale-cream defect)
# `dark boots`     -> `dark leather boots`     (the paw defect)
# Nothing else moves.  `skin` is deliberately absent: it is on the route
# closure's FACE_TERMS list and the guard refuses it, and this clause is about
# his shins rather than his face.
PROMPT = ("1boy, solo, seated, bare sage green legs, dark shorts, "
          "dark leather boots, short grass, detailed cinematic anime, "
          "masterpiece, best quality, very aesthetic")

NEGATIVE = ("pale legs, mittens, paws, "
            "tall grass, overgrown, foliage, bushes, "
            "lowres, worst quality, low quality, text, watermark, "
            "photorealism, 3d render, blurry, 2boys, multiple heads")

NOTE = (
    "ROUND THREE OF THE MASKED LOWER-BODY PASS: P3, AND NOTHING ELSE. Round "
    "two passed every clause but one -- he is seated, the seam is invisible, "
    "his head held at mean |delta| 1.247 -- and failed P3: pale cream thighs "
    "where canon is desaturated sage, and rounded dark paws where canon has "
    "boots. Two nouns move: `bare legs` -> `bare sage green legs` and `dark "
    "boots` -> `dark leather boots`, with `pale legs, mittens, paws` added to "
    "the negative. EVERYTHING ELSE IS BYTE-IDENTICAL TO ROUND TWO: same init "
    "sha 67ad5c8b, same mask sha 81357e39, same hint sha da14ee0b, same net, "
    "scale 1.0, --pad-crop 0, 40 steps, cfg 7.5, strength 0.95, seed 20260823, "
    "no LoRA. WHAT TO CHECK ON THE DRY PNG: byte-identical to rounds one and "
    "two -- white starts at row 890, nowhere above it, full width.")

BAR = """ROUND TWO'S CLAUSES, UNCHANGED, PLUS THE ONE IT FAILED.

HELD (all passed in round two; a regression on any of them means the colour
word reached more than the colour, which is the pre-registered risk):
   I1 mean |delta| above y 890 <= 2.0, no structural change.
   I2 his head at 1:1 against taste/refs/goblin-canon-founder-0821.png.
   P0 legs present.  P1 seated, knees up and out.  P2 adopted.
   S1 the seam at y 884..920 reads as a body.  S2 one figure.

THE CLAUSE THIS CELL EXISTS FOR:
   P3a SKIN VALUE. The bare thigh reads DESATURATED SAGE, matching the canon's
       own bare shin, sampled at (370, 930) on
       taste/refs/goblin-canon-founder-0821.png. Measured, not eyeballed: mean
       RGB of the thigh region against that sample. SATURATED KELLY is a FAIL
       in the other direction and is the pre-registered risk.
   P3b FEET. Boots with an ankle and a sole, not a rounded paw with a cuff.

VERDICT: P3a and P3b, with every held clause still holding. If P3a fails toward
saturation the compositor takes it and no fourth wording rung is filed."""

PREDICTED = """FIRST, AND IT IS THE PRE-REGISTERED RISK: SATURATION. `green` on
a full-frame pass turned him kelly with green hair and deleted the pose, and the
route note already says sage is not one tag. Here the pose is mask-anchored so
the pose half should not be reachable, but the legs may still come back too
saturated. That outcome closes the WORDING lever on P3 and hands it to a
palette-transfer compositor, which is $0 and has no sampler in it.

SECOND: THE FEET DO NOT MOVE. A paw is a small, low-contrast region at the
bottom of a 27% band and `dark leather boots` may simply not reach it. That is
not a route failure; it is an argument for rendering the stance set at a framing
where the feet are larger, or for accepting it in training data where the boots
are dark shapes anyway.

THIRD, AND IT WOULD BE THE EXPENSIVE ONE: THE COLOUR WORD COSTS A HELD CLAUSE.
If the legs go sage AND the stance reverts to two vertical legs, the wording
rule from the twopass correction holds in this regime too and the route needs
wording A restored with the colour done in the compositor.

WHAT WOULD SURPRISE ME: sage legs, real boots and every held clause holding.
That is the stance set unblocked -- four to six frames, about two minutes of
card, and the v3 dataset exists."""


def main() -> int:
    write = "--write" in sys.argv
    assert_under_clip77("%s prompt" % NEW_ID, PROMPT)
    assert_under_clip77("%s negative" % NEW_ID, NEGATIVE)
    assert_no_face_terms(NEW_ID, PROMPT, NEGATIVE)

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "the goblin v3 lane, 2026-08-22 -- round three",
            "consumer": (
                "THE v3 DATASET. Round two proved the route: a mask splits "
                "identity from pose and they stop trading, and the frame is "
                "seated with his head held. What it did not prove is that the "
                "frames are ON MODEL below the cut, and a v3 trained on pale "
                "cream thighs and paw feet would learn pale cream thighs and "
                "paw feet -- the exact way a defect becomes canon. This cell "
                "is the gate between one proof frame and a stance set."),
            "success": (
                "ONE 832x1216 png whose bare thigh reads desaturated sage "
                "against the canon's own shin sample and whose feet are boots, "
                "with every clause round two passed still passing."),
            "why": (
                "ROUND TWO PASSED SEVEN CLAUSES AND FAILED ONE. He is seated, "
                "the knees come up and out past the authored hint, the seam is "
                "invisible, one figure, and his head held at mean |delta| 1.247 "
                "at strength 0.95 -- a strength the i2i route measured as "
                "destroying his face at 0.45. The single failure is P3: pale "
                "cream thighs where canon is desaturated sage, and rounded dark "
                "paws where canon has boots.\n\n"
                "THAT IS A WORDING DEFECT ON A ROUTE WHOSE WORDING LEVER HAS "
                "MOVED ONCE AND MOVED EVERYTHING. Round one drew no legs at all "
                "because wording A's only noun for the masked region was grass; "
                "naming the legs produced legs. Naming their colour and their "
                "footwear is the same lever aimed one clause further.\n\n"
                "AND IT IS THE LAST WORDING RUNG ON P3 EITHER WAY. If the "
                "colour word oversteers to saturated kelly -- the failure the "
                "twopass correction measured on a full-frame pass -- the "
                "compositor takes it: a palette transfer from the canon's own "
                "bare shin costs no GPU and no sampler."),
        },
        overrides={
            "key:priority": 2,
            "payload:prompt.txt": PROMPT + "\n",
            "payload:negative.txt": NEGATIVE + "\n",
            "argv:--note": NOTE,
        },
        extra={
            "bar": BAR,
            "failure_predicted_in_advance": PREDICTED,
            "the_one_variable": (
                "THE WORDING, aimed at P3. Against ep2-b13-lowerbody-w2-0822: "
                "same init sha 67ad5c8b, same mask sha 81357e39, same hint sha "
                "da14ee0b, same net, scale 1.0, --pad-crop 0, 40 steps, cfg "
                "7.5, strength 0.95, seed 20260823, no LoRA. prompt.txt and "
                "negative.txt move and nothing else does."),
            "what_the_route_has_established_in_two_rounds": (
                "1. A MASK SPLITS IDENTITY FROM POSE AND THEY STOP TRADING. "
                "Six previous rounds measured a knob on which his face and his "
                "stance want opposite ends; at strength 0.95 with the head "
                "outside the mask, both are true in the same frame. "
                "2. THE PROMPT CHOOSES THE REGION'S CONTENT, NOT THE HINT. "
                "Round one's skeleton was byte-identical to round two's and "
                "drew no legs, because the positive named grass and not legs. "
                "A skeleton conditions WHERE a body goes; it does not ask for "
                "one. "
                "3. THE SEAM IS A NON-PROBLEM. It was the predicted most-likely "
                "failure and it is invisible in the landed frame. "
                "4. THE PROTECTED REGION IS NOT BYTE-EXACT AND THAT IS FIXED "
                "OUTSIDE THE SAMPLER. --pad-crop 0 means diffusers never calls "
                "apply_overlay, so the head takes one VAE round trip; "
                "pipeline/jerry_lowerbody_restore_0822.py pastes the init's own "
                "rows back and asserts the result byte-identical."),
        },
        retoken=[("b13lowerbodyw2-0822", "b13lowerbodyw3-0822"),
                 ("b13-lowerbody-w2-s20260823", "b13-lowerbody-w3-s20260823"),
                 ("b13-lowerbody-w2-DRY", "b13-lowerbody-w3-DRY")],
        by="pipeline/derive_jerry_lowerbody_w3_0822.py",
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
