#!/usr/bin/env python3
r"""BEAT 04, THE RESTAGE: action A -- THE PEEK -- five seeds on the crf-10 recipe.

THE PICK. `/review/ep2-b04-action-0820` offered three replacement actions for a
beat the engine has now refused from both directions, and the founder picked
**A -- THE PEEK** on 2026-08-20 (relayed to this lane by the coordinator the
same night). The card's own words for A, verbatim:

    "The scavenger leans out from behind the trunk to look, and pulls straight
     back the moment he has looked -- the whole head and shoulder make the
     trip, twice, and he is still doing it when the shot ends."

and its scoring line, also verbatim: "his head crosses the trunk's edge and
returns, at least twice, with motion in the last twenty frames."

WHY THE WORD `trunk` IS NOT IN THE PROMPT, and this is the placement law and
not a liberty. THIS BEAT'S PLATE HAS NO TRUNK IN IT. `04-the-footnote-mac-plate-
r1s1.png` is a close crop on his face and shoulders in deep grass, with tall
blades crossing the foreground -- the trunk belongs to beat 03. Naming a noun
this engine cannot see in the init is how a noun gets DRAWN mid-clip (the
prompt-summons law), and the beat 15 rung paid for the sharper version of the
same rule this week: state only what IS in the shot, never what is absent, and
not even inside the positive -- `Nobody touches the plant` put a hand on the
plant. So the cover he leans out from is THE COVER THE PLATE ACTUALLY SHOWS:
the tall grass blades already in front of him. Same action, same joke, same
score (head crosses the edge of the cover and returns); one fewer invented
object.

THE THREE PLACEMENT CLAUSES, which is the whole wording change:
  * ONGOING, not a static attitude -- "again and again ... the same trip
    repeated". Measured on 2026-08-20 across b03/b13/b15: a terminal placement
    naming an ONGOING action held position at no cost to the performance
    (b15, HOLD 0.508, no freeze), while one naming a STATIC ATTITUDE bought
    the hold by killing the clip (b03, 33 dead frames; b13, face-band 10.80 ->
    0.64).
  * MIDDLE placement -- "HALFWAY THROUGH he is out past the blades mid-look".
  * END placement -- "AT THE END he is still leaning out and pulling back,
    mid-trip". This is the card's "and he is still doing it when the shot ends"
    and it is also what makes the last-twenty-frames clause scorable.

WHY A BATCH OF FIVE AND NOT ONE SAMPLE. The one-sample rule is one sample per
RECIPE CHANGE, and this changes no recipe: init, size, frames, fps, guidance,
sigmas, two-stage, offload and `--image-crf 10` are rung 1's byte for byte, and
that recipe has now run clean three times (eyes-crf10, headlock, tightcrop).
What varies across the five jobs is THE SEED ONLY -- proven-recipe seed clones,
the sanctioned batch shape in episode-loop-v2 step 2 ("i2v from the picked
plate, 4-8 seeds in one batch, pick by eye"). The prompt is byte-identical in
all five, so the batch answers one question -- does this engine perform the
peek -- instead of five.

THE ONE VARIABLE vs rung 1, and its one forced consequence. The variable is the
ACTION CLAUSE. The consequence is that rung 1's negative CONTAINS THE PICKED
ACTION: `drifting sideways` and `moving to a different spot` forbid, in as many
words, the sideways travel A asks for. Those two phrases are DELETED and
nothing is added; every other phrase in that negative is byte for byte,
including the whole camera block (pan, tilt, dolly, zoom, push in, pull back)
because the camera must still not move, and including `walking out of frame`,
`leaving the frame`, `standing up` and `sitting down`, because the restage asks
for none of those. A spec whose negative forbids its own positive is not a
controlled variable, it is a contradiction.

THE DESIGN CAVEAT, NAMED UP FRONT. The init is the ADULT-MAN goblin -- the
design the founder ruled canon on 08-19 and then partly superseded on 08-20
("the goblin must read as the B tile's CREATURE, not an adult man"). Beat 04 is
on the re-render list for that ruling and this batch does NOT address it. THE
QUESTION HERE IS MOTION AND STAGING, and it is separable: whether this engine
will play a repeated lean-out on a locked camera is a fact about the engine, not
about which face is on the plate. When the creature plate lands, this prompt
moves onto it unchanged. Do not read a pass here as a plate pick.

$0, ~7 min each, ~35 min for the set. No download, no new weights.

Run:  python3 pipeline/derive_b04_peek_0820.py [--write]
"""

