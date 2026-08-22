# Beat 13, THE SHADE — the plate stands up when you ask it to stand up

2026-08-16 · job `pipeline/jobs/motion-poscontrol-r2-0816.yaml` · commits
`2bc8b941` (filed) → `77cc8277` (result) · four renders, one job, one seed · $0.

**This report was written by a SECOND lane.** The lane that ran the experiment
pushed `1dfbfdb3`, `727de28b` and `77cc8277` and then died with its transcript
gone. The commits survived; the explanation did not. Everything below was
re-verified from the artifacts — the clips were pulled from
`origin/farm-results-rtx5090`, the frames were opened, the numbers were
re-computed locally, and two of the dead lane's claims are corrected here. This
is the second time a lane has died holding a result (the bark-board verdict was
the first, and it was re-judged from scratch). Hence this file.

---

## 1. THE HEADLINE, AND IT SURVIVES VERIFICATION

Beat 13's plate is not frozen and never was. Handed a **different action clause**
against a **byte-identical control**, the same plate, the same seed, the same
negative and the same recipe, **the boy stands up and walks forward.**

What does **not** survive verification is the *reason*. The commit subject says
the problem is that `"rock slowly forward and back"` is "the wrong SIZE of
request". That is one of **at least three** readings of a single sample, and the
other two are not ruled out. §5.

---

## 2. THE CLAUSE CHANGE, VERBATIM AND BYTE-DIFFED

Both prompts are published at
`origin/farm-results-rtx5090:farm-out/motion-poscontrol-r2-0816/prompt-a{0,3}.txt`.
Byte-level diff of the two files:

```
COMMON PREFIX  (50 bytes, byte-identical)
    sitting on grass, knees up, arms around knees. He

A0 (control)   (29 bytes)
    rocks slowly forward and back

A3 (variable)  (98 bytes)
    puts his hands on the grass, pushes himself up onto his feet, stands up
    straight and steps forward

COMMON SUFFIX  (171 bytes, byte-identical)
    . 2D anime, hand-drawn cel animation, flat cel shading, clean ink linework,
    anime key art, cinematic lighting, detailed, newest, masterpiece, best
    quality, very aesthetic.
```

Subject clause and style tail are byte-identical. **Only the action clause
differs.** Measured on the real Gemma tokenizer on the box before filing: a0 58
tokens, a3 73, negative 38, limit 1024.

### The one-variable chain, each link checked

| Link | Evidence | Verified |
|---|---|---|
| Same plate | both jobs-render jsons point at `poscontrol-init-b13-704x1280.png`, asserted sha `1745a491db3c…` | yes, in the job yaml |
| Same seed | `20260815` in both jobs-render jsons | yes |
| Same negative | `negative_prompt_embeds` = `d9315dc3a259` on **all four** arms | yes, `embeds-verify.txt` |
| Four distinct prompts | `prompt_embeds` a0 `87b76c09cc5d` / a1 `70eb2b246a2a` / a2 `7dbb499788d9` / a3 `3793fca1786e` | yes, all distinct |
| Same recipe | **the a0 and a3 argv are 30 entries each and differ in exactly 4** | yes, diffed |

The four differing argv entries are `--jobs …a0.json`→`a3.json`, `--task …-a0`→
`-a3`, `--bench-jsonl …bench-a0.jsonl`→`a3.jsonl`, `--bench-label …-a0`→`-a3`.
**No recipe flag differs at all** — same `--size 704x1280 --frames 97 --fps 24
--guidance 2.0 --distilled-sigmas --two-stage --image-crf 33 --offload
sequential --mode production`.

Note for anyone re-checking: **the argv does not carry the prompt.** The prompt
enters as a pre-encoded `embeds-a{0,3}.pt` named in the jobs json, which is why
`embeds-verify.txt` is the load-bearing artifact and not the argv.

---

## 3. THE CONTROL — SIX, NOT SEVEN, AND NOT "ACROSS FIVE NIGHTS"

A0 came back sha
`42043851da4b246cfcd4e858cda828da992d0d48f15ef10d81d3a99c1ceb445a`, so every
number here is directly comparable to everything the b13 investigation has
published.

**Two corrections to the record.** The count is **six**, not seven, and every one
of the six landed inside **seventeen hours on one box**, not across five nights.
Enumerated by grepping every published `.sha256` manifest on all six farm
results branches — these are all of them:

