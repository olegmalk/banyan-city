# Wan 2.2 — what the authors' own inference code actually does

Read on 2026-08-04 from the official repo, cloned shallow:
`https://github.com/Wan-Video/Wan2.2` @ `42bf4cf` ("fix readme"), org
`Wan-Video` = Alibaba's Wan team (`LICENSE.txt` = Apache 2.0, headers read
"Copyright 2024-2025 The Alibaba Wan Team Authors"). Not a mirror.

Why this document exists: we run TI2V-5B through **our own diffusers pipeline**
(`pipeline/wan_i2v.py`), not through their `generate.py`. Every number we chose
was chosen without reading theirs. This is the comparison. Citations are
`path:line` into the clone; the clone is scratch and will be deleted, so the
quoted values are reproduced here rather than pointed at.

Nothing in this document was executed. Read-only pass over source + README. The
one exception is arithmetic: §4's timestep tables reimplement the scheduler's
own formula from the source rather than running it, and are marked as such.

**In a hurry: read §7 (summary) — reference settings, the consumer-GPU recipe
per model, the A14B-at-4-steps answer, and the three things we do differently.**

---

## 1. Official reference settings, per model

From `wan/configs/`. `wan_shared_cfg` is the base every model updates over, so
a value not overridden in a model's own file is inherited from it —
`sample_fps` and `frame_num` are the two that bite.

`wan/configs/shared_config.py:6-20` — inherited by all:

| field | value |
|---|---|
| `t5_model` | `umt5_xxl` |
| `t5_dtype` | `torch.bfloat16` |
| `text_len` | 512 |
| `param_dtype` | `torch.bfloat16` |
| `num_train_timesteps` | 1000 |
| `sample_fps` | **16** (TI2V-5B overrides to 24; A14B does NOT) |
| `frame_num` | **81** (TI2V-5B overrides to 121; A14B does NOT) |
| `sample_neg_prompt` | the Chinese list — see §5 |

Per model (blank = inherited from shared):

| field | ti2v-5B `wan_ti2v_5B.py` | i2v-A14B `wan_i2v_A14B.py` | t2v-A14B `wan_t2v_A14B.py` |
|---|---|---|---|
| `sample_steps` | **50** (:34) | **40** (:35) | **40** (:35) |
| `sample_guide_scale` | **5.0** (:35) | **(3.5, 3.5)** low,high (:37) | **(3.0, 4.0)** low,high (:37) |
| `sample_shift` | **5.0** (:33) | **5.0** (:34) | **12.0** (:34) |
| `sample_fps` | **24** (:32) | 16 (inherited) | 16 (inherited) |
| `frame_num` | **121** (:36) | 81 (inherited) | 81 (inherited) |
| `boundary` | — (single model) | **0.900** (:36) | **0.875** (:36) |
| `vae_checkpoint` | `Wan2.2_VAE.pth` (:16) | `Wan2.1_VAE.pth` (:17) | `Wan2.1_VAE.pth` (:16) |
| `vae_stride` | **(4, 16, 16)** (:17) | (4, 8, 8) (:18) | (4, 8, 8) (:17) |
| `patch_size` | (1,2,2) | (1,2,2) | (1,2,2) |
| `dim` / `ffn_dim` | 3072 / 14336 | 5120 / 13824 | 5120 / 13824 |
| `num_heads` / `num_layers` | 24 / 30 | 40 / 40 | 40 / 40 |
| `qk_norm`, `cross_attn_norm` | True, True | True, True | True, True |
| `eps` | 1e-6 | 1e-6 | 1e-6 |

`sample_solver` is not in the configs — it is a `generate.py` CLI flag
(see §1b) defaulting to `unipc`, with `dpm++` as the alternative.

**TI2V-5B's reference clip is therefore 121 frames @ 24fps = 5.04s at 50 steps,
shift 5.0, guide 5.0, 704x1280.** That is the exact configuration behind the
"under 9 minutes on a 4090" claim on the model card.

Note `vae_stride` (4,16,16) on the 5B against (4,8,8) on the A14Bs: the 5B's
Wan2.2 VAE compresses space 16x per axis, which is why a 5B model can serve
704x1280 natively at all. Latent grid for 704x1280x121 is
`121/4=31 (30+1) x 44 x 80`; for the A14B at 720x1280x81 it is `21 x 90 x 160`
— **~4.6x more latent tokens per frame-step on the A14B before counting its
larger dim.** Relevant to tomorrow's A14B test: the step cost gap is not just
5B vs 14B params, it is also 4x the token count.

### 1b. `generate.py` argument defaults and the resolution rules

`generate.py:57-198` (arg parser). Sentinel-style defaults — `-1` / `None`
means "take the model config's value", resolved in `_validate_args`:

- `--frame_num` default `None` → `cfg.frame_num` (`generate.py:275`), and
  **must be 4n+1**: `assert args.frame_num % 4 == 1` (`generate.py:277`).
  Our `frames - (frames % 4) + 1` in `wan_i2v.py:275` and `:470` computes the
  same grid; their assert is the same rule stated as a check.
- `--sample_steps` default `None` → `cfg.sample_steps` (`generate.py:271`).
- `--sample_shift` default `None` → `cfg.sample_shift` (`generate.py:284`).
- `--sample_guide_scale` default `None` → `cfg.sample_guide_scale`
  (`generate.py:287`).
- `--sample_solver` default `'unipc'`, choices `['unipc', 'dpm++']`
  (`generate.py:170-174`).
