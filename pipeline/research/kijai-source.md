# kijai/ComfyUI-WanVideoWrapper — source read

Read of the community's most battle-tested Wan runner, for technique extraction
only. **We are not adopting ComfyUI.** Goal: reference settings and portable
techniques for our own diffusers pipeline (24GB RTX 5090 + 64GB RAM, Windows).

- Clone: `https://github.com/kijai/ComfyUI-WanVideoWrapper` shallow, HEAD
  `088128b` ("Don't count .disabled as duplicate"), read 2026-08-04.
- Nothing was executed; no ComfyUI installed. All claims below are from source.
- File:line citations are against that commit.

Main files by size: `nodes_sampler.py` (2888), `nodes.py` (2376),
`nodes_model_loading.py` (2153), `wanvideo/modules/model.py` (~3400),
`utils.py` (778), `custom_linear.py` (281), `fp8_optimization.py` (45).

---

## 1. BLOCK SWAP — the actual implementation

### Granularity: whole transformer blocks, nothing finer

`blocks_to_swap` counts **top-level `WanAttentionBlock`s** off the *end* of the
stack. `wanvideo/modules/model.py:2053`:

```python
swap_start_idx = len(self.blocks) - blocks_to_swap
```

Blocks `[0, swap_start_idx)` stay resident on `main_device` forever; blocks
`[swap_start_idx, N)` live on CPU and are moved in/out one at a time
(`model.py:2055-2063`). There is no sub-block (per-linear) granularity in the
block-swap path — that is what the separate `vram_management_args` /
`offload_percent` path does (`nodes_model_loading.py:319-326`), and the two are
mutually exclusive by assertion (`nodes_model_loading.py:1111`):

```python
assert not (vram_management_args is not None and block_swap_args is not None), \
    "Can't use both block_swap_args and vram_management_args at the same time"
```

Block counts per model, from the node tooltip (`nodes_model_loading.py:299`):
**14B = 40 blocks, 1.3B and 5B = 30 blocks**, LongCat = 48. Confirmed in the
configs (`wanvideo/configs/wan_i2v_14B.py:31`: `i2v_14B.num_layers = 40`,
`num_heads = 40`) and in the loader's autodetect
(`nodes_model_loading.py:1311-1322`, which picks 40 / 30 / 48 / 30). Default
`blocks_to_swap = 20`, max 48. VACE blocks swap separately
(`vace_blocks_to_swap`, 15 blocks, default 0, `nodes_model_loading.py:305`).

Two extra optional offloads, both default False
(`nodes_model_loading.py:300-301`): `offload_txt_emb` and `offload_img_emb` —
the text/image embedders get moved to CPU and pulled in only for their single
call (`model.py:2823-2830` for img_emb, `model.py:2837-2875` for text_embedding).
These are one-shot per forward, so they are nearly free and worth having.

### The runtime loop: swap-in before, swap-out after, per block

`model.py:3225-3298`, inside the per-step block loop:

```python
# Wait for block to be ready
if b >= swap_start_idx and self.blocks_to_swap > 0:
    if self.prefetch_blocks > 0 and events is not None:
        if not events[b].query():
            events[b].synchronize()
    block.to(self.main_device)                      # 3256  swap IN
...
x, x_ip, lynx_ref_feature, x_ovi = block(x, ...)    # 3274  compute
...
if b >= swap_start_idx and self.blocks_to_swap > 0:
    block.to(self.offload_device, non_blocking=self.use_non_blocking)  # 3298  swap OUT
```

So the steady-state VRAM cost of the swapped region is **exactly one block**
(plus `prefetch_blocks` more if enabled). Note the asymmetry: the swap-**in** at
`model.py:3256` is a plain blocking `.to()` — `non_blocking` is *not* passed —
while the swap-**out** at 3298 is `non_blocking=self.use_non_blocking`. Sending
to CPU async is the safe direction; pulling to GPU is made synchronous so the
weights are definitely there before `block()` runs.

### Sync or async H2D: effectively SYNCHRONOUS. The CUDA stream is disabled.

This is the detail worth knowing, `model.py:3201-3205`:

```python
# Asynchronous block offloading with CUDA streams and events
if torch.cuda.is_available():
    cuda_stream = None #torch.cuda.Stream(device=device, priority=0) # todo causes issues on some systems
    events = [torch.cuda.Event() for _ in self.blocks]
    swap_start_idx = len(self.blocks) - self.blocks_to_swap if self.blocks_to_swap > 0 else len(self.blocks)
```

The side stream is **commented out** with "todo causes issues on some systems".
`torch.cuda.stream(None)` is a no-op context manager, so the prefetch at
`model.py:3244-3248` issues its copies on the *default* stream — i.e. it cannot
overlap with the compute that is also on the default stream, beyond what the
copy engine does for a single H2D. The `torch.cuda.Event` machinery
(`events[prefetch_idx].record(cuda_stream)` / `events[b].synchronize()`) is
still wired up and correct, so re-enabling the stream is a one-line change —
they just don't ship it on.

Practical read: **their block swap is a synchronous, prefetch-hinted, one-block
window.** The "async" in the comment is aspirational. Any latency hiding we add
on our side would be an improvement over this baseline, not a port of it.

### Prefetch

`model.py:3239-3248`, default 0 (`nodes_model_loading.py:306`):

```python
if self.prefetch_blocks > 0:
    for prefetch_offset in range(1, self.prefetch_blocks + 1):
        prefetch_idx = b + prefetch_offset
        if prefetch_idx < len(self.blocks) and self.blocks_to_swap > 0 and prefetch_idx >= swap_start_idx:
            context_mgr = torch.cuda.stream(cuda_stream) if torch.cuda.is_available() else nullcontext()
            with context_mgr:
                self.blocks[prefetch_idx].to(self.main_device, non_blocking=self.use_non_blocking)
                if events is not None:
                    events[prefetch_idx].record(cuda_stream)
```

Two things: (a) it re-issues the `.to()` for the same block on every iteration
it is in range, so with `prefetch_blocks=1` each block gets moved once
speculatively and then again (as a no-op) by the blocking `.to()` at 3256;
(b) the tooltip is the actual guidance and it is honest —
`nodes_model_loading.py:306`: *"1 is usually enough to offset speed loss from
block swapping, use the debug option to confirm it for your system"*.

`prefetch_blocks` costs one extra block of VRAM per unit.

### Pinned memory: NOT USED. `use_non_blocking` is the knob, default off.

There is no `pin_memory()` / `.pin_memory()` call anywhere in the repo (grepped
for `pin_memory|pinned` across `*.py` — only hits are the `use_non_blocking`
plumbing). The offload buffers are ordinary pageable CPU tensors.

