# Loop cycle 015 — the softness was an upscale, and the slowness was paging

**Opened:** 2026-08-02 (overnight) · **Closed:** pending founder screen
**Source:** founder on `ep1-v21-CANON.mp4`: *"1 done. 2 too low quality.
tommorow we WILL post."* And, on the motion.yaml round: *"definitely improvement,
but i noticed these all have a pattern of like, shaking alot, strangly."*

## 1. The worker could fetch the queue and still not read it

Dad shut the 5090 down after a crash; the restart died with
`'NoneType' object has no attribute 'read'` inside pyyaml. The traceback pointed
at YAML and the fault was six frames earlier: `farm_worker.sh()` passed
`text=True` with no `encoding=`, so subprocess decoded git's output with the
**locale** codec — cp1252 on that box. `pipeline/farm-queue.yaml` legitimately
holds an em dash and the Chinese terms from Wan's official negative prompt, and
cp1252 dies on 静 (`E9 9D 99`).

Reproduced exactly: the queue file fails cp1252 at **byte 372 → 0x9d**, which is
byte-for-byte the founder's traceback.

The nasty part is where the decode happens — on subprocess's **reader thread**,
where the `UnicodeDecodeError` cannot propagate. `.stdout` is silently set to
`None` and the crash surfaces later, somewhere unrelated. Fixed at 23 call sites
across 11 files; `queue_head()` now reports a zero-length read as "cannot see
the queue" rather than treating it as empty, because those are opposite facts
that used to look identical. `test_subprocess_reads_are_utf8` fails if any
text-mode subprocess read omits `encoding=`, and was verified by reintroducing
the bug (it names `farm_worker.py:68`).

**The platform that runs the renders is not the platform that runs the tests.**
Only a static check catches this class.

## 2. "Too low quality" was a 1.5x upscale, measured

`render_t3` assembles onto a **720x1280** canvas. Every clip in the rejected
canon was **480x832** — blown up 1.5x to fill it. Soft is the arithmetic, not the
model's fault, and the entire 15-task queue was set to render 480x832 again: a
full night would have reproduced exactly what the founder turned down.

704x1280 had never completed on this card (`vid-720p-all` twice, `-c`, `-d`, `-e`
once each — five attempts, zero clips), so the question got **one beat, not
fifteen**, with `--offload`. It landed. Verified real before acting on it: 61
frames, 24fps, spatial sd 35.2 where noise would be ~74 and a flat frame 0.

At 704 wide the source is **near-native** for the canvas (2.3% up, not 150%).
Side-by-side of the same beat and seed in `cmp-b01.png`: defined hair strands,
sharp glasses frame, distinct keyswitches, against mush.

## 3. Offload is a 1.93x speedup — controlled, not inferred

Same beat 1, same seed, same 20 steps, back to back:

| | time |
|---|---|
| 480x832, **no** offload | 462s (and 467, 471, 475, 493 earlier) |
| 704x1280, **with** offload | **240s** |

Higher resolution, twice as fast, with resolution as the only *other* variable
and pointing the wrong way — so offload is the cause. This is the
**24.4/26GB residency** measured earlier: with the model pinned to the card the
renderer pages against itself, a silent multiplier that reads as a slow model.
`--offload` is `enable_model_cpu_offload()`, the supported path — **not** the
hand-rolled text-encoder eviction that corrupted every frame earlier the same
day, which is the trap this must never be confused with.

Consequence: the per-clip rate quoted to the founder and to dad earlier
(**208s per second of video**, from four 480x832 no-offload clips) is now stale
and roughly 2x pessimistic. Deliberately **not** revised here on one clip —
today already produced two speedups that turned out wrong or broken. The revised
median waits for the 14-clip set.

## 4. The shake fix worked; the shake was never camera translation

Measured with FFT phase correlation (this ffmpeg has no libvidstab), reporting
drift, direction reversals and non-rigid warp separately, because "how much
motion" is the wrong question — a pan reverses never, jitter reverses constantly.

