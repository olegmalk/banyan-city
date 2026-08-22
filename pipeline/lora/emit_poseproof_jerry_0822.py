#!/usr/bin/env python3
r"""B2 ROUND FOUR: the pose bar, run on the code path where the net is PROVEN.

WHAT THIS IS AND WHY IT IS NOT ANOTHER ROUND OF THE SAME THING.
`registry.yaml`'s bnyjerry v2 entry closes B2 as VOID, not FAILED, and the
difference is a control. Round two ran the three skeletons with `--no-lora` and
the pose net drew an unrelated standing figure; round three re-ran them on the
TWINS blob -- the one weight this tree has ever made work -- and got the same
unrelated standing figure. TWO BLOBS, TWO CONTROLS, ONE OUTCOME: the fault is
`controlnet_plate.py`'s TXT2IMG path, not the weights and not the hint.

THE SAME NET DEMONSTRABLY DRIVES SOMEWHERE ELSE IN THIS TREE. Round two of the
goblin i2i route measured it moving 15.05 mean abs through `inpaint_fruit.py`,
whose ControlNet is composed INSIDE an inpaint pipeline rather than swapped in
by `AutoPipelineForText2Image.from_pipe`. The registry named the cheap fix and
this job is it, verbatim: an ALL-WHITE MASK at STRENGTH 1.0 through
`inpaint_fruit.py` IS txt2img-with-ControlNet, on the one path where the pose
net acts. Every pixel is in the mask; every timestep runs; the init is fully
noised before step one and contributes nothing. `inpaint_fruit.py` grew the same
eight-line `--lora` arm on 2026-08-22 (selftest 51/51, the filed
ep2-b08-str70-0820 sidecar still reproduced byte for byte).

TWO CELLS, AND THE SECOND ONE IS NOT OPTIONAL.
The founder's standing rule is ONE SAMPLE BEFORE ANY BATCH, and this is that
sample -- one recipe, one skeleton, beat 13's own sit. The control beside it is
not a second sample, it is the instrument check this lane has now been taught
twice: round two's 0/6 measured nothing precisely because nobody had asked what
the stack does with no LoRA in it. Three renders bought that finding then; two
buy it here.

  base  -- no LoRA. Does the SKELETON drive on this path? If this cell stands
           up straight, the fix did not work and the wave does not start.
  w08   -- bnyjerry v2 fused at 0.8, the weight B1 identity passed at. Does the
           pose survive the LoRA, and does his face survive the pose?

THE JUDGE IS THE FOUNDER'S OWN PICTURE. `taste/refs/goblin-canon-founder-0821.png`
at 1:1, and the bar is BOTH halves: pose adopts AND identity holds. Either alone
is a fail, because either alone is a beat that cannot be staged.

  python3 pipeline/lora/emit_poseproof_jerry_0822.py            # dry
  python3 pipeline/lora/emit_poseproof_jerry_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v2-b2r4-0822"
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
OUT = "pipeline/lora/poseproof-jerry-b2r4-0822.yaml"

# THE NET IS THE TWINS DIRECTORY, because that is the one round three proved is
# at least the right weight, and because it is the net `inpaint_fruit.py`'s own
# selftest exercises. Same net as round three: the ONE variable moving here is
# the code path.
TWINS = r"C:\banyan-farm\cnet-openpose-twins"

# BEAT 13'S OWN POSE. Not a synthetic test pose -- the sit skeleton is the hint
# round two drove at scale 1.0 through an img2img pass without bending a knee,
# so a pass here is directly comparable to a filed failure, and a pass is
# immediately a beat.
SKELETON = "jerry-canon-h37fsit-0821.png"
SKELETON_REL = "farm-out/jerry-canon-assets-0821/%s" % SKELETON

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
    "b2r4-sit-base": (
        "B2 ROUND FOUR, THE CONTROL. No LoRA. Does the openpose skeleton drive "
        "a composition through inpaint_fruit.py's ControlNet-inside-inpaint "
        "pipeline, where controlnet_plate.py's from_pipe txt2img path did not "
        "on either xinsir blob? A standing figure here means the fix failed and "
        "the goblin wave does not start."),
    "b2r4-sit-w08": (
        "B2 ROUND FOUR, THE BAR ITSELF. bnyjerry v2 fused at 0.8 -- the weight "
        "B1 identity passed at -- with beat 13's sit skeleton at scale 1.0. "
        "Both halves must hold: the pose adopts AND his face survives, judged "
        "at 1:1 against taste/refs/goblin-canon-founder-0821.png."),
}


def steps():
    return [
        {"name": "fetch", "argv": [PY_RENDER, r"%s\fetch_hints.py" % WORK]},
        # THE CONTROL RUNS FIRST, deliberately, and it is round two's lesson in
        # the step order: a job killed halfway should leave behind the cell that
        # tells you whether the instrument works.
        cell("b2r4-sit-base", None),
        cell("b2r4-sit-w08", SHIP_WEIGHT),
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
        "priority": 60, "max_attempts": 1, "est_minutes": 8,
        "owner": "the wave lane, 2026-08-22",
        "depends_on": TRAIN_JOB,
        "consumer": (
            "THE GOBLIN WAVE, which the founder pre-authorised ON A PASSING "
            "POSE MECHANISM. Identity already passed (B1, founder-ratified "
            "dataset). Pose is the one open half, and every goblin beat is "
            "staged with a per-beat skeleton -- so a pose net that does not "
            "drive is not a bar problem, it is the production blocker."),
        "success": (
            "TWO CELLS THAT SEPARATE. `base` must ADOPT THE SKELETON with no "
            "LoRA loaded -- that is a working instrument, and it is exactly "
            "what rounds two and three could not get out of the txt2img path. "
            "Only then does `w08` say anything, and it must hold BOTH halves: "
            "the pose adopts AND his identity survives at 1:1 against "
            "taste/refs/goblin-canon-founder-0821.png."),
        "why": (
            "B2 IS VOID, NOT FAILED. Two no-LoRA controls on two openpose blobs "
            "both drew an unrelated standing figure through "
            "controlnet_plate.py's AutoPipelineForText2Image.from_pipe path, "
            "while the same net moved 15.05 mean abs through inpaint_fruit.py. "
            "The registry named the fix rather than a debugging expedition: an "
            "all-white mask at strength 1.0 through the inpaint driver IS "
            "txt2img-with-ControlNet, on the one path where the net is proven "
            "to act. ONE VARIABLE MOVES FROM ROUND THREE: the code path."),
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
