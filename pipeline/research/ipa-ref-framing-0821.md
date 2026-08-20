# IP-Adapter reference framing: what the encoder actually receives

**2026-08-21, goblin reference-route lane.** Written because `ep2-jerry-face-k3-0821`
drew the best goblin face this tree has made **and put two horns on it**, and the
ladder's closing entry named the cause as a guess and refused to render on it:

> *at 19.1% of a 416x608 canvas the head is ~116 px, and CLIP ViT-H encodes the
> reference at 224x224 — so the subject lands around 43 px in the encode. […]
> **This is not researched and it is not being acted on tonight.***

This is that research. **The guess was directionally right and materially
incomplete.** The subject is small, but smallness is the second defect. The
first is that **the top 30% of the reference subject — the entire cranial dome —
was cut off before the encoder ever saw it**, by a center crop nobody in this
repo knew was happening.

---

## 1. The code path, from source. This is not opinion.

**diffusers builds its own image processor, with no arguments, and ignores
whatever the reference looks like.** `StableDiffusionXLControlNetPipeline`
inherits `load_ip_adapter` from `IPAdapterMixin`:

```python
feature_extractor = CLIPImageProcessor()
self.register_modules(feature_extractor=feature_extractor)
```

— [`diffusers/loaders/ip_adapter.py`, v0.29.2](https://raw.githubusercontent.com/huggingface/diffusers/v0.29.2/src/diffusers/loaders/ip_adapter.py)
(source code; v0.29.2 is the version `controlnet_plate.py` pins in its own header)

**`CLIPImageProcessor()`'s defaults are a shortest-edge resize followed by a
square center crop:**

| field | default |
|---|---|
| `do_resize` | `True` |
| `size` | `{"shortest_edge": 224}` |
| `resample` | `PILImageResampling.BICUBIC` |
| `do_center_crop` | `True` |
| `crop_size` | `{"height": 224, "width": 224}` |

— [`transformers/models/clip/image_processing_clip.py`](https://raw.githubusercontent.com/huggingface/transformers/main/src/transformers/models/clip/image_processing_clip.py)
(source code)

**And the encoder is 224 with 14-px patches**, i.e. a 16x16 = 256-token grid:
`"image_size": 224`, `"patch_size": 14`, `"hidden_size": 1280`,
`CLIPVisionModelWithProjection` —
[h94/IP-Adapter `models/image_encoder/config.json`](https://huggingface.co/h94/IP-Adapter/raw/main/models/image_encoder/config.json)
(official config; this is the ViT-H folder `controlnet_plate.py` deliberately
selects, see its `IP_IMAGE_ENCODER_FOLDER` note).

Note also: there is **no `preprocessor_config.json`** in that folder (404), so
nothing overrides the defaults above even in principle. The library's built-in
`CLIPImageProcessor()` is the whole story.

**Therefore: aspect ratio of the reference is not cosmetic. It decides which
pixels exist.** A reference wider or taller than square has its long dimension
trimmed to square, centered, *after* the short side is scaled to 224.

## 2. The first-party tooling warns about exactly this

The most-used IP-Adapter implementation emits a runtime warning for non-square
references:

> "the IPAdapter reference image is not a square, CLIPImageProcessor will resize
> and crop it at the center. If the main focus of the picture is not in the
> middle the result might not be what you are expecting."

— warning text reproduced in
[tencent-ailab/IP-Adapter issue #330](https://github.com/tencent-ailab/IP-Adapter/issues/330)
(first-party tooling emitting it; the issue author is a user reporting it, not
authoring it)

And the maintainer documentation of `ComfyUI_IPAdapter_plus` states it as a
property of CLIP rather than of IP-Adapter:

> "The encoder resizes the image to 224×224 **and crops it to the center!**"
> […] "use square pictures as reference for more predictable results"

> "a `PrepImageForClipVision` node has been added that does all the required
> operations for you. You just have to select the crop position
> (top/left/center/etc...) and a sharpening amount if you want."

— [cubiq/ComfyUI_IPAdapter_plus README](https://huggingface.co/datasets/2unnaa/ComfyUI_IPAdapter_plus/raw/main/ComfyUI_IPAdapter_plus-6a411dcb2c6c3b91a3aac97adfb080a77ade7d38/README.md)
(maintainer docs). **An entire node exists in the most-used implementation for
the single purpose of controlling this crop.** That is how routine the trap is.

**CONFIDENCE: highest.** Two independent source files, one official config, one
first-party warning, one maintainer doc, all agreeing.

## 3. What this did to k3, measured rather than inferred

`jerry-tile-headfit-0821.png` is **416x608**. Short edge 416 → 224, so the
canvas becomes **224x327**, and the center crop keeps **rows 51..275**.

The head was authored at crown 0.093 of frame — original rows 62..172, which
land at resized rows **33..93**. The crop begins at row 51.

> **Resized rows 33..51 — the top 30% of the subject, the whole bald dome —
> were discarded before encoding.**

What survived, measured on the actual 224x224 tensor input:

| reference | canvas | after resize | crop | subject bbox in the encode | % of encoder pixels | dome |
|---|---|---|---|---|---|---|
| k1 `jerry-tile-head-0821.png` | 156x152 | 230x224 | trims 3 px a side | 223x215 | **95.6%** | intact |
| k3 `jerry-tile-headfit-0821.png` | 416x608 | 224x327 | **cuts 51 rows off the top** | 64x42, flush to row 0 | **5.4%** | **amputated** |

Evidence, at 6x, the resized reference before and after the crop side by side:
`review/ep2-goblin-design-0819/CLIP-STARVE-0821.png`

**k1 drew no horns. k3 drew two, from the temples, growing upward — the
direction the skull was cut.** The tile's dark ear flanges sit at the widest
point of the skull and, in the encode, run up *into* the cut edge and stop
there. A subject truncated at a frame boundary is a subject whose continuation
the model must invent.

So the horn has **two** candidate causes and the research separates them:

- **the CUT** — a truncated skull completed past its truncation, and
- **the STARVATION** — 94.6% of the 256-token grid is flat green, so the
  identity is weakly encoded and gets completed from the checkpoint's priors.

Both are consequences of the same authoring mistake (a portrait canvas with the
subject placed high), and **the k4 sweep is designed to tell them apart**,
because a square canvas removes the cut while leaving the ratio free to vary.

## 4. On subject-to-frame ratio: the community is split, and that is the finding

There is no single published number for "what fraction of the reference the face
should occupy." What there is:

- **Against wide/contextual references**, and stated in our exact failure mode:
  the FaceID/Plus-Face variants "want a tight face crop, framed close, not a
  full-body shot" because *"if you feed it a wide photo, the encoder sees mostly
  background and gets confused."* —
  [Runflow IPAdapter guide](https://www.runflow.io/blog/comfyui-ipadapter-guide)
  (community guide). **k3 is precisely "the encoder sees mostly background".**
- **Against maximally tight crops**: "full head and shoulders usually works
  better than tight face crops, as the model needs context to understand face
  structure." — same source, reporting the counter-position.
- **Reference detail is destroyed by the downsample regardless**: the general
  reference-guided literature notes that high-resolution references are
  "downsampled to a fixed low-resolution before being fed into the model, so
  fine-grained details are discarded," with identity distortion as a named
  consequence — e.g.
  [RefGC-SR²](https://arxiv.org/pdf/2606.15158) (paper, adjacent domain: this
  is about reference-guided SR, not IP-Adapter, and is cited only for the
  mechanism).

**CONFIDENCE: low-to-medium, and genuinely contested.** Nobody publishes a
curve. **This is exactly why the next rung is a sweep and not a single guess** —
the public answer is "make it square and make the subject dominant," which
brackets our band but does not pick a point in it.

**The uncomfortable corollary, written down because it cuts against the result
this lane liked:** if starvation is what weakened the transfer, then **k3's
best-yet eye (1.24x the tile's) may be an artifact of a crippled embedding
rather than a ratio effect.** A weak adapter transfers less of everything —
including less of the oversized-eye bias that k1 showed at full strength.
Un-crippling the reference may bring the big eye back. That outcome is named in
the k4 specs in advance.

## 5. Masked IP-Adapter does leak, and it is documented

Our containment break — the tile's purple cowl appearing at the neck, outside a
mask limited to the head box — does not require a bug:

> "It is not surgically clean — there is always some bleed between elements […]
> a little of the reference leaks out."

— [Runflow, ComfyUI attention masking](https://www.runflow.io/blog/comfyui-attention-masking)
(community). The masking feature's own design discussion in diffusers
([#6802](https://github.com/huggingface/diffusers/issues/6802),
[#7238](https://github.com/huggingface/diffusers/issues/7238)) treats masks as
attention-level weighting applied per attention layer at latent resolution, not
as a hard spatial clip on the output.

**But there is a simpler explanation available for k3 specifically, and it
should be preferred**: in an encode that is 94.6% flat green, the purple cowl is
one of the very few saturated, high-contrast, non-green features present. Its
share of the surviving signal is *larger* in k3's reference than in k1's, not
smaller. **Restoring the head's dominance should reduce the cowl's relative
weight without touching the mask at all** — and if the cowl persists across the
whole k4 band, then it is the mask, and that is a different instrument.

**CONFIDENCE: medium.** Leakage is real and documented; which of the two causes
drove *our* cowl is untested, and the sweep tests it for free.

## 6. What this changes in the pipeline

1. **Reference canvases are square from now on.** A square reference makes the
   resize exact and the center crop a **no-op**, which is the only condition
   under which an authored head-to-frame ratio is the ratio the model receives.
   On k3 it was not: authored 19.1%, encoded 18.7% *of a view that had already
   thrown the crown away.*
2. **`pipeline/author_jerry_squareref_0821.py`** builds them, and **prints what
   the encoder will actually see** — subject bbox and % of encoder pixels — and
   **exits nonzero if the subject touches an encoder edge.** That check, run on
   k3's reference, would have failed it before a GPU second was spent.
3. **The claim that needs no rung to verify**: any future reference whose aspect
   is not 1:1 is being cropped. Check it with `clip_view()` in that module
   rather than reasoning about it.

## 7. Sources

| # | source | type |
|---|---|---|
| 1 | [diffusers `loaders/ip_adapter.py` v0.29.2](https://raw.githubusercontent.com/huggingface/diffusers/v0.29.2/src/diffusers/loaders/ip_adapter.py) | source code |
| 2 | [transformers `image_processing_clip.py`](https://raw.githubusercontent.com/huggingface/transformers/main/src/transformers/models/clip/image_processing_clip.py) | source code |
| 3 | [h94/IP-Adapter image_encoder config.json](https://huggingface.co/h94/IP-Adapter/raw/main/models/image_encoder/config.json) | official config |
| 4 | [tencent-ailab/IP-Adapter #330](https://github.com/tencent-ailab/IP-Adapter/issues/330) | first-party warning text |
| 5 | [cubiq/ComfyUI_IPAdapter_plus README](https://huggingface.co/datasets/2unnaa/ComfyUI_IPAdapter_plus/raw/main/ComfyUI_IPAdapter_plus-6a411dcb2c6c3b91a3aac97adfb080a77ade7d38/README.md) | maintainer docs |
| 6 | [Runflow IPAdapter guide](https://www.runflow.io/blog/comfyui-ipadapter-guide) | community guide |
| 7 | [Runflow attention masking](https://www.runflow.io/blog/comfyui-attention-masking) | community guide |
| 8 | [diffusers #6802](https://github.com/huggingface/diffusers/issues/6802), [#7238](https://github.com/huggingface/diffusers/issues/7238) | design discussion |
| 9 | [RefGC-SR²](https://arxiv.org/pdf/2606.15158) | paper, adjacent domain |

**What I did not find, stated so the next lane does not re-search it:** no paper
or maintainer statement gives a recommended subject-to-frame *number* for
IP-Adapter references, and no source discusses horns or invented headwear
specifically. The completion-from-priors reading in §3 remains **inference from
the mechanism**, not a cited finding — which is why it is being tested rather
than asserted.
