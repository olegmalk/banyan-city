#!/usr/bin/env python3
r"""TRAIN-JERRY-V2: the job spec, its numbers derived from the manifest.

WHY A GENERATOR AND NOT A HAND-WRITTEN YAML. The repeat count, the image-pass
count and the optimizer-step count all fall out of ONE number -- how many frames
survived judging -- and that number is not knowable when the bars are written.
Hand-writing the spec would mean either guessing the frame count before the
renders (and quietly keeping the guess when reality differed) or writing the
bars after seeing the frames. Both are the failure this tree keeps naming. So:

  * THE BARS ARE IN THIS FILE AND THIS FILE IS COMMITTED BEFORE ANY FRAME IS
    ADMITTED. They are pre-registered in the only sense that means anything --
    git has them, with a timestamp, before the thing they judge exists.
  * THE NUMBERS ARE READ FROM `manifest-jerry-v2-0822.yaml` at emit time, so the
    spec cannot claim a dataset it does not have.

  python3 pipeline/lora/emit_train_jerry_v2_0822.py            # dry
  python3 pipeline/lora/emit_train_jerry_v2_0822.py --write
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

MANIFEST = "pipeline/lora/manifest-jerry-v2-0822.yaml"
BASE_SNAPSHOT = (r"C:\Users\artvn\.cache\huggingface\hub"
                 r"\models--cagliostrolab--animagine-xl-3.1\snapshots"
                 r"\483f0c322568ed13697ed01dd0be07204746d12b")

# THE STAGE STEP, AS A STRING SO THE SPEC CARRIES IT VERBATIM.
#
# TWO ROOTS AND THE TRANSFERRED TREE IS TRIED FIRST. The box's repo checkout is
# hundreds of commits behind and does not contain this dataset at all; the
# frames, captions and manifest are moved directly (tar, scp, sha verified end
# to end). Pinning to the verified tree also means a `git pull` landing
# mid-flight cannot change the dataset under a running job. The checkout stays
# as a second candidate so this keeps working once the box is current, and
# NOTHING IS TRUSTED BECAUSE OF HOW IT ARRIVED -- every frame is verified
# byte-for-byte below either way. The step prints which root it used.
STAGE_PY = r"""
import hashlib, os, shutil, yaml
CANDIDATES = [r"%(work)s\src", r"C:\banyan-farm\banyan-city"]
REL = "%(manifest)s"
repo = next((c for c in CANDIDATES if os.path.exists(os.path.join(c, REL))), None)
if repo is None:
    raise SystemExit("NO DATASET ROOT. Tried:\n  " + "\n  ".join(CANDIDATES))
print("dataset root:", repo, flush=True)
man = yaml.safe_load(open(os.path.join(repo, REL), encoding="utf-8"))
if man.get("trigger") != "%(trigger)s":
    raise SystemExit("manifest trigger is %%r, not %(trigger)s" %% man.get("trigger"))
dst = r"%(work)s\img\%(repeat)d_%(trigger)s"
os.makedirs(dst, exist_ok=True)
os.makedirs(r"%(work)s\out", exist_ok=True)
os.makedirs(r"%(work)s\log", exist_ok=True)
n = 0
for fr in man["frames"]:
    src = os.path.join(repo, fr["image"])
    if not os.path.isfile(src):
        raise SystemExit("MISSING FRAME: " + fr["image"])
    have = hashlib.sha256(open(src, "rb").read()).hexdigest()
    if have != fr["sha256"]:
        raise SystemExit("SHA MISMATCH for %%s\n  want %%s\n  have %%s"
                         %% (fr["image"], fr["sha256"], have))
    cap = os.path.join(repo, fr["caption_file"])
    if not os.path.isfile(cap):
        raise SystemExit("MISSING CAPTION: " + fr["caption_file"])
    base = fr["cell"]
    shutil.copyfile(src, os.path.join(dst, base + ".png"))
    shutil.copyfile(cap, os.path.join(dst, base + ".txt"))
    n += 1
print("staged %%d image+caption pairs, all sha256 verified" %% n, flush=True)
if n != man["count"]:
    raise SystemExit("staged %%d but the manifest says %%d" %% (n, man["count"]))
