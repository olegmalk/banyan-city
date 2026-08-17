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

## 3c. Do SDXL controlnets run on an anime finetune like animagine-3.1?

Evidence is weaker here — no benchmark found, only existence proofs and one honest
negative:

- **Yes in practice**: published Animagine-XL-3.0 ComfyUI workflows include ControlNet
  alongside LoRA/IPAdapter — <https://comfyworkflows.com/workflows/3e83739d-cb2d-43c3-b137-24ca7146b628>
  Base-SDXL controlnets are used with SDXL finetunes generally; the incompatibility
  boundary is between *model families*, not between a base and its finetune
  (<https://comfyui.nomadoor.net/en/faq/sd15-sdxl-asset-compatibility/> draws the line
  at SD1.5 / SDXL / Flux and says nothing against same-family finetunes).
- **Someone trained one directly on our exact family**: `SubMaroon/ControlNet-anime-colorize`
  is an SDXL ControlNet trained on **cagliostrolab/animagine-xl-3.0** —
  <https://huggingface.co/SubMaroon/ControlNet-anime-colorize/blob/main/README.md>.
  That confirms architecture compatibility with animagine. But read its own verdict:
  *"Experimental model. Low quality. Not intended for production use"*, "not stable",
  "inconsistent color behavior." Useless to us as a checkpoint (it is a colorize
  experiment), useful only as proof the pairing loads and trains.
- One hard incompatibility to note if anyone tries the Mac shortcut: the **CoreML**
  conversions of animagine-xl 2.0/3.1 **cannot be used with ControlNet** —
  <https://huggingface.co/coreml-community/coreml-animagine-xl-3.1>. Diffusers on MPS
  is fine; CoreML is not.

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

### Attend-and-Excite is the wrong tool

**Attend-and-Excite** (SIGGRAPH 2023) — <https://arxiv.org/pdf/2301.13826>,
code <https://github.com/yuval-alaluf/Attend-and-Excite>, project page
<https://yuval-alaluf.github.io/Attend-and-Excite/>

- Also training-free, but it targets **catastrophic neglect** — the model dropping a
  subject entirely — by strengthening cross-attention on each subject token. It
  makes a missing thing appear. It has **no mechanism for capping a count at two**,
  and cannot suppress a third leaf. Wrong tool for our failure; it addresses "the
  seedling has no leaves," not "the seedling has four."

## 5. The two dedicated count-control methods, and their real numbers

Both are SDXL-based, so the architecture is right. Neither is exact.

**CountGen / Make It Count** (CVPR 2025) —
<https://make-it-count-paper.github.io/>, code
<https://github.com/Litalby1/make-it-count>,
paper <https://openaccess.thecvf.com/content/CVPR2025/papers/Binyamin_Make_It_Count_Text-to-Image_Generation_with_an_Accurate_Number_of_CVPR_2025_paper.pdf>

- Built on **SDXL**; code is public. But it is **not training-free**: it ships a
  *trained* re-layout predictor and inference wants a downloaded checkpoint at
  `pipeline/mask_extraction/relayout_weights/relayout_checkpoint.pth`. Weights we do
  not have; free to fetch, but it is a new dependency, and it was trained against
  base-SDXL internal features — pointing it at animagine's finetuned UNet is
  off-distribution and unproven.
- Its own framing of why this is hard is the best sentence in the literature for our
  situation: the model "needs to keep a sense of separate identity for every instance
  of the object, **even if several objects look identical or overlap**." Two leaves on
  one stem are identical, adjacent and often overlapping — the worst case named by the
  paper that is trying to fix it.
- CountGen is limited to **single-class** objects.

**CountDiffusion** — <https://arxiv.org/html/2505.04347>

- **Training-free, plug-and-play**, explicitly demonstrated on **SDXL**. Closest
  thing to a drop-in.
- But it needs **Grounded SAM** at inference to detect/segment and count the
  instances. That is the load-bearing dependency, and it is the part most likely to
  break on us: Grounded SAM detecting two attached cotyledons on a stylised anime
  seedling as two instances is not something anyone has shown.
