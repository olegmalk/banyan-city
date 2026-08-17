# COMPOSITE-THEN-INPAINT — the house pattern for an attribute the sampler cannot hit

**2026-08-17, the bark lane (beats 06/08/10).** Written because the mechanism that
ended a four-day prop block has just been chosen for a completely different
problem (leaf count), and the next lane needs the method rather than the anecdote.
Thirty samples across four boards stand behind it, and so does one place it does
**not** work, which is §11.

The founder's ask today was *"we need to have control."* This is currently the only
mechanism in the repo that delivers it, and the reason is one sentence:

> **With a composited init, the thing you want is not a sample from the model.**

Load-bearing rather than convenient: the box has **no text-to-video path** —
`ltx_i2v.py:543` makes `init` required — so every beat travels forward as pixels
regardless. An init is infrastructure.

---

## 1. The class of problem this predicts — recognise it without being told

Two different diagnoses land in the same place (the pixels), and it is worth
keeping them apart because they have different signatures.

**CLASS A — NO CONTINUOUS ENCODING.** The attribute is not a direction in the
conditioning space at all, so there is no knob to turn. *Cardinality is the type
case:* CLIP's numeral embeddings are near-identical, so the number barely reaches
the model (arXiv:2503.06884 tests prompt refinement directly and rejects it;
arXiv:2406.10210 measures plain SDXL numerals at 26–28%, ceiling ~59% **with** a
trained ReLayout U-Net and a detector in the loop). Our own frames agree: the
strongest available wording — numeral **plus** explicit negation of every wrong
count — returned 0 of 16 frames with two leaves, while height, a continuous
adjective, bound 3 of 4 in the same batch.

**CLASS B — BAND COLLISION.** The attribute *is* encodable, but its carrier in the
image occupies the same frequency band as a structure you must not lose. Then
every noise level high enough to write the one rewrites the other, and the two
thresholds **coincide in sigma** instead of being separated by a gap. Bark was
this: crust is high-frequency relief and the board's straight silhouette is
carried in the same band.

**The three signs of a band collision, all cheap to test:**

1. **The bracket is ADJACENT in `int(steps × strength)`.** Beat 10's boundary sat
   between 0.79 (clean rectangle, no bark) and 0.82 (bark crust, notched edge) —
   at 40 steps those are steps 31 and 32. Nothing in between exists to try.
2. **Raising the step count buys real new positions and the boundary does not
   move.** Beat 06 was re-run at 80 steps: 0.638 (step 51) is a position 40 steps
   cannot express and is not a duplicate of 50/80 — and the wall reappeared at
   51 → 52, at the same fraction. More steps is a finer ruler, not a fix.
3. **One axis of the ask binds while another never does at any setting.** Beat 06:
   shape ceiling 0.638, material floor never reached anywhere on the ladder.

**Class A or Class B, the move is the same: stop asking the model to invent the
structure.** But note which one you have, because Class A is the *stronger* case —
a composited count is not a sample from anything, whereas a composited texture
still has to survive a sampler that may disagree with it (§11).

## 2. Why 0.30, mechanically

An img2img/inpaint pass runs only `int(steps × strength)` of its denoising
schedule. At 40 steps, strength 0.30 runs **12** steps, starting from a latent that
still carries the init's structure; the early high-sigma steps where global layout
is decided **never run**. That is the whole reason *"finish this structure"*
succeeds where *"invent this structure"* fails, and it is why 0.2–0.35 is the band
community practice names for preserving layout and identity
(stable-diffusion-art.com/denoising-strength, learn.rundiffusion.com).

Two more things follow from the same arithmetic and both bit us:

- **The knob is quantised.** `int(40 × 0.79) = 31` and `int(40 × 0.82) = 32`. Two
  strengths inside one step are the *same render* — beat 10's 0.805 came back
  **byte-identical** to 0.82. If your bracket is one step wide, raise steps or stop.
