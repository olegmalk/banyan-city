#!/usr/bin/env python3
"""PRE-STAGED. Fires on the founder answering "B" to /review/ep2-b13-shade-0820.

Until then this file is WRITTEN AND NOT RUN, and running it writes a spec that
is still not enqueued. Nothing here touches a GPU.

WHAT IT EMITS
-------------
`pipeline/jobs/ep2-b13-tallmotion-0820.yaml` -- beat 13's motion rung 5, which is
rung 4 (`ep2-b13-shadelit-0820`) with ONE VARIABLE CHANGED: the init is the
TALLER-THAN-CANON plate instead of the canon-height one. Same words, same seed,
same mask geometry, same crop, same recipe. Rung 4 is therefore a true control
and that is the entire reason nothing else may be touched in passing.

WHY THE LIFT STEP IS NOT OPTIONAL
---------------------------------
Rung 4's init is the rung-3 sample put through `beat13_exposure_lift.py` at
k = 2.0. If the tall sample skipped that curve, rung 5 would differ from rung 4
in TWO things -- plant height and plate tone -- and the comparison would be
measuring the curve instead of the plant. So this script refuses to run until
the lifted tall plate exists, and prints the exact command that makes it.

WHY THE SHA IS COMPUTED HERE AND NOT TYPED
------------------------------------------
The plate this depends on does not exist yet at the time this file is written.
A pre-staged spec carrying a guessed sha is a job that fails on the box; a
pre-staged spec carrying no sha is a job that renders the wrong pixels. So the
sha is read off the file at emit time, and if the file is missing this stops
with the command that produces it rather than inventing anything.

AFTER IT RUNS, and only after the author has said B:
  1. add the one-shot height exception to pipeline/canon.yaml AS an exception
     (see this directory's README -- canon first, always, because
     check_canon_drift.py reads canon and not review cards)
  2. commit and PUSH the lifted plate -- the box fetches it by raw URL under the
     sha this script asserts
  3. python3 pipeline/box_enqueue.py pipeline/jobs/ep2-b13-tallmotion-0820.yaml

Run:  python3 pipeline/decisions-pending/ep2-b13-shade-0820/derive-b13-tallmotion.py [--force]
$0. Writes ONE spec file and nothing else.
"""
import glob
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))
import derive_spec  # noqa: E402

SEED = 20260820
PARENT = "pipeline/jobs/ep2-b13-shadelit-0820.yaml"
NEW_ID = "ep2-b13-tallmotion-0820"
OLD_BASE = "13-the-shade-LTX-lit-0820"
NEW_BASE = "13-the-shade-LTX-tall-0820"
OLD_BENCH = "bench-b13-shadelit"
NEW_BENCH = "bench-b13-tallmotion"

TALLDIR = os.path.join(REPO, "farm-out", "ep2-b13-tallcomp-0820")
OLD_PLATE = "b13-sapcomp-lit-0820.png"
OLD_SHA = "f63c61f4588568544a97cd15dec3c63663e3fb51425f1735bc0d38e78a878576"
NEW_PLATE = "b13-tallcomp-lit-0820.png"
LIFTED = os.path.join(TALLDIR, NEW_PLATE)

VARIABLE = (
    "WHICH PNG THE COVER-CROP READS, AND NOTHING ELSE. Rung 4's plate is the "
    "canon-height sapling composited beside him at knee height and finished by a "
    "0.30 pass; this one is the SAME plate, the SAME 0.30 recipe and the SAME "
    "k=2.0 exposure curve, with the drawn plant ~921 px instead of ~485 px -- "
    "~48.7 cm against canon's ~40 cm, its blades on his EYE LINE instead of below "
    "his knee line. The prompt, the negative, the seed, the mask geometry, the "
    "crop size, the crop anchor, the frame count and every render flag are rung "
    "4's byte for byte.")

WHY_THIS_EXISTS = (
    "THE AUTHOR RULED. Beat 13's G8 clause -- the plant's shade on his eyes -- "
    "failed four times, and the write-up closed the route in this repo's own "
    "files: raising the plant was refused by the composite tool's own guard, "
    "lowering his head is a new posed plate, and underneath both sat a question "
    "only the author could answer. He answered it: the plant may be drawn taller "
    "than canon in this one shot. This rung spends that ruling once, on the "
    "cheapest possible test of it -- one variable, against a control that already "
    "exists.")

