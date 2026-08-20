#!/usr/bin/env python3
r"""Score ep2-b09-cropmotion-0820 against the four bars its own spec pre-registered.

    python3 pipeline/judge_b09_cropmotion_0820.py [--frames-out DIR]

WHY A FILE AND NOT A SNIPPET. The parent (`ep2-b09-faceturn-crf10-0819`) was
measured by hand and its verdict quotes numbers -- 0.66, 2.155, 74.23 -- that
nothing in the tree can recompute. This clip's whole value is a COMPARISON to
that parent, so the arithmetic has to be readable by the next lane or the
comparison is a claim rather than a measurement.

THE PROBES ARE PLACED BY GEOMETRY, NOT BY EYE, and that is deliberate. The init
is a known crop of a known plate, so both boxes can be *derived*:

    r1s3 source (832x1216)  --crop [223,9,609,572] + LANCZOS to 832x1216-->
    platecrop (832x1216)    --cover-crop to 704x1280 (scale 1.0526, left 86)-->
    the clip's frame 1

so the plate's own recorded face box travels through two affine steps and lands
where it lands. Nothing is eyeballed and nothing is nudged to make a number.

AND THE PROBES ARE PUBLISHED WITH THEIR DISPERSION, because this ladder has now
retracted three fixed-window instruments (work-ladder-0819.md, "THREE
INSTRUMENTS RETRACTED"). A fixed box measures the SUBJECT only while the subject
stays under it, and the tell is in `luma_std`, not in the mean:

    collapse  -- the box slid onto a flat field (sky, grass). Premise dead.
    explosion -- the box slid onto an EDGE (lit cheek / dark cloak). Premise
                 dead, and this is the dangerous shape: an inflated std reads
                 like a subject that changed.

Both are reported for f001 and f121 on both boxes. If either fires, the C2/C3/C4
numbers computed over that box are void and must be re-placed by eye, not
argued with.

FREEZE IS COUNTED TWO WAYS AND ONLY ONE OF THEM RANKS. judge_clip's terminal
exact-duplicate run is reported for continuity, but it ranks clips BACKWARDS
whenever the death point moves: a clip that dies at f035 and then jitters by one
grey level has no exact duplicates at all and scores better than one that dies
at f110 cleanly. LAST LIVE PAIR (the last consecutive pair whose mean |delta|
clears a floor) and the dead-pair count are what this file reads.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

REPO = Path(__file__).resolve().parent.parent
CLIP = REPO / "farm-out/ep2-b09-cropmotion-0820/09-the-pause-LTX-ep2-b09-cropmotion-0820.mp4"
PARENT = REPO / "farm-out/ep2-b09-faceturn-crf10-0819"

# ---------------------------------------------------------------- geometry ---
# Recorded in farm-out/ep2-b09-platecrop-0820/09-the-pause-platecrop-r1s3.yaml
SRC_FACE = (300, 170, 530, 330)          # face box in the r1s3 SOURCE, 832x1216
SRC_HEAD_TOP, SRC_HEAD_CHIN = 20, 330    # head extents in the same frame
CROP_BOX = (223, 9, 609, 572)            # plate_crop's box, then LANCZOS to 832x1216
PLATE_WH = (832, 1216)
CLIP_WH = (704, 1280)
DEAD_PAIR = 0.20                         # collect_farm's dead-pair floor


def plate_from_source(box):
    """Source pixels -> platecrop pixels (crop then resize back to 832x1216)."""
    x0, y0, x1, y1 = CROP_BOX
    sx = PLATE_WH[0] / float(x1 - x0)
    sy = PLATE_WH[1] / float(y1 - y0)
    return ((box[0] - x0) * sx, (box[1] - y0) * sy,
            (box[2] - x0) * sx, (box[3] - y0) * sy)


def clip_from_plate(box):
    """Platecrop pixels -> clip pixels (cover_crop.py, 832x1216 -> 704x1280)."""
    W, H = CLIP_WH
    sw, sh = PLATE_WH
    s = max(W / float(sw), H / float(sh))
    nw, nh = int(round(sw * s)), int(round(sh * s))
    left, top = (nw - W) // 2, (nh - H) // 2
    return (box[0] * s - left, box[1] * s - top,
            box[2] * s - left, box[3] * s - top)


def to_int_box(b):
    return tuple(int(round(v)) for v in b)


FACE = to_int_box(clip_from_plate(plate_from_source(SRC_FACE)))
# The head box: full head height at the composition plate_crop wrote
# (head top at 0.02 of frame, chin at 0.57), width taken as the face box's.
_hp = clip_from_plate((0, 0.02 * PLATE_WH[1], 0, 0.57 * PLATE_WH[1]))
HEAD = (FACE[0], int(round(_hp[1])), FACE[2], int(round(_hp[3])))
GRASS = (0, 1000, 704, 1280)             # control strip, no subject expected


# ------------------------------------------------------------ measurement ---
def decode(path, outdir):
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(path),
                    "-vsync", "0", f"{outdir}/f%03d.png"], check=True)
    return sorted(Path(outdir).glob("f*.png"))


def grey(p):
    return np.asarray(Image.open(p).convert("L"), dtype=np.float64)


def box_stats(p, box):
    im = Image.open(p).convert("RGB").crop(box)
    a = np.asarray(im, dtype=np.float64)
    lum = a @ np.array([0.299, 0.587, 0.114])
    g = im.convert("L")
    hp = (np.asarray(g, dtype=np.float64)
          - np.asarray(g.filter(ImageFilter.GaussianBlur(1.0)), dtype=np.float64))
    return {"luma": round(float(lum.mean()), 2),
            "luma_std": round(float(lum.std()), 2),
            "r_minus_b": round(float((a[..., 0] - a[..., 2]).mean()), 2),
            "highpass_sigma1_std": round(float(hp.std()), 3)}


def head_extent_measured(p, box, thresh=0.35):
    """Head top/chin read off the frame, not asserted.

    The head sits against sky and grass; a column-band gradient magnitude finds
    the rows where drawn structure exists. Reported BESIDE the arithmetic
    prediction so a disagreement is visible rather than averaged away.
    """
    a = grey(p)
    band = a[:, box[0]:box[2]]
    gy = np.abs(np.diff(band, axis=0)).mean(axis=1)
    gx = np.abs(np.diff(band, axis=1)).mean(axis=1)[:len(gy)]
    energy = gy + gx
    lo = energy.max() * thresh
    rows = np.flatnonzero(energy > lo)
    if rows.size == 0:
        return None
    return int(rows[0]), int(rows[-1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames-out", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    with tempfile.TemporaryDirectory() as td:
        fs = decode(CLIP, td)
        n = len(fs)
        print(f"clip {CLIP.name}  {n} frames  face box {FACE}  head box {HEAD}")

        # per-frame greys over the two boxes, float64, whole-frame for controls
        face = np.stack([grey(p)[FACE[1]:FACE[3], FACE[0]:FACE[2]] for p in fs])
        grass = np.stack([grey(p)[GRASS[1]:GRASS[3], GRASS[0]:GRASS[2]] for p in fs])
        whole = np.stack([grey(p) for p in fs])

        face_step = np.abs(np.diff(face, axis=0)).mean(axis=(1, 2))
        grass_step = np.abs(np.diff(grass, axis=0)).mean(axis=(1, 2))
        whole_step = np.abs(np.diff(whole, axis=0)).mean(axis=(1, 2))
        face_drift = np.abs(face - face[0]).mean(axis=(1, 2))
        grass_drift = np.abs(grass - grass[0]).mean(axis=(1, 2))

        # ---- probe integrity, BEFORE any bar is read off these boxes
        probes = {"f001": {}, "f%03d" % n: {}}
        for label, p in (("f001", fs[0]), ("f%03d" % n, fs[-1])):
            for name, box in (("face", FACE), ("head", HEAD), ("grass", GRASS)):
                probes[label][name] = box_stats(p, box)

        # ---- C1 framing
        ext = head_extent_measured(fs[0], HEAD)
        pred = (HEAD[3] - HEAD[1]) / float(CLIP_WH[1])
        meas = None if ext is None else (ext[1] - ext[0]) / float(CLIP_WH[1])

        # ---- freeze, two ways
        exact = 0
        for s in whole_step[::-1]:
            if s == 0.0:
                exact += 1
            else:
                break
        live = np.flatnonzero(whole_step > DEAD_PAIR)
        last_live = int(live[-1]) + 1 if live.size else None
        dead_pairs = int((whole_step <= DEAD_PAIR).sum())

        third = (n - 1) // 3
        by_third = [round(float(face_step[:third].mean()), 3),
                    round(float(face_step[third:2 * third].mean()), 3),
                    round(float(face_step[2 * third:].mean()), 3)]
        top10 = (np.argsort(face_step)[::-1][:10] + 1).tolist()

        out = {
            "clip": str(CLIP.relative_to(REPO)),
            "frames": n,
            "boxes": {"face": list(FACE), "head": list(HEAD), "grass": list(GRASS)},
            "probes": probes,
            "C1_head_frac_predicted": round(pred, 4),
            "C1_head_frac_measured": None if meas is None else round(meas, 4),
            "C1_head_rows_measured": ext,
            "C2_f001_to_f002_face_step": round(float(face_step[0]), 3),
            "C3_face_highpass_f001": probes["f001"]["face"]["highpass_sigma1_std"],
            "C3_face_highpass_last": probes["f%03d" % n]["face"]["highpass_sigma1_std"],
            "C3_retained_pct": round(
                probes["f%03d" % n]["face"]["highpass_sigma1_std"]
                / probes["f001"]["face"]["highpass_sigma1_std"] * 100, 1),
            "C4_face_step_mean": round(float(face_step.mean()), 3),
            "C4_motion_by_third": by_third,
            "ten_largest_face_steps": top10,
            "face_drift_from_f0_last": round(float(face_drift[-1]), 2),
            "grass_drift_from_f0_last": round(float(grass_drift[-1]), 2),
            "grass_step_mean": round(float(grass_step.mean()), 3),
            "whole_luma_min_max": [round(float(whole.mean(axis=(1, 2)).min()), 2),
                                   round(float(whole.mean(axis=(1, 2)).max()), 2)],
            "whole_largest_luma_step": round(
                float(np.abs(np.diff(whole.mean(axis=(1, 2)))).max()), 3),
            "freeze_terminal_exact_run": exact,
            "last_live_pair": last_live,
            "dead_pairs_of": [dead_pairs, n - 1],
        }

        if a.frames_out:
            d = Path(a.frames_out)
            d.mkdir(parents=True, exist_ok=True)
            for i in (1, 21, 40, 60, 80, 100, n):
                Image.open(fs[i - 1]).save(d / f"b09cm-f{i:03d}.png")

        if a.json:
            print(json.dumps(out, indent=2))
        else:
            for k, v in out.items():
                if k == "probes":
                    for lab, boxes in v.items():
                        for name, st in boxes.items():
                            print(f"  probe {lab:5s} {name:5s} {st}")
                else:
                    print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
