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

### The diffusers version question — stay on 0.29.2, and here is the risk both ways

**Recommendation: stay on 0.29.2 for r9 and for the foreseeable beats. Do not
upgrade.** Stated as a recommendation rather than a hedge, with what it costs.

The only capability an upgrade buys is ControlNet-Union, and the tag probe puts
that out of reach anyway: `ControlNetUnionModel` does not exist at v0.29.2
through v0.31.0 and first appears at **v0.32.0** (PR #10131, merged 2024-12-11),
while the Union fixes for issue #11861 only land in **v0.35.0** — so "upgrade for
Union" means a six-minor-version jump, not one.

**What we give up by staying: nothing r9 needs, and less than it looks.** Union's
pitch is many control types in one model. We need one. And multi-control does
not actually require Union — 0.29.2's SDXL ControlNet pipeline already accepts
`Union[ControlNetModel, List[ControlNetModel], MultiControlNetModel]` and
converts a list into a `MultiControlNetModel` itself, so even a depth+lineart
round is reachable on the pin we have.

**What we risk by upgrading, which is the larger number.** r9's whole value is
comparability: r5, r6, r7 and r8 all rendered on this exact stack, and the
pre-registered rubric in §8 scores r9 against r8's measured `~30%`. Change the
renderer in the same round that changes the architecture and the result answers
neither question — the same two-variables-at-once error r8 was careful to avoid
on platform. Beyond this beat, `C:\banyan-farm\venv` is the venv every render in
flight uses. Worth noting honestly in the other direction: diffusers 0.29.2
shipped 2024-06-27, ten months before PyTorch added Blackwell support, so the
stack is already an untested pairing that happens to work — which is an argument
for not disturbing it, not for churning it.

**When to revisit:** if a beat ever needs three or more simultaneous controls
where Union's single-model efficiency actually matters. Qualify it then in a
**separate** environment, which is this repo's established pattern
(`C:\banyan-video` exists for exactly this reason), never as an in-place upgrade
of the image venv.

One trap if anyone tries Union on the current pin regardless: its configs
declare `_class_name: "ControlNetModel"`, so `from_pretrained` will *attempt*
the load and then fail or misload on the extra Union tensors rather than
refusing cleanly.

### Polarity — the silent failure to guard against

MiDaS/DPT predicts *inverse* depth: larger value = nearer. The card's
`get_depth_map` min-max normalises and replicates to three channels, so **near
must come out bright**. Getting this backwards produces a valid-looking map of
an inverted scene and a round that measures nothing. §7 checks it by eye before
any diffusion runs.

---

## 4. G1 — the provenance chain through a derived map

G1, as `shots.md` states it, "fails any candidate *conditioned on* a still that
is revoked or was never approved".

**This is also why b15 is the only admissible geometry source, and that is worth
saying plainly because it looks like a taste choice and is not one.** The obvious
move — condition on a beat-01 frame that already has the right sunrise palette —
is illegal, not merely worse: as `shots.md` records, "every beat-01 frame
carrying the right palette — r2-s3, r3-s3, r6-s3 — is unapproved or revoked and
would have failed the round before he saw it." `15-something-s-coming.png`
(b15-r3-s1) is the only approved sapling-in-grass frame in the tree. So the
palette collision r8 hit was not bad luck in choosing an init; it is structural,
and it is exactly why the fix has to be to *discard* the init's colour rather
than to find a better-coloured init. There is no better-coloured init to find
until the founder approves a beat-01 frame.

The chain r9 is conditioned on:

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

**No non-commercial artifact appears in this recipe, and none may.** The trap
worth naming, because the instinct is to reach for the newest estimator: the
Depth Anything V2 family is *not* uniformly licensed across its sizes, and it is
worse than the usual assumption —

| Depth Anything V2 | licence (card YAML) |
|---|---|
| `Depth-Anything-V2-Small-hf` | `apache-2.0` |
| `Depth-Anything-V2-Base-hf` | **`cc-by-nc-4.0`** |
| `Depth-Anything-V2-Large-hf` | **`cc-by-nc-4.0`** |

Base is non-commercial too, not just Large, so "use the middle size" is the
version of this mistake most likely to get made. A CC-BY-NC artifact anywhere in
a canon still's chain would poison the composite the way `models-licence.md`
records the Wan2.2-Turbo distill doing. Worth recording for whenever we do want
Depth Anything: the **V1** family (`LiheYoung/depth-anything-{small,base,large}-hf`)
is `apache-2.0` at every size, and V1-Large is byte-for-byte the same size as
V2-Large with the same API — a clean drop-in if the NC licence is ever the only
objection.

The recommended recipe avoids the question entirely: `Intel/dpt-hybrid-midas` is
`apache-2.0`.

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

**The token counts must be measured on the BOX, and the script must refuse to
run without a real CLIP tokenizer** — the same trap r7 and r8 both carried, kept
here unchanged. `sd_prompt._token_estimate` over-counts a positive of this shape
by roughly 3 tokens near the 77 boundary, so a count taken on the Mac is not the
count the model sees. Since the whole comparability claim of this round rests on
the positive being byte-identical to r8's 65 tokens and the negative to r7's 72,
a Mac-side measurement would not merely be imprecise, it would invalidate the
round. `if _clip_tokenizer() is None: return 8` stays exactly as r8 has it, and
`--measure` prints the r8 control beside r9 on the box's own tokenizer before
anything is drawn.

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

## 9. Download list — staged on the box 2026-08-10

Byte sizes are from the Hugging Face API `tree/main` endpoint, not the rounded
figures on the web page, and every file is pulled by exact name via
`allow_patterns` — several of these repos carry ComfyUI-format siblings that a
bare `snapshot_download` would drag along by the gigabyte. Sizes are verified
against these counts after landing.

| Artifact | Files | Exact bytes | Notes |
|---|---|---|---|
| `diffusers/controlnet-depth-sdxl-1.0` | `diffusion_pytorch_model.fp16.safetensors` + `config.json` | **2,502,139,134** (2502.14 MB) + 1.27 kB | the fp32 file is 5,004,167,860 B; take the fp16 variant |
| `Intel/dpt-hybrid-midas` | `pytorch_model.bin` + `config.json` + `preprocessor_config.json` | **489,648,389** (489.65 MB) + 9.88 kB + 382 B | see the `.bin` note below |

**2,991,787,523 bytes — about 2.99 GB total**, into the box's default Hugging
Face hub cache, loaded by repo id: no explicit paths, no `local_dir`, matching
how r5–r8 load animagine, which is already cached there.

Smaller fallbacks on the same licence, if 2.99 GB is ever the objection:
`diffusers/controlnet-depth-sdxl-1.0-mid` at 545,197,729 B fp16 and
`-small` at 320,237,179 B fp16. Both take `variant="fp16"`.

### The wider set staged on the box, with D15 verdicts

Staged 2026-08-10 so later rounds and other beats do not wait on a download.
**Staging is not endorsement** — the r9 recipe uses only the first two rows, and
the licence column is what decides whether a weight may ever touch a canon
still.

| Repo / file | Bytes | Licence | D15 verdict |
|---|---|---|---|
| `diffusers/controlnet-depth-sdxl-1.0` fp16 | 2,502,139,134 | `openrail++` | **OK for canon** — r9's arm |
| `Intel/dpt-hybrid-midas` `pytorch_model.bin` | 489,648,389 | `apache-2.0` | **OK for canon** — r9's estimator |
| `Intel/dpt-large` `model.safetensors` | 1,367,456,044 | `apache-2.0` | **OK for canon** — safetensors fallback |
| `xinsir/controlnet-depth-sdxl-1.0` | 2,502,139,104 | `apache-2.0` | **OK for canon** — the named r10 substitution |
| `xinsir/controlnet-canny-sdxl-1.0` | 2,502,139,104 | `apache-2.0` | OK for canon, but see §2 — canny finds 0.12 % of this plate |
| `xinsir/controlnet-scribble-sdxl-1.0` | 2,502,139,104 | `apache-2.0` | OK for canon; same edge-density objection |
| `TheMistoAI/MistoLine` fp16 | 2,502,139,104 | `openrail++` **+ attribution condition** | **OK for canon ONLY with visible credit** — the README requires commercial users to acknowledge TheMisto.ai "in the documentation, website, or other prominent and visible locations". Usable, but it puts a standing obligation on anything it renders. |
| `LiheYoung/depth-anything-large-hf` | 1,341,322,868 | `apache-2.0` | **OK for canon** — the permissive alternative to the NC V2 weights |
| `lllyasviel/Annotators` — `sk_model.pth`, `sk_model2.pth`, `netG.pth` | 17,173,511 + 17,173,511 + 217,631,959 | **NONE DECLARED** | 🚨 **DO NOT USE FOR CANON STILLS.** Card says `license: other`, the README is 23 bytes of YAML, there is no LICENSE file, and per-file upstream terms differ (informative-drawings, Anime2Sketch, HED, CMU OpenPose — OpenPose upstream is itself non-commercial). Evaluation only until someone establishes per-file provenance. |

**Explicitly NOT staged, and not to be staged:** every `cc-by-nc-4.0` weight —
`Depth-Anything-V2-Base-hf` and `-Large-hf`, and
`bdsqlsz/qinglong_controlnet-lllite` (`cc-by-nc-sa-4.0`, and in a format
`ControlNetModel` cannot load anyway). Also avoided:
`ShermanG/ControlNet-Standard-Lineart-for-SDXL`, which declares **no licence at
all**, and `Eugeoter/noob-sdxl-controlnet-lineart_anime`, whose Fair AI Public
License 1.0-SD is copyleft-style — commercial use is allowed but derivatives and
public deployments must carry the same terms, which is a governance decision
rather than a steward's.

**Two things that need no download at all**, worth knowing before anyone stages
more weight: Canny is pure OpenCV with **no model and zero licence exposure**,
and `LineartStandardDetector` is likewise model-free — a Gaussian-difference in
OpenCV. If we ever want a lineart arm with no licence question attached, that is
the one to try first.

**No pip install of any kind.** Both additions load through `diffusers 0.29.2`
and `transformers 4.44.2` exactly as pinned; that is the main reason this
pairing was chosen over the alternatives, and it is a constraint on r9 rather
than a convenience.

### The load-pattern trap — every repo wants a different call

There is no single incantation, and the differences are silent rather than
loud. Getting these wrong costs a run each:

| Repo | `variant="fp16"` | Why |
|---|---|---|
| `diffusers/controlnet-*` | **pass it** | ships both `…fp16.safetensors` and fp32 |
| `xinsir/controlnet-*` | **must NOT pass it** | no `*.fp16.safetensors` exists; the single default file already holds fp16 weights, so passing `variant` raises |
| `TheMistoAI/MistoLine` | **must pass it** | the *inverse* case — it ships **only** the fp16 variant, so omitting `variant` raises |
| `TencentARC/t2i-adapter-*` | pass it — spelled correctly | the official cards contain the typo `varient="fp16"`, which is silently swallowed and downloads the 316 MB fp32 file instead |

Two more, both dtype and format rather than naming:

- **Load the ControlNet in bf16, not fp16.** `variant` selects which *file* to
  download; `torch_dtype` sets the in-memory dtype, and it must match the
  UNet's. So
  `ControlNetModel.from_pretrained(..., variant="fp16", torch_dtype=torch.bfloat16, use_safetensors=True)`.
  A ControlNet left in fp16 against a bf16 UNet fails at the first forward pass
  on a scalar-type mismatch.
- **`Intel/dpt-hybrid-midas` ships `pytorch_model.bin` only — a pickle, and this
  is a live hazard rather than a note.** PyTorch 2.6 flipped `torch.load` to
  default `weights_only=True`, and the box runs torch 2.11. Transformers is
  expected to handle it, but this is the one load in the recipe with no
  safetensors path. **Fallback if it fails: `Intel/dpt-large`** —
  1,367,456,044 B, `apache-2.0`, real `model.safetensors`, same DPT/MiDaS
  family and the same `DPTForDepthEstimation` API. Both are staged so Stage 0
  can simply use whichever loads. Prefer safetensors everywhere else in this
  manifest for the same reason.

**On `xinsir/controlnet-depth-sdxl-1.0` — the named r10 substitution if r9's
geometry comes back too weak.** apache-2.0 (licence-preferable), 2,502,139,104 B,
loads with the standard `ControlNetModel.from_pretrained`, trained on
MiDaS-and-Zoe depth so it accepts the very DPT map this plan already produces —
no new preprocessor, no new pip package. Two things to get right when we take
it, both of which would otherwise waste a run:

- **`variant="fp16"` raises on the xinsir repos.** There is no
  `*.fp16.safetensors` file; the single default file already holds fp16-precision
  weights. Load it with `torch_dtype=` and **no `variant` argument at all** —
  the opposite of the diffusers weight's call, which is exactly the kind of
  detail that gets copy-pasted wrong.
- Its card recommends `controlnet_conditioning_scale = 1.0` where the diffusers
  card recommends 0.5, so r9's sweep values do not carry across unchanged.

**Two negative results, recorded so they are not re-proposed:**

- **ControlNet-Union / Promax cannot run on our pin.** `ControlNetUnionModel`
  does not exist in diffusers 0.29.2 — it first appears in **v0.32.0** (PR
  #10131, merged 2024-12-11), and 0.32.x is itself known-buggy for Union, with
  the fixes landing in v0.35.0. Worse than a missing convenience wrapper: the
  Union configs declare `_class_name: "ControlNetModel"`, so a naive
  `from_pretrained` on 0.29.2 will *attempt* the load and then fail or misload
  on the extra Union tensors. Also `xinsir/controlnet-union-sdxl-1.0-promax`
  does not exist as a repo — promax is a differently-named file inside the base
  repo, which is why the ecosystem loads the `brad-twinkl` repack instead.
- **T2I-Adapter is the interesting cheap alternative, and is not being taken
  this round.** `TencentARC/t2i-adapter-depth-midas-sdxl-1.0` is `apache-2.0`
  and **158,060,440 B fp16 — sixteen times smaller** than a full ControlNet, and
  both `T2IAdapter` and `StableDiffusionXLAdapterPipeline` are present in 0.29.2.
  Adapters apply a looser, cheaper conditioning than ControlNets, which for a
  round that explicitly wants *loose* geometry is arguably a feature rather than
  a compromise. It is not r9's arm only because r9 should change one thing, and
  the diffusers ControlNet is the pairing with a published operating point. If
  r9's problem turns out to be that the control is too *tight* — a b15 clone in
  sunrise colours — this is the first thing to try. (Their model cards contain a
  typo, `varient="fp16"`, which is silently swallowed and downloads the 316 MB
  fp32 file instead.)

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

**Artifact and licence manifest** — exact byte sizes in §9 and the licence
verdicts in §5 come from a parallel research lane that queried the Hugging Face
API `tree/main` endpoint per repo rather than reading rounded figures off the
web pages, and probed the diffusers source tree tag by tag to date
`ControlNetUnionModel`:

- `https://huggingface.co/api/models/<repo>/tree/main?recursive=true`
- diffusers PR #10131 "Add ControlNetUnion" —
  <https://github.com/huggingface/diffusers/pull/10131> — and release v0.32.0
  <https://github.com/huggingface/diffusers/releases/tag/v0.32.0>
- Depth Anything V2 cards, per size —
  <https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf>,
  <https://huggingface.co/depth-anything/Depth-Anything-V2-Base-hf>,
  <https://huggingface.co/depth-anything/Depth-Anything-V2-Large-hf>
- Depth Anything V1, the apache-2.0 alternative —
  <https://huggingface.co/LiheYoung/depth-anything-large-hf>
- `TencentARC/t2i-adapter-depth-midas-sdxl-1.0` —
  <https://huggingface.co/TencentARC/t2i-adapter-depth-midas-sdxl-1.0>

**Still outstanding, and named so it is not mistaken for settled.** A third lane
was dispatched for the community's *comparative* findings — depth vs canny vs
lineart vs T2I-Adapter vs the IP-Adapter composition variants on colour leakage,
and their reported conditioning-scale ranges — and it did not return. Nothing
above depends on it: the sweep is anchored to the diffusers card's own published
`0.5` rather than to community ranges, the choice of depth over edges rests on
the measurement of our own plate in §2, and every licence was read off a card
directly. What that lane would add is corroboration on the *scale* values and on
whether the IP-Adapter composition route deserves a place in r10 — neither of
which changes what r9 should render.
