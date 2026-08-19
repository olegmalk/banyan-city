#!/usr/bin/env python3
r"""Derive pipeline/jobs/ep2-b12-noscav-0819.yaml -- ONE clause deleted, nothing else.

PARENT: pipeline/jobs/ep2-b12-stillmotion-s20260871-0819.yaml, the only one of
beat 12's five takes that is genuinely LOCKED AND FLAT: whole-frame drift -0.04
levels over 121 frames, camera +7px with all six blocks of the 3x2 grid agreeing
inside 1px. It fails on one thing and one thing only -- a black bird with a large
white eye rises from behind the lower leaf at f030 and is gone by f090.

THE DEFECT IS A PHRASE IN THE POSITIVE, AND IT IS MEASURED, NOT SUSPECTED.
Four of five independent seeds put a dark crouching figure behind the lower leaf,
in the same slot. The exception is 20260818, whose camera had left the plate by
f008 -- so of the takes that stayed on the plate, it is four of four. The plate
itself is clean: b12-init-704x1280.png is leaves, sun, cloud and sky with no dark
form anywhere. Byte-identical init across all five (c6575d0d...), so it is
invented at sample time by something identical on every seed. There is one
candidate, and it is in the positive:

    Tight on the sapling's two leaves, perfectly still -- THE SCAVENGER CROUCHED
    BEHIND THEM, OUT OF FRAME. Static locked framing, ...

A diffusion positive has no negation operator and no way to place a named
subject outside the canvas. "Out of frame" is not renderable; what that clause
actually encodes is *scavenger, crouched, behind the leaves* -- a subject and a
position -- and that is what got drawn. The negative's `goblin, creature, person,
face, hands, figure entering frame` fought it on every one of those renders and
lost, which is the standing law about negatives doing what positives place.

THIS IS NOT "DELETING TEXT THE SCRIPT DOES NOT CONTAIN". The first draft of this
argument said so and it was wrong: node.md:83 is the approved shot description
and it carries the clause almost verbatim -- "Tight on the sapling's two leaves,
perfectly still -- the scavenger is still crouched in the grass behind them, out
of frame." The prompt is a faithful transcription of an approved line.

WHAT MAKES THE DELETION RIGHT IS THE OTHER HALF OF THE SAME NODE. node.md:189
states the staging: "12 RELATED -- he is crouched in the grass behind the leaves
and out of frame, not below them. OFF-SCREEN ONLY; THE PICTURE DID NOT CHANGE."
Canon requires the scavenger to be absent from the picture. Four of five renders
put him in it. So the RENDER violates canon, and the deletion moves the output
TOWARD the approved staging rather than away from it.

  * NOT R4. It changes a prompt, not the script. What would be R4 is editing the
    line itself, or widening a framing he approved as "tight on two leaves".
  * The generalisable law, which outranks this beat: A SHOT DESCRIPTION IS NOT A
    PROMPT. Staging prose describes what is true of the SCENE, including what is
    deliberately off-screen -- normal, useful screenwriting. A diffusion positive
    can only describe WHAT IS IN THE FRAME. Whoever writes a prompt from a script
    line must strip every clause about what the camera does not see.

ONE VARIABLE. Same plate at the same sha, same seed 20260871, same negative word
for word, same 121 frames / 704x1280 / 24 fps / guidance 2.0 / --distilled-sigmas
/ --two-stage / --image-crf 10 / --offload sequential / --mode production. The
only change is the span `-- the scavenger crouched behind them, out of frame`
leaving the positive. NOTHING REPLACES IT: the shot is the two leaves, and
substituting a describing phrase would make this two variables.

$0 to derive. No model, no network, no GPU. ~8 min on the card, one sample.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import derive_spec  # noqa: E402

SRC = "pipeline/jobs/ep2-b12-stillmotion-s20260871-0819.yaml"
OUT = "pipeline/jobs/ep2-b12-noscav-0819.yaml"
NEW_ID = "ep2-b12-noscav-0819"
SEED = 20260871

DELETED_SPAN = " -- the scavenger crouched behind them, out of frame"

# The parent's positive with DELETED_SPAN removed and the sentence closed. Every
# other character, including the style tail, is the parent's.
PROMPT = (
    "Tight on the sapling's two leaves, perfectly still. Static locked framing, "
    "the frame never moves and nothing enters it. The leaves hold their shape "
    "and their position; only the grass stirs, very slightly, in the air. "
    "Detailed cinematic anime, warm amber backlight, hazy out-of-focus grassy "
    "field, soft glowing light, masterpiece, best quality, very aesthetic.")


def main() -> int:
    parent = derive_spec.load(os.path.join(derive_spec.REPO, SRC))
    old_prompt = [v for k, v in parent["payload"].items()
                  if k.endswith("b12-motion-prompt.txt")]
    if len(old_prompt) != 1:
        print("!! expected exactly one motion prompt in the parent")
        return 2
    if DELETED_SPAN not in old_prompt[0]:
        print("!! the span this rung exists to delete is not in the parent "
              "prompt -- refusing to file a rung whose premise is stale.")
        return 3
    # The deletion is the ONLY difference, proved rather than asserted.
    if old_prompt[0].replace(DELETED_SPAN, "") != PROMPT:
        print("!! PROMPT is not the parent's prompt minus the span. Diff:\n"
              "   want %r\n   have %r"
              % (old_prompt[0].replace(DELETED_SPAN, ""), PROMPT))
        return 4

    child = derive_spec.derive(
        src=SRC, new_id=NEW_ID, by="pipeline/derive_b12_noscav_0819.py",
        fresh={
            "owner": "beat 12 lane, 2026-08-19 -- derived by "
                     "pipeline/derive_b12_noscav_0819.py",
            "consumer": (
                "BEAT 12 IN THE EP2 CUT, and it is the beat's first shot at a take "
                "that fails NOTHING. The seed axis closed 0 for 5: every take failed "
                "at least one clause, and on four of the five the failure was the same "
                "one -- a crouching figure behind the lower leaf, on four independent "
                "seeds, in the same slot. Beat 12 ships today as best-available with a "
                "colour fault named, on a take carrying a different prompt and a "
                "different seed. This rung asks whether removing one unrenderable "
                "clause removes the figure and leaves the locked, flat clip that "
                "20260871 already produced. If it does, beat 12 has a candidate the "
                "assembler can swap in; if it does not, the cause is not the phrase "
                "and the beat needs a plate route instead."),
            "success": (
                "ONE 121-frame 704x1280 mp4 with its sidecar and the 704x1280 init it "
                "was conditioned on, published into courier-box with a .sha256 "
                "manifest. THE DECISIVE CLAUSE IS B1, NO FIGURE ANYWHERE: it is the "
                "one thing that separates this take from its parent, and a pass on "
                "everything else with a figure still in frame is a FAIL of this job. "
                "The bar below was written before the pixels existed."),
            "why": (
                "ONE VARIABLE off ep2-b12-stillmotion-s20260871-0819, and the variable "
                "is a span of text: `-- the scavenger crouched behind them, out of "
                "frame` leaves the positive and NOTHING REPLACES IT. A diffusion "
                "positive has no negation operator and no way to place a named subject "
                "outside the canvas, so that clause encodes a subject and a position "
                "and gets them drawn -- four of five seeds, four of four among the "
                "takes that stayed on the plate, against a negative that names goblin, "
                "creature, person, face, hands and figure entering frame. node.md:189 "
                "requires the scavenger OFF-SCREEN ONLY, 'the picture did not change', "
                "so the render is what violates canon and the deletion moves the output "
                "toward the approved staging. Not R4: this changes a prompt, not the "
                "script."),
        },
        overrides={
            "payload:b12-motion-prompt.txt": PROMPT,
            # A no-op in value and not in effect: it re-parses every
            # jobs-render.json and asserts the seed really reads 20260871, so
            # the derivation block cannot disagree with the payload the way the
            # parent generation's did.
            "seed": SEED,
        },
        retoken=[
            # THE DUPLICATE-FILENAME TRAP, closed in the generator where it
            # belongs. s20260818, s20260872 and s20260873 all published their
            # mp4 as `12-related-LTX-stillmotion-crf10-s20260818.mp4` -- three
            # distinct takes, one basename, three directories -- because the
            # take's identity lives in the job id and the filename carries only
            # the recipe and the seed. This take shares BOTH with its parent, so
            # an id-only retoken would have published a fourth collision.
            ("12-related-LTX-stillmotion-crf10-s20260871",
             "12-related-LTX-noscav-s20260871"),
            ("bench-b12-stillmotion", "bench-b12-noscav"),
        ],
        extra={
            "the_clause_deleted_and_the_canon_that_requires_it": {
                "deleted_span": DELETED_SPAN.strip(),
                "prompt_before": old_prompt[0],
                "prompt_after": PROMPT,
                "nothing_replaces_it": (
                    "Deliberate. The shot is the two leaves. Substituting a describing "
                    "phrase would make this two variables and would re-open the "
                    "question of what the substitute itself summons."),
                "the_approved_line_does_contain_it": (
                    "node.md:83, the approved shot description, reads \"Tight on the "
                    "sapling's two leaves, perfectly still -- the scavenger is still "
                    "crouched in the grass behind them, out of frame.\" The prompt is a "
                    "transcription of it. This rung is NOT 'deleting text the script "
                    "does not contain' -- that justification was drafted, checked, and "
                    "found false before filing."),
                "what_makes_the_deletion_right": (
                    "node.md:189, the staging half of the same node: \"12 RELATED -- he "
                    "is crouched in the grass behind the leaves and out of frame, not "
                    "below them. OFF-SCREEN ONLY; THE PICTURE DID NOT CHANGE.\" Canon "
                    "requires the scavenger absent from the picture; four of five "
                    "renders put him in it. The RENDER violates canon, and the deletion "
                    "moves the output toward the approved staging."),
                "the_law_that_outranks_this_beat": (
                    "A SHOT DESCRIPTION IS NOT A PROMPT. Staging prose describes what is "
                    "true of the scene, including what is deliberately off-screen -- "
                    "normal screenwriting. A diffusion positive can only describe what "
                    "is IN the frame. Transcribing an off-screen clause verbatim asks "
                    "for exactly the thing the script says to exclude."),
                "scope_named_honestly_and_NOT_claimed_as_audited": (
                    "315 specs match `out of frame`, and sampled, the overwhelming "
                    "majority are NEGATIVES banning subject exits -- `walking out of "
                    "frame, leaving the frame` -- a correct and unrelated use. The "
                    "defect is an off-screen clause inside a POSITIVE, and beat 12 is "
                    "the only confirmed instance. The audit that would settle it reads "
                    "positives only and HAS NOT BEEN RUN; a whole-file grep cannot tell "
                    "the two apart. Named as unowned, not claimed as measured."),
                "authority": (
                    "NOT R4. A prompt is not the script. What would be R4 is editing "
                    "node.md's line, or widening a framing he approved as 'tight on two "
                    "leaves'. Beat 12's line was approved by name on 2026-08-19 "
                    "(5d6eb792) and STEWARDSHIP.md 6 is discharged for this beat."),
            },
            "bar": {
                "written_before_the_pixels": (
                    "Every clause below is pre-registered. Instruments are named per "
                    "clause; numbers are FILTERS and the verdict is the read. All 121 "
                    "frames opened, not sampled -- the beat-07 lane's standard."),
                "B1_NO_FIGURE_ANYWHERE_AND_IT_IS_THE_DECISIVE_CLAUSE": (
                    "No scavenger, goblin, person, face, hand, limb or dark humanoid "
                    "form in ANY of the 121 frames, at any edge and behind either leaf. "
                    "This is the clause the rung exists for and it outranks every other "
                    "clause here: a take that passes B2-B5 with a figure in it is a "
                    "FAIL. Scored by opening every frame, with the region behind the "
                    "LOWER LEAF -- where four of four on-plate seeds put him, and where "
                    "20260871's bird rose at f030 -- looked at specifically. THE BIRD "
                    "COUNTS: the parent's only mover was a black bird with a large white "
                    "eye, and 'any figure' includes it. Reported as figure/bird/neither "
                    "so a partial result is legible instead of rounded."),
                "B2_EXACTLY_TWO_LEAVES_and_the_count_is_scored_AGAINST_THE_PLATE": (
                    "beats.'12'.done_when asks for exactly two cotyledons and one bare "
                    "side-branch. THE PLATE DOES NOT CARRY THAT AND NO i2v RENDER CAN "
                    "ADD IT, because the init is frame one. Measured on the plate "
                    "itself: four blade-sized components, major axes 619/772/607/591 px, "
                    "aspects 2.85/3.11/3.38 against composite-init-pattern.md 8's "
                    "pre-registered 1.6-2.6 band -- lance-shaped, and more than two. So "
                    "the clause here is the one this render CAN fail: THE COUNT MUST NOT "
                    "CHANGE across the 121 frames. No leaf appears, vanishes, wilts or "
                    "grows. The absolute count remains a PLATE FAULT with a named route "
                    "(the composite instrument that solved beats 15 and 19) and is not "
                    "charged to this take."),
                "B3_CAMERA_LOCKED": (
                    "Instrument: farm-out/ep2-b12-stillmotion-s20260818-0819/"
                    "b12_camera_drift.py -- phase correlation on native-resolution "
                    "BT.601 gray, cumulated, reported whole-frame AND per 3x2 block. "
                    "PASS = whole-frame |dy| and |dx| within the parent's own result "
                    "(+7px, all six blocks agreeing inside 1px). A real camera move is "
                    "region-consistent; field re-inking is not. THE INSTRUMENT'S OWN "
                    "LIMIT IS CARRIED: a hard fade or content substitution destroys the "
                    "correlation peak, so if B4 collapses, THE BLOCK NUMBERS ARE NOISE "
                    "and must not be quoted as a camera move (s20260873 read +133px per "
                    "block against a whole-frame +0px). Framing is a per-render check "
                    "and is never inherited from a passing sibling: 20260818 tilted "
                    "-387px with the ban in both the positive and the first six tokens "
                    "of the negative."),
                "B4_MATCHED_CONTENT_LUMA_WITHIN_BOUNDS": (
                    "Mean luma of the OVERLAP REGION ONLY -- f000 rows [s:] against fN "
                    "rows [:H-s] at the measured cumulative shift -- so a fade cannot "
                    "hide behind a pan and a pan cannot forge a fade. PASS = |matched "
                    "drift| f000->f120 under 20 levels, two-sided, plus the equal-thirds "
                    "band read from pipeline/luma_drift.py for the sign-disagreement "
                    "check. Bands disagreeing in sign is never scored as a collapse; a "
                    "single band moving alone is an OBJECT until eyes say otherwise. The "
                    "parent read -0.04 matched, and 20260819 on this same plate read "
                    "-91.05, so this axis is live even though the seed is the flat one: "
                    "the collapse is a (seed x plate) INTERACTION and the prompt is one "
                    "of the two things changing here."),
                "B5_FOUR_QUARTERS_MOTION_alive_but_not_moving": (
                    "'Perfectly still' does not mean 'a still'. Interframe median "
                    "reported for EACH QUARTER of the clip -- f000-030, f030-060, "
                    "f060-090, f090-120 -- and separately inside the leaf mask and the "
                    "grass band. PASS = the grass band is non-zero in ALL FOUR quarters "
                    "and the leaf band is near zero in all four. Quartered because the "
                    "parent's whole-clip grass figure was 0.011 while a bird crossed it, "
                    "i.e. a single number over 121 frames cannot tell 'alive throughout' "
                    "from 'one event in the middle of a dead clip'. Measured on regions, "
                    "not on the frame: a perfect 32px fall over a frozen background "
                    "moves whole-frame interframe by 0.056 and would fail a frame-level "
                    "floor."),
            },
            "pre_registered_fail_modes": {
                "FAIL-FIGURE-ANYWAY": (
                    "the crouching form returns with the clause gone. NAMED AS THE MOST "
                    "USEFUL NEGATIVE RESULT: it would move the cause off the phrase and "
                    "onto the plate or the checkpoint, and would retire prompt surgery "
                    "as beat 12's lever in one clip."),
                "FAIL-BIRD": (
                    "no scavenger, but the parent's black bird with the white eye rises "
                    "again. B1 counts it. Named separately from FAIL-FIGURE-ANYWAY "
                    "because they point at different causes -- the bird was never in any "
                    "prompt."),
                "FAIL-DEAD": (
                    "nothing moves, grass included. The parent already sat at 0.011 in "
                    "the grass band, so this beat is closer to dead than to busy and "
                    "deleting a subject clause can only reduce what there is to animate. "
                    "Named as MORE LIKELY THAN THE FIGURE RETURNING."),
                "FAIL-COLLAPSE": (
                    "matched-content luma drift 20 levels or more. This seed held at "
                    "-0.04 on this plate, but the collapse is a (seed x plate) "
                    "interaction and the prompt is not a proven-innocent third factor."),
                "FAIL-CAMERA": "a real, region-consistent move. Per-render, never inherited.",
                "FAIL-PLANT-CHANGE": "a leaf appears, vanishes, wilts or grows.",
                "reporting_rule": (
                    "every mode above is reported BY NAME whether or not it fired, and a "
                    "mode discovered after the fact is reported as unpredicted rather "
                    "than folded into the nearest pre-registered one -- the parent "
                    "generation's DUSK COLLAPSE is why that sentence is here."),
            },
            "failure_predicted_in_advance": (
                "FAIL-DEAD IS MORE LIKELY THAN THE FIGURE RETURNING, and saying so is "
                "what makes a clean pass worth something. The parent's grass band "
                "measured 0.011 -- effectively frozen -- and its ONLY mover was the bird "
                "this rung is trying to delete. Remove the one subject clause from a "
                "positive whose whole first sentence asks for stillness, on a recipe "
                "measured to over-deliver stillness (beat 18 went 5.956 -> 0.570 at crf "
                "10 and was scored FAIL-FROZEN), and the plausible outcome is a clip with "
                "nothing in it at all. That is why B5 quarters the motion instead of "
                "reporting one number: a dead clip and a locked clip differ only in the "
                "grass, and only if you look at the grass in every quarter."),
            "not_asked_by_this_rung": (
                "No pick, no promotion, no cut swap, and no plate route filed off this "
                "sample. THE PICK IS R4 AND NO BEAT-12 TAKE HAS EARNED ONE. Beat 12 keeps "
                "12-related-b12-tightB-untrimmed.mp4 as best-available with its colour "
                "fault named, whatever this returns. The absolute leaf count is a plate "
                "question and is not re-litigated here. The positives-only `out of frame` "
                "audit is named in this spec and is NOT owned by this job."),
            "init_provenance": (
                "genomes/sapling/nodes/002b-first-citizen/takes/stills/12-related-r4-s2.png, "
                "sha256 cc6bd5f0c0cc116d3cb6530a9bae81ac5b5593a683e4e80e20d6319e0cc0c074, "
                "read off the box from "
                "C:\\banyan-farm\\courier-box\\farm-out\\ep2-b12-plateship-0819\\ -- "
                "verified present at that exact sha by certutil on 2026-08-19 before this "
                "spec was written -- and re-asserted by cover_crop.py before a pixel is "
                "written. It is the SHIPPED beat-12 take's own init and the same file all "
                "five seed takes conditioned on (init byte-identical across all five, "
                "c6575d0d...), which is what licenses reading them as one plate. No fetch "
                "step and no network: this spec's grandparent had one, it 404'd, and the "
                "cure was a box-local copy under the same sha assertion (0f799ddd)."),
            "duration_and_the_assembler_trap": (
                "121 frames at 24 fps = 5.0417 s. render_t3's default fill for footage is "
                "now a last-frame HOLD (af863c0b) and the palindrome survives only as "
                "opt-in `loop_fill: pingpong`, which nothing in this tree writes -- but "
                "beat 12 is near-still, so a palindrome here would be nearly invisible, "
                "which is worse and not better. Whoever assembles should check beat 12's "
                "slot length against 5.0417 s rather than assume."),
        })

    # The deletion is the only change to either prompt file, checked on the
    # written child rather than on the plan.
    neg = [v for k, v in child["payload"].items() if k.endswith("b12-negative.txt")]
    parent_neg = [v for k, v in parent["payload"].items()
                  if k.endswith("b12-negative.txt")]
    assert neg == parent_neg, "the negative must be the parent's, word for word"
    pos = [v for k, v in child["payload"].items()
           if k.endswith("b12-motion-prompt.txt")][0]
    assert "scavenger" not in pos, "the span survived"
    assert pos == PROMPT

    out = derive_spec.write(child, OUT)
    print("parent   %s" % SRC)
    print("child    %s" % os.path.relpath(out, derive_spec.REPO))
    print("deleted  %r" % DELETED_SPAN.strip())
    print("seed     %d (re-parsed out of jobs-render.json)" % SEED)
    print("dropped  %s" % ", ".join(
        child["derivation"]["keys_the_parent_had_that_did_NOT_cross"]))
    print("steps    %s" % ", ".join(s["name"] for s in child["steps"]))
    print("rc=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
