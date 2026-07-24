# Node 001 — shot list (per-beat generation prompts)

Shot list for the **molt-successor script** (`001-t0-b`, SCRIPT-SPEC.md,
2026-07-25) — one generation prompt per script beat, assembled by
`pipeline/render_t3.py`. Base footage only (no burned-in text, no dialogue —
post adds terminal overlays and VO), 9:16 vertical, ~10s per shot.
The previous 5-beat shot list (t0-a era) is preserved in git history; the
published t3 leaves were assembled from its clips.

**Naming for assembly:** save each clip as `NN-slug.mp4` in a clips dir, where
`NN` is the beat number below, then:
`python3 pipeline/render_t3.py sapling 001 --clips <dir> --out episode.mp4`

Status legend: ✅ generated · ⬜ needs footage

---

## Beat 01 — COLD OPEN (0:00–0:05) ⬜ needs footage

```
Vertical 9:16 macro shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette. A tiny mascot-simple banyan sapling — thin curved trunk, two oversized expressive leaves, no face; all its acting is leaf angle — trembles in the wind, filling the lower half of the frame, alone in a vast green field under a huge flat watercolor sky. The leaves shake and steady, shake and steady, as gusts comb waves through simplified grass. Morning light, peach and gold washes. No photorealism, no 3D render look, no heavy texture. No text.
```

## Beat 02 — THE CRASH (0:05–0:15) ⬜ needs footage

```
Vertical 9:16 shot, night interior, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette. A tired male engineer in his 30s sways and collapses sideways out of frame mid-keystroke; his ceramic mug tips off the desk and falls with him. A cramped dark apartment washed in flat deep indigo, lit only by the cold teal glow of a computer monitor full of red error text. Simple slumped silhouette, a few clean lines for an exhausted face, 3 a.m. exhaustion. Static camera holds on the empty chair and glowing monitor after he falls. No photorealism, no 3D render look, no heavy texture. No text.
```

## Beat 03 — REBOOT (0:15–0:25) ⬜ needs footage

```
Vertical 9:16 shot from ground level, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette. A small round bird flutters down and lands on the top leaf of a tiny mascot-simple banyan sapling — thin curved trunk, two oversized expressive leaves, no face — bending the leaf under its weight, then hops off and flies away, the leaf springing back. Enormous empty green field, impossibly saturated too-blue flat watercolor sky with drifting simplified clouds, warm morning light in peach and gold washes. No photorealism, no 3D render look, no heavy texture. No text.
```

## Beat 04 — INVENTORY: SENSE (0:25–0:40) ⬜ needs footage

```
Vertical 9:16 shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette. Glowing root filaments spread downward and outward through dark soil in an underground cross-section view beneath a tiny mascot-simple sapling — clean bioluminescent teal and green neon lines reaching through a near-black flat wash, lighting up veins of dark water as simple shimmering flat shapes and mineral particles as sparse glittering dots, a living map assembling itself. Slow camera push-in as the root network completes. No photorealism, no 3D render look, no heavy texture. No text.
```

## Beat 05 — INVENTORY: GROW (0:40–0:55) ⬜ needs footage

```
Vertical 9:16 timelapse shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette. The sun arcs overhead three times in accelerating day-night sweeps of peach, gold, indigo washes while, on a tiny mascot-simple banyan sapling, one single new leaf slowly unfurls from a bud — deliberate, proud, bright green against the flat watercolor field. The sapling otherwise holds perfectly still; only light and the one leaf change. No photorealism, no 3D render look, no heavy texture. No text.
```

## Beat 06 — THE WHOLE API (0:55–1:05) ⬜ needs footage

```
Vertical 9:16 wide shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette. Wind sweeps slow waves through simplified grass across an enormous empty field, a tiny fragile mascot-simple sapling — thin curved trunk, oversized expressive leaves, no face — alone at the center, dwarfed by a vast flat watercolor sky. Midday light, mostly empty frame, quiet scale: one small living thing and a world that does not notice it. Slow steady push-in. No photorealism, no 3D render look, no heavy texture. No text.
```

## Beat 07 — THE HOOK (1:05–1:20) ⬜ needs footage

```
Vertical 9:16 shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette. Rhythmic concentric rings of soft light pulse through dark soil like sonar — step, step, step — each pulse rolling in from the far edge of an underground cross-section view and lighting glowing teal root filaments as it passes, brighter and closer each time. Beneath a tiny sapling silhouette above the soil line, the root network flares with each hit. Bioluminescent teal and green on near-black, tension building through rhythm alone. No photorealism, no 3D render look, no heavy texture. No text.
```

---

## Progress

0 of 7 beats exist for the t0-b script — this shot list awaits the regrow
era (Kaggle floor or watering; character/style reference conditioning is
the standing prerequisite — see loop cycle-001 verified backlog).
Provenance for any generated beat goes in a sibling `NN-slug.meta.yaml`
(platform, model, prompt, cost) so `render_t3.py` records per-beat sources
in the T3 leaf.
