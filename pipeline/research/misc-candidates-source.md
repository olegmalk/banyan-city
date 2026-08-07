# Misc candidates — source reading

Three repos read (analysis only, nothing executed), cloned shallow on
2026-08-04 into a scratchpad, not into this repo:

| # | Repo | Cloned from | Why we looked |
|---|---|---|---|
| 1 | `Wan2.2-TI2V-5B-Turbo` | `quanhaol/Wan2.2-TI2V-5B-Turbo` | a 4-step distill of the model we already run in production |
| 2 | `kandinsky-5` | `kandinskylab/kandinsky-5` | the cleanest-licensed (MIT) I2V model in the field |
| 3 | `Open-Sora` | `hpcaitech/Open-Sora` | completeness — confirm or correct our recorded "44GB+, weaker" |

**Legal note on repo 1.** `Wan2.2-TI2V-5B-Turbo` is CC BY-NC-SA 4.0. Reading
and analysing it is fine; using its weights in a project that publishes output
is not (see `models-licence.md`). Everything below about it is a description of
*method* in our own words, from their README, configs and paper reference — no
code from that repo has been copied into banyan-city and none should be. The
Self-Forcing technique it applies is from a public paper and is not theirs to
own; only their specific weights and code are encumbered.

**This does not reopen a settled question.** `licence_gate.py:196-209` already
records quanhaol's weights as a permanent hard fail ("Rejected on licence, not
merit, and never worth revisiting"), and nothing here disputes that. The
question asked was the different one: *could we build our own clean equivalent?*

**Incidental find, worth someone's five minutes.** `licence_gate.py:400-408`
still carries the belief that was corrected on 2026-08-02 twenty lines earlier:
it states quanhaol "has no text at any URL: both LICENSE paths 404 ... Reading
is not a task that can be completed." Cloning the repo today disproves that
first-hand — `LICENSE.md` is **git-tracked, 19,151 bytes**, contains
"NonCommercial" nine times and "ShareAlike", exactly as the correction at
`:196-208` says. The `UNCLEARABLE` dict is empty and the gate's *behaviour* is
correct, so nothing is mis-gated; but the stale paragraph tells the next reader
to stop looking for a document that does exist. Prose fix only, in a guard file
I have not touched.

## Summary — the three verdicts

1. **Make our own 4-step distill: possible, clean, and not worth it at the
   published scale.** The method is DMD2, the training scale is confirmed
   (16xA100 / 48 h / 4,000 iters), the upstream framework is **Apache 2.0**, and
   the distillation is **data-free** — we would need only our own stills and
   prompts, no licensed corpus. Cost of one run ~$850–2,100; realistic first
   attempt **$2,000–5,000 plus 1–2 weeks**. A LoRA-DMD variant would be
   ~$150–500 on a single rented GPU but is unvalidated for this model.
   **The killer is the payoff, not the cost:** our own measured step sweep puts
   the real wall-clock win at **~2.2x (188s → ~85–100s)**, not the 3.5x
   projected in `speed-quant.md` — see §1e-bis, which corrects that projection.
   Recommendation: **wait** for a permissively-licensed distill (the demand is
   proven, the technique is public, $0 to be patient), and take the free
   6-step timing measurement that would firm up the 2.2x figure.

2. **Kandinsky 5.0 I2V Lite: MIT confirmed, and unsuitable for us on the
   merits.** Its shipped default negative prompt negates "2D cartoon, cartoon,
   2d animation, paintings" — the model is tuned away from our entire aesthetic.
   It also caps at **464x848** for our input (a hard pixel budget in code, not a
   setting) and the distilled/no-CFG checkpoints are **T2V only**, so I2V is
   stuck at NFE 100 / 139 s per clip on an H100. The 12GB claim is real and
   SDPA is supported, so the 5070 Ti box *could* run it — but 16GB of host RAM
   against a resident Qwen2.5-VL-7B is the open risk. Honest role: a
   licence-emergency fallback, nothing more.

3. **Open-Sora: confirmed, and worse than our note said.** Peak memory is
   **52.5 GB at 256x256 with offloading already on**, 60.3 GB at 768px; our
   recorded "44GB+" was their multi-GPU figure. 11B denoiser stacked on T5-XXL.
   Last model release March 2025. Not reachable on a 24GB card at any setting.

---

## 1. Wan2.2-TI2V-5B-Turbo — what they actually did, and what it would cost us

