#!/usr/bin/env python3
r"""THE TWO-PASS, PASS TWO, ON THE RELIT PLATE. This is the wave's candidate recipe.

WHERE THIS STANDS AFTER SEVEN ROUNDS.
  * The pose net DRIVES through `inpaint_fruit.py` with an all-white mask at
    strength 1.0 -- proven twice with no LoRA in the pass, once on a two-figure
    standing hint and once on beat 13's own seated one.
  * bnyjerry v2 HOLDS identity at 0.8 -- founder-ratified dataset, read at 1:1.
  * THE TWO CANNOT SHARE ONE PASS on a non-standing pose. Round seven walked the
    weight to 0.35 and the hint to scale 1.4: his face leaves between 0.65 and
    0.50 and the seated legs never arrive at any rung. 21 of 21 training frames
    are standing and that is a lower-body prior no knob reaches.
  * SPLIT ACROSS TWO PASSES THEY BOTH SURVIVE. `twopass-b13seat-s065` came back
    seated AND goblin -- dome, pointed near-horizontal ears, narrow almond eye,
    tiny dark pupil -- with one fault, a mauve skin inherited from a pass-one
    plate the sampler had lit as a purple twilight.
  * `tp1day-b13seat` is that plate re-rendered with the light named. Same
    skeleton, same seed, no LoRA, flat overcast daylight, and the seat held.

SO THIS JOB IS THE RECIPE END TO END, and the only thing it is still choosing is
the strength. 0.65 is the rung that already produced a seated goblin; 0.75 asks
whether one rung up sharpens his identity -- the crown cowlick and the skin were
the two soft spots -- before the seat starts to dissolve the way round seven's
ladder dissolved it. Both halves, still: HE SITS, and he is himself at 1:1
against taste/refs/goblin-canon-founder-0821.png.

  python3 pipeline/lora/emit_twopass_r2_jerry_0822.py            # dry
  python3 pipeline/lora/emit_twopass_r2_jerry_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v2-twopass2-0822"
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
OUT = "pipeline/lora/twopass-r2-jerry-0822.yaml"

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
# THE INIT IS PASS ONE'S OWN OUTPUT, ALREADY ON THE CARD in the courier's
# farm-out. It is not fetched: the bytes never left the box, and the sha below
# was read off BOTH copies (local scp and Get-FileHash on the box) before it was
# written here, so --init-sha256 is a real pin and not a restatement.
INIT_BOX = (r"C:\banyan-farm\courier-box\farm-out\lora-jerry-v2-tp1day-0822"
            r"\tp1day-b13seat.png")
INIT_SHA = "7e6b9964526be3dd7f8b16bee5a325f62a1c2157e63273fe5e94d604e36e2bb8"
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


def cell(name: str, weight, scale="1.0", strength="1.0"):
    """One render. `strength` below 1.0 is what makes this a second PASS."""
    argv = [PY_RENDER, r"%s\inpaint_fruit.py" % WORK,
            "--init", INIT_BOX,
            "--init-sha256", INIT_SHA,
            # THE MASK CARRIES NO --sha FLAG because the driver has none for it;
            # it hashes the mask itself into the sidecar. The bytes are still
            # pinned -- fetch_hints.py refuses the download on any mismatch.
            "--mask-png", r"%s\%s" % (WORK, MASK),
            # STRENGTH 1.0 AND PAD-CROP 0 ARE THE TWO HALVES OF "THIS IS
            # TXT2IMG". 1.0 runs every timestep, so the init is noised out; 0
            # turns off padding_mask_crop entirely, so diffusers crops nothing
            # and the hint is handed over at native scale (the driver's own
            # selftest: at --pad-crop 0 the magnification is exactly 1.0).
            "--strength", strength,
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
    "twopass2-b13seat-s065": (
        "THE CANDIDATE RECIPE. Pass one's RELIT seated plate as the init, "
        "all-white mask, bnyjerry at 0.8, beat 13's skeleton still attached at "
        "1.0, strength 0.65 -- the rung that already produced a seated goblin "
        "before the light was fixed. If this is clean, it is the wave's recipe."),
    "twopass2-b13seat-s075": (
        "ONE RUNG UP. 0.65 left a crown cowlick and a skin that took its colour "
        "from the init; 0.75 gives the LoRA more of the trajectory to fix both. "
        "The risk is the seat: round seven showed the standing prior reasserting "
        "itself as soon as the LoRA gets enough of the pass."),
}


def steps():
    out = [{"name": "fetch", "argv": [PY_RENDER, r"%s\fetch_hints.py" % WORK]}]
    for s in ("0.65", "0.75"):
        out.append(cell("twopass2-b13seat-s%s" % s.replace(".", ""), "0.8",
                        strength=s))
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
        "priority": 66, "max_attempts": 1, "est_minutes": 5,
        "owner": "the wave lane, 2026-08-22",
        "depends_on": TRAIN_JOB,
        "consumer": (
            "THE GOBLIN WAVE, and this is the last mechanism available to it "
            "before the answer becomes a retrain. Pass one is proven and free; "
            "this is the half that decides."),
        "success": (
            "ONE CELL WHERE HE SITS AND HE IS HIMSELF. That is the wave's "
            "recipe and it is a two-pass rather than a one-pass. If both cells "
            "come back as a seated human boy, the LoRA cannot reach through an "
            "init at any strength that preserves the pose, and the answer is a "
            "RETRAIN on posed frames -- a card-hour that needs no human -- "
            "rather than any further knob."),
        "why": (
            "ROUND SEVEN CLOSED THE ONE-PASS ROUTE: identity leaves between "
            "0.65 and 0.50 and the seated legs never arrive, because 21 of 21 "
            "training frames are standing and that is a lower-body prior no "
            "weight or scale reaches. But round six's own control cell IS a "
            "correctly seated figure -- the pose exists, it is wearing the "
            "wrong person. This asks the two questions of two passes instead "
            "of one, and the second pass is the i2i route used for the "
            "property it was CLOSED for: it re-lights and cannot re-ground."),
        "env": {
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "cell_count": {"strength_bracket": 2},
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