- `--base_seed` default `-1` → random (`generate.py:280-282`).
- `--size` default `'1280*720'`, validated against
  `SUPPORTED_SIZES[task]` (`generate.py:265-268`).
- `--convert_model_dtype` store_true (`generate.py:120`).
- `--offload_model` default `None` → **True when single-GPU, False when
  distributed** (`generate.py:257-262`).
- `--t5_cpu` store_true (`generate.py:116`).

`wan/configs/__init__.py:43-49` — supported sizes, and the 5B is the odd one:

```
't2v-A14B':  ('720*1280', '1280*720', '480*832', '832*480')
'i2v-A14B':  ('720*1280', '1280*720', '480*832', '832*480')
'ti2v-5B':   ('704*1280', '1280*704')          # ONLY these two
```

**TI2V-5B officially supports 704x1280 and 1280x704 and nothing else.** Our
`--size` default is `480x832` (`wan_i2v.py:554`) — a bucket that is on the
A14B list but *not* on the 5B's. It runs (the diffusers pipeline does not
enforce a table), but it is off-spec for the model we actually use, and the
704x1280 canary that "answered a question five whole-batch attempts had only
failed at" was the model's own native resolution.

### 1c. Where our numbers differ from theirs (TI2V-5B)

| knob | ours (`pipeline/wan_i2v.py`) | official | note |
|---|---|---|---|
| steps | **25** (`:551`) | **50** | half. Our step sweep (06/10/14/20) sat entirely below their reference. |
| guidance | 5.0 (`:552`) | 5.0 | match |
| shift | **never set** | **5.0** | see below — this is the big one |
| fps | 24 (`:577`) | 24 | match |
| frames | `4.0s` → 97 (`:550`,`:275`) | 121 (5.04s) | ours is shorter; both valid 4n+1 |
| size | **480x832** (`:554`) | 704x1280 | off the 5B's supported list |
| dtype | bfloat16 (`:249`,`:304`) | bfloat16 | match |
| solver | diffusers default for the repo's `scheduler_config.json` | `unipc` (or `dpm++`) | not directly comparable across libs |

**`shift` is unset in our pipeline.** We construct a scheduler explicitly only
on the AnimeGen path — `FlowMatchEulerDiscreteScheduler(shift=3.0)`
(`wan_i2v.py:215`) — where the value 3.0 matches neither of Alibaba's A14B
figures (5.0 for i2v, 12.0 for t2v). On the 5B path we pass no scheduler at
all, so we inherit whatever `Wan-AI/Wan2.2-TI2V-5B-Diffusers`'
`scheduler_config.json` ships; that is *probably* shift 5.0 (the diffusers port
is by the same team) but we have never checked it, and it is the single
parameter that most directly controls how much of the trajectory is spent in
the high-noise regime — i.e. how much large-scale *motion* gets established
versus refined. Given 2026-08-03's open question is "beat 1 basically doesn't
move at all", an unverified shift is a live suspect and a one-line check.

---

## 2. Memory / offload options — what each one actually does

All four are plumbed from `generate.py` into every pipeline's `__init__` or
`generate()`. None of them is diffusers' `enable_model_cpu_offload()`; they are
hand-rolled and coarser.

**`--offload_model` (bool, default True on single GPU / False when
`world_size > 1` — `generate.py:322-325`, `:257-262`)**
Not per-module streaming. It is a small number of whole-model `.to()` moves at
fixed points in the sample loop:

- move the T5 text encoder to GPU, encode positive + negative, then
  `self.text_encoder.model.cpu()` (`textimage2video.py:500-505`;
  `image2video.py:302-307`).
- move the DiT to GPU once before the loop (`textimage2video.py:563-565`).
- `torch.cuda.empty_cache()` after *each* of the two CFG forwards inside every
  step (`textimage2video.py:582-587`; `image2video.py:395-400`).
- after the loop, `self.model.cpu()` + synchronize + `empty_cache()` before the
  VAE decode (`textimage2video.py:603-606`) — so the DiT is never resident at
  the same time as the VAE decode. On the A14B, both experts go to CPU
  (`image2video.py:415-418`).
- final `gc.collect()` + `torch.cuda.synchronize()` (`:613-615`).

The cost is therefore ~2 `empty_cache()` calls per step, not a full weight
round-trip per step. The DiT stays on the GPU for the whole loop.
**On the A14B it additionally drives expert swapping** — see §4.

**`--convert_model_dtype` (store_true — `generate.py:220-223`)**
One line: `model.to(self.param_dtype)` i.e. `.to(torch.bfloat16)`
(`textimage2video.py:155-156`, `image2video.py:165-166`). Docstring: "Convert
DiT model parameters dtype to 'config.param_dtype'. Only works without FSDP."
**Without this flag the DiT stays in whatever dtype the checkpoint shipped
in**, and `WanModel.from_pretrained` does not force bf16 — so the default
`generate.py` run holds fp32 weights and only *computes* in bf16 via
`torch.amp.autocast('cuda', dtype=self.param_dtype)`
(`textimage2video.py:330`, `image2video.py:336`). That is exactly the "34GB on
disk, transformer 20GB fp32" observation already recorded in
`wan_i2v.py:325-330` — and it is why every consumer-GPU command in their README
passes `--convert_model_dtype`. We get this for free (`torch_dtype=bfloat16` at
`from_pretrained`, `wan_i2v.py:304`), so it is not a gap on our side.

