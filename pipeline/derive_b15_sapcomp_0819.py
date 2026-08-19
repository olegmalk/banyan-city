#!/usr/bin/env python3
r"""Derive pipeline/jobs/ep2-b15-sapcomp-0819.yaml FROM ep2-b19-sapcomp-0819.yaml.

WHY A SCRIPT AND NOT A TYPED FILE. work-ladder-0819.md's standing rule: "One
variable per rung, and prefer to make that a fact about the file -- derive the
new spec from its parent programmatically rather than retyping it." The parent
here is the one composite-then-inpaint job in this repo that has been fired and
scored: `ep2-b19-sapcomp-0819` passed all eight clauses of its pre-registered
bar on the first GPU fire, 3.8 s, $0. Every sampler number, the whole
`inpaint_fruit.py` payload, the env block, the needs, the dry-run-before-any-
model gate and the no-glob publish are carried BY COPY, so "the recipe is the
proven one" is checkable with a diff instead of trusted.

THE ONE VARIABLE IS THE BEAT: beat 15's composite init replaces beat 19's.
Everything a sampler does is byte-identical -- 40 steps, cfg 7.5, strength 0.30,
pad-crop 64, blur 8, seed 20260819, animagine-xl-3.1 base weights in the SDXL
inpaint pipeline. What changes is the init, its mask, the two prompt files and
the bar, because those are the beat.

THE DERIVATION GUARD THE LADDER ASKED FOR, FIRED HERE TOO. Three crf-10 specs
on 2026-08-19 were derived from their parents INCLUDING the parent's `verdict`,
`verdict_measured` and `pick` blocks, so a filed job carried a PASS belonging to
a different clip. This script REFUSES to carry any key matching verdict / pick /
sweep / plate_ack and prints what it dropped. `ep2-b19-sapcomp-0819.yaml` now
carries a large `verdict_0819` block and a same-day retraction inside it, so
this is not a hypothetical on this exact parent -- it is the file's current state.

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
PARENT = os.path.join(REPO, "pipeline", "jobs", "ep2-b19-sapcomp-0819.yaml")
OUT = os.path.join(REPO, "pipeline", "jobs", "ep2-b15-sapcomp-0819.yaml")

PARENT_DIR = r"C:\banyan-farm\b19sapcomp-0819"
CHILD_DIR = r"C:\banyan-farm\b15sapcomp-0819"

# The two files the box fetches, and their sha256s as committed to origin/main in
# 1251caa0. The box asserts both again before a model loads.
INIT_NAME = "15-good-listener-sapcomp-0819.png"
INIT_SHA = "109abc613ff5c6d6a334c9964abaabe121b2e20a10ca1d91d06ff4d79d29e91c"
MASK_NAME = "15-good-listener-sapcomp-mask-0819.png"
MASK_SHA = "f7933427bba319044058d8712a1574b35ad084768e5807b4f3e060a6ea810fdb"
LOCAL_INIT = os.path.join(REPO, "farm-out", "ep2-b15-sapcomp-0819", INIT_NAME)
LOCAL_MASK = os.path.join(REPO, "farm-out", "ep2-b15-sapcomp-0819", MASK_NAME)

REFUSE = re.compile(r"verdict|pick|sweep|plate_ack", re.I)

# ---------------------------------------------------------------------------
# THE PROMPT. Beat 15's own passing wording, carried from plate_scratch.py's
# DRAFTS[15] (which scored 6 of 7 on r1), with the PLANT clause rewritten to
# describe what the composite already draws instead of asking for a count the
# checkpoint cannot deliver. Two rungs of wording failed at that count -- r1 gave
# five blades on three nodes, r2 moved one clause and the plant did not move at
# all -- which is why the structure is now in the INIT and the words only have to
# agree with it.
#
# The figure terms are kept SHORT but present on purpose. padding_mask_crop=64
# denoises a crop around the mask bbox (x 121..310, y 285..604), and his
# silhouette's left edge runs x 291..370 through those rows, so a slice of him IS
# inside the crop and 278 mask px land on him. Dropping his terms would leave that
# slice to the checkpoint's own prior; spending the whole prompt on him would
# invite a second figure into the field. `solo` and `2boys` guard that from both
# directions.
PROMPT = (
    "a tiny sapling rooted in the grass, exactly two wide oval leaves with soft "
    "round tips on one thin bare stem, beside one seated lean adult goblin man in "
    "a patchwork cloak, solo, sunny grassy field, wide shot, detailed cinematic "
    "anime, masterpiece, best quality, very aesthetic"
)

# THE DEFECT CLASS IS FIRST, per the parent's own negative_ordering note: the
# 77-token CLIP ceiling drops the TAIL silently, so the terms this rung is about
# lead and `low quality` is last. These are beat 15's OBSERVED failures across
# twenty-four judged artifacts plus its bar's own named FAILs -- extra leaves and
# nodes, a bead vine, a bud/ball at the tip -- not guesses.
#
# AND IT IS MEASURED, NOT ESTIMATED. The first version of this negative had 29
# comma-terms and measured 85 OF 77 on animagine's own CLIP vocab -- eight tokens
# would have fallen silently off the tail, which is the exact defect the parent's
# note warns about while counting WORDS. pipeline/clip_token_count.py was written
# for this and the terms below are what came back under the ceiling: five removed
# as redundant (`extra leaves` is covered by three/four/many; `serrated leaves` by
# `pointed lance leaves`, and the observed defect was lance-tipped not serrated;
# `flower pot` by `potted plant`; `trunk` by `large tree`/`thick branch`; `flower`
# by `bud`/`ball at the tip`, which is the shape actually observed -- a white
# SPHERE). Measured: prompt 58 of 77, negative 71 of 77 -- the parent's own
# negative measures 71 too, which is the control that says the counter is right.
NEGATIVE = (
    "three leaves, four leaves, many leaves, extra stalk, multi-node weed, "
    "pointed lance leaves, bead, vine, bud, ball at the tip, fruit, potted plant, "
    "large tree, thick branch, forest, 2boys, child, chibi, standing, close-up, "
    "text, photorealism, 3d render, low quality"
)


# The parent's two --note strings describe BEAT 19'S mask ("the two cleared twig
# arcs ... 17.08 percent of the frame") and its three-rung wording ladder. A
# path-swap does not make those true of this beat, and a note that is wrong about
# the mask is worse than no note: it is the thing the dry step exists to check
# against. So the two notes are REPLACED, and they are the only prose in the steps
# that is not the parent's.
DRY_NOTE = (
    "mask geometry check. Writes the mask and exits BEFORE a model is loaded, so a "
    "wrong mask costs seconds instead of a GPU fire. The mask is the union of the "
    "removed weed's footprint and the drawn sapling's own footprint, dilated 12 and "
    "feathered 3 -- 42792 px, 4.23 percent of the frame, extent x 121..310 y "
    "285..604. WHAT TO CHECK ON THE DRY PNG: that the mask does not reach his face, "
    "his spectacles, his hands, his knees or his boots, because those carry the six "
    "clauses r1 already passes. It DOES touch him: 278 px fall inside his silhouette "
    "proper and 589 inside the dilated protect halo, where his cloak's left edge runs "
    "x 291..370 through the mask's own rows. That is known, is why FAIL-FIGURE is a "
    "pre-registered clause, and is the number to check has not grown.")
RENDER_NOTE = (
    "ONE SAMPLE, ONE SEED. Every sampler number is the parent job's: 40 steps, cfg "
    "7.5, strength 0.30, pad-crop 64, blur 8, animagine-xl-3.1 base weights in the "
    "SDXL inpaint pipeline. THE ONE VARIABLE IS THE INIT: beat 15's plant is "
    "composited instead of prompted. 0.30 runs int(40 * 0.30) = 12 of 40 denoising "
    "steps from a latent that still carries the drawn structure, so the high-sigma "
    "steps where global layout is decided never run -- which is why 'finish this "
    "structure' succeeds where 'invent this structure' failed at TWO wordings here "
    "(r1 five blades on three nodes; r2 moved one clause and the plant did not move "
    "at all). Beat 19 closed its wording ladder at three rungs and this beat closed "
    "its own at two, on the same law.")


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def swap_dir(value):
    """Carry a step/argv/payload path over to this job's working directory."""
    if isinstance(value, str):
        return value.replace(PARENT_DIR, CHILD_DIR).replace(
            PARENT_DIR.replace("\\", "/"), CHILD_DIR.replace("\\", "/"))
    if isinstance(value, list):
        return [swap_dir(v) for v in value]
    return value


