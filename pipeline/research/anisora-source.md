# Index-anisora (bilibili) — source read

**Status:** complete, 2026-08-04. Read from the GitHub repo `bilibili/Index-anisora` at `main`
(verified official, see Identity below; shallow clone, last push 2026-07-16). Citations are
`repo-relative-path:line`. **Nothing from the repo was executed** — source read only. The one
computation in this document (the timestep table in §4) is my own arithmetic on their documented
formula, and is labelled as such.

All six questions answered: §1 licence, §2 compatibility + recipe + 8-step verification,
§3 conditioning, §4 VRAM/RAM, §5 motion, §6 negative prompt and prompt conventions.

**Scope of the question:** V3.2 as an anime-native I2V candidate for the sapling series —
detailed cinematic 2D anime, image-to-video from approved stills, 704x1280 vertical, on a
24GB RTX 5090 / 64GB RAM Windows box, driven by our own diffusers pipeline (`wan_i2v.py`
A14B path).

---

## Identity — is this the official repo?

Yes. `https://api.github.com/repos/bilibili/Index-anisora`: `full_name: bilibili/Index-anisora`,
`fork: false`, 2497 stars, last push 2026-07-16, GitHub licence detection `apache-2.0`.
The repo's own README asserts exclusivity:

> **This github project is the only official homepage of the Anisora project. Any websites
> not listed on the official homepage are not affiliated with the project team.**
> — `README.md:36`

`README.md:6` links out to exactly the HF org we were pointed at (`huggingface.co/IndexTeam/Index-anisora`)
and to ModelScope `bilibili-index`, so the GitHub repo and the HF weights repo are the same project.

---

## 1. LICENCE — the answer is NOT plain Apache-2.0

The root `LICENSE` is **214 lines: the stock Apache License 2.0 text at `LICENSE:1-201`
(including its APPENDIX boilerplate at `:178-201`), and then an appended "Model License
Agreement" at `LICENSE:203-214` that adds restrictions.** GitHub's licence detector reports
"apache-2.0" because it pattern-matches the Apache body and does not see the addendum past it.
This matters for a publishing decision.

The appended block, verbatim, `LICENSE:203-213`:

> `[Model License Agreement], Based on [Apache 2.0] License with Additional Restrictions:`
> `User Notice: Should you undertake fine-tuning/retraining or derivative development of this model, you must additionally comply with:`
> 1. `Usage Restrictions: The retrained model shall not be used for purposes violating laws or regulatory requirements of the output/usage jurisdiction (including but not limited to generating false information, discriminatory content, privacy infringement, etc.).`
> 2. `Output Compliance: For retrained models with generative capabilities, you must ensure all outputs comply with legal and regulatory requirements of the output/usage jurisdiction (including but not limited to false information, discriminatory content, or privacy violations).`
> 3. `Retraining Obligations: When retraining this model, you must independently ensure: (a) Training data contains no illegal or infringing content; (b) Retrained models won't be deployed in high-risk automated decision-making scenarios (e.g., credit assessment, employment evaluation) without passing compliance audits; (c) No circumvention of regulatory or review mechanisms in output/usage jurisdictions.`
> 4. `Liability: You assume full responsibility for all activities involving this model, including retraining and derivative works. Should your actions result in third-party claims, administrative penalties, or other losses to our company, you shall indemnify all damages (including legal fees, litigation costs, compensation, fines) and take necessary measures to eliminate negative impacts.`
> 5. `Downstream Compliance: You must ensure downstream users of derivative works comply with these terms through binding agreements. You bear liability for downstream violations.`
> 6. `Attribution: All copies of retrained models must retain this original copyright notice and restrictive clauses.`

**Reading of it for our use:**

- Every added clause is scoped by its own preamble to **fine-tuning / retraining / derivative
  development of the model**. Clauses 1, 2, 3 and 6 all say "retrained model" or "when retraining".
  Plain **inference** — feeding our own approved stills through the released weights and
  publishing the resulting clips — is not what these clauses reach. For our use (inference only,
  no fine-tune) the effective terms are Apache-2.0.
- Clause 4 (liability/indemnity) is *not* scoped to retraining in its own text — "all activities
  involving this model". That is broader than Apache-2.0's warranty disclaimer and is a term a
  publisher should be aware of, though it is an indemnity, not a use restriction.
- **It is not an OSI-clean Apache-2.0 grant.** Calling the model "Apache-2.0" in our provenance
  would be inaccurate. Correct provenance string is something like
  "Apache-2.0 plus bilibili Model License Agreement additional restrictions".

**Does it cure the HF "apache-2.0 tag with no licence text" gap?** Partly, and not in the
direction hoped for.