**`--t5_cpu` (store_true — `generate.py:149-153`)**
Runs the UMT5-XXL encoder on the CPU and moves only the resulting embeddings to
GPU (`textimage2video.py:506-510`, `image2video.py:308-312`). Docstring: "Only
works without t5_fsdp." Note this is *encode on CPU*, not "reuse cached
embeddings" — the pipeline still does its own encoding, so it is not the thing
that broke our image conditioning. Cost is CPU T5 latency once per clip;
saving is ~11GB of VRAM never touched.

**`init_on_cpu` (constructor kwarg, default True — not a CLI flag)**
`textimage2video.py:46`, `:79`, `:157-158`. Builds the DiT on CPU and defers
the `.to(device)` to the sample loop. Forced False when any of
`t5_fsdp/dit_fsdp/use_sp` is set (`:84-85`).

### 2a. Their recommended consumer-GPU recipe, verbatim

**(a) TI2V-5B — this is the one that matters to us.** `README.md:228` (t2v) and
`README.md:240` (i2v):

```
python generate.py --task ti2v-5B --size 1280*704 --ckpt_dir ./Wan2.2-TI2V-5B \
  --offload_model True --convert_model_dtype --t5_cpu \
  --image examples/i2v_input.JPG --prompt "..."
```

`README.md:233`: "This command can run on a GPU with at least 24GB VRAM (e.g,
RTX 4090 GPU)." `README.md:235`: "If you are running on a GPU with at least
80GB VRAM, you can remove the `--offload_model True`, `--convert_model_dtype`
and `--t5_cpu` options to speed up execution."

So **all three flags together are the 24GB recipe**, and the "under 9 minutes
on a 4090" figure is a *fully offloaded, T5-on-CPU* number. Note the size is
given as `1280*704` (landscape); the 9:16 equivalent is `704*1280`.

**(b) I2V-A14B — they do not claim it runs on 24GB.** `README.md:197`:

```
python generate.py --task i2v-A14B --size 1280*720 --ckpt_dir ./Wan2.2-I2V-A14B \
  --offload_model True --convert_model_dtype --image ... --prompt "..."
```

`README.md:200`: "This command can run on a GPU with at least **80GB** VRAM."
`README.md:151`: "If you encounter OOM (Out-of-Memory) issues, you can use the
`--offload_model True`, `--convert_model_dtype` and `--t5_cpu` options to
reduce GPU memory usage." — i.e. adding `--t5_cpu` is the whole of their extra
advice, and it is still an 80GB command with it. The benchmark footnote
(`README.md:435`) confirms the split: "Single-GPU: 14B: `--offload_model True
--convert_model_dtype`, 5B: `--offload_model True --convert_model_dtype
--t5_cpu`".

**There is no official 24GB recipe for A14B.** For that they point elsewhere —
`README.md:57`: "[DiffSynth-Studio] provides comprehensive support for Wan 2.2,
including low-GPU-memory layer-by-layer offload, FP8 quantization, sequence
parallelism, LoRA training, full training." That is the same class of technique
as the fp8 layerwise casting we already do on the AnimeGen path
(`wan_i2v.py:165-172`) — so our approach there is the sanctioned one, just via
diffusers instead of DiffSynth. The 80GB figure is also the number
`wan_i2v.py:133-137` already corrected itself about: it is the *base* A14B
README's, and AnimeGen's own card says 24GB. Both are true of different recipes.

---

## 3. Multi-GPU — and no, not across two machines

What exists, all of it single-node:

- **FSDP** for the DiT (`--dit_fsdp`) and T5 (`--t5_fsdp`).
  `wan/distributed/fsdp.py:12-35`: PyTorch `FullyShardedDataParallel`,
  `sharding_strategy=ShardingStrategy.FULL_SHARD`, auto-wrap per transformer
  block (`lambda_fn=lambda m: m in model.blocks`), `MixedPrecision(param_dtype=
  bfloat16, reduce_dtype=float32, buffer_dtype=float32)`,
  `sync_module_states=True`. FULL_SHARD means every block's parameters are
  all-gathered from all ranks on every forward pass.
- **DeepSpeed Ulysses sequence parallelism** (`--ulysses_size N`).
  `wan/distributed/ulysses.py:9-46` — `distributed_attention()` does
  `all_to_all` on q, k and v (scatter head dim, gather sequence dim), runs
  flash attention on the local shard, then `all_to_all` back. Four collectives
  per attention layer per forward. Installed by monkey-patching each block's
  `self_attn.forward` and the model's `forward`
  (`textimage2video.py:143-147`).
- **Ring attention: not present.** No ring/striped attention anywhere in the
  repo. `README.md:156` names only FSDP + Ulysses.
- **DeepSpeed the library: not a dependency** (`requirements.txt` has no
  deepspeed) — only the Ulysses *algorithm* is reimplemented.
- Constraints: `cfg.num_heads % ulysses_size == 0` (`generate.py:363`),
  `ulysses_size == world_size` (`:342`), and both FSDP and SP hard-assert
  against non-distributed use (`:334-339`).

**Interconnect assumption: NVLink/PCIe inside one box.** Both init paths
hardcode `backend="nccl"` (`generate.py:328-332`; `wan/distributed/util.py:8-10`
`dist.init_process_group(backend='nccl')`). Every launch example in the README
is `torchrun --nproc_per_node=8` on a single node (`:160`, `:208`, `:251`,
`:275`) — there is no `--nnodes`/`--master_addr` example except
`--nnodes 1` for animate (`:342`).

**Usable across two machines on gigabit Ethernet: no.** NCCL *can* fall back to
TCP sockets, so it would technically launch, but the traffic is not close to
survivable. Worked for our case — TI2V-5B, 704x1280, 121 frames, 2 ranks:

- latent grid `31 x 44 x 80`, patch (1,2,2) → `seq_len = 31*40*22 = 27280`
  tokens (`textimage2video.py:480-483`).
- q (or k, or v) is `27280 x 3072` bf16 = **168 MB**. A 2-rank `all_to_all`
  moves half of each ≈ 84 MB; four collectives per attention layer ≈ **336 MB
  per layer per forward**.
- 30 layers → ~10 GB per forward. CFG is two forwards per step (§6) → **~20 GB
  per sampling step**. 50 steps → **~1 TB of all-to-all per clip.**
- gigabit Ethernet at a perfect 125 MB/s = **~160 s of pure network per step**
  against our measured 8.67 s/step of compute. ~18x slower than one GPU, and
  Ulysses would make the clip *worse than useless*.

FSDP over the same link is no better: FULL_SHARD re-gathers ~10 GB of bf16 5B
weights every forward, ~80 s per forward at 1 GbE. And `distributed_attention`
calls `flash_attention` directly (`ulysses.py:38`), so the SP path additionally
hard-requires flash-attn — see §6.

**Conclusion for the laptop farm: two machines cannot split one clip.** The
only sound multi-machine unit of work is *one whole clip per machine*, which is
what `farm_worker.py` already does. Nothing in Alibaba's code changes that.

---

## 4. A14B expert switching — and the 4-step answer

### How it works

Two full 14B DiTs, loaded as separate models from subfolders
`low_noise_model` / `high_noise_model` (`image2video.py:104-120`, names from
`wan_i2v_A14B.py:30-31`). `README.md:450`: "a high-noise expert for the early
stages, focusing on overall layout; and a low-noise expert for the later
stages, refining video details. Each expert model has about 14B parameters,
resulting in a total of 27B parameters but only 14B active parameters per step."

The schedule is a **single hard threshold on the timestep**, not a blend:

```python
boundary = self.boundary * self.num_train_timesteps      # image2video.py:341
...
def _prepare_model_for_timestep(self, t, boundary, offload_model):
    if t.item() >= boundary:
        required_model_name = 'high_noise_model'          # :189-191
    else:
        required_model_name = 'low_noise_model'           # :192-194
