# Handover — 2026-08-20, written at the close of the 08-19 night

Written by the night-close lane at the end of 2026-08-19. Everything below is on
disk and pushed. Read `HANDOVER-0819.md` for the shift immediately before this one
and `STATE.md` for the running log.

**178 commits landed on 08-19 across seven lanes.** This file is not a list of them.
It is the four things a person needs at 09:00: what is waiting on the founder, what
we now know that we did not know yesterday, what will bite you, and what state the
episode is actually in.

**Two things in the older records are now wrong and will mislead you.** `HANDOVER-0819.md`
§1 says the founder's one open question is the cold open — superseded; he watched
`ep2-demo-0819c` during the day and bounced on other things. And `work-ladder-0819.md`
names the cut's slates as 07/09/15/19 — the live cut's slates are **09, 15 and 16**.

---

## 1. Waiting on the founder

**One question is the key, and it is one letter.** The rest of the table is behind it or
is not taste at all.

| | What | Where | What it unblocks |
|---|---|---|---|
| **1. THE KEY** | **The goblin letter — "Which one is the goblin?"** Answer **A** (the picked card, the round young one) · **B** (the adult) · or **name a third**. | **`https://banyan.city/review/ep2-goblin-design-0819`** — the trace link. Three pictures plus `the-split-0819c.jpg`, all nine goblin beats one frame each. | **Every goblin-identity render in the project.** If A: beats 07/14/17/19 re-render. If B: 03/04/08/13/20 re-render. Also releases beat 20's re-roll, which is now known to be a **one-job** fix. |
| 2 | **The guards look** — do they read as grown men, and does it matter? **Recast / Accept / Stage around it.** Plus a smaller second question: may the goblin read as a plain green man? | `https://banyan.city/review/ep2-guards-0818` | Beats 05, 06, 10, 11 (all `best-available`) and beat 09's plate. |
| 3 | **D23, the automation charter — his signature.** Reply "D23 approved"; partial is a complete answer ("D23 approved except 2"). **Silence is explicitly not acceptance here.** | `DECISIONS.md` line 1532 | Nothing renders on it; it is governance, which is why it cannot be taken steward-side. |
| 4 | **Beat 17's restaged script line has never been read by him.** One line: *"The scavenger pushes himself up, gives his cloak a shake, and turns to go."* | `genomes/sapling/nodes/002b-first-citizen/leaves/002b-t0-c.yaml` — `approval_status` says so in terms | §6. His 08-19 "all approved" covered beats 12, 13, 15, 19, 20 **only**. Beat 17 is meanwhile PASS and shipping in the review cut. |

**Sequencing matters between 1 and 2.** The guards page illustrates the goblin with
`b14-seeds.jpg`, captioned "the current adult goblin" — which is the very adult the
goblin letter says nobody authorised. Ask 1 first; the green-man half of 2 is downstream
of it.

**Why the goblin letter exists, in one paragraph,** because whoever hands it over should
be able to say it: he watched 0819c and asked *"some scenes including the goblin has him
as an adult??"* Nine beats show two different characters and the split falls exactly on
the render date — round/young on everything rendered on or before 08-16, lean adult on
08-18/19. The trace concludes **nobody authorised the adult.** It entered through a
steward-model ledger entry on 08-13, was rewritten as `a lean wiry adult goblin man` in
`91a35fe1`, his own approved reference set was blacklisted under `not_these:` with the
comment `~4 heads, oversized cranium, toddler stance`, and the string then propagated to
~14 sites in `plate_scratch.py`. The steward's own read is on the page: **"I think A is
the answer."**

**Veto window open, not a question:** beat 11 `r1s1` sits under "Picks — veto only" on the
board; silence accepts.

**Taken steward-side and deliberately not on his board** (the 08-18 widening: routes,
bars, tradeoffs and defect rates are ours; he gets taste, ~1 at a time, with pixels) —
beat 08's pointing arm, beat 14 re-stage, beat 17's brush route, beat 21's leaves and
background object, matte-vs-gloss on the fig, and beat 16's slate-or-ship. Each has a
written verdict; each is one line to veto.

**Spend: $0.** Nothing metered today on any lane, and nothing is queued that would be.

---

## 2. Laws proven on 08-19

