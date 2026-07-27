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
Vertical 9:16 close shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. A pair of hands hammering fast on a mechanical keyboard in near-darkness, keys visibly moving, faint monitor glow on his knuckles, dark room, deep indigo. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 02 — THREE OH SEVEN (0:05–0:11) ⬜ needs footage

Line: 'Production went down at 2:41.' Camera on the terminal - the machine is the referent.

```
Vertical 9:16 close shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. A spinner turning steadily in a terminal window filling a dark monitor, cold teal light flickering across it, a hunched silhouette faintly reflected, 3am apartment. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 03 — DEPLOY SUCCEEDED (0:11–0:16) ⬜ needs footage

no dialogue - post burns the deploy-succeeded card. Camera stays on the screen.

```
Vertical 9:16 close shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. A terminal spinner resolving and settling into a finished line, cursor blinking softly after it, cold teal screen glow, dark room. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 04 — THE FALL (0:16–0:21) ⬜ needs footage

no dialogue - the death, in one shot. The mug reaches the floor before he does.

```
Vertical 9:16 medium shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. A hunched man at a desk tipping sideways out of his chair while a mug topples off the desk edge and falls, papers lifting, dark room, cold monitor light. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 05 — HUH. GREEN. (0:21–0:24) ⬜ needs footage

Line: 'Huh. Green.' Camera low on the floor; the cooling fan winds down over black.

```
Vertical 9:16 close shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. A ceramic mug shattering on a wooden floor in near-darkness, fragments scattering outward, the last monitor light dying. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 06 — TOO BLUE (0:24–0:29) ⬜ needs footage

Line: 'Hospital ceiling. Hospitals are green now.' The wrong-ceiling joke IS the shot.

```
Vertical 9:16 low close shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. One enormous green leaf trembling and shaking in the wind, so close it fills almost the entire frame edge to edge, seen from directly beneath against a flat impossibly blue sky. No grass, no field, no other leaves, no plants, no clouds. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 07 — FLAILING ONE (1) LEAF (0:29–0:36) ⬜ needs footage

Line: 'I appear to be flailing one (1) leaf.' The flail is the joke - camera on the leaf.

```
Vertical 9:16 low close shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. A single leaf on a thin stem whipping and flailing wildly while everything around it stays motionless, calm grass, shaky handheld camera following it, blue sky. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 08 — SEV-1 (0:36–0:47) ⬜ needs footage

Line: 'Right. Sev-1.' Stillness arriving is the shot; post burns the terminal lines.

```
Vertical 9:16 low close shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. One leaf coming to a complete stop and holding still on its stem, faint dust settling around it, calm grass, pale blue sky behind. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 09 — WHOAMI (0:47–0:52) ⬜ needs footage

no dialogue - post types the whoami overlay over this frame.

```
Vertical 9:16 low close shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. A small green two-leaf seedling standing quietly in short grass, leaves barely stirring, soft pale sky, clean empty composition. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 10 — SENSE (0:52–1:02) ⬜ needs footage

Line: 'Sense. I can taste the water table.' Camera underground - the sense IS the image.

```
Vertical 9:16 underground cross-section, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. A solid wall of dark soil filling the entire frame, seen from the side like a cutaway, pale thin roots threading down through it while glinting water veins and rings of light pulse sideways through the earth toward them, mineral specks catching. No sky, no stars, no lightning, no outer space, no horizon. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 11 — GROW (1:02–1:08) ⬜ needs footage

Line: 'Latency: three days. Throughput: one leaf.' Timelapse on the one new leaf.

```
Vertical 9:16 close shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. A tight green bud on a thin stem unfurling into a new leaf while light sweeps across it repeatedly, shadows swinging fast, clouds streaking behind. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 12 — UNDEFINED (1:08–1:11) ⬜ needs footage

Line: 'That is the whole API.' Camera on the strain that achieves nothing.

```
Vertical 9:16 close shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. A thin sapling stem in open ground straining and bowing hard against nothing, roots pulling taut in bare soil, grass still, nothing else moving, pale sky. No flowerpot, no planter, no windowsill, no indoors. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 13 — I ALWAYS LEFT (1:11–1:20) ⬜ needs footage

Line: 'I walked away.' The road he can no longer take - no tree in this frame.

```
Vertical 9:16 wide shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. An empty dirt road running away across grass toward a pale horizon, wind moving the grass in waves, drifting clouds, no traveller on it. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 14 — WORTH STAYING IN (1:20–1:32) ⬜ needs footage

Line: 'I can only make this spot worth staying in.' The want of the series, as a grip.

```
Vertical 9:16 low macro shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. Thin pale roots gripping dark crumbling soil and tightening, loose grains shifting, grass blades moving around the stem, warm low raking light, shallow focus. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 15 — SOMETHING'S COMING (1:32–1:36) ⬜ needs footage

Line: 'Something is coming.' Camera underground; the footsteps are felt, not seen.

```
Vertical 9:16 underground cross-section, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds, gentle pastel-leaning palette. A solid wall of dark soil filling the entire frame, seen from the side like a cutaway, rings of light pulsing sideways through the earth toward pale thin roots, brighter and faster with each pulse, soil grains trembling. No sky, no stars, no comet, no outer space, no horizon. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```