`use_non_blocking` defaults **False**, `nodes_model_loading.py:304`, tooltip:
*"Use non-blocking memory transfer for offloading, reserves more RAM but is
faster"*. Set on the transformer at `nodes_sampler.py:104`; the field's default
is False at `model.py:1848`.

Worth being precise about the consequence: `non_blocking=True` into *pageable*
host memory is not a real async DMA — CUDA has to stage it. So they are leaving
the single biggest cheap win on the table. **Pinning the offload buffers is the
obvious upgrade over this implementation**, and it is what would make a real
side-stream prefetch pay off.

### Load-time placement — the part that actually matters for OOM

The blocks are never all in VRAM, not even transiently. `load_weights()`
decides a **per-parameter destination device** from the block index before the
tensor is materialised, `nodes_model_loading.py:911-921`:

```python
load_device = transformer_load_device
if block_swap_args is not None:
    load_device = device
    if block_idx is not None:
        if block_idx >= len(transformer.blocks) - block_swap_args.get("blocks_to_swap", 0):
            load_device = offload_device
    elif vace_block_idx is not None:
        if vace_block_idx >= len(transformer.vace_blocks) - block_swap_args.get("vace_blocks_to_swap", 0):
            load_device = offload_device
set_module_tensor_to_device(transformer, name, device=load_device, dtype=dtype_to_use, value=value)
```

Same logic on the GGUF path (`nodes_model_loading.py:846-856`). `block_idx` is
parsed straight out of the parameter name (`nodes_model_loading.py:879-883`).

`init_blockswap()` in `utils.py:93-120` handles the *non*-patched-linear case
and shows the same shape — everything that is not a block goes to GPU, blocks
get placed by `transformer.block_swap(...)`:

```python
def init_blockswap(transformer, block_swap_args, model):
    if not transformer.patched_linear:
        if block_swap_args is not None:
            for name, param in transformer.named_parameters():
                if "block" not in name or "control_adapter" in name or "face" in name:
                    param.data = param.data.to(device)
                elif block_swap_args["offload_txt_emb"] and "txt_emb" in name:
                    param.data = param.data.to(offload_device)
                elif block_swap_args["offload_img_emb"] and "img_emb" in name:
                    param.data = param.data.to(offload_device)
            transformer.block_swap(
                block_swap_args["blocks_to_swap"] - 1 ,
                ...
```

Note `blocks_to_swap - 1` there (`utils.py:105`) — an off-by-one against the
sampler path, which sets `transformer.blocks_to_swap` to the raw value
(`nodes_sampler.py:105`). Also that call site does not forward
`prefetch_blocks` or `block_swap_debug`. Minor, but it means the UI number is
not exactly the block count on every path.

### How many blocks resident per VRAM budget

The wrapper does **not** compute this. There is no VRAM-budget-to-blocks
heuristic anywhere — `blocks_to_swap` is a user dial with a default of 20 and a
tooltip listing block counts so you can reason about it yourself
(`nodes_model_loading.py:299`). What it does instead is *report* the split so
you can tune by observation, `model.py:2089-2095`:

```python
log.info("Block swap memory summary:")
log.info(f"Transformer blocks on {self.offload_device}: {total_offload_memory:.2f}MB")
log.info(f"Transformer blocks on {self.main_device}: {total_main_memory:.2f}MB")
log.info(f"Total memory used by transformer blocks: {(total_offload_memory + total_main_memory):.2f}MB")
log.info(f"Non-blocking memory transfer: {self.use_non_blocking}")
```

plus the per-block timing breakdown under `block_swap_debug`
(`model.py:3249-3302`) printing `transfer_time`, `compute_time`,
`to_cpu_transfer_time` per block — that is their tuning method: raise
`blocks_to_swap` until you fit, then raise `prefetch_blocks` until
`transfer_time` stops dominating.

Rough arithmetic for us: A14B at fp8 is ~14GB of weights, ~40 blocks, so a
block is ~300-350MB. On 24GB with an I2V A14B expert pair we are not
weight-bound the way a 12GB card is; block swap for us is about making
*headroom for activations* at higher resolution / longer clips, not about
fitting the model at all. Swapping 10 blocks buys ~3-3.5GB.

### Portability verdict for our diffusers pipeline

**The technique is trivially portable. It is ~40 lines and needs no ComfyUI.**
Nothing in the mechanism touches ComfyUI: it is `block.to(device)` before and
after each block's `forward`, plus load-time per-parameter placement. Their only
framework dependency is `comfy.model_management.soft_empty_cache()`
(`model.py:2086`) which is `torch.cuda.empty_cache()` in a trenchcoat, and
`set_module_tensor_to_device` which is **accelerate's**, not Comfy's — we
already have accelerate as a diffusers dependency.

Two implementation routes for us:

1. **Forward-pre/post hooks** (no fork of the model class). Register
   `register_forward_pre_hook` / `register_forward_hook` on
   `transformer.blocks[i]` for `i >= swap_start_idx`, doing the `.to()` in each.
   ~30 lines, works on the stock diffusers `WanTransformer3DModel`, survives
   upstream diffusers updates. This is the one I'd write.
2. **Sub-class the block loop** — closer to kijai's, but means owning a copy of
   the transformer forward. Not worth it.

Effort: **half a day including the load-time placement**, which is the fiddly
part — diffusers' `from_pretrained` wants to place the whole model, so we would
load with `device_map=None` on meta/CPU and then place per-block ourselves
before the first forward. If we skip load-time placement and just do the
runtime hooks, it is **an hour**, but then the model must fit in VRAM once at
load, which defeats half the point.

Value for us specifically: **moderate, not urgent.** We are on 24GB, and our
stated near-term problem is not OOM on TI2V-5B (30 blocks, small). It becomes
worth doing the moment we run I2V-A14B at higher resolution or want both noise
experts resident. If we implement it, do it *better* than the reference in two
specific ways the source shows are missing: **pin the CPU-side buffers**, and
**actually use a side stream** for prefetch (their `cuda_stream = None` is an
admission, and the event plumbing to make it work is already sketched at
`model.py:3204`/`3248`/`3254-3255`).

---

## 2. fp8 and fp8_scaled handling

There are **two separate and independent things** here, and conflating them is
the main trap. Reading the code straightens it out:

| | storage | matmul | needs custom ops? | needs sm >= 8.9? |
|---|---|---|---|---|
| `fp8_e4m3fn` | fp8 | bf16/fp16 (weight upcast per-forward) | no | no |
| `fp8_e4m3fn_scaled` | fp8 + per-layer scale | bf16/fp16 | **no** | no |
| `fp8_e4m3fn_fast` | fp8 | **real fp8** via `torch._scaled_mm` | no (torch builtin) | **yes** |
| `fp8_e4m3fn_scaled_fast` | fp8 + scale | real fp8, scale as `scale_b` | no | yes |

