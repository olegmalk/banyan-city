# Loop cycle 014 — the death was a hole, and it was measurable all along

**Opened:** 2026-08-01 (overnight) · **Closed:** pending founder screen
**Source:** founder's standing note, unresolved across cycles 011–013: *"his
death is very anticlimatic"*, and cycle 013's three cold readers agreeing *"the
death does not read — he knocked his coffee over / he fell asleep"*.

## The note that four rounds of work failed to fix

The thump has been moved, replaced, re-placed against measured offsets,
re-recorded from a real public-domain thud, and finally re-mastered from −14 to
−17 LUFS so it would stop being crushed by the limiter. After all of it the
founder's note stood.

**Because the thump was never the problem.** At 14s it is the loudest moment in
the episode — louder than any line of dialogue. Four rounds moved something that
was already right.

## Diagnosis

Measured, not listened to:

1. **Beat 4 runs 10.08s. The script gives it 5** (`THE FALL — 0:15–0:20`). It is
   two 5.04s shots concatenated at full length, and it carries **no VO at all**.
2. **That silent double-length beat IS the "anticlimax".** RMS across it decays
   from −28 dB to −46 while dialogue sits at −13: nine and a half seconds of
   near-nothing at the exact moment the story turns.
3. **It is in every cut ever screened**, always at 15s, and it has been getting
   worse — v11 6.5s, v13 6.2s, v17 7.5s, v18 9.5s. The −17 LUFS re-master
   shipped as *the fix for this note* made it 2s longer and 5 dB deeper: pulling
   the master down lifted the impact above the dialogue (the ask) and widened the
   hole behind it (not noticed). One problem traded for a worse version of another.
4. **`qa_episode` could not see it.** `silencedetect` thresholds on PEAKS, and the
   peaks stayed above the −33 dB floor, so "no quiet stretch > 3.5s" passed on
   every cut while the actual defect went unnamed for three cycles.
5. Separately: **beat 5, scripted "Black, and the sound of a cooling fan spinning
   down", is a 4-second copy of the bright sky** — luma 135.8 against 136.2 for
   the sky beat after it. The same shot twice. So "Huh. Blue.", written to be
   spoken in the dark *before* the reveal, plays on top of the reveal.

## Fixes

**In the pipeline (landed):** `qa_episode.quiet_hole()` measures the longest
stretch far below the episode's OWN 90th-percentile speech level, relative rather
than absolute, because an absolute floor cannot express "far below the speech
around it". Reports length, location and floor as a warning — scored silence is
real, and two seconds of nothing lands a death where nine loses the audience.
Verified against a steady-tone control. This is the check that should have
existed at cycle 011.

**In the cut (three options, deliberately NOT bundled — measured independently):**

| | 14–25s mean | hole |
|---|---|---|
| baseline (= v18) | −35.0 dB | 9.5s |
| beat 4 → scripted 5s (both shots kept, 2.52s each) | −27.2 dB | gone |
| + fan −18→−11 dB / 12s→7.2s, + room hum under a black beat 5 | −24.9 dB | gone |

**The beat-4 trim is the whole fix** and is not a taste call: a beat running
double its scripted length with no dialogue is a defect. The other two are
optional, and one of them is contentious —

## What this cycle also found about cycle 013

Cycle 013 records the sky-instead-of-black as the founder's own call: *"The
founder was right that naming the colour over a black frame wastes the line."*
The founder's actual words, as far as they can be traced, are *"when he says 'huh
blue' its showing the terminal image for some reason"* — an objection to the
**terminal**, not an endorsement of the sky. A paraphrase became an attributed
decision, the script was never updated to match, and the two have contradicted
each other in silence ever since. Flagged to the founder rather than reverted:
if the call was real it stands, but then `node.md` must stop claiming otherwise.

**Nothing committed.** Picture is script, script is R4. Cuts for screening:
`ep1-v19-BASELINE / -B4TRIM / -FULL.mp4`, frames in `DEATH-before-after.png`,
sound half in `death-fix-sound.patch`.

## Lesson

A note that survives four attempted fixes is a note nobody has measured. "It
feels anticlimactic" was a precise, quantitative statement about level over time
the entire time — and the QA suite was asking a question ("is it silent?") close
enough to the real one ("is it far below the dialogue?") to return a green tick
for three cycles.
