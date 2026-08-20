#!/usr/bin/env python3
r"""Derive ep2-b13-tallcomp-0820 from ep2-b13-sapcomp-0820. ONE variable: the init.

WHAT THIS RUNG IS. On /review/ep2-b13-shade-0820 the author is asked one taste
question: does beat 13's current take satisfy "tips his head sideways into the
sapling's hand-sized patch of shade", OR may the plant be drawn TALLER THAN
CANON in this one shot so the shade can reach his face? Answer A has had pixels
for days. Answer B had none, because the only tool that can draw it refuses to
(NO_DRAW_ABOVE_Y = 640 in pipeline/beat13_shade_composite.py exists precisely so
nothing it draws can reach his hands, arms or face). That refusal was opened
once, under --founder-option, and produced the composite this job samples.

A COMPOSITE IS NOT A SAMPLE. The drawn plant is flat vector art laid over the
plate; whether the sampler will convert it into the frame's own line quality is
the open question, and the sapcomp parent is the only evidence that 0.30 does
that on this exact plate. So this rung changes the init and NOTHING ELSE:
animagine-xl-3.1 base weights in the SDXL inpaint pipeline, 40 steps, cfg 7.5,
strength 0.30, padding_mask_crop 64, blur 8, seed 20260820, and the prompt and
negative carried byte-for-byte. The b13 negative is 72 of 77 CLIP tokens; one
added word silently drops the tail, so it is not touched.

WHY derive_spec RATHER THAN A HAND-ROLLED CLONE. The parent is SCORED -- it
carries verdict_0820 and NOTE_this_spec_is_SCORED -- and a deny-list clone leaks
exactly that class of key under exactly that class of name. derive_spec's
allow-list drops both by construction, and prints what it dropped.

$0. No model, no network, no GPU in this script.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b13-sapcomp-0820.yaml"
OUT = "pipeline/jobs/ep2-b13-tallcomp-0820.yaml"
NEW_ID = "ep2-b13-tallcomp-0820"

INIT_SHA = "bf2d258b7f007173bc9c9b898f382d03625f97cdea943cce9381f66baf84cd0f"
MASK_SHA = "b1a0fb39d3bd64c2f52ecfc2f8da050e5d2eb9ca560c7541663413c1ff5b51de"

FETCH = r'''#!/usr/bin/env python3
"""Fetch beat 13's TALLER-THAN-CANON composite and its mask; refuse on any sha mismatch.

No model, no GPU, no spend. Both files are on origin/main, so the sha256s
asserted here are verifiable against the repo by anyone who clones it. They were
made on a Mac by pipeline/beat13_shade_composite.py --founder-option, so they are
NOT on the box's courier worktree -- the courier only ever contains what the box
produced.

