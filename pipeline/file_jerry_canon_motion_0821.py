#!/usr/bin/env python3
r"""FILE the canon-motion tranche on the box. The deriver's missing half.

    python3 pipeline/file_jerry_canon_motion_0821.py --plan     # print, write nothing
    python3 pipeline/file_jerry_canon_motion_0821.py --write    # emit the seven yamls
    python3 pipeline/file_jerry_canon_motion_0821.py --write --force

WHY THIS FILE EXISTS AND IS NOT AN EDIT TO ITS SIBLING. The design lives in
`derive_jerry_canon_motion_0821.py` -- SLOTS, MOTION_STYLE, the identity clause,
the negative and the canon motion BAR are that lane's authorship and are imported
here, not retyped. What that module does NOT have is an emitter: its `--write`
prints "--write is intentionally not wired to the queue" and returns 0 having
written nothing, so the seven specs its docstring describes have never existed as
files. This module is the emitter, in its own file so two lanes are not writing
one path.

WHAT RENDERING THESE ANSWERS, stated before a frame exists. The sibling's premise
is that the face-dissolve is a function of how far the render is pushed, so a
shorter render dodges it. THE 14-CLIP WAVE CANNOT SUPPORT THAT CLAIM: every clip
in it rendered 121 frames, so it holds no evidence either way, and the onsets it
did record are NOT one number -- f055 on three clips, f065 on a fourth, ~f095 and
f106 on two more. Three of those are INSIDE 97 frames, so "trim to 97" does not
by itself get behind the fault. What is left is the real question, and it is the
one this tranche is the first to ask: DOES THE ONSET MOVE WITH THE TOTAL FRAME
COUNT? If a 105-frame render eggs at ~f048 the fault is proportional and no trim
will ever outrun it; if it eggs at f055 again the fault is absolute and 105 buys
nothing; if it does not egg at all, the sibling was right. All three outcomes are
worth four minutes of card time each, which is why these are filed as INFORMATION
with nothing swapped into any cut.

DEFECTS FIXED HERE, each mechanical, none a taste call:
  1. PLATE ROUND IS PER BEAT, NOT UNIFORM. The sibling hardcodes `PLATE_ROUND =
     "w2"` for all seven. Beats 02, 07 and 08 have a LATER round, w2b, which is
     w2 plus `background characters` and `group` in the plate negative on exactly
     the three beats where a second figure can intrude -- and for beats 07 and 08
     the repo's farm-out has no w2 plate at all. Each beat's init is bound here by
     name AND by sha256, verified against the box before filing.
  2. THE POSITIVE STOPPED FIGHTING ITS OWN NEGATIVE. The sibling's identity
     clause opens "ONE small green goblin child alone" while its own negative
     carries `child, chibi, baby` -- and canon's plate negative carries `child,
     chibi` too (jerry_canon_0821.NEGATIVE). The word is dropped from the
     positive; the proportion is carried by the plate, whose head_frac is 0.370
     by the founder's own 2026-08-21 ruling, and not by a word the negative is
     simultaneously suppressing.
  3. BEAT 07 NO LONGER NEGATES THE FIGURE ITS BAR REQUIRES. The shared negative
     lists `second face, second goblin, two goblins, crowd`; the same module's
     bar clause C2 requires TWO figures on beat 07 for the whole clip. b07 gets a
     negative with those four terms struck. A prompt cannot summon what its own
     negative removes.
  4. THE HOLD-FILL ARITHMETIC CLOSES. The sibling computes trim_to 97 and
     hold_fill 16 for a 121-frame slot: 97 + 16 = 113, eight frames short. Hold
     fill is `slot - trim_to` here, so the numbers reach the slot.

WHAT IS NOT FIXED, ON PURPOSE, AND IS PRE-REGISTERED INSTEAD. The action clauses
are the sibling lane's, verbatim, including the two places they argue with their
own init frame (b02 asks a figure already in frame to run INTO frame; b07 asks for
a guard that is in no canon plate). Rewriting another lane's stage directions to
make a prediction come true is how a wave stops being evidence. They are filed as
written and named in `failure_predicted_in_advance`.

NOTHING IS SWAPPED. No cut is touched, no pick is recorded. `success` on every
one of these seven ends at "a candidate"; the swap is the founder's word.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec                                    # noqa: E402
import derive_jerry_canon_motion_0821 as D            # noqa: E402
import jerry_canon_0821 as C                          # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b20-tilemotion-s2-0821.yaml"
PARENT_ID = "ep2-b20-tilemotion-s2-0821"
OWNER = "canon-motion filer/judge lane, 2026-08-21"
BY = "pipeline/file_jerry_canon_motion_0821.py"

RENDER_FRAMES = D.RENDER_FRAMES          # 105 = 8*13+1, legal for LTX's 8n+1 gate
TRIM_MARGIN = D.TRIM_MARGIN
FPS = D.FPS

# ── THE PLATE BINDING. round token -> the beats it is the newest round for.
# w2b is w2 plus two second-figure terms in the PLATE negative, on the three
# beats where a second figure can intrude. Both digests below were read off the
# repo copy AND off C:\banyan-farm\courier-box\farm-out on the box; they match.
PLATES = {
# BEAT 02 IS w2 AND THAT IS A DECISION, NOT AN OMISSION. b02 has a w2b spec and
# a DONE heartbeat on the box, but the pivot lane's own report reads "b02's
# re-roll was worse, so b02 keeps w2" -- the seed re-roll that cleared background
# goblins on 07 and 08 cost more than it bought here. Beats 07 and 08 have no
# usable w2 at all; w2b is their only landed round.
    2:  ("w2",  "b33a3b2fddee4603c95cd86bedb8df62df51378d44804e9d6b12c567e3637e57"),
    3:  ("w2",  "b937a6fe7a5f542ec6c0cd1de0645c8a7dfe59b39bf6d6cbe2c4b5cefbcf7b85"),
    4:  ("w2",  "98e20fd2f39bd5afdcc62b5945fda1b1c03167d7420a2ae76ffcab5dae280816"),
    7:  ("w2b", "d6a27d2686eef97e161da6ec6154b4639ebc2409d4fdb91568efa74b0ab97c87"),
    8:  ("w2b", "b4b41077abca121394815d8277e7eb44d936426358ae8c292c72e5288f6f1748"),
    13: ("w2",  "740d9d1b77f50a9b21e2dd49c7cefd5b9d7ebce74eaf8fca8cf5c72e2246f4f6"),
    20: ("w2",  "8575b7e55c5b73e263d1a6bcfc684a6435865376e528500ac7859ba09d427535"),
}

BOX_PLATE = (r"C:\banyan-farm\courier-box\farm-out\ep2-b%02d-canon-%s-0821"
             r"\ep2-b%02d-canon-%s-0821-ipahead.png")

# ── ONE SEED A BEAT, and the number says which beat so a stray file is traceable.
SEEDS = {b: 20260900 + b for b in D.SLOTS}

# ── ORDER OF INFORMATION, not of beat number. Priority sorts ASCENDING in
# box_autofill.py (`key=lambda p: (p[1].get("priority", 100), p[0])`), so the
# lowest number is fed to the card first.
#   b13 first  -- jerry_canon_0821.SAMPLE_BEAT, the frame the founder pointed at.
#   b08 second -- the only beat where BOTH old seeds egged at the same frame
#                 (f055). If the frame count moves anything, it moves here.
PRIORITY = {13: 20, 8: 21, 2: 22, 3: 23, 4: 24, 7: 25, 20: 26}

# ── THE INIT'S OWN STATE, in the plate's own words (jerry_canon_0821.WAVE_POSES,
# verbatim). A motion prompt that describes a pose the init does not hold is
# arguing with its own first frame.
STAGING = {b: C.WAVE_POSES[b] for b in D.SLOTS}

# ── THE MIDPOINT CLAUSE. The parent's prompt shape puts a HALFWAY THROUGH
# sentence last and it is the one clause that measurably moved a frozen clip, so
# it is kept as a shape and written per beat off the beat's own done_when.
HALFWAY = {
    2:  "he is mid-skid, still upright, leaning back, not yet down",
    3:  "he is all the way down behind the trunk and still, eyes turned to one side",
    4:  "he is leaned out sideways at full extension, looking, not yet back",
    7:  "the guard's arm is up and level, pointing at him, and he is leaning away",
    8:  "his chin is already down and his eyes are on his own belly",
    13: "his shoulders are down and his head has begun to tip sideways",
    20: "his head is up off the fruit, the fruit still closed in both hands",
}

# ── IDENTITY. The sibling's clause with `child` struck -- see defect 2 -- and
# nothing else moved.
IDENTITY_ONE = (
    "Subject already in frame: ONE small green goblin alone, bald, large "
    "pointed ears, off-white eyes with narrow vertical slit pupils, "
    "mandarin-collar sage shirt, dark shorts, dark boots. His face, ears, skin "
    "colour and clothes DO NOT CHANGE for the whole clip.")

# Beat 07 only. BOTH figures are placed before anything is asked of either, which
# is the sibling's point 2, and the goblin is named first so the adapter's subject
# is the one the plate holds.
IDENTITY_TWO = (
    "Subject already in frame: TWO figures, both present in the very first frame "
    "and in every frame after it. ONE small green goblin, bald, large pointed "
    "ears, off-white eyes with narrow vertical slit pupils, mandarin-collar sage "
    "shirt, dark shorts, dark boots, standing at the left. ONE TALL ARMOURED "
    "CITY GUARD in a helmet, standing at the right, facing the goblin, a full "
    "head taller. Both faces, both costumes and the goblin's skin colour DO NOT "
    "CHANGE for the whole clip.")

# ── THE NEGATIVE. The sibling's, and for b07 the four second-figure terms are
# struck because its own bar clause C2 requires the second figure -- defect 3.
B07_STRIKE = ("second face, ", "second goblin, ", "two goblins, ", "crowd, ")


def negative_for(beat: int) -> str:
    neg = D.NEGATIVE
    if beat != 7:
        return neg
    for term in B07_STRIKE:
        neg = neg.replace(term, "")
    return neg + ", only one figure, solo, empty background, missing guard"


def identity_for(beat: int) -> str:
    return IDENTITY_TWO if beat == 7 else IDENTITY_ONE


def prompt_for(beat: int) -> str:
    _, action, done_when = D.SLOTS[beat]
    # "He" is unambiguous on six beats; on 07 there are two figures in the
    # sentence before it, so the goblin is named rather than pronouned.
    subject = "The goblin is" if beat == 7 else "He is"
    return ("%s, anime key art. %s %s %s. THE ACTION: %s -- %s. "
            "HALFWAY THROUGH %s."
            % (D.MOTION_STYLE, identity_for(beat), subject, STAGING[beat],
               action, done_when, HALFWAY[beat]))


def plan_row(beat: int) -> dict:
    slot, action, done_when = D.SLOTS[beat]
    rnd, sha = PLATES[beat]
    trim_to = min(RENDER_FRAMES - TRIM_MARGIN, slot)
    return {
        "beat": beat,
        "new_id": "ep2-b%02d-canonmotion-0821" % beat,
        "slot_frames": slot,
        "slot_s": round(slot / float(FPS), 3),
        "render_frames": RENDER_FRAMES,
        "trim_to": trim_to,
        # DEFECT 4: slot - trim_to, so 97 + 24 reaches 121 rather than 113.
        "hold_fill_frames": max(0, slot - trim_to),
        "plate_round": rnd,
        "plate_sha256": sha,
        "plate_box_path": BOX_PLATE % (beat, rnd, beat, rnd),
        "seed": SEEDS[beat],
        "priority": PRIORITY[beat],
        "action": action,
        "done_when": done_when,
        "figures": 2 if beat == 7 else 1,
        "prompt_chars": len(prompt_for(beat)),
    }


def plan() -> list:
    return [plan_row(b) for b in sorted(D.SLOTS, key=lambda x: PRIORITY[x])]


# ── The two sentences that are this beat's alone, written per beat so no two of
# ── the seven carry the same question. derive_spec refuses a verbatim re-use.
def why_for(row: dict) -> str:
    b = row["beat"]
    return (
        "MOTION FOR BEAT %02d ON THE FOUNDER-IMAGE CANON PLATE, round %s, filed "
        "as INFORMATION while the plate sheet is unanswered.\n\n"
        "THE BEAT: %s. Done when %s.\n\n"
        "WHY %d FRAMES AND NOT 121. This beat's slot in the cut is %d frames "
        "(%.3f s), ffprobed off the clip review/ep2-ship-0821 is shipping right "
        "now, not read off the script's paper timing. The 14-clip wave that "
        "preceded this one rendered 121 frames on every clip and lost the face "
        "on six of them, at f055 three times, f065 once, ~f095 and f106 once "
        "each. IT THEREFORE HOLDS NO EVIDENCE ON WHETHER THAT ONSET MOVES WITH "
        "THE FRAME COUNT, because the frame count never moved. This job moves "
        "it, once, to %d. That is the whole question it asks.\n\n"
        "WHAT IS NOT BEING ASKED. Whether the plate reads as his goblin -- that "
        "is the founder's, it is on his board, and it is not answered by any "
        "number this job produces."
        % (b, row["plate_round"], row["action"], row["done_when"],
           row["render_frames"], row["slot_frames"], row["slot_s"],
           row["render_frames"]))


def consumer_for(row: dict) -> str:
    return (
        "A CANDIDATE for beat %02d of the canon patch wave, and evidence on the "
        "frame-count question for the other six. review/ep2-ship-0821 is NOT "
        "touched by this job and no clip is swapped by it: the swap is the "
        "founder's word on the plate sheet plus a separate judgement with its "
        "own bar." % row["beat"])


def success_for(row: dict) -> str:
    return (
        "ONE 704x1280 %d-frame 24fps mp4 at seed %d, init cover-cropped from "
        "the canon %s plate with sha256 %s asserted before a frame is written. "
        "Scored on M1/M2/W1/W2/A1/C1/C2 in `bar`, and the frame number at which "
        "the face-dissolve begins is RECORDED WHETHER OR NOT IT PASSES -- a "
        "clean clip's answer to the frame-count question is the number 'never', "
        "and that is a datum, not an absence."
        % (row["render_frames"], row["seed"], row["plate_round"],
           row["plate_sha256"][:16]))


def predicted_for(row: dict) -> str:
    b = row["beat"]
    common = (
        "THE PREDICTION THIS TRANCHE EXISTS TO TEST, and it is filed before the "
        "pixels. LTX has no IP-Adapter. Every canon plate was drawn by one, "
        "holding a face the base checkpoint does not otherwise produce, and LTX "
        "is handed that face as PIXELS in one init frame and asked to keep it "
        "against its own prior. So IDENTITY DRIFT, IF IT COMES, DRIFTS TOWARD "
        "LTX'S PRIOR -- a rounder, more human head -- and shows up LATE. The "
        "prior wave's version of this was the green egg: silhouette and colour "
        "kept, features simply not drawn.\n\n"
        "AND THE SHARPER PREDICTION, which is the one that pays. The onsets "
        "recorded at 121 frames were f055, f055, f055, f065, ~f095, f106. If "
        "the fault is PROPORTIONAL to the render, a 105-frame clip should lose "
        "the face near f048 and the shorter render buys nothing at all. If it "
        "is ABSOLUTE, it lands at f055 again and the shorter render still buys "
        "nothing. ONLY A CLIP THAT HOLDS PAST ITS TRIM POINT SUPPORTS THE "
        "PREMISE. Two of the three outcomes retire the frame-count idea and "
        "point at the LoRA (train-jerry-0820) as the only durable fix, because "
        "a LoRA moves the prior where an init frame only argues with it.\n\n"
        "THE STRUCTURAL RISK ACROSS THE WHOLE TRANCHE IS A FREEZE, AND IT IS "
        "NOT THE MODEL'S FAULT. A plate is posed at the beat's most legible "
        "instant, which is usually the beat's END: b08's plate is already "
        "`head bowed, looking down`, b13's is already `sitting`, b20's is "
        "already `looking up`. An i2v clip whose init already holds the "
        "finished pose has nowhere to travel, and this tree has shipped a still "
        "with a runtime before. If the passes here are frozen passes, the "
        "finding is that the patch wave needs START-STATE plates, which is a "
        "plate-side change and not a motion recipe at all.")
    per = {
        2: ("BEAT 02 SPECIFIC, AND IT IS AN INIT/ACTION CONFLICT I AM FILING "
            "RATHER THAN EDITING. The action clause says he runs INTO frame "
            "from the left and drops behind a thin sapling trunk. He is "
            "already in the init frame -- an init frame is frame zero, he "
            "cannot enter it -- and the canon b02 plate has NO sapling trunk "
            "in it, because the beat's own stage direction is that he has not "
            "seen the sapling yet. So the dive has nothing to dive behind and "
            "the model must invent it. Rewriting another lane's stage "
            "direction to make my own prediction come true is how a wave stops "
            "being evidence, so it is filed as written and this is the note."),
        3: ("BEAT 03 SPECIFIC. Its plate is already `squatting, hiding behind "
            "a thin trunk` and its action is to crouch and HOLD STILL. This is "
            "the beat most likely to return a technically-passing frozen clip, "
            "and the eye-flick is the only thing in it that moves. If the "
            "eyes do not flick, the pass is a still."),
        4: ("BEAT 04 SPECIFIC, AND IT IS THE ACTION, NOT THE FACE. The peek is "
            "out-look-back, and the pull-back is the joke. Two plate rounds "
            "failed to draw a lean, so the whole lean-and-return is being "
            "asked of the motion model from a plate that only hunches. If LTX "
            "will not produce a return from a standing init, the answer is a "
            "two-plate approach -- lean plate, return plate -- and not a third "
            "wording."),
        7: ("BEAT 07 SPECIFIC AND IT IS THE LIKELIEST FAILURE IN THE TRANCHE. "
            "Both old seeds drew NO GUARD and the beat was simply absent. The "
            "sibling's fix is to PLACE both figures in the wording, and that "
            "fix is applied here -- both figures are named before anything is "
            "asked of either, and the four second-figure terms that were in "
            "the shared negative are struck. BUT THE CANON b07 PLATE CONTAINS "
            "ONE FIGURE. i2v is being asked to introduce a character that is "
            "in none of its pixels, and the prompt-summons law cuts both ways: "
            "wording places a subject at TEXT-TO-IMAGE time, and this is not "
            "that. I expect no guard, and the value of the job is that it says "
            "so cheaply. The named next rung is a TWO-FIGURE PLATE, not a "
            "fourth wording."),
        8: ("BEAT 08 SPECIFIC AND IT IS THE SHARPEST TEST IN THE TRANCHE. This "
            "is the one beat where BOTH prior seeds lost the face at the SAME "
            "frame -- f055 twice -- which is what made it a recipe fault "
            "rather than seed luck. f055 sits INSIDE a 97-frame trim, so if "
            "the onset is absolute this clip eggs again and the frame-count "
            "premise dies here first. Its plate is also already `head bowed, "
            "looking down`, so the freeze risk above applies to it hardest."),
        13: ("BEAT 13 SPECIFIC. It is jerry_canon_0821.SAMPLE_BEAT and it runs "
             "first on purpose: it is the frame the founder pointed at when he "
             "said the goblin read as an adult, and the prior wave's s1 egged "
             "at f065 while its s2 held all 121 frames. A split like that "
             "means the draw is live here, so a single failure on this beat is "
             "NOT by itself evidence about the frame count."),
        20: ("BEAT 20 SPECIFIC. Its prior s2 is the only clip in the whole "
             "14-clip wave that closed a done_when -- the head rose from f055 "
             "and was up by f076 -- and it did that at 121 frames with the "
             "face intact throughout. THIS BEAT THEREFORE HAS THE MOST TO "
             "LOSE FROM A SHORTER RENDER: 105 frames is a change to a beat "
             "that was already working, and its plate is already `looking up`, "
             "so a freeze here would be a regression rather than a finding. "
             "It is filed last for that reason."),
    }
    return common + "\n\n" + per[b]


def trim_plan_for(row: dict) -> str:
    if row["hold_fill_frames"]:
        return (
            "RENDER %d, TRIM TO %d, HOLD THE LAST GOOD FRAME FOR %d MORE to "
            "reach this beat's %d-frame slot. The arithmetic closes: %d + %d = "
            "%d. The sibling module's own plan printed trim 97 with hold-fill "
            "16 for this slot, which is 113 and eight frames short, because it "
            "computed the fill from the RENDER length instead of from the trim "
            "point. NO STEP IN THIS JOB TRIMS OR FILLS ANYTHING -- ltx_i2v.py "
            "has no length flag and this is a note for whoever stages a swap, "
            "which happens in render_t3.fit_duration and only on the founder's "
            "word. `hold_fill: false` is the per-beat reverse."
            % (row["render_frames"], row["trim_to"], row["hold_fill_frames"],
               row["slot_frames"], row["trim_to"], row["hold_fill_frames"],
               row["trim_to"] + row["hold_fill_frames"]))
    return (
        "RENDER %d, TRIM TO %d, NO HOLD-FILL -- this beat's slot is %d frames "
        "and the render is %d longer, which is the trim margin and is discarded. "
        "No step in this job trims anything; ltx_i2v.py has no length flag. The "
        "trim belongs to whoever stages a swap, on the founder's word."
        % (row["render_frames"], row["trim_to"], row["slot_frames"],
           row["render_frames"] - row["trim_to"]))


def script_line_for(beat: int) -> str:
    """The beat's own stage direction, from jerry_canon_0821.WAVE, verbatim.

    WAVE[beat][3] is the node.md quotation the canon plate wave was authored
    against, so a motion spec and its plate cite one source rather than two.
    """
    return C.WAVE[beat][3]


def script_authority_for(beat: int) -> str:
    return (
        "Node 002b-first-citizen, live script `002b-t0-c`, `approved_by: "
        "founder`, `approved_on: 2026-08-03`. The line is untouched by this "
        "job. Beat %02d's staging is quoted in `script_line` from "
        "jerry_canon_0821.WAVE[%d], which is the same node text the canon "
        "plate under this clip was drawn against. NOTE ON PROVENANCE: this "
        "spec's parent is a BEAT 20 job and both of these keys cross "
        "derive_spec's allow-list as structure -- carried unedited they would "
        "have had beat %02d claiming beat 16's restaging as its authority, so "
        "they are re-stated here rather than inherited." % (beat, beat, beat))


def spec_for(row: dict) -> dict:
    b, new_id = row["beat"], row["new_id"]
    nn = "%02d" % b
    # Longest-first, and every pair chosen so it CANNOT match inside the parent
    # id "ep2-b20-tilemotion-s2-0821" -- derive_spec appends the id pair LAST, so
    # a loose "b20-" rule would eat the id before the id rule ever saw it. That
    # is exactly how the parent's own retoken left a stale bench filename behind.
    retoken = [
        ("bench-ep2-b20-peek-s3-0820", "bench-ep2-b%s-canonmotion-0821" % nn),
        ("20-evidence-LTX-", "%s-evidence-LTX-" % nn),
        ("b20-motion-prompt.txt", "b%s-motion-prompt.txt" % nn),
        ("b20-negative.txt", "b%s-negative.txt" % nn),
        ("b20-jobs-encode.json", "b%s-jobs-encode.json" % nn),
        ("b20-jobs-render.json", "b%s-jobs-render.json" % nn),
        ("b20-embeds.pt", "b%s-embeds.pt" % nn),
        ("b20-init-704x1280.png", "b%s-init-704x1280.png" % nn),
    ]
    overrides = {
        "seed": row["seed"],
        "argv:--src": row["plate_box_path"],
        "argv:--sha256": row["plate_sha256"],
        "argv:--frames": row["render_frames"],
        "key:beat": b,
        "key:priority": row["priority"],
        "key:est_minutes": 8,
        # script_authority and script_line are ALLOW-listed STRUCTURE, so they
        # cross the derivation untouched -- and the parent is a BEAT 20 spec
        # whose script_line quotes beat 16's node text. Carried unedited, all
        # seven of these would have claimed beat 16's staging as their own
        # authority. Both are re-stated per beat off the node's own words.
        "key:script_authority": script_authority_for(b),
        "key:script_line": script_line_for(b),
        "payload:b%s-motion-prompt.txt" % nn: prompt_for(b),
        "payload:b%s-negative.txt" % nn: negative_for(b),
    }
    extra = {
        "bar": D.BAR,
        "failure_predicted_in_advance": predicted_for(row),
        "identity_and_wardrobe_source": (
            "taste/refs/goblin-canon-founder-0821.png, the founder's own image, "
            "supplied 2026-08-21 with \"dude, this is how the goblin should "
            "look\". TWO THINGS THE OLDER BARS IN THIS TREE STILL SAY THAT THIS "
            "DESIGN CONTRADICTS, so they are not scored here: THERE IS NO TUSK "
            "-- the broken tusk and the patchwork cloak belong to the adult "
            "design the founder replaced, and a tusk arriving in motion is "
            "DRIFT, not a pass criterion. AND THE EYES ARE NOT BLANK -- canon's "
            "own plate negative strikes `blank eyes, no pupils`; the eye is an "
            "off-white sclera with a narrow dark vertical slit and no iris. A "
            "pale-green iris filling the eye is the w1 fault and it fails here."),
        "one_sample_rule": (
            "SATISFIED, AND NOT BY THE COUNT. Seven jobs is not one recipe "
            "scaled to seven: it is seven beats, each an independent question "
            "with its own init plate, its own action and its own slot, at one "
            "seed each. What IS scaled is the frame count, and it is scaled "
            "from a rung that has never been sampled at all -- which is the "
            "objection, and the answer to it is the order these are filed in. "
            "Beat 13 runs FIRST and alone in priority: it is the canon module's "
            "own SAMPLE_BEAT, and if 105 frames breaks it, the remaining six "
            "are cancellable before the card has spent twenty minutes."),
        "plate_provenance": (
            "farm-out/ep2-b%s-canon-%s-0821/ep2-b%s-canon-%s-0821-ipahead.png, "
            "832x1216, sha256 %s. Verified on BOTH sides before filing: the "
            "repo copy and C:\\banyan-farm\\courier-box\\farm-out on the box "
            "hash identically. cover_crop.py asserts that digest before it "
            "writes an init frame, so an edited or re-rendered plate stops this "
            "job rather than quietly animating a different character. Round %s "
            "is this beat's newest canon round; beats 02, 07 and 08 have a w2b "
            "round that is w2 plus `background characters` and `group` in the "
            "PLATE negative."
            % (nn, row["plate_round"], nn, row["plate_round"],
               row["plate_sha256"], row["plate_round"])),
        "post_ship_patch": (
            "review/ep2-ship-0821 IS NOT TOUCHED BY THIS JOB. Nothing in this "
            "spec writes into the cut, and the clip it produces is a candidate "
            "until the founder rules on the plate sheet."),
        "the_one_variable": (
            "THE FRAME COUNT, 121 -> %d, held identical across all seven jobs "
            "so the tranche answers one question seven times. The init plate, "
            "the action and the seed are per-beat by necessity -- they are what "
            "makes a beat a beat -- and everything the recipe consists of "
            "(size, fps, guidance, sampler, sigmas, two-stage, crf, offload) is "
            "the shipped b16 rung's, unchanged." % RENDER_FRAMES),
        "the_rung_this_is_one_variable_from": (
            "ep2-b16-motion-0820 by way of ep2-b20-tilemotion-s2-0821 -- the "
            "only motion recipe in this tree that shipped a goblin into the cut "
            "on its first sample. Size, guidance, sampler settings and prompt "
            "SHAPE are inherited unchanged. The frame count is what moves, and "
            "the plate underneath is a different character than that rung saw: "
            "the founder-image canon, not the B tile."),
        "trim_and_hold_plan": trim_plan_for(row),
    }
    return derive_spec.derive(
        PARENT, new_id,
        fresh={"why": why_for(row), "consumer": consumer_for(row),
               "success": success_for(row), "owner": OWNER},
        overrides=overrides, retoken=retoken, extra=extra, by=BY)


# ── The plate digests are asserted against the box BEFORE anything is written.
def verify_plates_on_box() -> list:
    lines, bad = [], []
    for row in plan():
        r = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=25", "-o", "BatchMode=yes", "rtx5090",
             'powershell -NoProfile -Command "(Get-FileHash \'%s\' '
             '-Algorithm SHA256).Hash.ToLower()"' % row["plate_box_path"]],
            capture_output=True, text=True)
        have = (r.stdout or "").strip().splitlines()
        have = have[-1].strip() if have else ""
        ok = have == row["plate_sha256"]
        lines.append("  beat %02d  %s  %s" % (row["beat"], "OK " if ok else "!! ",
                                              row["plate_box_path"]))
        if not ok:
            bad.append("beat %02d: want %s have %r"
                       % (row["beat"], row["plate_sha256"][:16], have[:16]))
    if bad:
        raise SystemExit("!! PLATE DIGEST MISMATCH ON THE BOX -- nothing written.\n"
                         + "\n".join("   " + b for b in bad))
    return lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing spec (derive_spec still refuses "
                         "to overwrite one that carries a verdict)")
    ap.add_argument("--verify-plates", action="store_true",
                    help="hash every init plate on the box and exit")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    if a.verify_plates:
        print("\n".join(verify_plates_on_box()))
        return 0
    rows = plan()
    if not a.write:
        print(json.dumps(rows, indent=2))
        print("\nnothing written. --write emits the seven yamls; filing them on "
              "the box is a separate box_enqueue.py --backlog call.")
        return 0

    print("verifying every init plate digest on the box first:")
    print("\n".join(verify_plates_on_box()))
    for row in rows:
        out = "pipeline/jobs/%s.yaml" % row["new_id"]
        path = derive_spec.write(spec_for(row), out, force=a.force)
        print("  beat %02d  p%-3d seed %d  render %d -> trim %d + hold %d = %d  "
              "plate %s  %s"
              % (row["beat"], row["priority"], row["seed"],
                 row["render_frames"], row["trim_to"], row["hold_fill_frames"],
                 row["trim_to"] + row["hold_fill_frames"], row["plate_round"],
                 os.path.relpath(path, REPO)))
    print("\nseven specs written. NOTHING IS ENQUEUED and no cut is touched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