- It **does** supply the missing licence text: the HF repo carries an `apache-2.0` metadata
  tag with no licence body, and the GitHub repo of the same project carries a real licence
  file. The vet gate's "unverifiable" is resolvable — there IS an authoritative licence document.
- It **does not** confirm the HF tag. The authoritative text is Apache-2.0 **+ restrictions**,
  so the bare `apache-2.0` tag on the HF weights repo is incomplete rather than merely
  undocumented.
- **Does it cover weights or only code?** The addendum is explicitly about "this model" and
  "retrained models" — so this file is the document that governs the **weights**, not just the
  code. That is the useful finding: the licence file is the model licence. Corroborating, the
  README announces weight releases as licence events: `README.md:28` "Anisora V2 weights are now
  licensed under Apache 2.0", `README.md:26` "Anisora V3 weights are now licensed under Apache
  2.0 and publicly available". Note V3.2's own release note (`README.md:24`) does **not** repeat
  a licence statement, so V3.2 weights inherit the repo-level file rather than having their own.
- Caveat worth carrying: the V3.2 weights are a fine-tune of **Alibaba's Wan2.2-A14B**, whose own
  licence therefore also applies upstream. The vendored code files all carry
  `# Copyright 2024-2025 The Alibaba Wan Team Authors. All rights reserved.`
  (e.g. `anisoraV3.2/wan/image2video.py:1`, `anisoraV3.2/wan/configs/wan_i2v_A14B.py:1`).

Per-directory licence files also exist (`anisoraV1_train_gpu/MODEL_LICENSE`,
`anisoraV2_npu/LICENSE`, `anisora_rl/MODEL_LICENSE`, and vendored third-party ones under
`reward/character/samurai/`, `sat/`, `lpips/`) — those are V1/V2/RL-era and third-party
components, not V3.2.

---

## 2. V3.2 inference — architecture and drop-in compatibility

### It is Wan2.2-I2V-A14B, unmodified architecture

`anisoraV3.2/wan/configs/wan_i2v_A14B.py` is byte-for-byte the Alibaba stock config —
including the Alibaba copyright header at line 1:

```
i2v_A14B.t5_checkpoint  = 'models_t5_umt5-xxl-enc-bf16.pth'   # :12
i2v_A14B.t5_tokenizer   = 'google/umt5-xxl'                    # :13
i2v_A14B.vae_checkpoint = 'Wan2.1_VAE.pth'                     # :16
i2v_A14B.vae_stride     = (4, 8, 8)                            # :17
i2v_A14B.patch_size     = (1, 2, 2)                            # :20
i2v_A14B.dim            = 5120                                 # :21
i2v_A14B.ffn_dim        = 13824                                # :22
i2v_A14B.freq_dim       = 256                                  # :23
i2v_A14B.num_heads      = 40                                   # :24
i2v_A14B.num_layers     = 40                                   # :25
i2v_A14B.qk_norm        = True                                 # :27
i2v_A14B.cross_attn_norm= True                                 # :28
i2v_A14B.low_noise_checkpoint  = 'low_noise_model'             # :30
i2v_A14B.high_noise_checkpoint = 'high_noise_model'            # :31
```

Two-expert MoE-by-timestep exactly as Wan2.2: `boundary = 0.900`
(`anisoraV3.2/wan/configs/wan_i2v_A14B.py:36`), high-noise expert for `t >= 0.9*1000`,
low-noise below (`anisoraV3.2/wan/image2video.py:195-200`, `:370`). VAE is the **Wan2.1**
VAE (`Wan2_1_VAE`, imported at `anisoraV3.2/wan/image2video.py:24`, instantiated `:101-103`) —
16-channel latents, 4x temporal stride — matching official Wan2.2-I2V-A14B. No CLIP image
encoder anywhere in the V3.2 tree (there is no `wan/modules/clip.py` under `anisoraV3.2/`,
unlike `anisoraV3/wan/modules/clip.py` which was the Wan2.1-era build). That too matches
Wan2.2 I2V.

**Verdict on our A14B path: the weights are drop-in.** Same shapes, same T5 (umt5-xxl,
`text_len=512`, `anisoraV3.2/wan/configs/shared_config.py:9-11`), same VAE, same dual-expert
layout with the same 0.900 boundary. Nothing in the config or module list departs from stock
Wan2.2-I2V-A14B.

### Their conditioning code IS modified — but reduces to stock for our case

See §3. Short version: for a single first-frame still their `y` tensor is constructed
identically to official Wan2.2 I2V, so `WanImageToVideoPipeline` semantics hold. Their
extra capability (multiple anchor frames at arbitrary temporal positions) is a *calling
convention* on the same tensor, not an architecture change.

### Reference recipe (their own README command)

`anisoraV3.2/README.md:24-36`:

