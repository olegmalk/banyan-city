#!/usr/bin/env python3
r"""SPECS FROM THE GOBLIN STANDARD. One deriver, two consumers, no hand-copying.

    python3 pipeline/derive_jerry_wave_0821.py poseset
    python3 pipeline/derive_jerry_wave_0821.py sceneset
    python3 pipeline/derive_jerry_wave_0821.py patchwave
    python3 pipeline/derive_jerry_wave_0821.py round2
    python3 pipeline/derive_jerry_wave_0821.py --selftest

WHY ONE FILE FOR BOTH. `pipeline/jerry_standard_0821.py` holds the recipe the
2026-08-21 steward ruling names; this file is the only thing that turns it into
job yaml. Two consumers want the same eighteen values and the way they have gone
wrong before is by copying seventeen of them:

  POSESET   -- the LoRA dataset's remaining gate. `curation-tile-0820.yaml` has
               been HELD since 08-20 on SEVEN usable frames in FOUR poses, and
               its own words are that a pose-locked character LoRA is worse than
               none. Eight poses at the standard is the arithmetic that changes.
  PATCHWAVE -- the seven ep2 beats where the goblin does not read as the tile.
               `ship-manifest.yaml goblin_design_audit_0820` names them: 02, 03,
               04, 07, 08, 13, 20. Post-ship patches; nothing here touches
               review/ep2-ship-0821 until a plate is judged and picked.

EVERY SPEC IS ONE VARIABLE FROM `ep2-jerry-face-k6a-0821`, and the variable is
named per rung. The wording, negative, seed, controlnet, scale, adapter, weight,
reference and head_frac are the standard's and are not this file's to move; what
moves is the SKELETON, the POSE WORDS that match it, and the MASK -- and the mask
is DERIVED from the skeleton rather than chosen, because the five head keypoints
translate as a rigid block and so does the box the adapter acts in.

THE ONE-SAMPLE RULE, DISCHARGED AND NOT WAIVED. Each mode files ONE frame per
question -- one per pose, one per beat -- not a seed fan. The recipe itself was
sampled thirteen times (k1..k6d). What these batches vary is the thing a single
sample cannot vary. Seeds fan in ROUND TWO, on the rungs that miss, which is
episode-loop-v2's two-rounds-per-question and not a scaled recipe.

$0 to emit. No model, no network, no GPU.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard      # noqa: E402
import derive_spec             # noqa: E402
import jerry_standard_0821 as S  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── THE POSE SET ─────────────────────────────────────────────────────────────
# suffix, skeleton stem, pose words
#
# `stand` IS NOT IN THIS LIST AND THAT IS DELIBERATE, not an omission. The
# standing pose at this recipe is `ep2-jerry-face-k6a-0821` itself -- same
# skeleton, same words, same mask, same seed -- and it is already rendered and
# published in farm-out/. Re-deriving it would emit a spec byte-identical to its
# own parent, which derive_spec refuses on the payload clause and which would
# burn a GPU minute to reproduce a frame we have. The standing frame enters the
# set from k6a's own output; these seven are the poses it cannot supply.
POSESET = [
    ("stride", "jerry-skel-h19stride-0820",
     "walking, arm outstretched, in tall grass, full body"),
    ("reach",  "jerry-skel-h19reach-0820",
     "arms up, in tall grass, full body"),
    ("point",  "jerry-skel-h19point-0820",
     "arm outstretched, pointing, in tall grass, full body"),
    ("hunch",  "jerry-skel-h19hunch-0820",
     "standing, hunched over, arms at sides, in tall grass, full body"),
    ("crouch", "jerry-skel-h19crouch-0820",
     "squatting, in tall grass, full body"),
    ("kneel",  "jerry-skel-h19kneel-0820",
     "kneeling, in tall grass, full body"),
    ("seat",   "jerry-skel-h19seat-0820",
     "sitting, hands clasped between knees, head lowered, in tall grass, "
     "full body"),
]

POSESET_WHY = """POSE %s of seven, at the standard the 2026-08-21 steward ruling
names. `pipeline/lora/curation-tile-0820.yaml` has been HELD since 08-20 and the
hold's reason has changed four times -- "no proportion", then "no face", then
"the wording cannot reach it", then "one clause and a dial" -- while the set
itself has never moved off SEVEN FRAMES IN FOUR POSES (b14 kneel x2, b15 sit x2,
b19 seat x3). That file's own gate says a pose-locked character LoRA is worse
than no LoRA, because it appears to work on the beat it was trained on and fails
silently everywhere else. Three of those four poses are seated.

So the gate is BREADTH AT A RECIPE THAT PASSES, and until k6a there was no recipe
that passed. Twelve tileset poses held the face and were bobbleheads; six skel
poses held the proportion and drew a blank egg; six wording rungs drew an eye
that was round or absent. k6a is the first frame in thirteen whose eye is not
oversized (1.07x) AND which keeps a mouth AND holds containment.

THE ONE VARIABLE HERE is the SKELETON and the two or three pose words that
describe it, moving together -- a kneeling skeleton under `standing, arms at
sides` is a contradiction rather than a control -- plus the MASK, which is not a
choice: it is k6a's own mask translated by this pose's head-block offset, and for
`stand` it is k6a's mask byte-for-byte."""

POSESET_CONSUMER = """THE JERRY LoRA TRAINING SET, and nothing else. A frame
passing every clause of the bar joins pipeline/lora/curation-tile-0820.yaml with
its caption written against canon's corrected tile read; a frame failing any
clause is REJECTED, because keeping near-misses is precisely what made the
31-frame set untrainable. No beat plate here, nothing promoted to a cut.

WHY REJECTION IS THE DEFAULT AND NOT PEDANTRY, in that file's own accounting: ten
beat-20 man-reads would have taught the trigger token a human face, twelve
bobbleheads a mascot, six blank eggs a blank egg. A LoRA learns what it is shown,
and after training the trigger token OUTRANKS every prompt that would argue with
the defect."""

POSESET_PREDICTED = """THE UPRIGHT POSES LAND AND THE FOLDED ONES ARE THE RISK,
and this time the risk has a NEW name, because the adapter is new. k6b/k6c/k6d
put the tile's PURPLE COWL back at 47.3%/17.8%/39.2% where the general adapter
had held it out for seven straight rungs -- the face weight transfers costume
through a mask that used to contain it, and it is coverage-gated. k6a at 20% read
0.0%. Nothing about this batch changes coverage, so the prediction is that the
cowl stays out; a cowl appearing on a FOLDED pose would say the mask translation
is letting the adapter act somewhere it did not before, and that is a mechanism
finding worth the rung.

SECOND PREDICTION, from the pose set that ran before this one: `crouch` and
`kneel` compress the skeleton, so if the net reads a folded skeleton as a SMALL
figure rather than a folded one they come back correctly posed and BOBBLEHEADED.
`reach` and `point` are the safest -- legs identical to `stand`'s, arms the only
change. `hunch` is the one I expect the net to soften into a duplicate of
`stand`: it differs by a quarter of a head height.

IF FIVE OF SEVEN PASS, the set reaches eight poses (these plus k6a's standing frame) at the tile's proportion
against seven frames in four, the majority read of the trigger token stops being
seated, and the LoRA's pose gate discharges on arithmetic rather than on hope."""


