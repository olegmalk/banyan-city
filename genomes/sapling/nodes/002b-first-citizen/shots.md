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

**Round 5 rendered and was rejected (ledger record 1, `ep2-b01-r5-provisional`,
`reject_all`, 0.80). The word `sturdy` did not move the drawing.** Three of the
four did not put the plant on the ground at all — s0 and s2 hang it DOWN from the
top edge like a vine, s1 floats a detached sprout above the horizon — and those
same three stand a human child in a field the script calls empty. s3 is clean of
both and then reproduces the revoked plate's own measurements: hairline stem, apex
25% from the top, ~36% of frame height, *taller in frame than the 32% he threw
out*.

**Round 6 changes three things, and each one is a transfer from a beat that has
already passed rather than a new idea.**

1. **Grass-height framing, from the b15/b12 precedent.** The b15 plate he passed
   on 2026-08-08 reads *"one slender sapling standing tall in short grass, its thin
   stem rising well above the grass"*, and that is the wording that survives.
   Beat 01 gets the same construction: `standing in short grass, its sturdy curved
   stem rising well above the grass`. This is the round's real lever and it fixes
   two separate failures with one clause. Short grass is a **ground plane**, which
   is what s0/s1/s2 lacked when they hung the plant off the top edge or floated it;
   and it is a **scale reference**, which converts "tall" from a proportion of the
   FRAME into a proportion of the GRASS. His two sentences — *"the sapling reads
   tall"* and *"its tooooo tall"* — only contradict each other while height is
   measured against the frame. Measured against grass they are one instruction, and
   this is the wording that lets the drawing obey both.
2. **Person-binding in the positive-lift convention.** `no girl, no boy, no child,
   no person`, comma-terminated and letter-initial so `sd_prompt` lifts them into
   the negative (the tag forms `no 1girl` / `no 1boy` do NOT lift and would sit in
   the positive asking for a girl — measured, see beat 13). Record 26 proved these
   are necessary but **not sufficient on a beat whose subject clause names a
   humanoid**. Beat 01 is the opposite case — the subject is a plant and no
   character is named — so this is precisely where they are predicted to bind, and
   the r6 result is a clean test of that boundary rather than a repeat of beat 13's.
3. **Register fix from r4.** Measured on the real `sd_prompt` path: the r5 wording
   with the person terms added **dropped `masterpiece, best quality, very
   aesthetic` off the positive tail** — the exact defect `308c74e` found on beat 13,
   arriving here the moment the negations grew. Four token-cuts pay for it, all of
   them things the record has already retired: `banyan` (beat 13 renders without
   it), `exactly` (the table above shows four wordings and none of them made the
   model count, and *"dont overthink the leafs on it"* puts the count out of scope),
   `alone in a vast empty grass field` (now said better by `short grass`), and
   `sunrise, peach and gold morning sky` → `peach and gold sunrise sky`. Tail
   verified intact before rendering, not after.

`no extra leaves` also comes out, and that is a deliberate trade rather than a
cut for space: the negative is at CLIP's ceiling, the four person terms have to
fit, and the leaf count is the one thing on this beat he has explicitly put out of
scope. `fit_negative` still sheds `realistic skin texture, jpeg artifacts,
deformed, extra limbs` from the least-important end and says so out loud — cheap
losses on a plant-only frame whose own negative already forbids people. Everything
rounds 1-4 settled stands: `40cm`, `whole plant in frame`, `wide shot`, the fruit
described without the word `fig`, the scale negatives, `no chibi / no mascot / no
creature / no face`. Four candidates on this beat's own four seeds; the sheet
carries labels and seeds only — no favourite, no ordering (R4).

