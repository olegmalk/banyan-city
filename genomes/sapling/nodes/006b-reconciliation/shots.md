# Node 006b — shot list (36 shots, 1:1 with the script's beats)

Rebuilt 2026-08-10 for `006b-t0-b`. The previous list was **4 shots for the
whole episode** — one picture every 22 seconds, which is the defect the
founding author named on episode 2 ("the pictures did not match the script").
This list is **one shot per beat, 4–7s, camera on the referent of that beat's
line** (SCRIPT-SPEC.md "one beat = one shot").

Base footage only: no burned-in text, no dialogue — post adds captions, VO and
every sky-label overlay. 9:16 vertical. Each prompt's FIRST sentence states the
primary action (motion grammar, `../../style.md`), so the model does not return
a still.

**Growth ladder (`../../style.md`):** 006b sits at the same rung as its sibling
006a — **~1.6 m young tree**, full small crown, first woody bark, side
branches, a shrine you can stand under. Never "sapling" here, and never
"tiny": from 004 the comedy is bureaucratic, not physical. The small shade
patch on the ground is a prop and characters use it.

**Character continuity (anime model sheet, `../../style.md`):** the MAGISTRATE
is a sharp angular silhouette in dark robes of office, a seal on a chain and an
open pocket-watch in her hand; her face is drawn for one raised eyebrow. The
SCAVENGER is a small round goblin — enormous ears that act like a second face,
one broken tusk, huge expressive eyes, faded green patchwork cloak. The FARMER
is a broad squarish silhouette in a straw hat, three lines for his whole face,
permanently unimpressed. Beside the tree: a crooked lean-to, a three-stone
cairn, a clay jug.

**The sunset window** (beats 16–25) is the same overlay canon as 004: the solid
world flickers into a glowing teal wireframe — grass a lattice, the cairn
low-poly, the jug a plain cylinder. **The labels are post overlays, never
generated** — the prompts ask for the wireframe world with empty air where the
label will sit.

**Token budget — RE-MEASURE BEFORE GENERATING.** Checked 2026-08-10 through
`sd_prompt.compress()`, the same call `farm_worker` makes, but **on a machine
with no CLIP tokenizer**, so the count was the module's deliberately
pessimistic prose estimate and it drops more than the real path would. Under
that pessimistic reading no prompt here loses a *content* sentence — the four
longest (beats 01, 02, 16, 24) were shortened until none did. What the
estimate cannot settle is the booster tail (`masterpiece, best quality, very
aesthetic`), whose silent loss on three of 002b's beats is recorded in that
node's shot list and cost this repo a batch of flat, pale frames on
2026-07-26. Before any batch, re-run the check on a box that has the real
tokenizer and spend the cheapest words, never the beat's subject.

**Assembly:** save each clip as `NN-slug.mp4` in a clips dir, then
`python3 pipeline/render_t3.py sapling 006b --clips <dir> --out ep.mp4`

**Not renderable yet.** `006b-t0-b` carries no `approved_by` — STEWARDSHIP.md
§6 forbids voice, footage or assembly from this node until the founder has read
the script. This list exists so that the reading and the shot plan can be
judged together.

Status legend: ✅ generated · ⬜ needs footage

---

## Beat 01 — COLD OPEN (0:00–0:06) ⬜ needs footage

Line: VO, premise. Camera wide on the whole settlement with one figure at the road's edge — the shot that says where we are and that something has arrived.

```
Grass ripples across a wide empty field at dusk while a lone dark figure stands motionless at the far road's edge. Nearer, a 1.6 metre young banyan tree with woody bark, a crooked lean-to and a three-stone cairn. Amber-into-indigo sky, long shadows. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 02 — REGULATION ONE (0:06–0:11) ⬜ needs footage

Line: MAGISTRATE, "Settlement review is conducted at last light." Camera on her — the arrival is the event.

```
A tall woman in dark robes of office turns an open pocket-watch in her hand without lifting her eyes, alone at the edge of a dusk clearing, a heavy seal swinging at her chest. Sharp angular silhouette, one raised eyebrow, low amber sun behind her, grass moving at her hem. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 03 — FROZEN MID-BITE (0:11–0:15) ⬜ needs footage

Line: VO, "Rule *One*." Camera on the goblin — the reaction shot is the joke.

