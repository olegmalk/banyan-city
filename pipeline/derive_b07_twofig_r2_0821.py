#!/usr/bin/env python3
r"""BEAT 07 TWO-FIGURE PLATE, ROUND 2: the eyes, and only the eyes.

    python3 pipeline/derive_b07_twofig_r2_0821.py            # dry run
    python3 pipeline/derive_b07_twofig_r2_0821.py --write

ROUND 1 LANDED rc=0 AND WAS JUDGED AT 1:1 AGAINST ITS OWN PRE-REGISTERED BAR.
Four of the six bars passed outright and one failed:

  G1 TWO FIGURES          PASS. Exactly two, both whole, one ground line.
  G2 THE FOUNDER'S GOBLIN FAIL, on ONE attribute. Green skin, bald, large
                          pointed ears and the mandarin collar with its frog
                          closure are all there. THE EYES ARE NOT: he came
                          back with large ROUND green eyes where canon has
                          off-white eyes with narrow vertical slit pupils, and
                          the round eye is most of why the face also reads
                          younger than the canon adult.
  G3 THE GUARD IS A MAN   PASS, and emphatically -- five heads, full plate,
                          helmeted, a head and a half over the goblin. That is
                          the founder's "dumb grown men" ruling in pixels.
  G4 NO ADAPTER LEAK      PASS. Nothing of the goblin's face is on the guard.
  G5 ARM MID-RAISE        MARGINAL. The arm is up and aimed, but reads closer
                          to fully extended than to mid-raise, and the hand
                          sits above his skull rather than at his face.
  G6 STAGING              PASS.

THE HYPOTHESIS THIS ROUND TESTS, AND THE ONE IT ALREADY KILLED
--------------------------------------------------------------------------
The first guess was the IP-Adapter mask -- that at the goblin's stature the box
had slipped onto his neck and diluted the face signal. THAT GUESS IS WRONG AND
IT WAS CHECKED BEFORE ANYTHING WAS FILED: the box 87,485,412,763 was drawn on
the round-1 output and it contains the whole skull, both ears and the entire
face, with only a little slack at the collar. The mask is not the lever, so it
does not move. Checking cost one composite and saved a round.

WHAT IS LEFT IS THE WORDING, and the round-1 prompt is where it went wrong. To
buy room for the guard clause, round 1 spent the goblin's eye description down
to the single term `slit pupils` -- where beat 07's ACCEPTED solo canon plate
carries `slit pupils, constricted pupils` AND, in a two-subject prompt, has no
second subject competing for the attribute. So the eye clause is restored and
reinforced, and the observed defect is banned by name.

THE ONE VARIABLE IS THE EYE CLAUSE. Positive gains `white eyes` and
`constricted pupils`; the negative gains `round pupils` and `big round eyes`.
Room is bought by dropping `muted color`, `best quality` and `boots` from the
positive and `watermark`, `wrinkled skin` and `eyepatch` from the negative --
none of which describes an eye, and all of which round 1 demonstrably did not
need: the palette, the quality and the boots all came back correct without
them being load-bearing, and none of the three dropped negatives fired.

EVERYTHING ELSE IS HELD: the same two-figure skeleton at the same sha, the
same controlnet at scale 1.0, the same square reference, the same ip-mask, the
same ip-scale, the same weight, the same seed 20260899. G5 is deliberately NOT
addressed -- it is a skeleton change, it is marginal rather than failing, and
two variables in one round is how a lane stops knowing which one worked.
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

PARENT = "pipeline/jobs/ep2-b07-twofig-0821.yaml"
NEW_ID = "ep2-b07-twofig-r2-0821"

# 75 of 77, measured. `white eyes` + `constricted pupils` are the change.
PROMPT = ("2boys, goblin, green skin, bald, pointy ears, white eyes, slit "
          "pupils, constricted pupils, eyebags, thin eyebrows, mandarin "
          "collar, green shirt, black shorts, standing at left, arms at "
          "sides, and one tall armored city guard in a helmet at right, "
          "facing him, arm rising to point, tall grass, full body")

# 73 of 77. `round pupils` and `big round eyes` ban the observed defect by name.
NEGATIVE = ("lowres, worst quality, low quality, text, blank eyes, no pupils, "
            "round pupils, big round eyes, thick eyebrows, cloak, hood, "
            "patchwork, human face on the goblin, old man, hair, beard, "
            "child, chibi, 3boys, crowd, multiple heads, disembodied head, "
            "glowing eyes, orange eyes, third eye")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    assert_under_clip77("b07 r2 prompt", PROMPT)
    assert_under_clip77("b07 r2 negative", NEGATIVE)

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "canon-motion plate-fix lane, 2026-08-21",
            "consumer": (
                "STILL THE INIT FOR BEAT 07'S MOTION SPEC, which is the one "
                "job in the plate-fix wave that has not been filed -- beats "
                "02, 03 and 20 went to motion round 2 the moment their plates "
                "passed, and beat 07 did not, because animating a goblin whose "
                "eyes are not the founder's would spend the card on the wrong "
                "character. This plate is what unblocks it. Nothing in "
                "review/ep2-ship-0821 reads this file."),
            "success": (
                "ONE 832x1216 png that clears round 1's bar WITH G2, and the "
                "eyes are the whole question. E1 the goblin's eyes are "
                "off-white with NARROW VERTICAL SLIT PUPILS, read at 1:1 "
                "against taste/refs/goblin-canon-founder-0821.png -- not "
                "round, not a green iris, not blank; E2 with the eye fixed the "
                "face reads as the canon ADULT rather than a child. HELD FROM "
                "ROUND 1, and a regression on any of them fails this plate "
                "even if the eye is perfect: exactly two figures; the guard "
                "five heads, armoured, helmeted, a head and a half taller; no "
                "adapter leak onto the guard; the mandarin collar and frog "
                "closure still on the goblin; both full body in tall grass. "
                "The named degenerate outcome is THE BANNED-ATTRIBUTE SWAP: "
                "`blank eyes, no pupils` and `round pupils` are both in the "
                "negative now, and a model squeezed between them can return a "
                "featureless eye. That is a FAIL, not a win on E1."),
            "why": (
                "BEAT 07'S ROUND-1 TWO-FIGURE PLATE FIXED THE STAGING AND MISSED "
                "THE EYES, AND THE EYE IS THE FOUNDER'S IMAGE.\n\nRound 1 was "
                "filed to answer whether a two-figure plate could exist at all, "
                "because the beat's motion take proved a guard summoned by "
                "wording alone re-stages the shot and loses the goblin. It can: "
                "two figures, one ground line, the guard a genuine grown man at "
                "five heads per the founder's 2026-08-20 ruling, and no "
                "IP-Adapter leak onto him. What came back wrong is one "
                "attribute of one character -- large round green eyes where "
                "canon has off-white eyes with narrow vertical slit "
                "pupils.\n\nTHE FIRST EXPLANATION WAS TESTED AND DISCARDED "
                "BEFORE THIS WAS FILED. The suspicion was the IP mask: at the "
                "goblin's stature in a two-figure frame the head box might have "
                "slipped onto his neck. Drawing 87,485,412,763 on the round-1 "
                "output settles it -- the box holds the whole skull, both ears "
                "and the entire face. So the mask is correct and is held "
                "unchanged, and the lever is the wording that round 1 cut to "
                "make room for the guard: the accepted SOLO canon plate for "
                "this beat says `slit pupils, constricted pupils`, and round 1 "
                "said only `slit pupils` -- in a prompt that now has a second "
                "subject competing for every attribute.\n\nWHAT THIS JOB DOES: "
                "round 1 with the eye clause restored and the observed defect "
                "banned by name. Same skeleton, same controlnet, same "
                "reference, same mask, same ip-scale, same seed."),
        },
        overrides={
            "payload:prompt.txt": PROMPT,
            "payload:negative.txt": NEGATIVE,
            "key:priority": 15,
        },
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THE EYE CLAUSE, on both sides of the prompt. POSITIVE gains "
                "`white eyes` and `constricted pupils`; NEGATIVE gains `round "
                "pupils` and `big round eyes`. Room is bought by dropping "
                "`muted color`, `best quality` and `boots` from the positive "
                "and `watermark`, `wrinkled skin` and `eyepatch` from the "
                "negative -- none of them describes an eye, and round 1 shows "
                "none was load-bearing: the palette, the render quality and the "
                "boots all came back correct, and not one of the three dropped "
                "negatives fired. HELD, UNCHANGED AND ON PURPOSE: the "
                "two-figure skeleton %s at the same sha, "
                "xinsir/controlnet-openpose-sdxl-1.0 at scale 1.0, the square "
                "reference jerry-canon-sq45-0821.png, the IP mask %s, ip-scale "
                "1.0, ip-adapter-plus-face_sdxl_vit-h, and seed 20260899."
                % (CONTROL, IP_MASK)),
            "hypothesis_tested_and_discarded_before_filing": (
                "THE IP MASK, and it cost one composite instead of a round of "
                "GPU. The first explanation for a drifting face on a "
                "two-figure plate is a mask that no longer sits on the head -- "
                "the box was derived at the goblin's stature 0.53 and the canon "
                "head_box() assumes 0.90, so a slip was plausible enough to "
                "act on. It was DRAWN ON THE ROUND-1 OUTPUT instead: "
                "87,485,412,763 contains the whole skull, both ears and the "
                "entire face, with a little slack at the collar and nothing "
                "missing at the crown. The mask is therefore held. This is "
                "recorded because a wrong hypothesis that was checked is worth "
                "more to the next lane than a right one that was guessed."),
            "not_done_on_purpose": (
                "G5 IS NOT ADDRESSED. Round 1's arm reads closer to fully "
                "extended than to the authored mid-raise, and the hand sits "
                "above the goblin's skull rather than at his face. That is a "
                "SKELETON change -- ARM_ELB / ARM_WRI in "
                "pipeline/author_b07_twofig_skel_0821.py -- and it would be a "
                "second variable in a round whose whole question is the eye. "
                "It is also marginal rather than failing: an over-extended "
                "point still gives the motion model somewhere to travel from, "
                "where a MISSING guard gave it nothing. If the eye lands and "
                "G5 still bothers the founder, it is one skeleton edit and a "
                "third round. ALSO NOT DONE: no motion is rendered or filed "
                "by this job."),
            "failure_predicted_in_advance": (
                "THE BANNED-ATTRIBUTE SWAP, and it is why E1 is written as "
                "three exclusions rather than one inclusion. The negative now "
                "carries `blank eyes, no pupils` AND `round pupils, big round "
                "eyes`; a model that cannot satisfy both may return a "
                "featureless or a solid-dark eye, which would score as 'not "
                "round' while being just as far from canon. SECOND: the eye "
                "terms are worth 5 tokens and they were paid for out of the "
                "guard's half of a 77-token budget -- if the guard degrades "
                "(loses the helmet, drops below five heads) the budget is the "
                "cause and the answer is a longer-context checkpoint, not a "
                "sixth wording."),
        },
        by="pipeline/derive_b07_twofig_r2_0821.py",
    )

    out = "pipeline/jobs/%s.yaml" % NEW_ID
    print("%-24s prompt 75/77  negative 73/77  (mask HELD %s)"
          % (NEW_ID, IP_MASK))
    if not a.write:
        print("\n-- dry run. re-run with --write.")
        return 0
    path = derive_spec.write(child, out, force=a.force)
    derive_fetch_guard.assert_fetch_urls_resolve(path, must_hold=(CONTROL,))
    print("   wrote %s  (fetch urls resolve)" % os.path.relpath(path, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
