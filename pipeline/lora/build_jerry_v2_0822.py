#!/usr/bin/env python3
r"""THE JERRY v2 DATASET, ASSEMBLED FROM THE ADMITTED CELLS AND NOTHING ELSE.

v1'S DATASET WAS NEVER TRAINED AND MUST NOT BE REVIVED. `train-jerry-0820.yaml`
is held at the top of its own file: `manifest-jerry-0821.yaml`'s 15 frames were
curated against the ADULT read at head_frac 0.190 through wording that says
`lean wiry adult goblin man`, and the founder superseded that on 2026-08-21. The
four eye rounds that followed were all vetoed -- "these are not my goblin" -- and
`route_closure_2026_08_22` closed the whole prompt-side route. EVERY FRAME IN
v1'S SET IS ANIMAGINE'S GUESS AT HIS FACE. Not one of them is his drawing.

v2'S FRAMES ARE HIS DRAWING. Each one is `taste/refs/goblin-canon-founder-0821.png`
-- the picture he picked with "dude, this is how the goblin should look" -- cut
to a framing, mirrored or not, and re-lit by an img2img pass at strength <= 0.40
that `goblin-i2i-route-0822.md` measured cannot invent a face because it never
runs the steps where faces are decided. That is the whole argument for this
dataset and it is a mechanism rather than a hope.

WHAT THIS FILE REFUSES TO DO, AND EACH REFUSAL IS A LESSON THAT COST SOMETHING.

  * IT NEVER GLOBS. The frames are named, one per admitted cell, and a cell that
    is not in the admissions file is not in the set no matter what is on disk.
    Globbing a directory is how a dropped frame gets trained on.
  * IT NEVER RE-CAPTIONS A FRAME TO MATCH WHAT ARRIVED. The caption was written
    before the render, in the cell table, and is conditional on the render. A
    frame whose ground did not arrive is DROPPED, not relabelled -- the caption
    comes out of `derive_goblin_dataset_0822.caption_for` and this file has no
    code path that can edit one.
  * IT VERIFIES EVERY sha256 AGAINST THE FRAME ON DISK and writes it into the
    manifest, which is the item-18 gate the trainer re-checks before it stages.
  * IT REFUSES A SET THAT IS ONE CAMERA. If any of the three framings admits
    nothing, the set is the pose-locked dataset `curation-tile-0820` refused, and
    this exits nonzero saying so.

THE REPEAT IS ARITHMETIC AND IT IS PRINTED. `pipeline/research/character-lora-sdxl-0820.md`
section 5 puts our target at ~1200 image passes. With N admitted frames over 10
epochs the repeat is round(1200 / (10 * N)), and the resulting pass count and
optimizer-step count are both printed so the training spec can quote a measured
number instead of a plan.

  python3 pipeline/lora/build_jerry_v2_0822.py            # dry
  python3 pipeline/lora/build_jerry_v2_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "pipeline"))
import derive_goblin_dataset_0822 as D                    # noqa: E402

ADMISSIONS = "pipeline/lora/admissions-jerry-v2-0822.yaml"
CAPTION_DIR = "pipeline/lora/captions/jerry-v2-0822"
MANIFEST = "pipeline/lora/manifest-jerry-v2-0822.yaml"
TARGET_PASSES = 1200
EPOCHS = 10


def frame_path(cell: str) -> str:
    """Where the runner's courier lands this cell's only output."""
    return "farm-out/ep2-jds-%s-0822/b13-jds-%s-s%d.png" % (
        cell, cell, D.SEED0 + int(cell[1:]))


def load_admissions() -> dict:
    import yaml
    p = os.path.join(REPO, ADMISSIONS)
    if not os.path.isfile(p):
        raise SystemExit(
            "!! %s does not exist. The set is built from a JUDGED list, not "
            "from whatever is on disk -- write the admissions file first, one "
            "entry per rendered cell, each `admit: true|false` with a reason."
            % ADMISSIONS)
    return yaml.safe_load(open(p, encoding="utf-8"))


def main() -> int:
    write = "--write" in sys.argv
    adm = load_admissions()
    rows = adm["cells"]

    unknown = [c for c in rows if c not in D.CELLS]
    if unknown:
        raise SystemExit("!! admissions names cells that do not exist: %s"
                         % ", ".join(sorted(unknown)))

    admitted = [c for c in sorted(rows) if rows[c].get("admit")]
    dropped = [c for c in sorted(rows) if not rows[c].get("admit")]
    if not admitted:
        raise SystemExit("!! nothing admitted -- there is no dataset")

    # THE ONE-CAMERA REFUSAL. `curation-tile-0820` refused to unblock a goblin
    # dataset on seven frames in four poses, in its own words: "a pose-locked
    # character LoRA is worse than no LoRA because it appears to work on the
    # beat it was trained on." Framing is this set's only geometric axis, so a
    # framing that admits nothing is that refusal arriving again.
    by_framing = {}
    for c in admitted:
        by_framing.setdefault(D.INITS[D.CELLS[c][0]][2], []).append(c)
    missing = [f for f in ("full body", "cowboy shot", "portrait")
               if not by_framing.get(f)]
    if missing:
        raise SystemExit(
            "!! %s admitted ZERO frames. A set that is one camera trains a "
            "distance, not a character -- curation-tile-0820 refused a goblin "
            "dataset for exactly this and its refusal stands. Re-render that "
            "framing or drop the run; do NOT back-fill from another framing."
            % " and ".join(missing))

    N = len(admitted)
    repeat = max(1, round(TARGET_PASSES / float(EPOCHS * N)))
    passes = N * repeat * EPOCHS
    steps = passes // 2  # train_batch_size 2

    frames = []
    for cell in admitted:
        rel = frame_path(cell)
        p = os.path.join(REPO, rel)
        if not os.path.isfile(p):
            raise SystemExit("!! %s is admitted and %s is not on disk" % (cell, rel))
        sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
        init_key, strength, _gc, ground, _lc, light = D.CELLS[cell]
        frames.append({
            "cell": cell,
            "image": rel,
            "sha256": sha,
            "caption_file": "%s/%s.txt" % (CAPTION_DIR, cell),
            "caption": D.caption_for(cell),
            "init": init_key,
            "framing": D.INITS[init_key][2],
            "ground": ground,
            "light": light,
            "strength": strength,
            "why_kept": rows[cell].get("why", ""),
        })

    print("admitted %d of %d   dropped %d" % (N, len(rows), len(dropped)))
    for f in sorted(by_framing):
        print("   %-12s %2d frames" % (f, len(by_framing[f])))
    print("   grounds  %2d distinct" % len({f["ground"] for f in frames}))
    print("   lights   %2d distinct" % len({f["light"] for f in frames}))
    print("   mirrored %2d of %d" % (sum(1 for f in frames
                                         if f["init"].endswith("-flip")), N))
    print("   repeat %d  ->  %d image passes, %d optimizer steps at batch 2 "
          "(target ~%d)" % (repeat, passes, steps, TARGET_PASSES))

    if not write:
        print("\n-- dry run. re-run with --write.")
        return 0

    cdir = os.path.join(REPO, CAPTION_DIR)
    os.makedirs(cdir, exist_ok=True)
    for f in frames:
        with open(os.path.join(REPO, f["caption_file"]), "w",
                  encoding="utf-8") as fh:
            fh.write(f["caption"] + "\n")

    import yaml
    doc = {
        "subject": "jerry",
        "trigger": "bnyjerry",
        "built_by": "pipeline/lora/build_jerry_v2_0822.py",
        "built_on": "2026-08-22",
        "authority": (
            "taste/refs/goblin-canon-founder-0821.png -- the founder's own "
            "picture, selected with 'dude, this is how the goblin should "
            "look'. pipeline/canon.yaml route_closure_2026_08_22."),
        "supersedes": (
            "pipeline/lora/manifest-jerry-0821.yaml -- 15 frames curated for "
            "the ADULT read the founder superseded on 2026-08-21, never "
            "trained, left on disk as evidence."),
        "route": (
            "Every frame is the canon image itself, cut to a framing and "
            "re-lit by img2img at strength <= 0.40. "
            "pipeline/goblin-i2i-route-0822.md section 3."),
        "count": N,
        "repeat": repeat,
        "image_passes": passes,
        "optimizer_steps_at_batch_2": steps,
        "framings": {k: len(v) for k, v in sorted(by_framing.items())},
        "grounds": sorted({f["ground"] for f in frames}),
        "lights": sorted({f["light"] for f in frames}),
        "caption_scheme": (
            "Ten clauses, three variable, identical length on every frame. "
            "`standing`, `looking at viewer` and the framing word are named on "
            "EVERY frame although they never vary, because a named attribute "
            "is one the trigger is excused from carrying -- and the one thing "
            "this LoRA must not learn is a pose, since a pose net moving him "
            "is the entire reason it is being trained. Length is uniform per "
            "the v2b dilution finding in registry.yaml."),
        "dropped": {c: rows[c].get("why", "") for c in dropped},
        "frames": frames,
    }
    with open(os.path.join(REPO, MANIFEST), "w", encoding="utf-8") as fh:
        fh.write("# THE JERRY v2 DATASET -- GENERATED. Edit "
                 "pipeline/lora/build_jerry_v2_0822.py, not this file.\n"
                 "#\n# Every frame is the founder's own drawing, re-lit. See "
                 "the `route` key.\n")
        yaml.safe_dump(doc, fh, sort_keys=False, width=88, allow_unicode=True)
    print("\nwrote %s and %d caption(s)" % (MANIFEST, N))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