```
A small round goblin stops moving mid-bite with a piece of bread halfway to his mouth, his enormous ears dropping slowly flat against his skull. One broken tusk, huge expressive eyes going wide, faded green patchwork cloak. Dusk field behind him, warm rim light, grass swaying. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 04 — ALWAYS AN OUTAGE (0:15–0:21) ⬜ needs footage

Line: VO, the rule nobody remembers the reason for. Camera macro on the watch — the object the regulation lives in.

```
An open brass pocket-watch turns slowly in a woman's fingers, its lid swinging, dusk light sliding gold across the dial. Extreme close macro, shallow depth, dark robe sleeve and a chain out of focus behind. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 05 — THE HEADCOUNT (0:21–0:26) ⬜ needs footage

Line: VO, "They have arranged themselves into a headcount." Camera on the two of them lining up — the picture IS the joke.

```
A broad farmer in a straw hat and a small round goblin slide sideways into a neat evenly spaced row and stand to attention, nobody having asked them to. Wide flat static framing like a police line-up, dusk field, long shadows running out sideways, grass drifting. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 06 — THE LEDGER (0:26–0:31) ⬜ needs footage

Line: MAGISTRATE, "Shade. Founded yesterday." Camera on the ledger — she is reading, so we read with her.

```
Two hands open a heavy leather ledger and the pages fall flat, last light lying gold across handwritten columns. Close over-the-shoulder, dark robe sleeves, a seal on a chain hanging into frame. Blurred dusk field beyond. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 07 — ONE-ISH (0:31–0:36) ⬜ needs footage

Line: MAGISTRATE (off), "one-ish". Camera cuts to the structure being described — the cut is the punchline.

```
A crooked lean-to of deadfall leaning against a rock sags further as the wind pushes it, one branch sliding loose. Dusk field, the 1.6 metre young banyan tree with woody bark just in frame beside it. Static camera, unimpressed framing, dust drifting in low amber light. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 08 — MENDED ITSELF (0:36–0:40) ⬜ needs footage

Line: MAGISTRATE (off), "Water: mended itself." Camera on the water.

```
Clear water runs steadily along a repaired earth irrigation channel, rippling past a clay jug set on the bank. Low close angle at ground level, dusk gold on the surface, reeds moving. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 09 — POPULATION THREE (0:40–0:46) ⬜ needs footage

Line: MAGISTRATE, "Population: three… 'answers questions'." Camera on the finger stopping on the line — the discrepancy is born here.

```
A woman's finger slides down a handwritten ledger column and stops dead on one line. Extreme close on the page, dusk light raking across the paper grain, the finger held still while the page edge lifts in the wind. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 10 — THE SNAP (0:46–0:52) ⬜ needs footage

Line: MAGISTRATE, "The assessor is thorough. So either he is wrong, or the sky is." Camera on her closing everything — decision made.

```
A woman in dark robes closes a heavy ledger, glances at the pocket-watch and snaps its lid shut in one continuous movement. Medium shot, sharp angular silhouette against a low amber sun, seal swinging on its chain, one eyebrow raised. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 11 — THE SKY? (0:52–0:56) ⬜ needs footage

Line: SCAVENGER, "…The sky, ma'am?" / MAGISTRATE, "Four minutes." Camera on the two of them turning to each other — the clock is hers, the confusion is theirs.

```
A broad farmer in a straw hat and a small round goblin turn their heads at the same moment and look at each other, the goblin's enormous ears swivelling forward. Tight two-shot, dusk field behind, warm rim light, grass swaying. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 12 — RECONCILE (0:56–1:02) ⬜ needs footage

Line: VO, "she is here to *reconcile* us." Camera on the tree — the VO's own body, the thing being reconciled.

```
Leaves breathe almost imperceptibly on a 1.6 metre young banyan tree with a small full crown and first woody bark, standing alone in the last of the light. Close low angle up the trunk, dusk sky behind, grass drifting past the base and a small shade patch fading on the ground. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 13 — LEDGER VERSUS PRODUCTION (1:02–1:07) ⬜ needs footage

Line: VO, "I used to be this woman." Camera on the ledger under her arm — the object of the comparison.

```
A heavy leather ledger rides clamped under a dark-robed arm while a seal on a chain swings against its cover, both moving with her step. Close tracking shot from the side, dusk field sliding past out of focus behind. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 14 — A WORSE ROBE (1:07–1:12) ⬜ needs footage

Line: VO, "At three in the morning. In a worse robe." Camera on her silhouette — the robe is the joke.

```
Dark robes of office lift and ripple in the field wind around a tall angular silhouette standing against a very low sun. Backlit contre-jour, the figure almost black, dust and seed heads drifting through the light. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 15 — LAST LIGHT (1:12–1:16) ⬜ needs footage

