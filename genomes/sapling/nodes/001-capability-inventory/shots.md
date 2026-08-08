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
no server room, no lab equipment` go to the negative.

REVISED AGAIN the same day, after that rewrite rendered. The house landed — all four
candidates were domestic — but not one of them had a terminal with a success line in
it. What they had was gibberish glyphs sprayed across the screen and anime-girl
desktop wallpaper behind them, in neon vaporwave: the only style break in a forty-
frame wave. The cause was in the code, not the words. `sd_prompt.suppressed_negatives`
lifted `text` out of the negative for any beat whose subject named a screen, so beat 3
— the one beat in the genome that rule ever fired on — was the one beat with nothing
fighting the junk. It now un-negates `text` only for a prompt that names the actual
words it wants drawn, which this one does not and should not: **screens in this show
are abstract glow.** Beat 1 has drawn "one glowing monitor with code" that way, with
`text` negated, since 2026-07-27, and this beat is written to match it — a bright
green line of code and a cursor, no words to read. `no wallpaper, no neon` go to the
negative for the vaporwave desktop; `no cubicle` comes off, the office reading died
with the old prompt and the budget is better spent. Measured on the real CLIP
tokenizer: positive 69 tokens, negative 55; on the deliberately pessimistic tag
estimate a machine without transformers falls back to, 74 and 58. Nothing dropped
either way, and `text` is back in the negative where the other 176 beats keep it.

```
close-up of a personal computer monitor on a cluttered home desk, dark terminal window on the glowing screen, one bright green line of code, blinking cursor, warm desk lamp, coffee mug, houseplant, lived-in bedroom corner at night, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No laboratory, no server room, no lab equipment, no person, no wallpaper, no neon. No photorealism, no 3D render look. 9:16 vertical, no text.
```

**REJECTED 2026-08-08 (founder, R4): ALL EIGHT — `b03-r1-s0..s3` AND `b03-r2-s0..s3`.**
Both rounds, the whole set. **NEW DIRECTION, his: make it a CLOSE-UP** — the third
instruction on this beat, and it is a lens note rather than a content note, so it
stacks on the two above rather than replacing them. The standing note still holds:
unmistakably indoors, domestic. Neither of the two rewrites is retracted; what
changes is the distance. A close-up also gives the domestic reading somewhere to
live at this size — a screen filling the frame with the warm lamp, the mug rim and
the room's edge just inside it, rather than a desk photographed from across a room.

**Not queued yet, and deliberately.** This redraw is GATED behind checklist item 07
with beats 6, 10, 14 and 15 — see the wave note at the foot of this file.
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

**REJECTED 2026-08-08 (founder, R4): ALL FOUR — `b06-r1-s0..s3`.** Recorded as
**rejected without a stated axis**: his words were that none of them quite work, and
he named no fault. That is a legitimate verdict and it is written down as what it is
rather than dressed in a reason we invented — do not attribute one to him later.

The redraw direction is therefore UNCHANGED from the rewrite above (no leaf, sky
shot; the leaf-is-him reasoning still stands) plus the one cross-cutting note that
came out of the same pass: **character consistency**, which was his dominant
objection across this whole wave. Beat 6 has no character in frame by construction,
so what it inherits from that note is the shared-anchor technique itself — whatever
item 07 settles for holding a design steady across shots is what this beat's sky,
light and palette get anchored to, so it stops being a frame from a different show.

**Not queued yet, and deliberately.** GATED behind checklist item 07 — see the wave
note at the foot of this file.
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

**REJECTED 2026-08-08 — the founder DELEGATED this one and the steward decided it
against the script, not against taste.** His note on `b10-r1-s3` was: *"actually has
character consistency, although it isn't exactly showing roots, so maybe it's not
aligning with the correct idea, you decide."* So the frame was offered on one virtue
(consistency) with one doubt (no roots), and the delegation is explicitly about
whether the doubt is fatal.

**The rule applied: are visible roots load-bearing for this beat's R1 state change or
its text, or are they incidental staging?** Load-bearing, on three counts, all of them
in `node.md` and none of them a matter of preference:

- The beat's own on-screen card is `SENSE   ✓  roots / air / vibration` — the word is
  printed over the picture. A frame with no roots in it makes the overlay contradict
  the plate.
- The beat's image line is *"He pushes attention downward and the image blooms: an
  underground root-map, veins of dark water, mineral glitter"* — the root-map IS the
  image the script asks for.
- The node's R1 is *"capabilities exactly two (sense, grow)"*, and this beat is the
  entire demonstration of the first one. Roots are the organ the sense runs on: the
  VO's *"I can taste the water table. I can feel the ground"* has no visible mechanism
  without them.

The 2026-08-07 rewrite that brought the camera up out of the ground kept `pale roots
at the surface` in the prompt for exactly this reason. So a candidate that drops them
fails the script, and the founder's stated virtue does not rescue it — **character
consistency is what the redraw must PRESERVE, not what it may trade the beat's
subject for.** REJECT; beat 10 joins the gated redraw wave.

**Redraw direction — both things at once, and that is the difficulty.** Keep whatever
made `b10-r1-s3` consistent, and get the roots back in frame: roots readable at the
surface where the stem meets the soil, damp earth, the episode's field and morning
light. And carry the note the checklist already raised — **10 and 14 came back as
very nearly the same picture** (same low angle, same two-leaf sprout, same warm soil)
because their rewritten directions are nearly the same words. More seeds will not fix
that. One of the two has to be re-lensed; this beat is the one that should move, since
14's *"Low at the base of the trunk"* is the script's own words and beat 10's framing
has already been moved once. Take 10 lower and closer — into the soil line rather than
standing off it — so the two read as different distances on different subjects.

**Not queued yet, and deliberately.** GATED behind checklist item 07 — see the wave
note at the foot of this file.
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

REVISED AGAIN the same day. The environment was fixed and the strain was not: all
four candidates came back calm and upright, a sprout standing straight in a nice
field. `bent into a tense arc, leaning hard and straining` is what the beat MEANS —
the trunk straining against nothing — and Animagine has no picture for any of it.
`tense`, `straining` and `hard` are states of mind; `arc` is geometry with no body
attached. The rewrite names only what the model can draw, in the physical vocabulary
that finally worked on 002b's leaf count: **bent low, taut curve, arched over almost
horizontal, leaf tips pulled down near the grass** — a shape, stated four ways, no
adverbs. And the prior it has to beat goes in the negative, which is where a "not" is
worth anything: `no upright stem`. The script's word is still the target ("The trunk
strains against nothing and nothing happens"); the prompt just stopped asking for it
in English. `no flowerpot` comes off to pay for `no upright stem` — the pot never
appeared in any of the four, and one term of budget buys the actual defect. Measured:
positive 69 tokens real / 75 estimated, nothing dropped. The NEGATIVE is at the
ceiling and was already — 76 of 77 real tokens, the same as the old prompt, and it
only lands there because the duplicated `text` deduplicates away first. On the
pessimistic estimate it goes over and sheds one HOUSE term (`realistic skin
texture`) while `no upright stem` survives untouched: the drop order doing its job,
since a term written for this beat outranks a global default. Any machine that can
render counts exactly, so the 76 is the number that ships.

```
plant focus, no humans, one tiny two-leaf sprout, its thin green stem bent low into a taut curve, arched over almost horizontal, leaf tips pulled down near the grass, damp brown soil, short green grass, sunlit field, pale blue morning sky, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No cracked ground, no dry dirt, no grey floor, no upright stem. No photorealism, no 3D render look. 9:16 vertical, no text.
```

**PICKED 2026-08-08 (founder, R4): `b12-r2-s1`.** The one pick in the whole wave.
`takes/stills/12-undefined-r2-s1.png` (seed 20261731, round 2) is promoted
byte-for-byte to `stills/12-undefined.png`, which is founder-approved canon and the
file every renderer actually reads — `video_task` globs `stills/NN-*.png` for its
conditioning frame and skips `REVOKED` names. The frame it replaces, the 2026-07-27
approval he refused on the cracked grey floor, is retired in place as
`stills/12-undefined-REVOKED-cracked-grey.png` rather than deleted, the way this
directory already carries 03, 07, 10, 14 and 15's revocations (R6). Checksum and
provenance: `stills/README.md`.

**THE RESERVATION HE ATTACHED, VERBATIM, AND THE PICK STANDS ANYWAY:** *"not sure
what it's supposed to be."* That is legibility, and it is the same complaint that
condemned beat 14 — so it is recorded here rather than filed as a compliment.
It is NOT a rejection and must not be read back as one: he named the frame, the frame
is canon, and nothing re-renders on the strength of the doubt. What it is is a flag on
the beat's whole conceit. The shot is a stem bending against nothing for three
seconds under the line *"That's the whole API"* — the strain reads as a shape long
before it reads as a *meaning*, and round 2 exists precisely because round 1 drew no
strain at all. If the assembled v33 comes back with the same note on this beat, the
lever is the beat's staging or its caption, **not** a fifth prompt: two rounds have
already established that Animagine draws the shape when asked for geometry and
nothing when asked for effort.
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

**REJECTED 2026-08-08 (founder, R4): ALL FOUR — `b14-r1-s0..s3`.** His words:
*"all too small, not good character consistency."* Two faults, and they are separate.

**Subject scale.** The rewrite above fixed legibility by putting the sprout back in
frame, and then framed it too far off: at 13.0 seconds this is the LONGEST slot in the
episode and the plant does not command it. The subject has to be bigger in frame —
the sprout and its grip filling the shot, ground and stones reading as the bed it
holds rather than as most of the picture. Note that `low close shot` is already in the
prompt and did not deliver it; the lever is composition wording (the plant occupying
the frame, close on the base) and not another synonym for "close".

**Character consistency**, the wave-wide objection. The sprout here has to be the same
plant as beats 6, 10, 11, 12 and 15 — same leaf count, same stem, same palette — and
across four seeds it is not. That is the fault item 07 is about, and it is why this
redraw waits rather than firing tonight.

Both hold together with the note the checklist already raised: **10 and 14 are near
twins.** 14 keeps its framing, because *"Low at the base of the trunk: roots gripping
soil"* is the script's own line; beat 10 is the one that moves. See beat 10 above.

**Not queued yet, and deliberately.** GATED behind checklist item 07 — see the wave
note at the foot of this file.

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

**REJECTED 2026-08-08 (founder, R4): ALL FOUR — `b15-r1-s0..s3`.** His words:
*"bad character consistency."* One axis, and it is the wave's axis.

The 2026-08-07 decision above is NOT reopened — surface level, the sapling as
protagonist, the presence entering as a warm glow from the right, nothing shown of
what is coming. He asked for the sapling and this is the beat that finally has one in
it; what he refused is that the sapling in it is not the sapling. This is the closing
frame of the episode and the last thing a viewer sees before the hook, so a plant that
does not match beats 6, 10, 11 and 12 breaks the identity at the worst possible
moment. Redraw direction: the composition unchanged, the character anchored by
whatever item 07 settles.

**Not queued yet, and deliberately.** GATED behind checklist item 07 — see the wave
note directly below.

---

## THE 2026-08-08 REDRAW WAVE — beats 3, 6, 10, 14, 15 — GATED, NOT QUEUED

The founder screened all forty candidate frames on 2026-08-08 and the wave produced
**one pick and five rejections**: `b12-r2-s1` is canon (beat 12 above), and beats 3,
6, 10, 14 and 15 need drawing again. Beat 7 is not in this list — it is answered by
the 7/8/9 progression, which is checklist item 03 and still open.

**Why nothing is rendering tonight, stated plainly, because the standing rule is that
a runnable job runs now.** This wave is not runnable. **Character consistency is the
founder's dominant objection** — he named it on 14 and 15 as the fault, and on 10 as
the one virtue that nearly saved a frame — and the technique that fixes it has not
been chosen. That choice is **checklist item 07**, the open question of whether
episode 2 gets a character sheet: one approved drawing the later beats are drawn
against. Episode 2 asked it first because eighty frames came back as twenty different
shows, but the answer governs episode 1's redraws too — the same model, the same
absence of an anchor, the same drift. Firing five redraws on the old technique before
that answer lands buys five more frames of five more shows and spends the founder's
next screening pass on a question he has already been asked.

So the gate is a real dependency and not a wait for office hours: the recipe is
undecided, and **ONE SAMPLE BEFORE ANY BATCH** applies to the technique the moment it
is. When item 07 is answered, the wave fires as one sample first, then the set.

Queue entry: `ep1-stills-redraw-wave2-*` in `pipeline/farm-queue.yaml` `backlog:`,
`gate: founder`, carrying each beat's direction. The per-beat directions are the
authority and live in the beat sections above.