"""
OUT = "pipeline/lora/train-jerry-v2-0822.yaml"
JOB = "lora-jerry-v2-0822"
WORK = r"C:\banyan-farm\%s" % JOB
TRIGGER = "bnyjerry"
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB

# THE PUBLISH STEP. Copies what may travel; hashes what may not.
PUBLISH_PY = r"""
import hashlib, glob, os, shutil, yaml
OUT = r"%(work)s\out"
DST = r"%(farmout)s"
os.makedirs(DST, exist_ok=True)

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

# 1. THE SAMPLE TRAVELS.
published = []
for png in sorted(glob.glob(os.path.join(OUT, "SAMPLE-*.png"))):
    shutil.copyfile(png, os.path.join(DST, os.path.basename(png)))
    published.append(os.path.basename(png))
    print("published", os.path.basename(png), flush=True)

# 2. THE WEIGHTS DO NOT. Their hashes and box paths do, which is the half that
#    makes provenance survive the blob staying on one machine.
ck = {}
for w in sorted(glob.glob(os.path.join(OUT, "*.safetensors"))):
    b = os.path.basename(w)
    ck[b] = {"sha256": sha(w), "bytes": os.path.getsize(w), "box_path": w}
    print("hashed", b, ck[b]["sha256"][:16], flush=True)
if not ck:
    raise SystemExit("NO CHECKPOINTS in %%s -- training produced nothing" %% OUT)

doc = {"job": "%(job)s", "trigger": "%(trigger)s",
       "weights_stay_on_the_box": (
           "Each checkpoint is ~228 MB. GitHub rejects blobs over 100 MiB and "
           "the courier does `git add -A -- farm-out`, so a checkpoint here "
           "would leave a permanently unpushable commit and block every lane. "
           "The sha256s below are the durable half."),
       "checkpoints": ck, "samples": published}
with open(os.path.join(DST, "weights-jerry-v2-0822.yaml"), "w",
          encoding="utf-8") as fh:
    yaml.safe_dump(doc, fh, sort_keys=False, width=88)

# 3. A .sha256 BESIDE EVERYTHING THAT TRAVELLED.
with open(os.path.join(DST, "%(job)s.sha256"), "w", encoding="utf-8") as fh:
    for n in sorted(os.listdir(DST)):
        q = os.path.join(DST, n)
        if os.path.isfile(q) and not n.endswith(".sha256"):
            fh.write("%%s  %%s\n" %% (sha(q), n))
print("publish complete ->", DST, flush=True)
"""

# ══════════════════════════════════════════════════════════════════════════
# BARS — pre-registered, written before a single training frame was admitted.
#
# THE RULERS ARE NOT NEW AND NOT THIS LANE'S. E1-E5 are the founder's own image
# read at 1:1, verbatim from `derive_goblin_i2i_0822.BAR`, which is the bar round
# one and round two were already judged on. Nothing below was invented to be
# passed.
#
# ── WHY THE BAR SET IS NOT THE SAPLING'S. The sapling LoRA is judged on whether
# it draws an OBJECT correctly. This one is judged on whether it makes a FACE
# survive into a pass that a POSE NET is also driving, because that -- and
# nothing else -- is the reason it is being trained. Section 4 of
# `goblin-i2i-route-0822.md` states the claim this whole run exists to test:
#
#   > a LoRA and a skeleton can both act at strength 1.0 because there is no
#   > init competing with them
#
# B2 IS THAT SENTENCE AS A MEASUREMENT. Every other bar here is a way for B2 to
# be wrong for a boring reason -- the identity did not train (B1), the style
# broke (B4), the token eats every prompt it touches (B3). If B2 passes, every
# goblin beat in episode two and three unlocks at once; if B2 fails with B1
# passing, the LoRA is a re-lighting tool with extra steps and the goblin has no
# route to a new body position at all. That second outcome is written down here,
# before the run, so it cannot be softened afterwards.
BARS = """\
B1  IDENTITY, 15 CELLS, JUDGED AT 1:1 AGAINST taste/refs/goblin-canon-founder-0821.png
    FIVE fresh prompts the dataset does not contain, at THREE seeds each. Fresh
    means: a setting, a light and a framing no admitted frame carries. A cell
    passes when E1-E4 all hold (E5 where costume is in frame):
      E1 narrow almond eye, off-white field, TINY dark pupil, heavy upper lid.
         A large round iris of any colour is a FAIL -- this is the axis four
         founder vetoes were spent on.
      E2 broad low dome; smallish pointed ears NEAR HORIZONTAL. A tall egg skull
         with large upswept ears is the vetoed design.
      E3 smooth face -- no brow furrows, no nasolabial folds, no jowls.
      E4 desaturated sage, washed and high-key. Saturated kelly green is the
         vetoed palette.
      E5 shirt with a placket, dark shorts, dark boots.
    BAR: >= 13 of 15.
    JUDGED BY A BLIND COLD READER -- a fresh agent handed one frame, his image
    and the E-clauses, no prompt text, no mention of this lane, one frame at a
    time at full resolution. Same instrument the sapling runs used.

