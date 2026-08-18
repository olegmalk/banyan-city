# Handover — 2026-08-19, night shift (supervisor v2)

Written at the end of an overnight supervisor loop that began by replacing a crashed
predecessor. Everything below is on disk and pushed. Read `HANDOVER-0818-night.md`
for the shift immediately before this one and `STATE.md` for the running log.

**First thing to know: the predecessor did not lose work.** I was briefed that it
died mid-verdict on beat 08's board composite. It had not — the verdict was appended
and committed (`bae1e273`), the specs were clean in git, and its own handover was
written. I verified that against disk and the box before touching anything, and the
correct action was to stand down from the recovery and go find real work instead. If
you inherit a "resume the crashed lane" brief, check it the same way first.

The night's work was **five verdicts, two research findings, one restage proven, and
one correction to a finding of my predecessor's — plus one to a finding of my own.**

---

## 1. Waiting on Roman/Oleg — and it is one question, not four

The predecessor's handover queued **four** founder decisions. The boundary Roman
widened on 2026-08-18 puts three of them back on the steward ("route choices,
quality bars, tradeoffs… just leave me the taste questions", ~1 open question at a
time). So three were taken and answered here, with reasons, veto-able by one line.

| # | Decision | Why it is genuinely his |
|---|---|---|
| 1 | **Watch the cold open and say yes or no.** `https://banyan.city/review/ep2-cold-open-0818/` — verified live tonight, 200, all three assets serve. | It cleared a pre-registered technical bar. Whether it is *good*, and whether it opens episode 2, is R4 and nobody else's. |

**Taken off his board, with the reasoning recorded in the specs:**

- **Beat 08's pointing arm** — a route choice, explicitly steward-side since 0818.
  Not answered by a render tonight; it needs its own sample and its own bar, and I
  ran out of night before the queue floor let me get to it. It is *not* a founder
  question and should not be handed back as one.
- **Beat 14, re-stage or cut** — the assembly lane moved on this independently
  tonight (`b8a81d9b`).
- **The 4.92 GiB repo and the deploy clone** — architectural, unchanged, still a
  daytime conversation. Evidence remains in `pipeline/deploy-weight-finding-0818.md`.

## 2. Verdicts filed tonight — five, each against a bar written before its pixels

Every one is appended to the spec that produced it. No bar was edited, in either
direction, and where a clip fell in a gap the bar had left, the gap is named rather
than patched.

- **Beat 18 tremble, seed 20260871 — PASS**, and named the **pick** of the three.
  The only seed with motion in all four quarters (interframe medians 5.56 / 6.67 /
  6.05 / 5.16) and zero specular pumping.
- **Beat 18 tremble, seed 20260872 — FAIL-STROBE.** 28 of 120 adjacent frame pairs
  pump the specular by >25% of clip max; the passing sibling scores 0 on identical
  code. Caught on a *consecutive*-frame strip — a sheet sampled every 15 frames
  cannot see a strobe.
- **Beat 18 tremble, seed 20260873 — PASS, the weakest possible.** Quarters run 9.22
  / 4.10 / 0.72 / 0.45: it moves, then stops dead for the back half. The bar defines
  FAIL-FROZEN as "the plate simply sits still" and asks only that the fig "visibly
  MOVE", without saying for how long. So it passes, and I did not harden the clause
  after the fact to catch a clip I disliked.
- **Beat 17 shake — PASS on S1+S2+S3.** See §3; this is the night's result.
- The three-seed beat-18 set's real finding is the *comparison*: 1 pass, 1 strobe, 1
  decay means **the strobe is seed-borne**, where the 0812 read had it looking like a
  property of the recipe. Opposite conclusion, and the reason three seeds were filed
  instead of one.

## 3. The restage collected — beat 17 now has a take that matches canon

Beat 17 was restaged on 2026-08-18 (`brushes off` → `gives his cloak a shake`) on the
strength of 8/8 stand, 8/8 turn, **0/8 brush**. Nothing had been rendered against the
new line, so the beat had no take matching canon. `ep2-b17-shake-0818` fixed that on
**one seed**.

**S2, the load-bearing clause, passes on the exact test written before the render.**
Across f030–f041 he takes the cloak in hand, lifts it up and out into an extended
sheet of fabric, sweeps it down across his body and lets it settle — one full
out-and-back of the hem across roughly a third of the frame, feet planted. That is
not cloth trailing a moving body. **The engine that would not draw a brush in eight
seeds drew a shake on the first one.**

**And it abandoned the plate in eight frames.** 92% of all colour drift from the init
is complete by f008: a blue sky over a green meadow becomes an amber sky over a dry
brown field with an orange cloak, then holds steady for 88 frames. No pre-registered
clause covered plate fidelity, so it is recorded as a gap and **not** scored as a
failure. Part of it is mine — I put "afternoon light warming toward amber" in the
positive prompt myself.

## 4. Two research findings, both zero-GPU, one of them a clean negative

