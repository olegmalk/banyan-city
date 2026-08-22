#!/usr/bin/env python3
r"""ROUND FIVE -- the other two stances, asked in the language that works.

ROUND THREE PROVED THE WORDING IS THE VARIABLE. Same crouch skeleton, same seed,
no LoRA: wording A crouched, wording A plus "soft overcast daylight, flat even
light" stood up. And the same pair was already sitting in the filed frames --
b2r6-base (wording A) sits, tp1day (wording A + the light key) leans.

`tp1rest` rendered stride and hunch on the RELIT wording only. Neither has ever
been asked in wording A, and the route doc's conclusion -- that they are
geometry failures needing re-authored hints -- was drawn from cells that share
the crouch's confound exactly.

RE-AUTHORING A HINT IS AN AFTERNOON OF PIL AND A NEW SHA IN EVERY DOWNSTREAM
JOB. RE-ASKING ONE IS FIFTY SECONDS. So the cheap question goes first, and the
geometry case only gets made if these two fail on the wording that works:

  tp5-p1-stride-wA   beat 02, THE SPRINT.
  tp5-p1-hunch-wA    beat 04, THE FOOTNOTE.

Both pass one, no LoRA, wording A byte for byte, seed 20260822, scale 1.0 --
identical in every respect to the cell that drove the crouch except the hint.
That makes the four h240 stances one comparable set for the first time.

WHAT THE GEOMETRY SAYS THEY SHOULD DO, so the verdict can be checked against a
prediction rather than written after the fact. Measured off
author_jerry_skel_0820.figure at head_frac 0.240:

    pose       span   knee-hip   x-span   distance from `stand`
    stand      0.867    +216.5    250.3   --
    seatspan   0.596      +9.7    250.3   large        DROVE (wording A)
    crouch     0.535     -19.5    274.1   largest      DROVE (wording A)
    stride     0.867    +206.8    321.8   small
    hunch      0.807    +216.5    214.5   smallest

stride keeps stand's span and crown-to-sole exactly -- its planted foot never
leaves the authored ground line -- and differs by a 71 px wider x-span, a lifted
right ankle and a swung left arm. hunch differs by a head dropped a quarter of
its own height and shoulders rolled 0.02 of stature in and down. If the wording
was the whole story these two adopt too. If they come back as clean standing
figures on wording A, the hints are genuinely under-authored and round six
re-authors them -- with a prediction on record either way.
"""

from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v2-twopass5-0822"
TRAIN_JOB = "lora-jerry-v2-0822"
WORK = r"C:\banyan-farm\%s" % JOB
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB
LORA = r"C:\banyan-farm\%s\out\bnyjerry-sdxl-v2.safetensors" % TRAIN_JOB
LORA_SHA = "4340857d02f17dbfa50c66e0a2d8f4dc3ffebb4fad1621bb3f59242e61bfeb8b"
PY_RENDER = r"C:\banyan-farm\venv\Scripts\python.exe"
RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
OUT = "pipeline/lora/twopass-r5-jerry-0822.yaml"

TWINS = r"C:\banyan-farm\cnet-openpose-twins"

SEAT_SKEL = "jerry-skel-h240seat-0821.png"
STRIDE_SKEL = "jerry-skel-h240stride-0821.png"
HUNCH_SKEL = "jerry-skel-h240hunch-0821.png"
SKEL_DIR = "farm-out/jerry-skel-assets-0820"

# PASS ONE'S INIT: the flat grey plate, fully noised at strength 1.0 and
# carrying nothing. PASS TWO'S INIT: round six's own base cell, which is the
# ONLY frame in this lane that is actually seated. Its sha was read off the
# published farm-out copy on the branch AND recomputed from the local extract
# before it was written here, so --init-sha256 is a real pin.
INIT_FLAT = "jerry-poseproof-init-0822.png"
MASK = "jerry-poseproof-maskall-0822.png"
ASSET_DIR = "farm-out/jerry-poseproof-assets-0822"
INIT_SEAT_BOX = (r"C:\banyan-farm\courier-box\farm-out\lora-jerry-v2-b2r6-0822"
                 r"\b2r6-b13seat-base.png")
INIT_SEAT_SHA = "5f7d41a616edf80744d9961a573dafc59a003944272b65a535c01aecd415acef"

SEED = "20260822"

# ---------------------------------------------------------------- the wording
# ONE STRING, b2r6-base's, byte for byte. The trigger token stays even with no
# LoRA loaded: at a fixed seed an unknown token is still a trajectory, and
# tidying it out would make these cells incomparable to the one that drove.
W_A = ("bnyjerry, 1boy, solo, in tall grass, detailed cinematic anime, "
       "masterpiece, best quality, very aesthetic")

NEG = ("lowres, worst quality, low quality, text, watermark, photorealism, "
       "3d render, blurry, 2boys, multiple heads")

PROMPTS = {"wA": W_A}

