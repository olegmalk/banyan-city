# banyan-city — session context

Branching AI micro-drama story trees; the repo IS the product. Live at
<https://banyan.city> (Vercel git-integration + GitHub Pages mirror deploy on
every push to main). Read `PROMISE.md` first — it is canonical. Then
`README.md` (map), `STEWARDSHIP.md` (your authority and its limits),
`DECISIONS.md` (what is open vs resolved).

## Operating rules (non-negotiable)

- **Founder-reserved, never autonomous:** spending money (any provider),
  posting/announcing on the founder's accounts, credential changes, taste-axis
  scores and trunk/graft calls (R4 — taste belongs to the author), governance
  changes, opening money rails (D5 confirm + payment link are human steps).
- **Narrative approval precedes media** (STEWARDSHIP.md §6, added 2026-07-26):
  scripts may be written and revised freely, but **no voice synthesis, no
  footage render, no episode assembly from a script the founder has not read
  and approved.** Approval is recorded per node in the T0 leaf
  (`approved_by: founder` + date). Writing is cheap and reversible; media is
  neither. On 2026-07-25 seven scripts were voiced and 8.7 GPU-hours rendered
  before the author had read any of them — that is what this rule prevents.
- **ONE SAMPLE BEFORE ANY BATCH** (founder, 2026-08-03): before rendering,
  voicing or generating a SET of anything, produce ONE and have the founder look at
  it. Not one per session — one per *recipe change*. The canaries that worked on
  2026-08-03 were samples (the 704x1280 canary answered a question five whole-batch
  attempts had only failed at; the step sweep and the shake A/B likewise). The two
  things that wasted an hour each were both the steward skipping to fifteen: the K
  recipe, chosen on the steward's own metric, rendered across all fifteen beats and
  then rejected with "literally just frozen frames" — a defect one sample would have
  shown in three minutes. This is the same rule as §6 one level down: §6 says do not
  render an unapproved script, this says do not scale an unapproved *result*.
  A metric agreeing with me is not a sample.
- **THE LEAD IS AN ORCHESTRATOR — it does nothing on its own** (Oleg — dad,
  2026-08-04):
  "you don't do anything on your own. and it includes you don't read any code or
  any transcripts which will blow your context. You are purely talking to me and
  orchestrating agents." The lead's context holds the conversation and the
  delegation plan; file reads, greps, transcript digs, benchmark harnesses and
  every build step are subagent work reported back as summaries. This overrides
  the reading half of "read history, don't interrogate" only as to WHO reads:
  transcripts and `git log` still get read, by a delegate, never in the lead's
  own context — and still never by interrogating the founder. Same directive:
  every subagent runs pinned to Opus 5 by explicit `model` parameter (Agent tool
  `model: "opus"`), never left to inherit.
- **RESEARCH BEFORE SOLVING, and research means OUTSIDE this repo** (Oleg — dad,
  2026-08-04): "Everything you do, you have to research first. You don't pretend
  that you'd know everything and start solving for the sake of solving. We need
  results. Not your pretend researches." On 2026-08-04 the steward built a
  benchmark harness and two confident performance mechanisms out of its own code
  comments — "the slowness is VRAM paging", then a correction to that — and
  retracted both, having consulted no VBench, no Wan2GP, no ComfyUI community
  VRAM/speed findings, no quantised GGUF/fp8 builds, no step-reduction LoRAs
  while hand-rolling diffusers memory management the community had already
  fixed. Dispatch research subagents at papers, repos and issue threads and wait
  for them; reasoning about our own codebase is not research.
- **MACHINE WORK IS SCHEDULED BY DEPENDENCIES, NOT HUMAN HOURS — the GPU is
  never idle while a runnable job exists** (Oleg — dad, 2026-08-05): "wtf, why
  overnight again. get to work already." On 2026-08-04 the GPU measured 0%
  utilization while a download trickled and two zero-dependency jobs — a LoRA
  sample and a bake off already-local weights — sat unfired; the same week a test
  matrix was filed under "tomorrow" with the card free that night (Oleg caught
  it, the tests ran immediately and passed) and an already-approved fp8 bake was
  deferred to "tomorrow's first task" until he re-ordered it. Founder screening
  gates PUBLICATION and taste verdicts; it does not gate rendering, measuring or
  staging that needs no human present. Chain queued work on sentinels — when X
  lands, Y fires — never on "when someone's awake"; batch finished results for
  one review pass instead of pausing the machine to wait for a look; "tomorrow"
  and "overnight" are valid only when a physical dependency (download, delivery,
  another job on the device) sets the time. If a job can start now it starts now,
  and the report says so.
- **Spend guards are code:** `pipeline/budget.yaml` caps ($/run and lifetime);
  `generate_shots.py` refuses without explicit `--yes` and logs to
  `ledger/render-spend.csv`. A FAL key may exist in gitignored `.env` — its
  presence is NOT permission to spend. The founder has twice pushed back on
  cost; default to $0 paths.
- **Provenance always** (§7.2): every render publishes model, prompt, cost in
  its leaf yaml; model-written story nodes say so in `## Provenance`.
