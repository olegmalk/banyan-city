# Handover — 2026-08-18, night shift

Written by the steward at the end of an overnight supervisor loop. Everything
below is on disk and pushed; this file is the connective tissue. Read
`HANDOVER-0817.md` for the day before it and `STATE.md` for the running log.

The night's work was **judging, not building**: seven renders came off the card,
all seven were read frame by frame against bars that were written before they
existed, and every verdict is appended to the job spec that produced it. Nothing
was rendered on a whim, nothing was promoted, and no bar was moved to make a
result look better than it was.

## 1. Waiting on Roman/Oleg — nothing else unblocks these

| # | Decision | What it unblocks |
|---|---|---|
| 1 | **Watch the cold open and say yes or no.** `https://banyan.city/review/ep2-cold-open-0818/` — the clip, the frames, and now all six seeds side by side. It cleared a pre-registered technical bar; whether it is *good*, and whether it opens episode 2, is R4 and only yours. | Episode 2's opening shot. It is the furthest-along piece of the cut. |
| 2 | **Beat 14: re-stage it, or cut what we have.** Two seeds now say the two clauses that decide `done_when` — the glance must return, the face must read embarrassed — are properties of the *staging*, not the seed. Re-rolling will not fix them. | Beat 14's slot. This is the "re-stage the whole beat" half of the question the 2026-08-18 board already put to you. |
| 3 | **Beat 08: where does a pointing arm come from?** The composite/init route is now *proven* (see §2), so the beat is down to exactly one missing ingredient. The candidate sources — a posed reference, a drawn arm, a re-staged plate — are a production choice, not a render one. | Beat 08's gesture, and the pattern for any future beat needing a limb the plate lacks. |
| 4 | **The repo is 4.92 GiB and the deploy clone is riding its limit.** Full evidence in `pipeline/deploy-weight-finding-0818.md`. Getting render media off main's deploy path is architectural and touches where the project's own evidence lives — which is the product — so I picked nothing and moved nothing. | Deploy reliability. Not urgent: the site never went down. |

## 2. What was settled tonight — these generalise

- **A change in the LIGHT is a caveat; a loss of the DRAWING is a failure.** The
  cold-open bar didn't say this, and two seeds forced it: the pick blooms hard
  but every grass blade stays a drawn blade, while seed 20260828 lets the blades
  dissolve into a flat wash with stray hairline strokes. That line is the only
  principled reason to tolerate one and not the other, and it is now written
  into the specs so the next reader inherits it rather than re-deriving it.
- **Seed sweeps hit independent axes, and that caps what they can buy.** Six
  seeds of one cold-open recipe: colour path ramps in 2 of 6, camera holds in 2
  of 6, plate fidelity ranges from perfect to blown out — and *no two failures
  shared a cause*. One pass in six is what three independent dice look like. The
  practical rule: once failures stop correlating, more seeds is a lottery ticket,
  not an experiment. Stop and change a variable instead.
- **`0.30` finishes and does not add — confirmed on a staging change it was never
  asked to invent.** Beat 08's Mac-side rigid composite (board lowered 130 px,
  $0, no model) survived a 0.30 pass *and came back cleaner*: the compositor's
  rectangular seam-ghost resolved into cloak folds and a mushy fist became a
  drawn fist. Measured: mean |diff| 10.61 inside the mask, **0.04 outside it**.
  The pattern in `pipeline/composite-init-pattern.md` §9b is load-bearing and now
  has a second, harder proof.
- **The engine's "gross motion renders" claim is weaker than it looked.** Beat
  14 seed 1 reached for the dirt and broke ground; seed 2's hands never left his
  knees. Same plate, same prompt. The 0-of-8 in-hand record stands, but a gross
  reach is not therefore reliable — it was 1 of 2. Don't extend the 12-of-12
  whole-body record to arm reaches without testing.
- **On Vercel, `Previous build caches not available` is not a symptom** — it
  prints on healthy builds. The real marker is a missing `Cloning completed:`.
  And most of a day's `CANCELED` count is our own build guard doing its job on
  docs-only pushes. Both of these were live false leads tonight.

## 3. The card is empty, on purpose

`ready`, `running` and `backlog` on the rtx5090 are all empty, and the three Macs
are alive and idle. **That is a finding, not a lapse.** Every 0818 spec in the
repo has been run; every verdict written tonight ends in an explicit
`what_this_licenses`, and all five of them say the same thing:

- more cold-open seeds — **not ruled**, the sweep closed on the independent-axes
  finding above;
- a beat 14 re-stage — **not ruled**, it is R4 and it is question 2 in the table;
- a beat 08 arm — **not ruled**, it is a new route needing its own sample, its
  own bar, and the production choice in question 3.

The standing rule is that the GPU never idles while a *runnable, ruled* job
exists. Inventing a seventh seed to keep the card warm would have broken the
older rule that nothing gets queued without a consumer. So the queue empties and
this file says so out loud.

## 4. State of the machines and the site

- **rtx5090** — healthy, seven jobs tonight, all `rc=0`, all published to
  `farm-out` and pushed by the runner. No bugchecks, no worker restarts needed.
- **Macs 1/2/3** — all `ALIVE`, workers idle, queues empty. Nothing ruled for
  them.
- **banyan.city** — up and **current**, serving tonight's pages. It spent about
  three hours stale while clones wedged; the Pages mirror carried everything
  throughout and prod caught up on its own once the queue drained.
- **Spend** — $0. Everything tonight was local GPU and local compositing.

## 5. Where to look

| Thing | Path |
|---|---|
| Cold open, the candidate + all six seeds | `review/ep2-cold-open-0818/` |
| The pick, its reasons, and the sweep summary | `pipeline/jobs/ep2-b01-growmotion-b-0818.yaml` (`outcome`, `pick`, `sweep_summary`) |
| Per-seed verdicts with measurements | `pipeline/jobs/ep2-b01-growmotion-b{2,3,4,5,6}-0818.yaml` |
| Beat 14, what two seeds settled | `pipeline/jobs/ep2-b14-mac-motion-s2-0818.yaml` |
| Beat 08, the route proven | `pipeline/jobs/ep2-b08-boardcomp-0818.yaml` |
| Deploy clone evidence + how it resolved | `pipeline/deploy-weight-finding-0818.md` |