# ── THE PATCH WAVE ───────────────────────────────────────────────────────────
# Filled by patchwave(); see WAVE below.
PATCHWAVE_CONSUMER = """THE ep2 PATCH WAVE. A judged plate for beat %s, which
feeds that beat's motion re-derive; the motion spec is written when the plate is
picked, not before. THIS IS A POST-SHIP PATCH: review/ep2-ship-0821 is NOT
touched by this job and no frame is swapped into the cut until a plate is judged,
picked and its motion take passes its own bar.

WHY THIS BEAT IS IN THE WAVE: %s"""

PATCHWAVE_WHY = """BEAT %s OF THE SEVEN-BEAT WAVE, at the standard the
2026-08-21 steward ruling names. `review/ep2-ship-0821/sources/ship-manifest.yaml
goblin_design_audit_0820` read all 21 beats at 1:1 against the B tile and found
the goblin in ELEVEN, of which TWO are tile-faithful (15, 19), one is near-tile
on one attribute (14), one is unjudgeable (17), and SEVEN read as somebody else.
canon's 08-19 list said five; the audit adds 02 (grey child, on no design sheet
and never audited) and 07 (a full head of WHITE HAIR on a character whose canon
is bald, and it was filed among the four that were RIGHT).

This beat's break: %s

THE ONE VARIABLE against ep2-jerry-face-k6a-0821 is the SKELETON, the pose words
that match it, and the mask that follows the skeleton. The face wording, the
negative, the seed, the controlnet, the conditioning scale, the adapter, its
weight, its reference and head_frac 0.190 are the standard's and are untouched --
which is the whole point: if this beat's goblin comes back wrong, the wrongness
is attributable to the framing and not to a recipe someone re-typed."""

PATCHWAVE_PREDICTED = """THE FRAMING IS THE UNTESTED AXIS AND IT IS NAMED AS SUCH.
Every one of the thirteen ladder rungs was a FULL-BODY STANDING figure at
head_frac 0.190 in tall grass. This wave asks the same recipe for other stances
and other ground, and two things could break that no rung has tested:

  1. THE MASK. It is derived, not guessed -- k6a's box translated by the pose's
     head-block offset, exact because the head keypoints move rigidly -- but a
     DERIVED mask has never been rendered. If the adapter acts on the wrong
     region the face will be somewhere other than the head, and that is visible
     in one glance.
  2. THE COWL. k6b/k6c/k6d put the tile's purple cowl back through the same mask
     that held it for seven rungs, coverage-gated at 25%+ and clean at k6a's 20%.
     Coverage does not change here, so the cowl should stay out. If it appears,
     the mask translation is the cause and the finding is worth more than the
     plate.

WHAT I DO NOT PREDICT AND WILL NOT PRETEND TO: whether one seed lands the beat.
It is ONE frame per beat on purpose -- one sample per new framing -- and round
two fans seeds only on the beats that miss."""


def _emit(new_id, job_dir, hint, pose_words, why, consumer, success, variable,
          bar, predicted, beat, priority, extra_keys=None, seed=None,
          force=False, prompt=None, negative=None, mask=None):
    pose = S.SKELETONS[hint][0]
    mask = mask or S.mask_for(pose)
    extra = {
        "bar": bar,
        "the_one_variable": variable,
        "the_rung_this_is_one_variable_from": S.PARENT_ID,
        "failure_predicted_in_advance": predicted,
        "one_sample_rule": S.ONE_SAMPLE,
        "ip_adapter": S.ip_adapter_block(hint, pose),
    }
    extra.update(extra_keys or {})
    overrides = {
        "argv:--control": "pipeline/control/%s.png" % hint,
        "argv:--control-sha256": S.SKELETONS[hint][1],
        "argv:--ip-mask": mask,
        "argv:--repo-commit": S.ASSET_COMMIT,
        "payload:prompt.txt": prompt or S.prompt_for(pose_words),
        "key:beat": beat,
        "key:priority": priority,
        "key:est_minutes": 4,
    }
    if negative is not None and negative != S.NEGATIVE:
        overrides["payload:negative.txt"] = negative
    if seed is not None and seed != S.SEED:
        overrides["seed"] = seed
    child = derive_spec.derive(
        src=S.PARENT,
        new_id=new_id,
        fresh={"owner": "goblin standard lane, 2026-08-21",
               "why": why, "consumer": consumer, "success": success},
        overrides=overrides,
        retoken=[(S.PARENT_DIR_TOKEN, job_dir)],
        extra=extra,
        by="pipeline/derive_jerry_wave_0821.py",
    )
    # Stage and publish are REPLACED rather than retokened: the parent's stage
    # step pins jerry-skel-h19-0820's name against its sha, and a retoken that
    # renamed the file without renaming the digest would emit a job that fetches
    # the right bytes under the wrong name or dies on a mismatch. Authoring them
    # from the standard is the only way the three digests stay together.
    py = r"C:\banyan-farm\venv\Scripts\python.exe"
    child["steps"][0] = {"name": "stage",
                         "argv": [py, "-c", S.stage_step(job_dir, hint)]}
    child["steps"][-1] = {"name": "publish",
                          "argv": [py, "-c",
                                   S.publish_step(job_dir, new_id, hint)]}
    child["artifacts"] = [r"C:\banyan-farm\%s\out\%s-%s.png"
                          % (job_dir, new_id, S.ARM)]

    # Assert what was asked for is what came out. derive_spec already refuses an
    # override that matched nothing; this catches the opposite -- a value that
    # matched somewhere unintended, or a step the parent carried that we forgot.
    argv = [t for s in child["steps"] for t in s.get("argv", [])]
    for flag, want in (("--control", "pipeline/control/%s.png" % hint),
                       ("--control-sha256", S.SKELETONS[hint][1]),
                       ("--ip-mask", mask),
                       ("--ip-ref-sha256", S.IP_REF_SHA),
                       ("--ip-scale", S.IP_SCALE),
                       ("--ip-weight", S.IP_WEIGHT),
                       ("--scale", S.CONTROL_SCALE),
                       ("--arm", S.ARM),
                       ("--task", new_id)):
        if argv.count(flag) != 1:
            raise SystemExit("!! %s: %s appears %d times"
                             % (new_id, flag, argv.count(flag)))
        got = argv[argv.index(flag) + 1]
        if got != want:
            raise SystemExit("!! %s: %s is %r, want %r"
                             % (new_id, flag, got, want))
    # The `derivation` block RECORDS the retoken pair, so it names the parent
    # job dir on purpose and is excluded -- everywhere else the token surviving
    # would mean a path pointing at another job's directory on the card.
    joined = repr({k: v for k, v in child.items() if k != "derivation"})
    if S.PARENT_DIR_TOKEN in joined:
        raise SystemExit("!! %s still names the parent job dir" % new_id)
    if S.IP_WEIGHT_SHA not in joined:
        raise SystemExit("!! %s does not record the adapter digest" % new_id)

    out = "pipeline/jobs/%s.yaml" % new_id
    derive_spec.write(child, out, force=force)
    derive_fetch_guard.assert_fetch_urls_resolve(
        os.path.join(REPO, out),
        must_hold=(S.DRIVER, hint + ".png", S.IP_REF + ".png"))
    print("wrote %s   skel=%-28s mask=%s" % (out, hint, S.mask_for(pose)))
    return out


