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

### 2.2 Shape — HIS RULING, 2026-08-17: AVERAGE LEAVES

> *"the sapling 2 leaves are average leaves"*
>
> — the founder, 2026-08-17

**The canon is ORDINARY LEAVES.** A plain, unremarkable leaf — the shape anyone
draws when you say "leaf" — and nothing exotic on either side of it. His sentence
rules out the *special* leaf in both directions:

- **Out: deeply lobed, five-fingered fig leaves.** A palmate mature-fig leaf is
  the opposite of average. It is a botanical specimen and it reads as one.
- **Out: a leaf drawn as a feature.** No lance shapes, no exaggerated
  silhouette, no leaf whose shape is the subject of the shot.

**What his words do NOT settle, and are not stretched to cover:** leaf SIZE in
the frame (§4 still records `oversized` and `big` as both live and unruled), and
whether the two leaves are called *cotyledons*. "Average" is a ruling about
shape. It is not a ruling about vocabulary or about scale.

#### THIS SUPERSEDES THE STEWARD INFERENCE OF 2026-08-16 — both dates stay visible

House style is §6's: superseded text stands and the correction is added beside
it. Until 2026-08-17 this section read:

> ~~**Shape — ⚠ STEWARD INFERENCE, NOT HIS WORDS. VETOABLE IN ONE LINE.**~~
> ~~**The working canon is ROUND/OVAL COTYLEDONS.** He did not say this. He
> ruled two leaves; the shape is the steward's inference from that ruling…~~
> ~~A two-leaf plant at ~40 cm is a **cotyledon-stage seedling**, and cotyledons
> are round or oval.~~ ~~**TO VETO:** one line — *"lobed, not round"* — and this
> section inverts.~~

**The veto arrived, and it went neither of the two ways the inference offered.**
The inference framed the question as round-or-lobed. He answered *average*, which
**keeps the inference's practical effect** — the palmate fig leaf is still out,
so §6.3 stands unchanged — and **drops its botanical claim**: the canon no longer
asserts the leaves are round *because they are cotyledons*. It asserts they are
ordinary because he said so. What was the steward's to defend is now his, and
§2.2 is no longer the one inference in this file.

Both dates, so nobody applies the older rule: **2026-08-16** (steward inference,
round/oval cotyledons) → **2026-08-17** (his ruling, average leaves). Same shape
of supersession §5 records for 2026-08-08's *"dont overthink the leafs on it"* →
the 2026-08-16 two-leaf ruling. The evidence the inference leaned on is not
deleted either, and it survives his ruling intact: *"wide oval cotyledon leaves
with soft round tips, not narrow, not pointed, not lance-shaped"* on beats 12,
15, 19 and 20 describes an average leaf and is compliant; *"deeply lobed fig
leaves with five fingers"* on beat 01 does not and is not.

**The negative `no simple oval leaves`** (live on beats 01 and 18) is still
wrong, and it is now wrong against **his words** rather than against an
inference: an average leaf is closer to a simple oval than to anything else, so a
prompt forbidding simple ovals forbids the canon. §6.3 stands.

**NOT DONE HERE, and it is a real gap.** `pipeline/canon.yaml`'s subject
`sapling-cotyledon-shape` still encodes the 08-16 inference, and
`check_canon_drift.py` reads it — so the machine check enforces the superseded
inference until that lane carries his ruling into it. Both files were
**uncommitted in another lane's hands** as this was written (` M` in
`git status`), and editing either would have put two lanes in one file — the
mistake §6.6 already declined once. Flagged, not touched.

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

The figure is stated outright by the show's own approved VO, beat 03 of 002b:

> **VO:** *"A creature is using me as cover. I am forty centimeters tall."*

