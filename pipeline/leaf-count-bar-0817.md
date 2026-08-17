# EXACTLY TWO LEAVES — pre-registered bar and stop rule (2026-08-17)

**This file is committed BEFORE any pixel of the rungs it scores exists.** That is
its whole point. Anything scored against it is scored as written here; the bar is
tightened FORWARD ONLY and never after a picture is seen. Bending bars after the
fact is how 8/12 "passes" became 0/12 usable on this project.

Lane: leaf-count. Owner of this file: the leaf-count lane. Measurement is the
steward's; **shippability is R4 and the founder's alone.**

---

## 1. What is being fixed, and what is already fine

Six plant plates were judged on 2026-08-17 against bars pre-registered before the
pixels (`pipeline/plate-verdicts-0817.md`, long form in each spec's `verdict_0817`,
commit `d61135ac`). The result was a clean asymmetry:

| half of the founder's ruling | result |
|---|---|
| **leaf count = 2** | **failed 4 of 6 plates.** 0 of 16 frames on `ep2-b01-canon-0817`; 2 of 4 on `ep2-b21-scale-0817` |
| **height ("set height… dont double in size suddenly")** | **bound 3 of 4** on `ep2-b21-scale-0817`. Nothing waist-high, nothing tree-sized, nothing doubled |

The founder's ruling, verbatim (2026-08-16): *"lets be a bit more strict with the
sapling. make sure it has 2 leafs and has a set height, height might be a bit hard
for the ai to make exact, so dont go crazy on it, just dont make it double in size
suddenly."*

And on shape, verbatim (2026-08-17): **"the sapling 2 leaves are average leaves"** —
his words. This **supersedes** the steward's earlier round/oval-cotyledon guess,
which both prior bars correctly excluded from scoring as steward inference. Shape is
now settled, ordinary, and scoreable. See `genomes/sapling/THE-SAPLING.md` (canon;
a narrative lane owns that file — read only).

So: **height is largely reachable by wording. Count is the whole problem.** Beats 01
and 21 are plate-blocked on count alone.

## 2. Why count is expected to resist wording — external evidence, not our own comments

Per the standing directive (Oleg, 2026-08-04) research came before the design, and
from outside this repo. Exact instance count is a known, measured, heavily-studied
failure of text-to-image diffusion. Sources and what each actually establishes:

- **"Text-to-Image Diffusion Models Cannot Count, and Prompt Refinement Cannot
  Help"** — Cao, Guo, Huo, Liang, Shi, Song, Zhang, Zhuang, arXiv:2503.06884 (2025).
  <https://arxiv.org/abs/2503.06884>. Introduces T2ICountBench, isolating counting
  from other capabilities with human evaluation. Finding: *all* state-of-the-art
  diffusion models fail to produce the requested number, and **an exploratory study
  on prompt refinement shows such interventions generally do not improve counting
  accuracy.** This paper is the reason the stop rule in §5 allows exactly one more
  wording rung and not a ladder.
- **"Make It Count: Text-to-Image Generation with an Accurate Number of Objects"** —
  Binyamin et al., CVPR 2025. <https://arxiv.org/pdf/2406.10210> /
  <https://ar5iv.labs.arxiv.org/html/2406.10210>. Implemented **on SDXL**, which is
  our stills model. The number that matters: **plain SDXL with a numeral in the
  prompt scores 26–28% counting accuracy** (human and automatic eval, CoCoCount);
  their CountGen reaches 54%. Mechanism: read instance layout out of self-attention
  at t≈500 (layer `l52_up`) + Otsu-thresholded cross-attention masks + DBSCAN
  clustering, then a **ReLayout U-Net trained on ~10K SDXL image pairs** adds or
  removes instances. **It needs training.** Not a $0 path for us.
  Its framing of the field is the useful part: the accepted decomposition is
  **(1) text→layout, then (2) layout→image**. Count is a layout problem, not a
  wording problem.
- Same paper on the alternative: **Bounded Attention** works layout→image but
  *"requires users to manually provide the bounding boxes."* CountGen's stated
  advantage over it is that it invents the layout automatically. **For us that
  supposed weakness is the entire opportunity: we are not generating a random scene,
  we are drawing one designed character whose layout we already know.** We can
  simply provide the layout.
- **"Counting Guidance for High Fidelity Text-to-Image Synthesis"**,
  arXiv:2306.17567 — gradients from a class-agnostic counting network steer the
  predicted noise each step. Needs an extra counting network in the loop; not in our
  stack. Also reports that a **ControlNet-with-pattern-condition baseline counts
  better than plain SD but the images "often do not appear natural."**
- **"Iterative Object Count Optimization for Text-to-image Diffusion Models"**,
  arXiv:2408.11721 — same family, optimisation in the loop, same conclusion that the
  numeral alone does not carry.
- Community/practice on the low-strength init, which is the mechanism we already own:
  <https://stable-diffusion-art.com/denoising-strength/> and
  <https://learn.rundiffusion.com/img2img-docs/> both put **0.2–0.35 denoise as the
  band that preserves layout and identity while allowing a style shift.** That is an
  independent confirmation of the 0.30 our own bark-clipboard fix landed on for
  beats 06 and 10 — the composite's structure survives, the sampler restyles it.
