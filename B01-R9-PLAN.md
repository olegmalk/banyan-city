# Beat 01, round 9 — the depth-ControlNet round

**Status: a plan, not a script.** Nothing here has been rendered and nothing has
been downloaded. Written 2026-08-10 by the b01-r9 research lane, against
`shots.md` at `445b8c682a5f94954d98a2a0be5209876c0c558c666c085ba126b35614e491c9`
(commit `11e5ab1`).

## The round in one sentence

r9 takes the b15 plate as **geometry only** — a depth map, colour discarded
before the first denoise step — so that beat 01's own prompt keeps the
peach-and-gold sunrise wide shot that img2img overwrote at every strength r8
tried.

---

## 1. What r8 settled, and the exact thing it did not

r8's own table, from `shots.md`:

| arm | grounded, whole plant | person | pale slab | stem height |
|---|---|---|---|---|
| i35 | **4 of 4** | 0 | 0 | ~30% on all four |
| i55 | **4 of 4** | 0 | 0 | ~25–34% |
| t2i | 0 of 4 | 1 | 1 | apex OFF-FRAME on three |

Seven rounds of wording could not produce one grounded whole-plant frame; the
init produced eight. And all eight wear the plate's amber dusk, its shaft of
light and its macro bokeh, where the beat asks for `peach and gold sunrise sky,
wide shot`. The t2i control draws that sky correctly on all four seeds, so the
prompt is fine and the init is overriding it.

r8's closing sentence is the thing r9 has to answer:

> In this particular plate the palette IS the composition — the light shaft is
> what makes it a macro, and the macro is what makes the sapling read small — so
> strength cannot buy one without spending the other.

**That sentence is true about strength and does not generalise to depth.** An
img2img init is an RGB array in which geometry and colour are the *same
numbers*; `strength` is a single scalar over that array, so there is no setting
at which it keeps one and drops the other. r8 measured this correctly and its
ladder is conclusive: at 0.35 the palette has not moved, at 0.55 it has still
not moved while the stem has started growing back. A depth map performs the
separation *before* diffusion starts — it is one channel of geometry with the
colour thrown away, so there is no colour left to leak. The question r9 asks is
therefore not "can we tune the leak down" but "is the geometry still sufficient
once the colour is gone".

**The honest risk, stated up front.** If what made the sapling read small to the
founder was the macro *look* rather than the size relationship, then a
sunrise-wide-shot version of the same geometry may not read small to him, and
that is a taste question (R4) no measurement here can settle. r9 is built to
produce exactly the frame that asks him that question.

---

## 2. The plate, measured

Before choosing a control type I measured what is actually extractable from
`001-capability-inventory/stills/15-something-s-coming.png` (832x1216, sha256
`f60c1404…`, the render size exactly — no resize, no crop, unlike the video
path `plate_prep.py` exists for). Method: scipy Gaussian→Sobel→non-maximum
suppression→hysteresis Canny plus luminance statistics, Mac-side, no model, no
GPU, no download.

| Canny thresholds | edge pixels | density | in sky band (top 45%) | in grass band |
|---|---|---|---|---|
| 100 / 200 (the ControlNet default) | 1 185 | **0.12 %** | 54 (0.01 %) | 1 131 (0.20 %) |
| 50 / 150 | 1 727 | 0.17 % | 106 (0.02 %) | 1 621 (0.29 %) |
| 20 / 60 | 8 290 | 0.82 % | 569 (0.13 %) | 7 721 (1.39 %) |

Looking at the maps: at 100/200 the **only** surviving structure is the
sprout's own outline — the two cotyledon leaves and the stem, and nothing else
in the frame. At 20/60 the near-field grass blades appear as long diagonal
strokes, still with no ground plane and now noisy.

Two findings, both of which correct a guess I would otherwise have written
down:

- **Canny cannot carry this plate's geometry.** 0.12 % density is a
  substantially blank control map. This is a soft painterly image whose
  structure is tonal, not linear; an edge extractor has almost nothing to find.
  The same reasoning weakens lineart here — informative-drawings would do better
  than Canny on a painting, but it is still an edge-domain extractor pointed at
  an image with very few edges.
