# Node 002b — shot list (per-beat generation prompts)

The **whole episode** as a shot list — one generation prompt per script beat,
so node 002b (the trunk's second node) can be rendered end-to-end and
assembled by `pipeline/render_t3.py`. Same rules as node 001's list: base
footage only (no burned-in text, no spoken dialogue — post adds caption
overlays and VO), 9:16 vertical, ~10s per shot, one take.

**Character continuity (paste into any beat that shows him):** the scavenger
is a small, round goblin — enormous ears that act like a second face, one
broken tusk, huge expressive eyes, patchwork cloak in faded greens and
browns. The sapling is a tiny mascot-simple tree, ~40cm, thin curved trunk
with a single oversized expressive leaf (plus, this episode only, one small
fig) — never a face; its acting is leaf angle and timing. Keeping these
clauses verbatim across beats and platforms is the cheap half of character
consistency; the taste axes (motion/look) judge the rest.

**Naming for assembly:** save each clip as `NN-slug.mp4` in a clips dir, then:
`python3 pipeline/render_t3.py sapling 002b --clips <dir> --out episode.mp4`
render_t3 fits each clip to its beat's script duration; any missing beat
renders as a slate, so partial shot lists still assemble.

**Voice (optional):** drop `NN-vo.mp3` beside a clip and it's muxed on that
beat; silent stays watchable (captions carry VO and dialogue).

Status legend: ✅ generated · ⬜ needs footage

---

## Beat 01 — COLD OPEN (0:00–0:05) ⬜ needs footage

Script beat: macro on the sapling and its one fig — the premise and the
episode's payoff planted in the first five seconds (R7).

```
Vertical 9:16 macro shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette. A tiny mascot-simple banyan sapling — thin curved trunk, two oversized expressive leaves, no face — sways gently in a green field; on its thinnest branch hangs one small ripe fig, catching warm morning light, slightly heavier than the branch wants to hold. The fig bobs with each sway. Peach and gold washes, vast empty watercolor sky. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 02 — THE FUGITIVE (0:05–0:20) ⬜ needs footage

Script beat: the footsteps from 001 arrive — small, fast, panicked. Something
dives into frame. Footage needs urgency entering a calm frame.

```
Vertical 9:16 shot, enormous empty field as a soft watercolor wash of warm peach and gold morning light with long soft shadows, a tiny mascot-simple sapling — thin curved trunk, one oversized expressive leaf, ~40cm tall — alone at center frame, static camera. Suddenly a small, round goblin — enormous ears, huge expressive eyes, one broken tusk, patchwork cloak in faded greens and browns — sprints into frame from the side at full panicked speed, skids in the grass, and dives behind the tiny sapling. A few simple cartoon dust puffs and grass flecks kicked up. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 03 — THE PATROL (0:20–0:40) ⬜ needs footage

Script beat: the goblin hides behind a trunk that covers one-sixth of him while
two mismatched patrol guards jog past and argue. Comedy of scale; the guards'
dialogue is carried by captions — footage needs the visual gag and the search.

```
Vertical 9:16 shot, morning field in warm peach and gold watercolor washes with long soft shadows. A small, round goblin — enormous ears, huge expressive eyes, one broken tusk, patchwork cloak in faded greens and browns — presses his back against the pencil-thin curved trunk of a tiny 40cm mascot-simple sapling, sucking in his belly, absurdly failing to hide — the tiny tree covers almost none of him. In the background two patrol guards drawn as round, harmless shapes in mismatched, ill-fitting armor jog past, stop, and scan the field; one consults a clipboard made of tree bark. They gesture at each other in disagreement. Deadpan comedic staging, static camera. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 04 — THE LONELY MONOLOGUE (0:40–1:00) ⬜ needs footage

Script beat: danger passed; the scavenger sits in the sapling's tiny shade,
knees up around his ears, and talks to a plant because it's the only thing
that won't file a report. The episode's emotional center — footage needs
smallness, warmth, and practiced loneliness.

```
Vertical 9:16 intimate shot, midday: high flat greens, pale blue-white sky, minimal shadow. A small, round goblin — enormous ears, huge expressive eyes, one broken tusk, patchwork cloak in faded greens and browns — sits curled in the one tiny patch of shade under a 40cm mascot-simple sapling, knees pulled up to his ears to fit into it, with the practiced ease of someone used to small shelters. He talks quietly to the little tree, picking at the dirt, glancing around embarrassed. Vast empty watercolor-wash field behind, the single oversized leaf above him. Gentle, lonely, tender tone, slow imperceptible push-in. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 05 — THE ANSWER (1:00–1:15) ⬜ needs footage

Script beat: the sapling spends everything it owns — one fig, released from
the thinnest branch, bonking off the scavenger's head. Footage needs the
deliberateness of the drop (this is a *decision*, not wind).

```
Vertical 9:16 extreme close-up: high on the thinnest branch of a tiny 40cm mascot-simple sapling hangs one small ripe fig, trembling slightly, rimmed by warm amber afternoon light against a soft watercolor-wash sky. The camera holds on the fig as the stem slowly, deliberately lets go — the fig drops out of frame. Cut within the same take to a low wide angle: the fig bounces softly off the head of a small, round goblin — enormous ears, huge expressive eyes, one broken tusk, patchwork cloak in faded greens and browns — who was walking away, and lands in the grass at his feet. He stops mid-step. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 06 — THE HOOK (1:15–1:30) ⬜ needs footage

Script beat: "…Did you just *answer* me?" — the fig held up like evidence, the
empty field, and one leaf tilting in absolute stillness. The franchise's
signature gesture; the leaf tilt must read as intentional.

```
Vertical 9:16 shot, late afternoon sliding from amber into indigo, silhouettes reading before faces, absolute stillness — no wind, grass frozen. A small, round goblin — enormous ears, huge expressive eyes, one broken tusk, patchwork cloak in faded greens and browns — stands facing a tiny 40cm mascot-simple sapling, holding a small fig up in both hands like evidence, wide-eyed. Slow push-in past him toward the sapling's single oversized leaf. In the dead-still air, the one leaf slowly, deliberately tilts to one side — an unmistakable intentional gesture from a plant; its expression is pure pose, never a face. Hold on the tilted leaf. Quiet awe, warm low amber light. Hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, minimal shading (single shadow tone), simplified shapes, soft watercolor-wash backgrounds with large empty areas, gentle pastel-leaning palette, expressive minimal faces. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

---

## Progress

0 of 6 beats generated for the t0-b molt script (2026-07-25); the published t3 leaves were assembled from t0-a-era clips. Generating footage is a paid action wherever it runs
(platform credits or API) — a founder call per the spend rules
(STEWARDSHIP.md §4, `pipeline/budget.yaml`); this list exists so that call is
one command, not a writing session. Platform choice tracks
[D8](../../../../DECISIONS.md): whatever wins the trials renders these five.

Provenance for any generated beat goes in a sibling `NN-slug.meta.yaml`
(platform, model, prompt, cost) so `render_t3.py` records per-beat sources in
the T3 leaf. A full set here + node 001's remaining beats 03/05 = the trunk's
first two episodes fully filmed.
