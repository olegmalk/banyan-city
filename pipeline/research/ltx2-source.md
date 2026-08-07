# LTX-2 upstream source read — findings

Source: `https://github.com/Lightricks/LTX-2` @ `4f89057` ("Merge pull request #266
from alexanderar/dubit-rename"), committed 2026-08-03 17:27 +0300. Shallow clone,
read-only, nothing executed. Clone path (ephemeral):
`/private/tmp/claude-501/.../scratchpad/ltx2`.

Citations below are `path:line` relative to the repo root.

Repo is a uv monorepo of three packages: `ltx-core` (model + loader +
quantization), `ltx-pipelines` (the runnable pipelines), `ltx-trainer` (LoRA
training). Plus `ltx-kernels`, a CUDA/C++ extension package.

## Bottom line for tonight

1. **The distilled sigma list is family-wide and hardcoded** —
   `[1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0]`,
   a Python constant, nothing checkpoint-derived. Safe to use with the bf16
   diffusers transformer. But it is violently non-uniform, so
   `num_inference_steps=8` is **not** the same thing — the list must be passed
   explicitly. Guidance 1.0 is right, and the negative prompt is dead weight on
   this path. (§1)
2. **`--offload cpu`, not fp8, is upstream's answer to a 24GB card**: stated
   requirements are ~28GB VRAM with no offload vs ~36GB RAM + ~5GB VRAM with CPU
   offload. And offload is **incompatible with fp8-scaled-mm** by a hard raise —
   the expensive fp8 port would cost us the offload path rather than complement
   it. (§4, §2)
3. **Tiled VAE decode is on by default upstream** (768px/64 overlap spatial,
   80/24 temporal) and each pipeline stage builds its model, runs, and frees it
   via `.to("meta")` before the next stage exists. Gemma-3-12B and the 22B
   transformer are never co-resident. Hold both in a diffusers script and we OOM
   for reasons unrelated to the transformer. (§4)

Three things that contradict or complicate what we thought:

- **"8 steps" is 8 + 3 across two resolutions**, not 8. Stage 1 runs at *half*
  the target size, then a separate 2x spatial-upsampler checkpoint, then 3 more
  steps at full size starting from sigma 0.909. A single-stage 8-step diffusers
  render at final resolution is off-recipe in the soft/under-detailed
  direction. (§1)
- **The conditioning still is deliberately re-encoded through libx264 at CRF 33
  before being VAE-encoded.** A clean PNG is out of distribution by their own
  reckoning. Cheap knob, and diffusers won't do it. (§3)
- **Their own i2v prompt doctrine says describe only what *changes* from the
  image, and never invent camera motion** — restating visual detail already in
  the still is what *causes* scene cuts. Given the last few cycles were spent
  fighting frozen frames and camera shake, this is worth a read. (§3)

---

## 1. THE DISTILLED SCHEDULE — answer: family-wide, hardcoded, and NOT what a
## diffusers 8-step flow-match default will give you

The distilled sigmas are **module-level Python constants**, not read from the
checkpoint:

`packages/ltx-pipelines/src/ltx_pipelines/utils/constants.py:14-24`

```python
# Noise schedule for the distilled pipeline. These sigma values control noise
# levels at each denoising step and were tuned to match the distillation process.
DISTILLED_SIGMA_VALUES = [1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0]

# Reduced schedule for super-resolution stage 2 (subset of distilled values)
STAGE_2_DISTILLED_SIGMA_VALUES = [0.909375, 0.725, 0.421875, 0.0]

DISTILLED_SIGMAS = torch.tensor(DISTILLED_SIGMA_VALUES)
STAGE_2_DISTILLED_SIGMAS = torch.tensor(STAGE_2_DISTILLED_SIGMA_VALUES)
# Stage 2 schedule for the tiled-data-parallel multi-GPU runner.
TDP_DISTILLED_SIGMAS = torch.tensor([0.625, 0.4, 0.0])
```

**Checkpoint-specific or family-wide?** Family-wide — and orthogonal to
fp8-vs-bf16:

- The only checkpoint-sniffing function in the codebase is
  `detect_params()` at `utils/constants.py:110-130`. It reads the safetensors
  `model_version` metadata key and returns `LTX_2_3_PARAMS` vs `LTX_2_PARAMS`.
  Those params objects carry `num_inference_steps`, resolution and **guider**
  settings — they contain **no sigma list at all**. Nothing in the repo derives
  a sigma schedule from checkpoint metadata.
- `DistilledPipeline.__call__` takes the sigmas as default arguments
  (`distilled.py:125-126`: `stage_1_sigmas: torch.Tensor = DISTILLED_SIGMAS`,
  `stage_2_sigmas: torch.Tensor = STAGE_2_DISTILLED_SIGMAS`) and the CLI `main()`
  at `distilled.py:225-235` never overrides them.
- Quantization is a **separate, orthogonal** constructor argument
  (`distilled.py:55` `quantization: QuantizationPolicy | None`). fp8 vs bf16
  changes only how the weights are stored/multiplied, never the schedule.

=> **Our render tonight can use this exact list against the bf16 diffusers
transformer. It is the right list.**

### But: "8 steps, guidance 1.0" is NOT the same thing as this schedule

Two traps, both of which bite a naive diffusers run:

1. **The schedule is violently non-uniform and front-loaded.** Five of the eight
   steps sit between sigma 1.0 and 0.975 — i.e. five near-no-op steps at maximum
   noise — then it jumps 0.975 -> 0.909375 -> 0.725 -> 0.421875 -> 0.0. A
   diffusers `FlowMatchEulerDiscreteScheduler` asked for
   `num_inference_steps=8` produces a roughly-linear (or shift-warped) ramp,
   which is a *completely different* trajectory. Setting `num_inference_steps=8`
   is not equivalent to using the distilled schedule; you must pass
   `sigmas=[1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875]`
   explicitly (diffusers convention: pass the 8 leading sigmas, the trailing 0.0
   is appended by the scheduler — verify against the installed scheduler's
   `set_timesteps(sigmas=...)` handling, which normally appends the final zero
   itself).
2. **"8 steps" in their README means 8 + 3, in two stages at two resolutions.**
   `README.md:102` says "8 steps stage 1, 4 steps stage 2"; the code says stage 2
   is 4 *sigmas* = **3 steps** (`constants.py:19`). And the stages are not the
   same resolution: `distilled.py:143` runs stage 1 at `width // 2, height // 2`,
   then `distilled.py:168` runs the latent through the **spatial upsampler**
   (a separate 2x checkpoint, `ltx-2.3-spatial-upscaler-x2-1.1.safetensors`),
   then stage 2 re-denoises at full resolution starting from
   `noise_scale=stage_2_sigmas[0]` = **0.909375** with the upscaled latent as
   `initial_latent` (`distilled.py:182-201`). Stage 2 is a latent-space
   img2img-style refine at strength 0.909, not a fresh generation.

   So a single-stage diffusers run using `DISTILLED_SIGMAS` reproduces **stage 1
   only** — which upstream expects to be at *half* the target resolution. If we
   render one sample single-stage at final resolution, we are off-recipe in a way
   that predicts exactly the failure mode of a distilled model asked to do too
   much in 8 steps: soft, under-resolved, low-detail. Worth knowing before we
   judge the sample's look.

### Guidance 1.0 — confirmed correct for distilled

The distilled pipeline uses `SimpleDenoiser` (`distilled.py:156`, `:183`), and
there is no guider in the distilled path at all. The CFG/STG machinery
(`MultiModalGuiderParams`, `cfg_scale=3.0` etc. at `constants.py:40-59`) belongs
to the **non-distilled** `PipelineParams` used by the two-stage/HQ pipelines. So
`guidance_scale=1.0` (i.e. no CFG, single forward pass per step) is the right
call for the distilled checkpoint, and it means **the negative prompt is unused
on this path** — see §3.

---

## 2. Their fp8 loading path — and the good news: there are TWO of them, and the
## easier one is a pure state-dict transform

`ltx-core` ships two independent fp8 policies, dispatched by string in
`packages/ltx-pipelines/src/ltx_pipelines/utils/quantization_factory.py:17-36`:

| policy | for | mechanism |
|---|---|---|
| `fp8-cast` | **bf16 checkpoints** (downcast on the fly) *and* prequant fp8 checkpoints (folds the scales away) | store fp8, upcast to input dtype inside `forward` |
| `fp8-scaled-mm` | **prequantized fp8 checkpoints only** | `torch._scaled_mm` with the checkpoint's per-tensor scales |

### 2a. `fp8-scaled-mm` — plain torch, no custom kernels

`packages/ltx-core/src/ltx_core/quantization/fp8_scaled_mm.py:23-76` — the whole
thing is one `nn.Module`:

```python
class FP8Linear(nn.Module):
    self.weight       = nn.Parameter(... dtype=torch.float8_e4m3fn ...)
    self.weight_scale = nn.Parameter(torch.empty((), dtype=torch.float32 ...))   # scalar
    self.input_scale  = nn.Parameter(torch.empty((), dtype=torch.float32 ...))   # scalar
    def forward(self, x):
        qinput = torch.clamp(x * self.input_scale.reciprocal(), fp8_min, fp8_max).to(torch.float8_e4m3fn)
        output = torch._scaled_mm(qinput, self.weight.t(),
                                  scale_a=self.input_scale, scale_b=self.weight_scale,
                                  out_dtype=x.dtype, use_fast_accum=True)
```

Facts that matter:

- **No custom kernels.** `torch._scaled_mm` is stock PyTorch. `ltx-kernels`
  (the CUDA/C++ package) is *not* on this path — its fp8 content is the
  *blockwise* deep-gemm kernels (`packages/ltx-kernels/csrc/blockwise/...`),
  a different, unrelated quantization scheme
  (`ltx_core/quantization/blockwise/`). Per-tensor scaled-mm needs nothing built.
- Both scales are **scalars** (`torch.empty(())`, and `fp8_cast.py:295-296`
  hard-rejects `scale.ndim != 0`). So it is per-tensor, not per-channel — one
  float per layer for weights, one for activations.
- `input_scale` is a **static activation scale baked into the checkpoint**, not
  computed at runtime. Nothing calibrates it; it is just loaded. So if a
  converter drops it, there is no way to recover it from the weights — it must
  come out of the file.
- Layer set is **auto-discovered from the file header**, not hardcoded
  (`fp8_scaled_mm.py:136-164`): a layer is swapped iff it has a
  `.weight_scale` key **and** its `.weight` has dtype `F8_E4M3`. Discovery reads
  only the safetensors JSON header (`fp8_scaled_mm.py:15-20`), no tensor loads.
  It raises rather than silently no-op'ing on a bf16 checkpoint
  (`:148-152`). Matching to module names is by suffix (`:154-156`).
- The swap happens as a post-load `ModuleOps` mutator walking `named_modules()`
  and `setattr`-ing replacements (`_swap_linears_to_fp8`, `:111-133`).
- **A corruption bug of exactly our family is already fixed here**, at
  `fp8_scaled_mm.py:52-56`:
  > `# Clamp before cast: out-of-range values cast to NaN/saturated FP8, which`
  > `# produces black-screen output on some checkpoints (e.g. ltx-2-19b-dev-fp8).`
  Activations are clamped to the fp8 range *before* the cast. A naive port that
  writes `(x * input_scale.reciprocal()).to(torch.float8_e4m3fn)` without the
  clamp gets black frames. See §5 — this is the nearest in-repo analogue to the
  green/grayscale reports.

### 2b. `fp8-cast` on a prequant checkpoint — the cheap way to use the fp8 file

This is the finding that reprices the whole fp8 question. `fp8_cast.build_policy`
(`fp8_cast.py:326-337`) handles a **prequantized** checkpoint by *folding the
scale into the weight at load time* and throwing the scale away:

`packages/ltx-core/src/ltx_core/quantization/fp8_cast.py:290-301`

```python
def _on_param(param_key, value):
    scale = scales.get(param_key)
    if scale is None:
        return TRANSFORMER_LINEAR_DOWNCAST_MAP.apply_to_key_value(param_key, value)
    scale = scale.to(device=value.device)
    if scale.ndim != 0:
        raise ValueError(...)
    bf16 = (value.to(torch.float32) * scale).to(torch.bfloat16)
```

i.e. **`weight_bf16 = weight_fp8.float() * weight_scale`**, one line, and
`input_scale` is irrelevant on this path because activations stay bf16. The
`*_scale` keys are then dropped (`_drop_scale`, `:303-310`), with a deliberate
crash if a scale key appears that `_read_scales` didn't pre-register — they
explicitly guard against a silently-desynced fold (`:306-309`, and the comment at
`:313-317` explains they register the drop ops first so a stray scale crashes
before a mismatched fold can land).

Concrete numbers from their own verification comment (`fp8_cast.py:242-247`):
every scale key in `ltx-2.3-22b-{dev,distilled}-fp8.safetensors` carries the raw
prefix `model.diffusion_model.` — **2924/2924 (dev) and 2992/2992 (distilled)**
scale keys.

### What porting to diffusers actually costs

Two tiers, and we should price them separately:

**Tier 1 — dequantize-on-load (~30-40 LOC, no modelling changes).** Read the fp8
safetensors ourselves, and for each `*.weight` with a sibling `*.weight_scale`
emit `w.float() * scale -> bf16`; drop `*_scale` and `*input_scale`; strip the
`model.diffusion_model.` prefix; hand the resulting bf16 state dict to the
diffusers transformer. Touches only our loading script. This buys **download and
disk savings only — zero VRAM savings**, because the weights end up bf16 in
memory. Given we already have the bf16 diffusers checkpoint, Tier 1 is worth
~nothing to us. Do not spend the evening on it.

**Tier 2 — real fp8 inference (~150-200 LOC, touches three things).** Port
`FP8Linear` + `_swap_linears_to_fp8` + `get_fp8_swap_module_ops` (that is
~150 LOC of the file, all pure-torch and self-contained), then:
1. **the converter** — diffusers' LTX-2 conversion drops `weight_scale` /
   `input_scale`; we need our own state-dict path that keeps them and maps
   the upstream `model.diffusion_model.*` names onto diffusers' module names.
   This is the actual work and the actual risk: it is a **name-mapping
   problem**, not a maths problem. Our known failure is exactly here.
2. **module construction** — swap `nn.Linear`->`FP8Linear` after the diffusers
   transformer is instantiated but before `load_state_dict`, so the fp8 dtypes
   and the two scalar params exist to receive the file's values.
3. **LoRA fusing** — only if we ever fuse LoRAs; `_fp8_scaled_mm_fuse`
   (`:167-186`) dequant/add/re-quantizes. Skip entirely for now.

Tier 2's payoff is roughly halving transformer VRAM. Whether it is needed at all
on a 24GB card is answered by §4 — their own answer to "not enough VRAM" is
`--offload`, not fp8.


---

## 3. Recommended inference settings for image-to-video 2.3

### There are no resolution buckets

Searched for them; they do not exist. The only constraints in code are
divisibility and the defaults:

- **Divisibility** (`utils/helpers.py:321-332`, `assert_resolution`): two-stage
  pipelines (including `DistilledPipeline`, which passes `is_two_stage=True` at
  `distilled.py:128`) require height *and* width divisible by **64**. One-stage
  requires 32. That is the whole rule — any 64-multiple is legal.
- **Frame count** (`utils/args.py:446-447`): `num_frames = 8*K + 1`. Not
  asserted, only documented in the help text.
- **Defaults for the distilled CLI**: `--height 1024 --width 1536`
  (`args.py:788-801` sets height/width to `params.stage_2_*`, and
  `constants.py:62-67` derives those as 2x `stage_1_height=512` /
  `stage_1_width=768`), `--num-frames 121`, `--frame-rate 24.0`, `--seed 10`
  (`constants.py:34-38`).
- The HQ variant's default is 1088x1920 (`constants.py:80-83`), which is the
  only 16:9-shaped preset anywhere in the repo.

### Vertical / portrait

Nothing in the code cares about orientation — height and width are independent
and symmetric everywhere. Portrait works by passing a portrait pair; the only
requirement is /64. For reference, both **704x1280** (11x64, 20x64) and
**1088x1920** (17x64, 30x64) are legal two-stage sizes, so our existing
704x1280 canary resolution is on-recipe as far as upstream is concerned.

Two orientation gotchas that are ours to handle, not theirs:

- **The conditioning image is resize-then-center-cropped to the target**
  (`media_io.py:121`, `resize_and_center_crop`). Feed a landscape still to a
  portrait render and you silently lose the sides. Our input stills must
  already be at the target aspect.
- **`assert_resolution` fires on the *final* size, and stage 1 runs at
  half** (`distilled.py:143`). 704x1280 -> stage 1 at 352x640, both /32. Fine.

### The conditioning image is deliberately JPEG-ish degraded first

`DEFAULT_IMAGE_CRF = 33` (`constants.py:103`), and
`load_image_and_preprocess` (`media_io.py:106-123`) calls
`preprocess(image, crf)` -> `encode_single_frame` -> `decode_single_frame`
(`media_io.py:695-731`): the still is **round-tripped through libx264 at CRF 33**
before it is VAE-encoded. `crf=0` bypasses it (`media_io.py:723-724`), exposed as
the optional 4th value of `--image PATH FRAME_IDX STRENGTH [CRF]`
(`args.py:79-91`).

This is not a bug — it is a deliberate domain match to the compressed video
frames the model saw in training. A clean PNG handed straight to a diffusers i2v
pipeline is *out of distribution* by their own reckoning. This is a cheap,
testable knob for us and diffusers almost certainly does not do it.

### Image conditioning strength — semantics are inverted from "denoise strength"

`VideoConditionByLatentIndex.apply_to`
(`ltx-core/src/ltx_core/conditioning/types/latent_cond.py:41`):

```python
latent_state.clean_latent[:, start_token:stop_token] = tokens
latent_state.denoise_mask[:, start_token:stop_token] = 1.0 - self.strength
```

So `strength=1.0` -> `denoise_mask=0` -> those tokens are pinned to the clean
image latent for the whole run; `strength=0.8` leaves them 20% free. Higher =
more locked to the image. The README quickstart and docs examples use **0.8-0.9**
for a first frame, not 1.0.

Mechanically: `timesteps = denoise_mask * sigma` per token
(`helpers.py:275-284`), and after **every** step the latent is re-blended with
the clean latent, `denoised*mask + clean*(1-mask)`
(`post_process_latent`, `helpers.py:248-250`, called from `samplers.py`
`_step_state`). Conditioning is a per-token timestep mask, not a noised
init latent.

`frame_idx == 0` routes to `VideoConditionByLatentIndex` (latent replacement);
any other index routes to `VideoConditionByKeyframeIndex`
(`helpers.py:144-155`). So first-frame i2v and mid-shot keyframing are
different code paths.

### Negative prompt: none on the distilled path

`DEFAULT_NEGATIVE_PROMPT` exists (`constants.py:137-149`, and it is long — worth
reading if we ever run the non-distilled model) but `--negative-prompt` is only
registered by `default_1_stage_arg_parser` (`args.py:540-549`) and its
descendants. `default_2_stage_distilled_arg_parser` (`args.py:788-811`) does
**not** register it, because `SimpleDenoiser` never runs an uncond pass. Passing
a negative prompt to a distilled render at guidance 1.0 does nothing.

(Their negative prompt does include `motion blur`, `camera shake`, `jittery
movement` and `flickering` — consistent with what we already found in ours.)

### Sampler identity — our diffusers translation is safe

- The loop is `for step_idx, _ in enumerate(tqdm(sigmas[:-1]))`
  (`samplers.py:70`): **9 sigmas = 8 model calls**.
- `EulerDiffusionStep.step` (`components/diffusion_steps.py:32-40`):
  `dt = sigma_next - sigma`; `sample + to_velocity(sample, sigma, denoised)*dt`,
  computed in float32.
- The transformer itself is a **velocity** model; `X0Model`
  (`model/transformer/model.py:505-535`) wraps it and converts to denoised via
  `to_denoised`, then the Euler step converts straight back to velocity. Net
  algebra is identical to a standard flow-match Euler step on velocity — which
  is what diffusers' `FlowMatchEulerDiscreteScheduler` does. So the scheduler
  translation is sound; only the **sigma list** has to be forced (see §1).
- Alternative steppers exist and are *not* used by the distilled path:
  `Res2sDiffusionStep` (2nd-order + SDE, `eta=0.5`) for the HQ pipeline, and
  `EulerCfgPpDiffusionStep` (CFG++). Also
  `gradient_estimating_euler_denoising_loop` with `ge_gamma=2.0`
  (`samplers.py:80+`, `docs/optimization.md:127-149`) which they claim gets
  40 steps of quality in 20-30 — a **non-distilled** lever, ignore for now.

### Their own i2v prompting doctrine — this one is worth reading twice

`ltx-core/src/ltx_core/text_encoders/gemma/encoders/prompts/gemma_i2v_system_prompt.txt`
is the system prompt for their `--enhance-prompt` i2v rewriter, i.e. Lightricks'
own statement of what a good LTX-2 i2v prompt looks like. Three rules in it cut
directly against habits we have:

- `:6` — **"Describe only changes from the image: Don't reiterate established
  visual details. Inaccurate descriptions may cause scene cuts."** Restating what
  is already in the still is not neutral; it *causes cuts*.
- `:16` — **"Camera motion: DO NOT invent camera motion/movement unless
  requested by the user."**
- `:7` — present-progressive verbs ("is walking", "speaking"); `:8` temporal
  connectors ("as", "then", "while"); `:13` "Restrained language. Avoid dramatic
  terms."
- `:9-10` — audio is expected to be **interleaved through** the prompt, not
  appended at the end, and speech must be given as exact quoted words with a
  voice description. (LTX-2 generates audio jointly; `distilled.py:204` decodes
  an audio track on every render whether we want one or not.)

The t2v counterpart is in the same directory (`gemma_t2v_system_prompt.txt`),
and `README.md:111-121` adds: single flowing paragraph, start with the action,
keep under 200 words.

---

## 4. Memory management — the numbers, and the one hard incompatibility

### Their stated expectations, verbatim

`packages/ltx-pipelines/src/ltx_pipelines/utils/types.py:113-124`:

```
- ``NONE``: All weights on GPU (no streaming). Fastest inference,
  requires enough VRAM for the full model (~28 GB for LTX-2).
- ``CPU``: Weights pinned in CPU RAM, streamed layer-by-layer to a
  small GPU buffer. First pass reads from disk; subsequent passes
  reuse the CPU cache. Requires ~36 GB RAM + ~5 GB VRAM.
- ``DISK``: Weights read from disk on demand through a small CPU
  buffer, then streamed to GPU. Every pass re-reads from disk.
  Lowest memory: ~5 GB RAM + ~5 GB VRAM.
```

For a 24GB 5090 + 64GB RAM this is decisive: **`OffloadMode.NONE` does not fit**
(~28GB stated, and that figure reads like it is for the 19B LTX-2.0 — a 22B bf16
transformer alone is ~44GB, so treat 28GB as a floor, not a target).
`OffloadMode.CPU` at ~36GB RAM + ~5GB VRAM fits our box comfortably. That is
upstream's answer to our hardware, and it is **not** fp8.

### The hard incompatibility: offload XOR fp8-scaled-mm

`packages/ltx-pipelines/src/ltx_pipelines/utils/blocks.py:316-323`:

```python
# WeightsProvider currently only supports plain bf16 + fp8_cast LoRA fusion
# (no companion-key emission). Quantization policies that emit
# companion keys (e.g. ``.weight_scale``) cannot be streamed yet.
if quantization is not None and quantization.fuse_rule is not fp8_cast_fuse_rule:
    raise ValueError(
        "Block streaming is not supported with this quantization policy "
        "(only bf16 and fp8_cast are currently supported)."
    )
```

So: bf16 + offload = fine. fp8-cast + offload = fine. **fp8-scaled-mm + offload =
hard error.** (`docs/pipelines.md:121` says the same for HDR:
"`--offload` ... disables FP8 quantization when not `none`".) This means the
expensive Tier-2 fp8 port from §2 would *cost* us the offload path, not
complement it.

### The architecture trick we should copy regardless of fp8

`blocks.py:1-5`: **"Blocks build a model on each `__call__`, use it, then free
GPU memory."** Every stage — `PromptEncoder`, `ImageConditioner`,
`DiffusionStage`, `VideoUpsampler`, `VideoDecoder`, `AudioDecoder` — is a
separate object that constructs its model, runs, and tears it down. The teardown
is `gpu_model()` (`utils/gpu_model.py:14-35`): `synchronize` ->
**`model.to("meta")`** -> `cleanup_memory()`. Moving to `meta` releases storage
for params and buffers regardless of which device they were on — a cleaner
release than `del` + `empty_cache`.

This matters at 24GB because **Gemma-3-12B is the text encoder**. It is never
resident at the same time as the 22B transformer. If our diffusers script builds
pipeline components eagerly and holds them, we OOM for reasons that have nothing
to do with the transformer. Encode the prompt, free the encoder, then build the
transformer.

`AllocatorTrimStrategy.DEFER` (`gpu_model.py:19-21`) skips the trim to keep the
caching allocator warm for back-to-back runs — the right choice when we batch
beats, the wrong one when we are near the ceiling.

### Other levers, none of which we currently use

- **`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`** — required alongside
  quantization per `docs/optimization.md:7` and `:48-52`. Cheap; set it.
- **Tiled VAE decode is ON by default in their CLI.** `distilled.py:223` passes
  `TilingConfig.default()`, which is spatial tiles of **768px with 64px
  overlap** and temporal tiles of **80 frames with 24 overlap**
  (`video_vae/tiling.py:64-69`). Tile size must be >=64 and /32; overlap /32;
  temporal >=16 and /8 (`:15-50`). A 121-frame decode at 1024x1536 is *not*
  attempted in one shot upstream. If diffusers' VAE decode isn't tiled, that is
  a likely OOM point independent of the transformer.
- **`MEMORY_EFFICIENT_DECODE`** (`video_vae/memory_efficient_decode.py:1-22`) —
  an opt-in `ModuleOps` that rewrites the decoder to use preallocated workspace
  buffers, in-place norm/SiLU/affine, in-place temporal-chunked conv (non-causal
  only), and frees the input before `DepthToSpaceUpsample` convs so peak never
  holds input+output. Applied in `blocks.py` for the video decoder.
- **`--max-batch-size`** (`args.py:379-391`): guided denoisers batch up to 4
  guidance passes into one forward; default 1 runs them sequentially. Irrelevant
  to distilled (one pass, no guidance).
- **`--compile mode=reduce-overhead`** captures CUDA graphs and is the main
  latency lever, but reserves static memory pools — explicitly a
  memory-for-speed trade (`docs/optimization.md:80-83`). Don't reach for it at
  24GB. Blocks are compiled shape-polymorphically on the sequence dim, so one
  artifact serves all token counts (`:66`).
- **`unsafe_skip_cache_dynamic_shape_guards`** — do **not** enable. It is a
  documented correctness hazard: a kernel first compiled at a short sequence
  keeps int32 address arithmetic and reading it back at **>~58k tokens/rank**
  overflows to out-of-bounds reads, "surfacing as a CUDA illegal memory access or
  **silently corrupted output**" (`docs/optimization.md:119`).
- **`ltx_pipelines.utils.vram_budget`** is referenced by `hdr_ic_lora.py:23`,
  `:788-790` as the way to compute max frames per resolution — **the module does
  not exist in the public repo.** Dead advice; don't chase it.

---

## 5. The Windows / consumer-Blackwell question (issue #37, green/grayscale)

**Nothing in this repo names the bug.** No mention of green output, grayscale
output, an issue number, or the RTX 5090 outside of the trainer's hardware
tables. The public git history cannot help either, and that is itself a finding:

**The public repo is a squashed mirror.** Every content drop is one commit
titled `Automated PR - <date>`, so there are no per-fix commit messages to grep.
Drops since June 2026 are exactly three: `f4b06fb` 2026-06-17, `63fd9a4`
2026-07-07, and `10c9979` 2026-08-03 (which is only the LipDub -> Dub-It
rename). History starts `fc3b319` 2026-01-05. Conclusion: **do not expect
upstream git to tell us when a Windows/Blackwell fix landed** — the granularity
does not exist. Only the file contents are informative.

What the code *does* say, in descending order of usefulness to us:

1. **They deliberately refuse FlashAttention-4 on consumer Blackwell.**
   `ltx-core/src/ltx_core/model/transformer/attention.py:267-292`:
   > `- Datacenter Blackwell (sm_100, B200): FA4 > SDPA. FA4 is intentionally *not*`
   > `  picked on consumer Blackwell (sm_120) -- known regressions in newer`
   > `  FA4 betas; users who want it on sm_120 must opt in explicitly.`
   The dispatch is by compute-capability major: `major == 9` -> FA3/FA4,
   `major == 10` -> FA4 (`:281-289`). **sm_120 is major 12, so a 5090 falls
   through to plain SDPA** with the priority list
   `CUDNN > FLASH > EFFICIENT > MATH` (`_SDPA_FULL_PRIORITY`, `:231-236`).
   `README.md:104` corroborates from the other side: the only FA4 revision they
   have verified is `flash-attn-4==4.0.0b9` against torch 2.9.1+cu128, and
   "newer betas have known issues on consumer Blackwell".

   **This is our most actionable lead on the corruption.** Their SDPA priority
   puts **cuDNN attention first**, and cuDNN attention is the historical source
   of silent wrong-output (not crash) bugs on brand-new architectures. Our
   diffusers run uses torch SDPA too, so it is subject to the same dispatch. If
   tonight's sample comes out green/grey/monochrome, the first experiment is to
   force a different SDPA backend —
   `with torch.nn.attention.sdpa_kernel(SDPBackend.EFFICIENT_ATTENTION):` (or
   `MATH`, slow but definitionally correct) around the denoise loop. A green or
   grayscale frame is a *plausible* signature of attention returning garbage,
   and MATH-vs-cuDNN is a 1-line A/B that settles it.

2. **A black-frame corruption bug of the same family is already fixed in their
   fp8 path.** `quantization/fp8_scaled_mm.py:52-56` — out-of-range activations
   cast to NaN/saturated fp8 and "produces black-screen output on some
   checkpoints (e.g. `ltx-2-19b-dev-fp8`)"; fixed by clamping before the cast.
   Evidence that (a) this model family does fail by emitting degenerate flat
   frames rather than crashing, and (b) the cause was numeric range, not a
   driver.

3. **Windows is a second-class platform, in exactly two documented places.**
   `quantization/fp8_cast.py:62-74` — stochastic rounding is a Triton kernel, and
   "When Triton is not available (e.g., on Windows), this falls back to
   deterministic (nearest) rounding via `weight.to(dtype)`". Gated on
   `TRITON_AVAILABLE`, which is a bare `try: import triton`
   (`loader/kernels.py:2-8`), and additionally on `device.type == "cuda"`
   (`fp8_cast.py:72`). Also `docs/multigpu/README.md:29`: "**Linux** -- NCCL and
   CUDA-IPC peer buffers are Linux-only (no macOS/Windows)." Neither causes
   colour corruption; both mean a Windows box silently takes different code
   paths, so **do not assume a Windows result reproduces a Linux one.**

4. `ltx-kernels/setup.py:43-44`: "the Blackwell (100a/120) path is implemented
   but **not yet validated on real Blackwell hardware** -- needs a B200 + CUDA
   12.8 build/run pass." Only affects the optional compiled-kernels package,
   which we are not building; but it is upstream saying, in their own words,
   that Blackwell is untested.

5. Colour handling, for completeness, since "green" invites the theory: the
   encoder path is explicit and looks correct — `libx264`, `pix_fmt=yuv420p`,
   with `colorspace` and `color_range` tagged from a `FrameConverter`
   (`media_io.py:383-392`), default `yuv420p_bt709_converter_` doing the RGB->YUV
   matrix on GPU (`utils/color_conversion.py:1-7, 62-70`). Full-vs-limited range
   is modelled (`ColorRange.MPEG/JPEG`, `:29-38`). A mis-tag here shifts colour
   or contrast; it does not produce grayscale. **Grayscale output means the
   chroma planes are ~constant, which points upstream of the encoder — at the
   latents.** Prioritise hypothesis 1.

---

## 6. AI disclosure / AUP enforcement in code: there is none

Searched the whole tree for `watermark`, `c2pa`, `content credential`, `synthid`,
`disclos`, `provenance`, `metadata stamp`. **Zero hits in code.** The model does
not stamp anything and the pipelines do not either:

- Video encode (`media_io.py:339-392`) sets codec, CRF, preset, pix_fmt,
  colorspace and color_range. It writes **no** metadata, comment, or
  `encoder`-tag of their choosing beyond what libx264/pyav write by default.
  `:794` adds `movflags=+faststart` on the HDR preview path — that is it.
- No steganographic or frequency-domain watermark anywhere in the VAE, decoder,
  or vocoder.
- Nothing checks or records an AUP acceptance at runtime.

**The disclosure duty is contractual, not technical**, and it is explicit. The
LTX-2 Community License (dated January 5, 2026), **ATTACHMENT A: Use
Restrictions**, item 5 (`LICENSE:310-314`), forbids using outputs:

> "To generate or disseminate information and/or content (e.g. images, code,
> posts, articles), and place the information and/or content in any context
> (e.g. bot generating tweets) **without expressly and intelligibly disclaiming
> that the information and/or content is machine generated**;"

