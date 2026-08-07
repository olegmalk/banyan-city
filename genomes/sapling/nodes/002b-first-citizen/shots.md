# Node 002b — shot list (21 shots, 1:1 with the script's beats)

Rebuilt 2026-07-25 for loop cycle 007. The previous list was 6 shots for
102 seconds — one image per scene, which is why the picture did not follow
the script. This list is **one shot per beat, 3–6s, camera on the
referent of that beat's line** (SCRIPT-SPEC.md "one beat = one shot").

Base footage only: no burned-in text, no dialogue — post adds captions and
VO. 9:16 vertical. Each prompt's FIRST sentence states the primary action
(motion grammar, `style.md`), so the model does not render a still.

**Assembly:** save each clip as `NN-slug.mp4` in a clips dir, then
`python3 pipeline/render_t3.py sapling 002b --clips <dir> --out ep.mp4`

**Free render path:** `pipeline/kaggle/animatediff-kaggle.ipynb` with
`NODE = "002b"` — 21 shots ≈ 8–15 h of Kaggle's free weekly GPU.

Status legend: ✅ generated · ⬜ needs footage

**Five prompts edited 2026-08-07, measured on the real `sd_prompt` path before the
beats 02-21 batch, not guessed.** Three of them were losing their whole style tail
in silence. `compress()` drops trailing SENTENCES to reach CLIP's 77 tokens, and on
beats 02, 03 and 15 the sentence it dropped was the one carrying `masterpiece, best
quality, very aesthetic` — the booster tags Animagine XL 3.1's card requires, whose
omission this repo has already paid for once: "flat abstract shapes in a garish
palette", 2026-07-26, recorded in `sd_prompt.py`'s own header. Beat 02 also lost
`empty morning field` and `wide shot` with it. So 12 of the 80 images in the batch
would have come back in a different, knowably worse look than the other 68.

The fix spends the cheapest words, never the beat's subject. Beats 02 and 03 give up
`cinematic lighting, detailed, newest` — house boilerplate repeated identically on all
21 beats — to keep the boosters and the environment; beat 02 also drops `huge
expressive eyes` (beat 04 is the close-up that carries them) and beat 03 drops
`sucking in his belly`, keeping the size mismatch the beat exists to show. Beat 15
loses only two adjectives. Measured after: 02 = 72 tokens, 03 = 72, 15 = 76, all
tails intact.

Two more are continuity with the canon frame, which is what `stills/01-cold-open.png`
now is: beat 12's sky is its SUBJECT and had no palette at all, so it takes beat 01's
`peach and gold morning sky` rather than letting the model pick; and beat 04's
`dappled morning light` asked for overhead foliage in a location beat 01 establishes
as a vast empty field with one 40cm seedling in it — nothing there can dapple, so it
is `soft morning light`.

Checked and deliberately NOT changed: no beat's NEGATIVE drops a term (measured with
the real CLIP tokenizer against `farm_worker`'s exact house list — worst is beat 12 at
73 of 77), and `mascot-simple` stays in beats 02, 03 and 12, where it modifies the
sapling rather than naming the subject. Beat 01's rounds only proved it must not be
the SUBJECT, and the queue entry says so.

---

## Beat 01 — COLD OPEN (0:00–0:06) ⬜ needs footage