```

`boundary = 0.900` for i2v-A14B (`wan_i2v_A14B.py:36`) → threshold **t = 900**
of 1000. (t2v-A14B uses 0.875 → 875, `wan_t2v_A14B.py:36`.)

Two consequences worth knowing:

1. **The guidance scale switches with the expert too.**
   `image2video.py:390-391`: `sample_guide_scale = guide_scale[1] if t >=
   boundary else guide_scale[0]` — and the config tuple is *documented
   low-first*: `sample_guide_scale = (3.5, 3.5)  # low noise, high noise`
   (`wan_i2v_A14B.py:37`). For i2v both are 3.5 so it is invisible; for t2v it
   is `(3.0, 4.0)` — **4.0 while the high-noise expert runs, 3.0 after.** Note
   3.5 is also well below the 5.0 the 5B uses and below our default.
2. **Expert swapping is what `--offload_model` costs on the A14B.**
   `_prepare_model_for_timestep` moves the *other* expert to CPU and the
   required one to GPU (`:195-203`), guarded by a device check so it is a no-op
   except at the crossing. With `offload_model or init_on_cpu` true there is
   therefore exactly **one** ~14B CPU↔GPU round trip per clip, at the boundary
   crossing — not one per step. Good news for a 24GB card: the swap is cheap
   and happens once.

### Which expert gets which steps at 4 steps

The timestep grid is deterministic given (steps, shift). From
`fm_solvers_unipc.py:109-134` (init with `shift=1`: `sigma_max = 0.999`,
`sigma_min = 0.0`) and `:184-213`
(`sigmas = linspace(sigma_max, sigma_min, N+1)[:-1]`, then
`sigmas = shift*sigmas/(1+(shift-1)*sigmas)`, then
`timesteps = (sigmas*1000).astype(int64)`). Reproducing that arithmetic:

| steps | shift 5.0 (official i2v-A14B) | high-noise steps @ boundary 900 |
|---|---|---|
| **4** | **999, 937, 833, 624** | **2 of 4** (999, 937) |
| 8 | 999, 972, 937, 892, 833, 749, 624, 416 | 3 of 8 |
| 40 (reference) | 999 … | 15 of 40 |
| 50 | 999 … | 18 of 50 |

| steps | shift 3.0 (**what our AnimeGen path sets**) | high-noise steps @ 900 |
|---|---|---|
| **4** | **999, 899, 749, 499** | **1 of 4** (999 only) |
| 40 | 999 … | 10 of 40 |

**Answer: at 4 steps and the official shift of 5.0, the high-noise expert runs
steps 1-2 and the low-noise expert runs steps 3-4 — a 50/50 split, which is
roughly the 37.5% high-noise share of the 40-step reference, so a 4-step
distilled run does *not* structurally starve either expert.**

**But our shift = 3.0 halves that to 1 of 4, on a one-integer margin.**
`wan_i2v.py:215` constructs `FlowMatchEulerDiscreteScheduler(shift=3.0)` for
the AnimeGen A14B path. At shift 3.0 and 4 steps the second timestep lands at
**t = 899 against a boundary of 900** — it misses the high-noise expert by one
unit of 1000. Layout-and-motion (the high-noise expert's job, per
`README.md:450`) would get **one** forward pass out of four, and the remaining
three would be the detail-refiner working on whatever that single pass laid
down. That is a plausible mechanism for exactly the complaint on the table
("basically doesn't move at all") and it is a one-line change to test.

