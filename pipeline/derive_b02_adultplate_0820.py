#!/usr/bin/env python3
r"""Beat 02: the goblin beat nobody had ever flagged, and it has no adult plate.

WHAT THIS ANSWERS. On 2026-08-20 the founder wrote: "all of the goblin clips
today has had him as an adult. very bad character consistency." His own 08-19
ruling on /review/ep2-goblin-design-0819 makes the ADULT canon
(pipeline/canon.yaml `ep2-goblin-design-adult`), so the defect is not the adult
-- it is the MIX. The audit of every take in review/ep2-ship-0821 found four
beats still carrying the pre-ruling round child: 02, 04, 08 and 13.

BEAT 02 IS THE NEW ONE, AND IT IS THE FIRST SHOT OF THE GOBLIN IN THE EPISODE.
The 08-19 split page audited ep2-demo-0819c and listed nine goblin beats -- 03,
04, 08, 13, 20 round; 07, 14, 17, 19 adult. Beat 02 is on neither list. It was
missed. The script is unambiguous about who is on screen there:

    "A SCAVENGER -- goblin-ish, big ears, patchwork cloak, one broken tusk --
     sprints into frame, skids, and dives behind the sapling's thin trunk"

and the take in the ship cut, 02-the-sprint-b02-anchor-s20260834-0817, is the
round child: a big pale dome, four heads tall, child stance. So the very first
time the audience meets the character, he is the wrong one -- and beat 03, four
seconds later, is the ratified adult. That is the flip the founder saw, at the
worst possible place in the episode.

WHY A PLATE AND NOT A MOTION JOB. Beat 02's motion recipe is proven -- sixteen
`anchor` clips ran on 08-17 and one of them is what ships. It is an i2v recipe,
so the CHARACTER COMES FROM THE INIT PLATE, and every b02 plate this tree owns
descends from `ep2-b02-plate-0814`, which ran the IPA harness against
`refs-goblin-approved-0814`: the reference set frozen from the founder's "seed
s0 is the goblin" ruling, every tile of which is a small round-domed
child-proportioned goblin. There is no adult b02 plate anywhere on disk. The
08-13 attempts (`ep2-b02-adult-a/b`, `ep2-b02-adultplate/B`) predate the ruling
and their sheet, /review/ep2-picks/sheets/b02-adult-0813.jpg, is twelve round
figures. Firing motion tonight would render the child again, faster.

WHY THE TEXT ROUTE AND NOT THE REFERENCE ROUTE. The obvious one-variable move
is to point the b02 IPA plate job at a different `--refs` directory, and it is
wrong here: the only adult-leaning set staged on the box is
`refs-goblin-d1std-0815`, whose own header measures it at "4.5 to 5 heads ...
The only round inside the brief". It is design 1's lineage -- the round one --
and it would reproduce the defect. THE RATIFIED WORDING IS THE ONLY THING IN
THIS TREE THAT RELIABLY DRAWS THE ADULT: `lean wiry adult goblin man, green
skin, bald head, patchwork cloak` is what the Mac farm's plates carried on 08-18
and 08-19, and those are exactly the four beats that came out adult. Cast is
provable from text alone -- so this is txt2img with no reference image at all,
and the character is carried by the canon string quoted verbatim.

THE RECIPE IS PROVEN AND THE ONE CHANGE IS THE ARM. Parent is
`ep2-b08-cnetplate-r5-0819`, a two-minute SDXL plate job that has run clean on
this card. `--arm` moves from `hintskel` to `nocontrol`, which is
`controlnet_plate.py`'s own pure-txt2img path (`use_cn = a.arm != "nocontrol"`,
line 488). On that arm `--control`, `--control-sha256` and `--scale` are never
read -- they sit inside `if use_cn:` -- so they are left byte-identical rather
than edited, and this file says so out loud instead of leaving a reader to
wonder why a control hint is still in the argv of a job that uses none.

SIX SEEDS, ONE PROMPT, AND WHY THAT IS NOT A BANNED BATCH. ONE SAMPLE BEFORE
ANY BATCH governs scaling an UNAPPROVED RESULT -- rendering fifteen beats off a
recipe nobody has looked at. This is the other thing: a plate seed sweep, which
is how this project has picked every character design it owns (the 25-tile
`goblin-picker-0814.jpg` the founder ruled "seed s0" on, the six-design
`goblin-design-0815.jpg` he picked 1 from, and the A/B/C card that produced the
ruling this job serves). Six draws of one prompt is the SHEET, and the sheet is
the sample. Nothing renders motion off any of them until a human has looked at
the six side by side.

FILED TO BACKLOG, NOT READY, ON PURPOSE. At 20:57 tonight the card measured
0 ready / 0 running / 0 backlog -- last night's failure exactly. Autofill tops
`ready` up from `backlog/` every three minutes with no session alive, so these
draw overnight and the sheet is waiting in the morning.

$0, ~2 min each, 6 jobs. Run:  python3 pipeline/derive_b02_adultplate_0820.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b08-cnetplate-r5-0819.yaml"
PARENT_DIR_TOKEN = "b08cnetplate-r5-0819"

# The canon identity string is quoted VERBATIM from pipeline/canon.yaml
# ep2-goblin-design-adult and is the first clause, before any staging, because
# on this model the head of the prompt is what the cast is decided by.
PROMPT = (
    "lean wiry adult goblin man, green skin, bald head, long pointed ears, "
    "one broken tusk, faded green patchwork cloak, sprinting low through tall "
    "grass, mid-stride, leaning forward, dust at his heels, one tiny two-leaf "
    "sapling standing tall ahead of him, wide shot, static camera, morning "
    "field, 2D anime, cel shading, clean ink linework, cinematic lighting, "
    "detailed, masterpiece, best quality, very aesthetic"
)

# The negative fences the read the founder complained about, BY NAME. The
# 08-15 adult prompt that started this whole drift had NO `child` in its
# negative -- the goblin-design page names that omission as one of the three
# steps by which an inference became canon. It is not omitted here.
NEGATIVE = (
    "child, kid, boy, baby, toddler, chibi, mascot, cute, round face, chubby "
    "cheeks, blush, oversized head, big head, domed cranium, short stubby "
    "limbs, girl, crowd, two goblins, extra arms, extra hands, extra fingers, "
    "deformed hands, armor, helmet, knight, dark, night, text, watermark, "
    "photorealism, 3d render, low quality, deformed"
)

SEEDS = [20260820, 20260821, 20260822, 20260823, 20260824, 20260825]

BAR = {
    "p1_he_is_the_ratified_adult": (
        "THE CLAUSE THE JOB EXISTS FOR. Read at 1:1 against picture B on "
        "/review/ep2-goblin-design-0819 and against beats 07, 14, 17 and 19 of "
        "the ship cut: lean, angular, five and a half to six heads tall, green "
        "skin, bald, long pointed ears. NOT the round child of picture C -- no "
        "four-head proportion, no oversized dome, no pink cheek patches, no "
        "child stance. A tile that is arguable is a NO; the whole point of the "
        "sheet is that some tiles will not be arguable."
    ),
    "p2_he_is_running": (
        "The pose reads as a sprint at 1:1: weight forward, one leg driving, "
        "not a standing figure with motion lines. Beat 02's whole content is "
        "the dive, and an i2v init that shows him standing gives the motion "
        "recipe nowhere to go. Second in rank behind P1 and ahead of P3."
    ),
    "p3_the_sapling_is_tiny_and_in_frame": (
        "One thin stem with two leaves, rooted, and SHORTER THAN HE IS -- the "
        "founder's standing ruling that the sapling is tiny, which beat 13's "
        "shipped take broke by growing a mature forked tree. Nice to have on a "
        "plate, not fatal: the motion job can be conditioned on a tile that "
        "has him and no plant, and beat 03 already carries the size mismatch."
    ),
    "p4_wide_enough_for_a_dive": (
        "Full body in frame with grass around him, not a bust and not a "
        "close-up. The script says \"Camera wide so the dive reads\" and a "
        "cropped plate cannot be widened by a motion prompt."
    ),
    "p5_one_figure": (
        "Exactly one creature. No second goblin, no guard, no human. The b08 "
        "lane has burned eleven rungs on `green skin` landing on two bodies "
        "out of one pooled embedding, and that failure is cheap to detect here "
        "and expensive to detect after a motion render."
    ),
}

for seed in SEEDS:
    new_id = "ep2-b02-adultplate-s%d-0820" % seed
    child = derive_spec.derive(
        src=PARENT,
        new_id=new_id,
        fresh={
            "owner": "goblin-design audit lane, 2026-08-20 (beat 02 -- the missed goblin beat)",
            "consumer": (
                "A six-tile sheet, judged by eye in the morning, whose winner "
                "becomes the init plate for a beat 02 motion job on the proven "
                "`anchor` recipe -- and through that, beat 02's slot in "
                "review/ep2-ship-0821, which today opens the episode on the "
                "wrong creature. Nothing consumes a single one of these tiles "
                "on its own: the sheet is the artifact and the pick is a "
                "person's."
            ),
            "success": (
                "One 832x1216 SDXL plate, seed %d, of the founder-ratified lean "
                "wiry adult goblin sprinting through a morning field, drawn "
                "from the canon wording and NO reference image. It lands as one "
                "tile of a six-seed sheet and is scored against the five "
                "clauses in `bar`, in rank order: he is the adult, he is "
                "running, the sapling is tiny, the framing is wide, there is "
                "one figure. A tile that fails P1 is discarded whatever else it "
                "does, because P1 is the founder's complaint and the other four "
                "are craft." % seed
            ),
            "why": (
                "$0, ~2 minutes, zero dependencies, and it is the ONLY missing "
                "input for the one goblin beat in this episode that has never "
                "had an adult plate drawn for it. The card measured 0 ready / "
                "0 running / 0 backlog at 20:57 -- the same empty-box window "
                "that wasted last night -- and this needs no session alive to "
                "run."
            ),
        },
        overrides={
            "argv:--arm": "nocontrol",
            "argv:--seed": str(seed),
            "payload:prompt.txt": PROMPT,
            "payload:negative.txt": NEGATIVE,
            "key:beat": 2,
            "key:est_minutes": 3,
        },
        retoken=[(PARENT_DIR_TOKEN, "b02adultplate-s%d-0820" % seed)],
        extra={
            "the_one_variable_and_the_three_inert_flags": (
                "The arm, from `hintskel` to `nocontrol`. `controlnet_plate.py` "
                "line 488 reads `use_cn = a.arm != \"nocontrol\"`, and "
                "`--control`, `--control-sha256` and `--scale` are read only "
                "inside `if use_cn:` (lines 592-608). They are therefore left "
                "BYTE-IDENTICAL to the parent's rather than edited out -- an "
                "edit would be a second difference between this job and a "
                "recipe that has run clean, and the honest record is that they "
                "are present and never read. The prompt, the negative, the "
                "beat and the seed are the job's own; the model, the sampler, "
                "the size, the steps and the cfg are the parent's."
            ),
            "bar": BAR,
            "pre_registered_fail_modes": (
                "P-THE-CHILD-COMES-BACK -- the model resolves `goblin` to the "
                "round young one regardless of `lean wiry adult`, which is the "
                "read the whole 08-13 to 08-15 ladder was fighting when it had "
                "no `child` in its negative. Named as most likely on the tiles "
                "that also carry `tiny`. "
                "P-THE-SAPLING-EATS-THE-ADJECTIVES -- `tiny two-leaf sapling` "
                "sits four clauses after `lean wiry adult` and SDXL pools the "
                "whole string; `tiny` landing on HIM instead of the plant is "
                "the specific mechanism that made `a small goblin` read as a "
                "child in the first place (the 08-13 diagnosis, which the "
                "goblin-design page calls probably still right). "
                "P-TWO-FIGURES -- `green skin` on two bodies, the b08 lane's "
                "standing defect. "
                "P-NO-SPRINT -- he stands still in tall grass and the pose "
                "clause is ignored, which is P2 and is survivable only if some "
                "tile does run. "
                "P-CROPPED -- the figure fills the frame and the dive has "
                "nowhere to happen."
            ),
            "failure_predicted_in_advance": (
                "P-THE-SAPLING-EATS-THE-ADJECTIVES. This prompt asks for a "
                "LEAN ADULT and a TINY PLANT in one pooled embedding, and this "
                "model's documented habit in this repo is to move size words "
                "onto the subject. If it fires -- adult wording, child result, "
                "on tiles that drew the sapling and not on tiles that did not "
                "-- the next rung is to drop the plant from the plate entirely "
                "and let the motion job's field carry it, NOT a seventh "
                "wording of the identity string."
            ),
            "init_provenance": (
                "NONE, and that is the design. No IPA, no reference image, no "
                "control hint: this is txt2img from the canon string quoted "
                "verbatim out of pipeline/canon.yaml. Every existing b02 plate "
                "descends from refs-goblin-approved-0814, which is the round "
                "child set, and the only adult-leaning refs on the box "
                "(refs-goblin-d1std-0815) measure themselves at 4.5-5 heads and "
                "would reproduce the defect. Text is the route that has "
                "actually drawn this character."
            ),
            "not_done_on_purpose": (
                "NO MOTION JOB IS FILED AGAINST THESE. A plate nobody has "
                "looked at is not an approved result, and firing beat 02's "
                "motion recipe on an unseen tile is the exact thing ONE SAMPLE "
                "BEFORE ANY BATCH exists to stop. No edit to "
                "plate_scratch.py, wave-drafts.yaml or the canon identity "
                "string -- the string is quoted, not revised. No touch to "
                "beats 08 or 13, which peer lanes own tonight."
            ),
            "how_to_judge_this_in_the_morning": (
                "Tile all six into one contact sheet next to picture B and "
                "picture C from /review/ep2-goblin-design-0819, and answer P1 "
                "off the sheet in one line per tile. Only the P1 survivors get "
                "read for P2-P5. If no tile passes P1, the finding is that the "
                "canon wording alone does not carry this pose and the next rung "
                "is an adult reference set -- which does not exist yet and "
                "would have to be cut."
            ),
        },
    )
    derive_spec.write(child, "pipeline/jobs/%s.yaml" % new_id)
    print("wrote pipeline/jobs/%s.yaml  (seed %d, arm nocontrol)" % (new_id, seed))
