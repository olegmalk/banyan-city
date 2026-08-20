#!/usr/bin/env python3
"""RUNG 5 on beat 15: the action clause finally gets a MIDDLE in continuous aspect.

ONE VARIABLE -- ONE INSERTED SENTENCE. Same init, same sha, same anchor, same
seed 20260820, same negative byte for byte, same 121 frames, same every flag.
Rung 4 is the control and it is exact: this box has demonstrated bit-exact
reproducibility on this recipe across an eight-hour gap.

WHY THIS AND NOT A FIFTH PLANT EDIT. Rungs 1-4 all spent their variable on the
plant clause, and rung 4 closed it: the goblin is in all 121 frames, there is no
mound anywhere, and H1 passes with the character who could pick the plant up
still in the picture. The noun law has its confirmation and the axis is done.

WHAT RUNG 4 LEAVES, MEASURED. It fails H2 on both halves -- FREEZE 5 frames from
f116 against a bar of none, HOLD strength 0.638 against 0.60 and against rung 2's
0.508 -- and the number understates the shape. The clip is two clips:

    whole-frame interframe f009 -> f084 : mean 0.166, max 0.417   (75 dead frames)
    every spike in the clip             : f087..f118
    mouth band over the dead stretch    : mean 0.213, max 1.192   (open, HELD)
    his eye band, template-matched      : dx 0 dy 0 at f087, then
                                          dx +184 dy -30 at f120
    the background rock over the same   : dx 0..+3

So: nothing for two thirds, then everything at once, including a slide a quarter
of the frame wide, away from the plant, on a locked camera.

THAT IS THE EXACT SHAPE BEATS 03 AND 13 HAD BEFORE THEIR RUNG 3, AND THE REPAIR
IS ALREADY MEASURED ON BOTH. The edit is: name a state at the halfway point for
the sampler to travel through, and describe it as something still HAPPENING
rather than a pose arrived at.

    beat 13  face band mean abs interframe   0.64 -> 4.798   (bar 3.0)
    beat 13  last twenty pairs               0.148 -> 2.263  (bar 1.0)
    beat 03  step frames f060..f072          0.44/0.40/0.34 -> 7.60/7.29/7.02
    beat 03  judge_clip FREEZE               33 from f088 -> 7 from f114

Beat 15 has never had this edit. It is one sentence, it is proven on two siblings
at the same init family and the same seed, and F-MIDDLE-IS-A-CUT is already
ANSWERED on both of them -- `HALFWAY THROUGH THE SHOT` produced no shot change,
no relocation and no second scene, largest whole-frame interframe 4.32 on beat 13
and 7.7 on beat 03.

AND IT IS THE CHEAPEST AVAILABLE TEST OF THE RELOCATION. The inserted sentence
says he is sitting IN THE SAME SPOT at the halfway point, so it is a POSITION
anchor in the middle as well as an ongoing action. Rung 4's terminal sentence
places his posture and his hands and says nothing about where in the frame he is
sitting, and by this ladder's own law an unplaced thing takes whatever position
is going. If he still slides right, a frame-position phrase in the TERMINAL
sentence is rung 6 -- named here, not fired here, because bolting it on now would
be a second variable.

NOT DONE: no fifth edit to the rooting clause, no touch to the terminal sentence,
no shorter render (--frames is an input to the denoiser's temporal grid, not a
crop, so a shorter rung is a re-roll and cannot inherit this one's early frames),
no new seed, no new init, no plate work.

$0. Writes ONE spec file and nothing else.
Run:  python3 pipeline/derive_b15_listenmid_r5_0820.py [--force]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 20260820

PARENT = "pipeline/jobs/ep2-b15-listengrass-0820.yaml"
NEW_ID = "ep2-b15-listenmid-0820"
OLD_BASE = "15-good-listener-LTX-grassroot-0820"
NEW_BASE = "15-good-listener-LTX-mid-0820"
OLD_BENCH = "bench-b15-listengrass"
NEW_BENCH = "bench-b15-listenmid"

# The insertion point: the terminal sentence, kept byte for byte, gains a
# sentence in front of it. Nothing else in the prompt is touched.
ANCHOR = ("IN THE LAST FRAME he is still sitting in the grass with both hands on "
          "his knees,")
MIDDLE = ("HALFWAY THROUGH THE SHOT he is still sitting in the same spot with both "
          "hands still on his knees, his head still going further down and over "
          "toward the two leaves, and his mouth still moving as he keeps talking "
          "to them. ")

GROUND_NOUNS = ("soil", "earth", "dirt", "mud", "loam", "clay", "ground",
                "topsoil", "humus", "compost", "sand", "gravel", "mound")
TOUCH_WORDS = ("touch", "pick", "pluck", "grab", "hold", "lift", "uproot", "pull")

VARIABLE = (
    "ONE SENTENCE INSERTED IN FRONT OF THE TERMINAL SENTENCE, and nothing "
    "removed and nothing else changed. `HALFWAY THROUGH THE SHOT he is still "
    "sitting in the same spot with both hands still on his knees, his head still "
    "going further down and over toward the two leaves, and his mouth still "
    "moving as he keeps talking to them.` Every clause in it is CONTINUOUS -- "
    "still sitting, still going further, still moving, keeps talking -- because "
    "the one thing this family has measured about terminal conditioning is that a "
    "static attitude is satisfied by making every frame the last frame, and an "
    "ongoing action is not. It also names WHERE he is (`in the same spot`) at the "
    "midpoint, which is the cheapest test of rung 4's relocation: 184 px right, "
    "30 px up, on a camera measured locked. THE ROOTING CLAUSE IS NOT TOUCHED and "
    "carries no ground-material noun; the terminal sentence is not touched; the "
    "negative, the seed, the init, the sha, the anchor, the frame count and every "
    "render flag are rung 4's.")

RUNG_4_CONTROL = (
    "ep2-b15-listengrass-0820: THE NOUN DELETION WORKED AND IT IS STILL A FAIL. "
    "The goblin is in all 121 frames and there is no mound of soil anywhere -- "
    "verified frame by frame and at 1:1 across f093..f098 -- where rung 3 deleted "
    "him at f094 and replaced him with bare earth. The plant is rooted at f105 and "
    "f120 with no hand on it, and the skin probe could be RE-PLACED for the first "
    "time on this beat: cheek (505,440,555,464) at f120 reads luma 92.0 / R-B 15.8 "
    "/ std 13.5 against f000's 90.3 / 18.8 / 14.3, i.e. +1.7 luma with the "
    "dispersion matching. IT FAILS H2: FREEZE 5 frames from f116 against a bar of "
    "none, HOLD strength 0.638 against 0.60 and against rung 2's 0.508 -- and the "
    "shape is worse than the margin. f009->f084 reads mean 0.166 / max 0.417 "
    "whole-frame, the mouth band 0.213 over the same stretch (open, HELD), and "
    "every spike in the clip lives in f087..f118, where he also slides 184 px "
    "right and 30 px up while the background holds at dx 0..+3.")

BAR = {
    "H1_THE_DEAD MIDDLE IS GONE".replace(" ", "_"): (
        "THE CLAUSE THIS RUNG EXISTS FOR, and the instrument is rung 4's own. "
        "Whole-frame mean-absolute interframe luma over the STEP FRAMES from f009 "
        "to f084 -- this family holds every 3rd frame at 8.0 effective fps, so the "
        "gaps are meaningless and the step frames are the signal -- must have a "
        "MEAN of at least 1.5 and at least a THIRD of its step frames above 1.0. "
        "Rung 4 read mean 0.166 with a maximum of 0.417 over the whole stretch: not "
        "one step frame anywhere near 1.0. Rung 2, the loosest clip in the family, "
        "is the other control. PUBLISHED WITH ITS SHAPE, never as a bare mean: beat "
        "13's rung 3 read 4.798 as a mean and 26-35 on its step frames, and the "
        "bare mean would have read as smooth motion that is not on the screen."),
    "H2_THE_PLANT_AND_THE_SUBJECT_BOTH_SURVIVE_IT": (
        "GATE, and it is carried from rung 4's H0 and H1 together because rung 4 is "
        "the first clip on this beat to hold both at once and it must not be given "
        "back. The goblin is present and recognisable in every one of the 121 "
        "frames, checked on a full-clip sheet with f094 opened by name; and at f105 "
        "and f120 the plant is ONE thin stem with TWO leaves running down into the "
        "grass with no hand on it. IF EITHER FAILS, NOTHING ELSE IS SCORED -- a "
        "motion clause measured on a clip that lost its subject or its plant is the "
        "mistake rung 3 made and rung 4 was written to stop."),
    "H3_THE_RELOCATION_IS_SMALLER": (
        "His own eye band, template-matched against f010, must end within 60 px of "
        "where it started, measured at f105 AND f120, with the background rock "
        "template published beside it at the same frames so a camera move cannot be "
        "scored as a slide. Rung 4 read dx +182 dy -30 at f105 and dx +184 dy -30 "
        "at f120 against a rock holding at dx 0..+3. 60 px is a THIRD of rung 4's "
        "slide and is deliberately not zero: the middle sentence anchors the "
        "midpoint, not the end, so a partial fix is the expected shape of a pass "
        "and would be a real finding either way."),
    "H4_no_terminal_freeze_and_no_stillness_tax": (
        "judge_clip FREEZE must read none, or a run shorter than 5 (rung 4 read 5 "
        "from f116; rung 2 read none), and HOLD strength must come in at or below "
        "rung 4's 0.638. VOID CONDITION, carried: these are a performance reading "
        "only while the clip is ONE CONTINUOUS SHOT. All six clips in this family "
        "read period 3 at 8.0 effective fps; a clip that reads period 1 has a cut "
        "in it and its hold statistics are RETRACTED, not credited."),
    "H5_the_beat_still_reads": (
        "Carried from rung 4, which passed it: he is sitting in the grass with his "
        "knees up and both hands on his knees at f120, and his mouth is open at "
        "f030, f060 and f090. Read at 4x, not off a number."),
}

FAIL_MODES = [
    "F-MIDDLE-DOES-NOTHING -- the dead middle survives the insertion, i.e. this "
    "beat's terminal conditioning saturates in a way beats 03 and 13's did not. "
    "That would be the first divergence in this family under an identical edit and "
    "would point at the PLATE rather than the words -- beat 15's is the only one of "
    "the three whose subject and plant are far apart, so there may simply be no "
    "small action available to him that the frame can show.",
    "F-MIDDLE-IS-A-CUT -- `HALFWAY THROUGH THE SHOT` read as a shot change. "
    "ANSWERED NO on beats 03 and 13 with largest whole-frame interframe 4.32 and "
    "7.7, so this is carried for completeness rather than as a live risk; it is "
    "re-reported because the negative's `cut to another shot, scene change, shot "
    "change` is by this ladder's own law not protection.",
    "F-SUBJECT-RELOCATES-AGAIN -- H3 fails, i.e. a midpoint position anchor does "
    "not hold the end. NAMED AS THE MOST LIKELY FAILURE OF THIS RUNG, because the "
    "anchor is in the wrong sentence for the frame it has to fix: the slide happens "
    "between f087 and f105, after the midpoint. If it fires, rung 6 is a frame "
    "position in the TERMINAL sentence -- one clause, and the axis is then closed at "
    "two placements.",
    "F-PLANT-PICKED-UP / F-SUBJECT-DELETED -- H2's gate. Held on rung 4 and on "
    "both sibling beats through the same edit; a regression is attributable to the "
    "inserted sentence and would be a serious finding about how much one prompt can "
    "place at once.",
    "F-MOTION-AT-THE-COST-OF-THE-FACE -- beat 13 paid for this exact edit by "
    "pressing its face into its own knee for thirty frames in the middle. Beat 15's "
    "equivalent cost would be the mouth or the head occluding at f060, which H5 "
    "checks by eye at 4x.",
    "F-IDENTITY-DRIFT -- held on rung 4 with a re-placed probe whose dispersion "
    "matched (std 13.5 against 14.3). Publish luma_std with every reading: a "
    "collapse is a box on a field and an inflation is a box on an edge, and only "
    "the dispersion shows either.",
]

NOT_DONE = (
    "NO FIFTH EDIT TO THE ROOTING CLAUSE -- that axis is closed by rung 4, which "
    "removed two words, added none, and produced a clip with the goblin in all 121 "
    "frames and no mound anywhere. NO TOUCH TO THE TERMINAL SENTENCE: a frame "
    "position there is rung 6 if H3 fails, and adding it now would make this rung "
    "two variables and unattributable. NO recipe change -- size, frames, fps, "
    "guidance, distilled sigmas, two-stage, offload, mode and --image-crf 10 are "
    "the b14 crf-10 parent's, five rungs deep. NO new init, NO new sha, NO new "
    "anchor. NO new seed: 20260820 for the fifth time. NO change to the NEGATIVE, "
    "unchanged since rung 1. NO SHORTER RENDER: --frames is an input to the "
    "denoiser's temporal grid and not a crop, so shortening re-rolls the whole "
    "video and cannot inherit this one's early frames as evidence. NO plate work "
    "and NO composite -- beat 15's plate puts him and the sapling far apart and "
    "that is a real open question, but it belongs to the plate lane and is not "
    "this rung. No pick, no plate_ack, no cut, no publication: beat 15 stays a "
    "SLATE.")


def main():
    force = "--force" in sys.argv
    parent = derive_spec.load(os.path.join(REPO, PARENT))
    key = [k for k in parent["payload"]
           if k.endswith("b15-motion-prompt.txt")][0]
    old = parent["payload"][key]
    if old.count(ANCHOR) != 1:
        raise SystemExit("!! the terminal sentence appears %d times in the parent "
                         "prompt (want exactly 1) -- refusing to guess where the "
                         "middle goes." % old.count(ANCHOR))
    new = old.replace(ANCHOR, MIDDLE + ANCHOR, 1)

    low = MIDDLE.lower()
    hit = [n for n in GROUND_NOUNS if n in low]
    if hit:
        raise SystemExit("!! the inserted sentence carries the ground-material "
                         "noun(s) %s -- rung 4 spent a GPU fire proving that "
                         "costs the subject. REFUSING." % ", ".join(hit))
    hit = [w for w in TOUCH_WORDS if w in low]
    if hit:
        raise SystemExit("!! the inserted sentence carries the plant-touching "
                         "word(s) %s -- rungs 1 and 2 each lost the plant to one. "
                         "REFUSING." % ", ".join(hit))
    if len(new) - len(old) != len(MIDDLE):
        raise SystemExit("!! the prompt grew by %d chars, not the inserted "
                         "sentence's %d -- something else changed. REFUSING."
                         % (len(new) - len(old), len(MIDDLE)))
    if old not in new.replace(MIDDLE, "", 1):
        raise SystemExit("!! rung 4's prompt is not contained in rung 5's minus "
                         "the insertion. This rung is an INSERTION and nothing "
                         "else. REFUSING.")

    child = derive_spec.derive(
        src=PARENT, new_id=NEW_ID,
        by="pipeline/derive_b15_listenmid_r5_0820.py",
        fresh=dict(
            owner="the composite-plate motion lane, 2026-08-20, rung 5",
            consumer=(
                "The episode 2 cut, beat 15, still a SLATE. Rung 4 fixed the plant "
                "clause and left a shape problem -- 75 dead frames and then "
                "everything at once, including a slide a quarter of the frame wide. "
                "This is the edit that repaired exactly that shape on beats 03 and "
                "13, applied to beat 15 for the first time. Downstream: the beat's "
                "entry in review/ep2-picks/ and, if it passes, a founder screening. "
                "The cut swap is a taste call and is not proposed here."),
            success=(
                "ONE 704x1280 121-frame mp4 off the same init and the same seed as "
                "ep2-b15-listengrass-0820.yaml, differing from it by ONE INSERTED "
                "SENTENCE and nothing else, in which the middle of the clip is no "
                "longer dead, the goblin is still in all 121 frames and the plant is "
                "still rooted with no hand on it. %s" % VARIABLE),
            why=(
                "$0, ~4.5 minutes of GPU, no download. Beat 15 has spent four rungs "
                "on the plant clause and rung 4 closed it -- no mound, no deleted "
                "subject, H1 passing with the character present, and a skin probe "
                "that could be re-placed for the first time. What is left is not a "
                "plant question: 75 consecutive frames at 0.166 whole-frame "
                "interframe with an open mouth held still, and every spike crammed "
                "into the last quarter. That is the same shape beats 03 and 13 had, "
                "and the same one-sentence edit fixed it on both -- beat 13's face "
                "band 0.64 -> 4.798, beat 03's step frames 0.4 -> 7.6 -- so this is "
                "a measured repair rather than a fifth wording, and F-MIDDLE-IS-A-CUT "
                "is already answered NO on two beats before it is risked on a third."),
        ),
        overrides={"payload:b15-motion-prompt.txt": new, "seed": SEED},
        retoken=[(os.path.basename(PARENT)[:-5], NEW_ID),
                 (OLD_BASE, NEW_BASE), (OLD_BENCH, NEW_BENCH)],
        extra={
            "skin_probe": _probe(parent),
            "rung_4_the_control": RUNG_4_CONTROL,
            "the_one_variable": VARIABLE,
            "bar": BAR,
            "not_done_on_purpose": NOT_DONE,
            "pre_registered_fail_modes": FAIL_MODES,
            "the_prompt_diff": {
                "parent_chars": len(old),
                "child_chars": len(new),
                "chars_inserted": len(MIDDLE),
                "chars_removed": 0,
                "inserted_sentence": MIDDLE.strip(),
                "inserted_immediately_before": ANCHOR,
                "asserted_before_the_spec_was_written": [
                    "the parent prompt is contained in the child minus the "
                    "insertion, byte for byte",
                    "the growth equals the inserted sentence exactly",
                    "the inserted sentence contains no ground-material noun "
                    "(rung 3 cost the subject to one)",
                    "the inserted sentence contains no plant-touching word "
                    "(rungs 1 and 2 each cost the plant to one)",
                ],
            },
        })
    out = os.path.join("pipeline", "jobs", "%s.yaml" % NEW_ID)
    print("prompt %d -> %d chars (+%d inserted, 0 removed)"
          % (len(old), len(new), len(MIDDLE)))
    print(derive_spec.write(child, out, force=force))
    return 0


def _probe(parent):
    probe = dict(parent["skin_probe"])
    probe["carried_verbatim_from"] = (
        "ep2-b15-listengrass-0820.yaml, and through it from the rung-1 spec where "
        "the box was placed by eye at 5x before any of these frames existed. The "
        "box is UNMOVED, because every rung renders the same init at the same sha, "
        "anchor and crop.")
    probe["rung_4_re_placement_and_what_to_do_with_it"] = (
        "Rung 4's f120 reading in the fixed box was luma 201.9 with std 2.4 against "
        "f000's 90.3 / 14.3 -- a COLLAPSE, i.e. an empty box, because he had "
        "translated 184 px right out from under it. Re-placed by eye at 4x on f120 "
        "over a printed coordinate grid at (505,440,555,464) it read luma 92.0 / R-B "
        "15.8 / std 13.5, i.e. +1.7 luma with the dispersion matching, and identity "
        "held. DO THE SAME HERE: read the fixed box first, and if its dispersion "
        "collapses or explodes, retract it and re-place by eye on the frame in "
        "question rather than reporting the number. A dispersion that jumps is a box "
        "on an edge exactly as one that collapses is a box on a field; both are the "
        "premise dying and only the dispersion shows it.")
    return probe


if __name__ == "__main__":
    raise SystemExit(main())
