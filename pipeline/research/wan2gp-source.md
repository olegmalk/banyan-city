# Wan2GP + mmgp source read — what is portable to our diffusers pipeline

Read-only source study, 2026-08-04. No code was executed.

Sources cloned shallow (`--depth 1`) to scratchpad:

- `deepbeepmeep/Wan2GP` @ HEAD — the app (`wgp.py` is **773,988 bytes / one file**).
- `deepbeepmeep/mmgp` @ `bc3f618` — the memory library. **Wan2GP does not vendor it**;
  `requirements.txt:2` pins `mmgp==3.7.11`. All the memory tech lives in
  `mmgp/src/mmgp/offload.py` (3902 lines). Reading only Wan2GP would have
  missed 100% of it.

## LICENCE FLAG — read before porting a single line

`mmgp/LICENSE.md` is **GPL-3.0**. The `mmgp/README.md:174` separately claims
"free to use my module for non commercial use as long you give me proper
credits", and `pyproject.toml:11` declares `license-files = ["LICENSE.md"]`.
Those two statements do not agree with each other.

Consequences for us, both of which matter because this repo IS the public product:

- **Copy code from `offload.py` into our pipeline → our repo inherits GPL-3.**
  Copyleft is file-level viral for derivative works. banyan-city is currently
  a public repo whose licence posture is tracked in
  `pipeline/research/models-licence.md`; taking mmgp source would be the single
  biggest licence event in the repo's history.
- **`pip install mmgp` and calling it is the ordinary GPL "mere use" case** and
  is a much weaker claim on us than copying source — but the README's
  "non commercial" line is a separate, non-OSI restriction that a GPL-3 licence
  file does not authorise the author to add, and we would be relying on which
  of two contradictory statements wins.

**The techniques below are not themselves copyrightable — the ideas
(pinned staging buffer, second stream prefetch, partial preload) can be
reimplemented from this description.** That is the recommended route and it is
what the port estimates assume: *reimplement from the description, do not
paste*. Flag to founder before either route (this is a licence/governance
call, not a steward call).

---

## 1. THE MEMORY TECH — how block swap actually works

### 1.1 The core trick: parameters are swapped by `setattr`, not by buffer copy

There is no preallocated VRAM arena and no `copy_` into a fixed buffer. mmgp
keeps a permanent Python-side registry of the **CPU** tensors and swaps
`module.<param_name>` between the CPU tensor and a fresh CUDA copy.

Registry build — `offload.py:2591-2614` (`add_module_to_blocks`):

```python
for k,p in submodule.named_parameters(recurse=False):
    ref = _get_tensor_ref(p)
    tied_param = self.parameters_ref.get(ref, None)
    blocks_params.append((submodule, k, p, False, tied_param))
```

`blocks_of_modules[entry_name]` is a list of
`(parent_module, param_name, cpu_tensor, is_buffer, tied_param)`. That list
holds the only strong reference to the CPU tensor, keyed by
`entry_name = f"{model_id}/{blocks_name}"`.

Load — `offload.py:2715-2720`:

```python
q = p.to("cuda", non_blocking=True)
q = _make_buffer(q) if is_buffer else _make_parameter(q, requires_grad=False)
setattr(parent_module, n, q)
```

Unload — `offload.py:2799-2805`: re-`setattr`s the *original CPU tensor* `p`
back onto the module. The GPU copy dies by refcount. No `del`, no
`empty_cache()` on the hot path.

Why this design is good: it works on **any** `nn.Module` with no model-side
changes, survives quantised tensors (`_get_quantized_subtensors`,
`offload.py:440`), and handles **tied weights** — a second parameter aliasing
the same storage gets pointed at the already-moved GPU tensor
(`offload.py:2703-2707`, `2722-2723`) instead of being copied twice.

### 1.2 What triggers a swap: a per-module `forward` wrapper

Every submodule's `forward` is replaced (`hook_check_load_into_GPU_if_needed`,
`offload.py:3282-3296`). The wrapper calls `_pre_check` (`offload.py:3245-3256`)
which is decorated `@torch._dynamo.disable`:

```python
self.ensure_model_loaded(model_id)
if blocks_name is None: ...
elif blocks_name != self.loaded_blocks[model_id] and \
     blocks_name not in self.preloaded_blocks_per_model[model_id]:
    self.gpu_load_blocks(model_id, blocks_name)
```

So the swap is **lazy and demand-driven** — entering transformer block N's
forward is what loads block N. Note `_get_wrapper_for_type`
(`offload.py:3258-3280`) `exec`s a *uniquely named function per module class*
specifically so `torch.compile` produces one code object per class; the comment
at `3266` says all heavy logic is kept out-of-graph in `_pre_check`. This is
the compile-compatibility hack.

### 1.3 Async prefetch — one extra CUDA stream, full-device sync

Streams are created once (`offload.py:2561-2562`):

```python
self.default_stream  = torch.cuda.default_stream(torch.device("cuda"))
self.transfer_stream = torch.cuda.Stream()
```

The prefetch logic (`offload.py:2747-2764`) is small enough to quote whole:

```python
if self.async_transfers and blocks_name != None:
    prev = self.prev_blocks_names[entry_name]
    first = prev == None or prev != loaded_block
    next_blocks_entry = self.next_blocks_names.get(entry_name)
    if first:
        cpu_to_gpu(torch.cuda.current_stream(), self.blocks_of_modules[entry_name])
    torch.cuda.synchronize()
    if next_blocks_entry != None:
        cpu_to_gpu(self.transfer_stream, self.blocks_of_modules[next_blocks_entry])
```

