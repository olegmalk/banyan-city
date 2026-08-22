# The masked lower-body pass — how the goblin finally sat down

**2026-08-22, the v3 lane.** Four samples, about a hundred seconds of card,
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
Jobs: `ep2-b13-lowerbody-0822`, `-w2-`, `-w3-`, `-kneel-`.
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
of 21 training frames stand, pre-registered before a frame was admitted, and §6
measures that it is even narrower than that — and
this pass does not need it: the identity is the init's own pixels. It is also
the one configuration in which the pose net has been observed to drive in this
tree (four of four postures, twopass CORRECTION §3).

## 3. What four rounds measured

| round | the one variable | result |
|---|---|---|
| r1 | the mask (all-white → below y 900), strength 0.35 → 0.95 | head HELD at 0.95 (mean abs delta 1.247). **No legs at all**: the band filled with tall grass, row luminance 128 → 73 across y 880..1000. |
| r2 | the wording: `in tall grass` out, `seated, bare legs, dark shorts, dark boots` in | **SEATED.** Knees up and out past the authored hint, shins descending, feet planted. Seam invisible. One figure. Thighs pale on the lit side; feet are paws. |
| r3 | the wording again, aimed at P3: `bare sage green legs`, `dark leather boots` | Real boots with soles and heels — and they run knee-high and hide the thighs, and the stance narrows. Not better than r2, differently wrong. |
| **gate** | **the hint only** — seat → kneel, with the positive still saying `seated`, byte-identical | **THE HINT WON.** The legs go down and forward instead of up and out: limb mass at y 1180 is 245 px against r2's 0, and at y 1040 it spans x 0..746 against r2's 0..567. Against a contradicting noun. |

Held across all four: init sha, mask sha, hint sha, net, scale 1.0,
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
5. **The hint carries GEOMETRY; the prompt carries CONTENT; and they were made
   to argue on purpose.** The gate cell kept the word `seated` in the positive
   and swapped only the skeleton for a kneel. The legs knelt. So the stance set
   is a hint-authoring job: four PNGs and about eight minutes of card, with no
   per-stance wording round. Taken with finding 2, the division is clean — the
   noun decides WHETHER a body is drawn in the region, the skeleton decides WHAT
   SHAPE it is, and the skeleton wins when they disagree.
6. **The protected region is NOT byte-exact, and the reason is mechanical.**
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

**The stance set is NOT queued**, and the reason is no longer "does the route
generalise" — the gate answered that. It is that the v3 dataset design changed
this afternoon, and §6 is why.

**And the plan this section carried an hour ago was wrong.** It said: run the
same masked pass on the 21 founder-ratified frames, so each posed frame gets its
own torso. That cannot be done. **Nineteen of the 21 have no lower body in
them** — 11 are upper-body crops and 8 are cowboy shots — so there is nothing
below a cut to replace. The two that do are the canon and its mirror. The
correction is §6.

**One more thing the gate bought at $0, and it is a guard finding.** Its first
attempt refused on the card in two seconds: `SHA MISMATCH for
jerry-kneel-hint-0822.png -- want da14ee0b, have 7f1655bb`, rc=1, no model
loaded. The retoken had renamed the hint everywhere including inside its fetch
URL, but the SHA is a SECOND string and it appears twice — in the argv and in
the inherited `fetch_init.py` payload — and only the argv had been overridden.
A wrong hint would have rendered a perfectly plausible frame answering a
different question. **The fix is to retoken the hash rather than override one
copy of it**, for the same reason `derive_spec` retokens ids and directory
tokens: a retoken reaches every copy of a string by construction, an override
reaches the one place its author remembered.

## 5. What this does not do

It is not a plate for beat 13 and it is not a taste call. The founder's question
page at `/review/ep2-goblin-twopass-0822` stands unchanged — whether this posture
is the show is R4 and not the steward's. What changed today is that the steward
can now put him in a posture at all.

## 6. THE DIAGNOSIS WAS UNDERSTATED, AND THE CORRECTION MAKES THE FIX SMALLER

