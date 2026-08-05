# Quantisation and speed data for Wan 2.2 — public reference points

**Compiled:** 2026-08-04 by research subagent (res-speed) for banyan-city.
**Scope:** open-source community quantisation + speed data, so we can pick a build per
card (24GB RTX 5090 laptop, 12GB RTX 5070 Ti laptop). Licence status is noted inline
but **not adjudicated here** — sibling agent `res-licence` owns that.

Every number is tagged:

- **MEASURED-BY-AUTHOR** — the person publishing it ran it and states the rig.
- **CLAIMED** — asserted without a stated rig, or restated secondhand.
- **SEO-SUSPECT** — appears on a content-farm domain with no author, no rig, and
  numbers that do not reconcile with primary sources. Do not plan against these.

---

## 0. Headline correction: we are not 5-10x off. We are ~1.2x off the official 4090.

This was the reason for the task and it turns out to rest on a bad reference.

The "4090 at FP8 does 60-120s per 4-second 720p clip at FIFTY steps" figure traces to
SEO-farm blogs (`localaimaster.com`, `runaihome.com`, `wan27.org`), and where those
pages attribute it at all they attribute it to the **A14B 14B model**, not TI2V-5B.
It also contradicts the model authors. Discard it.

The primary source is Alibaba's own model card and repo:

> "Without specific optimization, TI2V-5B can generate a 5-second 720P video in
> **under 9 minutes on a single consumer-grade GPU**, ranking among the fastest
> 720P@24fps video generation models."

