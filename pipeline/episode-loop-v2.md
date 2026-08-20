# The episode loop, v2 — founder-defined 2026-08-20

Verbatim intent (founder): "setup character consistency, then for each beat,
make the reference image, remake it a few times to make sure its right, make
the clip, remake a few times, then do all the voices and captions afterwards
... shouldn't take so long."

## Step 0 — once per show, not per beat
Character LoRA(s) for the recurring cast + locked design sheet. No beat
renders until identity is a solved input. (Jerry LoRA: in training. Sapling:
composite-first until its LoRA gate is met.)

## Per beat (target: <30 min)
1. PLATE: render 4-8 candidates in one batch (seeds/variants). Pick BY EYE at
   a contact sheet. Remake the batch at most twice. No essays.
2. CLIP: i2v from the picked plate, 4-8 seeds in one batch. Pick by eye.
   Remake at most twice.
3. If two batch rounds fail the same way → the BEAT is wrong for the engine:
   restage the action (steward drafts, founder picks), don't grind the axis.

## After all beats
Voices + captions in one pass (they are stable; render_t3 muxes). Assemble,
watch, ship.

## Evaluation rules
- Eyes first. Instruments exist ONLY for canon gates (identity, licence,
  publish QA) — never per-beat aesthetics.
- Measured laws (prompt-summons, placement>negatives, crf-conditioning,
  composite-first for undrawable objects) are INPUTS to wording, not
  per-beat research to re-run.
- A failed batch gets ONE line in the ladder, not a verdict document.