Node enum, `nodes_model_loading.py:1085-1086`:

```python
"quantization": (["disabled", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e4m3fn_scaled", "fp8_e4m3fn_scaled_fast",
                  "fp8_e5m2", "fp8_e5m2_fast", "fp8_e5m2_scaled", "fp8_e5m2_scaled_fast"], {"default": "disabled",
    "tooltip": "Optional quantization method, 'disabled' acts as autoselect based by weights. Scaled modes only work with
    matching weights, _fast modes (fp8 matmul) require CUDA compute capability >= 8.9 (NVIDIA 4000 series and up),
    e4m3fn generally can not be torch.compiled on compute capability < 8.9 (3000 series and under)"}),
```

### Detection: automatic, from the state dict

`nodes_model_loading.py:1187-1211` — `quantization="disabled"` is really
"autodetect". They sniff the first fp8 tensor's dtype, then look for the
`scaled_fp8` marker key and for any `.scale_weight` / `.weight_scale` suffix:

```python
if quantization == "disabled":
    for k, v in sd.items():
        if isinstance(v, torch.Tensor):
            if v.dtype == torch.float8_e4m3fn:
                quantization = "fp8_e4m3fn"
                if "scaled_fp8" in sd:
                    is_scaled_fp8 = True
                    quantization = "fp8_e4m3fn_scaled"
                break
            elif v.dtype == torch.float8_e5m2:
                ...
scale_weights = {}
if "fp8" in quantization:
    for k, v in sd.items():
        if k.endswith(".scale_weight") or k.endswith(".weight_scale"):
            is_scaled_fp8 = True
            break
if is_scaled_fp8 and "scaled" not in quantization:
    quantization = quantization + "_scaled"
```

and then they hard-fail on a mismatch rather than silently producing garbage
(`nodes_model_loading.py:1220-1223`):

```python
if is_scaled_fp8 and "scaled" not in quantization:
    raise ValueError("The model is a scaled fp8 model, please set quantization to '_scaled'")
if not is_scaled_fp8 and "scaled" in quantization:
    raise ValueError("The model is not a scaled fp8 model, please disable '_scaled' in quantization")
```

Two naming conventions in the wild are normalised to one
(`nodes_model_loading.py:1600`) — this matters for us because it means the
Kijai/WanVideo_comfy repo files are not internally consistent:

```python
sd = {k.replace(".weight_scale", ".scale_weight"): v for k, v in sd.items()}
```

Scales are collected and moved to GPU in `base_dtype` up front
(`nodes_model_loading.py:1711-1715`) — they are tiny, one per Linear:

```python
scale_weights = {}
if "fp8" in quantization:
    for k, v in sd.items():
        if k.endswith(".scale_weight"):
            scale_weights[k] = v.to(device, base_dtype)
```

### Where the scale is applied — a subclassed nn.Linear, no custom ops

The scaled (non-fast) path swaps every `nn.Linear` for `CustomLinear` via
`_replace_linear` (`nodes_model_loading.py:1756-1758`):

```python
elif "scaled" in quantization or lora is not None:
    transformer = _replace_linear(transformer, base_dtype, sd, scale_weights=scale_weights, compile_args=compile_args)
    transformer.patched_linear = True
```

`_replace_linear` (`custom_linear.py:44-87`) walks children, reads
`in/out_features` from the state dict, looks up `f"{module_prefix}scale_weight"`
and constructs the replacement under `accelerate.init_empty_weights()` so no
memory is touched twice.

The whole of the scaled-fp8 math is `custom_linear.py:247-265`:

```python
def forward(self, input):
    weight = self._prepare_weight(input)          # self.weight.to(input) -> upcast fp8 -> bf16
    bias = self.bias.to(input) if self.bias is not None else None
    # Only apply scale_weight for non-GGUF models
    if not self.is_gguf and self.scale_weight is not None:
        if weight.numel() < input.numel():
            weight = weight * self.scale_weight
        else:
            input = input * self.scale_weight
    weight = self._get_weight_with_lora(weight)
    out = self._linear_forward_impl(input, weight, bias)
    del weight, input, bias
    return out
```

Three things to take from this:

1. **No custom kernel, no custom op, no triton.** It is
   `F.linear(input, weight.to(bf16) * scale, bias)`. The `torch.library.custom_op`
   wrappers at `custom_linear.py:6-41` exist purely to stop `torch.compile` from
   breaking the graph on the LoRA arithmetic — `_linear_forward_impl` picks the
   direct or custom-op variant based on `allow_compile`
   (`custom_linear.py:147-154`). Nothing about scaled fp8 requires them.
2. **The scale is per-tensor (a scalar), not per-channel.** That is forced by
   the `weight.numel() < input.numel()` branch — moving the multiply onto the
   *input* is only algebraically valid for a scalar. So the format is: fp8
   storage + one fp32 scalar per Linear. Cheap to support.
3. **`_scaled` alone buys memory, not speed.** The weight is upcast to the
   activation dtype every forward (`custom_linear.py:244`:
   `weight = self.weight.to(input)`), so the matmul is bf16 as usual. The win is
   ~half the weight bytes resident, and the scale recovers the dynamic range
   that plain fp8 casting loses. Speed comes only from `_fast`.

### The `_fast` path — `torch._scaled_mm`, the only place fp8 math happens

`fp8_optimization.py` is 45 lines. `convert_fp8_linear`
(`fp8_optimization.py:34-45`) monkeypatches `forward` on every Linear not in
`params_to_keep`, stashing `original_forward`, and attaches the scale:

```python
if scale_weight_keys is not None:
    scale_key = f"{name}.scale_weight"
    if scale_key in scale_weight_keys:
        setattr(submodule, "scale_weight", scale_weight_keys[scale_key].float())
```

and the forward (`fp8_optimization.py:6-31`, header comment credits ComfyUI and
MinusZoneAI):

```python
scale_weight = getattr(cls, 'scale_weight', None)
if scale_weight is None:
    scale_weight = torch.ones((), device=input.device, dtype=torch.float32)
else:
    scale_weight = scale_weight.to(input.device).squeeze()
scale_input = torch.ones((), device=input.device, dtype=torch.float32)

input = torch.clamp(input, min=-448, max=448, out=input)
inn = input.reshape(-1, input_shape[2]).to(torch.float8_e4m3fn).contiguous() #always e4m3fn because e5m2 * e5m2 is not supported
bias = cls.bias.to(base_dtype) if cls.bias is not None else None
o = torch._scaled_mm(inn, cls.weight.t(), out_dtype=base_dtype, bias=bias, scale_a=scale_input, scale_b=scale_weight)
```

