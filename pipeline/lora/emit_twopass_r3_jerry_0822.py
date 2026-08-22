#!/usr/bin/env python3
r"""ROUND THREE OF THE TWO-PASS -- and it opens by contradicting round two's close.

WHAT THE ROUTE DOC FILED, AND WHAT THE PIXELS SAY.
  `goblin-twopass-route-0822.md` closes on two claims. Read at 1:1 against the
  frames themselves, one of them does not hold:

    * "tp1day-b13seat ... the seat held."  IT DID NOT. tp1day is a STANDING boy
      leaning forward with his forearms crossed in front of him. There is no
      seat in it: no knees up, no hips at knee height, ankles on the floor line
      under a vertical spine. It is also not lit by the flat overcast daylight
      its prompt names -- it came back a purple twilight, the exact light the
      relight was written to remove.
    * And therefore "twopass2-b13seat-s075 ... Seated" is inherited from a plate
      that was not seated. The two-pass VERDICT survives -- pass two changed
      appearance and did not change structure, which is precisely what it was
      chosen for -- but what it preserved was a lean, not a sit.

THE ONE VARIABLE BETWEEN A SEAT AND A LEAN IS THE PROMPT, and both frames are
already on disk to prove it. Same net, same blob, same scale 1.0, same all-white
mask, same strength 1.0, same seed 20260822, same `jerry-skel-h240seat-0821.png`
byte for byte:

    b2r6-b13seat-base   "bnyjerry, 1boy, solo, in tall grass, detailed
                         cinematic anime, masterpiece, best quality,
                         very aesthetic"
                        -> HE SITS. Knees up, forearms on the knees, hands
                           clasped, hips down in the grass.

    tp1day-b13seat      the same string with the trigger dropped and
                        "soft overcast daylight, flat even light" added
                        -> HE STANDS AND LEANS.

Nothing else moved. So the pass-one half is **wording-sensitive at fixed seed**,
and that confound sits underneath the route doc's other finding as well: all
three of `tp1rest`'s failing stances ran the RELIT wording and none of them has
ever been rendered on the wording that actually drove.

AND THE GEOMETRY DOES NOT SAY WHAT THE ROUTE DOC SAYS EITHER. Measured off
`author_jerry_skel_0820.figure` at head_frac 0.240, crown-to-sole as a fraction
of stature, and the knee minus hip in pixels:

    pose       span   knee-hip   what the hint actually encodes
    stand      0.867    +216.5   --
    seatspan   0.596      +9.7   knees level with the hips        DROVE
    crouch     0.535     -19.5   knees ABOVE the hips             failed
    stride     0.867    +206.8   stand, 71px wider, one ankle 3%  failed
    hunch      0.807    +216.5   stand, head down 0.06 stature    failed

`crouch` is the DEEPEST fold in the set -- deeper than the seat -- and it still
failed, which retires "the seat is the deepest fold and the rest are shallower"
as the explanation. `stride` and `hunch`, meanwhile, are not failures of the net
at all: they are hints that ASK FOR STANDING. stride shares stand's span, its
crown-to-sole, and its hip/knee/ankle fractions to three places; it differs by a
wider x-span and one ankle raised 3%. hunch differs by a head dropped a quarter
of a head height. "A standing figure with one arm out" and "standing with hands
clasped" are the CORRECT renderings of those two hints. The net drove all four.
Two of them asked for standing, and one of them was never asked in the language
that works.

SO THIS ROUND ASKS FOUR QUESTIONS, ONE CELL EACH, ABOUT 25 SECONDS EACH.

  A  tp3-p1-crouch-wA        pass one, crouch, wording A byte for byte.
                             Does the driving wording drive a fold that the
                             relit wording did not?
  B  tp3-p1-crouch-wAlight   wording A plus the light key, nothing else.
                             Isolates the light key from the trigger token.
  C  tp3-seat-i6-s075        pass two on b2r6-base -- an init that IS a seat.
                             Does the seat survive a 0.75 pass? The filed
                             s075 never tested this; its init was a lean.
  D  tp3-seat-i6-s075-green  C plus one native skin tag. The skin fault is
                             the last open deviation and the route doc puts
                             its fix in pass ONE's light, which is the half
                             that is pose-fragile. Pass two cannot change
                             structure by construction, so it is the safer
                             place to spend a colour term -- if it works.

Cells A and B are the wording control; C and D are an A/B, one term apart.
Re-authored stride and hunch hints are round FOUR and are deliberately not in
this job: they need a commit and a push before the box can fetch them by sha,
and no cell here waits on that.

  python3 pipeline/lora/emit_twopass_r3_jerry_0822.py            # dry
  python3 pipeline/lora/emit_twopass_r3_jerry_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v2-twopass3-0822"
TRAIN_JOB = "lora-jerry-v2-0822"
WORK = r"C:\banyan-farm\%s" % JOB
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB
LORA = r"C:\banyan-farm\%s\out\bnyjerry-sdxl-v2.safetensors" % TRAIN_JOB
LORA_SHA = "4340857d02f17dbfa50c66e0a2d8f4dc3ffebb4fad1621bb3f59242e61bfeb8b"
PY_RENDER = r"C:\banyan-farm\venv\Scripts\python.exe"
RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
OUT = "pipeline/lora/twopass-r3-jerry-0822.yaml"

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
# WORDING A IS b2r6-base's, BYTE FOR BYTE, INCLUDING THE TRIGGER TOKEN. With no
# LoRA loaded `bnyjerry` is an unknown token, but an unknown token is still a
# text embedding and still moves the trajectory at a fixed seed -- which is
# exactly why it stays in the control rather than being tidied out of it. Cell B
# adds the light key to THIS string and changes nothing else, so the two cells
# bracket the light key alone.
W_A = ("bnyjerry, 1boy, solo, in tall grass, detailed cinematic anime, "
       "masterpiece, best quality, very aesthetic")
W_A_LIGHT = ("bnyjerry, 1boy, solo, in tall grass, soft overcast daylight, "
             "flat even light, detailed cinematic anime, masterpiece, "
             "best quality, very aesthetic")
# PASS TWO. `green skin` is the native danbooru tag and the house dialect
# (CLAUDE.md: native-tag dialect); "sage" is an English adjective the model has
# no tag for and would be spending a term on nothing.
W_P2 = W_A
W_P2_GREEN = ("bnyjerry, 1boy, solo, green skin, in tall grass, detailed "
              "cinematic anime, masterpiece, best quality, very aesthetic")

NEG = ("lowres, worst quality, low quality, text, watermark, photorealism, "
       "3d render, blurry, 2boys, multiple heads")

PROMPTS = {
    "wA": W_A,
    "wAlight": W_A_LIGHT,
    "p2": W_P2,
    "p2green": W_P2_GREEN,
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
    "tp3-p1-crouch-wA": (
        "THE WORDING CONTROL. Pass one, no LoRA, crouch skeleton, and the "
        "EXACT string b2r6-base drove a seat with -- trigger token included. "
        "tp1rest's crouch ran the relit wording and came back upright; crouch "
        "is the deepest fold in the h240 set (span 0.535, knees 19px ABOVE the "
        "hips) so 'too shallow a departure from standing' cannot be why it "
        "failed. If this adopts, the three-stance failure is a PROMPT finding "
        "and not a geometry one, and pass one's light key is the thing that "
        "must go."),
    "tp3-p1-crouch-wAlight": (
        "THE LIGHT KEY, ALONE. Cell A's string plus 'soft overcast daylight, "
        "flat even light' and nothing else -- so A minus B is the light key "
        "and not the trigger token. If A adopts and B does not, naming a light "
        "in pass one costs a pose, which is a rule the whole wave then has to "
        "obey."),
    "tp3-seat-i6-s075": (
        "PASS TWO ON A REAL SEAT. The filed twopass2-s075 was measured on "
        "tp1day, which is a standing lean; this runs the identical recipe on "
        "b2r6-base, the one plate in the lane where he is actually sitting. "
        "The two-pass mechanism says structure cannot move at 0.75 -- so if "
        "that is true, this comes back SEATED and goblin, and the wave has its "
        "first real frame."),
    "tp3-seat-i6-s075-green": (
        "THE SKIN, SPENT IN PASS TWO INSTEAD. Cell C plus one native tag. The "
        "route doc puts the sage fix in pass one's light, but pass one is the "
        "half that loses poses to wording and its named light key did not even "
        "produce the light it named. Pass two cannot change structure by "
        "construction, which makes it the cheap place to spend a colour term. "
        "The risk is the opposite one: 'green skin' overshooting canon's "
        "desaturated sage into a saturated green."),
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
    out.append(cell("tp3-p1-crouch-wA", "%s/%s" % (SKEL_DIR, CROUCH_SKEL),
                    "wA", flat, flat_sha, "1.0"))
    out.append(cell("tp3-p1-crouch-wAlight", "%s/%s" % (SKEL_DIR, CROUCH_SKEL),
                    "wAlight", flat, flat_sha, "1.0"))
    out.append(cell("tp3-seat-i6-s075", "%s/%s" % (SKEL_DIR, SEAT_SKEL),
                    "p2", INIT_SEAT_BOX, INIT_SEAT_SHA, "0.75", weight="0.8"))
    out.append(cell("tp3-seat-i6-s075-green", "%s/%s" % (SKEL_DIR, SEAT_SKEL),
                    "p2green", INIT_SEAT_BOX, INIT_SEAT_SHA, "0.75",
                    weight="0.8"))
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
        "priority": 68, "max_attempts": 1, "est_minutes": 5,
        "owner": "the two-pass route lane, 2026-08-22",
        "depends_on": TRAIN_JOB,
        "consumer": (
            "THE GOBLIN WAVE'S POSE MECHANISM, re-opened. Beat 13's pass-two "
            "frame is the founder's next taste call and it is currently a LEAN "
            "sold as a SIT; cell C is the frame that would replace it. Cells A "
            "and B decide whether the other twenty beats are a wording fix or "
            "a hint re-authoring, which is the difference between tonight and "
            "a day of PIL work."),
        "success": (
            "C COMES BACK SEATED AND GOBLIN -- that is the wave's real first "
            "frame and the one the founder should judge. A ADOPTS THE CROUCH "
            "and B DOES NOT -- then pass one's light key is banned lane-wide "
            "and the remaining stances are a re-render, not a re-author. If A "
            "also fails, the crouch is a geometry problem after all and round "
            "four re-authors all three hints."),
        "why": (
            "The route doc's close rests on 'tp1day ... the seat held'. It did "
            "not hold: tp1day is a standing lean, so the frame filed as the "
            "wave's passing seated sample is not seated. b2r6-base IS, and the "
            "only difference between the two is the prompt at a fixed seed. "
            "Every claim downstream of that sentence has to be re-asked, and "
            "these four cells are the cheapest way to ask them."),
        "env": {
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "cell_count": {"wording_control": 2, "pass_two_ab": 2},
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
                 "# pipeline/lora/emit_twopass_r3_jerry_0822.py, not this file.\n\n")
        yaml.safe_dump(spec, fh, sort_keys=False, width=88, allow_unicode=True)
    print("wrote %s  (%d steps)" % (OUT, len(st)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
