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

**The sapling — DATASET BUILT 2026-08-21 (26 frames), training blocked on the
same SETUP.md. It could not be harvested the way Jerry's was, and this is the
more important of the two.**

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

It was not started off those ~23 frames for two honest reasons: they belong to
live lanes and are still moving, and five near-identical field scenes **with the
scavenger in every one of them** is below the variety floor a character LoRA
needs — a subject LoRA trained on frames that share a backdrop learns the
backdrop into the trigger, and a figure in every frame teaches it a figure. The
gate is **≥20 composited saplings spanning distinct scenes, scales and
lighting** — and the growth ladder (`genomes/sapling/style.md:150-158`, ~15 cm
and 2 leaves in 001 rising to ~1.6 m and 6 leaves by 006a) means scale and leaf
count must stay *variables in the captions*, never baked in, or one LoRA cannot
serve seven episodes. Research doc §3 and §4 spell that out.

**BUILT 2026-08-21 — `manifest-sapling.yaml`, 26 frames, gate cleared on scale
and scenes, NOT on leaf count.** Purpose-built rather than harvested, in three
steps, all $0:

1. **Plates.** Four rounds of goblin-free, plant-free ground planes by text
   (`review/ep3-sapling-dataset-0821/plates-0821.yaml`). The rule that bought
   them: *a scene clause naming only ground cover returns a macro of that ground
   cover, at any framing* — what buys a drawable plane is a landform or a
   receding feature. Round 4 then found `low angle` was cargo and was drawing a
   fisheye; dropping it returned 8 straight-horizon plates from 8 cells.
   **Eleven plates kept, eleven distinct lightings** — sunset, overcast, dawn
   mist, alpine noon, forest dapple, backlit avenue.
2. **Composites.** `build_sapling_lora_composites_0821.py` drives
   `beat16_sapling_composite.py` over a typed geometry table: 26 rows, four
   scale tiers, varied root, tilt, leaf length and spread. Every root was aimed
   against the tool's own C1–C5 checks, which rejected 12 of the first 24.
3. **Naturalize.** One 0.30 SDXL inpaint per composite on the box
   (`derive_sapling_lora_naturalize_0821.py`, 26 specs, seed 20260820).
   **26 of 26 returned, 0 failed, 26 of 26 passed the D bars** — two leaves, no
   figure, background intact, blades visibly shaded rather than the flat drawn
   shapes the init handed over.

**The one axis the set does NOT cover is leaf count: every frame has two.**
`beat16_sapling_composite.py` draws the canon two, `leaf_count_composite.py`
only *removes* leaves from a plate that has too many, and inventing a third
would break canon `sapling-two-leaves` to satisfy a dataset axis. The leaf-count
token is explicit in every caption — which is the mechanism that keeps it out of
the trigger — but its value is constant in v1. **A v2 that serves 004 and later
needs a tool that can draw three, five and six leaves, and that tool does not
exist.** Height is captioned as the *story* height and framing as the *camera*,
kept as separate tokens so the set cannot teach that camera distance is growth.

## Next rungs, named and not fired

1. **Run SETUP.md on the box** (~3–4 GB of download, no GPU needed, can run
   while the card is busy), then file `train-jerry-0820.yaml --backlog`.
2. **A variety batch for Jerry**, ~30 GPU-minutes. All 31 frames are crouched or
   seated in a sunny field; there is one true close-up and no standing figure,
   no back view, no night. Bar B5 in the training spec is designed to expose
   exactly this, and if it fails, this is the fix.
3. ~~**The sapling composite dataset**~~ — DONE 2026-08-21, see State. What is
   left of this rung is the **training spec**, which is not written: there is no
   `train-sapling-0821.yaml`, and writing one before SETUP.md exists on the box
   would be filing against an installer that has never run. It waits behind
   rung 1, not behind the dataset.
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