`registry.yaml` and every document downstream of it say the pose is locked
because **"21 of 21 training frames are standing"**. That is true and it is not
the whole shape of the problem. Measured on `manifest-jerry-v2-0822.yaml` today:

| framing | frames |
|---|---|
| upper body | 11 |
| cowboy shot (mid-thigh) | 8 |
| **full body** | **2** |

and the two full-body frames are `canon-full` and `canon-full-flip`, verified
byte-identical to `taste/refs/goblin-canon-founder-0821.png` and to its mirror
(mean abs delta 0.000, maxdiff 0, both directions).

**So the standing prior is not 21 frames deep. It is ONE frame deep.** The LoRA
has been shown this character's legs exactly once, plus that once flipped. That
reframes three things at once:

1. **It explains why no knob reached it.** Round seven walked the weight down to
   0.35 and the seated legs never arrived; the twopass walked strength and
   weight across six cells. Both were looking for a competing lower-body
   configuration to fade *toward*. There isn't one in the weights. There is one
   picture.

2. **It makes the caption failure legible.** All 21 captions carry `standing` —
   including the 19 that do not show a standing leg. The token was attached to
   frames with no lower body in them at all, which is the most literal possible
   form of "a tag with nowhere to attach". The setting tag worked in the same 21
   files because every one of them *does* show a background.

3. **AND IT MAKES THE FIX MUCH SMALLER THAN A REBUILD.** The plan was reading as
   "manufacture a posed dataset". It does not need to be. The 19 crops carry no
   lower-body signal, so they cannot fight a new one; the entire opposition is
   two frames of one picture. **Three or four posed full-body frames would make
   posed the MAJORITY of everything the trigger has ever seen below the waist**,
   in a dataset otherwise byte-identical to the one whose identity bars already
   pass.

### The v3 spec this implies, and it is deliberately minimal

* **KEEP all 21 frames and all 21 captions byte-identical.** v2b measured that
  lengthening the captions of frames that are already working costs identity —
  B1 went 11 → 9 → 11 as two clauses were added and taken back with pixels and
  recipe held. Nothing that currently passes gets touched.
* **ADD 3–4 posed full-body frames** from this route. Seat and kneel are on disk
  already, and the gate says a further stance is one hint PNG.
* **Their captions name the stance** (`sitting`, `kneeling`) where the existing
  two full-body captions say `standing`. That gives the pose token real contrast
  **on the only frames that carry a lower body at all** — 4 posed against 2
  standing — which is the first time in this project that token has had anywhere
  to attach.
* **One variable against v2**, so a score is attributable: the added frames. Not
  the recipe, not the captions of the 21, not the repeat count.

### And P3 does not have to be solved before the set is built

The one open defect — pale thighs, paw feet, a left-right boot mismatch of ~82
RGB units — sits at the BOTTOM of the frame. In `r2` the knees are at y 930–1000
and the paws at y 1080–1120. **A crop at y 1070 removes every defective pixel
and keeps the entire pose signal**, because on a seated chibi the fold is the
knees and not the feet.

That is free, it needs no sampler, and it is *already the dataset's own idiom*:
8 of the 21 ratified frames are cowboy shots and 11 are upper-body crops, so a
posed frame cropped above the boot is more consistent with the set than a
full-body one would be. It also removes the risk that four frames of paw feet
outvote the two canon frames that have real boots.

What it costs is the silhouette — a cropped frame teaches the fold, not the
whole standing-to-seated outline. So the honest assembly rule is: crop the
frames whose extremities are wrong, keep full-body only where the boots came
back right, and record which is which per frame. The palette transfer above
stays available for the thighs either way.

### The risk this carries, named before the run

Every posed frame shares ONE upper body, byte for byte — the canon's, moved by
an integer. Four of them is four copies of one torso, one pair of arms and one
light. If v3's identity bar falls, that is the first suspect, and it has a cheap
answer: the frames can be reframed and re-cropped after the pass, and the pass
can run at more than one `DROP` so the torso sits at a different height in each.
**Neither is a research question and neither needs the card.**
