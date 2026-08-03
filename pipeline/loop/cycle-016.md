# Loop cycle 016 — everything suppressing the motion was ours

**Opened:** 2026-08-03 · **Closed:** pending founder screen of the F re-render
**Source:** founder on the model comparison — *"wan 2.2 basically doesnt move at
all, literally"* — then on the assembled cut, *"this ep1-v22-hires.mp4 is too static
for almost all of the beats"*, and on the steward's chosen fix, *"literally just
frozen frames."*

## The finding

Nothing about Wan 2.2 was the problem. Four separate motion suppressors were in our
own prompts, three of them added deliberately for other reasons:

| suppressor | why it was added | cost |
|---|---|---|
| Wan's own anti-static defaults (静态, 静止) | inherited from the official negative | fixed cycle 015 |
| our shake-suppression terms | to fix *"shaking alot, strangly"* (cycle 015) | **3.3x** |
| `"camera locked"` in all 15 directions | to stop scene drift | **1.3x** |
| the steward's own `"hands going still"` | rewriting beat 1 | froze the beat |

Each was a correct fix for the complaint in front of it, and each acted on motion
nobody was thinking about at the time. **This is now the pattern to expect: in this
pipeline you get motion by REMOVING suppressors, and you stop motion by NAMING it in
the negative. Positive prose about stillness does nothing** — variant H wrote *"his
head, shoulders and torso stay still"* into the direction and pinned nothing at all.

`"camera locked"` is the one worth remembering: it protected nothing. In
image-to-video **the init frame locks the framing**, not the phrase. Camera
translation measured 0.00–0.02px with it removed, against 4.83px on the clip the
founder called *"aggressively moving"*.

## The measurement was wrong all day, and that is the real lesson

Every figure quoted before the last hour was a **mean** frame-to-frame delta. A mean
is dragged up by one big jump, so it cannot distinguish continuous animation from a
frozen clip with one cut in it.

| variant | mean | median | frames barely moving |
|---|---|---|---|
| the cut he rejected | 0.19 | 0.13 | **70%** |
| shake terms off | 0.64 | 0.62 | 25% |
| + no `"camera locked"` | 0.84 | 0.79 | 22% |
| **F — his pick** | 1.22 | **1.30** | **3%** |
| **K — steward's pick** | 0.35 | 0.27 | **38%** |
| hosted models, for scale | — | 1.03–1.13 | 0% |

K's celebrated "4.1x hand-to-body ratio" was achieved by suppressing motion
*everywhere*, not by pinning the body — and fifteen beats were re-rendered on it, 48
minutes, before the founder looked at the result and said *"literally just frozen
frames."* He was describing 38% dead frames, exactly.

**The share of frames that barely move is the number that matches an eye.** It is
now what `collect_farm.py --measure` reports.

## Dead ends, recorded so they are not re-tried

- **Frame count.** 61 → 121 frames made it *worse* (0.62 → 0.59). The founder called
  this before it was tested: *"we dont need so many frames.. thats.. not the point."*
  More frames at the same fps lengthen the clip; they do not speed the hands.
- **The static scene anchor.** Dropping the 25-word composition tail: 0.62 → 0.54,
  also worse. Good reasoning (the image already *is* the composition), wrong answer.
- **`"motion blur"` in the negative.** 0.63 vs 0.62 — motion-neutral. Reverted rather
  than kept, because a change that buys nothing while weakening the anti-photoreal
  guard is not worth keeping just because it was argued for well.
- **Guidance.** Not a dead end — an **invalid test**. See below.
- **Pinning the body.** Costs animation in every form: positive 25% frozen, negative
  43%, none 3%. There is no version of this that keeps both.

## Infrastructure that was hiding the answers

Four bugs that each turned a real measurement into a non-result:

1. **`--guidance` never reached the renderer.** The cfg 3.0 clip was byte-identical
   to cfg 5.0 — same sha256, 0.000/255 pixel difference. The batch path passed the
   flag; the single-beat path, which every clip uses, did not. And `stage_render`
   hardcoded `guidance_scale=5.0`. "Guidance did nothing" had already been written
   into a commit message on the strength of that.
2. **The negative prompt was truncated mid-word**, and silently. A still beat hit
   exactly the 460-char cap and the tail arrived as `"fil"`. The cap turned out to be
   a guess against a ~512-**token** budget (~146 tokens actual), so five of eight
   anti-scene-change terms were being dropped from every still-beat render.
3. **stderr was not drained until the child exited.** tqdm writes there, so a slow
   render looked silent — and an unread pipe fills at ~64KB and **blocks the child**,
   which is indistinguishable from a hang from outside. Reproduced: the harness
   demonstrating it had to be killed at its own timeout.
4. **The stall watchdog could not tell slow from hung**, killing a healthy 45-minute
   render for being slow. Two clocks now: silence kills, printing-but-no-progress
   gets three hours.

And one test was **enforcing a belief against evidence**: it asserted every motion
direction must contain `"camera locked"`. That would have blocked the founder's own
call. A test may enforce an invariant; it may not outvote a measurement.

## Fixed alongside

- **`WANTS_MOVE` did not recognise its own vocabulary.** The rewritten directions say
  "hammer", "flying", "slamming", "thrashes" — none matched, so five beats silently
  lost their anti-static terms. Now stem-matched, because the old list had "pulses"
  but not "pulsing".
- **`antistatic_for` now takes the FIRST signal.** It checked stillness first, so
  "types fast … hands going still" read as a still beat. Directions are written
  subject-first; the opening clause is the subject.
- **Kaggle's free GPU was rendering LTX**, which is licence-blocked — every video it
  ever made for us was unusable on arrival. Wan 2.2 was already wired and never
  selected.
- **60s of pure waste per clip**: the worker slept the full poll interval after every
  task, with the next beat already queued. 15 minutes an episode.

## Verdict

The founder chose variant F off the comparison — *"this is actually the best overall,
do this kinda thing. its very good."* — the same variant he had rejected an hour
earlier for body motion, seeing it beside the alternatives. All fifteen directions
are rewritten in its register; beats 4, 6 and 8 are untouched because they are
deliberately still.

## Lesson

Three of the four suppressors were added by the steward, in response to a real
founder note, and each one traded away something nobody was measuring at the time.
The instrument compounded it: a mean hid a 38%-frozen clip well enough to get it
recommended and rendered fifteen times.

**The founder's eye beat the steward's metric six times today** — the frame count,
the frozen frames, F over K, the headroom question, beat 1's stop, and whether the
model comparison was worth doing. When a note and a measurement disagree, check what
the measurement is actually asking before trusting it.
