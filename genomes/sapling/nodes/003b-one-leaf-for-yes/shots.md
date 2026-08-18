# Node 003b — shot list (21 shots, 1:1 with the script's beats)

Rebuilt 2026-07-25 for loop cycle 007 alongside `003b-t0-c`. **One shot
per beat, 4–7s, camera on the referent of that beat's line**
(SCRIPT-SPEC.md "one beat = one shot"). This episode needed it most: a
question, the cost underground, the tilt and the reaction are four
different pictures, not one held wide across a montage.

Base footage only: no burned-in text, no dialogue — post adds captions and
VO. 9:16 vertical. Every prompt's FIRST sentence carries the primary
action (motion grammar, `style.md`).

**Character continuity (anime model sheet, `style.md`):** the scavenger is
a small round goblin — enormous ears that act like a second face, huge expressive eyes, patchwork cloak in faded greens and
browns. The sapling is a tiny mascot-simple tree, ~55cm — thin curved trunk, TWO
oversized expressive leaves, no face, and ONE thin bare side-branch (the
fig grew there and fell in 002b). Every beat must show the same object:
two leaves, one bare branch. All its acting is leaf angle and timing.

**Height is the ladder's, leaf count is the script's — and they disagree.**
`style.md`'s canonical growth ladder gives 003b **~55 cm** (taken here, and the
reason this block no longer says 40 cm) but also says *three* leaves. The script
cannot carry three: the whole protocol is "one leaf for yes", beat 19 is TWO
LEAVES tilting at once, and the cold open names "two oversized leaves". Two it
stays until someone with the authority says otherwise — flagged, not silently
reconciled, because both files are canon and only one of them can be right.

**Assembly:** `python3 pipeline/render_t3.py sapling 003b --clips <dir> --out ep.mp4`
**Free render:** `python3 pipeline/kaggle/run_remote.py push 003b`

Status legend: ✅ generated · ⬜ needs footage

---

## Beat 01 — COLD OPEN (0:00–0:06) ⬜ needs footage

**DIALECT SAMPLE — this is the only converted prompt in this file.** Beats 02-21 are still
in the v2 "low detail" dialect the founder killed on 2026-07-27. This one was rewritten to the
current detailed-cinematic dialect using 002b's converted prompts as the template (action first,
style tail last), the approved goblin identity (green skin, bald, long pointed ears, red eyes,
patchwork cloak — NO tusk, per his 2026-08-12 reference), and 003b's `style.md` ladder row.
Content is unchanged from the v2 prompt: same hands, same fig, same sapling behind. ONE sample
decides the recipe for the other 20; nothing else in this file is converted until it is looked at.
Head clause is r8's species assertion (`A small goblin boy` + definition + `solo`) because the
harness DERIVES its count tag from the first comma-clause and `goblin` alone returns `1other`,
the indeterminate-humanoid tag blamed for three rounds at 0/4. The box copy of this prompt is
`authored_ep3_003b_b01_dialect` in pipeline/wave-drafts.yaml, identical but for a {{GOBLIN}}
placeholder the harness fills from --goblin-def.

Line: premise + fig recap. Camera on the fig in the GOBLIN's hands with the tree's bare branch visible behind — the gate misread the hands as the tree's.

```
A small goblin boy, green skin, bald head, solo, kneels in sunlit grass holding a small round purple fruit, one slender sapling with two big leaves growing from the earth beside him. Wide morning meadow, blue sky. Static camera, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No girl, no child. No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 02 — EVIDENCE RETURNED (0:06–0:11) ⬜ needs footage

Line: "only two possibilities." Camera on the fig being set down at the trunk.

```
Vertical 9:16 shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. A small round goblin — enormous ears, patchwork cloak — crouches and sets a ripe fig down carefully at the base of a tiny sapling's trunk, then adjusts its position twice, like evidence being logged. Dawn field, low warm light. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 03 — TWO POSSIBILITIES (0:11–0:16) ⬜ needs footage

Line: "One: I have lost it. Two: you're in there." Camera eye-to-eye with the tree.

```
Vertical 9:16 close two-shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. A small goblin lowers himself until his huge eyes are level with the two leaves of a tiny sapling and stares straight into it, unblinking, his enormous ears slowly rising. Profile framing, tree and goblin sharing the frame equally. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 04 — THE TEST (0:16–0:21) ⬜ needs footage

Line: "So we test it." Camera BEHIND him over his shoulder (the gate flagged beats 03/04 as the same 'man arranges himself' shot) — we see what he sees.

```
Vertical 9:16 shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. Seen from behind over a small goblin's shoulder and enormous ears: he settles cross-legged on the grass and squares up to a tiny sapling that sits small and centred in his view, the field opening out around it. Dawn light, static camera. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 05 — MOVE ONE LEAF (0:21–0:26) ⬜ needs footage

