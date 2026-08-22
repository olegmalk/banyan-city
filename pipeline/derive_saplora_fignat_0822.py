#!/usr/bin/env python3
r"""SAPLING LoRA v2, STEP 3: one 0.30 inpaint over each figure+ground composite.

THIS FILE IS `derive_sapling_lora_naturalize_0821.py` WITH ONE CLAUSE INVERTED,
AND THE INVERSION IS THE WHOLE POINT OF v2. That file's header says, correctly
for v1:

    "NO FIGURE IN ANY PROMPT, and that is the point of the whole plate
     exercise: the existing composites carry the scavenger in every frame, and
     a subject LoRA fed a figure in every frame learns a figure."

It was right, and it worked, and it overshot. v1's 44 frames are figure-free
44 times out of 44, so `bnysapling` learned NO FIGURE as part of the subject:
asked for a goblin crouching beside it the LoRA drew none in 3 of 3, in the
no-regression pair at weight 0.8 it DELETED a figure that the base checkpoint
draws without it, and two of the four identity misses are the plant FUSED INTO
a creature's body (`pipeline/lora/registry.yaml` `bars_result`). The answer to
a monoculture is not the opposite monoculture. These eight frames carry a
figure and SAY SO IN THE CAPTION, which is the mechanism that keeps an
attribute out of the trigger -- the same one v1 used for leaf count and story
height, pointed at the axis that actually failed.

SO THE FIGURE IS IN THE POSITIVE AND OUT OF THE NEGATIVE, both deliberately.
`1boy` and `goblin` sit in v1's negative; here `1boy` is in the POSITIVE. That
is not decoration, it is THE PROMPT-SUMMONS LAW this tree paid four beats to
learn and re-confirmed on 2026-08-22: every composited object that has survived
i2v here was NAMED in its prompt, and the only two that vanished are the only
two whose prompt never mentioned them. The goblin is already drawn in the init
by ControlNet + IP-Adapter, so a 0.30 pass whose prompt does not mention him is
a pass being told he is not there -- over a mask that is 1.6% to 8.5% of the
frame, but the negative reaches the whole conditioning.

NOTHING ELSE IN THE RECIPE MOVES. 40 steps, cfg 7.5, strength 0.30, pad-crop
64, blur 8, animagine-xl-3.1, seed 20260820 -- `ep2-b16-sapcomp-r2-0820`'s
numbers by copy, the recipe that has now finished five composited plants plus
all 44 of v1's frames. The variable is the INIT, eight times, which is what a
dataset is. ONE SAMPLE BEFORE ANY BATCH is a rule about RECIPE CHANGES and the
recipe is not changing; the two things that ARE new -- the ground clause and
the figure -- were each sampled at the plate step (g1, judged at 1:1, verdict
on its own spec) before any of this was filed.

  python3 pipeline/derive_saplora_fignat_0822.py            # dry
  python3 pipeline/derive_saplora_fignat_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec            # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77  # noqa: E402
import build_saplora_figcomp_0822 as F                     # noqa: E402
import derive_saplora_figplate_0822 as P                   # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b16-sapcomp-r2-0820.yaml"
PARENT_DIRTOK = "b16sapcomp-r2-0820"
PARENT_OUTTOK = "b16-sapcomp"
SRC_DIR = "farm-out/ep3-saplora-figinit-0822"
SEED = 20260820   # the parent job's, unchanged

# IDENTICAL IN ALL EIGHT PROMPTS. It is the canon description and it is the
# only thing the LoRA is being taught, so it is the one clause that must not
# vary with the scene.
PLANT = ("a young sapling with exactly two wide oval leaves with soft round "
         "tips on one thin bare stem, rooted in the ground")

# THE FIGURE CLAUSE, ALSO IDENTICAL IN ALL EIGHT. Short on purpose: he is
# already drawn in the init by ControlNet and the IP-Adapter, so this clause's
# job is to tell the pass he EXISTS, not to redesign him. A longer description
# would spend CLIP budget competing with geometry that has already won.
FIGURE = "1boy, a small green goblin sitting behind it"

TIER_WORDS = {
    "s":  "a tiny sprout, small in a wide frame",
    "m":  "small, at middle distance",
    # v1 read "standing clear of the grass"; with the ground no longer grass
    # that phrase had to move, and "clear of the ground" would have said the
    # plant is off it. The clause means the plant is unobstructed, so it says so.
    "l":  "standing clear, mid frame",
    "xl": "close to the camera, large in frame",
}

# THE NEGATIVE IS v1'S WITH `1boy, people, goblin` REMOVED AND NOTHING ELSE
# TOUCHED. Those three are the only terms that contradict this batch, and
# removing exactly them -- rather than rewriting the string -- is what keeps
# every other guard v1 paid for. The leaf-count bans stay, because canon
# `sapling-two-leaves` rests on them and B5 is the one bar v1 passed on the
# committed ruler. `no humans` also comes out of the POSITIVE, where v1 had it.
NEGATIVE = ("three leaves, four leaves, many leaves, extra stalk, branching "
            "stem, pointed lance leaves, lobed leaves, bud, flower, fruit, "
            "large tree, thick branch, second plant, two plants, text, "
            "photorealism, 3d render, low quality, worst quality, blurry")


def prompt_for(cell, tier):
    ground = P.CELLS[cell][3]
    return ("%s, %s, %s, on %s, detailed cinematic anime, masterpiece, "
            "best quality, very aesthetic"
            % (PLANT, TIER_WORDS[tier], FIGURE, ground))


BAR = """JUDGED BY EYE AT CONTACT-SHEET LEVEL, AS A DATASET AND NOT AS A SHOT.
This frame is never cut into anything; its only consumer is the sapling LoRA's
v2 training set, so the bars are the ones a training frame has to clear. FIVE
OF THE SIX ARE v1'S VERBATIM. D3 IS INVERTED AND THAT IS THE POINT.
  D1 EXACTLY TWO LEAVES ON ONE STEM. Canon `sapling-two-leaves`. Three is a
     delete, so is one. The init has two by construction, so a three here means
     the 0.30 pass invented one and the finding is about the pass.
  D2 AVERAGE LEAVES. Canon `sapling-cotyledon-shape` -- ordinary, plain, no
     lobes, no lance, no exaggerated silhouette.
  D3 A FIGURE IS PRESENT, AND IT IS SEPARATE FROM THE PLANT. Inverted from
     v1, where a figure was a delete. Here a frame with NO figure is the
     delete, because a figure-free frame is what the set already has 44 of.
     The figure must also be DISTINCT: if the pass has fused the plant into
     him, or grown the stem out of his body, the frame is rejected -- that is
     the exact defect v1 produced and it must not be taught back in.
  D4 THE PLANT IS DRAWN, NOT PASTED. Line weight and cel shading in the
     plate's dialect. g7 IS THE NAMED RISK HERE: its palette sampled ONE
     green-dominant pixel, so its init plant is a single flat olive with no
     light/dark at all. If the pass does not give it shading, g7 is dropped.
  D5 THE SCENE SURVIVES, AND SPECIFICALLY THE GROUND DOES. The pass may not
     repaint the plate around the mask, and the material under the plant --
     cracked earth, path, rock, gravel, sand, leaf litter, mud -- must still
     read as that material afterwards. A frame whose ground has reverted to
     GRASS is a delete: it is the v1 monoculture growing back and it would be
     captioned with a ground word its pixels no longer support.
  D6 ONE PLANT. No second sapling grown out of the ground beside it."""

PREDICTED = """FIRST, AND IT IS THE ONE THIS BATCH IS ACTUALLY RISKING: D5, THE
GROUND REVERTING. The plate step already showed this checkpoint's prior pulling
toward vegetation -- the g1 sample was asked for bare ploughed earth and
returned a planted vegetable bed -- and a 0.30 pass runs 12 of 40 steps with
the ground word `on <material>` in the positive. The mask is 1.6-8.5% of the
frame so the pass should not reach the ground at all; if it does, the finding
is that pad-crop inpainting is not as local as five previous rounds have
assumed, which is worth knowing well beyond this lane.
SECOND: D3 FUSION. The plant sits in front of the figure's lower body on g3, g5
and g7 rather than beside him. Those three are where a 0.30 pass could merge
the two silhouettes, and they are the three to look at first. If they fuse, the
frames are dropped and the finding is that a dataset teaching `figure present`
must also teach `figure NOT overlapping`, which would be a second batch.
THIRD, AND IT IS ALREADY MEASURED RATHER THAN PREDICTED: g7's flat palette. It
is not a risk, it is a known defect with an unknown remedy -- the pass either
shades it or it does not.
NOT PREDICTED AND WORTH SAYING: the small tier is NOT a risk here the way it was
in v1. v1's third prediction was that masks near 1.3% of the frame would come
back untouched, and all 44 frames landed, so that floor was never found. The
smallest mask in this batch is g6 at 1.58%."""


def main() -> int:
    write = "--write" in sys.argv
    filed = []
    for cell, tier, root, height, tilt, lf, ls, side in F.ROWS:
        new_id = "ep3-saplora-fignat-%s-0822" % cell
        dirtok = "saplora-fignat-%s-0822" % cell
        init = "sapfig-%s-0822.png" % cell
        mask = "sapfig-%s-mask-0822.png" % cell
        want = {}
        for name in (init, mask):
            p = os.path.join(REPO, SRC_DIR, name)
            if not os.path.isfile(p):
                print("!! missing %s/%s -- run "
                      "build_saplora_figcomp_0822.py --write first"
                      % (SRC_DIR, name))
                return 1
            with open(p, "rb") as fh:
                want[name] = hashlib.sha256(fh.read()).hexdigest()

        prompt = prompt_for(cell, tier)
        np_ = assert_under_clip77("%s prompt" % new_id, prompt)
        nn_ = assert_under_clip77("%s negative" % new_id, NEGATIVE)

        fetch = '''#!/usr/bin/env python3
"""Fetch this dataset frame's composited init and its mask, refusing on any sha
mismatch. Both are on origin/main under %s/, so these
sha256s are verifiable against the repo by anyone who clones it. They were
drawn on a Mac by pipeline/beat16_sapling_composite.py, so they are NOT on the
box's courier worktree -- the courier only holds what the box produced."""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\%s"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "%s/")
UA = {"User-Agent": "banyan-city-saplora/1.0 (albert.numbro@gmail.com)"}
WANT = {
    "%s":
        "%s",
    "%s":
        "%s",
}

