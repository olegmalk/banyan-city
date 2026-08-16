# Loop cycle 018 — the engine moves a figure's body in 12 of 12, so the limit was never the engine

**Opened and CLOSED:** 2026-08-16 · **Source:** the twelve beat-17 clips rendered
2026-08-15 (`ep2-b17-{full,rise,turn}-s{1..4}-0815`), which had sat unjudged with no
verdict recorded anywhere. No GPU was used to reach this finding — the renders were
already paid for.

> ### ⚠ CORRECTION, 2026-08-16 — read before you quote "12 of 12 passing"
>
> **This document calls all twelve cells "passing". Against the bar the job specs
> actually wrote, that is TRUE and the measurement below is sound. Against beat 17's
> `done_when`, it is FALSE.** A later frame-by-frame audit of all 97 frames of each of
> the four `full` cells found **0 of 4 brush the cloak**.
>
> **The twelve passed the STAND. The BRUSH was never tested by anything in this
> cycle.** Everything below measures head-top rise and lateral head travel — a stand
> and a turn. No measurement in this document looks at the hands at all.
>
> The gap is in the specs, not in the arithmetic: **the specs' pre-registered bar was
> narrower than the beat's own `done_when`.** The bar was "hips leave the grass AND head
> crosses the frame midline" — **two verbs, both whole-body.** Beat 17's `done_when` in
> `review/ep2-picks/done-definitions.yaml` is **three**:
>
> > `stand, brush, turn — a departure. NOTE the turn takes his face away from the lens
> > by design, so the staging law does not apply here: this is the one beat where
> > turning away IS the action.`
>
> **That gap is how a three-verb claim got printed off a two-verb clip.** Nothing below
> is retracted and nothing below is rewritten — the stand-up result is real, and its
> detector was falsified by overlay, which is why it is trustworthy. What is withdrawn
> is only the word *passing*, wherever this document applies it to the beat rather than
> to the specs' bar. See **"The brush was never measured"** near the end.
>
> **Beat 17's `done_when` is NOT reworded by this correction.** It was pre-registered on
> 2026-08-15 from `node.md`, before these clips existed, precisely so it could not be
> bent to fit them. A bar that gets loosened to match the footage certifies nothing.

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

**Scope, added 2026-08-16:** this heading is exact and it stays. *Stands up* is what was
measured and what 12 of 12 did. It is **not** "12 of 12 perform beat 17" — the brush was
not measured here, and 0 of 4 `full` cells do it. See the correction at the top.

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
   → **2026-08-16: this one is no longer a hypothesis.** Three lines of evidence
   converged on it, one of them *inside these very clips* — see "The converged finding"
   below. Hypotheses 1 and 2 remain untested.

Beat 06 asks a chest-cropped two-figure frame to turn a prop in the hands. Beat 17 asks
a wide single-figure frame to stand a body up. That is a composition-and-plate
difference, not an engine difference, and it is testable.

## The brush was never measured — and when it was, it is 0 of 4

**Added 2026-08-16, after the audit this cycle predates.** Every number above is a
head-top row or a head centroid. **Not one measurement in this cycle looks at a hand.**
The brush clause of `done_when` was therefore not scored, not failed, and not passed —
it was **absent from the instrument**, which is a different and more dangerous thing
than a miss, because an untested clause reports as silence and silence got read as
assent.

A frame-by-frame audit of **all 97 frames** of each of the four `full` cells:

| cell | stand | turn | **brush** | what the arms actually do |
|---|---|---|---|---|
| `full-s1` | ✅ | ✅ | **✗** | arms unfold, drop to the sides |
| `full-s2` | ✅ | ✅ | **✗** | arms unfold, drop to the sides |
| `full-s3` | ✅ | ✅ | **✗** | hands come to rest on knees / belt |
| `full-s4` | ✅ | ✅ | **✗** | cloak contact **without traversal** |

**4 of 4 stand and turn. 0 of 4 brush.** In every cell the arms unfold and drop to the
sides, or the hands settle on the knees or the belt. The `full-s4` cell is the one worth
naming precisely: there **is** hand-to-cloak contact, but no travel across the cloth —
the cloak moves because it is draped on a body that is rotating. **That is drape plus
body rotation, not a stroke**, and it is exactly the F6 failure mode
(`contact without traversal`) that beat 17's insert-plate spec names in advance. A
changed picture is not a pass.

So beat 17 stands at **two of its three verbs**, from a bar that only ever asked for the
two it got.

## The converged finding: this engine renders gross whole-body motion and drops small in-hand actions

**Recorded 2026-08-16.** Three independent lines of evidence arrived at the same shape
on the same day, and hypothesis 3 above is no longer a hypothesis:

1. **12 of 12 stand-ups** — this cycle. A gravity-driven whole-body displacement, on a
   wide plate, every single time.
2. **Two small-in-hand arms on the same plate, frozen f0→f96**, with only clouds and a
   bird moving. Same plate, same engine — the only change is that the requested action
   is small and in the hands.
3. **4 of 4 stand-and-turn with 0 of 4 brush, inside single clips.** This is the
   strongest of the three because it is *within* one clip: the same 97 frames contain a
   whole body rising and an in-hand action that does not happen. No plate difference, no
   prompt difference, no seed difference can explain it — **the engine did the large
   motion and dropped the small one out of the same instruction.**

**This also explains beats 06, 08 and 10**, which have resisted every lever tried on
them. All three ask for **small in-hand prop manipulation**: rotating a board held at
the chest, and the equivalents in 08 and 10. They are not failing for want of the right
wording. They are asking this engine for the one class of motion it demonstrably drops.

**The implied fix is UNDER TEST, NOT A RESULT:** *make the small action the largest
motion in frame* — so the in-hand action stops being the small thing and becomes the
gross thing. A lane is running that now. **Do not cite it as a finding, do not build on
it, and do not re-file blocked specs against it until it reports.** It is the obvious
move, and the obvious move is exactly the kind this repo has printed as fact before
measuring.

## What this releases

Beat 17's pre-registered fallback resolves the *other* way: the seated plate is the
RIGHT approach. **The ep2 cut had no beat-17 take at all and now has twelve passing
ones**, so the beat moves from "no plate, no take" to a pick among candidates — a
steward call with reasons, not a taste verdict (R4 stays with the author).

> **CORRECTED 2026-08-16 — the sentence above is left standing, and "twelve passing
> ones" is wrong.** They are twelve takes that pass the *specs' stand-only bar*; **none
> of the four audited passes beat 17's `done_when`.** What genuinely releases is
> narrower and still worth having:
>
> - **The seated plate is vindicated.** The pre-registered fallback ("if he never leaves
>   the ground in any of the twelve cells, animating beat 17 from a seated plate is the
>   wrong approach") resolves the good way, and that is untouched by the brush finding.
> - **The beat moves from "no plate, no take" to "footage that misses its bar"** — which
>   is a real advance over nothing, and is how the 2026-08-16 demo cut labels it: in the
>   cut, marked as short of what the beat asks for, deliberately not green.
> - **It does not move to "done".** Picking a best-of-twelve remains a steward call with
>   reasons (R4 stays with the author), but there is now a named defect to pick
>   *against*, and no pick closes the beat while 0 of 4 brush.