Seven. Where a later result narrowed one, the narrowing is in the same section rather
than buried in a correction further down.

### The (seed × plate) interaction — no factor is guilty alone

Beat 12's plate on seed 20260819 loses **91.05 levels** of luma over 121 frames. Same
plate, same prompt, same 42-token argv, seed 20260871: **−0.04**. One integer of seed
between them. And 20260819 is innocent elsewhere — it holds on b01 at **+16.59** and on
b18 at **−4.28**. `--image-crf 10` was exonerated across four clips with opposite
outcomes; every other sampler flag is identical across all six specs. **The cause is the
pair, not any member of it.**

The recorded reasoning error is worth more than the finding: eliminating four candidates
one at a time is sound *only if a single cause exists*, and every branch of every bar
written that night assumed one. Both "more likely" predictions on this axis were wrong in
the same way.

Consequence: **a collapse on this plate is fixable by a re-roll** — which is why beat 20's
darkening is a one-job fix, and why that job is frozen rather than doubted (§5).
`pipeline/loop/darkening-crf-diagnostic-0819.md`

### Camera lock is not promptable on this recipe — it is a per-seed lottery

`ep2-b12-stillmotion-s20260818-0819` tilted **−387px**, 30% of frame height, dx = 0 on
every frame, monotone, all six blocks of a 3×2 grid agreeing inside 1px. The ban was in
**both** places: the positive opens *"Static locked framing, the frame never moves and
nothing enters it"*, and the negative's first six tokens are *"camera pan, camera tilt,
zoom, dolly, push in, pull back."* It tilted anyway, on a seed with form on beat 01 twice.
**Framing is a per-render check — never inherited from a passing sibling, never argued
from the prompt.**

Three lanes had measured camera lock three different ways ad hoc, so the instrument is now
committed beside the artifacts:
`farm-out/ep2-b12-stillmotion-s20260818-0819/b12_camera_drift.py` — phase correlation, 3×2
block consistency, and luma on the **overlap region** so a fade cannot hide behind a pan
and a pan cannot forge a fade. Its own limit is in its docstring and it fired tonight: a
hard fade or content substitution destroys the correlation peak, so **block numbers on a
collapsing clip are noise and must not be quoted as a camera move** (s20260873 reads
+133px per block against a whole-frame +0px; the whole-frame number and the eye are right).

**Narrowed the same night:** "lottery" survives for *camera*. It does **not** survive for
the intruder — §3.

### `--frames` is not a trim, and five other lanes were relying on it

`ep2-b12-shortstill-0819`: one variable off its parent, `--frames 121 → 73`, everything
else identical. The premise was that 73 frames "would never render the part of the ramp
that collapsed." **False.** Frame count is an input to the denoiser's temporal grid, so a
shorter rung is a **full re-roll, not a prefix.** Same plate (f000 125.47 on both) and
then completely different clips — at f024 the parent reads 125.33 and the rung 108.84; the
parent is flat to f048 then falls off a cliff, the rung falls for 42 frames then sits still.

**Invalidates** any rung shaped as "shorten it so it does not reach the part that broke",
and any attempt to inherit a longer rung's early frames as evidence. Filed at ladder level
because b01, b07, b14, b17, b18 and b19 are all running LTX rungs.
`pipeline/jobs/ep2-b12-shortstill-0819.yaml` → `verdict_this_job_measured.THE_PREMISE_WAS_WRONG`

### The pitch attractor at ~110 Hz — a reference number predicts nothing

Chatterbox pulls every rendered take toward **~110 Hz**, which is exactly where the
SAPLING/tree voice sits. Deep refs do not stay deep: `am_onyx` at −6st went in at a
**63.7 Hz** reference and came back out at **110.1 Hz**. The engine also does not preserve
ref timbre (`am_michael` in at centroid 2183, out at 1325). So **pitch is the only
separator that survives cloning, and it must be measured on the rendered take** — never
predicted from the reference. The only safe direction is up.

