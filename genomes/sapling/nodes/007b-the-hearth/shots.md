# Node 007b — shot list (36 shots, 1:1 with the script's beats)

Rebuilt 2026-08-10 for `007b-t0-b`. The previous list was **5 shots for the
whole episode**, and its worst offender was the investigation: four days of
findings sat in one code block under one held image. Each day is now its own
picture. This list is **one shot per beat, 4–7s, camera on the referent of
that beat's line** (SCRIPT-SPEC.md "one beat = one shot").

Base footage only: no burned-in text, no dialogue — post adds captions, VO and
every sky-label overlay. 9:16 vertical. Each prompt's FIRST sentence states the
primary action (motion grammar, `../../style.md`).

**Growth ladder (`../../style.md`):** 007b sits at the same rung as 006b and
its 006a/007a siblings — **~1.6 m young tree**, full small crown, first woody
bark, side branches. Never "sapling", never "tiny": from 004 the comedy is
bureaucratic, not physical.

**Character continuity (anime model sheet, `../../style.md`):** the SCAVENGER
is a small round goblin — enormous ears that act like a second face, one
broken tusk, huge expressive eyes, faded green patchwork cloak. The FARMER is
a broad squarish silhouette in a straw hat, three lines for his whole face,
permanently unimpressed. Beside the tree: a crooked lean-to, a three-stone
cairn, a clay jug, and from beat 17 a small ring of stones between the roots.

**The sunset window** is the same overlay canon as 004 and 006b: the solid
world flickers into a glowing teal wireframe. **Every label, dialog box and
system line is a post overlay, never generated** — the prompts ask for the
wireframe world with clear empty air where the text will sit. That includes
beats 26 and 28–32, which are structured so the overlay has somewhere to land.

**The fire is the episode's other continuity object:** small, deliberately
ringed, sitting in soil between the roots of a tree made of wood. Every shot
from beat 21 onward that includes the tree also includes that fire.

**Token budget — RE-MEASURE BEFORE GENERATING.** Checked 2026-08-10 through
`sd_prompt.compress()`, the same call `farm_worker` makes, but **on a machine
with no CLIP tokenizer**, so the count was the module's deliberately
pessimistic prose estimate. Under that reading no prompt here loses a
*content* sentence — the three longest (beats 01, 18, 26) were shortened until
none did. What the estimate cannot settle is the booster tail (`masterpiece,
best quality, very aesthetic`), whose silent loss is recorded in 002b's shot
list and cost this repo a batch of flat, pale frames on 2026-07-26. Re-run the
check on a box with the real tokenizer before any batch.

**Assembly:** save each clip as `NN-slug.mp4` in a clips dir, then
`python3 pipeline/render_t3.py sapling 007b --clips <dir> --out ep.mp4`

**Not renderable yet.** `007b-t0-b` carries no `approved_by` — STEWARDSHIP.md
§6 forbids voice, footage or assembly from this node until the founder has read
the script.

Status legend: ✅ generated · ⬜ needs footage

---

## Beat 01 — COLD OPEN (0:00–0:06) ⬜ needs footage

Line: VO, premise. Camera on the goblin taking dictation from a tree inside the wireframe — one shot that states the whole absurd situation.

```
A small round goblin leans over a bark slab and scratches at it with a charcoal stick, taking dictation from a young banyan tree beside him. Medium shot at sunset, the world around them a glowing teal wireframe lattice, the two of them solid and warm, grass mesh rippling. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 02 — DICTATION (0:06–0:11) ⬜ needs footage

Line: VO, "you find out what the counter counts." Camera tight on the leaves tilting and the charcoal chasing them — the protocol in one frame.

```
Two broad leaves tilt sharply, once and then again, while a charcoal stick scratches after them across bark just below. Tight close-up, leaves and slab sharing the frame, teal wireframe glow behind, charcoal dust drifting. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 03 — FOUR CHARACTERS (0:11–0:16) ⬜ needs footage

No line. The joke is the ratio: a whole day's window, four marks. The marks themselves are post overlay; the shot is the empty bark.

