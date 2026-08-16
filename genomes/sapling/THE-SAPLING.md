# THE SAPLING — what the plant IS

**This file is current and is meant to be rendered from.** It exists because
`genomes/sapling/style.md` disclaims itself on its own third line (*"⚠ STALE
(2026-07-27) … Do not render from this"*), and a canon kept in a file that says
not to use it is not a canon. Style — the *look* of the show — still belongs to
`style.md` and to the founder (R4). This file describes one *object*: the plant
the show is named after.

It is the answer to the `THERE IS NO SAPLING` card (`review/inbox.yaml`,
2026-08-16), which established by survey that 12 of episode 2's 21 beats put the
sapling, its leaf or its fruit on screen and that **no prose description of the
plant existed anywhere in the repo** except one self-disclaiming sentence.

Machine-checkable form: `pipeline/canon.yaml` subjects `sapling-two-leaves`,
`sapling-cotyledon-shape` and `sapling-height`, swept by
`python3 pipeline/check_canon_drift.py`. Prompt-level continuity:
`python3 pipeline/check_sapling_scale.py`.

---

## 1. THE RULING — his words, verbatim

> *"alright, lets be a bit more strict with the sapling. make sure it has 2
> leafs and has a set height, height might be a bit hard for the ai to make
> exact, so dont go crazy on it, just dont make it double in size suddenly"*
>
> — the founder, 2026-08-16

Three things are settled by that sentence and nothing more is:

1. **TWO LEAVES.** Not "one or two". Not "three or four". Two.
2. **A SET HEIGHT.** The plant has one, and it is written down (§3).
3. **THE CONSTRAINT ON HEIGHT IS CONTINUITY, NOT PRECISION.** He said so
   himself — *"height might be a bit hard for the ai to make exact, so dont go
   crazy on it"*. The failure he named is **sudden doubling**, and that is the
   thing to check for. Chasing an exact centimetre count is explicitly not the
   job.

---

## 2. LEAVES

### 2.1 Count — HIS RULING, two

Every prompt that puts the plant in frame asks for **exactly two leaves**.

Wordings already in the repo that satisfy this: *"two big leaves"*, *"exactly
two oversized cotyledon leaves"*, *"a thin stem with two oversized leaves"*.

Wordings that violate it, found live on 2026-08-16 and corrected below:
*"only three or four leaves"* (beat 01), and any prompt that describes foliage
without a count.

### 2.2 Shape — ⚠ STEWARD INFERENCE, NOT HIS WORDS. VETOABLE IN ONE LINE.

**The working canon is ROUND/OVAL COTYLEDONS.**

**He did not say this.** He ruled two leaves; the shape is the steward's
inference from that ruling, recorded here so he can strike it in one line
without a new card. The reasoning, written down so the veto is cheap:

- A two-leaf plant at ~40 cm is a **cotyledon-stage seedling**, and cotyledons
  are round or oval. That is what a seed's first two leaves are.
- **Deeply lobed, five-fingered fig leaves are MATURE-TREE foliage.** They are
  incompatible with a two-leaf seedling: a fig does not carry palmate leaves and
  two of them.
- The existing evidence already leaned the same way before he ruled. *"wide oval
  cotyledon leaves with soft round tips, not narrow, not pointed, not
  lance-shaped"* appears on **four** beats (12, 15, 19, 20) against *"deeply
  lobed fig leaves with five fingers"* on **one** (01). The growth ladder in
  `style.md` puts 001 at *"two oversized cotyledon leaves"* and 002a/b/c at
  *"two leaves + one thin side-branch"* — cotyledon language, not fig-leaf
  language.

**TO VETO:** one line — *"lobed, not round"* — and this section inverts. Nothing
else in this file depends on it.

**The negative `no simple oval leaves`** (live on beats 01 and 18) is the exact
inverse of this inference and is corrected below.

---

## 3. HEIGHT

### 3.1 The set height

**~40 cm at node 002b.** This is not new; it is the `002a/b/c` row of the
canonical growth ladder (`genomes/sapling/style.md` §"Canonical growth ladder",
steward 2026-07-25), and it is the one part of that file that is not stale
because it is structure, not look:

| Node | Height | Canopy |
|---|---|---|
| 001 | ~15 cm | two oversized cotyledon leaves |
| **002a/b/c** | **~40 cm** | **two leaves + one thin side-branch** |
| 003b | ~55 cm | three leaves, bare fig branch |

The figure is corroborated by the show's own approved VO, beat 03 of 002b:

> **VO:** *"A creature is using me as cover. I am forty centimeters tall."*

That line is voiced, in `node.md`, in `shots.md` and in `clips/03-vo.json`. It
is canon and it is arithmetic: the sapling is **shorter than the goblin**, which
is the entire joke of beat 03 — he hides behind a plant *"that hides almost none
of him"*.

### 3.2 The height is a RELATION, not a number the model has to hit

He said height is hard to make exact and asked us not to go crazy on it. So the
canon is expressed as a relation, which a model *can* hit and a reader *can*
adjudicate:

> **The sapling is knee-high on the goblin: about 40 cm, always shorter than he
> is, in every beat of 002b.**

### 3.3 `standing tall` is POSTURE, not height — and this was already ruled

Nine drafts say the sapling is *"standing tall"*. **This is not a violation and
must not be scored as one.** The distinction is already ledgered, in
`taste/steward-model.v1.md` axis A7, in the steward model's own words against
his:

> *"'Reads tall' is about how the subject sits in the FRAME, not about the
> character's stated size."*

Beat 02's own draft proves it by writing both at once — *"a tiny 40cm
mascot-simple sapling standing tall"*. A rule that fired on `standing tall`
would fire on nine drafts for no defect, which is the cry-wolf pattern that got
the runner watchdog switched off for four days after 60 false restarts in five
hours.

Likewise **`no taller than the grass around it`** (beats 01, 12) is compatible
with 40 cm in summer grass and is **not** a violation.

**The one wording that genuinely breaks the ruling is `taller than he is`** — it
makes the plant taller than the goblin, contradicts the voiced VO line, and
destroys beat 03's cover joke. See §5.1.

### 3.4 The frame-proportion band, for anyone measuring

A7 also fixes a ceiling, off a measured plate rather than eyeballed:

> **Ceiling:** *"you used a frame i never approved, and its **tooooo tall**."* —
> founder, 2026-08-08, revoking episode 2's cold-open plate.
>
> What "too tall" measured: a **1–3 pixel hairline stem standing 385 px, 32% of
> the frame's height**, apex at 25.9% from the top.
>
> **Floor:** *"all too small, not good character consistency"* — same day.

So: a hairline thread reaching a third of the frame is past the ceiling; a
subject lost in the frame is under the floor. **Treat these as the outer walls,
not as a target.** The rule inside them is §1.3 — do not double suddenly.

---

## 4. WHAT IS STILL UNDETERMINED — deliberately not filled in

He ruled on two leaves and a set height. The following are **not** settled by
his words and are **not** invented here. Anything below may be chosen per shot
until someone with the authority rules:

- **The stem.** Live prompts variously say *"sturdy curved stem"*, *"pencil-thin
  trunk"*, *"thin trunk"*, *"slender upright stem"*, and beat 12 says *"no
  trunk"* while beats 02 and 03 have the goblin hiding behind a trunk. **No
  canon.** (Note only: A7 asks for *"a stem of real substance"* rather than a
  hairline, which is a proportion note, not a stem description.)
- **Leaf size in the frame.** *"oversized"* and *"big"* are both live. No ruling.
- **The side-branch.** The growth ladder says **one thin side-branch** at 002b
  and that is the only figure that exists; whether it is bare, and where it sits,
  is undetermined.
- **Fruit shape.** *"one small round purple fruit"* against *"a small
  teardrop … NOT a sphere, NOT a round ball"* — both live. **Not this file's
  subject**; the fig is a separately frozen canon and belongs to the fig lane.
- **Fruit colour** is PURPLE by his 2026-08-13/14 ruling and is registered
  separately as `ep2-fig-purple` in `pipeline/canon.yaml`. His purple ruling
  kills red; §5.2 records that it also has to kill **green**, explicitly,
  because green survived it by not being named.
- **"mascot-simple"** — the word `style.md` uses and that our own records blame
  for the plant coming back as a creature with a face. Flagged, not ruled.

---

## 5. SUPERSESSION — read this before applying any older sapling rule

### THE 2026-08-08 RULE IS SUPERSEDED BY THE 2026-08-16 RULE.

> **2026-08-08 (SUPERSEDED):** *"whats the point of a character sheet for the
> engineer? … im talking about the sapling, and its very simple, just make it
> tall in each clip of it, and thats pretty much it. **dont overthink the leafs
> on it.**"*
>
> Recorded in `taste/steward-model.v1.md` axis A1 as a standing rule that **leaf
> count and leaf shape are NOT to be scored** — *"No prompt term, QA check or
> screening note counts leaves or matches leaf shape."*

> **2026-08-16 (IN FORCE):** *"lets be a bit more strict with the sapling. make
> sure it has 2 leafs and has a set height."*

**Both dates are given so nobody applies the older rule and skips scoring the
leaves.** As of 2026-08-16 leaf **count** is scored and is canon; leaf **shape**
is scored against the inference in §2.2 until he vetoes it. The 08-08 sentence
survives only in its other half — the **character-sheet decline** still stands,
and this file is prose, not a sheet, which is what the card asked him for.

The 08-08 **height** rule (A7 floor/rule/ceiling) is **not** superseded; it is
about frame proportion and is preserved verbatim in §3.3–3.4.

---

## 6. CORRECTIONS ISSUED 2026-08-16

House style: **superseded text is left standing and a dated correction is added
beside it.** Nothing below was erased.

### 6.1 `taller than he is` — beat 15

Directly violates §3. Found in the *payload prompt text* of six job specs:

`ep2-b15-leaf-0813.yaml:46`, `ep2-b15-leafB-0813.yaml:46`,
`ep2-b15-sapling-probe-0812.yaml:58`, `ep2-b15-sapling-r2-0812.yaml:53`,
`ep2-b15-seedB-0812.yaml:43`, `ep2-b15-seedC-0813.yaml:43`
(and `farm-out/ep2-b15-mac-plate-0815/15-good-listener-mac-body-r6.yaml:17`,
*"one thin bare stalk taller th…"*).

**All six already ran** (verified against `pipeline/measured/queue-history.json`
by `task` name). A fired job spec is a **receipt**, not an instruction: editing
its payload would falsify the record of the bytes that were actually sent. They
are therefore left standing and superseded by this file. The two specs cited by
name in `STATE.md` and in the card carry a dated correction header pointing
here, so anyone following the citation lands on the correction.

The phrase **is not in `wave-drafts.yaml`**, so no reusable draft carries it and
nothing can pick it up again.

### 6.2 `ONE SINGLE ROUND GREEN FIG` and other green-fig positives

His 2026-08-13/14 ruling made the fig **purple**. His 2026-08-16 ruling kills
**red**. Neither names **green**, so green survived both by omission — which is
how it is still live. **It is corrected here explicitly: the fig is PURPLE, and
green is a defect, not a default.**

Verified live on 2026-08-16 in *positive* prompt text (negatives saying `no green
fig` are the canon working and were excluded):

- **Job specs, 31 of them, all already run** — 9 on beat 01
  (`cold-r2`, `cold-r2B`, `figgrow-055`, `figgrow-055-r2`, `figgrow-055-r3`,
  `nocrf`, `shape`, `shape-a2`, `shapeB`) and 16 on beat 18
  (`count`, `countB`, `figfeat`, `figfeatB`, `figshape`, `figshape-r2`,
  `figshape-r2B`, `figshapeB`, `firstera`, `motion`, `nocrf`, `seedB`,
  `stable:48`, `stableB:50`, `tight:47`, `tightB:47`). Receipts; left standing.
  *(The card cited `ep2-b18-stable-0812.yaml:48`; re-derived and confirmed
  correct, and `stableB:50` / `tightB:47` carry it too.)*
- **Reusable drafts in `pipeline/wave-drafts.yaml` — these are the ones that
  matter**, because a draft can be picked again by a future job:
  `b01:authored`, `b01:authored_b01_t2i_fig`, `b18:authored`,
  `b18:authored_b18_plantneg`, `b18:authored_b18_refresh`. Corrected additively
  (§6.5).

### 6.3 `deeply lobed fig leaves with five fingers` + `no simple oval leaves`

The exact inverse of §2.2. Live in seven reusable drafts:
`b01:authored_b01_figleaf`, `b01:authored_b01_figleaf2`,
`b01:authored_b01_figleaf3`, `b01:authored_b01_figlit`,
`b18:authored_b18_figleaf2`, `b18:authored_b18_figleaf3`,
`b18:authored_b18_figlit`. Corrected additively (§6.5).

### 6.4 `only three or four leaves` — beat 01

Violates §2.1 outright. Live in `b01:authored` and `b01:authored_b01_t2i_fig`.
**This one was not in the survey and was found while verifying it.** Corrected
additively (§6.5).

### 6.5 `sapling_drafts_ACK_0816` — the superseded drafts, enumerated

The drafts below contradict this canon, **all of their job specs have already
fired**, and each has a dated `*_0816` replacement beside it in
`pipeline/wave-drafts.yaml`. They are acknowledged history. `check_canon_drift.py`
stays quiet on them **and fails immediately if anything queues one** — an
acknowledged draft may sit in history, but nothing may fire it.

    authored_b01_figleaf
    authored_b01_figleaf2
    authored_b01_figleaf3
    authored_b01_figlit
    authored_b01_t2i_fig
    authored_b18_figleaf2
    authored_b18_figleaf3
    authored_b18_figlit
    authored_b18_plantneg
    authored_b18_refresh

The bare key `authored` is also acknowledged, for `sapling-two-leaves` and
`sapling-fig-not-green` only. That key exists on **every** beat and the
acknowledgement list has no beat filter, so this would normally be a blindfold.
It is safe for these two subjects and only these two because their forbidden
phrases — `three or four leaves` and a positive `green fig` — occur on beats 01
and 18 alone in the whole corpus, and both subjects are beat-scoped to exactly
those. **Do not copy that line to a subject whose forbid appears widely.**

**The already-fired job-spec payloads are acknowledged too** — 26 green-fig on
beats 01/18 and 6 `taller than he is` on beat 15, each enumerated in
`pipeline/canon.yaml` and each verified run by `task` name against
`pipeline/measured/queue-history.json`, a 573-row completed-run ledger. They are
receipts (§6.1).

### 6.6 FIVE KNOWN-FALSE FAILURES IN THE SWEEP, and why they are not being papered over

As of 2026-08-16 `check_canon_drift.py` reports five
`unrun_job_against_canon` failures against this canon:
`ep2-b04-goblin-close-0811` (×3), `ep2-b18-plantneg-0812` and
`ep2-b18-refresh-0811`. **All three specs ran.** Verified by `task` name in
`queue-history.json`.

They are false because the checker's run-detection looks only at `farm-out/`
directories and render-time sidecar variants; `farm-out/` is pruned, so age
alone manufactures "no render evidence". `ep2-b04-goblin-close-0811` is doubly
false: its `--variant authored` names a key that exists on every beat, so it is
attributed to beats 01 and 18 as well as its own.

**This is not fixed here on purpose.** `check_canon_drift.py` belongs to another
lane and was mid-change while this canon was being written; reaching into it
would have been two lanes editing one uncommitted file. The fix is one line in
theirs — gate payload prompts and unrun-job detection on `queue-history.json`
the way `unrun_jobs` already gates variants — and it deletes every `jobs/...`
entry from the acknowledgement lists as a side effect. Recorded here so the
count is not mistaken for five real violations, and not suppressed, because a
suppressed false positive is how a check stops being read.

---

## 7. NOTHING WAS RENDERED, DRAWN OR SPENT FOR THIS FILE

$0, no GPU, no render, no voice. Every claim above was verified by reading:
`review/inbox.yaml`, `pipeline/wave-drafts.yaml` (as text, never a YAML
round-trip), all 824 specs in `pipeline/jobs/`,
`pipeline/measured/queue-history.json`, `genomes/sapling/style.md`,
`taste/steward-model.v1.md`, and `genomes/sapling/nodes/002b-first-citizen/`.

**No reference image exists for the plant and none was made.** `genomes/sapling/refs/`
holds the goblin and the engineer; `review/SHEETS/` has sheets for the goblin and
the guards and none for the plant; the sampler has `goblin`, `guard` and `fig`
keys and **no `sapling` key**. Drawing one would be proposing what the plant
looks like, which is the R4 call this canon deliberately does not make — it
records his ruling and marks its own one inference as inference.

## Provenance

Written by the steward (Claude Opus 5), 2026-08-16, from the founder's ruling of
the same date. §2.2 is steward inference and is labelled as such. All other
sections are his words, the ledgered growth ladder, or measurements re-derived
from the repo.
