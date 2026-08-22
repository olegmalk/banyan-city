#!/usr/bin/env python3
r"""The LoRA-WEIGHT ladder: find the scale where the subject still draws and the
no-regression contamination stops.

    <render-venv>/python.exe pipeline/lora/run_ladder.py \
        --lora out/bnysapling-sdxl-v1.safetensors \
        --sampler pipeline/lora/sample_lora.py --out-dir ladder

WHY THIS EXISTS, AND IT IS A FINDING AND NOT A GUESS. The 2026-08-22 one sample
answered the expensive question — `bnysapling` DRAWS the canon two-leaf sapling,
which five closed wording ladders never could. The no-regression pair drawn in
the same session answered a cheaper one badly. At the shipping weight 0.8, the
identical prompt and seed ("a stone bridge over a river, forest, afternoon
light") came back:

  * WITHOUT the small figure that stands on the bridge in the no-LoRA frame --
    an OBJECT DELETED, not a tone shift, and the sharpest single piece of
    evidence here. Every one of the 44 training frames is figure-free.
  * darker and flatter, deeper blues, less sky light
  * recomposed lower and tighter

No sapling appeared, which is the failure this bar was most afraid of and it did
not happen. But `train-sapling-0822.yaml` bar B3 fails on "a visible shift in
palette, line weight or shading style", and this is visible without effort.

A FAIL AT ONE WEIGHT IS NOT A FAIL AT EVERY WEIGHT, and 0.8 was picked before any
pixel existed by copying the Jerry spec. Research section 6 already records 0.65
as the community working point when LoRAs are stacked. So the question this
answers is a two-sided one that a single number cannot: as the scale comes down,
contamination should fade AND the sapling should get worse. Where those two
curves cross is the shipping weight, and it is a measurement, not a taste call.

WHAT IT DELIBERATELY DOES NOT DO: change any pre-registered bar. B3 was scored at
0.8 and stays scored at 0.8. This ladder is a SEPARATE, later measurement whose
result is a recommended weight for the NEXT run, not a re-grade of this one.
Bars tighten forward only.

$0, no provider. Both halves of every rung share one seed with the 0.8 pair
already on disk, so the whole ladder is comparable frame to frame.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TAIL = ("anime style, cel shading, detailed background, "
        "masterpiece, best quality, very aesthetic")

# THE SUBJECT SIDE. P1 verbatim from train-sapling-0822.yaml BARS -- the same
# prompt the one sample used, so its 0.8 frame is already the top rung of this
# ladder and does not need redrawing.
SUBJECT = ("bnysapling, a young sapling, two leaves, 25 cm tall, medium shot, "
           "bare tilled earth field, a low stone wall behind, overcast, " + TAIL)
SUBJECT_NEG = ("1boy, 1girl, people, goblin, text, watermark, signature, "
               "photorealism, 3d render, low quality, worst quality, blurry")

# THE CONTAMINATION SIDE. Verbatim from the no-regression pair, so the 0.8 frame
# and the no-LoRA frame already on disk are this ladder's two endpoints.
CLEAN = ("a stone bridge over a river, forest, afternoon light, " + TAIL)
CLEAN_NEG = ("text, watermark, signature, photorealism, 3d render, "
             "low quality, worst quality, blurry")

SEED = 20260822

# 0.8 is omitted on purpose: both its frames exist already and redrawing them
# would spend card time to reproduce bytes we can read. 0.0 is the no-LoRA frame,
# which also exists already.
WEIGHTS = (0.65, 0.5, 0.35, 0.2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lora", required=True)
    ap.add_argument("--sampler", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--dry-run", action="store_true")
    # Same reason as run_grid.py: box_enqueue refuses a spec whose artifacts are
    # named by no step's argv, and these filenames are derived from the weight.
    ap.add_argument("--require", nargs="*", default=[])
    a = ap.parse_args()

    cells = []
    for w in WEIGHTS:
        tag = ("%0.2f" % w).replace(".", "")
        cells.append((f"SUBJECT-w{tag}", SUBJECT, SUBJECT_NEG, w))
        cells.append((f"CLEAN-w{tag}", CLEAN, CLEAN_NEG, w))

    if a.dry_run:
        for name, pos, _n, w in cells:
            print(f"{name}  weight={w}  {pos[:64]}...")
        print(f"{len(cells)} cells")
        return 0

    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    failed = []
    for i, (name, pos, neg, w) in enumerate(cells, 1):
        dest = out / f"{name}.png"
        print(f"[{i}/{len(cells)}] {name}", flush=True)
        rc = subprocess.call([sys.executable, a.sampler,
                              "--lora", a.lora, "--lora-weight", str(w),
                              "--prompt", pos, "--negative", neg,
                              "--width", "832", "--height", "1216",
                              "--steps", "40", "--guidance", "7.5",
                              "--seed", str(SEED), "--out", str(dest)])
        if rc != 0 or not dest.exists():
            failed.append(name)
            print(f"   !! {name} did not render (rc={rc})", flush=True)

    print(f"\n{len(cells) - len(failed)} of {len(cells)} cells drawn -> {out}")
    absent = [r for r in a.require if not (out / r).exists()]
    if failed:
        print("MISSING: " + ", ".join(failed))
    if absent:
        print("REQUIRED CELL ABSENT: " + ", ".join(absent))
    return 0 if not failed and not absent else 1


if __name__ == "__main__":
    sys.exit(main())