Line: "move one leaf." Camera close on his waiting face.

```
Vertical 9:16 extreme close-up, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, gentle pastel palette. A small goblin's face fills the frame as he holds very still and waits, huge eyes fixed off-frame, one enormous ear twitching once. Breath held. Shallow blurred field behind, dawn light. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 06 — THE COST (0:26–0:31) ⬜ needs footage

No dialogue — the effort nobody can see. Camera underground.

```
Vertical 9:16 shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, gentle pastel palette. Glowing teal root filaments pull tight and flare brighter and brighter beneath a tiny sapling in an underground cross-section, light gathering then rushing upward through the trunk like effort being spent. Near-black soil, bioluminescent teal, rising intensity. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 07 — THE TILT (0:31–0:36) ⬜ needs footage

No dialogue — the answer. FRAMING 1 of 5 tilts: side-on macro, leaf filling the frame (each tilt gets a distinct scale/angle — the gate found them identical).

```
Vertical 9:16 close-up, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. In dead-still air with every blade of grass frozen, one oversized leaf of a tiny sapling tilts slowly and deliberately to one side, then holds, motionless. Unmistakably a choice, not a breeze. Dawn light, quiet. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 08 — NO WIND (0:36–0:41) ⬜ needs footage

Line/beat: no dialogue — "His ears go flat; he checks the grass — not one blade is moving." Camera on him checking a windless world.

```
Vertical 9:16 shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. A small goblin's enormous ears flatten back against his head as he turns to scan an utterly still field — not one blade of grass moving, no birds — then turns slowly back toward the tiny sapling. Dawn light, uncanny stillness everywhere. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 09 — THE PROTOCOL (0:41–0:46) ⬜ needs footage

Line: "One leaf for yes. Nothing for no. Deal?" Camera on him leaning in to make the treaty — the gate caught the old cut showing him check the grass while this line played.

```
Vertical 9:16 shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. A small goblin leans in slowly until his face is right beside the two oversized leaves of a tiny sapling and speaks low and carefully, one hand raised as if setting terms. Conspiratorial, tender, dawn light. Tight two-shot. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 10 — DEAL (0:46–0:55) ⬜ needs footage

Line: the tree's protocol joke. FRAMING 2 of 5: low angle from the grass line, leaf against open sky.

```
Vertical 9:16 close-up, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. Seen from low in the grass against open sky, one oversized leaf tilts a second time, crisply and without hesitation in completely still air, then settles back level. Confident, almost brisk. Low upward angle. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 11 — THE INTERROGATION (0:55–1:00) ⬜ needs footage

Line: "Are you a spirit? A demon? A god?" Camera on him pacing and tallying.

```
Vertical 9:16 shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. A small goblin paces briskly back and forth in front of a tiny sapling, gesturing with one hand as he fires off questions, stopping on each pass to scratch another tally mark into the dirt with a stick. Comic rhythm, morning field. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 12 — HALF A TILT (1:00–1:05) ⬜ needs footage

Line: "…We'll circle back to that one." FRAMING 3 of 5: extreme macro on the leaf's stem joint, so the hesitation is mechanical.

```
Vertical 9:16 extreme close-up, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, gentle pastel palette. One oversized leaf holds perfectly still for a long moment, then gives the smallest, most reluctant partial tilt — barely committing — and stops halfway. Comic hesitation read entirely through leaf angle. Tight macro, still air. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 13 — THE FIG QUESTION (1:05–1:10) ⬜ needs footage

Line: "Were you the fruit? Did you MEAN to drop it at my feet?" Camera on fig and bare branch together.

**HIS RULING, 2026-08-17 — the line no longer depends on the head-bounce.** The
line read *"Did you MEAN to hit my head?"* until today, which only made sense if
the fig had struck him in 002b beat 19, and he killed that contact on 2026-08-15
(*"ok then just make the fig fall on the ground and the goblin will notice it"*).
Asked about the contradiction he ruled: *"yes, i understand a line on the site is
contradicting it. well.. lets rewrite it, we didn't think when first publishing it
and we dont have viewers for now so its fine to change it."* The accusation is
what the beat is for and it is intact — he is still charging the plant with
**intent**, the next beat's tilt is still a confession, and *"I knew it!"* still
lands. Only the impact is gone. The prompt below is unchanged: it never asked for
the bounce, it asks for the fig held up beside the branch and a look between them,
which is the accusation staged.