```
The teal lattice drains out of the world and warm dusk floods back as a bark slab drops into frame, nearly empty, held in two green clawed hands. Close overhead shot of the slab, a few charcoal smudges at the top and a great deal of blank bark below, hands trembling slightly. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 04 — THREE SECONDS A DAY (0:16–0:20) ⬜ needs footage

Line: VO, "three seconds per day." Camera on the stack — the data set, and how small it is.

```
A goblin's hand slides one more bark slab onto a leaning stack of slabs propped against tree roots. Close low angle at ground level, dusk, the pile visibly wobbling, dry grass moving around it. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 05 — SLOWER DASHBOARDS (0:20–0:25) ⬜ needs footage

Line: VO, "they were at least *paid* for." Camera on the goblin's face over the pile.

```
A small round goblin leans over a stack of bark slabs and counts them with one claw, ears drooping further with each one. Close-up, huge expressive eyes, one broken tusk, faded green patchwork cloak, warm dusk light, dust in the air. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 06 — DAY ONE (0:25–0:29) ⬜ needs footage

Line: VO, "the farmhouse: dwelling, hearth one." Camera on the farmhouse in wireframe with clear air above the roof for the post label.

```
Smoke climbs from the chimney of a distant farmhouse rendered in glowing teal wireframe, the only warm thing in a cold lattice field. Wide shot across the valley at last light, low-poly roof and mesh walls, clear empty sky above the building, scan shimmer travelling through the grass. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 07 — DAY TWO (0:29–0:33) ⬜ needs footage

Line: VO, "our lean-to: structure, question mark." Camera on the lean-to in wireframe, clear air above it.

```
A crooked deadfall lean-to sags in the wind, rendered as a sparse teal wireframe of loose lines that barely hold together. Medium shot, cold mesh against indigo night, empty air above the structure, wireframe grass rippling at its base. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 08 — DAY THREE (0:33–0:39) ⬜ needs footage

Line: VO, "the sky is unsure about *rocks*." Camera on the cairn — the absurdity is that this thing gets a label at all.

```
Three stacked stones sit rendered as a blocky low-poly cairn while the teal lattice shimmers over them and wireframe grass ripples around the base. Close medium shot, cold mesh on a dark field, clear empty air above the stones, faint scan lines moving upward. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 09 — DAY FOUR (0:39–0:44) ⬜ needs footage

Line: VO, "the farmer stands still, and is counted." Camera on the farmer inside the wireframe, the count tick added in post beside him.

```
A broad farmer in a straw hat stands motionless in his field while the teal wireframe world ripples and shifts around him, only his hat brim and the mesh grass moving. Medium wide, the farmer solid and warm against a cold lattice landscape, clear air beside his shoulder. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 10 — AND ME (0:44–0:48) ⬜ needs footage

Line: VO, "I stand still. I am not." Camera on the tree, matched to beat 09's framing — the whole finding is the cut between these two shots.

```
Leaves breathe faintly on a 1.6 metre young banyan tree standing motionless as the teal wireframe world ripples around it, nothing rendering beside it at all. Medium wide matched exactly to the previous shot's framing, the tree solid and warm against cold lattice, clear empty air at its shoulder. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 11 — THE CASE BOARD (0:48–0:54) ⬜ needs footage

Line: VO, "It counts *fires*." Camera on the evidence board. Findings are post overlay on the blank bark.

```
A goblin turns a large bark slab around toward camera and holds it up, charcoal marks running down it in four rough rows. Close on the slab filling most of the frame, warm dusk, his ears and eyes just visible over the top edge, dust drifting. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 12 — A PERSON IS A HEARTH (0:54–0:58) ⬜ needs footage

Line: VO, "A person is where their hearth is." Camera on the smoke — the answer, in solid world now.

```
Smoke climbs steadily out of a stone farmhouse chimney and drifts sideways into a darkening sky. Close medium shot on the chimney against deep dusk, warm orange light leaking from a window below, smoke curling. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 13 — THE HEARTH TAX (0:58–1:03) ⬜ needs footage

Line: VO, "the kingdom taxes by hearth." Camera on the kingdom's own paperwork. Column headings are post overlay.

```
A kingdom notice nailed to a roadside post flutters and snaps in the wind, its ruled columns and inked tally marks catching the last light. Close shot, weathered paper and rusted nail, dusk field blurred behind, edges of the paper lifting. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 14 — A CACHED COPY (1:03–1:09) ⬜ needs footage

Line: VO, "a *cached copy of the schema*… called tradition." The idea's own picture: the kingdom and the console are the same shape. Distant labels are post overlays.

```
A slow wide pan sweeps across a whole valley of teal wireframe farmhouses, each identical low-poly roof carrying the same empty patch of air above it. Vast establishing landscape at night, cold mesh terrain on indigo, a walled town in mesh far off, scan shimmer rolling over the hills. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 15 — THE ASSIGNMENT (1:09–1:13) ⬜ needs footage

