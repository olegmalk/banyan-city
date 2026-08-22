#!/usr/bin/env python3
r"""THE v3 DECISIVE LADDER: the three bars that decide whether the goblin unblocks.

WHAT THIS JOB IS FOR, IN ONE PARAGRAPH. `bnyjerry v2` draws his face and cannot
be posed by any instrument this tree owns -- words fail, an openpose weight
ladder loses his face between 0.65 and 0.50 without bending a knee at 0.35, a
two-pass keeps the seat only in the cell where he is somebody else, and an i2i
breaks the face between 0.40 and 0.45 with the pose unmoved at 0.40. v3 is v2's
twenty-one frames, byte-identical and re-asserted, plus THREE POSED FRAMES, on
the measurement that the standing prior was never 21 frames deep: only two of
the 21 show a lower body at all, and they are the canon and its mirror. This job
reads whether that one change moved the thing nothing else could.

WHY ALL THREE BARS ARE IN ONE JOB. They are not independent questions. A v3 that
poses and loses his face is not a result, it is v2's own failure mode arriving
from the other side; a v3 that keeps his face and cannot pose is v2 with three
wasted frames. The verdict is the CONJUNCTION, so the cells that decide it run
together and are read together, and a partial ladder is not a partial answer.

THE STRUCTURE, AND EVERY CELL IS HERE BECAUSE IT CAN CHANGE THE VERDICT.

  B2  POSE ADOPTION -- 3 skeletons x 2 seeds, at the identity weight.
      SEAT and KNEEL are stances v3 TRAINS ON. STRIDE IS NOT, and that is the
      whole design: a v3 that adopts the two it was shown and refuses the third
      has memorised three postures, which is a different and much weaker result
      than an unlocked pose axis -- and shots.md asks for a walking goblin in
      three of its prompt lines. Run at 0.8, the weight v2's identity passed at,
      because the claim under test is that a DATASET fix removes the need for
      the weight ladder that failed.
  B1  IDENTITY ON FRESH SETTINGS -- 5 prompts x 3 seeds.
      v2's bar, unchanged, as a NO-REGRESSION bar on the thing v2 does well. All
      three posed frames share ONE torso byte-for-byte, so if identity falls
      this is the instrument that catches the cost.
  B3  NO REGRESSION -- a no-LoRA control and the same prompt at two weights.
      Carried forward because the sapling lane failed it across three datasets
      and two caption schemes and concluded it reads on the WEIGHT, not the set.

THE RECIPE IS ROUND SEVEN'S, UNCHANGED, AND THAT IS LOAD-BEARING. Same driver,
same all-white-mask-at-strength-1.0 txt2img path, same net, same flat plates,
same steps and cfg. `controlnet_plate.py`'s txt2img path does NOT move a pose
with no LoRA loaded on either of xinsir's blobs, while this driver measurably
drives the same net -- so this is the one code path in this repo where the pose
net is proven to act, and a B2 failure here cannot be blamed on the instrument.

THE SHA IS NOT HARD-CODED AND THIS SCRIPT REFUSES WITHOUT IT. A checkpoint
directory holds five epochs with names one character apart. The emitter reads
the sha out of the published `weights-jerry-v3-0822.yaml`, so this job CANNOT be
filed before training has landed and cannot name bytes that do not exist.

  python3 pipeline/lora/emit_ladder_jerry_v3_0822.py            # dry
  python3 pipeline/lora/emit_ladder_jerry_v3_0822.py --write
  python3 pipeline/lora/emit_ladder_jerry_v3_0822.py --write --epoch 000008  # grade an intermediate
"""
from __future__ import annotations

