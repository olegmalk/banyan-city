# COMPOSITE-THEN-INPAINT — the house pattern for an attribute the sampler cannot hit

**2026-08-17. Written by the bark lane (beats 06/10) at the lead's request, BEFORE
the sapling compositor's first pixel exists.** §1–§7 are the pattern, generalised
off a result that already passed. §8 is the pre-registration for the sapling init:
what it must guarantee and how it will be checked, committed before it can be
bent to fit a picture. Bending a bar after the picture is how 8/12 "passes"
became 0/12 usable here.

**The rule, in one line: if an attribute has no continuous encoding in the
conditioning, no sampler knob will reach it — put it in the pixels with plain
image processing, then denoise at 0.30 so the sampler only finishes what is
already there.**

---

## 1. The diagnostic — which axis is this?

Before reaching for a composite, split the ask by axis and ask what CLIP does
with each:

| Axis | Encoding | Reachable by wording? |
|---|---|---|
| Material ("bark, not navy plastic") | continuous, densely trained | **YES** — deleting the noun `clipboard` took chrome+paper from 24/24 present to 0/24 |
| Height / scale ("set height, don't double") | continuous adjective | **YES** — bound 3 of 4 plates |
| Geometry ("large flat rectangular board") | weakly bound to the verb | **NO** — the words rendered, into the *scenery*: flat rectangular planks appeared at the frame edge while the hands went on cupping a scrap. A BINDING failure, not a vocabulary one |
| Cardinality ("exactly two leaves") | **none** — numeral embeddings are near-identical | **NO** — 0 of 16 frames with the strongest available wording |

Two failures that look alike and are not: bark's geometry *rendered but did not
bind*; the leaf count *never reached the conditioning at all*. Both end at the
same place — the pixels — but only the second is settled by published work
(arXiv:2503.06884 tests prompt refinement directly and rejects it;
arXiv:2406.10210 measures plain SDXL numerals at 26–28%, ceiling ~59% with a
trained ReLayout U-Net and a detector in the loop). The count case is therefore
*stronger* than bark's was: with a composited init the count is not a sample from
the model at all. **Two leaves drawn in are two leaves.**

## 2. Bark's collision, and why every knob failed

Eleven single samples on beat 10 ruled out strength (at 40 and 80 steps), step
count, a second repair pass, the seed, and value-matched material wording. The
mechanism they agreed on:

> **Bark crust is high-frequency relief. The board's straight silhouette is
> carried in the SAME frequency band.** So every noise level high enough to make
> the model *write* crust is high enough to rewrite the outline, and every level
> low enough to keep the outline leaves the init's smooth face untouched. The two
> thresholds coincide in sigma instead of being separated by a gap.

That argument only holds *while the model is asked to invent the relief*. Put the
relief in the init and the thresholds separate — measured, on two beats: material
present and shape intact at 0.30, shape gone by 0.45. On beat 06 they did not
merely separate, they **crossed** (shape ceiling 0.638 with a bare init sat below
a material floor that was never reached at any strength).

**The generalisation: look for the axis your target shares a band with.** If the
thing you want and the thing you must not lose live in one band, no knob
separates them, and the only move left is to stop asking the model to invent.

## 3. Why 0.30, stated mechanically

An img2img/inpaint pass runs only `int(steps × strength)` of its denoising
schedule. At 40 steps, strength 0.30 runs **12** steps and starts from a latent
that still carries the init's structure; the early high-sigma steps where global
layout is decided never run. That is the whole reason "finish this structure"
succeeds where "invent this structure" fails, and it is why the band 0.2–0.35 is
the one community practice names for preserving layout and identity
(stable-diffusion-art.com/denoising-strength, learn.rundiffusion.com).

Corollary worth knowing: arXiv:2505.04831 incrementally inpaints under a reward
and uses **object count** as its proof of concept. Beats 06 and 10 did that loop
by hand, one sample at a time.

## 4. The three choices that stopped bark reading as a decal

A composite can fail in a way no prompted render can: it can look *pasted*. Each
of these was made on evidence from the plate, and they are the house checklist.

1. **PROCEDURAL, NOT A PHOTOGRAPH.** A photo imports a licence and a provenance
   question into a repo whose rule is provenance always, and photoreal detail
   dropped into a cel-shaded frame *is* the decal failure mode by construction.
