# `/review/ep2-b13-shade-0820` — what fires on each answer

The card asks one taste question with two answers, and as of 2026-08-20 **both
have pixels**:

> Does this satisfy *"tips his head sideways into the sapling's hand-sized patch
> of shade"* — or may the plant be drawn **taller than canon in this one shot**
> so the shade can actually reach his face?

---

## On **"A"** / *"that's the shade, ship it"*

**File nothing. Enqueue nothing.** The current take already ships.

Beat 13 is in `review/ep2-demo-0820` right now as best-available with its fault
named. "A" means the shade clause is written off, the beat closes, and the only
work left is bookkeeping: record the verdict in the card, in `review/inbox.yaml`,
in `pipeline/work-ladder-0819.md` and in the beat-13 row of
`review/ep2-demo-0820/sources/picks-0820.yaml` (`why: carry-forward` → the
clause is retired by ruling, not by measurement), and delete this directory.

There is deliberately no spec here for A, because A's answer is *stop*, and a
pre-staged rung for "stop" would be a rung nobody asked for.

## On **"B"** / *"draw it taller in this one shot"*

Three things fire, in this order. All three are written; none is enqueued.

1. **CANON GETS THE EXCEPTION, AS AN EXCEPTION.** Before any render, add the
   one-shot exception to `pipeline/canon.yaml` under the sapling-height subject —
   scoped to beat 13 of node 002b, with the ruling date and the reason. This is
   first on purpose: the standing rule is that the sapling is ~40 cm and always
   shorter than he is in *every* beat of 002b, and an exception that lives only in
   a job spec is a drift. `check_canon_drift.py` reads canon; it does not read
   review cards.
2. **`derive-b13-tallmotion.py`** — emits `pipeline/jobs/ep2-b13-tallmotion-0820.yaml`
   off the landed still, computing its sha at emit time rather than carrying a
   stale one. Then `python3 pipeline/box_enqueue.py pipeline/jobs/ep2-b13-tallmotion-0820.yaml`.
3. **Judge it against the b13 bars MINUS the shade clause's instrument.** See
   below — this is the part most likely to be got wrong by a lane reading only the
   spec.

### What the motion rung is, and what its one variable is

It is `ep2-b13-shadelit-0820` — the b14 crf-10 LTX recipe, seed and words
unchanged — with **the init swapped** for the taller-plant plate. One variable.
Rung 4 is a true control for it, which is the whole reason not to touch anything
else in passing.

### The shade clause: score it BY EYE, and do not resurrect its instrument

G8 (`THE_PLANTS_SHADE_IS_ON_HIS_EYES`) has a pre-registered numeric instrument in
`pipeline/jobs/ep2-b13-shadelit-0820.yaml`, and **that instrument is retracted by
its own author in the same file**:

> As written it PASSES, twice over … IT PASSES JUST AS HUGELY ON THE CONTROL …
> An instrument that passes on the clip already judged G8 FAIL is not an
> instrument.

The failure mode is the fixed-window one this repo has now retracted four times:
both probe bands read std 88–89 at f120 because his head has tipped right over
and neither box is on the thing it names any more. **Do not re-run it, and do not
write a new fixed-box version of it.** If B is ruled and the tall plant is in
frame, whether a readable patch of shade lands on his face is decided by opening
the frames — which is also why the question came to the author in the first place.

**The clauses that ARE scored on the motion rung:** H1 (the performance is not
given back), H2 (still seated, knees up, plant holds), H3 (the sideways tilt
survives), A5 (no exposure blowout, measured against this job's own f000), A2
(the ratified adult holds). Rung 4 passed four of those and missed H1's mean by
0.115 with its pre-registered `F-MOTION-COST` not firing; that is the number to
beat.

### The honest risk, pre-registered here rather than after the fact

The composite is `is_show_content: false` and so is its still sample. **A motion
clip built on it is the first artifact in this chain that could plausibly enter a
cut, and it must not do so on the strength of this ruling alone** — "draw it
taller" licenses the *staging*, not the take. The clip still has to pass the bars
above on its own, and it inherits the plate's cast frame for frame.

Second risk, visible in the still: at the framing beat 13 has, a plant tall enough
to reach his eye line has to be drawn in a 248 px corridor between the frame edge
and his face, so its two blades come out near-vertical and overlapping rather than
splayed. That is a property of the shot, not of the drawing, and if the author
dislikes how it reads the answer may be neither A nor B but a re-staged plate.

## Contents

| file | fires on | state |
|---|---|---|
| `derive-b13-tallmotion.py` | B | written, not run |
