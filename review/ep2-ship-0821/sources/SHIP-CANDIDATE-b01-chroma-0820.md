# SHIP-CANDIDATE — beat 01, `01-cold-open-COMP-chroma-s20260840.mp4`

**An additive note from the beat-01 composite lane. It edits nothing the ship lane
owns.** The ship lane already holds its own copy of this clip; this file is the
provenance and the verdict behind it, so the assembly does not have to go looking.

    sha256   12e256fd35f1b10119da67909bfa3fb0d15f1be44b1323c73f47e174af501e28
    landed   2026-08-20, evening — inside the 12:00 2026-08-21 ship cutoff
    job      pipeline/jobs/ep2-b01-figcomp-heldfield-0820.yaml
    verdict  verdict_chromaticity_rung_0820 / _measured / verdict_cut_swapped_0820
    also in  review/ep2-demo-0820 revision d (cut sha 173179f4…c16a0), qa_local PASS

## What it is

A **composite, not a render.** No sampler ran for it: $0, zero GPU seconds. The
**fig** is `ep2-b01-fignonly-s20260840-0820`'s fig, frame for frame. The **field**
is `ep2-b01-figcrf10-s20260840-0820`'s field, frame for frame, everywhere outside a
feathered matte taken from `fig_track.py`'s own per-frame masks. Same seed, same
init, same prompts on both ingredients — one argv value apart. Both are named with
their shas in the clip's sidecar and the licence gate walks that list.

## Why it is the candidate

It **replaced** `01-cold-open-LTX-fignonly-s20260840.mp4` in the review cut on the
evening of 08-20. Both takes score **7 of 8** scored clauses and both fail only
**G5a**. The difference is which seven:

| | fignonly (out) | this clip (in) |
|---|---|---|
| G5a bands failed | 3 of 4 | **1 of 4** (grass floor 0.062 / 0.20) |
| shaft / sapling NCC | −0.324 / 0.055 | **0.982 / 0.734** |
| luma delta at peak | +10.85 | **+0.93** |
| worst consecutive NCC | 0.9403 | **0.9966** |
| G1 | 121/121, f108 | 121/121, f108 |
| G1 identical across 6 encodes | no | **yes** |

G1 was verified across PNG and libx264 crf 0, 10, 14, 18 and 23 — all six rows
121/121 live, empty dead list, 90 % of growth at f108. That test was written into
the spec before the build existed, and it is why no encode was chosen to get an
answer.

## The fault it ships with, named

**G5a fails on the grass floor, 0.062 against a 0.20 bar**, inherited whole from the
held plate. On that plate the grass band's consecutive-frame NCC is 0.9950 and its
decay is monotonic — a foreground that *sweeps*, not one being re-inked — but the
clause is a two-point test and cannot tell those apart. That is filed as a bar
defect for a ruling; it was **not** used to re-score this clip.

**And the cost that was paid for the pass:** the per-channel colour match moved the
fig's end state from hue 293.9 to **305.2**. Still inside the 270–320 clause, but
10.8° of a 12.0° bound that was written down first.

## What is R4 and not settled

The take this replaced is the **more dramatic** picture — its whole sapling grows,
two big leaves sweep the top third by f120. This one is a locked-off plate where
only the fig moves, which is what the cold-open line asks for and what G5a enforces.
The written standard picks this one. **The founder has screened neither.** Both are
side by side at
`farm-out/ep2-b01-figcomp-heldfield-0820/evidence/COMP-SWAP-chroma-vs-incut.jpg`.

**Veto is one line — "beat 01: put fignonly back."** The outgoing clip is committed
at `farm-out/ep2-b01-fignonly-s20260840-0820/` with its sidecar and sha256 manifest.