Read that as: *if block N was already prefetched by block N-1, skip the
blocking load entirely; then kick off block N+1 on the transfer stream and
return, so N+1's H2D copy overlaps N's compute.* `first` is False in the steady
state, which is the whole point — the blocking load only happens on entry to
the chain.

Two honest weaknesses worth knowing before we copy the idea:

- It uses **`torch.cuda.synchronize()`** (full device barrier), not
  `Event.wait()` / `stream.wait_stream()`. Simple and correct, but it also
  waits on unrelated work. An event-based port would be strictly better.
- Prefetch depth is **exactly 1** block. There is no `prefetch_blocks`
  N-deep knob anywhere in `offload.py` (grepped: no such symbol). Depth-1 is
  all there is; the tuning lever is instead *how many blocks are permanently
  resident* (§1.5).

### 1.4 Pinned memory — packed into few big buffers, not per-tensor

`non_blocking=True` is a no-op from pageable memory, so pinning is what makes
§1.3 actually asynchronous. mmgp does not pin tensor-by-tensor; `_pin_sd_to_memory`
(`offload.py:513`) / `_move_to_pinned_tensor` (`offload.py:332`) copy many small
tensors into **one big pinned slab** at an offset, capped by
`BIG_TENSOR_MAX_SIZE`. It also pre-extracts tied weights
(`_extract_tie_weights_from_sd`, `offload.py:485`) so aliases are not pinned twice,
and caps total pinning against `_get_max_reservable_memory` /
`perc_reserved_mem_max` (`offload.py:231-243`) so it cannot lock the box up.

Pinning is the cheapest large win available to us and the least entangled with
their app (see ranking in §1.6).

### 1.5 `tune_preloading` — the part I did not expect, and the best idea here

`offload.py:3377-3451`. Rather than stream every block, mmgp decides how many
blocks can stay **permanently resident** in the budget and streams only the
remainder.

- `_detect_main_towers` (`offload.py:244`) auto-finds the repeated block stacks
  ("towers" of "floors", i.e. `blocks.0..N`), `min_floors=5`.
- Budget accounting (`3386-3407`): subtract the model's non-block base size,
  then subtract `2 * max_floor_size` **per tower** — that is the explicit
  reservation for the async double buffer, and it confirms the README's
  "asyncTransfers requires twice the budget".
- `preload_blocks_count = int(tower_budget / max_floor_size)` (`3411`), and the
  preloaded blocks are spread **evenly** through the stack via
  `space_between = (nb_blocks - preload_blocks_count) / preload_blocks_count`
  (`3420`) — not the first K. Even spacing means the streamed blocks are
  interleaved with resident ones, so each streamed block's prefetch has a
  resident block's compute to hide behind.
- The non-preloaded blocks are relinked into their own chain (`3430-3431`), and
  when there is a single tower the chain is closed into a **circle**
  (`3439-3441`): the last streamed block prefetches the first, so step N+1's
  block 0 is already in flight while step N finishes. Their log calls this a
  "circular shuttle" (`3449`).

This is the single most valuable idea in the codebase for us: it degrades
smoothly from "everything resident" (24GB, big model) to "3 blocks resident"
(8GB) with one number, and the even-spacing + circular-link details are
non-obvious enough that we would not have invented them.

### 1.6 Cache hygiene on the hot path

`empty_cache_if_needed` (`offload.py:2884-2895`) only calls
`torch.cuda.empty_cache()` when reserved ≥ 0.9·capacity **and** allocated ≤
0.70·reserved — i.e. only when the allocator is badly fragmented, never
routinely. It is rate-limited to once per 200 ms by `ready_to_check_mem`
(`offload.py:2873-2881`), whose comment notes querying reserved memory is
itself expensive, and it is skipped entirely when anything is compiled
(`2874-2875`). Worth copying verbatim in spirit: our own pipelines' habit of
calling `empty_cache()` per step is a measurable tax.


---

## 2. Their A14B-on-consumer-hardware recipe

Scratchpad paths for the citations below:
`.../scratchpad/wan2gp/` and `.../scratchpad/mmgp/`.

### 2.1 Two experts = two separate checkpoints, held simultaneously

`defaults/i2v_2_2.json` is the whole A14B config and it is short. The expert pair
is expressed as two URL lists:

- `URLs` → `wan2.2_image2video_14B_high_*` (high-noise expert)
- `URLs2` → `wan2.2_image2video_14B_low_*` (low-noise expert)

Each list offers three formats, and the order matters — it is the quality/VRAM ladder:

1. `..._mbf16.safetensors` — full bf16
2. `..._quanto_mbf16_int8.safetensors` — **prequantized** quanto int8, bf16 compute
3. `..._quanto_mfp16_int8.safetensors` — prequantized quanto int8, fp16 compute

The models are rehosted under `huggingface.co/DeepBeepMeep/Wan2.2/`, not fetched
from the official Wan repo.

Note what this means: **they do not on-the-fly quantize A14B by default, they
download an already-int8 checkpoint.** On-the-fly is the fallback —
`wgp.py:3923` only sets `quantizeTransformer` when
`transformer_quantization in ("int8","fp8")` **and** `model_def` opts in via
`auto_quantize` **and** `"quanto" not in model_filename`. Default quantisation
level is `int8` (`wgp.py:2524`, `3238`).

In the pipe both experts are live at once as `transformer` and `transformer2`
(`wgp.py:3799`, `4012-4013`), and the denoise loop switches by rebinding a local
pointer — `models/wan/any2video.py:1404`:

```python
if model_switch_phase == phase_no-1 and self.model2 is not None: trans = self.model2
```

