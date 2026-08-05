# lightx2v + VBench — source reading

Read-only source study of two upstream repos, done 2026-08-04. Nothing was
executed; every claim below is a file:line citation from a shallow clone.

| repo | url | pinned commit |
|---|---|---|
| lightx2v | <https://github.com/ModelTC/LightX2V> | `78a036b` (2026-08-04, "Fix: fastwam training lr_eta_min (#1330)") |
| VBench | <https://github.com/Vchitect/VBench> | `45e79ec` (2026-03-23, "Update README.md") |

lightx2v is the same org that publishes the Lightning/distill LoRAs on
huggingface.co/lightx2v, so for §1 it is the *authoritative* source: they
trained the weights and this is the code they trained them for.

---

## 1. The Lightning 4-step recipe for Wan 2.2 I2V-A14B (authoritative)

Source of truth: `configs/distill/wan22/wan_moe_i2v_distill_lora_4step_cfg_ulysses.json`
and `configs/distill/wan22/wan_moe_i2v_distill_with_lora.json` (identical except
for multi-GPU parallelism), cross-checked against the library example
`examples/wan/wan_i2v_with_distill_loras.py`.

```
infer_steps          4
denoising_step_list  [1000, 750, 500, 250]     # NOT timesteps — see below
boundary_step_index  2                          # expert switch, by STEP INDEX
sample_shift         5.0
enable_cfg           false                      # single forward per step
sample_guide_scale   [3.5, 3.5]                 # DEAD VALUE — see below
LoRA strength        1.0  on BOTH experts       # rank 64
target_video_length  81 frames
resolution           720x1280 (config) / 480x832 also blessed (example)
use_image_encoder    false                      # A14B takes no CLIP image embed
```

LoRA files, per `examples/wan/wan_i2v_with_distill_loras.py:34-35`:

- `wan2.2_i2v_A14b_high_noise_lora_rank64_lightx2v_4step_1022.safetensors`
- `wan2.2_i2v_A14b_low_noise_lora_rank64_lightx2v_4step_1022.safetensors`

Both at `strength: 1.0`. There is no asymmetry between experts, and no
"0.5 for high / 1.0 for low" folklore anywhere in the repo. The `_1022` suffix
is a weight revision date; the fully-merged (non-LoRA) checkpoints in
`examples/wan/wan_i2v_distilled.py:15-16` carry a *newer* high-noise revision
(`_4step_1030`) than low-noise, so revisions are pinned per-expert and are
worth re-checking on HF rather than assumed matched.

### 1a. CFG is off, and the guide scale is a vestigial value

`enable_cfg: false` gates out the entire CFG branch at
`lightx2v/models/networks/wan/model.py:285`, so `sample_guide_scale` is never
read on this path. The two lines that would have applied a *per-expert* guide
scale are commented out in the shipped source:

- `lightx2v/models/runners/wan/wan_distill_runner.py:63` — `#  self.scheduler.sample_guide_scale = self.config["sample_guide_scale"][0]`
- `lightx2v/models/runners/wan/wan_distill_runner.py:73` — `# self.scheduler.sample_guide_scale = self.config["sample_guide_scale"][1]`

The library examples pass `guidance_scale=1`
(`examples/wan/wan_i2v_distilled.py:41`, `wan_i2v_with_distill_loras.py:47`),
which is the honest expression of the same thing. **Do not copy `3.5` out of
that JSON into a diffusers `guidance_scale`** — the distilled model is
CFG-free; 4 steps means 4 forward passes, not 8. (`sample_guide_scale` is
assigned raw at `models/schedulers/wan/scheduler.py:28`, so it would be the
*list* `[3.5, 3.5]`, not a float — further evidence nothing consumes it here.)

T2V, for contrast, carries `[4.0, 3.0]`
(`configs/distill/wan22/wan_moe_t2v_distill_lora.json`) with `enable_cfg` also
false — same dead-value situation, and a hint the numbers are leftovers from a
CFG-distillation ablation.

### 1b. `denoising_step_list` is indices, not timesteps — the trap

This is the one thing a diffusers reimplementation will get wrong.
`lightx2v/models/schedulers/wan/step_distill/scheduler.py:25-33`:

