# Open-weight image-to-video models — licence audit

Researched 2026-08-04. Scope: every open-weight I2V model that could realistically
run locally on (a) RTX 5090 laptop, ~24GB VRAM, Windows, (b) RTX 5070 Ti laptop, 12GB
VRAM. Verdicts are about **whether we may publish and monetise the output**, given
banyan-city publishes clips publicly under CC BY 4.0 with per-clip provenance.

> **See first: [Wan2.2-TI2V-5B-Turbo licence chain](#priority-the-wan22-ti2v-5b-turbo-4-step-licence-chain)
> at the bottom of this file. Verdict: BLOCKED. The original distill is CC BY-NC-SA 4.0.
> Our `vet_model.py` gate was right; the non-commercial link is the distill itself.**

Test applied (all four must pass, else NO):

1. Takes an image (or text+image) as conditioning — we condition on an approved still.
2. Licence permits commercial publication of output, **no field-of-use restrictions
   travelling to the output**, no territory exclusion.
3. Weights downloadable without a gate we cannot pass.
4. Runs in 24GB or 12GB.

## Summary table

| Model (HF repo id) | I2V? | Params / on-disk | Licence NAME | Verdict | Min VRAM (authors' own claim) |
|---|---|---|---|---|---|
| `Wan-AI/Wan2.2-I2V-A14B` (+`-Diffusers`) | Yes | 27B total / 14B active MoE; repo ~76GB incl. 11.4GB T5 + 508MB VAE | Apache-2.0 | **SHIP-SAFE** | 80GB single-GPU unoptimised |
| `QuantStack/Wan2.2-I2V-A14B-GGUF` | Yes | Q2_K 5.3GB → Q8_0 15.4GB per expert | Apache-2.0 | **SHIP-SAFE** | n/a (Q4_K_S 8.75GB/expert) |
| `Wan-AI/Wan2.2-TI2V-5B` (+`-Diffusers`) | Yes (text+image) | 5B; repo ~34.2GB total | Apache-2.0 | **SHIP-SAFE** | "consumer-grade graphics cards like 4090" |
| `Wan-AI/Wan2.2-S2V-14B` | Yes (image+audio) | 16B total / 14B active | Apache-2.0 | **SHIP-SAFE** | 80GB |
| `Wan-AI/Wan2.2-Animate-14B` | V2V (image+driving video) | 14B | Apache-2.0 | **SHIP-SAFE** | not stated |
| `Wan-AI/Wan-Dancer-14B` | Yes (image+music) | 14B | Apache-2.0 | **SHIP-SAFE** | not stated |
| `Wan-AI/Wan2.1-I2V-14B-480P` / `-720P` | Yes | 14B | Apache-2.0 | **SHIP-SAFE** | not stated |
| `Wan-AI/Wan2.1-VACE-1.3B` / `-14B` | Yes | 1.3B / 14B | Apache-2.0 | **SHIP-SAFE** | not stated |
| `aidealab/AnimeGen-I2V` | Yes | 14B active, BF16; repo ~114GB (all variants), ~14.3GB BF16/expert | Apache-2.0 (stock text, verified) | **SHIP-SAFE** | "RTX 4090 or higher" |
| `IndexTeam/Index-anisora` V2 / V3 / V3.1 / V3.2 | Yes | 14B (V2/V3, Wan base) | Apache-2.0 | **SHIP-SAFE** | V3.1 has a 12GB-compatible build (ModelScope) |
| `IndexTeam/Index-anisora` **V1 / 5B** | Yes | 5B | Apache-2.0 tag over **CogVideoX-5B** base | **UNCLEAR** (laundering) | "cost-effective on RTX 4090" |
| `kandinskylab/Kandinsky-5.0-I2V-Lite-5s` | Yes | 2B | **MIT** (tag and LICENSE agree) | **SHIP-SAFE** | "24 GB with offloading" |
| `IamCreateAI/Ruyi-Mini-7B` | Yes | 7.1B | Apache-2.0 | **SHIP-SAFE** | 21.5GB @360x480; 54.8GB @720x1280 |
| `hpcai-tech/Open-Sora-v2` | Yes | 11B | Apache-2.0 | **SHIP-SAFE** | 44.3GB peak @256x256 |
| `stepfun-ai/stepvideo-ti2v` | Yes | 29B | **MIT** | **SHIP-SAFE** but impractical | 75.5–76.4GB single GPU |
| `nvidia/Cosmos-Predict2.5-2B` / `-14B` | Yes (IMAGE2WORLD) | 2B / 14B | NVIDIA Open Model License | **SHIP-SAFE** w/ caveat | not stated |
| `Lightricks/LTX-2.3` / `-fp8` / `-nvfp4` | Yes | 22B | LTX-2 Community License Agreement | **UNCLEAR** — founder call | fp8 distilled 12–16GB; 24GB w/ offload; 32GB BF16 |
| `Lightricks/LTX-2` | Yes | 19B | LTX-2 Community License Agreement | **UNCLEAR** — founder call | not stated |
| `Lightricks/LTX-Video-0.9.8-13B-distilled` (13B family) | Yes | 13B | LTXV Open Weights License 0.X | **UNCLEAR** — founder call | not stated |
| `Lightricks/LTX-Video` **2B v0.9 / 0.9.1 / 0.9.5** | Yes | 2B / 5.7–9.4GB | **RAIL-M** | **BLOCKED** — research only | n/a |
| `Skywork/SkyReels-V3-R2V-14B` | Yes (1–4 ref images) | 14B, BF16 | Skywork Community License | **UNCLEAR** — licence is PDF-only | `--low_vram` flag "for GPUs under 24GB" |
| `Skywork/SkyReels-V2-I2V-14B-720P` | Yes | 14B / 16B on disk | Skywork License | **UNCLEAR** — same | 43.4GB peak @540P |
| `tencent/HunyuanVideo-I2V` | Yes | 13B | Tencent Hunyuan Community License | **BLOCKED** — territory | n/a |
| `tencent/HunyuanVideo-1.5` | Yes | 8.3B | Tencent Hunyuan Community License | **BLOCKED** — territory | n/a |
| `lllyasviel/FramePackI2V_HY` | Yes | 13B | **none declared** (Hunyuan-derived) | **BLOCKED** | 6GB (code claim) |
| `THUDM`/`zai-org/CogVideoX-5b-I2V` | Yes | 6B | CogVideoX License | **BLOCKED** | "from 5GB" w/ optimisations |
| `zai-org/CogVideoX1.5-5B-I2V` | Yes | 5B | CogVideoX License | **BLOCKED** | n/a |
| `stabilityai/stable-video-diffusion-img2vid-xt` | Yes | 2B | Stability AI Community License | **BLOCKED** | A100 80GB reference |
| `genmo/mochi-1-preview` | **NO** | 10B | Apache-2.0 | **NO — fails I2V requirement** | 22GB bf16 / <20GB ComfyUI |
| `quanhaol/Wan2.2-TI2V-5B-Turbo` + all diffusers/GGUF rebuilds | Yes | 5B, 4 steps | **CC BY-NC-SA 4.0** | **BLOCKED** — NonCommercial *and* ShareAlike | 4GB (GGUF) |
| `lightx2v/Wan2.2-Lightning` → `Wan2.2-I2V-A14B-4steps-lora-rank64-Seko-V1` | Yes (LoRA) | rank-64 LoRA, 4 steps | Apache-2.0 (GitHub `LICENSE.txt` verified) | **SHIP-SAFE** | A14B host model |
| `FastVideo/FastWan2.2-TI2V-5B-FullAttn-Diffusers` (the T5 3-step LoRA) | Yes (text+image, via the 5B base) | rank-128 LoRA 630MB, or 10.0GB merged | Apache-2.0 (GitHub `LICENSE` read + vendored) | **SHIP-SAFE** — mirror caveat below | TI2V-5B host model, no new base weights |

---

## Verbatim licence clauses governing OUTPUT

### Wan family — Apache-2.0 — SHIP-SAFE

Model card, <https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B>:

> "We claim no rights over the your generated contents, granting you the freedom to
> use them while ensuring that your usage complies with the provisions of this license."

Stock Apache-2.0 text: <https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/LICENSE.txt>
— confirmed unmodified Apache License 2.0, which contains **no output clause at all**
(so nothing travels to output) and no territory or field-of-use restriction.

**Paper-trail caveat, flag this:** neither `Wan-AI/Wan2.2-I2V-A14B` nor
`Wan-AI/Wan2.2-TI2V-5B` ships a `LICENSE` file in the HF repo. The HF file listings
contain no LICENSE; the Apache-2.0 claim rests on (a) the HF `license: apache-2.0`
metadata tag and (b) the one sentence quoted above in the README. The actual licence
text lives only in the GitHub repo. Tag and README agree, and the GitHub text is
genuine Apache-2.0, so the verdict stands — but if we ever need to *prove* our chain,
cite the GitHub `LICENSE.txt`, not the HF repo.

The README also carries an acceptable-use sentence ("must not involve sharing any
content that violates applicable laws, causes harm to individuals or groups…").
This is README prose, not licence text, and Apache-2.0 has no mechanism to bind it
to output. Not a blocker.

### aidealab/AnimeGen-I2V — Apache-2.0 — SHIP-SAFE (verified, cleaner than we recorded)

<https://huggingface.co/aidealab/AnimeGen-I2V/raw/main/LICENSE> is the stock
Apache License 2.0, January 2004:

> "Apache License
> Version 2.0, January 2004
> http://www.apache.org/licenses/"

**No additions beyond stock Apache-2.0** — no output clause, no commercial
restriction, no custom terms. HF tags include `commercial-use`. Base model is
`Wan-AI/Wan2.2-I2V-A14B`, itself Apache-2.0, so the whole chain is permissive.
This is the strongest licence position of any anime-specific model in the field.

### Index-AniSora (Bilibili) — Apache-2.0 — SHIP-SAFE for V2/V3+

<https://github.com/bilibili/Index-anisora>:

> "Anisora V3 weights are now licensed under Apache 2.0 and publicly available"
> "Anisora V2 weights are now licensed under Apache 2.0"

Base-model chain by version — this is what decides the verdict:

| Version | Base | Chain clean? |
|---|---|---|
| V1 (5B) | CogVideoX-5B | **NO** — Apache-2.0 declared over a CogVideoX-License base |
| V2 | Wan2.1-14B | Yes (Apache-2.0 base) |
| V3 / V3.1 / V3.2 | Wan2.2 | Yes (Apache-2.0 base) |

**Use V3.2.** It is trained on Wan 2.2, needs only 8 inference steps, and V3.1
shipped a 12GB-VRAM-compatible build. Avoid the `5B` / `5B_RL` folders and
`Disty0/Index-anisora-5B-diffusers`: those are the CogVideoX-based V1 line and
inherit the laundering problem below.

Paper-trail caveat: the HF repo `IndexTeam/Index-anisora` carries an `apache-2.0`
tag but **no LICENSE file**. Same situation as Wan.

### Kandinsky 5.0 — MIT — SHIP-SAFE (best licence in the field)

HF tag on `kandinskylab/Kandinsky-5.0-I2V-Lite-5s`: `mit`.
<https://raw.githubusercontent.com/kandinskylab/kandinsky-5/main/LICENSE>:

> "The MIT License (MIT)
>
> Copyright (c) 2025 Kandinsky Lab
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights"

Tag and file **agree**. MIT has no output clause, no field-of-use restriction, no
territory. 2B params — the only genuinely small SHIP-SAFE I2V model in the list.

### NVIDIA Cosmos-Predict2.5 — NVIDIA Open Model License — SHIP-SAFE with caveat

<https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/>:

> "NVIDIA claims no ownership rights in outputs. You are responsible for outputs
> and their subsequent uses."

No territory restriction. Guardrail clause binds *us as licensee*, not the output:

> "If You bypass, disable, reduce the efficacy of, or circumvent any technical
> limitation, safety guardrail or associated safety guardrail hyperparameter,
> encryption, security, digital rights management, or authentication mechanism…
> your rights under this Agreement will automatically terminate."

Practically fine — we would just not disable the safety filter. **But Cosmos is a
physical-AI world-simulation model** aimed at robotics and autonomous driving, not
stylised animation. Licence-clean, wrong tool. Low priority.

### LTX — three different licences — our recorded "REJECTED" is PARTLY WRONG

This is the biggest correction in the audit. See the corrections section.

**LTX-Video 2B v0.9.x — RAIL-M — BLOCKED, research only.**
<https://huggingface.co/Lightricks/LTX-Video/raw/main/ltx-video-2b-v0.9.1.license.txt>:

> "Subject to the terms and conditions of this License, each Contributor hereby
> grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free,
> irrevocable copyright license to reproduce, prepare, publicly display, publicly
> perform, sublicense, and distribute the Model and Derivatives of the Model,
> **only for the Permitted Purpose**."

with Permitted Purpose defined as "for academic or research purposes only, and
explicitly excludes commercialization such as downstream selling of the Model or
Derivatives of the Model."

Output clause — note the sting in the tail:

> "Except as set forth herein, Licensor claims no rights in the Output You generate
> using the Model. You are accountable for the input you insert into the Model, the
> Output you generate and its subsequent uses. **No use of the Output can contravene
> any provision as stated in the License.**"

That last sentence is exactly the OpenRAIL structure — a restriction that travels
to output. BLOCKED, confirmed.

**LTX-Video 13B — LTXV Open Weights License 0.X — commercial IS permitted under $10M.**
<https://huggingface.co/Lightricks/LTX-Video/raw/main/LTX-Video-Open-Weights-License-0.X.txt>:

> "entities with annual revenues of at least $10,000,000 (the 'Commercial Entities')
> are eligible to obtain a paid commercial use license"

> "Licensor claims no rights in the Output you generate using the Model. You are
> accountable for input you insert into the Model, the Output you generate and its
> subsequent uses."

**LTX-2 and LTX-2.3 — LTX-2 Community License Agreement (5 January 2026).**
<https://raw.githubusercontent.com/Lightricks/LTX-2/main/LICENSE>:

> "you are granted a non-exclusive, worldwide, non-transferable and royalty-free
> limited license under Licensor's intellectual property or other rights owned by
> Licensor embodied in LTX-2 to use, reproduce, prepare, distribute, publicly
> display, publicly perform, sublicense, copy, create derivative works of, and make
> modifications to LTX-2, **for any purpose**"

> "Entities with annual revenues of at least $10,000,000 (the 'Commercial Entities')
> are required to obtain a paid commercial use license in order to use LTX-2 and
> Derivatives of LTX-2"

> "Except as set forth herein, Licensor claims no rights in the Output you generate
> using LTX-2. You are accountable for input you insert into LTX-2, the Output you
> generate and its subsequent uses."

Worldwide, no territory exclusion, commercial permitted free below $10M revenue,
Licensor claims no rights in output. **But** it carries a 20-item use-restriction
schedule that constrains what may be done with output, including:

> "place the information and/or content in any context without expressly and
> intelligibly disclaiming that the information and/or content is machine generated"

plus prohibitions on unlawful use, deepfakes/impersonation without consent, medical
advice, law-enforcement and immigration use, military use, employment/credit/housing
decisions, training competing models (commercial users), and more.

**Why this is a founder decision, not a steward call.** The disclosure requirement we
already satisfy and then some — every clip publishes model, prompt and cost in its
leaf yaml (§7.2), and the repo *is* the provenance record. The real question is
structural: we publish under **CC BY 4.0**, which grants downstream recipients
unrestricted use. The LTX schedule purports to restrict what may be done with the
output. Those two cannot both be true for a downstream recipient. This is the same
incompatibility we already identified for OpenRAIL — it is not weaker just because
the rest of the LTX licence is friendlier. Verdict: **UNCLEAR, founder call**, filed
with the taste/governance decisions rather than resolved here.

### SkyReels (Skywork) — UNCLEAR, licence not machine-readable

`Skywork/SkyReels-V3-R2V-14B` and `SkyReels-V2-I2V-14B-720P` tag `skywork-license`.
The Skywork Community License is distributed **only as a PDF** (in
`SkyworkAI/Skywork` and mirrored in `Skywork/Skywork-13B-base`). I could not extract
a verbatim Outputs clause or a Territory definition from the licence body. What is
verifiable from the model cards:

> "The Skywork model supports commercial use" — and users "must abide by terms and
> conditions within [Skywork Community License]", with no additional licensing fee.

The `SkyReels-V3` GitHub README states **no licence at all**. Grant language found in
secondary sources describes it as "non-exclusive, worldwide, non-transferable,
non-sublicensable, **revocable**, royalty-free" — a revocable grant is a poor
foundation for published commercial work, and I could not confirm it primary-source.
**UNCLEAR.** Do not use until someone reads the PDF. Not worth the effort while
AniSora V3.2 and AnimeGen-I2V exist under stock Apache-2.0.

### HunyuanVideo family — BLOCKED on territory (our record CONFIRMED)

<https://huggingface.co/tencent/HunyuanVideo-I2V/raw/main/LICENSE> and
<https://huggingface.co/tencent/HunyuanVideo-1.5/raw/main/LICENSE>, both
**Tencent Hunyuan Community License Agreement**, identical clause:

> "'Territory' shall mean the worldwide territory, excluding the territory of the
> European Union, United Kingdom and South Korea."

The output clause itself is generous —

> "Tencent claims no rights in Outputs You generate. You and Your users are solely
> responsible for Outputs and their subsequent uses."

— but it operates only inside Territory. We publish on TikTok and a public website;
we cannot exclude EU/UK/KR viewers, and there is no reading under which a
geographically-limited licence supports worldwide publication. **BLOCKED**, and this
now extends to HunyuanVideo-1.5 (8.3B, Nov 2025), which several 2026 blog roundups
mis-report as Apache-2.0. It is not.

### FramePack — BLOCKED, no licence on the weights at all

The `lllyasviel/FramePack` **code** is Apache-2.0. The **weights** are
`lllyasviel/FramePackI2V_HY` — a HunyuanVideo derivative (the `_HY` suffix; the
project downloads ~30GB of HunyuanVideo components at setup). Checked
<https://huggingface.co/api/models/lllyasviel/FramePackI2V_HY>:

- `cardData` license field: **absent**
- tags: `diffusers`, `safetensors`, `region:us` — **no licence tag**
- file list: `.gitattributes`, `README.md`, `config.json`, three
  `diffusion_pytorch_model-0000N-of-00003.safetensors`, index json — **no LICENSE file**

So: undeclared licence on weights derived from a base that excludes the EU, UK and
South Korea. This is the textbook laundering pattern — a permissive repo licence on
the code being read as though it covered the weights. **BLOCKED.** The widely-quoted
"FramePack is Apache-2.0, runs in 6GB" is a statement about the code only. The 6GB
figure is real and attractive; the licence is unusable.

### CogVideoX — BLOCKED

<https://huggingface.co/THUDM/CogVideoX-5b-I2V/raw/main/LICENSE> and
<https://huggingface.co/zai-org/CogVideoX1.5-5B-I2V/raw/main/LICENSE>, both
**The CogVideoX License**:

> "Under the terms and conditions of this license, the licensor hereby grants you a
> non-exclusive, worldwide, non-transferable, non-sublicensable, **revocable**,
> royalty-free copyright license."

Output clause is fine on its face:

> "The intellectual property rights of the generated content belong to the user to
> the extent permitted by applicable local laws."

Blockers are elsewhere: commercial use requires you to "register and obtain a basic
commercial license"; "the number of service users (visits) for your commercial
activities must not exceed 1 million visits per month"; and a field-of-use clause
banning applications that "undermine China's national security and national unity,
harm the public interest of society, or infringe upon the rights and interests of
human beings", plus "any military, or illegal purposes".

Three independent fails: a gate we must pass (registration), a hard traffic cap, and
a political field-of-use restriction. Plus the grant is **revocable** — unacceptable
for work already published. **BLOCKED.**

### Stable Video Diffusion — BLOCKED

<https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt/raw/main/LICENSE.md>
— **Stability AI Community License Agreement**:

> "Stability AI grants You a non-exclusive, worldwide, non-transferable,
> non-sublicensable, **revocable** and royalty-free limited license…for any
> Commercial Purpose."

> "If at any time You or Your Affiliate(s)…generate more than USD $1,000,000 in
> annual revenue…any licenses granted to You under this Agreement shall terminate."

> "As between You and Stability AI, You own any outputs generated from the Models or
> Derivative Works to the extent permitted by applicable law."

Output ownership is clean, but the grant is revocable and **auto-terminates** on
crossing $1M revenue — meaning a future success retroactively strands published
clips. **BLOCKED.** Independently, SVD-XT is a 2023-era 2B model with no text
conditioning at 576x1024; it is not a serious candidate for our look anyway.

### Mochi 1 — fails the hard I2V requirement

`genmo/mochi-1-preview` is genuine Apache-2.0 ("We're releasing the model under a
permissive Apache 2.0 license") — licence-clean, and 22GB in bf16 would fit the 24GB
laptop. But it is **text-to-video only**. Genmo listed I2V as a future update and
never shipped it in the open weights; the I2V on genmo.ai is a platform feature, not
this checkpoint. We condition on an approved still, so pure T2V is useless to us.
**NO.**

---

## Corrections to the five findings recorded in the repo

**1. Wan 2.2 recorded as Apache-2.0 — CORRECT, with two additions.**
Verified stock Apache-2.0 at the GitHub `LICENSE.txt`, and the model card explicitly
disclaims rights in generated content. Two things to add: (a) the HF repos carry the
Apache-2.0 *tag* and a README sentence but **ship no LICENSE file** — cite GitHub if
we ever need to prove the chain; (b) **there are no Wan 2.5, 2.6 or 2.7 open
weights.** I enumerated the whole `Wan-AI` org via the HF API: the newest entries are
`Wan-Dancer-14B`, `Wan2.2-Animate-14B`, `Wan2.2-S2V-14B` and the Wan 2.2 line.
Wan 2.5 shipped September 2025 as **API-only** on Alibaba Cloud and remains so; 2.6
and 2.7 marketing sites (`wan27.org` and similar) do not correspond to any weights in
the official org. Do not plan around a Wan 2.5+ local release.
New Apache-2.0 members of the family worth knowing: **`Wan2.2-S2V-14B` takes image +
audio → video**, which maps directly onto our existing Chatterbox VO manifests.

**2. `aidealab/AnimeGen-I2V` recorded as Apache-2.0, ~54GB bf16 — CORRECT, and
stronger than recorded.** Unlike Wan and AniSora, this repo **does** ship a LICENSE
file, and it is stock Apache-2.0 with **no added clauses** — no output restriction,
no commercial condition. HF tags include `commercial-use`. Base is Wan2.2-I2V-A14B
(Apache-2.0), so no laundering. Size correction: the repo totals **~114GB** across
all variants (dev transformers plus `high_noise.safetensors` / `low_noise.safetensors`),
with ~14.3GB of BF16 parameters per expert — the ~54GB figure is in the right
neighbourhood for one usable two-expert bf16 set, but the full clone is twice that.
Budget disk accordingly.

**3. LTX-Video recorded as REJECTED — PARTLY WRONG, and materially out of date.**
Three separate corrections:
- The recorded reason ("2B is research-only, GitHub LICENSE is Apache-2.0 covering
  CODE ONLY") is **correct for the 2B v0.9.x checkpoints** — those are literally
  RAIL-M, "academic or research purposes only". Verified verbatim.
- But it is **wrong as a verdict on LTX as a family.** The **13B** checkpoints
  (0.9.7 / 0.9.8) fall under the *LTXV Open Weights License 0.X*, which **permits
  commercial use free** below $10M annual revenue. "Research-only" does not describe
  them.
- And the record predates two releases. **LTX-2 (19B) shipped January 2026** and
  **LTX-2.3 (22B) shipped March 2026**, under the *LTX-2 Community License
  Agreement*: worldwide, no territory exclusion, "for any purpose", free commercial
  below $10M revenue, Licensor claims no rights in output. On Artificial Analysis
  LTX-2 ranked top-3 for image-to-video overall and **#1 among open-source models**.
  The fp8 distilled build runs in **12–16GB**, i.e. it fits *both* laptops.
  This is the strongest-quality licence-plausible model we are currently excluding.

  The real objection is **not** "research only" — it is the 20-item use-restriction
  schedule, which travels to output and collides with our CC BY 4.0 publication, the
  same structural problem we flagged for OpenRAIL. That is a governance call, so I
  have marked LTX-2/2.3 **UNCLEAR — founder call** rather than resolving it. Worth
  putting in front of Roman: the recorded rejection rests on a reason that no longer
  applies to the models we would actually want to use.

**4. HunyuanVideo recorded as REJECTED on EU/UK/South Korea territory exclusion —
CORRECT, verbatim confirmed, and extend it.** The clause is identical in
`HunyuanVideo-I2V` and in **`HunyuanVideo-1.5`** (8.3B, November 2025), which is the
one being pushed hard in 2026 roundups and is repeatedly mis-described as Apache-2.0.
It is not. Also extend the rejection to **FramePack**, whose weights are a
HunyuanVideo derivative with no licence declared at all — worth naming explicitly in
our records, because FramePack's Apache-2.0 code licence and its 6GB VRAM figure make
it the single most likely thing for someone to adopt by mistake.

**5. OpenRAIL/OpenRAIL++ recorded as structurally incompatible with our CC BY 4.0 —
CORRECT, and the principle now catches more than we listed.** The LTX-Video 2B
licence *is* RAIL-M, and its output clause is the exact mechanism we objected to:
"No use of the Output can contravene any provision as stated in the License." The
same structure, in friendlier packaging, is what makes LTX-2/2.3 UNCLEAR rather than
SHIP-SAFE. Recommend generalising the recorded rule from "OpenRAIL is a problem" to
"any licence that conditions *output* use is a problem, whatever it is called" — that
formulation catches RAIL-M, the LTX schedules and CogVideoX in one test.

## Additional laundering flags found

Checked specifically because HF tags and LICENSE files disagree so often:

- **`lllyasviel/FramePackI2V_HY`** — worst case in the field. No licence tag, no
  LICENSE file, Hunyuan-derived weights. The Apache-2.0 everyone quotes is the code repo.
- **`IndexTeam/Index-anisora` V1 / `5B` / `5B_RL`, and the third-party
  `Disty0/Index-anisora-5B-diffusers`** — declare `apache-2.0` over a **CogVideoX-5B**
  base whose own licence is non-Apache, revocable, and registration-gated for
  commercial use. Bilibili's Apache-2.0 grant on V2/V3 is fine (Wan base); the 5B line
  is not. Use V3.2, not 5B.
- **`IamCreateAI/Ruyi-Mini-7B`** — Apache-2.0, and I chased the chain because the card
  says the transformer is "inherited from HunyuanDiT". Resolved **clean**: the direct
  base is `alibaba-pai/EasyAnimateV4-XL-2-InP`, which is itself Apache-2.0 ("This
  project is licensed under the Apache License (Version 2.0)"), and the HunyuanDiT
  relationship is *architectural*, not a weight inheritance. Separately, the
  HunyuanDiT licence I fetched grants "non-exclusive, worldwide" with **no** territory
  exclusion — that clause was added later for HunyuanVideo, not present in HunyuanDiT.
  Ruyi stands as SHIP-SAFE.
- **`zai-org` / `THUDM` CogVideoX** — HF tag is `license: other`, and multiple 2026
  blog roundups (including ones ranking models for RTX 5090) assert CogVideoX is
  Apache-2.0. **False.** Only the *CogVideoX-2B* T2V module is Apache-2.0; every 5B
  variant including both I2V models is under the CogVideoX License. Do not trust the
  secondary sources here.
- **Kandinsky 5.0** — blogs say Apache-2.0; it is actually **MIT**, i.e. *more*
  permissive than reported. Tag and LICENSE file agree. A rare case of the metadata
  understating our position.
- **`QuantStack/Wan2.2-I2V-A14B-GGUF`** and `bullerwins/…-GGUF` — declare `apache-2.0`
  over an Apache-2.0 base. Clean; quantisations of Wan are safe to use.

## Practical notes on fitting these in 24GB and 12GB

- **Wan 2.2 A14B is a two-expert MoE** (`high_noise_model` / `low_noise_model`). The
  experts run sequentially, so peak VRAM is roughly *one* expert, not both. That is
  why the authors' "80GB" figure and the community's 12GB reality both hold. GGUF per
  expert: Q2_K 5.3GB, Q3_K_M 7.18GB, Q4_K_S 8.75GB, Q4_K_M 9.65GB, Q5_K_M 10.8GB,
  Q6_K 12GB, Q8_0 15.4GB. Q4_K_S fits 12GB with room for the VAE; Q8_0 fits 24GB.
- Add the text encoder to any Wan budget: `models_t5_umt5-xxl-enc-bf16.pth` is
  **11.4GB** and the Wan 2.2 VAE is 2.82GB. On 12GB these must be CPU-offloaded
  between stages, not co-resident.
- **AnimeGen-I2V inherits Wan 2.2's architecture exactly**, so every Wan 2.2 A14B
  memory trick, quantisation and offload path applies to it unchanged. That is the
  main practical argument for it over anything else anime-specific.
- Authors' minimum-VRAM claims in the table above are unoptimised single-GPU figures
  and are systematically pessimistic by 3–6x versus quantised community pipelines.
  Treat them as an upper bound, not a requirement.

## Ranked recommendation

**12GB (RTX 5070 Ti laptop) — SHIP-SAFE only:**

1. `IndexTeam/Index-anisora` **V3.2** — anime-native, Wan2.2 base, 8-step inference,
   V3.1 shipped a 12GB build. Apache-2.0. Best answer to "Wan isn't made for anime style".
2. `QuantStack/Wan2.2-I2V-A14B-GGUF` **Q4_K_S** (8.75GB/expert) — known-good baseline,
   same recipe surface as our current work.
3. `kandinskylab/Kandinsky-5.0-I2V-Lite-5s` — 2B, **MIT**, cleanest licence of all;
   lowest ceiling on quality.
4. `Wan-AI/Wan2.2-TI2V-5B` — ~10GB bf16 transformer, authors target a 4090.
5. `IamCreateAI/Ruyi-Mini-7B` — anime/game-tuned, but 21.5GB even at 360x480; needs
   `low_gpu_memory_mode`. Marginal at 12GB.

**24GB (RTX 5090 laptop) — SHIP-SAFE only:**

1. `aidealab/AnimeGen-I2V` — anime-native Wan 2.2 finetune, stock Apache-2.0 with a
   real LICENSE file, `commercial-use` tagged, drop-in for our Wan tooling. Top pick.
2. `IndexTeam/Index-anisora` **V3.2** — second anime-native option; 8 steps is a large
   speed win for the iterate-in-minutes loop.
3. `Wan-AI/Wan2.2-I2V-A14B` at fp8 / Q8_0 (15.4GB per expert) — the control baseline.
4. `Wan-AI/Wan2.2-S2V-14B` — image + audio → video. Apache-2.0. Directly consumes the
   VO we already synthesise; worth a canary on lip-sync-driven beats.
5. `kandinskylab/Kandinsky-5.0-I2V-Lite-5s` — MIT, "24GB with offloading".
6. `hpcai-tech/Open-Sora-v2` — Apache-2.0 and fully transparent, but 44GB+ peak and
   weaker output than Wan. Include for completeness, not for production.

**Excluded but worth a founder decision:** `Lightricks/LTX-2.3` (fp8 distilled,
12–16GB, fits both machines, #1 open-source on Artificial Analysis I2V, native
synchronised audio). Licence permits commercial use free below $10M revenue and
claims no rights in output; the blocker is a use-restriction schedule that travels to
output and collides with CC BY 4.0. Same structural objection as OpenRAIL — and the
reason recorded in our repo for rejecting LTX no longer applies to it.

## Sources

- <https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B>
- <https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/LICENSE.txt>
- <https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B/tree/main>
- <https://huggingface.co/Wan-AI/Wan2.2-S2V-14B>
- <https://huggingface.co/Wan-AI/Wan-Dancer-14B>
- <https://huggingface.co/api/models?author=Wan-AI>
- <https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF>
- <https://huggingface.co/aidealab/AnimeGen-I2V> and `/raw/main/LICENSE`
- <https://github.com/bilibili/Index-anisora>
- <https://huggingface.co/IndexTeam/Index-anisora>
- <https://huggingface.co/kandinskylab/Kandinsky-5.0-I2V-Lite-5s>
- <https://raw.githubusercontent.com/kandinskylab/kandinsky-5/main/LICENSE>
- <https://huggingface.co/IamCreateAI/Ruyi-Mini-7B>
- <https://huggingface.co/alibaba-pai/EasyAnimateV4-XL-2-InP>
- <https://huggingface.co/hpcai-tech/Open-Sora-v2>
- <https://huggingface.co/stepfun-ai/stepvideo-ti2v>
- <https://huggingface.co/nvidia/Cosmos-Predict2.5-2B>
- <https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/>
- <https://raw.githubusercontent.com/Lightricks/LTX-2/main/LICENSE>
- <https://huggingface.co/Lightricks/LTX-2.3>
- <https://huggingface.co/Lightricks/LTX-Video/raw/main/LTX-Video-Open-Weights-License-0.X.txt>
- <https://huggingface.co/Lightricks/LTX-Video/raw/main/ltx-video-2b-v0.9.1.license.txt>
- <https://huggingface.co/api/models?author=Lightricks>
- <https://huggingface.co/tencent/HunyuanVideo-I2V/raw/main/LICENSE>
- <https://huggingface.co/tencent/HunyuanVideo-1.5/raw/main/LICENSE>
- <https://huggingface.co/Tencent-Hunyuan/HunyuanDiT/raw/main/LICENSE.txt>
- <https://huggingface.co/api/models/lllyasviel/FramePackI2V_HY>
- <https://github.com/lllyasviel/FramePack>
- <https://huggingface.co/THUDM/CogVideoX-5b-I2V/raw/main/LICENSE>
- <https://huggingface.co/zai-org/CogVideoX1.5-5B-I2V/raw/main/LICENSE>
- <https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt/raw/main/LICENSE.md>
- <https://huggingface.co/genmo/mochi-1-preview>
- <https://huggingface.co/Skywork/SkyReels-V3-R2V-14B>
- <https://huggingface.co/Skywork/SkyReels-V2-I2V-14B-720P>
- <https://github.com/SkyworkAI/SkyReels-V3>
- <https://ltxworkflow.com/resources/community/ltx-23-vram-requirements-12gb-16gb-24gb> (secondary, VRAM only)

---

# PRIORITY: the Wan2.2-TI2V-5B-Turbo 4-step licence chain

Resolved 2026-08-04 at the team lead's request, ahead of the rest of the survey.
Question: may we render with a 4-step Self-Forcing Turbo distill of Wan2.2-TI2V-5B
and publish the output under CC BY 4.0?

## Overall verdict: BLOCKED at link 1. Do not use any Turbo build.

**Our `pipeline/vet_model.py` gate is CORRECT and is CONFIRMED, not overturned.**
The non-commercial link is **link 1 — the original distill itself**
(`quanhaol/Wan2.2-TI2V-5B-Turbo`), which is **CC BY-NC-SA 4.0**. The gate's verdict
on the GGUF ("hard-fail — laundering an NC base") names the right problem; the only
refinement is that the laundering starts one link earlier than the GGUF. Every
downstream repo — diffusers conversion, both GGUF builds — inherits the NC and the
ShareAlike from this file, and none of them can cure it.

Note the base model is fine. `Wan-AI/Wan2.2-TI2V-5B` is Apache-2.0 (see the Wan
section above). The distill authors took an Apache-2.0 base and released their
*derivative* under a more restrictive licence, which Apache-2.0 permits them to do.
Nothing is wrong upstream; the restriction is added at the distill.

### Link 1 — `github.com/quanhaol/Wan2.2-TI2V-5B-Turbo` — **BLOCKED**

Fetched 2026-08-04 via `gh api repos/quanhaol/Wan2.2-TI2V-5B-Turbo/contents/LICENSE.md`.
Repo created 2025-08-06, last pushed 2026-03-15.

Two signals to note before the text. The licence file is **`LICENSE.md`, not `LICENSE`**
— a plain fetch of `/main/LICENSE` returns 404, which is how this gets missed. And
GitHub's own licence detector reports:

```
"license": {"key": "other", "name": "Other", "spdx_id": "NOASSERTION"}
```

`NOASSERTION` means GitHub could not match the file to a standard SPDX licence — the
repo does **not** show an "Apache-2.0" badge, and anyone assuming it inherits the
base model's Apache-2.0 is guessing.

The file is the full text of **Creative Commons Attribution-NonCommercial-ShareAlike
4.0 International**. Title line, verbatim:

> "# Attribution-NonCommercial-ShareAlike 4.0 International"

Governing grant, Section 2(a)(1), verbatim:

> "Subject to the terms and conditions of this Public License, the Licensor hereby
> grants You a worldwide, royalty-free, non-sublicensable, non-exclusive, irrevocable
> license to exercise the Licensed Rights in the Licensed Material to:
>
> A. reproduce and Share the Licensed Material, in whole or in part, **for
> NonCommercial purposes only**; and
>
> B. produce, reproduce, and Share Adapted Material **for NonCommercial purposes
> only**."

Definition of NonCommercial, Section 1(k), verbatim:

> "__NonCommercial__ means not primarily intended for or directed towards commercial
> advantage or monetary compensation."

Definition of License Elements, Section 1(g), verbatim:

> "The License Elements of this Public License are Attribution, NonCommercial, and
> ShareAlike."

URL: <https://github.com/quanhaol/Wan2.2-TI2V-5B-Turbo/blob/main/LICENSE.md>

**Why this blocks us twice over — the ShareAlike is the part that leaves no room.**

1. **NonCommercial.** banyan-city publishes to TikTok and its own site and is
   explicitly commercially-adjacent. The grant covers reproducing the Licensed
   Material only for NonCommercial purposes, and *loading the weights to render is
   reproduction*. This is not merely a restriction on redistributing the weights; it
   restricts the act of use. Private commercial rendering is outside the grant too.

2. **ShareAlike, and this is decisive independently of the NC clause.** BY-NC-SA
   requires Adapted Material to be licensed under BY-NC-SA or a "BY-NC-SA Compatible
   License" (Section 1(c)). **CC BY 4.0 is not on the Creative Commons compatible-licenses
   list and cannot be** — a compatible licence must itself carry NonCommercial and
   ShareAlike. So even if we argued the NC clause away, we still could not publish
   downstream under CC BY 4.0, which is exactly what our provenance model does. The
   two licences are directly opposed: CC BY 4.0 grants recipients commercial use;
   BY-NC-SA forbids us from granting it.

There is a genuine legal grey area about whether *generated video* is "Adapted
Material" of the weights at all. I am not resolving it and we should not rely on it:
the NC clause independently reaches the act of rendering, we would be betting a
published, monetised series on an untested theory, and STEWARDSHIP.md §7.2 requires
us to publish the model in each clip's leaf yaml — so the claim would be made in
public, in writing, on every affected clip.

The README compounds the problem rather than helping. Fetched 2026-08-04 from
<https://raw.githubusercontent.com/quanhaol/Wan2.2-TI2V-5B-Turbo/main/README.md>: it
contains **no licence statement at all**, and acknowledges building on
**Self-Forcing, Self-Forcing-Plus, CausVid, MagicMotion, Wan2.1 and Wan2.2**. The
authors ask for citation of their MagicMotion paper (arXiv:2503.16421). CausVid in
particular has its own upstream terms, so even a hypothetical relicensing by the
Fudan authors would not obviously clear the whole stack. Not worth chasing while
link 1 is NC.

### Link 2 — `huggingface.co/yetter-ai/Wan2.2-TI2V-5B-Turbo-Diffusers` — **BLOCKED**

Confirmed as reported: **no licence declared.** See the next tool call for the
tree/API check. What "no licence declared" means for us, stated plainly, because it
is the crux of the redistributor question:

**An undeclared licence is not a permissive licence, and it does not reset the
chain.** Two things are true simultaneously and both are bad:

- The **weights remain governed by link 1's CC BY-NC-SA 4.0.** A redistributor cannot
  enlarge rights it never held. Silence changes nothing about what we may do — we
  still face NC + SA.
- The **redistribution itself is unlicensed to us.** Under BY-NC-SA §3(a) a
  downstream sharer must attach the licence text and attribution; omitting it means
  the redistributor is out of compliance, and we receive no grant *from them* at all.
  So we would be relying on a chain whose middle link is itself in breach.

The practical upshot: link 2 is strictly worse than link 1, not better. A missing
licence is the single most common way an NC base gets laundered into a repo that
*looks* clean, and it is why a `license:` tag must never be trusted over the
upstream chain.

### Link 3 — the GGUF builds — **BLOCKED** (our gate confirmed)

`hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF` and `Kiijoku/Wan2.2-TI2V-5B-Turbo-GGUF`.
See the following tool calls for current-state verification. Quantisation is a
mechanical transformation of the weights; it produces Adapted Material under
BY-NC-SA §1(a) and carries NC + SA forward unchanged. Whatever either repo declares
in its `license:` tag, **the tag cannot be correct if it is more permissive than
CC BY-NC-SA 4.0**, because neither uploader is the licensor of link 1.

`pipeline/vet_model.py`'s classification of `hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF` as
"hard-fail — laundering an NC base" (verified live 2026-08-02) is **upheld**.

### Link 4 — `huggingface.co/lightx2v/Wan2.2-Lightning` — see below

Lower priority per the request, and moot for us while we are on TI2V-5B: Lightning
is A14B-only. Checked for the LICENSE.txt-vs-prose discrepancy; result recorded below.

## Fallback: how to get the speedup without the licence

The 3.5x is not worth a licence breach, and it is not the only route to it. In
descending order of confidence:

1. **`IndexTeam/Index-anisora` V3.2 — Apache-2.0, and it is already an 8-step model.**
   This is the best answer by a wide margin: it gets most of the step reduction
   *natively*, it is trained on Wan 2.2, and it is anime-native, which is the founder's
   actual complaint about Wan ("its not made for anime style"). One recipe change, two
   problems solved, licence clean. Sample one beat before any batch.
2. **`lightx2v/Wan2.2-I2V-A14B-Moe-Distill-Lightx2v`** and the Lightning LoRAs — same
   family of step-distillation trick, but check each one's chain the same way; only
   worth it if we move to A14B, where AnimeGen-I2V also lives.
3. **Ordinary step-count tuning on stock Apache-2.0 Wan2.2-TI2V-5B.** Our own step
   sweep on 2026-08-03 (steps-06/10/14/20) already established this axis empirically —
   the licence-clean floor may be lower than 14 without any distill.
4. Do not pursue: any Turbo build, under any repo name, at any quantisation.

If someone wants the Turbo recipe specifically, the only clean path is asking the
Fudan authors (liqh24@m.fudan.edu.cn, zhenxingfd@gmail.com, wangrui21@m.fudan.edu.cn)
to dual-licence, and even then CausVid's upstream terms would need checking. That is
a founder-reserved outbound contact, not a steward action.

## Link-by-link verification data (all fetched 2026-08-04)

Queried `https://huggingface.co/api/models/<repo>` directly and inspected
`cardData.license`, the `license:` tags, and the full `siblings` file list.

| Repo | Declares | LICENSE file in tree? | Last modified | Verdict |
|---|---|---|---|---|
| `quanhaol/Wan2.2-TI2V-5B-Turbo` (HF weights) | **nothing** | **none** | 2025-08-23 | **BLOCKED** |
| `github.com/quanhaol/Wan2.2-TI2V-5B-Turbo` (code) | CC BY-NC-SA 4.0 in `LICENSE.md`; GitHub reports `NOASSERTION` | yes (`LICENSE.md`) | 2026-03-15 | **BLOCKED** |
| `Kijai/WanVideo_comfy` (conversion source) | **nothing** | none relevant | — | **BLOCKED** |
| `yetter-ai/Wan2.2-TI2V-5B-Turbo-Diffusers` | **nothing** | **none** | 2025-11-12 | **BLOCKED** |
| `hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF` | `apache-2.0` | **none** | 2025-12-19 | **BLOCKED** (laundering) |
| `Kiijoku/Wan2.2-TI2V-5B-Turbo-GGUF` | `apache-2.0` | **none** | 2026-04-27 | **BLOCKED** (laundering) |
| `lightx2v/Wan2.2-Lightning` | `apache-2.0` | **none on HF**; `LICENSE.txt` on GitHub | 2025-11-13 | **SHIP-SAFE** w/ caveat |

### Link 2 confirmed — `yetter-ai/Wan2.2-TI2V-5B-Turbo-Diffusers` declares nothing

`cardData.license: None`, zero `license:` tags, and the only `.md` in the tree is
`README.md` — **no LICENSE file**. Confirmed exactly as reported.

Worth recording: **the authors' own HF weights repo, `quanhaol/Wan2.2-TI2V-5B-Turbo`,
also declares nothing** — no tag, no LICENSE file. The CC BY-NC-SA 4.0 exists *only*
in the GitHub repo, in a file named `LICENSE.md` that a fetch of `/main/LICENSE`
misses with a 404. So a reviewer working from HuggingFace alone sees an unlicensed
5B Wan derivative and has every temptation to assume it inherits the base's
Apache-2.0. That is the trap, and it is why the GitHub side must be checked.

### Link 3 confirmed — both GGUF repos launder, and they are the same repo twice

Both declare, in front matter that simultaneously names the NC base:

```yaml
license: apache-2.0
base_model:
- quanhaol/Wan2.2-TI2V-5B-Turbo
pipeline_tag: image-to-video
```

Neither ships a LICENSE file. `Kiijoku/Wan2.2-TI2V-5B-Turbo-GGUF` is a **verbatim
clone** of `hum-ma`'s card, down to the prose and the Civitai links — so it is not
independent corroboration of the Apache-2.0 claim, it is the same error copied. The
Kiijoku copy is the more recently touched of the two (2026-04-27), so age is no guide.

Both were converted not from the original but from
`Kijai/WanVideo_comfy/Wan22-Turbo/Wan2_2-TI2V-5B-Turbo_fp16.safetensors` — a fourth
link, which **also declares no licence** (`cardData.license: None`, no license tag;
the sole LICENSE file in that repo covers an unrelated Ditto LoRA). The chain is
therefore: Apache-2.0 base → **CC BY-NC-SA 4.0 distill** → unlicensed fp16 repack →
unlicensed/`apache-2.0`-declared GGUF. The Apache-2.0 reappears at the far end with
no act of relicensing anywhere in between, by parties who never held the right to
grant it.

`pipeline/vet_model.py`'s hard-fail on `hum-ma/Wan2.2-TI2V-5B-Turbo-GGUF` is
**upheld**. Two refinements for the gate, both cheap:

- Add `Kiijoku/Wan2.2-TI2V-5B-Turbo-GGUF`, `yetter-ai/Wan2.2-TI2V-5B-Turbo-Diffusers`
  and `Kijai/WanVideo_comfy` (Wan22-Turbo path) to the same hard-fail class.
- When resolving a licence from GitHub, glob `LICENSE*` rather than fetching `LICENSE`.
  A 404 on `LICENSE` is not evidence of absence — it is how this one hides. Treat
  GitHub's `spdx_id: NOASSERTION` as a hard-fail signal in its own right.

The pull here is real and should be named: these GGUFs run in **4GB of VRAM** at 4
steps and the card recommends exactly the 704x1280 we use. That is the most tempting
thing in this entire audit, and it is unusable.

### Link 4 answered — `lightx2v/Wan2.2-Lightning`: no LICENSE on HF, but Apache-2.0 verified on GitHub

Direct answer to the question asked: **`LICENSE.txt` does not exist in the HF repo
tree.** The full `siblings` list contains no licence file of any kind; the
`apache-2.0` on the card is metadata plus front matter only. Same paper-trail
weakness as Wan itself.

But the chain is sound, unlike Turbo's. `github.com/ModelTC/Wan2.2-Lightning` **does**
ship `LICENSE.txt`, and GitHub's licence detector resolves it to **`Apache-2.0`** —
not `NOASSERTION`. Declared base models are `Wan-AI/Wan2.2-T2V-A14B`,
`Wan-AI/Wan2.2-I2V-A14B` and `Wan-AI/Wan2.2-TI2V-5B`, all Apache-2.0. An Apache-2.0
distill of Apache-2.0 bases is internally consistent and involves no expansion of
rights. **SHIP-SAFE**, with the same "cite GitHub, not HF" caveat we apply to Wan.

**Correction to the framing of the question: Lightning is not A14B-only, and it is not
moot.** The file tree contains an image-to-video variant —

```
Wan2.2-I2V-A14B-4steps-lora-rank64-Seko-V1
```

— alongside five T2V-A14B builds. It is a **rank-64 LoRA, 4 steps, no CFG**, claiming
~20x speed-up. `Wan2.2-TI2V-5B` is listed as a declared base model but has no weights
in the tree yet, so there is currently no 5B Lightning build.

This changes the recommendation materially.

## Revised fallback: the speedup is available licence-clean

Supersedes the fallback list written above for this section.

1. **`lightx2v/Wan2.2-Lightning` → `Wan2.2-I2V-A14B-4steps-lora-rank64-Seko-V1`.**
   Same 4-step, CFG-free trick as Turbo, same speed class, **Apache-2.0 with a
   GitHub-verified LICENSE.txt**. It is a LoRA over Wan2.2-I2V-A14B — which is also
   AnimeGen-I2V's base — so it plausibly stacks with our top-ranked 24GB anime model.
   Two caveats before anyone gets excited: LoRA-over-finetune stacking is empirical,
   not guaranteed, and this pushes us to A14B, which is the 24GB machine only. Sample
   one beat.
2. **`IndexTeam/Index-anisora` V3.2 — Apache-2.0, natively 8 steps, anime-native,
   Wan2.2 base.** Still the best single move available: it addresses the founder's
   actual complaint ("wan 2.2 is still pretty good, the problem is its not made for
   anime style") *and* most of the step count, with the cleanest licence of the three.
   V3.1 shipped a 12GB build, so unlike option 1 it serves both laptops.
3. **Step-count tuning on stock Apache-2.0 `Wan2.2-TI2V-5B`.** Our own sweep on
   2026-08-03 (steps-06/10/14/20) already probed this axis; the licence-clean floor
   may be below 14 with no distill at all. Zero new licence surface.
4. **Do not use any Turbo build**, under any repo name, at any quantisation, from any
   uploader. The NC is upstream of all of them.

Per ONE SAMPLE BEFORE ANY BATCH: each of options 1–3 is a *recipe change*, so each
needs one beat rendered and looked at before it goes near fifteen.

---

# The FastWan 3-step LoRA (ACTION-PLAN T5) — verdict: SHIP-SAFE, with the download source named

**Researched 2026-08-07**, live against the HF and GitHub JSON APIs, for
`t5-fastwan-licence-1786090200`. T5's rule was that the LoRA may not be
DOWNLOADED until this clears. It clears.

## Overall verdict: SHIP-SAFE at the origin. Take the weights from the authors, or record the mirror's sha256.

The short version, because it is the opposite of the Turbo chain and the
difference matters: **Turbo was BLOCKED because its origin is NonCommercial.
FastWan's origin is Apache-2.0 and grants everything we need.** What is imperfect
here is only the paper trail between the authors and the file our recipe points
at — a hygiene defect belonging to the redistributors, not a restriction on us.

Exactly the pattern
[Lightning set](#link-4-answered--lightx2vwan22-lightning-no-license-on-hf-but-apache-20-verified-on-github):
HF metadata says `apache-2.0` with no LICENSE file in the tree; the authors'
GitHub repo ships the real text. Both surfaces were checked, as that precedent
requires.

## Link 1 — `FastVideo/FastWan2.2-TI2V-5B-FullAttn-Diffusers`, the origin — **SHIP-SAFE**

<https://huggingface.co/FastVideo/FastWan2.2-TI2V-5B-FullAttn-Diffusers>

`cardData.license: apache-2.0`, tag `license:apache-2.0`, `gated: False`, 60,733
downloads, last modified 2025-11-25. The full `siblings` list — 24 files, 24.2GB
— contains **no LICENSE file of any kind**, and the card declares no
`repository` field. On HF alone this is a tag with nothing behind it.

The README links `github.com/hao-ai-lab/FastVideo` four times as the authors' own
project. That repo **does** ship `LICENSE`, 10757 bytes, and GitHub's detector
resolves it to `spdx_id: Apache-2.0` — *not* `NOASSERTION`, the signal that
exposed Turbo.

<https://raw.githubusercontent.com/hao-ai-lab/FastVideo/main/LICENSE>:

> "Apache License
> Version 2.0, January 2004
> http://www.apache.org/licenses/"

Diffed against `apache.org/licenses/LICENSE-2.0.txt` rather than eyeballed. The
**operative sections 1–9 are whitespace-normalised identical** (10107 characters
each). The only difference in the whole file is 561 characters of the APPENDIX
*boilerplate template* — the "Copyright [yyyy] [name of copyright owner]…" notice
you are meant to paste into your own source files — which upstream truncated.
That is instructions for applying the licence, not terms. **Nothing added, no
clause removed:** no output clause, no NonCommercial, no ShareAlike, no
territory, no field-of-use, no acceptable-use schedule. Apache-2.0 is silent
about output, which is the reason it passes, not any affirmative grant.

The README carries no restrictive prose either — grepped for
commercial/research/restrict/prohibit and the only hit is *"If you use the
FastWan2.2-TI2V-5B-FullAttn-Diffusers model for your research, please cite our
paper"*. A citation request is not a licence condition.

**Base chain, and it is the cleanest possible for us.** The `base_model` metadata
field is empty — the hygiene caveat `vet_model.py`'s docstring already names
FastWan for — but the card prose states it: *"FastWan2.2-TI2V-5B-Full-Diffusers
is built upon Wan-AI/Wan2.2-TI2V-5B-Diffusers."* That is **our own production
base**, Apache-2.0, already SHIP-SAFE in the table above and already inside a
published episode. An Apache-2.0 distill of an Apache-2.0 base expands nobody's
rights and is internally consistent.

Now vendored, per the remedy `vet_model.py` had already written down for this
exact repo: `licences/FastVideo-FastWan-LICENSE.txt`, sha256
`5c7f173199fd7fb3cc83d86d24f3541e8ae0cb8c16e912ca519ed6a1435bd8f3`. The tool
moved `UNVERIFIABLE → CLEAR` as a result, and its self-test expectation moved
with it (11/11). Delete the vendored file and it reverts — the rule was
satisfied, not loosened.

## Link 2 — `DeepBeepMeep/Wan2.2`, what the recipe actually downloads — **unlicensed mirror**

The ACTION-PLAN T5 recipe comes from Wan2GP's `defaults/ti2v_2_2_fastwan.json`,
and that file's `loras` entry is a single hard URL, fetched live:

```json
"loras": ["https://huggingface.co/DeepBeepMeep/Wan2.2/resolve/main/loras_accelerators/Wan2_2_5B_FastWanFullAttn_lora_rank_128_bf16.safetensors"]
```

So the bytes T5 would put on the 5090 come from **neither FastVideo nor Wan-AI**.
`DeepBeepMeep/Wan2.2` declares:

- **no `license` in `cardData`, no `license:` tag** — nothing at all;
- **no LICENSE file** — the only `.md` among its 130 files is `README.md`;
- `base_model: ["Wan-AI/Wan2.2-T2V-A14B"]`, which is **the wrong base** for a 5B
  TI2V LoRA — a repo-wide default, not a statement about this file;
- a README that is a WanGP feature list, and a `loras_accelerators/readme.txt`
  whose entire contents are the two words `loras accelerators`.

`vet_model.py DeepBeepMeep/Wan2.2` → **UNVERIFIABLE**, correctly.

`Kijai/WanVideo_comfy` holds the same file at `FastWan/`. It is **byte-identical**
— both copies report LFS sha256
`79290493711b022e1c6e655d803715cd8a91a75cdb139856cad46f354e2f681c`, 660,874,456
bytes — established from the `paths-info` API **without downloading anything**.
Two mirrors of one artifact, not two independent sources, which is the same trap
the twin Turbo GGUFs set. Kijai declares no licence either (its sole LICENSE file
covers an unrelated Ditto LoRA) and its README's "Other model sources" list
credits nine upstreams — **hao-ai-lab/FastVideo is not among them**.

**Why this is a caveat and not a block.** Nobody in this chain claims *more* than
upstream granted; they claim nothing. Apache-2.0 §2 grants a perpetual,
irrevocable licence to reproduce and prepare derivative works, directly from the
Licensor to every recipient. A redistributor omitting the LICENSE is failing
their own §4 obligations — it does not withdraw the grant that reaches us from
FastVideo. That is the structural inverse of Turbo, where the restriction was
upstream of every mirror and no downstream repackaging could clean it.

**What is genuinely unproven:** that this 630MB rank-128 file is a mathematical
extract of FastVideo's checkpoint. The evidence is naming, Wan2GP's own
description, and kijai's known practice — and this repo has been bitten before by
provenance-by-naming ("permission does not travel by names looking alike",
`vet_model.py`). Circumstantial support: kijai's merged
`Wan2_2-TI2V-5B-FastWanFullAttn_bf16.safetensors` is 9,999,659,744 bytes against
FastVideo's own `transformer/diffusion_pytorch_model.safetensors` at
9,999,660,080 — **336 bytes apart**, i.e. the same tensor budget with a rewritten
safetensors header. Consistent with a repack. Not proof.

Two clean ways to close it, both $0:

1. **Download the transformer from FastVideo's own repo** (10.00GB) instead of the
   630MB mirror. No third-party link at all, and it is the *same* 5B architecture
   we already run. Costs disk and download time, buys a complete chain.
2. **Use the mirror and record `sha256:79290493…` in the clip sidecar** alongside
   the model string. The artifact becomes identifiable forever and the gap is
   published rather than hidden — which is what §7.2 is for.

Either satisfies the gate. Neither needs the founder.

## What `licence_gate.py` says about the string the render would record — and a hole it exposes

Run against the classifier live. Our sidecars take the shape
`model: Wan-AI/Wan2.2-TI2V-5B-Diffusers` (see `bench-T1T2T3/*.meta.yaml`), so a
T5 clip would record the base plus the LoRA. Every candidate form resolves the
same way:

| string fed to `model_licences()` | resolves as | verdict |
|---|---|---|
| `Wan-AI/Wan2.2-TI2V-5B-Diffusers` | `[('wan', 'Apache-2.0')]` | allow |
| `Wan-AI/Wan2.2-TI2V-5B-Diffusers + FastVideo/FastWan2.2-TI2V-5B-FullAttn LoRA rank128 bf16 (via DeepBeepMeep/Wan2.2)` | `[('wan', 'Apache-2.0')]` | allow |
| `FastVideo/FastWan2.2-TI2V-5B-FullAttn-Diffusers` | `[('wan', 'Apache-2.0')]` | allow |
| `Wan2_2_5B_FastWanFullAttn_lora_rank_128_bf16.safetensors` | `[('wan', 'Apache-2.0')]` | allow |
| `fastwan` | `[('wan', 'Apache-2.0')]` | allow |

The verdict is right and **the reasoning is not**. `MODEL_LICENCES` matching is
substring-based, and `"wan"` is a substring of `"fastwan"` — so the gate allows
the LoRA on an accident of spelling, having read nothing about it. The bare word
`fastwan`, naming no Wan-AI repo whatsoever, comes back Apache-2.0.

This is precisely the failure the table's own `voxcpm2` comment warns about — *"a
new release inherits the licence of any allowed model whose name is a prefix of
its own… the direction that bites is always allow-by-inheritance"* — and it is
worse when the accident agrees with the truth, because nothing ever surfaces it.
Contrast `quanhaol/Wan2.2-TI2V-5B-Turbo`, which also contains `wan` but is caught:
its explicit `quanhaol` key is non-allow, and `engine_licence()` returns the
worst clause. **The explicit key is the only thing doing the work**, and FastWan
has none.

Adding one is R4 — `vet_model.py` is explicit that editing
`licence_gate.MODEL_LICENCES` is a human decision, and this check does not make
it. Recorded here as the finding it is. The safe reading in the meantime: a T5
sidecar passes the gate, but it passes on the base's licence, so the sidecar must
name the LoRA and its source explicitly for the provenance to mean anything.

## Sources (all fetched 2026-08-07)

- <https://huggingface.co/api/models/FastVideo/FastWan2.2-TI2V-5B-FullAttn-Diffusers>
- <https://huggingface.co/FastVideo/FastWan2.2-TI2V-5B-FullAttn-Diffusers/raw/main/README.md>
- <https://api.github.com/repos/hao-ai-lab/FastVideo>
- <https://raw.githubusercontent.com/hao-ai-lab/FastVideo/main/LICENSE>
- <https://www.apache.org/licenses/LICENSE-2.0.txt> (canonical, for the diff)
- <https://raw.githubusercontent.com/deepbeepmeep/Wan2GP/main/defaults/ti2v_2_2_fastwan.json>
- <https://huggingface.co/api/models/DeepBeepMeep/Wan2.2>
- <https://huggingface.co/DeepBeepMeep/Wan2.2/raw/main/loras_accelerators/readme.txt>
- <https://huggingface.co/api/models/Kijai/WanVideo_comfy>
- <https://huggingface.co/Kijai/WanVideo_comfy/raw/main/README.md>
- `paths-info` API on all three repos, for LFS sha256 without downloading weights
