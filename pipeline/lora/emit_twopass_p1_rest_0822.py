#!/usr/bin/env python3
r"""PASS ONE for the other three AGE B stances, because it needs nobody awake.

BEAT 13 IS PROVEN AND THESE ARE THE SAME HALF OF THE SAME RECIPE.
`twopass2-b13seat-s075` holds both halves: beat 13's seated stance and, at 1:1
against taste/refs/goblin-canon-founder-0821.png, his dome, his near-horizontal
pointed ears with the dark inner shell, his narrow almond eye and tiny dark
pupil, his brow furrow. Pass one is the half that carries the POSE and the
LIGHT and loads no LoRA at all, so it involves no taste call and no weight
choice -- it is the slow, decidable half, and the founder's screening gates
publication and verdicts, not staging that needs no human present.

THE THREE REMAINING AGE B SKELETONS ARE THE FOUNDER'S OWN AGE DIAL, authored at
head_frac 0.240 and already filed against their beats:

  jerry-skel-h240stride-0821   beat 02, THE SPRINT
  jerry-skel-h240crouch-0821   beats 03 (BAD COVER) and 20 (EVIDENCE)
  jerry-skel-h240hunch-0821    beat 04, THE FOOTNOTE

Same net, same scale, same seed, same daylight wording, no LoRA. Each output is
pass two's `--init` for its beat, and pass two cannot be queued until these
exist because its init sha has to be known before its argv is written. That
dependency is the reason this runs now rather than after a review pass.

WHAT THIS IS NOT. It is not the wave. No plate here is published, none is
assembled, and none carries the goblin at all -- pass one draws a stranger in
the right posture on purpose. The taste call on the wave is still the founder's.

  python3 pipeline/lora/emit_twopass_p1_rest_0822.py            # dry
  python3 pipeline/lora/emit_twopass_p1_rest_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v2-tp1rest-0822"
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
OUT = "pipeline/lora/twopass-p1rest-jerry-0822.yaml"

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
# THE ONLY CHANGE FROM ROUND SIX'S PROMPT IS THE LIGHT KEY, and it is the light
# the founder's own canon frame is lit by: flat, cool, overcast daylight, which
# is what lets his skin read as the desaturated sage of that image instead of
# taking a colour from whatever hour the sampler picks. No pose word, still --
# the pose is the skeleton's job and a pose word would make a passing cell
# unattributable. No face term -- route_closure_2026_08_22 forbids one.
PROMPT = ("1boy, solo, in tall grass, soft overcast daylight, flat even light, "
          "detailed cinematic anime, masterpiece, best quality, very aesthetic")

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


def cell(name: str, weight, hint):
    """One render. `weight` None is the no-LoRA control."""
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
            "--control", r"%s\%s" % (WORK, hint),
            "--control-sha256", sha_of("farm-out/jerry-skel-assets-0820/%s" % hint),
            "--scale", "1.0",
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
    "tp1rest-b02stride": (
        "PASS ONE, beat 02, THE SPRINT. No LoRA: this plate carries the POSE and the "
        "flat overcast daylight, and pass two puts bnyjerry into it at "
        "strength 0.75 -- the recipe beat 13 passed both halves on."),
    "tp1rest-b03crouch": (
        "PASS ONE, beats 03 BAD COVER and 20 EVIDENCE. No LoRA: this plate carries the POSE and the "
        "flat overcast daylight, and pass two puts bnyjerry into it at "
        "strength 0.75 -- the recipe beat 13 passed both halves on."),
    "tp1rest-b04hunch": (
        "PASS ONE, beat 04, THE FOOTNOTE. No LoRA: this plate carries the POSE and the "
        "flat overcast daylight, and pass two puts bnyjerry into it at "
        "strength 0.75 -- the recipe beat 13 passed both halves on."),
}


def steps():
    out = [{"name": "fetch", "argv": [PY_RENDER, r"%s\fetch_hints.py" % WORK]}]
    out.append(cell("tp1rest-b02stride", None, "jerry-skel-h240stride-0821.png"))
    out.append(cell("tp1rest-b03crouch", None, "jerry-skel-h240crouch-0821.png"))
    out.append(cell("tp1rest-b04hunch", None, "jerry-skel-h240hunch-0821.png"))
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
    lines.append('    "jerry-skel-h240stride-0821.png": ("%s%s", "%s"),' % (
        RAW, "farm-out/jerry-skel-assets-0820/jerry-skel-h240stride-0821.png",
        sha_of("farm-out/jerry-skel-assets-0820/jerry-skel-h240stride-0821.png")))
    lines.append('    "jerry-skel-h240crouch-0821.png": ("%s%s", "%s"),' % (
        RAW, "farm-out/jerry-skel-assets-0820/jerry-skel-h240crouch-0821.png",
        sha_of("farm-out/jerry-skel-assets-0820/jerry-skel-h240crouch-0821.png")))
    lines.append('    "jerry-skel-h240hunch-0821.png": ("%s%s", "%s"),' % (
        RAW, "farm-out/jerry-skel-assets-0820/jerry-skel-h240hunch-0821.png",
        sha_of("farm-out/jerry-skel-assets-0820/jerry-skel-h240hunch-0821.png")))
    # AND THE TWO FLAT PLATES. Dropped from this list once already, which cost
    # a job: the fetch reported three skeletons OK and inpaint_fruit refused rc
    # 2 on a missing init one line later. Every file the argv NAMES has to be
    # in the fetch, not only the ones that changed.
    for rel in ("%s/%s" % (ASSET_DIR, INIT), "%s/%s" % (ASSET_DIR, MASK)):
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
        "priority": 55, "max_attempts": 1, "est_minutes": 6,
        "owner": "the wave lane, 2026-08-22",
        "depends_on": TRAIN_JOB,
        "consumer": (
            "PASS TWO, immediately, as its --init. And behind it the wave: this "
            "is the first half of the only recipe that has ever put beat 13's "
            "pose and the goblin's face in one frame."),
        "success": (
            "A SEATED FIGURE IN FLAT DAYLIGHT. The stance is already proven at "
            "these settings; the only open question is whether naming the light "
            "costs the pose anything, and the answer has to be looked at before "
            "pass two runs on it."),
        "why": (
            "The two-pass produced a seated goblin whose only fault is a mauve "
            "skin and a crown cowlick, both inherited from a pass-one plate "
            "rendered in a purple twilight nobody asked for. The i2i route "
            "cannot re-ground a colour it is handed, so the colour has to be "
            "correct before it is handed over."),
        "env": {
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "cell_count": {"pass_one_plates": 3},
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
