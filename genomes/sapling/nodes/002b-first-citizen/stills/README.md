# Approved stills — the exact pixels the motion stage animates

Same contract as 001's `stills/`: every PNG here was **picked by the founder**
(R4) and is canon. The renderers read this directory and not `takes/` —
`video_task` globs `stills/NN-*.png` for its conditioning frame, `render_local`
and `generate_shots --from-stills` resolve `stills/NN-<slug>.png` by name, and
`build_status` calls a beat *final* when that exact file exists. So the file
name is not decoration: it is `NN-<slug>.png` with the slug `shots.md` gives
the beat (`parse_shots`), which for beat 01 is `cold-open`.

To REVOKE a pick: delete the PNG (git records it, R6 keeps the history), the
way 001 carries its `-REVOKED-` frames.

## 01-cold-open.png — picked 2026-08-07

The founder, asked to choose among the beat-01 candidates, answered:
**"r3-s3 and retire"**. That is R4 and it settles two things at once — the
frame, and the dialect condition the script's approval was written around
(`leaves/002b-t0-c.yaml` `approval_scope`: *"beats 02-21 await his verdict on
that sample before conversion"*). The sample is settled, so beats 02-21 are
sanctioned.

| | |
|---|---|
| promoted from | `takes/stills/01-cold-open-r3-s3.png`, copied byte-for-byte |
| sha256 | `7cc22aa124229385b55e1e9ab68f403e6bb8b13bf781979f021751a4bcab3557` |
| size | 832 × 1216 |
| model | `cagliostrolab/animagine-xl-3.1` — the house still model |
| prompt | round 3, the fenced block under **Beat 01** in `shots.md`, unchanged |
| seed | 20263720 — **derived, not recorded**: `still_local.py:140` seeds `SEED + beat + i*1000` with `SEED = 20260719`, and `s3` is the fourth variant. The stills path writes no sidecar at all (`farm_worker.py:430`, traced in `8d7ceed`), so nothing beside the pixels says this; it is arithmetic on the file name |
| cost | $0 — local MPS/CUDA, no provider |

**The accepted flaw, written down because it was accepted and not fixed.** The
plant carries **four leaves**; the character has two. Four wordings were spent
on that count (`a single pair of oversized leaves`, `exactly two oversized
cotyledon leaves`, `sprout with only two oversized leaves`) and the table in
`shots.md` records what each drew — the best of them got three leaves once, in
one of four seeds, and lost the composition in the other three. This is a
limitation of the model, not an unfinished prompt, and the founder picked the
frame with it in view. Do not spend a fifth round on synonyms for "two": the
levers left are img2img over this plate, a pose controlnet, or a different
checkpoint, and none of them is a prompt.

**The frame is also the START of a motion, deliberately.** The script's
condition is that the fig *grows* on screen rather than already hanging. A 0.35
img2img repaint of this exact plate comes back with a larger, rounder fruit —
which is a defect when you ask for a smaller one and a ready-made end frame
when you ask for a swelling one. `takes/stills/01-cold-open-i2i-r3s3-*.png` are
those repaints, kept as candidates for the end of the move.

**No sidecar here, on purpose.** 001's stills carry none either. A
`.meta.yaml` naming `cagliostrolab/animagine-xl-3.1` would be scored by
`licence_gate` as a new CreativeML Open RAIL++-M violation (D15, open, the
founder's to settle) and would fail CI's ratchet — so the provenance lives in
this file and in git, exactly as it does for episode 1.
