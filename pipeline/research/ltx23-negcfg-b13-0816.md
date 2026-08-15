# Beat 13, THE SHADE — the negative's content vs CFG's strength, and where period 2 lives

2026-08-16 · job `pipeline/jobs/ep2-b13-negcfg-0816.yaml` · commit `cff618e5` ·
one job, three renders, one crop, one encoder process · $0, local card.

**The two samples `68dbe136` asked for, and both answers are clean.**

- **The lever is CFG STRENGTH, not the negative's content.** Deleting the negative
  entirely while holding guidance at the control's 2.0 leaves the hold **exactly
  where it was**: period 3, 32.0 distinct pictures, 8.0 effective fps. The
  negative's thirteen clauses are innocent of the hold.
- **Guidance 1.5 does not reach period 2 either.** It reads period 3 / 32.0 /
  8.0, the same as 2.0. So the guidance→cadence relation is **not a ramp between
  32 and 48 pictures — it is a step, and the step edge sits in the interval
  (1.0, 1.5]**. Nothing lands between 32.0 and 48.0.
- Which sharpens the mechanism: what moved the hold at 1.0 is not "less
  guidance". It is the point where **the uncond pass stops running at all** —
  `do_classifier_free_guidance` is `(guidance_scale > 1.0)`. At 1.5 and 2.0 the
  pass runs and the cadence is period 3. At 1.0 it does not run and the cadence
  is period 2. Whether the flip is the branch itself or a magnitude effect that
  happens to bite just below 1.5 is **not settled by these two samples**; the one
  sample that would settle it is named at the bottom and was not fired.
- **Period 2 as a floor is still unresolved.** The floor test needed an arm that
  reached period 2 by a third route; 1.5 did not reach it at all, so it neither
  confirms nor falsifies the floor. The only two arms that have ever reached
  period 2 on this beat remain guidance 1.0 and the 9px blurred plate.

**And nothing here scales.** In all three new arms **the figure does not rock**.
The prompt's action clause asks him to rock slowly forward and back, and across
frames 0/16/32/48/64/80/96 every arm holds the same folded pose. 48 pictures of
the wrong thing is not a better beat than 32, and neither is 32 with a bigger
number beside it.

---

## 1. The numbers

`pipeline/hold_period.py` for period/strength/pictures/fps; trough-peak `depth()`
from `pipeline/vae_roundtrip.py`, imported, not re-implemented. Reference depths:
b13 0.038, STG arm 0.059, b06-DONE 0.181, b02-FIXED 0.431, a clean VAE round trip
0.971 — the metric is scale-free and reads a ±3% ripple like a freeze, which is
why it travels with every period.

| arm | guidance | negative | period | strength | **depth** | distinct pictures | eff. fps | mean pair diff | frame-mean luma swing | terminal freeze | render |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **A control** | 2.0 | full, 25 w / 38 tok | **3** | 0.923 | **0.038** | **32.0** | **8.0** | 3.188 | 2.94 / 255 | none | 236 s |
| **B** | 2.0 | **EMPTY**, 1 tok | **3** | 0.904 | **0.041** | **32.0** | **8.0** | 3.557 | 3.21 / 255 | none | 186 s |
| **C** | **1.5** | full | **3** | 0.930 | **0.028** | **32.0** | **8.0** | 5.127 | 10.08 / 255 | none | 182 s |
| prior art, `68dbe136` | 1.0 | dead: no uncond pass | 2 | 0.913 | 0.035 | 48.0 | 12.0 | 8.164 | **81.39 / 255** | none | 131 s |

**THE TERMINAL FREEZE IS SCORED SEPARATELY FROM THE HOLD** and there is none in
any arm: the last frame carrying new pixels is **96 of 96** in all four, with
**zero** bit-identical pairs anywhere in any clip. Beat 13 has the hold and no
wall — unlike the two bark clips on beats 06 and 10 that this lane's brief cites,
which is the whole reason the two failures are measured apart.