Line: SCAVENGER, "You want a *fire*. Next to *you*." Camera on him reading the instruction.

```
A small round goblin's ears drop all the way down as he reads a bark slab held in both hands, eyes travelling across it and stopping. Close-up, huge expressive eyes, one broken tusk, warm dusk, faded green patchwork cloak, air moving. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 16 — KINDLING WITH OPINIONS (1:13–1:18) ⬜ needs footage

Line: SCAVENGER, "*kindling with opinions*." Camera stays on his face — the episode's best joke gets the close-up it never had.

```
A goblin throws one hand up in apology mid-sentence, appalled, his enormous ears flaring outward. Tight close-up, huge expressive eyes and one broken tusk filling the frame, warm dusk rim light, background thrown soft. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 17 — THE STONES (1:18–1:23) ⬜ needs footage

No line. He builds it anyway — the terror is in the hands.

```
Green clawed hands lower a stone slowly into soil between thick tree roots and set it beside two others, dust rising where it lands. Extreme close at ground level, woody roots and dark earth, dusk light, dust lifting where the stone lands. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 18 — THE FIRE BRIGADE (1:23–1:27) ⬜ needs footage

Line: FARMER, "One spark and your whole religion is charcoal." Camera on the farmer and the jug — the threat and the mitigation in one frame.

```
A broad farmer in a straw hat plants his feet beside a half-built stone ring and hefts a full clay jug against his hip, water spilling at the rim. Medium shot, unimpressed posture, three lines for his whole face, dusk field, tree roots at frame edge. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 19 — ROOMMATE (1:27–1:31) ⬜ needs footage

Line: SCAVENGER, "He's my roommate." Camera on the goblin defending the arrangement.

```
A small round goblin throws both arms wide in defence of the arrangement, ears up, chest out. Medium close, huge expressive eyes, patchwork cloak swinging with the gesture, warm dusk, the stone ring and roots behind him. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 20 — WORSE (1:31–1:35) ⬜ needs footage

Line: FARMER, "Worse." Camera on the farmer not moving a muscle. Secondary motion carries the hold.

```
A farmer in a straw hat stands completely still holding a full jug while smoke and dust drift past him and the grass ripples at his boots. Close medium shot, three lines for his whole face, hat brim shifting slightly in the wind, deep dusk behind. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 21 — THE FLAME CATCHES (1:35–1:40) ⬜ needs footage

No line. The event of the episode.

```
A small flame catches inside a ring of stones, rises, and steadies into a steady burning point of orange. Extreme close at ground level between thick tree roots, dark soil, sparks lifting, warm light spreading out across the earth. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 22 — THE LEAVES PULL BACK (1:40–1:44) ⬜ needs footage

Line: VO, "There is a fire inside my root perimeter." Camera on the tree's reaction — its only means of acting.

```
Every leaf on a 1.6 metre young banyan tree pulls visibly back and curls away from a small fire burning at its base. Medium shot up the trunk, warm orange light thrown upward across woody bark and leaf undersides, night behind, smoke drifting. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 23 — WORST UPTIME STRATEGY (1:44–1:51) ⬜ needs footage

Line: VO, "the worst uptime strategy I have ever personally approved." Camera at the trunk's own eye level, far too close to the flame.

```
Firelight flickers hard across woody bark from a few centimetres away as the flame moves in the stone ring just beyond it. Extreme close on the trunk surface with the fire burning out of focus behind, deep orange and black, sparks drifting up through frame. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 24 — SUNSET (1:51–1:55) ⬜ needs footage

No line. The window opens on the night the fix is tested.

```
The sun drops to the horizon and a teal wireframe lattice blooms out across the whole field, overtaking the grass in a wave. Wide shot of the clearing, the small fire a single warm point among the cold mesh, the young tree in silhouette, scan shimmer spreading. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 25 — THE LEAN-TO RE-RENDERS (1:55–2:00) ⬜ needs footage

No line. Its label rewrites (post overlay) and the settlement label begins to flicker beyond it — keep both patches of air clear.