Notes worth carrying:

- `scale_a` (the **activation** scale) is hardcoded to **1.0**. Activations are
  just clamped to ±448 (the e4m3fn max) and cast. There is no dynamic activation
  quantisation at all. That is a real quality compromise, and it is why `_fast`
  is opt-in rather than default.
- Falls back to `original_forward` for any input that is not rank-3
  (`fp8_optimization.py:28-29`), so norm/embedding paths are untouched.
- `_fast` is incompatible with unmerged LoRAs, asserted twice
  (`nodes_model_loading.py:1761-1762`, `nodes_sampler.py:135-136`:
  `"FP8 matmul with unmerged LoRAs is not supported"`).

### LoRA merging into scaled weights

The fiddly case: merging a LoRA into an fp8-scaled base means the diff has to be
divided/multiplied through the scale. `utils.py:246-264` handles it by
multiplying the dequantised temp weight by the scale before patching:

```python
def patch_weight_to_device(self, key, device_to=None, inplace_update=False, backup_keys=False, scale_weight=None):
    ...
    if scale_weight is not None:
        temp_weight = temp_weight * scale_weight.to(temp_weight.device, temp_weight.dtype)
```

and `utils.py:334-344` then scales the weights that have a `scale_weight` but
were *not* LoRA-patched, guarded by a `scale_weights_applied` flag so it cannot
double-apply. This is the part I would expect to get wrong on a first
implementation.

### Autocast

For fp8 without patched linears, they wrap the whole prediction in autocast
(`nodes_sampler.py:1181-1182`):

```python
autocast_enabled = ("fp8" in model["quantization"] and not transformer.patched_linear)
with torch.autocast(device_type=mm.get_autocast_device(device), dtype=dtype) if autocast_enabled else nullcontext():
```

i.e. autocast is the *fallback* for un-patched fp8; the `CustomLinear` path
handles dtypes explicitly and does not need it.

Also: `params_to_keep` (`nodes_model_loading.py:1724`) lists what never goes to
fp8 — `norm`, `bias`, `time_in`, `patch_embedding`, `time_`, `img_emb`,
`modulation`, `text_embedding`, `adapter`, `add`, `ref_conv`, `audio_proj`. And
in `load_weights` (`nodes_model_loading.py:894-909`) `patch_embedding`,
`motion_encoder`, `condition_embedding` are forced **fp32**, and modulation/norm
keep fp32 if that is how they were stored. Getting `modulation` wrong is a
classic Wan artifact source.

### Pricing this option for us

**Cheap. `_scaled` support is worth having; `_fast` probably is not.**

Supporting `fp8_e4m3fn_scaled` in our diffusers pipeline is: detect
`.scale_weight`/`.weight_scale` keys, strip them out of the state dict, and
subclass `nn.Linear` to do `weight.to(input) * scale` before `F.linear`. Call it
**60-80 lines and an afternoon**, no custom kernels, no compute-capability
floor, and it works on any torch that has `torch.float8_e4m3fn` storage. The
payoff is ~7GB instead of ~14GB for A14B weights with better fidelity than naive
fp8 casting — which is what would let us hold both noise experts, or combine
with block swap for higher-res.

`_fast` (`torch._scaled_mm`) is a different proposition: the 5090 is sm_120 so
the >= 8.9 gate is satisfied, and it is a torch builtin so still no custom ops.
But `scale_a = 1.0` with a raw ±448 clamp on activations is exactly the kind of
silent quality regression that costs us a screening cycle, and it forecloses
unmerged LoRAs — which we need for Lightning. **Skip `_fast`.**

This is our second data point after Lightricks': both converge on *per-tensor
scalar scale, fp8 storage, high-precision matmul*, applied in a Linear subclass.
That consistency is the useful signal — the format is stable enough to support
without tracking a moving target.

---

## 3. Lightning / distill LoRA recipes for Wan 2.2 A14B

These come from the shipped example workflows, which are kijai's own reference
settings. Values below are decoded from the JSON graphs — widget order resolved
against each node's `INPUT_TYPES`, and linked (converted-to-input) widgets
traced to their source constants, because **several of the stale widget values
in the JSON disagree with the constants actually feeding them.** Specifically,
`wanvideo_2_2_I2V_A14B_example_WIP.json` sampler 27 shows `end_step` widget 10
while the `INTConstant` wired to it is **3**. Read the links, not the widgets.

`WanVideoSampler` widget order (`nodes_sampler.py:37-72`):
`steps, cfg, shift, seed, [control_after_generate], force_offload, scheduler,
riflex_freq_index, denoise_strength, batched_cfg, rope_function, start_step,
end_step, add_noise_to_samples`.

### The A14B two-expert structure