os.makedirs(OUT, exist_ok=True)
for name, want in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(RAW + name, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %%s -- refusing.\\n   want %%s\\n   have %%s"
                 %% (name, want, have))
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %%s %%d bytes sha %%s OK" %% (name, len(raw), have), flush=True)
''' % (SRC_DIR, dirtok, SRC_DIR, init, want[init], mask, want[mask])

        pose, pose_words, emotion, ground_word, _ = P.CELLS[cell]
        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "the sapling-LoRA v2 lane, 2026-08-22",
                "consumer": (
                    "THE SAPLING LoRA'S v2 TRAINING SET and nothing else. "
                    "This is figure frame %s of %d: plate cell %s (skeleton "
                    "%s, ground `%s`), plant rooted %s of him at %d px stem, "
                    "%s tier. It is not a beat, it does not enter a cut, and "
                    "it is not a candidate for one. v1 measured 44 of 44 "
                    "frames figure-free and 44 of 44 on grass; this frame is "
                    "neither."
                    % (cell, len(F.ROWS), cell, pose, ground_word, side,
                       height, tier)),
                "success": (
                    "ONE 832x1216 png at seed %d in which the plant reads as "
                    "DRAWN rather than composited, A FIGURE IS PRESENT AND "
                    "SEPARATE FROM IT, and the ground is still `%s` and not "
                    "grass. Scored on the six bars in `bar`."
                    % (SEED, ground_word)),
                "why": (
                    "SAPLING LoRA v2 NEEDS FRAMES THAT CARRY A FIGURE AND A "
                    "NON-GRASS GROUND, because those two absences are the "
                    "entire diagnosis of v1's three failing bars "
                    "(pipeline/lora/registry.yaml `bars_result`, verdict page "
                    "review/ep3-sapling-lora-0822/SHIP-0822.md). This is a "
                    "variety problem, so the fix is frames and not "
                    "hyperparameters and not a weight -- the weight ladder "
                    "was measured and its two curves never cross.\\n\\n"
                    "THE RECIPE IS UNCHANGED FROM THE 44 FRAMES OF v1 AND "
                    "FROM ep2-b16-sapcomp-r2-0820 BEFORE THEM: 40 steps, cfg "
                    "7.5, strength 0.30, pad-crop 64, blur 8, seed %d. The "
                    "INIT is the variable. What is new is in the PROMPT, and "
                    "it is one clause: the figure is named. v1's naturalize "
                    "banned `1boy, goblin` in its negative on purpose and "
                    "that is exactly the instruction being reversed."
                    % SEED),
            },
            overrides={
                "key:node": "003b-one-leaf-for-yes",
                "key:priority": 9,
                "key:est_minutes": 3,
                "key:sample": False,
                "payload:prompt.txt": prompt,
                "payload:negative.txt": NEGATIVE,
                "argv:--seed": str(SEED),
            },
            retoken=[(PARENT_DIRTOK, dirtok),
                     (PARENT_OUTTOK, "fignat-%s" % cell)],
            extra={
                "bar": BAR,
                "failure_predicted_in_advance": PREDICTED,
                "dataset_cell": {
                    "cell": cell, "plate_pose": pose,
                    "ground_material": ground_word,
                    "figure_present": True,
                    "plant_side": side, "scale_tier": tier,
                    "stem_px": height, "root": list(root),
                    "for": "pipeline/lora/manifest-sapling-v2.yaml",
                },
                "the_one_variable": (
                    "THE INIT. Against the other seven cells in this batch the "
                    "recipe, the seed, the plant clause, the figure clause and "
                    "the negative are identical; the ground word and the "
                    "composited geometry are what differ. Against v1's 44 "
                    "naturalize jobs the difference is TWO clauses: the figure "
                    "is named in the positive, and `1boy, people, goblin` are "
                    "removed from the negative. Nothing else in either string "
                    "moved."),
                "item_18_scope": (
                    "ZERO LTX PIXELS. SDXL plate (animagine-xl-3.1, ControlNet "
                    "+ IP-Adapter) -> a numpy composite -> this one SDXL "
                    "inpaint. DECISIONS.md item 18 bans training on LTX frames "
                    "specifically and is OPEN; this records scope and does not "
                    "close it. The v2 training job's stage step refuses any "
                    "frame whose manifest does not assert an animagine chain."),
                "clip77_measured_not_estimated": (
                    "positive %d of 77, negative %d of 77, counted on "
                    "animagine-xl-3.1's own vocab before this file was written."
                    % (np_, nn_)),
            },
            by="pipeline/derive_saplora_fignat_0822.py")

        child["steps"].insert(0, {
            "name": "fetch",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", fetch]})

        out = "pipeline/jobs/%s.yaml" % new_id
        # `derivation` is EXCLUDED because naming the parent is its entire job
        # -- it is the provenance record, and the `retokened` list inside it
        # necessarily prints both sides of every rename. Everything the runner
        # actually reads is checked.
        joined = repr({k: v for k, v in child.items() if k != "derivation"})
        if PARENT_DIRTOK in joined or PARENT_OUTTOK in joined:
            raise SystemExit("!! %s still names the parent job dir" % new_id)
        pay = child["payload"][r"C:\banyan-farm\%s\prompt.txt" % dirtok]
        # THE FIGURE MUST BE IN THE POSITIVE AND OUT OF THE NEGATIVE. This is
        # the one inversion the whole file exists for, so it is the one thing
        # asserted rather than trusted -- a copy-paste from the v1 deriver
        # would silently restore the ban and produce eight more frames of
        # exactly what the set already has too many of.
        neg = child["payload"][r"C:\banyan-farm\%s\negative.txt" % dirtok]
        if "1boy" not in pay or "goblin" not in pay:
            raise SystemExit("!! %s: the figure is not in the positive" % new_id)
        for dead in ("1boy", "goblin", "people", "no humans"):
            if dead in neg:
                raise SystemExit("!! %s: %r is in the NEGATIVE -- that is v1's "
                                 "instruction and this batch reverses it"
                                 % (new_id, dead))
        if P.CELLS[cell][3] not in pay:
            raise SystemExit("!! %s: the ground material is not in the positive"
                             % new_id)
        if write:
            derive_spec.write(child, out)
            print("wrote %s\n   clip77 %d/%d  ground=%-18s side=%-10s tier=%s"
                  % (out, np_, nn_, ground_word, side, tier))
        else:
            print("%-34s clip77 %d/%d  %s" % (new_id, np_, nn_, pay))
        filed.append(out)

    if not write:
        print("\n-- dry run, %d cell(s). re-run with --write." % len(filed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