Attachment A also forbids impersonation/deepfakes without consent (item 7,
`LICENSE:317-319`) and generating false information to harm (item 3). The
preamble to Attachment A binds us to the separate Acceptable Use Policy
(`LICENSE:293-296`), which is a URL/document not vendored in the repo — if we
need its text, it has to be fetched from Lightricks, and this repo does not
contain it.

Practical consequence for us: **our per-post disclosure is the only disclosure
that will exist.** Nothing is embedded in the file, so nothing survives a
re-upload or a screen-record. If we want durable provenance we have to add it
ourselves (our leaf yaml already does this per §7.2 of STEWARDSHIP; the mp4
itself carries nothing). And since the licence says "expressly and intelligibly",
a disclosure buried in a repo file arguably does not discharge it for a TikTok
post — the disclaimer belongs where the content is placed.

---

## Addendum: `strict=False` makes a dropped scale silent, not loud

`packages/ltx-core/src/ltx_core/loader/single_gpu_model_builder.py:67` and `:83`:

```python
meta_model.load_state_dict(sd, strict=False, assign=True)
```

Two consequences.

**Benign upstream:** `input_scale` appears nowhere in the codebase except as a
declared `nn.Parameter` on `FP8Linear` (`fp8_scaled_mm.py:42,56,62`) — no sd-op
reads or drops it. On the fp8-cast path, `_read_scales` sweeps *every* `*_scale`
key (`fp8_cast.py:261-263`), so an `.input_scale` becomes a scales-dict entry
keyed `...to_q.input` that nothing ever looks up, and the raw `.input_scale` key
itself matches no registered suffix op and passes through unchanged
(`sd_ops.py:131` returns unmatched keys as-is). `strict=False` then discards it.
Harmless, but it means the two fp8 policies do not share a scale-key contract.

**A live hazard for our port:** `FP8Linear` creates both scales with
`torch.empty(())` — **uninitialized memory** (`fp8_scaled_mm.py:41-42`). With
`strict=False`, a converter that drops `weight_scale`/`input_scale` produces a
model that **loads without error and multiplies by garbage**. That is a very
plausible route to green/grey/black output that looks like a hardware or driver
problem and is neither. If we ever build the Tier-2 fp8 path, the port must
assert that every swapped layer received both scales — check
`load_state_dict`'s returned `missing_keys` and fail loudly. Do not rely on
`strict=True` alone either, since the diffusers module tree legitimately has
other missing/extra keys.
