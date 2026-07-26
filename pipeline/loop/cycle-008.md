# Cycle 008 — the audio didn't match the script either

**Opened** 2026-07-25, night, immediately after cycle 007's scripts landed.
**Trigger:** not a new founder complaint. Cycle 007 fixed the picture side of
dad's verdict — *"the video is not matching the audio at all, or the script"* —
and I went looking for whether the audio side had ever been checked. It had
not.

## Method

Measure, do not read. Every claim below came from a measurement that
contradicted something the repo already asserted, usually something I had
asserted earlier the same evening.

## Four defects, all in the voice/assembly path

### 1. Stage directions owned 3.6–4.5s of silent screen time — each

Cycle 006 put short stage directions on screen for a good reason: the tree has
no mouth, so its answers *are* stage directions ("One leaf tilts."), and they
were reaching nobody. It was implemented as a **blocklist** of camera words,
which is the wrong shape. The list held `close-up` but not `close on`, and said
nothing about scenery or about other characters' business, so it admitted **258
of the genome's 271 directions**. Each admitted one then took a silent hold
before the beat's line, captioned with words nobody speaks:

| where | what the viewer got |
|---|---|
| 002b beat 16 | 3.6s of silence reading *"Close on the sapling's leaf; the scavenger sits blurred behind it"*, then the line |
| 001 beat 13 | 4.5s of silence reading *"The sun arcs overhead three times as one new leaf unfurls from a bud"*, then a 3.6s line |

Total silent hold across the genome: **~1057s**. This is two founder
complaints in one mechanism — *"that random delay in the beginning, no sound
for like 3 seconds straight staring at the random ai animation"* (07-23) and
*"this is literally just the script being put as dialogue"* (07-25). I had
fixed the caption layer so directions stopped being **spoken**; I never checked
that they had stopped owning **time**.

**Fix:** `pipeline/direction.py` — an allowlist. The tree must be the SUBJECT
and must be gesturing. Naming a leaf is not enough: *"He holds the fig up
beside the bare branch it fell from"* is the goblin's business. **9 gestures
survive genome-wide**, exactly the one-bit protocol the show runs on, for 20s
total. The hold is capped at 2.2s, because past a couple of seconds a silent
hold stops reading as a pause and starts reading as a stalled video.

### 2. A beat that lost its dialogue kept the previous cut's voice

`synth_vo` skipped no-line beats with a bare `continue`, leaving whatever take
was on disk from before the script changed. Cycle 007 renumbered every beat, so:

- **007a beat 5 played the episode's closing line, "…Who's that?", 20 seconds in.**
- 001 beat 5 played 21 seconds of narration over a silent shot of a man falling
  off a chair.

Four orphans across the trunk. **Fix:** synth_vo archives them as it goes (R6),
plus any take numbered past the last beat; `retime_beats.py` refuses to run when
voice and script disagree in either direction.

### 3. Beat time ranges were hand-written, so every density number was fiction

The ranges in the beat headings are treated as truth by `render_t3` (slot
sizing), `lint_genome` (shots.md must repeat them) and the loop's own density
tables. They were guesses. Nine of 001's eighteen beats held more voice than
their window allowed, so the assembler stretched the slots and **001 assembled
at 133s against a script claiming 88s** — meaning the "a cut every 4.9s" I
logged in cycle-007 *earlier the same evening* described no episode that has
ever existed.

**Fix:** `pipeline/retime_beats.py` derives the ranges by calling
`fit_duration`, the very function the assembler sizes slots with. Nothing is
capped: a beat whose voice runs 20s gets a 20s range and is **reported** as over
spec, because that beat is carrying too much and the fixes — a shorter line, or
a cut inside the line — are the author's (R4).

### 4. Masters undershot the platform target when peak-bound

`loudnorm` in linear mode clamps its own gain against the true-peak ceiling and
then reports a `target_offset` it never applied. Nothing measured the result. A
bench cut of 001 came out at **−15.4 LUFS** against −14.

Scope, measured rather than assumed: the seven **published** episodes are all
−14.2 to −14.4 and pass. The undershoot bites on peak-bound or
long-quiet material — which is precisely the profile of every re-rendered
episode until real footage lands.

**Fix:** measure the master and feed the shortfall back through loudnorm's own
`offset`. Two wrong turns are recorded in the commit, both of which read fine
and failed the gate: a `volume=` stage bolted onto the final mux put true peak
at 0.1 dBTP because it ran *after* the 44.1k downsample. The loop stops when a
pass stops buying loudness and says the material is peak-bound, rather than
burning encodes on an asymptote.

## What the corrected numbers are