— [Wan-AI/Wan2.2-TI2V-5B model card](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B)
and [Wan-Video/Wan2.2 README](https://github.com/Wan-Video/Wan2.2/blob/main/README.md).
Consumer-grade GPU = RTX 4090; test flags `--offload_model True --convert_model_dtype
--t5_cpu`. **MEASURED-BY-AUTHOR (model authors).**

The default step count for that recipe is **50**, confirmed from
[`wan/configs/wan_ti2v_5B.py`](https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/wan/configs/wan_ti2v_5B.py):
`sample_steps = 50`, `sample_guide_scale = 5.0`, `sample_shift = 5.0`, `frame_num = 121`.

Normalise both to seconds per denoising step:

| Rig | Recipe | s/step | Source |
|---|---|---|---|
| RTX 4090 24GB (official) | TI2V-5B, 5s 720P, 50 steps, offload+t5_cpu | **~10.8** | official, MEASURED-BY-AUTHOR |
| **our RTX 5090 laptop 24GB** | TI2V-5B, 704x1280, bf16, model_cpu_offload | **13.4** | ours, measured |

We are **1.24x slower per step than the official 4090 reference**, on a laptop part
that also drives a desktop. That is unremarkable. And we already run 14 steps where
the official recipe runs 50 — at 50 steps we would be at ~670s (11.2 min) against
their ~540s (9 min). **The pipeline is roughly where it should be. There is no
mystery 10x to find.** See §4 for the one place a real 10x hides, and note that our
symptoms only partly match it.

The remaining headroom is real but it is ordinary engineering, not a bug:
step reduction (§3, up to 3.5x), attention + compile (§2, ~1.5-2x), and getting off
`enable_model_cpu_offload` if the memory budget allows (§2).

---

## 1. Quantised builds

### 1a. Wan 2.2 TI2V-5B — GGUF (the 5B we already use)

[QuantStack/Wan2.2-TI2V-5B-GGUF](https://huggingface.co/QuantStack/Wan2.2-TI2V-5B-GGUF)
— direct conversion of `Wan-AI/Wan2.2-TI2V-5B`. ~36.5k downloads/month.
Consumed via the ComfyUI-GGUF custom node (`ComfyUI/models/unet`), **not** diffusers.

| Quant | Size | Notes |
|---|---|---|
| Q2_K | 1.85 GB | too degraded to plan around |
| Q3_K_S / Q3_K_M | 2.29 / 2.55 GB | |
| Q4_0 / Q4_1 / Q4_K_S / **Q4_K_M** | 3.03 / 3.25 / 3.12 / **3.43 GB** | Q4_K_M = usual 12GB pick |
| Q5_0 / Q5_1 / Q5_K_S / **Q5_K_M** | 3.64 / 3.87 / 3.56 / **3.81 GB** | |
| Q6_K | 4.21 GB | |
| **Q8_0** | **5.4 GB** | near-lossless reference quant |

Licence: card tag says **apache-2.0**, and the card adds "Since this is a quantized
model, all original licensing terms and usage restrictions remain in effect."
**This one is not laundering** — the base `Wan-AI/Wan2.2-TI2V-5B` is itself
**Apache 2.0**, so the tag matches the base. (The base card does carry a
use-conduct paragraph: no unlawful content, no harm to individuals or groups, no
targeting vulnerable populations. Not a commercial restriction. `res-licence` to confirm.)

### 1b. fp8 scaled checkpoints

| Repo | File | Size | Licence tag |
|---|---|---|---|
| [Kijai/WanVideo_comfy_fp8_scaled](https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled) | `TI2V/Wan2_2-TI2V-5B_fp8_e4m3fn_scaled_KJ.safetensors` | **5.28 GB** | apache-2.0 |
| [Comfy-Org/Wan_2.2_ComfyUI_Repackaged](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/tree/main/split_files/diffusion_models) | `wan2.2_ti2v_5B_fp16.safetensors` (+ fp8_scaled for the 14B pair) | fp16 ~10GB | — |

Kijai's fp8 scaling method is ported from Tencent's HunyuanVideo work; his card
reports fp8-scaled beating plain fp16 casting on quality-per-VRAM.
Note his repo card describes itself against a `Wan2.1-VACE-1.3B` base in places —
the repo is a grab-bag of many Wan variants, so read the per-file provenance,
not the card header. Licence tag apache-2.0, consistent with Wan's base licence.

Also relevant for us: the text encoder.
`split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors` in the Comfy-Org
repack is the fp8 UMT5 — this is what lets you stop paying for `--t5_cpu`.

### 1c. NF4 / bitsandbytes

Supported in principle via `BitsAndBytesConfig(load_in_4bit=True,
bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)` —
[diffusers bitsandbytes docs](https://huggingface.co/docs/diffusers/en/quantization/bitsandbytes).
No published NF4 Wan 2.2 TI2V-5B checkpoint found. And there is a live correctness
warning for exactly this combination:
[diffusers #11006 — "Broken video output with Wan 2.1 I2V pipeline + quantized transformer"](https://github.com/huggingface/diffusers/issues/11006).
**Do not put NF4 on the critical path.** GGUF and fp8 are the trodden routes.

### 1d. 4-step distilled TI2V-5B — the interesting one, see §3

- [quanhaol/Wan2.2-TI2V-5B-Turbo](https://huggingface.co/quanhaol/Wan2.2-TI2V-5B-Turbo) (weights) / [GitHub](https://github.com/quanhaol/Wan2.2-TI2V-5B-Turbo)
- [yetter-ai/Wan2.2-TI2V-5B-Turbo-Diffusers](https://huggingface.co/yetter-ai/Wan2.2-TI2V-5B-Turbo-Diffusers) — **diffusers format**, F32/BF16, ~483 downloads/month. **No licence declared on the card** — flag for `res-licence`.
- [hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF](https://huggingface.co/hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF) — GGUF of the Turbo: Q2_K 1.86GB, Q3_K 2.3-2.79GB, Q4_K 3.03-3.44GB, Q5_K 3.56-3.82GB, Q6_K 4.22GB, Q8_0 5.4GB. Licence tag apache-2.0.

---

## 2. Measured speed numbers

Sorted by usefulness. Anything without resolution AND steps AND card was discarded.

| Model | Card | Res / frames | Steps | Time | s/step | Precision + opts | Tag |
|---|---|---|---|---|---|---|---|
| TI2V-5B | RTX 4090 24GB | 720P / 5s (121f) | 50 | <540s | ~10.8 | bf16, offload_model, t5_cpu | **MEASURED-BY-AUTHOR** ([official](https://github.com/Wan-Video/Wan2.2/blob/main/README.md)) |
| **TI2V-5B (ours)** | **RTX 5090 laptop 24GB** | **704x1280 / 3-4s** | **14** | **188s** | **13.4** | **bf16, enable_model_cpu_offload** | **ours** |
| TI2V-5B (ours) | RTX 5090 laptop 24GB | 704x1280 | 20 | 240s | 12.0 | same | ours |
| Wan2.2 (size n/s) | 8x H100 | n/s | 40 | 187s → 60s | 4.67 → **1.51** | FA3 baseline; +batched fwd, +time-emb, +SageAttention, +TeaCache | **MEASURED-BY-AUTHOR** ([Voltage Park](https://www.voltagepark.com/blog/accelerating-wan2-2-from-4-67s-to-1-5s-per-denoising-step-through-targeted-optimizations)) |
| Wan 2.1 I2V 720P (14B) | RTX 4090 | 720P / 64f | 20 | 1002s → 516s | 50.1 → 25.8 | +SageAttention +TeaCache +torch.compile | MEASURED-BY-AUTHOR, vendor page ([InstaSD](https://www.instasd.com/workflows/wan-2-1-i2v-720p-sageattention-teacache-torch-compile)) |
| Wan2.2 Q8_0 GGUF | 16GB card (model n/s) | n/s | n/s | — | ~22 | GGUF Q8 | CLAIMED (secondhand, rig underspecified) |
| A14B | RTX 4090 | 720P / 5s | 50 (default) | ~9 min | ~10.8 | — | CLAIMED — **and suspect**: identical to the official *5B* figure, likely a farm blog conflating the two |
| TI2V-5B | RTX 4090 | **480P** / 5s | 50 | ~4 min | ~4.8 | unoptimised | CLAIMED (restated from official docs) |
| "4090 fp8, T5 on GPU" | RTX 4090 | 720P / 4s | 50 | 60-120s | 1.2-2.4 | fp8 | **SEO-SUSPECT — discard.** This is the figure that started the panic. Implies 4-9x faster per step than the model authors' own 4090 number. |

### What the optimisation stack is actually worth

The two independent MEASURED rows agree on the shape:

- **SageAttention alone: ~10%** (Voltage Park, 3.40s → 3.10s/step). Modest.
- **TeaCache: ~50%** (Voltage Park, 3.10s → 1.51s/step) — the single biggest lever
  in that stack, but it is a *cache*, and see the quality cost in §3.
- **Sage + TeaCache + torch.compile together: 1.94x** (InstaSD, 4090, 1002s → 516s).

So ~1.5-2x from the attention/compile/cache layer, not 10x.

### Offloading is a real tax and we are paying it

We use `enable_model_cpu_offload`. Community and maintainer reports on the diffusers
offload family:

- `enable_sequential_cpu_offload` — [diffusers #2266, ">3x slowdown"](https://github.com/huggingface/diffusers/issues/2266); another report 6 it/s → 2 it/s. (We are not using this one, but it bounds how bad offload can get.)
- `enable_model_cpu_offload` moves whole modules to CPU when idle — cheaper than sequential, but still a per-step PCIe round trip for the transformer.
- Newer alternative: **group offloading** with `use_stream=True`
  ([diffusers #10503](https://github.com/huggingface/diffusers/pull/10503),
  [speed-memory-optims docs](https://huggingface.co/docs/diffusers/en/optimization/speed-memory-optims)),
  which overlaps transfer with compute. Maintainer note: with `use_stream=False` it is
  *slower* than blockswap. This is the upgrade path from where we are.

Our peak is **22.9GB for a 5B model** whose bf16 weights are only ~10GB (fp8: 5.28GB).
So **activations, not weights, dominate** — 121 frames at 704x1280 is a very large
latent. Two consequences: (a) fp8/GGUF weights buy less headroom than the file sizes
suggest, and (b) 12GB cannot hold this shape at all without spilling.

---

## 3. Step reduction — the biggest single win, and the Lightning question resolved

### The Lightning LoRAs do NOT support TI2V-5B. Resolve our repo note accordingly.

[lightx2v/Wan2.2-Lightning](https://huggingface.co/lightx2v/Wan2.2-Lightning) /
[ModelTC/Wan2.2-Lightning](https://github.com/ModelTC/Wan2.2-Lightning) ships:

- Wan2.2-**T2V-A14B** — V1 and V1.1, 4 steps
- Wan2.2-**I2V-A14B** — V1, 4 steps
- Wan2.2-**TI2V-5B** — **on the Todo list only. Never released.**

And from the maintainers in
[discussions/1 "wan2.2 5B TI2V"](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/1):
they trained on TI2V-5B "for a while but didn't get good results."
So: not merely unreleased, actively attempted and abandoned. Claimed "x20 speed-up"
at 4 steps without the CFG trick applies to the A14B models.

**Licence, resolving our repo's "metadata says apache-2.0 but ships none" note:** the
card now declares apache-2.0 *in prose* — a "License Agreement" section reading "The
models in this repository are licensed under the Apache 2.0 License" — and references
a `LICENSE.txt`. So the note is stale on the "ships none" point. Whether that file is
actually present and whether Apache-2.0 is theirs to grant over a distilled Wan
derivative is `res-licence`'s call, not mine — though note the Wan base is itself
Apache 2.0, which makes this far less fraught than the usual laundering case.

Moot for us regardless, unless we move to A14B.

### What actually exists for TI2V-5B: Wan2.2-TI2V-5B-Turbo

[quanhaol/Wan2.2-TI2V-5B-Turbo](https://github.com/quanhaol/Wan2.2-TI2V-5B-Turbo) —
"the first open-source repository of the distilled I2V version of Wan2.2-TI2V-5B."

- Method: **Self-Forcing** framework, step + CFG distillation, DMD in the training scripts.
- **4 steps, no CFG trick.** 121 frames, 24fps, **1280x704 — exactly our shape.**
- Trained 4,000 iterations, <48h, 16x A100.
- Quality: demo videos only. **No quantitative comparison against the base model
  published.** No measured inference speed with a GPU named. So the 3.5x is arithmetic
  from step count, not someone's stopwatch.
- Diffusers path exists: [yetter-ai/Wan2.2-TI2V-5B-Turbo-Diffusers](https://huggingface.co/yetter-ai/Wan2.2-TI2V-5B-Turbo-Diffusers) — `WanImageToVideoPipeline`, **4 steps, guidance_scale=1.0, UniPCMultistepScheduler with flow_shift=5.0**. This drops into our existing diffusers code. **No licence declared on that card** — flag.
- GGUF path: [hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF](https://huggingface.co/hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF) (ComfyUI only).
- Also: [Civitai "Wan Damme" — Rapid WAN 2.2 5B 4-step fp8 Turbo T2V/I2V](https://civitai.com/models/1995164/wan-damme-rapid-wan-22-5b-4-steps-checkpoint-t2vi2v). Civitai licence terms are per-model and often non-commercial — flag hard.

**14 steps → 4 steps is 3.5x, and it is the only change here that costs no quality
by caching.** Distillation moves the model; caching skips work within a fixed model.
For us, where the founder's rejection mode is *"literally just frozen frames"*, note
that both step reduction and caching are exactly the kind of change that can flatten
motion. This is a ONE-SAMPLE-BEFORE-ANY-BATCH candidate if anything ever was.

### Caching alternatives (fixed model, no retraining)

| Method | Reported | Quality cost | Tag |
|---|---|---|---|
| **TeaCache** | 1.5-2x+ | On Wan2.1-1.3B, TeaCache-fast: **1.98x speedup, PSNR 22.1dB, LPIPS 0.173, SSIM 0.777, -3.74% VBench-2.0**. Practical threshold: `rel_l1_thresh` ~0.2 for Wan; above that detail loss sets in. | MEASURED (paper-sourced); [ComfyUI-TeaCache](https://github.com/welltop-cn/ComfyUI-TeaCache) |
| DeepCache | — | No Wan-specific measured data found. Designed for UNet architectures; Wan is a DiT. Likely not applicable. | — |
| MagCache | magnitude-aware cache, successor claim to TeaCache | [arXiv 2506.09045](https://arxiv.org/pdf/2506.09045) | CLAIMED |
| CausVid / Self-Forcing / Causal Forcing++ | 4-step, and 1-2 step variants | [thu-ml/Causal-Forcing (ICML 2026)](https://github.com/thu-ml/Causal-Forcing); [CausVid distilled Wan 2.1 collection](https://huggingface.co/collections/linoyts/causvid-distilled-wan-21). **All Wan 2.1**, not 2.2. Causal Forcing++ 2-step reports best VBench total among the family. | MEASURED (papers) |

TeaCache's -3.74% VBench and PSNR 22.1dB is the honest picture: real 2x, real
visible cost. Given our anime-style problems it is second priority behind Turbo.

---

## 4. The Windows paging question

**Confirmed, and NVIDIA's own framing is that it trades speed for not crashing.**

Primary source: [NVIDIA — System Memory Fallback for Stable Diffusion](https://nvidia.custhelp.com/app/answers/detail/a_id/5490)
(403s to automated fetch; content confirmed via search indexing and the coverage below).

- **Driver 536.40** introduced the fallback: applications use shared system memory
  when VRAM is exhausted, "preventing crashes by allowing applications to run at
  lower speeds."
- **Driver 546.01+** added the setting to disable it.
- NVIDIA's own example: Stable Diffusion needing ~6GB on a 6GB card invokes the
  mechanism and gets slower.
- Coverage: [VideoCardz](https://videocardz.com/newz/nvidia-introduces-system-memory-fallback-feature-for-stable-diffusion) (402 to automated fetch).

**Community confirmation of exactly the silent-slowdown-not-OOM symptom:**

> "The speed quickly becomes slow, **approximately 10 times slower**, which is bad."

— [AUTOMATIC1111/stable-diffusion-webui discussion #14077](https://github.com/AUTOMATIC1111/stable-diffusion-webui/discussions/14077),
whose author explains the mechanism as RAM being allocated instead of VRAM for tensor
storage. **MEASURED-BY-AUTHOR.** Also
[oobabooga/textgen #4484](https://github.com/oobabooga/textgen/discussions/4484)
and [NVIDIA dev forums on VRAM offload](https://forums.developer.nvidia.com/t/driver-support-level-for-vram-offload-to-system-ram/258809).

**How to change it:** NVIDIA Control Panel → Manage 3D Settings →
**CUDA - Sysmem Fallback Policy** → set to **"Prefer No Sysmem Fallback"**
(alternative: "Driver Default"). Settable globally or per-application under the
Program Settings tab — per-application, pointed at our python.exe, is the right move
so the desktop keeps its safety net. Requires driver 546.01+. Consequence: we will
get hard OOM instead of slow runs. **That is what we want** — it converts an
invisible tax into a visible error.

### Honest read for our case

The 10x figure is real but it describes a *fully* spilling workload. Ours is at
22.9/25.7GB — spilling somewhat, not catastrophically — and our measured 13.4s/step
is only 1.24x off the official 4090. If we were paging 10x we would be at ~100s/step.
So: worth flipping the switch (it is free, and it makes the problem legible), but
**do not expect it to be the 10x.** Expect it to either produce a modest gain or turn
one configuration into a clean OOM that tells us where the real ceiling is.

One more Blackwell-specific hazard, and it is a primary source on nearly our
hardware: [Comfy-Org/ComfyUI #11775](https://github.com/Comfy-Org/ComfyUI/issues/11775)
— **RTX 5070 (12GB, Blackwell), driver 581.57, Windows 11, torch 2.7.1+cu128**,
Wan2.2 GGUF Q4/Q8: cumulative **host** RAM leak, 20-30GB+ after 2-3 runs at
1280x720/81f, never freed, eventually OOM. VRAM frees correctly; system RAM does not.
"Tried to unpin tensor not pinned by ComfyUI" warnings on unload. Only a reboot
recovers it. Directly relevant to the 12GB card and to any long batch. Partial
workaround: manual memory-cleanup nodes; does not eliminate it.

**Note on cu128 vs cu130:** one source ([wan27.org](https://wan27.org/blog/wan-2-2-gguf-guide),
**SEO-SUSPECT**) claims cu128 "underperforms on Blackwell" and to prefer cu130 plus
`--disable-async-offload` for sm_120 instability. I could not corroborate the
underperformance claim from any primary source, and the PyTorch threads I found on
sm_120 are mostly stale early-2025 complaints from before stable cu128 shipped
sm_120 support ([pytorch #164342](https://github.com/pytorch/pytorch/issues/164342)).
**Treat cu130 as unverified.** cu128 stable is correct for sm_120; the ComfyUI issue
above is on cu128 and is a leak, not a throughput deficit.

---

## 5. Recommended builds

Both are Apache-2.0-lineage (Wan base is Apache 2.0), so neither is licence-blocked
for commercial publication of output on current evidence — `res-licence` confirms.
The one flag: the diffusers Turbo conversion declares no licence on its card.

### 24GB (RTX 5090 laptop) — ship-safe fastest

1. **`yetter-ai/Wan2.2-TI2V-5B-Turbo-Diffusers`, 4 steps, guidance_scale=1.0,
   UniPCMultistepScheduler flow_shift=5.0.** Drops into our existing diffusers code.
   14 → 4 steps = **3.5x**, projected **188s → ~54s** sample, ~248s → **~110s** per beat.
2. Set **CUDA - Sysmem Fallback Policy = Prefer No Sysmem Fallback** on python.exe.
   Free, and converts invisible paging into a legible OOM.
3. fp8 weights (`Wan2_2-TI2V-5B_fp8_e4m3fn_scaled_KJ.safetensors`, 5.28GB) + fp8 UMT5,
   then **try dropping `enable_model_cpu_offload` entirely**; if it OOMs, move to
   group offloading with `use_stream=True` rather than back to model offload.
4. Only then SageAttention + torch.compile (~1.5-2x, measured). TeaCache last — it is
   the one with published quality loss.

### 12GB (RTX 5070 Ti laptop)

`Wan2.2-TI2V-5B-Turbo-GGUF` **Q4_K_M (3.44GB)**, or Q5_K_M (3.82GB) if it fits —
but GGUF means the **ComfyUI** path, not diffusers, which is a second pipeline to
maintain. Text encoder on CPU. Given activations dominate at 704x1280x121, expect
this card to need reduced frame count or resolution regardless of quant, and expect
ComfyUI #11775's host-RAM leak. **My read: this card is not a 704x1280/121f machine.**
Use it for stills, T1/T2, or shorter/lower-res drafts, and keep 704x1280 renders on
the 5090.

---

## 6. Caveats

- The Turbo 3.5x is **arithmetic from step count**, not anyone's measurement. Nobody
  has published a stopwatch number for TI2V-5B-Turbo on any card.
- Nobody has published a quality comparison of Turbo vs base TI2V-5B either. Demos only.
- Step reduction and caching both plausibly flatten motion, which is our known
  failure mode. ONE SAMPLE, one beat, founder screens it, before any batch.
- No credible measured RTX 5090 (desktop or laptop) Wan 2.2 number found anywhere.
  Our 13.4s/step may be the best public 5090 datapoint that exists. Worth publishing.
