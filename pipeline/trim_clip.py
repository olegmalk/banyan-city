#!/usr/bin/env python3
r"""trim_clip.py — cut frames off the head and/or tail of a rendered mp4 and
write the 7.2 provenance sidecar that says what was cut and why.

    python3 pipeline/trim_clip.py --src IN.mp4 --out OUT.mp4 \
        --start-frame 0 --end-frame 85 --why "..." [--task ...]

WHY THIS IS A FILE AND NOT A ONE-LINER. Every trim in this tree so far was a
hand-typed ffmpeg line plus a hand-typed sidecar, and the two drifted: a clip
whose sidecar says 108 frames and whose container says 121 is a provenance
claim that is simply false, and §7.2 makes the sidecar the published record.
So the frame count in the sidecar is READ BACK OUT OF THE WRITTEN FILE with
ffprobe rather than computed from the arguments, and the source digest is
hashed from the bytes on disk rather than copied from whatever the caller
believed the source was.

TRIM IS THE CHEAPEST LEVER IN THE LADDER (trim > composite > wording > seed
batch) and it is $0: no sampler runs, no GPU is touched, nothing is queued.
The re-encode is libx264 crf 10, matching what the pipeline's other trims do,
because the sources are crf-10 or crf-33 mp4s and a stream copy cannot cut on
an arbitrary frame.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
         "-show_entries", "stream=nb_read_frames,width,height,r_frame_rate",
         "-of", "json", path], capture_output=True, text=True,
        encoding="utf-8", check=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return (int(s["nb_read_frames"]), int(s["width"]), int(s["height"]),
            float(num) / float(den))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--start-frame", type=int, default=0,
                    help="first frame KEPT (inclusive)")
    ap.add_argument("--end-frame", type=int, default=-1,
                    help="last frame KEPT (inclusive); -1 = to the end")
    ap.add_argument("--why", required=True,
                    help="what is being cut and what was measured")
    ap.add_argument("--task", default="")
    ap.add_argument("--crf", default="10")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    src = a.src if os.path.isabs(a.src) else os.path.join(REPO, a.src)
    out = a.out if os.path.isabs(a.out) else os.path.join(REPO, a.out)
    if not os.path.isfile(src):
        raise SystemExit("!! no such source: %s" % src)
    if os.path.abspath(src) == os.path.abspath(out):
        raise SystemExit("!! refusing to trim a clip onto itself")

    n_src, w, h, fps = probe(src)
    last = n_src - 1 if a.end_frame < 0 else a.end_frame
    if not (0 <= a.start_frame <= last <= n_src - 1):
        raise SystemExit("!! frame window %d..%d is not inside 0..%d"
                         % (a.start_frame, last, n_src - 1))
    if a.start_frame == 0 and last == n_src - 1:
        raise SystemExit("!! that window is the whole clip -- nothing to trim")

    src_sha = sha256(src)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    sel = "between(n\\,%d\\,%d)" % (a.start_frame, last)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", src,
         "-vf", "select='%s',setpts=N/FRAME_RATE/TB" % sel,
         "-an", "-c:v", "libx264", "-crf", a.crf, "-pix_fmt", "yuv420p",
         "-r", "%g" % fps, out], check=True)

    n_out, ow, oh, ofps = probe(out)          # READ BACK, never assumed
    want = last - a.start_frame + 1
    if n_out != want:
        raise SystemExit("!! wrote %d frames, the window says %d -- refusing "
                         "to write a sidecar that disagrees with the file"
                         % (n_out, want))

    # Carry what the source's own sidecar knows, so the trim does not erase
    # the render's provenance.
    src_side = src + ".meta.yaml"
    inherited = {}
    if os.path.isfile(src_side):
        inherited = yaml.safe_load(open(src_side, encoding="utf-8")) or {}

    meta = {
        "platform": "local-deterministic (ffmpeg trim of a rendered mp4)",
        "model": "none - no sampler ran for this clip",
        "model_licence": "n/a - the edit adds no model output",
        "source_clip": os.path.basename(src),
        "source_path": os.path.relpath(src, REPO),
        "source_sha256": src_sha,
        "source_frames": n_src,
        "source_platform": inherited.get("platform")
                           or inherited.get("source_platform") or "unrecorded",
        "source_model": inherited.get("model")
                        or inherited.get("source_model") or "unrecorded",
        "source_model_licence": inherited.get("model_licence")
                                or inherited.get("source_model_licence")
                                or "unrecorded",
        "shot_beat": inherited.get("shot_beat"),
        "size": "%dx%d" % (ow, oh),
        "fps": ofps,
        "frames": n_out,
        "seconds": round(n_out / ofps, 3),
        "edit": ("ffmpeg select frames %d..%d of %d, re-encoded libx264 crf %s"
                 % (a.start_frame, last, n_src, a.crf)),
        "frames_cut_head": a.start_frame,
        "frames_cut_tail": n_src - 1 - last,
        "seed": inherited.get("seed"),
        "guidance": inherited.get("guidance"),
        "steps": inherited.get("steps"),
        "task": a.task or inherited.get("task"),
        "cost_usd": 0,
        "mode": "production",
        "why_trimmed": a.why,
    }
    meta = {k: v for k, v in meta.items() if v is not None}
    with open(out + ".meta.yaml", "w", encoding="utf-8") as fh:
        fh.write("# Shot provenance (7.2) - EDIT of a rendered mp4. "
                 "No sampler ran for this file.\n")
        yaml.safe_dump(meta, fh, sort_keys=False, width=88,
                       allow_unicode=True, default_flow_style=False)

    print("%s  %d -> %d frames (%.2fs), head -%d tail -%d"
          % (os.path.relpath(out, REPO), n_src, n_out, n_out / ofps,
             a.start_frame, n_src - 1 - last))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
