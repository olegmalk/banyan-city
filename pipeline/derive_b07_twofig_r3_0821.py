#!/usr/bin/env python3
r"""BEAT 07 TWO-FIGURE PLATE, ROUND 3: put back the two words I should not have spent.

    python3 pipeline/derive_b07_twofig_r3_0821.py            # dry run
    python3 pipeline/derive_b07_twofig_r3_0821.py --write

WHAT ROUND 2 SETTLED, AND IT IS KEPT VERBATIM
--------------------------------------------------------------------------
Round 2's one variable was the eye clause and IT WORKED: `white eyes,
constricted pupils` in the positive and `round pupils, big round eyes` in the
negative turned round 1's large round green eyes into off-white sclera with
narrow vertical slit pupils, read at 1:1. That clause is carried into this
round UNCHANGED, and so is the whole negative.

WHAT ROUND 2 BROKE, AND WHY -- THIS ROUND IS THE UNDO
--------------------------------------------------------------------------
To buy 5 tokens for the eye clause inside a 77-token budget, round 2 dropped
`muted color` and `boots` from the positive, on the argument that round 1
showed neither was load-bearing because the palette and the boots had come
back correct. THAT ARGUMENT WAS BACKWARDS. They came back correct BECAUSE the
terms were there. Reading the absence of a defect as proof the guard against
it is unnecessary is how a budget gets spent on the wrong thing. Round 2
returned:

  * a warm palette -- blue sky, golden grass, gold-trimmed armour -- entirely
    off the muted sage dialect (`muted color` gone);
  * A HARD-EDGED RECTANGULAR MASK HALO around the goblin. Same IP mask, same
    ip-scale as round 1, which has no halo -- so it is not a mask fault. The
    masked region kept the reference's muted palette while everything outside
    it went warm, and the divergence drew the boundary as a visible box;
  * the guard's pointing hand rendered as BRIGHT GREEN GOBLIN SKIN, aimed up
    and away rather than at the goblin;
  * sandals instead of boots (`boots` gone).

THE ONE CHANGE, AND WHERE THE TOKENS COME FROM
--------------------------------------------------------------------------
`muted color` and `boots` are restored. The 4 tokens are bought from THE GUARD
CLAUSE and nowhere else, because openpose is already carrying everything the
words were duplicating -- his stature, his pose, his position and the raised
arm are all in the skeleton at controlnet scale 1.0, so his wording can shrink
without losing him:

  round 2  "and one tall armored city guard in a helmet at right, facing him,
            arm rising to point"
  round 3  "tall armored guard, helmet, at right, arm rising to point at him"

`facing him` is dropped because the skeleton faces him; `point at him` now
carries the aim, which round 2's hand got wrong. Positive measures 76 of 77,
counted not estimated.

HELD, AND EVERY ONE ON PURPOSE: the eye clause verbatim, the entire negative
verbatim (including `round pupils, big round eyes`, which is what fixed the
eye), the two-figure skeleton at the same sha, the controlnet at scale 1.0,
the square reference, the IP mask 87,485,412,763 -- verified correct by
drawing it on round 1's output -- ip-scale 1.0, the adapter weight, and seed
20260899.

THE PREDICTION: if the halo is what this lane thinks it is -- a palette split
across the mask boundary -- restoring `muted color` removes it WITHOUT the
mask changing, and that is the cheapest possible test of the diagnosis. If the
halo survives a muted palette, the diagnosis was wrong and the next lever is
ip-scale, not wording.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                            # noqa: E402
import derive_fetch_guard                                     # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77     # noqa: E402
from derive_b07_twofig_0821 import BAR, CONTROL, IP_MASK      # noqa: E402
from derive_b07_twofig_r2_0821 import NEGATIVE                # noqa: E402

PARENT = "pipeline/jobs/ep2-b07-twofig-r2-0821.yaml"
PARENT_DIRTOK = "b07twofig-0821"
NEW_ID = "ep2-b07-twofig-r3-0821"
NEW_DIRTOK = "b07twofig-r3-0821"

# 76 of 77, measured. Eye clause verbatim from round 2; `muted color` and
# `boots` restored; the 4 tokens taken out of the guard clause alone.
PROMPT = ("2boys, goblin, green skin, bald, pointy ears, white eyes, slit "
          "pupils, constricted pupils, eyebags, thin eyebrows, mandarin "
          "collar, green shirt, black shorts, boots, standing at left, arms "
          "at sides, tall armored guard, helmet, at right, arm rising to "
          "point at him, muted color, tall grass, full body")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    assert_under_clip77("b07 r3 prompt", PROMPT)
    assert_under_clip77("b07 r3 negative", NEGATIVE)

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "canon-motion plate-fix lane, 2026-08-21",
            "consumer": (
                "THE PLATE BEAT 07'S MOTION SPEC HAS BEEN WAITING TWO ROUNDS "
                "FOR. Beats 02, 03 and 20 went to motion the moment their "
                "plates passed; beat 07 is the only beat of the four with no "
                "usable plate, and therefore the only one with no round-2 clip "
                "at all. If this one clears, its motion rung can be filed off "
                "it. review/ep2-ship-0821 is not touched by this job, and the "
                "founder's per-beat review page reads clips, not plates."),
            "success": (
                "ONE 832x1216 png that keeps round 2's eye and loses round 2's "
                "three regressions. KEPT FROM ROUND 2: K1 off-white sclera with "
                "NARROW VERTICAL SLIT PUPILS at 1:1; K2 the mandarin collar "
                "with its frog closure. RECOVERED FROM ROUND 1: P1 the muted "
                "sage palette -- no blue sky, no golden grass, no gold-trimmed "
                "armour; P2 NO RECTANGULAR HALO around the goblin, the "
                "background continuous across the IP-mask boundary; P3 the "
                "guard's pointing hand is ARMOURED, not green goblin skin, and "
                "is aimed AT him rather than up and away; P4 dark boots, not "
                "sandals. HELD THROUGHOUT: exactly two figures on one ground "
                "line, goblin left and guard right; the guard five heads, "
                "armoured, helmeted, a head and a half taller; both full body "
                "in tall grass. The named degenerate outcome is THE GUARD "
                "THINNING OUT: his wording lost 4 tokens to pay for this, so "
                "if he comes back shorter than five heads, unhelmeted, or "
                "absent, the budget is the cause and the answer is ip-scale "
                "rather than another wording round."),
            "why": (
                "ROUND 2 FIXED THE EYE AND BROKE THREE OTHER THINGS, ALL FROM "
                "ONE BAD TRADE, AND THIS ROUND UNDOES THE TRADE WITHOUT "
                "UNDOING THE FIX.\n\nRound 2's one variable was the eye clause "
                "and it worked: `white eyes, constricted pupils` plus `round "
                "pupils, big round eyes` in the negative produced canon slit "
                "pupils where round 1 had round green eyes. It is kept "
                "verbatim here, negative included.\n\nWhat it cost was paid in "
                "the wrong currency. To fit 5 tokens of eye into 77, round 2 "
                "dropped `muted color` and `boots`, reasoning that round 1 "
                "proved them unnecessary because the palette and boots came "
                "back right. They came back right BECAUSE those terms were "
                "there -- the absence of a defect is not evidence the guard "
                "against it is idle. The result was a warm palette, sandals, a "
                "guard hand made of green goblin skin, and A VISIBLE "
                "RECTANGULAR MASK HALO around the goblin. The halo is the "
                "interesting one: the IP mask and ip-scale are IDENTICAL to "
                "round 1, which has no halo, so the box is not a mask fault -- "
                "it is the masked region holding the reference's muted palette "
                "while everything outside went warm, drawing the boundary.\n\n"
                "WHAT THIS JOB DOES: restores `muted color` and `boots` and "
                "buys the 4 tokens back from THE GUARD CLAUSE only, which is "
                "the one place in the prompt duplicating work the skeleton "
                "already does -- his stature, position, facing and raised arm "
                "are all in the openpose canvas at scale 1.0. Nothing else "
                "moves: not the eye clause, not the negative, not the "
                "skeleton, not the mask, not ip-scale, not the seed.\n\nIT IS "
                "ALSO A TEST OF THE HALO DIAGNOSIS, and a free one. If the halo "
                "is a palette split, a muted palette removes it with the mask "
                "untouched. If it survives, the diagnosis was wrong and the "
                "next lever is ip-scale, not words."),
        },
        overrides={
            "payload:prompt.txt": PROMPT,
            "key:priority": 15,
        },
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THE PROMPT'S BUDGET ALLOCATION, and nothing else in the job. "
                "RESTORED: `muted color` and `boots`. PAID FOR BY the guard "
                "clause alone -- \"and one tall armored city guard in a helmet "
                "at right, facing him, arm rising to point\" becomes \"tall "
                "armored guard, helmet, at right, arm rising to point at "
                "him\". `facing him` goes because the SKELETON faces him, and "
                "`point at him` replaces it carrying the aim that round 2's "
                "hand got wrong. Positive 76 of 77, counted with "
                "animagine-xl-3.1's own vocab. HELD BYTE-FOR-BYTE: round 2's "
                "eye clause, round 2's ENTIRE negative, the two-figure "
                "skeleton %s at the same sha, "
                "xinsir/controlnet-openpose-sdxl-1.0 at scale 1.0, "
                "jerry-canon-sq45-0821.png, the IP mask %s, ip-scale 1.0, "
                "ip-adapter-plus-face_sdxl_vit-h, seed 20260899."
                % (CONTROL, IP_MASK)),
            "the_mistake_this_round_corrects": (
                "STATED PLAINLY BECAUSE IT WAS THIS LANE'S, AND BECAUSE THE "
                "SHAPE OF IT WILL RECUR. Round 2's spec argued: \"round 1 "
                "shows none was load-bearing: the palette, the render quality "
                "and the boots all came back correct, and not one of the three "
                "dropped negatives fired.\" That is an inference from a clean "
                "result to a redundant cause, and it is invalid whenever the "
                "cause is what produced the clean result. In a fixed token "
                "budget every addition is a subtraction, so the question is "
                "never \"did this term fire?\" but \"what was this term "
                "holding?\" -- and the only way to answer it is to look at "
                "what the term describes, not at whether the picture was fine "
                "while it was present."),
            "halo_diagnosis_under_test": (
                "PRE-REGISTERED, AND THE JOB IS ITS OWN EXPERIMENT AT NO EXTRA "
                "COST. CLAIM: round 2's hard-edged rectangle around the goblin "
                "is not an IP-Adapter mask fault but a palette discontinuity "
                "across the mask boundary -- inside kept the reference's muted "
                "sage, outside went warm once `muted color` was dropped. "
                "EVIDENCE FOR IT ALREADY IN HAND: round 1 used the SAME mask "
                "at the SAME ip-scale and has no halo, and the mask box was "
                "separately verified correct by drawing 87,485,412,763 on "
                "round 1's output, where it contains the whole skull, both "
                "ears and the face. FALSIFIABLE HERE: restoring `muted color` "
                "with the mask untouched should remove the box. IF THE HALO "
                "SURVIVES, this diagnosis is wrong, the mask or ip-scale is "
                "implicated after all, and the next lever is ip-scale -- not a "
                "fourth wording."),
            "not_done_on_purpose": (
                "THE NEGATIVE IS NOT TOUCHED, including the temptation to ban "
                "the green hand by name. `green hands` cannot be banned on a "
                "plate whose protagonist has green hands, and the leak is "
                "predicted to be a symptom of the palette rather than a fault "
                "of its own -- banning a symptom would also destroy the test "
                "above. G5 IS STILL NOT ADDRESSED: the arm reads more extended "
                "than the authored mid-raise, which is a skeleton edit "
                "(ARM_ELB / ARM_WRI in "
                "pipeline/author_b07_twofig_skel_0821.py) and would be a "
                "second variable. AND NO MOTION IS FILED BY THIS JOB -- the "
                "beat 07 motion rung waits on a human opening this png, which "
                "is the same rule that kept it unfiled through two rounds."),
        },
        by="pipeline/derive_b07_twofig_r3_0821.py",
        retoken=[(PARENT_DIRTOK, NEW_DIRTOK)],
    )

    # The check round 2 shipped without. derive_spec warns now; this refuses.
    import yaml as _yaml
    blob = _yaml.safe_dump({k: v for k, v in child.items() if k != "derivation"})
    if PARENT_DIRTOK in blob:
        raise SystemExit("!! the parent's box scratch dir survives retokening")
    if NEW_DIRTOK not in blob:
        raise SystemExit("!! the child names no scratch dir of its own")

    out = "pipeline/jobs/%s.yaml" % NEW_ID
    print("%-24s prompt 76/77  negative HELD 73/77  scratch %s"
          % (NEW_ID, NEW_DIRTOK))
    if not a.write:
        print("\n-- dry run. re-run with --write.")
        return 0
    path = derive_spec.write(child, out, force=a.force)
    derive_fetch_guard.assert_fetch_urls_resolve(path, must_hold=(CONTROL,))
    print("   wrote %s  (fetch urls resolve)" % os.path.relpath(path, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
