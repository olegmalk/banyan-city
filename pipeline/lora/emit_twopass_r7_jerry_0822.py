#!/usr/bin/env python3
r"""ROUND SEVEN -- the drive-proof for the one hint that was actually wrong.

Round five closed the stance question three ways out of four. On wording A, at
scale 1.0, with no LoRA anywhere in the pass: the seat sits, the crouch
crouches, the stride strides. The hunch came back a standing figure with its
head slightly down -- and the geometry says that is the CORRECT rendering of the
hint it was given. At head_frac 0.240 the old `hunch` differs from `stand` by a
head dropped 0.25 of its own height and shoulders rolled 0.02 in; span 0.807
against 0.867, hip, knee and ankle fractions identical to three places. The net
drew what was drawn for it.

`jerry-skel-h240hunchdeep-0822.png` is that hint re-authored as a SPINE: crown
down 141 px against 82 at the shoulders so the neck halves to 60 px, shoulders
narrowed to 172, hips down toward softened knees, arms folded in and hands low.
Span 0.721 -- between standing's 0.867 and the seat's 0.596, both measured
points on the adoption curve.

ONE CELL, ONE QUESTION, IDENTICAL IN EVERY OTHER RESPECT TO THE CELL THAT DROVE
THE CROUCH: does the re-authored hint read as a hunch?

  tp7-p1-hunchdeep-wA   pass one, no LoRA, wording A byte for byte, seed
                        20260822, scale 1.0.

The old hint is not deleted and this cell is read against round five's, which is
the same skeleton family, the same wording and the same seed -- so the pair is
the hint and nothing else. A pass makes beat 04's posture the fourth proven one
and closes the pose half of the wave. A fail says the span band is not the law
either and the next variable is named from the pair, not guessed.
"""

from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v2-twopass7-0822"
TRAIN_JOB = "lora-jerry-v2-0822"
WORK = r"C:\banyan-farm\%s" % JOB
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB
LORA = r"C:\banyan-farm\%s\out\bnyjerry-sdxl-v2.safetensors" % TRAIN_JOB
LORA_SHA = "4340857d02f17dbfa50c66e0a2d8f4dc3ffebb4fad1621bb3f59242e61bfeb8b"
PY_RENDER = r"C:\banyan-farm\venv\Scripts\python.exe"
RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
OUT = "pipeline/lora/twopass-r7-jerry-0822.yaml"

TWINS = r"C:\banyan-farm\cnet-openpose-twins"

SEAT_SKEL = "jerry-skel-h240seat-0821.png"
DEEP_SKEL = "jerry-skel-h240hunchdeep-0822.png"
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
    "tp7-p1-hunchdeep-wA": (
        "BEAT 04, THE FOOTNOTE, on a hint that finally asks for a hunch. The "
        "old skeleton was a standing figure with its head tipped down and the "
        "net rendered it faithfully twice. This one drops the crown 141 px "
        "against 82 at the shoulders, closing the neck to half the standing "
        "gap, narrows the shoulders, softens the knees and folds the arms in. "
        "Everything else -- wording, seed, scale, net, mask, strength, no LoRA "
        "-- is byte-identical to the cell that drove the crouch, so this "
        "measures the hint and nothing else."),
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
    out.append(cell("tp7-p1-hunchdeep-wA", "%s/%s" % (SKEL_DIR, DEEP_SKEL),
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
    for rel in ("%s/%s" % (SKEL_DIR, DEEP_SKEL),
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
        "priority": 72, "max_attempts": 1, "est_minutes": 5,
        "owner": "the two-pass route lane, 2026-08-22 (round seven)",
        "depends_on": TRAIN_JOB,
        "consumer": (
            "BEAT 04 OF THE GOBLIN WAVE, the last unproven posture in the AGE "
            "B set. Three of four are proven; this is the fourth."),
        "success": (
            "A FIGURE THAT READS AS FOLDED INWARD -- head sunk toward the "
            "collar, shoulders in, knees soft. Then the pose half of the wave "
            "is closed at four for four and the only thing left is the "
            "identity half, which is a taste call and a retrain. A standing "
            "figure again says span is not the law either, and the next "
            "variable gets named off the pair rather than guessed."),
        "why": (
            "Round five re-asked all three failing stances in the wording that "
            "drives and two of them adopted immediately. The hunch did not, "
            "and it is the one whose measurements predicted it would not: it "
            "is the smallest departure from standing in the set. So the hint "
            "was re-authored rather than the net re-tuned, and this is the "
            "cell that says whether that was right."),
        "env": {
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "cell_count": {"stance_drive_proof": 1},
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
                 "# pipeline/lora/emit_twopass_r7_jerry_0822.py, not this file.\n\n")
        yaml.safe_dump(spec, fh, sort_keys=False, width=88, allow_unicode=True)
    print("wrote %s  (%d steps)" % (OUT, len(st)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