Verdict up front: **a clean 4-step distill of our own production model is
technically reproducible and legally clean, but it is a ~$1k–5k, one-to-two-week
project, not a $0 one.** The recommendation is to wait for someone else to ship a
permissively-licensed equivalent, because the demand is already proven and the
technique is public. If the founder ever wants to fund it, there is a cheaper
variant (LoRA-DMD, roughly $150–500) that is worth pitching instead of the
published full-parameter recipe.

### 1a. The method

Two things at once, and the second falls out of the first for free:

**Step distillation via DMD2** (Distribution Matching Distillation 2, arXiv
2405.14867; the original DMD is 2311.18828 — both cited in their own source).
Three copies of the 5B denoiser are held at once:

- a **student** ("generator"), initialised from Wan2.2-TI2V-5B, trainable;
- a **teacher** ("real score"), the same frozen weights, never updated;
- a **critic** ("fake score"), trainable, whose job is to model the
  distribution the *student* currently produces.

Each iteration: the student produces a video from noise; the critic and the
teacher are each asked to denoise a re-noised version of that output; the
difference between their two predictions is used as a gradient that pushes the
student's output distribution toward the teacher's. The critic is trained
alongside on a plain diffusion objective against the student's own samples, so
it tracks the moving target. The critic is updated 5 times per student update
(`dfake_gen_update_ratio: 5`).

**CFG distillation, for free.** When the teacher's prediction is computed, it
is evaluated *twice* — once on the real prompt, once on the negative prompt —
and combined at guidance scale 6.0, i.e. the teacher is asked its CFG'd
opinion. The critic side uses guidance 0.0. So the student is trained to match
a distribution that already has CFG baked in, and therefore needs no CFG at
inference. That is why their model runs one forward pass per step instead of
two. See `model/dmd.py:38-43` and `:124-148` for where the two guidance scales
diverge.

**Four steps, fixed.** The student is trained and run on the timestep list
`[1000, 750, 500, 250]` with `warp_denoising_step: true` and a flow-matching
timestep shift of 5.0. Total work at inference = **4 forward passes**, versus
our production 14 steps (`speed-quant.md:127`) at CFG 5.0 = **28 passes** — we
do run classifier-free guidance, with a real negative prompt
(`pipeline/wan_i2v.py:250-252`, guidance default `:552`). 7x fewer passes.

**But 7x fewer passes is not 7x faster, and this is the number that matters.**
See §1e-bis below — our own measured step sweep says the real wall-clock win is
about **2.2x**, and a projection in `speed-quant.md` that says otherwise is
superseded.

**One nuance worth flagging:** despite the repo being a fork of Self-Forcing and
the README naming it, the Wan2.2 config sets `generator_type: bidirectional`.
They did **not** use the causal/autoregressive rollout that Self-Forcing is
actually about — they used Self-Forcing's *codebase* to run a bidirectional DMD2
distill. So the thing to reproduce is DMD2, and the Self-Forcing framing is
partly incidental. That simplifies any reimplementation.

### 1b. Training scale — our recorded figure is CONFIRMED

Their README states it plainly: **4,000 iterations, under 48 hours, 16 A100
GPUs.** Our note was right.

Supporting detail from `configs/self_forcing_wan22_dmd.yaml`: per-GPU batch
size 1, `total_batch_size: 64` (so 16 GPUs x 4 gradient-accumulation steps),
LR 5e-7 on the student and 1e-7 on the critic, AdamW with beta1 0.0, EMA 0.99
starting at step 200, gradient checkpointing on, FSDP full-shard across student
/ teacher / critic / text-encoder, with the text encoder CPU-offloaded.
Training latent shape `[1, 31, 48, 44, 80]` = 31 latent frames x 48 channels x
44x80, i.e. **121 frames at 704x1280, exactly our pixel budget** (their h=704
w=1280 is landscape; ours is the same bucket rotated).

Why 16 GPUs and not one: three resident copies of a 5B model plus two AdamW
optimizer states. Full-parameter fp32 master weights + Adam moments for the
student alone is ~60 GB, the critic the same again, plus ~30 GB of bf16 weights,
plus Qwen/T5 and activations. Call it 150 GB+ of state before activations. This
is a cluster-shaped job as published.

### 1c. Data — the surprise, and it is good news

**The distillation is data-free in the distribution sense.** DMD2's "backward
simulation" (paper §4.5) means the student's noisy inputs are generated by
running the student itself, so no ground-truth video and no teacher-output pairs
are needed. The teacher *is* the data distribution.