```
A tiny 40cm seedling standing in short grass, its sturdy curved stem no taller than the grass around it, two oversized cotyledon leaves, one small round purple fruit hanging from the stem, whole plant in frame, wide shot, peach and gold sunrise sky, no girl, no boy, no child, no person, no chibi, no mascot, no creature, no face, no branches, no night sky, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

**r6 RENDERED AND REFUSED — two of the three changes worked and the beat still has
no plate** (ledger record 28, `reject_all`, 0.75; sheet `LABELED-b01-r6.png`).

**Person binding: complete success, 0 people in 4 of 4** against three of four in
r5. Taken with record 26, the boundary is now measured from both sides and is worth
stating as a rule for every other beat: **`no girl, no boy, no child, no person`
binds on a beat whose subject is not a character, and does not bind on one whose
subject clause names a humanoid.** Beat 13 is the second case; this is the first.

**Grass-height framing: half. It fixed WHERE the plant stands and not HOW BIG it
is.** All four have a real ground plane, short grass and a sunrise horizon, and
A2/A5/A6 are +1 across the set — the most consistent environment this beat has
produced. But s0 runs a hairline stem up 85% of the frame, s1 runs it straight out
of the top edge so `whole plant in frame` fails outright, and s2 repeats r5's exact
vine failure and hangs the plant DOWNWARD from the top.

**s3 is the first frame in six rounds inside his ceiling** — a small two-leaf
seedling sitting just above the grass at about a fifth of frame height, which is
what `a tiny 40cm seedling, whole plant in frame` has been asking for since round 1
— and it is ruined by a tall pale rectangular column filling the right third, an
unexplained slab in a field the script calls empty. A7 finally goes positive and A3
goes to -2 on the same frame. Vetoed, and still the most useful frame in the set:
it proves this wording CAN reach the scale he wants.

**The fig is in 0 of 4, which is 0 of 20 across six rounds** (s1 has a pink fruit
lying detached in the grass). More evidence for a conclusion the record already
reached, not a new problem.

**The next lever is not another synonym.** Three of the four failures are about the
stem's LENGTH, and `40cm`, `whole plant in frame` and now `short grass` have all
failed to bound it. The one prompt-side idea left is that **`rising well above the
grass` — the clause this round imported from b15 — is itself what makes it tall**,
and that naming the grass as the measure (*no taller than the grass around it*)
says the opposite thing. That is a different claim from the one b15 proved, so it
is r7's single variable if there is an r7.

**Round 7 ran that variable and the answer is NO — the clause makes it TALLER.**
The fence above now carries r7's wording: `rising well above the grass` gives way
to `no taller than the grass around it`, the record's own phrasing, and nothing
else moves. That the negative did not move is a *precondition* rather than a
claim — `pipeline/render_b01r7.py` refuses to spend a step unless the string it
is about to send matches the negative in the r6 sidecars character for character
and all four person terms survive the 77-token fit. Both passed, so the positive
is the only thing that changed.

**Measured, on the box's real CLIP tokenizer with the r6 fence as the control:**
r7 positive 72 of 77, style anchor INTACT, no sentence dropped; r6 control 70 of
77, anchor intact; delta +2, exactly the two added words. The same check on the
Mac reports the anchor DROPPED and would have stopped the round at its own hard
gate — that is `_token_estimate` over-counting by ~3 near the boundary with no
`transformers` present, the trap r8 documented. The script now refuses to run at
all without a real tokenizer rather than printing an estimate as a measurement.

**The stem height fraction, which is what this beat is now scored on** (apex to
groundline over frame height, against the 32% hairline he revoked):

| seed | frame | result |
|---|---|---|
| 20260720 | s0 | stem exits the top edge *and* runs to the bottom — ~93% visible, `whole plant in frame` fails |
| 20261720 | s1 | hangs DOWN from the top edge, ungrounded — **and stands a child in the grass** |
| 20262720 | s2 | hangs DOWN from the top edge, ungrounded — r5's and r6's vine failure, third round running |
| 20263720 | s3 | the only rooted whole-plant frame: apex 51.8%, base ~90.9%, **stem ~39% of frame height** |

s3 is the number that settles it. On this same seed r6 drew the first frame in
six rounds *inside* his ceiling, at about a fifth of frame height; one clause took
it to 39% — taller than the 32% plate he revoked with *"its tooooo tall"*.

**THE MECHANISM, and it is the part worth keeping: CLIP does not encode negation,
which is the whole reason this codebase lifts `no X` out of the positive in the
first place.** An unlifted `no X` in the positive is read by the model as `X`.
This clause is not lifted — `_NEGATION` captures at most 25 characters before a
comma and the clause is 31 — so what the model actually saw asserted *taller than
the grass around it*. **The proposal recorded above was self-defeating and that is
recorded rather than quietly dropped:** a measure expressed as a negation cannot
work in a positive prompt, and lifting it would not have helped, because it would
have put "taller than the grass around it" in the NEGATIVE, forbidding the
composition instead of bounding it. **Do not spend r8 on `not above` or `never
higher than` — same defect.** If the measure is worth another round it must be
asserted POSITIVELY, as a relation the model can draw rather than a limit it must
respect (grass reaching up over the seedling's leaves, the plant half-buried in
it). That is a suggestion, not a decision.

**Person binding regressed to 1 of 4 and record 28's rule is too strong as
written.** s1 stands a child in the grass with `girl, boy, child, person` all
verified in the sent negative — the same string, to the byte, that returned 0 of 4
in r6 on the same seed. A rule stated as a property of the NEGATIVE was broken by
one clause of POSITIVE text. What fits all three rounds is about the subject:
r5 grounded the plant in 1 of 4 and drew people in 3 of 4; r6 grounded it in 4 of
4 and drew people in 0 of 4; r7 grounds it in 2 of 4 and draws one. When the plant
fails to occupy the frame as its subject, the model fills the composition with a
figure. Hypothesis over three rounds, not a measured law.

**The slab is seed-linked.** s3 carries the same unexplained pale rectangular
column that ruined r6-s3, on the same seed 20263720, surviving a change to the
positive. A fourth round on that seed should expect it.

**The fig is 0 of 4 again — 0 of 24 across seven rounds**, with one honest
ambiguity: the upper rounded form on s0 is the closest any round has come, and at
full resolution it still reads as a curled backlit leaf, as do the s1 and s2 pods,
which carry midribs and pointed tips. Observed, not gated.

Ledger record 41 (`ep2-b01-r7-sample`, `reject_all`, 0.88) was written BEFORE the
sheet. Sheet `LABELED-b01-r7.png`, labels and seeds only — no favourite, no
ordering (R4) — built and not opened.

**Round 8 stopped arguing with the prompt. THE FENCE ABOVE IS UNCHANGED** — r8
was rendered by stripping the height predicate script-side, after asserting the
text on disk is byte-for-byte r7's, so this list still carries one authored
version of the beat instead of eight. `its sturdy curved stem no taller than the
grass around it,` became `its sturdy curved stem,` for the render only: the noun
and both adjectives stay, and only the height instruction leaves. It leaves
because it is going somewhere else — into the init image. This is the lever this
section named on 2026-08-06 (*"the levers that are left are all outside the
prompt — img2img over a chosen plate, a pose controlnet, or a different
checkpoint"*), taken at last.

**The init was not a taste choice, it was the only admissible one.** Gate G1
fails any candidate *conditioned on* a still that is revoked or was never
approved, and an img2img round is conditioned on its init by definition. So the
init has to be a frame the founder has passed, and
`001-capability-inventory/stills/15-something-s-coming.png` (b15-r3-s1) is the
only approved sapling-in-grass frame in the tree. Every beat-01 frame carrying
the right palette — r2-s3, r3-s3, r6-s3 — is unapproved or revoked and would
have failed the round before he saw it. Its sha256 is asserted at render time.

**Three arms on the same four seeds, one axis, and the third arm is a control:**
`i35` (img2img, strength 0.35), `i55` (0.55, the top of the range the
2026-08-06 repaints ever measured) and `t2i` (no init — r7's architecture with
the clause removed). One loaded set of weights, one device, and a sent negative
byte-identical to r6's and r7's, so the arms differ by the init image alone.

**THE ARCHITECTURE WORKS AND THE CONTROL IS WHY WE KNOW:**

| arm | grounded, whole plant | person | pale slab | stem height |
|---|---|---|---|---|
| i35 | **4 of 4** | 0 | 0 | ~30% on all four |
| i55 | **4 of 4** | 0 | 0 | ~25–34% |
| t2i | 0 of 4 | 1 | 1 | apex OFF-FRAME on three |

The t2i control reproduced r5's, r6's and r7's exact failures on demand — s0
runs a stem the full height of the frame, s1 does the same and stands a child
under it, s2 hangs the plant off the top edge ungrounded, s3 carries the pale
column for the **third** round running on seed 20263720. Eight img2img frames
are all grounded, whole-plant, person-free and slab-free. Seven rounds of
wording could not produce one such frame; the init produced eight. It also
settles that the r7 clause was not the cause of the tall stem — deleting it
changed nothing in the t2i arm.

**And it fails on the axis it did not set out to move, which is the finding.**
The i-arms wear the b15 plate's palette and lens: deep amber dusk, a shaft of
light, macro bokeh, where this beat asks for `peach and gold sunrise sky, wide
shot`. The t2i control draws that sky correctly on all four seeds, so the prompt
is fine and the init is overriding it. **The strength ladder says this is not a
tuning problem:** at 0.35 the palette has not moved, and at 0.55 it has *still*
not moved while the stem has begun growing back toward the ceiling (i55-s0
~34%). In this particular plate the palette IS the composition — the light shaft
is what makes it a macro, and the macro is what makes the sapling read small — so
strength cannot buy one without spending the other.

**What r9 should therefore be, and what it should not.** Not another strength. A
**pose or depth ControlNet** takes the b15 LAYOUT as geometry while leaving
colour and light entirely to this beat's own prompt — precisely the separation
strength could not give us. The checkpoint swap is the other named option. A
third exists and is currently illegal: img2img from a beat-01 *sunrise* frame,
which G1 forbids until some beat-01 frame is approved.

**The fig is 0 of 12, and for the first time the observation is informative.**
The init carries no fruit at all, so this was a clean test of whether img2img
adds an object the init lacks, and at both strengths the answer is no — a small
green node at the leaf junction, nothing that reads as fruit. t2i-s3 drew three
rounded pink fruits lying in the grass, unattached. Taken with 2026-08-06's
settled result that size adjectives only make it bigger, the fruit is neither a
prompt lever nor an img2img lever: it is an inpaint, or it is his call to drop it
from this beat.

Ledger record 44 (`ep2-b01-r8-sample`, `reject_all`, 0.72 — lower than r7's 0.88
because this set finally answers the sentence he keeps repeating and invites a
narrow, nameable objection) was written BEFORE the sheet. Sheet
`LABELED-b01-r8.png`, twelve tiles, arm labels, addresses and seeds only, footer
saying the rows are the parameter axis — built and not opened.

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

Line: the tree's. Camera ON THE TREE for the tree's own line — framed TIGHT on the leaves, because the scavenger is still crouched low in the grass behind the plant and a wide shot would read as him having left (caught by the comprehension gate).

**KNEE-HEIGHT REWRITE 2026-08-17 — the prompt below is UNCHANGED and the pick
survives.** His ruling was *"rewrite the beats to work at knee height. change the
story."* Beat 12's script line said the scavenger was *"crouched behind the trunk,
below frame"*, which only works if the plant is tall enough to have a crouching man
below its leaves; at ~40 cm it is not. The line now reads *"crouched in the grass
behind them, out of frame"*. **Nothing in the picture changed** — this beat's
`done_when` requires the goblin ABSENT and the prompt already says `no trunk, no
ground, no other character`, so the fix was entirely in off-screen prose.
`ep2-b12-tightB` is therefore NOT invalidated.

**Round 3 was rejected on all four (ledger record 19, `ep2-b12-r3-provisional`,
`reject_all`, 0.88): every frame made a large pink RIPE FRUIT the subject of a beat
whose own text says `no fruit`, s0 gave that fruit a face, and s2 put a city
skyline behind it.**

**Round 4 is the plant-only recipe, and it is two fixes that this file already
owns.**

**`mascot-simple` comes out, and it is the first cause.** Beat 01 recorded on
2026-08-06 that this word — borrowed from beats 02-03, where it modifies a sapling
a goblin hides *behind* — becomes the SUBJECT when it leads a plant clause, and
three of four candidates there came back as a chibi mascot CREATURE with leaves on
its head. It has been sitting in this beat's prompt ever since. s0's fruit with a
face is that same failure: asking for a mascot and then being surprised by a face.
So the word goes, and **beat 01's negative block — `no chibi, no mascot, no
creature, no face` — comes in**, which is safe here for the reason `308c74e` set
out: lifting `creature` and `face` is safe only on the **plant-only** beats (01,
12, 16, 18, 21), and this is one of them. Beat 13, whose subject IS a creature with
a face, must never get this block. `no city, no buildings` joins them for s2's
skyline.

**Register fix, same as beat 13's.** Beat 12 is on `308c74e`'s list of eleven
tail-droppers (2, 3, 6, 7, 12, 13, 15, 16, 18, 19, 20) — beats where `compress()`
was shedding the trailing sentence to reach CLIP's 77 tokens and taking `cinematic
lighting, detailed, newest` and Animagine's `masterpiece, best quality, very
aesthetic` with it. The long em-dash clause is what cost the budget, so the prose
is rewritten tight and the tail was **measured intact before rendering**, not
assumed. `sapling` also gives way to `seedling`: it is the botanical vocabulary the
passing beats use, and it is in `sd_prompt._SMALL`, so the scale negatives keep
firing.

**What this round does NOT claim.** `no fruit` was already lifting into the
negative in r3 and the model drew fruit anyway, so the ripe fig is not simply an
un-negated word. The bet is that it was `mascot-simple` pulling a whole mascot
composition — face, fruit and all — into a frame that asked for two leaves, and
that a tight leaves-only subject with the mascot vocabulary gone leaves nothing for
the fruit to hang off. If r4 comes back with fruit again, that hypothesis is dead
and the next lever is the count tag, not more negations.

```
Extreme close-up of two oversized green cotyledon leaves of a tiny seedling filling the frame, utterly still, peach and gold morning sky and drifting blurred clouds behind them, no trunk, no ground, no fruit, no chibi, no mascot, no creature, no face, no other character, no city, no buildings, very slow push-in, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

