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
}

# Revisions. ONE VARIABLE PER REVISION, and the reason is written down before it
# renders. `--rev N` merges over the base draft above.
REVS = {
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