| # | job | published name | DONE at |
|---|---|---|---|
| 1 | `ep2-b13-shade-cycle-s2-0815` | `13-the-shade-LTX-cycle-s2.mp4` | 2026-08-15 19:55 |
| 2 | `ep2-b13-stg-0815` | `13-the-shade-STG-OFF-control.mp4` | 2026-08-15 23:26 |
| 3 | `ep2-b13-guidance-0815` | `13-the-shade-CFG-2p0-control.mp4` | 2026-08-15 23:50 |
| 4 | `ep2-b13-blurplate-0815` | `13-the-shade-PLATE-clean-control.mp4` | 2026-08-16 00:00 |
| 5 | `ep2-b13-negcfg-0816` | `13-the-shade-NEG-full-cfg2p0-control.mp4` | 2026-08-16 01:02 |
| 6 | `motion-poscontrol-r2-0816` | `poscontrol-a0-b13-control.mp4` | 2026-08-16 12:47 |

Six byte-identical renders is still a strong determinism result and the
comparability claim stands. But "across five nights" (in `77cc8277`, in
`727de28b`'s docstring, and as "five times across four nights" in the job yaml)
is **inflated**: it is one evening and the following morning, same machine, same
driver, same weights. Nothing here shows the recipe is byte-reproducible across
a reboot, a driver bump or a second box. Do not quote it as if it did.

---

## 4. BOTH ARMS — MEASURED, AND THEN OPENED

### How body motion was established, and what the method cannot see

**Method.** `pipeline/body_motion.py`: both frames decoded to grayscale at 1/4,
high-pass filtered, block-matched (48px blocks, ±128px search) and summarised as
the **median** block displacement, read across a **ladder** of pairs against f0.
A ladder rather than one pair because gait is cyclic — a runner four seconds in
can be back near her starting pose, and a single f0→f96 reading would call that
clip still.

**What it cannot see, stated before the numbers:**

- It **cannot tell a camera move from a body move.** A dolly and a walk both
  translate content.
- It **has a floor on this material.** On the provably-frozen a0 control the
  median reads **12–19px**, driven by a global 12–16px vertical drift of the
  whole picture. Anything under ~20px here means "did not move".
- It **saturates.** a3's f0→f48 reports 14.7% of blocks on the ±128px boundary,
  so large displacements are a floor, not a value.
- **p90 / max / moved_frac / articulation are retired** — §6.
- **It is a filter, never a verdict.** Which is why §4.2 exists.

**Re-computed locally on my machine from the published mp4s; every figure below
reproduces the dead lane's table exactly.**

| pair | A0 "rocks slowly forward and back" | A3 "…pushes himself up… stands up straight and steps forward" |
|---|---|---|
| f0→f4 | 16.00 | **0.00** |
| f0→f24 | 16.49 | **4.00** |
| f0→f48 | 12.00 | **106.73** |
| f0→f72 | 5.66 | **105.60** |
| f0→f96 | 18.94 | **104.69** |

A0 wanders between 5.66 and 18.94 with no direction — inside the noise floor.
A3 is flat at zero for a fifth of a second, then climbs to >100px and stays
there. Terminal freeze scored separately and clean in both: last pair with a new
pixel 96 of 96, zero bit-identical pairs, no soft tail.

### 4.2 What I saw when I opened the frames

Both sheets built at f0/8/16/…/96 from the published mp4s and read by eye.

**A0 — the control. It does not move.** At every one of the thirteen sampled
frames the boy is in the identical folded pose: knees drawn up, both arms wrapped
around the shins, hands clasped low in front, head slightly bowed, the same
frown, the same two shoes flat on the grass, the same twig to his right. Nothing
rocks — there is no forward lean at any frame and no backward one. What changes
is the drawing being re-inked: grass hatching reshuffles, the shadow under his
knees breathes, the whole picture drifts a dozen pixels vertically. This is the
third cold read to say the same thing and it agrees with the two before it.

**A3 — the variable. It performs the whole action.**

- **f0–f24** — identical to A0's folded pose. He genuinely holds still for the
  first quarter of the clip.
- **f32** — the first movement: knees splay outward, the clasped hands come apart
  and drop toward the grass, weight shifts forward.
- **f40** — hands planted flat on the grass either side of him, hips lifting off
  the ground, head dropping.
- **f48** — a deep crouch on all fours, arms straight, head down.
- **f56–f64** — folded at the waist with hands near the ground and legs
  straightening — the middle of a rise from a bow.
- **f72** — nearly upright, head still tipped forward, arms hanging.
- **f80** — **fully standing**, arms at his sides — and **his head is out of the
  top of the frame.** Only shoulders-down is visible.
- **f88, f96** — standing and stepping forward, head still out of frame, and at
  f96 the near leg is clearly mid-stride.

**It is animation, not a cut.** I pulled frames 40–52 *consecutively*: the head
tips down and the hips rise a few pixels per frame, eased, with no discontinuity
anywhere. There is no jump cut and no scene change.

**A2 (photoreal runner) and A1 (waterfall)** were the arms testing the question
`86d50df6` had already closed. A2 I opened as well: a full running gait, legs
alternating through the stride, ponytail swinging, surf rolling, camera tracking
— median displacement 80–117px at *every* pair including f0→f4. It moves.
**But A1 and A2 are photoreal live-action prompts on photographic plates.** They
establish "this engine moves things", not "this engine moves a cel-anime figure",
and after `86d50df6` neither was needed. **A3 is the only load-bearing arm** in
this job, because it is the only one on our own plate in our own dialect.

---

## 5. DOES IT GENERALISE? NO. IT IS A BEAT-13 OBSERVATION.

**Ruling: "the action is too small a request" is a ONE-SAMPLE HYPOTHESIS about
beat 13, not a general rule, and the sample does not isolate size.**

### 5.1 What is actually established

**Established, hard:** on beat 13's plate, at the production recipe, seed
20260815, `"He puts his hands on the grass, pushes himself up onto his feet,
stands up straight and steps forward"` produces a complete seated-to-standing
stand-up, and `"He rocks slowly forward and back"` produces nothing. One sample
per arm.

**Established, twice over:** a seated cel-anime figure on this checkpoint can be
made to STAND UP. Beat 17 did it in 12 of 12 cells (`86d50df6`), beat 13 did it
in 1 of 1 here. That is a real, robust finding.

**NOT established:** that the discriminating variable is the *size* of the
action.

### 5.2 The three confounds in this one sample

A0 and A3 differ in exactly one clause — but that clause differs along **three
axes at once**, and the experiment cannot separate them:

1. **SIZE.** Rocking is a small displacement; standing is a large one. This is
   the reading the commit takes.
2. **KIND — cyclic vs monotonic.** "Rocks slowly forward and back" is
   **cyclical and returns to its start pose**. "Stands up and steps forward" is
   **monotonic and displacing**. An i2v model conditioned on a single init frame
   has every reason to collapse a return-to-start request onto the init — and
   our ladder metric is, by its own docstring, weakest exactly on cyclic motion.
   This reading fits the data as well as the size reading does.
3. **DECOMPOSITION.** A0 is one verb. A3 is a **chain of four sub-movements**
   (hands on the grass → push up → stand straight → step forward), and 98 bytes
   against 29. A neighbouring lane is already chasing whether a sub-movement
   chain buys duration (`f4dd75d8`). A3 has one; A0 does not.

Any of the three explains the result. **Nothing in this job distinguishes them.**

### 5.3 And beat 17 does not break the tie

Beat 17's twelve cells and beat 13's one arm are **different beats, different
plates, different characters, different framing — and the same action.** Both
asked for a stand-up and both got one. So what has now been shown twice is
narrow and specific: **"stand up" works.** No arm anywhere has held plate, seed
and recipe fixed and varied only the *size* of the action. Agreement between the
two is suggestive of "big gravity actions are reachable"; it is not evidence
about small ones, because **no small action has ever been tested on a plate known
to respond.** Beat 13's plate is now known to respond — which is what makes the
test in §8 cheap.

### 5.4 The part that IS general, and it is the expensive part

**The composition finding generalises further than the wording one**, because it
is a measurement of pictures rather than an inference from one render.

Independently verified here with a *different* mask than the dead lane's (green-
skin for the goblin, warm-skin for the boy), largest-blob, top row, **mask
overlaid back onto the plate and opened**:

| plate | head-top row | % of 1280 | headroom above the figure |
|---|---|---|---|
| `b17-init-704x1280.png` | **510** (lane measured 508) | 39.8% | 40% of the frame is empty sky |
| `poscontrol-init-b13-704x1280.png` | **131** (lane measured 132) | 10.2% | 10% |

Two independent measurements agreeing within 2px. b17's 508 is also exactly twice
`86d50df6`'s 254, which was measured at half resolution — a third agreement.

**And the consequence is the one that matters for production: A3's stand-up is
unusable as shot.** The action succeeded and the frame could not hold it — his
head leaves the top of the picture at f80 and is still gone at f96. Beat 13 as
currently plated cannot contain the action its plate is willing to perform.

**FALSIFICATION NOTE, because this measurement nearly went wrong.** My first
head-tracker used a warm-skin mask and reported b17's head-top at row 663 — a
disagreement of 155px with the lane. It was wrong: the goblin's skin is *green*,
and the mask had latched onto a small pink patch at his collar. **The overlay
caught it in one look.** Had I trusted the number I would have "refuted" a
correct finding. This is the same failure the beat-17 lane caught with the same
technique (sky speckle setting the head-top row, silently scoring three complete
stand-ups as "no movement"). **Overlay the mask, every time.**

---