There is **no** "expert switch" node. Each expert is a *separate model loader*
with its *own* LoRA and its *own* sampler; the samplers are chained through
`samples` and partitioned by `start_step` / `end_step`
(`nodes_sampler.py:70-71`, tooltips: *"0 means full sampling, otherwise samples
only from this step"* / *"-1 means full sampling"*). Both samplers get the same
`steps`, so the step grid is shared and the handoff is exact.

From `wanvideo_2_2_I2V_A14B_example_WIP.json`, traced end to end:

| | HIGH noise expert | LOW noise expert |
|---|---|---|
| checkpoint | `Wan2_2-I2V-A14B-HIGH_fp8_e4m3fn_scaled_KJ.safetensors` | `Wan2_2-I2V-A14B-LOW_fp8_e4m3fn_scaled_KJ.safetensors` |
| LoRA | `lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16` | same file |
| **LoRA strength** | **3.0** | **1.0** |
| sampler | node 27, `start_step=0`, `end_step=3` | node 90, `start_step=3`, `end_step=-1` |
| cfg | **2.0 on step 0 only, then 1.0** | 1.0 flat |
| steps / shift / scheduler | 6 / 8.0 / `dpm++_sde` | 6 / 8.0 / `dpm++_sde` |

Common to both: `base_precision=fp16_fast`,
`quantization=fp8_e4m3fn_scaled`, `load_device=offload_device`,
`attention_mode=sageattn`, `rope_function=comfy`, `riflex_freq_index=0`,
`force_offload=True`, LoRA `merge_loras=False`, block swap `[20 blocks,
offload_img_emb=False, offload_txt_emb=False, use_non_blocking=False,
prefetch_blocks=1]`, `832x480x81` frames
(`WanVideoImageToVideoEncode` widgets `[832, 480, 81, ...]`), torch.compile
`["inductor", dynamic=False, "default", fullgraph=False, 64, compile_transformer_blocks_only=True, 128]`.

`wanvideo_2_2_I2V_A14B_TimeToMove_example.json` is the *identical* recipe
(same strengths 3.0/1.0, same 0-3/3-6 split, same shift 8, same cfg schedule) —
so this is a settled configuration, not a one-off.

### The strength-3.0-on-HIGH oddity, and the real Lightning LoRA

Note that the I2V A14B examples use a **Wan 2.1** distill LoRA
(`lightx2v_I2V_14B_480p_...`) on a 2.2 model, and compensate for the mismatch on
the high-noise expert by cranking strength to **3.0**. That is the tell: the 2.1
LoRA under-drives 2.2's high-noise expert, so the fix is 3x strength there and
1.0 on low.

The actual `Wan2.2-Lightning` 4-step LoRA does appear, in
`wanvideo_2_2_Fun_control_camera_example_01.json`, and when the *native* 2.2
LoRA is used the strength goes back to **1.0**:

- HIGH: `Wan22-Lightning/Wan2.2-Lightning_I2V-A14B-4steps-lora_HIGH_fp16.safetensors`, **strength 1.0**, on `Wan2_2-Fun-Control-Camera-A14B-HIGH_fp8_e4m3fn_scaled_KJ`
- LOW: `Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16`, **strength 1.0**, on `Wan2_2-I2V-A14B-LOW_fp8_e4m3fn_scaled_KJ`
- 6 steps, cfg 1, **shift 5.0**, `dpm++_sde`, split at **step 2** (`0→2` high, `2→-1` low), block swap 30 with `prefetch_blocks=1`

So: **use strength 1.0 with the native Wan2.2-Lightning LoRA; strength 3.0 is a
workaround for using the 2.1 lightx2v LoRA on the 2.2 high-noise expert.** Note
they mix — Lightning_HIGH on the high expert, lightx2v on the low expert — rather
than using the Lightning LOW file. That is a taste call, not a constraint.

### Steps: 6, not 4

Every A14B distill workflow in the repo runs **6 steps**, not 4, despite the
LoRA being a "4steps" LoRA. The 2.1 example
(`wanvideo_2_1_14B_I2V_example_03.json`) runs **4** steps, shift 5, cfg 1,
`dpm++_sde`, lightx2v strength 1.0 — single expert, no split. So the extra two
steps in 2.2 exist to give the two-expert split somewhere to land: 3+3 or 2+4.

### The boundary

Two data points: **shift 8.0 → split at 3/6**; **shift 5.0 → split at 2/6**.
Both are ~40-50% of the schedule on the high-noise expert. There is no
sigma-threshold-based automatic boundary anywhere in the wrapper — it is a
hand-set integer step index. Worth knowing before we build something cleverer
than the reference and then can't compare against it.

### The CFG trick — this is the thing to steal

`cfg` on the HIGH-noise sampler is not a scalar. It is a per-step list from
`CreateCFGScheduleFloatList` (`nodes_utility.py:202-250`) with
`steps=6` (linked from the shared constant), `cfg_scale_start=2.0`,
`cfg_scale_end=2.0`, `interpolation=linear`, `start_percent=0.0`,
`end_percent=0.01`.

Working through `nodes_utility.py:227-247`: `cfg_list = [1.0]*6`;
`start_idx = 0`; `end_idx = min(int(6*0.01), 5) = 0`; the loop covers `i in
range(0, 1)` so only `cfg_list[0] = 2.0`. Result:

```
cfg = [2.0, 1.0, 1.0, 1.0, 1.0, 1.0]
```

**One step of real classifier-free guidance at the highest noise level, then
distilled cfg=1 for the rest.** The sampler accepts this natively — `cfg` is
normalised to a per-step list at `nodes_sampler.py:207-216`:

```python
if isinstance(cfg, list):
    if steps < len(cfg): ... cfg = cfg[:steps]
    elif steps > len(cfg): ... cfg.extend([cfg[-1]] * (steps - len(cfg)))
    log.info(f"Using per-step cfg list: {cfg}")
else:
    cfg = [cfg] * (steps + 1)
```

and indexed per step at `nodes_sampler.py:2406` / `2500` / `2509`
(`cfg[min(i, len(timesteps)-1)]`). The node description
(`nodes_utility.py:221`) states the intent: *"outside the set range cfg is set
to 1.0"*.

Cost: exactly **one extra transformer forward** out of 6 (the uncond pass on
step 0 only) — ~8% slower for a full CFG pass at the point in the schedule where
composition and subject identity are decided. Given our failure modes are
subject invention/drift and frozen output, this is a direct hit.

### anisora V3.2: NOT HANDLED. No special support exists.

Grepped `anisora` case-insensitively across all `*.py`, `*.json` and `*.md` in
the repo — **zero hits**. There is no anisora-specific loader, LoRA handling,
shift default, or scheduler. The wrapper treats it as any other Wan 2.2 I2V
fine-tune, which means: if anisora V3.2 ships as a full checkpoint it loads
through the ordinary `WanVideoModelLoader` path; if it ships as a LoRA it goes
through `WanVideoLoraSelect` at whatever strength. **We get no reference
settings for anisora from this source** — the community settings we may have
seen for it are not in this repo, so treat them as unverified. Plan to sample it
ourselves.

### For comparison — their TI2V-5B reference (what we run today)

`wanvideo_2_2_5B_I2V_example_WIP.json`, single sampler, single expert:

- `wan2.2_ti2v_5B_fp16.safetensors`, `base_precision=fp16_fast`,
  `quantization=disabled`, `attention_mode=sageattn`
- **steps 30, cfg 5.0, shift 8.0, scheduler `flowmatch_pusa`**, `rope_function=comfy`,
  `riflex_freq_index=0`, no block swap node at all
- the controlnet variants use `Wan2_2-TI2V-5B-FastWanFullAttn_bf16` with the
  *same* 30/5.0/8.0/`flowmatch_pusa` — i.e. they did not re-tune for FastWan

Two things to check against our `wan_i2v.py`: **shift 8.0** for 5B (not 5.0),
and **`flowmatch_pusa`** rather than unipc/euler as the 5B scheduler.

---

## 4. SageAttention integration

### Our recorded note does not check out against this source

We have `sageattn_qk_int8_pv_fp16_cuda` written down as the black-frames fix.
**This repo never names that function.** Grepped `qk_int8|pv_fp16|pv_fp8|sageattn_qk`
across all `*.py`, `*.md`, `*.json`, `*.txt` — the only hits are inside a vendored
third-party directory unrelated to the main path
(`ultravico/sageattn/attn_qk_int8_per_block.py:1`, which is a copy of
thu-ml/DiT-Extrapolation, and `ultravico/sageattn/core.py:7`). Neither is reachable
except via the `sageattn_ultravico` mode.

What they actually do is call the **package-level dispatcher and let it choose the
backend**. `wanvideo/modules/attention.py:14` then `:108-109`:

```python
from sageattention import sageattn
...
elif attention_mode == 'sageattn':
    return sageattn_func(q, k, v, tensor_layout="NHD").contiguous()
```

`sageattn()` in the sageattention package is the auto-dispatching entry point —
it picks the per-arch kernel (the `qk_int8_pv_*` variants) itself based on
compute capability. So:

**Answer: there is no known-good named backend function to copy. Their
known-good integration is "call `sageattn()`, layout `NHD`, and let the package
dispatch."** If `sageattn_qk_int8_pv_fp16_cuda` fixed black frames for us, that
finding is ours alone and is not corroborated here — keep it, but re-label it as
unverified against kijai rather than "the community's fix". It is plausible as a
*workaround*: forcing the fp16-PV kernel avoids whatever the auto-dispatched
fp8-PV path does on our card.

### The wrapper's actual dtype discipline around sage — this is the likelier fix

`attention.py:16-24`, inside the custom op:

```python
if not (q.dtype == k.dtype == v.dtype):
    return sageattn(q, k.to(q.dtype), v.to(q.dtype), attn_mask=..., tensor_layout=tensor_layout)
elif q.dtype == torch.float32:
    return sageattn(q.to(torch.float16), k.to(torch.float16), v.to(torch.float16), ...).to(torch.float32)
else:
    return sageattn(q, k, v, ...)
```

Two guards worth copying verbatim: **k and v are coerced to q's dtype** (a
mismatch is a silent-garbage source), and **fp32 is routed through fp16** rather
than handed to sage.

