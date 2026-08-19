# Pose-class ControlNet for SDXL — external research for beat 08's pointing arm

**Lane:** external research, 2026-08-19. **Spend: $0.** No renders, no queue
filing, no downloads. Everything below is either upstream fact (linked) or a
read-only probe of machines we already own.

## Why this file exists

`pipeline/controlnet_probe.py` loads `xinsir/controlnet-scribble-sdxl-1.0` (line
80) against `cagliostrolab/animagine-xl-3.1` (line 74). That probe closed with a
mechanism verdict, not a tuning verdict: a **scribble-class** net reads
*enclosure*. Closed contours come back traced as object boundaries; an open
stick figure comes back drawn as literal glowing lines. Three axes were
bracketed and none of them changes what the net can read. Beat 08 needs an arm
**aimed by geometry** — which is a pose problem, and pose-class nets exist for
SDXL. Beat 08's second blocker is separate and is answered in §5: both figures
render goblin-green because nothing in the current pipeline binds an attribute
to a *figure*.

## Grades used

- **DEMONSTRATED** — verified here by running/inspecting the artifact, or an
  upstream artifact I opened and looked at.
- **MAINTAINER** — the author of the weights says it, on their own model card or
  in their own discussion thread. Believable, unverified by us.
- **FOLKLORE** — SEO content farms, tutorial blogs, or a claim that appears only
  as restated assertion with no image, diff or code behind it. Recorded so the
  next lane does not mistake it for evidence.

---

## 1. What pose-class ControlNets exist for SDXL