import hashlib
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOB = "lora-jerry-v3-ladder-0822"
TRAIN_JOB = "lora-jerry-v3-0822"
WORK = r"C:\banyan-farm\%s" % JOB
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB
TRAIN_OUT = r"C:\banyan-farm\%s\out" % TRAIN_JOB
# The `--output_name` train-jerry-v3-0822.yaml passes to sd-scripts. The final
# checkpoint is exactly this plus `.safetensors`, with no epoch suffix.
OUTPUT_NAME = "bnyjerry-sdxl-v3"
WEIGHTS_YAML = "farm-out/%s/weights-jerry-v3-0822.yaml" % TRAIN_JOB
PY_RENDER = r"C:\banyan-farm\venv\Scripts\python.exe"
RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
OUT = "pipeline/lora/ladder-jerry-v3-0822.yaml"

TWINS = r"C:\banyan-farm\cnet-openpose-twins"

# ── B2's THREE SKELETONS, at the founder's own age dial (head_frac 0.240).
#
# `in_dataset` is not decoration: it is the axis the bar reads. Two cells the set
# was shown and one it was not, so "the pose axis opened" and "the trigger
# memorised three postures" produce DIFFERENT ladders and can be told apart.
SKELETONS = {
    "seat": ("jerry-skel-h240seat-0821.png", True,
             "v3 TRAINS ON A SEATED FRAME (posed-seat, cropped at 1088). This "
             "is also the skeleton rounds one through three drove at scale 1.0 "
             "through an img2img pass without bending a knee, and the one the "
             "v2 LoRA overrode at 0.8 -- so this cell has a filed failure to "
             "be compared against rather than a fresh baseline."),
    "kneel": ("jerry-skel-h240kneel-0822.png", True,
              "v3 TRAINS ON A KNEELING FRAME (posed-kneel, uncropped). "
              "Authored for this ladder because the AGE B set had seat, "
              "stride, crouch and hunch and no kneel, and the bar naming kneel "
              "was committed before the training frames were admitted."),
    "stride": ("jerry-skel-h240stride-0821.png", False,
               "**NOT IN THE DATASET, DELIBERATELY.** The single most "
               "informative cell in this job. Seat and kneel passing tells us "
               "the frames took; only stride tells us whether the POSE AXIS "
               "opened. shots.md asks for a goblin walking away and stopping "
               "mid-step in three of its prompt lines, so this is also the "
               "cell a beat is actually waiting on."),
}
SKEL_DIR = "farm-out/jerry-skel-assets-0820"

# The flat plates that turn this driver into txt2img. See
# pipeline/author_jerry_poseproof_0822.py.
INIT = "jerry-poseproof-init-0822.png"
MASK = "jerry-poseproof-maskall-0822.png"
ASSET_DIR = "farm-out/jerry-poseproof-assets-0822"

W, H = 832, 1216
SHIP_WEIGHT = "0.8"
B2_SEEDS = ("20260822", "20260901")

# B2's PROMPT IS ROUND ONE'S, BYTE FOR BYTE. It carries the trigger and NO POSE
# WORD -- the pose is the skeleton's job, which is the entire experiment, and a
# pose word would make a passing cell unattributable between the net and the
# wording. That matters more in v3 than it did in v2: v3 is the first set in
# which the pose token varies in pixels, so a pose word in this prompt could
# now genuinely do work and would contaminate the reading.
B2_PROMPT = ("bnyjerry, 1boy, solo, in tall grass, detailed cinematic anime, "
             "masterpiece, best quality, very aesthetic")
NEG = ("lowres, worst quality, low quality, text, watermark, photorealism, "
       "3d render, blurry, 2boys, multiple heads")

# ── B1's FIVE FRESH PROMPTS. Fresh means a setting, a light AND a framing that
# no admitted frame carries. The dataset's grounds are `a hazy meadow` and `tall
# grass`; its lights are eleven daylight variants; none of the five below is in
# either list. Caption-shaped on purpose: the LoRA was trained on that shape and
# a bar that changes the shape measures two things.
B1_PROMPTS = {
    "wall": "a grey stone wall behind, flat overcast light",
    "night": "a snowy blue night, cold moonlight",
    "beach": "a sunset beach, warm backlight",
    "indoor": "a dim wooden interior, single lamp light",
    "desert": "a cracked desert flat, harsh noon light",
}
B1_FRAMING = "upper body"
B1_SEEDS = ("20260822", "20260901", "20261006")