## 6. THE DISPLACEMENT METRIC: WHAT IS RETIRED, AND WHAT TO USE

`727de28b` validated `body_motion.py` against two clips whose answer was known by
opening frames, and **half of what it printed failed.** That retirement lived
only in a docstring and in stdout prose. It is now structural:

**USE:** `median_disp_px` from `pipeline/body_motion.py`, read across a **LADDER**
of pairs (f0→f4, f24, f48, f72, f96). It is the only column validated against
both a clip known to move and a clip known to hold. **It has a floor of ~20px on
cel line art** — see §4.

**RETIRED — DO NOT QUOTE:**

- **`p90_disp_px`, `max_disp_px`, `moved_frac_*`, `articulation_*`.** They read
  p90 110px and 85% of blocks "moved" **on the b13 control**, a clip whose figure
  provably does not move. `max` sits at 181.02px on almost everything, which is
  exactly the diagonal of the ±128px search box — those blocks **railed to the
  corner**. Cel art is full of near-identical strokes and flat fields, so an
  ambiguous block finds a confident-looking match anywhere. (`articulation_max_px`
  reads 192.42 on a3 — *past* the diagonal, which is the same pathology.) The
  median survives because most blocks are background and the railing ones are a
  tail.
- **`depth`** as an action signal — **INVERTED**. Observed range: 0.038 b13
  control (frozen) < **0.293 b17-full-s1 (a complete stand-up)** < 0.516
  b06-d1neg (zero human motion). In this job a3, a full stand-up, reads **0.031**
  and the frozen a0 reads **0.038** — the acting clip scores *lower* than the dead
  one on the same plate and seed.
- **`distinct_pictures` / `effective_fps`** as an action signal. a3, a complete
  stand-up, reads **48.0 distinct pictures** — the exact number guidance-1.0 and
  the 9px blurred plate reached with no body motion at all. a2's full running
  gait reads **12.0**, the worst of anything measured. b17's stand-up reads 24.0
  against the frozen control's 32.0. **Six lanes spent a week driving that number
  up.**
- **`cadence`** (the pre-`hold_period` metric) — structurally blind, odd hold
  periods alias to exactly 1.00x.
- **Chained-NCC camera scale** — same railing pathology. Align frames.

### What changed in code so this cannot be quoted again by accident

1. **`pipeline/body_motion.py` — the retired columns are now NESTED** in the
   result dict and in the `--json` output under the key
   `UNRELIABLE_ON_LINE_ART_DO_NOT_QUOTE`, with a `why` string inside it. The
   previous retirement was prose only; a lane loading `measurements.json` got
   `p90_disp_px` at top level with no warning attached. Now the access path
   itself shouts. `median_disp_px` gained a sibling `VALIDATED_METRIC` key.
2. **`pipeline/body_motion.py` — a `RETIRED_METRICS` block is now the FIRST
   section of the module docstring**, before "why this exists", listing every
   retired metric in the tree, not just this module's own.
