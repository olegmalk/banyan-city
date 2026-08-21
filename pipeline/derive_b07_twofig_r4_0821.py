#!/usr/bin/env python3
r"""BEAT 07, ROUND 4: stop paying for the goblin's face in tokens.

    python3 pipeline/derive_b07_twofig_r4_0821.py            # dry run
    python3 pipeline/derive_b07_twofig_r4_0821.py --write

THIS IS A RECIPE CHANGE, NOT A FOURTH WORDING ROUND, AND IT IS ONE SAMPLE.
--------------------------------------------------------------------------
Three rounds established that the wall is the 77-token CLIP budget and not the
wording. Every attribute has been achieved in some round and never all in one:

  attribute            R1     R2     R3
  goblin slit pupils   FAIL   PASS   PASS
  muted palette        PASS   FAIL   PASS
  no mask halo         PASS   FAIL   PASS
  guard hand armoured  PASS   FAIL   PASS
  boots                PASS   FAIL   PASS
  guard helmeted human PASS   PASS   FAIL

Each round was a zero-sum reallocation of the same tokens. So this round stops
reallocating and removes a claimant instead: THE GOBLIN'S FACE COMES OFF THE
PROMPT ENTIRELY and is left to the instrument that was always carrying it.

WHY THAT IS SAFE TO TRY. The IP-Adapter reference jerry-canon-sq45-0821.png is
the founder's own image cropped to the head box plus 18 px -- wide enough that
it contains the ears, which project 27% of a skull width each side -- flooded
to a flat field and centred at 45% head-of-frame on a square canvas. It is a
face reference and nothing else. Its mask, 87,485,412,763, has now been
verified correct THREE separate ways: drawn on round 1's output it contains the
whole skull, both ears and the face; round 3's halo test cleared with the mask
byte-identical, which exonerated it again; and no round has ever leaked the
adapter onto the guard except when the palette diverged.

  DELETED from the positive: `white eyes, slit pupils, constricted pupils,
  eyebags, thin eyebrows`. Those five describe the face the reference holds.
  KEPT: `goblin, green skin, bald, pointy ears` -- the species anchor. Deleting
  those too would risk the model not drawing a goblin at all, and they are
  cheap; the authorisation was to drop the identity TAGS, not the noun.

IP-SCALE 1.0 -> 1.25, AND THE K2 PRECEDENT SAYS WHAT TO WATCH.
--------------------------------------------------------------------------
The face now has no word-side support, so the adapter is raised to compensate.
The size of the step is argued rather than picked: the k-ladder's own step was
0.7 -> 0.9, +29% relative, and 1.0 -> 1.25 is the same relative move. It is a
real raise -- a timid one would answer nothing on a single sample -- and the
failure it risks is already scored below.

k2 (`ep2-jerry-face-k2-0821`) is the precedent and it is explicit about the
direction of the damage: more adapter strength "should pull the eye further
toward the reference's proportions ... while pulling the HEAD further toward a
reference that is 100% head", and the outcome that would stop the route is
"containment breaks -- seated, purple cowl, or the tile's field". So the two
regressions to look for are HEAD INFLATION (a bobblehead; k2 predicted head_frac
climbing and heads-tall falling through its 4.5 bar) and CONTAINMENT BLEED (the
reference's own framing or background arriving in the plate).

THAT RISK IS LIVE HERE AND NOT THEORETICAL: this lane's goblin already reads
head-heavy and childlike in ALL THREE rounds at ip-scale 1.0. If 1.25 makes
that worse, the instruction is to RECORD AND STOP -- not to open a round 5.

THE FREED BUDGET GOES TO THE GUARD, ALL OF IT.
--------------------------------------------------------------------------
Round 3 lost him because his wording lost `city`, `in a helmet` as a phrase and
`facing him`. All of it is restored and then some: `one tall human city guard
in full armor and a closed helmet at right, a full head taller, facing him, arm
rising to point`. `human` is explicit because round 3 returned a bare green
goblin skull on his shoulders, and `a full head taller` is the G3 bar written
into the prompt. The negative gains `two goblins, goblin guard, bare head` --
the round-3 defect banned by name -- paid for by dropping `orange eyes`, `third
eye`, `eyepatch` and `glowing eyes`, none of which has ever fired in four
rounds.

Positive 72 of 77, negative 75 of 77, both counted and not estimated. HELD: the
skeleton at the same sha, controlnet scale 1.0, the reference, the mask, the
seed 20260899, `muted color` and `boots` -- the two terms round 3 proved
load-bearing.
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
from derive_b07_twofig_0821 import CONTROL, IP_MASK           # noqa: E402

PARENT = "pipeline/jobs/ep2-b07-twofig-r3-0821.yaml"
PARENT_DIRTOK = "b07twofig-r3-0821"
NEW_ID = "ep2-b07-twofig-r4-0821"
NEW_DIRTOK = "b07twofig-r4-0821"
IP_SCALE = "1.25"

# 72 of 77. The goblin's FACE is gone from here on purpose; the adapter has it.
PROMPT = ("2boys, goblin, green skin, bald, pointy ears, mandarin collar, "
          "green shirt, black shorts, boots, standing at left, arms at sides, "
          "and one tall human city guard in full armor and a closed helmet at "
          "right, a full head taller, facing him, arm rising to point, muted "
          "color, tall grass, full body")

# 75 of 77. `two goblins, goblin guard, bare head` is round 3's defect banned
# by name; `human face on the goblin` is kept because the positive no longer
# says anything about his face at all.
NEGATIVE = ("lowres, worst quality, low quality, text, blank eyes, no pupils, "
            "round pupils, big round eyes, thick eyebrows, cloak, hood, "
            "patchwork, human face on the goblin, two goblins, goblin guard, "
            "bare head, old man, hair, beard, child, chibi, 3boys, crowd, "
            "multiple heads, disembodied head")

BAR = """JUDGED BY EYE AT 1:1, BOTH IDENTITIES, AND THE HEAD IS SCORED FIRST.

  A1  THE GOBLIN IS STILL THE FOUNDER'S GOBLIN WITH NO WORDS HELPING. Read
      against taste/refs/goblin-canon-founder-0821.png: off-white sclera with
      NARROW VERTICAL SLIT PUPILS, eyebags, thin brows, green skin, bald,
      large pointed ears. This is the whole experiment -- if the adapter can
      hold the face alone, the token budget stops being the wall for every
      two-character plate in this show, not just this one.
  A2  HE IS NOT A BOBBLEHEAD. THE K2 REGRESSION, AND IT IS SCORED BEFORE THE
      FACE IS ADMIRED. His head must not be visibly larger relative to his
      body than in rounds 1-3 at ip-scale 1.0. k2 predicted exactly this when
      strength went up against a reference that is 100% head, and this goblin
      already reads head-heavy at 1.0.
  A3  NO CONTAINMENT BLEED. The reference's own flat flooded field, its square
      framing, or its crop must not appear in the plate. k2 named containment
      as the outcome that stops the route.
  G1  EXACTLY TWO FIGURES, both whole, one ground line, goblin left.
  G2  THE GUARD IS A HELMETED HUMAN. A CLOSED HELMET on his head -- not a bare
      skull, not green, not pointed ears. Round 3 returned a goblin in armour
      and that is the defect this round's freed budget was spent to fix.
  G3  HE IS A GROWN MAN, five heads, a full head taller, in full plate. The
      founder's 2026-08-20 ruling: "they should look like grown men. yes. dumb
      grown men."
  G4  NO ADAPTER LEAK ONTO HIM -- armoured gauntlet, not green skin.
  P1  MUTED SAGE PALETTE, no halo, dark boots. All three were won in round 3
      and a regression on any is a FAIL even if the faces are perfect.

