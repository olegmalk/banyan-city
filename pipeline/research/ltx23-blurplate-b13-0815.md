# A motion-blurred init plate halves the hold too — and unlike guidance, it costs nothing but sharpness

Measurement pass, 2026-08-16. **One recipe change, one sample, one matched
control rendered in the same job.** Nothing is scaled off this. $0 — local card,
no provider, two clips of 238 s and 199 s on an otherwise idle 5090.

This fires lever **L5** of `pipeline/research/ltx23-motion-source.md`
(`dfa87c27`). Read it beside `ltx23-cfg-b13-0815.md`, which fired L4 the same
night — **the two land on the same number from opposite directions**, and that
coincidence is the most interesting thing either of them found (§4).

Spec: `pipeline/jobs/ep2-b13-blurplate-0815.yaml`. **No renderer code was
touched**: the blur lives in the job's own payload crop script.

---

## The answer

**Blurring the init plate — one crop, 9 px of directional smear along y, nothing
else changed — takes beat 13 from period 3 to period 2 and from 32 distinct
pictures to 48**, with a stable background, a stable exposure, and a completely
flat energy profile across the clip.

| | control, clean plate | **9 px y-blurred plate** |
|---|---|---|
| hold period | **3** | **2** |
| autocorrelation at that lag | 0.923 | 0.917 |
| trough/peak **depth** | **0.038** | **0.041** |
| distinct pictures in 97 frames | **32.0** | **48.0** |
| **effective fps** | **8.0** | **12.0** |
| terminal freeze (bit-identical frames) | none | none |
| last change above 0.05 MAD | frame 96 of 96 | frame 96 of 96 |
| mean full-res per-pair MAD | 3.76 | **3.71** |
| frame-mean luma swing over the clip | 2.9 of 255 | 5.1 of 255 |
| f0->f96 alignment | scale 1.000 dy **+12**, ncc 0.873 | scale 1.000 dy **-2**, ncc **0.923** |
| render time | 238 s | 199 s |

The comb, full-resolution per-pair MAD, frames 40-48:

```
control      0.6  0.4 10.5 | 0.6  1.1  8.4 | 0.4  0.4 10.2     one loud pair every THREE
blur 9px y   0.3  6.4  0.5 | 7.5  0.4  6.6 | 0.3  7.2  0.3     one loud pair every TWO
```

Read the mean MAD row beside the period row, because together they say something
the period alone does not: **3.76 -> 3.71 is the same amount of change, spread
over 50% more pictures.** The blurred arm is not moving harder; it is moving in
smaller, more frequent steps. Its lag-1 autocorrelation is **-0.95**, about as
clean a two-frame alternation as the estimator can report.

---

## What it did NOT do, each measured rather than assumed

Three ways this could have been a fake win. All three were checked.

1. **It is not the camera.** `align_frames.py` on the action-free top band,
   f0->f96: scale **1.000**, dx 0, dy **-2**, ncc **0.923**. The control on the
   same tool reads scale 1.000, dy **+12**, ncc 0.873 — so the blurred arm's
   background is *more* stable than the control's, not less, and there is no
   zoom. (The CFG arm, by contrast, could not be registered at all: best ncc
   0.263 with the search widened to scale 0.80-1.40 and ±60 px.) Three clips on
   2026-08-15 showed unrequested push-ins of 1.036x and 1.26x, so this was
   settled by alignment, not by looking at a contact sheet.
2. **It is not exposure flicker.** The frame-mean luma swings 5.1 of 255 across
   the clip (the CFG arm swings 81.4). Removing each frame's mean luma and
   re-differencing leaves the reading unchanged — period **2**, **48.0** distinct,
   mean MAD 3.93 against a raw 3.68. The DC term was not producing the pairs.
3. **It does not decay.** Full-res per-pair MAD by twelfths:

