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
| beat 19 blocker | "no plate exists" since 08-15 | **dead** — fruit aloft on 3 of 3 draws |
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
- **Next rung — named, costed, not fired:** a **composite init**. The project
  already owns the picture it cannot write: **beat 18's plate passes its bar as
  ONE round deep-purple-violet fig on ONE very thin branch**. The route exists
  in-repo (`composite-init-pattern.md`, `beat14_field_composite.py`,
  `beat08_gesture_composite.py`). Take r3's man, pose, field and framing — 5 of 7
  terms already passing — and composite beat 18's fig in at scale. That is a
  build, bigger than a rev, and it is the honest next step.
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
