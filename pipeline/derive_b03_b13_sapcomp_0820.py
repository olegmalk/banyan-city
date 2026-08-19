#!/usr/bin/env python3
r"""Derive pipeline/jobs/ep2-b03-sapcomp-0820.yaml and ep2-b13-sapcomp-0820.yaml
FROM ep2-b15-sapcomp-0819.yaml.

WHY A SCRIPT AND NOT TWO TYPED FILES. work-ladder-0819.md's standing rule: "One
variable per rung, and prefer to make that a fact about the file -- derive the
new spec from its parent programmatically rather than retyping it." The parent is
`ep2-b15-sapcomp-0819`, which is itself derived from the scored
`ep2-b19-sapcomp-0819` and has since been FIRED AND JUDGED (it carries its own
`verdict_0819` and a `NOTE_this_spec_is_SCORED`). So the composite-then-inpaint
recipe carried here is not merely proven once, it is proven twice, and "the
recipe is the proven one" is checkable with a diff rather than trusted.

WHY TWO SPECS FROM ONE SCRIPT, AND WHY THAT IS NOT TWO VARIABLES. "One variable
per rung" is about what is asked of the SAMPLER, not about how many files a tool
writes. Beats 03 and 13 are two independent rungs that happen to share every
sampler number; each spec's one variable is its own init. Writing them from one
derivation makes it impossible for the two to drift apart in a way a reader would
have to diff two 500-line files to notice -- which is the failure this repo has
already paid for, when 80 specs in pipeline/jobs/ carried beat 02's success bar
because they were authored by copying one file by hand.

EVERY SAMPLER NUMBER IS THE PARENT'S, BY COPY: 40 steps, cfg 7.5, strength 0.30,
pad-crop 64, blur 8, animagine-xl-3.1 base weights in the SDXL inpaint pipeline,
the whole `inpaint_fruit.py` payload, the env block, the needs, the dry-run-
before-any-model gate and the no-glob publish. What changes per beat is the init,
its mask, the two prompt files, the notes and the bar, because those ARE the beat.

THE SEED MOVES TO 20260820 AND THAT IS DELIBERATE. Both parents ran seed
20260819 on their own inits. Re-using it here would produce a file named
s20260819 for a run that is not that run, and this repo has already published
three b12 takes under one basename because a seed lived in a filename that did
not move. New day, new seed, new step name, new artifact name.

THE DERIVATION GUARD, FIRED ON A PARENT THAT REALLY DOES CARRY A VERDICT. Three
crf-10 specs on 2026-08-19 were derived from their parents INCLUDING the parent's
`verdict` blocks, so a filed job carried a PASS belonging to a different clip.
This script refuses to carry any key matching verdict / pick / sweep / plate_ack
and prints what it dropped. It also refuses to OVERWRITE a child that has since
been scored, because a scored verdict is the only record of what the pixels were.

$0. No model, no network, no GPU. Deterministic.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PARENT = os.path.join(REPO, "pipeline", "jobs", "ep2-b15-sapcomp-0819.yaml")
PARENT_DIR = r"C:\banyan-farm\b15sapcomp-0819"
PARENT_ID = "ep2-b15-sapcomp-0819"
PARENT_INIT = "15-good-listener-sapcomp-0819.png"
PARENT_MASK = "15-good-listener-sapcomp-mask-0819.png"
PARENT_INIT_SHA = "109abc613ff5c6d6a334c9964abaabe121b2e20a10ca1d91d06ff4d79d29e91c"
PARENT_MASK_SHA = "f7933427bba319044058d8712a1574b35ad084768e5807b4f3e060a6ea810fdb"
PARENT_STEM = "b15-sapcomp"
PARENT_SEED = "20260819"
SEED = "20260820"

REFUSE = re.compile(r"verdict|pick|sweep|plate_ack", re.I)

# ---------------------------------------------------------------------------
# THE TWO BEATS. Every string below is either measured (the shas and the mask
# geometry are printed by the compositors and re-asserted here against the files
# on disk) or quoted from the beat's own pre-registered definition.
# ---------------------------------------------------------------------------
BEATS = [
    dict(
        beat=3,
        slug="bad-cover",
        jid="ep2-b03-sapcomp-0820",
        wdir=r"C:\banyan-farm\b03sapcomp-0820",
        stem="b03-sapcomp",
        init="03-bad-cover-sapcomp-0820.png",
        init_sha="7b823832de44cd959e0ab9fb92ac83f645ca0dda983daee3fb366979cdc0d9f7",
        mask="03-bad-cover-sapcomp-mask-0820.png",
        mask_sha="5bd2074189015a87a52e9872bf16d1a21211a4b22ccab3010bfd78ac1ccf3e6c",
        outdir="farm-out/ep2-b03-sapcomp-0820",
        tool="pipeline/beat03_cover_composite.py",
        priority=33,
        # THE PROMPT AGREES WITH THE INIT INSTEAD OF ASKING FOR IT. DRAFTS[3]'s
        # own wording asked for `crouching behind a tiny sapling with two big
        # leaves` and the sampler bound neither the count nor the relation; both
        # are now IN the pixels, and the words only have to not contradict them.
        # His terms stay short but present: padding_mask_crop=64 denoises a crop
        # around the mask bbox (x 67..461, y 533..1173) and his cloak, arm and
        # knee are inside it, so dropping him would leave that slice to the
        # checkpoint's prior. `solo` and `2boys` guard the other direction.
        prompt=(
            "a tiny sapling rooted in the grass, exactly two wide oval leaves with "
            "soft round tips on one thin bare stem, in front of one crouching lean "
            "adult goblin man in a patchwork cloak, solo, far too small to hide "
            "him, sunny grassy field, detailed cinematic anime, masterpiece, best "
            "quality, very aesthetic"),
        # Defect class first: the 77-token CLIP ceiling drops the TAIL silently.
        # These are beat 03's OBSERVED failures -- r1s1 drew a branching stem with
        # six to eight leaflets -- plus the plant-girl block DRAFTS[3] carries,
        # because naming a plant beside a figure summons alraune on this
        # checkpoint and this prompt names one.
        negative=(
            "three leaves, four leaves, many leaves, leaflets, extra stalk, "
            "multi-node weed, branching stem, pointed lance leaves, bud, flower, "
            "large tree, thick branch, forest, plant girl, alraune, 2boys, child, "
            "chibi, standing, text, photorealism, 3d render, low quality"),
        dry_note=(
            "mask geometry check. Writes the mask and exits BEFORE a model is "
            "loaded, so a wrong mask costs seconds instead of a GPU fire. The mask "
            "is the union of the REMOVED WEED's footprint and the DRAWN SAPLING's "
            "own footprint, dilated 12 -- 83000 px, 8.20 percent of the frame, "
            "extent x 67..461 y 533..1173. WHAT TO CHECK ON THE DRY PNG: that it "
            "does not reach his FACE (box x 222..424 y 232..512) or anything above "
            "y=700, because his head, face, chest and the whole of the character "
            "read r1 already passes live there and the compositor asserts 0 px "
            "changed in them. It DOES cover his forearm and thigh, by design: the "
            "drawn plant stands BETWEEN THE CAMERA AND HIM and 13240 drawn px fall "
            "inside his measured torso band. That is the beat, not a defect."),
        render_note=(
            "ONE SAMPLE, ONE SEED. Every sampler number is the parent job's: 40 "
            "steps, cfg 7.5, strength 0.30, pad-crop 64, blur 8, animagine-xl-3.1 "
            "base weights in the SDXL inpaint pipeline. THE ONE VARIABLE IS THE "
            "INIT. 0.30 runs int(40 * 0.30) = 12 of 40 denoising steps from a "
            "latent that still carries the drawn structure, so the high-sigma "
            "steps where global layout is decided never run -- which is why "
            "'finish this structure' succeeds where 'invent this structure' "
            "failed. Beat 03 is the first rung in this family whose blocker is not "
            "only CARDINALITY but a RELATION between two objects: r1s1's own "
            "verdict is 'the seedling sits to his LEFT, beside him, and he is not "
            "behind it'. A relation between a figure the sampler has already "
            "placed and a plant it draws where it likes is not a knob either, so "
            "it is composited too."),
        consumer=(
            "THE EP2 CUT, which carries beat 03 on b03-refire-0814 -- footage drawn "
            "on 08-14 from the ROUND YOUNG GOBLIN the founder ruled against on "
            "08-19, so the beat has no usable plate at all. Last night's r1s1 fixed "
            "the character and its own verdict is 'FAIL on the beat, PASS on the "
            "character'. This is the init that can carry the beat."),
        success=(
            "ONE 832x1216 png, its mask and its provenance sidecar, published into "
            "courier-box. THE BAR IS BEAT 03'S OWN done_when, quoted verbatim from "
            "plate_scratch.py DRAFTS[3] where it was pre-registered before r1 "
            "existed: 'he crouches and the COVER IS COMICALLY INADEQUATE - the "
            "trunk hides a fraction of him and the joke is visible without "
            "dialogue. A crouch that actually conceals him fails the beat.'"),
        why=(
            "Both of r1s1's defects are structural and neither is a knob. The plant "
            "was 'a branching stem with six to eight leaflets, not two leaves' -- "
            "composite-init-pattern.md 1's CLASS A, which beats 15 and 19 each "
            "closed a wording ladder on without moving a single leaf. And the JOKE "
            "is a RELATION: 'he is not behind it, not using it, not attempting to "
            "hide'. pipeline/beat03_cover_composite.py removed the weed whole into "
            "the plate's own field and drew ONE canon two-leaf sapling BETWEEN THE "
            "CAMERA AND HIM at 38.4 cm through the plate's own measured ground "
            "plane, $0 on the Mac, with six rounds rejected by eye first. Ten "
            "pre-registered checks pass and every number is printed."),
        bar={
            "the_definition_this_is_staged_TO": (
                "plate_scratch.py DRAFTS[3].done_when, verbatim: 'he crouches and "
                "the COVER IS COMICALLY INADEQUATE - the trunk hides a fraction of "
                "him and the joke is visible without dialogue. A crouch that "
                "actually conceals him fails the beat.' NOTE the standing conflict "
                "DRAFTS[3] already records: done_when says 'the trunk', and the "
                "founder's 'thats ridiculous, lmao. the sapling is tiny' ruling has "
                "since contradicted it. The cover here is the canon sapling's own "
                "stem, which is not a softening -- it is what makes the cover "
                "comically inadequate."),
            "P1_exactly_one_plant_two_leaves_one_stem": (
                "ONE plant in his half of the frame, TWO blades, ONE thin stem. "
                "Extra stalks, extra leaves, leaflets, a multi-node weed or a bud "
                "at the tip all FAIL. This is the clause r1s1 failed six to eight "
                "leaflets on."),
            "P2_THE_COVER_RELATION_AND_IT_IS_THE_CLAUSE_THIS_RUNG_EXISTS_FOR": (
                "The plant stands BETWEEN THE CAMERA AND HIM and occludes part of "
                "him. Composited: 13240 drawn px fall inside his measured torso "
                "band x 256..733 y 700..1080. A plant merely BESIDE him is the "
                "frame r1s1's verdict already rejected and FAILS."),
            "P3_the_cover_is_COMICALLY_INADEQUATE": (
                "He is plainly visible. 0 drawn px above y=700, so his head, face, "
                "shoulders and chest are wholly unobstructed while the plant covers "
                "a strip of forearm and thigh. A plant that actually conceals him "
                "FAILS."),
            "P4_scale": (
                "38.4 cm through the plate's own ground plane (head 232 px / 23 cm "
                "= 10.09 px/cm at his depth, ground y=1080, far field edge y=500), "
                "inside the 30-50 cm band beat 19 pre-registered for canon's ~40 "
                "cm."),
            "P5_ONE_LEAN_ADULT_GOBLIN": (
                "r1s1's character read is the term this rung must not spend. Bald "
                "long green skull, adult face, patchwork poncho, kneeling. The "
                "compositor asserts 0 px changed outside its own footprint and 0 "
                "maxdiff over his face box, so any drift here is the SAMPLER's and "
                "is a FAIL of this rung."),
            "P6_no_second_plant": (
                "The weed is gone whole -- no stub, no node, no attachment point. "
                "Pattern 13: a surviving cue is what the sampler grows a leaflet "
                "back onto, and beat 01 lost a rung to exactly that."),
            "P7_outdoors_sunlit_field": "Bright daylight, open grass, pale sky. No forest, no interior.",
            "C8_THE_ONE_VARIABLE": (
                "THE PLANT READS AS THE CANON TWO-LEAF SAPLING, AS DRAWN CEL ART, "
                "AND IN FRONT OF HIM. Exactly two blades on one stem, in the "
                "plate's dialect -- a mid-green body, a dark cel outline, a "
                "luminance-ridge midrib and no photoreal detail. If the sampler "
                "converts the composite into the frame's own line quality this "
                "passes; if it leaves a flat decal, or deletes the plant, it fails "
                "and the finding is that 0.30 is too low for a plant drawn over a "
                "figure rather than over field."),
            "how_scored": (
                "By eye at 1x and 3x on the plant region, against the committed "
                "composite side by side, and against the done_when above and "
                "nothing else. A metric is a filter, never a verdict."),
            "numeric_filters": (
                "green blade blobs >=250 px in the plant zone; BLADE count by eye "
                "(the two blades and the stem read as ONE component where they "
                "touch, so 1-3 components are expected); blade aspect against "
                "composite-init-pattern.md 8's pre-registered 1.6-2.6 band "
                "(composite: 1.73 and 1.75); px changed outside the mask "
                "(composite: 0 against the parent plate); highpass std inside the "
                "drawn region in -> out, because pattern 7's PASS tell is a "
                "POSITIVE one: 'if you cannot see a difference between your "
                "composite and the output, the pass is a paste.'"),
        },
        authority=(
            "Node 002b-first-citizen, approved_by: founder. THIS PRODUCES A PLATE, "
            "NOT AN EPISODE: STEWARDSHIP 6 gates voice, footage and assembly, and a "
            "still init for an approved beat is none of those. inpaint_fruit.py "
            "writes approved: false and a provisional: block into its own sidecar, "
            "so nothing here can be mistaken for a pick or a plate_ack. The "
            "STAGING this is drawn to is beat 03's own done_when, which has never "
            "been revised; the `trunk` wording inside it is superseded by the "
            "founder's `the sapling is tiny`, and that conflict is quoted in the "
            "bar rather than silently resolved."),
        negative_ordering=(
            "THE DEFECT CLASS IS FIRST ON PURPOSE, AND THE CEILING IS MEASURED "
            "RATHER THAN ESTIMATED. composite-init-pattern.md 4: animagine's budget "
            "is 77 CLIP tokens and any word added silently drops the TAIL, which is "
            "where `text, photorealism, 3d render, low quality` live. Measured with "
            "pipeline/clip_token_count.py on animagine's own vocab, not counted in "
            "words: prompt 65 of 77, negative 68 of 77. The leaflet and branching-"
            "stem terms lead because they are r1s1's OBSERVED defect, and the "
            "plant-girl block is carried from DRAFTS[3]'s own negative because "
            "naming a plant beside a figure summons alraune on this checkpoint."),
        fail_modes={
            "FAIL-COUNT": (
                "a leaf count other than exactly two, or a second stalk, or the "
                "leaflets coming back. r1s1 drew six to eight of them and this is "
                "CLASS A, so it is the clause the composite exists for."),
            "FAIL-NO-COVER": (
                "the plant ends up beside him rather than in front of him, or stops "
                "occluding him. That is the frame r1s1's verdict already rejected, "
                "and it is reachable here in a way it is not on beats 15 and 19: "
                "the mask covers a strip of HIM, so a 0.30 pass could in principle "
                "resolve the overlap the other way and paint his thigh over the "
                "plant."),
            "FAIL-FIGURE": (
                "his face, his skull, his poncho or his kneel drift. 0 px of him "
                "change going in and the face box is byte-identical, so any drift "
                "is the sampler's. Named because the mask DOES touch him."),
            "FAIL-WEED-RETURNS": (
                "a leaflet or a stub grows back in the cleared region. Pattern 13's "
                "law -- an emptied region is filled with whatever the surviving cue "
                "suggests -- and beat 01 lost a rung to it. The weed was removed "
                "whole precisely so there is no cue left."),
            "FAIL-DECAL": (
                "any of pattern 5's tells: shading ignoring the frame's light "
                "(measured straight down, (0.02, -0.9998), from the sun disc rather "
                "than from a low-pass gradient his black trousers dominate); an edge "
                "stopping short of or overrunning the object's own; detail at the "
                "wrong scale against his hand as an in-frame ruler."),
            "FAIL-SMEAR": (
                "the erased vacancy resolves as fog or as a flat patch instead of "
                "as grass. The fill is per-row interpolation and asserts NO texture "
                "it cannot see, so the blade structure inside the vacancy is "
                "entirely the sampler's to supply. This is the honest risk of the "
                "removal method and it is named before the fire, not after."),
        },
        flagged=(
            "WHAT THIS RUNG DOES NOT FIX, so nobody scores it as passed. r1s1's "
            "verdict also reads 'He reads RESIGNED, not caught out.' That is his "
            "EXPRESSION and his POSE and no composite reaches either. This rung "
            "supplies the size-and-position relation only; whether a resigned kneel "
            "sells `dives` is a second variable belonging to the pose/motion lane."),
    ),
    dict(
        beat=13,
        slug="the-shade",
        jid="ep2-b13-sapcomp-0820",
        wdir=r"C:\banyan-farm\b13sapcomp-0820",
        stem="b13-sapcomp",
        init="13-the-shade-sapcomp-0820.png",
        init_sha="9ae127d1b6935f1224a22100a8390f0dc4e12db7385bea48c93da4f039864f07",
        mask="13-the-shade-sapcomp-mask-0820.png",
        mask_sha="702ce6b0cb0584ae6ac0080b85b317d9afd2333fdf0102bf17d6dfc9696d013e",
        outdir="farm-out/ep2-b13-sapcomp-0820",
        tool="pipeline/beat13_shade_composite.py",
        priority=33,
        prompt=(
            "a tiny sapling rooted in the grass, exactly two wide oval leaves with "
            "soft round tips on one thin bare stem, beside one lean adult goblin man "
            "sitting folded small with his knees drawn up, solo, patchwork cloak, "
            "grassy field, warm afternoon light, detailed cinematic anime, "
            "masterpiece, best quality, very aesthetic"),
        negative=(
            "three leaves, four leaves, many leaves, leaflets, extra stalk, "
            "multi-node weed, branching stem, pointed lance leaves, bud, flower, "
            "large tree, thick branch, forest, plant girl, alraune, 2boys, child, "
            "chibi, standing, text, photorealism, 3d render, dark, night, low quality"),
        dry_note=(
            "mask geometry check. Writes the mask and exits BEFORE a model is "
            "loaded, so a wrong mask costs seconds instead of a GPU fire. THIS "
            "COMPOSITE IS PURELY ADDITIVE -- there was no wrong plant near him to "
            "remove -- so the mask is the DRAWN SAPLING's footprint alone, dilated "
            "12: 41497 px, 4.10 percent of the frame, extent x 13..252 y 647..1174. "
            "WHAT TO CHECK ON THE DRY PNG: that it does not reach his FACE (box x "
            "250..570 y 60..500), his hands or his folded arms -- 0 drawn px sit "
            "above y=640 and the compositor asserts 0 px changed anywhere outside "
            "its own footprint, so PASS on cast and on pose is byte-identical to "
            "r1s1 going in. 192 drawn px fall inside his declared leg band; that is "
            "a foreground blade crossing his shin and is what tells a reader the "
            "plant is nearer to camera than his leg."),
        render_note=(
            "ONE SAMPLE, ONE SEED. Every sampler number is the parent job's: 40 "
            "steps, cfg 7.5, strength 0.30, pad-crop 64, blur 8, animagine-xl-3.1 "
            "base weights in the SDXL inpaint pipeline. THE ONE VARIABLE IS THE "
            "INIT. 0.30 runs int(40 * 0.30) = 12 of 40 denoising steps from a "
            "latent that still carries the drawn structure. Beat 13's r1s1 is the "
            "only plate of last night's three whose ACTION clause landed -- folded "
            "small, knees up -- and its single fault is that 'in the thin shade of "
            "a tiny sapling' bought shade and lost the plant. Its own verdict names "
            "this route: 'If the plant is solved compositionally, this pose is "
            "worth keeping.'"),
        consumer=(
            "THE EP2 CUT, which carries beat 13 on b13-refire-0814 and is C-group. "
            "Last night's r1s1 is the best plate this beat has ever had and it is "
            "unusable for one reason: there is no identifiable sapling in it. This "
            "is the init that keeps that pose and gives it the plant."),
        success=(
            "ONE 832x1216 png, its mask and its provenance sidecar, published into "
            "courier-box. THE BAR IS BEAT 13'S OWN done_when, quoted verbatim from "
            "plate_scratch.py DRAFTS[13]: 'he ends FOLDED SMALL in the sapling's "
            "shade, knees up.' The SCRIPT CONFLICT that definition flags -- the "
            "script says 'slides down the trunk' and the founder has ruled the "
            "sapling is tiny, so there is no trunk to slide down -- is left OPEN "
            "here exactly as DRAFTS[13] leaves it. This is a still of the END "
            "STATE; how he gets there is an author call, not a steward one."),
        why=(
            "The plant is DRAWN rather than asked for, and this plate makes the "
            "cleanest possible version of that claim: there was nothing to erase, "
            "so the tool is additive only and 'his pose and cast are untouched' is "
            "arithmetic rather than a claim -- 0 px changed outside the drawn "
            "footprint. pipeline/beat13_shade_composite.py drew one canon two-leaf "
            "sapling beside him with its crown at his measured knee line, $0 on the "
            "Mac, with three rounds rejected by eye first. Nine pre-registered "
            "checks pass."),
        bar={
            "the_definition_this_is_staged_TO": (
                "plate_scratch.py DRAFTS[13].done_when, verbatim: 'he ends FOLDED "
                "SMALL in the sapling's shade, knees up. SCRIPT CONFLICT, flagged "
                "not solved: the script says `slides down the trunk`, and the "
                "founder has ruled the sapling is tiny - `thats ridiculous, lmao. "
                "the sapling is tiny` - so there is no trunk to slide down. The END "
                "STATE is what the beat needs; how he gets there is an author call, "
                "not a steward one.'"),
            "P1_exactly_one_plant_two_leaves_one_stem": (
                "ONE foreground plant, TWO blades, ONE thin stem. SCOPE, STATED "
                "BEFORE SCORING: this clause is about the FOREGROUND SAPLING. A "
                "second, multi-leaflet background sprig sits at x 660..832 y 80..270 "
                "and is deliberately NOT removed -- it is distant scrub, removing it "
                "is a second variable, and its bbox is recorded here so nobody reads "
                "this clause as 'exactly two leaves in frame'."),
            "P2_THE_PLANT_EXISTS_AND_IS_IDENTIFIABLE_AND_IT_IS_THE_CLAUSE_THIS_RUNG_EXISTS_FOR": (
                "A reader can point at the sapling. r1s1's whole fault was 'NO "
                "IDENTIFIABLE SAPLING ... the scale reads as big foliage overhead, "
                "not a 40 cm plant'. Out-of-focus foliage standing in for the plant "
                "FAILS."),
            "P3_BESIDE_HIM_AT_KNEE_HEIGHT": (
                "He sits at the base of the stem and the plant is beside him with "
                "its crown at his knee line. Composited: crown y=659 against his "
                "measured knee-top line y=595, 64 px below it, band +-70."),
            "P4_scale_REPORTED_NOT_SCORED_AND_HERE_IS_WHY": (
                "25.9 cm at his depth, and that number is NOT a pass/fail clause on "
                "this plate. Beats 03 and 19 size their plant through a measured "
                "ground plane; this is a tight portrait with NO HORIZON IN FRAME, so "
                "there is nothing to build a plane from. The only handle is his head "
                "(435 px / 23 cm = 18.91 px/cm) and it gives two answers that "
                "disagree: 25.9 cm for the drawn plant, versus a 40 cm plant at his "
                "exact depth being 757 px with its crown at his BROW -- which is not "
                "'beside him at knee height' by any reading. His seated mass is 2.5 "
                "head-heights where a real adult hugging his knees is about 4, so "
                "the head-derived rate overstates centimetres here. The SCORED "
                "clause is therefore P3's relation, and this number is printed "
                "beside it rather than converted into a pass."),
            "P5_FOLDED_SMALL_KNEES_UP_ONE_LEAN_ADULT_GOBLIN": (
                "The terms r1s1 already passes: seated, knees drawn to the chest, "
                "arms wrapped over them, shoulders in, bald green adult. The "
                "compositor asserts 0 px changed outside the drawn footprint and 0 "
                "maxdiff over his face box, so any drift here is the SAMPLER's and "
                "is a FAIL of this rung."),
            "P6_thin_shade": (
                "The plant casts or sits in thin shade rather than deep gloom. "
                "r1s1's second recorded fault is that it is DIM -- 'a green gloom "
                "with dark, night sitting in the negative' -- and that fault is "
                "CARRIED, not fixed, by this rung. Recorded so it is not re-scored "
                "as this rung's failure."),
            "C8_THE_ONE_VARIABLE": (
                "THE PLANT READS AS THE CANON TWO-LEAF SAPLING AND AS DRAWN CEL "
                "ART. If the sampler converts the composite into the frame's own "
                "line quality this passes; if it leaves a flat decal, or deletes "
                "the plant into the background foliage it so closely matches in "
                "colour, it fails -- and THAT is the finding worth having, because "
                "this is the lowest-contrast field any composite in this house has "
                "been dropped onto."),
            "how_scored": (
                "By eye at 1x and 3x on the plant region, against the committed "
                "composite side by side, and against the done_when above and "
                "nothing else. A metric is a filter, never a verdict."),
            "numeric_filters": (
                "drawn components >=250 px (composite: 1 -- the plant is ONE "
                "object); blade aspect against composite-init-pattern.md 8's "
                "pre-registered 1.6-2.6 band (composite: 1.71 and 1.72); px changed "
                "outside the mask (composite: 0 against the parent plate); highpass "
                "std inside the drawn region in -> out (pattern 7: relocation, not "
                "engagement, is the pass tell)."),
        },
        authority=(
            "Node 002b-first-citizen, approved_by: founder. THIS PRODUCES A PLATE, "
            "NOT AN EPISODE: STEWARDSHIP 6 gates voice, footage and assembly, and a "
            "still init for an approved beat is none of those. inpaint_fruit.py "
            "writes approved: false and a provisional: block into its own sidecar. "
            "The SCRIPT CONFLICT inside beat 13's own done_when -- `slides down the "
            "trunk` against a tiny sapling -- is left open here exactly as "
            "DRAFTS[13] leaves it. This still is the END STATE only; drawing the "
            "slide would be making an author's call silently, which is the class of "
            "thing that put an unratified goblin on screen for four days."),
        negative_ordering=(
            "THE DEFECT CLASS IS FIRST ON PURPOSE, AND THE CEILING IS MEASURED "
            "RATHER THAN ESTIMATED. Measured with pipeline/clip_token_count.py on "
            "animagine's own vocab: prompt 64 of 77, negative 72 of 77. `dark, "
            "night` is kept and sits late on purpose: it is in DRAFTS[13]'s own "
            "negative, r1s1 came back DIM anyway, and this rung is not the one "
            "trying to fix the exposure -- dropping the terms would change a second "
            "variable, and moving them to the front would spend budget the leaf "
            "count needs."),
        fail_modes={
            "FAIL-COUNT": (
                "a leaf count other than exactly two on the foreground plant, or a "
                "second stalk. CLASS A, and the clause the composite exists for."),
            "FAIL-PLANT-DISSOLVES": (
                "the sampler erases the plant back into the background foliage. THIS "
                "IS THE MOST LIKELY FAILURE ON THIS PLATE and it is named first "
                "among the risks: the drawn plant's own colours were sampled from "
                "this frame, and this frame is green foliage edge to edge, so the "
                "contrast between object and ground is the lowest any composite in "
                "this house has been dropped onto. If it dissolves, the finding is "
                "that 0.30 is too low HERE and the next rung is a strength sweep, "
                "not a fourth wording."),
            "FAIL-FIGURE": (
                "his folded pose, his knees, his arms, his face or his skull drift. "
                "0 px of him change going in -- this composite is additive and "
                "touches nothing outside the plant -- so any drift is the "
                "sampler's. PASS on cast and on pose is r1s1's and is not this "
                "rung's to spend."),
            "FAIL-SCALE": (
                "the plant comes back reading as big foliage overhead rather than "
                "as a knee-high seedling, which is r1s1's own recorded fault "
                "returning through a different door."),
            "FAIL-DECAL": (
                "any of pattern 5's tells: shading ignoring the frame's light "
                "(set to (0.15, -0.988) from the rim arc over his skull, because "
                "the low-pass gradient is measuring HIM at this magnification); an "
                "edge stopping short of or overrunning the object's own; detail at "
                "the wrong scale against his hands as an in-frame ruler."),
            "FAIL-TWO-PLANTS-READ-AS-ONE": (
                "the background sprig at x 660..832 y 80..270 and the drawn sapling "
                "read as one object or as a pair of equals. The drawn plant is 0 px "
                "inside that box and they are at opposite corners, but this is "
                "named because leaving the sprig in frame is a declared choice and "
                "declared choices should carry their own risk."),
        },
        flagged=(
            "WHAT THIS RUNG DOES NOT FIX. r1s1's verdict names TWO faults and this "
            "rung addresses one. The second -- 'DIM. A green gloom with dark, night "
            "sitting in the negative ... darker than a sunny field, and it is the "
            "same override the b08 posenet rung measured' -- is a plate-level "
            "exposure problem that a 0.30 pass over 4 percent of the frame cannot "
            "touch. It is carried forward, not solved, and it is not this rung's to "
            "be scored on."),
    ),
]


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def swap(value, pairs):
    if isinstance(value, str):
        for old, new in pairs:
            value = value.replace(old, new)
            value = value.replace(old.replace("\\", "/"), new.replace("\\", "/"))
        return value
    if isinstance(value, list):
        return [swap(v, pairs) for v in value]
    return value


def derive(parent, spec) -> dict:
    out = os.path.join(REPO, "pipeline", "jobs", spec["jid"] + ".yaml")

    # The asserted bytes are asserted HERE too: a spec that names a sha the local
    # artifact does not have is the "stale checkout" failure this repo has paid
    # for once, and refusing it at derivation time costs nothing.
    for name, want in ((spec["init"], spec["init_sha"]),
                       (spec["mask"], spec["mask_sha"])):
        p = os.path.join(REPO, spec["outdir"], name)
        if not os.path.isfile(p):
            raise SystemExit("!! missing %s -- the init must be committed BEFORE "
                             "the spec that fetches it off origin/main." % p)
        have = sha256_of(p)
        if have != want:
            raise SystemExit("!! SHA MISMATCH for %s\n   want %s\n   have %s"
                             % (p, want, have))

    # The same defect from the opposite direction: a re-run must not silently
    # DELETE a child's own verdict once the pixels have been scored.
    if os.path.isfile(out) and "--force" not in sys.argv:
        existing = yaml.safe_load(open(out, "r", encoding="utf-8")) or {}
        scored = sorted(k for k in existing if REFUSE.search(k))
        if scored:
            raise SystemExit(
                "!! %s already carries %s -- refusing to overwrite a SCORED spec.\n"
                "   Re-deriving would delete the verdict, which is the only record "
                "of what the pixels were.\n   Pass --force if that is genuinely "
                "what you want." % (os.path.relpath(out, REPO), ", ".join(scored)))

    refused = sorted(k for k in parent if REFUSE.search(k))
    child = {k: v for k, v in parent.items() if k not in refused}

    pairs = [
        (PARENT_DIR, spec["wdir"]),
        (PARENT_ID, spec["jid"]),
        (PARENT_INIT, spec["init"]),
        (PARENT_MASK, spec["mask"]),
        (PARENT_INIT_SHA, spec["init_sha"]),
        (PARENT_MASK_SHA, spec["mask_sha"]),
        (PARENT_STEM + "-s" + PARENT_SEED, spec["stem"] + "-s" + SEED),
        (PARENT_STEM, spec["stem"]),
        ("b15sapcomp-0819", os.path.basename(spec["wdir"])),
        ("farm-out/ep2-b15-sapcomp-0819/", spec["outdir"] + "/"),
        ("pipeline/beat15_listener_composite.py", spec["tool"]),
        ("beat 15's SAPLING composite", "beat %02d's SAPLING composite" % spec["beat"]),
        ("banyan-city-b15-sapcomp/1.0", "banyan-city-%s/1.0" % spec["stem"]),
    ]

    child["payload"] = {swap(k, pairs): swap(v, pairs)
                        for k, v in parent["payload"].items()}
    child["payload"][spec["wdir"] + r"\prompt.txt"] = spec["prompt"]
    child["payload"][spec["wdir"] + r"\negative.txt"] = spec["negative"]

    steps = []
    for step in parent["steps"]:
        s = dict(step)
        argv = swap(list(step["argv"]), pairs)
        # THE SEED IS MOVED IN THE ARGV, NOT ONLY IN THE FILENAMES. A filename
        # that says s20260820 over a run that fired 20260819 is the b12
        # duplicate-basename defect with the labels swapped.
        argv = [SEED if a == PARENT_SEED else a for a in argv]
        if s.get("name") == "s" + PARENT_SEED:
            s["name"] = "s" + SEED
        if "--note" in argv:
            argv[argv.index("--note") + 1] = (
                spec["dry_note"] if s["name"] == "dry" else spec["render_note"])
        s["argv"] = argv
        if "note" in s:
            s["note"] = swap(step["note"], pairs)
        steps.append(s)
    child["steps"] = steps
    child["artifacts"] = [
        spec["wdir"] + "\\" + spec["stem"] + "-s" + SEED + ".png",
        spec["wdir"] + "\\" + spec["init"],
    ]

    child["id"] = spec["jid"]
    child["task"] = spec["jid"]
    child["beat"] = spec["beat"]
    child["priority"] = spec["priority"]
    child["est_minutes"] = 5
    child["owner"] = ("beat %02d lane, 2026-08-20 -- derived by "
                      "pipeline/derive_b03_b13_sapcomp_0820.py" % spec["beat"])
    child["consumer"] = spec["consumer"]
    child["success"] = spec["success"]
    child["why"] = spec["why"]
    child["bar"] = spec["bar"]
    # AUTHORED, NEVER SWAPPED. These three keys are beat-15 PROSE in the parent --
    # its approval commit, its token measurement, its named fail modes -- and a
    # path substitution would leave all three saying true things about the wrong
    # beat. That is the exact defect that put beat 02's success bar on 80 specs in
    # pipeline/jobs/. They are re-authored per beat below and the parent's are
    # dropped, not edited.
    child["script_authority"] = spec["authority"]
    child["negative_ordering"] = spec["negative_ordering"]
    child["pre_registered_fail_modes"] = spec["fail_modes"]
    child["what_this_rung_does_NOT_fix"] = spec["flagged"]
    child["init_provenance"] = (
        "%s -- $0, no GPU, no network, no sampler. Drawn on the Mac from "
        "%s/%s (the plate this beat's r1s1 produced on 2026-08-19), sha256 %s. "
        "The tool prints every measured number it uses and refuses on a plate sha "
        "mismatch before it reads a pixel."
        % (spec["tool"], spec["outdir"].replace("sapcomp-0820", "mac-plate-0819"),
           spec["init"].replace("sapcomp-0820", "mac-plate-r1s1"), spec["init_sha"]))
    child["mask_provenance"] = (
        "Written by the same tool in the same run; sha256 %s. It covers the drawn "
        "plant AND, on beat 03, the erased vacancies -- not only what was painted. "
        "A mask fitted to the paint alone makes the result a foregone conclusion "
        "and measures nothing (beat 14's C8)." % spec["mask_sha"])
    child.pop("section_6_is_DISCHARGED_on_this_beat", None)
    child.pop("NOTE_this_spec_is_SCORED", None)
    child.pop("failure_predicted_in_advance", None)
    child["derivation"] = {
        "by": "pipeline/derive_b03_b13_sapcomp_0820.py",
        "parent": PARENT_ID,
        "parent_is_scored": True,
        "carried_structural_keys": sorted(
            k for k in child if k in parent and not REFUSE.search(k)),
        "dropped_from_parent": refused,
        "seed": int(SEED),
        "one_variable": "the init: beat %02d's composite replaces beat 15's"
                        % spec["beat"],
    }


    # A last, dumb, load-bearing check: no string anywhere in the child may still
    # name the parent's beat. The b12 duplicate-basename defect and the 80-spec
    # copied-success-bar defect were both this, caught by nobody.
    # THE `derivation` BLOCK IS EXEMPT AND MUST BE. Naming the parent is its whole
    # job -- a provenance record that cannot say where it came from is not one --
    # so the stale-token scan runs over everything else. This is the difference
    # between "no string names the wrong beat" and "no string names the parent",
    # and only the first is the invariant worth having.
    body = yaml.safe_dump({k: v for k, v in child.items() if k != "derivation"},
                          sort_keys=False, allow_unicode=False)
    for stale in ("b15sapcomp", "b15-sapcomp", "ep2-b15-sapcomp",
                  "15-good-listener", PARENT_INIT_SHA, PARENT_MASK_SHA):
        if stale in body:
            i = body.find(stale)
            raise SystemExit("!! %s still mentions %r after the swap -- refusing "
                             "to file a job that would fetch the wrong beat.\n   "
                             "CONTEXT: ...%s..."
                             % (spec["jid"], stale,
                                body[max(0, i - 200):i + 120].replace("\n", " ")))
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(yaml.safe_dump(child, sort_keys=False, allow_unicode=False))
    print("WROTE %s  (dropped from parent: %s)"
          % (os.path.relpath(out, REPO), ", ".join(refused) or "nothing"))
    return child


def main() -> int:
    parent = yaml.safe_load(open(PARENT, "r", encoding="utf-8"))
    for spec in BEATS:
        derive(parent, spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