What it caught: GUARD 2 measured **1.7 Hz** from the tree — the only confusable pair in the
cut — and GUARD 1 was a loaded gun at **1.1 Hz of reference separation**, passing only
because MPS non-determinism happened to push him +14 Hz. After the re-voice: SAPLING 109.6,
GUARD 2 **135.6** (26.0 Hz clear, was 1.7), SCAVENGER 167.8, GUARD 1 **192.0** (82.4 clear,
was 22.8 by luck). Worst pair in the episode is now 24.2 Hz.
`genomes/sapling/nodes/002b-first-citizen/clips/guards-revoice-0819.yaml`

### Scribble nets read enclosure and nothing else

Beat 08's route, rung 5 (`ep2-b08-cnetplate-r5-0819`), on
`xinsir/controlnet-scribble-sdxl-1.0`. A **closed contour** is read as an object boundary
and traced; an **open medial-axis skeleton** means nothing to it, so it drew the skeleton
as literal glowing lines in the picture — guard spine column luma **212.3 vs 165.4**
surround, goblin **218.2 vs 186.0**. Non-enclosure proved independently by flood fill: the
contour traps the fill (18007 px / 11247 px), the skeleton leaks to the frame border on both.

Counter-intuitive and measured: **stroke weight is a precision dial, not a strength dial.**
7px vs 3px at the same scale traced **94.4% vs 98.3%** — thinner binds *tighter* (nocontrol
floor 26.1%).

**Rules out** hand-authored geometry as a composition lever for beat 08 on this net, and
retires the scale and stroke sweeps. Reported against itself: averaged over *all* ink the
enrichment is only 1.4–1.7×, indistinguishable from the floor — the effect is local to
strokes landing inside a figure.
`pipeline/b08-arm-route-0819.md` §10

### Masked IP-Adapter reached identity where grammar and geometry could not — then a bare pose net beat it

After five contour rungs and every wording variant had failed the same clause,
`ep2-b08-ipamask-0819` split the two figures' identities **on the first sample**, using two
masked IP-Adapter references and changing nothing else — same hint bytes, same seed, same
prompt word for word *including* the `green skin` that had been broadcasting to both heads.

| frame | guard G−R | goblin G−R | separation |
|---|---|---|---|
| rung 2 (no adapter) | +34.0 | +29.4 | **−4.6** |
| rung A (masked refs) | **−14.5** | +28.5 | **+43.0** |

Why grammar could not do it: a contour "cannot say which body an attribute belongs to."
Why geometry could not: identity was never a conditioning problem, so no value of scale or
stroke could reach it.

**Carry the caveat.** Later the same day the bare **pose** net beat it with no adapter at
all — rung B guard **−27.5 / +55.5**, rung B2 **−32.6 / +83.0**. Five contour frames, five
failures; two skeleton frames, two passes. The masked references are *possibly redundant,
not proven so.* Also unstable: `plump` broadcast onto the GUARD in one frame and the GOBLIN
in a frame differing only by an elbow — **no single frame's attribute assignment is
evidence about wording.**
`pipeline/b08-arm-route-0819.md` §11, undercut in §13–14

### The palindrome fix — a third of the episode was playing backwards

`render_t3.render_beat` filled any slot that outran its clip by playing the footage
**forward then reversed**, and printed nothing while doing it. It was firing silently on
**8 of 18 footage beats** — 1, 3, 4, 6, 10, 11, 17, 18. Beat 06's board went up-down-up.
Beat 01's fig ripened purple and then un-ripened, **under a verdict that had passed the
source for "growth monotone, 0 shrinks" — true of the file, false of the cut.**

Default fill for footage is now a last-frame **hold** (`tpad=stop_mode=clone`, padded 0.2 s
past the slot so `-stream_loop` cannot wrap to frame 1). Bench rebuild, moving frame-pairs
inside the fill window, old → new: b01 103/104 → **0/104**, b06 105/113 → **0/113**, b18
137/140 → **0/140**. The palindrome survives only as opt-in `loop_fill: pingpong`, which
nothing in this tree writes.

Beat 19 — a fig *falling* — was protected only by **0.09 s of luck**. Reversed, it shows a
fig flying back up onto the stem. Committed `af863c0b`; **not applied to any cut** (§5).

---

## 3. Tonight's judging — beat 12's seed axis closes 0 for 5, and the cause is a phrase

Seeds 4 and 5 landed and both fail, which was the expected close. Judging them properly
turned up something better than a sixth seed.

