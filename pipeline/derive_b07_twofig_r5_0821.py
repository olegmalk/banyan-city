#!/usr/bin/env python3
r"""BEAT 07, ROUND 5: the two terms round 4 proved the adapter does not carry.

    python3 pipeline/derive_b07_twofig_r5_0821.py            # dry run
    python3 pipeline/derive_b07_twofig_r5_0821.py --write

THIS COMPLETES ROUND 4'S DECOMPOSITION AND IS NOT A NEW QUESTION.
--------------------------------------------------------------------------
Round 4 deleted every goblin face word and raised ip-scale 1.0 -> 1.25. It
scored 7 of 9 and produced the decomposition this round acts on:

  THE ADAPTER CARRIES EYE SHAPE. With no face words at all it returned the
  species, the bald skull, the large pointed ears, the skin, and NARROW
  VERTICAL SLIT PUPILS -- the hardest, most canon-specific feature and the one
  six k-ladder wording rungs never reached.

  THE WORDS WERE CARRYING EYE COLOUR AND SMALL DETAIL. What round 4 lost was
  the OFF-WHITE SCLERA (came back green) and the EYEBAGS.

So exactly those two go back in, and nothing else about the recipe moves. This
is the change round 4's own finding licenses by name.

ALSO SETTLED BY ROUND 4, AND HELD HERE: ip-scale 1.25 is SAFE on this
reference and this mask. k2's bobblehead was the gating risk and it did not
fire -- at an identical crop box R4's head is the same size relative to his
body as R1's and R3's at 1.0, if anything a shade smaller. The faint ring
ghosting in the field is equally present in R3 at 1.0, so it is pre-existing
and not a scale artefact. The scale therefore stays at 1.25 rather than being
walked back: it is what is buying the slit pupil with the words gone.

THE ONE HONEST DEVIATION FROM "BYTE-IDENTICAL PLUS TWO TERMS"
--------------------------------------------------------------------------
`white eyes, eyebags` costs SIX CLIP tokens, not the four this lane estimated
when it reported five free. Counted, round 4's positive is 72 and adding them
makes 78 -- one over the ceiling, where the overflow is silent and drops from
the tail, which on this prompt is `muted color, tall grass, full body`.

One token had to come from somewhere, and `arms at sides` is where:

  * IT IS THE MOST REDUNDANT PHRASE IN THE PROMPT. The two-figure openpose
    skeleton states it explicitly -- the goblin's arms hang at his sides in
    the canvas, at controlnet scale 1.0 for the full denoise.
  * IT IS THE SAME CLASS OF CUT ROUND 4 ALREADY VALIDATED. Round 4 bought the
    guard back by shortening HIS clause on exactly this argument -- openpose
    carries stature, position and pose, so words need not -- and the guard
    came back correct. This applies the proven reasoning to the goblin.
  * DROPPING IT LANDS AT 74 OF 77 rather than 77 of 77. Taking the alternative
    single-token cut would sit exactly on the ceiling with no margin, and this
    lane has already been bitten once this session by a prompt whose tail was
    silently dropped. Three tokens of headroom is worth more than the phrase.

Positive 74 of 77, counted. NEGATIVE IS BYTE-IDENTICAL to round 4, as are the
skeleton and its sha, controlnet scale 1.0, the reference, the IP mask
87,485,412,763, ip-adapter-plus-face_sdxl_vit-h, ip-scale 1.25 and seed
20260899.

IF THIS IS 9 OF 9 the beat 07 motion spec gets filed off it immediately, on
the laws the passing three (04, 08, 13) ran on. Either way the four-round
attribute table and the plates go to the founder's per-beat page.
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
from derive_b07_twofig_r4_0821 import NEGATIVE, IP_SCALE      # noqa: E402

PARENT = "pipeline/jobs/ep2-b07-twofig-r4-0821.yaml"
PARENT_DIRTOK = "b07twofig-r4-0821"
NEW_ID = "ep2-b07-twofig-r5-0821"
NEW_DIRTOK = "b07twofig-r5-0821"

# 74 of 77, counted. Round 4's positive + `white eyes, eyebags`, - `arms at
# sides` (openpose states it; see the module docstring for why that one).
PROMPT = ("2boys, goblin, green skin, bald, pointy ears, white eyes, eyebags, "
          "mandarin collar, green shirt, black shorts, boots, standing at "
          "left, and one tall human city guard in full armor and a closed "
          "helmet at right, a full head taller, facing him, arm rising to "
          "point, muted color, tall grass, full body")

BAR = """JUDGED BY EYE AT 1:1, BOTH IDENTITIES, AGAINST ROUND 4 SIDE BY SIDE.
NINE BARS. Round 4 scored seven of them and this round must not trade any away.

  THE TWO THIS ROUND IS FOR
  E1  OFF-WHITE SCLERA. The eye white is off-white, not a green iris filling
      the eye. Read at 1:1 against taste/refs/goblin-canon-founder-0821.png.
  E2  EYEBAGS. Present under both eyes, as in round 3 and the founder's image.

  THE SEVEN ROUND 4 ALREADY WON -- a regression on ANY of these is a FAIL of
  this round even if E1 and E2 both land, because round 4 is then the better
  plate and this was a bad trade:
  E3  NARROW VERTICAL SLIT PUPILS. Round 4 got these from the adapter alone.
  A2  NO BOBBLEHEAD. Head no larger relative to body than round 4 at the same
      identical crop box. ip-scale is unchanged at 1.25 so this should hold,
      and it is still scored because it is the k2 risk.
  A3  NO CONTAINMENT BLEED beyond round 4's faint pre-existing ring ghosting.
  G1  EXACTLY TWO FIGURES, whole, one ground line, goblin left.
  G2  THE GUARD WEARS A CLOSED HELMET AND IS HUMAN. Round 4 won this back and
      it is the single most expensive thing in the prompt.
  G3  FIVE HEADS, A FULL HEAD TALLER, FULL PLATE.
  G4  ARMOURED GAUNTLET, no green hand.
  P1  MUTED SAGE PALETTE, no mask halo, dark boots.