- **Low strength is not free.** At 0.30 the model still moves the same *amount* of
  pixel it moves at 0.45 (mean |Δ| inside the region 14.5 vs 15.9 — see §9). What
  changes is **what it draws**, not how much.

For the loop this pattern implies, there is a paper: **arXiv:2505.04831**
incrementally inpaints under a reward and uses **object count** as its proof of
concept. Beats 06 and 10 ran that loop by hand, one sample at a time.

## 3. The three anti-decal choices

A composite can fail in a way no prompted render can: it can look *pasted*. Each
of these was made on evidence from the plate, and together they are the checklist.

1. **PROCEDURAL, NOT A PHOTOGRAPH OR A CLONE.** A photo imports a licence and a
   provenance question into a repo whose rule is provenance always, and photoreal
   detail dropped into a cel-shaded frame *is* the decal failure mode by
   construction. A shifted clone of nearby pixels is decal tell #4, a repeat.
2. **FITTED TO THE OBJECT, NOT TO THE MASK.** Beat 10's mask quad was *not* the
   board — it overshot ~10px on every side and ran into a gripping hand and the
   coat. Filling the quad would have painted bark over fingers. The board was
   segmented, and the texture mapped through a homography fitted to *that*
   silhouette, so the texture edge and the object edge are the same edge. This is
   the strongest single defence against reading as a decal.
3. **THE PLATE'S OWN LIGHT IS KEPT.** Direction *measured* from the low-pass
   luminance gradient of the plate's own object (beat 10: dx +0.385 dy −0.923;
   beat 06: dx +0.575 dy −0.818), carried into object space through the
   homography's Jacobian; the plate's low-frequency shading field then re-applied
   multiplicatively, so a lit rim stays lit and a shaded corner stays shaded.

Plus: inset the drawing 2px and paint the surviving rim as a dark cel outline, so
the new content keeps a drawn edge in the plate's own dialect instead of a texture
running off a cliff.

**The five decal tells, committed before the render and checked after:** texture
axes not following the object's tilt; a pattern ignoring the frame's light; a
swatch stopping short of, or overrunning, the object's own edge; visible tiling or
a repeat; detail at the wrong scale read against a hand or other in-frame ruler.
Across thirty samples **FAIL-DECAL never fired below 0.45** — the tells are worth
keeping precisely because they came back negative every time and so did not cost a
single rung.

## 4. The numbers actually used

| | |
|---|---|
| Model | `cagliostrolab/animagine-xl-3.1` **base** weights in `StableDiffusionXLInpaintPipeline` (`unet.in_channels=4`, the latent-blend branch — diffusers 0.29.2 supports it explicitly) |
| Steps / cfg / seed | **40 / 7.5 / 20260815** on every sample |
| `padding_mask_crop` / `blur` | **64 / 8** (pad 12 tested once, §11) |
| Strength | **0.30 = the passing value.** 0.45 fails. |
| Composite | `--relief 3.4 --target-lum 78 --target-std 26 --rim 2 --tex 768 --ss 3`, seeded value-noise fbm; per-object grain via `--noise-scale` |
| Cost / time | **$0**, 3.7–6.2s render, 9–15s wall, local rtx5090 |
| Gate | `--init-sha256` asserted before anything loads; `--dry-run` writes the mask and exits before a model is touched |

**Prompt discipline that made the samples mean anything:** one variable per fire,
and the prompt files were **never opened** across all thirty — measured on
animagine's own `CLIPTokenizer` at 52/77 positive and **exactly 77/77** negative
(confirmed real, not a silent clamp, by tokenizing with a probe word appended:
it went to 81). Zero negative headroom means **any word added silently drops the
tail**, so that file is frozen unless a rung is spent on it.

## 5. What failed before it worked

**Composites rejected BY EYE before any GPU ran.** This is the point of doing the
structure with image processing: a rejection costs seconds.