from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b04-eyes-crf10-0819.yaml"

# The plate, and the sha the crop step asserts. Checked against the working
# tree below -- derive_fetch_guard.assert_fetch_urls_resolve does not apply
# here (this family reads the plate off the box's own courier-box mirror, not
# over a raw.githubusercontent URL, and that guard REFUSES a spec with no URL),
# so the equivalent check is done by hand against the same bytes.
PLATE_REPO_PATH = "farm-out/ep2-b04-mac-plate-0819/04-the-footnote-mac-plate-r1s1.png"
PLATE_SHA = "5dd35da532612e5d85c15ef3353068bf1e44675f8ddfc73c316ac2f654d4e350"

# Rung 1's positive. Everything outside the action block is byte-identical;
# the action block is action A, placed at the middle and at the end.
PROMPT = (
    "2D anime, hand-drawn cel animation, static locked framing, the frame never "
    "moves, flat cel shading, clean ink linework, anime key art. Subject already "
    "in frame: ONE lean wiry adult goblin man alone, green skin, bald head, "
    "long pointed ears, patchwork cloak, crouched low in deep tall grass in "
    "bright daylight, seen close on his face and shoulders. HE LEANS OUT AND "
    "PULLS STRAIGHT BACK, AGAIN AND AGAIN: he tips his head and one shoulder "
    "together out past the tall grass blades that cross in front of him, looks, "
    "then pulls straight back in behind the blades the same way he came, and "
    "leans out again -- his head and shoulder travel as one piece and the same "
    "trip repeats. HALFWAY THROUGH he is out past the blades mid-look, his head "
    "and shoulder clear of the grass and already tipping back. AT THE END he is "
    "still leaning out and pulling back, mid-trip, the movement unfinished and "
    "carrying on past the last frame. HIS MOUTH STAYS SHUT the whole time and "
    "his jaw stays set -- he is looking, not speaking, and no word is said. He "
    "stays down low with his knees under him in the grass. He stays THE SAME "
    "GOBLIN from the first frame to the last: the same green skin, the same "
    "bald head, the same long pointed ears, one face and one figure only. The "
    "light on him is CONSTANT and does not flicker, pulse or strobe. Soft "
    "steady daylight, cinematic lighting, detailed, newest, masterpiece, best "
    "quality, very aesthetic."
)

# Rung 1's negative with exactly two phrases deleted and nothing added.
NEGATIVE = (
    "open mouth, talking, speaking, shouting, teeth, tongue, lip sync, "
    "second face, second goblin, two goblins, 2boys, crowd, child, chibi, "
    "baby, girl, round head, big eyes, cute, different face, changing face, "
    "face changing, morphing, melting face, skin colour change, human skin, "
    "pale skin, hair, wig, glasses, flickering light, strobe, strobing, "
    "pulsing light, flashing light, blinking glow, camera pan, camera tilt, "
    "panning, tilting, camera movement, dolly, zoom, push in, pull back, "
    "tripod, camera, camera equipment, film equipment, walking out of frame, "
    "leaving the frame, standing up, sitting down, scene change, shot change, "
    "new camera angle, different location, photorealistic, 3D render, CGI, "
    "live action, motion blur, text"
)

SCRIPT_LINE = (
    'Beat 04 THE FOOTNOTE (0:16-0:22), node.md verbatim: "The scavenger holds '
    'his breath, eyes darting." RESTAGED 2026-08-20 by founder pick A off '
    '/review/ep2-b04-action-0820, THE PEEK: "The scavenger leans out from '
    'behind the trunk to look, and pulls straight back the moment he has '
    'looked -- the whole head and shoulder make the trip, twice, and he is '
    'still doing it when the shot ends." The VO line is UNCHANGED and is not '
    're-recorded: "Worst stealth plan I have ever seen -- and I once watched '
    'an architect hide an outage in a footnote."'
)

