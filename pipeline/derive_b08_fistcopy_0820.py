#!/usr/bin/env python3
"""Derive `ep2-b08-fistcopy-0820` -- §21's copy-the-fist rung, at last fileable.

PARENT IS `ep2-b13-tallcomp-0820` AND THAT IS A SHAPE, NOT AN ANCESTRY. Beat 08
has no inpaint job in its own line: the whole b08 route to date is txt2img +
controlnet, and `ep2-b08-gripcomp-0820` never reached the card at all -- §21
found it was "an INIT plus a MASK. It has never been near the card." So the
parent supplies the composite-init + mask + `inpaint_fruit.py` machinery that
b03/b13/b15/b19 proved, and every beat-08 fact is authored here. `derive_spec`
carries only ALLOW-listed structure, so none of b13's thinking rides along.

WHAT IS DELIBERATELY NOT CHANGED: the prompt and the negative are beat 08's own
scale30 text, BYTE-IDENTICAL. This sample tests the COMPOSITE and nothing else.
§18 measured that grip wording buys a hand and pays for it with the board -- and
that trade does not even apply here, because the board is outside the mask and
the latent blend restores it every step, so the board CANNOT be lost by this
pass. Wording is therefore a lever this rung does not need and does not spend:
one variable.

$0 to run. No model, no network, no GPU -- it writes a yaml.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import derive_spec  # noqa: E402
import beat08_grip_copy as C  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB = "ep2-b08-fistcopy-0820"
SEED = 20260820

INIT = "08-first-citizen-fistcopy-0820.png"
MASK = "08-first-citizen-fistcopy-mask-0820.png"
INIT_SHA = "7cc1a4cb12ca14a3628eb9ba8b8257ccc1f07f7cf9a9727d8ce769e1d5de8d45"
MASK_SHA = "bfee06c5f1bf7ddc895c6c0cd5a26f541e034ed4d3516d9a15a8e2e032d55785"

FETCH = '''#!/usr/bin/env python3
"""Fetch beat 08's FIST-COPY composite and its mask; refuse on any sha mismatch.

No model, no GPU, no spend. Both files are on origin/main -- written by
pipeline/beat08_grip_copy.py on a Mac, so they are NOT on the box's courier
worktree, which only ever contains what the box produced. The sha256s asserted
here are verifiable against the repo by anyone who clones it.

