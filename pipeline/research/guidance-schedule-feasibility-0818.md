# Can we schedule guidance per step? No — and not by anything worth doing at night

2026-08-18, night supervisor (v2) · zero GPU, zero spend · code read, not a render

**Answer: our wrapper cannot express a guidance schedule, and neither can the
pipeline underneath it. This is reported rather than hacked in, per the instruction
that came with the task. No sample was filed and no code was touched.**

---

## The question

`pipeline/research/video-samplers-steps-temporal-0818.md` and
`cfg-video-motion-negprompt-0818.md` point at the same lever: LTX's own shipped
distilled config uses a **guidance schedule** — CFG off early, spiking mid-denoise,
off again late — where our motion recipe uses a **flat 2.0**. The ALG finding says
the first denoising step effectively locks the image and suppresses motion, which
matches beat 14's clip with its 80 frozen frames, and matches the cold-open sweep's
dominant defect (four of six seeds hold still, then pop 2-3x in 1-4 frames — see the
correction appended to `pipeline/jobs/ep2-b01-growmotion-b-0818.yaml`).

So: is the knob reachable?

## What the code actually says

**Our wrapper — no.** `pipeline/ltx_i2v.py:1466`:

```
ap.add_argument("--guidance", type=float, default=1.0, help="distilled: CFG 1")
```

A scalar float. It reaches the pipeline at line 1148 as
`common = dict(guidance_scale=a.guidance, ...)` — one number, both stages of the
two-stage recipe, every step.

**The pipeline underneath — also no.** Checked against the installed build on the
card rather than assumed (`diffusers 0.39.0`,
`diffusers.pipelines.ltx2.pipeline_ltx2_image2video`):

```
guidance_scale: float = 4.0,
audio_guidance_scale: float | None = None,
```

Scalar in the signature, documented as `float`. There is no list form and no
per-step callback for it. A schedule would mean subclassing or patching the
pipeline's `__call__` to vary `guidance_scale` across the denoising loop — a change
to the code path **every render in this project goes through**, written at night,
to test a hypothesis. That is exactly the trade the instruction ruled out, and it is
the same shape as the 2026-08-04 mistake: building a mechanism instead of measuring
one.

## The near-miss worth recording

STG looked like a free proxy and is not, quite. `stg_kwargs()` already accepts
`spatio_temporal_guidance_blocks` as a **list**, and `ltx_i2v.py:1153` records that
upstream's own dev config uses per-step schedules —
`first_pass stg_scale [0,0,4,4,4,2,1]`, `second_pass [1]` — which is structurally the
very thing we want: **zero on the first steps, ramp mid, fall away**. If that shape
helps motion, it is already known to upstream.

But the list there is over transformer **blocks**, not timesteps, and our
`--stg-scale` is itself a scalar applied to both passes. Our own comment is explicit
that this was deliberate: one number, both passes, *"rather than a schedule we would
be inventing."* So STG gives us the right shape in upstream's config and the wrong
axis in ours. Reaching it needs the same kind of code change.

## Knobs that ARE exposed today, for whoever picks this up

`--steps` (default 8), `--guidance` (scalar), `--stg-scale` + `--stg-blocks`,
`--distilled-sigmas` (a flag — the sigma schedule is upstream's
`DISTILLED_SIGMA_VALUES` constant, not a parameter), `--two-stage`, `--frames`,
`--image-crf`, `--offload`. Notably **there is no `--shift`**: the flow-matching
timestep shift the research names as the other main temporal lever is not surfaced
at all, though `_scheduler_shift(pipe)` is read for the bench record, so the
scheduler has one and we only ever report it.

Of these, `--steps` is the one real one-variable experiment available with **zero
code change**, and the research ranks step count as a plausible cause of the
pop. That is a legitimate sample for a daytime lane to file against the cold-open
G1 defect.

## What this licenses

Nothing tonight. No sample was filed, because the one the task described cannot be
expressed without modifying `ltx_i2v.py` and probably the diffusers pipeline with
it. Two things are named for a daytime decision, both with the founder awake and
both needing their own bar:

1. **Guidance schedule** — requires a pipeline subclass. Worth doing only if the
   step-count sample below fails to move the defect, since it is far more invasive.
2. **Step count** — reachable now, one variable, no code change. The cheaper test of
   the same hypothesis and it should go first.

The beat-14 bar referenced in the task (`M1`–`M4` plus a first-80-frames motion-onset
clause) is **not written into any spec**, because writing a bar for a render that
cannot be produced would leave a bar in the tree with nothing to score.