# ── B3's PROMPT CARRIES NO TRIGGER AND NO GOBLIN. If a goblin shows up, the
# LoRA is leaking into every frame the show renders, which is a shipping stop
# regardless of what B1 and B2 say.
B3_PROMPT = ("1girl, solo, standing in a wheat field, straw hat, warm evening "
             "light, detailed cinematic anime, masterpiece, best quality, "
             "very aesthetic")
B3_WEIGHTS = ("0.8", "0.65")
B3_SEED = "20260822"

FETCH_PY = '''#!/usr/bin/env python3
"""Fetch the three skeletons and the two flat plates, each pinned by sha256.

The skeletons are the SAME BYTES the earlier rounds drove, which is what makes a
v3 cell comparable to a filed v2 failure instead of merely adjacent to it."""
import hashlib, os, sys, urllib.request

OUT = r"%s"
UA = {"User-Agent": "banyan-city-v3ladder/1.0 (albert.numbro@gmail.com)"}
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
found = sorted(glob.glob(OUT + "/*.png")) + sorted(
    glob.glob(OUT + "/*.png.meta.yaml"))
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
    raise SystemExit("NOTHING TO PUBLISH -- the ladder produced no files")
'''


def sha_of(rel: str) -> str:
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def resolve_lora(epoch: str):
    """The checkpoint's box path and sha256, READ from the published manifest.

    REFUSING IS THE FEATURE. Round seven hard-coded a sha, which is correct once
    the weights exist and is a lie before they do. This job is derived from a
    training run that may not have finished, so the emitter reads the sha the
    PUBLISH step wrote and stops if it is not there -- which makes "the ladder
    cannot be filed against weights that do not exist" a property of the tool
    rather than a thing the operator remembers.
    """
    p = os.path.join(REPO, WEIGHTS_YAML)
    if not os.path.isfile(p):
        raise SystemExit(
            "!! %s is not on disk, so v3's weights have not landed yet.\n"
            "   This ladder names a checkpoint by sha256 and will not invent "
            "one.\n"
            "   Wait for %s to finish and for the courier to publish, then:\n"
            "     git pull && python3 %s --write"
            % (WEIGHTS_YAML, TRAIN_JOB,
               "pipeline/lora/emit_ladder_jerry_v3_0822.py"))
    doc = yaml.safe_load(open(p, encoding="utf-8"))
    ck = doc.get("checkpoints") or doc
    names = sorted(k for k in ck if str(k).endswith(".safetensors"))
    if not names:
        raise SystemExit("!! %s names no .safetensors checkpoint" % WEIGHTS_YAML)
    if epoch:
        hit = [n for n in names if epoch in n]
        if not hit:
            raise SystemExit(
                "!! no checkpoint matching %r. sd-scripts names the "
                "intermediates `<output_name>-NNNNNN.safetensors` (six digits, "
                "the EPOCH number), so --epoch 000008 selects epoch 8. have:\n"
                "   %s" % (epoch, "\n   ".join(names)))
        name = hit[0]
    else:
        # THE FINAL CHECKPOINT IS THE ONE WITH NO SUFFIX, AND SORTING FOR IT IS
        # A TRAP. sd-scripts writes `bnyjerry-sdxl-v3.safetensors` for the last
        # epoch and `bnyjerry-sdxl-v3-000002.safetensors` for each
        # `save_every_n_epochs` rung, so the unsuffixed final sorts FIRST and
        # `names[-1]` picks epoch 8 while calling it final. That is exactly the
        # "five checkpoints one character apart" hazard --lora-sha256 exists
        # for, arriving one layer up where the sha guard would not catch it
        # (the sha would match -- the wrong checkpoint's).
        final = "%s.safetensors" % OUTPUT_NAME
        if final not in ck:
            raise SystemExit(
                "!! %s is not in %s. Training may have been interrupted before "
                "the final save; pass --epoch <NNNNNN> to grade an "
                "intermediate. have:\n   %s"
                % (final, WEIGHTS_YAML, "\n   ".join(names)))
        name = final
    row = ck[name]
    return (row.get("box_path") or r"%s\%s" % (TRAIN_OUT, name),
            row["sha256"], name)