There is no unload/reload dance in the model code at all. mmgp is what makes
that affordable: both experts are registered models with their own budgets, and
whichever one is not being called simply has its blocks resident on the CPU side.
`ensure_model_loaded` → `unload_all` (`offload.py:3226-3228`) evicts the other
expert on first touch, since `transformer`/`transformer2` are not in the
co-tenant map (`offload.py:2547-2550`).

The switch point is a **timestep threshold, not a step index**
(`shared/utils/loras_mutipliers.py:152-168`): it walks the timestep schedule and
takes the first `i` where `t <= switch_threshold`. Base A14B ships
`switch_threshold: 900` with `guidance_phases: 2`, `guidance_scale: 3.5`,
`guidance2_scale: 3.5`, `flow_shift: 5`, `denoising_strength: 0.9`.
Because it is threshold-based, the high/low split stays at the same *noise level*
when you change step count — worth copying rather than hardcoding "steps 0-2 high,
3-4 low".

### 2.2 Quantisation per VRAM tier — the honest answer

**There is no VRAM→quant-level table in this repo.** I looked for one; what
exists instead is: quantisation is a *global user setting* defaulting to int8
(`wgp.py:2524`), and the VRAM adaptation happens entirely through **mmgp budgets**,
which is a different axis. The tiering is:

| mmgp profile | pinned RAM | budget | Their stated floor (mmgp README:73-77) |
|---|---|---|---|
| 1 HighRAM_HighVRAM | all models | none (unlimited) | 48 GB RAM + 24 GB VRAM |
| 2 HighRAM_LowVRAM | all models | `*`=3000 MB | 48 GB RAM + 12 GB VRAM |
| 3 LowRAM_HighVRAM | transformer only | none | 32 GB RAM + 24 GB VRAM |
| 4 LowRAM_LowVRAM | transformer only | `*`=3000 MB | 32 GB RAM + 12 GB VRAM |
| 5 VerylowRAM_LowVRAM | **none** | `*`=3000, transformer=400 MB | 24 GB RAM + 10 GB VRAM |

