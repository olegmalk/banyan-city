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
