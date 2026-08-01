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

## D11 — The shot board: crowd-powered generation is the main artifact (directed by dad 2026-07-27; awaiting founder ratification)

Dad's directive (relayed in-session; the founder flagged the authorship afterward),
verbatim intent: *"we need a multiplayer system where multiple
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

## D12 — No money rails: contributors are people with tasks (RESOLVED, dad's direction affirmed by the founder in-session, 2026-07-27)

The watering MONEY rail (D5's payment half) is parked indefinitely. A contributor
is a **person with a task**: they take a beat off the shot board and bring their
own tools, their own API key (billed by their own provider, never held by us), or
their own free compute (fork the Kaggle notebook under their own account). All
contributions land in the ledger as `type: compute`, credited by name — visible
and branch-ordering without any money touching the project. Rationale: same
power for everyone, very simple, and no payment custody in a family project.
The founders' own spend (the $15 motion authorization) remains separate,
founder-authorized, capped, and ledgered as before.

## D13 — The tree publishes CC BY 4.0, and five beats of the live episode do not (OPEN — founder call, 2026-08-01)

`pipeline/licence_gate.py`'s first full run found 46 licence violations. All
pre-existing; almost all in node 001. Records hygiene closed 25 of them (see the
commit): fifteen orphaned Stable Video Diffusion takes archived under R6,
fifteen POST sidecars renamed after fixing the `post_motion.py` bug that had been
writing them to the wrong filename, four VO manifests given the engine of record
already sitting in `voices.yaml`.

**Twenty-one remain, and the shape of them is the decision.**

The tree releases every episode under **CC BY 4.0** — a licence that grants
strangers commercial reuse. An input that forbids commercial use cannot be inside
a work that grants it; publishing one makes our own licence a false statement to
everyone who relies on it. That is the whole argument, and it does not depend on
anyone suing us.

**RESOLVED 2026-08-01 (founder, in session): the PixVerse account is the FREE
TIER.** So the third remedy below is off the table — there is no paid plan to
record — and the footage genuinely cannot be published. The five beats must be
re-rendered on a publish-safe route, which is queued on Wan 2.2 (Apache-2.0, $0).
Until those land, the only postable cut is `ep1-v19-CLEAN.mp4`, which substitutes
the local-deterministic POST takes and costs 4-40x less motion on six of fifteen
beats.

One thing this does NOT forbid: making a PixVerse version to WATCH. Showing a cut
to the founder or to dad is not distribution. A PixVerse-only comparison cut is
fine as an internal artifact provided it is labelled unpublishable and never
reaches banyan.city, TikTok, or the takes/clips/ directory the site copies from.

**1. Five beats of the live episode (2, 4, 8, 11, 13) are PixVerse free-tier.**
`DECISIONS.md` D8 already recorded that tier as "license-blocked (personal-use
only ToS)" on 2026-07-27 — written down, then used anyway, then published to
banyan.city and TikTok. This is the real one. Remedies, cheapest first:

- **Re-render on Wan 2.2 (Apache-2.0), $0, queued on the 5090 as
  `vid-720p-licence-…`.** The remake is licence-clean by construction and the
  work was happening anyway. Recommended.
- **Swap to the `.POST.mp4` take.** Every one of the five beats already has a
  local-deterministic alternate, publishable today, no render needed. The fast
  path if a cut has to ship before the Wan clips land.
- **If any of those takes was made on a PAID PixVerse plan, record the plan in
  the sidecar and nothing else is needed.** Only the founder or the contributor
  knows. Worth asking before re-rendering anything.

**2. Flow (6 files) and LTXV (2 files) — READ as of 2026-08-01. Both now need a
decision, not more research.**

**LTXV: the recorded reason for blocking it was wrong.** The Open Weights License
0.X (dated 2025-04-15, and by its own header applying to every LTXV release since
v0.9.6, so it governs our unpinned 2026-07 takes) says at §5: *"Licensor claims no
rights in the Output you generate using the Model."* The $10,000,000 revenue
threshold in §2 decides **who must buy a licence for the model** — every granted
verb in §2 takes "the Model" as its object, §3's redistribution conditions are
scoped to "the Model or Derivatives of the Model", and §1.4 defines Derivatives
model-to-model only (weights transferred into another model, distillation,
synthetic training data). A rendered video is Output under §1.8, not a Derivative.
The cap gates the weights, not the footage. **Recommendation: allow it.** Left
unflipped pending founder sign-off — nobody here is a lawyer, `allow` is the
direction that publishes things, and the two affected files are unused trial takes
of beat 1, so waiting costs nothing.

**Flow: no ownership problem, but we cannot pass on what we were given.** There is
no Flow- or Labs-specific terms document at all (labs.google/terms is a 404; the
service-specific index lists Labs.google against only the main ToS). The ToS says
*"Google won't claim ownership over that content"*, and never mentions commercial
use in any direction — the word appears once, defining "consumer". But two
conditions attach to the output under "Don't abuse our services": no *"using
AI-generated content from our services to develop machine learning models"*, and
no *"misleading others into thinking that generative AI content was created by a
human"*; plus a SynthID watermark that *"should not be tampered with or removed"*.
Our own release grants reusers "any purpose, even commercially" — training
included — so we cannot honestly hand on restrictions we accepted. That is a
judgement about what we warrant to reusers, not missing text. Independently, all
three files record `watermark: true` (visible Flow sparkle), which disqualifies
them regardless. **Recommendation: move them off the published surface.**

**3. A licence seam nobody chose.** The three Flow trial clips live under
`pipeline/`, which `LICENSE-CODE.md` claims as MIT ("the pipeline, tooling, site
generators, and any scripts"), while `LICENSE-CONTENT.md` applies CC BY 4.0 to
"genomes, nodes, scripts, leaves, taste files". So three watermarked Veo videos
currently sit inside an MIT-declared tree. That looks unintended and needs a
human decision independent of either licence question.

**4. And a correction to the scoping in this entry's first draft.** It said the
blocked footage was gitignored, so the exposure was the deployed site only. That
was checked against `clips/` and generalised wrongly: **`takes/clips/` is fully
tracked** — every PixVerse, SVD and LTX mp4 is committed and public on GitHub, as
are the three Flow trials. So `build_site.publishable()` closes one of two
exposure paths. Since the repo IS the product, "not in any episode" is not the
same as "not published", and removing a tracked file is a history question as well
as a working-tree one.

**The gate is a ratchet, and that was a judgement call worth stating.**
`pages.yml` runs `lint_genome.py` immediately before `build_site.py`, so making
these 21 fatal would not have reddened a badge — it would have stopped
banyan.city from deploying at all, overnight, blocking the founder's own goal of
shipping episode 1. So pre-existing debt is an advisory and the *count* is
asserted (`LICENCE_DEBT = 21`): one new violation fails lint and the test suite
immediately, and the number may only go down. `LICENCE_GATE_STRICT=1` makes
every violation fatal — the founder's switch, to flip the day the tree is clean.
Raising `LICENCE_DEBT` to make a build pass would turn the one gate that can
catch an unpublishable episode into a rubber stamp.
