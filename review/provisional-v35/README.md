# ep1 v35 — PROVISIONAL SCREENING CUT, 2026-08-10

`ep1-v35-PROVISIONAL.mp4` — 89.2s, 720x1280, 15 beats, 0 slate, $0.
sha256 `7d09b46b5be26ec5…`

> **Re-assembled 2026-08-10 ~20:10 — beat 6 only.** Roman picked the beat-6
> frame (*"this one is good enough lets not overthink it, use that"*) and beat 6
> now holds `06-too-blue-r8d-step3-s0` instead of `b06-r5-s2`, a frame he had
> explicitly rejected. The other fourteen clips are byte-identical to the
> version described below; the cut's sha256 changed because beat 6's clip did.
> He approved the FRAME — not the cut, not canon, not publication (R4).
> The previous sha was `acb42c2eb8ae482f…`.

**What this is:** v34 with five beats swapped for plate twins, so the geometry
fix can be judged **in an episode** instead of in a folder of sixteen loose
clips. Nothing here is published, promoted, or announced. No taste verdict is
offered on any beat — that is yours (R4).

**What this is NOT:** a claim that the five new clips are good. They are not
being offered as good. The twins fix **geometry only**, and every twin inherits
its raw round's motion defects — beat 08's in particular is a correctly-framed
version of a clip already measured as a motion regression. The defects are named
per beat below so you can watch it once and know what you are looking at.

## The one thing the twins actually fix

Every clip in the v34 motion series was rendered off a raw 832x1216 still
resized to 704x1280 — a **24.4% vertical stretch**. The cut is a cover-centre
crop. A stretched clip dropped in beside the others would jump.

A twin is the identical render with one thing changed: the conditioning image is
a properly prepared 704x1280 plate. Measured on frame 0 against two
reconstructions of the clip's own still (`QA-plate-twins-0810.md`), sixteen pairs
inverted with no exception:

| | vs stretch | vs crop |
|---|---|---|
| raw arm (beat 08 r2) | 2.75 | 17.17 |
| **twin** (beat 08 r2) | **17.22** | **2.83** |
| the clip already in the v34 cut | 17.09 | 1.28 |

The twin lands on the same side as the cut's own clip. **The twin is not a new
framing — it is the framing the cut already uses.** The raw version was the odd
one out.

## Which round went in, and why that one

Where a beat had several twin rounds I did **not** pick the best one — that is a
taste call and not mine. The rule is mechanical: **highest round number
available.** Nothing more. The record explicitly warns that "latest" is not
"best" (879820f, 655d2c6 both record a later round being worse than an earlier
one), so this rule avoids making a judgement; it does not make a good one. Every
round of every beat is twinned and sitting in `review/v34-motion/` — **any of
these five is yours to override**, and the alternatives are listed.

## Per beat — all fifteen

Twins run 2.708s. Where a beat's slot is longer, `render_t3` palindromes the clip
(plays it, then plays it backwards) so the seams are motion-continuous rather
than jump-cuts. The loop factor is listed because on beats 08 and 10 it is large.