| setting | value |
|---|---|
| task | `i2v-A14B` |
| size | `1280*720` |
| `--sample_steps` | **8** |
| `--sample_shift` | **5** |
| `--sample_guide_scale` | **1** (i.e. CFG off) |
| `--base_seed` | 4096 |
| solver | `unipc` (default, `anisoraV3.2/generate_txt_new.py:195-199`) |
| fps | **16** (`shared_config.py:18`) |
| frame_num | 81 default (`shared_config.py:20`); README:120-122 "81 frames equals about 5 seconds, must satisfy F=8x+1" |

Note the config file still carries the **stock Alibaba defaults** — `sample_steps = 40`,
`sample_guide_scale = (3.5, 3.5)`, `sample_shift = 5.0`
(`anisoraV3.2/wan/configs/wan_i2v_A14B.py:34-37`). The 8-step/CFG-1 recipe exists **only in
the README command line**, overriding those defaults via argparse
(`generate_txt_new.py:58-66` fall back to cfg only when the flag is absent). So anyone running
the config defaults gets 40 steps at CFG 3.5.

### Resolution buckets — 704x1280 is present but gated

`anisoraV3.2/wan/configs/__init__.py:17-33` — `SIZE_CONFIGS` and `MAX_AREA_CONFIGS` both
include `'704*1280'` and `'1280*704'` (lines 22-23, 31-32), our exact target.

But `SUPPORTED_SIZES` at `:35-39` allows for `i2v-A14B` only
`('720*1280', '1280*720', '480*832', '832*480')` — **704*1280 is listed only for `ti2v-5B`**
(line 38). And `generate_txt_new.py:73-75` asserts `args.size in SUPPORTED_SIZES[args.task]`.
So their CLI refuses `--task i2v-A14B --size 704*1280` even though the area config exists.

This is cosmetic for us. For I2V, `size` is used **only** to look up `max_area`
(`generate_txt_new.py:441` passes `max_area=MAX_AREA_CONFIGS[args.size]`); the actual output
h/w are derived from the **input image's aspect ratio** and that area budget
(`anisoraV3.2/wan/image2video.py:275-284`):

```python
h, w = img.shape[1:]
aspect_ratio = h / w
lat_h = round(np.sqrt(max_area * aspect_ratio) // vae_stride[1] // patch_size[1] * patch_size[1])
lat_w = round(np.sqrt(max_area / aspect_ratio) // vae_stride[2] // patch_size[2] * patch_size[2])
h = lat_h * vae_stride[1];  w = lat_w * vae_stride[2]
```

Feed a 704x1280 still with `max_area = 704*1280` and you get 704x1280 out. In our own
pipeline the `SUPPORTED_SIZES` assert never runs.

### The 8-step claim — verified, and it is native, not a LoRA

Claim: `README.md:24` (2025/09/23) — "We have released V3.2 weights, which is trained on the
stronger wan2.2 model and **can reduce the number of inference steps to 8**".

What the code shows:

- **No LoRA anywhere in the V3.2 inference path.** Weights load as full checkpoints via
  `WanModel.from_pretrained(checkpoint_dir, subfolder=checkpoint_dir_lowname/highname)`
  (`anisoraV3.2/wan/image2video.py:106-107`, `:115-116`). There is no adapter load, no
  `peft`/`lora` import, no scale/alpha argument. So the few-step capability is **baked into the
  released weights** — a native distill/fine-tune, consistent with the 126GB two-expert
  download rather than a small side file.
- **CFG scale 1 corroborates it.** Their command passes `--sample_guide_scale 1`. A model that
  produces good output with guidance disabled is the signature of a guidance-distilled model.
  Their V2 notes describe the same lineage: "Distillation-accelerated inference without quality
  compromise, faster and cheaper" (`README.md:116`).
- Speed claim for the previous generation, for scale: "The V3 model can generate 5 sec 360p
  video shot within 8 sec" (`README.md:26`).

**The claim survives reading the code**, with one important asterisk about how they spend the
8 steps — see the CFG waste finding in §4.

### The whole V3.2 code tree is vendored Alibaba Wan — zero anisora source

Checked every `.py` under `anisoraV3.2/`: all of them are stock Wan files. 36 of 40 carry
`# Copyright 2024-2025 The Alibaba Wan Team Authors. All rights reserved.` on line 1; the four
that do not (`wan/utils/fm_solvers.py`, `wan/utils/fm_solvers_unipc.py`, `wan/utils/qwen_vl_utils.py`,
`wan/modules/t5.py`) are the HF/diffusers-derived files that are unheadered in official Wan too.
`grep -rni anisora anisoraV3.2/**/*.py` returns **nothing**.

The only substantive anisora edit in the V3.2 inference path is the conditioning-mask rewrite in
`anisoraV3.2/wan/image2video.py:302-350` (§3) plus the `generate()` signature change to accept
image/position lists. **Everything that makes AniSora anime-good lives in the weights, not the code.**

