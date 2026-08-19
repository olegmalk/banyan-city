# The work ladder — 2026-08-19

**What this file is.** A standing answer to "what is the next runnable job, and
who consumes it", written so the queue never has to be re-derived from scratch by
whoever wakes up next. It exists because at 01:00 tonight the rtx5090 measured
**0 ready, 0 running, 0 backlog**, with autofill's own status reading
`backlog_empty` — *"the card idles until a lane files real work"* — while the
current cut carried **four slates**. Those two facts cannot both be acceptable,
and the second one is the answer to the first.

**The principle this file encodes.** *The episode cut is the consumer, and every
slate beat in it is a consumer-named runnable job.* A slate is not an absence of
work. It is the most precisely specified work in the project: a named beat, with
a written `done_when`, and nothing in the slot. When the card is empty and a cut
has slates, the queue was not out of work — nobody had translated the work into
jobs.

**How to read the rungs.** Each one names a consumer, a single variable, and a
pre-registered bar. `ONE SAMPLE` means one seed, one clip, one picture — looked
at and scored before anything scales. A rung with no consumer is not on this
ladder.

---

## Where things stood at 01:00 and where they stand now

| | 01:00 | now |
|---|---|---|
| rtx5090 ready/running/backlog | 0 / 0 / 0 | continuously fed since 01:06 |
| ep2 cut slates | 07, 09, 15, 19 | same four — with routes attached to all four |
| Mac farm | 3 idle | 5 plates drawn and scored |
| beat 19 blocker | "no plate exists" since 08-15 | **dead twice** — fruit aloft on 3 of 3 draws, then the plant solved by a composite init |
| i2v identity collapse | attributed to beat 11's plate | **attributed to one flag, measured** |
| Mac render durability | none — hand-scp only | `--collect` implemented; 18 stranded files recovered |

---

## THE FINDING THAT OUTRANKS EVERYTHING ELSE ON THIS PAGE

**`--image-crf 33` was destroying the conditioning image on every i2v job on this
card.**

`ltx_i2v.py:1072` round-trips the init still through libx264 at `--image-crf`
before it conditions anything. Two runs, byte-identical but for that integer:

| measure | crf 33 | crf 10 |
|---|---|---|
| f001→f002 face-crop step | **39.34** | **0.66** |
| ten largest interframe steps | the ten **earliest** | spread f14–f94 |
| face drift from frame 0 | 74.23 | 32.82 |
| background strip drift | 60.89 | 9.89 |
| motion by third | 8.24 / 0.43 / 1.45 | 3.00 / 0.51 / 2.95 |

At 33 the init is abandoned at the first denoising step — an adult man is a
different, younger person by frame 21. At 10 the same init holds for 121 frames
**and the performance survives** (eyes downcast → narrowed → fully closed, hand
travelling off the cheek). Evidence: `pipeline/jobs/ep2-b09-faceturn-0819.yaml`
and `ep2-b09-faceturn-crf10-0819.yaml`, both with appended verdicts.

**What this obliges, before any plate money is spent:**

1. **Beat 11 is not necessarily broken.** Its `status_override_0815` retired a
   passing verdict over *"total identity collapse away from the plate across
   f16–f21"* — the same window, now explained by a flag. Re-run before concluding
   anything about its plate. *(In flight.)*
2. **Beat 07's brand-new motion ran at 33** and is being re-run at 10. *(Running.)*
3. **"The b18 recipe holds a fruit and not a person" is refined, not overturned.**
   b18's init was degraded too; a macro of a fruit had little to lose.
4. **A plate cannot survive being compressed at 33.** Check the CRF before
   spending a rung on a plate for any beat whose motion collapsed.

**Stated limits.** This establishes that **33 is wrong**, not that 10 is right.
The optimum between them is unmeasured and does not need measuring before the
finding is used. A research lane is reading the upstream Lightricks/diffusers/
ComfyUI conditioning path; if there is a real conditioning-strength parameter, it
is a better lever than a codec round-trip and this result does not preclude it.

---

## The four slates

### Beat 07 — CONFISCATE
- **Blocked on:** was "no footage that a verdict lets into a cut"; the only 0817
  job declares `is_show_content: false`.
