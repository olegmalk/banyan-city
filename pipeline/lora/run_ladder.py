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


# --------------------------------------------------------------------------
# --weights IS ADDITIVE AND THE DEFAULT IS THE FROZEN LADDER. Added 2026-08-22
# when the spec was re-pointed at v2c: the standing rule is one sample before a
# SET, and this file could only ever draw all four rungs, so the gate in front
# of an eight-cell sweep had no way to spend two cells. `--weights 0.65` draws
# exactly one rung, and the sweep that follows it is the same script with the
# flag left off.
#
# WITHOUT THE FLAG NOTHING MOVES. The default is the WEIGHTS tuple above, by
# identity and not by re-parsing a string, so the argv this builds for an
# un-flagged run is byte-for-byte the argv it built before the flag existed --
# `--selftest` asserts that against a frozen copy of the eight-cell list. The
# ladder's comparability rests on the rungs, prompts and seeds not being
# re-picked; this flag lets a rung be DEFERRED, never redefined.

def parse_weights(values) -> tuple:
    """None -> the frozen ladder. A list -> a validated subset/superset of it."""
    if values is None:
        return WEIGHTS
    if not values:
        raise ValueError("--weights given with no value")
    out = []
    for v in values:
        w = float(v)
        if not 0.0 < w <= 1.0:
            raise ValueError("weight %r out of range (0, 1]" % (v,))
        if w in out:
            raise ValueError("weight %r given twice" % (v,))
        out.append(w)
    return tuple(out)


def build_cells(weights) -> list:
    cells = []
    for w in weights:
        tag = ("%0.2f" % w).replace(".", "")
        cells.append((f"SUBJECT-w{tag}", SUBJECT, SUBJECT_NEG, w))
        cells.append((f"CLEAN-w{tag}", CLEAN, CLEAN_NEG, w))
    return cells


def selftest() -> int:
    # 1. The un-flagged run is the old run. Frozen by hand from the pre-flag
    #    file: four rungs, two sides each, in this order, with these tags.
    frozen = [
        ("SUBJECT-w065", 0.65), ("CLEAN-w065", 0.65),
        ("SUBJECT-w050", 0.5), ("CLEAN-w050", 0.5),
        ("SUBJECT-w035", 0.35), ("CLEAN-w035", 0.35),
        ("SUBJECT-w020", 0.2), ("CLEAN-w020", 0.2),
    ]
    default = build_cells(parse_weights(None))
    assert [(c[0], c[3]) for c in default] == frozen, default
    # and the weight strings that reach the sampler are unchanged too
    assert [str(c[3]) for c in default] == ["0.65", "0.65", "0.5", "0.5",
                                            "0.35", "0.35", "0.2", "0.2"]
    # 2. Prompts are per-side constants, not per-rung -- a subset run must draw
    #    the SAME two prompts the full sweep would draw at that rung.
    one = build_cells(parse_weights(["0.65"]))
    assert len(one) == 2, one
    assert one == default[:2], one
    # 3. Order is the caller's order, and a rung off the frozen ladder is legal
    #    (the flag defers rungs; it does not police them).
    assert [c[0] for c in build_cells(parse_weights(["0.9", "0.45"]))] == [
        "SUBJECT-w090", "CLEAN-w090", "SUBJECT-w045", "CLEAN-w045"]
    # 4. Refusals.
    for bad in ([], ["0"], ["1.4"], ["-0.5"], ["0.65", "0.65"]):
        try:
            parse_weights(bad)
        except ValueError:
            continue
        raise AssertionError("parse_weights(%r) should have refused" % (bad,))
    print("run_ladder selftest OK: default ladder unchanged (%d cells), "
          "--weights subsets and refusals behave" % len(default))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lora")
    ap.add_argument("--sampler")
    ap.add_argument("--out-dir")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    # ADDITIVE. Omit it and the ladder is the frozen four rungs, unchanged.
    ap.add_argument("--weights", nargs="+", default=None,
                    help="rungs to draw (default: %s)" % (WEIGHTS,))
    # Same reason as run_grid.py: box_enqueue refuses a spec whose artifacts are
    # named by no step's argv, and these filenames are derived from the weight.
    ap.add_argument("--require", nargs="*", default=[])
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    for req in ("lora", "sampler", "out_dir"):
        if not getattr(a, req):
            ap.error("--%s is required" % req.replace("_", "-"))

    try:
        weights = parse_weights(a.weights)
    except ValueError as exc:
        ap.error(str(exc))
    cells = build_cells(weights)

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