def poseset(force=False):
    written = []
    for suffix, hint, pose_words in POSESET:
        written.append(_emit(
            new_id="ep2-jerry-set-%s-0821" % suffix,
            job_dir="jerryset-%s-0821" % suffix,
            hint=hint, pose_words=pose_words,
            why=POSESET_WHY % suffix.upper(),
            consumer=POSESET_CONSUMER,
            success=("ONE 832x1216 png at seed %d, the k6a standard entire, "
                     "conditioned on %s.png at scale %s with the pose words "
                     "'%s' and the adapter masked to %s. Scored on the k6a bar; "
                     "any failure rejects it from the training set."
                     % (S.SEED, hint, S.CONTROL_SCALE, pose_words,
                        S.mask_for(S.SKELETONS[hint][0]))),
            variable=("the SKELETON and the pose words that describe it, moving "
                      "together ('%s'), plus the mask that follows the skeleton "
                      "by translation. Everything else -- wording, negative, "
                      "seed, controlnet, scale, adapter, weight, reference, "
                      "head_frac -- is ep2-jerry-face-k6a-0821's to the byte."
                      % pose_words),
            bar=S.BAR, predicted=POSESET_PREDICTED,
            beat=2, priority=44, force=force))
    return written


# ── THE SCENE x SCALE GRID ───────────────────────────────────────────────────
# The pose set moved ONE axis and left two standing. Every one of its seven
# frames is `in tall grass` at `full body` -- one scene, one scale -- and a LoRA
# trained on frames that share a background learns the background. The dataset
# gate wants breadth, and pose is only the axis that was cheapest to see.
#
# THE SCALE AXIS HAS ONE END AND IT IS THE WIDE END, and that is a committed
# ruling and not a shortcut. canon: `the tile is a wide full-body at which scale
# the model draws the face as a blank-eyed mask; THE CLOSER THE CROP, THE MORE IT
# RESOLVES THAT MASK INTO A DETAILED ADULT HUMAN MALE.` round2 closed beat 04's
# close-up rung on that measurement WITHOUT RUNNING IT and routed the beat's
# crop to post. So this grid does not file a medium or a close rung: those would
# be GPU minutes spent on a defect the record already measured. The dataset's
# close scale comes from cropping these plates, which is the same route round2
# named, and it is the curation lane's crop to make.
#
# What is left is genuinely two scales -- `full body` and `full body, wide shot`
# (the latter is committed precedent, patchwave beat 02) -- crossed with five
# backdrops taken from the episode's own prompt vocabulary rather than invented.
SCENESET_SCENES = [
    ("grass", "in tall grass"),
    ("field", "in an open green grass field, short grass"),
    ("hill",  "on a grassy hillside"),
    ("sky",   "in an empty field, low horizon, peach and gold sunrise sky"),
    ("noon",  "in an empty field under a midday-blue sky"),
]
SCENESET_SCALES = [("f", "full body"), ("w", "full body, wide shot")]
# Rotated across the grid so no cell repeats a triple and the poses spread too.
SCENESET_POSES = [
    ("st", "jerry-skel-h19-0820",       "standing, arms at sides"),
    ("rc", "jerry-skel-h19reach-0820",  "arms up"),
    ("pt", "jerry-skel-h19point-0820",  "arm outstretched, pointing"),
    ("sd", "jerry-skel-h19stride-0820", "walking, arm outstretched"),
    ("hn", "jerry-skel-h19hunch-0820",  "standing, hunched over, arms at sides"),
    ("cr", "jerry-skel-h19crouch-0820", "squatting"),
    ("kn", "jerry-skel-h19kneel-0820",  "kneeling"),
    ("si", "jerry-skel-h19sit-0820",    "sitting"),
    ("se", "jerry-skel-h19seat-0820",
     "sitting, hands clasped between knees, head lowered"),
]

SCENESET_WHY = """SCENE %s x SCALE %s, a DATASET-GATE FILLER and nothing else.

`pipeline/lora/curation-tile-0820.yaml` is held on SEVEN frames in FOUR poses and
its gate asks for BREADTH from a recipe that passes. The pose set answered the
pose axis and left the other two untouched: all seven of its frames are `in tall
grass` at `full body`, one scene and one scale, and a character LoRA trained on
frames that share a backdrop learns the backdrop as part of the trigger token --
the same failure mode the file already names for pose, one axis over.

THE ONE VARIABLE HERE IS THE BACKGROUND WORDS AND THE FRAMING WORD. The skeleton
comes from the committed set, the mask follows it by translation, and everything
the standard pins -- face wording, negative, seed, controlnet, scale, adapter,
weight, reference, head_frac -- is k6a's to the byte.

NO MEDIUM AND NO CLOSE RUNG IS FILED, on canon's own measurement that the closer
the crop the more the blank-eyed mask resolves into a detailed adult human male;
round2 closed that question without running it and routed the crop to post. The
close scale of this dataset is a crop of these plates, made by the lane that
curates it."""

SCENESET_CONSUMER = """THE JERRY LoRA TRAINING SET, and nothing else -- these are
DATASET-GATE FILLERS. THIS LANE DOES NOT JUDGE THEM. The chain lane that owns
`ep2-jerry-face-k6a-0821` and `curation-tile-0820.yaml` scores every frame on the
k6a bar and decides what joins the set; a frame failing any clause is REJECTED,
because keeping near-misses is exactly what made the 31-frame set untrainable. No
beat plate here, nothing promoted to a cut, nothing touching
review/ep2-ship-0821."""

SCENESET_PREDICTED = """THE BACKGROUND IS THE CHEAP AXIS AND THAT IS THE POINT.
Nothing in this grid touches the identity clauses, the adapter or its mask, so
the prediction is that pass rate tracks the POSE the cell drew and not the
backdrop -- upright cells land, folded cells carry the pose set's two known
risks (bobblehead compression, and the magenta neck that b03-r2/b20-r2 are
measuring at a second seed right now).

THE ONE THING THIS GRID CAN TEACH BEYOND FILLING THE SET: if a backdrop clause
moves a bar clause -- a sunrise sky warming the skin off the tile's green, a
hillside horizon tilting the figure out of containment -- that is a finding about
the recipe's robustness that the single-backdrop pose set could not have seen.
If it teaches nothing, the set still gains the breadth the gate asked for, which
is what these were filed for.

SEEDS ARE PINNED AT THE STANDARD'S %d ACROSS EVERY CELL, deliberately: with the
seed held, a cell that differs from k6a only in backdrop shows what the backdrop
did and nothing else."""


