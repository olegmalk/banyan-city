# beat 17 — THE GESTURE-UNDERWAY INIT. Bar and stop rule, written before any pixel exists.

2026-08-17. Written and committed BEFORE the init is built and BEFORE anything is
enqueued, so that no result can be talked into the answer this lane would prefer.

## Why this exists, and what has already been eliminated

Beat 17 is GOODBYE — "The scavenger stands, brushes off, and turns to go."
`brushes off` is in the approved script line `002b-t0-c` (`approved_by: founder`).
The brush has never landed. What has been eliminated, all of it by measurement
already in the repo, none of it by this lane:

1. **The plate is not the cause.** `503e40be` verified in bytes (sha 74e8eccf,
   pulled from `origin/farm-results-rtx5090` and hashed) and then in pixels that
   the init behind the eight failing `full` takes is ALREADY a goblin seated on
   grass, knees up, **both hands resting empty on the near knee**, no prop in
   frame, open field, crown at y=510 of 1280 (40% headroom). The two plate faults
   named in `steward-picks-0815.yaml` (`HE IS ALREADY STANDING AT FRAME ONE IN ALL
   EIGHT`, and every candidate arming his hands) are real but belong to the
   2026-08-15 `idfix` candidates, which are **not** the plates the failing takes
   used. A seated, hands-empty, outdoors, high-headroom init has therefore already
   been tried, and it produced **8/8 stand-and-turn, 0/8 brush**.
2. **Size in frame is not the lever.** `ep2-b17-bigbody-s20260911..14-0817` ran
   four fresh seeds on a byte-identical composition and returned **0 of 4**,
   below the kill line those specs pre-registered. The causal claim "stay in
   distribution while making the action as large as that frame allows" is dead.
   The one clip that ever brushed is real and remains real, which puts the
   engine's rate at about **one in five** — indistinguishable from the base rate
   six earlier lanes were already fighting.
3. **Isolating the action does not help.** The brush asked for ALONE, at the same
   seed, byte-identical otherwise: **0 of 2**.

Every one of those attempts asked the engine to **INITIATE** the gesture. Not one
has asked it to **CONTINUE** one. That is the single untested distinction left,
and it is the one the composite mechanism actually speaks to: the proven finding
is that structure put INTO the pixels survives, because the sampler *finishes*
rather than *invents*. Applied to motion, the question is whether an init in
which the hand is already on the cloak, mid-stroke, buys a stroke the engine will
not start on its own.

## The question, stated so that either answer is useful

**Does this engine continue a hand-on-cloak brush that is already underway at
frame one?**

- **If yes** — the defect is INITIATION, not execution. The remedy would be a
  staging change (open the shot mid-gesture, or cut the beat so the brush is
  already running). That remedy is an **R4 authorship call and not this lane's**;
  this lane would only have shown that it is available.
- **If no** — the engine cannot sustain hand-on-cloth traversal from any plate,
  at any size, initiated or continued. That closes the last instrument a lane
  can reach and makes the disposition of `brushes off` unambiguously the
  founder's decision.

## The init — no drawing, no compositing, no decal risk

The mechanism is "put the structure in the pixels instead of asking for it in
words." The obvious way to get a hand on a cloak would be to composite or draw
one, and this beat is the **worst case for FAIL-DECAL** because it is about
hands, in a dialect where a drawn hand reads as a sticker. So the structure is
taken from the engine's own output instead: **frame 026 of the one clip that ever
performed the brush**, `farm-out/ep2-b17-bigbody-motion-0816/17-goodbye-bigbody-LTX-handbrush.mp4`
on `origin/farm-results-rtx5090` (clip sha256
`3aaa6ad34b54f495c7a7e679dac460abc683a49adc0c61d21d35ed2ff053b7f4`). It is
already 704x1280, already in dialect, already in distribution, and needed no
seam, no mask and no inpaint. This is the same mechanism as the composite
pattern, with none of the drawing risk — stated plainly because it is a
substitution of tool, not of principle.

**Frame 026 was selected by rule, not by eye-appeal.** The rule: the peak of the
winner's FIRST stroke, i.e. the earliest local maximum of the committed tracker's
travel curve. Measured with `pipeline/b17_hand_track.py` (validated on this
machine against that lane's published numbers — peak frame 64 exactly, control
2.2 px to f040): travel rises 2.0 px at f016 → 117 px at f022 → 200 px at f024 →
**221 px (1.23 hand-widths) at f026**, holds ~220 to f034, falls to 79 px by
f050, then out again to 237 px at f064. f026 and f028 tie at 221 px; the earlier
is taken. The other-hand control reads **1 px** at f026, so the pose is genuine
articulation and not a camera move. Confirmed by eye at 2x on a committed contact
sheet: a formed hand with discrete claws laid across the dark cloak, arm extended
across the body, the other hand still down at the knee.

So frame one of this probe holds: **seated, outdoors, headroom, one hand in
contact with the cloak at full extension of a stroke, the other hand at the
knee.** Hands are not empty — deliberately, and that is the whole variable.

## The bar — efd7bafa's, verbatim, with ONE declared forward tightening

