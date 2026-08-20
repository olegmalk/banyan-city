#!/usr/bin/env python3
"""BEAT 13'S PLATE-EXPOSURE RUNG: the same words on a lifted plate.

ONE VARIABLE, AND IT IS NOT A WORD. The prompt, the negative, the seed, the
mask, the crop size, the crop anchor, the frame count and every render flag are
ep2-b13-shademid-0820's, byte for byte. The only difference is which PNG the
cover-crop reads: `b13-sapcomp-lit-0820.png` instead of
`b13-sapcomp-s20260820.png`, the same pixels through
`y = k*x/(1+(k-1)*x)` at k = 2.0 on linear light. See
pipeline/beat13_exposure_lift.py for the curve, the sweep and the reason it is
an exposure gain with a shoulder rather than a gamma.

WHY THIS RUNG IS EARNED RATHER THAN ASSERTED. shademid pre-registered the test
in its own bar before its pixels existed: *if H1 passes -- a clip that is
demonstrably moving -- and G8 still fails, the wording is exonerated and the
next rung is the plate.* H1 passed by a factor of seven over rung 2 (face-band
mean absolute interframe 10.80 -> 0.64 -> 4.798) and H3's sideways tilt passed
decisively, and G8 failed for the third time. Three rungs have moved the face
band and the tilt and not one has put light on his eyes.

THE MECHANICAL ARGUMENT, measured on the plate before this spec existed. In this
dialect an ordinary cel shadow terminator is a step of about 24 luma. On the
plate as it is, his cheek reads 114.6 and the whole frame's median is 89.5, so a
shade drawn on his face lands at ~90.6 -- the frame's own median. IT WOULD READ
AS MORE MURK, NOT AS A SHADE. Lifted, the cheek reads 146.4 against a median of
118.1, and a one-step shade lands at ~122, a clear step above the field. The
lift also GROWS the face-to-field separation (25.1 -> 28.3) where a gamma would
have shrunk it.

AND THE OBJECTION, PRE-REGISTERED AS THE MOST LIKELY FAILURE. "Beat 13's plate is
the dim one" is true of the FIELD and false of the FACE. Cropped-init whole-frame
median luma: b13 89.5, b03 181.7, b15 202.4. Cheek probe, same instrument on all
three: b13 114.6, b03 101.8, b15 93.3. Beat 13 already had the BRIGHTEST face and
the darkest field of the three plates, so an exposure lift may simply be aimed at
the wrong pixels -- and the geometric objection underneath it is worse: at f120
his eyes are at y~400-560 and the seedling's 60px leaves are at y~690-780, BELOW
him, so there is no light direction on this plate under which a 15cm plant casts
anything onto a face 300px above it. If G8 fails again here, exposure joins
wording as an exonerated suspect and beat 13's remaining lever is FRAMING -- the
head and the leaves in one register -- which is a composite geometry rung and not
a plate-tone one.

$0. Writes ONE spec file and nothing else. The lifted plate must already exist
and be committed and PUSHED: the job fetches it by raw URL under the sha
asserted below.
Run:  python3 pipeline/derive_b13_shadelit_0820.py [--force]
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 20260820

PARENT = "pipeline/jobs/ep2-b13-shademid-0820.yaml"
NEW_ID = "ep2-b13-shadelit-0820"
OLD_BASE = "13-the-shade-LTX-midend-0820"
NEW_BASE = "13-the-shade-LTX-lit-0820"
OLD_BENCH = "bench-b13-shademid"
NEW_BENCH = "bench-b13-shadelit"

OLD_PLATE = "b13-sapcomp-s20260820.png"
NEW_PLATE = "b13-sapcomp-lit-0820.png"
OLD_SHA = "bb0ad70c4294aa1647a0db1567df30482c97780359adc799818ff1dd88e0f7b2"
LIFTED = os.path.join(REPO, "farm-out", "ep2-b13-sapcomp-0820", NEW_PLATE)

VARIABLE = (
    "WHICH PNG THE COVER-CROP READS, AND NOTHING ELSE. "
    "b13-sapcomp-s20260820.png becomes b13-sapcomp-lit-0820.png: the same "
    "832x1216 pixels through y = k*x/(1+(k-1)*x) on linear light at k = 2.0, a "
    "true exposure gain with a built-in shoulder (slope k at black, slope 1/k at "
    "white, 0 -> 0 and 1 -> 1 exactly, so it cannot clip -- asserted, 0 newly "
    "pure-white pixels). NO GEOMETRY CHANGE: same size, every pixel keeps its "
    "coordinates, so the published composite mask and assert_framing.py's "
    "pre-registered WANT_BBOX are both still valid and are carried unchanged. NO "
    "COLOUR CORRECTION: the curve runs per channel in linear light, which is what "
    "an exposure change physically is, and R-B is published before and after "
    "rather than steered. The PROMPT, the NEGATIVE, the seed 20260820, the crop "
    "size, the LEFT anchor, 121 frames, guidance 2.0, distilled sigmas, "
    "two-stage, sequential offload and --image-crf 10 are shademid's byte for "
    "byte. A gamma was this lane's first choice and was rejected by measurement, "
    "not by taste: gamma COMPRESSES the top of the range, so face-minus-median "
    "goes 25.1 -> 24.6 (g 0.85) -> 23.7 (g 0.75) -> 22.4 (g 0.65), the wrong "
    "direction for a clause that needs a dark patch to be legible on a lit face. "
    "The exposure gain takes it to 28.3.")

RUNG_3_CONTROL = (
    "ep2-b13-shademid-0820: THE BEST CLIP THIS BEAT HAS PRODUCED AND STILL A "
    "FAIL. rc=0, 121 frames, 262.4 s, $0. H1 passed by 7x -- face band "
    "(250,240,400,360) mean absolute interframe 10.80 (rung 1, earned by walking "
    "out of frame) / 0.64 (rung 2, frozen) / 4.798 (rung 3), against a bar of "
    "3.0, with the step frames reading 26-35 at f066..f099. H3 passed "
    "decisively: the head travels from upright and facing camera at f000 to fully "
    "over on its side by f090, where rung 2 'leans but does not tip'. Posture "
    "held, plant held, camera locked, exposure flat at +1.71. It failed on H2's "
    "FACE sub-clause -- the head tips so far that from ~f042 to ~f072 the face is "
    "pressed into his own knee and is not legible at f060 -- and on G8, for the "
    "third time.")

BAR = {
    "G8_THE_PLANTS_SHADE_IS_ON_HIS_EYES": (
        "THE FAILED CLAUSE AND THE ONLY REASON THIS RUNG EXISTS, and it is now "
        "measured rather than eyeballed. At f120, read at 4x: a distinct darker "
        "patch lying across the eye band, with a visible EDGE, that is not his "
        "own arm, knee or brow shadow. INSTRUMENT, pre-registered: eye band "
        "(290,350,500,410) mean luma at f120 must be at least 15 BELOW the "
        "forehead/dome band (300,150,480,260) at the same frame, and the eye "
        "band must still sit at least 20 ABOVE the frame's p5 -- i.e. a shade, "
        "not a hole. Both bands are published at f000 and f120 whatever the "
        "verdict. THE NUMBER IS THE FILTER AND THE EYE IS THE DECISION: a brow "
        "shadow satisfies the arithmetic and is not the beat, so a PASS requires "
        "an edge that can be traced to the plant."),
    "H1_THE_PERFORMANCE_IS_NOT_GIVEN_BACK": (
        "CARRIED FROM SHADEMID, WHICH WON IT, AND IT IS THE THING MOST AT RISK. "
        "Face band (250,240,400,360), the same fixed band as rungs 1-3, mean "
        "absolute interframe luma over all 120 pairs at or above 3.0, and the "
        "last twenty pairs at or above 1.0. Shademid read 4.798 and 2.263. A "
        "brighter init is a different conditioning image and this engine has "
        "already shown that a cleaner init can cost motion (beat 18 lost 90% of "
        "its interframe to crf 10); a lifted one may do the same. Published with "
        "its SHAPE, not as a bare mean: this family holds every 3rd frame "
        "(judge_clip period 3, 8.0 effective fps, all six clips), so the energy "
        "is on the step frames and the gaps read 0.04-0.35. A clip that reads "
        "period 1 while its siblings read period 3 has a CUT in it and the hold "
        "statistics are retracted, not credited."),
    "H2_he_is_still_seated_knees_up_and_the_plant_holds": (
        "Carried. At f120 he is folded small in the grass with his knees up, "
        "satisfying the founder's 2026-08-18 ruling `no slide, he sits down "
        "beside it`; and the plant is ONE thin stem with TWO leaves, rooted, at "
        "f000 f030 f060 f090 f120. Both passed on shademid and a regression on "
        "either is attributable to the init."),
    "H3_the_sideways_tilt_survives": (
        "Carried, and judged 1:1 side by side against shademid rather than "
        "against a memory of it: upright and facing camera at f000, over on its "
        "side by f090, face rotated back toward the camera at f120. This is the "
        "attitude the beat asks for and shademid is the first clip that drew it."),
    "A5_no_exposure_blowout_MEASURED_AGAINST_THE_LIFTED_PLATE": (
        "f000 to f120 whole-frame mean luma within +/-25. THE BASELINE MOVES "
        "WITH THE VARIABLE AND THAT IS NOT A LOOSENING: the lifted cropped init "
        "reads mean 125.65 / p50 118.1 where shademid's read 103.36 / 89.5, so "
        "f120 is compared to THIS job's f000 and never to shademid's. Shademid "
        "ran +1.71 across 121 frames, the flattest of the six, and that is the "
        "number to beat. A drift materially larger than +/-2 on a recipe whose "
        "only change is a tone curve would itself be the finding."),
}

FAIL_MODES = [
    "F-EXPOSURE-IS-NOT-THE-SUSPECT -- G8 fails a FOURTH time on a plate that is "
    "measurably 31.8 luma brighter on the cheek and 28.6 on the whole-frame "
    "median. NAMED AS THE MOST LIKELY OUTCOME OF THIS RUNG, and the reasoning is "
    "published above rather than after the fact: beat 13 already had the "
    "brightest FACE of the three composite plates (cheek 114.6 against b03's "
    "101.8 and b15's 93.3) and only the darkest FIELD, and no light direction on "
    "this plate puts a 15cm plant's shadow on a face 300px above it. If it fires, "
    "exposure joins wording as an exonerated suspect, the axis is closed at two "
    "instruments, and the remaining lever is FRAMING -- his head and the leaves "
    "in one register -- which is a composite-geometry rung, not a plate-tone one.",
    "F-MOTION-COST -- H1 regresses. A lifted init is a different conditioning "
    "image, and this box has already measured a cleaner init costing beat 18 "
    "roughly 90% of its interframe motion. If the face band falls below 3.0 the "
    "lift is not free and the tradeoff is a real finding about tone versus "
    "amplitude, independent of G8.",
    "F-WASHED-CEL -- the dialect breaks: the cloak's blacks lift out of ink and "
    "the frame reads as flat rather than as cel-shaded. k = 2.6 was rejected by "
    "eye for exactly this before k = 2.0 was written, and the plate's p5 only "
    "moves 8.1 -> 15.3, so it is not expected -- but the engine re-inks every "
    "frame and may push it further than the plate does.",
    "F-IDENTITY-DRIFT -- the skin probe's f000 baseline moves by construction "
    "(cheek R 100.1 G 123.8 B 65.7 luma 110.1 becomes R 130.9 G 156.7 B 89.8 "
    "luma 141.3, both Rec.601 on the same box on the same crop). f120 is scored "
    "against the LIFTED f000. A judge who scores it against the parent's number "
    "will find a fictional +31 catastrophe.",
    "F-PLANT-REVERT / F-PLANT-PICKED-UP -- rechecked, held on all three b13 "
    "rungs so far.",
]

NOT_DONE = (
    "NO WORDING CHANGE OF ANY KIND -- the prompt and the negative are shademid's "
    "byte for byte, and that is the whole design: wording was exonerated by "
    "shademid's own pre-registered test and a fourth wording would be the ladder "
    "this repo forbids. NO recipe change: size, frames, fps, guidance, distilled "
    "sigmas, two-stage, offload, mode and --image-crf 10 are the b14 crf-10 "
    "parent's. NO new seed: 20260820 for the fourth time. NO new anchor -- LEFT, "
    "as shademid. NO change to the composite MASK and none to assert_framing.py's "
    "WANT_BBOX, because the lift moves no pixel's coordinates. NO COLOUR "
    "CORRECTION and NO MASKED OR SELECTIVE LIFT: a mask is a second instrument "
    "and this ladder has twice had a masked or colour-predicate instrument return "
    "a clean, wrong number on green-on-green ground. NO SHORTER RENDER: --frames "
    "is an input to the denoiser's temporal grid, not a crop. NO re-composite and "
    "NO re-framing -- that is the rung F-EXPOSURE-IS-NOT-THE-SUSPECT names, and "
    "it is named rather than fired. No pick, no plate_ack, no cut, no "
    "publication: beat 13 stays a SLATE.")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    force = "--force" in sys.argv
    if not os.path.isfile(LIFTED):
        raise SystemExit("!! %s does not exist. Run "
                         "pipeline/beat13_exposure_lift.py --k 2.0 first -- a "
                         "spec that asserts a sha for a file nobody has made is "
                         "a job that fails on the box." % LIFTED)
    new_sha = sha256(LIFTED)
    parent = derive_spec.load(os.path.join(REPO, PARENT))

    # The parent's fetch script, retokened by hand exactly as derive_spec will
    # retoken everything else, then pointed at the lifted plate. The MASK entry
    # is untouched: the lift changes no geometry, so the authored footprint
    # assert_framing.py reads is the same file it always was.
    fkey = [k for k in parent["payload"] if k.endswith("fetch_init.py")][0]
    fetch = parent["payload"][fkey]
    for old, new in ((os.path.basename(PARENT)[:-5], NEW_ID),
                     (OLD_BASE, NEW_BASE), (OLD_BENCH, NEW_BENCH)):
        fetch = fetch.replace(old, new)
    if fetch.count(OLD_PLATE) != 1 or fetch.count(OLD_SHA) != 1:
        raise SystemExit("!! expected exactly one mention of the plate name and "
                         "one of its sha in fetch_init.py; found %d and %d. "
                         "REFUSING to guess." % (fetch.count(OLD_PLATE),
                                                 fetch.count(OLD_SHA)))
    fetch = fetch.replace(OLD_PLATE, NEW_PLATE).replace(OLD_SHA, new_sha)
    fetch = fetch.replace(
        '"""RESTORE beat 13\'s composite plate AND ITS MASK to the courier path',
        '"""RESTORE beat 13\'s EXPOSURE-LIFTED composite plate AND ITS MASK to '
        'the courier path')

    child = derive_spec.derive(
        src=PARENT, new_id=NEW_ID,
        by="pipeline/derive_b13_shadelit_0820.py",
        fresh=dict(
            owner="the composite-plate motion lane, 2026-08-20, the plate rung",
            consumer=(
                "The episode 2 cut, beat 13, still a SLATE. shademid is the best "
                "clip this beat has produced and fails on one clause, G8, which "
                "its own pre-registered test handed to the plate. This is that "
                "plate rung and nothing else. Downstream: the beat's entry in "
                "review/ep2-picks/ and, if it passes, a founder screening. The "
                "cut swap is a taste call and is not proposed here."),
            success=(
                "ONE 704x1280 121-frame mp4 off the SAME WORDS, the same seed and "
                "the same mask as ep2-b13-shademid-0820, conditioned on an "
                "exposure-lifted copy of its plate, in which the plant's shade "
                "reads on his eyes at f120 WITHOUT giving back the performance "
                "shademid won. %s" % VARIABLE),
            why=(
                "$0, ~4.5 minutes of GPU, no download, and the plate already "
                "exists at 0 GPU seconds -- numpy and PIL over one PNG, with the "
                "before/after luma table and the k sweep published beside it and "
                "looked at at 1:1 and 6x before this spec was written. Beat 13 "
                "has spent three rungs on wording and shademid closed that axis "
                "by its own pre-registered condition, so the next lever is the "
                "only other thing in the job that can change without changing the "
                "beat: the tone of the picture the model is conditioned on. It is "
                "also the cheapest rung this beat will ever get -- the variable "
                "is one file path and one sha."),
        ),
        overrides={
            "payload:fetch_init.py": fetch,
            "argv:--src": (r"C:\banyan-farm\courier-box\farm-out"
                           r"\ep2-b13-sapcomp-0820\%s" % NEW_PLATE),
            "argv:--sha256": new_sha,
            "seed": SEED,
        },
        retoken=[(os.path.basename(PARENT)[:-5], NEW_ID),
                 (OLD_BASE, NEW_BASE), (OLD_BENCH, NEW_BENCH)],
        extra={
            "skin_probe": _probe(parent),
            "rung_3_the_control": RUNG_3_CONTROL,
            "the_one_variable": VARIABLE,
            "bar": BAR,
            "not_done_on_purpose": NOT_DONE,
            "pre_registered_fail_modes": FAIL_MODES,
            "the_plate_lift": {
                "tool": "pipeline/beat13_exposure_lift.py",
                "curve": "y = k*x/(1+(k-1)*x) on linear light, k = 2.0",
                "parent_plate": "farm-out/ep2-b13-sapcomp-0820/%s" % OLD_PLATE,
                "parent_sha256": OLD_SHA,
                "lifted_plate": "farm-out/ep2-b13-sapcomp-0820/%s" % NEW_PLATE,
                "lifted_sha256": new_sha,
                "evidence": ("farm-out/ep2-b13-sapcomp-0820/"
                             "CONTACT-b13-exposure-k2.0-0820.png -- the cropped "
                             "init before and after, side by side at 1:1"),
                "whole_frame_704x1280_crop": {
                    "before": "mean 103.36  p5 8.1   p50 89.5   p95 214.7  std 66.42",
                    "after": "mean 125.65  p5 15.3  p50 118.1  p95 231.1  std 67.83",
                },
                "probes_on_the_crop_luma_before_after": {
                    "cheek_the_pre_registered_skin_probe": "114.6 -> 146.4 (+31.8)",
                    "forehead_dome": "123.5 -> 154.9 (+31.4)",
                    "eye_band": "103.4 -> 130.6 (+27.1)",
                    "mouth_jaw": "87.1 -> 112.7 (+25.6)",
                    "the_composited_plant_leaves": "96.0 -> 121.9 (+25.9)",
                    "lower_third_the_dark_half": "73.0 -> 94.2 (+21.2)",
                    "grass_upper_left_the_bright_end": "195.0 -> 215.8 (+20.8)",
                },
                "asserted_by_the_tool_before_it_wrote_the_file": [
                    "size unchanged 832x1216, so the mask and WANT_BBOX stay valid",
                    "no channel value decreased (the curve is monotonic)",
                    "0 pixels newly driven to pure white (the shoulder held)",
                ],
                "rejected_by_eye_first": (
                    "k = 2.6 -- the cloak's blacks lift out of ink at 6x and the "
                    "frame starts reading flat rather than cel-shaded. k = 1.5 "
                    "moves the median only 89.5 -> 105.1, inside the noise of the "
                    "thing it is trying to buy. Sweep printed and looked at at "
                    "1:1 and at 6x on the head before k was chosen; no GPU."),
            },
        })
    out = os.path.join("pipeline", "jobs", "%s.yaml" % NEW_ID)
    print("lifted plate sha %s" % new_sha)
    print(derive_spec.write(child, out, force=force))
    return 0