001, re-timed from measured voice: **18 beats, 111s, a cut every 6.2s, 0.89
spoken lines per shot.** Six beats still exceed the 6s spec — each holding a
single line that takes 7–9s to say. Only 3 of 51 measured lines run over 6s and
the median line is 10 words at 177 wpm, so the lines are *not* too long. The
over-spec beats were mostly the silent holds of defect 1.

## Mistakes I made inside this cycle

Recorded because the repo's rule is that the pipeline learns, not the person.

- **Overstated a defect's blast radius** in a commit message ("every episode
  this season has been shipping ~1.5 LU quieter") before measuring the
  published files. They were fine. Amended before pushing.
- **Gutted `synth_vo.py` with a regex.** Extracting the direction rules used a
  function-body bound of "next blank-blank-line", and there wasn't one — it
  swallowed the rest of the file, `main()` included (423 → 182 lines).
- **Verified that extraction in the wrong interpreter.** I imported the new
  module under the pipeline venv (python 3.14), where PEP 649 makes annotations
  lazy, so a missing `from pathlib import Path` imported cleanly. The VO run
  uses cb-venv (3.11), where annotations evaluate at def time; it died
  instantly and killed the re-voice of 005, 006a and 007a. **A `for` loop's
  exit code is not its body's exit code** — the chain reported three nodes
  "done" in the same minute and I read the timestamps as progress. Both
  interpreters are now checked before anything is believed.

## Status

All four fixes are in and verified by measurement; lint and the pipeline tests
(219 checks) are green, read as their own step. Re-voicing and re-timing the
trunk with the final rules is in flight. The verdict on whether picture and
sound now match the script is the founder's (R4) and cannot be self-assessed.

## Addendum (2026-07-26): the free tier cannot run this model

Wan 2.1 T2V produced blank grey on Kaggle's T4 twice — once with the whole
pipeline in fp16 (luma spread 14 of 255) and again with the VAE forced to fp32
(spread 22). The VAE was not the problem. The transformer is.

Wan 2.1 is released and trained in **bfloat16**. fp16 has the same 16 bits but a
far smaller exponent range, so activations that are fine in bf16 overflow to inf
and then NaN, which decodes to a flat mid-grey frame. The fix is to run it in
bf16 — and:

| Kaggle free accelerator | arch | bf16? |
|---|---|---|
| Tesla T4 | sm_75 (Turing) | **no** — bf16 arrives with Ampere, sm_80 |
| Tesla P100 | sm_60 (Pascal) | no, and current torch ships no kernels for it |
| TPU v3-8 | — | not a CUDA path for this pipeline |

**There is no bf16 GPU on Kaggle's free tier.** fp32 would be numerically safe
and is ~8x slower on a T4 (roughly 4 hours per 5-second shot against 29 minutes),
which cannot finish an episode inside a 12-hour session.

So the $0 floor is not "Wan on Kaggle". It is a model that is fp16-native. The
obvious candidate is **AnimateDiff on an anime-tuned SD1.5 checkpoint**: SD1.5 is
fp16-safe by design, runs fast on a T4, and — the part that matters more than
speed — flat cel-shaded anime is exactly what those checkpoints are good at,
which is closer to `style.md` than a general-purpose video model was ever going
to get. CogVideoX-2B is the fallback (fp16 supported, unlike the bf16 5B).

Cost of learning this: about 9.5 GPU-hours of the weekly 30, six pushes, and one
false success report. The guard that now aborts on a blank frame is the reason
the next wrong model costs one clip instead of a session.

## Addendum 2 (2026-07-26): local rendering is off the table, and why

I moved rendering to the founder's Mac after he questioned why I was still
fighting Kaggle. The reasoning was right — the push/wait/fetch loop was costing
far more than the compute — but I ran it on his machine without measuring the
cost first, and he had to kill it because the machine became unusable.

Measured, M1 Pro / 32 GB, AnimateDiff at 512x512 x16 frames:

- **4-5 minutes per denoising step.** At 25 steps that is ~1.5 hours for one
  3-second clip, ~30 hours for a 20-beat episode.
- 12+ GB resident, and it starves everything else.

The cause is structural, not a misconfiguration: AnimateDiff is not a per-frame
image model. Its temporal attention attends across all 16 frames at once, and
MPS has no efficient kernel for that shape. A free Kaggle T4 does the same work
in minutes. So the conclusion inverts what I told the founder an hour earlier —
**the T4 is the right compute and the Mac is not**, and the fast-iteration
argument does not survive a 90-minute step count.

`render_local.py` now refuses to run without an explicit
`--yes-this-eats-the-machine`, with the measured numbers in the refusal. It is
kept rather than deleted because the code is correct, the approval gate inside it
is worth having, and a smaller model or a newer machine could make it viable.