FETCH_PY = '''#!/usr/bin/env python3
"""Fetch every hint and plate this job drives, each pinned by sha256."""
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

NOTES = {
    "tp5-p1-stride-wA": (
        "BEAT 02, THE SPRINT, re-asked. tp1rest drove this hint on the relit "
        "wording and got a standing figure with one arm out. The hint is the "
        "narrowest departure from `stand` in the set by span -- it holds the "
        "planted foot on the authored ground line by design -- so it is the "
        "one most likely to be a genuine geometry failure. Prediction on "
        "record: if the crouch's wording finding generalises, the lifted right "
        "ankle and the swung left arm show up here; if it does not, this comes "
        "back upright and the hint needs re-authoring."),
    "tp5-p1-hunch-wA": (
        "BEAT 04, THE FOOTNOTE, re-asked. hunch differs from `stand` by a head "
        "dropped 0.25 of its own height and shoulders rolled in -- the "
        "smallest x-span in the set. tp1rest's cell came back 'standing with "
        "hands clasped', which is arguably the correct rendering of that hint. "
        "Wording A is the last cheap thing to try before the spine gets "
        "re-authored with a real forward curve."),
}


def sha_of(rel: str) -> str:
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def cell(name, skel_rel, prompt_key, init_box, init_sha, strength, weight=None):
    skel = os.path.basename(skel_rel)
    argv = [PY_RENDER, r"%s\inpaint_fruit.py" % WORK,
            "--init", init_box,
            "--init-sha256", init_sha,
            "--mask-png", r"%s\%s" % (WORK, MASK),
            "--strength", strength,
            "--pad-crop", "0",
            "--blur", "0",
            "--controlnet", TWINS,
            "--control", r"%s\%s" % (WORK, skel),
            "--control-sha256", sha_of(skel_rel),
            "--scale", "1.0",
            "--prompt-file", r"%s\prompt-%s.txt" % (WORK, prompt_key),
            "--negative-file", r"%s\negative.txt" % WORK,
            "--steps", "40", "--cfg", "7.5", "--seed", SEED,
            "--out", r"%s\out\%s.png" % (WORK, name)]
    if weight is not None:
        argv += ["--lora", LORA, "--lora-weight", weight,
                 "--lora-sha256", LORA_SHA]
    argv += ["--note", NOTES[name]]
    return {"name": name, "argv": argv}


def steps():
    flat = r"%s\%s" % (WORK, INIT_FLAT)
    flat_sha = sha_of("%s/%s" % (ASSET_DIR, INIT_FLAT))
    out = [{"name": "fetch", "argv": [PY_RENDER, r"%s\fetch_hints.py" % WORK]}]
    out.append(cell("tp5-p1-stride-wA", "%s/%s" % (SKEL_DIR, STRIDE_SKEL),
                    "wA", flat, flat_sha, "1.0"))
    out.append(cell("tp5-p1-hunch-wA", "%s/%s" % (SKEL_DIR, HUNCH_SKEL),
                    "wA", flat, flat_sha, "1.0"))
    out.append({"name": "publish", "argv": [PY_RENDER, "-c", PUB_PY % (
        WORK.replace("\\", "/") + "/out", FARMOUT.replace("\\", "/"), JOB)]})
    return out


def payloads() -> dict:
    pay = {}
    pay[r"%s\inpaint_fruit.py" % WORK] = open(
        os.path.join(REPO, "pipeline/inpaint_fruit.py"), encoding="utf-8").read()
    for key, text in PROMPTS.items():
        pay[r"%s\prompt-%s.txt" % (WORK, key)] = text
    pay[r"%s\negative.txt" % WORK] = NEG
    lines = []
    for rel in ("%s/%s" % (SKEL_DIR, STRIDE_SKEL),
                "%s/%s" % (SKEL_DIR, HUNCH_SKEL),
                "%s/%s" % (ASSET_DIR, INIT_FLAT),
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
        "priority": 70, "max_attempts": 1, "est_minutes": 5,
        "owner": "the two-pass route lane, 2026-08-22 (round five)",
        "depends_on": TRAIN_JOB,
        "consumer": (
            "BEATS 02 AND 04 OF THE GOBLIN WAVE. Neither can be staged until "
            "its posture is proven, and the difference between a wording fix "
            "and a hint re-authoring is fifty seconds against an afternoon."),
        "success": (
            "EITHER STANCE ADOPTS -- then the wording finding generalises past "
            "the crouch and the whole h240 family is a re-render. BOTH COME "
            "BACK UPRIGHT -- then stride and hunch are genuinely under-authored "
            "hints, which the measurements predict, and round six re-authors "
            "them with a real knee lift and a real spine curve. Both outcomes "
            "are a result; neither needs a knob."),
        "why": (
            "The route doc concluded that three of four stances are a geometry "
            "problem. Round three showed one of the three was a WORDING "
            "problem, and all three cells shared the same relit prompt. The "
            "conclusion therefore rests on a confound, and these two cells "
            "remove it for the price of a minute of card."),
        "env": {
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "cell_count": {"stance_drive_proof": 2},
        "payload": payloads(),
        "steps": st,
        "artifacts": [r"%s\%s.sha256" % (FARMOUT, JOB)],
    }
    if not write:
        print("would emit %s with %d step(s)" % (OUT, len(st)))
        for s in st:
            print("   %s" % s["name"])
        return 0
    with open(os.path.join(REPO, OUT), "w", encoding="utf-8") as fh:
        fh.write("# TWO-PASS ROUND THREE -- the wording control and pass two on\n"
                 "# an init that is actually a seat. GENERATED. Edit\n"
                 "# pipeline/lora/emit_twopass_r5_jerry_0822.py, not this file.\n\n")
        yaml.safe_dump(spec, fh, sort_keys=False, width=88, allow_unicode=True)
    print("wrote %s  (%d steps)" % (OUT, len(st)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