def _probe(parent):
    probe = dict(parent["skin_probe"])
    probe["f000_reading"] = ("R 130.9 G 156.7 B 89.8, R-B 41.0, luma 141.3 "
                             "(std 6.6) -- ON THE LIFTED INIT, Rec.601, the same "
                             "box on the same 704x1280 left-anchored crop.")
    probe["f000_reading_on_the_PARENT_plate_for_reference_only"] = (
        "R 100.1 G 123.8 B 65.7, R-B 34.4, luma 110.1 (std 6.0). REPRODUCED "
        "EXACTLY by this lane's own instrument before the lift was applied, "
        "which is what establishes that the two readings are like for like. IT "
        "IS NOT THIS JOB'S BASELINE: f120 is scored against the LIFTED f000 "
        "above. Scoring it against this line yields a fictional +31 luma "
        "identity catastrophe, and this rung's one variable is exactly the thing "
        "that would cause it.")
    probe["carried_verbatim_from"] = (
        "ep2-b13-shademid-0820.yaml, and through it from the rung-1 spec where "
        "the box was placed by eye at 5x before any of these frames existed. THE "
        "BOX IS UNMOVED -- (286,282,352,336) -- and only its f000 reading changes, "
        "because the one variable changes what is under it. Re-placing a probe "
        "after the frames exist is choosing the number; re-reading an unmoved "
        "probe on a new init is the measurement.")
    probe["publish_luma_std_with_every_reading"] = (
        "A fixed window measures the subject only while the subject stays in the "
        "window, and the DISPERSION is the only thing that says so. Beat 13's own "
        "rung 3 went luma_std 6.0 -> 85.0 -> 56.6 as the head tipped out from "
        "under the box and left it straddling lit cheek and dark cloak: an "
        "EXPLOSION is a box on an edge exactly as a COLLAPSE is a box on a field, "
        "and beat 13's is the more dangerous shape because an inflated std looks "
        "like a subject that changed. If either appears, the probe is RETRACTED, "
        "re-placed by eye at 5x on the frame in question, and the verdict written "
        "by eye at 1:1 with material published beside luma.")
    return probe


if __name__ == "__main__":
    raise SystemExit(main())
