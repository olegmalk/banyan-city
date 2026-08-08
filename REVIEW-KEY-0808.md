# Review key — 2026-08-08 candidate frame addresses

Every candidate frame on the `LABELED-WAVE-0807-*.png` sheets carries a burned-in
amber badge. Type the badge text; this file resolves it to exactly one PNG.

**Say the label, nothing else** — `b06-r1-s3`, or just `b06-s3` if the beat has only
one round. The implementing agent resolves it here and never guesses.

## Label grammar

```
b<beat>-r<round>-s<slot>    a redraw-fix candidate      (checklist item 02)
p<beat>-r<round>-s<slot>    a progression candidate     (checklist item 03)
```

**`b` and `p` are not interchangeable and this is the one trap in the set.**
Beats 7, 8 and 9 were drawn twice for two different purposes: once as ordinary
per-beat fixes (`b07-*`) and again as the wide/medium/close progression (`p07-*`,
`p08-*`, `p09-*`). For beat 7 the two sets even share seeds, so seed alone does not
identify a frame. The sheets' own captions already make this split — they read
`beat 07 [fix]` and `beat 07 [prog]`; `b`/`p` is that same distinction, shortened.

Rounds: **r1** = the first wave, **r2** = the re-render that supersedes it. A beat with
no r2 row has only ever had one round. Slots are the four seeds of a batch, `s0`–`s3`,
left-to-right then top-to-bottom on every sheet. The round-2 progression frames are
single-seed, so they are `s0` only (their file is named `-prog2-t0.png`).

## How these labels were derived

Not from grid position. Every tile on every sheet was cut out and pixel-matched
against all 72 source stills; each of the 88 tiles matched exactly one file
(mean per-channel distance < 0.07 on a 16x24 fingerprint, nearest rival far behind).
Seeds come from each PNG's `.meta.yaml` sidecar, not from the captions drawn on the
sheets. This file and the burned badges are generated from that one verified map.

All source paths below are relative to the repo root, under `genomes/sapling/nodes/001-capability-inventory/takes/stills/`.

## `b03-*` — checklist item 02

Beat 3 — indoors, domestic. **r3 is the live set** (drawn 2026-08-08 on his
close-up direction after he rejected all eight of r1+r2 the same day); r1 drew
gibberish glyphs on the screens (a bug in ours, since fixed).

| label | source PNG | seed | on sheets |
|---|---|---|---|
| **`b03-r1-s0`** | `03-deploy-succeeded-fix-s0.png` | 20260722 | `beat03-fix`, `beat03-r2`, `overview` |
| **`b03-r1-s1`** | `03-deploy-succeeded-fix-s1.png` | 20261722 | `beat03-fix`, `beat03-r2` |
| **`b03-r1-s2`** | `03-deploy-succeeded-fix-s2.png` | 20262722 | `beat03-fix`, `beat03-r2` |
| **`b03-r1-s3`** | `03-deploy-succeeded-fix-s3.png` | 20263722 | `beat03-fix`, `beat03-r2` |
| **`b03-r2-s0`** | `03-deploy-succeeded-r2-s0.png` | 20260722 | `beat03-r2`, `beat03-r3` |
| **`b03-r2-s1`** | `03-deploy-succeeded-r2-s1.png` | 20261722 | `beat03-r2`, `beat03-r3` |
| **`b03-r2-s2`** | `03-deploy-succeeded-r2-s2.png` | 20262722 | `beat03-r2`, `beat03-r3` |
| **`b03-r2-s3`** | `03-deploy-succeeded-r2-s3.png` | 20263722 | `beat03-r2`, `beat03-r3` |
| **`b03-r3-s0`** | `03-deploy-succeeded-r3-s0.png` | 20260722 | `beat03-r3` |
| **`b03-r3-s1`** | `03-deploy-succeeded-r3-s1.png` | 20261722 | `beat03-r3` |
| **`b03-r3-s2`** | `03-deploy-succeeded-r3-s2.png` | 20262722 | `beat03-r3` |
| **`b03-r3-s3`** | `03-deploy-succeeded-r3-s3.png` | 20263722 | `beat03-r3` |

