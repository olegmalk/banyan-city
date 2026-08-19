#!/usr/bin/env python3
"""The two numbers the sapcomp-motion bar asks for, and NOTHING ELSE.

    python3 pipeline/measure_sapcomp_motion_0820.py <clip.mp4> --spec <spec.yaml>
                                                    [--out <dir>]

Reports exactly two measured clauses and refuses to pretend it can report the
others:

  A5  WHOLE-FRAME MEAN LUMA at f000 and at the last frame, and the delta. The
      growmotion five put five seeds of ONE recipe on ONE init at +67.70,
      +57.06, +43.56, +22.42 and +10.68 -- a 6x spread that is a property of
      the SEED, so a blowout here is re-rolled rather than re-flagged. Whole
      frame, so no mask and no predicate can bias it.

  A2  THE SKIN PROBE, read out of the spec's own `skin_probe` block so the box
      cannot be moved after the pixels exist. R, G, B, R-B and luma at f000 and
      at the last frame. THE WHOLE TRIPLE IS PUBLISHED, not a single scalar:
      §18 of the ladder said publish the MATERIAL and not only the luma, after
      a probe placed by colour landed on a cream sleeve and produced a clean,
      wrong number -- and a GREEN-SKINNED figure on a GREEN field is exactly
      the case where one scalar decides nothing. The box in every spec was
      placed BY EYE at 5x on skin, never by a colour rule.

WHAT THIS DELIBERATELY DOES NOT MEASURE, and the refusal is the point.

  A1 (the plant holds), A3 (camera), A4 (not frozen) and every beat clause are
  left to eyes on the sheet this writes. A1 in particular: the obvious
  instrument is a green mask over the plant, and this repo has already paid for
  that twice. `ep2-b01-growmotion-b13-0819` warns that a colour-predicate mask
  reported a one-frame colour pop and a 2.0x-2.5x area step that were BOTH
  ARTEFACTS OF THE MASK, and the judging lane that built a luma-normalised
  green-magenta replacement watched it drop the subject entirely through a
  desaturated phase and manufacture a 3.9x step out of nothing. Five clips went
  UNSCORED rather than scored off that instrument, which was the right call.
  Counting two leaves is a job for a person looking at five frames.

  A3 likewise: beat 19's raw [4,4] horizon shift was NOT a camera move -- the
  vertical fit was +3px on the low-contrast horizon and -1px on the
  high-contrast fence posts, i.e. the field RE-INKING. A raw global fit here
  would report a camera fault that does not exist.

  A4 likewise: a whole-frame interframe floor is the wrong instrument on a
  near-still beat. Beat 19's tracker self-test showed a PERFECT 32px subject
  move over a frozen background reads 0.056 whole-frame. Use
  pipeline/judge_clip.py for HOLD/DEPTH/FREEZE, which answers "how deep is the
  hold" honestly, and then open the frames.

$0. ffmpeg + Pillow + numpy. No model, no network, no GPU.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import yaml
from PIL import Image

SHEET_FRACTIONS = (0.0, 0.25, 0.5, 0.75, 1.0)


def luma(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def frame_count(clip):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
         "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", clip],
        capture_output=True, text=True, check=True)
    return int(out.stdout.strip())


def extract(clip, idx, dst):
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", clip,
         "-vf", "select=eq(n\\,%d)" % idx, "-vsync", "0", "-frames:v", "1", dst],
        check=True)
    return Image.open(dst).convert("RGB")


def read_box(im, box):
    a = np.asarray(im.crop(tuple(box))).astype(float)
    l = luma(a)
    return dict(R=round(float(a[..., 0].mean()), 1),
                G=round(float(a[..., 1].mean()), 1),
                B=round(float(a[..., 2].mean()), 1),
                R_minus_B=round(float(a[..., 0].mean() - a[..., 2].mean()), 1),
                luma=round(float(l.mean()), 1),
                luma_std=round(float(l.std()), 1))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("--spec", required=True,
                    help="the job spec, read for its pre-registered skin_probe box")
    ap.add_argument("--out", default=None, help="where the frame sheet goes")
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)

    spec = yaml.safe_load(open(a.spec))
    probe = spec.get("skin_probe") or {}
    box = probe.get("box_xyxy_in_the_704x1280_init")
    if not box:
        sys.exit("!! %s carries no skin_probe.box_xyxy_in_the_704x1280_init -- "
                 "refusing to invent one after the pixels exist." % a.spec)

    n = frame_count(a.clip)
    idxs = sorted({min(n - 1, int(round(f * (n - 1)))) for f in SHEET_FRACTIONS})
    out_dir = a.out or os.path.join(os.path.dirname(os.path.abspath(a.clip)) or ".",
                                    "sheet-" + os.path.basename(a.clip).rsplit(".", 1)[0])
    os.makedirs(out_dir, exist_ok=True)

    frames, rows = {}, []
    with tempfile.TemporaryDirectory() as td:
        for i in idxs:
            im = extract(a.clip, i, os.path.join(td, "f%04d.png" % i))
            frames[i] = im
            whole = np.asarray(im).astype(float)
            rows.append(dict(frame=i,
                             whole_frame_luma=round(float(luma(whole).mean()), 2),
                             skin=read_box(im, box)))

    first, last = rows[0], rows[-1]
    report = {
        "clip": os.path.basename(a.clip),
        "spec": os.path.basename(a.spec),
        "frames_in_clip": n,
        "size": list(frames[idxs[0]].size),
        "A5_whole_frame_luma": {
            "f%03d" % first["frame"]: first["whole_frame_luma"],
            "f%03d" % last["frame"]: last["whole_frame_luma"],
            "delta": round(last["whole_frame_luma"] - first["whole_frame_luma"], 2),
            "bar": "within +25; a blowout is SEED-sensitive and is re-rolled, "
                   "not re-flagged",
        },
        "A2_skin_probe": {
            "box_xyxy": list(box),
            "placed_on": probe.get("placed_on"),
            "spec_f000_reading": probe.get("f000_reading"),
            "f%03d" % first["frame"]: first["skin"],
            "f%03d" % last["frame"]: last["skin"],
            "delta_luma": round(last["skin"]["luma"] - first["skin"]["luma"], 1),
            "delta_R_minus_B": round(
                last["skin"]["R_minus_B"] - first["skin"]["R_minus_B"], 1),
            "bar": "within +/-25 luma and +/-15 R-B, and the eyes decide",
        },
        "per_sampled_frame": rows,
        "NOT_MEASURED_HERE": (
            "A1 the plant holds, A3 camera, A4 not-frozen and every beat clause. "
            "A1 needs eyes: a colour-predicate plant mask has produced a clean "
            "wrong number twice in this repo and five clips were left UNSCORED "
            "rather than scored off one. Use judge_clip.py for HOLD/DEPTH/FREEZE "
            "and open the sheet."),
    }

    # the sheet the eyes actually judge on
    cells = [frames[i] for i in idxs]
    w, h = cells[0].size
    scale = 0.5
    cw, ch = int(w * scale), int(h * scale)
    sheet = Image.new("RGB", (cw * len(cells) + 8 * (len(cells) - 1), ch), (18, 18, 18))
    for k, im in enumerate(cells):
        sheet.paste(im.resize((cw, ch), Image.LANCZOS), (k * (cw + 8), 0))
    sheet_path = os.path.join(out_dir, "SHEET-%s.png"
                              % os.path.basename(a.clip).rsplit(".", 1)[0])
    sheet.save(sheet_path)
    report["sheet"] = sheet_path
    report["sheet_frames"] = idxs

    txt = json.dumps(report, indent=2)
    print(txt)
    if a.json:
        with open(a.json, "w") as fh:
            fh.write(txt + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