Two caveats stated plainly:

- `shift=3.0` is not arbitrary — it matches Alibaba's own note "If you want to
  generate a 480p video, it is recommended to set the shift value to 3.0"
  (`textimage2video.py:439`, `image2video.py:232`). But we render 704x1280,
  which is their 720p case, where the recommendation is **5.0**
  (`wan_i2v_A14B.py:34`). The 3.0 is the right number for the wrong resolution.
- Our path runs **diffusers**, not this code, so the exact integers depend on
  diffusers' `FlowMatchEulerDiscreteScheduler` grid (which starts at
  `sigma_max = 1.0`, not 0.999) and on whether diffusers switches experts by
  the same `boundary_ratio`. Under diffusers' formula the 4-step shift-3.0 grid
  works out to ~`[1000, 857, 600, 3]` — still **1 of 4** high-noise, same
  conclusion, different integers. **Verify on the render machine with a
  one-line print of `scheduler.timesteps` and the pipeline's
  `boundary_ratio`** before spending a render on it; the conclusion above is
  from Alibaba's source, the diffusers translation of it is not.

---

## 5. Prompt handling

### 5a. The official negative prompt, and the four terms we drop

`wan/configs/shared_config.py:19` — one string, shared by every model, no
per-model override anywhere in the repo. There are **no comments** on it in the
source; the terms are unannotated. 28 comma-separated terms, joined with
**fullwidth commas (U+FF0C `，`)**, no spaces:

```
色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，
最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，
画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，
杂乱的背景，三条腿，背景人很多，倒着走
```

Gloss, in order: 1 garish colour tone, 2 overexposed, **3 static**, 4 blurry
indistinct detail, 5 subtitles, 6 style, 7 artwork, 8 painting, **9 picture /
screen-image**, **10 motionless**, 11 overall grey cast, 12 worst quality,
13 low quality, 14 JPEG compression residue, 15 ugly, 16 mutilated,
17 extra fingers, 18 badly drawn hands, 19 badly drawn face, 20 deformed,
21 disfigured, 22 malformed limbs, 23 fused fingers, **24 a motionless
picture**, 25 cluttered background, 26 three legs, 27 too many people in the
background, 28 walking backwards.

Diffed term-by-term against our `NEG` (`wan_i2v.py:69-72`): **our list is 24
terms, order preserved, nothing added — and it drops FOUR of theirs, not the
three the comment names.**

| dropped | # | gloss | named in our comment? |
|---|---|---|---|
| 静态 | 3 | static | yes |
| **画面** | **9** | **picture / screen-image / "a frame"** | **NO** |
| 静止 | 10 | motionless | yes |
| 静止不动的画面 | 24 | a motionless picture | yes |

`wan_i2v.py:56-58` says "The official list contains 静态 (static), 静止
(motionless) and 静止不动的画面 (a motionless picture)". **画面 is a fourth,
undocumented deletion.** It sits in the official list at position 9,
immediately after 风格 / 作品 / 画作 (style / artwork / painting) — i.e. inside
the "this output looks like a flat 2D picture rather than a moving scene"
cluster, not the anti-stillness cluster. Suppressing 画面 pushes *away* from
flat-picture-ness. We removed it, undocumented, in the same edit that was
supposed to remove only anti-stillness terms.

**This is a live, cheap suspect for "beat 1 basically doesn't move at all."**
It is a distinct hypothesis from the `SHAKE_NEG` one already flagged at
`wan_i2v.py:78-83`, it costs one sample to test, and it should be tested
separately from `--no-shake-neg` so the two do not confound. Either way the
comment needs correcting to say four terms.

Minor, probably irrelevant, worth knowing: we join with ASCII `", "` where they
join with `，`. Different tokens into UMT5. Untested; low prior.

### 5b. Prompt extension — and the spec it encodes

`--use_prompt_extend` (default **off**, `generate.py:169-173`) runs the prompt
through an LLM before the video model sees it. Two backends:

- `dashscope` (paid Alibaba API, needs `DASH_API_KEY`) — `qwen-plus` for t2v,
  `qwen-vl-max` for i2v (`prompt_extend.py:137-138`). **Not for us: costs
  money, founder-reserved.**
- `local_qwen` (default method, `generate.py:174-179`) — `Qwen2.5-14B-Instruct`
  for text, **`Qwen2.5-VL-7B-Instruct` for image-to-video**
  (`prompt_extend.py:267-268`, `:294`). README:181 also offers
  `Qwen2.5-VL-3B-Instruct`. $0 and local, and the VL model is *shown the
  conditioning image*.

`README.md:164`: "Extending the prompts can effectively enrich the details in
the generated videos, further enhancing the video quality. **Therefore, we
recommend enabling prompt extension.**" Note `README.md:437`: the efficiency
table was measured *without* it.

**The system prompts are the authors' spec for what a Wan i2v prompt should
be** (`wan/utils/system_prompt.py`), and that is the useful part even if we
never run the rewriter. `I2V_A14B_EN_SYS_PROMPT` (`:85-104`), which `ti2v-5B`
also uses for its i2v path (`prompt_extend.py:44-47`), instructs verbatim:

- "rewrite the provided video description prompts based on the images given by
  users, **emphasizing potential dynamic content**" (`:86`)
- "**Focus on dynamic content in the video description and avoid adding static
  scene descriptions. If the user's input already describes elements visible in
  the image, remove those static descriptions.**" (`:91`)
