#!/usr/bin/env python3
r"""ROUND SIX -- the bisection, and the one axis pass two has never been given.

ROUND FOUR PUT THE SECOND PASS'S TWO CURVES ON THE SAME PICTURE AS THE FIRST'S.
All three cells ran on b2r6-base, the only plate in this lane where he is
actually sitting, LoRA weight 0.8 throughout:

    0.75   a standing lean, and he is himself
    0.65   a standing lean, and he is himself
    0.55   HE SITS -- and he is a human boy with hair

So the seat survives below 0.65 and his face arrives at or above 0.65, which is
round seven's non-crossing curves reproduced one level up, in the pass that was
chosen precisely because it "cannot change structure". It can. Against a pose
the LoRA's 21-of-21 standing dataset disagrees with, it does.

TWO THINGS ARE STILL UNASKED, AND BOTH ARE UNDER A MINUTE.

  H  tp6-seat-i6-s060       THE BISECTION. 0.60 is the only untested rung
                            between the last seat and the first face. If the
                            curves cross anywhere they cross here, and one cell
                            settles it either way.
  I  tp6-seat-i6-s055-w10   THE AXIS PASS TWO HAS NEVER BEEN GIVEN. Every
                            second-pass cell in this lane has run the LoRA at
                            0.8. Strength and weight are not the same knob:
                            strength decides HOW MANY timesteps the LoRA gets,
                            weight decides how loud it is in each. 0.55 is the
                            rung that keeps the seat; this asks whether a
                            louder LoRA can put his face into the few steps it
                            is allowed, instead of asking for more steps and
                            losing the pose with them.
  J  tp6-seat-i6-s060-w10   the same question one rung up, so H and I are not
                            a single point each.

IF ALL THREE COME BACK AS A LEAN OR A STRANGER, the second pass is closed on the
same mechanism the first one was, and the wave's answer is a v3 trained on posed
frames -- which pass one can now generate three stances of, on wording A, with
no LoRA at all.
"""

from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v2-twopass6-0822"
TRAIN_JOB = "lora-jerry-v2-0822"
WORK = r"C:\banyan-farm\%s" % JOB
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB
LORA = r"C:\banyan-farm\%s\out\bnyjerry-sdxl-v2.safetensors" % TRAIN_JOB
LORA_SHA = "4340857d02f17dbfa50c66e0a2d8f4dc3ffebb4fad1621bb3f59242e61bfeb8b"
PY_RENDER = r"C:\banyan-farm\venv\Scripts\python.exe"
RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
OUT = "pipeline/lora/twopass-r6-jerry-0822.yaml"

TWINS = r"C:\banyan-farm\cnet-openpose-twins"

SEAT_SKEL = "jerry-skel-h240seat-0821.png"
CROUCH_SKEL = "jerry-skel-h240crouch-0821.png"
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

# ---------------------------------------------------------------- the wordings
# WORDING A is b2r6-base's, byte for byte, and round three proved it is the one
# string in this lane that lets the net drive a fold. Nothing is tidied out of
# it -- the trigger token stays even where no LoRA is loaded, because at a fixed
# seed a token is a trajectory.
W_A = ("bnyjerry, 1boy, solo, in tall grass, detailed cinematic anime, "
       "masterpiece, best quality, very aesthetic")
# ONE TAG, INSERTED WHERE THE LIGHT KEY WAS. `green skin` is the native danbooru
# tag; "sage" is an English adjective with no tag behind it. This is the whole
# variable in cell G.
W_A_GREEN = ("bnyjerry, 1boy, solo, green skin, in tall grass, detailed "
             "cinematic anime, masterpiece, best quality, very aesthetic")
W_P2 = W_A

NEG = ("lowres, worst quality, low quality, text, watermark, photorealism, "
       "3d render, blurry, 2boys, multiple heads")

