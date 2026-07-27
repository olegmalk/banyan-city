# Regrow an episode

The Promise says anyone can re-render any episode **better**. This is the door.
A leaf is one render of a node; leaves coexist as siblings, so your regrow
never overwrites anyone — it lands next to the existing renders and competes
on material. No permission needed at any step. Rough is fine: a regrow that
exists beats a perfect one that doesn't.

## 1. Pick an episode (and beats)

Any node with a `shots.md` is regrowable — one generation prompt per script
beat, status-marked (✅ generated · ⬜ needs footage). Start at
[`genomes/sapling/nodes/001-capability-inventory/shots.md`](genomes/sapling/nodes/001-capability-inventory/shots.md)
or browse the tree at <https://banyan.city>. You can regrow a single beat or
the whole episode — `render_t3.py` slates whatever's missing, so partial
regrows still assemble end-to-end.

Two things are canon and travel with every prompt:

- **The prompts themselves** — run them verbatim, then improve execution
  (model, seed, steps), not intent.
- **The style bible** — [`genomes/sapling/style.md (⚠ stale — v2 look killed 2026-07-27, see STATE.md; v3 pending)`](genomes/sapling/style.md (⚠ stale — v2 look killed 2026-07-27, see STATE.md; v3 pending))
  (low-detail anime, v2). Style is a taste axis (R4); a regrow in a different
  style is a fork of taste, not a regrow.

## 2. Render — three routes

### Route A — free: the Kaggle notebook ($0, anyone)

[`pipeline/kaggle/render-kaggle.ipynb`](pipeline/kaggle/render-kaggle.ipynb)
renders `shots.md` prompts with open Apache-2.0 Wan 2.1 weights on Kaggle's
free GPU quota (30 h/week). Exact steps:

1. [kaggle.com](https://www.kaggle.com) → **New Notebook** → **File → Import
   Notebook** → upload the `.ipynb`. Account must be phone-verified for GPU.
2. Notebook settings: **Accelerator = GPU (T4/P100)**, **Internet = ON**.
3. Edit the config cell: `GENOME`, `NODE` (e.g. `"001"`), `BEATS` (`None` =
   every beat without ✅, or `[3, 5]`), `SEED`, `STEPS`.
4. **Run All**. ~20–45 min per clip; a 5-beat episode is an afternoon of queue.
5. Download `clips.zip` from the **Output** tab and unzip locally.

Each clip arrives as `NN-slug.mp4` with its `NN-slug.meta.yaml` provenance
already written. Honest roughness: output is 480×832 at 5 s per beat — beats
run longer, so `render_t3` pads the last frame and you'll see it. That's the
$0 floor, and it's real.

### Route B — your own API key: `generate_shots.py`

Compute-as-watering with your key, your money — the tree spends nothing:

```sh
python3 pipeline/generate_shots.py sapling 001 --provider wan --clips-dir /tmp/ep001 --yes
```

Providers: `wan` (`DASHSCOPE_API_KEY`), `fal` (`FAL_KEY`, pick `--model`),
`veo` (`GEMINI_API_KEY`), `kling` (agent CLI). `--beats 03,05` limits scope.
The script prints a cost estimate, refuses without explicit `--yes`, honors
the caps in `pipeline/budget.yaml`, and writes `NN-slug.mp4` +
`NN-slug.meta.yaml` — exactly the layout step 3 assembles.

### Route C — any tool of yours

Platform free tier, local ComfyUI, whatever you've got. The contract:

- Run the `shots.md` prompts **verbatim** (they carry the
  [style bible](genomes/sapling/style.md (⚠ stale — v2 look killed 2026-07-27, see STATE.md; v3 pending)) block).
- 9:16 vertical, ~10 s per beat, base footage only — no burned-in text, no
  dialogue; post adds overlays, captions, VO.
- Save as `NN-slug.mp4` (`NN` = beat number) and write `NN-slug.meta.yaml`
  by hand:

```yaml
# Shot provenance (§7.2)
platform: your-tool-or-platform
model: exact-model-name-and-version
shot_beat: 3
prompt: 'the verbatim prompt you ran'
seed: 20260720          # if your tool takes one; omit if not
duration_s: 10
aspect: '9:16'
cost_usd: 0.0           # what YOU paid; estimates say so in a note
date: '2026-07-20'
```

## 3. Assemble

Bench-render first (touches nothing):

```sh
python3 pipeline/render_t3.py sapling 001 --clips <your-clips-dir> --out /tmp/001-regrow.mp4
```

Watch it. Missing beats render as slates; a `NN-vo.mp3` beside a clip is
muxed onto that beat automatically. Deps: pyyaml, pillow, ffmpeg on PATH.

When it's right, publish the leaf — drop `--out` and pick the **next unused
suffix** (node 001 already has `-t3-a` and `-t3-b`, so yours is `c`):

```sh
python3 pipeline/render_t3.py sapling 001 --clips <your-clips-dir> --suffix c
```

This writes `leaves/001-t3-c.mp4` + `leaves/001-t3-c.yaml` — aggregating your
`meta.yaml` files into per-beat `sources` — and registers the leaf in
`lineage.yaml`. The leaf yaml it writes (hand-write the same shape only if
your route bypassed the pipeline):

```yaml
# Leaf metadata — every render publishes its full provenance (§7.2)
leaf: 001-t3-c
node: '001'
tier: T3
form: full-video-mp4
content: 001-t3-c.mp4
author: pipeline/render_t3.py (assembly; per-beat footage sources below)
model: "per-beat — see sources"
prompt: "per-beat — see sources"
seed: "per-beat — see sources"
cost_usd: 0.0            # sum of what you actually paid
status: live             # live | superseded | ring — leaves are archived, never deleted (R6)
platform_urls: []
sources:                 # one entry per beat, from your NN-slug.meta.yaml files
- beat: 1
  slug: "COLD OPEN — 0:00–0:12"
  clip: 01-cold-open.mp4
  audio: none
  platform: kaggle-free-gpu
  model: Wan2.1-T2V-1.3B (Apache-2.0)
  cost_usd: 0.0
```

## 4. Submit — the PR

One PR, containing:

- [ ] your clips + `NN-slug.meta.yaml` files — in the node's `clips/` dir if
      it's free, else a sibling `clips-<suffix>/` dir (`--clips` points anywhere)
- [ ] `leaves/<node>-t3-<suffix>.mp4` + `.yaml` (step 3 wrote both)
- [ ] the leaf registered in `lineage.yaml` (step 3 did this too)
- [ ] one row in [`ledger/watering.csv`](ledger/watering.csv) — compute is
      watering ([WATERING.md](WATERING.md)):

```csv
2026-07-20,001,001-t3-c,yourhandle,compute,0.00,"Kaggle T4 ~3 GPU-h, 5 beats, Wan2.1-T2V-1.3B",costs-first-70-30-v1,
```

- [ ] `python3 pipeline/lint_genome.py` passes

Use a handle (or `anonymous`) — never more than you choose to publish. If git
isn't your thing, open an issue with a link to your clips and the steward
files the PR credited to you.

## 5. What happens next

- **Citizens screen it.** Your leaf enters the same public queue as every
  render — the [🔍 Screen a leaf](../../issues/new?template=screening.yml)
  form ([CONTRIBUTING.md](CONTRIBUTING.md)), landing in the node's
  `sap/screening.yaml`. Screening narrows; it doesn't decide.
- **The taste file decides.** The author's extracted rules
  ([`taste/sapling.founder.v0.3.md`](taste/sapling.founder.v0.3.md)) are
  applied to the shortlist; selection commits cite rule IDs
  ([README](README.md#how-curation-works-the-short-version)).
- **Leading leaf is a taste call.** Which render fronts the node page is the
  founder's call on material (R4); see [DECISIONS.md](DECISIONS.md) for the
  hardening thresholds. If yours leads, the old leaf goes `superseded` —
  archived with full provenance, never deleted (R6). If it doesn't, it stays
  live as a sibling, and your ledger row stands either way.
