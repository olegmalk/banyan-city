# Node 001 — shot list (15 shots, 1:1 with the script's beats)

Rebuilt 2026-07-27 when the founder restored the original first-person opening.
**One shot per beat, camera on the referent of that beat's line** (SCRIPT-SPEC.md).

Follows the two rules `style.md` records from the renderer: a shot is a **subject OR
a vista, never a small subject inside one** — SD1.5 draws the vista and drops the
subject — and prompt order is **subject, then setting as trailing tags, then style**,
because whatever leads becomes the composition.

Every prompt's first clause carries MOTION, because the animator is image-to-video:
it can only move what is already in the frame.

Base footage only: no burned-in text — post adds the captions, terminal cards and
status overlays. 9:16 vertical.

**Assembly:** `python3 pipeline/render_t3.py sapling 001 --clips <dir>`
**Free render:** `python3 pipeline/kaggle/run_remote.py push 001`

Status legend: ✅ generated · ⬜ needs footage

---

## Beat 01 — THE KEYBOARD (0:00–0:05) ⬜ needs footage

no dialogue - the sound is the cold open. Camera on the hands; the typing stopping is the cut.

```
1boy, solo, dark silhouette, glasses, messy hair, hood down, hands typing fast on a mechanical keyboard, one glowing monitor with code, dark apartment, night, city lights through blinds, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 02 — THREE OH SEVEN (0:05–0:11) ⬜ needs footage

Line: 'Production went down at 2:41.' Camera on the terminal - the machine is the referent.

```
1boy, solo, over the shoulder, dark silhouette, glasses, messy hair, hood down, large glowing monitor, terminal log text, mechanical keyboard, mug, dark apartment, 3am, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 03 — DEPLOY SUCCEEDED (0:11–0:16) ⬜ needs footage

no dialogue - post burns the deploy-succeeded card. Camera stays on the screen.

```
computer monitor close-up filling the frame, terminal window, command finishing, green success line, blinking cursor, dark room, deep blue glow, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 04 — THE FALL (0:16–0:21) ⬜ needs footage

no dialogue - the death, in one shot. The mug reaches the floor before he does.

```
1boy, solo, adult man, mature tired face, glasses, messy hair, collapsing sideways off a tipping chair at a desk, chair falling with him, eyes closing, a mug knocked off the desk mid-air, dark room, monitor glow, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No child, no kid, no blush, no wind. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 05 — HUH. GREEN. (0:21–0:24) ⬜ needs footage

Line: 'Huh. Green.' Camera low on the floor; the cooling fan winds down over black.

```
thick curved glazed ceramic shards of a broken coffee mug scattered flat on dark wooden floorboards, a puddle of spilled coffee, near darkness, dying screen glow, low camera angle, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No paper, no cards, no intact mug, no kintsugi. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 06 — TOO BLUE (0:24–0:29) ⬜ needs footage

Line: 'Hospital ceiling. Hospitals are green now.' The wrong-ceiling joke IS the shot.

```
extreme close-up of the underside of one giant green leaf filling the entire frame edge to edge, glowing backlit veins, tiny patches of vivid blue sky in the corners, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No woman, no girl, no person, no people, no figure, no grass. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 07 — FLAILING ONE (1) LEAF (0:29–0:36) ⬜ needs footage

Line: 'I appear to be flailing one (1) leaf.' The flail is the joke - camera on the leaf.

```
one tiny sprout alone in a grass field, its single leaf bent far over to one side, mid-motion, low angle, vivid blue sky, simple clear composition, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No people, no hands, no figure, no falling person, no trees. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 08 — SEV-1 (0:36–0:47) ⬜ needs footage

Line: 'Right. Sev-1.' Stillness arriving is the shot; post burns the terminal lines.

```
a single small leaf on a thin stem holding perfectly still, dust motes settling in sunlight around it, calm short grass, pale blue sky, quiet, low close shot, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 09 — WHOAMI (0:47–0:52) ⬜ needs footage

no dialogue - post types the whoami overlay over this frame.

```
a tiny two-leaf green sprout standing alone in short grass, centered, quiet empty composition, soft pale morning sky, gentle light, low close shot, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 10 — SENSE (0:52–1:02) ⬜ needs footage

Line: 'Sense. I can taste the water table.' Camera underground - the sense IS the image.
The pulsing footstep-RINGS are a POST overlay (deterministic, like the terminal cards) —
three founder-rejected rounds proved the model cannot be trusted to draw them.

```
dark underground soil texture filling the whole frame, side view, thin pale roots reaching down through the earth, small glowing blue water droplets between soil grains, quiet darkness, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No people, no cave, no portal, no eye, no sky, no lightning. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 11 — GROW (1:02–1:08) ⬜ needs footage

Line: 'Latency: three days. Throughput: one leaf.' Timelapse on the one new leaf.

```
macro close-up of a tiny green sprout, one brand new bright leaf unfurling at its tip, morning dew drops, soft golden morning light, gentle pale sky, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No people, no hands, no girl, no light trails, no tree. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 12 — UNDEFINED (1:08–1:11) ⬜ needs footage

Line: 'That is the whole API.' Camera on the strain that achieves nothing.

```
a single thin green plant stem bent into a tense arc, growing from cracked flat dirt ground, minimalist empty scene, pale grey sky, quiet, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No person, no figure, no cloak, no ghost, no sphere, no flowerpot. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 13 — I ALWAYS LEFT (1:11–1:20) ⬜ needs footage

Line: 'I walked away.' The road he can no longer take - no tree in this frame.

```
an empty dirt road running straight to a pale horizon across windswept grass fields, waves in the grass, drifting clouds, wide melancholic landscape, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 14 — WORTH STAYING IN (1:20–1:32) ⬜ needs footage

Line: 'I can only make this spot worth staying in.' The want of the series, as a grip.

```
macro close-up of thin white plant roots weaving between dark soil crumbs and gripping them tight, fine root hairs, warm low side light, sharp detail, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No fabric, no cloth, no feet, no skin, no people, no sky. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 15 — SOMETHING'S COMING (1:32–1:36) ⬜ needs footage

Line: 'Something is coming.' Camera underground; the footsteps are felt, not seen.
The approaching RINGS are a POST overlay, brighter/faster than beat 10's (same mechanism).

```
dark underground soil texture filling the whole frame at night, side view, pale roots reaching down, faint warm glow bleeding in from the right edge deep in the earth, dust grains suspended, ominous quiet, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No people, no figure, no cave, no portal, no eye, no sky, no comic panels. No photorealism, no 3D render look. 9:16 vertical, no text.
```
