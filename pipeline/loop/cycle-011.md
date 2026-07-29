# Cycle 011 — 2026-07-29 — the screening notes cycle

## Diagnosis (founder screening, v2→v6 same evening)

The founder screened the first complete remake cut and filed six notes in
~90 minutes. Each exposed a distinct pipeline defect class:

1. **"two thousand forty-one"** — the TTS reads `2:41` as an integer.
   Class: text-normalization gap between card text and spoken text.
2. **Death anticlimactic** — beat 04 cut straight from typing to a corpse
   with no impact moment. Class: single-shot beats can't carry an event.
3. **"Huh. Green." misaligned** — the line played over the coffee-mug shot;
   the *green* is the deploy-succeeded glow, so the line belongs on the
   green terminal as his vision fades. Class: shot/line referent drift
   (the shot list predated the founder's read of the joke).
4. **Beat 01 not animated** — assembly used POST while six AI takes existed.
   Class: mechanical take-picking; choosing takes is taste (founder's).
5. **Thump v1 read as a gunshot** — sharp attack + noise crack. Class:
   sound design is iterated like everything else.
6. **Script/shot mismatch** — "Hospitals are green now" vs the blue canon
   shot. Founder rewrote the line to *blue* (author's correction).

## Fixes (all in pipeline, same evening)

- `render_t2.clean_speech` gained spoken-time normalization (2:41 → "two
  forty-one"; 3:07 → "three oh seven"); cards keep the digits.
- `synth_vo` gained `--beats` for surgical single-line retakes (~2 min per
  note instead of a full re-voice).
- Beat 04 is a two-shot sequence (hand → mug) using the assembler's
  existing `-alt` sequencing, with a synthesized 38 Hz body-thud at the cut
  (v1 of the thump was rejected as gunshot-like; v2 duller, slow attack).
- Beat 05 plays the deploy-green terminal with a dying-vision grade
  (dim + vignette + fade to black) — deterministic ffmpeg, $0.
- Screening cuts stage ONE chosen take per beat (curated dir), replacing
  the accidental all-takes showreel.

## Verdict

Pending — v6 delivered for the founder's return. Also open: the named
worst-emotion voice lines (notes promised), and a possible voice-engine
bake-off (fish.audio open model vs Chatterbox; the hosted fish API is
paywalled — 402, nothing spent).

## Lesson

The remake's last mile was not rendering — it was the founder's six notes,
each turned around in minutes because stills, voice lines, SFX and takes
are all independently re-buildable. Iteration speed on NOTES, not on
pixels, is what "fast" means now.
