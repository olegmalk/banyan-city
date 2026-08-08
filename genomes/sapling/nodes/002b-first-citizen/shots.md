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

The fix spends the cheapest words, never the beat's subject. Beat 02 drops `huge
expressive eyes` (beat 04 is the close-up that carries them) and shortens the cloak
to `faded green patchwork cloak`; beat 03 drops `sucking in his belly` and says `it`
for `the tiny tree`, keeping the size mismatch the beat exists to show. Beat 15 loses
two adjectives. Measured after: 02 = 76 tokens, 03 = 77, 15 = 76, every tail intact.

**The first version of this fix was wrong, and one sample caught it.** It bought the
boosters by giving up `cinematic lighting, detailed, newest` on beats 02 and 03, on
the reasoning that those three words are house boilerplate repeated on all 21 beats
and therefore the cheapest thing in the sentence. They are not boilerplate: they are
the `detailed cinematic anime` look itself, which is the style the founder settled on
after killing v2 low-detail on 2026-07-27. Rendered, beat 02 came back flat and
pale — a small mascot animal on an empty green field under a midday-blue sky, no
lineweight, no lighting — while beat 05, whose prompt was untouched and still carried
those words, came back in full glossy detail on the same model, the same seeds and
the same run. The token arithmetic had agreed with the edit the whole time. A metric
agreeing with me is not a sample, and the picture is what says so.

Two more are continuity with beat 01 — with its **prompt**, which is what survived
2026-08-08's revocation of the plate drawn from it (see Beat 01): beat 12's sky is
its SUBJECT and had no palette at all, so it takes beat 01's
`peach and gold morning sky` rather than letting the model pick; and beat 04's
`dappled morning light` asked for overhead foliage in a location beat 01 establishes
as a vast empty field with one 40cm seedling in it — nothing there can dapple, so it
is `soft morning light`.

Checked and deliberately NOT changed: no beat's NEGATIVE drops a term (measured with
the real CLIP tokenizer against `farm_worker`'s exact house list — worst is beat 12 at
73 of 77), and `mascot-simple` stays in beats 02, 03 and 12, where it modifies the
sapling rather than naming the subject. Beat 01's rounds only proved it must not be
the SUBJECT, and the queue entry says so.

**Twelve prompts edited 2026-08-08 for the r3 redraw wave**
(`ep2-stills-redraw-b02-21` in the farm queue; the eighty 2026-08-07 frames were
"competent frames of twenty different shows" and the founder saw the report).
What changed, and the exact scope of each change:

- **The tall-sapling direction** (his ruling of 2026-08-08, the one b15-r3-s1 of
  node 001 validated) lands as `standing tall` in the SIX beats where the whole
  plant is in shot: 02, 03, 13, 15, 17, 19. It is deliberately NOT added to five
  beats where the sapling appears but its height is not in frame — 12 (tight on
  the two leaves, no trunk base by its own words), 16 (one leaf fills the frame),
  18 (held macro on the fruit), 20 (only a bare branch overhead), 21 (one leaf
  close-up) — because asking a macro to stand tall cancels the macro. Each of
  those five carries the exemption and its reason in its render sidecar. Beats
  04-11 and 14 have no sapling in frame at all and take no direction.
- **HIS CEILING RIDES WITH THE RULE and is recorded here, not baked into twenty
  prompts.** On the same day he asked for a tall sapling he revoked beat 01's
  plate as "tooooo tall" — a 1-3px hairline stem standing 32% of the frame. Read
  together: the tall reading is WIDTH-AND-SUBSTANCE work, not just height — a
  plant that owns the height of its shot on a stem of real thickness, not a
  thread against the sky. Rewriting all twenty prompts on that steward reading
  of one adjective would be "a metric agreeing with me is not a sample", so the
  words above stay minimal (`standing tall`) and this caveat is written down so
  the contact sheet is screened knowing both his sentences. Beat 01's own redraw
  (below) is the one place the ceiling changes a word, because the ceiling was
  ruled ON that beat's plate.
- **The four screening faults, fixed at their likeliest cause and nowhere else:**
  beat 09 drew SPLIT PANELS in all four seeds — `comic timing` (the one panel-
  inviting phrase in the file) became `deadpan timing` and `no split panels` is
  written comma-terminated so `sd_prompt` lifts it into the negative; beat 12
  grew a big ripe orange-pink FRUIT the story has not grown yet — `no fruit`
  joins its negation run; beat 13 read as a GARAGE — `open green grass field`
  anchors it outdoors, and `of someone used to tiny shelters` (the one indoor-
  shelter image in the prompt) is the clause spent to pay for it; beat 14 sat on
  DESERT DIRT — `shallow flat background` became `shallow green grass
  background`; beat 18's fruit was big, ripe and orange-pink — `small ripe fig`
  became `small round green fruit`, dropping `ripe` (the word that coloured beat
  01's fruit peach, that beat's round-2 evidence) and `fig` (which names the
  LEAF in this model's vocabulary, same evidence); beat 20 came back at NIGHT —
  `Amber sliding toward indigo` became `Warm amber afternoon light`. Amber
  afternoon, not the queue entry's "morning of the episode": the closing run
  17-21 is written at afternoon-warming-toward-amber in this file's own words,
  so morning would contradict the four beats around it; the fix goes to the
  palette beats 18 and 19 already hold. Beats 19 and 20 still say `fig`/`ripe
  fig` — not named as faults, so not touched (inventing a fault the founder did
  not name is worse than redrawing) — flagged for the screening pass since beat
  18 beside them now says `green fruit`.
- **Words spent to stay under CLIP's 77 tokens** (same discipline as the
  2026-08-07 edits above, cheapest words and never the subject): beat 02 pays
  `cartoon` and `empty` (the dust reads cartoon in this style anyway, and the
  field's emptiness survives in `wide shot` and in beat 05's own words), beat
  03 pays `absurdly` (redundant beside "covers almost none of him"), beat 15
  pays `loosely`. Beat 02's spend is measured, not guessed: with `standing
  tall` added and nothing paid, `compress()` dropped the beat's entire style
  tail on the estimate counter — the exact 12-of-80 failure the 2026-08-07
  note above records.
- **The negative changes by exactly one term, inherited, not chosen** — `tall
  tree` out of the scale block, the other seven in, the list b15-r3-s1 was drawn
  on. Scoped to the wave script (`render_wave5.py`); `pipeline/sd_prompt.py` is
  untouched.
- **Seeds:** beats whose words or negative changed reuse their own four seeds,
  so a contact-sheet column against the last round is a controlled pair — 02,
  03, 09, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21 (16 and 21 change only by the
  `tall tree` removal, which is load-bearing there). Beats 04, 05, 06, 07, 08,
  10 and 11 changed in neither words nor negative, and no fault was named on
  them — they draw the NEXT four seeds of their own series (k=4..7), because new
  noise is the only honest lever a no-axis redraw leaves (the same reasoning as
  001's beat 6 on 2026-08-08).

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

**PICKED 2026-08-07 (founder, R4): `r3-s3`** — *"r3-s3 and retire"* — and then
**REVOKED BY HIM ON 2026-08-08. THIS BEAT HAS NO CANON FRAME.** His words:

> you used a frame i never approved, and its tooooo tall.

`stills/01-cold-open.png` is renamed in place to
`stills/01-cold-open-REVOKED-too-tall.png`, so every renderer skips it and beat 01
resolves to `None`. The full record — his sentence in context, the provenance of
the revoked file, and the measurements below — is in `stills/README.md`.

**Two things are being revoked at once and only one of them is about pixels.**
*"a frame i never approved"* is about how the pick was taken: the sheet he chose
from carried a steward-hand `<- BEST PLATE` label beside `r3-s3`. A pick sheet
that names a favourite is not a pick sheet (R4), so the 2026-08-07 verdict is
withdrawn rather than defended. And *"tooooo tall"* is about the drawing: the stem
is a 1-3 pixel hairline standing 32% of the frame's height with its apex 25.9%
from the top, where the prompt asks for *a tiny 40cm seedling, whole plant in
frame*. The frame's own shape is not the complaint — 832x1216 is aspect 0.684,
*wider* than the 9:16 the show ships in.

**THE PROMPT BELOW IS NOT REVOKED WITH THE PLATE, and the redraw starts from it.**
Everything rounds 1-4 settled is evidence about words, not about that one
candidate: the mature-tree fix, the dropped `mascot-simple`, the fruit described
without the word `fig`, the 76-token negative. The redraw
(`ep2-b01-cold-open-redraw` in the farm queue — four candidates, one labelled
sheet, **no favourite marked on it**) runs this prompt with the tall-sapling
reconciliation the other twenty beats are getting, and with his ceiling in view:
he has now called one drawing of this plant *too* tall on the same day he asked
for a tall sapling, so "reads tall" means a slender vertical that owns the height
of the shot, not a hairline weed against the sky.

**What the revocation does NOT undo: the dialect, and beats 02-21.** The
2026-08-07 pick had a second job — it settled the native-tag dialect that
`leaves/002b-t0-c.yaml` scoped the script's approval to (*"beats 02-21 await his
verdict on that sample before conversion"*). That stays settled, and the reason is
not this frame: since 2026-08-08 he has ruled on episode 2's twenty redraws by
name and approved its narration voice on the beat-03 take, both of which presume
the episode is being made in this dialect. **That is a reading, and it is written
down as one** — if he means the dialect went back open with the frame, beats 02-21
stop and this paragraph is where the mistake will be found.

**The four-leaf flaw is not what he revoked it for.** The plant carries four
leaves where the character has two; that was argued down through the four wordings
in the table above as a model limitation and the pick was made in view of it. His
sentence says nothing about leaves, and *"dont overthink the leafs on it"*
(2026-08-08) puts the count explicitly out of scope for the redraw. Do not spend a
fifth round on synonyms for *two*.

**Round 5 (2026-08-08, `ep2-b01-cold-open-redraw`) changes ONE clause in the
fence below: `thin curved stem` → `sturdy curved stem`.** That is his ceiling
made into a word — the revoked plate failed as a 1-3px hairline thread, and
"reads tall" has to mean a small plant that owns the height of its shot on a stem
of real substance. Everything else rounds 1-4 settled stands untouched: `40cm`,
`whole plant in frame`, `wide shot`, the fruit described without the word `fig`,
the sunrise palette, the negations. Recipe change rides with the other twenty:
`tall tree` out of the scale negatives in the wave script only. Four candidates,
r5, on this beat's own four seeds; the sheet carries labels only — no favourite,
no ordering, no "closest to" — which is the whole reason this round exists (R4).

**What the pick unblocked on 2026-08-07, and where each of those four stands after
the revocation.** The script's approval was scoped to this sample —
`leaves/002b-t0-c.yaml`: *"beats 02-21 await his verdict on that sample before
conversion"*, and *"No VO, no stills and no footage may be produced until the dialect
is settled"*. Settled, and still settled (see the reading above). Of the four queue
entries that lost their founder gate that day: **beats 02-21 stills** and the
**21-beat re-voice** are unaffected and proceeded; **beat 01's video on both
renderers ran and is now spent** — the two clips exist, they were re-rendered on the
aspect-correct crop of this plate, and on 2026-08-08 he declined to judge Wan
against LTX on them at all (*"neither"*). **No further beat-01 footage is to be
rendered until a new plate is picked.** A model bake-off on a revoked frame is what
he just refused; re-running it on the same frame would ask him the same question
twice.

```
A tiny 40cm banyan seedling, exactly two oversized cotyledon leaves, sturdy curved stem, one small round green fruit hanging from the stem, alone in a vast empty grass field, whole plant in frame, wide shot, sunrise, peach and gold morning sky, no humans, no chibi, no mascot, no creature, no face, no extra leaves, no branches, no night sky, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 02 — THE SPRINT (0:06–0:11) ⬜ needs footage

