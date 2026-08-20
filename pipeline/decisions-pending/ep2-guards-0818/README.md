# `/review/ep2-guards-0818` — what fires on each answer

The card asks one taste question: **do the guards read as grown men, and if not,
does that matter?** It offers three answers. Beat 09 — one of episode 2's two
remaining slates — is held by that answer and nothing else.

---

## On **"pass"** (accept them as they are)

**Run `swap-b09-into-cut.sh`.** It is written, it is idempotent up to the git
step, and it needs no further decision. Beat 09 stops being a slate and the cut
goes to **20 footage / 1 slate**, the most episode 2 has had.

That script is the whole of it. Do not also file a casting rung — "pass" means
the read is accepted, and re-casting after it would be spending the card's answer
twice.

## On **"recast"**

**File nothing from here.** A casting rung needs a new wording or a new reference
and neither exists yet; writing one now would be guessing which. Beat 09 stays a
slate, the cut stays at 19/2, and the four wide-shot guard beats (05, 06, 10, 11)
go back to the casting lane with the ruling attached.

What is *known* and should be carried into whatever gets written: the adjective
route is closed by the 2026-08-12 ruling (body-type and tone words stay out of the
prompt), so a recast rung cannot be "say adult". Five rounds have already failed
that way.

## On **"stage"** (crop, angle, coverage carry the age)

**File nothing from here — but note that beat 09 is already the evidence for it,
and it is already built.** Beat 09's close-up scored adult 5 of 12 where the four
wide shots scored 0 of 12, and the crop that produced it is a solved, measured
route (`pipeline/beat09_plate_crop.py`; the finding is *"crop the reference to the
bar and condition on the crop"*). If the answer is "stage", then `swap-b09-into-cut.sh`
**also** applies — beat 09 IS a staged-around beat — and the follow-on work is
re-cropping beats 05/06/10/11 the same way, which is a new rung and not a
pre-stageable one.

---

## The one trap in the swap, carried here so nobody rediscovers it

`render_t3.get_clip()` globs `NN-*.mp4` and takes the **sorted first**. Leaving an
old file beside a new one is a coin flip on filename ordering, not a swap. Beat 09
has no `09-*.mp4` in the cut today (it is a slate), so nothing needs deleting —
but the script asserts that rather than trusting it.

And: `build_site` publishes only what git tracks, while `.gitignore:50-59` ignores
`review/**/*.mp4` and `review/**/*.jpg`. **Force-add the media before running the
gate** or `qa_local` reports broken links. That is exactly how the beat-03 swap
failed on its first attempt on 08-20.

## What the swap does NOT do

It does not touch beats 05, 06, 10 or 11, and it does not re-render anything. It
also does not need a VO copy: `09-vo.mp3` and `09-vo.json` are already in the cut's
`sources/` (`total_s 1.881`, GUARD 1: *"…We confiscate the goblin?"*).

**Slot arithmetic, so the result is not a surprise.** `render_t3.fit_duration()`
returns `max(min(cdur, vdur+2.0), vdur+0.4)`. With the clip at 5.042 s and the VO
at 1.881 s the slot is **3.88 s ≈ 93 of the 121 frames** — f094–f121 are cut and no
hold branch fires. The hand-dissolution defect is in f001–f008 and therefore stays
in shot; it is named on the card.