Both freeze detectors were given a positive control before any arm was read,
because a detector that has only ever returned "none" has not been shown to be
able to return anything else. `POSCTRL-exact-freeze-at-61.mp4` is the control's
first 62 frames followed by frame 61 repeated 35 times, re-encoded losslessly:
the exact detector reads **index 61, run 35**, and the soft detector reads the
same. A second control encoded at crf 18 shows why both exist — H.264 does not
always emit a skip for a repeated frame, so a provably frozen tail can decode
with max|A−B| up to 8 and MAD up to 0.024, at which the **exact** test reports no
freeze on a clip that is frozen. Hence the soft threshold of MAD < 0.05, sitting
between that 0.024 ceiling and the live pairs of these arms, which run 0.3–15.

## 2. Arm B: the negative is not inert — it is just not the cadence

The tempting misreading of "period unchanged" is "the negative did nothing". It
did plenty; it did nothing *to the hold*.

Against the control frame for frame, arm B is a **different clip**: mean
|B − control| over all 97 frames is **8.68 of 255**, and it diverges as it runs —
1.65 at f0, 8.35 at f48, 9.49 at f96. Two clips from the same seed, same plate,
same positive embedding, byte-identical positive conditioning (proved, see §5),
differing only in whether thirteen negative clauses were subtracted. The picture
moved. The cadence did not budge: period 3 either way, 32.0 pictures either way,
8.0 effective fps either way, depth 0.038 → 0.041.

So the anti-static negative — `still image, freeze frame` and eleven clauses
forbidding camera movement — **buys nothing against the hold it was presumably
added to fight**. That is worth knowing on its own terms. It is not an argument
for deleting it: it demonstrably changes the picture, and what it changes it to
is a taste question this lane does not own.

## 3. Arm C: more change per picture, not more pictures

Guidance 1.5 is further from the control than B is — mean |C − control| is
**17.24** — and each new picture differs more: mean pair difference 5.13 against
the control's 3.19, and the loud pairs in the mid-clip window read 15.6 / 14.2 /
19.5 against the control's 8.7 / 10.4 / 9.1. Its depth, 0.028, is the *lowest* of
every arm ever measured on this beat, meaning the quiet pairs are quieter still:
a **sharper** three-frame stutter, not a faster one.

That is the shape of the finding. Between 1.5 and 2.0, CFG magnitude modulates
**how much a new picture differs from the last**. It does not touch **how often a
new picture arrives**. Only crossing to 1.0 does that.

## 4. What the frames say, which is not what the counts say

`pipeline/research/EVIDENCE-negcfg-b13-0816.png`, three panels, and I opened them.

**Panel A, consecutive frames 44–51, head and torso.** Each tile carries its
full-resolution RGB MAD against the tile to its left, so the comb is visible
rather than asserted:

```
A control 2.0 + full neg   1.18  8.66  0.39  0.45 10.44  0.75  0.57  9.06   <- loud, quiet, quiet
B 2.0 + EMPTY negative     0.85 12.91  0.47  0.68 10.21  0.78  0.62 11.59   <- the SAME comb
C 1.5 + full negative      0.73 15.62  0.48  0.70 14.22  0.91  0.77 19.51   <- the SAME comb, louder
D 1.0, no uncond pass      0.61 13.56  0.59 20.75  0.70 27.22  1.29 16.01   <- alternating: period 2
```

A, B and C are the same picture three times over, then a new one — a period-3
comb you can count off the tiles. D alternates. Nothing subtle here, and the
three new arms are visually indistinguishable in cadence.

**Panel B, the pose at f0/16/32/48/64/80/96.** In A, B and C the scavenger is in
the identical folded pose at frame 0 and at frame 96 — knees up, arms around
knees, hands clasped, head tipped forward. He does not rock. What moves between
the loud pairs is the drawing being redrawn in place: the shadow across the skull
slides, the ear edge redraws, the grass behind the shoulder reshuffles. In D the
whole frame re-lights instead — f16 washed pale, f32 blown out, f64 green, f80
dark — and he still does not rock.

**Panel C, the per-pair difference series.** A, B and C are flat end to end (by
twelfths: control 4.6 / 2.9 / 3.8 / 4.6 / 3.2 / 4.0 / 3.7 / 2.9 / 4.3 / 4.5 /
2.7 / 4.8). D front-loads and dies: 8.7 → 13.6 → 16.0 in the first quarter, then
6.5 / 5.6 / 3.4 / **2.84** by the final twelfth — **below the control's 4.75**.
So "48 distinct pictures" for the 1.0 arm is a clip average taken over a clip
that stops moving; measured on the last eighth alone the control is the livelier
one. `68dbe136` reported this and it reproduces exactly on this harness.

