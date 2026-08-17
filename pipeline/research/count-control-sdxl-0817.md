# Can we force EXACTLY two leaves? External research, 2026-08-17

Scope: SDXL (animagine-xl-3.1), $0, local weights. Question is COUNT, not shape.
Every claim below carries a URL. Written incrementally — sources are committed as
found, not held in context.

## 1. The literature says counting is a *known, unsolved* failure of SDXL-class models

**Text-to-Image Diffusion Models Cannot Count, and Prompt Refinement Cannot Help**
(T2ICountBench) — <https://arxiv.org/abs/2503.06884>, PDF
<https://arxiv.org/pdf/2503.06884>, OpenReview <https://openreview.net/forum?id=kL3pz7YSQF>

- Peer-reviewed benchmark, not anecdote. Finding: *all* SOTA diffusion models fail
  to generate the correct object count; accuracy falls as count rises.
- Mechanism named: SD/SDXL/unCLIP use **CLIP** as text encoder, and the CLIP text
  encoder's embeddings are **near-identical across numerals** — the number is
  barely present in the conditioning signal at all.
- Explicitly tested and rejected: **prompt refinement does not fix it.** That is a
  direct external confirmation of our own beat-01/21 result — the founder's
  "make sure it has 2 leafs" is not reachable by wording, and no rewording lane
  will reach it either. Height binding by wording is consistent with this (size is
  a continuous adjective CLIP encodes; cardinality is not).

Implication for us: stop spending rungs on wording for count. Count must be
imposed by pixels or by attention surgery, not by text.

## 2. ControlNet/segmentation reduces count error but does NOT pin it

**Iterative Object Count Optimization / Detection-Driven Object Count Optimization
for Text-to-Image Diffusion Models** — <https://arxiv.org/html/2408.11721v1>,
PDF <https://arxiv.org/pdf/2408.11721>

- Reports that conditioning on a **segmentation map via ControlNet lowers** object
  count error **but does not eliminate it**, and that the accuracy gained costs
  semantic correspondence — images under restrictive segmentation maps "appear
  unnatural" (our own "stiff/traced" failure mode, in a paper).
- So: a 2-stroke hint biases toward 2, it does not guarantee 2.

Related counting papers to check for runnability (do NOT assume available):
- **Make It Count** (CVPR 2025) — <https://arxiv.org/pdf/2406.10210>,
  <https://openaccess.thecvf.com/content/CVPR2025/papers/Binyamin_Make_It_Count_Text-to-Image_Generation_with_an_Accurate_Number_of_CVPR_2025_paper.pdf>
- **D2D: Detector-to-Differentiable Critic** — <https://arxiv.org/pdf/2510.19278>

(status of these two: pending — runnability on animagine + local weights unknown
at time of writing.)

## 3. Test-time attention methods: real, SDXL-proven, and still not exact

**Be Yourself: Bounded Attention for Multi-Subject Text-to-Image Generation**
(ECCV 2024) — <https://arxiv.org/html/2403.16990v1>,
<https://link.springer.com/chapter/10.1007/978-3-031-72630-9_25>

- **Training-free**, no extra weights — the only class of method so far that could
  run on animagine at $0 without a download.
- Demonstrated on **SD *and* SDXL** (SDXL results are their Fig. 9-10). This is the
  rare case of a paper method that is actually architecture-compatible with us.
- States the diagnosis we are living: vanilla SDXL, given several semantically
  similar subjects, leaks semantics between them and **"inaccurat[ely] generat[es]
  the number of objects."** Two leaves on one seedling is the maximally hard case
  of that — same token, same appearance, adjacent.
- **Input the user must author: one bounding box per subject.** Boxes we can draw
  for two leaves; that part is not a blocker.
- **But it is not exact.** Their own counting metric is **0.83 vs 0.74** baseline.
  A method that raises count accuracy from ~3-in-4 to ~5-in-6 does not deliver
  "exactly two, every plate." It reduces the reroll cost; it does not end it.
- Second caveat: the formulation is *n distinct textual subjects*, each with its own
  box. Two leaves are not distinct subjects in the prompt — we would be asking it to
  bind one repeated token to two boxes, which is off-label for the method.

## 3b. SDXL ControlNet weights that actually exist (and the SD1.5 trap)