| seed | camera dy | luma (matched content) | how it fails |
|---|---|---|---|
| 20260819 | +0px | **−91.05** | real dusk fade, plus a bird |
| 20260871 | +7px | −0.04 | locked and flat — **but a bird with a white eye rises and leaves** |
| 20260818 | **−387px** | −1.35 | camera tilt, off the plate into grass |
| **20260872** | −180px, blocks incoherent | −8.20 | **a crouching intruder that never leaves**, + the frame re-composing |
| **20260873** | +0px | **−43.48** | **the sky replaced by a wall of reeds**, + a brief intruder |

All verified against their own `.sha256`, and the init is **byte-identical across all five**
(`c6575d0d…`), which is what licenses reading them as one plate. s20260872 is worth one
extra line because it is the trap in the table: **it PASSES the bar's own decisive number**
(−16.93 raw, −8.20 matched) and is still not footage.

**The close could not be written without re-opening s20260871.** It had been recorded as
"clean on luma, stillness/bird/leaf clauses **unjudged**" — so asserting "every take failed
something" would have been asserting a failure nobody had measured. Run properly it is
**+7px with all six blocks agreeing at 1px, luma −0.04** — genuinely locked and flat — and
then a black bird with a large white eye rises from behind the lower leaf at f030 and is
gone by f090.

### The intruder is not a lottery and not the plate — it is a phrase in the positive

**Four of five takes** put a dark figure behind the lower leaf, in the same slot, on four
independent seeds. The one exception is `20260818`, whose camera had already left the plate
by f008. The plate itself is clean: `b12-init-704x1280.png` is leaves, sun, cloud and sky
with no dark form anywhere. So it is invented at sample time, reliably, by something
identical on every seed. There is one candidate:

> Tight on the sapling's two leaves, perfectly still — **the scavenger crouched behind
> them, out of frame.** Static locked framing, the frame never moves and nothing enters it.

A diffusion positive has **no negation operator and no way to place a named subject outside
the canvas.** "Out of frame" is not renderable. That clause encodes *scavenger, crouched,
behind the leaves* — a subject and a position — and that is what got drawn, four times. The
negative's `goblin, creature, person, face, hands, figure entering frame` fought it on every
one of those renders and lost.

**It also means beat 12's `why: goblin-free beat` was wrong on four of five renders** — a
beat everyone believed was clear of the goblin-identity freeze has been generating off-model
scavenger figures. Nothing was published, so nothing breached, but the freeze is closer to
this beat than the specs say, and whoever holds the design letter should know it.

### The generalisable law: a shot description is not a prompt

**This outranks beat 12 and is the reason to read this section.** My first draft justified
the fix as "deleting text the approved line does not contain." **Checking that before
publishing showed it was wrong** — `node.md:83`, the approved shot description, contains the
clause almost verbatim, and the prompt is a transcription of it.

But the *render* is what violates canon, not the deletion. The same node states the staging
at line 189: *"12 RELATED — he is crouched in the grass behind the leaves and out of frame,
not below them. **Off-screen only; the picture did not change.**"* Canon says the scavenger
must **not** be in the picture; four of five renders put him in it.

So: a script's staging prose describes what is true of the **scene**, including what is
deliberately **off-screen** — normal, useful screenwriting. A diffusion positive can only
describe **what is in the frame.** Transcribing an off-screen clause verbatim asks for
exactly the thing the script says to exclude. **Whoever writes a prompt from a script line:
strip every clause about what the camera does not see.**

**Scoped honestly, because the obvious grep lies.** 315 specs match `out of frame`, and
sampled, the overwhelming majority are **negatives** banning subject exits — `walking out of
frame, leaving the frame` — which is a correct, unrelated use. The defect is an off-screen
clause inside a **positive**, and beat 12 is the only confirmed instance. **The audit that
would settle it has not been run**: it must read positives only, and a whole-file grep
cannot tell the two apart. Named as unowned rather than claimed as measured.

### The next rung, named and costed, deliberately not filed

**`ep2-b12-noscav-0819`** — delete the span `— the scavenger crouched behind them, out of
frame` from `b12-motion-prompt.txt`, seed **20260871** (the one take that is locked and flat
and fails only on the intruder), everything else identical. ~8 min, $0, one sample. Bar: the
intruder clause alone.

