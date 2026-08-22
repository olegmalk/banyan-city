# The goblin two-pass — how beat 13 got a pose and a face in the same frame

**2026-08-22, the wave lane.** Written because seven rounds of B2 produced one
recipe and four retired theories, and the next lane should inherit both.

## 1. The recipe, first, because it is short

    PASS ONE   inpaint_fruit.py
               --init   <flat grey 832x1216>          (fully noised; carries nothing)
               --mask-png <all-white 832x1216>        (every pixel is redrawn)
               --strength 1.0                         (every timestep runs)
               --pad-crop 0  --blur 0                 (hint magnification exactly 1.000x)
               --controlnet C:\banyan-farm\cnet-openpose-twins  --scale 1.0
               --control  <the beat's AGE B skeleton, head_frac 0.240>
               NO --lora
               prompt: the beat, NO pose word, NO face term,
                       and a NAMED LIGHT KEY

    PASS TWO   inpaint_fruit.py
               --init   <pass one's own output, sha-pinned>
               --mask-png <the same all-white mask>
               --strength 0.75                        ← the number that matters
               --controlnet ... --control <the SAME skeleton> --scale 1.0
               --lora bnyjerry-sdxl-v2.safetensors --lora-weight 0.8
               --lora-sha256 4340857d02f17dbfa50c66e0a2d8f4dc3ffebb4fad1621bb3f59242e61bfeb8b

An all-white mask at strength 1.0 **is** txt2img-with-ControlNet; the same
driver at strength 0.75 **is** img2img-with-ControlNet. One driver, two passes,
`$0`, about 25 seconds each on the 5090.

Sample that passed both halves: `twopass2-b13seat-s075`, beat 13's own seat.
Judged at 1:1 against `taste/refs/goblin-canon-founder-0821.png`: broad low
dome, near-horizontal pointed ears with the dark inner shell, narrow almond eye,
tiny dark pupil, the brow furrow, the crown mark. Seated — knees up, forearms on
the knees, hands clasped, which is the `h240seat` stance.

**The one open deviation:** his skin reads desaturated grey-brown where canon is
sage. That is inherited from pass one's light and is a pass-one fix, not a knob —
see §4.

## 2. Why one pass cannot do it

| cell | weight | hint scale | identity | pose |
|---|---|---|---|---|
| r6 base | none | 1.0 | n/a (a stranger) | **seated** |
| r6 w08 | 0.80 | 1.0 | **yes** | no |
| r7 | 0.65 | 1.0 | **yes** | no |
| r7 | 0.50 | 1.0 | gone | no |
| r7 | 0.35 | 1.0 | gone | no |
| r7 | 0.80 | **1.4** | **yes** | no |

His face leaves between 0.65 and 0.50; the seated legs have not arrived by 0.35.
**The two curves do not cross.** Every LoRA cell adopted the hint's *upper* body
— clasped hands, forearms in, a forward lean — and not one adopted the leg fold.

The lock is a **lower-body prior**, and its cause was pre-registered in
`emit_train_jerry_v2_0822.BARS` before a single training frame was admitted:
**21 of 21 training frames are standing.** No weight and no conditioning scale
reaches a prior that strong, which is why round seven was the last knob round
rather than the first of five.

## 3. Why two passes can

`goblin-i2i-route-0822.md` closed img2img-from-canon as a *posing* route on a
mechanism: at low strength only the last `s*N` steps run, global structure is
decided in the high-noise steps the pass never enters, so a skeleton at scale
1.0 moved grass and light by 15.05 mean abs and did not bend a knee.

That is a failure as a posing route and it is **exactly the property wanted
here**. Pass two must change appearance and must *not* be able to change
structure. The seated composition lives in the init, where the LoRA cannot argue
with it, and the LoRA gets the only job it is good at.

0.65 was too low — he stayed a human boy. 0.75 is the rung where his identity
arrives and the seat still holds. Above that is untested and is where the seat
should be expected to dissolve.

## 4. Four theories this cost, and why each is retired

**"The code path is the fault."** Rounds two and three blamed
`controlnet_plate.py`'s `AutoPipelineForText2Image.from_pipe` construction, on
the grounds that `inpaint_fruit.py` "drives the same net measurably — 15.05 mean
abs". Round four ran the inpaint path and its control failed identically. The
15.05 reading was the error: the sentence it came from says the net *did not
bend a knee*, so 15.05 is grass and light, not a pose. **A number quoted out of
the sentence that qualifies it is not evidence.**

**"The blob is the fault."** Round three swapped xinsir's default openpose blob
for the `twins` directory. Same unrelated standing figure. Two blobs, one
outcome.

**"The LoRA overrides the net."** True at 0.8 on a non-standing skeleton, and
round six proved it cleanly — but it was *not* what rounds one to four were
measuring, because their controls had no LoRA in the pass at all.