```python
sigma_start = self.sigma_min + (self.sigma_max - self.sigma_min)      # = 1.0
self.sigmas = torch.linspace(sigma_start, self.sigma_min, 1001)[:-1]  # 1000 pts
self.sigmas = self.sample_shift * self.sigmas / (1 + (self.sample_shift - 1) * self.sigmas)
self.timesteps = self.sigmas * self.num_train_timesteps
self.denoising_step_index = [self.num_train_timesteps - x for x in self.denoising_step_list]
self.timesteps = self.timesteps[self.denoising_step_index]
```

So `[1000, 750, 500, 250]` becomes **indices** `[0, 250, 500, 750]` into a
1000-point sigma grid that has *already* had the flow-matching shift applied.
Working it through with `shift = 5.0` (σ_shifted = 5σ/(1+4σ)):

| step | index | σ pre-shift | σ post-shift | timestep fed to model |
|---|---|---|---|---|
| 0 | 0 | 1.00 | 1.0000 | 1000.0 |
| 1 | 250 | 0.75 | 0.9375 | 937.5 |
| 2 | 500 | 0.50 | 0.8333 | 833.3 |
| 3 | 750 | 0.25 | 0.6250 | 625.0 |

The sigmas the model actually sees are `[1.0, 0.9375, 0.8333, 0.625]` — **not**
`[1.0, 0.75, 0.5, 0.25]`. Naively handing diffusers
`timesteps=[1000, 750, 500, 250]`, or letting it build its own 4-step shifted
schedule, gives a different (much steeper) trajectory. To reproduce exactly in
diffusers: set `FlowMatchEulerDiscreteScheduler`'s sigmas to those four values
with a trailing `0.0`.

The update rule is plain flow-matching Euler
(`scheduler.py:80-89`, `Wan22StepDistillScheduler.step_post`):

```python
x0 = latents - flow_pred * sigma            # predict clean
latents = x0 + flow_pred * sigma_next       # re-noise to next sigma (skipped on last step)
```

i.e. `x_{n+1} = x_n - (σ_n - σ_{n+1}) · v`, standard Euler. No special
integrator to port.

### 1c. Expert switching is by step index, and it agrees with boundary 0.9

`boundary_step_index: 2` switches on *step count*, not on a sigma threshold:
`wan_distill_runner.py:61` — `if self.scheduler.step_index < self.boundary_step_index:`
→ high-noise expert for steps 0-1, low-noise for steps 2-3.

Diffusers/official Wan 2.2 instead thresholds on a `boundary` sigma. The two
agree here: with σ = `[1.0, 0.9375, 0.8333, 0.625]` and the official I2V
boundary of `0.900` (which lightx2v also states explicitly as `"boundary": 0.900`
in `configs/distill/wan22/wan_moe_i2v_distill_int8_4step_ulysses_npu.json`),
the split is high/high/low/low — **the same 2+2**. So a sigma-boundary
diffusers pipeline and this index-boundary one land in the same place, and a
2+2 expert split is the correct target to verify against.

`Wan22StepDistillScheduler` also derives `sigma_bound = sigmas[2]` (= 0.8333)
and a `calculate_alpha_beta_high()` (`scheduler.py:75-78`), which are not used
by `step_post` — training-side or unused, not needed for inference parity.

The `LightX2VPipeline.create_generator` defaults (`lightx2v/pipeline.py:171-173`)
restate the same recipe as library defaults: `boundary=0.900`,
`boundary_step_index=2`, `denoising_step_list=[1000, 750, 500, 250]`. (There is
also a `distilled_sigma_values` override that takes explicit sigmas, but it is
wired only for LTX-2 and lingbot — `models/schedulers/ltx2/scheduler.py:317`,
`models/schedulers/lingbot_video/scheduler.py:43` — *not* the Wan path.)

### 1d. Newer weights exist than the ones the configs point at

`README.md:66` (news, 2026-04-20) releases 4-step I2V weights **trained on a
720p dataset with a reworked low-noise objective**, claiming better fine detail
and texture than earlier revisions:

- `wan2.2_i2v_A14b_high_noise_lightx2v_4step_720p_260412.safetensors`
- `wan2.2_i2v_A14b_low_noise_lightx2v_4step_720p_260412.safetensors`

in `huggingface.co/lightx2v/Wan2.2-Distill-Models`. These supersede the
`_1022` LoRAs referenced throughout `configs/` — the repo's configs lag its own
model releases, and the `260412` weights appear **only** in that README line,
in no config or script.

