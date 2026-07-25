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
| `python3 pipeline/build_site.py` | genomes → `_site/` (deployed on push) |
| `python3 pipeline/render_t1.py sapling <id>` | script → storyboard leaf |
| `python3 pipeline/render_t2.py sapling <id>` | storyboard → silent animatic (needs playwright chromium; portable path fallback) |
| `python3 pipeline/render_t3.py sapling <id> --clips <dir> [--out x.mp4]` | per-beat clips → captioned 9:16 episode w/ title+end cards; slate for missing beats; muxes `NN-vo.mp3` audio in sync; `--out` = bench, no leaf |
| `python3 pipeline/generate_shots.py sapling <id> --provider fal\|veo\|kling --yes` | shots.md → API clips (PAID — founder go only) |
| `python3 pipeline/t3-trials/intake.py <file> <platform> <A\|B\|C>` | archive a manual trial clip w/ provenance |

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

- **Free provider quota is SPENT** (~$35 list, $0 billed, ledgered). Next
  renders = Kaggle ($0 floor: `pipeline/kaggle/wan-t2v-kaggle.ipynb`), paid
  (founder go only), or watering. Never assume quota remains.
- **MAKING ERA CLOSED by design** — no episode 8 until sap says so.
- **Style is v2: low-detail anime** — `genomes/sapling/style.md` is the
  visual bible. 001's photoreal Veo clips are archived v1 evidence; do not
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

Local dev: T2 stills need `T2_NPM_DIR` → dir with `npm install playwright`;
voice needs `T2_TTS_PYTHON` → python3.13 venv with `pip install kokoro-onnx
soundfile` + model files in `~/.cache/banyan-tts/` (kokoro-v1.0.onnx,
voices-v1.0.bin — free download, kokoro-onnx GitHub releases; tts_kokoro.py
self-heals the espeak data-path quirk). Chatterbox VO needs `cb-venv`
(python3.11: chatterbox-tts + `setuptools<81` for perth; `torch.load`
patched to `map_location` cpu), refs in `~/.cache/banyan-tts/cb-refs/`.
Pipeline python deps in a venv (markdown, pyyaml, pillow, imageio-ffmpeg).
Run tests as their own step and read the exit code BEFORE committing —
piping to tail masks failures (this bit twice on 2026-07-19).
