#!/usr/bin/env python3
"""Generate a PLATE TWIN job spec for every clip in the v34 motion series.

WHAT A TWIN IS. Every clip in `C:\\banyan-farm\\v34-motion-0810\\` was rendered by
feeding the renderer a raw 832x1216 still, which it resized to 704x1280 without
regard to aspect -- a 24.4% vertical stretch (26ece5c). A twin is the same clip
re-rendered with exactly one thing changed: `--init` is fed a 704x1280 plate
prepared by `plate_prep.prepare_plate` (CROP_POLICY = "cover-centre") instead of
the raw still. Prompt, negative, seed, size, frames, fps, steps, guidance,
sigmas, two-stage and the renderer binary are all held fixed.

WHY GENERATED RATHER THAN HAND-WRITTEN. The recipe for each twin is read out of
that clip's OWN `.meta.yaml` -- the text that actually rendered -- not retyped
from a spec. Two specs in `pipeline/jobs/` (ep1-b04/b07-v34-motion-r2) show why
that matters: both mandate prepare_plate, both name seeds and prompts that never
ran, and the clips on disk carry different ones. A spec can drift from the
render; a sidecar written at render time cannot.

WHY EVERY ROUND AND NOT A CHOSEN FEW. Which round of a beat belongs in the v35
cut is a taste call (R4) and is currently unresolved -- 879820f and 655d2c6 both
record later rounds being worse than earlier ones, so "latest" is not a safe
proxy for "best". Twinning all of them makes every candidate available in correct
geometry and leaves the choice where it belongs. Priority orders latest-round-
first per beat so that if the queue is interrupted the likeliest candidates exist.

THE ONE SAMPLE THIS SCALES FROM is ep1-b08-v34-plate-ab, which drained at 03:41Z
and measured frame 0 at MAD 2.83 vs a cover-crop of its still and 17.22 vs a
stretch of it -- the exact inverse of its raw-init pair (2.75 / 17.17) -- with the
picture content unchanged. This script exists because that sample passed.

    python3 pipeline/plate_twins.py            # write specs into pipeline/jobs/
    python3 pipeline/plate_twins.py --list     # what it would generate
"""

from __future__ import annotations

import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = os.path.join(REPO, "pipeline", "jobs")

SERIES_DIR = r"C:\banyan-farm\v34-motion-0810"
PLATE_DIR = r"C:\banyan-farm\v34-plates-0810"
STILLS = (r"C:\banyan-farm\banyan-city\genomes\sapling\nodes"
          r"\001-capability-inventory\stills")
# The series copy, sha256 d49f8ecb.., which matches neither repo HEAD nor the
# working tree. Using it is what keeps a twin comparable to its pair; swapping in
# the repo copy would change two things at once. Recorded, not quietly fixed.
RENDERER = r"C:\banyan-farm\ltx_i2v.py"
VENV_PY = r"C:\banyan-video\venv\Scripts\python.exe"
NODE = "001-capability-inventory"          # founder-approved, leaf 001-t0-d.yaml

STILL_FOR_BEAT = {
    3: "03-deploy-succeeded.png",
    4: "04-the-fall.png",
    7: "07-zero-0-moving-parts.png",
    8: "08-sev-1.png",
    10: "10-sense.png",
}

# A twin of this already exists -- it is the sample the rest scale from.
ALREADY_TWINNED = {"08-ltx-r2-s20260739"}

ENV = {
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8",
    "PYTHONUNBUFFERED": "1",
    "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
    "HF_HUB_DISABLE_XET": "1",
    "HF_HUB_DOWNLOAD_TIMEOUT": "60",
    "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
    "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
}


def strip_annotation(text: str) -> str:
    """Drop the `[unused: ...]` line video_task appends inside the negative block.

    It is a note the sidecar writer added at render time, not part of the prompt
    that was encoded. Feeding it back in would make the twin's conditioning differ
    from its pair by a line of English -- the exact thing a twin must not do.
    """
    lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("[unused:")]
    return "\n".join(lines).rstrip()


def parse_round(stem: str) -> tuple:
    """`03-ltx-r3-s20260734` -> ('r3', 3). The wave round carries no token."""
    m = re.match(r"^(\d+)-ltx-(?:(.+)-)?s(\d+)$", stem)
    if not m:
        raise SystemExit("!! cannot parse clip stem %r" % stem)
    beat, token, seed = int(m.group(1)), m.group(2), m.group(3)
    if token is None:
        return "r1", beat, seed, "wave"        # the original ep1-v34-motion-wave
    return token, beat, seed, token


def steps_of(meta: dict) -> tuple:
    """'8@352x640+3@704x1280' -> (8, True). Asserts rather than assumes.

    Every clip in this series was rendered two-stage at these sizes. If one was
    not, its twin cannot be produced by this template and the job must be written
    by hand -- so this raises instead of silently rendering something else.
    """
    s = str(meta.get("steps", ""))
    m = re.match(r"^(\d+)@352x640\+(\d+)@704x1280$", s)
    if not m:
        raise SystemExit("!! unexpected steps %r -- twin template does not cover it" % s)
    return int(m.group(1)), True


