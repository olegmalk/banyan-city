# Character LoRA on SDXL for the recurring cast — external research

**Lane:** external research, 2026-08-20. **Spend: $0.** No training run, no
download, no queue filing. Everything below is either upstream fact (linked) or
a read-only probe of machines we already own.

## Why this file exists

`STATE.md` (2026-08-20, founder): **one day per episode from ep3 on**, and
enabler #1 is *"character LoRA on the canon cast — kills the identity-drift
class."* Today identity is re-fought per frame: every plate prompt carries the
goblin's design clause in prose, spends ~15 of a 77-token CLIP budget on it
(`pipeline/sd_prompt.py` exists solely because we overrun that budget), and
still comes back wrong often enough that `pipeline/canon.yaml` has *four*
open drift subjects about one character's hair, height, leaf count and fruit
colour. A LoRA moves identity out of the prompt and into the weights.

## Grades used

- **DEMONSTRATED** — verified here by running/inspecting the artifact on our own
  hardware.
- **MAINTAINER** — the author of the weights/code says it, on their own model
  card, docs or issue tracker. Believable, unverified by us.
- **COMMUNITY** — repeated, load-bearing practitioner consensus with artifacts
  behind it (Civitai guides, kohya discussions, tagger cards).
- **FOLKLORE** — restated assertion with no image, diff or code behind it.
  Recorded so the next lane does not mistake it for evidence.

---

## 0. SCOPE — who gets a LoRA at all (founder ruling, 2026-08-20)

The founder ruled today that **one-episode characters get no consistency
infrastructure.** Consistency effort is reserved for the recurring cast. The
story tree was then surveyed against that rule
(`genomes/sapling/lineage.yaml`, every `nodes/*/node.md` speaker label,
`genomes/sapling/style.md` §Character model sheet):

| Character | On screen in | Nodes | Ruling |
|---|---|---|---|
| **THE SAPLING** (protagonist / VO) | ep1–ep7, every branch | **16/16** | **LoRA — build now** |
| **THE SCAVENGER / Jerry** (adult goblin) | ep2, 3, 4, 5, 6, 7 | **8** | **LoRA — build now** |
| THE FARMER | ep4, 5, 6, 7 | 9 | LoRA — **blocked**, never drawn to approval (4 rejected charref rounds) |
| THE MAGISTRATE | ep6, 7 | 3 | LoRA — **blocked**, only 2 charref rounds exist |
| GUARD 1 (Dren) / GUARD 2 | ep2 (002b) only | 1 | **NO LoRA** |
| THE ASSESSOR | ep5 (005) only | 1 | **NO LoRA** |
| THE PILGRIM | ep7 (007a) final beat, non-speaking | 1 | **NO LoRA** |

**ep3 = node `003b-one-leaf-for-yes`, and its entire on-screen cast is two:
the sapling and the scavenger.** Those two LoRAs unblock ep3 completely. The
farmer and magistrate are genuinely recurring but have no approved reference
frames to train from, so they queue behind their charref approval, not behind
this research.

Sunk-cost note, recorded rather than argued: the guards already consumed 5
charref rounds, 4 reference sheets and two `canon.yaml` drift subjects
(`ep2-guard-cast`, `ep2-guard-hair`) across 7 beats. The ruling does not undo
that work — those sheets still serve ep2 — it stops the *next* increment.

### 0.1 The rule this becomes for ep3 scripting

> **One-episode characters are designed for the engine; recurring characters
> get the engine trained on them.**
>
> When a script introduces a character who appears in exactly one episode, the
> design brief is *"whatever animagine-xl-3.1 draws consistently by default"* —
> a stock, prior-aligned silhouette the base model already has a strong mode
> for, described in three or four booru tags. It is not permitted to acquire a
> `canon.yaml` drift subject, a charref round, a reference sheet or a LoRA.
> Consistency tooling is spent only on characters who will be re-drawn in a
> later episode.

Design guidance for those one-shot characters, from the consistency literature
(**COMMUNITY**): push the silhouette so the character is identifiable from
outline alone; limit the palette to two or three saturated colours in clear
zones rather than seven related tones; put the accent colour on one prominent
element. A character with three distinct colour zones regenerates more
consistently than a subtly-layered one — which is exactly why our guards, whose
only distinguishing canon is *"A = dark cropped hair, B = light sandy hair"*,
needed five rounds. Two tags of difference is below the engine's resolution.