The only real data requirement is **prompts, plus one still image each** for the
I2V conditioning. This is visible in the trainer: it loads a video from
`MagicData.csv`, takes the first frame, VAE-encodes that as the conditioning
latent — and sets the clean-latent variable to `None`
(`trainer/wan22_distillation.py:265-269`). The remaining 120 frames it decoded
off disk are discarded. Their 36,770-row CSV of 1920x1080 stock clips is, in
effect, an expensive way to get 36,770 prompt+frame pairs.

Consequences for us, both favourable:

- **No corpus to license.** We would train on our own approved stills and our
  own beat prompts. Every input is clean: the teacher (Wan2.2-TI2V-5B) is
  Apache 2.0 and we already run it, the images are ours, the prompts are ours.
- **Narrow is legitimate, maybe even better.** We need one visual style, one
  aspect ratio, a handful of characters. Nothing requires matching their
  generic-stock-footage diversity, and a distill that only has to cover 2D-anime
  vertical stills plausibly converges in well under 4,000 iterations. That is
  an inference, not a measured claim — but it is the main lever on the bill.

### 1d. Licence path for a clean reproduction

This is cleaner than expected. **The upstream Self-Forcing repo
(`guandeh17/Self-Forcing`) is Apache 2.0** — verified by fetching its LICENSE.
`quanhaol` forked it and relicensed *their* fork CC BY-NC-SA 4.0. So:

- the DMD/DMD2 training machinery is available to us under Apache 2.0 from
  upstream;
- what is encumbered is specifically quanhaol's Wan2.2 adaptation — the
  `wan22/` tree, the Wan2.2 score-distillation trainer, the Wan2.2 config, the
  few-step inference pipeline — and their released weights;
- so a clean build means **writing the Wan2.2 adaptation ourselves on top of the
  Apache base**: a model wrapper, the image-latent conditioning path, and the
  4-step schedule. That is a defined engineering task, not a research project.

Also checked: `GoatWu/Self-Forcing-Plus` is **CC BY-NC-SA** as well — not usable
as a base. Do not start from it.

Standing rule regardless: their published weights are off-limits for anything we
publish, and Kijai's ComfyUI support for them (their README, 2026-01-26) does
not change that — packaging does not relicense.

### 1e. What it would cost

One successful published-recipe run = 16 x 48 = **768 A100-hours**. At 2026
market rates (A100 80GB: ~$1.07–1.49/hr on-demand at budget providers, ~$0.60/hr
spot, ~$2.06 at Lambda; H100 ~$2.46/hr spot, and H100 is ~2–2.5x an A100 here,
so ~340 H100-hours):

| Route | Compute | Rough cost | Wall time |
|---|---|---|---|
| 16xA100, budget on-demand | 768 A100-hr | **~$850–1,150** | 48 h |
| 16xA100, spot | 768 A100-hr | ~$460 | 48 h + preemptions |
| 8xH100 node | ~340 H100-hr | **~$840–2,100** | ~44 h |

Spot is more viable than it looks — their trainer checkpoints and resumes with a
step-offset sampler, so a preemption costs progress, not the run.

**But one run is not the project.** Reimplementing the Wan2.2 adaptation on the
Apache base, standing up a multi-node FSDP job for the first time, and the
near-certainty of at least one throwaway run puts a realistic first attempt at
**$2,000–5,000 and one to two weeks of engineering**. For a project whose
lifetime spend is $0.40, that is not a marginal decision.

**The cheaper variant, if this is ever funded.** Train LoRA adapters on the
student and critic instead of all 5B parameters. Optimizer state collapses from
~120 GB to ~1 GB; you still need three bf16 copies of the 5B denoiser (~30 GB)
plus activations, which fits a single rented 80 GB card. Estimated **$150–500
and 4–8 days on one GPU**, no multi-node work at all. This is not the published
recipe and nobody has published a LoRA-DMD for TI2V-5B I2V specifically, so it
carries real technical risk — but community 4-step LoRAs for Wan models are
built exactly this way, and it is the only version of this idea that fits our
budget posture. It would still need a founder go.

**The $0 option, and the recommendation.** Wait. The technique is public, the
teacher is Apache, and demand for a permissive TI2V-5B distill is already
demonstrated (Kijai packaged the NC one). The lightx2v line has shipped
Apache-licensed step-distill LoRAs for Wan models before — that thread is being
read separately and is the place to check first. Patience costs nothing and this
is a fast-moving field.

