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

## Beat 01 — THE KEYBOARD (0:00–0:05) ⬜ needs footage01

no dialogue - the sound is the cold open. Camera on the hands; the typing stopping is the cut.

```
1boy, solo, dark silhouette, glasses, messy hair, hood down, hands typing fast on a mechanical keyboard, one glowing monitor with code, dark apartment, night, city lights through blinds, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 02 — THREE OH SEVEN (0:05–0:10) ⬜ needs footage02

Line: 'Production went down at 2:41.' Camera on the terminal - the machine is the referent.

```
1boy, solo, over the shoulder, dark silhouette, glasses, messy hair, hood down, large glowing monitor, terminal log text, mechanical keyboard, mug, dark apartment, 3am, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 03 — DEPLOY SUCCEEDED (0:10–0:15) ⬜ needs footage03

no dialogue - post burns the deploy-succeeded card. Camera stays on the screen.

```
computer monitor close-up filling the frame, terminal window, command finishing, green success line, blinking cursor, dark room, deep blue glow, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 04 — THE FALL (0:15–0:20) ⬜ needs footage04

no dialogue - the death, in one shot. The mug reaches the floor before he does.

```
close-up on the side of an office chair, a man's limp hand hanging straight down past the armrest, relaxed open fingers, motionless, sleeve of a rumpled shirt, papers settled on the dark floor below, cold monitor glow from above, dark room at night, dramatic shadows, shallow depth of field, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No face, no head, no full body, no horror, no blood, no standing. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 05 — FAN SPINNING DOWN (0:20–0:24) ⬜ needs footage05