- **The honest numbers:** SDXL baseline count accuracy **34%**, CountDiffusion
  **59%**; single-class MAE 2.33 → 0.90 objects. Authors concede it "still struggles"
  as counts rise, limited by both base model and counting model.

**So the ceiling of the published art is ~59% on the drop-in method and ~83% on
Bounded Attention's metric.** Nobody has published exact count control on SDXL. Any
plan of the form "add method X and the plate will have two leaves" is false.

## 6. Verdict: the cheap proven thing wins, and it is not close

Our composite-then-inpaint pattern — build the structure with plain image processing,
then denoise at **strength ~0.30** — is the only approach on the table where the count
is **not a sample from the model at all**. Two leaves drawn into the init are two
leaves; the sampler is only asked to restyle pixels it is already sitting on.

External support for the mechanism (tutorial-grade, not papers, but uncontested):
low denoising 0.2–0.35 "preserves identity or layout" and is for "small refinements,
cleanup, light style shifts"; if the output loses subject/pose/composition, lower the
strength — <https://stable-diffusion-art.com/denoising-strength/>,
<https://www.rundiffusion.com/img2img-docs>,
<https://wiki.shakker.ai/en/webui-img2img-denoising-strength-guide>.
Mechanically: noise is added to the init latent in proportion to strength and only
`steps x strength` denoising steps run, so at 0.30 most of the init's structure is
never destroyed to begin with — <https://deepwiki.com/AUTOMATIC1111/stable-diffusion-webui/4.2-image-to-image-(img2img)>

And **iterative inpainting with a per-step check has a paper behind it**: *Steerable
Scene Generation with Post Training and Inference-Time Search*
(<https://arxiv.org/pdf/2505.04831>) incrementally inpaints masked regions under a
task-specific reward and uses **the number of feasible objects as its proof of
concept**. Inpaint-one-at-a-time-and-verify is a recognised way to get counts right;
it is exactly what beats 06 and 10 did by hand for the clipboard.

Ranked recommendation for the count problem:

1. **Composite-then-inpaint at 0.30** (already proven here, $0, no new weights, count
   is deterministic). The leaves come from PIL/compositing, not from the sampler.
2. **Add a scribble/lineart ControlNet hint on top of a composited init** if the
   restyle drifts — `xinsir/controlnet-scribble-sdxl-1.0` or `TheMistoAI/MistoLine`,
   both of which *advertise* crude hand-drawn strokes as valid input, and both
   Apache-2.0/OpenRAIL++. Treat it as a *bias*, never a guarantee: the count paper
   measured segmentation-ControlNet as reducing count error while trading away
   semantic correspondence and producing unnatural images
   (<https://arxiv.org/html/2408.11721v1>).
3. **Regional prompting / Attention Couple** — mature tooling
   (<https://stable-diffusion-art.com/regional-prompter/>,
   <https://github.com/lllyasviel/Fooocus/discussions/913>,
   <https://github.com/pamparamm/ComfyUI-ppm/issues/21>) but **no source found that
   claims or measures count control**; it steers *where* prompts apply, not how many
   instances appear. Do not spend rungs here on a count promise nobody makes.
4. **CountDiffusion / CountGen** — last, and only if 1-3 fail. New dependencies
   (Grounded SAM; a trained relayout checkpoint), unproven on an anime finetune, and
   even at their best they are 59%/83%, not 100%.

Dead-end warnings so nobody re-walks them:

- **More wording will not fix count.** Rejected by T2ICountBench directly
  (<https://arxiv.org/abs/2503.06884>) — the CLIP text encoder barely varies with the
  numeral. This is settled literature, not our opinion.
- **Do not download SD1.5 controlnets.** They will not load on SDXL at all.
- **Do not reach for "lllyasviel's SDXL controlnet."** It does not exist as his own
  weights.
- **CoreML animagine cannot take a controlnet** — any Mac controlnet work must be
  diffusers/MPS.