def cell(name, *, lora, lora_sha, weight, prompt_file, skeleton=None,
         seed="20260822", note=""):
    """One render on the round-seven txt2img path. `weight` None = no LoRA."""
    argv = [PY_RENDER, r"%s\inpaint_fruit.py" % WORK,
            "--init", r"%s\%s" % (WORK, INIT),
            "--init-sha256", sha_of("%s/%s" % (ASSET_DIR, INIT)),
            "--mask-png", r"%s\%s" % (WORK, MASK),
            # STRENGTH 1.0 AND PAD-CROP 0 ARE THE TWO HALVES OF "THIS IS
            # TXT2IMG": 1.0 noises the init out entirely, 0 turns off
            # padding_mask_crop so diffusers crops nothing and any hint reaches
            # the net at exactly the scale it was authored (magnification 1.0,
            # asserted by the driver's own guard).
            "--strength", "1.0", "--pad-crop", "0",
            # BLUR 0: a blurred all-white mask is still all white, but a knob at
            # a non-zero value in a control experiment is a variable nobody
            # named.
            "--blur", "0"]
    if skeleton:
        argv += ["--controlnet", TWINS,
                 "--control", r"%s\%s" % (WORK, skeleton),
                 "--control-sha256", sha_of("%s/%s" % (SKEL_DIR, skeleton)),
                 "--scale", "1.0"]
    argv += ["--prompt-file", r"%s\%s" % (WORK, prompt_file),
             "--negative-file", r"%s\negative.txt" % WORK,
             "--steps", "40", "--cfg", "7.5", "--seed", seed,
             "--out", r"%s\out\%s.png" % (WORK, name)]
    if weight is not None:
        argv += ["--lora", lora, "--lora-weight", weight,
                 "--lora-sha256", lora_sha]
    argv += ["--note", note]
    return {"name": name, "argv": argv}


def build_steps(lora, lora_sha, ckpt):
    st = [{"name": "fetch", "argv": [PY_RENDER, r"%s\fetch_hints.py" % WORK]}]

    # ── B2 FIRST, AND THE ORDER IS THE POINT. If the job dies halfway, the half
    # worth having is the one no prior attempt has ever produced. B1 and B3
    # re-measure things v2 already answered; B2 is the question.
    for stance, (png, in_set, why) in SKELETONS.items():
        for i, seed in enumerate(B2_SEEDS):
            st.append(cell(
                "b2-%s-s%d" % (stance, i + 1), lora=lora, lora_sha=lora_sha,
                weight=SHIP_WEIGHT, prompt_file="prompt-b2.txt",
                skeleton=png, seed=seed,
                note=("B2, %s skeleton at conditioning scale 1.0, LoRA %s at "
                      "weight %s, seed %s. IN THE v3 DATASET: %s. %s The "
                      "prompt carries the trigger and NO POSE WORD -- the pose "
                      "is the skeleton's job and a pose word would make a "
                      "passing cell unattributable between the net and the "
                      "wording."
                      % (stance, ckpt, SHIP_WEIGHT, seed,
                         "yes" if in_set else "NO", why))))

    # ── B1, five fresh settings x three seeds.
    for tag, setting in B1_PROMPTS.items():
        for i, seed in enumerate(B1_SEEDS):
            st.append(cell(
                "b1-%s-s%d" % (tag, i + 1), lora=lora, lora_sha=lora_sha,
                weight=SHIP_WEIGHT, prompt_file="prompt-b1-%s.txt" % tag,
                seed=seed,
                note=("B1 IDENTITY ON A FRESH SETTING: %s, %s framing, seed "
                      "%s, LoRA %s at %s, NO skeleton. Fresh means a setting, "
                      "a light and a framing no admitted frame carries -- the "
                      "dataset's only grounds are `a hazy meadow` and `tall "
                      "grass`. This is v2's bar re-run unchanged, as a "
                      "no-regression bar on the axis v2 already passes: all "
                      "three added frames share ONE torso byte-for-byte, so if "
                      "identity fell, it fell here."
                      % (setting, B1_FRAMING, seed, ckpt, SHIP_WEIGHT))))

    # ── B3, the control first so a dead job still has something to compare to.
    st.append(cell("b3-noLoRA", lora=lora, lora_sha=lora_sha, weight=None,
                   prompt_file="prompt-b3.txt", seed=B3_SEED,
                   note=("B3 CONTROL: the identical prompt and seed with NO "
                         "LoRA LOADED. This is the twin every B3 cell is read "
                         "against, so it renders first -- a half-finished job "
                         "with the control in it is still a comparison.")))
    for w in B3_WEIGHTS:
        st.append(cell("b3-w%s" % w.replace(".", ""), lora=lora,
                       lora_sha=lora_sha, weight=w,
                       prompt_file="prompt-b3.txt", seed=B3_SEED,
                       note=("B3 NO REGRESSION at weight %s. The prompt "
                             "carries NO TRIGGER and NO GOBLIN. BAR: no goblin "
                             "intrudes and the frame is not visibly "
                             "recoloured, reframed or restyled against "
                             "b3-noLoRA. Measured at two weights because the "
                             "sapling lane failed this bar on three datasets "
                             "and two caption schemes and concluded it reads "
                             "on the WEIGHT rather than on the set." % w)))

    st.append({"name": "publish", "argv": [PY_RENDER, "-c", PUB_PY % (
        WORK.replace("\\", "/") + "/out", FARMOUT.replace("\\", "/"), JOB)]})
    return st


