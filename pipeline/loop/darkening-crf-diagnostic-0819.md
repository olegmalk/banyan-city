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

## RESULTS — measured 2026-08-19, `pipeline/luma_drift.py`, equal thirds

**The flag is exonerated, and the verdict it came from should be reversed rather
than narrowed: the darkening is not a recipe property at all.**

### The instrument reproduces the numbers it was built to check

Before trusting it on the clean pairs I ran it on the two takes that do darken.
It lands on the beat-20 verdict's figure exactly and beat 12's to a rounding
step, from a cold decode with no knowledge of either number:

| clip | crf | seed | f000 → f120 | drift | bands |
|---|---|---|---|---|---|
| `ep2-b12-stillmotion-0819` | 10 | 20260819 | 125.86 → 34.80 | **−91.05** | all fall (−85.4 / −116.7 / −71.2) |
| `ep2-b20-motion-0819` | 10 | 20260819 | 142.25 → 117.22 | **−25.03** | all fall (−22.0 / −5.1 / −47.9) |

b20's per-band figures come back −22.02 / −5.11 / −47.91 against the verdict's
−22.04 / −5.11 / −47.89. Same instrument, same convention, independently written.

### The two one-variable pairs

| pair | arm | crf | f000 → f120 | drift | bands agree |
|---|---|---|---|---|---|
| **b01** seed 20260818 | parent | 33 | 87.02 → 160.26 | **+73.24** | YES, all rise |
| | child | 10 | 88.09 → 89.46 | **+1.37** | no |
| **b18** seed 20260871 | parent | 33 | 116.13 → 115.91 | **−0.22** | no |
| | child | 10 | 116.21 → 126.35 | **+10.14** | YES, all rise |

**No crf-10 arm darkens. Not one.** `d10` is +1.37 and +10.14; the `CRF-CAUSED`
branch required `d10 ≤ −10` and cannot fire on any reading. The largest drift
anywhere in the experiment belongs to a **crf-33** arm — beat 01's parent climbs
73 levels, all three bands together, and nearly all of it inside the first second
(87.02 at f000, 154.17 by f024, then flat). That is the ladder's "original blooms
to 148.4", confirmed by a second instrument.