**Two mistakes here, and the second is the one that matters.** Running an
unmeasured heavy job on someone's working machine is the obvious one. The real
one is that I had the measurement available for free — a single step would have
told me — and instead I launched the full job three times concurrently, which
also caused the "MPS out of memory" I then misdiagnosed as a config problem.

## A finding worth keeping, independent of platform

CLIP truncates at **77 tokens**, and every one of 001's twenty prompts is
113-145. Measured with the actual tokenizer, beat 1's prompt is cut here:

> …a tiny mascot-simple banyan sapling — thin curved trunk, two oversized
> expressive leaves, no ***[CUT]*** face — trembles and shivers in a gust of
> wind, filling the lower half of the frame, alone in a vast green field…

So the model never sees the **action** — the trembling, the wind, the framing,
the light — because ~45 tokens of style preamble consume the budget first. Every
prompt in the genome has this shape. Whatever renders the season, the prompts
need restructuring: a compact style tag, the action early, and the "no
photorealism / no text" tail moved into the negative prompt where it belongs
(it is already there, so the tail is pure waste). This is very likely a
contributor to the mush, and it costs nothing to fix.

## Addendum 3 (2026-07-26): the renderer works, and what it cost to find out

Seventeen pushes to get one picture. The pipeline now renders a coherent,
on-genre shot in about 80 seconds on Kaggle's free T4, assembles to a captioned
9:16 episode, and passes all twelve QA checks. What follows is what was actually
wrong, in the order it was found, because almost none of it was where I looked.

| attempt | what I believed | what was true |
|---|---|---|
| 1–6 | Kaggle config, memory, dtype | all real bugs, none of them the blocker |
| 7 | Wan needs bf16 | true, and fatal: no free GPU has bf16 |
| 8–11 | AnimateDiff resolution | real: 432x768 x24 is 2.5x the module's native size |
| 12 | the VAE is destroying good latents | **wrong** — final latents at std 0.357 were themselves flat, and I read a decreasing curve as healthy because I wanted to |
| 13 | prompt truncation | real: all 182 prompts ran 113-145 tokens against CLIP's 77, so the model never saw the ACTION |
| 14 | style tag first protects it | backfired: whatever leads the prompt BECOMES the subject — abstract lineart, then a leaf close-up |
| 15 | negative prompts beat priors | **wrong** — "no mature tree" produced a thicker trunk |
| 16 | **the checkpoint and adapter are an incompatible pairing** | correct, and found by bisecting rather than guessing |
| 17 | prompts were being delivered | **wrong** — the notebook clones from GitHub and I had not committed |

### The three habits that cost the most

**I built alarms instead of instruments.** Every guard reported *that* a render
failed — blank frame, wrong contrast, bad exit code. None reported *where*. Thirty
lines printing latent statistics settled in one run what six pushes could not, and
bisecting (plain still, no adapter → adapter on vanilla SD1.5) settled the rest.
The lesson is not "add more checks"; it is that a check which cannot localise a
fault is nearly worthless.

**I shipped fixes to the file I was not running.** The resolution fix went into
`render_local.py` while I pushed the notebook. The prompt rewrite went into a
working tree the remote cannot see. Both produced *unchanged output*, which reads
as "the fix did nothing" rather than "the fix never arrived" — the most expensive
possible failure mode. `run_remote` now refuses to push with uncommitted prompt
changes, and says why.

**I compared quantities that were not the same quantity.** The blank guard
measured RGB spread against a threshold calibrated on LUMA spread — 28 versus 18
on the same frame — so the notebook passed a grey clip that qa_episode failed.
Not a threshold to tune; the wrong measurement.

### And the failure mode no automated check caught at all

Contrast cannot see meaning. A vivid abstract batik pattern scored 153 and passed
every gate I own. A leaf on a lilypad scored 36 and passed. The founder looked at
the contact sheet and said "that looks like a leaf on a lilypad", which was worth
more than every number I had produced. **Every render now goes to him as a contact
sheet.** That is the check.

### Where the remaining work is

Five beats of 001 rendered: three match their beat well, one is washed out
(multiple trees where there should be one), one does not depict its action. So
roughly 60% first-pass usable, and the gap is prompt craft rather than plumbing.

Guards learned to distinguish a broken SYSTEM from one bad INPUT: a blank beat is
now kept as `.SUSPECT`, skipped, and reported, and the run only aborts if most
beats fail. One awkward prompt had been costing the other nineteen.

Still open: character consistency across 166 shots with no reference-image
conditioning, which is the problem cycle-007 predicted would arrive once shot
counts rose, and which no prompt tweak addresses.
