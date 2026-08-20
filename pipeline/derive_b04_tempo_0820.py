#!/usr/bin/env python3
r"""BEAT 04, THE TEMPO RUNG: the peek batch's own named follow-up.

WHAT THE BATCH SETTLED. `ep2-b04-peek-s1..s5-0820` established that this engine
PLAYS the founder's picked action -- it does not refuse it. On four of five he
takes his head off axis and brings it back. What it does not do is fit two trips
into 121 frames: s1, s2 and s4 give ONE out-and-back and then settle, and only
s3 starts a second. (s5 looked like the winner and was a camera pan; top-corner
mean abs luma 49.4 and 52.2 against f001 where s3 reads 1.72 and 0.93.)

So the defect is TEMPO, not action, and the batch pre-registered exactly this:
"One clean trip that is still moving at f121 is a PARTIAL and the follow-up is a
TEMPO WORD, not a restage."

THE ONE VARIABLE, AND WHY IT IS AN ADJECTIVE AND NOT A NUMBER. The obvious
wording is "twice" or "three times", and this repo has already paid to learn
that numerals do not bind on this stack: cardinality is Class A in
pipeline/composite-init-pattern.md -- CLIP's numeral embeddings are near
identical, the strongest available count wording returned 0 of 16 frames with
two leaves, and the same study found that HEIGHT, a CONTINUOUS ADJECTIVE, bound
3 of 4 in the same batch. Counting the trips is the lever that is measured not
to work. Making each trip FASTER is a continuous adjective, and a shorter trip
is how two of them fit in five seconds. So the clause changes from a lean that
"repeats" to one that is QUICK, SHARP and NERVOUS, and the count is left to
follow from the speed instead of being asked for.

EVERYTHING ELSE IS s3'S, BYTE FOR BYTE: the init and its sha, the crop, size,
frames, fps, guidance, sigmas, two-stage, --image-crf 10, and the negative --
which still has `drifting sideways` and `moving to a different spot` deleted and
nothing added, exactly as the peek batch left it.

t1 CARRIES s3'S OWN SEED (20260822) so the tempo clause is the only difference
from the best clip in the batch and the comparison is one variable. t2 and t3
walk, so a win at t1 can be told apart from a lucky draw.

AND THE CAMERA CHECK IS NOW PART OF THE BAR, because s5 taught it: the two TOP
corner patches, mean abs luma against f001. Under ~3 the camera is locked. s5
would have been picked by eye and was a pan; no clip from this rung is judged
without that number.

$0, ~7 min each, ~21 min for the set.

Run:  python3 pipeline/derive_b04_tempo_0820.py [--write]
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b04-peek-s3-0820.yaml"

# s3's positive with the action block's TEMPO changed and nothing else.
PROMPT = (
    "2D anime, hand-drawn cel animation, static locked framing, the frame never "
    "moves, flat cel shading, clean ink linework, anime key art. Subject already "
    "in frame: ONE lean wiry adult goblin man alone, green skin, bald head, "
    "long pointed ears, patchwork cloak, crouched low in deep tall grass in "
    "bright daylight, seen close on his face and shoulders. HE SNAPS OUT AND "
    "SNAPS STRAIGHT BACK, QUICK AND NERVOUS: he flicks his head and one "
    "shoulder out past the tall grass blades that cross in front of him in one "
    "fast movement, takes the look in an instant, and whips straight back in "
    "behind the blades -- a short sharp trip, over almost as soon as it starts, "
    "and he is already going out again. HALFWAY THROUGH he is snapping back in "
    "behind the blades at speed, his head already turning the other way. AT THE "
    "END he is "
    "mid-flick, caught partway out, the movement unfinished and carrying on "
    "past the last frame. HIS MOUTH STAYS SHUT the whole time and his jaw stays "
    "set -- he is looking, not speaking, and no word is said. He stays down low "
    "with his knees under him in the grass. He stays THE SAME GOBLIN from the "
    "first frame to the last: the same green skin, the same bald head, the same "
    "long pointed ears, one face and one figure only. The light on him is "
    "CONSTANT and does not flicker, pulse or strobe. Soft steady daylight, "
    "cinematic lighting, detailed, newest, masterpiece, best quality, very "
    "aesthetic."
)

BAR = """JUDGED BY EYE AT 1:1, AND THE CAMERA NUMBER IS READ BEFORE ANY OTHER
CLAUSE, because s5 taught this batch that the best-looking clip can be a pan.
  T0 CAMERA LOCKED -- mean abs luma of the TWO TOP corner patches against f001,
     under ~3. s3 read 1.72 / 1.46 / 0.93 / 2.14; s5 read 49.4 / 5.4 / 52.2 /
     7.7 and is a FAIL. Bottom corners are his cloak on this plate and say
     nothing. A clip that fails T0 is not scored further.
  T1 TWO TRIPS. His head goes off axis and returns, and then does it again.
     This is what the rung is for and it is the only clause that can promote it.
  T2 STILL GOING AT f121 -- visible travel inside the last twenty frames.
  T3 IT IS STILL A PERFORMANCE, not a vibration. `quick`, `snap`, `whip` and
     `blur` are speed words and the named risk is that they buy speed by
     shaking; a head that jitters in place is a FAIL and is not two trips.
  T4 MOUTH SHUT for 121 frames, one figure, no melt, the same goblin at f121 as
     at f001.
