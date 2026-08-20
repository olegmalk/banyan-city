#!/usr/bin/env python3
"""Derive `ep2-b08-eraseonly-0820` -- the corrective for a rung that came back
with a second goblin in it.

PARENT IS `ep2-b08-fistcopy-0820`, WHICH FAILED, AND THAT IS REAL ANCESTRY THIS
TIME. That job put a byte-exact copy of the guard's fist at the board and asked
one 18408 px mask to do three things at strength 0.99. It deleted the fist and
it kept the copied digits -- both as predicted -- and into the rest of the mask
it drew a whole second goblin: green skull, blond hair, pointed ears, a buttoned
shirt placket where the harness strap had been.

THE OBVIOUS CORRECTIVE WAS WRONG AND IT WAS MEASURED BEFORE IT WAS FILED. I had
argued hardest for the forearm corridor, so the corridor looked like the
culprit. Dropping it saves **434 px of 18408** -- it was already covered by the
fist's own margin and the copy's rim. Filing that rung would have changed 2% of
the mask and taught nothing.

THE ACTUAL CAUSE IS GEOMETRY. The two work sites -- the fist at y 542-620 and
the copy at y 633-711 -- are 13 px apart, so ANY mask covering both is one
~200 px tall region. It does not split at OLD_GROW 4 any more than at 14; that
was swept. A region that size, at 0.99, under a prompt naming "the small goblin
man", with NO spatial conditioning anywhere in this pipeline, gets filled with
the largest available noun. `composite-init-pattern.md` names that failure in
those words.

SO THIS RUNG MASKS ONE SITE AND ASKS ONE QUESTION: can the sampler delete the
hand from real strap pixels? 10020 px in a 102x118 box, grow 10 instead of 14.
The copy stays in the init, wholly outside the mask, and reads as a decal --
its contact edge becomes a SECOND pass on this pass's output. Two small masks
in series, never one big one.

ONE VARIABLE. Strength stays 0.99, the prompt stays byte-identical, the seed
moves only because a repeat draw on a changed mask is a different sample. If a
noun still arrives in a 102x118 box, the answer is strength, and that is the
next rung rather than this one.

$0 to run. No model, no network, no GPU -- it writes a yaml.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import derive_spec  # noqa: E402
import beat08_grip_copy as C  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB = "ep2-b08-eraseonly-0820"
SEED = 20260821

INIT = "08-first-citizen-eraseonly-0820.png"
MASK = "08-first-citizen-eraseonly-mask-0820.png"
INIT_SHA = "7cc1a4cb12ca14a3628eb9ba8b8257ccc1f07f7cf9a9727d8ce769e1d5de8d45"
MASK_SHA = "8c94f1403c3e13839fe2351c70e494f9f2961c0b5a718db3f786d2a341a2d505"

FETCH = '''#!/usr/bin/env python3
"""Fetch beat 08's ERASE-ONLY composite and its mask; refuse on any sha mismatch.

No model, no GPU, no spend. Both files are on origin/main -- written by
pipeline/beat08_grip_copy.py on a Mac, so they are NOT on the box's courier
worktree, which only ever contains what the box produced. The sha256s asserted
here are verifiable against the repo by anyone who clones it.

