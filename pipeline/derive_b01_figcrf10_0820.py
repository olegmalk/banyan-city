#!/usr/bin/env python3
"""Beat 01's G5a rung: the one clip that ever held its field is the one with a clean init.

ONE VARIABLE, and it is `--image-crf`: 33 -> 10. Same seed 20260840, same init PNG,
same negative (with the twelve exposure terms this family earned today), same motion
prompt byte for byte, same every other flag, same 121 frames.
`ep2-b01-fignonly-s20260840-0820` is the control and it is an exact one.

WHY THIS VARIABLE, AND IT WAS SITTING IN THE ARGV THE WHOLE TIME.

`--image-crf N` round-trips the conditioning still through libx264 at CRF N before
it is used as the init. It is this pipeline's conditioning-strength knob under
another name: a low CRF hands the model a near-clean anchor, a high one hands it a
mushy anchor it is free to reinvent around.

Seven beat-01 clips have now been scored on the geometry-anchored detector. Exactly
ONE holds its field, and it is the only one that was rendered at crf 10:

  clip                          --image-crf   sapling NCC f000->f120   luma delta
  incumbent  s20260826            **10**            **0.637**            **+1.46**
  b10        s20260835              33               0.144               +71.07
  b11        s20260836              33               0.126               +57.37
  b12        s20260837              33              -0.195               +44.17
  b15        s20260840              33               0.092               +17.45
  b16        s20260841              33              -0.174               +23.67
  fignonly   s20260840              33               0.055               +10.85

Six clips at crf 33 land between -0.195 and 0.144 with no seed escaping the band.
One clip at crf 10 lands at 0.637 -- four times the best of them -- and is also the
only one whose whole-frame luma never leaves the plate. **The band is tight and the
outlier is the one with a different conditioning image, not a different seed.**

THE CONFOUND IS REAL AND IT IS THE REASON THIS IS WORTH A FIRE. The crf-10 clip is
also the only one at seed 20260826, so across the existing pool crf and seed are
perfectly confounded and NOTHING in hand separates them. This rung separates them by
holding the seed and moving only the crf. Whatever it returns is informative:

  * field holds  -> crf was the cause, seed was never the story, and six seeds of
                    lottery were spent on the wrong axis;
  * field moves  -> crf was not the cause, the incumbent's stability belongs to its
                    seed after all, and the localisation route is the one left.

WHY NOT THE TWO ROUTES THE LAST VERDICT NAMED. It left "plate-side or
compositor-side" open. Plate-side -- an init whose sapling is already at final size
-- is aimed at a cause the evidence does not establish: **the same plate produced a
held sapling under the incumbent**, so the plate is not indicted, and the change
would throw away a plate that passed its bar 7 of 7. Compositor-side is real but it
is a bigger commitment (it makes the background a still), it needs no GPU, and it
should not be spent before the cheap in-pipeline knob that the measurement actually
points at has been tried once. This rung is 12 GPU-minutes and it is the last
prompt/flag-level question beat 01 has.

WHAT IS DELIBERATELY NOT EDITED. The negative keeps all twelve exposure terms. They
are earned -- they took the bloom from +17.45 to +10.85 and from 71 frames over luma
100 to zero, and cost the fig nothing measurable -- and removing them would be a
second variable. The six plant-growth terms also stay, byte for byte, even though
the last rung measured them inert: deleting them now would confound this test with
their removal. They are dead weight carried on purpose so the control is exact.

$0 to file. ~12 minutes of GPU.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

PARENT = "pipeline/jobs/ep2-b01-fignonly-s20260840-0820.yaml"
NEW_ID = "ep2-b01-figcrf10-s20260840-0820"
SEED = 20260840

PARENT_REF = "the parent named in `control` below"
VARIABLE = ("The ONLY difference from %s is `--image-crf`, 33 -> 10, in the render step's "
            "argv. Same seed 20260840, same init PNG, same negative and same motion prompt "
            "byte for byte, same every other flag, same 121 frames." % PARENT_REF)
VARIABLE_NAMED = VARIABLE.replace(PARENT_REF, "ep2-b01-fignonly-s20260840-0820")

BAR = {
    "carried_from": ("pipeline/jobs/ep2-b01-fignonly-s20260840-0820.yaml, clause for clause and "
                     "threshold for threshold. Not one number is relaxed for this rung."),
    "how_it_is_judged": (
        "pipeline/fig_track.py (geometry-anchored, selftest 15/15) against anchor mask "
        "b01-nubcomp-s20260826-mask.png, plus the region-NCC and whole-frame-luma probes. ONE "
        "sample of ONE recipe change, judged on landing, not batched."),
    "G1_growth_by_a_continuous_path": (
        "SCORED. Detector live on every frame it scores; no single-frame area step at or above "
        "2.0x; the frame reaching 90% of total growth at or after f060. Control: 121/121 live, "
        "1.084x, f108. THE INCUMBENT FAILS THIS AT f009 AND THAT IS THE WHOLE RISK OF THIS RUNG "
        "-- see H1_ALSO_THE_PREDICTED_COST."),
    "G2_end_state_deep_purple_violet": (
        "SCORED, and requires a LIVE final frame: fig hue 270-320 deg, saturation >= 0.60. "
        "Control: hue 293.9, sat 0.788. A dead last frame retracts the clause, never guesses it."),
    "G3_exactly_two_leaves_in_every_frame": (
        "CARRIED BUT NOT SCORED -- no leaf counter exists in this repo and a sampled look cannot "
        "certify a universal over 121 frames. Eye note only."),
    "G4_no_size_doubling": (
        "SCORED on b13's settled reading: maximum single-frame area ratio under 2.0x, not total "
        "growth. Control: 1.084x."),
    "G4b_below_the_grass": (
        "CARRIED BUT NOT SCORED -- no grass line is defined on the plate or in any spec, so there "
        "is no threshold to measure against. Eye note only."),
    "G5a_field_stability_THE_CLAUSE_THIS_RUNG_EXISTS_FOR": (
        "SCORED. Region NCC between f000 and the last frame -- gain- and offset-invariant, so an "
        "exposure change cannot fake it -- on four bands: shaft y0-350; sapling y430-740 x150-560; "
        "fig box y700-900 x230-450; grass floor y1000-1280. PASS requires sapling >= 0.45 AND "
        "shaft >= 0.70 AND grass >= 0.20, with fig box < 0.30 so that the fig is the thing that "
        "changed. Control fails at sapling 0.055 / shaft -0.324 / grass 0.038. The crf-10 "
        "incumbent reads 0.637 / 0.932 / 0.323 and would pass all three."),
    "G5b_camera_locked": (
        "CARRIED BUT NOT SCORED -- global_zoom refuses: disagreeing quadrants mean the picture is "
        "redrawn rather than moved, and a fit on the grid edge publishes railed:true. Neither is "
        "quotable. Reported, never scored."),
    "H_luma_bloom": (
        "SCORED. Peak whole-frame luma within 12.0 levels of f000, and at most 6 of 121 frames "
        "above luma 100. Control PASSES at +10.85 / 0 frames, and this rung must not lose that."),
    "H1_frozen_ALSO_THE_PREDICTED_COST": (
        "SCORED. FAIL if fig-box NCC to the final frame is at or above 0.80 by f060. Control: "
        "-0.127. This is the clause most likely to break: the crf-10 incumbent is frozen from "
        "f030 and reaches 90% of its growth by f009."),
    "H5_detach_or_teleport": (
        "SCORED by the detector's jump gate plus a 40 px bound on the fig centroid against the "
        "f000 geometric anchor (785.1, 339.4). Control: 20.6 px."),
    "H6_scene_break": "SCORED. FAIL if any consecutive whole-frame NCC drops below 0.80.",
    "conjunctive": (
        "A partial is a FAIL. Three clauses are unscored by declaration (G3, G4b, G5b); they can "
        "produce neither a PASS nor a FAIL and the verdict will say so out loud rather than let an "
        "absent key read as a clear one."),
}

PRE_REGISTERED_FAIL_MODES = {
    "F1_the_field_holds_and_the_fig_keeps_its_arc": (
        "G5a passes and G1/H1 hold. Then crf was the cause all along, the seed lottery was run on "
        "the wrong axis for six fires, and this is the first beat-01 clip to clear every scored "
        "clause -- a veto-able steward pick proposed WITH pixels under R4."),
    "F2_the_field_holds_and_the_fig_pops": (
        "G5a passes, H1 or G1 fails -- the clip becomes an incumbent-shaped result at a new seed. "
        "This is the most likely single outcome and it is the informative one: it would show "
        "field stability and fig growth are ONE knob on this engine, not two, and that no "
        "conditioning setting separates them. The route then is localisation "
        "(compositor-side: grow the fig against a held plate, using this detector's own per-frame "
        "masks, which already exist and are validated), and NOT another flag sweep."),
    "F3_nothing_changes": (
        "Region NCC and luma land within noise of the control. Then --image-crf does not reach "
        "this behaviour at all, the incumbent's stability belongs to its SEED after all, and the "
        "confound resolves the other way. Cheap to learn and it closes the flag route."),
    "F4_the_cleaner_init_changes_the_look": (
        "crf 10 alters grain, colour or contrast enough that the clip no longer matches the "
        "plate the other twenty beats were cut against. Watch for it; it is a taste question, it "
        "is the founder's under R4, and it is not scored by any clause above."),
}


def main():
    force = "--force" in sys.argv
    child = derive_spec.derive(
        src=PARENT, new_id=NEW_ID,
        by="pipeline/derive_b01_figcrf10_0820.py",
        fresh=dict(
            owner="the fig-detector judging lane, 2026-08-20",
            consumer=(
                "THE COLD OPEN OF EPISODE 2'S CUT, which as of this filing holds the parent clip "
                "as a best-available steward pick with G5a failing and named. This rung is the "
                "one remaining flag-level attempt to close G5a. A PASS makes beat 01 the first "
                "clip in its history to clear every scored clause and is proposed as a swap with "
                "pixels under R4; a FAIL is consumed too, because it separates a confound that "
                "six seed fires never touched and decides whether the route is localisation."),
            success=(
                "ONE 704x1280 121-frame mp4 at 24 fps off the same init and the same seed 20260840 "
                "as %s, differing from it in a single argv value and nothing else, in which the "
                "sapling and shaft regions hold at region NCC 0.45 and 0.70 from f000 to the last "
                "frame while the fig box stays below 0.30, AND the fig still ramps by a continuous "
                "path -- 90%% of its growth at or after f060, no single-frame step at or above "
                "2.0x -- to a deep purple-violet end state, AND the whole-frame luma peak stays "
                "within 12.0 levels of f000 with at most 6 frames over 100. %s Every threshold is "
                "carried unchanged from the control's own bar; none was relaxed to make this "
                "clearable, and two of them (G1, H luma) are clauses the control already passes "
                "and this rung must not lose." % (PARENT_REF, VARIABLE)),
            why=(
                "$0, ~12 minutes of GPU, no download. Seven beat-01 clips have been scored on the "
                "honest detector. Six of them ran --image-crf 33 and land in a tight band of "
                "-0.195 to 0.144 on sapling region NCC, no seed escaping it. The seventh ran "
                "--image-crf 10 and lands at 0.637, four times the best of them, and is also the "
                "only clip whose whole-frame luma never leaves the plate. --image-crf round-trips "
                "the conditioning still through libx264 before it is used as the init, so it is "
                "this pipeline's conditioning-strength knob under another name. It is also "
                "perfectly confounded with seed across the existing pool, and nothing in hand "
                "separates them. Holding the seed and moving only the crf separates them in one "
                "fire, and both outcomes are worth having."),
        ),
        overrides={"argv:--image-crf": "10", "seed": SEED},
        retoken=[(os.path.basename(PARENT)[:-5], NEW_ID),
                 ("01-cold-open-LTX-fignonly-s20260840",
                  "01-cold-open-LTX-figcrf10-s20260840")],
        extra={
            "the_one_variable": VARIABLE_NAMED,
            "bar": BAR,
            "pre_registered_fail_modes": PRE_REGISTERED_FAIL_MODES,
            "control": (
                "ep2-b01-fignonly-s20260840-0820, frame for frame -- same seed, same init, same "
                "prompts. Its verdict and every threshold this bar quotes are appended to that "
                "spec under verdict_this_job_measured. That clip is IN THE CUT as of 2026-08-20 "
                "as a best-available steward pick with G5a failing and named, so this rung's "
                "control is also its incumbent."),
            "the_confound_this_rung_separates": (
                "Across the seven scored beat-01 clips, --image-crf 10 occurs exactly once and "
                "seed 20260826 occurs exactly once, on the same clip. Every conclusion drawn from "
                "that clip's field stability -- including this lane's own 'the clause is "
                "achievable on this recipe' -- rests on a pair of variables that have never been "
                "moved independently. This is the experiment that moves one of them."),
            "init_provenance": (
                "Unchanged from the control: the shared beat-01 nub composite init, the frame-1 "
                "plate that passed its bar 7 of 7 on 2026-08-18, nub inpainted at composite "
                "centre 405,750 (mask b01-nubcomp-s20260826-mask.png, 832x1216, cover-cropped to "
                "704x1280, centroid (785.1, 339.4)). That mask is also the detector's geometric "
                "anchor, so the judging instrument and the render start from the same object. "
                "NOTE: --image-crf does not change this PNG; it changes the libx264 round-trip "
                "applied to it before conditioning."),
            "failure_predicted_in_advance": (
                "F2 is the likeliest: the field holds and the fig pops, because the crf-10 clip "
                "in hand is frozen from f030. Named before the render so that a popped arc reads "
                "as the predicted cost of a fair test rather than a surprise, and so that the "
                "conclusion it licenses -- localisation, not another flag sweep -- is on record "
                "before the pixels are seen."),
            "script_authority_note": (
                "Node 002b-first-citizen, approved_by: founder, approved_on: 2026-08-03. Motion "
                "prompt unchanged from the control and unchanged from the original cold-open "
                "sentence. Sidecar stamps approved: false / provisional: true. Silent, $0, no "
                "voice synthesis, no episode assembly. Nothing enters the cut without R4."),
        },
    )
    out = "pipeline/jobs/%s.yaml" % NEW_ID
    print(derive_spec.write(child, out, force=force))


if __name__ == "__main__":
    main()