NOT SCORED: which goblin design is on the plate. The init is the superseded
adult man, as it was for the whole peek batch."""

PREDICTED = """T3 IS THE RISK I AM BUYING. Every speed word in the positive is
also a word for small fast motion, and the cheapest way for a video model to
look fast is to jitter. If the set comes back shaking rather than travelling,
the tempo axis is closed the way the eye axis was, and the honest next move is
the card's option C -- the slow sink -- which was argued as the grossest motion
available and the most likely to simply work.
SECOND: NO CHANGE AT ALL. `quick` may be too weak a signal against 121 frames of
a model that has already shown it likes one slow arc, in which case three of
three look like s1 and the axis is closed by a different door.
THIRD, AND THE ONE I WOULD ACTUALLY TAKE: ONE FAST TRIP AND THEN A SETTLE. That
is a partial and it means the speed bound but the repeat did not, and the next
lever is the END placement rather than the tempo -- `already going out again`
is doing that work here and could be made the last clause instead of the middle
one.
WHAT I AM NOT DOING is asking for a number. `twice` and `three times` are the
obvious words and cardinality is measured not to bind on this stack (0 of 16
frames at the strongest count wording), while a continuous adjective bound 3 of
4 in the same study. Spending a rung on a numeral would be re-running an
experiment this repo has already paid for."""

SEEDS = [("t1", 20260822), ("t2", 20260861), ("t3", 20260862)]


def main() -> int:
    write = "--write" in sys.argv
    for tag, seed in SEEDS:
        new_id = "ep2-b04-tempo-%s-0820" % tag
        parent_seed = (seed == 20260822)
        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "beat-04 restage lane, 2026-08-20 night (the tempo rung)",
                "consumer": (
                    "BEAT 04'S SLOT IN THE EPISODE 2 CUT. The peek batch settled "
                    "that this engine plays the founder's picked action and "
                    "settled what is still wrong with it: three of four clips "
                    "fit ONE out-and-back into 121 frames where the card asked "
                    "for two. This is the batch's own named follow-up, seed %d "
                    "of three. It is not a restage and not a new action -- the "
                    "pick stands and only the speed of the trip changes."
                    % seed),
                "success": (
                    "One 704x1280 121-frame mp4 at seed %d with TWO trips in it. "
                    "The camera number is read first: mean abs luma of the two "
                    "TOP corner patches against f001, under ~3, because the "
                    "peek batch's best-looking clip was a pan at 49.4 and 52.2 "
                    "and would have been picked by eye. Then T1 two out-and-back "
                    "trips; T2 visible travel inside the last twenty frames; T3 "
                    "it is travel and not a jitter -- a head vibrating in place "
                    "is a FAIL and is not two trips; T4 mouth shut, one figure, "
                    "no melt, same goblin at f121.%s"
                    % (seed,
                       " THIS JOB CARRIES s3'S OWN SEED, so the tempo clause is "
                       "the only difference from the best clip in the peek "
                       "batch."
                       if parent_seed else
                       " The seed is walked off s3's so a win at t1 can be told "
                       "apart from a lucky draw.")),
                "why": (
                    "$0, ~7 minutes, one clause, and it is the rung the peek "
                    "batch named in advance -- 'the follow-up is a TEMPO WORD, "
                    "not a restage'. The card was idle with no runnable job on "
                    "it and this is the best-argued work available: a completed "
                    "batch, a single diagnosed defect, a one-variable change on "
                    "a recipe that has now run clean eight times. Seed %d of "
                    "three." % seed),
            },
            overrides={
                "seed": seed,
                "payload:b04-motion-prompt.txt": PROMPT,
                "key:est_minutes": 7,
            },
            retoken=[],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "pre_registered_fail_modes": (
                    "T-JITTER the speed words buy a vibrating head instead of a "
                    "faster trip; the likeliest, and it closes the tempo axis. "
                    "T-NOCHANGE `quick` is too weak and all three look like s1's "
                    "single slow arc. T-ONETRIP one fast trip then a settle -- a "
                    "partial, meaning speed bound and repeat did not, and the "
                    "next lever is the END placement rather than the tempo. "
                    "T-PAN the camera moves, as it did on s5; T0 exists so this "
                    "cannot be mistaken for travel. T-SMEAR speed words pull "
                    "smeared frames even though `motion blur` is in the "
                    "negative; a first draft of this positive said `his head a "
                    "blur of movement` and that phrase was REMOVED before "
                    "filing rather than shipped and explained -- a positive "
                    "that contradicts its own negative is not a controlled "
                    "variable, which is the peek batch's own lesson one rung "
                    "earlier."),
                "the_one_variable": (
                    "THE TEMPO OF THE ACTION CLAUSE. s3's positive asked for a "
                    "lean that 'repeats'; this asks for one that is QUICK, SHARP "
                    "and NERVOUS and lets the count follow from the speed. The "
                    "middle and end placements are kept and re-pointed at the "
                    "faster motion. Identity, camera, mouth, crouch and quality "
                    "clauses are s3's byte for byte. THE NEGATIVE IS UNTOUCHED, "
                    "still with `drifting sideways` and `moving to a different "
                    "spot` deleted and nothing added, exactly as the peek batch "
                    "left it. Init, sha, crop, size, frames, fps, guidance, "
                    "sigmas, two-stage and --image-crf 10 are s3's. Across the "
                    "three jobs only the seed differs, and t1's is s3's."),
                "why_an_adjective_and_not_a_number": (
                    "Because the number is measured not to bind. Cardinality is "
                    "Class A in pipeline/composite-init-pattern.md -- no "
                    "continuous encoding, CLIP's numeral embeddings near "
                    "identical, and this repo's own frames put the strongest "
                    "available count wording at 0 of 16. The SAME study found a "
                    "continuous adjective (height) binding 3 of 4 in the same "
                    "batch. `twice` is the obvious word and spending a rung on "
                    "it would re-run an experiment already paid for; a shorter "
                    "trip is how two of them fit in five seconds."),
                "init_provenance": (
                    "s3's, unchanged, which is rung 1's and rung 2's: "
                    "farm-out/ep2-b04-mac-plate-0819/"
                    "04-the-footnote-mac-plate-r1s1.png, sha256 5dd35da5...4350, "
                    "cover-cropped to 704x1280 by the same step with the same "
                    "assertion."),
                "the_design_note_up_front": (
                    "THE INIT IS THE SUPERSEDED ADULT MAN, as it was for the "
                    "whole peek batch. The founder ruled on 2026-08-20 that the "
                    "goblin must read as the B tile's CREATURE; beat 04 is on "
                    "the re-render list for it and this rung does not address "
                    "it. The question here is tempo, which is a fact about the "
                    "engine and separable from which face is on the plate. Not "
                    "a plate pick."),
                "not_done_on_purpose": (
                    "No new action -- the founder's pick stands and this is a "
                    "tempo adjustment inside it. No numeral. No negative edit. "
                    "No crop, crf, guidance or sigma change. No goblin-design "
                    "change. No cut swap: beat 04 still ships b04-refire-0814 "
                    "as best-available with its fault named, and no clip from "
                    "the peek batch was picked either."),
            },
            by="pipeline/derive_b04_tempo_0820.py",
        )
        out = os.path.join(REPO, "pipeline", "jobs", new_id + ".yaml")
        if write:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(derive_spec._dump(child))
        print("%-27s seed %-9d %s%s" % (new_id, seed,
                                        "written" if write else "(dry)",
                                        "   <- s3's seed" if parent_seed else ""))
    if not write:
        print("\n-- dry run. re-run with --write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
