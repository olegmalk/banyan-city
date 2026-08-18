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

The night's work was **seven verdicts, three research findings, beat 17's restage
proven and closed, and two corrections — one to a finding of my predecessor's and one
to a finding of my own that a control render falsified the same night.**

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

## 2. Verdicts filed tonight — seven, each against a bar written before its pixels

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
- **Beat 17, three takes — PASS, PASS, PASS**, on progressively stricter bars: action
  only, then action + plate, then action + plate + garment. See §3; this is the
  night's result and the third take is the pick.
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

**The follow-up ran and PASSED all four clauses, and it cost me a finding.**
`ep2-b17-shake-noamber-0819` — same init, same seed, same negative, same recipe, that
one clause deleted — reads **13.6 at f008 against a ceiling of 40** and **31.0 at f096
against 55**, where the amber take read 80.7 and 87.3. The sky that had moved 102
levels moves 8.7. Action clauses all hold: he stands, spreads the cloak wide and lets
it collapse back with his feet planted, and strides off with his back to the lens.
**Beat 17 now has a take that matches canon and keeps the plate's world.**

That result **falsifies what I wrote three hours earlier.** I had called the 0818
collapse "the cleanest instance we have of an I2V conditioning-boundary collapse" and
published beat 17 as that hypothesis's clean hit. A boundary artifact does not vanish
because six words leave a prompt. The cause was the prompt. Both the verdict and
`latent-boundary-cold-open-0819.md` are corrected, retitled and banner-flagged rather
than quietly edited — **the hypothesis is now demonstrated nowhere in our material.**
It had a price attached, which is why it mattered: the 0818 verdict had named a
start-frame conditioning-strength change to `ltx_i2v.py` as the next move, which would
have been patching the code path every render passes through in order to fix a prompt.
**Withdrawn as unmotivated.**

**Residual defect, and it was a hole in a clause I wrote myself:** the world was
preserved and the *garment* was not. His dark navy cloak became a pink-and-cream
poncho from f024 on, and P1 passed anyway because it measures whole-frame distance
and a cloak is a small share of the pixels. Right idea, wrong granularity.

**So a third take closed it.** `ep2-b17-shake-navy-0819` — one variable again, the
positive prompt now *names* the cloak's colour, seed held — **passes all five
clauses.** P2 (the new garment clause) reads hue 223.8/sat 0.58 at f036 and 231.1/0.47
at f060, inside the required 180–260° at ≥0.40, against a plate of 220°/0.65 and the
0819 failure of 346°/0.24. P1 improved to 12.5 and 24.6. **Beat 17 now has a take that
keeps the action, the world and the garment at once, and it is the pick of the three.**

Two things worth carrying from how that verdict was reached. **S2 nearly went wrong by
eye**: the consecutive strip looks frozen, and measured, the hem swings 68px with 17
direction reversals — more than either sibling. The strip I opened sat inside a single
opening phase. And the **honest cost is unscored**: overall motion is the lowest of the
three (interframe median 0.50, half the frame pairs near-duplicates). The cloak moves
more while the clip moves less. Three beat-17 specs now share that blind spot.

The negative prompt was deliberately left alone throughout. Naming what you want in
the positive is the lever with evidence behind it; banning what you don't is the one
without — four of six cold-open seeds pushed in against an explicit "zoom, dolly,
push in".

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

- **rtx5090** — healthy, every job tonight `rc=0`. Three beat-17 renders, all judged
  and committed before handover. **Nothing is in flight and the queue is empty** — and
  that is a stop on a result, not fatigue: beat 17's chain closed with a take that
  passes every clause any bar has asked of it, so the next move there is a taste look,
  not a render.
- **The 8 files in `C:\banyan-queue\ready` are not work.** They are all `.HOLD`,
  `.HOLD-wrong-action` or `.DUP-already-ran` suffixed and the runner correctly
  reports `ready=0`. Do not be fooled by the file count as I nearly was.
- **banyan.city** — up, 200, but **stale at end of shift, and this touches the one
  founder question.** Last `Ready` deploy is 23m old; behind it sit one `Building` at
  17m and five `Queued`. **I did not cancel anything**, on the predecessor's evidence
  that the one clone allowed to run finished at 41:22 while all three that were killed
  never did. Let a slow clone run.
- **Consequence to know before you point Roman at the cold open:** production still
  serves the *pre-correction* text of `review/ep2-cold-open-0818/`. The clip, the
  frames and the six-seed sheet are unchanged and correct — the only thing missing is
  the paragraph replacing "three independent axes" with the four-of-five reading. The
  page is still fine for the taste call; it just carries superseded reasoning until
  the queue drains. Verified live: the old sentence is still being served, the new one
  is not. Re-check before handing him the link.
- **Spend** — $0. Everything was local GPU, local ffmpeg, and reading.

## 7. Where to look

| Thing | Path |
|---|---|
| Beat 17, the restage proven + the plate collapse | `pipeline/jobs/ep2-b17-shake-0818.yaml` |
| Beat 17, the amber control that withdrew my finding | `pipeline/jobs/ep2-b17-shake-noamber-0819.yaml` |
| **Beat 17, the pick — action + world + garment** | `pipeline/jobs/ep2-b17-shake-navy-0819.yaml` |
| Beat 18 tremble, three verdicts + the pick | `pipeline/jobs/ep2-b18-tremble-s2026087{1,2,3}-0817.yaml` |
| Latent boundary: the hit, the miss, and my own correction | `pipeline/research/latent-boundary-cold-open-0819.md` |
| The dead-negative audit | `pipeline/research/cfg1-deadneg-audit-0818.md` |
| Why there is no guidance schedule | `pipeline/research/guidance-schedule-feasibility-0818.md` |
| The cold-open sweep correction | `pipeline/jobs/ep2-b01-growmotion-b-0818.yaml`, `sweep_summary_correction` |

## 8. What I would pick up first

1. **Beat 08's arm** — the one piece of ruled work I did not reach. It is a steward
   route choice, not a founder question.
2. **`ep2-b01-growmotion-b7`/`b8`** were queued by another lane and are unjudged. They
   are seeds, not variables; the sweep's stop conclusion is unaffected either way.
3. **Named, not built:** `box_enqueue.py` has no queue-time warning for guidance ≤ 1.0
   paired with a live negative. It must warn rather than block — two of the 94 are
   deliberate guidance probes.
