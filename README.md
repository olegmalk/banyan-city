# Banyan City

**An open framework for growing story trees** — AI-rendered, vertically-shot micro-drama series that *branch* instead of running linear. Curated by one human author's extracted taste. Screened and funded by the citizens watching. Every decision, dollar, and render publicly auditable in this git repository.

This repo **is** the product. There is no company behind it, no walled platform, no paywall. Just a tree, its genome, and the people who water it.

> Read [PROMISE.md](PROMISE.md) first. It's short, it's canonical, and everything else follows from it.

---

## Start here

| If you want to… | Read |
|---|---|
| Understand what this place promises | [PROMISE.md](PROMISE.md) |
| Learn the seven rules of the grove | [GUIDELINES.md](GUIDELINES.md) |
| Decode the words (tree, leaf, sap, watering…) | [VOCABULARY.md](VOCABULARY.md) |
| See the full design and build plan | [PRD.md](PRD.md) |
| Read the first story | [`genomes/sapling/`](genomes/sapling/) — start at [node 001](genomes/sapling/nodes/001-capability-inventory/node.md) |
| See what's still undecided | [DECISIONS.md](DECISIONS.md) |

## The first tree: *Sapling*

An engineer dies debugging production at 3 a.m. and reincarnates in another world as a **banyan sapling**. He can't move, fight, or flee — only sense, grow, and make the space around him worth staying in.

The story has already branched. After [node 001](genomes/sapling/nodes/001-capability-inventory/node.md), three continuations of the same moment coexist as siblings — all alive, none rejected:

- **[002a — The Broken Channel](genomes/sapling/nodes/002a-broken-channel/node.md)** — the roots find broken irrigation, and the world *responds*
- **[002b — The First Citizen](genomes/sapling/nodes/002b-first-citizen/node.md)** — a fugitive scavenger talks to a plant, and the plant answers
- **[002c — ADMIN(?)](genomes/sapling/nodes/002c-admin-wireframe/node.md)** — at sunset the world renders wireframes, and one label is his

Which one leads? That's decided on material and watering, not by vote and not by decree. Read them and react.

## How to branch a story

Anyone may branch any released node. Your only obligation: **declare your parent** (Guideline 1).

1. Fork this repository (or open a PR here — both are legitimate; a branch doesn't need the root repo's permission to exist).
2. Create a node directory under `genomes/sapling/nodes/`, e.g. `002d-your-title/`, containing:
   - `node.md` — your script: beats, the state change (R1 — every scene must change something), and the hook (R5). Text is a real render — the T0 tier costs nothing.
   - `leaves/` — metadata for each render of your node (see any existing node for the format)
   - `sap/` — starts empty; reaction data accumulates here
3. Add your node to `genomes/sapling/lineage.yaml` with its `parent:` declared. That line is the whole ceremony.

Your branch may contradict, subvert, or outgrow its parent. The tree polices lineage, never direction. It can never be deleted — only go dormant if unwatered, and anyone may revive it.

Don't want to write new story? **Re-render existing story better** — any episode, free GPU included: [REGROW.md](REGROW.md).

## How to fork the city

Take everything — guidelines, structure, vocabulary, pipeline. Rename it. Go. The concrete checklist is **[SEED.md](SEED.md)**, and the taste-extraction interview (the framework's front door, [PRD.md §7.3](PRD.md)) is runnable:

```sh
python3 pipeline/extract_taste.py --tree <your-tree> --author <you>
```

No permission, no notice, no shame. A fork is how the forest spreads. Contributions to *this* tree — reacting, screening, branching, building — are covered in [CONTRIBUTING.md](CONTRIBUTING.md).

## How curation works (the short version)

- **Citizens screen.** Rendered candidates enter a public queue; the crowd rates and **narrows** — it does not decide.
- **The taste file decides.** The author's extracted rules ([taste/sapling.founder.v0.3.md](taste/sapling.founder.v0.3.md)) are applied to the shortlist; every selection commit cites the rule IDs that drove it.
- **The human amends rules, never commits.** If a selection feels wrong, the fix is a public diff to the taste file — the log stands.
- **Disagreement is exit, not override.** Don't like the trunk? Water a rival branch.

## Money

Citizens fund **specific renders**, not vague content ("Node 002b, 8 candidates, ~$14"). Every render publishes its prompt, model, seed, and cost. Every dollar lands in [`ledger/watering.csv`](ledger/watering.csv) with its published split. The ledger is empty right now — watering (money **and** compute) is documented in [WATERING.md](WATERING.md) and opens in Phase 3, blocked on the split decision ([D5](DECISIONS.md)).

## Read it without git

The tree lives at **<https://banyan.city>** — the lineage as an explorable tree, every node's script, every leaf's cost, and a 💧 react link per node. (Free mirror: <https://olegmalk.github.io/banyan-city/> — the canonical layer is git; rendering surfaces are plural and disposable.)

Reactions are mapped to GitHub issues (one per node — [#1](https://github.com/olegmalk/banyan-city/issues/1) onward, one issue per node as the tree grows); each node's `sap/reactions.yaml` records its channel canonically.

## Status

**Phase 2 underway; the render ladder is climbing to full video.** The tree is visible: the site builds from `pipeline/build_site.py` and deploys on every push; `pipeline/lint_genome.py` guards the tree's structure in CI; reactions map to issues and are harvested daily into each node's `sap/summary.yaml` by `pipeline/harvest_sap.py`. Every node carries T0 (script), T1 (storyboard, `render_t1.py`), and T2 (silent animatic, `render_t2.py`) leaves — all at $0. **T3 (full AI video) is now real:** `pipeline/render_t3.py` assembles platform-generated clips into a captioned, card-topped 9:16 episode, and the first footage is in — the [T3 platform trials](https://banyan.city/trials) render the same three shots on each candidate model (first up: Veo 3.1 via Google Flow), scored in the open. The first full episode of node 001 is assembling as its shots come in (see [`shots.md`](genomes/sapling/nodes/001-capability-inventory/shots.md)). Next: finish a watermark-free node-001 episode, choose the model on trial evidence, then open watering/money (Phase 3, blocked on [D5](DECISIONS.md)).

## Licenses

- Story content: [CC BY 4.0](LICENSE-CONTENT.md) (provisional — see [D1](DECISIONS.md))
- Code: [MIT](LICENSE-CODE.md) (provisional — see [D2](DECISIONS.md))