### 1e-bis. CORRECTION: the payoff is ~2.2x wall clock, not 3.5x

`speed-quant.md:301` projects "14 → 4 steps = **3.5x**, projected 188s → ~54s".
**That projection assumes step count scales linearly and our own later
measurements say it does not.** From the sweep rendered 2026-08-03, recorded in
`DECISION.md:10`:

| Steps | Measured | Delta |
|---|---|---|
| 14 | 188 s | — |
| 10 | 153 s | −35 s over 4 steps → 8.75 s/step |
| 8 | 136 s | −52 s over 6 steps → 8.67 s/step |

Two independent pairs agree on **~8.7 s per step**, which implies a **fixed
overhead of ~66 s** per clip (188 − 14 x 8.7) that no step reduction can touch —
text encode, VAE encode/decode, model load/offload shuffling.

Extrapolating that fit (DERIVED-FROM-OURS, labelled as derived):

- 4 steps, still with CFG: 66 + 4(8.7) = **~101 s → 1.9x**
- 4 steps, CFG-free as Turbo is (per-pass ~4.35 s): 66 + 4(4.35) = **~84 s → 2.2x**

So the realistic prize is **188s → roughly 85–100s**, not 54s. Worth having; not
worth $1–5k and two weeks. Anyone pricing this decision should use 2.2x.

Two honest caveats: the ~66 s overhead is a two-point linear fit, not a measured
floor; and a `steps-06` clip already exists from that same sweep, so **timing the
6-step render would confirm or break this fit for free** — the fit predicts
~118 s. That is the cheapest next measurement in this whole area and nobody has
taken it.

### 1f. Their inference-time findings — there are none, and that is the finding

Asked directly: does the repo document quality costs, motion effects, or
settings guidance? **No.** I grepped the whole tree for limitations, ablations,
quality metrics, artifacts, motion discussion, known issues. There is nothing.
No paper of its own (the README's citation points at their earlier MagicMotion
work), no VBench numbers, no side-by-side, no discussion of what 4 steps costs
versus 50. Six demo videos and a training command.

So on **our frozen-frames axis specifically: zero evidence either way.** Anyone
claiming this recipe would or would not fix our motion problem is guessing.

The complete inference recipe is four lines
(`configs/inference/wan22.yaml`): the 4-step list, `warp_denoising_step: true`,
the model name. No guidance scale — because there is no CFG. Their entrypoint
resizes the input still to exactly the target h/w with LANCZOS, VAE-encodes it,
and runs 4 steps at 24 fps for 121 frames. Defaults: seed 43, 704x1280.

**One indirect signal, and it cuts against us.** The same authors' follow-up,
FlashMotion (CVPR 2026, built on this exact repo), exists precisely because
few-step distillation *hurts motion*: its abstract states that applying these
distillation approaches to trajectory-controllable generation "results in
noticeable degradation in both video quality and trajectory accuracy," and its
fix is a three-stage pipeline that retrains motion-control adapters *after*
distilling. That is scoped to trajectory control, not to our case — but it is
the authors themselves documenting that 4-step distillation and motion fidelity
are in tension. Given that our open defect is frozen frames, treat "distill to
4 steps" as a **speed** lever with a motion risk, not as a motion fix.

---

## 2. Kandinsky 5.0 I2V Lite 5s — cleanest licence in the field, wrong model for us

Verdict: **the licence is as good as advertised and the 12GB claim is real, but
this model is actively trained away from 2D animation and tops out well below
our resolution.** Its honest role is a fallback if licence pressure ever forces
us off Wan — not a candidate for our look, and not a second-box workhorse.

### 2a. The finding that settles it

The default negative prompt, hardcoded in both their T2V and I2V pipelines
(`kandinsky/i2v_pipeline.py:125`, `kandinsky/t2v_pipeline.py:128`), begins:

> `Static, 2D cartoon, cartoon, 2d animation, paintings, images, worst quality, ...`

The authors put **"2D cartoon, cartoon, 2d animation, paintings"** in the
default negative — i.e. the shipped configuration actively steers *away from*
the exact aesthetic banyan-city is made of. That is a photoreal-tuned model
telling you what it considers a defect. We could of course override the
negative, but the default reveals the training distribution's bias, and no
amount of prompt surgery moves a base distribution.

(Incidentally `Static` leads that same negative list — they have our
frozen-frames axis too, and their answer was to negative-prompt it.)

