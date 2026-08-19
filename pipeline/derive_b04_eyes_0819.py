#!/usr/bin/env python3
r"""Beat 04's motion, derived from the crf-10 face recipe that is already proven.

WHY THIS PARENT AND NOT ANOTHER. Beat 04's `done_when` is
"stillness with LIVE EYES: held breath readable in the body, eyes moving side to
side. This is the one beat where a near-motionless body is correct and only the
eyes carry it."  `ep2-b09-faceturn-crf10-0819` is the ONE job in this repo that
has demonstrated exactly that and nothing else: a slow eye close-and-reopen over
forty frames on a LOCKED camera, with the init holding for all 121 frames. Its
own ladder entry reads "the engine CAN move a face". The match is not
approximate -- the proven capability and the required capability are the same
sentence.

WHAT CHANGES, AND IT IS THE INIT AND THE WORDS ONLY. Size, frames, fps,
guidance, distilled sigmas, two-stage, offload, mode and --image-crf 10 are all
inherited untouched. `--image-crf 10` is the whole reason this parent exists:
at 33 the init was abandoned at the first denoising step and an adult man was a
different, younger person by frame 21. On a beat whose entire content is one
face holding still, a flag that discards the face is fatal, so the parent is
chosen for that integer as much as for the performance.

THE INIT is `04-the-footnote-mac-plate-r1s1.png`, drawn on macbook2 tonight from
the founder-ratified adult wording and judged the best frame of the re-render
wave. It is staged on the box at
`courier-box\farm-out\ep2-b04-mac-plate-0819\` and its sha256 was verified
BYTE-FOR-BYTE on both ends before this script was written
(5dd35da5...4350); the crop step asserts it again before writing anything, so a
truncated copy fails loudly instead of animating a corrupt picture.

NOT A NEW RECIPE, SO NOT A NEW SAMPLE. Every generative parameter is the
parent's. One clip.

$0. Run:  python3 pipeline/derive_b04_eyes_0819.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b09-faceturn-crf10-0819.yaml"
NEW_ID = "ep2-b04-eyes-crf10-0819"
OUT = "pipeline/jobs/%s.yaml" % NEW_ID

INIT = (r"C:\banyan-farm\courier-box\farm-out\ep2-b04-mac-plate-0819"
        r"\04-the-footnote-mac-plate-r1s1.png")
INIT_SHA = "5dd35da532612e5d85c15ef3353068bf1e44675f8ddfc73c316ac2f654d4e350"

# THE IDENTITY CLAUSE IS COPIED, NOT COMPOSED -- byte-identical to the string the
# founder ratified on 2026-08-19 and to DRAFTS[14]/DRAFTS[4]'s. The motion stage
# is exactly where an unratified adjective would slip back in, so it does not get
# to write one.
PROMPT = (
    "2D anime, hand-drawn cel animation, static locked framing, the frame never "
    "moves, flat cel shading, clean ink linework, anime key art. Subject already "
    "in frame: ONE lean wiry adult goblin man alone, green skin, bald head, "
    "long pointed ears, patchwork cloak, crouched low in deep tall grass in "
    "bright daylight, seen close on his face and shoulders. HE IS HOLDING HIS "
    "BREATH AND ONLY HIS EYES MOVE: his eyes flick to one side, hold, then "
    "travel slowly back across to the other side. HIS MOUTH STAYS SHUT the "
    "whole time and his jaw stays set -- he is listening for something, not "
    "speaking, and no word is said. His head and shoulders stay STILL. He stays "
    "THE SAME GOBLIN from the first frame to the last: the same green skin, the "
    "same bald head, the same long pointed ears, one face and one figure only. "
    "The light on him is CONSTANT and does not flicker, pulse or strobe. Soft "
    "steady daylight, cinematic lighting, detailed, newest, masterpiece, best "
    "quality, very aesthetic."
)

# The parent's negative with its GUARD identity clauses swapped for the goblin's
# and the round-build bans added. Everything structural -- the anti-camera-move
# block, the anti-strobe block, the anti-morph block, the scene-change block --
# is the parent's word for word, because those are the clauses that bought the
# locked 121-frame take and none of them is this job's variable.
NEGATIVE = (
    "open mouth, talking, speaking, shouting, teeth, tongue, lip sync, "
    "second face, second goblin, two goblins, 2boys, crowd, child, chibi, baby, "
    "girl, round head, big eyes, cute, different face, changing face, face "
    "changing, morphing, melting face, skin colour change, human skin, pale "
    "skin, hair, wig, glasses, "
    "flickering light, strobe, strobing, pulsing light, flashing light, "
    "blinking glow, camera pan, camera tilt, panning, tilting, camera movement, "
    "dolly, zoom, push in, pull back, tripod, camera, camera equipment, film "
    "equipment, walking out of frame, leaving the frame, drifting sideways, "
    "moving to a different spot, standing up, sitting down, scene change, shot "
    "change, new camera angle, different location, photorealistic, 3D render, "
    "CGI, live action, motion blur, text"
)

child = derive_spec.derive(
    src=PARENT,
    new_id=NEW_ID,
    fresh={
        "owner": "enactment lane, 2026-08-19 (the goblin re-render wave)",
        "consumer": (
            "The episode 2 cut, beat 04. The cut currently carries "
            "b04-refire-0814, which is the ROUND young goblin the founder ruled "
            "against on 2026-08-19 -- \"c kinda is but still pretty bad so change "
            "it\". This clip is the replacement take. Its plate is the adult he "
            "picked, so the only question left on this beat is whether the eyes "
            "carry it in motion."
        ),
        "success": (
            "One 704x1280 121-frame mp4 in which the goblin's EYES MOVE SIDE TO "
            "SIDE and almost nothing else does. Scored against beat 04's own "
            "done_when: LIVE EYES with the held breath readable, on a body that "
            "is near-motionless -- this is the one beat where a still body is "
            "correct. PASS needs all four: E1 the eyes visibly travel to one "
            "side and back, judged at 1:1 and not from a metric; E2 the mouth "
            "stays SHUT for all 121 frames -- an open mouth reads as speech and "
            "this beat has no line; E3 he is the SAME adult goblin at frame 121 "
            "as at frame 1, green, bald, long-eared, no drift toward a human or "
            "a child; E4 the camera does not move. FAIL-FROZEN is a real "
            "outcome here and is NOT a pass: on a beat carried entirely by the "
            "eyes, an init held so hard that nothing moves fails exactly as "
            "badly as a face that morphs."
        ),
        "why": (
            "$0, ~7 minutes, no download, and it is the first motion job the "
            "2026-08-19 ruling makes legal. Every generative parameter is "
            "inherited from ep2-b09-faceturn-crf10-0819, the one job that has "
            "demonstrated this exact capability -- a face performing on a locked "
            "camera with the init surviving 121 frames at --image-crf 10. Only "
            "the init picture and the words change, so a bad result is "
            "attributable to this beat rather than to the recipe."
        ),
    },
    overrides={
        # Same seed as the parent's proven take, so the only differences between
        # that clip and this one are the init picture and the words.
        "seed": 20260819,
        "key:beat": 4,
        "key:est_minutes": 7,
        "argv:--src": INIT,
        "argv:--sha256": INIT_SHA,
        "payload:b04-motion-prompt.txt": PROMPT,
        "payload:b04-negative.txt": NEGATIVE,
    },
    # ORDER MATTERS AND A BARE `b09- -> b04-` IS WRONG HERE. derive_spec appends
    # its own (parent id -> child id) rule AFTER these, so a bare `b09-` rewrites
    # `ep2-b09-faceturn-crf10-0819` to `ep2-b04-faceturn-...` first and the
    # parent-id rule then matches nothing -- leaving every payload and artifact
    # under a directory named `faceturn` while the job is called `eyes`. Caught by
    # reading the generated file. So each payload basename is named explicitly and
    # nothing here can touch the parent id.
    retoken=[
        ("b09-motion-prompt", "b04-motion-prompt"),
        ("b09-negative", "b04-negative"),
        ("b09-jobs-encode", "b04-jobs-encode"),
        ("b09-jobs-render", "b04-jobs-render"),
        ("b09-embeds", "b04-embeds"),
        ("b09-init-", "b04-init-"),
        ("09-the-pause", "04-the-footnote"),
        ('"beat": 9', '"beat": 4'),
    ],
    extra={
        "bar": {
            "e1_the_eyes_travel": (
                "The eyes visibly move to one side, hold, and come back. Read at "
                "1:1 on the actual frames. THE PRE-REGISTERED MOST LIKELY "
                "FAILURE IS THAT THEY DO NOT: the parent's win was an eye "
                "close-and-reopen, which is a LID movement, and a lateral GAZE "
                "shift is a different and smaller motion. If E1 fails while E2, "
                "E3 and E4 pass, the finding is that this engine moves lids and "
                "not gaze, and the next rung is a lid-based reading of the same "
                "beat -- a slow blink under held breath -- not a fifth wording."
            ),
            "e2_mouth_shut": (
                "Closed for all 121 frames. Beat 04 has no line; an open mouth "
                "is a speech cue and would have to be cut."
            ),
            "e3_identity_holds": (
                "Same adult goblin at frame 121 as at frame 1 -- green, bald, "
                "long pointed ears. This is the clause --image-crf 10 exists to "
                "protect: at 33 the parent's man was a different, younger person "
                "by frame 21, and a drift toward a CHILD here would re-open the "
                "exact question the founder just closed."
            ),
            "e4_camera_locked": (
                "No pan, tilt, dolly or zoom. Inherited clause; the parent held "
                "it."
            ),
        },
        "pre_registered_fail_modes": (
            "F1 FAIL-FROZEN -- nothing moves at all, and on this beat that is a "
            "failure and not a safe outcome. F2 GAZE-DOES-NOT-SHIFT while the "
            "rest holds (see e1, the most likely). F3 the mouth opens. F4 "
            "identity drifts toward a human or a child. F5 the grass animates "
            "and the face does not, which would read as wind rather than as a "
            "performance."
        ),
        "init_provenance": (
            "04-the-footnote-mac-plate-r1s1.png, drawn on macbook2 2026-08-19 "
            "from DRAFTS[4] at seed 20260819, on the founder-ratified adult "
            "wording. Judged the best frame of the re-render wave and the wave's "
            "control -- the only one of four beats with no plant in it and the "
            "only one that landed. sha256 5dd35da5...4350, verified byte-for-byte "
            "on the Mac and on the box before this spec existed, and asserted "
            "again by the crop step at run time."
        ),
        "failure_predicted_in_advance": (
            "The gaze shift (F2). The parent proved LIDS move; nothing in this "
            "repo has yet shown a lateral GAZE travelling on this engine, and "
            "the two are not the same motion. Named here so that if it comes "
            "back frozen-eyed the result is a finding about the engine rather "
            "than a disappointment about the beat."
        ),
        "not_done_on_purpose": (
            "No recipe change of any kind -- size, frames, fps, guidance, "
            "sigmas, two-stage, offload, mode and --image-crf 10 are the "
            "parent's. No second seed. No crf sweep: 33 is established wrong and "
            "10 is established workable, and the optimum between them is not "
            "this beat's question. No pick, no plate_ack, no cut, no publish."
        ),
    },
)
derive_spec.write(child, OUT)
print("wrote", OUT)
