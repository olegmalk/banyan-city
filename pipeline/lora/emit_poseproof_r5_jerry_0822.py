#!/usr/bin/env python3
r"""B2 ROUND FIVE: the hint is the variable nobody has ever moved.

FOUR ROUNDS HAVE NOW FAILED THE SAME CONTROL, AND THE CONSTANT IS NOT THE ONE
THE LANE KEPT CHANGING. With NO LoRA loaded, an openpose skeleton at
conditioning scale 1.0 has failed to drive a composition through:

  round 2  controlnet_plate.py txt2img, xinsir default blob   -> standing stranger
  round 3  controlnet_plate.py txt2img, xinsir TWINS blob     -> standing stranger
  round 4  inpaint_fruit.py, all-white mask, strength 1.0,    -> bust-framed girl
           TWINS blob, the path measured at 15.05 mean abs

TWO CODE PATHS, TWO BLOBS, THREE CONTROLS, ONE OUTCOME. What every one of those
runs shares is the HINT: a `jerry-canon-h37f*-0821.png` skeleton authored by this
tree. Round four's registry note read the i2i measurement -- "the net moved 15.05
mean abs" -- as proof the net drives on the inpaint path. It is not: 15.05 mean
abs is the net moving GRASS AND LIGHT. The same sentence says it "did not bend a
single knee". The net has never once been observed POSING anything in this tree.

SO THIS ROUND SWAPS THE HINT AND NOTHING ELSE. Same driver, same all-white mask,
same strength 1.0, same TWINS net, same scale, same seed, same prompt, same
weight -- and `b08-openpose-nat-0819.png` in place of the jerry sit. That hint is
the one section 28 of b08-arm-route-0819.md drove, it is the hint
`inpaint_fruit.py`'s own selftest is pinned to, and side by side with the jerry
skeleton the difference is structural rather than stylistic: the b08 hint carries
a SHOULDER BAR AND TWO ARM CHAINS hanging off the neck, and the jerry hint has a
head cluster floating at the top of a long bare torso line with no shoulders and
no arms on it. A net trained on real annotator output has nothing to read in the
second one.

WHAT EACH ANSWER MEANS, WRITTEN DOWN BEFORE THE RENDER.
  base ADOPTS  -> the instrument works, the jerry skeleton author is the bug, and
                  it is a $0 still-side fix. The wave is alive.
  base FAILS   -> the net is inert in this tree on every path and every blob, the
                  per-beat skeleton mechanism does not exist, and the goblin wave
                  cannot be built on it. That is the finding, and it stops here
                  rather than costing a fifth round.
  w08 is the actual B2 bar riding along: if a skeleton CAN drive, does his
  identity survive it, and does the pose survive his identity.

THE b08 HINT IS TWO STANDING FIGURES, which makes adoption unmissable rather
than arguable -- the prompt says `1boy, solo`, so two figures at those two
positions can only have come from the net.

  python3 pipeline/lora/emit_poseproof_r5_jerry_0822.py            # dry
  python3 pipeline/lora/emit_poseproof_r5_jerry_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v2-b2r5-0822"
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
OUT = "pipeline/lora/poseproof-jerry-b2r5-0822.yaml"

# THE NET IS THE TWINS DIRECTORY, because that is the one round three proved is
# at least the right weight, and because it is the net `inpaint_fruit.py`'s own
# selftest exercises. Same net as round three: the ONE variable moving here is
# the code path.
TWINS = r"C:\banyan-farm\cnet-openpose-twins"

# BEAT 13'S OWN POSE. Not a synthetic test pose -- the sit skeleton is the hint
# round two drove at scale 1.0 through an img2img pass without bending a knee,
# so a pass here is directly comparable to a filed failure, and a pass is
# immediately a beat.
SKELETON = "b08-openpose-nat-0819.png"
SKELETON_REL = "farm-out/ep2-b08-scale30-0820/%s" % SKELETON

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


def cell(name: str, weight):
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
            "--control", r"%s\%s" % (WORK, SKELETON),
            "--control-sha256", sha_of(SKELETON_REL),
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
    "b2r5-nat-base": (
        "B2 ROUND FIVE, THE CONTROL, AND THE ONLY VARIABLE IS THE HINT. No "
        "LoRA. Same driver, mask, strength, net, scale, seed and prompt as "
        "round four; the jerry sit skeleton is replaced by b08-openpose-nat, "
        "the hint section 28 drove and the one this driver's selftest is "
        "pinned to. Two standing figures in a `1boy, solo` frame can only "
        "have come from the net."),
    "b2r5-nat-w08": (
        "B2 ROUND FIVE, THE BAR RIDING ALONG. bnyjerry v2 fused at 0.8 on the "
        "same known-good hint. Only readable if `base` adopted: does his "
        "identity survive a driving skeleton, and does the pose survive him."),
}


def steps():
    return [
        {"name": "fetch", "argv": [PY_RENDER, r"%s\fetch_hints.py" % WORK]},
        # THE CONTROL RUNS FIRST, deliberately, and it is round two's lesson in
        # the step order: a job killed halfway should leave behind the cell that
        # tells you whether the instrument works.
        cell("b2r5-nat-base", None),
        cell("b2r5-nat-w08", SHIP_WEIGHT),
        {"name": "publish", "argv": [PY_RENDER, "-c", PUB_PY % (
            WORK.replace("\\", "/") + "/out", FARMOUT.replace("\\", "/"), JOB)]},
    ]


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
        "priority": 61, "max_attempts": 1, "est_minutes": 8,
        "owner": "the wave lane, 2026-08-22",
        "depends_on": TRAIN_JOB,
        "consumer": (
            "THE GOBLIN WAVE, and this cell decides whether it exists. The founder "
            "pre-authorised the wave ON A PASSING POSE MECHANISM; identity "
            "already passed. If a known-good hint does not drive here either, "
            "there is no per-beat pose mechanism in this tree and the wave "
            "cannot be staged the way it was authorised."),
        "success": (
            "A SEPARATION THAT SURVIVES EITHER WAY. `base` adopting means the "
            "instrument works and the jerry skeleton author is the bug -- a $0 "
            "still-side fix and the wave is alive. `base` failing means the "
            "openpose net is inert in this tree on both code paths and both "
            "blobs, the per-beat skeleton mechanism does not exist, and that "
            "is the finding rather than a fifth round."),
        "why": (
            "FOUR ROUNDS, TWO CODE PATHS, TWO BLOBS, THREE FAILED NO-LoRA "
            "CONTROLS -- and the constant across all of them is the HINT, "
            "which is the one thing never swapped. The registry read `the net "
            "moved 15.05 mean abs through inpaint_fruit.py` as proof the net "
            "drives on that path; the same sentence says it did not bend a "
            "single knee, so 15.05 is grass and light, not a pose. Side by "
            "side, b08-openpose-nat carries a shoulder bar and two arm chains "
            "off the neck and the jerry skeleton carries a head cluster on a "
            "bare torso line with neither. ONE VARIABLE MOVES: the hint."),
        "env": {
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "cell_count": {"no_lora_control": 1, "lora_w08": 1},
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
