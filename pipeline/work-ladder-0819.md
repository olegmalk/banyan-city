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
  rung.** *This bullet was written wrong an hour earlier and is corrected here,
  dated 08-19, by the next sample in the same lane. The retracted version claimed
  the fig went from a composited 272° to 309° and that this reproduced beat 18's
  305° — "gloss and the magenta lean are animagine's fig, not either beat's
  recipe". **The hue half of that was my own measurement error** and the full
  retraction with the numbers is in `ep2-b19-sapcomp-0819.yaml`. In short: the 309°
  was a circular mean over a **box**, not over the fruit, and 39% of the pixels in
  it were **his cloak's shadow on the grass** at 11°, which dragged a 277° body to
  a "308.5°" mean. On the body the hue barely moves — composite 271°, 0.30 = 277°,
  0.22 = 279°. The convergence with beat 18's 305° was a coincidence between a
  contaminated number and a real one; **beat 18's own findings are untouched**, what
  is withdrawn is my claim to have reproduced them.*
  **The corrected statement, which is narrower and more useful:** at 0.30 the
  composite carries **geometry AND hue**, and does **not** carry **matteness**.
  Measured properly — p99−p50 of luminance over the *segmented body*, so a small
  bright spot on a dark body reads as a wide spread — the composite's matte fill is
  **4.3** and the 0.30 output is **71.8**: a real specular, correctly caught by
  `FAIL-CRYSTAL`. `glossy` was in the negative, at the front of it, and arrived
  anyway — the positive-placement law firing a fifth time.
- **And the specular is REACHABLE, which the wrong version implied it was not.**
  `ep2-b19-sapgloss-0819` changed **one key — strength 0.30 → 0.22** (12 → 8 of 40
  steps), same seed, same init sha, same words, and the spread fell **71.8 → 23.9**
  — an ordinary **cel shadow terminator**, i.e. the house dialect. The drawing
  survived (no `FAIL-PASTE` even at 8 steps) and the 0.30 sample's one partial, the
  extra leaflets at the leaf junction, **resolved**. So **gloss here is a mid-sigma
  effect and strength reaches it** — the first mechanism anyone has attached to
  §9's material half. Two samples, 6.7 s of GPU total. *Predicted outcome was
  "unchanged", on the argument that a specular is fine high-frequency detail that
  the low-sigma tail adds in both renders. Wrong: in this dialect the highlight is
  a large hard-edged lobe over a third of the fruit — a low-frequency shape
  decision.* Evidence at 3× and 8×: `farm-out/ep2-b19-sapgloss-0819/`.