The r3 row reuses r1/r2's own seeds, so each `LABELED-beat03-r3.png` column is a
controlled pair — the close-up rewording is the only variable.

## `b06-*` — checklist item 02

Beat 6 — sky only, no leaf. **r3 is the live set** (drawn 2026-08-08). His r1
verdict named NO fault, so the prompt is byte-unchanged and r3 draws the NEXT
four seeds of the beat's own series — **columns on its sheet are NOT controlled
pairs**, and there is no `r2` for this beat (the round-2 tag belongs to beats 3
and 12; same label logic as beat 15's jump to r3).

| label | source PNG | seed | on sheets |
|---|---|---|---|
| **`b06-r1-s0`** | `06-too-blue-fix-s0.png` | 20260725 | `beat06-fix`, `beat06-r3`, `overview` |
| **`b06-r1-s1`** | `06-too-blue-fix-s1.png` | 20261725 | `beat06-fix`, `beat06-r3` |
| **`b06-r1-s2`** | `06-too-blue-fix-s2.png` | 20262725 | `beat06-fix`, `beat06-r3` |
| **`b06-r1-s3`** | `06-too-blue-fix-s3.png` | 20263725 | `beat06-fix`, `beat06-r3` |
| **`b06-r3-s0`** | `06-too-blue-r3-s0.png` | 20264725 | `beat06-r3` |
| **`b06-r3-s1`** | `06-too-blue-r3-s1.png` | 20265725 | `beat06-r3` |
| **`b06-r3-s2`** | `06-too-blue-r3-s2.png` | 20266725 | `beat06-r3` |
| **`b06-r3-s3`** | `06-too-blue-r3-s3.png` | 20267725 | `beat06-r3` |

## `b10-*` — checklist item 02

Beat 10 — at the plant's base, not underwater. **r3 is the live set** (drawn
2026-08-08: roots foregrounded against the delegation, re-lensed to the soil
line so 10 and 14 stop being twins; the tall-sapling recipe).

| label | source PNG | seed | on sheets |
|---|---|---|---|
| **`b10-r1-s0`** | `10-sense-fix-s0.png` | 20260729 | `adjacency`, `beat10-fix`, `beat10-r3`, `overview` |
| **`b10-r1-s1`** | `10-sense-fix-s1.png` | 20261729 | `beat10-fix`, `beat10-r3` |
| **`b10-r1-s2`** | `10-sense-fix-s2.png` | 20262729 | `beat10-fix`, `beat10-r3` |
| **`b10-r1-s3`** | `10-sense-fix-s3.png` | 20263729 | `beat10-fix`, `beat10-r3` |
| **`b10-r3-s0`** | `10-sense-r3-s0.png` | 20260729 | `beat10-r3` |
| **`b10-r3-s1`** | `10-sense-r3-s1.png` | 20261729 | `beat10-r3` |
| **`b10-r3-s2`** | `10-sense-r3-s2.png` | 20262729 | `beat10-r3` |
| **`b10-r3-s3`** | `10-sense-r3-s3.png` | 20263729 | `beat10-r3` |

Same seeds down each column — controlled pairs.

## `b12-*` — checklist item 02

Beat 12 — same fix as 10. **r2 is the live set**; r1 did not carry the strain the script asks for.

