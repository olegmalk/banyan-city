# Sampler / scheduler / step-count → temporal artifacts in video diffusion

External research, 2026-08-18. Scope: sampler and scheduler choice and step count in
video diffusion, and their effect on temporal artifacts. Driving defect: an
image-to-video clip where the subject's size changes in a sudden 1–4 frame STEP (a
"pop", sometimes with one blended/crossfade-looking frame at the join) instead of
ramping smoothly, with the rest of the clip static.

Every claim below is labelled DEMONSTRATED (paper, benchmark, before/after grid,
maintainer statement, or shipped code/config) vs FOLKLORE (unsupported forum comment).

---

**Bottom line up front:** the literature and maintainer record strongly document *motion attenuation* (clips coming out static/damped) from low steps and distillation LoRAs — that half of your defect is well-attested. The other half, a **discrete 1–4 frame size step with one blended frame at the join**, is *not* documented as a sampler artifact anywhere I could find. It **is** documented as a **latent-chunk / conditioning-boundary artifact**, and the numbers line up: Wan's VAE compresses 4 pixel frames per latent frame, LTX's compresses 8. A 1–4 frame pop is one Wan latent frame wide. That is your strongest lead by a distance, and it is a different bug from the sampler.

---

## 1. Sampler comparisons for video specifically

**There is no published, controlled sampler-vs-temporal-artifact grid for video models.** I looked for one across arXiv, VBench-derived ablations, and the ComfyUI/Kijai/diffusers trackers. Every sampler ablation I found in papers holds the sampler *fixed* (e.g. DDIM-50) and varies something else. Be sceptical of anyone who tells you a sampler ranking for video motion.

What actually exists:

