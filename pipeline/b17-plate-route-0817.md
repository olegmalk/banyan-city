# Beat 17's plate route — already spent, and the brush is NOT conceded

**2026-08-17, the bark/composite lane.** Assigned: build a composited init that is
*seated, hands empty, outdoors, with headroom*, on the reasoning that beat 17's
plate blocks two of its three verbs. **That plate already exists, the failing takes
already ran from it, and the brush still did not appear.** Zero pixels were
rendered to establish this, and no seed was spent.

## 1. The premise, and why it is two days stale

The plate faults are real but they belong to the **2026-08-15 idfix candidates**
(`steward-picks-0815.yaml`: *"HE IS ALREADY STANDING AT FRAME ONE IN ALL EIGHT"*,
and all eight arm his hands). Those are not the plates the `full` takes used. The
**2026-08-17** cold-read in `done-definitions.yaml` §`17.full_arm_read_0817`
supersedes them:

> 4/4 STAND and 4/4 TURN AWAY … **0/4 BRUSH.** With the 0-of-4 already recorded for
> s1..s4, the `full` wording stands at **8/8 stand-and-turn and 0/8 brush**.

## 2. The init those eight takes ran from — verified in bytes and in pixels

`ep2-b17-full-s5-0816.yaml` asserts `--sha256 74e8eccf9653…` on
`farm-out/ep2-b17-full-s1-0815/b17-init-704x1280.png`. I pulled that file out of
`origin/farm-results-rtx5090` and hashed it: **`74e8eccf9653edadd9cdd70b419b9a325932bede3238ace06a2308fb95452a6a`,
an exact match**, so this is the init, not a picture like it. Then I opened it,
because a prompt asking for something is not a render delivering it.

Its own sidecar positive (`ep2-b17-mac-plate-0815/17-goodbye-mac-seated-r1.yaml`)
asks for *"sitting on grass in an open field, **empty hands resting on his knees**…
small figure low in frame; vast blue sky and clouds fill the space above him"*, and
fences `standing`, `walking`, `broom`, `spear`, `staff`, `mallet`, `hammer`,
`sword`, `stick`, `basket`, `holding object` in the negative.

**The pixels deliver all four conditions:**

| Condition asked of me | In the init already |
|---|---|
| seated | **yes** — sitting on grass, knees drawn up |
| hands empty | **yes** — both hands rest on the near knee, nothing held, no prop anywhere in frame |
| outdoors | **yes** — open field, hills, sky |
| headroom | **yes, 40%** — his crown is at y=510 of 1280 |

## 3. So neither plate fault can be the brush's cause

The two faults a composite would fix were **both already absent** when the brush
failed 8 times out of 8. And the pick lane's own measurement closes the last door:
the engine drops the brush **0 of 2 when it is asked for ALONE at the same seed,
byte-identical otherwise**. With the action isolated, nothing competing for it, on
a seated plate with empty hands and 40% headroom — still no brush.

**A composited seated/hands-empty init therefore has nothing to add. The plate
instrument is exhausted for this verb**, and that is the stop rule being honoured
rather than climbed: beat 17 has already burned 8 seeds at zero, and this route
would have been the ninth through eleventh.

**The brush is not conceded here.** What this says is narrower and it should not be
read as wider: *the plate cannot reach it.* `brushes off` is in the approved script
line (`002b-t0-c`, `approved_by: founder`), so dropping it is an R4 rewrite and
nobody's call but the founder's — I am not proposing it, I am reporting that the
instrument I was handed cannot get there.

## 4. What the pattern can and cannot do here — stated plainly

`composite-init-pattern.md` pins **attributes in a still** by putting structure in
the pixels and denoising at 0.30. Beat 17's defect is **a motion engine omitting an
action**. A composited still cannot make LTX perform a gesture it declines to
perform; there is no strength setting on a video model's choice of verb. The
pattern's own §1 test applies and comes back negative: this is not an attribute
with no continuous encoding, and it is not a band collision — it is an omission.

**The one composite-shaped idea that remains distinct** — and it is named rather
than filed, because two things about it are not mine: an init that already holds
**the first frame of the gesture** (near hand on the cloak), so the clip has to
*finish* a brush rather than *invent* one, which is exactly this pattern's logic
ported from stills to motion. Its two problems: (a) it means drawing a **hand** in
this dialect, and §5 of the pattern is a list of composites rejected for far
easier shapes than a hand — this is the worst case for FAIL-DECAL, and the hand law
makes it load-bearing on the beat that is *about* hands; (b) "already brushing at
frame one" changes the action's reading from *stand → brush → turn* to something
else, which is an authorship question and R4's.

## 5. The one number I can add: size in frame, against a calibrated reference

The live variable the pick lane isolated is **SIZE IN FRAME** — this engine renders
gross whole-body motion (12 of 12 stand-ups) and drops small in-hand actions.
This lane owns the only measured scale reference in the repo, so here it is beside
beat 17's actual init. Head height as a fraction of frame height, measured by
segmenting green skin (rule `G-B>60 & G>150 & R<G-20`, largest head component):

| Frame | Head height | Outcome |
|---|---|---|
| **beat 17 init `74e8eccf`** | **11.4%** (146px of 1280, bbox x285-395 y510-656) | 0/8 brush |
| beat 08 wide (bark) | 10.3% | FAIL-MATERIAL |
| beat 08 tight (bark) | 15.6% | FAIL-MATERIAL |
| beat 06 (bark) | 16.0% | **PASS** |

Beat 17's init sits just above the size that failed for bark and well below the band
where bark's fine detail arrived, which **agrees with the pick lane's conclusion,
reached independently, that size in frame is the variable worth spending on**. The
`bigbody` and `insert` specs are aimed at the right thing.

**And the caution that comes with it, from this lane's own failure.** That table is
a reference point, not a law, for two reasons. It measures the **stills** model
drawing cel detail, while beat 17's defect is a **video** model choosing a verb —
different engines. And on beat 08 the scale hypothesis was tested and **died**: a
plate staged tighter landed on beat 06's own register (15.6% against 16.0%) with a
board 1.65× the pixels, and the material still did not arrive. So a bigger body in
frame is the best remaining lever *and* it has a precedent for not working. Whoever
runs `bigbody` should know both halves before spending four seeds.

## 6. Flag for whoever re-renders this plate

The seated plate's own positive contains **"vast blue sky and clouds fill the space
above him"** — naming the sky positively, which is the phrase class recorded as
summoning a colossus on this very beat. It happens to have rendered cleanly here,
but a reseed of this wording carries that risk, and the headroom this plate needs
does not have to be bought with a sky noun.

---

**Cost: $0. No GPU, no seeds, no provider, nothing enqueued, nothing re-fired.**
Nothing in the `bigbody`/`insert` lane was touched. One file was read out of the
results branch and hashed; the queue was not involved.