**Against my own pre-registration:** none of the four branches fits cleanly. The
rule was written for a space where *something* darkens, and in the clean pairs
nothing does — three of four clips brighten and the fourth is flat. `NOT-CRF` is
the branch whose *conclusion* holds, but its stated test ("the crf-33 arm drifts
down comparably") describes a world this data is not in. Recorded as a defect in
the bar, not smoothed over: **a drift rule needs a two-sided threshold**, because
the failure this recipe family actually produces is as often a bloom as a fade.

Band-sign clause, as pre-registered: the two clips whose bands disagree
(b01-crf10 at +0.66 / −3.70 / +7.13, b18-crf33 at +1.99 / +8.17 / −10.80) are
**not** scored as fades in either direction. Both are small and neither is
claimed as anything; no clip here needs eyes, because no clip here is called a
fade.

*One honest discrepancy.* On beat 01 the ladder records the crf-10 arm ending at
84.8 against a plate of 85.1, and the parent blooming to 148.4; I measure 89.46
and 160.26. Same direction, same magnitude class, ~5–12 levels apart. The b12/b20
figures reproduce almost exactly, so the instrument is not the suspect — the
beat-01 lane used a different, uncommitted convention (a crop, or an RGB mean
rather than BT.601 luma). **This is the whole argument for one committed
instrument**, and from here the beat-01 numbers should be re-cited from this file.

### What this settles, and it is the opposite of what was believed

The beat-20 verdict concluded *"IT IS A RECIPE PROPERTY AND NOT A BEAT
PROPERTY."* **The render argv says it cannot be.** All six specs, diffed flag by
flag:

| flag | value across all six |
|---|---|
| `--size` / `--frames` / `--fps` | 704x1280 / 121 / 24 |
| `--guidance` / `--two-stage` / `--distilled-sigmas` | 2.0 / set / set |
| `--offload` / `--mode` | sequential / production |
| `--image-crf` | **the only flag that differs** |

Every sampler number is identical across the takes that darken and the takes that
do not, and the one flag that varies is now measured on four clips: **two darken
catastrophically, two do not darken at all.** `--image-crf 10` is therefore
neither necessary nor sufficient for the effect, and no other sampler setting
distinguishes the groups because no other sampler setting varies. **The cause
lies in what is left: the init plate, the prompt, or the seed.** It is a beat
property, and the recipe-property claim is withdrawn.

### The lead, stated as a lead and not a mechanism

**Both darkening takes were rendered on seed 20260819. Neither clean take was**
(b01 on 20260818, b18 on 20260871).

| take | seed | drift |
|---|---|---|
| b12-stillmotion | **20260819** | −91.05 |
| b20-motion | **20260819** | −25.03 |
| b01 parent / child | 20260818 | +73.24 / +1.37 |
| b18 parent / child | 20260871 | −0.22 / +10.14 |

Two different beats, two different plates, two different prompts, two different
subjects — one shared seed, and the only two collapses on record. With `--size`
and `--frames` fixed the initial noise tensor is a function of the seed alone,
and this box was just shown to be **bit-exact reproducible at a fixed seed**, so
"this seed's noise draw carries a luminance bias" is a coherent mechanism rather
than a coincidence-shaped story. It is still only n=2 and it is **not** claimed
as established.

**It is also the cheapest possible test, and it is a legal one-variable rung:**
take either clean goblin-free carrier and change **only** the seed to 20260819.
b01 growmotion is the better carrier — its crf-33 arm blooms +73, so a seed that
drags luminance down has room to show against a known-bright baseline, and beat
01 is a sapling nub with no character on screen. Pre-register the bar as
`luma_drift.py` whole-frame drift with the two-sided threshold this file just
found missing. **Named here and filed as the next rung; nothing is claimed until
it runs.**

### What this licenses

**No promotion, no cut swap, no seed pick.** Four existing clips were measured
and one instrument was committed. Concretely it does three things: it removes
`--image-crf` from the suspect list for the darkening; it replaces the beat-20
verdict's recipe-property sentence with a beat-property one; and it retires the
brightness clause that verdict asked for *in the form it asked for it* — the
clause is still worth carrying on every 121-frame rung, but written **two-sided**
and attached to **the plate and seed**, not to the crf flag.

Beats 01, 12, 18 and 20 are all goblin-free on screen, so none of this touches
the identity freeze.

---

## SEED ARM — appended 2026-08-19, both probes landed and judged

The lead named seed 20260819 as the only thing the two collapses shared. **It is
cleared on both carriers.** Two rungs filed, run and judged within the hour, each
one variable off a passed goblin-free recipe:

| rung | carrier | seed | drift f000→f120 | bands | branch |
|---|---|---|---|---|---|
| `ep2-b01-growmotion-s20260819-0819` | b01 nub | 20260819 | **+16.59** | disagree (−0.17 / +14.40 / +35.54) | **PASS-HOLD** |
| `ep2-b18-tremble-s20260819-0819` | b18 macro | 20260819 | **−4.28** | agree (−1.66 / −2.20 / −8.98) | **PASS-HOLD** |

Neither reaches the two-sided 20-level bound; the collapses they were compared
against measured −91.05 and −25.03. `PASS-HOLD` was pre-registered as the more
likely outcome on both and fired on both.

*Against the flattering reading:* the b18 arm's three bands **do** all fall, so it
has the collapse's shape at 1/6th of the bound and 1/21st of b12's size. Worth one
sentence rather than none — but beat 18 now sits inside ±11 levels on every seed
and every crf value ever measured on it (−0.22, +10.14, −5.52, −4.28), so a −4.28
is that beat's noise floor and not a small collapse.

### Where the darkening question now stands

Three of the four candidate causes are measured out:

| candidate | status | evidence |
|---|---|---|
| `--image-crf 10` | **exonerated** | on four clips with opposite outcomes |
| every other sampler flag | **excluded** | argv identical across all six specs |
| seed 20260819 | **exonerated** | holds on two independent carriers |
| **the plate or the prompt** | **what is left** | not yet tested |

`ep2-b12-stillmotion-s20260871-0819` is the converse and the closer: the take that
lost 91.05 levels, re-rolled on 20260871 — the flattest seed on record —
everything else byte-identical. `FAIL-COLLAPSE-AGAIN` is pre-registered as the
more likely outcome, and if it fires the seed is exonerated from the other
direction too and the cause is the plate or the prompt. It was queued at
17:50 and is the only rung this question still needs.

---

## CLOSED — the converse rung landed and the answer is an INTERACTION

`ep2-b12-stillmotion-s20260871-0819`: **drift −0.04.** The parent, byte-identical
in plate, prompt and every sampler flag, measured **−91.05**. One integer of seed
between them.

| | seed | drift | bands |
|---|---|---|---|
| `ep2-b12-stillmotion-0819` | 20260819 | **−91.05** | all fall |
| `ep2-b12-stillmotion-s20260871-0819` | **20260871** | **−0.04** | disagree, all under 1 level |

**`FAIL-COLLAPSE-AGAIN` was pre-registered as more likely and did not fire.** The
plate and the prompt are exonerated along with everything else, and the true shape
of the answer is one no branch of any bar in this file described:

| factor | alone | evidence |
|---|---|---|
| `--image-crf 10` | **not the cause** | four clips, opposite outcomes, identical argv |
| every other sampler flag | **not the cause** | argv identical across all six specs |
| seed 20260819 | **not sufficient** | holds on b01 +16.59, on b18 −4.28 |
| b12's plate + prompt | **not sufficient** | holds on 20260871 at −0.04 |
| **seed × plate together** | **this is it** | 20260819 on *this* plate, and only there |

**My reasoning error, since it was pre-registered and therefore checkable:** I
treated the four candidates as mutually exclusive single causes and eliminated
them one at a time, which is a sound method only if a single cause exists. Each
elimination was individually correct and the conclusion each one pointed at — "so
it must be the next one on the list" — was wrong. A bar whose branches are all
single causes cannot express an interaction, and both of my "more likely"
predictions on this axis were wrong in the same way.

### What this is worth, practically

**A collapse on this plate is fixable by a re-roll**, because the plate and prompt
are now demonstrably capable of a flat 121-frame render. Beat 12 has a take that
holds luminance dead flat where the previous one lost 91 levels — *on luminance
only*; its stillness, bird and leaf clauses are unjudged and the pick is R4.

**Beat 20 is very likely the same and is deliberately left alone.**
`ep2-b20-motion-0819` also ran seed 20260819 and also collapsed (−25.03), so its
darkening is probably this interaction and probably re-rollable in one job. **That
rung is NOT filed:** beat 20's plate is the scavenger, and re-rolling it risks a
goblin-identity render under the freeze. It waits for the design answer or for
someone with authority to call the plate clear. **This is the single most
actionable thing in this file and the reason it is not acted on is a rule, not an
oversight.**

**Filed instead:** `ep2-b12-stillmotion-s20260818-0819`, a third seed on this
plate, because one clean seed can be luck and two would make 20260819 the outlier.

### The clause this leaves behind

The brightness clause beat 20 asked for is still worth carrying on every
121-frame rung, and `luma_drift.py` makes it cheap — but write it **two-sided**
and attach it to **the (seed, plate) pair**, not to a flag and not to a beat. The
honest generalisation from six clips is narrow: *this recipe family can lose or
gain 90 levels on a seed that behaves perfectly elsewhere, so luminance is a
per-render check and never a property you inherit from a passing sibling.*