**SD1.5 controlnets do not load on SDXL — architectural, not a bug.** SDXL's UNet is
2.6B vs 860M with two text encoders (OpenCLIP ViT-G + CLIP ViT-L) instead of one, and
a controlnet's branches are trained against one backbone's feature distribution, so
it must be trained per base model. ComfyUI FAQ answer to "can I use an SD1.5
ControlNet with SDXL": *"no, you cannot"* … *"there is almost no compatibility
between different models"*, failing with `y is None, did you try using a controlnet
for SDXL on SD1?` — <https://comfyui.nomadoor.net/en/faq/sd15-sdxl-asset-compatibility/>
Also note the inverse trap seen in the wild: A1111's extension printing *"ControlNet
does not support SDXL -- disabling"* on a genuinely-SDXL checkpoint —
<https://github.com/Mikubill/sd-webui-controlnet/issues/1910>

| repo | for | licence | size | note |
|---|---|---|---|---|
| `xinsir/controlnet-scribble-sdxl-1.0` | SDXL | Apache-2.0 | ~1B, F16 | takes crude/simple sketches by design; card claims better aesthetics than its own canny |
| `xinsir/controlnet-union-sdxl-1.0` (+ ProMax) | SDXL | — | one file, 10+ control types | now upstreamed into diffusers as `ControlNetUnionModel` — <https://huggingface.co/docs/diffusers/v0.35.1/en/api/pipelines/controlnet_union>; card warns it was **not** trained with hand/face annotation — <https://huggingface.co/xinsir/controlnet-union-sdxl-1.0> |
| `diffusers/controlnet-canny-sdxl-1.0` | SDXL | openrail++ | 1B, ~1 GB F32 | <https://huggingface.co/diffusers/controlnet-canny-sdxl-1.0> |
| `diffusers/controlnet-canny-sdxl-1.0-small` | SDXL | openrail++ | **0.2B, 7x smaller** | self-described *"experimental"*; "works pretty good on most conditioning images" but "for more complex conditionings, the bigger checkpoints might be better" — <https://huggingface.co/diffusers/controlnet-canny-sdxl-1.0-small>. No `-mid` on that card. |
| `TheMistoAI/MistoLine` | SDXL | OpenRAIL++ | `rank256` / `fp16` | explicitly accepts *"hand-drawn sketches, different ControlNet line preprocessors, and model-generated outlines"*, claims to "adapt to any type of line art input" — <https://huggingface.co/TheMistoAI/MistoLine> |
| `lllyasviel/*` | **SD1.5/2.0 only** | — | — | ControlNet v1.1 is SD1.5/2.0 — <https://huggingface.co/lllyasviel/ControlNet>, <https://comfyui-wiki.com/en/resource/controlnet-models/controlnet-v1-1-sd15-sd2>. His `sd_control_collection` is an **aggregation of other people's** SDXL controlnets (kohya controllllite, t2i-adapters, thibaud), not lllyasviel-trained SDXL weights — <https://huggingface.co/lllyasviel/sd_control_collection>. Do not reach for "the lllyasviel one" here. |

Community consensus (secondary source, Medium/GitHub discussion, not a benchmark):
xinsir's are *"currently the most reliable for SDXL"* —
<https://medium.com/intelligent-art/controlnet-union-promax-for-sdxl-5c1bb137b94c>,
<https://github.com/Mikubill/sd-webui-controlnet/discussions/2989>

## 4. A crude PIL-drawn scribble IS a legitimate ControlNet input

This was the cheapest thing to be wrong about, and it is not wrong. The
**xinsir/controlnet-scribble-sdxl-1.0** card —
<https://huggingface.co/xinsir/controlnet-scribble-sdxl-1.0> — says outright:

- *"the sketch can be very simple and so does the prompt"*, and the model supports
  *"any type of lines and any width of lines."* No photo-derived edge map needed;
  two ellipses drawn with PIL are in-distribution for this checkpoint.
- Line **width is a control-strength dial** in the card's own words (the sentence is
  garbled in the card — it says "thick" twice — but the contrast it draws is thin
  line = coarse control, obeys the prompt more / thick line = strong control, obeys
  the condition image more). So we would have both `conditioning_scale` and stroke
  weight as knobs, which matters for the low/high strength trap.
- Apache-2.0, ~1B params, F16. Card claims *"higher aesthetic performance than our
  Controlnet-Canny-Sdxl-1.0"* and midjourney-comparable output; its table reports
  LAION-aesthetic 6.03 / perceptual similarity 0.5701 but does **not** benchmark
  against the official diffusers controlnets, so the widely repeated "xinsir beats
  the official ones" is community consensus, not a measured claim on that card.

**Attend-and-Excite** (SIGGRAPH 2023) — <https://arxiv.org/pdf/2301.13826>,
code <https://github.com/yuval-alaluf/Attend-and-Excite>, project page
<https://yuval-alaluf.github.io/Attend-and-Excite/>

- Also training-free, but it targets **catastrophic neglect** — the model dropping a
  subject entirely — by strengthening cross-attention on each subject token. It
  makes a missing thing appear. It has **no mechanism for capping a count at two**,
  and cannot suppress a third leaf. Wrong tool for our failure; it addresses "the
  seedling has no leaves," not "the seedling has four."