SCRIPT_AUTHORITY = (
    "Node 002b-first-citizen, live script `002b-t0-c`, `approved_by: founder`, "
    "`approved_on: 2026-08-03`, read from "
    "genomes/sapling/nodes/002b-first-citizen/leaves/002b-t0-c.yaml -- the leaf "
    "the render gate itself reads. The ACTION is restaged under the founder's "
    "2026-08-20 pick on /review/ep2-b04-action-0820, which is a stage "
    "direction and not a script change: the VO line is untouched, so the "
    "approved leaf still governs. (Rung 1 and rung 2 both carried a "
    "script_line naming BEAT 09 THE PAUSE, inherited from a beat-09 parent and "
    "never corrected; it is corrected here.)"
)

BAR = """SCORED BY EYE FIRST, at 1:1, against the card's own scoring line --
"his head crosses the trunk's edge and returns, at least twice, with motion in
the last twenty frames", read against THE COVER THIS PLATE HAS (the tall grass
blades in the foreground) rather than a trunk that is not in it.
  P1 THE TRIP HAPPENS TWICE. His head and shoulder travel out past the grass
     and come back, and then do it again. Once is a lean, not a peek, and is
     a partial at best.
  P2 STILL GOING AT f121. There is visible travel inside the last twenty
     frames. A clip that completes the second trip and then sits is the beat's
     old failure wearing a new action.
  P3 MOUTH SHUT for all 121 frames. Rung 1 and rung 2 both held this and
     losing it would mean the action bought its motion out of the face.
  P4 CAMERA LOCKED. The lean must be HIM moving, not the frame moving. This is
     the fail mode with the most room to hide: a pan reads as a lean at a
     glance and does not at 1:1 against the grass in the corners.
  P5 SAME FIGURE at f121 as at f001 -- green, bald, long-eared, one face, one
     body, no drift to a second goblin and no melt.
FROZEN IS A FAIL and is named so it cannot be claimed: this beat has now been
failed once from each direction and a clip that simply holds still satisfies
nothing.
NOT SCORED HERE: which goblin design is on the plate. The init is the
superseded adult man; beat 04 is on the 08-19 re-render list and that is a
different job."""

PREDICTED = """P4, THE CAMERA, IS THE ONE I EXPECT TO FIGHT. Every previous
rung on this beat asked the subject to move LESS, so the camera block in the
negative was never under load; this is the first that asks for lateral travel,
and the cheapest way for a video model to produce lateral travel is to move the
frame. The negative's camera phrases stay in for exactly this reason, and if a
pan comes back anyway the next rung is a positive placement of the background
(the grass in the corners does not move), not a longer negative -- this
ladder's negatives have failed to hold position three for three.
SECOND MOST LIKELY: P1 AT ONE TRIP. 121 frames at 24 fps is 5 seconds and two
full out-and-back trips is a brisk tempo; the engine may give one slow lean. One
clean trip that is still moving at f121 is a PARTIAL and the follow-up is a
tempo word, not a restage.
THIRD: THE SUPPRESSED LEAN. If the deletion of `drifting sideways` and `moving
to a different spot` turns out not to have been enough and he stays put, the
suspicion falls on `walking out of frame` / `leaving the frame`, which a lean
past the frame's cover could be read as touching. That is a one-phrase rung and
it is named here rather than discovered later.
IF ALL FIVE SEEDS FAIL THE SAME WAY, that is two batch rounds' worth of
evidence against action A on this engine, and per episode-loop-v2 step 3 the
answer is the card's option C (the slow sink -- one scalar, grossest motion,
already argued as the most likely to simply work), NOT a sixth wording."""

SEEDS = [20260820, 20260821, 20260822, 20260823, 20260824]