THE INIT THIS FETCHES BREAKS CANON ON PURPOSE, AND THAT IS THE WHOLE POINT.
Canon says the sapling is ~40 cm and always shorter than he is (node.md:181-187,
founder 2026-08-16 "thats ridiculous, lmao. the sapling is tiny"). This one is
drawn at ~48.7 cm so the author can look at the exception instead of imagining
it. Nothing built on these bytes may enter a cut.
"""
import hashlib, os, sys, urllib.request

OUT = r"C:\banyan-farm\b13tallcomp-0820"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "farm-out/ep2-b13-tallcomp-0820/")
UA = {"User-Agent": "banyan-city-b13-tallcomp/1.0 (albert.numbro@gmail.com)"}
WANT = {
    "13-the-shade-tallcomp-0820.png":
        "%s",
    "13-the-shade-tallcomp-mask-0820.png":
        "%s",
}

os.makedirs(OUT, exist_ok=True)
for name, want in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(RAW + name, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %%s -- refusing.\n   want %%s\n   have %%s"
                 %% (name, want, have))
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %%s %%d bytes sha %%s OK" %% (name, len(raw), have), flush=True)
''' % (INIT_SHA, MASK_SHA)

DRY_NOTE = (
    "MASK GEOMETRY CHECK. Writes the mask and exits BEFORE a model is loaded, so a "
    "wrong mask costs seconds instead of a GPU fire. THIS MASK IS TWICE THE PARENT'S: "
    "80592 px, 7.97 percent of the frame, against the sapcomp parent's 41497 px and "
    "4.10 percent -- because the plant is 921 px tall here instead of 485. Like the "
    "parent's it is the DRAWN PLANT'S FOOTPRINT ALONE dilated, and the composite is "
    "purely additive: there was no wrong plant near him to erase. WHAT TO CHECK ON THE "
    "DRY PNG: that the white region is a tall narrow column up the left of the frame "
    "and that it does NOT touch his FACE (box x 250..570 y 60..500), his hands or his "
    "folded arms. The compositor measured 37224 drawn px above y=640 -- the guard the "
    "founder-option deliberately lifted -- and ZERO of them inside his face box, with "
    "C2 face-box maxdiff 0 armed and passing. If the dry mask reaches his face, the "
    "composite is wrong and this job stops here at $0.")

SAMPLE_NOTE = (
    "ONE SAMPLE, ONE SEED, ONE VARIABLE. Every sampler number is the sapcomp parent's, "
    "unchanged: 40 steps, cfg 7.5, strength 0.30, pad-crop 64, blur 8, seed 20260820, "
    "animagine-xl-3.1 base weights in the SDXL inpaint pipeline, and the prompt and "
    "negative byte-for-byte (the negative is 72 of 77 CLIP tokens; a single added word "
    "silently drops the tail). THE ONE VARIABLE IS THE INIT: the taller-than-canon "
    "composite replaces the canon-height one. 0.30 runs int(40 * 0.30) = 12 of 40 "
    "denoising steps from a latent that still carries the drawn structure, which is "
    "the setting that converted the parent's flat vector plant into the frame's own "
    "line quality. WHETHER IT DOES THE SAME OVER TWICE THE AREA, AGAINST SKY AND "
    "BACKGROUND FOLIAGE RATHER THAN GRASS, IS THE WHOLE QUESTION AND IT IS NOT "
    "ASSUMED. This is card evidence for /review/ep2-b13-shade-0820. It is not a cut "
    "init, it is not a pick, and passing a bar is not a licence to enter a cut.")

WHY = (
    "ANSWER B OF A TASTE QUESTION NEEDS PIXELS, AND SO FAR ONLY ANSWER A HAS THEM. "
    "The card /review/ep2-b13-shade-0820 asks the author whether the plant may be "
    "drawn taller than canon in this one shot so its shade can reach his face. Four "
    "b13 motion rungs have now failed the shade clause, and the closing note on "
    "ep2-b13-shadelit-0820 says why the route is closed at the plate: `there are only "
    "two ways to put them in one register: raise the plant, or lower his head`, and "
    "raising the plant is refused by the composite tool itself. That refusal was "
    "opened once under --founder-option and drew the taller plant. A DRAWN COMPOSITE "
    "IS FLAT VECTOR ART, NOT A FRAME -- the sapcomp parent is the only evidence that "
    "a 0.30 inpaint converts it into this plate's line quality, and that evidence was "
    "earned on a 4.10 percent mask over grass. This rung asks whether the same recipe "
    "holds over 7.97 percent against sky and foliage. Asking the author to rule on "
    "vector art when a $0 five-minute sample can show him the real frame would be "
    "putting the question badly.")

CONSUMER = (
    "THE REVIEW CARD /review/ep2-b13-shade-0820, AND NOTHING ELSE -- explicitly NOT "
    "the ep2 cut. It sits beside the committed composite as the second half of "
    "answer B: the composite shows the geometry, this shows what the sampler makes of "
    "it. The card owner stages it; this lane does not touch review/. If the author "
    "rules A, these pixels are archived evidence of a road not taken and cost $0. If "
    "he rules B, the exception is written into pipeline/canon.yaml AS an exception so "
    "it cannot drift, and a NEW plate is authored under it -- this still does not "
    "become that plate.")

SUCCESS = (
    "ONE 832x1216 png, its mask and its provenance sidecar, published into "
    "courier-box with a sha256 manifest naming every file in full. LANDING IS A "
    "LOOKED-AT ANSWER, NOT A PASS: the honest outcome of this rung may well be `the "
    "tall plant does not survive the sampler` or `it survives and reads as a "
    "lollipop`, and either of those is a delivered result because it answers the "
    "card's question with pixels. What would NOT be success is a frame nobody opened, "
    "a glob that published nothing, or a verdict written from a metric instead of an "
    "eye. THE CLAUSE THIS CANNOT SETTLE IS NAMED IN ADVANCE: it is a STILL, so it "
    "cannot show the head tipping into the shade. It shows whether a believable tall "
    "plant exists in this frame at all, which is the necessary condition for the "
    "motion rung that would follow a B ruling.")

BAR = {
    "WHICH_BARS_APPLY_AND_WHY_THE_B13_MOTION_BARS_DO_NOT": (
        "Beat 13's rung bars (ep2-b13-shadelit-0820 `bar:`) are G8, H1, H2, H3, A5, A2 "
        "and they were written for a 121-frame CLIP. H1 is mean absolute INTERFRAME "
        "luma over 120 pairs, H3 is `the head travels from upright at f000 to over on "
        "its side by f090`, and A5 is f000-to-f120 whole-frame drift. THIS IS ONE "
        "STILL. There is no f120, so those three clauses have no instrument here and "
        "are NOT carried -- scoring a still against an interframe mean would be "
        "manufacturing a number. H2 (seated, knees up, one stem two leaves) and A2 "
        "(the ratified adult holds) DO survive the translation and are carried below "
        "as P5 and P1. The still-relevant bars are therefore the COMPOSITE-PLATE ones "
        "from the parent ep2-b13-sapcomp-0820 -- P1..P6 and C8 -- adapted, plus the "
        "new risk this init introduces."),
    "G8_IS_NOT_SCORED_HERE_AND_ITS_INSTRUMENT_IS_RETRACTED": (
        "G8_THE_PLANTS_SHADE_IS_ON_HIS_EYES is the clause the whole b13 ladder exists "
        "for and it is NOT scored on this frame. Quoting ep2-b13-shadelit-0820 "
        "`verdict_measured.G8_THE_PLANTS_SHADE_IS_ON_HIS_EYES` verbatim: 'FAIL BY EYE, "
        "AND ITS NUMERIC INSTRUMENT IS RETRACTED -- I wrote that instrument in this "
        "spec and it does not discriminate. As written it PASSES, twice over: at f120 "
        "the eye band (290,350,500,410) reads luma 107.5 against the forehead band "
        "(300,150,480,260) at 210.1, i.e. 102.6 BELOW where the bar asked for 15; and "
        "87.4 above the frame's p5 of 20.1 where the bar asked for 20. IT PASSES JUST "
        "AS HUGELY ON THE CONTROL: shademid reads 94.4 against 189.5, 95.1 below, p5 "
        "11.5. An instrument that passes on the clip already judged G8 FAIL is not an "
        "instrument. THE TELL IS THE DISPERSION, again: both fixed bands read std "
        "88-89 at f120 because the head has tipped right over and neither box is on "
        "the thing it names any more.' TWO CONSEQUENCES, AND THE SECOND IS THE ONE "
        "THAT BINDS THIS JOB. First, no band-difference number is computed here, "
        "because a retracted instrument does not become sound by being pointed at a "
        "different picture. Second, THE SHADE CLAUSE IS OUT OF THIS RUNG'S SCOPE "
        "ANYWAY: this is a still of a head that has not tipped, and the composite's "
        "own sidecar says so -- 'It does not show the shade landing on his face. It "
        "shows a plant whose leaves are at his eye line, which is the necessary "
        "condition.' A reader who scores shade on this frame is scoring the wrong "
        "rung, and a PASS here is not progress on G8."),
    "P1_exactly_one_plant_two_leaves_one_stem": (
        "ONE foreground plant, TWO blades, ONE thin stem, carried from the parent with "
        "the same scope note: the multi-leaflet BACKGROUND SPRIG at x 660..832 y "
        "80..270 is distant scrub, is deliberately not removed, and this clause is not "
        "'exactly two leaves in frame'. THE TRANSLATION RISK IS NEW AND IS NAMED IN "
        "P7: at the +-70 deg the frame corridor forced, the two blades already OVERLAP "
        "in the composite. If the sampler resolves that overlap into a single lobed "
        "organ, the count is one, not two, and this clause FAILS -- overlapping "
        "geometry is not a defence."),
    "P2_THE_PLANT_EXISTS_AND_IS_IDENTIFIABLE": (
        "A reader can point at the sapling and call it a plant. This is the clause "
        "r1s1's whole fault was measured against ('NO IDENTIFIABLE SAPLING ... the "
        "scale reads as big foliage overhead, not a 40 cm plant'), and it is harder "
        "here than on the parent, not easier: a tall thin stem with a lobed head at "
        "the top is the shape of several things that are not plants."),
    "P3_BESIDE_HIM_AND_REACHING_HIS_EYE_LINE": (
        "THE PARENT'S P3 IS INVERTED HERE AND THAT INVERSION IS THE ANSWER UNDER TEST. "
        "The parent scored 'crown at his knee line, y 659 against 595, band +-70'. "
        "This composite puts the crown at y 199 against the same measured knee line "
        "y 595 -- 396 px above it -- because a plant that clears his knee line is the "
        "whole of what answer B asks for. So the SCORED relation here is: the plant is "
        "BESIDE him (rooted at x 150, clear of his footprint) and its blades sit at or "
        "about his EYE LINE, and it is still ONE plant rooted in the ground rather "
        "than something growing out of frame or out of him. The parent's numeric knee "
        "clause is REPORTED AS INVERTED, not scored, because scoring it would be "
        "scoring answer B against answer A's premise."),
    "P4_scale_REPORTED_NOT_SCORED": (
        "~48.7 cm at his depth against canon's ~40 cm, on this plate's head-derived "
        "rate of 18.91 px/cm (435 px / 23 cm). NOT a pass/fail clause, for the "
        "parent's reason and one more. The parent's reason: this is a tight portrait "
        "with NO HORIZON IN FRAME, so there is no ground plane to size against, and "
        "the head-derived rate demonstrably overstates centimetres here -- his seated "
        "mass is 2.5 head-heights where a real adult hugging his knees is about 4. The "
        "additional reason: THE NUMBER BEING OVER CANON IS THE POINT OF THE FRAME, so "
        "a clause that fails on it would fail the job for succeeding. The centimetre "
        "figure is printed beside the picture on the card and the AUTHOR decides "
        "whether 48.7 is an acceptable exception. That is a taste call and it is his."),
    "P5_FOLDED_SMALL_KNEES_UP_ONE_LEAN_ADULT_GOBLIN": (
        "Carried from the parent's P5 and from b13's H2/A2: seated, knees drawn to the "
        "chest, arms wrapped over them, shoulders in, bald green lean adult, one face, "
        "one figure, long pointed ears, cloak. AND HERE IT IS NEARLY ARITHMETIC: the "
        "compositor asserts 0 px changed outside the drawn footprint and face-box "
        "maxdiff 0, and THE MASK DOES NOT COVER HIS FACE. So he goes in byte-identical "
        "to the r1s1 plate the founder's own approved beat produced, and ANY drift in "
        "his face, hands, arms or skull is the SAMPLER'S and is a FAIL of this rung. "
        "The padding_mask_crop round trip does change pixels outside the mask -- the "
        "parent measured 24822 of them, only 239 exceeding a diff of 8 -- so the test "
        "is READABLE drift by eye at 3x, not a nonzero pixel count."),
    "P6_thin_shade_CARRIED_NOT_FIXED": (
        "The frame is DIM -- 'a green gloom with dark, night sitting in the negative' "
        "-- and that is r1s1's recorded plate-level fault, carried by every rung built "
        "on it. A 0.30 pass cannot reach a plate exposure and is not being asked to. "
        "Recorded here so it is not re-scored as this rung's failure. Note also that "
        "ep2-b13-shadelit-0820 already EXONERATED exposure as the suspect behind the "
        "shade clause (its F_EXPOSURE_IS_NOT_THE_SUSPECT fired as predicted), so "
        "nobody should read this frame's dimness as the reason the shade is absent."),
    "P7_THE_TWO_BLADES_MUST_STILL_READ_AS_TWO_BLADES": (
        "NEW ON THIS RUNG, PRE-REGISTERED BEFORE THE PIXELS EXIST, AND IT IS A "
        "CONSEQUENCE OF THE FRAMING RATHER THAN A DRAWING FAULT. The composite's "
        "sidecar records the corridor: 'THE PLANT HAD TO FIT A 248 px CORRIDOR ... "
        "+-50 deg runs off the left edge, +-58 deg puts 114 px inside his face box, "
        "and only +-70 deg clears both -- 34 px of margin left, 7 px right ... at +-70 "
        "deg the two blades are near-vertical and overlap into a two-lobed mass rather "
        "than splaying like the default's.' That is visible in the committed composite "
        "before any sampler touches it. THE QUESTION THIS RUNG ANSWERS IS WHETHER 12 "
        "DENOISING STEPS MAKE THAT MASS READ AS FOLIAGE OR AS A PADDLE. Both answers "
        "are worth having and neither is a drawing bug to be fixed by a fourth "
        "composite: at this framing there is no room for a tall plant to have wide "
        "leaves, and if the sampler cannot rescue the overlap then the real answer to "
        "the card is that a taller plant costs the leaf silhouette."),
    "C8_THE_ONE_VARIABLE": (
        "THE PLANT READS AS A PLANT AND AS DRAWN CEL ART IN THIS FRAME'S OWN DIALECT. "
        "Same clause as the parent's C8 and same tell: if the sampler converts the "
        "composite into the frame's own line quality this passes; if it leaves a flat "
        "decal, or deletes the plant into the background it so closely matches in "
        "colour, it fails. THE GROUND HAS CHANGED AND THE PARENT'S PASS DOES NOT "
        "TRANSFER FOR FREE. The parent's plant sat on grass over 4.10 percent of the "
        "frame; this one is 7.97 percent and its upper two thirds sit against bright "
        "sky-lit backdrop and the frame's own background foliage, including the sprig "
        "at the top right. More area, a brighter and busier ground, and a subject "
        "whose silhouette is now competing with real leaves rather than grass blades. "
        "The parent measured highpass sigma-3 std inside the mask 17.05 -> 15.84 "
        "(0.93x) on its pass; that ratio is a FILTER to print beside the picture, not "
        "the verdict."),
    "how_scored": (
        "By eye at 1x and 3x on the plant region and on his face, against the "
        "committed composite side by side, and against the clauses above and nothing "
        "else. A metric is a filter, never a verdict -- and on this beat that is not a "
        "slogan: G8's numeric instrument passed hugely on the very clip it was written "
        "to reject, and the b13 skin probe's f000 baseline had to be retracted and "
        "re-placed by hand. Numbers printed beside this frame are printed as numbers."),
}

FAILS = {
    "FAIL-BLADES-READ-AS-ONE-LOBED-MASS": (
        "THE MOST LIKELY FAILURE ON THIS INIT AND IT IS NAMED FIRST. The two blades "
        "overlap in the composite by construction -- the 248 px corridor between the "
        "frame edge at x 2 and his face box at x 250 forced +-70 deg, and at +-70 deg "
        "they are near-vertical and cross. If 12 denoising steps merge them into one "
        "lobed organ, P1's count is one and P1 FAILS. The finding would be that a "
        "plant tall enough to reach his eye line cannot keep its two-leaf silhouette "
        "at this framing, which is a real answer to the card and not a bug to be "
        "fixed by a fourth composite."),
    "FAIL-LOLLIPOP": (
        "THE STEM READS AS A MANUFACTURED OBJECT RATHER THAN AS A PLANT. 921 px tall, "
        "26 px wide, dead straight, with a lobed head at the top: that is also the "
        "silhouette of a lollipop, a balloon on a stick, a wire, a spoon, a fly "
        "swatter, a road sign or a microphone, and SDXL has strong priors for every "
        "one of them. The tell is the JOIN and the BASE -- a plant's stem tapers, "
        "bends under the weight of its own head and roots into the grass; a lollipop's "
        "does none of those. The parent's own pass note records the sampler ADDING a "
        "taper and a rooted base the composite did not draw, so this is the clause "
        "where that behaviour either repeats at four times the length or does not. "
        "P2 FAILS if a reader cannot call it a plant."),
    "FAIL-PLANT-DISSOLVES": (
        "The sampler erases the plant back into the background. Named first on the "
        "parent and it did not fire there; it is named again because THE GROUND IS "
        "DIFFERENT, not because the parent's pass makes it unlikely. The plant's upper "
        "two thirds now overlap real background foliage of similar hue rather than "
        "grass, and the mask is nearly twice the area, so there is more surface over "
        "which the model can decide the region is backdrop. If it dissolves, the "
        "finding is that 0.30 is too low HERE -- the next rung would be a strength "
        "step on this init, not a fourth wording and not a fourth composite."),
    "FAIL-FIGURE": (
        "His folded pose, his knees, his arms, his face or his skull drift. THE MASK "
        "DOES NOT COVER HIS FACE and the composite changed 0 px outside the drawn "
        "footprint with face-box maxdiff 0, so he arrives byte-identical to the r1s1 "
        "plate and any readable change is the sampler's alone. This is the clause the "
        "card cares about second-most: if answering B costs the performance, the "
        "author needs to know that when he rules."),
    "FAIL-MASK-HALO": (
        "A visible seam, rectangle or brightness step along the padding_mask_crop "
        "boundary. NAMED BECAUSE THE AREA DOUBLED: pad-crop 64 crops the masked region "
        "with padding, upscales it to pipeline resolution, inpaints and pastes back, "
        "and the paste boundary now runs the full height of the frame instead of "
        "sitting low in the grass. HF's own documentation warns that this latent-blend "
        "branch is 'why you can see the mask outline'. The parent's boundary was short "
        "and in texture; this one crosses his shoulder line and open backdrop, where a "
        "seam would be obvious."),
    "FAIL-SCALE-INVERSION": (
        "The plant comes back reading as a NEAR-CAMERA weed or a DISTANT tree rather "
        "than as a tall plant beside him at his own depth. This is r1s1's original "
        "recorded fault -- 'the scale reads as big foliage overhead' -- returning "
        "through the door this rung deliberately opened, and it is the specific way "
        "answer B can fail while still looking like a competent frame."),
    "FAIL-COUNT": (
        "A leaf count other than exactly two on the foreground plant, or a second "
        "stalk, by any route other than the blade merge FAIL-BLADES-READ-AS-ONE names "
        "-- the model adding leaflets, a bud or a flower up the length of a stem four "
        "times longer than the parent's. CLASS A. The negative carries three leaves, "
        "four leaves, many leaves, leaflets, extra stalk, multi-node weed, branching "
        "stem, bud, flower, and it is 72 of 77 tokens, so it is defended but not "
        "cheap to extend."),
    "FAIL-DECAL": (
        "Pattern 5's tells: shading that ignores the frame's light axis (measured "
        "(0.15, -0.988) off the rim arc over his skull); an edge stopping short of or "
        "overrunning the object's own; detail at the wrong scale against his hands as "
        "an in-frame ruler. The composite renormalised its shade against the ambient "
        "level where the plant is ROOTED rather than over its whole 921 px footprint, "
        "so the drawn gradient is already correct at the base and weakest at the top "
        "-- the top is where a decal would show."),
    "FAIL-TWO-PLANTS-READ-AS-ONE": (
        "The background sprig at x 660..832 y 80..270 and the drawn sapling read as "
        "one object or as a pair of equals. The drawn plant is 0 px inside that box, "
        "but this risk GREW with the plant: at the parent's height the two were at "
        "opposite corners, and at 921 px the sapling's crown (y 199) is now at the "
        "same height in frame as the sprig. Two plants at the same eye level on "
        "opposite sides of his head is a composition the card should see named."),
}

ONE_VARIABLE = (
    "THE INIT, AND ITS MASK, AND NOTHING ELSE. Model, prompt file, negative file, "
    "steps 40, cfg 7.5, strength 0.30, padding_mask_crop 64, blur 8 and seed 20260820 "
    "are the sapcomp parent's, carried by pipeline/derive_spec.py's allow-list rather "
    "than retyped. The init changes from 13-the-shade-sapcomp-0820.png (canon-height "
    "plant, crown at his knee line, mask 41497 px / 4.10 percent) to "
    "13-the-shade-tallcomp-0820.png (~48.7 cm plant, crown at y 199, mask 80592 px / "
    "7.97 percent). Both composites came off the SAME plate, "
    "farm-out/ep2-b13-mac-plate-0819/13-the-shade-mac-plate-r1s1.png sha 9ae127d1..., "
    "from the SAME tool in the same $0 Mac-side family, so the comparison between this "
    "frame and the parent's is a controlled one.")

NOT_DONE = (
    "NO WORDING CHANGE: prompt.txt and negative.txt are the parent's bytes. The "
    "negative measures 72 of 77 CLIP tokens on animagine's own vocab and the positive "
    "64 of 77, so an added word drops the tail silently -- and 'a tiny sapling' stays "
    "in the positive even though this plant is not tiny, BECAUSE CHANGING IT WOULD BE "
    "A SECOND VARIABLE. If the plant comes back reading small or the wording is judged "
    "to be fighting the init, that is a finding for the NEXT rung and it is written "
    "here in advance so it cannot be claimed afterwards as a foreseen fix. NO SEED "
    "CHANGE: 20260820, the parent's. NO STRENGTH SWEEP: one sample, one seed, one "
    "variable -- a sweep is what you file if 0.30 fails, not what you fire alongside "
    "it. NO SECOND COMPOSITE at a different height or lean: the sidecar states the "
    "geometry is the steward's and is offered as ONE legible instance of 'taller', and "
    "a second instance would ask the author two questions where the card asks one. NO "
    "CANON EDIT: pipeline/canon.yaml still says the sapling is ~40 cm and shorter than "
    "he is, and it stays that way unless the author rules otherwise, at which point "
    "the exception is written in AS an exception. NO REVIEW CARD EDIT FROM THIS LANE.")

INIT_PROV = (
    "pipeline/beat13_shade_composite.py --founder-option -- $0, no GPU, no network, no "
    "sampler. Drawn on the Mac over "
    "farm-out/ep2-b13-mac-plate-0819/13-the-shade-mac-plate-r1s1.png (sha 9ae127d1b693"
    "5f1224a22100a8390f0dc4e12db7385bea48c93da4f039864f07), the plate this beat's r1s1 "
    "produced on 2026-08-19; the tool refuses on a plate sha mismatch before it reads "
    "a pixel. Committed at farm-out/ep2-b13-tallcomp-0820/13-the-shade-tallcomp-0820."
    "png, sha " + INIT_SHA + ", with its own .meta.yaml beside it. THE CHECKS THAT "
    "STAYED ARMED AND PASSED: C1 outside-footprint 0 px; C2 face-box maxdiff 0; C3 "
    "whole plant in frame; C6 one drawn component; C8 0 px in the background sprig; C9 "
    "darkest drawn luma 24 against the plate's own 23. TWO CHECKS WERE LIFTED AND BOTH "
    "ARE PRINTED RATHER THAN HIDDEN: C7_NO_DRAW_ABOVE_Y (37224 drawn px above y=640, "
    "where the default build requires 0 -- that guard IS the refusal the author is "
    "being asked to override, and zero of those px are inside his face box) and "
    "C4_crown_at_knee_line (crown y 199 against knee line y 595, reported not scored, "
    "because a plant clearing his knee line is what answer B asks for). The default "
    "code path was re-verified untouched: it still reproduces 9ae127d1... byte for "
    "byte, which matters because ep2-b13-sapcomp-0820.yaml asserts that sha before it "
    "loads a model.")

MASK_PROV = (
    "Written by the same tool in the same run; sha " + MASK_SHA + ", 80592 white px, "
    "7.97 percent of the 832x1216 frame, against the sapcomp parent's 41497 px and "
    "4.10 percent. It is the DRAWN PLANT'S FOOTPRINT dilated, and on this composite "
    "that is the honest fit rather than a convenient one: the build is purely additive "
    "-- there was no wrong plant to erase, so there are no vacancies to include, which "
    "is the case beat 03's mask had and this one does not. THE AREA DOUBLING IS ITSELF "
    "A PRE-REGISTERED RISK and is carried in C8 and FAIL-MASK-HALO rather than "
    "mentioned only here. The mask geometry is the STEWARD'S, not the author's: he is "
    "being asked about a height, and 'lower', 'shorter', 'other side' remains one "
    "number and one re-draw at $0.")

NEGATIVE_ORDERING = (
    "UNCHANGED FROM THE PARENT AND DELIBERATELY SO. Measured with "
    "pipeline/clip_token_count.py on animagine's own vocab: prompt 64 of 77, negative "
    "72 of 77. The defect class (three leaves, four leaves, many leaves, leaflets, "
    "extra stalk, multi-node weed, branching stem) is first on purpose; `dark, night` "
    "sits late on purpose and is kept because it is in DRAFTS[13]'s own negative and "
    "this rung is not the one trying to fix the exposure. WITH 5 TOKENS OF HEADROOM "
    "THERE IS NO ROOM TO ADD A `lollipop` OR `signpost` TERM AGAINST "
    "FAIL-LOLLIPOP, and that is stated rather than quietly skipped: a term added at "
    "the tail of a 72-token negative is not reliably read, and dropping a leaf-count "
    "term to make room would trade the CLASS A defect for a speculative one. If "
    "FAIL-LOLLIPOP fires, the repair is a mask or geometry change on the next rung, "
    "not a word squeezed into this one.")

IS_SHOW_WHY = (
    "CARD EVIDENCE, NOT A CUT INIT, AND PASSING A BAR IS NOT A LICENCE TO ENTER A CUT. "
    "This frame builds a shot canon forbids. Canon says the sapling is ~40 cm and "
    "always shorter than he is, in every beat of 002b (node.md:181-187; founder "
    "2026-08-16, 'thats ridiculous, lmao. the sapling is tiny'). The plant here is "
    "~48.7 cm and its blades are at his eye line. It exists for exactly one purpose: "
    "to sit on /review/ep2-b13-shade-0820 as the drawn half of answer B so the author "
    "can rule on a picture instead of on a description. NO CLIP, NO EPISODE AND NO "
    "PUBLICATION MAY BE BUILT ON IT, and a PASS on every clause below changes none of "
    "that -- a bar measures whether the sampler did its job, and whether this shot may "
    "exist at all is a taste call reserved to the author (R4). Canon is unchanged "
    "unless and until he rules 'draw it taller', at which point the exception goes "
    "into pipeline/canon.yaml AS an exception so it cannot drift into the other beats.")


def main() -> int:
    child = derive_spec.derive(
        src=PARENT,
        new_id=NEW_ID,
        fresh={
            "why": WHY,
            "consumer": CONSUMER,
            "success": SUCCESS,
            "owner": ("beat 13 tallcomp lane, 2026-08-20 -- derived by "
                      "pipeline/derive_b13_tallcomp_0820.py"),
        },
        overrides={
            "payload:fetch_init.py": FETCH,
            "argv:--init-sha256": INIT_SHA,
            "key:est_minutes": 6,
        },
        # One pair does the whole job: `sapcomp` appears in the box directory,
        # both composite filenames, both output filenames, the courier path, the
        # manifest name and the job id, and NOWHERE ELSE. It is deliberately not
        # `sapling` -- the prompt says "a tiny sapling" and those bytes must not
        # move.
        retoken=[("sapcomp", "tallcomp")],
        extra={
            "is_show_content": False,
            "is_show_content_why": IS_SHOW_WHY,
            "the_one_variable": ONE_VARIABLE,
            "init_provenance": INIT_PROV,
            "mask_provenance": MASK_PROV,
            "bar": BAR,
            "pre_registered_fail_modes": FAILS,
            "negative_ordering": NEGATIVE_ORDERING,
            "not_done_on_purpose": NOT_DONE,
        },
        by="pipeline/derive_b13_tallcomp_0820.py",
    )

    # ---- The two --note strings are per-step, and `argv:--note` would write the
    # ---- same sentence into both. Patched here by hand, each asserted against
    # ---- the parent text it replaces so a renamed or reordered step cannot make
    # ---- this silently a no-op.
    wants = {"dry": ("mask geometry check.", DRY_NOTE),
             "s20260820": ("ONE SAMPLE, ONE SEED.", SAMPLE_NOTE)}
    patched = []
    for step in child["steps"]:
        want = wants.get(step.get("name"))
        if not want:
            continue
        prefix, new = want
        argv = step["argv"]
        i = argv.index("--note")
        if not argv[i + 1].startswith(prefix):
            raise SystemExit("!! step %r --note does not start with %r -- refusing "
                             "to overwrite a note I cannot identify."
                             % (step["name"], prefix))
        argv[i + 1] = new
        patched.append(step["name"])
    if sorted(patched) != ["dry", "s20260820"]:
        raise SystemExit("!! expected to patch the dry and s20260820 notes, patched %s"
                         % (patched or "nothing"))

    # ---- Belt and braces on the one variable. Checked STRUCTURALLY, on the
    # ---- argv and the payload, rather than by scanning the serialised text: the
    # ---- parent's sha legitimately appears in prose (it is the plate both
    # ---- composites were drawn over) and in derivation.overrides_applied, which
    # ---- is the record OF the substitution. A string scan flags both and proves
    # ---- nothing about what the box will actually execute.
    STALE_INIT = "9ae127d1b6935f1224a22100a8390f0dc4e12db7385bea48c93da4f039864f07"
    STALE_MASK = "702ce6b0cb0584ae6ac0080b85b317d9afd2333fdf0102bf17d6dfc9696d013e"

    asserted = []
    for step in child["steps"]:
        argv = step.get("argv") or []
        if "--init-sha256" not in argv:
            continue
        asserted.append((step["name"], argv[argv.index("--init-sha256") + 1]))
    assert len(asserted) == 2, "expected --init-sha256 on 2 steps, got %s" % asserted
    for name, sha in asserted:
        assert sha == INIT_SHA, "step %r still asserts %s" % (name, sha)

    fetch = [v for k, v in child["payload"].items() if k.endswith("fetch_init.py")]
    assert len(fetch) == 1, "expected exactly one fetch_init.py payload"
    assert INIT_SHA in fetch[0] and MASK_SHA in fetch[0], "fetch lost a sha"
    assert STALE_INIT not in fetch[0] and STALE_MASK not in fetch[0], (
        "fetch_init.py still names the parent's composite or mask")
    assert STALE_MASK not in derive_spec._dump(child), (
        "the parent's MASK sha survives somewhere in the child")

    path = derive_spec.write(child, OUT)
    print("WROTE %s" % path)
    print("dropped from the SCORED parent: %s"
          % child["derivation"]["keys_the_parent_had_that_did_NOT_cross"])
    print("notes patched: %s" % ", ".join(patched))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
