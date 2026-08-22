#!/usr/bin/env python3
r"""B2 ROUND SIX: the mechanism passed, so now the PRODUCTION hint runs on it.

ROUND FIVE PASSED BOTH HALVES AND THE INSTRUMENT IS NO LONGER VOID.
`inpaint_fruit.py` with an all-white mask at strength 1.0 -- txt2img with a
ControlNet, on the path where the net acts -- drove `b08-openpose-nat-0819` to a
complete adoption with NO LoRA loaded: TWO full-body figures, at the skeleton's
two positions, at its two different heights, out of a `1boy, solo` prompt. The
w08 cell then held BOTH halves at once: the same two-figure composition, drawn
as two goblins whose dome, near-horizontal ears, narrow almond eye and tiny dark
pupil read correct at 1:1 against taste/refs/goblin-canon-founder-0821.png. A
LoRA and a skeleton CAN share a pass at strength 1.0, exactly as
goblin-i2i-route-0822 section 4 claimed and no run had been able to test.

SO WHAT KILLED FOUR ROUNDS WAS THE HINT'S GEOMETRY, NOT THE NET AND NOT THE PATH.
Rounds one through four all drove a `jerry-canon-h37f*-0821` skeleton: head_frac
0.370, a 2.7-head figure whose head keypoints are enormous and whose shoulder
line sits at 0.615 of stature. The renderer is not the difference -- both
families come out of the same `author_b08_openpose_hint.draw_bodypose`. The
PROPORTION is. A net trained on annotator output from photographs of people has
never seen a body shaped like that, and it contributed nothing on any path or
blob.

AND THAT DIAGNOSIS PREDICTS SOMETHING TESTABLE, WHICH IS WHAT THIS JOB IS.
The 0.370 family was authored back when the skeleton was the ONLY carrier of the
goblin's proportions -- there was no LoRA, so the hint had to make him look like
himself. That constraint is gone: bnyjerry v2 carries his identity now, and
round five proved it survives a driving skeleton. The wave's actual beat hints
are the AGE B family the founder ruled on, `jerry-skel-h240*-0821` at head_frac
0.240 -- 4.17 heads, far closer to the 5.26 of the hint that just worked and
never once tested on this recipe.

ONE SAMPLE, ONE BEAT, BEFORE ANY BATCH. Beat 13's own seat skeleton, the founder's
own age dial, on the recipe that just passed. If it adopts and he holds, the wave
has a proven per-beat mechanism and can batch. If the pose flattens at 0.240, the
proportion ceiling is somewhere between 0.190 and 0.240 and that is the next
question rather than fifteen bad plates.

  python3 pipeline/lora/emit_poseproof_r6_jerry_0822.py            # dry
  python3 pipeline/lora/emit_poseproof_r6_jerry_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v2-b2r6-0822"
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
OUT = "pipeline/lora/poseproof-jerry-b2r6-0822.yaml"

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
    "b2r6-b13seat-base": (
        "B2 ROUND SIX, THE CONTROL. No LoRA, beat 13's own AGE B seat skeleton "
        "(head_frac 0.240) on the recipe round five passed. Does a 4.17-head "
        "figure drive where a 2.7-head one contributed nothing and a 5.26-head "
        "one drove completely?"),
    "b2r6-b13seat-w08": (
        "B2 ROUND SIX, THE PRODUCTION CELL. bnyjerry v2 at 0.8 on beat 13's own "
        "hint. This is the wave's actual recipe, sampled once on one beat before "
        "any batch. Both halves must hold: he sits, and he is himself at 1:1."),
}


def steps():
    return [
        {"name": "fetch", "argv": [PY_RENDER, r"%s\fetch_hints.py" % WORK]},
        # THE CONTROL RUNS FIRST, deliberately, and it is round two's lesson in
        # the step order: a job killed halfway should leave behind the cell that
        # tells you whether the instrument works.
        cell("b2r6-b13seat-base", None),
        cell("b2r6-b13seat-w08", SHIP_WEIGHT),
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
        "priority": 62, "max_attempts": 1, "est_minutes": 8,
        "owner": "the wave lane, 2026-08-22",
        "depends_on": TRAIN_JOB,
        "consumer": (
            "THE GOBLIN WAVE, one sample before the batch. Every goblin beat is "
            "staged with one of the four AGE B skeletons; this is the first "
            "time any of them meets the recipe that works."),
        "success": (
            "BEAT 13'S OWN SKELETON DRIVES A SEATED FIGURE and bnyjerry holds "
            "at 1:1. That is a proven per-beat mechanism and the wave batches "
            "off it. A standing or bust-framed cell means the proportion "
            "ceiling sits between 0.190 and 0.240, which is the next question "
            "and is cheaper than fifteen bad plates."),
        "why": (
            "ROUND FIVE PASSED: the net drove b08-openpose-nat completely with "
            "no LoRA, and bnyjerry v2 at 0.8 then held identity ON TOP of that "
            "driven composition. The four earlier failures were the HINT's "
            "geometry -- head_frac 0.370, a 2.7-head figure no annotator ever "
            "produced -- and that shape was only ever needed because the "
            "skeleton used to be the sole carrier of his proportions. The LoRA "
            "carries them now. This tests the founder's own AGE B dial, 0.240, "
            "which is what every wave beat is actually staged with."),
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
