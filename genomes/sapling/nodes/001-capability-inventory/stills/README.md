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
used to say; renaming is better, and it is what beats 3, 7, 8, 9, 10, 12, 14 and 15 do.

## 07 / 08 / 09 — the progression, picked 2026-08-08 (item 03)

The founder answered checklist item 03 with three addresses and nothing else, verbatim:
**"po7-r1-s2, po8-r2-s0, po9-r1-s2"** — his own shorthand for the `p07`/`p08`/`p09`
grammar, normalised and resolved through `REVIEW-KEY-0808.md`, the pixel-matched
address map, not by grid position. That is R4. The reading of each pick, and the
directions they endorse, are in `shots.md` under **Beat 07**, **Beat 08** and
**Beat 09**.

| | beat 07 — WIDE | beat 08 — MEDIUM | beat 09 — CLOSE |
|---|---|---|---|
| label | `p07-r1-s2` | `p08-r2-s0` | `p09-r1-s2` |
| promoted from | `takes/stills/07-zero-0-moving-parts-prog-s2.png` | `takes/stills/08-sev-1-prog2-t0.png` | `takes/stills/09-whoami-prog-s2.png` |
| copied | byte-for-byte | byte-for-byte | byte-for-byte |
| sha256 | `76e4d81fa108654d7575224f6495c8c5932f7e57d49c57d6c458fc3db39e4282` | `e886758c3a344c87450304f50746ce825b38cf1ef9f765fde0db4212855115b2` | `16ec0b49e04e540681b857d75b5db466f15f0cdeb30705707bb1a5afa50f5f66` |
| size | 832 × 1216 | 832 × 1216 | 832 × 1216 |
| model | `cagliostrolab/animagine-xl-3.1` | same | same |
| round | **1** (`candidate_set: prog`) | **2** (`candidate_set: prog2`) | **1** (`candidate_set: prog`) |
| seed | **20262726** | **20260726** | **20262728** |
| task | `ep1-stills-rework-1786124640` | `ep1-stills-round2-1786129764` | `ep1-stills-rework-1786124640` |
| steps / guidance | 40 / 7.5 | 40 / 7.5 | 40 / 7.5 |
| wall | 9s, rtx5090 | 39s, rtx5090 | 9s, rtx5090 |
| prompt | the fenced block under **Beat 07** in `shots.md` | the fenced block under **Beat 08** in `shots.md` — the round-2 text, NOT `shots-alt-789.md`'s | the fenced block under **Beat 09** in `shots.md` |
| cost | $0 — local CUDA, no provider | $0 | $0 |
| replaces | `07-zero-0-moving-parts-REVOKED-grayened.png` | `08-sev-1-REVOKED-same-picture.png` | `09-whoami-REVOKED-same-picture.png` |

**Every seed above is read out of that PNG's own `.meta.yaml` sidecar under `takes/`,
not off a sheet caption.** Round 1's sidecars were reconstructed from `wave.log` on
2026-08-07 and say so in their own header comments; round 2 wrote itself at render
time.

**The three frames they replace are kept, and their names say why he refused them.**
Beat 7's is `-REVOKED-grayened` — his word, from v32: *"beat 7 makes everything look
grayened … the main problem is that it drastically changes the style."* Beats 8 and 9
are `-REVOKED-same-picture`, the other half of the same list: *"beat 7, 8, 9 are
basically the same picture."* Beat 7 was on both halves, and **the wide he picked
answers both** — that dual duty was written into item 03's copy before he read it, so
the palette complaint is closed by this pick rather than left hanging.

**THE ONE CAVEAT ON THE RECORD: THE PICKS MIX ROUNDS.** Wide and close are round 1;
the medium is round 2. Round 1's one documented flaw was **colour drift across the
trio** — that is the entire reason round 2 was rendered, and round 2 removed it by
using a byte-identical palette block, a byte-identical negative and **one shared seed
(20260726) across all three shots**, with the lens as the only variable. Two of the
three canon frames now come from outside that lock: three different seeds, and beat
09's negative is a different string from the other two. **The combination is his call**
— he picked per beat with the three sheets side by side, and mixing rounds was stated
as a legal answer in the copy he answered from. **But the drift risk transfers to the
assembled cut and is judged at the v33 screening, not here.** If 7→8→9 reads as three
colour temperatures rather than one camera moving in, re-rendering a single beat on the
palette-locked block costs 39 seconds at $0 and the round-2 wide and close already
exist. Nothing re-renders before he has seen them cut together.

**No sidecars beside these three either**, for the reason spelled out at the foot of
this file: a `.meta.yaml` naming `cagliostrolab/animagine-xl-3.1` next to a canon still
scores as a new CreativeML Open RAIL++-M finding and would push CI's licence ratchet
past 25. The provenance is this table, the takes' own sidecars, and git.

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