### 2b. Resolution ceiling — 464x848, not 704x1280

The I2V pipeline does not take a width/height. It derives output resolution
**from the input still**, downscaled to fit a fixed pixel budget. For the Lite
5s config (`metrics.resolution: 512`) that budget is `512*768 = 393,216` px
with dimensions rounded to multiples of 16
(`kandinsky/i2v_pipeline.py:97-99`, `:23-36`).

Our 704x1280 still is 901,120 px — **2.3x over budget**. Running the maths in
their resize function on our exact input gives **464 x 848** (aspect preserved).
Reaching 704x1280 would need a 1.51x upscale on every clip.

There is one untested lever: the `max_area` branch jumps to `1024*1024` when the
config resolution is not 512, and the *Pro* I2V checkpoint is shipped with both
an HD and an SD config pointing at the same weights — so resolution is a config
choice, not baked into a checkpoint. But **no HD config ships for Lite I2V**,
which strongly implies it was neither trained nor validated there. Forcing it
would be off-distribution guesswork.

### 2c. Speed — the distilled variants do not include I2V

This is the trap. Kandinsky advertises four tiers: SFT, CFG-distilled (2x),
diffusion-distilled into 16 steps (6x), and pretrain. **Every distilled and
no-CFG checkpoint is T2V only.** The I2V Lite 5s ships in exactly one flavour:
SFT, `num_steps: 50`, `guidance_weight: 5.0` → **NFE 100**, and a measured
**139 s on an H100** for a 5-second clip at SD resolution.

139 s on an H100 for 464x848 is not a good starting point. On a 5070 Ti 12GB —
a card several times slower than an H100 for this workload, needing offloading
that costs more time again — expect **roughly 10–20 minutes per 5-second clip**
(estimate, not measured). For comparison our production path already renders at
704x1280 on the 5090.

### 2d. Second-box fit (RTX 5070 Ti 12GB / 16GB RAM / Windows) — plausible, with caveats

Genuinely encouraging on memory. Their changelog: 2025-10-07 "the entire
pipeline now running at 24 GB with offloading"; 2025-10-19 "generation should
work on the GPUS with **12 GB** of memory," via further VAE tiling plus an
**NF4-quantised Qwen2.5-VL** from bitsandbytes. And **SDPA is a supported
attention engine** (`--attention_engine`), so no Flash-Attention build is
required — that matters a lot on Windows.

The caveats:

- The text encoder is **Qwen2.5-VL-7B-Instruct** (`download_models.py:69-71`)
  plus a CLIP. A 7B VLM alongside the 2B DiT is why offloading is mandatory,
  and offloading to **16 GB of system RAM** is the real question mark — the 12GB
  claim is about VRAM and says nothing about host RAM headroom. Our second box
  is thin exactly there.
- `expand_prompts: bool = True` by default: the pipeline calls Qwen2.5-VL to
  *rewrite your prompt using the image* before generating. For hand-tuned
  per-beat prompts that is unwanted; set it off. It also means the VLM must be
  resident, not merely available.
- Sage Attention had a known noisy-output bug when built from source as of
  2025-10-19 (their note). Use SDPA.

### 2e. Diffusers-loadable: yes