- **`ostris/ip-composition-adapter`** (<https://huggingface.co/ostris/ip-composition-adapter>)
  and the IP-Adapter composition models discussion
  (<https://github.com/Mikubill/sd-webui-controlnet/discussions/2781>): an
  IP-Adapter variant that injects a reference image's **composition** while largely
  ignoring its style and content. Relevant because our box harness already runs
  IP-Adapter with a refs dir at weight 0.15 — image conditioning is wired, so
  raising or re-aiming it costs no download. Recorded as a candidate, not fired here.

**Mechanism selected for the structural rung: give the model the layout instead of
asking for it** — composite a deterministic two-leaf seedling, then restyle it with
a LOW-strength pass (0.30). This is the manual-layout branch the literature says
works, it is our own already-proven bark-clipboard pattern, it needs no training and
no new weights, and it is $0. It is not a new idea invented for this job; it is the
published decomposition (text→layout→image) with the layout step done in PIL.

The **vacancy law** already established here applies and is consistent with the
above: an empty region is a hole the model fills with the largest noun and the
negative does not reach it. `no third leaf` cannot fix a count. Nothing ships on it.

## 3. The bar — score exactly this

Every rung renders to `832x1216` and is judged on **every frame it produced, at full
resolution**, with the frame count stated as `X of N`. Never impressions.

### AXIS A — COUNT (the axis under test)

Per frame: count distinct leaf blades **on the sapling**. `PASS-COUNT` iff the count
is exactly **2**.

Counting rules, fixed now because the prior pass showed exactly where the ambiguity
lives (beat 21 scored "THREE (two opposite plus one drooping lower leaf)"):

- A leaf blade = any distinct expanded green lamina attached to the plant. This
  **includes** an apical/terminal leaf, a drooping lower leaf, and any partly
  occluded blade whose outline is identifiable as a separate blade.
- Cotyledons count as leaves.
- Grass blades and background foliage are **not** counted. Neither is a bare stem or
  side-branch carrying no blade.
- **An illegible plant scores `FAIL-COUNT-ILLEGIBLE` and counts as a failure, not as
  an excluded frame.** Beat 01 rows r2/r3 collapsed into a giant purple mass with a
  seedling in front; a frame where the plant cannot be read is not a frame that
  passed, and must never be quietly dropped from the denominator.

### AXIS A RATE — the looseness both prior bars flagged, closed here

Both `verdict_0817` blocks recorded the same defect: *"this bar names attributes per
FRAME but never a RATE over the batch, so 'does the sample pass' was not actually
defined"*, and both instructed the next rung to state one. It is stated now, before
the pixels:

- **BOUND** — ≥ **7 of 8** frames (87.5%) score exactly two.
- **PARTIAL** — ≥ 1/2 but < 7/8.
- **NOT BOUND** — < 1/2.

`N` must be ≥ 4 and is fixed by the spec before firing. The 87.5% floor is not
arbitrary: on beats 01 and 21 the sapling **is the shot**, and beat 21's own verdict
ruled that *"a plate that returns three leaves half the time is not a plate for a
beat where the plant is the entire shot."* A plate carried forward must hold on
essentially every frame, because motion consumes the plate rather than re-picking it.

### AXIS B — HEIGHT (the half that already works; must not be broken)

Carried forward **UNCHANGED** from `ep2-b21-scale-0817`, on that verdict's own
instruction that *"the height clause should be carried forward UNCHANGED, since it is
the one thing here that demonstrably works."* Same words, same test, so the numbers
are comparable:

> plant top at or below the surrounding grass line, with the grass silhouetted
> against the sky above the plant — `no taller than the grass around it`

plus the three failure modes the founder named himself: **nothing waist-high,
nothing tree-sized, nothing suddenly doubled in size.**

Reported as `X of N`. **Baseline to beat or hold: 3 of 4 (75%).** If count improves
while height falls below 75%, that is reported as a **REGRESSION** in the same
breath as the count result and not buried. The point of scoring both is that a count
fix must not silently break the half that already binds.

### AXIS C — SHAPE (newly scoreable, founder-settled, tightened FORWARD)

`PASS-SHAPE` = ordinary, average leaf blades — an everyday simple leaf shape.
`FAIL-SHAPE` = round/oval cotyledon buttons, or fig-lobed / palmate / compound
leaves.

This is a **forward-only tightening** and it is declared here before any pixel.
Both prior bars explicitly refused to score shape because round/oval was the
steward's inference and `THE-SAPLING.md` 2.2 flagged it vetoable in one line. The
founder vetoed it on 2026-08-17 in one line, exactly as anticipated. Shape is now
his, settled, and ordinary. Reported as `X of N`, and it is a reported axis — a
shape miss alone does not fail a rung whose question is count.

### NOT SCORED (named now so it cannot be reached for later)

- **Leaf tilt / any motion** — a still cannot show motion; that is the motion job's bar.
- **Fruit colour** where the draft asks for no fig. Where a fig *is* asked for, purple
  is canon-wide and retroactive, and colour already binds (it held on every legible
  b01 frame and on the passing b18 plate).
- **Treeline and thin bare side-branch** — beat 21's bar listed these as PASS clauses
  and then found 0 of 4 frames had either, forcing it to report two readings because
  the bar did not say which it meant. **Resolved FORWARD: they are scene-dressing,
  NOT pass requirements.** They will not be used to fail or to pass anything.
- **Shippability, look, framing, composition** — R4 and the founder's. Named as
  founder cards, never settled here.

### Backend discipline

**Every rung in this lane renders on ONE backend — the rtx5090 box, bf16/CUDA.**
bf16/CUDA renders red where fp16/MPS, fp32/MPS and bf16/MPS render purple off the
identical seed (MAE 60–61). Comparing across machines measures the machine, not the
wording. If any rung is ever run on a Mac, `python3 pipeline/mac_preflight.py` runs
first (two Macs have rendered SDXL as pure noise on weights that passed every size
and manifest check) and the cross-backend caveat is stamped on the verdict.

Token budget: CLIP 77, enforced by `plate_scratch.py`. Any token trade is recorded
and the traded words are named as first suspects. **The style tail is not cut** — it
confounds comparisons.

## 4. Rungs, in order, one sample each

**ONE SAMPLE BEFORE ANY BATCH** (founder, 2026-08-03), one per *recipe change*. A
metric agreeing with the steward is not a sample. A real `--dry` runs before every
fire.

- **Rung 1 — WORDING, and it is the LAST wording rung.** One sample. Spends the one
  remaining wording attempt on the best-informed phrasing rather than climbing a
  ladder of near-identical guesses. Height clause carried forward verbatim.
- **Rung 2 — STRUCTURAL: layout given, not asked for.** Composite a deterministic
  two-leaf seedling, restyle at LOW strength (0.30). Fires only if rung 1 does not
  reach BOUND, and is filed as its own distinctly-named spec.

## 5. STOP RULE — pre-registered, and honoured

Beat 17 burned 8 seeds at 0 brushes by firing rungs until something looked
acceptable. This lane does not do that.

1. **Wording gets exactly one more sample — rung 1 — and then it is done.** The
   budget is spent on evidence, not repetition: arXiv:2503.06884 says prompt
   refinement does not improve counting; Make It Count measures plain SDXL numerals
   at 26–28%; and this repo has already spent 3 distinct drafts and 20 frames on it
   (`canon`, `scale`, `figleafcanon`) for 2 successes out of 20.
2. **If rung 1 does not reach BOUND (≥7/8), wording is declared INSUFFICIENT and no
   further wording rung is fired.** No reseeding a wording nobody has watched — four
   wording levers died that way on 2026-08-16. No rung 1b, no "one more phrasing".
3. The next instrument is then the one **already named** in §2 and §4 — composite
   then low-strength inpaint — filed as a spec, not improvised at the console.
4. **Hard ceiling for this lane: 2 fires (1 wording + 1 structural).** If the
   structural rung also misses the bar, the verdict is *"exactly-two is not reachable
   at $0 in this harness"* and the third instrument is **named and not fired**:
   ControlNet SDXL (canny/scribble) or T2I-Adapter sketch conditioned on a drawn
   two-leaf outline, which needs a weight download and is a founder/steward call, not
   a thing to start blind at the end of a lane.
5. **A rung that misses is reported as a miss with its rate.** `X of N` on the
   axes above. No rung is re-read looking for a kinder denominator, and nothing is
   filed off a failing plate — a beat whose plant is wrong cannot be rescued by
   motion, which is beat 16's expensive lesson, where the wrong plant *was* the shot.

## 6. Provenance

Bar authored by the leaf-count lane, 2026-08-17, before any rung existed. External
sources are listed in §2 with URLs and are outside this repo. $0 throughout: local
card, no provider, no spend. Scores land in each rung spec's own verdict block and a
one-line-per-rung index lands here.

## 7. Results index (appended only after a rung is judged)

- **Rung 2 — STRUCTURAL, `ep2-b01-leafcomp-inpaint-0817` (fired 2026-08-17, box, bf16/CUDA,
  $0): COUNT BOUND, 4 of 4 exactly two blades (rate 100% ≥ 7/8).** Height held with no
  regression — apex y 625 in the init vs 625/632/626/627 out, |Δ| ≤ 7px, nothing doubled;
  baseline was 3 of 4, it holds 4 of 4. Shape reported: broad ovate left blade, narrower
  curved right blade, closer to "average" than the init's lance quartet. No mask seam and no
  decal tell at 4x — it reads drawn. Mechanism: the composite fixes the count in the pixels
  and the 0.30 pass keeps it, so cardinality is out of the sampler's hands. Rung 1 (wording)
  was never fired and is now moot; the lane's second fire is unspent. Full score in that
  spec's `verdict_0817`. Remaining calls are the founder's: whether these are his "average
  leaves", and shippability of an off-canon mechanism plate.
