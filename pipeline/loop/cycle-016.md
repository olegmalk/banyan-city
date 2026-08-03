# Loop cycle 016 — the picture was frozen because we told it to be

**Opened:** 2026-08-03 · **Closed:** pending founder screen of the F-recipe cut
**Source:** the founder, on the 720p cut assembled overnight: *"this
ep1-v22-hires.mp4 is too static for almost all of the beats."* And earlier, on the
model comparison: *"wan 2.2 basically doesnt move at all, literally."*

## The finding

Nothing was wrong with Wan 2.2. **Four separate instructions we had added ourselves
were suppressing motion**, three of them added for reasons that had nothing to do
with motion:

| term | why it was added | what it cost |
|---|---|---|
| Wan's own 静态/静止 defaults | inherited from the official negative | freezing, fixed in cycle 015 |
| our shake-suppression terms | founder: *"shaking alot, strangly"* | **3.3x** motion when removed |
| `"camera locked"`, in all 15 directions | stop the camera drifting | measured **free** to remove |
| `"hands going still"` (steward's wording) | describe the end of the typing | froze the beat entirely |

The `"camera locked"` result is the one worth remembering: **in image-to-video the
init frame locks the framing, not the phrase.** Camera translation measured
0.00–0.02px with it removed, against 4.83px on the clip the founder had called
"aggressively moving". It was protecting nothing and taxing the subject.

## The measurement was wrong all day, and that is the real lesson

Every figure the steward quoted — 0.19, 0.62, 1.18, "K wins with a 4.1x hand/body
ratio" — was a **mean** frame-to-frame difference. A mean is dragged up by one large
jump, so it cannot tell continuous animation from a clip that sits still and then
cuts.

Re-scored on the median plus the share of barely-moving frames:

| variant | mean | median | frozen frames |
|---|---|---|---|
| the cut he rejected | 0.19 | 0.13 | **70%** |
| shake terms off | 0.64 | 0.62 | 25% |
| + no `"camera locked"` | 0.84 | 0.79 | 22% |
| **F — + amplitude wording** | 1.22 | **1.30** | **3%** |
| K — + body negative | 0.35 | 0.27 | **38%** |
| hosted models, for scale | — | 1.03–1.13 | **0%** |

**The steward recommended K and re-rendered fifteen beats on it.** K's celebrated
ratio came from suppressing motion everywhere rather than from pinning the body. The
founder's *"literally just frozen frames"* was exact about a clip that had been
called the winner an hour earlier, and he then picked F — the variant he had himself
rejected — once he could see it beside the alternatives.

**A mean hid a third of the frames not moving.** Any future motion claim uses median
+ frozen share.

## What the body-motion trade actually is

The founder's objection to F was *"he's like moving all of his body parts the whole
time"*. Every attempt to fix that cost animation, monotonically:

| body constraint | median | frozen |
|---|---|---|
| none (F) | 1.30 | 3% |
| in the POSITIVE ("his torso stays still") | 0.69 | 25% |
| in the NEGATIVE (no swaying, no leaning…) | 0.29 | 43% |

So it cannot be had both ways with prompt-level controls, and the negative is the
worst of the three. Writing stillness into the positive did essentially nothing —
the fourth time today the negative turned out to be the lever and the positive did
not.

## Infrastructure that was hiding results

Three of these mattered more than any prompt change, because each one produced a
confident wrong conclusion:

1. **`--guidance` never reached the renderer.** The single-beat path did not pass it
   and `stage_render` hardcoded 5.0, so a cfg 3.0 canary produced a file
   BYTE-IDENTICAL to the cfg 5.0 baseline — same sha256. "Guidance did nothing" was
   written into a commit message on the strength of that non-result. Guidance remains
   untested.
2. **The negative prompt was silently truncated**, mid-word, at a 460-char cap that
   was a guess against a ~512-*token* budget. Still beats were losing five of the
   eight anti-scene-change terms on every render — the terms that fixed the scene-cut
   drift in the first place.
3. **stderr was not drained until the child exited.** tqdm writes there, so a
   sampler that was running normally looked silent, and an unread pipe can fill and
   block the child outright — indistinguishable from a hang, and the shape of the
   "eight hours, no clips, still breathing" night in cycle 014.

Also: the new amplitude verbs (*hammer, flying, drive, jolt, slamming*) were not in
`WANTS_MOVE`, so five rewritten beats silently lost their anti-static terms — the
classifier did not recognise the strongest motion language in the file as motion.
Caught by the tests, not by eye. The vocabulary now matches stems, because it had
"pulses" but not "pulsing".

## A test that had to be replaced, not satisfied

`test_pipeline` asserted **every** motion prompt contains `"camera locked"`. That
encoded a belief measurement has since falsified, and it would have blocked the
founder's own call. It now checks only the three deliberately-still beats keep it.

**A test may enforce an invariant; it may not outvote a measurement.**

## Fixes landed

- all 15 directions rewritten in F's register — name the amplitude, not the fact of
  motion; `"camera locked"` kept only on beats 4, 6, 8
- shake suppression decided per beat, following `antistatic_for` inverted
- `antistatic_for` takes the FIRST signal, so a direction can say "stay still" about
  the body and still get anti-static
- `--guidance` plumbed through all three sampling paths; a test asserts every
  sampling parameter reaches the child, that no flag is sent the renderer does not
  define, and that no defined flag goes unread
- `--keep-text-encoder` deleted: declared, plumbed, read nowhere
- negative deduped, cut on a comma, truncation printed, cap raised with arithmetic
- stderr drained on its own thread and counted as liveness; two watchdog clocks
- Kaggle's notebook switched off LTX, which is licence-blocked, onto Wan 2.2

## Lesson

Three of the four motion suppressors were added for PICTURE QUALITY and acted on
MOTION — the shake terms, `"motion blur"` (measured neutral, reverted), and Wan's
inherited defaults. A negative prompt does not know why a term is there.

And the founder was right six times before the measurement was: frames were never
the point, the frames were frozen, F beat K, we did not need more compute, beat 1
needed no stop, and the model comparison was worth doing. The steward's metric
disagreed with him three of those times and the metric was wrong each time.