def payloads() -> dict:
    pay = {r"%s\inpaint_fruit.py" % WORK: open(
        os.path.join(REPO, "pipeline/inpaint_fruit.py"), encoding="utf-8").read()}
    pay[r"%s\prompt-b2.txt" % WORK] = B2_PROMPT
    pay[r"%s\prompt-b3.txt" % WORK] = B3_PROMPT
    for tag, setting in B1_PROMPTS.items():
        pay[r"%s\prompt-b1-%s.txt" % (WORK, tag)] = (
            "bnyjerry, 1boy, solo, standing, looking at viewer, %s, %s, anime "
            "style, cel shading, masterpiece, best quality, very aesthetic"
            % (B1_FRAMING, setting))
    pay[r"%s\negative.txt" % WORK] = NEG
    # THE PNGs ARE FETCHED, NOT PAYLOADED -- payloads are text, and every image
    # this tree sends to the card is pinned by sha256 and refused on mismatch.
    lines = []
    rels = ["%s/%s" % (SKEL_DIR, v[0]) for v in SKELETONS.values()]
    rels += ["%s/%s" % (ASSET_DIR, INIT), "%s/%s" % (ASSET_DIR, MASK)]
    for rel in rels:
        lines.append('    "%s": ("%s%s", "%s"),'
                     % (os.path.basename(rel), RAW, rel, sha_of(rel)))
    pay[r"%s\fetch_hints.py" % WORK] = FETCH_PY % (WORK, chr(10).join(lines))
    return pay


