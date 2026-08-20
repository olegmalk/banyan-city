#!/usr/bin/env python3
r"""Derive `ep2-b08-nostrap2-0820` -- negative the last noun, or close the route.

ONE VARIABLE: the NEGATIVE. Strength stays 0.70, the positive stays byte-identical,
the init, the mask, the seed 20260822, the 40 steps and the cfg 7.5 all stay.

WHY THIS AND NOT ANOTHER STRENGTH. `ep2-b08-str70-0820` deleted the fist
completely and kept the guard's own harness strap running from buckle to belt --
the first frame on this route to do either. What it added was a SECOND BROWN BAND
crossing the strap below the buckle, a small X the init does not have. That is a
NOUN, and this route has already MEASURED that the prompt chooses nouns:
`ep2-b08-nogoblin-0820` removed "goblin"/"green skin" from the positive and the
goblin vanished outright at unchanged strength, 1934 green px to 166. So the
lever aimed at what is actually wrong is the negative, and the noun to name is
the one that arrived.

AN INTERMEDIATE STRENGTH IS EXPLICITLY NOT THE RUNG. 0.99 over-draws (shard rate
9.27% against the plate's 1.82%), 0.70 under-inks (0.38%), and the fault AT 0.70
is a noun rather than a quantity. A midpoint would search for a value satisfying
a conjunction the knob does not express -- the same refusal beat 01's crf ladder
reached on 2026-08-20.

THE STOPPING RULE, PRE-COMMITTED BEFORE THE RENDER. If this pass draws a THIRD
unwanted noun, THE ROUTE CLOSES on the conclusion already written in
`b08-arm-route-0819.md` Section 23: a tool with no spatial conditioning of any
kind trades one invention for another indefinitely, and five samples is enough to
say so. Beat 08's grip goes back to txt2img and this file is the last inpaint
rung on it.

$0 to run. No model, no GPU -- it writes a yaml and copies two PNGs.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import derive_fetch_guard as G  # noqa: E402
import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b08-str70-0820.yaml"
PARENT_ID = "ep2-b08-str70-0820"
JOB = "ep2-b08-nostrap2-0820"
SEED = 20260822

WANT = {
    "08-first-citizen-eraseonly-0820.png":
        "7cc1a4cb12ca14a3628eb9ba8b8257ccc1f07f7cf9a9727d8ce769e1d5de8d45",
    "08-first-citizen-eraseonly-mask-0820.png":
        "8c94f1403c3e13839fe2351c70e494f9f2961c0b5a718db3f786d2a341a2d505",
}

# THE PARENT'S NEGATIVE, KEPT WHOLE, PLUS THE NOUN THE PARENT ACTUALLY DREW.
# `double strap, crossed straps, second strap, extra strap, strap end` names the
# crossing band; `buckle, clasp, buckles` is carried in from the grandparent's
# failure and kept because the parent only ALMOST stopped drawing hardware -- a
# few-px orange speck survived at x~600 y~575. Nothing else moves.
NEGATIVE = (
    "double strap, crossed straps, second strap, extra strap, strap end, "
    "buckle, clasp, buckles, "
    "goblin, green skin, pointed ears, second figure, face, head, "
    "hand, fist, fingers, knuckles, arm, buttons, placket, "
    "giant, colossus, towering figure, different scale, floating, raised "
    "clipboard, second board, extra arms, extra hands, extra fingers, deformed "
    "hands, crowd, girl, child, chibi, armor, helmet, knight, dark, night, "
    "text, watermark, photorealism, 3d render, low quality, deformed\n")

DRY_NOTE = (
    "MASK GEOMETRY CHECK -- AND IT MUST BE BYTE-IDENTICAL TO THE PARENT'S. This "
    "rung changes the NEGATIVE and nothing else: same init sha, same mask sha, "
    "same seed 20260822, same strength 0.70, same 40 steps, same cfg 7.5, same "
    "positive. The mask is the guard's original left fist grown 10, 10020 px, "
    "largest component 9956 px in a 102x118 box at the CHEST. WHAT TO CHECK ON "
    "THE DRY PNG: one compact white blob at roughly x 555..660 y 528..635 with "
    "the strap running through it, NO white at the board's top edge near y~670, "
    "and no white on the guard's FACE (x 531..601 y 355..420) or the goblin "
    "(x 60..260 y 430..1140). If it differs from ep2-b08-str70-0820's dry mask "
    "at all, something other than the negative moved and this job must stop "
    "here at $0.")

fresh = {
    "why": (
        "ONE BAND SHORT. ep2-b08-str70-0820 is the first frame on this route to "
        "delete the fist AND keep the guard's own harness strap running from "
        "buckle to belt, with no second buckle, no clasp and zero green pixels "
        "-- in-mask G-R -23.11 against -19.90 for the real material around it. "
        "It failed ONE pre-registered sub-clause: a second brown band crosses "
        "the strap below the buckle, forming a small X the init does not have. "
        "That is a NOUN, and this route has measured that the prompt chooses "
        "nouns -- taking 'goblin' out of the positive took the goblin out of the "
        "picture at unchanged strength. So the lever is the negative and the "
        "noun to name is the one that arrived. NOT another strength: 0.99 "
        "over-draws at 9.27% shard against the plate's 1.82%, 0.70 under-inks at "
        "0.38%, and the remaining fault is a noun rather than a quantity."),
    "consumer": (
        "BEAT 08's PLATE DECISION, and this is the LAST inpaint rung on it "
        "either way. If the crossing band goes, beat 08 has a grip plate and the "
        "route finishes on a frame rather than an argument. If a THIRD unwanted "
        "noun arrives, the route CLOSES on the conclusion in "
        "b08-arm-route-0819.md Section 23 -- a tool with no spatial conditioning "
        "trades one invention for another indefinitely -- and the grip goes back "
        "to txt2img with five measured samples saying why. The stopping rule is "
        "written here, before the render, so it cannot be renegotiated after "
        "seeing the pixels."),
    "success": (
        "ONE 832x1216 PNG plus its sidecar, published into courier-box, off the "
        "same asserted init sha as all three parents. The bar below is the "
        "parent's bar unchanged except that H1(b) now also asks for the plate's "
        "own INK back, which is the defect 0.70 introduced. NOT a pick and NOT a "
        "plate_ack."),
    "owner": ("beat 08 arm-route lane, 2026-08-20 -- derived by "
              "pipeline/derive_b08_nostrap2_0820.py off ep2-b08-str70-0820, "
              "init, mask, seed, strength and positive all UNCHANGED"),
}

overrides = {
    "key:beat": 8,
    "key:priority": 34,
    "key:est_minutes": 2,
    "argv:--note": DRY_NOTE,
    "payload:negative.txt": NEGATIVE,
}

extra = {
    "sample_declaration": (
        "ONE SAMPLE, the FIFTH and last on this route. Four before it, each "
        "moving exactly one thing, each buying a finding that ruled something "
        "out: mask SIZE does not choose the noun (18408 px drew a head, 10020 px "
        "drew a fist); the PROMPT does (the goblin vanished outright); STRENGTH "
        "governs how much gets invented over the conditioning (0.99 over-draws, "
        "0.70 keeps the strap). About fifty seconds of card in total, $0."),
    "strength_argument": (
        "UNCHANGED AT 0.70, and that is the point of this rung -- it is the only "
        "value measured to delete the fist without over-drawing. The pre-committed "
        "refusal stands and is repeated so it is not quietly dropped: DO NOT "
        "PROPOSE AN INTERMEDIATE STRENGTH. The pool samples the knob at 0.70 and "
        "0.99; one under-inks, one over-draws, and the fault this rung attacks is "
        "a noun that a quantity cannot address."),
    "what_the_four_parent_runs_established": (
        "Measured on landed frames. (1) THE FIST CAN BE DELETED, and it does not "
        "need 0.99 -- 0.70 deletes it completely. (2) MASK SIZE DOES NOT CHOOSE "
        "THE NOUN. (3) THE PROMPT DOES: removing 'goblin'/'green skin' removed it "
        "entirely at unchanged strength, in-mask G-R -2.83 with 1934 px above "
        "+20 to -16.06 with 166, and 0.70 reached -23.11 with ZERO. (4) STRENGTH "
        "GOVERNS INVENTION, symmetrically: shard rate 1.82% for the material "
        "replaced, 9.27% at 0.99, 0.38% at 0.70 -- neither end lands on the "
        "plate's own line quality. (5) THE PROTECTED DIGITS SURVIVE every pass, "
        "and take LESS damage at 0.70 (maxdiff 78) than at 0.99 (121). (6) "
        "--pad-crop drift is DETERMINISTIC: 8574 / 8598 / 8600 px over three "
        "renders of identical geometry, 100% of it inside the crop box every "
        "time. (7) C4' AS PRESCRIBED CANNOT SCORE THIS GEOMETRY -- three VOIDs -- "
        "and at a re-based ring it PASSES ALL FOUR FRAMES INCLUDING A GREEN "
        "GOBLIN FIST, so it cannot be the clause that decides this beat."),
    "bar": {
        "H1_the_fist_is_GONE_the_strap_RUNS_and_it_is_INKED": (
            "(a) DELETED: no skin-toned remnant inside poly(FIST) grown 6, by eye "
            "at 14x. The parent PASSED this at 0.70 and a regression would be a "
            "surprise. (b) ONE STRAP: the guard's own diagonal strap runs "
            "continuously from the buckle to the belt and NO second band, no "
            "crossing X, no strap end, no second buckle and no clasp appears. "
            "This is the clause the parent failed and the only reason this rung "
            "exists. (c) INKED: the fill's ink density (px with L<90 inside the "
            "erase region) is within 3 points of the plate's 13.3%. The parent "
            "read 10.5% -- soft, not wrong -- and 0.99 read 24.6%. This is a NEW "
            "sub-clause and it is registered as the one most likely to fail, "
            "because nothing in this rung is aimed at it."),
        "C4prime_SHARD_RATE_with_a_FLOOR_this_time": (
            "Shard rate = fraction of erase-region px whose |grad| exceeds the "
            "99th percentile of its own real ring at 35-45 px. BAR: 0.80% <= "
            "rate <= 3.00%. THE FLOOR IS NEW and it is the correction the parent "
            "earned: at 0.38% the parent is 4.8x SMOOTHER than the 1.82% material "
            "it replaced, and the ceiling-only clause called that a pass. "
            "Calibration, from an empirical null of 200 real windows of this "
            "footprint: median 0.35%, p95 4.11%, p99 6.74%. The floor is "
            "deliberately BELOW the plate's own 1.82% -- a fill quieter than its "
            "surroundings is expected where a hand has been removed from cloth; "
            "5x quieter is not."),
        "C4prime_RING_RE_BASED": (
            "assess() on the erase region with the init as plate and THE RING AT "
            "35-45 px; D >= 0.45, N >= 0.25, F <= 2.60; publish the annulus's "
            "real-pixel fraction. DO NOT RUN THE PRESCRIBED 3-12 px RING -- three "
            "VOIDs on this geometry. AND A PASS HERE DECIDES NOTHING: this "
            "instrument has now passed a green goblin fist, a wedge fan and a "
            "clean strap. It is reported for continuity, not as evidence."),
        "H3_the_digits_SURVIVED": (
            "Three finger creases and the thumb individually legible at 14x on "
            "the copied fist. Report its maxdiff: 55 / 121 / 78 across the three "
            "parents, and it is inside the pad-crop box, so it is never zero."),
        "H5_NO_NEW_NOUN": (
            "No face, no head, no figure, no placket, no hardware. Measured on "
            "the green channel: in-mask G-R mean and px above +20, against "
            "-19.90 and 0 for the real material around the fill. The parent read "
            "-23.11 and ZERO; anything above zero is a regression."),
        "B8_hair": "maxdiff 0 over the head box (500..640, 300..430), as on all three parents.",
        "B6_wardrobe": "Cream shirt, white sash and brown wrap still THREE garments.",
        "OUT_OF_MASK_DRIFT_is_MEASURED_not_assumed": (
            "Report changed px outside the mask, their maxdiff, and how many "
            "fall outside the crop box x488-719 y458-705. The last figure has "
            "been 0 three times and the totals 8574 / 8598 / 8600; a fourth "
            "reading in that band confirms the drift is a property of the crop."),
        "scale30_clauses_hold": (
            "Goblin box (60..260, 430..1140) and board box (300..832, 660..1000) "
            "re-measured; they have read maxdiff 0 and 1 on every frame."),
    },
    "pre_registered_fail_modes": {
        "most_likely_A_THE_INK_STAYS_SOFT": (
            "Nothing in this rung aims at ink density, so 10.5% is the value to "
            "expect again. If the band goes and the ink stays soft, THAT IS A "
            "PASS OF THIS RUNG AND A NEW, SMALLER QUESTION -- and it is a "
            "compositor question, not a sampler one: the plate's own ink can be "
            "carried over the fill. It does NOT license a sixth inpaint rung."),
        "second_A_THIRD_NOUN_ARRIVES": (
            "A pocket, a seam, a fold-that-is-an-object, a strap the negative "
            "did not name. THE ROUTE CLOSES. This is the stopping rule and it is "
            "not renegotiable after the fact: three nouns negatived one at a "
            "time is a tool being steered by exclusion, which does not converge."),
        "third_THE_NEGATIVE_EATS_THE_REAL_STRAP": (
            "'double strap, second strap, extra strap' at cfg 7.5 could suppress "
            "the strap the pass is supposed to KEEP, leaving bare shirt where the "
            "harness crosses. That would be a FAIL of H1(b) from the other "
            "direction and it would mean the negative cannot distinguish 'a "
            "second one' from 'this one' -- which also closes the route, because "
            "the remaining lever would be spatial conditioning the tool lacks."),
        "NOT_a_fail_mode_the_seam_at_the_copy": (
            "The copy's stair-stepped octagonal edge is untouched by this pass "
            "and WILL still read as a decal. Expected, and the second pass's job."),
        "NOT_a_fail_mode_a_C4prime_PASS": (
            "C4' has passed all four frames on this route including a green "
            "goblin fist. A fifth pass is not evidence."),
    },
    "init_provenance": (
        "pipeline/beat08_grip_copy.py --write --variant eraseonly. init and mask "
        "BYTE-IDENTICAL to all three parents, fetched by sha from "
        "farm-out/%s/ on origin/main. THE URL IS ASSERTED BY THE DERIVER via "
        "pipeline/derive_fetch_guard.py, which re-reads the emitted yaml AFTER "
        "retoken -- the guard that ep2-b08-nogoblin-0820's 404 bought." % JOB),
    "scope_limits": (
        "This does not settle beat 08's staging and does not attempt the "
        "forearm. It is the last inpaint rung on the grip either way."),
}

child = derive_spec.derive(
    src=PARENT,
    new_id=JOB,
    fresh=fresh,
    overrides=overrides,
    retoken=[("b08str70-0820", "b08nostrap2-0820"),
             ("b08-str70", "b08-nostrap2")],
    extra=extra,
    by="pipeline/derive_b08_nostrap2_0820.py")

print("published init + mask -> %s/"
      % G.publish_beside_the_child("farm-out/" + PARENT_ID,
                                   "farm-out/" + JOB, WANT))
out = derive_spec.write(child, "pipeline/jobs/%s.yaml" % JOB)
G.assert_fetch_urls_resolve(out, tuple(WANT))
print("wrote %s" % out)
