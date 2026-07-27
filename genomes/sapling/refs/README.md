# Character references — one image per recurring character

The show has four recurring characters across 166 shots, and SD1.5 invents a new
one every time it is asked. Measured 2026-07-26: four beats of 002b that all
specify the same goblin produced four different characters — a green cloaked
runner, a pale big-eared hooded figure, a wide-eyed child's face, and a figure in
a broad hat. The style was consistent; the person was not.

Text cannot fix this. A prompt describes a *type*, and the model samples a fresh
instance of that type per shot. Consistency needs the same IMAGE conditioning
every time, which is what IP-Adapter does.

So each file here is one character's canonical look, and every shot they appear in
is conditioned on it:

| file | character | source |
|---|---|---|
| `jerry.png` | the goblin keeper — small, hooded, enormous ears, pale cloak | frame from 002b beat 3, tightly cropped to the figure |

Replacing a reference re-casts that character everywhere, which is a taste call
(R4) and belongs to the founder. Adding one for the farmer, the magistrate and the
assessor is the obvious next step once the goblin proves the mechanism.

## A reference transfers TONE as well as identity

Two things get copied, and the second one surprised me.

**Composition.** `jerry.png` was first cropped loosely from a rendered frame that
happened to contain a stone arch, and every conditioned shot came back with a soft
circular vignette. IP-Adapter was reproducing the reference faithfully, scenery
included.

**Contrast.** So I re-cropped tight to the figure to remove the arch — and 3 of 4
beats came back BLANK (luma spread 17-27, against 38-62 with the loose crop). The
tight crop was a pale figure on flat grey, and a flat reference produces flat
output. The arch was noise; the tonal structure around it was load-bearing.

The reference in place is therefore the LOOSE crop, because it renders. Its
vignette is a known cosmetic artefact, accepted until a reference is made properly.

**Making one properly** means rendering a character sheet on purpose — the figure
centred on a plain but not washed ground, with real light and shadow — rather than
harvesting a frame from an episode. That is the open task, and it is cheap: one
render, then every shot the character appears in inherits it.

## Strength

`IPA_SCALE` in the notebook. Measured on four beats of 002b:

| scale | identity | composition |
|---|---|---|
| 0 (none) | four different characters | free |
| 0.6 | consistent | reference dictates it — a sprint and a close-up both became a centred standing figure, and two of four went blank |
| **0.35** | consistent | prompt drives it again; a close-up stayed a close-up |

## `style-plate.png` — one look for the whole show (empty slot, founder's pick)

The founder's verdict on the first assembled cut of episode 1 was that it read as
fifteen unrelated AI images. Prompt fixes make each shot *correct*; they do not
make fifteen shots a *family*. The same mechanism that keeps a character consistent
can keep a look consistent: condition every beat on one image that defines the
palette and light.

So the renderer now looks for `style-plate.png` in this directory. If it is here,
every beat that has no character reference of its own inherits it at
`STYLE_SCALE = 0.30` — deliberately below the 0.35 used for faces, because a plate
must tint the palette, not dictate content. A beat with a character reference keeps
using that instead; a character's identity outranks the house style.

Nothing else changes. The slot is empty and the feature is inert until a file
exists, because **which frame IS the show is a taste call (R4) and belongs to the
founder, not the renderer.** The mechanism is ready so that answering it is a file
drop and a commit, not a code change.

To use it: pick the frame that looks most like the show, save it here as
`style-plate.png`, commit, push, re-render. To stop using it: delete the file.

Same caveat as above applies with more force, since this one touches every shot —
a reference transfers tone and background, so a plate cropped from a dark interior
will darken outdoor beats. Prefer a plate whose light is typical of the show rather
than the single prettiest frame.
