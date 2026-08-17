# Judging brief — ep2 beat 02 `anchor` (16 seeds) and beat 03 `st` (15 seeds)

2026-08-17. You are a READING lane. Your reading is the verdict; a metric is a filter.

## What you are given

For each clip `<name>`:

- `pipeline/measured/judge-0817-b02b03/cold/<name>/strip-01.png` … `strip-NN.png`
  — **CONSECUTIVE source frames**, one frame apart, each cell labelled with its
  source frame index and nothing else. Read them **in order, all of them**.
- `.../cold/<name>/overview.png` — an EVEN spread across the full 97 frames.
  Use it for PROPORTIONS ONLY (how much of the clip is dead air). It is
  **not** evidence about smoothness — six skipped frames of a continuous
  move look exactly like a cut. That defect produced a wrong verdict on the
  record; do not repeat it.
- `.../cold/<name>.json` — the coldread manifest (window, head/body/tail MAD).

## Read the STRIPS FIRST, before the overview, before the json.

## The two beats — quote the right one

### Beat 02 — THE SPRINT (`02-the-sprint-LTX-anchor-*.mp4`)

node.md script line:

> A SCAVENGER — goblin-ish, enormous ears, one broken tusk, patchwork cloak —
> sprints into frame, skids, and dives behind the sapling's thin trunk.

`done_when` (review/ep2-picks/done-definitions.yaml, beat 02):

> he ARRIVES and GOES DOWN: entry, skid, dive, in that order and legible as one
> continuous move. Note the plate must already contain the sapling — every take
> that named a sapling not in frame grew a tree instead.

Recorded fault to test against: *"the frame goes nearly EMPTY by mid-clip — he
sprints out of shot instead of skidding and diving. A viewer cannot see the beat
happen at all."*

The motion prompt actually rendered (identical for all 16 seeds):

> He stays in the middle of the frame the whole time. He runs a few steps and
> drops flat to the ground. \<style tail\>

### Beat 03 — BAD COVER (`03-bad-cover-LTX-st-*.mp4`)

node.md script line:

> The scavenger crouches behind a trunk that hides roughly one-sixth of him.

`done_when` (beat 03):

> he crouches and the COVER IS COMICALLY INADEQUATE — the trunk hides a fraction
> of him and the joke is visible without dialogue. A crouch that actually
> conceals him fails the beat.

Two faults are on the record and **they contradict each other**. Judge what you
see, not the record:

- older: *"he ends small at the frame edge beside the sapling"*
- newer (charged to the plate): *"all five arms of its earlier wave ended with
  the figure enlarged and cropped at the waist, feet gone"*

The motion prompt actually rendered (identical for all 15 seeds):

> Crouched right down low, knees folded up, head down. \<style tail\>

## The plates (verified identical across every seed of each beat, by MD5)

- **beat 02 plate** — a bald big-eared goblin child, greenish, in a grey-green
  shirt and dark shorts, standing centred and still, head tilted down, hands
  together at his chest, FULL BODY with bare feet visible on grass, sunlit green
  field behind. **THERE IS NO SAPLING AND NO TRUNK ANYWHERE IN THE PLATE.**
- **beat 03 plate** — the same character, standing centred and still, arms at
  his sides, full body, boots on grass. Two tiny two-leaf sprouts at the lower
  LEFT and lower RIGHT frame edges, each a few inches tall. **THERE IS NO TRUNK
  BEHIND HIM AND NOTHING HE COULD BE BEHIND.**

Both plates are at `pipeline/measured/judge-0817-b02b03/PLATE-b02.png` and
`PLATE-b03.png`. Open the one for your beat before you read any strip, so you
know what frame 0 is and can say what changed.

## Report format — one block per clip, exactly these fields

```
clip: <name>
seed: <the number in the filename>
picture_changed: <YES/NO + what visibly differs between frame 0 and the last
                  frame. This is NOT the same question as the next field.>
action_performed: <YES/NO/PARTIAL + name the movement you can see, with the
                  source frame indices where it starts and ends. For beat 02:
                  does he RUN (legs alternating, body translating or gait
                  cycling) and does he GO DOWN (torso to ground)? For beat 03:
                  does he FOLD from standing to a low crouch?>
done_when_verdict: <PASS / FAIL + which clause of the beat's own done_when
                    fails. Beat 02's clauses: entry, skid, dive, one continuous
                    move, sapling present. Beat 03's clauses: crouches, cover
                    comically inadequate, joke legible without dialogue.>
framing: <where the figure is at frame 0, mid, and end. Does any part of him
          leave the frame? Is he cropped, and at what body part? Are his feet
          in frame at the end? Say what you SEE — do NOT claim the camera
          zoomed or pushed in; that is a scale claim and needs an instrument.>
faults: <every defect you can see: limb melt, extra limbs, face collapse,
         identity change, background swim, banding, dead air, hard cut between
         two ADJACENT frames (say the two indices).>
notes: <anything that contradicts the recorded fault for this beat>
```

## Rules, non-negotiable

- **Do NOT quote depth or cadence.** Both are retired. Depth is *inverted* (a
  full stand-up scores 0.290, a zero-motion clip 0.516). Cadence aliases every
  odd hold period to exactly 1.00x. The coldread output prints cadence on a line
  that says RETIRED — do not put that number in your report.
- **Hold period and terminal freeze are two different numbers.** Do not compute
  either; a separate instrument does. If you SEE a run of identical pictures,
  say which frame indices, and call it what it is.
- **No camera-scale claims** ("it zooms", "it pushes in", "the camera pulls
  back") without an internal control. You have no instrument. Describe what is
  in frame and where instead.
- **A hard cut only counts if the two frames are ADJACENT indices.** Check the
  labels before you call one.
- **One take in three failing its action is the expected base rate.** Do not
  soften a FAIL to make the pile look better, and do not invent a fault to look
  rigorous.
- Read every strip sheet. If a clip has 5 sheets, open 5.
- $0, no GPU, no renders, no enqueue. Read-only.