That line is voiced, in `node.md`, in `shots.md` and in `clips/03-vo.json`.
**Read the speaker label: VO is the SAPLING** (`node.md:30`, *"I used to be an
engineer. Now I'm a tree."*), and the goblin is **SCAVENGER**. So this is the
plant saying how tall the plant is — not the goblin, and not a measurement of
the goblin. It is canon. What follows from it is **not** arithmetic, because the
goblin's height is stated nowhere: the sapling is **shorter than the goblin**
because that is the entire joke of beat 03 — he hides behind a plant *"that
hides almost none of him"*.

### 3.2 The height is a RELATION, not a number the model has to hit

He said height is hard to make exact and asked us not to go crazy on it. So the
canon is expressed as a relation, which a model *can* hit and a reader *can*
adjudicate:

> **The sapling is about 40 cm, always shorter than he is, in every beat of
> 002b.**

**CORRECTED 2026-08-16 — the words "knee-high on the goblin" are withdrawn.**
Until today this line read:

> ~~The sapling is knee-high on the goblin: about 40 cm, always shorter than he
> is, in every beat of 002b.~~

It is left standing above rather than erased, so that nobody restores it by
finding it quoted somewhere else. Three things about the correction:

**1. Why "knee-high" was wrong: it is already spoken for, one rung up the same
ladder.** The growth ladder in `genomes/sapling/style.md` assigns **"knee-high"
to node 004 at ~90 cm** — the row whose whole point is that the plant finally
casts a shade patch big enough for a goblin to sit in, which is why the town is
called Shade. Using the same word for **~40 cm at 002b** put one label on two
heights **2.25× apart in the same document family**, which is exactly the
continuity trap §3 exists to close. And it resolved in the wrong direction: read
literally, a 40 cm knee puts the goblin at roughly 1.4 m, and then **004's 90 cm
plant is thigh-high and the ladder's own row label breaks.**

**2. What survives, because both halves are sourced.** The **figure** — ~40 cm
is the ladder's own `002a/b/c` row (§3.1), and the VO states it (see 3 below). The
**relation** — `always shorter than he is` — is beat 03's cover joke and is
untouched. Only the body-part metaphor is gone, and **nothing replaces it**: the
canon now uses the 002a/b/c row's own height cell as its vocabulary, so it can
no longer collide with a row label.

**3. THE PREMISE THIS ALSO CORRECTS — who says "forty centimeters".** It is
**not the goblin**. `node.md:40` is spoken by **VO**, and VO is **the sapling**,
established ten lines earlier at `node.md:30`: *"VO (dry, flat, engineer): I
used to be an engineer. Now I'm a tree."* The goblin's speaker label is
**SCAVENGER** throughout. So *"I am forty centimeters tall"* is the **sapling
stating its own height** — direct evidence for the figure, and stronger than
"corroboration" — and **the goblin's height is stated nowhere in this repo.**
"Knee-high on the goblin" quietly converted the plant's own stated height into a
measurement of the goblin's body and thereby invented a number for him. The
replacement wording states the plant's height and the relation, and **says
nothing whatever about how tall he is** — which is the correct posture, and not
merely a cautious one. **How the plant and the goblin stand relative to each
other is an open R4 question and this correction must not pre-empt it.** It is
deliberately silent on the goblin's height, and it anchors no beat's staging.

**Known and NOT fixed here, recorded so it is not lost a second time:**
`knee high` is also an accepted *prompt* scale anchor — `pipeline/canon.yaml`
`below-the-goblin`, `pipeline/check_sapling_scale.py:120`, `sd_prompt.py:79`,
and roughly twenty live drafts in `pipeline/wave-drafts.yaml` use it to mean the
40 cm plant. Those inherit the same collision with the ladder's 004 row. Changing
the anchor vocabulary is a corpus-wide sweep with test consequences
(`pipeline/test_pipeline.py` and `pipeline/test_sapling_scale.py` both assert on
the string) and it is not this correction. Two prose restatements of the
withdrawn wording also survive, in a file this pass had no licence to edit:
`pipeline/check_sapling_scale.py:125` and `:245`. All of it is written down
**here**, in the canon that governs it, rather than in a job spec that cannot
act on it.

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
is scored against §2.2, which as of **2026-08-17** is his own ruling
(*"the sapling 2 leaves are average leaves"*) and no longer a steward inference. The 08-08 sentence
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

> **CORRECTION_0816 — the five are gone, and so is the pre-existing sixth.**
> The paragraphs above stand as written; they were true for about an hour. The
> checker's own lane shipped the fix in `4a8580de` — *"the render evidence is 90%
> untracked, so the check answered CI differently from the laptop and said purple
> had never run when six ledger rows carry it"* — which is the same root cause
> reported from here, found independently and fixed properly rather than by the
> one line suggested. `check_canon_drift.py` now reports **`fail=0 ack=68`**: the
> five false `unrun_job_against_canon` findings are gone, and so is
> `canon_never_ran ep2-fig-purple`, the one failure that predated this canon.
>
> **The `jobs/...` acknowledgement entries in `pipeline/canon.yaml` are still
> live and still needed** — the fix corrected run *detection*, not the decision
> to read fired payloads, so those prompts are still swept and still correctly
> acknowledged. Verified: zero `stale_acknowledgement` findings.

---

## 7. THE CONTINUITY CHECK — `pipeline/check_sapling_scale.py`

*"Don't make it double in size suddenly"* is the one part of his ruling that is
measurable, so it got a check. **It reads words, not pixels**, and the reason is
the second half of this section.

**What it does.** Every prompt that can still run — all reusable
`wave-drafts.yaml` drafts, plus the payloads of job specs with **no completed
run in `queue-history.json`** — is classified:

- **FAIL** if it states the size *wrongly* (`taller than he is`).
- **OK** if it carries an explicit scale anchor: `40cm`, `knee high`,
  `shorter than he`, `no taller than the grass`.
- **EXEMPT** if the framing is macro/close-up — the whole plant is not in shot,
  so its size is not depicted.
- **WARN** if the plant is in frame and **nothing says how big it is**.

**Why coverage and not contradiction.** `check_canon_drift.py` already catches
prompts that state the wrong size. Nothing caught prompts that state *no* size —
and that is the actual mechanism of the doubling. **A stated height cannot double
between two beats; an unstated one re-rolls every seed.**

**The measurement, 2026-08-16:** of 87 live plant prompts, **6 are anchored, 13
are exempt macros, and 68 say nothing at all.** That number *is* the finding. It
is reported as WARN and the check **exits 0** on it — it is a coverage map, not
an alarm, and it blocks nothing.

### 7.1 What it cannot do — including one hole nobody should try to fill

1. **It cannot measure a pixel.** A prompt saying `40cm` that renders a tree
   passes here. Only an eye catches that.

2. **APPARENT HEIGHT IS NOT PLANT SIZE, and no cross-beat pixel measure can be
   honest about it.** Tested rather than assumed, by pulling frames and looking:
   `cuts/checklist/002b-b01-5b.mp4` frame 0 shows the whole plant as a hairline
   stem across half the frame; `review/ep2-prov-0809/ltx-002b-b12-prov-v2.mp4`
   frame 0 shows the *same plant in the same node* as an extreme macro — seven
   broad leaves edge to edge, no stem base, no grass, no horizon. They differ in
   apparent scale by more than 10x and **neither is a continuity error**: beat
   12's shots.md asks for *"tight on the sapling's TWO leaves against the sky"*.
   A rule of the form "apparent height must not jump between beats" would fire on
   every correctly framed macro in the episode. It is not unreliable — it is
   **measuring the wrong quantity**, because it conflates shot scale with plant
   size. Hence macro beats are exempt, and no cross-beat pixel metric exists.

3. **Within one clip a size change WOULD be meaningful** — every prompt says
   *"static locked framing, the frame never moves"* — **and it is still not
   attempted.** Segmenting a small green plant against green grass is the exact
   class in which four trackers were retired for cause in two days: a colour rule
   matching **zero** hand pixels; one that could not tell a hand from a bald
   head; a freeze index calling clips frozen while the figure rose 35–44% of
   frame height; a head tracker whose box sat on the **sky band**. Every one was
   confident. The b01 frame above is the *favourable* case — dark plant, bright
   sky — and even there the apex is against sky while the base is buried in
   grass, so the base, and therefore the height, has no defined edge.

### 7.2 The manual check, which is the honest one

Build a contact sheet of the plant across beats in story order — the tooling
already exists (`pipeline/compare_sheet.py`, `pipeline/build_comparison.py`, and
the `CONTACT-*.png` convention) — and look once. The eye settles *"did this
double"* in seconds and needs no threshold. **A guard that cries wolf gets
disabled** — the runner watchdog was switched off for four days after 60 false
restarts in five hours — so an untrustworthy measure is worse here than no
measure plus the habit of looking.

Tests: `python3 pipeline/test_sapling_scale.py` (22, all from real repo strings).

## 8. NOTHING WAS RENDERED, DRAWN OR SPENT FOR THIS FILE

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
the same date. All sections are his words, the ledgered growth ladder, or
measurements re-derived from the repo.

**Revised 2026-08-17 by the steward (Claude Opus 5), narrative lane** — §2.2 only.
The one section that was labelled steward inference is now his ruling
(*"the sapling 2 leaves are average leaves"*, 2026-08-17); the superseded
inference is kept struck-through beside it with both dates. Nothing else in the
file moved, no machine-checkable subject was edited (see §2.2's last paragraph on
`pipeline/canon.yaml`), and $0 was spent: no render, no GPU, no voice.