2. **FITTED TO THE OBJECT, NOT TO THE MASK.** The mask quad was not the board —
   it overshot into a hand and the coat. Filling the quad would have painted bark
   over fingers. The board was segmented, and the texture mapped onto a
   homography fitted to *that* silhouette, so the texture edge and the object
   edge are the same edge. This is the strongest single defence against decal.
3. **THE PLATE'S OWN LIGHT IS KEPT.** Light direction is *measured* from the
   low-pass luminance gradient of the plate's own object, carried into object
   space through the homography Jacobian; the plate's low-frequency shading field
   is then re-applied multiplicatively. A flat sticker has none of that, which is
   what makes it read as one.

Plus: inset the drawing 2px and paint the surviving rim as a dark cel outline, so
the new content keeps a drawn edge in the plate's own dialect instead of a
texture running off a cliff.

**The five decal tells, committed before the render and checked after:** texture
axes not following the object's tilt; a pattern ignoring the frame's light; a
swatch stopping short of, or overrunning, the object's own edge; visible tiling or
a repeat; detail at the wrong scale read against a hand or other in-frame ruler.

## 5. What failed before it worked — the half that saves the next lane

**Rejected composites, all caught BY EYE before any GPU ran** (this is the point
of doing it with image processing — a rejection costs seconds):

- b10 v1: 4 octaves at gx=20 read as **scratched burlap**, and the raw
  segmentation left notches and a staircase — a FAIL-SHAPE introduced by the
  compositor itself. Fix: fewer, wider plates; convex hull for straight edges.
- b10 v2: subtracting `bright` **re-cut the chrome clip open**; `fill_holes`
  cannot close a hole that touches the border. Fix: union the filled segment back
  in *after* the exclusion.
- b06 v1: beat 10's `hull & ~excl` verbatim stopped the bark **~12px inside the
  board's own left edge** and chamfered a corner — decal tell #3, drawn by the
  compositor. Fix: the quad *is* the board here, so the quad is the base.
- b06 v2: beat 10's noise grid on a 190×215px board read as **corduroy**. Fix:
  `--noise-scale 0.62`. Grain scale is per-object, not per-recipe.
- b06 v3: the board's right half is warmer, so 60px of face under the clip went
  unseen and **half the chrome clip stood**. Fix: relax B-R, discriminate on B-G.

**And the colour rule transferred ZERO times across four boards** — navy needed
`B-R ≥ 10`, near-black needed `B-R ≥ -2`, maroon inverted it, warm brown needed
`R-G` instead. Assume you will re-derive the segmentation for every plate.

**Sampler-side failures at the rung above:** 0.45 split beat 10's slab in two
where the model read the deepest composited fissure as an **object boundary** —
in this dialect a strong dark line *is* an edge — and chewed beat 06's top edge
into a crest. **Design rule out of that: never composite an internal line
stronger than the object's own outline.**

## 6. Two laws that bite compositors specifically

- **THE VACANCY LAW.** An emptied region is a hole the model fills with the
  largest available noun, and **the negative does not reach it**. Never leave an
  unpainted gap you have not given positive content.
- **THE HAND LAW.** If a figure is in frame, every hand must be specified —
  including ones you do not care about.

## 7. Is there a band collision for leaves? Yes, and it is not the count

Cardinality is not a frequency phenomenon, so there is no crust/silhouette
analogue for the *count itself*. But the thing that destroys a composited count at
the rung above is exactly bark's failure, one level over:

> **Two adjacent blades are separated by a thin, high-frequency negative space.
> Leaf interior texture and that gap live in the same band.** Any strength high
> enough to redraw blade interiors can close the gap (two blades merge → 1) or
> resolve a strong midrib as an object boundary and split one blade (→ 3).

This is why the published methods' own papers warn they fail when instances are
**identical, adjacent and overlapping** — which is precisely two leaves on one
stem. It converts into two hard design rules for the compositor, both testable
before any GPU runs: **the gap between the blades must be wide and unambiguous**,
and **the midrib must be drawn weaker than the blade outline** (bark's split
lesson, transferred).

---

## 8. PRE-REGISTRATION — `pipeline/sapling_init_composite.py`

