# Approved stills — the exact pixels the motion stage animates

Each PNG here was **approved by the founder** (2026-07-27, stills review rounds,
kernel v43+) and is canonical: the Kaggle notebook uses a committed still instead
of redrawing the beat, so what was approved is what gets animated (SVD is
image-to-video — the still IS the shot). Kaggle has no persistent disk; the repo
is the resume mechanism, same as clips/.

Provenance: drawn by cagliostrolab/animagine-xl-3.1 from the beat's shots.md
prompt (see git history for the exact prompt at approval time), steps 40, cfg 7.5,
seed 20260719+beat.

To REVOKE an approval: rename the PNG to `NN-<slug>-REVOKED-<why>.png` (git records
it, R6 keeps history). The renderers skip any name containing `REVOKED`
(`video_task.py:1182`, `:1295`, `:1359`), so a revoked frame stays readable as
evidence without ever being animated again. Deleting works too and is what this file
used to say; renaming is better, and it is what beats 3, 7, 10, 12, 14 and 15 do.

## 12-undefined.png — picked 2026-08-08, and the only pick of that wave

The founder screened the forty replacement candidates rendered on 2026-08-07 and
picked exactly one: **`b12-r2-s1`** for beat 12. That is R4, it is recorded verbatim
with the reservation he attached to it in `shots.md` under **Beat 12**, and it is the
frame every renderer now reads for this beat.

| | |
|---|---|
| promoted from | `takes/stills/12-undefined-r2-s1.png`, copied byte-for-byte |
| sha256 | `5bf2f645215e4fa10b47eb1e9f189edbf8775d056162791db410556b84913d87` |
| size | 832 × 1216 |
| model | `cagliostrolab/animagine-xl-3.1` — the house still model |
| prompt | round 2, the fenced block under **Beat 12** in `shots.md`, unchanged |
| seed | 20261731 — **recorded, not derived**: round 2 wrote a real sidecar at render time (`takes/stills/12-undefined-r2-s1.png.meta.yaml`, task `ep1-stills-round2-1786129764`), which round 1 did not and had to be reconstructed from `wave.log` |
| steps / guidance | 40 / 7.5, 39s wall on the rtx5090 |
| cost | $0 — local CUDA, no provider |

**It replaces a frame he refused, and that frame is kept.** The 2026-07-27 approval
for this beat is now `12-undefined-REVOKED-cracked-grey.png` — the dark place with
the dry cracked grey floor he named on 2026-08-07. It is the record of what was
refused and the reason the round-2 prompt reads the way it does.

**The reservation he picked it with, and it is not a defect to fix quietly:** *"not
sure what it's supposed to be."* The pick stands and nothing re-renders on it; the
full reading is in `shots.md`, because a note like that belongs beside the direction
it questions and not only beside the pixels.

**No sidecar here, on purpose** — the same reason 002b's `stills/README.md` gives. A
`.meta.yaml` naming `cagliostrolab/animagine-xl-3.1` beside a canon still would be
scored by `licence_gate` as a new CreativeML Open RAIL++-M finding (D15, open, the
founder's to settle) and would fail CI's ratchet. The provenance lives in this file,
in the take's own sidecar under `takes/`, and in git.