- **The light shaft is not an edge feature and would not have been transferred
  by Canny anyway.** Peak column-luminance gradient across the top 25 % is
  1.43 per pixel where a hard edge exceeds 2.0, and the sky band holds 0.01–0.02 %
  of the edges at usable thresholds. My prior worry that an edge map would
  re-impose the shaft was wrong.

Third measurement, aimed at the main risk to the depth plan — the sprout stem is
thin, and a depth estimator downsamples. Round-tripping the plate through the
estimator's input resolution and back, the sprout band (y 60–80 %, x 40–70 %)
retains **98.7 %** of its contrast at short-side 518 and **94.6 %** at 384. The
sprout survives the downsample.

**Conclusion: depth, not edges.** The plate's content is a tonal depth
arrangement — large near-field blades, sprout at mid distance, open background —
and that arrangement *is* the composition r8 proved works. A depth field reads
it; an edge detector does not.

---

## 3. Which depth ControlNet, and why the newest preprocessor is the wrong one

**Match the preprocessor to the ControlNet's training preprocessor.** This is
the standard rule and it is the one that decides the recipe here, against the
instinct to reach for the newest depth model.

`diffusers/controlnet-depth-sdxl-1.0`'s own model card builds its conditioning
image with `DPTForDepthEstimation.from_pretrained("Intel/dpt-hybrid-midas")` —
MiDaS 3.0 hybrid, through plain `transformers`. Three consequences, all in our
favour:

1. **No dependency change on the box.** `DPTForDepthEstimation` and
   `DPTImageProcessor` have been in `transformers` far longer than the box's
   pinned `4.44.2`. Depth Anything V2 would be both a preprocessor mismatch for
   this ControlNet and a reason to touch the pin — and that pin is load-bearing:
   r8's token-count trap runs on this venv's CLIP tokenizer, `diffusers 0.29.2`
   is pinned against it, and the repo's own precedent for "needs newer
   libraries" is a *separate* environment (`C:\banyan-video`), not an upgrade in
   place. **r9 runs in `C:\banyan-farm\venv` and changes nothing in it.**
2. **No new pip package.** xinsir's card drives its example through
   `controlnet_aux` detectors; the diffusers pairing needs only `transformers`,
   which is already installed.
3. **A documented operating point.** That card states
   `controlnet_conditioning_scale = 0.5  # recommended for good generalization`,
   which anchors the sweep to a published number rather than a guess.

Depth estimation on non-photographic art is a real technique, not an
improvisation: AniDepth (SIGGRAPH 2025 Talks) runs depth estimation over anime
keyframes for exactly this purpose. It is still the assumption in this plan
carrying the most weight, which is why §7 makes looking at the map a gate rather
than a formality.

### Verified against the pinned versions, not from memory

Checked against the `v0.29.2` tag itself, because a plan that assumes an API is
a plan that fails on the box:

- `StableDiffusionXLControlNetPipeline` exists in 0.29.2, and its `__call__`
  carries `controlnet_conditioning_scale` (default `1.0`), `control_guidance_start`
  (`0.0`), `control_guidance_end` (`1.0`) and `guess_mode` (`False`). The
  conditioning image is passed as `image=`.
- `AUTO_TEXT2IMAGE_PIPELINES_MAPPING` contains
  `("stable-diffusion-xl-controlnet", StableDiffusionXLControlNetPipeline)`, and
  `AutoPipelineForText2Image.from_pipe(pipe, controlnet=cn)` swaps the class
  while **reusing the already-loaded modules** rather than reloading them. So
  r9 keeps r8's discipline exactly: one set of animagine weights, one dtype, one
  device, one tokenizer, shared by the control arm and the ControlNet arms.
- `cagliostrolab/animagine-xl-3.1` is a `stabilityai/stable-diffusion-xl-base-1.0`
  finetune, so generic SDXL ControlNets are architecturally compatible, and
  832x1216 is one of the resolutions its card lists.