BAR = {
    "G8_THE_PLANTS_SHADE_IS_ON_HIS_EYES": (
        "SCORED BY EYE AT 4x AND BY NO NUMBER, AND THE REASON IS PUBLISHED "
        "RATHER THAN ASSUMED. This clause's pre-registered numeric instrument "
        "was RETRACTED by its own author on rung 4: it passes hugely on the very "
        "clip it was written to reject (eye band 102.6 below the forehead band "
        "where the bar asked for 15, and 95.1 below on the control), because "
        "when the head tips over neither fixed box is on the thing it names any "
        "more -- both read std 88-89 at f120. THAT INSTRUMENT MUST NOT BE "
        "RE-RUN, and a new fixed-box version of it must not be written: this "
        "repo has now retracted the fixed-window failure four times. What a PASS "
        "looks like: at f120, opened at 4x, a distinct darker patch lying across "
        "his eye band with a visible EDGE that can be TRACED TO THE PLANT -- not "
        "his own brow, arm or knee shadow. The whole point of the card was that "
        "this is a look, not a measurement."),
    "H1_THE_PERFORMANCE_IS_NOT_GIVEN_BACK": (
        "Face band (250,240,400,360), the same fixed band as rungs 1-4, mean "
        "absolute interframe luma over all 120 pairs, and the last twenty pairs. "
        "RUNG 4 IS THE NUMBER TO BEAT: 2.885 mean (which missed the 3.0 bar by "
        "0.115, with F-MOTION-COST not firing) and 3.240 over the last twenty. "
        "Published with its SHAPE and not as a bare mean -- this family holds "
        "every 3rd frame, so a clip reading period 1 where its siblings read "
        "period 3 has a CUT in it and its hold statistics are retracted."),
    "H2_he_is_still_seated_knees_up_and_the_plant_holds": (
        "Carried from rung 4, which passed it. At f120 he is folded small with "
        "his knees up; the plant is ONE stem with TWO leaves, rooted, at f000 "
        "f030 f060 f090 f120. THE PLANT CLAUSE IS THE ONE AT REAL RISK HERE and "
        "it is why this rung is worth running even if G8 fails again: the "
        "composited sapling has survived 121 frames at 4.1% of frame, and this "
        "asks it to survive at roughly double that, taller, thinner, and against "
        "sky and background foliage rather than grass."),
    "H3_the_sideways_tilt_survives": (
        "Carried. Upright and facing camera at f000, over on its side by f090, "
        "face rotated back toward camera at f120. Judged 1:1 beside rung 4 rather "
        "than against a memory of it."),
    "A5_no_exposure_blowout_MEASURED_AGAINST_THIS_JOBS_OWN_f000": (
        "f000 to f120 whole-frame mean luma within +/-25, scored against THIS "
        "job's f000 and never against rung 4's. Rung 4 ran -0.29 across 121 "
        "frames, the flattest of the six, and that is the number to beat."),
    "A2_the_ratified_adult_holds": (
        "Carried from rung 4 with its probe box unmoved. Publish luma_std with "
        "every reading: an inflated dispersion means the box is straddling an "
        "edge, not that the subject changed, and beat 13's own rung 3 went 6.0 -> "
        "85.0 -> 56.6 as the head tipped out from under it."),
}