```
A wireframe lean-to brightens and its mesh redraws itself line by line while further back the air over the clearing begins to flicker. Medium shot, teal lattice on indigo, the small fire glowing warm inside the mesh, empty air above the lean-to and above the clearing. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 26 — THE DIALOG (2:00–2:05) ⬜ needs footage

No line. The first dialog the tree has ever been shown. The box itself is a post overlay — the shot must leave the air above the trunk clear.

```
Light gathers and pulses in the empty air just above a young banyan tree's crown, as though something is opening there. Low medium shot, the tree solid inside teal wireframe surroundings, a great deal of clear dark air above the crown, embers rising below. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 27 — SEVENTEEN HOURS (2:05–2:10) ⬜ needs footage

Line: VO, "someone took seventeen hours." Camera tight on the leaves beside the (post-added) dialog — the thing being asked.

```
Two broad leaves hang and turn very slightly beside a patch of pulsing empty air. Tight close-up, leaves at one side of frame and clear dark space at the other for the dialog, cold teal light on the leaf edges, warm firelight from below. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 28 — THE HOURS BACK (2:10–2:14) ⬜ needs footage

Line: VO, "You never get the hours back." Camera on the leaves gathering — the decision being made, before it lands.

```
Leaves gather and tense along a branch, pulling back the way an arm pulls back. Close on the branch, teal light above and orange firelight below, the whole crown tightening, air moving through it. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 29 — Y (2:14–2:18) ⬜ needs footage

No line. The instant answer — the whole character arc in one movement.

```
One leaf swings up hard and strikes a point of light in the air above the crown, instantly and without hesitation. Close medium shot, the leaf blurred with speed, a bright flare at the point of contact, teal wireframe world behind, embers scattering. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 30 — THE CASCADE (2:18–2:23) ⬜ needs footage

No line. Labels cascade in post; the shot gives them a clear column of air to cascade through.

```
Pulses of teal light run upward through the air above the clearing one after another, each brighter than the last. Wide upward-looking shot, wireframe rooftops and treetops along the bottom edge, most of the frame clear dark sky, light rippling through it. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 31 — NO QUESTION MARK (2:23–2:28) ⬜ needs footage

Line: VO, "The sky is *sure* about us." Camera on the settlement label's patch of sky as it settles — post writes `SHADE · settlement · pop. 3`.

```
The rippling light over the clearing settles and holds steady, the flicker going out of it. Wide upward shot over the whole wireframe settlement, tree, lean-to and cairn in mesh along the bottom, a broad band of clear steady-lit air above them. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 32 — THE LAST LINE (2:28–2:33) ⬜ needs footage

No line. The hook renders in the corner as the window dies — keep the lower corner clear and let the eye be drawn away from it.

```
The teal lattice begins to fail and dim across the clearing, the mesh dropping out in patches. Wide shot, the world half solid and half wireframe, one bottom corner of frame deliberately empty and dark, the small fire steady at the centre, embers rising. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 33 — LOGGED (2:33–2:37) ⬜ needs footage

Line: VO, "Logged." Camera on the ordinary world coming back — and the fire still burning in it.

```
The wireframe drops out of the world and warm night floods back over the clearing, crickets in the grass. Medium wide, the small ringed fire burning between the roots of the young tree, moths drifting through the light, everything else dark. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 34 — THE CHEER (2:37–2:42) ⬜ needs footage

No line. Both characters, both reactions, one frame: the victory nobody but the tree can read.

```
A small goblin throws both fists up and cheers at the night sky while beside him a farmer pours a careful arc of water in a circle around a fire pit. Wide two-shot, warm firelight from below on both of them, night field behind, water catching the light as it falls. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 35 — THE OTHER SIDE (2:42–2:47) ⬜ needs footage

Line: VO, "the other side of that word." Camera holds on the fire — small, ringed, and now an entry in something.

```
Flames sway slowly inside a ring of stones, embers lifting one at a time into the dark. Extreme close at ground level between tree roots, deep orange on black, ash drifting, the ring of stones catching the light. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 36 — THE HOOK (2:47–2:53) ⬜ needs footage

Line: VO, "Something tails this log." Camera pulls the dark down over the fire. Post smash-cuts to black on the last word and lays the end card.

```
Embers drift upward from a small ringed fire and go out one by one as the dark closes over the frame above them. Low wide shot, the fire tiny at the bottom of frame and an enormous black night filling the rest, faint smoke rising into nothing. Cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic. No photorealism, no 3D render look. 9:16 vertical, no text.
```