NINE OF NINE IS A PASS AND THE MOTION SPEC GETS FILED OFF IT. Anything else is
recorded against the four-round table and beat 07 goes to the founder as it
stands. NOTE ONE KNOWN GAP THAT IS NOT ON THIS LIST: round 4's collar frog
closures degraded into plain round buttons. No token was spent on them, so
they are watched and reported, not scored -- adding a term for them would have
cost the guard, and the guard is worth more than the frogging."""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    assert_under_clip77("b07 r5 prompt", PROMPT)
    assert_under_clip77("b07 r5 negative", NEGATIVE)

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "canon-motion plate-fix lane, 2026-08-21",
            "consumer": (
                "THE PLATE BEAT 07'S MOTION SPEC GETS FILED OFF IF IT IS NINE "
                "OF NINE -- that is the standing agreement and the motion rung "
                "is written the moment a human confirms this plate. Beat 07 is "
                "the only one of the wave's four failed beats with no round-2 "
                "clip at all, because no plate has yet been good enough to "
                "animate. SECOND CONSUMER: the finding itself. Round 4 showed "
                "the adapter carries eye SHAPE and words carry eye COLOUR; if "
                "putting exactly those two words back closes the gap without "
                "costing the guard, that division of labour becomes a reusable "
                "rule for every two-character plate in this show."),
            "success": (
                "ONE 832x1216 png that is NINE OF NINE. THE TWO THIS ROUND IS "
                "FOR: E1 off-white sclera, not a green iris filling the eye; E2 "
                "eyebags present under both eyes. THE SEVEN ROUND 4 ALREADY "
                "WON, and a regression on any of them FAILS this round even if "
                "E1 and E2 land, because round 4 would then be the better "
                "plate: E3 narrow vertical slit pupils; A2 no bobblehead at an "
                "identical crop box; A3 no containment bleed beyond round 4's "
                "faint pre-existing ring ghosting; G1 exactly two whole figures "
                "on one ground line; G2 THE GUARD IN A CLOSED HELMET, human; G3 "
                "five heads, a full head taller, full plate; G4 armoured "
                "gauntlet, no green hand; P1 muted sage palette, no mask halo, "
                "dark boots. The named degenerate outcome is THE GUARD PAYING "
                "AGAIN: six tokens of goblin went back into a 77-token budget "
                "and one came out of the goblin's own pose clause, but if the "
                "guard loses his helmet or his species anyway, the budget is "
                "the cause and the answer is not a sixth wording round."),
            "why": (
                "ROUND 4 SPLIT THE FACE INTO WHAT THE ADAPTER HOLDS AND WHAT "
                "THE WORDS HELD, AND THIS PUTS BACK EXACTLY THE SECOND "
                "HALF.\n\nWith every goblin face word deleted and ip-scale at "
                "1.25, round 4 returned the species, the bald skull, the large "
                "pointed ears, the skin AND narrow vertical slit pupils -- the "
                "hardest feature in the canon, which six k-ladder wording rungs "
                "never reached. It did not return the off-white sclera, which "
                "came back as a green iris, or the eyebags. That is a clean "
                "decomposition and it names its own next rung: `white eyes, "
                "eyebags`, and nothing else.\n\nIP-SCALE STAYS AT 1.25. Round 4 "
                "was gated on k2's bobblehead and it DID NOT FIRE -- at an "
                "identical crop box the head is the same size relative to the "
                "body as at 1.0, if anything smaller, and the faint ring "
                "ghosting is equally present in round 3 at 1.0 so it is not a "
                "scale artefact. The scale is what is buying the slit pupil "
                "now that the words are gone, so walking it back would undo the "
                "thing that worked.\n\nONE TOKEN HAD TO MOVE AND IT IS "
                "DISCLOSED. `white eyes, eyebags` measures SIX tokens, not the "
                "four this lane estimated when it reported five free; 72 + 6 is "
                "78, one over. `arms at sides` is dropped to make room because "
                "the openpose skeleton states it outright -- the goblin's arms "
                "hang at his sides in the canvas at controlnet scale 1.0 -- and "
                "because that is the SAME argument round 4 used to shorten the "
                "guard's clause, which came back correct. Dropping it lands at "
                "74 of 77 instead of sitting exactly on the ceiling with no "
                "margin, and a silently dropped tail has already cost this lane "
                "a round today.\n\nEVERYTHING ELSE IS BYTE-IDENTICAL to round "
                "4: the negative, the skeleton and its sha, controlnet scale "
                "1.0, the reference, the mask, the adapter weight, ip-scale and "
                "the seed."),
        },
        overrides={
            "payload:prompt.txt": PROMPT,
            "key:priority": 15,
        },
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THE TWO WORDS ROUND 4 PROVED THE ADAPTER DOES NOT CARRY: "
                "`white eyes` and `eyebags`, added to the positive. HELD "
                "BYTE-FOR-BYTE: the entire negative, the two-figure skeleton %s "
                "at the same sha, xinsir/controlnet-openpose-sdxl-1.0 at scale "
                "1.0, jerry-canon-sq45-0821.png, the IP mask %s, "
                "ip-adapter-plus-face_sdxl_vit-h, --ip-scale %s, and seed "
                "20260899. ONE FURTHER CHANGE, DISCLOSED RATHER THAN BURIED: "
                "`arms at sides` is removed, because the two words cost SIX "
                "tokens and not the four estimated, and 72 + 6 = 78 is over the "
                "ceiling. It is the phrase openpose states most explicitly and "
                "it is the same cut round 4 made to the guard's clause and got "
                "away with. Result 74 of 77."
                % (CONTROL, IP_MASK, IP_SCALE)),
            "ip_scale_1_25_carried_from_round_4": (
                "IP-SCALE 1.25 IS SAFE ON THIS REFERENCE AND THIS MASK, and "
                "that is round 4's most transferable result. k2 "
                "(ep2-jerry-face-k2-0821) predicted that raising adapter "
                "strength against a reference that is 100% head would inflate "
                "the head, and named containment breaking as the outcome that "
                "stops the route. NEITHER FIRED. Measured the way the bar asked "
                "-- an IDENTICAL crop box across rounds 1, 3 and 4 so head size "
                "cannot be a framing artefact -- round 4's head at 1.25 is the "
                "same size relative to his body as rounds 1 and 3 at 1.0, if "
                "anything marginally smaller. The faint concentric ring "
                "ghosting around his head is equally present in round 3 at 1.0, "
                "so it is pre-existing rather than scale-induced. The dial has "
                "more room than the k-ladder's 0.7 -> 0.9 experience implied."),
            "failure_predicted_in_advance": (
                "THE GUARD PAYS AGAIN, and it is the whole risk of this round. "
                "Six tokens of goblin went back into a fixed budget. One came "
                "out of the goblin's own pose clause rather than the guard's, "
                "which is the entire reason `arms at sides` was chosen -- but "
                "the guard clause is long and it is the first thing a tokeniser "
                "squeeze has taken twice already (round 3 lost his helmet and "
                "his species that way). IF HE COMES BACK BARE-HEADED OR GREEN, "
                "the trade failed and round 4 is the better plate. SECOND: the "
                "adapter at 1.25 and `white eyes` may now DOUBLE UP on the eye "
                "and flatten it -- the negative still carries `blank eyes, no "
                "pupils`, and a sclera pushed too hard with the slit pupil lost "
                "would be an E1 win that fails E3, which is why E3 is on the "
                "scored list and not assumed."),
            "not_done_on_purpose": (
                "THE COLLAR FROGGING IS NOT BOUGHT. Round 4's frog closures "
                "degraded into plain round buttons, and a term for them would "
                "have cost the guard's clause, which is worth more. It is "
                "watched and reported rather than scored. THE SKELETON IS NOT "
                "TOUCHED, so G5 -- the arm reading more extended than the "
                "authored mid-raise -- remains open and remains not this "
                "round's question. AND NO MOTION SPEC IS FILED BY THIS JOB: it "
                "is filed AFTER a human confirms nine of nine, which is the "
                "rule that has kept the card off an off-canon character for "
                "four rounds."),
        },
        by="pipeline/derive_b07_twofig_r5_0821.py",
        retoken=[(PARENT_DIRTOK, NEW_DIRTOK)],
    )

    import yaml as _yaml
    blob = _yaml.safe_dump({k: v for k, v in child.items() if k != "derivation"})
    if PARENT_DIRTOK in blob:
        raise SystemExit("!! the parent's box scratch dir survives retokening")
    if NEW_DIRTOK not in blob:
        raise SystemExit("!! the child names no scratch dir of its own")

    out = "pipeline/jobs/%s.yaml" % NEW_ID
    print("%-24s prompt 74/77  negative HELD  ip-scale %s HELD  scratch %s"
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