| clip | global drift | reversals |
|---|---|---|
| b07 WAN, the founder's *"aggressively moving, very weird"* | 4.83px | 12% |
| the four shake-fixed clips | 0.00–0.11px | 0% |

Camera is genuinely locked now. **But the first control was wrong**: the `.POST`
set, picked as "the shaky ones", measures 0.00px too — it is the *frozen* set
(*"beat 9 literally doesn't move at all, not one pixel"*). Only b07 ever
measured as moving, and it is the one the founder named. Raw pixel deltas confirm
the fixed clips are not frozen: adjacent frames differ by 0.7–1.2/255 while
first-to-last differs by 4.8–13.7 — content animating under a locked camera,
which is the goal.

## 5. "No typing" was the direction, not the model

Beat 2's `motion.yaml` said *"the hooded man's silhouette shifts subtly"*. The
script says *"He types the last of it, fast, and stops dead. The spinner turns."*
The model rendered the direction faithfully: his hand is in the same raised
position at frames 0, 30 and 59 and the only change is a green glow. **The
steward wrote that direction.**

Audited all 15 against the script's own action line and fixed the four where the
direction contradicted **its own already-approved still**:

- **1, 2** — the stills have the keyboard and monitor in frame, so typing and the
  spinner are animatable without touching composition.
- **7** — the still is *already* a whip caught mid-motion, so asking for another
  whip restarted the gesture instead of finishing it. That is the *"aggressively
  moving, in a very weird way"*. Now a decaying rebound, which is what the
  script's "twitches" means and what a springy stem actually does.
- **10** — the beat exists to show the approaching thump as *"rings of light
  through soil"*, and the direction said **"no light rays"**, suppressing the one
  thing the audience must see. Now pulses the glow the still already has, while
  still refusing god rays.

## 6. The sidecar published two thirds of its provenance

§7.2 says every render publishes "model, prompt, cost". `write_sidecar` wrote
model, size, steps, seed, guidance and cost — and **not the prompt**. That gap is
why telling a bad direction from a bad model required re-running the pipeline to
reconstruct a string, and why anyone auditing the tree could not tell at all.
Prompt and negative now ship in every sidecar as literal block scalars,
round-trip verified against a prompt containing quotes, colons and Chinese.

## 7. And the death: no engine ever showed the fall (see D14)

Cycle 014 measured the anticlimax as a 9.5s near-silent hole in a beat running
double its scripted length. True, and now partly self-fixing since beat 4 becomes
one clip instead of two concatenated shots. But there is a second layer under it.

Beat 4's script writes three motions — *"A sharp breath in — the frame tips
sideways — the mug hits the floor before he does"*. Its approved still is
deliberately the aftermath: *"limp hand hanging straight down… **motionless**…
No face, no head, no full body, no horror, no blood, no standing."* The still owns
composition and i2v can only animate what is in frame, so every step behaves
correctly and **the fall is never depicted**.

Checked whether going licence-clean would cost us a fall that PixVerse had been
providing: it would not. `04-the-fall.PIXVERSE.mp4` is also a slow drift across
the limp hand and scattered papers — no fall in it either. **No version of beat 4,
in any engine, has ever shown him fall.** Recorded as **D14** with two
opposite-taste resolutions; changed nothing, because composition is R4.

## Lesson

Three of tonight's five findings were the steward telling the model to do the
wrong thing and then reading the result as a model limitation — the direction that
asked for a glow instead of typing, the direction that forbade the light rings the
beat exists to show, the queue that asked for the resolution the founder had just
rejected. The founder's notes have now been right about the cause, not just the
symptom, five times running. When a note and a measurement disagree, the
measurement is usually asking a slightly different question.

And the canary earns its keep every time: one beat answered the resolution
question that five previous whole-batch attempts had only failed at.
