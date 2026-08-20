#!/usr/bin/env python3
"""Beat 01 cold open: the negative prompt gains the only fault its best seed has.

ONE VARIABLE, and it is `b01-negative.txt`. Same init, same sha, same anchor,
SAME SEED 20260840, same motion prompt byte for byte, same every flag, same 121
frames. `ep2-b01-growmotion-b15-0819` is the control and it is an exact one.

WHY THIS RUNG AND NOT A SEED RE-ROLL -- the derived rung this lane was given
said "all fail on seed-sensitive bloom -> file one seed re-roll". All five DO
fail. They do not all fail on bloom, and the difference decides the job.

Scored 2026-08-20 with `pipeline/fig_track.py`, the geometry-anchored detector
(the colour predicate that manufactured b15's 3.9x balloon is retired):

  b10 20260835  FAIL G5   luma +71.07, 120/121 frames over 100
  b11 20260836  FAIL G5   luma +57.37, a clean 9.01x arc inside a blown field
  b12 20260837  FAIL H6   the location changes by f024; shaft NCC 0.145
  b15 20260840  FAIL G5   THE MILDEST BLOOM OF THE FIVE, +17.45
  b16 20260841  FAIL H1   90% of growth by f061, then a static third

b15 is the one that matters. It clears every clause the bar has except one:
121/121 frames live, ZERO shrinking frames, max single-frame step 1.08x, 90% of
its growth still arriving at f111, ending deep purple at hue 301.6 -- and it
carries the SMALLEST field disturbance in the pool. A seed re-roll is a lottery
on the axis b15 already won. It cannot fix the axis b15 lost.

WHAT b15 LOST ON, MEASURED. Region NCC f000->f120, gain- and offset-invariant so
the exposure jump cannot fake it, against the INCUMBENT cold open (seed
20260826) on the same init and the same recipe as the in-pool control:

                       shaft   sapling   fig box   grass floor
    incumbent          0.932     0.637     0.023      0.323
    b15 (20260840)    -0.355     0.092     0.002      0.027

The incumbent holds the field and decorrelates only the fig box -- which is
exactly what the clause asks for, so it is ACHIEVABLE ON THIS RECIPE and this is
not a wish. b15 redraws everything. Its two leaves go from a sprout below the
grass tips at f000 to filling the upper half of the frame at f120; the stem
thickens and elongates; the grass thickens with it. The prompt already says the
nub is "the only thing in frame that moves" and the engine did it anyway.

THE EDIT, stated as the diff it is. The parent negative reads

    camera pan, camera tilt, zoom, dolly, push in, pull back, tripod, cut to
    another shot, scene change, different location, split screen, still image,
    freeze frame

Thirteen terms, and every one of them forbids the CAMERA or the CUT. Not one
forbids the SUBJECT from growing or the FIELD from brightening. b15 obeyed all
thirteen -- there is no proven camera push in it, see below -- and failed on the
two things nothing in the list mentioned. The child appends:

    growing plant, sprouting, unfurling leaves, stem lengthening, leaves
    enlarging, plant enlarging, blooming, brightening, exposure change,
    overexposed, blown highlights, changing background

Twelve terms added, none removed, and both groups serve the SAME clause: G5,
"only the fig moves". A growing sapling and a brightening field are one fault --
something other than the fig is changing -- so this is one variable aimed at one
clause, not two edits bundled. The negative goes from ~30 to ~48 tokens, well
inside the 77 the beat-08 lane measured crowding at on 2026-08-20, and that
measurement was on a POSITIVE prompt where the crowding cost was a dropped
subject; there is no subject here to drop.

WHAT IS DELIBERATELY NOT EDITED. The motion prompt does not change by one
character. It is the sentence that produced the best growth arc this beat has
ever measured and it already contains the correct instruction; the hypothesis
under test is that the instruction needs to be on the NEGATIVE side to bind, not
that it needs rewording. Rewording it would put the 19.37x arc at risk to test
something else. The seed does not change either, for the same reason and because
holding it is what makes b15 a frame-for-frame control.

TWO THINGS THIS RUNG MUST NOT BE READ AS CLAIMING.

  * NO CAMERA PUSH WAS EVER PROVEN on b15, and the anti-zoom terms stay only
    because removing them would be a second variable. The first fit said 1.5x on
    three of four quadrants; that was the search grid's edge. Re-run to 2.50 the
    same pair reads 2.20 whole-frame with quadrants [2.5, 2.5, 1.25, 1.55] --
    the top of the picture magnifying about twice as hard as the bottom, which
    is a locally-varying redraw and not a camera move. `global_zoom` now
    publishes `railed: true` rather than that number (fig_track.py 527c4b5f).
  * THE BLOOM IS STILL SEED-SENSITIVE and this rung does not claim to have
    explained it: 6x spread across five seeds of one recipe, +17.45 to +71.07,
    while the incumbent seed on the same init never exceeds luma 100 at all
    (+1.46 lifetime). If this child blooms like its parent, the negative-side
    hypothesis is dead for the exposure half and the next rung is plate-side.

The bar below is the parent's, clause for clause, with the two clauses this
round proved are the real gate written as NUMBERS instead of adjectives -- an
explicit whole-frame luma bound and an explicit field-stability bound, both
scored by instruments that exist today and both with the incumbent's measured
values as the reference. G3 and G4's "below the grass" are carried as the parent
wrote them but marked unscored, because this repo has no leaf counter and no
grass line and pretending otherwise is how the five went unjudged for a day.

$0 to file. ~12 minutes of GPU when the card takes it.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b01-growmotion-b15-0819.yaml"
NEW_ID = "ep2-b01-fignonly-s20260840-0820"
SEED = 20260840

PARENT_NEG = (
    "camera pan, camera tilt, zoom, dolly, push in, pull back, tripod, cut to another "
    "shot, scene change, different location, split screen, still image, freeze frame"
)
NEW_NEG = PARENT_NEG + (
    ", growing plant, sprouting, unfurling leaves, stem lengthening, leaves enlarging, "
    "plant enlarging, blooming, brightening, exposure change, overexposed, blown "
    "highlights, changing background"
)

BAR = {
    "carried_from": "pipeline/jobs/ep2-b01-growmotion-b15-0819.yaml, clause for clause",
    "how_it_is_judged": (
        "pipeline/fig_track.py --frames <dir> --anchor-mask "
        "anchor/b01-nubcomp-s20260826-mask.png, plus the region-NCC and whole-frame-luma "
        "probes recorded in the parent's verdict_this_job_measured. Judged on landing, "
        "not batched -- this is ONE sample of ONE recipe change under the one-sample rule."
    ),
    "G1_growth_by_a_continuous_path": (
        "SCORED. Detector live on every frame it scores; no single-frame area step at or "
        "above 2.0x; growth distributed rather than popped -- the frame reaching 90% of "
        "total growth must be at or after f060. Parent b15: 121/121 live, max step 1.08x, "
        "90% at f111. The INCUMBENT fails this clause at f009 and that is on the record."
    ),
    "G2_end_state_deep_purple_violet": (
        "SCORED, and it requires a LIVE f120. Fig hue at the last frame in 270-320 deg "
        "with saturation at or above 0.60. Parent b15: hue 301.6, sat 0.72. If the last "
        "frame is dead the clause is retracted, not guessed -- b16 is why this sentence "
        "exists: 55 dead frames, f098 reads amber, f120 looks purple, neither was scored."
    ),
    "G3_exactly_two_leaves_in_every_frame": (
        "CARRIED BUT NOT SCORED -- NO INSTRUMENT EXISTS. This repo has no leaf counter and "
        "a sampled look cannot certify a universal over 121 frames. Recorded as an eye "
        "note. Naming this is the point; it was scored by assumption before."
    ),
    "G4_no_size_doubling": (
        "SCORED on the reading ep2-b01-growmotion-b13-0819 settled and this lane did not "
        "move: maximum single-frame area ratio under 2.0x, not total growth. TENSION "
        "CARRIED FORWARD: that reading admits an unbounded total and b15 rode it to "
        "19.37x. Not changed here, because changing a settled clause in the same breath "
        "as scoring against it is how a bar stops meaning anything."
    ),
    "G4b_below_the_grass": (
        "CARRIED BUT NOT SCORED -- no grass line is defined in this spec or on the plate, "
        "so there is no threshold. Eye note only. If it is to become a bar someone must "
        "put a y-coordinate on the plate first."
    ),
    "G5a_field_stability_THE_NEW_EXPLICIT_CLAUSE": (
        "SCORED, and this is the clause that killed the best clip of the last round. "
        "Region NCC between f000 and f120 -- gain- and offset-invariant, so a global "
        "exposure change cannot fake it -- on four bands: shaft y0-350; sapling y430-740 "
        "x150-560; fig box y700-900 x230-450; grass floor y1000-1280. PASS requires "
        "sapling at or above 0.45 AND shaft at or above 0.70 AND grass floor at or above "
        "0.20, with the fig box BELOW 0.30 (the fig must be the thing that changed). "
        "Reference values, measured, not invented: the incumbent seed 20260826 on this "
        "same init reads 0.932 / 0.637 / 0.023 / 0.323 and would pass; parent b15 reads "
        "-0.355 / 0.092 / 0.002 / 0.027 and fails on three of the four."
    ),
    "G5b_camera_locked": (
        "CARRIED BUT NOT SCORED -- the instrument refuses. global_zoom fits one scale to "
        "the picture and refits it on four disjoint quadrants; disagreeing quadrants mean "
        "the picture is being redrawn and no scale may be quoted, and a fit that lands on "
        "the grid edge now publishes railed:true and is unquotable as well. Not one of "
        "the five 2026-08-20 clips was quadrant-consistent. Reported, never scored."
    ),
    "H_LUMA_BLOOM_THE_OTHER_NEW_EXPLICIT_CLAUSE": (
        "SCORED. Whole-frame mean luma, every frame, no fig mask involved so no part of "
        "it is retractable. FAIL if peak whole-frame luma exceeds f000 by more than 12.0 "
        "levels, or if more than 6 of 121 frames read above luma 100. Reference values, "
        "measured: incumbent +1.46 with 0 frames over 100 (passes with room); the five "
        "seeds run +17.45 (b15), +23.67, +44.17, +57.37, +71.07 with 71 to 120 frames "
        "over 100, and ALL FIVE FAIL THIS BOUND INCLUDING THE MILDEST. Correcting the "
        "2026-08-20 ladder while carrying it forward: it is not true that all five pass "
        "100 by f024 -- b15 sits at 99.58 at f024 and peaks 104.64 at f035."
    ),
    "H1_frozen": (
        "SCORED. FAIL if fig-box NCC to the final frame is at or above 0.80 by f060, "
        "i.e. the last half is a still. b16 reads 0.669 at f060 and 0.965 at f100."
    ),
    "H5_detach_or_teleport": (
        "SCORED by the detector's own jump gate, live per frame; plus the fig centroid "
        "must stay within 40 px of its f000 geometric anchor (785.1, 339.4) for the whole "
        "clip. Parent b15 moves 14 px across 121 frames and passes."
    ),
    "H6_scene_break": (
        "SCORED. FAIL if any consecutive whole-frame NCC drops below 0.80. b16 reads "
        "0.6415 at f001 and fails; b15 reads 0.9522 worst and passes."
    ),
    "conjunctive": (
        "A partial is a FAIL, as the parent said. Two clauses are unscored by declaration "
        "(G3, G4b) and one is unquotable by its own instrument (G5b); those three cannot "
        "produce a PASS and cannot produce a FAIL, and the verdict will say so out loud "
        "rather than let an absent key read as a clear one."
    ),
}

PRE_REGISTERED_FAIL_MODES = {
    "F1_the_negative_does_not_bind": (
        "The sapling grows anyway and the field still blooms: region NCC and luma land "
        "within noise of the parent's. Then negative-side conditioning does not reach "
        "this fault on this engine, the two candidate fixes left are plate-side (a plate "
        "whose sapling is already at final size, so there is nothing to grow) or a "
        "staged colour-only ramp, and NEITHER is licensed by this rung."
    ),
    "F2_it_binds_and_takes_the_fig_with_it": (
        "The field holds -- G5a and the luma bound pass -- and G1 collapses, because "
        "'growing' and 'enlarging' suppressed the one thing that was supposed to enlarge. "
        "This is the predicted cost and the most likely single outcome. It would make the "
        "clause boundary the finding: the engine cannot separate the fig from its plant "
        "by wording, and the split has to be made in the plate or in the compositor."
    ),
    "F3_it_binds_cleanly": (
        "Field holds AND the fig still ramps. This is the first clip in this beat's "
        "history to clear every scored clause, it becomes a veto-able steward pick for "
        "the cold open, and the swap into review/ep2-demo-0820 is proposed WITH pixels "
        "and with the incumbent's own G1 failure alongside it. Still not a taste verdict; "
        "R4 is the founder's."
    ),
    "F4_the_seed_does_not_reproduce": (
        "Same seed, same init, one prompt file changed, and the output differs "
        "structurally everywhere. Then b15 was never a control for anything, this whole "
        "family of one-variable rungs has been comparing noise, and that is worth knowing "
        "before another one is filed."
    ),
}

# `retoken` rewrites the parent id EVERYWHERE in the child, prose included, and it
# has to -- the payload dict keys are Windows paths built from it. So the four
# FRESH sentences must not spell the parent id out: the first draft's `success`
# came back reading "the same seed as ep2-b01-fignonly-s20260840-0820", i.e. the
# job citing itself as its own control. They say "the parent" and point at the
# `control` key, which is authored `extra` and survives intact.
PARENT_REF = "the parent named in `control` below"

# Two spellings of the same sentence: the FRESH keys get the one that names no
# id (so retoken cannot touch it), `extra` gets the one that names the parent.
VARIABLE = (
    "The ONLY difference from %s is the contents of b01-negative.txt: twelve terms "
    "appended, none removed. Same seed 20260840, same init, same motion prompt byte for "
    "byte, same steps, same flags, same 121 frames." % PARENT_REF
)
VARIABLE_NAMED = VARIABLE.replace(PARENT_REF, "ep2-b01-growmotion-b15-0819")


def main():
    force = "--force" in sys.argv
    child = derive_spec.derive(
        src=PARENT, new_id=NEW_ID,
        by="pipeline/derive_b01_fignonly_0820.py",
        fresh=dict(
            owner="the fig-detector judging lane, 2026-08-20",
            consumer=(
                "THE COLD OPEN OF EPISODE 2'S CUT, which currently holds "
                "01-cold-open-b01-nubgrow-crf10-s20260826-0819.mp4 and should not. That "
                "incumbent passed 7 of 7 on the colour predicate retired today; rescored "
                "on the geometry-anchored detector it reaches 90% of its growth by f009 "
                "and is visually static from f030, which is the G1 failure -- 'a fig "
                "appeared' rather than 'the fig grew' -- that G1 exists to catch. It also "
                "holds its field perfectly, which none of the five challengers do. This "
                "job asks whether one clip can do both. A PASS is a veto-able steward "
                "pick and a proposed swap, with pixels, under R4. A FAIL is consumed too: "
                "it says whether the fig and its plant are separable by wording at all, "
                "which decides whether the next move is plate-side or prompt-side."),
            success=(
                "ONE 704x1280 121-frame mp4 at 24 fps off the same init and the same seed "
                "20260840 as %s, differing from it in the "
                "contents of one payload file and nothing else, in which the whole-frame " % PARENT_REF +
                "luma peak stays within 12.0 levels of f000 with at most 6 frames over "
                "100, the sapling and shaft regions hold at region NCC 0.45 and 0.70 "
                "f000-to-f120 while the fig box falls below 0.30, and the fig still ramps "
                "by a continuous path to a deep purple-violet end state with no "
                "single-frame area step at or above 2.0x. %s Every threshold above is a "
                "value MEASURED on this init today -- the incumbent's for the field ones, "
                "the parent's for the growth ones -- and not a number chosen to be "
                "clearable. G3 and G4's 'below the grass' are carried unscored because no "
                "instrument for either exists in this repo." % VARIABLE),
            why=(
                "$0, ~12 minutes of GPU, no download, nothing to fetch. All five "
                "growmotion seeds were scored FAIL today against bars pre-registered "
                "before their renders, and the pool's structure is the finding: the "
                "recipe gives a locked field with a popped fig (the incumbent, seed "
                "20260826) or a real growth arc inside a moving field (b15, seed "
                "20260840), and no seed of six has given both. That is why this is not a "
                "seed re-roll -- a seventh seed re-runs a lottery whose two outcomes are "
                "both already in hand and both already fail. It changes instead the one "
                "thing the measurement names: b15 obeyed all thirteen negative terms and "
                "failed on the two faults none of them mentions. One variable, one "
                "sample, judged on landing before anything is scaled."),
        ),
        overrides={"payload:b01-negative.txt": NEW_NEG, "seed": SEED},
        # The second pair fixes a defect this family has carried all along: every
        # sibling publishes its mp4 as `...-s20260826.mp4` regardless of the seed it
        # actually ran, because the derive step never retokened `artifacts`. The
        # 2026-08-20 ladder found b13's manifest unverifiable by name for exactly this
        # reason and noted the five growmotion clips are indistinguishable by filename.
        # This child's output says which seed made it.
        retoken=[(os.path.basename(PARENT)[:-5], NEW_ID),
                 ("01-cold-open-LTX-nubgrow-b-s20260826",
                  "01-cold-open-LTX-fignonly-s20260840")],
        extra={
            "the_one_variable": VARIABLE_NAMED,
            "bar": BAR,
            "pre_registered_fail_modes": PRE_REGISTERED_FAIL_MODES,
            "control": (
                "ep2-b01-growmotion-b15-0819, frame for frame. Its verdict and every "
                "number this bar references are appended to that spec under "
                "verdict_this_job_measured."),
            "init_provenance": (
                "The shared beat-01 nub composite init, unchanged: the frame-1 plate that "
                "passed its bar 7 of 7 on 2026-08-18, with the small green nub inpainted "
                "at composite centre 405,750 (mask b01-nubcomp-s20260826-mask.png, "
                "832x1216, cover-cropped to 704x1280 -- centroid (785.1, 339.4)). That "
                "mask is also the detector's geometric anchor, so the judging instrument "
                "and the render start from the same object."),
            "failure_predicted_in_advance": (
                "F2 is the most likely single outcome: the negative binds and takes the "
                "fig with it, because 'growing', 'enlarging' and 'blooming' do not know "
                "that the fig is exempt. It is named here before the render so that a "
                "collapsed arc reads as the predicted cost of a fair test and not as a "
                "surprise to be explained away afterwards."),
            "script_authority_note": (
                "Node 002b-first-citizen, approved_by: founder, approved_on: 2026-08-03. "
                "The motion prompt is unchanged from the parent and is the script's own "
                "cold-open sentence. Sidecar stamps approved: false / provisional: true. "
                "Silent, $0, no voice synthesis, no episode assembly. Nothing enters the "
                "cut without the founder's eye under R4."),
        },
    )
    out = "pipeline/jobs/%s.yaml" % NEW_ID
    print(derive_spec.write(child, out, force=force))


if __name__ == "__main__":
    main()