**r4 RENDERED, THE HYPOTHESIS HELD, AND `b12-r4-s2` IS A PROVISIONAL PICK** (ledger
record 31, `pick_holds`, 0.70; sheet `LABELED-b12-r4.png`). PROVISIONAL — a
steward prediction of his taste logged before he saw it. He has ratified nothing.

**The ripe fruit is gone in 4 of 4**, against 4 of 4 carrying it in r3. So is the
face s0 put on it and so is s2's city skyline. The reading this round committed to
in writing beforehand is the one that survives: `no fruit` was already lifting into
the negative in r3 and being ignored, because **`mascot-simple` was importing a
whole mascot COMPOSITION — face and fruit together — that negating one noun could
not dismantle. Removing the word that summons the composition beat negating its
parts.**

**That result transfers, and it should be spent: beats 02 and 03 still carry
`mascot-simple`.** It is the correct word there — it modifies a sapling the goblin
hides *behind*, so it is not the subject — but this beat carried it for the same
reason and it took over anyway. Worth a look before either is redrawn.

s2 is the pick: several large backlit green leaves filling the left and centre with
sun and drifting cloud behind, which is this beat's own sentence. s0, s1 and s3 are
clean of every r3 defect but are SKY pictures with leaves at the edge, and the beat
exists to be the tree holding still while the sky moves — a frame where the sky is
the subject inverts it. **The risk on the pick is A1, scored 0:** these are long
lanceolate leaves and the sapling elsewhere in the show has broader rounded
cotyledons. With no stem or silhouette in a close-up the mismatch is arguable
rather than glaring, but it is the axis to watch. Leaf COUNT is deliberately not
scored — out of scope since 2026-08-08.

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

