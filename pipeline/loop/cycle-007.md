# Loop cycle 007 — shot density: the picture doesn't follow the script (2026-07-25)

Opened by the founder's dad on the before/after showcase, and it
supersedes the whole cycle-006 line of work in priority:

> "The video is not matching the audio at all, or the script. It feels
> like you just have a random video playing that isn't correlating to the
> script. That is the main problem."

## Measured

| ep | voice runtime | distinct shots | lines | sec/shot | lines/shot |
|---|---|---|---|---|---|
| 001 | 62s | 5 | 11 | 12.4 | 2.2 |
| 002b | 86s | 5 | 17 | 17.3 | 3.4 |
| 003b | 78s | 4 | 14 | 19.5 | 3.5 |
| 004 | 75s | 4 | 18 | 18.7 | 4.5 |
| 005 | 81s | 4 | 30 | 20.4 | 7.5 |
| 006a | 153s | 6 | 41 | 25.4 | 6.8 |
| 007a | 81s | 7 | 24 | 11.6 | 3.4 |

**Season: 616s of voice over 35 distinct shots — one shot every 18
seconds, carrying 4.4 lines each.** Short-form video cuts every 1.5–3s;
TV dialogue 2–4s. The tree is 6–12x under the floor.

Worked example (006a beat 3): 23 lines / 80 seconds of a legal argument
that moves through resident → property → livestock → tenancy → shrine,
covered by TWO shots of "she paces the clearing." The dialogue advances
through five distinct ideas; the frame shows one generic tableau. A
viewer cannot map words to picture because the picture has no
per-moment content to map to.

## This explains earlier symptoms as one root cause

- founder 2026-07-23: "some videos just loop the same clip WAYYY too long"
- cycle-001 verified defect: "climax replays its entire 10s clip verbatim"
- cold-viewer 2026-07-25: "the visuals actively taught me the wrong
  referent — 'it has no hearth' over a close-up of the goblin"
- cold-viewer: "the tree is never established as a character at all"
  (it is off-screen while it speaks)

Every one of those is shot starvation. The assembly-side fixes of cycles
001–006 (audio floor, caption sync, speaker labels, loop seams, voice
separation) were real and measurable — comprehension moved 6/10 → 7/10 —
but they were treating a footage problem with post-production.

## The fix (structural, not assembly)

**Shot per moment, not shot per beat.** A beat is a 20–30s unit of
script; a shot must be a 2–5s unit of *attention*, and the camera must be
on the referent the line is about. That means ~1 shot per 1–2 lines:
roughly 150–200 shots for the season instead of 35, and 15–25 shots per
new episode instead of 4–7.

Consequences, honestly:

1. **Shot lists must be written at line granularity** — cheap ($0),
   steward work, and the prerequisite for everything else. Also the place
   to fix referent alignment: each shot names whose line it covers.
2. **Render capacity is now the project's binding constraint.** Free
   provider quota is spent. 4–6x more footage per episode makes the
   `$0` Kaggle floor (`pipeline/kaggle/wan-t2v-kaggle.ipynb`, never
   validated end-to-end) the critical path, not a nice-to-have.
3. **Character consistency gets harder as shots multiply** — 20 shots of
   the same goblin means 20 chances to redesign him. Reference-image
   conditioning (verified cycle-001 backlog) is no longer optional; it
   ships with the density fix or the density fix makes drift worse.

## The fix, as executed (2026-07-25)

All seven trunk nodes molted to `SCRIPT-SPEC.md`. Dialogue is verbatim in
every case; what changed is where the camera points. Measured after:

| node | length | shots before | shots after | cut every | lines/shot |
|---|---|---|---|---|---|
| 001  | 88s  | 5 | 18 | 4.9s | 0.89 |
| 002b | 107s | 5 | 21 | 5.1s | 0.86 |
| 003b | 119s | 4 | 21 | 5.7s | 0.81 |
| 004  | 117s | 4 | 21 | 5.6s | 0.86 |
| 005  | 149s | 4 | 25 | 6.0s | 1.08 |
| 006a | 189s | 6 | 31 | 6.1s | 0.94 |
| 007a | 193s | 7 | 29 | 6.7s | 0.66 |

**Season: 35 shots → 166 shots, measured.** One shot every 18 seconds
carrying 4.4 lines became one every 5.8s carrying 0.87. Total runtime grew
595s → 962s: the episodes are longer because a shot now gets time to read,
not because dialogue was added (144 lines across the trunk, none invented —
the count moves only where a long line was split at its natural break). Each node was read by a
context-free cold viewer before commit and its faults fixed pre-render;
the transcripts are in each node's `sap/`.

Two canon-level defects surfaced during the rewrite and were fixed in
`style.md`: the tree's **size was never defined** anywhere in the series
(a sprout and a shade-giving tree are different characters, and the town
is named Shade) — now a growth ladder from ~15cm at 001 to ~1.6m at the
finale; and the motion grammar was implicit, so prompts described
tableaux instead of actions. Still open and reserved to the author (R4):
**the protagonist has no name.**

## What the rewrite cost, discovered downstream

1. **Every VO track in the season is stale.** VO is synthesized per beat
   as `NN-vo.mp3`; the old files are numbered against a 4–7 beat
   structure and the scripts now have 18–31. Re-voicing the trunk is
   ~150 lines of local Chatterbox time, not a re-tag.
2. **All 166 shots need footage.** Nothing carries forward — 001's
   surviving clips are v1 photoreal, archived by design.
3. **Kaggle interactive sessions produce nothing fetchable.** The
   founder's first real run (2026-07-25) rendered a beat in a browser
   tab; when the tab closed the session died, and `kernels output` 404s
   because there is no saved version. Batch (`kernels push`) is the only
   mode that yields retrievable clips. `run_remote.py push <node>
   --steps N` now drives it headless; 001 is queued at STEPS=25.

## Status

Diagnosis fixed at the level it was diagnosed: script and shot list, not
assembly. Green on lint and the 28 tests. Awaiting footage and a founder
screening (R4) — the verdict on whether the picture now matches the
script cannot be self-assessed.