No line. The clock beat: the sun reaches the horizon and the four minutes are up.

```
The sun's lower edge touches the horizon and shadows sweep out sideways across a wide empty field, the whole frame going long and gold. Wide landscape, the small settlement in silhouette at one side, grass rippling in waves. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 16 — THE WINDOW (1:16–1:20) ⬜ needs footage

No line. The overlay opens. Labels are post overlays — leave the air above the clearing clear.

```
The solid world flickers into a glowing teal wireframe as the light dies: grass a lattice of lines, the cairn a low-poly block, the jug a plain cylinder. Wide clearing, indigo sky, empty air above the settlement, scan shimmer in the mesh. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 17 — STILL TALKING (1:20–1:25) ⬜ needs footage

Line: SCAVENGER, "The water's very reliable now, ma'am—". Camera on him, oblivious inside the wireframe.

```
A small round goblin gestures enthusiastically at a clay jug with both hands, entirely oblivious, while the world around him glows as a teal wireframe lattice. Medium shot, his patchwork cloak and huge eyes solid and normal against the mesh, ears up, night sky behind. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 18 — MA'AM? (1:25–1:29) ⬜ needs footage

Line: SCAVENGER, "…Is she having a moment? Ma'am?" Camera on his ears turning — his confusion is the line.

```
A goblin's hands drop to his sides and his enormous ears swivel around toward a dark-robed back turned away from him. Close on the goblin, one broken tusk, eyes narrowing in confusion, teal wireframe grass glowing behind. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 19 — READING THE SKY (1:29–1:33) ⬜ needs footage

No line. The reveal shot: she is looking UP, and the camera says so before the VO does.

```
A woman in dark robes tilts her chin up and tracks something moving in the air above her, her back turned on everyone. Low angle from below, her face lit from above by cold teal light, wireframe field glowing behind her, robe hem moving. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 20 — THE LABEL (1:33–1:37) ⬜ needs footage

Line: VO, "It says two." Camera on her eyeline — the empty air over the clearing where post renders `SHADE · settlement(?) · pop. 2`.

```
Wireframe treetops and roofs drift at the bottom of frame while empty dark sky opens above the clearing, a faint teal glow rising from the mesh below into clear air. Upward-looking shot, most of the frame deliberately empty sky, one or two floating motes. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 21 — THE SEAL (1:37–1:42) ⬜ needs footage

Line: VO, "Her seal renders too." Camera macro on the seal — the proof she is inside the system. Its wireframe tag is a post overlay.

```
A heavy metal seal on a chain swings up into the light held in a woman's raised hand, turning slowly. Extreme close macro, the metal flickering for an instant into glowing teal wireframe edges and back to solid, dark background, shallow depth. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 22 — THE REVEAL (1:42–1:48) ⬜ needs footage

Line: VO, "She can see the debug layer." Camera on the tree with the wireframe world behind it — the VO's dawning is his own shot.

```
Leaves flutter and shiver on a 1.6 metre young banyan tree with woody bark as a teal wireframe world glows behind them. Close on the crown, the tree solid and warm against the cold lattice field beyond, night sky, faint mesh shimmer travelling through the background. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 23 — CENTURIES (1:48–1:55) ⬜ needs footage

Line: VO, "They've read the console for centuries and built a civilization around never admitting it." **The episode's central idea, and this is its picture:** the whole kingdom rendered as a console. Distant labels are post overlays.

```
A slow wide pan sweeps across an entire valley rendered in glowing teal wireframe — lattice fields, low-poly farmhouses, a mesh road running to a distant walled town. Vast establishing landscape at night, cold teal on indigo, scan shimmer travelling over the terrain, clear empty air above each distant roof. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 24 — WHEN THEY DISAGREE (1:55–2:01) ⬜ needs footage

Line: MAGISTRATE (quietly), "One of them gets corrected." Camera tight on her face beside the leaves — she is talking to the tree and to nobody else.

```
A woman in dark robes leans close to a young tree's trunk and speaks quietly, eyes still turned upward. Tight two-shot, her sharp profile one side of frame and the tree's leaves the other, teal light on both, two small figures far behind. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 25 — THE WINDOW CLOSES (2:01–2:05) ⬜ needs footage

No line. The overlay collapses; the world is ordinary again and the audience feels the loss of the layer.

