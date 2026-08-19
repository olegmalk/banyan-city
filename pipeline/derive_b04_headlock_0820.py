#!/usr/bin/env python3
r"""Beat 04, rung 2: lock the head POSITIVELY. One variable.

Rung 1 (ep2-b04-eyes-crf10-0819) failed beat 04 in one specific way: the gaze
shifted by a HEAD ROTATION (head-band centroid travelled 64.7 px) where
`done_when` says "only the eyes carry it". Everything else passed -- the
ratified adult held for all 121 frames, the mouth stayed shut, the camera stayed
locked.

WHY POSITIVELY AND NOT IN THE NEGATIVE. Rung 1's positive already contained
"His head and shoulders stay STILL" and the head turned anyway. This ladder's
own law, four times over on other beats, is THE POSITIVE PLACES WHAT YOU WANT
AND THE NEGATIVE DOES NOT -- so the rung is not "add `head turn` to the
negative", it is to say the thing wanted CONCRETELY and in the place that works:
where the head is pointing, and what the pupils do instead. "Stay still" is an
instruction; "chin square to camera, pupils sliding to the far corner of his
eyes" is a picture. Rung 1's own next_rung entry named these as two rungs and
put this one first; the negative-side rung is only fired if this fails.

ONE VARIABLE. Everything else -- init, seed, size, frames, fps, guidance,
sigmas, two-stage, offload, --image-crf 10 and the entire negative -- is rung
1's, byte for byte. The negative is deliberately NOT touched in the same job, so
a change in the head has exactly one candidate cause.

$0, ~7 min. Run:  python3 pipeline/derive_b04_headlock_0820.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b04-eyes-crf10-0819.yaml"
NEW_ID = "ep2-b04-headlock-0820"

# Rung 1's positive with ONE clause rewritten. Unchanged text is byte-identical.
PROMPT = (
    "2D anime, hand-drawn cel animation, static locked framing, the frame never "
    "moves, flat cel shading, clean ink linework, anime key art. Subject already "
    "in frame: ONE lean wiry adult goblin man alone, green skin, bald head, "
    "long pointed ears, patchwork cloak, crouched low in deep tall grass in "
    "bright daylight, seen close on his face and shoulders. HIS HEAD DOES NOT "
    "MOVE: his chin stays square to the camera and his skull is locked in place "
    "as if held, the same three-quarter angle in every frame. ONLY HIS PUPILS "
    "MOVE -- they slide to the far corner of his eyes, hold there, then slide "
    "back across to the other corner, the whites of his eyes showing on the "
    "side he looks away from. HIS MOUTH STAYS SHUT the whole time and his jaw "
    "stays set -- he is listening for something, not speaking, and no word is "
    "said. He stays THE SAME GOBLIN from the first frame to the last: the same "
    "green skin, the same bald head, the same long pointed ears, one face and "
    "one figure only. The light on him is CONSTANT and does not flicker, pulse "
    "or strobe. Soft steady daylight, cinematic lighting, detailed, newest, "
    "masterpiece, best quality, very aesthetic."
)

child = derive_spec.derive(
    src=PARENT,
    new_id=NEW_ID,
    fresh={
        "owner": "enactment lane, 2026-08-20 (beat 04, rung 2)",
        "consumer": (
            "Beat 04's slot in the episode 2 cut, which rung 1 could not fill. "
            "Rung 1 established that the adult survives animation and that the "
            "camera and mouth hold; the single thing standing between this beat "
            "and a cuttable take is whether the eyes can move WITHOUT the head. "
            "This answers that, and its answer decides between a wording route "
            "and a staging route -- there is no third wording after it."
        ),
        "success": (
            "One 704x1280 121-frame mp4 in which the HEAD IS STILL and the EYES "
            "MOVE. The instrument is fixed before the render and is rung 1's, so "
            "the two numbers are comparable: head-band ink centroid over rows "
            "100-520, which travelled 64.7 px in rung 1. PASS needs H1 head "
            "travel UNDER 20 px -- a third of rung 1's, chosen because below "
            "that a rotation stops reading as a turn at this crop; H2 the "
            "eye-band mean interframe difference AT OR ABOVE rung 1's 0.356, so "
            "the eyes have not simply been frozen along with the head; H3 the "
            "gaze visibly reaches a different place at 1:1, judged by eye and "
            "not by H2 alone; and H4 rung 1's passing clauses all survive -- "
            "mouth shut, camera locked, and the same adult goblin at frame 121 "
            "as at frame 1. THE OBVIOUS DEGENERATE PASS IS NAMED SO IT CANNOT BE "
            "CLAIMED: a totally frozen clip satisfies H1 perfectly and fails H2 "
            "and H3, and is a FAIL."
        ),
        "why": (
            "$0, ~7 minutes, one variable, on a recipe that has now run clean "
            "twice. The card was idle and this rung was already named in rung "
            "1's own verdict, so it is filed rather than left for someone to "
            "re-derive."
        ),
    },
    overrides={
        "payload:b04-motion-prompt.txt": PROMPT,
        "key:est_minutes": 7,
    },
    retoken=[],
    extra={
        "the_one_variable": (
            "The positive's head clause, and nothing else. Rung 1 said 'His head "
            "and shoulders stay STILL' inside the eye sentence; this says where "
            "the head is pointing and what the pupils do instead. THE NEGATIVE "
            "IS UNTOUCHED, byte for byte, on purpose: adding 'head turn' to it "
            "in the same job would leave two candidate causes for any "
            "improvement. Init, seed, and every generative flag are rung 1's."
        ),
        "bar": {
            "h1_head_still": (
                "Head-band ink centroid travel under 20 px, same instrument and "
                "same rows as rung 1's 64.7 px."
            ),
            "h2_eyes_not_frozen_too": (
                "Eye-band mean interframe at or above rung 1's 0.356. This "
                "clause exists because H1 alone is trivially satisfied by a dead "
                "clip."
            ),
            "h3_the_gaze_arrives": (
                "At 1:1 the gaze visibly reaches a different place than it "
                "started. Eye call, and it outranks H2 if they disagree."
            ),
            "h4_rung_1_clauses_hold": (
                "Mouth shut, camera locked, same adult goblin at frame 121 as at "
                "frame 1. All three passed in rung 1 and losing one would mean "
                "the head clause bought its win somewhere else."
            ),
        },
        "pre_registered_fail_modes": (
            "G1 THE HEAD TURNS ANYWAY -- most likely, because rung 1's positive "
            "already asked for stillness in weaker words and this engine moved "
            "the head regardless; if it fires, wording is closed on this axis "
            "and the next move is staging, not a third sentence. G2 FROZEN -- "
            "the head lock takes the whole clip with it, H1 passes and H2/H3 "
            "fail; this is a FAIL and is named so it cannot be reported as a "
            "win. G3 the pupils render as a hard flat shape and read as a "
            "different character. G4 'the whites of his eyes showing' comes back "
            "as all-white eyes with no pupil at all, which the b08 lane already "
            "saw once under a different mechanism."
        ),
        "failure_predicted_in_advance": (
            "G1. Rung 1 asked for a still head in plain words and got a 64.7 px "
            "rotation. The bet here is only that a CONCRETE placement beats an "
            "abstract instruction, which is this ladder's own repeatedly "
            "measured law -- but it is a bet, and if it loses, beat 04's eyes "
            "are not reachable by wording on this engine and the honest next "
            "move is to crop tighter so a small rotation READS as a glance."
        ),
        "init_provenance": (
            "Identical to rung 1's: 04-the-footnote-mac-plate-r1s1.png, "
            "sha256 5dd35da5...4350, published through ep2-b04-mac-plate-0819 "
            "and now resolvable on origin/farm-results-rtx5090, so both the "
            "plate and the refs guards RUN and PASS with no plate_ack."
        ),
        "not_done_on_purpose": (
            "No negative edit. No seed change. No crf change. No recipe change "
            "of any kind. No second seed. No staging change -- that is the "
            "route this rung exists to decide between, and taking it now would "
            "answer nothing."
        ),
    },
)
derive_spec.write(child, "pipeline/jobs/%s.yaml" % NEW_ID)
print("wrote pipeline/jobs/%s.yaml" % NEW_ID)