Caveat, and it is the awkward one: the `260412` pair are **full merged
checkpoints**, not LoRAs. Enumerating every Wan 2.2 weight file referenced
anywhere in `configs/`, `examples/` and `scripts/` turns up exactly two I2V
LoRA revisions — `..._lora_rank64_lightx2v_4step_1022.safetensors`, high and
low — plus merged checkpoints at `_4step`, `_4step_1030` and fp8/int8 variants.
So there is **no 720p LoRA** in this repo's world: the 720p detail/texture
improvement is available only by swapping the whole transformer. For a
diffusers pipeline the `_1022` rank-64 LoRAs remain the easy integration, and
the 720p merged checkpoints are a separate, heavier experiment — but "boosts
fine-grained detail rendering and visual texture" is precisely the axis this
project has been fighting, so they are worth a look on the HF repo listing (it
may carry revisions the README never mentioned).

---

## 2. What lightx2v is, and what it accelerates

A **general** lightweight inference framework for diffusion video/image models,
Apache-2.0 — not Wan-specialised, though Wan is its best-covered family. It
carries runners for Wan 2.1/2.2 (+ VACE, Animate, S2V), HunyuanVideo 1.5,
LTX-2, Qwen-Image, Flux2, SeedVR2, Cosmos, Self-Forcing and more
(`lightx2v/pipeline.py:14-40` imports ~25 runner classes). Architecturally it
is a **registry framework**: attention ops, matmul/quant ops, schedulers and
runners each register under a string key and are selected by config, which is
why the config JSONs read as the real API.

Acceleration techniques, all selectable per-config:

| technique | where | notes |
|---|---|---|
| step distillation | `models/schedulers/wan/step_distill/`, `configs/distill/` | their own 4-step Lightning weights + CFG removal |
| quantisation | `common/ops/mm/`, registry keys below | fp8/int8/int4/nvfp4/mxfp4/mxfp6/mxfp8/GGUF |
| attention backends | `common/ops/attn/` | 20+ files; sage2/3, flash2/3/4, sparse variants, SDPA |
| sparse attention | `rainfusion_attn.py`, `radial_attn.py`, `svg_attn.py`, `nbhd_attn.py`, `draft_attn.py` | e.g. rainfusion `sparsity: 0.8` |
| feature caching | `configs/caching/` | TeaCache, MagCache, AdaCache, TaylorSeer, first/dual/dynamic-block |
| CPU/disk offload | `enable_offload(...)`, `configs/offload/` | `block` / `phase` / `model` granularity, lazy load |
| parallelism | `configs/dist_infer/`, `parallel` key | Ulysses + ring seq-parallel, CFG-parallel, TP |
| disaggregated serving | `lightx2v/disagg/` | Mooncake-based |
| VAE tricks | `setup_vae.py`, LightTAE | distilled/lightweight decoders |
| frame interpolation | `video_frame_interpolation` key | RIFE, e.g. 16→30fps |

Quant registry keys (`common/ops/mm/`, via
`grep MM_WEIGHT_REGISTER`): `fp8-triton`, `int8-triton`, `fp8-sgl`, `int8-sgl`,
`fp8-q8f`, `int8-q8f`, `fp8-vllm`, `int8-vllm`, `fp8-torchao`, `int8-torchao`,
`fp8-pertensor`, `fp8-b128-deepgemm`, `int4-g128-marlin`, `nvfp4`, `mxfp4`,
`mxfp8`, `mxfp6-mxfp8`, plus a full GGUF ladder (`gguf-Q4_K_M` … `gguf-Q8_0`).

### What they claim, and how honestly

The headline table (`README.md:~120-146`, "Updated on 2025.12.01") is
**Wan2.1-I2V-14B-480P, 40 steps, 81 frames**, reported as **s/it** — a
per-step time, so it isolates the engine from the step count. That is a
fair-minded unit. Single-GPU H100: Diffusers 9.77 s/it → LightX2V 5.18 s/it
(**1.9x**); vs xDiT 8.93, FastVideo 7.35, SGL-Diffusion 6.13. On RTX 4090D
single-GPU: Diffusers 30.50 → LightX2V 20.26 (**1.5x**), with xDiT and
SGL-Diffusion OOM-ing outright. Their own stack table adds no-CFG (1.9x) and
+fp8 (2.1x) on top, 8-GPU H100.