Their changelog says Kandinsky 5 Video Lite was accepted into diffusers
(huggingface/diffusers PR #12478), and a `Kandinsky-5.0-I2V-Lite-5s-Diffusers`
weight repo exists on the Hub. So it would drop into our diffusers pipeline
rather than needing their bespoke runner. Not verified by running anything.

### 2f. Licence and architecture, for the record

- **Repo code: MIT** (`LICENSE`, "Copyright (c) 2025 Kandinsky Lab"). This is
  the cleanest licence of anything we have looked at, and it is why the model
  deserved a look at all. Weight-repo terms on the Hub should be confirmed
  separately before any use — MIT on the code does not automatically cover the
  checkpoints.
- Architecture: flow-matching latent diffusion. DiT with cross-attention to
  text, model dim 1792, ff 7168, 32 visual + 2 text blocks, patch (1,2,2), 16
  latent channels. Text = Qwen2.5-VL (3584-d) + CLIP (768-d). VAE = HunyuanVideo
  3D VAE. I2V is a conditioning flag (`visual_cond: true`) on the same
  architecture. 2B parameters.
- Cadence matches ours: `time_length * 24 // 4 + 1` latent frames, 24 fps, 5 s
  → 31 latent frames / 121 frames.
- Repo is alive (last commit 2026-01-19) and shipped I2V 2025-11-15, Pro
  2025-11-20, camera-control LoRAs 2025-11-24. Those **camera LoRAs** are the
  one genuinely interesting adjacent artifact given our camera-lock work,
  though they are Kandinsky-specific and do not transfer to Wan.
- Kandinsky Pro I2V exists (model dim 4096, ff 16384, 60 blocks) but T2V Pro at
  HD measures 1241 s per 5 s clip on an H100. Out of scope for our hardware.

---

## 3. Open-Sora — CONFIRMED completeness-tier, and worse than we recorded

Verdict first: **our note was right and if anything generous.** Nothing in the
repo justifies more attention. Do not spend a GPU-hour on it.

**It is a dead project by video-model standards.** Last *model* release is
Open-Sora 2.0, March 2025. The most recent commit on `main` (`7ad6a96`,
2026-04-09) is a README edit. Seventeen months without a model while Wan, LTX
and Kandinsky all shipped generations.

**Memory: does not fit our 24GB box, not even close.** From their own
Computational Efficiency table (`README.md`), text-to-video on H100/H800 at 50
steps, single GPU, peak GPU memory:

| Resolution | 1 GPU | 2 GPUs | 4 GPUs | 8 GPUs |
|---|---|---|---|---|
| 256x256 | 52.5 GB (60 s) | 44.3 GB | 44.3 GB | — |
| 768x768 | 60.3 GB (1656 s) | 48.3 GB | 44.3 GB | 44.3 GB |

The 256x256 single-GPU figure of 52.5 GB is **with `--offload True` already
on** — that is the reduced number, not the naive one. Our recorded "44GB+ peak"
turns out to be the *multi-GPU* figure; the number that matters for a
single-card box is 52.5–60.3 GB. A 24GB 5090 is out by a factor of ~2.2, and
the 768px path takes 28 minutes per clip on an H100.

**Why it is so heavy** (`configs/diffusion/inference/256px.py`): the denoiser
is an 11B flux-architecture DiT (hidden 3072, 24 heads, 19 double + 38
single blocks) and it is *stacked on top of* T5-v1.1-XXL (context dim 4096,
~11B params) plus CLIP-ViT-L plus the HunyuanVideo VAE. Four large models
resident. Compare Wan2.2-TI2V-5B: one 5B denoiser and a T5 we already fit.

**I2V support is real but not an advantage.** `--cond_type i2v_head` does
first-frame conditioning, which is our exact use case, and the README says the
model is "optimized for image-to-video." There are also `i2v_tail`,
`i2v_loop` (connect two images) and two `v2v` extension modes — a genuinely
richer conditioning menu than Wan's. It does not matter, because the memory
floor makes all of it unreachable.

**Vertical: yes in principle.** `sampling_option.aspect_ratio` accepts
`16:9`, `9:16`, `1:1`, `2.39:1`, and `num_frames` any `4k+1` up to 129. But
resolution is bucketed as `"256px"` or `"768px"` (fixed pixel budget, aspect
chosen within it), so there is no path to our exact 704x1280 — we would be
taking whatever their 9:16 bucket is and rescaling.

**Other frictions, for the record.** Default 50 steps. Guidance is split
text 7.5 / image 3.0 with "oscillation" toggles (`text_osci`, `image_osci`) we
would have to learn. Prompt refinement and the dynamic motion-score evaluator
both call the OpenAI API (`OPENAI_API_KEY`) — optional, but it tells you where
the project's head is. Inference is `torchrun`-based with ColossalAI tensor/
sequence parallelism, i.e. built for multi-GPU clusters, not one desktop card.
Install wants `xformers` pinned to a CUDA 12.1 wheel and `flash-attn` compiled
from source — on Windows with a Blackwell card that is its own weekend.

**One thing worth remembering.** `configs/diffusion/inference/high_compression.py`
swaps the Hunyuan VAE for a DC-AE `f32t4c128` (32x spatial compression vs 8x)
with spatial *and* temporal tiling, and drops parallelism entirely. That is the
architectural idea that makes long/large video cheap, and it is the same
direction LTX-2 went. Worth knowing as a *concept*; not worth chasing here,
since the 11B denoiser above it is still 11B.

**Licence, since it is the one clean thing:** repo code is Apache 2.0.
Irrelevant given the above, but noted so nobody re-checks.

---
