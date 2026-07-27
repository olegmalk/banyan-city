# The Machine — how banyan.city operates, end to end

One page, the whole loop. Everything below is enforced by code in `pipeline/`
or recorded in the tree; nothing depends on anyone's memory.

## The lifecycle of an episode

1. **Script (T0).** A node is born under `genomes/<tree>/nodes/` with a script
   of 15–25 filmable beats ([SCRIPT-SPEC.md](SCRIPT-SPEC.md)). Anyone may draft;
   model-written text says so in its Provenance section.
2. **Founder approval.** No voice, footage, or assembly is made from a script
   the founder has not read and approved (STEWARDSHIP §6 — enforced by the
   render tools themselves, which refuse unapproved nodes).
3. **Stills.** Each beat gets one frame, drawn from the exact recipe on the
   node's **shot board** (`<node>-shots.html`). The founder verdicts every
   frame; approved pixels are committed to `nodes/<node>/stills/` and become
   canonical — the motion stage animates *those pixels*, never a redraw.
4. **Motion takes.** Approved stills are animated — by the free pipeline, or by
   **anyone** using the board's recipe with their own tools and credits (D11).
   Every take lands in `takes/` with full provenance (§7.2) and plays on the
   board. Competing takes are the point.
5. **Assembly (T3).** Approved clips + the measured voice track become the
   episode (`render_t3.py`), pass the QA gate (`qa_episode.py`), and the
   founder screens the cut. Taste verdicts are always the founder's (R4).
6. **Publish.** The episode becomes a leaf; the site (this site — rebuilt from
   git on every push) shows it; the founder posts it to distribution.
7. **Reactions.** Every node has ONE GitHub issue — its 💧 reaction inbox —
   opened at the node's birth and **kept open for the node's whole life**. It
   is a mailbox, not a task: "open for 18 days" is its normal, healthy state.
   Reactions become sap; sap decides which branches grow next.
8. **Branch.** Cliffhangers fork; competing continuations coexist; material
   support (reactions, watering) — not votes — decides what the tree grows.

## The crowd rails (D11)

- **Fork a beat:** the shot board publishes every beat's complete recipe —
  still, prompts, model, seed, settings. Generate a better take with your own
  credits, submit it with provenance ([WATERING.md](WATERING.md), compute as
  watering).
- **Fork a prompt:** prompts are text in `shots.md`; a PR is a pitch.
- **Re-render an episode:** [REGROW.md](REGROW.md) is the walkthrough.
- **Fund a render:** [WATERING.md](WATERING.md); split per D5, ledgered.

## What is enforced by code

- `lint_genome.py` — structural honesty (CI on every push)
- `test_pipeline.py` — the render logic's regression suite (CI)
- STEWARDSHIP §6 approval gate — render tools refuse unapproved narrative
- `budget.yaml` + spend ledger — paid renders are founder-authorized, capped,
  and logged; the default path is $0
- Provenance sidecars (§7.2) — every artifact names its model, prompt, cost

## Where things live

| What | Where |
|---|---|
| The promise & guidelines | [PROMISE.md](PROMISE.md), rendered at [/city](city.html) |
| Scripts, stills, takes, leaves | `genomes/<tree>/nodes/<node>/` |
| Shot boards | `<node>-shots.html` per node, linked from every card |
| Decisions (open & resolved) | [DECISIONS.md](DECISIONS.md) |
| The quality loop & its history | `pipeline/loop.md`, `pipeline/loop/cycle-*.md` |
| Reactions | one GitHub issue per node (💧 on every card) |
| Money & compute ledgers | `ledger/` |