So the **engine-only** win over diffusers is ~1.5-1.9x per step. Every
eye-catching number above that (the "50x", "42x", "25x") is
*step-count × CFG × quant* compounded against a 40-or-50-step CFG baseline —
i.e. mostly the distillation, which is a *weights* win we can have in diffusers
for free. Worth keeping the two apart when reading their marketing.

The one claim aimed squarely at this project's hardware: `README.md:62`
(2026-05-29) — [`lightx2v/Wan2.2-NVFP4-Sparse`](https://huggingface.co/lightx2v/Wan2.2-NVFP4-Sparse),
NVFP4 quantisation-aware step distillation + sparse attention **for Blackwell**,
">50x speedup on a single RTX 5090". NVFP4 is a 4-bit format with real hardware
support on sm_120, so this is not vapour — but see §3 for what it costs to run.

---

## 3. Windows + Blackwell viability

**Verdict: genuinely viable, and it degrades gracefully.** Windows is a
first-class target, not an afterthought.

Evidence:

- `requirements_win.txt` exists and is Windows-shaped: `triton-windows`,
  `torchao`, no flash-attn, no sgl-kernel.
- `scripts/win/run_wan_i2v.bat`, `scripts/win/run_wan_t2v.bat`.
- A whole guide: `docs/EN/source/deploy_guides/deploy_local_windows.md`, plus
  a Windows section in `docs/EN/source/getting_started/quickstart.md`
  ("Operating System: Linux (Ubuntu 18.04+) or **Windows 10/11**").
- A prebuilt one-click Gradio bundle (`env/` + `LightX2V/` + `.bat`), and
  **"Note for RTX 50 Series GPU Users: we provide a dedicated runtime
  environment"** as a separate download. Both are hosted on Quark Cloud (a
  mainland-China file host) — usable but not a supply chain I would drop into
  a $0 pipeline without inspection.

### Do custom kernels need building? Mostly no.

This is the important part. Three tiers:

1. **Zero-build tier.** `torch_sdpa` is a registered attention backend
   (`common/ops/attn/torch_sdpa.py:11`) that is pure `F.scaled_dot_product_attention`.
   Quantisation defaults to **Triton** kernels — the Windows guide, step 7:
   *"By default, LightX2V uses Triton kernel for quantization inference, which
   is efficient and requires no additional dependencies. Just ensure that
   `triton-windows` is installed."* Registry confirms `fp8-triton` / `int8-triton`
   exist. So `attn_mode="torch_sdpa"` + `*-triton` quant runs on Windows with
   **no compilation at all**.
2. **Prebuilt-wheel tier.** SageAttention 2 and Flash-Attention 2 install from
   Windows wheels; the guide links two community wheel repos
   (`woct0rdho/SageAttention`, `sdbds/SageAttention-for-windows`) and notes
   "SageAttention's CUDA version doesn't need to be strictly aligned, but Python
   and PyTorch versions must match". vLLM-for-Windows wheels
   (`SystemPanic/vllm-windows`) are optional, only for `*-vllm` quant.
3. **Source-build tier (Linux-leaning).** `lightx2v_kernel/` is a CUTLASS/CMake
   C++ extension and is where NVFP4/MXFP8 live. `lightx2v_kernel/CMakeLists.txt:80`
   builds `-gencode=arch=compute_120a,code=sm_120a` (note line 79, plain
   `sm_120`, is **commented out** — they target the `a` variant specifically),
   compiling `nvfp4_scaled_mm_kernels_sm120.cu`, `mxfp8_*_sm120.cu`, etc. This
   is the tier the "50x NVFP4-Sparse" claim depends on, and it is the one tier
   with a real Windows/MSVC risk. `models/networks/wan/infer/mxfp8_fuse.py:42`
   warns and **falls back** if the device is not SM120/SM120a, so the guard is
   the other direction — the code is fine with a 5090, the question is only
   whether the toolchain builds.

### The sm_120 detail worth knowing regardless of lightx2v

`common/ops/attn/sage_attn.py:26-37`:

```python
capability = torch.cuda.get_device_capability(0) if torch.cuda.is_available() else None
if capability in [(8, 9), (12, 0)]:
    from sageattention import sageattn_qk_int8_pv_fp16_triton as sageattn
else:
    from sageattention import sageattn
```

