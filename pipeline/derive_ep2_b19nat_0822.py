#!/usr/bin/env python3
r"""Derive the 0.30 NATURALIZE job for BEAT 19's fig, drawn into the CURRENT plate.

    python3 pipeline/derive_ep2_b19nat_0822.py            # dry run
    python3 pipeline/derive_ep2_b19nat_0822.py --write

THE RUNG THIS CLOSES, NAMED LAST NIGHT AND NAMED AGAIN THIS MORNING
--------------------------------------------------------------------
`ep2-b19-dropmotion-0822` did the thing this beat had been waiting for since
08-15: **the fig came off the stem and landed in the grass.** Two of the beat's
three events, in order, off a plate where the plant and the fruit had been DRAWN
in and settled at 0.22. That result is what makes the whole composite route
credible -- i2v will animate a hand-drawn object.

Its own verdict named the next version in one sentence and it was not fired:
*"the plate betrays its age -- sapgloss is from 08-19 and predates the goblin
correction, so the face in it was never his, and it is replaced within 25 frames
anyway, first block interframe 8.92 against a 0.08 to 0.83 middle."* So: **the
fig into a CURRENT plate, drawn on the corrected face, and then that same motion
asked of it.** This job is the plate half.

WHY IT DID NOT HAPPEN UNTIL NOW, and it was a tool shape rather than a decision.
`beat19_sapling_composite.py` can draw a fig but has b19's OLD plate typed into
it -- hard-coded leaf tips, a ground-plane px/cm model, two whips to erase, beat
18's fruit to hang -- so aiming it at the w4 plate is an edit to its source and
not a flag. `beat16_sapling_composite.py` is the parametric one (root, height,
tilt, leaf fraction on the command line) and it had no fruit. It has an optional
`--fig` now, OFF by default, and the five plates that tool has already produced
are byte-identical without it -- asserted by re-running beat 12's own command
line and comparing the sha.

THE COLOUR RULE IS STATED, NOT SMUGGLED, exactly as beat 06's board states it:
the fig's HUE is canon's (beat 18's ratified fruit measures in the violet family;
beat 19's own old plate measured 266-274 deg) because a washed-out green field
contains no violet to sample, and only its VALUE is fitted to the plate. The fit
is capped so it may darken canon's violet toward the frame and may NOT brighten
it past itself -- the uncapped first run returned a hot pink (255,143,255), which
is neither canon's colour nor anything in the picture.

TWO NEGATIVE TERMS ARE STRUCK FROM THE SIBLING DERIVER AND BOTH WOULD HAVE BEEN
FATAL. `fruit`, because the fruit is the object this beat is ABOUT -- the 08-21
tranche struck it for beat 20 on exactly this ground. And `1boy, goblin, person`,
because this plate IS the goblin and the mask sits in the grass beside him.

$0 to derive. ~4 GPU minutes.
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
import derive_ep2_sapnat2_0822 as S                           # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77     # noqa: E402

BEAT = 19
# ROUND 2 IS ONE NUMBER AND IT WAS THE THIRD PRE-REGISTERED FAILURE MODE.
# r1 at 0.30 passed P2 through P6 -- nothing moved, one fig, one plant, two
# leaves, matte, the goblin untouched -- and FAILED P1: the plant and the fruit
# came back as flat as they were drawn. That is what the spec said would mean
# "the boundary is about EDGE HARDNESS rather than about being man-made, which
# is a better-shaped rule than the one beat 06 produced", and it is. Beat 06's
# board wanted 0.45 for the same reason and got it. So: 0.45, one number, and
# what it measures is whether the strength boundary follows the OBJECT (made vs
# organic) or the PLATE (a hard-inked cel frame vs this soft high-key one).
STRENGTH = "0.45"
ROUND = "r2"
SUFFIX = "" if ROUND == "r1" else "-" + ROUND
NEW_ID = "ep2-b19-fignat%s-0822" % SUFFIX
DIRTOK = "b19fignat%s-0822" % SUFFIX
OUTTOK = "b19-fignat%s" % SUFFIX
PUBDIR = NEW_ID

SRC_DIR = "farm-out/ep2-b19-figcomp-0822"
INIT = "b19-figcomp-in-0822.png"
MASK = "b19-figcomp-in-mask-0822.png"

FETCH = (S.P.FETCH
         .replace(r"C:\banyan-farm\b{beat:02d}sapnat-0821",
                  r"C:\banyan-farm\%s" % DIRTOK)
         .replace("farm-out/ep2-b{beat:02d}-sapnat-0821/", "%s/" % SRC_DIR)
         .replace("banyan-city-b{beat:02d}-sapnat/1.0",
                  "banyan-city-b19-fignat/1.0")
         .replace("beat {beat:02d}", "beat 19"))

PROMPT = (
    "a young sapling with exactly two wide oval leaves with soft round tips on "
    "one thin bare stem, rooted in the grass, with ONE small deep violet fig "
    "hanging on the stem, with one small green goblin standing in the tall "
    "grass behind it, solo, sunny grassy field, detailed cinematic anime, "
    "masterpiece, best quality, very aesthetic")

# `fruit` is STRUCK from the base -- it is the object this beat is about, and
# the 08-21 tranche struck it for beat 20 on exactly that ground. The figure
# bans are struck too: this plate IS the goblin.
NEGATIVE = (S.P.NEGATIVE_BASE
            .replace("bud, flower, fruit, large tree", "bud, flower, large tree")
            # TRIMMED TO FIT, and the four terms kept are the four failure
            # modes this beat has actually produced rather than a wish list:
            # a count above one, a glossy fruit, a faceted gem, and a bead on
            # a thread. `many fruits` covers `two fruits` and `bunch of
            # berries`; `glossy` covers `specular highlight`.
            + ", many fruits, glossy fruit, faceted gem, bead on a thread")

BAR = """JUDGED BY EYE AT 1:1. THE FRUIT IS THE QUESTION.

  P1  THE FIG AND THE PLANT ARE DRAWN, NOT PASTED. Cel shading and the plate's
      own ink weight; the compositor's flat fill and hard cut edge are gone.
  P2  NOTHING HAS MOVED. Stem root, leaf tips and the FIG'S CENTRE sit where
      the compositor put them, within a few px. If the fig has relocated onto
      the goblin, onto the ground, or into the air, this plate is a FAIL --
      the whole point of drawing it is that the motion rung can then say "it
      hangs on the stem" as a description rather than a summons.
  P3  EXACTLY ONE FIG AND EXACTLY TWO LEAVES. Beat 19's wording ladder closed
      on fruit counts of 4, ~8 and 3, never 1, and canon says two leaves. Any
      other count is a FAIL however well drawn.
  P4  IT IS A FIG AND NOT A GEM. The old plate's "fruits" were VIOLET FACETED
      CRYSTALS on threads -- diamond-cut, hard specular. Canon wants MATTE.
      A glossy highlight is a FAIL and it is in the negative.
  P5  THE GOBLIN SURVIVES UNCHANGED. Face, ears, skin, wardrobe, pose. The
      mask is in the grass beside him and must not have reached him. This is
      the clause the whole re-plate exists for: the point of moving off the
      08-19 sapgloss plate is that its face was never the founder's.
  P6  THE PLANT SITS IN THE GRASS, with contact at the root and no halo.

