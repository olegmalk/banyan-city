#!/usr/bin/env python3
r"""Draw the sapling LoRA's pre-registered bar grid — 15 cells plus one probe.

    <render-venv>/python.exe pipeline/lora/run_grid.py \
        --lora out/bnysapling-sdxl-v1.safetensors --lora-weight 0.8 \
        --sampler pipeline/lora/sample_lora.py --out-dir grid

WHY A SEPARATE FILE AND NOT SIXTEEN STEPS IN THE JOB SPEC. Sixteen `sample_lora`
steps would re-import torch and re-load a 6.9 GB SDXL checkpoint sixteen times —
roughly nine minutes of pure model loading against ninety seconds of drawing.
More importantly it would put the PROMPTS in sixteen places, and the whole point
of pre-registering them is that they exist once, verbatim, and cannot be
re-picked cell by cell after a bad frame.

WHY IT SHELLS OUT TO sample_lora.py INSTEAD OF IMPORTING THE PIPELINE. Every
frame must carry the same §7.2 sidecar the ONE SAMPLE carried — same model line,
same lora_sha256, same `approved: false` / `provisional: true`. Re-implementing
that here would be a second writer of the same record, and the two would drift.
The model-load cost that buys is real and accepted: correctness of the record
beats nine minutes of card time, and the card is idle.

THE PROMPTS BELOW ARE FROZEN. They are copied verbatim from the `## BARS` block
of `pipeline/lora/train-sapling-0822.yaml`, committed at 9a4042299 before any
pixel of this LoRA existed. Editing one after seeing a frame is re-picking a bar
after the fact, which is how 8/12 "passes" became 0/12 usable on this project.
If a prompt is badly worded, that goes in the verdict; the bar stays as scored.

$0. No network beyond the checkpoint already cached on the box, no provider.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TAIL = ("anime style, cel shading, detailed background, "
        "masterpiece, best quality, very aesthetic")

# The house negative for this grid. It carries NO leaf-count and NO leaf-shape
# word, deliberately: bar B5 asks whether the LoRA itself draws two ordinary
# blades, and the dataset's own negative ("three leaves, four leaves, many
# leaves, extra stalk, branching stem, pointed lance leaves, lobed leaves...")
# would answer that on the LoRA's behalf. See train-sapling-0822.yaml step 3.
NEG = ("1boy, 1girl, people, goblin, text, watermark, signature, "
       "photorealism, 3d render, low quality, worst quality, blurry")

# P4's whole question is a figure in frame, so `1boy` and `goblin` come OUT of
# its negative and only its negative. Declared here rather than discovered in a
# log later.
NEG_P4 = ("1girl, text, watermark, signature, "
          "photorealism, 3d render, low quality, worst quality, blurry")

SEEDS = (20260822, 20260823, 20260824)

PROMPTS = {
    # id: (positive, negative)
    "P1": ("bnysapling, a young sapling, two leaves, 25 cm tall, medium shot, "
           "bare tilled earth field, a low stone wall behind, overcast, " + TAIL, NEG),
    "P2": ("bnysapling, a young sapling, two leaves, 15 cm tall, close-up, "
           "in a clay pot on a windowsill, warm lamplight, indoor, " + TAIL, NEG),
    "P3": ("bnysapling, a young sapling, two leaves, 90 cm tall, wide shot, "
           "open green meadow, distant hills, clear sky, flat daylight, " + TAIL, NEG),
    "P4": ("bnysapling, a young sapling, two leaves, 40 cm tall, medium shot, "
           "a goblin crouching beside it, open green meadow, flat daylight, " + TAIL, NEG_P4),
    "P5": ("bnysapling, a young sapling, two leaves, 25 cm tall, medium shot, "
           "dry autumn grassland, brown grass, low sun, " + TAIL, NEG),
}

# RECORDED, NOT GRADED. One seed. The manifest's leaf_count_values is 1 — every
# training frame is two-leaf — so this measures where v1 stands on leaf-count
# promptability and carries no pass or fail attached to it.
PROBE = ("bnysapling, a young sapling, four leaves, 40 cm tall, medium shot, "
         "open green meadow, flat daylight, " + TAIL, NEG)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lora", required=True)
    ap.add_argument("--lora-weight", default="0.8")
    ap.add_argument("--sampler", required=True,
                    help="path to sample_lora.py — the one writer of the sidecar")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--dry-run", action="store_true",
                    help="print the 16 cells and draw nothing")
    # WHY THIS FLAG EXISTS AND IS NOT DECORATION. box_enqueue.py's
    # output_path_problems refuses any spec whose `artifacts:` names a file no
    # step's argv mentions -- because the runner's missing-artifact check is
    # worthless if the list was carried over from another job. The cell names
    # here are DERIVED (prompt id x seed), so nothing in the spec's argv would
    # name them and the job could not be filed at all. Naming the sentinel cells
    # on the command line satisfies that guard AND makes this script assert what
    # it produced, which is strictly better than the spec asserting it alone.
    ap.add_argument("--require", nargs="*", default=[],
                    help="basenames that MUST exist when the grid finishes")
    a = ap.parse_args()

    out = Path(a.out_dir)
    cells = [(f"{pid}-s{seed}", pos, neg, seed)
             for pid, (pos, neg) in PROMPTS.items()
             for seed in SEEDS]
    cells.append(("PROBE-fourleaf-s%d" % SEEDS[0], PROBE[0], PROBE[1], SEEDS[0]))

    if a.dry_run:
        for name, pos, _neg, seed in cells:
            print(f"{name}  seed={seed}  {pos[:72]}...")
        print(f"{len(cells)} cells")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    failed = []
    for i, (name, pos, neg, seed) in enumerate(cells, 1):
        dest = out / f"{name}.png"
        argv = [sys.executable, a.sampler,
                "--lora", a.lora, "--lora-weight", str(a.lora_weight),
                "--prompt", pos, "--negative", neg,
                "--width", "832", "--height", "1216",
                "--steps", "40", "--guidance", "7.5",
                "--seed", str(seed), "--out", str(dest)]
        print(f"[{i}/{len(cells)}] {name}", flush=True)
        rc = subprocess.call(argv)
        # A single bad cell must not throw away the fifteen that worked; the
        # denominator is what the bars are scored on, so a missing cell is
        # reported rather than silently reducing N.
        if rc != 0 or not dest.exists():
            failed.append(name)
            print(f"   !! {name} did not render (rc={rc})", flush=True)

    print(f"\n{len(cells) - len(failed)} of {len(cells)} cells drawn -> {out}")
    if failed:
        print("MISSING: " + ", ".join(failed))

    absent = [r for r in a.require if not (out / r).exists()]
    if absent:
        print("REQUIRED CELL ABSENT: " + ", ".join(absent))

    # Nonzero if the grid is too thin to score the bars at their stated
    # denominators (15 graded cells + 1 probe), or if a sentinel is missing.
    return 0 if not failed and not absent else 1


if __name__ == "__main__":
    sys.exit(main())