### Polarity — the silent failure to guard against

MiDaS/DPT predicts *inverse* depth: larger value = nearer. The card's
`get_depth_map` min-max normalises and replicates to three channels, so **near
must come out bright**. Getting this backwards produces a valid-looking map of
an inverted scene and a round that measures nothing. §7 checks it by eye before
any diffusion runs.

---

## 4. G1 — the provenance chain through a derived map

G1, as `shots.md` states it, "fails any candidate *conditioned on* a still that
is revoked or was never approved". The chain r9 is conditioned on:

```
b15-r3-s1  genomes/sapling/nodes/001-capability-inventory/stills/15-something-s-coming.png
           APPROVED, canon since d4488de, sha256 f60c1404f88d45720ca295dfc753e9eaabb815446710bcfffb3c7a07b7277f54
   │
   ├─ Intel/dpt-hybrid-midas @ pinned revision, DPTImageProcessor defaults,
   │  torch.inference_mode, min-max normalise, replicate to 3 channels
   ▼
depth map  genomes/sapling/nodes/002b-first-citizen/control/b01-r9-depth-b15.png
           committed as an artifact, sha256 recorded and asserted at render time
   │
   ▼
StableDiffusionXLControlNetPipeline(image=<that map>)
```

**Why this satisfies G1.** The geometry source is still the approved still and
nothing else enters. The map is a pure function of it under pinned weights and
fixed parameters, with no sampling. It carries strictly *less* information than
the approved still — one channel of geometry, colour discarded — so it can
subtract from approved content but cannot introduce unapproved content. And both
hashes are asserted by the script: the plate's, exactly as r8 asserted
`INIT_SHA`, and the map's, so neither the source nor the derivative can be
swapped without the round refusing to start.

**The caveat, and why the map is committed rather than regenerated.** A
monocular depth estimator is a neural net, not a mechanical transform; it infers
structure and could in principle invent some. Two mitigations, both cheap:
Stage 0 makes a human look at the map before a single diffusion step runs, and
the map is **committed as a file** so the round is reproducible later even if
the estimator's weights, its library, or its defaults move. Regenerating the map
at render time would make the round depend on a model download staying
byte-stable, which is the weaker design.

This is the same shape as r8's init assertion, one derivation further along.

---

## 5. D15 — licence verdicts

Quoted from the model cards, not paraphrased.

| Artifact | Role | Licence (as stated) | Verdict |
|---|---|---|---|
| `cagliostrolab/animagine-xl-3.1` | base checkpoint (unchanged from r5–r8) | "CreativeML Open RAIL++-M License" — permits commercial use, modification, distribution; use restrictions travel | already in the composite; no change |
| `diffusers/controlnet-depth-sdxl-1.0` | structure control | `openrail++` | **SAFE** — same family as the base; adds no restriction the composite does not already carry |
| `diffusers/controlnet-depth-sdxl-1.0-small` | fallback (0.2B, "7x smaller") | `openrail++` | **SAFE**, same reasoning |
| `Intel/dpt-hybrid-midas` | depth preprocessor | `apache-2.0` | **SAFE** — permissive, adds nothing |
| `xinsir/controlnet-depth-sdxl-1.0` | alternative structure control | `apache-2.0` | **SAFE**, and licence-preferable; see §9 |

**No non-commercial artifact appears in this recipe, and none may.** The
specific trap worth naming, because the instinct is to reach for it: the Depth
Anything V2 family is *not* uniformly permissive across its size variants, and a
CC-BY-NC artifact anywhere in a canon still's chain would poison the composite
the way `models-licence.md` records the Wan2.2-Turbo distill doing. The
recommended recipe avoids the question entirely by using an apache-2.0
estimator.

The r9 sidecar must declare, in addition to r8's fields:
`controlnet`, `controlnet_licence`, `controlnet_conditioning_scale`,
`control_guidance_start`, `control_guidance_end`, `depth_estimator`,
`depth_estimator_licence`, `control_map`, `control_map_sha256`, and
`control_map_derived_from` + `control_map_source_sha256` naming the plate.