- "If the input is too short, **add reasonable motion-related details** based on
  the image content." (`:89`)
- "**Retain and emphasize descriptions of camera movements**, such as 'the
  camera pans up'…" (`:90`)
- "Limit the rewritten prompt to **100 words or less**." (`:92`)

Their nine worked examples (`:95-103`) are all pure motion, ~10-25 words, e.g.
"A black squirrel focuses on eating, occasionally looking around." and "A woman
wearing a pearl necklace looks to the right and speaks."

Two things follow for us:

1. **The prompt is supposed to describe motion ONLY, with everything already
   visible in the still deleted.** We do this on the AnimeGen path — where
   `wan_i2v.py:412-414` follows AIdeaLab's "a MOTION-only prompt" — and *not*
   on the 5B production path, which sends whatever `motion.yaml` holds. Two
   independent author groups specify the same thing, so this is worth an audit
   of what we actually send per beat.
2. There is a **dedicated empty-prompt path**: `decide_system_prompt` routes
   `len(prompt) == 0` on an i2v task to `I2V_A14B_EMPTY_*_SYS_PROMPT`
   (`prompt_extend.py:91-92`, system prompts at `:107-147`), whose brief is
   "bring the image provided by the user to life through reasonable
   imagination". README:214 shows `--prompt ''` used exactly this way. So
   "hand it the still and let it decide the motion" is a supported mode, not a
   degenerate one. (Note `ti2v-5B` has no `"empty"` key, but
   `decide_system_prompt` returns on the `"ti2v" in task` branch first
   (`:86-90`), so a 5B empty prompt gets the normal i2v system prompt — no
   crash, and the VL model still sees the image.)

### 5c. Motion amplitude control: there is none

`grep -rni "amplitude|motion_scale|motion_strength|motion_bucket"` over
`wan/`, `generate.py` and `README.md` returns **nothing**. Wan 2.2 exposes no
numeric motion knob — no SVD-style `motion_bucket_id`, no amplitude scalar.
The only levers the authors themselves use are:

- **the prompt**, per §5b — and the T2V system prompt is explicit that motion is
  a *prompt* responsibility: rule 4 (`system_prompt.py:17`, `:46`) tells the
  rewriter that "for the actions in the prompt, describe the process of the
  motion in detail; **if there is no action, add an action description**
  (swaying the body, dancing, etc.), and appropriate motion may also be added
  to background elements (clouds drifting, wind blowing the leaves)."
- **the negative prompt**, per §5a — three of its 28 terms exist to push away
  from stillness.
- **`shift`**, which redistributes steps between the high-noise (layout and
  motion) and low-noise (detail) regimes — §1c and §4.

So our two moves on this axis — deleting the anti-stillness negatives and
adding shake suppressors — were edits to the only two levers that exist, made
in the same session, in the same direction. Alibaba's own rule 4 also names
"swaying the body" as a *desirable* addition, which is close to what the
founder called "shaking alot, strangly": the same phenomenon is their target
and our defect. That asymmetry is real and is about our show, not the model —
"camera locked, small true movement" is a narrower ask than Wan's defaults aim
at, and it will not be reached by the negative prompt alone.

---

## 6. Performance: their tricks, and the measured comparison

### 6a. Their published 4090 number, against ours

`README.md:427-438` + `assets/comp_effic.png` (a table image — transcribed
here). Format is total seconds / peak GB, at the settings in `README.md:435`:

| GPU | model | res | 1 GPU | 4 GPU | 8 GPU |
|---|---|---|---|---|---|
| **4090** | **TI2V-5B I2V** | **720P** | **524.8 s / 22.8 GB** | 227.3 / 22.6 | 160.1 / 22.6 |
| 4090 | TI2V-5B T2V | 720P | 534.7 / 22.9 | 231.3 / 22.6 | 157.2 / 22.6 |
| H100 | I2V-A14B | 720P | 1055.9 / 59.7 | 290.4 / 51.6 | 159.0 / 37.0 |
| H100 | I2V-A14B | 480P | 327.8 / 41.0 | 92.4 / 40.8 | 52.9 / 26.1 |
| A100 | I2V-A14B | 720P | 2810.9 / 59.7 | 730.5 / 51.6 | 393.4 / 37.0 |
| H20 | I2V-A14B | 720P | 4054.7 / 59.7 | 1076.9 / 51.6 | 577.0 / 37.0 |

**524.8 s is the "under 9 minutes" claim, and it is 121 frames at 50 steps =
10.50 s/step on a desktop 4090, with `--offload_model True
--convert_model_dtype --t5_cpu`.**

Ours: 8.67 s/step marginal at 704x1280 on the 5090 laptop. The two are not
directly comparable until the frame counts are matched — their step covers
31 latent frames (121 frames), and if ours was measured at our 4.0s / 97-frame
default it covers 25. Token counts are 27280 vs 22000, so scaling ours by
27280/22000 gives **~10.75 s/step — within 3% of a desktop 4090.**

That is worth stating plainly: **on this evidence the 5090 laptop is running at
4090-desktop speed, from a card that should be substantially faster, and their
4090 figure is with full offload while (as far as this document knows) ours is
not.** That is consistent with — and is independent evidence for — the
unresolved WDDM sysmem-fallback paging suspicion already written down at
`wan_i2v.py:325-331`, and it is the strongest single argument for spending a
sample on the diagnosis. Their peak of 22.8 GB against our 23.89 GiB card also
says we are operating with almost no headroom by design, not by accident.