FAIL_MODES = [
    "F-THE-SHADE-STILL-DOES-NOT-LAND -- G8 fails a fifth time even with the "
    "plant at his eye line. NAMED AS A REAL POSSIBILITY RATHER THAN A REMOTE "
    "ONE, and the mechanism is already visible in the still: the light axis on "
    "this plate is (0.15, -0.988), i.e. very nearly straight down in image "
    "space, so a blade BESIDE his eyes casts almost straight down PAST his face "
    "rather than across it. Getting the shade onto the face may need the plant "
    "leaning over him, which is a different staging and a different question. If "
    "this fires, the honest report is that the beat is not filmable at this "
    "FRAMING and the remaining lever is a re-posed plate -- authored work, and "
    "the author's.",
    "F-BLADES-READ-AS-ONE-LOBED-MASS -- the two cotyledons come out as a single "
    "clover or balloon rather than as two leaves, breaking H2's plant clause. "
    "PRE-REGISTERED BECAUSE IT IS ALREADY VISIBLE IN THE COMPOSITE: the frame "
    "gave the plant a 248 px corridor between the left edge and his face box, "
    "which forced the blade axis to +-70 deg, and at that angle they cross.",
    "F-LOLLIPOP -- a 921 px plant carries a long thin stem, and beat 13's own "
    "compositor docstring records a straight stem being rejected by eye as a "
    "lollipop before the default's bow was added. The bow is carried and scaled, "
    "but at double the height it may not be enough.",
    "F-PLANT-DISSOLVES-UNDER-MOTION -- the composited plant has held 121 frames "
    "at 4.1% of frame on beats 03 and 13, including green-on-green at the lowest "
    "object-to-ground contrast this house has attempted. At ~8% and against sky "
    "it is a genuinely new test, and beat 09's clip this week showed the softest "
    "object in a frame dissolving over eight frames while everything else held.",
    "F-MOTION-COST -- H1 regresses below rung 4's 2.885. A different init is a "
    "different conditioning image and this box has measured a cleaner init "
    "costing beat 18 ~90% of its interframe motion.",
]