`(12, 0)` is sm_120 — consumer Blackwell, i.e. the 5090. On that card they
deliberately route `sage_attn2` to the **Triton** implementation rather than the
CUDA one. Useful intelligence even if we never adopt the engine: it says the
maintainers found the compiled SageAttention2 CUDA path unreliable or absent on
sm_120 and chose Triton there.

`sage_attn3` (used by `configs/distill/wan22/wan_moe_i2v_distill_5090.json`)
imports `sageattn3_blackwell` from a separate `sageattn3` package
(`sage_attn.py:53-56`) — SageAttention 3 is Blackwell-only and access-gated, so
treat that config as aspirational rather than a drop-in.

**Every** optional accelerator import is `try/except ImportError` with a log
line and a `None` sentinel (`sage_attn.py:22-69` is five such blocks in a row).
The engine is built to run degraded, which is the right shape for a Windows box.

One friction point: `pyproject.toml` pins `torch<=2.8.0`,
`torchvision<=0.23.0`, `torchaudio<=2.8.0`. Fine for a 5090 (cu128 support
landed in torch 2.7), but it will fight any newer torch already installed for
Blackwell.

There is also an official `lightx2v/lightx2v` Docker image
(`26052801-cu130`, cu128 and cu124 tags) — the clean escape hatch if the
Windows path bogs down, WSL2 permitting.

---

## 4. Is it adoptable as a library? Yes — but we don't want it.

**It is genuinely library-shaped**, unlike Wan2GP. `lightx2v/pipeline.py`
exposes a real class with a fluent API, and `examples/` has 60+ scripts using
it as an import:

```python
from lightx2v import LightX2VPipeline
pipe = LightX2VPipeline(model_path=..., model_cls="wan2.2_moe_distill", task="i2v")
pipe.enable_offload(cpu_offload=True, offload_granularity="block", ...)
pipe.enable_lora([{"name": "high_noise_model", "path": ..., "strength": 1.0}, ...])
pipe.create_generator(attn_mode="sage_attn2", infer_steps=4, height=480, width=832,
                      num_frames=81, guidance_scale=1, sample_shift=5.0)
pipe.generate(seed=42, image_path=..., prompt=..., negative_prompt=..., save_result_path=...)
```

It also `pip install`s from git, has a `pyproject.toml`, a documented
`switch_lora()` for hot-swapping expert LoRAs
(`models/runners/wan/wan_distill_runner.py:193`), and an OpenAI-ish server under
`lightx2v/server/`. So "app-shaped like Wan2GP" is **not** a fair charge.

But adopting it means **replacing** our diffusers pipeline, not augmenting it:

- It is a parallel universe to diffusers. It reimplements the transformer
  (`models/networks/wan/model.py`), weights loading, schedulers and VAE
  handling against its own registries. There is no "use lightx2v's scheduler
  inside a diffusers pipeline" seam.
- `lightx2v/pipeline.py` eagerly imports every runner (25+ model families) at
  module import, dragging `lightx2v_platform`, `qtorch`, `swanlab`, `gradio`,
  `fastapi` and friends into the process.
- Its per-step engine win over diffusers is the ~1.5-1.9x from §2 — real, but
  the same order as choosing a decent attention backend, and far less than the
  step-distillation win we can get in diffusers with the LoRAs alone.

**Recommendation: mine it, don't adopt it.** The valuable export is §1 — the
sigma schedule, the 2+2 expert split, LoRA strength 1.0/1.0, and above all
"CFG off, `guidance_scale=1`, ignore the 3.5". That is ~20 lines of scheduler
setup in our existing diffusers pipeline. Revisit the engine only if (a) we
want NVFP4 on the 5090 badly enough to fight a CUTLASS build, or (b) the
720p `260412` merged checkpoints prove much better and we want their offload
machinery to fit two A14B experts in 24GB.

---

## 5. VBench Dynamic Degree — how the field measures "frozen frames"

`vbench/dynamic_degree.py`, 164 lines total. The whole method:

1. **Frames** (`:96-113`). Decode with cv2, resample to ~8 fps:
   `interval = max(1, round(fps / 8))`, keep every `interval`-th frame. Our
   16 fps clips → every 2nd frame; 24 fps → every 3rd.
