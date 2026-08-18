# CFG in video diffusion: motion, temporal behaviour, and whether negative prompts do anything

External research, 2026-08-18. Every claim tagged **[DEM]** (paper, benchmark table,
shipped source code, or maintainer statement) or **[FOLK]** (bare forum/blog comment,
no evidence attached). Source code counts as DEM: it is what actually runs.

---

## 0. TL;DR for our pipeline

1. **CFG=1 means the negative prompt is not merely weak — it is never evaluated.**
   Proven in three independent codebases (ComfyUI, LTX-Video, diffusers). If we run any
   distilled / Lightning / CausVid / few-step recipe, every negative prompt in our job
   specs is dead text. **[DEM]**
2. **Vendors ship CFG *schedules*, not constant CFG.** LTX-Video 13B's production config
   is `guidance_scale: [1, 1, 6, 8, 6, 1, 1]` over timesteps — guidance OFF at the start,
   OFF at the end, spiking in the middle. That is the Kynkäänniemi "guidance interval"
   result, shipped. **[DEM]**
3. **Wan 2.2 applies a different CFG to each MoE expert** — `(3.0, 4.0)` = low-noise 3.0,
   high-noise 4.0. Confirmed in the sampling loop. **[DEM]**
4. **Wan's default negative prompt is a motion *booster*.** It contains three separate
   anti-static terms. Translating it to English is the folk-warned failure mode. **[DEM]**
   for the content, **[FOLK]** for "keep it in Chinese".
5. Evidence that raising CFG specifically *freezes* video is **weaker than the folklore
   suggests** — see §1.4. The strongest measured claim is about I2V and image conditioning,
   not text CFG scale.

---

## 1. CFG scale and motion

### 1.1 Official recommended guidance values (all from shipped config/source)

