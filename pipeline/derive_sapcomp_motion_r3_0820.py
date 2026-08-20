#!/usr/bin/env python3
"""RUNG 3: state what IS (beat 15), and place a MIDDLE as well as an end (03, 13).

Rung 2 proved the placement mechanism and split on its cost, and rung 3 is the
two repairs that split implies. Same init, same sha, same anchor, same seed
20260820, same negative byte for byte, same every flag. ONE VARIABLE EACH, and
in each case it is the action clause.

WHAT RUNG 2 ESTABLISHED, because rung 3 is derived from it and not from a guess:

  * A PLACEMENT OF THE LAST FRAME HOLDS THIS ENGINE WHERE A NEGATIVE CANNOT.
    Three for three. Beat 03 was out of frame at f114 and ended crouched; beat
    13 was walking away at f114 and ended folded small with a readable face;
    beat 15 stood at f100 and never stood.
  * THE COST SPLIT THE SET BY WHAT THE TERMINAL SENTENCE NAMES. Beats 03 and 13
    placed a STATIC ATTITUDE and paid: beat 03 froze dead for 33 frames from
    f088 (ncc 1.0000), beat 13's face-band interframe fell 10.80 -> 0.64 with
    the last twenty pairs at 0.148. Beat 15 placed an ONGOING ACTION -- head
    tilted toward the plant WHILE talking -- and paid nothing: FREEZE none, ncc
    0.926..1.000, HOLD strength 0.508, the loosest of all six clips.
  * A NEGATION INSIDE THE POSITIVE PROMPT IS NOT A PROHIBITION. Beat 15's rung 2
    ended with `Nobody touches the plant and nobody picks it up.` The sapling
    stayed rooted to f090 -- 85 frames better than rung 1 -- and then his hand
    closed on the stem at f105 and it was out of the ground at f120. Rung 1 lost
    the same plant to the idiom `a hand's width away`. Both fixes reintroduced
    the noun phrase they were written to exclude.

SO, ONE VARIABLE EACH:

  BEAT 15 -- the final sentence. The negation comes out and is replaced by a
  statement of what IS in the shot, with NO plant-touching noun anywhere in it:
  no `touch`, no `pick`, no `hand` within reach of the plant. The hands are
  still placed, on his knees, because that placement held for 105 frames in rung
  2 and is not what failed. Nothing else moves -- the ongoing-action terminal
  sentence is rung 2's and is left alone precisely because it worked.

  BEATS 03 AND 13 -- a MIDDLE is placed as well as an end, and both the middle
  and the end name something ONGOING rather than a pose. This is rung 2's own
  evidence applied: the sampler satisfied a static terminal attitude by making
  every frame the last frame, so rung 3 gives it a state at the halfway point to
  travel through and describes both states as continuing actions (eyes moving,
  shoulders settling, breathing, the head still going over) rather than as
  positions to be arrived at and held.

NOT DONE THIS PASS: beat 13's plate-exposure rung. Its rung-2 verdict names the
DIM green-gloom plate as the reason G8 (the shade on his eyes) failed and says
the next rung is a plate rung -- but that is only true if the WORDING is not
also implicated, and rung 2's wording was frozen nearly solid. Deferred until
this sample says whether a moving take can find the shade. If G8 fails again
here, on a clip that is demonstrably not frozen, the plate rung is the answer
and this defers to it.

$0. Writes three spec files and nothing else.
Run:  python3 pipeline/derive_sapcomp_motion_r3_0820.py [--force]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 20260820

BEATS = [
    dict(
        parent="pipeline/jobs/ep2-b15-listenlast-0820.yaml",
        new_id="ep2-b15-listenroot-0820", beat=15, p="b15", tag="listenroot",
        old_base="15-good-listener-LTX-lastframe-0820",
        new_base="15-good-listener-LTX-rooted-0820",
        old_bench="bench-b15-listenlast",
        # ONE SENTENCE REPLACED. Everything before it is rung 2's, byte for byte.
        replace=("Nobody touches the plant and nobody picks it up.",
                 "The plant's thin stem stays in the ground for the whole shot, "
                 "rising up out of the grass beside him with soil and grass "
                 "around its base, and it is rooted there in the last frame "
                 "just as it is in the first."),
        variable=(
            "THE FINAL SENTENCE OF THE ACTION CLAUSE, and nothing else. "
            "`Nobody touches the plant and nobody picks it up.` becomes a "
            "statement of what IS: the stem stays in the ground, rising out of "
            "the grass, rooted in the last frame as in the first. NO "
            "PLANT-TOUCHING NOUN SURVIVES ANYWHERE IN THE PROMPT -- no `touch`, "
            "no `pick`, no `hand` in the same sentence as the plant. His hands "
            "are still placed, on his knees, because that placement held for 105 "
            "frames in rung 2 and is not what failed. The ongoing-action "
            "terminal sentence is rung 2's, unchanged, because it is the one "
            "thing in this family that bought position for free."),
        rung2=("ep2-b15-listenlast-0820: FAIL at the last frame and the best clip "
               "of six. Rooted to f090 (85 frames better than rung 1), never "
               "stands, talks throughout, FREEZE none, HOLD strength 0.508 -- the "
               "loosest of all six. Then his hand closes on the stem at f105 and "
               "at f120 the plant is out of the ground."),
        bar={
            "H1_THE_PLANT_IS_STILL_ROOTED_IN_THE_LAST_FRAME": (
                "THE FAILED CLAUSE AND THE ONLY REASON THIS RUNG EXISTS. At f105 and "
                "f120, read at 2x on the plant region: the stem runs down into the "
                "grass and no hand is on it. Rung 2 is the control and it is a precise "
                "one -- it passed this at f090 and failed it at f105, so the whole "
                "question is the last sixth of the clip. A clip that holds to f090 and "
                "loses it again is a FAIL and the finding would be that the pick-up is "
                "not prompt-driven at all but something the engine does to a small "
                "object near a hand, after which the next rung is mechanical."),
            "H2_NOTHING_IS_BOUGHT_FROM_THE_PERFORMANCE": (
                "Rung 2's own numbers are the floor, because rung 2 is the control and "
                "it cost nothing: FREEZE none, and HOLD strength at or below 0.60 "
                "(rung 2 read 0.508; its frozen beat-03 sibling read 0.958 with a "
                "33-frame dead tail). A rung 3 that fixes the plant by stilling the "
                "clip has traded the one clean result in this family for the one "
                "broken clause, and is a FAIL."),
            "H3_the_beat_still_reads_and_he_stays_seated": (
                "Carried from rung 2, which passed both: he is sitting in the grass at "
                "f120, and his mouth is open and moving at f030/f060/f090. A "
                "regression on either is attributable to the one sentence."),
        },
    ),
    dict(
        parent="pipeline/jobs/ep2-b03-coverlast-0820.yaml",
        new_id="ep2-b03-covermid-0820", beat=3, p="b03", tag="covermid",
        old_base="03-bad-cover-LTX-lastframe-0820",
        new_base="03-bad-cover-LTX-midend-0820",
        old_bench="bench-b03-coverlast",
        replace=(
            "He is crouched down low in the grass behind the little two-leaf plant, "
            "ducking to hide behind it, and he stays down in the same spot. His head "
            "and shoulders drop toward the grass, his eyes go wide and dart to one "
            "side. The plant hides almost none of him and he stays plainly visible in "
            "full view. IN THE LAST FRAME he is still crouched down low in the grass "
            "behind the plant, with his shoulders no higher than the top of the "
            "leaves and his head down.",
            "He is crouched down low in the grass behind the little two-leaf plant, "
            "ducking to hide behind it, and he stays down in the same spot. He keeps "
            "sinking lower and his eyes keep darting from side to side as he watches. "
            "HALFWAY THROUGH THE SHOT he is low behind the plant with his shoulders "
            "still settling downward and his eyes still moving. IN THE LAST FRAME he "
            "is still crouched down low behind the plant with his shoulders no higher "
            "than the top of the leaves, still breathing and still watching, and his "
            "eyes are still moving. The plant hides almost none of him and he stays "
            "plainly visible in full view."),
        variable=(
            "THE ACTION CLAUSE GAINS A MIDDLE AND BOTH ITS STATES BECOME ONGOING. "
            "Rung 2 placed one static terminal attitude -- `IN THE LAST FRAME he is "
            "still crouched down low` -- and the sampler satisfied it by making every "
            "frame the last frame: 33 frames byte-identical from f088. Rung 3 names a "
            "state at the halfway point for it to travel through, and describes both "
            "the middle and the end as things still happening (shoulders still "
            "settling, eyes still moving, still breathing) rather than as positions "
            "arrived at. The wording shape is taken from the one sibling that paid no "
            "cost, ep2-b15-listenlast-0820, whose terminal sentence named an ongoing "
            "action and did not freeze."),
        rung2=("ep2-b03-coverlast-0820: the placement worked and G2 fired with it. He "
               "is still crouched behind the plant at f120 where rung 1 was out of "
               "frame at f114 -- and judge_clip reports 33 FRAMES DEAD AT THE TAIL "
               "FROM FRAME 88, ncc exactly 1.0000. He holds the pose because the "
               "render stopped."),
        bar={
            "H1_NO_TERMINAL_FREEZE": (
                "THE FAILED CLAUSE. judge_clip FREEZE must read none, or a run shorter "
                "than 6 frames. Rung 2 read 33 frames dead from f088 at ncc 1.0000 and "
                "is the control. This is the clause the rung exists for and it is "
                "measured by a committed instrument rather than by eye."),
            "H2_he_is_still_crouched_in_the_last_frame": (
                "CARRIED FROM RUNG 2, WHICH WON IT, and it must not be given back. At "
                "f120 he is down in the grass behind the plant, in frame, shoulders no "
                "higher than the leaf tops. Rung 1 was out of frame at f114. A rung 3 "
                "that unfreezes the tail by letting him stand up again has undone the "
                "one thing rung 2 achieved."),
            "H3_the_duck_reads_and_keeps_reading": (
                "The head-and-shoulders drop is there AND the last twenty frames are "
                "not a held photograph: whole-frame ncc floor below 0.95 (rung 2: "
                "0.891 overall but 1.0000 for its last 33). Judged at 1:1 as well -- "
                "the number chooses the frames, the eyes decide."),
            "H4_the_cover_is_still_comically_inadequate": (
                "He is plainly visible at f120; the plant hides a strip and no more. "
                "beats.'03'.done_when: `a crouch that actually conceals him fails the "
                "beat`."),
        },
    ),
    dict(
        parent="pipeline/jobs/ep2-b13-shadelast-0820.yaml",
        new_id="ep2-b13-shademid-0820", beat=13, p="b13", tag="shademid",
        old_base="13-the-shade-LTX-lastframe-0820",
        new_base="13-the-shade-LTX-midend-0820",
        old_bench="bench-b13-shadelast",
        replace=(
            "He is sitting folded small in the grass beside the little two-leaf plant "
            "with his knees up around his ears, and he stays sitting there in the same "
            "spot. His head tilts over to ONE SIDE, his cheek toward the plant, until "
            "the plant's small patch of shade lies across his eyes. IN THE LAST FRAME "
            "he is still sitting in the grass with his knees up, his head tilted over "
            "sideways with his face still turned toward the camera, and the small "
            "patch of shade lying across his eyes.",
            "He is sitting folded small in the grass beside the little two-leaf plant "
            "with his knees up around his ears, and he stays sitting there in the same "
            "spot. His head keeps tilting further over to ONE SIDE, his cheek toward "
            "the plant, and he keeps breathing slowly while he settles. HALFWAY "
            "THROUGH THE SHOT he is sitting with his head part of the way over to the "
            "side and his face turned toward the camera, still breathing and still "
            "leaning over. IN THE LAST FRAME he is still sitting in the grass with his "
            "knees up, his head tilted right over sideways, his face still turned "
            "toward the camera and still breathing, and the plant's small patch of "
            "shade is lying across his eyes."),
        variable=(
            "THE ACTION CLAUSE GAINS A MIDDLE AND BOTH ITS STATES BECOME ONGOING, the "
            "same edit as its beat-03 sibling and for the same measured reason. Rung "
            "2's terminal sentence named a static attitude and the face-band "
            "interframe collapsed 10.80 -> 0.64, with the last twenty pairs at 0.148. "
            "Rung 3 gives the tilt a halfway state to pass through and keeps both "
            "states in continuous aspect -- `keeps tilting`, `keeps breathing`, `still "
            "leaning over`, `still breathing` -- on the evidence of "
            "ep2-b15-listenlast-0820, whose ongoing-action terminal sentence held "
            "position at HOLD strength 0.508 with no freeze."),
        rung2=("ep2-b13-shadelast-0820: the placement worked on every clause it was "
               "aimed at and G2 took the performance. Still folded small with his "
               "knees up at f120 and his FACE READABLE IN EVERY FRAME, where rung 1 "
               "folded its face into its knees from f024 and walked out at f114 -- and "
               "face-band interframe mean 10.80 -> 0.64, last-20 24.07 -> 0.148, "
               "whole-frame ncc range 0.687..1.000 -> 0.972..0.9997."),
        bar={
            "H1_THE_PERFORMANCE_COMES_BACK": (
                "THE FAILED CLAUSE, and it is measured on the same fixed face band "
                "(250,240,400,360) as rung 2 so the three rungs are directly "
                "comparable. Mean absolute interframe luma at or above 3.0, and the "
                "last twenty pairs at or above 1.0. The three readings so far are rung "
                "1 10.80 / 24.07 and rung 2 0.64 / 0.148. THE BAR IS DELIBERATELY NOT "
                "RUNG 1'S NUMBER: rung 1 earned its 10.80 by standing up and walking "
                "out of frame, so matching it would be a failure. What is wanted is a "
                "seated man who is visibly alive, which is a middle this family has "
                "not yet produced."),
            "H2_he_is_still_seated_knees_up_face_readable": (
                "CARRIED FROM RUNG 2, WHICH WON BOTH, and neither may be given back. At "
                "f120 he is folded small with his knees up -- the founder's ruling, "
                "`no slide, he sits down beside it`, 2026-08-18 -- and his face is "
                "legible at f000, f030, f060, f090 and f120. Rung 1 lost the face for "
                "fifty frames to a forward fold and rung 3 must not reintroduce it "
                "while chasing H1."),
            "H3_the_tilt_is_SIDEWAYS_and_goes_further_than_rung_2s": (
                "Rung 2's tilt was a lean rather than a tip. With a halfway state named "
                "and the aspect continuous, the head should travel further over to the "
                "side by f120 than it did in rung 2, judged at 1:1 side by side."),
            "H4_G8_the_shade_on_his_eyes_and_what_it_decides": (
                "Weak again and named again. Rung 2 failed it and blamed the DIM plate, "
                "but rung 2 was also frozen nearly solid, so the plate was not the only "
                "suspect. THIS SAMPLE IS WHAT SETTLES IT: if H1 passes -- a clip that is "
                "demonstrably moving -- and G8 still fails, the wording is exonerated "
                "and beat 13's next rung is the PLATE EXPOSURE rung its rung-2 verdict "
                "named, deferred from this pass on purpose."),
        },
    ),
]


def _fresh(b):
    return dict(
        owner="the composite-plate motion lane, 2026-08-20, rung 3",
        consumer=(
            "The episode 2 cut, beat %02d, still a SLATE. Rung 2 fixed this beat's "
            "position and left exactly one clause broken; this is the repair for "
            "that clause and nothing else. Downstream: the beat's entry in "
            "review/ep2-picks/ and, if it passes, a founder screening. The cut "
            "swap is a taste call and is not proposed here." % b["beat"]),
        success=(
            "ONE 704x1280 121-frame mp4 off the same init and the same seed as %s, "
            "differing from it in ONE CLAUSE, which repairs that job's single "
            "failed bar WITHOUT giving back anything it won. %s Rung 2 is the "
            "control and the comparison is frame for frame against it: same init, "
            "same sha, same anchor, same seed, same negative byte for byte, same "
            "every flag, so a difference between them was bought by that clause."
            % (os.path.basename(b["parent"]), b["variable"])),
        why=(
            "$0, ~12 minutes, no download, and the card is idle. Rung 2 settled "
            "the mechanism -- a placement of the last frame holds this engine "
            "where a negative cannot, three beats for three -- and split on its "
            "cost in a way that names its own repair: the one sibling that paid "
            "NOTHING is the one whose terminal sentence described an ongoing "
            "action rather than a pose. Rung 3 applies that observation to the two "
            "that froze and removes the last negation from the one that did not. "
            "Nothing else changes, so a bad result is attributable to the clause."),
    )


def _extra(b):
    parent = derive_spec.load(os.path.join(REPO, b["parent"]))
    probe = dict(parent["skin_probe"])
    probe["carried_verbatim_from"] = (
        "%s, and through it from the rung-1 spec where the box was placed by eye at "
        "5x before any of these frames existed. Every rung renders the same init at "
        "the same sha, anchor and 704x1280 crop, so the box lands on the same skin. "
        "Copied byte for byte and labelled rather than re-placed: re-placing a probe "
        "after the frames exist is choosing the number."
        % os.path.basename(b["parent"]))
    return {
        "skin_probe": probe,
        "rung_2_the_control": b["rung2"],
        "the_one_variable": b["variable"],
        "bar": b["bar"],
        "not_done_on_purpose": (
            "NO recipe change -- size, frames, fps, guidance, distilled sigmas, "
            "two-stage, offload, mode and --image-crf 10 are the b14 crf-10 "
            "parent's, three rungs deep now. NO new init, NO new sha, NO new "
            "anchor. NO new seed: 20260820 for the third time, so rungs 1 and 2 are "
            "both true controls. NO change to the NEGATIVE, unchanged since rung 1 "
            "-- it named `standing up` and `walking out of frame` and failed, and "
            "leaving it in place is what keeps every rung a test of the positive. "
            "NO plate work: beat 13's plate-exposure rung is deferred to what H4 "
            "says here. No pick, no plate_ack, no cut, no publication."),
        "pre_registered_fail_modes": [
            "F-STILL-FROZEN / F-STILL-DAMPED -- the middle placement does not "
            "restore motion, in which case the finding is that terminal "
            "conditioning saturates regardless of aspect and the next rung is "
            "mechanical: a shorter render, since 121 frames is the whole slot and a "
            "73-frame clip has no dead tail to fill.",
            "F-POSITION-GIVEN-BACK -- motion returns and he stands up or leaves "
            "again, i.e. the middle placement dilutes the terminal one. That would "
            "be a real finding about how much a single prompt can place at once.",
            "F-PLANT-PICKED-UP -- beat 15's failed clause; re-checked on all three, "
            "since beats 03 and 13 have now held their plants across two rungs each.",
            "F-MIDDLE-IS-A-CUT -- `HALFWAY THROUGH THE SHOT` is read as a shot "
            "change rather than as a moment. The negative already carries `cut to "
            "another shot, scene change, shot change`, which by this ladder's own "
            "law is not protection; named so it is a finding and not a surprise.",
            "F-IDENTITY-DRIFT -- held on all six clips so far; a regression would be "
            "attributable to the clause.",
        ],
    }


def main():
    force = "--force" in sys.argv
    for b in BEATS:
        parent = derive_spec.load(os.path.join(REPO, b["parent"]))
        key = [k for k in parent["payload"]
               if k.endswith("%s-motion-prompt.txt" % b["p"])][0]
        old_prompt = parent["payload"][key]
        before, after = b["replace"]
        if before not in old_prompt:
            raise SystemExit("!! %s: the clause to replace is not in the parent "
                             "prompt -- refusing to write a spec whose 'one "
                             "variable' matched nothing." % b["new_id"])
        new_prompt = old_prompt.replace(before, after, 1)
        child = derive_spec.derive(
            src=b["parent"], new_id=b["new_id"],
            by="pipeline/derive_sapcomp_motion_r3_0820.py",
            fresh=_fresh(b),
            overrides={"payload:%s-motion-prompt.txt" % b["p"]: new_prompt,
                       "seed": SEED},
            retoken=[(os.path.basename(b["parent"])[:-5], b["new_id"]),
                     (b["old_base"], b["new_base"]),
                     (b["old_bench"], "bench-%s-%s" % (b["p"], b["tag"]))],
            extra=_extra(b))
        out = os.path.join("pipeline", "jobs", "%s.yaml" % b["new_id"])
        print(derive_spec.write(child, out, force=force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
