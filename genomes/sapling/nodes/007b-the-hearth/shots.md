# Node 007b — shot list (per-beat generation prompts)

The whole episode as a shot list — one generation prompt per script beat, for
end-to-end rendering and assembly by `pipeline/render_t3.py`. Same rules as
node 001's list: base footage only (no burned-in text, no spoken dialogue —
post adds caption overlays, all wireframe label/dialog text, and VO), 9:16
vertical, ~10s per shot, one take.

**Wireframe-window convention:** the sunset-window beats (01, 02, 04, 05)
render the overlay style as base footage — the world reduced to neon-green
vector wireframe on near-black, grass as lattice, objects as low-poly
outlines (`style.md` palette anchors). Every label, tag, and dialog panel in
those shots is generated as a **blank** frame; post types every character of
text into them.

**Character continuity (paste into any beat that shows them — anime model
sheet, `style.md`):** the sapling is a tiny, mascot-simple ~50cm tree — thin
curved trunk, one or two oversized expressive leaves, never a face; its
acting is entirely leaf angle and timing. The scavenger is a small, round
goblin — enormous ears that act like a second face, one broken tusk, huge
expressive eyes, patchwork cloak in faded greens and browns. The farmer is a
broad, squarish silhouette in a straw hat; three lines draw his whole face;
permanently unimpressed posture; clay jug. Standing props: the crooked
lean-to, the three-stone cairn, the clay jug — and, new this episode from
Beat 03 onward, a **tiny stone-ringed fire pit between the sapling's roots**,
its flame always small, careful, and fully inside the ring.

**Naming for assembly:** save each clip as `NN-slug.mp4` in a clips dir, then:
`python3 pipeline/render_t3.py sapling 007b --clips <dir> --out episode.mp4`
Missing beats render as slates; partial lists still assemble.

Status legend: ✅ generated · ⬜ needs footage

---

## Beat 01 — COLD OPEN (0:00–0:10) ⬜ needs footage

Script beat: sunset, the wireframe window. The scavenger takes dictation with
charcoal and a bark slab — the tree tilts leaves, he scribbles — and the
window closes on four written characters.

```
Vertical 9:16 shot, sunset. The shot opens inside the overlay window: the whole clearing reduced to neon-green vector wireframe on near-black — grass as a clean glowing lattice, a crooked lean-to, a three-stone cairn, a small round goblin, and a tiny 50cm sapling all drawn as simple unlabeled low-poly outlines, small blank rectangular tag frames hovering beside them, empty of any text. After roughly three seconds the wireframe dissolves and the world snaps solid into flat cel-shaded dusk, amber into indigo washes, silhouettes reading before faces: the scavenger — a small round goblin with enormous ears that act like a second face, one broken tusk, huge expressive eyes, patchwork cloak in faded greens and browns — sits bolt upright at attention before the sapling, a charcoal stick in hand and a bark slab on his knees. The sapling — a tiny, mascot-simple ~50cm tree with a thin curved trunk and one or two oversized expressive leaves, never a face — tilts a leaf deliberately; the goblin scribbles furiously, tongue out in concentration, then holds the slab up proudly showing four rough unreadable charcoal scratch marks. Static camera, deadpan ritual comedy. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 02 — THE INVESTIGATION (0:10–0:35) ⬜ needs footage

Script beat: a montage across days — each sunset a three-second wireframe
read (farmhouse solid, lean-to uncertain, cairn baffling, farmer counted
while the scavenger is not), findings scrawled onto the bark slab like a case
board.

```
Vertical 9:16 montage-style shot alternating between two looks. Look one, brief sunset flashes in the overlay window — the world as neon-green vector wireframe on near-black, grass as lattice: a squat distant farmhouse rendered as a bright, solid low-poly outline with a steady blank tag frame beside it; then the crooked lean-to as a fainter, incomplete outline with a flickering blank tag; then a three-stone cairn outline whose blank tag wavers as if unsure; then a broad squarish farmer outline in a straw hat standing still, glowing bright with a firm blank tag, while beside him a small round goblin outline stands equally still and barely renders at all, dim and tagless. Look two, between the flashes, warm flat cel-shaded daytime scenes across several days: the scavenger — a small round goblin, enormous ears like a second face, one broken tusk, huge expressive eyes, patchwork cloak in faded greens and browns — adds rough unreadable charcoal scratch marks to a bark slab case board propped against the cairn, while the sapling — a tiny mascot-simple ~50cm tree, thin curved trunk, one or two oversized expressive leaves, never a face — directs him with small precise leaf tilts. Detective-montage energy, warm peach and gold day washes against the neon-on-black window reads. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 03 — THE BUILD (0:35–0:55) ⬜ needs footage