And the setting that actually matters: **every Wan 2.2 example workflow runs
`base_precision=fp16_fast`, i.e. `torch.float16`, not bf16**
(`nodes_model_loading.py:1143`). `fp16_fast` additionally flips a torch flag
(`nodes_model_loading.py:1145-1153`):

```python
if base_precision == "fp16_fast":
    if hasattr(torch.backends.cuda.matmul, "allow_fp16_accumulation"):
        torch.backends.cuda.matmul.allow_fp16_accumulation = True
    else:
        raise ValueError("torch.backends.cuda.matmul.allow_fp16_accumulation is not available in this version of torch, requires torch 2.7.0.dev2025 02 26 nightly minimum currently")
```

So the reference configuration is **fp16 activations + fp16 accumulation +
`sageattn`**. If we are running bf16 activations into sage, that is a difference
from the known-good path and a plausible cause of the black frames we saw —
sage's int8-QK quantisation is calibrated around fp16 ranges, and the wrapper
never feeds it bf16 in any shipped workflow.

### Blackwell / sm_120

There is **no sm_120 detection and no Blackwell-conditional code path.** The only
`torch.cuda.get_device_capability` call in the entire repo is
`nodes_model_loading.py:1215`, and it is used for one fp8-compile warning
(`< (8, 9)`, `nodes_model_loading.py:1217`), not for attention.

Blackwell support is instead a **separate user-selected mode**, `sageattn_3`
(`nodes_model_loading.py:39`), which imports the SageAttention 3 Blackwell kernel
with a two-step fallback (`attention.py:72-78`):

```python
try:
    from sageattn3 import sageattn3_blackwell as sageattn_blackwell
except Exception:
    try:
        from sageattn import sageattn_blackwell
    except Exception:
        sageattn_blackwell = attention_func_error
```

and calls it with a transpose to head-second layout and `per_block_mean=False`
(`attention.py:102-103`):

```python
elif attention_mode == 'sageattn_3':
    return sageattn_blackwell(q.transpose(1,2), k.transpose(1,2), v.transpose(1,2), per_block_mean=False).transpose(1,2).contiguous()
```

Note `sageattn_3` is **not wrapped in a `torch.library.custom_op`**, unlike
`sageattn`/`sageattn_varlen`/`sageattn_ultravico` — so it will graph-break under
torch.compile. On our 5090 it is the arch-native option and worth an A/B against
plain `sageattn`, but expect to lose compile fusion around attention.

Full mode list (`nodes_model_loading.py:39-40`), **default `sdpa`**
(`nodes_model_loading.py:1090`) — note the default is *not* sage; sage is opted
into by every example workflow:

```python
attention_modes = ["sdpa", "flash_attn_2", "flash_attn_3", "sageattn", "sageattn_3", "radial_sage_attention", "sageattn_compiled",
                    "sageattn_ultravico", "comfy"]
```

The whole dispatcher is 23 lines (`attention.py:95-117`) and has no ComfyUI
dependency except the `comfy` mode itself (`attention.py:4`, `:112-113`) — so
this is directly liftable into our pipeline as an attention-processor swap.

There is also a per-block, per-step-range attention override
(`model.py:3215-3223`, `attention_mode_override` with `blocks`, `start_step`,
`end_step`) — i.e. you can run a cheap kernel on most blocks and an exact one on
a few. Interesting but not a priority.

---

## 5. Sampler / scheduler defaults — reference settings to diff against `wan_i2v.py`

### Node defaults vs. what the Wan 2.2 workflows actually use

The node defaults (`nodes_sampler.py:39-72`) are generic Wan 2.1 values and are
**not** the 2.2 recipe. Both columns matter — the left is what you get if you
change nothing, the right is what kijai ships as the 2.2 I2V A14B example:

| param | node default | 2.2 I2V A14B (distill) | 2.2 TI2V-5B |
|---|---|---|---|
| `steps` | 30 | **6** | **30** |
| `cfg` | 6.0 | **1.0**, with **2.0 on step 0** | **5.0** |
| `shift` | 5.0 | **8.0** | **8.0** |
| `scheduler` | `unipc` | **`dpm++_sde`** | **`flowmatch_pusa`** |
| `riflex_freq_index` | 0 (disabled) | 0 | 0 |
| `force_offload` | True | True | True |
| `denoise_strength` | 1.0 | 1.0 | 1.0 |
| `batched_cfg` | False | False | False |
| `rope_function` | `comfy` | `comfy` | `comfy` |
| `start_step` / `end_step` | 0 / -1 | **0/3 then 3/-1** | 0 / -1 |
| `add_noise_to_samples` | False | False | False |
| resolution / frames | 832x480 / 81 | 832x480 / 81 | 832x480 / 81 |

`rope_function` default is `comfy` with the tooltip explaining why
(`nodes_sampler.py:60`): *"Comfy's RoPE implementation doesn't use complex
numbers and can thus be compiled, that should be a lot faster when using
torch.compile. Chunked version has reduced peak VRAM usage when not using
torch.compile"*. If our pipeline uses a complex-number RoPE and we want
`torch.compile`, that is a known blocker.

