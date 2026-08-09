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

**Addendum 2026-08-07 — this was never ratified, and it was applied wider than it
is written.** The status line above says "for the founder to ratify or amend" and
no ratification of it exists anywhere: not in git, not in this file, not in
`STATE.md`, not in the transcripts. For twenty-five days these draft criteria were
enforced as law — and beyond their own subject, which is a node's official `live`
leaf. They were read as gating any appearance of a cut on the site at all. The
founder struck that reading down on 2026-08-07: see
**[D17](#d17--working-cuts-may-publish-to-an-unlisted-review-area-resolved--founder-2026-08-07)**,
which supersedes it for working cuts and leaves criterion 4 — the canon gate —
standing. **D9 itself is still open.**

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

**PARTLY RE-OPENED 2026-08-04.** Oleg's watch-only directive removes the
pass-through reasoning behind §2's **Flow** finding; the visible SynthID watermark
and the two conditions on us survive it, so Flow is not cleared, only re-openable.
**The PixVerse five (§1) are NOT affected** — a personal-use-only free tier binds us
as the publisher regardless of what we offer viewers. See items 0, 2 and 4 of the
2026-08-04 entry below.

---

## D14 — Beat 4's fall is written but never shown (OPEN — founder's, R4)

*Raised 2026-08-02 by the steward, from an audit of all 15 motion directions
against the script's own action lines. This is a composition question, so it
waits for the author.*

The founder's note on the newest cut was **"his death is very anticlimatic"**.
That is not a rendering failure. It is the script and the still describing two
different moments, and the still winning — as it must, because the still owns
composition and image-to-video can only animate what is already in the frame.

**The script (node.md, beat 4, approved):**

> A sharp breath in — the frame tips sideways — the mug hits the floor before he does.

Three events, all motion: a breath, a camera tilt, an object falling.

**The still (shots.md, beat 4, approved):**

> close-up on the side of an office chair, a man's limp hand hanging straight
> down past the armrest, relaxed open fingers, **motionless** … papers **settled**
> on the dark floor below … *No face, no head, no full body, no horror, no blood,
> no standing.*

That is the aftermath, deliberately and tastefully so — it is the seconds *after*
the fall, with every restriction pointing away from showing a body drop. The
motion direction ("the limp hand stays motionless, one loose paper settles")
matches the still faithfully. So the pipeline is behaving correctly at every
step, and **the fall is never depicted anywhere in the episode.** The anticlimax
is structural, not accidental.

**Two coherent resolutions, and they are opposite in taste:**

1. **Keep the aftermath; make the anticlimax deliberate.** Let the fall happen
   entirely in sound — the sharp breath, the mug, the fan spinning down — over a
   held shot of the limp hand. This is the restrained reading, it needs no new
   render, and it is arguably a better death than showing it. If chosen, the
   *script* line should change so it stops promising a tilt the picture will
   never deliver.
2. **Show the fall.** Requires a new beat-4 still depicting it mid-motion (the
   chair tipping, the mug leaving the desk edge) and a direction with a tilting
   camera. Note this is the one beat where the script *authors* camera movement,
   so the global "camera locked" discipline would be overridden here on purpose —
   which is a real exception, not a slip, and the shake work must not undo it.

**The steward's recommendation is (1)**, on the grounds that the still's
restrictions read as a considered choice rather than an oversight, and that
sound is already carrying the moment. But this is R4 — taste belongs to the
author — so nothing changes until the founder says which.

**What the steward did NOT do:** touch beat 4's still, its direction, or its
script line. The four directions fixed in the same pass (1, 2, 7, 10) were all
cases where the direction contradicted *its own already-approved still*; beat 4's
direction agrees with its still, and the disagreement is one level up.

---

## D15 — every approved still is OpenRAIL++, and the gate was clearing it (OPEN — founder's)

*Found 2026-08-03 by the steward while vetting AnimeGen. Raises the licence debt
count from 21 to 38. Nothing was hidden and nothing was allowed: the record was
corrected, the ratchet fired, and CI is red until this is decided.*

**The stale record.** `licence_gate.MODEL_LICENCES` recorded
`"animagine": "faipl-1.0-sd"` with the comment *"outputs unrestricted"*. That was
true of an earlier version of the repo. `cagliostrolab/animagine-xl-3.1`'s own
card now says:

> This model is licensed under the CreativeML Open RAIL++-M License… **Note: This
> license supersedes any previous community license tags (e.g., FAIPL)** applied
> to earlier versions of this repository.

HF's tag agrees: `openrail++`. And the same `licence_gate.py` already lists
`r"openrail"` among licences whose conditions travel — **so the gate held two
records that contradicted each other, and the permissive one won on every
asset.** A stale allow is worse than a missing one: it reads as due diligence.

**What the text actually says** (SDXL `LICENSE.md`, 14105 bytes, sha256
`19b6998b569b53ac1fc2158a8a3202c8699a9a4605b47075715d9c96be7fb6d0`):

> "Except as set forth herein, **Licensor claims no rights in the Output** You
> generate using the Model."

> "**No use of the output can contravene any provision as stated in the
> License.**"

So this is not an ownership problem — nobody claims our frames. It is a
**pass-through** problem, exactly the shape of the google-flow finding in D13:
the output's *use* is bound to Attachment A's restrictions, and our own release
offers reusers CC BY 4.0, i.e. unrestricted use. We cannot grant what we do not
hold.

**Scope, and it is the whole picture.** `animagine` drew **all fifteen approved
stills**, and image-to-video means every frame of every episode descends from
one. 4 files / 17 records are flagged today (`leaves/001-t3-d.yaml` plus three
`01-the-keyboard` sidecars); the true reach is every still in the tree, visible
only where a record happens to name the model. `stills/` itself carries no
sidecars at all — 16 tracked PNGs with provenance stated only in a README.

**Three ways out, and the choice is the founder's:**

1. **Narrow our own offer.** Publish the *stills* (and footage derived from them)
   under terms that carry OpenRAIL++'s use restrictions, keeping CC BY 4.0 for
   text and code. Honest and needs no re-render — but it means banyan.city's
   pictures are no longer freely reusable, which cuts against "the repo IS the
   product". This also resolves D13's google-flow question the same way.
2. **Re-draw the stills on a model whose grant we can pass on.** Costs a full
   still pass and a new founder approval round for fifteen compositions, and the
   look will shift. The steward has NOT surveyed candidates yet; doing so is the
   obvious next step if this is the direction.
3. **Decide the restrictions are compatible in our case.** Attachment A forbids
   uses we have no intention of making (harming minors, unlawful discrimination,
   etc.). A reasoned position that our CC BY 4.0 offer does not actually conflict
   is defensible — but it is a legal judgement about what we promise reusers, and
   it belongs to the author, not the steward.

**The ratchet was NOT raised to make CI pass.** `LICENCE_DEBT` is set to 38 with
this entry as its justification, because the count asserts *"no new unpublishable
asset"* and no new asset appeared — a record was corrected. Raising it for any
other reason would turn the one gate that can stop an unpublishable episode into
a rubber stamp. It must come back down as assets are retired, never up to
accommodate them.

**Not a blocker for screening `ep1-v22-hires.mp4`.** That cut is all Wan 2.2
(Apache-2.0) motion over these stills; the question here is what licence the
published result carries, not whether the episode is watchable.

**RE-OPENED FOR REVIEW 2026-08-04.** Oleg's watch-only directive removes the
pass-through half of the argument above. Nothing here is resolved and the ratchet
still stands at 38 — but the three ways out must be re-read against what Attachment
A actually forbids. See item 4 of the 2026-08-04 entry below.

### HALF OF IT IS DECIDED — the visibility half, by the founder, 2026-08-09

His words, in full and unedited:

> put the images from my computer onto there please, not like theres any reason
> to hide it

**What that settles.** The candidate frames — ten contact sheets and the five
provisionally picked plates — publish to `banyan.city/review`. They had been
held back on this entry: item 02 of the checklist said *"the frames are not on
this page"* and named D15 as the reason, which was the right call while nobody
had asked him. He asked.

**What it does NOT settle, and nobody here may settle it for him.** The three
ways out above are still three; he picked none of them in general. The licence
conflict is untouched: `animagine-xl-3.1` is CreativeML Open RAIL++-M, its use
restrictions travel to the output, and this tree still offers reusers CC BY 4.0.
"There is no reason to hide it" is a statement about secrecy, not about what we
warrant to a stranger who downloads a frame.

**So the implementation is way-out 1, applied to one surface only.** Those images
publish under an offer narrowed to the restrictions they carry — OpenRAIL++'s
Attachment A, *not* CC BY 4.0 — said out loud in three places: one line under
every gallery on the page, a `published_under:` field in each image's sidecar,
and this entry. Granting only what we hold is what makes them publishable at
all; the gate is not being relaxed, it is being told what the offer is.

**Three conditions in code, in `licence_gate.REVIEW_GALLERY`, and each closes a
different route:**

1. the **directory** he named, `cuts/review-assets/` — a declaration, like
   `archive/` and `takes/`. A frame that moves out is judged with nothing
   softened;
2. the **record says so** — no `published_under:` line, no clearance. Without
   this, dropping a refused file into the right directory would clear it and
   writing nothing would be cheaper than writing the truth, which is hole 2
   wearing a new hat;
3. the **model is one he authorised** — only this one. **D16's LTX clips stay
   withheld**, because that sign-off is a separate question and he has not
   answered it, and a model in no table stays withheld too: a licence nobody has
   read cannot be narrowed to terms nobody has read.

**The debt ratchet does not move, and that is the point rather than a
convenience.** It counts assets we *cannot* publish. These we can, under the
narrowed offer, so counting them would make the number mean something else — and
raising it to absorb them is the move the ratchet exists to stop. They stay
visible: lint prints them every run as one collapsed advisory that says
"PUBLISHED ANYWAY, under an offer narrowed…". Debt stayed at 25 across this
change, verified before and after.

**What is committed is a JPEG rendition, not the original PNG.** 54 MB became
9.8 MB and clone time is a real cost. Each sidecar records the source path, its
SHA-256 and the encoding, so a published image is checkable against the frame it
came from; the candidate PNGs stay gitignored, and this is a published copy
rather than a promotion to canon.

**Still open and still his:** whether the tree narrows its offer generally
(which would also answer D13's google-flow finding), re-draws the fifteen
approved stills on a model whose grant we can pass on, or reasons that the
restrictions do not conflict in our case.

---

## D16 — LTX-2/2.3 is a CANDIDATE under watch-only, gated on three things we control (OPEN — founder call, 2026-08-04; **gate (c) FIRED TWICE on 2026-08-06 — suspended, then SCREENED AND CLEARED ON LOOK; still OPEN because adoption now waits on integration work that is not done. Two addenda at the end, in order. The licence analysis is unchanged throughout**)

*Raised by the steward from `pipeline/research/models-licence.md` (finding 3) and
`pipeline/research/DECISION.md`, both 2026-08-04, both quoting the primary licence
texts verbatim — then **rewritten the same day**, because Oleg's watch-only
directive changed the question this entry was asking. Attachment A was afterwards
extracted from the primary text in full (<https://raw.githubusercontent.com/Lightricks/LTX-2/main/LICENSE>,
20 items) and re-read under the new posture. Two movements, therefore: the recorded
**reason** for rejecting LTX had expired, and the objection that replaced it has
now been answered by the posture.*

**The posture this entry now rests on** (Oleg, process authority, 2026-08-04,
verbatim):

> "when we publish clips they are for people to watch, not use for anything, so
> dont create problems for scale."

Published rendered media carries **no reuse grant** — watch-only. That is recorded
once, with what it does and does not change, in the 2026-08-04 entry below; this
entry only uses it. **Verdict here moves from BLOCKED to CANDIDATE.**

**What we recorded.** `licence_gate.py` keeps `ltx` / `lightricks` off the
publish-safe side, *"not to be re-proposed without reading D13"*, on the reason
*"weights ship under THREE licences by version; the 2B is 'academic or research
purposes only, and explicitly excludes commercialization', and the GitHub LICENSE
that looks like plain Apache-2.0 covers CODE ONLY."*

**That is verbatim-confirmed — for the 2B v0.9.x checkpoints only.** Those are
literally RAIL-M:

> "No use of the Output can contravene any provision as stated in the License."

The provision it points at is *"academic or research purposes only"*, so that
clause reaches **our own** publication — which is the form of the objection that
survives the watch-only posture (item 3 of the entry below). **BLOCKED, unchanged**,
and the "code only" warning is still true of the GitHub file.

**But it is wrong as a verdict on the family, and the record predates two
releases.** **LTX-2 (19B, January 2026)** and **LTX-2.3 (22B, March 2026)** ship
under the *LTX-2 Community License Agreement* (5 January 2026):

> "you are granted a non-exclusive, worldwide, non-transferable and royalty-free
> limited license … to use, reproduce, prepare, distribute, publicly display,
> publicly perform, sublicense, copy, create derivative works of, and make
> modifications to LTX-2, **for any purpose**"

> "Except as set forth herein, Licensor claims no rights in the Output you
> generate using LTX-2."

Worldwide, no territory exclusion, commercial use free below $10,000,000 annual
revenue, no rights claimed in output. On Artificial Analysis LTX-2 ranks top-3 for
image-to-video overall and **#1 among open-source models**, and the fp8 distilled
build runs in **12-16GB** — so it fits *both* laptops, including the 12GB card
that cannot render 704x1280 on Wan at all. It is the strongest-quality
licence-plausible model we had excluded, and the sentence we excluded it on
describes the 2B v0.9.x checkpoints.

(The 13B 0.9.7 / 0.9.8 checkpoints are a third licence again, the *LTXV Open
Weights License 0.X*, already read end-to-end and recommended `allow` in
[D13](#d13--the-tree-publishes-cc-by-40-and-five-beats-of-the-live-episode-do-not-open--founder-call-2026-08-01) §2.
Nothing there is disturbed: 0.X applies by its own header to releases since
2025-04-15, and the RAIL-M checkpoints all predate that date, so the two readings
are consistent and the discriminator is which checkpoint a take was rendered with.)

**The objection that watch-only removes.** The blocker in this entry's first draft
was structural: LTX-2/2.3 carries a 20-item use-restriction schedule constraining
what may be done with the **output**, we publish under CC BY 4.0 which grants
recipients unrestricted use, and both cannot be true for a downstream reuser — the
same shape as the OpenRAIL++ finding in [D15](#d15--every-approved-still-is-openrail-and-the-gate-was-clearing-it-open--founders)
and the Flow finding in D13. **Under watch-only there is no downstream reuser to
contradict**, and the primary text confirms it from the other side: **flow-down in
Section 3 is scoped to "LTX-2 or Derivatives of LTX-2" — never to Output.** We
would distribute neither weights nor derivatives, so no notice attaches to a
published clip and **a viewer is never a party to the licence.** The reuse-side
concern is fully cleared.

**What survives binds US. Three duties:**

1. **Disclose per surface (Attachment A item 5).** Machine-generated content must be
   *"expressly and intelligibly"* disclaimed — and the duty attaches to **each
   surface the footage appears on**, not to the repo. §7.2 does not discharge it: a
   leaf yaml is not a TikTok post. **Distribution rule: every post or embed carrying
   LTX footage sets an AI-generated label** — TikTok has a native toggle, so the
   cost is one switch per post. `POSTING-KIT.md` step 0 is where it belongs.
2. **Never train on the output (item 18).** No LoRA, no finetune, no distillation
   from LTX frames. Named because training on our own footage is a plausible thing
   to want later, and this forecloses it for LTX material specifically.
3. **Do not strip technical limitations or safety filters (item 19).** Scope is
   undefined in the text, and there is an **unresolved edge: quantisation.** The fp8
   build is the whole reason LTX fits 12-16GB, and whether reducing precision counts
   as removing a "technical limitation" is not answered by the licence. Flagged, not
   resolved.

**THE ONE OPEN RISK — item 20, and it lands on the crowd plan, not on us rendering
episodes.** It bars use in any product that

> "directly competes with Licensor's commercial products or services"

Lightricks sells **LTX Studio**, an AI video-production tool. Us rendering our own
episodes: low risk — we are a story tree, not a video tool. **Powering a public,
contributor-facing generation service with LTX is on its face inside that
category** — and that is D11's shot board, which dad's crowd-first directive makes
the main artifact. **Standing rule to record: LTX may render our episodes; it must
never become a generation engine we offer contributors or the public.**

Two stability caveats on the same licence, both worth knowing before anything is
built on it: **Attachment A incorporates an external AUP that Lightricks may revise
unilaterally**, so this verdict is only as stable as a document we do not control;
and **Section 2's $10,000,000 trigger is ENTITY revenue** — above it a paid licence
is required and its terms are not stated.

**The licence-simpler fallback.** The 13B LTX-Video checkpoints (0.9.7 / 0.9.8,
*LTXV Open Weights License 0.X*) carry a strictly narrower **16-item** schedule:
**items 17-20 are absent** and only the disclosure duty survives. So if item 20
worries the founder, the fallback is a weaker model whose licence cannot reach the
shot board at all. (D13 §2 already read 0.X end to end and recommended `allow`.)

**Net status: LTX-2.3 = CANDIDATE** under watch-only, up from BLOCKED, gated on
three things that are all ours: **(a)** the per-post AI-disclosure rule above,
recorded as a distribution rule binding on whoever posts; **(b)** the item-20
standing rule, recorded; **(c)** **one sample beat, founder-screened** — a model
swap is a recipe change, so ONE SAMPLE BEFORE ANY BATCH applies, one beat and not
fifteen, and the look is R4. (a) and (b) cost nothing and are written down here;
(c) is the gate that actually holds this open.

**What waiting costs, stated honestly:** nothing yet. No clip in the tree is LTX-2
and nothing is queued on it. What it costs later is the field's best open-source I2V
model and the only route to real motion on the 12GB machine. **The steward is not
proposing adoption** — this entry exists so a rejection whose reason has expired
stops reading as a settled fact.

**ADDENDUM 2026-08-04 — the second licence in the chain is Gemma's, and it is
SHIP-SAFE.** LTX-2.3 does not carry its own text encoder: the **required** one is
Google **Gemma-3-12B**, so the *Gemma Terms of Use*
(<https://ai.google.dev/gemma/terms>) and Google's Prohibited Use Policy sit in the
chain of **every LTX clip** we would render — a second licence everything above
never examined. Read end to end 2026-08-04. **Verdict: ship-safe for watch-only**,
and on three points it is cleaner than the LTX text:

- **No rights claimed in output. §3.3 verbatim:** *"Google claims no rights in
  Outputs you generate using Gemma. You and your users are solely responsible for
  Outputs and their subsequent uses."*
- **Commercial use is permitted unconditionally** — no revenue threshold (unlike
  LTX-2's $10,000,000 entity trigger), no MAU cap, no royalty, no territory
  exclusion, no NC clause.
- **No flow-down to viewers.** §3.1's notice-and-agreement duties fire only on
  distributing *"Gemma or Model Derivatives"*, and a Model Derivative is **defined
  as a MODEL** — an mp4 is not one. **No Gemma notice is needed on any post.**
- **Its provenance duties are already over-satisfied.** Gemma's provenance items are
  qualified on deception, and the per-surface AI-generated label recorded above
  (duty 1) goes further than they ask.

**THE COST, stated plainly:** the PUP is **incorporated by reference** and Google
*"reserves the right to update"* it — so adopting LTX-2.3 puts a **second
unilaterally-revisable AUP** in the chain, alongside Lightricks' own, doubling the
stability caveat above rather than adding a new kind of risk. The Gemma text also
carries a **termination-and-delete clause** and a **reserved right to restrict usage
remotely**.

**How we would obtain the weights does not change any of it.** The build we would
fetch is the ungated Lightricks mirror
(`Lightricks/gemma-3-12b-it-qat-q4_0-unquantized`, tagged `license:gemma`). The
preamble makes **acceptance by conduct** — using the weights is agreeing — so we are
bound by the Gemma ToU regardless of Google's HF gate. **Lawful to fetch, bound
anyway**; there is no version of this where the mirror routes around the licence.

**The item-20 standing rule now reads across both licences.** Gemma's *Distribution*
definition explicitly includes *"making Gemma or its functionality available as a
hosted service via API, web access, or any other electronic or remote means"* — so a
public render-your-own-beat tool would trigger §3.1's duties on the Gemma side
exactly as it trips item 20 on the Lightricks side. **Standing rule, restated: these
models render our episodes; they never become a generation service we offer
contributors or the public.** Two independent licences now say the same thing about
[D11](#d11--the-shot-board-crowd-powered-generation-is-the-main-artifact-directed-by-dad-2026-07-27-awaiting-founder-ratification)'s
shot board.

**Net D16 status, updated: the Gemma gate is CLEAR.** Remaining gates are both ours
and both unchanged — the per-post AI-disclosure rule, and the one founder-screened
sample beat (weights downloading 2026-08-04).

**ADDENDUM 2026-08-06 — gate (c) fired, and it fired NEGATIVE. Candidacy
SUSPENDED, on a picture defect, not on the licence.** The gate this entry says
"actually holds this open" is **(c) one sample beat, founder-screened**. The
founder screened it on 2026-08-06 and his verdict on the LTX clips was that they
*"turn black and white ... an unnecessary colour transition"*. He separately
cleared the fp8 build **on look** — *"barely a difference"* — which is a real
clearance and is recorded, but it is a clearance of the fp8 *cast*, not of the
model.

**Measured, so the suspension is not an impression** (`bench-platform/colour-drift-20260806.log`,
38 clips, one code path, $0): every LTX-2.3 clip loses **86-89% of its chroma over
its own length** (Cab 28.07 → 3.78 on the bf16 b1; half gone by frame 6, 90% by
frame 18), while every Wan-5B, AnimeGen, AnimateDiff and **July LTX-Video 0.9**
clip of the same beat through the same export path is flat. Upstream has it open
as Lightricks/LTX-2 issue **#37** on this exact card, with no fix.

**Status: LTX-2.3 = CANDIDACY SUSPENDED**, down from CANDIDATE, **pending the
founder's screening of one on-bucket sample** at LTX-2.3's own **960x544x121**
geometry — the leading suspect, per Lightricks' own guidance, is that we run far
off that bucket. That sample was launched 2026-08-06 18:42 and **did not complete**
(the render box left the LAN mid-denoise at step 4 of 8); it is staged for a
one-command re-run.

**What this addendum does NOT do.** It does not touch (a) or (b), which cost
nothing and stand. It does not change one word of the licence analysis above —
Attachment A, item 20, the Gemma chain and the $10M entity trigger all read exactly
as they did, and **none of them is why**. It does not close D16: this entry stays
**OPEN**, because whether a model is good enough to ship is **R4**, and so is
whether to spend another sample on it. Reopening the candidacy needs the on-bucket
clip in front of the founder, not an argument in this file.

**ADDENDUM 2 — 2026-08-06, later the same day: gate (c) fired a SECOND time and
CLEARED. The suspension above is LIFTED. D16 stays OPEN, and the reason has moved
from the picture to the plumbing.**

*Addendum 1 is left standing word for word. It was an accurate record of the first
screening, and superseding it is not the same as it having been wrong.*

**What reopened it was not an argument in this file — it was the founder looking
again.** Addendum 1 closed by saying exactly that. Shown the same clips with the
colour measurement in hand, he cleared all three of the things that had been logged
as defects:

- **fp8 cast vs bf16** — *"barely a difference"*. (Already recorded in addendum 1
  as a real clearance of the *cast*; it is repeated here because it is now one of
  three, not a lone exception.)
- **The within-clip chroma collapse** — *"fine"*. The figure he was shown is the
  measured one: **86%, Cab 28.07 → 3.78** on the bf16 b1 (89.4% on the fp8).
- **The 3-frame motion cadence** — *"fine"*. Also measured: **~22 distinct motion
  states in a 65-frame 24 fps clip, an effective 8 fps**.

**Gate (c) is therefore SATISFIED.** It read *"one sample beat, founder-screened"*.
It has now been screened twice on the same day, and the second screening is the
operative one. **LTX-2.3 moves CANDIDACY SUSPENDED → CANDIDATE, SCREENED AND
CLEARED ON LOOK.** The five LTX rows in `MODEL-COMPARISON.md` §1 and the banners on
`COMPARISON.html` are updated in place, each quoting the suspension it supersedes.

**What this clearance is, exactly — and it is narrower than "we are using LTX".**
It is a clearance **on look**, of clips at **704x1280x65 and 352x640x65**. It is
not an adoption decision, not a decision to spend the on-bucket sample, and not a
statement that the collapse is desirable — only that the founder saw it and does
not consider it disqualifying. R4 is his to revisit at any time, and the
measurements stay on the page so that revisiting it is cheap.

**Why D16 is still OPEN, and this is the part a future session should read first:
LTX is not wired into anything, and wiring it in naively makes it slower than the
incumbent.** Measured 2026-08-06, $0:

- `pipeline/video_task.py` hardcodes the Wan renderer in **both** places it
  launches one — **`:1015`** and **`:1082`**, both `pipeline/wan_i2v.py`. There is
  no LTX queue path; LTX is hand-run via `pipeline/ltx_i2v.py` plus a separate
  `--stage encode` pass.
- Given the queue's shape — one process per beat — LTX costs **≈78 min for a
  15-beat episode against the incumbent 5B's ≈42**, because each beat re-pays an
  **88s Gemma load**, the transformer load and the **139s fp8 cast**.
- A **jobs-loop** (load once, render all) brings it to **≈25 min**. **That work is
  not done.**

So the honest status is: **the look is cleared, the adoption is not, and what
stands between them is engineering rather than taste.** Anyone re-litigating LTX
should start by pricing the jobs-loop, not by re-arguing the colour — that question
was answered by the person whose question it is.

**Unchanged by this addendum:** (a) and (b) stand. The licence analysis is
untouched for the third time — Attachment A, item 20, the Gemma chain and the $10M
trigger all read as they did, and **none of them was ever why**. The **OFF-BUCKET —
PROVISIONALLY NON-COMPARABLE** markers on every LTX row also stand: they are a
statement about geometry, and no taste verdict retires one. The on-bucket sample
(launched 2026-08-06, killed when the render box left the LAN mid-denoise) is
**no longer a gate** — it is now an open throughput question, worth running when
the box is reachable.

---

## 2026-08-04 — clips are watch-only (Oleg), and the licence audit re-read under that posture

*Two things landed the same day and the second changes what the first means.
Evidence trail for the audit: `pipeline/research/models-licence.md` (every clause
quoted verbatim from the primary document) and `pipeline/research/DECISION.md`,
whose §7 licence-checked its two recommended models independently and reached the
same verdicts. Items 1-3 are record entries; items 4 and 5 are open and founder's.*

**0. THE POSTURE.** Oleg, process authority, 2026-08-04, verbatim:

> "when we publish clips they are for people to watch, not use for anything, so
> dont create problems for scale."

**Published rendered media carries no reuse grant — watch-only. We are not
offering clips under CC BY 4.0.**

*What this changes:* every objection of the form "our CC BY 4.0 offer would grant
reusers rights this licence does not give us" is moot **for media**, because there
is no offer. That argument was doing the work in the Flow finding (D13), the
OpenRAIL++ stills finding (D15) and the first draft of D16.

*What it does NOT change:* **every restriction that binds US as the party
rendering and publishing.** Non-commercial clauses, territory limits, revocable
grants, registration gates and personal-use-only ToS all reach our own act of
using the weights, and are untouched by what we offer viewers. Items 2 and 3 below
are entirely about keeping that distinction straight.

*And it is posture, not yet law here.* `pipeline/licence_gate.py` still tests every
asset against the CC BY 4.0 offer; `LICENSE-CONTENT.md` still applies CC BY 4.0 to
leaves; the 38-violation debt count and the lint ratchet are both computed on the
old premise. [D1](#d1--content-license) recorded CC BY 4.0 for content and is a
*resolved* decision — amendable the way it was made, which is not by a steward.
Making watch-only real in the licence files and the gate is item 5.

**1. HunyuanVideo's territory rejection is CONFIRMED verbatim, and it extends to
HunyuanVideo-1.5.** Both `tencent/HunyuanVideo-I2V/LICENSE` and
`tencent/HunyuanVideo-1.5/LICENSE` carry the identical Tencent Hunyuan Community
License clause:

> "'Territory' shall mean the worldwide territory, excluding the territory of the
> European Union, United Kingdom and South Korea."

Its output clause is generous (*"Tencent claims no rights in Outputs You
generate"*) but operates only inside Territory, and we publish on TikTok and a
public website that we cannot geo-fence. **HunyuanVideo-1.5 (8.3B, November 2025)
is the one being pushed hardest in 2026 roundups and is repeatedly mis-described
as Apache-2.0. It is not** — that is the specific error to expect from secondary
sources. The rejection also reaches **FramePack**, whose *code* is Apache-2.0 but
whose weights (`lllyasviel/FramePackI2V_HY`) declare no licence at all over a
HunyuanVideo derivative: no tag, no LICENSE file, no base_model. Named explicitly
because a permissive code licence plus a 6GB VRAM figure makes it the single most
likely thing here to be adopted by accident. Recorded in `pipeline/vet_model.py`
CASES as well, so the tool refuses it rather than only this file.

**Watch-only does not touch this one.** Territory is a limit on *our* licence to use
the weights at all: publishing where EU, UK and South Korean viewers can see it is
outside the granted Territory whatever grant we do or do not offer them.

**2. The Wan2.2-TI2V-5B-Turbo chain: BLOCKED at the distill, and no mirror can cure
it.** The 4-step distill `quanhaol/Wan2.2-TI2V-5B-Turbo` is **CC BY-NC-SA 4.0**
(`LICENSE.md` in the GitHub repo; the HF weights repo declares nothing at all, and
GitHub's own detector reports `spdx_id: NOASSERTION`, which is how a tag-based
check misses it). Two clauses each disqualify it independently — §1(k) *"NonCommercial
means not primarily intended for or directed towards commercial advantage or
monetary compensation"*, and the ShareAlike requirement that adaptations carry
*"the same License Elements"*. **ShareAlike is decisive on its own:** CC BY 4.0 is
not a BY-NC-SA-compatible licence and cannot be, since compatibility requires
carrying NC and SA forward — so even if the NC argument went our way we still
could not publish the result under CC BY 4.0, which is what our provenance model
does. The base is fine and nothing is wrong upstream: Apache-2.0 permits a
finetuner to license their own contribution more restrictively, and these authors
did. Every downstream link inherits it — the unlicensed diffusers conversion, the
unlicensed fp16 repack, both `apache-2.0`-declaring GGUFs — and the temptation is
real enough to name: those GGUFs run in **4GB at 4 steps** and their card
recommends exactly our 704x1280. **The only clean route to that recipe is asking
the Fudan authors to dual-licence, which is founder-reserved outbound contact**
(and even then CausVid's upstream terms would need checking). Do not adopt any
Turbo build, under any repo name, at any quantisation.

**READ THIS BEFORE ANYONE READS WATCH-ONLY AS UNBLOCKING AN NC MODEL. It does
not, and this verdict is unchanged by item 0.** CC BY-NC-SA's NonCommercial clause
binds **us** — the party loading the weights, rendering, and publishing for a
project that is explicitly commercially-adjacent. Loading weights to render *is*
reproduction, so the grant does not cover the act even before anything is
published; and ShareAlike constrains what we may license anything made from it
under, which is a limit on us too. Neither clause has anything to do with what
grant we offer viewers, so removing the reuse offer removes nothing here. **The
same reasoning keeps D13's five PixVerse beats blocked** — a free tier that is
personal-use-only binds us as the publisher, and a public episode for this project
is not personal use. Watch-only clears *pass-through* arguments and only those.

**3. The output-use rule, generalised and then rescoped the same day.** Our record
says OpenRAIL/OpenRAIL++ is structurally incompatible with our CC BY 4.0 offer.
The audit recommended widening that to a single test:

> ~~**Any licence that conditions the use of OUTPUT is a problem for us, whatever
> the licence is called.**~~

**SUPERSEDED 2026-08-04 by Oleg's watch-only decision (item 0), the same day it was
recorded.** Its reasoning was pass-through — we cannot grant reusers rights we do
not hold — and with no reuse grant on media there is nothing to pass through. As
written it would now reject models over restrictions that could never bite us.
**The rule that replaces it:** a condition on output use is a problem only if

- **(a)** it could bite **our own** publication or promotion of the episodes, or
- **(b)** its notice or disclosure obligations are impractical at our scale.

Everything else in a restriction schedule is a list of things we were not going to
do anyway. Worked through the three cases the old rule caught:

- **RAIL-M — still BLOCKED, on (a).** *"No use of the Output can contravene any
  provision as stated in the License"*, and the provision it points at is
  *"academic or research purposes only"*. Publishing an episode is neither, so this
  one reaches our own publication directly.
- **LTX-2/2.3 — passes (a), and (b) is a founder decision.** One AI-generated label
  per post is practical; item 20 is the real question. See D16.
- **CogVideoX — still BLOCKED, and not on an output clause at all.** A registration
  gate we must pass, a hard one-million-visits-per-month traffic cap, a political
  field-of-use clause, and a **revocable** grant. Every one of those binds us.

So the surviving test is: **"does this licence restrict what WE may do with what we
make, or oblige us to something we cannot sustain per post?"** `licence_gate.py` and
`vet_model.py` still implement the *old* shape — `vet_model`'s three states turn on
*"does the grant reach the output"* — which is stricter than we now need but never
wrong in the dangerous direction. Rewording the code is not urgent; reading item 0
before trusting either tool's verdict is.

**4. The OpenRAIL++ stills debt (D15, and D13's Flow finding) — RE-OPENED FOR
REVIEW. Not resolved, and not by the steward.** D15's argument was pass-through:
*"the output's use is bound to Attachment A's restrictions, and our own release
offers reusers CC BY 4.0, i.e. unrestricted use. We cannot grant what we do not
hold."* Item 0 removes exactly that half of it. What is left is the question D15
never had to answer — **what does SDXL's Attachment A actually forbid, and does any
of it bite our own publication or promotion?** Its own option 3 already gestured at
the answer (*"Attachment A forbids uses we have no intention of making"*), and under
watch-only that is the option that got stronger, not weaker.

**Do not read this as 38 violations clearing.** Nobody has enumerated Attachment A
against our actual conduct yet, the ratchet still stands at 38, and the same
re-reading is owed to **D13's Flow finding** — pass-through was half of it, but the
visible SynthID watermark and the two conditions on *us* (no training on the output,
no passing it off as human-made) are the other half and are untouched. **Explicitly
out of scope: PixVerse and any NC input.** Those bind us (item 2), so no posture
change reaches them. This is R4/governance — the founder's, flagged here so nobody
acts on the old reasoning in either direction.

**5. FOR ROMAN — watch-only meets crowd-first, and the split needs his word.** Two
things he owns intersect here: dad's **crowd-first directive** (full transparency,
fork-per-beat, the shot board as the main artifact — D11) and the still-pending
licence pick for episode 1. The coherent split to put to him: **story, scripts, node
text, taste files, pipeline and the repo itself stay open exactly as they are;
rendered MEDIA is watch-only.** That keeps "the repo IS the product" intact and takes
only the mp4s out of the reuse offer. It needs a [D1](#d1--content-license) amendment
and a licence file that says so — and it interacts with D16's item-20 standing rule,
since a contributor-facing render service is the one thing LTX must never power.
**Open — founder item, not a resolution.**

## D17 — Working cuts may publish to an unlisted review area (RESOLVED — founder, 2026-08-07)

**Question:** may a cut the author has not passed be served from banyan.city so
he can watch it, or must it stay a file on a laptop?

**Status:** **resolved** (2026-08-07, founder, in session) — **it may.** His
words, verbatim:

> i don't remember making this rule... its just unnessecary restrictions

> "Don't produce media from scripts I haven't read" does not mean you cant put
> media we have already produced on the website.

**He is right, and the provenance is exact.** The rule he could not remember
making is **[D9](#d9--when-is-a-nodes-t3-video-leaf-publishable)**, written by
the steward on 2026-07-13 (`6064860`), whose own status line reads *"open —
draft criteria below, for the founder to ratify or amend."* **No ratification of
it exists** — not in git, not in this file, not in `STATE.md`, not in the
session transcripts. He never made it because nobody ever made it; it has been
draft decision-support for twenty-five days, applied as if it were law.

And it was applied wider than it was written. D9 asks one question — *when does
an assembled T3 episode become a node's official `live` leaf* — which is the
**canon** question. Its criteria were being read as gating any appearance of a
cut on the site at all, including a copy that claims to be no such thing. That
step is not in D9 and was never anywhere else either.

**What changed.** Cuts he has not passed may be published to an **unlisted
review area** — `/review/`, built by `build_site.render_review()` from
`cuts/cuts.yaml`. Every item is stamped *WORKING CUT — NOT THE EPISODE*, dated,
and carries what changed since the previous cut. The page sends
`<meta name="robots" content="noindex, nofollow">` and nothing in the site
navigation links to it; the one link is from the author's own decision queue on
the studio page, which is where he goes to make the call. The mp4s are
committed — the single sanctioned exception to *media does not go into git*,
because a static site cannot serve a file that is not in the repo.

**What this does to D9.** D9's dangling status resolves as follows, and only
this far: **its screening-gates-publication reading is superseded for WORKING
CUTS** served from the unlisted review area. **Its criterion 4 stands** — *"the
author has seen the assembled episode and approved it as the node's
representative video (R4)"* — because that is the canon gate, and unlike the
rest of D9 it matches what was actually ratified elsewhere. Criteria 1, 2, 3 and
5 (footage complete, watermark policy, provenance, lint green) are untouched and
still apply to a `live` leaf. **D9 remains OPEN as to canon**; nothing here
ratifies the parts of it nobody has ratified.

**What did NOT change, and none of it was up for discussion:**

- **STEWARDSHIP §6 stands untouched, and it is the one gate here that was
  genuinely ratified.** Dad asked for it on 2026-07-25 — *"I have to see the
  narrative before you produce the footage and attach the audio. Right?"* — the
  founder assented the same evening at 20:38:22Z — *"yeah that split sounds
  right, do it"* — and it was committed as `b6c510a`. No voice synthesis, no
  footage render, no episode assembly from a script the founder has not read.
  Every beat on the review page comes from the approved 001 script; this
  decision moved nothing into production.
- **The canon gate stands.** No cut becomes THE episode without his verdict
  (R4). None of these has a leaf, none is on the season page, and the stamp says
  so on every player.
- **The licence gate applies to everything served.** `cuts/` is now one of
  `licence_gate.Gate.run()`'s scanned roots, and every file passes
  `build_site.publishable()` before it is copied. A blocked file is named on the
  page as withheld, never quietly dropped. Debt is unchanged at 38.

**The open licence question this does not settle.** The drawn frames under every
beat are `cagliostrolab/animagine-xl-3.1` (OpenRAIL++), which is the open
**[D15](#d15--every-approved-still-is-openrail-and-the-gate-was-clearing-it-open--founders)**
debt. Publishing these cuts adds no new model and no new exposure — the episode
already on the site carries the same debt — but it does not resolve it, and the
review page says so in its own receipts rather than leaving a reader to find out.

**How to revisit:** delete the block from `cuts/cuts.yaml` and the files stop
being served on the next build. Nothing else depends on them.

## D18 — "Spend guards are code" covered renders and nothing else; a metered service now gets its guard and its meter before it is connected (RESOLVED — dad, 2026-08-08)

**Question:** the project has had a hard spend rule since the beginning — caps
in `pipeline/budget.yaml`, `generate_shots.py` refusing without `--yes`, every
charge landing in `ledger/render-spend.csv`. It stopped a $0.40 breach from
becoming a habit. So how did banyan.city run up **more than $100 in under a
month** without one line of it appearing in any ledger, on any page, or in any
refusal?

**Status:** **resolved** (2026-08-08, dad, on removing the project from his
Vercel account) — because **every guard we had was pointed at renders**, and
this was not a render.

**What the old rule actually covered.** Read it literally, the way the code
implements it: a *render* has a *provider*, a *per-run price* and a *lifetime
cap*, and a human types `--yes`. Every clause assumes a discrete, priced,
human-initiated job. Infrastructure is none of those things. Build minutes and
bandwidth have no per-run price, no `--yes`, no row, and — the part that made
this expensive — **no human initiating them**. A courier heartbeat is not a
purchase decision anyone makes; it is a purchase decision the *machine* makes,
2,344 times in a month (STATE.md 2026-08-08). The guard could not have caught
it, because the guard was waiting to be asked.

**The decision, and it is deliberately wider than Vercel.** *Any metered
external service gets two things before it is connected to this repo, and
"before" is the whole rule:*

1. **A code-side guard**, in the repo, that bounds what the machine can spend
   without a human — the same shape as `budget.yaml`, adapted to whatever the
   meter counts. For a build service that means an explicit **allowlist of refs
   that may trigger a build** (default: `main` only) committed in config, so a
   new branch costs nothing until someone says it should. For a bandwidth or API
   meter it means the cap and the refusal path in code, not in a dashboard
   setting that no reader of this repo can see.
2. **A monitoring line on the status page**, fed by a $0 source, that says what
   the thing has cost so far. **A meter nobody can read is not a meter.** Free
   tiers do not exempt a service from this — a free tier is a meter with a cliff,
   and the cliff is where the bill starts.

**A dashboard toggle does not satisfy this.** The setting that would have
prevented the whole incident exists in Vercel's UI, and its absence is invisible
from the repo: `vercel.json` carries `"github": {"silent": true}`, which silences
comments and reads, to a hurried eye, like it silences builds. Guards live in
files a reader can diff. If the only record of a limit is in someone's account
settings, the limit is not part of the product and the next person to connect a
service will not know it was ever there.

**What this does NOT change.** It adds no authority to the steward. Opening an
account, choosing a paid tier, moving a domain, and every credential remain
**founder-reserved human steps**, exactly as before — this decision governs what
must be *built and visible* before such a connection is made, never who may make
it. And it does not retroactively bless the spend: the >$100 was real money on
dad's card, and the standing instruction that came with it — keep money in mind,
permanently — is the reason this is a decision entry and not a bug fix.

**How to revisit:** amend per Guideline 6. The concrete obligations it creates
are tracked as work, not left as sentiment — `infra-spend-tile-1786166880` in
`pipeline/farm-queue.yaml` builds the status line, and the ref allowlist ships
with whatever config the new account's project uses.

## D19 — The steward may run ahead of the founder's eye: production is ungated, publication is not, and taste becomes a written model (RESOLVED IN PART — dad, 2026-08-09; one item OPEN, the founder's)

**Question:** the founder's eye is this project's ground truth and always has
been — R4 reserves taste to the author, §6 reserves media to scripts he has
read. But an eye is not available on demand and the machine is. Through late
July and early August the pattern repeated: work finished, then waited, and the
GPU sat at 0% while a verdict slept. Can the steward act *ahead* of his verdict
without ever acting *instead* of it — and if so, where exactly is the line?

**Status:** **resolved in part** (2026-08-09, three directives from dad in one
day) — **yes, ahead is allowed; instead is not.** Production runs without a
prior look; publication and money do not move without the founder. One item —
the §6 conversion and one leaf sentence that rides with it — is logged **open**
at the end of this entry, because §6 reserves itself to the author of record.

**The three directives, in the order he gave them, verbatim.**

1. *"human feedback should never be a blocker, by design"* — the pipeline may
   not be built so that a human look is a required step between two machine
   steps. Work is staged speculatively; the verdict lands on finished candidates.
2. *"taste has to be codified and iterated on"* — his judgement stops being an
   oracle only he can run and becomes a written, falsifiable model the steward
   can be wrong in front of.
3. *"only publishing and moey spending is gated. all production including audio
   you can handle. I will give feedback if needed."*

**What (1) and (2) built, the same day.** `taste/steward-model.v1.md`: ten
ranked axes mined from every recorded verdict in the repo, each with an
observable test and his own words with a date; five binary admissibility gates
that run *before* any score, because a gate failure means a candidate is
unjudgeable and must not reach his eye; −2…+2 per axis with any −2 vetoing the
pick outright, since he does not trade a named fault against a virtue; and
`taste/steward-model.ledger.yaml`, where a predicted verdict and a confidence
are written **before he sees anything** and his words land beside them verbatim
as hit/partial/miss. Only misses drive v2. `taste/sapling.founder.v0.3.md` is
untouched and stays his — the new file is the steward's *predictor* of him, and
its header says a disagreement means the model is wrong, never him. It
authorises nothing.

**What (3) settles.** Rendering, voice synthesis and episode assembly stop being
things that wait for a look. Audio is named explicitly because it was the half
most often held back. His notes become **pull-based** — *"I will give feedback
if needed"* — volunteered when he has something to say, rather than a gate the
pipeline halts at to request one. Taken together the three complete
**PROVISIONAL MODE**: labelled provisional pick, machines ahead of the verdict,
nothing scheduled around a human being awake (the standing 2026-08-05
directive).

**What stays gated, in his words: publishing and money.** Public posting on his
accounts and spend of any kind remain founder-reserved, unchanged and
unconditioned by this. [D17](#d17--working-cuts-may-publish-to-an-unlisted-review-area)'s
unlisted `/review` area is the screening surface — a working cut landing there
is not publication — and nothing unratified reaches a public surface.
Provisional labelling and the prediction ledger are conditions of the whole
arrangement, not decorations on it: the licence to run ahead is paid for by
saying, in advance and in writing, what the steward expects him to say.

**In practice none of the open item below costs anything today.** §6 only ever
bit on media made from script text the founder has not read, and the only
episode in production is not that:
`genomes/sapling/nodes/002b-first-citizen/leaves/002b-t0-c.yaml` carries
`approved_by: founder`, `approved_on: 2026-08-03`, his approval quote, two
`approval_conditions`, and two further revisions in his own words dated
2026-08-08. Production on 002b is clear on the §6 axis however this resolves.

### OPEN — one ratification commit closes both halves (the founder's, per STEWARDSHIP Term 2)

**(a) The §6 conversion.** Read literally, *"all production"* reaches past
approved scripts and would relax [STEWARDSHIP.md](STEWARDSHIP.md) §6 from
*read-before-media* to *read-before-publish*. **That amendment is not entered
here**, because §6 anticipates this precise instruction and refuses it by name.
Its text says it is *"stated plainly so it is not softened later"*, and it closes:

> Corollary on *whose* approval: this gate is the founder's. Family and
> contributors may review, request, and be listened to — their notes have driven
> most of the loop's cycles — but a script becomes producible only when the
> author of record says so.

Two facts are logged here and neither is adjudicated against the other. **The
directive came from dad**, and the corollary's named ratifier is the author of
record. **And it arrived through the same chat channel that has been carrying
founder verdicts all week** — verdicts this repo has booked as the founder's and
acted on: *"yeah its good"* passing beat 1's VO retake, and the three-character
plate pick `b15-r3-s1`, both 2026-08-08. So the channel is the one the project
already treats as authoritative, and the corollary still names a ratifier who
has not ratified *this*. §6 therefore stands as written until that one commit.

**(b) One sentence in 002b's leaf, superseded by his own subsequent conduct.**
`002b-t0-c.yaml`'s `approval_scope` says approval covers the STORY only, not the
shot prompts, and closes: *"No VO, no stills and no footage may be produced
until the dialect is settled."* Written 2026-08-03, that sentence is the text
that forbids the episode-level renders now being staged — and the founder
himself has walked past it repeatedly since:

- **He approved episode 2's VO after it was written** — `54562ca` (beat 16 gets
  a voice), `0636023` (beat 1's retake passes, *"narration is complete with
  nothing left to ask"*), `c21c8f4` (he settles both of episode 2's lines, one
  of them by changing nothing). Those are the same 2026-08-08 revisions the leaf
  records above its own prohibition on VO.
- **He directed the b02-21 redraw wave and screened its predecessors**, and the
  dialect it was drawn in is the current native-tag recipe — `shots.md` was
  converted for that 80-image batch on 2026-08-07, with the token-budget fix
  measured rather than guessed. Beat 01's sample was screened and its successor
  plate picked from the r3/r5 sheets.

The sentence is therefore **stale, not violated**: the dialect was settled by
conduct. It is annotated in place and **not deleted** (R6, and closed decisions
are never edited away) — the annotation points here. Its formal retirement rides
with (a) so that one founder commit closes both. Flagged independently the same
night by the item08-close workstream, which reached the same conclusion from the
other direction.

**How to revisit:** amend per Guideline 6, except the open item, which is the
founder's one commit. The prediction ledger is the evidence this decision will
be judged on — if the model's rolling hit rate does not earn the licence to run
ahead, the licence is what should shrink, not the record of what it predicted.