| # | What it looked like | The actual cause | Fix |
|---|---|---|---|
| b10 v1 | scratched **burlap** | 4 octaves at gx=20 — too many thin lines; raw segmentation left notches and a staircase | fewer wider plates, 3 octaves; convex hull for straight edges |
| b10 v2 | chrome clip **re-opened** | subtracting `bright` re-cut it, and `fill_holes` cannot close a hole touching the border | union the filled segment back in *after* the exclusion |
| b06 v1 | bark stopped **12px inside** the board's own left edge, corner chamfered | the hull was the hull of the *visible* face; this board has a dark rim the colour rule misses | the quad **is** the board here, so the quad is the base |
| b06 v2 | **corduroy** | beat 10's noise grid on a 190×215px board — grain scale is per-object, not per-recipe | `--noise-scale 0.62` |
| b06 v3 | **half the chrome clip standing** | the board's right half is warmer (B-R −1..+1), so 60px of face under the clip went unseen and the clip-gap measured 60px instead of 26 | discriminate on B-G, relax B-R to ≥ −2 |
| b08 c2 | "grey weathered slate" — **a rejection for the wrong reason** | the statistic was contaminated: the quad contains the goblin's **green** hand (R-G −26..−2) where beat 06's contains a pale human hand. Measured on the pixels the compositor actually changed: b06 +12.3, b08 +12.1, c1 +11.0, my "fix" +8.6 — c1 already matched | revert; c3 is byte-identical to c1, which is how the revert was verified |

**The colour rule transferred ZERO times across four boards.** Navy needed
`B-R ≥ 10`; near-black needed `B-R ≥ -2`; maroon **inverted** it (`B-G ≥ 3`); warm
mid-brown needed `R-G ≥ 16 & B-G ≤ -8`, whose sign the previous board *accepted*
with. Assume you re-derive segmentation for every plate, and measure the pixels
your compositor changes — not the pixels inside your quad.

**Two structural fixes worth stealing.** (a) The chrome clip sat *on* the board's
top edge on beat 06 and *protruded above* it on beat 08 — no quad that is the
board can reach it and no hole-filling can either, so it is filled by **geometry**
(per column, quad-top → first face pixel, only where the gap is small) and unioned
back in **after** the bright subtraction. (b) When the object is rotated, a
horizontal top band takes a wedge out of it — run the band along the board's own
top **normal**.

**And one sampler-side failure that became a design rule.** At 0.45 beat 10 split
its slab in two where the model read the **deepest composited fissure as an object
boundary** — in this dialect a strong dark line *is* an edge. So: **never
composite an internal line stronger than the object's own outline.** The leaf
translation is a midrib, and it should be a luminance ridge rather than a drawn
line.

## 6. Two laws that bite compositors specifically

- **THE VACANCY LAW.** An emptied region is a hole the model fills with the largest
  available noun, and **the negative does not reach it**. Never leave an unpainted
  gap you have not given positive content.
- **THE HAND LAW.** If a figure is in frame, every hand must be specified —
  including ones you do not care about.

## 7. Scoring a blend — the failure modes, and where the boundary sat

The two directions fail differently, which is what makes a blend scoreable by eye:

**TOO HIGH — it invents, and it merges or splits.** Beat 10 at 0.99: the rectangle
was *gone*, replaced by a dark shaggy pelt with torn spiky edges. At 0.45, with the
composite already in place: the slab **split into two planks** with background
through the gap, the top edge chewed into a ragged crest. Beat 06 at the same 0.45:
top edge a chewed crest with a bite out of it, bottom-right corner rounded, and a
bark-coloured wedge drawn **over a finger**. Above 0.65 on beat 06 the region went
**translucent** — the tunic and sash read *through* the board and the crossing hand
was deleted outright. **The named modes:** `FAIL-SHAPE` (straight edges or square
corners lost), `FAIL-MERGE`/split (two adjacent instances become one, or one
becomes two along an internal line), and for counts the same thing under a
different name — this is exactly why the published count methods warn they fail
when instances are **identical, adjacent and overlapping**.