Line: the tree's first VO. Camera on the TREE and the fig — premise and the
ending's payoff in one frame. The fig must GROW here, not already be hanging
(founder, 2026-08-03: "we need to make SURE the fig growing on the sapling is
mentioned, last time we generated 002b it just.. appeared"). It is also the only
thing episode 1 said he can do — `GROW ✓ slow. directional.` — so the growth is
continuity, not decoration.

Prompt rewritten 2026-08-06, twice, against drawn evidence. The first still came
back as a thick woody MATURE branch carrying ~8 leaves and a ripe pink peach; the
scale negatives were already firing and lost anyway, so the fix went into the
positive prompt — the sapling leads instead of the scene, "40cm" and "whole plant
in frame" state the scale the episode's joke depends on, the fig is small, green
and unripe (it still swells, which is the founder's condition, but "ripening" is
what coloured it peach), and `macro shot` is gone because it invited the
branch-scale crop. That killed the mature tree in all four candidates. Two things
it got wrong, and both were words I had added: `mascot-simple`, borrowed from
beats 02-03 where it modifies the sapling a goblin hides behind, became the
SUBJECT here and three of four candidates drew a chibi mascot CREATURE with
leaves on its head; and the fig appeared in none of the four, with `no ripe
fruit` / `no large fruit` sitting in the negative prompt where they suppress the
one piece of fruit the beat exists to show. So: no `mascot-simple`, no fruit
negatives, and `no chibi` / `no mascot` / `no creature` / `no face` written
comma-terminated so `sd_prompt` lifts them into the negative instead.

Rewritten a third time 2026-08-06, against the eight candidates those two rewrites
drew. Two failures survived both and neither is seed luck: the fig is in 0 of 8, and
all 8 carry four to six leaves. The likeliest reason for the missing fruit is that
`fig` in this model's caption vocabulary names the *leaf*, not the fruit — so the
fruit is now described without the word, `one small round green fruit hanging from
the stem`. And `a single pair of oversized leaves` is prose the model ignored eight
times; `seedling` plus `exactly two oversized cotyledon leaves` is the botanical
vocabulary for a plant that has only two. `sapling` gives way to `seedling` because
keeping both words costs four tokens and puts the compressed prompt exactly on CLIP's
77-token ceiling (measured with the real tokenizer, this way it is 73); `seedling` is
in `sd_prompt._SMALL` too, so the scale negatives still fire. Everything rounds 1-2
proved is untouched — `40cm`, `whole plant in frame`, `wide shot`, the sunrise
palette, the booster tail, and the entire negative list — so the subject description
is the only thing that changed.

A fourth attempt, later on 2026-08-06, changed only the leaf clause and is **not** in
the prompt below, because it lost more than it won. `exactly two oversized cotyledon
leaves` became `sprout with only two oversized leaves` — the bet was on `sprout`,
since the two-leaf sprout is a motif this model has actually seen drawn thousands of
times, whereas counting words are something it has only ever read. It got closer than
anything before: seed 20260720 came back with **three** leaves where every earlier
attempt gave four to six. But three is not two, and the other three seeds paid for it
by losing the composition round 3 had already won — 20261720 and 20263720 both hung
the plant off the top edge of the frame, and 20262720 cropped in to a single leaf. So
the wording stays at round 3's and the leaf count is now four wordings deep:

| wording | rounds | leaf count it drew |
|---|---|---|
| `a single pair of oversized leaves` | 1–2 | 4–6, in 8 of 8 |
| `exactly two oversized cotyledon leaves` | 3 | 4–6, in 4 of 4 |
| `sprout with only two oversized leaves` | 4 | 3 at best, in 1 of 4 — and 3 of 4 lost the composition |

Do not spend a fifth round on synonyms for "two": treat the two-leaf character as
something this model will not draw on request, and a thing the founder accepts or
rejects (R4). The levers that are left are all outside the prompt — img2img over a
chosen plate, a pose controlnet, or a different checkpoint.

Also settled on 2026-08-06, and also not worth re-trying: **size adjectives do not
shrink the fruit.** Two img2img repaints over `01-cold-open-r3-s3.png` at strength
0.35, changing only the fruit clause — `one tiny unripe green fruit nub on the stem`
and `one pea-sized unripe green fruit on the stem` — both came back with a fruit
*larger* and rounder than the plate they started from, the first of them lime-yellow
rather than green. The model hears `fruit` and draws a finished one; `tiny`, `nub`,
`unripe` and `pea-sized` do not move it, and `pea-sized` moved only the colour. The
practical consequence for this beat is the opposite of a defeat: the script wants the
fig to *swell* across the six seconds, so the un-repainted plate is the start frame and
a 0.35 repaint of it is a ready-made end frame. Do not spend more rounds asking for a
smaller fruit in words; choose the frame instead.

Fixed 2026-08-07, having been known and left alone through rounds 1-4: the negative
prompt was 82 tokens against CLIP's 77-token ceiling, so its tail was silently
dropped — diffusers warns when the *positive* prompt truncates but not when the
negative does. For this beat the lost words were duplicates (`photorealism`, `text`),
which is the only reason it cost nothing here; on 001 beat 7 the same defect was
throwing away 16 of the author's terms. `sd_prompt.fit_negative` now deduplicates and
then drops from the least important end, saying out loud what it dropped. This beat's
negative comes to 76 tokens: the duplicate `text` goes, and `realistic skin texture`
is spent — house boilerplate, in a shot whose own negative already says `no humans`.
Everything the beat asks for survives, including `night sky` and the scale negatives.

**The eight candidates in `takes/stills/` predate that fix** and were drawn with
`realistic skin texture` in force and `photorealism` silently absent. They are still
valid plates to choose from — but a re-render at the same seed will no longer match
them exactly, so pick from the files, do not expect to reproduce them.

**PICKED 2026-08-07 (founder, R4): `r3-s3`.** His words were *"r3-s3 and retire"* —
the frame, and the retirement of a stale question in his inbox, in one line.
`takes/stills/01-cold-open-r3-s3.png` is promoted byte-for-byte to
`stills/01-cold-open.png`, which is founder-approved canon and the file every
renderer actually reads (`video_task` globs `stills/NN-*.png` for its conditioning
frame). Provenance, checksum and the derived seed are in `stills/README.md`.

**The flaw he accepted with it: four leaves, where the character has two.** That is
not an unfinished prompt — it is the model, argued down through the four wordings in
the table above and refused by all of them. The pick is a verdict on a known
limitation, so do not "fix" it with a fifth synonym for *two*: the levers left are
img2img over this plate, a pose controlnet, or another checkpoint.

**What the pick unblocks.** The script's approval was scoped to this sample —
`leaves/002b-t0-c.yaml`: *"beats 02-21 await his verdict on that sample before
conversion"*, and *"No VO, no stills and no footage may be produced until the dialect
is settled"*. Settled. Beats 02-21 stills, the 21-beat re-voice, and beat 01's video
on both renderers are sanctioned from this date, and their four queue entries lost
their founder gate the same day.

```
A tiny 40cm banyan seedling, exactly two oversized cotyledon leaves, thin curved stem, one small round green fruit hanging from the stem, alone in a vast empty grass field, whole plant in frame, wide shot, sunrise, peach and gold morning sky, no humans, no chibi, no mascot, no creature, no face, no extra leaves, no branches, no night sky, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 02 — THE SPRINT (0:06–0:11) ⬜ needs footage

No dialogue — pure action. Camera wide so the dive reads.

```
A small round goblin — enormous ears, one broken tusk, patchwork cloak in faded greens and browns — sprints in panicked, skids in the grass kicking up cartoon dust, and dives behind a tiny 40cm mascot-simple sapling. Static camera, empty morning field, wide shot, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 03 — BAD COVER (0:11–0:16) ⬜ needs footage

Line: "A creature is using me as cover. I am forty centimeters tall." Camera on the size mismatch the line describes.

```
A small round goblin — enormous ears, one broken tusk, patchwork cloak — crouches low behind the pencil-thin trunk of a tiny 40cm mascot-simple sapling, absurdly failing to hide as the tiny tree covers almost none of him. Deadpan comedic staging, static camera, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 04 — THE FOOTNOTE (0:16–0:22) ⬜ needs footage

Line: the architect/footnote joke. Camera close on the held breath.

```
A small round goblin's face fills the frame as he holds his breath, cheeks puffed, huge expressive eyes darting left and right, enormous ears twitching at every sound. Slow push-in, soft morning light, close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 05 — THE PATROL (0:22–0:27) ⬜ needs footage

Line: GUARD 1, "Apple thief." Camera on the guards arriving.

```
Two patrol guards drawn as round harmless shapes in mismatched ill-fitting armor jog into frame and halt, heads turning as they scan an empty morning field; one carries a clipboard made of tree bark. Wide static camera, long soft shadows, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 06 — THE CLIPBOARD (0:27–0:34) ⬜ needs footage

Line: GUARD 2 reclassifying the crime. Camera on the clipboard — the thing the line is about.

```
A round guard in mismatched armor turns over a clipboard made of tree bark and traces a line on it with one finger as he reads, brow furrowed with bureaucratic seriousness. The clipboard fills the lower third of the frame. Slow drift in, medium close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 07 — CONFISCATE (0:34–0:37) ⬜ needs footage

Line: "So we confiscate the apple." Camera on the pointing guard.

```
A round guard in mismatched armor thrusts one arm out decisively, pointing off-frame, chin raised with the confidence of a man who believes he has solved the problem. His partner's shoulder is just visible at frame edge. Static camera, morning field, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 08 — INSIDE HIM (0:37–0:42) ⬜ needs footage

Line: "The apple is inside him, Dren." Camera follows the pointing finger to the goblin's belly.

```
A round guard lowers his bark clipboard and points flatly at the round belly of a small goblin in a patchwork cloak, who looks down at himself. Deadpan two-shot, no movement but the pointing arm, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 09 — THE PAUSE (0:42–0:45) ⬜ needs footage

Line: "…We confiscate the goblin?" Camera close on the guard's slow realisation.

```
A round guard's face works slowly through an idea: eyes drifting, mouth opening slightly, helmet slipping a fraction as he tilts his head. Held close-up, minimal motion, comic timing, close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 10 — NO FORM (0:45–0:50) ⬜ needs footage

Line: "There's no form for that." Camera on the blank back of the clipboard.

```
A round guard flips his bark clipboard around and holds up its completely blank back toward his partner, shaking it once for emphasis. The blank board dominates the frame. Static camera, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 11 — THEY LEAVE (0:50–0:55) ⬜ needs footage

Line: the tree's "trapped in a workflow." Camera on the departing guards.

```
Two round guards in mismatched armor walk away from camera across an empty field, gesturing at each other in continuing disagreement, growing smaller as they go. Static wide camera, long morning shadows stretching behind them, wide shot, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 12 — RELATED (0:55–1:00) ⬜ needs footage

Line: the tree's. Camera ON THE TREE for the tree's own line — framed TIGHT on the leaves, because the scavenger is still hidden behind the trunk and a wide shot would read as him having left (caught by the comprehension gate).

```
Clouds drift and blur behind the two oversized leaves of a tiny mascot-simple sapling that fill the frame and stay utterly still — no trunk base, no ground, no other character visible. The stillness of the tree against a moving peach and gold morning sky. Very slow push-in, tight close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 13 — THE SHADE (1:00–1:04) ⬜ needs footage

Line: "…Thanks for the shade." Camera on the goblin folding into the tiny shade.

```
A small round goblin slides down the trunk of a tiny 40cm sapling and folds himself into its single small patch of shade, pulling his knees up around his enormous ears with the practised ease of someone used to tiny shelters. Midday light, high flat greens, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 14 — THE DEFENSE (1:04–1:10) ⬜ needs footage

Line: the apple defence. Camera on his hands in the dirt — embarrassment made physical.

```
A small goblin's clawed fingers pick and scratch at loose dirt, flicking pebbles aside, while above them his face glances away, embarrassed, then back down. Intimate low close-up, shallow flat background, close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 15 — GOOD LISTENER (1:10–1:15) ⬜ needs footage

Line: "You're a good listener." Camera holds BOTH of them — the conversation is the subject.

```
A small goblin tips his head back and looks up at the tiny sapling beside him, talking, gesturing loosely with one hand; the sapling's two oversized leaves hang above him in frame. Warm midday light, lonely tone, slow push-in, two-shot, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 16 — WHY (1:15–1:22) ⬜ needs footage

Line: the tree's longest thought. Camera ON THE LEAF, goblin blurred behind.

```
One oversized green leaf of a tiny sapling fills the frame and turns very slightly in still air, its edge catching light; far behind it, out of focus and small, a goblin shape sits talking in flat pastel blur. Shallow depth, quiet, held, extreme close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 17 — GOODBYE (1:22–1:27) ⬜ needs footage

Line: "you didn't see me." Camera on him standing to leave.

```
A small round goblin pushes himself up to standing, brushes dust off his patchwork cloak with two quick swipes, and turns away from the tiny sapling toward the open field. Static camera, afternoon light warming toward amber, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 18 — THE DECISION (1:27–1:34) ⬜ needs footage

Line: the tree deciding to spend everything. Camera on the FIG — the thing being spent.

```
One small ripe fig trembles on the thinnest branch of a tiny sapling, its stem flexing under the weight, rimmed by warm amber afternoon light against a soft wash sky. The trembling grows; the stem bends further. Held macro, no cut, extreme close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 19 — THE DROP (1:34–1:39) ⬜ needs footage

No dialogue — the physical event. Deliberately WIDE (the gate flagged a scale jump from the previous macro): tree and scavenger must share one frame so cause and effect read in a single take.

```
A small ripe fig drops from a tiny sapling's branch, bounces softly off the head of a small round goblin walking away below, and lands in the grass at his feet as he stops mid-step. Single continuous take, static camera, amber afternoon, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 20 — EVIDENCE (1:39–1:42) ⬜ needs footage

Line: "…Did you just answer me?" Camera on the goblin holding the fig like evidence.

```
A small round goblin crouches, picks a fig up out of the grass with both hands, straightens, and raises it in front of him like evidence, huge eyes widening as he looks up at a bare branch above. Amber sliding toward indigo, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 21 — THE ANSWER (1:42–1:47) ⬜ needs footage

The tree's reply, and the show's signature gesture. Camera ON THE LEAF; the tilt must read as intentional.

```
In dead-still air with the grass frozen, one oversized leaf of a tiny sapling tilts slowly and deliberately to one side — an unmistakably intentional gesture from a plant — then holds, motionless. Low amber light, quiet awe, no wind anywhere in frame, close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

---

## Progress

0 of 21 generated. This is the first shot list built to the cycle-007
density rule and it is the intended first job for the free Kaggle path
(`NODE = "002b"`). Provenance for each generated clip goes in a sibling
`NN-slug.meta.yaml` (platform, model, prompt, cost) so `render_t3.py`
records per-beat sources in the leaf (§7.2).

Character consistency across 21 shots is the known risk (cycle-001
verified defect): the same goblin must survive twenty generations. Wan
1.3B on Kaggle has no reference-image conditioning, so expect drift and
judge on material — if it breaks the episode, reference conditioning
becomes the next blocking task rather than a backlog item.
