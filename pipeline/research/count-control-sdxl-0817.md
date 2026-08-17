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