---

## 3. Image-to-video conditioning — how faithful, and why anime

### The mask rewrite, and why it reduces to stock for a single first frame

They replaced Wan's first-frame-only mask with an arbitrary-position multi-anchor mask.
Wan's original two lines are left in as a comment at `anisoraV3.2/wan/image2video.py:302-303`:

```python
# msk = torch.ones(1, F, lat_h, lat_w, device=self.device)
# msk[:, 1:] = 0
```

and replaced by `anisoraV3.2/wan/image2video.py:305-311`:

```python
msk = torch.zeros(1, F, lat_h, lat_w, device=self.device)
id_list = []
for iii in range(len(Tid_list)):
    id_ = int((F-1)*Tid_list[iii])
    id_ = round((id_)/8)*8        # anchor frames snap to multiples of 8
    msk[:, id_:id_+1] = 1
    id_list.append(id_)
```

Then the identical Wan reshape at `:313-318`, and the latent side at `:336-340` (replacing Wan's
`concat([img, zeros(F-1)])`, still present commented at `:342-350`):

```python
vae_in = torch.zeros(3, F, h, w)
for iii in range(len(id_list)):
    im_in = torch.nn.functional.interpolate(Img_list_new[iii][None].cpu(), size=(h, w), mode='bicubic').transpose(0, 1)
    vae_in[:, id_list[iii]] = im_in[:, 0]
y = self.vae.encode([vae_in.to(self.device)])[0]
y = torch.concat([msk, y])        # :352
```

