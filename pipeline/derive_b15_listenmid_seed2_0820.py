#!/usr/bin/env python3
"""THE CONFIRMATION SEED on beat 15's first passing recipe. ONE VARIABLE: the seed.

Rung 5 (`ep2-b15-listenmid-0820`) is the first clip this beat has produced that
this lane can score green on everything it can measure, and every one of the five
rungs before it ran at seed 20260820. Five rungs at one seed is exactly what made
them true controls of each other -- and it is also exactly why nobody yet knows
whether rung 5's result belongs to the RECIPE or to that one draw.

WHAT RUNG 5 BOUGHT, measured against every earlier rung on the same instruments.
Whole-frame mean-absolute interframe luma, ALL pairs f009..f084 -- the stretch
that was dead in every previous clip -- and the mouth band (300,420,420,500) over
the same stretch:

    rung 1  listenmotion   0.396   mouth 1.915   (and it lost the plant to a hand)
    rung 2  listenlast     0.079   mouth 0.200   ("the loosest of all six")
    rung 4  grassroot      0.166   mouth 0.213   (open mouth, HELD)
    rung 5  mid            0.623   mouth 1.759

plus judge_clip FREEZE **none** (rung 4: 5 frames from f116), HOLD strength 0.559
(rung 4: 0.638, bar 0.638), and **period 2 / 60 distinct pictures / 12.0 effective
fps** where all six earlier clips in this family read period 3 / 40 / 8.0. It is
the first clip on this beat with twice the temporal resolution of its siblings,
and by eye he now tips his head down toward the leaves and stays put, where rung
4 slid 184 px right in its last quarter.

WHY A SEED AND NOT ANOTHER EDIT. There is no wording rung left that this lane can
justify: the plant clause is closed (rung 4), the placement axis has had its
terminal (rung 2) and its middle (rung 5), and the remaining gap -- that the plate
puts his face ~160 px from the leaves where the script says "a hand's width" -- is
a PLATE property and belongs to the plate lane. What is genuinely unknown, and
cheap, is whether this recipe reproduces. This box has already demonstrated that
the SAME seed reproduces bit for bit across eight hours; nobody has asked what a
DIFFERENT one does to this recipe. The precedent is in the ladder: beat 14's
crf-10 rung was believed until its second seed COST MOVEMENT, and that second seed
is why the crf finding is stated per-beat instead of as a blanket rule.

AND THE CONSUMER IS NAMED. Beat 15's cut slot. Rung 5 is the clip that would be
put in front of the founder; a recipe that only works at one draw is not a recipe,
and finding that out costs 4.5 minutes and $0 -- whereas finding it out after a
screening costs the screening.

$0. Writes ONE spec file and nothing else.
Run:  python3 pipeline/derive_b15_listenmid_seed2_0820.py [--force]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b15-listenmid-0820.yaml"
NEW_ID = "ep2-b15-listenmid-s2-0820"
OLD_BASE = "15-good-listener-LTX-mid-0820"
NEW_BASE = "15-good-listener-LTX-mid-s20260821-0820"
OLD_BENCH = "bench-b15-listenmid"
NEW_BENCH = "bench-b15-listenmid-s2"
SEED = 20260821

VARIABLE = (
    "THE SEED, 20260820 -> 20260821, AND NOTHING ELSE IN THE FILE. The prompt is "
    "rung 5's byte for byte -- including the inserted middle sentence -- and so "
    "are the negative, the init, its sha, the crop size, the anchor, 121 frames, "
    "guidance 2.0, distilled sigmas, two-stage, sequential offload and "
    "--image-crf 10. 20260821 is the next integer after the seed this whole "
    "family has run on, chosen for that reason and no other: a neighbouring "
    "integer has no more claim on a good draw than a distant one, and picking a "
    "seed with a story attached is how a confirmation becomes a selection.")

BAR = {
    "S1_THE_MIDDLE_IS_STILL_ALIVE": (
        "THE CLAUSE THIS JOB EXISTS FOR. Whole-frame mean-absolute interframe "
        "luma over ALL pairs f009..f084 must land at or above 0.30, and the mouth "
        "band (300,420,420,500) over the same stretch at or above 0.80. THE "
        "NUMBERS ARE CALIBRATED AGAINST THIS BEAT'S OWN HISTORY AND NOT INVENTED: "
        "rung 2, the clip the ladder called the loosest of six, reads 0.079 / "
        "0.200; rung 4 reads 0.166 / 0.213; rung 5 reads 0.623 / 1.759. The floor "
        "is set at roughly HALF of rung 5 and four times rung 2, so a seed that "
        "merely halves the effect still passes and a seed that lands back in the "
        "old regime cannot. (Rung 5's own bar asked for 1.5 on a step-frame "
        "measure; that threshold was invented without calibration, is above "
        "anything this engine has produced on this beat at any seed, and is "
        "retracted rather than carried.)"),
    "S2_THE_PLANT_AND_THE_SUBJECT_BOTH_HOLD": (
        "GATE. The goblin present and recognisable in all 121 frames, checked on a "
        "full-clip sheet; the plant ONE thin stem and TWO leaves, rooted, with no "
        "hand on it, at f000 f030 f060 f090 f120. If either fails nothing else is "
        "scored. Rung 3 lost the subject to one noun and rung 2 lost the plant to "
        "one phrase, at THIS seed; whether that was the words or the draw is part "
        "of what this job answers."),
    "S3_NO_TERMINAL_FREEZE_AND_NO_STILLNESS_TAX": (
        "judge_clip FREEZE none, and HOLD strength at or below 0.638 (rung 4's "
        "number; rung 5 read 0.559). REPORT THE PERIOD WHATEVER IT IS: rung 5 is "
        "the only clip in this family that reads period 2 / 60 distinct / 12.0 "
        "effective fps against everyone else's period 3 / 40 / 8.0, and whether "
        "that doubling is the recipe or the draw is the single most interesting "
        "thing this job can report. Period 1 still voids the hold statistics -- it "
        "means a cut."),
    "S4_HE_DOES_NOT_RELOCATE": (
        "His eye band within 60 px of where it started at f105 and f120, with a "
        "background template published at the same frames so a camera move cannot "
        "be scored as a slide. Rung 4 slid dx +184 dy -30 against a background "
        "holding at dx 0..+3; rung 5 does not slide by eye. USE A TEMPLATE FROM "
        "f010 AND REPORT ITS RESIDUAL: on rung 5 the f010 eye-band template hit "
        "the search boundary at mad 35 on every later frame, which means the head "
        "had TIPPED rather than travelled and the tracker had nothing to lock -- a "
        "boundary hit at a high residual is a FAILED MEASUREMENT and must be "
        "reported as one, not as a 60 px slide."),
    "S5_the_beat_still_reads": (
        "He is sitting in the grass with his knees up and both hands on his knees "
        "at f120; his head tips down and over toward the two leaves rather than "
        "away; his mouth is open at f030, f060 and f090. Read at 4x."),
}

FAIL_MODES = [
    "F-SEED-CARRIED-THE-RESULT -- S1 fails and the middle is dead again. NAMED AS "
    "THE OUTCOME THAT MATTERS MOST, because it is the one that changes what "
    "happens next: rung 5 would then be a lucky draw rather than a recipe, it must "
    "not be offered as a cut candidate on its own, and the honest next step is a "
    "third seed to see which of the two is the outlier. Beat 14's crf-10 rung is "
    "the precedent -- believed until its second seed cost movement.",
    "F-PLANT-PICKED-UP / F-SUBJECT-DELETED at a new seed -- S2's gate. This would "
    "be the most valuable failure in the set: it would mean the noun law's fixes "
    "were seed-specific, and every conclusion beat 15 has drawn from five rungs at "
    "one seed would need re-reading.",
    "F-PERIOD-REVERTS -- the clip comes back at period 3 / 8.0 effective fps with "
    "the middle still alive. That would separate two things this lane currently "
    "cannot: whether the inserted sentence bought MOTION or bought TEMPORAL "
    "RESOLUTION. Not a failure of the beat; a sharpening of the finding.",
    "F-IDENTITY-DRIFT -- a different draw is the classic place for it. Publish "
    "luma_std with every probe reading; a collapse is a box on a field and an "
    "inflation is a box on an edge, and rung 4's probe collapsed 14.3 -> 2.4 "
    "purely because the subject walked out from under it.",
    "F-MIDDLE-IS-A-CUT at a new seed -- answered NO on beats 03 and 13 and on rung "
    "5, so this is carried for completeness. The negative's `cut to another shot` "
    "is by this ladder's own law not protection.",
]

NOT_DONE = (
    "NO WORDING CHANGE OF ANY KIND. NO recipe change -- size, frames, fps, "
    "guidance, distilled sigmas, two-stage, offload, mode and --image-crf 10 are "
    "the b14 crf-10 parent's, six rungs deep. NO new init, NO new sha, NO new "
    "anchor, NO new mask. NO SHORTER RENDER: --frames is an input to the "
    "denoiser's temporal grid and not a crop. NO THIRD SEED FILED ALONGSIDE THIS "
    "ONE -- a sweep answers a question one sample has not yet asked, and if this "
    "seed agrees with rung 5 the question is closed at two. NO plate work: that "
    "the plate puts his face ~160 px from the leaves where the script says a "
    "hand's width is real, open, and the plate lane's. No pick, no plate_ack, no "
    "cut, no publication -- beat 15 stays a SLATE and rung 5 is not offered as a "
    "candidate until this job reports.")


def main():
    force = "--force" in sys.argv
    parent = derive_spec.load(os.path.join(REPO, PARENT))
    pkey = [k for k in parent["payload"] if k.endswith("b15-motion-prompt.txt")][0]
    prompt = parent["payload"][pkey]

    child = derive_spec.derive(
        src=PARENT, new_id=NEW_ID,
        by="pipeline/derive_b15_listenmid_seed2_0820.py",
        fresh=dict(
            owner="the composite-plate motion lane, 2026-08-20, the confirmation seed",
            consumer=(
                "The episode 2 cut, beat 15, still a SLATE. Rung 5 is the first "
                "clip this beat has produced that scores green on everything this "
                "lane can measure, and it is the clip that would go in front of "
                "the founder. This asks the one question that has to be answered "
                "before it does: is that the recipe or the draw. Downstream: the "
                "beat's entry in review/ep2-picks/ and a founder screening. The "
                "cut swap is a taste call and is not proposed here."),
            success=(
                "ONE 704x1280 121-frame mp4 off the SAME PROMPT, the same init and "
                "the same sha as ep2-b15-listenmid-0820, at a DIFFERENT SEED, whose "
                "middle is still alive, whose subject and plant both hold, and "
                "which therefore establishes rung 5's result as a property of the "
                "recipe rather than of one draw. %s" % VARIABLE),
            why=(
                "$0, ~4.5 minutes, and the card is empty. Five rungs at one seed "
                "made them true controls of each other and left exactly one thing "
                "unmeasured: reproducibility across draws. This box has shown the "
                "SAME seed reproduces bit for bit across eight hours; nobody has "
                "asked what a different one does. Beat 14's crf-10 rung is the "
                "precedent for asking -- it was believed until its second seed cost "
                "movement, and that is why the crf finding is stated per-beat "
                "rather than as a blanket rule. Cheaper now than after a "
                "screening."),
        ),
        overrides={"seed": SEED},
        retoken=[(os.path.basename(PARENT)[:-5], NEW_ID),
                 (OLD_BASE, NEW_BASE), (OLD_BENCH, NEW_BENCH)],
        extra={
            "skin_probe": dict(parent["skin_probe"]),
            "rung_5_the_control": (
                "ep2-b15-listenmid-0820 at seed 20260820. f009..f084 all-pairs "
                "whole-frame interframe 0.623 and mouth band 1.759, against rung "
                "2's 0.079 / 0.200 and rung 4's 0.166 / 0.213; judge_clip FREEZE "
                "none, HOLD period 2 strength 0.559, 60 distinct pictures, 12.0 "
                "effective fps -- twice the temporal resolution of every other "
                "clip in this family. Goblin present throughout, plant rooted, "
                "camera locked (background rock dx 0 dy 0, mad 3.7-4.0), and no "
                "relocation by eye where rung 4 slid 184 px."),
            "the_one_variable": VARIABLE,
            "bar": BAR,
            "not_done_on_purpose": NOT_DONE,
            "pre_registered_fail_modes": FAIL_MODES,
            "the_prompt_is_unchanged": {
                "chars": len(prompt),
                "asserted": "byte-identical to ep2-b15-listenmid-0820's",
            },
        })
    out = os.path.join("pipeline", "jobs", "%s.yaml" % NEW_ID)
    ckey = [k for k in child["payload"] if k.endswith("b15-motion-prompt.txt")][0]
    if child["payload"][ckey] != prompt:
        raise SystemExit("!! the prompt changed. This job's only variable is the "
                         "seed. REFUSING.")
    print("prompt unchanged, %d chars; seed %d -> %d" % (len(prompt), 20260820, SEED))
    print(derive_spec.write(child, out, force=force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