> *The round-5 wording, retired as the live fence when round 6 replaced it —
> `parse_shots` reads the FIRST fence in a beat's section, so a superseded prompt
> cannot stay fenced or it is the one that renders. Recorded verbatim in the four
> `13-the-shade-r5-s*.png.meta.yaml` sidecars, which is where prompt provenance
> actually lives:* "A tiny 40cm seedling with two oversized cotyledon leaves
> stands in open grass; a small round goblin folds into its patch of shade, knees
> up around his ears, no girl, no boy, no child, no person. Midday light, open
> green grass field, cinematic lighting, detailed, newest, masterpiece, best
> quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no
> text."

**ROUND 5 RENDERED AND WAS REJECTED. Subject order was not the fault either**
(ledger record 27, `ep2-b13-r5-sample`, `reject_all`, 0.90). Four seeds, 38
GPU-seconds, 2026-08-09. Measured before rendering: 64 positive tokens on the box's
real CLIP tokenizer with the boosters and style anchor intact, 69 negative,
nothing dropped from either — so the r4 register fix is confirmed stable across a
rewording, and it is the only thing here that is.

**Zero of four contain the seedling as a plant, for the third round running.** s0
is a chibi creature asleep in grass wearing leaves as a hood; s1 is an anime child
in a leaf hat, human face, unmistakable; s2 collapsed both nouns into a single
pale-green sphere the size of a boulder with leaves stuck to its sides; s3 is a
pointed-eared chibi with two cotyledons **growing out of the top of its head** —
beat 19's recorded fault, now drawn on this beat in two consecutive rounds. And the
person negatives were verified lifted and s1 is still a child.

**THE DIAGNOSIS THIS BUYS, AND IT IS WORTH THE FORTY SECONDS.** Three rounds have
now attacked this beat through the positive prompt's grammar and A1 has not moved
once:

| round | what it changed | A1 |
|---|---|---|
| r3 | scale/creature negatives as the picks page recommended | -2 in 4 of 4 |
| r4 | shortened until the style tail survived; botanical binding (`seedling`, `two oversized cotyledon leaves`) | -2 in 4 of 4 |
| r5 | subject order inverted — seedling leads, goblin subordinate | -2 in 4 of 4 |

Beat 01's botanical binding did not transfer, and neither did subject position. The
theory that the goblin was winning because it held the subject slot predicted that
promoting the seedling would separate them; **it did not separate them, it fused
them harder** — r5's s2 is the two nouns as one object, which is a *worse* fusion
than r4's, not a better one. So the remaining variable is the one r5's own note set
aside on purpose: **the Danbooru count tag `1other`, which has been held constant
at exactly one non-human character across r3, r4 and r5 while the beat needs two
subjects in frame — a goblin AND a 40cm seedling.** Every round so far has asked
this checkpoint to draw two things while a tag in the prompt asserts there is one,
and the checkpoint has resolved the contradiction the only way it can: by merging
them. That is now the leading hypothesis and it is the next experiment.

**It is NOT run tonight, and no wave fires off this beat.** Two further things are
recorded as candidates so the next round changes one of them and not three: the
count tag itself (`sd_prompt.count_tag` is pipeline code, so changing it is a code
change with its own tests, not a prompt edit), and the possibility that a
two-subject frame is not a prompt problem at all — a plate composed from the beat
01 seedling with the goblin drawn in by img2img would sidestep the count tag
entirely. **Choosing between those is a taste and scope call, not a steward call.**

**ROUND 6 IS THE VOCABULARY CORRECTION, and it is the first round that attacks
the count tag.** Specified in full by `pipeline/research/two-subject-composition.md`
§3.1 and §5 — a research memo built from the Animagine model card, the Danbooru
wiki and the diffusers docs, not from our own code comments. The memo's finding is
that r5's own closing note was half right: `1other` is indeed the remaining
variable, but the Danbooru wiki defines it as *"a **humanoid** character of
ambiguous or indeterminate gender"* — it is not a "not a person" tag at all. So
every round so far has opened by asserting the humanoid its own negatives were
trying to remove, which is why r4's s1 and r5's s1 came back as anime children
*after* `girl, boy, child, person` were verified lifted into the negative. Second
finding, never yet tested: the fusion classes have exact Danbooru tag names —
`leaf on head` alone carries ~10.5k posts — and **not one of them has ever been in
our negative.** The prose `no girl, no boy` that `_NEGATION` lifts are weak
negatives on a checkpoint trained on comma-separated tags.

Three changes, all inside existing tooling, and nothing else moves:

1. **Count tag `1other` → `1boy`,** obtained the only way it can be — by the
   leading clause, since `_tag_from_clause` derives the tag and you cannot set it
   by writing it. `a small round goblin boy` puts a `_MALE` token in the first
   comma-clause, and `_MALE` is tested before `_OTHER`, so the deriver returns
   `1boy` with `goblin` still at token four. `solo` follows it: it asserts
   *exactly one character*, which forbids the second figure while leaving the
   plant free, because scenery is not a character and no count tag can ask for one.
   **Entailed by this and stated so it is not mistaken for a fourth change:
   `no boy` and `no person` come OUT of the prose.** Declaring `1boy` and negating
   `boy` in the same prompt is the exact self-contradiction §1a says is the defect;
   keeping it would reintroduce the fault under a new name. `no girl` and
   `no child` stay — they target r4/r5's actual failure and contradict nothing.
2. **The fusion classes negated in tag form**, through the `explicit` tier so
   `fit_negative` protects them: `leaf on head, plant girl, alraune, monster girl,
   flower on head, head wreath, hair ornament, leaf hair ornament, plant hair`.
   These are the *exact names of what r4 and r5 drew*.
