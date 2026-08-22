#!/usr/bin/env python3
r"""B2 ROUND SEVEN: the pose net wins or the LoRA does, and the knob is one of two.

ROUND SIX SPLIT CLEANLY AND THAT SPLIT IS THE WHOLE SPEC FOR THIS JOB.
Beat 13's own AGE B seat skeleton (head_frac 0.240), on the recipe round five
passed:

  base, no LoRA   -> A SEATED FIGURE. Knees drawn up, forearms on the knees,
                     hands clasped in front -- the h240seat stance, adopted.
                     THE NET DRIVES AT THE FOUNDER'S OWN AGE DIAL.
  w08             -> A STANDING GOBLIN, framed bust-to-hip, arms at his sides.
                     Identity perfect. Pose gone.

That is reading A from the registry's round-two note, now isolated and provable
because the instrument underneath it finally works: THE LoRA OVERRIDES THE NET
AT 0.8. It is the predicted failure and the cause was written down before the
weights existed -- 21 of 21 training frames are standing, 19 of 21 are cowboy or
upper-body crops, because the route that made the dataset could not move a pose
and the pupil finding forced the framing. A trigger that learned `standing,
bust` fights a full-body seated skeleton, and at 0.8 it wins.

ROUND FIVE IS WHY THIS IS A KNOB AND NOT A WALL. There, at 0.8, the SAME LoRA
did NOT override -- b08-openpose-nat drove two full-body figures and bnyjerry
held identity on top of them. So the two forces are comparable in magnitude, and
which one wins is set by how strongly the hint speaks. Two levers reach that,
and this job walks both in one pass:

  THE WEIGHT, 0.65 / 0.50 / 0.35 at scale 1.0. Turn the LoRA down until the pose
  survives, and read where identity starts to go. The sapling ladder measured
  these two curves NOT crossing; this one has to be measured, not assumed.
  THE SCALE, 1.4 at weight 0.8. Turn the hint up instead, keeping the identity
  that already passes. Cheaper if it works, because nothing about the LoRA moves.

THE PASS IS STILL BOTH HALVES: he sits, AND he is himself at 1:1 against
taste/refs/goblin-canon-founder-0821.png. A cell that only sits is a stranger in
the right posture and is not a beat.

  python3 pipeline/lora/emit_poseproof_r7_jerry_0822.py            # dry
  python3 pipeline/lora/emit_poseproof_r7_jerry_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v2-b2r7-0822"
TRAIN_JOB = "lora-jerry-v2-0822"
WORK = r"C:\banyan-farm\%s" % JOB
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB
LORA = r"C:\banyan-farm\%s\out\bnyjerry-sdxl-v2.safetensors" % TRAIN_JOB
# THE SHA THE REGISTRY FILED FOR epoch10_final. Passed as `--lora-sha256`, so a
# run that picked up epoch08 -- one character away in the same directory --
# refuses at rc 16 instead of producing a frame nobody can attribute.
LORA_SHA = "4340857d02f17dbfa50c66e0a2d8f4dc3ffebb4fad1621bb3f59242e61bfeb8b"
PY_RENDER = r"C:\banyan-farm\venv\Scripts\python.exe"
RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
OUT = "pipeline/lora/poseproof-jerry-b2r7-0822.yaml"

# THE NET IS THE TWINS DIRECTORY, because that is the one round three proved is
# at least the right weight, and because it is the net `inpaint_fruit.py`'s own
# selftest exercises. Same net as round three: the ONE variable moving here is
# the code path.
TWINS = r"C:\banyan-farm\cnet-openpose-twins"

# BEAT 13'S OWN POSE. Not a synthetic test pose -- the sit skeleton is the hint
# round two drove at scale 1.0 through an img2img pass without bending a knee,
# so a pass here is directly comparable to a filed failure, and a pass is
# immediately a beat.
SKELETON = "jerry-skel-h240seat-0821.png"
SKELETON_REL = "farm-out/jerry-skel-assets-0820/%s" % SKELETON

# THE FLAT PLATES. See pipeline/author_jerry_poseproof_0822.py for why an
# all-white mask plus strength 1.0 is txt2img and why the init is a required
# argument with no influence.
INIT = "jerry-poseproof-init-0822.png"
MASK = "jerry-poseproof-maskall-0822.png"
ASSET_DIR = "farm-out/jerry-poseproof-assets-0822"

W, H = 832, 1216
SEED = "20260822"
SHIP_WEIGHT = "0.8"

# THE PROMPT IS ROUND ONE'S, BYTE FOR BYTE, and that is the point of it. It
# carries the trigger and NO POSE WORD -- the pose is the skeleton's job, which
# is the entire experiment, and a pose word would make a passing cell
# unattributable between the net and the wording. It carries no face term
# either: route_closure_2026_08_22 forbids one and his face is the LoRA's job.
PROMPT = ("bnyjerry, 1boy, solo, in tall grass, detailed cinematic anime, "
          "masterpiece, best quality, very aesthetic")
NEG = ("lowres, worst quality, low quality, text, watermark, photorealism, "
       "3d render, blurry, 2boys, multiple heads")

FETCH_PY = '''#!/usr/bin/env python3
"""Fetch the skeleton and the two flat plates, each by sha256.