No dialogue — pure action. Camera wide so the dive reads.

```
A small round goblin — enormous ears, one broken tusk, faded green patchwork cloak — sprints in panicked, skids in the grass kicking up dust, and dives behind a tiny 40cm mascot-simple sapling standing tall. Static camera, morning field, wide shot, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 03 — BAD COVER (0:11–0:16) ⬜ needs footage

Line: "A creature is using me as cover. I am forty centimeters tall." Camera on the size mismatch the line describes.

```
A small round goblin — enormous ears, one broken tusk, patchwork cloak — crouches low behind the pencil-thin trunk of a tiny 40cm mascot-simple sapling standing tall, failing to hide as it covers almost none of him. Deadpan comedic staging, static camera, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
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
A round guard's face works slowly through an idea: eyes drifting, mouth opening slightly, helmet slipping a fraction as he tilts his head. Held close-up, minimal motion, deadpan timing, no split panels, close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
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
Clouds drift and blur behind the two oversized leaves of a tiny mascot-simple sapling that fill the frame and stay utterly still — no trunk base, no ground, no fruit, no other character visible. The stillness of the tree against a moving peach and gold morning sky. Very slow push-in, tight close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 13 — THE SHADE (1:00–1:04) ⬜ needs footage

Line: "…Thanks for the shade." Camera on the goblin folding into the tiny shade.