---

## 6. The recipe

Everything not named here is r8's, unchanged, so the arms differ by the control
and nothing else.

| Held constant from r8 | Value |
|---|---|
| base | `cagliostrolab/animagine-xl-3.1`, bf16, cuda |
| size / steps / cfg | 832x1216 / 40 / 7.5 |
| seeds | `20260720, 20261720, 20262720, 20263720` (`SEED + BEAT + i*1000`, SEED 20260719) |
| positive | byte-identical to r8's sent positive, 65 CLIP tokens |
| negative | byte-identical to `R7_NEG_SENT`, 72 CLIP tokens |
| shots.md | **not edited**; the height predicate is stripped script-side after asserting the fence on disk is byte-for-byte r7's |

The sent positive, for reference — this exact string, from r8's sidecars:

```
A tiny 40cm seedling standing in short grass, its sturdy curved stem, two oversized cotyledon leaves, one small round green fruit hanging from the stem, whole plant in frame, wide shot, peach and gold sunrise sky, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic
```

**Arms — one axis, three points, bracketing the card's own 0.5:**

| arm | `controlnet_conditioning_scale` | `control_guidance_start` / `end` |
|---|---|---|
| `d40` | 0.40 | 0.0 / 1.0 |
| `d60` | 0.60 | 0.0 / 1.0 |
| `d80` | 0.80 | 0.0 / 1.0 |

3 arms x 4 seeds = **12 frames**, matching r8's shape.

**Guidance start/end are fixed, deliberately.** Ending control early is the
standard trick for letting the prompt own late-stage colour — but a depth map
carries no colour, so here it would be a second variable bought against a
problem the architecture already solves. If r9 shows geometry and palette
fighting late in the denoise, `control_guidance_end` is r10's axis, not r9's.

**The control arm costs one frame, not four.** r8 already rendered t2i on these
four seeds with this exact positive and negative; those frames are r9's control
and re-rendering them would spend a third of the round reproducing a known
result. Instead r9 renders **one** t2i frame on seed 20260720 and compares its
sha256 to `01-cold-open-r8-t2i-s0.png`. A match proves the environment has not
drifted and promotes r8's whole t2i arm to r9's control for free; a mismatch is
reported, not gated on — GPU nondeterminism would be a finding about the bench,
not about this beat. Thirteen frames, roughly ten seconds each.

---

## 7. Ordering — one sample, twice, before the round

The house rule is one sample per *recipe change*, and r9 changes the recipe
twice: once when a control map appears, once when the ControlNet first runs.

**Stage 0 — derive the map and look at it. No diffusion.** Seconds of compute.
Three gates, and the round stops on any of them:

- **polarity**: near is bright (see §3);
- **the sprout is there**, and its extent matches the plate — this is the
  measured risk from §2 and the reason the whole plan could be wrong;
- **the shaft is gone**, and the sky band is a smooth far-field gradient with no
  wedge in it. If the shaft survives into the depth map, depth is not the
  separation and r9 should not render.

**Stage 1 — one frame.** `d60`, seed 20260720. Look at it. This is the sample
the rule demands, and it is three minutes against the hour the K recipe cost by
skipping straight to fifteen.

**Stage 2 — the remaining twelve**, only if Stage 1 holds geometry *and* draws
this beat's own sky.

Stages 0 and 1 need no human in the loop to *run* — they need one to look before
Stage 2. Nothing here waits on an hour of the day.

---

## 8. Pre-registered rubric

Fixed before any pixel exists. Two axes, because r9 claims two things.

**A — geometry, unchanged from r8 so the numbers are comparable.** Stem height
fraction (apex to groundline over frame height) against the 32 % ceiling he
revoked, with r8's ~30 % (i35) as the standing best; plus grounded-whole-plant,
person and pale-slab counts, each n of 4 per arm. Person-binding is observed,
never assumed — r7 regressed to 1 of 4 on a byte-identical negative.

**B — palette, the new axis, measured rather than eyeballed**, because "the
colour is free now" is exactly the kind of claim that flatters itself. Computed
from the PNGs with numpy alone:

