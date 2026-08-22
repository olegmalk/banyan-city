#!/usr/bin/env python3
r"""THE JERRY v2 BAR GRID: 29 cells that answer the five pre-registered bars.

THE BARS WERE COMMITTED BEFORE THE DATASET EXISTED -- `emit_train_jerry_v2_0822.BARS`,
in git since before a single frame was admitted. This file does not restate them
and cannot relax them; it renders the cells they call for.

WHY B2 IS FIRST IN THE STEP LIST EVEN THOUGH IT IS SECOND IN THE BARS. B2 is the
only bar whose answer changes what the show can do. `goblin-i2i-route-0822.md`
section 4 claims a LoRA and a skeleton can both act at strength 1.0 because no
init competes with them, and that claim is the entire reason this LoRA was
trained -- the img2img route already re-lights him and provably cannot re-pose
him. If B2 passes, every goblin beat in episodes two and three unlocks. If B2
fails, the goblin has no route to a new body position at all and that is the
finding the founder needs. It runs first so that a job killed halfway still
answers the question that matters.

THE B2 CELLS ARE THE FIRST THING IN THIS TREE TO PUT A LoRA AND A POSE NET IN ONE
PASS. `controlnet_plate.py` grew a `--lora` arm on 2026-08-22 for exactly this;
before it, `sample_lora.py` took no hint and `controlnet_plate.py` took no LoRA,
so the claim was untestable. The skeletons are the ones already authored at
head_frac 0.370 -- the proportion measured off the founder's own image -- and are
the SAME hints round two drove at scale 1.0 when it scored 0 of 3 on pose
adoption. That zero is B2's control: same net, same scale, same skeletons, and
the only difference is that his identity now arrives as trained weights instead
of as an init competing with them.

  python3 pipeline/lora/emit_bars_jerry_v2_0822.py            # dry
  python3 pipeline/lora/emit_bars_jerry_v2_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v2-bars-0822"
TRAIN_JOB = "lora-jerry-v2-0822"
WORK = r"C:\banyan-farm\%s" % JOB
TRAIN_OUT = r"C:\banyan-farm\%s\out" % TRAIN_JOB
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB
LORA = r"%s\bnyjerry-sdxl-v2.safetensors" % TRAIN_OUT
PY_RENDER = r"C:\banyan-farm\venv\Scripts\python.exe"
RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
OUT = "pipeline/lora/bars-jerry-v2-0822.yaml"

JOB2 = "lora-jerry-v2-b2r2-0822"
WORK2 = r"C:\banyan-farm\%s" % JOB2
FARMOUT2 = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB2
OUT2 = "pipeline/lora/bars-jerry-v2-b2r2-0822.yaml"
PUB2 = '''
import hashlib, glob, os, shutil
OUT = "%s"
DST = "%s"
os.makedirs(DST, exist_ok=True)
n = 0
found = sorted(glob.glob(OUT + "/*.png")) + sorted(glob.glob(OUT + "/*.png.meta.yaml"))
for p in found:
    if os.path.isfile(p):
        shutil.copyfile(p, os.path.join(DST, os.path.basename(p)))
        n += 1
with open(os.path.join(DST, "%s.sha256"), "w", encoding="utf-8") as fh:
    for name in sorted(os.listdir(DST)):
        q = os.path.join(DST, name)
        if os.path.isfile(q) and not name.endswith(".sha256"):
            fh.write("%%s  %%s" %% (hashlib.sha256(open(q, "rb").read()).hexdigest(), name) + chr(10))
print("published", n, "file(s) ->", DST, flush=True)
if n == 0:
    raise SystemExit("NOTHING TO PUBLISH")
''' % (WORK2.replace("\\", "/") + "/out", FARMOUT2.replace("\\", "/"), JOB2)

SHIP_WEIGHT = "0.8"          # the ladder below is what decides the real one
SEEDS = ("20260822", "20260823", "20260824")

NEG = ("lowres, worst quality, low quality, text, watermark, photorealism, "
       "3d render, blurry, 2boys, multiple heads")

# ── B1 / B4 / B5. FIVE PROMPTS THE DATASET DOES NOT CONTAIN.
#
# "Fresh" is enforced rather than asserted: every admitted frame in
# `manifest-jerry-v2-0822.yaml` carries the setting `a hazy meadow` (or `tall
# grass` on the two canon frames) and the light is one of eleven daylight keys.
# None of these five is either. THREE OF THE FIVE ALSO NAME A POSE THE SET NEVER
# SHOWS -- every training frame is a standing figure, because the route that made
# them cannot move a pose -- and those three are B5, the caption design's own bar.
#
# id -> (prompt tail after the trigger, is this a B5 pose cell)
B1_PROMPTS = {
    "p1": ("1boy, solo, sitting, full body, on a wooden bench in a stone "
           "cellar, warm lamplight, anime style, cel shading", True),
    "p2": ("1boy, solo, crouching, full body, on a snowy path, cold blue "
           "light, anime style, cel shading", True),
    "p3": ("1boy, solo, walking, full body, along a cobbled street at night, "
           "lantern light, anime style, cel shading", True),
    "p4": ("1boy, solo, standing, upper body, in a dim workshop, single "
           "candle, anime style, cel shading", False),
    "p5": ("1boy, solo, standing, full body, on a beach at sunset, orange "
           "backlight, anime style, cel shading", False),
}

# ── B2. THE DECISIVE BAR. skeleton -> why this one.
#
# All three are `jerry_canon_0821` hints at head_frac 0.370, published in
# farm-out/jerry-canon-assets-0821/ and fetched by sha like any other asset.
B2_SKELETONS = {
    "sit": ("jerry-canon-h37fsit-0821.png",
            "BEAT 13'S OWN POSE, and the exact hint round two drove at scale "
            "1.0 through an img2img pass. It did not bend a knee. This cell is "
            "that experiment with the init removed and the identity moved into "
            "the weights, which is the whole hypothesis in one frame."),
    "crouch": ("jerry-canon-h37fcrouch-0821.png",
               "A deep fold -- both knees and the hips -- so P1 is unmissable. "
               "A pose that only half adopts is readable here and is not on a "
               "gentler skeleton."),
    "stride": ("jerry-canon-h37fstride-0821.png",
               "Asymmetric limbs. The dataset is 9 mirrored frames out of 21 "
               "and a set that taught a handedness would show it on a stride "
               "before it showed it anywhere else."),
}

# ── B3. NO REGRESSION. A prompt with NO trigger and NO goblin in it.
B3_PROMPT = ("a stone bridge over a river, green hills behind, soft daylight, "
             "anime style, cel shading, detailed background, masterpiece, "
             "best quality, very aesthetic")
B3_ARMS = (("base", None), ("w80", "0.8"), ("w50", "0.5"))

# ── THE WEIGHT LADDER. The sapling ladder measured two curves that NEVER CROSS
# -- contamination fading smoothly as the weight drops while the subject
# collapsed below 0.65 -- and the usable band was read off it rather than
# assumed. Same instrument, same five rungs, one seed, one prompt.
LADDER = ("0.8", "0.65", "0.5", "0.35", "0.2")


# ── B2 ROUND TWO, AND ITS CONTROL. Added after B2 scored 0 of 6 on P1.
#
# ALL SIX CELLS CAME BACK STANDING, BUST-FRAMED AND SATURATED, with a full-body
# skeleton at conditioning scale 1.0 and the LoRA fused at 0.8. Two readings fit
# that and they demand opposite actions, so neither is asserted:
#
#   A. THE LoRA OVERRIDES THE NET. 19 of the 21 training frames are cowboy or
#      upper-body crops -- the framing monoculture the pupil finding FORCED,
#      since no full-body frame could be rendered without a coloured iris. A
#      trigger that learned "bust" would fight a full-body skeleton, and at 0.8
#      it would win.
#   B. THE NET IS NOT REACHING THE DENOISER IN THIS STACK. The sidecar says
#      scale 1.0 and names the net, but a sidecar records what was ASKED.
#
# THE CONTROL SEPARATES THEM IN ONE RENDER. `--no-lora` on the identical stack:
# if the pose adopts with no LoRA loaded, the net works and reading A is right;
# if it does not, the net was never driving and B2's zero says nothing about the
# LoRA at all. Running the weight rungs without this control would have been the
# lane measuring a knob whose instrument it had not checked.
B2R2_WEIGHTS = ("0.5", "0.35", None)   # None = the no-LoRA control


def steps_b2r2():
    out = [{"name": "fetch",
            "argv": [PY_RENDER, r"%s\fetch_hints.py" % WORK2]}]
    for w in B2R2_WEIGHTS:
        tag = "base" if w is None else "w" + w.replace(".", "")
        for name in sorted(B2_SKELETONS):
            hint = B2_SKELETONS[name][0]
            argv = [PY_RENDER, r"%s\controlnet_plate.py" % WORK2,
                    "--task", "b2r2-%s-%s" % (name, tag),
                    "--arm", "hint",
                    "--controlnet", "xinsir/controlnet-openpose-sdxl-1.0",
                    "--control", r"%s\%s" % (WORK2, hint),
                    "--scale", "1.0",
                    "--prompt-file", r"%s\b2-prompt.txt" % WORK2,
                    "--negative-file", r"%s\negative.txt" % WORK2,
                    "--width", "832", "--height", "1216",
                    "--seed", "20260822",
                    "--out", r"%s\out" % WORK2]
            if w is not None:
                argv[2:2] = []
                argv += ["--lora", LORA, "--lora-weight", w]
            out.append({"name": "b2r2-%s-%s" % (name, tag), "argv": argv})
    out.append({"name": "publish", "argv": [PY_RENDER, "-c", PUB2]})
    return out


def steps():
    out = []

    # ---- B2 FIRST. See the module docstring.
    for name, (hint, _why) in B2_SKELETONS.items():
        for i, seed in enumerate(SEEDS[:2]):
            out.append({
                "name": "b2-%s-s%d" % (name, i + 1),
                "argv": [PY_RENDER, r"%s\controlnet_plate.py" % WORK,
                         "--task", "b2-%s-s%d" % (name, i + 1),
                         "--arm", "hint",
                         "--controlnet", "xinsir/controlnet-openpose-sdxl-1.0",
                         "--control", r"%s\%s" % (WORK, hint),
                         "--scale", "1.0",
                         "--lora", LORA, "--lora-weight", SHIP_WEIGHT,
                         "--prompt-file", r"%s\b2-prompt.txt" % WORK,
                         "--negative-file", r"%s\negative.txt" % WORK,
                         "--width", "832", "--height", "1216",
                         "--seed", seed,
                         "--out", r"%s\out" % WORK],
            })

    # ---- B1 / B4 / B5.
    for pid in sorted(B1_PROMPTS):
        tail, _pose = B1_PROMPTS[pid]
        for i, seed in enumerate(SEEDS):
            out.append({
                "name": "b1-%s-s%d" % (pid, i + 1),
                "argv": [PY_RENDER, r"%s\sample_lora.py" % WORK,
                         "--lora", LORA, "--lora-weight", SHIP_WEIGHT,
                         "--prompt", "bnyjerry, " + tail +
                         ", masterpiece, best quality, very aesthetic",
                         "--negative", NEG,
                         "--width", "832", "--height", "1216",
                         "--steps", "40", "--guidance", "7.5", "--seed", seed,
                         "--out", r"%s\out\B1-%s-s%d.png" % (WORK, pid, i + 1)],
            })

    # ---- B3.
    for arm, w in B3_ARMS:
        argv = [PY_RENDER, r"%s\sample_lora.py" % WORK,
                "--lora", LORA,
                "--prompt", B3_PROMPT,
                "--negative", "1boy, goblin, people, text, watermark, blurry",
                "--width", "832", "--height", "1216",
                "--steps", "40", "--guidance", "7.5", "--seed", "20260822",
                "--out", r"%s\out\B3-%s.png" % (WORK, arm)]
        if w is None:
            argv.append("--no-lora")
        else:
            argv[argv.index("--lora") + 2:argv.index("--lora") + 2] = \
                ["--lora-weight", w]
        out.append({"name": "b3-%s" % arm, "argv": argv})

    # ---- THE LADDER.
    tail, _ = B1_PROMPTS["p4"]
    for w in LADDER:
        out.append({
            "name": "ladder-w%s" % w.replace(".", ""),
            "argv": [PY_RENDER, r"%s\sample_lora.py" % WORK,
                     "--lora", LORA, "--lora-weight", w,
                     "--prompt", "bnyjerry, " + tail +
                     ", masterpiece, best quality, very aesthetic",
                     "--negative", NEG,
                     "--width", "832", "--height", "1216",
                     "--steps", "40", "--guidance", "7.5", "--seed", "20260822",
                     "--out", r"%s\out\LADDER-w%s.png" % (WORK, w.replace(".", ""))],
        })

    # ---- PUBLISH. The courier pushes from farm-out and nowhere else.
    out.append({
        "name": "publish",
        "argv": [PY_RENDER, "-c", r"""