3. **`pipeline/judge_clip.py` — the most dangerous surviving line is gone.** It
   printed, on every clip, every run:
   `DEPTH 0.031 (b13 0.029 hold | b06-DONE 0.215 | b02-FIXED 0.397)` — a
   reference scale that reads as a ladder where **higher is better**, which is
   precisely the inversion. It now prints the retirement and the three
   counterexamples in the inverted order instead. The `HOLD` line likewise now
   says in place that distinct-pictures is not an action signal, and points at
   `body_motion.py`.
4. **A retirement banner was added to
   `pipeline/loop/measurements-poscontrol-0816.txt`** — the artifact most likely
   to be quoted, whose tables print retired columns with no warning on them.
5. A cosmetic bug in the retirement text itself (`85%%` printing literally in a
   non-format string) is fixed.

`body_motion.py --selftest` exit 0 after all of it; the selftest's legitimate
internal reads of the retired columns go through a single named accessor,
`retired()`, so `grep -rn 'retired('` finds every remaining use in the tree.

---

## 7. BEAT 08 — SEE `1dfbfdb3` AND §7 OF THIS FILE'S COMPANION

`1dfbfdb3` reports that
`farm-out/ep2-b08-twohander/b19-init-704x1280.png` — the picture beat 08's takes
were animated from — is a **costume card**: one figure, waist-up, eyes closed,
blank paper, no field, no second guard, no scavenger, while beat 08's `done_when`
requires three bodies and a belly in frame. Findings are in the handover report
accompanying this commit. The structural hazard is repo-wide and visible from
the branch listing alone: `farm-out/ep2-b17-lw/`,
`farm-out/ep2-b17-refire/` and `farm-out/ep2-b17-refireB/` each contain a
**`b13-init-704x1280.png`** — beat-17 jobs carrying a beat-13 plate. A plate is
identified by a filename convention that nothing enforces.

---

## 8. THE SAMPLE THAT WOULD SETTLE §5, AND IT WAS NOT FIRED

Named, not fired: the card has one job running and four in the backlog, and it
is fed.

**Two renders on beat 13's own plate, same seed, same recipe, same negative,
argv differing only in labels — a 2×2 collapsed to its two informative cells:**

- **Arm L (large + cyclic):** `"He rocks his whole body far forward until his
  forehead almost touches his knees, then leans far back, then forward again."`
- **Arm S (small + monotonic + chained):** `"He lifts his right hand off his
  knee, turns the palm over, and sets it back down on the grass beside him."`

Read the result the same way: median over the ladder, then open the frames.

- L moves and S holds → **size** is the variable. The commit's headline stands.
- L holds and S moves → **kind** (cyclic vs monotonic) is the variable, and
  "too small" is wrong. Three beats would need re-wording, not re-plating.
- Both move → beat 13's original wording was simply weak, and the whole "size"
  story dissolves.
- Neither moves → size *and* kind both matter, and only large monotonic actions
  are reachable — the most restrictive answer and the one with the biggest
  consequences for the wave.

**Is it worth one? Yes — but it is worth exactly two renders, not a batch.**
~8 minutes each, $0, on a plate now known to respond. It is the cheapest thing
on the board that can change a decision, because it decides whether three stuck
beats get **re-plated wide** (expensive, and another lane already owns that test
for 06/08/10) or **re-worded** (free). Firing a wave of wordings before this 2×2
would repeat the mistake this whole investigation just made.

**Do not** re-run the minimal positive control. That question is closed twice
over: the engine can move a figure.

---

## 9. WHAT THIS RENAMES

For two days, six independent lanes reported "the figure never moves its body"
and it was treated as an engine limit. It was not. Those six lanes correctly
eliminated wording (5 wordings × 3 seeds), the plate as an onset lever, the
13-latent count, the VAE/decode path, STG, the 200-word ceiling, the negative's
content and guidance as a ramp — **all correct, and all beside the point**,
because every one of them was measuring *how often the picture changed* while the
question was *whether the body moved*, and every one of them was asking the plate
for the one action it would not perform.

The problem is renamed, not solved:

> **from** "the engine will not move our figures"
> **to** "we do not yet know which property of an action request this engine will
> execute, and our frames may not have room for the ones it will."

That is a smaller, cheaper, testable problem. It is also still a hypothesis with
one sample behind it.