def sceneset(force=False):
    written, n = [], 0
    for scene_tag, scene_words in SCENESET_SCENES:
        for scale_tag, scale_words in SCENESET_SCALES:
            for _ in range(2):
                pose_tag, hint, pose_verb = SCENESET_POSES[n % len(SCENESET_POSES)]
                n += 1
                pose_words = "%s, %s, %s" % (pose_verb, scene_words, scale_words)
                # The `stand` x `tall grass` x `full body` cell IS k6a itself --
                # same skeleton, same words, same seed, already rendered and
                # published. derive_spec refuses it on the payload clause and it
                # would burn a GPU minute reproducing a frame we have, so the
                # rotation advances one and the cell keeps its two rungs.
                if pose_words == S.POSE_STAND:
                    pose_tag, hint, pose_verb = SCENESET_POSES[
                        n % len(SCENESET_POSES)]
                    n += 1
                    pose_words = "%s, %s, %s" % (pose_verb, scene_words,
                                                 scale_words)
                suffix = "%s%s%s" % (scene_tag, scale_tag, pose_tag)
                written.append(_emit(
                    new_id="ep2-jerry-scene-%s-0821" % suffix,
                    job_dir="jerryscene-%s-0821" % suffix,
                    hint=hint, pose_words=pose_words,
                    why=SCENESET_WHY % (scene_tag.upper(), scale_words.upper()),
                    consumer=SCENESET_CONSUMER,
                    success=("ONE 832x1216 png at seed %d, the k6a standard "
                             "entire, conditioned on %s.png at scale %s with the "
                             "pose words '%s' and the adapter masked to %s. "
                             "Scored on the k6a bar BY THE CHAIN LANE; any "
                             "failure rejects it from the training set."
                             % (S.SEED, hint, S.CONTROL_SCALE, pose_words,
                                S.mask_for(S.SKELETONS[hint][0]))),
                    variable=("the BACKGROUND WORDS ('%s') and the FRAMING WORD "
                              "('%s'), with the skeleton drawn from the committed "
                              "set and the mask following it by translation. "
                              "Everything else -- face wording, negative, seed, "
                              "controlnet, scale, adapter, weight, reference, "
                              "head_frac -- is ep2-jerry-face-k6a-0821's to the "
                              "byte." % (scene_words, scale_words)),
                    bar=S.BAR, predicted=SCENESET_PREDICTED % S.SEED,
                    beat=2, priority=46,
                    extra_keys={"dataset_gate_filler": (
                        "FILED BY THE FILER LANE, JUDGED BY THE CHAIN LANE. This "
                        "spec exists to give pipeline/lora/curation-tile-0820.yaml "
                        "breadth on the SCENE and SCALE axes the pose set left at "
                        "one value each. It makes no verdict and picks nothing."),
                        "scene_axis": scene_words,
                        "scale_axis": scale_words},
                    force=force))
    return written


# beat, skeleton stem, pose words, the audit's named break, the framing note
#
# THE POSE WORDS ARE THE BEAT'S OWN ACTION, read off
# genomes/sapling/nodes/002b-first-citizen/shots.md, and the skeleton is the
# published one nearest that action. Where the nearest is not near, the spec
# says so in `framing_gap` rather than pretending -- see beats 04 and 07.
WAVE = [
    ("02", "jerry-skel-h19stride-0820",
     "running, leaning forward, in tall grass, full body, wide shot",
     "CHILD AND GREY. Not green at all -- bone-grey/white with a huge round "
     "cranium, low pointed ears, closed eyes, a chubby child body, grey shirt "
     "and shorts. Breaks the tile on SPECIES COLOUR and on BUILD at once, and "
     "it has never appeared on a design sheet, in the 08-19 split, or in any "
     "re-render list. Its ship_status has read UNJUDGED since 08-17 because "
     "nobody looked.",
     "THE WORST IDENTITY BREAK IN THE CUT."),
    ("03", "jerry-skel-h19crouch-0820",
     "squatting, hiding behind a thin trunk, in tall grass, full body",
     "ADULT MAN. Human nose with nostrils, rounded human ear, nasolabial "
     "folds, flat olive rather than the tile's two-tone.",
     "on the 08-19 split."),
    ("04", "jerry-skel-h19hunch-0820",
     "standing, hunched over, leaning out past tall grass blades, upper body",
     "ADULT MAN, and the worst offender. Iris and pupil in a human eye, a full "
     "human nose, long swept-back elf spikes, brow furrows and cheekbones.",
     "THE TIGHTEST CROP IN THE CUT, which is why it is the worst offender -- "
     "the audit's own framing finding. Every clause of the bar is legible at "
     "this size, so this beat is the wave's hardest test and also its clearest "
     "read."),
    ("07", "jerry-skel-h19-0820",
     "standing, arms at sides, beside tall grass, full body",
     "ADULT MAN WITH WHITE HAIR ON A CHARACTER WHOSE CANON IS BALD, plus the "
     "guard's round spectacles, a human nose, and adult male height beside the "
     "guard.",
     "FILED AMONG THE FOUR THAT WERE 'RIGHT' on 08-19. It is not. `bald` is "
     "canon and this frame has hair; `hair` and `beard` are both in the "
     "standard's negative."),
    ("08", "jerry-skel-h19-0820",
     "standing, looking down at his own belly, arms at sides, in tall grass, "
     "full body",
     "CHILD. Small body, big head, closed sad eyes, buttoned coat -- the "
     "pre-ruling round one.",
     "on the 08-19 split. `child` and `chibi` are both in the standard's "
     "negative and head_frac 0.190 is the geometric answer to the big head."),
    ("13", "jerry-skel-h19seat-0820",
     "sitting, hands clasped between knees, head lowered, in tall grass, "
     "full body",
     "ADULT MAN. Human eye and lid, human nose, small human ear, a lined male "
     "face, normal head-to-shoulder ratio.",
     "THIS IS THE FRAME THE FOUNDER RULED ON, verbatim: 'this is one of the "
     "images where the goblin looks like an adult, which is wrong.' If any "
     "beat in the wave has to land, it is this one."),
    ("20", "jerry-skel-h19crouch-0820",
     "squatting, holding a small fruit with both hands, looking up, in tall "
     "grass, full body",
     "OLD MAN. Wrinkled forehead and jowls, a heavy human nose, an ear with no "
     "point at all, pupils.",
     "the 08-18 result 'the adult goblin draws, the chibi child is gone' was "
     "recorded as a FIX. Measured against the tile it is a different failure, "
     "not a repair. Nine of its 26 seeds also wore the guard's wire-rim "
     "glasses."),
]