3. **The plant re-bound as scenery** — `Plant, grass, outdoors` opening its own
   sentence, rather than hanging off the goblin in a prepositional phrase. This is
   Danbooru's grammar for "a plant is in the shot and belongs to the ground".

Deliberately NOT bundled: the two-pass inpaint (§3.2), regional IP-Adapter (§3.3)
and the checkpoint swap (§3.8). Running vocabulary and architecture in one sample
would tell us nothing about either — the same argument r5 made for holding the tag
constant while inverting word order, one rung up.

**Pre-registered gate, written before the render.** Per seed, four binary
predicates (memo §5): P1 the plant is present *as a plant*, rooted, not touching
the character; P2 the goblin is a goblin, not a human child; P3 no fusion —
nothing plant-like growing from head or body; P4 two separate silhouettes with
background visible between them. r4 and r5 both scored **0/4**. **Pass = at least
3 of 4 seeds passing all four predicates.** Any result above zero is information;
only ≥3/4 unblocks the fifteen goblin-and-plant beats.

> *The round-6 wording, retired as the live fence when round 8 replaced it —
> `parse_shots` reads the FIRST fence in a beat's section, so a superseded prompt
> cannot stay fenced or it is the one that renders. Recorded verbatim in the four
> `13-the-shade-r6-s*.png.meta.yaml` sidecars, and inherited byte-for-byte by
> round 7, which changed only the conditioning:* "A small round goblin boy, solo,
> folds into a thin patch of shade, knees up around his ears, no girl, no child.
> Plant, grass, outdoors, a tiny 40cm seedling with two oversized cotyledon leaves
> rooted in the ground beside him. Midday light, cinematic lighting, detailed,
> newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render
> look. 9:16 vertical, no text."

**ROUND 6 RENDERED. THE FUSION IS GONE AND THE GATE STILL FAILED, 1 of 4**
(ledger record 32, `ep2-b13-r6-sample`, `reject_all`, 0.72). Four seeds, 37
GPU-seconds, 2026-08-09. Measured on the box's real CLIP tokenizer before a step
was spent: **count tag `1boy`** confirmed off the real `sd_prompt` path, 72
positive tokens with boosters and style anchor intact and **nothing dropped from
the positive**, negative 73 sent.

**Three rounds of grammar moved nothing; the vocabulary correction moved three
predicates out of four on the first try:**

| round | what it changed | P1 plant | P2 goblin | P3 no fusion | P4 two shapes | all four |
|---|---|---|---|---|---|---|
| r3 | scale/creature negatives | 0/4 | — | 0/4 | 0/4 | 0/4 |
| r4 | style tail saved; botanical binding | 0/4 | 1/4 | 0/4 | 0/4 | 0/4 |
| r5 | subject order inverted (confounded — see below) | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| **r6** | **`1boy, goblin, solo` + fusion tags negated + plant as scenery** | **4/4** | **1/4** | **4/4** | **4/4** | **1/4** |

Not one frame wears a leaf, grows a cotyledon out of its head, or collapses the
two nouns into a single object, and every frame has a rooted plant with clear
background between it and the character. **The count tag was the cause**, exactly
as the memo argued from the Danbooru wiki: `1other` asserts a humanoid, so r3–r5
spent every round asking for the very thing their negatives were deleting, and no
count tag can give a plant a slot because plants are not characters.

**P2 is what failed, and it is now a different problem than it was.** It is no
longer the prompt contradicting itself — it is `goblin` losing to `1boy` in three
seeds of four: s0 is a pale elf child, s1 a featureless dome-headed figure, s3 a
hood with no face. **s2 proves the tag can win** — green skin, long pointed ears,
grey cloak, the closest thing to this show's goblin yet drawn on any beat — so
this is weighting and conditioning, not impossibility.

**The memo's pre-committed ladder therefore selects §3.3, regional IP-Adapter on
the 5090 box**, conditioning the goblin region on an approved goblin still: "that
is an A1 problem and IP-Adapter is the A1 tool." The ladder was fixed in advance
precisely so this choice would not be made by whoever was disappointed, and it is
not being re-made now. **No wave fires** — the gate said ≥3 of 4 and the answer is
1 of 4.

Two things recorded so they are not rediscovered as surprises. **The negative
budget collision was real and harmless:** nine fusion tags push the negative to 99
CLIP tokens, and `fit_negative` sacrificed seven house terms to fit (`realistic
skin texture, jpeg artifacts, deformed, extra limbs, blurry, low quality,
signature`) — pre-authorised by the memo, asserted by the render script (every
fusion term had to survive or it stopped), and the frames came back clean anyway
at A5/A6 +1 in four of four. **And re-binding the plant as scenery bought
separation at the cost of intimacy:** no frame draws the shade *relationship* the
line depends on — nobody sits in shade cast by the seedling he is thanking — and
s1 draws a thick tree trunk, which the scale negatives forbid and which inverts
the joke the beat is built on. That is the next prompt problem after the identity
one.

**r5's result cannot confirm or deny its own hypothesis, and is scored here only
for completeness.** It changed subject order on top of the two causes r6 has now
shown to be live and untouched at the time, so its 0/4 is not evidence about
subject order — the memo said so before r6 ran, and r6 did not change that.

**ROUND 8 IS THE SPECIES CORRECTION, and the founder ordered it.** His words,
2026-08-09: *"all the goblin images look like female demihumans, definitely need
to regenerate"* — set against the script's own noun, *"a small round goblin"*.
Four axes fall out of that sentence and they are the round's target: **male,
round, green-skinned, and not an elf.**

**r8 goes back to the r6 branch, and that is forced, not preferred.** Record 34
ruled that G1 — "staged on, CONDITIONED ON, or demonstrated with a still that is
REVOKED or was never approved" — fails every frame the regional IP-Adapter
produces, because it conditions on `13-the-shade-r6-s2`, which the founder has
now explicitly rejected along with the rest. The same bar disqualifies §3.2, the
two-pass inpaint, which would need an approved plate we do not have. **The only
admissible branch tonight is the one that draws from text alone**, and the memo's
own §3.1 result is the reason it is worth taking: the vocabulary correction is
the only move that has ever shifted a predicate on this beat, and it shifted
three at once.

**THE MECHANISM IS MEASURED, not reasoned from our own frames.** Danbooru wiki
post counts, read 2026-08-09:

| tag | posts | what the corpus says |
|---|---|---|
| `goblin` | 4,257 | *"child-sized, with green skin, fangs, pointy noses, and pointy ears"* — the show's goblin IS the canonical one |
| `female goblin` | 1,717 | **implicates `goblin`** — so **40.3% of everything carrying the token `goblin` is female** |
| `elf` | 111,449 | *"grace, finesse, and youthful appearance"*; implies `pointy ears`. Outweighs `goblin` **26 to 1** |
| `green skin` | 30,541 | implicates `colored skin`; *"often associated with orcs"* |
| `colored skin` | 208,206 | *"any color that would be unnatural for a normal human"* |
| `plump` | 43,371 | *"slightly chubby, but not enough to be fat"* |
| `fat` | 19,390 | *"chubbier than plump"* — overshoots the script's "round" |
| `male focus` | 1,106,133 | *"can be tagged with either 1boy or multiple boys"* — additive to the count tag, not a replacement |

**That table answers the founder's complaint with a number.** Two in five posts
carrying the token `goblin` are tagged `female goblin`, and because the child tag
implicates the parent, every one of them trained the word `goblin` on a female
demihuman. *"All the goblin images look like female demihumans"* is not a
mis-render — it is the corpus, sampled faithfully. And the elf is the same story
one step up: `elf` outweighs `goblin` 26:1 and carries pointy ears with it, so a
young pointy-eared humanoid resolves to the far heavier tag. **These are the
exact tag names of both failures, and neither has ever been in a negative on this
beat** — the same class of gap §1b found for the fusion classes, which is the gap
r6 closed to take P1/P3/P4 from 0/4 to 4/4.

**`1boy` IS NOT THE FAULT AND IT STAYS — this was checked before it was kept.**
The suspicion was that `1boy` pulls the pretty-boy/elf reading. It does not
survive the evidence. `_tag_from_clause` derives the tag from the first
comma-clause and tests `_MALE` before `_OTHER`, so removing "boy" does not give a
neutral prompt — it gives `1other` back, the tag §1a proved asserts *"a humanoid
character of ambiguous or indeterminate gender"* and which cost r3–r5 three
rounds at 0/4. Dropping `1boy` would attack the not-female axis by deleting the
only token asserting male. The female mass is measured to be inside `goblin`,
not inside `1boy`. **`monster boy` was considered and rejected on its definition,
not on taste:** it denotes *"a bishounen or ikemen mixed with a monster"* — it
names the pretty-boy failure rather than curing it.

**THE BUDGET DECIDED HOW MUCH VOCABULARY FITS, and it was measured on the box's
real CLIP tokenizer before a step was spent.** Seven candidate wordings were run
through the real `compress()`. Every variant carrying three or more species tags
came back **with the style anchor deleted** — `compress()` sheds the trailing
sentence to reach 77, and that sentence is `Midday light, cinematic lighting,
detailed, newest, masterpiece, best quality, very aesthetic`. That is precisely
the r4 defect this beat already paid for once, so it is a hard stop, not a
trade. Measured: `green skin, colored skin, plump` = 61 tokens **with the anchor
gone**; `green skin, plump, male focus` = 62 **with the anchor gone**;
**`green skin, plump` = 77 tokens with the anchor and the plant sentence intact
and nothing dropped.** Two tags is what the budget buys, so `colored skin`,
`male focus` and `pointy ears` are **filed, not bundled** — and `pointy ears`
would in any case be arguing for the elf, which implies it.

**Exactly one axis moves: the species/build assertion, said in the checkpoint's
own vocabulary.** Both halves are that one axis, which is r6's move applied to
species instead of count — assert what the goblin IS, negate the exact tag names
of what it keeps coming back as:

1. **Positive:** the prose word `round` gives way to the tag `plump`, and the tag
   `green skin` is added. `green skin` is the attribute P2 turns on and record 34
   filed it as a candidate after r7 failed to transfer it from an image. Nothing
   else in the sentence moves; the plant sentence and the style tail are r6's,
   byte-for-byte, because P1/P3/P4 are at 4/4 and this round must not touch them.
2. **Negative:** `female goblin` and `elf` join r6's nine fusion tags in the
   `explicit` tier, where `fit_negative` protects them. Measured: all eleven
   survive at 76 tokens, at the cost of two more house terms (`watermark`,
   `abstract`) on top of the seven r6 already sacrificed — pre-authorised here
   the same way r6 pre-authorised its seven, and asserted by the render script,
   which stops if any of the eleven is dropped.

**The known risk, stated in advance.** `elf` implies `pointy ears`, and the
Danbooru goblin has pointy ears, so negating `elf` may cost the ears this
creature is supposed to have. If r8 comes back green and plump with small round
human ears, **that** is the trade and `pointy ears` is the next positive tag to
buy — which is also the round that would need `colored skin` cut to pay for it.

**Pre-registered gate, written before the render, and it grows by the founder's
two axes.** Per seed, the memo §5 four, plus the two his verdict added: P1 the
plant is present *as a plant*, rooted, not touching the character; P2 the goblin
is a goblin, not a human child; P3 no fusion; P4 two separate silhouettes;
**P5 not female — the figure reads male or at minimum not feminine-coded; P6 not
an elf — green-skinned goblin, not a pale graceful fantasy humanoid.** r6 scored
1/4 on the original four and r7 scored 0/4. **Pass = at least 3 of 4 seeds
passing ALL SIX.** Ledger record written BEFORE any sheet is built. No wave fires
off this beat without the founder, and nothing here goes on his screen tonight.