- **Matte-vs-gloss is still R4 and still open** (raised by b18's verdict). Nothing
  above closes it. **Which of the two plates ships is a taste call, not a defect
  call** — 0.22 is matte and simpler, 0.30 is glossier with more incident at the
  junction, and the canon line says "matte violet fig". Both are committed side by
  side so it can be settled on pixels in one look.
- **Also killed, from the other side:** §9's "material half fails in the wide
  whole-body register" hypothesis. `FAIL-MATERIAL` was pre-registered here as the
  **most likely** outcome on exactly that argument, and it did not fire on a
  whole-body wide shot. §9's plate dependence is still unexplained, and shot
  register is now ruled out from both directions.
- **NOT A PICK.** No `plate_ack`, no promotion, no leaf, nothing in any cut. Beat
  19 now has **two passing plate samples and zero picks**, and the slate stays a
  slate until the author says otherwise. The "named, not fired" lever from the
  first version — strength 0.20–0.25 — **was fired and is the bullet above**; the
  post-pass is no longer needed for gloss. Still named, not fired: this plate's
  motion wants `--image-crf 10`, not 33, on the evidence of
  `ep2-b09-faceturn-crf10-0819`.
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

---

## Appended 2026-08-19 by the beat-19 drop lane

Two rungs fired here: the plate PICK the composite lane left open, and the first
motion take off it. Both are committed with their pixels.

### BEAT 19'S PLATE IS PICKED — 0.22, by derivation, not by taste

The composite lane left beat 19 with **two passing plates and zero picks** and
filed the choice as R4, on the reading that "matte-vs-gloss is still open".
**It is not open — it is written down, and in three places that all predate both
samples:**

1. **`matte` is in the fig clause itself**, and the clause travels with the
   subject rather than the beat: `authored_b01_scale_0816` and both 08-17 rungs
   carry *"one small deep purple-violet fig, green at its neck, **matte**,
   growing on its thin stem"* (`wave-drafts.yaml:518`, `:573`). Live wording, not
   an archived round.
2. **Gloss on this exact fruit has been a DEFECT here for five days.**
   `wave-drafts.yaml:225` — *"the fruit came back GLOSSY … where the canon is
   matte with no shine at all"*; `:242` — *"TOO GLOSSY … nothing about it reads
   matte"*, after which gloss was banned by name and a whole reference set was
   built so *"the fruit tells it the colour AND THE MATTE SURFACE"*.
3. **`canon.yaml`'s fig subject reaches beat 19 explicitly** — `ep2-fig-purple`,
   `scope.beats: [19, 20]`. It rules colour and is **silent on finish**, and
   silence is not contradiction. Nothing anywhere prefers a specular.

**Picked on the pixels, not the label** — "sapgloss" names *the job that went
after gloss*, not the glossy output, and getting that backwards was a live risk.
At 8×: 0.30 carries a hard-edged bright lobe over a third of the fruit and reads
**wet**; 0.22 carries one soft terminator, i.e. an ordinary cel shadow. The
instrument agrees (p99−p50 over the segmented body: 71.8 → 23.9) and is the
filter, not the decision. **Cost of the pick:** 0.30's extra incident at the leaf
junction, which canon does not ask for — and 0.22 also loses the parent's one
PARTIAL, the junction leaflets. **Veto is one word for $0:** the other plate is
already rendered, committed and passing, so "glossier" re-picks it with no GPU.
Recorded in `ep2-b19-sapgloss-0819.yaml` `pick_0819`.

### THE MOTION TAKE OFF IT FAILS, AND IT FAILS BY ANIMATING BEAT 20

`ep2-b19-dropmotion-0819` — the b14 crf-10 LTX recipe cloned whole, 121f
704x1280, 264s of GPU, $0. **My prediction was pre-registered and wrong in the
useful direction:** I argued the engine would not move a 32×43px object by less
than its own height (F-FROZEN / F-IMPERCEPTIBLE). It produced plenty of motion
and **pointed it at the wrong subject.**

- From ~f025 the sapling **thickens and elongates**. At f030 **his right hand
  leaves his knee**. f039–f065 that hand **rests on the plant's leaves**. By f088
  the sapling is a **sprawling prostrate plant — four or more large leaves, a
  horizontal runner, and TWO figs** — held to f120.
- **The figs reach grass level because the plant lies down.** There is no
  detachment event anywhere in the clip.
- **So the engine rendered beat 20's line inside beat 19** (*"picks the fig up
  with both hands"*), with no hand action in the prompt, both hands on knees in
  the plate, and `fruit in his hands` as the FIRST tokens of the negative.
  **Positive placement beats negatives for a sixth time.**
- `F-PLANT-REVERT` fired hardest: two leaves → four+, one fig → two, upright stem
  → runner. That plant cost four drawing rounds and a closed three-rung wording
  ladder, and **motion undid all of it in 90 frames.** No beat-19 job had ever
  checked the count under motion, which is why the clause existed.
- **crf 10 did not freeze this beat.** Amplitude was never the problem, so the
  crf-33 A/B this spec pre-registered is **CANCELLED by its own condition** — it
  was named only if a freeze fired. Worth stating: a pre-registered follow-up run
  unconditionally is how a lane burns a card on a closed question.

Evidence, both sheets committed: `farm-out/ep2-b19-dropmotion-0819/`.

### Three instrument findings, because two of them overturned the numbers

- **A framing bug caught BEFORE the GPU, by measuring the plate against the
  recipe.** 832x1216 → 704x1280 cover-crop discards 81.7 original px **per
  side**, and beat 19's fruit lives at original x 743..773. **A centred crop
  keeps 8 of its 32 columns** — the subject of the beat, cropped out. Fixed with
  `--anchor right` (default `center`, so every earlier copy reproduces byte for
  byte) and hard-guarded by a pre-render `assert_framing.py` that refuses if the
  fruit is not aloft, in frame and clear of the body zone. Both were run against
  the real plate here: PASS right-anchored, **REFUSE centred**.
- **M2 read PASS on all three thresholds and is an artifact** — 114px of descent,
  bottom edge y1059, 0.0px of movement over the last 12 frames, every clause
  satisfied **by the plant migrating**. Reported FAIL. This is the rule's own
  case: *a metric agreeing with me is not a sample.*
- **M5's raw [4,4] horizon shift is not a camera move.** dx = 0 everywhere, and
  the vertical fit is **+3px on the low-contrast horizon band but −1px on the
  high-contrast fence posts** — region-inconsistent, so it is the field
  **re-inking**, the same thing that gave beat 06 depth 0.516 with zero human
  motion. Reported PASS with both numbers: filing a camera fault that does not
  exist is its own defect.

### A bar clause the ladder should carry forward, and one it should narrow

- **`M3` was ASYMMETRIC and the founder's ruling is not.** It was written as *no
  FRUIT pixel inside a static body box measured at f000*. **His arm left the
  box**, so the clause was structurally unable to see **body-onto-fruit**
  contact — which is the contact this clip contains. The next motion bar on this
  beat needs a **per-frame body mask** and a symmetric clause: no contact in
  either direction, in any frame.
- **The "share of pairs under 0.5 interframe" clause this ladder asked for is the
  wrong instrument on a near-still beat**, and the tracker's self-test said so
  *before* the clip existed: a **perfect** 32px fruit drop over a frozen
  background moves whole-frame interframe by **0.056** and would fail the floor.
  Threshold left as filed and its FAIL recorded as uninformative. **Generalise
  it: a near-still beat puts its floor on the TRACKED SUBJECT, never on the
  frame.**

### FOR THE ASSEMBLY LANE — beat 19 is still a SLATE, and it carries a trap

- **Nothing to cut.** No pick, no plate_ack, no leaf, no lineage entry. The
  beat's blocker **moved** rather than cleared: no longer *"no plate exists"* —
  the plate exists and is picked — but ***"no motion recipe has produced a
  fall"***. **Superseded later the same day, and only in its second half:
  `ep2-b19-dropcomp-0819` is a fall** — 5.0000s, $0, composited, bar 8 of 8 (see
  the rung below). Still nothing to cut: **no pick, no plate_ack, no leaf, no
  lineage entry**, and the clip contains **no notice**, which `done_when`
  requires. The blocker is now *"the beat's third action is not in any clip, and
  whether a 48px drop is the beat is R4."*
- **NEVER LET AN ASSEMBLER PALINDROME BEAT 19.** `render_t3.py:616` reverses any
  clip whose slot outruns it (`dur > cdur + 0.05`, `cdur <= 16.0`). Beat 19's
  slot is 1:34–1:39 = **5.000s**; a 121f/24 clip is **5.0417s** (ffprobe). So it
  does **not** fire — **by 0.09s**. That margin is the entire safety of an
  **irreversible** action: reversed, this beat shows a fig **flying back up onto
  a stem**. Any retime, trim or shorter re-render past 5.09s turns it on
  silently. Beat 19 is the first beat in the show whose action a viewer can see
  run backwards, and the assembler has no notion of that.
  **CLOSED IN THE TOOL, 2026-08-19 (commit below): the assembler has a notion of
  it now.** The default fill for footage is a **last-frame HOLD**, not a
  palindrome, so beat 19's safety no longer rests on 0.09s of frame-count luck —
  a retime past the threshold now freezes the fig where it landed instead of
  flying it back up onto the stem. The palindrome survives only as opt-in
  (`loop_fill: pingpong` in a clip's own sidecar), which **no clip, spec or leaf
  in this tree writes**. The warning stays on this page because it is the reason
  the fix exists, and because it is still true of the **published 0819c cut**.

### FOR THE NEXT ASSEMBLY — the palindrome fix is in the tool and **READY**, nothing is republished

> **What changed.** `render_t3.render_beat` used to fill a slot that outran its
> clip by playing the footage forward and then **reversed** (loop cycle 005 —
> right that a plain loop restart is a hard jump-cut, wrong that a reversal is
> the cure: a reversal has no seam because it runs time backwards). It now plays
> the clip **once** and freezes its final frame for the remainder
> (`tpad=stop_mode=clone`, padded 0.2s past the slot so `-stream_loop` can never
> wrap to frame 1). A hold reads as the beat **landing**; a reversal reads as
> **time flowing backwards**. Held stills are unaffected — they are still
> *stretched*, per the founder's 2026-08-07 ruling.
>
> **Measured on a bench rebuild of 0819c** (same `--clips
> review/ep2-demo-0819c/sources`, scratch `--out`, published cut untouched). The
> branch fired on exactly the 8 beats the audit named — **1, 3, 4, 6, 10, 11,
> 17, 18** — and prints a line now instead of nothing. Picture-region
> frame-to-frame change **inside the fill window**, before → after:
>
> | beat | fill | OLD moving pairs | NEW moving pairs |
> |---|---|---|---|
> | 01 | 4.31s | 103 / 104 | **0 / 104** |
> | 04 | 2.03s | 16 / 49 | **0 / 49** |
> | 06 | 4.69s | 105 / 113 | **0 / 113** |
> | 11 | 0.44s | 9 / 11 | **0 / 11** |
> | 17 | 0.57s | 12 / 14 | **0 / 14** |
> | 18 | 5.82s | 137 / 140 | **0 / 140** |
> | 03, 10 | 0.24s, 0.09s | 0 / 6, 0 / 2 | **0 / 6, 0 / 2** |
>
> Beat 06 by eye: the board goes up and **stays** up, where the published cut has
> it go up, down, up. Beat 01: the fig ripens to purple and **stays** purple,
> where the published cut un-ripens it to green. Beats 3 and 10 were already
> invisible in both (0.1–0.3s of fill) — the audit said as much.
>
> **What is NOT done, and is not this lane's call.** No cut is republished and no
> page is edited: 0819c on the review surface still contains all 8 palindromes,
> and its own page documents them. The first assembly run after this commit gets
> the holds for free. Three comments elsewhere now describe the old behaviour and
> belong to their own lanes: `beat19_drop_animate.py:137-139`,
> `derive_b20_motion_0819.py:465`, `derive_b12_stillmotion_0819.py:368` — each
> argues a frame count from the palindrome threshold, and each argument is now
> moot rather than wrong.

### The rung this lane recommends — composite the fall, $0, no engine — **FIRED, 2026-08-19, and it passed**

> **`ep2-b19-dropcomp-0819` — the rung below is no longer a recommendation, it is a
> clip.** 704×1280, **120 frames = 5.0000s**, crf 18, **$0, no GPU, 44s of CPU**,
> deterministic. Tool: `pipeline/beat19_drop_animate.py`. Evidence, six images plus
> the mp4 and a sha manifest: `farm-out/ep2-b19-dropcomp-0819/`.
>
> **The bar was written before the tool and scored 8 of 8**, plus one clause the
> build itself added. The numbers that matter:
> - **max |frame − plate| OUTSIDE the fig's path corridor, across all 120 frames: 0**,
>   and **f000 IS the cropped picked plate byte for byte**. That is the whole point of
>   the instrument: his pose, his hands, his face, both cotyledons, the stem, the
>   side-branch and the horizon are *structurally incapable* of changing, and the fig's
>   **stalk stays on the branch**, which is what a picked fruit leaves behind.
> - fall descent per frame `0.32 0.96 1.60 2.24 2.88 3.53 4.17 4.82 5.46 6.11` —
>   strictly increasing (constant acceleration), no jump >12px, no reversal.
> - **48px of descent, 29px RIGHT, 46° of rotation**, so it ends lying on its side with
>   its stalk end up. The rotation is doing more work than the travel.
> - **leftmost fig pixel over the whole clip x 609 against a Z-BODY edge of x 500 —
>   109px of margin on EVERY frame.** It only ever travels right, so the founder's
>   no-contact ruling is satisfied *structurally*, not luckily.
> - **exactly one violet blob in all 120 frames** — the clause the i2v take failed
>   hardest, here impossible to fail.
> - **5.0000s against a 5.000s slot**: the palindrome branch cannot be reached.
>
> **What it does NOT contain, said plainly: he does not notice.** `done_when` asks for
> the fall, the landing *and* the notice, in that order; this has the first two, exactly,
> and the third not at all. A composite can move the fig and nothing else, and animating
> his head would destroy the one property that makes the clip trustworthy. The last
> **2.792s is an honest still**. **Still a SLATE** — no `plate_ack`, no leaf, no lineage
> entry, nothing in any cut. **What changed is the blocker:** it was *"no motion recipe
> has produced a fall"*, and a fall now exists at $0 with every founder ruling met.
>
> **FOUR ROUNDS WERE REJECTED BY EYE FIRST AND THREE OF THEM HAD A FULLY GREEN BAR.**
> Read this before any composite rung, because it is the generalisable half:
> 1. a **horizontal clone** for the hole behind the fig — this lane's own instrument
>    from `beat19_drop_composite.py` — sat up to **29 levels off the true background**
>    and covered a ring the fig never occupied; the moment the sprite moved half a pixel
>    a **ragged bright fringe** appeared down its left side on f024 *and nowhere else*.
> 2. **row-wise interpolation** replaced it and produced an **olive rectangle of bands**,
>    because its endpoint test was "not thin structure" and the pixels 4px to the fig's
>    upper left are **his cast shadow** — broad, and therefore not thin.
> 3. the **harmonic solve** that fixed the bands came out **dead flat** (interior std 0.1
>    against the field's 4.3, a fig-shaped blob 9 levels off its surroundings) because a
>    2px safety gap left the solve **with no boundary to be anchored to at all**. *A
>    Dirichlet condition has to touch the thing it conditions.*
> 4. the centre was solved from the bottom edge with a **rectangle's** bound,
>    `hh·cos + hw·sin`, instead of the **ellipse's** `√((hw·sin)² + (hh·cos)²)` — which
>    overstates the extent by **8.4px at 46°**, so the landed fig **hovered over its own
>    contact shadow** with clear grass between them. **Every bar clause was green on that
>    frame.** B5b — *read the fig's own alpha footprint against the measured grass line* —
>    was added afterwards so the next one cannot be.
>
> The lesson is the same one three times: **a bar written on the target cannot see the
> code missing the target**, and a metric on the *background* cannot see a defect in the
> *object*. Open the pixels at 6–9x, and open two consecutive frames, not one.

Every precondition is already met: **the camera is locked**, the fig is a
**32×43px rigid object**, the plate is picked and passing, and this lane already
owns `pipeline/beat19_drop_composite.py`, which **drew** that plant. A sprite
translated down a parabola over the static plate produces a physically exact
32px fall into the grass beside him and **cannot produce any of the three faults
that killed this take** — the plant cannot revert, he cannot reach, and a second
fig cannot appear, because nothing is being re-generated. It satisfies his ruling
exactly. **Not a fifth wording:** the failure is *subject attribution*, and this
repo now has five rungs saying words do not fix that (tonight's b08 finding
included — *"five rungs of geometry could not say which body an attribute belongs
to; a reference image behind a mask can"*).

**The author's card underneath all of it:** whether beat 19 is filmable **wide**
at all. His knee-height canon caps the fall at ~30cm and the board requires the
sapling and the scavenger in one frame, so the drop is **~32px of a 1280-tall
frame however it is produced**. Story question, not an engine one, and this clip
is the first evidence for it. **`ep2-b19-dropcomp-0819` is now the best evidence
for it**, because it is the version with *every engine defect removed*: if a 48px
drop does not read as the beat there, the framing is the reason and nothing else
is left to blame.

### TOOLING RUNG — `box_autofill.py` reports `backlog_empty` from a junk directory when run on a Mac

**Not hypothetical: it has done it four times, on three dates, and the card was
hungry each time.** `pipeline/box_autofill.py` and `box_runner.py` both do
`os.makedirs(os.path.join(root, sub))` with `root = r"C:\banyan-queue"`. On
POSIX that path is **one filename containing backslashes**, so the call creates a
literal directory named `C:\banyan-queue` **in the CWD** with real `backlog/`,
`ready/`, `running/`, `done/`, `failed/` inside it. `json_names()` then does
`os.listdir` on that local tree, finds nothing, and the tool reports:

```
status: backlog_empty
why: "HUNGRY: ready holds 0.0 min, under the 45 min floor, and the backlog has
      nothing eligible to file … NOTHING WAS INVENTED"
```

**Every word of which is false about the box, and nothing in the output says it
never talked to it.** The `except OSError` net cannot fire, because the junk
directory genuinely exists after the first run. Evidence is still on disk at the
repo root — `C:\banyan-queue/autofill.log` carries 2026-08-17 ×2 and 2026-08-19
×2 (`07:32:32Z`, `07:32:50Z`), and it shows up in `git status` as an untracked
`C:\banyan-queue/`.

**It is worse than one-directional, and this lane hit the other half too.** The
same file's `status()` and `verify_deployed()` paths use `ssh()`, so they are
correct only **off**-box. Run `--status` **on** the box and it tries to ssh to
`rtx5090` from `rtx5090` and dies after 60s (`subprocess.TimeoutExpired`,
verified today). **So neither invocation is fully correct:** the fill path is
box-only and silently lies off-box; the status path is Mac-only and hangs
on-box.

**The guard this wants is small and has two directions:** the fill path refuses
unless `os.name == "nt"` (or the root resolves to a real absolute path on this
platform); `--status` / `--verify-deployed` refuse when they are already on the
worker they would ssh to. Cheaper than the fifth occurrence, and this is a
**no-artificial-delay** defect, not a cosmetic one — a false `backlog_empty` is
exactly how a runnable job sits while the card idles. *(How this lane worked
around it: file with `box_enqueue.py --backlog` — which correctly ssh's for
everything — then run the fill **on the box over ssh**. Promotion was immediate
and the render started with no wait.)*

### TOOLING RUNG — `box_enqueue.py` has no idempotency check, and it re-rendered a finished job

**Same night, same lane, a second tooling hole — and this one spent GPU.**
`ep2-b19-dropmotion-0819` **ran twice**: `…-1787128259` at 08:30 (the run the
verdict is scored on) and `…-1787129173` at 08:46:22, **seven minutes after the
first landed in `done/`**. 264s of GPU on a question the first run had already
answered.

**Mechanism, established from disk rather than inferred:**

- The box's `autofill.log` reads `BACKLOG EMPTY` at **every** tick across the
  window — 08:36, 08:39, 08:42, 08:45, 08:48, 08:51. **No fill event at 08:46**,
  so the duplicate never came through `backlog/`.
- **No `.SUPERSEDED` parked file.** `box_autofill.plan_fill` *does* dedupe —
  line 418 skips any backlog entry whose id is already in
  `ready/`/`running/`/`done/`/`failed/` and parks it — so it never saw this one.
- Therefore the duplicate went **straight into `ready/`**, which is exactly what
  `box_enqueue.py <spec>` does when `--backlog` is omitted, and the runner
  claimed it.

**The dedupe lives one layer downstream of the tool that needed it.**
`box_enqueue`'s only collision guard is `output_path_problems` / payload-path
claims, and that compares against **LIVE** jobs only (`ready/`, `running/`). The
first run was already in `done/`, so nothing objected. Eleven reasons the queue
can refuse a job, and *"this exact job already ran"* is not one of them.

**Why a second call happened, stated plainly because the tool half is the part
worth fixing:** this lane was interrupted and re-logged twice while the render
was in flight, and a resumed copy re-ran the file-and-fire step. That is the
**"resumed agents fork"** hazard — a resumed agent is a NEW copy — meeting a tool
with no idempotency check. The agent-side mistake is ordinary and will recur;
what turned it into wasted GPU is that nothing refused it.

**THE RUNG:** an idempotency refusal in `box_enqueue`. **Same job id — or better,
same spec sha — already present in `ready/`, `running/`, `done/` or `failed/` ⇒
REFUSE**, with an explicit `--again` to override for a deliberate re-run. Spec
sha is the stronger key: it also catches a re-file under a nudged id, and it
lets a genuinely edited spec through, which an id check would block. Cheap, and
it is the same shape as the guard the crf-10 wave wanted (a derivation step that
refuses to carry a parent's `verdict`/`pick` keys) — both are *refuse the thing
that cannot be right*, at the one place that can see it.

**THE ONE THING SALVAGED, and it is worth having:** the two runs are
**byte-identical**. Same mp4 sha (`333ea495…`), same init, same sidecar, same
prompt and negative — two independent runs 16 minutes apart, each with its own
model load and its own libx264 conditioning round trip. **LTX i2v is bit-exact
reproducible on this box at a fixed seed**, which nobody had measured. Only
`bench-…jsonl` differs, because it records wall-clock and peak memory. Narrowly:
one spec, one seed, one machine, one weight set — it says nothing about
reproducibility across machines or torch builds. Written up beside the artifacts
in `farm-out/ep2-b19-dropmotion-0819/DUPLICATE-RUN-0819.md`, so a reader who
finds two completed job records for one id does not have to work out which
artifact they hold.

---

## Appended 2026-08-19 by the finish-line / assembly lane

### BEAT 09 IS THE HONEST SLATE, AND HERE IS EXACTLY WHY IN ONE LINE

**Both its clips are `is_show_content: false` because their init is a plate that
fails its own pre-registered plate bar on three named terms — head ~35% of frame
height against a 55% bar, a hand in frame at 12 of 12, the face reads adult at
only 5 of 12 — and a clip inherits its plate's cast defects frame for frame,
however well it moves.** That is not a judgement made after the fact; it is
written in both specs' own headers.

**The ladder's reading of this beat was right and is now sharper.** It said the
next rung is *not* another motion clip, and that the plate lane's own
`blocked_on` names the real one. It does — and the plate work is further along
than "reference-weight or a crop pass" suggests, because the two plate rungs
this beat has had **measured a direct conflict between the two instruments**:

| instrument | hair (near-black, cropped) | framing (head ≥55%) |
|---|---|---|
| Mac wording rung, 7 renders | **0 of 7** — brown and shaggy every time | 48–53%, and **56% at seed 20260820** |
| box IP-Adapter rung, 12 renders | **3 of 12** — reference conditioning reaches hair | **0 of 12**, 25–35%, *worse* than the rung it was correcting |

Reference conditioning wins the hair and pays for it in framing — its own
pre-registered fail mode, fired 12 of 12, "the refs depict two men at full length
in a field, and they dragged a close-up out to a medium". So **the two things
beat 09 needs are, on present evidence, bought with each other's money.**

### THE ONE DERIVABLE RUNG, FILED — AND A MECHANISM FOUND BY READING, NOT RENDERING

`plate_scratch.py REVS[(9,3)]`, filed on macbook1 as `mac-b09r3-0819-130617`.
**One token: `dark` → `black` in the hair clause.** This is not a new idea — it is
the sentence the b09 plate lane wrote and deliberately did not spend: *"the next
thing beat 09 tries is `black hair`, which is this checkpoint's own tag, instead
of `dark`. THAT IS THE ONE CHANGE THIS BEAT NEEDS AND THIS LANE DOES NOT SPEND A
FIFTH SEED ON IT — it is named, measured and left for the next lane."* Fired at
**seed 20260820**, which is not a second variable: it is the only one of the seven
whose head clears P3, and there is a committed, scored picture at that exact seed
and wording to A/B against, so the render differs from a file on disk by one token.

**And the 7-of-7 brown has a mechanism nobody had written down.** This prompt pair
has been **asking for `dark` hair and forbidding `dark` at the same time, at every
render.** The negative's last clause is `photorealism, 3d render, dark, night` —
`dark` is in there as a *lighting* term — and it has sat beside a positive saying
`dark cropped hair` since r1. SDXL's text encoder has no scoping: nothing
subtracts darkness from the light and not the hair. That is a far better
explanation of 7 of 7 than "this checkpoint will not draw black hair", and it is a
**prediction rather than a story**, because `black` appears in no negative.

**Why the existing guard missed it, which is the reusable part.**
`plate_scratch.py`'s clash check splits both strings on commas and intersects
whole chunks, so it compares `a guard man with dark cropped hair and wire-rim
glasses` against `dark` and finds nothing. **A token-level check over the same two
strings would have fired on day one.** Named as a guard worth adding; not built
here, one lane one variable.

### THE RUNG RAN, IT FAILED, AND IT TOOK MY MECHANISM DOWN WITH IT

**H2 fired.** `farm-out/ep2-b09-mac-plate-0819/09-the-pause-mac-plate-r3s1.png`,
137 s on macbook1, $0. The hair came back **mid-to-dark warm brown and shaggy for
the eighth time**, with the same pale swathe over the crown. Measured rather than
eyeballed — this beat has already had one eyeballed hue claim retracted — with two
independent masks over the top 30% of frame that agree:

| mask | r2s4 (`dark`) | r3s1 (`black`) |
|---|---|---|
| central band, darker half of pixels | mean luma **54.7**, RGB 63.9/51.9/45.3 | **61.1**, RGB 67.6/59.8/50.4 |
| share of that band under luma 60 | **41.1%** | **7.7%** |
| warm-pixel mask (R≥G≥B, luma<120) | mean luma **62.0**, p25 58.6 | **66.4**, p25 65.3 |

Not darker. Two agreeing masks say very slightly **lighter**. Near-black on this
checkpoint would be luma under ~40 and near-neutral; this is neither.

**So the mechanism I filed an hour ago is RETRACTED.** The prediction was that the
negative's bare `dark` was cancelling the positive's `dark cropped hair`, and the
block said in advance that `black` appears in no negative, which makes it a
prediction and not a story. `black` in the positive, with `black` nowhere in the
negative, still returned brown. It may be a real interaction somewhere; **it is not
what was holding beat 09's hair.**

**What survives, and it is the more useful half.** `brown hair` **has been in this
negative at all eight renders and brown hair arrived at all eight.** The positive
places what you want; the negative does not — seventh data point on this
checkpoint. And P3 **held** across the wording change (crown cropped, chin ~y690
of 1216, ≥56%), which confirms F3's claim that this seed's framing is a property of
the seed rather than of the exact words. P7's eyes were shut, pre-registered as an
expected fail at this seed. Five of seven, the same score as r2 with the same two
clauses failing. Unpre-registered and reported forward: the garment got *worse* —
the tan tunic and white sash render as a **white sleeveless vest with a bare
shoulder**.

**THE HAIR AXIS IS NOW CLOSED BY MEASUREMENT: eight renders, two wordings, the
unwanted colour negated throughout.** Per this file's own three-rungs rule the next
instrument is compositional, and it is already bracketed from both sides — the box
IP-Adapter rung reached near-black cropped hair at **3 of 12** and paid for it in
framing at **0 of 12** (25–35% against a 55% bar), its own pre-registered fail mode
firing because the refs depict two men at full length. **So beat 09's plate is a
REFERENCE-PLUS-CROP job: condition on the refs to get the hair, then recover the
framing with a crop pass rather than with words.** That is a build, it is named and
not fired, and it is where the plate lane's `blocked_on` pointed before any of
these numbers existed. `mature male` and the four-seed eye pick both wait on a
settled wording, and the honest statement after this rung is that **wording will
not settle it.**

### WHAT THIS RUNG DOES NOT DO, SAID BEFORE ANYONE READS A PASS INTO IT

**It cannot close beat 09's slate and its own block says so.** Two of the three
open faults are untouched:

- **The eyes.** P7 needs them open; the eye tag is a **1-in-4 rate**, not a lever
  (that lane retracted its own rule as pre-registered: open once, a wink once,
  open-but-blank-white once, shut once). At seed 20260820 they are **shut**, so P7
  is an expected FAIL at this seed.
- **The adult read.** The face reads adolescent and **there is no age tag in the
  prompt at all** — `1boy` is the only person tag. `mature male` is this
  checkpoint's own adult tag and the vacancy law says that absence is why every
  frame decides his age afresh. **Named, one token, unfired.**

**And the two clauses have never co-occurred:** seed 20260817 has the eyes and a
48% head; seed 20260820 has a 56% head and shut eyes. **So the plate beat 09
ships off is a render-N-and-pick on a SETTLED wording** — hair first (running),
then the age tag, then four fresh seeds to pick a pair of open eyes. Beat 09 stays
a slate in tonight's cut, and the cut slates it gracefully with its VO over the
card — which matters here, because beat 09's line is the episode's punchline.

### THE CUT IS ASSEMBLED: `review/ep2-demo-0819b/`, 18 FOOTAGE BEATS AND 3 SLATES

One slate fewer than any cut this episode has had. Three clips changed, all of
them this page's own crf finding cashed in **per beat**, each on another lane's
written verdict: **beat 07 slate → footage** (PASS M1–M4, cut-preferred,
`done_when` met clause by clause, with the shared-uniform plate fault carried in
the open and visible in a frame strip on the page), **beat 01** (PASS, fixes the
bloom its incumbent's own verdict admitted), **beat 17** (PASS, cleaner
conditioning, two costs no clause covers written down). **Beat 18 was offered the
same upgrade and refused it** on FAIL-FROZEN. Three took the flag, one rejected
it — the per-beat rule, actually applied per beat. $0, no GPU: one ffmpeg
assembly, two copies and one scp. Bench (`--out`), no leaf, nothing promoted, and
both replaced clips are still on disk so every swap is one line to undo.

### THE THING THE SLATE COUNT HIDES, now in a file rather than in a paragraph

`review/ep2-picks/cut-readiness-0819.yaml` — one row per beat 1–21: best take with
its sha256, the verdict that licenses it, whether its VO exists, and `blocked_on`,
each row citing the cut's own ingredient hashes, a `verdict*:` block, or the
beat's `done_when`. Every hash in it was recomputed from bytes on disk; the check
caught a one-character typo, and it caught the file making the *identical*
unquoted-scalar mistake it was documenting in `b15-0819-verdict.yaml`.

**FOUR beats have a written PASS (01, 07, 17, 18). THIRTEEN are best-available.
EIGHT of those — 3, 4, 5, 6, 10, 13, 16, 21 — have no verdict block of any kind
and have ridden five consecutive cuts unchanged.** They are not suspected of being
bad; they have never been judged, and five appearances is not five passes. **The
slates are the loud, tracked problem; the quiet middle is where the unknown
actually lives.** Named here rather than fixed: judging eight beats is its own unit
with its own bars, and inventing bars for footage that already exists is how a bar
gets bent to fit the clip — which is exactly what `done-definitions`' repeated
`definition_written: ... NOT from any existing take` fields exist to prevent.

**Also recorded and not acted on** (each is one line to take or veto): beat 12's
cut file is the `-untrimmed` one whose colour-shift fault its own `trim_0815`
record already resolved by edit — not swapped because 1.38s against a 5s slot with
5s of VO over it is a duration decision, and beat 12 is another lane's tonight.

### TOOLING RUNG — every spec in this repo counted its 77-token budget in WORDS, and one was at 85

**Filed 2026-08-19 from `3f3f139a`, in the lane's own words: "the negative I was
about to file measured 85 of 77, and nothing would have told me."** Recorded here
because the tool half is fixed and the *habit* half is not, and the habit is
spread across ~30 filed specs.

**The mechanism, which is silent by design and therefore invisible in a spec
review.** animagine's prompt budget is **77 CLIP tokens including the two
specials**, and a prompt over it is not refused — CLIPTokenizer **truncates the
TAIL**. Every negative in this tree front-loads its defect terms *precisely
because* of that, which is a correct habit that only works if the count is known.
Nothing in the pipeline printed the count, so nothing ever was.

**Words are not tokens, and the gap is not small.**
`ep2-b15-sapcomp-0819`'s first negative was **29 comma-terms** — the kind of
figure specs have been quoting as "26 terms / 38 words, comfortably under" — and
it measured **85 of 77**. Eight tokens would have been dropped in silence, off the
tail, which is where a filer puts the terms it cares least about *and* where a
long negative's last defect terms actually sit. It was trimmed to **71** before
the spec was filed.

**The tool exists and is $0:** `pipeline/clip_token_count.py`. It implements CLIP
BPE directly over `vocab.json` / `merges.txt` from the model already in the
machine's HF cache — no transformers, no torch, no network — takes `--spec`,
`--text` or `--file`, and **exits 1 when anything measured is over the ceiling, so
it can gate a filer**. Its control is the parent job whose negative it measures at
71 against that spec's own recorded claim of comfortable headroom: the claim was
right by luck, and the instrument says so rather than agreeing with the prose.

**THE RUNG, and it is the same shape as the two above it — refuse the thing that
cannot be right, at the one place that can see it.** `box_enqueue.py` should
measure every positive and negative in a spec it is about to queue and **REFUSE a
prompt over 77**, the way it already refuses a job whose output path is
unresolvable. Filing-time is the only moment the fix is free: after the render,
the eight dropped tokens are indistinguishable from a recipe that simply did not
work, and the whole run is a rung spent on a question the prompt never asked.

**What is NOT claimed here.** No render in this repo is known to have been
degraded by truncation — the one measurement over the ceiling was caught before it
ran. What is established is that **the count was never checked**, and ~30 specs
were filed on a word count standing in for a token count. Re-measuring the
already-run specs is its own unit and would be worth doing before any of their
negatives is reused as a parent.

---

## ~~HOLD~~ **LIFTED 2026-08-19 — B. THE LEAN ADULT IS THE GOBLIN.**

**THE RULING, verbatim, 2026-08-19, answering `/review/ep2-goblin-design-0819`:**

> well b definitely and the damn goblin. c kinda is but still pretty bad so change it

**GOBLIN RENDERS ARE LEGAL AGAIN, on the adult design.** Plates, motion jobs and
re-renders all fire; the identity wording `lean wiry adult goblin man, green skin,
bald head, patchwork cloak` is now **founder-ratified canon** rather than steward
inference, and is registered in `pipeline/canon.yaml` as subject
`ep2-goblin-design-adult`. The founder's 08-14 *"seed s0 is the goblin"* and 08-15
*"ill take 1 for the goblin"* are **superseded on the design axis** — by him, in a
direct A/B against rendered frames, which neither earlier sheet could offer
because neither contained a lean adult anywhere. s0 remains the identity **seed**
and the 08-15 deformed-skull caveat still binds any reference build.

**WHAT "c kinda is but still pretty bad so change it" OBLIGES.** The round takes
are not a different character to him — they *"kinda"* read as the goblin — but
*"change it"* is an instruction and not a shrug. **Beats 03, 04, 08, 13 and 20 are
re-rendered to the adult design.** That is the wave; it is filed below.

**TWO RECORDS THIS RULING VINDICATES rather than reverses**, both flagged as
possibly-backwards by the forensic trace when the answer was unknown:

- **today's b20 "chibi fix" was a real fix.** `DRAFTS[20]`'s adult wording and the
  08-18 result *"the adult goblin draws … the chibi child is gone"* were pointing
  the right way after all. b20 still needs its corrected plate (the tree), but the
  build in it is right.
- **the b07/b08 adult identity wording was right.** Both were authored off the
  ratified string and neither needs unwinding.

**THE STEWARD'S READ WAS A, AND IT WAS WRONG.** Recorded plainly because it is the
whole argument for asking with pixels: the steward's case for A was that A had a
quote and B had an inference, which is a sound *records* argument and a wrong
*taste* argument. Nobody had ever put the two creatures next to each other and
asked. The three-picture card cost 0 GPU-seconds and reversed the lane's own
conclusion in one line.

~~NO GOBLIN-IDENTITY RENDER FIRES UNTIL `/review/ep2-goblin-design-0819` IS
ANSWERED. Not a plate, not a motion job, not a re-render of either design
group, and not one further edit to the goblin's identity wording in
`pipeline/plate_scratch.py` or `pipeline/wave-drafts.yaml`. Work that does not
touch the goblin's face or build carries on normally — this hold is scoped to one
character's design, not to episode 2.~~ **Discharged by the ruling above. The
trace below is kept because it is the record of how the drift happened, not
because anything is still held.**

**RUNGS THIS LIFT UNBLOCKS, named so nobody stops at a stale `FROZEN` row.** Three
sections written earlier tonight, while the answer was unknown, declined work on
freeze grounds and are all now open. They are left standing as written — this is
an append-only log — and superseded here rather than edited in place:

| Section, as written earlier tonight | Status now |
|---|---|
| *"b20's converse rung is NOT filed on purpose: its plate is the scavenger, so re-rolling it risks a goblin-identity render under the freeze"* | **OPEN.** And better than open: beat 20 is in the re-render wave regardless, so the plate is being redrawn anyway. |
| *"a one-job fix is waiting behind it … whoever holds the design answer should know"* | **The design answer is B, and this lane holds it.** The b20 re-roll is a real one-job fix and is folded into the wave below. |
| the summary row *"beat 20 re-roll — **FROZEN** — scavenger plate, goblin-identity freeze"* | **UNFROZEN.** |
| *"beat 12's `why: goblin-free beat` has been wrong on four of five renders … the freeze is closer to this beat than the specs say"* | The **freeze** part is discharged; the **finding** is not. Beat 12 still draws an uninvited scavenger from an off-screen clause, and that is a prompt defect on its own merits, ruling or no ruling. |

**WHY, in one paragraph.** The founder watched `ep2-demo-0819c` and asked *"some
scenes including the goblin has him as an adult??"* — as a **surprise**. He was
right on both counts: nine beats in that cut show the goblin and they show two
characters. Five read round and young (03, 04, 08, 13, 20), four read lean adult
(07, 14, 17, 19), and **the split falls exactly on the render date** — everything
drawn on or before 08-16 is round, everything drawn 08-18/08-19 is the adult.
Tracing the authority for the adult found none. His two picks are both round
(`goblin-picker-0814.jpg`, ruled *"seed s0 is the goblin"* 08-14, is 25 round
tiles; `goblin-design-0815.jpg` design 1, ruled *"ill take 1 for the goblin"*
08-15, is labelled *squat, round-bellied* and is the roundest of six). His age
words are *"not old.."* and *"actually a young dumb goblin, but not cute"* — the
axis he named is **cute → not cute**, and the pipeline moved on **child → adult**,
which is a different axis. The one card that ever asked him to bless an adult read
came back *"these generations arent very good"*.

**THE PROPAGATION, so a lane can find it rather than re-derive it.**

| When | What | Where |
|---|---|---|
| 08-13 | steward-authored rule *"He is SHORT, not YOUNG: an adult in miniature, never a child"* — a defensible diagnosis, and it **kept "short"** | `taste/steward-model.ledger.yaml`, `ep2-b13-adult` |
| 08-15 13:28 | rewritten into the prompt as **`a lean wiry adult goblin man`**, replacing `a small goblin boy`; the "short" half dropped; authority cited is an inference (*"The founder's complaint is that he reads as a baby"*) with no quote beside it; `no child` in the same negative | commit `91a35fe1` — `insert_b04_crouch_plate_0815.py`, `wave-drafts.yaml`, `ep2-b04-crouchplate-0815.yaml`, `refs-goblin-d1std-0815.yaml` |
| 08-15 | **the founder's own approved reference blacklisted**: `refs-goblin-approved-0814` (frozen from his "seed s0" ruling) listed under `not_these:` as `# ~4 heads, oversized cranium, toddler stance` | `pipeline/refs/refs-goblin-d1std-0815.yaml` |
| 08-16 | becomes the identity string — `lean wiry adult goblin man, green skin, bald head, patchwork cloak` — now at ~14 sites | commit `9eb7bd15`, `pipeline/plate_scratch.py` |
| 08-18 | board asserts *"Beat 14 is the adult you chose"* on a silence-accepts card. **He never chose it.** b14's plate was drawn 08-18 off the adult wording and shipped on the steward's ruling — `5d872ac3`'s own body says *"the 2026-08-18 board asked about and the steward shipped"* | `review/inbox.yaml`, `5d872ac3` |
| 08-18 | that claim hard-coded as *"beat 14 is the one the founder chose and it is the one that renders"*, and every later beat inherits it | `pipeline/plate_scratch.py:376-381` |

**~~THE FIX THAT MAY HAVE BEEN BACKWARDS.~~ RESOLVED 2026-08-19: IT WAS FORWARDS.**
The 08-18 result *"b20 FIXED: the adult goblin draws … the chibi child is gone"*
was filed as a win, and under **B** it is one. ~~If the founder answers **A**,
b20's **round** frame is the correct one and that fix was a regression queued for
shipping.~~ The round b20 frame served its purpose as picture **C** on the card —
it is the frame he looked at and called *"still pretty bad"* — and beat 20 is now
in the re-render wave.

**NOT CROSS-APPLIED — checked, so nobody widens this further than the facts.** The
*"reads adolescent"* complaint is about the **guards** (beats 05, 06, 10, 11 and
beat 09's plate); every `THE ADULT READ` block in the pipeline is scoped to beat
09. No goblin spec inherited it. What did bleed is **vocabulary**: this repo
writes *"reads adolescent rather than adult"* as a defect by default, and inside
that habit an adult goblin read as a fix instead of a change of character. `mature
male` on beat 09's guard plate remains a legitimate named-and-unfired build and is
**not** covered by this hold.

**~~WHAT LIFTS IT.~~ WHAT LIFTED IT.** One letter on
`/review/ep2-goblin-design-0819`, answered 2026-08-19: **B** — the adult is canon,
the five round beats get re-rendered. (The other two branches, kept for the
record: **A** would have re-rendered the four adult beats; a third design would
have sent the next instrument to a reference image, a LoRA or a drawn design,
**not** a seventh wording — that wall was measured on 08-15, `squat,
round-bellied` rendering 0 of 4, all slim, on a pure text-to-image path where
nothing outranks the prompt. Worth keeping: that measurement is *why* B is cheap
to execute and A would have been expensive — the model draws lean readily and
resisted squat four times out of four.)

---

## Guard 2's voice — appended 2026-08-19 by the VO lane

**AWAITING ONE LETTER on `/review/ep2-guard2-voice-0819`: A, B or C.** No Guard 2
re-synthesis fires until then, because voice is a taste axis (R4) and the steward
does not cast. Everything else in VO carries on; this is scoped to one character.

**THE BOUNCE.** Watching `ep2-demo-0819c`: *"guard 2 has the same voice as the
sapling..."* He was right, and measurement says he was right to within 2 Hz.
Per-character medians off that cut's own takes (`qa_voices.py` estimators — median
F0 by autocorrelation, spectral centroid):

| character | F0 | centroid | vs the tree |
|---|---|---|---|
| SAPLING (VO, `bm_fable`) | 107.4 Hz | 1182 Hz | — |
| **GUARD 2 (`am_echo`)** | **109.1 Hz** | **1283 Hz** | **dF0 1.7, dCent 101 — CONFUSABLE** |
| GUARD 1 (`am_adam`) | 131.9 Hz | 1906 Hz | dF0 22.8 — clear |
| SCAVENGER (`am_puck`) | 164.4 Hz | 1865 Hz | dF0 57.0 — clear |

It is the **only** confusable pair in the cut. One defect, exactly where he said.

**CAUSE: CASTING GAP, NOT A MIS-WIRE — so do not go looking for a bug.**
`voices.yaml` assigns `GUARD 2: am_echo`, `am_echo.wav` exists, and
`synth_vo.py:130` clones from it. That chain is correct end to end. What is
missing is the *shaping*: `build_refs.py`'s `VOICE_SHAPING` hands a per-character
ref passage + speed + semitone offset to `am_puck`, `bm_george`, `bm_daniel`,
`bf_isabella` — **and to nobody else**. Both guards were cast after that
2026-07-25 pass and have no entry, so both cloned from the same shared `REF_TEXT`
at speed 1.0 / pitch 0.0. That file's own comment already names this as *"the
acoustic cause of the founder's 'voices are mixed up'"*; the guards were simply
never swept up by the fix. Measured ref distances from `bm_fable`: `am_adam`
**1.1 Hz**, `am_echo` **8.4 Hz**. Guard 1 drifted clear in synthesis by luck.

**GUARD 1 IS A LOADED GUN.** His ref is 1.1 Hz from the tree's and he passes only
because chatterbox happened to push him up 14 Hz on these three takes. Takes are
non-deterministic on MPS (no seeding — see `ChatterboxEngine.synth`), so a
re-voice could land him on the tree with nothing changed. He gets a
`VOICE_SHAPING` entry in the same pass as the pick.

**TWO ENGINE FACTS WORTH NOT RE-DERIVING** (measured across 9 candidate synths):

1. **Chatterbox does not preserve the ref's timbre.** A first candidate set built
   to differ in *brightness* came back flattened onto one timbre — `am_michael`
   went in at centroid 2183 and out at 1325. **Pitch is the only separator that
   survives cloning.** Designing voices by timbre is wasted effort here.
2. **It pulls pitch toward the middle by a noisy +4..+20 Hz and refuses
   extremes.** `am_onyx` at −6st (ref 63.7 Hz) rendered *back up* to 110.1 Hz —
   straight onto the sapling. So a ref number predicts nothing: every candidate
   must be measured on the **rendered take**, which is what `build_refs.py`'s
   comment has said all along and is now quantified.

**THE THREE CANDIDATES**, all clear of both the sapling and Guard 1 by the
`qa_voices` bar (confusable iff dF0 < 12 Hz **and** dCent < 400 Hz), all mutually
distinct (A–B 63.7 Hz, A–C 96.7 Hz, B–C 33.0 Hz), each speaking beat 10 verbatim:

| | base | pitch | rendered | clear of tree | soft collision |
|---|---|---|---|---|---|
| A | `am_onyx` | −4st | 83.0 Hz | 24.4 Hz | FARMER dF0 8.6 (other thread) |
| B | `am_michael` | +4st | 146.8 Hz | 39.4 Hz | ASSESSOR dF0 10.8 (other thread) |
| C | `am_fenrir` | +5st | 179.8 Hz | 72.4 Hz | none |

Rejected variants, with the numbers, are in
`review/ep2-guard2-voice-0819/candidates.yaml` so nobody re-runs them: `am_onyx`
−6st and −2st, `am_eric` −1st and natural, `am_santa` +3st.

**WHAT THE PICK COSTS.** Add the winner to `VOICE_SHAPING`, point `GUARD 2` at
that base voice in `voices.yaml`, rebuild refs, re-synth **beats 06/08/10 only**
(approved text unchanged — the ruled-legal re-synthesis class, 003b precedent;
old takes archived to `clips/vo-archive/` per R6), re-measure against the whole
cast on the fresh takes, rebuild the cut. Candidate refs are parked as
`~/.cache/banyan-tts/cb-refs/guard2sw-{D1,M2,H2}.wav` (A/B/C) — **the live cast
refs were not touched.** $0.

### RULED — the founder picked **B**, 2026-08-19

Verbatim, from the picker at `/review/ep2-guard2-voice-0819`: **"B"**. Guard 2 is
the rules-lawyer — `am_michael`, **+4 semitones**, candidate B's ref passage,
speed 1.05, measured **146.8 Hz** on the rendered take. That is an R4 taste
ruling on the character's voice and the steward does not re-tune it. Recorded on
the picker page, in `candidates.yaml` (`picked:`), and as a resolved card in
`review/inbox.yaml`.

**ENACTED THE SAME PASS, AND BOTH GUARDS ARE RE-VOICED.** `VOICE_SHAPING` now
carries `am_michael` (+4.0st, B's ref passage, speed 1.05) and `am_adam`
(+9.0st, speed 1.08); `voices.yaml` points GUARD 2 at `am_michael`. The rebuilt
`am_michael.wav` measures **142.0 Hz / centroid 3067 — identical to the
`guard2sw-M2.wav` he auditioned**, so what ships is what he heard rather than a
near-miss of it. Beats 05-10 re-synthesized, approved text untouched, old takes
in `clips/vo-archive/` (R6). Full provenance:
`genomes/sapling/nodes/002b-first-citizen/clips/guards-revoice-0819.yaml`. $0.

**THE DEFECT HE HEARD IS GONE, MEASURED ON THE NEW TAKES.** Character medians
across the episode, and every one of the six pairs clears the 20 Hz bar:

| character | F0 | vs the tree |
|---|---|---|
| SAPLING (VO, `bm_fable`) | 109.6 Hz | — |
| GUARD 2 (`am_michael` +4st) | 135.6 Hz | **26.0 Hz — was 1.7** |
| SCAVENGER (`am_puck` +7.5st) | 167.8 Hz | 58.2 Hz |
| GUARD 1 (`am_adam` +9st) | 192.0 Hz | 82.4 Hz — was 22.8 *by luck* |

Worst pair in the whole episode is now GUARD 1/SCAVENGER at 24.2 Hz; the guards
are 56.4 apart. Per-take: 192.0 / 181.8 / 212.4 (G1) and 135.6 / 134.1 / 135.6
(G2) — `am_michael` is the steadiest voice in the cast at a 1.5 Hz spread.

**GUARD 1 WAS THE LOADED GUN AND IS NOW DISARMED BY CONSTRUCTION.** His ref went
from 1.1 Hz off `bm_fable` to 75.5 Hz off it. The reason he went UP and not down,
which is the reusable finding: **the engine's attractor sits at ~110 Hz, which is
exactly where the tree is.** Sixteen rendered takes across seven offsets — deep
refs do not stay deep, they get pulled onto the sapling (−8st spans 77.7-126.0
over seven takes; −9st threw 117.1 once, straight onto the tree). +9st was the
tightest distribution measured, 7.9 Hz across three takes. Down is not a quieter
version of the same choice; down is the defect.

**TWO THINGS MEASURED HERE THAT NOBODY SHOULD RE-DERIVE.** (1) *Short lines
undershoot.* Beat 07 is five words and rendered 177.8 / 174.5 / 170.2 / 181.8
across four attempts, always below the same voice's long lines — the clone needs
voiced material to reach the ref's pitch. Best of the four is on disk. (2) *The
GUARD 1/SCAVENGER pair overlaps per-take even though it passes on medians* — the
scavenger's own takes span 155.8-192.0, a 36 Hz spread that predates this pass.
They never alternate (guards 05-10, scavenger 13-20), unlike the pair the founder
caught, so it is filed for the VO lane rather than fixed by re-rolling a
character this ruling does not cover.

**WHAT THE NEXT ASSEMBLY INHERITS — no flag, no copy step.** `render_t3` reads
`clips/NN-vo.mp3` and the measured chunk timings in `clips/NN-vo.json` straight
out of the node directory, so **the next cut picks these six takes up
automatically.** This lane deliberately did NOT rebuild the published cut:
`review/ep2-demo-0819c/sources/` still holds the old takes, and the guard voices
in the live cut stay wrong until somebody assembles. That is the one thing left
on this item.

---

## BEAT 12 — the second rung, and a finding that is not about beat 12

`ep2-b12-shortstill-0819` — **FAIL**. One variable off `ep2-b12-stillmotion-0819`
(`--frames 121 → 73`), same seed 20260819, same init, same prompt files, same
sampler numbers. rc=0, 73 frames, 704×1280, 24 fps, 3.0417 s, 221 s of GPU, $0.
Verdict and every number are in the spec's `verdict_this_job_measured`.

### `--frames` IS NOT A TRIM, AND THAT INVALIDATES A MOVE SEVERAL LANES ARE USING

The rung's derivation (`70cd3b98`) argued that because the parent's fade was
"progressive and back-loaded", 73 frames would "never render the part of the ramp
that collapsed". **That reasoning is wrong and the pixels say so.** The two
renders share `f000` — both conditioned on the same plate — and diverge
immediately:

| | f000 | f024 | f060 | f072 | f120 |
|---|---|---|---|---|---|
| parent, 121f | 125.47 | 125.33 | 113.63 | 98.91 | 34.37 |
| this rung, 73f | 125.47 | **108.84** | 104.03 | 104.04 | — |

The parent is flat to f048 and then falls off a cliff. This one falls for 42
frames and then sits still. **Frame count is an input to the denoiser's temporal
grid, not a crop of a longer render**, so a shorter rung is a re-roll of the whole
video. Any rung anywhere on this ladder of the form "shorten it so it does not
reach the part that broke" has no basis, and any rung that shortens **cannot**
inherit the longer rung's early frames as evidence. Filed here rather than in the
beat-12 spec because b01, b07, b14, b17, b18 and b19 are all running LTX rungs and
this is the kind of thing that gets re-derived at 2am.

### What actually failed

The pre-registered dusk clause fired on its number — |lum(f072) − lum(f000)| =
**21.43** against a 12-level bound — and **mis-attributed it**. Three-band mean
luminance, f000 → f072:

| rows | f000 | f072 | Δ |
|---|---|---|---|
| 0–560 (sky, big lit leaf) | 134.84 | 133.29 | **−1.55** |
| 560–1120 (mid-ground) | 130.48 | 83.55 | **−46.93** |
| 1120–1280 | 75.13 | 73.41 | **−1.72** |

Two thirds of the frame do not move. The parent on the same bands falls
everywhere (134.73 / 130.60 / 75.09 → 35.77 / 36.50 / 21.99) — *that* is a dusk
fade; this is not one. What this is: **a large dark leaf mass enters at the left
edge about f004 and grows across the mid-ground until f048**, pixels under
luminance 40 going 5.09% → 19.97% and then holding. Gamma-lifted 2× at f048 it has
midribs, a lobed contour and a warm rim light — **foliage, not a creature**, so it
scores as `FAIL-PLANT-CHANGE` and not `FAIL-INTRUDER`. The negative already
carried "new leaf, extra leaf, growing leaf".

Also dead, as the bar honestly predicted: grass-band interframe median **0.0000**,
0.054 levels/frame ramp-subtracted on the plateau, 8.7% of pixels changing at all
between f060 and f061. **And the "grass band" contains no grass** — rows 1024–1280
at this framing are another leaf and a strip of sky, so the parent's 0.011
measured a leaf too. *"Only the grass stirs" is unscoreable on this plate at any
length.* A wider plate, not a different prompt, is what that clause needs.

### What passed, including one thing for the first time

- **No intruder.** No goblin, hand, face, figure or creature at any edge in any of
  the 73 frames. No bird. The white speck near the top is in the **init** (peak
  luminance 200.6 there, 183.5 at f000).
- **Hue holds** — 0.09° across the first second, 1.15° across the clip, against
  the shipped crf-33 take's **40.24°**. Second independent confirmation that beat
  12's recorded warm-to-cool fault belongs to the crf-33 flag, not the beat.
- **Camera locked, and measurable for the first time on this beat** — the parent's
  fade had invalidated the instrument. Level-normalised SAD f000→f072: best shift
  dy=+1 dx=−1 at 43.038 against 43.098 at no shift, an improvement of 0.06 levels.

### What the bird question now costs

The rung was built so the bird's absence would decide between "it needed frames it
no longer has" and "the negative's *creature* does not hold". **Because 73f is a
different render, neither answer is available.** The only honest statement is "no
creature in this render"; the parent's bird is still unexplained. That is a cost of
the wrong premise and it is written down rather than resolved in the flattering
direction.

### Standing state

**No swap.** Beat 12 keeps `12-related-b12-tightB-untrimmed.mp4`, `best-available`
with its colour fault named, and the upgrade its cut-readiness row already
records — the *trimmed* crf-33 take, an edit and not a re-render — is untouched by
anything measured here. **No third rung filed**: the spec's `what_this_licenses`
says one clip and it is honoured. Recorded for whoever takes the lane next, as a
recommendation and not an order: the frame-count lever is spent as a dodge; both
rungs now show the same shape of failure (**the negative names the thing that
arrives and does not hold it** — "creature", then "new leaf"), so the next lever is
the *positive* prompt, which spends its whole first sentence asking for stillness
and gets total stillness plus one uninvited object. Beat 12 has no goblin on
screen, so none of this waits on the design answer.

---

## HANDOVER appended 2026-08-19 by the queue-keeper lane

**THE DARKENING IS NOT THE CRF FLAG, AND IT IS NOT THE SEED. THREE OF FOUR
CANDIDATES ARE MEASURED OUT AND THE FOURTH IS RUNNING.** Full working in
`pipeline/loop/darkening-crf-diagnostic-0819.md`; the instrument is
`pipeline/luma_drift.py`, which is new, committed, and is the brightness clause
beat 20's verdict asked for and nobody had written.

**The rung as ordered could not be built, and the reason was the finding.** The
order was "vary only `--image-crf` back to 33 on b01 or b18". **Both of those
carriers are already at crf 33** — they are the baselines. Their crf-10 siblings
were already rendered this morning off identical init shas, so the question was
answerable at **$0 on four existing clips**, with two beats instead of one and
both arms instead of one, and with the card left free. That is what ran.

| clip | crf | seed | drift f000→f120 | bands |
|---|---|---|---|---|
| b12-stillmotion | 10 | 20260819 | **−91.05** | all fall |
| b20-motion | 10 | 20260819 | **−25.03** | all fall |
| b01 parent | 33 | 20260818 | **+73.24** | all rise |
| b01 crf10 child | 10 | 20260818 | +1.37 | disagree |
| b18 parent | 33 | 20260871 | −0.22 | disagree |
| b18 crf10 child | 10 | 20260871 | +10.14 | all rise |

The instrument was validated against the collapses first and returns b20's
**−25.03 exactly** and its bands to 0.02. **crf 10 sits on four clips: two
collapse, two do not.** And the argv diff kills the rest of the recipe as a
suspect — all six specs are **identical on size, frames, fps, guidance,
two-stage, distilled-sigmas, offload and mode**, with `--image-crf` the only flag
that varies. No sampler setting separates the darkeners from the clean takes
because no sampler setting differs. **Beat 20's "IT IS A RECIPE PROPERTY AND NOT
A BEAT PROPERTY" is withdrawn; it is the other way round.**

**Two corrections to the evidence the question was built on.** Beat 12's
`shortstill` **−46.93 is not darkening** — its own verdict scores it
`FAIL-PLANT-CHANGE`, a leaf crossing the mid-ground while the other two bands move
1.6 levels. The real second data point is the 121-frame parent's −91. And beat
01's ladder figures (84.8 / 148.4) come back **89.46 / 160.26** on the committed
instrument: same direction, 5–12 levels apart, because that lane measured with an
uncommitted convention. Re-cite beat 01's luminance from the diagnostic file.

**The seed lead was real, was tested, and is now closed too.** Both collapses ran
on **20260819** and no clean take did. Two rungs filed, run and judged inside the
hour — `ep2-b01-growmotion-s20260819-0819` **PASS-HOLD +16.59**,
`ep2-b18-tremble-s20260819-0819` **PASS-HOLD −4.28**, `PASS-HOLD` pre-registered
as more likely on both. *Against myself:* the b18 arm's three bands all fall, so it
has the collapse's shape at a twenty-first of its size — but beat 18 sits inside
±11 levels on every seed and crf value ever measured on it, so that is its floor.

### CARD STATE AND THE ONE RUNG IN FLIGHT

**Running: `ep2-b12-stillmotion-s20260871-0819`** (queued 17:50). The converse and
the closer: the take that lost 91.05 levels, re-rolled on **20260871**, the
flattest seed on record, everything else byte-identical.
**`FAIL-COLLAPSE-AGAIN` is pre-registered as MORE likely** — if it fires, the seed
is exonerated from the other direction too and **the cause is the plate or the
prompt**, which is a route someone can then actually decide. Judge it with
`python3 pipeline/luma_drift.py <clip>`; the bar is two-sided, `|drift| >= 20`
with bands agreeing.

**The card is at ONE, not the floor of two, and that is a refusal rather than an
oversight.** Every other item on the legal list is now closed or blocked:

- **b01 and b18 seed depth are closed by this lane's own verdicts.** Both bridge
  seeds FAILED. **b17** (seed 20260843) fails **H3, leaf count** — an uninvited
  green leaf drifts through the upper third f040→f051, on a bar that says exactly
  two leaves in every frame and calls a partial a FAIL; everything else held.
  **s4** (seed 20260878) fails the **four-quarters clause** — interframe medians
  7.33 / 7.25 / **0.44** / 4.02 against the passing parent's 5.60 / 6.69 / 6.05 /
  5.13. Q1 and Q2 are livelier than the passing seed's and **Q3 is 14x deader**,
  at the same 0.45 the bar had already recorded as "reads visually frozen". Both
  verdicts say no re-roll, so filing a further depth seed would contradict them.
- **b21 is BLOCKED and was not waived.** `box_enqueue` refused
  `ep2-b21-daylight-s20260903-0819` because the parent's `--src` is
  `C:\banyan-farm\plates-local\12-related-r4-s2.png` — **a beat-12 plate**, on a
  path no farm-out job owns, so its reference set cannot be checked. **The passing
  beat-21 verdict rests on that plate.** A `plate_ack` here would push a
  cross-beat plate through the one guard built to catch exactly that, so the spec
  was deleted rather than filed. **Someone with authority over beat 21 should
  establish which plate that verdict is actually about** — this may be a
  provenance problem in a PASS, not just an enqueue problem.
- **b20's converse rung is NOT filed on purpose:** its plate is the scavenger, so
  re-rolling it risks a goblin-identity render under the freeze.

**b01's growmotion leaf is the third sighting of one pattern** — the negative
names the thing that arrives and does not hold it, after beat 12 twice
("creature", then "new leaf"). Three beats, one mechanism. That is a prompt
finding waiting for an owner.

### REPAIRS DONE

- **The b01 duplicate-filename defect is repaired for b13 and b14**, exactly as
  their own spec said it should be — a rename plus a manifest rewrite, no
  re-render. Clips and sidecars now read `s20260838` / `s20260839` instead of the
  init plate's `20260826`; both `.sha256` name rows rewritten and **every hash
  re-verified against the new names**, contents byte-untouched. Done on the **box
  first**, then `origin/farm-results-rtx5090` (`e67e752d`), so a courier push
  cannot restore the old name beside the new. **Still open:** twelve other
  growmotion jobs share the plate-seed name, and `sweep_summary` still calls its
  pick "20260826 PASS" when that clip's sidecar reads **20260818**.
- **The derivation now refuses what the clones kept.** `pipeline/derive_seedprobe_0819.py`
  strips `verdict|pick|sweep|plate_ack|caveats_not_scored|what_this_licenses`,
  names every clip seed-true and job-unique, and asserts each substitution
  matched. It caught two real things: an ordering bug where the id substitution
  ate the clip name, and — on the b18 parent — **six inherited findings keys
  including a full `verdict: PASS`**. Those are renamed on `s4` now, but
  **`ep2-b18-tremble-s2-0819` and `-s3-0819` still carry a PASS belonging to
  s20260871 on clips nobody has opened.**
- **`box_autofill.py --status` lied to this lane on the first call** — reported
  `backlog_empty` with an idle card, from the junk `C:\banyan-queue` directory,
  exactly as the tooling rung above predicts. **Every card reading in this
  handover was taken by `ssh rtx5090 dir /b` directly.** The guard that rung asks
  for is still unwritten and it is still costing readings.

### NOT DONE, and named rather than left silent

The **$0 re-measure of the b01 six-seed sweep** on a colour-independent mask was
not started. It is genuinely ready — all six clips are already in the local git
object store on `origin/farm-results-rtx5090` (extract under distinct names, they
share one basename) — but the colour-independent instrument **does not exist as
code**: commit `2c157810` ran it ad hoc and landed only YAML. Its spec is prose in
`ep2-b01-growmotion-b14-0819.yaml`'s `verdict_this_job_measured.instrument`, and
the nearest template is `farm-out/ep2-b19-dropmotion-0819/b19_fruit_track.py` —
keep its windowed nearest-centroid track, discard its hue predicate, which is the
artefact. Writing that instrument is part of the repair, not a prerequisite to
find.

### CORRECTION to the handover above — the converse rung landed and changed its conclusion

The handover said "the plate or the prompt is what is left". **It is not.** The
converse rung came back **−0.04** on seed 20260871, against **−91.05** on the same
plate, same prompt, same argv, seed 20260819. `FAIL-COLLAPSE-AGAIN` was
pre-registered as more likely and did not fire.

**Every factor is innocent on its own. The cause is a (seed × plate) INTERACTION**
— 20260819 collapses on beat 12's plate, holds on b01 (+16.59) and b18 (−4.28);
beat 12's plate holds on 20260871. Full table and my own reasoning error in
`pipeline/loop/darkening-crf-diagnostic-0819.md`. Short version of the error:
eliminating four candidates one at a time is sound only if a single cause exists,
and every branch of every bar I wrote was a single cause, so the result had
nowhere to land.

**The actionable consequence, and the one thing to read if nothing else:** a
collapse on this plate is **fixable by a re-roll**. `ep2-b20-motion-0819` also ran
20260819 and also collapsed (−25.03), so beat 20's darkening is very likely the
same interaction and very likely re-rollable in one job — **and that rung is
deliberately NOT filed, because b20's plate is the scavenger and re-rolling it
would be a goblin-identity render under the freeze.** Whoever holds the design
answer should know a one-job fix is waiting behind it.

**Card as this lane stops: ONE running** —
`ep2-b12-stillmotion-s20260818-0819-1787147942`, a third seed on beat 12's plate,
because one clean seed can be luck and two make 20260819 the outlier. Judge with
`python3 pipeline/luma_drift.py <clip>`, two-sided, `|drift| >= 20` with bands
agreeing; `PASS-HOLD` named as more likely **with the caveat that the last two
predictions on this axis were both wrong.** If the runner has not pushed to
`farm-results` yet, scp from
`rtx5090:C:/banyan-farm/courier-box/farm-out/<job-id>/` rather than waiting for a
courier tick.

**Standing note for every 121-frame rung from here:** luminance is a **per-render**
check, never inherited from a passing sibling — this family can move 90 levels on
a seed that behaves perfectly on two other beats. Two-sided bound, attached to the
(seed, plate) pair, instrument already committed.

---

## Appended 2026-08-19 by the beat-12 third-seed judging lane

### THE THIRD SEED HELD ITS BRIGHTNESS AND MOVED THE CAMERA 387px INSTEAD

`ep2-b12-stillmotion-s20260818-0819` — **FAIL-CAMERA**, and the luminance question
it was filed to answer **PASSES**. Two verdicts in one clip and they must not be
blended. Verdict, every number and three evidence sheets:
`pipeline/jobs/ep2-b12-stillmotion-s20260818-0819.yaml` `verdict_0819` and
`farm-out/ep2-b12-stillmotion-s20260818-0819/`.

- **The clause:** cumulative vertical drift **−387px** (30% of frame height),
  **dx = 0** on every frame, dy 0 for seven frames then a monotone ramp to
  −5px/frame, and **region-consistent** — all six blocks of a 3×2 grid inside 1px
  at f060, the beat-19 lane's own test for a real move versus field re-inking.
  Shift-compensation collapses raw mean |diff| f000→f120 from 59.66 to 17.47:
  **almost everything that happens in this clip is the camera.** By f100 the frame
  has descended into a bank of grass that is not in the plate.
- **The luma answer, repaired.** `luma_drift.py` read whole-frame **−15.45** — a
  PASS on the spec's two-sided ≥20 bar — with **bands violently disagreeing**
  (+37.91 / −50.95 / −33.41). Eyes said the disagreement is not an object, it is
  the whole picture sliding. Measured on **matched content** (f000 rows [387:] vs
  f120 rows [:893]) the drift is **−1.35**, and a tracked 400-row patch moves
  −5.32. So the honest figure for the ladder's table is **−1.35, not −15.45**.
- **Against myself, and it is the interesting half.** If a descent into a dark
  lower field can forge −15, it could forge −91, and the parent's "DUSK COLLAPSE"
  would have been a framing artefact all along. **Tested on all three clips and
  killed:** s20260819 drifts **+0px** with a genuine −91.05, s20260871 **+7px** /
  −0.04, s20260818 **−387px** / −1.35. The parent's fade is a real fade on a
  locked frame, and the **(seed × plate) interaction reading stands.**

| seed | camera drift | luma (matched content) | how it fails |
|---|---|---|---|
| 20260819 | +0px | **−91.05** | real dusk fade, plus a bird |
| 20260871 | +7px | −0.04 | clean on both — the flat one |
| **20260818** | **−387px** | **−1.35** | **camera tilt** |

**Three seeds, one plate, one 42-token argv, three different failure modes, none
of them shared.** What that settles: two of three hold luminance, 20260819 is the
outlier, **a collapse on this plate is fixable by a re-roll** — which is the answer
beat 20 was waiting on (its own re-roll stays unfiled: scavenger plate, under the
goblin-identity freeze). What it does not settle: **no seed has yet produced a
usable 121-frame take on this plate.** The clean-luminance seed is the one that
moved the camera.

### CAMERA LOCK IS NOT PROMPTABLE ON THIS RECIPE — IT IS A PER-SEED LOTTERY

This is the first defect on this ladder that the positive-placement law does **not**
explain, because **the ban is in both places**: the positive opens *"Static locked
framing, the frame never moves and nothing enters it"* and the negative's first six
tokens are *"camera pan, camera tilt, zoom, dolly, push in, pull back"*. It tilted
387px anyway, on a seed with form on beat 01 twice. So the consequence is the same
shape as this page's standing luminance note: **framing is a PER-RENDER check,
never inherited from a passing sibling and never argued from the prompt.**

Three lanes have now measured camera lock three different ways ad hoc —
level-normalised SAD (b12-shortstill), a two-region horizon fit (b19), phase
correlation (here). `farm-out/ep2-b12-stillmotion-s20260818-0819/b12_camera_drift.py`
is committed beside the artifacts so a fourth lane does not invent a fourth
convention: per-frame phase correlation, 3×2 block consistency, **and** luminance
measured on the overlap region so a fade cannot hide behind a pan or a pan forge a
fade. **Its own limit, recorded:** a hard fade destroys the correlation peak in a
low-contrast block (s20260819's bottom-right block reads (183,39) while
whole-frame and the other five read 0) — the same effect the shortstill lane hit
from the other side when the fade invalidated its camera instrument.

### SEED DEPTH ON BEAT 12 STOPS AT THREE — a refusal, not an omission

The question three seeds were filed to answer **is answered**. A fourth seed would
measure the **lottery** rather than a mechanism: the three takes fail three
different ways, so the next seed's outcome is uninformative about every hypothesis
on the table. This also honours the spec's own `what_this_licenses`, the
three-rungs-closes-an-axis rule, and the b01/b18 seed-depth verdicts that both
said no re-roll. **No pick, no plate_ack, no cut swap** — beat 12 keeps
`12-related-b12-tightB-untrimmed.mp4`, `best-available`, colour fault named.

### THE DERIVATION GUARD IS A DENY-LIST WHERE IT NEEDS TO BE AN ALLOW-LIST

`derive_b12_stillmotion_0819.py`'s `keys_refused` names five parent keys it
stripped. **Five more came through under names its filter does not match**, and
this judging found them by reading the file it was about to score:
`cut_preference` (beat 01's — a fig growing from idx8, a calyx — with this job's
id substituted through it, so **two generations** of inheritance),
`pre_registered_fail_modes_as_fired`, `fail_mode_I_DID_NOT_PRE_REGISTER`,
`what_the_next_rung_should_be`, `the_duplicate_run` (all four the s20260819
parent's, describing a −91.1 collapse and a bird that are **not in this clip**),
plus `derivation.seed` reading **20260819** while the render manifest and the
rendered sidecar both read **20260818**. All six **renamed, not deleted**, per this
page's convention. The generalisable half: **a verdict can arrive under any key
name**, so the guard three lanes have now asked for should be an ALLOW-list of
keys a child may carry, not a deny-list of five it may not.

### CARD STATE AND THE OWNER MAP AS THIS LANE FOUND IT

**The card is EMPTY and this lane is not filling it, which needs saying out loud
rather than leaving a zero on the page.** Read directly (`ssh rtx5090 dir /b`, not
`box_autofill --status`, for the reason two rungs above): `ready/` holds only six
deliberately parked `.HOLD` / `.DUP` files, `running/` 0, `backlog/` 0.

| rung | state |
|---|---|
| beat 12 third seed | **DONE** — FAIL-CAMERA, luma question answered, verdict committed |
| beat 12 fourth seed | **REFUSED by this lane's own verdict** (see above) |
| beat 12 next lever (the positive prompt) | **NOT FILABLE AS WRITTEN.** The only motion his approved line permits is the grass, `shortstill` established there is no grass in frame at this framing, and this clip confirms it — the grass only arrives *because the camera left the plate*. "A wider plate, not a different prompt" is what that clause needs, and **beat 12 has no `DRAFTS`/`REVS` entry in `plate_scratch.py` at all** (checked: keys are 9, 14, 15, 19, 20), so there is no one-variable plate rung to file; `12-related-r4-s2` came from elsewhere and its wording depth is unestablished. Widening a framing he approved as **"tight on two leaves"** is R4 either way. |
| beats 07 / 09 / 15 / 19 | owned by their own lanes; 15 and 19 also §6-blocked for footage |
| beat 08 hint / identity | axis closed by measurement; next step is research, owned |
| beat 14 | PARKED by steward ruling until the slates close |
| beat 20 re-roll (now known to be a one-job fix) | **FROZEN** — scavenger plate, goblin-identity freeze |
| beat 21 plate provenance | BLOCKED — a beat-12 plate under a beat-21 PASS, needs someone with authority over beat 21 |

**So no unfrozen, unowned, runnable RENDER exists for this lane tonight, and
inventing one is what `box_autofill` is written never to do.** What this lane did
with the free hands instead is the tooling rung below.

### TOOLING RUNG TAKEN — `box_autofill.py` can no longer report `backlog_empty` from a junk directory

The rung this page filed twice and nobody owned is **done, tested and committed**,
in both directions it named:

- **The fill path refuses off-box.** `fill_platform_problem()` refuses when the
  root is a Windows-shaped path (drive letter, or any backslash) and `os.name !=
  "nt"`, **before** the `os.makedirs` that used to create a local directory whose
  *name* contains backslashes. The refusal names the correct door rather than just
  saying no — `box_enqueue.py --backlog` to file, `ssh rtx5090 box-autofill.cmd`
  to fire a tick — and it exits **4**, deliberately **not 2**: `Last Result` is one
  number to a scheduled task, 2 already means *"the card wants work and nobody
  filed any"*, and that is precisely the reading this bug used to forge. The guard
  is keyed on the **shape of the root**, not the platform alone, so a POSIX root
  (a test tmpdir, `BANYAN_QUEUE_ROOT` pointed somewhere real) still fills normally
  on a Mac — verified both ways.
- **The ssh paths refuse on-box.** `--status`, `--verify-deployed` and `--deploy`
  all dial `ssh rtx5090`; run on the box they dial the box and hang until the 60 s
  timeout. They now refuse there and print `dir /b C:\banyan-queue\ready` instead.
  **The test is `os.name` and NOT a hostname compare, on purpose:** the ssh alias
  is `rtx5090` while the box's own hostname is **`MSI`** — it says so in every job
  record it writes — so a name match would silently never fire.
- **Belt and braces:** the same check also sits at the top of `tick()`, because
  that is the function that creates the directories and an importer (a test,
  another tool, a **resumed** agent) reaches it without passing through `main()`.

Verified: `test_box_autofill.py` grew 14 assertions across two cases (a Windows
root on POSIX exits 4, creates **no** junk directory, and `tick()` raises when
imported directly; all three ssh flags refuse under a simulated `os.name = "nt"`
while the fill path is the one that *is* allowed there). **All three gates read by
exit code, not by eye:** `test_box_autofill.py` 0, `test_pipeline.py` 0,
`lint_genome.py` 0.

**Deliberately NOT deployed, and that is the whole point of where the bug lives.**
`--deploy` would ship this file to the box and re-register the scheduled task; the
guard changes **nothing** on the box, because there `os.name == "nt"` and the fill
path is legal. The false `backlog_empty` was always a **Mac-side** report. So no
scheduled-task churn, no restart, no drift for `--verify-deployed` to find beyond
the one it already documents. **The junk `C:\banyan-queue/` directory at the repo
root is left in place on purpose:** it is the dated evidence this page cites
(`autofill.log`, 08-17 ×2 and 08-19 ×2) and deleting it would remove the record of
a bug the same night the guard landed.

**Still unowned after this, and named rather than silently left:** the
`box_enqueue` **idempotency** refusal (same rung, one section up — it re-ran a
finished job and spent 264 s of GPU), and the derivation **allow-list** above.

### RECONCILIATION with the b12/15/20 lane's seeds 4 and 5, filed after this section

`ep2-b12-stillmotion-s20260872-0819` and `-s20260873-0819` landed in `336b9cb5`
while this was being written, and **they are not the rung this lane refused.**
"Seed depth stops at three" above is scoped to **the (seed × plate) darkening
question**, which three seeds answered; that lane's own `why` asks a different one
— *"what beat 12 lacks is a PASSING take"* — and its commit reports **one clause
failing per take**, which is consistent with this lane's finding that the failing
clause changes seed to seed. Read together, the two lanes now have **five takes on
one plate and no take that fails nothing**, and that is the state to quote rather
than either lane's headline. **Neither lane has made a pick.**

Worth noting for the allow-list rung: both new specs carry the inherited parent
blocks **with this lane's `_INHERITED_..._NOT_THIS_JOB` names already on them**. So
the honest naming propagated, and the derivation still copies the blocks. Naming a
leak is not closing it.

---

## SEEDS 4 AND 5 JUDGED — the beat-12 seed axis closes 0 for 5, and the cause is a phrase

Both landed, both fail, and judging them turned up something better than a sixth
seed. `ep2-b12-stillmotion-s20260872-0819` and `-s20260873-0819`, pulled from
`rtx5090:C:/banyan-farm/courier-box/farm-out/` (the courier still has not pushed)
and verified against each job's own `.sha256`, 4 of 4 content files OK on both.
**The init is byte-identical across all five takes** (`c6575d0d…`), which is what
licenses reading them as one plate.

| seed | camera dy | luma (matched content) | how it fails |
|---|---|---|---|
| 20260819 | +0px | **−91.05** | real dusk fade, **plus a bird** |
| 20260871 | +7px | −0.04 | flat and locked — **but a bird with a visible eye rises and leaves** |
| 20260818 | **−387px** | −1.35 | camera tilt, off the plate into grass |
| **20260872** | −180px, blocks incoherent | −8.20 | **a crouching intruder that never leaves**, + the frame re-composing |
| **20260873** | +0px | **−43.48** | **the sky replaced by a wall of reeds**, + a brief intruder |

**Five seeds, one plate, one 42-token argv, five different failures, none shared.
The lottery odds are no longer an estimate: 0 for 5.**

### s20260871 WAS NEVER FULLY JUDGED, AND JUDGING IT IS WHAT BROKE THE CASE OPEN

The honest close this lane was pointed at — *"seven takes have each failed
something, stop filing seeds, the next lever is R4-gated"* — could not be written
without checking the one take nobody had finished scoring. `s20260871` was recorded
as "clean on luma, stillness/bird/leaf clauses **unjudged**". So it was pulled and
run: **+7px cumulative drift with all six blocks agreeing at 1px, luma −0.04,
tracked patch inside ±10.** That take is genuinely, measurably locked and flat —
and then **a black bird with a large white eye rises from behind the lower leaf at
~f030 and is gone by f090.** It fails, but it fails on the *intruder* clause, which
is the same clause the parent failed on and which nobody had yet counted.

### THE INTRUDER IS NOT A LOTTERY AND NOT THE PLATE — IT IS A PHRASE IN THE POSITIVE

Count it across the five takes and the pattern is not subtle:

| take | intruder behind the lower leaf? |
|---|---|
| 20260819 | **yes** — the parent's unexplained "bird" |
| 20260871 | **yes** — black bird, white eye, f030→f090 |
| 20260818 | no — *and its camera had already left the plate by f008* |
| 20260872 | **yes** — rim-lit crouching mass with two ear-shapes, f018→f120, permanent |
| 20260873 | **yes** — dark rounded form f006→f024, then swallowed by the reed wall |

**Four of five, always in the same slot, on four independent seeds — and the one
exception is the take whose framing descended out of the plate before anything
could appear there.** The plate itself is clean: `b12-init-704x1280.png` is leaves,
sun, cloud and sky, with no dark form anywhere in it. So the intruder is invented at
sample time, reliably, by something in the conditioning that is the same on every
seed. There is exactly one candidate, and it is in the positive prompt:

> Tight on the sapling's two leaves, perfectly still — **the scavenger crouched
> behind them, out of frame.** Static locked framing, the frame never moves and
> nothing enters it.

A diffusion positive has **no negation operator and no way to place a named subject
outside the canvas.** "Out of frame" is not renderable; what the clause actually
encodes is *scavenger, crouched, behind the leaves* — a subject and a position — and
a scavenger crouched behind the leaves is exactly what four of five takes drew. The
negative's `goblin, creature, person, face, hands, figure entering frame` has been
fighting the positive on every one of those renders and losing every time.

**This is the ladder's own positive-placement law, third instance** — and the first
where the fix is a *deletion* rather than a rewrite. It also means beat 12's
`why: goblin-free beat` has been **wrong on four of five renders**: a beat everyone
believed was clear of the goblin-identity freeze has been generating off-model
scavenger figures all evening. Nothing was published, so nothing breached; but the
freeze is closer to this beat than the specs say, and the next lane should know it.

### THE NEXT RUNG, AND WHY IT IS NOT THE R4 ONE THIS LANE EXPECTED TO NAME

The standing read was that beat 12's next lever is **plate-side or R4-gated (a wider
framing)**, because the only motion the approved line permits is the grass and
`shortstill` established there is no grass at this framing. **That is still true of
the *motion* clause and it is still R4.** But it is not the binding constraint any
more, because the thing killing four of five takes is not motion — it is a subject
the prompt asks for by name.

**Next rung: `ep2-b12-noscav-0819`. One variable — delete the span
`— the scavenger crouched behind them, out of frame` from
`b12-motion-prompt.txt`. Nothing else changes: same plate sha, same negative, same
seed (use 20260871, the one take that is locked and flat and fails only on the
intruder), same 42-token argv, same crf 10, 121 frames.** Pre-register the bar as
the intruder clause alone: `EVIDENCE-scan-every6f.png` shows no dark form behind
the lower leaf at any frame. ~8 min of card time, $0, one sample.

Why this is **not** R4 and is filable by a steward: it deletes text describing
something the founder's approved line does not contain, that the negative already
bans, and that is not supposed to be visible. **The approved line — "tight on two
leaves, perfectly still" — is untouched**, which is precisely what a widening rung
could not say. If it passes, beat 12 has its first take that fails nothing and the
pick goes to R4 with pixels. If it fails, the intruder is deeper than the prompt and
*then* the wider plate is the R4 question to take to the founder.

**NOT FILED TONIGHT, and named rather than quietly skipped.** The card is empty
(`ready` 0, `running` 0, `backlog` 0) and this rung is runnable, unowned, goblin-free
and zero-dependency — so by the no-idle law it should be on the card. It is not,
because the only derivation path is `derive_b12_stillmotion_0819.py`, whose
**deny-list leak is still open** (six inherited verdict keys, twice), and filing
through it at 20:30 would propagate a third generation of another beat's verdict
into a fresh spec. Hand-writing the spec instead is the right move and it is the
next lane's first job, not a thing to rush at the end of a close. **One rung, named
and costed, is what this lane leaves on the card in place of a sixth seed.**

### WHAT IS RECORDED, AND WHAT IS EXPLICITLY NOT

Verdicts with every number are in each job's own `verdict_0819`. Evidence sheets
(`EVIDENCE-keys-f000-f120.png`, `EVIDENCE-scan-every6f.png`) are committed beside
the artifacts for all three takes judged tonight, including the re-judged
`s20260871`. **No pick, no plate_ack, no promotion, no leaf, no lineage entry, no
cut swap.** Beat 12 keeps `12-related-b12-tightB-untrimmed.mp4`, `best-available`,
colour fault named. **The pick is R4 and no take has earned one.**

**One defect found while judging, not fixed:** all three of `s20260818`,
`s20260872` and `s20260873` publish their mp4 as
`12-related-LTX-stillmotion-crf10-s20260818.mp4` — three distinct takes, one
filename, three directories. Sidecar, bench row and `.sha256` all carry the correct
seed on each, so provenance is recoverable and nothing is mis-attributed. **The
repair belongs in the generator, not in these files:** renaming a published artifact
invalidates the `.sha256` that proves it arrived intact.

> **Correction to the section above, same night, 20:40.** It says "the card is
> empty (`ready` 0, `running` 0, `backlog` 0)". That was read off
> `box_autofill --status` at 16:24Z and it is no longer true: the beat-19 lane
> filed `ep2-b19-sapmid-0819` at ~16:39Z and it went to `running` at 20:40 local.
> Read directly, the card now holds **0 ready / 1 running / 0 backlog**, with
> `ready/` containing only the eight parked `.HOLD` / `.DUP` files. **The GPU is
> not idle.** The no-idle argument for filing `ep2-b12-noscav-0819` tonight is
> therefore weaker than the section above implies — the rung is still the right
> next one, but it is queued behind live work rather than rescuing a dead card.
> Recorded rather than edited in place: a status snapshot is a timestamp, not a
> state, which is the standing lesson about inferring lane liveness.

### CORRECTION TO THE RUNG ABOVE — the approved line DOES contain the scavenger, and the argument is better for it

The section above justifies `ep2-b12-noscav-0819` as non-R4 by saying it "deletes text
describing something the founder's approved line does not contain." **That is wrong, and
checking it before publishing is what turned a weak argument into a sound one.**
`genomes/sapling/nodes/002b-first-citizen/node.md:83` — the approved shot description —
reads, in full:

> Tight on the sapling's two leaves, perfectly still — **the scavenger is still crouched
> in the grass behind them, out of frame.**

The prompt is a near-verbatim transcription of it. So the clause is canon, and deleting
it from the *script* would be R4.

**But the render is what violates canon, not the deletion.** The same node states the
staging explicitly at line 189: *"12 RELATED — he is crouched in the grass behind the
leaves and out of frame, not below them. **Off-screen only; the picture did not change.**"*
Canon says the scavenger must NOT be in the picture. Four of five renders put him in it.
**Deleting the clause from the prompt is what makes the render obey the approved staging** —
it moves the output toward canon, not away from it. The script is untouched and needs no
R4. What *would* be R4 is changing the line itself, or widening the framing.

### THE GENERALISABLE LAW: A SHOT DESCRIPTION IS NOT A PROMPT

This is the real finding and it outranks beat 12. A script's staging prose describes what
is true of the **scene**, including what is deliberately **off-screen** — that is normal,
useful screenwriting. A diffusion positive can only describe **what is in the frame.**
Transcribing an off-screen clause verbatim into a positive therefore asks for precisely
the thing the script says to exclude, and the negative cannot claw it back: beat 12's
negative bans `goblin, creature, person, face, hands, figure entering frame` and lost four
times out of five.

**Whoever writes the next prompt from a script line: strip every clause about what the
camera does not see.** "Out of frame", "off-screen", "behind the camera", "just outside
the shot" are instructions to a human reader and requests to a sampler.

**Scoped honestly, because 315 specs match `out of frame` and that number is misleading.**
Sampled, the overwhelming majority are **negatives** banning subject exits — `walking out
of frame, leaving the frame`, `running out of frame, exiting frame` — which is a correct
and unrelated use. The defect is an off-screen clause inside a **positive**, and beat 12 is
the only confirmed instance. **The audit that would settle it has not been run**: it must
read positives only, and a grep across whole spec files cannot distinguish the two. Named
as unowned rather than claimed as measured.

---

## THE RE-RENDER WAVE — appended 2026-08-19 by the enactment lane

**The ruling that ordered it, verbatim:** *"well b definitely and the damn goblin.
c kinda is but still pretty bad so change it"* (`/review/ep2-goblin-design-0819`).
B is the lean adult and he is the goblin. The C group — **03, 04, 08, 13, 20** —
reads as him but is *"pretty bad"*, and *"change it"* is an instruction.

### Where the wave stands after one pass

| beat | plate | cast | beat's own `done_when` | outstanding |
|---|---|---|---|---|
| 03 BAD COVER | `03-bad-cover-mac-plate-r1s1` | **PASS** | **FAIL** — he is *beside* the seedling, not behind it; nothing says COVER, so the joke is not visible without dialogue | the plant, and the cover RELATION |
| 04 THE FOOTNOTE | `04-the-footnote-mac-plate-r1s1` | **PASS**, sharpest of the four | **NEAR-PASS** — eyes off-axis to frame left, jaw set; body barely in frame at this crop | nothing blocking; usable as a plate |
| 13 THE SHADE | `13-the-shade-mac-plate-r1s1` | **PASS** | **POSE PASSES** — folded small, knees to chest, arms over | the plant; frame is dim |
| 20 EVIDENCE | `20-evidence-mac-plate-r4s1` | **PASS** | **FAIL** — no fig at all, no look up | see below; r1s1 has the fig |
| 08 | not re-fired | — | — | both 08-19 rungs already have verdicts; see below |

### The finding that outranks the rest of this section

**The cast is solved and the canon sapling is not drawable by words on this
checkpoint.** 3 of 3 frames came back the lean adult from the ratified wording
alone — no reference image, no IP-Adapter, no LoRA, one seed each. And 3 of 3
plant beats missed the plant: `a tiny sapling with two big leaves`, a wording
`THE-SAPLING.md` lists as **already satisfying** the founder's two-leaf ruling,
drew six-to-eight leaflets (03, 20) or no identifiable plant at all (13).

**Beat 04 is the control.** It is the only one of the four with no plant in it and
the only one that lands. Three plant beats failed on the plant; the plantless beat
passed. That is what turns three misses into a closed axis rather than a run of
bad luck.

**So the wording ladder for the canon sapling is CLOSED** — three rungs on one
axis, plus the b19 lane's three earlier wordings, is six. Per this ladder's own
standing rule the next instrument is **compositional, and it gets named, not
fired**: `ep2-b19-sapcomp-0819`, which put a fig on a plant with numpy in 3.8 s at
$0 after three wordings could not, and passed all eight clauses of its bar. **A
composited sapling dropped into these three plates is the rung. A fourth sentence
about leaves is not.**

Read this as a *scoping* result, not a stop: **the goblin half of all three beats
is done and will not need re-drawing when the plant is solved**, and beat 13's
pose is a pass on its own terms and is worth keeping.

### Beat 20, and an error of mine worth keeping

`REVS[(20,4)]`'s declared variable landed — r1's thick gnarled tree is gone — **and
the beat got worse**, losing the fig and the look up. The cause is mine and is
written into the entry: it was sold as one variable and was three (the plant,
*plus* `crouching`, *plus* a compressed fig clause). `crouching`, added to
reconcile "look UP" with a 40 cm plant, resolves very reasonably as a man kneeling
to look **down** at a seedling. **The next rung is r1's positive byte for byte with
only the plant clause swapped, and the token budget paid out of the lighting tail
— never out of the fig clause or the look-up clause. This rev is the measurement
proving those two are load-bearing.**

**A free result worth more than the rev:** `r1s1`'s fig is unmistakably **purple**
from a prompt whose only fruit word is `a ripe fig`. That reproduces
`backend_divergence_probe.py` on a fresh draw — the Mac gives the founder's
2026-08-16 purple for free. **`20-evidence-mac-plate-r1s1.png` is the frame to
show him for that ruling.**

### Beat 08 — not re-fired, and why

Both 08-19 rungs already carry verdicts: `ep2-b08-ipamask-0819` **PASSED branch
(1)** (per-figure identity binds; beat 08 has a recipe for the first time) and
`ep2-b08-posenet-sample-0819` came back **branch (2)** (pose binds; the forearm
flips). The thing the freeze was actually holding is the rung posenet **named and
did not take**: *re-stage the arm — elbow low and near the ribs, forearm reaching
forward and down — and change nothing else.* That is a staging edit to
`author_b08_openpose_hint.py` carrying its `--selftest`, then ONE sample. **It is
legal now and it is unowned.**

### The card

The rtx5090 is **idle and verified healthy** — the runner-surgery lane's restart
landed 23:03 and its latency probe claimed and completed in the same second,
against the ~8 minutes it cost before. **No goblin motion job is runnable yet**:
motion needs a plate that has passed, and the blocker on three of four plates is
compositional work that does not use the GPU. The named box rung above (b08 arm
re-stage) is the honest next GPU job.

### Two tooling faults found while filing, named not fixed

1. **`mac_enqueue.known_beats()` cannot see `DRAFTS[15] = {...}`.** It parses only
   the `DRAFTS = {...}` literal, so beat 15 — one of the cut's four slates —
   **cannot be enqueued on the farm at all**. Beats 03, 04 and 13 were put inside
   the literal for this reason.
2. **The checkout guard is blind on macbook2 and macbook4.** Those two keep
   `~/banyan-city` as a non-git rsync copy, so the guard's `git HEAD` read finds
   nothing and passes. It correctly refused macbook1 for the same staleness
   minutes earlier. b04's first attempt died `rc=4 no inline draft for beat 4`.
   Both code roots are now synced from their farm checkouts.

### THE COURIER CANNOT PUSH, AND IT BLOCKS EVERY BOX PLATE — found 2026-08-19 23:5x

**Measured, not inferred.** `C:\banyan-farm\courier-box` is **45 commits ahead of
`origin/farm-results-rtx5090` and 1 behind it** — diverged, with the true remote
head hours old. `ep2-b04-mac-plate-0819` ran clean (rc=0, 2 artifacts,
20:00:31Z), the courier committed it locally as `e8f21b95 "hb: DONE
ep2-b04-mac-plate-0819"`, and **it never left the box.**

**Why this is bigger than one plate.** `box_enqueue`'s plate and refs guards read
`origin/farm-results-rtx5090` at enqueue time. While the backlog stands, **no
newly published box plate can ever resolve as a motion init** — every such job
gets *"could not fetch this job's --src"* and the only way past is a
`plate_ack:` waiver, which the standing rules forbid a lane from granting itself.
So a stuck courier does not merely delay artifacts; **it silently pushes every
downstream lane toward waiving a provenance guard.** That is the shape of failure
this repo keeps writing rules against.

**What was done and what deliberately was not.** The plate was carried across by
hand — the box's own published bytes pulled back off `courier-box\farm-out\` and
pushed from a machine whose push works, in an isolated worktree, adding three
files and removing none. Hash-identical in all three places
(`5dd35da5…4350`). Both guards then RAN and PASSED with **no plate_ack**: plate
flatness **0.134** against the 0.62 refuse line, refs resolved to producer
`ep2-b04-mac-plate-0819`. `ep2-b04-eyes-crf10-0819` is queued.

**The divergence itself is NOT resolved and is the runner-surgery lane's call.**
A force-push would discard the one commit this branch has that the box does not;
rebasing 45 artifact commits on a 5.5 GiB repo is that lane's work, and its push
logic was changed tonight (`PUSH_TIMEOUT_SECONDS` 300 → 60, deferred events).
**Hand-carrying is a workaround for one plate, not a fix.** Until it is fixed,
any lane publishing a box plate must expect to carry it across the same way.

## Appended 2026-08-20 by the beat 08 staging lane — NO MORE b08 TEXT2IMG PLATES

**Steward ruling, recorded so no lane files a fourth.** Beat 08's cut plate comes
from the **skeleton path**, not from `plate_scratch` and not from a bare
text2img sample. Bare text2img keeps producing **colossi** on this beat, and
2026-08-19's macbook1 plate (`farm-out/ep2-b08-mac-plate-0819/`,
`08-inside-him-mac-plate-r1s1.png`, seed 20260816) is the **third instance**: a
giant goblin floating in a green field above a small guard standing on a
separate path, board raised at his chest, no gesture, no shared ground plane.

**It is not a wording problem and that is now settled rather than argued.** That
sample's own `why_this_plate` field records the previous attempt returning "a
HILL-SIZED goblin looming over three tiny guards", and the rewrite that followed
*deleted the reserved sky* precisely to remove the vacancy a colossus grows in.
It came back a colossus anyway. Beat 08's r4 had already proved a negative naming
`giant, colossal, monster, kaiju, statue, face in the sky` removes it **not at
all**, and the uncontrolled tally at the route's seed is **4 of 4**.

**What the skeleton path buys, measured, on the same beat:** two figures at their
authored positions with no fusion, a stature ratio inside 10% of the authored
1.100, one ground plane, the pointing arm on the **guard** in five consecutive
mechanisms, and — since `ep2-b08-twins-sample-0819` — the hand arriving 52.5 px
from its authored wrist with the goblin's arm staying on its own skeleton.
Nothing wording-only has come close to any of it.

**So:** a b08 plate job that has no ControlNet hint has no consumer. If a lane
believes it needs one, the thing to file is a rung on the skeleton route with a
pre-registered bar, not another sample of a question closed three times.

## Appended 2026-08-20 by the judging lane — THREE DONE JOBS SWEPT, ONE WAS ACTUALLY UNJUDGED

**The sweep, and the false alarm inside it.** Three jobs sat in the box's
`done/` reported as having no verdict: `ep2-b04-mac-plate-0819`,
`ep2-b19-sapmid-b-0819`, `ep2-b12-noscav-0819`. Read directly, **two of the
three were already fully judged** — `ep2-b19-sapmid-b-0819` at commit `95be8d0e`
and `ep2-b12-noscav-0819` at `3ecb8a34`, both carrying real measured numbers and
a `pre_registered_fail_modes_as_fired` roll-call. They were invisible to a
`^verdict:` grep because both write the key as **`verdict_measured:`**.

**Named because it will misfire again.** This repo has two verdict key
conventions in live use — `verdict:` + `verdict_measured:` (the b04 lane) and
`verdict_measured:` alone (the derived-spec lanes). Any lane auditing for
unjudged work must match `^verdict`, not `^verdict:`, or it re-judges settled
rungs. **Counted, not estimated:** of the 928 jobs in `done/` that have a local
spec, **886 lack `^verdict:` but only 840 lack `^verdict`** — so **46 specs are
judged in a form a `^verdict:` grep calls unjudged**, and two of tonight's three
were among them.

**The other 840 are not a backlog.** Appending the verdict to the spec is a
recent convention; most of those jobs were judged in a loop cycle, a contact
sheet or this ladder. **The set that actually matters is jobs finished in the
last two days**: of the **58** distinct jobs in `done/` dated 08-19 or 08-20,
**8 have a spec with no verdict in any form** —
`ep2-b01-growmotion-b10/b11/b12-0818`, `ep2-b01-growmotion-b15/b16-0819`,
`ep2-b12-plateship-0819`, `ep2-b15-macplate-publish-0819`,
`ep2-b20-plateship-0819`. (`probe-heartbeat-latency-0819` has no spec at all.)
The growmotion five are **gaps inside a sweep whose b13, b14 and b17 siblings
are judged**, which is the kind of hole that reads as "nothing there" rather
than "not looked at".

### `ep2-b04-mac-plate-0819` — PASS on all three clauses, verdict now in the spec

The one genuinely unjudged job. Measured and appended to the spec:

| clause | result | number |
|---|---|---|
| two files + `.sha256` manifest in farm-out | **PASS** | 3 files, 1,301,379 / 1,885 / 203 bytes; manifest lists both, sorted |
| PNG sha256 unchanged after the copy | **PASS** | `5dd35da5…4350` on the box (certutil), on `main`, and in `origin/farm-results-rtx5090` — **three-way identity** |
| motion job resolves it with **no `plate_ack`** | **PASS** | `ep2-b04-eyes-crf10-0819` `--src` → this plate, `--sha256` `5dd35da5…`, plate_ack key count **0**, flatness **0.134** vs the 0.62 refuse line, refs producer `ep2-b04-mac-plate-0819`; job rc=0, 121 frames |
| *(unregistered, checked anyway)* right beat, not corrupt | **PASS** | opened at 832×1216: lean **adult** goblin, bald domed head, long pointed ears, eyes off-axis frame left, jaw set — beat 04, no child build, no blush |

Job itself: 1 step, rc=0, start **and** finish `2026-08-19T20:00:31Z`, $0, no GPU.

**Rung this CLOSES.** "THE COURIER CANNOT PUSH, AND IT BLOCKS EVERY BOX PLATE"
above recorded the hand-carry and the guards passing; it is now scored against
the spec's own pre-registered bar and the spec carries the verdict. **The b04
plate-publication rung is closed.** The route — publish through a farm-out
directory one spec owns — is proven a second time after
`ep2-b14-mac-plate-0818`, and is the legal way past `box_enqueue` for any lane
holding a Mac plate with a motion job downstream.

**Rung this does NOT open.** No cut consequence. The plate is
`approved: false / provisional: true / founder_verdict: null`, and the clip made
from it (`ep2-b04-eyes-crf10-0819`) failed its own beat clause — the gaze moves
by a **head rotation of 64.7 px**, which its verdict explicitly refuses to
license as a cut swap. **Beat 04's slate keeps `b04-refire-0814`.** The
follow-on rung, `ep2-b04-headlock-0820`, is already filed, run and judged.

**Qualification, recorded because the spec promised a route it did not get.**
The spec's prose said "let the courier push it". The courier did not: 45 commits
diverged, the plate committed locally as `e8f21b95` and never left the box. The
bytes reached the branch by hand-carry. The `success` clause names files, a hash
and a guard outcome — never the courier — so this is not a clause failure, but
**every lane publishing a box plate should still expect to carry it across by
hand** until the runner-surgery lane fixes the divergence.

### The three courier jobs in that set of 8 — all PASS, verdicts now in the specs

Same shape, same bar: copy named files to a farm-out directory one spec owns,
prove byte-identity by hash, write a manifest. All three ran rc=0 and **every
file is hash-identical in three places** — the manifest the job wrote on the
box, the copy on `main`, and the blob on `origin/farm-results-rtx5090`.

| job | files | key hash | guard consequence |
|---|---|---|---|
| `ep2-b12-plateship-0819` | 2 + manifest, 5 s | PNG `cc6bd5f0…c074` = the sha `ep2-b12-tightB-0813` cropped | `ep2-b12-stillmotion-0819` `--src` → this path, **plate_ack count 0**, ran |
| `ep2-b20-plateship-0819` | 2 + manifest, 5 s | PNG `4b87cf4f…d119` | `ep2-b20-motion-0819` ran off it, **plate_ack count 0** — **beat 20 got footage for the first time** |
| `ep2-b15-macplate-publish-0819` | 4 + manifest, 12 s | r1s1 `8a9bd14b…4ebe`, r2s1 `b4b28ab5…a103` | **guard not yet exercised** — no beat-15 motion job exists to fetch it |

**Unregistered check run on all three anyway.** A hash proves integrity and
proves nothing about subject, and this ladder has a b04 entry about cropping the
wrong beat's plate. Opened at full size: b12 is layered leaves on a pink sunset
with **no figure** (the same picture `ep2-b12-noscav-0819` scored across 121
frames); b20 is the goblin cupping a **purple fig** — r1s1, the seed this ladder
picked, not the fig-less r4s1 it scored FAIL; b15 is the goblin sitting turned
toward a **two-leaf seedling**, one of the few plates in that wave whose plant
landed. All three are the right beat.

**Rungs these close.** Beat 12's and beat 20's plate-delivery rungs are closed —
both consumers ran with the guards **on**. **Beat 15's is only half closed:** the
bytes resolve on the branch, but no beat-15 motion job has been filed against
them, so the `--src` guard has never actually fetched this plate. That is proof
by construction, weaker than beat 12's and beat 20's, and it is recorded as such
in the spec rather than rounded up to a pass.

**No cut consequence from any of the three.** All three specs say so themselves
and this lane confirms it: beat 12 keeps its take with the warm-to-cool colour
fault named; **beat 20 stays a slate** because `ep2-b20-motion-0819`'s own
`verdict_cut` reads "NOT PROPOSED FOR THE CUT" — a steward call, not a courier's;
beat 15 stays a slate because publishing an init is not footage and
**STEWARDSHIP.md §6 is undischarged**. A courier job's pass is a pass on bytes.

### The growmotion five — measured, NOT scored, and the reason is b13's own warning

`ep2-b01-growmotion-b10/b11/b12-0818` and `b15/b16-0819` are the remaining five
unjudged jobs. This lane pulled all five, ran the committed instruments, and
built 121-frame sheets — then **declined to write clause verdicts**, because the
detector it built reproduces the exact artifact `ep2-b01-growmotion-b13-0819`
already warns about:

> "a green-OR-purple colour-predicate mask reported a one-frame colour pop and a
> 2.0x-2.5x single-frame area step on this clip, and BOTH ARE ARTEFACTS OF THE
> MASK — the fig passes through teal and desaturated slate on it"

A luma-normalised green-magenta mask (`gmn = (G-(R+B)/2)/luma`, correct in that
it survives these clips' +67-level exposure jump) still **drops the fig entirely
during its desaturated slate phase**, which manufactures a fake area collapse
and a fake balloon on either side of the transition. On `b15` it read area 2917
at f084 and 11302 at f096 — an apparent 3.9x step that is the mask losing and
re-acquiring the object, not the fig. **Scoring G1/G4/H4 off that would be
scoring the instrument.** `b13` also settles the reading of G4 that any scorer
must use — *maximum single-frame ratio under 2.0x*, not total growth, which is
how `b13` passed G4 while growing x10.30.

**What IS measured and holds regardless of the mask:**

| seed | job | whole-frame luma f000→f120 | cumulative dy | interframe mean | pairs <0.5 |
|---|---|---|---|---|---|
| 20260835 | b10 | 87.09 → **154.79 (+67.70)** | **0 px** | 1.589 | 0/120 |
| 20260836 | b11 | 87.19 → 144.25 (+57.06) | −202 px | 3.220 | 11/120 |
| 20260837 | b12 | 87.29 → 130.84 (+43.56) | −90 px | 3.121 | 0/120 |
| 20260840 | b15 | 87.55 → 98.23 (**+10.68**) | −141 px | 2.318 | 0/120 |
| 20260841 | b16 | 87.35 → 109.76 (+22.42) | −109 px | 1.234 | 25/120 |

**The blowout is the recipe, not a seed.** All five open at luma ~87.1–87.6 —
the init plate measures **89.63**, so every clip does start on the plate — and
all five have already jumped to 100–156 by **f024**. `b13`'s verdict called its
own +39.60 "the *blooms to pale amber* fault … this seed is four times worse on
it than its sibling"; **b10 is +67.70, worse than b13, and b15 at +10.68 is six
times better than b13**. That is a 6x spread across seeds of one recipe, and it
says the fault is seed-sensitive rather than fixed — which is the useful thing
here and it needs no fig mask to say.

**Do not read the dy column as camera moves.** The drift instrument's own test
is region-consistency across its 3×2 blocks, and **not one of the five is
region-consistent** (b15's blocks span −167 to +137 px). By that test these are
field re-inking, not translation. H4/G5 need eyes, not this number.

**So the rung is: build a fig detector that survives the slate phase** — anchor
on the f000 nub locus (measured on the shared init: area 373 px, dia 24 px, at
y789/x341, gmn +0.347) and track by region continuity rather than by a colour
predicate, so the object is never lost between hues. Until that exists these
five stay unscored, and **"unscored" is written here rather than left as an
absent key**, which is how they went unnoticed in the first place.

### One integrity defect found in passing: `ep2-b01-growmotion-b13-0819`'s manifest is stale

Its `.sha256` lists `01-cold-open-LTX-nubgrow-b-s20260826.mp4` and the matching
`.meta.yaml`; the directory actually holds **`…-s20260838.mp4`**. The files were
renamed to the true seed *after* the manifest was written, so **a `sha256 -c`
against that manifest fails to find 2 of its 6 entries.** The bytes are fine —
the renamed mp4 hashes to `92e67c20…8057`, exactly what the manifest claims — so
this is a naming defect, not corruption. It is worth fixing because a manifest
that cannot be checked by name is a manifest nobody will check. **b13 is the only
sibling that retokened its output filename at all**; the other six publish as
`s20260826.mp4` regardless of their real seed, which is the derive step failing
to retoken `artifacts` and is why the five above are indistinguishable by
filename.

## Appended 2026-08-20 by the beat 08 staging lane — the grip rung, and beat 08's canon filing

**Rung: `ep2-b08-grip-0820`, FAIL, and the two findings are worth more than the
frame.** One variable, the positive prompt, +9 words asserting the grip
positively (`fingers and thumb gripping the clipboard edge`), everything else
byte-identical and verified in the sidecar. Two pre-registered branches fired
together: the guard came back **bald** against canon at unchanged conditioning
(prompt crowding is real at 73 of 77 tokens), and **the clipboard disappeared
entirely** — authored quad 23.5 % of pixels under luma 80 against the parent's
75.8 %. The grip clause bound to the right *hand* and the wrong *object*:
fingers and thumb are drawn, articulated, closed around the **sash strap**.
Full numbers in the spec's `verdict_measured` and route log
`pipeline/b08-arm-route-0819.md` §18.

**The standing lesson for any lane touching a prompt on a ControlNet route:
`--scale2 0.3` was never measured as robust, only as untested.** It carried the
object for exactly the one text it was measured with. A conditioning strength is
a property of the *pair* (hint strength, prompt), and nine words at fixed
strength is enough to lose the object. Re-verify the object after any prompt
edit; do not inherit "0.3 works" across a wording change.

**And an extension of §17's probe rule, which this frame forced.** §17 said
publish the **material**, not just the luma. §18 says **a colour predicate
cannot decide that material on a figure whose clothes are skin-coloured**: the
guard's cream shirt reads R−B 34.7 against his skin's 42.6–49.7, and the first
probe placed here by colour landed on a **sleeve** at 100 % "pale" — it would
have passed a naive material test and produced a clean, wrong number. Guard
boxes are placed by eye at 5x and published with their R−B alongside the luma.

**Canon filing, apply-not-invent (a).** `pipeline/canon.yaml` `ep2-guard-hair`
scoped itself to beats 5, 6, 7, 9, 10, 11 — **beat 08 was missing and it is a
guard beat**, the two-hander itself. Added as an application with a dated note;
nothing re-ruled. The gap was not free: putting beat 08 in scope immediately
surfaced two specs written **2026-08-18, six days after the canon**, both asking
for "a tall bald guard in a brown cloak" —
`ep2-b08-boardcomp-0818` and `ep2-b08-twofig-gesture-0818`. Both have already
run and carry an `outcome`, so both are acknowledged as history rather than
edited (rewriting a scored spec's prompt falsifies what its frame came from).
The same six-beat list appears in `review/ep2-picks/done-definitions.yaml`
`what_this_releases` and `guard_plates_are_miscast_0816`, so the record that
backs the suppression list carries the dated note.
`check_canon_drift.py` 1 → 0 fail; `lint_genome`, `test_pipeline` rc=0.

**Canon filing (b): the goblin's trousers are GENUINELY UNRULED, and are NOT
ruled here.** Both the parent and this frame put him in full teal trousers to
the ankle; twinsipa had him bare-legged with a tan loincloth. Checked against
what is actually ruled: `ep2-goblin-design-adult` ratifies the identity wording
`lean wiry adult goblin man, green skin, bald head, patchwork cloak` — a cloak
and nothing below the waist — and the founder's words on
`/review/ep2-goblin-design-0819` (*"well b definitely and the damn goblin"*)
chose a **build**, not a wardrobe. **The B evidence does not settle it, and the
pixels are why:** the four adult-B tiles he approved show four different lower
halves — b07 a long tunic over dark leggings, b14 loose pale trousers, b19 bare
green legs and bare feet under a cloak, b17 wrapped greaves and boots. Nor does
any input to beat 08 assert legwear: `b08-ref-goblin-0819.png` is a
head-and-shoulders crop that shows nothing below the collar, and the prompt says
nothing. So the trousers are an **unasserted attribute the model is inventing
per frame**, which is the standing shape of every attribute this beat has lost.
Filed as one taste card for his next batch, with pixels; **no conformity verdict
is recorded either way.**

---

## Beats 03 and 13: the composite route closes the re-render wave's last two plant misses (2026-08-20)

Both beats had a plate drawn the night before whose **character passed and whose
plant did not**, and both are now inits that a 0.30 pass converted on the first
fire. One GPU fire each, one seed, no retries, **$0**.

| beat | what r1s1's own verdict said | what was composited | outcome |
|---|---|---|---|
| 03 `bad-cover` | *"FAIL on the beat, PASS on the character"* — plant was "a branching stem with six to eight leaflets", and "he is not behind it, not using it, not attempting to hide" | weed removed whole; one canon two-leaf sapling drawn **between the camera and him** at 38.4 cm | **PASS** on the one variable |
| 13 `the-shade` | *"THE BEST OF THE THREE… PASS on cast and on pose; FAIL on the plant"* — "NO IDENTIFIABLE SAPLING" | purely additive: one canon sapling drawn beside him, crown at his measured knee line | **PASS** on the one variable |

**Beat 03 is the first rung in this family whose blocker was not only
cardinality.** Beats 15 and 19 each closed a wording ladder on a COUNT. Beat 03's
`done_when` is a **RELATION** — "the cover is comically inadequate" requires the
plant to occlude him — and a relation between a figure the sampler has already
placed and a plant it draws where it likes is no more a knob than a numeral is.
So the relation was composited too, and it held.

### The two findings worth stealing

**A THIN-STRUCTURE SWEEP IS THE WRONG MATTE ON A TEXTURED FIELD, and there is a
replacement.** `beat15_listener_composite.py` removes its weed with a row
running-mean test because *its* field is flat (lum 212, std 4.7). Beat 03's field
is hundreds of hard diagonal blade strokes; the same test flagged 33841 px, the
grown footprint took **85% of the box**, and the clone-fill returned a smooth
rectangle with straight edges — rejected at 1x. A **seeded colour flood** (4
measured seed windows, a rule the field does not satisfy) takes **28.5%** and
leaves every blade around it untouched. And then nothing can be cloned into the
hole either: a nearest-in-row clone across a 40–80 px vacancy repeats the same
few source pixels and came back as a ladder of horizontal dashes. **Per-row
interpolation from the vacancy's own boundary** asserts no structure it cannot
see, and the mask hands the texture back to the sampler.

**That was the pre-registered risk (FAIL-SMEAR) and it did not fire.** The cleared
region came back reading as field. So *flood + boundary-fill + 0.30* is now a
demonstrated route for taking an object out of a hard-textured plate, which is
the case the flat-field method could not reach.

Beat 13's own named risk, **FAIL-PLANT-DISSOLVES**, also did not fire, and it was
the harder bet: that plate is green foliage edge to edge and the plant's colours
were sampled from it, so it is the **lowest object-to-ground contrast any
composite in this house has been dropped onto**.

### The pass tell is a POSITIVE one, and both show it

`composite-init-pattern.md` §7: *"if you cannot see a difference between your
composite and the output, the pass is a paste."* Beat 03's blades gained a lit
internal highlight, its stem was re-drawn thinner, and **the sampler deleted the
three root blades the compositor drew**. Beat 13's outline picked up the frame's
line weight and its stem gained a taper and a rooted base the composite never
had. Highpass sigma-3 std inside the mask: **10.25 → 9.17** and **17.05 → 15.84**
— it *smoothed* the drawing rather than adding detail, which on a cel frame is
the right direction.

### One number a later lane would otherwise misread

**`max change outside the mask is 0.0` is a claim about the COMPOSITE, not about
the OUTPUT.** These two samples changed **40245 px** and **24822 px** outside
their masks. That is not the sampler repainting the figure: the extents are the
mask bbox plus a ~20 px halo — exactly what `padding_mask_crop=64` crops, resizes
and pastes back — and only **587** and **239** of those pixels exceed a diff of 8.
Both face boxes are **maxdiff 0**. Anyone reading the parent specs' 0.0 as an
output invariant would score every job in this family a failure.

### Four smaller corrections the pixels forced, each caught by a check rather than by luck

- **An outline that is not in the alpha is half an outline.** Rim strokes straddle
  the polygon edge, so with alpha = fill only, their outer half lands where
  `al=0` and is masked away. Result: 1 px hairlines, and blades that read as flat
  grey discs.
- **A soft alpha edge over a black trouser leg is not a drawn line.** C9 read a
  darkest drawn luma of **7** and it was the *plate* showing through alpha
  0.02–0.2. Measured on the solid interior (al > 0.9) it is 44 against the plate's
  16.
- **LANCZOS rings, and an unclipped ring is a hole.** Where two outline strokes
  cross, the downsampled rim overshot 1.0; `out*(1-r) + RIM*r` with r > 1 drives
  the result negative and clips to black.
- **A stem width is a fraction of plant height, not a constant.** 9 px is right on
  beat 03 (head 232 px); on beat 13's close-up (head 435 px) the same 9 px read as
  a bent wire. Both now sit near 3% of plant height, where beat 19's passing stem
  also sits.

C8 fired once for real on beat 03 — angling the blades up pushed 139 px of tip
above y=700, the line below which nothing of his head, face or chest lives — and
**the plant moved, not the threshold.**

### What is still open, on the record rather than folded into the pass

- **Beat 03's performance.** r1s1 said he *"reads RESIGNED, not caught out"*. This
  rung declared that out of scope in advance and it is still true: the size and
  position relation lands, the acting does not. That is the pose/motion lane's
  variable and it is the next thing this beat needs.
- **Beat 13 is still the DIM plate**, and its background sprig at x 660..832
  y 80..270 is still in frame by choice. A 0.30 pass over 4.1% of the frame cannot
  reach a plate-level exposure and did not pretend to.
- **Beat 13 cannot be scored in centimetres and says so.** No horizon is in frame,
  so no ground plane exists to build. Its scored clause is the RELATION (crown at
  his measured knee line); the 25.9 cm figure is printed beside it with the
  disagreement that produced it — a 40 cm plant at his exact depth would put its
  crown at his brow, and his seated mass is 2.5 head-heights where a real one is
  ~4.

**The composite-then-inpaint route is now 4 for 4** (beats 15, 19, 03, 13) at
getting a canon two-leaf sapling into a frame that four wording ladders could not.

### A filer bug that was blocking beat 15's cut slate, fixed in passing

`mac_enqueue.known_beats` matched one spelling of a beat entry — the four-space
`    15: {` inside the `DRAFTS` literal — and `plate_scratch.py` also grows beats
by **assignment** after that literal closes. `DRAFTS[15] = {` at line 5526 is beat
15's whole entry and a column-0 assignment is invisible to a four-space regex.

**The guard was wrong in the REFUSING direction, which is why it was quiet.**
`main` checks the set before it files anything and exits 2 with *"plate_scratch.py
has no inline prompt for beat(s) [15]"*; plate_scratch could draw beat 15
perfectly well. Nothing errored — work simply never got queued, and beat 15's cut
slate sat blocked on the filer rather than on a defect. `known_revs`, three lines
below, already handled **both** of its spellings and said so in its docstring; the
asymmetry was the whole bug. The selftest asserts beat 15 specifically **and** the
general invariant — every beat plate_scratch spells either way is visible — so a
third spelling fails on the file itself rather than on a hand-kept list.

## Appended 2026-08-20 by the beat 08 staging lane — the second rung, and the number is now closed

**`ep2-b08-scale50-0820`, FAIL, and it ends the tuning.** One variable,
`--scale2` 0.3 → 0.5, the grip prompt held byte-identical. **The board came all
the way back** (authored quad 0.757 of pixels below luma 80, against 0.235 at
0.3 and 0.758 on the boardless-prompt frame) **and the cream shirt and white
sash merged into the brown wrap on the way** — sleeve RGB (161.6,115.4,80.3)
against (217.9,193.4,165.0) at 0.3, i.e. the 1.0+0.8 collapse arriving at
1.0+0.5. Frame luma 114.4, monotone in the second net's strength.

**The reusable form of it, for any lane composing two ControlNets: one knob buys
the object AND the garments, and they move in opposite directions.** The usable
window on this beat is narrower than 0.3–0.5, not the 0.3–0.8 the route had
assumed. Do not read "a stronger object net just draws the object better" —
past some value it is also redrawing everything else, and garment BOUNDARIES go
before limbs do (both arms survived here; the shirt did not).

**Two clean separations, each worth more than the frame.** (1) **The hair is a
prompt-budget problem, not a conditioning problem** — conditioning rose by two
thirds and the guard stayed bald, so at 73 tokens crowding alone loses `light
sandy hair`. The B8 instrument's two inputs are now individually calibrated.
(2) **Where a hand goes is not the object net's to decide** — strengthening the
board moved the far hand by nothing; it sat at the chest on the strap at 0.3 and
sits there at 0.5. Position belongs to the pose hint and the prompt.

**Route status: every free lever on beat 08's grip is now spent, and the next
one is argued rather than guessed.** Wording summons a grip and binds it to the
wrong object while costing the board; strength restores the board and moves no
hand while costing the wardrobe; the guidance window was excluded two rungs ago.
What remains is a short stroke for the gripping hand in the board hint at the
authored L-wrist, at `--scale2` 0.3 with the prompt back to 64 tokens. That
would be the first figure ink ever placed in that hint and it is **still owed
the five tracing losses in writing before anyone authors it** — the point here
is only that it now has the evidence it was waiting for. **Not taken by this
lane. `ep2-b08-scale30-0820` remains the best frame on beat 08; no pick, no
plate_ack, no cut.**

---

## Appended 2026-08-20 by the beat 08 staging lane — the grip mark, argued against the five tracing losses BEFORE it is authored

Three rungs (§17, §18, §19 of `pipeline/b08-arm-route-0819.md`) each closed a
free lever and each ended by naming the same next one: **figure ink in the board
hint.** Every one of them also said the same thing about it — *it is owed the
five tracing losses in writing before anyone authors it.* This is that writing.
It is filed before any code is touched, and it changes the proposal.

### 0. One measurement first, because it re-describes the defect

The parent's verdict says *"the sleeve ends in a rounded mitten-like form and the
board's top edge tucks under it — no fingers, no thumb, no grip."* That is true
and it is not the whole defect. Measured on
`farm-out/ep2-b08-scale30-0820/ep2-b08-scale30-0820-scale30.png`, geometry-placed
boxes, luma > 200 for the cream masses:

| form | centroid | distance to authored `Lelb` (627.2, 579.7) | distance to authored `Lwri` (621.7, 668.4) |
|---|---|---|---|
| the drawn fist with individual fingers | **(620.3, 577.9)** | **7.1 px** | **90.5 px** |
| the digit-free cream lobe on the board's top edge | (679.2, 630.4) | 66.6 px | 68.9 px |

**The guard's near hand is drawn one joint short.** It is not missing and it is
not badly drawn — it is a well-articulated fist sitting 7 px from the authored
*elbow*, closed around a shoulder strap the model invented, with 90 px of sleeve
fabric continuing down to the board and terminating in a lobe. So the beat's
failing clause is not "the model cannot draw a hand at this scale" (it drew one,
here, in this frame, at 0.3, with fingers). It is **"the arm's terminus is in the
wrong place, and the object net has never been told where it is."**

That matters for the argument, because it is the difference between asking this
net for a *drawing* — which the five losses say it will not give — and asking it
for a *position*, which is the one thing it does give.

### 1. The five losses, stated as what they actually are

All five are `xinsir/controlnet-scribble-sdxl-1.0` conditioned on hand-authored
figure ink, route log §8–§10.

| # | rung | ink class | what the net did |
|---|---|---|---|
| 1 | `ep2-b08-cnetplate-0819` — contour, 7 px, 0.80 | whole-figure enclosure | traced 97.7 % of authored ink; **flat mannequin**; the arm ended in nothing |
| 2 | `ep2-b08-cnetplate-r2-0819` — contour, 7 px, 0.45 | whole-figure enclosure | traced 94.4 %, surface-only; aimed wide **by construction** — and **drew a good hand with an extended index finger at the enclosed arm terminus** |
| 3 | `ep2-b08-cnetplate-r3-0819` — contour, 7 px, 0.28 | whole-figure enclosure | **staging LOST** — drawn but uncontrolled |
| 4 | `ep2-b08-cnetplate-r4-0819` — contour, 3 px, 0.45, **+ a 1 px finger stroke** | thin **open** stroke at the arm's end | 98.3 % traced, 83.4 % of strongest gradients on ink — and **the finger stroke did not carry; the hand regressed to a fingerless wedge** |
| 5 | `ep2-b08-cnetplate-r5-0819` — skeleton, 7 px, 0.45 | medial axis, **non-enclosure**, inside the figures | every composition clause failed; the ink was **DRAWN AS LIGHT** (+47.0 luma on the guard's spine column) |

§10's synthesis, which is the thing to beat: *"any hint this net can read is a
hint it traces, and any hint it cannot read it ignores or draws. There is no
setting that yields a model-drawn figure inside an authored composition."* And
its ruling: **hand-authored geometry is closed as a composition lever for beat 08
on this net.** That ruling is real and it is not being quietly stepped over here.

### 2. The proposal as named does NOT survive, and loss 4 is the reason

Every rung that named this lever called it *"a **short stroke** for the gripping
hand."* **A short stroke is loss 4 exactly** — an open, thin mark appended at the
end of a limb, in this hint, on this net. It failed at 0.45 with a whole contour
around it to hold it; it is being proposed at 0.3 with nothing around it. §9 did
not merely record that failure, it ruled on it: *"whatever the class, B4b needs a
**hand-sized mark** at the end of the arm — a 1 px finger has now failed once."*

**So the named proposal is rejected by this lane and is not what gets authored.**

### 3. The variant that does survive, and precisely why it is a different class

**A closed, hand-sized loop at 7 px stroke, centred on the authored L-wrist
`(621.6704, 668.4352)`, straddling the board's top edge.** Not a stroke — an
enclosure. Five properties, each answering a specific loss:

**(a) It is enclosure-class, which is the one thing this net reads.** This is not
an inference from the losses; it is the *positive control already in the parent
frame.* The same net, the same hint file, the same 0.3, the same seed put a
closed quad on screen at the authored position and the authored 9° tilt. An
enclosure at 0.3 in this rig is a measured capability, not a hope.

**(b) 7 px, not 3 px, and loss 2 is the one positive in the loss set.** §9's
finding was that stroke weight is a *precision* dial with the opposite sign to
the assumption: 3 px is a single unambiguous edge locus and the outline snaps to
it (loss 4's wedge); **7 px is an ambiguous ribbon and the model fills it with
its own drawing** — which is why loss 2, at 7 px, produced an articulated hand at
an enclosed arm terminus. The grip loop is loss 2's single success extracted from
loss 2's failure: same class, same weight, same kind of location. The board hint
is already at `STROKE = 7`.

**(c) The scope is one body part, not a character.** Losses 1–4 conditioned the
entire silhouette of two whole bodies, and what they cost was *character*:
identity, wardrobe, linework, face. The loop is ≈ 46 × 34 px — about 0.11 % of
the frame — and it asserts nothing about the guard's face, his hair, his
wardrobe, his pointing arm, or the goblin. Those are the four things the losses
destroyed and the loop is silent on all of them. **This is the load-bearing
distinction and it should be read as scope, not as size:** a hint that says
"this character's edge is here" replaces the model's drawing of the character; a
hint that says "one prop-contact boundary is here" does not.

**(d) It touches no limb the hint does not already touch.** The hint's selftest
pins the guard limbs its ink meets to exactly `{gripping forearm, torso, L
thigh}` — the three a clipboard at the hip occludes. A loop of half-extent ≤ 23 px
at `Lwri` stays inside that set with room: the nearest *new* capsule is the
gripping upper arm at 88.9 px and the neck→Rhip torso bar at 81.6 px. **The grip
mark can be added without widening the figure-ink carve-out by one limb**, and
`--selftest` will assert that as pixels rather than as a claim.

**(e) It is the first time the two nets agree at one pixel.** The openpose net has
authored the guard's L-wrist at `(621.6704, 668.4352)` since `562911c8`, at scale
1.0, and §14 already established that **the pose net's binding is not rigid** —
an authored limb gets overridden when the checkpoint prefers a different reading.
Section 0's 90.5 px is that override, measured. The scribble net has never been
told anything about that coordinate. The loop is not a new *kind* of instruction;
it is a second, independent assertion of an existing one, from the net whose
placements this frame demonstrably obeys.

### 4. The objection that nearly killed it, and the answer is in the parent frame

§16's mechanism: for a scribble net a black pixel is not an absence of
instruction, it is *"no edge here"* — so a 99.7 %-black hint asserts "no edges
anywhere". Read literally, **the interior of the grip loop would be an assertion
that the hand has no finger creases**, i.e. the hint would be *commissioning the
mitten.*

That is a 0.8 phenomenon and the parent frame proves it. At 0.8 the frame
flattened everywhere and the wardrobe became one robe; at 0.3 the parent's own B6
verdict reads *"hair with visible strands, folds in the sleeves, the gold harness
clasp and belt buckle both legible, **a well-drawn fist gripping the harness
strap with individual fingers**."* **Both halves of §16's mechanism are already
calibrated at 0.3 inside the very frame this rung derives from:** the "no edge"
half is weak enough that the model draws finger creases anyway, and the "edge
here" half is strong enough to place a closed form at an authored location and
tilt. The loop asks for one more instance of the second and relies on the first
staying weak.

### 5. What the losses still predict, pre-registered as named failure modes

Loss 3 is the live one and it is not argued away. At 0.28 figure ink stopped
binding, and 0.3 is 0.02 above it; §18 further showed 0.3 is not robust but
**prompt-coupled** — nine words erased the board entirely at unchanged strength.
The loop carries roughly a tenth of the board's ink. The honest position is that
loss 3's number came from a *single-net* frame while the board binds at 0.3 in
*this two-net rig* where the residuals add — so loss 3 does not transfer
directly, but it makes "ignored" the single most likely outcome.

| mode | class | what it looks like | what it would settle |
|---|---|---|---|
| **L1 IGNORED** | loss 3 | hand still at the elbow, board unchanged | small-scope figure ink cannot bind at the only strength the wardrobe survives → route leaves this net |
| **L2 FLAT-TRACE** | loss 1 | a hard-rimmed, digit-free blob at the wrist | 7 px is not a ribbon at 0.3; §9's precision finding is scale-dependent |
| **L3 MERGE** | loss 5 | loop and board top edge read as one enclosure — a bump on the board, or a luminous bar at the wrist | non-enclosure behaviour re-appears when two enclosures touch |
| **L4 BOARD-COST** | §18 | the board degrades because the *pair* (hint, prompt) moved | §18's lesson generalises from prompt edits to hint edits |
| **L5 THIRD-HAND** | new | a hand at the wrist **and** the existing fist at the strap | the checkpoint will not relocate a committed hand, only add one |

L4 is mandatory to measure, not optional: §18's standing lesson is that a
conditioning strength is a property of the *pair*, and this rung moves the other
half of the pair.

### 6. Verdict on the argument, and the fallback named in advance

**An honest version survives — but only as (3), and (3) is not the thing three
rungs kept naming.** The route asked for a stroke; the record says a stroke is a
recorded loss and a 7 px closed loop at an arm terminus is the record's one
success. The sample is therefore authorised by this lane as a **hand-sized closed
loop**, one variable (the hint), `--scale2` held at 0.3, the prompt reverted
byte-for-byte to the 64-token parent text so §18's crowding goes with it, seed
pinned at 20260819.

**Two guards on the authoring, so this cannot become a second variable.**
`build()` keeps its current default and `--selftest` asserts the default hint is
still byte-identical to `38cd39da…` — the parent's hint stays reproducible on
disk and the grip variant is opt-in. The two hints then differ **only** by the
loop, provably, rather than by assertion.

**And the fallback if it loses, named now so nobody has to invent one under
pressure: composite-then-inpaint**, which went **4 for 4 today** (beats 15, 19,
03, 13) on precisely this shape of problem — a RELATION between a figure the
sampler has already placed and something it draws where it likes. Beat 03's entry
above says it in general terms: *"a relation between a figure the sampler has
already placed and a plant it draws where it likes is no more a knob than a
numeral is."* "A hand grips this board" is that same relation. Drawing the hand
into the parent plate and running a 0.30 pass with `padding_mask_crop=64` touches
neither net, risks neither the board nor the wardrobe, and is the instrument this
house has the most evidence for. It is **named, not taken** — the hint rung goes
first because it is one variable on a recipe already on the card, costs ~30 s of
GPU, and keeps beat 08's plate a single-pass render rather than a two-pass
composite.

**`ep2-b08-scale30-0820` remains the best frame on beat 08. No pick, no
`plate_ack`, no cut, and the words "complete plate candidate" are not used.**

## Appended 2026-08-20 by the composite-plate motion lane — the three converted plates get their first motion take, and two of this lane's own instruments broke on the same mechanism

**One rung, three samples, one seed.** `ep2-b15-listenmotion-0820`,
`ep2-b03-covermotion-0820`, `ep2-b13-shademotion-0820` — the b14 crf-10 LTX
recipe as cloned for beat 19, fired once on each of the three plates the
composite-then-inpaint route converted, at seed **20260820** on all three, so a
difference between them is a difference between the **plates**. Only the init
picture and the words change. rc=0 on all seven steps of all three, 121 frames
each, 268/263/263 s, **$0**. All three FAIL. Nothing is proposed for the cut.

### The shared defect, and it was named in advance on one of the three

**HE STANDS UP AND WALKS OUT OF FRAME.** Beat 03 rises at f090 and is gone by
f114; beat 13 rises at f084 and is gone by f114; beat 15 stands at f100. On a
five-second beat that leaves the last quarter with no goblin in it.

**Every one of those three prompts carried `standing up` and `walking out of
frame, leaving the frame` in its NEGATIVE** — beat 13's had `sliding down a
trunk, sliding, standing up, getting up` as its *first four terms*. None held.
That is the **seventh, eighth and ninth sighting** of *positive placement beats
negatives*, and the first time this lane had written the fail mode down in
advance **with its remedy already named**: beat 03's spec pre-registered
F-STANDS-UP and said the answer was a positive placement of the down attitude,
"not an eighth wording of the prohibition".

### THE FINDING WORTH STEALING: a noun in the prompt is a placement wherever it appears, including inside an idiom that does not mean it

Beat 15 is the only one of the three whose **plant** clause failed, and it did
not fail on cardinality. Two leaves and one stem throughout — beat 19's
F-PLANT-REVERT did not fire. What fired is an **object binding**: at f000 the
sapling is rooted at frame left; by f060, at 2x, **the stem is gone and his
forearm is where it was**, holding the leaf pair level with his eyes; by f100
it is back in the ground.

The prompt's plant clause said `ONE thin stem, TWO leaves, ROOTED IN THE GRASS`
— positive, first-class, unambiguous. It lost to four words in the action
clause: **`talks to them FROM A HAND'S WIDTH AWAY`**. In English that `hand` is
a unit of measurement. To the sampler it was a placement.

**This is §18's b08 grip finding arriving from the other side.** There, nine
words asserting `fingers and thumb gripping the clipboard edge` drew fingers and
thumb, correctly articulated, **around the sash strap** — the right hand, the
wrong object. Here a hand nobody asked for found the right object. Same law.
And note what did *not* save it: `He stays sitting in the grass with his hands
on his knees` is in the same prompt **four words later**. **A competing
placement does not beat an incidental noun; the noun has to go.**

The fix is a **prompt** change and cannot be a script change: `from a hand's
width away` is the founder's own sentence in the approved node.md:98.

### TWO INSTRUMENTS BROKE, BOTH ON THE SAME MECHANISM, AND BOTH WERE THIS LANE'S OWN

Both bars were pre-registered by this lane before the pixels, and both are
**confounded by the subject leaving the frame**. Neither remedy was invoked.

- **A2, the skin probe, on beat 03: +131.8 luma, far outside its ±25 bar — and
  it is neither an exposure fault nor an identity fault.** By f120 **he is not
  in the box**; it is sitting on open sky. The tell is in the number the bar did
  not read: `luma_std` collapses **18.5 → 3.0**, because a flat box is an empty
  box. Re-placed by eye at 5x on f102 — cheek box (296,86,352,124) — it reads
  luma 113.9 / R−B 37.2 against f000's 98.0 / 33.0, i.e. **+15.9 and +4.2, both
  inside the bar**, and at 1:1 he is plainly the ratified lean adult. **A fixed
  probe box is an identity instrument only while the subject stays under it.**
- **A5, whole-frame luma, on beat 13: +44.4, which is growmotion-blowout
  territory — and the exposure never moved.** The track is 97.7 / 97.3 / 96.6 /
  96.5 / 96.5 / 96.5 / 96.4 **flat to f060**, then 91.4, 91.8, and only then
  100.4 / 109.1 / 134.4 / 142.1 as he rises and exits. The rise is **his dark
  mass leaving a bright field.** Beat 03's is the same shape with the sign
  flipped mid-clip: 143.4 flat to f030, **155.7 at f040 when he ducks his dark
  mass out of the upper frame**, 130.5 at f100 when he stands and fills it,
  156.2 at f120 when he has gone. **A whole-frame luma delta is an exposure
  reading only while the subject's footprint is constant.** Scoring beat 13 a
  blowout and firing the pre-registered seed re-roll would have spent a GPU fire
  on a fault that does not exist.

**Generalised, because this is the third instrument family this ladder has
retracted:** an instrument whose window is fixed in the frame measures the
SUBJECT only while the subject stays in the window. The growmotion mask lost the
fig to a hue change; these two lost him to a walk. In all three cases the number
stayed clean and confident while its premise died — which is why the dispersion
statistic (`luma_std` here) is worth publishing beside the mean, and why the
frames get opened.

### WHAT HELD, AND ON THE HARDER PLATE

**The composited two-leaf sapling survived 121 frames on beats 03 and 13** —
including, on beat 03, a full stand-up and exit, after which it stands alone in
the middle of the frame still exactly one stem and two leaves. Beat 13's is the
stronger of the two: that composite was dropped onto **green foliage edge to
edge**, the lowest object-to-ground contrast any composite in this house has
been given, and neither F-PLANT-REVERT nor F-PLANT-DISSOLVES fired across 121
frames. Beat 19's motion take lost exactly this clause.

**And beat 03's acting variable moved for the first time.** r1s1's plate verdict
was *"he reads RESIGNED, not caught out"*, and the composite pass fixed the
geometry without touching the acting. Here, from about f036 his head and
shoulders drop until by f060 his head is near grass level behind the plant, and
he holds it to f084. It reads as ducking. **One positive placement of the action
did it.**

Identity held on all three (beat 15's is the tightest: **−3.6 luma and +5.5 R−B
over eighty frames** on its pre-registered box). Camera locked on all three. No
freezes; beat 13's own pre-registered F-NOTHING-MOVES prediction was **wrong** —
the head is in continuous motion from f004, it simply tips **forward into his own
knees** instead of sideways into the shade, taking his face out of view for fifty
frames.

### Two things done before the GPU that are worth copying

- **The anchor was measured against the recipe, not assumed.** 832x1216 →
  704x1280 discards **81.7 original px per side**. Beat 13's composited sapling
  begins at original **x=13**, so a centred crop would have cut **72 px off the
  subject of the clause the whole composite route exists to satisfy** — on the
  beat whose r1s1 verdict read *"NO IDENTIFIABLE SAPLING"*. Beat 03's mask
  reaches x=67 and is also clipped. Both filed `--anchor left`; beat 15 clears a
  centred crop with 41 px to spare and keeps the default.
- **The framing assert is the MASK, not a colour predicate**, and it is the
  reason this file differs from beat 19's `assert_framing.py`, which found its
  fruit with a hue window. These are green plants on green fields. The composite
  mask is the plant's own authored footprint; pushed through the identical
  cover-crop it gives the exact output bbox with no predicate at all. **All three
  reproduced the Mac's number exactly on the box** — `x 70..485 y 561..1235`,
  `x 14..265 y 681..1236`, `x 41..240 y 300..636` — two machines, two Pillows,
  zero drift.

### One guard-adjacent act, said out loud

`box_enqueue.plate_problems` reads a job's `--src` off
`origin/farm-results-rtx5090` **and nowhere else**, and the courier has pushed
nothing to that branch since **2026-08-19T17:54** — the tip before today was
itself another lane's hand-carry of beat 04's plate for the same reason. Beats
03's and 13's sapcomp plates were therefore **carried across by hand**,
byte-identical, and re-hashed on the branch afterwards (`7d3ab86a…`,
`bb0ad70c…`). **The alternative was `plate_ack: "unfetchable"` and it was not
taken:** half that guard's demonstrated value is declining to wave through a
picture it cannot see, and one of the two jobs that hit it in the 2026-08-14
wave was cropping the wrong beat's plate. The remedy for an unfetchable plate is
bytes.

### Rung 2 is filed and running, and it is one variable on all three

`ep2-b15-listenlast-0820`, `ep2-b03-coverlast-0820`, `ep2-b13-shadelast-0820`.
The action clause stops describing a **movement** and places **the last frame**
as a fact; the **negative is deliberately unchanged**, because it already named
`standing up` and did not hold, and leaving it there is what makes this a test of
the positive. Same init, same seed, same flags — rung 1 is a true control.
Precedent with numbers: `ep2-b04-headlock-0820` moved one clause out of an
instruction and into a placement and cut head-band travel **64.7 px → 4.7 px**.
**Its cost is pre-registered here as G2 and is the likeliest failure:** that rung's
lock took the eyes with it (eye-band interframe 0.356 → 0.126) and the clip went
too calm. **A clip that holds the last frame by holding every frame is a FAIL of
rung 2, not a pass.** Beat 15's rewrite carries the idiom fix for free.

### One scar re-earned, recorded because it is in CLAUDE.md already

`pipeline/measure_sapcomp_motion_0820.py` was committed with
`subprocess.run(text=True)` and no `encoding=`. The suite has a test for exactly
that and it went red the moment the file landed; the file was committed in
between because lint and tests had been run **before** it was written and not
after, and the suite's output was piped to `/dev/null`. *Run tests as their own
step and read the exit code BEFORE committing* — third sighting.

---

## Appended 2026-08-20 by the beat 08 staging lane — the grip mark FIRED, and the mode that fired was not one of the five

`ep2-b08-gripmark-0820`, **FAIL**, and the argument above is falsified in its
load-bearing step. Full numbers in the spec's `verdict_measured` and route log
`pipeline/b08-arm-route-0819.md` §20; evidence
`farm-out/ep2-b08-gripmark-0820/EVIDENCE-b08-gripmark-0820.png`.

**What the argument got right.** The named proposal — "a short stroke" — really
was tracing loss 4, and rejecting it was right: the mark that got authored, a
closed 7 px hand-sized loop, **bound**. The pre-registered most-likely mode (L1
IGNORED, loss-3 class) did NOT fire. 511 gold pixels, centroid **(615.7, 681.2)**,
**14.2 px** from the authored L-wrist. Figure ink at `--scale2` 0.3 in this
two-net rig is above threshold, and loss 3's 0.28 number — measured on a single
net — does not transfer. L2 did not fire either: the traced form is fully drawn,
with a rim, a dark inset and a highlight.

**What the argument got wrong, and it is the useful half.** The loop came back as
**a second gold belt clasp**. §3(e) of the argument claimed the mark was
different in kind because "the openpose net has authored a wrist at exactly
(621.6704, 668.4352) since 562911c8 … the grip mark is the first time the two
conditions agree at one pixel, and agreement between nets is not a new class of
instruction." **As measured, the pose keypoint contributed nothing.** Neither did
the prompt, which says `clipboard lowered in one hand`.

### The rule to steal, and it outlives this beat

**On a scribble net you choose the SHAPE and the PLACE. You do not choose the
NOUN.** §10 established that any hint this net can read is a hint it traces; the
corollary this frame adds is that **what gets traced is named by the surrounding
pixels**. Every one of the five tracing losses drew ink ON a figure, so the ink
WAS the silhouette that named itself and the question never arose. This is the
first authored mark on the route whose intended noun differed from what its
neighbourhood implies, and the neighbourhood won: a rounded closed form on a belt
line beside a leather strap is hardware. **Place an authored enclosure only where
the scene already implies the object you want** — which is exactly why the board
hint has worked four times. A rectangle at a hip, beside a hand, is a board.

### And a second rule, for anyone composing hints anywhere

**The effective conditioning load is (strength x INK), not strength.** The hint
gained 29% more ink at an unchanged 0.3 (fraction 0.00324 → 0.00418) and cost the
same two clauses that raising strength to 0.5 and adding nine prompt tokens each
cost: the board fell **0.754 → 0.234** (the wording rung's was 0.229) and the
guard went **bald** with BOTH of B8's calibrated inputs held at values that
passed. §18's lesson generalises — a conditioning strength is a property of the
triple (strength, prompt, ink), and **"0.3 is the scale that works" must not be
inherited across a HINT edit** any more than across a prompt edit.

### What held

B0 with the new sha in the sidecar and `prompt tokens: 64` in the log; B1 two
figures, exactly two hands (**L5 third-hand did not fire**), zero boards so no
duplication; B2 +55.5; B7 22.9 / 18.7 on boxes **re-placed by eye at 5x** and
published with luma AND material — the parent's guard forearm box landed on a
**sleeve** here, the third frame running that admissibility rule has earned
itself; B4b-i **better** than the parent at 39.8 px; B4c; B6 intact; the pointing
arm untouched exactly as the hint's selftest promised. **The loop did not act
globally.**

### One operational note for every lane on this box

**The courier push has failed 23 times in a row** (`push exceeded 60s and its
process tree was killed`). `farm-out/` on the rtx5090 is box-only right now and
this result had to be pulled by `scp`. Nothing is lost, but nobody should read an
empty `farm-results-rtx5090` as "the job did not run".

**Route status: every free lever on beat 08's grip is spent, including the one
three rungs deferred.** The fallback the spec named in advance is now the route —
**composite-then-inpaint** on the parent plate, 4 for 4 on 2026-08-20 across
beats 15, 19, 03 and 13, and the one instrument that never has to ask this net
for a noun because the compositor draws the noun and the sampler only re-renders
it. **Not taken by this lane. `ep2-b08-scale30-0820` remains the best frame on
beat 08; NO pick, NO plate_ack, NO cut, and beat 08 does NOT have a complete
plate candidate.**

### Rung 2 landed the same night: the placement holds him in place on all three, and only ONE of the three paid the G2 cost

`ep2-b03-coverlast-0820`, `ep2-b13-shadelast-0820`, `ep2-b15-listenlast-0820`.
One sentence changed on each — same init, same sha, same anchor, same seed
20260820, **the negative byte for byte identical**, every flag identical. rc=0
on all three, 121 frames, $0.

**THE MECHANISM IS SETTLED. A placement of the last frame holds this engine
where a negative cannot.** Beat 03 was out of frame at f114 and is now still
crouched behind the plant at f120. Beat 13 was walking away at f114 and had
folded its face into its own knees from f024; it is now still folded small with
its knees up **and its face readable in every frame**, which satisfies the
founder's *"no slide, he sits down beside it"*. Beat 15 stood at f100 and now
never stands. Three for three, against negatives that had already failed three
for three.

**AND THE COST SPLIT THE SET, WHICH IS THE FINDING.** G2 — pre-registered off
`ep2-b04-headlock-0820`, whose lock cut head travel 64.7 px → 4.7 px and killed
the eyes — fired on two of the three and in two different shapes:

| beat | terminal sentence names | position | cost |
|---|---|---|---|
| 03 | a static attitude (*still crouched down low*) | held | **33 frames dead from f088**, ncc 1.0000 |
| 13 | a static attitude (*still sitting, knees up*) | held | face-band interframe **10.80 → 0.64**, last-20 **24.07 → 0.148** |
| 15 | an **ongoing action** (*head still tilted toward the plant … he is talking*) | held | **none** — FREEZE none, ncc 0.926–1.000, HOLD strength **0.508**, the loosest of all six clips |

**A terminal placement that names an ONGOING ACTION appears to hold position
without buying it from the performance; one that names a STATIC ATTITUDE buys
it by making every frame the last frame.** One sample across three beats of one
rung — the next thing to test, not a law.

**Beat 13 also settled rung 1's instrument argument by experiment.** Same init,
same seed, same recipe: whole-frame luma **+44.4 in rung 1, −5.0 in rung 2**.
The only difference is that in rung 1 he walked out of the frame. The +44.4 was
the exit and never the exposure. Beat 13 r2 is also the first clip of the six
whose pre-registered skin box is **still valid at f120**, because it is the
first where he is still under it (−3.4 luma, −4.9 R−B).

**Beat 15 fails at the last frame, and the sentence that caused it is the one I
wrote to prevent it.** Deleting `a hand's width away` bought **85 frames** — the
sapling stays rooted to f090 against rung 1's f020 — and then at f105 his hand
closes on the stem and at f120 the plant is uprooted and hanging from his fist.
The prompt's final sentence was **`Nobody touches the plant and nobody picks it
up.`** A negation inside the *positive* prompt is not a prohibition; it is the
phrase `picks it up`, placed. **The rule this beat has now paid for twice: state
only what IS in the shot, never what is absent — and not even inside the
positive.** Both of my fixes reintroduced the noun phrase they were meant to
exclude.

Per-clause verdicts in each spec's `verdict_measured`. No cut consequence: beats
03, 13 and 15 stay slates.

---

## Appended 2026-08-20 by the beat 08 judging lane — the composite route reached beat 08 and beat 08 is the plate it does not fit

A lane took §20's named fallback (composite-then-inpaint, 4 for 4 that day),
wrote `pipeline/beat08_grip_composite.py`, and died mid-judging with its state
recorded as "Round 3 reads correctly" plus a self-caught doubt about its own
detail bar. This lane finished the judging. **`ep2-b08-gripcomp-0820`, FAIL.**
Full numbers in `pipeline/b08-arm-route-0819.md` §21; evidence at 5x in
`farm-out/ep2-b08-gripcomp-0820/EVIDENCE-b08-gripcomp-verdict-0820.png`.

### Three things a lane picking up a dead lane's work should copy

**1. "It reads correctly" was a note about a file the source no longer builds.**
The on-disk init differs from what `build()` produces in **4488 of the hole's
4489 px and zero px anywhere else** — the fill was swapped after the artifact
was written, and `--write` refuses on a failing selftest, so the artifact is
from a round that passed and the code is from a round that does not. *Before
trusting any inherited "it works", rebuild the artifact and diff it.* The two
files agreeing is not the default; here they had already diverged.

**2. The dead lane's own self-catch was wrong, and measuring it was still the
right move.** It suspected its detail baseline was inflated because the ring
included the removed object's outline. It does — by **0.08 of 17.94**. Same ring
pixels, gradient with the fist present 17.94, with it gone 17.86; the *innermost*
annulus is the *coolest* (12.53 at 1 px, 21.4 at 8–10 px), because the gold clasp
and the shirt folds are what make that neighbourhood busy. Re-based five ways
that exclude the object entirely, the fill reads 17–22% against a 45% bar.
**Inheriting a doubt is not the same as inheriting a finding.** Re-base it, and
publish the number even when it changes nothing.

**3. THE BAR CERTIFIED THE WRECKAGE — and this is the transferable one.** The
two fills fail in opposite directions and the pre-registered instrument caught
only one:

| | fill grad | share of ring | bar | what it is at 5x |
|---|---|---|---|---|
| round 3, on disk | **16.04** | **89%** | **PASS** | a ribbed corduroy comb down the strap |
| current source | 3.29 | 18% | FAIL | a smooth blob, strap gone, clasp dangling |

A mean-|gradient| detail bar asks *is this flat?* and nothing else. **A ladder of
streaks is not flat, so it passes at twice the threshold, and an eye rejects it
in a second.** The obvious fix does not work either — `|gy|/|gx|` is **0.64 in
the fill and 0.64 in the untouched ring**, because a fill that continues along a
material's axis inherits that material's own anisotropy. Measured, not assumed.
**Any lane using composite-init-pattern.md §9b's 45% gradient bar should read it
as a smear detector only.** It cannot arbitrate between a fill and an artifact.

### The route finding, which outlives beat 08

**Composite-then-inpaint is licensed where the vacancy's material is continuous
and unstructured. It is not a licence to relocate a part of a figure across its
own clothing.** Beats 15, 19, 03 and 13 all removed an object from a homogeneous
field or dropped a sprite onto one; **not one had to reconstruct a garment
junction.** Beat 08's move opens 4489 px in a harness-strap / cuff / shirt
junction with a gold clasp on its top edge, and the plate holds no clean source
for it — no patch to copy, no axis to continue, no boundary to interpolate.
Three fill families have now proved that. **The operation is wrong, not the
fill.**

### What the composite did buy, because it is real and it is the ceiling

Maxdiff outside the mask **0** over the whole frame, zero stray px, all six of
the parent's published pure-skin probes untouched: GUARD spread **21.7** (bar
25.0, every region ≤ 0.0), GOBLIN **8.1** (every region ≥ +41.6), **B2 +60.6** —
reproducing the parent's published figures exactly, coordinates + luma + material
in §21 per the rule three frames have earned. B4a 0.754 → **0.664**, the drop
being the hand's intended occlusion of the board corner. And the grip is
**half-bought**: real drawn fingers and a thumb at the board's top edge at 5x,
straddling it 1540/1439, centroid **4.9 px** from the authored L-wrist against
the parent's 90.5 — the parent's defect inverted. It still fails `held, not
tucked`: a visible stair-stepped octagonal rim, sitting on the board's outline
rather than closing around it, no contact shading. A sticker of a hand.

### Next rung: named, argued, and deliberately NOT filed

Not a fourth fill. The honest version is to **copy** the fist to the board edge
and leave the original in the init inside the mask, so the sampler removes it
from real pixels. **Not filed, and the reasons are the point.** A 0.30 pass does
not delete a hand — 0.30 is the number that exists to preserve structure — so
the rung must choose a higher strength inside the mask, which re-opens B6, B8
and the wardrobe at the `(strength × ink)` prices §20 measured. That is an
argued tradeoff, not a knob turn. And decisively: **the instrument that would
score its vacancy has just been shown to certify artifacts at twice its bar.** A
render whose verdict cannot be trusted has no consumer. A replacement for the
detail bar comes first, and nothing tried here is it.

**`ep2-b08-scale30-0820` remains the best frame on beat 08. NO pick, NO
plate_ack, NO cut, and beat 08 does NOT have a complete plate candidate.**

## Appended 2026-08-20 by the composite-plate motion lane — rung 3 was ALREADY FILED AND ALREADY RUN, and nobody had looked at it for seven and a half hours

`ep2-b15-listenroot-0820`, `ep2-b03-covermid-0820`, `ep2-b13-shademid-0820`. The
lane that wrote "filing rung 3 now" did file it — commit `2dee7fe7` at 04:33, all
three enqueued, all three run by 04:56, rc=0, 121 frames, 264.7 / 268.3 / 262.4 s,
$0 — and then died before pulling a single frame. **The card was idle and three
finished renders sat unread on it from 04:56 to 12:20.** The first thing a
resuming lane owes a dead one is not a re-file; it is a look at `done/`.

**This lane re-filed them before checking, which is the operational lesson worth
more than the apology.** `box_enqueue.py` refuses a reused id against `ready/`,
`running/` and `backlog/` — it does **not** look in `done/`, so three completed
jobs re-queued clean and one of them re-rendered before it was caught. The two
that had not started were renamed `.DUP-already-ran-0820` in `ready/` on the
`ep2-b02-anchor` precedent. **Check `done/` by task name before you enqueue
anything a previous lane may have filed.**

### And the mistake paid for itself: bit-exact reproducibility, end to end, eight hours apart

The b03 duplicate ran to completion at 12:27 and produced
`06446b9e6306a779e0b545748cbf58f5f5fb9697a87b2aa296e5a7440519903e` — **byte for
byte the same mp4 as the 04:42 run**, across fetch_init, cover_crop,
assert_framing, encode, render and publish, on the same box at seed 20260820.
Only the sidecar timestamps differ. Nobody had ever measured that on this rig;
now the whole "same seed is a true control" argument three rungs deep has a
number behind it.

### THE HEADLINE: a middle placement in continuous aspect gives the performance back, and it is measured on the instrument that was written before the pixels

| beat | face/whole-frame instrument | rung 1 | rung 2 | **rung 3** |
|---|---|---|---|---|
| 13 | face band (250,240,400,360) mean abs interframe | 10.80 | 0.64 | **4.798** |
| 13 | same, last 20 pairs | 24.07 | 0.148 | **2.263** |
| 03 | whole-frame interframe at f060..f072 (step frames) | — | 0.44 / 0.40 / 0.34 | **7.60 / 7.29 / 7.02** |
| 03 | judge_clip FREEZE (exact ncc 1.0000 run) | — | 33 from f088 | **7 from f114** |

Beat 13's bar was **3.0 mean / 1.0 last-20 and deliberately not rung 1's 10.80**,
because rung 1 earned its number by standing up and walking out of frame. 4.798 is
the seated middle it asked for and this family had never produced. Beat 13's tilt
also goes **fully sideways** where rung 2's verdict had to write "he leans, he does
not tip" — judged 1:1 side by side, and it is not close.

**Publish the SHAPE of an interframe mean, not the mean.** All six clips in this
family read `judge_clip` **period 3, 8.0 effective fps** — a new picture every
third frame — so the energy lives on the step frames and the gaps read 0.04–0.35.
Beat 13's band reads **26.4, 30.9, 34.8, 35.4, 34.4, 32.7, 32.2, 31.1, 28.9** at
f066..f090 and **17.32, 13.28, 8.37** inside the last twenty. Rung 2's step frames
read 0.16–0.23. Like for like the comparison holds; quoted as a bare mean it would
have looked like smooth 4.8-per-frame motion, which is not what is on the screen.

### F-MIDDLE-IS-A-CUT did NOT fire, on either beat

`HALFWAY THROUGH THE SHOT` was read as a moment, not a shot change. Largest
whole-frame interframe anywhere in beat 13 is 4.32 and in beat 03 is 7.7 — both
are the body moving on a step frame. It was pre-registered as a real risk because
the negative's `cut to another shot, scene change, shot change` is by this
ladder's own law not protection. **The phrase is safe and other beats may use it.**

### THE COST, AND IT IS NOT THE COST RUNG 2 PAID

Rung 2's G2 was a *stillness* tax — the clip bought its terminal position by making
every frame the last frame. Rung 3 pays in a different currency on each beat:

- **Beat 13 gave back the FACE, in the middle, for about thirty frames.** From
  ~f042 to ~f072 the head has tipped far enough that the face is pressed into his
  own knee; the bar named f060 explicitly and the face is not readable there. This
  is **rung 1's fifty-frame fold returning at 60% length** as the direct consequence
  of the tilt that H3 wanted. Legible at f000, f030, f090, f120.
- **Beat 03 gave back nothing and still failed by one frame**, 7 against a bar of
  "under 6". And the exact-freeze instrument **understates both clips**: at the
  interframe level rung 3 is dead from **f075** and rung 2 from **f069**. The
  middle placement bought seventeen times the motion energy through the middle and
  **did not move the moment the clip stops.** A rung 4 aimed at the trailing run is
  aimed at the wrong 45 frames; the cheap answer is a **shorter render** — 121
  frames is the whole slot and the last 45 are dead in every clip of this family.

### BEAT 15: THE NOUN LAW, THIRD CONFIRMATION IN THREE CONSECUTIVE RUNGS ON ONE BEAT

**At f094 the goblin is deleted and replaced by a mound of bare earth, in one frame
pair, and never returns.** Whole-frame interframe on f093→f094 reads **28.14**
against a clip median of **0.171**; no other pair in the clip exceeds 1.7. It is a
hard swap. The last 27 frames of a five-second beat about a man talking to a
seedling contain no man.

The one variable was the rooting clause, and it introduced one new noun:
`rising up out of the grass beside him **with soil and grass around its base**`.
`soil` appears in **no other beat-15 prompt** — not `listenmotion`, not
`listenlast`. The beat's three rungs now read:

| rung | the phrase | what arrived |
|---|---|---|
| 1 | `talks to them from a **hand's width** away` | a hand, holding the plant at eye level |
| 2 | `Nobody touches the plant and nobody **picks it up**` | a pick-up: the plant uprooted in his fist at f120 |
| 3 | `with **soil** and grass around its base` | a mound of soil, in the frame's largest object slot, which was the subject |

**A noun is a placement wherever it appears — including inside a subordinate clause
about something else — and a placement with no assigned position takes the position
of the largest thing nearby.** §18's b08 grip finding said the *neighbourhood* names
what a mark becomes; this says the *frame* decides where an unplaced noun lands. The
next rung on beat 15 is one edit: **no soil, no earth, no dirt, no ground-material
noun of any kind** — the stem and the grass are the only nouns the rooting clause
may contain. Three GPU fires, one rule, three independent confirmations at one init
and one seed.

### THREE INSTRUMENTS RETRACTED, AND ONE OF THEM BROKE IN A SHAPE THIS FILE HAD NOT SEEN

Yesterday's entry generalised that a fixed window measures the subject only while
the subject stays in the window, and named `luma_std` **collapse** as the tell. All
three of today's skin probes broke; **only two broke that way**.

| beat | probe f000 → f120 | luma_std | what the box was actually on |
|---|---|---|---|
| 03 | luma 98.4 → 228.5 | **18.5 → 5.9** (collapse) | the hazy horizon — his head dropped ~450 px by f060 |
| 15 | luma 90.3 → 203.2 | **14.9 → 3.1** (collapse) | lit grass — the subject is not in the picture |
| 13 | luma 107.6 → 49.0 | **6.0 → 85.0 → 56.6** (**explosion**) | the boundary between lit cheek and dark cloak |

**A dispersion that jumps fourteenfold is a box on an EDGE exactly as a dispersion
that collapses is a box on a FIELD. Both are the premise dying and only the
dispersion shows it** — the means were 130, 113 and 59 luma out, all three clean,
confident and meaningless. Beat 13's is the more dangerous of the two shapes,
because a *collapsed* std looks obviously wrong on inspection and an *inflated* one
looks like a subject that changed.

Beats 03 and 13 re-placed by eye at 5x on f120 and published with **material as
well as luma**: b03 cheek (90,850,140,890) luma 92.4 / R−B 17.9 / std 7.4 and the
lit temple (60,700,120,760) luma 103.5 / R−B 34.9 — **+5.1 luma, +1.6 R−B**, i.e.
the same skin; b13 cheek (180,440,240,500) luma 90.6 / R−B 17.3 / std 4.9, with two
neighbouring placements inside 1.7 luma of it. Identity holds on both by eye at 1:1.
**Beat 15's has nothing to re-place onto**, which is the only honest thing a probe
can say about a frame with no subject in it.

### What this decides

- **Beat 13's next rung is the PLATE EXPOSURE rung**, and it is now earned rather
  than asserted. Its spec pre-registered the test: *if H1 passes and G8 still fails,
  the wording is exonerated.* H1 passed by 7x and G8 failed — at f120 his eyes are
  at y≈400–560 and the seedling is at y≈690–780 with 60 px leaves. Three rungs of
  wording have moved the face band 10.80 → 0.64 → 4.798 and the tilt from nothing to
  fully sideways, and **not one of them put light on his eyes.** Wording is done on
  this beat.
- **Beat 03's next lever is length or plate, not words.**
- **Beat 15's next rung is one noun.**
- **No pick, no `plate_ack`, no cut, no publication. Beats 03, 13 and 15 stay
  slates.** Per-clause verdicts in each spec's `verdict_measured`; clips, sheets and
  `EVIDENCE-*.png` under `farm-out/ep2-b{15,03,13}-{listenroot,covermid,shademid}-0820/`.