| repo | licence | files diffusers needs | bytes | last update | verdict |
|---|---|---|---|---|---|
| [`xinsir/controlnet-openpose-sdxl-1.0`](https://huggingface.co/xinsir/controlnet-openpose-sdxl-1.0) | **apache-2.0** (front-matter + body both) | `config.json`, `diffusion_pytorch_model.safetensors` | 1,235 + **2,502,139,104** | 2024-07-09 | **the pick** |
| ↳ same repo, `diffusion_pytorch_model_twins.safetensors` | apache-2.0 | needs an explicit filename load | 2,502,139,104 | 2024-07-09 | second variant, see below |
| [`thibaud/controlnet-openpose-sdxl-1.0`](https://huggingface.co/thibaud/controlnet-openpose-sdxl-1.0) | **`other` — "License: refers to the OpenPose's one"** | no `.safetensors` at the diffusers name; only `diffusion_pytorch_model.bin` | **5,004,4xx,xxx** (fp32) | 2023-09-03 | **REJECT — licence** |
| [`xinsir/controlnet-union-sdxl-1.0`](https://huggingface.co/xinsir/controlnet-union-sdxl-1.0) (pose mode) | apache-2.0 | `config.json` + 2,512 MB, **and** `ControlNetUnionModel` | 2,512 MB / 2,513 MB promax | 2024-07-30 | **REJECT — needs a diffusers we do not have** |
| `lllyasviel/*` openpose SDXL | — | — | — | — | **does not exist.** v1.1 is SD1.5/2.0. Already documented in `cnet-cache-crosswalk-0817.md`; do not re-chase it |
| [`r3gm/controlnet-openpose-sdxl-1.0-fp16`](https://huggingface.co/r3gm/controlnet-openpose-sdxl-1.0-fp16) | apache-2.0 | `diffusion_pytorch_model.fp16.safetensors` | 2,502,139,104 — **identical byte count** | 2024-06-06 | pointless mirror, see below |

Sizes and dates are **DEMONSTRATED** — pulled from the HF model API with
`?blobs=true`, not from prose.

### The three findings that actually decide this

**thibaud is a licence landmine, not a size problem.** Its model card says, in
full, *"License: refers to the OpenPose's one."* CMU OpenPose upstream is
academic / non-commercial. This repo has already ruled on exactly this hazard
once: `B01-R9-PLAN.md` §9 flags `lllyasviel/Annotators` **DO NOT USE FOR CANON**
because its per-file upstream terms inherit CMU's non-commercial OpenPose
licence. thibaud inherits the same defect at the *weights* level, where it would
attach to every frame it ever renders. xinsir is plain apache-2.0 with no
attribution condition — the same clean footing that made scribble the tier-2
default over MistoLine. **DEMONSTRATED** (I read both licence lines).

**xinsir already ships fp16/bf16, so there is no download to shave.** 2,502,139,104
bytes ÷ 2 = 1,251,069,552 ≈ the 1,251,014,160 params the crosswalk measured for
the *scribble* net. The r3gm "fp16" mirror is byte-identical in size to xinsir's
file — it is a rename, not a quantisation, and its only effect is to flip the
`variant=` trap (r3gm **requires** `variant="fp16"`; xinsir **raises** if you
pass it). Use xinsir and keep `CONTROLNET_VARIANT = None` exactly as
`controlnet_probe.py` already does. **DEMONSTRATED.**

**union is out on a version wall, not on quality.** It needs
`ControlNetUnionModel`; the box runs diffusers **0.29.2** (verified below) and
that class landed later. Same conclusion `cnet-cache-crosswalk-0817.md` reached
on 08-17; nothing has changed. **DEMONSTRATED.**

### The `twins` variant

xinsir, in [discussion #3](https://huggingface.co/xinsir/controlnet-openpose-sdxl-1.0/discussions/3),
on his own repo: twins is *"a model with similar performance and different
style"* — **more precise pose adherence, lower aesthetic score**; the default
file is prettier and looser. **MAINTAINER.** For beat 08 the whole point is that
the arm lands where geometry says, so twins is the *interesting* arm of an A/B —
but it is a second 2.5 GB download and it is not the first rung. Note it and
move on.

### Structural compatibility with animagine-xl-3.1

`xinsir/controlnet-openpose-sdxl-1.0/config.json`, fetched and parsed:

```
_class_name          ControlNetModel
_diffusers_version   0.20.0.dev0
cross_attention_dim  2048
block_out_channels   [320, 640, 1280]
addition_embed_type  text_time
```

That is **field-for-field identical** to the scribble net's config, which
`cnet-cache-crosswalk-0817.md` already measured as matching animagine-xl-3.1's
UNet (`cross_attention_dim` 2048, `block_out_channels` [320,640,1280],
`addition_embed_type: text_time`). So the openpose net **loads** against our
base for the same reason the scribble net does — no new risk on that axis.
**DEMONSTRATED.** (Loading is not reading; the probe's whole lesson is that those
are different questions.)

### Anime-checkpoint compatibility — the real answer

The concern is legitimate: both nets were finetuned from
`stabilityai/stable-diffusion-xl-base-1.0` on photo data. But xinsir's own model
card headline is *"below are the result for midjourney and anime, just for
show"*, and it ships `masonry0.webp` (6016×10000) as the anime showcase. **I
downloaded it and looked at the top band.** It is a column of side-by-side
pairs: on the left a colored-limb skeleton on pure black, on the right a clean,
fully-rendered anime figure — pink-haired girl in a white dress, a seifuku
schoolgirl, a blue-haired girl in a sundress, a girl in a school uniform with a
sword — each one matching its skeleton's pose. No photoreal bleed, no muddy
"anime-ish photo" hybrid, and the anime figures are *cleaner* than the photoreal
ones in `masonry_real.webp`. **DEMONSTRATED for anime-class SDXL checkpoints
generally; MAINTAINER as to which checkpoint** — xinsir does not name the anime
base he used, so this is not a certificate for animagine-xl-3.1 specifically.
It is, however, an existence proof that this net does not fight anime, which is
the thing that was in doubt.

Corroborating, weaker: the Civitai **ControlNetXL (CNXL)** aggregation ships
`controlnetxlCNXL_xinsirOpenpose` and `...xinsirOpenposeTwins` in a collection
built for anime/Illustrious SDXL checkpoints, alongside a
`xinsir scribble-anime` entry. Packaging is not a quality report. **FOLKLORE**
as to quality; useful only as a signal the anime community adopted it.

Searches for Animagine-specific openpose reports returned nothing but content
farms. Recorded as absent, not as negative.

---

## 2. Can the pose hint be authored in plain PIL? — YES, and here is the exact spec

**Confirmed. No preprocessor, no annotator, no `controlnet_aux`, no model.** The
hint is colored lines and dots on a black canvas, and the reference
implementation is 40 lines of geometry. This keeps the draw-hints-in-PIL
discipline intact and keeps us clear of `lllyasviel/Annotators` — which is the
one licence landmine sitting in our own cache.

Source of truth: [`controlnet_aux/open_pose/util.py :: draw_bodypose`](https://raw.githubusercontent.com/huggingface/controlnet_aux/master/src/controlnet_aux/open_pose/util.py).
**DEMONSTRATED** — fetched and read, not recalled.

**Keypoint order (COCO-18, 0-indexed).** Not taken on trust — *derived* from the
`limbSeq` table below, which is self-consistent only with this ordering:

```
0 nose        1 neck       2 R-shoulder  3 R-elbow   4 R-wrist   5 L-shoulder
6 L-elbow     7 L-wrist    8 R-hip       9 R-knee   10 R-ankle  11 L-hip
12 L-knee    13 L-ankle   14 R-eye      15 L-eye    16 R-ear    17 L-ear
```

**The shared 18-colour ramp** (RGB, exactly as in the source):

```
[255,0,0] [255,85,0] [255,170,0] [255,255,0] [170,255,0] [85,255,0]
[0,255,0] [0,255,85] [0,255,170] [0,255,255] [0,170,255] [0,85,255]
[0,0,255] [85,0,255] [170,0,255] [255,0,255] [255,0,170] [255,0,85]
```

**`limbSeq` (1-indexed in the source) zipped against that ramp — 17 limbs:**

| # | limb (0-indexed names) | colour |
|---|---|---|
| 0 | neck → R-shoulder | 255,0,0 |
| 1 | neck → L-shoulder | 255,85,0 |
| 2 | R-shoulder → R-elbow | 255,170,0 |
| 3 | **R-elbow → R-wrist** | 255,255,0 |
| 4 | L-shoulder → L-elbow | 170,255,0 |
| 5 | **L-elbow → L-wrist** | 85,255,0 |
| 6 | neck → R-hip | 0,255,0 |
| 7 | R-hip → R-knee | 0,255,85 |
| 8 | R-knee → R-ankle | 0,255,170 |
| 9 | neck → L-hip | 0,255,255 |
| 10 | L-hip → L-knee | 0,170,255 |
| 11 | L-knee → L-ankle | 0,85,255 |
| 12 | neck → nose | 0,0,255 |
| 13 | nose → R-eye | 85,0,255 |
| 14 | R-eye → R-ear | 170,0,255 |
| 15 | nose → L-eye | 255,0,255 |
| 16 | L-eye → L-ear | 255,0,170 |

`colors[17]` (`255,0,85`) is never used for a limb — it only ever appears as the
L-ear dot.

### The gotcha that will bite an author who skims

**Limb colours and dot colours index the same list differently.** Limbs are
`zip(limbSeq, colors)` — colour *i* belongs to limb *i*. Dots are
`zip(keypoints, colors)` — colour *i* belongs to **keypoint** *i*. So the nose
*dot* is `255,0,0` while the neck→R-shoulder *limb* is also `255,0,0`, and the
R-wrist dot is `170,255,0` while the R-elbow→R-wrist limb is `255,255,0`. Anyone
who writes "one colour per body part" gets a hint the net has never seen.
**DEMONSTRATED** from the source.

### Draw order and rendering rules

1. Black canvas, RGB.
2. **Limbs first, at 60 % intensity:** `int(c * 0.6)` per channel. An
   `ellipse2Poly` at the limb midpoint, major semi-axis `length/2`, minor
   semi-axis `stickwidth`, rotated to `atan2(ΔY, ΔX)` in degrees, filled convex.
   A plain PIL `line(..., width=2*stickwidth)` plus round caps is a faithful
   substitute — the ellipse is a rounded thick segment.
3. **Dots second, on top, at full intensity:** filled circle, radius `4`.
4. Missing keypoints are **skipped**, and any limb touching a missing keypoint
   is skipped. Occlusion is expressed by omission, not by a sentinel.
5. Coordinates in the reference are normalised 0–1 and multiplied by `W`/`H`.
   Ours can be authored in pixels directly.

### Line thickness is load-bearing for xinsir specifically

xinsir's own card: *"When using the default pose line the performance may be
unstable, this is because the pose label use more thick line in training to have
a better look."* He ships a replacement `draw_bodypose` whose only change is a
resolution-dependent multiplier — `stickwidth` stays 4 but the ellipse minor axis
becomes `stickwidth * ratio` and the dot radius becomes `4 * ratio`:

```
max(W,H) <  500  -> ratio 1.0
         <  1000 -> ratio 2.0
         <  2000 -> ratio 3.0     <-- our 1024-class canvases
         <  3000 -> ratio 4.0
         <  4000 -> ratio 5.0
         <  5000 -> ratio 6.0
         else       ratio 7.0
```

At a 1024-class canvas that is **ratio 3.0 → limbs ~24 px thick, dots r=12 px**.
Drawing a 4 px skeleton at 1024 is a *known* way to get an unstable result from
this net, and it would look exactly like "the net ignored the hint" — the same
symptom the scribble probe closed on. Do not reproduce that mistake by
inheriting the default. **MAINTAINER** for the claim, **DEMONSTRATED** for the
exact bands (read from the card), and independently reported by a third party in
[`comfyui_controlnet_aux#447`](https://github.com/Fannovel16/comfyui_controlnet_aux/issues/447)
("trained with non-default pose lines (and dots), they were made significantly
thicker"), still open there.

**No face/hand keypoints needed.** xinsir's recommended preprocessor call is
`hand_and_face=False`. Body-18 only. **MAINTAINER.**

---

## 3. Offline reachability

**What must be on disk: exactly two files.**

```
config.json                          1,235 bytes
diffusion_pytorch_model.safetensors  2,502,139,104 bytes
```

Total **2,502,140,339 bytes ≈ 2,386 MiB** — the same figure the crosswalk
recorded for every xinsir net already on the box. Nothing else in the repo is
load-bearing: the other 22 files are `.webp` showcase art, `README.md`,
`.gitattributes`, and the second `_twins` weight file.

**Can `ControlNetModel.from_pretrained` load them offline? Yes — already proven
on this exact machine.** `cnet-cache-crosswalk-0817.md` records
`xinsir/controlnet-scribble-sdxl-1.0` loading under `HF_HUB_OFFLINE=1` in the
box venv and reporting 1,251,014,160 params. The openpose repo has an identical
file layout and an identical `config.json` shape, so the same call path applies
with no code change beyond the constant. **DEMONSTRATED (sibling repo, same
machine).**

**Do NOT pass `variant="fp16"`.** xinsir ships the plain filename. Passing the
kwarg raises. `controlnet_probe.py` already gates this (`CONTROLNET_VARIANT =
None`); `render_b01r9.py` hardcodes `"fp16"` and would crash. Documented in the
crosswalk; restated because it is the single most likely way this rung fails on
first contact.

**Box inventory as of right now** — `dir /b` on
`C:\Users\artvn\.cache\huggingface\hub`, run read-only over ssh:

- **No openpose net of any kind is cached.** Present: xinsir canny, depth,
  scribble; diffusers depth; MistoLine. So this rung has a **real 2,386 MiB
  download**, and it is the only download it has.
- `HF_HUB_OFFLINE` blocks fetching by construction, so the download is a
  deliberate one-off with the flag cleared, run **on the box** (which has the
  network — that is how the current cache got there). Not a Mac-side transfer.
- **Pass `allow_patterns`.** A naive
  `snapshot_download("xinsir/controlnet-openpose-sdxl-1.0")` pulls **~5,014 MB**
  — both weight files plus ~10 MB of showcase webp. With
  `allow_patterns=["config.json", "diffusion_pytorch_model.safetensors"]` it is
  **2,386 MiB**. That is a 2.5 GB difference for one kwarg.

**Box venv, probed read-only just now** (`C:\banyan-farm\venv`):

```
diffusers 0.29.2
from diffusers.image_processor import IPAdapterMaskProcessor   -> OK
from diffusers import StableDiffusionXLControlNetPipeline      -> OK
"ip_adapter_image" in StableDiffusionXLControlNetPipeline.__call__ params -> True
```

**DEMONSTRATED.** That last line is the answer to §5 and it is not a guess.

---

## 4. Two figures in one hint

**Honest grade: the mechanism is sound and the maintainer has not demonstrated
it.**

**What the hint format gives us that scribble never could.** A skeleton is a set
of absolute pixel coordinates. Two skeletons in one hint therefore specify each
figure's *pixel extent* — head-top to ankle — as geometry, not as an adjective.
Our colossus fault is scale mismatch between figures; "a tall figure and a short
figure" is a prompt the model can round off, whereas two skeletons whose
neck-to-ankle spans differ by a stated ratio is a constraint in the conditioning
tensor. This is a mechanism argument from the format, and it is the strongest
reason to prefer pose over scribble for beat 08. It is not an empirical claim
and this file does not dress it as one.

**What the maintainer shows.** I opened four of xinsir's own hint→result strips
(`000010`, `000101`, `000128`, `000180`) and the top band of the anime masonry.
**Every single example is one figure.** The card makes no multi-person claim
anywhere. So: **no maintainer evidence, either way**, for two figures.
**DEMONSTRATED absence.**

**The documented failure mode, and why it may not be ours.**
[`Mikubill/sd-webui-controlnet#1791`](https://github.com/Mikubill/sd-webui-controlnet/issues/1791)
(open since 2023-07): with multiple characters, *"one person's arms and legs are
often connected to others"*, OpenPose cannot express *"which arm and which leg
belonged to whom"*, producing *"very serious bad anatomy problems"*. The
reporter's own framing pins the cause precisely: **the hint has no per-figure
identity channel and no occlusion channel.** Two skeletons are just 34 dots and
34 segments in one image; if they interpenetrate, nothing says which limb is
whose. **DEMONSTRATED** (real issue, mechanism stated, still open).

Beat 08's composition is *adjacent* figures, not overlapping ones — which is
exactly the case the failure mode does not describe. That is a reason to expect
it to work, not a reason to skip the sample. The workaround named in that thread
is multi-ControlNet (pose + depth, or pose + scribble) with staggered
`guidance_start`/`guidance_end`, so depth carries the who-is-in-front
information the skeleton cannot. Worth knowing; we already hold both depth nets
locally if it comes to that. **FOLKLORE** as to whether it helps — nobody in the
thread posted a before/after.

Content farms (crepal.ai, generativelabs.com, openlaboratory.com) assert this
net *"excels at handling complex multi-person scenes"* and offer
`controlnet_conditioning_scale` 0.5–1.5 as the multi-figure remedy. Zero images,
zero code, mutually copied phrasing. **FOLKLORE — do not cite.**

**One sample answers this in three minutes** and no amount of further reading
will. That is the whole shape of the recommendation below.

---

## 5. Identity binding — this is the good news, and it costs nothing

Beat 08's other blocker (both figures goblin-green) has a **verified, already-local**
answer: **IP-Adapter with per-region masks, composed into the same SDXL
ControlNet pipeline.**

**Upstream: officially documented, with two figures, on SDXL.** The diffusers
[IP-Adapter guide](https://huggingface.co/docs/diffusers/main/en/using-diffusers/ip_adapter)
has a *Masking* section whose worked example is literally our case — prompt
`"2 girls"`, two reference images, two binary masks, one per figure:

```py
from diffusers.image_processor import IPAdapterMaskProcessor
processor = IPAdapterMaskProcessor()
masks = processor.preprocess([mask1, mask2], height=1024, width=1024)
masks = [masks.reshape(1, masks.shape[0], masks.shape[2], masks.shape[3])]
pipeline.set_ip_adapter_scale([[0.7, 0.7]])
pipeline(prompt="2 girls",
         ip_adapter_image=[[face_image1, face_image2]],
         cross_attention_kwargs={"ip_adapter_masks": masks}).images[0]
```

The same guide's *Structural control* section states IP-Adapter combines with
ControlNet in one pipeline. **MAINTAINER** (HF's own docs; their side-by-side
"with mask / without mask" figure is the evidence).

**Ours: it composes, in the version we have, with weights we already hold.**
Probed on the box just now, read-only:

- `diffusers 0.29.2` — `IPAdapterMaskProcessor` imports.
- `StableDiffusionXLControlNetPipeline.__call__` **accepts `ip_adapter_image`**.
  One pipeline, pose control *and* per-region image conditioning. No community
  pipeline, no fork, no upgrade.
- `models--h94--IP-Adapter` is **already in the box cache and complete** — 0
  `.incomplete` files, 4 blobs, 4,074,282,584 bytes:
  - `models/image_encoder/model.safetensors` — 2,528,373,448 (ViT-H, the encoder
    the `_vit-h` adapters require)
  - `sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors` — 847,517,512
  - `sdxl_models/ip-adapter_sdxl_vit-h.safetensors` — 698,391,064

**DEMONSTRATED.** Per-figure identity binding is a **$0, zero-download** path.
The masks are ours for free too: we author the skeletons, so we know each
figure's bounding box exactly — the mask is a filled rectangle or a dilated
skeleton silhouette drawn in the same PIL pass. No segmentation model.

Only gap: `ip-adapter-plus-face_sdxl_vit-h.safetensors` (847.5 MB), the *face*
variant the docs' example uses, is **not** cached. Beat 08 needs costume and
palette separation, not face identity, so the general `plus` adapter we already
hold is the right first try. Note the download in case faces become the blocker.

### The alternatives, graded and dismissed

- **Regional prompting (attention-coupling), diffusers community pipeline** —
  hako-mikan's port exists in `examples/community` but is built on
  `StableDiffusionPipeline`: **SD1.5 only, no SDXL**. **DEMONSTRATED** from the
  community README/table.
- **`mixture_tiling_sdxl`** — real SDXL community pipeline, real per-region
  prompts, but it is a *tiling* pipeline and does not take a ControlNet. Wrong
  tool. **DEMONSTRATED.**
- **Forge Couple / Regional Prompter (A1111/Forge extensions)** — widely used
  for exactly "two characters, no colour contamination", and there is a
  [2024-03 bug report that attention mode broke](https://github.com/lllyasviel/stable-diffusion-webui-forge/issues/515).
  Both are webui extensions, not diffusers. Porting is a project, not a rung.
  **FOLKLORE** as to our stack.
- **Two-pass inpaint per figure** (generate with pose, then mask-inpaint each
  figure with its own prompt) — needs no new weights and works today, but it is
  two extra denoise passes per beat and it can break the pose it just
  established. Legitimate fallback if masked IP-Adapter underperforms; not the
  first rung.

---

## Suggested next rung, costed — a recommendation, not a filed job

**Do the two things in this order. The first is free.**

### Rung A — masked IP-Adapter on the CURRENT scribble net. $0, no download.

Everything it needs is already on the box: diffusers 0.29.2,
`IPAdapterMaskProcessor`, `ip-adapter-plus_sdxl_vit-h`, the ViT-H encoder, and a
ControlNet pipeline that accepts `ip_adapter_image`. It attacks the goblin-green
blocker **independently of the pose question**, so it is not blocked on any
download and it should start now, not after. **ONE SAMPLE:** beat 08's existing
scribble hint, two rectangular masks from the figures' known boxes, two
reference crops (one per figure's palette), `set_ip_adapter_scale([[0.7, 0.7]])`.
One image. Founder looks at whether the two figures came out visually distinct.

### Rung B — xinsir openpose, one sample.

**Download:** `xinsir/controlnet-openpose-sdxl-1.0`,
`allow_patterns=["config.json", "diffusion_pytorch_model.safetensors"]` →
**2,386 MiB / 2,502,140,339 bytes**. Skip `allow_patterns` and it is ~5,014 MB.

**Who runs it:** the **box**, itself, one `snapshot_download` with
`HF_HUB_OFFLINE` cleared for that call only. The box has the network — the
current cache is proof. Not a Mac-side download, not a courier copy. Zero
dollars; it is a public apache-2.0 repo. It is also the *only* physical
dependency in this plan, so under the no-artificial-delay rule it should fire as
soon as someone is at a prompt, and rung A runs while it lands.

**The one sample, with the three things that make it not waste an hour:**

1. **Author the hint in PIL at ratio 3.0** — limbs ~24 px, dots r=12 px at a
   1024-class canvas, per xinsir's own replacement function. A 4 px skeleton is
   a documented way to get an unstable result and would look exactly like "the
   net ignored the hint."
2. **Use the §2 colour table verbatim**, and mind that limbs and dots index the
   same 18-colour ramp *differently*.
3. **`CONTROLNET_VARIANT = None`** — do not pass `variant="fp16"`.

Sample content: **both** figures' skeletons in one hint, at their intended
scales, with beat 08's pointing arm aimed by the R-elbow→R-wrist segment
(`255,255,0`). One image, `controlnet_conditioning_scale=1.0` as the card
recommends. It answers three open questions at once — does pose bind at all on
animagine, do two skeletons produce two distinct figures, and does the stated
scale ratio survive — and it answers them in one render. Then, and only then,
consider the `twins` variant (a second 2,386 MiB, "more precise pose, lower
aesthetic score") as an A/B, and multi-ControlNet pose+depth (both depth nets
already local, $0) if the two figures fuse.

**What this rung explicitly does not do:** it does not scale to fifteen beats on
a metric. One sample, founder looks, then batch.

## Provenance

External research lane, 2026-08-19, $0. Upstream facts from HF model API
(`?blobs=true`), model cards, `controlnet_aux` source, diffusers docs and the
linked GitHub issues — every one fetched and read for this file, none recalled.
Local facts from read-only probes of the rtx5090 box (`dir /b` on the HF cache,
one `python -c` import check in `C:\banyan-farm\venv`) and from
`pipeline/research/cnet-cache-crosswalk-0817.md` and
`pipeline/controlnet_probe.py`. xinsir showcase images were downloaded and
visually inspected; the anime finding in §1 and the single-figure finding in §4
are from looking at them, not from reading about them. No renders, no queue
filing, no downloads of model weights.