| # | beat | what's in v35 | source | what it carries |
|---|---|---|---|---|
| 01 | the keyboard | **v34 fallback** — footage | v33 copy | no motion round was ever rendered for this beat |
| 02 | three-oh-seven | **v34 fallback** — footage | v33 copy | no motion round |
| 03 | deploy succeeded | **TWIN r3** — loops 1.31x | `03-…-LTX-r3-plate` | **framing drifts.** r1 panned 35% of the frame width; r2 fixed most of it but left a slide that crops the monitor bezel and was a REJECT on its own falsifier (07218cb); r3 was specified to fix that residual and **its outcome was never measured or opened before now.** On the frames: the picture slides across the shot — by the last frame the monitor has moved off-centre right with its edge cropped and the plant has grown from a sliver to a third of the frame. Picture itself is clean: no human, no invented object. Alternatives: r1, r2 |
| 04 | the fall | **TWIN r4** — plays once, complete | `04-…-LTX-r4-plate` | **this is the big visible change.** The cover-crop drops 19.6% of the width and this shot's hand sits near the edge, so it reads meaningfully tighter than v34's held still. That is the correct framing (it is what every delivered episode uses) but it is the one beat where you will notice the crop itself. **The invented wrist phone that r1/r2/r3 all drew is gone** — not visible in r4's frames. Beat has no VO. Alternatives: r1, r2, r3 (all three hallucinate the phone) |
| 05 | fan spinning down | **v34 fallback** — held still | v33 copy | held plate, 12% push-in. No motion round |
| 06 | too blue | **YOUR PICK** — held still | `b06-r8d-step3-s0` | **changed 2026-08-10 after the table below was written.** This is the frame you took at ~19:58 — the repaired step 3, the one where the wolf and the metal ring are gone and the cloud is banked to the edges. It replaces `b06-r5-s2`, which you had rejected and which v34 was still holding. Held still, 12% push-in. **No motion round has ever run on this beat** and no ruling covers whether it should — your "yeah keep em still" named 05/09/12/15, not 06. Approved as a frame; not canon, not published |
| 07 | zero moving parts | **TWIN r5-g20** — loops 2.46x | `07-…-LTX-r5-g20-plate` | **guidance 2.0** — the only round where the negative prompt did anything at all (at guidance 1.0 the distilled model runs no unconditional pass, so half the prompt was inert all night). The pre-registered risk was that off-spec guidance breaks the image; **checked on the frames, it did not** — clean cel palette, horizon holds, no invented object. This beat animates **on twos** (~12fps effective) in every round; that is the sampler, not the wording. Alternatives: r1, r2, r3, r4 |
| 08 | sev-1 | **TWIN r2** — loops 4.77x | `08-…-LTX-r2-plate` | **KNOWN MOTION REGRESSION, and the highest-round rule walked straight into it.** r2's affirmative framing lock froze the one beat that was already moving: median flow 1.07 → 0.10, frozen frame-pairs 0% → 66% (879820f). Four frames across the clip are near-identical — confirmed by eye. It is correctly framed and nearly still. **r1 is the alternative and it moves**; this is the substitution most worth overriding. Longest loop in the cut |
| 09 | whoami | **v34 fallback** — held still | v33 copy | held plate. No motion round |
| 10 | sense | **TWIN r2** — loops 3.88x | `10-…-LTX-r2-plate` | **the sprout climbs.** Its apex rises 181px over the shot, identical in both rounds — and no framing wording can bind it, because it is the subject being *drawn taller* inside a fixed frame, not a camera move (655d2c6). Visible on the frames: the stem grows through the shot. Whether that suits the line is yours. Picture clean otherwise. Alternative: r1 |
| 11 | grow | **v34 fallback** — footage | v33 copy | no motion round |
| 12 | undefined | **v34 fallback** — held still | v33 copy | held plate. No motion round |
| 13 | i always left | **v34 fallback** — footage | v33 copy | no motion round |
| 14 | worth staying in | **v34 fallback** — held still | canon `b14-r4-s3` | **this beat HAS motion rounds and deliberately has no twin.** r1 collapses (the sapling bends over and leaves frame); r2 is upright and clean but drifts up and crops the leaf tips. The re-cut was **gated in code** (26ece5c) because its spec applied beat 08's freezing lock to the most frozen beat in the cut. So v35 shows you the v34 held still here. This is the biggest remaining hole |
| 15 | something's coming | **v34 fallback** — held still | v33 copy | held plate. No motion round |

**Five twins in, ten v34 fallbacks.** Of the ten, nine simply never had a motion
round rendered; only beat 14 has footage that was deliberately held back.

## Two things about the cut as a whole

- **`qa_episode` carries two pre-existing warnings**, both structural and both
  also present in v34: a 5.5s dialogue hole from 12s (beats 04 and 05 have no
  VO) and a dark opening (beat 01 is a dark room by design).
- **The licence gate refuses this cut, as expected.** Ten of its ingredients are
  withheld: the five LTX twins (LTX-2 Community Licence, D16 open) and five held
  stills on OpenRAIL++ frames (D15 open). Both are your calls and neither is
  touched here. **This is a screening cut and cannot be published either way.**

## Provenance

Assembled with `python3 pipeline/render_t3.py sapling 001 --clips
review/provisional-v35/clips --out review/provisional-v35/ep1-v35-PROVISIONAL.mp4`
— bench mode, so no leaf was written and nothing entered the genome.
`scripts/v35-assemble.sh` was read first and not used: its two subcommands
(`ratify`/`flip`) both answer the **beat 6** question and neither substitutes
twins. Its staging convention and its exact `render_t3` call are what this
followed. No model ran, no GPU, $0.

> **DO NOT RUN `scripts/v35-assemble.sh` ANY MORE — it will silently destroy the
> twins.** It was written the night before, when v35 was going to be v34 plus a
> beat-6 change, so both subcommands begin with `stage_clips()`, which does
> `rm -rf review/provisional-v35/clips` and re-copies from
> `review/provisional-v34/clips`. Since commit `a57bf05` that is no longer a
> no-op: beats 03, 04, 07, 08 and 10 differ between v34 and v35, and staging
> would revert all five to their v34 versions with no warning. The 2026-08-10
> beat-6 swap therefore called `pipeline/hold_still.py` and `pipeline/render_t3.py`
> directly on the existing directory, replacing beat 6's two files and touching
> nothing else. The script needs a guard before its next use; that is the
> assemble lane's file, not this note's. Each substituted clip was copied
byte-identical out of `review/v34-motion/` (`cmp` clean) and its sidecar carries a
banner naming the twin, the round and the rule.
