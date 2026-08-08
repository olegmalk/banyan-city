# ACTION PLAN — from seven source dossiers to tomorrow's renders

**2026-08-04.** Synthesis of the seven upstream source reads in this directory.
Deadline: **Wednesday evening 2026-08-05.** Production model: Wan2.2-TI2V-5B,
our diffusers pipeline, RTX 5090 laptop (24GB VRAM, 64GB RAM as of today,
Windows). $0 budget, watch-only publication, founder screens everything,
**ONE SAMPLE BEFORE ANY BATCH** applies to every row below.

Citation tags: `[wan22]` wan22-official-source.md · `[kijai]` kijai-source.md ·
`[w2gp]` wan2gp-source.md · `[lx2v]` lightx2v-vbench-source.md · `[ltx]`
ltx2-source.md · `[aniso]` anisora-source.md · `[misc]`
misc-candidates-source.md · `[dec]` DECISION.md · `[lic]` models-licence.md.

Three standing gates for everything below: any **new weight file** goes through
`licence_gate.py` / `vet_model.py` first; **step count is a taste call** (R4,
founder); **money is founder-reserved** and nothing here needs it.

---

## 1. Tomorrow's test matrix

Run order is chosen so the cheapest, highest-evidence things happen on the
pipeline that already works, before anything that might not even load. Every row
is ONE clip on ONE beat (use the beat with the live complaint — beat 1), same
seed throughout, screened before the next row starts.

### T0 — three prints, no render. Gate, not a sample. (5 min, 0 GPU)

Do not trust a single number tomorrow until these are on screen:

1. `torch.__version__`. **Avoid 2.8.0 and 2.9.0**: upstream reports host-RAM
   leaks when switching models on 2.8.0 and Conv3D perf regressions that make
   VAE VRAM explode on 2.9.0 `[w2gp §5.3]`. Those are exactly the two things
   we would be measuring tomorrow (two-expert swapping; a 22GB VAE spike).
2. `pipe.transformer.dtype` — the transformer ships fp32 on disk and our
   runtime dtype has never been verified `[dec §3 cause 5]`.
3. `pipe.scheduler.config.shift`, `pipe.scheduler.timesteps`, and (A14B path)
   `boundary_ratio`. We never set shift on the 5B path and inherit whatever the
   HF `scheduler_config.json` ships `[wan22 §1c]`.

Also, before any A14B VRAM or speed number: set **CUDA Sysmem Fallback Policy =
Prefer No Sysmem Fallback** on python.exe. Nobody upstream disables it
`[w2gp §5.2]`, which means a "successful" A14B run that is 5x slower than
expected is the signature of silent spill to host RAM, not of offload working.
One click, one-click revert, and it converts an invisible tax into a legible OOM.

### T1 — 5B `shift`, three samples. The one untested knob with the most evidence. (~12 min)

| | value | source |
|---|---|---|
| A | whatever T0 printed (baseline) | ours, unverified `[wan22 §1c]` |
| B | **5.0** | Alibaba's own 720p value for TI2V-5B `[wan22 §1]` |
| C | **8.0** | kijai's shipped 5B I2V example `[kijai §3, §5]` |

Hold everything else: 14 steps, guidance 5.0, 704x1280, current frame count,
same seed, same prompt. Expected ~248s/beat, peak 22.9/25.7GB `[dec §2]`.
If T0 prints 5.0, swap C's slot for **3.0** (Alibaba's 480p value, and FastWan's
`flow_shift`) so the sweep still brackets three regimes.

Why first: shift is the only parameter that decides how much of the trajectory is
spent in the high-noise regime — i.e. establishing large-scale *motion* — versus
refining detail, and it is one of only three motion levers Wan 2.2 exposes at all
(prompt, negative prompt, shift; there is **no** `motion_bucket_id`, no amplitude
scalar, confirmed by exhaustive grep) `[wan22 §5c, §7]`. Three independent
upstreams give three different values for the same model. We have never measured
any of them.

### T2 — restore `画面` to the negative prompt. (~4 min)

Our `NEG` drops **four** of Alibaba's 28 terms, not the three the comment names.
The undocumented fourth is `画面` (picture / flat frame), which sits in the
*quality* cluster next to 风格/作品/画作 (style/artwork/painting) rather than the
anti-stillness cluster — suppressing it pushes *away* from flat-picture-ness, so
removing it pushed toward it `[wan22 §5a]`. Sharper than the dossier knew: the
other three dropped terms **are** re-added per beat through `ANTI_STATIC`
(`pipeline/video_task.py:367`); `画面` has no re-add path anywhere, so it is the
only one we suppress unconditionally.

**Run it alone.** Do not combine with `--no-shake-neg` — that is a separate live
suspect and confounding the two wastes both samples `[wan22 §5a]`.

### T3 — the prompt contract on the 5B path. (~4 min, free)

**Four independent author groups specify the same I2V prompt shape, and we apply
it on the AnimeGen path only, not on the 5B production path** `[wan22 §7.2]`:

- Alibaba: "emphasize potential dynamic content"; "avoid adding static scene
  descriptions — if the user's input already describes elements visible in the
  image, **remove those static descriptions**"; ≤100 words. Their nine worked
  examples are 10-25 words of pure motion `[wan22 §5b]`.
- Lightricks: "Describe only changes from the image. Don't reiterate established
  visual details. **Inaccurate descriptions may cause scene cuts.**" And: "DO NOT
  invent camera motion unless requested." Present-progressive verbs, restrained
  language `[ltx §3]`.
- AniSora: same clause, verbatim `[aniso §5]`. AIdeaLab: motion-only
  (already followed at `wan_i2v.py:412-414`).