```
The teal wireframe lattice collapses out of the world and solid warm dusk floods back across the clearing. Wide shot, the young tree, lean-to and cairn returning to normal colour, night settling, moths drifting, grass moving. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 26 — ROUTINE AGAIN (2:05–2:10) ⬜ needs footage

Line: MAGISTRATE, "Findings noted. Review pending." Camera on her being an official again — the whiplash is the joke.

```
A woman in dark robes turns briskly back to two waiting figures and tucks a ledger away under her arm, all business. Medium wide, warm dusk, the farmer and the goblin still standing in their unnecessary row, lantern-blue night behind. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 27 — AT THE ROAD (2:10–2:16) ⬜ needs footage

Line: MAGISTRATE, "Last time a ledger held a name the sky would not count—". Camera on her back — she does not turn around, and that is the shot.

```
A dark-robed figure stops walking at the edge of a road and stands with her back to camera, facing the dark. Rear medium shot from the clearing, her silhouette against a deep indigo sky, robe hem and chain moving in the wind, road disappearing ahead. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 28 — THE VALLEY (2:16–2:21) ⬜ needs footage

Line: MAGISTRATE (off), "—the sky stopped counting the whole valley." Camera on the valley she means: absolutely no lights in it.

```
Cloud shadow drifts across a wide dark valley at night with no lights anywhere in it, empty from ridge to ridge. Vast landscape, deep blue-black, faint starlight on bare hills, mist moving low in the bottom of the valley. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 29 — THE ARCHIVE MAP (2:21–2:26) ⬜ needs footage

Line: MAGISTRATE (off), "There are maps in the archive with a town on them." Camera on the map. Any town name is a post overlay, not generated.

```
Lamplight drifts across an old hand-drawn map lying under glass, brown ink hills and a small drawn town at its centre. Overhead close shot, aged paper grain, a moth shadow passing over the surface, dark archive room beyond the pool of light. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 30 — NOT PERMITTED (2:26–2:31) ⬜ needs footage

Line: MAGISTRATE, "A town I am not permitted to remember." Camera on her face giving nothing away.

```
A woman half-turns her head toward camera and gives nothing away, jaw set, one eyebrow flat. Tight close-up in profile-to-three-quarter, night behind her, a single cold highlight along her cheekbone, hair and robe collar moving in the wind. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 31 — BE COUNTABLE (2:31–2:36) ⬜ needs footage

Line: MAGISTRATE, "Be countable by harvest's end." Camera holds her and the tree in one frame — the order and the thing ordered.

```
A dark-robed woman turns her head just far enough to put a young banyan tree in her eyeline across the clearing. Wide two-shot, her in the near dark at the road and the 1.6 metre tree small and lit at the other side of frame, night grass rippling between them. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 32 — AMEND THE SKY (2:36–2:41) ⬜ needs footage

Line: MAGISTRATE, "I would rather amend the sky than the ledger." Camera on her face, the sky behind her — both nouns in one frame.

```
Cloud drifts across the last colour draining out of the sky behind a woman's face as she looks up, one eyebrow raised. Close-up, low angle so a wide band of dying indigo sky sits behind her head, clouds drifting, seal chain swinging at the bottom of frame. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 33 — NO ONE HAS TRIED (2:41–2:46) ⬜ needs footage

Line: MAGISTRATE (quieter), "No one has ever been permitted to try." Camera down on the seal in her hand — her authority, and its limit.

```
A woman's fingers close slowly around a heavy metal seal held low in her palm as she looks down at it. Close on the hand and the seal, night, one warm low light source, chain swinging gently, dark robe filling the background. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 34 — INTO THE DARK (2:46–2:50) ⬜ needs footage

No line. She leaves; the deadline stays.

```
A dark-robed figure walks away down a night road and the darkness swallows her, robes the last thing visible. Wide rear shot, the road running to a black horizon, dust lifting behind her steps, stars faint above. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 35 — TWO WEEKS (2:50–2:55) ⬜ needs footage

Line: VO, "Two weeks to convince the sky that I exist." Camera on the tree alone under the sky it has to convince.

```
Leaves hang almost motionless on a 1.6 metre young banyan tree as the last light drains off them, only the grass below still moving. Medium wide, the tree alone against a huge darkening sky that fills most of the frame, lean-to and cairn small at its feet. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 36 — THE HOOK (2:55–3:02) ⬜ needs footage

Line: VO, "I usually lost." Camera macro on one leaf as the light goes off it. Post smash-cuts to black on the last word and lays the end card.

```
The last light slides off a single broad banyan leaf and the leaf turns very slightly on its stem. Extreme close macro, leaf veins and woody twig, everything behind it falling to black, one point of starlight, air moving. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```
