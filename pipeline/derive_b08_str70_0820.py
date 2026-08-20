#!/usr/bin/env python3
r"""Derive `ep2-b08-str70-0820` -- the noun is gone, so now turn the drawing down.

ONE VARIABLE: strength 0.99 -> 0.70. Same init sha, same mask sha, same seed
20260822, same 40 steps, same cfg 7.5, same prompt, same negative. The seed is
deliberately NOT moved: at a changed strength the same seed is the control, not
a repeat.

WHY THIS RUNG IS EARNED AND WAS NOT EARNED TWO RUNGS AGO. `b08-arm-route-0819.md`
Section 23 pre-committed strength as the next lever and then refused to pull it,
on the correct ground that the fault was a NOUN and strength does not choose
nouns. Section 24 discharged that objection by measurement:
`ep2-b08-nogoblin-0820` removed the goblin from the prompt and removed it from
the picture -- in-mask G-R went -2.83 (1934 px above +20) to -16.06 (166), against
-19.90 for the untouched material around the fill. What is left is not a
character. It is OVER-DRAWING: the plate's own strap severed at the mask's top
edge, a NEW brown strap segment carrying a NEW GOLD CLASP drawn across it, and a
fan of hard white and black wedges at 9.27% shard density against the 1.82% of
the material it replaced. Strength is exactly the knob that governs how far the
sampler may invent over its conditioning, so it is now aimed at the fault that
is actually there.

0.70 IS STILL ABOVE THE STRUCTURE-PRESERVING REGIME (0.30), which matters: the
job is still to DELETE a drawn fist, and 0.236/0.30-class values have already
been measured as insufficient for that on this tree. 0.70 is the value Section 23
pre-registered, carried unchanged so this is the rung that was written down and
not a fresh guess.

THE FETCH-URL TRAP, HANDLED IN CODE RATHER THAN REMEMBERED. `derive_spec`
retokens EVERY string in a child, including the raw.githubusercontent URL that
must keep pointing at a directory somebody has actually published. That is
exactly what killed `ep2-b08-nogoblin-0820`'s first filing -- rc=1, HTTP 404,
three seconds in. So this script PUBLISHES the init and the mask under the
child's own name and then ASSERTS, against the emitted yaml, that the URL it
carries is a directory that exists with those two files at those two shas. Git
stores one blob for identical content, so the copies cost two tree entries.

$0 to run. No model, no GPU -- it writes a yaml and copies two PNGs.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b08-nogoblin-0820.yaml"
PARENT_ID = "ep2-b08-nogoblin-0820"
JOB = "ep2-b08-str70-0820"
SEED = 20260822          # UNCHANGED: at a changed strength the same seed is the control
STRENGTH = 0.70

INIT = "08-first-citizen-eraseonly-0820.png"
MASK = "08-first-citizen-eraseonly-mask-0820.png"
INIT_SHA = "7cc1a4cb12ca14a3628eb9ba8b8257ccc1f07f7cf9a9727d8ce769e1d5de8d45"
MASK_SHA = "8c94f1403c3e13839fe2351c70e494f9f2961c0b5a718db3f786d2a341a2d505"

DRY_NOTE = (
    "MASK GEOMETRY CHECK -- AND IT MUST BE BYTE-IDENTICAL TO THE PARENT'S. This "
    "rung changes STRENGTH and nothing else: same init sha, same mask sha, same "
    "seed 20260822, same 40 steps, same cfg 7.5, same prompt, same negative, "
    "0.99 -> 0.70. The mask is the guard's original left fist grown 10, 10020 px, "
    "largest component 9956 px in a 102x118 box at the CHEST. WHAT TO CHECK ON "
    "THE DRY PNG: one compact white blob at roughly x 555..660 y 528..635 with "
    "the strap running through it, NO white at the board's top edge near y~670, "
    "and no white on the guard's FACE (x 531..601 y 355..420) or the goblin "
    "(x 60..260 y 430..1140). If it differs from ep2-b08-nogoblin-0820's dry "
    "mask at all, something other than strength moved and this job must stop "
    "here at $0.")

fresh = {
    "why": (
        "THE NOUN IS GONE AND THE OVER-DRAWING IS NOT. ep2-b08-nogoblin-0820 "
        "answered the question its own rung asked: take the goblin out of the "
        "prompt and the sampler stops drawing one -- in-mask G-R -2.83 with 1934 "
        "px above +20 became -16.06 with 166, against -19.90 for the untouched "
        "material around the fill. What it drew INSTEAD is the fault this rung "
        "aims at: the plate's own harness strap severed at the mask's top edge, "
        "a NEW brown strap segment carrying a NEW GOLD CLASP across it, and a fan "
        "of hard white and black wedges measuring 9.27% shard density against "
        "1.82% for the material it replaced. Asked for 'brown leather harness "
        "strap, brown cuff' with 10020 px of freedom at 0.99, the sampler drew "
        "another one of those, with hardware. Strength is the knob that governs "
        "how far a pass may invent over its conditioning, and it is now pointed "
        "at a fault that is actually a quantity rather than a noun."),
    "consumer": (
        "BEAT 08's PLATE DECISION, and the LAST rung on the inpaint route. The "
        "conclusion behind it is already written in b08-arm-route-0819.md "
        "Section 23 and is not being re-argued: if a pass with a region-accurate "
        "prompt and a turned-down strength still invents hardware inside the "
        "mask, then a tool with NO spatial conditioning of any kind -- "
        "inpaint_fruit.py has no controlnet -- cannot be asked to erase a limb "
        "from a figure, and beat 08's grip goes back to the txt2img route with "
        "FOUR measured samples saying why. Either way this closes the route."),
    "success": (
        "ONE 832x1216 PNG plus its sidecar, published into courier-box, off the "
        "same asserted init sha as the parent. The bar below is the parent's bar "
        "with H1's plausibility half sharpened by what the parent actually drew, "
        "and with the C4' clause corrected so it can be scored at all. NOT a pick "
        "and NOT a plate_ack."),
    "owner": ("beat 08 arm-route lane, 2026-08-20 -- derived by "
              "pipeline/derive_b08_str70_0820.py off ep2-b08-nogoblin-0820, "
              "init and mask UNCHANGED"),
}

overrides = {
    "key:beat": 8,
    "key:priority": 34,
    # The parent's whole job was 20 s wall, 9.7 s of it render. 7 minutes was
    # inherited fiction and it inflates what box_autofill thinks the card holds.
    "key:est_minutes": 2,
    "argv:--strength": "%.2f" % STRENGTH,
    "argv:--note": DRY_NOTE,
}

extra = {
    "sample_declaration": (
        "ONE SAMPLE, and the FOURTH on this route. Each of the three before it "
        "moved exactly one thing and each bought a distinguishable finding: "
        "fistcopy (18408 px mask) drew a goblin HEAD, eraseonly (10020 px) drew a "
        "green goblin FIST, nogoblin (prompt) drew NO goblin at all and a second "
        "buckled strap instead. Four renders, about forty seconds of card in "
        "total, $0, and a route that will be closed or finished on the next look "
        "rather than argued about."),
    "strength_argument": (
        "CHOSEN: 0.70, at 40 steps and cfg 7.5, and it is the value Section 23 "
        "pre-registered rather than a fresh guess. THE OBJECTION THAT HELD IT "
        "BACK IS DISCHARGED: Section 23 declined to pull this lever because the "
        "fault was a NOUN and strength does not choose nouns. Section 24 measured "
        "the noun gone at 0.99 with the prompt alone, so what remains is a "
        "quantity. 0.70 IS STILL ABOVE THE STRUCTURE-PRESERVING REGIME: the pass "
        "must still DELETE a drawn fist from real pixels, and this tree has "
        "already measured 0.236-class and 0.30-class values as insufficient for "
        "deletion (see inpaint_fruit.py's own docstring and the 0.55 rung). The "
        "risk being accepted, named in advance: at 0.70 the fist may only DENT."),
    "what_the_three_parent_runs_established": (
        "Measured on landed frames, not inferred. (1) THE FIST CAN BE DELETED -- "
        "it was, completely, at 0.99, twice. (2) THE PROTECTED DIGITS SURVIVE A "
        "0.99 PASS -- the copied fist's three creases and thumb stayed legible at "
        "9x through all three runs. (3) MASK SIZE DOES NOT CHOOSE THE NOUN: "
        "18408 px drew a head, 10020 px drew a fist, same noun either way. "
        "(4) THE PROMPT DOES CHOOSE THE NOUN: removing 'goblin'/'green skin' "
        "removed it entirely, first try, at unchanged strength. (5) "
        "`--pad-crop 64` BREAKS THE OUT-OF-MASK GUARANTEE, and the breakage is "
        "now bounded: 8598 of 8598 out-of-mask changed px fall INSIDE the crop "
        "box x488-719 y458-705, 0 outside, dense within ~20 px of the mask "
        "boundary and gone by 30. (6) C4' AS PRESCRIBED CANNOT SCORE THIS "
        "GEOMETRY -- three VOIDs -- because that drift band eats its 3-12 px "
        "ring; the ring must be re-based."),
    "bar": {
        "H1_the_fist_is_GONE_and_the_strap_RUNS": (
            "THE ONE QUESTION THIS RUNG ASKS, and it is the parent's H1 with its "
            "second half made explicit because that is the half that failed. "
            "(a) DELETED: no skin-toned fist survives inside poly(FIST) grown 6, "
            "by eye at 9x -- the parent PASSED this and a regression means 0.70 "
            "was too low to erase. (b) PLAUSIBLE: the guard's own diagonal "
            "harness strap RUNS CONTINUOUSLY through the mask, entering at the "
            "top edge and leaving at the bottom, and no second strap, second "
            "buckle or second clasp appears. The parent severed the strap and "
            "drew a new clasp across the break; that is the defect this rung is "
            "trying to buy out."),
        "C4prime_RING_RE_BASED": (
            "Run pipeline/fill_quality.py's assess() on the erase region "
            "(08-first-citizen-eraseonly-erase-0820.png) with the init as plate "
            "and THE RING PUSHED OUT TO 35-45 px. D >= 0.45 AND N >= 0.25 AND "
            "F <= 2.60. DO NOT RUN THE PRESCRIBED 3-12 px RING AND REPORT ITS "
            "VOID AS A RESULT: it has VOIDed three times on this exact geometry "
            "and it will VOID again, because --pad-crop repaints the annulus. "
            "Measured on both parent frames, identically: real fraction of the "
            "annulus is 3.1% at 3-12, 41.4% at 20-30, 99.1% at 30-40 and 100.0% "
            "at 35-45. PUBLISH THE ANNULUS'S REAL-PIXEL FRACTION beside the "
            "score. AND READ THE SCORE WITH ITS KNOWN BLIND SIDE IN HAND: C4' "
            "bars D from below only, so it passed the parent's wedge fan at "
            "D 3.479 and the grandparent's green goblin fist at D 1.751. A PASS "
            "HERE IS NOT EVIDENCE THE FILL IS GOOD."),
        "C4prime_SHARD_RATE_the_clause_C4_is_missing": (
            "THE CEILING C4' DOES NOT HAVE, measured here because the parent "
            "showed why it is needed. Shard rate = fraction of fill px whose "
            "|grad| exceeds the 99th percentile of its own real ring (35-45 px). "
            "Reference values on this exact footprint: the material this fill "
            "replaces 1.82%, the grandparent's goblin fist 2.79%, the parent's "
            "wedge fan 9.27%. BAR: <= 3.00%. Also report near-black (L<40) and "
            "near-white (L>240) counts, whose reference is 242 and 535 on the "
            "init against 925 and 1542 on the parent."),
        "H3_the_digits_SURVIVED": (
            "The copied fist's three finger creases and thumb are still "
            "individually legible at 9x. It is wholly outside the mask but "
            "INSIDE the pad-crop box (box y ends 705, the copy spans y 640-705), "
            "so it is not untouched: it read maxdiff 55 at the grandparent and "
            "121 at the parent. Report the number; legible is the bar."),
        "H5_NO_NEW_NOUN": (
            "No face, no head, no figure, no placket -- and, sharpened by the "
            "parent, NO NEW HARDWARE: no second buckle and no second clasp. "
            "Judged by eye at 4x on the whole frame, plus the green-channel "
            "measurement that made the parent's verdict checkable: in-mask G-R "
            "mean and px above +20, against -19.90 and 0 for the real material "
            "around the fill."),
        "B8_hair": (
            "Canon light sandy hair, not bald. maxdiff 0 over the head box "
            "(500..640, 300..430), which has now held at 0 through three runs "
            "because the head is outside the crop box."),
        "B6_wardrobe": (
            "Cream shirt, white sash and brown wrap are still THREE garments. "
            "The mask reaches none of them but the shirt around the fist."),
        "OUT_OF_MASK_DRIFT_is_MEASURED_not_assumed": (
            "Report changed px outside the mask, their maxdiff, and how many of "
            "them fall outside the pad-crop box x488-719 y458-705. The answer to "
            "the last one has been 0 twice and any other answer is a finding. "
            "Reference: 8574 px / maxdiff 132 at the grandparent, 8598 / 151 at "
            "the parent."),
        "scale30_clauses_hold": (
            "B1, B2, B3, B4a, B4b, B4c, B5 re-measured on the landed frame. "
            "Goblin box (60..260, 430..1140) and board box (300..832, 660..1000) "
            "are both far outside the crop box and have read maxdiff 0 and 1."),
    },
    "pre_registered_fail_modes": {
        "most_likely_A_the_fist_only_DENTS": (
            "0.70 is a 29% cut in how far the pass may leave its conditioning, "
            "and deletion is the thing that needs freedom. If a skin-toned "
            "remnant survives inside poly(FIST) grown 6, THE ROUTE IS CLOSED, not "
            "retuned: 0.99 deletes but over-draws and 0.70 under-deletes would "
            "mean no single value satisfies the conjunction, which is the same "
            "shape of refusal the b01 crf ladder reached and it should be read "
            "the same way. DO NOT PROPOSE 0.85."),
        "second_THE_CLASP_COMES_BACK_ANYWAY": (
            "If the strap is still severed and a clasp is still drawn at 0.70, "
            "then the invention is not a function of strength either, and the "
            "honest conclusion in the consumer field fires: no spatial "
            "conditioning, no limb erasure, back to txt2img."),
        "third_A_SEAM_AT_THE_COPY": (
            "The copy's stair-stepped octagonal edge is untouched by this pass "
            "and WILL still read as a decal. EXPECTED, NOT A FAIL -- it is the "
            "second pass's job, and it is written here again so that seeing it "
            "does not get mistaken for a regression."),
        "NOT_a_fail_mode_a_C4prime_PASS": (
            "C4' passing is not evidence of a good fill on this instrument: it "
            "passed a green goblin fist and a wedge fan. Only the shard-rate "
            "clause and the eye clauses can fail this frame."),
    },
    "init_provenance": (
        "pipeline/beat08_grip_copy.py --write --variant eraseonly. init %s "
        "sha %s, mask %s sha %s -- BYTE-IDENTICAL to both parents, fetched by "
        "sha from farm-out/%s/ on origin/main. THE URL IS ASSERTED BY THE "
        "DERIVER, not trusted: derive_spec retokens every string in a child, "
        "which is what pointed ep2-b08-nogoblin-0820's first filing at a "
        "directory nobody had published and killed it with a 404 three seconds "
        "in. This script publishes both files under this job's own name and then "
        "re-reads the emitted yaml to check the URL it carries resolves."
        % (INIT, INIT_SHA, MASK, MASK_SHA, JOB)),
    "scope_limits": (
        "This does not settle beat 08's staging and it does not attempt the "
        "forearm. The plate draws the guard's hand at the authored elbow and the "
        "pose hint wants it at the wrist; re-routing a limb needs spatial "
        "conditioning that inpaint_fruit.py does not have. That is a txt2img "
        "question and this rung leaves it there."),
}


def publish_init_beside_the_child() -> str:
    """Put the init and the mask where the retokened URL will point.

    Returns the repo-relative directory. Refuses on any sha mismatch: a file
    published under a new name with the wrong bytes is worse than a 404,
    because fetch_init.py's assertion would catch it on the CARD instead of
    here, after the job has been queued and claimed.
    """
    src = os.path.join(REPO, "farm-out", PARENT_ID)
    dst = os.path.join(REPO, "farm-out", JOB)
    os.makedirs(dst, exist_ok=True)
    for name, want in ((INIT, INIT_SHA), (MASK, MASK_SHA)):
        s = os.path.join(src, name)
        if not os.path.isfile(s):
            raise SystemExit("!! %s is not in farm-out/%s -- nothing to publish"
                             % (name, PARENT_ID))
        shutil.copy2(s, os.path.join(dst, name))
        with open(os.path.join(dst, name), "rb") as fh:
            have = hashlib.sha256(fh.read()).hexdigest()
        if have != want:
            raise SystemExit("!! %s published with the wrong bytes\n   want %s\n"
                             "   have %s" % (name, want, have))
    return "farm-out/" + JOB


def assert_the_fetch_url_resolves(spec_path: str) -> None:
    """Re-read the EMITTED yaml and check its fetch URL against the filesystem.

    Not the deriver's inputs -- the emitted file, after retoken has had its
    way with every string in it. This is the guard the 404 bought.
    """
    import re

    import yaml
    with open(spec_path, encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    # Every string the spec carries, payload bodies included. The URL is built
    # in the payload as two ADJACENT python literals split over a line break --
    # `"...main/"` then `"farm-out/<dir>/"` -- so the concatenation is undone
    # before matching, or the regex sees a host with no path and reports
    # nothing, which is the one answer this guard must never give.
    def strings(v):
        if isinstance(v, str):
            yield v
        elif isinstance(v, dict):
            for k, x in v.items():
                yield k
                yield from strings(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                yield from strings(x)
    blob = re.sub(r'"\s*"', "", "\n".join(strings(spec)))
    urls = set(re.findall(
        r"https://raw\.githubusercontent\.com/[^/]+/[^/]+/main/"
        r"(farm-out/[A-Za-z0-9._-]+)/", blob))
    if not urls:
        raise SystemExit("!! no farm-out fetch URL in %s -- this deriver "
                         "assumes one and will not pass a spec it cannot check"
                         % spec_path)
    for rel in sorted(urls):
        d = os.path.join(REPO, rel)
        missing = [n for n in (INIT, MASK)
                   if not os.path.isfile(os.path.join(d, n))]
        if not os.path.isdir(d) or missing:
            raise SystemExit(
                "!! the emitted spec fetches from %s/ and that directory does "
                "not hold %s.\n   THIS IS THE RETOKEN TRAP: derive_spec "
                "rewrites every string in a child, published-artifact URLs "
                "included. Publish the files there or override the payload "
                "after retoken." % (rel, ", ".join(missing) or "the init"))
        print("  fetch URL OK: %s/ holds both files" % rel)


child = derive_spec.derive(
    src=PARENT,
    new_id=JOB,
    fresh=fresh,
    overrides=overrides,
    retoken=[("b08nogoblin-0820", "b08str70-0820"),
             ("b08-nogoblin", "b08-str70")],
    extra=extra,
    by="pipeline/derive_b08_str70_0820.py")

published = publish_init_beside_the_child()
print("published init + mask -> %s/" % published)
out = derive_spec.write(child, "pipeline/jobs/%s.yaml" % JOB)
assert_the_fetch_url_resolves(out)
print("wrote %s" % out)