The skeleton is the SAME BYTES rounds one through three drove -- that is what
makes this comparable to their filed failures. The plates are generated and
committed by pipeline/author_jerry_poseproof_0822.py."""
import hashlib, os, sys, urllib.request

OUT = r"%s"
UA = {"User-Agent": "banyan-city-poseproof/1.0 (albert.numbro@gmail.com)"}
WANT = {
%s
}

os.makedirs(OUT, exist_ok=True)
for name, (url, want) in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %%s -- refusing." %% name + chr(10) +
                 "   want %%s" %% want + chr(10) + "   have %%s" %% have)
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %%s %%d bytes OK" %% (name, len(raw)), flush=True)
'''

PUB_PY = '''
import hashlib, glob, os, shutil
OUT = "%s"
DST = "%s"
os.makedirs(DST, exist_ok=True)
n = 0
found = []
found += sorted(glob.glob(OUT + "/*.png"))
found += sorted(glob.glob(OUT + "/*.png.meta.yaml"))
for p in found:
    if os.path.isfile(p):
        shutil.copyfile(p, os.path.join(DST, os.path.basename(p)))
        n += 1
with open(os.path.join(DST, "%s.sha256"), "w", encoding="utf-8") as fh:
    for name in sorted(os.listdir(DST)):
        q = os.path.join(DST, name)
        if os.path.isfile(q) and not name.endswith(".sha256"):
            fh.write("%%s  %%s" %% (
                hashlib.sha256(open(q, "rb").read()).hexdigest(), name) + chr(10))
print("published", n, "file(s) ->", DST, flush=True)
if n == 0:
    raise SystemExit("NOTHING TO PUBLISH -- the sample produced no files")
'''


def sha_of(rel: str) -> str:
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def cell(name: str, weight, scale="1.0"):
    """One render. `weight` None is the no-LoRA control; `scale` is the hint's."""
    argv = [PY_RENDER, r"%s\inpaint_fruit.py" % WORK,
            "--init", r"%s\%s" % (WORK, INIT),
            "--init-sha256", sha_of("%s/%s" % (ASSET_DIR, INIT)),
            # THE MASK CARRIES NO --sha FLAG because the driver has none for it;
            # it hashes the mask itself into the sidecar. The bytes are still
            # pinned -- fetch_hints.py refuses the download on any mismatch.
            "--mask-png", r"%s\%s" % (WORK, MASK),
            # STRENGTH 1.0 AND PAD-CROP 0 ARE THE TWO HALVES OF "THIS IS
            # TXT2IMG". 1.0 runs every timestep, so the init is noised out; 0
            # turns off padding_mask_crop entirely, so diffusers crops nothing
            # and the hint is handed over at native scale (the driver's own
            # selftest: at --pad-crop 0 the magnification is exactly 1.0).
            "--strength", "1.0",
            "--pad-crop", "0",
            # AND BLUR 0, because a blurred all-white mask is still all white
            # but a blur is a knob, and a knob at a non-zero value in a control
            # experiment is a variable nobody named.
            "--blur", "0",
            "--controlnet", TWINS,
            "--control", r"%s\%s" % (WORK, SKELETON),
            "--control-sha256", sha_of(SKELETON_REL),
            "--scale", scale,
            "--prompt-file", r"%s\prompt.txt" % WORK,
            "--negative-file", r"%s\negative.txt" % WORK,
            "--steps", "40", "--cfg", "7.5", "--seed", SEED,
            "--out", r"%s\out\%s.png" % (WORK, name)]
    if weight is not None:
        argv += ["--lora", LORA, "--lora-weight", weight,
                 "--lora-sha256", LORA_SHA]
    argv += ["--note", NOTES[name]]
    return {"name": name, "argv": argv}


NOTES = {
    "b2r7-b13seat-w065": (
        "B2 ROUND SEVEN, THE WEIGHT LADDER at 0.65, hint scale 1.0. At 0.8 the "
        "LoRA overrode beat 13's seat skeleton, which the same skeleton "
        "drove cleanly with no LoRA in the pass. Turning the trigger down "
        "until the pose survives, and reading where his face starts to go."),
    "b2r7-b13seat-w050": (
        "B2 ROUND SEVEN, THE WEIGHT LADDER at 0.50, hint scale 1.0. At 0.8 the "
        "LoRA overrode beat 13's seat skeleton, which the same skeleton "
        "drove cleanly with no LoRA in the pass. Turning the trigger down "
        "until the pose survives, and reading where his face starts to go."),
    "b2r7-b13seat-w035": (
        "B2 ROUND SEVEN, THE WEIGHT LADDER at 0.35, hint scale 1.0. At 0.8 the "
        "LoRA overrode beat 13's seat skeleton, which the same skeleton "
        "drove cleanly with no LoRA in the pass. Turning the trigger down "
        "until the pose survives, and reading where his face starts to go."),
    "b2r7-b13seat-w080-s14": (
        "B2 ROUND SEVEN, THE OTHER LEVER. Weight stays at 0.8 -- the value "
        "identity passed at -- and the HINT is turned up to 1.4 instead. If "
        "this sits, the wave keeps the identity it already has and nothing "
        "about the LoRA moves."),
}