WHAT THE INIT CONTAINS, SO THE OPERATOR IS NOT SURPRISED BY IT: the guard has
TWO left fists. That is not a defect, it is the rung. The plate's own fist is
still at the strap where it was drawn -- inside the mask, for this pass to
delete from real pixels -- and a byte-exact COPY of it sits at the board's top
edge, WHOLLY OUTSIDE the mask, so it comes through untouched. The copy's edge
will still read as a decal in this output and that is expected: drawing its
contact is a SECOND pass on this pass's result. The parent job put both sites
in one mask and the sampler filled it with a whole second goblin.
"""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\b08eraseonly-0820"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "farm-out/ep2-b08-eraseonly-0820/")
UA = {"User-Agent": "banyan-city-b08-eraseonly/1.0 (albert.numbro@gmail.com)"}
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
    "a wrong mask costs seconds instead of a GPU fire. THIS MASK IS ONE REGION "
    "AND IT IS THE WHOLE POINT: 10020 px, 0.99 percent of the frame, largest "
    "component 9956 px in a 102x118 box -- against the 18408 px / 142x211 region "
    "that hosted a second goblin's head on this job's parent. It is the guard's "
    "ORIGINAL left fist at the harness strap, grown 10, and NOTHING ELSE: no "
    "forearm corridor, no rim around the copy, no board band. WHAT TO CHECK ON "
    "THE DRY PNG: one compact white blob up at the CHEST, roughly x 555..660 "
    "y 528..635, with the strap running through it; NO white anywhere near the "
    "board's top edge at y~670 (the copied fist must be entirely black -- it is "
    "outside the mask and must stay drawn); and no white touching the guard's "
    "FACE (x 531..601 y 355..420) or the goblin (x 60..260 y 430..1140). If "
    "there is white at the board edge, this is the parent's mask and not this "
    "one, and the job must stop here at $0.")

fresh = {
    "why": (
        "THE PARENT CAME BACK WITH A CHARACTER IN IT. `ep2-b08-fistcopy-0820` "
        "asked one 18408 px mask, at strength 0.99, to delete a fist AND draw a "
        "forearm AND draw a contact edge. It did the two things the argument "
        "predicted -- deleted the fist, kept the copied digits byte-intact -- "
        "and filled the rest with a second goblin: green skull, blond hair, "
        "pointed ears, a buttoned shirt placket where the harness strap had "
        "been. THE CORRIDOR I HAD ARGUED HARDEST FOR WAS NOT THE CAUSE, and "
        "that was measured before this rung was written: dropping it saves 434 "
        "px of 18408, because it was already covered by the fist's own margin "
        "and the copy's rim. The cause is geometry -- the two work sites are 13 "
        "px apart, so any mask covering both is one ~200 px tall region, and it "
        "does not split at OLD_GROW 4 any more than at 14. So this rung stops "
        "asking one pass to do two edits. ONE SITE, ONE QUESTION."),
    "consumer": (
        "BEAT 08's PLATE DECISION, unchanged, and now narrowed to its "
        "load-bearing half. §21 ruled the vacancy unfillable BY US; the parent "
        "asked whether the SAMPLER could fill it from real strap pixels and the "
        "answer came back buried under a goblin. This asks it cleanly. A pass "
        "means the fist can be removed and beat 08's grip becomes a two-pass "
        "composite -- delete here, contact in a second pass on this output. A "
        "fail closes composite-then-inpaint on this beat for good and sends the "
        "grip back to staging with a measured reason instead of a suspicion."),
    "success": (
        "ONE 832x1216 PNG plus its sidecar, published into courier-box, off the "
        "asserted init sha. The bar is below, written before the pixels existed, "
        "and it includes the clause the parent taught: the mask's largest "
        "component is 1.8x smaller by area than the region that hosted a face. "
        "NOT a pick and NOT a plate_ack."),
    "owner": ("beat 08 arm-route lane, 2026-08-20 -- derived by "
              "pipeline/derive_b08_eraseonly_0820.py, init by "
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
    # prompt.txt and negative.txt are NOT overridden: they are already beat
    # 08's own scale30 text on the parent, and derive_spec refuses a
    # "override" that is byte-identical -- correctly. Unchanged wording is
    # what makes the mask the only variable.
}

extra = {
    "sample_declaration": (
        "ONE SAMPLE, and the SECOND on this route. The first "
        "(ep2-b08-fistcopy-0820) is why this one exists, and it is exactly what "
        "the founder's 2026-08-03 rule buys: one render, seven minutes, $0, and "
        "a route corrected before anything was scaled. One variable moves here "
        "-- the mask. Strength stays 0.99 and the prompt stays byte-identical; "
        "the seed moves only because a repeat draw against a changed mask is a "
        "different sample, not a repeat."),
    "strength_argument": C.STRENGTH_ARGUMENT,
    "what_the_parent_run_established": (
        "Measured on the landed frame, not inferred. (1) THE FIST CAN BE "
        "DELETED -- it was, completely. (2) THE PROTECTED DIGITS SURVIVE A 0.99 "
        "PASS -- they did, byte-intact, which confirms the latent-blend "
        "argument and means strength is NOT the lever that endangers them. "
        "(3) A ~200 px TALL MASK AT 0.99 GETS FILLED WITH A CHARACTER. (4) "
        "`--pad-crop 64` BREAKS THE OUT-OF-MASK GUARANTEE: the landed frame "
        "differs from its init in 15355 px OUTSIDE the mask, maxdiff 160, "
        "because padding_mask_crop upscales a crop and resamples it back. That "
        "is a property of the tool, it applies to every composite in this tree, "
        "and on that frame the guard's head fell outside the crop box and read "
        "maxdiff 0 -- B8 survived by luck of geometry, not by the guarantee. "
        "IT IS IN THIS SPEC'S BAR AS A MEASURED CLAUSE FOR THAT REASON."),
    "init_provenance": (
        "pipeline/beat08_grip_copy.py --write --variant eraseonly, selftest "
        "PASS on 19 clauses. init %s sha %s, mask %s sha %s, both on "
        "origin/main and fetched by sha. The INIT IS BYTE-IDENTICAL to the "
        "parent's (same sha 7cc1a4cb...): the composite did not change, only "
        "the mask did, which is what makes this a one-variable sample. The mask "
        "is the guard's original fist grown 10 and nothing else -- 10020 px, "
        "largest component 9956 px in a 102x118 box." % (INIT, INIT_SHA, MASK, MASK_SHA)),
    "bar": {
        "H1_the_fist_is_GONE": (
            "THE ONE QUESTION THIS RUNG ASKS. The original fist must be DELETED "
            "and replaced by plausible harness strap, cuff and shirt: no "
            "skin-toned blob survives inside poly(FIST) grown 6, judged by eye "
            "at 5x. The parent PASSED this clause, so a regression here would "
            "mean the smaller mask starved the pass of context."),
        "C4prime": (
            "Run pipeline/fill_quality.py on the erase region (published as "
            "08-first-citizen-eraseonly-erase-0820.png) with the init as "
            "--plate: D >= 0.45 AND N >= 0.25 AND F <= 2.60. NOTE THE PARENT "
            "RETURNED **VOID** ON THIS CLAUSE, CORRECTLY -- its 18408 px mask "
            "left only 120 real px in the 3-12 px ring, below the 200 px floor, "
            "so the instrument refused to score rather than guess. That is dead "
            "zone 5 behaving as documented. This mask is small enough that the "
            "ring clears it: measured 4673 real px on the init."),
        "H3_the_digits_SURVIVED": (
            "The copied fist's fingers and thumb are still individually legible "
            "at 5x. The parent proved this holds at 0.99; here the copy is "
            "WHOLLY outside the mask rather than merely interior-protected, so "
            "it should hold more strongly."),
        "H5_NO_NEW_NOUN": (
            "THE CLAUSE THE PARENT BOUGHT. No face, no head, no figure, no "
            "garment placket that was not in the init appears anywhere in the "
            "mask. Judged by eye at 4x on the whole frame, not just the crop -- "
            "the parent's goblin was obvious at 1x and would have been caught by "
            "any look at all."),
        "B6_wardrobe": (
            "The cream shirt, the white sash and the brown wrap are still THREE "
            "garments. The mask no longer reaches the sash or the belt at all; "
            "what remains exposed is the shirt around the fist."),
        "B8_hair": (
            "Canon light sandy hair, not bald. 0 px of the head are in the mask "
            "AND the head must also fall outside the --pad-crop box: the parent "
            "showed the mask alone does not guarantee this. Measured as maxdiff "
            "0 over the head box (500..640, 300..430)."),
        "OUT_OF_MASK_DRIFT_is_MEASURED_not_assumed": (
            "Report changed px outside the mask and their maxdiff. The parent "
            "read 15355 px / maxdiff 160. This mask's crop box is much smaller, "
            "so the number should fall; whatever it is, it is REPORTED rather "
            "than claimed to be zero, and every scale30 clause is re-measured "
            "on the landed frame rather than assumed to survive."),
        "scale30_clauses_hold": (
            "B1, B2 (goblin/guard skin separation, +60.6), B3, B4a, B4b, B4c, "
            "B5 re-measured on the landed frame. The board is far outside this "
            "mask and outside its crop box."),
    },
    "pre_registered_fail_modes": {
        "most_likely_A_NOUN_STILL_ARRIVES": (
            "102x118 is smaller than the region that hosted a head but it is "
            "not small. If a face, a hand or a bunched garment object appears, "
            "the mask is not the whole lever and STRENGTH is the next rung: "
            "0.99 -> 0.70, which is still above the 0.30 structure-preserving "
            "regime. That is the pre-committed next step and it is one variable."),
        "second_THE_FIST_ONLY_DENTS": (
            "The smaller margin gives the pass less real strap to reason from, "
            "so the deletion could come back partial where the parent's was "
            "complete. If so the answer is grow 10 -> 12, not more strength."),
        "third_A_SEAM_AT_THE_COPY": (
            "With no rim in the mask, the copy's stair-stepped octagonal edge "
            "is untouched and WILL still read as a decal. THIS IS EXPECTED, NOT "
            "A FAIL of this rung -- it is the second pass's job. It is written "
            "here so that seeing it does not get mistaken for a regression."),
        "NOT_a_fail_mode_the_vacancy_artifact": (
            "The corduroy comb, the smooth blob and the per-row ladder cannot "
            "recur: there is no vacancy and no fill function in the init."),
    },
    "scope_limits": (
        "This does not settle beat 08's staging, and it deliberately does not "
        "attempt the forearm. The plate draws the guard's hand at the authored "
        "elbow and the pose hint wants it at the wrist; re-routing a limb needs "
        "spatial conditioning, and inpaint_fruit.py has no controlnet at all. "
        "That is a txt2img-route question and this rung leaves it there."),
}

child = derive_spec.derive(
    src="pipeline/jobs/ep2-b08-fistcopy-0820.yaml",
    new_id=JOB,
    fresh=fresh,
    overrides=overrides,
    retoken=[("b08fistcopy-0820", "b08eraseonly-0820"),
             ("08-first-citizen-fistcopy-mask-0820", "08-first-citizen-eraseonly-mask-0820"),
             ("08-first-citizen-fistcopy-erase-0820", "08-first-citizen-eraseonly-erase-0820"),
             ("08-first-citizen-fistcopy-0820", "08-first-citizen-eraseonly-0820"),
             ("b08-fistcopy", "b08-eraseonly"),
             ("s20260820", "s%d" % SEED)],
    extra=extra,
    by="pipeline/derive_b08_eraseonly_0820.py")

out = derive_spec.write(child, "pipeline/jobs/%s.yaml" % JOB)
print("wrote %s" % out)
