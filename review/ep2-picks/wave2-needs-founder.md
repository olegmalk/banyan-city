# wave 2 — what the fixer lane could not fix, and why it stops here

Written 2026-08-12 by the overnight fixer lane while reading the sixteen
identity-frozen rounds (`farm-out/ep2-bNN-idfix/`). Everything below is either
outside the lane's authority or a model limit that has now had its one r2. Facts
and frame counts are in `review/ep2-picks/wave2-faults-fixer.yaml`; this file is
the short list of things that need a human decision.

---

## 1. `patchwork cloak` in the frozen goblin definition is what sews his skull

**This is the biggest finding of the night and the lane cannot act on it, because
definitions are frozen.**

The wave contains a natural experiment nobody designed:

| beat | `goblin_definition_as_sent` | skull in the four frames |
|---|---|---|
| 02 | `green skin, bald head, patchwork cloak` | pale/tan crown with sutures, **4/4** |
| 03 | `green skin, bald head, patchwork cloak` | sutured seam or cream skull, **3/4** |
| 04 | `green skin, bald head, patchwork cloak` | cream dome + X-stitches, **4/4** |
| **08** | **`green skin, bald head`** (no cloak) | **clean green, unbroken, 0/4 faults** |

Beat 08 is the only beat whose definition omits `patchwork cloak`, and it is the
only goblin beat whose heads are clean. Read together with the beat-02 r2 — where
banning `scars` and `stitched skin` removed the sutures **and** the pale dome at
the same time, showing they were one fault — the reading is that `patchwork` sits
next to `bald head` in the identity slot and the model applies the fabric to the
skull.

- **The workaround is proven and is already shipping**: the beat-level ban `no
  scars, no stitched skin` cleared it 4/4 on beat 02 without harming the cloak,
  and it is propagated to the other goblin beats tonight.
- **The cause is the definition**, and changing a frozen definition is not the
  fixer's call. Options for the founder: reorder so `patchwork cloak` is not
  adjacent to `bald head`; move the cloak out of the identity slot into each
  beat's own sentence (which is where beat 08 already has it); or leave the
  definition alone and keep paying two negative tokens per goblin beat forever.

## 2. The sapling will not stand next to the goblin

Beats 02, 03, 13, 15, 17, 19 and 20 all ask for a tiny sapling beside or in front
of him. Across the `_idfix` wave the single sapling is replaced by a bed of
generic seedlings, parked at the frame edge, or simply absent. This is old —
commit `bdcb1a2a` recorded it as absent from all eight goblin frames.

The beat-02 r2 is the best result so far: moving the stem into an early clause got
a readable single sapling in **2 of 4** frames. That is real movement and still
not a fix. Beats 02 and 03 have now each had their one r2 on this, per the lane's
instructions, and the lane is not spending a third round on it.

**Needs a decision**: this may want a different tool than prompt wording — an
img2img or inpaint pass that puts the sapling in deliberately, or a composition
LoRA, or accepting 2/4 and picking the good seeds.

## 3. The guards are drawn as hard, muscular adult men

Beats 05, 06 and 07, every frame. Sharp cheekbones, scowls, bared teeth in one.
The ratified guard is a **"silly harmless bureaucrat"** with a round soft body and
a visible face — and beat 05 **sends those exact words** and still drew a muscular
man in one frame of four, so the wording is known not to bind on its own.

The lane deliberately did **not** chase this inside a round: it is a taste axis
(R4), and stacking it onto rounds that were fixing settings and cameras would have
made those results unattributable. It needs either the founder's own words for the
guard, or a character sheet the way the goblin got one.

## 4. Beat 08 keeps its worst frame

`08-inside-him-wave1-s1` draws the goblin as a waist-high green egg with a face on
it, standing between two bald humans. Beat 08 has the tightest budget in the wave
(76/77 positive, 76/77 negative, and it already overran once in commit `6d177f4`),
so its one r2 spends everything on the camera — the two overhead frames are also
the two worst, and a belly seen from directly above is a plausible route to a
sphere. **Not fixed and not attempted**: the black-not-brown tunic (3/4) and the
fact that nobody in any frame points at a belly (0/4), which is the beat's joke.