def main() -> int:
    write = "--write" in sys.argv
    epoch = ""
    for i, a in enumerate(sys.argv):
        if a == "--epoch" and i + 1 < len(sys.argv):
            epoch = sys.argv[i + 1]
    lora, lora_sha, ckpt = resolve_lora(epoch)
    st = build_steps(lora, lora_sha, ckpt)
    n_render = sum(1 for s in st if s["name"] not in ("fetch", "publish"))

    spec = {
        "id": JOB, "task": JOB, "node": "002b-first-citizen",
        "runner": "box", "needs_gpu": True, "needs": ["cuda", "vram20"],
        "priority": 62, "max_attempts": 1,
        "est_minutes": max(8, int(n_render * 0.8) + 3),
        "owner": "the goblin v3 lane, 2026-08-22",
        "depends_on": TRAIN_JOB,
        "consumer": (
            "THE FOUNDER'S OWN OPEN QUESTION at /review/ep2-goblin-twopass-0822 "
            "-- whether this character can be posed at all -- and every goblin "
            "beat in episodes two and three behind it. This is the job that "
            "answers the page."),
        "success": (
            "A JUDGED CONJUNCTION, NOT A SCORE. B2 >= 5 of 6 on pose adoption "
            "AND >= 5 of 6 on identity, B1 >= 13 of 15, B3 clean at a weight "
            "B1 and B2 also pass at. A run that fails B2 and says so, with the "
            "in-dataset and out-of-dataset stances read separately, is a "
            "success: it closes the last candidate on the board. A run that "
            "reports a pose without reading the face is not."),
        "why": (
            "EVERY INSTRUMENT THIS TREE OWNS HAS FAILED B2 ON THIS CHARACTER, "
            "so the bar has a measured control at zero and this is the only "
            "candidate left. v3's bet is that the failure was never a placement "
            "problem: the standing prior is ONE FRAME DEEP -- of the 21 "
            "ratified frames, 11 are upper-body crops and 8 are cowboy shots, "
            "and the only two showing a lower body are the canon and its "
            "mirror -- so every knob was hunting for a competing configuration "
            "to fade toward and there was none in the weights.\n\n"
            "THE STRIDE CELL IS WHY THIS LADDER IS WORTH A CARD-HOUR RATHER "
            "THAN A CONFIRMATION. Seat and kneel are stances v3 trains on; "
            "stride is not. A pass on all three says the pose AXIS opened. A "
            "pass on seat and kneel with stride refused says the trigger "
            "memorised three postures, which is a real and much weaker result, "
            "and it is one the beats care about -- shots.md asks for a walking "
            "goblin in three prompt lines."),
        "env": {
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "checkpoint": ckpt,
        "checkpoint_sha256": lora_sha,
        "cell_count": {"B2_pose": len(SKELETONS) * len(B2_SEEDS),
                       "B1_identity": len(B1_PROMPTS) * len(B1_SEEDS),
                       "B3_regression": 1 + len(B3_WEIGHTS)},
        "recipe_is_round_sevens": (
            "UNCHANGED, AND THAT IS LOAD-BEARING. Same driver, same "
            "all-white-mask-at-strength-1.0 txt2img path, same net (the twins "
            "directory), same flat plates, same 40 steps and cfg 7.5. "
            "controlnet_plate.py's txt2img path does NOT move a pose with no "
            "LoRA loaded on either of xinsir's blobs, while this driver "
            "measurably drives the same net -- so it is the one code path in "
            "this repo where the pose net is proven to act, and a B2 failure "
            "here cannot be blamed on the instrument."),
        "payload": payloads(),
        "steps": st,
        "artifacts": [r"%s\%s.sha256" % (FARMOUT, JOB)],
    }

    if not write:
        print("would emit %s" % OUT)
        print("  checkpoint %s  sha %s" % (ckpt, lora_sha[:16]))
        print("  %d render cell(s): B2 %d, B1 %d, B3 %d"
              % (n_render, len(SKELETONS) * len(B2_SEEDS),
                 len(B1_PROMPTS) * len(B1_SEEDS), 1 + len(B3_WEIGHTS)))
        for s in st:
            print("   %s" % s["name"])
        print("\n-- dry run. re-run with --write.")
        return 0

    with open(os.path.join(REPO, OUT), "w", encoding="utf-8") as fh:
        fh.write("# THE v3 DECISIVE LADDER -- B2 pose adoption, B1 identity on\n"
                 "# fresh settings, B3 no-regression, in one job because the\n"
                 "# verdict is their CONJUNCTION.\n"
                 "# GENERATED. Edit pipeline/lora/emit_ladder_jerry_v3_0822.py,\n"
                 "# not this file.\n\n")
        yaml.safe_dump(spec, fh, sort_keys=False, width=88, allow_unicode=True)
    print("wrote %s  (%d render cells, checkpoint %s)" % (OUT, n_render, ckpt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
