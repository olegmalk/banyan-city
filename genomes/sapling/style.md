# Sapling — visual style bible (v2: low-detail anime)

**Decided by the founder, 2026-07-19** (direct instruction to the steward:
"not a realistic theme — a low detail anime theme"). This supersedes the v1
photoreal-fantasy look used in the first trial clips and shot lists. Style is
a taste axis (R4): this file is the founder's call, executed by the steward;
amending it is a founder edit like any taste change.

## The look, in one block

Every generation prompt carries this style block verbatim (then scene
specifics on top):

```
Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean
linework, minimal shading (single shadow tone), simplified shapes, soft
watercolor-wash backgrounds with large empty areas, gentle pastel-leaning
palette, expressive minimal faces. No photorealism, no 3D render look, no
heavy texture. 9:16 vertical, no text.
```

## Why low detail (beyond taste)

- **Consistency is cheaper.** Simple character shapes survive across shots
  and across model providers far better than photoreal faces do — the
  continuity clauses actually hold.
- **Budget models close the gap.** Flat-color anime is where Wan/Hailuo-class
  pricing competes with Veo-class output; the D8 bake-off should be re-judged
  in this style (noted in DECISIONS.md).
- **The overlay belongs.** The system's wireframe/debug layer reads as
  *native* against flat cel shading — UI lines over UI-adjacent art — instead
  of clashing with photographic footage.

## Character model sheet (anime terms — paste what a shot needs)

- **The sapling:** a tiny, almost mascot-simple tree — thin curved trunk, one
  or two oversized expressive leaves; its acting is entirely leaf angle and
  timing. Never a face, never eyes; expression is *pose*.
- **The scavenger (goblin):** small and round, enormous ears that act like a
  second face, one broken tusk, huge expressive eyes, patchwork cloak in
  faded greens and browns. Cartoonishly bad at hiding.
- **The farmer:** broad, squarish silhouette; straw hat; three lines can draw
  his whole face; permanently unimpressed posture; clay jug.
- **The assessor:** a thin vertical line of a man; dust-grey robes, chained
  ledger, quill stub; moves like a metronome, drawn with ruler-straight edges.
- **The magistrate:** sharp angular silhouette in dark robes of office; a
  seal on a chain; a face drawn for one raised eyebrow.
- **Patrol guards:** mismatched armor, one bark clipboard; round, harmless
  shapes.

## Palette anchors (per time of day)

- **Dawn/morning:** warm peach and gold washes, long soft shadows.
- **Midday:** high flat greens, pale blue-white sky, minimal shadow.
- **Dusk/hook scenes:** amber into indigo; silhouettes read before faces.
- **Night/full moon:** deep indigo with silver rim light, flat and quiet.
- **Underground/sensing:** near-black with bioluminescent teal and green —
  glowing root filaments as clean neon lines.
- **The overlay window:** the world reduces to neon-green vector wireframe on
  near-black — grass as lattice, objects as labeled low-poly outlines. (This
  is the one place "low detail" becomes literal geometry.)

## What stays true from v1

Shot content, camera direction, beat timing, the no-burned-in-text rule, and
all continuity facts (props, staging, arrival choreography) are unchanged —
only the rendering style moved. Post still adds captions, overlays, and VO.

## Status of v1 footage

The node-001 trial clips (Veo/Flow, photoreal, beats 1/2/4) remain archived
with full provenance at `/trials/` and in the 001 T3 leaf — they are v1
evidence, not canon style. Remaking them in v2 anime is a founder render
session (free tier) or a D8-funded run; the rewritten prompts sit ready in
`nodes/001-capability-inventory/shots.md`.

## Shot-prompt motion grammar (production convention, steward-drafted 2026-07-24)

Adopted from loop cycles 001/005 (verified on frames: near-still hook
shots, 10-second freeze-frames). These are PRODUCTION rules, not taste —
the founder's visual bible above always wins on look.

1. **The first sentence carries the primary action.** Generation models
   front-load whatever the opening describes: "A tired engineer sits at a
   desk… then collapses" renders 6 seconds of sitting. Write "An engineer
   collapses out of frame mid-keystroke; the mug tips…" — the shot is
   already mid-action at frame 1.
2. **Stillness is expressed through secondary motion.** Never "completely
   still / motionless" alone — pair with drifting clouds, grass ripple,
   shifting light, one leaf breathing, plus a perceptible camera move.
   A held breath must still be alive on a phone screen.
3. `pipeline/lint_genome.py` warns (advisory, never failing) on both.

## Why the tree grows (added 2026-07-26, founder decision)

Growth had a ladder but no **cause**, so the jump from waist-high at 005 to a
man's height at 006a read as an error rather than an event. The cause is now
canon and stated on screen once, in 005: the tree redirected groundwater toward
the farmer's field in 004 by growing roots west, and that water feeds it too —
*"His field drinks. So do I. That is why I am taller this week than I have any
right to be."*

Two things follow, and both are drawable:

- Growth is **not** uniform over time. It tracks input. A well-watered stretch
  shows a real jump; a spent or hoarding stretch shows none.
- Growth can be **withheld**. In 007a the tree banks two weeks of it for the
  demo, and branch three is visibly starved *because* of it — thin and half-bare
  where the others are full. That is the same currency 003b established, where
  one leaf-tilt spent the whole day's reserve, and it is why the finale's bloom
  costs something.

## Canonical growth ladder (per node) — steward, 2026-07-25

Growth is the protagonist's only verb, so his **size is continuity**, and it
was never written down. The result was a contradiction a cold reader caught
in 004: the same tree described as a two-leaf sprout *and* as something with
a trunk to lean on, leaves overhead, and enough shade to sit in — in a town
named Shade. No animator can draw that. This ladder is the fix; every shot
prompt states the node's row verbatim.

| Node | Height | Canopy | Notes |
|---|---|---|---|
| 001 | ~60 cm (shin-high) | a small round crown on a thin bending stem | a young tree, not a seedling — see the renderer note below |
| 002a/b/c | ~75 cm | small crown + one thin side-branch | the branch is where the fig grew and fell |
| 003b | ~90 cm | fuller crown, bare fig branch | casts a real hand-sized shadow |
| 004 | **~1.1 m (knee-high)** | five or six leaves in a small crown | casts one real shade patch, big enough for a sitting goblin — this is why the town is called Shade |
| 005 | ~1.3 m | small crown, first woody bark | the assessor can call it "one specimen" without irony |
| 006a/007a | ~1.6 m | full small crown, side branches | a shrine you can stand under; fig-bearing |

Two rules follow:

1. **Never write "tiny sapling", "seedling" or "sprout" anywhere.** Not even in
   001. This is a renderer constraint discovered the hard way on 2026-07-26:
   SD1.5 will not draw a 15 cm two-leaf sprout as a character. Five attempts
   produced a leaf on a lilypad, a botanical specimen, or abstract lineart, and
   negative-prompting "mature tree" made the tree *larger*. Ask it for a small
   young TREE — stem, small round crown, sky, ground — and it renders that
   reliably and on-style in about 80 seconds.

   The ladder above was rewritten to start where the tool is strong rather than
   where a spec sheet wished it would be. The comedy of smallness survives: the
   tree is still dwarfed by an empty field, still grows one leaf in three days,
   still gets called "one specimen" by a man with a ledger. What is lost is the
   *pathetic* miniature scale, which was a steward invention of 2026-07-25 and
   never something the scripts required.
2. **The shade patch is a prop.** From 004 onward it exists on the ground,
   it is small, and characters use it. It is the town's namesake and the
   first thing he ever gave anyone.
