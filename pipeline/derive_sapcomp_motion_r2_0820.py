#!/usr/bin/env python3
"""RUNG 2 ON ALL THREE: the action clause becomes a PLACEMENT OF THE LAST FRAME.

ONE VARIABLE, and it is the same variable on all three beats, which is the
whole design. Rung 1 (ep2-b15-listenmotion-0820, ep2-b03-covermotion-0820,
ep2-b13-shademotion-0820) failed with one shared terminal defect and one
beat-specific one:

  * SHARED, all three: HE STANDS UP AND LEAVES. Beat 03 rises at f090 and is
    out of frame by f114; beat 13 rises at f084 and is out by f114; beat 15
    stands at f100. Every one of those three prompts carried `standing up` and
    `walking out of frame, leaving the frame` in its NEGATIVE, in the first
    clause or the middle. None held. Seventh, eighth and ninth sighting of
    POSITIVE PLACEMENT BEATS NEGATIVES.
  * BEAT 15 ONLY: the sapling was PICKED UP -- rooted at f000, held in a raised
    hand beside his face f020-f090, back in the ground by f100 -- because the
    action clause said `talks to them FROM A HAND'S WIDTH AWAY`. The idiom's
    `hand` is a unit of measurement in English and a PLACEMENT to the sampler.

BOTH ARE THE SAME BUG AND SO THEY GET ONE FIX. Rung 1's prompts described a
MOVEMENT ("he ducks down and freezes", "he tips his head sideways", "he talks
to them from a hand's width away") and then forbade the unwanted end state in
the negative. Rung 2's prompts describe THE LAST FRAME as a fact, and the
beat-15 rewrite drops the body-part noun as a side effect of saying the same
thing without an idiom.

THE PRECEDENT AND ITS NUMBERS. `ep2-b04-headlock-0820` moved exactly one clause
out of an instruction and into a placement -- "His head and shoulders stay
STILL" became "his chin stays square to the camera and his skull is locked in
place as if held, the same three-quarter angle in every frame" -- at the same
init, seed, negative and flags, and the head-band centroid travel fell from
64.7 px to 4.7 px. Fourteenfold, from a wording shape. That rung ALSO recorded
the cost, which is pre-registered here as this rung's top risk: the lock took
the eyes with it and the clip went too calm. See G2 below.

NOTHING ELSE MOVES. Same init, same seed 20260820, same negative, same recipe,
same framing, same skin probe. A difference between rung 1 and rung 2 is a
difference made by one sentence.

$0. Writes three spec files and nothing else.
Run:  python3 pipeline/derive_sapcomp_motion_r2_0820.py [--force]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

SEED = 20260820

BEATS = [
    dict(
        parent="pipeline/jobs/ep2-b15-listenmotion-0820.yaml",
        new_id="ep2-b15-listenlast-0820",
        beat=15, tag="listenlast", p="b15",
        out_base="15-good-listener-LTX-lastframe-0820",
        old_base="15-good-listener-LTX-sapcomp-0820",
        old_bench="bench-b15-listenmotion",
        action=(
            "He is sitting in the grass with both hands resting on his knees and he "
            "stays sitting there in the same spot. His head is tilted down and over "
            "to one side so that his face is a few centimetres from the two leaves, "
            "and he is talking to them: his mouth moves as he speaks. IN THE LAST "
            "FRAME he is still sitting in the grass with both hands on his knees, his "
            "head still tilted down toward the plant, and the plant is still rooted in "
            "the ground with its stem rising out of the grass beside him. Nobody "
            "touches the plant and nobody picks it up."),
        rung1=("ep2-b15-listenmotion-0820: FAIL on A1. Two leaves throughout, so the "
               "count never moved -- but from f020 to f090 the stem was gone and his "
               "forearm was where it had been, holding the leaf pair level with his "
               "eyes, and he stood up at f100."),
        variable=("The action clause. `talks to them FROM A HAND'S WIDTH AWAY` becomes "
                  "`his face is a few centimetres from the two leaves`, which says the "
                  "same distance with NO BODY-PART NOUN IN IT, and the clause now "
                  "places the last frame instead of describing a movement. The plant "
                  "clause gains the two sentences the failure names: rooted in the "
                  "ground in the last frame, and nobody picks it up."),
        bar={
            "G1_THE_PLANT_STAYS_IN_THE_GROUND": (
                "THE CLAUSE THIS RUNG EXISTS FOR. At f000, f030, f060, f090 and f120 the "
                "sapling's stem rises out of the grass and no hand is on it. Rung 1's "
                "exact failure -- a raised hand holding the leaf pair with the forearm "
                "where the stem was -- is a FAIL here however well the rest reads. Read at "
                "1:1 and at 2x on the plant region; no plant mask, for the reason the "
                "growmotion five went unscored."),
            "G3_he_is_still_seated_in_the_last_frame": (
                "At f120 he is sitting in the grass, not standing and not out of frame. "
                "Rung 1 stood him up at f100 against a negative that named `standing up` "
                "in its first clause."),
            "G4_the_beat_still_reads": (
                "His head is tilted down toward the leaves and his mouth moves. If G1 and "
                "G3 pass and G4 fails -- a seated, plant-respecting clip in which nothing "
                "happens -- that is the G2 cost below and the finding is about the "
                "placement shape, not about this beat."),
        },
    ),
    dict(
        parent="pipeline/jobs/ep2-b03-covermotion-0820.yaml",
        new_id="ep2-b03-coverlast-0820",
        beat=3, tag="coverlast", p="b03",
        out_base="03-bad-cover-LTX-lastframe-0820",
        old_base="03-bad-cover-LTX-sapcomp-0820",
        old_bench="bench-b03-covermotion",
        action=(
            "He is crouched down low in the grass behind the little two-leaf plant, "
            "ducking to hide behind it, and he stays down in the same spot. His head "
            "and shoulders drop toward the grass, his eyes go wide and dart to one "
            "side. The plant hides almost none of him and he stays plainly visible in "
            "full view. IN THE LAST FRAME he is still crouched down low in the grass "
            "behind the plant, with his shoulders no higher than the top of the "
            "leaves and his head down."),
        rung1=("ep2-b03-covermotion-0820: FAIL. The duck landed -- head near grass "
               "level f036-f084, the first time this beat's acting clause has moved at "
               "all -- and then he rose at f090 and walked out of the right of frame by "
               "f114. The plant held all 121 frames."),
        variable=("The action clause. `and freezes there ... he does not stand up and "
                  "does not leave the frame` becomes a placement of the last frame: `IN "
                  "THE LAST FRAME he is still crouched down low in the grass behind the "
                  "plant, with his shoulders no higher than the top of the leaves`. The "
                  "prohibition is deleted from the positive; the negative is unchanged, "
                  "so what is being tested is whether the PLACEMENT does what the "
                  "negative could not."),
        bar={
            "G3_he_is_still_crouched_in_the_last_frame": (
                "THE CLAUSE THIS RUNG EXISTS FOR. At f120 he is down in the grass behind "
                "the plant, in frame, with his shoulders no higher than the leaf tops. "
                "Rung 1 was out of frame by f114."),
            "G5_the_duck_survives_the_lock": (
                "The head-and-shoulders drop that rung 1 achieved between f036 and f084 is "
                "still there. Rung 1 is the control and it is a real one: this is the only "
                "beat-03 artifact on which the performance clause has ever moved, and a "
                "rung 2 that keeps him seated by freezing him has traded the win for the "
                "clause."),
            "G6_the_cover_is_still_comically_inadequate": (
                "He is plainly visible at f120; the plant hides a strip of him and nothing "
                "more. beats.'03'.done_when: `a crouch that actually conceals him fails "
                "the beat`."),
        },
    ),
    dict(
        parent="pipeline/jobs/ep2-b13-shademotion-0820.yaml",
        new_id="ep2-b13-shadelast-0820",
        beat=13, tag="shadelast", p="b13",
        out_base="13-the-shade-LTX-lastframe-0820",
        old_base="13-the-shade-LTX-sapcomp-0820",
        old_bench="bench-b13-shademotion",
        action=(
            "He is sitting folded small in the grass beside the little two-leaf plant "
            "with his knees up around his ears, and he stays sitting there in the same "
            "spot. His head tilts over to ONE SIDE, his cheek toward the plant, until "
            "the plant's small patch of shade lies across his eyes. IN THE LAST FRAME "
            "he is still sitting in the grass with his knees up, his head tilted over "
            "sideways with his face still turned toward the camera, and the small "
            "patch of shade lying across his eyes."),
        rung1=("ep2-b13-shademotion-0820: FAIL twice. The head tipped -- continuously "
               "from f004, so the predicted F-NOTHING-MOVES did not fire -- but it "
               "tipped FORWARD AND DOWN into his own knees, taking his face out of view "
               "from f024 to f078, and then he rose at f084 and was out of frame by "
               "f114. The plant held all 121 frames on the lowest-contrast plate here."),
        variable=("The action clause. `tips his head slowly sideways ... and does not "
                  "stand up, does not slide` becomes a placement of the last frame that "
                  "does two jobs in one sentence: still seated, knees up, head tilted "
                  "SIDEWAYS with the face still toward camera. `his face still turned "
                  "toward the camera` is the new half and it is aimed at rung 1's "
                  "specific miss -- a sideways tilt that keeps the face readable, rather "
                  "than the forward fold the init already afforded."),
        bar={
            "G3_he_is_still_seated_knees_up_in_the_last_frame": (
                "THE CLAUSE THIS RUNG EXISTS FOR, and it is a FOUNDER ruling and not a "
                "steward preference: `the shipped version stands (no slide, he sits down "
                "beside it, thin shade)`, 2026-08-18. At f120 he is seated with his knees "
                "up. Rung 1 was out of frame by f114."),
            "G7_the_tilt_is_SIDEWAYS_and_the_face_stays_readable": (
                "His head goes over to one side and his face is still visible at f120. "
                "Rung 1's tilt was real and pointed the wrong way: by f024 the head was a "
                "bald dome seen from above with the cloak's shadow where the face had "
                "been, and it stayed that way for fifty frames. A beat with no face in it "
                "cannot carry a reaction."),
            "G8_the_shade_lands_on_his_eyes": (
                "Weakest clause of the three and said so in advance. The plate's shade is "
                "thin and its frame is the green gloom beat 13's plate verdict already "
                "recorded as CARRIED, NOT FIXED. If G3 and G7 pass and only G8 fails, this "
                "beat's next rung is a PLATE exposure rung and not another wording."),
        },
    ),
]

G2_COST = (
    "G2 THE PRE-REGISTERED COST OF THIS SHAPE, and it is named because the "
    "precedent paid it. ep2-b04-headlock-0820 moved one clause from an "
    "instruction into a placement and cut head travel 64.7 px -> 4.7 px, "
    "fourteenfold -- AND IT TOOK THE EYES WITH IT: eye-band interframe fell "
    "0.356 -> 0.126 and the gaze stopped travelling, which its own spec had "
    "pre-registered as a degenerate pass and reported as a FAIL. The same "
    "trade is the likeliest failure here. A clip that holds the last frame by "
    "holding EVERY frame is a FAIL of this rung, not a pass, and the finding "
    "would be that terminal placement buys position at the cost of "
    "performance -- after which the next rung places the MIDDLE of the shot "
    "as well as its end, rather than reaching for a flag.")


def main():
    force = "--force" in sys.argv
    for b in BEATS:
        # the prompt is rebuilt from rung 1's, replacing only its action clause
        parent = derive_spec.load(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), b["parent"]))
        key = [k for k in parent["payload"]
               if k.endswith("%s-motion-prompt.txt" % b["p"])][0]
        old = parent["payload"][key]
        tail = old.split("The little plant stays exactly as it is", 1)[1]
        new_prompt = (b["action"] + " The little plant stays exactly as it is" + tail)
        b["_prompt"] = new_prompt
        child = derive_spec.derive(
            src=b["parent"], new_id=b["new_id"],
            by="pipeline/derive_sapcomp_motion_r2_0820.py",
            fresh=_fresh(b),
            overrides={"payload:%s-motion-prompt.txt" % b["p"]: new_prompt,
                       "seed": SEED},
            retoken=[(b["old_base"], b["out_base"]),
                     (b["old_bench"], "bench-%s-%s" % (b["p"], b["tag"]))],
            extra=_extra(b))
        out = os.path.join("pipeline", "jobs", "%s.yaml" % b["new_id"])
        print(derive_spec.write(child, out, force=force))
    return 0


def _fresh(b):
    return dict(
        owner="the composite-plate motion lane, 2026-08-20, rung 2",
        consumer=(
            "The episode 2 cut, beat %02d, still a SLATE. Rung 1 produced this beat's "
            "first motion candidate with a real canon sapling in it and the candidate "
            "is not cuttable, for a reason one sentence wide. This is the fix for that "
            "sentence. Immediately downstream: the beat's entry in review/ep2-picks/ "
            "and, if it passes, a founder screening. The cut swap is a taste call and "
            "is not proposed here." % b["beat"]),
        success=(
            "ONE 704x1280 121-frame mp4 off the same init and the same seed as %s, "
            "differing from it in ONE SENTENCE, in which THE LAST FRAME IS THE ONE THE "
            "PROMPT PLACES. %s The comparison that matters is against rung 1 frame for "
            "frame and not against an absolute: both clips exist, they share an init, a "
            "seed, a negative and every flag, so any difference between them was bought "
            "by that sentence." % (os.path.basename(b["parent"]), b["variable"])),
        why=(
            "$0, ~12 minutes, no download, and the card went idle the moment rung 1 "
            "finished. The remedy is already written in rung 1's own verdict, the "
            "precedent is measured -- 64.7 px -> 4.7 px on ep2-b04-headlock-0820 from "
            "one clause moved out of an instruction and into a placement -- and firing "
            "the same sentence shape on THREE beats at one seed tests the MECHANISM "
            "rather than the beat. Nothing else changes, so a bad result is "
            "attributable to the sentence."),
    )


def _extra(b):
    return {
        "rung_1_the_control": b["rung1"],
        "the_one_variable": b["variable"],
        "bar": dict(b["bar"], G2_the_pre_registered_cost=G2_COST),
        "not_done_on_purpose": (
            "NO recipe change: size, frames, fps, guidance, distilled sigmas, "
            "two-stage, offload, mode and --image-crf 10 are rung 1's, which are the "
            "b14 crf-10 parent's. NO new init -- the same composited plate, the same "
            "sha, the same anchor and the same pre-registered framing bbox. NO new "
            "seed: 20260820 again, so rung 1 is a true control. NO change to the "
            "NEGATIVE, which is the point -- it already named `standing up` and "
            "`walking out of frame` and did not hold, and leaving it in place is what "
            "makes this a test of the positive. No pick, no plate_ack, no cut, no "
            "publication."),
        "pre_registered_fail_modes": [
            "F-DEGENERATE-STILL -- the last frame is held by holding every frame. The "
            "precedent's own cost; see G2. A FAIL, not a safe outcome.",
            "F-STANDS-UP-ANYWAY -- the placement does no better than the negative did, "
            "in which case the finding is that words will not hold this engine in "
            "place on these inits and the next rung is mechanical rather than verbal.",
            "F-PLANT-PICKED-UP -- rung 1 held the plant on beats 03 and 13 and lost it "
            "to a hand on beat 15. Re-checked on all three.",
            "F-IDENTITY-DRIFT -- rung 1 held on all three; a regression here would be "
            "attributable to the sentence.",
        ],
    }


if __name__ == "__main__":
    raise SystemExit(main())
