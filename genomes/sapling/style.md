# Sapling — visual style bible (v2: low-detail anime)

> **⚠ STALE (2026-07-27):** the founder killed this flat/low-detail look after live screening — see `STATE.md` (2026-07-27 evening) and the live shot boards for the current detailed cinematic look. The v3 rewrite of this document awaits the founder (taste, R4). Do not render from this.


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

## A shot is a subject OR a vista — never a small subject inside one

Discovered 2026-07-26/27 across five renders of the same beat. SD1.5 will draw a
subject close, and it will draw an empty landscape, and asked for "one tiny sapling
alone in a vast field" it draws the **field** and omits the sapling entirely. At
512x768 a genuinely tiny thing is a few pixels; the model resolves the composition
it can see. Rewording does not fix it — subject-first, environment-first, scale
negatives and four phrasings all produced either a landscape with no tree or a
specimen on a void.

So the smallness is carried by the **cut**, not by one frame:

- a beat whose line is about the tree -> **close on the tree**, with grass, sky or
  soil moving behind it (which is also what gives SVD something to animate)
- a beat whose line is about the emptiness -> **wide of the empty field, no tree in
  it at all**
- where the contrast is the point -> both, as consecutive beats

This is why cycle-007's density rule pays for itself twice: with 20 beats instead of
5, an idea can afford two shots, and "a tiny thing in an enormous world" is a cut
rather than a compromise.

Prompt structure that follows from it, in order: **subject, then setting as trailing
tags, then style.** Whatever leads the prompt becomes the composition — leading with
the style tag produced abstract lineart, leading with the shot type produced a macro
of leaves, and leading with the meadow produced a meadow with no sapling.

## Canonical growth ladder (per node) — steward, 2026-07-25

Growth is the protagonist's only verb, so his **size is continuity**, and it
was never written down. The result was a contradiction a cold reader caught
in 004: the same tree described as a two-leaf sprout *and* as something with
a trunk to lean on, leaves overhead, and enough shade to sit in — in a town
named Shade. No animator can draw that. This ladder is the fix; every shot
prompt states the node's row verbatim.

| Node | Height | Canopy | Notes |
|---|---|---|---|
| 001 | ~15 cm | two oversized cotyledon leaves | a sprout; no trunk, no branch |
| 002a/b/c | ~40 cm | two leaves + one thin side-branch | the branch is where the fig grew and fell |
| 003b | ~55 cm | three leaves, bare fig branch | tall enough to cast a hand-sized shadow |
| 004 | **~90 cm (knee-high)** | five or six leaves in a small crown | casts one real shade patch, big enough for a sitting goblin — this is why the town is called Shade |
| 005 | ~1.2 m | small crown, first woody bark | the assessor can call it "one specimen" without irony |
| 006a/007a | ~1.6 m | full small crown, side branches | a shrine you can stand under; fig-bearing |

Two rules follow:

1. **Never write "tiny sapling" past 003b.** From 004 he is a young tree.
   The comedy of smallness lives in 001–003; from 004 the comedy is
   bureaucratic, not physical.
2. **The shade patch is a prop.** From 004 onward it exists on the ground,
   it is small, and characters use it. It is the town's namesake and the
   first thing he ever gave anyone.
