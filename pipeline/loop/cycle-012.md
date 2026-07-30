# Loop cycle 012 — v6 screening notes: the death gets its sound

**Opened:** 2026-07-30 · **Verdict source:** founder's v6 notes (in chat)

## The founder's three notes

1. "Some subtitles are offset."
2. "'huh. green.' should be 'huh. blue.'" (author's line change — R4).
3. "His death is very anticlimactic… something missing that would make it
   much better, because it's a bit boring right now. Probably sound effects
   or music, or go in a whole other direction."

## Diagnoses

1. **Subtitle drift was structural.** The master audio was built as per-beat
   AAC segments concatenated with `-c copy`; AAC quantizes each segment to
   ~23 ms frames and the per-beat video encodes quantize to the frame grid,
   so the two tracks drifted apart cumulatively — later beats' captions lag
   the voice. Captions are burned per-beat (relative times), so the video
   was right; the AUDIO was in the wrong place.
2. The line was recorded, captioned, and manifested as "Huh. Green."
3. **The script's own sound design was never built.** Beat 1 scripts "one
   mechanical keyboard, very fast — then it stops"; beat 5 scripts "Black,
   and the sound of a cooling fan spinning down." Neither existed. The
   gunshot-like thump (cycle 011 v1) was removed and never replaced, so the
   fall played over nothing but the constant wind bed — no contrast, no event.

## Fixes (pipeline, $0)

- **render_t3: one placed mix, not concatenated segments.** Every beat's VO
  is `adelay`ed to its beat's MEASURED video offset (from the actual encoded
  beat files) in a single filtergraph → audio position derives from the
  video, drift is structurally impossible. Assembly now prints the timeline
  table (beat starts + durations) so sound cues are placed against real
  numbers, not paper timing.
- **Line change**: node.md + shots.md → "Huh. Blue."; clip renamed
  `05-huh-blue.mp4`; Chatterbox retake of beat 5 (1.2 s, old take archived
  to vo-archive/, R6). Founder-directed 2026-07-30. Reads consistent with
  the blue-hospital joke chain (his correction of 2026-07-29).
- **The death is contrast, not volume** (`pipeline/sfx.py` + per-node
  `clips/sound.yaml`): synthesized room hum + fast keyboard through the
  opening (J-cut, stops just before the first line) → at the tip-over ALL
  sound dies (hum out + wind bed ducked) → the mug lands ALONE in true
  silence at 14.9 s → the scripted fan spin-down under "Huh. Blue." → the
  world's wind returns with the too-blue sky. No thump, no music: an
  engineer's death told in machine sounds going quiet. All cues synthesized
  with fixed seeds — re-render is bit-identical, nothing downloaded.
- **Bug found by QA on the way**: the bed duck as an afade out+in pair
  silenced the ENTIRE bed (`afade=t=in` mutes everything before its start).
  qa_episode's "no digital silence" check caught it; replaced with a
  windowed `volume` expression. QA now fully green (12 checks; the one
  warn is the scripted BLACK cold open).

## Evidence

- Timeline table: mug transient measured at 14.9 s at −16 dB inside a
  −35 dB silence window; fan 16.3→19.7 s; "Blue." caption frame verified
  inside its chunk window over the fallen-mug shot.
- `banyan-drops/ep1-remake-screening-v7.mp4` (94 s, −14.4 LUFS, peak-bound).

## Verdict

Pending — v7 delivered for the founder's screen. Asks: subtitles now
synced? does the death land? sound.yaml times marked (ear) are the knobs.
Offered: founder-recorded real phone foley (mug, keyboard) to replace the
synthesized stand-ins — better sound AND family provenance.

## Lesson

When a moment is boring, read the script again before adding anything —
episode 1's sound design was already written, in stage directions nobody
had built. And: silence needs something to be the absence OF; the room hum
exists so its death is audible.
