# DIAG — negation clauses in positive prompts

Read-only audit, 2026-08-11. No prompt, spec or job file was edited. Every fix
below belongs to the lane that owns the beat.

## What was searched, and the denominator

| source | files read | distinct positive prompts |
|---|---|---|
| `.meta.yaml` sidecars (what was actually SENT) | 771 parsed (868 on disk; `.vercel/output/static/**` excluded as build copies of `review/**`) | — |
| `pipeline/jobs/*.yaml` — `payload:` `*-prompt.txt` blocks | 124 job specs, 74 carrying prompt text | — |
| `pipeline/farm-queue.yaml` | 1 | 0 (no `prompt:` key in `tasks:` or `backlog:` today — every hit is a comment) |
| `pipeline/wave-drafts.yaml` — `authored:` | 1 | 15 |
| `genomes/sapling/nodes/*/shots.md` — fenced beat prompts | 9 nodes | 240 |
| loose `*prompt*.txt` under `review/` | 4 | 4 (3 duplicate a sidecar exactly) |
| `pipeline/jobs/ep2-*-goblin-*.yaml` | 24 | 0 inline — they invoke `render_wave_sample.py`, whose text is the `wave-drafts.yaml` row |

**Sidecar and job-spec prompts, deduplicated by exact normalised text: 192
distinct positive prompts.** Plus 240 authored `shots.md` beat prompts and 15
`wave-drafts.yaml` drafts, which are the *source* text for the SDXL path rather
than the sent text — counted separately because `sd_prompt.compress()` rewrites
them before they are sent.

| pipeline | distinct sent positives | carrying a negation clause |
|---|---|---|
| **LTX-2.3-Distilled i2v** (guidance 1.0) | 38 | **26** |
| SDXL stills (`animagine-xl-3.1`, guidance 7.5) | 71 | 7 |
| legacy video — Veo 3.1, wan, AnimateDiff/dreamshaper, ti2v5b, animegen, pixverse, hailuo | 77 | 44 (all archive) |
| deterministic hold-still (`hold_still.py`, no model) | 6 | 0 |

Authored source text: **240 of 240** `shots.md` beat prompts carry a `no X`
clause as authored (the house tail `No photorealism, no 3D render look. 9:16
vertical, no text.`), but `sd_prompt.compress()` lifts them into the negative —
**17 of 240 survive into the sent positive**, and 11 of those 17 are ordinary
prose adverbials ("without lifting her eyes", "without hesitation"). Same for
`wave-drafts.yaml`: 15 of 15 authored, 1 of 15 survives.

## The mechanism, stated per pipeline

