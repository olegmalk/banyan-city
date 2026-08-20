# Character LoRAs for the recurring cast

Enabler #1 for the founder's **one day per episode from ep3 on** bar
(`STATE.md`, 2026-08-20): move character identity out of the prompt and into the
weights, so it stops being re-fought per frame.

**Nothing here has been trained. Nothing here is filed on the queue.** $0 spent.

| file | what it is |
|---|---|
| `../research/character-lora-sdxl-0820.md` | UNIT 1 — the external research, with sources. Read this first; everything below is downstream of it |
| `dataset-jerry.yaml` | UNIT 2 — the curation. 31 includes and 20 rejects, each with a reason |
| `build_dataset.py` | UNIT 2 — turns the curation into captions + a sha-addressed manifest. `--check` re-verifies |
| `captions/jerry/*.txt` | UNIT 2 — 31 generated captions |
| `manifest-jerry.yaml` | UNIT 2 — generated. Paths, shas, captions, tiers |
| `SETUP.md` | UNIT 3 — the one-time trainer install on the box. **The current blocker** |
| `train-jerry-0820.yaml` | UNIT 3 — the training job + pre-registered bars. Not filed |
| `sample_lora.py` | UNIT 3 — draws one frame from a trained LoRA in the render venv |

## Scope: who gets one

Founder ruling, 2026-08-20: **one-episode characters get no consistency
infrastructure.** Surveyed against the story tree
(`genomes/sapling/lineage.yaml`, every node's speaker labels):

- **THE SAPLING** — 16/16 nodes. Gets a LoRA. **Dataset blocked, see below.**
- **THE SCAVENGER (Jerry)** — 8 nodes, ep2→ep7. Gets a LoRA. **Dataset built.**
- THE FARMER (9 nodes), THE MAGISTRATE (3) — recurring, so they qualify, but
  neither has ever been drawn to approval. They queue behind their charref, not
  behind this work.
- The two guards, the assessor, the pilgrim — one episode each. **No LoRA, and
  no reference sheets, no `canon.yaml` drift subjects, no charref rounds.**

ep3 is `003b-one-leaf-for-yes` and its entire on-screen cast is the sapling and
Jerry. Those two unblock it.

## State

**Jerry — dataset done, training blocked on SETUP.md.**
31 curated frames, all 832×1216, all committed, captions generated, manifest
sha-addressed. The install is the only thing between here and a run.

**The sapling — dataset cannot be harvested the way Jerry's was, and this is
the more important of the two.**

Jerry's dataset exists because the checkpoint *can already draw him* — the
ratified wording returns an on-model adult goblin at a good rate, so harvesting
verdicted frames was enough. The sapling is the opposite case. Per
`pipeline/work-ladder-0819.md`, the wording ladders for the canon two-leaf
sapling are **CLOSED** — three rungs on one axis, then two more, all failing the
same way: bead-strung vines, faceted crystals on bare twigs, fruit counts of 4
and 8 and 3 but never 1. **There is no pool of correct model-drawn saplings to
curate, because the model has never drawn one.**

What exists instead is ~23 frames across five beats where a canon sapling was
**composited in with numpy** (`beat19_drop_composite.py`,
`derive_b03_b13_sapcomp_0820.py` and siblings) — one rooted stem, two wide oval
cotyledons, drawn deterministically at $0 with no GPU. Several lanes are
producing more of these right now.

That inverts the usual order, and it is the interesting route: **train the LoRA
on the composites, to teach the checkpoint the thing it currently cannot draw.**
Bootstrapping a LoRA from composited or synthetic exemplars is standard
practice; here it would also retire the compositing step, which is presently a
per-beat manual cost on every sapling shot in the show.

It is not started here for two honest reasons: today's composites belong to live
lanes and are still moving, and ~23 frames across five near-identical field
scenes is below the variety floor a character LoRA needs. The gate is **≥20
composited saplings spanning distinct scenes, scales and lighting** — and the
growth ladder (`genomes/sapling/style.md:150-158`, ~15 cm and 2 leaves in 001
rising to ~1.6 m and 6 leaves by 006a) means scale and leaf count must stay
*variables in the captions*, never baked in, or one LoRA cannot serve seven
episodes. Research doc §3 and §4 spell that out.

## Next rungs, named and not fired

1. **Run SETUP.md on the box** (~3–4 GB of download, no GPU needed, can run
   while the card is busy), then file `train-jerry-0820.yaml --backlog`.
2. **A variety batch for Jerry**, ~30 GPU-minutes. All 31 frames are crouched or
   seated in a sunny field; there is one true close-up and no standing figure,
   no back view, no night. Bar B5 in the training spec is designed to expose
   exactly this, and if it fails, this is the fix.
3. **The sapling composite dataset**, once the live lanes settle and the count
   clears the gate above.
4. **Two open R4 questions for the founder, with pixels** — both surfaced by
   curating, neither settled here because taste is his: (a) Jerry's **ear
   shape** is unstable across the source frames, long pointed vs small rounded,
   and the ratified wording says nothing about ears; (b) `node.md` describes
   **"one broken tusk"** and *no* rendered frame has ever had one. A LoRA
   averages whatever it is fed, so both want a ruling before v2 — but not
   before v1, which is deliberately left mixed rather than committing to a
   reading he has not made.

## The one thing that can break the farm

`sd-scripts`' requirements pull **xformers**, and on this sm_120 card pip
resolves that by silently replacing torch with a build that has no Blackwell
kernels — which breaks *every render on the box*, not just training. Separate
venv, `--sdpa` instead of xformers, and `pip show torch` after every install
step. SETUP.md has the detail and the sources.