# THE BEATS WHOSE FRAMING THE STANDARD DOES NOT YET COVER, named rather than
# papered over. Every one of the thirteen ladder rungs was a FULL-BODY STANDING
# figure at head_frac 0.190 in tall grass; two of these seven beats are not that
# shot, and filing them anyway is a deliberate round-one choice, not an oversight.
FRAMING_GAP = {
    "02": "NONE NAMED. shots.md wants a wide shot of a sprinting dive; "
          "jerry-skel-h19stride-0820 is a striding figure at the tile's "
          "proportion and the words carry the lean. Full body, tall grass, "
          "which is the regime the standard was measured in.",
    "03": "NONE NAMED. A crouch behind a thin trunk is the crouch skeleton "
          "plus the trunk in words. The trunk is the sapling's business, not "
          "the goblin's, and this plate is judged on the goblin.",
    "04": "YES, AND IT IS THE BIGGEST IN THE WAVE. shots.md calls beat 04 a "
          "CLOSE-UP -- head and one shoulder past the grass blades -- and the "
          "audit calls it 'the tightest crop in the cut and the worst "
          "offender'. The standard has NO close-up rung: every skeleton "
          "published is a full-body figure, the ip mask is a head box sized "
          "for one, and canon's own close-up finding is that `patchwork "
          "cloak` paints the SKULL at a head-and-shoulders crop while "
          "`ragged cloak` does not. This round-one frame is therefore the "
          "standard at its own framing with the beat's ACTION, and it "
          "answers a narrower question: does the k6a face survive a hunched "
          "lean-out at all. If it does, the close-up is round two and it is "
          "two variables (crop and cloak tag), which is a rung of its own and "
          "not a tweak to this one.",
    "07": "YES. The beat's SUBJECT is a guard -- shots.md: 'a round guard in "
          "mismatched armor thrusts one arm out, pointing off-frame' -- and "
          "the goblin is in frame beside him at adult male height with white "
          "hair and the guard's spectacles. This plate supplies THE GOBLIN "
          "ONLY, standing at the tile's proportion with `hair`, `beard` and "
          "`old man` in the negative. Composing him back beside the guard is "
          "the motion/composite step's problem and it is not solved here; "
          "what is solved here is whether a bald tile-true goblin is "
          "available to compose at all, which today he is not.",
    "08": "PARTIAL. shots.md is a deadpan TWO-SHOT, guard and goblin. Same "
          "answer as 07: the goblin alone, at proportion, looking down at his "
          "own belly, and the two-shot is composed downstream. The child read "
          "this beat carries is a BUILD defect and build is exactly what "
          "head_frac 0.190 supplies as geometry.",
    "13": "NONE NAMED. The goblin folding into the sapling's shade is the "
          "seatspan skeleton, which is the tile's own stance.",
    "20": "PARTIAL. The 08-17 knee-height rewrite has him crouched, holding "
          "the fig in both hands, looking level at the thinnest branch. The "
          "crouch skeleton and the words carry the stance; THE FIG'S COLOUR "
          "AND THE BRANCH are beat 20's own long-running canon question and "
          "are NOT touched here -- this plate is judged on the creature.",
}


def patchwave(force=False):
    written = []
    for beat, hint, pose_words, break_note, framing in WAVE:
        written.append(_emit(
            new_id="ep2-b%s-tilefix-p1-0821" % beat,
            job_dir="b%stilefix-p1-0821" % beat,
            hint=hint, pose_words=pose_words,
            why=PATCHWAVE_WHY % (beat, break_note),
            consumer=PATCHWAVE_CONSUMER % (beat, framing),
            success=("ONE 832x1216 png at seed %d, the k6a standard entire, "
                     "conditioned on %s.png at scale %s with the pose words "
                     "'%s' and the adapter masked to %s. Scored on the k6a bar "
                     "by eye at 1:1 against adult-b19-0819.jpg. A PASS is a "
                     "plate candidate for beat %s and nothing more -- the pick "
                     "is a separate judgement and the motion re-derive is a "
                     "separate spec."
                     % (S.SEED, hint, S.CONTROL_SCALE, pose_words,
                        S.mask_for(S.SKELETONS[hint][0]), beat)),
            variable=("the FRAMING -- this beat's stance and pose words -- and "
                      "the mask that follows the skeleton. Everything else is "
                      "ep2-jerry-face-k6a-0821's to the byte, so a bad result "
                      "here is attributable to the framing and not to a recipe "
                      "somebody re-typed."),
            bar=S.BAR, predicted=PATCHWAVE_PREDICTED,
            beat=int(beat), priority=22,
            extra_keys={"framing_gap": FRAMING_GAP[beat],
                        "post_ship_patch": (
                "review/ep2-ship-0821 IS NOT TOUCHED BY THIS JOB. The audit "
                "that named this wave says so in as many words: 'This is an "
                "audit, not a swap. No beat changes in the 2026-08-21 cut; "
                "every re-render it names is a post-ship patch.' A plate here "
                "becomes a candidate, a candidate becomes a pick, a pick "
                "becomes a motion spec, and only a passing motion take is "
                "swapped -- four judgements, none of them this job's.")},
            force=force))
    return written



# ── ROUND TWO ────────────────────────────────────────────────────────────────
# Filed after round one was judged by eye at 1:1 against the tile. Five of seven
# beats passed and are picked; two failed and are re-asked here, one seed-fan is
# added on the one fault that appeared twice. THIS IS THE SECOND AND LAST ROUND
# per question -- episode-loop-v2.
#
# ROUND ONE'S VERDICTS, one line each, so this table is readable without the
# ladder: b02 PASS, b03 PASS (magenta at the neck), b04 FAIL (stands upright;
# the beat is a lean-out), b07 PASS (bald, no spectacles -- the white hair is
# gone), b08 FAIL (a bare round pot belly, which is the CHILD read this beat
# exists to remove), b13 PASS and the best of the wave, b20 PASS (magenta at the
# neck).
#
# suffix, skeleton, pose words, seed, why-this-rung
ROUND2 = [
    ("b04", "r2", "jerry-skel-h19hunch-0820",
     "hunched over, leaning out to one side from behind tall grass, looking "
     "sideways, in tall grass, full body", None,
     "ROUND ONE STOOD UPRIGHT. The hunch skeleton differs from `stand` by a "
     "quarter of a head height and the net softened it exactly as the pose-set "
     "prediction said it might; `leaning out past tall grass blades` did not "
     "reach the body. The words now name the LEAN and the DIRECTION, which is "
     "the one variable.\n\n"
     "AND THE CLOSE-UP QUESTION IS ANSWERED BY NOT ASKING IT. Round one's "
     "framing_gap said beat 04's close-up was a rung of its own at two "
     "variables. It is not, and canon already contains the reason: `the tile "
     "is a wide full-body at which scale the model draws the face as a "
     "blank-eyed mask; THE CLOSER THE CROP, THE MORE IT RESOLVES THAT MASK "
     "INTO A DETAILED ADULT HUMAN MALE.` Asking this checkpoint for a close-up "
     "is asking it for the defect. The route is therefore to render FULL BODY, "
     "where the recipe is measured and passes, and obtain the beat's crop in "
     "post -- which is what the shipped b04 clip already is, a tight crop of a "
     "plate. The close-up rung is CLOSED WITHOUT BEING RUN, on canon's own "
     "measurement, and that is cheaper than four more frames."),
    ("b08", "r2", "jerry-skel-h19-0820",
     "standing, head bowed, looking down, arms at sides, in tall grass, "
     "full body", None,
     "ROUND ONE DREW A BARE ROUND POT BELLY. `looking down at his own belly` "
     "named the belly and the model drew one -- uncovered, protruding, and "
     "reading as a chubby CHILD, which is precisely the defect the audit "
     "logged against this beat ('small body, big head, closed sad eyes'). A "
     "positive draws what it names; the beat's belly is the GUARD'S line and "
     "the guard's pointing finger, not something the goblin's plate has to "
     "show. The words now ask only for the LOOK DOWN. One variable."),
    ("b03", "r2", "jerry-skel-h19crouch-0820",
     "squatting, hiding behind a thin trunk, in tall grass, full body", 20260824,
     "ROUND ONE PASSED THE FACE AND CARRIED MAGENTA AT THE NECK, and so did "
     "b20 and the crouch pose-set rung -- three frames, all of them FOLDED, "
     "while every standing frame in the wave read clean. THE MECHANISM IS "
     "NAMED AND IT IS OURS: the mask translates down with the head, but a "
     "seated or squatting figure is COMPRESSED, so the same 200x220 box that "
     "held only a head on a standing figure now overlaps neck and shoulder -- "
     "and k6b/k6c/k6d already proved this adapter transfers the tile's PURPLE "
     "COWL through a mask when it is given more to act on. This rung changes "
     "the SEED alone, which asks whether the magenta is the mechanism or the "
     "draw. If it survives the seed it is the mask and the fix is a smaller "
     "box on folded poses, which is a third rung and would be named then."),
    ("b20", "r2", "jerry-skel-h19crouch-0820",
     "squatting, holding a small fruit with both hands, looking up, in tall "
     "grass, full body", 20260824,
     "THE SAME SEED QUESTION AS b03-r2, on the second frame that showed the "
     "magenta neck. Two frames at one new seed is what separates a mechanism "
     "from a draw; one would not. The fig's COLOUR and the branch remain beat "
     "20's own canon question and are untouched here."),
]