**Rewritten 2026-08-09 as the ONE SAMPLE for the r4 wave, and the fault it fixes
was measured, not guessed.** All four r3 candidates were rejected on A1 at −2 —
*"the sapling is a giant round creature in every one of them"* — and the
`PROVISIONAL-PICKS-0809.md` wave diagnosis put that down to beat 01's
`no chibi / no mascot / no creature / no face` negatives never having been ported
to beats 02-21. Running the real `sd_prompt` path on this beat says the first
cause is something else and cheaper: **the whole second sentence was being
dropped before the model ever saw it.** `compress()` sheds trailing SENTENCES to
reach CLIP's 77 tokens, and on the old wording the sentence it shed was the only
one carrying the environment, the camera, `cinematic lighting, detailed, newest`
and Animagine's required `masterpiece, best quality, very aesthetic`. What
actually rendered was `1other, a small round goblin slides down the trunk of a
tiny 40cm sapling standing tall … with practised ease` and nothing else — no
style anchor, no boosters, no field. That is the same defect the 2026-08-07 note
above fixed for beats 02, 03 and 15, and it is live on eleven of this node's
twenty-one beats (2, 3, 6, 7, 12, 13, 15, 16, 18, 19, 20). Two of the three
frames the picker kept, 16 and 18, are on that list, and they are exactly the two
he marked down for style — A5 −1 on 16, and 18's *"faint white dashed sketch
marks … a flourish this wave added that nothing else in the show has"* — while
beat 21, which keeps its tail, drew no style complaint at all.