import hashlib, glob, os, shutil
# FORWARD SLASHES AND A PLAIN `name = "literal"`, BOTH FOR THE SAME NON-HUMAN
# READER. box_enqueue's arm guard resolves publish globs statically so it can
# check that every --arm step's picture is claimed by something; it matches
# `name = "literal"` (no r-prefix), it resolves `VAR + "/pattern"` (not
# os.path.join), and it normalises forward slashes itself. Written any other way
# the guard cannot see the patterns, reports the B2 pictures as unclaimed, and
# refuses the job -- which is the guard working correctly on a spec that was
# talking past it. Windows takes forward slashes in every path API used here.
OUT = "%s"
DST = "%s"
os.makedirs(DST, exist_ok=True)
# THE GLOB IS `*.png` AND NOT `*`, AND THAT IS FOR A READER RATHER THAN FOR
# CORRECTNESS. box_enqueue's arm guard scans publish globs for the picture each
# --arm step will write, and it only inspects patterns whose basename mentions
# .png -- a bare `*` names nothing it can check, so the guard reports the B2
# cells as unclaimed and refuses the job. Spelling the extension is how the
# guard is satisfied honestly, rather than by adding a path that lies.
# THE GLOB CALLS ARE LITERAL, ONE PER PATTERN, AND THAT IS FOR A READER THAT IS
# NOT HUMAN. box_enqueue's arm guard parses this source for glob() calls and
# resolves their arguments statically, so it can check that every --arm step's
# picture is actually claimed by something. A pattern held in a LOOP VARIABLE is
# unresolvable, the guard leaves it alone rather than guessing, and the B2 cells
# then read as unclaimed -- which is how eight good ep2-b04-tileread renders
# exited rc=1 on 2026-08-21 with the pictures already on the card. Spelling each
# pattern out is what lets the guard do its job instead of being talked past.
n = 0
found = []
found += sorted(glob.glob(OUT + "/*.png"))
found += sorted(glob.glob(OUT + "/*.png.meta.yaml"))
found += sorted(glob.glob(OUT + "/*.txt"))
for p in found:
    if os.path.isfile(p):
        shutil.copyfile(p, os.path.join(DST, os.path.basename(p)))
        n += 1