### Scheduler construction

Full list at `wanvideo/schedulers/__init__.py:21-38`. The two that matter:

`dpm++_sde` (`schedulers/__init__.py:77-86`):

```python
elif 'dpm' in scheduler:
    if 'sde' in scheduler:
        algorithm_type = "sde-dpmsolver++"
    else:
        algorithm_type = "dpmsolver++"
    sample_scheduler = FlowDPMSolverMultistepScheduler(shift=shift, algorithm_type=algorithm_type)
    if sigmas is None:
        sample_scheduler.set_timesteps(steps, device=device, use_beta_sigmas=('beta' in scheduler))
```

`FlowDPMSolverMultistepScheduler` is their vendored copy
(`wanvideo/schedulers/fm_solvers.py`), Wan-repo lineage, not diffusers'. The
closest diffusers equivalent for us is `DPMSolverMultistepScheduler` with
`algorithm_type="sde-dpmsolver++"` and `use_flow_sigmas=True` — worth an
explicit numerical comparison rather than assuming equivalence.

`flowmatch_pusa` for 5B (`schedulers/__init__.py:130-135`), note the `steps+1`:

```python
elif 'flowmatch_pusa' in scheduler:
    sample_scheduler = FlowMatchSchedulerPusa(shift=shift, sigma_min=0.0, extra_one_step=True)
    if sigmas is None:
        sample_scheduler.set_timesteps(steps+1, denoising_strength=denoise_strength, shift=shift)
```

`shift` is passed to the constructor **and** to `set_timesteps` — if we only pass
it in one place in our pipeline, the sigmas will differ.

For context on distill schedules generally: the hardcoded 4-step lists are
`flowmatch_distill` → `[999, 750, 500, 250]` (`schedulers/__init__.py:120`,
raises if `steps != 4` at `:125-126`) and `flowmatch_causvid` 14B →
`[999, 934, 862, 756, 603, 410, 250, 140, 74]` (`schedulers/__init__.py:104`).
Neither is what the Lightning workflows use — those use `dpm++_sde` on an
ordinary 6-step grid.

### Negative prompt handling — and the trap in it

**There is no default negative prompt in the code.** Both text-encode nodes
declare `"negative_prompt": ("STRING", {"default": "", "multiline": True})`
(`nodes.py:198` and `nodes.py:290`). The canonical Wan negative lives only in the
example workflows.

The important mechanical fact: **at `cfg == 1.0` the negative prompt is never
used.** `nodes_sampler.py:1526` returns immediately after the conditional pass:

```python
noise_pred_cond = noise_pred_cond[0]
...
if math.isclose(cfg_scale, 1.0):
    if use_fresca:
        noise_pred_cond = fourier_filter(noise_pred_cond, fresca_scale_low, fresca_scale_high, fresca_freq_cutoff)
    ...
```

and negative embeds are only validated when cfg differs from 1
(`nodes_sampler.py:1506-1508`):

```python
if not math.isclose(cfg_scale, 1.0):
    if negative_embeds is None:
        raise ValueError("Negative embeddings must be provided for CFG scale > 1.0")
```

Combined with the per-step cfg list from §3, this means: **in a distilled cfg=1
pipeline the negative prompt is inert, and the `CreateCFGScheduleFloatList`
step-0 spike is exactly what switches it back on for one step.** See §6.

---

## 6. Our known failure modes — what this source addresses

### 6a. Static / frozen output — there are FOUR explicit knobs

This is the best material in the repo for us. `WanVideoImageToVideoEncode`
(`nodes.py:985-1011`) exposes motion-amplitude controls whose tooltips name our
exact symptom:

```python
"noise_aug_strength": ("FLOAT", {"default": 0.0, ..., "tooltip": "Strength of noise augmentation, helpful for I2V where some noise can add motion and give sharper results"}),   # nodes.py:992
"start_latent_strength": ("FLOAT", {"default": 1.0, ..., "tooltip": "Additional latent multiplier, helpful for I2V where lower values allow for more motion"}),                    # nodes.py:993
"end_latent_strength": ("FLOAT", {"default": 1.0, ..., "tooltip": "Additional latent multiplier, helpful for I2V where lower values allow for more motion"}),                      # nodes.py:994
"augment_empty_frames": ("FLOAT", {"default": 0.0, ..., "tooltip": "EXPERIMENTAL: Augment empty frames with the difference to the start image to force more motion"}),             # nodes.py:1008
```

All four are trivially portable — they operate on the **conditioning latent**
`y`, not on the model. Implementations:

`start_latent_strength` / `end_latent_strength` (`nodes.py:1140-1141`) — two
lines, applied right after the VAE encode of the conditioning stack:

```python
y[:, :1]  *= start_latent_strength
y[:, -1:] *= end_latent_strength
```

`y[:, :1]` is the first conditioning latent frame (our start image). Scaling it
**down** weakens the model's anchor to the start frame, which is precisely what
"first frame repeated 81 times" is — an over-strong anchor. Try `0.9`, `0.8`.

`augment_empty_frames` (`nodes.py:1142-1144`) — pushes the *padding* frames away
from the start frame, i.e. manufactures an initial gradient for motion to follow:

```python
if augment_empty_frames > 0.0:
    frame_is_empty = (mask[0].mean(dim=(-2, -1)) < 0.5).view(1, -1, 1, 1)
    y = y[:, :1] + (y - y[:, :1]) * ((augment_empty_frames+1) * frame_is_empty + ~frame_is_empty)
```

Read it as: for empty (non-conditioned) frames, amplify the deviation from the
start latent by `(augment_empty_frames + 1)`; leave conditioned frames alone.

`noise_aug_strength` (`nodes.py:1073-1074`, `1083-1084`) adds noise to the
reference **image pixels** before encoding, via `utils.py`'s
`add_noise_to_reference_video`:

```python
def add_noise_to_reference_video(image, ratio=None):
    sigma = torch.ones((image.shape[0],)).to(image.device, image.dtype) * ratio
    image_noise = torch.randn_like(image) * sigma[:, None, None, None]
    image_noise = torch.where(image==-1, torch.zeros_like(image), image_noise)
    image = image + image_noise
    return image
```

Note the `image == -1` guard — padding regions (encoded as -1) are left clean.

**All four default to "off"** in both the node defaults and the shipped 2.2
workflows (`WanVideoImageToVideoEncode` widgets in the A14B example are
`[832, 480, 81, 0, 1, 1, true, false, false]` → `noise_aug_strength=0`,
`start_latent_strength=1`, `end_latent_strength=1`). So these are documented
escape hatches, not part of the reference recipe. Which is the right way to read
them: reach for them when the reference recipe produces frozen frames.