**And the exposure number says what much of D's advantage is made of.** The
frame-mean luma SWING across the clip is 2.94 of 255 for the control, 3.21 for B,
10.08 for C — and **81.39 for D**. A third of the greyscale, on a clip where the
figure never moves. Removing the DC term does leave D's difference series larger
(9.92 DC-removed vs 8.89 raw, the same direction `68dbe136` measured), so it is
not *only* exposure; but a clip whose global brightness swings 81 levels while the
subject holds one pose is not a clip that found the motion.

## 5. Why these three clips are comparable, and the fifth identical control

**The control came back byte-identical again.**
`13-the-shade-NEG-full-cfg2p0-control.mp4` sha256
`42043851da4b246cfcd4e858cda828da992d0d48f15ef10d81d3a99c1ceb445a`, init
`210932b760f70ef34b97f41a28d1905ef5358e5f6982110c3f2440884b8b5199` — the fifth
independent job across four nights to reproduce both from an asserted source
plate through a fresh crop, encode and denoise. The bar written into the job said
a non-matching control would invalidate the comparison rather than be explained
away; it matched, and it also reproduces the published reading exactly (period 3,
strength 0.923, depth 0.038, 32.0 pictures, 8.0 fps) on a harness rebuilt from
`hold_period.py` and `vae_roundtrip.depth()` on this machine. The same harness
reproduces `68dbe136`'s guidance-1.0 arm exactly too (period 2, depth 0.035,
48.0, 12.0), so the comparison is not resting on two lanes' numbers agreeing by
description.

**One encoder process, and the difference between the two embeds files is proved,
not assumed.** Gemma loads once; `--jobs` carries two entries with the same
`prompt_file` and different `negative_file`. The job's `verify-embeds` step then
hashes the raw tensor bytes of both `.pt` files and refuses unless the positive
halves are byte-identical and the negative halves differ. It published:

```
prompt_embeds                  FULL 87b76c09cc5d8775  EMPTY 87b76c09cc5d8775  IDENTICAL
prompt_attention_mask          FULL aa37b27eb329fac1  EMPTY aa37b27eb329fac1  IDENTICAL
negative_prompt_embeds         FULL d9315dc3a2590609  EMPTY 9989bd17efb4f47c  DIFFERS (expected)
negative_prompt_attention_mask FULL f9717b8d3ce844a9  EMPTY e585d1393cd6fee9  DIFFERS (expected)
```

So arm B's variable is bounded to the negative half of one tensor file. Not "we
believe Gemma is deterministic" — the positive halves are the same bytes.

**An empty negative is upstream's own unconditional embedding, not a hack.**
diffusers 0.39.0's `LTX2ImageToVideoPipeline.encode_prompt` runs
`negative_prompt = negative_prompt or ""`, inspected on the box before the job was
written. An empty negative file therefore produces exactly what upstream produces
when no negative is given at all, with the uncond pass still running at 2.0.

**The argv diff, asserted by the generator rather than eyeballed.** Three renders
built from one function whose only recipe parameter is guidance:

```
control vs empty-neg : recipe flags differing = NONE  (only --jobs, plumbing)
control vs cfg 1.5   : recipe flags differing = ['--guidance']
control vs ep2-b13-guidance-0815's render-control : IDENTICAL modulo plumbing
```

**Measured on the real tokenizer before firing**, not estimated: positive 37 words
/ **58 tokens** (sha `638b5c22`, matching the guidance job's payload byte for
byte), full negative 25 words / **38 tokens** (sha `50fb304c`), empty negative
**1 token**, against a 1024 limit.

## 6. Two corrections and one hole, all found in passing