**The actual fault: the hint's PROPORTION.** Rounds one to four all drove
`jerry-canon-h37f*-0821` — head_frac 0.370, a 2.7-head figure whose shoulder
line sits at 0.615 of stature. Both hint families come out of the same
`author_b08_openpose_hint.draw_bodypose`, so the renderer is not the difference.
A net trained on annotator output from photographs of people has never seen a
body that shape, and it contributed nothing on any path or blob.

**And that shape was only ever needed because the skeleton used to be the sole
carrier of his proportions.** There was no LoRA, so the hint had to make him look
like himself. `bnyjerry v2` carries that now. The constraint that produced the
defect was lifted by the thing the defect was blocking.

## 5. What is on disk

| artifact | what it is |
|---|---|
| `lora-jerry-v2-b2r4-0822` | the inpaint path on the OLD hint — control fails |
| `lora-jerry-v2-b2r5-0822` | `b08-openpose-nat`, no LoRA → full adoption; w08 → identity holds on top |
| `lora-jerry-v2-b2r6-0822` | beat 13 AGE B: base seated, w08 standing — the split |
| `lora-jerry-v2-b2r7-0822` | the weight ladder 0.65/0.50/0.35 and the scale-1.4 arm |
| `lora-jerry-v2-twopass-0822` | first two-pass, on a twilight init — seated goblin, mauve skin |
| `lora-jerry-v2-tp1day-0822` | pass one relit, flat overcast daylight — the seat held |
| `lora-jerry-v2-twopass2-0822` | **the pass**, `s075` |
| `lora-jerry-v2-tp1rest-0822` | pass-one plates for stride / crouch / hunch |

## 6. What the wave still needs

1. **Three of the four stances do not drive yet, and that is a new finding.**
   `tp1rest` rendered pass one for stride, crouch and hunch on the identical
   recipe — same net, scale, seed, prompt, **no LoRA in the pass** — and none of
   the three adopted the way the seat did. All three came back upright: the
   stride is a standing figure with one arm out, the hunch is standing with
   hands clasped, the crouch is the closest and is only lowered in frame with
   the hands cupped. So beat 13's seat is not yet a general result about the
   `h240` family; it is a result about one skeleton in it.

   **This does not touch the two-pass verdict** — pass two was measured against
   a pass-one plate that *had* adopted, and it held. It says the pass-one half
   needs its own round: the seat is the deepest, most distinctive fold in the
   set (both knees, both hips, arms braced on the knees), and the three that
   failed are all shallower departures from standing. The obvious next variable
   is the same one that fixed rounds one to four — proportion — tested down
   toward the 0.190 that drove completely, one skeleton at a time.

   Pass two for any beat is otherwise blocked only on a mechanical detail:
   `--init-sha256` cannot be written until pass one's output exists, so the two
   halves are two jobs.