**TOO LOW — it reads pasted, or traced.** The surface stays the composite's own
soft airbrushed relief: smooth gradients, no drawn edges, and at a distance it
reads as *a shadow cast on cloth* or a soft-focus panel rather than the material.
That is beat 08's entire five-sample result (§11).

**The pass tell, and it is a positive one you can see at 3x:** the soft procedural
relief **comes back as crisp cel line work in the same weight and colour as the
line art elsewhere in the frame.** On beat 06's pass the fissures returned as hard
black cel lines and flat cel-shaded plates; the model had *contributed*, and the
contribution was visible against the composite. If you cannot see a difference
between your composite and the output, the pass is a paste.

**Two cheap numeric filters that agree with the eye — filters, never verdicts:**

- **Where the energy went.** Highpass (σ3) std inside the region, in → out:
  beat 06's pass **19.75 → 19.27** but relocated *into edges*; beat 08's failure
  **17.63 → 17.04**, energy still in gradients. Same magnitude, different kind.
- **How much moved.** Mean |Δ| against the init inside the region: 14.5 / 16.8 /
  13.1 (beat 08 failures) against **15.9** (beat 06 pass). *The sampler engages the
  same amount in both.* Engagement is not evidence of success — a metric agreeing
  with you is not a sample.

**Where the boundary sat, measured:** with a **bare** init the two thresholds
coincided (beat 06: shape ceiling 0.638, material floor never reached; beat 10:
0.79 clean / 0.82 crust-with-notch, adjacent steps). With a **composited** init
they separated and on beat 06 they **crossed**: material present *and* shape intact
at **0.30**, shape gone by **0.45**. So the working window is 0.30, the failure
above it is shape, and the failure below it is a paste.

---

## 8. ~~PRE-REGISTRATION — `pipeline/sapling_init_composite.py`~~ — STOOD DOWN 2026-08-17

**House style: the superseded text stays and the correction is written beside it.**

