# Node 006b — shot list (per-beat generation prompts)

The whole episode as a shot list — one generation prompt per script beat, for
end-to-end rendering and assembly by `pipeline/render_t3.py`. Same rules as
node 001's list: base footage only (no burned-in text, no spoken dialogue —
post adds caption overlays, the sky-label overlays, and VO), 9:16 vertical,
~10s per shot, one take.

**Character continuity (paste into any beat that shows them — anime model
sheet, `../../style.md`):** the magistrate is a sharp angular silhouette in
dark robes of office, a seal on a chain and an open pocket-watch in her hand;
her face is drawn for one raised eyebrow. The scavenger is a small, round
goblin — enormous ears that act like a second face, one broken tusk, huge
expressive eyes, patchwork cloak in faded greens and browns. The farmer is a
broad, squarish silhouette in a straw hat; three lines draw his whole face;
permanently unimpressed posture. The sapling is a tiny, mascot-simple ~50cm
tree — thin curved trunk, one or two oversized expressive leaves, never a
face; beside it a crooked lean-to, a three-stone cairn, and a clay jug.

**Naming for assembly:** save each clip as `NN-slug.mp4` in a clips dir, then:
`python3 pipeline/render_t3.py sapling 006b --clips <dir> --out episode.mp4`
Missing beats render as slates; partial lists still assemble.

Status legend: ✅ generated · ⬜ needs footage

---

## Beat 01 — COLD OPEN (0:00–0:10) ⬜ needs footage

Script beat: dusk; the magistrate is simply *there* at the clearing's edge,
alone — no one saw her come — reading an open pocket-watch; the scavenger,
mid-bite of bread, freezes.

```
Vertical 9:16 shot, dusk. A tiny settlement in an enormous empty field — a mascot-simple 50cm sapling with a thin curved trunk and one or two oversized expressive leaves, a crooked lean-to, a three-stone cairn, a clay jug — under an amber-into-indigo sky where silhouettes read before faces. At the clearing's edge stands the magistrate, a sharp angular silhouette in dark robes of office, a seal on a chain, calmly reading an open pocket-watch in her hand, her face drawn for one raised eyebrow — she was not there a moment ago and no one saw her arrive. In the foreground a small round goblin — enormous ears that act like a second face, one broken tusk, huge expressive eyes, patchwork cloak in faded greens and browns — freezes mid-bite of a piece of bread, eyes going huge. Static camera, quiet authority, comedic dread. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 02 — THE READING (0:10–0:35) ⬜ needs footage

Script beat: she reads the assessor's ledger aloud, flat, as the light goes
long and gold; the humans stand in an anxious row like a headcount; she closes
the ledger, checks the watch, snaps it shut; farmer and scavenger exchange a
look — *the sky?*

```
Vertical 9:16 shot, last golden light of dusk, long shadows stretching across flat grass. The magistrate — a sharp angular silhouette in dark robes of office, a seal on a chain, her face drawn for one raised eyebrow — stands reading flatly from an open ledger, unhurried, official. Facing her in an anxious row like a headcount: a farmer with a broad squarish silhouette, straw hat, and three-line unimpressed face, and a small round goblin with enormous ears, one broken tusk, huge expressive eyes, and a patchwork cloak in faded greens and browns, fidgeting; beside them the tiny mascot-simple 50cm sapling with its oversized expressive leaves held very neatly, on its best behavior. She closes the ledger, lifts an open pocket-watch, and snaps it shut. The farmer and the goblin exchange a sideways baffled glance. Deadpan bureaucratic gravity; warm amber wash deepening toward indigo at the frame edges. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 03 — THE WINDOW (0:35–1:05) ⬜ needs footage

Script beat: sunset — the world flickers to the wireframe overlay; the humans
notice nothing (the scavenger still chattering, offering the jug); the
magistrate turns her back on all of them and reads the sky, holds up her seal
and it renders in wireframe too; she steps close to the trunk and speaks
quietly; the window closes and the world goes solid again. Post adds the
`SHADE · settlement(?) · pop. 2` sky label and the seal tag inside the empty overlay frames.

```
Vertical 9:16 shot, the instant of sunset. Open on warm dusk over a tiny settlement — a mascot-simple 50cm sapling with oversized expressive leaves, a crooked lean-to, a three-stone cairn, a clay jug — then the whole world flickers and reduces to clean glowing neon-green vector wireframe geometry on near-black: the grass becomes a flat green lattice, the cairn a low-poly stack of outlined stones, the jug a labeled glowing cylinder outline with a small empty tag-frame beside it, the lean-to bare glowing edges, and a small empty rectangular frame of green light hangs in the dark sky above the clearing. Inside this wireframe world, the magistrate — a sharp angular silhouette in dark robes of office, her face drawn for one raised eyebrow — has turned her back on everyone and gazes up, reading the sky; she raises her seal on its chain and the seal itself renders as glowing green wireframe with a small empty tag-frame beside it. Behind her, drawn as simple dark outlines, a small round goblin with enormous ears, one broken tusk, and a patchwork cloak in faded greens and browns chatters obliviously and offers up the wireframe jug, while a broad squarish farmer in a straw hat with a three-line face stands unmoved — the humans notice nothing. She steps close to the little tree's trunk, her eyes still on the sky, and speaks quietly to it — her mouth moving as she says something we do not hear. Then the wireframe flickers out and the world snaps back solid: warm amber-into-indigo dusk, quiet. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 04 — THE PRECEDENT (1:05–1:25) ⬜ needs footage

Script beat: all routine again, she takes her leave — then stops at the road,
precisely where the assessor paused, and speaks without turning around; she
walks into the dark; long hold on the tree, leaves very still against the
last light. Smash to black (post).

```
Vertical 9:16 shot, dusk falling into night, amber light collapsing to deep indigo — silhouettes read before faces. The magistrate — a sharp angular silhouette in dark robes of office, a seal on a chain, her face drawn for one raised eyebrow — walks away from the tiny settlement down the dirt road, then stops at the exact edge of the clearing without turning around, a still black cut-out against the last band of amber sky, and says something we do not hear. Behind her, small in frame: a broad squarish farmer in a straw hat with a three-line face and a small round goblin with enormous ears, one broken tusk, and a patchwork cloak stand motionless beside a mascot-simple 50cm sapling with a thin curved trunk and oversized expressive leaves. She walks on into the dark and is gone. The camera holds long on the little tree alone against the dying light, its leaves unnaturally, perfectly still, slow push-in as indigo swallows the amber. Heavy quiet. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

---

## Progress

0 of 4 beats generated. Generating footage is a paid action wherever it runs —
a founder call per the spend rules (STEWARDSHIP.md §4, `pipeline/budget.yaml`).
Platform choice tracks [D8](../../../../DECISIONS.md). Provenance for any
generated beat goes in a sibling `NN-slug.meta.yaml` (platform, model, prompt,
cost) so `render_t3.py` records per-beat sources in the T3 leaf.

006b is one of the R4 sibling pair (006a/006b); the trunk call between them is
the founder's. Both siblings' shot lists sit ready so the choice can be felt
on rendered material, not argued on paper.