PROMPTS = {
    "wA": W_A,
    "wAgreen": W_A_GREEN,
    "p2": W_P2,
}

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
    "tp6-seat-i6-s060": (
        "THE BISECTION AND NOTHING ELSE. 0.65 leaned with his face on it, 0.55 "
        "sat with a stranger's. 0.60 is the only rung between them and this is "
        "the whole cell. A pass here is the wave's first real frame; a fail "
        "closes the strength axis by exhaustion rather than by argument."),
    "tp6-seat-i6-s055-w10": (
        "LOUDER, NOT LONGER. Every pass-two cell in this lane has held the LoRA "
        "at 0.8 and moved only the strength, which conflates two knobs: "
        "strength buys the LoRA MORE TIMESTEPS -- and the early ones are "
        "exactly where global structure is decided, so buying them is what "
        "costs the seat. Weight buys it more VOICE inside the timesteps it "
        "already has. 0.55 is the rung that provably keeps the seat, so this "
        "asks for his face without asking for a single extra step."),
    "tp6-seat-i6-s060-w10": (
        "THE SAME TRADE ONE RUNG UP, so neither H nor I is a single sample of "
        "its own axis. If 0.60/1.0 sits AND is him, the recipe is a weight "
        "finding and the route doc's whole strength ladder was the wrong "
        "search direction."),
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
    out = [{"name": "fetch", "argv": [PY_RENDER, r"%s\fetch_hints.py" % WORK]}]
    out.append(cell("tp6-seat-i6-s060", "%s/%s" % (SKEL_DIR, SEAT_SKEL),
                    "p2", INIT_SEAT_BOX, INIT_SEAT_SHA, "0.60", weight="0.8"))
    out.append(cell("tp6-seat-i6-s055-w10", "%s/%s" % (SKEL_DIR, SEAT_SKEL),
                    "p2", INIT_SEAT_BOX, INIT_SEAT_SHA, "0.55", weight="1.0"))
    out.append(cell("tp6-seat-i6-s060-w10", "%s/%s" % (SKEL_DIR, SEAT_SKEL),
                    "p2", INIT_SEAT_BOX, INIT_SEAT_SHA, "0.60", weight="1.0"))
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
    for rel in ("%s/%s" % (SKEL_DIR, SEAT_SKEL),
                "%s/%s" % (SKEL_DIR, CROUCH_SKEL),
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
        "priority": 71, "max_attempts": 1, "est_minutes": 5,
        "owner": "the two-pass route lane, 2026-08-22 (round six)",
        "depends_on": TRAIN_JOB,
        "consumer": (
            "THE FRAME THE FOUNDER JUDGES. Every candidate beat-13 frame in "
            "this lane is a standing lean wearing the goblin's face; the seat "
            "exists only in a no-LoRA plate of a stranger. One of these two "
            "rungs is the frame that carries both, or there is no such frame "
            "and the wave's next step is a v3 retrain rather than a render."),
        "success": (
            "ONE RUNG WHERE HE SITS AND HE IS HIMSELF at 1:1 against "
            "taste/refs/goblin-canon-founder-0821.png. If 0.65 gives both, "
            "that is the recipe and the wave restarts on it. If 0.65 leans and "
            "0.55 sits without his face, the second pass has the same "
            "non-crossing curves the first one has and the answer is a "
            "retrain. Cell G is independent: a seat that survives a skin tag "
            "means the last open deviation is closed in pass one."),
        "why": (
            "Round three moved the two-pass verdict: at 0.75 the second pass "
            "turned a seated init into a standing lean, so it DOES reach "
            "structure against the LoRA's standing prior. The strength is "
            "therefore not settled and 0.75 is the wrong rung, not the right "
            "one. And the skin has nowhere left to be fixed except pass one, "
            "because the tag did nothing in pass two -- which is why cell G "
            "asks whether pass one can afford it."),
        "env": {
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "cell_count": {"bisection": 1, "weight_axis": 2},
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
                 "# pipeline/lora/emit_twopass_r6_jerry_0822.py, not this file.\n\n")
        yaml.safe_dump(spec, fh, sort_keys=False, width=88, allow_unicode=True)
    print("wrote %s  (%d steps)" % (OUT, len(st)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
