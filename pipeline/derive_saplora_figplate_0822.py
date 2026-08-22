#!/usr/bin/env python3
r"""SAPLING LoRA v2, STEP 1: plates that carry A FIGURE and NON-GRASS GROUND.

WHY THIS FILE EXISTS, IN ONE MEASUREMENT. `pipeline/lora/registry.yaml` records
the v1 result: `bnysapling` draws the canon two-leaf sapling (a first -- five
wording ladders had closed on it), and THREE of the five pre-registered bars
fail. All three trace to two monocultures in the 44-frame set, both named in
`pipeline/lora/README.md` before training and both measured after it:

    44 of 44 training frames are FIGURE-FREE  -> B2_figure 0/3, and the
      no-regression pair at 0.8 DELETES a figure that is present without the
      LoRA. Two of B1's four identity misses are the plant FUSED INTO a
      creature's body. The trigger learned "no figure" as part of the subject.
    44 of 44 stand on GRASS -> ground COLOUR generalises (brown autumn
      grassland 3/3) and ground MATERIAL does not (bare tilled earth 1/3; the
      other two returned a green meadow).

The v1 dataset was built goblin-free ON PURPOSE and that was the right call for
v1 -- `derive_sapling_lora_naturalize_0821.py` says so in its own header: "a
subject LoRA fed a figure in every frame learns a figure". THE ANSWER TO A
MONOCULTURE IS NOT THE OPPOSITE MONOCULTURE. v2's set carries BOTH kinds of
frame and names which it is in every caption, so figure-presence becomes a
caption VARIABLE -- the same mechanism that kept leaf count and story height out
of the trigger in v1, applied to the axis that actually failed.

WHY THE POSE ROUTE DRAWS THE FIGURE. `jerry_canon_0821` + `controlnet_plate.py`
is the only instrument in this tree that reliably BINDS a figure into a plate:
an OpenPose skeleton at ControlNet 1.0 plus the founder's own reference through
IP-Adapter. Prompting for a goblin without it is a lottery. It is used here
unchanged -- same reference, same head_frac, same adapter, same conditioning
strength, same seed -- and the two things this file varies are:

    THE SKELETON, which sets the figure's DISTANCE and its side of frame. The
      depth cells `sitfar60/50/42` were authored on 2026-08-22 for beat 16 and
      measured there: all three put an unoccupied foreground band in front of
      him (396 px at 60%), which is exactly the band a sapling has to stand in.
      They sit at cx 0.655, right of centre; the full-span poses sit at 0.5.
    THE LOCATION CLAUSE, which sets the GROUND MATERIAL. This is the axis the
      v1 plates never had: every one of the seventeen is a grass field, so
      `bnysapling` has never once seen its own roots meet anything else.

WHAT THIS FILE DOES NOT CLAIM. These are DATASET plates, not beat candidates.
They are not scored against the canon goblin bar, they are not plate candidates
for any beat, and nothing in `review/ep2-ship-0821` is touched. The goblin only
has to READ AS A FIGURE IN THE FRAME for the axis to be trained; his design is
beat work and belongs to the canon lane. That is stated so a passing plate here
is never mistaken for a passing plate there.

THE GREEN-PIXEL HAZARD, NAMED BEFORE THE RENDER BECAUSE IT IS THE ONE THAT
BITES. Step 2 composites the plant with `beat16_sapling_composite.py`, whose
`foliage_palette` builds the plant OUT OF THE PLATE'S OWN GREENS so it is not a
decal. On a bare-earth or sand plate the only green-dominant pixels may be THE
GOBLIN'S SKIN -- and a plant built out of his skin colour is the exact fusion
defect v1 already has. Every location clause below therefore keeps a REAL GREEN
IN THE FRAME (a hedgerow, scrub, a verge, ferns, dune grass) while the ROOTING
SURFACE stays non-grass. If a cell still comes back with no green but him, the
composite step refuses it at C5 and the cell is dropped rather than curated
around -- and the refusal is the finding.

ONE SAMPLE BEFORE ANY BATCH (founder, 2026-08-03). The location clause is a
RECIPE CHANGE on this route: no plate on the pose route has ever asked for
anything but "in tall grass". `--batch` therefore REFUSES until the sample cell
has been rendered AND judged -- a `verdict*` key on its own spec -- exactly the
gate `derive_jerry_canon_0821` puts in front of its own wave.

  python3 pipeline/derive_saplora_figplate_0822.py --sample     # g1, one cell
  python3 pipeline/derive_saplora_figplate_0822.py --batch      # the other 7
  python3 pipeline/derive_saplora_figplate_0822.py --cell g4
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard                    # noqa: E402
import derive_spec                           # noqa: E402
import jerry_canon_0821 as C                 # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b16-canon-w7a-0821.yaml"
PARENT_DIR_TOKEN = "b16canon-w7a-0821"
NODE = "003b-one-leaf-for-yes"
OWNER = "the sapling-LoRA v2 lane, 2026-08-22"
PY = r"C:\banyan-farm\venv\Scripts\python.exe"

SAMPLE_CELL = "g1"

# id -> (skeleton pose, location clause, emotion, ground caption word, why this
#        cell). The clause replaces "in tall grass" and NOTHING ELSE moves.
#
# THE GROUND WORD IS THE CAPTION TOKEN, not prose: it goes into the v2 caption
# verbatim as `rooted in <word>` so ground material is a named variable and the
# trigger is excused from carrying it. The clause and the word are kept
# together here so they cannot drift apart.
#
# DISTANCE IS THE SKELETON AND IT IS SWEPT ON PURPOSE. v1's figure bar asked for
# "a goblin crouching beside it" and got zero of three; a set that only ever
# shows a figure at one depth would answer that bar at one depth. The sweep is
# far (sitfar42) -> mid (sitfar50) -> near (sitfar60), three depths over seven
# materials, plus the sample's full-span `crouch` as the one figure-fills-the-
# frame cell. All three depth cells sit at cx 0.655, RIGHT of centre, which is
# a real limit of this batch and is recorded rather than papered over: the
# figure's SIDE does not vary here, only its distance. Side variety comes from
# the other half of the set -- the eight harvested ep2 frames, whose plants sit
# at cx 121..577 with the figure on either side of them -- and from where the
# plant is rooted at step 2, which is free to choose.
CELLS = {
    "g1": ("crouch",
           "squatting, in a ploughed field of bare brown earth, green hedgerow "
           "behind, full body", "wary", "bare tilled soil",
           "THE SAMPLE, and it is the bar's own words. v1 was asked for `bare "
           "tilled earth field` and returned a green meadow on two of three "
           "seeds. RENDERED AND JUDGED -- see `verdict_0822` on its own spec. "
           "J1 (a figure) and J3 (green that is not him) pass; J2 (the ground) "
           "fails on both faults this file predicted before the render, and "
           "the batch below is what that verdict says to do about them."),
    # -- THE BATCH, REWRITTEN AFTER THE SAMPLE. Two things changed and both are
    # the sample's verdict rather than a preference.
    #
    # ONE: EVERY CELL BELOW IS A DEPTH SKELETON. `crouch` is full-span and it
    # left NO unoccupied foreground band -- his boots reach the bottom edge and
    # the only rootable strips are the frame edges, too narrow for a plant
    # whose leaves reach 150 px sideways. sitfar60/50/42 leave a MEASURED
    # 396 px band at 60%, and `ep2-b16-sapnat4-0822` is the existence proof:
    # the same plant rooted at x=190 on a sitfar60 plate, standing clear of
    # him, moved 9 px by the 0.30 pass. Three depths over seven materials, with
    # the DEPTH repeating and the MATERIAL varying -- that is the right way
    # round for this sweep, and it is not the way the first table had it.
    #
    # TWO: THE MATERIAL IS THE SUBJECT OF THE CLAUSE, not its location. The
    # sample asked for `in a ploughed field of bare brown earth` and got a
    # PLANTED VEGETABLE BED: the earth arrived, `bare` did not. Each clause
    # below leads with the surface the pose sits ON, and the crop ban in
    # CROP_BAN carries what the adjective could not.
    "g2": ("sitfar60",
           "sitting on dry cracked bare earth, a green hedgerow far behind, "
           "full body", "deadpan", "dry cracked earth",
           "The sample's material, asked for properly. `bare` failed as an "
           "adjective inside a location clause and is retried as the SURFACE "
           "the pose sits on, with the crop ban carrying the rest."),
    "g3": ("sitfar50",
           "sitting on a bare dirt path, grass verges to either side, full "
           "body", "worried", "a dirt path",
           "The mixed cell on purpose: grass IS in frame and the rooting "
           "surface is not it. v1 has two path plates (u08, r08) and rooted on "
           "their verges every time, so `path` has never once been the ground "
           "the plant actually stands on -- v1's ground failure is partly a "
           "CAPTION failure and this cell is the pixel half of it."),
    "g4": ("sitfar42",
           "sitting on flat grey rock, green moss in the cracks, full body",
           "relief", "flat grey rock",
           "The FURTHEST figure in the batch (42% span) on the hardest "
           "material. Rock is the one ground that cannot be mistaken for a "
           "colour shift of grass, which is precisely the distinction v1's "
           "ground bar could not make: brown autumn grassland 3/3, bare tilled "
           "earth 1/3."),
    "g5": ("sitfar60",
           "sitting on a grey gravel track, green weeds at the far edge, full "
           "body", "sheepish", "gravel",
           "A granular material at the batch's nearest depth. Gravel and sand "
           "are the two textures whose failure mode is `it drew grass anyway`, "
           "and that is readable at a glance rather than by measurement."),
    "g6": ("sitfar50",
           "sitting on pale dry sand, green dune grass far behind, full body",
           "deadpan", "pale dry sand",
           "The palest ground in the set, and the hardest case for "
           "`foliage_palette`, which needs real plate greens to build the "
           "plant out of. The dune grass is there for that and the composite "
           "step measures whether it was enough instead of assuming it."),
    "g7": ("sitfar42",
           "sitting on a forest floor of fallen brown leaves, green ferns "
           "behind, full body", "worried", "fallen leaves",
           "Organic but not grass, which is the boundary case for whether the "
           "trigger learned `grass` or learned `soft green stuff`. At the "
           "furthest depth so it is not confounded with g4's rock."),
    "g8": ("sitfar60",
           "sitting on a wet muddy track after rain, a green verge behind, "
           "full body", "alarmed", "wet mud",
           "Wet ground. v1's only wet plates (v05 moor, v12 puddles) are still "
           "GRASS, so wetness has been trained and the wet MATERIAL has not. "
           "The specular half is already known to survive the 0.30 pass."),
}

# ADDED TO THE NEGATIVE FOR EVERY CELL, AND FOR ONE MEASURED REASON. The sample
# came back a planted vegetable bed -- rows of low cabbage-like plants over the
# soil that was asked for. A two-leaf sapling composited into a bed of similar
# green plants would teach the trigger that its subject appears in a crowd of
# its own kind, which is a worse defect than the grass monoculture this batch
# exists to break and which defeats the leaf-count bar as well.
#
# TERMS ARE ADDED, NEVER STRIPPED, and the distinction is load-bearing. Beat
# 16's w5 round DELETED four "inert" containment terms from this exact negative
# and BROKE THE EYE on all four cells; the finding recorded then was that
# "adding X did nothing" does not license "removing X is free". Nothing is
# removed here. This is the only change to the negative side in the whole batch
# and the risk of an addition is named rather than assumed away: if the eye or
# the costume moves against g1, this string is the first suspect.
# IT IS TWO WORDS BECAUSE THE BUDGET IS SIX TOKENS, MEASURED NOT GUESSED. The
# parent negative already costs 71 of animagine's 77, so the first draft of
# this ban -- eight terms, "vegetable garden, crop rows, cabbages, potted
# plant, bushes, flowers, sapling, seedlings" -- measured 93 and the emitter
# REFUSED it. That refusal is the guard working: an over-long negative does not
# error at the card, it silently drops its tail, and the tail is whatever was
# added last.
#
# `crops, seedlings` (75 of 77, two tokens of margin) is the pair chosen over
# `crops, plants` and `crops, bushes, flowers` at the same or higher cost, and
# the reason is the GREEN-PIXEL HAZARD at the top of this file. A blanket ban
# on `plants` or `bushes` would also suppress the hedgerow, ferns, moss and
# dune grass that each clause deliberately keeps in frame so
# `foliage_palette` has a green that is NOT the goblin's skin to build the
# plant out of. `crops, seedlings` names the sample's actual defect -- rows of
# low cultivated plants -- and nothing else.
CROP_BAN = "crops, seedlings"

# THE GROUND WORDS MAY NOT COLLIDE WITH GRASS. A cell whose caption word says
# grass would be a fifty-second grass frame wearing a new name.
for _cid, _row in CELLS.items():
    if "grass" in _row[3]:
        raise SystemExit("!! cell %s ground word %r says grass" % (_cid, _row[3]))


def _clip77(label, text):
    import clip_token_count as clip
    c = clip.Clip()
    n = c.count(text)[0] + clip.SPECIALS
    if n > clip.CEILING:
        raise SystemExit("!! %s is %d of %d -- the tail would be DROPPED and "
                         "the tail is the pose and the LOCATION, which is the "
                         "whole variable of this batch" % (label, n,
                                                           clip.CEILING))
    return n


def _sample_judged():
    """The batch is gated on a verdict key existing on the sample's spec."""
    import yaml
    p = os.path.join(REPO, "pipeline/jobs/%s.yaml" % _cell_id(SAMPLE_CELL))
    if not os.path.isfile(p):
        return False, "the sample spec %s does not exist yet" % os.path.basename(p)
    with open(p, encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    key = [k for k in spec if k.startswith("verdict")]
    if not key:
        return False, ("%s carries no `verdict*` key -- the sample has not been "
                       "judged by eye at 1:1. ONE SAMPLE BEFORE ANY BATCH means "
                       "the batch waits." % os.path.basename(p))
    return True, "judged: %s" % key[0]


def _cell_id(cid):
    return "ep3-saplora-fig%s-0822" % cid


def emit(cid, priority=8, force=False):
    if cid not in CELLS:
        raise SystemExit("!! no cell %r; have %s" % (cid, ", ".join(sorted(CELLS))))
    pose, pose_words, emotion, ground_word, cell_why = CELLS[cid]
    sample = (cid == SAMPLE_CELL)
    stem = C.SKELETONS[pose]
    mask = C.head_box(pose)
    prompt = C.prompt_for(pose_words, emotion)
    # The sample rendered on the parent's negative untouched; every cell after
    # it carries CROP_BAN, which is the sample's verdict. See CROP_BAN above --
    # terms are ADDED, never stripped.
    negative = C.NEGATIVE if sample else (C.NEGATIVE + ", " + CROP_BAN)
    new_id = _cell_id(cid)
    job_dir = "saplora-fig%s-0822" % cid

    n_pos = _clip77("%s prompt" % new_id, prompt)
    n_neg = _clip77("%s negative" % new_id, negative)

    fresh = {
        "owner": OWNER,
        "consumer": (
            "THE SAPLING LoRA v2 DATASET, and nothing else. This plate is step "
            "1 of three: a figure-bearing, non-grass-ground plate here; "
            "`beat16_sapling_composite.py` draws the canon two-leaf sapling "
            "onto it at step 2 ($0, local, no GPU); one 0.30 SDXL inpaint "
            "finishes it at step 3. The finished frame enters "
            "`pipeline/lora/manifest-sapling.yaml` with a caption naming BOTH "
            "the ground material (`%s`) and the figure's presence, and v2 "
            "retrains on it. IT IS NOT A BEAT CANDIDATE." % ground_word),
        "success": (
            "ONE 832x1216 png at seed %d carrying (a) A FIGURE THAT READS AS A "
            "FIGURE and (b) A ROOTABLE NON-GRASS GROUND PLANE the plant can "
            "stand on. Both are scored in `judge`. The goblin's DESIGN is not "
            "scored here and a design miss is not a fail -- see "
            "`what_is_not_scored_here`." % C.SEED),
        "why": (
            "SAPLING LoRA v2, PLATE CELL %s.\n\n%s\n\n"
            "THE GAP THIS BATCH EXISTS TO CLOSE, measured not asserted. v1 "
            "trained on 44 frames of which 44 are figure-free and 44 stand on "
            "grass. Bars B2_figure (0/3), B2_ground (4/6) and B3 "
            "(no-regression at 0.8, which DELETED a figure) all fail on those "
            "two facts and on nothing else -- the full score is in "
            "pipeline/lora/registry.yaml `bars_result` and the verdict page is "
            "review/ep3-sapling-lora-0822/SHIP-0822.md. This is a variety "
            "problem, so the fix is frames and not hyperparameters.\n\n"
            "THE ONE VARIABLE AGAINST ep2-b16-canon-w7a-0821 IS THE LOCATION "
            "CLAUSE (and, across the batch, the skeleton). The reference, the "
            "adapter, the adapter scale, head_frac %.3f, ControlNet %s and "
            "seed %d are byte-identical to w7a's, so a plate that comes back "
            "wrong is attributable to the words that name the ground."
            % (cid, cell_why, C.HEAD_FRAC, C.CONTROL_SCALE, C.SEED)),
    }

    extra = {
        "ip_adapter": dict(C.ip_adapter_block(pose),
                           ref="%s/%s.png" % (C.ASSET_DIR, C.IP_REF),
                           ref_sha256=C.REF_SHA[C.IP_REF], scale=C.IP_SCALE),
        "dataset_cell": {
            "cell": cid,
            "pose": pose,
            "ground_material": ground_word,
            "caption_clause": "rooted in %s" % ground_word,
            "figure_clause": "with a small green goblin in the frame",
            "for": "pipeline/lora/manifest-sapling.yaml, v2",
        },
        "judge": (
            "JUDGED AT 1:1, TWO CLAUSES, AND THE SECOND ONE IS THE RUNG.\n\n"
            "  J1 THE FIGURE. Is there ONE creature in the frame that reads as "
            "a figure -- a head, a body, limbs, at the pose asked for? Design "
            "is not scored (see below). Two figures, no figure, or a shape "
            "that does not resolve is a FAIL.\n"
            "  J2 THE GROUND, and this is the whole point of the cell. Is the "
            "near foreground %s -- the MATERIAL, readable as itself at 1:1 -- "
            "and is there an unoccupied band of it the plant can be rooted in "
            "without touching him? A cell that returns A GREEN MEADOW has "
            "reproduced v1's own failure at the plate step and is a FAIL; that "
            "is exactly what the LoRA did when asked for bare tilled earth.\n"
            "  J3 GREEN IS PRESENT SOMEWHERE THAT IS NOT HIM. Step 2's "
            "`foliage_palette` builds the plant out of the plate's own greens. "
            "If the only green-dominant pixels in the frame are the goblin's "
            "skin, the composited plant will be built out of HIS colour -- the "
            "fusion defect v1 already has, arriving through the palette. Each "
            "clause names a hedgerow, scrub, verge, moss, weeds, dune grass or "
            "ferns for this reason. RECORDED, and the composite step measures "
            "it: C5 refuses the cell if the fill luma disagrees with the "
            "field." % ground_word),
        "what_is_not_scored_here": (
            "THE GOBLIN'S DESIGN. This is a dataset plate for a SAPLING LoRA, "
            "not a beat candidate, and the canon bar in "
            "ep2-b16-canon-w7a-0821 does NOT travel with it. The subject being "
            "trained is the plant; the figure has to be PRESENT so the trigger "
            "stops meaning `no figure`, and that is the entire requirement. A "
            "plate whose ears or eyes miss the founder's image is still a "
            "usable dataset frame and is NOT a candidate for any beat. Said "
            "here so a pass on this page can never be quoted as a pass on "
            "that one."),
        "the_one_variable": (
            "THE LOCATION CLAUSE, `%s`, in place of w7a's `in tall grass`; and "
            "across the batch the SKELETON (%s here), which sets the figure's "
            "distance and side. Everything else in the recipe is w7a's."
            % (pose_words, pose)),
        "the_rung_this_is_one_variable_from": (
            "ep2-b16-canon-w7a-0821 -- the plate that put ground in front of "
            "him after four cells of negative, four of distance clause and one "
            "of conditioning strength had all failed to. Its foreground band "
            "is what makes the pose route usable for a dataset at all."),
        "failure_predicted_in_advance": (
            "TWO, NAMED BEFORE THE RENDER.\n"
            "  1. THE LIGHTING/GROUND WORD LOSES TO THE MODEL'S PRIOR. This is "
            "documented on this exact checkpoint: round 5 of the field batch "
            "asked for a green meadow under `cold clear winter light` and got "
            "a SNOWFIELD (v10), and `alpenglow` got snow and conifers (v14) -- "
            "the lighting word carried the ground with it. Here the ground "
            "word is the one that must win, against a prior that has drawn "
            "tall grass on every plate this route has ever made. If a cell "
            "comes back grass, the lever is NOT a negative (four cells of "
            "negative are already measured dead against this route's "
            "composition) -- it is to make the material the SUBJECT of the "
            "clause rather than its location.\n"
            "  2. THE ONLY GREEN IS HIM. See J3. The clause carries a green "
            "that is not the goblin for this reason, and the composite step "
            "measures it rather than trusting it."),
        "clip77_measured_not_estimated": (
            "positive %d of 77, negative %d of 77, counted with "
            "animagine-xl-3.1's OWN vocab by pipeline/clip_token_count.py. The "
            "location clause is the TAIL of the positive, so a spec that "
            "overran would silently drop the one thing this batch varies -- "
            "which is why it is counted here and not estimated."
            % (n_pos, n_neg)),
        "item_18_scope": (
            "ZERO LTX PIXELS. This plate is SDXL text-to-image "
            "(animagine-xl-3.1) under ControlNet + IP-Adapter, and every frame "
            "downstream of it is that plate -> a numpy composite -> one SDXL "
            "inpaint. DECISIONS.md item 18 bans training on LTX frames "
            "specifically; the training job's stage step refuses any frame "
            "whose manifest does not assert an animagine chain. Item 18 is "
            "OPEN and is the founder's to rule on -- this records scope, it "
            "does not close it."),
        "post_ship_patch": (
            "review/ep2-ship-0821 IS NOT TOUCHED BY THIS JOB, and neither is "
            "any beat page. This is dataset material for a LoRA that has not "
            "passed its bars."),
    }
    if sample:
        extra["one_sample_rule"] = (
            "THIS IS THE ONE SAMPLE FOR THE WHOLE BATCH. The location clause "
            "is a recipe change on this route -- every plate the pose route "
            "has ever drawn says `in tall grass` -- so seven more cells wait "
            "on this frame being LOOKED AT at 1:1. --batch refuses to emit "
            "until this spec carries a `verdict*` key. g1 is the sample "
            "because its material is the bar's own words: v1 was asked for "
            "`bare tilled earth field` and returned a green meadow.")

    overrides = {
        "argv:--control": "pipeline/control/%s.png" % stem,
        "argv:--control-sha256": C.SKELETON_SHA[stem],
        "argv:--ip-ref": "pipeline/control/%s.png" % C.IP_REF,
        "argv:--ip-ref-sha256": C.REF_SHA[C.IP_REF],
        "argv:--ip-mask": mask,
        "argv:--ip-scale": C.IP_SCALE,
        "argv:--repo-commit": C.ASSET_COMMIT,
        "argv:--scale": C.CONTROL_SCALE,
        "argv:--seed": str(C.SEED),
        "argv:--task": new_id,
        "payload:prompt.txt": prompt,
        # THE SAMPLE DID NOT OVERRIDE THE NEGATIVE AND THAT WAS DELIBERATE. It was
        # byte-identical to w7a's (derive_spec refuses an "override" that
        # changes nothing, which is how this was caught), so it carries through
        # the derivation untouched. The record already says why it must:
        # beat 16's w5 round stripped four "inert" containment terms out of
        # this exact negative and BROKE THE EYE on all four cells. The
        # variable here is the location clause and nothing on the negative
        # side moves with it. Every cell AFTER the sample overrides it with
        # CROP_BAN appended, because the sample came back a planted vegetable
        # bed and a crowd of similar green plants is a worse teacher than the
        # grass it replaced.
        "key:node": NODE,
        "key:priority": priority,
        "key:est_minutes": 4,
        "key:sample": bool(sample),
    }
    if not sample:
        overrides["payload:negative.txt"] = negative
    child = derive_spec.derive(
        src=PARENT, new_id=new_id, fresh=fresh, overrides=overrides,
        retoken=[(PARENT_DIR_TOKEN, job_dir)], extra=extra,
        by="pipeline/derive_saplora_figplate_0822.py")

    # BEAT IS DROPPED, NOT CARRIED. The parent is a beat-16 spec; this job is
    # not beat work and a `beat:` key on it would be a lie a reader would
    # believe. derive_spec carries it as structure, so it comes off here.
    child.pop("beat", None)

    child["steps"][0] = {"name": "stage",
                         "argv": [PY, "-c", C.stage_step(job_dir, stem, C.IP_REF)]}
    child["steps"][-1] = {"name": "publish",
                          "argv": [PY, "-c",
                                   C.publish_step(job_dir, new_id, stem, C.IP_REF)]}
    child["artifacts"] = [r"C:\banyan-farm\%s\out\%s-%s.png"
                          % (job_dir, new_id, C.ARM)]

    # ---- every flag the frame is conditioned on, asserted on the EMITTED argv.
    argv = [t for s in child["steps"] for t in s.get("argv", [])]
    for flag, want in (("--control", "pipeline/control/%s.png" % stem),
                       ("--control-sha256", C.SKELETON_SHA[stem]),
                       ("--ip-ref", "pipeline/control/%s.png" % C.IP_REF),
                       ("--ip-ref-sha256", C.REF_SHA[C.IP_REF]),
                       ("--ip-mask", mask),
                       ("--ip-scale", C.IP_SCALE),
                       ("--ip-weight", C.IP_WEIGHT),
                       ("--scale", C.CONTROL_SCALE),
                       ("--seed", str(C.SEED)),
                       ("--arm", C.ARM),
                       ("--task", new_id)):
        if argv.count(flag) != 1:
            raise SystemExit("!! %s: %s appears %d times"
                             % (new_id, flag, argv.count(flag)))
        got = argv[argv.index(flag) + 1]
        if got != want:
            raise SystemExit("!! %s: %s is %r, want %r" % (new_id, flag, got, want))

    joined = repr({k: v for k, v in child.items() if k != "derivation"})
    if PARENT_DIR_TOKEN in joined:
        raise SystemExit("!! %s still names the parent job dir" % new_id)
    if C.IP_WEIGHT_SHA not in joined:
        raise SystemExit("!! %s does not record the adapter digest" % new_id)

    pay = child["payload"][r"C:\banyan-farm\%s\prompt.txt" % job_dir]
    # THE LOCATION CLAUSE IS THE VARIABLE, SO IT IS THE ONE THING ASSERTED
    # PRESENT. A spec that dropped it would render a grass plate under a
    # non-grass name and the whole batch would be a null nobody could read.
    if pose_words not in pay:
        raise SystemExit("!! %s: the pose and LOCATION are not in the positive"
                         % new_id)
    if "in tall grass" in pay:
        raise SystemExit("!! %s: the parent's `in tall grass` survived into the "
                         "positive -- this cell would be a fifty-second grass "
                         "frame" % new_id)
    for live in ("pointy ears", "mandarin collar"):
        if live not in pay:
            raise SystemExit("!! %s: %r is not in the positive" % (new_id, live))

    out = "pipeline/jobs/%s.yaml" % new_id
    derive_spec.write(child, out, force=force)
    derive_fetch_guard.assert_fetch_urls_resolve(
        os.path.join(REPO, out),
        must_hold=(C.DRIVER, stem + ".png", C.IP_REF + ".png"))
    print("wrote %s\n   skel=%-30s ground=%-18s clip77=%d/%d\n   +  %s"
          % (out, stem, ground_word, n_pos, n_neg, pay))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="emit %s only" % SAMPLE_CELL)
    ap.add_argument("--batch", action="store_true",
                    help="emit every cell EXCEPT the sample; gated on its verdict")
    ap.add_argument("--cell", help="emit one cell by id")
    ap.add_argument("--priority", type=int, default=8)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    if a.sample:
        return 0 if emit(SAMPLE_CELL, priority=a.priority, force=a.force) else 1
    if a.cell:
        return 0 if emit(a.cell, priority=a.priority, force=a.force) else 1
    if a.batch:
        ok, why = _sample_judged()
        if not ok:
            print("!! BATCH REFUSED -- %s" % why)
            print("   ONE SAMPLE BEFORE ANY BATCH (founder, 2026-08-03). Render")
            print("   %s, look at it at 1:1, then add a verdict key to its spec."
                  % _cell_id(SAMPLE_CELL))
            return 1
        print("sample gate: %s" % why)
        for cid in sorted(CELLS):
            if cid == SAMPLE_CELL:
                continue
            emit(cid, priority=a.priority, force=a.force)
        return 0

    print("cells (%d):" % len(CELLS))
    for cid in sorted(CELLS):
        pose, words, emo, ground, _ = CELLS[cid]
        print("  %-3s %-9s %-20s %s" % (cid, pose, ground, words))
    print("\n--sample emits %s; --batch emits the rest once it is judged."
          % _cell_id(SAMPLE_CELL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
