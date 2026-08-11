# Episode 1 → canon: the remaining-work list

**Written 2026-08-11 by the ep1-to-canon lane. Read-only audit; nothing here was
rendered, promoted or published.**

Roman, 2026-08-11: *"lets not waste time, keep the iteration going and finish
episode 1, then move on to episode 2."* His definition of finished, 2026-08-10,
recorded as [D21](DECISIONS.md#d21--finished-has-a-definition-now-and-it-is-the-founders-resolved--roman-2026-08-10):

> finished means that the episode 1 video has been polished. promoted to canon,
> and ready to be published.

Three gates, three different kinds of thing: **polished** is taste (R4, his),
**promoted to canon** is mechanical (lint-enforced; the *word* is his, the typing
is not), **ready to be published** is licence + provenance clearance. This
document is the list of what stands in each.

**The cut this is measured against** is
`review/tonight/EP1-PROVISIONAL-v36b-bench.mp4` — 91.09s, 15 beats, no slates,
built by the `recut-1400` lane and still being written while this was read (the
manifest changed under this audit once, at 89.67s → 91.09s, when the sapling
insert landed). It is a **bench cut: no leaf, not canon**. Re-measure before
acting on any row.

---

## The 15 beats

`slot` is `render_t3.fit_duration` = `max(min(cdur, vdur+2.0), vdur+0.4)` for a
voiced beat. A clip shorter than `vdur+0.4` **loops** — a palindrome, not a
jump-cut (loop cycle 005 fixed the seam), but still the thing he named:
*"i'd rather not have any looping, it looks bad."*

| # | clip in the cut | cdur | vdur | slot | fit | judged? | what remains |
|---|---|---|---|---|---|---|---|
| 01 | `01-the-keyboard.mp4` (Wan2.2-5B) | 2.54 | — | 2.54 | silent, ok | still never refused; **motion never judged** | needs R4 (or leave — it is not a defect) |
| 02 | `02-three-oh-seven.mp4` (Wan2.2-5B) | 2.54 | 4.45 | 4.85 | **LOOPS 1.91×** | **founder-picked clip** ("face B is the best out of the 2", 2026-08-03) and **he ordered it restored today** | **needs R4** — his own pick loops under its line |
| 03 | `03-deploy-succeeded-LTX-89f.mp4` | 3.71 | 3.13 | 3.71 | covers | still `b03-r4-s3` canon 2026-08-09; **motion never judged** | needs R4 on the motion |
| 04 | `04-the-fall.mp4` (v35 plate twin r4) | 2.71 | — | 2.71 | silent, ok | he praised the zoom-out, refused the content: *"literally his hand repeatedly moving, although the zoom out is great"* (2026-08-10) | a 385f `handsstill` fix (16.04s) is rendered and **unjudged** → needs R4 |
| 05 | `05-fan-spinning-down.mp4` + `05-…-alt1-sapling-reveal.mp4` | 4.21 | — | 4.21 | silent, ok | held still under **"yeah keep em still"**; the 1.42s sapling insert is **new today and unjudged** | needs R4 on the insert only |
| 06 | `06-too-blue.mp4` (held still, 12% push-in) | 4.88 | 4.47 | 4.88 | covers | **frame is his** (`b06-r8d-step3-s0`, 2026-08-10); **motion refused today**: *"beat 6 is not what we're looking for, try the same slow zoom out like with beat 4, no need for animation"* | the zoom-out he asked for **is rendered** (`06-too-blue-ZOOMOUT-121f.mp4`, 5.04s) and **not in the cut** → wire in, then R4 |
| 07 | `07-zero-0-moving-parts.mp4` (v35 plate twin r5-g20) | 2.71 | 6.24 | 6.64 | **LOOPS** | **refused today**: *"the control has some people in the background which we dont want, and the pull-back is nice but the clouds are too low"* | the fix **is rendered** (`…-385f-cloudshigh.mp4`, 16.04s) and **not in the cut** → wire in, then R4 |
| 08 | `08-sev-1-ltx-r2-plate-313f-s20260739.mp4` | 13.04 | 12.51 | 13.04 | covers | **APPROVED today** — *"beat 8 looks good"* | **done** (licence gate only) |
| 09 | `09-whoami.mp4` (held still) | 2.58 | — | 2.58 | silent, ok | still `p09-r1-s2` picked 2026-08-08; held still under **"yeah keep em still"** | **done** (licence gate only) |
| 10 | `10-sense.mp4` (v35 plate twin r2) | 2.71 | 10.12 | 10.52 | **LOOPS** | **refused today**: *"for beat 10 in both of the clips the saplings are wobbling too much"* | the anti-wobble fix **is rendered** (`10-ltx-affirm-265f-s20260897.mp4`, 11.04s) and **not in the cut** → wire in, then R4 |
| 11 | `11-grow-LTX-129f.mp4` | 5.38 | 4.97 | 5.38 | covers | **motion never judged** | needs R4 on the motion |
| 12 | `12-undefined.mp4` (held still) | 2.58 | 1.60 | 2.58 | covers | still `b12-r2-s1` picked 2026-08-08; held still under **"yeah keep em still"** | **done** (licence gate only) |
| 13 | `13-i-always-left-LTX-217f.mp4` | 9.04 | 8.36 | 9.04 | covers | **motion never judged** | needs R4 on the motion |
| 14 | `14-…-ltx-r2f-313f-affirm-s20260898.mp4` | 13.04 | 12.59 | 13.04 | covers | still `b14-r4-s3` canon 2026-08-09; **first motion this beat has ever had**, rendered today, **unjudged** | needs R4 on the motion |
| 15 | `15-something-s-coming.mp4` (held still) | 2.58 | 1.37 | 2.58 | covers | still `b15-r3-s1` picked 2026-08-08; held still under **"yeah keep em still"** | **done** (licence gate only) |

**Counts: 4 done (08, 09, 12, 15) · 3 need mechanical work first (06, 07, 10 —
the clip that answers his note exists and is not wired in) · 8 need R4
(01, 02, 03, 04, 05-insert, 11, 13, 14).**

**Three beats loop: 02, 07, 10.** Two of those three (07, 10) stop looping the
moment the already-rendered clip is wired in. Beat 02 does not — see below.

### Beat 02 is the one genuinely stuck beat

He restored it himself today and the restored clip loops. The two clips were
never the same shot at two lengths: the Wan clip he picked holds one framing for
all 61 frames; the LTX 121f replacement cut to a different shot at ~frame 40 and
threw away the face he chose it for. So the loop cannot be fixed by putting the
LTX clip back. Fixing it needs either his tolerance for the loop or a new render
of *his* framing at ≥117 frames.

### Nothing in the cut is a slate

`slate_beats: []`. All 15 beats are real footage or a held still. The held
stills are 05, 06, 09, 12, 15 — four of them (05, 09, 12, 15) are held under his
explicit **"yeah keep em still"** ruling; **06 is not covered by that ruling**
and is the one held still he has not blessed as a hold.

---

## The non-beat blockers

### 1. Canon promotion mechanics — what the operation actually is

Short version: **it is one command, it takes minutes, and the only thing it is
waiting on is his word plus the licence answer.**

- A bench cut is a bench cut *because of the `--out` flag*. `render_t3.py:1264`
  returns before writing anything: `return 0  # bench render — no leaf, no lineage`.
- **Drop `--out` and the same tool promotes**: it writes
  `genomes/sapling/nodes/001-capability-inventory/leaves/001-t3-e.yaml` and
  `001-t3-e.mp4` (next letter — `a` through `d` exist) and registers the leaf in
  `lineage.yaml`. The command is
  `python3 pipeline/render_t3.py sapling 001 --clips <dir>`.
- The leaf yaml it writes carries `leaf, node, tier, form, content, author,
  model, prompt, seed, cost_usd, status: live, platform_urls, sources` — matching
  `001-t3-d.yaml`. Per-beat provenance rides in `sources:`, which is already
  complete for all 15 beats.
- **The §6 gate is already satisfied.** `render_t3.py:919-928` refuses any
  unapproved node through `render_local.approved()` — *"bench cuts included — a
  cut IS media"* — and node 001 passes it today, which is how these bench cuts
  are being made at all. The sapling-reveal insert did **not** change `node.md`
  (the ledger's own words: `what_changed_in_the_script: NOTHING`), so approval is
  intact and no re-read of the script is mechanically required.
- `lint_genome.py` exits **0** right now. Promotion does not fail it on structure.

**So nothing structural blocks promotion.** What blocks it is the next item.

### 2. The licence gate — the single biggest thing between here and published

`lint_genome.py` exits **0** today: *"tree healthy — 1 genome(s) linted, 0
violations"*, with 483 warnings and **25 pre-existing licence violations on a
ratchet of 25 — a NEW one fails CI.**

That ratchet is the trap. **11 of the 15 beats in the current cut are
`publishable: false`**, and promoting them into a canon leaf is what turns them
from "a bench cut nobody published" into a new licence violation that fails CI.

- **9 clips blocked by D16** (LTX-2 Community Licence): beats 03, 04, 06*, 07,
  08, 10, 11, 13, 14.
- **4 blocked by D15** (CreativeML Open RAIL++-M, via the still each hold is cut
  from): beats 06 (`06-too-blue-r8d-step3-s0.png`), 09
  (`09-whoami-prog-s2.png`), 12 (`12-undefined-r2-s1.png`), 15
  (`15-something-s-coming-r3-s1.png`), plus the new beat-05 sapling insert
  (cut from `12-undefined-r2-s1.png`).
- **Publishable today: beats 01, 02 and 05's fan clip** — all Wan2.2-TI2V-5B
  under Apache-2.0 — and every VO mp3.

This is the distinction that matters: the gate blocks **publication**. Whether it
also blocks **canon promotion** turns on the CI ratchet, not on the gate itself —
a canon leaf carrying a new non-shippable ingredient is a new violation.

### 3. D15 and D16 — both OPEN, both his, and they block different artefacts

**D15 — "every approved still is OpenRAIL++, and the gate was clearing it
(OPEN — founder's)".** `animagine-xl-3.1` is CreativeML Open RAIL++-M, its use
restrictions travel to the output, and this tree offers reusers CC BY 4.0. On
2026-08-03 he said *"put the images from my computer onto there please, not like
theres any reason to hide it"* — and D15 records exactly how far that goes:

> "There is no reason to hide it" is a statement about secrecy, not about what we
> warrant to a stranger who downloads a frame.

The carve-out built on it is narrow by design: it clears **stills in
`cuts/review-assets/`, with a `published_under:` line, from the one model he
authorised** — and D15 says in the same breath that **"D16's LTX clips stay
withheld"**. An *episode* is none of those things, so the carve-out does not
reach this cut.

*Blocks:* the four held-still beats' source frames — 06
(`06-too-blue-r8d-step3-s0.png`), 09 (`09-whoami-prog-s2.png`), 12
(`12-undefined-r2-s1.png`), 15 (`15-something-s-coming-r3-s1.png`) — and through
12's frame, the new beat-05 sapling insert.

*The open question, verbatim:* whether the tree **"narrows its offer generally…,
re-draws the fifteen approved stills on a model whose grant we can pass on, or
reasons that the restrictions do not conflict in our case."** Three ways out, all
R4, and no precondition on anyone else.

**D16 — "LTX-2/2.3 is a CANDIDATE under watch-only… (OPEN — founder call)".**
The heading records that gate (c) *"FIRED TWICE on 2026-08-06 — suspended, then
SCREENED AND CLEARED ON LOOK; still OPEN because adoption now waits on
integration work that is not done"*, and that **"the licence analysis is
unchanged throughout"**.

*Blocks:* the nine LTX clips in the cut — beats 03, 04, 07, 08, 10, 11, 13, 14
(and the beat-06 zoom-out candidate).

*The open question* is the one already on the checklist as **item 20 — "LTX clips
on the site — one yes or no"**, `state: open`, and item 24 states the consequence
plainly: *"Nothing on this card can be shown here and that is the licence gate
working, not a missing render… Item 20 is the only thing between them and this
page."*

> **One caveat on D16, flagged rather than acted on.** Its "why this is still
> open" section is dated 2026-08-06 and says *"LTX is not wired into anything"*
> and that `video_task.py` has no LTX queue path. The **licence** half is current;
> the **adoption** half has been overtaken by events — nine of the fifteen beats in
> today's cut are LTX renders produced on the box. Worth a correction in
> `DECISIONS.md`, which is not this lane's to write.

### 4. The VO — no take is marked provisional, and none is marked final either

All 11 voiced beats (02, 03, 06, 07, 08, 10, 11, 12, 13, 14, 15) carry a
measured `chatterbox-0.5B` manifest with `lines[].chunks` and a `total_s`
`render_t3` sizes the slot from. Beats 01, 04, 05 and 09 are silent by script.

**Not one manifest carries a `provisional`, `draft`, `approved` or `status`
key** — so the honest answer is that the VO is *unmarked*, not that it is final.
The only note on any of them is beat 03's, and it is deliberate: *"cut mid-word:
the line is interrupted by his death, not finished."* If "polished" is to include
the voice, that is a question he has to be asked; nothing on disk answers it.

### 5. Provenance — no gaps

Checked with the real `licence_gate.sidecar_for()` (`pipeline/licence_gate.py:1128`),
not a glob. **All 16 clips and all 11 VO mp3s in the cut resolve a sidecar: zero
gaps.** The clips resolve `<name>.mp4.meta.yaml`; the VO resolves through the
third shape, `NN-vo.json` beside `NN-vo.mp3`, which is why a naive
`*.mp3.meta.yaml` glob reports 11 false misses here. Every sidecar parses and
carries `platform`, `model` and `cost_usd`; the held stills additionally carry
`source_still`, `source_still_sha256` and `still_model_licence`.

---

## What Roman must answer (shortest first)

1. **Item 20 — LTX clips on the site: yes or no?** One word. It unblocks 9 of 15
   beats and is the only thing between the cut and any page.
2. **Beat 02 loops 1.91× under its line. Keep the loop, or re-render your framing longer?**
3. **Beat 05's new 1.42s sapling reveal at 0:22 — keep it?** (It is beat 12's
   picture shown twice; the draft leaf `leaves/drafts/001-t0-e-draft.yaml` is
   written for your read.)
4. **Beats 06, 07, 10: the clip that answers your note is rendered — yes or no on each?**
5. **Beats 03, 11, 13, 14 have never had a motion verdict. Yes or no on each?**
6. **Beat 04's `handsstill` fix — yes or no?**
7. **Beat 01's motion has never been judged. Yes or no?**
8. **Is episode 1 polished?** (D21 gate 1 — only you can close it.)
9. **The word to promote to canon.** (D21 gate 2 — founder-reserved.)

## What runs without him (dependency order)

1. **Wire the three answered clips into a fresh bench cut** —
   `06-too-blue-ZOOMOUT-121f.mp4`, `07-…-385f-cloudshigh.mp4`,
   `10-ltx-affirm-265f-s20260897.mp4` are all on disk in `review/tonight/` and
   all cover their slots. This kills the loops on 07 and 10 and puts his three
   named faults in front of him in one pass. Runnable now, no gate:
   `python3 pipeline/render_t3.py sapling 001 --clips <dir> --out review/tonight/EP1-PROVISIONAL-v37-bench.mp4`
2. **Batch the unjudged beats into one screening pass** rather than asking him
   nine times — 01, 03, 04, 05-insert, 11, 13, 14 plus the three above.
3. **Nothing else.** Canon promotion, publication and every taste verdict are
   founder-reserved, and the licence gate is his call, not a code change.

---

## Sources that were stale, and were verified per beat instead

Four, all of which would have sent a lane the wrong way:

1. **`cuts/cuts.yaml` checklist item 10** — *"Beat 6 — both your options are
   drawn… Pick one"*, `state: open`. He made that pick on 2026-08-10 (~19:58):
   *"this one is good enough lets not overthink it, use that."*
2. **`pipeline/pending-founder.yaml`, `ep1-frame-picks`** — *"One is left —
   scene 6."* Same stale fact.
3. **The v36/v36b beat-06 sidecar banner** — line 2 reads *"the frame under this
   clip is a STEWARD PICK the founder has not seen"* while the same file at line
   40 carries `founder_verdict: approved_as_the_beat_6_frame`,
   `founder_verdict_date: 2026-08-10`. The banner is stale boilerplate; the body
   is right.
4. **`shots.md`'s beat-06 section** ends at round 5's provisional pick and never
   records the r8d pick that superseded it. Its wave summary (~line 1041) was
   already corrected on 2026-08-11 and that correction holds.

The authoritative sources, confirmed: **each beat's own section plus `stills/` on
disk** for frames, **`taste/steward-model.ledger.yaml`** for today's verdicts
(entries `ep1-motion-founder-verdicts-0811` and `ep1-b02-121f-founder-reject-0811`),
and **the cut's own `.meta.yaml` `ingredients:` list** for what is actually in it.