A FAIL on P2 or P5 kills the plate. A FAIL on P1 alone is a strength question
-- and note that beat 06 measured this morning that a hard-edged MADE object
wants 0.45 where a leaf wants 0.30; a fig is organic, so 0.30 is the right
first ask and a flat fig would be the interesting result."""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    init_abs = os.path.join(REPO, SRC_DIR, INIT)
    mask_abs = os.path.join(REPO, SRC_DIR, MASK)
    for f in (init_abs, mask_abs):
        if not os.path.isfile(f):
            raise SystemExit("!! missing composite input %s" % f)
    init_sha, mask_sha = S.sha256_of(init_abs), S.sha256_of(mask_abs)
    assert_under_clip77("b19 prompt", PROMPT)
    assert_under_clip77("b19 negative", NEGATIVE)

    retoken = [
        (S.PARENT_ID, NEW_ID),
        ("ep2-" + S.PARENT_PUBDIR.split("ep2-")[1], PUBDIR),
        (S.PARENT_MASK, MASK),
        (S.PARENT_INIT, INIT),
        (S.PARENT_DIRTOK, DIRTOK),
        (S.PARENT_OUTTOK, OUTTOK),
    ]
    child = derive_spec.derive(
        S.PARENT, NEW_ID,
        fresh={
            "owner": "morning compositor lane, 2026-08-22",
            "consumer": (
                "THE INIT FOR BEAT 19's NEXT DROP RENDER. The clip staged on "
                "/review/ep2-beats-0821 for this beat already makes the fruit "
                "fall, and its named fault is that its plate predates the "
                "goblin correction so the face in it was never the founder's. "
                "This is the same object on a plate that has his face. Named "
                "consumer: a re-derive of ep2-b19-dropmotion-0822 with this "
                "init, filed only after a human opens this png."),
            "success": (
                "ONE 832x1216 png in which ONE deep violet MATTE fig hangs on "
                "the stem of a two-leaf sapling in the grass, drawn rather "
                "than pasted, in the position the compositor put it, with the "
                "goblin behind it untouched. The named degenerate outcomes are "
                "a fig that has RELOCATED (which would make the motion "
                "prompt's 'it hangs on the stem' a summons again) and a fig "
                "that comes back as a faceted gem, which is what this beat's "
                "old plate actually contained."),
            "why": (
                "THE RUNG BEAT 19's OWN VERDICT NAMED AND NOBODY FIRED.\n\n"
                "ep2-b19-dropmotion-0822 made the fruit fall -- two of the "
                "beat's three events, in order, off a plate where the plant "
                "and the fig had been drawn in by hand. That result is the "
                "evidence under the whole composite route. Its verdict also "
                "named its own successor in one sentence: the plate is from "
                "08-19, it predates the goblin correction, the face in it was "
                "never the founder's, and it is replaced within 25 frames "
                "anyway (first block interframe 8.92 against a 0.08-0.83 "
                "middle).\n\n"
                "So the fig goes into a CURRENT plate -- ep2-b19-canon-w4-0821, "
                "the same plate this beat's other clip used -- and the same "
                "motion is asked of it afterwards.\n\n"
                "WHY IT WAITED, and it was a tool shape rather than a "
                "decision: beat19_sapling_composite.py can draw a fig but has "
                "b19's old plate typed into it, and the parametric compositor "
                "had no fruit. It has an optional --fig now, off by default, "
                "and beat 12's plate re-renders byte-identical without it."),
        },
        overrides={
            "seed": S.SEED,
            "argv:--init-sha256": init_sha,
            "argv:--strength": STRENGTH,
            "argv:--note": (
                "ATTACHED TO BOTH THE DRY STEP AND THE RENDER STEP. ON THE DRY "
                "STEP it is a MASK GEOMETRY CHECK before any model loads: the "
                "mask must be ONE blob shaped like a small plant with a bead "
                "on its stem, standing in the grass to the LEFT of the goblin, "
                "and IT MUST NOT TOUCH HIM. If it reaches his leg, his tunic "
                "or his face, the pass has a licence to redraw the character "
                "this whole re-plate exists to preserve, and P5 fails by "
                "construction. ON THE RENDER STEP: one pass, one seed, 12 of "
                "40 steps from a latent that still holds the drawn fig."),
            "payload:prompt.txt": PROMPT,
            "payload:negative.txt": NEGATIVE,
            "payload:fetch_init.py": FETCH.format(
                beat=BEAT, init=INIT, mask=MASK,
                init_sha=init_sha, mask_sha=mask_sha),
            "key:beat": BEAT,
            "key:priority": 15,
            "key:script_line": (
                "Beat 19 THE DROP: the fig comes off the stem, lands in the "
                "grass, and he notices. Three events in order -- and the "
                "object that performs all three has to be in the plate before "
                "any of them can be asked for."),
        },
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THE INIT, and within it the FIG. Every sampler number is the "
                "b16 rung's by copy through derive_ep2_sapnat_0821: 40 steps, "
                "cfg 7.5, strength 0.30, pad-crop 64, blur 8, seed 20260820, "
                "the whole inpaint_fruit.py payload, the env block, the needs, "
                "the dry-run gate and the no-glob publish. The prompt names "
                "the fig because the init contains one. TWO NEGATIVE TERMS ARE "
                "STRUCK from the sibling deriver and both would have been "
                "fatal: `fruit`, because the fruit is what this beat is about "
                "(the 08-21 tranche struck it for beat 20 on the same ground), "
                "and the figure bans, because this plate IS the goblin."),
            "init_provenance": (
                "%s/%s, 832x1216, sha256 %s, with its mask %s sha256 %s, both "
                "on origin/main and sha-asserted by the fetch. The plate under "
                "the composite is farm-out/ep2-b19-canon-w4-0821/"
                "ep2-b19-canon-w4-0821-ipahead.png -- the CURRENT plate, drawn "
                "on the corrected face. The plant and the fig were cut by "
                "pipeline/beat16_sapling_composite.py with --fig; its geometry "
                "json is beside the png and records the fig's centre, its "
                "radii, and that its hue is canon's while its value is the "
                "plate's own local p22." % (SRC_DIR, INIT, init_sha, MASK,
                                            mask_sha)),
            "failure_predicted_in_advance": (
                "THREE. THE FIG BECOMES A GEM, which is not a hypothetical -- "
                "this beat's 08-19 mac plate contained VIOLET FACETED CRYSTALS "
                "on threads, hard specular, and the model clearly has that "
                "reading available for a small violet ovoid on a stem. Banned "
                "in the negative and scored as P4. THE MASK REACHES HIM: it "
                "sits in the grass beside his left leg and the pad-crop is 64 "
                "px, so P5 is the clause most at risk and it is a killing one. "
                "AND THE FIG STAYS FLAT: beat 06 measured this morning that a "
                "hard-edged MADE object needs 0.45 where a leaf needs 0.30. A "
                "fig is organic and 0.30 is the right first ask, so a flat fig "
                "here would say the boundary is about EDGE HARDNESS rather "
                "than about being man-made, which is a better-shaped rule than "
                "the one beat 06 produced."),
            "not_done_on_purpose": (
                "NO MOTION IS FILED WITH THIS. The re-derive of "
                "ep2-b19-dropmotion-0822 onto this init is a two-string change "
                "and could be filed in the same breath, and that is exactly "
                "the thing the one-sample rule forbids: the motion prompt's "
                "licence is that the init CONTAINS the fig, and nobody has "
                "looked at whether it still does after the pass."),
        },
        by="pipeline/derive_ep2_b19nat_0822.py",
        retoken=retoken,
    )
    out = "pipeline/jobs/%s.yaml" % NEW_ID
    print("%-24s beat %-3d init %s..  prompt %d chars"
          % (NEW_ID, BEAT, init_sha[:12], len(PROMPT)))
    if not a.write:
        print("\n-- dry run. re-run with --write.")
        return 0
    path = derive_spec.write(child, out, force=a.force)
    derive_fetch_guard.assert_fetch_urls_resolve(path, must_hold=(INIT, MASK))
    print("wrote %s  (fetch urls resolve)" % os.path.relpath(path, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