**Not R4** — it changes a prompt, not the script, and it moves the output *toward* the
approved staging. What would be R4 is changing the line itself, or widening a framing he
approved as "tight on two leaves."

**Not filed** because the only derivation path, `derive_b12_stillmotion_0819.py`, still leaks
inherited verdict keys (§4), and filing through it at the end of a close would propagate a
third generation of another beat's verdict into a fresh spec. **Hand-write the spec.** This
is the next lane's first job.

No pick, no promotion, no cut swap. Beat 12 keeps `12-related-b12-tightB-untrimmed.mp4`,
`best-available`, colour fault named. **The pick is R4 and no take has earned one.**

---

## 4. Traps

### The one that will silently ship the wrong voices again

`work-ladder-0819.md:1279` says *"render_t3 reads `clips/NN-vo.mp3` and the measured chunk
timings in `clips/NN-vo.json` straight out of the node directory, so the next cut picks these
six takes up automatically — no flag, no copy step."*

**The code disagrees, and I read it rather than trusting either of us.** In
`pipeline/render_t3.py`, `find_audio()` (line 249, called at 1088) and `vo_manifest()` (line
347, called at 1094) both resolve against **`args.clips`** — the same `--clips` directory as
the video — with **no fallback to the node directory.** Re-running the documented command
verbatim would re-mux the **old** VO out of `sources/`. Pointing `--clips` at the node's own
`clips/` is not a workaround either: `check_clips_dir()` (line 209) exits with *"no per-beat
clips (NN-*.mp4) found"*, because that directory holds only VO files.

**The copy step is mandatory:** six mp3 + six json for beats 05–10 into the new sources dir
before assembling.

### The derivation guard is a deny-list where it needs to be an allow-list

`derive_b12_stillmotion_0819.py`'s `keys_refused` names five parent keys it strips. **Six more
came through under names its filter does not match**, twice — including beat 01's
`cut_preference` with this job's id substituted through it (two generations of inheritance),
and a `derivation.seed` reading the wrong seed while the sidecar read the right one. All were
renamed rather than deleted, per convention, and **the naming propagated to the two new specs
while the leak stayed open.** Naming a leak is not closing it. **A verdict can arrive under
any key name**, so the guard must be an allow-list of keys a child may carry.

### Duplicate filenames across distinct takes — the repair pattern

`s20260818`, `s20260872` and `s20260873` all publish their mp4 as
`12-related-LTX-stillmotion-crf10-s20260818.mp4`. Three distinct takes, one filename, three
directories. Sidecar, bench row and `.sha256` each carry the correct seed, so provenance is
recoverable and nothing is mis-attributed. **The repair belongs in the generator, not in these
files: renaming a published artifact invalidates the `.sha256` that proves it arrived intact.**
That is the pattern — fix the writer, leave the evidence.

### Already fixed, so you do not re-find it

`box_autofill.py` can no longer report `backlog_empty` from a junk directory it created itself.
The fill path refuses when the queue root is Windows-shaped and `os.name != "nt"`, **before** the
`makedirs` that used to create a local directory with backslashes in its name, and it exits **4**
rather than 2 — 2 already means "the card wants work and nobody filed any", which is precisely the
reading the bug used to forge. The junk `C:\banyan-queue/` directory at the repo root is **left in
place on purpose** as the dated evidence.

### Smaller ones, named rather than left

- **The ladder's slate list is stale.** It says 07/09/15/19; the live cut's slates are **09, 15, 16**.
- **`review/ep2-picks/b15-0819-verdict.yaml` does not parse** — unquoted mapping-shaped fragment at
  line 59, `yaml.safe_load` dies at column 35. Nothing globs that directory so no builder is broken,
  but that lane's verdict is machine-unreadable.
- **`render_t3` prints `[ footage pending ]` on every slate card.** True for beat 15; **wrong for
  beat 16**, where footage exists and is barred by a ruling.
- **A status snapshot is a timestamp, not a state.** I wrote "the card is empty" off a 16:24Z
  `box_autofill --status`; by 20:40 a beat-19 job was running. Read the box directly.

---

## 5. State of the episode

