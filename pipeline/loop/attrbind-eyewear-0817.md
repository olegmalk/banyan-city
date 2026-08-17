# Attribute binding: one attribute, one figure of several — eyewear on guard A only

Lane: `attrbind-eyewear` (0817). Founder ruling 2026-08-15, verbatim:
*"draw the second man without glasses. we need to have control."*

That is not the two options offered (drop the wire-rims, or draw both men in
glasses). It rejects both and asks for a **mechanism**: the attribute lands on
the figure we choose, and the engine does not get a vote on our cast. The cast
stands as drawn (founder, 2026-08-15) — guard A carries wire-rims, guard B must
not, and no cast redraw is available as an escape.

## The defect (established, not re-litigated here)

Naming eyewear inside ONE man's clause puts glasses on BOTH men, **5 of 5**.
The two men are the patrol guards; it surfaces in beats 05, 09, 10. This lane
does NOT spend card re-reproducing that count — it is already measured.

## External research (done before building — Oleg, 2026-08-04)

The published diagnosis of why this happens, and it is not a wording problem:

- **ALE-Edit**, *Addressing Attribute Leakages in Diffusion-based Image Editing
  without Training* (arXiv 2412.04715). Root cause: CLIP's text encoder is
  **causal**, so later tokens absorb the semantics of earlier attribute tokens,
  and the **EOS token carries global prompt semantics**. An attribute named
  anywhere is therefore smeared into the global conditioning that steers the
  whole frame. Their fix, **Object-Restricted Embeddings (ORE)**, is training
  free: encode each entity's clause *separately*, substitute those token
  positions into the base embedding, zero the other entities' positions, and
  **replace the EOS with the object-specific EOS**. Implemented on LCM +
  Grounded-SAM, not SDXL.
