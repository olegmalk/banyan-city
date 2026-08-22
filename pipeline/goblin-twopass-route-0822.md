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
