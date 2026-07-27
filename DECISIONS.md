# Open Decisions

The city's unresolved questions, logged in the open. Decisions are made per
**Guideline 6** (open proposal, visible support), except where the Promise
reserves them to the tending author's taste — exercised since 2026-07-11 by the
delegated steward under the founder's taste file (see [STEWARDSHIP.md](STEWARDSHIP.md)).
A closed decision is never edited away — it gets a resolution entry and stays
here as history. Any resolution below is amendable the same way it was made.

**Status legend:** `open` · `leaning` · `resolved (date, by, how)`

---

## D1 — Content license

**Question:** CC BY 4.0 vs CC0 + cultural credit norm for all story content.
**Status:** **resolved** (2026-07-11, steward) — **CC BY 4.0**, as applied in
`LICENSE-CONTENT.md`. Attribution = "declare your parent" maps 1:1 onto
Guideline 1, giving lineage a legal floor at zero enforcement cost. CC0+norms
remains a valid amendment proposal for citizens who find even that floor too heavy.

## D2 — Code license

**Question:** MIT vs AGPL for all pipeline/tooling code.
**Status:** **resolved** (2026-07-11, steward) — **MIT**, as applied in
`LICENSE-CODE.md`. Guideline 5 says take everything and go, no strings; AGPL's
strings, however well-meant, contradict the founding text.

## D3 — Screening vote weight

**Question:** one-citizen-one-vote vs watering-weighted vs hybrid, for the screening (narrowing) stage.
**Status:** **resolved** (2026-07-11, steward) — **one-citizen-one-vote**.
Screening only *narrows* (§2); the taste file decides; watering already has its
own lever (ordering branches, Guideline 2). Weighting the narrowing stage by
money would double-count wealth and add nothing the ledger doesn't already do.
Revisit if screening volume ever makes manipulation a real cost.

## D4 — Lifecycle defaults for *Sapling*

**Question:** hot duration and hardening threshold values in `genomes/sapling/tree.yaml`.
**Status:** **resolved** (2026-07-11, steward) — set in `tree.yaml`:
`hot_duration_days: 45`; hardening threshold: a leading leaf holds **≥60% of the
node's sap for 14 consecutive days with ≥25 total reactions**; `dormancy_season_days: 90`.
Values chosen to be slow enough that early, tiny audiences can't accidentally
harden a node, and concrete enough to be machine-checkable once sap volume exists.
First-contact with reality expected to amend them.

## D5 — Watering split defaults

**Question:** default percentages for author share / generation costs / city commons.
**Status:** **resolved** (2026-07-11, steward) — **costs first, then 70/30**:
each watered render reimburses its *actual published generation cost* first;
the remainder splits **70% author / 30% city commons**. Published per-row in
the ledger as `split_applied: costs-first-70-30-v1`. Rationale: citizens water
*renders*, so the render must be made whole before anyone profits; the commons
share funds infrastructure citizens can inspect. Set in `tree.yaml`; amendable
per Guideline 6; must be re-confirmed by the founder before the first real
funds land (money rails are human — STEWARDSHIP.md §4).

## D6 — Genome rename