- **MaskAttn-SDXL** (arXiv 2509.15357) — region-level gating of SDXL
  cross-attention logits. Names our exact failure ("cross-token interference
  where entities entangle and attributes mix across objects") but **learns** a
  binary mask per layer. Training. Not available to us.
- **Training-free Regional Prompting for Diffusion Transformers**
  (arXiv 2411.02395) — regional attention masks, training free, but **DiT /
  FLUX**, not SDXL U-Net.
- **BindEdit** (arXiv 2606.18906) — same framing: when token-group→mask binding
  fails at attention level, tokens activate beyond their region and produce
  blended/hybrid objects.
- diffusers community pipelines: `regional_prompting_pipeline` (hako-mikan) is
  **SD 1.5 ONLY**. The only SDXL region-aware community pipelines are
  `stable_diffusion_mixture_tiling_pipeline_sdxl` and the tile-SR one — coarse
  panorama tiling, not face-scale control.
- a1111 / ComfyUI community practice on multi-character attribute bleed
  (AUTOMATIC1111 discussion #2757, Civitai multi-subject threads): consensus is
  that two *differently specified* characters in one pass is unreliable, and the
  standard remedy is **"generate twins, then inpaint the area"**, or a regional
  prompter.
- diffusers `padding_mask_crop` (inpaint pipelines, issue #6345; a1111
  "inpaint only masked"): crops the mask bbox + padding, inpaints at **full
  resolution**, scales back. This is the reason face-scale inpainting works at
  all — a small region in a large frame has too few pixels for detail.
- SDXL inpainting does **not** require a separate inpaint checkpoint: the
  9-channel inpaint UNet was initialised from base SDXL with the 5 extra
  channels zero-initialised, so `StableDiffusionXLInpaintPipeline` runs on a
  standard 4-channel SDXL checkpoint (our `animagine-xl-3.1`) via the masked
  latent path. $0, offline, no download.

**Conclusion drawn from the outside work, before any pixels:** there is no
drop-in regional-prompting mechanism for SDXL in our stack. The available
training-free mechanisms are (a) ORE-style per-clause text encoding, and
(b) composite-then-inpaint — which is already **our own proven pattern** (bark
clipboard, beats 06 and 10, low strength 0.30).

## Which class does eyewear belong to — the question this lane answers

Known here: **hair and garments BIND to their person clause. A prop does NOT** —
it goes to whoever is drawn nearest. Eyewear is ambiguous by construction: worn
like a garment, sited on a face like a prop. The 5/5 spread is prop-class
behaviour, but that is inference, not measurement. Arm 1 below is what
distinguishes them.

## Pre-registered bar — written BEFORE the pixels exist

Per-sample scoring, three objective booleans read off the rendered frame:

1. `A_glasses` — the figure we designated carries visible eyewear.
2. `B_bare` — the second man carries **no** eyewear.
3. `cast_holds` — no third figure gains eyewear, and both men still read as two
   guards in patrol uniform (identity held 14/14 on a correctly-cast plate;
   that baseline is what must not be broken to buy the fix).

A sample **passes** iff `A_glasses AND B_bare AND cast_holds`. Reported as a
count out of N. An impression is not a score. A metric agreeing with me is not
a sample.

**Adoption threshold: a mechanism is adopted only at ≥4/5 passes across 5
seeds.** 3/5 or worse is not adopted, whatever it looks like. If this bar turns
out loose it is tightened FORWARD and said out loud — never retroactively.
Bending bars after seeing the picture is how 8/12 "passes" became 0/12 usable.

Out of scope for this lane, named and moved past: whether a passing plate is
**shippable** — look, framing, whether the wire-rims are the right wire-rims —
is R4, the founder's alone.

## Arms, cheapest first, ONE SAMPLE per recipe change

- **Arm 1 — positive-clause negation.** `no glasses` inside man B's own clause.
  Cheap, and it is the direct garment-vs-prop probe: if B comes back bare, the
  attribute is reachable by B's clause and eyewear binds garment-class. Prior:
  **expected to fail.** Vacancy law here says the negative does not reach an
  empty region, and ALE-Edit says leakage is a *binding* failure — a negation
  cannot unbind. Note `plate_scratch.py` refuses any tag present in both
  positive and negative (**exit 7**), so the real negative prompt is
  mechanically unavailable for this; this arm is positive-side only.
- **Arm 2 — composite-then-inpaint (the candidate mechanism).** Render the plate
  with **no eyewear token anywhere** — both men bare, which is also the founder's
  literal instruction — then inpaint eyewear onto guard A's face region ONLY,
  low strength, `padding_mask_crop` for face-scale resolution. Control is
  structural: the attribute cannot leak to B because B's pixels are never
  denoised.
- **Arm 3 — ORE-style split encoding.** Only if Arm 2 fails or is too heavy for
  the card. Per-clause text encoding with object-specific EOS.

## Machine discipline

Fixed seed set across arms; one variable at a time. Backend split is real —
bf16/CUDA renders red where fp16/MPS, fp32/MPS and bf16/MPS render purple off
the identical seed (MAE 60-61), so **all arms run on ONE backend** or the
measurement is of the machine, not the wording. A plate is never a prediction
about a prompt; colour does not travel. CLIP 77-token budget is enforced by
`plate_scratch.py` — any token trade is recorded and the traded words are named
as first suspects; the style tail is not cut, it confounds comparisons.
If anything renders on a Mac, `pipeline/mac_preflight.py` gates it first (two
Macs are currently suspect; macbook1/macbook3 rendered SDXL as pure noise for
days behind a UNet of exactly the right length with 88%/93% holes).

## Why this is worth more than a beat-05 fix

If Arm 2 holds, the mechanism is general: **any attribute, onto any one of
several figures, by construction rather than by wording** — draw the frame
without the attribute, then denoise only the region that should carry it.
"We need to have control" applies to every attribute we ever bind to one figure
among several, and the founder asked for the mechanism, not the dodge.
