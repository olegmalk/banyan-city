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

## Status

Diagnosis logged. Next: line-granular shot list for the front door (001,
whose molt script is already R7-compliant) as the template, then Kaggle
validation. No assembly-side work is scheduled — it cannot fix this.