def steps():
    # THE LADDER RUNS DOWN, and the scale arm runs LAST rather than first. If
    # the job is killed halfway the weight curve is the half worth having:
    # it is three points on a line, and one point of a different lever is not.
    out = [{"name": "fetch", "argv": [PY_RENDER, r"%s\fetch_hints.py" % WORK]}]
    for w in ("0.65", "0.50", "0.35"):
        out.append(cell("b2r7-b13seat-w%s" % w.replace(".", ""), w))
    out.append(cell("b2r7-b13seat-w080-s14", "0.8", scale="1.4"))
    out.append({"name": "publish", "argv": [PY_RENDER, "-c", PUB_PY % (
        WORK.replace("\\", "/") + "/out", FARMOUT.replace("\\", "/"), JOB)]})
    return out


def payloads() -> dict:
    """Scripts and prompts written to the box at enqueue time.

    THE DRIVER TRAVELS AS SOURCE, this tree's standing pattern: the job carries
    the exact bytes it ran, so a verdict months later is reproducible after the
    repo moves on. This copy of `inpaint_fruit.py` is the one that grew `--lora`.
    """
    pay = {}
    pay[r"%s\inpaint_fruit.py" % WORK] = open(
        os.path.join(REPO, "pipeline/inpaint_fruit.py"), encoding="utf-8").read()
    pay[r"%s\prompt.txt" % WORK] = PROMPT
    pay[r"%s\negative.txt" % WORK] = NEG
    # THE PNGs ARE FETCHED, NOT PAYLOADED -- payloads are text, and every image
    # this tree sends to the card is pinned by sha256 and refused on mismatch.
    lines = []
    for rel in (SKELETON_REL, "%s/%s" % (ASSET_DIR, INIT),
                "%s/%s" % (ASSET_DIR, MASK)):
        lines.append('    "%s": ("%s%s", "%s"),'
                     % (os.path.basename(rel), RAW, rel, sha_of(rel)))
    pay[r"%s\fetch_hints.py" % WORK] = FETCH_PY % (WORK, chr(10).join(lines))
    return pay


def main() -> int:
    import yaml
    write = "--write" in sys.argv
    st = steps()
    spec = {
        "id": JOB, "task": JOB, "node": "002b-first-citizen",
        "runner": "box", "needs_gpu": True, "needs": ["cuda", "vram20"],
        "priority": 63, "max_attempts": 1, "est_minutes": 6,
        "owner": "the wave lane, 2026-08-22",
        "depends_on": TRAIN_JOB,
        "consumer": (
            "THE GOBLIN WAVE'S RECIPE. Everything else is settled: the path, "
            "the net, the hint family and the identity. This picks the two "
            "numbers the fifteen plates are rendered at."),
        "success": (
            "ONE CELL THAT HOLDS BOTH HALVES: beat 13's seated stance AND "
            "bnyjerry at 1:1. That cell's weight-and-scale pair is the wave's "
            "recipe. If the two curves cross -- pose only arriving below the "
            "weight where his face leaves -- then the dataset's standing "
            "monoculture is the blocker and the answer is a retrain on posed "
            "frames, which this job would have measured rather than guessed."),
        "why": (
            "ROUND SIX ISOLATED THE CONFLICT with a working instrument under "
            "it: the h240seat skeleton drives a seated figure with no LoRA, and "
            "the LoRA at 0.8 replaces it with the standing bust its 21 standing "
            "training frames taught. Round five proves the two forces are "
            "comparable -- there, at the same 0.8, the net won. So which one "
            "wins is a knob, and there are exactly two knobs."),
        "env": {
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "cell_count": {"weight_ladder": 3, "scale_arm": 1},
        "payload": payloads(),
        "steps": st,
        # THE PICTURES ARE CLAIMED BY THE PUBLISH GLOB. inpaint_fruit takes an
        # explicit --out, so the names DO appear in argv, but they land in the
        # work dir and travel via farm-out; the .sha256 is the one declared
        # artifact and the glob is what the arm guard reads.
        "artifacts": [r"%s\%s.sha256" % (FARMOUT, JOB)],
    }
    if not write:
        print("would emit %s with %d step(s)" % (OUT, len(st)))
        for s in st:
            print("   %s" % s["name"])
        return 0
    with open(os.path.join(REPO, OUT), "w", encoding="utf-8") as fh:
        fh.write("# B2 ROUND FOUR -- the pose bar on inpaint_fruit.py's proven\n"
                 "# ControlNet path. GENERATED. Edit\n"
                 "# pipeline/lora/emit_poseproof_jerry_0822.py, not this file.\n\n")
        yaml.safe_dump(spec, fh, sort_keys=False, width=88, allow_unicode=True)
    print("wrote %s  (%d steps)" % (OUT, len(st)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
