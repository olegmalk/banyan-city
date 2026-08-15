# LTX-2.3 distilled: why the picture holds, and what is actually documented

Research pass, 2026-08-15. **No renders, no enqueues, no recipe change was made by this
pass.** Everything below is either (a) fetched from a primary source with the URL given,
(b) measured read-only on clips that already exist on this disk, or (c) explicitly
labelled UNKNOWN.

Rule applied throughout, because a previous steward relayed maintainer quotes that did
not exist: **every quote here was fetched during this pass and the URL is given.** Where
I could not find a source I wrote "no source found" instead of reconstructing something
plausible.

Our recipe under examination: LTX-2.3 22B **distilled**, diffusers, RTX 5090, 704x1280,
97 frames, 24 fps, two-stage (8 steps @352x640 -> 2x latent upsample -> 3 steps
@704x1280), distilled sigmas, guidance 2.0, image-crf 33, sequential CPU offload,
**VAE tiling on**.

---

## 0. The one-line answer

**13 latents for 97 frames is exactly correct and is not our bug.** The 2-3 frame hold is
*not* the latent grid either — the latent grid is period-**8**, and we measure period-**3**.
The strongest *sourced* candidate for the hold is on the **decode** side, not the denoise
side: Lightricks has publicly acknowledged an encode->decode "ghosting/image duplication"
defect in the LTX-2 VAE, and there are two independent community bug reports that the
**tiled** LTX-2 VAE specifically produces ghosting between temporal chunks. We run tiled
VAE in every mode. That is testable with **zero generation** — replay latents we already
capture through an untiled decode.

Separately, and independently: our `cadence` metric is **mathematically incapable** of
seeing a 3-frame hold. Proven below with a four-line reproduction.

---

## 1. What sets the temporal resolution of an LTX generation

### 1.1 The compression ratio — DOCUMENTED

The VAE config of the exact repo we load the VAE from,
<https://huggingface.co/diffusers/LTX-2.3-Diffusers/raw/main/vae/config.json>:

```json
"_class_name": "AutoencoderKLLTX2Video",
"patch_size": 4,
"patch_size_t": 1,
"latent_channels": 128,
"spatial_compression_ratio": 32,
"temporal_compression_ratio": 8,
"downsample_type": ["spatial", "temporal", "spatiotemporal", "spatiotemporal"],
"upsample_factor": [2, 2, 1, 2],
"upsample_type": ["spatiotemporal", "spatiotemporal", "temporal", "spatial"]
```

The LTX-Video paper agrees for the 0.9.x generation — "LTX-Video: Realtime Video Latent
Diffusion", HaCohen et al., <https://arxiv.org/abs/2501.00103>, which states a compression
ratio of **"1:192"** and **"32 x 32 x 8 pixels per token"**. So 32x spatial, 8x temporal,
unchanged from 0.9.x to 2.3 as far as the config shows.

### 1.2 The arithmetic — DOCUMENTED

diffusers' own LTX-2 pipeline,
<https://github.com/huggingface/diffusers/blob/main/src/diffusers/pipelines/ltx2/pipeline_ltx2.py>,
computes it verbatim as:

```python
latent_num_frames = (num_frames - 1) // self.vae_temporal_compression_ratio + 1
```

(the same line appears again inside `prepare_latents`). Therefore:

    (97 - 1) // 8 + 1 = 13

**13 is the expected, correct value. It is not a misconfiguration.** For reference:
121 frames -> 16 latents, 161 -> 21, 193 -> 25, 65 -> 9.

