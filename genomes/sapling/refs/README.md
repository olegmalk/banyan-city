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
| `jerry.png` | the goblin keeper — small, hooded, enormous ears, patchwork cloak | frame from 002b beat 3, the closest render to `style.md`'s model sheet |

Replacing a reference re-casts that character everywhere, which is a taste call
(R4) and belongs to the founder. Adding one for the farmer, the magistrate and the
assessor is the obvious next step once the goblin proves the mechanism.