B2  POSE ADOPTION -- THE DECISIVE BAR, AND THE REASON THIS LoRA EXISTS
    `bnyjerry` + an OpenPose skeleton at conditioning scale 1.0, TXT2IMG, no
    init, LoRA at the shipping weight. THREE authored skeletons (the seated,
    the crouch and the stride from jerry_canon_0821, at head_frac 0.370 -- the
    proportion measured off the founder's own image) x TWO seeds = 6 cells.
    Each cell is read on two clauses:
      P1 DID THE BODY ADOPT THE SKELETON? A visible knee bend, hip drop or
         seated fold where the hint has one. Round two's img2img cells scored
         0/3 here with the identical net at the identical scale, so this clause
         has a measured control at zero.
      P2 DID THE IDENTITY SURVIVE IT? E1-E4, same reading as B1.
    BAR: >= 5 of 6 on P1 AND >= 5 of 6 on P2. A cell that adopts the pose and
    loses the face is a FAIL, and so is the reverse -- the whole claim is that
    both happen in one pass.

B3  NO REGRESSION, AT TWO WEIGHTS
    An A/B pair -- identical prompt and seed, LoRA loaded and unloaded -- on a
    prompt carrying NO trigger and NO goblin, at weight 0.8 and again at the
    shipping weight if that differs. BAR: no goblin intrudes, and the frame is
    not visibly recoloured, reframed or restyled against its no-LoRA twin.
    REGISTRY NOTE, CARRIED FORWARD DELIBERATELY: the sapling lane failed this
    bar in v1, v2 and v2b -- three datasets, two caption schemes, one outcome --
    and concluded "B3 should stop being treated as a dataset bar; the next thing
    to test against it is the WEIGHT and the merge." It is therefore measured at
    two weights here rather than one, and a failure at 0.8 with a pass lower
    down is a WEIGHT finding, not a dataset verdict.

B4  STYLE, THE CONTROL
    The 15 B1 frames read for our look -- detailed cinematic anime, native-tag
    dialect. BAR: 15 of 15. A character LoRA that drags the show's style with it
    is not shippable at any identity score. This bar passed 15/15 in all three
    sapling runs and is here to catch the case where it stops.

B5  NO POSE LOCK -- THE CAPTION DESIGN'S OWN BAR
    Every training frame in this set is a STANDING figure, because the route
    that made them cannot move a pose. The caption scheme's answer is to name
    `standing`, `looking at viewer` and a framing word on all of them, so the
    trigger is excused from carrying any of the three. THIS BAR TESTS WHETHER
    THAT WORKED. Of the 15 B1 cells, several prompt for a pose the dataset never
    shows (sitting, crouching, walking). BAR: <= 2 of 15 return a standing
    figure when another pose was asked for.
    B5 AND B2 ARE THE SAME QUESTION FROM TWO SIDES and are both here on purpose:
    B5 asks whether WORDS can move him, B2 asks whether a SKELETON can. B2 is
    the one that matters for production -- the beats are staged with skeletons --
    but a B5 failure with a B2 pass would say the trigger fused the pose and the
    net is overriding it, which is a different and more fragile thing to ship.

EPOCHS. Judged on the five saved checkpoints, not just the last. Picking the
epoch is part of the job and overfitting past the sweet spot is the standard
character-LoRA failure; the sapling v1 lane closed the epoch axis for its own
fusion defect by grading epoch 6 on the identical grid, and that is the cheap
insurance being bought again here.

WEIGHT. No weight is sanctioned in advance. The sapling ladder measured that its
subject COLLAPSED below 0.65 while contamination faded smoothly -- two curves
that never cross -- and the usable band was read off that ladder rather than
assumed. The same ladder runs here (0.8 / 0.65 / 0.5 / 0.35 / 0.2, both sides,
one seed) and the shipping weight comes out of it or does not exist.
"""


def main() -> int:
    import yaml
    write = "--write" in sys.argv
    mp = os.path.join(REPO, MANIFEST)
    if not os.path.isfile(mp):
        print("!! %s does not exist yet.\n"
              "   The bars in this file are committed and the numbers are not, "
              "because the numbers come from how many frames survived judging. "
              "Build the dataset first:\n"
              "     python3 pipeline/lora/build_jerry_v2_0822.py --write"
              % MANIFEST)
        return 1
    man = yaml.safe_load(open(mp, encoding="utf-8"))
    if man.get("trigger") != TRIGGER:
        print("!! manifest trigger is %r, not %r" % (man.get("trigger"), TRIGGER))
        return 1

    n = man["count"]
    repeat = man["repeat"]
    steps = man["optimizer_steps_at_batch_2"]
    warmup = max(1, round(steps * 0.05))     # research section 5: cosine, 5% warmup

    spec = {
        "id": JOB,
        "task": JOB,
        "node": "002b-first-citizen",
        "runner": "box",
        "needs_gpu": True,
        "needs": ["cuda", "vram20"],
        "priority": 60,
        "max_attempts": 1,
        "est_minutes": 45,
        "owner": "the goblin-LoRA lane, 2026-08-22",
        "consumer": (
            "EVERY GOBLIN BEAT IN EPISODES TWO AND THREE, or none of them. "
            "goblin-i2i-route-0822.md closed the img2img route as a posing "
            "route on a mechanism and named this as the only remaining path to "
            "a goblin who can be put in a NEW BODY POSITION. Bar B2 is that "
            "claim as a measurement. If B2 passes, the beats unlock at once; if "
            "B2 fails with B1 passing, the goblin has no route to a new pose at "
            "all and that is the finding."),
        "success": (
            "A JUDGED ANSWER, NOT A PASSING ONE. The bars in `## BARS` were "
            "committed before a single training frame was admitted. A run that "
            "fails B2 and says so, with the epoch and weight ladders measured, "
            "is a success; a run that reports a score without the ladders is "
            "not."),
        "why": (
            "SIXTEEN ROUNDS OF PROMPT-SIDE FACE WORK WERE VETOED FOUR TIMES, "
            "and canon.yaml route_closure_2026_08_22 closed that route by rule. "
            "The replacement put his pixels in as PIXELS and worked -- his eye "
            "reached an output for the first time -- but only at strengths that "
            "cannot move a pose, because the face surviving and the pose not "
            "moving are ONE MECHANISM read twice: at strength <= 0.40 the pass "
            "never runs the high-noise steps where structure is decided.\n\n"
            "A LoRA acts in those steps. That is the entire argument, and it is "
            "the last one available.\n\n"
            "THE DATASET IS %d FRAMES AND EVERY ONE OF THEM IS HIS DRAWING, "
            "re-lit and re-grounded by that same img2img route at strength "
            "<= 0.40 -- which cannot invent a face precisely because it never "
            "runs the steps that would. v1's 15 frames were animagine's guess at "
            "his face, curated for an age read the founder superseded; they are "
            "not used and manifest-jerry-0821.yaml stays on disk as evidence."
            % n),
        "env": {
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1",
            "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "dataset": MANIFEST,
        "dataset_frames": n,
        "recipe": (
            "kohya sd-scripts v0.11.1, dim 32 / alpha 16, unet_lr 1e-4, "
            "te_lr 5e-5, cosine + %d warmup, AdamW8bit, batch 2, repeat %d, "
            "10 epochs, bf16, seed 20260822. EVERY HYPERPARAMETER IS THE "
            "SAPLING RUNS', UNCHANGED -- this run's variable is the subject and "
            "the dataset, and a moved knob would give a different score two "
            "explanations." % (warmup, repeat)),
        "arithmetic": (
            "%d frames x repeat %d x 10 epochs = %d image passes, %d optimizer "
            "steps at batch 2. Research section 5 puts the target at ~1200 "
            "passes; the repeat is round(1200 / (10 x frames)) and is derived "
            "rather than chosen." % (n, repeat, n * repeat * 10, steps)),
        "requires": {
            "render_venv_package": (
                "peft==0.12.0, installed with --no-deps. diffusers 0.29.2 gates "
                "ALL LoRA loading behind USE_PEFT_BACKEND; its absence once cost "
                "twenty clean minutes of training and five checkpoints before a "
                "nine-second ValueError."),
        },
        "weights_never_reach_git": (
            "Each checkpoint is ~228 MB and GitHub hard-rejects any blob over "
            "100 MiB, while box_runner.Courier._publish does `git add -A -- "
            "farm-out` and pushes -- one checkpoint in farm-out/ leaves a "
            "permanently unpushable commit and stops EVERY lane's results "
            "reaching this tree. The weights stay at %s\\out and the sha256s "
            "travel in registry.yaml." % WORK),
        "steps": [
            # ── 1. STAGE. kohya wants `<image>.txt` beside `<image>`; ours live
            # in pipeline/lora/captions/ on purpose, because farm-out/ is
            # EVIDENCE and the trainer must never write into it. This builds a
            # throwaway flat dir from the manifest and verifies every sha256 on
            # the way -- the item-18 gate in code, so a frame edited or
            # re-rendered since the manifest stops the run instead of silently
            # changing what the LoRA trained on.
            #
            # THE DIR NAME ENCODES THE REPEAT. sd-scripts reads `<N>_<name>` and
            # repeats each image N times per epoch. %d frames x %d x 10 epochs =
            # %d image passes, %d optimizer steps at batch 2, against research
            # section 5's ~1200 target.
            {"name": "stage",
             "argv": [r"C:\banyan-farm\venv-lora\Scripts\python.exe", "-c",
                      STAGE_PY % {"work": WORK, "repeat": repeat,
                                  "manifest": MANIFEST, "trigger": TRIGGER}]},
            {"name": "train",
             "argv": [r"C:\banyan-farm\venv-lora\Scripts\python.exe",
                      r"C:\banyan-farm\sd-scripts\sdxl_train_network.py",
                      "--pretrained_model_name_or_path", BASE_SNAPSHOT,
                      "--train_data_dir", r"%s\img" % WORK,
                      "--output_dir", r"%s\out" % WORK,
                      "--output_name", "%s-sdxl-v2" % TRIGGER,
                      "--network_module", "networks.lora",
                      "--network_dim", "32", "--network_alpha", "16",
                      "--learning_rate", "1e-4", "--unet_lr", "1e-4",
                      "--text_encoder_lr", "5e-5",
                      "--lr_scheduler", "cosine",
                      "--lr_warmup_steps", str(warmup),
                      "--optimizer_type", "AdamW8bit",
                      "--max_train_epochs", "10", "--save_every_n_epochs", "2",
                      "--train_batch_size", "2",
                      "--resolution", "832,1216",
                      "--enable_bucket",
                      # 832 IS THE SHORT-SIDE FLOOR OF THIS TREE'S TRAINER, and
                      # it is not aesthetic: sd-scripts asserts
                      # min(resolution) >= min_bucket_reso before it loads a
                      # weight, and the 1024 default cost the sapling lane a run.
                      # This set holds 832x1216 AND 832x832 frames, so bucketing
                      # is doing real work here rather than resolving to one.
                      "--min_bucket_reso", "832", "--max_bucket_reso", "2048",
                      "--mixed_precision", "bf16", "--save_precision", "bf16",
                      "--gradient_checkpointing",
                      "--cache_latents", "--cache_latents_to_disk", "--sdpa",
                      "--seed", "20260822",
                      "--save_model_as", "safetensors",
                      "--logging_dir", r"%s\log" % WORK]},
            # ── 3. ONE SAMPLE, NOT A GRID. CLAUDE.md, founder 2026-08-03. This
            # draws ONE frame from the final checkpoint and the bar grid is a
            # SEPARATE job that is filed only if this frame is worth grading.
            #
            # THE PROMPT ASKS FOR SOMETHING THE SET DOES NOT CONTAIN, on purpose,
            # and it is the axis this dataset is weakest on: A SETTING THAT IS
            # NOT A MEADOW. All 21 frames stand in the same hazy field because
            # the route cannot change a background, and every caption names it
            # so the trigger is excused from carrying it. If `bnyjerry` only
            # works over that meadow, the excusing did not take and the ship
            # page says so.
            #
            # NOTE THE VENV: the RENDER venv, not venv-lora. The plates we ship
            # are drawn by C:\banyan-farm\venv at bf16 on CUDA, so that is
            # where a LoRA has to be measured.
            {"name": "sample",
             "argv": [r"C:\banyan-farm\venv\Scripts\python.exe",
                      r"%s\sample_lora.py" % WORK,
                      "--lora", r"%s\out\%s-sdxl-v2.safetensors" % (WORK, TRIGGER),
                      "--lora-weight", "0.8",
                      "--prompt",
                      "bnyjerry, 1boy, solo, standing, looking at viewer, upper "
                      "body, a grey stone wall behind, flat overcast light, "
                      "anime style, cel shading, masterpiece, best quality, "
                      "very aesthetic",
                      "--negative",
                      "lowres, worst quality, low quality, text, watermark, "
                      "photorealism, 3d render, blurry, 2boys, multiple heads",
                      "--width", "832", "--height", "832",
                      "--steps", "40", "--guidance", "7.5",
                      "--seed", "20260822",
                      "--out", r"%s\out\SAMPLE-bnyjerry-wall-overcast.png" % WORK]},
            # ── 4. PUBLISH. The courier pushes from farm-out and from nowhere
            # else. ep2-cnet-probe-0817 rendered all four arms successfully,
            # left them in its own job dir, and was recorded as never having run
            # in two separate documents for TWO DAYS -- then passed its own
            # pre-registered bar when someone finally looked at the box by hand.
            # This step is that lesson as code, and box_enqueue refuses the spec
            # without it.
            {"name": "publish",
             "argv": [r"C:\banyan-farm\venv-lora\Scripts\python.exe", "-c",
                      PUBLISH_PY % {"work": WORK, "farmout": FARMOUT,
                                    "trigger": TRIGGER, "job": JOB}]},
        ],
        # THE WEIGHTS ARE NOT AN ARTIFACT AND THAT IS POLICY, NOT AN OVERSIGHT.
        # Each checkpoint is ~228 MB; GitHub hard-rejects any blob over 100 MiB
        # and `box_runner.Courier._publish` does `git add -A -- farm-out` then
        # pushes, so ONE checkpoint in farm-out leaves a permanently unpushable
        # commit and stops every other lane's results reaching this tree. What
        # travels is the SAMPLE and the SHA256s: the publish step writes a
        # manifest naming all five epochs, their hashes and their box paths,
        # which is what registry.yaml reads and what keeps a frame traceable to
        # the exact bytes that drew it.
        "artifacts": [
            r"%s\SAMPLE-bnyjerry-wall-overcast.png" % FARMOUT,
            r"%s\weights-jerry-v2-0822.yaml" % FARMOUT,
        ],
    }

    if not write:
        print("would emit %s" % OUT)
        print("  frames %d  repeat %d  passes %d  steps %d  warmup %d"
              % (n, repeat, n * repeat * 10, steps, warmup))
        print("  framings: %s" % man["framings"])
        print("\n-- dry run. re-run with --write.")
        return 0

    with open(os.path.join(REPO, OUT), "w", encoding="utf-8") as fh:
        fh.write("# JERRY CHARACTER LoRA v2 -- SDXL / animagine-xl-3.1.\n"
                 "# GENERATED. Edit pipeline/lora/emit_train_jerry_v2_0822.py, "
                 "not this file.\n#\n"
                 "# The BARS at the bottom were committed in that generator "
                 "before a single\n# training frame was admitted. The numbers "
                 "come from the manifest.\n\n")
        yaml.safe_dump(spec, fh, sort_keys=False, width=88, allow_unicode=True)
        fh.write("\n## BARS\n#\n")
        for line in BARS.splitlines():
            fh.write(("# " + line).rstrip() + "\n")
    print("wrote %s  (%d frames, repeat %d, %d steps)" % (OUT, n, repeat, steps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