**Scope, so lanes do not collide.** I own **the pixels that go in**: the
compositor and one sample of its output. I do **not** own the inpaint rungs or
their scoring (`pipeline/leaf-count-bar-0817.md`, that lane's rung 2), and I do
not touch the ControlNet scribble hint (`pipeline/author_scribble.py`) — that is a
*control image*; this is *the init the sampler refines*. A peer's
`pipeline/leaf_count_composite.py` (`07840029`) is the **subtractive** first cut:
it patches named extra leaves out with shifted background. This tool is the
**additive** one, for a reason measured on the plate below.

**Why subtraction alone cannot serve this bar.** On
`farm-out/ep2-b01-brightbase-figmatte/01-cold-open-bright-i35b-s0.png` the sprout
has four **narrow lance-shaped** blades. Canon §2.2 rules lance shapes OUT ("no
lance shapes… out: a leaf drawn as a feature"), and the founder's 2026-08-17
ruling is **average leaves**. Removing two of four leaves therefore yields two
*wrong-shaped* leaves: it can pass count and still miss the shape axis the same
document settles. Count and shape have to be authored together, so the blades are
**drawn**, not merely reduced.

### What the composite must GUARANTEE

- **G1 COUNT.** Exactly two leaf blades on the sapling, by construction.
- **G2 SHAPE.** Ordinary blades — a simple oval-ovate blade with a soft tip and a
  short petiole. Not round buttons, not lance, not lobed/palmate/compound.
- **G3 HEIGHT IS INHERITED, NOT AUTHORED.** The plate's own apex is the target.
  Height is the half that already binds at 3 of 4 and the composite must not be
  the thing that breaks it, so the tool measures the plate's plant apex and base
  and refuses to move them beyond tolerance. The founder's named failure is
  *sudden doubling*, so the check is a ratio, not a centimetre count.
- **G4 NO VACANCY.** Every pixel of every erased blade is refilled with content
  synthesised from the plate's own surrounding ring — never left empty, and never
  a shifted clone of a nearby feature (that is decal tell #4, a visible repeat).
- **G5 NOTHING ELSE MOVES.** Outside the erase ∪ draw region, the plate is the
  founder's own bytes: maxdiff 0.

### How it will be CHECKED — mechanically, printed, and nonzero-exit on failure

Numbers fixed now, against an 832×1216 plate. A metric is a filter, never a
verdict: **every run is also opened by eye at 1x and 3x**, and a metric agreeing
with me is not a sample.

| # | Check | Threshold |
|---|---|---|
| C1 | blade components in the drawn structure, after an opening that removes the stem | **exactly 2**, each ≥ 400px |
| C2 | minimum gap between the two blade components, and that the gap pixels are not blade | **≥ 10px** |
| C3 | apex y of the composited plant vs the plate's measured apex | **\|Δ\| ≤ 12px** (~1% of frame height) |
| C4 | plant height ratio out/in | **0.90–1.10** (the anti-doubling check) |
| C5 | blade aspect, length:width | **1.6–2.6** (below 1.4 is a round button; above 3.0 is the lance this plate already has) |
| C6 | residual structure inside the erase region after refill: largest component standing out from the local low-pass field | **< 400px**, i.e. below the smallest thing that could read as a blade |
| C7 | maxdiff outside the dilated erase ∪ draw region | **0** |
| C8 | determinism: same args → same sha256, printed by the tool | byte-identical on a re-run |

### Named failure modes — any one is a FAIL, reported as loudly as a pass

`FAIL-COUNT` C1 ≠ 2. `FAIL-MERGE` C2 under threshold — the two blades touch or
share an ambiguous gap, the state the rung above turns into one leaf.
`FAIL-HEIGHT` C3 or C4 out of band. `FAIL-SHAPE` C5 out of band, or the blade
reads as a button/lance/lobe by eye. `FAIL-VACANCY` C6 — a lance tip or a smear
survived the refill, or the refill repeats a recognisable feature.
`FAIL-DECAL` any of the five tells in §4. `FAIL-SEAM` a visible paste box.

### Method

ONE SAMPLE BEFORE ANY BATCH, one per recipe change, opened before the next is
authored. $0, local, no GPU, no network, no model. If a bar here turns out to be
loose, it is said out loud and tightened **forward only** — never retroactively,
and never on the sample it would have failed.
