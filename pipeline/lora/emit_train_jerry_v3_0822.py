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

MANIFEST = "pipeline/lora/manifest-jerry-v3-0822.yaml"
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
OUT = "pipeline/lora/train-jerry-v3-0822.yaml"
JOB = "lora-jerry-v3-0822"
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
with open(os.path.join(DST, "weights-jerry-v3-0822.yaml"), "w",
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
THE THREE BARS BELOW WERE COMMITTED BEFORE THE FIRST v3 FRAME WAS TRAINED ON,
and two of them are v2's own, re-run unchanged so a v3 score is comparable to a
v2 score rather than to a new yardstick.

B2  POSE ADOPTION -- THE DECISIVE BAR, AND THE ONLY REASON v3 EXISTS
    v2 fails this. Every instrument this tree owns has failed it: words (B5), an
    openpose weight ladder that loses his face between 0.65 and 0.50 without
    bending a knee at 0.35, a two-pass whose only seat-keeping cell is the cell
    where he is somebody else, and an i2i whose face breaks between 0.40 and
    0.45 with the pose unmoved at 0.40. So this bar has a MEASURED CONTROL AT
    ZERO and that is what makes it decisive rather than hopeful.

    `bnyjerry` + an OpenPose skeleton at conditioning scale 1.0, TXT2IMG, no
    init, LoRA at the identity weight. THREE authored skeletons x TWO seeds =
    6 cells, and the three are chosen to separate memorisation from a real axis:

      SEAT   -- in the dataset (posed-seat). If this fails, nothing worked.
      KNEEL  -- in the dataset (posed-kneel). Same.
      STRIDE -- **NOT IN THE DATASET, AND DELIBERATELY SO.** It is the only cell
                that distinguishes "the trigger learned three stances" from "the
                pose axis is unlocked". A v3 that adopts seat and kneel and
                refuses stride has memorised its training frames, which is worth
                knowing and is NOT the result the beats need -- shots.md asks
                for a walking goblin in three of its prompt lines.

    Each cell reads on two clauses:
      P1 DID THE BODY ADOPT THE SKELETON? A visible knee bend, hip drop or
         seated fold where the hint has one.
      P2 DID THE IDENTITY SURVIVE IT? E1-E4 of B1, same reading.
    BAR: >= 5 of 6 on P1 AND >= 5 of 6 on P2. A cell that adopts the pose and
    loses the face is a FAIL and so is the reverse -- the claim is that both
    happen in ONE pass, and the whole history of this character is that they
    trade.

B1  IDENTITY, FRESH SETTINGS, 15 CELLS, AT 1:1 AGAINST
    taste/refs/goblin-canon-founder-0821.png
    v2'S BAR, RE-RUN BYTE-FOR-BYTE, and it is here as a NO-REGRESSION bar on the
    thing v2 already does well. Five fresh prompts the dataset does not contain
    at three seeds each; fresh means a setting, a light and a framing no
    admitted frame carries. A cell passes when E1-E4 hold (E5 where costume is
    in frame):
      E1 narrow almond eye, off-white field, TINY dark pupil, heavy upper lid.
         A large round iris of any colour is a FAIL -- four founder vetoes.
      E2 broad low dome; smallish pointed ears NEAR HORIZONTAL.
      E3 smooth face -- no brow furrows, no nasolabial folds, no jowls.
      E4 desaturated sage, washed and high-key.
      E5 shirt with a placket, dark shorts, dark boots.
    BAR: >= 13 of 15, WHICH IS v2'S BAR AND NOT A RELAXED ONE. v3 added three
    frames that share ONE torso byte-for-byte (the canon's, moved by an integer
    DROP of 150) and if identity falls that is the first suspect -- so this bar
    is the instrument that catches the cost of the fix, and a v3 that poses at
    the price of B1 is not shippable.
    JUDGED BY A BLIND COLD READER -- a fresh agent handed one frame, his image
    and the E-clauses, no prompt text, no mention of this lane.

B3  NO REGRESSION, AT TWO WEIGHTS
    An A/B pair -- identical prompt and seed, LoRA loaded and unloaded -- on a
    prompt carrying NO trigger and NO goblin, at weight 0.8 and again at the
    shipping weight if that differs. BAR: no goblin intrudes, and the frame is
    not visibly recoloured, reframed or restyled against its no-LoRA twin.
    CARRIED FORWARD DELIBERATELY: the sapling lane failed this in v1, v2 and v2b
    -- three datasets, two caption schemes, one outcome -- and concluded that B3
    should stop being read as a dataset bar and start being read against the
    WEIGHT and the merge. A failure at 0.8 with a pass lower down is a WEIGHT
    finding here too, not a v3 verdict.

WHAT IS NOT SCORED, SO THE LADDER STAYS SHORT ENOUGH TO ACTUALLY RUN.
B4 (style) and B5 (pose via words) are not in this ladder. B4 passed 15/15 in
every run this tree has done and B5 is answered in advance -- the corrected
caption law says a tag steers only where the attribute varies, and v3 is the
first set where pose varies at all, so B5's outcome is interesting but it is not
what unblocks a beat. B2 is. If B2 and B1 both pass, the beats unlock and B4/B5
are measured on the way through.

THE KNOWN GAP, DECLARED HERE BECAUSE IT WILL SHAPE THE READING. All three posed
frames are MIRROR-SYMMETRIC. The one-knee cell was built for the asymmetric axis
and both budgeted draws traded pose against paint -- draw one gave asymmetry
81.4 with a pink thigh no crop reaches, draw two gave the paint back and
symmetrised him. So if v3 poses but poses SYMMETRICALLY, that is the predicted
shape of a partial pass and the fix is a third draw or a re-authored hint,
neither of which is a research question.

EPOCHS. Judged on the five saved checkpoints, not just the last. Overfitting
past the sweet spot is the standard character-LoRA failure and the epoch axis is
part of the job.

WEIGHT. No weight is sanctioned in advance. The sapling ladder measured a
subject that COLLAPSED below 0.65 while contamination faded smoothly -- two
curves that never cross -- and the usable band was read off the ladder rather
than assumed. The same ladder runs here and the shipping weight comes out of it
or does not exist.
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
              "     python3 pipeline/lora/build_jerry_v3_0822.py --write"
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
        "owner": "the goblin v3 lane, 2026-08-22",
        "consumer": (
            "EVERY GOBLIN BEAT IN EPISODES TWO AND THREE, and the founder's own "
            "open question page at /review/ep2-goblin-twopass-0822, which asks "
            "whether this character can be posed at all. v2 answers no on every "
            "instrument. B2 is that question as a measurement with a control at "
            "zero. If B2 and B1 both pass, the beats unlock at once and the "
            "page gets its answer; if B2 fails with B1 passing, then the pose "
            "is not a dataset property either and that closes the last "
            "candidate on the board."),
        "success": (
            "A JUDGED ANSWER, NOT A PASSING ONE. The bars in `## BARS` were "
            "committed before a single training frame was admitted. A run that "
            "fails B2 and says so, with the epoch and weight ladders measured, "
            "is a success; a run that reports a score without the ladders is "
            "not."),
        "why": (
            "THE DIAGNOSIS EVERYONE WAS CARRYING WAS UNDERSTATED, AND THE "
            "CORRECTION MAKES THE FIX SMALLER THAN A REBUILD. Every document in "
            "this tree said the pose is locked because `21 of 21 training "
            "frames are standing`. Measured on the v2 manifest: 11 are "
            "upper-body crops, 8 are cowboy shots, and only TWO show a lower "
            "body -- the canon and its mirror, verified byte-identical to "
            "taste/refs/goblin-canon-founder-0821.png. THE STANDING PRIOR IS "
            "ONE FRAME DEEP. Round seven's weight ladder and the two-pass's six "
            "cells were both hunting for a competing lower-body configuration "
            "to fade toward, and there is no second configuration in the "
            "weights to fade to.\n\n"
            "SO v3 ADDS THREE POSED FRAMES AND CHANGES NOTHING ELSE. That makes "
            "posed the MAJORITY of every leg the trigger has ever seen -- 3 "
            "against 2 -- in a dataset whose other 21 frames are carried with "
            "their own sha256s and their own caption strings, both asserted at "
            "build time. The 19 crops carry no lower-body signal at all, so "
            "they cannot fight a new one.\n\n"
            "AND IT IS THE FIRST SET IN WHICH THE POSE TAG HAS ANYWHERE TO "
            "ATTACH. v2 named `standing` on all 21 and pose stayed unpromptable, "
            "while the SETTING generalised cleanly out of one meadow -- a "
            "controlled experiment inside one training run, whose clause is "
            "that a caption tag keeps an attribute steerable only where the "
            "attribute VARIES in the dataset. `hazy meadow` had somewhere to "
            "attach outside the LoRA; nothing outside the LoRA knows what this "
            "creature's legs look like.\n\n"
            "THE HISTORY THIS REPLACES. Sixteen rounds of prompt-side face work "
            "were vetoed four times, "
            "and canon.yaml route_closure_2026_08_22 closed that route by rule. "
            "The replacement put his pixels in as PIXELS and worked -- his eye "
            "reached an output for the first time -- but only at strengths that "
            "cannot move a pose, because the face surviving and the pose not "
            "moving are ONE MECHANISM read twice: at strength <= 0.40 the pass "
            "never runs the high-noise steps where structure is decided.\n\n"
            "A LoRA acts in those steps. That is the entire argument, and it is "
            "the last one available.\n\n"
            "THE DATASET IS %d FRAMES AND EVERY ONE OF THEM CARRIES HIS FACE "
            "AS PIXELS, by one of two mechanisms and NOT by resemblance. The 21 "
            "carried from v2 are his drawing re-lit by an img2img pass at "
            "strength <= 0.40, which cannot invent a face because it never runs "
            "the steps that would. The 3 posed frames are his head held OUTSIDE "
            "an SDXL inpaint mask -- base weights, unet.in_channels 4, so the "
            "unmasked latent is restored at EVERY timestep and cannot drift at "
            "any strength -- with the legs generated inside at 0.95 against an "
            "openpose skeleton and NO LoRA in the pass, then rows 0..883 pasted "
            "back byte for byte and asserted. Their legs are generated and the "
            "manifest says so. v1's 15 frames were animagine's guess at his "
            "face, curated for an age read the founder superseded; they are not "
            "used and manifest-jerry-0821.yaml stays on disk as evidence."
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
            "IDENTICAL TO v2's, DELIBERATELY AND WITHOUT EXCEPTION -- this "
            "run's single variable is the three added frames, and a moved knob "
            "would give a different score two explanations. "
            "kohya sd-scripts v0.11.1, dim 32 / alpha 16, unet_lr 1e-4, "
            "te_lr 5e-5, cosine + %d warmup, AdamW8bit, batch 2, repeat %d, "
            "10 epochs, bf16, seed 20260822. EVERY HYPERPARAMETER IS THE "
            "SAPLING RUNS', AND v2's, UNCHANGED. The repeat is re-derived from "
            "the frame count by the same formula and lands at 5, which happens "
            "to give exactly 1200 image passes." % (warmup, repeat)),
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
        # THE PAYLOAD, AND IT IS HERE BECAUSE ITS ABSENCE COST A STEP.
        # The 2026-08-22 run trained clean -- 630 steps, rc=0, five checkpoints
        # on disk -- and then died in one second on `can't open file
        # sample_lora.py`, because the sample step named a script in the job's
        # work dir that nothing had ever written there. The training was not
        # lost, but the job was recorded as FAILED, and a job in failed/ is a job
        # the next reader believes produced nothing.
        #
        # THE RULE THIS ENCODES: a step that names a script under the WORK dir
        # must have a payload that puts it there. box_enqueue verifies payload
        # paths against each other but cannot know which argv entries are files.
        "payload": {
            r"%s\sample_lora.py" % WORK: open(
                os.path.join(REPO, "pipeline/lora/sample_lora.py"),
                encoding="utf-8").read(),
        },
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
                      "--output_name", "%s-sdxl-v3" % TRIGGER,
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
                      "--lora", r"%s\out\%s-sdxl-v3.safetensors" % (WORK, TRIGGER),
                      "--lora-weight", "0.8",
                      "--prompt",
                      # THE ONE SAMPLE ASKS THE ONE QUESTION v3 CHANGED, and it
                      # asks it on a setting the set does not contain so the
                      # v2 canary is not lost either. `sitting` is now a token
                      # that VARIES in the pixels, which it never was in v2, so
                      # a txt2img sample is for the first time a real read on
                      # B5 -- and it is free. The two failure modes are
                      # visually distinct: a wrong face says training hurt
                      # identity, a standing figure says the tag still has
                      # nowhere to attach and only the skeleton ladder will
                      # tell us anything. Neither is scored here; this is the
                      # canary, and the ladder is the bar.
                      "bnyjerry, 1boy, solo, sitting, looking at viewer, upper "
                      "body, a grey stone wall behind, flat overcast light, "
                      "anime style, cel shading, masterpiece, best quality, "
                      "very aesthetic",
                      "--negative",
                      "lowres, worst quality, low quality, text, watermark, "
                      "photorealism, 3d render, blurry, 2boys, multiple heads",
                      "--width", "832", "--height", "832",
                      "--steps", "40", "--guidance", "7.5",
                      "--seed", "20260822",
                      "--out", r"%s\out\SAMPLE-bnyjerry-v3-sitting-wall.png" % WORK]},
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
            r"%s\SAMPLE-bnyjerry-v3-sitting-wall.png" % FARMOUT,
            r"%s\weights-jerry-v3-0822.yaml" % FARMOUT,
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
        fh.write("# JERRY CHARACTER LoRA v3 -- SDXL / animagine-xl-3.1.\n"
                 "# GENERATED. Edit pipeline/lora/emit_train_jerry_v3_0822.py, "
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