- **The latent-boundary lead: one hit, one miss.**
  `pipeline/research/latent-boundary-cold-open-0819.md`. LTX's VAE quantum is 8 pixel
  frames and frame 0 *is* the conditioning image. Beat 17's 92%-by-f008 is a textbook
  I2V conditioning-boundary collapse. **The same test on all eight cold-open clips
  comes back negative**: every seed front-loads into latent 1 — *including the pick,
  which front-loads hardest of all at 32.7%*. So front-loading is this recipe's
  constant, not G1's cause. A lead that looked strongest is measured not to apply,
  and no sample was filed against it.
- **The CFG-1 dead-negative audit.**
  `pipeline/research/cfg1-deadneg-audit-0818.md`. 94 specs pair guidance 1.0 with a
  non-empty negative, where the uncond pass never runs. The check that mattered was
  not the count but whether any verdict *credited* a negative that never fired:
  **zero of 94**. The dead configuration is in the tree; the dead reasoning is not.
  The mechanism was already known here (`ltx23-negcfg-b13-0816.md`) and already
  guarded in `ltx_i2v.py:sidecar_negative`.
- **The guidance schedule is not reachable.**
  `pipeline/research/guidance-schedule-feasibility-0818.md`. `--guidance` is a scalar
  and diffusers 0.39.0's LTX2 signature is `guidance_scale: float`. A schedule means
  patching the `__call__` every render passes through — reported, not hacked in at
  night.

## 5. Two corrections, one to my predecessor and one to me

**The predecessor's**: the cold-open sweep stopped on "three independent axes… no two
failures share a cause". Its own data two lines above says the colour path pops in
**4 of 6**, and four of the five rejects fail G1 by the same shape. It was never
three dice. The *stop* conclusion was right and stands; the reason was wrong, and the
wrong reason pointed at "wait for R4" instead of at a testable variable. Appended to
`ep2-b01-growmotion-b-0818.yaml` and applied to the review page the founder reads.

**Mine**: that correction asserted the recipe "does not distribute change across the
clip". Measured across all eight clips, that is true of the *passing* seed too, so it
describes the recipe and not the defect. Narrowed in the research file rather than
quietly dropped. The arithmetic that stands is the 4-of-5-on-one-clause part.

Also discarded rather than quoted: my first beat-17 camera measurement read edge
correlation ~0.00 against f000 and looked like a violent camera move. It was the
palette collapse destroying correlation. Redone among post-collapse frames it holds
0.81–0.96 and the framing is static.

## 6. State of the machines and the site

- **rtx5090** — healthy. `ep2-b17-shake-noamber-0819` was claimed at 20:08:33Z and
  should be done by ~20:15Z; **it is the one thing in flight and it is unjudged.**
  Its bar is pre-registered and carries S1/S2/S3 verbatim plus a new P1 plate-fidelity
  ceiling (mean |RGB| from init < 40 at f008, < 55 at f096 — set from the measured 0818
  failure of 80.7/87.3, not from taste). **P1 is scored separately from the action and
  the verdict must report both.**
- **The 8 files in `C:\banyan-queue\ready` are not work.** They are all `.HOLD`,
  `.HOLD-wrong-action` or `.DUP-already-ran` suffixed and the runner correctly
  reports `ready=0`. Do not be fooled by the file count as I nearly was.
- **banyan.city** — up, 200. Deploys were queuing again at end of shift: one Building
  at 13m with three Queued behind it. **I did not cancel anything**, on the
  predecessor's evidence that the one clone allowed to run finished at 41:22 while
  all three that were killed never did. Let a slow clone run.
- **Spend** — $0. Everything was local GPU, local ffmpeg, and reading.

## 7. Where to look

| Thing | Path |
|---|---|
| Beat 17, the restage proven + the plate collapse | `pipeline/jobs/ep2-b17-shake-0818.yaml` |
| Beat 17, the one follow-up, **in flight and unjudged** | `pipeline/jobs/ep2-b17-shake-noamber-0819.yaml` |
| Beat 18 tremble, three verdicts + the pick | `pipeline/jobs/ep2-b18-tremble-s2026087{1,2,3}-0817.yaml` |
| Latent boundary: the hit, the miss, and my own correction | `pipeline/research/latent-boundary-cold-open-0819.md` |
| The dead-negative audit | `pipeline/research/cfg1-deadneg-audit-0818.md` |
| Why there is no guidance schedule | `pipeline/research/guidance-schedule-feasibility-0818.md` |
| The cold-open sweep correction | `pipeline/jobs/ep2-b01-growmotion-b-0818.yaml`, `sweep_summary_correction` |

## 8. What I would pick up first

1. **Judge `ep2-b17-shake-noamber-0819`** against its P1 clause. If P1 still fails
   with the amber clause gone and the seed held, the collapse is the conditioning
   boundary and not the prompt — and the next move is a start-frame conditioning knob
   `ltx_i2v.py` does not expose, which is a daytime decision, not another sample.
2. **Beat 08's arm** — the one piece of ruled work I did not reach. It is a steward
   route choice, not a founder question.
3. **`ep2-b01-growmotion-b7`/`b8`** were queued by another lane and are unjudged. They
   are seeds, not variables; the sweep's stop conclusion is unaffected either way.
4. **Named, not built:** `box_enqueue.py` has no queue-time warning for guidance ≤ 1.0
   paired with a live negative. It must warn rather than block — two of the 94 are
   deliberate guidance probes.