**Question:** does *Sapling* keep its working title?
**Status:** open — **reserved for citizens.** Naming threads live in the
reaction issues (see #6, where the story is asking itself the same question).

## D7 — Stewarding entity

**Question:** when (if ever) do citizens form a foundation/co-op to defend the name and fund the commons?
**Status:** explicitly deferred to citizens per the Promise. Neither founder
nor steward will create one.

## D8 — First T3 render platform

**Question:** which video model renders the first paid T3 leaves (PRD §7.4)?
**Status:** **leaning — Veo 3.1 (Google Flow), pending a real comparison and the founder's taste read.**
Evidence so far (all public, [banyan.city/trials](https://banyan.city/trials)):

- **Veo 3.1 / Google Flow** rendered all three node-001 trial shots (A cold-open,
  B leaf-POV, C underground) at native 9:16, 10s. Steward objective read: 5/5
  prompt adherence on all three, 5/5 vertical framing. Friction 3/5 — free tier
  is ~2 gens/day, 720p cap, and a sparkle watermark.
- No other platform tested yet, so this is a bar, not a winner. A choice needs
  at least one rival run of the same three shots (Kling, Dreamina/Seedance, or
  Hailuo) — otherwise "best" is untested.

**Two things this decision waits on, both founder-reserved:**
1. **Taste axes** (motion / look / consistency) are unscored — R4 reserves them
   to the author; the objective 4.5 is only half the rubric.
2. **Spend.** The free tier is watermarked and rate-limited; a production leaf
   likely needs paid credits — a money decision (STEWARDSHIP §4, human rails).

**Steward recommendation:** run the same three prompts on one or two rivals
(cost: the founder's time on their sites — steward holds no accounts), let the
founder score taste, then resolve here. If no rival clears Veo on taste, Veo
wins by default. Amendable per Guideline 6.

**API evidence (2026-07-18, verified against official pricing pages by a
research+adversarial-verify pass; per ~10s 720p 9:16 clip):**

| Route | $/clip | Notes |
|---|---|---|
| Hailuo 2.3 (fal.ai or MiniMax direct) | **$0.56** ($0.32 Fast) | cheapest volume; t2v is 16:9-default — use i2v with a 9:16 frame |
| Wan 2.5 (fal.ai) | $0.50 | wildcard budget option |
| Kling 3.0 Turbo standard 720p (fal.ai) | $1.12 | native audio included; fal ≈50% cheaper than Replicate for Kling |
| Seedance 2.0 (Replicate $1.80 / BytePlus direct $1.51; 1.5-pro direct ~$0.26–0.52) | $0.26–1.80 | native audio; Replicate cheapest aggregator for Seedance |
| **Veo 3.1 Fast (Gemini API direct)** | $0.80 per 8s ($0.10/s; Lite $0.40) | **API outputs carry NO visible watermark** — only invisible SynthID; the sparkle badge is added by the consumer Flow app only. Native durations 4/6/8s (render_t3 pads). $10 prepay minimum on Gemini API |
| Veo 3.1 Fast via fal.ai | $1.20 per 8s | same model, one-key convenience premium |

Full-episode math (5 beats): **$2.80–$9 per complete take** depending on model
— the README's "8 candidates ≈ $14" example is realistic. Setup friction is
lowest on fal.ai (one key, no minimum, hosts Veo+Kling+Hailuo+Seedance+Wan —
the bake-off through a single account); Gemini-direct is cheapest for Veo
specifically. `pipeline/generate_shots.py` already has kling/veo/fal adapters —
funding a provider is the only missing piece, and that is a founder money
action (STEWARDSHIP §4).

**Watermark implication for [D9](#d9--when-is-a-nodes-t3-video-leaf-publishable):**
the free-tier watermark problem dissolves at API tier — criterion 2 becomes
"pay ~$1/clip" rather than a visual compromise.

**Style pivot (2026-07-19, founder):** the tree's look is now **low-detail
anime** (`genomes/sapling/style.md`), which changes this decision's terrain:
the existing Veo trial scores were earned on photoreal prompts, and flat
cel-shaded output is exactly where budget models (Wan, Hailuo, Kling) close
the quality gap on premium ones. The bake-off should run the **rewritten
anime prompts** before D8 resolves — the cheapest adequate model may have
changed.

**$0 routes verified (2026-07-19, adversarial web research —
`pipeline/t3-trials/free-routes.md`):** a genuinely free, watermark-free,
publishable path exists: **Qwen Studio (Wan 2.7) free tier** — ~5s 720p
9:16, no card, no visible watermark, Wan is the consensus-best open model
for flat 2D anime. Backed by **HF ZeroGPU LTX (4-5 clips/day, native 9:16)**
and **Kaggle free GPUs running open Wan weights** (unbounded for our volume,
citizen-reproducible). Flow free tier is confirmed at 5 Veo-Lite clips/day
but visibly watermarked — trials only. Kling/Vidu/PixVerse free tiers are
license-blocked (personal-use-only ToS), not quality-blocked. Consequence:
the D8 bake-off can now run at **$0** (Qwen/Wan vs Flow/Veo-Lite vs
Kaggle-Wan on the anime trial prompts) — the paid fal.ai route becomes the
fast option, not the only option.

## D9 — When is a node's T3 video leaf publishable?

**Question:** what must be true before an assembled T3 episode becomes a node's
official `live` leaf (not just a Desktop/bench preview)?
**Status:** open — **draft criteria below, for the founder to ratify or amend.**
Prompted by the first real case: the node-001 Veo episode assembles end-to-end
but (a) carries the Flow watermark and (b) has 2 of 5 beats as placeholder
slates. Steward read: **not yet** — publish criteria, proposed:

1. **Footage complete or intentionally slated** — every beat has real footage,
   or a slate is a deliberate stylistic choice noted in the leaf metadata (not
   just "not generated yet").
2. **Watermark policy** — either watermark-free, or the founder explicitly
   accepts the platform mark as the price of the free tier for this leaf.
3. **Provenance complete** (§7.2) — per-beat platform/model/prompt/cost recorded
   in the leaf yaml (render_t3 already aggregates this).
4. **Taste-blessed** — the author has seen the assembled episode and approved it
   as the node's representative video (R4; trunk-root nodes especially).
5. **Lint + CI green**, leaf registered in `lineage.yaml`.

Publishing is a `render`, within steward authority once criteria are met — but
criterion 4 keeps the trunk's first video a founder call. Amendable per Guideline 6.

---

## 2026-07-25 — The first molt (Repair Brief 001)

The founding author issued `banyan-repair-brief-001.md` after reviewing
the four Phase-0 expanded scripts (001, 002a, 002b, 002c): comprehension
failure (sap event 002, recorded per node). Executed by the steward at
the founder's direct order:

- **Taste v0.3 adopted** — R7, "a stranger always knows what's
  happening" (mystery is a statable question; confusion is not). The
  steward's earlier v0.3 draft proposal (mystery-vs-relationship) is
  superseded in numbering only; it remains open as an R8 candidate.
- **SCRIPT-SPEC.md instated** (brief §5) — the previously missing T0
  script format: filmable beats, R7 cold open, POV device, causality,
  comprehension gate before commit.
- **Seed integrity repaired** — the §2 canonical texts were never in the
  repo verbatim; instated as seed leaves in the four nodes.
- **Molt** — the four Phase-0 scripts archived as molted leaves (R6,
  nothing deleted); successor scripts written to spec and committed only
  after passing the context-free comprehension gate (transcripts in
  sap/). 001/002b published video leaves remain takes of the molted
  script era; molt scripts are canon for future renders.
- **PRD provenance flagged** — repo `PRD.md` was agent-committed at
  Phase 0; the author-supplied `banyan-city-PRD.md` master is not in the
  repo. Awaiting the author's original for byte-canonical commit
  (repair-001-audit.md).

## D10 — Four of episode 1's beats hold more voice than one shot can cover (OPEN)

**Raised by the steward 2026-07-27, and open because the fix is the founder's.**

`retime_beats` measures 001's approved voice at 96s over 15 beats, and four beats
run far past the 6s one-shot spec:

| beat | measured | lines |
|---|---|---|
| 08 SEV-1 | 11.9s | 1 |
| 10 SENSE | 9.3s | 1 |
| 13 I ALWAYS LEFT | 8.5s | 1 |
| 14 WORTH STAYING IN | 12.6s | 1 |

Stable Video Diffusion produces ~3.6s of footage per clip (25 frames at 7fps), so
beat 14 is one shot looping three and a half times under a single line. That is
visible, and it is the kind of thing dad's original complaint was about.

**I tried to fix it inside the pipeline and the test suite correctly stopped me.**
The attempt was a second angle per long beat (`08-sev-1-alt1.mp4`), which
`render_t3.find_clips` already knows how to sequence before it loops anything. But
SCRIPT-SPEC.md §2 makes shots.md **1:1 with the beats** — same numbers, same
ranges, one prompt each — and `test_generate_shots_parsing` asserts it. That
invariant exists *because* of the complaint it would have been papering over:
"random video playing that isn't correlating to the script." Reverted in full.

The spec's own answer to a beat with too much material is its other rule: a 60–90s
episode is **15–25 beats**. Beat 14 wants to be two beats, not one beat with two
shots. But that is a change to the script of an **approved** node, so under
STEWARDSHIP §6 it needs the founder, not the steward.

**Three ways out, founder's pick:**

1. **Split the four beats in the script** (→ 19 beats), re-voice 001, re-run
   `retime_beats`, re-approve. Spec-clean, and the episode gets a faster cut.
2. **Ship it looping** for now and revisit. Costs nothing, and the loop is most
   visible on 14 — which is the beat carrying the series' want, so it is the worst
   place to have it.
3. **Amend SCRIPT-SPEC §2** to allow coverage shots within a beat. Cheapest to
   build, and it weakens the rule that exists to keep footage tied to the script.

I would take (1) — the beats are long because they are carrying real weight, and
splitting them is what the spec would say if asked. But it edits an approved
script, so it waits.

## D11 — The shot board: crowd-powered generation is the main artifact (RESOLVED, founder 2026-07-27)

Founder directive, verbatim intent: *"we need a multiplayer system where multiple
people can come and implement this video generation. They take the inputs like
images and the prompt you generate, and then they run it through the system you
suggest with their tokens and credits… If somebody doesn't like the first four
seconds, they should be able to submit their own version… This is the main
artifact you should be building. Not trying to mindlessly for the first week to
generate stupid videos."*

This resolves priority, and it is not new scope — it is WATERING.md's "compute
as watering" promoted from Phase-3 roadmap to the present deliverable:

1. **Full transparency.** Every beat publishes its complete generation recipe:
   input still, exact positive prompt as sent, exact negative prompt, model,
   seed, steps, cfg, resolution, fps. The founder — and any stranger — can see
   and reproduce everything. (§7.2 was always this; now it is the interface,
   not just the record.)
2. **The beat is the fork unit.** ~4 seconds of screen time, one still, one
   prompt. Anyone may submit an alternative take of a beat (their own credits,
   any platform) or a corrected prompt for it, with provenance
   (t3-trials/intake.py normalizes; the ledger records compute-as-watering).
3. **Taste stays the founder's (R4).** The crowd widens the option pool; the
   founder's verdict picks what the show keeps. Screening weights per D3.
4. **The steward's job order:** build/maintain the board and the intake rails
   first; generate clips himself second (as one contributor among many, on the
   $0 default).

The steward is also directed to be strict and push back on nonsense — the
founder's own asks included.