- **Moved tonight:** first-ever motion rendered, and a re-run at crf 10 is on the
  card now.
- **Next rung:** judge both takes against the bar `ep2-b07-point-motion-0819`
  pre-registered, and the flag question against `crf_addendum_bar`. FAIL-FROZEN
  matters more here than on beat 09: **on a pointing beat the point *is* the
  motion**, so an init held so hard nothing moves is fatal.
- **Do not** re-litigate the figure count. `figure_count_ruled_from_the_script_0817`
  removed the three-figure blocker: beat 07 needs **two** figures.

### Beat 09 — THE PAUSE
- **Blocked on:** the guard-cast call (R4, open) *and*, underneath it, an engine
  question nobody had asked.
- **Settled tonight:** the engine **can** move a face — a slow eye
  close-and-reopen over forty frames on a locked camera. And the init now holds.
- **Next rung:** *not* another motion clip. The plate lane's own `blocked_on`
  names the real one — reference-weight or a crop pass, to reach the 55 % head
  the bar demands (best measured: ~35 %). That is a recipe change and wants
  **ONE SAMPLE**.
- Both clips are `is_show_content: false` and barred from the cut by their own
  headers. **The slate stays a slate.**

### Beat 15 — GOOD LISTENER
- **Blocked on:** unknown until tonight — no 0817/0818 job existed, but a large
  0815 inventory does (lookup, long, twobeat, leaf, wave, remake…). *(A lane is
  inventorying and judging it now.)*
- **Likely shape of the blocker:** `done_when` needs **him and the sapling in the
  same frame**, and several ep2 plates are recorded as having no sapling at all.
  If that is it, the rung is a **plate**, not another motion reseed.

### Beat 19 — THE DROP
- **Was blocked on:** *"not renderable until the plate exists"*, since 08-15.
  `plate_requirement_0815` recorded that **every** plate we owned showed the fruit
  already lying in the grass — "exactly why the beat was blocked".
- **That blocker is dead.** Three draws tonight, **fruit aloft on all three**, Q1
  never fired. The hands went from gripping the stem to folded on his knees on a
  single edit (`both hands on his knees`) — the positive-placement law from beats
  05/10 holding a third time where the negative could not.
- **Still blocked on:** the plant. Three wordings produced a bead-strung vine
  every time, twice doubled; fruit count went 4 → ~8 → 3, never 1.
  **The wording ladder is closed at three rungs**, per this repo's own rule.
- **~~Next rung — named, costed, not fired:~~ FIRED, AND IT PASSES.**
  `ep2-b19-sapcomp-0819`, 3.8 s of GPU, $0, all eight clauses of the bar the
  parent plate had pre-registered. The rung as written above said "composite beat
  18's fig in at scale" and **both halves of that were wrong once the pixels were
  opened** — which is the value of the rung, not an objection to it:
  - the parent's four "fruits" are **violet faceted crystals on threads**, hung
    off two **bare twigs**. P1 and P6 fail by **class**, not by count, so
    subtraction reaches neither axis (`composite-init-pattern.md` §8 finding 2 had
    already recorded this from the other side: count and shape are one job).
  - beat 18's passing plate is an **extreme close-up macro** whose fig spans
    ~430px where beat 19's needs ~30px. An 18× downsample imports a smudge, and
    "detail at the wrong scale" is decal tell #5. It served as the **shape and
    colour authority** instead of as pixels.
  So the plant was **drawn**: `pipeline/beat19_drop_composite.py` clears both
  twigs into the plate's own field and draws one rooted stem, two wide oval
  cotyledons, one thin side-branch and one fig. **Four rounds were rejected by eye
  first, ~4.5 s each, no GPU.** Evidence, with the composite committed beside the
  output so the A/B can be made by anyone:
  `farm-out/ep2-b19-sapcomp-0819/`.