NO DIALOGUE - the fan spin-down over near-black is the beat. 'Huh. Blue.' moved
to beat 06 where the blue actually appears (founder, 2026-08-03: 'yeah just move
it'). The picture here was always right; the LINE was in the wrong beat.

```
extreme macro close-up of two thick curved glazed ceramic shards lying flat on dark wooden floorboards, a thin dark spill soaking into the wood grain, almost no light, deep shadow, one weak cold grey glow from off frame, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No intact mug, no whole cup, no handle, no cup shape, no pink, no magenta, no red, no blood, no bright colours, no window, no doorway, no room, no furniture, no people, no paper, no cards, no kintsugi. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 06 — TOO BLUE (0:24–0:29) ⬜ needs footage06

Line: "Ceiling's gone. Open-plan hospital." The wrong-ceiling joke IS the shot — he is looking at open sky WITH clouds, so the gag is that he files it as architecture.

```
no humans, plant focus, pov from inside tall grass, camera on the ground pointing straight up, a vast flat clear blue morning sky filling most of the frame, soft out-of-focus grass blade tips fringing the very edges of the frame, one small green sprout leaf leaning into view at the bottom, one tiny wisp of cloud, gentle morning light, dreamy, detailed, newest, masterpiece, best quality, very aesthetic No 1girl, no girl, no boy, no person, no face, no eyes, no hair, no portrait, no big clouds, no forest, no tree, no abstract shapes. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 07 — ZERO (0) MOVING PARTS (0:29–0:35) ⬜ needs footage07

Line: 'I appear to have zero (0) moving parts.' The STILLNESS is the joke - camera
on the leaf, and the leaf does not move. Founder, 2026-08-03: the old flail
contradicted this episode's own `MOVE x undefined` card two beats later, and it
pre-spent 002b's ending. **Render this beat with `hold_still.py`, not the video
model** - a shot whose joke is that nothing can move must not be handed to a model
that has to put something in every frame.

REFRAMED 2026-08-04 (steward, flagged for the founder). The original prompt asked for
an "extreme close-up macro shot, one single young leaf... nearly filling the frame".
Four generations under it returned a mature branch carrying eight or more leaves,
even with `many leaves, leaf cluster, foliage, branch, woody trunk` all in the
negative: at macro framing this model reads "leaf" as "foliage" and no negative term
overrides it. Beat 08's still - "a single small leaf on a thin stem" at LOW CLOSE
framing - renders the sprout correctly and always has. So the framing moved to the
one that works, kept deliberately cool/overcast/flat so it does not duplicate beat
08's warm backlit grass two seconds later. The beat's job (one still sprout, nothing
moving) is unchanged; only the lens is.

```
no humans, plant focus, a tiny two-leaf sprout on one thin stem standing dead still, low close shot from just above the soil, sparse short grass, pale cool overcast sky, flat even light, dead calm air, nothing moving, detailed, newest, masterpiece, best quality, very aesthetic No macro close-up, no leaf filling the frame, no many leaves, no leaf cluster, no foliage, no branch, no woody trunk, no mature plant, no bush, no motion blur, no whipping, no bending, no wind, no sunset, no golden hour, no backlight, no person, no hands. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 08 — SEV-1 (0:35–0:48) ⬜ needs footage08

Line: 'Right. Sev-1.' Stillness arriving is the shot; post burns the terminal lines.

```
a single small leaf on a thin stem holding perfectly still, dust motes settling in sunlight around it, calm short grass, pale blue sky, quiet, low close shot, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 09 — WHOAMI (0:48–0:53) ⬜ needs footage09

no dialogue - post types the whoami overlay over this frame.

```
a tiny two-leaf green sprout standing alone in short grass, centered, quiet empty composition, soft pale morning sky, gentle light, low close shot, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 10 — SENSE (0:53–1:03) ⬜ needs footage10

Line: 'Sense. I can taste the water table.' Camera underground - the sense IS the image.
The pulsing footstep-RINGS are a POST overlay (deterministic, like the terminal cards) —
three founder-rejected rounds proved the model cannot be trusted to draw them.

```
macro close-up of dark wet soil at ground level, one pale thin root tip curling between the grains, clinging water droplets catching a faint blue light, damp earth texture sharp in the foreground, shallow depth of field, quiet, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No abstract shapes, no vertical streaks, no drips, no paint drips, no cross-section, no diagram, no cave, no tunnel, no doorway, no cave mouth, no black frame, no empty darkness, no people, no portal, no eye, no sky, no lightning, no god rays, no light shafts. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 11 — GROW (1:03–1:09) ⬜ needs footage11

Line: 'Latency: three days. Throughput: one leaf.' Timelapse on the one new leaf.

```
macro close-up of a tiny green sprout, one brand new bright leaf unfurling at its tip, morning dew drops, soft golden morning light, gentle pale sky, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No people, no hands, no girl, no light trails, no tree. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 12 — UNDEFINED (1:09–1:12) ⬜ needs footage12

Line: 'That is the whole API.' Camera on the strain that achieves nothing.

```
a single thin green plant stem bent into a tense arc, growing from cracked flat dirt ground, minimalist empty scene, pale grey sky, quiet, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No person, no figure, no cloak, no ghost, no sphere, no flowerpot. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 13 — I ALWAYS LEFT (1:12–1:21) ⬜ needs footage13

Line: 'I walked away.' The road he can no longer take - no tree in this frame.

```
an empty dirt road running straight to a pale horizon across windswept grass fields, waves in the grass, drifting clouds, wide melancholic landscape, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 14 — WORTH STAYING IN (1:21–1:34) ⬜ needs footage14

Line: 'I can only make this spot worth staying in.' The want of the series, as a grip.

```
macro close-up of pale thin roots wrapped tight around a clump of dark brown soil, fine root hairs gripping, crumbs of earth, warm low light raking across the surface, shallow depth of field, quiet, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No abstract shapes, no vertical streaks, no drips, no paint drips, no cross-section, no diagram, no cave, no tunnel, no doorway, no cave mouth, no black frame, no empty darkness, no people, no portal, no eye, no sky, no lightning, no god rays, no light shafts. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 15 — SOMETHING'S COMING (1:34–1:37) ⬜ needs footage15

Line: 'Something is coming.' Camera underground; the footsteps are felt, not seen.
The approaching RINGS are a POST overlay, brighter/faster than beat 10's (same mechanism).

```
macro close-up of dark soil and small stones at ground level, pale roots among them, strong warm orange light raking in from the right side and lighting the grains clearly, long shadows stretching left, loose dust, ominous, well lit, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No abstract shapes, no vertical streaks, no drips, no paint drips, no cross-section, no diagram, no cave, no tunnel, no doorway, no cave mouth, no black frame, no empty darkness, no people, no portal, no eye, no sky, no lightning, no god rays, no light shafts. No photorealism, no 3D render look. 9:16 vertical, no text.
```