```
control      2.93 4.47 3.77 3.02 4.76 3.99 2.76 3.85 4.22 3.13 3.98 4.19
blur 9px y   3.91 3.77 3.70 3.80 3.85 3.62 3.80 3.59 3.34 3.63 3.70 3.77
```

   Flat end to end — flatter than the control's own profile, and with none of
   the CFG arm's collapse (which fell from 17.75 to 2.98 over the same span).
   Neither arm has the frame-62 wall: zero bit-identical pairs in either, last
   change at frame 96 of 96 in both.

---

## The cost, and it is a real one: the clip is soft for all 97 frames

`pipeline/research/EVIDENCE-blurplate-b13-0815.png`, three panels. I opened them.

Panel B is the one that matters. The blur does not behave like a "motion cue"
that the model consumes and discards — **it becomes the look of the whole clip.**
At f0 the figure is smeared, and at f96 it is still smeared: the ears are soft,
the ink linework never re-forms, the shirt seams stay mushy. The clean control
beside it holds crisp anime linework for all 97 frames. Nothing resharpens.

That matters here specifically. The founder killed the v2 low-detail style on
2026-07-27 for being **unreadable on screening**, and the current look is
"detailed cinematic anime". A recipe that buys 12 fps by making every frame soft
is trading against a taste call the founder has already made — which is his to
make, not this lane's, and the reason this is reported rather than adopted.

**And he still does not rock.** The prompt's action clause is "He rocks slowly
forward and back". Across seven frames spanning the clip the blurred arm holds
the same folded pose the control holds. The head drifts a few pixels; the body
does not perform the action. Panel C shows the two-frame comb clearly; it does
not show a rock.

---

## The coincidence, which is the finding worth passing on

Two interventions with nothing mechanically in common —

- **guidance 2.0 -> 1.0**, which weakens the conditioning signal at every step
  and kills the negative outright (`ltx23-cfg-b13-0815.md`), and
- **a blurred init plate**, which degrades the conditioning *image* while leaving
  guidance, prompt, seed, sigmas and every flag untouched

— produce **exactly the same reading: period 3 -> 2, 32.0 -> 48.0 distinct
pictures, 8.0 -> 12.0 effective fps.** Not similar; identical, to the resolution
the metric reports.

Neither reaches period 1. Neither makes the figure act. Both hold at the same
depth as the control (0.038 control, 0.035 CFG, 0.041 blur).

The hypothesis that suggests — **stated as a hypothesis, from two samples, not
proved** — is that period-2 is a *floor of this recipe* rather than a property of
either lever: degrade the conditioning in almost any way and the distilled
transformer moves from three-frame holds to two-frame holds and stops there. If
that is right, then no amount of further conditioning-degradation reaches
per-frame motion, and the next question is not "which lever" but "what changes
the floor" — steps, sigmas, the distilled checkpoint itself, or the dev
checkpoint that schedules `stg_scale` to 4 and `guidance_scale` to 8.

**Two samples are two samples.** The honest way to test that hypothesis is a
third degradation of a different kind on the same beat and control, one variable,
looking for period 2 again. This pass does not license one; it names it.

---

## How the two arms were kept matched, and the proof the default path is unchanged

**ONE source plate at an asserted sha, cropped TWICE by ONE script**; one encode
feeding both arms; one seed 20260815; both renders in one job. The two render
argvs are byte-identical apart from `--jobs`, `--task`, `--bench-jsonl` and
`--bench-label` — the generator asserts it — so the plate is genuinely the only
variable, and it enters through the per-arm jobs json rather than through a
recipe flag. The prompt, negative, source plate, plate sha and crop script were
read out of `pipeline/jobs/ep2-b13-stg-0815.yaml` rather than retyped.

`pipeline/ltx_i2v.py` was not edited. The blur is three argparse lines and one
`if a.motion_blur > 0:` block added to the job's own payload crop script; the
generator asserts the extension is **insertion-only** (all 35 of the STG lane's
lines still present verbatim, +30 added), and that the clean arm does not pass
the option at all. The empirical proof is stronger than the static one:

```
210932b760f70ef34b97f41a28d1905ef5358e5f6982110c3f2440884b8b5199  b13-init-704x1280-clean.png
42043851da4b246cfcd4e858cda828da992d0d48f15ef10d81d3a99c1ceb445a  13-the-shade-PLATE-clean-control.mp4
b36b3355211a96986d08da1952457c74a470228527b1c90bb3dc9e82e518b848  b13-init-704x1280-blur9px-y.png
34a4ee8573e4e422a19abe808fabb9e357f44ff5fc5fe23c349d94758925c560  13-the-shade-PLATE-blur9px-y.mp4
```

The clean crop step **asserts its own output sha and fails the job** rather than
continuing if it drifts — and it hashed to the same `210932b7…` the STG and CFG
lanes rendered from, producing the same `42043851…` clip. That is now **four
independent jobs across three nights** returning the identical bytes from an
asserted source plate through a fresh crop, encode and denoise.

The blur is declared rather than tuned: one axis, one length. The scripted action
is "rocks slowly forward and back", whose screen projection is dominantly
vertical, so the streak runs along y; 9 px on a 1280-tall frame is ~0.7% of frame
height. **A different length or axis is a further sample, one variable each, and
this job does not license one.**

Recipe, unchanged and not under test: 704x1280, 97 frames, 24 fps, two-stage
8@352x640 + 3@704x1280, distilled sigmas, guidance 2.0, image-crf 33, sequential
offload, STG unpassed on both arms. Prompt measured on the real Gemma tokenizer
before firing: 58 tokens / 37 words, negative 38 / 25, of a 1024 limit. Sidecars
carry `cost_usd: 0` and no `approved:` key.

---

## What this closes and what it leaves

**Closed.** L5. A motion-blurred conditioning frame is not inert — it is one of
only two things that has ever moved this hold. `Shecht-ltx`'s semi-official
"if the initial frames contains motion cues (such as motion blur) it may help"
(github.com/Lightricks/LTX-Video/issues/184) is, on one sample, **correct about
the period and silent about the cost**.

**Open, and deliberately untouched by one sample.**

- **Blur length and axis.** 9 px along y is one point. 3 px might buy the period
  without the softness; 20 px might not buy more. Unknown.
- **Blur the SUBJECT only.** A global smear is why the whole clip is soft. A
  masked blur on the figure alone is the obvious next shape and needs a mask,
  which is a second judgement and therefore a second sample.
- **Whether the softness survives the second stage differently at another CRF.**
  We run image-crf 33; the same source suggests 30->35. Untested in combination,
  and combining them would be two variables.
- **Whether any of this transfers off beat 13.** One beat, one plate, one seed,
  one wording.

**This is not a recipe change and must not become one.** Neither this nor the
CFG result makes the figure act, and this one makes every frame soft against a
taste call the founder has already made once. On 2026-08-03 a recipe was picked
on a steward's own metric, rendered across all fifteen beats, and came back
"literally just frozen frames". 48 pictures of the wrong thing is not a better
beat than 32.

---

## Provenance

Steward, 2026-08-16, model claude-opus-5. Both clips were rendered on the RTX
5090 in the renderer's own venv from `pipeline/jobs/ep2-b13-blurplate-0815.yaml`,
published to `farm-results-rtx5090:farm-out/ep2-b13-blurplate-0815/` with a
sha256 manifest, and measured on this machine with `pipeline/hold_period.py`
(`d820bf3f`) **imported and not edited** — it belongs to another lane — plus the
trough/peak `depth()` from `pipeline/vae_roundtrip.py` (`70e3c79a`), copied
locally rather than landed in `hold_period.py`. The harness was validated before
use by reproducing the STG lane's published control numbers exactly. Frame
alignment is `align_frames.py`, the STG lane's tool, unmodified. The GitHub quote
is **not** re-fetched here and is attributed to `ltx23-motion-source.md`
(`dfa87c27`) where it was fetched. $0 spent, one queue entry, fired on an idle
card the moment the CFG job released it.