A2 or A3 failing means the SCALE is wrong, and the instruction for that outcome
is RECORD AND STOP, not round 5. A1 failing with A2/A3 clean means the adapter
cannot hold the face alone at any strength, which closes this route cleanly and
is worth knowing. Only all of A1-A3, G1-G4 and P1 together is a pass."""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    assert_under_clip77("b07 r4 prompt", PROMPT)
    assert_under_clip77("b07 r4 negative", NEGATIVE)

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "canon-motion plate-fix lane, 2026-08-21",
            "consumer": (
                "THE PLATE BEAT 07'S MOTION SPEC IS STILL WAITING FOR, after "
                "three rounds in which no plate passed on both figures. If "
                "this one clears, the beat 07 motion rung gets filed off it "
                "immediately using the laws the passing three (04, 08, 13) "
                "ran on. ITS SECOND CONSUMER IS EVERY FUTURE TWO-CHARACTER "
                "PLATE IN THIS SHOW: if the IP-Adapter can hold the founder's "
                "goblin with no face words at all, the 77-token budget stops "
                "being the wall wherever two characters have to share it."),
            "success": (
                "ONE 832x1216 png in which BOTH identities are right at once "
                "for the first time. A1 the goblin is the founder's goblin -- "
                "off-white sclera, narrow vertical slit pupils, eyebags, thin "
                "brows, green, bald, large pointed ears -- WITH NO FACE WORDS "
                "IN THE PROMPT; A2 he is NOT a bobblehead, his head no larger "
                "relative to his body than at ip-scale 1.0 in rounds 1-3; A3 "
                "no containment bleed -- none of the reference's flat field, "
                "square framing or crop in the plate; G1 exactly two figures, "
                "whole, one ground line; G2 THE GUARD WEARS A CLOSED HELMET "
                "and is human -- not a bare green skull with pointed ears, "
                "which is what round 3 returned; G3 five heads, a full head "
                "taller, full plate; G4 armoured gauntlet, no green hand; P1 "
                "muted sage palette, no mask halo, dark boots, all three held "
                "from round 3. The named degenerate outcome is THE BOBBLEHEAD: "
                "k2 predicted that raising adapter strength against a "
                "reference that is 100% head inflates the head, this goblin "
                "already reads head-heavy at 1.0, and A2 is therefore scored "
                "BEFORE the face is admired."),
            "why": (
                "THREE ROUNDS PROVED THE WALL IS THE TOKEN BUDGET, SO THIS "
                "ROUND REMOVES A CLAIMANT INSTEAD OF MOVING TOKENS "
                "AROUND.\n\nR1 had the guard and missed the eye. R2 had the "
                "eye and lost the palette, the mask boundary, the guard's hand "
                "and the boots. R3 had the eye, the palette, no halo, the hand "
                "and the boots, and lost the guard -- he came back as a bare "
                "green goblin skull in armour. Every attribute has been "
                "achieved in some round and never all in one, and every round "
                "was the same 77 tokens reallocated. That is a structural "
                "result, not a wording problem.\n\nWHAT THIS JOB DOES: takes "
                "the goblin's FACE off the prompt entirely -- `white eyes, "
                "slit pupils, constricted pupils, eyebags, thin eyebrows` are "
                "deleted -- and leaves it to the IP-Adapter reference, which "
                "is a head-and-ears crop of the founder's own image and has "
                "been carrying it all along. The adapter is raised 1.0 -> 1.25 "
                "to compensate, the same +29% relative step the k-ladder used "
                "at 0.7 -> 0.9. Every freed token goes to the guard: `human` "
                "and `closed helmet` are explicit because round 3 returned "
                "neither, `a full head taller` writes the G3 bar into the "
                "prompt, and `two goblins, goblin guard, bare head` bans the "
                "round-3 defect by name.\n\nWHAT IS HELD: the skeleton at the "
                "same sha, controlnet scale 1.0, the reference, the mask "
                "87,485,412,763, seed 20260899, and `muted color` and `boots` "
                "-- the two terms round 3 proved were load-bearing when round "
                "2 spent them.\n\nWHAT STOPS THE ROUTE: k2 is explicit that "
                "raising strength pulls the head toward a reference that is "
                "100% head. If A2 or A3 fires, this is RECORDED AND STOPPED at "
                "one sample -- beat 07 keeps its slot in the founder's "
                "per-beat queue with the three-round table as its record."),
        },
        overrides={
            "argv:--ip-scale": IP_SCALE,
            "payload:prompt.txt": PROMPT,
            "payload:negative.txt": NEGATIVE,
            "key:priority": 15,
        },
        extra={
            "bar": BAR,
            "the_one_variable": (
                "WHERE THE GOBLIN'S FACE COMES FROM: tokens, or the adapter. "
                "That is one mechanism even though it touches three fields, "
                "and the three move together by necessity -- deleting the face "
                "words is what frees the budget, raising ip-scale is what "
                "replaces them, and the guard clause is what the freed budget "
                "was freed FOR. DELETED from the positive: `white eyes, slit "
                "pupils, constricted pupils, eyebags, thin eyebrows`. RAISED: "
                "--ip-scale 1.0 -> %s. RESTORED AND EXTENDED: the full guard "
                "clause plus `human`, `closed helmet` and `a full head "
                "taller`, with `two goblins, goblin guard, bare head` added to "
                "the negative. HELD BYTE-FOR-BYTE: the two-figure skeleton %s "
                "at the same sha, xinsir/controlnet-openpose-sdxl-1.0 at scale "
                "1.0, jerry-canon-sq45-0821.png, the IP mask %s, "
                "ip-adapter-plus-face_sdxl_vit-h, seed 20260899, `muted color` "
                "and `boots`." % (IP_SCALE, CONTROL, IP_MASK)),
            "the_step_size_and_why_it_is_that_size": (
                "1.0 -> 1.25 is the SAME RELATIVE MOVE the k-ladder made when "
                "it tested this dial: k1 -> k2 went 0.7 -> 0.9, +29%. A timid "
                "raise answers nothing on a single sample and a large one "
                "guarantees the bobblehead, so the step that already has "
                "precedent in this tree is the defensible one. Note the "
                "starting point is itself already above the k-ladder's chosen "
                "0.7 -- the canon-plate route moved to 1.0 with a different "
                "reference -- so 1.25 is unexplored territory for this show "
                "and is being entered with A2 scored first and a stop rule "
                "attached."),
            "failure_predicted_in_advance": (
                "THE BOBBLEHEAD, NAMED BY k2 BEFORE THIS LANE EXISTED. "
                "ep2-jerry-face-k2-0821 filed, for the same dial: more adapter "
                "strength 'should pull the eye further toward the reference's "
                "proportions ... while pulling the HEAD further toward a "
                "reference that is 100% head', and it named containment "
                "breaking -- 'seated, purple cowl, or the tile's field' -- as "
                "the outcome that stops the route. BOTH ARE LIVE HERE AND ONE "
                "IS ALREADY HALF-PRESENT: this lane's goblin reads head-heavy "
                "and childlike in all three rounds at 1.0, so 1.25 has less "
                "headroom than k2 had. SECOND, AND SPECIFIC TO DELETING THE "
                "WORDS: the negative still bans `round pupils, big round eyes` "
                "but the positive no longer asks for slits, so the adapter is "
                "unopposed AND unassisted -- if it returns a blank or "
                "featureless eye that is a FAIL of A1, not a partial win. "
                "THIRD: `2boys` with only one face reference may hand the "
                "guard the goblin's head again, which is why `two goblins, "
                "goblin guard, bare head` is in the negative."),
            "stop_rule": (
                "ONE SAMPLE, AND A2 OR A3 ENDS THE ROUTE. If raising ip-scale "
                "inflates the head or bleeds the reference's containment into "
                "the plate, this is RECORDED AND STOPPED -- no round 5, no "
                "ladder of scales. Beat 07 then keeps its slot in the "
                "founder's per-beat iteration queue with the three-round "
                "attribute table as its record, and the next move is his. This "
                "is written into the spec because a scale ladder is exactly "
                "the kind of thing a lane talks itself into at 2am after a "
                "near miss."),
            "not_done_on_purpose": (
                "THE SKELETON IS NOT TOUCHED, so G5 -- the arm reading more "
                "extended than the authored mid-raise -- is still open and is "
                "still not this round's question. NO MOTION IS FILED BY THIS "
                "JOB EITHER; the beat 07 motion rung waits on a human opening "
                "this png, which is the rule that has kept it unfiled through "
                "three rounds and is the reason no GPU time has been spent "
                "animating an off-canon character."),
        },
        by="pipeline/derive_b07_twofig_r4_0821.py",
        retoken=[(PARENT_DIRTOK, NEW_DIRTOK)],
    )

    import yaml as _yaml
    blob = _yaml.safe_dump({k: v for k, v in child.items() if k != "derivation"})
    if PARENT_DIRTOK in blob:
        raise SystemExit("!! the parent's box scratch dir survives retokening")
    if NEW_DIRTOK not in blob:
        raise SystemExit("!! the child names no scratch dir of its own")
    if '"%s"' % IP_SCALE not in blob and IP_SCALE not in blob:
        raise SystemExit("!! --ip-scale did not reach the child")

    out = "pipeline/jobs/%s.yaml" % NEW_ID
    print("%-24s prompt 72/77  negative 75/77  ip-scale %s  scratch %s"
          % (NEW_ID, IP_SCALE, NEW_DIRTOK))
    if not a.write:
        print("\n-- dry run. re-run with --write.")
        return 0
    path = derive_spec.write(child, out, force=a.force)
    derive_fetch_guard.assert_fetch_urls_resolve(path, must_hold=(CONTROL,))
    print("   wrote %s  (fetch urls resolve)" % os.path.relpath(path, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