**DEMONSTRATED (maintainer statement + in-thread image grid)** — Kijai, author of ComfyUI-WanVideoWrapper, [issue #257](https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/257), 2025-03-17, posting a comparison image:
> "dpm++ should be the same as dpmpp_2m, or closest at least. Comfy samplers are different, these nodes can only use diffusers samplers so it's limited selection. **Unipc has been best for normal generations, dpm/euler can be useful for flowedit/vid2vid.**"

**FOLKLORE (single unreproduced user report) + maintainer pushback** — [issue #124](https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/124). User MarisKay: "unipc, with the same sampler settings as dpm++, both at 10 steps, tends to generate more high-speed, fast-forward-like videos where the character moves excessively fast and erratically." Kijai's reply is the useful part:
> "I don't think 10 steps is a good comparison point, it generally isn't enough for anything but preview. Unipc overall seems a lot better for me at least."

Note the direction: the only motion complaint against UniPC is *too much / erratic* motion at low steps, not stuttering.

**DEMONSTRATED (paper, but images not video)** — bh1 vs bh2 is settled in the [UniPC paper](https://arxiv.org/pdf/2302.04867) and restated in [diffusers docs](https://huggingface.co/docs/diffusers/en/api/schedulers/unipc): B₁(h)=h vs B₂(h)=eʰ−1; bh1 wins by 1–3 FID at NFE 5–6, bh2 catches up and wins above that, and **"for guided sampling, B₁(h) is worse than B₂(h) consistently."** Recommendation: bh1 for unconditional under 10 steps, bh2 otherwise. **No temporal claim at all** — this is FID on images. In ComfyUI these are two separate entries in `SAMPLER_NAMES`: `uni_pc` and `uni_pc_bh2` ([samplers.py](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/samplers.py)).

**FOLKLORE / discard** — `apatero.com`, `comfyui.dev/docs/guides/...`, `vantagewithai.com` and similar "ComfyUI Sampler Guide 2025" pages surface at the top of every search and contain confident rankings ("DPM++ 2M Karras delivers best quality with 20–30 steps", "mixing euler_a → dpmpp_sde creates artifacts"). These are unattributed SEO content with no grids, no seeds, no methodology. Do not cite them.

**Unverifiable but real** — there is a genuine community test archive with workflows and metadata: [Civitai: Wan 2.2 14B I2V Tests of Sampler Setting with and without speed LoRAs](https://civitai.com/models/1937373/wan-22-14b-i2v-tests-of-sampler-setting-with-and-without-speed-loras). The written conclusions live in two Reddit threads (`/comments/1naubha/`, `/comments/1nc8hcu/`) which are hard-blocked to fetchers, including every redlib mirror I tried. The artifacts are downloadable if you want the ground truth.

**`res_multistep`** is Nvidia's Cosmos sampler (predictor-corrector). Available in WanVideoWrapper. I found **no** evidence for or against it on temporal quality — only vendor description.

---

## 2. Scheduler / sigma schedule

### The linear-quadratic schedule is Movie Gen's, not LTX's — and the rationale is the most useful thing in this whole report

**DEMONSTRATED (paper, §3.4.2)** — [Movie Gen, arXiv:2410.13720](https://arxiv.org/html/2410.13720v1):
> "The linear-quadratic strategy is predicated on the observation that **the first inference steps are pivotal in setting up the scene and motion of the video.**"

…and "a video generated with 1000 linear steps can be precisely emulated by 25 linear steps followed by 25 quadratic steps." ~20× inference speedup.

**DEMONSTRATED (code provenance)** — ComfyUI's `linear_quadratic_schedule` carries the comment `# from: https://github.com/genmoai/models/blob/main/src/mochi_preview/infer.py#L41`, i.e. it is Genmo Mochi's implementation, params `threshold_noise=0.025`, `linear_steps = steps // 2`.

**Correction to a common claim:** the [LTX-Video paper](https://arxiv.org/abs/2501.00103) §2.5.2 "Timestep scheduling" does **not** describe a linear-quadratic schedule. It describes a **log-normal training-time timestep distribution shifted toward higher noise as a function of token count** ("We adopt this recommendation and shift the timestep scheduler towards the higher-noise regions, depending on the number of tokens"), with percentile clamping at 0.5/99.9. LTX offers `linear-quadratic` as one *option* (`sampler: "uniform" | "linear-quadratic" | "from_checkpoint"`), inherited from the Mochi/Movie Gen line.

**DEMONSTRATED (shipped config) — this is the concrete number you want.** Lightricks' own distilled configs, e.g. [`configs/ltxv-13b-0.9.8-distilled.yaml`](https://github.com/Lightricks/LTX-Video/blob/main/configs/ltxv-13b-0.9.8-distilled.yaml):

```yaml
first_pass:
  timesteps: [1.0000, 0.9937, 0.9875, 0.9812, 0.9750, 0.9094, 0.7250]
second_pass:
  timesteps: [0.9094, 0.7250, 0.4219]
```

Five of the seven first-pass steps sit in the **top 2.5%** of the noise range, then it takes two huge jumps. That is the Movie Gen thesis made literal: spend nearly all your steps where scene and motion are decided, then leave.

### Karras sigmas on video / flow-matching models

**DEMONSTRATED (code)** — in [ComfyUI `samplers.py`](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/samplers.py), `karras`, `exponential` and `kl_optimal` are registered with `use_ms=False`:

```python
"karras": SchedulerHandler(k_diffusion_sampling.get_sigmas_karras, use_ms=False),
```
```python
if handler.use_ms:
    return handler.handler(model_sampling, steps)
return handler.handler(n=steps, sigma_min=..., sigma_max=...)
```

They never see `model_sampling` — they only get `(n, sigma_min, sigma_max)` and reconstruct a k-diffusion/EDM-shaped curve. So they cannot respect a flow-matching model's timestep mapping or its `shift`. `simple`, `beta`, `normal`, `sgm_uniform`, `ddim_uniform`, `linear_quadratic` all index the model's own sigma table.

**MY INFERENCE, not a citation:** Karras with ρ=7 concentrates steps near `sigma_min` — i.e. at *low* noise, where detail is refined. Movie Gen §3.4.2, Wan 2.2's MoE design, and the ALG paper (below) all say motion is decided at *high* noise. So Karras on a video flow-matching model spends its budget in exactly the wrong half. That is a coherent mechanism, but **I found no published before/after video grid demonstrating it.**

**FOLKLORE** — "on flow-matching models the karras and exponential sigma switches are universal failures" appears only in unattributed blog content (apatero.com). Plausible, unsupported.

**FOLKLORE (but specific and testable)** — several LTX users report that Euler + `linear_quadratic` (Mochi) "completely avoids both white borders and unwanted logo additions" after "hundreds of video generations." No grid published.

### Wan 2.2's MoE boundary is a scheduler problem in disguise

**DEMONSTRATED (official model card)** — [Wan-AI/Wan2.2-I2V-A14B](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B): high-noise expert "for the early stages, focusing on overall layout"; low-noise expert "for the later stages, refining video details"; switch at a threshold defined as half of SNR_min. Consequence: your scheduler + `shift` + step count jointly determine **how many steps land inside the motion-deciding expert**. [ComfyUI-WanMoEScheduler](https://github.com/cmeka/ComfyUI-WanMoEScheduler) exists purely to solve boundary misalignment: "Too low: the boundary may fall in the wrong place, giving you an incorrect number of high or low steps." It does not claim specific artifacts from misalignment.

**DEMONSTRATED (published sweep, but not of steps)** — [Replicate's Wan 2.1 parameter sweep](https://replicate.com/blog/wan-21-parameter-sweep) swept `sample_guide_scale` 0–10 and `sample_shift` 1–9 at fixed 30 steps. Findings: guide scale 3–7 is the sweet spot, 8+ is "overcooked"; shift 1 creates "a dolly effect where backgrounds warp while subjects remain realistic"; shift 7–9 "surprisingly similar." Step count was **not** swept.

---

## 3. Step count, distilled models, and the Wan speed-LoRA motion problem

### The motion-loss problem is officially acknowledged, and no one has explained it

**DEMONSTRATED (official maintainer post, Owner-badged)** — lightx2v, [Wan2.2-Lightning discussion #26, "On the Slow Motion Issue of Wan2.2-Lightning"](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/26), 2025-08-13:
> "While our accelerated model is capable of generating visually appealing videos in just 4 inference steps, we've observed that **the motion speed in these videos tends to be slower compared to those produced by the base model using more inference steps.** This issue has been identified during our testing, and we're actively working on a solution."

Sept 8 update: "We have made a great progress in improving the motion speed and camera control." **No root cause given, at any point.**

**DEMONSTRATED (maintainer)** — [discussion #20](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/20): "The T2V lora slows the motion down, we are currently finding a way to solve this." I2V LoRA is better but still below the 40-step base.

**DEMONSTRATED (official ComfyUI docs)** — [docs.comfy.org Wan2.2 Fun Control](https://docs.comfy.org/tutorials/video/wan/wan2-2-fun-control):
> "A version using Wan2.2-Lightning 4-step LoRA from lightx2v: **may cause some loss in video dynamics** but offers faster speed" … "Since using the 4-step LoRA provides a better experience for first-time workflow users, but may cause some loss in video dynamics, we have enabled the accelerated LoRA version by default."

**Primary user threads** — [#5 "bad motion"](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/5): dan5 "the new lightning lora kills the motion and is worse than the one from wan 2.1"; darksidewalker "It just ignores most motions, it is almost like a 'live wallpaper.'" [#14](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/14): AgustinCaniglia "2.2 lightning specially in the high noise model kills all the complex motions.. cinematic feels is gone." Maintainer X-niper's reply there deflects ("One possible reason may be you are using I2V workflow with the T2V loras").

**Resolution dependence** (FOLKLORE, single report, but easy to test): "res 1280x720 normal speed, 960x544 a bit slower. 832x480 slow motion" — [#20](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/20).

### Workarounds, with attribution

| Workaround | Source | Grade |
|---|---|---|
| LoRA strength 0.6–0.8 on **high** expert, 1.0 on **low**; CFG 2–3.5 high / 1.0 low; 8 steps (4+4) | Aorora12, [#5](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/5) | FOLKLORE, widely repeated |
| 3-sampler: sampler 1 **no LoRA** at CFG 3.5 (steps 1–4), sampler 2 LoRA ×2 at CFG 1, sampler 3 LoRA 0.7 | bicio78ita, [#20](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/20); Sikaworld1990 "3 sampler is the solution", [#5](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/5) | FOLKLORE |
| Reduce LoRA weight rather than raise CFG | ui8768, [#20](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/20) | FOLKLORE |
| Stack the Wan **2.1** lightning LoRA on top of 2.2 | community, [#14](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/14) | FOLKLORE |
| Official: Euler scheduler, shift = 5, CFG 1, steps 4 | X-niper (maintainer), [#5](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/5) | MAINTAINER |
| Disabling the high-noise LoRA fixes slow motion but gives "jittery or horror motions" | [Stable-Video-Infinity #66](https://github.com/vita-epfl/Stable-Video-Infinity/issues/66) | FOLKLORE, useful negative result |

The Wan2.2-Lightning 4-step timestep list is `[1000.0, 937.5, 833.3, 625.0]` (σ = 1.0, 0.9375, 0.8333, 0.625 → 0), with the first two on the high-noise expert. The **final Euler step traverses 62.5% of the trajectory in one shot.** ([lightx2v #13](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/13); shift k=5 via t' = (kt/1000)/(1+(k−1)(t/1000))·1000.)

### The paper-level evidence: it's *attenuation*, not *stepping*

**DEMONSTRATED (paper §3.1)** — [Adaptive Video Distillation, arXiv:2603.21864](https://arxiv.org/html/2603.21864v1):
> "**mode collapse extends into the temporal dimension, resulting in videos with limited or even static motion**" … "temporal collapse … leads to videos with limited motion dynamics, sometimes even near-static sequences or reduced variations"

Cause: "distribution matching losses … induce mode collapse in image generation … In video generation, this problem is further amplified by the temporal dimension." Table 2: baseline DMD Dynamic Degree **72.22 → 99.72** with temporal regularization. No per-step-count breakdown.

**DEMONSTRATED (paper + VBench + human study)** — [MoGAN, arXiv:2511.21592](https://arxiv.org/abs/2511.21592): few-step video diffusion produces "**jitter, ghosting, or implausible dynamics**"; "the standard denoising MSE objective provides no direct supervision on temporal consistency, allowing models to achieve low loss while still generating poor motion." On Wan2.1-T2V-1.3B, MoGAN beats the 3-step DMD model by **+13.3%** VBench motion score and the 50-step teacher by +7.3%; human study 56% vs 29% over DMD.

**Be blunt:** across all of this, the documented low-step/distillation defect is **damped, slow, or frozen motion** — plus jitter and ghosting. **I found no paper, benchmark, or maintainer statement documenting "stepped" / quantized / discontinuous motion as a low-step artifact.** If your defect is a discrete pop, the step count is probably not what's producing the *pop* (though it is very likely producing the *static rest of the clip*).

### Why "the rest is static" is over-determined for I2V

**DEMONSTRATED (paper §3.1, VBench)** — [Adaptive Low-Pass Guidance (ALG), arXiv:2506.08456](https://arxiv.org/html/2506.08456v1). I2V models are measurably more static than their T2V siblings: CogVideoX −16.6%, Wan 2.1 −18.6% dynamic degree. Mechanism:
> "high-frequency components within input images cause a **'shortcut' effect, where generation trajectory prematurely locks onto the image's appearance during denoising**" … "the fine-grained details of the reference image locks in the early generation stages, confining the generation trajectory from the beginning."

Timing is the striking part: Figure 2 shows the shortcut appears **after just one denoising step (t=0.02 of 50)**. Fix = low-pass filter the conditioning during the first 6% of steps. Absolute dynamic-degree baselines are damning: **LTX-Video 12.6** (→21.1 with ALG), Wan 2.1 28.9 (→41.5), CogVideoX 64.2 (→82.5), HunyuanVideo 88.2 (→92.7).

Read that against a 4-step schedule: if the appearance lock happens within the first 2% of a 50-step trajectory, then at 4 steps your **first step already spans 6%** — the lock is total and unavoidable, and every motion decision is quantized into a handful of coarse Euler jumps.

Lightricks addresses the same thing by *deliberately degrading* the conditioning image: `LTXVAddGuideAdvanced` applies JPEG-style compression via a `crf` parameter (default 29, range 0–51) and a `strength` multiplier. Community guidance: "Pinning a keyframe at strength 1 and LTX can lock onto it and refuse to move — the well-known launch-era weak-I2V behavior."

*(Secondary, UNVERIFIED: search snippets attribute to [AC3D, arXiv:2411.18673](https://arxiv.org/abs/2411.18673) the claims that camera motion is a low-frequency signal generated "within the first 10%" of diffusion while scene motion finalizes late. Both the PDF and HTML fetches failed for me — I could not confirm this in the paper. It agrees with ALG and Movie Gen, so treat it as corroborating flavour, not evidence.)*

---

## 4. Abrupt change at a specific frame index — **this is where your defect lives**

### The structural fact that makes your 1–4 frame pop diagnosable

**DEMONSTRATED** — Wan's VAE compresses `(1+T)×H×W×3 → [1+T/4, H/8, W/8]`. **The first frame is its own causal latent slice**; after that each latent step advances **exactly four** pixel frames. Two 3D downsample blocks each with causal temporal conv, kernel (3,1,1) stride (2,1,1) → temporal stride 4. Frame counts must be **4n+1** (81 frames → 21 latent positions: 1 + 20). Source: [Wan technical report, arXiv:2503.20314](https://arxiv.org/pdf/2503.20314); [Kijai VAE internals](https://deepwiki.com/kijai/ComfyUI-WanVideoWrapper/4.4-vae-and-latent-processing).

So: **pixel frame 0 = latent 0 = your conditioning image. Pixel frames 1–4 = latent 1.** A size change that happens across frames 0→1 and completes by frame 4, with the rest static, is *precisely* one latent frame wide and sits *precisely* on the I2V conditioning boundary. **Check whether your pop starts at frame 1 and settles at frame 4.** If it does, this is a VAE/conditioning boundary artifact, not a sampler artifact, and no amount of sampler swapping will fix it.

For LTX the quantum is 8: `LTXVAddGuide` **enforces** `frame_idx` divisible by 8 and guide videos of length 8n+1 ([ComfyUI docs](https://docs.comfy.org/built-in-nodes/LTXVAddGuide)).

### The closest published match to your exact description

**DEMONSTRATED (report + working mitigation)** — [kijai/ComfyUI-WanVideoWrapper #295](https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/295), endframe I2V, 81 frames:
> "it's smoothly approaching the end frame, then **in the last few frames there is a sudden 'morph' effect where it jumps to exactly match the end frame.** Sometimes the effect is just a slight flutter in color, other times it is a large, obvious, **sudden morph that sometimes ends up on a blurry frame.**"

Mitigation that works: `end_latent_strength` 0.95–0.98 instead of 1.0. This is your defect's mirror image at the other end of the clip — an over-strong latent conditioning anchor forcing a discrete jump across one latent boundary, with a blended/blurry frame at the join. **The equivalent knob on your side is the start-frame conditioning strength.**

### The cleanest documented per-latent-chunk artifact

**DEMONSTRATED (reproduction + control experiment; no maintainer explanation)** — [Kijai/WanVideo_comfy_fp8_scaled discussion #31](https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/discussions/31), Wan 2.2 Animate:
> "the **last 4 frames (last latent)** of the 77-frame window get progressively dark and introduce artifacts, causing a noticeable jump between windows"

Motion stops following the driving video during those 4 frames, then "picks right back up with the correct brightness and motion at frame 78." The user then ran the decisive control: dropping to a 73-frame segment followed by a 77-frame window made **the last 8 frames** of the second window corrupt — the corruption span scales in units of 4. Nobody has explained it.

### VAE-side, isolated from the DiT

**DEMONSTRATED (isolating code, user weathon)** — [Wan-Video/Wan2.1 #369](https://github.com/Wan-Video/Wan2.1/issues/369), first frames of long videos flicker/colour-shift. weathon isolated it: removing the first latent frame before decode does *not* fix it, but dropping the first 5 decoded pixel frames does →
> "Seems like it is a problem of the VAE not the DiT" … "After reading the wan paper, I think this is due to the fact that **wan vae treats the first frame differently**"

**DEMONSTRATED (reconstruction-only, DiT excluded)** — [modelscope/DiffSynth-Studio #1253](https://github.com/modelscope/DiffSynth-Studio/issues/1253): "Wan2.2-VAE reconstruction exhibits a severe color discrepancy specifically on the first frame. Wan2.1-VAE does not exhibit this behavior under identical conditions." Encode→decode round-trip only, so the diffusion model is not involved at all. Unanswered.

**DEMONSTRATED (implementation invariant; engineering spec, not peer review)** — [utensils/mold #744](https://github.com/utensils/mold/issues/744), a Wan causal-3D-VAE port spec:
> "Feat-cache protocol: `CACHE_T=2` trailing frames per conv, flat cache indexed by conv-visit order (`feat_idx` counter); encode chunks 1/4/4/4 pixel frames; decode 1 latent frame per iteration"
> "**Wrong cache order/chunking ⇒ temporal seams every 4 frames.**"

That is the direct answer to your question "has anyone documented per-latent-chunk seams": yes, as a *known failure mode of getting the cache protocol wrong*. Kijai's implementation notes state the intent ("Last 2 frames from previous chunk are prepended to current chunk … allows seamless video encoding/decoding across temporal chunks without discontinuities at chunk boundaries") — so the seam is what you get when that prepend is missing or mis-ordered, e.g. in a hand-rolled or ported decode loop, or in tiled decode with too little overlap.

**Tiled decode** is the everyday version of the same bug: `VAEDecodeTiled`'s `temporal_size` / `temporal_overlap` govern it, and the documented guidance is `temporal_overlap ≥ 8` to avoid choppy output ([ComfyUI docs](https://docs.comfy.org/built-in-nodes/VAEDecodeTiled)).

**LTX, 8-frame quantum** — [IAMCCS-nodes #12](https://github.com/IAMCCS/IAMCCS-nodes/issues/12): adding a last-frame guide "produces artifacts at the end. The only solution that completely eliminates the problem is to use LTXVAddGuide to **add 8 frames and then trim that last 8 frames** after generation." Maintainer confirmed: "Yes, trimming the extra tail is the correct solution, and this is already built into my IAMCCS workflows." One latent frame's worth, discarded.

### Sliding windows / context windows

If anything in your chain splits the clip and re-joins it, joins are where discontinuities live by construction. Kosinkadink (AnimateDiff-Evolved author) on why non-looped contexts drift, [issue #296](https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved/issues/296):
> "Without FreeNoise, the contexts are sorta unshackled due to the initial noise being different, so in pure text2img scenarios, it's a bit random in how much each context could change (especially when overlap is low)."

His recommendation: always use `FreeNoise` or `repeated_context` noise types for anything past 16 frames. WanVideoWrapper's context options work the same way — split into windows, **blend** the overlaps ([node docs](https://www.runcomfy.com/comfyui-nodes/ComfyUI-WanVideoWrapper/wan-video-context-options)). Blending overlaps is *literally* a crossfade at the join.

**Papers, weaker:** [VideoGuide, arXiv:2410.04364](https://arxiv.org/abs/2410.04364) Fig. 14 (Appendix E) is titled "VideoGuide helps solve the issue of sudden frame shifts in LaVie samples" — the artifact is named and shown but **no mechanism and no frame indices are given**. [Prompt to Progression, arXiv:2509.19690](https://arxiv.org/html/2509.19690) targets abrupt-vs-gradual attribute transitions but attributes them to a prompt-space "distance effect", and its defect is smeared distortion across frames rather than a single-frame jump. Neither is a good fit for your bug.

---

## 5. One blended / crossfaded frame at a transition — what that signature actually means

Ranked by how cleanly the evidence ties a *single* mixed frame to a cause:

**1. Frame-rate conversion with blending (DEMONSTRATED, ffmpeg docs).** `minterpolate` in `mi_mode=blend` is defined as: **"the interpolated frame is the mean of previous and next frames"** ([ffmpeg filters docs](https://ffmpeg.org/ffmpeg-filters.html), [minterpolate reference](https://ayosec.github.io/ffmpeg-filters-docs/8.0/Filters/Video/minterpolate.html)). That is exactly one crossfaded frame per insertion point. Meanwhile the plain `fps` filter **duplicates and drops, never blends** ([vf_fps.c](https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_fps.c), [DeLaHunt's annotated docs](https://blog.jdlh.com/en/2020/04/30/ffmpeg-fps-documented/)) — which produces *stepped* motion **without** a blend frame. **Stepped motion plus one blended frame is the signature of a non-integer frame-rate conversion where duplication and blending are both in play.** If any part of your chain retimes 16 fps → 24/30 fps, check it before you touch the sampler. This is the cheapest hypothesis to falsify: count the distinct frames in the raw model output before any mux.

**2. RIFE / FILM interpolation across a detected or missed cut (DEMONSTRATED, SVP docs).** RIFE uses a scene-change threshold; set too high, it interpolates across a discontinuity and produces **ghosting — "a translucent second image of a moving subject appears alongside the primary subject"**; set too low, false detections cause **"stuttering" (repeated frames)** ([SVP RIFE wiki](https://www.svp-team.com/wiki/RIFE_AI_interpolation)).

**3. VAE causal-conv cache at a chunk boundary (MECHANISM, documented cache; artifact not directly documented).** With `CACHE_T=2`, the decoder's output at a chunk boundary is a function of both the previous chunk's trailing latents and the current one. A frame that is mathematically a mixture of two latent states is a mechanically plausible source of exactly one "blended-looking" frame at each 4-frame boundary. I could not find anyone who has isolated and published this specific artifact, so treat the mechanism as sound and the attribution as unproven.

**4. Mismatched high/low-noise expert LoRAs (FOLKLORE, but a specific self-diagnosis).** [lightx2v discussion #25](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/25): lynn03 "In my videos, the image is duplicated with a ghost effect"; RJBlinx found the cause in his own graph — "the `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors` in the LoraLoaderModelOnly Node **had changed to the `low_noise` file by itself**. So I was running 2x low_noise loras instead of 1 high and 1 low, **which could produce ghosting effect**." Worth a 30-second check of your LoRA wiring.

**5. Generic few-step ghosting (DEMONSTRATED as a category only).** MoGAN names "ghosting" among the defects of few-step video diffusion ([arXiv:2511.21592](https://arxiv.org/abs/2511.21592)) but does not localize it to single frames.

---

## Suggested diagnostic order

Cheapest-first, and note that the first three cost nothing and don't require re-rendering:

1. **Dump the raw per-frame PNGs from the model output, before any mux, retime or interpolation, and find the exact frame index of the pop.** Everything below hinges on that number.
2. **If the pop is at frames 1–4** (or any 4k boundary for Wan, 8k for LTX): it is a latent-chunk / conditioning-boundary artifact. Go to the conditioning-strength knob (Wan `start_latent_strength`, LTX `LTXVAddGuide` `strength` / `crf`), per [#295](https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/295) and the ALG shortcut result. **Do not** change the sampler.
3. **If the blended frame survives in the raw dump, it's the model or the VAE. If it only appears after mux, it's ffmpeg** — check for `minterpolate`, `framerate`, or a non-integer fps change. Also confirm your frame count is 4n+1 (Wan) or 8n+1 (LTX).
4. **If the pop is at a window/context-window boundary:** raise overlap, or enable FreeNoise/`repeated_context`.
5. **Only then** attack the "rest is static" half, which is the well-documented one: raise steps, drop speed-LoRA strength on the **high-noise expert** to 0.6–0.8 (keep 1.0 on low), and switch off `karras`/`exponential` sigmas in favour of `simple`/`beta`/`linear_quadratic` so the schedule actually spends steps where motion is decided.

**Sources:** [kijai #124](https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/124) · [kijai #257](https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/257) · [kijai #295](https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/295) · [UniPC paper](https://arxiv.org/pdf/2302.04867) · [diffusers UniPC](https://huggingface.co/docs/diffusers/en/api/schedulers/unipc) · [Civitai Wan 2.2 sampler tests](https://civitai.com/models/1937373/wan-22-14b-i2v-tests-of-sampler-setting-with-and-without-speed-loras) · [Movie Gen](https://arxiv.org/html/2410.13720v1) · [LTX-Video paper](https://arxiv.org/abs/2501.00103) · [LTX distilled config](https://github.com/Lightricks/LTX-Video/blob/main/configs/ltxv-13b-0.9.8-distilled.yaml) · [ComfyUI samplers.py](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/samplers.py) · [Wan2.2-I2V-A14B card](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B) · [WanMoEScheduler](https://github.com/cmeka/ComfyUI-WanMoEScheduler) · [Replicate sweep](https://replicate.com/blog/wan-21-parameter-sweep) · [lightx2v #5](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/5) · [#13](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/13) · [#14](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/14) · [#20](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/20) · [#25](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/25) · [#26](https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/26) · [docs.comfy.org Wan2.2 Fun Control](https://docs.comfy.org/tutorials/video/wan/wan2-2-fun-control) · [Adaptive Video Distillation](https://arxiv.org/html/2603.21864v1) · [MoGAN](https://arxiv.org/abs/2511.21592) · [ALG](https://arxiv.org/html/2506.08456v1) · [Wan tech report](https://arxiv.org/pdf/2503.20314) · [Kijai VAE internals](https://deepwiki.com/kijai/ComfyUI-WanVideoWrapper/4.4-vae-and-latent-processing) · [Kijai fp8 discussion #31](https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/discussions/31) · [Wan2.1 #369](https://github.com/Wan-Video/Wan2.1/issues/369) · [DiffSynth #1253](https://github.com/modelscope/DiffSynth-Studio/issues/1253) · [mold #744](https://github.com/utensils/mold/issues/744) · [LTXVAddGuide docs](https://docs.comfy.org/built-in-nodes/LTXVAddGuide) · [IAMCCS #12](https://github.com/IAMCCS/IAMCCS-nodes/issues/12) · [VAEDecodeTiled docs](https://docs.comfy.org/built-in-nodes/VAEDecodeTiled) · [AnimateDiff-Evolved #296](https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved/issues/296) · [WanVideo Context Options](https://www.runcomfy.com/comfyui-nodes/ComfyUI-WanVideoWrapper/wan-video-context-options) · [VideoGuide](https://arxiv.org/abs/2410.04364) · [Prompt to Progression](https://arxiv.org/html/2509.19690) · [ffmpeg filters](https://ffmpeg.org/ffmpeg-filters.html) · [vf_fps.c](https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_fps.c) · [fps filter documented](https://blog.jdlh.com/en/2020/04/30/ffmpeg-fps-documented/) · [SVP RIFE wiki](https://www.svp-team.com/wiki/RIFE_AI_interpolation) · [Stable-Video-Infinity #66](https://github.com/vita-epfl/Stable-Video-Infinity/issues/66)