```
A small goblin boy, green skin, plump, solo, folds into a thin patch of shade, knees up around his ears, no girl, no child. Plant, grass, outdoors, a tiny 40cm seedling with two oversized cotyledon leaves rooted in the ground beside him. Midday light, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

**KNEE-HEIGHT REWRITE 2026-08-17 — THE TRUNK-SLIDE IS GONE AND THE PROMPT ABOVE IS
NOT TOUCHED.** His ruling: *"rewrite the beats to work at knee height. change the
story."* This is the beat `done-definitions.yaml` has carried a flagged SCRIPT
CONFLICT on since 2026-08-15 — *"the script says 'slides down the trunk', and the
founder has ruled the sapling is tiny … so there is no trunk to slide down. The END
STATE is what the beat needs; how he gets there is an author call, not a steward
one."* That author call is now made.

~~"The scavenger slides down the trunk and folds into the sapling's tiny shade,
knees up around his ears."~~ → *"The scavenger's legs give out and he drops to sit
in the grass at the base of the stem, then tips his head sideways into the sapling's
hand-sized patch of shade — the only part of him it will cover — knees up around his
ears."*

**Why this is a new action and not a softer one.** The slide was a vertical descent
*along the plant*, and no 40 cm plant affords one. The replacement is a collapse onto
the ground *beside* it, and it carries a new idea the old line did not have: **the
shade is smaller than he is, so he has to choose which part of himself to shade, and
he chooses his eyes.** That is what makes the beat's line land — *"…Thanks for the
shade"* is sincere and absurd at once, and the gift is now measurable at one head's
worth. The beat's job is unchanged: this is where cover becomes company, where the
fugitive stops hiding *behind* the plant and starts living *at* it, and it is the
first time he addresses it. It still ends him on the ground with his hands in reach
of the dirt, which is what beat 14 needs, and still folded small with knees up, which
is what beat 17's opening plate was to be built from.

**THE END STATE IS PRESERVED VERBATIM IN ITS OWN TERMS** — *"he ends FOLDED SMALL in
the sapling's shade, knees up"* — so `done_when` is satisfied by the new line and no
definition has to move. Its SCRIPT CONFLICT paragraph is now discharged and reads
stale; re-transcribing it belongs to the pick lane that owns that file, and it is
flagged there rather than edited from here.

**The prompt above is deliberately unchanged, for two measured reasons.** It already
stages the end state and never staged the approach — `folds into a thin patch of
shade, knees up around his ears` beside `a tiny 40cm seedling … rooted in the ground
beside him` — so it was never asking for a trunk-slide and is knee-height correct as
written. And it sits at **exactly 77 CLIP tokens measured on the box's real
tokenizer**, with eleven negatives the render script asserts; one added word sheds
the trailing sentence and deletes the style anchor, which is the r4 defect this beat
has already paid for once. Buying the sit-down in words is a later round's trade —
`folds into` → `sits down into` is same-length and is the cheapest candidate — and
it is a gross whole-body move, which is the class this engine renders (12 of 12
stand-ups on beat 17's wide plate) rather than the small in-hand class it drops.

## Beat 14 — THE DEFENSE (1:04–1:10) ⬜ needs footage

Line: the apple defence. Camera on his hands in the dirt — embarrassment made physical.

```
A small goblin's clawed fingers pick and scratch at loose dirt, flicking pebbles aside, while above them his face glances away, embarrassed, then back down. Intimate low close-up, shallow green grass background, close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 15 — GOOD LISTENER (1:10–1:15) ⬜ needs footage

Line: "You're a good listener." Camera holds BOTH of them — the conversation is the subject.

**KNEE-HEIGHT REWRITE 2026-08-17 — the look is now DOWNWARD, and that is a better
beat.** His ruling: *"rewrite the beats to work at knee height. change the story."*
~~"He looks up at the sapling; both of them share the frame."~~ → *"He tips his head
down and sideways until his eyes are level with the two leaves, and talks to them
from a hand's width away; both of them share the frame."* Looking UP at a ~40 cm
plant requires him lying under it; sitting from beat 13 his eyes are already above
it. **The beat's job is that the conversation is the subject and he treats the plant
as a person, and a man lowering himself to be eye-level with a seedling says that
harder than a man gazing up at one.** It is also what the child episode already
does — 003b stages *"He crouches until he is eye to eye with the little tree"* — so
this fixes a continuity break rather than making one.

Prompt above, superseded sentence kept: ~~"A small goblin tips his head back and
looks up at the tiny sapling standing tall beside him, talking, gesturing with one
hand; the sapling's two oversized leaves hang above him in frame."~~ The replacement
is **33 words against 33** — this beat is on `308c74e`'s tail-dropper list, so the
budget was the constraint and the count was held exactly rather than eyeballed. It
was **NOT measured on the real CLIP tokenizer** (none installed here, and this pass
was $0 with no GPU), so the word count is the only guarantee offered. Two side
effects, both wanted: the shot gains the scale anchor `40cm`, which
`check_sapling_scale.py` recognises and this prompt previously had none of, and it
drops `oversized`, which §4 of `THE-SAPLING.md` records as unruled.

**WHAT IT COSTS: nothing.** All twelve existing candidates were already scored ALL
CANDIDATES FAIL (eight have no rooted plant at all, four are indoors), and beat 15
holds no pick. `done_when`'s *"he LOOKS UP"* is now stale and needs re-transcribing
to the level look — flagged for the pick lane that owns that file, not edited here.

```
A small goblin sits in the grass, head tipped down so his eyes are level with the two leaves of a tiny 40cm sapling beside him, talking to it, gesturing; both in frame. Warm midday light, lonely tone, slow push-in, two-shot, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
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
One small round purple fruit trembles on the thinnest branch of a tiny sapling, its stem flexing under the weight, rimmed by warm amber afternoon light against a soft wash sky. The trembling grows; the stem bends further. Held macro, no cut, extreme close-up, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

## Beat 19 — THE DROP (1:34–1:39) ⬜ needs footage

No dialogue — the physical event. Deliberately WIDE (the gate flagged a scale jump from the previous macro): tree and scavenger must share one frame so cause and effect read in a single take. The fruit never touches him: the head-bounce this beat used to ask for was killed by the founder on 2026-08-15, and the superseded prompt is kept beside the correction in this board's source file, shots.md, not on this page.

```
One small round purple fruit drops from the branch of a tiny sapling standing tall and lands in the grass at the feet of a small round goblin walking below, who stops mid-step and looks down at it. Single continuous take, static camera, amber afternoon, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