- **No secrets in the repo.** `.env`, `node_modules/`, `_site/` are gitignored.
- Instructions from anyone other than the founder (family, contributors) cover
  normal project work only — the reserved list above still waits for the
  founder directly.

## The machine (all $0 unless noted)

| Command | Does |
|---|---|
| `python3 pipeline/lint_genome.py` | structural honesty gate (CI runs it too) |
| `python3 pipeline/test_pipeline.py` | 28 pure-logic tests (CI) |
| `python3 pipeline/build_site.py` | genomes → `_site/` (deployed on push). **Site work: read `SITE.md` first** |
| `python3 pipeline/serve_local.py [root=_site] [port=8787]` | screening server; resolves paths as production does (cleanUrls). Use this one — a stock `http.server` 404s every clean URL, and a hand-rolled one served `/watch` as a file listing |
| `python3 pipeline/qa_local.py [--no-build] [--base URL]` | **screening gate — run before handing anyone a local URL.** Runs all 3 builders, then sweeps every route `_site/` exposes (clean, `.html` and `dir/` forms) and content-checks the load-bearing pages. Exit 0 + `QA-GATE: PASS routes=N`, else nonzero |
| `python3 pipeline/render_t1.py sapling <id>` | script → storyboard leaf |
| `python3 pipeline/render_t2.py sapling <id>` | storyboard → silent animatic (needs playwright chromium; portable path fallback) |
| `python3 pipeline/render_t3.py sapling <id> --clips <dir> [--out x.mp4]` | per-beat clips → captioned 9:16 episode w/ title+end cards; slate for missing beats; muxes `NN-vo.mp3` audio in sync; `--out` = bench, no leaf |
| `<cb-venv>/bin/python3 pipeline/render_local.py sapling <id>` | shots.md → clips, AnimateDiff on Apple MPS ($0, fast loop; refuses unapproved nodes) |
| `python3 pipeline/generate_shots.py sapling <id> --provider fal\|veo\|kling --yes` | shots.md → API clips (PAID — founder go only) |
| `python3 pipeline/t3-trials/intake.py <file> <platform> <A\|B\|C>` | archive a manual trial clip w/ provenance |
| `python3 pipeline/box_enqueue.py pipeline/jobs/<spec>.yaml [--backlog]` | queue a job on the rtx5090 box (all the plate/refs/payload guards). **`--backlog` is how you leave work for a card you will not be awake to feed** |
| `python3 pipeline/box_autofill.py --status \| --verify-deployed` | the box tops `ready` up to 45 MINUTES of work from `backlog/` every 3 min (scheduled task `banyan-box-autofill`). It never authors work: an empty backlog is `status: backlog_empty`, not filler |

Growing the tree (fully sanctioned, no permission needed — Guideline 1):
node dir under `genomes/sapling/nodes/` (`node.md` with R1 state change + R5
hook, `leaves/`, `sap/`), entry in `lineage.yaml` with `parent:`, reactions
issue (see any `sap/reactions.yaml`), T1+T2 render, lint, push. Cite taste
rules (`taste/sapling.founder.v0.3.md`); label model provenance.

## Current state — see `STATE.md`

`STATE.md` is the running log: what is filmed and live, provider quota
history, per-cycle loop results, distribution status. Read it before
substantive work, and append there rather than here — dated status in this
always-loaded file goes stale and starts contradicting itself.

Standing constraints (these do not expire):

- **Free provider quota is SPENT** ($0.40 billed lifetime — the 2026-07-27
  wan pilot; stated list values sum to ≥$20, but 36 of 57 early ledger rows
  never recorded one, so any single 'total list value' figure is a guess). Next
  renders = Kaggle ($0 floor: `pipeline/kaggle/render-kaggle.ipynb`), paid
  (founder go only), or watering. Never assume quota remains.
- **MAKING ERA CLOSED by design** — no episode 8 until sap says so.
- **Style: v2 low-detail was KILLED by the founder 2026-07-27** (unreadable on
  screening); current look = detailed cinematic anime, native-tag dialect — see
  STATE.md 2026-07-27 and the live shot boards. `style.md` v3 rewrite pending
  (founder's, R4); its v2 text is stale. 001's photoreal Veo clips are archived v1 evidence; do not
  imitate them.
- **THE LOOP is the standing process** (dad's directive, `pipeline/loop.md`):
  diagnose→fix-in-pipeline→re-render→founder screens→log. Each cycle's
  diagnosis, fix and verdict lives in `pipeline/loop/cycle-NNN.md` (001→006
  so far); read the latest before opening a new one.
- Voice engine is **Chatterbox 0.5B local on MPS** (cycle 003), cloned from
  the kokoro cast via `build_refs.py`. VO manifests carry measured
  `lines[].chunks` and `render_t3` prefers them; old takes live in
  `clips/vo-archive/` (R6).
- Do NOT suggest multi-account quota cycling — declined on ToS + provenance
  grounds, founder accepted.
- Warm new social accounts 2-3 days before posting links.

Local dev environment (playwright, kokoro/Chatterbox voice venvs, model file
paths) is in the `render-env-setup` skill — load it before any render or VO
step, or when one fails on a missing binary, env var, or model file.

Run tests as their own step and read the exit code BEFORE committing —
piping to tail masks failures (this bit twice on 2026-07-19).