| label | source PNG | seed | on sheets |
|---|---|---|---|
| **`b12-r1-s0`** | `12-undefined-fix-s0.png` | 20260731 | `beat12-fix`, `beat12-r2`, `overview` |
| **`b12-r1-s1`** | `12-undefined-fix-s1.png` | 20261731 | `adjacency`, `beat12-fix`, `beat12-r2` |
| **`b12-r1-s2`** | `12-undefined-fix-s2.png` | 20262731 | `beat12-fix`, `beat12-r2` |
| **`b12-r1-s3`** | `12-undefined-fix-s3.png` | 20263731 | `beat12-fix`, `beat12-r2` |
| **`b12-r2-s0`** | `12-undefined-r2-s0.png` | 20260731 | `beat12-r2` |
| **`b12-r2-s1`** | `12-undefined-r2-s1.png` | 20261731 | `beat12-r2` |
| **`b12-r2-s2`** | `12-undefined-r2-s2.png` | 20262731 | `beat12-r2` |
| **`b12-r2-s3`** | `12-undefined-r2-s3.png` | 20263731 | `beat12-r2` |

## `b14-*` — checklist item 02

Beat 14 — roots in soil, warm raking light. **r3 is the live set** (drawn
2026-08-08 against "all too small, not good character consistency": the plant
fills the frame, framing kept — the script's own line).

| label | source PNG | seed | on sheets |
|---|---|---|---|
| **`b14-r1-s0`** | `14-worth-staying-in-fix-s0.png` | 20260733 | `adjacency`, `beat14-fix`, `beat14-r3`, `overview` |
| **`b14-r1-s1`** | `14-worth-staying-in-fix-s1.png` | 20261733 | `beat14-fix`, `beat14-r3` |
| **`b14-r1-s2`** | `14-worth-staying-in-fix-s2.png` | 20262733 | `beat14-fix`, `beat14-r3` |
| **`b14-r1-s3`** | `14-worth-staying-in-fix-s3.png` | 20263733 | `beat14-fix`, `beat14-r3` |
| **`b14-r3-s0`** | `14-worth-staying-in-r3-s0.png` | 20260733 | `beat14-r3` |
| **`b14-r3-s1`** | `14-worth-staying-in-r3-s1.png` | 20261733 | `beat14-r3` |
| **`b14-r3-s2`** | `14-worth-staying-in-r3-s2.png` | 20262733 | `beat14-r3` |
| **`b14-r3-s3`** | `14-worth-staying-in-r3-s3.png` | 20263733 | `beat14-r3` |

Same seeds down each column — controlled pairs.

## `b15-*` — checklist item 02

Beat 15 — surface level, orange glow entering from the right. **Two rounds. `r3` is
the live set, and `b15-r3-s1` is CANON** — he passed it on 2026-08-08 ("b15-r3-s1"),
it was promoted byte-for-byte to `stills/15-something-s-coming.png`, and its pass is
what released beats 3, 6, 10 and 14 to the GPU (their r3 sets are on the four
`LABELED-beat*-r3.png` sheets). There is no `r2` for this beat: the round-2 tag
belongs to beats 3 and 12, and jumping to `r3` keeps a label meaning the same round
everywhere.

| label | source PNG | seed | on sheets |
|---|---|---|---|
| **`b15-r1-s0`** | `15-something-s-coming-fix-s0.png` | 20260734 | `beat15-fix`, `beat15-r3`, `overview` |
| **`b15-r1-s1`** | `15-something-s-coming-fix-s1.png` | 20261734 | `beat15-fix`, `beat15-r3` |
| **`b15-r1-s2`** | `15-something-s-coming-fix-s2.png` | 20262734 | `adjacency`, `beat15-fix`, `beat15-r3` |
| **`b15-r1-s3`** | `15-something-s-coming-fix-s3.png` | 20263734 | `beat15-fix`, `beat15-r3` |
| **`b15-r3-s0`** | `15-something-s-coming-r3-s0.png` | 20260734 | `beat15-r3` |
| **`b15-r3-s1`** | `15-something-s-coming-r3-s1.png` | 20261734 | `beat15-r3` |
| **`b15-r3-s2`** | `15-something-s-coming-r3-s2.png` | 20262734 | `beat15-r3` |
| **`b15-r3-s3`** | `15-something-s-coming-r3-s3.png` | 20263734 | `beat15-r3` |

The r3 row is drawn on r1's own four seeds, so a column of `LABELED-beat15-r3.png` is
a controlled pair: same noise, same model, same 40 steps at cfg 7.5, same 832x1216.
The prompt sentence is the only variable — `a tiny two-leaf sprout standing at ground
level` became `one slender sapling standing tall, its thin stem rising well above the
grass` — plus one term removed from the negative, `tall tree`, which `sd_prompt`
appends for any prompt that says `sapling` and which would have forbidden the thing
the sample exists to test. That removal is in the wave script only; `sd_prompt.py` is
untouched until he rules.

## Beats 7, 8 and 9 — pick from the three per-beat sheets

**Use `LABELED-beat07-all.png`, `LABELED-beat08-all.png`, `LABELED-beat09-all.png`.**
One sheet per beat, that beat's five candidates in a single row — the four r1
frames then the one r2 frame — laid out exactly like the beat 3 and beat 12
sheets. No rows to interpret, no trio labels.

This replaces the trio-row presentation for picking, on the founder's
instruction (2026-08-08): *"stop doing all this complicated row stuff, keep it
like it was for the previous beats."* The `T*` section below is kept as the
record of what those rows meant, not as a way to answer.

**Answer with three `p*` addresses, one per beat** — e.g. "`p07-r2-s0`,
`p08-r1-s1`, `p09-r2-s0`". Mixing rounds across the three beats is a legal
answer; the tables below resolve each address on its own.

## `p07-*` — checklist item 03

Beat 7 **wide** in the progression. **r2 is the live set** (palette + seed locked across 7/8/9).

| label | source PNG | seed | on sheets |
|---|---|---|---|
| **`p07-r1-s0`** | `07-zero-0-moving-parts-prog-s0.png` | 20260726 | `beat07-prog`, `overview`, `progression-789`, `progression-789-r2` |
| **`p07-r1-s1`** | `07-zero-0-moving-parts-prog-s1.png` | 20261726 | `beat07-prog`, `progression-789` |
| **`p07-r1-s2`** | `07-zero-0-moving-parts-prog-s2.png` | 20262726 | `beat07-prog`, `progression-789` |
| **`p07-r1-s3`** | `07-zero-0-moving-parts-prog-s3.png` | 20263726 | `beat07-prog`, `progression-789` |
| **`p07-r2-s0`** | `07-zero-0-moving-parts-prog2-t0.png` | 20260726 | `progression-789-r2` |

All five are on `LABELED-beat07-all.png`, left to right in the order above.

## `p08-*` — checklist item 03

Beat 8 **medium** in the progression. **r2 is the live set.**

| label | source PNG | seed | on sheets |
|---|---|---|---|
| **`p08-r1-s0`** | `08-sev-1-prog-s0.png` | 20260727 | `beat08-prog`, `overview`, `progression-789`, `progression-789-r2` |
| **`p08-r1-s1`** | `08-sev-1-prog-s1.png` | 20261727 | `beat08-prog`, `progression-789` |
| **`p08-r1-s2`** | `08-sev-1-prog-s2.png` | 20262727 | `beat08-prog`, `progression-789` |
| **`p08-r1-s3`** | `08-sev-1-prog-s3.png` | 20263727 | `beat08-prog`, `progression-789` |
| **`p08-r2-s0`** | `08-sev-1-prog2-t0.png` | 20260726 | `progression-789-r2` |

All five are on `LABELED-beat08-all.png`, left to right in the order above.

## `p09-*` — checklist item 03

Beat 9 **close** in the progression. **r2 is the live set.**

| label | source PNG | seed | on sheets |
|---|---|---|---|
| **`p09-r1-s0`** | `09-whoami-prog-s0.png` | 20260728 | `beat09-prog`, `overview`, `progression-789`, `progression-789-r2` |
| **`p09-r1-s1`** | `09-whoami-prog-s1.png` | 20261728 | `beat09-prog`, `progression-789` |
| **`p09-r1-s2`** | `09-whoami-prog-s2.png` | 20262728 | `beat09-prog`, `progression-789` |
| **`p09-r1-s3`** | `09-whoami-prog-s3.png` | 20263728 | `beat09-prog`, `progression-789` |
| **`p09-r2-s0`** | `09-whoami-prog2-t0.png` | 20260726 | `progression-789-r2` |

All five are on `LABELED-beat09-all.png`, left to right in the order above.

## `T*` — the 7/8/9 trio rows (`TRIOS-789-0808.png`) — SUPERSEDED, kept for the record

> **Do not ask for a `T` label and do not answer with one.** The founder turned
> this presentation down on 2026-08-08 in favour of the three plain per-beat
> sheets above. The mapping below stays because it is the record of how the 15
> frames were grouped, and because a `T` label spoken earlier still has to
> resolve to something. Every frame in it is reachable by its `p*` address.

The `progression-789*` sheets show every 7/8/9 candidate in one grid, which reads
as one mixed pile — *"for beat 7/8/9, i am confused? all of these are mixed in?"*
`TRIOS-789-0808.png` re-lays the same 15 frames as **five rows**, one row per
candidate cut: left-to-right in every row is **wide (beat 7) → medium (beat 8) →
close (beat 9)**. **Say a row label — `T1` … `T5` — and it resolves to exactly
three PNGs.** Individual `p*` addresses still work; the small amber chip on each
tile is that one frame's own label, unchanged from the tables above.

**How the rows were grouped.** Two different rules, and the sheet says which is
which on the row band:

- **`T1` is authoritative.** The r2 frames (`candidate_set: prog2`) were rendered
  as a trio on purpose: one byte-identical palette/negative block and **ONE
  shared seed, 20260726, across all three shots** — their sidecars state it. The
  lens is the only variable. There is exactly one r2 trio, so exactly one r2 row.
- **`T2`–`T5` are grouped by SLOT INDEX, and mixing across those rows is
  allowed.** The r1 frames (`candidate_set: prog`) are three independent 4-seed
  batches with per-beat seeds (`2026N7 26 / 27 / 28`), so no authored trio
  grouping exists for them. Row `Tn` = the nth seed of each shot's own batch —
  a presentation convention, not a claim that those three belong together.

| trio | round | beat 7 — wide | beat 8 — medium | beat 9 — close |
|---|---|---|---|---|
| **`T1`** | **r2 — LIVE, palette + seed locked** | `p07-r2-s0` → `07-zero-0-moving-parts-prog2-t0.png` | `p08-r2-s0` → `08-sev-1-prog2-t0.png` | `p09-r2-s0` → `09-whoami-prog2-t0.png` |
| **`T2`** | r1 — slot 0 | `p07-r1-s0` → `07-zero-0-moving-parts-prog-s0.png` | `p08-r1-s0` → `08-sev-1-prog-s0.png` | `p09-r1-s0` → `09-whoami-prog-s0.png` |
| **`T3`** | r1 — slot 1 | `p07-r1-s1` → `07-zero-0-moving-parts-prog-s1.png` | `p08-r1-s1` → `08-sev-1-prog-s1.png` | `p09-r1-s1` → `09-whoami-prog-s1.png` |
| **`T4`** | r1 — slot 2 | `p07-r1-s2` → `07-zero-0-moving-parts-prog-s2.png` | `p08-r1-s2` → `08-sev-1-prog-s2.png` | `p09-r1-s2` → `09-whoami-prog-s2.png` |
| **`T5`** | r1 — slot 3 | `p07-r1-s3` → `07-zero-0-moving-parts-prog-s3.png` | `p08-r1-s3` → `08-sev-1-prog-s3.png` | `p09-r1-s3` → `09-whoami-prog-s3.png` |

Seeds per row: `T1` 20260726 / 20260726 / 20260726 (shared); `T2` 20260726 /
20260727 / 20260728; `T3` 20261726 / 20261727 / 20261728; `T4` 20262726 /
20262727 / 20262728; `T5` 20263726 / 20263727 / 20263728.

A mixed pick is a legal answer and needs no trio label — name the three `p*`
addresses, e.g. "`p07-r2-s0`, `p08-r1-s1`, `p09-r2-s0`".

## `b07-*` — not on the checklist

Beat 7 *fix* set — **superseded, not on the checklist.** Beat 7's answer now comes from the item-03 progression (`p07-*`). Listed only so a `b07` address never silently resolves to a progression frame.

| label | source PNG | seed | on sheets |
|---|---|---|---|
| **`b07-r1-s0`** | `07-zero-0-moving-parts-fix-s0.png` | 20260726 | `beat07-fix`, `overview` |
| **`b07-r1-s1`** | `07-zero-0-moving-parts-fix-s1.png` | 20261726 | `beat07-fix` |
| **`b07-r1-s2`** | `07-zero-0-moving-parts-fix-s2.png` | 20262726 | `beat07-fix` |
| **`b07-r1-s3`** | `07-zero-0-moving-parts-fix-s3.png` | 20263726 | `beat07-fix` |

## Which sheet to look at

| sheet | shows | status |
|---|---|---|
| `LABELED-WAVE-0807-overview.png` | s0 of every set, all ten on one screen | **round 1 only** — its beat 3 and beat 12 tiles are the rejected r1 frames |
| `LABELED-beat03-r3.png` | beat 3, r2 + r3, 8 frames, same seed per column | **current — use this one for beat 3** |
| `LABELED-beat06-r3.png` | beat 6, r1 + r3, 8 frames, r3 on NEW seeds | **current — use this one for beat 6** |
| `LABELED-beat10-r3.png` | beat 10, r1 + r3, 8 frames, same seed per column | **current — use this one for beat 10** |
| `LABELED-beat14-r3.png` | beat 14, r1 + r3, 8 frames, same seed per column | **current — use this one for beat 14** |
| `LABELED-WAVE-0807-beat03-r2.png` | beat 3, r1 + r2, 8 frames | superseded by `beat03-r3` (all eight rejected 2026-08-08) |
| `LABELED-WAVE-0807-beat06-fix.png` | beat 6, 4 frames | superseded by `beat06-r3` |
| `LABELED-WAVE-0807-beat10-fix.png` | beat 10, 4 frames | superseded by `beat10-r3` |
| `LABELED-WAVE-0807-beat12-r2.png` | beat 12, both rounds, 8 frames | answered — `b12-r2-s1` is canon |
| `LABELED-WAVE-0807-beat14-fix.png` | beat 14, 4 frames | superseded by `beat14-r3` |
| `LABELED-beat15-r3.png` | beat 15, both rounds, 8 frames, same seed per column | **current — the ONE SAMPLE, screen this first** |
| `LABELED-WAVE-0807-beat15-fix.png` | beat 15, 4 frames | superseded by `beat15-r3` |
| `LABELED-beat07-all.png` | beat 7, all 5 candidates in one row, r1 then r2 | **current — use this one for beat 7** |
| `LABELED-beat08-all.png` | beat 8, all 5 candidates in one row, r1 then r2 | **current — use this one for beat 8** |
| `LABELED-beat09-all.png` | beat 9, all 5 candidates in one row, r1 then r2 | **current — use this one for beat 9** |
| `TRIOS-789-0808.png` | 7/8/9 as 5 trio rows, 15 frames, wide→medium→close per row | **superseded 2026-08-08** — row presentation turned down; kept for the record |
| `LABELED-WAVE-0807-progression-789-r2.png` | 7/8/9 progression, both rounds, 6 frames | superseded for picking by the three per-beat sheets |
| `LABELED-WAVE-0807-progression-789.png` | 7/8/9 progression round 1, all 12 seeds | round 1 only, one mixed grid — the sheet that caused the confusion; kept for comparing seeds within r1 |
| `LABELED-WAVE-0807-adjacency.png` | the r1 picks for 10, 12, 14, 15 side by side | beat 12's tile is an r1 frame, superseded |
| `LABELED-WAVE-0807-beat03-fix.png` | beat 3 round 1 alone | superseded by `beat03-r2` |
| `LABELED-WAVE-0807-beat12-fix.png` | beat 12 round 1 alone | superseded by `beat12-r2` |
| `LABELED-WAVE-0807-beat07-prog.png` | beat 7 progression r1, 4 seeds | per-shot view of `progression-789` |
| `LABELED-WAVE-0807-beat08-prog.png` | beat 8 progression r1, 4 seeds | per-shot view of `progression-789` |
| `LABELED-WAVE-0807-beat09-prog.png` | beat 9 progression r1, 4 seeds | per-shot view of `progression-789` |
| `LABELED-WAVE-0807-beat07-fix.png` | beat 7 fix set, 4 frames | superseded — beat 7 is answered by `p07-*` |

`WAVE-0807-style-anchor.png` has no labelled version: it is the OLD look kept for
contrast, not a candidate set, so nothing on it is pickable.

## Episode 2 (checklist item 07) — already addressable, left alone

The `CONTACT-002b-*.png` sheets were **not** relabelled. They already carry the
address on every tile: `CONTACT-002b-b01.png` prints `r2-s0  seed 20260720` in each
tile's caption strip — the same convention the `01-cold-open-r3-s3` pick came from.
The four multi-beat sheets (`b02-06`, `b07-11`, `b12-16`, `b17-21`) print the slot and
seed per tile and the beat and round in the row header above each strip
(`BEAT 02  THE SPRINT  [r2]`), so an address there reads as beat + round + slot too.
For those, keep quoting episode 2 picks in the existing full form, e.g.
`002b-b02-r2-s3` — the `b`/`p` grammar above is episode 1 only.

**2026-08-08 evening — the r3 redraw wave supersedes those sheets for picking.**
Beats 02-21 were redrawn (the eighty of 2026-08-07 were "competent frames of
twenty different shows"; the text fixes are the 2026-08-08 wave note in that
node's `shots.md`). The new sheets are `CONTACT-002b-r3-b02-06.png`,
`-b07-11.png`, `-b12-16.png`, `-b17-21.png` — same band convention, band header
`BEAT 02  THE SPRINT  [r3]`, caption `r3-s0  seed 20260721`. Quote picks in the
same full form, e.g. `002b-b02-r3-s3`. Every set jumped to `r3` regardless of
how many rounds a beat had before, so a round label means the same wave
everywhere (the beat-15 logic). The old `CONTACT-002b-b02-06`…`b17-21` sheets
are superseded for picking; they remain the record of the rejected round.

**Beat 01 — round 5, `LABELED-b01-r5.png`.** The 2026-08-07 pick was revoked on
2026-08-08 ("a frame i never approved, and its tooooo tall" — the old sheet
carried a steward favourite mark, which is why this sheet carries labels and
seeds ONLY). Four candidates, `b01-r5-s0`..`b01-r5-s3`, drawn on the round-3
prompt with `sturdy curved stem` (his ceiling) and the b15-r3-s1 negative
recipe. `CONTACT-002b-b01.png` stays as the record of rounds 2-4 and of the
i2i evidence; it is not a pick surface any more.

---

**This key is committed; the sheets it addresses are not.** The key is pure text —
labels, source filenames, seeds — so no candidate pixel ships with it and it adds
nothing to the open D15 licence-gate debt. It is committed because a spoken label
has to resolve in every clone: `STATE.md` and the published checklist both send the
founder here, and a key living in one working tree makes every recorded pick address
unresolvable everywhere else. The `LABELED-*`, `TRIOS-*` and `CONTACT-*` sheets, and
the candidate PNGs they are cut from, stay local review artifacts by design.
