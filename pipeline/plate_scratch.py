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
            "blank paper, no field, no second guard and no scavenger. Its "
            "done_when needs three bodies and a belly in frame. No wording "
            "reaches a target that is not in the picture, which is why every "
            "lever failed. Cycle 018 measured the other half of this: on beat "
            "17's WIDE full-body plate with ~40% headroom the engine moved a "
            "whole body in 12 of 12 takes. This plate gives beat 08 beat 17's "
            "composition -- wide, full-length, real field, room above the "
            "heads -- and changes nothing else."
        ),
        "prompt": (
            "3boys, full body, wide shot, scenery, standing in a green field, "
            "two adult guard men in uniform facing a lean adult goblin man, "
            "green skin, bald head, patchwork cloak, near guard holds a "
            "wooden clipboard at chest height, small figures low in frame, "
            "wide blue sky above, sunny day, masterpiece, best quality"
        ),
        "negative": (
            "text, close-up, portrait, upper body, cropped, bust, "
            "1boy, 2boys, 4boys, solo, white background, simple background, "
            "baby, child, chibi, stitches, scars, spear, staff, sword, "
            "tree, forest, house, indoors, photorealism, 3d render, dark, night"
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
        "prompt": (
            "2boys, full body, medium shot, two guard men standing together "
            "in tall grass, hedgerow behind, near taller man with light "
            "sandy hair, cream shirt, white shoulder sash, brown wrap skirt, "
            "holding a large flat bark board in both hands, one man behind "
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
        "prompt": (
            "1boy, a small goblin boy, green skin, bald head, patchwork "
            "cloak, solo, in a sunny grassy field, raises a ripe fig in both "
            "hands in front of him like evidence, huge eyes widening as he "
            "looks up at a bare branch above. Warm amber afternoon light, "
            "cinematic lighting, detailed, newest, masterpiece, best "
            "quality, very aesthetic"
        ),
        "negative": (
            "photorealistic, text, girl, child, glowing eyes, glowing orb, "
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
