# Is the progressive darkening caused by `--image-crf 10`?

**Filed 2026-08-19 by the queue-keeper lane. This section is written BEFORE the
instrument is run, and the section below it is appended after. Nothing above the
RESULTS line was edited once numbers existed.**

## The question, and why the rung it was ordered as cannot be built

The standing order was: pick the cleaner goblin-free carrier (b18 tremble or b01
growmotion), take the seed class of a measured-darkening take, and **vary only
`--image-crf` back to 33 on one sample.**

**That rung cannot be filed, because both named carriers are already at crf 33.**
Read off the specs:

| spec | `--frames` | `--image-crf` |
|---|---|---|
| `ep2-b01-growmotion-0818` | 121 | **33** |
| `ep2-b18-tremble-s2-0819` | 121 | **33** |
| `ep2-b01-growmotion-crf10-0819` | 121 | **10** |
| `ep2-b18-tremble-crf10-0819` | 121 | **10** |
| `ep2-b12-stillmotion-0819` (darkens −91) | 121 | 10 |
| `ep2-b12-shortstill-0819` | 73 | 10 |
| `ep2-b20-motion-0819` (darkens −25.03) | 121 | 10 |

There is no crf-33 to return them to. **But the reason is better than the
order:** the one-variable pairs the question needs were already rendered on
2026-08-19 and are sitting on this disk. Both crf-10 specs were derived
programmatically from their crf-33 parents and both record an **identical init
sha** — `ep2-b01-growmotion-crf10-0819` off `ep2-b01-growmotion-b-0818`
(sha `1a7ff3d0…`, seed 20260826), `ep2-b18-tremble-crf10-0819` off
`ep2-b18-tremble-s20260871-0817` (sha `b6cf610a…`, seed 20260871). Same seed,
same init, same prompts, same 121-frame temporal grid, same sampler numbers,
**`--image-crf` the only difference.**

So the diagnostic is a **$0 measurement of four existing clips**, not a render.
It is also a strictly better experiment than the one that was ordered: two
independent beats instead of one, both directions of the flag instead of one
arm, and the GPU stays free for the seed-depth rungs already on the card.

## One correction to the evidence the question was built on

The order cited two darkening observations. **One of them is not darkening.**

- **Beat 20, `ep2-b20-motion-0819`: real, and global.** Whole-frame mean walks
  141.89 → 116.86 over 121 frames, −25.03, and **all three bands fall together**
  (190.79→168.75, 97.53→92.42, 137.24→89.35). Plate fidelity is excluded at
  source: init 143.78 against f000 141.89, a 1.89-level hold. The drift happens
  during sampling.
- **Beat 12 `shortstill`, rows 560–1120 −46.93: NOT a fade, and its own verdict
  says so.** The other two bands move −1.55 and −1.72. What moves is **a dark
  leaf mass entering at the left edge about f004 and growing across the
  mid-ground** — scored `FAIL-PLANT-CHANGE`, foliage with midribs and a warm rim
  light under a 2× gamma lift. A mean over one band cannot tell an object from a
  fade, which is exactly the blind spot `luma_drift.py` is documented against.

**The real second data point is the 121-frame parent, `ep2-b12-stillmotion-0819`:
125.47 → 34.37, −91 levels, falling in all three bands** (134.73/130.60/75.09 →
35.77/36.50/21.99). That is the take the beat-20 verdict actually cited when it
concluded "two beats, same drift, same recipe".

So the standing evidence is **two 121-frame crf-10 takes that darken globally**,
and the hypothesis under test is the beat-20 verdict's own words: *"IT IS A
RECIPE PROPERTY AND NOT A BEAT PROPERTY."*

## What I already know, disclosed so the result cannot be read as blinder than it is

This is a **retrospective** measurement — the pixels existed before the bar did,
which is weaker than pre-registering a render, and it is labelled as such.

I am **not blind on beat 01.** The ladder already records its crf-10 take ending
at luma 84.8 against a plate of 85.1 while "the original blooms to 148.4". If
that holds up, beat 01's crf-10 arm *holds* and its crf-33 arm *brightens* — the
opposite of the hypothesis. **I have no prior luminance figure of any kind for
either beat-18 arm, so the b18 pair is the informative one** and the b01 pair is
a check on a number someone else reported.

## The bar, fixed now

Instrument: `pipeline/luma_drift.py`, equal thirds, frames 0/24/48/72/96/120,
whole-frame mean BT.601 luma on the decoded mp4. Magnitude threshold **10
levels**, taken from beat 12's own 12-level dusk bound rounded down; both
observed drifts (−25.03, −91) clear it by a wide margin.

Per pair, `d10` = whole-frame drift f000→f120 of the crf-10 arm, `d33` = same for
the crf-33 arm:

- **`CRF-CAUSED`** — `d10 ≤ −10` **and** `|d33| < |d10| / 2`, on **both** pairs.
  The flag is implicated; a brightness clause belongs on every crf-10 rung.
- **`NOT-CRF`** — on at least one pair, the crf-33 arm drifts down comparably
  (`d33 ≤ d10 / 2`) or further. The darkening survives removing the flag, so it
  belongs to the rest of the recipe — the 121-frame grid, the two-stage
  distilled-sigma schedule — and the beat-20 verdict's attribution is too narrow.
- **`NEITHER-ARM-DARKENS`** — both arms hold within ±10 on both pairs. Then
  neither b01 nor b18 reproduces the effect at all, the carriers are simply not
  susceptible, and the two darkening takes differ from them by something other
  than crf. This outcome licenses no claim about the flag.
- **`MIXED`** — the two pairs disagree. Beat-dependent; the recipe-property claim
  fails as stated, and the next question is what the susceptible beats share.

**Named as most likely before running: `NOT-CRF`.** Two reasons. The beat-20
verdict itself excludes the init at source (1.89 levels of hold) and places the
drift in sampling, which the flag only reaches indirectly; and the one prior
number on record points the other way, with a crf-33 arm blooming +63 while its
crf-10 sibling held. If `NOT-CRF` fires, the honest reading is that a real
finding — two beats darkening — was attributed to the one knob that had recently
changed.

**Also pre-registered, because a band mean invites the leap:** if a pair's three
bands disagree in sign, that clip is **not** scored as a fade in either
direction. It gets `OBJECT-SUSPECTED` and needs eyes on the frames, exactly as
beat 12's mid-band did.

**What this licenses either way: nothing renders off it.** It is one measurement
of four existing clips. It cannot promote a take, swap a cut, or pick a seed —
and it does not touch the goblin-identity freeze, since beats 01 and 18 are a
sapling nub and a macro leaf with no character on screen.

---

## RESULTS

Not yet measured. The instrument has not been run at the time this
pre-registration was committed.