**LTX — the negative is never read.** `pipeline/ltx_i2v.py:1001-1008` records it
and `pipeline/jobs/ep1-b13-217f-vo-length-run.yaml:61-70` verifies it at source
in the box's own diffusers 0.39.0: `do_classifier_free_guidance =
(guidance_scale > 1.0) or (audio_guidance_scale > 1.0)`, audio defaults to the
video scale, we send 1.0. So the positive is the only channel, and a `no X`
clause in it delivers `X`.

**Someone did know, and drew the wrong conclusion from it.** The b13 spec moves
its figure/tree ban into the positive on purpose and says why:

> "This is why `no tree` is written into the POSITIVE tail as a description of
> an empty landscape: **a negation there at least contributes no forbidden
> noun**, whereas a negative term contributes nothing whatsoever."

The premise in bold is the bug. A negation in the positive contributes exactly
the forbidden noun.

**SDXL — different, and mostly already handled.** `sd_prompt._NEGATION`
(`pipeline/sd_prompt.py:89`) pulls `no <noun>` out of the positive and
`beat_negative()` appends it to the negative, which on this path binds (verified
on beat 03: restoring `text` to the negative killed the gibberish glyphs 4/4).
The SDXL hits below are the cases that escape that lift, plus one deliberate
exception.

---

## CLASS (a) — negation clauses in a positive prompt

### (a) LTX path — actively harmful, injects the forbidden noun

Every one of the 26 hits carries the same two house fences. Listed by beat with
the current repo home; `ep1` = node `001-capability-inventory`, `ep2` = node
`002b-first-citizen`.

| beat | ep | pipeline | offending text (quoted from the positive) | also class (b)? |
|---|---|---|---|---|
| 02 | ep1 | LTX | `the camera never moves and the frame never changes` | — |
| 03 | ep1 | LTX | `Subject already in frame: no human, no person, no man, no woman, no boy, no girl, no hand, no face` · `no zoom, no push-in, no camera rise` · `the frame never changes` | — |
| 04 | ep1 | LTX | `no zoom, no push-in, no camera rise` · `no second person, no crowd, no face` · (`ep1-b04-385f-hands-still.yaml`) `the hands stay completely still and do not move` | — |
| 06 | ep1 | LTX | `no ground, no horizon, no buildings, nothing but sky` · `no zoom, no push-in, no camera rise` · full figure ban | **yes** |
| 07 | ep1 | LTX | full figure ban + `no buildings` · `no push-in, no camera rise, no pan, no cut` · `nothing in it changes` · `without ever stopping` · `the camera never moves` | **yes** |
| 08 | ep1 | LTX | full figure ban · `no zoom, no push-in, no camera rise` | — |
| 10 | ep1 | LTX | full figure ban · `no zoom, no push-in, no camera rise` · `the camera never moves` · (`ep1-b10-stillwording-0811.yaml`) `there is no wind, no breeze, no gust, nothing is blowing` and `does not bend, lean, tilt, sway, nod, bob or wobble at any point` | **yes** |
| 11 | ep1 | LTX | `no growing, no unfurling, no new leaf` · `no zoom, no push-in, no camera rise` · full figure ban | — |
| 13 | ep1 | LTX | full figure ban · `no tree, no plant, no building` · `no zoom, no push-in, no camera rise` · `waves that never stop` | — |
| 14 | ep1 | LTX | full figure ban (r2/r3); r1 `no humans` | **yes** (r1, resolved) |

The figure ban is one string, repeated verbatim on beats 03, 06, 07, 08, 10, 11,
13, 14: `Subject already in frame: no human, no person, no man, no woman, no
boy, no girl, no hand, no face`. The framing fence is a second: `framing locked,
no zoom, no push-in, no camera rise`. **Two strings account for most of the 26.**

### (a) SDXL path — separate and milder; the negative binds here

7 of 71 distinct sent SDXL positives, and they split three ways.

| beat | ep | offending text | reading |
|---|---|---|---|
| 06 | ep1 | `no humans, tall grass, grass, sky, …` (head of positive, r5–r8) | **DELIBERATE AND MEASURED — not a defect.** The sidecars document it: `no humans` is restored to the head of the positive *and every person noun is deleted from the negative*. That took the beat from a girl in 2/4 (r3) and 3/4 (r4) to **zero in 4/4** (r5), held through r6–r8d. Traps 7 and 8 refuse the run if either half slips. Leave it alone. |
| 01 | ep2 | `its sturdy curved stem no taller than the grass around it` (`002b/shots.md` beat 01) | **A LIVE FAULT, already diagnosed and still in canon.** `_NEGATION` captures at most 25 characters before a comma; this clause is 31, so it is **not** lifted and the model read "taller than the grass around it". See class (b). |
| 08 | ep2 | `Deadpan two-shot, no movement but the pointing arm` (`002b/shots.md` beat 08, also `wave-drafts.yaml` beat 8) | survives the lift; injects "movement". No recorded complaint against it. |
| 07 | ep1 | `dead calm air, nothing moving` | survives; injects "moving". No recorded complaint. |

The remaining 3 are the beat-06 `no humans` string in its other arm wordings.

Of the 17 `shots.md` clauses that survive `compress()`, the six that name a thing
or a behaviour rather than a manner are: `002b` b01 `no taller than the grass
around it`; `002b` b08 `no movement but the pointing arm`; `005` b13 `nothing
else moves`; `007a` b23 `does NOT walk under it`; `007a` b29 `nothing moving but
the light`; `007b` b10 `nothing rendering beside it at all`. The last four are on
**unapproved nodes with no footage**, so they are latent, not live.

### (a) Legacy video — archive only, no action

44 of 77. Every one is a pre-LTX clip (Veo 3.1 / wan / AnimateDiff / ti2v5b /
pixverse / hailuo) rendered from the *uncompressed* prose shot list, so the
house tail went out verbatim: `No photorealism, no 3D render look, no heavy
texture, no text`. They live under `clips/footage-archive/`,
`clips/archive-t2v-realistic/` and `pipeline/t3-trials/outputs/`. These are v1
evidence, nothing re-renders on them, and `compress()` now strips the tail
before it can happen again. Recorded for completeness; not a finding.

---

## CLASS (b) — positive wording that commands a recorded defect

Each row needs a named complaint. Five qualify.

| beat | ep | pipeline | offending positive text | the recorded complaint it matches |
|---|---|---|---|---|
| **10** | ep1 | LTX | `the tall grass around it sways in a light breeze` and `its two small leaves tremble very slightly` — **still present in the live `pipeline/jobs/ep1-b10-guidance20-0811.yaml`** | Founder, 2026-08-11: *"for beat 10 in both of the clips the saplings are wobbling too much"* (`taste/steward-model.ledger.yaml`, `what_he_said_verbatim` + the `beat_10:` block). The already-known instance. |
| **10** | ep1 | LTX | `pipeline/jobs/ep1-b10-stillwording-0811.yaml`: `there is no wind, no breeze, no gust, nothing is blowing` and `does not bend, lean, tilt, sway, nod, bob or wobble at any point` | Same complaint. **This is the anti-wobble job, and the words `sway` and `wobble` are inside its positive prompt, along with wind, breeze and gust.** The only channel the sampler reads now contains every noun the beat is trying to remove. Owner's call, but this is the sharpest instance in the repo. |
| **10** | ep1 | LTX | `no camera rise` in the positive of r1/r2 | Ledger record `ep1-b10-v34-motion-r2-sample` (2026-08-10) — apex climb of **181 px, 14.1% of frame height**, identical in r1 and r2. The record names the cause itself: r1's *"only framing instruction was the negation `no camera rise`"*. |
| **07** | ep1 | LTX | `Subject already in frame: no human, no person, no man, no woman, no boy, no girl, no hand, no face` (+ `no buildings`) | Founder, 2026-08-11: *"for beat 07, the control has some people in the background which we dont want"*. The forbidden noun and the complained-of defect are the same word, in the only channel read. |
| **06** | ep1 | LTX | `pipeline/jobs/ep1-b06-121f-motion.yaml`: `no ground, no horizon, no buildings, nothing but sky` | Founder, 2026-08-10, recorded verbatim in the b06 r6/r7/r8 sidecars as `founder_direction_verbatim`: *"…right now its showing the ground as some flat place, or showing cities for some reason"*. The positive supplies `ground`, `horizon` and `buildings`. |
| **01** | ep2 | **SDXL** | `002b/shots.md` beat 01: `its sturdy curved stem no taller than the grass around it` | Founder: *"its tooooo tall"*. Diagnosed in the b01 r7 ledger record: the clause is 31 chars, `_NEGATION` caps at 25, so it was **not** lifted; the sent negative was byte-identical to r6's, so the positive was the only thing that moved, and stem height went from ~20% of frame (r6, same seed) to **39%** — taller than the 32% plate he revoked. Listed separately because SDXL's negative *does* bind: the fault here is the failed lift, not an inert negative. |

**Resolved precedent, listed because it is the same shape:** beat 14 r1's
positive said `the slender sapling sways gently in a steady breeze, its thin
stem bending and springing back`. Ledger `ep1-b14-v34-motion-sample`: *"the
sapling bends monotonically from frame 40 and is near-horizontal and leaving
frame by 64"*, cause *"the prompt, not the model … LTX honoured `bending` and
never `springing back`"*. Fixed in r2/r3 by replacing the directional verbs with
ambient ones. That fix is the template for the rows above.

**Deliberately NOT flagged:** beat 08's positive says `the broad leaves sway
gently`, the same word as beat 10 — but the founder's 2026-08-11 verdict on beat
08 is *"beat 8 looks good"*. No complaint, no flag.

---

## CLEAN

**LTX — 12 of 38 distinct positives carry no negation clause:** ep1 beat 01 (the
keyboard, all three wordings incl. the `SAMPLE-ltx23-b01` recipe); ep2 002b
beats 01 (fig swell), 12, 15, 16 (both the drift control and treatment), 18, 21.
Every clean LTX prompt is either beat 01 or an ep2 002b provisional — **the
entire ep1 motion set from beat 02 to beat 14 is affected.**

**SDXL — 64 of 71 distinct sent positives are clean**, and 223 of 240 authored
`shots.md` beat prompts reach the model clean because `compress()` lifts their
fences correctly. All 15 `wave-drafts.yaml` goblin drafts are clean after the
lift except beat 8. Node 001 beats 01, 03, 10 and 14 were spot-checked
end-to-end: the authored `no X` terms land in the negative and nothing survives
in the positive. The ep2 goblin wave (24 job specs, 220 stills sidecars) is
clean apart from beat 08's one clause.

**Deterministic hold-still clips — 6 of 6 clean**, trivially: no model runs.

## Repo text vs rendered sidecar

Matched by `task:` id: **63 sidecars agree with their job spec byte-for-byte, 2
disagree** — and in both the sidecar is the *better* text.

| task | job spec | sidecar |
|---|---|---|
| `ep1-b04-v34-motion-r2-0810` | `pipeline/jobs/ep1-b04-v34-motion-r2.yaml` — `everything holds its position, framing locked, no zoom, no push-in, no camera rise` | `review/v34-motion/04-the-fall-LTX-r2.mp4.meta.yaml` — that whole block replaced by affirmative anchors: `the camera is locked on a tripod and stays perfectly still, the hands stay resting flat on the papers in the same spot the whole time, … the composition is identical in every frame` |
| `ep1-b07-v34-motion-r2-0810` | `pipeline/jobs/ep1-b07-v34-motion-r2.yaml` — same negation block | `review/v34-motion/07-zero-0-moving-parts-LTX-r2.mp4.meta.yaml` — `a locked-off tripod shot: the camera never moves, the horizon line stays at the same height in the frame, … the composition is identical in every frame` |

**The two job files on disk are behind the recipe that actually rendered.**
Anyone re-firing `ep1-b04-v34-motion-r2` or `ep1-b07-v34-motion-r2` from the
repo would re-introduce a negation block those renders had already dropped. The
figure ban survives in both sidecars, so that half is not affected.

Five job specs have no sidecar at all — `ep1-b02-121f-vo-length-run`,
`ep1-b06-121f-motion`, `ep1-b11-129f-vo-length-run`, `ep1-b13-217f-vo-length-run`,
`ep1-b10-stillwording-0811` — meaning unrendered, or rendered on the box and not
yet couriered back. Their repo text is all there is.

## Scale

The pattern is **not** two beats. On the LTX path it is 26 of 38 distinct
positives, covering every ep1 beat from 02 to 14, and it reduces to **two shared
strings** — the figure ban and the framing fence — plus a handful of per-beat
clauses. The two that already had a founder complaint attached (03 and 10) were
found first because someone was looking at those beats, not because they were
unusual.

Nothing here is a recommendation beyond: each of these needs its owner to look.
Lanes are live on beats 03, 07, 10 and 14.