def spec_for(path: str) -> dict:
    import yaml

    stem = os.path.basename(path)[:-len(".mp4.meta.yaml")]
    with open(path, encoding="utf-8") as fh:
        meta = yaml.safe_load(fh)
    rnd, beat, seed, label = parse_round(stem)
    if str(meta.get("seed")) != seed:
        raise SystemExit("!! %s: filename seed %s != meta seed %s"
                         % (stem, seed, meta.get("seed")))
    if str(meta.get("size")) != "704x1280":
        raise SystemExit("!! %s: size %s" % (stem, meta.get("size")))
    steps, two_stage = steps_of(meta)
    frames = int(round(float(meta["seconds"]) * 24))
    guidance = str(meta["guidance"])
    still = STILL_FOR_BEAT[beat]
    out_mp4 = "%s\\%s.mp4" % (SERIES_DIR, stem.replace("-s%s" % seed, "-plate-s%s" % seed))
    jid = "ep1-b%02d-v34-plate-twin-%s" % (beat, rnd)
    task = "%s-0810" % jid
    prompt_f = "%s\\%s-prompt.txt" % (PLATE_DIR, jid)
    neg_f = "%s\\%s-negative.txt" % (PLATE_DIR, jid)
    embeds = "%s\\ltx-embeds-%s.pt" % (PLATE_DIR, jid)
    plate = "%s\\%02d-704x1280.png" % (PLATE_DIR, beat)

    render_argv = [
        VENV_PY, RENDERER, "--stage", "render",
        "--embeds", embeds,
        "--prompt-file", prompt_f, "--negative-file", neg_f,
        "--init", plate,
        "--out", out_mp4,
        "--size", "704x1280",
        "--frames", str(frames),
        "--fps", "24",
        "--steps", str(steps),
        "--guidance", guidance,
        "--distilled-sigmas",
    ]
    if two_stage:
        render_argv.append("--two-stage")
    render_argv += ["--seed", seed, "--beat", str(beat),
                    "--task", task, "--worker", "rtx5090"]

    return {
        "id": jid,
        "task": task,
        "node": NODE,
        "beat": beat,
        "runner": "box",
        "needs_gpu": True,
        # latest round of a beat first: r5 -> 30, r4 -> 31, ... so an interrupted
        # queue still leaves the likeliest cut candidates on disk.
        "priority": 30 + (9 - int(re.match(r"r(\d+)", rnd).group(1))),
        "max_attempts": 1,
        "owner": "card-runner (plate twins)",
        "source_clip": "%s\\%s.mp4" % (SERIES_DIR, stem),
        "consumer": (
            "the v35 screening cut. Its ingredient for beat %d must be a "
            "cover-crop like every beat already in the cut; the existing clip is "
            "a 24.4%% vertical stretch and would jump against its neighbours. "
            "Which ROUND of beat %d the cut uses is R4's open call -- this makes "
            "that call choosable by giving every candidate correct geometry."
            % (beat, beat)),
        "success": (
            "A 704x1280 %d-frame mp4 at %s whose frame 0 matches a cover-centre "
            "crop of %s rather than a naive stretch of it, by the mean-absolute-"
            "difference test in 26ece5c, and whose picture content matches its "
            "pair %s.mp4. Content drift is a finding, not a pass."
            % (frames, out_mp4, still, stem)),
        "why": (
            "One variable against its pair: --init is a prepared plate instead of "
            "the raw 832x1216 still. Recipe copied from %s.mp4.meta.yaml."
            % stem),
        "est_minutes": 5,
        "needs": ["cuda", "vram20", "video-venv"],
        "payload": {
            prompt_f: strip_annotation(meta["prompt"]),
            neg_f: strip_annotation(meta["negative"]),
        },
        "env": dict(ENV),
        "steps": [
            {"name": "plate", "argv": [VENV_PY, "-c",
                'import sys; sys.path.insert(0, r"C:\\banyan-farm\\banyan-city\\pipeline")\n'
                'from plate_prep import prepare_plate\n'
                'out, rec = prepare_plate(\n'
                '    r"%s\\%s",\n'
                '    "704x1280", r"%s", "%02d")\n'
                'print("plate", out); print(rec["plate_wxh"], rec["crop_policy"])\n'
                % (STILLS, still, PLATE_DIR, beat)]},
            {"name": "encode", "argv": [
                VENV_PY, RENDERER, "--stage", "encode", "--embeds", embeds,
                "--prompt-file", prompt_f, "--negative-file", neg_f]},
            {"name": "render", "argv": render_argv},
        ],
        "artifacts": [plate, out_mp4],
    }


HEADER = """\
# GENERATED by pipeline/plate_twins.py -- do not hand-edit, regenerate.
#
# Plate twin of {src}.mp4: the same render with `--init` fed a 704x1280
# cover-centre plate instead of the raw 832x1216 still. Every other argument was
# read out of that clip's own .meta.yaml, which is the text that actually
# rendered. See 26ece5c for the 24.4% stretch this corrects and the b08 plate A/B
# that showed the correction works without changing the picture.
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("metas", nargs="+", help="local copies of <clip>.mp4.meta.yaml")
    ap.add_argument("--list", action="store_true", help="print, write nothing")
    args = ap.parse_args(argv)

    import yaml

    written = []
    for path in sorted(args.metas):
        stem = os.path.basename(path)[:-len(".mp4.meta.yaml")]
        if stem in ALREADY_TWINNED or "-plate-" in stem:
            print("  skip %-28s (twin exists)" % stem)
            continue
        spec = spec_for(path)
        dest = os.path.join(JOBS, spec["id"] + ".yaml")
        print("  %-30s -> %s  prio %d" % (stem, os.path.basename(dest), spec["priority"]))
        if args.list:
            continue
        body = HEADER.format(src=stem) + yaml.safe_dump(
            spec, sort_keys=False, allow_unicode=True, width=100, default_flow_style=False)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(body)
        written.append(dest)
    if written:
        print("\nwrote %d specs" % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