The LTX-2 model card states the input rule: **"Frame count must be divisible by 8 + 1"**
and "Width & height settings must be divisible by 32"
(<https://huggingface.co/Lightricks/LTX-2>, same text on
<https://huggingface.co/Lightricks/LTX-2.3>). 97 = 8x12 + 1, in spec. Note the diffusers
pipeline **does not validate** `num_frames` — it validates only `height`/`width` % 32 and
raises `ValueError` there — so an out-of-spec frame count would silently floor rather than
error. Ours is in spec, so this is not biting us, but it is worth knowing.

### 1.3 "13 latent timesteps" names the wrong thing

Latent frames and denoising steps are orthogonal quantities. The 13 is the **temporal
extent of the latent tensor** (13 x 22 x 40 x 128 at 704x1280), not a step count. With
`patch_size_t: 1` the transformer sees 13 temporal positions, each covering 8 output
frames = **0.333 s of screen time per latent frame** at 24 fps. Our log line calling them
"latent timesteps" is a naming bug in our code, not a model property.

### 1.4 The consequence that actually matters

**The latent grid is period-8. We measure period-3.** So the hold is *not* the temporal
compression grid showing through — if it were, held runs would be 8 frames long and would
align to latent-frame boundaries. This is the same conclusion the 2026-08-06 pass reached
internally ("LTX-2's documented 8x temporal VAE predicts period-8, not period-3") and
external sources do not overturn it. **The mechanism for period-3 is not explained by the
compression ratio.** See §2.3 for the best-sourced candidate.

---

## 2. Is the hold a known characteristic?

### 2.1 DOCUMENTED: the distilled checkpoint trades something away, in Lightricks' words

<https://huggingface.co/diffusers/LTX-2.3-Distilled-Diffusers> — the distilled model runs
in "8 steps with CFG = 1, **trading some flexibility for substantially faster
inference**". That is the only official statement of the tradeoff I found; it does not say
"motion". No source found for an official Lightricks statement that the distilled
checkpoint has less motion than dev.

### 2.2 DOCUMENTED: Lightricks' own docs say CFG costs motion, and the distilled recipe turns off both motion knobs

This is the strongest documented finding in the whole pass.

<https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-pipelines/docs/multimodal-guidance.md>:

> "Higher `cfg_scale` = stronger prompt adherence but potentially **less natural motion**;
> higher `stg_scale` = better temporal coherence but slower inference."

Independently, the STG paper — "Spatiotemporal Skip Guidance for Enhanced Video Diffusion
Sampling", Hyung et al., <https://arxiv.org/abs/2411.18664> — opens its abstract with:

> "While sampling guidance techniques like CFG improve quality, **they reduce diversity and
> motion**."

Now compare the two official multi-scale configs in the Lightricks repo. **Distilled**
(<https://github.com/Lightricks/LTX-Video/blob/main/configs/ltxv-13b-0.9.8-distilled.yaml>):

```yaml
first_pass:
  timesteps: [1.0000, 0.9937, 0.9875, 0.9812, 0.9750, 0.9094, 0.7250]
  guidance_scale: 1
  stg_scale: 0
second_pass:
  timesteps: [0.9094, 0.7250, 0.4219]
  guidance_scale: 1
  stg_scale: 0
```

**Dev** (<https://github.com/Lightricks/LTX-Video/blob/main/configs/ltxv-13b-0.9.8-dev.yaml>):

```yaml
first_pass:
  guidance_scale: [1, 1, 6, 8, 6, 1, 1]
  stg_scale:      [0, 0, 4, 4, 4, 2, 1]
  skip_block_list: [[], [11, 25, 35, 39], [22, 35, 39], [28], [28], [28], [28]]
  num_inference_steps: 30
second_pass:
  guidance_scale: [1]
  stg_scale: [1]
  skip_block_list: [27]
```

Two things fall out:

1. **Our two-stage pattern is the official one.** Distilled first pass = 7 timesteps at a
   downscaled resolution, second pass = 3 timesteps at full resolution through a spatial
   upsampler. Ours is 8 + 3 with a 0.5 downscale against their 0.6667. **The two-stage
   shape is not the problem** and should stop being a suspect.
2. **On the distilled path, `stg_scale` is 0 in both passes.** The one lever Lightricks'
   own documentation associates with temporal behaviour, and the one a Lightricks
   collaborator names when asked how to get more motion (§3.1), is **switched off by
   construction in the distilled recipe** and scheduled up to 4 in the dev recipe. If STG
   is the motion lever, *the distilled checkpoint as shipped does not use it.*

**Our recipe runs guidance 2.0, not the documented 1.0.** On the distilled path CFG is
what activates our negative prompt (which contains 静态 / 静止, "static"/"motionless"),
so 2.0 was presumably chosen deliberately to make that negative bite. Per both sources
above, raising CFG is documented to cost motion. This is a real documented divergence —
though note the brief says the recipe is closed by many samples, so treat it as a
must-recheck rather than a discovery (lever L4).

### 2.3 DOCUMENTED-ish: an acknowledged VAE encode->decode duplication defect

<https://github.com/Lightricks/LTX-2/issues/86> ("ltx2's VAE is BUGGED", **closed as
completed**). Issue body, verbatim:

> "We found that during data prepare for training, just do encode -> decode a video and
> see for yourself. It has this strange **ghosting/image duplication** effect that causes
> undesirable effects at video."

Reply from `rluxemburg` (author_association NONE in the API, but the same handle closed
the official LTX-2.3 HF discussion on behalf of the LTX.io org, so read this as a
Lightricks person speaking informally, not as a formal maintainer statement):

> "We're working on revisions to the VAE for the next release of LTX-2
> (info here). In the meantime, yes, take a look at the work Kijai has done."

That is an **acknowledged image-duplication defect reachable by a pure VAE round trip,
with no denoiser involved at all.** It is the single best-sourced candidate for a held
picture that the denoiser did not intend.

### 2.4 COMMUNITY: the tiled VAE specifically

Two independent reports, different projects:

- <https://github.com/Comfy-Org/ComfyUI/issues/11767> — "[bug] vae encode tiled is bugged
  with ltx2 and causes **ghosting in between temporal chunk**." State: open, labelled
  "Potential Bug". Workflow described: "load video -> encode tiled -> vae decode tiled ->
  video." Reporter's workaround is increasing temporal tile size to avoid gaps.
- <https://github.com/deepbeepmeep/Wan2GP/issues/1738> — "LTX-2.3 Tiled VAE artifacts,
  grid and ghosting - v11.35" (closed). In the thread, `JELSTUDIO` reports the same
  ghosting reproduces in official LTX-desktop, i.e. not a Wan2GP bug; `Eklipsis` reports
  ComfyUI does **not** show it and speculates ComfyUI chunks time differently; `Eklipsis`
  names the VAE as the likely source. 4+ distinct participants.

**We run VAE tiling on in every mode** (`pipeline/ltx_i2v.py` keeps it enabled to hold the
704x1280 decode inside VRAM). We are therefore in exactly the configuration two separate
projects report ghosting from. This is the highest-value untested lever in the document.

Caveat, stated plainly: **none of these reports says "the picture holds for 3 frames."**
They say ghosting/duplication. The connection to our period-3 measurement is a
**hypothesis**, not a sourced fact — but it is cheap and decisive to test (L1, L2).

### 2.5 COMMUNITY: static output generally

- <https://github.com/Lightricks/LTX-2/issues/117> "Static video" — open, 4 comments, all
  from non-maintainers, **no maintainer answer**. Users report confusion at static
  results; one links a suggestion that the *default negative prompt* may be matching the
  input image.
- <https://github.com/Lightricks/LTX-2/issues/135> "keypoint interpolation generates
  static images" — open.
- <https://github.com/Lightricks/LTX-2/issues/156> "Text artifacts, slow motion, and
  temporal incoherence" — open, 1 comment.
- <https://github.com/Lightricks/LTX-Video/issues/170> — "Sageattn and the 13B results in
  a static image", 0 comments. If SageAttention is in our stack this is worth an eye; if
  not, ignore.
- <https://github.com/deepbeepmeep/Wan2GP/issues/1738>, comment by `JELSTUDIO`: LTX **2.0**
  distilled produces fewer artifacts than LTX **2.3** distilled, and motion-related
  artifacts make practical video work hard. Single report, unverified.

So: "LTX goes static" is a **recurring community complaint with no official
acknowledgement or fix**. It is not documented behaviour and it is not folklore either —
it is an open, unanswered class of report.

### 2.6 Is step-distillation the mechanism? UNKNOWN, and probably not the whole story

The general claim — distillation trades diversity and motion for step count — is supported
for guidance specifically (STG abstract, §2.2: CFG "reduce[s] diversity and motion", and
distilled models bake guidance in). I did **not** find a primary source stating that
*step*-distillation of a video diffusion model reduces motion magnitude. No source found.
I am deliberately not reaching for the Wan "Lightning/CausVid LoRA kills motion" analogue
without having fetched it in this pass.

More decisively: a distillation story predicts *less* motion, smoothly. It does not
predict a **clean period-3 comb** with lag-1/2/4/5 autocorrelation at **-0.42**. Negative
autocorrelation at lag 1 means consecutive pairs actively anti-correlate — one pair moves,
two do not, repeating. That is a *quantisation* signature, not a weak-motion signature.
This is the strongest argument that the hold is a decode/temporal artefact rather than the
denoiser simply being lazy.

### 2.7 Already closed, do not re-chase

<https://github.com/Lightricks/LTX-2/issues/148> ("Artifacting at end of video with
LTX-2.3", 5 comments) and
<https://huggingface.co/Lightricks/LTX-2.3/discussions/13> — end-of-clip garbled
text/logo artifacts. Officially resolved by `rluxemburg` (LTX.io) pointing to
`ltx-2.3-spatial-upscaler-x2-1.1.safetensors`. **We already load the 1.1 upscaler**, so
this thread is closed for us. The alternative sigma schedules posted in that discussion
target *that* artifact, not motion — do not import them as a motion fix.

---

## 3. What practitioners actually do

### 3.1 STG — the only maintainer answer to this exact question that exists

<https://github.com/Lightricks/LTX-Video/issues/184>, titled "For the ltx13B model, how to
increase the motion size of the generated video?". First reply, from **`ybitterman`,
author_association COLLABORATOR** (Yaki Bitterman is a listed author on the LTX-Video
paper), verbatim and in full:

> "Playing with the STG blocks will help with that. There's a lot of info about it in the
> Discord server: https://discord.gg/Mn8BRgUKKy"

That is the entire maintainer answer. It is real, it is short, and it is the only one.
Everything else in that thread is from non-maintainers (see §3.2).

What STG is: <https://arxiv.org/abs/2411.18664>, Hyung, Kim, Hong, Kim, Choo. Abstract,
verbatim: "STG employs an implicit weak model via self-perturbation... By selectively
skipping spatiotemporal layers, STG produces an aligned, degraded version of the original
model to boost sample quality **without compromising diversity or dynamic degree**."

Where it lives in LTX: `stg_mode` ("attention_values", "attention_skip", "residual",
"transformer_block"), `stg_scale`, `skip_block_list` in the 0.9.8 configs above; and in
LTX-2 as `MultiModalGuiderParams(stg_scale=..., stg_blocks=[...])` documented at
<https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-pipelines/docs/multimodal-guidance.md>
(typical `stg_scale` 0.5-1.5, disable at 0.0; `stg_blocks` e.g. `[29]` for the last block;
also `rescale_scale` 0.5-0.7 to prevent over-saturation when guidance is raised).

**Status: DOCUMENTED lever, maintainer-endorsed for this exact symptom, currently at 0 in
our recipe because the distilled config sets it to 0.** Whether the diffusers LTX2
pipeline we call even exposes `stg_scale` — as opposed to the `ltx-pipelines` package —
is **UNKNOWN and must be checked in the installed diffusers source before anyone plans a
sample.**

### 3.2 Conditioning-image CRF and motion cues in the plate

Same thread, <https://github.com/Lightricks/LTX-Video/issues/184>, from `Shecht-ltx`
(author_association NONE, but the handle carries the `-ltx` suffix; treat as
semi-official at best), verbatim:

> "@Shuaizhang7 Hi! You should try **increasing the CRF** and also **if the initial frames
> contains motion cues (such as motion blur) it may help**"

and, when asked how much:

> "Try to increase from 30 to 35"

We run **image-crf 33**, i.e. already inside the band they name. Two readings:

- The CRF number itself is near-exhausted as a lever (33 of a suggested 30->35).
- The **second half of that sentence is untested by us**: our init plates are clean,
  crisp, motion-blur-free stills. The advice is that a plate *containing motion cues*
  helps. The brief says the init plate is not a motion lever — but what was measured was
  *onset* (9/10 clips start inside 0.25 s) and *which plate*, not *whether the plate
  depicts blur*. Those are different claims. Flagged as L5, honestly labelled
  semi-official.

### 3.3 Prompting — DOCUMENTED, and we are well outside the guidance

<https://github.com/Lightricks/LTX-2> README: prompts should "focus on detailed,
chronological descriptions of actions and scenes" and **"Keep within 200 words"**.

Our worst prompt is 684 Gemma-3 tokens, roughly 500 words — about **2.5x the documented
ceiling**. This is not truncation (the encoder limit is 1024 tokens and nothing is cut);
it is being outside the regime the authors say the model wants. The 0.9.8 configs
corroborate that long prompts are treated as unusual: both set
`prompt_enhancement_words_threshold: 120`, i.e. under 120 words they *expand* the prompt.

Community prompting guides (secondary sources, not Lightricks: RunDiffusion, crepal.ai,
dreampixelforge, surfaced via search) converge on "single flowing paragraph, present
tense, name the camera move and when it happens, and describe how subjects look *after*
the move so the model completes it rather than abandoning it halfway." The
"abandoning it halfway" framing maps suspiciously well onto "no figure is still acting
after frame 64", but **the official ltx.io prompt guides were unfetchable this pass (403
and header-overflow errors)**, so I am labelling this **COMMUNITY/unverified** rather than
documented. No verbatim official quote obtained.

### 3.4 Distilled vs dev

Community, from <https://github.com/deepbeepmeep/Wan2GP/issues/1738>, `jizzy1978-maker`,
a settings recommendation given for the ghosting/motion complaints: use the LTX **DEV**
model (not distilled), the **HQ res2s** sampler, **matching input and output resolution
exactly**, 25 fps at the p1 refinement stage. Single report; the "matching input/output
resolution exactly" point cuts against our 352x640 -> 704x1280 two-stage and is worth
noting, though it contradicts Lightricks' own multi-scale configs which downscale by
0.6667. **Unverified, one reporter.**

Official side: the dev config schedules `stg_scale` up to 4 and `guidance_scale` up to 8;
the distilled config uses neither (§2.2). So there is a **documented capability gap**, not
merely a quality gap. **No source found** for a controlled side-by-side of distilled vs
dev motion.

### 3.5 Frame count and fps

No source found for any documented interaction between `num_frames`, `fps` and the
compression ratio beyond the 8k+1 rule. `frame_rate` is passed to the pipeline as a float
and 24.0 is what the official examples use. LTX-2 additionally has a "Duration Head" that
"lets you omit `--num-frames` and have the clip length predicted from the prompt"
(<https://github.com/Lightricks/LTX-2>) — interesting, unexplored, not obviously a motion
lever.

### 3.6 What I checked and found nothing on

- No source found: an official maximum sustained-action duration, or any statement that
  the second half of an LTX clip goes static.
- No source found: any Lightricks statement that the distilled checkpoint is for preview
  only.
- No source found: anyone reporting a *period-3* frame hold in LTX specifically. Our
  2026-08-06 lag-3 measurement appears to be the only instance of that number anywhere I
  could reach.
- Note for honesty: <https://github.com/Lightricks/LTX-2/issues/202> and
  <https://github.com/Lightricks/LTX-2/issues/275> read like our own filings. **Do not
  cite our own issues back to ourselves as external corroboration.**

---

## 4. How motion should actually be measured

### 4.1 Why `cadence` failed — proven, not hypothesised

`pipeline/coldread_frames.py` computes `cadence` as the ratio of mean per-pair luma MAD on
**even-indexed** pairs to **odd-indexed** pairs inside the motion window. That is a
**parity-2 detector**. Feeding it synthetic series with a loud pair every N:

| true hold period | cadence reads |
|---|---|
| 2 | 26.67x |
| 3 | **1.00x** |
| 4 | 14.12x |
| 5 | **1.00x** |
| 6 | 9.56x |

Reproduction (run this pass, 4 lines, no dependencies beyond numpy):

```python
d = np.array([8.0 if i % period == 0 else 0.3 for i in range(90)])
idx = np.arange(len(d)); ev, od = d[idx % 2 == 0], d[idx % 2 == 1]
lo, qu = (ev, od) if ev.mean() >= od.mean() else (od, ev)
cadence = lo.mean() / qu.mean()
```

**Every odd hold period aliases to exactly 1.00x** — the loud pairs distribute evenly
across both parities, so the ratio is 1 by construction. The 1.06x reading was not a
measurement error or a noise problem. The metric **cannot** represent a 3-frame hold. It
detects period 2, 4 and 6 and is blind to 3 and 5. It must not be trusted as a
freeze detector again in its present form.

This is also exactly the failure mode VBench guards against: its `temporal_flickering`
dimension is MAE between consecutive frames
(<https://github.com/Vchitect/VBench/blob/master/vbench/temporal_flickering.py>, functions
`mae_seq` / `calculate_mae`), and the VBench README states that static videos must be
**filtered out before** evaluating temporal flickering, because they would score well on
it. Frame-difference metrics reward stillness; that is a known property, not our discovery.

### 4.2 The fix, validated on our own clips this pass

**Autocorrelation of the per-pair difference series.** The peak lag *is* the hold period,
for any period, and it is scale-free. Measured read-only on existing files (per-pair mean
absolute luma difference, then autocorrelation of the mean-removed series):

| clip | lag1 | lag2 | lag3 | lag4 | lag5 | lag6 | verdict |
|---|---|---|---|---|---|---|---|
| `0815-b13-AFTER.mp4` | -0.42 | -0.41 | **0.97** | -0.41 | -0.41 | 0.92 | clean period-3 hold |
| `0815-b13-BEFORE.mp4` | 0.20 | 0.28 | **0.61** | 0.14 | 0.19 | 0.37 | weaker period-3 |
| `0814-b10-candidate.mp4` | 0.16 | **0.88** | 0.13 | 0.79 | 0.09 | 0.69 | period-2 hold |

Two properties worth having:

- It separates the two failure shapes that `cadence` conflates — b13 is period-3
  (cadence-invisible), b10 is period-2 (cadence-visible). Both are holds.
- It is **robust to resolution**: computed at 352x640 and at 88x160 the lag-3 value moves
  from 0.97 to 0.96. So it can be run on an 1/8-scale decode, which also suppresses the
  1-2px line-work churn that inflates raw MAD on anime line art. That churn is precisely
  what made the clip look like it was moving.

Cost: one ffmpeg pipe to grayscale rawvideo plus numpy. No model, no flow, no GPU, ~1 s.

### 4.3 ffmpeg `mpdecimate` — useful, but not sufficient alone

Verified locally (`ffmpeg -h filter=mpdecimate`, ffmpeg 8.x, homebrew): options `hi`
(default 768), `lo` (default 320), `frac` (default 0.33), `max`, `keep`. `freezedetect`
takes `n` (noise tolerance, default 0.001) and `d` (minimum duration, default **2
seconds**).

Run at defaults on our clips: `0815-b13-AFTER.mp4` keeps **83 of 97** frames,
`0815-b13-BEFORE.mp4` keeps **65 of 97**, `0814-b10-candidate.mp4` keeps 97 of 121. So
mpdecimate at stock thresholds **does not** report a clean 3x hold — the line-work churn
exceeds its duplicate thresholds. It is a genuine signal (b13-BEFORE dropping a third of
its frames is meaningful) but it answers "are frames byte-similar", not "how many distinct
pictures are there". `freezedetect`'s default `d=2` is longer than the entire hold, so it
would need `d=0.1` to be relevant at all.

**Ranking for our purpose — "would this catch a clip that holds every picture for 3
frames":**

1. **Autocorrelation of the frame-difference series at 1/8 scale** — yes, cleanly, 0.97.
   $0, seconds, no dependencies. Validated above on our files.
2. **mpdecimate frame-drop ratio** — partially; a strong secondary signal, needs threshold
   tuning for line art, reports a ratio not a period.
3. **VBench `dynamic_degree`** — would catch it, but coarsely. Source read at
   <https://github.com/Vchitect/VBench/blob/master/vbench/dynamic_degree.py>: it runs
   **RAFT** optical flow, takes `rad = sqrt(u^2 + v^2)`, scores the **mean of the top 5%**
   flow magnitudes per pair, thresholds at `6.0 * (scale/256.0)` where scale is the
   smaller frame dimension, and calls the video dynamic only if the number of pairs over
   threshold reaches `4 * (count/16.0)`. It returns a **boolean per video**, not a period,
   and it needs a RAFT checkpoint. Good as a gate, useless as a diagnostic.
4. **`cadence` in its present form** — no. Structurally blind to odd periods.

Also from VBench source, for anyone tempted to add "quality" metrics: `subject_consistency`
is DINO-feature similarity between frames and `motion_smoothness` is AMT frame
interpolation error — **both score a frozen clip as excellent**. They must never be read
without `dynamic_degree` beside them.

No source found for a motion metric designed specifically for anime/line-art generated
video. The 1/8-downscale trick above is our own mitigation, validated only on our clips.

---

## 5. Ranked, testable levers

Every one of these is a **single sample or a zero-generation measurement**, per the
one-sample rule. None is a step or guidance tweak except L4, which is included only
because two primary sources name CFG as a motion cost.

**L1 — Decode existing latents with VAE tiling OFF. Zero generation.**
Source: <https://github.com/Comfy-Org/ComfyUI/issues/11767> (tiled LTX2 VAE causes
"ghosting in between temporal chunk") + <https://github.com/deepbeepmeep/Wan2GP/issues/1738>
(same, and reproduces in official LTX-desktop) + <https://github.com/Lightricks/LTX-2/issues/86>
(Lightricks person acknowledges an encode->decode duplication defect, VAE revisions in
progress). We run tiling on in every mode.
*A single sample would show:* replay one already-captured latent tensor through an untiled
decode and take the lag-3 autocorrelation. If it drops from 0.97 toward 0, **the hold is
our tiling and the denoiser was never the problem.** If it stays at 0.97, the decode side
is exonerated in one measurement and every future lane can stop looking there.

**L2 — VAE round-trip a real moving video. Zero generation, no denoiser at all.**
Source: <https://github.com/Lightricks/LTX-2/issues/86> — "just do encode -> decode a video
and see for yourself."
*A single sample would show:* encode any real 97-frame clip with genuine motion through
the LTX-2.3 VAE and decode it, then measure lag-3 autocorrelation on input and output. If
the round trip *imposes* period-3 on footage that did not have it, the mechanism is the
VAE, full stop, and no prompt or sampler work can ever fix it. This is the single most
decisive experiment in this document and it generates nothing.

**L3 — Establish whether `stg_scale` is reachable at all from the diffusers LTX2 pipeline
we call. Zero generation, pure source read.**
Source: maintainer `ybitterman`, <https://github.com/Lightricks/LTX-Video/issues/184> —
"Playing with the STG blocks will help with that"; parameters documented at
<https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-pipelines/docs/multimodal-guidance.md>;
official distilled config has `stg_scale: 0`, dev config schedules it to 4.
*A single sample would show:* nothing to render — read the installed
`diffusers/pipelines/ltx2/` source for `stg_scale` / `stg_blocks` / skip-layer support. If
absent, the only maintainer-endorsed motion lever is **unavailable through our call path**,
which is itself a decision-grade finding and reframes the whole recipe question.

**L4 — guidance 2.0 -> 1.0, one clip, same seed.**
Source: <https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-pipelines/docs/multimodal-guidance.md>
("Higher `cfg_scale` = ... potentially less natural motion") + STG abstract
<https://arxiv.org/abs/2411.18664> ("CFG ... reduce diversity and motion") + the official
distilled config's `guidance_scale: 1`. Listed *only* because primary sources name it; the
brief says the recipe is closed, so this is a recheck under a new measurement, not a new
idea.
*A single sample would show:* whether the anti-static negative prompt we bought with CFG
2.0 is costing more motion than it buys. Read it with autocorrelation, not `cadence` —
this is exactly the comparison the old metric could not adjudicate.

**L5 — one init plate carrying visible motion blur.**
Source: `Shecht-ltx`, <https://github.com/Lightricks/LTX-Video/issues/184> — "if the
initial frames contains motion cues (such as motion blur) it may help". Semi-official
(handle suffix, association NONE). Distinct from the closed plate-onset question: that
measured *when* motion starts and *which* plate, not whether the plate depicts blur.
*A single sample would show:* whether a motion-blurred conditioning frame changes the hold
period or the frame-64 stall, against the same prompt and seed.

**L6 — one clip at ~200 words of prompt.**
Source: <https://github.com/Lightricks/LTX-2> README, "Keep within 200 words"; the 0.9.8
configs' `prompt_enhancement_words_threshold: 120`. We run ~500 words. Not truncation — a
documented regime we are outside of.
*A single sample would show:* whether a 200-word cut of the beat-13 prompt sustains action
past frame 64 where the 500-word one does not.

**L7 — replace `cadence` with lag-autocorrelation before any of the above is scored.**
Source: proven in §4.1 (odd periods alias to exactly 1.00x) and validated in §4.2 on three
of our own clips; corroborated in principle by VBench's own requirement to filter static
videos out before running its MAE-family `temporal_flickering`
(<https://github.com/Vchitect/VBench/blob/master/vbench/temporal_flickering.py>).
*This is a prerequisite, not an experiment.* Every lever above is scored with a number,
and the current number is structurally incapable of reporting the defect. Fix the ruler
first.

**Not levers — retired by this pass.** The two-stage 8+3 pattern (it is the official
shape, §2.2); the 13-latent count (correct arithmetic, §1.2); the end-of-clip artifact
sigmas from HF discussion 13 (they target a different artifact and we already run the 1.1
upscaler, §2.7); frame count and fps (no source found for any motion interaction, §3.5).

---

## Provenance

Written by the steward, 2026-08-15, model claude-opus-5. All URLs were fetched during this
pass; all quotes are verbatim from those fetches. The three clip measurements in §4.2 and
the mpdecimate counts in §4.3 were computed read-only on files already on disk — no
generation, no GPU, no spend. Sources that could not be fetched (ltx.io official prompt
guides, 403 / header overflow) are labelled as unverified rather than paraphrased.
