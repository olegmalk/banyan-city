# The Loop — repeatable quality cycle (founder's dad, 2026-07-23)

The season shipped rough because episodes were made *once*. The loop makes
quality compound instead: every cycle upgrades the **pipeline**, and any
episode rendered afterward — remake or new — inherits every fix ever made.
The episode being remade is just the loop's test bench.

## The cycle

1. **DIAGNOSE** — review the benchmark episode cold, like a scrolling
   viewer: what loses attention, ranked by damage. Evidence required
   (frames, timestamps), not vibes. Founder winces and platform numbers
   (ledger/reach.csv) join the list as they exist.
2. **FIX** — top 1–3 defects only, and only as *pipeline/prompt-system*
   changes (style bible, character blocks, shot grammar, renderer code).
   A fix that only helps one video is a hand-touch, not a fix.
3. **RE-RENDER** — the same benchmark episode, next version number, on the
   $0 path (Kaggle floor / free quota if any). Founder-reserved spend rules
   unchanged.
4. **SCREEN** — founder watches old vs new side by side. Keep or revert.
   If clearly better: post it; platform metrics become the external score.
5. **LOG** — `pipeline/loop/cycle-NNN.md`: defects found → fixes applied →
   what the founder felt → what the numbers did. Then go to 1.

## Rules

- **Benchmark: episode 001** (the front door — every viewer judges the
  show by it) until a cycle's diagnosis says another episode teaches more.
- One cycle = small and finished beats big and half-done. Never fix more
  than 3 things per cycle; you can't tell what worked.
- Old versions are never deleted (R6) — v1/v2 stay as leaves; the site
  shows the latest.
- **QA gate (2026-07-24, founder directive):** every re-render passes
  `pipeline/qa_episode.py` — the end-to-end test encoding every
  confirmed defect class (faststart, loudness/peak, dead air, frozen or
  dark opens, captions vs platform chrome, manifest engine/chunks) —
  before it is staged for a drop or published as a leaf.
- Diagnosis is model-run; **taste verdicts stay the founder's** (R4):
  the loop proposes, the screening decides.
- Every re-render publishes provenance like any leaf (§7.2).

## Cycle log

| Cycle | Diagnosed | Top defects | Fixes | Verdict |
|---|---|---|---|---|
| 001 | 2026-07-23 | silent 2.5s open; −22 LUFS + dead-air holes; wall-of-text captions (15 confirmed, `loop/cycle-001.md`) | 3 chosen, all render_t3 assembly — v3 re-cuts at $0 | **KEPT** (founder, 2026-07-23: "indeed it is better") |
| 002 | 2026-07-23 (founder winces on v3) | captions offset from voice; voice very emotionless | measured chunk sync + directed pauses/speed (`synth_vo.py`) | founder on v4: "i dont see a difference" — rhythm wasn't the ceiling, the engine was → cycle 003 |
| 003 | 2026-07-23 | kokoro cannot act (engine ceiling) | second engine: Chatterbox 0.5B local/MPS, cloned from kokoro cast refs (`build_refs.py`), per-line emotion direction from script cues | founder on v5: "it is improving for sure" — KEPT; rolling to eps 2–7 |
| 004 | 2026-07-24 | dead-air tails: beat slots ran the full clip regardless of voice length | voice-led slots (`fit_duration`, ≤2s beat-out) | KEPT — founder posted ep 4 |
| 004b | 2026-07-24 | "voices are mixed up" — clone convergence from one shared reference passage | per-character reference text, speeds, pitch offsets (`build_refs.py`) | partial; measured properly in 007-adjacent work |
| 005 | 2026-07-24 | loop restarts read as jump-cuts; near-still hook shots | palindrome loop seams; motion grammar in `style.md` + advisory lint | KEPT |
| 006 | 2026-07-25 | comprehension: no speaker attribution; the tree mute on screen (3 cold-viewer tests) | speaker-labelled captions (incl. THE TREE), deadpan register, unspoken text removed, `qa_voices.py` + separated pitch bands | cold-viewer 6/10 → 7/10; founder still could not follow → cycle 007 found why |
| 007 | 2026-07-25 | **shot density: one shot every 18s carrying 4.4 lines — the picture cannot follow the script** (dad: "random video not correlating") | structural: all 7 trunk scripts molted to one beat = one shot (35 → 166 shots), `SCRIPT-SPEC.md`, growth ladder | scripts done + cold-read; awaiting footage, then founder screening (R4) |
| 008 | 2026-07-25 (night) | **the AUDIO didn't match the script either, and no gate was looking**: stage directions owned 3.6–4.5s of silent screen time each (~1057s genome-wide); beats that lost dialogue in the molt kept the previous cut's voice (007a spoke its closing line at beat 5); beat time ranges were hand-guessed, so 001 claimed 88s and assembled at 133s; masters undershot −14 LUFS when peak-bound | `direction.py` allowlist (only the tree's own gestures reach screen, hold capped 2.2s); synth_vo archives orphaned takes; `retime_beats.py` derives ranges via the assembler's own `fit_duration`; measure-then-correct mastering | fixes verified by measurement; re-voice + re-time of the trunk in flight, founder screening pending |