**Re-ruled 2026-08-18** — asked again because the line was already published, he
said: *"change the head bounce line even though its published. we discussed this,
its fine."* The correction above is confirmed in his words a second time and the
prompt below still stands unchanged. Superseded line, kept struck through so
nobody restores it by finding it quoted here:
~~"Were you the fruit? Did you MEAN to hit my head?"~~

```
Vertical 9:16 shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. A small goblin raises a ripe fig up beside the bare thin branch it fell from, holding both in the same frame and looking between them accusingly, eyebrows climbing. Morning light, deadpan comic staging. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 14 — GUILTY (1:10–1:15) ⬜ needs footage

Line: "I *knew* it!" FRAMING 4 of 5: two-shot — leaf in foreground, the goblin's waiting face soft behind it.

```
Vertical 9:16 close-up, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. One oversized leaf fills the foreground and holds unnaturally still for a long guilty beat while behind it, soft and out of focus, a small goblin's face waits — then the leaf tilts, slowly, all the way over. Comic timing carried by the pause. Still air. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 15 — THE FILING PROBLEM (1:15–1:20) ⬜ needs footage

Line: "Everywhere else, I'm a filing problem." Camera on him gesturing at himself, deflated.

```
Vertical 9:16 medium shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. A small goblin sits down heavily beside a tiny sapling, all the energy gone out of him, gestures loosely at his own patchwork body with both hands, then lets them drop into his lap. Quiet, tender, flat midday light. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 16 — THE ASK (1:20–1:25) ⬜ needs footage

Line: "Can I stay?" Camera on his hands in the dirt — he won't look up.

```
Vertical 9:16 close-up, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, gentle pastel palette. A small goblin's clawed fingers dig and worry at loose soil, arranging pebbles into a tiny row and knocking them over again, while above them his face stays deliberately turned away and down. Vulnerable, restless hands. Intimate low angle. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 17 — THE BUDGET (1:25–1:30) ⬜ needs footage

Line: the tree on walking away. Camera underground on a nearly spent system.

```
Vertical 9:16 shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, gentle pastel palette. Glowing teal root filaments pulse thin and low through dark soil, dimming and recovering unevenly like a battery near the end of its charge, one faint surge travelling up toward the trunk. Near-black underground cross-section, sparse light. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 18 — TOWARD (1:30–1:37) ⬜ needs footage

Line: "growth includes deciding what to grow toward." Camera on both leaves on the edge of a decision.

```
Vertical 9:16 extreme close-up, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. Both oversized leaves of a tiny sapling quiver and strain at their stems, right on the edge of moving, in air that is completely still — a decision being made, not a wind blowing. Tight macro, warm afternoon light. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 19 — TWO LEAVES (1:37–1:42) ⬜ needs footage

No dialogue — the emphatic yes. FRAMING 5 of 5: wide enough to include the root line, so the COST is visible (the gate: 'I don't see that it cost tomorrow unless you darken the roots on screen').

```
Vertical 9:16 close-up, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. Both oversized leaves tilt at the same moment, together and unmistakably — and at the same time the faint teal glow visible in the soil around the trunk's base dims and goes out. Emphatic and costly. Framed to include leaves and root line together, warm light. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 20 — THE LEAN-TO (1:42–1:48) ⬜ needs footage

Line: "That's not a camp anymore." Camera on the building going up, badly.

```
Vertical 9:16 timelapse, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. A small goblin drags deadfall branches one at a time and leans them against a rock beside a tiny sapling, building a crooked little lean-to that sags and gets propped up again, tongue out in concentration as the afternoon light shifts. Comic, warm, visibly incompetent construction. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

## Beat 21 — THE HOOK (1:48–1:53) ⬜ needs footage

Line: "I hereby name this place—" Camera on the fig raised over the settlement at dusk.

```
Vertical 9:16 shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash background, gentle pastel palette. A small goblin plants his feet, draws himself up to full height and raises a single ripe fig above his head like a founding charter, the crooked lean-to and the tiny sapling silhouetted beside him. Dusk palette sliding amber into indigo, ceremonial and absurd. Slow push-in. No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.
```

---

## Progress

0 of 20 generated for the `003b-t0-c` skeleton. Provenance for each
generated clip goes in a sibling `NN-slug.meta.yaml` (platform, model,
prompt, cost) so `render_t3.py` records per-beat sources in the leaf
(§7.2).

Consistency risk: the goblin appears in 14 of 20 shots and the leaf-tilt
gesture recurs five times — it must read identically every time
(cycle-001 verified defect). Wan 1.3B has no reference-image
conditioning; judge on material.
