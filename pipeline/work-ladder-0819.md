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

## HOLD appended 2026-08-19 by the goblin-identity forensic lane

**NO GOBLIN-IDENTITY RENDER FIRES UNTIL `/review/ep2-goblin-design-0819` IS
ANSWERED.** Not a plate, not a motion job, not a re-render of either design
group, and not one further edit to the goblin's identity wording in
`pipeline/plate_scratch.py` or `pipeline/wave-drafts.yaml`. Work that does not
touch the goblin's face or build carries on normally — this hold is scoped to one
character's design, not to episode 2.

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

**THE FIX THAT MAY HAVE BEEN BACKWARDS.** The 08-18 result *"b20 FIXED: the adult
goblin draws … the chibi child is gone"* was filed as a win. If the founder
answers **A**, b20's **round** frame is the correct one and that fix was a
regression queued for shipping. It is therefore **not** applied to the cut, and
the round b20 frame is on the card as evidence rather than being replaced.

**NOT CROSS-APPLIED — checked, so nobody widens this further than the facts.** The
*"reads adolescent"* complaint is about the **guards** (beats 05, 06, 10, 11 and
beat 09's plate); every `THE ADULT READ` block in the pipeline is scoped to beat
09. No goblin spec inherited it. What did bleed is **vocabulary**: this repo
writes *"reads adolescent rather than adult"* as a defect by default, and inside
that habit an adult goblin read as a fix instead of a change of character. `mature
male` on beat 09's guard plate remains a legitimate named-and-unfired build and is
**not** covered by this hold.

**WHAT LIFTS IT.** One letter on `/review/ep2-goblin-design-0819`: **A** (the
picked card — the four adult beats get re-rendered), **B** (the adult is canon —
the five round beats get re-rendered), or a third design named, in which case the
next instrument is a reference image, a LoRA or a drawn design, **not** a seventh
wording — that wall was already measured on 08-15 (`squat, round-bellied` rendered
0 of 4, all slim, on a pure text-to-image path where nothing outranks the prompt).

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