**A timing claim of `68dbe136`'s needs trimming.** That lane reported guidance 1.0
as "45% faster (238s → 131s) because CFG 1.0 runs no uncond pass". This job ran
three renders in one process sequence and the *first* one is systematically slow:
control (2.0, full negative) 236 s, then arm B — **the identical recipe** bar the
negative — 186 s, then arm C 182 s. Roughly 50 s of that 107 s gap is position in
the job, not the uncond pass. The real saving from dropping the uncond pass is
nearer 131 vs 186, about **30%**. The direction stands; the number was inflated by
run order.

**The sidecar caveat is fixed.** `ltx_i2v.py` appended
`[unused: guidance 1.0 ... changed no pixel]` to **every** sidecar with a
non-empty negative regardless of guidance, so every 2.0 render published a line
claiming its negative was inert. It is text and never touched a pixel. The
2026-08-15 lane found it and left it because another lane held the file;
`ltx_i2v.py` was clean tonight, so `sidecar_negative(negative, guidance)` now
attaches the caveat only when `guidance <= 1.0` — upstream's own truth condition —
and a test pins both directions, the 1.0 boundary, the empty-negative case, a
string-typed guidance, and that the caveat text exists in exactly one function.

**A real §7.2 hole, NOT fixed here, named for whoever owns the render path next.**
Every clip in this job published `prompt: ''` and `negative: ''` in its sidecar.
That is not this job's doing: on the two-stage `--jobs` path the render stage
receives its text only as embeddings, so `a.prompt`/`a.negative` are empty and the
sidecar has nothing to record. The consequence is concrete — **arm B's sidecar and
the control's sidecar are indistinguishable**, though they were rendered from
different negatives. Provenance for these three clips lives in the job spec and in
the published `b13-embeds-verify.txt`, not in the sidecars. The minimal honest fix
is for the render stage to record the embeds path and its sha256, and ideally to
carry `prompt_file`/`negative_file` forward from the encode entry; it touches the
sidecar schema, so it belongs to a lane that owns that change rather than to this
one.

## 7. What is now eliminated, and the one sample that would go next

Eliminated by measurement on beat 13, none of it re-derived here: prompt wording
(five wordings, three seeds); the init plate as an onset lever; the 13-latent
count; the whole VAE/decode side; STG at upstream's recommended 1.0/[28]; the
200-word prompt ceiling (premise wrong — 37 words / 58 tokens); and now **the
negative's content**, and **CFG magnitude anywhere in [1.5, 2.0]**.

What has ever moved the cadence: guidance **1.0**, and a 9px motion-blurred init
plate. Two arms, both landing on period 2 / 48.0 / 12.0, neither making the figure
act.

**The single next sample, named and deliberately not fired: guidance 1.05 or
1.1.** It is the only thing that separates "the cadence flips when the uncond pass
stops running" from "CFG magnitude matters, and the effect simply bites below
1.5". Above 1.0 the negative stays alive and the uncond pass still runs, so a
1.1 arm that reads period 3 makes the flip a property of the `> 1.0` branch, and
one that reads period 2 makes it a magnitude effect with a knee between 1.1 and
1.5. Either answer changes what a fix would look like. It is one sample, it is
not fired here, and the card is not idle — five of another lane's jobs are queued
behind this one.

**The standing caution stands.** In every arm measured, neither figure rocks. A
metric is a filter, never a verdict; the cold read decides, and the cold read on
all three of tonight's arms is a boy sitting perfectly still while the drawing
around him is re-inked.

---

### Provenance

Model `diffusers/LTX-2.3-Distilled-Diffusers`, bf16, seed 20260815, 704x1280,
97 frames @ 24 fps, two-stage 8@352x640 + 3@704x1280, distilled sigmas,
image-crf 33, sequential offload, STG unpassed on every arm. Plate
`13-the-shade-ipa-r0-w015-s0.png` sha256 `1745a491…`, asserted by the crop step
before anything was written. Node `002b-first-citizen`, script `002b-t0-c`,
`approved_by: founder` 2026-08-03. Three silent motion takes on an approved node;
no voice synthesis, no episode assembly. cost_usd 0 — local card, no provider.

Published: `C:\banyan-farm\courier-box\farm-out\ep2-b13-negcfg-0816\` with a
sha256 manifest. Camera-scale numbers are deliberately absent: the chained-NCC
method rails to its search boundary when the fits fail, so the only registration
statistic quoted here is consecutive-frame ncc, which is exact.
