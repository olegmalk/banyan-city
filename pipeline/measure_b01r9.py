#!/usr/bin/env python3
"""B01-R9-PLAN.md §8 axis B, computed the way the plan pre-registered it.

Numpy and PIL only -- no model, no GPU, no download. Axis A (geometry) is
DELIBERATELY NOT HERE: stem height, grounded-whole-plant, person and pale-slab
counts are content questions, and this repo has already recorded what happens
when a number is allowed to answer one (`ep1-v34-motion-metric-disqualified` --
the arm that scored best was the arm that invented a phone). Those are answered
by opening the frames.

What this file computes, per the plan:

  sky colour  mean RGB of the top 25% of frame, plus HSV saturation, plus the
              L2 distance from that mean to each of three references. r9 passes
              if its sky sits with `r8-t2i-s0` (the correct sunrise) and not
              with the b15 plate (the amber dusk that leaked through every
              img2img arm).

  the shaft   column-luminance profile across the top 25%: the mean luminance
              of each image column, then the peak, where it sits, and how far
              above the profile mean it stands. The plate's peak is at x=333 of
              832 and stands +42 above its own mean; a shaft-free frame has no
              such central spike.

TWO SHAFT READINGS, BECAUSE THEY ANSWER DIFFERENT QUESTIONS AND STAGE 1 ONLY
REPORTED ONE. `at_plate_x` is the column at x=333 -- did the PLATE's shaft ride
through the depth map? -- and it is the number the Stage 1 record quotes
(`+1.60 above mean where the plate sits +42.21`; both reproduce here to 0.01).
`peak_over_mean` is the frame's OWN highest column wherever it falls, which is
the number that catches a shaft the model re-invented somewhere else. Stage 1
flagged exactly that by eye and had no number for it. A frame can pass the first
and fail the second, and several do.

Both are stated as an ABSOLUTE difference in 0-255 luminance, not a ratio,
because the plan quotes them that way and a ratio moves with sky brightness.

    python3 pipeline/measure_b01r9.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
STILLS = ROOT / "genomes/sapling/nodes/002b-first-citizen/takes/stills"
PLATE = (ROOT / "genomes/sapling/nodes/001-capability-inventory/stills"
         / "15-something-s-coming.png")

REFERENCES = {
    "PLATE-b15": PLATE,                              # the amber dusk that leaked
    "r8-i35-s0": STILLS / "01-cold-open-r8-i35-s0.png",   # the leak, measured
    "r8-t2i-s0": STILLS / "01-cold-open-r8-t2i-s0.png",   # the correct sunrise
}

TOP_FRACTION = 0.25
# Where the b15 plate's own shaft sits, measured in §8 of the plan. Sampling the
# r9 frames at this exact column is what answers "did the plate's shaft come
# through the depth map", as distinct from "does this frame have a shaft".
PLATE_PEAK_X = 333
# Rec. 601 luma. Named rather than left as magic numbers because the plate's
# published profile (56.3 to 119.9, peak at x=333) was computed with it, and a
# different weighting would silently make these numbers incomparable to it.
LUMA = np.array([0.299, 0.587, 0.114])


def saturation(mean_rgb: np.ndarray) -> float:
    """HSV S of a single RGB triple in 0-1. (max-min)/max, 0 when black."""
    hi, lo = float(mean_rgb.max()), float(mean_rgb.min())
    return 0.0 if hi <= 0 else (hi - lo) / hi


def measure(path: Path) -> dict:
    img = Image.open(path).convert("RGB")
    a = np.asarray(img, dtype=np.float64)
    h, w, _ = a.shape
    band = a[: int(round(h * TOP_FRACTION)), :, :]

    mean_rgb = band.reshape(-1, 3).mean(axis=0)
    cols = (band @ LUMA).mean(axis=0)          # one luminance per image column
    peak = int(np.argmax(cols))

    return {
        "file": path.name,
        "size": f"{w}x{h}",
        "mean_rgb": [round(float(v), 2) for v in mean_rgb],
        "saturation": round(saturation(mean_rgb / 255.0), 3),
        "col_lum_min": round(float(cols.min()), 2),
        "col_lum_max": round(float(cols.max()), 2),
        "col_lum_mean": round(float(cols.mean()), 2),
        "peak_x": peak,
        "peak_x_frac": round(peak / w, 3),
        "peak_over_mean": round(float(cols.max() - cols.mean()), 2),
        "at_plate_x": round(float(cols[PLATE_PEAK_X] - cols.mean()), 2),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", default=None, help="also write the rows here")
    ap.add_argument("--dirs", nargs="*", default=["review/b01-r9",
                                                  "review/b01-r9-stage2"],
                    help="repo-relative dirs of r9 frames to measure")
    a = ap.parse_args()

    rows, refs = [], {}
    for name, path in REFERENCES.items():
        if not path.exists():
            print(f"!! missing reference {name}: {path}", file=sys.stderr)
            return 2
        r = measure(path)
        r["id"] = name
        refs[name] = np.array(r["mean_rgb"])
        rows.append(r)

    for d in a.dirs:
        for png in sorted((ROOT / d).glob("*.png")):
            r = measure(png)
            r["id"] = f"{d.split('/')[-1]}/{png.stem}"
            rows.append(r)

    for r in rows:
        m = np.array(r["mean_rgb"])
        for name, ref in refs.items():
            r[f"L2_to_{name}"] = round(float(np.linalg.norm(m - ref)), 2)
        # The plan's actual question, reduced to one word per frame.
        r["clusters_with"] = ("t2i" if r["L2_to_r8-t2i-s0"] < r["L2_to_PLATE-b15"]
                              else "PLATE")

    hdr = (f"{'frame':22} {'meanRGB':24} {'sat':>6} {'L2t2i':>7} {'L2plate':>8} "
           f"{'with':>6} | {'atX333':>7} {'peakX':>6} {'peak+':>7}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        rgb = "(" + ", ".join(f"{v:6.2f}" for v in r["mean_rgb"]) + ")"
        short = r["id"].replace("b01-r9-stage2/01-cold-open-r9-", "").replace(
            "b01-r9/01-cold-open-r9-", "S1:")
        print(f"{short:22} {rgb:24} {r['saturation']:6.3f} "
              f"{r['L2_to_r8-t2i-s0']:7.2f} {r['L2_to_PLATE-b15']:8.2f} "
              f"{r['clusters_with']:>6} | {r['at_plate_x']:7.2f} "
              f"{r['peak_x']:6d} {r['peak_over_mean']:7.2f}")

    if a.json:
        Path(a.json).write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