Caveat, so this is not over-read: I did not verify which frame count our
8.67 s/step was measured at, and 720P in their table means 1280x704 landscape
(same pixel count as 704x1280). Confirm the frame count before quoting the 3%.

Also note **Ulysses scales sublinearly even on datacentre interconnect**:
4090 1→4 GPUs is 524.8→227.3 s (2.3x, not 4x) and 1→8 is 3.3x, not 8x. A
second consideration against §3's multi-machine idea, on top of the bandwidth
arithmetic.

### 6b. What their code does that ours does not

- **flash-attn is a hard requirement of the DiT, not an option.**
  `wan/modules/attention.py` defines both `flash_attention()` (FA3 if
  `flash_attn_interface` imports, else FA2, `:88-127`) and a wrapper
  `attention()` that falls back to `torch.nn.functional.
  scaled_dot_product_attention` with a warning that "Padding mask is disabled
  … It can have a significant impact on performance" (`:164-179`).
  **But `wan/modules/model.py:9` imports `flash_attention` directly and calls
  it at `:145` and `:175` — the SDPA fallback is never reached by the DiT.**
  `flash_attn` is an unconditional line in `requirements.txt`, and
  `INSTALL.md:19-33` devotes a section to making it build. `ulysses.py:38` also
  calls `flash_attention` directly. Their 10.5 s/step is a FlashAttention
  number; `README.md:436` notes FA3 specifically for the Hopper rows.
  **We never select an attention backend at all** — we take whatever the
  installed diffusers picks (SDPA by default on most builds). If our 5090 is
  running SDPA against their FA2/FA3, that is a second candidate explanation
  for the speed parity in §6a, and unlike the paging theory it is testable
  without a render (check what the transformer's attention processor resolves
  to, and whether flash-attn is even installed in the video venv).
- **No `torch.compile`, no CUDA-graph, no TF32 or `cudnn.benchmark` setting
  anywhere.** `grep -rn "torch.compile|dynamo|cudnn.benchmark|
  matmul.allow_tf32|set_float32_matmul"` over `wan/` and `generate.py` returns
  nothing. So compile is a *lever neither of us pulls*, not a gap — and it is
  an untried $0 speed idea for a bf16 DiT looping 50 identical steps.