**For `Tid=[0.0]` this is mathematically identical to official Wan2.2 I2V:** `id_ = 0`, so
`msk` is 1 at frame 0 and 0 elsewhere (= Wan's `ones` then `[:,1:]=0`), and `vae_in` is the image
at frame 0 with zeros after (= Wan's `concat`). Same 4+16 = 20-channel `y`, same
channel-concat into the DiT (`anisoraV3.2/wan/modules/model.py:437-445`,
`x = [torch.cat([u, v], dim=0) ...]`, i.e. `in_dim = 36`).

**So `WanImageToVideoPipeline` / our `wan_i2v.py` A14B path is a valid host for these weights
for ordinary first-frame I2V.** No custom code required.

Their extra capability — several anchor stills at several temporal positions (`&&0,0.5,1`) — is
a *calling convention* on the same tensor, not an architecture change. If we ever want
first+last-frame or mid-frame anchoring we'd need ~15 lines in our own pipeline, not their repo.
Their shipped examples exercise it: `anisoraV3/data/inference_any.txt:1` (`&&0,0.5`), `:2`
(`&&0,0.5,1`), `:3` (single anchor at `&&0.75`).

### First-frame preservation: there is none, by design

I looked specifically for a latent-replacement / re-injection clamp. **There isn't one.** The
sampling loop at `anisoraV3.2/wan/image2video.py:411-439` never re-writes the anchor frame's
latent between steps — no `latent[:, 0] = init_latent`, no blending, no masked-composite.
Conditioning is entirely via the `y` channels, exactly like vanilla Wan I2V.

Consequence for our storyboard-still workflow: **AniSora V3.2 is not architecturally more
faithful to the init frame than vanilla Wan.** Any improvement in first-frame adherence is a
learned property of the fine-tune, not a guarantee in code. Their own benchmark is the evidence
to lean on, not the code: `README.md:190` VBench **I2V Subject 97.52 (best in table)** and
**Subject Consistency 96.99 (best in table)**, and `README.md:207` AniSora-Benchmark
**Image-Video Consistency 91.96 vs Wan-2.1's 88.50** and **Character Consistency 94.88 (V1)**.
Those are the numbers that argue it holds a character better than vanilla Wan.

### Anime-specific handling: none in code, all in weights

Grepped the V3.2 tree for line-art / cel / flat-colour / palette handling: **nothing**. No edge
detection, no line-art preprocessor, no palette or chroma preservation, no anime-specific VAE.
The inference path is colour-agnostic stock Wan.

So the honest answer to "why should it beat vanilla Wan on our material" is: **because of the
training data and the reward alignment, and that is a claim we have to test, not read.** The
supporting claims in the repo:

- `README.md:161` (abstract): a data pipeline with "over 10M high-quality data", and "the
  generation model incorporates a **spatiotemporal mask module** to facilitate key animation
  production functions such as image-to-video generation, frame interpolation, and localized
  image-guided animation."
- `README.md:175`: the mask module is the framework's stated core contribution.
- `README.md:141-149`: anime-optimised benchmark, 948 labelled animation clips, ACG-aligned;
  `reward/` holds reward models for RLHF, `anisora_rl/` is "the first RLHF framework for anime
  video generation" (`README.md:155`).
- `README.md:17` on intended domain: "series episodes, Chinese original animations, manga
  adaptations, VTuber content, anime PVs, mad-style parodies".
- `data_pipeline/` — their anime data cleaning pipeline (`README.md:135-138`).

Adjacent capability worth knowing about but out of scope for V3.2: the **anymask** model
(`README.md:22`, released 2025-10-31, HF `anymask` folder, code in `anisora_anymask/`) does
"image-to-video generation with temporal and spatial masks" — the closest thing to region-locked
conditioning if we ever need to pin part of a frame.

---

## 4. VRAM / RAM — this is the finding that bites

### They publish no V3/V3.2 memory requirement at all

Grepped every markdown in the repo. The only hardware numbers are **V1-era** (CogVideoX-5B, not
Wan): `README.md:131` "Cost-effective deployment on RTX 4090", and `anisoraV1_infer/README.md:59-62`
"**2 × RTX 4090** runs **OOM** during decoding", "**RTX 4090** only supports up to **640×1088**
resolution". Nothing anywhere states a V3.2 requirement. Their own commands assume 1-2 unnamed
datacentre GPUs with FSDP.

### Built-in memory levers (all of them)

| lever | where | what it does |
|---|---|---|
| `offload_model` | `generate_txt_new.py:116-121`; **defaults to `True` on single GPU** (`:258-259`) | swaps the inactive expert to CPU, keeps one resident: `anisoraV3.2/wan/image2video.py:202-211` |
| per-forward `empty_cache` | `image2video.py:424-429` | between the cond and uncond passes |
| post-sample offload | `image2video.py:444-447` | both experts to CPU before VAE decode |
| `--t5_cpu` | `generate_txt_new.py:132-136`; used at `image2video.py:330-334` | keeps umt5-xxl off the GPU |
| `--convert_model_dtype` | `generate_txt_new.py:212-216`; `image2video.py:170-171` | casts DiT to `param_dtype` = **bf16** (`shared_config.py:14`) |
| `--dit_fsdp` / `--t5_fsdp` / `--ulysses_size` | `generate_txt_new.py:127-141` | multi-GPU sharding only; asserted off for single GPU (`:270-275`) |

**There is no quantisation.** Grepped V3.2 for `quantiz|fp8|int8|bitsandbytes|gguf` — the only hit
is a `uint8` cast in the video writer (`wan/utils/utils.py:45`). No fp8, no GGUF, no torchao.

### The arithmetic against our 24GB / 64GB box

- A14B is **14B parameters per expert, two experts**. At bf16 that is **~28GB for one expert** —
  already **over the 5090's 24GB** before activations, before the 20-channel `y`, before the
  ~74k-token sequence that 704x1280x81 implies (`lat_h=160`, `lat_w=88`, 21 latent frames,
  tokens = 21 x 80 x 44 = 73,920).
- Their best single-GPU configuration — `offload_model=True` + `convert_model_dtype` + `t5_cpu` —
  gets peak VRAM down to *one bf16 expert plus activations*, i.e. **still ~28GB+. It does not
  fit.** Their code has no lever that closes this gap.
- **Both experts are genuinely required** at the 8-step recipe, so we cannot halve the problem by
  downloading one. Computing their documented schedule (`fm_solvers_unipc.py:184-207`,
  `sigmas = linspace(sigma_max, sigma_min, N+1)[:-1]` then `shift*s/(1+(shift-1)*s)`,
  `timesteps = sigmas*1000`; `sigma_max=0.999`, `sigma_min=0.0` from `:108-134`; scheduler built
  with `shift=1` at `image2video.py:373-376` then `set_timesteps(steps, shift=5)` at `:377-378`):

  | steps | timesteps | high-noise (t>=900) | low-noise |
  |---|---|---|---|
  | **8** | 999.8, 972.0, 937.3, 892.6, 833.1, 749.7, 624.7, 416.4 | **3 steps** | **5 steps** |
  | 40 | 999.8 … | 15 steps | 25 steps |

  So 8 steps = 3 on the high-noise expert, 5 on the low-noise, **exactly one expert swap**
  (boundary 900 = `0.900 x 1000`, `image2video.py:370`). Cheap swap, but both experts needed.
  (That table is my own arithmetic on their documented formula — I did not execute their code.)
- **RAM is the second squeeze.** The download is fp32 (~57GB per expert). `WanModel.from_pretrained`
  loads an expert whole (`image2video.py:106-107`, `:115-116`) — a single 57GB fp32 expert nearly
  fills 64GB RAM on its own, and `offload_model` wants *both* experts resident in CPU RAM
  simultaneously (~114GB fp32, ~56GB bf16). **Plan on converting the weights to bf16 or fp8 on
  disk before first run**; do not expect the stock script to load 126GB of fp32 on a 64GB box.

**Verdict: V3.2 A14B will not run on the 24GB 5090 with their code.** It needs an fp8 path
(~14GB/expert, comfortable) or block-swap — i.e. our own quantised loader, Kijai's fp8/GGUF
Wan2.2 A14B conversions, or diffusers + torchao. None of that comes from this repo.

### The 12GB V3.1 build — announced, not shipped here

`README.md:23` (2025/09/25) is the entire record: "The 12GB VRAM available version of V3.1 has
been uploaded to ModelScope", linking `modelscope.cn/models/bilibili-index/Index-anisora` →
`wan.7z`. **Nothing about what was cut is in the GitHub repo** — no code, no config, no notes,
no `anisoraV3.1/` directory (the repo has only `anisoraV3/` and `anisoraV3.2/`). Grepping the
whole tree for `12g|wan\.7z|V3\.1` returns only that line plus `anisoraV3/README.md:16,20`.

Two things we *can* infer from the repo rather than guess:

- **V3.1 is Wan2.1-14B-class, not A14B.** `anisoraV3/README.md:16` and `:20` tell you to download
  the **V3.1** folder to run the `anisoraV3/` code, and that code's config is
  `anisoraV3/wan/configs/wan_i2v_14B.py` with `--ckpt_dir Wan2.1-I2V-14B-480P`
  (`anisoraV3/README.md:32`) and a CLIP encoder (`anisoraV3/wan/modules/clip.py`). So the 12GB
  build is a **single 14B Wan2.1 model, not a two-expert 28B stack** — that alone is most of the
  memory difference, before any quantisation in the `.7z`.
- Therefore the 12GB claim does **not** transfer to V3.2. Nothing suggests a 12GB A14B exists.

**If 24GB is a hard constraint, V3.1 (single 14B, Wan2.1 base, 12GB build exists) is the variant
that actually fits, and V3.2 is the one that needs a quantised loader we build.** Worth noting
V3.1 is also the motion-improved release (`README.md:25`).

---

## 5. Motion — read this before choosing AniSora

This is our critical axis, and the repo's own numbers cut against the model.

### What they give us for control

- **A `motion score` token in the prompt.** `anisoraV3.2/README.md:135-139`:
  Motion Score, recommended **2.0-4.0**, "Controls movement intensity (higher values = more
  dynamic motion)". Aesthetic Score 5.0-7.0, "higher = more cinematic".
- Every shipped example uses **`motion score: 3.0`** — `anisoraV3.2/data/inference_any.txt:1`,
  `anisoraV3.2/data/inference_360.txt:1-3`. The README's own prose example uses `4.0`
  (`anisoraV3.2/README.md:141`).
- `README.md:25` (V3.1): "provide **enhanced motion range capabilities**. For optimal results,
  we strongly recommend using the v3.1 weights with a **motion score setting of 2.0-4.0**."
- `README.md:26` (V3): "delivering **greater overall dynamics and more natural motion**."

So yes — they address motion explicitly, and they expose it as a **conditioning token trained
into the model**, which is a genuinely better lever than prompt adjectives. It is a continuous
knob we can sweep, exactly the shape of experiment our step-sweep and shake-A/B already use.

### But their own benchmarks say AniSora moves *less* than everything else

VBench, `README.md:183-193` — AniSora has the **lowest Motion Score in the entire table**:

| model | Motion Score | Motion Smoothness | I2V Subject | Subject Consistency |
|---|---|---|---|---|
| Vidu | **77.51** | 97.71 | 92.25 | 88.27 |
| Opensora-Plan V1.3 | 76.45 | 99.13 | 93.53 | 88.86 |
| MiniMax | 66.53 | 99.20 | 95.95 | 93.62 |
| **GT (real anime)** | **56.05** | 98.72 | 96.02 | 94.37 |
| **AniSora** | **45.59** | **99.34** | **97.52** | **96.99** |

AniSora-Benchmark, `README.md:198-211` — same shape, and the direct Wan comparison:

| model | Visual Motion | Visual Smooth | Visual Appeal | Image-Video Consistency |
|---|---|---|---|---|
| Vidu-1.5 | **78.95** | 55.37 | 50.68 | 66.85 |
| **Wan-2.1** | **61.88** | 81.70 | 82.05 | 88.50 |
| GT | 58.27 | 92.20 | 89.72 | 94.69 |
| AniSora-V2 | **50.34** | **86.98** | **85.91** | **91.96** |
| AniSora-V1 | 48.45 | 71.88 | 65.38 | 82.66 |

**AniSora-V2 scores 50.34 on Visual Motion against Wan-2.1's 61.88 — it is measurably stiller
than the vanilla Wan we are already fighting for motion.** It wins everything else in that row
(smoothness, appeal, both consistency metrics), which is exactly the consistency-for-motion trade
you would expect from a model tuned for character stability. Note these tables are V1/V2 numbers;
**no V3/V3.1/V3.2 row is published in this repo**, and V3.1's headline was "enhanced motion
range" — so the released V3.2 may well be better than these rows. But the published evidence we
have points the wrong way on our one critical axis, and the burden is on a sample to disprove it.

### The recipe silently disables our anti-stillness lever

Their recommended `--sample_guide_scale 1` means the negative prompt does nothing (§6). Our
existing anti-frozen-frame work — the negative-prompt stillness terms, the shake-terms A/B — is
**CFG-dependent and does not transfer to a CFG=1 recipe.** Under their recipe the only motion
levers are the `motion score` token, `shift`, seed, and the prompt's verb content.

### One prompt principle worth stealing

Stock-Wan but directly on point, `anisoraV3.2/wan/utils/system_prompt.py:91` (the I2V prompt
extender's instruction): "Focus on dynamic content in the video description and **avoid adding
static scene descriptions. If the user's input already describes elements visible in the image,
remove those static descriptions.**" Same idea in Chinese at `:69` and `:111`. For I2V from an
approved still, describing what is already visible spends prompt budget on stillness — describe
only what *changes*.

---

## 6. Negative prompt and prompt conventions

### Negative prompt: stock Wan, unchanged, and inert at their recipe

`anisoraV3.2/wan/configs/shared_config.py:19` — one line, verbatim the standard Wan2.1/2.2
Chinese negative prompt, **not customised for anime**:

```
色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，
JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，
手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走
```

(garish colour tone, overexposed, **static**, blurry details, subtitles, style, artwork, painting,
picture, **still**, overall greyness, worst quality, low quality, JPEG artefacts, ugly, mutilated,
extra fingers, badly drawn hands, badly drawn face, deformed, disfigured, malformed limbs, fused
fingers, **motionless picture**, cluttered background, three legs, crowded background, walking
backwards.)

Default is empty and falls back to that config value: `image2video.py:320-321`
(`if n_prompt == "": n_prompt = self.sample_neg_prompt`). Note it contains three anti-stillness
terms (静态 / 静止 / 静止不动的画面) — but see below.

### The CFG=1 finding — a real inefficiency in their script

`anisoraV3.2/wan/image2video.py:422-431` computes **both** passes unconditionally, every step:

```python
noise_pred_cond   = model(latent_model_input, t=timestep, **arg_c)[0]
noise_pred_uncond = model(latent_model_input, t=timestep, **arg_null)[0]
noise_pred = noise_pred_uncond + sample_guide_scale * (noise_pred_cond - noise_pred_uncond)
```

At their recommended `--sample_guide_scale 1` this is algebraically
`uncond + 1*(cond - uncond) = cond`. So:

1. **The negative prompt has exactly zero effect at the reference recipe** — including its three
   anti-stillness terms. Anyone tuning the negative prompt at CFG=1 is tuning nothing.
2. **The discarded uncond forward is still paid for.** 8 steps cost **16 DiT forwards** for 8
   steps of useful work. In our own pipeline, skipping the uncond pass when CFG==1 is a
   **straight ~2x speedup** over their script with bit-identical output. Free win, and it halves
   the per-step VRAM churn too.

Per-expert CFG is supported (`guide_scale` tuple, low/high, `image2video.py:271-272`, `:419-420`,
default `(3.5, 3.5)` at `wan_i2v_A14B.py:37`) — so if we want the negative prompt back we can run
CFG>1 on one expert only, at the cost of steps.

### Prompt format

Documented at `anisoraV3.2/README.md:125-141`:

```
[Video description] + aesthetic score: X.X. motion score: X.X. There is no text in the video.
```

- The **"There is no text in the video." clause is marked Mandatory** (`README.md:139`) —
  "Prevents unwanted captions or text overlays". Directly useful for us: our episodes carry
  burned-in captions from `render_t3.py`, so we do not want the model inventing text.
- **Long, detailed prompts** (`README.md:133`): "Our model works better with long, detailed
  prompts since it's trained with such prompts." Their shipped examples run 60-120 words
  (`data/inference_any.txt:1`, `data/inference_360.txt:1-3`) and read as scene descriptions with
  the score suffix appended.
- English is fine and preferred for V3: `anisoraV3/README.md:125` says
  "[Video description **in English Better**]".
- Prompt extension is **not** wired up for V3.2 — `README.md:133`: "We will integrate prompt
  extension into the codebase (similar to Wan2.1) in the future. For now, it is recommended to
  use third-party LLMs (such as GPT-4o) to extend your prompt."

A worked example, `anisoraV3.2/data/inference_any.txt:1` (their only `inference_any` case):

> In the animated series "My Little Pony: Friendship is Magic," we witness a heartwarming scene
> featuring two characters: a purple unicorn with pink mane and tail, and a green dragon with a
> purple mane and tail. The unicorn, adorned with a sparkling star on its flank, strides forward
> with purpose. Suddenly, the unicorn raises its arm, seemingly about to express something
> important.aesthetic score: 5.5. motion score: 3.0. There is no text in the video.@@data/inference-imgs/1.png&&0

Note the pattern: **name the show/style, describe characters concretely, then one clear action
beat** ("strides forward", "raises its arm"). The 360-rotation prompts additionally lead with a
fixed incantation — "A 360-degree turning and circling video of an anime character. This is a long
shot with a plain white background." (`data/inference_360.txt:1-3`).

### Do not use their prompt extender

`--use_prompt_extend` (`generate_txt_new.py:162-183`, `:281-295`) runs the **stock Wan** extender
in `wan/utils/prompt_extend.py` against the system prompts in `wan/utils/system_prompt.py`. Two
reasons to leave it off:

1. Those system prompts know nothing about AniSora's convention — they never emit
   `aesthetic score` / `motion score` / the no-text clause, so extending a prompt would **strip
   the very tokens the weights were trained on**.
2. The vendored Wan system prompts contain content-substitution clauses that silently rewrite the
   user's prompt on a list of topics rather than passing it through
   (`system_prompt.py:21-23` and `:50-52`, clauses 8-10 in both the ZH and EN blocks). Whatever
   one thinks of that policy, silent prompt substitution is incompatible with our provenance rule
   (§7.2: publish the prompt that was actually used). Compose prompts ourselves and append the
   score suffix.

---

## Documentation defects found (so we do not trip on them)

1. **The prompt-file format is documented backwards.** `anisoraV3.2/README.md:108` (and
   `anisoraV3/README.md:103`) say `image_path@@prompt&&image_position`. The code does the
   opposite — `generate_txt_new.py:410`: `pormpt, image_path = text.split('@@')`. All their own
   data files are **prompt first**: `data/inference_any.txt:1`, `data/inference_360.txt:1-3`.
   Correct format is `PROMPT@@img[,img...]&&Tid[,Tid...]`.
2. **Frame-count rule is stated two ways.** `generate_txt_new.py:99` help text says "4n+1";
   `anisoraV3.2/README.md:121` says "must satisfy F=8x+1". Given anchors snap to multiples of 8
   (`image2video.py:309`), **8x+1 is the safe rule** — 81 satisfies both.
3. **704x1280 is blocked by an assert, not by the model.** `SUPPORTED_SIZES['i2v-A14B']`
   (`wan/configs/__init__.py:37`) omits it although `MAX_AREA_CONFIGS` has it (`:31`); the assert
   is `generate_txt_new.py:73-75`. Irrelevant in our own pipeline (§2).
4. **The 8-step recipe is not in the config.** Config still ships Alibaba's 40 steps / CFG 3.5
   (`wan_i2v_A14B.py:34-37`). Only the README command line sets 8 / CFG 1.
5. **V3's docs are internally inconsistent about steps** — `anisoraV3/README.md:29-37`
   (single-GPU) passes no `--sample_steps` (so 40), while `:41-59` (multi-GPU) passes 8. Same
   model. Treat their step counts as suggestions, not measurements.
6. `--image` is documented as "specifies the output folder" (`anisoraV3.2/README.md:114`) but for
   the i2v path the output folder is `--save_dir`; `--image` is unused in the list branch.

---

## Bottom line

- **Licence:** the GitHub repo carries a real licence file the HF repo lacks, so the "unverifiable"
  gap is closable — but the answer is **Apache-2.0 + a bilibili "Model License Agreement" with six
  additional restrictions** (`LICENSE:203-214`), and those restrictions are scoped to
  fine-tuning/retraining, which we are not doing. **For inference-and-publish our effective terms
  are Apache-2.0**, with a broad indemnity clause (clause 4) as the one term that is not
  retraining-scoped. Do not label the model plain "apache-2.0" in provenance.
- **Compatibility:** architecture is stock Wan2.2-I2V-A14B; for first-frame I2V their conditioning
  is bit-identical to official Wan. **Drop-in for our A14B path.**
- **8 steps:** real, native (no LoRA anywhere), and paired with CFG=1 — but their script wastes
  half its compute on a discarded uncond pass at CFG=1, which we should not replicate.
- **The blocker is VRAM, not licence or code:** ~28GB per bf16 expert, both experts needed, no
  quantisation in the repo. Needs our own fp8 path, or V3.1 (single 14B) instead.
- **The risk is motion:** their own published benchmarks put AniSora *below vanilla Wan-2.1* on
  visual motion. The `motion score` token is a real trained knob and the right first thing to
  sweep — on ONE sample.