So the subject clause is shortened until the tail survives: **73 positive tokens
with the boosters and the style anchor intact**, measured, against 53 before with
both gone. `sapling standing tall` gives way to `seedling with two oversized
cotyledon leaves`, which is beat 01's proven botanical binding and is what stops
the plant being drawn as a second round creature beside the goblin; `seedling`
also still fires `sd_prompt._SMALL`, so the scale negatives are appended exactly
as before.

**Beat 01's negative block is deliberately NOT ported here, and must not be.**
Lifting `creature`, `face` and `chibi` into the negative is safe on the
plant-only beats (01, 12, 16, 18, 21 — which is why the three the picker kept are
all plant-only, *"the only ones where no character had to be drawn"*). This beat's
subject IS a creature with a face and enormous ears. The human terms are the ones
that belong here, and they are written `no girl, no boy, no child, no person`
rather than as the danbooru tags: `sd_prompt`'s negation regex only lifts a noun
that starts with a letter, so `no 1girl, no 1boy` would be left sitting in the
POSITIVE prompt asking for a girl and a boy — measured, and the reason the wave
script must not take that recommendation literally.

**Round 4 was rendered and REJECTED, and it split the fault cleanly in two.**
Four seeds, ~40 GPU-seconds, 2026-08-09. The style half of the fix WORKED: with
the trailing sentence no longer dropped, all four came back as soft cinematic
anime with real light and a coherent palette instead of the flat cartoon r3
returned, which retires the "twenty different shows" register complaint for this
beat as a *mechanical* problem with a *measured* remedy. **A1 did not move.** Zero
of four contain the sapling as a plant: s0 wears a leaf as a hat above bare human
legs, s1 is an anime child holding a sprout, s2 is an unreadable pale mass, and s3
grows the sprout *out of the figure's head* — beat 19's recorded fault appearing
here. The person negatives were verified lifted into the negative on the real path
and the checkpoint drew people anyway, so on a beat whose subject clause names a
humanoid this is **not** a negative-prompt problem.