WHAT THE INIT CONTAINS, SO THE OPERATOR IS NOT SURPRISED BY IT: the guard has
TWO left fists. That is not a defect, it is the rung. The plate's own fist is
still at the strap where it was drawn -- inside the mask, for this pass to
delete from real pixels -- and a byte-exact COPY of it sits at the board's top
edge, outside the mask, where its drawn digits are protected by the latent
blend at every step. §21 tried the other order (move the hand, fabricate a fill
for the vacancy) and three fill families all left an artifact an eye names.
"""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\b08fistcopy-0820"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "farm-out/ep2-b08-fistcopy-0820/")
UA = {"User-Agent": "banyan-city-b08-fistcopy/1.0 (albert.numbro@gmail.com)"}
WANT = {
    "%s":
        "%s",
    "%s":
        "%s",
}

os.makedirs(OUT, exist_ok=True)
for name, want in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(RAW + name, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %%s -- refusing.\\n   want %%s\\n   have %%s"
                 %% (name, want, have))
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %%s %%d bytes sha %%s OK" %% (name, len(raw), have), flush=True)
''' % (INIT, INIT_SHA, MASK, MASK_SHA)

DRY_NOTE = (
    "MASK GEOMETRY CHECK. Writes the mask and exits BEFORE a model is loaded, so "
    "a wrong mask costs seconds instead of a GPU fire. THIS MASK IS 18408 px, "
    "1.82 percent of the frame, bbox (548,518)-(691,730). IT IS THREE REGIONS "
    "AND ONE HOLE. (1) the guard's ORIGINAL left fist at the harness strap, "
    "grown 14 px -- the pass DELETES it; (2) the forearm corridor from the "
    "authored elbow (627,580) to the authored wrist (622,668), 24 px half-width "
    "-- the pass DRAWS an arm through it; (3) a 12 px rim around the copied fist "
    "at the board's top edge -- the pass draws CONTACT and occlusion there. THE "
    "HOLE is the copied fist's interior, 2852 px, held OUT of the mask so its "
    "drawn digits survive: they are the one thing in this rung that must not be "
    "re-invented. WHAT TO CHECK ON THE DRY PNG: that the white region does NOT "
    "reach the guard's FACE (box x 531..601 y 355..420), the goblin (x 60..260 "
    "y 430..1140), or the guard's pointing hand (x 255..360 y 640..730) -- all "
    "three are asserted by the compositor's K12 and all three pass -- and that "
    "there is a clearly BLACK island inside the white rim at the board's top "
    "edge. If that island is missing the digits are unprotected and this job "
    "must stop here at $0.")

fresh = {
    "why": (
        "§21 named this rung, refused to file it, and gave two reasons. Both are "
        "now discharged. THE FIRST: 'a 0.30 pass does not delete a hand ... so "
        "the rung has to choose a higher strength inside the mask and that "
        "re-opens the exact clauses (B6, B8, the wardrobe) the 0.30 number was "
        "bought with. That is an argued tradeoff, not a knob turn.' The argument "
        "is written out in pipeline/beat08_grip_copy.py STRENGTH_ARGUMENT and "
        "its load-bearing half is a MEASUREMENT, not a position: those clauses "
        "were bought at the CONDITIONING scale on a whole-frame txt2img render, "
        "and a masked pass cannot write a pixel outside its mask at any "
        "strength, so B8's canon hair is 0 of 18200 px reachable and the gold "
        "clasp is 11 of 994. THE SECOND: 'the instrument that would score its "
        "vacancy has just been shown to certify artifacts at twice its bar.' "
        "That instrument is replaced -- pipeline/fill_quality.py, C4', whose "
        "false-positive rate on this very plate is a measured 3.0%."),
    "consumer": (
        "BEAT 08's PLATE DECISION. The beat has no complete plate candidate: "
        "ep2-b08-scale30-0820 is the best frame and its grip clause fails, and "
        "§21 closed the move-the-hand route with a general rule -- "
        "composite-then-inpaint is licensed where the vacancy's material is "
        "continuous and unstructured, and is NOT a licence to relocate part of a "
        "figure across its own clothing. This sample answers the one question "
        "that rule leaves open: whether the vacancy can be avoided altogether by "
        "copying rather than moving, and letting the sampler delete the original "
        "from real strap pixels. A pass makes beat 08 a plate candidate; a fail "
        "closes the composite route on this beat and sends it back to staging."),
    "success": (
        "ONE 832x1216 PNG plus its sidecar, published into courier-box, off the "
        "asserted init sha. The bar is below and every clause of it was written "
        "before the pixels existed. NOT a pick and NOT a plate_ack: landing is "
        "judged by this lane against the bar, and R4 taste calls are the "
        "founder's."),
    "owner": ("beat 08 arm-route lane, 2026-08-20 -- derived by "
              "pipeline/derive_b08_fistcopy_0820.py, init by "
              "pipeline/beat08_grip_copy.py (selftest PASS, 18 clauses)"),
}

overrides = {
    "key:beat": 8,
    "key:priority": 34,
    "key:est_minutes": 7,
    "argv:--strength": "%.2f" % C.STRENGTH,
    "argv:--init-sha256": INIT_SHA,
    "argv:--seed": str(SEED),
    "argv:--note": DRY_NOTE,
    # `script_authority` IS ON DERIVE_SPEC'S ALLOW LIST, AND ON THIS PARENT IT
    # CARRIES BEAT 13'S OWN SCRIPT CONFLICT VERBATIM ("`slides down the trunk`
    # against a tiny sapling"). Inherited it would be a sentence about another
    # beat's open authoring question standing as this job's authority. The
    # ALLOW list is right that the KEY belongs on a child; the VALUE never
    # does. Caught by grepping the derived yaml for the parent's beat number,
    # which is worth doing after every derivation this tool cannot police.
    "key:script_authority": (
        "Node 002b-first-citizen, approved_by: founder. THIS PRODUCES A PLATE, "
        "NOT AN EPISODE: STEWARDSHIP 6 gates voice, footage and assembly, and a "
        "still init for an approved beat is none of those. inpaint_fruit.py "
        "writes approved: false and a provisional: block into its own sidecar. "
        "Beat 08's script line is 'lowers the clipboard and points' and this "
        "rung touches only the LOWERING hand -- the pointing arm is outside the "
        "mask and byte-restored every step. No authoring call is made here: the "
        "hand that grips is the plate's own drawn fist, translated, so not one "
        "digit is invented."),
    "payload:fetch_init.py": FETCH,
    "payload:prompt.txt": open(os.path.join(
        REPO, "farm-out", "ep2-b08-scale30-0820", "prompt.txt"),
        encoding="utf-8").read(),
    "payload:negative.txt": open(os.path.join(
        REPO, "farm-out", "ep2-b08-scale30-0820", "negative.txt"),
        encoding="utf-8").read(),
}

extra = {
    "sample_declaration": (
        "ONE SAMPLE, one seed, one strength. The founder's 2026-08-03 rule: "
        "before rendering a SET of anything, produce ONE. This is the first "
        "inpaint pass beat 08 has ever filed and the first anywhere in this tree "
        "asked to DELETE a fully-inked object rather than integrate one, so "
        "there is no prior on which side of the deletion threshold it lands."),
    "strength_argument": C.STRENGTH_ARGUMENT,
    "init_provenance": (
        "pipeline/beat08_grip_copy.py --write, selftest PASS on 18 clauses. "
        "init %s sha %s, mask %s sha %s, both on origin/main and fetched by sha. "
        "The init is ep2-b08-scale30-0820's plate (sha 448e40cb...) with a "
        "byte-exact translated COPY of the guard's own fist added at (+18,+91); "
        "3101 of 3101 copied px are identical to the plate's, 0 strokes were "
        "drawn, and the 4489 px §21 could not fill are all still byte-identical "
        "plate because no vacancy was ever opened." % (INIT, INIT_SHA, MASK, MASK_SHA)),
    "bar": {
        "C4prime": (
            "THE CLAUSE THIS RUNG WAITED FOR. Run pipeline/fill_quality.py on "
            "the 7914 px region where the original fist was (published as "
            "08-first-citizen-fistcopy-erase-0820.png): D >= 0.45 AND N >= 0.25 "
            "AND F <= 2.60, against the landed frame with the init as --plate. "
            "The retired C4 would have passed the gripcomp corduroy comb at 89%; "
            "C4' fails it at N 0.084 / F 7.87 and passes every honest composite "
            "fill on b03/b13/b15/b19. Measured false-positive rate 3.0%."),
        "H1_the_fist_is_GONE": (
            "The original fist must be DELETED, not dented. No skin-toned blob "
            "survives inside poly(FIST) grown 6: judged by eye at 5x and by the "
            "absence of a closed light region there. THIS IS THE CLAUSE THE "
            "STRENGTH WAS CHOSEN FOR and the one most likely to fail."),
        "H2_the_arm_CONNECTS": (
            "A forearm runs from the authored elbow (627,580) to the copied "
            "hand at the wrist (621,673) with no gap and no second limb. §21's "
            "'sticker of a hand' verdict is what this clause exists to prevent."),
        "H3_the_digits_SURVIVED": (
            "The copied fist's drawn fingers and thumb are still individually "
            "legible at 5x. They are outside the mask and restored every step by "
            "the latent blend, so this is close to guaranteed -- it is in the bar "
            "because --blur 8 softens the boundary and the outer rim of them does "
            "take a fraction of the pass."),
        "H4_contact_not_decal": (
            "The hand closes around the board's top edge: contact shading or "
            "occlusion is visible where fingers cross it, and the stair-stepped "
            "octagonal rim §21 named is gone. This is the clause the 12 px rim "
            "was opened for."),
        "B6_wardrobe": (
            "The cream shirt, the white sash and the brown wrap are still THREE "
            "garments, not one robe. 20.1% of the shirt and 32.5% of the sash "
            "are inside the corridor and are genuinely at risk -- see the named "
            "fail mode. Measured the way §19 measured it: sleeve RGB against "
            "scale30's (217.9,193.4,165.0), and merged-into-wrap reads about "
            "(161.6,115.4,80.3)."),
        "B8_hair": (
            "Canon light sandy hair, not bald. 0 of 18200 head px are in the "
            "mask so this CANNOT move; it is in the bar as a falsifiable check "
            "on that claim, and if it moves the mask is not what it says it is."),
        "scale30_clauses_hold": (
            "Every clause scale30 passes, outside the mask, unchanged: B1, B2 "
            "(goblin/guard skin separation, +60.6), B3, B4a (board quad px below "
            "luma 80, 0.758 -- MINUS the hand's intended occlusion of the top-left "
            "corner, which is the point of the rung and not a regression), B4b, "
            "B4c, B5. The board is OUTSIDE the mask and the latent blend restores "
            "it every step, so unlike §18 this pass cannot lose it."),
    },
    "pre_registered_fail_modes": {
        "most_likely_THE_FIST_SURVIVES": (
            "0.99 is 39 of 40 steps and should be enough, but this is the first "
            "deletion this tree has asked for and the fist is high-contrast with "
            "its own dark outline. If a skin-coloured lump remains at the strap, "
            "the answer is NOT more strength -- it is already at the ceiling -- "
            "it is a wider OLD_GROW so the pass has more real strap to reason "
            "from, or the route closes."),
        "second_B6_MERGES_IN_THE_CORRIDOR": (
            "A fifth of the cream shirt and a third of the white sash are inside "
            "the forearm corridor and get redrawn from near-noise. §19 measured "
            "exactly this collapse at --scale2 0.5: shirt + sash + wrap became "
            "ONE BROWN ROBE. If it fires, the corridor is the cause and it is "
            "narrowable -- ARM_R 24 was chosen to fit a sleeve, not measured."),
        "third_TWO_HANDS": (
            "The pass deletes the original incompletely AND draws a new hand at "
            "the end of the corridor, leaving three hands in frame. Named "
            "because the negative already carries 'extra arms, extra hands' and "
            "it did not prevent the parent's mitten."),
        "NOT_a_fail_mode_the_vacancy_artifact": (
            "The corduroy comb, the smooth blob and the per-row ladder cannot "
            "recur: there is no vacancy and no fill function in the init. If "
            "C4' fails, it fails on what the SAMPLER drew, which is a different "
            "and more interesting failure."),
    },
    "scope_limits": (
        "Whether beat 08's staging is right. §21's rule stands and this sample "
        "does not overturn it -- it tests the one case the rule leaves open. It "
        "also says nothing about the goblin, the pointing arm, or the hair, all "
        "of which are outside the mask by construction."),
}

child = derive_spec.derive(
    src="pipeline/jobs/ep2-b13-tallcomp-0820.yaml",
    new_id=JOB,
    fresh=fresh,
    overrides=overrides,
    retoken=[("b13tallcomp-0820", "b08fistcopy-0820"),
             ("13-the-shade-tallcomp-mask-0820", "08-first-citizen-fistcopy-mask-0820"),
             ("13-the-shade-tallcomp-0820", "08-first-citizen-fistcopy-0820"),
             ("b13-tallcomp", "b08-fistcopy"),
             ("s20260820", "s%d" % SEED)],
    extra=extra,
    by="pipeline/derive_b08_fistcopy_0820.py")

out = derive_spec.write(child, "pipeline/jobs/%s.yaml" % JOB)
print("wrote %s" % out)