- **`torch.amp.autocast('cuda', dtype=bfloat16)` wraps the whole sample loop
  and the VAE decode** (`textimage2video.py:329-333`, `image2video.py:335-340`)
  — including the decode, at `:608-609` inside the same `with`. We instead run
  the VAE in explicit float32 (`wan_i2v.py:211-212` on the AnimeGen path;
  diffusers' default for `AutoencoderKLWan` elsewhere). That float32 VAE is
  precisely what OOM'd on 2026-08-03 (`wan_i2v.py:94-101`). **Their VAE decode
  runs under bf16 autocast.** Not a free swap — diffusers upcasts the Wan VAE
  deliberately, and a bf16 VAE can band or shift colour — but it is the
  authors' own configuration and it directly addresses our one hard OOM.
- **VAE tiling: they have none, because they chunk over time instead.**
  `wan/modules/vae2_2.py:783-810` encodes in `iter_ = 1 + (t-1)//4` temporal
  chunks and `:812-830` decodes **one latent frame at a time**
  (`iter_ = z.shape[2]`), carrying causal state in `feat_cache`. There is no
  spatial tiling and no `enable_tiling` equivalent. Our `tile_vae()`
  (`wan_i2v.py:88-125`) is therefore an *addition* on top of a VAE that is
  already streaming temporally — which is the right call for our card, and
  worth knowing is not something the authors found necessary.
  The VAE's own internal attention does use
  `F.scaled_dot_product_attention` (`vae2_2.py:267`), not flash-attn.
- **CFG is two sequential forwards per step, never a batch of 2**
  (`textimage2video.py:580-585`, `image2video.py:393-398`), with an
  `empty_cache()` between them under offload. Lower peak VRAM, no throughput
  win. Relevant to reading step timings: **one "step" = two full DiT
  forwards**, so 8.67 s/step is ~4.3 s per forward.

### 6c. Two conditioning details of the 5B path we should know

Not performance, but they are how the model actually receives the still, and
they differ by model:

- **TI2V-5B has no image encoder. It conditions by latent inpainting.**
  The image is VAE-encoded to `z` (`textimage2video.py:512`), and the first
  latent frame is *overwritten with it at every step*:
  `latent = (1. - mask2[0]) * z[0] + mask2[0] * latent` before the loop
  (`:551`) and again after every scheduler step (`:598`). The timestep is also
  **spatially varying** — the conditioned region is handed t=0 while the rest
  gets t: `temp_ts = (mask2[0][0][:, ::2, ::2] * timestep).flatten()`
  (`:573-578`), built from `masks_like([noise], zero=True)`
  (`utils.py:172-199`, which zeroes `[:, 0]`). There is no `y` channel and no
  CLIP.
- **I2V-A14B conditions completely differently**: a 4-channel mask is
  concatenated to a VAE encoding of `[image, zeros(F-1)]` and passed as `y=`
  into the model (`image2video.py:289-296`, `:314-323`) — the classic Wan 2.1
  i2v scheme. So the two models are not interchangeable in how the still binds,
  and a habit tuned on the 5B may not transfer to tomorrow's A14B test.
- **They resize by aspect-preserving LANCZOS + centre crop**, with the output
  size *derived from the image's own aspect ratio* under a max-area budget
  (`best_output_size`, `utils.py:202-225`; used at
  `textimage2video.py:462-474`). We do `Image.open(...).resize((w, h),
  LANCZOS)` (`wan_i2v.py:403`), which **squashes** rather than crops if the
  still is not exactly the target ratio. Harmless while our stills are true
  9:16; a trap the moment one is not.

---

## 7. Summary

### Reference settings table (what the authors run)

| | TI2V-5B (ours) | I2V-A14B (tomorrow) |
|---|---|---|
| steps | **50** | **40** |
| guidance | **5.0** | **3.5** (low), **3.5** (high) |
| shift | **5.0** (3.0 only for 480p) | **5.0** (3.0 only for 480p) |
| solver | unipc (or dpm++) | unipc (or dpm++) |
| frames / fps | **121 @ 24fps** = 5.04s | **81 @ 16fps** = 5.06s |
| resolution | **704x1280 or 1280x704, nothing else** | 720x1280, 1280x720, 480x832, 832x480 |
| boundary | n/a | **0.900** |
| dtype | bf16 params, bf16 autocast | bf16 params, bf16 autocast |
| negative | the 28-term Chinese list, unchanged | same |
| prompt | motion-only, ≤100 words, statics deleted | same |

### Consumer-GPU recipe

- **TI2V-5B:** `--offload_model True --convert_model_dtype --t5_cpu` → their
  stated 24GB / RTX 4090 recipe, measured at 524.8 s and 22.8 GB peak for a
  720P i2v clip. Drop all three only at ≥80GB.
- **I2V-A14B:** **no official 24GB recipe exists.** Their single-GPU command is
  `--offload_model True --convert_model_dtype` and is documented as **80GB**;
  `--t5_cpu` is the only further advice and does not change that. For 24GB they
  point at DiffSynth-Studio's layer-by-layer offload + FP8 — i.e. the fp8
  layerwise-casting approach we already use on the AnimeGen path is the
  sanctioned one. Expect the A14B test to be memory-bound, not step-bound.

### A14B at 4 steps: which expert gets which steps

A single hard threshold, no blending: `high_noise_model` while
`t >= 0.900 * 1000 = 900`, `low_noise_model` below. Guidance switches with it.

- **At the official shift 5.0: timesteps `[999, 937, 833, 624]` → high-noise
  gets steps 1-2, low-noise gets steps 3-4. A clean 2/2 split**, close in
  proportion to the 15/40 of their reference run. A 4-step Lightning run does
  not structurally starve either expert.
- **At the shift 3.0 our code sets: `[999, 899, 749, 499]` → 1/3.** Step 2
  lands at t=899 against a boundary of 900 and flips to the detail expert. The
  layout-and-motion expert would run once in four. Verify diffusers' exact
  `timesteps` and `boundary_ratio` on the render machine before acting, but
  shift 5.0 is the documented value for 720p either way.

### Top 3 things our pipeline does differently from the authors' own code

1. **Steps and shift.** We run **25 steps** against their **50**, and we never
   set **shift** on the 5B path at all (inheriting an unverified value from the
   HF `scheduler_config.json`), while setting **3.0** — their *480p*
   recommendation — on the A14B path we render at 704x1280. Shift is the one
   parameter that decides how much of the trajectory is spent establishing
   motion versus refining detail, which is the exact axis of the open
   "doesn't move at all" question, and it is the only major knob we have never
   measured. Also: our default `--size 480x832` is not on the 5B's supported
   list; only 704x1280 and 1280x704 are.
2. **The prompt contract.** Both Alibaba (`system_prompt.py:91`) and AIdeaLab
   specify a Wan i2v prompt as **motion only, with anything already visible in
   the still deleted, under 100 words**, and Alibaba ship a $0 local
   `Qwen2.5-VL-7B` rewriter to enforce it (off by default; they recommend
   turning it on). We follow this on the AnimeGen path and not on the 5B
   production path. Separately, our `NEG` drops **four** official terms, not
   the three the comment claims — the undocumented fourth is `画面`
   (picture / flat-frame), which sits in the *quality* cluster and pushes away
   from flat-picture-ness. That is a fresh, one-sample suspect for the
   stillness complaint, and it must be tested separately from `--no-shake-neg`.
3. **Attention backend and the speed gap.** Their DiT calls flash-attn
   *directly* — `model.py:9` imports `flash_attention`, not the `attention()`
   wrapper, so the SDPA fallback is dead code for the DiT and `flash_attn` is a
   hard requirement. We select no backend and get whatever diffusers defaults
   to. Their 4090 figure is 10.50 s/step; ours scaled to the same token count
   is ~10.75 s/step — **a 5090 laptop matching a desktop 4090, while theirs is
   fully offloaded and ours is not.** Either the missing flash-attn or the
   already-suspected WDDM sysmem paging (`wan_i2v.py:325-331`) would explain
   it; the attention one is checkable without a render.

Honourable mentions, both cheap: their VAE decode runs under **bf16 autocast**
where ours is float32 (the source of our one hard OOM), and they resize with
**aspect-preserving LANCZOS + centre crop** where we squash to WxH.

### What is NOT worth pursuing

**Splitting one clip across two machines.** FSDP and Ulysses are the only
parallelism present, both NCCL-hardcoded, both single-node in every example.
Ulysses would push ~20 GB of all-to-all per sampling step for our 5B config —
~160 s per step of pure network on gigabit Ethernet against 8.67 s of compute.
And even on datacentre interconnect it only returns 2.3x for 4 GPUs and 3.3x
for 8. One whole clip per machine remains the only sound unit of work.