Ledger record 26 (`ep2-b13-r4-sample`, `reject_all`, confidence 0.85). The
twenty-beat r4 wave was NOT fired on the strength of it — that is the ONE SAMPLE
rule doing exactly the job it exists for.

**Round 5 changes ONE thing: which noun is the subject.** The diagnosis is that
"A small round goblin" led the sentence, so the goblin was the subject and the
seedling trailed behind it in a prepositional phrase — and this checkpoint
resolves a subordinate plant by fusing it into the character it is attached to.
Beat 01's botanical binding worked there because the plant was the *only* subject.
So r5 inverts the grammar and changes nothing else: the seedling stands as the
subject of the first clause, the goblin follows it as the subordinate one. Same
four seeds, so the pair is controlled on the wording. Measured at **70 positive
tokens with the boosters and style anchor intact**, negatives unchanged and still
lifting `girl, boy, child, person`, and the Danbooru count tag stays `1other`
exactly as in r4 — worth stating, because holding the tag constant is what makes
subject order the only variable.

(Noted for a later round, not acted on here: `1other` asserts one non-human
character while this beat needs a goblin AND a plant in frame. That may be part of
the fusion and it is a *different* experiment; changing the tag and the word order
in the same sample would tell us nothing about either.)

```
A tiny 40cm seedling with two oversized cotyledon leaves stands in open grass; a small round goblin folds into its patch of shade, knees up around his ears, no girl, no boy, no child, no person. Midday light, open green grass field, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 14 — THE DEFENSE (1:04–1:10) ⬜ needs footage

Line: the apple defence. Camera on his hands in the dirt — embarrassment made physical.

```
A small goblin's clawed fingers pick and scratch at loose dirt, flicking pebbles aside, while above them his face glances away, embarrassed, then back down. Intimate low close-up, shallow green grass background, close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 15 — GOOD LISTENER (1:10–1:15) ⬜ needs footage

Line: "You're a good listener." Camera holds BOTH of them — the conversation is the subject.

```
A small goblin tips his head back and looks up at the tiny sapling standing tall beside him, talking, gesturing with one hand; the sapling's two oversized leaves hang above him in frame. Warm midday light, lonely tone, slow push-in, two-shot, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 16 — WHY (1:15–1:22) ⬜ needs footage

Line: the tree's longest thought. Camera ON THE LEAF, goblin blurred behind.

```
One oversized green leaf of a tiny sapling fills the frame and turns very slightly in still air, its edge catching light; far behind it, out of focus and small, a goblin shape sits talking in flat pastel blur. Shallow depth, quiet, held, extreme close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 17 — GOODBYE (1:22–1:27) ⬜ needs footage

Line: "you didn't see me." Camera on him standing to leave.

```
A small round goblin pushes himself up to standing, brushes dust off his patchwork cloak with two quick swipes, and turns away from the tiny sapling standing tall toward the open field. Static camera, afternoon light warming toward amber, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 18 — THE DECISION (1:27–1:34) ⬜ needs footage

Line: the tree deciding to spend everything. Camera on the FIG — the thing being spent.

```
One small round green fruit trembles on the thinnest branch of a tiny sapling, its stem flexing under the weight, rimmed by warm amber afternoon light against a soft wash sky. The trembling grows; the stem bends further. Held macro, no cut, extreme close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 19 — THE DROP (1:34–1:39) ⬜ needs footage

No dialogue — the physical event. Deliberately WIDE (the gate flagged a scale jump from the previous macro): tree and scavenger must share one frame so cause and effect read in a single take.

```
A small ripe fig drops from the branch of a tiny sapling standing tall, bounces softly off the head of a small round goblin walking away below, and lands in the grass at his feet as he stops mid-step. Single continuous take, static camera, amber afternoon, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 20 — EVIDENCE (1:39–1:42) ⬜ needs footage

Line: "…Did you just answer me?" Camera on the goblin holding the fig like evidence.

```
A small round goblin crouches, picks a fig up out of the grass with both hands, straightens, and raises it in front of him like evidence, huge eyes widening as he looks up at a bare branch above. Warm amber afternoon light, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
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