2. **Optical flow** (`:77`). RAFT, `iters=20`, `test_mode=True`, on each
   consecutive sampled pair.
3. **Per-pair score** (`:42-56`). Flow magnitude `rad = sqrt(u² + v²)` per pixel,
   then take the mean of the **largest 5%** of magnitudes:
   `cut_index = int(h*w*0.05)`; `max_rad = mean(sort(-rad)[:cut_index])`.
4. **Adaptive params** (`:59-61`):
   ```python
   scale = min(frame.shape[-2:])                      # short side, in px
   thres     = 6.0 * (scale / 256.0)
   count_num = round(4 * (count / 16.0))              # count = n sampled frames
   ```
5. **Verdict** (`:84-93`). Count pairs whose `max_rad > thres`; return `True`
   as soon as the count reaches `count_num`. **Per clip the result is a
   boolean.** The reported dimension score (`:141-149`) is just the *fraction
   of clips judged moving*.

Worked for our case, 81 frames @ 16 fps, 704x1280: sampled count ≈ 41,
`count_num = round(4*41/16) = 10`, `thres = 6.0*704/256 = 16.5` px. So: at
least 10 of ~40 frame-pairs must show ≥16.5 px of flow in their top-5% pixels.
At 480x832 the threshold drops to 11.25 px.

### How this differs from our median-frame-diff score — and why ours may be wrong

Two substantive differences, both in VBench's favour:

- **Optical flow, not pixel difference.** Frame-diff conflates *motion* with
  exposure drift, film-grain noise, compression breathing and global fades.
  Flow measures actual displacement. A clip that flickers in brightness while
  standing perfectly still scores high on frame-diff and ~0 on flow.
- **Top 5%, not the median.** This is the big one. VBench deliberately looks at
  the *most-moving* 5% of pixels, so "small subject moves, background static"
  registers as motion. A **median** over all pixels does the opposite: with a
  static background filling most of the frame, the median pixel barely changes
  and the clip reads as frozen *even when the character is moving*.

That second point bears directly on this project's history: the failure being
chased is hand/character motion against largely static anime backgrounds, and
the K recipe was chosen on our own metric and then rejected by eye as
"literally just frozen frames". A median-frame-diff score is *structurally*
mismatched to that judgement in both directions — it under-credits real
subject motion and over-credits whole-frame shimmer. Switching to a top-5%
statistic is worth doing even if we keep frame-diff and never touch RAFT.

### Running just this metric, locally, at $0 — yes, and it's cheap

- `DynamicDegree` (the class) depends only on **torch, cv2, numpy, easydict**
  plus RAFT. `vbench.utils` (which drags in `decord`) is imported only by the
  `compute_dynamic_degree` wrapper for benchmark-manifest loading — not needed.
- **RAFT is fully vendored** in `vbench/third_party/RAFT/core/` — 352 KB of
  pure torch, no build step, no external package.
- Weights: `raft-things.pth`, fetched at `vbench2_beta_i2v/utils.py:376` from
  `https://dl.dropboxusercontent.com/s/4j4z58wuv8o0mfz/models.zip` (~20 MB).
  A Dropbox link of that vintage is a rot risk; **torchvision now ships RAFT
  natively** (`torchvision.models.optical_flow.raft_large`, `C_T_V2` weights =
  Chairs+Things, the same training recipe as `raft-things`). Using torchvision's
  copy means vendoring *nothing* — my recommendation — at the cost that absolute
  scores won't be bit-comparable to published VBench numbers. Irrelevant for
  internal A/B, so long as we don't quote our numbers as "VBench Dynamic Degree".
- **Do not `pip install` VBench.** Its `requirements.txt` pins `numpy<2.0.0`,
  `transformers==4.33.2`, `decord`, `detectron2`, `lvis`, `pyiqa`, `fairscale`
  — it would wreck a working diffusers environment. Extract the metric instead.

**One change to make regardless of adoption:** keep the continuous
`static_score` list (`dynamic_degree.py:79`), not just the boolean. The boolean
cannot rank two candidate recipes — every non-frozen clip returns `True`. For
A/B work the useful number is the per-pair top-5% flow magnitude series, from
which the boolean is a trivial derivation.

---