---

## 1. The machine, measured — and the brief's spec was wrong

Probed over ssh today, read-only:

| Fact | Value | Grade |
|---|---|---|
| GPU | `NVIDIA GeForce RTX 5090 **Laptop** GPU` | **DEMONSTRATED** |
| VRAM | **24463 MiB = 23.89 GiB** — *not* 32 GB | **DEMONSTRATED** |
| Compute capability | `(12, 0)` — Blackwell **sm_120** | **DEMONSTRATED** |
| Driver | 610.78 | **DEMONSTRATED** |
| Python | 3.12.10 (`C:\banyan-farm\venv`) | **DEMONSTRATED** |
| torch | **2.11.0+cu128** — correct wheel, sm_120 kernels present | **DEMONSTRATED** |
| Free disk on C: | **54.0 GB** of 926.5 GB | **DEMONSTRATED** |
| Base model cached | `models--cagliostrolab--animagine-xl-3.1`, diffusers layout, snapshot `483f0c322568ed13697ed01dd0be07204746d12b` | **DEMONSTRATED** |
| Trainer installed | **NONE.** `pip list` is 29 packages: no `kohya`, no `sd-scripts`, no `peft`, no `bitsandbytes`, no `opencv`, no `onnxruntime`. `diffusers 0.29.2`, `accelerate 0.33.0`, `transformers 4.44.2` | **DEMONSTRATED** |

Two consequences that change the plan:

1. **24 GB, not 32.** SDXL LoRA at 1024² still fits comfortably (§5), so the
   still-side plan is unaffected. But it kills the video-side option outright:
   LTX-2.3 LoRA training documents **32 GB as the floor** with INT8
   quantisation and 80 GB+ as the recommendation (**MAINTAINER**). We are below
   the floor. A video-model LoRA is not available to us on this card at any
   settings, so §7's conclusion is not a preference, it is the only route.
2. **No trainer.** Per the brief, this means **spec + SETUP.md, and STOP** — no
   `--backlog` filing. `pipeline/lora/SETUP.md` names the one-time install.

### 1.1 The sm_120 trap, and why our venv must be protected