def main() -> int:
    # The asserted bytes are asserted HERE too: a spec that names a sha the local
    # artifact does not have is the "stale checkout" failure this repo has already
    # paid for once, and it costs nothing to refuse it at derivation time.
    for path, want in ((LOCAL_INIT, INIT_SHA), (LOCAL_MASK, MASK_SHA)):
        if not os.path.isfile(path):
            print("!! missing %s -- the init must be committed BEFORE the spec "
                  "that fetches it off origin/main." % path)
            return 2
        have = sha256_of(path)
        if have != want:
            print("!! SHA MISMATCH for %s\n   want %s\n   have %s"
                  % (path, want, have))
            return 3

    parent = yaml.safe_load(open(PARENT, "r", encoding="utf-8"))

    refused = sorted(k for k in parent if REFUSE.search(k))
    child = {k: v for k, v in parent.items() if k not in refused}

    # ---- carried BY COPY, untouched: env, needs, the whole payload script, the
    # ---- sampler numbers inside the steps, max_attempts, sample, runner.
    inpaint_key = PARENT_DIR + r"\inpaint_fruit.py"
    fetch_key = PARENT_DIR + r"\fetch_init.py"
    payload = dict(parent["payload"])
    inpaint_src = payload[inpaint_key]
    inpaint_sha = hashlib.sha256(inpaint_src.encode("utf-8")).hexdigest()

    # fetch_init.py is carried with its guard logic byte-identical and only its
    # three data facts swapped: the output dir, the raw path and the WANT map.
    fetch_src = payload[fetch_key]
    fetch_src = fetch_src.replace(PARENT_DIR, CHILD_DIR)
    fetch_src = fetch_src.replace("farm-out/ep2-b19-sapcomp-0819/",
                                  "farm-out/ep2-b15-sapcomp-0819/")
    fetch_src = fetch_src.replace("banyan-city-b19-sapcomp/1.0",
                                  "banyan-city-b15-sapcomp/1.0")
    fetch_src = fetch_src.replace('"19-the-drop-sapcomp-0819.png"',
                                  '"%s"' % INIT_NAME)
    fetch_src = fetch_src.replace(
        '"b6dbd53bffd0dae77eb410c7669a042c9a040fb3faf2a5f5a5032b7431418903"',
        '"%s"' % INIT_SHA)
    fetch_src = fetch_src.replace('"19-the-drop-sapcomp-mask-0819.png"',
                                  '"%s"' % MASK_NAME)
    fetch_src = fetch_src.replace(
        '"ce1e5ba2f89e9cabd0f90a3316a1436605bfd152a23b7add994995e255bcf266"',
        '"%s"' % MASK_SHA)
    fetch_src = fetch_src.replace("beat 19's SAPLING composite",
                                  "beat 15's SAPLING composite")
    fetch_src = fetch_src.replace("pipeline/beat19_drop_composite.py",
                                  "pipeline/beat15_listener_composite.py")
    for stale in ("19-the-drop", "b6dbd53b", "ce1e5ba2", "b19"):
        if stale in fetch_src:
            print("!! fetch_init.py still mentions %r after the swap -- refusing "
                  "to file a job that would fetch the wrong beat." % stale)
            return 4

    child["payload"] = {
        CHILD_DIR + r"\inpaint_fruit.py": inpaint_src,
        CHILD_DIR + r"\fetch_init.py": fetch_src,
        CHILD_DIR + r"\prompt.txt": PROMPT,
        CHILD_DIR + r"\negative.txt": NEGATIVE,
    }

    # ---- steps: the argv lists are the parent's with three substitutions --
    # ---- the working dir, the init filename and the init sha. Counted below.
    steps = []
    argv_tokens = argv_same = 0
    for step in parent["steps"]:
        s = dict(step)
        argv = swap_dir(list(step["argv"]))
        argv = [a.replace("19-the-drop-sapcomp-0819.png", INIT_NAME)
                 .replace("19-the-drop-sapcomp-mask-0819.png", MASK_NAME)
                 .replace("b6dbd53bffd0dae77eb410c7669a042c9a040fb3faf2a5f5a5032b7431418903", INIT_SHA)
                 .replace("ce1e5ba2f89e9cabd0f90a3316a1436605bfd152a23b7add994995e255bcf266", MASK_SHA)
                 .replace("b19-sapcomp", "b15-sapcomp")
                 .replace("ep2-b19-sapcomp-0819", "ep2-b15-sapcomp-0819")
                for a in argv]
        for old, new in zip(step["argv"], argv):
            argv_tokens += 1
            argv_same += 1 if old == new else 0
        if "--note" in argv:
            argv[argv.index("--note") + 1] = (
                DRY_NOTE if s["name"] == "dry" else RENDER_NOTE)
        s["argv"] = argv
        s["note"] = swap_dir(step.get("note", "")) if "note" in step else None
        if s["note"] is None:
            s.pop("note")
        steps.append(s)
    child["steps"] = steps
    child["artifacts"] = [
        CHILD_DIR + r"\b15-sapcomp-s20260819.png",
        CHILD_DIR + "\\" + INIT_NAME,
    ]

    # ---- the beat: ids, ownership, and the bar. -----------------------------
    child["id"] = "ep2-b15-sapcomp-0819"
    child["task"] = "ep2-b15-sapcomp-0819"
    child["beat"] = 15
    child["priority"] = 34
    child["est_minutes"] = 5
    child["owner"] = ("beat 15 lane, 2026-08-19 -- taken over from a crashed peer "
                      "and derived by pipeline/derive_b15_sapcomp_0819.py")
    child["consumer"] = (
        "THE EP2 CUT, which carries beat 15 as a SLATE. Twenty-four judged beat-15 "
        "artifacts (12 wave stills, 6 mac plates, 6 LTX motion takes) fail this beat "
        "and NOT ONE of them fails on the acting -- every one fails because the thing "
        "sharing the frame with him is not the sapling, which is the whole of "
        "beats.'15'.done_when. All six motion takes were animated from ONE init whose "
        "plant is a wiry weed topped with a white sphere, so no reseed can reach the "
        "bar. This is the init beat 15 has to have before it can be animated at all.")
    child["success"] = (
        "ONE 832x1216 png, its mask and its provenance sidecar, published into "
        "courier-box. THE BAR IS BEAT 15'S OWN: P1-P7 are carried VERBATIM from "
        "plate_scratch.py DRAFTS[15], where they were pre-registered before r1 existed "
        "and where r1 scored 6 of 7 against them. P3 is the one clause r1 failed and it "
        "is the clause this rung exists for. C8 is the composite half of the same "
        "question, and P8 is scoreable for the first time.")
    child["why"] = (
        "The plant is DRAWN rather than asked for. Two wording rungs closed the leaf "
        "count: r1's `two leaves on one thin stem` gave five blades on three nodes, and "
        "r2's `two leaves at the top of one bare stem` did not move the plant at all. "
        "composite-init-pattern.md 1 calls cardinality CLASS A -- 'the attribute is not "
        "a direction in the conditioning space at all, so there is no knob to turn' -- "
        "and Class A is the pattern's strongest case, because a composited count is not "
        "a sample from anything. pipeline/beat15_listener_composite.py removed the weed "
        "into the plate's own field and drew one canon sapling, $0 on the Mac, with two "
        "rounds rejected by eye first. Max change outside the mask is 0.0, so the six "
        "clauses r1 already passes are byte-identical to r1.")

    child["section_6_is_DISCHARGED_on_this_beat"] = (
        "READ THIS BEFORE REUSING ANY EARLIER BEAT-15 TEXT. Until today every beat-15 "
        "artifact was scored with GAZE DELIBERATELY UNSCORED, because STEWARDSHIP.md 6 "
        "was live on this beat: its staging was rewritten on 2026-08-17 with beats 12, "
        "13, 19 and 20 and leaves/002b-t0-c.yaml recorded 'approval_status: NOT YET READ "
        "BY HIM'. The founder read all three rewritten lines and approved them on "
        "2026-08-19 ('all approved', recorded in 5d6eb792), so 6 came off all five "
        "restaged beats and the approved line is now the thing to stage TO. That is why "
        "P8 below is scored rather than recorded. It is also why this job is a PLATE and "
        "not footage: 6 gated voice, footage and assembly, and its discharge does not "
        "make a still init into a pick.")

    child["bar"] = {
        "the_approved_line_this_is_staged_TO": (
            "node.md:98 as rewritten and approved 2026-08-19: 'He tips his head down and "
            "sideways until his EYES ARE LEVEL WITH THE TWO LEAVES, and talks to them "
            "from a hand's width away; both of them share the frame.' And "
            "beats.'15'.done_when, written 2026-08-15 retroactively from node.md so it "
            "could not be bent to fit existing takes: 'he LOOKS UP and the SAPLING IS IN "
            "THE SAME FRAME. Both in shot is the whole point of the beat -- a close-up of "
            "him looking up at nothing fails it however well he acts.' The two agree on "
            "the load-bearing half: BOTH OF THEM IN ONE FRAME, with a real sapling."),
        "P1_both_in_one_frame": (
            "he and the SAPLING ARE IN THE SAME FRAME, both wholly inside 832x1216, "
            "neither cropped. Twenty-four artifacts had not managed this with a real plant."),
        "P2_rooted_and_attached": (
            "one stem rises out of the grass with its base in shot and every leaf joins "
            "it. This clause killed eight of the twelve wave stills with detached leaves "
            "floating at the frame edges."),
        "P3_the_plant_is_the_sapling_AND_IT_IS_THE_CLAUSE_THIS_RUNG_EXISTS_FOR": (
            "Exactly ONE plant, TWO leaves, ONE thin stem, shorter than he is. Extra "
            "stalks, extra leaves, a bead-strung vine, a multi-node weed or a bud/ball at "
            "the tip all FAIL. This is the ONLY clause r1 failed -- 'the leaves sit on TWO "
            "OR THREE NODES, roughly four or five of them, where the bar says exactly "
            "two' -- and it is the axis two wordings could not move."),
        "P4_scale": (
            "the plant's top sits BELOW the seated goblin's head. The composite is 200 px "
            "tall with its apex 135 px below his head top at y 257, so this clause is "
            "carried from r1 by construction and a FAIL here means the sampler grew the "
            "plant."),
        "P5_outdoors_in_an_open_field": (
            "grass to the horizon, real sky, no interior, no wall panel, no floating disc "
            "of turf."),
        "P6_one_lean_adult_goblin": (
            "one figure, seated in the grass, lean and long-limbed with an angular skull, "
            "in a plaid patchwork cloak, both hands on his knees. Not a child, not a "
            "chibi, not standing."),
        "P7_not_a_close_up": "wide, whole body, and the plant reads.",
        "P8_HIS_EYES_ARE_LEVEL_WITH_THE_TWO_LEAVES_scored_for_the_first_time": (
            "his eye line falls INSIDE the blades. Measured on this plate at 4x: his "
            "pupils behind his spectacles are at y 370 and the composite's blades are "
            "centred at y 374 spanning y ~348-400. SCORED HONESTLY AS CARRIED BY "
            "CONSTRUCTION, not as something the sampler achieved -- the composite placed "
            "the blades at his measured eye level, so the only way this clause FAILS is if "
            "the inpaint MOVES them. That is a real risk worth a clause: the mask is "
            "dilated 12 px and the sampler is free inside it."),
        "P9_spectacles_recorded_from_r2_forward": (
            "he wears spectacles that no beat-15 prompt has ever asked for -- a third "
            "independent sighting of the unprompted-eyewear binding the beats 05/10 lane "
            "is chasing. Reported, and a change to them inside the mask is attributable to "
            "this job."),
        "C8_THE_ONE_VARIABLE": (
            "THE PLANT READS AS THE CANON TWO-LEAF SAPLING AND AS DRAWN CEL ART. Exactly "
            "two wide oval leaves with soft round tips on one thin rooted stem -- and the "
            "composite's flat procedural fill must have COME BACK as cel line work in the "
            "same weight and colour as the line art elsewhere in the frame. "
            "composite-init-pattern.md 7 names the pass tell and it is a POSITIVE one "
            "visible at 3x: 'If you cannot see a difference between your composite and the "
            "output, the pass is a paste.' The composite and a parent/composite A/B at 3x "
            "are committed at farm-out/ep2-b15-sapcomp-0819/ so the comparison can be made "
            "by anyone."),
        "how_scored": (
            "By eye at 1x and 3x on the plant region, against the committed composite side "
            "by side, and against the parent plate for the clauses r1 already passed. The "
            "numeric checks are FILTERS, never verdicts -- 'a metric agreeing with me is "
            "not a sample', and this repo retracted a hue finding the same day for "
            "averaging over a box instead of segmenting the object."),
        "numeric_filters": (
            "green blade blobs >=250 px in the plant zone (composite: 3 components, "
            "[3343, 3342, 414], because the two blades and the stem touch at the joint -- "
            "so 1 or 3 are both expected and the BLADE count is by eye); blade aspect "
            "against composite-init-pattern.md 8's pre-registered 1.6-2.6 band (composite: "
            "1.72); highpass sigma-3 std inside the drawn region, in -> out (pattern 7: "
            "RELOCATION into edges is the pass, magnitude alone is not); mean |delta| "
            "against the init inside the region (pattern 7: engagement is not success); "
            "px changed OUTSIDE the mask (composite: 0.0 against the parent)."),
    }

    child["failure_predicted_in_advance"] = (
        "FAIL-PASTE IS NAMED AS THE MOST LIKELY OUTCOME HERE, and it is a DIFFERENT "
        "prediction from the parent job's, on a measurement rather than a hunch. Beat 19's "
        "spec predicted FAIL-MATERIAL from composite-init-pattern.md 9's plate dependence "
        "and it did not fire. What is different about this init is its SIZE: the drawn "
        "footprint is 8540 px inside a 42792 px mask (4.23% of frame) against beat 19's "
        "drawn plant inside a 172847 px mask (17.08%), and the drawn structures here are "
        "THIN -- a stem 7.0 px at the root tapering to 2.1 px, and two blades 43x25 px. "
        "padding_mask_crop=64 upscales the crop, which is the countermeasure and the reason "
        "this is a prediction and not a refusal. But 12 of 40 steps over a small thin "
        "structure is the least conversion pressure any composite in this repo has been "
        "given, so 'the drawing comes back unconverted' is the honest expectation. If it "
        "fires, the named lever is the parent's own knob in the other direction -- "
        "strength 0.30 -> 0.40, which is ONE SAMPLE and no new code -- and NOT a wording, "
        "because the wording ladder on this beat is closed at two rungs.")

    child["pre_registered_fail_modes"] = {
        "FAIL-PASTE": (
            "the drawn shapes come back unconverted -- same flat fill, same uniform "
            "outline, no cel line work, no drawn vein or midrib. The 0.30-too-low "
            "direction, and the outcome named most likely above."),
        "FAIL-SHAPE": (
            "the sampler re-invents inside the mask: the stem splits, a blade is chewed or "
            "lance-tipped, the joint grows a third stub. The 0.30-too-high direction, which "
            "beat 10 hit at 0.45 by reading its own deepest composited line as an object "
            "boundary. The petiole/midrib here is capped at the plate's own outline step "
            "(213.9 -> 45.1) precisely to deny that."),
        "FAIL-COUNT": (
            "a leaf count other than exactly two, or a second stalk. THE AXIS TWO WORDINGS "
            "ALREADY FAILED -- r1 five blades on three nodes, r2 unmoved -- so this is the "
            "clause the whole rung exists for."),
        "FAIL-NODE": (
            "leaves reappear at a SECOND node on the bare stem. Distinct from FAIL-COUNT: "
            "the count can be right at the top and the stem still grow a lower pair, which "
            "is exactly how r1 failed."),
        "FAIL-TIP-BALL": (
            "a bud, ball or fruit appears at the stem tip or hanging off it. Named because "
            "the init under all six of this beat's motion takes was a weed topped with a "
            "WHITE SPHERE, so it is this checkpoint's demonstrated prior on this beat -- and "
            "because continuity genuinely wants a fig here (THE-SAPLING.md gives 002b 'two "
            "leaves + one thin side-branch' and the fig does not leave the plant until beat "
            "19). It is still a FAIL: the fig is a SECOND VARIABLE and frozen canon "
            "belonging to the fig lane, and beat 15's own P3 scores a bud at the tip as a "
            "fail. Flagged in the composite's sidecar rather than smuggled in."),
        "FAIL-VACANCY": (
            "a new noun grows where the weed was removed. composite-init-pattern.md 6: 'an "
            "emptied region is a hole the model fills with the largest available noun, and "
            "the negative does not reach it.' 21377 px were clone-filled from the plate's "
            "own field with 0 px left without a source, so a firing here means the law "
            "reaches further than the fill."),
        "FAIL-FIGURE": (
            "damage to a clause that PASSES. The mask necessarily puts 278 px inside his "
            "silhouette proper and 589 px inside the dilated protect halo, and his cloak's "
            "left edge runs x 291..370 through the mask's rows, so his cloak, his hands or "
            "his spectacles coming back wrong is attributable to this job and is a FAIL, "
            "not a wash. Reported with px counts, per region, as the parent's verdict did."),
        "FAIL-EYE-LEVEL": (
            "the sampler moves the blades off his eye line. P8 is carried by construction, "
            "so this is the only way it can fail -- and it is the clause the founder's own "
            "approved sentence turns on."),
        "FAIL-SEAM": (
            "a visible join, a row of dashes or a vertical edge where the weed was cloned "
            "out. Named because an earlier composite round DID produce exactly that -- grey "
            "dashes at x 233-257 and a seam at x 262 -- and was rejected by eye before any "
            "GPU. The fix was restricting the clone source to the measured clean field; "
            "this clause is how we find out whether the fix held under the sampler."),
        "FAIL-DECAL": (
            "any of pattern 5's five tells: texture axes not following the blade's own tilt; "
            "shading ignoring the frame's measured straight-down light (dx -0.072 dy "
            "-0.997); a swatch stopping short of or overrunning the object's own edge; "
            "visible tiling; detail at the wrong scale against his hands as an in-frame "
            "ruler. Never fired below 0.45 in thirty-one prior samples, so it is a real "
            "check rather than a formality only because this drawing is new."),
        "reporting_rule": (
            "EVERY mode above is reported BY NAME in the verdict whether or not it fired. "
            "Naming the most likely outcome in advance is what makes it meaningful when it "
            "turns out wrong."),
    }

    child["script_authority"] = (
        "Node 002b-first-citizen, approved_by: founder, and beat 15's rewritten staging "
        "approved by name on 2026-08-19 (5d6eb792). THIS PRODUCES A PLATE, NOT AN EPISODE: "
        "STEWARDSHIP 6 gates voice, footage and assembly, and a still init for an approved "
        "beat is none of those. inpaint_fruit.py writes approved: false and a provisional: "
        "block into its own sidecar, so nothing here can be mistaken for a pick or a "
        "plate_ack.")
    child["init_provenance"] = (
        "farm-out/ep2-b15-sapcomp-0819/%s, sha256 %s, drawn by "
        "pipeline/beat15_listener_composite.py on a Mac, $0, no model loaded. Its parent is "
        "farm-out/ep2-b15-mac-plate-0819/15-good-listener-mac-plate-r1s1.png sha256 "
        "8a9bd14b00c45ff50d0996b75cb4023bfbf8022f393b9e62c31f89f20fbf4ebe "
        "(animagine-xl-3.1, seed 20260819, Apple MPS, 141.1s, scored 6 of 7). Both are on "
        "origin/main in 1251caa0 and ce4ba822, so every sha asserted in this spec is "
        "verifiable by anyone who clones the repo -- and the composite was RE-DERIVED from "
        "the committed script and the committed parent before it was committed, producing "
        "the same bytes." % (INIT_NAME, INIT_SHA))
    child["mask_provenance"] = (
        "farm-out/ep2-b15-sapcomp-0819/%s, sha256 %s. 42792 px, 4.23%% of frame: the union "
        "of the removed weed's footprint and the drawn sapling's own footprint, dilated 12 "
        "and feathered 3. Extent x 121..310, y 285..604. 278 px of it fall inside his "
        "silhouette proper (target 0) and that exposure is what makes FAIL-FIGURE a real "
        "clause rather than a formality." % (MASK_NAME, MASK_SHA))
    child["negative_ordering"] = (
        "THE DEFECT CLASS IS FIRST ON PURPOSE, AND THE CEILING IS MEASURED RATHER THAN "
        "ESTIMATED. composite-init-pattern.md 4: animagine's budget is 77 CLIP tokens and "
        "'any word added silently drops the tail'. Every earlier spec in this repo has "
        "claimed headroom by counting WORDS. This one counted tokens on animagine's own "
        "vocab with pipeline/clip_token_count.py, and the first draft of this negative "
        "measured 85 OF 77 -- eight tokens would have been dropped in silence, off the tail, "
        "which is where `text, photorealism, 3d render, low quality` live. Trimmed to 24 "
        "terms measuring 71 of 77; the prompt measures 58 of 77. Control: the PARENT job's "
        "negative measures 71 on the same instrument, matching its own recorded claim of "
        "comfortable headroom, which is what says the counter is right rather than "
        "convenient. Ordering: the terms that name this beat's ACTUAL observed failures "
        "(leaf counts, extra stalk, multi-node weed, lance tips, bead/vine, a bud or ball at "
        "the tip) are at the FRONT, so if the tail is ever clipped it is `low quality` that "
        "goes and not the one thing this rung is about. It is also not load-bearing: the "
        "standing law is that the positive places what you want and the negative does not -- "
        "six times on this checkpoint a defect the negative forbade arrived anyway -- and "
        "here the structure is placed by the INIT, which is stronger than either.")
    child["derivation"] = {
        "parent": "pipeline/jobs/ep2-b19-sapcomp-0819.yaml",
        "by": "pipeline/derive_b15_sapcomp_0819.py",
        "inpaint_fruit_py_sha256_carried_byte_for_byte": inpaint_sha,
        "argv_tokens_identical_to_parent": "%d of %d" % (argv_same, argv_tokens),
        "keys_refused": (refused or "none") if not refused else
            ("REFUSED, not carried: %s. A derived spec that inherits its parent's verdict "
             "makes `grep verdict:` report a PASS belonging to a different clip -- which "
             "happened three times on 2026-08-19 before this guard existed."
             % ", ".join(refused)),
        "what_is_NOT_the_same": (
            "the init and its mask, the two prompt files, the bar, the fail modes, the "
            "beat/id/owner/consumer keys, and the working directory. Nothing a sampler "
            "reads: steps, cfg, strength, seed, pad-crop, blur, dtype and the model are the "
            "parent's."),
    }

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(child, fh, sort_keys=False, width=100,
                       default_flow_style=False, allow_unicode=False)

    print("parent  %s" % os.path.relpath(PARENT, REPO))
    print("child   %s" % os.path.relpath(OUT, REPO))
    print("keys refused: %s" % (", ".join(refused) or "none"))
    print("inpaint_fruit.py carried byte-for-byte, sha256 %s" % inpaint_sha)
    print("argv tokens identical to parent: %d of %d" % (argv_same, argv_tokens))
    print("init %s sha OK; mask %s sha OK" % (INIT_NAME, MASK_NAME))
    print("prompt  %d chars / %d comma-terms" % (len(PROMPT), PROMPT.count(",") + 1))
    print("negative %d chars / %d comma-terms" % (len(NEGATIVE), NEGATIVE.count(",") + 1))
    print("rc=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
