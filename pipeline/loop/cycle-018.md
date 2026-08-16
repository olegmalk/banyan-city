# Loop cycle 018 — the engine moves a figure's body in 12 of 12, so the limit was never the engine

**Opened and CLOSED:** 2026-08-16 · **Source:** the twelve beat-17 clips rendered
2026-08-15 (`ep2-b17-{full,rise,turn}-s{1..4}-0815`), which had sat unjudged with no
verdict recorded anywhere. No GPU was used to reach this finding — the renders were
already paid for.

## Why these twelve mattered more than they looked

By 2026-08-16 **six independent lanes** had reported the same signature: the figure's
body never moves. Identical pose at f0 and f96, linework re-inked in place between
frames. Cycle 017 closed the same morning with a seventh instance — `ep2-b06-d1neg`,
depth 0.516, a guard who does not shift a shoulder for 97 frames.

The hypothesis forming across those lanes was that **this engine cannot move a figure
at all**, and a lane was standing up a minimal positive control to test it.

Beat 17 already contained that control and nobody had looked. Its bar was written into
every one of the twelve specs BEFORE the renders existed:

> "the goblin's hips leave the grass AND his head crosses the frame midline while he
> stays in the same field — no cut, no scene change, no camera move, no second figure.
> The finding worth reporting is either outcome: if he never leaves the ground in any
> of the twelve cells, animating beat 17 from a seated plate is the wrong approach."

Hips leaving the ground is a whole-body, gravity-driven displacement. **It cannot be
faked by re-inking, by a push-in, or by any metric artefact** — which is exactly what
the other six lanes lacked.

## THE RESULT: 12 of 12. Every cell stands up.

| arm | seeds | head-top rise (fraction of frame height) |
|---|---|---|
| `full` | s1-s4 | 39.7% · 37.5% · 30.2% · 34.1% |
| `rise` | s1-s4 | 35.0% · 33.0% · **29.2%** (weakest) · 30.8% |
| `turn` | s1-s4 | 31.1% · 35.6% · 29.2% · 32.0% |

All twelve open identically — head-top row 254 ± 1 — so all twelve genuinely start on
the plate. **The weakest cell in the set still lifts the head by 29% of the frame.**

### How the figure was found, and how the tool was falsified

Not eyeballed off a contact sheet. The plate is a vivid yellow-green goblin in a
purple-grey cloak against blue sky above a horizon, so above the horizon the only
strongly green thing in frame is the goblin himself:

    mask = (G > R + 8) & (G > B + 30) & (row < 0.62 * height)
      sky    B > G      excluded      cloak  B >= R > G   excluded
      cloud  R ~ G ~ B  excluded      grass  green, but below the row cut

Per frame: the topmost row carrying at least 6 masked pixels, and the centroid x of
the mask's top 18% band. Then — the step that matters — **the mask and the detected
head-top were drawn back onto the frames and looked at.** The red sits on the goblin.
A tool that reports a number nobody has falsified is the thing this repo keeps
getting burned by.

**It caught its own bug doing so.** The first version took `ys.min()` as the head top.
On `full-s4` frame 0 a handful of speckle pixels near the top of the sky set that
minimum to row 15 on a SEATED goblin whose head is at row 254 — and the clip's rise
silently came out as **0**, turning a complete stand-up-and-turn-away into a failure.
Two other cells were wrong the same way. Requiring a row to carry real width before it
counts as the figure fixed all three. *A sparse false positive on one frame is enough
to invert a verdict, and the only reason it was caught is that the overlay disagreed
with the number.*

### It is the body, not the camera

In every overlay the horizon line and the background mountains stay at a **fixed
height** while the goblin rises through the frame. A camera tilt moves the horizon and
the figure together; here only the figure moves. Camera *scale* is deliberately not
quoted anywhere in this cycle — the chained-NCC estimate rails to its search boundary
when the fit fails (c870f08f).

### It is continuous, not a cut

`full-s1` frames 38-49 read consecutively are a smooth eased rise: hips off the grass,
weight transferring onto the feet, spine straightening in small increments, no step
anywhere. The lowest min_ncc in the set (`full-s2`, 0.576) is the motion blur of the
goblin striding out of frame at the end, not a scene change. No cell contains a second
figure.

### The half of the bar that was degenerate, reported as such

**"His head crosses the frame midline" cannot be scored on this plate.** The head
starts 2.6 px from the midline (cx 173.4 against a midline of 176.0 at half-scale), so
whether it "crosses" is decided by sub-pixel jitter, and the literal count — 4 of 12 —
carries no information. The honest substitute is lateral head travel, which is large
in every cell: 102-255 px at half-scale, 29-73% of the frame width. Recorded here
rather than quietly scored, because a criterion that turns out to be undecidable
should be retired out loud and not converted into a pass or a fail.

## What this overturns

**The engine can move a figure's body. The six-lane signature is not an engine limit
and must stop being described as one.** Whatever is wrong with beats 06, 10 and 13,
"the model cannot animate a person" is not it, and no further lane should spend seeds
proving or assuming that.

**And depth is not merely blind to action — on this evidence it is inverted:**

| clip | real body motion | depth |
|---|---|---|
| `ep2-b17-full-s1` | a full stand-up, hips off the grass | **0.290** |
| `ep2-b06-d1neg` | none whatsoever | **0.516** |

The clip with the most genuine human motion in the repository scores well below the
clip with none. Depth answers "how deep is the hold" and nothing else. Ranking takes
by it selects against the thing we want. (Recorded in `judge_clip.py`'s docstring too,
where the next lane will actually meet it.)

## What it points at instead — the live hypotheses, none of them tested here

Beat 17 differs from the beats that fail in three ways, and they are now the
candidates worth a lane:

1. **One figure, not two.** Beats 06 and 10 are both two-guard beats, and their
   dominant failure was an uncommanded push-in that took the second guard out of frame.
2. **A full-body wide plate with headroom** — the action has somewhere to happen.
   Beat 06's plate is a chest crop; there is no room in it for a body to move.
3. **A large gravity-driven whole-body action** (standing up and leaving) rather than a
   small in-hand manipulation (rotating a board held at the chest).

Beat 06 asks a chest-cropped two-figure frame to turn a prop in the hands. Beat 17 asks
a wide single-figure frame to stand a body up. That is a composition-and-plate
difference, not an engine difference, and it is testable.

## What this releases

Beat 17's pre-registered fallback resolves the *other* way: the seated plate is the
RIGHT approach. **The ep2 cut had no beat-17 take at all and now has twelve passing
ones**, so the beat moves from "no plate, no take" to a pick among candidates — a
steward call with reasons, not a taste verdict (R4 stays with the author).