| Model | Recommended CFG | Source | Notes |
|---|---|---|---|
| Wan 2.1 (all tasks) | **5.0** | [`generate.py` arg default](https://github.com/Wan-Video/Wan2.1/blob/main/generate.py) | single scalar, `--sample_guide_scale` default 5.0 |
| Wan 2.2 T2V-A14B | **(3.0, 4.0)** | [`wan_t2v_A14B.py`](https://github.com/Wan-Video/Wan2.2/blob/main/wan/configs/wan_t2v_A14B.py) | comment: `# low noise, high noise`; `boundary=0.875`, shift 12.0, 40 steps |
| Wan 2.2 I2V-A14B | **(3.5, 3.5)** | [`wan_i2v_A14B.py`](https://github.com/Wan-Video/Wan2.2/blob/main/wan/configs/wan_i2v_A14B.py) | `boundary=0.900`, shift 5.0 |
| Wan 2.2 TI2V-5B | **5.0** | [`wan_ti2v_5B.py`](https://github.com/Wan-Video/Wan2.2/blob/main/wan/configs/wan_ti2v_5B.py) | dense model, no MoE, 50 steps |
| LTX-Video 2B 0.9.6-dev | **3** (+ `stg_scale: 1`, `rescaling_scale: 0.7`) | [`ltxv-2b-0.9.6-dev.yaml`](https://github.com/Lightricks/LTX-Video/blob/main/configs/ltxv-2b-0.9.6-dev.yaml) | 40 steps |
| LTX-Video 13B 0.9.8-dev | **schedule `[1,1,6,8,6,1,1]`** | [`ltxv-13b-0.9.8-dev.yaml`](https://github.com/Lightricks/LTX-Video/blob/main/configs/ltxv-13b-0.9.8-dev.yaml) | see §2.3 |
| LTX-Video distilled (2B & 13B) | **1** (`stg_scale: 0`) | [`ltxv-13b-0.9.8-distilled.yaml`](https://github.com/Lightricks/LTX-Video/blob/main/configs/ltxv-13b-0.9.8-distilled.yaml) | README: "Does not require classifier-free guidance and spatio-temporal guidance" |
| LTX-Video (README general) | "3-3.5 are the recommended values" | [LTX-Video README](https://github.com/Lightricks/LTX-Video) | |
| HunyuanVideo | **embedded 6.0**, true CFG off | [diffusers pipeline](https://huggingface.co/docs/diffusers/en/api/pipelines/hunyuan_video) | `guidance_scale=6.0` is *embedded*; real CFG only if `true_cfg_scale>1` **and** a negative prompt is given |
| CogVideoX | **6.0**, `use_dynamic_cfg=True` | [`cli_demo.py`](https://github.com/THUDM/CogVideo/blob/main/inference/cli_demo.py), [diffusers](https://github.com/huggingface/diffusers/blob/main/src/diffusers/pipelines/cogvideo/pipeline_cogvideox.py) | official CLI passes `use_dynamic_cfg=True` for both t2v and i2v |
| SVD | **no text CFG at all** | [diffusers SVD pipeline](https://github.com/huggingface/diffusers/blob/main/src/diffusers/pipelines/stable_video_diffusion/pipeline_stable_video_diffusion.py) | image-conditioned only; see §1.3 |

All **[DEM]** — read out of the repos today.

LTX 0.9.6-dev's odd trio (CFG 3 / STG 1 / rescale 0.7) is the reason LTX is described as a
"low CFG" model: it is genuinely tuned for ~3, and its distilled variants for exactly 1.

### 1.2 Does high CFG reduce motion? What is actually demonstrated

**[DEM] — CFG reduces diversity, and this is measured.** STG (CVPR 2025) states plainly:
"CFG often reduces diversity, leading to saturated or overly simplified results" and
"Higher CFG scales improve Imaging Quality but reduce diversity, as reflected in higher FVD."
([arXiv 2411.18664](https://arxiv.org/abs/2411.18664))

**[DEM] — for I2V, CFG is stated to reduce motion.** Same paper: *"CFG increases the
influence of the conditioned image, reducing motion."* This is the clearest paper-level
statement of the effect, and note the mechanism it names: it is about the **conditioning
image** getting amplified, not about text guidance per se.

**[DEM] — the measured motion swing is real and large, on SVD.** STG Table 2, SVD:

| | FVD ↓ | IS ↑ | Imaging Q | Aesthetic Q | Motion Smooth | **Dynamic Degree** |
|---|---|---|---|---|---|---|
| CFG | 151.3 | 38.0 | 0.687 | 0.637 | 0.966 | **0.562** |
| STG | **128.7** | **38.5** | 0.694 | 0.639 | 0.968 | **0.694** |

Swapping CFG for STG moved dynamic degree 0.562 → 0.694 (+23% relative), with FVD also
improving. That is the single best "guidance choice changes motion" number I found.

**[DEM] — but it does NOT replicate on the T2V models in the same paper.** STG Table 1:

| Model | Imaging Q | Aesthetic Q | Motion Smooth | **Dynamic Degree** |
|---|---|---|---|---|
| Mochi + CFG | 0.524 | 0.507 | 0.985 | **0.87** |
| Mochi + STG | 0.628 | 0.554 | 0.988 | **0.86** |
| Open-Sora + CFG | 0.561 | 0.493 | 0.982 | **0.902** |
| Open-Sora + STG | 0.606 | 0.509 | 0.987 | **0.895** |

Dynamic degree went **down slightly** on both. STG's honest claim is "does not *compromise*
dynamics," not "increases motion." The big motion win is SVD-specific (an I2V model), which
matches the "conditioning image dominance" mechanism above.

### 1.3 SVD has no text CFG — and its guidance is a *frame* schedule

`StableVideoDiffusionPipeline` takes `min_guidance_scale=1.0`, `max_guidance_scale=3.0`
and does:

```python
guidance_scale = torch.linspace(min_guidance_scale, max_guidance_scale, num_frames)
```

i.e. **guidance ramps 1.0 → 3.0 across the frame axis**: no guidance on the first frame
(so it stays faithful to the input image), full guidance by the last frame. There is no
text encoder and no negative prompt anywhere in the pipeline; motion is controlled by the
micro-conditioning scalars `motion_bucket_id` (default 127) and `noise_aug_strength`
(default 0.02, docstring: "Increase it for more motion"). **[DEM]**

This is worth internalising: the one model whose motion knob is *not* CFG exposes explicit
motion conditioning instead, and still schedules its guidance rather than holding it flat.

### 1.4 Blunt assessment of the "high CFG freezes video" folklore

- The claim that **low CFG increases motion but loses prompt adherence** is everywhere in
  forums and I found **no controlled sweep** — no paper table varying CFG ∈ {2,4,6,8} and
  reporting dynamic degree. **[FOLK]**
- ALG ([arXiv 2506.08456](https://arxiv.org/html/2506.08456v1)) explicitly **declines** to
  do that ablation: it fixes CFG per model (CogVideoX 6.0, Wan 2.1 5.0, HunyuanVideo 6.0,
  LTX-Video 3.0) and attacks motion from a different angle entirely. Its diagnosis of static
  I2V output is *"high-frequency components of the reference image, causing I2V models to
  lock onto these fine details"* — **an image-conditioning shortcut, not a CFG problem.** **[DEM]**
- ALG's baseline numbers are however the most useful absolute motion figures available
  (VBench-I2V Dynamic Degree, at each model's *recommended* CFG):

  | Model | baseline DD | + ALG |
  |---|---|---|
  | CogVideoX | 64.2 | 82.5 |
  | Wan 2.1 | **28.9** | 41.5 |
  | HunyuanVideo | 88.2 | 92.7 |
  | LTX-Video | **12.6** | 21.1 |

  Wan 2.1 I2V at CFG 5 scores 28.9 and LTX-Video at CFG 3 scores 12.6 — **these models are
  near-static by default even at their vendor-recommended guidance.** Low CFG did not save
  LTX. Blaming our frozen frames on CFG alone would be reading the folklore, not the data. **[DEM]**

**Verdict:** "CFG reduces *diversity* and, in I2V, *motion*" is demonstrated. "Raising CFG
by 2 points will freeze your subject" is folklore with no sweep behind it. The bigger,
measured lever for static video is the conditioning image and the guidance *schedule*, not
the guidance *scalar*.

---

## 2. CFG scheduling over timesteps

### 2.1 Guidance interval (Kynkäänniemi et al., NeurIPS 2024) **[DEM]**

[arXiv 2404.07724](https://arxiv.org/abs/2404.07724) · [code](https://github.com/kynkaat/guidance-interval)

Core finding, verbatim: *"guidance is clearly harmful toward the beginning of the chain
(high noise levels), largely unnecessary toward the end (low noise levels), and only
beneficial in the middle."* Restricting guidance to a middle interval improved record
ImageNet-512 FID **1.81 → 1.40**, and held up on SDXL. Their EDM2-XXL setting: interval
`[17, 22]` with guidance 2.0 — guidance active for roughly a *sixth* of the chain.

Caveat: **this paper is images only.** Its extension to video is by adoption (§2.3), not by
the authors' own experiments.

### 2.2 CFG-Zero* (2025) **[DEM], but the video gain is small**

[arXiv 2503.18886](https://arxiv.org/abs/2503.18886) · [code](https://github.com/WeichenFan/CFG-Zero-star) · [project page](https://weichenfan.github.io/webpage-cfg-zero-star/)

Two parts:
- **optimized scale**: rescale the uncond prediction by `s* = (v_cond · v_uncond)/||v_uncond||²`
  before the CFG combine.
- **zero-init**: zero out the first K ODE steps entirely (default **K=1**; K=2 was better for
  Lumina-Next and SD3, K=1 for the better-trained SD3.5 — "SD3.5 exhibits a decline in
  performance when a higher proportion of initial steps are zeroed out").

Rationale is the same as §2.1: early-step flow estimates are inaccurate, so CFG points
samples down wrong trajectories.

Video results (Table 5, Wan-2.1) are **thin — be honest about this**:

| | CFG | CFG-Zero* |
|---|---|---|
| Wan2.1 14B total | 83.99 | **84.06** (+0.07) |
| Wan2.1 1B total | 80.52 | **80.91** |
| Wan2.1 1B aesthetic | 61.67 | **64.24** |
| Wan2.1 1B imaging | 65.40 | **68.13** |

+0.07 VBench points on the 14B is noise-adjacent. The 1B gains are real. Paper also reports
Motion Smoothness +0.92 on 14B — but **motion smoothness rising is not motion increasing**;
a frozen frame is perfectly smooth. No dynamic-degree improvement is claimed.

### 2.3 The strongest evidence is Lightricks shipping both, together **[DEM]**

`configs/ltxv-13b-0.9.8-dev.yaml`, first pass:

```yaml
guidance_scale:     [1, 1, 6, 8, 6, 1, 1]
stg_scale:          [0, 0, 4, 4, 4, 2, 1]
rescaling_scale:    [1, 1, 0.5, 0.5, 1, 1, 1]
guidance_timesteps: [1.0, 0.996, 0.9933, 0.9850, 0.9767, 0.9008, 0.6180]
skip_block_list:    [[], [11,25,35,39], [22,35,39], [28], [28], [28], [28]]
num_inference_steps: 30
cfg_star_rescale: true
```

Second pass: `guidance_scale: [1]`, `stg_scale: [1]`, `skip_initial_inference_steps: 17`.

Read that carefully. A commercial video model vendor's default production recipe:
- runs **CFG = 1 (off) for the first two timestep bands** — that is zero-init generalised,
- **spikes to 6 → 8 → 6** in a narrow middle band — that is the guidance interval,
- **drops back to 1** for the tail — "largely unnecessary toward the end",
- sets **`cfg_star_rescale: true`** — that is CFG-Zero*'s optimized scale, in the shipped default,
- and varies **STG scale and which blocks are skipped per band** on top.

Mechanics confirmed in [`pipeline_ltx_video.py`](https://github.com/Lightricks/LTX-Video/blob/main/ltx_video/pipelines/pipeline_ltx_video.py):
`guidance_timesteps` maps each sampler timestep to an index into the lists, and the
`cfg_star_rescale` block computes `alpha = <e_text, e_uncond>/||e_uncond||²` then
`e_uncond ← alpha * e_uncond` before the standard combine.

This is the single most actionable finding in the brief: **flat CFG is not what the
best-tuned open video pipeline does.**

### 2.4 CogVideoX ships its own dynamic CFG **[DEM]**

`use_dynamic_cfg=True` is passed by CogVideoX's own official CLI for t2v, i2v and v2v. The
schedule:

```python
self._guidance_scale = 1 + guidance_scale * (
    (1 - math.cos(math.pi * ((num_inference_steps - t.item()) / num_inference_steps) ** 5.0)) / 2)
```

A cosine ramp of the guidance weight across the denoising chain. (The formula is arithmetically
odd — it mixes a step count with a raw timestep value — but it is what ships and what the
vendor's own demo enables by default.) Two of the major open video models therefore schedule
CFG out of the box; constant CFG is the outlier, not the norm.

### 2.5 APG — Adaptive Projected Guidance **[DEM]**

[arXiv 2410.02416](https://arxiv.org/abs/2410.02416), ICLR 2025, Disney Research + ETH.
Decomposes the CFG update into components parallel and orthogonal to the conditional
prediction and **down-weights the parallel component**, which is what drives oversaturation.
Claim: "retains the quality-boosting advantages of CFG while enabling the use of higher
guidance scales without oversaturation," improving FID, recall and saturation scores.
This is a *magnitude* fix, not a *scheduling* fix — orthogonal to §2.1–2.3, and stackable.

Video-specific evidence: **none found.** The paper is image-centric. **[FOLK]** for any claim
it helps video temporal behaviour.

### 2.6 Free ComfyUI availability — all of it, mostly built in **[DEM]**

Read out of ComfyUI master today:

| Technique | Node | Where |
|---|---|---|
| CFG-Zero* (optimized scale **only**) | `CFGZeroStar` | **core**, [`comfy_extras/nodes_cfg.py`](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy_extras/nodes_cfg.py) |
| CFG norm rescale | `CFGNorm` | core, same file |
| APG | `APG` / "Adaptive Projected Guidance" (`eta`, `norm_threshold` default 5.0, `momentum`) | **core**, [`comfy_extras/nodes_apg.py`](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy_extras/nodes_apg.py) |
| STG/PAG-style skip guidance | `SkipLayerGuidanceDiT` (`scale` 3.0, `start_percent` 0.01, `end_percent` **0.15**, `rescaling_scale`) | **core**, [`comfy_extras/nodes_slg.py`](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy_extras/nodes_slg.py) — docstring: "Inspired by Perturbed Attention Guidance" |
| CFG-Zero* **+ zero-init** | `CFGZeroStarAndInit` (`use_zero_init`, `zero_init_steps`) | KJNodes, [`model_optimization_nodes.py`](https://github.com/kijai/ComfyUI-KJNodes/blob/main/nodes/model_optimization_nodes.py) |
| Wan-specific SLG | `WanVideoSLG` (`blocks` default "10", start 0.1 / end 1.0) | [WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper) |
| cfg_zero_star, zero-init, FreSca, TCFG, RAAG for Wan | `WanVideoExperimentalArgs` | WanVideoWrapper `nodes.py` |
| PAG / SEG / SWG / NAG / TPG / FDG | — | [pamparamm/sd-perturbed-attention](https://github.com/pamparamm/sd-perturbed-attention) |

Two things worth flagging:
- ComfyUI core's `CFGZeroStar` implements **only the optimized-scale half**. If we want
  zero-init we need KJNodes' `CFGZeroStarAndInit` or WanVideoWrapper's experimental args.
- Core `SkipLayerGuidanceDiT` defaults to `end_percent=0.15` — it is already an *interval*
  technique, active only in the first 15% of the chain.

There is **no built-in generic "CFG interval / limiter" node** in core ComfyUI; the interval
behaviour has to come from a scheduler-side implementation (as LTX does natively) or a
custom node.

---

## 3. STG and PAG

### 3.1 STG — Spatiotemporal Skip Guidance **[DEM]**

[arXiv 2411.18664](https://arxiv.org/abs/2411.18664) · CVPR 2025 · [project](https://junhahyung.github.io/STGuidance/) · [code](https://github.com/junhahyung/STGuidance)

Training-free. Builds an **implicit weak model by skipping selected spatiotemporal layers**
of the model itself, then guides away from it — so, autoguidance without training a weak
model, and without CFG's diversity penalty.

Demonstrably improves (numbers in §1.2):
- Imaging quality: Mochi 0.524 → 0.628, Open-Sora 0.561 → 0.606
- Aesthetic quality: Mochi 0.507 → 0.554
- FVD on SVD: 151.3 → 128.7
- **Dynamic degree on SVD: 0.562 → 0.694** (the headline motion result)
- Dynamic degree on Mochi/Open-Sora: essentially flat (marginally down)

Layer choice: layer 35 of Mochi's 48, layer 8 of SVD's 16, layer 12 of Open-Sora's 28 —
i.e. **roughly mid-depth**, chosen empirically. Two variants: STG-A (attention skip, scale
2.0) and STG-R (residual skip, scale 1.0).

Adoption: merged into LTX-Video's main repo, and into diffusers as a community pipeline.
LTX's `stg_mode` defaults to `"attention_values"` with options `attention_skip`, `residual`,
`transformer_block`. LTX 0.9.6-dev uses `stg_scale: 1` / `skip_block_list: [19]`; the 13B
0.9.8-dev schedule ramps STG **4 → 4 → 4 → 2 → 1** across bands with per-band skip lists.

### 3.2 PAG — Perturbed Attention Guidance **[DEM] for images, thin for video**

[arXiv 2403.17377](https://arxiv.org/abs/2403.17377) · [code](https://github.com/cvlab-kaist/Perturbed-Attention-Guidance) · [diffusers docs](https://huggingface.co/docs/diffusers/en/api/pipelines/pag)

Replaces selected self-attention maps with an identity matrix to produce a
structure-degraded sample, then guides away from it. PAG's direction is *added to* CFG's
with an independent scale.

PAG is the ancestor of STG — STG is explicitly the spatiotemporal generalisation, and
ComfyUI's `SkipLayerGuidanceDiT` cites PAG in its docstring. I found **no PAG-vs-CFG video
motion benchmark**; the STG paper mentions autoguidance as the comparison point, not PAG.
Anyone claiming PAG fixes video motion is extrapolating. **[FOLK]**

Related, if we ever chase motion quality directly: SPG (Smooth Perturbation Guidance,
[arXiv 2503.02577](https://arxiv.org/html/2503.02577v1)) builds the weak model by *temporally
smoothing* motion — same family, motion-targeted.

---

## 4. Do negative prompts work at all?

### 4.1 At CFG = 1 the negative prompt is not weak — it is never computed **[DEM ×3]**

Three independent implementations, read today:

**ComfyUI** — [`comfy/samplers.py`](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/samplers.py):
```python
def sampling_function(model, x, timestep, uncond, cond, cond_scale, model_options={}, seed=None):
    if math.isclose(cond_scale, 1.0) and model_options.get("disable_cfg1_optimization", False) == False:
        uncond_ = None
```
The uncond conditioning is replaced with `None` and the second forward pass never runs.

**LTX-Video** — `pipeline_ltx_video.py`:
```python
do_classifier_free_guidance = guidance_scale[i] > 1.0
```
evaluated **per step**, so on the 13B schedule the negative prompt is live only during the
`6, 8, 6` bands and dead everywhere else.

**diffusers Wan** — `pipeline_wan.py`: `do_classifier_free_guidance` is `self._guidance_scale > 1.0`,
and the `negative_prompt` docstring says it outright: *"Ignored when not using guidance
(i.e., ignored if `guidance_scale` is less than 1)."*

So for any Lightning / LightX2V / CausVid / distilled recipe pinned at CFG 1 — which is what
all the 4-step Wan workflows do — **every negative prompt in the workflow is inert**. Not
"weak", not "diluted": mathematically absent, and the code doesn't even spend the FLOPs.

The peer-reviewed framing of the same fact, from NAG (NeurIPS 2025): *"Few-step diffusion
models facilitate rapid inference, but generally lack support for CFG, making negative
guidance ineffective."* ([arXiv 2505.21179](https://arxiv.org/abs/2505.21179),
[project](https://chendaryen.github.io/NAG.github.io/)) **[DEM]**

**The fix, if we need negatives on a distilled model: NAG.** Extrapolates in *attention*
space with L1 normalisation instead of through a second guidance pass. Works on UNet and
DiT, few-step and multi-step, image and video. Cost on Wan2.1: **+1.3s (12%)** vs CFG's
+10.7s (100%). Available as [ComfyUI-NAG](https://github.com/ChenDarYen/ComfyUI-NAG)
(supports Wan incl. VACE, and HunyuanVideo) and natively as `WanVideoApplyNAG` in
WanVideoWrapper. NAG's README gives **no recommended `nag_scale`** — we would have to sweep
it ourselves, one sample at a time.

Also in this space: VSF (Value Sign Flip, [arXiv 2508.10931](https://arxiv.org/pdf/2508.10931))
and a negpip-style weighted-prompt fork for WanVideoWrapper
([issue #1834](https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/1834)) that pushes
`(term:-1.0)` suppression through the *positive* prompt at CFG=1. The latter is unmerged and
the thread is unresolved — a commenter objects "I don't think this works with T5-based text
encoders? You're probably better off using NAG." **[FOLK]**

### 4.2 HunyuanVideo: embedded guidance is not CFG **[DEM]**

HunyuanVideo distils guidance into the weights. Tech report §5.2
([arXiv 2412.03603](https://arxiv.org/html/2412.03603v1)): they "distill the combined output
for unconditional and conditional inputs into a single student model," trained with "the
guidance scale randomly sampled from 1 to 8," for **~1.9× acceleration**. Maintainer
`jiawangbai` confirms in [issue #113](https://github.com/Tencent-Hunyuan/HunyuanVideo/issues/113):
*"It is more efficient to use embedded CFG compared to two separated branches during
inference (approximately 1.9x acceleration)."*

Consequence: the default `guidance_scale=6.0` is a **conditioning input to the network**, not
a CFG combine. Turning it up does not run a negative branch. Real negative prompting needs
`true_cfg_scale > 1` **and** an explicit negative prompt, which doubles inference cost.

Worth noting §5.2's own framing: CFG "significantly improves the sample quality and **motion
stability** of text-conditioned diffusion models." The vendors regard CFG as *stabilising*
motion — the opposite valence from the community's "CFG freezes motion."

### 4.3 Are negative prompts weak for camera/motion terms?

Mixed, and the honest answer is that the direct evidence is thin.

**[DEM] — the Wan team clearly believes camera-motion negatives work, and ships one.**
Wan 2.1 I2V-14B prepends a camera term to the shared negative prompt
([`wan_i2v_14B.py`](https://github.com/Wan-Video/Wan2.1/blob/main/wan/configs/wan_i2v_14B.py)):
```python
i2v_14B.sample_neg_prompt = "镜头晃动，" + i2v_14B.sample_neg_prompt
```
`镜头晃动` = "camera shake / wobble". Only the I2V config does this. That is a vendor
deliberately spending negative-prompt budget on a camera term, for the task where the
conditioning image makes shake most objectionable.

**[DEM] — the default negative prompt is engineered to *increase* motion.** The shared default
([`shared_config.py`](https://github.com/Wan-Video/Wan2.1/blob/main/wan/configs/shared_config.py),
byte-identical in Wan 2.2) is:

> 色调艳丽，过曝，**静态**，细节模糊不清，字幕，风格，作品，画作，画面，**静止**，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，**静止不动的画面**，杂乱的背景，三条腿，背景人很多，倒着走

Three separate anti-static terms — 静态 ("static"), 静止 ("still"), 静止不动的画面
("motionless picture") — plus 倒着走 ("walking backwards"), a temporal-coherence term. **Most
of the semantic budget in Wan's default negative prompt is spent fighting frozen video.**
This reframes the whole question: for Wan, the negative prompt *is* the motion control, and
running at CFG 1 throws it away (§4.1).

**[FOLK] — "keep it in Chinese."** Widely repeated (e.g. this
[Japanese writeup](https://scrapbox.io/work4ai/Wan2.1%E3%81%AE(%E3%83%87%E3%83%95%E3%82%A9%E3%83%AB%E3%83%88%E3%81%AE)Negative_Prompt%E3%81%AF%E4%B8%AD%E5%9B%BD%E8%AA%9E%E3%81%AE%E3%81%BE%E3%81%BE%E4%BD%BF%E3%81%A3%E3%81%9F%E3%81%BB%E3%81%86%E3%81%8C%E8%89%AF%E3%81%84),
403 to automated fetch — I could not read the body or verify it carries an A/B). Plausible —
umT5 is multilingual and the model was trained with these exact strings — but I found **no
side-by-side test**. Everyone uses the default Chinese prompt mostly because it is the
config default and gets copied forward, which is a weaker reason than "it was tested."

**[DEM] — text conditioning genuinely is a poor channel for camera control.** AC3D
([arXiv 2411.18673](https://arxiv.org/abs/2411.18673), NVIDIA) finds camera motion is
**low-frequency in nature**, that DiTs "implicitly perform camera pose estimation under the
hood," and that **"only a sub-portion of their layers contain the camera information."**
Their fix is architectural conditioning restricted to those layers and to an early
conditioning schedule — not prompting. The field's answer to camera control is
ControlNet-style pose conditioning, which is a strong implicit statement that text (positive
or negative) is not the right lever.

I found **no study isolating negative-prompt efficacy for camera terms specifically.** The
strong claim "camera terms in the negative prompt do nothing" is **[FOLK]**. The defensible
version: camera motion is a low-frequency, layer-localised, early-timestep property, and text
is a blunt instrument for it — while *object/scene* motion terms like 静态 sit right in the
middle of what the text encoder represents well.

---

## 5. Wan 2.2 MoE and CFG

**[DEM] — CFG is applied per-expert, and the high-noise expert gets MORE of it.**
[`wan/text2video.py`](https://github.com/Wan-Video/Wan2.2/blob/main/wan/text2video.py):

```python
boundary = self.boundary * self.num_train_timesteps      # 0.875 * 1000 = 875 for T2V

model = self._prepare_model_for_timestep(t, boundary, offload_model)
sample_guide_scale = guide_scale[1] if t.item() >= boundary else guide_scale[0]

noise_pred_cond   = model(latent_model_input, t=timestep, **arg_c)[0]
noise_pred_uncond = model(latent_model_input, t=timestep, **arg_null)[0]
noise_pred = noise_pred_uncond + sample_guide_scale * (noise_pred_cond - noise_pred_uncond)
```

with `_prepare_model_for_timestep` selecting `high_noise_model` when `t >= boundary`.
Docstring: *"If tuple, the first guide_scale will be used for low noise model and the second
guide_scale will be used for high noise model."*

So for T2V-A14B: **t ≥ 875 → high-noise expert at CFG 4.0; t < 875 → low-noise expert at
CFG 3.0.** For I2V-A14B both are 3.5 with boundary 0.900. Note this is itself a (coarse,
two-step) CFG schedule — Wan 2.2 does not run flat CFG either.

**[DEM] — official role split, but stated as *layout*, not *motion*.** The
[Wan2.2-T2V-A14B model card](https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B) says the A14B
series uses "a high-noise expert for the early stages, focusing on **overall layout**; and a
low-noise expert for the later stages, **refining video details**," with the switch at
"a threshold step t_moe corresponding to half of the SNR_min." ComfyUI's
[Wan2.2 day-0 blog](https://blog.comfy.org/p/wan22-day-0-support-in-comfyui) repeats it
verbatim: "High-noise experts handle overall layout, while low-noise experts refine details."

**[FOLK] — "the high-noise expert determines motion."** This is the universal community
gloss and it is a *reasonable* inference — layout/composition is settled early, and in a
video model the early-timestep global structure includes the motion trajectory (consistent
with AC3D finding camera motion is low-frequency and early). But **no official Wan statement
says "motion."** The word Alibaba uses is 布局/layout. Treat "put your motion LoRA / motion
prompt on the high-noise expert" as a plausible, widely-held, unverified heuristic.

Corollaries that ARE demonstrated and do matter for us:
- Wan 2.2 gives us **two independent CFG knobs already**, no custom nodes needed — the
  cheapest available experiment in this whole brief is sweeping `(low, high)` around the
  `(3.0, 4.0)` default and measuring motion.
- Both experts run cond **and** uncond forward passes, so the negative prompt is live for
  both — *unless* a speed LoRA drops either to CFG 1.

**[FOLK]** — "CFG above 9.0 over-sharpens the low-noise model, use 6.0–7.5" and similar
per-expert tuning advice circulating on blogs (runpod, apatero, etc.). No A/B behind any of
it, and note it contradicts the vendor default of 3.0.

---

## 6. What I could not find

- Any controlled **CFG-scale sweep with dynamic-degree measurements** on a modern video model.
  This is a genuine gap in the literature, and it is the exact question we were asking.
  It is also cheap for us to run.
- Any **video** evaluation of APG or of the guidance-interval paper by their own authors.
- Any **isolated test of negative-prompt efficacy for camera terms**.
- Any A/B for **Chinese vs English** Wan negative prompts.
- A built-in **generic CFG-interval node** for ComfyUI.

## 7. Cheapest next experiments, in order

1. **Audit our job specs for CFG=1 + non-empty negative prompt.** Pure static check, zero GPU.
   Any such pair is a lie in the config and should be deleted or the CFG raised.
2. **Wan 2.2 per-expert CFG sweep** around `(3.0, 4.0)` — one sample per cell, motion measured,
   no new code.
3. **Port LTX's shape to whatever we run**: CFG 1 for the first ~2 bands, spike mid-chain,
   CFG 1 for the tail. LTX ships it; it is the best-evidenced schedule available.
4. `CFGZeroStar` is a free core node and costs nothing to leave on — but expect the 14B-scale
   gain (+0.07 VBench) to be invisible. Do not spend a screening slot proving it.
5. If we ever pin a distilled recipe at CFG 1 and still want negatives: NAG, +12% time.

---

## Sources

Model source & configs: [Wan2.1](https://github.com/Wan-Video/Wan2.1) · [Wan2.2](https://github.com/Wan-Video/Wan2.2) · [Wan2.2-T2V-A14B card](https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B) · [LTX-Video](https://github.com/Lightricks/LTX-Video) · [HunyuanVideo](https://github.com/Tencent-Hunyuan/HunyuanVideo) · [CogVideo](https://github.com/THUDM/CogVideo) · [diffusers](https://github.com/huggingface/diffusers) · [ComfyUI](https://github.com/comfyanonymous/ComfyUI) · [ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper) · [ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes)

Papers: [CFG-Zero* 2503.18886](https://arxiv.org/abs/2503.18886) · [STG 2411.18664](https://arxiv.org/abs/2411.18664) · [Guidance interval 2404.07724](https://arxiv.org/abs/2404.07724) · [APG 2410.02416](https://arxiv.org/abs/2410.02416) · [PAG 2403.17377](https://arxiv.org/abs/2403.17377) · [NAG 2505.21179](https://arxiv.org/abs/2505.21179) · [ALG 2506.08456](https://arxiv.org/html/2506.08456v1) · [AC3D 2411.18673](https://arxiv.org/abs/2411.18673) · [HunyuanVideo 2412.03603](https://arxiv.org/html/2412.03603v1) · [SPG 2503.02577](https://arxiv.org/html/2503.02577v1) · [VSF 2508.10931](https://arxiv.org/pdf/2508.10931)

Other: [STG project page](https://junhahyung.github.io/STGuidance/) · [NAG project page](https://chendaryen.github.io/NAG.github.io/) · [ComfyUI-NAG](https://github.com/ChenDarYen/ComfyUI-NAG) · [sd-perturbed-attention](https://github.com/pamparamm/sd-perturbed-attention) · [guidance-interval code](https://github.com/kynkaat/guidance-interval) · [ComfyUI Wan2.2 day-0 blog](https://blog.comfy.org/p/wan22-day-0-support-in-comfyui) · [HunyuanVideo issue #113](https://github.com/Tencent-Hunyuan/HunyuanVideo/issues/113) · [WanVideoWrapper issue #1834](https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/1834)