- **sky colour**: mean RGB of the top 25 % of frame, for every r9 frame and for
  three references — the b15 plate, `r8-i35-s0` (the leak) and `r8-t2i-s0` (the
  correct sky). r9 passes if its sky sits with the t2i reference, not with the
  plate.
- **the shaft**: column-luminance profile across the top 25 %. The plate's
  profile runs 56.3 to 119.9 with its peak at x=333 of 832 (40 % across); a
  shaft-free frame has no such central peak. Report the peak position and the
  peak-to-mean ratio per frame.

**r9 succeeds only if both hold** — geometry inside the ceiling on at least
three of four seeds on at least one arm, *and* sky clustering with t2i. Either
one alone is a failure, and the two failures mean different things:

- **geometry holds, palette still leaks** → depth is not the separation either,
  which retires structure-control for this beat and leaves the checkpoint swap
  and inpaint as the named levers;
- **palette free, geometry gone** → the control is too weak, which is a scale
  question and argues for a higher-scale r10, not a new architecture.

Saying in advance what each failure would retire is the point; it is what keeps
the round from being re-read afterwards as whatever it happened to produce.

**The fig stays observed and ungated.** `shots.md` has settled it: 0 of 12 in
r8, size adjectives make it larger, and it is an inpaint or a founder call to
drop it. A depth map of a fruitless plate carries no fruit, so r9 says nothing
new here and should not pretend to.

---

## 9. Download list — for the card-runner lane, not fired here

Nothing below has been downloaded. Sizes are as shown on the Hugging Face files
pages.

| Artifact | Files | Size | Notes |
|---|---|---|---|
| `diffusers/controlnet-depth-sdxl-1.0` | `diffusion_pytorch_model.fp16.safetensors` + `config.json` | **2.5 GB** + 1.27 kB | the fp32 file is 5 GB; take the fp16 variant |
| `Intel/dpt-hybrid-midas` | `pytorch_model.bin` + `config.json` + `preprocessor_config.json` | **490 MB** + 9.88 kB + 382 B | see the `.bin` note below |
| `diffusers/controlnet-depth-sdxl-1.0-small` | fallback only | 0.2B params, "7x smaller" | not needed unless the 2.5 GB is a problem |

**About 3.0 GB total**, into the box's default Hugging Face hub cache, loaded by
repo id — no explicit paths and no `local_dir`, matching how r5–r8 load
animagine, which is already cached there.

**No pip install of any kind.** Both additions load through `diffusers 0.29.2`
and `transformers 4.44.2` exactly as pinned; that is the main reason this
pairing was chosen over the alternatives, and it is a constraint on r9 rather
than a convenience.

Two things that will otherwise cost the box a failed run:

- **Load the ControlNet in bf16, not fp16.** `variant="fp16"` selects which
  *file* to download; `torch_dtype` sets the in-memory dtype, and it must match
  the UNet's. So
  `ControlNetModel.from_pretrained(..., variant="fp16", torch_dtype=torch.bfloat16, use_safetensors=True)`.
  A ControlNet left in fp16 against a bf16 UNet fails at the first forward pass
  with a scalar-type mismatch.
- **`Intel/dpt-hybrid-midas` ships `pytorch_model.bin` only** — there is no
  safetensors file in that repo, so `use_safetensors=True` cannot be passed to
  the estimator and the load goes through `torch.load`. Expected to work on the
  pinned transformers, but it is the one load in this recipe without a
  safetensors path, so it is the one to watch on first run.

**On xinsir/controlnet-depth-sdxl-1.0** (apache-2.0, 1B, F16, loads with the
standard `ControlNetModel.from_pretrained`): licence-preferable to the diffusers
weight and widely reported as stronger, but its card drives the preprocessor
through `controlnet_aux` — a new pip dependency with its own transformers and
timm constraints, pointed at the venv whose pin r8's token trap depends on. It
is trained on MiDaS-and-Zoe depth, so it would in fact accept the DPT map this
plan already produces, and it recommends scale 1.0 rather than 0.5. **Named as
the r10 substitution if r9's geometry comes back too weak** — swapping the
weight is one line and needs no new preprocessor.