with open(os.path.join(DST, "%s.sha256"), "w", encoding="utf-8") as fh:
    for name in sorted(os.listdir(DST)):
        q = os.path.join(DST, name)
        if os.path.isfile(q) and not name.endswith(".sha256"):
            fh.write("%%s  %%s\n" %% (
                hashlib.sha256(open(q, "rb").read()).hexdigest(), name))
print("published", n, "file(s) ->", DST, flush=True)
if n == 0:
    raise SystemExit("NOTHING TO PUBLISH -- the grid produced no files")
""" % (WORK.replace("\\", "/") + "/out",
       FARMOUT.replace("\\", "/"), JOB)],
    })
    return out


FETCH_PY = '''#!/usr/bin/env python3
"""Fetch the three authored OpenPose skeletons, each by sha256.

They are `jerry_canon_0821` hints at head_frac 0.370 -- the proportion measured
off the founder's own image -- and are the SAME hints round two drove at scale
1.0 when it scored zero on pose adoption. Using the identical bytes is what
makes B2 comparable to that control."""
import hashlib, os, sys, urllib.request

OUT = r"%s"
UA = {"User-Agent": "banyan-city-jerrybars/1.0 (albert.numbro@gmail.com)"}
WANT = {
%s
}

os.makedirs(OUT, exist_ok=True)
for name, (url, want) in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %%s -- refusing." + chr(10) +
                 "   want %%s" %% want + chr(10) + "   have %%s" %% have)
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %%s %%d bytes OK" %% (name, len(raw)), flush=True)
'''


def payloads():
    """Scripts and prompts written to the box at enqueue time.

    THE DRIVERS TRAVEL AS SOURCE, which is this tree's standing pattern: a job
    carries the exact script bytes it ran, so a verdict months later is
    reproducible even after the repo moves on. `controlnet_plate.py` is the copy
    that grew the `--lora` arm on 2026-08-22; `sample_lora.py` is unchanged.
    """
    pay = {}
    pay[r"%s\controlnet_plate.py" % WORK] = open(
        os.path.join(REPO, "pipeline/controlnet_plate.py"), encoding="utf-8").read()
    pay[r"%s\sample_lora.py" % WORK] = open(
        os.path.join(REPO, "pipeline/lora/sample_lora.py"), encoding="utf-8").read()

    # THE B2 POSITIVE CARRIES THE TRIGGER AND NO POSE WORD. The pose is the
    # SKELETON's job here -- that is the entire experiment -- and a pose word in
    # the prompt would make a passing cell unattributable between the net and
    # the wording. It carries no face term either: route_closure_2026_08_22
    # forbids one, and his face is the LoRA's job now.
    pay[r"%s\b2-prompt.txt" % WORK] = (
        "bnyjerry, 1boy, solo, in tall grass, detailed cinematic anime, "
        "masterpiece, best quality, very aesthetic")
    pay[r"%s\negative.txt" % WORK] = NEG

    # THE SKELETONS ARE FETCHED, NOT PAYLOADED -- they are PNGs, and every asset
    # this tree sends to the card is pinned by sha256 and refused on mismatch.
    lines = []
    for _n, (hint, _w) in sorted(B2_SKELETONS.items()):
        rel = "farm-out/jerry-canon-assets-0821/%s" % hint
        sha = hashlib.sha256(
            open(os.path.join(REPO, rel), "rb").read()).hexdigest()
        lines.append('    "%s": ("%s%s", "%s"),' % (hint, RAW, rel, sha))
    pay[r"%s\fetch_hints.py" % WORK] = FETCH_PY % (WORK, chr(10).join(lines))
    return pay


def main() -> int:
    import yaml
    write = "--write" in sys.argv
    st = steps()
    st.insert(0, {"name": "fetch",
                  "argv": [PY_RENDER, r"%s\fetch_hints.py" % WORK]})

    spec = {
        "id": JOB, "task": JOB, "node": "002b-first-citizen",
        "runner": "box", "needs_gpu": True, "needs": ["cuda", "vram20"],
        "priority": 58, "max_attempts": 1,
        "est_minutes": 40,
        "owner": "the goblin-LoRA lane, 2026-08-22",
        "depends_on": TRAIN_JOB,
        "consumer": (
            "THE FOUNDER, through the ship page, and the ep2/ep3 plate step "
            "behind it. B2 is the cell that decides whether the goblin can be "
            "put in a new body position at all."),
        "success": (
            "A JUDGED ANSWER, NOT A PASSING ONE. 29 frames that let every "
            "pre-registered bar be scored at 1:1, including the two -- B2 and "
            "B3 -- whose failure modes are written down in advance."),
        "why": (
            "The bars in `emit_train_jerry_v2_0822.BARS` were committed to git "
            "before a single training frame was admitted. This job renders the "
            "cells they call for and changes none of them.\n\n"
            "B2 RUNS FIRST because it is the only bar whose answer changes what "
            "the show can do, and a job killed halfway should still answer it."),
        "env": {
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "cell_count": {"B2_pose_adoption": 6, "B1_B4_B5_identity": 15,
                       "B3_no_regression": 3, "weight_ladder": 5},
        "payload": payloads(),
        "steps": st,
        # EVERY OUTPUT IS NAMED, NOT GLOBBED. box_enqueue refuses a step whose
        # picture no artifacts entry mentions, and it is right to: on 2026-08-21
        # eight good ep2-b04-tileread renders exited rc=1 with the pictures
        # already sitting on the card, because nothing downstream claimed them.
        # controlnet_plate writes `<task>-<arm>.png`, so the B2 cells land as
        # `b2-<pose>-s<n>-hint.png` and each one is listed.
        # THE B2 PICTURES ARE CLAIMED BY THE PUBLISH GLOB, NOT BY THIS LIST,
        # AND THE TWO GUARDS ARE WHY. `controlnet_plate` derives its output name
        # from --task and --arm, so the string `b2-sit-s1-hint.png` appears in no
        # argv anywhere -- and box_enqueue refuses a declared artifact that no
        # step names, correctly, because an artifacts list carried over from
        # another spec makes the runner's missing-artifact check meaningless.
        # The arm guard is satisfied instead by the publish step's literal
        # `OUT + "/*.png"`, which is the mechanism it exists to look for. Every
        # file that travels is still hashed into the .sha256 below.
        "artifacts": (
            [r"%s\B1-%s-s%d.png" % (FARMOUT, pid, i + 1)
               for pid in sorted(B1_PROMPTS) for i in range(len(SEEDS))]
            + [r"%s\B3-%s.png" % (FARMOUT, arm) for arm, _w in B3_ARMS]
            + [r"%s\LADDER-w%s.png" % (FARMOUT, w.replace(".", ""))
               for w in LADDER]
            + [r"%s\%s.sha256" % (FARMOUT, JOB)]),
    }

    if not write:
        print("would emit %s with %d step(s)" % (OUT, len(st)))
        for s in st:
            print("   %s" % s["name"])
        return 0
    with open(os.path.join(REPO, OUT), "w", encoding="utf-8") as fh:
        fh.write("# THE JERRY v2 BAR GRID -- GENERATED. Edit\n"
                 "# pipeline/lora/emit_bars_jerry_v2_0822.py, not this file.\n"
                 "#\n# The bars themselves live in\n"
                 "# pipeline/lora/emit_train_jerry_v2_0822.py `BARS`, committed\n"
                 "# before any training frame was admitted.\n\n")
        yaml.safe_dump(spec, fh, sort_keys=False, width=88, allow_unicode=True)
    print("wrote %s  (%d steps)" % (OUT, len(st)))

    # ---- B2 ROUND TWO, ITS OWN JOB so the first grid's verdicts stay filed
    # against the spec that produced them.
    st2 = steps_b2r2()
    pay2 = {k.replace(WORK, WORK2): v for k, v in payloads().items()}
    spec2 = dict(spec)
    spec2.update({
        "id": JOB2, "task": JOB2, "priority": 57, "est_minutes": 12,
        "depends_on": TRAIN_JOB,
        "consumer": (
            "THE B2 VERDICT ITSELF. Round one scored 0 of 6 on pose adoption "
            "and two readings fit that result -- the LoRA overriding the net, "
            "or the net not reaching the denoiser. This job's `base` arm is the "
            "control that separates them, and without it the zero is "
            "uninterpretable."),
        "success": (
            "A SEPARATION, not a pass. If the three `base` cells adopt their "
            "skeletons, the net works and B2's zero is the LoRA; if they do "
            "not, B2 measured nothing about the LoRA and the grid's decisive "
            "bar is void until the stack is fixed."),
        "why": (
            "B2 IS THE ONLY BAR WHOSE ANSWER CHANGES WHAT THE SHOW CAN DO, and "
            "round one's zero is currently unattributable. The control costs "
            "three renders and is the difference between a finding and a guess."),
        "payload": pay2,
        "steps": st2,
        "artifacts": [r"%s\%s.sha256" % (FARMOUT2, JOB2)],
        "cell_count": {"B2_at_w050": 3, "B2_at_w035": 3, "B2_no_lora_control": 3},
    })
    with open(os.path.join(REPO, OUT2), "w", encoding="utf-8") as fh:
        fh.write("# B2 ROUND TWO + ITS NO-LoRA CONTROL -- GENERATED. Edit\n"
                 "# pipeline/lora/emit_bars_jerry_v2_0822.py, not this file.\n\n")
        yaml.safe_dump(spec2, fh, sort_keys=False, width=88, allow_unicode=True)
    print("wrote %s  (%d steps)" % (OUT2, len(st2)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
