# Two subjects in one frame — a goblin AND a seedling

Researched 2026-08-09. External sources only: model cards, the Danbooru wiki,
diffusers documentation, papers, and the source repos of the extensions that
claim to solve this. Nothing in this memo is reasoned from our own code
comments; where our stack is described, the claim was executed against the real
venv and the command is given.

**Consumer.** `genomes/sapling/nodes/002b-first-citizen` — the goblin+seedling
wave. Node 002b has 21 beats. Five are plant-only (01, 12, 16, 18, 21) and beat
08 is guard-and-goblin with no plant; those six render today. The remaining
**15 beats need a goblin AND a plant in the same frame**, and all 15 are blocked
on the defect below. This memo exists to pick r6 for those 15.

**Status: research memo, provisional.** It recommends an experiment; it does
not authorise a wave. ONE SAMPLE still governs (CLAUDE.md), and the founder's
screen is still the taste ground truth.

---

## 1. What is actually failing

r3 and r4 both fused the two subjects. r4's record (shots.md, ledger record 26
`ep2-b13-r4-sample`, `reject_all`, confidence 0.85) is the cleanest evidence we
have: four seeds, **zero** contained the sapling as a plant — s0 wore a leaf as
a hat, s1 was an anime child holding a sprout, s2 an unreadable mass, s3 grew
the sprout out of the figure's head. r5 inverts which noun leads the sentence
and is unrendered.

Three externally-documented mechanisms are stacked on this prompt, and the
in-repo diagnosis names only the third.

### 1a. `1other` does not mean what the prompt is using it to mean

Every r3/r4/r5 goblin prompt opens with the Danbooru count tag `1other`. The
shots.md note reads it as "one **non-human** character". The Danbooru wiki
defines it as:

> "An image depicting a **humanoid** character of ambiguous or indeterminate
> gender, either because their face or features are not visible, they're
> androgynous, they're a genderless being or their gender is not canonically
> known."
> — [Danbooru wiki, `1other`](https://safebooru.donmai.us/wiki_pages/1other)

Two consequences, both matching the observed failures:

- `1other` asserts **a humanoid**. It is not a "not a person" tag; it is a
  "person of unknown gender" tag. That is why r4 returned an anime child (s1)
  and bare human legs (s0) *after* the person negatives were verified lifted
  onto the real path. The count tag was asking for the humanoid the negatives
  were trying to remove. The prompt is fighting itself, in the model's own
  vocabulary, and the tag wins because a leading count tag is the strongest
  positional prior a Danbooru-trained checkpoint has.
- Count tags count **characters**. Objects, plants and scenery are not
  characters and get no slot. So a Danbooru-native prompt has **no way to
  declare "and also a plant"** by counting. `2others` would ask for a second
  humanoid, not a plant. There is no count-tag fix; there is only a
  *composition* fix or a *vocabulary* fix.

### 1b. The plant-as-accessory prior is enormous in the training data

Animagine XL 3.1 was trained on ~870k Danbooru-tagged anime images and its own
card says it "is optimized for Danbooru-style tags rather than natural language
prompts"
([model card](https://huggingface.co/cagliostrolab/animagine-xl-3.1)). In that
corpus a plant near a character is overwhelmingly *worn* by the character:
`leaf on head` alone carries ~10.5k posts, alongside `flower on head`,
`hair ornament`, `plant girl`, `alraune` and the whole monster-girl family. The
tag `plant` exists (~71k posts) but as scenery, not as a co-subject.

So "leaf-hat" and "sprout-from-head" are not glitches. They are the maximum-
likelihood reading of *character + plant noun* under this checkpoint's prior.
This is the `concept bleeding` SDXL's own report names and that
[Isolated Diffusion](https://arxiv.org/abs/2403.16954) formalises: attachments
bind to the wrong subject when subjects share one conditioning stream.

**The operational consequence is the one the r4 post-mortem missed.** The
negatives are written as English prose — `no girl, no boy, no child, no person`
— which `sd_prompt._NEGATION` lifts into the negative prompt as the words
"girl", "boy", "child", "person". On a checkpoint trained on comma-separated
tags, prose nouns are weak negatives. The fusion classes have *exact tag names*
in the model's own vocabulary, and none of them are being negated. `leaf on
head` is not in any negative we ship.

### 1c. Subject order (what r5 tests)

Real and worth testing — CLIP is order-sensitive and a Danbooru model doubly so
("1girl/1boy, character name, from what series, everything else in any order" is
the card's own template, and the *ordered* part is the head of it). But r5
changes only this, on top of 1a and 1b, which are untouched. If r5 fails, it
will have failed for reasons that are not its own hypothesis, and we will have
learned nothing. **r5 as designed is not a clean experiment.** See §5.

---

## 2. The survey, ranked

Ranked by (probability of clearing the A1 veto class) ÷ (cost to us). "Cost"
counts our stack: diffusers on Apple MPS in **float32** (still_local.py forces
it — fp16 NaNs the SDXL UNet on this box), one job at a time at ~13 GB, or the
5090 box; $0 only; provenance sidecar per still; and character consistency is
A1, so anything that changes the checkpoint changes every frame we have.

| # | Option | Deps / licence | Cost | Fusion fix? | Verdict |
|---|---|---|---|---|---|
| 1 | **Danbooru-native vocabulary** (fix the count tag, negate the fusion tags) | none — already-shipped `--extra-neg` | ~1 h | Attacks 1a+1b directly, the two causes never yet addressed | **Run first** |
| 2 | **Two-pass inpaint** (plant first, goblin second) | diffusers core, verified present | ~5 h | *Structurally* cannot fuse — plant pixels are outside the mask | **Build as the guaranteed floor** |
| 3 | **Regional IP-Adapter masks** | `h94/IP-Adapter` (Apache-2.0), ~700 MB + 2.5 GB ViT-H | ~4 h + VRAM | Routes *image* conditioning per region; also buys A1 consistency | Strong second, 5090 box |
| 4 | **Attention Couple** (masked cross-attention, reimplemented) | custom `AttnProcessor`; refs are GPL-3.0/AGPL-3.0 — **must not vendor** | 10–14 h | The technique the community actually uses | Only if 1–3 fail |
| 5 | **Mixture-of-Diffusers tiling (SDXL)** | diffusers community pipeline | ~4 h + N× compute | Per-region prompts, blended | Compute-hostile on MPS fp32 |
| 6 | **Bounded Attention** (`run_xl.py`) | MIT, research code, CUDA | 8–12 h | Purpose-built for exactly this | 5090 box only; cite, don't start here |
| 7 | **ControlNet-SDXL layout** | ~2.5 GB controlnet | ~4 h | Places subjects; does not unbind attributes | Complement, not a fix |
| 8 | **Checkpoint swap** (Illustrious / NoobAI) | FAIPL-1.0-SD — already in `licence_gate.ALLOW` | ~2 h + re-render everything | Newer, better tag adherence | Breaks A1 across the show — separate wave |
| 9 | **BREAK syntax** | n/a | ~0 | **No.** See §3.9 | Rejected on mechanism |
| 10 | **Composable Diffusion (`AND`)** | SD1.5-only community pipeline | port required | Weak spatially | Rejected |

---

## 3. The options in detail

### 3.1 Danbooru-native vocabulary — 1 hour, zero new dependencies

Not a technique from a paper; a correction of two mistakes the model card and
the Danbooru wiki both document. Three moves:

1. **Stop asserting a humanoid we then negate.** `1other` (§1a) must go. The
   Danbooru-correct declaration for one goblin and no second character is
   `1boy, goblin, solo` — `solo` asserts *exactly one character in the image*,
   which is precisely the constraint we want (it forbids the anime child from
   becoming a second figure) while leaving the plant free to be scenery, since
   scenery is not a character. `goblin` is a real Danbooru tag and carries the
   green skin / ears / tusk morphology we keep writing out in prose.
2. **Negate the fusion classes in the model's own tag vocabulary**, not in
   prose: `leaf on head, plant girl, alraune, monster girl, flower on head,
   head wreath, hair ornament, leaf hair ornament, plant hair, potted plant`.
   These are the *exact* names of what r4 drew. This is the single largest
   untried lever and it costs one `--extra-neg` string.
3. **Give the plant a scenery binding, not a subject binding.** Danbooru's
   grammar for "a plant is in the shot and belongs to the ground" is
   `plant, grass, outdoors` — with the plant clause separated from the
   character clause by a comma boundary rather than a prepositional phrase that
   grammatically subordinates it to the goblin.

Watch two traps, both measured in our own code:

- `sd_prompt.count_tag()` derives the count tag from the leading clause via
  `_tag_from_clause`; you do not set it by writing it. Changing the intended tag
  means changing the leading clause (or the pattern). `still_local.py` prints
  the final `POS:` and `NEG:` before it renders — **read that line and confirm
  the tag before spending a single step.**
- `_NEGATION` only lifts a noun beginning with a letter, so `no 1girl` stays in
  the *positive* prompt asking for a girl. Tag-form negatives must go through
  `--extra-neg`, never through `no …` in the prompt body.

Licence: none. Cost: ~1 h of prompt work, ~40 GPU-seconds for four seeds.

### 3.2 Two-pass inpaint — the deterministic floor

This is [Isolated Diffusion](https://arxiv.org/abs/2403.16954)'s core idea
("isolate and resynthesise each subject individually with corresponding text
prompts to avoid mutual interference") reduced to something we can ship this
week, and it exploits the fact we already have: **the plant-only beats work.**
Three of the frames the founder kept are plant-only — his own words, *"the only
ones where no character had to be drawn"*. Beat 01's botanical binding is
proven.

Pass 1: render the seedling alone with beat 01's proven recipe.
Pass 2: `AutoPipelineForInpainting` with a mask covering the goblin's region
only, prompt = the goblin clause alone (`1boy, goblin, solo, …`), then
`image_processor.apply_overlay()` to force the unmasked area byte-identical.

Why it is the floor: **the plant is outside the mask, so no amount of prior can
turn it into a hat.** The worst case is a badly composited goblin, which is a
different and much cheaper failure than fusion — and a failure the founder has
never vetoed, because it has never been produced.

Verified present in the real venv this morning:

```
cd pipeline && <cb-venv>/bin/python3 -c "
from render_local import _shim_transformers; _shim_transformers()
from diffusers import StableDiffusionXLInpaintPipeline"
```
→ `SDXLInpaint OK after shim`, and `padding_mask_crop`, `strength`,
`mask_image`, `cross_attention_kwargs` are all present in `__call__`. The shim
is required (cb-venv runs transformers 5.2.0 against diffusers 0.29.0) and
`still_local.py` already calls it.

Diffusers explicitly sanctions using a non-inpaint checkpoint — "you can also
use regular checkpoints"; the trade is "the overall image quality may be lower,
but it generally tends to preserve the mask area", which for our purpose is the
*desirable* half of the trade
([inpaint guide](https://huggingface.co/docs/diffusers/en/using-diffusers/inpaint)).
Use `padding_mask_crop=32` (crops+upscales the masked region, then overlays) and
`mask_processor.blur(mask, blur_factor≈16)` for the seam.

Cost: ~5 h for a `still_two_pass.py` alongside `still_local.py`. No new
dependency, no new licence, animagine stays the checkpoint so A1 is untouched.

### 3.3 Regional IP-Adapter masks — native diffusers, and it pays an A1 dividend

Diffusers ships binary masking for IP-Adapter as a documented, first-class
feature: `IPAdapterMaskProcessor` preprocesses one mask per IP-Adapter image and
they are passed as `cross_attention_kwargs={"ip_adapter_masks": masks}`, with
per-image scales. The doc's worked example is literally two characters in one
frame with `prompt="2 girls"`
([IP-Adapter guide](https://huggingface.co/docs/diffusers/en/using-diffusers/ip_adapter)).
Verified importable in cb-venv (`from diffusers.image_processor import
IPAdapterMaskProcessor` → OK) and `IPAdapterAttnProcessor2_0.__call__` accepts
`ip_adapter_masks`.

What it does and does not do: it routes **image** conditioning regionally, not
text. So it does not by itself stop the text prompt from binding a leaf to a
head — but conditioning the plant region on an approved plant still and the
goblin region on an approved goblin still puts strong regional evidence against
fusion, and it directly serves A1 (character consistency), which no other option
here does.

Costs: `ip-adapter_sdxl.bin` ~700 MB plus a CLIP ViT-H image encoder ~2.5 GB, on
top of a **float32** SDXL that already sits near 13 GB on MPS. This one belongs
on the 5090 box, not the Mac. Licence: `h94/IP-Adapter` is Apache-2.0 — clean,
and it claims nothing over output. ~4 h.

### 3.4 Attention Couple / regional cross-attention — the real technique, and a licence trap

This is what the community actually uses for two characters. The mechanism:
split the prompt into per-region segments, encode each separately, and mask
cross-attention so latents inside region *k* attend only to segment *k*'s
tokens. Reference implementations:

- [`Haoming02/sd-forge-couple`](https://github.com/Haoming02/sd-forge-couple) —
  Basic (auto tiles) / Advanced (explicit 0.0–1.0 coordinate boxes + weights) /
  Mask (hand-drawn) modes; states "SD1 and SDXL are supported". **GPL-3.0.**
- [`hako-mikan/sd-webui-regional-prompter`](https://github.com/hako-mikan/sd-webui-regional-prompter)
  — distinguishes *Attention mode* (normal speed) from *Latent mode* ("the
  number of areas × the generation time of one pic", better LoRA separation);
  `BREAK`/`AND`/`ADDCOL`/`ADDROW`/`ADDBASE`/`ADDCOMM` separators; base-ratio
  blending. **AGPL-3.0.**
- [`pamparamm/ComfyUI-ppm`](https://github.com/pamparamm/ComfyUI-ppm) —
  Attention Couple for SDXL and Anima, ComfyUI nodes.

A community write-up puts regional prompting at ~91% accuracy on 2-character
scenes versus ~68% for a single prompt
([Apatero guide](https://www.apatero.com/blog/regional-prompter-comfyui-complete-guide-2025)) —
treat as indicative, not measured by us.

**Two hard blockers for us.** (a) Every mature implementation is a ComfyUI or
Forge extension; we run bare diffusers and have no ComfyUI. There is **no
maintained pure-diffusers Attention Couple** — the diffusers community pipeline
`regional_prompting` (hako-mikan's own port) is listed **SD 1.5 only**
([community README](https://github.com/huggingface/diffusers/blob/main/examples/community/README.md)).
(b) GPL-3.0 and AGPL-3.0 are exactly the copyleft family `licence_gate.py`
treats as fatal to this tree. **We may read them; we must not vendor or
translate them line-by-line.** A clean-room reimplementation from the published
technique is ~150–250 lines of custom `AttnProcessor` plus mask bookkeeping at
every UNet resolution, and it must be re-validated on MPS where custom attention
paths are historically where this box breaks. Budget 10–14 h with real risk of
overrun. Not the first move.

For completeness: [MaskAttn-SDXL](https://arxiv.org/abs/2509.15357) does this
with *learned* masking heads inside the SDXL UNet — it requires training, so it
is out; and [training-free regional prompting](https://arxiv.org/abs/2411.02395)
targets DiT models (SD3/FLUX), not SDXL.

### 3.5 Mixture-of-Diffusers tiling, SDXL

The diffusers community list carries `stable_diffusion_mixture_tiling_sdxl` (an
SDXL port of Álvaro B. Jiménez's Mixture of Diffusers) — "generates cohesive
images by integrating multiple diffusion processes, each focused on a specific
image region". Genuinely SDXL and genuinely official-adjacent, unlike everything
in §3.4. Two problems: it is grid/tile shaped, so a plant and a goblin who
overlap (he sits *in its shade*) do not decompose cleanly; and it runs a
diffusion process per tile, multiplying an already float32-on-MPS render. Verify
the exact `custom_pipeline` id against diffusers 0.29.x before costing it —
community pipelines are fetched from `main` and routinely need a newer core.

### 3.6 Bounded Attention

[Be Yourself: Bounded Attention](https://arxiv.org/abs/2403.16990) (ECCV 2024) is
the closest paper to our exact defect: training-free, it bounds information flow
during sampling to "prevent detrimental leakage among subjects". The
[repo](https://github.com/omer11a/bounded-attention) is **MIT** and ships
`run_xl.py` for SDXL, taking bounding boxes `[(x0,y0,x1,y1), …]` in 0–1 space
plus per-subject token indices, with `num_guidance_steps` trading runtime for
strength. Research code, CUDA-oriented, needs an `nltk` tagger download. If §3.1
and §3.2 both disappoint, this is the principled next stop — on the 5090 box.
8–12 h.

### 3.7 ControlNet-SDXL layout conditioning

A crude two-blob scribble or depth map fixes *where* each subject is. It does
not fix *attribute binding* — a leaf can still land on a head that is in the
right place. Useful as a composition lock on top of a winner, not as the fix.
~4 h, ~2.5 GB weights.

### 3.8 Checkpoint swap — real, but it is a different project

Illustrious-XL and NoobAI-XL post-date Animagine XL 3.1 (both second-half 2024);
Illustrious builds on Kohaku XL-Beta "for cleaner linework and tag adherence"
and NoobAI extends Illustrious on a broader Danbooru/e621 set. Both ship under
Fair AI Public License 1.0-SD, which `licence_gate.ALLOW` already recognises
(`\bfaipl\b`), so the licence road is open — note that Animagine's own card now
supersedes its old FAIPL tag with CreativeML Open RAIL++-M, whose *use
restrictions travel* (our gate records this as D15).

But every approved still in the tree was drawn by animagine, and **A1 is
character consistency**. Swapping the checkpoint mid-episode is not a two-subject
fix, it is a re-shoot of the show. File it as its own wave with its own
one-sample gate; do not entangle it with r6.

### 3.9 BREAK — rejected on mechanism, and this matters

BREAK is not a model feature and has no spatial semantics. It is an
AUTOMATIC1111 *prompt-parser* behaviour: CLIP processes prompts in 75-token
chunks, and BREAK "fills the current chunk with padding characters" so the next
text starts a fresh chunk — you are choosing where the chunk boundary lands, and
nothing else
([A1111 features wiki](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/features),
[issue #2305](https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/2305)).
Regional Prompter *reuses* the keyword as a region separator; that spatial
meaning belongs to the extension, not to BREAK. Animagine's card never mentions
it.

Diffusers has no BREAK. The nearest equivalent is
[compel](https://github.com/damian0815/compel) (MIT, `pip install compel`,
supports SDXL's dual encoders), whose `.and()` conjunction concatenates separate
embeddings. **Not installed in either of our venvs** (checked). Two honest
notes: (a) at 70–73 positive tokens our prompts do not even reach one chunk, so
BREAK-style chunking has nothing to separate; (b) compel would let us exceed 77
tokens, which is a *different* win (it would have prevented the trailing-sentence
drop that cost us the style anchor on eleven beats) and is worth ~2 h on its own
merits — but it will not unfuse a goblin.

### 3.10 Composable Diffusion

[Liu et al.](https://arxiv.org/abs/2206.01714)'s conjunction operator sums
separate noise predictions. Diffusers ships it as `composable_stable_diffusion`,
**SD 1.5 only**, and it controls *presence* far better than *position* — it does
not stop a leaf landing on a head. Porting to SDXL for a technique that does not
target our failure mode is not worth the hours.

---

## 4. What the founder's record constrains

- **A1 (character consistency) is the veto axis here**, and every r3/r4 rejection
  was an A1 rejection, not a style one. r4 proved the style half of the fix works
  (all four came back as soft cinematic anime); *A1 did not move*. So r6 must be
  scored on A1 and only A1 — a style improvement is not a pass.
- **Deadpan cinematic anime, no mascot fusion.** Options that make the plant
  *cuter* to distinguish it (a face, a mascot reading) are the wrong direction:
  the same founder killed v2 low-detail and revoked beat 01 as "tooooo tall".
- **`still_local.py` ends with `subprocess.run(["open"] + opened)`** — it throws
  every rendered still onto the founder's screen. He is reviewing right now. Any
  r6 run must land in `takes/stills/` without `open`; add a `--no-open` flag (or
  set the equivalent) *before* the first sample, not after.
- Provenance sidecar per still is non-negotiable (§7.2). Any new script must
  write the same `.meta.yaml` shape `still_local.py` does — model, prompt,
  negative, seed, and for a two-pass render **both** passes' prompts and the
  mask, or the record does not describe what made the picture.

---

## 5. Recommended r6 experiment

**One beat. Four seeds. One recipe change. Ledger entry before any screen.**

Beat 13 (THE SHADE), because it is the beat r4 was rejected on — so r6 is a
controlled comparison against a recorded 0/4, not against a vibe. Same four
seeds as r3/r4/r5, so the column stays a controlled pair all the way down.

**r6 = §3.1 only.** Not §3.2, not §3.3. The reason is the reason r5 is a muddy
experiment: §1a and §1b have *never been tested*, they cost an hour and forty
GPU-seconds, and every expensive option below them is only worth building if the
cheap correction fails. Running vocabulary and architecture in the same sample
would tell us nothing about either — the same argument shots.md already made for
holding the count tag constant while inverting word order, applied one rung up.

Change exactly three things, all inside the existing tooling:

1. Leading clause rewritten so `_tag_from_clause` yields **`1boy`**, with
   `goblin, solo` following. (`1other` asserts the humanoid we are negating.)
2. `--extra-neg "leaf on head, plant girl, alraune, monster girl, flower on
   head, head wreath, hair ornament, leaf hair ornament, plant hair"` — the
   fusion classes in tag form. Confirm against the printed `NEG:` line that the
   77-token negative budget did not drop them; `fit_negative` will trim, and
   what it trims must be the house boilerplate, not these.
3. Plant re-bound as scenery — `plant, grass, outdoors` in its own clause —
   rather than in a prepositional phrase hanging off the goblin.

Everything else held: checkpoint, resolution, steps, CFG, style anchor,
boosters, seeds. Run it detached, write to `takes/stills/`, **do not `open`**.

### Success criterion — scored before the founder sees anything

Per seed, four binary predicates. This is the A1 veto class written down so it
can be failed by a machine:

| | Predicate | r4 result |
|---|---|---|
| P1 | The plant is present **as a plant** — stem plus two cotyledon leaves, rooted in ground, not touching the character's body | 0/4 |
| P2 | The goblin is present **as a goblin** — green, big ears, tusk, cloak; not a human child | 1/4 (s1 was a child) |
| P3 | **No fusion**: nothing plant-like on or growing from the head or body; no plant-creature hybrid | 0/4 |
| P4 | **Two separate silhouettes** with background visible between them somewhere | 0/4 |

**Gate: ≥3 of 4 seeds pass all four predicates.** r4 scored 0/4 on P1, P3 and
P4, so any result above zero is information and only ≥3/4 is a pass. The
steward taste model (`taste/steward-model.v1.md`) scores and predicts into
`steward-model.ledger.yaml` **before** the contact sheet goes anywhere near a
screen, per the standing order. Failing the gate is a normal outcome and must
not be argued past — "a metric agreeing with me is not a sample" cuts both ways.

### The ladder if r6 fails

Fixed in advance so the next step is not chosen by whoever is disappointed:

- **r6 fails on P1/P3 (still fusing)** → build §3.2, the two-pass inpaint. It is
  the only option that cannot fuse, and its cost is bounded at ~5 h with no new
  dependency. Ship it as the recipe for all 15 beats.
- **r6 fails on P2 (goblin off-model / a human)** → §3.3, regional IP-Adapter on
  the 5090 box, conditioning the goblin region on an approved goblin still. That
  is an A1 problem and IP-Adapter is the A1 tool.
- **Both, or the composite reads pasted** → §3.6 Bounded Attention (MIT, SDXL,
  5090). §3.4 only after that, clean-room, never vendored.

Two things to file for their own experiments, not to fold into r6: compel for
the 77-token ceiling (§3.9), and the Illustrious/NoobAI checkpoint question
(§3.8).

---

## Sources

- [cagliostrolab/animagine-xl-3.1 model card](https://huggingface.co/cagliostrolab/animagine-xl-3.1) — Danbooru-tag optimisation, prompt template, ~870k training images, CFG 5–7, CreativeML Open RAIL++-M
- [Danbooru wiki, `1other`](https://safebooru.donmai.us/wiki_pages/1other) — "a humanoid character of ambiguous or indeterminate gender"; objects and plants are not characters
- [Isolated Diffusion (arXiv 2403.16954)](https://arxiv.org/abs/2403.16954) — concept bleeding; isolate-and-resynthesise per subject
- [Be Yourself: Bounded Attention (arXiv 2403.16990)](https://arxiv.org/abs/2403.16990) / [code, MIT](https://github.com/omer11a/bounded-attention) — training-free multi-subject, `run_xl.py`
- [MaskAttn-SDXL (arXiv 2509.15357)](https://arxiv.org/abs/2509.15357) — learned masked cross-attention in the SDXL UNet (requires training)
- [Training-free Regional Prompting for DiT (arXiv 2411.02395)](https://arxiv.org/abs/2411.02395) — SD3/FLUX, not SDXL
- [Composable Diffusion (arXiv 2206.01714)](https://arxiv.org/abs/2206.01714)
- [diffusers IP-Adapter guide](https://huggingface.co/docs/diffusers/en/using-diffusers/ip_adapter) — `IPAdapterMaskProcessor`, `ip_adapter_masks`, SDXL
- [diffusers inpaint guide](https://huggingface.co/docs/diffusers/en/using-diffusers/inpaint) — non-inpaint checkpoints, `padding_mask_crop`, mask blur, `apply_overlay`, chained pipelines
- [diffusers community pipelines README](https://github.com/huggingface/diffusers/blob/main/examples/community/README.md) — `regional_prompting` (SD1.5), `composable_stable_diffusion` (SD1.5), `stable_diffusion_mixture_tiling_sdxl`
- [hako-mikan/sd-webui-regional-prompter](https://github.com/hako-mikan/sd-webui-regional-prompter) — AGPL-3.0; attention vs latent mode; BREAK/AND separators
- [Haoming02/sd-forge-couple](https://github.com/Haoming02/sd-forge-couple) — GPL-3.0; Attention Couple, SD1+SDXL
- [pamparamm/ComfyUI-ppm](https://github.com/pamparamm/ComfyUI-ppm) — Attention Couple for SDXL/Anima
- [AUTOMATIC1111 features wiki](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/features) and [issue #2305](https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/2305) — BREAK is 75-token chunk padding
- [damian0815/compel](https://github.com/damian0815/compel) — MIT, SDXL dual encoders, `.and()` conjunction
- [OnomaAIResearch/Illustrious-XL-v1.1](https://huggingface.co/OnomaAIResearch/Illustrious-XL-v1.1) and [Animagine vs Illustrious/NoobAI comparison](https://note.com/kazuya_bros/n/n84fa6fe9360b?hl=en) — successor checkpoints, tag adherence
- [Regional Prompter in ComfyUI guide](https://www.apatero.com/blog/regional-prompter-comfyui-complete-guide-2025) — indicative 2-character accuracy figures (not measured by us)

Local facts in this memo were executed, not assumed: diffusers 0.29.0 / torch
2.6.0 / transformers 5.2.0 in cb-venv (0.29.2 / 2.13.0 / 4.44.2 in the m1pro
farm venv); `StableDiffusionXLInpaintPipeline` imports after
`render_local._shim_transformers()`; `padding_mask_crop`, `strength`,
`mask_image` and `cross_attention_kwargs` are all in its `__call__`;
`IPAdapterMaskProcessor` imports and `IPAdapterAttnProcessor2_0.__call__`
accepts `ip_adapter_masks`; compel is absent from both venvs.