(`offload.py:3852-3877`; mmgp's own transformer default is 1200 MB, `offload.py:3847`.)

Then Wan2GP overrides those budgets far more aggressively — `wgp.py:3791-3801`,
for profiles 2, 4 and 5:

```python
budgets = { "transformer": ... 100, "text_encoder": 100, "*": max(1000 if profile==5 else 3000, preload) }
if "transformer2" in pipe: budgets["transformer2"] = ... 100
```

**100 MB per 14B expert.** That is not a typo and it is the answer to "how do they
run A14B on 8GB": the transformer is essentially never resident — with a 100 MB
budget `tune_preloading` (§1.5) preloads *nothing*, and every block is streamed
in with a depth-1 prefetch behind it. VRAM then holds activations plus two
blocks, not weights. Profile 3 is the opposite extreme: `{"*": "70%"}` of card
capacity (`wgp.py:3803`).

The escape hatch for people with real VRAM is `preload` (CLI `--preload` or
`server_config["preload_in_VRAM"]`, `wgp.py:3784-3786`), which replaces the
100 MB with an explicit MB figure for transformer, transformer2 *and* text_encoder.
Profiles 3 and 4 additionally pin both experts (`wgp.py:3805-3807`):

```python
if "transformer2" in pipe:
    if profile in [3,4]: kwargs["pinnedMemory"] = ["transformer", "transformer2"]
```

Two half-precision 14B experts pinned is ~56 GB of page-locked RAM at bf16, or
~28 GB at int8 — which is why mmgp auto-degrades to partial pinning when the
estimate exceeds reservable RAM (`offload.py:3669-3672`) instead of dying.

There are fractional profiles too: `4.5` = profile 4 with `asyncTransfers=False`,
`3.5` = profile 3 with `pinnedMemory=False` (`wgp.py:3809-3812`) — i.e. the two
knobs you turn when you run out of RAM rather than VRAM.

### 2.3 Resolution / frame limits per tier, and stated timings

Also largely absent as a table. The concrete claim in `README.md:75` is
**"5-6GB of VRAM only for 5s (124 frames) and 8-9GB of VRAM for 15s at 832x480"**
(that line is about the current release's optimisation, not specifically A14B).
The A14B-adjacent number is `README.md:218` for Bernini 14B (a Wan-2.2 derivative):
81 frames needs "12 GB of VRAM for v2v / 16GB for v2v + ref frames", and it notes
the upstream model is "advertised to work on a H100".

**No per-card s/step benchmarks exist anywhere in the repo.** There is no
BENCHMARKS.md and no timing table; `docs/GETTING_STARTED.md:87-89` is as
granular as guidance gets ("Low VRAM (6-8GB): use 1.3B models / High VRAM (16GB+):
any model, longer videos"). So we cannot compare their A14B speed to our
8.67 s/step 5B figure from this source — that comparison will have to come from
our own bench tomorrow.

### 2.4 The one-paragraph recipe for our 24 GB / 64 GB Windows box

Fetch both experts as `wan2.2_image2video_14B_{high,low}_quanto_mbf16_int8.safetensors`
(prequantized int8, ~14 GB the pair at int8 vs ~56 GB at bf16) rather than
quantizing on the fly; keep both loaded as `transformer`/`transformer2`; run mmgp
**profile 3** (`{"*": "70%"}`, pin the transformers, nothing else) since 24 GB VRAM
+ 64 GB RAM is exactly its target, and fall back to profile 4 with a raised
`preload` if the pinning estimate blows past reservable RAM; drive it at
`guidance_phases: 2`, `switch_threshold: 876`, `guidance_scale: 1`,
`guidance2_scale: 1`, `flow_shift: 5`, `num_inference_steps: 4`, euler, with the
two Lightning LoRAs phase-gated `"1;0 0;1"` (§3); leave VAE tiling **off** at our
resolution because their own heuristic returns `tile_size = 0` for a ≥24 GB card
below 1920×1088 (§4); and install SageAttention 2.2 (cu130/torch≥2.9 Blackwell
wheel) plus Triton before measuring anything (§5, §6).

---

## 3. Lightning / distill LoRA handling over A14B

### 3.1 Two LoRAs, one per expert, gated by phase

`profiles/wan_2_2/Lightning i2v v2025-10-14 2 Phases - 4 Steps.json`, complete:

```json
{ "num_inference_steps": 4, "guidance_scale": 1, "guidance2_scale": 1,
  "switch_threshold": 876, "model_switch_phase": 1, "guidance_phases": 2,
  "flow_shift": 5, "sample_solvers": "euler",
  "loras_multipliers": "1;0 0;1",
  "activated_loras": [
    ".../Wan2.2_I2V_A14B_HIGH_lightx2v_MoE_distill_lora_rank_64_bf16.safetensors",
    ".../Wan2.2_I2V_A14B_LOW_4steps_lora_rank64_Seko_V1_forKJ.safetensors" ] }
```

The load-bearing detail is `"1;0 0;1"`: space separates LoRAs, `;` separates
**phases**. LoRA #1 (HIGH) is at multiplier 1 in phase 1 and 0 in phase 2;
LoRA #2 (LOW) is the reverse. So both LoRAs are loaded onto both experts and
**switched by weight, not by loading** — the phase boundary computed in
`get_model_switch_steps` is fed to `update_loras_slists`
(`models/wan/any2video.py:1409-1410`), and per-step scaling is looked up at
`offload.py:2908-2914` off a `_lora_step_no` the loop sets every step via
`offload.set_step_no_for_lora(trans, start_step_no + i)`
(`any2video.py:1458`). Note lines 1409-1410 call `update_loras_slists` for
**both** `self.model` and `self.model2` — the multiplier schedule is what
distinguishes them, not the adapter set.

Also note the two LoRAs are not a matched pair from one release: HIGH is
lightx2v MoE-distill rank-64, LOW is "Seko V1 forKJ" 4-step rank-64. They mix
vendors per expert.

### 3.2 CFG at guidance 1

`guidance_scale: 1` in both phases. Their per-model default (non-distilled) is
3.5 (`defaults/i2v_2_2.json`); the distilled profile drops both phases to 1, and
the NVFP4 4-step Wan2.1 finetune does the same with `"guidance_scale": 1,
"num_inference_steps": 4, "sampler_solver": "euler", "flow_shift": 1`
(`defaults/i2v_nvfp4.json`). Nothing exotic — guidance 1 means the uncond pass is
simply not run, halving per-step cost, which is half of where 4-step's speed comes
from.

### 3.3 Their documented fix for Lightning's slow motion — relevant to our frozen-frame problem

`profiles/wan_2_2/Lightning i2v v2025-10-14 3 Phases - 8 Steps.json` carries a
`help` string that is worth quoting verbatim:

> "This finetune uses the Lightning 250928 4 steps Loras Accelerator for Wan 2.2
> but extend them to 8 steps in order to insert a CFG phase before the 2
> accelerated phases with no Guidance. **The ultimate goal is reduce the slow
> motion effect of these Loras Accelerators.**"

The mechanism is a 3-phase schedule where phase 1 is real CFG at the noisiest
timesteps and only phases 2-3 are LoRA-accelerated:

```json
{ "num_inference_steps": 8, "guidance_phases": 3,
  "guidance_scale": 3.5, "guidance2_scale": 1, "guidance3_scale": 1,
  "switch_threshold": 985, "switch_threshold2": 800, "model_switch_phase": 2,
  "flow_shift": 5, "loras_multipliers": "0;1;0 0;0;1" }
```

Read the multipliers: **both LoRAs are off in phase 1** (`0;...`). Phase 1 is
plain guided A14B; the HIGH LoRA turns on in phase 2, the LOW LoRA in phase 3, and
the expert switch moves to the phase 2→3 boundary (`model_switch_phase: 2`).
`switch_threshold: 985` makes phase 1 very short — with 8 steps at flow_shift 5,
one or two steps of real CFG.

Why this matters to us specifically: this repo has been fighting exactly the
failure this profile exists to fix. `pipeline/loop/` cycles and the working files
in the repo root (`MOTION-FIX-beat1.mp4`, `beat1-4-plus-amplitude.mp4`) are motion
work, and the K recipe was rejected in the founder's words as "literally just
frozen frames". If tomorrow's A14B test uses a 4-step Lightning LoRA and the
output is frozen or slow, **the upstream-documented answer is not more prompt
amplitude — it is spending 8 steps with a guided phase 1 and the LoRAs switched
off for it.** That is a recipe change, so under the ONE SAMPLE rule it needs one
beat rendered and screened, not a sweep.

### 3.4 anisora: not supported, at all

I grepped the full tree (`*.py`, `*.json`, `*.md`) for
`anisora|aniSora|AniSora|Index-anisora`: **zero hits.** There are 213 files in
`defaults/` and none of them is anisora. So:

- Wan2GP gives us **nothing** for Index-anisora V3.2 — no config, no LoRA
  handling, no verification that it loads.
- The useful inference is structural: anisora V3.2 being "same architecture as
  A14B" means their A14B path *should* accept it as a drop-in `URLs`/`URLs2` pair,
  but that is my inference from the architecture claim, **not something this repo
  demonstrates**. Treat anisora as unvalidated by this source; budget the time
  accordingly tomorrow and test A14B first.

---

## 4. VAE handling — where the 720p spike actually goes

Two VAEs, and they behave differently in a way that matters to us:

- `models/wan/modules/vae.py` — Wan **2.1** VAE, 8× spatial / 4× temporal. This is
  the one **A14B** uses (tomorrow's test).
- `models/wan/modules/vae2_2.py` — Wan **2.2** VAE, 16× spatial. This is the one
  our incumbent **TI2V-5B** uses.

### 4.1 Tile-size heuristic is capacity-driven, and returns "off" for our card

`vae.py:970-1001` (2.1 / A14B):

```python
if mixed_precision: device_mem_capacity = device_mem_capacity / 2
if device_mem_capacity >= 24000:
    use_vae_config = 2 if (output_height*output_width > 1920*1088) else 1
elif device_mem_capacity >= 16000: use_vae_config = 3
elif device_mem_capacity >= 8000:  use_vae_config = 4
else:                              use_vae_config = 5
# 1 -> 0 (off), 2 -> 1024, 3 -> 512, 4 -> 256, 5 -> 128
```

`vae2_2.py:1285-1306` (2.2 / our 5B) is the coarser version: ≥24000 → off,
≥8000 → 256, else 128, with no resolution refinement.

For our 24 GB 5090 at 704×1280 = 901,120 px, which is below the 1920×1088 =
2,088,960 px trigger, this returns **`tile_size = 0` — tiling off entirely.**
Their position is that a 24 GB card does not need to tile at our resolution. Note
`mixed_precision` halves the capacity input, so enabling it would demote us to
the 512 tier.

### 4.2 Tiled *encode* exists for A14B and is disabled for the 5B

This asymmetry is easy to miss and I nearly did:

- `vae.py:1003-1011` — encode tiles for real: `if tile_size > 0:` →
  `spatial_tiled_encode`.
- `vae2_2.py:1308-1317` — **`if tile_size > 0 and False :`** → the tiled encode
  branch is dead code. Every 2.2-VAE encode is full-frame.

So: if the ~22 GB 720p encode spike we are worried about is on the **A14B** path,
tiled encode is available (`spatial_tiled_encode`, `vae.py:842-849`:
`tile_latent_min_size = tile_size/8`, `tile_overlap_factor = 0.25`). If it is on the
**TI2V-5B** path, upstream has no encode-side mitigation at all and never has —
which is itself the answer to "how do they avoid it": for I2V the encode input is
one conditioning image (or a short clip), so the encode is cheap and the spike
they engineer against is the **decode**, not the encode. Worth checking which of
the two our 22 GB figure actually came from before porting anything.

### 4.3 The real trick: temporal chunking + streaming straight to CPU uint8

`decode_tile_chunks` (`vae.py:719-740`, `vae2_2.py:937-956`) is a **generator that
decodes one latent frame at a time**, exploiting the VAE's causal 3D convs by
carrying the conv state forward in `feat_cache=self._feat_map` /
`feat_idx=self._conv_idx`, with `first_chunk=True` on the first:

```python
for i in range(x.shape[2]):
    self._conv_idx = [0]
    tile = self.decoder(x[:, :, i:i+1, :, :], feat_cache=self._feat_map, feat_idx=self._conv_idx, ...)
    yield frame_start, tile
```

`decode_to_cpu_uint8` (`vae.py:741-839`) then composes temporal chunking with
spatial tiling and never materialises a full float video on the GPU:

- The **output buffer is CPU uint8**, allocated once (`vae.py:776`):
  `torch.empty((b, 3, target_frames, H, W), dtype=torch.uint8, device="cpu")`.
- Latents are held on CPU when tiling (`746-747`) and each tile is moved to GPU
  alone (`794`).
- Each decoded chunk is converted and copied into the CPU buffer immediately
  (`830`), then `del tile`.
- Only thin **edge strips** (`blend_extent` wide) are retained, on CPU, for seam
  blending across rows/cols (`818-828`, `_blend_v_edge_` / `_blend_h_edge_`).

Peak decode VRAM is therefore ≈ one spatial tile × one temporal chunk (1 latent
frame → 4 output frames at 4× temporal), independent of clip length. That is the
single most portable VAE idea here and it does not require mmgp at all — it is
plain PyTorch against the VAE's existing `feat_cache` API.

Frame arithmetic to reuse: decoded frames = `(latent_frames - 1) * 4 + 1`
(`vae.py:748`); needed latents for a target frame count =
`(max(target_end,1) - 1 + 3) // 4 + 1` (`752`). The non-tiled path
(`762-767`) still goes through `_vae_float_to_cpu_uint8`, so the uint8-on-CPU
return type is uniform either way.

There is no temporal *overlap* blending — temporal continuity comes from the conv
feature cache, not from overlapping windows. Only spatial tiles overlap (0.25).

---

## 5. Windows-specific handling

### 5.1 The pinned-memory cap is 40% on Windows vs 50% on Linux

`offload.py:231-242` — the only real OS branch in the whole memory library:

```python
if perc_reserved_mem_max <= 0:
    perc_reserved_mem_max = 0.40 if os.name == 'nt' else 0.5
max_reservable_memory = perc_reserved_mem_max * physical_memory
```

On our 64 GB Windows box that is a **25.6 GB ceiling on page-locked RAM**. Two
int8 A14B experts (~14 GB total) fit under it; two bf16 experts (~56 GB) do not,
and mmgp will silently downgrade to `partialPinning` (`offload.py:3669-3672`)
rather than fail. It is overridable via the `perc_reserved_mem_max` env var
(`offload.py:234`) — an env var, notably, not just a kwarg.

Related, from `mmgp/README.md:16`: *"These RAM requirements are for Linux systems.
Due to different memory management Windows will require an extra 16 GB of RAM to
run the corresponding profile."* So their profile-4 "32 GB RAM" floor is really
48 GB on Windows. Our 64 GB is comfortable for profile 3/4 with int8, tight with bf16.

### 5.2 What is NOT here — WDDM and sysmem fallback

I searched both trees for `wddm`, `sysmem`, "system memory fallback", "shared
memory fallback", `cudaMallocAsync`: **no hits at all.** The only
`PYTORCH_CUDA_ALLOC_CONF` use is `expandable_segments:True` inside an unrelated
model (`models/kandinsky5/kandinsky/models/vae.py:21`) and a bare mention in
`docs/CLI.md:316`.

That absence is a finding, not a gap in my search:

- They do **not** disable the NVIDIA driver's sysmem fallback. On Windows a
  VRAM overcommit therefore silently spills to host RAM over PCIe and the run
  gets slow instead of OOMing. Their whole design leans the other way — keep
  weights on the host deliberately and stream them — so they never need the
  driver to do it accidentally. For **our** bench tomorrow this matters a lot:
  **a "successful" A14B run that is 5× slower than expected is the signature of
  sysmem fallback, not of block swap.** We should read
  `torch.cuda.memory_reserved()` and wall-clock per step, and if we want hard
  failures instead of silent spill, that is an NVIDIA Control Panel setting
  (per-process "CUDA - Sysmem Fallback Policy") — not something this repo touches.
- `windows_os = os.name == 'nt'` is assigned at `offload.py:3506` and **never
  read** — a leftover. There is no WDDM-aware allocation path.
- One Windows trick is present but **deliberately disabled**:
  `flush_torch_caches` (`offload.py:1938`) has a `psapi.EmptyWorkingSet(handle)`
  call behind `if os.name == "nt" and False: # suspicion of crash`. Do not
  resurrect it.
- `flush_torch_caches` does call `torch._C._host_emptyCache()`
  (`offload.py:1934-1937`, guarded by `AttributeError`) — that frees the **pinned
  host** cache, which is the thing that actually leaks across model switches.
  Cheap and worth copying if we pin.

### 5.3 Toolchain versions — the concrete traps

`docs/INSTALLATION.md:5-9`, and these are stated as tested combinations:

- **RTX 30XX–50XX: Python 3.11.14 + PyTorch 2.10 + CUDA 13.0/13.1.** Their install
  command is `pip install torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0
  --index-url https://download.pytorch.org/whl/cu130`, and CUDA **13.1** is the
  stated requirement for RTX 20xx–50xx (`INSTALLATION.md:17`). Note this is
  **cu130, not cu128** — the brief mentioned cu128; upstream has moved past it and
  says so explicitly: NVFP4 kernels *require* leaving cu128 behind
  (`INSTALLATION.md:9`: "you will need to upgrade to Python 3.11, PyTorch 2.10
  with Cuda 13.0 if you are still using the old install setup based on cuda 12.8").
- **Avoid PyTorch 2.8.0 and 2.9.0** (`INSTALLATION.md:7`), verbatim: *"not
  recommended to use either PytTorch 2.8.0 as some System RAM memory leaks have
  been observed when switching models or 2.9.0 which has some Convolution 3D perf
  issues (VAE VRAM requirements explode)."* Both failure modes are exactly what
  we would be measuring tomorrow — a RAM leak across model switches (we switch two
  experts every run) and a VAE VRAM explosion (our 22 GB spike question). **Check
  `torch.__version__` on the Windows box before trusting any A14B VRAM number.**
- Triton on Windows: `pip install triton-windows` for RTX 40XX–50XX
  (`INSTALLATION.md:52-55`); it is required for torch.compile *and* for Sage.
- SageAttention 2.2 on Windows RTX 40XX–50XX is a prebuilt wheel
  (`INSTALLATION.md:68-70`):
  `sageattention-2.2.0+cu130torch2.9.0andhigher.post4-cp39-abi3-win_amd64.whl`
  from `woct0rdho/SageAttention`. No compile step needed — this is the single
  highest-value 20 minutes of setup on that box.

### 5.4 Blackwell / sm120 specifics

- Arch gate for bf16: `wgp.py:2453-2458` — `gpu_major < 8` falls back to fp16.
  A 5090 is sm120 (major 12), so bf16 is used.
- Attention eligibility (`shared/attention.py:239-255`): `sage3` requires
  `major >= 10` **and** Triton; `sage2` requires `is_sage2_supported()` and Triton.
  A 5090 clears both.
- `sageattn_blackwell` / `sageattn3_blackwell` are imported if present
  (`shared/attention.py:125-144`), including a "word0 windows version" fallback
  import path.
- NVFP4 exists as a real path but only for a Wan **2.1** I2V 4-step finetune, not
  for A14B: `defaults/i2v_nvfp4.json` says *"For full speed, a sm120+ GPU is
  needed (RTX 50xx) and the lightx2v kernels must be installed."* There is **no
  NVFP4 A14B checkpoint** in `defaults/`. So NVFP4 is not an option for tomorrow's
  A14B test, and int8 quanto is the ceiling.

---

## 6. What of their tech would speed up our WORKING TI2V-5B recipe

Our baseline for this section: **704×1280, 8.67 s/step + 67 s fixed overhead** on
the 5090, via `pipeline/wan_i2v.py`.

### 6.1 The headline — a 3-step distill LoRA exists for our exact model at our exact resolution

`defaults/ti2v_2_2_fastwan.json`, in full-enough part:

```json
{ "model": { "name": "Wan2.2 TextImage2video FastWan 5B",
    "architecture": "ti2v_2_2",
    "description": "FastWan2.2-TI2V-5B-Full-Diffusers is built upon Wan-AI/Wan2.2-TI2V-5B-Diffusers.
                    It supports efficient 3-step inference and produces high-quality videos at 121x704x1280 resolution",
    "URLs": "ti2v_2_2",
    "loras": [".../loras_accelerators/Wan2_2_5B_FastWanFullAttn_lora_rank_128_bf16.safetensors"] },
  "video_length": 121, "guidance_scale": 1, "flow_shift": 3, "num_inference_steps": 3 }
```

Three things make this the most valuable line in the repo for us:

1. `"URLs": "ti2v_2_2"` — it **reuses the base checkpoint we already have working**.
   This is a LoRA on top of our incumbent, not a new model. No new download of
   weights, no new architecture, no re-validation of the conditioning path.
2. `num_inference_steps: 3` at `guidance_scale: 1`. We ran a step sweep at 6/10/14/20
   (`steps-06.mp4` … `steps-20.mp4`, `STEPS-SWEEP-strip.png` in the repo root), so we
   are somewhere in that band. Going to 3 steps is a **2–7× cut in sampling work**,
   and `guidance_scale: 1` drops the unconditional pass on top of that if our
   current recipe runs CFG.
3. The description names **121×704×1280** — our exact frame count and our exact
   resolution. This is not a recipe we have to adapt.

`flow_shift: 3` (not the base model's 5) is part of the recipe; do not carry our
current flow_shift over.

Caveat that keeps this honest: FastWan is a distill LoRA, and §3.3 documents that
this family of accelerators causes **slow motion** — which is the exact defect our
K recipe was rejected for. So this is a recipe change under the ONE SAMPLE rule:
one beat, screened, before anything else. If it comes back frozen, the upstream fix
is §3.3's shape (spend a couple of guided steps first with the LoRA off), not more
prompt amplitude.

### 6.2 Attention — their default is sage2, and we are almost certainly on sdpa

`shared/attention.py:258-262`:

```python
def get_default_attention_mode():
    for attn in ("sage2", "sage", "sdpa"):
        if attn in get_supported_attention_modes(): return attn
    return "sdpa"
```

sdpa is their **last** resort. `README.md:61` claims Sage "accelerates a Video /
Image Generation up to x2 with very little quality loss". On Windows RTX 50xx it is
a **prebuilt wheel, no compilation** (§5.3), and it needs Triton
(`triton-windows`). Their call wrapper is `sageattn2_wrapper`
(`shared/attention.py:86-119`) using `tensor_layout="NHD"`.

For our diffusers pipeline this means writing one custom attention processor that
routes to `sageattn2` instead of SDPA. That is the **cheapest per-step win
available to us** — it touches one class, not the memory architecture, and it is
orthogonal to §6.1 (they multiply).

sage3 (`sageattn_blackwell`) is importable and gate-eligible on sm120
(`shared/attention.py:125-144`, `239-244`) but is **not in the default preference
list** — treat it as experimental, try sage2 first.

### 6.3 TeaCache is not available for our model; MagCache is

`models/wan/wan_handler.py:352-353`:

```python
"tea_cache": not shotplan and not (base_model_type in ["i2v_2_2"] or test_wan_5B(base_model_type) or multiple_submodels),
"mag_cache": not shotplan,
```

and `test_wan_5B` is `base_model_type in ["ti2v_2_2", "lucy_edit", "kiwi_edit"]`
(`wan_handler.py:56-57`) — `ti2v_2_2` **is** our model. So:

- **TeaCache is explicitly disabled for our TI2V-5B *and* for A14B.** The brief
  asked about TeaCache: the answer is upstream turned it off for both models we
  care about. Do not spend time on it.
- **MagCache is enabled**, and ships pre-calibrated per-architecture magnitude
  tables — including a dedicated `test_wan_5B` branch with **separate t2v and i2v
  tables** (`wan_handler.py:183-188`), plus an `i2v_2_2` table for A14B (`181-182`).
  Settings are `magcache_thresh: 0`, `magcache_K: 2` (`wan_handler.py:174-178`).

But note the interaction: step-skipping caches only pay off when there are steps
worth skipping. **At 3 steps there is nothing to skip**, so MagCache and §6.1 are
alternatives rather than a stack, and §6.1 is strictly the better one. MagCache is
the fallback if FastWan's motion turns out unusable and we are stuck at 14–20 steps.

### 6.4 Compile is OFF by default, and would hurt us at 3 steps

`wgp.py:2529` — `"compile": ""`, i.e. disabled unless the user opts in. When
enabled, the pattern is worth knowing (it is how compile and block-swap coexist):

- `torch.compile` is applied **per tower module**, not to the whole transformer:
  `submodel.forward = torch.compile(submodel.forward, backend="inductor", mode=compile_mode)`
  (`offload.py:3764-3765`).
- The offload hook is registered as a `forward_pre_hook` **before** compilation
  (`hook_preload_blocks_for_compilation`, `offload.py:3230-3240`), with the comment
  that such a hook mid-chain "seems to break memory performance".
- `_pre_check` is `@torch._dynamo.disable`d and `gpu_load_blocks` /
  `gpu_unload_blocks` are `@torch.compiler.disable()`d (`offload.py:2683`, `2777`,
  `3245`) — all the swapping is kept out-of-graph.
- `torch._dynamo.config.cache_size_limit = 10000` (`offload.py:3578`), and
  `empty_cache_if_needed` is short-circuited whenever anything is compiled
  (`offload.py:2874-2875`).

For us: compile trades a large one-time warmup for per-step gains. Our problem is
already 67 s of *fixed* cost against a shrinking sampling cost — compile makes the
fixed term worse. **Skip compile** unless we move to a persistent worker process
that amortises warmup across many clips.

### 6.5 The 67 s fixed overhead — their tooling for it

They do not have our problem because WanGP is a long-running server: the model is
loaded once and stays. Our `_sample()` already loads once and loops over jobs
(`pipeline/wan_i2v.py:386-392`, "Loading once and looping turned four clips from
~44 minutes into a bit over ten"), so we pay 67 s per *batch* — but under the ONE
SAMPLE rule we deliberately render one clip at a time, which means we pay it every
time. Their applicable pieces:

- **Prequantized single-file int8 checkpoints.** `defaults/ti2v_2_2.json` already
  lists `wan2.2_text2video_5B_quanto_mbf16_int8.safetensors` alongside the bf16 —
  roughly half the bytes to read off disk and no on-the-fly quantise step.
- **`save_model(model, path, do_quantize=True)`** (`offload.py:2364`) plus
  `load_model_data` / `fast_load_transformers_model` (`offload.py:2053`, `1831`) —
  their documented workflow (mmgp README:142-145) is: bake your own single
  prequantized file once, then load that forever. Metadata (quant map + config) is
  embedded so no `config.json` needs to travel with it.
- **`pinToMemory` / `partialPin` at load time**, which the README says is more RAM
  efficient and faster than pinning afterwards, and pinning makes host→device up to
  2× faster (mmgp README:102, 134).
- **`torch._C._host_emptyCache()`** (`offload.py:1934-1937`) to release the pinned
  host cache between model switches.

Realistically the biggest structural fix for the 67 s is a **persistent worker**
(load once, accept jobs) rather than any mmgp feature — and we already have
`pipeline/farm_worker.py` as a daemon, so the machinery exists.

### 6.6 One thing we may be doing for no benefit: VAE tiling on the 5B

`pipeline/wan_i2v.py:88-125` (`tile_vae`) unconditionally enables diffusers' VAE
tiling on both paths, added after a real AnimeGen OOM in
`autoencoder_kl_wan._encode`. That fix was correct for the *A14B/fp8* path. But by
their heuristic (§4.1) a **24 GB card at 704×1280 should not tile at all**
(`tile_size = 0`), and tiling costs time (overlapping tiles are recomputed at 0.25
overlap). Also worth knowing: for the 2.2 VAE our 5B uses, upstream's tiled
*encode* is dead code anyway (`vae2_2.py:1314`), so on that path `enable_vae_tiling()`
is diffusers' implementation doing work upstream deliberately skips.

This is a measurable A/B on the 5B path only — tiling off, watch peak VRAM and
wall time — not a change to make blind, and **not** something to touch on the
AnimeGen/A14B path where it fixed a real OOM.

---

## 7. Ranked: portable memory techniques by value-to-port-effort

Assumes reimplementation from the descriptions above, **not** copying GPL-3 source
(see the licence flag at the top).

| # | Technique | Value to us | Port effort | Verdict |
|---|---|---|---|---|
| 1 | **int8 the text encoder, keep it in the pipe** (`offload.py:3831-3839`, `wgp.py:3245`) | Very high — kills our 11.4 GB T5 resident cost without touching the conditioning path | Low: `optimum-quanto` quantize on the loaded T5, ~20 lines | **Do first** |
| 2 | **Streaming VAE decode to CPU uint8** (§4.3, `vae.py:741-839`) | High — makes decode VRAM independent of clip length, kills a whole class of OOM | Low-medium: plain PyTorch over the VAE's existing `feat_cache`; no mmgp | **Do** |
| 3 | **Cache hygiene: rate-limited, threshold-gated `empty_cache()`** (§1.6) | Medium-high — removes a per-step tax and the fragmentation stalls we hit on 2026-08-02 | Very low: ~15 lines | **Do** |
| 4 | **Prequantized single-file int8 checkpoints** (§6.5) | Medium-high — attacks the 67 s directly, halves disk read | Low: one bake step, then load | **Do** |
| 5 | **Pinned staging + depth-1 async prefetch on a second stream** (§1.3-1.4) | Medium — only matters once weights genuinely do not fit | Medium-high: needs the param registry (§1.1) as a prerequisite | Only for A14B |
| 6 | **`setattr` param registry / block swap** (§1.1-1.2) | Medium — the enabling primitive for #5 and #7 | High: per-module forward wrapping, tied weights, quantised subtensors | Only if A14B will not fit any other way |
| 7 | **`tune_preloading` partial-preload + circular shuttle** (§1.5) | High *given* #6 — the idea that makes 24 GB behave like unlimited | Medium on top of #6; the algorithm is ~60 lines and I have it summarised | Best idea here, but gated behind #6 |
| 8 | Per-block `torch.compile` with out-of-graph hooks (§6.4) | Low for us — worsens our fixed-overhead problem | Medium (Triton on Windows) | Skip |

The honest read: **items 1-4 are cheap, independent of mmgp, and worth doing
regardless of tomorrow's outcome.** Items 5-7 are a real port (a few days, and a
licence conversation) that we should only start if A14B proves it earns its keep on
quality *and* cannot be made to fit any other way.