Sample: take beat 1's `motion.yaml` direction, strip everything already visible
in the approved still, keep the verbs, cap at 100 words, same seed. If it helps,
the second free sample is Alibaba's supported **empty-prompt** mode (`--prompt
''` routes to a dedicated system prompt whose brief is "bring the image to life")
`[wan22 §5b]`.

### T4 — SageAttention 2.2, separate venv. (~20 min setup + 4 min render)

Prebuilt Windows wheel, no compile step, for RTX 40/50xx:
`sageattention-2.2.0+cu130torch2.9.0andhigher.post4-cp39-abi3-win_amd64.whl`
from `woct0rdho/SageAttention`, plus `triton-windows` `[w2gp §5.3]`. Claimed
~35% on an RTX 5090 Laptop 24GB `[dec §2, CLAIMED]`; upstream's default
attention preference is `sage2 > sage > sdpa` with sdpa as the *last* resort
`[w2gp §6.2]`. Separate venv because the wheel pins the torch line.

Three things to get right, all from source:

- **On sm_120 force the Triton kernel.** lightx2v explicitly routes compute
  capability `(12,0)` to `sageattn_qk_int8_pv_fp16_triton` rather than the CUDA
  dispatch — the maintainers found the compiled CUDA path unreliable on this
  exact card `[lx2v §3]`.
- **Coerce k and v to q's dtype, and never hand fp32 to sage** — kijai's two
  guards, worth copying verbatim `[kijai §4]`.
- **Every shipped Wan 2.2 workflow runs fp16 activations** (`base_precision=
  fp16_fast`, plus `torch.backends.cuda.matmul.allow_fp16_accumulation = True`),
  never bf16. Sage's int8-QK quantisation is calibrated around fp16 ranges; bf16
  into sage is not a path any known-good workflow exercises `[kijai §4]`.

### T5 — FastWan 3-step LoRA on the model we already run. (licence gate + ~2 min render)

`Wan2_2_5B_FastWanFullAttn_lora_rank_128_bf16.safetensors` — a LoRA on top of our
existing TI2V-5B base (`"URLs": "ti2v_2_2"`, i.e. no new base weights), whose own
description names **121x704x1280**, our exact frame count and resolution
`[w2gp §6.1]`. Recipe, complete: **3 steps, guidance_scale 1, flow_shift 3**,
121 frames, 704x1280. Do not carry our current shift over.

Two warnings that decide how to read the sample:

- **At guidance 1 the entire negative prompt is inert.** The uncond pass is
  simply not run, so every anti-static and anti-shake term we have tuned stops
  applying — confirmed independently in three codebases `[kijai §5, §6b]`,
  `[aniso §6]`, `[lx2v §1a]`.
- **Distill LoRAs are documented to cause slow motion**, which is the exact
  defect the K recipe was rejected for. Upstream's own fix is not more prompt
  amplitude: it is spending 8 steps with a real guided phase 1 and the LoRA
  switched **off** for it `[w2gp §3.3]`; the same authors' follow-up paper exists
  because few-step distillation hurts motion `[misc §1f]`.

Secondary, if the LoRA disappoints: kijai ships a merged
`Wan2_2-TI2V-5B-FastWanFullAttn_bf16` at 30 steps / cfg 5.0 / shift 8.0 /
`flowmatch_pusa`, i.e. as a plain checkpoint swap with no re-tune `[kijai §3]`.

### T6 — A14B #1: `aidealab/AnimeGen-I2V`, the anime candidate already plumbed. (~30 min incl. load)

This is the A14B to test first: our pipeline already has the path (fp8 layerwise
casting, `wan_i2v.py:133,165`), it ships a real stock Apache-2.0 LICENSE file
with no added clauses, and it is tagged `commercial-use` `[dec §7]`.

- **Change `shift` 3.0 → 5.0.** At shift 3.0 and 4 steps, timestep 2 lands at
  t=899 against a boundary of 900 and flips to the *detail* expert — the
  layout-and-motion expert would run once in four. At 5.0 the split is a clean
  2/2, proportionally close to the 15/40 of Alibaba's reference run
  `[wan22 §4]`. 3.0 is their **480p** recommendation; we render 720p-class.
- **Print `scheduler.timesteps` and `boundary_ratio` before spending the
  render.** Under diffusers' grid (σ_max 1.0, not 0.999) the shift-3.0 4-step
  timesteps work out ~`[1000, 857, 600, 3]` — same 1-of-4 conclusion, different
  integers, but verify rather than assume `[wan22 §4]`.
- Steps 4 (its own example), guidance 1, boundary 0.900, motion-only prompt.
  Its example is 832x480; 704x1280 is our target and for I2V the size argument
  only sets a max-area budget `[aniso §2]`.
- **Expect memory-bound, not step-bound.** ~14.3GB per expert at bf16, two
  experts = 28.6GB on a 24GB card; fp8 storage halves it to ~7GB each
  `[kijai §2]`. There is **no official 24GB recipe for A14B** — Alibaba's
  single-GPU A14B command is documented as **80GB**, and for 24GB they point at
  layer-by-layer offload + fp8, i.e. the approach we already use `[wan22 §2a, §7]`.
- Per-step cost is not just 14B vs 5B: the A14B's VAE stride is (4,8,8) against
  the 5B's (4,16,16), so 720x1280x81 is ~4.6x more latent tokens per frame-step
  `[wan22 §1]`. And the A14B conditions by a 4-channel mask concatenated to
  `VAE([image, zeros])` where the 5B conditions by latent inpainting — habits
  tuned on the 5B do not transfer `[wan22 §6c]`.

### T7 — A14B #2: stock Wan2.2-I2V-A14B + lightx2v Lightning, only if T6's look fails.

Authoritative recipe, from the org that trained the weights `[lx2v §1]`:

- **4 steps. Sigmas `[1.0, 0.9375, 0.8333, 0.625]`, passed explicitly** (plus the
  trailing 0.0). Their config's `denoising_step_list [1000, 750, 500, 250]` are
  **indices into a 1000-point shift-5.0 grid, not timesteps** — handing diffusers
  `timesteps=[1000,750,500,250]` gives a much steeper, wrong trajectory. This is
  the one thing a diffusers reimplementation gets wrong `[lx2v §1b]`.
- `sample_shift` 5.0; plain flow-matching Euler; expert switch after step 2,
  equivalent to `boundary = 0.900` — both conventions land on the same 2+2
  `[lx2v §1c]`.
- **Both LoRAs at strength 1.0**, rank 64:
  `wan2.2_i2v_A14b_{high,low}_noise_lora_rank64_lightx2v_4step_1022.safetensors`.
  There is no "0.5 high / 1.0 low" folklore anywhere in their repo. **Do not copy
  kijai's 3.0 on HIGH** — that is a workaround for using a *Wan 2.1* LoRA on a
  2.2 expert; with the native 2.2 LoRA strength goes back to 1.0 `[kijai §3]`.
- **CFG off, `guidance_scale=1`. Ignore the `[3.5, 3.5]` in their config** — it
  is a dead value; the two lines that would have applied it are commented out in
  the shipped source `[lx2v §1a]`.
- 81 frames, 720x1280 or 480x832.
- **The one thing to steal:** kijai's per-step CFG list `[2.0, 1.0, 1.0, 1.0]` —
  one step of real classifier-free guidance at the highest noise level, then
  distilled cfg 1. Costs one extra forward out of the run (~8%) and is the only
  way the negative prompt applies at all in a distilled pipeline, at exactly the
  step where "is this a video or a still" is decided `[kijai §6b]`.
- If it returns frozen or slow-motion: the upstream-documented fix is 8 steps,
  3 phases, **both LoRAs off in phase 1** with real CFG 3.5 there
  (`switch_threshold` 985 then 800, `model_switch_phase: 2`) `[w2gp §3.3]`.

### T8 — AniSora V3.2, only if the weights are already converted. Otherwise cut.

**Hard gate:** the download is fp32, ~57GB per expert / ~126GB for the pair, and
`from_pretrained` loads an expert whole — a single fp32 expert nearly fills 64GB
of RAM, and offload wants both resident on the host. **Plan on converting to
bf16/fp8 on disk before the first run**; do not expect the stock path to work
`[aniso §4]`. If that conversion has not already happened, this row does not fit
in tomorrow.

**SUPERSEDED 2026-08-08 — do not act on the paragraph above, and do not re-run
its check.** Both halves have been answered. (1) *Has someone converted it?* Yes,
but not us: published quants exist — QuantStack Q8_0 15.88GB/expert and Q4_0
9.03GB, terracottahaniwa fp8 14.31GB (MODEL-COMPARISON.md 2026-08-07). The row is
**not cut**. (2) *Do we hold a conversion on disk?* **No — and no fp32 either.**
The 5090 was listed on 2026-08-08: the output dir `anisora-v3.2-bf16` is empty,
the HF cache holds 11.89GB of text encoder, VAE and index files with zero
transformer shards, `anisora-convert.cmd` never ran (no log exists) and its task
is archived. The fp32 fetch **failed** on 2026-08-05 — six attempts, all
`The file is too large to be downloaded using the regular download method.
Install hf_xet` — so **converting the fp32 ourselves is not a slow option on this
box, it is a closed one.** Take a published quant. Live blocker is the loader, not
the weights; see STATE.md 2026-08-08 (night) and MODEL-COMPARISON.md §1 T8.

Recipe, if it runs: **8 steps native — no LoRA anywhere in the V3.2 inference
path, the few-step capability is baked into the weights** — shift 5, guidance 1,
boundary 0.900 (3 high-noise steps, 5 low, exactly one expert swap), 81 frames
@ 16fps, use the **8x+1** frame rule not 4n+1 `[aniso §2, §4]`. Architecture is
stock Wan2.2-I2V-A14B and for a single first frame their conditioning is
mathematically identical to official Wan — **drop-in for our A14B path**
`[aniso §2, §3]`.

Prompt format is theirs and mandatory:
`[long detailed English description] aesthetic score: 5.5. motion score: 3.0.
There is no text in the video.` The no-text clause is marked Mandatory and we
want it (we burn our own captions in `render_t3`). **`motion score` is a trained
conditioning token, recommended 2.0-4.0 — that is the right first knob to sweep,
and a better lever than prompt adjectives** `[aniso §5, §6]`. Do **not** use
their prompt extender: it runs stock Wan system prompts that never emit the score
tokens the weights were trained on, and it silently substitutes content on a
topic list, which is incompatible with §7.2 provenance `[aniso §6]`.

**Expectation management, because this is the model we most wanted to work:**
their own published benchmarks put AniSora *below* vanilla Wan on our critical
axis — VBench Motion Score **45.59**, the lowest row in their own table, against
real-anime ground truth at 56.05; and on their own benchmark AniSora-V2 scores
**50.34 Visual Motion against Wan-2.1's 61.88** — while winning every consistency
metric in the same row. That is the consistency-for-motion trade you would expect
from a model tuned for character stability. No V3.x row is published. **The
burden is on one sample to disprove it** `[aniso §5]`. Also note their reference
recipe's guidance 1 disables the negative prompt, so none of our anti-stillness
work transfers to it `[aniso §6]`.

### Tonight's LTX-2.3 sample — how to read it, and the two branches

- **A single-stage 8-step render at final resolution reproduces stage 1 only,
  which upstream runs at HALF the target size.** Their "8 steps" is 8 + 3 across
  two resolutions with a separate 2x spatial-upsampler checkpoint in between, and
  stage 2 is a latent img2img refine at strength 0.909. So **soft and
  under-detailed is the predicted off-recipe failure, not the model's verdict**
  `[ltx §1]`.
- The sigmas must be passed explicitly:
  `[1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875]`.
  `num_inference_steps=8` produces a completely different trajectory — five of
  their eight steps sit between σ 1.0 and 0.975 `[ltx §1]`.
- Guidance 1.0 is correct and **the negative prompt does nothing** on the
  distilled path (no guider exists in it) `[ltx §1]`. Image conditioning
  strength 0.8-0.9, not 1.0 — higher means more locked to the still `[ltx §3]`.
- Two free knobs diffusers will not do for us: the conditioning still is
  deliberately **round-tripped through libx264 at CRF 33** before VAE encoding, a
  domain match to compressed training frames — a clean PNG is out of distribution
  by their own reckoning; and both axes must be /64 (704x1280 is legal)
  `[ltx §3]`.
- Memory: `OffloadMode.NONE` does not fit (~28GB stated, and that reads like the
  19B figure); **CPU offload at ~36GB RAM + ~5GB VRAM is upstream's answer to our
  box** and fits comfortably on 64GB. Critically, **Gemma-3-12B and the 22B
  transformer are never co-resident upstream** — each stage builds its model, runs,
  and frees it via `.to("meta")`. Encode the prompt, free the encoder, *then*
  build the transformer, or we OOM for reasons unrelated to the transformer. Set
  `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`; tiled VAE decode is on by
  default upstream (768px/64 overlap spatial, 80/24 temporal) `[ltx §4]`.
- **If it comes out green, grey or monochrome: do not debug our pipeline first.**
  Their SDPA priority list is `CUDNN > FLASH > EFFICIENT > MATH`, and cuDNN
  attention is the historical source of silent wrong-output on brand-new
  architectures. They also *deliberately refuse* FlashAttention-4 on consumer
  Blackwell (sm_120), citing known regressions. The one-line A/B is forcing
  `EFFICIENT_ATTENTION` (or `MATH`, slow but definitionally correct) around the
  denoise loop. Grayscale means near-constant chroma planes, which points at the
  latents, upstream of the encoder `[ltx §5]`.

---

## 2. Production-model fixes, ranked by evidence x cheapness

These are things the dossiers show we do **wrong or unmeasured on the 5B pipeline
that already works**. Type column: **SAMPLE** = a recipe change, needs one clip
screened (ONE SAMPLE rule); **MECH** = mechanically safe, output unchanged or
strictly better, no screening needed.

| # | Fix | Type | The experiment that proves it | Cost | Might fix | Cite |
|---|---|---|---|---|---|---|
| 1 | **`shift` never set on the 5B path** — three upstreams give 5.0 / 8.0 / 3.0 for the same model | SAMPLE (T1) | 3 clips, one beat, one seed, shift the only variable | ~12 min | frozen frames — shift is the *only* knob that redistributes steps between the motion regime and the detail regime | `[wan22 §1c, §7]` |
| 2 | **`画面` — the fourth, undocumented dropped negative** | SAMPLE (T2) | 1 clip with it restored, alone, *not* with `--no-shake-neg` | ~4 min | flat-picture / frozen look. The other three dropped terms are re-added per beat by `ANTI_STATIC`; this one never is | `[wan22 §5a]` |
| 3 | **Prompt contract not applied on the 5B path** (motion-only, statics deleted, ≤100 words) | SAMPLE (T3) | 1 clip, beat 1's direction stripped to verbs | ~4 min | scene cuts, invention, stillness. **Four** independent author groups specify the same shape | `[wan22 §5b]` `[ltx §3]` `[aniso §5]` |
| 4 | **No optimised attention backend** — Alibaba's DiT calls flash-attn *directly*; we take whatever diffusers defaults to | SAMPLE (T4) | prebuilt Sage wheel in a separate venv, same beat + seed | 20 min + 4 min | ~35% per-step. Diagnosis is free: check what the attention processor resolves to | `[wan22 §6b]` `[w2gp §5.3, §6.2]` |
| 5 | **VAE decode in explicit fp32; the authors run the decode under bf16 autocast** | SAMPLE | 1 clip with the decode under `autocast(bf16)`; inspect for banding/colour shift by eye | ~4 min | our **one hard OOM** (2026-08-03, `wan_i2v.py:94-101`). Not a free swap — diffusers upcasts the Wan VAE deliberately | `[wan22 §6b]` |
| 6 | **VAE tiling may be pure cost on the 5B** | SAMPLE (measurement) | tiling off, one clip, record peak VRAM + wall time | ~4 min | wall time. Upstream's heuristic returns `tile_size = 0` for a ≥24GB card below 1920x1088, and for the 2.2 VAE their tiled *encode* is dead code (`if tile_size > 0 and False`). **Do not touch this on the AnimeGen/A14B path** — it fixed a real OOM there | `[w2gp §4.1, §6.6]` |
| 7 | **`noise_aug_strength` — noise on the reference image pixels before encoding** | SAMPLE | 1 clip at a small value | ~4 min | frozen frames. Upstream's tooltip names our symptom: "some noise can add motion and give sharper results" | `[kijai §6a]` |
| 8 | **int8 the text encoder** | SAMPLE | quantise the loaded T5 with `optimum-quanto`, ~20 lines, 1 clip | ~1 h + 4 min | ~11.4GB of resident VRAM. Ranked "do first" upstream; needs a sample because the embeddings change numerically | `[w2gp §7 #1]` |
| 9 | **Sysmem fallback not disabled** on python.exe | MECH (T0) | n/a — one control-panel toggle | 2 min | converts an invisible paging tax into a legible OOM. Mandatory *before* trusting any A14B number | `[w2gp §5.2]` `[dec §3 cause 2]` |
| 10 | **torch version unverified** | MECH (T0) | one print | 1 min | 2.8.0 leaks host RAM on model switch; 2.9.0 makes VAE VRAM explode — the two things we measure tomorrow | `[w2gp §5.3]` |
| 11 | **`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` not set** | MECH | n/a | 1 min | fragmentation stalls | `[ltx §4]` |
| 12 | **Resize squashes instead of aspect-preserving LANCZOS + centre crop** | MECH | n/a | 15 min | nothing today (our stills are true 9:16); a silent trap the moment one is not | `[wan22 §6c]` |
| 13 | **Cache hygiene: we call `empty_cache()` per step** | MECH | n/a | ~15 lines | a per-step tax plus the fragmentation stalls of 2026-08-02. Upstream only empties when reserved ≥0.9·capacity **and** allocated ≤0.70·reserved, rate-limited to once per 200ms | `[w2gp §1.6]` |
| 14 | **Streaming VAE decode to CPU uint8** | MECH | before/after peak VRAM on the same clip | low-medium; plain PyTorch over the VAE's existing `feat_cache`, no mmgp | makes decode VRAM independent of clip length — kills a whole class of OOM | `[w2gp §4.3]` |
| 15 | **Prequantized single-file int8 checkpoint** | MECH | bake once, then load forever | ~1 h | roughly half the bytes read off disk, attacking the ~66s fixed cost | `[w2gp §6.5]` |
| 16 | **The ~66s fixed overhead itself** — batch path + persistent worker | MECH | queue one task with `beats: "1,2"` instead of two single-beat tasks | 0 (the code path exists, `video_task.py:818`) | 248s → ~200s/beat. Note the ONE SAMPLE rule means we pay the 66s on every screening clip regardless; the win is on the eventual 15-beat run | `[dec §3 cause 1]` `[w2gp §6.5]` |
| 17 | **Our `NEG` comment says three dropped terms; it is four** | MECH | n/a | 1 min | records honesty | `[wan22 §5a]` |

Two clarifications worth having before anyone reaches for them:

- **kijai's other three motion knobs do not port to the 5B unchanged.**
  `start_latent_strength`, `end_latent_strength` and `augment_empty_frames`
  operate on the A14B/Wan-2.1 `y` conditioning stack `[kijai §6a]`. The 5B has no
  `y` — it conditions by **latent inpainting**: the first latent frame is
  overwritten with the image latent before the loop *and again after every step*,
  with a spatially-varying timestep handing the conditioned region t=0
  `[wan22 §6c]`. The honest 5B analogue of "weaken the anchor" is relaxing that
  per-step re-injection, which is a real code change, not a knob. Only
  `noise_aug_strength` (row 7) ports as-is, because it acts on pixels before the
  VAE. Worth knowing precisely, since "first frame repeated 81 times" is exactly
  an over-strong anchor.
- **Anything that moves us to guidance 1 disables our entire negative prompt** —
  the uncond forward is not run, so every anti-static and anti-shake term stops
  applying. Confirmed independently in three codebases `[kijai §5, §6b]`,
  `[aniso §6]`, `[lx2v §1a]`. If we go distilled, kijai's step-0 CFG spike is the
  only way any of that machinery survives.

---

## 3. Metrics upgrade

Our motion figure is a **median frame-difference**, and the dossiers explain
mechanically why it misreads our exact failure. Two changes, ~half a day total,
$0, ~350MB of weights, all local — it runs on the M1 `[lx2v §5, §6]`.

**3a. Dynamic degree: RAFT optical flow with a top-5% statistic.** VBench's whole
method, 164 lines: resample frames to ~8fps (`interval = max(1, round(fps/8))`);
RAFT with `iters=20` on each consecutive pair; per-pair score = flow magnitude
`sqrt(u²+v²)` per pixel, then **the mean of the largest 5%**; threshold
`6.0 * (short_side/256)`; a clip counts as moving if `round(4*n/16)` pairs clear
it. For our 704x1280 at 81 frames/16fps that is: ~41 sampled frames, threshold
16.5px, at least 10 of ~40 pairs must clear it `[lx2v §5]`.

Why it replaces ours, on two counts, both in VBench's favour:

- **Flow, not pixel difference.** Frame-diff conflates motion with exposure
  drift, grain, compression breathing and fades. A clip that flickers in
  brightness while standing perfectly still scores high on frame-diff and ~0 on
  flow.
- **Top 5%, not the median — this is the one that matters.** A median over all
  pixels, against a largely static anime background, under-credits real subject
  motion and over-credits whole-frame shimmer. That is *structurally* the failure
  we have been chasing: it is how the K recipe passed our own metric and was then
  rejected by eye as "literally just frozen frames" `[lx2v §5]`.

Implementation notes: use **torchvision's `raft_large` (`C_T_V2` weights, the
same Chairs+Things recipe as VBench's `raft-things`)** rather than vendoring their
copy — VBench fetches its checkpoint from a 2021-vintage Dropbox link. Keep the
**continuous per-pair series**, not their boolean: every non-frozen clip returns
`True`, so the boolean cannot rank two candidate recipes. And because torchvision's
weights are not bit-identical to theirs, **do not publish our numbers as "VBench
Dynamic Degree"** `[lx2v §5]`.

**3b. Invention/drift: VBench's feature space, our aggregation.**
`check_invention.py` already has the right *shape* — distance from frame 0 over
time, `return_ratio` / `monotonic` / `area_ratio` / `spread_ratio` — computed on
96x171 contrast-normalised grayscale. The upgrade is swapping that pixel distance
for **DINO ViT-B/16 cosine distance** (robust to lighting, grain and global
shifts; sensitive to content identity) and keeping every one of our statistics
`[lx2v §6]`.

**Do not adopt VBench's `i2v_subject` aggregation — it would be a downgrade on
precisely our axis.** Its conformity term is
`0.4*max(cos(image, frame_i)) + 0.3*mean(consec) + 0.3*min(consec)`, and `max`
is pinned near 1.0 by frame 0 alone for any model that faithfully reproduces its
conditioning image (Wan does). So in practice their published I2V metric is
mostly a *smoothness* metric, and a clip can start on the approved still, invent
an entirely different scene, and still score well provided it drifts smoothly
`[lx2v §6b]`. Our "does it return toward the first frame" instinct is sharper
than the field's published version.

Cost: DINO ViT-B/16 ~330MB (or timm's `vit_base_patch16_224.dino` for the same
weights without a runtime git clone); transforms are `Resize(224)`
(antialias=False, no centre crop) + ImageNet mean/std. **Do not `pip install
vbench`** — its pins (`numpy<2.0.0`, `transformers==4.33.2`, `decord`,
`detectron2`) would wreck the render env. Extract the two metrics `[lx2v §5, §6]`.

**And do not attempt an official VBench-I2V submission.** `i2v_subject` alone is
246 prompts x 5 samples = 1,230 clips; the full suite is several thousand *per
model*, their conditioning stills are photographic 4K, and **9:16 vertical is not
among their supplied crops**. The evaluation is free; only their prompt suite is
expensive — so run the metrics on our own 15 beats via `mode='custom_input'`
`[lx2v §7]`.

---

## 4. Records corrections

Things the dossiers overturn in our own written records. Each needs the record
edited, not just noting here.

1. **REFUTED BY MEASUREMENT 2026-08-07, not merely uncorroborated — running T4
   settled this.** At our own attention shape (8160 tokens, 24 heads, head_dim
   128) on this card, `sageattn_qk_int8_pv_fp16_cuda` returns output
   **uncorrelated with torch SDPA: cosine similarity −0.0002, relative error
   5468%**. It raises nothing, produces no NaN, runs 38-53x "faster", and
   reproduces its garbage bit for bit across runs — silent corruption, the worst
   available failure mode, and it is what our records recommended. The **Triton**
   kernel is correct (cos 0.99991) and is what the measured T4 rows used;
   lightx2v's routing of capability `(12,0)` away from the CUDA dispatch is
   thereby confirmed on hardware rather than on their say-so. The bf16 worry below
   did **not** materialise: bf16 and fp16 score within 0.03% of each other on
   every kernel, and our bf16 pipeline rendered clean. Evidence:
   `bench-platform/t4-sage-fidelity-20260807.txt` §0. The original note follows,
   for the record.
   **The SageAttention black-frames note is uncorroborated.** We have
   `sageattn_qk_int8_pv_fp16_cuda` written down as "the community's fix" for
   Wan+Sage black frames (`[dec §3 cause 3]`, `[dec §4]`). kijai's repo — the
   source that note points at — **never names that function**; an exhaustive grep
   for `qk_int8|pv_fp16|pv_fp8|sageattn_qk` finds it only inside an unrelated
   vendored third-party directory. Their known-good integration is "call
   `sageattn()` with `tensor_layout="NHD"` and let the package dispatch"
   `[kijai §4]`. **Relabel ours as unverified.** Two better-sourced leads
   replace it: lightx2v deliberately routes compute capability `(12,0)` — our
   card — to the **Triton** kernel `sageattn_qk_int8_pv_fp16_triton`, i.e. the
   maintainers found the compiled CUDA path unreliable on sm_120 `[lx2v §3]`;
   and every shipped Wan 2.2 workflow feeds sage **fp16** activations with
   `allow_fp16_accumulation`, never bf16, which is what we would be doing
   `[kijai §4]`.
2. **AniSora's licence is now resolvable, and it is not plain Apache-2.0.** Our
   records carry it as `apache-2.0` tag with no licence text, "unverifiable"
   (`[dec §7]`, `[lic]`). The GitHub repo carries a real 214-line `LICENSE`: the
   stock Apache 2.0 body **plus an appended bilibili "Model License Agreement"
   with six additional restrictions** (`LICENSE:203-214`), and that file governs
   the *weights*, not just the code. Five of the six are scoped to
   fine-tuning/retraining, which we do not do — so **for inference-and-publish
   our effective terms are Apache-2.0** — but clause 4 (indemnity for "all
   activities involving this model") is not retraining-scoped. **Correct
   provenance string: "Apache-2.0 plus bilibili Model License Agreement
   additional restrictions."** Do not label it plain apache-2.0 `[aniso §1]`.
3. **The Lightning LoRA records need three fixes** `[lx2v §1, §1d]`,
   `[kijai §3]`:
   - **Strength is 1.0 on both experts**, per the org that trained them. There is
     no "0.5 high / 1.0 low" anywhere in their repo. kijai's **3.0 on HIGH is a
     workaround** for running a *Wan 2.1* lightx2v LoRA on a 2.2 high-noise
     expert; with the native Wan2.2-Lightning LoRA it goes back to 1.0.
   - **`[3.5, 3.5]` in their config is a dead value** — the two lines that would
     apply a per-expert guide scale are commented out in the shipped source. Do
     not copy it into a diffusers `guidance_scale`.
   - **Newer weights supersede the ones every config cites.** The `_1022` rank-64
     LoRAs are what `configs/` reference; the README announces 720p-trained
     `..._4step_720p_260412` weights claiming better fine detail and texture —
     but those are **full merged checkpoints, not LoRAs**, so that improvement is
     only available by swapping the whole transformer. There is no 720p LoRA.
4. **Our `NEG` comment undercounts the dropped terms.** It says the official list
   contains three anti-stillness terms and names them; we drop **four**. The
   fourth is `画面` `[wan22 §5a]` — and unlike the other three it has no per-beat
   re-add path through `ANTI_STATIC` (`video_task.py:367`), so it is suppressed on
   every clip. Fix the comment whether or not T2 changes anything.
5. **TeaCache is not "low priority", it is unavailable for both our models.**
   `[dec §4]` lists it last-but-present. Upstream **explicitly disables** it for
   `ti2v_2_2` (our 5B) *and* `i2v_2_2` (A14B) `[w2gp §6.3]`. **MagCache** is the
   one that is enabled, and it ships pre-calibrated per-architecture magnitude
   tables including a dedicated 5B branch with separate t2v/i2v tables — but
   step-skipping caches only pay when there are steps worth skipping, so it is
   the fallback if a few-step recipe's motion proves unusable, not a stack on
   top of one.
6. **The Turbo/distill payoff is ~2.2x, not 3.5x.** `speed-quant.md:301`
   projects 14→4 steps as 3.5x (188s → ~54s) by assuming step count scales
   linearly. Our own sweep says otherwise: 14 steps 188s, 10 steps 153s, 8 steps
   136s — two independent pairs agreeing on ~8.7s/step and therefore **~66s of
   fixed overhead no step reduction can touch**. Realistic prize: **188s →
   85-100s** `[misc §1e-bis]`. Anyone pricing a distill uses 2.2x. Free
   confirmation available: **a `steps-06` clip already exists from the
   2026-08-03 sweep and nobody has timed it** — the fit predicts ~118s. Cheapest
   unmade measurement in this whole area.
7. **The two-machine arithmetic was right but understated.** `[dec §5]` computes
   ~6.8GB of collectives per step (tensor-parallel) → ~7x slower than one card.
   The actual parallelism Alibaba ship is **Ulysses**, which is four collectives
   per attention layer per forward and two forwards per step under CFG: ~20GB per
   sampling step, ~1TB per clip, **~160s of pure network per step at gigabit
   against 8.67s of compute — ~18x slower** `[wan22 §3]`. Same verdict, stronger.
8. **"LTX-2 distilled is 8 steps" is 8 + 3 across two resolutions.** Stage 1 runs
   at *half* the target size, then a separate 2x spatial-upsampler checkpoint,
   then 3 more steps at full size starting from σ 0.909 as a latent img2img
   refine `[ltx §1]`. Any verdict recorded about tonight's single-stage sample
   must carry that caveat or it will be quoted later as "LTX-2 is soft".
9. **Open-Sora's memory figure in our records is the multi-GPU one.** We have
   "44GB+ peak"; single-GPU peak is **52.5GB at 256x256 with `--offload` already
   on**, 60.3GB at 768px `[misc §3]`. Worse than recorded, and unreachable either
   way.
10. **One record confirmed, so nobody reopens it:** `vet_model.py`'s hard-fail on
    `hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF` as "laundering an NC base" is **upheld**
    by the independent licence read `[dec §7]`. Nothing to fix.

---

## 5. Strategic options, priced

| Option | Cost | Payoff | Verdict |
|---|---|---|---|
| **Own 4-step distill of TI2V-5B** | $2,000-5,000 + 1-2 weeks realistic (one published-recipe run alone is 16xA100/48h ≈ $850-2,100); LoRA-DMD variant ~$150-500 on one rented 80GB card, 4-8 days, unvalidated for this model | ~2.2x, i.e. 188s → 85-100s | **Wait.** Founder-reserved (money) regardless |
| **Block-swap port** (kijai route) | ~1 hour for runtime hooks only; **half a day** with load-time per-parameter placement, which is the part that matters | headroom for activations, not fitting the model — ~3-3.5GB per 10 blocks swapped on A14B | **Only if A14B earns it on quality first** |
| **lightx2v as an engine** | replaces our diffusers pipeline wholesale | ~1.5-1.9x/step engine-only | **Mine it, don't adopt.** Take §1's recipe (~20 lines) |
| **Group offload for LTX-2** | a diffusers version bump + one call | makes a 22B transformer fit 24GB at all | **Do it — it is upstream's own answer to our box** |

**Own-Turbo-distill, the honest shape** `[misc §1]`: the method is DMD2, not the
Self-Forcing rollout the repo's name implies (their Wan2.2 config sets
`generator_type: bidirectional`), and **the upstream framework is Apache-2.0** —
only quanhaol's fork and weights are NC. The distillation is **data-free in the
distribution sense**: the teacher *is* the data distribution, so the only inputs
needed are prompts plus one still each. Every input would be ours and clean, and
a distill that only has to cover 2D-anime vertical stills plausibly converges in
well under their 4,000 iterations. What kills it is not the licence or the data —
it is that the prize is 2.2x (correction 6). Recommendation: **wait for a
permissively-licensed distill.** The technique is public, the teacher is Apache,
demand is proven (Kijai already packaged the NC one), and patience costs $0.

**Block-swap port** `[kijai §1]`: the mechanism is ~40 lines and touches no
ComfyUI — `block.to(device)` before and after each block's forward, plus
load-time per-parameter placement decided from the block index. Route to write:
`register_forward_pre_hook` / `register_forward_hook` on
`transformer.blocks[i]` for `i >= swap_start_idx`, on the stock diffusers
`WanTransformer3DModel`; survives upstream diffusers updates. If we build it,
**build it better than the reference in the two ways its own source admits are
missing**: pin the CPU-side buffers (their `non_blocking=True` into pageable
memory is not a real async DMA), and actually use a side stream — theirs is
commented out with "todo causes issues on some systems" while the event plumbing
to make it work is already sketched `[kijai §1]`. On top of that sits the best
idea in the other codebase: decide how many blocks stay **permanently resident**
in the budget and stream only the remainder, spread **evenly** through the stack
so each streamed block's prefetch hides behind a resident block's compute, with
the chain closed into a circle so step N+1's block 0 is already in flight
`[w2gp §1.5]`. **Licence boundary: mmgp is GPL-3.0 and this repo IS the public
product — reimplement from the description, never paste. That is a founder /
governance call, not a steward call** `[w2gp]` licence flag.

**lightx2v** `[lx2v §4]`: genuinely library-shaped (real fluent API, 60+ example
scripts, pip-installable) and Windows + RTX 5090 is genuinely first-class —
Triton quant needs no build, `torch_sdpa` needs nothing, only the NVFP4/CUTLASS
tier needs compiling. But it is a parallel universe to diffusers: its own
transformer, loader, schedulers and VAE handling, with no seam for "use their
scheduler inside our pipeline", and it eagerly imports 25 runner families plus
gradio/fastapi at module import. Its engine-only win is the same order as
choosing a decent attention backend. Watch its `torch<=2.8.0` pin — the version
`[w2gp §5.3]` tells us to avoid.

**Group offload for LTX-2** `[ltx §4]`: upstream's answer to a 24GB card is
`--offload cpu` (~36GB RAM + ~5GB VRAM), **not fp8** — and the two are mutually
exclusive by a hard raise, so the expensive fp8 port would *cost* us the offload
path rather than complement it. With 64GB RAM as of today, CPU offload fits
comfortably. The diffusers equivalent is group offloading with `use_stream=True`;
note it is unverified on sm_120/Windows, the maintainers say `use_stream=False`
is *slower* than blockswap, and revert is one call `[dec §4]`.

---

## 6. Dead ends — so nobody re-litigates them

1. **Splitting one clip across the two laptops. No.** Ulysses moves ~20GB of
   all-to-all per sampling step for our 5B config — ~160s of pure network per
   step at a perfect gigabit against 8.67s of compute, ~1TB per clip. FSDP
   `FULL_SHARD` is no better (~10GB re-gathered per forward, ~80s). Both are
   NCCL-hardcoded and single-node in every shipped example; ring attention is not
   present at all. And even on datacentre interconnect Ulysses returns **2.3x for
   4 GPUs and 3.3x for 8**, not 4x and 8x. One whole clip per machine is the only
   sound unit of work — which is what `farm_worker.py` already does
   `[wan22 §3, §6a]` `[dec §5]`.
2. **fp8-scaled single-file weights on diffusers 0.39.** Already measured
   unloadable on the box and documented in `pipeline/ltx_i2v.py:33-52`; the
   dossier explains the mechanism and adds a warning. diffusers' LTX-2 converter
   drops `weight_scale` / `input_scale`, and upstream loads with
   `strict=False` while `FP8Linear` creates both scales with `torch.empty(())` —
   **uninitialised memory**. A converter that drops the scales therefore produces
   a model that loads without error and multiplies by garbage: a very plausible
   route to green/grey/black output that looks like a driver problem and is
   neither. Tier-1 dequantise-on-load buys download and disk only, **zero VRAM**,
   so it is worth ~nothing to us now that we have the bf16 checkpoint; Tier-2
   real fp8 inference is ~150-200 LOC whose actual risk is a name-mapping
   problem, and it forecloses the offload path we need `[ltx §2, §4, addendum]`.
3. **Turbo weights, under any repo name, at any quantisation.** CC BY-NC-SA 4.0
   upstream; **ShareAlike alone is decisive** — CC BY 4.0 is not a BY-NC-SA
   Compatible Licence and cannot be, so we could not publish our output under it
   regardless of how the NonCommercial question resolves. The no-licence
   Diffusers mirror is *strictly worse* (its redistributor is out of compliance,
   so we receive no grant from them either), and the GGUFs are Adapted Material
   carrying NC and SA forward. Permanent hard fail, already recorded in
   `licence_gate.py:196-209` and upheld `[dec §7]` `[misc §1]`. The only clean
   route to that recipe is asking the Fudan authors to dual-licence — a
   founder-reserved outbound contact.
4. **Hunyuan family, FramePack, SkyReels.** HunyuanVideo-I2V and HunyuanVideo-1.5
   are **BLOCKED on a territory exclusion** in the Tencent Hunyuan Community
   License. FramePack's *code* is Apache-2.0 but its weights
   (`lllyasviel/FramePackI2V_HY`) are a HunyuanVideo derivative with **no licence
   declared at all** — the widely-quoted "Apache-2.0, runs in 6GB" is a statement
   about the code only. SkyReels V2/V3 are **UNCLEAR**: the licence is PDF-only,
   i.e. not machine-readable, and the V3 GitHub README states no licence at all
   `[lic]`.
5. **`torch.compile` at low step counts.** Upstream Wan2GP ships it **off** by
   default; Alibaba's own code has no `torch.compile`, no CUDA graphs, no TF32 or
   `cudnn.benchmark` anywhere. It trades a large one-time warmup for per-step
   gains, and our problem is already ~66s of *fixed* cost against a shrinking
   sampling cost — at 3-4 steps there is nothing left to amortise. Revisit only
   behind a persistent worker process. Two related traps if anyone does: a
   complex-number RoPE cannot be compiled (kijai's `rope_function=comfy` default
   exists for exactly this), and on Windows a first-run VRAM spike is usually a
   stale Triton cache — clear `~/.triton` and the `torchinductor_*` temp dir
   `[w2gp §6.4]` `[wan22 §6b]` `[kijai §5, readme]`.
6. **FlashAttention on this card.** FA3 needs sm_90 TMEM, absent on sm_120; FA2
   on Windows/sm_120 is community wheels only. Lightricks *deliberately refuse*
   FA4 on consumer Blackwell, citing known regressions in newer betas, and fall
   through to plain SDPA on a 5090 `[ltx §5]` `[dec §4]`. SageAttention is
   strictly the better target here.
7. **Kandinsky 5.0 I2V Lite** — the cleanest licence in the field (MIT code) and
   its 12GB claim is real, but its **shipped default negative prompt negates "2D
   cartoon, cartoon, 2d animation, paintings"**: the model is tuned away from our
   entire aesthetic, and no prompt surgery moves a base distribution. It also
   derives resolution from the input under a hard pixel budget — our 704x1280
   still comes out **464x848** — and every distilled/no-CFG checkpoint is **T2V
   only**, leaving I2V at NFE 100 / 139s per clip on an H100. Licence-emergency
   fallback, nothing more `[misc §2]`.
8. **Open-Sora** — dead by video-model standards (last *model* release March
   2025, seventeen months of README edits since), 52.5-60.3GB single-GPU peak
   with offload already on, an 11B DiT stacked on T5-XXL + CLIP + a Hunyuan VAE.
   Do not spend a GPU-hour on it `[misc §3]`.
9. **Multi-account quota cycling** — declined on ToS and provenance grounds,
   founder accepted. Not reopened by anything in these dossiers.