Script beat: the appalled scavenger builds a tiny stone-ringed fire pit
between the roots, placing each stone with terror; the farmer stands fire
brigade with a full jug; the flame catches — and every leaf on the tree pulls
back from it.

```
Vertical 9:16 shot, late afternoon shading toward dusk, warm amber washes and long soft shadows. Between the roots of the sapling — a tiny, mascot-simple ~50cm tree with a thin curved trunk and one or two oversized expressive leaves, never a face — the scavenger, a small round goblin with enormous ears that act like a second face, one broken tusk, huge expressive eyes, and a patchwork cloak in faded greens and browns, builds a very small stone-ringed fire pit: he lowers each stone into place with exaggerated terror, tiptoeing, wincing, ears flat. The farmer — a broad, squarish silhouette in a straw hat, his whole face three unimpressed lines — stands close by gripping a clay jug full of water with both hands, grimly ready. A flame catches in the pit: tiny, careful, comically modest, entirely contained inside its ring of stones — a hearth in miniature beside a wooden resident. Every oversized leaf on the sapling visibly pulls back and away from the little flame at once, the whole tree leaning off-axis from its own hearth. Nervous physical comedy, held wide so the smallness of the fire reads. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 04 — THE WINDOW (0:55–1:15) ⬜ needs footage

Script beat: sunset, full wireframe — the lean-to re-renders, the settlement
label flickers recalculating, a dialog opens over the tree for the first
time; one leaf snaps Y instantly; labels cascade until the settlement line
redraws solid and certain.

```
Vertical 9:16 shot held entirely inside the overlay window: the whole world as hand-drawn neon-green vector wireframe on near-black, low detail, bold clean linework, flat 2D, no gradients — grass as a glowing lattice, the crooked lean-to, three-stone cairn, broad squarish farmer in a straw hat, and small round big-eared goblin with one broken tusk and a patchwork cloak all simple low-poly outlines, and between the root lines of the tiny sapling outline a small stone-ring circle holding a flickering little vector flame. Sequence: first the lean-to outline re-renders from faint to bright and solid, its blank rectangular tag frame refreshing crisply; then a wide blank banner frame hovering over the whole clearing begins to flicker and stutter, recalculating; then, over the sapling outline — a thin curved trunk with one or two oversized leaves, never a face — a clean rectangular dialog panel draws itself in for the first time, completely blank, empty of any text. Instantly, with no hesitation, one wireframe leaf snaps a single decisive tilt; the blank panel pulses once and collapses, and a fast cascade of blank tag frames re-render across the scene, ending on the big settlement banner redrawing itself steady, bright, and certain. Slow drift-in on the little tree outline. Every frame, tag, and panel stays blank. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 05 — THE HOOK (1:15–1:25) ⬜ needs footage

Script beat: the dying window renders one last small corner line; the world
snaps solid — dusk, the tiny hearth-fire, the scavenger cheering at a sky he
cannot read, the farmer pouring a precautionary water arc. Long hold on the
little fire.

```
Vertical 9:16 shot, sunset ending. The shot opens in the dying overlay window: the neon-green vector wireframe world on near-black — grass lattice, low-poly outlines of the lean-to, cairn, farmer, goblin, and tiny sapling with a small ringed vector flame between its root lines — dims and gutters, outlines thinning and going out; in the last half-second a single small blank tag frame renders low in a corner of the frame, faint and system-quiet, empty of any text, then everything cuts out. The world snaps solid into flat cel-shaded dusk, amber into indigo, quiet and still: between the roots of the sapling — a tiny, mascot-simple ~50cm tree, thin curved trunk, one or two oversized expressive leaves, never a face — the tiny stone-ringed hearth-fire crackles, small and careful inside its ring. The scavenger — a small round goblin, enormous ears like a second face, one broken tusk, huge expressive eyes, patchwork cloak in faded greens and browns — cheers with both arms up at a sky he cannot read, while the farmer — broad squarish silhouette, straw hat, three-line unimpressed face — pours a slow precautionary arc of water from his clay jug in a ring around the fire pit. Long held final framing, slow push-in ending on the little flame alone. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

---

## Progress

0 of 5 beats generated. Generating footage is a paid action wherever it runs —
a founder call per the spend rules (STEWARDSHIP.md §4, `pipeline/budget.yaml`).
Platform choice tracks [D8](../../../../DECISIONS.md). Provenance for any
generated beat goes in a sibling `NN-slug.meta.yaml` (platform, model, prompt,
cost) so `render_t3.py` records per-beat sources in the T3 leaf.

With 007a's list also written, both sides of the founder's 006 trunk call
have renderable material one node deep — this list is the 006b line's.