ROUND2_PREDICTED = """SPLIT PREDICTION, AND IT IS FILED BEFORE THE RENDER.
b04-r2 and b08-r2 are WORDING rungs on a recipe whose wording route is otherwise
closed, and the reason they are expected to work where six face rungs did not is
that they move the POSE clause, not the identity clause -- the pose clause is the
one slot the standard leaves open, and every pose-set rung that changed it got
the pose it asked for. If b04 still stands upright, the finding is that the hunch
skeleton is under the net's resolution and the answer is a deeper-authored hint,
not more words.

THE SEED PAIR IS THE ONE THAT CAN TEACH SOMETHING EITHER WAY. If b03-r2 and
b20-r2 both come back clean, the magenta was the draw and round one's picks stand
with a noted seed. If BOTH keep it, it is the mask overlapping neck on compressed
poses and the fix is geometric -- shrink the box for folded skeletons -- which is
a change to jerry_standard_0821.mask_for and therefore to every folded frame
already rendered. If they SPLIT, one seed is not an instrument and the honest
answer is that we do not know yet."""


def round2(force=False):
    written = []
    for beat, tag, hint, pose_words, seed, note in ROUND2:
        written.append(_emit(
            new_id="ep2-%s-tilefix-%s-0821" % (beat, tag),
            job_dir="%stilefix-%s-0821" % (beat, tag),
            hint=hint, pose_words=pose_words,
            why=("ROUND TWO for beat %s, and the LAST round for this question.\n\n%s"
                 % (beat[1:], note)),
            consumer=("The ep2 patch wave's plate for beat %s. Round one is "
                      "judged and this rung either replaces its plate or "
                      "confirms it. POST-SHIP: review/ep2-ship-0821 is not "
                      "touched by this job." % beat[1:]),
            success=("ONE 832x1216 png, the k6a standard entire, with only the "
                     "named variable moved. Scored on the k6a bar by eye at 1:1 "
                     "against adult-b19-0819.jpg. There is no round three: if "
                     "this misses, the finding is recorded and the beat keeps "
                     "round one's plate or none."),
            variable=note.split(". ")[0] + ".",
            bar=S.BAR, predicted=ROUND2_PREDICTED,
            beat=int(beat[1:]), priority=20,
            extra_keys={"round": "TWO of two. episode-loop-v2 caps a question "
                                 "at two rounds and this is the cap, not a "
                                 "milestone on the way to more.",
                        "post_ship_patch": (
                            "review/ep2-ship-0821 IS NOT TOUCHED BY THIS JOB.")},
            seed=seed, force=force))
    return written



# ── THE TWO BEATS THE AUDIT OWED THAT ARE NOT MAN-READS ──────────────────────
# The seven-beat wave is the beats where the goblin reads as somebody else. The
# audit also named two beats that read as HIM and miss on ONE attribute each,
# and said so in as many words: "Beat 14 needs one attribute changed, the ears,
# not a re-render. Beat 17 needs nothing until a frame shows his face."
#
# BOTH ARE NOW CHEAPER TO FIX THAN TO ARGUE ABOUT, because the standard fixes
# each one for free as a side effect of what it already does:
#   b14's break is LONG TAPERING ELF SPIKES where the tile has short low
#   flanges. `pointy ears, long pointy ears, elf` are all in the standard's
#   negative and canon's measured finding is that the tile's ear ARRIVES
#   WITHOUT BEING ASKED FOR under exactly that suppression -- Danbooru has no
#   tag for it, so absence plus suppression is the only lever there is, and it
#   is already pulled. Every one of the eleven wave plates came back with short
#   low flanges and not one grew a spike.
#   b17's break is LEGS THAT RENDER BLUE-TEAL RATHER THAN GREEN on a back view.
#   `grey skin, pale skin` are in the negative and `colored skin, green skin`
#   is the wording's core; the eleven plates are uniformly green head to foot.
#
# b17 IS FILED AS A FRONT VIEW AND THAT IS A DEPARTURE, NAMED. The shipped beat
# is a back view and there is no back-view skeleton; every published hint is
# front-facing. This plate therefore cannot replace b17's framing on its own --
# what it can do is establish that the standard draws him green to the soles,
# which is the only thing b17's row actually complains about. If the colour
# holds, the b17 patch is a recolour or a re-pose, and that is a smaller
# question than it looks today.
WAVE2 = [
    ("14", "jerry-skel-h19kneel-0820",
     "kneeling, arms forward, in tall grass, full body",
     "NEAR TILE, ONE NAMED BREAK: long tapering elf spikes where the tile has "
     "short low flanges, plus a red-and-white striped scarf and no purple cowl. "
     "Eyes, dome, skin and folded stance already match the tile -- the audit's "
     "words are 'the ears are the whole gap'.",
     "THE EAR IS UNPROMPTABLE AND THAT IS WHY THE STANDARD FIXES IT. Danbooru "
     "has NO tag for a short low swept-back ear -- `short pointy ears` has zero "
     "posts, `round ears` does not exist, `long ears` is an ALIAS to `pointy "
     "ears` -- so no positive can request it. Canon's measured finding is that "
     "naming no ear tag at all and NEGATING both spike tags produces it anyway. "
     "The standard does exactly that, and eleven plates came back with flanges."),
    ("17", "jerry-skel-h19-0820",
     "standing, arms at sides, in tall grass, full body, barefoot",
     "UNJUDGEABLE ON THE FACE -- it is a back view -- but its LEGS RENDER "
     "BLUE-TEAL RATHER THAN GREEN, which is a species-colour break and is "
     "judgeable from any angle.",
     "A FRONT VIEW, WHICH IS A DEPARTURE AND IS NOT A REPLACEMENT FOR THE SHOT. "
     "There is no back-view skeleton; every published hint faces front. What "
     "this frame can settle is whether the standard draws him GREEN TO THE "
     "SOLES, which is b17's only actual complaint. Barefoot is in the words "
     "because beat 17 already ships barefoot and it matches the steward "
     "lower-half pick."),
]


