#!/usr/bin/env python3
r"""Derive `ep2-b08-cnetfill-0820` -- the fill gets the two hints it never had.

ONE VARIABLE: a ControlNet, inside the inpaint. Everything else is
`ep2-b08-str70-0820` byte-for-byte -- same init sha, same mask sha, same seed
20260822, same 40 steps, same cfg 7.5, same strength 0.70, same prompt, same
negative. The seed is deliberately NOT moved: at a changed conditioning the same
seed is the control, not a repeat.

WHY THIS RUNG EXISTS AND WHY IT IS NOT A SIXTH WORDING. `b08-arm-route-0819.md`
§26 CLOSED the prompt/strength/mask family with measurements, not opinions:

  1. the fist can be deleted and does not need 0.99 -- 0.70 deletes it;
  2. mask SIZE does not choose the noun, the PROMPT does -- for a KIND;
  3. strength governs invention symmetrically (5.1x too shard-dense at 0.99,
     4.8x too smooth at 0.70) and the plate's own line quality sits between the
     ends of the knob;
  4. a negative removes a KIND, NOT A COUNT: handed `second strap, crossed
     straps, extra strap` the pass redrew 91.3 % of the fill and the crossing
     band came back in the same place.

What is left on the best frame is one SHAPE. §27 names the only two levers that
reach a shape -- a controlnet or a hand-authored matte (R4, the author's) -- and
records that `inpaint_fruit.py` had no controlnet. Today it has one, so this is
the first of those two levers and the last one the steward may pull.

THE HINTS ARE NOT NEW AND THAT IS THE POINT. Both are the ones the plate's own
txt2img parent was rendered with: `b08-openpose-nat-0819.png` at scale 1.0 on the
xinsir openpose `twins` weights, and `b08-board-0820.png` at 0.3 on
xinsir/controlnet-scribble-sdxl-1.0. They are authored in PIL, they are already
in this beat's lineage, and -- decisively -- they are in the SAME 832x1216
coordinate frame as the init, because the init descends from the frame they
conditioned. A hint from anywhere else would be a second variable.

ALIGNMENT IS BY CONSTRUCTION, WHICH IS WHY THIS RUNG IS ALLOWED TO EXIST.
diffusers 0.29.2's `StableDiffusionXLControlNetInpaintPipeline` computes ONE
`crops_coords` from the mask and passes that same tuple to the init, to the mask
AND to every control image, in both the single-net and MultiControlNetModel
branches. The driver hands the hints over FULL-FRAME and crops nothing itself; it
refuses a hint that is not exactly the init's size, and before the render it
compares its own vendored `get_crop_region` against the live
`pipe.mask_processor.get_crop_region` and stops on any disagreement. Misalignment
is the class of defect that ate this beat twice, so it is a guard and not a hope.

$0 to run. No model, no GPU -- it writes a yaml and copies four PNGs.
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import derive_fetch_guard  # noqa: E402
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b08-str70-0820.yaml"
PARENT_ID = "ep2-b08-str70-0820"
JOB = "ep2-b08-cnetfill-0820"
SEED = 20260822          # UNCHANGED: at a changed conditioning the same seed is
                         # the control
STRENGTH = "0.70"        # UNCHANGED: the best fill lineage's own value
STAGE = r"C:\banyan-farm\b08cnetfill-0820"

INIT = "08-first-citizen-eraseonly-0820.png"
MASK = "08-first-citizen-eraseonly-mask-0820.png"
INIT_SHA = "7cc1a4cb12ca14a3628eb9ba8b8257ccc1f07f7cf9a9727d8ce769e1d5de8d45"
MASK_SHA = "8c94f1403c3e13839fe2351c70e494f9f2961c0b5a718db3f786d2a341a2d505"

# The plate's own conditioning, carried unchanged out of ep2-b08-scale30-0820.
TWINS_DIR = r"C:\banyan-farm\cnet-openpose-twins"
SCRIBBLE = "xinsir/controlnet-scribble-sdxl-1.0"
POSE_HINT = "b08-openpose-nat-0819.png"
POSE_SHA = "562911c8174a6ecc21bc8710a1ac1b7f965c3f2d865093a742c2598c37d952e0"
BOARD_HINT = "b08-board-0820.png"
BOARD_SHA = "38cd39da304dbb0317aa2522e1ccca099bef583e88e6573fde03b287358213d6"
SCALE = "1.0"
SCALE2 = "0.3"
HINT_SRC = "farm-out/ep2-b08-scale30-0820"

DRIVER = "pipeline/inpaint_fruit.py"

DRY_NOTE = (
    "MASK GEOMETRY AND HINT ALIGNMENT -- AND THE MASK MUST BE BYTE-IDENTICAL TO "
    "THE PARENT'S. This rung changes the CONDITIONING and nothing else: same "
    "init sha, same mask sha, same seed 20260822, same 40 steps, same cfg 7.5, "
    "same strength 0.70, same prompt, same negative, plus two ControlNets. The "
    "mask is the guard's original left fist grown 10, 10020 px, largest "
    "component 9956 px in a 102x118 box at the CHEST. WHAT TO CHECK ON THE DRY "
    "OUTPUT: (1) the mask PNG is one compact white blob at roughly x 555..660 "
    "y 528..635 with the strap running through it, no white at the board's top "
    "edge near y~670, none on the guard's FACE (x 531..601 y 355..420) and none "
    "on the goblin (x 60..260 y 430..1140); (2) TWO `hint` lines print, each "
    "saying 832x1216 MATCHES the init -- a hint of any other size is refused "
    "with rc 13 and the job stops here at $0; (3) a `pad_crop region` line "
    "prints the box diffusers will crop the init, the mask AND both hints with. "
    "If the mask differs from ep2-b08-str70-0820's dry mask at all, something "
    "other than the conditioning moved and this job must stop here at $0.")

fresh = {
    "why": (
        "THE LAST DEFECT ON THIS BEAT IS A SHAPE, AND THIS IS THE FIRST OF THE "
        "TWO LEVERS THAT REACH ONE. Five renders closed everything else by "
        "measurement rather than argument: mask size does not choose the noun "
        "(18408 px drew a head, 10020 px drew a fist); the prompt does choose a "
        "KIND (deleting `goblin` deleted it outright, first try, at unchanged "
        "strength); strength governs invention symmetrically and neither end "
        "lands on the plate's own line quality; and a negative handed the exact "
        "noun that arrived -- `second strap, crossed straps, extra strap` -- "
        "redrew 91.3 % of the fill and the crossing band came back in the same "
        "place. A negative removes a kind, not a count, because `second` is a "
        "cardinality over a thing the positive asks for by name and the text "
        "encoder has nowhere to put the word. What is left is a small X of brown "
        "band across the guard's strap: a SHAPE, and the only conditioning that "
        "addresses a shape is spatial. inpaint_fruit.py had no ControlNet when "
        "b08-arm-route-0819.md wrote that sentence in Section 27. It has one "
        "now, the pipeline is diffusers' own, and the two hints are the ones "
        "this plate's txt2img parent was rendered with."),
    "consumer": (
        "BEAT 08's PLATE, AND THE END OF THE STEWARD'S ROUTE EITHER WAY. If the "
        "crossing band is absent and every carried clause still holds, beat 08 "
        "finally has a complete plate: the fill gets wrapped in the "
        "--restore-only composite Section 27 adopted, and ONE motion sample off "
        "that plate follows immediately as the beat's take candidate. If the "
        "band survives spatial conditioning at scale 1.0, the route is closed in "
        "writing -- beat 08 ships as-is on ep2-b08-scale30-0820 and the "
        "hand-authored matte (R4, the author's and not the steward's) is the "
        "only lever left. No third outcome is on the table and no sixth wording "
        "is."),
    "success": (
        "ONE 832x1216 PNG plus its sidecar, published into courier-box, off the "
        "same asserted init sha and the same asserted mask sha as the parent, "
        "with BOTH hints published beside it. The sidecar must name controlnet, "
        "controlnet_2, both conditioning scales, both hint sha256s and the "
        "pad_crop_region_px box, and the log must carry the CROP REGION line "
        "showing the driver's vendored crop equals the live one. NOT a pick and "
        "NOT a plate_ack."),
    "owner": ("beat 08 arm-route lane, 2026-08-20 -- derived by "
              "pipeline/derive_b08_cnetfill_0820.py off ep2-b08-str70-0820, "
              "init, mask, seed, strength, prompt and negative UNCHANGED"),
}

overrides = {
    "key:beat": 8,
    "key:priority": 34,
    # Two ControlNet blobs to load on top of the base weights. The parent's whole
    # job was 20 s wall; this one carries ~5 GB more of weight loading and the
    # nets are already in the box cache.
    "key:est_minutes": 5,
    "argv:--note": DRY_NOTE,
}


def _read(rel: str) -> str:
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return fh.read()


FETCH = '''#!/usr/bin/env python3
"""Fetch beat 08's erase-only composite, its mask AND BOTH ControlNet hints.