**MAINTAINER / COMMUNITY.** Stable torch wheels below cu128 carry no sm_120
kernels; a 5090 hitting them either warns and degrades or raises
`CUDA error: no kernel image is available for execution on the device`
([kohya_ss #3276](https://github.com/bmaltais/kohya_ss/issues/3276),
[axolotl #2525](https://github.com/axolotl-ai-cloud/axolotl/issues/2525)).
Our venv is already correct — `2.11.0+cu128` — and
`pipeline/ONBOARD-WINDOWS.md:136` already records the cu128 index as mandatory.

**The live hazard is `xformers`, and it is a silent one.** sd-scripts'
`requirements.txt` pulls xformers; pip decides the installed torch is
incompatible with the xformers wheel it picked and **quietly replaces torch
with an older build that has no sm_120 kernels, with no warning that matters**
([RTX 5090 survival guide](https://dev.to/madcoolseed/rtx-5090-survival-guide-sm120-cuda-12-and-13-side-by-side-and-the-xformers-trap-25nh)).
That would break every render on this box, not just training.

Mitigations, in order, both written into `SETUP.md`:

- **Install the trainer into its OWN venv** (`C:\banyan-farm\venv-lora`), never
  `C:\banyan-farm\venv`. The render venv is load-bearing for the whole farm and
  must not be a dependency-resolution target.
- **Do not install xformers.** Use `--sdpa` (torch's built-in scaled dot
  product attention) instead. sd-scripts supports it as a first-class flag and
  it needs no extra package.
- **After every install step, `pip show torch` and confirm the `+cu128`
  suffix.** A version string without it means pip swapped the wheel.

---

## 2. Trainer: kohya sd-scripts

| Trainer | For SDXL characters in 2026 | Verdict |
|---|---|---|
| [**kohya-ss/sd-scripts**](https://github.com/kohya-ss/sd-scripts) | Reference implementation since 2022; `sdxl_train_network.py` is the path every community config is written against. Fused backward pass (v0.9+, Jan 2025) folds the optimizer step into the backward pass per parameter, cutting VRAM up to ~60% — SDXL 1024² training from ~24 GB down to ~10 GB with bf16 + Adafactor (**COMMUNITY**) | **THE PICK** |
| [OneTrainer](https://github.com/Nerogar/OneTrainer) | Mature DoRA support and a RunPod cloud tab. Genuinely good, but its advantages are cloud workflow and a LoRA variant we do not need | second choice |
| [ai-toolkit](https://github.com/ostris/ai-toolkit) | Now primarily the FLUX.2 / Z-Image / Qwen-Image tool. SDXL is not where its attention is | no |

Reason for the pick beyond features: **it is the only one whose failure modes
are already written down for our exact card.** The kohya_ss issue tracker has
our GPU in it. Depth of prior art is worth more here than DoRA.

Note the distinction: **`kohya-ss/sd-scripts` (the CLI library), not
`bmaltais/kohya_ss` (the Gradio GUI).** The GUI adds a large dependency tree and
a browser we do not want on a headless queue box; our jobs are argv lists
(`pipeline/box_enqueue.py`), which is exactly what sd-scripts is.

---

## 3. Dataset: how many frames, and of what

**COMMUNITY consensus, converging across sources:** 20–80 curated images for a
character; 20 is the floor for a good result, 5 gets "a mediocre LoRA"
([Civitai — Make your own LoRAs](https://civitai.com/articles/4/make-your-own-loras-easy-and-free)).
The brief's 20–60 is squarely inside consensus. **Variety matters more than
count** — angles, framing, lighting, expression.

**Regularization images: skip them.** They are optional in kohya, and the
practitioner report is that they either massively overfit or dampen training to
nothing, so they are worth reaching for only when the model cannot learn the
subject at all ([kohya_ss discussion #2056](https://github.com/bmaltais/kohya_ss/discussions/2056)).
Using them properly would also mean generating 200–500 class images first —
GPU time we would rather spend on the actual run. **COMMUNITY.**

Two dataset facts specific to us:

- **Our source frames are already 832×1216 / 9:16 plates.** SDXL bucketing
  (`--enable_bucket`, min 1024 / max 2048 per the standard config) handles
  non-square natively; we do **not** need to crop to 1024². Where a plate is a
  wide two-shot, a face/bust crop is still worth adding as a *separate* image —
  close crops teach the face, full frames teach the silhouette and costume.
- **The sapling is not a fixed-size subject.** `genomes/sapling/style.md:150-158`
  is a growth ladder: ~15 cm in 001 → ~40 cm in 002 → ~55 cm in 003b → ~90 cm
  in 004 → ~1.2 m in 005 → ~1.6 m in 006a/007a, with the leaf count rising
  2→6. A LoRA must therefore encode the sapling's **design language** (trunk
  curve, cotyledon shape, facelessness, palette) and must NOT bake in a size or
  a leaf count. §4 says how: those two attributes stay in the captions as
  variables, which keeps them promptable instead of absorbed.

---

## 4. Captioning — booru tags, in the dialect we already speak

`pipeline/sd_prompt.py` confirms our inference dialect is comma-separated
booru-ish tags terminating in `masterpiece, best quality`, and it exists
because our prompts overrun CLIP's 77 tokens. Animagine XL 3.1's own card
(**MAINTAINER**) states the model is *"optimized for Danbooru-style tags rather
than natural language prompts"*, gives the template
`1girl/1boy, character name, from what series, everything else in any order`,
and asks for the quality tags `masterpiece, best quality, very aesthetic,
absurdres` ([model card](https://huggingface.co/cagliostrolab/animagine-xl-3.1)).

**Train captions in that same dialect.** A caption written in prose while
inference is written in tags trains a mapping we never use.

### The pruning rule (**COMMUNITY**, and the single most consequential choice)

- The **activation tag goes first in every caption file** — booru training puts
  the strongest signal at the head of the tag string.
- **Delete every tag that describes the character's permanent identity** —
  skin colour, ear shape, tusk, bald head, hair colour, body build. Deleted
  attributes get absorbed *into the activation tag*, which is precisely the
  outcome we want: it means `bnyjerry` alone reproduces green skin, bald head
  and patchwork cloak with no clause spent.
- **Keep every tag that is a variable** — pose, expression, camera framing,
  lighting, background, time of day, and anything we need to keep steering. A
  tag kept in the caption stays promptable; a tag deleted becomes mandatory.
- Do not over-prune clothing unless the costume is genuinely invariant.

Applied to our two subjects:

| Subject | Trigger | PRUNE (absorb into trigger) | KEEP (stay steerable) |
|---|---|---|---|
| Goblin / Jerry | `bnyjerry` | green skin, bald head, patchwork cloak, enormous ears, broken tusk, lean wiry build, adult proportions | pose, gesture, expression, shot size, background, lighting, other figures in frame |
| Sapling | `bnysapling` | thin curved trunk, cotyledon leaf shape, no face, palette | **leaf count**, **height/scale**, pot vs soil, pose/lean, background, lighting |

Keeping leaf count and height in the sapling's captions is the mechanism that
makes one LoRA serve all seven episodes of the growth ladder.

**Trigger tokens must be rare strings.** `bnyjerry` / `bnysapling` are chosen to
tokenize as nonsense rather than collide with a real booru tag — `sapling` and
`jerry` both exist in the base model's vocabulary and would drag their priors in.
Verify by tokenizing before the run (we already own `pipeline/clip_token_count.py`).

**A second win, and it is the one that pays for this project.** A trigger token
is ~3 CLIP tokens where the goblin's prose clause is ~15–20. On a 77-token
budget that `pipeline/sd_prompt.py` was written to fight, the LoRA hands back
~15 tokens *per plate prompt* to action, framing and light — the exact content
that module documents us having truncated away on 2026-07-26.

### Tagger

**[`SmilingWolf/wd-eva02-large-tagger-v3`](https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3)
at threshold 0.35** (its default and the community default; **COMMUNITY**). It
writes kohya-style `.txt` sidecars next to each image. sd-scripts ships
`finetune/tag_images_by_wd14_tagger.py` which runs the WD family directly, so
this is not a new dependency beyond `onnxruntime-gpu`.

The tagger output is a **draft, not the caption.** Every file gets a human pass
to apply the prune/keep table above — auto-tags will happily emit `green skin`
and `bald`, which are exactly the tags that must be deleted.

---

## 5. Hyperparameters for a style-preserving character LoRA

Two clusters exist in the sources and they disagree; both are recorded, with
our pick and why.

| Knob | "Small/fast" (Civitai) | "Standard" (kohya-config consensus) | **Ours** |
|---|---|---|---|
| network_dim (rank) | 16 | 32 (64 for complex, 128 for style) | **32** |
| network_alpha | 8 (= dim/2) | = dim, or dim/2 | **16** (= dim/2) |
| unet_lr | 5e-4 | 1e-4 | **1e-4** |
| text_encoder_lr | 1e-4 (⅕ of unet) | 5e-5 | **5e-5** |
| scheduler | cosine with 3 restarts | constant with warmup | **cosine, 5% warmup** |
| optimizer | AdamW8bit | AdamW8bit | **AdamW8bit** |
| total steps | 250–1000 | 1500–2400 (20 img × 3 rep × 25–40 ep) | **~1200**, checkpoint every 2 epochs |

**Why 32/16 and not 16/8.** 16/8 is the Civitai default *for a photoreal person
on a photoreal base*. Our subjects carry non-human structure — a broken tusk, a
specific cotyledon shape, a two-leaf silhouette — which is closer to the
"complex" case. 32 is the conservative step up; it is still a ~35 MB file and
still trains inside our VRAM. Rank 64+ is where style bleed starts being
reported.

**Why alpha = dim/2 and not alpha = dim.** Alpha below rank scales the update
down and is the current preference for *style-preserving* transfer — precisely
our third bar. **COMMUNITY.**

**Why 1e-4 and not 5e-4.** 1e-4 is the documented SDXL baseline (5e-4 is the
SD1.5-era number carried forward). Our bar is style preservation against a
shipped look, so we take the slower rate and buy the difference back with
checkpoints.

**Save every 2 epochs and judge the checkpoints, not just the last one.** The
standard character-LoRA failure is overfitting past the sweet spot; the cheap
insurance is having epoch 8, 10, 12 and 14 on disk and picking by §Bars. This is
also the honest reading of the 250–1000 vs 1500–2400 disagreement: nobody knows
the right step count for *our* dataset, so we sample the axis instead of
asserting a point on it.

Memory settings for 24 GB (**COMMUNITY**, standard SDXL config):
`--mixed_precision bf16 --gradient_checkpointing --cache_latents
--cache_latents_to_disk --enable_bucket --min_bucket_reso 1024
--max_bucket_reso 2048 --sdpa --train_batch_size 2`. With the fused backward
pass available this has substantial headroom on 24 GB; batch 2 is chosen for
speed, and batch 1 is the fallback if it OOMs.

---

## 6. One LoRA per character, not one combined LoRA

**COMMUNITY, and unambiguous.** Training multiple characters into one LoRA with
distinct trigger tokens is possible but the reported failure is *feature
bleeding* — the characters converge toward each other, and at inference two
triggers in one prompt tend to produce two of the same character. Mitigations
exist (regional prompting, selective block enabling, multi-token DreamBooth
clustering — [arXiv 2510.09475](https://arxiv.org/abs/2510.09475)) and all of
them add inference-time machinery.

**Our shape makes the choice easy.** The goblin and the sapling are not even the
same *kind* of object — a humanoid and a plant. Separate LoRAs let us:

- weight them independently (a beat that is 90% sapling can run the goblin at
  0.5);
- retrain one without re-validating the other;
- ship the goblin LoRA the moment it passes, without waiting on the sapling's
  harder growth-ladder problem.

**The known cost, stated up front:** loading two character LoRAs simultaneously
is itself a reported bleed source, and beats with both characters in frame are
common from ep2 on. The mitigation to try first is the cheap one — drop each
LoRA's weight to ~0.65 when both are loaded, which is the reported working
point (**COMMUNITY**). This is a real open risk, and it is why the bars in §8
include a both-in-frame case rather than only single-subject prompts.

---

## 7. Where the LoRA has to live in OUR pipeline — the still side, and only there

Our architecture is: **SDXL (animagine-xl-3.1) draws the plate → LTX-2.3 22B
distilled animates it i2v** (`pipeline/ltx_i2v.py`). The question is whether the
character LoRA needs to exist on the LTX side too.

**Answer: no, and it cannot.** Three independent reasons, strongest last.

1. **It is not affordable.** §1 — LTX-2.3 LoRA training floors at 32 GB with
   INT8; the box has 23.89 GiB. Off the table regardless of merit.
2. **Identity is established by the conditioning image.** LTX i2v takes the
   plate as its conditioning signal, so whatever identity the plate carries is
   the identity the clip starts from. Fixing identity at the plate fixes it for
   the clip's opening — which is where a viewer reads who the character is.
3. **The drift that remains is a duration problem, not an identity-encoding
   problem** — see the caveat below.

**The honest caveat, because it is real.** LTX's own docs describe image
conditioning as a *soft* signal, not a pinned frame 0: the two-stage workflow
injects at **strength 0.7 in stage 1** ("establishing the starting point while
leaving room for natural motion") and **1.0 in stage 2** ("to preserve detail")
([LTX i2v guide](https://docs.ltx.io/open-source-model/usage-guides/image-to-video)).
So the model *may* redraw the subject. There is an open upstream report of
exactly this — [Lightricks/LTX-2 issue #255](https://github.com/Lightricks/LTX-2/issues/255),
i2v output "looks like a different generated person", **no maintainer reply, no
workaround, still open**. Community reporting puts noticeable drift past the
**5–8 second** mark (**FOLKLORE**, no artifact behind it, recorded only as a
direction to watch).

**Why that caveat does not change the conclusion for us:** our beats are
seconds long, not 5–8 seconds of continuous shot, so we sit at the short end of
the drift curve; and even if we sat at the long end, the fix available to a
24 GB box is not a video LoRA — it is shorter clips, a stronger conditioning
strength, or a mid-clip conditioning frame, all of which are prompt/parameter
work on the existing renderer.

**Therefore: the LoRA is a plate-step artifact.** It loads in whatever draws the
832×1216 SDXL still (`render_wave_sample.py` / `still_local.py` /
`controlnet_plate.py`) and nothing in `ltx_i2v.py` changes. This also means the
LoRA is testable entirely in stills — three minutes per sample, no video
render — which is what makes ONE SAMPLE BEFORE ANY BATCH cheap to honour here.

**Unresolved, and flagged for whoever owns the LTX lane:** we have never
*measured* our own i2v identity retention. The 0.7-strength fact says drift is
possible; issue #255 says it happens to someone. A one-clip probe — plate in,
clip out, compare first and last frame identity — would settle it for our
settings and our clip lengths. It is not this lane's unit and it is not a
blocker for training.

---

## 8. Pre-registered bars (written before any pixels; full form in `pipeline/lora/`)

1. **Identity lock** — 5 fresh prompts (not in the dataset) × 3 seeds = 15
   frames per character. A **blind cold reader**, given only the canon clause
   and the image, must call it the same character in ≥13/15. This is the same
   cold-read instrument `pipeline/jobs/ep2-b20-canonword-0816.yaml` used for
   the fig colour — the standing house method, not a new one.
2. **Style preservation** — the 15 frames must be indistinguishable in look from
   the shipped ep2 plates. Any drift toward photoreal, 3D, or a different line
   weight is a FAIL even if identity is perfect.
3. **No-regression** — a non-cast prompt (a landscape, an unrelated figure)
   rendered with the LoRA loaded at the shipping weight, against the identical
   prompt/seed with it unloaded. Visible contamination is a FAIL. This is the
   test that catches a LoRA that has learned "our style" instead of "this
   character".
4. **Both-in-frame** — one two-subject prompt with both LoRAs loaded at 0.65,
   checking that the sapling does not acquire green skin and the goblin does not
   sprout leaves (§6's known risk).
5. **Growth ladder** (sapling only) — the same prompt at `two leaves` and at
   `six leaves`, at 40 cm and at 1.6 m. If the LoRA has baked the size, this is
   where it shows, and it is a FAIL that sends us back to the captions.

---

## Sources

- [kohya-ss/sd-scripts](https://github.com/kohya-ss/sd-scripts) — reference SDXL LoRA trainer
- [bmaltais/kohya_ss issue #3276](https://github.com/bmaltais/kohya_ss/issues/3276) — RTX 5090 CUDA + xformers incompatibility
- [bmaltais/kohya_ss issue #3332](https://github.com/bmaltais/kohya_ss/issues/3332) — RTX 5090 training slowness / accelerate config
- [axolotl-ai-cloud/axolotl issue #2525](https://github.com/axolotl-ai-cloud/axolotl/issues/2525) — Blackwell sm_120 support
- [RTX 5090 survival guide: sm_120, CUDA 12 and 13, and the xformers trap](https://dev.to/madcoolseed/rtx-5090-survival-guide-sm120-cuda-12-and-13-side-by-side-and-the-xformers-trap-25nh)
- [OneTrainer vs Kohya SS vs AI Toolkit (2026)](https://sanj.dev/post/onetrainer-vs-kohya-ss-vs-ai-toolkit/)
- [LoRA Training 2026: Kohya SS, FLUX & VRAM Optimization](https://sanj.dev/post/lora-training-2025-ultimate-guide/)
- [Civitai — Make your own LoRAs, easy and free](https://civitai.com/articles/4/make-your-own-loras-easy-and-free) — dataset size, dim/alpha, LR, tag pruning
- [Haoming02 — All-in-One SD Guide, LoRATraining.md](https://github.com/Haoming02/All-in-One-Stable-Diffusion-Guide/blob/main/LoRATraining.md) — booru trigger placement
- [bmaltais/kohya_ss discussion #2056](https://github.com/bmaltais/kohya_ss/discussions/2056) — regularization images
- [cagliostrolab/animagine-xl-3.1 model card](https://huggingface.co/cagliostrolab/animagine-xl-3.1) — tag dialect, quality tags, negative prompt
- [SmilingWolf/wd-eva02-large-tagger-v3](https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3) — tagger
- [Civitai — Preventing style bleeding from character LoRAs by selectively enabling blocks (SDXL)](https://civitai.com/articles/5301/preventing-style-bleeding-from-character-loras-by-selectively-enabling-blocks-sdxl)
- [arXiv 2510.09475 — Few-shot multi-token DreamBooth with LoRA for style-consistent character generation](https://arxiv.org/abs/2510.09475)
- [LTX docs — Image-to-Video workflow](https://docs.ltx.io/open-source-model/usage-guides/image-to-video) — conditioning strengths 0.7 / 1.0
- [Lightricks/LTX-2 issue #255](https://github.com/Lightricks/LTX-2/issues/255) — i2v does not preserve identity; open, no maintainer reply
- [LTX — LoRA training for video generation](https://ltx.io/model/capabilities/lora-training) and [Lightricks/LTX-2 issue #180](https://github.com/Lightricks/LTX-2/issues/180) — video LoRA VRAM floor
- [getimg.ai — How to create consistent characters with AI (2026)](https://getimg.ai/blog/how-to-create-consistent-characters-with-ai) and [Vidu — Character design for AI video](https://www.vidu.com/blog/character-design-ai-video) — engine-friendly design principles (§0.1)