Scored on `pipeline/b17_hand_track.py`, `HAND_W = 180`, bar at 1.0 hand-width,
peak excursion relative to the cloth, which is the same tool and the same
statistic the winner and all four reseeds were judged on. Consistency of scoring
across the winner, the reseeds and this probe matters more than the scoring being
strict or generous.

- **M1** a hand in contact with the cloak.
- **M2** that hand TRAVELS at least one hand-width (180 px) across the fabric
  RELATIVE TO THE CLOTH. Travel in FRAME is the number that means nothing.
- **M3** the hand moves, not the camera: frame edges, horizon and cloth folds
  must not translate with it. Landmark NCC on SHOE_L, SHOE_R, GRASS_TL.
- **M4** a continuous path readable across consecutive frames.

FAIL is any of **F1** frozen, **F2** cloth-only, **F3** camera-only, **F4** morph
or teleport, **F5** scene break, **F6** contact without traversal (an explicit
FAIL, never a partial pass), **F7** body-instead-of-hand (a stand-up is not a
pass, a head turn is not a pass). Whether he stands is recorded separately and
scored as nothing.

**F4 precedent is binding and is not being softened.** Travel is read at the last
frame in which the hand is a formed hand with discrete claws. If the 1.0 bar is
crossed only after the hand loses its anatomy, that is **F4 MORPH and a FAIL** —
exactly as `ep2-b17-bigbody-s20260912-0817` was scored (270.2 px = 1.50 hw, but
86 px = 0.48 hw at f003, the last frame with formed hands). The converse is
honoured too: the winner's late claw-softening was scored NOT-F4 because its
hands stayed followable on a continuous path, and that ruling is not revisited.

**THE ONE TIGHTENING, DECLARED FORWARD AND WITH ITS REASON.** M1 now requires
contact **at the frame where M2 is met**, not merely at frame 0. This is
necessary because the geometry changed: efd7bafa's bar was written for a clip
starting with hands in the LAP, where any 180 px of hand travel had to be travel
toward and across the cloth. From THIS init the hand starts at full extension on
the cloak, so a hand that simply **drops back to the lap** would clear 180 px of
excursion while leaving the fabric — traversal without a brush. Requiring contact
at the measured frame closes that loophole. It is a tightening, it is registered
before any pixel exists, and it will not be relaxed afterwards. A **return
stroke** across the cloth passes and is meant to; a **release** does not.

**Failure is fully reachable, and this is the point of writing it down.** A mask
over only the empty region guarantees its result and measures nothing; a bar that
frame one already satisfies would be the same error. Under this bar frame one
satisfies **M1 only**. M2 is zero at frame 0 by construction — excursion is
measured *from* the init pose — so a frozen clip scores **F1** and the engine's
signature failure on this beat is the single likeliest outcome. A drop to the lap
scores **F6/M1**. A stand-up scores **F7**. A dissolve scores **F4**.

**Named prior for F5.** The init inherits the bigbody plate's marginal empty
region — the largest flat background patch is about 114x240 px against a head of
about 230x230. That axis has broken on this checkpoint four times (beat 08's
colossus in a reserved sky; beat 08 r4 showing that naming the invited noun in
the negative removes it not at all; the tight insert pulling the camera back to
manufacture a hole and putting a face in it; this lane's own r2 plate growing
three goblin heads in a flat grass margin). If a face, a second figure or a scene
break appears, that patch is the FIRST place to look — and it is a named prior,
not an excuse. **An F5 is still an F5.**

**Not computed and not quoted:** depth (retired AND inverted — stand-up 0.290,
zero-motion 0.516, bird-only 0.376) and cadence (odd hold periods alias to
1.00x).

## Stop rule, pre-registered and binding

**ONE SAMPLE FIRST.** One seed, one clip, ~11 minutes, $0 on the idle local card.
It is a recipe sample, not a measurement of rate: it establishes that the init
loads, that the clip renders, that nothing arrived in the 114x240 patch, and
whether the continuation happens at all.

Then **STOP AND REPORT, in every branch.** Specifically:

- **Sample FAILS the bar** → **STOP. No reseed, no second wording, no recipe
  sweep, no new plate.** Beat 17 has already burned eight seeds at zero and four
  more at zero on the size axis; the lesson recorded there is to change
  instrument, not to climb. This lane's instrument will have been spent, and the
  finding — that the last lane-reachable instrument does not get there — is
  handed up as-is.
- **Sample PASSES the bar** → **STOP ANYWAY, and do not call it a lever.** This
  is pre-registered because today's own evidence forbids the alternative: the
  bigbody lane established that at a ~1-in-5 base rate, **n=1 cannot tell a
  lever from a lucky draw**, and it killed a claim that had already been reported
  to the founder on exactly that mistake. A single pass here is consistent both
  with continuation being real and with the base rate. It would earn a four-seed
  reseed on the byte-identical init with the 3-4/4 real, 2/4 ambiguous, 1/4 KILL
  rule — and whether to spend that, or to restage the beat, is the founder's
  call, not this lane's.

