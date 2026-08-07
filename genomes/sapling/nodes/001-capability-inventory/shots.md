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

REWRITTEN 2026-08-07 to the founder's verdict: *"Beat 3 looks more like a terminal
in some.. lab. not realistic. whatever you intended it to be, you should make a new
image for it and make sure it looks like its inside a house."* The old prompt gave
the model a monitor, a dark room and a deep blue glow and nothing domestic at all —
which is the description of a lab bench. The screen is now a PERSONAL computer on a
home desk: warm lamp, mug, houseplant, a bedroom corner behind it. `no laboratory,
no server room, no lab equipment` go to the negative; the terminal stays the
subject (so `sd_prompt` keeps un-negating `text` for this beat).

```
close-up of a personal computer monitor on a cluttered home desk, terminal window, a command finishing, green success line, blinking cursor, warm desk lamp glow, coffee mug, houseplant, a lived-in bedroom corner at night, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No laboratory, no server room, no lab equipment, no cubicle, no person. No photorealism, no 3D render look. 9:16 vertical, no text.
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

REWRITTEN 2026-08-07 to the founder's verdict: *"for beat 6, there shouldnt be a
leaf in the image, doesnt make sense that he can see himself when he is looking at
the sky."* Correct — the leaf leaning into frame was HIM, and a first-person POV
cannot contain its own body. The whole foreground is gone: open sky, one drifting
wisp, and only a soft blurred green fringe at the very bottom edge to place the
camera on the ground. `no leaf, no plant, no stem` are in the negative now.

```
a vast open sky filling the frame seen from ground level looking straight up, no humans, deep clear blue morning sky, one thin wisp of white cloud drifting high above, a soft blurred green fringe of grass along the bottom edge, gentle morning light, dreamy, detailed, newest, masterpiece, best quality, very aesthetic No leaf, no plant, no stem, no foliage, no big clouds, no tree. No photorealism, no 3D render look. 9:16 vertical, no text.
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

RE-PALETTED 2026-08-07 to the founder's verdict: *"beat 7 makes everything look
grayened. thats not a bad thing but the main problem is that it drastically changes
the style."* The cool/overcast wording above was the steward's own device for
separating 7 from 8 — and it bought that separation with a palette break the
founder can see from across the room. Stillness is kept (dead calm air, nothing
moving); the grey is not. The episode's morning palette is back, `no grey sky, no
overcast` are in the negative, and the 7/8/9 separation moves to the place it
belongs — the LENS, in the progression set below.

```
plant focus, no humans, a tiny two-leaf sprout on one thin stem standing dead still, low close shot from just above the soil, short green grass, pale blue morning sky, soft morning light, one thin cloud drifting, dead calm air, nothing moving, detailed, newest, masterpiece, best quality, very aesthetic No macro close-up, no many leaves, no grey sky. No photorealism, no 3D render look. 9:16 vertical, no text.
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

REWRITTEN 2026-08-07 to the founder's verdict: *"for beat 10, another major style
change and it looks a sapling in the middle of a long body of water, with a blank
dark background."* The macro-underground framing had no horizon, no grass and no
daylight in it, so "wet soil under faint blue light" resolved as a plant standing in
water against black. The camera comes up to the plant's own base: the sense is
shown where the sprout meets the ground, in the episode's field and its morning
light, with the water read as droplets in the earth rather than a surface. Rings
remain a POST overlay.

```
plant focus, no humans, low shot at the base of a tiny two-leaf sprout, damp dark soil around its stem, pale roots at the surface, water droplets in the earth, short green grass at the frame edges, soft warm morning light, shallow depth of field, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No lake, no water surface, no dark background, no black void, no cave. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 11 — GROW (1:03–1:09) ⬜ needs footage11

Line: 'Latency: three days. Throughput: one leaf.' Timelapse on the one new leaf.

```
macro close-up of a tiny green sprout, one brand new bright leaf unfurling at its tip, morning dew drops, soft golden morning light, gentle pale sky, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No people, no hands, no girl, no light trails, no tree. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 12 — UNDEFINED (1:09–1:12) ⬜ needs footage12

Line: 'That is the whole API.' Camera on the strain that achieves nothing.

REWRITTEN 2026-08-07 to the founder's verdict: *"beat 12 follows the style well but
looks like the sapling is in a dark place, with a dry cracked and gray floor,
completely changes the enviroment, gotta regenerate that."* The prompt asked for
exactly that: `cracked flat dirt ground, pale grey sky`. Both are gone — the strain
happens in the same green field, damp soil and morning light as every other outdoor
beat, and the cracked-desert reading is in the negative.

```
plant focus, no humans, a single thin green stem of a tiny sprout bent into a tense arc, leaning hard and straining, rooted in damp brown soil among short green grass, open sunlit field, pale blue morning sky, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No cracked ground, no dry dirt, no grey floor, no flowerpot. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 13 — I ALWAYS LEFT (1:12–1:21) ⬜ needs footage13

Line: 'I walked away.' The road he can no longer take - no tree in this frame.

```
an empty dirt road running straight to a pale horizon across windswept grass fields, waves in the grass, drifting clouds, wide melancholic landscape, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 14 — WORTH STAYING IN (1:21–1:34) ⬜ needs footage14

Line: 'I can only make this spot worth staying in.' The want of the series, as a grip.

REWRITTEN 2026-08-07 to the founder's verdict: *"beat 14 is.. i dont know what?? what
is it supposed to be? i think you need to regenerate it."* That is a legibility
failure, not a taste one, and the prompt caused it: a macro crop of "roots wrapped
around a clump of soil" with no plant, no ground plane and no horizon in it has
nothing in frame to tell a viewer what they are looking at — it reads as texture.
The script's line is *"Low at the base of the trunk: roots gripping soil"*, so the
subject is restored: the sprout is IN the shot, stem rising out of the earth, roots
gripping down into it, field behind. The grip is legible because the thing gripping
is visible.

```
plant focus, no humans, low close shot at the base of a tiny two-leaf sprout, thin stem rising out of the ground, pale roots gripping into damp brown soil, small stones and short grass around it, warm afternoon light raking across the earth, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No cross-section, no diagram, no cave, no black void. No photorealism, no 3D render look. 9:16 vertical, no text.
```
## Beat 15 — SOMETHING'S COMING (1:34–1:37) ⬜ needs footage15

Line: 'Something is coming.' The footsteps are felt, not seen. The approaching RINGS
are a POST overlay, brighter/faster than beat 10's (same mechanism).

REWRITTEN 2026-08-07. The founder: *"for beat 15, why is it showing the underground?
i think it should show the sapling, no? well, you can decide."* Decided — surface
level, sapling as protagonist. The camera comes up out of the soil and sits with him
in the grass; the arriving presence enters the frame as a hard warm glow spilling in
from the right edge with the ground trembling under it, so the episode ends on the
character something is walking toward rather than on dirt. Nothing is shown of what
is coming, which is the hook (`no person, no figure, no monster` in the negative).

```
plant focus, no humans, a tiny two-leaf sprout standing at ground level in short grass, loose soil grains scattering around its base, a strong warm orange glow spilling in from the right edge of frame, long shadows stretching left, evening field, ominous, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No underground, no cave, no black void, no figure, no monster. No photorealism, no 3D render look. 9:16 vertical, no text.
```