## 6. Subject Consistency / I2V faithfulness — the invention problem, upstream

There are two relevant metrics and they are not the same.

### 6a. `subject_consistency` (T2V dimension) — closest to our invention detector

`vbench/subject_consistency.py:49-64`. DINO ViT-B/16 features per frame,
L2-normalised, then for every frame `i > 0`:

```python
sim_pre = max(0.0, cos(feat[i-1], feat[i]))     # vs previous frame
sim_fir = max(0.0, cos(feat[0],   feat[i]))     # vs FIRST frame
cur_sim = (sim_pre + sim_fir) / 2
```

averaged over frames. The `sim_fir` term is precisely the "does the clip stay
anchored to its first frame" idea our `check_invention.py` hand-rolled — the
field's version is an even 50/50 blend of first-frame anchoring and
frame-to-frame smoothness, in DINO feature space rather than pixel space.

### 6b. `i2v_subject` (VBench-I2V) — anchored to the *conditioning image*

`vbench2_beta_i2v/i2v_subject.py:19-64`. Same DINO ViT-B/16, but the anchor is
the **input image**, not frame 0:

```python
conformity[i] = max(0.0, cos(DINO(input_image), DINO(frame_i)))   # all frames
consec[i]     = max(0.0, cos(DINO(frame_{i-1}), DINO(frame_i)))   # i > 0

video_score = 0.4*max(conformity) + 0.3*mean(consec) + 0.3*min(consec)
```

`i2v_background` (`vbench2_beta_i2v/i2v_background.py:19-64`) is the **identical
formula** with **DreamSim** embeddings substituted for DINO. (The README §3
claims background consistency uses DINO features — that contradicts the code,
which does `from dreamsim import dreamsim`. Trust the code.)

**A caveat I'd flag before we copy this.** The conformity term uses **`max`**,
not `mean`. For any I2V model that faithfully reproduces its conditioning image
at frame 0 — which Wan does — `max(conformity)` is pinned near 1.0 by frame 0
alone, making that 0.4 nearly a free constant. The remaining 0.6 is
`mean + min` of *consecutive* similarity, i.e. temporal smoothness. So
`i2v_subject` is, in practice, mostly a smoothness metric that is *insensitive
to exactly the failure we care about*: a clip can start on the input image and
then invent an entirely different scene, and still score well as long as it
drifts smoothly. Our own "does it return toward the first frame" instinct is
arguably measuring something sharper than the published I2V metric. That is a
real finding, not a reason to discard theirs — but it means "adopt VBench's
i2v_subject" would be a **downgrade** on the invention axis specifically.

The honest synthesis: take VBench's **feature space** (DINO instead of pixels —
robust to lighting, grain, and global shifts, sensitive to content identity) and
keep **our own aggregation** (something like `mean` or `min` of conformity
against the conditioning frame, which actually punishes drift). Both are 30
lines on top of a DINO forward pass.

### What adopting it costs

- Model: DINO ViT-B/16, `dino_vitbase16_pretrain.pth` (~330 MB) from
  `dl.fbaipublicfiles.com`, loaded via `torch.hub.load('facebookresearch/dino:main', 'dino_vitb16')`
  (`vbench2_beta_i2v/utils.py:306-332`). $0, local, no build. A `local=True`
  mode clones the dino repo and wgets the checkpoint into `~/.cache/vbench`.
  (timm's `vit_base_patch16_224.dino` is the same weights without the torch.hub
  clone, if we want to avoid a git dependency at runtime.)
- Transforms are trivially reproducible (`vbench/utils.py:49-61`):
  `Resize(224)` (no centre-crop, `antialias=False`) + ImageNet
  mean/std `(0.485,0.456,0.406)/(0.229,0.224,0.225)`.
- `i2v_background` additionally needs the `dreamsim` package (own weight
  download). Skippable — the formula is identical, so DINO alone covers the
  concept.

---

## 7. VBench-I2V as a suite — dimensions, submission cost, local feasibility

Dimension list, `vbench2_beta_i2v/__init__.py:12-13`:

- **I2V-specific (3):** `i2v_subject`, `i2v_background`, `camera_motion`
  (CoTracker2 via torch.hub, `utils.py:337-341`).