Under no branch does this lane conclude that the brush is impossible, and under
no branch does it concede `brushes off`. Dropping the verb is a rewrite of an
approved script line: **R4, the founder's alone.**

## Scope

Engine probe, never to be cut into an episode. Sidecar stamped
`approved: false`, `provisional: true`, `is_show_content: false`, `cost_usd 0`.
`shots.md`, `pipeline/wave-drafts.yaml` and `pipeline/canon.yaml` are UNTOUCHED.
No `plate_ack`, no `gate:`, no `gate_ref:`. Opening a shot mid-gesture changes
how the action reads, which is authorship; this lane measures whether the engine
*can*, and does not propose that it *should*.

---

## RESULT, 2026-08-17 — FAIL. The answer is NO.

`ep2-b17-gestureinit-0817`, one seed (20260917), 11 minutes, $0. Clip
`0f38b4eb`, init `340427011b`, prompt `05942938` and negative `50fb304c` —
the same prompt bytes as all five prior clips, so **only the init differed**.
Full scoring is in the spec's `outcome:` block; this is the answer to the
question the bar was written to settle.

**Scored as written: peak excursion 176.6 px = 0.98 hand-widths at f055,
against a 1.0 bar. It misses by 3.4 px and it is a FAIL.** 0.98 is precisely
the number a lane is tempted to round up, and rounding it is how eight of
twelve "passes" on this episode became zero of twelve usable. At the last frame
holding a formed hand with discrete claws (~f043–f045) travel is 0.87–0.88 hw,
so it fails on that reading too. M1 passes by construction, M3 passes on
landmarks (SHOE_L 8 px at NCC 0.98, SHOE_R 4 px at 0.99, GRASS_TL 14 px at
0.97), M4 passes. **M2 — the only axis that separates a brush from a pose
change — fails.**

**And the near-miss on the number is not a near-miss on the action.** Travel
ramps monotonically from 0.00 hw to 0.98 hw over f000–f055 and then plateaus at
0.92–0.98 for the remaining 41 frames. A brush oscillates — the winner ran 231
px at f030, 101 at f048, 250 at f064. There is no return stroke, no second
pass, no oscillation at any amplitude. **The engine moved the arms once into a
new resting position and held it for the back half of the clip.**

### What this settles

**Initiation is NOT the defect.** The probe handed the engine the gesture
already underway, in its own dialect, from the one frame it ever brushed in,
with the hand and head larger than anywhere this beat has been tested (head
~27% of frame height, against 16.0% as the highest PASS in the stills
calibration). It still did not complete a stroke. Combined with what was
already on the record — a seated, hands-empty, outdoors, 40%-headroom plate at
0/8; four fresh seeds on a byte-identical composition at 0/4; the action asked
for alone at 0/2 — **the plate route is exhausted. No plate a lane can build
reaches this verb on this checkpoint.**

One contrast is worth keeping, because it is the clearest statement of the
failure: on the WIDE plate this engine substituted STAND + TURN AWAY eight
times out of eight; on this TIGHT plate, with no room to stand, it substituted
a two-armed settle-and-hold. **The substitution follows the framing, but it is
always a substitution.** Taking away the room to stand did not buy the brush —
it only changed which non-brush arrived.

### What this does NOT settle, and what is not this lane's to say

**The brush is not conceded and this lane has no standing to concede it.**
`brushes off` is in the approved script line `002b-t0-c`. The finding is that
the INSTRUMENT does not reach it, not that the verb should go. The three
remaining routes are all authorship or infrastructure, and every one of them is
above a lane:

1. **Accept the rate.** One clip in five did perform the brush and that clip is
   real. "Render five and pick" is a production-cost decision — R4's.
2. **Restage.** Re-cut beat 17 so the brush is not required in the same shot as
   the stand, or open mid-gesture. An R4 rewrite of an approved line.
3. **Change the engine.** LTX-2.3-Distilled is the constraint being measured
   here, not beat 17. A checkpoint with better fine-hand articulation is an
   infrastructure question, and lanes are already on LTX weights and distill.

**No further beat-17 rung is filed, and that is deliberate rather than
neglectful** — the stop rule above pre-registered exactly this branch, and a
fifth wording on a fourth plate would have no consumer. The next move on this
beat belongs to the founder.

### One thing the bar could not see — reported, not bent

M2 measures the **excursion magnitude** of one hand. It cannot distinguish a
hand sweeping ACROSS CLOTH from a hand travelling to a new resting position,
and the only reason that did not matter is that this clip fails M2 anyway. A
future bar on this action wants a direction or cloth-relative displacement
term. **This is a forward-only note for whoever writes the next bar; it is
applied to nothing retroactively and no number is minted for it here.** The
obvious candidate was tried and is untrustworthy: centroid separation between
the two arm+hand blobs reads 282 px at f000, 232 px minimum, 296 px at f096 —
it says the hands never converge, while the pictures plainly show them
overlapping in the image plane, because each blob is arm+hand and the two arms
enter from opposite sides. Six measures have been retired for cause on this
beat this week; a seventh is not being minted on the strength of one clip.
