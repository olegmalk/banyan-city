#!/usr/bin/env python3
r"""Beat 09: score an r2s2-crop motion clip against the INCUMBENT with one ruler.

    python3 pipeline/judge_b09_crop_0821.py --incumbent
    python3 pipeline/judge_b09_crop_0821.py --clip farm-out/<dir>/<x>.mp4 --geom r2s2
    python3 pipeline/judge_b09_crop_0821.py --all-r2s2      # every c*/m* that landed

WHY THIS FILE EXISTS AND `judge_b09_cropmotion_0820.py` DOES NOT DO THE JOB.
That file hardcodes ONE clip and ONE crop's geometry (r1s3: CROP_BOX
[223,9,609,572], hand box (430,430,660,700)). This batch renders a DIFFERENT
crop of a DIFFERENT plate -- r2s2, crop box [44,13,616,850] -- so every probe
box moves, and the whole point of the batch is a COMPARISON to the incumbent.
Two clips measured by two scripts is a claim; two clips measured by one script
in each one's own declared geometry is a measurement.

THE SLOT IS f001-f093 AND THAT IS THE NUMBER THAT MATTERS. Beat 09's slot in
`review/ep2-ship-0821` is 3.92 s at 24 fps; the clips are 121 frames / 5.04 s.
Frames f094-f121 are rendered and NOT SHIPPED. So every ranking figure here is
computed over the SLOT, with the full-clip figure printed beside it for the
ladder. The h-batch's headline cost -- "all three end with his eyes shut" --
lands at f100+, which is off the end of the slot; that is a fact about the cut
and it is the reason this rung was re-priced.

THE PAN RULER, AND THE ONE PATCH IT MUST NOT USE ON THIS PLATE. The ladder kept
a three-line camera ruler off the b04 s5 pan: mean abs luma of the TWO TOP
CORNER patches against f001, under ~3 = locked. ON THE r2s2 CROP THE TOP-RIGHT
CORNER IS HIS HAIR -- the head fills the upper right of the frame -- so that
patch measures the subject, not the world, and an inflated number there would
read as a pan that is not happening. It is excluded BY NAME and a left-edge
grass strip is used as the second background probe instead. The r1s3 incumbent
has the same problem in the same corner (blond hair highlight), so both
geometries use the same two patches and the comparison stays like-for-like.

WHAT RANKS. `last_live_pair` (the last consecutive pair whose whole-frame mean
|delta| clears 0.20) and the dead-pair count -- NOT judge_clip's terminal
exact-duplicate run, which ranks clips backwards whenever the death point moves.
A clip that dies at f035 and jitters by one grey level has no exact duplicates
at all and would score better than one that dies cleanly at f110.

WHAT DOES NOT RANK AND IS PRINTED ANYWAY: hand-box drift and interframe. They
say WHERE to look; whether the thing in the box is still a hand is an eye
question at 1:1 and this file refuses to answer it. `--frames-out` writes the
frames to look at.
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
SLOT_LAST = 93                 # beat 09's slot is f001-f093; f094-f121 do not ship
DEAD_PAIR = 0.20               # collect_farm's dead-pair floor
PAN_BAR = 3.0                  # ladder's camera-lock bar on a background patch

INCUMBENT = "farm-out/ep2-b09-cropmotion-0820/09-the-pause-LTX-ep2-b09-cropmotion-0820.mp4"

# Probe boxes in CLIP pixels (704x1280), placed on each crop's own init and
# recorded here rather than re-derived at judging time, so they are the same
# boxes every run and nobody can nudge one to make a number.
#
#   plate(832x1216) -> clip(704x1280): scale 1.052632, left 86, top 0
#
GEOM = {
    # r1s3: hand box is judge_b09_cropmotion_0820.py's, unchanged, so the
    # incumbent's numbers here are comparable to the ones already published.
    "r1s3": {
        "hand": (430, 430, 660, 700),
        "face": (89, 366, 610, 730),
        "bg_corner": (0, 0, 96, 96),          # sky
        "bg_low": (0, 1150, 120, 1280),       # grass, bottom-left
        "note": "top-right corner is his hair highlight -- excluded by name; the "
                "left-edge strip (0,300,80,800) is excluded too, it clips a hair wisp",
    },
    # r2s2: read off the cover-cropped init at 1:1 (scratchpad box render,
    # 2026-08-21). The hand sits at the MOUTH and CHIN on this plate, not flat
    # on the cheek as it does on r1s3 -- see the batch spec's H-POSE clause.
    "r2s2": {
        "hand": (145, 555, 430, 940),
        "face": (156, 415, 514, 768),
        "bg_corner": (0, 0, 96, 96),          # grass, dark
        "bg_low": (0, 1150, 120, 1280),       # grass, bottom-left
        "note": "top-right corner is his HAIR -- excluded by name, see docstring",
    },
}


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
            "highpass_sigma1_std": round(float(hp.std()), 3)}


def score(clip: Path, geom_name: str, frames_out=None) -> dict:
    g = GEOM[geom_name]
    with tempfile.TemporaryDirectory() as td:
        fs = decode(clip, td)
        n = len(fs)
        sl = min(SLOT_LAST, n)

        whole = np.stack([grey(p) for p in fs])
        def band(box):
            return np.stack([grey(p)[box[1]:box[3], box[0]:box[2]] for p in fs])
        hand, face = band(g["hand"]), band(g["face"])
        corner, low = band(g["bg_corner"]), band(g["bg_low"])

        whole_step = np.abs(np.diff(whole, axis=0)).mean(axis=(1, 2))
        face_step = np.abs(np.diff(face, axis=0)).mean(axis=(1, 2))
        hand_step = np.abs(np.diff(hand, axis=0)).mean(axis=(1, 2))
        hand_drift = np.abs(hand - hand[0]).mean(axis=(1, 2))

        live = np.flatnonzero(whole_step > DEAD_PAIR)
        last_live = int(live[-1]) + 1 if live.size else None
        live_slot = np.flatnonzero(whole_step[:sl - 1] > DEAD_PAIR)
        last_live_slot = int(live_slot[-1]) + 1 if live_slot.size else None

        # PAN RULER, TWO WAYS, because on THIS beat the raw form lies.
        # The b04 ruler is `mean abs luma of a background patch against f001,
        # under ~3 = locked`. Run raw on beat 09 it reports 8.1 on the sky
        # corner of the SHIPPING clip -- and the cause is not a camera, it is
        # exposure: whole-frame luma falls 95.96 -> 88.98 over the first thirty
        # frames (the crf-10 darkening this tree already has a diagnostic for,
        # pipeline/loop/darkening-crf-diagnostic-0819.md). So the patch is also
        # measured with its own mean removed, which is zero for a pure exposure
        # shift and large for a translation. THE RESIDUAL IS THE ONE THAT
        # RANKS; the raw number is printed so the b04 figures stay comparable.
        pan = {}
        for name, arr in (("bg_corner", corner), ("bg_low", low)):
            raw = np.abs(arr - arr[0]).mean(axis=(1, 2))
            c = arr - arr.mean(axis=(1, 2), keepdims=True)
            res = np.abs(c - c[0]).mean(axis=(1, 2))
            pan[name] = {
                "raw": {("f%03d" % f): round(float(raw[f - 1]), 2)
                        for f in (30, 60, 90, 120) if f <= n},
                "residual": {("f%03d" % f): round(float(res[f - 1]), 2)
                             for f in (30, 60, 90, 120) if f <= n},
                "residual_mean_in_slot": round(float(res[:sl].mean()), 2),
                "residual_max_in_slot": round(float(res[:sl].max()), 2),
                "residual_argmax_in_slot": int(np.argmax(res[:sl])) + 1,
            }
        pan["ladder_absolute_bar"] = PAN_BAR
        pan["locked_by_absolute_bar"] = all(
            v["residual_max_in_slot"] < PAN_BAR
            for k, v in pan.items() if isinstance(v, dict))

        return {
            "clip": str(clip.relative_to(REPO)) if str(clip).startswith(str(REPO)) else str(clip),
            "geom": geom_name,
            "frames": n,
            "slot_last_frame": sl,
            "boxes": {k: list(v) for k, v in g.items() if k != "note"},
            "box_note": g["note"],

            "T0_pan": pan,

            "last_live_pair": last_live,
            "last_live_pair_in_slot": last_live_slot,
            "dead_pairs_in_slot_of": [int((whole_step[:sl - 1] <= DEAD_PAIR).sum()), sl - 1],
            "dead_pairs_whole_of": [int((whole_step <= DEAD_PAIR).sum()), n - 1],

            "hand_drift_from_f001": {("f%03d" % f): round(float(hand_drift[f - 1]), 2)
                                     for f in (5, 8, 10, 20, 30, 50, 70, 93, 120) if f <= n},
            "hand_step_max_in_slot": round(float(hand_step[:sl - 1].max()), 2),
            "hand_step_argmax_in_slot": int(np.argmax(hand_step[:sl - 1])) + 1,

            "face_step_mean_in_slot": round(float(face_step[:sl - 1].mean()), 3),
            "face_step_mean_whole": round(float(face_step.mean()), 3),
            "face_step_by_third_of_slot": [
                round(float(face_step[a:b].mean()), 3)
                for a, b in ((0, sl // 3), (sl // 3, 2 * sl // 3), (2 * sl // 3, sl - 1))],
            "face_step_last20_max": round(float(face_step[-20:].max()), 3),

            "probe_f001": {k: box_stats(fs[0], g[k]) for k in ("hand", "face")},
            "probe_slot_end": {k: box_stats(fs[sl - 1], g[k]) for k in ("hand", "face")},
            "eye_frames_written": _write_frames(fs, frames_out, clip) if frames_out else None,
        }


def _write_frames(fs, outdir, clip):
    d = Path(outdir)
    d.mkdir(parents=True, exist_ok=True)
    stem = clip.stem[-28:]
    got = []
    for i in (1, 8, 30, 50, 70, 93, len(fs)):
        Image.open(fs[i - 1]).save(d / f"{stem}-f{i:03d}.png")
        got.append(i)
    return got


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", default=None)
    ap.add_argument("--geom", default="r2s2", choices=sorted(GEOM))
    ap.add_argument("--incumbent", action="store_true")
    ap.add_argument("--all-r2s2", action="store_true")
    ap.add_argument("--frames-out", default=None)
    a = ap.parse_args()

    jobs = []
    if a.incumbent:
        jobs.append((REPO / INCUMBENT, "r1s3"))
    if a.clip:
        jobs.append((Path(a.clip) if Path(a.clip).is_absolute() else REPO / a.clip, a.geom))
    if a.all_r2s2:
        for d in sorted((REPO / "farm-out").glob("ep2-b09-r2s2-*-0821")):
            for mp4 in sorted(d.glob("*.mp4")):
                jobs.append((mp4, "r2s2"))
    if not jobs:
        ap.error("give --incumbent, --clip or --all-r2s2")

    out = []
    for clip, geom in jobs:
        if not clip.is_file():
            print("!! missing: %s" % clip, file=sys.stderr)
            continue
        out.append(score(clip, geom, a.frames_out))
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