**The live cut is `ep2-demo-0819c`** — `https://banyan.city/review/ep2-demo-0819c` (verified 200
tonight). 21 beats, **18 footage, 3 slates, 113.29 s, 720×1280, $0, 0 GPU seconds.** It is the
newest cut; there is no 0819d.

Honest quality breakdown inside the 18 footage beats: **6 written PASS** (1, 7, 17, 18, 19, 21),
**8 with a verdict that is not a pass** (3, 4, 5, 6, 10, 11, 13, 14), **4 never judged at all**
(2, 8, 12, 20).

### The slates and who owns them

| slate | owner | blocker |
|---|---|---|
| **09 THE PAUSE** | b09 plate lane (**no agent active**) | Both motion clips declare `is_show_content: false` in their own headers. The engine question is settled; **the plate cannot cast the man** (head ~35% against a 55% bar). The hair axis was **closed by measurement tonight** — eight renders, two wordings, `brown hair` in the negative throughout, brown arrived all eight times. Next route is reference-plus-crop: a build, not a wording rev. Its VO is the episode's punchline and plays over the slate card. |
| **15 GOOD LISTENER** | `b15-lane` (active) | **The leaf count.** Wording ladder closed at two rungs with the count still wrong. Two blockers died today — §6 came off it, and "cannot get him and a rooted plant in one frame at canon scale" died (its new plate does it twice running). Named route: a composite init, the same instrument beat 19 used. |
| **16 WHY** (new slate — was footage in the last four cuts) | the assembly lane | **A founder ruling, not an engine problem.** 2026-08-16 R4: *"both of them are wrong though and do not resemble the sapling."* All three `done_when` clauses are met and the beat still fails — the rejected palmate leaf fills the frame in 87 of 97 frames. **This is the only decision in the cut that is not another lane's written verdict, and it is one line to reverse.** |

### Newly footaged today

- **Beat 07 CONFISCATE — in the cut, PASS on both takes**, first attempt, all 97 frames opened
  consecutively. `FAIL-FROZEN` and F2 (the pre-registered most-likely failure) never fired. crf 10 is
  cut-preferred: background strip drift 5.43 vs 36.41, costing 23% of whole-frame motion and keeping
  100% of the gesture. **Fault travelling with it:** the plate dresses the scavenger in the guard's own
  pale wrap tunic — two men in matching officials' kit in a beat that must read as
  authority-points-at-scavenger. Follow-up `ep2-b07-scavcostume-0819` is filed.
- **Beat 19 THE DROP — in the cut, replacing a slate in every previous cut this episode has had.**
  Made by `beat19_drop_animate.py`: a deterministic composite, **no GPU, no model, $0, 44 s of CPU**.
  PASS on 8 of 8 pre-registered clauses; max |frame − plate| outside the fig's corridor across all 120
  frames is **0**. **Best-available on a steward ruling, not a pick** — `done_when` asks for fall,
  landing *and* "HE DOES NOT NOTICE", and this has the first two exactly and the third not at all. The
  last 2.792 s is an honest still.

### Beat 20 — motion proven, plate frozen

`ep2-b20-motion-0819` is **PASS on the clause it exists for, and beat 20 has footage for the first
time in the history of this repo.** The pick-up completes by a continuous path, fruit in **121 of 121
frames**, and `FAIL-FROZEN` — pre-registered as the *most likely* outcome — **did not fire** (6.1 levels
of interframe motion). Settled: `--image-crf 10` does not kill a large action.

**It is not in the cut and stays a slate candidate** for two pre-declared plate faults, neither charged
to the render: a thick **mature-tree** limb crosses the top-right corner of every frame (the founder's
own recorded fault), and there is no sapling in frame at all, so the empty stem that `done_when` calls
"the evidence" is absent. Neither is fixable by i2v, because the init is frame one.

### Beat 19's midpoint plate did not run — and the fix for it was already written today

`ep2-b19-sapmid-0819` (the 0.26 midpoint between the two passing strengths) **failed at its first
step and never rendered**: `socket.gaierror [Errno 11001] getaddrinfo failed` out of `fetch_init.py`,
rc=1 at 16:43:12Z. **No verdict is written and its bar is untouched** — scoring it would be scoring an
empty directory.