def check_plate() -> None:
    path = os.path.join(REPO, PLATE_REPO_PATH)
    if not os.path.isfile(path):
        raise SystemExit("!! plate missing from the working tree: %s"
                         % PLATE_REPO_PATH)
    with open(path, "rb") as fh:
        have = hashlib.sha256(fh.read()).hexdigest()
    if have != PLATE_SHA:
        raise SystemExit("!! plate sha mismatch\n   want %s\n   have %s"
                         % (PLATE_SHA, have))
    print("plate OK  %s  %s" % (PLATE_SHA[:12], PLATE_REPO_PATH))


def main() -> int:
    write = "--write" in sys.argv
    check_plate()
    for i, seed in enumerate(SEEDS, start=1):
        new_id = "ep2-b04-peek-s%d-0820" % i
        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "beat-04 restage lane, 2026-08-20 night",
                "consumer": (
                    "BEAT 04'S SLOT IN THE EPISODE 2 CUT, which currently "
                    "carries b04-refire-0814 as best-available with its fault "
                    "named (the same iris in the same sockets from f005 to "
                    "f096). Two rungs closed the wording route from opposite "
                    "sides, the founder picked a NEW ACTION off "
                    "/review/ep2-b04-action-0820 on 2026-08-20 -- A, THE PEEK "
                    "-- and this is seed %d of five on it. The set is judged "
                    "as one contact sheet and at most one clip is picked; the "
                    "other four are evidence about the engine and nothing "
                    "else." % i),
                "success": (
                    "One 704x1280 121-frame mp4 at seed %d in which HE LEANS "
                    "OUT PAST THE GRASS AND PULLS BACK, TWICE, AND IS STILL "
                    "DOING IT AT THE LAST FRAME. Judged by eye at 1:1, not by "
                    "a metric: P1 two out-and-back trips; P2 visible travel "
                    "inside the last twenty frames; P3 mouth shut for all 121 "
                    "frames; P4 the CAMERA does not move -- the lean is him, "
                    "not the frame, checked against the grass in the corners; "
                    "P5 the same figure at f121 as at f001. A frozen clip is a "
                    "FAIL, and so is a clip whose lean turns out to be a pan."
                    % seed),
                "why": (
                    "$0, ~7 minutes, no download, and it is the first job the "
                    "founder's action pick makes legal -- the card said in as "
                    "many words that nothing was to be rendered until he chose, "
                    "and that a rung is filed off the pick the same day. Seed "
                    "%d of five: the recipe is unchanged from a family that has "
                    "run clean three times, so five seeds cost 35 GPU-minutes "
                    "and answer whether this engine will play the action at "
                    "all, which one seed cannot." % seed),
            },
            overrides={
                "seed": seed,
                "payload:b04-motion-prompt.txt": PROMPT,
                "payload:b04-negative.txt": NEGATIVE,
                "key:est_minutes": 7,
                "key:script_line": SCRIPT_LINE,
                "key:script_authority": SCRIPT_AUTHORITY,
            },
            retoken=[],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "pre_registered_fail_modes": (
                    "P1 ONE TRIP INSTEAD OF TWO (partial, tempo rung). P2 THE "
                    "SECOND TRIP COMPLETES AND THE CLIP THEN SITS -- fails the "
                    "last-twenty clause and is the old defect in new clothes. "
                    "P3 the mouth opens because the body is finally allowed to "
                    "move. P4 A CAMERA PAN WEARING THE LEAN'S CLOTHES, the "
                    "likeliest and the easiest to mis-pass at a glance. P5 "
                    "identity drift or a second goblin during the travel, which "
                    "is where drift has lived in every i2v result in this tree. "
                    "P6 THE LEAN IS SUPPRESSED ENTIRELY and he holds still, "
                    "which would point at the remaining motion phrases in the "
                    "negative rather than at the action."),
                "the_one_variable": (
                    "THE ACTION CLAUSE, and its one forced consequence in the "
                    "negative. The positive's stillness block ('HIS HEAD DOES "
                    "NOT MOVE ... ONLY HIS PUPILS MOVE', rung 2) is replaced by "
                    "action A placed at the middle and at the end as an ongoing "
                    "action; every other sentence is rung 1's byte for byte. "
                    "The negative has exactly two phrases DELETED -- 'drifting "
                    "sideways' and 'moving to a different spot' -- because they "
                    "forbid the picked action in as many words; nothing is "
                    "added to it, the camera block is untouched, and 'walking "
                    "out of frame', 'leaving the frame', 'standing up' and "
                    "'sitting down' all stay. Init, size, frames, fps, "
                    "guidance, sigmas, two-stage, offload and --image-crf 10 "
                    "are rung 1's. Across the five jobs THE SEED IS THE ONLY "
                    "DIFFERENCE; the prompt bytes are identical in all five."),
                "the_placement_law_as_applied": (
                    "Three clauses, each one a measured finding rather than a "
                    "preference. ONGOING not static: 2026-08-20, b03/b13/b15 -- "
                    "a terminal placement naming an ongoing action held "
                    "position at no cost (b15, HOLD 0.508, no freeze) while a "
                    "static attitude bought the hold by killing the clip (b03, "
                    "33 dead frames from f088; b13, face-band 10.80 -> 0.64). "
                    "MIDDLE AND END both placed, so the second trip is asked "
                    "for where it has to happen. NO UNPOSITIONED NOUN: the "
                    "card's word 'trunk' is NOT in the prompt because there is "
                    "no trunk in this plate -- it is beat 03's -- and naming a "
                    "noun the init does not contain is how this engine draws "
                    "one. The cover he leans out from is the tall grass already "
                    "crossing the foreground, which is what the plate shows."),
                "init_provenance": (
                    "Rung 1's and rung 2's, unchanged: "
                    "farm-out/ep2-b04-mac-plate-0819/"
                    "04-the-footnote-mac-plate-r1s1.png, sha256 5dd35da5...4350, "
                    "asserted by the crop step and re-checked against the "
                    "working tree by this deriver before the spec was written. "
                    "The mac plate PASSED its own screening and both the plate "
                    "and refs guards run with no plate_ack."),
                "the_design_note_up_front": (
                    "THE INIT IS THE SUPERSEDED ADULT MAN. The founder ruled on "
                    "2026-08-20 that the goblin must read as the B tile's "
                    "CREATURE and that 'adult' in canon was drift; beat 04 is "
                    "on the re-render list for it. This batch does NOT address "
                    "that and must not be read as a plate pick. Motion and "
                    "staging are separable from which face is on the plate -- "
                    "whether this engine will play a repeated lean-out on a "
                    "locked camera is a fact about the engine. When the "
                    "creature plate lands, this prompt moves onto it unchanged, "
                    "which is the point of asking the question now instead of "
                    "queueing behind it."),
                "one_sample_rule": (
                    "SATISFIED BY THE RECIPE, and the argument is made rather "
                    "than pointed at. The rule is one sample per RECIPE CHANGE. "
                    "No recipe changes here: the crf-10 family has run clean "
                    "three times on this exact plate (eyes-crf10, headlock, "
                    "tightcrop) and every generative flag is inherited. What "
                    "varies is the seed, which is the sanctioned batch shape in "
                    "episode-loop-v2 step 2 -- 'i2v from the picked plate, 4-8 "
                    "seeds in one batch, pick by eye'. The ACTION is new, and "
                    "the founder has already looked at it: he picked it off a "
                    "card that showed him both failures on frames."),
                "not_done_on_purpose": (
                    "No crop change -- the tighter crop was already measured as "
                    "a lever on this beat and came back almost absent, and "
                    "changing framing in the same job would leave two candidate "
                    "causes. No crf change. No guidance or sigma change. No "
                    "second plate. NO GOBLIN-DESIGN CHANGE: that is the peer "
                    "lanes' question tonight and this lane stays off it. "
                    "node.md and done-definitions.yaml are NOT edited by this "
                    "script -- the pick is recorded in script_line here, and "
                    "the script edit is a separate change with its own diff."),
            },
            by="pipeline/derive_b04_peek_0820.py",
        )
        out = os.path.join(REPO, "pipeline", "jobs", new_id + ".yaml")
        if write:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(derive_spec._dump(child))
        print("%-28s seed %d  %s" % (new_id, seed,
                                     "written" if write else "(dry)"))
    if not write:
        print("\n-- dry run. re-run with --write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
