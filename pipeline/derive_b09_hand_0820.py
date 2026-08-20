#!/usr/bin/env python3
r"""BEAT 09, THE POLISH: name the hand, four seeds, one clause.

THE ONE NAMED FAULT. `ep2-b09-cropmotion-0820` closed beat 09's framing axis and
passed four of four on its own bar -- the 2.157x LANCZOS crop ends at 105% of
frame 1's high-frequency energy, so FAIL-SOFT-COMPOUNDS did not fire, and cheek
luma, grass drift, sky corner, camera lock, face count and mouth all held. ONE
THING BROKE AND IT IS ONE OBJECT: the hand at his cheek. Full hand at f001,
fingers by f004, two fingers under the nose at f006, GONE BY f008. Hand box
(430,430,660,700) drifts 46.1 at the first pair; the parent's whole-frame figure
was 0.53. The ladder's reading -- "the init holds where it is sharp" -- makes
this the softest, most upscaled object in the frame paying for the upscale.

THE CLAUSE THIS RUNG ADDS, AND WHY IT IS THE OBVIOUS ONE NOBODY HAD SPENT.
READ THE PARENT'S POSITIVE: IT NEVER MENTIONS THE HAND. Not once. The prompt
describes hair, glasses, brows, eyes, head tilt, mouth, light -- and the hand
that is sitting on his cheek in the init is not in the text at all. This
ladder's most-measured law is that THE POSITIVE PLACES WHAT YOU WANT AND THE
NEGATIVE DOES NOT, and its companion is that a named noun gets DRAWN. An object
present in the init and absent from the conditioning has nothing holding it
through 121 frames of a model that is free to re-decide it. So the rung is not a
strength change, not a crf change and not a different crop: it is one sentence
that says where the hand is and what it is doing, in the concrete-placement
dialect that beat 04 rung 2 proved beats an abstract instruction (head travel
64.7 px -> 4.7 px off one clause moved out of an instruction and into a picture).

AND IT IS PHRASED AS AN ONGOING ACTION, not a static attitude. Measured
2026-08-20 across b03/b13/b15: an ongoing terminal placement held position with
no cost to the performance (b15, HOLD 0.508, no freeze); a static attitude
bought the hold by making every frame the last frame (b03, 33 dead frames; b13,
face-band interframe 10.80 -> 0.64). Beat 09's whole done_when is a face working
slowly through a thought, so a clause that freezes the clip to save the hand
would trade the beat for the prop. `his fingers rest against his cheek and stay
there, shifting a little as he thinks` keeps the hand present WITHOUT asking the
frame to stop.

NOTHING IS ADDED TO THE NEGATIVE. `melting`, `morphing` and `changing face` are
already in it and the hand dissolved anyway; this tree's negatives have failed
to hold position three for three, and adding `disappearing hand` would put the
phrase `disappearing hand` in the conditioning, which is the beat-15 trap --
`Nobody touches the plant` closed a fist on the plant. State what IS.

THE SEED SET IS DESIGNED, NOT ROUNDED UP. FOUR JOBS: h1 IS THE PARENT'S OWN SEED
20260819, so exactly one thing differs between it and a scored clip and the
comparison is a true one-variable read. h2-h4 walk, so if h1 holds the hand the
set immediately says whether that was the clause or the draw. The parent scored
0 of 1 on this object; 4 of 4 or 0 of 4 both mean something, and 1 of 4 means
the clause did not do it.

WHAT THIS DOES NOT DO. No cut swap and no promotion: beat 09 is a SLATE
(`slate_beats [9, 16]`), the adult/adolescent read is an open R4 card on
/review/ep2-guards-0818, and the parent pre-registered `is_show_content: false`
with its reason -- passing the bar you were given is not a licence to enter a
cut on a different bar. That reason is unchanged here and is carried forward
explicitly. THE OTHER NAMED ROUTE IS NOT TAKEN: the r2s2 crop (1.454x, 90% of
native) has a sharper hand and a SHUT EYE, which the ladder correctly calls a
trade rather than a fix. This rung keeps the eye and spends a sentence.

$0, ~7 min each, ~28 min for the set.

Run:  python3 pipeline/derive_b09_hand_0820.py [--write]
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b09-cropmotion-0820.yaml"

# The parent's positive with ONE sentence inserted. Every other byte is the
# parent's, in the parent's order.
PROMPT = (
    "2D anime, hand-drawn cel animation, static locked framing, the frame never "
    "moves, flat cel shading, clean ink linework, anime key art. Subject already "
    "in frame: ONE adult man alone, dark cropped hair, round wire-rim glasses on "
    "his face, standing in bright daylight with deep tall grass behind him. HIS "
    "HAND IS AT HIS FACE AND STAYS THERE: his fingers rest against his cheek "
    "with the thumb under his jaw, four fingers drawn whole against the skin, "
    "and they stay resting there the whole time, shifting a little against his "
    "cheek as he thinks. HIS FACE WORKS THROUGH A THOUGHT, SLOWLY: his brows "
    "draw together and then ease, his eyes shift and settle, his head tilts a "
    "few degrees. HIS MOUTH STAYS CLOSED the whole time -- he is thinking, not "
    "speaking, and no word is said. He stays THE SAME MAN from the first frame "
    "to the last: the same dark cropped hair, the same round wire-rim glasses, "
    "one face and one man only. The light on him is CONSTANT and does not "
    "flicker, pulse or strobe. Soft steady daylight, cinematic lighting, "
    "detailed, newest, masterpiece, best quality, very aesthetic."
)

BAR = """SCORED BY EYE AT 1:1 ON THE FIRST TEN FRAMES FIRST, because that is
where the parent died, and then across all 121.
  H1 THE HAND SURVIVES f008. A whole hand -- palm and four fingers readable
     against the cheek -- at f008, f030 and f120. This is the clause the rung
     exists for and it is the only one that can promote the rung.
  H2 THE HAND IS A HAND, not a mitten and not a fifth finger. A hand that
     survives by turning into a smudge is a FAIL and is named so it cannot be
     reported as a hold.
  H3 THE FACE STILL WORKS. Brows draw and ease, eyes shift and settle, the head
     tilts a few degrees. THE DEGENERATE PASS IS NAMED IN ADVANCE: a clip
     frozen hard enough to preserve the hand satisfies H1 perfectly and fails
     H3, and it is a FAIL. Beat 09's done_when is the face, not the prop.
  H4 THE PARENT'S PASSING CLAUSES ALL SURVIVE -- mouth closed for 121 frames,
     camera locked, one face, the same man at f121 as at f001, eyes open at the
     start and the end.