**This is the third network-fetch failure on the box today and the second lane to hit it**, and the
cure is already in the tree: `failed-acknowledged.yaml` carries a `fetch-404` group for
`ep2-b12-plateship-0819` whose two failures were fixed the same hour by **replacing the fetch with a
local copy step** (`0f799ddd`), after which the successor ran rc=0. That fix never crossed to this
lane. The init it fetches is already on origin/main at an asserted sha and could ride as a
`box_enqueue` payload with no DNS involved. Combined with `max_attempts: 1`, a three-second blink
permanently killed a GPU job and idled the card behind it.

**Re-runnable unchanged today** — but do the durable thing while you are there: payload the init and
raise `max_attempts`. Not re-queued by me: it is the beat-19 lane's rung, and `box_enqueue`'s
idempotency gap has already re-run a finished job and burned 264 s of GPU, which is exactly what two
lanes re-filing produces.

**The one job that would fix beat 20's darkening is a re-roll on a different seed** (its −25.03 ran on
20260819, the measured outlier). **It is not filed because b20's plate is the scavenger, and re-rolling
it is a goblin-identity render under the freeze.** That is a rule, not a doubt — and it is the single
most actionable thing waiting behind the letter in §1.

### The one thing that is button-ready right now

**Re-assemble the cut.** No GPU, no model, no spend, no ruling. It cashes in three finished pieces at
once:

1. **The six re-voiced guard takes.** Beats **5, 6, 7, 8, 10 carry wrong guard voices over real
   footage in the live cut, and beat 9's wrong voice plays over its slate card.** Verified by hash, not
   asserted — all six differ between the node's `clips/` and the published `sources/`, which are dated
   Aug 17. The published cut has Guard 2 at **1.7 Hz from the sapling**, the defect he heard.
2. **The palindrome → last-frame-hold fix.** The published 0819c still un-ripens beat 01's fig and bobs
   beat 06's board.
3. Beat 07's crf-10 take, already in.

Three things the assembler will not tell you: **the `--clips` copy step is mandatory** (§4); **runtime
will change** — 113.29 s will not survive the new VO lengths, since slots fit to the longer of script
and VO; and `render_t3` gates on §6 — *a bench cut is media* — so confirm §6 is off the node before
assuming the gate passes.

---

## 6. Machines, CI and the site

- **rtx5090 — idle, and the last job on it failed.** `ep2-b19-sapmid-0819` went to `running` at 20:40
  and was in `C:\banyan-queue\failed` three minutes later — **rc=1 at its first step**, DNS blip
  (`getaddrinfo failed`) fetching its init. No GPU ran. DNS resolves again now, so **it is re-runnable
  unchanged** (§5). `ready` holds only the eight parked `.HOLD`/`.DUP` files; `running` and `backlog`
  are empty. Read the box directly (`ssh rtx5090 dir /b C:\banyan-queue\...`), not
  `box_autofill --status`, which I caught being 16 minutes stale tonight — and note it reports
  `running` from a snapshot, so **a job can fail between two clean-looking statuses.**
- **So the card is genuinely empty as of ~17:15Z**, and there are two named, costed, unfrozen rungs to
  put on it: `ep2-b19-sapmid-0819` (re-run, owner's call) and `ep2-b12-noscav-0819` (hand-write the
  spec, §3).
- **CI is backed up on `lint-genome`, and it is not our code.** Runs at 15:05 and 15:23 finished in
  2:33 and 3:40; runs at **15:12 and 15:38 have been `in_progress` for over an hour**, stuck on the
  `sudo apt-get update && apt-get install fonts-dejavu-core` step. Mine (`42dcf0f8`) is stuck on
  `actions/checkout@v4` — **`.git` is 5.5 GiB** and every farm-out commit makes checkout slower.
  `mirror` and `pages` both went **green** on my push in 7 s and 5 m. **Local gates both pass at the
  tip:** `lint_genome.py` rc=0 (*"tree healthy — 0 violations"*, ratchet 25 unchanged) and
  `test_pipeline.py` rc=0, all tests. A red or hung `lint-genome` right now is infrastructure, but
  **check it is still the apt/checkout step before you conclude that.**
- **banyan.city — up, 200** in 0.64 s. Both founder pages serve: `ep2-goblin-design-0819` and
  `ep2-guards-0818`, plus the cut at `ep2-demo-0819c`.
