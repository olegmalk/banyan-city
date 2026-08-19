#!/usr/bin/env python3
"""ONE plate sample on Apple MPS from an INLINE prompt, with provenance.

    <farm-venv>/bin/python pipeline/plate_scratch.py --beat 14 --dry
    <farm-venv>/bin/python pipeline/plate_scratch.py --beat 14

WHY THIS EXISTS RATHER THAN `render_wave_sample.py`. That path renders a draft
key out of `pipeline/wave-drafts.yaml`, so testing a new plate framing means
editing a 350 KB hand-written provenance file that other lanes are usually in.
The beat-17 plate that solved its beat on the FIRST sample (2026-08-15,
`farm-out/ep2-b17-mac-plate-0815/`) did not go that way -- it was drawn by a
scratch runner from a prompt authored for the plate test, with `shots.md`
UNTOUCHED, and its own yaml says so. This file is that precedent made reusable.

WHY IT DOES NOT WRITE `shots.md` EITHER. The shot board is the crowd-facing
artefact and its wording is the founder's. A plate test proposes a framing; if
the framing wins, the board gets updated deliberately and separately.

ONE SAMPLE, NOT A BATCH (CLAUDE.md, founder 2026-08-03). `--seeds` exists but
refuses more than one unless `--i-have-seen-a-sample` is passed, because a
recipe change gets one picture looked at before it gets four.

TOKENS ARE MEASURED ON THE REAL TOKENIZER BEFORE ANYTHING IS DRAWN. SDXL's text
encoders truncate at 77 tokens silently; a prompt that overflows loses its tail,
which is where the style anchor lives. `--dry` measures and draws nothing.

WHAT A PLATE FROM THIS FILE IS EVIDENCE OF, AND WHAT IT IS NOT (2026-08-16).
**THIS MACHINE AND THE BOX ARE DIFFERENT RENDERERS.** Measured, not argued:
the same prompt, the same negative, the same checkpoint, the same 832x1216, the
same 40 steps, the same 7.5 guidance and the SAME SEED, with the starting latent
bit-identical because both paths seed a `torch.Generator("cpu")`, produce a
DIFFERENT PICTURE here than on the rtx5090 -- mean absolute pixel difference 61
of 255. Dtype is not the cause and was ruled out by rendering the box's own
bfloat16 on this machine: bf16/MPS vs bf16/CUDA is MAE 60.65 (same dtype, other
machine) while fp16 vs fp32 ON THIS MACHINE is MAE 3.2. The evidence and the
numbers are in `pipeline/backend_divergence_probe.py`; the mechanism is NOT
known and is deliberately not guessed at there.

So, for anyone about to draw here:

  * A PLATE IS EVIDENCE ABOUT A PICTURE. If the PNG itself travels forward --
    as the init image the box animates, or as the artefact -- the verdict on it
    stands, because the pixels are the thing that was judged and the thing that
    ships.
  * A PLATE IS NEVER A PREDICTION ABOUT A PROMPT. "This wording worked on the
    Mac, so the box will do it" IS VOID. It has never been true and on
    2026-08-16 it produced a purple fruit here from a prompt whose only other
    outing, on the box, returned red at 8 of 8 seeds.
  * COLOUR ESPECIALLY DOES NOT TRAVEL. This machine returns a purple fig with
    NO COLOUR WORD IN THE PROMPT AT ALL. The box does not. Canon colours must
    be written into the words for the box path regardless of what lands here.

NAME WHAT EVERY HAND IN FRAME IS DOING, INCLUDING THE HANDS YOU DO NOT CARE
ABOUT (2026-08-17). This is a rule about authoring a plate, not about one beat,
which is why it is here and not in a draft.

AN UNSPECIFIED HAND IS AN EMPTY REGION, AND THIS CHECKPOINT FILLS EMPTY REGIONS
WITH NOUNS. It is the vacancy law -- the one that says a flat margin with no noun
of its own grows the largest noun in the prompt -- applied to a body part instead
of to a sky. And as with every other instance of it, THE NEGATIVE DOES NOT REACH
IT: beat 11's strap survived a revision whose negative named it twice, at the
same seed, in a frame where three other added terms demonstrably moved both
heads.

THE EVIDENCE IS A CONTROL NOBODY PLANNED, which is most of why it is worth
believing. Two plates were drawn the same afternoon for unrelated reasons:
  * BEAT 05 specified BOTH men's arms (`arms swinging`). All four hands, opened
    at 4x-5x across three seeds: empty fists and open palms. NOTHING in any of
    them, no strap, no cord, nothing detached. 0 of 3 seeds grew an object.
  * BEAT 10 specified ONLY the near man's (`... in both hands`). He holds
    exactly the board he was given, every time. THE FAR MAN'S HANDS WERE NOT
    MENTIONED AND THEY CAME BACK HOLDING A LARGE BAMBOO POLE at one seed and a
    DUPLICATE OF THE BOARD at another -- with `weapon` sitting in the negative
    for the pole. 2 of 3 seeds grew an object; at the third his hands are
    clasped together, which is the model choosing a pose of its own and is
    exactly what naming one would have done on purpose.
Two conditions, one variable, three seeds each, in work aimed at something else
entirely: 2 of 3 against 0 of 3.

IT ALSO EXPLAINS THE STRAP RETROACTIVELY, and that is worth saying because two
revisions were spent on the wrong hypothesis. Beat 11's narrow dark strap was
never a stubborn prop and was never the sash -- (11,4) proved the sash bound to
a back while the strap stayed. It was an unspecified hand in a plate that
described two men in full-length view and never once said what their hands were
doing.

SO, WHEN AUTHORING: every hand that will be in frame gets a state. `loose fists
at their sides`, `arms swinging`, `hands clasped`, `holding X in both hands` --
a POSITIVE SHAPE, never `empty hands`, because CLIP cannot represent negation
and `empty hands` embeds as something very close to `hands`. If a hand does not
matter to the shot, frame it out or give it the cheapest state you can afford;
what you may not do is leave it unmentioned and expect nothing to appear in it.

TWO CANDIDATE RULES WERE WRITTEN HERE AND BOTH ARE RETRACTED. THEY ARE LEFT ON
THE PAGE, RETRACTED, BECAUSE THE RETRACTION IS THE MORE USEFUL ARTEFACT AND
BECAUSE THIS FILE'S OWN NEXT PARAGRAPH IS WHAT KILLED THEM. Read this before
adding a rule of your own.

RETRACTED: "do not forbid `horizon` in a shot that needs one". THE OBSERVATION
STANDS AND THE RULE DOES NOT. Beat 05 rendered a downward plan view at 3 of 3
seeds with `horizon` in its negative -- no horizon band, no hedgerow, figures
shrinking, and at the worst of them the count breaking. Deleting that one word at
seed 20260817, nothing else changed, produced near eye level, a horizon band, a
hedgerow of dark bushes and distant hills, and this docstring said "mechanism
confirmed" on the strength of it. THREE FRESH SEEDS OF THAT BYTE-IDENTICAL
DELETION CAME BACK HIGH-ANGLE, 3 OF 3, one of them with four figures including
two children. So the deletion is NOT a lever; the one good frame was that seed's
luck. What survives is narrower and still worth having: a clause naming something
"BEHIND" is dead in a plan view, because a plan view has no behind -- which is why
`hedgerow behind` sat in the positive rendering nothing -- and the ONE frame where
a horizon existed is the ONE frame where the hedgerow rendered. That is a
correlation on n=1 and it is labelled as one.

RETRACTED AS A RULE, KEPT AS A RATE: "a face plate must name the eye state".
`thoughtful` plus `mouth closed` gave beat 09 three shut faces at three seeds, and
adding `eyes open` with `closed eyes` in the negative opened them on the first
sample. At four seeds of that same wording the eyes are: correctly open once, a
WINK once, OPEN BUT BLANK WHITE WITH NO IRISES once, and shut once. So the tag
does reach the eyelids -- it moved them at 3 of 4 against 0 of 3 without it -- and
it delivers a usable pair of eyes at 1 IN 4. That is not a lever you can build a
plate on; it is a lottery ticket with better odds than nothing, and a beat that
needs open eyes needs render-N-and-pick, not this tag and a hope.

WHAT THAT LEAVES. The hand rule above is the only one of the three with a matched
control at three seeds a side, and it is the only one stated as a rule. The other
two were each written off ONE picture, by a lane that had already written the
warning below and put it two paragraphs away from its own violation of it.

A SINGLE-SEED OBSERVATION IS NOT A FINDING, AND SEED 20260817 HAS A RECORD.
That one seed has now manufactured TWO plausible false laws in two days, both of
which dissolved on fresh draws:
  * 2026-08-16, `attribute_merge_law_0816` -- "two same-species figures merge
    their described attribute sets". Falsified by (11,3), whose comment had named
    in advance the outcome that would kill it and then honoured it.
  * 2026-08-17 -- "`light sandy hair` does not bind on this checkpoint", observed
    off TWO DIFFERENT PROMPTS (beats 05 and 10) which made it look like a
    property of the model. It bound at 4 of 4 fresh seeds, and at one of them the
    cream shirt AND the brown wrap skirt bound to the blond man while the tan
    tunic bound to the dark-haired one, in the same frame.
And bf79e534 broke a third on the motion side the day before: four wordings had
"established" that guard B turns his head, and all four ran 20260817; at three
fresh seeds the back stayed turned in 2 of 3.
  * 2026-08-17, LATER THE SAME DAY, THIS LANE ITSELF -- "deleting `horizon` from
    the negative fixes the camera", written into this very docstring as a rule off
    ONE picture at 20260817 and retracted above at 3 of 3 fresh seeds. The lane
    that wrote the warning is the lane that broke it, within the hour, in the same
    file. That is how cheap this mistake is to make and it is why the paragraph is
    phrased as an instruction rather than an observation.
So: BEFORE BUILDING A WORDING LADDER ON ANY FAULT, SPEND THREE FRESH SEEDS ON THE
BYTE-IDENTICAL PROMPT, and write the decision rule down first. Three renders is
minutes on the Mac fleet and it is the cheapest insurance this file has. If the
fault is a seed effect the ladder you were about to build would have "worked" for
the wrong reason and been banked as a law.

THE IRONY IS DELIBERATE AND IS THE REASON THIS PARAGRAPH IS HERE RATHER THAN IN
A LANE REPORT. `pipeline/canon.yaml` exists because five times a decision moved
and the thing that actually runs did not. A constraint on HOW WE MEASURE, left
in one lane's write-up, becomes the sixth instance by the same mechanism -- and
this one would be worse, because the file that hid it for four days hid it with
a comment that sounded like the question had already been settled.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))

BASE = "cagliostrolab/animagine-xl-3.1"
W, H = 832, 1216          # what every ep2 plate is drawn at
STEPS, GUIDANCE = 40, 7.5  # the beat-17 plate's settings, unchanged

# Inline plate drafts. Each is authored against that beat's `done_when` in
# review/ep2-picks/done-definitions.yaml, quoted here so the bar and the prompt
# cannot drift apart.
DRAFTS = {
    17: {
        # ------------------------------------------------------------------
        # 2026-08-16, THE TIGHT-INSERT LANE. THE PLATE, AND THE BAR THE CLIP
        # MADE FROM IT WILL BE JUDGED BY. BOTH WRITTEN BEFORE ANY PIXEL.
        # ------------------------------------------------------------------
        # WHAT IS ALREADY SETTLED AND IS NOT RE-DERIVED HERE. Three independent
        # lines converged this week:
        #   1. Whole-body motion renders. Twelve beat-17 cells, judged against
        #      a bar written before the renders: 12 of 12 stand up, head-top
        #      rise 29.2%-39.7% of frame height, horizon fixed, and the
        #      colour-segmentation tool was falsified by overlaying its own
        #      mask back onto the frames (which caught sky speckle scoring
        #      three real stand-ups as "no movement").
        #   2. Small in-hand actions do not, ON THAT SAME PLATE. amp-brush and
        #      amp-brushseat, same seed, byte-identical otherwise, hold the
        #      seated pose f0->f96 with the hands clasped on the knee, while
        #      clouds, eyelids and a bird move.
        #   3. Both at once inside one clip. All four beat-17 `full` cells,
        #      audited at all 97 frames: 4 of 4 stand and turn, 0 of 4 brush.
        #      One cell has cloak CONTACT WITHOUT TRAVERSAL -- drape and body
        #      rotation, not a stroke.
        # => the engine renders GROSS motion and drops SMALL in-hand actions.
        #    That also fits beats 06, 08 and 10, which have failed every
        #    wording, strength, seed, recipe and composition lever and which
        #    all three ask for a small in-hand prop manipulation.
        #
        # THE ONE THING THIS PLATE TESTS: frame the action so that IT IS THE
        # LARGEST MOVEMENT IN FRAME. Not a figure in a landscape performing a
        # small gesture -- a tight insert where the hand and the cloak are the
        # whole picture and the hand's travel across the cloth is the only
        # thing large enough to be the shot's motion. If size-in-frame is the
        # lever, this renders. If it does not, size-in-frame is NOT the lever
        # and the engine simply cannot do fine hand action, which is a
        # different and bigger fact about what episode 2 can contain.
        #
        # WHY EACH CLAUSE, and every one of these was learned by losing a
        # render, not reasoned out here:
        #   `hand focus, close-up` FIRST -- leading framing tags carry real
        #       weight and trailing ones have almost none (a peer lost a whole
        #       render to a trailing `wide two-shot` and got a close-up with
        #       the subject missing). The two tightest tags on the ladder go
        #       at the very front where they bind.
        #   `resting flat on` -- a STATE, not a verb. Twenty-four candidates
        #       failed on "pushes himself up to standing" because the model
        #       renders the verb's END state; a plate that says "brushing"
        #       would come back mid-stroke or finished, with nowhere left to
        #       travel. The plate is the PRE state on purpose.
        #   `hand and forearm` -- a hand alone renders as a severed prop and
        #       gives i2v nothing to hang an arm's motion on.
        #   `stitched cloth filling the whole frame` -- an empty upper half in
        #       a portrait frame is a hole the model fills with the largest
        #       noun in the prompt (deleting `wide blue sky above` removed a
        #       colossus completely). A tight insert is unusual framing and
        #       WILL invite content into empty space, so there is no empty
        #       space: cloth goes edge to edge and the negative forbids sky.
        #   no character name anywhere -- a verb or a prop does not bind to a
        #       named character in this checkpoint, so nothing is asked to.
        #
        # PLATE BAR, pre-registered. Usable only if ALL FOUR hold:
        #   P1 cloth (or hand) fills essentially the whole frame -- no sky, no
        #      horizon, no empty region larger than a hand.
        #   P2 a green clawed hand is IN CONTACT with the cloth and spans at
        #      least ~15% of the frame's width.
        #   P3 there is open, unobstructed cloth on at least one side of the
        #      hand, at least one hand-width across, for a stroke to cross.
        #   P4 no face, no whole figure, no second hand-and-arm pair, no prop.
        #
        # MOTION BAR, pre-registered HERE so it cannot be rewritten after the
        # clip. It is a BODY-MOTION test, not a picture-changed test.
        #   PASS requires all of:
        #     M1 a hand is in contact with the cloak in at least one frame;
        #     M2 that hand TRAVELS across the fabric while in contact -- its
        #        position relative to the cloth moves at least one hand-width
        #        (~15% of frame width) between two frames of the clip;
        #     M3 it is the HAND moving and not the camera: the frame edges and
        #        the cloth's own folds do not translate with it;
        #     M4 the path is continuous -- read at consecutive frames, the
        #        hand can be followed from where it starts to where it ends.
        #   FAIL MODES, NAMED IN ADVANCE:
        #     F1 FROZEN -- identical hand position at f0 and f96, only the
        #        linework re-inked in place. Round 1's exact signature.
        #     F2 CLOTH-ONLY -- the fabric ripples or blows and the hand does
        #        not move relative to it.
        #     F3 CAMERA-ONLY -- the whole frame drifts, pushes in or zooms and
        #        hand and cloth keep the same relative geometry.
        #     F4 MORPH -- the hand dissolves, gains or loses fingers, or
        #        reappears somewhere else without a continuous path. A
        #        teleport is not a stroke.
        #     F5 SCENE BREAK -- the shot cuts, pulls back to a figure, changes
        #        location, or a second figure arrives.
        #     F6 CONTACT WITHOUT TRAVERSAL -- the hand touches and the cloth
        #        drapes or rotates under it but the hand does not travel.
        #        Explicitly a FAIL: it is what one of the four `full` cells
        #        already did and calling it a pass is how a bar gets bent.
        #   NOT EVIDENCE, and none of it will be quoted: `depth` is retired
        #   and inverted (full stand-up 0.290, zero-motion clip 0.516, a clip
        #   whose only movement was a bird 0.376); the old `cadence` metric is
        #   structurally blind (odd hold periods alias to exactly 1.00x);
        #   camera-scale numbers are unreliable without aligned frames. All 97
        #   frames get opened consecutively via pipeline/coldread_frames.py,
        #   cropped to the hand and the cloth, and any tool used gets its own
        #   output overlaid back onto the frames before it is believed.
        #
        # ONE SAMPLE. If it works, SAY SO AND STOP -- splitting beat 17 into
        # two shots and re-planning 06/08/10 as inserts is an authorship
        # decision, not this lane's.
        "slug": "goodbye-insert",
        "done_when": (
            "MOTION BAR (pre-registered before the plate was drawn): a hand "
            "makes contact with the cloak AND TRAVELS ACROSS IT -- at least "
            "one hand-width of movement relative to the cloth, continuous "
            "across consecutive frames, the hand moving and not the camera. "
            "FAIL modes named in advance: F1 frozen, F2 cloth-only, F3 "
            "camera-only, F4 morph/teleport, F5 scene break, F6 contact "
            "without traversal. A changed picture is not a pass."
        ),
        "why": (
            "Beat 17's script line is 'The scavenger stands, brushes off, and "
            "turns to go' and its definition wants stand, brush, turn. The "
            "stand and the turn render 12 of 12; the brush renders 0 of 4 in "
            "the compound and 0 of 2 when asked for alone at the same seed. "
            "The surrounding beat already works, so the insert is the only "
            "unknown -- which makes beat 17's brush the cleanest test of the "
            "general principle: frame the action so that it IS the largest "
            "movement in frame. This plate makes the hand and the cloak the "
            "entire picture so the stroke has nothing to compete with. A pass "
            "unlocks beats 06/08/10 as inserts; a fail retires size-in-frame "
            "as a lever and says the engine cannot do fine hand action."
        ),
        "prompt": (
            "hand focus, close-up, a green clawed hand and forearm resting "
            "flat on a dusty patchwork cloak, brown and grey stitched cloth "
            "filling the whole frame, deep folds in the fabric, dust and "
            "grass seed on the cloth, warm daylight, cinematic lighting, "
            "detailed, masterpiece, best quality, very aesthetic"
        ),
        "negative": (
            "text, face, head, portrait, looking at viewer, full body, "
            "wide shot, standing, walking, 1girl, 2boys, crowd, "
            "sky, clouds, horizon, grass field, tree, house, indoors, "
            "white background, simple background, holding object, spear, "
            "staff, sword, stick, photorealism, 3d render, dark, night"
        ),
        "seed": 20260816,
    },
    8: {
        "slug": "inside-him",
        "done_when": (
            "the clipboard comes DOWN and the point goes to the BELLY, both "
            "legible; both guards and the scavenger in frame, since a point "
            "needs its target visible."
        ),
        "why": (
            "Beat 08 has NO VERDICT YET and the reason is visible in one "
            "look: the picture its motion takes were animated from "
            "(farm-out/ep2-b08-twohander/b19-init-704x1280.png, sha 6c403952) "
            "is a COSTUME CARD -- one figure, waist-up, eyes closed, on flat "
            "blank paper, no field, no second guard and no scavenger. No "
            "wording reaches a target that is not in the picture, which is "
            "why every lever failed. REWRITTEN 2026-08-18, because the first "
            "Mac sample off the earlier wording came back with a HILL-SIZED "
            "goblin looming over three tiny guards and this field promised a "
            "plate that no longer exists. WHAT IT IS NOW. (1) TWO FIGURES, "
            "not three: done-definitions "
            "`figure_count_ruled_from_the_script_0817` reads the script as "
            "Guard 2 plus the scavenger, and the `done_when` above still "
            "asks for both guards and is superseded by that ruling, not by "
            "this note. (2) THE ADULT GOBLIN, in beat 14's identity wording "
            "character for character, because beat 14 is the man the founder "
            "chose and the plate that renders him. (3) THE GUARD IS NAMED -- "
            "guard B in the frozen wardrobe, in beat 10's exact clause, "
            "since `two adult guard men in uniform` described nobody. (4) "
            "THE UPPER BAND IS TALL GRASS. The earlier draft reserved it as "
            "`wide blue sky above` with `small figures low in frame`, which "
            "is the vacancy hole this beat has already paid for: it lost "
            "five samples to a colossus grown in a reserved sky, and its r4 "
            "proved a negative naming `giant, colossal, monster, kaiju, "
            "statue, face in the sky` removes it NOT AT ALL. So the hole is "
            "DELETED rather than negated and no giant words were added. "
            "Cycle 018 still governs the framing -- on beat 17's WIDE "
            "full-body plate the engine moved a whole body in 12 of 12 "
            "takes -- but the room above the heads is grass, not sky."
        ),
        # ------------------------------------------------------------------
        # CAST + SCALE CORRECTION, 2026-08-18. The 08-18 Mac sample off the
        # previous wording came back with a HILL-SIZED goblin looming over
        # three tiny guards. Four changes, each with a receipt already in this
        # file or in done-definitions.yaml:
        #   1. `3boys` -> `2boys`. done-definitions
        #      `figure_count_ruled_from_the_script_0817`: beat 08 is Guard 2
        #      and the scavenger, TWO figures. The `done_when` above still
        #      says "both guards and the scavenger" and is left standing --
        #      that ruling supersedes it and says so in its own text.
        #   2. THE GOBLIN IS NOW THE ADULT, in beat 14's identity wording
        #      copied character for character (`lean wiry adult goblin man,
        #      green skin, bald head, patchwork cloak`). The old `a lean adult
        #      goblin man` was a fifth wording of one character; beat 14 is
        #      the one the founder chose and it is the one that renders.
        #   3. `wide blue sky above` and `small figures low in frame` are
        #      DELETED and the upper band gets a noun of its own, `tall
        #      grass`. This is beat 11's vacancy law applied to the beat that
        #      first paid for it -- see the block at beat 11: "beat 08 lost
        #      five samples to a colossus grown in a reserved sky, and beat 08
        #      r4 proved a negative naming `giant, colossal, monster, kaiju,
        #      statue, face in the sky` removes it NOT AT ALL". So no giant
        #      words were added to the negative; the hole is filled instead.
        #      `scenery` goes with them: it is the tag that makes the
        #      landscape the subject and the men the staffage.
        #   4. THE GUARD IS NAMED. Guard B (= Guard 2, the one with the bark
        #      clipboard) in the frozen wardrobe of
        #      `guards_CORRECTION_0816.still_genuinely_the_founders_ANSWERED_0816`,
        #      and in beat 10's exact clause so the two plates cannot draw two
        #      different men. `uniform` described nobody. Guard A is not in
        #      this shot, so his wire-rims are not named and the D2
        #      glasses-bleed problem is not bought here.
        # `arm's length apart` carries the one spatial condition the beat
        # needs -- the belly has to be reachable by an extended arm -- without
        # `size difference` or "one taller", which is a GIANTESS TAG on this
        # checkpoint and is what the beat-11 block forbids.
        # Measured on the real CLIP tokenizer before commit: 76/77 positive,
        # 75/77 negative, no positive/negative collision (exit 7 clean).
        # ------------------------------------------------------------------
        "prompt": (
            "2boys, full body, wide shot, standing in tall grass, an adult "
            "guard man with light sandy hair, cream shirt, white shoulder "
            "sash, brown wrap skirt, lowers a bark clipboard and points at "
            "the belly of a lean wiry adult goblin man, green skin, bald "
            "head, patchwork cloak, arm's length apart, sunny day, "
            "masterpiece, best quality"
        ),
        # `2boys` LEAVES the negative -- it is now the count being asked for,
        # and leaving it would be the exit-7 contradiction. `3boys` takes its
        # place. `distant, small figure` and `sky` are the scale block; `sky`
        # goes in but `horizon` deliberately does NOT, because D4 in the beat
        # 11 sweep measured that `horizon` in the negative of a FRONT-FACING
        # wide shot tilts the camera down until the figures shrink -- which is
        # this beat's exact fault. `stick` joins the held-object block for the
        # goblin's unnamed hands (D3: an unspecified pair grows an object).
        "negative": (
            "text, close-up, portrait, upper body, cropped, "
            "1boy, 3boys, 4boys, solo, distant, small figure, "
            "white background, simple background, baby, child, chibi, "
            "stitches, scars, spear, staff, sword, stick, "
            "tree, forest, house, sky, indoors, photorealism, 3d render, "
            "dark, night"
        ),
        "seed": 20260816,
    },
    11: {
        # ==================================================================
        # 2026-08-16, THE GUARD-PLATE LANE. BEAT 11, "THEY LEAVE".
        # THE PLATE AND THE BAR IT WILL BE JUDGED BY, BOTH WRITTEN AND
        # COMMITTED BEFORE A SINGLE PIXEL EXISTS. THE BAR DOES NOT GET
        # SOFTENED AFTERWARDS.
        # ==================================================================
        # THE BEAT, QUOTED FROM ITS SCRIPT so the plate and the words cannot
        # drift apart. genomes/sapling/nodes/002b-first-citizen/node.md:
        #   "THEY LEAVE - 0:50-0:55.  The guards walk away arguing, backs to
        #    camera, genuinely trying to do their jobs."
        # And its done_when, done-definitions.yaml beats.'11':
        #   "two guards walk away from camera, backs turned, still arguing;
        #    both present the whole clip; field present at frame one."
        #
        # ------------------------------------------------------------------
        # WHY THIS PLATE EXISTS, AND WHY IT IS THE HIGHEST-VALUE ONE TO DRAW
        # ------------------------------------------------------------------
        # 1. THE CAST IS APPROVED AND NO PICTURE OF IT DOING ANYTHING EXISTS.
        #    The founder cast both men in his own words -- 2026-08-14
        #    "1 for the guards", 2026-08-15 "ill take the guard b you chose"
        #    (guards_CORRECTION_0816). That released the WORK of drawing
        #    staged plates and released no render: both men exist only as
        #    COSTUME CARDS ON A GREY VOID.
        # 2. BEAT 11 IS PURE WHOLE-BODY MOTION, which is the one thing this
        #    engine does reliably. Twelve beat-17 cells gave 12/12 whole-body
        #    stand-ups; the same plate's small in-hand action is 0 of 8, and
        #    a tight insert at 57% of frame width failed too. Two men walking
        #    away has no in-hand action in it at all.
        # 3. THE TAKE IN THE DEMO CUT IS KNOWINGLY BROKEN -- "TOTAL IDENTITY
        #    COLLAPSE AWAY FROM THE PLATE", a bald adult growing dark hair
        #    across f16-f21 and ending on two indistinguishable brown-haired
        #    backs.
        #
        # ------------------------------------------------------------------
        # THE FINDING THAT MADE THIS DRAFT, AND IT IS NOT ABOUT BEAT 11
        # ------------------------------------------------------------------
        # Every `farm-out/*/NN-*.yaml` sidecar for beats 05, 06, 09, 10 and 11
        # was read on 2026-08-16 -- 15 distinct prompts across 20 output dirs.
        # NOT ONE OF THE FIFTEEN NAMES GUARD A OR GUARD B. Every one asks for
        # an anonymous type: "two round bald guard men in plain brown tunics",
        # "silly harmless bureaucrats with round soft bodies and bare heads".
        # `bald` or `bare heads` appears in THIRTEEN of the fifteen.
        #
        # NEITHER APPROVED GUARD IS BALD. A has dark cropped hair, B has light
        # sandy hair, and wave-drafts.yaml says so while authoring the cast:
        # "`no hair, no wig` -- that is what made the goblin bald and THE
        # GUARDS NEED HAIR." So `bald` was never drift; it was ASKED FOR, and
        # every staged guard picture we own differs from the approved cast in
        # the first attribute a viewer reads off a human being -- and the one
        # attribute still legible when a man is facing away.
        #
        # That reframes beat 11's own recorded fault: the plate asked for
        # bald, the render grew dark hair, and dark hair is what guard A
        # ACTUALLY IS. We logged the model drifting TOWARD the approved cast
        # as the defect, and then spent rounds tuning identity-holding levers
        # on a plate that never specified an identity to hold. Beats 05 and 10
        # both carry `open_question: ... ONE answer settles both beats` about
        # guards reading "younger and softer" than 06 and 11 -- that is the
        # same cause, two plates each independently improvising a man.
        #
        # THE VOCABULARY BELOW IS NOT INVENTED. It is lifted from the drafts
        # that actually drew the approved men, so the words are already proven
        # on this checkpoint (pipeline/wave-drafts.yaml, read only, untouched):
        #   authored_guard_sheet_a:   "tall and lean, long face, DARK CROPPED
        #     HAIR, a plain brown tunic with a CLOTH SASH OF OFFICE across his
        #     chest, DARK TROUSERS AND BOOTS"
        #   authored_guard_b_derived: "a plain DARK BROWN TUNIC with a cloth
        #     sash of office across his chest, LIGHT SANDY HAIR, carrying a
        #     bark clipboard, dark trousers and boots"
        #
        # ------------------------------------------------------------------
        # WHY EACH CLAUSE. Every one is a lesson someone already paid for.
        # ------------------------------------------------------------------
        #   `2boys, from behind, full body, wide shot` LEADING -- leading
        #       framing tags carry real weight and trailing ones almost none
        #       (a peer lost a whole render to a trailing `wide two-shot`).
        #       Count and backs-turned are the two things that must bind, so
        #       they go at the very front.
        #   `standing in tall grass` -- a STATE, not a verb. The model renders
        #       a verb's END state, so "walk away growing smaller" (which is
        #       literally what the idfix plate asked for) returns them already
        #       small and half-gone, with nowhere left to travel. The plate is
        #       the PRE position on purpose: turned away, still near, with the
        #       field ahead of them. i2v supplies the walk.
        #   `tall grass background` -- THE VACANCY LAW, and beat 11 is the
        #       composition that invites it hardest: two figures walking into
        #       open field is by construction a large empty region. An empty
        #       region is a hole the model fills with the largest noun in the
        #       prompt AND THE NEGATIVE DOES NOT REACH IT -- beat 08 lost five
        #       samples to a colossus grown in a reserved sky, and beat 08 r4
        #       proved a negative naming `giant, colossal, monster, kaiju,
        #       statue, face in the sky` removes it NOT AT ALL; beat 17 r1's
        #       insert had no hole so the CLIP manufactured one by pulling the
        #       camera back and put a face in it; beat 17 r2 grew three extra
        #       goblin heads in a flat grass margin with `solo` LEADING and
        #       `2boys` in the negative. The fix that worked on the first
        #       sample is to give the background A NOUN OF ITS OWN, and `tall
        #       grass` is the one this repo has already used for it. Tall
        #       grass cannot become a character.
        #   the two men written as TWO SEPARATE PERSON CLAUSES, each pairing
        #       one hair colour with one garment -- a verb or prop does not
        #       bind to a named character on this checkpoint (the bark board
        #       attached to the goblin in 9 frames of 12; `pointing at
        #       another` in 3 of 3), and with TWO SAME-SPECIES MEN that risk
        #       is at its maximum. Binding by hair-plus-garment inside one
        #       clause is the best instrument available, and WHICH FIGURE GOT
        #       WHICH COSTUME IS CHECKED BY EYE afterwards, never assumed.
        #   NO `size difference`, and no "one taller, one shorter" -- `size
        #       difference` is a GIANTESS TAG on this checkpoint and made one
        #       figure 8x the other. Guard B is heavier-built on the sheet;
        #       that is given up deliberately rather than risked.
        #   NO CLIPBOARD, and this is a decision, not an omission. It is not
        #       in beat 11's done_when; props do not bind to a named figure
        #       here; and guard B's clipboard is the founder's OWN NAMED
        #       DEFECT ("there is a clipboard floating behind him") which must
        #       not be carried into anything derived from the reference. Its
        #       arrival is fail mode Q7 below.
        #   NO GLASSES, and the founder's open question cannot change this
        #       plate. Guard A's wire-rims are on his board unanswered. Beat
        #       11 is BACKS TURNED: wire-rims are not visible from any angle
        #       in this shot. The sheet's own appearance is used and glasses
        #       are simply absent from the prompt. His answer can be applied
        #       to beat 09 -- his face, in close-up -- without redrawing this.
        #       -- ANSWERED 2026-08-16. The paragraph above is left standing
        #       because its CONCLUSION for beat 11 is still right and the
        #       reasoning is what has to be visibly discharged; only its
        #       premise is dead. The question is not open: he ruled "the cast
        #       stands as drawn", and he had been asked about the wire-rims
        #       specifically and by name on that card, so "as drawn" answers
        #       the glasses as much as the rest of the sheet. THE GLASSES ARE
        #       CANON. Nothing in this plate changes -- beat 11 is backs
        #       turned, wire-rims are invisible from behind, and a plate that
        #       does not show them cannot contradict them. What DOES change is
        #       everything downstream: every guard prompt that shows guard A's
        #       FACE must now NAME the wire-rims, because leaving them unnamed
        #       is the same defect as the anonymous "two round bald guard men"
        #       that miscast every staged plate we have. Beat 09 is where it
        #       bites first. The word `wire-rim` appears in ZERO prompts in
        #       this repo (measured 2026-08-17), and no canon subject enforces
        #       it, so today nothing would catch its absence.
        #   `dark` IS NOT IN THE NEGATIVE, though it is in every other draft
        #       in this file. Both approved guards are defined by dark things
        #       (dark cropped hair, dark brown tunic, dark trousers), and a
        #       negative `dark` put there for LIGHTING would fight the cast
        #       itself. `night` alone carries the lighting intent. Named here
        #       so the difference from the other drafts is not read as sloppy.
        #
        # ------------------------------------------------------------------
        # PLATE BAR, PRE-REGISTERED. USABLE ONLY IF ALL SEVEN HOLD.
        # A lane confessed today to a bar that certified a prop's MATERIAL
        # while never mentioning its SHAPE, and scored 8/12 "passes" with 0/12
        # usable. So every load-bearing axis is named here, in advance.
        # ------------------------------------------------------------------
        #   P1 IDENTITY -- THE APPROVED PAIR. This is the whole point of the
        #      exercise and it is scored first. The two men must read as guard
        #      A and guard B of review/ep2-picks/sheets/guard-cast-0816.jpg:
        #      ONE WITH DARK HAIR in a light tan/beige tunic, ONE WITH LIGHT
        #      SANDY/BLOND HAIR in a darker brown garment. NEITHER MAN IS
        #      BALD -- a bald pair fails outright, no matter how good the
        #      staging, because bald is precisely the defect being corrected.
        #      Exact tailoring, sash geometry and boot detail are NOT scored;
        #      hair colour, garment value and the two being TOLD APART are.
        #   P2 TWO WHOLE FIGURES. Exactly 2 human figures -- not 1, not 3.
        #      Both full-length: head, torso, both arms, both legs, feet
        #      inside the frame. A third body ANYWHERE, including small in the
        #      background, is a FAIL and is the vacancy law's signature.
        #   P3 BACKS TURNED, WITH ROOM TO WALK INTO. Both men seen from
        #      behind: no face, no eyes, no frontal torso on either man. Field
        #      continues AHEAD of them, away from camera, unobstructed, for at
        #      least the height of a man, so the walk has somewhere to go. A
        #      plate with a wall of grass immediately behind them fails: it is
        #      the same defect as beat 02's high angle carrying the face away
        #      from the lens, caught before rendering instead of after.
        #   P4 SIZE IN FRAME. The taller man spans AT LEAST 25% of the frame
        #      height. The number exists to protect P1, not for its own sake:
        #      below it, hair colour and garment value stop being legible and
        #      the plate cannot carry identity into a render at all. `small
        #      figures low in frame` is what shrank beat 08 r1 to specks.
        #   P5 NO VACANCY. No flat untextured region larger than a man's
        #      torso: no sky band, no blank paper, no white background, no
        #      featureless colour wash. Grass texture to the top edge.
        #   P6 NO PROPS. No clipboard, no board, no badge, no weapon, in or
        #      near either man's hands, and nothing floating unattached.
        #   P7 FIELD PRESENT IN THE PLATE ITSELF -- the beat's own done_when
        #      says "field present at frame one", and a plate that opens on a
        #      void is where beat 11's ~1s white opening came from.
        #   RECORDED AND NOT SCORED: wire-rim glasses (invisible from behind),
        #      build difference between the men, palette continuity, time of
        #      day. This is a staging plate, never a take.
        #
        # ------------------------------------------------------------------
        # FAIL MODES NAMED IN ADVANCE, so none of them can be talked into a
        # pass after the fact.
        # ------------------------------------------------------------------
        #   Q1 BALD PAIR -- the beat-11 attractor, asked for by all 15 prior
        #      prompts and therefore the most likely single outcome.
        #   Q2 COUNT -- one man, three men, or a spectator in the field.
        #   Q3 FRONTAL -- one or both turn to face the lens. This checkpoint
        #      prefers faces and `from behind` is the load-bearing tag.
        #   Q4 SPECKS -- figures too small for the two costumes to be told
        #      apart. Staging correct, identity unreadable, still a fail.
        #   Q5 VACANCY FILL -- a large flat region, WHETHER OR NOT something
        #      has grown in it. The hole itself is the fail; what fills it is
        #      the next render's problem.
        #   Q6 COSTUME MERGE -- both men in the same outfit or the same hair
        #      colour, i.e. two copies of one guard. The highest-probability
        #      two-same-species-figures failure and an outright FAIL: the beat
        #      is two distinguishable men arguing.
        #   Q7 PROP ARRIVAL -- a clipboard or board appears, held or floating.
        #   Q8 SWAPPED COSTUME -- the dark hair lands on the dark-brown tunic
        #      and the sandy hair on the tan one. Recorded honestly if it
        #      happens; it is a FAIL of P1 because the pair is then neither
        #      guard, and it is the specific thing that must be CHECKED BY EYE
        #      rather than assumed from the wording.
        #
        # HONEST PRIOR: the last two-figure plate round hit 1 IN 15. Three or
        # four seeds are budgeted. ONE SAMPLE IS OPENED AND JUDGED FIRST, and
        # a single failure is not a dead end.
        #
        # DO NOT FIRE MOTION OFF THIS. If the plate passes, SAY SO AND STOP --
        # whether beat 11's replacement gets rendered is a separate decision,
        # and beats.'11'.blocked_on_0815 still has only its cast half
        # discharged. No `plate_ack` waiver, ever. shots.md, wave-drafts.yaml
        # and farm-queue.yaml are UNTOUCHED by this lane.
        "slug": "they-leave",
        "done_when": (
            "PLATE BAR, pre-registered before the plate was drawn. All seven "
            "must hold: P1 the two men are the APPROVED guards -- one dark "
            "haired in a light tan tunic, one light-sandy haired in a darker "
            "brown garment, NEITHER BALD; P2 exactly two whole figures, "
            "full-length, no third body; P3 both seen from behind, no face, "
            "with unobstructed field ahead of them to walk into; P4 the "
            "taller man spans at least 25% of frame height so the costumes "
            "are legible; P5 no flat untextured region larger than a torso; "
            "P6 no clipboard, board, badge or weapon; P7 field present in the "
            "plate itself. Fail modes named in advance: Q1 bald pair, Q2 "
            "wrong count, Q3 frontal, Q4 specks, Q5 vacancy, Q6 costume "
            "merge, Q7 prop arrival, Q8 swapped costume. Good staging with "
            "the wrong men is a FAIL -- identity is the point of this plate."
        ),
        "why": (
            "The founder cast both guards on 14 and 15 August, and no staged "
            "picture of them doing anything exists -- both men are costume "
            "cards on a grey void, which is why beats 05, 06, 07, 09, 10 and "
            "11 were animated off costume cards and cannot be cut. Worse, a "
            "sweep of all 15 plate prompts for those beats found NONE naming "
            "the cast: 13 of 15 ask for `bald` or `bare heads`, and neither "
            "approved guard is bald. So every guard plate we own is mis-cast "
            "at the most visible attribute there is, and beat 11's recorded "
            "`identity collapse` is the render growing the dark hair guard A "
            "actually has. Beat 11 goes first because it is PURE WHOLE-BODY "
            "MOTION -- the one thing this engine does reliably, 12/12 "
            "stand-ups against 0/8 in-hand -- and because the take standing "
            "in the demo cut is knowingly broken."
        ),
        "prompt": (
            "2boys, from behind, full body, wide shot, two guard men "
            "standing in tall grass, tall grass background, one man with "
            "dark cropped hair in a plain tan tunic, one man with light "
            "sandy hair in a dark brown tunic, cloth sash of office, dark "
            "trousers and boots, sunny day, masterpiece, best quality"
        ),
        "negative": (
            "text, looking at viewer, facing viewer, face, close-up, "
            "portrait, distant, small figure, bald, 1boy, 3boys, solo, "
            "sky, horizon, white background, simple background, "
            "holding object, clipboard, armor, helmet, knight, child, "
            "photorealism, 3d render, night"
        ),
        "seed": 20260816,
    },
    # ======================================================================
    # 2026-08-17, THE THREE REMAINING GUARD PLATES: 05, 10 AND 09.
    # PROMPTS AND BARS BOTH WRITTEN AND COMMITTED BEFORE A SINGLE PIXEL.
    # ======================================================================
    # WHY THESE THREE AND NOT FOUR. `guard_plates_are_miscast_0816` settles
    # beats 05, 06, 07, 09, 10 and 11 at once: 0 of 17 plate prompts for those
    # beats name any approved-cast attribute and 14 of 17 ask for `bald`, so
    # every guard plate the project owns invented its own man. Beat 11 has now
    # been redrawn and its plate passes 7/7. 06 already ships off a scene plate
    # whose only fault is cast consistency, and 07 is gated (the goblin is in
    # frame -- `corrections_to_the_brief.beat_07_is_not_goblin_free`). 08 IS
    # DELIBERATELY NOT DRAWN HERE: it needs a two-figure guard+goblin reference
    # that does not exist, and inventing the goblin's half of it in a guard
    # lane is exactly the improvisation this whole finding is about.
    #
    # THE CAST IS CLOSED AND IS READ OFF THE SHEET, NOT OFF A PROMPT. Founder,
    # 2026-08-16: "the cast stands as drawn", glasses included. Verified here by
    # OPENING review/ep2-picks/sheets/guard-cast-0816.jpg rather than trusting a
    # description of it:
    #   GUARD A (= "GUARD 1" in the script; beats 05 and 09) -- dark cropped
    #     hair, WIRE-RIM GLASSES, plain tan/beige wrap tunic, WIDE WHITE WAIST
    #     SASH, dark brown cropped trousers, brown boots.
    #   GUARD B (= "GUARD 2", the clipboard guard; beats 06, 10) -- light sandy
    #     hair, cream short-sleeved shirt, WHITE SASH DIAGONALLY OVER ONE
    #     SHOULDER, broad dark-brown wrap skirt, brown boots, TALLER AND
    #     HEAVIER than A.
    # The script assignment is not guessed either: node.md gives beat 09 to
    # "Guard 1" and beat 10 to "Guard 2", and done-definitions'
    # `beats.09.cast_gate_closed_0816` names guard A as the man in 09. So the
    # near man holding the board in 10 is B, and the face in 09 is A.
    # `wire-rim` appears in ZERO prompts repo-wide before these three.
    #
    # THE STRUCTURE IS COPIED FROM (11,3), WHICH IS THE ONLY GUARD PLATE THAT
    # HAS EVER PASSED ITS OWN BAR (7/7, and then 4 of 4 clips off it showed no
    # recurrence of the identity collapse that broke the beat's take). Reused
    # verbatim where it is reusable:
    #   * count tag FIRST (`2boys` / `1boy, solo`), framing tags second --
    #     leading framing tags bind and trailing ones do not.
    #   * `two guard men ... together` as the count clause. This is the
    #     construction that fixed beat 11's count on one sample, and beat 05's
    #     count history is the worst in the project (words have produced 1, 3
    #     and 3+ guards there), so it is not improved on.
    #   * ONE PERSON CLAUSE PER MAN, each holding that man's hair AND his
    #     garments. (11,3) falsified `attribute_merge_law_0816` doing this:
    #     with the body count right and each set inside one clause, hair
    #     colour binds to garment cleanly and the pair does not swap.
    #   * tall grass PLUS a hedgerow, always. The vacancy law says an empty
    #     region with no noun of its own gets filled with the largest noun in
    #     the prompt; the hedgerow gives the upper band a noun in advance.
    #     (11,3) measured 0.47 torsos of largest inscribed flat rectangle
    #     against a 1.0 bar with exactly this pairing.
    #   * `masterpiece, best quality` and nothing more. The style tail was cut
    #     back to the one proven at 70/77 (95d0c6d0) after nine drafts lost
    #     their tail to compress().
    #
    # WHAT IS NOT COPIED, AND WHY EACH NEGATIVE IS AUTHORED FRESH. (11,3) is a
    # REAR view; its negative forbids `face`, `looking at viewer`, `profile`,
    # `from side`, `close-up` and `portrait`. Two of these three plates need a
    # face and one of them IS a close-up. Inheriting that negative would draw a
    # plate fighting itself, which is the landmine documented at the rev merge
    # site and the reason exit 7 exists. So the head-turn terms appear in NONE
    # of the three (no rear views here) and each negative is written against
    # its own framing. Every pair below was checked for a positive/negative
    # collision and measured on the real CLIP tokenizer before this commit:
    # 05 72/77 pos 72/77 neg, 10 72/77 pos 74/77 neg, 09 65/77 pos 69/77 neg.
    #
    # THE ONE DEFECT CARRIED IN FROM BEAT 11, AND THE POSITIVE-SIDE ANSWER ALL
    # THREE GET. (11,3) passes 7/7 with one named defect: a narrow dark strap
    # hangs from guard B's left hand. It survived (11,4) at the same seed with
    # `holding object` AND `clipboard` in the negative -- twice-named and
    # untouched -- so THE NEGATIVE DOES NOT REACH IT. (11,4) also killed the
    # obvious hypothesis: the strap is NOT the homeless sash clause. Anchoring
    # the sash to a visible surface BOUND (a waist sash appeared on both men
    # where r3 had none) AND THE STRAP STAYED, so the two coexist. What r3, r4
    # and every other guard plate share is that THEY NEVER SAY WHAT THE HANDS
    # ARE DOING. An unspecified hand is a region with no noun of its own, which
    # is the vacancy law at the scale of a hand. (11,5) pre-registered that
    # instrument and died before firing it, so it is UNTESTED, not proven --
    # and these three plates are authored from scratch, so they pay none of the
    # re-edit cost that made (11,4) lose guard B's hair colour.
    # THEREFORE, IN ALL THREE: NO HAND IS LEFT UNSPECIFIED. 05 gives both men
    # `arms swinging` (they are jogging; the arms have a job). 10 gives the near
    # man's hands the beat's own prop, `in both hands`. 09 excludes hands from
    # the frame entirely by framing on the face, which is the cheapest form of
    # the same answer. Each is checked at 8x on every hand that is in frame.
    # This is ONE mechanism applied three ways, and it is falsifiable: if a
    # strap, cord or tab still hangs off a SPECIFIED hand, the object is not
    # attributable to hand-vacancy either and that is a real finding.
    #
    # THE SASH GETS A CAMERA-VISIBLE HOME IN ALL THREE, which is the one thing
    # (11,4) positively established. None of these three is a rear view, so
    # A's waist sash and B's shoulder sash are both surfaces the camera sees.
    #
    # WHAT A MAC PLATE IS AND IS NOT EVIDENCE OF. These are drawn on the Mac
    # fleet. The PNG travels forward as the literal first frame the box
    # animates (the box has no text-to-video path), so a verdict on the PICTURE
    # stands. A verdict on the WORDING DOES NOT: same prompt, same negative,
    # same seed, same checkpoint gives MAE 61 of 255 between this renderer and
    # the box's. Nothing below may be cited as "this wording works".
    #
    # ======================================================================
    # AN EIGHTH MEASURE IS RETIRED, 2026-08-17, AND ITS RETIREMENT IS WORTH
    # MORE THAN THE THREE NUMBERS IT PRODUCED. READ THIS BEFORE CITING P5.
    # ======================================================================
    # The vacancy measure the b11 lane validated -- largest INSCRIBED
    # axis-aligned flat rectangle, float64, calibrated by injecting rectangles
    # of known size -- was rebuilt independently for these three plates and
    # reproduces that lane's numbers exactly: b11 r3 comes out at 0.46 torsos
    # against its recorded 0.47, the 400x250 / 200x300 / 105x240 injections
    # recover at 390x240 / 190x290 / 95x230 (the ~10px inward erosion the 11px
    # window predicts), a 60x60 injection correctly loses to a larger real
    # region, and heavy noise yields a largest flat rectangle of ZERO. By every
    # check that lane ran, it is the same working measure.
    #
    # IT STILL GAVE THE WRONG ANSWER ON BEAT 05, AND ONLY THE OVERLAY CAUGHT
    # IT. Beat 05 r1 measures 0.61 torsos, comfortably inside the one-torso
    # bar, so on the number P5 passes. Overlay every flat pixel in magenta and
    # look, as the standing instruction says: 61.4% OF THE FRAME IS FLAT, one
    # continuous empty field from the top band to the bottom, against 34.6%
    # for the b11 plate that passed. The reason the rectangle stays small is
    # that the emptiness is PEPPERED WITH ISOLATED GRASS TUFTS, and any one
    # tuft is enough to break every rectangle that would have crossed it.
    # THE CONNECTED-REGION MEASURE OVER-REPORTED VACANCY BY MEASURING BRUSH
    # SPACING; THE INSCRIBED-RECTANGLE MEASURE UNDER-REPORTS IT BY LETTING A
    # FIVE-PIXEL MARK VETO A HOLE THE SIZE OF A MAN. Both are wrong in
    # opposite directions on a sparse field, and the second one is worse
    # because it fails in the direction of a PASS.
    # SECOND FAILURE, ON A DIFFERENT PLATE AND A DIFFERENT MECHANISM: on beat
    # 09's close-up the overlay shows the flat regions are the man's CHEEK,
    # HAIR AND COLLAR, and the largest rectangle sits on his face. A
    # flat-region measure on a close-up measures the SUBJECT, not the world,
    # and cannot speak to "is there a real background" at all. Beat 09's P4 is
    # therefore judged by eye on the background region only, and the number is
    # not cited for it.
    # SO: P5 IS NOT SCORED FROM THE RECTANGLE ALONE ON ANY OF THESE THREE.
    # What is reported is the rectangle, the overall flat FRACTION with b11
    # r3's 34.6% as the calibration point, and the overlay, and where they
    # disagree the overlay wins. No replacement measure is invented here under
    # time pressure -- eight have been retired this week and a ninth guessed at
    # in an hour would be the same mistake with a new name.
    #
    # ======================================================================
    # THE SEED SWEEP, AND ITS DECISION RULE, WRITTEN BEFORE ANY OF THE NINE
    # RENDERS EXISTS. This is the one thing that must not be skipped.
    # ======================================================================
    # THE CONFOUND IS THIS LANE'S OWN AND IT IS THE SAME ONE THAT WAS BROKEN
    # YESTERDAY. bf79e534: four wordings had 'established' that guard B turns
    # his head, and all four ran seed 20260817; three fresh seeds of the
    # byte-identical job showed the back turned in 2 of 3, so the head turn was
    # A SEED EFFECT and four wordings had been arguing with one draw. ALL
    # THREE PLATES ABOVE RAN SEED 20260817. Two of them independently returned
    # "both men dark-haired, glasses on both, no sandy hair anywhere", which
    # looks like a law about the checkpoint and is equally consistent with a
    # law about one draw. Building a wording ladder on it now would be the
    # confound rebuilt one day after it was dismantled.
    # So: THREE FRESH SEEDS OF EACH BYTE-IDENTICAL PROMPT, one beat per
    # machine, before any wording changes. Seeds 20260817-20260819 via
    # `--seeds 3 --i-have-seen-a-sample` (one sample HAS been seen and judged
    # for each, which is the only thing that flag may ever mean). s1 re-renders
    # seed 20260817 on the same machine, which is a free determinism check
    # against the sha256 already recorded: 05 da5637c8..., and a mismatch would
    # invalidate every comparison in this file.
    #
    # THE RULES, AND EACH NAMES BOTH OUTCOMES:
    #   D1 SANDY HAIR. Bound on at least ONE of the three fresh seeds of 05 or
    #      10 -> the two-figure identity failure is a seed effect, the person
    #      clauses are not the cause, and the next rung is a SEED BATCH, not a
    #      rewording. Bound on NONE of six -> it is the wording, and the
    #      specific suspect is stated in advance so it cannot be invented
    #      afterwards: FOUR-TO-FIVE ATTRIBUTES PER PERSON CLAUSE against
    #      (11,3)'s TWO, in a broken-up comma list against its strictly
    #      parallel `one man with HAIR in a GARMENT`. The r2 test would then be
    #      to cut back to two attributes per man in that exact shape -- which
    #      COSTS CAST ATTRIBUTES, so it is a trade to be made deliberately and
    #      with the founder's frozen wardrobe named as the thing being traded.
    #   D2 GLASSES BLEEDING ONTO BOTH MEN. On all three fresh seeds of both
    #      two-figure plates -> `glasses` over-applies across same-species
    #      figures on this checkpoint and belongs only in a ONE-FIGURE plate,
    #      which is a real constraint on beats 05 and 10 and a green light for
    #      09. On some and not others -> seed, and it is not a constraint.
    #   D3 THE UNSPECIFIED HAND. Beat 10's far man grew a bamboo pole with
    #      `weapon` in the negative while beat 05's four specified hands came
    #      back empty. If 10's far man is holding something at 2 or 3 of 3
    #      fresh seeds while 05's hands stay empty at 2 or 3 of 3, THE
    #      HAND-VACANCY LAW IS SUPPORTED with a matched control, and the rule
    #      that carries to every future plate is: NAME WHAT EVERY HAND IN
    #      FRAME IS DOING. If 05's hands also grow objects, the law is wrong
    #      and it is written down as wrong.
    #   D4 THE HIGH ANGLE AND THE MISSING HEDGEROW on beat 05. If the camera
    #      is high and the hedgerow absent at all three fresh seeds, that is
    #      the wording, and the stated suspect -- again, in advance -- is that
    #      `sky, horizon` in the negative of a FRONT-FACING wide shot leaves
    #      the camera nowhere to put a horizon except above the frame, so it
    #      tilts down. (11,3) does not pay this because its subjects walk away
    #      and the grass fills the frame regardless. Absent at some seeds only
    #      -> seed, and nothing is concluded.
    #   D5 BEAT 09's EYES. Shut at all three fresh seeds -> `thoughtful` plus
    #      `mouth closed` is a wording that renders a resting face, and the
    #      r2 variable is `eyes open` / `looking down in thought`. Open at any
    #      seed -> seed, and beat 09 needs a seed batch rather than a rewrite.
    # NOTHING IS PICKED FROM THIS SWEEP AND NO PLATE IS PROMOTED BY IT. Its
    # entire job is to say which of five faults are properties of a wording
    # and which are properties of one draw, so that the seeds that follow are
    # spent on the right thing.
    #
    # ======================================================================
    # THE SWEEP RAN. NINE RENDERS, THREE MACHINES, ~7 MINUTES OF WALL CLOCK.
    # RESULTS AGAINST THE FIVE RULES EXACTLY AS THEY WERE WRITTEN ABOVE.
    # Nothing is picked, nothing is promoted, and no rule is reinterpreted.
    # ======================================================================
    # THE COMPARISON BASE IS SOUND, checked before anything was read out of the
    # pictures. `--seeds 3` re-renders s1 at seed 20260817, and on all three
    # machines that re-render is BYTE-IDENTICAL to the plate committed at
    # 0ac649d5 -- 05 da5637c8..., 10 453a1f83..., 09 5dbb9e8b... So the
    # renderer is deterministic per machine and every difference below is the
    # seed and nothing else.
    #
    #   D1 SANDY HAIR -- IT IS A SEED EFFECT, AND THE RULE SAID SO IN ADVANCE.
    #      `light sandy hair` BOUND on 4 of the 4 fresh-seed two-figure
    #      renders: beat 05 s2 (a plainly blond man beside a black-haired one),
    #      05 s3, beat 10 s2 (platinum), and beat 10 s3 (blond, and there the
    #      cream shirt AND the brown wrap skirt bound to him correctly while
    #      the tan tunic bound to the dark-haired man). THE PERSON CLAUSES ARE
    #      NOT THE CAUSE. The pre-registered suspect -- four-to-five attributes
    #      per clause against (11,3)'s two -- IS WRONG AS AN EXPLANATION OF
    #      THIS FAULT and is recorded as wrong. Seed 20260817 alone returned
    #      two dark-haired men from BOTH prompts, which is what made it look
    #      like a law.
    #      THIS IS THE SECOND TIME IN TWO DAYS THAT SEED 20260817 HAS
    #      MANUFACTURED A FALSE LAW. bf79e534 broke the first one (four
    #      wordings, four turned heads, one seed). A lane that had skipped
    #      straight to r2 here would have rewritten the person clauses, thrown
    #      away cast attributes to do it, watched sandy hair "come back", and
    #      banked a third false law on top of the other two.
    #   D2 GLASSES BLEEDING ONTO BOTH MEN -- IT IS THE WORDING, AND IT IS A
    #      REAL CONSTRAINT ON BEATS 05 AND 10. Both men wear glasses in every
    #      two-figure render where the faces are legible: 05 s1, 05 s2, 10 s1,
    #      10 s2, 10 s3 -- 5 of 5. `glasses` was attached to exactly one person
    #      clause in both prompts. So on this checkpoint an eyewear tag
    #      OVER-APPLIES ACROSS TWO SAME-SPECIES FIGURES even when hair and
    #      garments separate cleanly at the same seed, which is a sharper fact
    #      than "attributes do not bind": THESE attributes bind and THAT one
    #      spreads. Consequence, stated plainly: guard A's wire-rims cannot be
    #      named in a two-guard plate without putting them on guard B too, so
    #      either they are left out of 05 and 10 and the beats rely on 09's
    #      close-up to carry them, or guard B is drawn wearing them and the
    #      founder is told. THAT IS A CAST QUESTION AND IS NOT THIS LANE'S
    #      CALL -- it is the first thing the founder should be asked about
    #      these plates.
    #   D3 THE UNSPECIFIED HAND -- SUPPORTED, WITH ITS MATCHED CONTROL, AT
    #      2 OF 3 AGAINST 0 OF 3. Beat 10's far man, whose hands no clause
    #      mentions, holds a BAMBOO POLE at s1 and a DUPLICATE OF THE BOARD at
    #      s2; at s3 his hands are CLASPED TOGETHER and empty. Beat 05, whose
    #      four hands are all covered by `arms swinging`, comes back with
    #      nothing in any hand at all three seeds. Reported as 2 of 3 and not
    #      as a law without exceptions, because the exception is real and is
    #      itself informative: left alone, the model either puts an object in
    #      the hand or invents a pose for it, and naming the pose is the same
    #      instrument either way. This is the finding promoted into this file's
    #      DOCSTRING, where a plate author meets it before writing a prompt.
    #   D4 THE HIGH ANGLE AND THE MISSING HEDGEROW -- IT IS THE WORDING,
    #      3 OF 3. Every beat 05 render is a downward high-angle across an open
    #      field with no horizon band and no hedgerow behind anyone; s3 is so
    #      high and so far that it also breaks the count to THREE FIGURES,
    #      which is beat 05's historical Q2 firing again with `distant, small
    #      figure` in the negative. The pre-registered suspect stands and is
    #      not softened: `sky, horizon` in the negative of a FRONT-FACING wide
    #      shot leaves the camera nowhere to put a horizon except above the
    #      frame, so it tilts down until the horizon is gone -- and a `hedgerow
    #      behind` needs a horizon to stand on. (11,3) never paid this because
    #      its men walk away and grass fills the frame regardless. The r2
    #      variable for beat 05 is therefore ONE THING: drop `horizon` from the
    #      negative (keeping `sky`) so the camera can hold eye level. Nothing
    #      about the person clauses is touched, because D1 just showed they are
    #      not the problem.
    #   D5 BEAT 09'S EYES -- IT IS THE WORDING, 3 OF 3 SHUT. `thoughtful` plus
    #      `mouth closed` renders a man RESTING, not thinking, at every seed.
    #      The r2 variable is `eyes open` in the positive and `closed eyes` in
    #      the negative. One variable, and it is the only change beat 09 needs
    #      to try next.
    #
    # AND FOUR THINGS THE SWEEP SETTLED THAT NO RULE ASKED ABOUT, recorded
    # because a seed sweep is the only cheap chance to learn them:
    #  1. `wire-rim glasses` BINDS AT 3 OF 3 on beat 09, as unmistakable round
    #     silver wire frames every time, never sunglasses and never goggles.
    #     The founder's ruling has landed in a picture.
    #  2. BEAT 09'S RECORDED FAULT IS CLEARED AT 3 OF 3. Tall grass, seed heads
    #     and broad leaves fill the background of every one; the beat whose own
    #     plate came back WHITE and was recorded as "another blank background"
    #     now has three that are not.
    #  3. THE BOARD LANDS ON THE WRONG MAN AT 3 OF 3, AND THIS ONE IS NOT THE
    #     SEED. The board clause sits INSIDE guard B's person clause, and the
    #     board went to the dark-haired man alone at s1 and s3 and to BOTH men
    #     at s2. Guard B never held it alone. So a PROP does not bind to the
    #     person clause it is written in the way HAIR and GARMENTS do; it
    #     attaches to whichever figure the model draws first or nearest. That
    #     matches this repo's recorded "a prop attached to the wrong figure in
    #     9 of 12 frames" and it is the real blocker on beat 10's plate -- a
    #     harder one than anything the wording ladder was aimed at, because
    #     beat 10's done_when names WHICH man flips the board.
    #  4. FOOTWEAR DRIFTS TO MODERN SHOES -- white and red SNEAKERS at 05 s2,
    #     05 s3 and 10 s2, sandals elsewhere -- where the cast wears brown
    #     boots. `brown boots` was cut from both prompts for the 77-token
    #     budget and its absence is visible in the pictures. A cast attribute
    #     dropped for tokens does not stay dropped; it gets replaced.
    5: {
        # ------------------------------------------------------------------
        # BEAT 05, "THE PATROL". node.md: "Two PATROL GUARDS jog in and halt,
        # scanning the field. Their armor doesn't match."
        # done_when, done-definitions beats.'05': "two guards jog in together
        # FROM FRAME ONE, stop, and scan; both adult men in tunic and sash;
        # field present at frame one; neither redrawn mid-clip."
        #
        # BOTH MEN AT FRAME 0 IS THE WHOLE JOB OF THIS PLATE. Beat 05 has
        # burned four rounds on the count and words alone have returned one
        # guard, three guards and "four-ish": round 1 had one guard f20-f80
        # and the second arriving at f100, round 2 overshot to THREE at both
        # seeds, round 3's geometry lever did not bind it either. The recorded
        # lever is "COUNT supplied by the plate", and a plate can only supply
        # a count it actually contains, so two whole men stand in frame one.
        #
        # WHY FRONT-ON AND NOT (11,3)'s REAR VIEW. Three reasons, none of them
        # aesthetic. The done_when requires "tunic and sash" to be READABLE,
        # and both sashes are worn on the front -- a rear view is what left
        # beat 11's sash with nowhere visible to be. Guard A's wire-rim
        # glasses cannot exist in a rear view at all. And beat 05 is the beat
        # that INTRODUCES these two men, so the shot the audience meets them
        # in is the one that has to carry their faces.
        #
        # `armor doesn't match` IS IN THE SCRIPT AND IS DELIBERATELY NOT DRAWN.
        # The approved cast wears no armour; `armor, helmet, knight` are in
        # the negative here as they are in every guard prompt, and the joke
        # line does not override "the cast stands as drawn". Flagged, not
        # silently dropped.
        #
        # PLATE BAR, PRE-REGISTERED. All seven must hold, and good staging
        # with the wrong men is a FAIL -- identity is the point:
        #   P1 THE APPROVED PAIR, AND NOT SWAPPED. One man dark cropped hair
        #      + tan tunic + white waist sash; ONE MAN TALLER with light sandy
        #      hair + cream shirt + white shoulder sash + brown wrap skirt.
        #      NEITHER BALD. Judged against guard-cast-0816.jpg.
        #   P2 EXACTLY TWO WHOLE FIGURES, full-length, no third body. Top and
        #      bottom bands cropped and swept separately, because beat 05's
        #      failure mode is specifically a third man.
        #   P3 BOTH FACES VISIBLE AND FORWARD, neither man's back to camera.
        #   P4 the taller man spans >=25% of frame height, so the costumes are
        #      legible at all.
        #   P5 NO FLAT UNTEXTURED REGION LARGER THAN A TORSO, measured with
        #      the float64 largest-inscribed-flat-rectangle measure that was
        #      validated by injecting rectangles of known size, and OVERLAID
        #      back onto the frame before the number is believed.
        #   P6 NOTHING HANGS FROM ANY OF THE FOUR HANDS -- no strap, cord,
        #      lanyard, tab or pendant -- and nothing detached anywhere in
        #      frame. Judged at 8x on every hand, never at 1x: at 1x beat 11's
        #      strap is a two-pixel line and two revisions "passed" it by not
        #      being looked at closely enough. A SASH IS NOT A FAIL OF P6.
        #   P7 FIELD PRESENT IN THE PLATE ITSELF, since the beat's own
        #      done_when demands it at frame one.
        #   P8 GLASSES ON THE DARK-HAIRED MAN, or their absence named. At this
        #      framing they are a handful of pixels, so this is scored as
        #      PRESENT / ABSENT / NOT LEGIBLE and NOT LEGIBLE is not a pass.
        # FAIL MODES NAMED IN ADVANCE: Q1 bald pair, Q2 wrong count (the
        # historical one), Q3 backs turned, Q4 costume swap (sandy hair takes
        # the tan tunic), Q5 vacancy, Q6 a hanging strap, Q7 armour arriving
        # off the script line, Q8 both men the same height.
        "slug": "the-patrol",
        "done_when": (
            "two guards jog in together FROM FRAME ONE, stop, and scan; both "
            "adult men in tunic and sash; field present at frame one; neither "
            "redrawn mid-clip. THE PLATE'S JOB: supply the COUNT, the WORLD "
            "and the CAST at frame zero, since four rounds of words have "
            "returned 1, 3 and 3+ guards. P1 approved pair not swapped, "
            "P2 exactly two whole figures, P3 both faces forward, P4 taller "
            "man >=25% of frame height, P5 no flat region larger than a "
            "torso, P6 nothing hanging from any of the four hands judged at "
            "8x, P7 field in the plate, P8 glasses present or their absence "
            "named. Good staging with the wrong men is a FAIL."
        ),
        "why": (
            "Beat 05 introduces both guards and every plate it has ever had "
            "was mis-cast: its own six prompts are all of the 'two round "
            "guard men ... silly harmless bureaucrats with round soft bodies "
            "and bare heads' family, and neither approved guard is bald. The "
            "recorded shipping fault, 'the two guards read younger and "
            "softer-drawn than the guards in beats 06 and 11', was filed as a "
            "taste call and is not one -- it is that no guard plate names the "
            "cast, so each beat improvised a different man. This is the first "
            "staged picture of the APPROVED pair arriving in a field, drawn "
            "front-on because the sashes and guard A's wire-rim glasses only "
            "exist on the side of him a rear view cannot see."
        ),
        "prompt": (
            "2boys, full body, wide shot, two guard men jogging together in "
            "tall grass, hedgerow behind, one man with dark cropped hair, "
            "glasses, a tan tunic and a white waist sash, one taller man "
            "with light sandy hair, a cream shirt, a white shoulder sash and "
            "a brown wrap skirt, arms swinging, masterpiece, best quality"
        ),
        # AUTHORED FOR THIS FRAMING, NOT INHERITED. (11,3)'s head-turn block
        # (`looking back, profile, from side`) and its `face` and `portrait`
        # terms are ABSENT ON PURPOSE: this plate needs two faces. What is
        # kept from it is the count block (`1boy, 3boys, solo`), the anti-bald
        # block, the vacancy block (`sky, horizon, white background, simple
        # background`) and the anti-armour block. `holding object, clipboard`
        # stay even though they have been shown not to reach a hanging strap
        # -- they do stop a whole clipboard arriving in beat 05, where the
        # script gives neither man a prop yet.
        "negative": (
            "text, bald, bare head, 1boy, 3boys, solo, crowd, girl, child, "
            "from behind, back view, close-up, portrait, distant, small "
            "figure, sky, horizon, white background, simple background, "
            "armor, helmet, knight, weapon, holding object, clipboard, "
            "photorealism, 3d render, night"
        ),
        "seed": 20260817,
        # ------------------------------------------------------------------
        # R1 VERDICT, 2026-08-17. macbook1 (M1 Max, 1.73 s/step, 73.0s),
        # seed 20260817, png sha256 da5637c8...  FIVE OF EIGHT FAIL.
        # Judged by opening the PNG and then 4x-5x crops of both men's hands,
        # the far man's hip and both heads, against the bar committed above
        # before it was drawn. Nothing is re-scoped.
        #   P1 APPROVED PAIR ......... FAIL, and this is the important one.
        #      BOTH MEN CAME BACK DARK-HAIRED AND BOTH WEAR GLASSES. The far
        #      man is guard A and is correct -- dark cropped hair, wire-rim
        #      glasses, tan tunic, white waist sash. The near man is a SECOND
        #      dark-haired bespectacled man in a full-length WHITE robe with a
        #      NAVY waist sash: `light sandy hair` did not bind at all, the
        #      `cream shirt` became a floor-length robe, the `brown wrap
        #      skirt` is absent, and the `white shoulder sash` became a dark
        #      waist sash. Guard B is simply not in this picture.
        #   P2 two whole figures ..... MARGINAL PASS. Exactly two, no third
        #      body in either band, but the far man's legs end in a stump with
        #      a boot-shaped blob and his feet are not resolved.
        #   P3 faces forward ......... PASS. Both faces front-on, no back
        #      turned. (Both are also mouth-open and eyes-shut, on which see
        #      the pose failure below.)
        #   P4 taller man >=25% ...... PASS on the number, ~41% for the near
        #      man, MEANINGLESS AS WRITTEN: "the taller man" cannot be
        #      identified when the taller man is not in the frame.
        #   P5 vacancy ............... THE MEASURE FAILED HERE AND THE MEASURE
        #      IS WHAT IS REPORTED FIRST. See the note at the end of this
        #      block. By eye this field is VACANT and P5 FAILS.
        #   P6 nothing hanging ....... PASS, AND IT IS THE ONE CLEAN RESULT ON
        #      THIS PLATE. All four hands opened at 4x-5x: guard A's two are
        #      closed empty fists, the near man's two are open and empty, and
        #      the dark shape at guard A's hip is his own trouser-and-boot
        #      mass, not a strap. NO STRAP, NO CORD, NO TAB, NOTHING DETACHED
        #      ANYWHERE. Beat 11's defect did not recur on a plate where both
        #      men's arms were given a job.
        #   P7 field in the plate .... PASS.
        #   P8 glasses ............... PASS ON THE DARK-HAIRED MAN and then
        #      OVER-APPLIED: the glasses are unmistakable wire-rims at 4x, and
        #      they are also on the man who should not have them. Recorded as
        #      P8 pass, P1 fail, because that is what the two conditions say.
        # UNPRE-REGISTERED FAILURES, named because they are real and were not
        # anticipated: THE POSE IS WRONG -- `arms swinging` came back as both
        # men flinging their arms wide and overhead with mouths open, which
        # reads as a cheer, not a jog. And THE CAMERA WENT HIGH-ANGLE: the
        # `hedgerow behind` did not render at all, there is no horizon band,
        # and the men are seen from above across an open field.
        # ------------------------------------------------------------------
    },
    10: {
        # ------------------------------------------------------------------
        # BEAT 10, "NO FORM". node.md: "Guard 2 flips the clipboard around:
        # the back is blank."
        # done_when, done-definitions beats.'10': "TWO guards in frame; the
        # near one flips the bark board and holds its blank back TOWARD HIS
        # PARTNER; board hand-sized; field present at frame one."
        #
        # THIS PLATE IS NOT PROMISED TO WORK IN MOTION AND THAT IS SAID HERE
        # RATHER THAN IN A REPORT. Beat 10's action is a SMALL IN-HAND PROP
        # MANIPULATION, which is the one thing this engine measurably drops:
        # twelve beat-17 cells gave 12 of 12 whole-body stand-ups and 0 of 8
        # in-hand brushes ON THE SAME PLATE, and all four `full` cells stand
        # and turn while none brushes. The composition claim that a tight
        # insert would fix it -- make the action the largest movement in frame
        # -- WAS KILLED: it reproduced 0 of 4. So no composition promise is
        # made here. A CORRECT PLATE IS STILL WORTH DRAWING, because the plate
        # supplies count, world and cast, which are three of beat 10's four
        # conditions and are exactly what its round-3 seeds split between
        # them; the flip is the fourth and it remains a lottery.
        #
        # THE BOARD IS DRAWN IN ITS *PRE* STATE, and this is a deliberate
        # structural choice with a receipt. Twenty-four candidates failed on
        # "pushes himself up to standing" because THIS CHECKPOINT RENDERS A
        # VERB'S END STATE: a plate that said "flipping" would come back
        # mid-flip or finished, with nowhere left to travel. So the board is
        # held in both hands with its written face toward the near man -- the
        # state beat 06 ends in and beat 10 begins in -- and the whole of the
        # flip is left for the animator.
        #
        # SIZE-IN-FRAME, HONESTLY BOUNDED. `medium shot` replaces (11,3)'s
        # `wide shot` and `large flat bark board` replaces a hand-sized one,
        # so the near man's body and the board are as big as they can be while
        # a second whole man is still in frame. That is a legibility argument
        # about the PLATE, not the retired composition claim about MOTION.
        # The board is asked to be LARGE while beat 10's own done_when says
        # `board hand-sized`: those are compatible -- hand-sized held forward
        # at a medium shot IS large in frame -- but if the render returns a
        # slab instead of a board, that is a P-condition failure and is scored
        # as one. The prop-inflation risk is known and named: wave-drafts
        # records `filling the lower third` as the construction motion-wave
        # measured inflating props into slabs, which is why that wording is
        # NOT used here.
        #
        # THE NEAR MAN IS GUARD B AND THAT IS NOT A GUESS. node.md gives this
        # line to GUARD 2, wave-drafts derives guard B carrying "the bark
        # clipboard, which is also the prop the script gives the clipboard
        # guard", and beat 06's board beat is Guard 2's as well. B is also the
        # taller and heavier man, which is what puts him nearest camera.
        #
        # PLATE BAR, PRE-REGISTERED. All eight must hold:
        #   P1 THE APPROVED PAIR, NOT SWAPPED, AND THE BOARD ON THE RIGHT MAN.
        #      NEAR: light sandy hair, cream shirt, white shoulder sash, brown
        #      wrap skirt, taller. BEHIND: dark cropped hair, tan tunic.
        #      NEITHER BALD. THE BOARD MUST BE IN THE SANDY-HAIRED MAN'S
        #      HANDS. A prop on the wrong figure is the recorded failure of
        #      this checkpoint -- 9 of 12 frames in one round -- so this is
        #      scored separately and a board on the dark-haired man is a FAIL
        #      even if everything else holds.
        #   P2 EXACTLY TWO WHOLE FIGURES, no third body.
        #   P3 THE NEAR MAN'S FACE AND HANDS BOTH IN FRAME. The flip needs the
        #      hands; the cast needs the face.
        #   P4 the near man spans >=45% of frame height (higher than beat 05's
        #      25% because this plate's argument is legibility of a prop).
        #   P5 NO FLAT UNTEXTURED REGION LARGER THAN A TORSO, measured with
        #      the validated float64 measure and overlaid before believed.
        #   P6 NOTHING HANGS FROM ANY HAND that is not the board itself -- no
        #      strap, cord, lanyard or tab. Judged at 8x on all four hands.
        #   P7 FIELD PRESENT IN THE PLATE ITSELF.
        #   P8 ONE BOARD, FLAT, UNOCCLUDED, HELD IN TWO HANDS, and readable as
        #      a hand-held bark board rather than a sign, banner, slab, page
        #      or book. Its written face toward the near man, its blank back
        #      NOT yet toward the partner -- a plate that has already flipped
        #      it is a FAIL, because the beat would have nowhere to go.
        # FAIL MODES NAMED IN ADVANCE: Q1 bald pair, Q2 wrong count, Q3 the
        # board on guard A, Q4 costume swap, Q5 vacancy, Q6 a hanging strap,
        # Q7 the board inflated into a slab or turned into a sign with text,
        # Q8 the board already flipped, Q9 the near man's hands cropped out.
        "slug": "no-form",
        "done_when": (
            "TWO guards in frame; the near one flips the bark board and holds "
            "its blank back TOWARD HIS PARTNER; board hand-sized; field "
            "present at frame one. THE PLATE'S JOB IS COUNT, WORLD, CAST AND "
            "THE PRE-FLIP BOARD -- NOT A PROMISE ABOUT MOTION: this beat's "
            "action is a small in-hand manipulation, which measures 0 of 8 "
            "in-hand against 12 of 12 whole-body, and the composition fix for "
            "it reproduced 0 of 4. P1 approved pair not swapped AND the board "
            "in the sandy-haired man's hands, P2 exactly two whole figures, "
            "P3 near man's face and hands both in frame, P4 near man >=45% of "
            "frame height, P5 no flat region larger than a torso, P6 nothing "
            "hanging from any hand but the board, P7 field in the plate, "
            "P8 one flat unoccluded bark board in two hands, NOT yet flipped."
        ),
        "why": (
            "Beat 10's four rounds split its conditions across seeds -- seedA "
            "had the pair and the world but the board faced camera instead of "
            "the partner and the caps drifted off-cast, seedB read the blank "
            "back perfectly with only one guard -- and its two plate prompts "
            "are 'two round bald guard men in plain brown tunics ... silly "
            "bureaucrats' and 'two bald guard men in plain brown tunics'. "
            "Neither names the cast and neither approved guard is bald, which "
            "is the whole of the recorded 'same guard-consistency fault as "
            "beat 05'. This plate supplies count, world and cast correctly "
            "and stages the board in its pre-flip state. It does NOT claim "
            "the flip will animate; that is a one-in-four lottery on this "
            "engine regardless of the plate, and saying so is the point."
        ),
        # PROP-SIZE CORRECTION, 2026-08-18, AND IT IS THE ONLY CHANGE HERE.
        # `a large flat bark board` -> `a hand-sized bark board`. The 08-18
        # Mac sample came back with the board as a PLAIN PLANK, and this
        # beat's own `done_when` says "board hand-sized" -- the prompt was
        # literally asking for the defect. Nothing else moves: seed, cast
        # clauses, framing and the whole negative are byte-identical to r1.
        #
        # NO GOBLIN IS ADDED TO THIS BEAT, and that is a deliberate refusal.
        # The 08-18 plate card in review/inbox.yaml lists beat 10 as "no
        # goblin at all" alongside beats 08 and 20 as one cast defect. IT IS
        # NOT ONE. node.md 0:45-0:50 is "Guard 2 flips the clipboard around:
        # the back is blank"; this beat's `done_when` reads "TWO guards in
        # frame ... holds its blank back TOWARD HIS PARTNER"; and
        # done-definitions `figure_count_ruled_from_the_script_0817` uses
        # BEAT 10 AS THE CONTROL that proves the actor-plus-target rule --
        # "the target of beat 10's gesture IS the partner", Guard 1, who asked
        # the question in beat 09. A goblin here would be a third body in a
        # two-guard shot and would break the count condition to fix a fault
        # this beat does not have. The card's own line invites this: "stop me
        # if the read is wrong."
        # Measured: 73/77 positive, 74/77 negative, exit 7 clean.
        "prompt": (
            "2boys, full body, medium shot, two guard men standing together "
            "in tall grass, hedgerow behind, near taller man with light "
            "sandy hair, cream shirt, white shoulder sash, brown wrap skirt, "
            "holding a hand-sized bark board in both hands, one man behind "
            "with dark cropped hair, glasses, a tan tunic, masterpiece, "
            "best quality"
        ),
        # AUTHORED FOR THIS FRAMING. `holding object` and `clipboard` are
        # ABSENT, and their absence is the one real difference from beat 05's
        # negative: this beat's subject IS a held board, so forbidding held
        # objects would be the self-contradiction exit 7 exists to catch, one
        # synonym away from tripping it. What replaces them is a block against
        # the WRONG BOARD -- `sign, banner, paper, book` -- since the recorded
        # failure is the prop becoming a slab or a titled sign, not the prop
        # being absent. `text` covers writing appearing on it.
        "negative": (
            "text, bald, bare head, 1boy, 3boys, solo, crowd, girl, child, "
            "from behind, back view, close-up, portrait, distant, small "
            "figure, sky, horizon, white background, simple background, "
            "armor, helmet, knight, weapon, sign, banner, paper, book, "
            "photorealism, 3d render, night"
        ),
        "seed": 20260817,
        # ------------------------------------------------------------------
        # R1 VERDICT, 2026-08-17. macbook2 (M1 Pro, 139.9s), seed 20260817.
        # THREE OF EIGHT FAIL, and one of the failures is the most useful
        # result this lane produced.
        #   P1 APPROVED PAIR + BOARD ON THE RIGHT MAN ... FAIL TWICE OVER.
        #      Both men are BLACK-HAIRED and both wear glasses, exactly as in
        #      beat 05 off a different prompt. `light sandy hair` bound on
        #      neither figure. Worse for this beat specifically: THE BOARD IS
        #      IN THE HANDS OF THE MAN WEARING GUARD A's TAN TUNIC, i.e. the
        #      near man took A's costume and B's prop, and the far man got an
        #      olive robe belonging to nobody. Q3 was pre-registered as a fail
        #      on its own and it fired.
        #   P2 two whole figures ..... PASS, both full-length, no third body.
        #   P3 near man's face+hands . PASS, both in frame and unoccluded.
        #   P4 near man >=45% ........ PASS, ~72% (y270 to y1150 of 1216).
        #   P5 vacancy ............... PASS, 0.44 torsos, AND THE OVERLAY
        #      AGREES for once: the flat pixels sit on the garments and the
        #      skin, and the grass texture runs across the whole upper band.
        #      This is the best world of the three plates.
        #   P6 nothing hanging but the board ... FAIL, AND THE WAY IT FAILED
        #      IS EVIDENCE FOR THE HAND-VACANCY LAW RATHER THAN AGAINST IT.
        #      The near man's hands were the only ones this prompt specified
        #      (`in both hands`) and they hold exactly what they were told to.
        #      THE FAR MAN'S HANDS WERE NOT SPECIFIED, AND THEY CAME BACK
        #      HOLDING A LARGE BAMBOO POLE that no clause asked for, with
        #      `weapon` sitting in the negative. Read against beat 05, where
        #      BOTH men's arms were given a job and all four hands came back
        #      empty, this is a matched pair: specified hands stayed empty or
        #      held the right thing, the one unspecified pair grew an object.
        #   P7 field in the plate .... PASS.
        #   P8 one flat unoccluded board, not yet flipped ... PASS ON FORM.
        #      One board, flat, rectangular, bark-brown, no text, held in two
        #      hands, unoccluded, and NOT flipped -- there is somewhere for
        #      the beat to go. It is on the wrong man, which is P1's failure
        #      and is not double-counted here.
        # NOT PRE-REGISTERED AND NAMED ANYWAY: both men are barefoot or in
        # sandals where the cast wears brown boots, and neither man is
        # noticeably taller than the other.
        # ------------------------------------------------------------------
    },
    9: {
        # ------------------------------------------------------------------
        # BEAT 09, "THE PAUSE". node.md: "Guard 1's face works through it,
        # slowly."
        # done_when, done-definitions beats.09: "close on Guard 1's face
        # working through the thought, in daylight; face holds, no morphing;
        # a real background behind him."
        #
        # THIS IS THE BEAT THE GLASSES QUESTION WAS ACTUALLY ABOUT, and the
        # file says so: `beats.11.glasses_do_not_affect_this_beat_0816` --
        # beat 11 is backs-turned, BEAT 09 IS HIS FACE IN CLOSE-UP.
        # `cast_gate_closed_0816` is explicit about what this plate owes:
        # "GUARD A WEARS WIRE-RIM GLASSES and beat 09's new plate must NAME
        # them, along with the rest of the frozen wardrobe - dark hair, tan
        # wrap tunic, wide white waist sash. The unnamed wire-rims are part of
        # why 'THE FACE CHANGES': a prompt that does not say glasses lets each
        # frame decide." `wire-rim` appears in ZERO prompts repo-wide. It is
        # written out in full here rather than as plain `glasses`, which is
        # what 05 and 10 could afford at their framings -- at a close-up the
        # frame shape is legible and is the thing being frozen.
        #
        # THE RECORDED FAULT IS THE BACKGROUND, AND IT IS FIRST-CLASS HERE.
        # Beat 09's round 1 gave a real world and lost the framing; round 2
        # won the framing at both seeds; round 3 kept the framing and lost the
        # FACE -- "the plate's guard is black-haired and the close-up that
        # follows is a brown-haired different man". And the beat's own scene
        # plate "came back WHITE so it does not help": the recorded fault on
        # the plate itself is *another blank background*. So the background is
        # not a trailing style word here. It is a NAMED NOUN IN THE POSITIVE
        # -- `tall grass and a green hedgerow behind him` -- and FIVE separate
        # blank-background terms sit in the negative. This is the vacancy law
        # applied where it has actually bitten this beat.
        #
        # WHY A CLOSE-UP PLATE AT ALL. The recorded lever, verbatim: "a plate
        # that IS a close-up of this guard's face, so identity comes from the
        # reference at the framing the beat actually uses - A FULL-BODY PLATE
        # CANNOT SUPPLY A FACE". Every guard plate the project owns is a full
        # or medium body. This is the first close one.
        #
        # THE HANDS ARE SOLVED BY EXCLUSION, which is the cheapest form of the
        # answer the other two plates give positively. Beat 11's strap hangs
        # from an unspecified hand; a face-filling frame has no hand in it to
        # put anything in. `hands` is in the negative as well, and that is
        # belt-and-braces rather than the instrument -- the negative has now
        # failed three times on nouns the POSITIVE invited, and this positive
        # invites no hand at all.
        #
        # `mouth closed` IS IN THE POSITIVE FOR A MEASURED REASON. Beat 11's
        # best take turns guard B's head "into full profile WITH AN OPEN
        # MOUTH" from f008; the checkpoint animates a talking man's head.
        # Beat 09 is a man thinking BEFORE he speaks, so the plate starts
        # closed-mouthed and gives the line somewhere to arrive from.
        #
        # PLATE BAR, PRE-REGISTERED. All seven must hold:
        #   P1 GUARD A AND NOT A STRANGER: dark cropped hair, WIRE-RIM
        #      GLASSES ON HIS FACE, an adult man's face. Judged against
        #      guard-cast-0816.jpg. NO GLASSES IS A FAIL OF P1, not a note --
        #      this is the beat whose whole problem is that the wardrobe was
        #      never written down.
        #   P2 EXACTLY ONE FACE, one head, no second figure and no crowd.
        #   P3 THE HEAD FILLS THE FRAME -- head height >=55% of frame height,
        #      measured crown to chin, so this is a face and not the chest-up
        #      medium that failed round 1.
        #   P4 A REAL BACKGROUND: identifiable foliage or grass behind him
        #      across the WHOLE frame, no white, grey, gradient or blank
        #      field, no drawn panel border (round 1 seedB drew a panel).
        #      Measured with the validated float64 flat-rectangle measure AND
        #      overlaid before the number is believed; a close-up has a
        #      shallower background than a wide, so the bar is stated in the
        #      same unit as the others: no flat region larger than a torso.
        #   P5 DAYLIGHT, per the done_when's "in daylight".
        #   P6 NOTHING HANGING ANYWHERE and no hand in frame at all.
        #   P7 MOUTH CLOSED, eyes open, an adult's face working -- not a
        #      finished expression and not mid-speech.
        # FAIL MODES NAMED IN ADVANCE: Q1 no glasses, Q2 blank or panelled
        # background (the recorded fault), Q3 too wide a framing, Q4 a second
        # figure, Q5 a child's or a girl's face, Q6 night or interior light,
        # Q7 mouth open, Q8 the glasses rendered as sunglasses or goggles.
        "slug": "the-pause",
        "done_when": (
            "close on Guard 1's face working through the thought, in "
            "daylight; face holds, no morphing; a real background behind him. "
            "THE PLATE'S JOB: supply GUARD A'S FACE AT THE FRAMING THE BEAT "
            "USES, since a full-body plate cannot supply a face and round 3 "
            "resolved a black-haired plate into a brown-haired stranger. "
            "P1 guard A with WIRE-RIM GLASSES (no glasses is a FAIL), P2 "
            "exactly one face, P3 head >=55% of frame height, P4 a real "
            "foliage background with no flat region larger than a torso and "
            "no panel border, P5 daylight, P6 nothing hanging and no hand in "
            "frame, P7 mouth closed with eyes open."
        ),
        "why": (
            "Beat 09 is recorded CONFUSING, not merely unfinished: 'THE FACE "
            "CHANGES between the first frame and the close-up' at both seeds, "
            "so the drift is the recipe and not one unlucky roll. Two causes "
            "are named in the file and this plate is the first thing to "
            "address either. The framing cause is that no plate this beat has "
            "ever had is a close-up, and identity cannot be carried into a "
            "close-up by a full-body reference. The wardrobe cause is that "
            "guard A's wire-rim glasses are drawn on the approved sheet and "
            "written in no prompt anywhere, so every frame decides them "
            "afresh. `wire-rim` appears in zero prompts repo-wide before this "
            "one. The plate's own recorded fault is a third thing -- 'another "
            "blank background' -- so the background is a named noun in the "
            "positive here and five terms in the negative."
        ),
        "prompt": (
            "1boy, solo, close-up, face filling the frame, a guard man with "
            "dark cropped hair and wire-rim glasses, thoughtful, mouth "
            "closed, a tan wrap tunic collar and a white sash on his "
            "shoulder, tall grass and a green hedgerow behind him, sunny "
            "day, masterpiece, best quality"
        ),
        # AUTHORED FOR A CLOSE-UP, WHICH IS WHY NOTHING HERE IS INHERITED.
        # (11,3)'s negative forbids `close-up`, `portrait` and `face` -- all
        # three of which this plate IS. Inheriting it would have drawn a plate
        # fighting its own negative and the only symptom would be a subtly
        # wrong picture read as a finding about the checkpoint. That is the
        # documented landmine, and exit 7 would have caught this one on
        # `close-up`. What this negative carries instead is the FIVE-TERM
        # BLANK-BACKGROUND BLOCK against the beat's own recorded fault, plus
        # `full body, wide shot, distant` to hold the framing that round 2
        # won, plus `indoors` and `dark, night` for the done_when's daylight.
        "negative": (
            "text, 2boys, 3boys, crowd, bald, hands, holding object, "
            "clipboard, armor, helmet, knight, child, girl, white "
            "background, simple background, grey background, blank "
            "background, plain background, sky, indoors, full body, wide "
            "shot, distant, photorealism, 3d render, dark, night"
        ),
        "seed": 20260817,
        # ------------------------------------------------------------------
        # R1 VERDICT, 2026-08-17. macbook3 (M1 Pro, 139.5s), seed 20260817.
        # THREE OF SEVEN FAIL. This is the closest of the three plates and it
        # clears both faults the beat was actually blocked on.
        #   P1 guard A WITH WIRE-RIM GLASSES ... SPLIT, SCORED AS FAIL.
        #      THE GLASSES BOUND, FIRST TIME IN THIS REPO. At 1x they are
        #      unmistakable round wire-rims with thin dark frames and a visible
        #      bridge -- not sunglasses, not goggles, so Q8 did not fire.
        #      `wire-rim` had appeared in zero prompts repo-wide before this
        #      one and it works. THE HAIR DID NOT: it came back mid-BROWN and
        #      shaggy where guard A's is dark, near-black and cropped, and the
        #      face reads as a teenager rather than an adult man. That is not
        #      a quibble on this beat -- the recorded fault is verbatim "the
        #      plate's guard is black-haired and the close-up that follows is
        #      a brown-haired different man", and this plate IS the
        #      brown-haired man. P1 says guard A and this is not guard A.
        #   P2 exactly one face ...... PASS. One head, no second figure.
        #   P3 head >=55% of frame ... FAIL, ~53% (crown y45 to chin y680 of
        #      1216). A marginal miss and it is not softened; the bar said 55.
        #   P4 REAL BACKGROUND ....... PASS, AND THIS IS THE RECORDED FAULT
        #      CLEARED. The recorded fault on this beat's own plate is
        #      "another blank background" and its scene plate "came back
        #      WHITE". This one has identifiable tall grass, seed heads and
        #      broad leaves across the entire frame, no white, no grey, no
        #      gradient field and no drawn panel border. It is thrown out of
        #      focus, which is a close-up doing what a close-up does, not a
        #      blank. THE MEASURE DOES NOT SUPPORT THIS AND IS NOT CITED FOR
        #      IT -- see the note at the end of this block.
        #   P5 daylight .............. PASS, bright and warm.
        #   P6 nothing hanging, no hand in frame ... PASS. There is no hand in
        #      the frame at all, which was the intent: the cheapest available
        #      form of the hand answer.
        #   P7 mouth closed, EYES OPEN ... FAIL. Mouth is closed as asked, but
        #      BOTH EYES ARE SHUT. `thoughtful` plus a closed mouth landed on
        #      a man with his eyes closed, which is a man not thinking but
        #      resting, and beat 09 is "Guard 1's face works through it".
        # ------------------------------------------------------------------
    },
    14: {
        "slug": "the-defense",
        "done_when": (
            "fingers at the dirt AND the glancing - embarrassment readable. "
            "Requires a plate where his hands and the ground are both in "
            "frame; a standing full-body plate cannot show this and should be "
            "sent back."
        ),
        "why": (
            "The only existing plate (ep2-b14-plate-0814) is exactly the "
            "standing full-body shot the definition says to send back: no "
            "hands, no ground. The beat IS the hands. This plate exists to put "
            "them in frame."
        ),
        # 96/77 on the first draft -- the tokenizer guard caught it before it
        # drew, and an overflow would have dropped the style anchor at the tail.
        "prompt": (
            "1boy, solo, lean wiry adult goblin man, green skin, bald head, "
            "patchwork cloak, crouching low, both clawed hands down at the "
            "bare earth, fingers picking at loose dirt, face turned away, "
            "embarrassed, low close-up, hands and dirt large in frame, "
            "green grass, sunny day, masterpiece, best quality, very aesthetic"
        ),
        "negative": (
            "text, standing, walking, running, full body, wide shot, distant, "
            "holding object, spear, staff, sword, stick, basket, broom, "
            "2boys, baby, child, chibi, stitches, scars, tree, forest, house, "
            "indoors, photorealism, 3d render, dark, night"
        ),
        "seed": 20260814,
    },
    19: {
        # ------------------------------------------------------------------
        # BEAT 19, "THE DROP". node.md (002b-first-citizen:118, commit
        # a483eb52, the author's own 2026-08-15 edit): "the stem lets go, the
        # fig falls, and lands in the grass at his feet. He notices."
        #
        # done-definitions beats.'19'.done_when: "WIDE enough to hold the
        # whole sapling and him at once; the fruit STARTS ON THE STEM, falls,
        # and LANDS ON THE GROUND; and he NOTICES it. Three things, in that
        # order: the fall, the landing, the noticing. NO CONTACT WITH HIS BODY
        # -- a take where the fruit touches him fails this beat now, however
        # well it moves."
        #
        # WHY THIS PLATE EXISTS AT ALL, AND WHY IT IS THE ONLY THING BLOCKING
        # THE BEAT. The beat's own entry ends `status: NO VERDICT YET -- and
        # not renderable until the plate exists`, and beat 19 is one of the
        # four SLATES in review/ep2-demo-0818/sources/picks-0818.yaml. The
        # requirement has been written down since 2026-08-15 under
        # `plate_requirement_0815` and was recorded there as "a requirement,
        # not a job -- the plate still needs commissioning". This is the
        # commissioning.
        #
        # !! THE FIG HANGS. IT DOES NOT LIE IN THE GRASS. This is the single
        # clause that kills every plate the project already owns, and it is
        # quoted rather than paraphrased because a lane briefed to draw "a
        # fallen fig in the grass beside him" would reproduce the exact
        # blocker: `plate_requirement_0815.fruit_must_be_on_the_stem` --
        # "UNCHANGED AND STILL DISQUALIFYING. The fruit has to have somewhere
        # to fall from, so it must be ON THE STEM in the plate. Every beat-19
        # plate we own shows it already lying in the grass, which is exactly
        # why the beat was blocked; the ruling changed where the fruit LANDS,
        # not where it STARTS, so no existing plate is rescued by it. Asking a
        # plate with the fruit already down for a fall is what made fruit
        # materialise in mid-air." The founder's ruling_0815 ("just make the
        # fig fall on the ground and the goblin will notice it") moved the
        # LANDING off his head and onto the ground. It did not move the start.
        #
        # THE HEAD-BOUNCE IS DEAD and nothing here asks for it: `bounces off
        # his head` was superseded on 2026-08-15 by the founder's own second
        # ruling, and `NO CONTACT WITH HIS BODY` is now a disqualifying clause
        # of done_when. That is why this plate stages him AN ARM'S LENGTH
        # CLEAR of the plant and why `holding fruit` and `fruit in hand` are
        # in the negative: the plate must not hand the motion a contact it is
        # forbidden to end in.
        #
        # THE BODY POSITION, AND THIS IS A FLAGGED STEWARD CALL RATHER THAN AN
        # INVENTION. `plate_requirement_0815.body_position` reads "OPEN
        # QUESTION -- FLAGGED, NOT INVENTED. Beat 17 ends with him standing
        # and turned away, so where his body is at the start of beat 19 is not
        # established by anything we hold. ... Do not let a render pick this
        # by default." It is not being picked by default here; it is DERIVED
        # from the two beats that bracket it, and the derivation is written
        # down so the author can overturn it in one line:
        #   * BEAT 20 opens "The scavenger picks the fig up with both hands
        #     and looks up at the bare branch." A man who picks a fig off the
        #     ground with BOTH hands in the next beat is low beside it at the
        #     end of this one. Standing does not hand beat 20 its opening.
        #   * BEAT 14 already renders this character correctly CROUCHING with
        #     his hands down at the earth, so a low pose is the pose this
        #     checkpoint draws him in without a fight.
        #   * `scavenger_in_frame` requires "his face is visible, or becomes
        #     visible when he looks", and a kneeling three-quarter body keeps
        #     the face available without a close-up, which P2 forbids.
        # If the author wants him standing, this draft is one word from it and
        # the plate is redrawn for $0. Nothing downstream is built on it yet.
        #
        # THE FRUIT IS PURPLE, and on this beat that is enforced IN THE WORDS
        # rather than hoped for. Founder ruling 2026-08-16 (done-definitions
        # beats.'20'.colour_ruled_0816): "the fruit should be purple. it
        # should not be that hard to make it purple." RED IS REJECTED and no
        # beat gets an exception. `deep purple` is in the positive because
        # `backend_divergence_probe.py` measured the colour to be a BACKEND
        # property -- same prompt, same seed, the Mac returns purple and the
        # box returns red -- so a Mac plate that comes back purple proves
        # nothing about the box and the word carries the canon either way.
        #
        # THE SAPLING IS TINY AND THAT IS CANON, NOT A STYLE PREFERENCE.
        # style.md's node table, row 002a/b/c: ~40 cm, "two leaves + one thin
        # side-branch", and "the branch is where the fig grew and fell". So
        # the fruit hangs from `its thin side-branch` and not from a stem in
        # the abstract, and `knee-high` is deliberately NOT used -- that is
        # row 004's height (~90 cm) and would be a canon drift. Beat 20's
        # recorded failure is the same defect from the other end: "THE BRANCH
        # IS THE WRONG TREE -- a thick gnarled MATURE-TREE limb ... a dead oak
        # limb overhead is not the branch this fruit fell from", diagnosed
        # there as "the plant improvised per beat rather than described once".
        # `large tree, thick branch, trunk, forest` are in the negative for
        # exactly that, and the positive names the small plant positively,
        # which is the instrument -- the negative is belt-and-braces and is
        # not being relied on. Same for `fruit on the ground`: the working
        # lever is the POSITIVE saying `hanging from its thin side-branch`,
        # because the recorded lesson on this checkpoint is that the negative
        # has repeatedly failed on nouns the positive itself invited.
        #
        # THE CAST WORDING IS BEAT 14'S, CHARACTER FOR CHARACTER: `lean wiry
        # adult goblin man, green skin, bald head, patchwork cloak`. Beat 20
        # was corrected to this same string on 2026-08-18 after `a small
        # goblin boy` drew "A ROUND-HEADED CHIBI CHILD WITH BIG EYES" -- the
        # "cute goblin" the founder rejected on beat 04. This beat gets the
        # adult the founder chose, in the words that already render him, and
        # not a seventh wording of the same man.
        #
        # PLATE BAR, PRE-REGISTERED BEFORE THE DRAW. All seven must hold:
        #   P1 THE FIG IS ON THE PLANT: exactly one fruit, ATTACHED to the
        #      sapling's branch and clear of the ground. A fig resting in the
        #      grass is a FAIL of P1 outright, not a note -- it is the
        #      recorded blocker and no other term can rescue it.
        #   P2 WIDE ENOUGH: the WHOLE sapling (root line to top leaves) AND
        #      the whole of him are inside the frame at once. done_when's
        #      first clause. A crop that loses either end is a FAIL.
        #   P3 NO CONTACT: no part of the fruit or the plant touches his body,
        #      and both his hands are empty and away from the fruit.
        #   P4 HIS FACE IS VISIBLE -- eyes and mouth readable, not the back of
        #      his head and not turned fully away. `scavenger_in_frame`: "a
        #      noticing you cannot see on his face is not one."
        #   P5 THE FRUIT READS PURPLE to a naive eye. Red, maroon, brown or
        #      "reddish purple" is a FAIL, per the founder's 08-16 ruling and
        #      beat 20's C-terms.
        #   P6 THE PLANT IS THE SAPLING: small, thin, a few leaves, rooted in
        #      the ground. A mature tree, a thick limb or a trunk entering the
        #      frame is a FAIL -- beat 20's exact recorded fault.
        #   P7 ONE FIGURE, an adult man's build and face. No second figure, no
        #      child, no chibi.
        # FAIL MODES NAMED IN ADVANCE, each to be reported whether or not it
        # fires: Q1 the fig already on the ground (the blocker), Q2 a crop
        # that loses the top of the plant or his feet, Q3 the fig in his hand
        # or against his body, Q4 his back to the lens, Q5 a red or brown
        # fruit, Q6 a mature tree or an overhead limb, Q7 a chibi child, Q8 no
        # fruit drawn at all, Q9 more than one fruit.
        # ------------------------------------------------------------------
        "slug": "the-drop",
        "done_when": (
            "WIDE enough to hold the whole sapling and him at once; the fruit "
            "STARTS ON THE STEM, falls, and LANDS ON THE GROUND; and he "
            "NOTICES it. NO CONTACT WITH HIS BODY. THE PLATE'S JOB is frame "
            "one of that: P1 exactly one fig ATTACHED to the sapling's branch "
            "and clear of the ground (a fig in the grass is the recorded "
            "blocker and fails outright), P2 the whole sapling and the whole "
            "of him in frame at once, P3 no contact and both hands empty, P4 "
            "his face visible, P5 the fruit reads purple to a naive eye, P6 "
            "the plant is the tiny sapling and not a mature tree or a thick "
            "limb, P7 one adult figure."
        ),
        "why": (
            "Beat 19 is a SLATE in the 0818 cut and its own entry says why: "
            "'not renderable until the plate exists'. Every plate the project "
            "owns puts the fig already in the grass, which is the recorded "
            "blocker -- a fall cannot be shot from a fruit that has already "
            "landed. This plate puts it back on the branch, stages him clear "
            "of the plant so the motion cannot end in the contact done_when "
            "disqualifies, and keeps him low so beat 20 opens where beat 19 "
            "leaves him."
        ),
        "prompt": (
            "1boy, solo, lean wiry adult goblin man, green skin, bald head, "
            "patchwork cloak, kneeling beside a tiny sapling rooted in the "
            "grass, one deep purple fig hanging from its thin side-branch, "
            "his face visible, wide shot, sunny grassy field, cinematic "
            "lighting, masterpiece, best quality, very aesthetic"
        ),
        "negative": (
            "text, 2boys, girl, baby, child, chibi, elf, standing, walking, "
            "close-up, portrait, holding fruit, fruit in hand, fruit on the "
            "ground, large tree, thick branch, trunk, forest, house, indoors, "
            "night, dark, photorealism, 3d render"
        ),
        # ------------------------------------------------------------------
        # r1 SCORED, 2026-08-19, macbook1, 70.6 s, seed 20260819, rc 0.
        # farm-out/ep2-b19-mac-plate-0819/19-the-drop-mac-plate-r1s1.png
        # sha256 3cc0b6bcb67e1527c11d7df0a732e77d7cea68a9d9696dc7468b7cc93be60944
        # (recomputed on the pulled copy, not read off the renderer's word).
        # Opened at full resolution and scored against the seven terms above,
        # exactly as written, before anything was filed on it.
        #
        # VERDICT: FAILS THE BAR, 2 of 7 terms down -- AND IT CLEARS THE ONE
        # DEFECT THAT HAS BLOCKED THIS BEAT SINCE 2026-08-15.
        #
        #   P1 THE FIG IS ON THE PLANT ... FAIL, on the COUNT half only, and
        #      the split matters. ATTACHMENT: won. A round deep-purple fruit
        #      sits at the top of the stalk, well clear of the ground, exactly
        #      where done_when needs it to start. COUNT: lost. Three or four
        #      smaller purple beads are strung down the stem below it. The bar
        #      said "exactly one fruit" and this is not one fruit.
        #   P2 WIDE ENOUGH ........... PASS. The whole plant, tip to root
        #      line, and the whole of him are in frame together. His feet are
        #      behind him under the cloak rather than cropped, and the plant's
        #      base is occluded by grass rather than cut off.
        #   P3 NO CONTACT ............ FAIL, AND THIS IS THE DISQUALIFYING
        #      ONE. HIS HAND IS CLOSED AROUND THE STEM. The fruit itself is
        #      untouched, so the letter of "the fruit touches him" is not
        #      broken -- but the plant is in his fist, and a fig cannot fall
        #      from a stem a man is holding. Q3 fires.
        #   P4 HIS FACE IS VISIBLE ... PASS. Clean profile, eye and mouth both
        #      readable. `scavenger_in_frame` is satisfied.
        #   P5 THE FRUIT READS PURPLE  PASS, unmistakably -- deep violet, no
        #      argument needed. The founder's 08-16 ruling lands on the first
        #      draw on this path, as the Mac's measured purple bias predicted.
        #   P6 THE PLANT IS THE SAPLING  PASS ON THE TERM AS WRITTEN, with a
        #      caveat that is not a soft pass and must not be read as one. The
        #      term forbids a mature tree, a thick limb or a trunk, and none is
        #      present: Q6 did not fire, which is beat 20's recorded fault
        #      absent here. THE CAVEAT: what came back is a lanky flower stalk
        #      taller than his kneeling head, and the fruit hangs from its TIP.
        #      Canon (style.md, row 002a/b/c) is ~40 cm with "two leaves + one
        #      thin side-branch", and "the branch is where the fig grew and
        #      fell". A tip is not a side-branch, and this is the same defect
        #      beat 20 died of from the other end -- the plant improvised per
        #      beat instead of described once. Recorded against P6, not scored
        #      against it, because P6 as written does not ask for the branch.
        #   P7 ONE FIGURE, ADULT .... PASS. One lean, wiry, bald adult goblin.
        #      Beat 14's cast wording holds on a beat it had never been used
        #      on. Q7 did not fire.
        #
        # FAIL MODES, ALL NINE REPORTED AS PROMISED:
        #   Q1 the fig already on the ground ..... DID NOT FIRE. **THIS IS THE
        #      RESULT.** `plate_requirement_0815` records that EVERY beat-19
        #      plate this project owns shows the fruit already lying in the
        #      grass, and that this is "exactly why the beat was blocked". It
        #      is up on the plant here on the first draw. The blocker is
        #      answerable by wording, and that was not known before today.
        #   Q2 crop loses the plant or his feet .. DID NOT FIRE.
        #   Q3 fruit in hand or against his body . FIRED -- via the STEM, not
        #      the fruit. See P3.
        #   Q4 back to the lens .................. DID NOT FIRE.
        #   Q5 red or brown fruit ................ DID NOT FIRE.
        #   Q6 mature tree or overhead limb ...... DID NOT FIRE.
        #   Q7 chibi child ....................... DID NOT FIRE.
        #   Q8 no fruit drawn .................... DID NOT FIRE.
        #   Q9 more than one fruit ............... FIRED. See P1.
        #
        # WHY BOTH FAILURES HAVE THE SAME CAUSE, AND IT IS A LAW THIS FILE
        # ALREADY WROTE DOWN. The header of this module records it from beats
        # 05 and 10: "BEAT 05 specified BOTH men's arms. ... BEAT 10 specified
        # ONLY the near man's." An unspecified limb does not stay still; the
        # model finds it a job. This positive said nothing whatsoever about his
        # hands, so the model gave them the nearest object. `holding fruit` and
        # `fruit in hand` were in the negative and did not save it -- which is
        # the third time in this file the negative has failed on a noun the
        # positive invited, and the reason the r1 comment above said in advance
        # that "the working lever is the POSITIVE". It was right about the
        # fruit's position and it did not apply the same law to the hands.
        # ------------------------------------------------------------------
        "seed": 20260819,
    },
    20: {
        "slug": "evidence",
        # THIS BAR CERTIFIES COLOUR AND NOTHING ELSE, and saying so in advance
        # is the point. A lane on 2026-08-16 confessed to a bar that certified
        # a prop's MATERIAL while never mentioning its SHAPE and scored 8/12
        # passes with 0/12 usable. So: this bar does not look at the goblin's
        # age or proportions, the species of the branch, the direction of his
        # gaze, the count, or the composition. A pass here SHIPS NOTHING.
        "done_when": (
            "COLOUR ONLY. A blind cold reader -- a fresh agent given the frame "
            "and nothing else, no context and no prompt text, asked `what "
            "colour is the fruit?` -- must answer with a word in the PURPLE "
            "family (purple, violet, aubergine, eggplant-purple, plum-purple, "
            "indigo, magenta-purple). PASS requires all of: C1 the reader "
            "finds exactly one fruit in frame at all -- no fruit is a FAIL, "
            "not a pass, because there is then nothing whose colour was "
            "tested; C2 the reader's colour word is in the purple family; C3 "
            "the answer is NOT hedged toward red or brown -- `purplish-red`, "
            "`reddish purple`, `brownish purple` and `maroon-purple` are all "
            "FAIL, because the founder's test is whether it reads purple to a "
            "naive eye, not whether purple is arguable; C4 the reader is "
            "asked BEFORE being told anything about figs, canon or this lane. "
            "Named in advance, the failure modes: Q1 RED SURVIVES (reader "
            "says red, dark red, maroon, burgundy, crimson, wine, brown, "
            "russet) -- the founder's exact rejection, and the next lever "
            "would be a NEGATIVE naming the failure colour, not more positive "
            "adjectives; Q2 BLACK COLLAPSE (reader says black) -- overshoot, "
            "`deep` is the suspect token; Q3 EGGPLANT (reads as a vegetable) "
            "-- already spent on beat 18, do not re-buy it; Q4 GLOWING ORB "
            "(the fault that came back 4 of 4 on the 08-12 round) -- colour "
            "of a light source is not colour of a fruit; Q5 NO FRUIT or more "
            "than one; Q6 THE COLOUR LANDS AND THE BEAT STILL DOES NOT -- "
            "expected, and explicitly NOT a pass for beat 20."
        ),
        "why": (
            "THE FOUNDER RULED THE FRUIT PURPLE, 2026-08-16: `the fruit "
            "should be purple. it should not be that hard to make it "
            "purple.` He is right, and the reason is mechanical rather than "
            "linguistic. The four seeds he rejected "
            "(farm-out/ep2-b20-idfix/20-evidence-wave1-s*.png, task "
            "ep2-b20-idfix-0812, 2026-08-12) were drawn from draft variant "
            "`authored_b20_refresh`, whose prompt -- read out of the frame's "
            "own sidecar, not guessed -- says `raises a RIPE FIG`. There is "
            "no colour word in it anywhere, and its negative bans glowing "
            "eyes, glowing orb, dark and night but nothing red or brown. "
            "BEAT 20 WAS NEVER ASKED FOR PURPLE. Measured on the real CLIP "
            "tokenizer, that prompt was 73/77 and its negative 75/77 -- "
            "nothing was truncated, so the missing colour was missing from "
            "the text, not lost in transit. The purple canon landed 08-13/14 "
            "into three beat-20 drafts (authored_b20_plate 74/77, _scene "
            "73/77, _adult 76/77, all three carrying `deep purple-violet "
            "fig, green at its neck, matte` INTACT in the positive) and not "
            "one of them has ever been rendered -- farm-out/ holds "
            "ep2-b20-idfix, -idfix-r2 and -ipa-frozen-0812 and no "
            "ep2-b20-plate-0814. That purple is reachable at all on this "
            "exact recipe is already evidenced: SAMPLE-b18-purple-fruit-0815"
            ".png, same checkpoint, same 832x1216x40 on MPS, `One small "
            "round purple fruit`, came back unmistakably purple. So r1 here "
            "is the CONTROL -- the failing prompt, byte for byte -- and r2 "
            "changes exactly one noun phrase in it."
        ),
        # r1 = THE CONTROL. Byte-identical to the `prompt:` field of
        # farm-out/ep2-b20-idfix/20-evidence-wave1-s3.yaml, the cell the
        # colour card labels THE PICK. It is here so r2 has something to be
        # one variable away from: the four rejected frames were drawn on CUDA
        # with an IP-Adapter reference this Mac does not have, so they cannot
        # serve as the control for an MPS render and pretending otherwise
        # would make the comparison unattributable.
        #
        # !! CORRECTION 2026-08-16 -- THE SENTENCE ABOVE IS FALSE, AND IT COST
        # FOUR DAYS. The four rejected frames in farm-out/ep2-b20-idfix/ were
        # drawn by `render_wave_sample.py`, WHICH CONTAINS NO IP-ADAPTER CODE
        # OF ANY KIND -- grep it. The IP-Adapter frames are a DIFFERENT
        # directory, farm-out/ep2-b20-ipa-frozen-0812/, written by a DIFFERENT
        # script, `goblin_ipa_sample.py`, at scale 0.6 against reference
        # 04-the-footnote-wave1-s0.png. Two render sets were conflated.
        #
        # WHY THE ERROR MATTERS MORE THAN THE FACT. This comment did not merely
        # record something untrue; IT FORBADE AN INVESTIGATION. Believing the
        # 08-12 frames could not serve as a control, no lane ever compared them
        # to an MPS render -- and that one comparison was the whole answer. The
        # prompts are BYTE-IDENTICAL in positive and in negative, and r1's seed
        # 20263739 IS one of the four 08-12 seeds (s3). So the colour word was
        # never the variable and never could have been, and three purple frames
        # were about to be read as proof that it was.
        #
        # This is a distinct failure from the five "a decision moved and the
        # records did not" instances in pipeline/canon.yaml. Those were records
        # that went STALE. This is a record that was WRONG AND LOAD-BEARING --
        # it closed a door and the door stayed closed because the note on it
        # sounded like it had already been tried.
        #
        # WHAT THE COMPARISON ACTUALLY SHOWED, measured in
        # `pipeline/backend_divergence_probe.py` (read its docstring): same
        # prompt, same seed, same everything, the Mac returns PURPLE and the
        # box returns RED. Precision is exonerated (bf16/MPS vs bf16/CUDA =
        # MAE 60.65, same dtype, different machine), so THE VARIABLE IS THE
        # BACKEND. Two standing consequences: the purple canon must be
        # enforced IN WORDS on the box path, because the Mac's free purple
        # does not travel there; and A MAC PLATE IS NEVER A PREDICTION ABOUT
        # WHAT THE BOX WILL DRAW FROM THE SAME WORDING.
        # ------------------------------------------------------------------
        # !! CAST CORRECTION, 2026-08-18, AND IT ENDS r1's LIFE AS A CONTROL.
        # READ THIS BEFORE TRUSTING THE THREE PARAGRAPHS ABOVE. They describe
        # r1 as "THE CONTROL -- the failing prompt, byte for byte" and as
        # "byte-identical to the `prompt:` field of
        # farm-out/ep2-b20-idfix/20-evidence-wave1-s3.yaml". THAT IS NO LONGER
        # TRUE OF THE STRING BELOW. It is left standing unedited because it is
        # what the record said, and because this file has already been burned
        # once by a comment that was WRONG AND LOAD-BEARING (see the 08-16
        # correction above). The colour question it existed to serve is
        # ANSWERED and closed by `backend_divergence_probe.py` -- same prompt,
        # same seed, Mac returns PURPLE and the box returns RED, so the
        # variable was never the wording -- and REVS[(20,2)] and [(20,3)]
        # restate their own positive AND negative in full, so neither of them
        # inherits anything from here and neither is disturbed by this edit.
        #
        # WHAT CHANGED AND WHY. The 08-18 Mac sample drew A ROUND-HEADED CHIBI
        # CHILD WITH BIG EYES -- a second goblin in an episode that has one,
        # and the "cute goblin" the founder rejected on beat 04. The prompt
        # asked for exactly that: `a small goblin boy` and `huge eyes`.
        #   `a small goblin boy` -> beat 14's identity wording, character for
        #       character: `lean wiry adult goblin man, green skin, bald head,
        #       patchwork cloak`. Beat 14 is the adult the founder chose and
        #       is the plate that renders him correctly; beat 20 now asks for
        #       the same man in the same words rather than a sixth wording.
        #   `huge eyes widening` -> `eyes widening`. The widening IS the
        #       staging -- the look up to the bare branch is half of
        #       `done_when` -- but `huge eyes` is a chibi cue and is the other
        #       half of what came back. The gesture is kept, the child is not.
        # STAGING IS OTHERWISE UNTOUCHED: both hands to the fig, the look up,
        # the bare branch, the field and the whole lighting tail are the same
        # words in the same order. The fruit stays `a ripe fig` -- purple is
        # a live founder ruling but the colour lever belongs to the revs, and
        # changing cast and colour in one draw would make neither attributable.
        # Negative: `baby, chibi` join `girl, child` so the block matches beat
        # 14's, and the duplicate `photorealistic` is dropped to pay for them
        # (`photorealism` was already in the same list).
        # Measured: 74/77 positive, 76/77 negative, exit 7 clean.
        # ------------------------------------------------------------------
        "prompt": (
            "1boy, lean wiry adult goblin man, green skin, bald head, "
            "patchwork cloak, solo, in a sunny grassy field, raises a ripe "
            "fig in both hands in front of him like evidence, eyes widening "
            "as he looks up at a bare branch above. Warm amber afternoon "
            "light, cinematic lighting, detailed, newest, masterpiece, best "
            "quality, very aesthetic"
        ),
        "negative": (
            "text, girl, baby, child, chibi, glowing eyes, glowing orb, "
            "dark, night, dusk, sunset, dim lighting, moody lighting, low "
            "key, shadows dominant, photorealism, leaf on head, plant girl, "
            "alraune, monster girl, flower on head, head wreath, hair "
            "ornament, leaf hair ornament, plant hair, female goblin, elf"
        ),
        # The seed of the rejected pick (s3 of ep2-b20-idfix-0812). It will
        # NOT reproduce that image here -- a CPU generator on MPS without the
        # IP-Adapter is a different draw -- and it is used only so the three
        # arms below share one seed and differ by their text alone.
        #
        # !! CORRECTION 2026-08-16. The conclusion is right and the reason is
        # wrong. There was no IP-Adapter on those frames (see the correction
        # above). It does not reproduce because MPS and CUDA are different
        # renderers: measured at this seed, CUDA-vs-MPS is MAE 61 while
        # fp16-vs-fp32 ON MPS is MAE 3. The draw differs by MACHINE, not by a
        # missing reference -- which is a far bigger fact, because it applies
        # to every prompt this file has ever drawn, not just this one.
        "seed": 20263739,
    },
}

# Revisions. ONE VARIABLE PER REVISION, and the reason is written down before it
# renders. `--rev N` merges over the base draft above.
REVS = {
    (20, 2): {
        # THE ONE VARIABLE, and it is one noun phrase: `a ripe fig` becomes
        # `a deep purple-violet fig`. Every other byte of the positive, the
        # whole negative and the seed are identical to r1. If r1 comes back
        # red-brown (as its CUDA siblings did, 4 of 4) and r2 comes back
        # purple, then colour is reachable by wording on this beat, the nine
        # rounds of fig work were never the problem here, and beat 20's fix
        # is to render a draft that already exists rather than to invent
        # vocabulary. If BOTH come back red, the wording lever is dead on
        # this composition and the next instrument is a negative that names
        # the failure colour -- which no beat-20 negative has ever done.
        #
        # WHY NOT THE FULL CANON PHRASE HERE. `deep purple-violet fig, green
        # at its neck, matte` is the canon and it is what r3 sends, but
        # dropped into r1's sentence it measures over 77 and the tail would
        # go silently. Two tokens of colour is the smallest edit that asks
        # the question, and a smaller edit is a cleaner attribution.
        "prompt": (
            "1boy, a small goblin boy, green skin, bald head, patchwork "
            "cloak, solo, in a sunny grassy field, raises a deep "
            "purple-violet fig in both hands in front of him like evidence, "
            "huge eyes widening as he looks up at a bare branch above. Warm "
            "amber afternoon light, cinematic lighting, detailed, newest, "
            "masterpiece, best quality, very aesthetic"
        ),
        # Restated BYTE FOR BYTE, not inherited. See the merge-site comment
        # in main(): a rev merges over DRAFTS[beat], never over the rev
        # before it, and a rev naming only a prompt would silently pick up a
        # negative nobody re-read.
        "negative": (
            "photorealistic, text, girl, child, glowing eyes, glowing orb, "
            "dark, night, dusk, sunset, dim lighting, moody lighting, low "
            "key, shadows dominant, photorealism, leaf on head, plant girl, "
            "alraune, monster girl, flower on head, head wreath, hair "
            "ornament, leaf hair ornament, plant hair, female goblin, elf"
        ),
    },
    (20, 3): {
        # NOT a variable on r2 -- this is the SHIP CANDIDATE, and it is here
        # so that a colour pass points at a string production can actually
        # send. It is `authored_b20_plate` from pipeline/wave-drafts.yaml AS
        # THE PIPELINE WOULD SEND IT: the exact output of
        # render_wave_goblin.check() -> sd_prompt.compress()/beat_negative()
        # with the goblin slot filled by goblin_ipa_sample's GOBLIN_DEF
        # (`green skin, bald head`), measured on the real CLIP tokenizer at
        # positive 74/77 and negative 77/77. Nothing here is authored by this
        # lane; wave-drafts.yaml is UNTOUCHED.
        #
        # Its negative sits at EXACTLY 77/77 with zero headroom, which is
        # recorded because it is the trap the next lane will walk into: one
        # more word in that draft and its tail leaves in silence.
        #
        # It differs from r2 in several ways at once (scene clause, framing,
        # the full canon fruit phrase, a different negative), so it is NOT
        # evidence about any single lever. r2 is the mechanism test; this is
        # the candidate.
        "prompt": (
            "1boy, a small goblin boy, green skin, bald head, solo, in green "
            "summer grass, a treeline and pale sky behind, raises a deep "
            "purple-violet fig, green at its neck, matte, in both hands like "
            "evidence. Medium full shot, bright morning light, cinematic "
            "lighting, detailed, newest, masterpiece, best quality, very "
            "aesthetic"
        ),
        "negative": (
            "photorealistic, 3d render, abstract, text, watermark, girl, "
            "child, hair, wig, armor, jewelry, ornament, long eyelashes, "
            "lipstick, dark, night, photorealism, leaf on head, plant girl, "
            "alraune, monster girl, flower on head, head wreath, hair "
            "ornament, leaf hair ornament, plant hair, female goblin, elf"
        ),
    },
    (8, 2): {
        # r1 came back UNUSABLE and in an instructive way: a colossal
        # two-headed goblin filling the upper half as a piece of SCENERY, and
        # three tiny identically-uniformed guards at the bottom edge seen from
        # BEHIND -- no scavenger among them, no clipboard, no faces. The
        # composition lever half-worked: the field, the sky, the headroom and
        # the full-length staging are all there. What broke is SCALE.
        #
        # THE ONE VARIABLE: `small figures low in frame`. It was lifted from
        # the beat-17 plate, where it is correct because that plate is `solo`
        # and the one figure keeps the frame. Here it shrank the real people
        # to specks, and a canvas with nothing of subject size left in it got
        # the remaining space filled with the only other noun available -- the
        # goblin, drawn at scenery scale. One phrase produced both defects, so
        # one phrase is what changes. Everything else, including `scenery`,
        # `wide shot`, the sky clause and the whole negative, is BYTE-IDENTICAL
        # to r1: if the goblin still comes back as landscape once the figures
        # are people-sized, that is a separate finding about the `scenery` tag
        # and it must not be confounded with this one.
        "prompt": (
            "3boys, full body, wide shot, scenery, standing in a green field, "
            "two adult guard men in uniform facing a lean adult goblin man, "
            "green skin, bald head, patchwork cloak, near guard holds a "
            "wooden clipboard at chest height, three men standing together, "
            "wide blue sky above, sunny day, masterpiece, best quality"
        ),
    },
    (8, 3): {
        # r2's variable WORKED and the prediction written into r2 above came
        # true, in the same render. Dropping `small figures low in frame` for
        # `three men standing together` made the three people person-sized,
        # full length, standing on a path FACING THE LENS, one of them holding
        # a board -- r1's specks-seen-from-behind are gone. And the colossal
        # goblin came back anyway, barely changed. r2 said in advance: "if the
        # goblin still comes back as landscape once the figures are
        # people-sized, that is a separate finding about the `scenery` tag."
        # It is, so `scenery` is r3's one variable and it is DELETED.
        #
        # Why that tag and not the goblin words: `scenery` is an animagine
        # composition tag that promotes the LANDSCAPE to subject. Beat 17's
        # plate carries it safely because that prompt is `solo` -- one figure
        # owns the frame and the tag only opens the sky behind him. Here it is
        # competing with three small people for what the picture is OF, and a
        # green cloaked hill is what it built out of the only large noun in
        # the prompt. Everything else, including the whole negative and the
        # `three men standing together` clause r2 proved, is BYTE-IDENTICAL.
        "prompt": (
            "3boys, full body, wide shot, standing in a green field, "
            "two adult guard men in uniform facing a lean adult goblin man, "
            "green skin, bald head, patchwork cloak, near guard holds a "
            "wooden clipboard at chest height, three men standing together, "
            "wide blue sky above, sunny day, masterpiece, best quality"
        ),
    },
    (8, 4): {
        # r3's hypothesis is FALSIFIED and that is worth as much as a pass.
        # Deleting `scenery` changed the giant not at all -- it is still there,
        # same pose, same scale. So the colossus is not that tag, and nobody
        # should spend another sample on it. r3 did move the figures closer and
        # larger (a side effect of the deletion, noted, not claimed as a lever)
        # and they now read as three uniformed men holding boards, facing the
        # lens, full length, in a field with sky above -- the COMPOSITION beat
        # 08 has never had. Two defects remain: the colossus, and all three men
        # being goblins where the beat needs two human guards and one goblin.
        #
        # THE ONE VARIABLE: the NEGATIVE, which has been byte-identical through
        # r1-r3 and has never once named the thing that keeps happening. Three
        # samples have now shown the failure is not scale (r2) and not the
        # `scenery` tag (r3), which leaves the positive's own nouns building a
        # goblin at landscape size in the empty upper half. A negative is the
        # cheapest instrument that addresses it directly and it is one edit.
        # The positive stays BYTE-IDENTICAL to r3, so if the colossus survives
        # a negative that forbids it by name, the cause is structural -- the
        # `wide blue sky above` clause reserving a subject-sized hole -- and
        # that, not more words, is what r5 would test.
        "prompt": (
            "3boys, full body, wide shot, standing in a green field, "
            "two adult guard men in uniform facing a lean adult goblin man, "
            "green skin, bald head, patchwork cloak, near guard holds a "
            "wooden clipboard at chest height, three men standing together, "
            "wide blue sky above, sunny day, masterpiece, best quality"
        ),
        # The first draft of this negative measured 90/77 and the tokenizer
        # guard refused to draw it -- its tail, which is where the anti-card
        # terms live, would have been dropped in silence. Trimmed to fit by
        # deleting terms no sample has ever needed: `titan`, `looming figure`,
        # `mountain shaped like a face`, `bust`, `baby`, `staff`, `chibi`,
        # `scars`, `stitches`. Named here so the trim is visible and nobody
        # reads the shorter list as a second variable.
        "negative": (
            "giant, colossal, monster, kaiju, statue, face in the sky, "
            "text, close-up, portrait, upper body, cropped, "
            "1boy, 2boys, 4boys, solo, white background, simple background, "
            "child, spear, sword, tree, forest, house, indoors, "
            "photorealism, 3d render, night"
        ),
    },
    (8, 5): {
        # r4 FALSIFIED TOO, and r4 said in advance what that would mean. A
        # negative naming `giant, colossal, monster, kaiju, statue, face in the
        # sky` left the colossus exactly where it was. So it is not the
        # `scenery` tag (r3) and it is not un-named-ness (r4); the words are
        # not what is putting it there. The foreground meanwhile is now RIGHT:
        # three full-length figures facing the lens, distinct costumes, one
        # holding a board, standing in a field with sky above -- beat 17's
        # composition, which beat 08 has never had.
        #
        # THE ONE VARIABLE, and it is the structural suspect r4 named: the
        # clause `wide blue sky above`. Every sample so far has reserved the
        # top half of a 832x1216 canvas for sky and then put the three people
        # in the bottom third, and every sample has filled the reserved half
        # with a subject. That is not a word problem, it is a composition
        # problem: an empty upper half in a portrait frame is a hole the model
        # will fill, and `wide shot` plus a large-noun goblin tells it what
        # with. Beat 17's plate gets away with the same clause because its one
        # figure is drawn LARGE and low, so the sky is negative space around a
        # subject rather than a vacancy. DELETING the clause is the smallest
        # change that tests it; the field, the figures and the whole negative
        # stay byte-identical to r4. If the colossus survives the deletion,
        # stop -- it is the `3boys`-plus-goblin nouns themselves and this beat
        # needs a different drafting approach, not a fifth adjective.
        "prompt": (
            "3boys, full body, wide shot, standing in a green field, "
            "two adult guard men in uniform facing a lean adult goblin man, "
            "green skin, bald head, patchwork cloak, near guard holds a "
            "wooden clipboard at chest height, three men standing together, "
            "sunny day, masterpiece, best quality"
        ),
        "negative": (
            "giant, colossal, monster, kaiju, statue, face in the sky, "
            "text, close-up, portrait, upper body, cropped, "
            "1boy, 2boys, 4boys, solo, white background, simple background, "
            "child, spear, sword, tree, forest, house, indoors, "
            "photorealism, 3d render, night"
        ),
    },
    (17, 2): {
        # ==================================================================
        # 2026-08-16, THE BIG-ACTION-IN-A-KNOWN-FRAME LANE. THE PLATE, AND
        # THE BAR THE CLIP MADE FROM IT WILL BE JUDGED BY. BOTH WRITTEN
        # BEFORE A SINGLE PIXEL EXISTS, AND NEITHER GETS REWRITTEN AFTER.
        # ==================================================================
        # WHAT r1 SETTLED AND WHAT IT LEFT OPEN. r1 (commit 6b5955cf) drew a
        # TIGHT INSERT -- a hand at 57.5% of the frame's width, the only
        # subject in shot, cloth edge to edge -- to test "make the small
        # action the largest motion in frame". It FAILED, and not in the way
        # the freeze failures fail. M1 contact passed and nothing else did:
        # the hand moved 226 px down-frame while three cloth landmarks moved
        # 214 px WITH it (hand-relative-to-cloth 0.01-0.06 hand-widths
        # against a 1.0 bar), because the 226 px was the CAMERA pulling back
        # and tilting; then the hand elongated, its claws detached, it
        # dissolved into a sleeve, and from f050 there was no insert at all,
        # only a medium portrait of a grinning spiky-haired man. The clip
        # moved ENORMOUSLY (per-pair mean |delta| up to 54) and spent every
        # bit of it RE-COMPOSING THE SHOT instead of performing the action.
        #
        # That leaves exactly two live readings, and r1 said honestly that
        # one sample cannot separate them:
        #   (a) the engine cannot do fine hand action AT ANY SCALE;
        #   (b) a tight insert with NO WHOLE BODY is out of distribution for
        #       this i2v checkpoint, so the shot escapes to a composition it
        #       knows -- a character portrait -- and the FRAMING dragged the
        #       clip away, rather than the action being impossible.
        #
        # ------------------------------------------------------------------
        # THE ONE THING THIS REVISION TESTS, AND WHY IT DISCRIMINATES
        # ------------------------------------------------------------------
        # Three cells of one grid have now been filled, and only one is left:
        #
        #   composition                     hand size    brush result
        #   ---------------------------------------------------------------
        #   wide, small figure, ~55% sky    8.5% of W    FROZEN (0/6)
        #     (17-goodbye-mac-seated-r1, the plate 12 of 12 stand-ups
        #      were rendered from; amp-brush and amp-brushseat froze on it)
        #   tight insert, NO body           57.5%        RE-COMPOSED (r1)
        #   whole body, figure fills frame  >=18%        *** UNTESTED ***
        #
        # The untested cell is the ONLY one that is both IN DISTRIBUTION and
        # has the action several times larger than the cell that froze. That
        # is precisely the disagreement between (a) and (b):
        #   * If the brush RENDERS here, (b) is right. The insert failed
        #     because of its framing, not because a hand cannot brush, and
        #     the lever for beats 06/08/10 is STAY IN DISTRIBUTION while
        #     getting the action big -- not "make the action big".
        #   * If it FAILS here, the action has now been asked for at 8.5%
        #     in-distribution (froze), at 18%+ in-distribution (this), and
        #     at 57.5% out-of-distribution (re-composed). Reading (a)
        #     survives: fine hand action is out of reach for this engine,
        #     and that changes what episode 2 can contain.
        # A pass and a fail are both the finding, and neither is a reason
        # for this lane to re-plan a beat. That is the author's call.
        #
        # WHY BEAT 17'S BRUSH AND NOT SOME OTHER ACTION. The surrounding beat
        # already works -- 12 of 12 stand-ups, 4 of 4 stand-and-turn -- so
        # the brush is the only unknown in it, and the brush is the same
        # SHAPE of action (small, in-hand, no gravity) that beats 06, 08 and
        # 10 have failed on with every wording, strength, seed and recipe.
        # Any other action would introduce a second difference.
        #
        # ------------------------------------------------------------------
        # THE A/B IS PURE ON THE PROMPT SIDE, WHICH r1's WAS NOT
        # ------------------------------------------------------------------
        # r1 had to change two words ("with both hands" -> "with his hand")
        # because a one-hand plate forced it, and it named that honestly.
        # This plate has BOTH HANDS on the cloak, so the motion prompt, the
        # motion negative, the seed (20260901) and every render flag can be
        # and WILL BE byte-identical to ep2-b17-amp-brush-0816, the clip that
        # FROZE. THE INIT PICTURE IS THE ONLY DIFFERENCE.
        #
        # NAMED HONESTLY AND NOT GLOSSED, because a new plate is never one
        # pixel of change: moving the camera in on the same seated pose
        # necessarily does three things at once to the picture -- the hands
        # get bigger, the sky vacancy goes away, and the figure is REDRAWN
        # rather than cropped (a crop of the old plate would have been
        # 380x520 px upscaled 1.85x, and a soft init is its own confound,
        # worse than a redraw). The POSE, the SUBJECT, the ACTION CLAUSE and
        # every render flag are held. Nobody should read this as a
        # single-pixel A/B; it is a single-COMPOSITION A/B.
        #
        # WHY EACH CLAUSE (each learned by losing a render, not reasoned out):
        #   `full body` FIRST and `solo` -- leading framing tags carry real
        #       weight and trailing ones almost none. The whole body staying
        #       in frame IS the variable under test, so it goes at the front.
        #   `sitting` and `resting flat on` -- STATES, not verbs. The model
        #       renders a verb's END state; a plate that said "brushing"
        #       would come back mid-stroke or finished with nowhere left to
        #       travel. The plate is the PRE state on purpose.
        #   `figure fills the frame` replaces the control plate's `small
        #       figure low in frame` + `vast blue sky and clouds fill the
        #       space above him`. Those two clauses are what made the hand
        #       8.5% of the width, and an empty upper half is a hole the
        #       model fills with the largest noun (beat 08 lost five samples
        #       to a colossus grown in exactly that hole). Grass and cloth
        #       are textured ground, not vacancy.
        #   `both clawed hands resting flat on the dusty cloak` -- on the
        #       CONTROL plate the hands rest on his bare green KNEE and the
        #       cloak is off to one side, so amp-brush asked for a brush that
        #       had nowhere to start. M1 has to be true in the plate itself.
        #   no character name anywhere -- verbs and props do not bind to a
        #       named character on this checkpoint, so nothing is asked to.
        #
        # ------------------------------------------------------------------
        # PLATE BAR, PRE-REGISTERED. The plate is usable only if ALL hold:
        # ------------------------------------------------------------------
        #   P1 THE WHOLE BODY IS IN FRAME -- head, torso, both arms, both
        #      hands and the legs are all inside the frame after the
        #      704x1280 cover crop. A cropped head or missing legs sends the
        #      plate back: an in-distribution whole-body composition is half
        #      the experiment.
        #   P2 BOTH clawed hands are IN CONTACT with the cloak, and the
        #      nearer hand spans AT LEAST 18% of the frame's width. The
        #      control plate that froze measures 8.5%, so this is at least a
        #      2.1x enlargement of the action. Measured on the cover-cropped
        #      704x1280 init, not on the 832x1216 draw.
        #   P3 OPEN, unobstructed cloth at least one hand-width across lies
        #      next to the hands, so a stroke has somewhere to go. Without
        #      it a fail is unreadable -- it could just be nowhere to travel.
        #   P4 NO EMPTY REGION larger than the figure's head: no sky band, no
        #      blank paper, no white background. The vacancy law.
        #   P5 EXACTLY ONE figure, no second face, no prop in either hand.
        #   Recorded and NOT scored: palette and cloak pattern continuity
        #   with the show's plates. This is an engine probe, never a take.
        #
        # ------------------------------------------------------------------
        # MOTION BAR, PRE-REGISTERED HERE SO IT CANNOT BE REWRITTEN AFTER THE
        # CLIP. It is a BODY-MOTION test, not a picture-changed test. Same
        # structure as r1's bar, which was good, plus one fail mode r1 did
        # not need and this one does.
        # ------------------------------------------------------------------
        #   PASS requires ALL of:
        #     M1 a hand is IN CONTACT with the cloak in at least one frame;
        #     M2 that hand TRAVELS ACROSS THE FABRIC while in contact -- its
        #        position RELATIVE TO THE CLOTH moves at least ONE HAND-WIDTH
        #        between two frames of the clip, where one hand-width is the
        #        hand's own width measured on the init plate. RELATIVE TO THE
        #        CLOTH, never relative to the frame: r1's hand moved 226 px
        #        in frame and 4-22 px relative to the cloth, and the frame
        #        number is the one that means nothing.
        #     M3 it is the HAND moving and NOT THE CAMERA: the frame edges,
        #        the horizon and the cloth's own folds do not translate with
        #        it.
        #     M4 the path is CONTINUOUS -- read at consecutive frames, the
        #        hand can be followed from where it starts to where it ends.
        #   FAIL MODES, NAMED IN ADVANCE:
        #     F1 FROZEN -- the hand holds one position f0->f96, linework
        #        re-inked in place. amp-brush's exact signature.
        #     F2 CLOTH-ONLY -- the fabric ripples or blows and the hand does
        #        not move relative to it.
        #     F3 CAMERA-ONLY -- the whole frame drifts, pushes in, tilts or
        #        zooms and hand and cloth keep the same relative geometry.
        #        This is what r1 did.
        #     F4 MORPH -- the hand dissolves, gains or loses fingers, or
        #        reappears elsewhere with no continuous path. A teleport is
        #        not a stroke.
        #     F5 SCENE BREAK -- the shot cuts, relocates, or a second figure
        #        or a face that is not his arrives.
        #     F6 CONTACT WITHOUT TRAVERSAL -- the hand touches and the cloth
        #        drapes, rotates or settles under it and the hand does not
        #        travel. EXPLICITLY A FAIL. One beat-17 `full` cell already
        #        did exactly this and could have been talked into a pass;
        #        calling it one is how a bar gets bent.
        #     F7 BODY-INSTEAD-OF-HAND -- NEW, and it is the fail mode this
        #        composition invites. Putting the whole body back in frame
        #        puts back everything the engine is GOOD at: this plate can
        #        stand him up, turn him, sway him, blink him, flutter the
        #        cloak and blow the grass, and the clip will then be full of
        #        motion with the hands still stuck to the cloth. Gross
        #        whole-body motion IS NOT THE BRUSH. A stand-up is not a
        #        pass, a head turn is not a pass, a cloak flutter is not a
        #        pass, and "the picture changed a lot" is not a pass. Only
        #        M1+M2+M3+M4 is a pass. Whether he stands up is RECORDED
        #        SEPARATELY, as the amp-brush spec recorded it, and scored
        #        as nothing.
        #
        #   TOOLING IS FALSIFIED BEFORE IT IS TRUSTED, because r1's would
        #   have lied twice. Its colour tracker was thrown away BEFORE the
        #   render: the hand LOOKS green and is not (R71 G69 B47 -- R above
        #   G), so `(G > R + 10)` matched ZERO pixels in the whole frame and
        #   would have reported "no hand" on all 97 frames, which reads
        #   identically to "the hand never appears". Its NCC replacement then
        #   failed its own self-check after f042 and r1 quoted no number past
        #   that point. So: every tracker gets (i) its mask or marker
        #   OVERLAID BACK onto real frames and looked at before a single
        #   number is believed -- that overlay is what turned 9-of-12 into
        #   12-of-12 -- and (ii) a self-check whose failure means NO NUMBER
        #   IS QUOTED past the frame it failed at.
        #
        #   NOT EVIDENCE, AND NONE OF IT WILL BE QUOTED. `depth` is RETIRED
        #   AND INVERTED, confirmed three ways: full stand-up 0.290,
        #   zero-motion clip 0.516, a clip whose only movement was a BIRD
        #   0.376. The old `cadence` metric is structurally blind -- odd hold
        #   periods alias to exactly 1.00x. Camera-scale numbers are
        #   unreliable without aligned frames. ALL 97 FRAMES GET OPENED
        #   CONSECUTIVELY via pipeline/coldread_frames.py and THE READING IS
        #   THE VERDICT.
        #
        # ONE SAMPLE. No sweep, no second seed, no wording variant.
        # Guidance, CFG and checkpoint belong to another lane and are not
        # touched. IF IT PASSES, THIS LANE SAYS SO AND STOPS -- re-cutting
        # beat 17 into two shots or re-planning 06/08/10 is an authorship
        # call and not this lane's. shots.md and wave-drafts.yaml UNTOUCHED.
        "slug": "goodbye-bigbody",
        "done_when": (
            "MOTION BAR (pre-registered before the plate was drawn): a hand "
            "makes contact with the cloak AND TRAVELS ACROSS IT -- at least "
            "one hand-width of movement RELATIVE TO THE CLOTH, continuous "
            "across consecutive frames, the hand moving and not the camera. "
            "FAIL modes named in advance: F1 frozen, F2 cloth-only, F3 "
            "camera-only, F4 morph/teleport, F5 scene break, F6 contact "
            "without traversal, F7 body-instead-of-hand. A changed picture "
            "is not a pass and a stand-up is not a pass."
        ),
        "why": (
            "r1's tight insert put the hand at 57.5% of the frame and the "
            "brush still did not happen -- but the clip did not freeze, it "
            "RE-COMPOSED itself into a character portrait, which leaves two "
            "readings one sample cannot separate: (a) fine hand action is "
            "impossible on this engine, or (b) an insert with no body is out "
            "of distribution and the framing dragged the clip away. This "
            "plate fills the one untested cell of the grid: WHOLE BODY IN "
            "FRAME -- the composition that renders 12 of 12 stand-ups -- "
            "with the hand action as large as that frame allows (>=18% of "
            "frame width against the frozen control's 8.5%). A pass says "
            "(b) and the lever is 'stay in distribution'; a fail says (a) "
            "and fine hand action is out of reach for episode 2."
        ),
        "prompt": (
            "1boy, solo, full body, sitting on grass in a field, figure "
            "fills the frame, lean wiry adult goblin man, green skin, bald "
            "head, dusty patchwork cloak draped over his knees, both green "
            "clawed hands resting flat on the cloak, large hands near the "
            "camera, low angle, sunny day, masterpiece, best quality, "
            "very aesthetic"
        ),
        # The first draft of this negative measured 88/77 and the tokenizer
        # guard REFUSED to draw it -- its tail, where the anti-vacancy and
        # anti-crop terms live, would have been dropped in silence. Trimmed
        # to fit by deleting terms no beat-17 sample has ever needed:
        # `mountains`, `out of frame`, `broom`, `staff`, `stick`, `basket`,
        # `scars`, `forest`, `house`, `white background`, `baby`. Named here
        # so the shorter list is not read as a second variable.
        "negative": (
            "text, standing, walking, running, wide shot, distant, "
            "small figure, sky, clouds, horizon, "
            "close-up, portrait, cropped, "
            "holding object, spear, sword, "
            "2boys, child, chibi, stitches, tree, indoors, "
            "photorealism, 3d render, dark, night"
        ),
    },
    (17, 3): {
        # r2 FAILED ITS OWN PRE-REGISTERED PLATE BAR, and it failed at P5 and
        # P4 -- the two criteria that exist because of the vacancy law. It is
        # recorded rather than quietly re-rolled, because the way it failed is
        # the law firing again on a lane that had already written the law down.
        #
        #   P1 whole body in frame ....... PASS. Bald head near the top, torso,
        #      both arms, both hands, legs and both bare feet all inside the
        #      704x1280 cover crop.
        #   P2 hands >=18% of frame width  PASS on size -- the near hand spans
        #      ~190 px = ~27% of the 704 px width, against the frozen control
        #      plate's 8.5%. Contact with the cloak is arguable rather than
        #      clean: the hands rest on a grey-black lap mass that reads as
        #      cloak, and the claws are fused into one yellow spike cluster.
        #   P3 open cloth beside the hands  PASS, the black cloak panel left of
        #      the near hand is about one hand-width across.
        #   P4 no empty region larger than his head ......... FAIL. The upper
        #      corners are a flat pale cream-green wash, several head-areas
        #      each, with no texture in them at all.
        #   P5 exactly one figure, no second face ........... FAIL, and badly.
        #      THREE extra grinning goblin heads are drawn into that flat
        #      region -- top-left corner, left edge and right edge -- despite
        #      `solo` leading the prompt and `2boys` sitting in the negative.
        #
        # P4 AND P5 ARE ONE DEFECT, NOT TWO, and it is the law this lane has
        # already paid for twice: AN EMPTY REGION IN A FRAME IS A HOLE THE
        # MODEL FILLS WITH THE LARGEST NOUN IN THE PROMPT. Beat 08 lost five
        # samples to a colossus grown in a reserved sky; r1's insert had no
        # empty region, so the CLIP made one by pulling the camera back and put
        # a face in it. Here the flat grass margin was the hole and the goblin
        # was the noun, three times over.
        #
        # WHY IT MATTERS MORE THAN USUAL AND WHY THIS PLATE CANNOT BE USED:
        # this experiment's whole question is whether the shot RUNS AWAY TO
        # ANOTHER COMPOSITION. Handing the i2v checkpoint an init that already
        # contains three other faces to escape into would confound F5 and F7
        # beyond rescue -- a second figure arriving would no longer be evidence
        # of anything, because it was in the plate.
        #
        # THE ONE VARIABLE: the background gets a NOUN OF ITS OWN so there is
        # no flat region left to fill. `sitting on grass in a field` becomes
        # `sitting in tall grass` plus `tall grass background`. Tall grass is
        # the fill this repo has already used for exactly this (ep1-b06's
        # r6a/r7a/r8a2 tallgrass arms) and it is not a character, so it cannot
        # become one. EVERYTHING ELSE IS BYTE-IDENTICAL to r2, negative
        # included -- deliberately, because r2's negative already carries
        # `2boys` and beat 08 r4 proved on this checkpoint that a negative
        # naming the invited noun by name (`giant, colossal, monster, kaiju,
        # statue, face in the sky`) removes it not at all. If the extra faces
        # survive a background that has something in it, THAT is a separate
        # finding and the negative is what r4 would try -- but it is not what
        # this revision spends a sample on.
        #
        # THE MOTION BAR AND THE PLATE BAR ARE UNCHANGED, both as committed in
        # efd7bafa before any pixel existed. A plate revision is a fixture
        # being brought up to a gate that was written first; it is not the
        # experiment, and nothing about M1-M4, F1-F7 or P1-P5 moves.
        # NOTE ON THE MECHANICS, because it would have silently ruined this
        # revision: `REVS` merges over `DRAFTS[beat]`, which for beat 17 is the
        # r1 TIGHT INSERT draft -- not over rev 2. A rev that names only a
        # prompt inherits the INSERT's negative (`face, head, portrait, full
        # body, wide shot, standing...`), which forbids the very whole body
        # this experiment is about. The negative below is therefore r2's,
        # RESTATED BYTE FOR BYTE rather than inherited, and `low angle` is kept
        # in the positive for the same reason -- so that the tall-grass clause
        # is the only thing that differs from r2.
        "slug": "goodbye-bigbody",
        "prompt": (
            "1boy, solo, full body, sitting in tall grass, tall grass "
            "background, figure fills the frame, lean wiry adult goblin man, "
            "green skin, bald head, dusty patchwork cloak draped over his "
            "knees, both green clawed hands resting flat on the cloak, large "
            "hands near the camera, low angle, sunny day, masterpiece, "
            "best quality, very aesthetic"
        ),
        "negative": (
            "text, standing, walking, running, wide shot, distant, "
            "small figure, sky, clouds, horizon, "
            "close-up, portrait, cropped, "
            "holding object, spear, sword, "
            "2boys, child, chibi, stitches, tree, indoors, "
            "photorealism, 3d render, dark, night"
        ),
    },
    (11, 2): {
        # r1 FAILED ITS OWN PRE-REGISTERED BAR, at P2 and therefore P1, and it
        # failed in the single most informative way available. Judged by
        # opening the PNG, against the bar committed in e4279ce5 before it was
        # drawn, criterion by criterion:
        #
        #   P1 the APPROVED PAIR ......... FAIL, necessarily -- there is only
        #      one man, so a pair cannot be assessed. The one man present is
        #      also a HYBRID: guard B's light sandy hair above guard A's tan
        #      tunic and dark cropped trousers. Fail mode Q8.
        #   P2 exactly two whole figures . FAIL. ONE figure. `2boys` LEADING
        #      the prompt, with `1boy` AND `solo` in the negative, and it still
        #      came back solo. Fail mode Q2, and it is the historically
        #      hardest thing in this beat family -- beat 05's record reads
        #      "words have now produced 1, 3 and 3+ on this beat".
        #   P3 backs turned, room ahead .. PASS on backs turned, unambiguous:
        #      back of the head, back of the tunic, no face, no eyes. MARGINAL
        #      on room -- the tall-grass band stands about one figure-height
        #      in front of him, though open mown grass runs off to his left.
        #   P4 >=25% of frame height ..... PASS, ~32.5% (roughly y440-y835 of
        #      1216). Hair colour and garment value are plainly legible, which
        #      is the only reason the number is in the bar.
        #   P5 no vacancy ................ PASS. Textured grass to the top
        #      edge, a hedgerow giving the upper third a noun of its own, and
        #      only a ~5% pale sky sliver at top-left, well under a torso.
        #   P6 no props .................. PASS. No board, no clipboard, no
        #      weapon, nothing floating.
        #   P7 field in the plate ........ PASS.
        #
        # SIX OF THE EIGHT NAMED FAIL MODES DID NOT FIRE, and two of those are
        # worth more than the count failure costs.
        #   * Q1 BALD PAIR IS DEFEATED. He has hair, and it is legibly sandy
        #     blond. Fourteen of the seventeen prior guard prompts asked for
        #     `bald`; this one forbade it and named the cast's hair, and the
        #     hair arrived on the first sample. The attribute this whole lane
        #     exists to fix is fixable by wording.
        #   * Q5 VACANCY DID NOT FIRE ON THE COMPOSITION THAT INVITES IT MOST.
        #     "Two figures walking into open field" is by construction a large
        #     empty region, and `tall grass background` filled it on the first
        #     sample with something that cannot become a character. That is a
        #     fourth confirmation of the vacancy law and the first PRE-EMPTION
        #     of it, rather than another post-mortem.
        # Q3 frontal, Q4 specks, Q6 costume merge between two men (untestable
        # at n=1) and Q7 prop all did not fire.
        #
        # THE ONE VARIABLE: THE COUNT, stated as a frame-one FACT.
        # The diagnosis is in the prompt's own words. The two men are written
        # as "ONE MAN with dark cropped hair..., ONE MAN with light sandy
        # hair...", so the literal string "one man" appears twice, naming a
        # singular subject each time, while the only plural assertions are the
        # leading `2boys` tag and "two guard men". A negative carrying `1boy`
        # and `solo` did not overcome it -- which is consistent with beat 08
        # r4, where a negative naming the unwanted thing by name removed it
        # not at all.
        #
        # The fix is the one this repo has already PROVEN for exactly this, on
        # beat 08 r2: replacing a clause that shrank and singularised the
        # group with `three men standing together` made three people
        # person-sized and plural in one sample, and r2's prediction about
        # what would survive came true in the same render. The same phrase,
        # adapted in number, is inserted here and NOTHING ELSE MOVES -- the
        # framing tags, the two person clauses, `tall grass background`, the
        # whole negative and THE SEED are byte-identical to r1, so if the
        # count binds, the phrase is what bound it.
        #
        # Deliberately NOT changed, so as not to confound: the "one man ...
        # one man" phrasing stays. If the count still fails with a stated pair
        # fact present, THAT phrasing is r3's single variable, and left/right
        # binding ("the man on the left has...") is r4's. Naming the ladder in
        # advance so no revision quietly does two things at once.
        #
        # ------------------------------------------------------------------
        # THE ATTRIBUTE-MERGE LAW, and a FALSIFIABLE PREDICTION FOR r2.
        # WRITTEN AND COMMITTED BEFORE r2's IMAGE WAS OPENED, so that r2 tests
        # it instead of being explained by it afterwards.
        # ------------------------------------------------------------------
        # r1's single figure did not carry guard A's attributes OR guard B's.
        # He carried BOTH, blended: B's light sandy hair above A's tan tunic
        # and A's dark cropped trousers. Neither man's set won; the two sets
        # MERGED onto the one body the prompt actually produced.
        #
        # THE LAW: WHEN THE COUNT FAILS, THE ATTRIBUTE SETS MERGE RATHER THAN
        # ONE NAMED MAN'S SET WINNING. This checkpoint does not bind an
        # attribute to a named character (the bark board went to the goblin in
        # 9 frames of 12; `pointing at another` in 3 of 3), so with fewer
        # bodies than described sets, every loose attribute lands on whatever
        # bodies exist. A COUNT FAILURE AND AN IDENTITY FAILURE ARE THEREFORE
        # THE SAME FAILURE ON THIS BEAT, not two to be fixed separately, and
        # fixing the count is a PREREQUISITE for testing identity at all --
        # P1 is literally unassessable at n=1.
        #
        # THE PREDICTION, which r2 can falsify:
        #   * IF r2 fixes the count to two men, the expected identity outcome
        #     is NOT "one right man and one wrong man". It is TWO MEN EACH
        #     CARRYING A BLEND -- e.g. both sandy-haired in tan, or one in tan
        #     with sandy hair and one in dark brown with sandy hair -- because
        #     the merge is about attributes being loose, not about a shortage
        #     of bodies. That outcome would be fail mode Q6 (costume merge)
        #     and would CONFIRM the law.
        #   * IF instead r2 returns two men with the two attribute sets
        #     CLEANLY SEPARATED, one dark-haired in tan and one sandy-haired
        #     in dark brown, the law is FALSIFIED as stated: body count alone
        #     was doing the binding, and the ladder's later rungs (the "one
        #     man ... one man" phrasing, then left/right binding) are not
        #     needed. That would be the best available outcome and it must not
        #     be quietly reinterpreted as "the law held".
        #   * IF r2 returns one man again, the law is untested, not confirmed.
        #
        # This is written down BEFORE the image is opened, on the same
        # principle as the plate bar itself.
        #
        # THE PLATE BAR AND THE FAIL MODES ARE UNCHANGED, as committed in
        # e4279ce5 before any pixel existed. A revision brings a fixture up to
        # a gate that was written first; it never edits the gate.
        "slug": "they-leave",
        "prompt": (
            "2boys, from behind, full body, wide shot, two guard men "
            "standing together in tall grass, tall grass background, one "
            "man with dark cropped hair in a plain tan tunic, one man with "
            "light sandy hair in a dark brown tunic, cloth sash of office, "
            "dark trousers and boots, sunny day, masterpiece, best quality"
        ),
        # Restated BYTE FOR BYTE rather than inherited. A rev merges over
        # DRAFTS[11], not over the rev before it, and a rev naming only a
        # prompt would inherit silently -- the guard at the merge site refuses
        # that with exit 6, and it is right to.
        "negative": (
            "text, looking at viewer, facing viewer, face, close-up, "
            "portrait, distant, small figure, bald, 1boy, 3boys, solo, "
            "sky, horizon, white background, simple background, "
            "holding object, clipboard, armor, helmet, knight, child, "
            "photorealism, 3d render, night"
        ),
    },
    (11, 3): {
        # r2 SOLVED THE COUNT AND THE IDENTITY ON ONE SAMPLE, and FALSIFIED
        # the law r2's own comment committed before the image was opened.
        # Judged by opening the PNG and then three crops of it at 2x-4x -- the
        # figures, the top band, the bottom band, the two heads, and guard B's
        # hand -- against the bar committed in e4279ce5.
        #
        #   P1 the APPROVED PAIR ......... PASS. LEFT: black cropped hair, a
        #      pale cream-tan long tunic-coat, dark grey cropped trousers,
        #      brown boots. RIGHT: light sandy-blond tousled hair, a mid-brown
        #      long tunic-coat, blue-grey cropped trousers, brown boots.
        #      Neither is bald. THE PAIRING IS CORRECT AND NOT SWAPPED: dark
        #      hair took the tan, sandy hair took the dark brown, exactly as
        #      the two person clauses wrote them.
        #   P2 two whole figures ......... PASS. Exactly two, both full-length
        #      to the boots. Top band and bottom band were cropped and swept
        #      separately for a third body: none.
        #   P3 backs turned, room ahead .. FAIL, and it is not softened. Both
        #      heads are turned into a REAR-THREE-QUARTER. The left man shows
        #      a clean profile edge -- brow, nose, cheek, jaw and the corner
        #      of an eye; the right man shows jaw and ear. The bar says "no
        #      face, no eyes" and there is a face and an eye. Room ahead is a
        #      MARGINAL pass: open clearing and a path lead away up-right, but
        #      directly ahead the tall-grass band stands about half a figure
        #      height off.
        #   P4 >=25% of frame height ..... PASS, ~35%.
        #   P5 no vacancy ................ PASS. Textured grass and foliage
        #      across the full width; the only soft region is a ~10% haze band
        #      at the very top which still carries grass silhouettes, and
        #      nothing grew in it.
        #   P6 no props .................. PASS AS WRITTEN -- no board, no
        #      clipboard, no badge, no weapon, nothing detached. NAMED DEFECT
        #      ANYWAY: a narrow dark strap or cord about a hand and a half
        #      long hangs from guard B's left hand. It originates at the hand
        #      rather than floating, so it does not trip P6, but an
        #      unexplained hanging object ON THIS MAN is precisely the class
        #      the founder named ("there is a clipboard floating behind him"),
        #      and guard B's own derived prompt canonically carries a bark
        #      clipboard, so this may be a vestige of one. It must be cleared
        #      before anything is frozen; it is recorded, not glossed.
        #   P7 field in the plate ........ PASS.
        # SIX OF SEVEN PASS. THE PLATE FAILS THE BAR, on P3.
        #
        # THE PREDICTION IS FALSIFIED, AND SAYING SO IS THE POINT OF HAVING
        # WRITTEN IT DOWN. (11,2)'s comment and done-definitions'
        # `attribute_merge_law_0816` both predicted, before this image was
        # opened, that fixing the count would yield TWO MEN EACH CARRYING A
        # BLEND rather than one right and one wrong -- and named the outcome
        # that would falsify the law: "if instead the two sets come back
        # CLEANLY SEPARATED, the law is FALSIFIED as stated, and body count
        # alone was doing the binding. That would be the best available
        # outcome and it must not be quietly reinterpreted as 'the law held'."
        # THE SETS CAME BACK CLEANLY SEPARATED. So: on this checkpoint, two
        # same-species figures DO bind hair-colour-to-garment when each pair
        # is written inside ONE person clause and the body count is right. The
        # merge seen at n=1 was a symptom of having one body for two described
        # sets, not of attributes being unbindable. That is a better world
        # than the one the law described, and the honest prior for two-figure
        # plates ("1 in 15") is too pessimistic for THIS construction.
        #
        # THE ONE VARIABLE: THE HEAD TURN. Positive stays BYTE-IDENTICAL to
        # r2, seed unchanged, so the negative's three added terms are the only
        # difference. `looking at viewer, facing viewer, face` did not reach
        # it, and the reason is legible: THE MEN TURNED TOWARD EACH OTHER, NOT
        # TOWARD THE LENS, and none of those three forbid that. `looking back,
        # profile, from side` name the thing that actually happened. Three
        # terms, ONE variable -- the same shape as (8,4)'s giant-terms cluster.
        #
        # CORRECTION, 2026-08-16, second lane, re-checked on a 7x crop of each
        # head before this rev was fired: "THE MEN TURNED TOWARD EACH OTHER" is
        # HALF WRONG and is left standing above with this note beneath it. Only
        # the LEFT man turns inward -- a full profile, brow, nose, lip, chin and
        # the corner of an eye. The RIGHT man turns OUTWARD, away from his
        # companion, to frame right; his crop shows a jaw and cheek edge and no
        # eye. So the two heads rotate in OPPOSITE directions, which is not
        # "two men angled into a conversation" and weakens the reading that
        # r2's P3 failure is the argument the script asks for. It does NOT
        # change this rev: neither rotation is toward the lens, so the three
        # terms already in r2's negative still cannot reach either of them, and
        # `looking back, profile, from side` name both an inward profile and an
        # outward one. Right fix, imprecise reason; the reason is now accurate.
        #
        # WHY THIS IS NOT A COSMETIC QUIBBLE, and it is the reason a whole
        # sample is spent on it: beat 11's recorded fault is IDENTITY COLLAPSE
        # DURING A TURN -- "the near guard's bald scalp fills in with dark
        # hair CONTINUOUSLY across f16-f21 AS HE TURNS HIS BACK". A plate that
        # already starts mid-rotation hands the render the exact motion in
        # which the previous take lost the man. A square-backed plate does not.
        #
        # AND THE AUTHORSHIP TENSION IS FLAGGED, NOT RESOLVED HERE. The script
        # line is "The guards walk away ARGUING, BACKS TO CAMERA" and the
        # done_when is "backs turned, STILL ARGUING". Heads angled toward each
        # other is one legitimate way to read an argument with backs turned,
        # so r2's P3 failure may be what the beat actually wants. THAT IS NOT
        # THIS LANE'S CALL. r3 exists so the choice is made between TWO
        # PICTURES rather than guessed at: r2 keeps its head turn, r3 tries a
        # square back, and both stay on disk.
        #
        # THE PLATE BAR AND THE FAIL MODES ARE UNCHANGED, as committed in
        # e4279ce5 before any pixel existed.
        "slug": "they-leave",
        "prompt": (
            "2boys, from behind, full body, wide shot, two guard men "
            "standing together in tall grass, tall grass background, one "
            "man with dark cropped hair in a plain tan tunic, one man with "
            "light sandy hair in a dark brown tunic, cloth sash of office, "
            "dark trousers and boots, sunny day, masterpiece, best quality"
        ),
        # Restated byte for byte from r2 apart from the three head-turn terms,
        # which are the single variable. Exit 6 requires the restatement and
        # is right to.
        "negative": (
            "text, looking at viewer, facing viewer, face, looking back, "
            "profile, from side, close-up, "
            "portrait, distant, small figure, bald, 1boy, 3boys, solo, "
            "sky, horizon, white background, simple background, "
            "holding object, clipboard, armor, helmet, knight, child, "
            "photorealism, 3d render, night"
        ),
        # ------------------------------------------------------------------
        # R3 VERDICT, appended 2026-08-16 by the third lane on this thread.
        # r3 was DRAWN at 19:28, three minutes after the commit that
        # pre-registered it, and then went unjudged: the lane that fired it
        # died holding the verdict, as the lane before it had. The pixels were
        # on disk the whole time. Judged here by opening the PNG and 7x crops
        # of both heads and both hands, against the SAME bar from e4279ce5 --
        # no re-scoping, and beat 11's own action quoted from its own node.
        #
        #   P1 the APPROVED PAIR ......... PASS, and unchanged from r2. LEFT
        #      dark cropped hair over a pale tan tunic-coat, RIGHT light sandy
        #      hair over mid-brown. Neither bald, not swapped.
        #   P2 two whole figures ......... PASS. Exactly two, full-length to
        #      the boots, no third body in either band.
        #   P3 backs turned, no face ..... PASS. THIS IS THE FIX. At 7x the
        #      left head is a pure rear view -- back of the skull, one ear,
        #      NO brow, NO nose, NO eye, none of the profile edge r2 showed.
        #      The right head is also pure rear. The three added negative
        #      terms reached both heads, and only the heads: nothing else in
        #      the frame moved.
        #   P4 >=25% of frame height ..... PASS, ~35% (crown y255 to boot
        #      y690 of 1216).
        #   P5 no vacancy ................ PASS, 0.47 torsos, measured (below).
        #   P6 no props .................. PASS AS WRITTEN, SAME NAMED DEFECT.
        #      The narrow dark strap still hangs from guard B's left hand and
        #      still ends in a small dark tab at mid-thigh. It SURVIVED a
        #      revision whose negative carries `holding object, clipboard`,
        #      at the same seed. Two samples is not one, and a negative that
        #      names the thing twice has now failed to remove it twice --
        #      the same shape as beat 08 r4's finding that naming the invited
        #      noun in the negative removes it not at all. Clearing this is a
        #      POSITIVE-side job (give the hand something to be, or crop it),
        #      and it is the one open defect on this plate.
        #   P7 field in the plate ........ PASS.
        # SEVEN OF SEVEN PASS. THE PLATE MEETS THE BAR. The ladder's third
        # rung landed on the first sample, and the count and the identity
        # BOTH survived it untouched -- so per the standing instruction the
        # last seed is NOT spent here. Beat 11 stops at r3.
        #
        # A MEASURE WAS RETIRED TO GET P5'S NUMBER, and the retirement is
        # worth more than the number. P5 was first measured as the largest
        # CONNECTED region of low local variance. Overlaid back onto the
        # frames it was obviously wrong: the "largest flat blob" in r2 had a
        # bounding box spanning the entire frame width (x0-830) while holding
        # only 45k px^2 -- a stringy filament threading the gaps BETWEEN
        # grass strokes, not a hole. Connected low-variance pixels measure
        # brush spacing. The vacancy law is about a CONTIGUOUS AREA BIG
        # ENOUGH TO GROW A NOUN IN, so the replacement measures the largest
        # INSCRIBED axis-aligned flat rectangle.
        #
        # TWO THINGS THE REPLACEMENT'S OWN CHECKS CAUGHT, both of which would
        # have shipped a confident wrong number:
        #  1. THE OBVIOUS CONTROL WAS INVALID. b17-bigbody r2 is this repo's
        #     canonical vacancy failure -- a flat margin that grew six goblin
        #     heads -- and it measured LOW. Correctly: by the time the frame
        #     exists the hole has been FILLED, so it is no longer there to
        #     measure. A VACANCY MEASURE CANNOT RETRO-DIAGNOSE A FILL; the
        #     defect consumes its own evidence. It can only answer the
        #     forward question, which is the one that matters for a plate:
        #     is there room left for the ANIMATOR to grow something.
        #  2. float32 WAS DESTROYING THE VARIANCE. The g^2 integral image
        #     reaches ~2.6e10 over a 1MP frame and sqrt(E[g^2]-E[g]^2) then
        #     loses the answer to catastrophic cancellation. A DEAD CONSTANT
        #     injected rectangle measured as 52% flat. float64 fixed it, and
        #     it means the original filaments were partly precision noise.
        # Validated the only way that is not circular: inject flat rectangles
        # of KNOWN size into a real frame and require recovery. 400x250,
        # 200x300 and 105x240 all recovered within the ~10px inward erosion
        # the 11px window predicts; a 60x60 correctly loses to the larger real
        # sky band; heavy noise yields no false hole. ONLY THEN was it used.
        # Numbers, largest inscribed flat box in torsos (torso = 105x240 px,
        # measured off r3's left figure): b11 r1 0.41, r2 0.49, R3 0.47, all
        # of them a thin strip at the very top of the frame and none of them
        # in the field. b17-bigbody r3 0.81. Well under the one-torso bar.
        # ------------------------------------------------------------------
    },
    (11, 4): {
        # ==================================================================
        # 2026-08-16, FOURTH LANE. THE STRAP, AND ONLY THE STRAP.
        # WRITTEN AND COMMITTED BEFORE THE PIXEL, as e4279ce5's bar was.
        # ==================================================================
        # WHAT IS NOT IN QUESTION: r3 PASSES 7/7 AND REMAINS THE BEAT-11
        # DELIVERABLE UNLESS THIS REV BEATS IT. Beat 11 is not re-opened. This
        # rev exists because r3 carries ONE named defect -- the narrow strap
        # hanging from guard B's left hand -- and because that defect is about
        # to be drawn three more times: beats 05, 10 and 09 all stage the same
        # cast with the same clause structure. Solving it here costs one seed;
        # not solving it here costs three plates.
        #
        # THE FACT THAT FORCED A POSITIVE-SIDE ANSWER. The strap survived r3,
        # whose negative carries BOTH `holding object` AND `clipboard`, at the
        # same seed, with the rest of the frame demonstrably reachable (the
        # three head-turn terms moved both heads in the same revision). So the
        # negative is not weak here, it is NOT REACHING THIS OBJECT. That is
        # the third instance of the standing law -- beat 08 r4's colossus
        # survived `giant, colossal, monster, kaiju, statue, face in the sky`,
        # beat 17 r2 grew goblin heads with `2boys` in the negative, and now
        # this. All three were beaten, or must be, on the POSITIVE side.
        #
        # THE HYPOTHESIS, AND IT IS SPECIFIC ENOUGH TO BE WRONG. The strap is
        # THE SASH. Read the positive as the tokenizer reads it:
        #
        #   ... one man with light sandy hair in a dark brown tunic,
        #       cloth sash of office,
        #       dark trousers and boots, ...
        #
        # `cloth sash of office` is a HOMELESS CLAUSE. It is the only narrow
        # cloth band named anywhere in the prompt; it belongs to no person
        # clause; it sits IMMEDIATELY AFTER GUARD B's clause, which is exactly
        # where CLIP adjacency would bind it; and A SASH OF OFFICE IS WORN
        # ACROSS THE CHEST, WHICH THIS CAMERA CANNOT SEE. The prompt therefore
        # asks for a visible thing and gives it nowhere visible to be. What
        # came back is a narrow pale-tan cloth band with a squared tab end,
        # hanging at the one place on B that the camera does see -- his near
        # hand. Two details fit this and fit nothing else: it is on B and not
        # on A (adjacency), and it is cloth-coloured and cloth-shaped rather
        # than board-shaped (a clipboard vestige would be a rectangle).
        #
        # This is the vacancy law wearing different clothes. There, an empty
        # REGION with no noun of its own gets filled with the largest noun in
        # the prompt. Here, a NOUN with no region of its own gets placed on
        # the nearest surface the camera can see. Same mechanism -- the model
        # will not simply drop something the prompt asked for -- and therefore
        # the same fix: GIVE IT A HOME THE CAMERA CAN SEE, rather than
        # forbidding it.
        #
        # THE ONE VARIABLE, and it is four words. `cloth sash of office`
        # becomes `a cloth sash of office across his back`. The sash is kept,
        # because it is the founder's cast (`authored_guard_sheet_a`,
        # `authored_guard_b_derived`, both carry it) and deleting a cast
        # attribute to dodge a rendering bug is the wrong trade. Everything
        # else -- every other byte of the positive, the WHOLE negative
        # restated below byte for byte, the seed, the size, the steps, the
        # guidance -- is r3's.
        #
        # WHAT IS DELIBERATELY NOT DONE, so the attribution stays clean.
        # NOT touching the negative: adding a third naming of the object would
        # confound the one thing this rev measures. `holding object, clipboard`
        # STAY, unchanged, precisely so that a clearance here is attributable
        # to the positive edit and not to a stronger prohibition.
        # NOT adding `empty hands` or `arms at their sides` in the same rev:
        # that is the OTHER positive-side instrument and it is r5's if this
        # fails. Two levers in one sample is one sample wasted.
        #
        # THE BAR. ALL SEVEN OF e4279ce5's P1-P7 STILL APPLY, UNCHANGED AND
        # UNSOFTENED, plus one:
        #   P8 NOTHING HANGS FROM EITHER HAND. No strap, cord, lanyard, tab,
        #      strip or pendant object at, from, or beside either man's hands,
        #      and nothing detached anywhere in frame. Judged at 10x on both
        #      hands of both men, not at 1x -- at 1x this strap is a two-pixel
        #      line and r1 and r2 both "passed" it by not being looked at
        #      closely enough. A SASH RENDERED AS A BAND ON B's BACK OR WAIST
        #      IS NOT A FAIL OF P8 -- that is the sash doing what it was just
        #      told to do, and it is cast-correct.
        #
        # OUTCOMES NAMED IN ADVANCE, so none can be reinterpreted afterwards:
        #   A. STRAP GONE, P1-P7 STILL HOLD -> hypothesis supported, r4 becomes
        #      the beat-11 plate, and the RULE CARRIES to 05, 10 and 09: in a
        #      rear or three-quarter view, every garment element whose only
        #      home is on the FRONT must be re-anchored to a surface the
        #      camera can see, or left out. That rule is what the other three
        #      plates get, not this prompt.
        #   B. STRAP GONE BUT P1-P7 DEGRADE (a face turns, the count breaks,
        #      the costumes swap) -> the edit reshuffled the image, r3 STANDS
        #      as the beat-11 deliverable, and the strap finding is recorded
        #      as "reachable, at a cost" rather than banked.
        #   C. STRAP SURVIVES UNCHANGED -> THE HYPOTHESIS IS DEAD and it is
        #      written down as dead. The sash is not the strap. r5 then runs
        #      the discriminating test the honest way: DELETE the sash clause
        #      outright. If the strap goes with it, the sash was the cause and
        #      anchoring merely failed to bind; if the strap is still there
        #      with no sash in the prompt at all, the object is coming from
        #      somewhere else entirely -- the likeliest remaining source being
        #      the checkpoint's own prior for a hand at a man's side -- and
        #      the answer is to give the hands a positive state of their own.
        #   D. THE STRAP MOVES to guard A, or a back sash appears AND the
        #      strap stays -> the strap was never the sash; go straight to
        #      r5's hand-state instrument and say so.
        "slug": "they-leave",
        "prompt": (
            "2boys, from behind, full body, wide shot, two guard men "
            "standing together in tall grass, tall grass background, one "
            "man with dark cropped hair in a plain tan tunic, one man with "
            "light sandy hair in a dark brown tunic, a cloth sash of office "
            "across his back, dark trousers and boots, sunny day, "
            "masterpiece, best quality"
        ),
        # Restated BYTE FOR BYTE from r3. Not one term added, and the two
        # terms that name the strap are left in place on purpose (see above).
        "negative": (
            "text, looking at viewer, facing viewer, face, looking back, "
            "profile, from side, close-up, "
            "portrait, distant, small figure, bald, 1boy, 3boys, solo, "
            "sky, horizon, white background, simple background, "
            "holding object, clipboard, armor, helmet, knight, child, "
            "photorealism, 3d render, night"
        ),
        # ------------------------------------------------------------------
        # R4 VERDICT, appended by the lane that fired it, same session.
        # OUTCOME C. THE HYPOTHESIS IS DEAD AND IT IS WRITTEN DOWN AS DEAD.
        # ------------------------------------------------------------------
        # THE SASH BOUND. It is not a case of "the anchor failed to reach it":
        # r4 renders a plainly visible WAIST SASH ON BOTH MEN -- a cream-white
        # band on the left man, a dark red-brown one on the right -- where r3
        # had none at all. The four words did exactly what they were asked to
        # do and the sash now has a home the camera can see.
        #
        # AND THE STRAP IS STILL THERE. Same man, same hand: a narrow pale
        # strap hangs from guard B's LEFT hand down to mid-thigh, judged at 5x
        # and 8x. So the strap is NOT the sash. The two now coexist in one
        # frame, which is a stronger refutation than the deletion test the
        # pre-registration reserved for this outcome -- deleting the clause
        # can no longer teach us anything the coexistence has not already
        # shown, so r5 does NOT spend a seed on it and goes straight to the
        # other instrument. The pre-registered plan is departed from HERE, in
        # writing, and for a stated reason.
        #
        # AND IT COST P1, which is outcome B on top of C. The right man's hair
        # came back DARK BROWN, not light sandy -- at 4x both heads are dark
        # and the pair is no longer told apart by hair, which is the single
        # attribute P1 is built on. The garment values collapsed with it
        # (mid-brown and grey-brown, not pale tan against dark brown). FOUR
        # WORDS IN THE MIDDLE OF THE PROMPT MOVED TWO ATTRIBUTES AT THE OTHER
        # END OF IT, at the same seed. That is the real cost of an edit on
        # this checkpoint and it is why r3 is not re-opened.
        #
        # SCORING, honestly: P1 FAIL, P2 pass, P3 PASS (both heads pure rear,
        # the three head-turn terms held), P4 pass ~36%, P5 pass, P6 pass as
        # written, P7 pass, P8 FAIL. TWO OF EIGHT FAIL.
        # **R3 REMAINS THE BEAT-11 DELIVERABLE.** r4 is an experiment that
        # returned a negative result and is kept on disk as evidence, not as a
        # candidate.
        #
        # WHAT SURVIVES AND CARRIES FORWARD: giving a homeless garment clause
        # a camera-visible home DOES bind on this checkpoint (the sash proves
        # it), so the rule is still worth having for 05/10/09 -- it just is
        # not the answer to the strap.
        # ------------------------------------------------------------------
    },
    (11, 5): {
        # ==================================================================
        # THE SECOND POSITIVE-SIDE INSTRUMENT, AND THE LAST SEED BEAT 11 GETS.
        # Pre-registered before the pixel, as r4's was.
        # ==================================================================
        # WHAT r4 SETTLED: the strap is not the sash, and the negative does
        # not reach it (`holding object` + `clipboard`, twice, same seed).
        # What is left is the hand itself. r3 and r4 both describe two men in
        # full-length rear view and NEVER SAY WHAT THEIR HANDS ARE DOING. An
        # unspecified hand at a man's side is a region with no noun of its
        # own, and this checkpoint's answer to a region with no noun is to put
        # something in it -- which is the vacancy law exactly, at the scale of
        # a hand instead of a sky.
        #
        # THE ONE VARIABLE: r3's positive, BYTE-IDENTICAL, plus one tag that
        # tells the hands what to be. `loose fists at their sides`.
        #
        # WHY THAT WORDING AND NOT `empty hands`. CLIP CANNOT REPRESENT
        # NEGATION. `empty hands` embeds as something very close to `hands`,
        # and a phrase that names the unwanted thing in order to deny it is
        # the same instrument that has now failed three times on this repo's
        # plates. A FIST IS A POSITIVE SHAPE: it is a closed hand, it is a
        # real tag on this checkpoint's vocabulary, it leaves no aperture for
        # a strap to pass through, and `at their sides` puts both arms where
        # the walk needs them. It also happens to be right for the beat --
        # the script line is two men ARGUING as they walk away.
        #
        # WHY THE BASE IS r3 AND NOT r4. r4 lost P1. r3 is the 7/7 plate and
        # the only thing wrong with it is the strap, so the strap fix is
        # tested against the picture that is otherwise correct. The sash goes
        # back to r3's homeless wording deliberately: it is a KNOWN quantity
        # there (it renders as nothing visible, which is harmless in a rear
        # view) and re-anchoring it is a second variable.
        #
        # THE BAR IS UNCHANGED: e4279ce5's P1-P7, plus P8 from (11,4) --
        # nothing hangs from either hand, judged at 8x-10x on all four hands.
        #
        # OUTCOMES, named in advance:
        #   A. STRAP GONE, P1-P7 HOLD -> r5 replaces r3 as the beat-11 plate,
        #      and THE RULE THAT CARRIES TO 05, 10 AND 09 IS: name what the
        #      hands are doing, positively, in every guard plate. That rule is
        #      what those three beats inherit -- not this prompt.
        #   B. STRAP GONE BUT P1-P7 DEGRADE (r4 showed a mid-prompt edit can
        #      move hair colour at the far end) -> r3 STANDS, and the rule is
        #      recorded as "reachable, at a cost", to be applied to 05/10/09
        #      where their prompts are being authored from scratch anyway and
        #      pay no such cost.
        #   C. STRAP SURVIVES A DEFINED HAND -> both positive-side instruments
        #      have failed, the object is not attributable to any clause in
        #      the prompt, and BEAT 11 STOPS. r3 stands with the strap logged
        #      as an open defect, 05/10/09 are drawn WITHOUT any strap-specific
        #      wording (since none of it works), and each is checked at 8x for
        #      the same artifact. That is a real answer and it is cheaper than
        #      a fourth seed guessing.
        "slug": "they-leave",
        "prompt": (
            "2boys, from behind, full body, wide shot, two guard men "
            "standing together in tall grass, tall grass background, one "
            "man with dark cropped hair in a plain tan tunic, one man with "
            "light sandy hair in a dark brown tunic, cloth sash of office, "
            "loose fists at their sides, dark trousers and boots, sunny day, "
            "masterpiece, best quality"
        ),
        # Restated BYTE FOR BYTE from r3. `holding object, clipboard` stay in
        # for the same reason as r4: a clearance must be attributable to the
        # positive edit, and they have already been shown not to reach it.
        "negative": (
            "text, looking at viewer, facing viewer, face, looking back, "
            "profile, from side, close-up, "
            "portrait, distant, small figure, bald, 1boy, 3boys, solo, "
            "sky, horizon, white background, simple background, "
            "holding object, clipboard, armor, helmet, knight, child, "
            "photorealism, 3d render, night"
        ),
    },
    # ======================================================================
    # 2026-08-17, THE r2 RUNG FOR ALL THREE GUARD PLATES. ONE VARIABLE EACH,
    # AND EACH VARIABLE IS THE ONE THE SEED SWEEP IDENTIFIED AS WORDING.
    # WRITTEN AND COMMITTED BEFORE ANY OF THE THREE PIXELS.
    # ======================================================================
    # WHY THREE REVS IN ONE COMMIT IS NOT A BATCH. A ladder cannot be
    # parallelised -- rung 2 depends on rung 1's verdict -- but THREE LADDERS
    # CAN RUN SIDE BY SIDE, because beat 05's camera angle, beat 09's eyelids
    # and beat 10's prop ownership are independent questions on independent
    # plates. Each of these is rung 2 of its own ladder, off its own judged
    # rung 1, fired on its own machine. Nothing here depends on anything else
    # here.
    # WHAT IS DELIBERATELY NOT FIXED IN ANY OF THEM. D2 (glasses landing on
    # both men in a two-guard plate) is a CAST question, not a wording bug to
    # be solved in a lane: either guard A's wire-rims are left out of 05 and 10
    # or guard B is drawn wearing them, and that is R4's call. `glasses` is
    # therefore left EXACTLY where r1 had it in both two-figure prompts, so
    # that whatever the founder decides is decided against pictures that
    # isolate one variable rather than pictures that moved two.
    # THIS IS EACH PLATE'S FOURTH AND LAST SEED IN THIS LANE. Three went to
    # the r1 sweep. If a rung 2 fails, the honest report is "the variable was
    # identified and the fix did not take", not a fifth guess.
    (5, 2): {
        # ------------------------------------------------------------------
        # BEAT 05, r2. THE ONE VARIABLE: `horizon` IS DELETED FROM THE
        # NEGATIVE. Nothing else moves -- not one byte of the positive, not the
        # seed, not the other twenty-five negative terms, and `sky` STAYS.
        #
        # WHY. D4 came back 3 of 3 wording, not seed: every beat 05 render is a
        # downward high-angle over an open field with no horizon band and no
        # hedgerow, and at s3 it is so high and so far that the count breaks to
        # THREE FIGURES -- this beat's historical fault -- with `distant, small
        # figure` sitting in the negative and failing to hold. The mechanism
        # named in advance and now tested: A FRONT-FACING WIDE SHOT HAS TO PUT
        # A HORIZON SOMEWHERE. Forbid it and the only place left is above the
        # frame, so the camera tilts down until it is gone, and everything else
        # follows -- the men shrink, the field opens into one flat expanse
        # (61.4% of r1s1 is flat against 34.6% on the b11 plate that passed),
        # and `hedgerow behind` has no ground to stand on because there is no
        # `behind` in a plan view.
        # `sky` STAYS ON PURPOSE. The vacancy law says an empty upper band gets
        # filled with the largest noun in the prompt, and deleting `hedgerow`
        # was never the problem -- what is wanted is a horizon WITH a hedgerow
        # on it, not open sky. If r2 returns eye level with a hedgerow and no
        # sky, the mechanism is confirmed and the fix is free. If it returns a
        # sky band anyway, then `sky` and `horizon` were doing one job and the
        # trade is a real one, to be named rather than papered over.
        # WHY NOT ALSO FIX THE POSE. `arms swinging` came back as both men
        # flinging their arms wide and overhead at 3 of 3 -- also wording. It
        # is left alone because a plan view at that distance is exactly the
        # framing in which a jog reads as a jumping-jack, so the camera is the
        # candidate CAUSE of the pose fault and not an independent second bug.
        # If eye level returns and the arms are still overhead, THEN the pose
        # is its own fault and beat 05 has a fifth-seed question worth asking.
        #
        # THE BAR IS UNCHANGED: P1-P8 exactly as committed in 7b193483, and
        # good staging with the wrong men is still a FAIL. What r2 is scored
        # on above all is P2 (exactly two whole figures), P5 (vacancy, judged
        # by the overlay and the flat FRACTION against b11 r3's 34.6%, never by
        # the retired rectangle alone) and the presence of a hedgerow.
        # OUTCOMES NAMED IN ADVANCE:
        #   A. EYE LEVEL, HEDGEROW PRESENT, TWO FIGURES -> the mechanism is
        #      confirmed, and the rule that carries to every future
        #      front-facing plate is: DO NOT FORBID `horizon` IN A SHOT THAT
        #      NEEDS ONE.
        #   B. EYE LEVEL BUT THE COUNT OR THE CAST DEGRADES -> the camera fix
        #      took and cost something; r1s1 and r2 both stay on disk and the
        #      choice is between two pictures.
        #   C. STILL HIGH-ANGLE -> `horizon` was not the lever, the mechanism
        #      is dead as stated, and beat 05's plate is NOT solved by a
        #      negative-side edit. The next instrument would be a positive-side
        #      one (`eye level`, `low angle`, a named horizon noun) and this
        #      lane says so rather than spending its last seed guessing.
        "slug": "the-patrol",
        # BYTE-IDENTICAL to the base draft. Not one character differs.
        "prompt": (
            "2boys, full body, wide shot, two guard men jogging together in "
            "tall grass, hedgerow behind, one man with dark cropped hair, "
            "glasses, a tan tunic and a white waist sash, one taller man "
            "with light sandy hair, a cream shirt, a white shoulder sash and "
            "a brown wrap skirt, arms swinging, masterpiece, best quality"
        ),
        # Restated byte for byte from the base draft APART FROM the deletion of
        # `horizon`, which is the single variable. Exit 6 requires the
        # restatement and is right to. 70/77.
        "negative": (
            "text, bald, bare head, 1boy, 3boys, solo, crowd, girl, child, "
            "from behind, back view, close-up, portrait, distant, small "
            "figure, sky, white background, simple background, "
            "armor, helmet, knight, weapon, holding object, clipboard, "
            "photorealism, 3d render, night"
        ),
        # ------------------------------------------------------------------
        # R2 VERDICT. macbook1, 70.8s, seed 20260817 unchanged.
        # OUTCOME A ON THE CAMERA. THE MECHANISM IS CONFIRMED.
        # ------------------------------------------------------------------
        # DELETING ONE WORD FROM THE NEGATIVE MOVED THE CAMERA. r1s1 at this
        # exact seed is a downward plan view over an open field. r2 is close to
        # EYE LEVEL, with a horizon band, a line of dark bushes reading as a
        # hedgerow along the top left and right, and distant hills behind it.
        # `hedgerow behind` had been in the positive all along and rendered
        # nothing three times; it rendered here the moment the horizon it needs
        # to stand on was allowed to exist. So the rule that carries to every
        # future front-facing plate is: DO NOT FORBID `horizon` IN A SHOT THAT
        # NEEDS ONE, and a clause that names something "behind" is dead in a
        # plan view because a plan view has no behind.
        # THE TRADE NAMED IN ADVANCE IS REAL AND IS NOT PAPERED OVER. `sky`
        # stayed in the negative and a pale sky band arrived anyway. The two
        # terms were doing one job; you cannot have a horizon and no sky.
        # SCORING, against the unchanged bar: P1 FAIL, P2 PASS, P3 PASS,
        # P4 PASS ~41%, P5 IMPROVED BUT NOT PASSED, P6 PASS, P7 PASS,
        # P8 PASS-AND-OVER-APPLIED. Detail on the three that need it:
        #   P1 is FAIL at this seed and THAT WAS EXPECTED AND IS NOT THE
        #      VARIABLE. Both men are dark-haired with glasses, exactly as
        #      r1s1 was, because the seed was deliberately held to isolate the
        #      camera. D1 already established that sandy hair binds at 4 of 4
        #      OTHER seeds, so beat 05's next step is A SEED BATCH OF THIS
        #      EXACT WORDING, not another word.
        #   P5 flat fraction 61.4% -> 52.6%, against 34.6% on the b11 plate
        #      that passed. Better, and still not there. The rectangle measure
        #      went the WRONG WAY over the same improvement (0.61 -> 0.68
        #      torsos), which is the third demonstration in one day that it
        #      cannot be trusted on a sparse field.
        #   P6 PASS at 4x on all four hands -- open empty palms, closed empty
        #      fingers, no strap, no cord, nothing detached. And guard A's WIDE
        #      WHITE WAIST SASH renders properly here for the first time, with
        #      a trailing end, which is a cast attribute arriving rather than
        #      drifting.
        # THE POSE IS PARTLY ITS OWN FAULT, WHICH THE PRE-REGISTRATION SAID
        # WOULD BE THE ANSWER IF THIS HAPPENED. r1's men fling both arms
        # overhead; r2's near man holds his arms out to the sides and the far
        # man has one arm raised. Better, not a jog. So the plan view was
        # AGGRAVATING the pose and is not the whole of it, and `arms swinging`
        # is a live second question for beat 05 -- with the hand answer intact
        # either way, since it is `arms swinging` that keeps the hands empty.
        #
        # THE SEED BATCH OFF THIS RUNG, RULE WRITTEN BEFORE IT RENDERS. This is
        # NOT a new recipe and needs no new sample gate: the wording has been
        # drawn and judged, and D1 already showed sandy hair binds at 4 of 4
        # seeds other than 20260817. The only open question about beat 05's
        # WORDING is whether the camera fix survives a seed change, and whether
        # P1 comes right when it does. `--seeds 4` off base 20260817 gives
        # three fresh draws plus a determinism re-check.
        #   E1 EYE LEVEL AT 2 OR 3 OF THE 3 FRESH SEEDS -> the camera fix is a
        #      property of the wording and beat 05's framing is SOLVED. At 0 or
        #      1 of 3 it was this seed's luck and the deletion is not a lever.
        #   E2 SANDY HAIR AT ANY FRESH SEED WITH THE CAMERA STILL AT EYE LEVEL
        #      -> that picture is beat 05's plate candidate, and the first
        #      cast-correct staged picture the beat has ever had. Sandy hair at
        #      NO fresh seed here, having bound at 4 of 4 before the camera
        #      changed, would mean the two interact -- a new and worse problem,
        #      to be written down rather than worked around.
        #   E3 THE COUNT. Three figures at any seed keeps beat 05's historical
        #      count fault open at eye level too; two at all three closes it.
        # Nothing is picked here either: a candidate is proposed, never
        # promoted, and P1 is judged against the founder's own sheet.
        #
        # ------------------------------------------------------------------
        # SEED-BATCH RESULT. E1 FAILS AND THE r2 VERDICT ABOVE IS RETRACTED.
        # ------------------------------------------------------------------
        # The re-rendered s1 is byte-identical to the committed r2s1, so the base
        # is sound and the three fresh draws are the only difference.
        #   E1 EYE LEVEL ... FAILS, 0 OF 3. s2 (20260818) is a downward plan view
        #      with a pale haze where the horizon was. s3 (20260819) is higher
        #      still, no horizon, no hedgerow, vast empty grass. s4 (20260820) is
        #      a full plan view and a collapse. THE RULE SAID: "at 0 or 1 of 3 it
        #      was this seed's luck and the deletion is not a lever." IT WAS THIS
        #      SEED'S LUCK. THE `horizon` DELETION IS NOT A LEVER, the r2 verdict
        #      above claiming "OUTCOME A ON THE CAMERA, THE MECHANISM IS
        #      CONFIRMED" IS WRONG, and it is left standing with this beneath it
        #      because the disagreement is the record. It was an n=1 claim made by
        #      a lane that had spent the previous hour proving n=1 claims wrong.
        #      WHAT SURVIVES, LABELLED AS n=1: the one frame with a horizon is the
        #      one frame where `hedgerow behind` rendered, across seven renders in
        #      which it otherwise rendered nothing. A clause naming something
        #      "behind" needs a behind. That is a correlation, not a mechanism.
        #   E2 SANDY HAIR ... BINDS, 3 OF 3 fresh seeds, so D1 holds and the
        #      camera edit did not break it -- there is no interaction. BUT NO
        #      FRAME QUALIFIES AS A CANDIDATE, because E2 required sandy hair
        #      WITH the camera at eye level and no frame has both.
        #   E3 THE COUNT ... STAYS OPEN, and worse than before. s2 two men. s3 two
        #      figures of which ONE IS A GIRL -- bobbed hair, a dress, no glasses
        #      -- with `girl, child` in the negative. s4 FOUR FIGURES: a
        #      SHIRTLESS adult, a second man, and TWO SMALL BLOND CHILDREN at the
        #      bottom edge, again with `child` in the negative. Beat 05's
        #      historical count fault is not fixed by a plate at eye level or
        #      otherwise, and the negative does not reach children either.
        #   Also across all three: MODERN WHITE SNEAKERS every time, no sash on
        #      either man at s2 or s4, and no hedgerow anywhere.
        # BEAT 05 IS NOT SOLVED. Its best picture remains r2s1, which is one
        # lucky draw and is honestly describable only as "1 in 4 at this wording".
        # The next instrument is POSITIVE-SIDE and this lane does not fire it:
        # `eye level` or `low angle` as a leading framing tag, where framing tags
        # are known to bind, rather than a deletion from the negative.
        # ------------------------------------------------------------------
    },
    (9, 2): {
        # ------------------------------------------------------------------
        # BEAT 09, r2. THE ONE VARIABLE: THE EYE STATE. `eyes open` is added
        # to the positive and `closed eyes` to the negative. That is one
        # variable expressed on both sides of the same tag, not two.
        #
        # WHY. D5 came back 3 of 3: the man's eyes are SHUT at every seed.
        # `thoughtful` plus `mouth closed` describes a man at rest, and the
        # checkpoint drew one -- three times, including one where a green leaf
        # arrived between his lips. Beat 09's script line is "Guard 1's face
        # WORKS THROUGH IT, slowly" and its done_when is "close on Guard 1's
        # face working through the thought": a man with his eyes closed is not
        # working through anything, he is dozing in a field.
        # WHY BOTH SIDES FOR ONE VARIABLE, when the standing lesson is that
        # negatives fail on nouns the positive invited. `closed eyes` is not an
        # invited noun here -- the positive will now ask for the OPPOSITE
        # state, so the negative is reinforcing a positive instruction rather
        # than trying to subtract something the prompt asked for. That is the
        # one configuration in which a negative term has reliably worked on
        # this repo's plates: (11,3)'s three head-turn terms moved both heads
        # precisely because the positive said `from behind`.
        # WHAT IS NOT TOUCHED. `mouth closed` STAYS, and it stays for a
        # measured reason that has not changed: beat 11's best take turns guard
        # B into full profile WITH AN OPEN MOUTH from f008, so this checkpoint
        # animates a talking man's head, and beat 09 is a man thinking BEFORE
        # he speaks. The tunic colour is also left alone even though it drifted
        # white / white-and-black / ORANGE across the three seeds -- that is a
        # second fault and it is named in the r1 verdict, not fixed here.
        #
        # THE BAR IS UNCHANGED: P1-P7 exactly as committed in 7b193483,
        # including P3's head >=55% of frame height (r1s1 landed at ~53% and
        # that was recorded as a fail, not softened) and P1's "no glasses is a
        # FAIL" -- which has now passed three times running.
        # OUTCOMES NAMED IN ADVANCE:
        #   A. EYES OPEN, P1-P6 HOLD -> beat 09 has a usable plate and the rule
        #      that carries is: A FACE PLATE MUST NAME THE EYE STATE, because
        #      `thoughtful` alone reliably closes them.
        #   B. EYES OPEN BUT THE FACE CHANGES (hair, age, the glasses) -> the
        #      edit reshuffled the picture, r1 stays on disk beside it, and the
        #      finding is "reachable, at a cost".
        #   C. EYES STILL SHUT -> a positive state tag plus its negative cannot
        #      open this checkpoint's eyes on a `thoughtful` face, and the
        #      honest next instrument is a different EXPRESSION word entirely
        #      (`frowning`, `squinting in thought`) rather than an eyelid tag.
        #      Beat 09 would stop here for this lane and say so.
        "slug": "the-pause",
        # r1's positive with `eyes open` inserted before `thoughtful`. 68/77.
        "prompt": (
            "1boy, solo, close-up, face filling the frame, a guard man with "
            "dark cropped hair and wire-rim glasses, eyes open, thoughtful, "
            "mouth closed, a tan wrap tunic collar and a white sash on his "
            "shoulder, tall grass and a green hedgerow behind him, sunny "
            "day, masterpiece, best quality"
        ),
        # Restated byte for byte from r1 APART FROM `closed eyes`, the other
        # half of the single variable. 72/77.
        "negative": (
            "text, 2boys, 3boys, crowd, bald, closed eyes, hands, holding "
            "object, clipboard, armor, helmet, knight, child, girl, white "
            "background, simple background, grey background, blank "
            "background, plain background, sky, indoors, full body, wide "
            "shot, distant, photorealism, 3d render, dark, night"
        ),
        # ------------------------------------------------------------------
        # R2 VERDICT. macbook3, 137.1s, seed 20260817 unchanged.
        # OUTCOME A ON THE EYES. THE VARIABLE WORKED ON THE FIRST SAMPLE.
        # ------------------------------------------------------------------
        #   P7 EYES OPEN, MOUTH CLOSED ... PASS, and this is the fix. Both eyes
        #      are plainly open -- amber irises visible behind the lenses -- the
        #      mouth is closed, and the brows are drawn slightly down into a
        #      frown. It reads as a man working something out, which is the
        #      beat. Three seeds of r1 gave three shut faces; one added tag
        #      plus its mirror in the negative opened them at the first sample.
        #      THE RULE THAT CARRIES: A FACE PLATE MUST NAME THE EYE STATE.
        #      `thoughtful` on its own reliably closes them on this checkpoint,
        #      and the beat that needs a face working through a thought is
        #      exactly the beat that cannot afford that.
        #   P1 guard A with wire-rims ... GLASSES PASS FOR THE FOURTH TIME
        #      RUNNING, round wire frames, no drift to sunglasses. HAIR STILL
        #      FAILS, and it is scored as a fail: dark brown and shaggy where
        #      guard A's is near-black and CROPPED, and the face still reads
        #      young rather than adult. Closer than r1's mid-brown, not there.
        #      This is the one condition beat 09 has never met and it is the
        #      condition the beat exists to fix.
        #   P2 PASS one face. P4 PASS, real grass and leaves across the whole
        #      frame -- four for four on the fault this beat was blocked on.
        #      P5 PASS daylight. P6 PASS, no hand in frame.
        #   P3 head >=55% ... FAIL, AND IT GOT WORSE, WHICH IS REPORTED
        #      RATHER THAN ROUNDED. Read off a 50px ruler overlaid on the
        #      frame: crown y60, chin y648, so 588 of 1216 = 48%. r1s1 was
        #      ~53%. The bar was 55% and this is further from it.
        # FIVE OF SEVEN PASS. Beat 09 is the closest of the three plates and
        # its two open faults are now precisely stated: the framing is not
        # tight enough, and the hair and age are not guard A's. Neither is
        # touched here, because this rung tested the eyes and the eyes are the
        # only thing it may claim.
        #
        # THE SEED BATCH OFF THIS RUNG, RULE WRITTEN BEFORE IT RENDERS. Same
        # standing: a judged wording, not a new recipe. The question this one
        # answers has never been asked for a SINGLE-figure plate -- D1 settled
        # it only for two-figure ones -- and it is the question beat 09 is
        # actually blocked on:
        #   F1 IS THE BROWN SHAGGY HAIR A SEED EFFECT? Near-black cropped hair
        #      at 1 or more of the 3 fresh seeds -> yes, and beat 09's plate is
        #      a draw away rather than a rewrite away. Brown at all three, with
        #      `dark cropped hair` in the positive every time -> the hair is the
        #      WORDING and the beat needs a different colour word (`black
        #      hair`, which is this checkpoint's own tag, rather than `dark`)
        #      before anything else is tried.
        #   F2 DOES THE EYE FIX HOLD? Eyes open at 2 or 3 of 3 -> the tag is a
        #      lever and the rule stands. Open at 1 of 3 -> r2s1 was luck and
        #      the rule is retracted; three shut faces at r1 and one open one
        #      is not a lever.
        #   F3 DOES THE HEAD GET BIGGER? Head >=55% at any seed -> P3 is a draw
        #      variable, not a wording one. Under 55% at all three, having been
        #      48-53% at four renders -> the framing tag cannot reach it and
        #      `face filling the frame` is not enough.
        # No candidate is promoted from this batch either.
        #
        # ------------------------------------------------------------------
        # SEED-BATCH RESULT. F1 IS THE WORDING, F2 RETRACTS THE RULE, F3 IS A
        # SEED. The re-rendered s1 is byte-identical to the committed r2s1.
        # ------------------------------------------------------------------
        #   F1 THE HAIR IS THE WORDING, 7 OF 7. Brown at every single render this
        #      beat has had -- three r1 seeds and four r2 seeds -- with `dark
        #      cropped hair` in the positive every time. Never near-black, never
        #      cropped; mid-to-dark brown and shaggy at all seven. So per the
        #      rule as written, the next thing beat 09 tries is `black hair`,
        #      which is this checkpoint's own tag, instead of `dark`. THAT IS THE
        #      ONE CHANGE THIS BEAT NEEDS AND THIS LANE DOES NOT SPEND A FIFTH
        #      SEED ON IT -- it is named, measured and left for the next lane
        #      rather than guessed at now.
        #   F2 THE EYE RULE IS RETRACTED, exactly as pre-registered. Across the
        #      four r2 seeds the eyes are: s1 CORRECTLY OPEN, amber irises; s2 a
        #      WINK, one green eye open and one shut; s3 OPEN BUT BLANK WHITE,
        #      no irises and no pupils at all, which reads as a corpse and is a
        #      new defect worth naming; s4 SHUT. So a usable pair of eyes at
        #      1 OF 4. The rule said "open at 1 of 3 -> r2s1 was luck and the
        #      rule is retracted", and it is retracted in this file's docstring
        #      too. THE HONEST RESIDUE, which is not nothing: the tag DOES reach
        #      the eyelids, 3 of 4 moved against 0 of 3 without it. It is a rate,
        #      not a lever, and a beat that needs open eyes needs
        #      render-N-and-pick.
        #   F3 THE HEAD SIZE IS A SEED VARIABLE, NOT A WORDING LIMIT. s4's head
        #      spans from above the top edge (the crown is cropped) to a chin at
        #      y680, so at least 56% of frame height against the 55% bar -- P3
        #      PASSES at that seed, having failed at 48-53% across the four
        #      before it. Read off a 50px ruler overlaid on the frame, not
        #      estimated. So `face filling the frame` CAN reach the bar and the
        #      framing needs seeds, not new words.
        # BEAT 09 REMAINS THE CLOSEST OF THE THREE AND IS STILL NOT A PASS. Its
        # two settled wins hold across all seven renders: wire-rim glasses at
        # 7 of 7, and a real foliage background at 7 of 7 on the beat whose
        # recorded fault was "another blank background". Its three open faults are
        # now each classified: the HAIR is wording and has a named next word, the
        # HEAD SIZE is a seed, and the EYES are a 1-in-4 rate. No plate is
        # proposed for a render.
        # ------------------------------------------------------------------
    },
    (10, 2): {
        # ------------------------------------------------------------------
        # BEAT 10, r2. THE ONE VARIABLE: `hands behind his back` IS ADDED TO
        # GUARD A's CLAUSE. Four words, at the end of the man who must NOT be
        # holding the board. The negative is restated byte for byte and the
        # seed does not move.
        #
        # WHY THIS AND NOT A REWORDING OF THE BOARD CLAUSE. The sweep found the
        # board on the WRONG MAN at 3 of 3 -- guard A alone at s1 and s3, BOTH
        # men at s2 -- and it is not the seed. The board clause already sits
        # INSIDE guard B's person clause, immediately after his wrap skirt, and
        # B is already the FIRST man named. Every ordering lever this prompt
        # has is already pointed the right way and the prop still goes to
        # whichever figure the model draws nearest. So a prop does not bind to
        # its person clause the way hair and garments demonstrably do (D1: at
        # 10 s3 the cream shirt and brown wrap skirt bound to the blond man
        # while the tan tunic bound to the dark-haired one, in the same frame
        # where the board went to the wrong one).
        # THE INSTRUMENT IS THE LAW THIS LANE JUST ESTABLISHED, USED FOR A
        # SECOND PURPOSE. D3: an unspecified hand is an empty region and this
        # checkpoint puts a noun in it. Beat 10's own far man proved it -- a
        # bamboo pole at one seed and a DUPLICATE OF THE BOARD at another.
        # `hands behind his back` does two things with one clause: it removes
        # the empty region that grew the pole, and it removes the only other
        # pair of hands the board could be placed in. If the board is a noun
        # looking for hands, this is the shot where there is exactly one pair
        # available and they are already told to hold it.
        # IT IS ALSO RIGHT FOR THE BEAT, which is worth saying because a fix
        # that fights the script is not a fix: guard A is the man LISTENING in
        # beat 10 -- Guard 2 has the board and the line -- and hands behind the
        # back is what a listening bureaucrat's hands do.
        # THE COST IS NAMED: THIS PROMPT NOW MEASURES 77/77, the entire budget,
        # with zero headroom. Nothing was cut to make room, so no second
        # variable sneaked in, but it means beat 10 cannot take another
        # additive rung after this one -- the next thing tried here would have
        # to be a DELETION. That is a real constraint on this beat and it is
        # recorded now rather than discovered later.
        #
        # THE BAR IS UNCHANGED: P1-P8 exactly as committed in 7b193483, and P1
        # still fails on a board in the dark-haired man's hands even if
        # everything else holds. P6 is now judged on FOUR hands as always, with
        # A's two expected to be out of sight behind him -- HANDS HIDDEN BEHIND
        # A BACK IS NOT A FAIL OF P6; they were given a state and the state put
        # them there.
        # OUTCOMES NAMED IN ADVANCE:
        #   A. BOARD IN THE SANDY-HAIRED MAN'S TWO HANDS AND NOWHERE ELSE ->
        #      the prop-ownership problem is solved by OCCUPYING THE OTHER
        #      HANDS, which is a general rule for every two-figure plate with
        #      a prop, and it is a second, independent confirmation of the
        #      hand-vacancy law.
        #   B. BOARD ON THE RIGHT MAN BUT A DUPLICATE APPEARS, or A's hidden
        #      hands come back holding something anyway -> occupying a hand
        #      with a POSE is weaker than occupying it with an OBJECT, which is
        #      a useful distinction and would be written down as one.
        #   C. BOARD STILL ON GUARD A -> prop ownership is NOT reachable by
        #      hand-state wording on this checkpoint. Then beat 10's plate
        #      cannot name which man holds the board, and the honest options
        #      are to draw the two men IDENTICALLY DRESSED so it does not
        #      matter, or to accept that beat 10 needs a composited or
        #      hand-corrected plate. Either is a bigger call than a seed, and
        #      this lane would stop and say so rather than spend a fifth.
        "slug": "no-form",
        "prompt": (
            "2boys, full body, medium shot, two guard men standing together "
            "in tall grass, hedgerow behind, near taller man with light "
            "sandy hair, cream shirt, white shoulder sash, brown wrap skirt, "
            "holding a large flat bark board in both hands, one man behind "
            "with dark cropped hair, glasses, a tan tunic, hands behind his "
            "back, masterpiece, best quality"
        ),
        # Restated BYTE FOR BYTE from the base draft. Not one term added or
        # removed, so a change in the board's owner is attributable to the four
        # words in the positive and to nothing else. 74/77.
        "negative": (
            "text, bald, bare head, 1boy, 3boys, solo, crowd, girl, child, "
            "from behind, back view, close-up, portrait, distant, small "
            "figure, sky, horizon, white background, simple background, "
            "armor, helmet, knight, weapon, sign, banner, paper, book, "
            "photorealism, 3d render, night"
        ),
        # ------------------------------------------------------------------
        # R2 VERDICT. macbook2, 137.2s, seed 20260817 unchanged.
        # THE INSTRUMENT DID NOT DEPLOY, WHICH IS NOT THE SAME AS THE
        # INSTRUMENT FAILING, AND THE DIFFERENCE IS THE WHOLE VERDICT.
        # ------------------------------------------------------------------
        # `hands behind his back` DID NOT RENDER. Guard A's arms are FOLDED
        # ACROSS HIS FRONT, in full view, at the centre of the frame. So the
        # test this rung was built to run -- does occupying the other pair of
        # hands move the prop -- WAS NEVER ACTUALLY RUN. Outcome C is not
        # earned and is not claimed; a pose tag that does not bind cannot
        # falsify anything about what a bound pose would have done. Recorded
        # this way on purpose, because "we tried occupying the hands and it
        # didn't work" would be a false entry that the next lane would trust.
        #
        # WHAT THE FOUR WORDS DID DO, at the far end of the prompt, exactly as
        # (11,4) warned a mid-prompt edit can: THEY FIXED THE IDENTITY AT THE
        # BAD SEED. This is the first time seed 20260817 has produced guard B
        # at all. The left man is unmistakably blond with a cream shirt and a
        # brown wrap skirt, the right man is black-haired with glasses. Four
        # words about one man's hands moved another man's hair colour, in the
        # helpful direction this time, which is the same mechanism that cost
        # (11,4) its P1 and is a reason to distrust the attribution of ANY
        # single-word result on this checkpoint.
        #
        # AND THE FOUNDER'S OWN NAMED DEFECT IS REPRODUCED BY THIS PLATE,
        # WHICH IS THE SERIOUS FINDING. There are TWO boards. Opened at 5x, the
        # right-hand board IS held -- a hand grips its lower edge, on GUARD A,
        # so the prop is still on the wrong man. Opened at 3x, THE LEFT-HAND
        # BOARD IS ATTACHED TO NOTHING: it hangs in the air beside guard B with
        # NO HAND ON IT, while his visible hand is up at his own collar holding
        # nothing at all. That is verbatim the defect the founder marked on the
        # cast sheet -- "THE FLOATING CLIPBOARD ... Attached to nothing, no
        # hand on it" -- and this lane has now reproduced it rather than
        # cleared it. It is named here and in the report and it is not softened
        # by the fact that the other board is held.
        # SCORING: P1 FAIL (guard A's garment came back OLIVE GREEN, not tan,
        # and the board is still his), P2 PASS, P3 FAIL (neither man's hands
        # hold the board as described), P4 PASS ~76%, P5 MARGINAL -- 0.85
        # torsos and 41.0% flat, the softest upper band of the day, though the
        # haze does carry leaf shapes, P6 FAIL on the floating board, P7 PASS,
        # P8 FAIL -- two boards, one unheld, neither in two hands.
        #
        # BEAT 10 IS NOT SOLVED AND THIS LANE STOPS HERE ON IT, with its budget
        # spent and the state stated plainly rather than a fifth guess fired.
        # THE MOST CAST-CORRECT PICTURE BEAT 10 HAS IS r1s3 (seed 20260819):
        # blond man in a cream shirt and brown wrap skirt beside a black-haired
        # man in glasses and a tan tunic, two whole figures, real grass -- with
        # the board in the WRONG man's hands. So beat 10's blocker is now
        # isolated to ONE condition and it is a hard one: PROP OWNERSHIP. The
        # board went to guard A or to both men at 4 of 4 renders, across two
        # wordings and four seeds, with the board clause inside guard B's own
        # person clause and B named first. Hair and garments bind to their
        # clauses; a prop does not. The honest remaining options are named in
        # the r2 pre-registration above under outcome C and every one of them
        # is bigger than a seed: retry the hand-occupying instrument with a
        # pose tag that actually binds, dress both men identically so ownership
        # stops mattering, or accept a composited or hand-corrected plate.
        # THAT IS A PRODUCTION DECISION, NOT A LANE DECISION.
        # ------------------------------------------------------------------
    },
    (14, 2): {
        # r1 came back a correct LOW CROUCH with the ground in frame -- the
        # framing lever worked on the first sample and the standing-plate
        # problem is solved. It failed on the DIRT: his hand rests on his knee,
        # and there is no bare earth anywhere, only grass.
        #
        # THE ONE VARIABLE: `green grass` was sitting in r1's own POSITIVE,
        # competing with `bare earth` and `loose dirt` for the same ground, and
        # grass won. This revision DELETES it from the positive and names it in
        # the negative, so the dirt has nothing to compete with. A deletion, not
        # an addition -- the same shape of fix that rescued the barkboard still.
        # The hand wording is BYTE-IDENTICAL to r1 on purpose: if the fingers
        # still do not reach the soil once the grass is gone, that is a separate
        # finding about verb binding and it must not be confounded with this one.
        "prompt": (
            "1boy, solo, lean wiry adult goblin man, green skin, bald head, "
            "patchwork cloak, crouching low, both clawed hands down at the "
            "bare earth, fingers picking at loose dirt, face turned away, "
            "embarrassed, low close-up, hands and dirt large in frame, "
            "patch of bare brown soil, masterpiece, best quality, very aesthetic"
        ),
        "negative": (
            "text, standing, walking, running, full body, wide shot, distant, "
            "grass, lawn, meadow, "
            "holding object, spear, staff, sword, stick, basket, broom, "
            "2boys, baby, child, chibi, stitches, scars, tree, forest, house, "
            "indoors, photorealism, 3d render, dark, night"
        ),
    },
    # ======================================================================
    # 2026-08-17. BEAT 14, "THE DEFENSE", REVISION 3.
    # THE PROMPT AND THE BAR IT WILL BE JUDGED BY, BOTH WRITTEN AND COMMITTED
    # BEFORE A SINGLE PIXEL EXISTS. THE BAR DOES NOT GET SOFTENED AFTERWARDS.
    # ======================================================================
    # THE BEAT, QUOTED FROM ITS SCRIPT so the plate and the words cannot drift
    # apart. genomes/sapling/nodes/002b-first-citizen/node.md, 1:04-1:10:
    #   "THE DEFENSE - 1:04-1:10.  He picks at the dirt, embarrassed, glancing
    #    around."
    #   > SCAVENGER: "It was *one* apple. It fell off the cart. On the ground,
    #     that's - that's foraging."
    # And its done_when, done-definitions.yaml beats.'14':
    #   "fingers at the dirt AND the glancing - embarrassment readable.
    #    Requires a plate where his hands and the ground are both in frame; a
    #    standing full-body plate cannot show this and should be sent back."
    # The beat IS THE HANDS. Its recorded refire fault is "he stands and looks
    # down instead of picking at the dirt. The beat IS the hands, and there are
    # no hands in it."
    #
    # ------------------------------------------------------------------
    # WHAT r1 AND r2 ALREADY SETTLED. NONE OF IT IS RE-DERIVED HERE.
    # ------------------------------------------------------------------
    # r1 (9eb7bd15) SOLVED THE THING THAT BLOCKED THE BEAT, ON THE FIRST
    # SAMPLE: a low crouch with the ground in frame, which is exactly what the
    # definition says a standing full-body plate cannot give. THE FRAMING
    # LEVER IS NOT RE-OPENED AND ITS WORDING IS CARRIED FORWARD UNTOUCHED. r1
    # failed on the DIRT -- one hand resting on a knee, no bare earth anywhere,
    # only grass.
    # r2 deleted `green grass` from r1's positive and named grass in the
    # negative. Dirt arrived, and BOTH hands came down into frame. But the
    # background went DESERT DUST -- re-creating the "beat 14 sat on DESERT
    # DIRT" fault this project had already found and fixed once.
    #
    # ------------------------------------------------------------------
    # THE DIAGNOSIS I DISAGREE WITH, AND WHY. This is the whole of r3.
    # ------------------------------------------------------------------
    # STATE.md 2026-08-16 stopped at two samples and wrote: "the two samples
    # show grass and dirt are bistable by wording -- one wins or the other
    # does -- while the beat needs a patch of bare dirt WITHIN a green field",
    # and filed it as a composition problem needing a tool rather than
    # adjectives. THAT STOP WAS THE RIGHT CALL AT THE TIME and the entry it
    # left is why this rev is cheap to author. But the bistability conclusion
    # is drawn from a comparison that MOVED TWO THINGS AT ONCE, and the
    # cleaner reading is already in this file's own docstring:
    #   r2 did not merely take grass off the ground. IT REMOVED THE
    #   BACKGROUND'S ONLY NOUN AND THEN FORBADE IT. After r2's edit the only
    #   world nouns left in the positive are `bare earth`, `loose dirt` and
    #   `patch of bare brown soil` -- three synonyms for one substance -- and
    #   `grass, lawn, meadow` sit in the negative. THE VACANCY LAW DOES THE
    #   REST: an empty region is a hole filled with the largest noun in the
    #   prompt, the negative does not reach it, and the largest noun in r2 is
    #   dirt. So the dirt ran to the horizon. That is not two substances
    #   fighting over one region; it is one region that was never given a noun.
    # Beat 08 lost five samples to a colossus grown in a reserved sky; beat 17
    # r2 grew three extra goblin heads in a flat grass margin with `solo`
    # LEADING and `2boys` negated; beat 11 r3 fixed it on the first sample by
    # GIVING THE BACKGROUND A NOUN OF ITS OWN. Beat 14 r2 is the same law with
    # dirt in the role of the colossus.
    #
    # ------------------------------------------------------------------
    # THE ONE VARIABLE: THE TWO GROUND SUBSTANCES ARE SEPARATED BY DEPTH,
    # EACH GIVEN ITS OWN NOUN, INSTEAD OF ONE BEING BANNED.
    # ------------------------------------------------------------------
    # NEAR, under his hands: `patch of bare brown soil` -- KEPT BYTE-IDENTICAL
    #     from r2, because that clause is what delivered bare dirt.
    # FAR, above and behind him: `tall green grass behind him` -- ADDED. Not
    #     `green grass`, which is r1's word and is a GROUND-PLANE noun that
    #     competed for the same pixels as the soil and won. `tall grass` is
    #     VERTICAL foliage that occupies a background band, it is the noun this
    #     repo has already used for exactly this job ((11,3), and the three
    #     0817 guard plates), and TALL GRASS CANNOT BECOME A CHARACTER.
    # AND THE UN-BAN IT REQUIRES: `grass, lawn, meadow` comes back OUT of the
    #     negative. This is not a second lever, it is a mechanical precondition
    #     -- asking for grass while forbidding grass is the contradiction exit 7
    #     exists to catch, and it would make whatever came back unattributable.
    #     Said out loud so nobody has to guess whether it was noticed.
    #
    # r3 THEREFORE SITS EXACTLY BETWEEN r1 AND r2, WHICH MAKES THE ATTRIBUTION
    # UNUSUALLY CLEAN, and this is checkable rather than asserted:
    #   * r3's NEGATIVE is BYTE-IDENTICAL to r1's.
    #   * r3's POSITIVE is r2's positive plus ONE clause.
    #   * THE SEED IS UNCHANGED at 20260814 -- r1, r2 and r3 are three draws of
    #     one seed, so nothing below is a seed difference. (And 20260814 is NOT
    #     20260817, the seed with a record for manufacturing false laws.)
    #
    # WHAT IS DELIBERATELY *NOT* CHANGED, AND THIS IS THE HARDER DISCIPLINE.
    # THE HAND WORDING IS BYTE-IDENTICAL TO r1 AND r2 -- `both clawed hands
    # down at the bare earth, fingers picking at loose dirt`. r2's own comment
    # pre-registered why: if the fingers still do not reach the soil once the
    # grass is gone, that is a SEPARATE finding about verb binding and must not
    # be confounded with this one. THAT EXPERIMENT RAN AND RETURNED: hands came
    # down, contact did not. So verb-binding is now a NAMED OPEN FAULT with a
    # named instrument waiting for it -- `picking at` is a VERB, and 24
    # candidates failed on "pushes himself up to standing" because this model
    # renders the verb's END state, so the state-tag form (`fingertips
    # touching the soil`) is r4's variable and r4's alone. Firing both at once
    # would buy a picture and no knowledge. P3 below is scored anyway, because
    # a fault you are expecting is still a fault you must write down.
    #
    # BOTH HANDS ARE NAMED, AND ON THIS BEAT THAT IS THE CENTRAL RISK RATHER
    # THAN A FORMALITY. The hand-vacancy law (this file's docstring, the only
    # rule here with a matched control at three seeds a side) says an
    # unspecified hand is an empty region that grows the largest noun and that
    # the negative does not reach it: beat 10's unnamed far man grew a bamboo
    # pole with `weapon` negated and a duplicate board at another seed, 2 of 3,
    # against beat 05's four SPECIFIED hands at 0 of 3. A beat whose entire
    # content is a pair of hands cannot afford to leave either of them vacant.
    # Both are given a state, in a positive shape, never `empty hands` -- CLIP
    # cannot represent negation and `empty hands` embeds close to `hands`.
    # This also makes the law FALSIFIABLE here: see Q4.
    #
    # NO EYE-STATE TAG, AND THAT IS A DECISION. `face turned away` is carried
    # from r1/r2, so there are no eyes to state. The rule "a face plate must
    # name the eye state" is RETRACTED in this file's own docstring -- it was
    # written off one picture and at four seeds delivered a usable pair of eyes
    # 1 time in 4, a wink once and open-but-blank-white once. It is not built
    # on here. The "glancing around" in the done_when is the CLIP's job; what
    # the plate owes the clip is a head to animate, which is P6.
    #
    # A CROP OF THE STANDING PLATE IS NOT AN OPTION AND IS NOT BEING WEIGHED.
    # A lane measured that a tight insert with no whole body goes out of
    # distribution and RE-COMPOSES INTO A PORTRAIT (beat 17 r1's insert had no
    # hole, so the clip manufactured one by pulling the camera back and put a
    # face in it). That failure mode is Q6, named in advance, precisely because
    # this framing is close to it.
    #
    # ------------------------------------------------------------------
    # PLATE BAR, PRE-REGISTERED. USABLE ONLY IF ALL SEVEN HOLD.
    # Every load-bearing axis is named, because a lane this week certified a
    # prop's MATERIAL while never mentioning its SHAPE and scored 8/12
    # "passes" with 0/12 usable.
    # ------------------------------------------------------------------
    #   P1 LOW AND OVER THE GROUND. He is crouched, squatting or kneeling --
    #      NOT standing -- and the ground he is over is inside the frame. This
    #      is r1's win and a regression here fails outright.
    #   P2 BOTH HANDS IN FRAME AND DOWN. Both hands visible, both below waist
    #      height, neither parked on a knee (r1's exact fault), and NOTHING in
    #      either of them.
    #   P3 CONTACT. At least one hand's fingers TOUCH the soil -- skin meeting
    #      dirt, not hovering above it. This is the axis r3 changes no wording
    #      for; a fail here is expected and informative, not a surprise, and
    #      it hands r4 its variable.
    #   P4 DIRT WITHIN A GREEN FIELD -- THE POINT OF THIS REVISION, AND BOTH
    #      HALVES ARE REQUIRED. Bare brown soil under or around his hands, AND
    #      green living vegetation present in the same frame. Bare ground with
    #      a dust/desert background is r2's fault and FAILS. Green ground with
    #      no bare soil anywhere is r1's fault and FAILS. One without the other
    #      is not a partial pass; it is the same picture we already have.
    #   P5 NO VACANCY. No flat untextured region larger than his torso -- no
    #      dust haze band, no white background, no featureless colour wash --
    #      and nothing grown in one. The hole itself is the fail, whether or not
    #      something has arrived in it.
    #   P6 HIS HEAD IS IN FRAME. Head inside the frame, turned down or away, so
    #      the clip has a head to animate the "glancing around" with. A frame
    #      cropped to hands and dirt alone FAILS -- it satisfies the letter of
    #      "hands and ground in frame" and destroys the beat.
    #   P7 ONE ADULT GOBLIN. Exactly one figure, adult proportions, green skin.
    #      No second body anywhere including small in the background.
    #   RECORDED AND NOT SCORED: costume identity against the goblin sheet
    #      (it drifted on both r1 and r2 and wants a REFERENCE, not words --
    #      out of scope for a wording rev and dishonest to score here), exact
    #      soil colour, time of day, cloak tailoring.
    #
    # ------------------------------------------------------------------
    # FAIL MODES NAMED IN ADVANCE so none can be talked into a pass after.
    # ------------------------------------------------------------------
    #   Q1 DESERT -- r2's exact signature: bare ground to the horizon, no green
    #      anywhere. Means the un-ban alone was not enough, and r4's variable is
    #      a negative that NAMES the failure world (`desert, sand, dunes, dry
    #      cracked earth, wasteland`), which no beat-14 negative has ever done.
    #   Q2 GRASS WINS -- r1's exact signature: green ground plane, no bare soil,
    #      hand back on the knee. Means the depth separation does not bind and
    #      the next instrument is COMPOSITIONAL (a mask, an init, a two-region
    #      tool), not another adjective. Say so and stop rather than laddering.
    #   Q3 HOVERING HANDS -- hands down, no contact. r2's residual fault
    #      surviving, which isolates verb-binding as the sole remaining cause
    #      and sends r4 to the state-tag form. THE EXPECTED OUTCOME.
    #   Q4 HAND-VACANCY OBJECT -- a stick, pole, basket or broom in either hand
    #      with all four nouns sitting in the negative. On the hand rule's own
    #      account this should NOT happen here, because BOTH hands are
    #      specified and the matched control is 0 of 3. IF IT HAPPENS ANYWAY THE
    #      HAND-VACANCY LAW IS WEAKER THAN THIS FILE STATES and that gets
    #      written down as a finding against the rule, not explained away.
    #   Q5 STANDING -- regression to `ep2-b14-plate-0814`, the plate the
    #      definition says to send back.
    #   Q6 PORTRAIT RE-COMPOSE -- comes back a face or upper-body shot with no
    #      ground. The measured out-of-distribution failure of tight inserts.
    #   Q7 CHILD OR CHIBI -- proportions collapse to a boy, with `baby, child,
    #      chibi` all negated.
    #
    # ------------------------------------------------------------------
    # DECISION RULE, WRITTEN BEFORE THE RENDER.
    # ------------------------------------------------------------------
    # ONE SAMPLE, opened and judged, before anything else. Then:
    #   * ALL SEVEN HOLD -> the picture is a candidate, and it is a candidate
    #     ON ITS PIXELS ONLY. IT IS NOT A FINDING ABOUT THE WORDING UNTIL THREE
    #     FRESH SEEDS OF THE BYTE-IDENTICAL PROMPT HAVE RUN -- a single-seed
    #     observation is not a finding, seed 20260817 manufactured two false
    #     laws in two days, and this file's own docstring was written by the
    #     lane that then broke that rule within the hour. Three seeds is
    #     minutes on the Mac fleet.
    #   * P4 FAILS -> Q1 or Q2 above dictates the next rung, and they dictate
    #     DIFFERENT rungs, which is why they are distinguished in advance.
    #   * ONLY P3 FAILS -> r4, state tag, background wording byte-identical.
    # SEEDS ARE PARALLELISED, RUNGS ARE NOT -- each rung depends on the
    # previous verdict and a ladder run concurrently is a ladder with no
    # controls.
    #
    # A MAC PLATE IS EVIDENCE ABOUT A PICTURE AND NEVER ABOUT A WORDING. The
    # PNG travels forward as the literal first frame the box animates (the box
    # has no text-to-video path), so a verdict on these pixels stands. "This
    # wording worked on the Mac" is VOID at MAE 61 of 255 between the two
    # renderers. Nothing here may be cited as proof a wording works.
    #
    # NOTHING IS ENQUEUED, NO MOTION IS FIRED, NO `plate_ack` IS WRITTEN, AND
    # shots.md, wave-drafts.yaml and farm-queue.yaml ARE UNTOUCHED BY THIS
    # LANE. If the plate passes, SAY SO AND STOP.
    # ------------------------------------------------------------------
    # THE TOKEN BUDGET, AND THE TWO WORDS IT COST. MEASURED, NOT ESTIMATED.
    # ------------------------------------------------------------------
    # THE GUARD IN THIS FILE FIRED ON THE FIRST DRAFT OF THIS REV AND IS THE
    # REASON THIS PARAGRAPH EXISTS: `--dry` on macbook1 returned
    # `TOKENS positive 80/77 TRUNCATED!! ... Refusing to draw.` Without it the
    # style anchor would have gone silently off the tail, which is exactly the
    # defect that killed nine drafts before `95d0c6d0` and exactly what the
    # first beat-14 draft did at 96/77.
    # r2's positive measures 74/77 on the real CLIP tokenizer, so THERE ARE
    # THREE TOKENS OF ROOM and the added clause costs six. Every candidate was
    # measured rather than guessed at (`tall green grass behind him` 6,
    # `tall grass behind him` 5, `tall grass behind` 4, `tall grass
    # background` 4). So the clause had to be paid for, and WHAT IT WAS PAID
    # WITH IS A DELIBERATE TRADE RECORDED HERE RATHER THAN A QUIET EDIT:
    #   `wiry` DELETED from `lean wiry adult goblin man`. A near-synonym of
    #     `lean`, which stays, as does `adult` (which P7 needs against Q7).
    #     Costume and build identity are explicitly NOT SCORED in this bar --
    #     they drifted on r1 and r2 both and want a REFERENCE, not words.
    #   `embarrassed` DELETED, and this is the one that deserves an argument
    #     rather than an assertion, because the done_when says "embarrassment
    #     readable". IT HAS NO FACE TO LAND ON. `face turned away` is in the
    #     same prompt and is carried from r1 -- an emotion adjective with the
    #     face turned out of view can only act as a diffuse style nudge. What
    #     makes this beat read embarrassed is a grown man crouched picking at
    #     dirt with his face averted, which is the POSTURE, and the "glancing
    #     around" that completes it is the CLIP's job off the head P6 reserves.
    #     If the plate passes every axis and still reads as nothing in
    #     particular, THIS DELETION IS THE FIRST SUSPECT and it is named here
    #     in advance so it cannot be rediscovered as a surprise.
    # THE STYLE TAIL WAS NOT TOUCHED, though cutting `very aesthetic` would
    # have bought two tokens and is the repo's own current standard (all three
    # 0817 guard plates end at `masterpiece, best quality`). r1 and r2 both
    # carry the longer tail, so cutting it here would change the style
    # conditioning between r2 and r3 and confound the one thing this rev tests.
    # RESULT, read off the real `--dry` step and not off this arithmetic:
    # `TOKENS positive 76/77 ok / TOKENS negative 64/77 ok`. ONE TOKEN OF
    # HEADROOM. The prediction from summing the measurements above was 77 and
    # the truth is 76 -- the sub-word pieces do not add the way the candidate
    # table suggests, which is itself the argument for running the step instead
    # of trusting the sum. Stated plainly because the next lane to add a word
    # here has one token to spend, and in a file whose whole subject is
    # silently lost tails that is worth a sentence. The positive still ends on
    # `very aesthetic`, which is `render_wave_goblin.ANCHOR_TAIL`, so the style
    # anchor is intact and present in what will actually be sent.
    (14, 3): {
        "prompt": (
            "1boy, solo, lean adult goblin man, green skin, bald head, "
            "patchwork cloak, crouching low, both clawed hands down at the "
            "bare earth, fingers picking at loose dirt, face turned away, "
            "low close-up, hands and dirt large in frame, "
            "patch of bare brown soil, tall green grass behind him, "
            "masterpiece, best quality, very aesthetic"
        ),
        # Restated BYTE FOR BYTE, not inherited -- a rev merges over
        # DRAFTS[14], never over the rev before it, and exit 6 refuses a rev
        # that names a prompt without restating its negative. This one is
        # byte-identical to DRAFTS[14]'s own negative, i.e. to r1's: r2's
        # `grass, lawn, meadow` is GONE, deliberately, and that deletion is
        # named in the comment above rather than left to be discovered.
        "negative": (
            "text, standing, walking, running, full body, wide shot, distant, "
            "holding object, spear, staff, sword, stick, basket, broom, "
            "2boys, baby, child, chibi, stitches, scars, tree, forest, house, "
            "indoors, photorealism, 3d render, dark, night"
        ),
    },
    # ======================================================================
    # 2026-08-17. BEAT 14 REVISION 4, WRITTEN AND COMMITTED AFTER r3 WAS
    # OPENED AND SCORED AND BEFORE r4 EXISTS. THE RUNG r3's VERDICT DICTATED.
    # ======================================================================
    # r3's SCORED RESULT, which this rev is a consequence of rather than a
    # guess: SIX AXES HELD, P5 FAILED, and NONE of the seven named fail modes
    # fired. Full frame description and verdict in
    # farm-out/ep2-b14-mac-plate-0817/14-the-defense-mac-plate-r3s1.yaml
    # (committed at d06bee24, sha f47f6d0a). In one line: bare soil under both
    # sets of fingertips AND green grass in the same frame -- so grass and dirt
    # are NOT bistable and that reading is retired -- but the band above and
    # behind his hunched back came back a featureless pale wash larger than his
    # torso.
    #
    # THE ONE VARIABLE, AND r3 IS WHAT NARROWED IT TO ONE. `tall green grass
    # behind him` BECOMES `tall green grass background`. Nothing else in the
    # positive changes, the negative is byte-identical again, and the seed is
    # still 20260814 -- so r1, r2, r3 and r4 are now four draws of ONE seed
    # differing by text alone.
    # WHY THAT EXACT SWAP. r3 proved the clause RENDERS; it rendered in the
    # wrong PLACE. `tall green grass` came back as tufts at the left and right
    # frame edges AT HIS OWN DEPTH -- an object beside him -- because `behind
    # him` is a prepositional phrase anchored to the FIGURE. `background` is a
    # booru-native framing suffix anchored to the FRAME, and it is the exact
    # construction (11,3) used when it fixed this on its first sample and
    # measured 0.47 torsos of largest flat rectangle. So the spatial operator
    # changes class -- figure-relative to frame-relative -- and the noun does
    # not change at all. That is the smallest edit that asks the question, and
    # it happens to BUY a token rather than cost one: `behind him` is two,
    # `background` is one.
    #
    # THE ALTERNATIVE MECHANISM, NAMED NOW SO IT CANNOT BE INVENTED LATER. The
    # pale wash may not be an unnamed region at all -- IT MAY BE AN UNNAMED
    # SKY. Nothing in beat 14's positive or negative has ever mentioned sky,
    # and (11,3)'s negative forbids `sky, horizon` while beat 14's does not.
    # If `background` does not reach the band, THE r5 CANDIDATE IS TO NAME THE
    # SKY POSITIVELY rather than to negate it -- deleting `wide blue sky above`
    # is what "removed a colossus completely" on beat 08, i.e. a sky with a
    # noun in it is a solved region and a sky with none is a hole. Negating it
    # is NOT the candidate, and the reason is this file's own retracted
    # `horizon` rule: a deletion from the negative looked like a lever at one
    # seed and died at 3 of 3 fresh ones.
    #
    # WHAT IS NOT CHANGED, AND ONE OF THESE IS A RUNG I HAD QUEUED AND AM
    # STANDING DOWN. The hand wording stays byte-identical for the FOURTH time.
    # r3's P3 CONTACT was pre-registered as THE EXPECTED FAILURE (Q3) and it
    # PASSED -- both sets of fingertips in a dug divot -- so the state-tag
    # revision I had named as r4's variable IS NOT EARNED and firing it now
    # would change a wording that is currently delivering the thing it was
    # going to be changed to deliver. Nothing in r3 can have FIXED contact
    # either, since the wording did not move; one frame cannot separate
    # "reachable at this seed all along" from "one draw". So contact is carried
    # as UNRESOLVED-BUT-WORKING and is watched at P3, not legislated about.
    #
    # THE BAR IS THE SAME SEVEN AXES AS r3 WITH ONE HONEST TIGHTENING, AND THE
    # DIRECTION OF THE EDIT MATTERS. P4 as written for r3 named both substances
    # and never named their RATIO, so r3's dirt plane with grass at the fringes
    # satisfied its text. THAT IS SCORED AS r3 WROTE IT AND IS NOT BEING
    # RETROACTIVELY FAILED -- bending a bar after the picture is the exact
    # failure that turned 8/12 "passes" into 0/12 usable this week. The
    # tightening applies FORWARD, from r4 on:
    #   P4' DIRT WITHIN A GREEN FIELD, WITH THE RATIO NAMED. Bare brown soil
    #       under or around his hands, AND green living vegetation, AND the
    #       green must read as A FIELD HE IS IN rather than a fringe at the
    #       frame's edges: green present on more than one side of him and
    #       continuing past the frame edge, not isolated tufts. A dirt plane
    #       bordered by grass is r3's outcome and is no longer a pass.
    #   P5 IS THE AXIS UNDER TEST and is unchanged: no flat untextured region
    #       larger than his torso, and nothing grown in one.
    #   P1, P2, P3, P6, P7 unchanged and all five must continue to hold --
    #       r3 passed all five and a regression in any of them fails r4 even if
    #       the band is fixed. THIS IS THE REAL RISK OF THIS REV: a background
    #       tag can pull the camera back, and pulling back is how P1's low
    #       framing and P2's hands-large-in-frame get lost. Q6 PORTRAIT
    #       RE-COMPOSE and a new Q8 CAMERA PULLED BACK (the ground stops being
    #       half the frame, the hands stop being large) are both live.
    #   FAIL MODES: Q1-Q7 as committed at c81323c6, plus Q8 above. Q1 desert is
    #       now LESS likely, not more, because the green noun is still present
    #       and is being moved rather than removed.
    #
    # DECISION RULE, UNCHANGED AND RESTATED SO IT IS NOT DRIFTED: ONE SAMPLE,
    # opened and judged. All seven (with P4') holding makes it a CANDIDATE ON
    # ITS PIXELS, and NOT a finding about the wording until THREE FRESH SEEDS
    # of the byte-identical prompt have run -- one seed has manufactured two
    # false laws in this repo in two days. P5 failing again sends the next rung
    # to the sky clause named above, not to another region word. Any regression
    # in P1/P2/P6 means the background tag costs the framing r1 won, and then
    # the honest answer is that this beat needs a composition tool after all --
    # which is where STATE.md's original stop pointed, and it would deserve to
    # be said plainly rather than laddered around.
    # Seeds parallelise, rungs do not. Nothing is enqueued off this, no motion
    # is fired, and no `plate_ack` is written.
    (14, 4): {
        "prompt": (
            "1boy, solo, lean adult goblin man, green skin, bald head, "
            "patchwork cloak, crouching low, both clawed hands down at the "
            "bare earth, fingers picking at loose dirt, face turned away, "
            "low close-up, hands and dirt large in frame, "
            "patch of bare brown soil, tall green grass background, "
            "masterpiece, best quality, very aesthetic"
        ),
        # Byte-identical to DRAFTS[14]'s negative and to r3's, restated rather
        # than inherited because exit 6 refuses a rev that names a prompt and
        # not a negative, and because the pair that actually gets drawn should
        # be readable in one place.
        "negative": (
            "text, standing, walking, running, full body, wide shot, distant, "
            "holding object, spear, staff, sword, stick, basket, broom, "
            "2boys, baby, child, chibi, stitches, scars, tree, forest, house, "
            "indoors, photorealism, 3d render, dark, night"
        ),
    },
    # ======================================================================
    # 2026-08-17. BEAT 14 REVISION 5, WRITTEN AFTER r4 WAS OPENED AND SCORED
    # AND BEFORE r5 EXISTS. NOT ONE TOKEN CHANGES. ONLY THEIR ORDER.
    # ======================================================================
    # r4's SCORED RESULT (01a3098d, sha 91318616): P4' PASSES -- bare soil with
    # green grass on four sides of it, a dirt patch inside a green field, which
    # is what the beat has wanted since 08-16 and what r1, r2 and r3 each missed
    # differently. P5 FAILS for the second rung: the band above his hunched back
    # is still a flat wash larger than his torso. Q8 CAMERA PULLED BACK fired
    # weakly -- r4 shows both boots where r3 cropped at the cloak, so the hands
    # are smaller and `hands and dirt large in frame` is less true than it was.
    #
    # THE FINDING r4 PRODUCED, AND IT RETIRES THE RUNG r4's COMMIT PROMISED.
    # THE HOLE IS ABOVE THE HORIZON. Grass grows on the ground, so no phrasing of
    # a grass noun can put grass up there, and all four rungs so far have aimed a
    # GROUND noun at a SKY region. r4's commit named the next candidate as
    # NAMING THE SKY POSITIVELY. THAT CANDIDATE IS WITHDRAWN, and it is withdrawn
    # on this repo's own strongest evidence about this exact failure mode rather
    # than on a change of mind: beat 17's draft records that "an empty upper half
    # in a portrait frame is a hole the model fills with the largest noun in the
    # prompt (DELETING `wide blue sky above` REMOVED A COLOSSUS COMPLETELY)".
    # Asking for a wide sky is what MANUFACTURES the flat region; beat 08 lost
    # five samples to a colossus grown in a reserved sky. So naming a sky here
    # would ask for precisely the large flat region P5 forbids. Recorded because
    # I committed the opposite plan two commits ago and the reversal is the
    # record.
    #
    # WHICH LEAVES THE OTHER HALF OF r4's OWN CONCLUSION: DO NOT FILL THE BAND,
    # REMOVE IT. If the frame is tight enough on the crouch and the ground there
    # is no above-horizon band to fill, and that fixes P5 and Q8 with one move
    # instead of trading them off. It is also the direction the beat's own
    # `done_when` asks for -- "a plate where his hands and the ground are both in
    # frame" -- which says nothing about a field.
    #
    # THE ONE VARIABLE, AND IT IS FREE. THE FRAMING TAGS MOVE TO THE FRONT.
    # `low close-up, hands and dirt large in frame` currently sit in the MIDDLE
    # of the positive and have sat there in ALL FOUR revisions. The measured law
    # this beat has therefore never once applied: LEADING FRAMING TAGS CARRY REAL
    # WEIGHT AND TRAILING ONES ALMOST NONE -- a peer lost a whole render to a
    # trailing `wide two-shot` and got a close-up with the subject missing, and
    # (11,3), (17,2) and (5,2) all put the count tag first and the framing tags
    # second for exactly this reason. (11,3) is the only guard plate that ever
    # passed its own bar and that is its construction.
    # NOT ONE TOKEN IS ADDED, REMOVED OR ALTERED. The multiset of words is
    # identical to r4's; only the position of two clauses changes. So it costs no
    # cast attribute, trades nothing, needs no deletion to pay for it, and the
    # measurement is expected to come back at r4's 75/77 -- which the real `--dry`
    # step will confirm rather than this comment asserting it. It is the cleanest
    # single variable available on this beat and the cheapest.
    #
    # THE BAR IS UNCHANGED FROM r4: P1, P2, P3, P4', P5, P6, P7 and Q1-Q8, as
    # committed at e70c36f6. Nothing is softened and nothing is added.
    # THE NAMED RISK OF THIS REV, stated in advance: `low close-up` LEADING may
    # over-tighten and re-compose into a portrait or an insert with no whole
    # body. That is Q6, and it is a MEASURED failure of this framing family (a
    # tight insert with no whole body goes out of distribution and re-composes
    # into a portrait; beat 17 r1's insert had no hole so the clip manufactured
    # one by pulling the camera back and put a face in it). If Q6 fires, leading
    # framing tags are too strong for this composition and the answer is
    # compositional -- a mask, an init, or the founder's own framing call -- not a
    # sixth wording.
    # DECISION RULE, unchanged: ONE SAMPLE, opened and judged. All axes holding
    # makes it a CANDIDATE ON ITS PIXELS and NOT a finding about the wording
    # until three fresh seeds of the byte-identical prompt have run. Seed stays
    # 20260814, so r1-r5 are five draws of one seed differing by text alone.
    # THIS IS THE LAST WORDING RUNG THIS LANE WILL FIRE. Two rungs have now
    # failed the same axis; if a third does, P5 is not reachable by words on this
    # composition and that gets reported as the answer rather than laddered
    # around. STATE.md's 2026-08-16 stop pointed at a composition tool, and its
    # instinct would then be vindicated even though its diagnosis is dead.
    (14, 5): {
        "prompt": (
            "1boy, solo, low close-up, hands and dirt large in frame, "
            "lean adult goblin man, green skin, bald head, "
            "patchwork cloak, crouching low, both clawed hands down at the "
            "bare earth, fingers picking at loose dirt, face turned away, "
            "patch of bare brown soil, tall green grass background, "
            "masterpiece, best quality, very aesthetic"
        ),
        # Byte-identical to r3's and r4's, restated per exit 6.
        "negative": (
            "text, standing, walking, running, full body, wide shot, distant, "
            "holding object, spear, staff, sword, stick, basket, broom, "
            "2boys, baby, child, chibi, stitches, scars, tree, forest, house, "
            "indoors, photorealism, 3d render, dark, night"
        ),
    },
    # ======================================================================
    # 2026-08-17. BEAT 14 REVISION 6. THE CAMERA ANGLE, FIRED ON THE FOUNDER'S
    # OWN CALL. WRITTEN AND COMMITTED BEFORE THE PIXEL EXISTS.
    # ======================================================================
    # WHY THIS RUNG EXISTS AT ALL, since r5 pre-committed to be the last one.
    # It is not this lane laddering around its own stop rule. r5's stop rule
    # named the next instrument -- a CAMERA ANGLE, `from above` -- and
    # deliberately did NOT fire it, for one reason that was correct: camera
    # angle is a LOOK decision and look is R4, the founder's. THE FOUNDER HAS
    # NOW MADE THE CALL: "for beat 14, fix it properly." So the instrument r5
    # left on the bench is fired by authority, not by escalation. The wording
    # ladder is still closed; this is not a sixth wording rung aimed at filling
    # the band.
    #
    # THE MECHANISM, INHERITED AND NOT RE-DERIVED. Three rungs (r3, r4, r5)
    # failed P5 and the diagnosis they converged on is that THE HOLE IS ABOVE
    # THE HORIZON: grass grows on the ground, so every rung aimed a GROUND noun
    # at a SKY region and none could ever reach it. r5 also proved the camera is
    # the thing that has never moved -- it enlarged the SUBJECT, and a bigger
    # subject at eye level still has a horizon in frame and therefore still has
    # sky above his hunched back. `from above` does not FILL the band, it
    # DELETES it: a high angle puts GROUND behind him where sky was.
    # AND THE PLAN THAT IS STILL FORBIDDEN: naming the sky positively. That was
    # r4's promised candidate, withdrawn at r5 on beat 17's evidence (DELETING
    # `wide blue sky above` REMOVED A COLOSSUS) and beat 08's five samples lost
    # to a colossus grown in a reserved sky. Asking for a wide sky MANUFACTURES
    # the flat region P5 forbids. It is not re-opened here.
    #
    # ------------------------------------------------------------------
    # THE ONE VARIABLE: `low close-up` BECOMES `from above, close-up`.
    # ------------------------------------------------------------------
    # The camera angle and nothing else. `low` is the camera-HEIGHT word in
    # r5's leading framing cluster and it is the current angle; changing the
    # angle IS editing that word. The subject's posture is NOT touched --
    # `crouching low` is a separate clause and stays byte-identical, so P1's
    # crouch does not depend on this edit. The clause stays LEADING, which is
    # r5's one measured win (framing tags at the FRONT undid Q8's camera pull-
    # back at zero token cost) and is preserved exactly. Both new tags are
    # booru-native atomic tags -- `from above` and `close-up` are real Danbooru
    # tags, which is the form this repo has measured as binding, where
    # `low close-up` is film language.
    # THE SEED IS UNCHANGED at 20260814. r1-r6 are SIX draws of one seed
    # differing by text alone.
    #
    # WHY IT IS A SWAP AND NOT AN ADDITION, AND THIS IS MEASURED, NOT PREFERRED.
    # Adding `from above` to r5 while KEEPING `low close-up` measures 78/77 on
    # the real CLIP tokenizer and THE GUARD IN THIS FILE WOULD REFUSE TO DRAW IT
    # (exit 5). So "add the angle and change nothing else" is not available at
    # this budget; the token guard forces the trade. It is also the honest form:
    # a prompt asking for a LOW camera and a HIGH camera in the same breath is a
    # contradiction, which is what exit 7 exists to catch one level up.
    # Every candidate was MEASURED on the venv's CLIPTokenizer against r5's
    # exact positive (75/77), not summed from a table:
    #   `from above,` added, `low close-up` kept ......... 78  REFUSED
    #   `low close-up` -> `from above, close-up` ......... 77  CHOSEN
    #   `low close-up` -> `close-up from above` ......... 76
    #   `low close-up` -> `from above` .................. 73  (drops close-up)
    #   `low close-up` -> `high angle, close-up` ........ 77
    # 77/77 IS ZERO HEADROOM AND THAT IS SAID OUT LOUD, because this file's
    # subject is silently lost tails and (20,3) is recorded as exactly this trap:
    # one more word in this positive and the anchor leaves without a message.
    # `close-up from above` at 76 would leave a token, and it is NOT chosen
    # because it is a compound that is not a trained tag pair, where the whole
    # point of the rev is that the angle must BIND. The real `--dry` step
    # confirms 77 before anything is drawn rather than this comment asserting it.
    # THE STYLE TAIL IS NOT TOUCHED. The positive still ends `masterpiece, best
    # quality, very aesthetic` -- `very aesthetic` is
    # `render_wave_goblin.ANCHOR_TAIL`, and cutting it would buy two tokens and
    # confound the comparison, since r1-r5 all carry it. Note that
    # plate_scratch.py does not call compress(), so there is no
    # `STYLE ANCHOR PRESENT` line to read: it is checked by reading the string.
    # The negative is BYTE-IDENTICAL to r3/r4/r5's, restated per exit 6, and
    # `from above` and `close-up` appear in neither half, so exit 7 is clean.
    #
    # ------------------------------------------------------------------
    # THE BAR. ALL SEVEN AXES CARRIED FORWARD UNCHANGED FROM e70c36f6 (P4'
    # tightened forward there, restated unchanged at 3c20c13a). NOTHING IS
    # SOFTENED, NOTHING IS ADDED, NOTHING IS TIGHTENED.
    # ------------------------------------------------------------------
    # P5 is scored by the SAME TEXT that failed r3, r4 and r5, so a pass here is
    # comparable to those fails. The other six are carried so that the question
    # "did the six that r5 passed SURVIVE the angle change" is answerable --
    # A FIX THAT DELETES THE SKY BY LOSING THE BURIED HANDS IS NOT A FIX, and a
    # regression in ANY of P1, P2, P3, P4', P6, P7 FAILS r6 even if the band is
    # gone.
    #   P1 LOW AND OVER THE GROUND -- crouched/squatting/kneeling, not standing,
    #      ground he is over inside the frame.
    #   P2 BOTH HANDS IN FRAME AND DOWN -- both visible, both below waist,
    #      neither parked on a knee, nothing in either.
    #   P3 CONTACT -- at least one hand's fingers TOUCH the soil, not hovering.
    #   P4' DIRT WITHIN A GREEN FIELD, RATIO NAMED -- bare brown soil under or
    #      around his hands, AND green living vegetation, AND the green reads as
    #      A FIELD HE IS IN: green on more than one side of him and continuing
    #      past the frame edge, not isolated tufts.
    #   P5 NO VACANCY -- no flat untextured region larger than his torso, no
    #      dust haze band, no white background, no featureless colour wash, and
    #      nothing grown in one. The hole itself is the fail. THE AXIS UNDER
    #      TEST, and the only axis three rungs have failed.
    #   P6 HIS HEAD IS IN FRAME -- head inside the frame, turned down or away,
    #      so the clip has a head to animate the "glancing around" with.
    #   P7 ONE ADULT GOBLIN -- exactly one figure, adult proportions, green
    #      skin, no second body anywhere including small in the background.
    #   RECORDED AND NOT SCORED, unchanged: costume identity against the goblin
    #      sheet (drifted on all five revisions; it wants a REFERENCE, not
    #      words), blank white eyes, exact soil colour, time of day.
    #
    # A LOOSENESS IN P6 THAT THIS REV IS LIKELY TO EXPOSE, NAMED BEFORE THE
    # PIXEL AND DELIBERATELY NOT ACTED ON. A high angle over a man whose face is
    # already turned away can return THE TOP OF A BALD SKULL and nothing else --
    # which satisfies P6 AS WRITTEN ("head inside the frame, turned down or
    # away") while giving the clip a featureless dome rather than a face to
    # glance with. If that happens, P6 IS SCORED AS WRITTEN -- A PASS -- and the
    # tightening is proposed FORWARD for r7 ("some facial feature legible: brow,
    # ear line, nose or eye"). It is NOT tightened now, because the whole
    # purpose of this bar is that r5's six passes and r6's are comparable, and
    # because bending a bar after seeing the picture is how 8/12 "passes" became
    # 0/12 usable this week. Saying it in advance is what stops it being
    # rediscovered as a surprise or quietly used to fail the rev.
    #
    # ------------------------------------------------------------------
    # FAIL MODES NAMED IN ADVANCE. Q1-Q8 as committed at c81323c6 and e70c36f6
    # all still live, plus three that belong to THIS instrument.
    # ------------------------------------------------------------------
    #   Q9  THE CROUCH GOES WITH `low`. P1 or P2 regresses because `low` in the
    #       leading framing cluster, not `crouching low`, was the word carrying
    #       r1's win. If this fires, r1's framing lever was never separable from
    #       the camera height and the beat's composition cannot be steered by
    #       tags at all -- report it, do not re-word around it.
    #   Q10 THE FIELD LEAVES WITH THE SKY. P4' fails because a high angle can
    #       fill the whole frame with soil and put no green anywhere -- deleting
    #       the band by deleting the field. THAT IS A TRADE, NOT A FIX, and it
    #       is scored as a FAIL of r6, not as a P5 win. This is the most likely
    #       way this rev goes wrong and it is why P4' is carried unchanged.
    #   Q11 TOP-OF-SKULL PLATE. The bald-dome case above. P6 passes as written;
    #       recorded as an observation and a forward tightening for r7.
    #   Q8  CAMERA PULLED BACK stays live: a high angle that also backs off
    #       loses `hands and dirt large in frame` and fails P2.
    #   Q6  PORTRAIT RE-COMPOSE stays live for the same reason it did at r5.
    #
    # ------------------------------------------------------------------
    # DECISION RULE AND STOP RULE, BOTH PRE-REGISTERED. THIS IS THE ONLY RUNG
    # THIS LANE FIRES.
    # ------------------------------------------------------------------
    # ONE SAMPLE, one seed (20260814), opened and judged by eye against the
    # seven axes above AS WRITTEN. No seed batch: the committed rule spends
    # three fresh seeds only once every axis holds, and `--seeds > 1` needs
    # `--i-have-seen-a-sample` anyway (exit 8).
    #   * ALL SEVEN HOLD -> the band is gone AND the six survived. That makes it
    #     a CANDIDATE ON ITS PIXELS ONLY, and NOT a finding about the wording
    #     until three fresh seeds of the byte-identical prompt have run (one
    #     seed manufactured two false laws in this repo in two days). WHETHER IT
    #     SHIPS IS R4 AND THE FOUNDER'S ALONE -- he authorised fixing the beat,
    #     not the result. The lane writes the founder card and STOPS: nothing
    #     enqueued, no motion, no `plate_ack`, no seed batch.
    #   * P5 PASSES BUT ANY OF THE OTHER SIX REGRESSES -> NOT A PASS. Report the
    #     trade by name (Q9, Q10, Q8, Q6) and STOP. A band removed by losing the
    #     buried hands or the green field is the picture we already had.
    #   * P5 FAILS A FOURTH TIME -> THE CAMERA-ANGLE INSTRUMENT IS SPENT TOO,
    #     and that is the finding: the empty band is not reachable by ANY
    #     leading-tag wording on this composition, angle tags included. NO r7
    #     WORDING RUNG IS FIRED. What is left gets NAMED, not run: (1) a
    #     two-region compositional tool -- an img2img init or an inpaint mask
    #     over the band, which is what STATE.md's 2026-08-16 stop pointed at;
    #     (2) a CROP of r5 or r6 below the horizon, which is a framing decision
    #     and therefore R4; (3) the founder's own call that a soft gradient sky
    #     is a milder fault than the white BURST that broke beats 06, 09 and 11
    #     -- offered to him as a question, never scored here as a pass.
    # A MAC PLATE IS EVIDENCE ABOUT A PICTURE AND NEVER ABOUT A WORDING (MAE 61
    # of 255 between MPS and the box). The PNG travels forward as the literal
    # first frame the box animates, so a verdict on these pixels stands; "this
    # wording worked on the Mac" is void and is not claimed. macbook1 is the
    # renderer for all six draws, and `mac_preflight.py` returned
    # `verdict: READY, problems: []` with every weight blob's sha256 re-read
    # against its own filename BEFORE this rung was authored -- two Macs
    # rendered SDXL as pure noise for days on weights that passed size, file
    # count and manifest.
    # shots.md, wave-drafts.yaml, farm-queue.yaml and genomes/ are UNTOUCHED.
    (14, 6): {
        "prompt": (
            "1boy, solo, from above, close-up, hands and dirt large in frame, "
            "lean adult goblin man, green skin, bald head, "
            "patchwork cloak, crouching low, both clawed hands down at the "
            "bare earth, fingers picking at loose dirt, face turned away, "
            "patch of bare brown soil, tall green grass background, "
            "masterpiece, best quality, very aesthetic"
        ),
        # Byte-identical to r3's, r4's and r5's, restated per exit 6.
        "negative": (
            "text, standing, walking, running, full body, wide shot, distant, "
            "holding object, spear, staff, sword, stick, basket, broom, "
            "2boys, baby, child, chibi, stitches, scars, tree, forest, house, "
            "indoors, photorealism, 3d render, dark, night"
        ),
    },
}


# ======================================================================
# 2026-08-17. BEAT 14 "r7" IS NOT A WORDING RUNG. IT IS THREE FRESH SEEDS OF
# r6, BYTE FOR BYTE, AND THE ONLY THING THAT VARIES IS THE SEED.
# Pre-registered before the pixels exist.
# ======================================================================
# READ THE REV NUMBER CAREFULLY: it is r7 only because `--rev` is how this file
# selects a draft, and a lane reading "r7" as a sixth wording of beat 14 would
# be reading it wrong. NOTHING IN THE TEXT MOVES. r6's stop rule closed the
# wording ladder and it stays closed.
#
# WHY THESE THREE DRAWS EXIST. r6 fixed P5 for the first time in four rungs --
# `from above` DELETED the above-horizon band instead of trying to fill it --
# and in the same frame P2 regressed: two forearms terminated in ONE FUSED HAND
# where r5 had two hands with ten fingertips buried. r6's own verdict recorded
# the attribution as IMPOSSIBLE AT ONE SEED and refused to guess: a top-down
# view of two arms converging on a point is a harder pose than side-by-side
# hands, but hands are this checkpoint's weakest anatomy at every angle, and one
# draw cannot separate "the angle fuses them" from "this seed drew a bad hand".
# THREE FRESH SEEDS IS THE ONLY INSTRUMENT THAT SEPARATES THEM, and the answer
# changes what happens next, so it is measurement rather than taste. Authorised
# on that ground by the coordinator; options (2) and (3) from r6's card -- crop
# r5 below its horizon, and whether a soft gradient band is milder than a white
# burst -- are LOOK decisions and went to the founder untouched.
#
# BYTE-IDENTITY IS STRUCTURAL HERE, NOT PROMISED. The rev is built by COPYING
# r6's dict and overriding one key, so the prompt and negative CANNOT drift by a
# character even if someone edits r6 later -- they would move together, which is
# the correct behaviour for a replication. No second copy of the strings exists
# to fall out of sync. (`dict(...)` also keeps `negative` present, so exit 6 is
# satisfied structurally too, and the pos/neg clash check of exit 7 sees exactly
# what r6 saw.)
#
# THE SEEDS: 20260820, 20260821, 20260822, from `--seeds 3` off this base. Fresh
# -- none of them has drawn this beat -- and deliberately NOT 20260817, which
# this repo records as the seed that manufactured two false laws in two days.
# r6's own 20260814 is not re-drawn, because a replication that includes the
# frame it is replicating is not three fresh seeds; with r6 the count is FOUR
# DRAWS OF ONE PROMPT.
# `--seeds 3` requires `--i-have-seen-a-sample` (exit 8) and that flag is
# honest here: r6 IS the sample, it was opened, described and scored in
# farm-out/ep2-b14-mac-plate-0817/...r6s1.yaml at 66e1b824 before these ran.
#
# THE BAR IS BYTE-IDENTICAL TO b1dabc0c: P1, P2, P3, P4', P5, P6, P7 and
# Q1-Q11, every axis scored as written. TWO THINGS ARE FORBIDDEN AND SAID OUT
# LOUD BECAUSE BOTH ARE TEMPTING NOW: P2 IS NOT SOFTENED because we now expect
# it to fail (a bar bent toward the expected answer certifies nothing), and
# NOTHING IS TIGHTENED on the strength of r6's passes either -- the P6
# tightening r6 floated stays withdrawn, and P5's confessed looseness (it is a
# per-region size test, blind to total flat area) is NOT patched mid-experiment.
# r5 is not retroactively re-scored.
#
# WHAT THE RESULT MEANS, PRE-COMMITTED SO IT CANNOT DRIFT AFTER THE PIXELS:
#   * P2 PASSES ON ANY ONE OF THE THREE -> THE FUSION IS SEED VARIANCE. `from
#     above` costs the beat nothing and r6's recipe is LIVE: this wording plus a
#     seed screen is the beat's plate path. Say so and STOP.
#   * P2 FAILS 3 OF 3 (four of four counting r6) -> THE FUSION IS THE ANGLE.
#     `from above` is SPENT AS WRITTEN: it buys P5 and P4' and it costs the
#     hands, which on this beat is not a trade worth taking, because the beat IS
#     the hands. The next instrument is then THE HAND, not the sky and not a
#     word -- an inpaint mask or an img2img init over the hand region -- and it
#     is NAMED, not fired here.
#   * EITHER WAY THE LANE STOPS AT THREE. No fourth seed, no fifth wording rung,
#     no seed picked after the fact: all three draws are reported whatever they
#     show, which is why the seeds are written down in this commit BEFORE they
#     exist.
# Each draw is scored and committed on its own. $0, macbook1, `mac_preflight.py`
# re-run to `verdict: READY, problems: []` before this batch. Nothing enqueued,
# no motion, no `plate_ack`; shots.md, wave-drafts.yaml, farm-queue.yaml and
# genomes/ untouched.
REVS[(14, 7)] = dict(REVS[(14, 6)], seed=20260820)

# ==========================================================================
# 2026-08-19. BEAT 14 REVISION 8. THE RESTAGE: EMBARRASSMENT PUT IN THE BODY
# INSTEAD OF ASKED FOR IN A WORD. WRITTEN BEFORE THE PIXEL EXISTS.
# ==========================================================================
# THE FINDING THAT FORCES THIS AND IT IS SETTLED, NOT SUSPECTED. Three data
# points, quoted from ep2-b14-mac-motion-s2-0818.yaml's own verdict:
#   * plate seed r1s3, recorded in done-definitions: "reads sullen rather than
#     embarrassed";
#   * motion seed 1 off that plate: "the face is flat, half-lidded, brows
#     level. It reads SULLEN -- or defiant -- not caught-out";
#   * motion seed 2, same plate, same prompt, same recipe, only the seed
#     changed: "FAIL, and identically to seed 1 ... Second seed, same read."
# The verdict's own conclusion: "THE SULLEN FACE IS STAGING, NOT SEED ... Settled:
# re-rolling seeds will not buy an embarrassed face." So the one thing this rev
# must NOT be is another seed, and the one thing it must not do is name the
# emotion harder.
#
# WHY NAMING IT HARDER IS NOT AVAILABLE, AND THE FILE ALREADY KNEW. `embarrassed`
# was in the BASE draft's positive and it is GONE by r5 -- five rungs of this
# beat have run without it. The word was tried and the beat is still sullen. An
# expression adjective on this checkpoint buys a face doing an adjective; it does
# not buy a man who has just been caught. The instrument left is the BODY.
#
# ------------------------------------------------------------------
# THE ONE VARIABLE: THE POSE CLAUSE. Everything else is r6, byte for byte.
# ------------------------------------------------------------------
#   `both clawed hands down at the bare earth, fingers picking at loose dirt,
#    face turned away`
#      ->
#   `one clawed hand picking at loose dirt, hand behind head, head down,
#    shoulders up`
# The leading framing cluster (`from above, close-up, hands and dirt large in
# frame`) is UNTOUCHED -- it is r5's one measured win and the founder's own r6
# camera call, and moving it would confound this rev with that one. The cast
# wording, the soil, the grass and the whole style tail are byte-identical to
# r6. The negative is byte-identical to r3/r4/r5/r6's, restated per exit 6.
#
# WHY THAT PARTICULAR POSE AND NOT A DIFFERENT ONE. `hand behind head` is the
# sheepish gesture -- the hand up to scratch the back of the head while the head
# drops and the shoulders come up -- and it is the single most legible
# caught-out cue in the drawing tradition this checkpoint was trained on. It is
# also legible WITHOUT the face, which matters: `face turned away` is what the
# beat has been drawing and the fix cannot depend on a face the framing may not
# hold. And it carries the one thing `face turned away` never did -- a REASON
# the face is down. A bowed head over dirt reads sullen because nothing in the
# frame says he is reacting to anybody. A hand up behind the head says he is.
#
# IT IS A BOORU-NATIVE ATOMIC TAG, AND THAT IS WHY IT IS THIS PHRASE AND NOT A
# BETTER SENTENCE. r6's own note is the precedent: `from above` and `close-up`
# were chosen over the more descriptive `close-up from above` because "the
# compound is not a trained tag pair, where the whole point of the rev is that
# the angle must BIND". `hand behind head` is a real Danbooru tag. `hand behind
# his neck` and `one hand at the nape` are prose, they are 2-4 tokens dearer,
# and on this beat's budget they do not fit anyway. Measured on the venv's real
# CLIPTokenizer against r6's exact positive (77/77, zero headroom):
#   `... the other hand up behind his neck, head ducked, shoulders raised` .. 81  REFUSED
#   `... other hand behind his neck, head ducked, shoulders up` ............. 79  REFUSED
#   `... hand behind his neck, head ducked, shoulders up` ................... 78  REFUSED
#   `... hand behind neck, head down, shoulders up` ......................... 76
#   `... hand behind head, head ducked, shoulders up` ....................... 77  (zero headroom)
#   `... hand behind head, head down, shoulders up` ......................... 76  CHOSEN
# The chosen line is the only candidate that is both booru-native and leaves a
# token of headroom, which this file's whole subject is silently losing.
#
# IT KEEPS BOTH HALVES OF done_when, AND THAT IS THE CONSTRAINT THAT SHAPED IT.
# done_when is "fingers at the dirt AND the glancing". Sending both hands to the
# neck would buy the register by deleting half the beat. So ONE hand stays in the
# dirt -- the beat's own subject, the reason a low framing was ever asked for --
# and only the second hand moves. `hands and dirt large in frame` is unchanged
# and P2 still scores exactly what it scored on r3-r7.
#
# THE R4 LINE, NAMED RATHER THAN STEPPED OVER. ep2-b14-mac-motion-s2-0818's
# verdict says it licenses "NOTHING", and specifically that "a restage of beat 14
# for the embarrassed glance is NOT ruled -- it is the founder's call under R4".
# That line is right about MOTION and about the BEAT, and neither is filed here.
# What it cannot mean is that the open question stays open with no pixels
# attached to it: the founder's screening standard is taste-only, one question at
# a time, ALWAYS WITH PIXELS, and the 2026-08-18 board put the restage half of
# this question to him with nothing to look at. A $0 still is what turns an
# argument into a card. THIS REV DECIDES NOTHING: no motion, no pick, no
# plate_ack, no leaf, no lineage, nothing enqueued on any GPU queue. It draws one
# picture so the call he already owns can be made on an image instead of on two
# lanes' prose.
#
# THE BAR. P1, P2, P3, P4', P5, P6 and P7 ARE CARRIED FORWARD BYTE-IDENTICAL and
# scored exactly as written on r3-r7 -- nothing softened, nothing tightened, and
# P5 is NOT patched even though its confessed looseness is still on the record.
# Carrying them is what makes "did the restage cost anything" answerable at all.
# ONE AXIS IS ADDED, and adding an axis mid-ladder is normally forbidden in this
# file, so the exemption is stated: r3-r7 are rungs of the P5 BACKGROUND ladder
# and this is not a rung of it. It is a different question, and a question with
# no axis cannot be answered by a picture.
#   P8 READS CAUGHT-OUT. The judged clause, and it is judged BY EYE at 1x with
#      no measure, because no measure this repo owns reads register. PASS needs
#      a man who has just been caught at something: the lowered head and the
#      hand up behind the head both present and legible, the shoulders up rather
#      than slumped. EXPLICIT FAILS, from the three data points above: FLAT AND
#      HALF-LIDDED (the sullen read), DEFIANT, SCOWLING or SLY (all three are
#      recorded on this beat's draws in pipeline/loop/beat14-field-init-0817.md:
#      "scowling, sly or sullen -- never embarrassed on all four draws"), and
#      BLANK. A face that merely hides is NOT a pass -- hiding is what r1-r7
#      already do.
# NEW FAIL MODES NAMED IN ADVANCE, on top of Q1-Q11 which all still stand:
#   Q12 THE SECOND HAND GOES SOMEWHERE ELSE -- to the face, the mouth, the ear,
#       or off frame entirely. A hand that lands on the NAPE rather than the
#       crown is a near miss and is reported as one; a hand at the FACE is a
#       plain fail, because that is the thoughtful-hand trope beat 09 measured
#       at 11 of 12 and it reads pondering, not caught.
#   Q13 THE DIRT HAND IS LOST. One hand named instead of two may drop the
#       ground contact the beat exists for. This is the cost that would make the
#       trade a bad one and it is the first thing to look at.
#   Q14 THE POSE GOES COY OR CUTE -- a bashful anime blush pose rather than a
#       grown man caught out. `baby, child, chibi` are already in the negative;
#       this is the same defect arriving through the staging instead of the cast.
# ONE SAMPLE. One seed, one draw, opened and scored on its own before anything
# else is filed on it -- and if P8 fails, the answer is that the BODY is spent
# too and the next instrument is a reference or a mask, not a ninth wording.
# $0, Apple MPS, nothing enqueued on the box.
REVS[(14, 8)] = {
    "prompt": (
        "1boy, solo, from above, close-up, hands and dirt large in frame, "
        "lean adult goblin man, green skin, bald head, "
        "patchwork cloak, crouching low, one clawed hand picking at loose "
        "dirt, hand behind head, head down, shoulders up, "
        "patch of bare brown soil, tall green grass background, "
        "masterpiece, best quality, very aesthetic"
    ),
    # Byte-identical to r3's, r4's, r5's and r6's, restated per exit 6.
    "negative": (
        "text, standing, walking, running, full body, wide shot, distant, "
        "holding object, spear, staff, sword, stick, basket, broom, "
        "2boys, baby, child, chibi, stitches, scars, tree, forest, house, "
        "indoors, photorealism, 3d render, dark, night"
    ),
    # r6's seed, unchanged. The seed is the ONE variable this beat has already
    # exhausted (two motion seeds, same read), so holding it fixed is what makes
    # r8 comparable to r6 on the axis that matters.
    "seed": 20260814,
}
# --------------------------------------------------------------------------
# r8 SCORED, 2026-08-19, macbook3, seed 20260814, rc 0.
# farm-out/ep2-b14-mac-plate-0819/14-the-defense-mac-plate-r8s1.png
# sha256 ca0eb53ead9ad068da677ab38db2fa699abc6f0facb387b8f72b5f6dd3ed50e2
# (sidecar confirms `revision: 8`, so the new --rev plumbing carried the right
# draft -- the first thing checked, since the whole point of that fix was that
# a wrong rev is invisible in the picture).
#
# VERDICT: FAILS. 4 of 8 terms hold. AND THE EXPERIMENT DID NOT RUN THE TEST IT
# WAS DESIGNED TO RUN, which is a more useful thing to say than "the restage
# failed" and is the difference between a finding and a story.
#
#   P1 LOW AND OVER THE GROUND ... PASS. Crouched, ground under him, in frame.
#   P2 BOTH HANDS IN FRAME AND DOWN, NEITHER PARKED ON A KNEE ... FAIL, and by
#      the exact clause this rev was steering away from. `hand behind head` did
#      NOT BIND AT ALL -- there is no hand anywhere near his head. The second
#      hand went to his KNEE, which P2 forbids by name. See the note below on
#      why this must NOT be counted into the r7 ladder's P2 tally.
#   P3 CONTACT .................. PASS. Fingers are IN the soil, clods thrown,
#      not hovering. Q13 DID NOT FIRE: naming one hand instead of two did not
#      cost the ground contact, which was the feared price of the trade.
#   P4' DIRT WITHIN A GREEN FIELD  FAIL. Bare soil is present under the hand and
#      green is present, but the term's own exclusion catches it: what is there
#      is ISOLATED TUFTS -- individual blades at the corners against a pale
#      ground -- and not green reading as a field he is in.
#   P5 NO VACANCY, THE AXIS UNDER TEST ... FAIL. A flat pale cream wash fills
#      the mid-frame on both sides of him, far larger than his torso. This is
#      the FOURTH rung to fail P5.
#   P6 HIS HEAD IS IN FRAME ..... PASS. In frame, turned down, available to
#      animate.
#   P7 ONE ADULT GOBLIN ......... PASS. One figure, adult proportions, green.
#   P8 READS CAUGHT-OUT ......... FAIL, and on the exact fail this bar named in
#      advance. The brow is furrowed and the eyes are narrowed into a downward
#      GLARE. That is the SCOWLING read, listed with FLAT AND HALF-LIDDED,
#      DEFIANT and SLY as explicit fails. It is now a fourth data point for the
#      register defect, alongside plate r1s3 and the two motion seeds.
#   Q12 THE SECOND HAND GOES SOMEWHERE ELSE ... FIRED, and WORSE than predicted.
#      The bar predicted a near miss -- the hand landing on the nape instead of
#      the crown -- and said that would be reported as a near miss. What
#      happened is that the tag did not render at all.
#   Q13 THE DIRT HAND IS LOST ... DID NOT FIRE.
#   Q14 THE POSE GOES COY OR CUTE  DID NOT FIRE. No blush, no bashful pose, an
#      adult throughout.
#
# WHY "THE BODY IS SPENT" WOULD BE AN OVERCLAIM, AND THE HONEST READING.
# The rev's stop rule said: "if P8 fails, the answer is that the BODY is spent
# too and the next instrument is a reference or a mask, not a ninth wording."
# P8 failed, so THE STOP HOLDS -- there is no r9 and this lane fires no ninth
# wording. But the REASON is not the one the stop rule anticipated. The
# hypothesis was "a staged caught-out pose will not read as caught-out". That
# was never tested, because the pose was never drawn: `hand behind head` was
# ignored. What r8 actually measured is that A BOORU-NATIVE POSE TAG DOES NOT
# BIND AT THIS FRAMING, on a prompt whose leading cluster is already spending
# its authority on `from above, close-up, hands and dirt large in frame`. The
# register question is therefore still OPEN, and it is open on a compositional
# instrument rather than a lexical one -- an inpaint mask or an img2img init
# over the arm region, or a reference pose. That is the same instrument r5's
# stop rule named for the hands on a different axis, arrived at independently
# from the other side. NAMED, NOT FIRED.
#
# !! DO NOT FOLD r8's P2 FAILURE INTO THE r7 LADDER. r6/r7 exist to answer
# whether `from above` costs the hands, and their decision rule turns on P2
# failing 3 of 3. r8 is NOT a rung of that ladder: its P2 failure is caused by
# THIS REV'S OWN POSE EDIT, which deliberately moved a hand off the ground and
# then failed to place it. Counting it would corrupt the one measurement r6 and
# r7 were filed to make. r8's P5 failure is likewise not a fourth seed of r7 --
# it is a different prompt.
# --------------------------------------------------------------------------

# ==========================================================================
# 2026-08-19. BEAT 19 REVISION 2. THE HANDS, PUT SOMEWHERE POSITIVELY.
# WRITTEN AFTER r1 WAS DRAWN AND SCORED, BEFORE r2 EXISTS.
# ==========================================================================
# r1's full verdict is in DRAFTS[19] above and is not repeated. The short of
# it: 5 of 7 terms hold, the recorded blocker (Q1, the fig already lying in the
# grass) DID NOT FIRE for the first time in this beat's history, and two terms
# failed -- P3 because his hand closed around the stem, and P1 because three or
# four extra purple beads came down the stalk behind the fruit.
#
# ------------------------------------------------------------------
# THE ONE VARIABLE: `both hands on his knees` IS ADDED. Nothing else moves.
# ------------------------------------------------------------------
# THE CHOICE OF INSTRUMENT IS NOT A PREFERENCE, IT IS THIS FILE'S OWN LAW.
# `holding fruit` and `fruit in hand` were already in r1's negative and the
# hand still went to the plant. The module header records why, from beats 05
# and 10: an arm the positive does not place is an arm the model finds a job
# for, and the answer is to place it. `both hands on his knees` is the
# cheapest positive placement that (a) is a real trained pose, (b) is
# physically what a kneeling man's hands do, (c) is compatible with beat 20
# opening on him picking the fig up with both hands -- they are already free
# and already low -- and (d) does not move his body, his face, the plant, the
# fruit, the light or the framing, all of which passed.
#
# WHY NOT ALSO FIX THE FRUIT COUNT IN THE SAME DRAW, SINCE IT IS ALSO A FAIL.
# Because two edits make an unattributable picture, and because the two
# defects are not equally urgent. P3 is a `done_when` clause -- "NO CONTACT
# WITH HIS BODY" -- and a stem in his fist forecloses the beat's whole action:
# a fig cannot fall from a branch a man is holding. P1's extra beads are a
# plant-shape defect on a plate that is otherwise the first one this beat has
# ever had with the fruit aloft. So the hands go first, alone.
# THE COUNT DEFECT IS NOT DROPPED, IT IS NAMED AS r3's VARIABLE IN ADVANCE:
# if r2 clears the hands and Q9 fires again, the next edit is the plant's
# description -- the canon `two leaves and one thin side-branch` shape from
# style.md row 002a/b/c, which also answers P6's recorded caveat that the
# fruit is hanging from the stalk's TIP where canon puts it on a side-branch.
# That is one edit, it fixes two recorded faults, and it is written down here
# so it cannot be re-derived as a discovery later.
#
# THE BAR IS UNCHANGED. P1-P7 and Q1-Q9 exactly as pre-registered in
# DRAFTS[19], byte for byte. NOTHING IS SOFTENED -- in particular P1 is NOT
# relaxed to "at least one fruit" now that we know the count is the harder
# half, and P6 is NOT tightened to demand the side-branch even though the
# caveat above says it should eventually. A bar edited between rungs makes the
# rungs incomparable, and this beat's whole hope is that r1 and r2 differ by
# one string.
# THE SEED IS UNCHANGED at 20260819, so r1 and r2 are two draws of one seed
# differing by text alone. ONE SAMPLE. $0, Apple MPS, nothing on the box.
REVS[(19, 2)] = {
    "prompt": (
        "1boy, solo, lean wiry adult goblin man, green skin, bald head, "
        "patchwork cloak, kneeling beside a tiny sapling rooted in the "
        "grass, both hands on his knees, one deep purple fig hanging from "
        "its thin side-branch, his face visible, wide shot, sunny grassy "
        "field, cinematic lighting, masterpiece, best quality, very aesthetic"
    ),
    # Byte-identical to r1's, restated per exit 6.
    "negative": (
        "text, 2boys, girl, baby, child, chibi, elf, standing, walking, "
        "close-up, portrait, holding fruit, fruit in hand, fruit on the "
        "ground, large tree, thick branch, trunk, forest, house, indoors, "
        "night, dark, photorealism, 3d render"
    ),
    "seed": 20260819,
}
# --------------------------------------------------------------------------
# r3 SCORED, 2026-08-19, macbook1, seed 20260819, rc 0, sidecar `revision: 3`.
# farm-out/ep2-b19-mac-plate-0819/19-the-drop-mac-plate-r3s1.png
# sha256 de7a256c29b0a752b335e1e022c111e654c4c65cbe43b05fb98bd9573e1c6cbf
#
# VERDICT: FAILS, 5 of 7, THE SAME SCORE AS r2 BY A DIFFERENT ROUTE. AND THIS
# CLOSES THE WORDING LADDER ON THE PLANT.
#   P1 THE FIG IS ON THE PLANT ... FAIL. The count came DOWN -- roughly eight
#      fruit at r2, THREE at r3 -- so `a single ... fig` moved the number in the
#      right direction and did not reach one. A NEW defect arrived with it: the
#      three read as faceted purple CRYSTALS or gems rather than round soft
#      fruit. Recorded as part of P1's failure, not as a separate term; the bar
#      asks for a fig and a gem is not one.
#   P6 THE PLANT IS THE SAPLING . FAIL, unchanged from r2 and this is the whole
#      finding. There are STILL TWO PLANTS, and they are still thin bare whips
#      with a leaf cluster at the tip -- not one ~40 cm sapling with two leaves
#      and a thin side-branch. `two leaves and one thin side-branch` was
#      supposed to foreclose the multi-node vine geometrically. It did not.
#   P3 NO CONTACT ..... PASS, held from r2. Hands still folded on his knees.
#   P2 PASS. P4 PASS. P5 PASS, purple. P7 PASS, one lean adult goblin.
#   Q1 THE FIG ALREADY ON THE GROUND ... DID NOT FIRE, THIRD DRAW RUNNING.
#
# THE LADDER STOPS HERE, AND THE RULE IS THIS FILE'S OWN. Three rungs have now
# aimed three different wordings at ONE axis -- r1 `a tiny sapling rooted in the
# grass`, r2 the same, r3 `a tiny sapling with two leaves and one thin
# side-branch` plus `a single ... fig` -- and the plant has come back as a
# multi-fruit bead vine every time, twice doubled. Beat 14's ladder stopped at
# three on P5 for exactly this reason and named a composition tool; beat 11's
# stopped at three. THE PLANT IS NOT REACHABLE BY WORDS ON THIS CHECKPOINT and
# a fourth wording is the thing this repo has repeatedly been wrong to fire.
#
# THE INSTRUMENT IS NAMED AND NOT FIRED, and it is concrete rather than a
# gesture at "composition":
#   * THE PROJECT ALREADY OWNS THE PICTURE IT CANNOT WRITE. Beat 18's plate
#     PASSES its bar as ONE round deep-purple-violet fig hanging from ONE very
#     thin branch, green at its neck. That is precisely the object this beat
#     keeps failing to draw, already drawn and already scored.
#   * THE ROUTE EXISTS IN THIS REPO. pipeline/composite-init-pattern.md,
#     beat14_field_composite.py and beat08_gesture_composite.py are the same
#     move made twice before: build the init by COMPOSITING a passing element
#     into a passing frame instead of asking one prompt for both.
#   * SO THE NEXT BEAT-19 STEP IS A COMPOSITE INIT -- r3's man, pose, field and
#     framing (5 of 7 terms already passing, and the hands solved) with beat
#     18's fig-on-a-branch composited in at the right scale -- NOT a fourth
#     prompt. That is a build, it is bigger than a rev, and it is named here so
#     the next lane inherits a route rather than a mystery.
#
# WHAT THE THREE RUNGS BOUGHT, so the ladder does not read as a waste: the
# recorded blocker is DEAD. `plate_requirement_0815` said every beat-19 plate we
# own shows the fruit already lying in the grass and that this is "exactly why
# the beat was blocked". Three draws, three times aloft, Q1 never fired. The
# hands went from gripping the stem to folded on his knees on one edit. Beat 19
# is no longer blocked on "we cannot get the fruit off the ground"; it is
# blocked on "we cannot get the plant down to one", which is a smaller and
# differently-shaped problem with a route attached.
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# r2 SCORED, 2026-08-19, macbook1, seed 20260819, rc 0.
# farm-out/ep2-b19-mac-plate-0819/19-the-drop-mac-plate-r2s1.png
# sha256 7075a4e8d8906711dbbab16bff950a7a689574070444d52eb9041073167693be.
#
# VERDICT: FAILS THE BAR -- AND THE ONE VARIABLE DID EXACTLY WHAT IT WAS FILED
# TO DO. THE HANDS ARE FIXED.
#   P3 NO CONTACT ............ PASS, cleanly. Both hands are folded on his
#      knees, empty, nowhere near the plant. Q3 does not fire. `both hands on
#      his knees` bound on the first draw, and the positive-placement law from
#      beats 05 and 10 holds a third time -- the negative could not do this and
#      six words in the positive could.
#   P1 THE FIG IS ON THE PLANT  FAIL, AND WORSE THAN r1 ON THE COUNT. r1 had
#      one fruit at the tip plus three beads down one stalk. r2 has TWO arcing
#      stalks flanking him carrying roughly EIGHT purple figs between them.
#      Attachment is still won -- every fruit is aloft, none is in the grass --
#      and the count is lost by more.
#   P6 THE PLANT IS THE SAPLING  FAIL, and this is a REGRESSION from r1's pass.
#      There are two plants, not one, and they are drooping vine arcs, not a
#      40 cm sapling with two leaves and a thin side-branch. Q6 still does not
#      fire (no mature tree, no thick limb, no trunk).
#   P2 PASS. P4 PASS, face visible and readable. P5 PASS, unmistakably purple.
#      P7 PASS, one lean adult goblin.
#   Q1 THE FIG ALREADY ON THE GROUND ... DID NOT FIRE, second draw running.
#   NOTED, NOT SCORED: `kneeling` drifted to SITTING. No term asks for kneeling
#      by name -- `body_position` is a flagged open question and sitting still
#      satisfies the derivation (he is low, both hands are free, and beat 20
#      opens on him picking the fig up from the ground). Recorded so the author
#      can overturn it, not scored against a term that does not exist.
#
# WHAT THIS SETTLES: the hands were a WORDING problem and they are solved. The
# fruit count is NOT, and two draws now say the same thing -- ask this
# checkpoint for a thin stalk with a fig on it and it draws a bead-strung vine.
# That is the r3 variable, named in advance at r2 and unchanged by this result.
# --------------------------------------------------------------------------

# ==========================================================================
# 2026-08-19. BEAT 19 REVISION 3. THE PLANT, DESCRIBED FROM CANON INSTEAD OF
# LEFT TO THE CHECKPOINT. WRITTEN AFTER r2 WAS DRAWN AND SCORED.
# ==========================================================================
# THE VARIABLE WAS NAMED BEFORE r2 EXISTED and r2 did not change it: "if r2
# clears the hands and Q9 fires again, the next edit is the plant's description
# -- the canon `two leaves and one thin side-branch` shape from style.md row
# 002a/b/c, which also answers P6's recorded caveat that the fruit is hanging
# from the stalk's TIP where canon puts it on a side-branch."
#
# ------------------------------------------------------------------
# THE ONE VARIABLE: THE PLANT CLAUSE.
#   `a tiny sapling rooted in the grass` + `one deep purple fig hanging from
#    its thin side-branch`
#      ->
#   `a tiny sapling with two leaves and one thin side-branch` + `a single deep
#    purple fig hanging from that branch`
# ------------------------------------------------------------------
# EVERY OTHER CLAUSE IS r2's, BYTE FOR BYTE, INCLUDING `both hands on his
# knees` -- r2's win is carried, not re-tested. Negative and seed unchanged
# from r1 and r2, so r1, r2 and r3 are three draws of ONE seed differing by
# text alone.
#
# WHY THIS WORDING AND NOT A NEGATIVE. `fruit on the ground` and `thick branch`
# are already in the negative and the extra fruit arrived anyway; there is no
# negative tag for "eight figs instead of one" that the positive does not
# invite first. This file's own record is that the negative has failed four
# times now on nouns the positive left vague. So the plant is DESCRIBED:
# style.md's node table, row 002a/b/c -- ~40 cm, "two leaves + one thin
# side-branch", "the branch is where the fig grew and fell". `two leaves`
# forecloses the multi-node vine geometrically: a plant with exactly two leaves
# has nowhere to hang eight fruit. `a single ... fig` states the count in the
# positive where it can bind. And `that branch` points the fruit at the
# side-branch rather than the stalk's tip, which is P6's recorded caveat and
# beat 20's recorded fault ("the plant improvised per beat rather than
# described once") answered in the same six words.
#
# THE BAR IS UNCHANGED, P1-P7 and Q1-Q9 byte for byte. In particular P6 is
# still NOT tightened to demand the side-branch even though this rev supplies
# it -- a bar edited to match the rung it is about to score certifies nothing.
# If r3 draws the side-branch, that is reported as an unscored gain, the way
# r1's caveat was recorded rather than scored.
#
# 77/77. ZERO HEADROOM, SAID OUT LOUD, the way (14,6) says it: one more word in
# this positive and `very aesthetic` -- render_wave_goblin.ANCHOR_TAIL -- leaves
# without a message. Three cheaper spellings were measured on the venv's real
# CLIPTokenizer looking for a token back and none of them buys one:
#   `... sapling with two leaves and one thin side-branch` + `that branch` .. 77  CHOSEN
#   `... sapling, two leaves and one thin side-branch` + `that branch` ...... 77
#   `... sapling with two leaves and one thin side-branch` + `the branch` ... 77
#   `... sapling, two leaves and one thin side-branch` + `the side-branch` .. 79  REFUSED
# The one trim that WOULD have paid is dropping `deep` from `deep purple`, and
# it is declined: `deep purple` is the canon colour phrase r1 and r2 both drew
# with, the founder's 08-16 colour ruling is live, and moving the colour word in
# the same draw as the plant word would put two variables in one picture.
# ONE SAMPLE. $0, Apple MPS, nothing on the box.
REVS[(19, 3)] = {
    "prompt": (
        "1boy, solo, lean wiry adult goblin man, green skin, bald head, "
        "patchwork cloak, kneeling beside a tiny sapling with two leaves and "
        "one thin side-branch, both hands on his knees, a single deep purple "
        "fig hanging from that branch, his face visible, wide shot, sunny "
        "grassy field, cinematic lighting, masterpiece, best quality, very "
        "aesthetic"
    ),
    # Byte-identical to r1's and r2's, restated per exit 6.
    "negative": (
        "text, 2boys, girl, baby, child, chibi, elf, standing, walking, "
        "close-up, portrait, holding fruit, fruit in hand, fruit on the "
        "ground, large tree, thick branch, trunk, forest, house, indoors, "
        "night, dark, photorealism, 3d render"
    ),
    "seed": 20260819,
}

# ==========================================================================
# 2026-08-19. BEAT 15, GOOD LISTENER. THE FIRST PLATE THIS BEAT HAS EVER BEEN
# ASKED FOR AT CANON SCALE. WRITTEN BEFORE ANY PIXEL EXISTS.
# ==========================================================================
# WHY THIS IS r1 OF A NEW LADDER AND NOT RUNG SEVEN OF THE OLD ONE. Beat 15
# already owns a six-rung plate ladder (farm-out/ep2-b15-mac-plate-0815/,
# 2026-08-15, r1-r6, every sidecar still `scored: false`) and twelve wave
# stills scored ALL CANDIDATES FAIL. Firing a seventh wording at a question
# six wordings have closed is the move this repo has repeatedly been wrong to
# make, and beat 19's ladder stopped at three tonight for exactly that reason.
# THIS IS NOT THAT. Every one of those six rungs asked for the SUPERSEDED
# staging -- r1 `head tipped far back, looking up`, r5 `head tilted back ...
# two huge broad leaves HIGH ABOVE HIS HEAD`, r6 `one thin bare stalk TALLER
# THAN HE IS`. On 2026-08-17 the founder ruled *"rewrite the beats to work at
# knee height. change the story"* and beat 15 was restaged; THE-SAPLING.md
# §6.1 then corrected `taller than he is` by name and cites r6's own sidecar
# as an instance of the violation. The old ladder measured a plant canon no
# longer has. Nothing on it transfers, so this is rung one.
#
# WHAT THE OLD LADDER DID BUY, so it does not read as waste. Judged 2026-08-19
# against beats.'15'.done_when: r1 close-up, no plant in shot. r2 a scale
# double -- one giant seated figure with a tiny goblin at its base. r3 and r5
# grew the plant OUT OF HIS SHOULDER. r4 and r5 set him on a floating disc of
# grass in open sky. r6 drew a conical leaf-mountain the size of a hill with a
# speck of a figure beneath it. Six rungs, six different ways to fail the same
# clause, and not one of them a plant a stranger would call a seedling.
#
# THE ONE THING EVERY BEAT-15 ATTEMPT HAS SHARED, and it is the finding: the
# plant. Eight idfix stills drew DETACHED LEAVES FLOATING at the frame edges
# with no stem and no root; four `tonight` stills drew a real rooted plant
# INDOORS against wall panels; ep2-b15-plate-0814 -- the init all six of the
# 0815 motion takes were animated from -- drew a wiry multi-node weed topped
# with a white SPHERE. `authored_b15_plate` in wave-drafts.yaml asked for `a
# tiny sapling with broad round cotyledon leaves` and got that ball on a stick.
# So the plant is DESCRIBED here instead of named, the way beat 19's r3 does
# it: style.md's node table, row 002a/b/c, ~40 cm, two leaves on a thin stem.
# `two leaves` forecloses the multi-node weed GEOMETRICALLY -- a plant with
# exactly two leaves has nowhere to put a fourth node -- and `rooted in the
# soil` puts attachment in the POSITIVE, where six failures say it has to live.
# `floating leaves` is in the negative too and is not trusted to do the work:
# this file's own record is that the negative has failed four times running on
# nouns the positive left vague.
#
# THE CAST WORDING IS BEAT 19 r3's, CHARACTER FOR CHARACTER, AND THAT IS
# DELIBERATE. `lean wiry adult goblin man, green skin, bald head, patchwork
# cloak` scored P7 PASS on three separate draws on this checkpoint TODAY. The
# beat-15 draft it replaces opens `A small goblin BOY` and its plate came back
# a round-headed child in a modern shirt, cargo shorts and sneakers -- the noun
# put the child in the picture, which is the same law beat 08 measured on
# 2026-08-17. No costume word is left to a reference here; the cloak is stated.
#
# HE IS SEATED, AND THAT IS NOT THIS FILE'S INVENTION. Beat 13, the beat
# immediately before, ends with *"his legs give out and he drops to sit in the
# grass at the base of the stem"* -- node.md, the live approved script. A
# standing beat-15 plate contradicts the frame before it. `both hands on his
# knees` is carried verbatim from beat 19 r2, where it bound on the first draw
# and solved that beat's contact fault; it also names what both hands are
# doing, per this file's own vacancy law.
#
# ── NO HEAD DIRECTION IS ASKED FOR, AND THAT IS THE §6 LINE. ──────────────
# Beat 15 is one of the five beats restaged on 2026-08-17, and
# leaves/002b-t0-c.yaml records `approval_status: NOT YET READ BY HIM`. The
# ONE clause that restage moved is where he looks: `He looks up at the
# sapling` became `he tips his head DOWN until his eyes are level with the two
# leaves`. Everything else this plate stages -- he is seated, the sapling is
# beside him, BOTH SHARE THE FRAME -- is in the sentence he read and approved
# on 2026-08-03 and is untouched by the restage. So this prompt contains no
# gaze word at all, in either direction. A plate is an i2v init and the clip
# performs the look; drawing one now with no head direction in it keeps the
# fixture useful under either reading and asks the founder for nothing he has
# not already given. P8 below scores nothing about the gaze, and no term about
# it may be added after the draw.
#
# THE BAR, PRE-REGISTERED, SCORED N OF 7 ON ONE SEED.
#   P1 BOTH IN ONE FRAME. The goblin and the plant are both wholly inside the
#      frame, neither cropped. This is done_when's whole point and a frame
#      that fails it fails the beat however well it is drawn.
#   P2 ROOTED AND ATTACHED. One stem meets the ground; the leaves are attached
#      to that stem. Any leaf not joined to a stem fails this, whatever else
#      is in shot -- eight of twelve prior candidates died here.
#   P3 THE PLANT IS THE SAPLING. Exactly ONE plant, TWO leaves, ONE thin stem.
#      Extra stalks, extra leaves, a bead-strung vine, a multi-node weed or a
#      bud/ball at the tip all FAIL.
#   P4 SCALE. The plant is SHORTER than the seated goblin's head. It may not
#      tower over him (§3.2: ~40 cm, always shorter than he is).
#   P5 OUTDOORS IN AN OPEN FIELD. Real grass at ground level and real sky or
#      treeline. An interior, a wall panel, a white void or a floating disc of
#      grass in empty sky all FAIL -- his own beat-21 ruling was *"doesnt look
#      like the sapling is outside"*.
#   P6 ONE LEAN ADULT GOBLIN, SEATED, IN A PATCHWORK CLOAK. Not a child, not a
#      chibi, not two figures, not standing, not in modern clothes.
#   P7 NOT A CLOSE-UP. His body and the plant both read at a glance.
#      done_when names this failure by name.
#   P8 GAZE: NOT SCORED, BY DESIGN. See the §6 paragraph above.
#
# FAIL MODES NAMED IN ADVANCE, recorded whether or not they fire, so a defect
# that arrives cannot be reported as a surprise or quietly dropped:
#   Q1 the plant grows out of his shoulder or head (mac r3 and r5 both did)
#   Q2 a scale double -- one giant figure and one tiny one (mac r2)
#   Q3 a hill-sized plant (mac r6, on `taller than he is`)
#   Q4 a sphere or bud on the stem tip (ep2-b15-plate-0814, the init that
#      poisoned all six 0815 motion takes)
#   Q5 indoors, wall panels, a doorway (the four `tonight` stills)
#   Q6 modern dress -- shirt, cargo shorts, sneakers (plate-0814's reference)
#   Q7 a mature tree, thick branch or trunk anywhere in frame
# A term found loose is said so and tightened FORWARD, never rewritten after
# the picture is seen.
#
# ONE SAMPLE, one seed. $0, Apple MPS, nothing on the box, no provider.
DRAFTS[15] = {
    "slug": "good-listener",
    "prompt": (
        "1boy, solo, lean wiry adult goblin man, green skin, bald head, "
        "patchwork cloak, sitting in the grass beside a tiny 40cm sapling "
        "rooted in the soil, two leaves on one thin stem, both hands on his "
        "knees, his face visible, wide shot, sunny grassy field, cinematic "
        "lighting, masterpiece, best quality, very aesthetic"
    ),
    # Beat 19 r3's negative with the three fruit terms removed -- this beat has
    # no fruit in it, and a negative naming a noun the positive never mentions
    # is dead weight that this repo has already audited off 94 specs once. The
    # four added terms are the beat-15 failures actually observed, not guesses.
    "negative": (
        "text, 2boys, girl, baby, child, chibi, elf, standing, walking, "
        "close-up, portrait, floating leaves, leaf on head, potted plant, "
        "flower pot, large tree, thick branch, trunk, forest, house, indoors, "
        "night, dark, photorealism, 3d render"
    ),
    "seed": 20260819,
    "done_when": (
        "he and the SAPLING ARE IN THE SAME FRAME, the plant rooted and "
        "attached, one stem and two leaves, shorter than he is, outdoors in "
        "an open field, one seated lean adult goblin in a patchwork cloak, "
        "not a close-up. Gaze is deliberately unscored (STEWARDSHIP.md §6 -- "
        "beat 15's restage is unread by the founder)."
    ),
    "why": (
        "Beat 15 is a SLATE in every cut we have made. Twelve wave stills, six "
        "mac plates and six LTX motion takes have been judged against it and "
        "all 24 fail, every one of them on the plant or on the frame rather "
        "than on the acting. All six motion takes were animated from ONE init "
        "whose plant is a wiry weed topped with a white sphere, so no reseed "
        "can reach the bar. This is the plate that has to exist before beat 15 "
        "can be animated at all, and it is the first one asked for since the "
        "2026-08-17 knee-height restage."
    ),
}

# --------------------------------------------------------------------------
# r1 SCORED, 2026-08-19, Apple MPS, seed 20260819, 141.1s, rc 0.
# farm-out/ep2-b15-mac-plate-0819/15-good-listener-mac-plate-r1s1.png
# sha256 recorded in the sidecar beside it.
#
# VERDICT: 6 OF 7, AND ALL SEVEN NAMED FAIL MODES STAYED SILENT. This is the
# best beat-15 plate that exists, on the first draw of the new ladder, and the
# six things it fixed are the six things twenty-four prior artifacts died on.
#   P1 BOTH IN ONE FRAME .......... PASS. Both wholly inside the frame, neither
#      cropped. Twenty-four artifacts had not managed this with a real plant.
#   P2 ROOTED AND ATTACHED ........ PASS, cleanly. One stem rises out of the
#      grass with its base in shot and every leaf joins it. This is the clause
#      that killed eight of the twelve wave stills (detached leaves floating at
#      the frame edges) and `rooted in the soil` in the POSITIVE bound on the
#      first draw -- the positive-placement law holds again.
#   P3 THE PLANT IS THE SAPLING ... FAIL, AND IT IS THE ONLY FAILURE. One
#      plant, one thin stem, no bead vine, no ball -- but the leaves sit on
#      TWO OR THREE NODES, roughly four or five of them, where the bar says
#      exactly two. `two leaves` moved the count enormously (the init under all
#      six motion takes was a multi-node weed topped with a sphere; mac r6 was a
#      hill) and did not reach two. Scored FAIL as written, not softened.
#   P4 SCALE ...................... PASS, and this is the first time. The
#      plant's top sits BELOW the seated goblin's head. Every previous beat-15
#      draw asked for a plant taller than he is and got one.
#   P5 OUTDOORS IN AN OPEN FIELD .. PASS. Grass to the horizon, real sky and a
#      cloud band. No interior, no wall panel, no floating disc of turf.
#   P6 ONE LEAN ADULT GOBLIN ...... PASS. One figure, seated in the grass, lean
#      and long-limbed with an angular skull, in a plaid patchwork cloak, both
#      hands on his knees. Not a child, not a chibi, not standing, no sneakers.
#      `boy` -> `lean wiry adult goblin man` did exactly what beat 08 measured.
#   P7 NOT A CLOSE-UP ............. PASS. Wide, whole body, plant reads.
#   P8 GAZE ....................... NOT SCORED, as registered. (Recorded and
#      not scored: his head is down and turned slightly toward the plant side.)
#   Q1-Q7 ......................... NONE FIRED. No plant on his shoulder, no
#      scale double, no hill, no bud-sphere, no interior, no modern dress, no
#      mature tree. Seven named in advance, seven silent.
#
# FOUND LOOSE AND TIGHTENED FORWARD, NOT REWRITTEN: HE IS WEARING SPECTACLES,
# and nothing in the prompt asks for eyewear. No term of the bar covers it so
# it is not scored here, and it is not waved off either -- an unprompted
# attribute arriving on a face is precisely what the eyewear-binding lane is
# chasing on beats 05 and 10, and this is a third independent sighting of it on
# a prompt that never mentions glasses. It is added to the bar as P9 FROM r2
# FORWARD, where it can be scored on a draw that was measured against it.
#
# ==========================================================================
# BEAT 15 REVISION 2. THE ONE VARIABLE IS THE LEAF COUNT. NOTHING ELSE MOVES.
# ==========================================================================
# THE VARIABLE, and it is the only clause that differs from r1:
#   `two leaves on one thin stem`  ->  `two leaves at the top of one bare stem`
# `bare` says the stem carries nothing between the soil and the leaves, which
# is the second node the picture actually grew; `at the top` puts both leaves
# at ONE node instead of leaving their position to the checkpoint. This is the
# same move beat 19 r3 made and it is worth making once here for a reason that
# beat did not have: there the plant clause competed with a fig hanging off it
# and the count never came down, HERE THERE IS NO FRUIT and the count already
# came most of the way. Beat 19's ladder stopped at three rungs on a closed
# question; this is rung two on an open one, and if r2 does not reach two
# leaves the answer is the composite route that lane already named
# (pipeline/composite-init-pattern.md), not a rung three.
#
# EVERY OTHER CLAUSE IS r1's, BYTE FOR BYTE -- the cast wording, `sitting in
# the grass`, `rooted in the soil`, `40cm`, `both hands on his knees`, `his
# face visible`, `wide shot`, `sunny grassy field` and the style tail. Six
# passing terms are CARRIED, not re-tested. STILL NO GAZE WORD, in either
# direction: the §6 line r1 was drawn on does not move because a leaf did.
# The negative is restated byte for byte below, per this file's exit-6 guard.
# Seed unchanged at 20260819, so r1 and r2 are two draws of ONE seed differing
# by four words. ONE SAMPLE. $0, Apple MPS, nothing on the box.
REVS[(15, 2)] = {
    "slug": "good-listener",
    "prompt": (
        "1boy, solo, lean wiry adult goblin man, green skin, bald head, "
        "patchwork cloak, sitting in the grass beside a tiny 40cm sapling "
        "rooted in the soil, two leaves at the top of one bare stem, both "
        "hands on his knees, his face visible, wide shot, sunny grassy field, "
        "cinematic lighting, masterpiece, best quality, very aesthetic"
    ),
    # Byte-identical to DRAFTS[15]'s, restated per exit 6. `glasses` is NOT
    # added: r1's spectacles are one sighting and the standing finding in this
    # repo is that the negative does not reach a noun the positive left vague.
    # Putting eyewear in the negative on the same draw that moves the leaf
    # clause would also be two variables in one picture.
    "negative": (
        "text, 2boys, girl, baby, child, chibi, elf, standing, walking, "
        "close-up, portrait, floating leaves, leaf on head, potted plant, "
        "flower pot, large tree, thick branch, trunk, forest, house, indoors, "
        "night, dark, photorealism, 3d render"
    ),
    "seed": 20260819,
    "done_when": (
        "r1's bar, unchanged in every term, PLUS P9 EYEWEAR: no spectacles or "
        "goggles on his face, nothing in the prompt asks for them. P3 is NOT "
        "loosened to accept r1's node count -- a bar edited to match the rung "
        "it is about to score certifies nothing. Gaze stays unscored (§6)."
    ),
    "why": (
        "r1 scored 6 of 7 with all seven named fail modes silent, and the one "
        "failure is the leaf count: two or three nodes where the script says "
        "'his eyes are level with the two leaves'. One clause moves."
    ),
}
# --------------------------------------------------------------------------
# r2 SCORED, 2026-08-19, Apple MPS, seed 20260819, rc 0, 77/77 tokens.
# farm-out/ep2-b15-mac-plate-0819/15-good-listener-mac-plate-r2s1.png
# sha256 b4b28ab54f0ca7dace0b50f302a101fd085cc2f4fcdbfc45f13bd92446d9a103
#
# VERDICT: 6 OF 8. THE ONE VARIABLE DID NOT MOVE ITS TERM, AND THAT IS THE
# RESULT. Two rungs have now aimed two wordings at the leaf count and the
# picture has not changed shape.
#   P3 THE PLANT IS THE SAPLING . FAIL, INDISTINGUISHABLE FROM r1. Still one
#      thin stem carrying leaves on TWO OR THREE NODES, roughly five of them.
#      `bare` did not clear the stem and `at the top` did not gather the pair.
#      Everything the words could buy on this axis was already bought by r1's
#      `two leaves`, which took it from a multi-node weed with a sphere down to
#      a seedling and then stopped.
#   P9 EYEWEAR .................. FAIL, and this is the term's first scored
#      outing. HE IS STILL WEARING SPECTACLES. Nothing in either prompt asks
#      for eyewear; it has now arrived on two different prompts at the same
#      seed on this checkpoint, which makes it a second independent sighting
#      for the eyewear-binding lane rather than a fluke of one draw.
#   P1, P2, P4, P5, P6, P7 ...... PASS, all six carried intact from r1. Both
#      wholly in frame, rooted and attached, plant below his head, open field
#      to a real horizon, one seated cloaked lean adult with both hands on his
#      knees, wide shot. Nothing regressed.
#   P8 GAZE ..................... NOT SCORED (§6). Recorded: head down, level.
#   Q1-Q7 ....................... NONE FIRED, second draw running.
#
# THE LADDER STOPS AT TWO, AND THE RULE IS THIS FILE'S OWN, WRITTEN BY THE
# BEAT-19 LANE TONIGHT: "THE PLANT IS NOT REACHABLE BY WORDS ON THIS
# CHECKPOINT and a fourth wording is the thing this repo has repeatedly been
# wrong to fire." Beat 19 needed three rungs to learn it because its plant
# clause competed with a fig; beat 15 has no fruit and learned it in two. A
# rung three is NOT filed.
#
# THE ROUTE, NAMED AND NOT FIRED, and beat 15 is a far cheaper composite than
# beat 19 because ITS OTHER HALF IS ALREADY DONE:
#   * THE FRAME IS SOLVED. r1 and r2 pass six of eight terms — the seated
#     cloaked lean adult, the open field, the scale, the wide two-shot framing
#     and both subjects inside the frame. Twenty-four prior artifacts could not
#     produce that frame with any plant in it at all.
#   * THE PLANT IS ALREADY DRAWN AND ALREADY PICKED, one beat away.
#     `ep2-b12-tightB` is beat 12's PICK and 002b-t0-c.yaml records that it
#     "SURVIVES INTACT" through the knee-height rewrite, prompt untouched byte
#     for byte. It is the canon leaves, held to a bar, on this show.
#   * SO THE NEXT BEAT-15 STEP IS A COMPOSITE INIT — r1's man, pose, cloak,
#     field, scale and framing with beat 12's leaves composited in on a thin
#     stem at ~40 cm, a hand's width from his face — NOT a third prompt. The
#     pattern is in pipeline/composite-init-pattern.md and has been built twice
#     already (beat14_field_composite.py, beat08_gesture_composite.py). That is
#     a build rather than a rev, it is bigger than this lane's one job, and it
#     is named here so the next lane inherits a route instead of a mystery.
#
# WHAT THE TWO RUNGS BOUGHT, so they do not read as waste. Beat 15's recorded
# blocker was that no plate we owned put HIM AND A ROOTED PLANT OUTDOORS IN ONE
# FRAME AT CANON SCALE — eight candidates had floating leaves, four were
# indoors, six mac plates put the plant on his shoulder or made it the size of
# a hill, and the init under all six motion takes was a weed with a ball on it.
# Two draws, and that blocker is DEAD: P1, P2, P4 and P5 pass twice running.
# Beat 15 is no longer blocked on "we cannot get him and a plant into a field
# together"; it is blocked on "we cannot get the leaf count to two", which is a
# smaller, differently-shaped problem with a route and a passing asset attached.
# --------------------------------------------------------------------------

REVS[(9, 3)] = {
    # --------------------------------------------------------------------------
    # BEAT 09, r3. THE ONE VARIABLE: ONE WORD OF HAIR COLOUR, `dark` -> `black`.
    #
    # THIS RUNG WAS NAMED, MEASURED AND DELIBERATELY LEFT UNFIRED BY THE LANE
    # THAT FOUND IT, and this is that lane's sentence being honoured rather than
    # a new idea: REVS[(9,2)]'s seed-batch result reads "F1 THE HAIR IS THE
    # WORDING, 7 OF 7 ... so per the rule as written, the next thing beat 09
    # tries is `black hair`, which is this checkpoint's own tag, instead of
    # `dark`. THAT IS THE ONE CHANGE THIS BEAT NEEDS AND THIS LANE DOES NOT
    # SPEND A FIFTH SEED ON IT -- it is named, measured and left for the next
    # lane rather than guessed at now." The F1 rule was written BEFORE the four
    # seeds rendered, and it fired at 7 of 7: mid-to-dark brown and shaggy at
    # every render beat 09 has ever had, with `dark cropped hair` in the
    # positive every single time. Guard A's hair is near-black and CROPPED.
    #
    # WHY `cropped` IS NOT TOUCHED. The named change is the COLOUR word and only
    # the colour word -- "`black hair` ... instead of `dark`" -- so the edit is
    # the single substitution `dark` -> `black` inside the same noun phrase.
    # `cropped` -> `short hair` (the checkpoint's own length tag) is a SECOND
    # axis and is named at the bottom of this block, not fired here. A rung that
    # moved both words could not say which one moved the picture.
    #
    # AND A MECHANISM FOR THE 7-OF-7 THAT NOBODY HAS WRITTEN DOWN, FOUND BY
    # READING THE TWO STRINGS SIDE BY SIDE RATHER THAN BY RENDERING ANYTHING.
    # THIS PROMPT PAIR HAS ASKED FOR `dark` HAIR AND FORBIDDEN `dark` AT THE
    # SAME TIME, AT ALL SEVEN RENDERS. The negative's last clause is
    # `photorealism, 3d render, dark, night` -- `dark` is in there as a LIGHTING
    # term, aimed at the night-scene prior, and it has been sitting beside a
    # positive that says `dark cropped hair` since r1. SDXL's text encoder has no
    # scoping: there is no mechanism by which a negative `dark` subtracts
    # darkness from the LIGHT and not from the HAIR. So the one condition this
    # beat has never once met is the one condition its own negative was
    # cancelling, which is a far better explanation of 7 of 7 than "the model
    # will not draw black hair" -- and it is a prediction, not a story, because
    # `black` appears NOWHERE in the negative. If H1 lands, that is the reading
    # confirmed; if H2 lands, this mechanism is wrong and it says so in advance.
    # WHY THE EXISTING GUARD DID NOT CATCH IT, which is the reusable part:
    # plate_scratch's clash check at line 5184 splits both strings on commas and
    # intersects whole chunks, so it sees `a guard man with dark cropped hair and
    # wire-rim glasses` against `dark` and finds no collision. A TOKEN-level
    # check over the same two strings would have fired on day one. Named as a
    # guard worth adding, and not built here -- one lane, one variable.
    #
    # WHY SEED 20260820 AND NOT THE PARENT'S 20260817, WHICH LOOKS LIKE A SECOND
    # VARIABLE AND IS NOT. It makes the A/B EXACT rather than approximate: there
    # is a committed, scored picture at this exact seed and wording --
    # farm-out/ep2-b09-mac-plate-0817/09-the-pause-mac-plate-r2s4.png,
    # sha256 in its sidecar -- so this render differs from a picture already on
    # disk by one token and nothing else. The seed also carries the ONE
    # measurement beat 09 cannot buy with words: r2s4 is the only render of the
    # seven whose head clears P3, read off a 50px ruler at >=56% of frame height
    # where the other six posted 48-53%. REVS[(9,2)]'s F3 result is explicit --
    # "THE HEAD SIZE IS A SEED VARIABLE, NOT A WORDING LIMIT ... `face filling
    # the frame` CAN reach the bar and the framing needs seeds, not new words."
    # Testing the colour word at the one seed known to satisfy the framing
    # clause is therefore the cheapest place the answer can be worth anything.
    #
    # WHAT THIS RUNG CANNOT DO, STATED FIRST SO NOBODY READS A PASS INTO IT.
    # IT CANNOT PRODUCE A USABLE PLATE, and beat 09's slate does not close
    # tonight on the strength of it. Two of the beat's three open faults are
    # untouched here and both are recorded:
    #   * THE EYES. P7 needs them OPEN. At this seed they are SHUT (r2s4), and
    #     the tag is a 1-in-4 RATE and not a lever -- REVS[(9,2)]'s F2 retracted
    #     its own eye rule at four seeds: open once, a wink once, open-but-blank
    #     white with no irises once, shut once. So P7 is an EXPECTED FAIL at
    #     this seed and is NOT this rung's business.
    #   * THE ADULT READ. The face reads adolescent here and at 7 of 12 of the
    #     box cast batch (`cast-0817-scores.yaml` c7: 5 of 12). No age tag is in
    #     this prompt at all; `1boy` is the only person tag. Named below.
    # NO SEED IN THE HISTORY OF THIS BEAT HAS EVER PRODUCED THE FRAMING AND OPEN
    # EYES TOGETHER -- s1 has the eyes and a 48% head, s4 has a 56% head and shut
    # eyes -- so the plate that beat 09 ships off is a render-N-and-pick on a
    # SETTLED wording, and the wording is what this rung is for.
    #
    # THE BAR IS P1-P7 UNCHANGED, exactly as committed in 7b193483 and carried
    # by r2, and the outcome on ONE clause is what this rung claims:
    #   H1 HAIR NEAR-BLACK AND STILL CROPPED-ISH -> the colour word IS the lever,
    #      the record's F1 rule is discharged, and beat 09's remaining faults are
    #      the eyes (a rate, needs N-and-pick) and the age (one unfired tag).
    #   H2 HAIR STILL MID-BROWN AND SHAGGY -> the colour is NOT reachable by
    #      wording on this checkpoint at 8 of 8, the wording ladder on hair
    #      CLOSES at that count by this repo's own three-rung rule, and the next
    #      instrument is compositional: the box cast rung already MEASURED that
    #      IP-Adapter reference conditioning does move hair (near-black at 3 of
    #      12) and pays for it in framing (25-35% against 55%, its own
    #      pre-registered fail mode firing 12 of 12). Those two facts together
    #      make beat 09's plate a REFERENCE-PLUS-CROP job, not a prompt job, and
    #      that is a build with a consumer rather than a mystery.
    #   H3 THE HEAD DROPS OFF 56% -> one token reshuffled the draw, F3's
    #      seed evidence does not transfer across wordings, and the framing has
    #      to be re-won at whatever wording survives. Report the ruler reading
    #      either way, measured and not estimated.
    #   H4 ANY OF P1/P2/P4/P5/P6 REGRESSES -> report it by name. P1's glasses
    #      half and P4 have now passed 7 of 7 each and a regression on either
    #      from a hair token would be a finding about attribute bleed, not noise.
    # NOT SCORED HERE: whether this plate is castable, promoted or ack'd. No
    # plate_ack, no pick, no leaf, nothing enters any cut from this rung.
    #
    # NAMED AND NOT FIRED, so the next lane inherits a route:
    #   (a) `cropped` -> `short hair`, the length half of the same fault, one
    #       token, only worth firing if H1 comes back black-but-shaggy.
    #   (b) AN AGE TAG. There is none in this prompt; `mature male` is this
    #       checkpoint's own adult tag and the positive-placement law this repo
    #       has now watched fire five times says the vacancy is why every frame
    #       decides his age afresh. One token, one rung, unfired.
    #   (c) render-N-and-pick for the eyes ONCE (a) and (b) are settled -- a
    #       judged wording at four fresh seeds, which is what F2's retraction
    #       leaves as the only honest route to an open pair.
    # --------------------------------------------------------------------------
    "slug": "the-pause",
    # r2's positive with ONE substitution: `dark cropped hair` -> `black cropped
    # hair`. Every other token is byte-identical to REVS[(9,2)].
    "prompt": (
        "1boy, solo, close-up, face filling the frame, a guard man with "
        "black cropped hair and wire-rim glasses, eyes open, thoughtful, "
        "mouth closed, a tan wrap tunic collar and a white sash on his "
        "shoulder, tall grass and a green hedgerow behind him, sunny "
        "day, masterpiece, best quality"
    ),
    # Restated BYTE FOR BYTE from REVS[(9,2)], which restated it byte for byte
    # from r1. It is unchanged, and it is written out here because the merge site
    # merges over DRAFTS[9] and not over r2 -- a rev that named only a prompt
    # would inherit the base draft's negative silently, which is the landmine
    # plate_scratch.py guards at line 5166 and refuses on.
    "negative": (
        "text, 2boys, 3boys, crowd, bald, closed eyes, hands, holding "
        "object, clipboard, armor, helmet, knight, child, girl, white "
        "background, simple background, grey background, blank "
        "background, plain background, sky, indoors, full body, wide "
        "shot, distant, photorealism, 3d render, dark, night"
    ),
    # The r2 SEED BATCH's s4. See the seed note above: this is the only seed of
    # the seven whose head clears P3, and there is a committed scored picture at
    # this seed and the parent wording to A/B against.
    "seed": 20260820,
}


def measure(pipe, text: str) -> tuple[int, bool]:
    tok = pipe.tokenizer
    ids = tok(text, truncation=False)["input_ids"]
    return len(ids), len(ids) > tok.model_max_length


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beat", type=int, required=True)
    ap.add_argument("--node", default="002b-first-citizen")
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--i-have-seen-a-sample", action="store_true")
    ap.add_argument("--rev", type=int, default=1, help="revision of the draft")
    ap.add_argument("--dry", action="store_true", help="measure, draw nothing")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if a.beat not in DRAFTS:
        print("!! no inline draft for beat %d. Present: %s"
              % (a.beat, sorted(DRAFTS)))
        return 4
    d = dict(DRAFTS[a.beat])
    if a.rev != 1:
        if (a.beat, a.rev) not in REVS:
            print("!! no rev %d for beat %d" % (a.rev, a.beat)); return 4
        # ------------------------------------------------------------------
        # THE MERGE SITE, AND THE LANDMINE THAT LIVES HERE. READ BEFORE
        # WRITING A REV.
        # ------------------------------------------------------------------
        # A REV MERGES OVER `DRAFTS[beat]`, NOT OVER THE REV BEFORE IT. So a
        # rev that names only a `prompt` INHERITS THE BASE DRAFT'S NEGATIVE,
        # silently, with nothing in the output to say so.
        #
        # That is not a theoretical hazard. It nearly ruined an experiment on
        # 2026-08-16: beat 17's BASE draft is the r1 TIGHT INSERT, whose
        # negative reads `text, face, head, portrait, looking at viewer,
        # FULL BODY, WIDE SHOT, standing, ...`. Rev 2 and rev 3 of that same
        # beat exist to test A WHOLE BODY FILLING THE FRAME -- the exact
        # composition that negative forbids. A rev that had named only its
        # prompt would have drawn a plate fighting its own negative and the
        # only symptom would have been a picture that came back subtly wrong,
        # read as a finding about the checkpoint rather than a bug in a dict
        # merge. IT FAILS SILENTLY IN THE DIRECTION OF "THE TEST QUIETLY DID
        # NOT TEST WHAT YOU THOUGHT", which is the worst direction there is.
        #
        # Two guards below make that structural instead of a matter of the
        # next lane being careful. Restating the negative byte for byte in the
        # rev, as (17,2) and (17,3) do, satisfies both.
        rev = REVS[(a.beat, a.rev)]
        if "prompt" in rev and "negative" not in rev:
            print("!! rev %d of beat %d overrides `prompt` but not `negative`, "
                  "so it would INHERIT the base draft's negative silently.\n"
                  "   A rev merges over DRAFTS[%d], never over the rev before "
                  "it. Restate the negative in the rev -- byte for byte if it "
                  "is meant to be unchanged -- so the pair that actually gets "
                  "drawn is visible in one place."
                  % (a.rev, a.beat, a.beat))
            return 6
        d.update(rev)

    # SECOND GUARD, and it runs for base drafts too: NO TAG MAY APPEAR IN BOTH
    # THE POSITIVE AND THE NEGATIVE. A prompt asking for `full body` against a
    # negative forbidding `full body` is not a weak prompt, it is a
    # contradiction, and the picture that comes back is unattributable. This is
    # the check that catches the merge landmine above even if someone deletes
    # the first one, because the inherited-negative failure always shows up as
    # exactly this collision.
    pos_tags = {t.strip().lower() for t in d["prompt"].replace(";", ",").split(",")}
    neg_tags = {t.strip().lower() for t in d["negative"].replace(";", ",").split(",")}
    clash = sorted(t for t in (pos_tags & neg_tags) if t)
    if clash:
        print("!! the positive and the negative BOTH name: %s\n"
              "   That is a contradiction, not a weak prompt, and whatever "
              "comes back cannot be attributed. If this is beat %d at a rev, "
              "check whether the rev inherited DRAFTS[%d]'s negative by "
              "accident -- that is how this collision usually happens."
              % (", ".join(repr(c) for c in clash), a.beat, a.beat))
        return 7

    if a.seeds > 1 and not a.i_have_seen_a_sample:
        print("!! %d seeds requested. ONE SAMPLE BEFORE ANY BATCH "
              "(CLAUDE.md, founder 2026-08-03) -- a recipe change gets one "
              "picture looked at first. Pass --i-have-seen-a-sample only if "
              "one has actually been seen." % a.seeds)
        return 8

    # STEWARDSHIP §6: no media from a node the founder has not approved.
    from render_local import approved  # noqa: E402
    if not approved("sapling", a.node):
        print("!! node %s is not founder-approved (§6). Refusing." % a.node)
        return 9

    out_dir = Path(a.out) if a.out else (
        REPO / "farm-out" / ("ep2-b%02d-mac-plate-%s" % (a.beat, date.today().strftime("%m%d"))))
    out_dir.mkdir(parents=True, exist_ok=True)

    import torch                                                  # noqa: E402
    from diffusers import StableDiffusionXLPipeline               # noqa: E402

    print("loading %s ..." % BASE, flush=True)
    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE, torch_dtype=torch.float16, use_safetensors=True)
    pipe.to("mps")

    np_, ntrunc = measure(pipe, d["prompt"])
    nn_, ntruncn = measure(pipe, d["negative"])
    print("TOKENS positive %d/77 %s" % (np_, "TRUNCATED!!" if ntrunc else "ok"))
    print("TOKENS negative %d/77 %s" % (nn_, "TRUNCATED!!" if ntruncn else "ok"))
    if ntrunc or ntruncn:
        print("!! a prompt overflows 77 tokens and its tail would be dropped "
              "silently. Refusing to draw. Shorten it.")
        return 5
    if a.dry:
        print("--dry: measured only, nothing drawn.")
        return 0

    for i in range(a.seeds):
        seed = d["seed"] + i
        g = torch.Generator("cpu").manual_seed(seed)
        t0 = time.time()
        img = pipe(prompt=d["prompt"], negative_prompt=d["negative"],
                   width=W, height=H, num_inference_steps=STEPS,
                   guidance_scale=GUIDANCE, generator=g).images[0]
        dt = time.time() - t0
        stem = "%02d-%s-mac-plate-r%ds%d" % (a.beat, d["slug"], a.rev, i + 1)
        png = out_dir / (stem + ".png")
        img.save(png)
        sha = hashlib.sha256(png.read_bytes()).hexdigest()
        meta = {
            "platform": "local-gpu (Apple Silicon, MPS)",
            "model": BASE,
            "model_licence": "CreativeML Open RAIL++-M (use restrictions travel; D15)",
            "cost_usd": 0.00,
            "shot_beat": a.beat,
            "beat_slug": d["slug"],
            "size": "%dx%d" % (W, H),
            "steps": STEPS,
            "guidance": GUIDANCE,
            "seed": seed,
            "render_seconds": round(dt, 1),
            "png_sha256": sha,
            "prompts_from": "authored for this plate test (shots.md UNTOUCHED)",
            "prompt": d["prompt"],
            "negative_prompt": d["negative"],
            "done_when": d["done_when"],
            "why_this_plate": d["why"],
            "founder_verdict": None,
            # A plate is a fixture, never a take. These two keys are written
            # so the standing sidecar guard ("approved: false, provisional,
            # cost_usd 0") is satisfied by the file itself rather than by a
            # lane remembering to say so in a report. `approved` is about the
            # PICTURE and is not the STEWARDSHIP.md §6 node approval, which is
            # checked separately above and would have refused the run.
            "approved": False,
            "provisional": True,
            "revision": a.rev,
            "scored": False,
        }
        (out_dir / (stem + ".yaml")).write_text(
            "\n".join("%s: %s" % (k, json.dumps(v)) for k, v in meta.items()) + "\n")
        print("wrote %s  (%.1fs, seed %d)" % (png, dt, seed), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