READ AS A SET AND NOT AS FOUR RESULTS. h1 carries the parent's own seed, so h1
against the parent is the one-variable read; h2-h4 say whether the answer is the
clause or the draw. 4/4 or 0/4 are both informative. 1/4 means the clause did
not do it and the honest next move is the r2s2 crop, with its shut eye priced in
as the trade the ladder already called it."""

PREDICTED = """I EXPECT THIS TO WORK, and I am saying so in advance so that a
win is not read as a surprise and a loss is not explained away. The parent's
positive does not contain the word hand; the object with the largest interframe
drift in the frame is the one object the conditioning never mentions; and the
placement law has now won on this engine four times, most recently converting a
64.7 px head rotation to 4.7 px off one reworded clause. If a named, placed hand
still dissolves at four seeds, that is a real finding about upscaled regions
under --image-crf 10 and it retires the wording route on this object.
THE FAILURE I ACTUALLY FEAR IS H3, THE FREEZE. Every placement win on this tree
that named a STATIC attitude bought it by killing the clip, and `stays there` is
one wrong word away from static. It is phrased as an ongoing action for exactly
that reason, and H3 is in the bar so the trade cannot be taken quietly.
SECOND: A SECOND HAND. Naming a hand summons a hand, and this frame has a body
that could grow one. The parent's negative already carries `two men` and `second
man` but nothing about hands, and nothing is being added to it -- if a second
hand arrives, THAT is the rung that earns a negative edit.
THIRD, AND UNLIKELY: the extra sentence displaces conditioning the face was
using and H3 degrades without freezing. The positive grows by one sentence out
of eight, so this is a small risk, but it is the reason the rung adds a sentence
rather than rewriting the face clauses to make room."""

# h1 is the PARENT'S OWN SEED on purpose: one variable against a scored clip.
SEEDS = [("h1", 20260819), ("h2", 20260851), ("h3", 20260852), ("h4", 20260853)]


def main() -> int:
    write = "--write" in sys.argv
    for tag, seed in SEEDS:
        new_id = "ep2-b09-hand-%s-0820" % tag
        parent_seed = (seed == 20260819)
        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "beat-09 polish lane, 2026-08-20 night",
                "consumer": (
                    "BEAT 09'S SLATE IN THE EPISODE 2 CUT -- one of the two "
                    "remaining empty slots, and the beat carrying the episode's "
                    "punchline. Its framing axis is closed and its parent "
                    "passed four of four; the single thing standing between "
                    "that clip and a cuttable take is a hand that dissolves by "
                    "f008. This is seed %d of the four-job set that tests the "
                    "one clause nobody had spent. NO PROMOTION follows a pass "
                    "here on its own: the adult/adolescent read is still an "
                    "open R4 card and this clip inherits the plate's cast frame "
                    "for frame." % seed),
                "success": (
                    "One 704x1280 121-frame mp4 at seed %d IN WHICH THE HAND IS "
                    "STILL A WHOLE HAND AT f008. Judged by eye at 1:1, first on "
                    "frames 1-10 where the parent died and then across all 121: "
                    "H1 palm and four fingers readable against the cheek at "
                    "f008, f030 and f120; H2 it is a HAND and not a smudge or a "
                    "mitten; H3 the face still works through the thought -- "
                    "brows, eyes, a few degrees of head tilt -- because a clip "
                    "frozen hard enough to keep the hand satisfies H1 and FAILS "
                    "this beat; H4 the parent's passing clauses all survive "
                    "(mouth closed, camera locked, one face, same man, eyes "
                    "open at start and end).%s"
                    % (seed,
                       " THIS JOB CARRIES THE PARENT'S OWN SEED, so it is the "
                       "one-variable read against a scored clip: everything but "
                       "the hand sentence is byte-identical to a run whose hand "
                       "was gone by f008."
                       if parent_seed else
                       " The seed is walked off the parent's, so this job is "
                       "what says whether a win at the parent's seed was the "
                       "clause or the draw.")),
                "why": (
                    "$0, ~7 minutes, one sentence, and it is the cheapest "
                    "unspent lever on the last two slates. The parent's "
                    "positive NEVER MENTIONS THE HAND -- the object with the "
                    "largest interframe drift in the frame (46.1 at the first "
                    "pair against 0.53 whole-frame on its own parent) is the "
                    "one object the conditioning does not name. The named-and-"
                    "not-fired rung in the ladder was 're-run this init with "
                    "the dissolution as the single pre-registered clause'; this "
                    "is that, with the clause placed in the positive instead of "
                    "only pre-registered in the bar. Seed %d of four." % seed),
            },
            overrides={
                "seed": seed,
                "payload:b09-motion-prompt.txt": PROMPT,
                "key:est_minutes": 7,
            },
            retoken=[],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "pre_registered_fail_modes": (
                    "H-FREEZE the clip holds the hand by holding everything; H1 "
                    "passes, H3 fails, and it is a FAIL. H-SMUDGE the hand "
                    "survives as a shape that is not a hand -- a mitten, three "
                    "fingers, a blur -- which reads as a hold on any metric and "
                    "not at 1:1. H-SECONDHAND naming a hand summons one and a "
                    "second arrives somewhere in frame; nothing was added to the "
                    "negative, so this is the fail mode that would earn a "
                    "negative edit rather than one being pre-spent. H-FACE-COST "
                    "the added sentence displaces conditioning the face clauses "
                    "were using and the thought stops reading, without a freeze. "
                    "H-LATE the hand survives f008 and goes later; that is "
                    "PROGRESS and not a pass, and the frame it goes at is the "
                    "number the next rung would be aimed with."),
                "the_one_variable": (
                    "ONE SENTENCE INSERTED INTO THE POSITIVE, naming the hand "
                    "and placing it. Every other byte of the positive is the "
                    "parent's, in the parent's order. THE NEGATIVE IS UNTOUCHED "
                    "byte for byte -- it already carries melting, morphing and "
                    "changing face and the hand dissolved anyway, and adding "
                    "'disappearing hand' would put that phrase in the "
                    "conditioning, which is the beat-15 trap. Init, crop, sha, "
                    "size, frames, fps, guidance, sigmas, two-stage, offload "
                    "and --image-crf 10 are the parent's. Across the four jobs "
                    "the prompt bytes are identical and only the seed moves; "
                    "h1's seed is the PARENT'S, which is what makes the set a "
                    "controlled comparison rather than four fresh draws."),
                "why_it_is_phrased_as_an_ongoing_action": (
                    "Measured 2026-08-20 on b03/b13/b15: a terminal placement "
                    "naming an ONGOING action held position at no cost to the "
                    "performance (b15, HOLD 0.508, no freeze), while one naming "
                    "a STATIC attitude bought the hold by making every frame "
                    "the last frame (b03, 33 dead frames from f088; b13, "
                    "face-band interframe 10.80 -> 0.64). Beat 09's done_when "
                    "IS the performance -- 'Guard 1's face works through it, "
                    "slowly' -- so a static hand clause would trade the beat "
                    "for the prop. Hence 'shifting a little against his cheek "
                    "as he thinks' rather than 'his hand does not move'."),
                "init_provenance": (
                    "The parent's, unchanged: "
                    "farm-out/ep2-b09-platecrop-0820/"
                    "09-the-pause-platecrop-r1s3.png, sha256 ba72dec8...da7d, "
                    "cover-cropped to 704x1280 by the same step with the same "
                    "assertion. This is the crop that closed beat 09's framing "
                    "axis -- 2.157x LANCZOS, 45% of a native close-up's "
                    "high-frequency energy at frame 1 and 105% of frame 1 by "
                    "f121. The r2s2 crop (1.454x, 90% of native) is the OTHER "
                    "named route and is deliberately not taken: its hand is "
                    "sharper and its eye is shut, which is a trade and not a "
                    "fix."),
                "is_show_content": False,
                "is_show_content_why": (
                    "CARRIED FORWARD FROM THE PARENT AND STILL TRUE. Beat 09 is "
                    "a slate (`slate_beats [9, 16]`) and stays one. This clip "
                    "inherits the plate's cast frame for frame and the "
                    "adult/adolescent read is an open R4 card on "
                    "/review/ep2-guards-0818. Passing the bar you were given is "
                    "not a licence to enter a cut on a different bar. NO PICK, "
                    "NO plate_ack, NO promotion, whatever the hand does."),
                "not_done_on_purpose": (
                    "No crop change. No crf change. No strength, guidance or "
                    "sigma change. No negative edit. No second init. No new "
                    "plate. No cut swap. The r2s2 route is left unfired on "
                    "purpose so that if this fails, there is still an unspent "
                    "lever with a known cost rather than a second wording."),
            },
            by="pipeline/derive_b09_hand_0820.py",
        )
        out = os.path.join(REPO, "pipeline", "jobs", new_id + ".yaml")
        if write:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(derive_spec._dump(child))
        print("%-26s seed %-9d %s%s" % (new_id, seed,
                                        "written" if write else "(dry)",
                                        "   <- parent's seed" if parent_seed else ""))
    if not write:
        print("\n-- dry run. re-run with --write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