2. **The skin.** Pass two inherits the init's colour by construction, so the
   sage has to be won in pass one's wording. `soft overcast daylight, flat even
   light` moved it most of the way; it is a pass-one prompt question and one
   sample answers it.
3. **A founder taste call on the sample**, which is R4 and not the steward's.
   The pose mechanism is now a mechanism; whether *this goblin in this posture*
   is the show is his.
4. **Per-beat wording, emotion, guards, figs and costume** — untouched here.
   This document settles the pose mechanism only.

**And the thing that would retire the two-pass entirely:** a v3 trained on POSED
frames. The lower-body lock is a dataset property with a named cause, and pass
one can now *generate* correctly posed frames of a stranger — which is not a
dataset of him, so it does not close the loop on its own. Worth a research pass
before a card-hour.

---

# CORRECTION, 2026-08-22 evening — the two-pass route lane

**Read this before acting on anything above.** Sections 1, 3 and 6 of the
document you have just read are wrong, and they are wrong because of one
sentence in §5 that was written from a filename rather than from the pixels.

## 1. `tp1day-b13seat` is not seated, so neither is `twopass2-b13seat-s075`

§1 files `twopass2-b13seat-s075` as the sample that "passed both halves … Seated
— knees up, forearms on the knees, hands clasped". It is not. It is a **standing
figure in a forward lean with its forearms crossed in front**. So is its init,
`tp1day-b13seat`, which §5 records as "pass one relit … the seat held".

§1 also records tp1day's light as flat overcast daylight because that is what
its prompt names. The frame is a purple twilight. The prompt named a light the
sampler did not deliver, and the note was written from the prompt.

## 2. The one variable was the wording, and both halves were already on disk

Same net, same `twins` blob, same scale 1.0, same all-white mask, same strength
1.0, same seed 20260822, same `jerry-skel-h240seat-0821.png` byte for byte, no
LoRA in either pass:

| cell | prompt | result |
|---|---|---|
| `b2r6-b13seat-base` | `bnyjerry, 1boy, solo, in tall grass, detailed cinematic anime, masterpiece, best quality, very aesthetic` | **HE SITS** |
| `tp1day-b13seat` | the same, trigger dropped, `soft overcast daylight, flat even light` added | he stands and leans |

Round three reproduced it deliberately on a second skeleton, and round four
showed the rule is not about light at all:

| cell | change from wording A | pose |
|---|---|---|
| `tp3-p1-crouch-wA` | none | **crouches** |
| `tp3-p1-crouch-wAlight` | `+ soft overcast daylight, flat even light` | stands |
| `tp4-p1-seat-wAgreen` | `+ green skin` | stands (and he is green) |

**Any addition to pass one's wording costs the pose.** Wording A is a knife
edge and it is now the lane's fixed string. This is also why §4's four retired
theories were all retired for the wrong reason: rounds one to four never held
the prompt fixed, so none of them was measuring the thing it named.

## 3. §6's three-stance finding was the same confound, and it is now four for four

All three `tp1rest` cells ran the relit wording. Re-asked in wording A:

| stance | hint span | knee−hip | wording A | verdict |
|---|---|---|---|---|
| `h240seat` | 0.596 | +9.7 px | `b2r6-b13seat-base` | **drives** |
| `h240crouch` | 0.535 | −19.5 px | `tp3-p1-crouch-wA` | **drives** |
| `h240stride` | 0.867 | +206.8 px | `tp5-p1-stride-wA` | **drives** |
| `h240hunch` | 0.807 | +216.5 px | `tp5-p1-hunch-wA` | does not |
| `h240hunchdeep` | 0.721 | +182.5 px | `tp7-p1-hunchdeep-wA` | **drives** |

§6 proposed testing proportion "down toward the 0.190 that drove completely".
Do not. `crouch` is the DEEPEST fold in the set and it failed on wording alone,
which retires depth-of-fold as the law. The one genuine geometry failure was
`h240hunch`, and the measurement says why: it differs from `stand` by a head
dropped 0.06 of stature and nothing else, so a standing figure with its head
down was the correct rendering of it. `hunchdeep` re-authors it as a spine —
crown down 141 px against 82 at the shoulders, neck halved to 60 px, shoulders
narrowed, knees softened — and it drives. **Four of four postures are proven.**

## 4. And §3 is wrong: pass two DOES change structure

§3's whole argument is that at low strength "global structure is decided in the
high-noise steps the pass never enters", so pass two "must change appearance and
must *not* be able to change structure". That was measured on tp1day, which was
already a lean — preserving a lean proves nothing about preserving a seat.

Six cells on `b2r6-b13seat-base`, an init that **is** a seat, across both knobs:

| strength | LoRA weight | pose | identity |
|---|---|---|---|
| 0.75 | 0.8 | lean | is him |
| 0.65 | 0.8 | lean | is him |
| 0.60 | 0.8 | lean | a human boy |
| 0.60 | 1.0 | lean | is him |
| 0.55 | 1.0 | lean | is him |
| **0.55** | **0.8** | **SITS** | **a human boy** |

The seat survives in exactly one cell and it is the one cell where he is
somebody else. Weight reaches structure as well as strength does. **The two
curves do not cross in the second pass either**, and the two-pass is retired as
a pose route on the same mechanism as the one-pass: 21 of 21 training frames are
standing, and wherever the LoRA is loud enough to be recognisably him it also
insists he is on his feet.

## 5. What is actually left

1. **A founder taste call**, published at `/review/ep2-goblin-twopass-0822`:
   his canon head beside the best rendered head at true 1:1, the six-cell
   ladder, the four stances, the wording pair, and one question with two named
   roads out of it. **Nothing stages until he answers** — every candidate frame
   is a lean, and whether that lean is the show is R4 and not the steward's.
2. **The v3 retrain on posed frames**, which §6's last paragraph called worth a
   research pass and which is now the only remaining mechanism. Pass one can
   generate correctly posed bodies in four stances at $0 — that is not a dataset
   of *him*, so the loop is still open, and the research question is how to get
   his identity onto a posed body without the LoRA that carries the standing
   prior. Do the reading before the card-hour.
3. **The skin is unsolved and has nowhere cheap left to go.** `green skin` in
   pass two coloured a leaf and left him alone; in pass one it turned him a
   saturated green with green hair and deleted the pose. Sage is not one tag.

## 6. The method note, because it is the whole lesson

Every wrong claim above came from reading a filename, a prompt or a metric
instead of the frame. §4 already says it — "a number quoted out of the sentence
that qualifies it is not evidence" — and then §5 filed a lean as a seat on the
strength of a note. Nineteen cells and about eight minutes of card time
overturned four documented findings. **Open the PNG.**