No model, no GPU, no spend. Every one of the four is on origin/main under this
job's own farm-out directory, and every one is asserted by sha256 before it is
written -- so a wrong byte is a refusal here rather than a wrong picture later.

WHY THE HINTS ARE FETCHED AND NOT ASSUMED PRESENT. They are already on the box
from the txt2img rungs, in another job's staging directory. Reaching into one
would make this job depend on a directory nobody promised to keep, and would
leave the frame conditioned on bytes this spec never named. The two files cost
about 90 KB.

WHAT THE INIT CONTAINS, SO THE OPERATOR IS NOT SURPRISED BY IT: the guard has
TWO left fists. That is not a defect, it is the lineage. The plate's own fist is
still at the strap where it was drawn -- inside the mask, for this pass to
delete from real pixels -- and a byte-exact COPY of it sits at the board's top
edge, WHOLLY OUTSIDE the mask, so it comes through untouched.
"""
import hashlib, os, sys, urllib.request

OUT = r"{stage}"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "farm-out/{job}/")
UA = {{"User-Agent": "banyan-city-b08-cnetfill/1.0 (albert.numbro@gmail.com)"}}
WANT = {{
    "{init}":
        "{init_sha}",
    "{mask}":
        "{mask_sha}",
    "{pose}":
        "{pose_sha}",
    "{board}":
        "{board_sha}",
}}

os.makedirs(OUT, exist_ok=True)
for name, want in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(RAW + name, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %s -- refusing.\\n   want %s\\n   have %s"
                 % (name, want, have))
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %s %d bytes sha %s OK" % (name, len(raw), have), flush=True)
'''.format(stage=STAGE, job=JOB, init=INIT, init_sha=INIT_SHA, mask=MASK,
           mask_sha=MASK_SHA, pose=POSE_HINT, pose_sha=POSE_SHA,
           board=BOARD_HINT, board_sha=BOARD_SHA)

extra = {
    "sample_declaration": (
        "ONE SAMPLE, and the SIXTH on this route -- but the first with a lever "
        "the previous five did not have. Each of the five moved exactly one "
        "thing and each bought a distinguishable finding: fistcopy (18408 px "
        "mask) drew a goblin HEAD; eraseonly (10020 px) drew a green goblin "
        "FIST; nogoblin (prompt) drew no goblin and a second buckled strap; "
        "str70 (strength) deleted the fist, kept the strap running and left one "
        "crossing band; nostrap2 (negative) redrew 91.3 % of the fill and left "
        "THE SAME BAND. This one moves the conditioning. About sixty seconds of "
        "card across all six, $0."),
    "the_one_variable_and_what_is_held": (
        "MOVED: two ControlNets inside the inpaint -- %s at %s on %s, composed "
        "as a MultiControlNetModel with %s at %s on %s. HELD BYTE-FOR-BYTE: init "
        "sha %s, mask sha %s, seed %d, strength %s, 40 steps, cfg 7.5, "
        "pad-crop 64, blur 8, prompt and negative. The hints are not new work: "
        "both are the ones ep2-b08-scale30-0820 -- the txt2img frame this init "
        "descends from -- was rendered with, so they are already in this beat's "
        "lineage AND in the init's own 832x1216 coordinate frame. A freshly "
        "authored hint would have been a second variable."
        % (TWINS_DIR, SCALE, POSE_HINT, SCRIBBLE, SCALE2, BOARD_HINT,
           INIT_SHA, MASK_SHA, SEED, STRENGTH)),
    "why_a_controlnet_can_reach_what_the_negative_could_not": (
        "MEASURED, NOT HOPED. Section 26's finding is that a negative prompt "
        "removes a KIND and not a COUNT: `goblin` is a kind and deleting it "
        "deleted the goblin, but `second strap` is a cardinality over a thing "
        "the POSITIVE asks for by name (`brown leather harness strap`), the same "
        "token pulls both ways, and CLIP has nowhere to put the word `second`. A "
        "ControlNet does not carry counts either -- it carries POSITIONS. The "
        "openpose hint says where the torso and the arm are; the scribble hint "
        "says where the board is. Neither says `one strap`, and this spec does "
        "not claim they do. The claim is narrower and is the thing being tested: "
        "with the region's geometry pinned by a spatial channel, the sampler has "
        "less unconditioned room in which to invent a second diagonal. If that "
        "is wrong, the band survives and the route closes -- which is a real "
        "result and the reason the fail modes below are written before the "
        "render."),
    "diffusers_facts_read_before_this_spec_was_written": (
        "READ OUT OF THE 0.29.2 SOURCE, NOT REMEMBERED. (1) "
        "StableDiffusionXLControlNetInpaintPipeline takes the SAME latent-blend "
        "branch at unet.in_channels == 4 (`return_image_latents = "
        "num_channels_unet == 4`), so the base animagine weights load into it on "
        "the identical terms as the plain inpaint pipeline -- there is no "
        "9-channel inpainting checkpoint involved and none is needed. (2) It "
        "accepts padding_mask_crop, computes ONE crops_coords from the mask, and "
        "passes that same tuple to the init, to the mask and to EVERY control "
        "image -- prepare_control_image(..., crops_coords=crops_coords, "
        "resize_mode=resize_mode) in both the ControlNetModel and the "
        "MultiControlNetModel branches. That is why hint alignment here is by "
        "construction: the driver hands the hints over full-frame and crops "
        "nothing itself. (3) AutoPipelineForInpainting.from_pipe(pipe, "
        "controlnet=[cn, cn2]) swaps the class while reusing the loaded modules, "
        "and a LIST is wrapped into a MultiControlNetModel by the constructor -- "
        "the same composition controlnet_plate.py uses on the txt2img side."),
    "driver_change_and_its_selftest": (
        "pipeline/inpaint_fruit.py grew --controlnet/--control/--control-sha256/"
        "--scale and their `2` siblings, all defaulting to nothing, and nothing "
        "is the branch six filed verdicts were measured on. Its --selftest is $0 "
        "and runs with no torch and no network: 32 assertions, of which the "
        "load-bearing one reproduces ep2-b08-str70-0820's OWN LANDED SIDECAR "
        "byte for byte through the refactored writer -- a filed verdict as the "
        "anchor rather than a fixture written the same day. Alignment is "
        "asserted structurally: every hint must equal the init's pixel size (rc "
        "13 otherwise) and the module is checked to contain no crop call of its "
        "own. At render time the vendored get_crop_region is compared against "
        "the live pipe.mask_processor.get_crop_region and a mismatch is rc 14. "
        "Also refused before any weight loads: an unlisted net (the licence "
        "travels with the name), a net with no hint, a hint with no net, an "
        "unpinned hint, a hint whose bytes are not the pinned ones, the same net "
        "composed with itself, and a conditioning scale that was never stated."),
    "bar": {
        "B0_THE_STACK_IS_WHAT_IT_CLAIMS": (
            "VOID-CHECK, READ FIRST. `the net did nothing` and `the net never "
            "loaded` are DIFFERENT FINDINGS and this rung must not confuse them. "
            "The job has no result unless all four hold: (i) the log prints "
            "`PIPELINE StableDiffusionXLControlNetInpaintPipeline, 2 net(s), "
            "scales [1.0, 0.3]`; (ii) the log prints a `CROP REGION` line saying "
            "vendored == live; (iii) the sidecar names `controlnet: %s`, "
            "`controlnet_2: %s`, `controlnet_conditioning_scale: 1.0`, "
            "`controlnet_2_conditioning_scale: 0.3`, `control_image_sha256: %s` "
            "and `control_2_image_sha256: %s`; (iv) the sidecar names "
            "`pad_crop_region_px` with a real box. Missing any one and the frame "
            "is VOID -- not a fail."
            % (TWINS_DIR, SCRIBBLE, POSE_SHA, BOARD_SHA)),
        "H1a_the_fist_is_GONE": (
            "No skin-toned fist survives inside poly(FIST) grown 6, by eye at "
            "9x. Both 0.99 and 0.70 passed this; a regression means the "
            "conditioning is holding the old limb in place, which is itself a "
            "finding and is pre-registered below as a fail mode."),
        "H1b_THE_CROSSING_BAND_IS_ABSENT": (
            "THE ONE QUESTION THIS RUNG ASKS, and it is a SPATIAL claim, so it "
            "is judged SPATIALLY AND BY EYE. The guard's own diagonal harness "
            "strap RUNS CONTINUOUSLY through the mask, entering at the top edge "
            "and leaving at the bottom, and NO SECOND BAND CROSSES IT. On "
            "ep2-b08-str70-0820 a second brown band crosses the strap below the "
            "buckle, forming a small X with two short stubs at its top; on "
            "ep2-b08-nostrap2-0820 the same band is in the same place after 91.3 "
            "% of the fill was redrawn. TWO INDEPENDENT READINGS ARE REQUIRED "
            "AND BOTH MUST PASS: (a) BY EYE AT 5x on the fill region, against "
            "the parent side by side; (b) THE BAND'S OWN MEASURED SIGNATURE -- "
            "count, on every horizontal scanline crossing the erase region, the "
            "maximal runs of strap-hued pixels, where strap hue is defined off "
            "THE PLATE's own strap sampled outside the mask and not off this "
            "frame. One strap crossing a scanline gives ONE run; the X gives "
            "TWO. The reference numbers for `band present` and `band absent` are "
            "measured on the THREE ALREADY-LANDED frames (init, str70, nostrap2) "
            "and written into the ladder BEFORE this frame is opened; they are "
            "not to be chosen after looking at it."),
        "C4prime_RING_RE_BASED": (
            "Run pipeline/fill_quality.py's assess() on the erase region with "
            "the init as plate and THE RING PUSHED OUT TO 35-45 px. D >= 0.45 "
            "AND N >= 0.25 AND F <= 2.60. DO NOT RUN THE PRESCRIBED 3-12 px RING "
            "AND REPORT ITS VOID AS A RESULT: it has VOIDed three times on this "
            "exact geometry because --pad-crop repaints the annulus. Real "
            "fraction of the annulus is 3.1 % at 3-12 and 100.0 % at 35-45. "
            "PUBLISH THE ANNULUS'S REAL-PIXEL FRACTION beside the score."),
        "C4prime_AND_SHARD_ARE_NECESSARY_AND_NOT_SUFFICIENT": (
            "WRITTEN INTO THE BAR BECAUSE SECTION 27 EARNED IT THE HARD WAY. C4' "
            "bars D from below only and has certified a green goblin fist (D "
            "1.751) and a wedge fan (D 3.479). The shard clause was added to fix "
            "that, and one rung later it PASSED A FRAME THAT IS UNUSABLE AT A "
            "GLANCE -- the ink-carry composite scored 2.82 % shard and 12.2 % "
            "ink, both inside their bands, while looking blocky, staircased and "
            "spotted with lavender background blobs on the guard's chest, "
            "because posterisation produces plate-like edge statistics by "
            "destroying the picture. SO: A PASS ON THIS RUNG REQUIRES LOOKING. "
            "No combination of automatic clauses may be reported as a pass "
            "without the 5x eye reading of H1b, and a metric agreeing with the "
            "steward is not a sample."),
        "SHARD_RATE_ceiling_AND_floor": (
            "Shard rate = fraction of fill px whose |grad| exceeds the 99th "
            "percentile of its own real ring (35-45 px). BAND: 0.80 % to 3.00 %. "
            "References on this exact footprint: the material this fill replaces "
            "1.82 %, the goblin fist 2.79 %, the wedge fan 9.27 %, str70 0.38 %, "
            "nostrap2 0.31 %. An empirical null of 200 real windows of this "
            "footprint puts the median at 0.35 %, p95 4.11 %, p99 6.74 %. The "
            "FLOOR is not decoration: it is the only automatic clause that "
            "failed nostrap2 in the direction that frame was actually wrong."),
        "INK_floor": (
            "Fraction of erase-region px with L < 90. FLOOR 10.3 %. References: "
            "the plate's own material 13.3 %, str70 10.5 %, nostrap2 9.1 % "
            "(fail), the 0.99 wedge fan 24.6 % (over-drawn)."),
        "H3_the_digits_SURVIVED": (
            "The copied fist's three finger creases and thumb are still "
            "individually legible at 9x. It is wholly outside the mask but "
            "INSIDE the pad-crop box, so it is not untouched: it read maxdiff 55, "
            "121 and 78 across three renders and 0 after the --restore-only "
            "composite. Report the number; legible is the bar."),
        "H5_NO_NEW_NOUN": (
            "No face, no head, no figure, no placket, no second buckle and no "
            "second clasp. Judged by eye at 4x on the whole frame, plus the "
            "green-channel measurement that made three verdicts checkable: "
            "in-mask G-R mean and px above +20, against -19.90 and 0 for the "
            "real material around the fill. References: -2.83 with 1934 px "
            "(green goblin fist), -16.06 with 166 (wedge fan), -23.11 with 0 "
            "(str70), -24.47 with 0 (nostrap2)."),
        "B8_hair": (
            "Canon light sandy hair, not bald. maxdiff 0 over the head box "
            "(500..640, 300..430), which has held at 0 through four runs because "
            "the head is outside the crop box."),
        "B6_wardrobe": (
            "Cream shirt, white sash and brown wrap are still THREE garments. "
            "The mask reaches none of them but the shirt around the fist."),
        "OUT_OF_MASK_DRIFT_is_MEASURED_not_assumed": (
            "Report changed px outside the mask, their maxdiff, and how many "
            "fall outside the pad-crop box the sidecar names. The answer to the "
            "last has been 0 four times running -- 8574 / 8598 / 8600 / 8572 px, "
            "a 0.3 % spread over identical geometry -- and any other answer is a "
            "finding. NOTE THAT THE SHIPPING FORM DOES NOT CARRY THIS AT ALL: "
            "Section 27's --restore-only composite takes the plate's own bytes "
            "outside the mask and measured 0 px beyond the feather. The raw "
            "render is measured anyway, because a change in a number that has "
            "been stable four times means the geometry moved."),
        "scale30_clauses_hold": (
            "B1, B2, B3, B4a, B4b, B4c, B5 re-measured on the landed frame. The "
            "goblin box (60..260, 430..1140) and the board box (300..832, "
            "660..1000) are both far outside the crop box and have read maxdiff "
            "0 and 1."),
    },
    "pre_registered_fail_modes": {
        "most_likely_A_THE_BAND_SURVIVES": (
            "The openpose hint carries eighteen body keypoints and the scribble "
            "hint carries a board; NEITHER names a strap, so it is entirely "
            "possible that pinning the torso and the arm leaves the sampler as "
            "free to draw a diagonal across the chest as it was. IF THE BAND IS "
            "STILL THERE, THE ROUTE CLOSES IN WRITING. Not retuned, not "
            "re-scaled, not re-hinted: three levers (prompt, strength, negative) "
            "and now a fourth (spatial conditioning) would have failed the same "
            "clause, beat 08 ships as-is on ep2-b08-scale30-0820, and the "
            "hand-authored matte -- R4, the author's and not the steward's -- is "
            "the only lever left. DO NOT PROPOSE SCALE 1.5, A THIRD NET, OR A "
            "STRAP HINT."),
        "second_THE_HINT_HOLDS_THE_OLD_FIST_IN_PLACE": (
            "The openpose skeleton puts a wrist near the region this pass is "
            "trying to empty. If a skin-toned remnant survives inside poly(FIST) "
            "grown 6 -- something neither 0.99 nor 0.70 did -- then the "
            "conditioning is fighting the deletion rather than shaping what "
            "replaces it. That is a REAL finding and it closes the route on the "
            "same terms as the first fail mode: it would mean the two jobs "
            "(erase a limb, and say what stands where it was) are not "
            "simultaneously satisfiable by any conditioning this driver can "
            "carry."),
        "third_THE_FILL_GOES_FLAT_OR_SPIKY": (
            "A conditioning channel at scale 1.0 inside a 10020 px hole may push "
            "the shard rate out of the 0.80-3.00 % band in either direction. "
            "This is a FAIL of the shard clause and is reported as one; it is "
            "NOT a licence to sweep the scale, because the clause that decides "
            "this rung is H1b and a shard failure with the band still present is "
            "the first fail mode wearing a second hat."),
        "fourth_A_SEAM_AT_THE_COPY": (
            "The copy's stair-stepped octagonal edge is untouched by this pass "
            "and WILL still read as a decal in the raw render. EXPECTED, NOT A "
            "FAIL -- and in the shipping form it is moot, because "
            "--restore-only puts the plate's own bytes back outside the mask and "
            "measured the copy byte-exact (maxdiff 0)."),
        "NOT_a_fail_mode_a_C4prime_OR_SHARD_PASS": (
            "Neither is evidence of a good fill on this instrument. C4' passed a "
            "green goblin fist and a wedge fan; the shard clause passed a "
            "posterised frame that is unusable at a glance. Only H1b's two "
            "readings can pass this frame."),
    },
    "the_shipping_form_is_the_composite_not_the_render": (
        "WHATEVER THIS PASS PRODUCES IS WRAPPED IN pipeline/beat08_ink_carry.py "
        "--restore-only BEFORE IT IS JUDGED AS A PLATE, per Section 27, which "
        "adopted that form for every inpaint result in this tree. It takes the "
        "fill inside the mask and the PLATE's own bytes outside it, blending "
        "only a 2 px feather: measured 0 px differing from the plate beyond the "
        "feather against 7560 for the raw render, and the protected fist copy "
        "back to byte-exact. It costs nothing, it cannot make a picture worse, "
        "and it retires a defect four renders in a row carried. It CANNOT remove "
        "a shape, which is why it is a wrapper here and not the rung."),
    "init_provenance": (
        "pipeline/beat08_grip_copy.py --write --variant eraseonly. init %s sha "
        "%s, mask %s sha %s -- BYTE-IDENTICAL to all five parents on this route. "
        "The two hints are %s sha %s and %s sha %s, carried unchanged from "
        "farm-out/ep2-b08-scale30-0820 -- the txt2img frame this init descends "
        "from -- which is what puts them in the init's own 832x1216 coordinate "
        "frame. All four are fetched by sha from farm-out/%s/ on origin/main. "
        "THE URL IS ASSERTED BY THE DERIVER, not trusted: derive_spec retokens "
        "every string in a child, which is what pointed ep2-b08-nogoblin-0820's "
        "first filing at a directory nobody had published and killed it with a "
        "404 three seconds in. This script publishes all four files under this "
        "job's own name via pipeline/derive_fetch_guard.publish_beside_the_child "
        "and then re-reads the emitted yaml with assert_fetch_urls_resolve."
        % (INIT, INIT_SHA, MASK, MASK_SHA, POSE_HINT, POSE_SHA, BOARD_HINT,
           BOARD_SHA, JOB)),
    "scope_limits": (
        "This does not settle beat 08's staging, it does not attempt the "
        "forearm, and it does not touch the txt2img plate. The plate draws the "
        "guard's hand at the authored elbow and the pose hint wants it at the "
        "wrist; re-routing a limb is a txt2img question and this rung leaves it "
        "there. It also does not license a conditioning-scale sweep: one sample, "
        "at the scales the plate's own parent used, and a verdict either way."),
}


def main() -> int:
    child = derive_spec.derive(
        src=PARENT,
        new_id=JOB,
        fresh=fresh,
        overrides=overrides,
        retoken=[("b08str70-0820", "b08cnetfill-0820"),
                 ("b08-str70-", "b08-cnetfill-")],
        extra=extra,
        by="pipeline/derive_b08_cnetfill_0820.py")

    # ---- THE DRIVER AND THE FETCH SCRIPT, REPLACED AFTER RETOKEN.
    # Overrides land after retoken by design, so the URL written here is the one
    # that reaches the card -- the retoken trap cannot touch it.
    child["payload"] = dict(child["payload"])
    for key in list(child["payload"]):
        base = os.path.basename(key.replace("\\", "/"))
        if base == "inpaint_fruit.py":
            child["payload"][key] = _read(DRIVER)
        elif base == "fetch_init.py":
            child["payload"][key] = FETCH

    # ---- THE CONDITIONING, SPLICED INTO BOTH RENDER STEPS.
    # Positionally before --prompt-file, the same way the txt2img rung spliced
    # its second net. Every flag is pinned by an assertion below rather than
    # trusted from the splice.
    # A LITERAL BACKSLASH, NOT os.path.join. This deriver runs on a Mac and
    # writes paths for Windows; os.path.join here yields
    # `C:\banyan-farm\...\b08cnetfill-0820/hint.png`, which Windows tolerates and
    # nobody reading the spec would trust. Twenty-four renders already went to
    # C:\Windows\System32 on this exact confusion (31a3c873).
    def _win(name: str) -> str:
        return STAGE + "\\" + name

    control_argv = [
        "--controlnet", TWINS_DIR,
        "--control", _win(POSE_HINT),
        "--control-sha256", POSE_SHA,
        "--scale", SCALE,
        "--controlnet2", SCRIBBLE,
        "--control2", _win(BOARD_HINT),
        "--control2-sha256", BOARD_SHA,
        "--scale2", SCALE2,
    ]
    spliced = 0
    for step in child["steps"]:
        if step["name"] in ("dry", "s%d" % SEED):
            i = step["argv"].index("--prompt-file")
            step["argv"][i:i] = list(control_argv)
            spliced += 1
    if spliced != 2:
        raise SystemExit("!! spliced the conditioning into %d step(s), wanted 2"
                         % spliced)

    # ---- PUBLISH THE HINTS TOO. A frame conditioned on two images whose bytes
    # ---- never left the box is a frame nobody can re-read.
    pub = [s for s in child["steps"] if s["name"] == "publish"][0]
    before = pub["argv"][2]
    pub["argv"][2] = before.replace(
        '    "prompt.txt",',
        '    "%s",\n    "%s",\n    "prompt.txt",' % (POSE_HINT, BOARD_HINT))
    if pub["argv"][2] == before:
        raise SystemExit("!! could not add the hints to the publish step's NAMES")

    # ---- ASSERTIONS. Each is a way a one-variable rung silently becomes a
    # ---- two-variable one, or a way this job dies on the card for $0 of value.
    argvs = [str(x) for s in child["steps"] for x in s["argv"]]

    def flag(n):
        return [argvs[i + 1] for i, v in enumerate(argvs) if v == n]

    # held byte-for-byte
    assert flag("--init-sha256") == [INIT_SHA] * 2, flag("--init-sha256")
    assert flag("--seed") == [str(SEED)] * 2, flag("--seed")
    assert flag("--strength") == [STRENGTH] * 2, flag("--strength")
    assert flag("--steps") == ["40"] * 2, flag("--steps")
    assert flag("--cfg") == ["7.5"] * 2, flag("--cfg")
    assert flag("--pad-crop") == ["64"] * 2, flag("--pad-crop")
    assert flag("--blur") == ["8"] * 2, flag("--blur")
    # the one variable, in BOTH steps
    assert flag("--controlnet") == [TWINS_DIR] * 2, flag("--controlnet")
    assert flag("--controlnet2") == [SCRIBBLE] * 2, flag("--controlnet2")
    assert flag("--scale") == [SCALE] * 2, flag("--scale")
    assert flag("--scale2") == [SCALE2] * 2, flag("--scale2")
    assert flag("--control-sha256") == [POSE_SHA] * 2
    assert flag("--control2-sha256") == [BOARD_SHA] * 2
    assert flag("--control") == [STAGE + "\\" + POSE_HINT] * 2, flag("--control")
    assert flag("--control2") == [STAGE + "\\" + BOARD_HINT] * 2, flag("--control2")
    assert not any("/" in p for p in flag("--control") + flag("--control2")), \
        "a forward slash reached a Windows path -- see 31a3c873"
    assert [s["name"] for s in child["steps"]] == \
        ["fetch", "dry", "s%d" % SEED, "publish"], \
        [s["name"] for s in child["steps"]]
    # THE PARENT ID MUST NOT SURVIVE IN ANYTHING THAT ADDRESSES A FILE, and
    # PROSE IS NOT ADDRESSING A FILE. The --note cites ep2-b08-str70-0820 on
    # purpose -- it tells the operator which dry mask to compare this one against
    # -- and the staged driver's selftest constants name that job's landed
    # sidecar as their golden, which is the whole reason the no-regression claim
    # is checkable. What must not survive is a PATH: an argv that names a
    # directory, a URL, a payload key or a declared artifact. That is what is
    # checked, one token at a time, rather than by grepping the whole blob and
    # then having to relax the check.
    def _addresses_a_file(tok: str) -> bool:
        t = tok.replace("\\", "/")
        return ("farm-out/" in t or "banyan-farm/" in t
                or t.endswith((".png", ".yaml", ".txt", ".sha256")))

    paths = [t for t in argvs if _addresses_a_file(t) and "\n" not in t]
    paths += [str(k) for k in child["payload"]]
    paths += [str(x) for x in child.get("artifacts") or []]
    bad = [p for p in paths if PARENT_ID in p or "b08str70" in p]
    assert not bad, "the parent id survived into a path: %s" % bad[:3]
    # and the publish step, which is one long python string rather than a token,
    # is checked on the directory literals it actually writes to
    pubsrc = pub["argv"][2]
    assert PARENT_ID not in pubsrc, "the publish step still writes to the parent"
    assert JOB in pubsrc, "the publish step lost this job's own directory"
    # the driver that ships is the driver on disk, and its selftest is green
    payload_driver = [v for k, v in child["payload"].items()
                      if k.endswith("inpaint_fruit.py")][0]
    assert payload_driver == _read(DRIVER), "the staged driver is not the file"
    assert "--controlnet" in payload_driver, \
        "the staged driver predates the ControlNet flags"
    assert "StableDiffusionXLControlNetInpaintPipeline" not in \
        payload_driver.split("def selftest")[0].split("FOURTH CALLER")[0], \
        "sanity: the class name should appear only below the docstring's note"
    # the words did not move
    import yaml as _yaml
    parent = _yaml.safe_load(open(os.path.join(REPO, PARENT), encoding="utf-8"))
    pp = {os.path.basename(k.replace("\\", "/")): v
          for k, v in parent["payload"].items()}
    cp = {os.path.basename(k.replace("\\", "/")): v
          for k, v in child["payload"].items()}
    for name in ("prompt.txt", "negative.txt"):
        assert pp[name] == cp[name], "%s drifted from the parent's" % name
    # and the four files this spec pins are the four files on disk
    for rel, want in ((os.path.join("farm-out", PARENT_ID, INIT), INIT_SHA),
                      (os.path.join("farm-out", PARENT_ID, MASK), MASK_SHA),
                      (os.path.join(HINT_SRC, POSE_HINT), POSE_SHA),
                      (os.path.join(HINT_SRC, BOARD_HINT), BOARD_SHA)):
        with open(os.path.join(REPO, rel), "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        assert got == want, "%s is %s, spec pins %s" % (rel, got, want)

    dst = "farm-out/" + JOB
    derive_fetch_guard.publish_beside_the_child(
        "farm-out/" + PARENT_ID, dst, {INIT: INIT_SHA, MASK: MASK_SHA})
    derive_fetch_guard.publish_beside_the_child(
        HINT_SRC, dst, {POSE_HINT: POSE_SHA, BOARD_HINT: BOARD_SHA})
    print("published init, mask and BOTH hints -> %s/" % dst)

    out = derive_spec.write(child, "pipeline/jobs/%s.yaml" % JOB)
    derive_fetch_guard.assert_fetch_urls_resolve(
        out, (INIT, MASK, POSE_HINT, BOARD_HINT))
    print("wrote %s" % out)
    print("id        %s" % child["id"])
    print("parent    %s" % PARENT_ID)
    print("variable  TWO ControlNets INSIDE the inpaint (%s @ %s, %s @ %s)"
          % (os.path.basename(TWINS_DIR), SCALE, SCRIBBLE, SCALE2))
    print("held      init/mask sha, seed %d, strength %s, prompt, negative"
          % (SEED, STRENGTH))
    print("steps     %s" % " -> ".join(s["name"] for s in child["steps"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