This section pre-registered a **second, additive** compositor for the sapling init
(two ordinary leaves drawn, at the plate's own height) with five guarantees and
eight numeric checks — count = 2 at ≥400px, ≥10px gap between blades, apex within
12px, height ratio 0.90–1.10 against sudden doubling, blade aspect 1.6–2.6,
residual < 400px, maxdiff 0 outside, byte determinism. **The lead stood it down**
before any pixel existed: the leaf-count lane already has a working compositor
("composite passes count with zero GPU fires"), and a duplicate tool in the tree is
worse than none. The bar was not bent and the tool was not run — it was deleted
unrun. Ownership: **the leaf-count lane owns the composite and the inpaint rungs**;
`cnet-audit` owns the ControlNet scribble hint, which is a *control image* biasing
count, never pinning it.

**Two findings from that hour are kept because they are about the plate, not about
the tool, and the lane that owns the composite may want them:**

1. **On `farm-out/ep2-b01-brightbase-figmatte/01-cold-open-bright-i35b-s0.png` the
   sprout has THREE lance-shaped blades, not four** — two upper, one long
   lower-left; the dark shape below the junction is stem line-work, traced at 8x
   (junction ≈ 415,700; blade tips ≈ 338,608 / 508,681 / 250,755).
2. **Subtraction alone cannot serve the shape axis.** Those blades are **narrow and
   lance-shaped**, and canon §2.2 rules lance shapes out — the founder's own
   ruling, 2026-08-17, is *"average leaves"*. Removing one of three passes the
   COUNT axis and leaves two wrong-shaped leaves. Count and shape are one job.

## 9. WHERE THE PATTERN BREAKS — beat 08, and both explanations are dead

**This is the honest limit and it is not a small one.** Seven samples across two
plates, three boards' worth of segmentation work, and beat 08 never passed.

**What transferred completely: the GEOMETRY half.** On three different boards the
composite tracked the traced edge to within **1.8px on every edge**, killed the
chrome clip, kept one straight top edge, and preserved both gripping hands and
their fingertip notches through five renders at three strengths. Not one FAIL-SHAPE,
FAIL-SEAM or FAIL-DECAL below 0.45. **Getting geometry out of the sampler works.**

**What did not transfer: the MATERIAL half.** At 0.30 and 0.38 the surface stayed
the composite's own soft smeared shading — 7 of 8 bar terms, `FAIL-MATERIAL`, the
same band all twenty-eight prior samples sat in. At 0.45 it failed *identically to
the other two beats*: translucent, tunic and sash reading through, surface becoming
cloth folds. **The window that exists on beats 06 and 10 is closed on beat 08.**

**Both candidate explanations were tested with one variable each, and both are
rejected:**

- **Board pixel size — NO.** `SIZETEST` resampled the board region **3.01×** to
  516px wide, twice beat 06's passing 254px, every other variable pinned. Same
  soft shading, *softer than its own init*. Also tested: `padding_mask_crop`
  64 → 12, computed rather than guessed (at pad 64 this board is 50% of the padded
  crop where beat 06's passing board was 70%; at pad 12 it is 71%). The model
  responded — thin hard hatch strokes appeared, which no other sample had — but
  they read as **scratches, not fissures**. Crop share is not the limiter either.
- **Shot scale / register — NO, and this one was a real hypothesis with a real
  test.** The theory: beat 06's plate is a close torso shot where animagine draws
  heavy cel line work; beat 08's is a whole-body two-shot the model renders with
  flat soft shading. A tighter plate was staged with the framing tag as the sole
  variable and it **landed on beat 06's register with a bigger board** — head at
  190px, **15.6%** of frame height against beat 06's passing **16.0%** and the
  failing wide shot's **10.3%**, board 1.65× the pixels. Result at 0.30:
  `FAIL-MATERIAL`, 7 of 8, again. At 0.45: hard-edged vertical splits arrive and
  they *are* real drawn line work, but the surface between them is still a smooth
  gradient — checked plank, not crust.

**So: the pattern holds across scale and framing for GEOMETRY, and its MATERIAL
half has an unexplained plate dependence.** What is ruled out on beat 08: strength
(0.30/0.38/0.45), board pixel size, crop share, shot scale, and the wording (never
opened). What is left and untested: the surrounding content's own texture register
(this plate's neighbours are teal robe and cloak, all flat), the checkpoint's prior
for the *scene class*, and a material the negative does not fence away. **Do not
spend rounds chasing a bigger board face or a tighter shot — both are already
dead.** If you need bark on beat 08, the next honest lever is a different one, and
naming which is the next lane's call, not this one's.

## 10. Running the pattern on a new attribute — the order that worked

1. **Split the ask by axis** and ask what CLIP does with each. Material and scale
   are continuous and usually bind by wording; geometry binds weakly; cardinality
   does not bind at all. **Do not composite an axis wording already reaches.**
2. **Prove the wording lever is spent, on frames, with the prediction written
   first.** Bark's geometry words *rendered* — flat rectangular planks appeared in
   the **scenery** while the hands went on cupping a scrap. That is a **binding**
   failure, and no further adjective fixes a binding failure.
3. **Test for the band collision** with the three signs in §1. If the bracket is
   one `int(steps × strength)` step wide, raise steps once to confirm the boundary
   does not move — then stop turning knobs.
4. **Build the composite and OPEN IT before any GPU runs.** Expect to reject two
   or three. Re-derive the segmentation for this plate. Measure the pixels your
   compositor changed, not the pixels in your quad.
5. **Write the bar, the failure modes and the decal tells BEFORE the first fire**,
   and score by opening the frame. Tighten a loose bar **forward only** — bending
   bars after the picture is how 8/12 "passes" became 0/12 usable here.
6. **Fire 0.30 first**, one sample, one variable. Then one rung either side only if
   the first tells you which way to go. Assert the mask sha and the init sha every
   fire; check the region diff and one untouched control object every time.
7. **Report the failure as loudly as the pass**, with the numbers that would let
   the next lane disagree with the pictures rather than with the prose.