### 6b. The anti-static negatives — confirmed, and there are four of them

The negative prompt in the A14B example workflow (`WanVideoTextEncode` node 16)
is the canonical Wan negative, verbatim:

```
色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走
```

The motion-suppressing terms, which is what we care about — there are **four**
distinct ones, not one:

| term | meaning |
|---|---|
| 静态 | static |
| 静止 | still / motionless |
| 静止不动的画面 | a motionless, unmoving picture |
| 整体发灰 | overall greyish (the washed-out look frozen output has) |

plus the "it's a still artwork not a video" cluster: 风格 (style), 作品
(artwork), 画作 (painting), 画面 (picture/frame). And 倒着走 (walking backwards),
which is a motion-*direction* negative — relevant if we ever see reversed gait.

The rest are anatomy/quality: 多余的手指 (extra fingers), 画得不好的手部 (poorly
drawn hands), 手指融合 (fused fingers), 三条腿 (three legs), 畸形的 (deformed),
毁容的 (disfigured), 形态畸形的肢体 (malformed limbs), 残缺的 (mutilated),
背景人很多 (many background people), 杂乱的背景 (cluttered background),
JPEG压缩残留, 最差质量, 低质量, 丑陋的, 过曝 (overexposed), 色调艳丽 (garish
colour), 细节模糊不清 (blurred indistinct detail), 字幕 (subtitles).

Given our recent commits around hand quality and dropped negative terms, note
that the canonical list already carries four separate hand/finger negatives —
worth checking ours has all four rather than one.

**But — and this is the finding that ties §3, §5 and §6 together — at cfg=1.0
this entire negative prompt does absolutely nothing.** The uncond forward is
skipped (`nodes_sampler.py:1526`). A distilled 4- or 6-step run at flat cfg=1
with a beautiful anti-static negative prompt is running with **no negative
prompt at all**. The `CreateCFGScheduleFloatList(cfg_start=2.0, cfg_end=2.0,
start_percent=0.0, end_percent=0.01)` on the high-noise expert is what buys one
step where the negative actually applies — at the highest noise level, where
"is this a video or a still" is decided.

### 6c. Subject invention / drift

Nothing purpose-built, but three relevant mechanisms:

**Skip Layer Guidance** (`WanVideoSLG`, `nodes.py:1690-1714`) — skips the uncond
pass on chosen blocks, defaults `blocks="10"`, `start_percent=0.1`,
`end_percent=1.0`, description *"Skips uncond on the selected blocks"*.
Implemented in the block loop at `model.py:3262-3265`:

```python
if self.slg_blocks is not None:
    if b in self.slg_blocks and is_uncond:
        if self.slg_start_percent <= current_step_percentage <= self.slg_end_percent:
            continue
```

Note it only fires on the uncond pass, so like the negative prompt it is **inert
at cfg=1**. Not usable in our distilled path except during the step-0 spike.

**Enhance-A-Video / FETA** (`WanVideoEnhanceAVideo`, `nodes.py:24-42`) — default
`weight=2.0`, `start_percent=0.0`, `end_percent=1.0`, points at
NUS-HPC-AI-Lab/Enhance-A-Video. Amplifies cross-frame attention correlation; it
is a temporal-consistency lever and works on the cond pass, so unlike SLG it
does function at cfg=1. Not used in the shipped 2.2 workflows.

**CFG-Zero-Star / FreSca / TCFG / RAAG / TSR** (`WanVideoExperimentalArgs`,
`nodes.py`, all default off): `cfg_zero_star`, `use_zero_init`,
`zero_star_steps=0`; `use_fresca` with `fresca_scale_low=1.0`,
`fresca_scale_high=1.25`, `fresca_freq_cutoff=20`; `use_tcfg` (*"TCFG:
Tangential Damping Classifier-free Guidance. CFG artifacts reduction"*);
`raag_alpha=0.0`; `temporal_score_rescaling` with `tsr_k=0.95`, `tsr_sigma=1.0`.
All of the CFG-derived ones are again cfg>1-only. `temporal_score_rescaling`
(*"The sampling temperature"* / *"How early TSR steer the sampling process"*) is
the one that plausibly touches motion at cfg=1 — untested by us, and not enabled
in any shipped workflow.

Net: **the wrapper's anti-drift toolkit is almost entirely CFG-based, and
therefore almost entirely unavailable in a distilled cfg=1 pipeline.** That is a
structural argument for the step-0 CFG spike rather than a menu of alternatives.

### 6d. One incidental operational note worth keeping

`readme.md` (memory section) documents that unmerged LoRA weights are now
registered as **buffers on the blocks**, so they participate in block swap:

> *"you use 1GB LoRA unmerged and swap 20 blocks on 14B model, we can divide the
> LoRA size by block count, single block grows by 25MB, 20 blocks grow by 500MB,
> so your VRAM usage would be 500MB more than before, to compensate you swap 2
> more blocks."*

And: *"if you did not use block swap, you will see increased memory use as the
LoRAs are part of the model and all on VRAM."* Relevant if we combine unmerged
Lightning LoRAs with a block-swap implementation of our own — attach LoRA tensors
to the block, not to a side table, or they will not move with it.

Also from `readme.md`: on Windows, `torch.compile` first-run VRAM spikes are
usually a stale Triton cache; clear `C:\Users\<username>\.triton` and
`C:\Users\<username>\AppData\Local\Temp\torchinductor_<username>`. We are on a
Windows box, so this is a real one to know.

---

## Cross-cutting: the reference `torch.compile` settings

Every 2.2 workflow uses `WanVideoTorchCompileSettings` with
`["inductor", dynamic=False, "default", fullgraph=False, 64, compile_transformer_blocks_only=True, 128]`.
The `compile_transformer_blocks_only=True` is the notable one — compile the
blocks, not the whole model, which is also what makes block swap and compile
coexist. The note in the example workflow (node 44) claims *"If you have Triton
installed, connect this for ~30% speed increase"*.

## What this source does NOT give us

- **anisora V3.2**: zero support, zero settings. Verified by exhaustive grep.
- **A VRAM-budget → blocks_to_swap heuristic**: does not exist; it is a manual dial.
- **A named known-good SageAttention backend function**: they call the
  auto-dispatcher. Our `sageattn_qk_int8_pv_fp16_cuda` note is not corroborated here.
- **A sigma-based expert boundary**: hand-set integer step index only.
- **Working async block prefetch**: the CUDA stream is commented out
  (`model.py:3203`) and the CPU buffers are not pinned.