---

## 10. What this plan does not decide

- **Whether the founder reads a sunrise wide shot as "small"** when the macro
  look that carried that reading is gone (§1). R4, his call, and the frame that
  asks it is the deliverable.
- **The fig.** Inpaint or drop; a founder call either way.
- **The checkpoint swap**, still on the table and untouched by this round.
- Animagine's card recommends CFG 5–7 and under 30 steps where we run 7.5 and
  40. Noted, deliberately not changed: r9's numbers have to be comparable to
  r5–r8's, and that is a separate round if it is ever one.

---

## 11. Sources

Every load-bearing claim above was read off a primary source — a model card, the
pinned library tag, or a measurement of our own plate. None of it is inference
from this repo's own code comments.

**Model cards** (licence strings, preprocessor pairings, recommended scales,
file sizes):

- `cagliostrolab/animagine-xl-3.1` — <https://huggingface.co/cagliostrolab/animagine-xl-3.1>
- `diffusers/controlnet-depth-sdxl-1.0` — <https://huggingface.co/diffusers/controlnet-depth-sdxl-1.0>
  and its files page <https://huggingface.co/diffusers/controlnet-depth-sdxl-1.0/tree/main>
- `diffusers/controlnet-depth-sdxl-1.0-small` — <https://huggingface.co/diffusers/controlnet-depth-sdxl-1.0-small>
- `Intel/dpt-hybrid-midas` — <https://huggingface.co/Intel/dpt-hybrid-midas>
  and its files page <https://huggingface.co/Intel/dpt-hybrid-midas/tree/main>
- `xinsir/controlnet-depth-sdxl-1.0` — <https://huggingface.co/xinsir/controlnet-depth-sdxl-1.0>

**The pinned library, read at the tag rather than from documentation** — this is
what makes the API claims in §3 checkable:

- `StableDiffusionXLControlNetPipeline.__call__` at v0.29.2 —
  <https://github.com/huggingface/diffusers/blob/v0.29.2/src/diffusers/pipelines/controlnet/pipeline_controlnet_sd_xl.py>
- `AUTO_TEXT2IMAGE_PIPELINES_MAPPING` and `from_pipe` at v0.29.2 —
  <https://github.com/huggingface/diffusers/blob/v0.29.2/src/diffusers/pipelines/auto_pipeline.py>

**Technique:**

- AniDepth — anime in-between diffusion using depth-guided warped line art,
  SIGGRAPH 2025 Talks — <https://dl.acm.org/doi/10.1145/3721239.3734091> —
  depth estimation over anime keyframes as an established technique rather than
  an improvisation here.
- Matching a preprocessor to the ControlNet trained on it —
  <https://comfyui.dev/docs/guides/Other%20Resources/preprocessor-options/>.
  The stronger form of this argument is that
  `diffusers/controlnet-depth-sdxl-1.0`'s own card builds its conditioning image
  with `Intel/dpt-hybrid-midas`, so the pairing is the reference one.

**Our own measurement** (§2): scipy Canny and luminance statistics over
`15-something-s-coming.png`, Mac-side, no model and no GPU. Method is stated
in §2 in enough detail to re-run; the numbers are reproducible from the plate
and its recorded sha256.

**Not yet returned.** Two outside-research lanes were dispatched in parallel
with this plan — one on the community's comparative findings for depth vs canny
vs lineart vs T2I-Adapter vs IP-Adapter-composition colour leakage and their
reported conditioning-scale ranges, one on a fuller artifact and licence
manifest. Neither had reported when this was written. Nothing above depends on
them: the recipe is anchored to the diffusers card's own published `0.5` rather
than to community ranges, and the licences here were read off the cards
directly. If those lanes come back with a materially better control type — the
most likely candidate is `xinsir/controlnet-depth-sdxl-1.0`, already costed in
§9 — the substitution is one line and §9 says so.