**CORRECTION 2026-08-17 — THE HEAD-BOUNCE IS DEAD, and this board was the last
published place still asking for it.** The founder ruled on **2026-08-15**:
*"ok then just make the fig fall on the ground and the goblin will notice it"* —
superseding his own earlier *"lets make it drop on his head"*. He changed the
script himself the same day (`node.md:118`, commit `a483eb52`, "the fig falls on
the ground now, so the board entry that foreclosed that has to say so"), which
now reads *"the stem lets go, the fig falls, and lands in the grass at his feet.
He notices."* `review/ep2-picks/done-definitions.yaml` beat 19 makes the contact
**disqualifying**: *"NO CONTACT WITH HIS BODY — a take where the fruit touches
him fails this beat now, however well it moves."* The eight beat-19 drafts in
`pipeline/wave-drafts.yaml` were corrected on 2026-08-16 (the four that can still
fire; the four whose only consumer had already fired are left as receipts). This
file was not, and it is the one a reader sees: it is published at
`/sapling/002b-first-citizen-shots`.

**What changed in the prompt above, and nothing else did.** `bounces softly off
the head of` → `lands in the grass at the feet of`, and the beat's third
requirement — *he NOTICES it* — is now stated (`looks down at it`) because
`done_when` asks for the fall, the landing and the noticing, in that order. The
fruit still **starts on the stem** (`drops from the branch`), which
`plate_requirement_0815` keeps as disqualifying and which no existing beat-19
plate satisfies. The corrected sentence is 38 words against the superseded 40, so
it cannot newly overflow `compress()`; **it was NOT measured on the real CLIP
tokenizer** — no tokenizer is installed on this machine and this change was $0
with no GPU — so the word count is the only guarantee offered here.

**Superseded 2026-08-15, kept verbatim so nobody restores it by finding it
quoted somewhere else** (this is the same reason `done_when_superseded_0815`
exists beside its replacement):

```
One small round purple fruit drops from the branch of a tiny sapling standing tall, bounces softly off the head of a small round goblin walking away below, and lands in the grass at his feet as he stops mid-step. Single continuous take, static camera, amber afternoon, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
```

**The eight `19-the-drop-r1-*` / `19-the-drop-r3-*` stills under `takes/stills/`
keep the bounce in their sidecars and are NOT corrected.** Those record the bytes
actually sent to the model; editing them would falsify a receipt rather than fix
a render. They are stale as to the bounce and they lose to the ruling.

**A published child episode depends on the line this removes, and that is the
author's call, not ours.** `003b-one-leaf-for-yes/node.md:83` reads
*"Were you the fruit? Did you MEAN to hit my head?"* and is live at
`/sapling/003b-one-leaf-for-yes`. Nothing in 003b is touched here; the conflict is
raised on the founder's board (`review/inbox.yaml`, card raised 2026-08-17).

## Beat 20 — EVIDENCE (1:39–1:42) ⬜ needs footage

Line: "…Did you just answer me?" Camera on the goblin holding the fig like evidence.

```
A small round goblin crouches, picks one small round purple fruit up out of the grass with both hands, straightens, and raises it in front of him like evidence, huge eyes widening as he looks up at a bare branch above. Warm amber afternoon light, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No photorealism, no 3D render look. 9:16 vertical, no text.
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

---

## Founder verdicts — 2026-08-11 ~16:15 local, the whole episode-2 picking page

Roman walked the picking page beat by beat and ruled on seven beats plus the
episode. His words are recorded verbatim below and scored in
`taste/steward-model.ledger.yaml` (SIXTH scoring; the per-beat verdict records
are `ep2-b01`..`b05-pickpage-founder-verdict-0811` and
`ep2-pickpage-founder-directive-0811`). Nothing here deletes or edits anything
above it — the prompts above are the record of what was sent, and this section is
the record of what he said about the results.

**Beat 01 — COLD OPEN.** *"none of them have figs and all of them have too many
leafs"* — rounds 5 through 9 and the fig frames, rejected together. Two faults,
both COUNTS, and both had already been drawn wrong and written down above: the
fig appeared in none of the candidates and the leaf count ran 4-6 where the
script has a two-leaf sapling. His 2026-08-03 approval of this node made the fig
a condition of the script (*"we need to make SURE the fig growing on the sapling
is mentioned"*), so a beat-01 frame without one does not satisfy him however well
it is drawn. The next round states TWO LEAVES and ONE FIG affirmatively and
counts them, and holds everything else minimal.

**Beat 02 — THE SPRINT.** *"none of them, are you sure you are using the right ai
image generator? this look quite bad"* — his second question about the ENGINE
rather than the prompt. It goes back to him as a question: the engine is
animagine-xl-3.1 on the box, $0, and it is the same engine that drew the goblin
he ratified three hours earlier.

**Beat 03 — BAD COVER.** *"ai is going too crazy, making the goblin in a house,
making the goblin compeltely white, making 2 goblins, and other weird stuff"* —
one setting fault and two that are properties of the SET, not of any frame: the
four candidates disagree with each other about what the goblin is and how many of
him there are.

**Beat 04 — THE FOOTNOTE.** *"these close ups are not really good, but they are
the old versions after all.. basically, bad character consistency, makign the
goblin look too complicated and ending up making t bad"* — a verdict on the
RECIPE. Those frames were the IP-Adapter set and the `green skin, tusks` tags-only
set, both from 2026-08-10. At ~15:45 the same afternoon he ratified the opposite
recipe on beat 15 — tags only, `green skin`, nothing else. Beat 04's prompt above
is unchanged and needs no staging fix: it states its shot size twice (*his face
filling the frame*, *close-up*) and is where the 2026-08-11 `medium shot` fix on
seven other beats was copied FROM. Re-run as `ep2-b04-goblin-close-0811`, one
variable — `tusks` removed.

**Beat 05 — THE PATROL.** *"almost all look like they are in some snowy forest,
otherwise its actually not bad"* — the only warm clause in the whole walk, and it
names ONE fault, the environment. It is not an approval of the guards: silence on
an element is not approval of it, and eleven lines later he says the guards have
no character yet.

**Beat 06 — THE CLIPBOARD.** *"none of them.. should probably setup a character
for the guards, take your time doing that"* — a PRESCRIPTION, not a fault. The
guards have never had a character reference of any kind, and six beats of this
episode are guard beats (05, 06, 07, 09, 10, 11). *"take your time"* is a licence
to spend time, which is the opposite of the usual constraint.

**Beat 07 — THE POINTING.** *"mot of them look good but as i said in beat 06, we
need to setup character consistency even if they only appear once. i mean, maybe
dont waste too much time on it but it will be needed so we dont have confusion"* —
he opened warm and still said no, and bounded the ask in the same breath: a cheap
reference per recurring body, not an identity programme.

**The episode.** *"i looked at all the beats and you have to change pretty much
all of them, do some regeneration, and do some evaluating of your own. train the
system."* Read with ONE SAMPLE BEFORE ANY BATCH: one sample per recipe change,
sequentially — not fifteen beats fired because he said "all". No guard-beat round
fires until a guard character reference exists and he has seen it.
