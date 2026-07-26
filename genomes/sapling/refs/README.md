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

## A reference is copied entirely, background included

The first version of `jerry.png` was cropped loosely from a rendered frame that
happened to contain a stone arch behind him. Every shot conditioned on it came back
with a soft circular vignette — IP-Adapter was reproducing the reference faithfully,
including the part that was scenery. It is a character reference, so it must contain
the character and as little else as possible: figure centred, plain ground, no
props, no framing device, no distinctive lighting.

## Strength

`IPA_SCALE` in the notebook. Measured on four beats of 002b:

| scale | identity | composition |
|---|---|---|
| 0 (none) | four different characters | free |
| 0.6 | consistent | reference dictates it — a sprint and a close-up both became a centred standing figure, and two of four went blank |
| **0.35** | consistent | prompt drives it again; a close-up stayed a close-up |
