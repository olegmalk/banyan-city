# Character LoRAs for the recurring cast

Enabler #1 for the founder's **one day per episode from ep3 on** bar
(`STATE.md`, 2026-08-20): move character identity out of the prompt and into the
weights, so it stops being re-fought per frame.

**THE SAPLING LoRA IS TRAINED AND MEASURED (2026-08-22).** $0 spent, still — one
card-hour on an idle box, no provider. Jerry is not trained; his spec is re-held
on the age pivot.

**Verdict in one line: the trigger DRAWS the canon two-leaf sapling — the object
five closed wording ladders never produced — at 14/15 on the committed count
ruler, and three of five bars still fail.** All three failures trace to the two
monocultures this file named before training: every frame is figure-free, and
every frame stands on grass. Full scoring with pixels:
**`review/ep3-sapling-lora-0822/SHIP-0822.md`**. Where the weights live and what
weight is sanctioned (none, and the ladder says why):
**`registry.yaml`**.

| file | what it is |
|---|---|
| `../research/character-lora-sdxl-0820.md` | UNIT 1 — the external research, with sources. Read this first; everything below is downstream of it |
| `dataset-jerry.yaml` | UNIT 2 — the curation. 31 includes and 20 rejects, each with a reason |
| `build_dataset.py` | UNIT 2 — turns the curation into captions + a sha-addressed manifest. `--check` re-verifies |
| `captions/jerry/*.txt` | UNIT 2 — 31 generated captions |
| `manifest-jerry.yaml` | UNIT 2 — generated. Paths, shas, captions, tiers |
| `SETUP.md` | UNIT 3 — the one-time trainer install on the box. **Ran end to end 2026-08-20; no longer a blocker** |
| `train-jerry-0820.yaml` | UNIT 3 — Jerry's training job + bars. **Re-held on the age pivot, never run.** Also carries the `min_bucket_reso 1024` defect below and would die on it |
| `manifest-sapling.yaml` | UNIT 2 — the sapling dataset. 44 frames, 17 plates, all SDXL-provenanced |
| `captions/sapling-0821/*.txt` | UNIT 2 — 44 captions. Leaf count and story height stay EXPLICIT, so they cannot fuse into the trigger |
| `train-sapling-0822.yaml` | UNIT 3 — **the run that happened.** Recipe, the item-18 scope gate in code, and the pre-registered bars |
| `sample-sapling-0822.yaml` | UNIT 3 — the samples, re-filed after the peft failure. Does not re-train |
| `bars-sapling-0822.yaml` + `run_grid.py` | UNIT 4 — the 15-cell bar grid and the recorded-not-graded leaf-count probe |
| `ladder-sapling-0822.yaml` + `run_ladder.py` | UNIT 4 — the LoRA-weight ladder. **It runs backwards; see the verdict** |
| `registry.yaml` | UNIT 5 — where trained weights live, their sha256s, and what weight is sanctioned |
| `sample_lora.py` | UNIT 3 — draws one frame from a trained LoRA in the render venv. **Refuses up front without a PEFT backend** |

## Three things that cost time, so they cannot cost it twice

1. **`--min_bucket_reso 1024` against an 832 short side is an instant abort.**
   sd-scripts asserts `min(resolution) >= min_bucket_reso`. Research §5's memory
   line is the standard 1024² SDXL config, where it passes by coincidence; for
   our 9:16 plates the min must be 832. **`train-jerry-0820.yaml` still has the
   1024 and would die the same way.**
2. **A LoRA sample needs `peft` and neither venv had it.** diffusers 0.29.2 gates
   all LoRA loading behind `USE_PEFT_BACKEND`. Install it
   **`--no-deps`** — a bare install can resolve torch away from 2.11.0+cu128 and
   break every render on the box.
3. **A rank-32 SDXL checkpoint is 228 MB, not the ~35 MB research §5 says.**
   Never publish weights to `farm-out/`: GitHub hard-rejects blobs over 100 MiB
   and the courier commits before it pushes, so one of them stops **every** lane's
   results reaching the tree. Three `.gitignore` guards now block it.

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

**BUILT 2026-08-21 — `manifest-sapling.yaml`. v1 was 26 frames over 11 plates;
v3 is 44 FRAMES OVER 17 PLATES, with the lighting ratio moved from 26 daylit : 0
non-daylit to 26 : 18.** Gate cleared on scale and scenes, NOT on leaf count. The
three build steps below describe v1 and their counts are v1's; v2 added the
lighting axis and v3 added the rule for asking for it (see the header of
`manifest-sapling.yaml`). Purpose-built rather than harvested, all $0:

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

Reordered 2026-08-22 by what the sapling run measured. Cheapest first; none of
1–4 needs the founder awake.

1. **A FIGURE BATCH FOR THE SAPLING, ~40 GPU-minutes. The one that matters.**
   Composite the canon sapling onto plates that CONTAIN A GOBLIN. All 44 frames
   are figure-free and the LoRA learned it: asked for a goblin beside the plant
   it drew none twice and a creature with the plant FUSED INTO ITS BODY once,
   and in the no-regression pair it DELETED a figure from a prompt it was not
   invited to. Three of five bars fail on this single gap, and ep3's entire
   on-screen cast is these two characters — a sapling LoRA that erases the other
   half of the cast cannot serve the episode it was built for.
2. **A NON-GRASS GROUND BATCH, ~20 GPU-minutes.** Tilled earth, stone, sand,
   snow, floorboards. Measured: ground COLOUR generalises (brown dry grass 3/3)
   and ground MATERIAL does not (bare tilled earth 1/3).
3. **Grade the earlier sapling epochs, ~15 GPU-minutes each.** Epochs 2/4/6/8
   are on the box unexamined. The fusion defect is what overfitting to "plant
   alone" looks like, so an earlier checkpoint may hold the sapling with less of
   it. Their sha256s are in `registry.yaml`.
4. **THE LEAF-COUNT COMPOSITOR — now urgent, not merely named.** The probe asked
   the trained LoRA for four leaves and it drew two: the count is fused into the
   trigger and is not promptable. Canon rises 2 → 6 leaves by 006a, so this gates
   every episode after 003b. A tool that can draw three, five and six blades
   still does not exist.
5. **The plate-step loader, deliberately NOT written.** `render_wave_sample.py`,
   `still_local.py` and `controlnet_plate.py` contain no LoRA code; the change is
   ~8 lines at `render_wave_sample.py:236` plus the sidecar fields. No work
   without a consumer, and the consumer for a loader is a LoRA that passed.
6. **Jerry.** His spec is re-held on the 2026-08-21 age pivot and its dataset is
   the wrong age; the gate is a founder ruling on `/review/ep2-goblin-age-0821`.
   When it is refiled, **fix `min_bucket_reso` first** — it is 1024 against an
   832 short side and aborts before the first weight loads.
7. **A variety batch for Jerry**, ~30 GPU-minutes, behind rung 6. All frames are
   crouched or seated in a sunny field; no standing figure, no back view, no
   night.
8. **Two open R4 questions for the founder, with pixels** — both surfaced by
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