NOT_DONE = (
    "NO WORDING CHANGE OF ANY KIND -- the prompt and the negative are rung 4's "
    "byte for byte. Wording was exonerated on this beat by rung 3's own "
    "pre-registered test and a fifth wording would be the ladder this repo "
    "forbids; the negative also sits near the 77-token ceiling, where any added "
    "word silently drops the tail. NO recipe change: size, frames, fps, "
    "guidance, distilled sigmas, two-stage, offload, mode and --image-crf 10 are "
    "the b14 crf-10 parent's. NO new seed: 20260820 for the fifth time. NO new "
    "anchor -- LEFT, as rungs 3 and 4. NO second variable of any kind: the "
    "exposure curve is the SAME k=2.0 applied to the SAME curve by the SAME "
    "tool, which is why this script refuses to run against an unlifted plate. "
    "NO CUT SWAP AND NO PICK. The author's ruling licenses the STAGING, not the "
    "take; this clip still has to pass the bars above on its own, and it "
    "inherits the plate's cast frame for frame.")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    force = "--force" in sys.argv

    if not os.path.isfile(LIFTED):
        samples = sorted(
            p for p in glob.glob(os.path.join(TALLDIR, "*.png"))
            if "mask" not in os.path.basename(p)
            and "tallcomp-0820.png" not in os.path.basename(p))
        hint = samples[0] if samples else os.path.join(
            TALLDIR, "<the landed 0.30 sample>.png")
        raise SystemExit(
            "!! %s does not exist, so there is no plate to assert a sha for.\n"
            "   The tall sample has to travel the SAME tone curve as rung 4 or "
            "this stops being a one-variable rung. Run:\n\n"
            "     python3 pipeline/beat13_exposure_lift.py --k 2.0 \\\n"
            "       --src %s \\\n"
            "       --out %s\n\n"
            "   then LOOK at it, then run this again."
            % (os.path.relpath(LIFTED, REPO), os.path.relpath(hint, REPO),
               os.path.relpath(LIFTED, REPO)))

    new_sha = sha256(LIFTED)
    parent = derive_spec.load(os.path.join(REPO, PARENT))

    fkey = [k for k in parent["payload"] if k.endswith("fetch_init.py")][0]
    fetch = parent["payload"][fkey]
    for old, new in ((os.path.basename(PARENT)[:-5], NEW_ID),
                     (OLD_BASE, NEW_BASE), (OLD_BENCH, NEW_BENCH)):
        fetch = fetch.replace(old, new)
    if fetch.count(OLD_PLATE) != 1 or fetch.count(OLD_SHA) != 1:
        raise SystemExit(
            "!! expected exactly one mention of the plate name and one of its "
            "sha in fetch_init.py; found %d and %d. REFUSING to guess -- rung 4's "
            "spec has changed shape since this was pre-staged and a human should "
            "look at it." % (fetch.count(OLD_PLATE), fetch.count(OLD_SHA)))
    fetch = fetch.replace(OLD_PLATE, NEW_PLATE).replace(OLD_SHA, new_sha)
    fetch = fetch.replace("ep2-b13-sapcomp-0820", "ep2-b13-tallcomp-0820")

    child = derive_spec.derive(
        src=PARENT, new_id=NEW_ID,
        by="pipeline/decisions-pending/ep2-b13-shade-0820/derive-b13-tallmotion.py",
        fresh=dict(
            owner=("the beat 13 lane, firing the founder's B ruling on "
                   "/review/ep2-b13-shade-0820"),
            consumer=(
                "The episode 2 cut, beat 13, which currently carries rung 4 as "
                "best-available with its G8 fault named. If this rung puts a "
                "traceable patch of the plant's shade on his eyes without giving "
                "back rung 4's performance, beat 13 closes on its own clause "
                "instead of on a waiver. If it does not, the beat is not "
                "filmable at this FRAMING and that is the finding."),
            success=(
                "ONE 704x1280 121-frame mp4 off the SAME WORDS, the same seed and "
                "the same mask as ep2-b13-shadelit-0820, conditioned on the "
                "taller-than-canon plate the author licensed, in which the "
                "plant's shade reads on his eyes at f120 WITHOUT costing H1, H2, "
                "H3 or A5. %s" % VARIABLE),
            why=WHY_THIS_EXISTS,
        ),
        overrides={
            "payload:fetch_init.py": fetch,
            "argv:--src": (r"C:\banyan-farm\courier-box\farm-out"
                           r"\ep2-b13-tallcomp-0820\%s" % NEW_PLATE),
            "argv:--sha256": new_sha,
            "seed": SEED,
        },
        retoken=[(os.path.basename(PARENT)[:-5], NEW_ID),
                 (OLD_BASE, NEW_BASE), (OLD_BENCH, NEW_BENCH)],
        extra={
            "the_one_variable": VARIABLE,
            "rung_4_the_control": (
                "ep2-b13-shadelit-0820: G8 FAIL (by eye; its instrument "
                "retracted), H1 2.885 mean / 3.240 last-twenty, H2 PASS, H3 "
                "PASS, A5 -0.29, A2 PASS. Four of five, and the one that failed "
                "is the one this rung exists for."),
            "bar": BAR,
            "not_done_on_purpose": NOT_DONE,
            "pre_registered_fail_modes": FAIL_MODES,
            "is_show_content": False,
            "why_is_show_content_false": (
                "The author's B ruling licenses the STAGING -- a one-shot "
                "exception to the ~40 cm rule, recorded in pipeline/canon.yaml AS "
                "an exception. It is not a licence for this take to enter the "
                "cut. Passing the bar you were given is not a licence to enter a "
                "cut on a different bar, and this clip inherits its plate's cast "
                "frame for frame. Any promotion is a separate pick."),
            "the_ruling_this_spends": (
                "Founder, on /review/ep2-b13-shade-0820: answer B, 'draw it "
                "taller in this one shot'. The card carried both answers as "
                "pixels -- rung 4's frames for A, and the "
                "beat13_shade_composite.py --founder-option composite plus its "
                "0.30 sample for B. The exception belongs in canon.yaml scoped to "
                "beat 13 of node 002b with the ruling date, and the general rule "
                "(~40 cm, always shorter than he is, in every beat of 002b) "
                "stands untouched everywhere else."),
            "provenance_of_the_init": {
                "plate": ("farm-out/ep2-b13-mac-plate-0819/"
                          "13-the-shade-mac-plate-r1s1.png"),
                "composite": ("pipeline/beat13_shade_composite.py "
                              "--founder-option -> farm-out/ep2-b13-tallcomp-0820/"
                              "13-the-shade-tallcomp-0820.png"),
                "sample": "ep2-b13-tallcomp-0820, 0.30, 40 steps, cfg 7.5, seed 20260820",
                "lift": ("pipeline/beat13_exposure_lift.py --k 2.0, the identical "
                         "curve rung 4's plate travelled"),
                "lifted_sha256": new_sha,
            },
        })

    out = os.path.join("pipeline", "jobs", "%s.yaml" % NEW_ID)
    print("lifted tall plate %s" % os.path.relpath(LIFTED, REPO))
    print("  sha256 %s" % new_sha)
    print(derive_spec.write(child, out, force=force))
    print("\nNOT ENQUEUED. Commit and PUSH the lifted plate first -- the box "
          "fetches it by raw URL under the sha above -- then:")
    print("  python3 pipeline/box_enqueue.py %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