- **Quality, reused from VBench v1 (7):** `subject_consistency`,
  `background_consistency` (CLIP ViT-B/32), `aesthetic_quality`,
  `imaging_quality`, `temporal_flickering`, `motion_smoothness` (AMT-S),
  `dynamic_degree` (RAFT).

Also present in the clone but out of scope here: `VBench-2.0/` (a separate,
larger benchmark) and `vbench2_beta_long/`, `vbench2_beta_trustworthiness/`.

### What a real submission requires — and why we should not attempt one

From `vbench2_beta_i2v/README.md` §4: for **each image-prompt pair, sample 5
videos**, named `$prompt-$index.mp4` with `$index` 0-4, seeds random and
recorded, not cherry-picked. Prompt counts per dimension: `i2v_subject` 246,
`i2v_background` 109, `camera_motion` 763, `aesthetic_quality`/`imaging_quality`
355. The input images come from their own high-res suite (mostly 4K+), which
must be downloaded from Google Drive via `gdown` and cropped to *our* aspect
ratio with `crop_to_diff_ratio.py` (they ship 1:1, 8:5, 7:4, 16:9 — note **9:16
vertical is not among them**, which matters for us).

Cost: `i2v_subject` alone is 246 x 5 = **1,230 clips**; the full I2V suite is
several thousand per model. At a few minutes per 81-frame clip on one 5090,
that is days-to-weeks **per model** — so for 4 candidate models, comparing on
the official suite is flatly infeasible on our hardware, before even counting
the 9:16 mismatch and the fact that their suite's photographic 4K stills are
nothing like our anime keyframes.

### What *is* feasible: the metrics on our own clips

`mode='custom_input'` (`vbench/__init__.py:46-76`) accepts an arbitrary folder
of mp4s, deriving prompts from filenames, and `custom_image_folder` supplies the
conditioning image per clip — exactly the shape of a 4-model bake-off on our own
15 beats. Every metric is an independent function
(`compute_<dimension>(json_dir, device, submodules_list)`), so dimensions can be
run one at a time.

Runtime is dominated by small vision models, not generation: DINO ViT-B/16 and
RAFT over ~40 sampled frames per clip is seconds per clip on any of our
machines — it would run on the M1 Mac, let alone the 5090. **The evaluation is
free; only the official prompt suite is expensive.**

---

## Bottom line

1. **Lightning recipe (authoritative, §1).** 4 steps; sigmas
   `[1.0, 0.9375, 0.8333, 0.625]` (from `denoising_step_list [1000,750,500,250]`
   read as *indices* into a shift-5.0 grid — not timesteps); `shift = 5.0`;
   plain flow-matching Euler; expert switch after step 2 (equivalent to
   `boundary = 0.900`); both LoRAs at `strength 1.0`; **CFG off,
   `guidance_scale = 1`** — the `3.5` in their config is dead code
   (`wan_distill_runner.py:63,73` commented out). Also: newer 720p-trained
   `260412` checkpoints exist and supersede the `_1022` LoRAs the configs cite.
2. **lightx2v engine: mine, don't adopt.** It is a real library, not a Wan2GP-style
   app, and Windows + RTX 5090 is genuinely supported (Triton quant needs no
   build; `torch_sdpa` needs nothing; SageAttention2 auto-routes to Triton on
   sm_120 per `sage_attn.py:26-37`; only the NVFP4/CUTLASS tier needs compiling).
   But its engine-only win over diffusers is ~1.5-1.9x/step, and adopting it
   means replacing our diffusers pipeline wholesale. Take the numbers, keep the
   pipeline. Watch the `torch<=2.8.0` pin.
3. **VBench metrics: worth adopting, with one correction.** Dynamic Degree is a
   better motion metric than ours on two counts (optical flow over pixel diff;
   **top-5% over median** — our median statistic structurally misreads "subject
   moves, background static", which is our actual failure mode). Adopt it via
   torchvision's `raft_large` rather than vendoring, and keep the continuous
   flow series instead of their boolean. For invention, take VBench's **DINO
   feature space** but **not** their `i2v_subject` aggregation — its `max`-based
   conformity term is nearly constant for image-faithful models and would be a
   downgrade on precisely the drift axis we care about.
   **Effort: roughly half a day** for both (each is ~30-60 lines around one
   pretrained forward pass, no builds, ~350 MB of weights, all $0 and local).
   Do *not* `pip install vbench` — its pins would break the render env.
