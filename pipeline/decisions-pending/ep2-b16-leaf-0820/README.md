# `/review/ep2-b16-leaf-0820` — what fires on each answer

The card names a contradiction between two of the author's own rulings:

> Beat 16's brief asks for a **leaf-as-subject macro shot** — node.md: *"close on
> the sapling's leaf; the scavenger sits blurred behind it"*, hardened by the shot
> list to *"the leaf is the subject and he is depth"*. `canon.yaml
> sapling-cotyledon-shape`, from his 08-17 answer, rules out *"any leaf drawn as a
> feature … NO LEAF WHOSE SHAPE IS THE SUBJECT OF THE SHOT"*.

Both are his, and they ask for opposite shots. Beat 16 is one of episode 2's two
remaining slates.

---

## On **"restage"** — *say what the shot should be instead*

**File nothing. Enqueue nothing.** This is authored work and it is R4's.

A wider restage — both leaves, the whole plant as subject, him behind it —
satisfies canon *and* the beat's sense while dropping the clause the sampler has
refused three times. But the new staging is a sentence only the author can write,
and pre-staging a spec for a shot nobody has described yet would be writing his
answer for him and calling it automation. When the sentence exists, it goes into
`node.md` and `done-definitions.yaml` and a plate rung is filed off it the same
day.

**One thing that IS known and should be carried into whatever he writes:** the
wording ladder for the current staging is closed at three rungs, and the third
was the strongest negative this repo has produced —
`ep2-b16-...-r2` held the same 73 tokens, same host, same seed, and moved one
chunk to a different position, and **the composition did not change at all**. So
a restage has to change the *staging*, not the sentence order. Reordering is not
a lever here.

## On **"licence it"** — *this one shot may feature the leaf's shape*

Two things fire, in this order. Both are written; neither is enqueued.

1. **CANON GETS THE EXCEPTION, AS AN EXCEPTION.** Before any render, scope a
   one-shot exception into `pipeline/canon.yaml` under `sapling-cotyledon-shape` —
   beat 16 of node 002b only, with the ruling date and the reason, and with the
   general prohibition left standing. `check_canon_drift.py` reads canon and not
   review cards, so an exception recorded anywhere else is a drift waiting to be
   cited as precedent.
2. **`derive-b16-leafmotion.py`** — emits `pipeline/jobs/ep2-b16-leafmotion-0820.yaml`
   off the landed still, computing its sha at emit time. Then
   `python3 pipeline/box_enqueue.py pipeline/jobs/ep2-b16-leafmotion-0820.yaml`.

   > **STATUS, 2026-08-20: this script is NOT WRITTEN YET, and the reason is not
   > an oversight.** It cannot be written honestly until the 0.30 still has
   > landed and been looked at, for two reasons. First, a derive script asserts
   > the sha256 of the plate it conditions on, and that plate does not exist yet —
   > the sibling beat-13 chain shows the shape, refusing to run and printing the
   > command that makes its input rather than carrying a guessed sha. Second, and
   > more important: **if the still comes back a paste or a re-render, there is no
   > motion rung to pre-stage at all** — the next step becomes a strength rung,
   > which is a different job with a different variable. Writing the motion spec
   > before seeing the still would be pre-staging the outcome I want. The still is
   > queued; this line gets replaced by the script or by a note saying why there
   > is none.

### What the card's third option already bought, and what it did not

The large-leaf composite was named and costed on 08-20 and **deliberately not
fired**, on the ground that "spending it before his word would be answering a
ruling with a render." It has since been built and sampled once, as *card
evidence only* — `is_show_content: false`, never a cut init, canon unchanged. That
changes what the author is ruling on (he now sees the shot rather than imagining
it); it does not change what the ruling is.

**The pre-registered risk, and it is a real one:** beats 15/19/03/13 composited a
*small* plant into a plate (4.1 % of frame on beat 13) and let a 0.30 pass make it
belong. Beat 16 needs a **large object drawn in front**, over most of the frame,
and a 0.30 pass over that much of a picture is closer to a re-render than to an
inpaint. If the sample shows the leaf's shape or position not surviving the pass,
then "licence it" is ruled but **not yet buildable**, and the honest next move is a
strength rung — which is its own variable and must not be bundled into the motion
job.

## Contents

| file | fires on | state |
|---|---|---|
| `derive-b16-leafmotion.py` | licence | **not yet written** — blocked on the 0.30 still, see step 2 |

The canon-exception step (1) needs no artifact and is not blocked: it is a hand
edit to `pipeline/canon.yaml`, and it comes first whatever the still shows.