def wave2(force=False):
    written = []
    for beat, hint, pose_words, break_note, note in WAVE2:
        written.append(_emit(
            new_id="ep2-b%s-tilefix-p1-0821" % beat,
            job_dir="b%stilefix-p1-0821" % beat,
            hint=hint, pose_words=pose_words,
            why=(PATCHWAVE_WHY % (beat, break_note)) + "\n\n" + note,
            consumer=PATCHWAVE_CONSUMER % (beat, note),
            success=("ONE 832x1216 png, the k6a standard entire, at seed %d. "
                     "Scored on the k6a bar by eye at 1:1, AND on this beat's "
                     "single named attribute, which is the reason it exists."
                     % S.SEED),
            variable=("the FRAMING for beat %s. The standard is otherwise "
                      "ep2-jerry-face-k6a-0821's to the byte." % beat),
            bar=S.BAR, predicted=PATCHWAVE_PREDICTED,
            beat=int(beat), priority=26,
            extra_keys={"the_single_attribute_this_beat_is_about": note,
                        "post_ship_patch": (
                            "review/ep2-ship-0821 IS NOT TOUCHED BY THIS JOB. "
                            "Beats 14 and 17 are the two the audit explicitly "
                            "took OUT of the re-render wave; this is the "
                            "cheaper check that the standard closes them "
                            "anyway, not a re-opening of them.")},
            force=force))
    return written



# ── THE AGE LADDER ───────────────────────────────────────────────────────────
# FOUNDER RULING, 2026-08-21, VERBATIM: "Younger, not chibi -- a kid/teen goblin,
# younger read than tile B, but NOT the killed round-chibi design."
#
# TILE B IS SUPERSEDED ON THE AGE AXIS AND ON NOTHING ELSE. Every creature
# attribute stays the tile's: blank white slit eyes, no nose bridge, one lipless
# line, the SHORT LOW SWEPT-BACK EAR, bald dome, green skin, patchwork cloak.
# Those are not on the table and nothing below touches them.
#
# TWO AXES, THREE POINTS EACH, NINE FRAMES, ONE BATCH, SEEDS PINNED.
#
#   GEOMETRY (rows) -- head_frac, the dial n5 already proved this tree controls
#   by manufacturing a bobblehead on demand from 0.190 -> 0.320 with everything
#   else held. Age reads primarily off head-to-body in a stylised figure.
#       h215  4.65 heads -- the teen end
#       h240  4.17 heads -- the kid end
#       h265  3.77 heads -- THE NAMED FAR END, expected to be too far
#
#   WORDING (columns) -- the AGE CLAUSE only. The identity clause, the tile
#   attributes and the framing are frozen.
#       w0  `lean wiry goblin`            the age word simply REMOVED. Control:
#                                         it isolates how much of the adult read
#                                         was geometry rather than the word.
#       w1  `young goblin, slim`          the ruling's direction, minimally.
#       w2  `teenage goblin boy, slim,    the ruling's direction with a face
#            soft rounded jaw`            cue, since he asked for a READ and not
#                                         only a proportion.
#
# THE NEGATIVE CHANGES BY EXACTLY ONE TERM AND IT IS THE RULING'S OWN TERM.
# `child` comes OUT -- he asked for a kid/teen read and negating `child` fights
# the ruling. `chibi` STAYS, and `super deformed`, `round-bellied` and `squat`
# are ADDED, because his floor is explicit: "NOT the killed round-chibi design".
# That is the whole difference between younger and the design killed on 08-20,
# and it is carried in the negative rather than hoped for.
#
# THE TILE'S OWN 5.26-HEAD READ IS NOT IN THE BATCH because it already exists:
# ep2-jerry-face-k6a-0821 is that frame at w-adult, and it goes on the picker
# page as the ANCHOR the founder is being asked to move away from.
AGE_SKELETONS = {
    "jerry-skel-h215-0821": ("stand",
        "adf9bc54f4882a4cce926906467489195f08c67bd917a0cc614055bce75a6064"),
    "jerry-skel-h240-0821": ("stand",
        "8d42ffbb42434449dabe3e9c06d19e20fe182097bc11d1abe9980a4ad41195e8"),
    "jerry-skel-h265-0821": ("stand",
        "16e74cf5bbb4b6fd648020279be8b4742ff8df1b1dfbc4b2cb18147ea4931844"),
}
S.SKELETONS.update(AGE_SKELETONS)

AGE_ROWS = [("h215", "jerry-skel-h215-0821", 0.215, 4.65, "the teen end"),
            ("h240", "jerry-skel-h240-0821", 0.240, 4.17, "the kid end"),
            ("h265", "jerry-skel-h265-0821", 0.265, 3.77, "THE NAMED FAR END")]


def age_mask(head_frac):
    """k6a's box SCALED about its centre by head_frac / 0.190.

    THE TRANSLATION RULE IS NOT ENOUGH HERE AND THAT IS THE ONE THING THIS
    LADDER CHANGES ABOUT THE STANDARD'S GEOMETRY. Every pose so far held
    head_frac at 0.190, so the head was the same SIZE in every frame and a
    translated box always covered it. This ladder moves head_frac itself: at
    0.265 the authored head is 1.39x k6a's, and k6a's 200x220 box -- which was
    already only a little larger than the 148x185 head it was drawn for --
    becomes SMALLER than the head it is supposed to mask. The adapter would then
    paint a face onto the middle of a skull and leave its edges to the
    checkpoint's own prior, which is the man-read.
    """
    k = head_frac / S.HEAD_FRAC
    x0, y0, x1, y1 = S.MASK_STAND
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    hw, hh = (x1 - x0) * k / 2.0, (y1 - y0) * k / 2.0
    r = [max(0, int(round(cx - hw))), max(0, int(round(cy - hh))),
         min(S.RENDER_W, int(round(cx + hw))),
         min(S.RENDER_H, int(round(cy + hh)))]
    return "%d,%d,%d,%d" % tuple(r)

AGE_COLS = [
    ("w0", "lean wiry goblin",
     "the age word simply REMOVED from k6a's clause -- the CONTROL, which "
     "isolates how much of the adult read was the geometry and how much was "
     "the word `adult`"),
    ("w1", "young goblin, slim",
     "the ruling's direction, minimally worded"),
    ("w2", "teenage goblin boy, slim, soft rounded jaw",
     "the ruling's direction with a FACE cue, because he asked for a younger "
     "READ and not only a younger proportion"),
]

AGE_TAIL = ("green skin, bald head, patchwork cloak, blank eyes, tsurime, "
            "jitome, thick eyebrows, half-closed eyes")
AGE_POSE = "standing, arms at sides, in tall grass, full body"

# k6a's negative, minus `child`, plus the three that hold the founder's floor.
AGE_NEG = ("lowres, worst quality, low quality, text, watermark, pointy ears, "
           "long pointy ears, elf, monster boy, pointy nose, dot nose, "
           "human face, wrinkled skin, old man, hair, beard, chibi, "
           "super deformed, round-bellied, squat, grey skin, pale skin")