- **What that sample settles beyond beat 19 — read this before any composite
  rung:** **at 0.30 the composite carries GEOMETRY and does NOT carry MATERIAL.**
  The fig was composited at hue **272°, matte**, and came back at **309°,
  glossy**. 309 is where **beat 18's own plate landed (305)**, and that verdict's
  `honest_caveat` names the identical two deviations — "toward magenta rather than
  deep violet" and "heavily GLOSSY with a hard specular highlight". Two beats, two
  completely different instruments, same two deviations: **gloss and the magenta
  lean are animagine-xl-3.1's fig, not either beat's recipe.** `glossy` was in the
  negative, at the front of it, and arrived anyway — the positive-placement law
  firing a fifth time. Matte-vs-gloss is **R4 and already a founder card** (raised
  by b18's verdict, still open); this only turns it into one checkpoint fact to
  rule on once instead of a per-beat surprise.
- **Also killed, from the other side:** §9's "material half fails in the wide
  whole-body register" hypothesis. `FAIL-MATERIAL` was pre-registered here as the
  **most likely** outcome on exactly that argument, and it did not fire on a
  whole-body wide shot. §9's plate dependence is still unexplained, and shot
  register is now ruled out from both directions.
- **NOT A PICK.** No `plate_ack`, no promotion, no leaf, nothing in any cut. The
  slate stays a slate until the author says otherwise. Named, not fired: if matte
  is wanted the levers left are **strength 0.20–0.25** (8–10 of 40 steps instead
  of 12) or a **post-pass**; and this plate's motion wants `--image-crf 10`, not
  33.
- **Still open for the author:** `body_position`. Tonight's plates derive a low
  pose from beat 20's opening (both hands to a fig on the ground) and beat 14
  (which renders this character crouching). Written down so it can be overturned
  in one word for $0.

---

## Beat 14 — not a slate, but the ladder stops here too

`REVS[(14, 8)]` staged embarrassment in the body instead of naming it, after the
sullen read was settled as a **staging** property on three data points. Result:
**4 of 8, and the experiment did not run the test it was built to run** —
`hand behind head` did not bind at all, and the second hand went to the knee,
which P2 forbids by name.

The pre-committed stop **holds**: no r9, no ninth wording. But the reason is
sharper than the stop rule anticipated. The hypothesis (*a staged caught-out pose
will not read as caught-out*) was never tested, because the pose was never drawn.
What was measured is that **a booru-native pose tag does not bind at this
framing**, on a prompt already spending its authority on `from above, close-up,
hands and dirt large in frame`. The register question is **still open**, on a
compositional instrument — an inpaint mask or img2img init over the arm region,
or a reference pose. Same instrument r5's stop rule named from the other side.

**Guard, recorded in the file:** r8's P2 and P5 failures must **not** be folded
into the r6/r7 ladder. That ladder turns on P2 failing 3 of 3 to decide whether
`from above` costs the hands, and r8's P2 failure is caused by its own pose edit.
Counting it would corrupt the one measurement r6 and r7 were filed to make.

---

## Two tooling holes closed tonight

Both are the same species: **a mechanism that looked present and was not.**

**1. `mac_enqueue.py` never sent `--rev`.** `plate_scratch.py` merges
`REVS[(beat, rev)]` over `DRAFTS[beat]`; the filer only ever sent `--beat`.
Filing "beat 14 r8" would have returned the **base draft** — the r1 wording from
five rungs ago — with an r8 story attached and nothing in the console to say so.

**2. The guard I added for it checked the wrong machine, and fired the same
hour.** `known_revs` reads the *filer's* checkout; the job runs the *worker's*.
A beat-19 r3 was filed onto a macbook whose `git pull` had aborted on an
untracked png: local guard passed, remote refused, `rc=4 0.1s`. Now checked **on
the host that will run it**, per host, with that host's HEAD and the exact
`git pull` printed in the refusal.

> The 0.1 s is why it is worth guarding, not why it isn't. A *missing* rev fails
> fast and loud. The expensive version is a checkout stale by one commit, which
> **has** the rev key holding the **previous wording** — nothing refuses, a plate
> comes back, and it is scored as the rev that was commissioned.

**3. `--collect` was advertised in the docstring since day one and never
implemented.** Worse than not offering it: you read the usage block, believe
collection is handled, and it is not. Implemented; **first run pulled 18 stranded
files off macbook2** — including **three beat-11 plates nobody had ever seen**.
macbook1 and macbook3 returned 0, which is the control that makes the 18 mean
something: those two are git checkouts. **macbook2 is not a git repository**, so
nothing it drew could ever have been committed by any mechanism this project
owns. A third of the Mac farm had been rendering into a hole since setup.

Design: **additive only** (`rsync --ignore-existing`) — a collector that can
clobber can silently replace a scored artefact with a stale copy; and it **does
not commit**, because collecting and judging are different decisions and a
collector that auto-committed would put unjudged pixels in the tree wearing a
commit message.

---

## Appended 2026-08-19 by the b08 / crf-10 judging lane

### Beat 14 — PARKED by steward ruling

**Status: parked, veto-able in one line.** The best available footage is already
in the cut, and expression-staging polish is not the bottleneck — four slates are.
Beat 14 has now absorbed a crf-10 pair (`ep2-b14-motion-crf10-0819` and its
second seed) whose finding was that crf 10 *did not change* the beat and at the
second seed *cost movement*; that is the third independent measurement telling us
this beat's remaining gap is taste, not mechanism. **Revisit after the slates
close.** Nothing about this ruling touches the footage in the cut or any bar.

### Beat 08's identity blocker — PARKED until the hint-shape axis resolves

**Green-on-both, four rungs running.** Every beat-08 conditioning rung —
0.80/7px, 0.45/7px, 0.28/7px and now 0.45/**3px** — returned two green figures
with pointed ears, at scales almost three times apart and at a 58% difference in
ink. The cause is structural and not a matter of tuning: **a contour cannot say
which body an attribute belongs to**, so `green skin` enters the pooled embedding
and lands on both. Per-figure IPAdapter is the candidate and it is its own probe.

**It stays parked because it has nothing to attach to.** An identity lever needs a
figure whose outline is the model's own, and no rung has produced one yet. Order
is not a preference here, it is a dependency: **hint shape first, identity second.**

### What the two units just judged ADD and REMOVE

**REMOVED — the beat-08 stroke-weight rung.** Filed, run, scored, closed. It was
§8's pre-committed instrument and the only one of three needing no new code.
Result: the pose held (B1/B3/B4a/B4c/B5), B2 failed a fourth time as
pre-registered, **B4b regressed** — the arm ends in a fingerless wedge where rung
2 drew a hand — and **B6's negative test failed again with no movement at all.**

The finding is that the dial points the wrong way. Share of authored ink with a
strong render gradient within 3px, one instrument, nocontrol as the floor:

| frame | ink traced |
|---|---|
| nocontrol | 26.1% |
| 0.80 / 7px | 97.7% |
| 0.45 / 7px | 94.4% |
| **0.45 / 3px** | **98.3%** |

**Stroke weight is a PRECISION dial, not a strength dial.** A 7px bar is an
ambiguous ribbon the model may fill anywhere; a 3px line is one edge locus the
outline snaps onto. So **two dials are now bracketed by measurement and neither
yields a figure the checkpoint drew — the tracing is caused by the ENCLOSURE.**

**ADDED — the top rung on this ladder: a hint that does not enclose bodies.**
Consumer: beat 08's cut slot. One variable: hint CLASS, from closed contour to
**sparse skeleton** — joint dots and single-line limbs plus the board, no closed
outline anywhere. Bar: carried unchanged from rungs 1–4, with B2 still an expected
FAIL and **B4b needing a hand-sized mark at the end of the arm whatever the class**
(a 1px finger has now failed once). `author_b08_pose_hint.py` already solves the
pose geometry — the two-link arm from a fixed fingertip clearance, the shared foot
line, the stature ratio — so this is a **draw mode, not new maths.** Fallback if
it stalls: an early `control_guidance_end`, which needs code first
(`controlnet_plate.py` hardcodes 1.0 at lines 167 and 277 and exposes no flag).

**NOT added, explicitly: no fifth stroke value and no interpolated scale.** Both
axes are closed by measurement, and a fifth sample on a closed axis is the wording
ladder this file already forbids.

### What the crf-10 re-runs change about the crf finding above

The finding at the top of this page stands and is now confirmed **at its source**,
which needed no render: measured against the true init, the conditioning image crf
33 actually feeds the model has **29.4%** of its pixels off by more than 8 levels
on beat 17 and 5.2% on beat 18, against crf 10's **7.1%** and 0.3%.

**But it is not a global win, and the ladder should stop treating it as one.**

| beat | fidelity | the bar | verdict |
|---|---|---|---|
| 01 cold open | f120 from init **15.2 vs 65.7**; luma ends 84.8 vs plate 85.1, original blooms to 148.4 | G1 better — monotone over 85 frames, 0 shrinks | **PASS, cut-preferred** |
| 17 shake | f000 5.54 vs 6.42 | all five clauses; P2 narrow at 0.420 sat | **PASS, cut-preferred** |
| 18 tremble | f000 2.53 vs 2.77 | **FAIL-FROZEN** — interframe median 0.570 vs 5.956 | **FAIL, original stands** |
| 14 motion | — | unchanged; second seed cost movement | no change |

**The calibration, which is the durable part:** a 2.4x cleaner conditioning image
buys only a **14%** closer first frame, because diffusion and not the encode
decides what f000 becomes — while the motion cost ranges from nil to **-90%**. The
gain is small and bounded; the cost is large and **beat-shape-dependent**. On a
macro plate whose whole content is fine high-frequency movement, a cleaner init
gives i2v less to push off from and the shot stops moving. **So crf 10 is a
per-beat decision with a motion measurement attached, never a blanket re-encode.**

**Two cut swaps are named and NOT made** — they belong to the next demo assembly
and are veto-able in one line: beat 01 and beat 17 to their crf-10 takes. Beat 18
stays as it is.

### A bar clause three beats have now needed and none has ever had

Beats 17 and 18 have both been scored on action while **near-duplicate frame pairs
went unmeasured**, and beat 17's own verdict flagged the same blind spot on 0818,
0819 and again tonight. The next motion bar on any beat should pre-register **a cap
on the share of frame pairs under 0.5 interframe** — beat 18's crf-10 take would
have been caught by it at 18 of 120 against the original's 3, without needing a
judgement call.

### One process defect worth a guard, found three times tonight

All three crf-10 specs were derived from their crf-33 parents **including the
parent's `verdict`, `verdict_measured` and `pick` blocks**, with ids renamed
through the file — so beat 17's inherited `pick` block recommended *the crf10 id*
for a decision made before that job existed, and beat 01's inherited `sweep_summary`
tallied six seeds the job never rendered. Anyone grepping `verdict:` on a filed job
would have read a PASS that belonged to a different clip.

They are renamed rather than deleted in all three, because those numbers are the
crf-33 baseline and were reproduced here to within rounding — which is what
confirms both the provenance and the instrument. **The guard this wants is small: a
spec-derivation step should refuse to carry a parent's verdict/pick/sweep keys into
a child, or should rename them on the way through.** Cheaper than the third
occurrence.

### Rung 5 ran, and it CLOSES the rung this ladder added an hour ago

The sparse skeleton was filed, rendered and scored the same night. **It failed
every composition clause and the frame drew the condition**: the shoulder bar and
its joint dots came back as a luminous cross with orbs on each figure's chest,
the leg bones as a glowing slab (guard spine column luma 212.3 against a 165.4
surround). *Against myself:* averaged over all the ink the brightness enrichment
matches the nocontrol floor, so the blanket version of that claim is not made —
the effect is localised to strokes that landed inside a figure.

**The reason reframes the whole four-rung ladder above it:
`xinsir/controlnet-scribble-sdxl-1.0` is a SCRIBBLE net.** Scribble conditioning
means *these lines are lines in the picture*. A closed contour is readable as an
object boundary — which is why the contour rungs held the staging and traced the
silhouette, and why a thinner stroke bound *tighter*. A medial-axis skeleton is
not a boundary, so the net drew it. **The enclosure was not a quirk to tune away;
it was the only thing this net could read.**

**So the top rung this file added is REMOVED, having been run.** Three axes are
bracketed by measurement — scale, stroke weight, hint class — and the space is
characterised: *any hint this net can read is a hint it traces; any hint it cannot
read it ignores or draws.* No setting yields a model-drawn figure inside an
authored composition. **Do not file a sixth hint variant.**

**ADDED in its place, as RESEARCH and not as a render:** does an SDXL-compatible
**OpenPose/DWPose** ControlNet exist, can its weights reach a box running
`HF_HUB_OFFLINE`, what is its licence, and **is its preprocessor the
`lllyasviel/Annotators` landmine this route has avoided by drawing hints with
PIL?** A pose skeleton is the right instruction and the wrong net. Per the
research-before-solving directive this is answered outside the repo before any
spec exists — and a hand-authored skeleton needing no annotator is the one
genuinely reusable thing rung 5 leaves behind.

**Beat 08's identity blocker is UNPARKED as a question, though nothing is filed.**
The parking order was "hint shape first, because an identity lever has nothing to
attach to on a figure whose outline is not the model's own." That reason is spent:
the axis is closed and no outline was freed. Identity now sits beside Route A's
plate campaign as the beat's two open routes, and whoever takes either should know
geometric conditioning on this net will not help.

**Unchanged and worth keeping visible:** rung 2 (0.45, 7px, contour) is still the
best frame beat 08 has produced, and a hand-authored contour is still the only
mechanism that has ever put this beat's pointing arm on the guard.

---

## Standing rules this ladder runs on

- **Never leave the card empty while a runnable job exists.** If nothing is
  filed, the ladder was not read.
- **ONE SAMPLE per recipe change.** One seed, looked at, before anything scales.
- **Pre-register the bar in the spec before the pixels exist**, with the FAIL
  modes named — and report every one of them, fired or not. Naming the most
  likely outcome in advance is what makes it meaningful when it turns out wrong
  (`FAIL-COLLAPSE-UNCHANGED` was named as most likely; it did not fire).
- **One variable per rung**, and prefer to make that a fact about the file:
  derive the new spec from its parent programmatically rather than retyping it.
- **Three rungs on one axis closes the wording ladder.** The next instrument is
  compositional, and it gets **named**, not fired.
- **The positive places what you want; the negative does not.** Four times now on
  this checkpoint, a defect the negative forbade arrived because the positive left
  it vague.
- **Taste is R4.** Bars, tradeoffs, routes and staging that applies a ruling are
  the steward's. Picks, promotion and `plate_ack` are not made in a job spec.

---

## Appended 2026-08-19 by the beat-07 judging lane

### BEAT 07 IS THE FIRST SLATE WITH FOOTAGE A VERDICT LETS INTO A CUT

**Both takes PASS.** The rung this ladder set — judge them against
`ep2-b07-point-motion-0819`'s pre-registered bar — ran: all 97 frames of each,
opened consecutively, plus native 704x1280 reads. M1–M4 all pass on both, first
attempt, and **F2 (the goblin points), the pre-registered most-likely failure,
never fired.** The guard raises his own arm at f050, the index finger lands on the
goblin's collar by f055, held to f096, measured at his own shoulder so no camera
move scores as the action.

**So the engine question open since 08-15 is answered YES:** a gesture binds to
the GUARD once both figures are fixed by an init. Text-to-image put the arm on the
goblin 3 of 3 and could not aim a point in 12 of 12 stills. i2v did both in one
seed. `FAIL-FROZEN` mattered more here than on beat 09 and did not fire either.

**crf 10 is the cut-preferred take, and it is this flag's first clean win.**
Background strip drift 5.43 against 36.41 — the crf-33 field visibly boils —
f001→f002 steps 4.78→1.05 (guard face) and 5.74→0.84 (goblin), and f021 renders a
hand where the parent draws a mitten. It cost **23%** of whole-frame motion and
kept **100%** of the gesture: the arm lifts *earlier* (f045 vs f050). That
sharpens the ladder's per-beat rule with a mechanism rather than overturning it —
**a gross whole-body gesture on a locked camera has enough authored motion that a
cleaner init does not starve it**, where beat 18's fine high-frequency tremble
did. The near-duplicate clause this ladder asked the next motion bar to carry was
pre-registered and reported: **0 of 96 pairs under 0.5 interframe in both takes.**

**Named, not made:** beat 07 → its crf-10 take in the next assembly.

### The slate's blocker MOVED, and the new rung is filed and running

Beat 07's `done_when` is met clause by clause by the crf-10 take. What is left is
**the plate: it dresses the SCAVENGER in the guard's own pale wrap tunic and white
sash.** Two men in one uniform read as two officials, and a CONFISCATE beat has to
read as an authority pointing at a scavenger. This lane does not overturn the
earlier lane's recorded judgement that the plate's three faults block a cut; it
**narrows the blocker from three to one** and leaves promotion where it belongs.

The cause is this repo's own positive-placement law for the **fifth** time: rung B
sends `a crouching goblin with green skin` — a noun phrase with one attribute and
**no garment at all** — so the only clothing terms in the prompt are the guard's
and they land on both men. **`ep2-b07-scavcostume-0819` is filed and running on
the card** (which measured 0/0/0 when this lane started): one variable, the
scavenger gets a garment bound inside his own noun phrase by the same grammar law
rung B used on `green skin`. `patched tunic`, **not** the canon `patchwork cloak`
— that em-dash costume list is gone from the goblin beats by r8's inherited
decision and is another lane's to re-add, and `patchwork cloak` climbs onto his
head 4 of 4 on this checkpoint. Measured on the real CLIP before the spec existed:
70/77 pos, 58/77 neg, zero faults, nothing dropped, parent at its recorded 65/77
as the control.

**The derivation guard this ladder asked for an hour ago now exists and fired.**
`pipeline/derive_b07_scavcostume_0819.py` refuses to carry a parent's
`verdict`/`pick`/`sweep` keys and names what it dropped — the parent's
`verdict_0819` block, recorded only as `keys_refused`. It also holds the argv to
**36 of 42 tokens byte-identical** to the parent, so "one variable" is a fact
about the file rather than a claim.

### BEAT 15 IS NOT A PLATE RUNG THIS LADDER CAN SPEND — §6, and it is already owned

Two findings, and either one is enough to stop a plate sample:

1. **STEWARDSHIP.md §6 is LIVE on beat 15.** Its staging was rewritten on
   2026-08-17 with four other beats (12, 13, 15, 19, 20) and
   `leaves/002b-t0-c.yaml` records `approval_status: NOT YET READ BY HIM` —
   "§6 therefore forbids voice synthesis, footage render and episode assembly
   FROM THESE FIVE BEATS until he does", repeated at node.md:204. Rendering the
   **old** staging instead is not the way round it: that is asking him to bless an
   inference his own next-day ruling replaced.
2. **The rung was already run tonight by the b15 lane** (`ce4ba822`): 24 judged
   artifacts, the blocker found to have never been the acting, **two** MPS draws,
   r1 at 6 of 7 with all seven fail modes silent, the wording ladder closed at two
   rungs, and the next route named as a composite (r1's frame + `ep2-b12-tightB`'s
   leaves). It filed a plate *publish* and no footage, for the §6 reason above.

**Defect worth one line:** `review/ep2-picks/b15-0819-verdict.yaml` does not parse
— line 59 carries `` `beats: [12, 13, 15, 19, 20]` `` unquoted inside a plain
scalar, so `yaml.safe_load` dies at column 35. Nothing globs that directory, so no
builder is broken, but the file cannot be machine-read. It is that lane's file.

### Owner map as this lane found it

| rung | state |
|---|---|
| beat 07 judge both takes | **DONE** — both PASS, verdicts appended, cut-preferred named |
| beat 07 next rung | **FILED AND RUNNING** — `ep2-b07-scavcostume-0819`, this lane |
| beat 15 plate | owned (b15 lane, run tonight) **and** §6-blocked for footage |
| beat 19 composite | owned (b19 composite lane) — and §6 applies to beat 19 too |
| beat 08 hint / identity | owned; hint axis closed by measurement, next step is research |
| beat 09 plate | the b09 plate lane's own `blocked_on`; judging owned elsewhere |
| beat 14 | PARKED by steward ruling until the slates close |
