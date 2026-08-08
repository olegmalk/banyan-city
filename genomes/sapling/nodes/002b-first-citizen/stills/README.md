# Approved stills — the exact pixels the motion stage animates

Same contract as 001's `stills/`: every PNG here was **picked by the founder**
(R4) and is canon. The renderers read this directory and not `takes/` —
`video_task` globs `stills/NN-*.png` for its conditioning frame, `render_local`
and `generate_shots --from-stills` resolve `stills/NN-<slug>.png` by name, and
`build_status` calls a beat *final* when that exact file exists. So the file
name is not decoration: it is `NN-<slug>.png` with the slug `shots.md` gives
the beat (`parse_shots`), which for beat 01 is `cold-open`.

**AS OF 2026-08-08 THIS DIRECTORY HOLDS NO CANON. Episode 2 has no approved
frame for any of its 21 beats.** Beat 01's was revoked by the founder (below);
beats 02-21 never had one — their candidates are in `takes/stills/` awaiting the
redraw queued as `ep2-stills-redraw-b02-21`.

## How to revoke a pick — rename it, do not delete it

**Rename in place** to `NN-<slug>-REVOKED-<why>.png`, the way 001 carries its
seven revoked frames. The renderers skip any filename containing `REVOKED`, and
that is code and not etiquette: `video_task.py:1307`, `:1432`, `:1500`,
`hold_still.approved_still`, `bench_models.py:88` and `check_sync.py:169` each
filter the substring out of the glob, so a renamed frame is invisible to every
path that could film it while staying open in the directory it was refused in.

An earlier version of this file said to *delete* the PNG. That was wrong on two
counts and is corrected here: deleting destroys the evidence of what the founder
refused (R6 keeps takes for exactly that reason), and `git` preserving a blob is
not the same as a reader being able to see the thing without archaeology.

## 01-cold-open.png — REVOKED 2026-08-08, and it is now `01-cold-open-REVOKED-too-tall.png`

**The founder's words, in full and unedited** (2026-08-08, in a message whose
other two sentences answered other questions):

> you are still using the bad beat 14 frame, no. for the wan or ltx decision,
> neither. **you used a frame i never approved, and its tooooo tall.**

**HE IS WITHDRAWING THE PICK, NOT REPORTING A NEW FAULT IN IT.** *"a frame i
never approved"* is about how the choice was taken, not about the pixels: the
sheet he chose `r3-s3` from on 2026-08-07 carried a steward-hand
**`<- BEST PLATE`** annotation next to that candidate. That is already on the
record as a process foul — a pick sheet that names a favourite is not a pick
sheet, and R4 says taste belongs to the author. So the 2026-08-07 verdict is not
being defended as "he did approve it really". It is withdrawn, and beat 01 is
back where it was before the sheet existed.

**"tooooo tall" READS AS THE PLANT, and the picture is what says so.** The word
could in principle have meant the frame's shape, and it does not: the file is
832x1216, aspect **0.684**, which is *wider* than the 9:16 (0.5625) the show
ships in — nothing about the file is tall. The plant is. Measured off the plate
rather than eyeballed: the stem is a **1-3 pixel hairline** that stands **385px,
32% of the frame's height**, with its apex at **y=315 — 25.9% from the top**, so
the tip reaches into the upper quarter of the shot and the fruit is silhouetted
against sky. The prompt asked for *"a tiny 40cm banyan seedling … whole plant in
frame"*; what got drawn is a tall spindly weed. Both halves of his sentence point
at the same object.

**THIS IS THE SAME WORD THE REDRAW WAVES ARE BEING RUN ON, AND THAT MATTERS
MORE THAN THIS BEAT.** His 2026-08-08 character ruling is *"just make it tall in
each clip of it"*, and episode 1's four remaining redraws plus episode 2's twenty
are drawing now on that rule with `tall tree` removed from the scale negatives.
A frame he calls *too* tall is therefore a **ceiling on the rule, discovered on
the same day the rule was set** — "reads tall" is a slender vertical that owns
the height of the shot, and this plate is past it. Nothing is being changed in
those waves on this reading (their outputs are R4 and unscreened), but their
contact sheets will be judged against it and the record says so in advance
rather than after.

**What is true now:** beat 01 has **no canon still**, `hold_still` and
`video_task` both resolve `None` for it (verified by call, not by reading the
filter), and the board reads **0/21 frames approved** where it read 1/21. The
redraw is queued as `ep2-b01-cold-open-redraw` — four candidates, one labelled
sheet, no favourite marked on it.

### The revoked file's own provenance, kept because the file is kept

| | |
|---|---|
| promoted from | `takes/stills/01-cold-open-r3-s3.png`, copied byte-for-byte, 2026-08-07 |
| sha256 | `7cc22aa124229385b55e1e9ab68f403e6bb8b13bf781979f021751a4bcab3557` |
| size | 832 × 1216 |
| model | `cagliostrolab/animagine-xl-3.1` — the house still model |
| prompt | round 3, the fenced block under **Beat 01** in `shots.md`, unchanged |
| seed | 20263720 — **derived, not recorded**: `still_local.py:140` seeds `SEED + beat + i*1000` with `SEED = 20260719`, and `s3` is the fourth variant. The stills path writes no sidecar at all (`farm_worker.py:430`, traced in `8d7ceed`), so nothing beside the pixels says this; it is arithmetic on the file name |
| cost | $0 — local MPS/CUDA, no provider |
| filmed twice | `review/ep2-b01/` — Wan TI2V-5B and LTX-2.3, then both re-rendered on the aspect-correct plate. Those four clips and their sidecars still name this still; they are **not** being rewritten, because they record what was actually filmed |

**The flaw that was known and accepted at pick time, and is not what he
revoked it for.** The plant carries **four leaves**; the character has two. Four
wordings were spent on that count and the table in `shots.md` records what each
drew. That was argued down as a model limitation and the pick was made in view of
it. His revocation says nothing about leaves — and *"dont overthink the leafs on
it"* (2026-08-08) says the count is explicitly not to be chased in the redraw.

**No sidecar here, on purpose.** 001's stills carry none either. A
`.meta.yaml` naming `cagliostrolab/animagine-xl-3.1` would be scored by
`licence_gate` as a new CreativeML Open RAIL++-M violation (D15, open, the
founder's to settle) and would fail CI's ratchet — so the provenance lives in
this file and in git, exactly as it does for episode 1.
