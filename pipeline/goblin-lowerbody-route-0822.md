# The masked lower-body pass — how the goblin finally sat down

**2026-08-22, the v3 lane.** Three samples, about seventy-five seconds of card,
`$0`. Written because the pose problem is solved and the next lane should
inherit the mechanism rather than the ladder.

## 1. The recipe, first, because it is short

    inpaint_fruit.py
      --init  <the canon, head+torso block moved +150 px, standing legs erased>
      --mask-png <WHITE ONLY BELOW y 900>       ← the whole idea
      --strength 0.95
      --pad-crop 0  --blur 8
      --controlnet xinsir/controlnet-openpose-sdxl-1.0  --scale 1.0
      --control <a seat skeleton at HIS measured segment lengths>
      NO --lora
      prompt: the legs NAMED as nouns

    then pipeline/jerry_lowerbody_restore_0822.py
      pastes the init's own rows 0..883 back, byte for byte, asserted.

Assets: `pipeline/author_jerry_lowerbody_0822.py` (`--write`).
Jobs: `ep2-b13-lowerbody-0822`, `-w2-`, `-w3-`.
Evidence: `farm-out/ep2-goblin-lowerbody-0822/` (contact sheets + the two
restored frames; the raw renders land under `farm-out/ep2-b13-lowerbody-*-0822/`
by courier). NOT `review/` -- `.gitignore:60` is `review/**/*.png`, so evidence
filed there would have been invisible to everyone but the machine that made it.

## 2. Why it works, and it is one sentence

Every closed lever on this character asked ONE REGION to carry identity and pose
at the same time, and they want opposite ends of the same knob:

| lever | outcome |
|---|---|
| pose by words (`crouching`) | a standing figure. B5 fails. |
| openpose + LoRA weight ladder | face leaves between 0.65 and 0.50; the leg fold has not arrived at 0.35 |
| two-pass, LoRA repaint on a seated init | the one cell that keeps the seat is the one cell where he is somebody else |
| i2i from the canon + openpose | face breaks between 0.40 and 0.45; the pose has not moved at 0.40 |

On base weights (`unet.in_channels == 4`) an SDXL inpaint pipeline restores the
unmasked latent at **every** timestep —

    latents = (1 - init_mask) * init_latents_proper + init_mask * latents

— so a region outside the mask cannot drift **at any strength**. Put his dome,
ears, eye, collar and placket outside; put the legs, the hem and the ground
inside. The tension stops existing because they are no longer the same pixels.

**And no LoRA is loaded.** `bnyjerry v2` is where the standing prior lives — 21
of 21 training frames stand, pre-registered before a frame was admitted — and
this pass does not need it: the identity is the init's own pixels. It is also
the one configuration in which the pose net has been observed to drive in this
tree (four of four postures, twopass CORRECTION §3).

## 3. What three rounds measured

| round | the one variable | result |
|---|---|---|
| r1 | the mask (all-white → below y 900), strength 0.35 → 0.95 | head HELD at 0.95 (mean abs delta 1.247). **No legs at all**: the band filled with tall grass, row luminance 128 → 73 across y 880..1000. |
| r2 | the wording: `in tall grass` out, `seated, bare legs, dark shorts, dark boots` in | **SEATED.** Knees up and out past the authored hint, shins descending, feet planted. Seam invisible. One figure. Thighs pale on the lit side; feet are paws. |
| r3 | the wording again, aimed at P3: `bare sage green legs`, `dark leather boots` | Real boots with soles and heels — and they run knee-high and hide the thighs, and the stance narrows. Not better than r2, differently wrong. |

Held across all three: init sha, mask sha, hint sha, net, scale 1.0,
`--pad-crop 0`, 40 steps, cfg 7.5, seed 20260823, no LoRA.

### The findings, ranked by how much they generalise

1. **A mask splits identity from pose and they stop trading.** Six rounds looked
   for a crossing point on a knob. There isn't one, and there doesn't need to
   be. This is the mechanism and it is not specific to a seat, a beat or this
   character.
2. **The prompt chooses the region's content; the hint only chooses where.**
   r1's skeleton is byte-identical to r2's and drew no legs, because wording A's
   only noun for that region was grass. `ep2-b08-nostrap2-0820` measured this
   lever and named it; this is a second, cleaner instance of it. **A skeleton
   conditions WHERE a body goes. It does not ask for one.**
3. **The wording-A rule is a property of the unconstrained case.** The twopass
   CORRECTION measured that ANY addition to pass one's wording costs the pose.
   Here four nouns were added and the pose ARRIVED. The difference is that the
   composition above the cut is fixed pixels rather than something the wording
   is choosing. The rule should be restated with that scope.
4. **The seam is a non-problem.** It was the pre-registered most-likely failure
   — a shirt cut off at a horizontal line, continued into a lap by a sampler —
   and it is invisible in the landed frames at 1:1.
5. **The protected region is NOT byte-exact, and the reason is mechanical.**
   diffusers only re-pastes in PIXEL space inside its `padding_mask_crop` branch
   (`apply_overlay`), and this route runs `--pad-crop 0` deliberately, so the
   head survives as latents and takes one VAE round trip: 95% of pixels move by
   at least one level, maxdiff ~118 on ink edges. That is a compositor fix, not
   a sampler one — `jerry_lowerbody_restore_0822.py`, and it asserts the result.

## 4. What is still open, and it is small

**P3, the extremities.** r2 gives the better stance with pale thighs and paw
feet; r3 gives real boots with a narrower stance and no visible leg. Both frames
also carry an ~82-unit RGB distance between the left and right foot — a
mismatched pair, present in BOTH, so it is not something r3 introduced.

**No fourth wording rung is filed**, and that stopping rule was written into
`ep2-b13-lowerbody-w3-0822` before the render. Two cells moved this clause and
both traded. What is licensed instead: a **palette-transfer compositor** off the
canon's own bare shin (RGB 120.4 / 130.0 / 110.4, sampled at 355..385 x
925..945), which is `$0`, has no sampler in it, and is the house tradition —
`beat20_fig_recolor.py`.

**The stance set is NOT queued**, deliberately, and the reason is a dataset
design question rather than a rendering one. Every frame this route makes off
the canon shares ONE upper body, byte for byte. Six of those in a v3 set would
teach the trigger that upper body. **The fix is to run the same masked pass on
the 21 FOUNDER-RATIFIED FRAMES** of `manifest-jerry-v2-0822.yaml` instead of on
the canon alone: each has its own torso, its own arms and its own light, and the
mask makes each one a posed frame of him with a different upper body. That needs
a per-frame cut line and hip measurement, which is a script rather than a
research question.

## 5. What this does not do

It is not a plate for beat 13 and it is not a taste call. The founder's question
page at `/review/ep2-goblin-twopass-0822` stands unchanged — whether this posture
is the show is R4 and not the steward's. What changed today is that the steward
can now put him in a posture at all.
