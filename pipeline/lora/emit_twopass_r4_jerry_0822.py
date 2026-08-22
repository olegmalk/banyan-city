#!/usr/bin/env python3
r"""ROUND FOUR -- the strength ladder on an init that is ACTUALLY a seat, and
the skin tag moved back into pass one now that the light key is banned.

WHAT ROUND THREE SETTLED, IN FOUR CELLS AND UNDER TWO MINUTES OF CARD.

  1. NAMING A LIGHT IN PASS ONE COSTS THE POSE. One variable, one control pair,
     same crouch skeleton, same seed 20260822, no LoRA in either pass:

       tp3-p1-crouch-wA        "bnyjerry, 1boy, solo, in tall grass, detailed
                                cinematic anime, ..."          -> HE CROUCHES.
       tp3-p1-crouch-wAlight   the same string + "soft overcast daylight,
                                flat even light"               -> HE STANDS.

     The same law already sat unread in the filed frames: b2r6-base (wording A)
     SITS and tp1day (wording A + the light key) STANDS AND LEANS, same seat
     skeleton, same seed. Two skeletons, one rule.

  2. SO THE THREE-STANCE FAILURE WAS NEVER ONE FINDING. crouch failed to a
     WORDING; stride and hunch fail to their own GEOMETRY -- measured off
     author_jerry_skel_0820.figure at head_frac 0.240, stride shares stand's
     span (0.867), crown-to-sole (843 px) and hip/knee/ankle fractions to three
     places and differs only by a 71 px wider x-span and one ankle raised 3%,
     while hunch differs from stand by a head dropped 0.06 of stature. Those two
     hints ASK FOR STANDING and the net drew what they asked. They are a
     re-authoring, not a re-render, and they are not in this job.

  3. AND PASS TWO AT 0.75 REACHES STRUCTURE AFTER ALL. tp3-seat-i6-s075 ran the
     filed recipe on b2r6-base -- a real seat -- and came back a standing lean
     with the goblin's face on it. So "pass two changes appearance and cannot
     change structure" is false at 0.75 against a pose the LoRA's 21-of-21
     standing dataset disagrees with. The route doc could not see this because
     its 0.75 cell was measured on tp1day, which was already a lean; preserving
     a lean proves nothing about preserving a seat.

  4. AND `green skin` IN PASS TWO DOES NOTHING TO HIM. tp3-seat-i6-s075-green
     put the tag one term into pass two's prompt and it coloured a LEAF. His
     skin stayed the same desaturated grey-brown.

THREE CELLS, ONE QUESTION EACH.

  E  tp4-seat-i6-s065   pass two at 0.65 on the seated init. Round three found
                        the ceiling; this asks where the floor is. 0.65 is the
                        rung the route doc says his face still arrives at.
  F  tp4-seat-i6-s055   one rung below the face's known departure point, so the
                        pair BRACKETS it: if 0.65 keeps the seat and the face,
                        that is the recipe; if only 0.55 keeps the seat, the
                        two curves do not cross in the second pass either and
                        the answer is a retrain on posed frames.
  G  tp4-p1-seat-wAgreen  pass one, seat skeleton, wording A plus ONE native
                        skin tag and nothing else. The light key costs a pose;
                        this asks whether every pass-one addition does, or only
                        the ones that redescribe the scene. If the seat holds
                        AND he is green, the skin is solved in the half that
                        can afford it.
"""

from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v2-twopass4-0822"
TRAIN_JOB = "lora-jerry-v2-0822"
WORK = r"C:\banyan-farm\%s" % JOB
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB
LORA = r"C:\banyan-farm\%s\out\bnyjerry-sdxl-v2.safetensors" % TRAIN_JOB
LORA_SHA = "4340857d02f17dbfa50c66e0a2d8f4dc3ffebb4fad1621bb3f59242e61bfeb8b"
PY_RENDER = r"C:\banyan-farm\venv\Scripts\python.exe"
RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
OUT = "pipeline/lora/twopass-r4-jerry-0822.yaml"

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
    "tp4-seat-i6-s065": (
        "THE LADDER, ON A REAL SEAT. Identical to tp3-seat-i6-s075 except the "
        "strength. 0.75 reached structure and turned b2r6-base's sit into a "
        "lean; 0.65 leaves the first 35% of the trajectory -- where global "
        "composition is decided -- untouched. The route doc says his face "
        "still arrives at 0.65, so this is the cell where both could be true "
        "at once."),
    "tp4-seat-i6-s055": (
        "ONE RUNG BELOW THE FACE'S KNOWN DEPARTURE. Round seven put identity's "
        "exit between 0.65 and 0.50 in a SINGLE pass; this asks the same "
        "question of the second pass, where the init is already a correct "
        "figure rather than noise. If the seat needs 0.55 and the face needs "
        "0.65, the two curves do not cross here either and the honest answer "
        "is a v3 trained on posed frames."),
    "tp4-p1-seat-wAgreen": (
        "IS EVERY PASS-ONE ADDITION POSE-FATAL, OR ONLY A SCENE ONE? The light "
        "key cost a crouch and a seat. A skin tag describes the SUBJECT rather "
        "than the frame, so it may cost nothing -- and pass two has already "
        "been shown not to carry a colour term at all. This is the only place "
        "left to spend one. No LoRA: the pose is the only thing being measured "
        "besides the hue."),
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
    out.append(cell("tp4-seat-i6-s065", "%s/%s" % (SKEL_DIR, SEAT_SKEL),
                    "p2", INIT_SEAT_BOX, INIT_SEAT_SHA, "0.65", weight="0.8"))
    out.append(cell("tp4-seat-i6-s055", "%s/%s" % (SKEL_DIR, SEAT_SKEL),
                    "p2", INIT_SEAT_BOX, INIT_SEAT_SHA, "0.55", weight="0.8"))
    out.append(cell("tp4-p1-seat-wAgreen", "%s/%s" % (SKEL_DIR, SEAT_SKEL),
                    "wAgreen", flat, flat_sha, "1.0"))
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
        "priority": 69, "max_attempts": 1, "est_minutes": 5,
        "owner": "the two-pass route lane, 2026-08-22 (round four)",
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
        "cell_count": {"strength_ladder": 2, "pass_one_skin": 1},
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
                 "# pipeline/lora/emit_twopass_r4_jerry_0822.py, not this file.\n\n")
        yaml.safe_dump(spec, fh, sort_keys=False, width=88, allow_unicode=True)
    print("wrote %s  (%d steps)" % (OUT, len(st)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