- **Spend — $0.** Everything tonight was scp, ffmpeg, numpy and reading.

### Worktree — five orphaned files, reported and not touched

Not mine, and I did not commit another lane's work:

```
 M pipeline/body_motion.py                      (+76 −22)
 M pipeline/jobs/ep2-b20-canonword-0816.yaml    (+6  −1)
 M pipeline/judge_clip.py                       (+14 −1)
 M pipeline/loop/measurements-poscontrol-0816.txt (+27 −1)
 M pipeline/measured/local-disk.yaml            (+5  −5)
```

**All five share one mtime, 15:39** — a single lane's working set, uncommitted for five hours. An
uncommitted diff is evidence a lane is alive, so this is *probably* live work and not debris; but the
lane has been silent since, and `body_motion.py` and `judge_clip.py` are shared instruments that other
lanes import. **Ask before assuming either.** `review/inbox.yaml` and `review/index.html` were also
dirty at the start of the night and have since been committed by their owner.

---

## 7. Where the records are

| Thing | Path |
|---|---|
| **The goblin letter (THE key)** | `https://banyan.city/review/ep2-goblin-design-0819` · `review/ep2-goblin-design-0819/index.html` · HOLD at `pipeline/work-ladder-0819.md:1097` |
| **The guards look** | `https://banyan.city/review/ep2-guards-0818` · scores in `review/ep2-picks/cast-0817-scores.yaml` |
| D23, awaiting signature | `DECISIONS.md:1532` |
| Beat 17's unread line (§6) | `genomes/sapling/nodes/002b-first-citizen/leaves/002b-t0-c.yaml` |
| **Tonight's two verdicts** | `pipeline/jobs/ep2-b12-stillmotion-s2026087{2,3}-0819.yaml` → `verdict_0819` |
| **The 0-for-5 close, the phrase, and the next rung** | `pipeline/work-ladder-0819.md`, final sections |
| Beat 12 evidence (5 takes, sheets, sha256) | `farm-out/ep2-b12-stillmotion-s2026087{1,2,3}-0819/`, `-s20260818-0819/` |
| **The camera-drift instrument** | `farm-out/ep2-b12-stillmotion-s20260818-0819/b12_camera_drift.py` |
| The brightness instrument | `pipeline/luma_drift.py` |
| The (seed × plate) diagnostic + the reasoning error | `pipeline/loop/darkening-crf-diagnostic-0819.md` |
| Beat 08: scribble enclosure, masked IP-Adapter, the pose-net undercut | `pipeline/b08-arm-route-0819.md` §10, §11, §13–14 |
| The ~110 Hz attractor and the re-voice | `genomes/sapling/nodes/002b-first-citizen/clips/guards-revoice-0819.yaml` |
| The palindrome fix | `pipeline/render_t3.py` (`af863c0b`); audit at `pipeline/work-ladder-0819.md:654` |
| Beat 19's drop composite + its verdict | `pipeline/beat19_drop_animate.py` · `farm-out/ep2-b19-dropcomp-0819/` |
| Cut contents, picks and the honest counts | `review/ep2-demo-0819c/sources/picks-0819c.yaml` |
| Per-beat cut readiness | `review/ep2-picks/cut-readiness-0819.yaml` |

## 8. What I would pick up first

1. **Hand the founder the goblin letter.** One link, one letter. Everything goblin-shaped is behind it,
   including a one-job fix for beat 20.
2. **Re-assemble the cut** — §5. It is the only finished work in the project whose button is unpressed,
   and it fixes wrong voices on five footage beats plus eight backwards-playing beats. **Do the `--clips`
   copy step** (§4).
3. **File `ep2-b12-noscav-0819` by hand** — §3. One deletion, ~8 min, $0, and it is a real shot at beat
   12's first take that fails nothing.
4. **Re-run `ep2-b19-sapmid-0819`** (owner: the b19 lane) and payload its init instead of fetching it —
   §5. The card is empty behind it.
5. **Named, not built:** the derivation **allow-list** (§4), the `box_enqueue` **idempotency** refusal
   (it re-ran a finished job and spent 264 s of GPU), and the **positives-only** audit for off-screen
   clauses (§3).