AGE_BAR = """SCORED FOR ONE THING THE FOUNDER ASKED AND FOUR HE DID NOT.
  A1 AGE READ -- does he read YOUNGER than adult-b19-0819.jpg? This is the
     question and it is HIS, not the steward's. The batch exists to give him
     three options with pixels, not to pick one.
  A2 NOT THE KILLED DESIGN -- his own floor, verbatim: "NOT the killed
     round-chibi design". A rung that reads round-bellied, squat or mascot
     FAILS and is shown as the far end rather than offered as an option.
REGRESSION CLAUSES, and a rung that buys age by breaking these is not an option:
  T1 blank white eyes, no iris, no pupil.
  T2 no human nose -- no bridge, no tip, no drawn nostrils.
  T4 SHORT LOW SWEPT-BACK EAR FLANGES, not spikes. This one is load-bearing:
     Danbooru has NO tag for this ear, so absence-plus-suppression is the only
     thing that has ever produced it, and the age pivot must not cost it.
  C1 containment -- green skin head to foot, patchwork cloak, no purple cowl."""

AGE_PREDICTED = """w0 IS THE RUNG I EXPECT TO SURPRISE, and it is in the batch
for exactly that reason. Thirteen ladder rungs established that this checkpoint's
own prior for `goblin man` is a human adult male, and the IP-Adapter reference is
a crop of an ADULT tile's head. So removing the word `adult` may change nothing
at all -- in which case the age read is carried by geometry and the reference,
and the wording column is decoration. That is worth one third of a batch to know
before anyone writes a fourth wording.

h265 IS EXPECTED TO FAIL A2. n5 drew the killed design at 3.13 heads and 3.77 is
between it and the tile. If it reads chibi, the ladder has found the floor
empirically instead of guessing at it, and the picker page shows it AS the floor.

THE RISK THAT WOULD COST THE MOST IS T4. A younger read and a rounder head are
the same direction, and `round ears` is not a tag we can negate -- the ear
survives only because nothing asks for an ear and both spike tags are suppressed.
If the bigger head fractions bring back a spike or a human ear, the age pivot has
a cost nobody has priced, and it shows up in this batch rather than in a wave."""


def ageladder(force=False):
    written = []
    for rtag, hint, hfrac, heads, rnote in AGE_ROWS:
        for ctag, ageclause, cnote in AGE_COLS:
            new_id = "ep2-jerry-age-%s%s-0821" % (rtag, ctag)
            prompt = "masterpiece, best quality, very aesthetic, 1boy, solo, %s, %s, %s" % (
                ageclause, AGE_TAIL, AGE_POSE)
            written.append(_emit(
                new_id=new_id,
                job_dir="jerryage-%s%s-0821" % (rtag, ctag),
                hint=hint, pose_words=AGE_POSE,
                prompt=prompt, negative=AGE_NEG,
                mask=age_mask(hfrac),
                why=("AGE LADDER %s x %s. FOUNDER RULING 2026-08-21, VERBATIM: "
                     "\"Younger, not chibi -- a kid/teen goblin, younger read "
                     "than tile B, but NOT the killed round-chibi design.\"\n\n"
                     "TILE B IS SUPERSEDED ON THE AGE AXIS AND ON NOTHING ELSE. "
                     "Every creature attribute here is still the tile's and is "
                     "not on the table.\n\n"
                     "THIS RUNG: head_frac %s (%.2f heads, %s) x the age clause "
                     "`%s` (%s). Two axes, three points each, nine frames, one "
                     "batch, seeds pinned to k6a's %d so nothing but the two "
                     "named variables moves."
                     % (rtag, ctag, rtag, heads, rnote, ageclause, cnote,
                        S.SEED)),
                consumer=("/review/ep2-goblin-age-0821 -- a THREE-OPTION PICKER "
                          "for the founder, built from this batch with the tile "
                          "and a current adult wave frame as anchors. The age "
                          "read is R4 and this job does not decide it; it "
                          "supplies one of the nine pixels he decides from. "
                          "Nothing is promoted, no beat changes, and every "
                          "adult-design job in the queue is already held."),
                success=("ONE 832x1216 png at seed %d, the k6a adapter recipe "
                         "entire -- same face weight, same square reference at "
                         "head 20%%, same mask, same ip-scale, same openpose net "
                         "at 1.0 -- with ONLY the skeleton's head_frac and the "
                         "age clause of the wording moved. Scored on A1, A2 and "
                         "the T1/T2/T4/C1 regression clauses." % S.SEED),
                variable=("TWO, named because this is a GRID and not a rung: "
                          "the skeleton's head_frac (%s, %.2f heads) and the "
                          "age clause of the positive (`%s`). They are crossed "
                          "on purpose -- with three points on each axis the "
                          "grid separates them, which a sequence of one-variable "
                          "rungs could not do inside one batch, and the founder "
                          "is waiting."
                          % (rtag, heads, ageclause)),
                bar=AGE_BAR, predicted=AGE_PREDICTED,
                beat=2, priority=4,
                extra_keys={
                    "founder_ruling_verbatim": (
                        "Younger, not chibi -- a kid/teen goblin, younger read "
                        "than tile B, but NOT the killed round-chibi design"),
                    "what_is_superseded": (
                        "THE AGE AXIS ONLY. adult-b19-0819.jpg stops being the "
                        "reference for how old he is, which retires `lean wiry "
                        "adult goblin man`, the 5.2-head T8 target and k6a's "
                        "claim to the word STANDARD. It stays the reference for "
                        "every creature attribute, and the SHORT LOW EAR "
                        "especially -- Danbooru has no tag for it, so "
                        "absence-plus-suppression is the only thing that has "
                        "ever drawn it and the pivot must not cost it."),
                    "the_negative_changed_by_one_term_and_it_is_his": (
                        "`child` OUT -- he asked for a kid/teen read and "
                        "negating `child` fights the ruling. `chibi` STAYS, and "
                        "`super deformed`, `round-bellied`, `squat` are ADDED, "
                        "because his floor is explicit: NOT the killed "
                        "round-chibi design. The floor is carried in the "
                        "negative rather than hoped for."),
                    "one_sample_rule": (
                        "THIS IS THE SAMPLE, and it is nine because it is a 3x3 "
                        "GRID on two crossed axes -- not one recipe rendered "
                        "nine times. The adapter recipe underneath was sampled "
                        "thirteen times (k1..k6d) and is frozen here to the "
                        "byte; what varies is the two things the ruling names. "
                        "Nothing scales off this batch until the founder picks."),
                },
                force=force))
    return written


def _selftest():
    rc = derive_spec.selftest() or derive_fetch_guard.selftest()
    import jerry_standard_0821
    return rc or jerry_standard_0821._selftest()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    force = "--force" in argv
    modes = [a for a in argv if not a.startswith("-")]
    if "--selftest" in argv:
        return _selftest()
    if not modes:
        print(__doc__)
        return 2
    written = []
    for m in modes:
        if m == "poseset":
            written += poseset(force=force)
        elif m == "sceneset":
            written += sceneset(force=force)
        elif m == "patchwave":
            written += patchwave(force=force)
        elif m == "round2":
            written += round2(force=force)
        elif m == "wave2":
            written += wave2(force=force)
        elif m == "ageladder":
            written += ageladder(force=force)
        else:
            print("!! unknown mode %r -- poseset | sceneset | patchwave | round2"
                  % m,
                  file=sys.stderr)
            return 2
    print("\n%d spec(s). Next: box_enqueue each one --backlog." % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
