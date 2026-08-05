# Model comparison — the living table

**Opened 2026-08-04** at Oleg's request: one place where every candidate video
model's render time, memory, parallelism, licence and *measurement status* sit
side by side, so nobody quotes an estimate as a measurement again. Rows are
appended per sample, not rewritten. Sources per row; see §3 for the update rule.

**THE OPTIMISATION TARGET, Oleg 2026-08-04: maximum seconds of video per second
of real time.** Not single-clip latency — *throughput*, which is why the table
carries a `s(video)/s(wall) @ batch` column and why every model is measured
batched rather than one clip at a time. Two disciplines come with it, and the
second is the one that keeps the metric honest:

- **A throughput row only counts at a quality level Roman has approved.** A fast
  model with a rejected look scores zero. Nothing here promotes itself by being
  quick.
- **Record the batch and the mode with the number, always.** Both forms of the
  figure are useful and they invert each other — `s(video)/s(wall)` for
  throughput, `s(wall) per 1s video` for cost — so cells state whichever they
  measured and, where it is cheap, both.

Every model is also measured in **two modes** (Oleg, 2026-08-04): a **preview**
recipe cheap enough for the iterate-in-minutes review loop, and **production**.
The mode column is not decoration — *a preview clip judged as production kills a
model unfairly, and the reverse ships junk.*

Reading rules, all load-bearing:

- **VRAM cells carry their offload strategy.** A `sequential-offload` peak
  measures the offload strategy, not what the card can hold, and is **not
  comparable** to a resident or `model_cpu_offload` row.
- **Nothing here is a quality verdict.** Defect *counts* are measurements and
  belong in the table; good/bad is Roman's (R4).
- **Host RAM cells say what else was running.** The 2026-08-04 5B rows were
  measured with a 114GB download in flight, whose page cache Windows counts as
  in-use-but-reclaimable, so those figures are *upper bounds on a busy box*, not
  the model's own footprint.
- **NEVER PLAN A LOAD BY WEIGHT SIZE. Measured 2026-08-04: loading AnimeGen's two
  28.58GB experts took ~128.7GB of commit charge for ~40GB of live weights — a
  ~3x retained overhead.** The cause is the runtime fp8 cast: it allocates the fp8
  copies while the bf16 storages it replaces are still committed, and
  `gc.collect()` returns them to the process heap but not to the OS. Windows then
  grew the pagefile 130.4 → 133.0 → 140.6GB and the first denoise step died 13GB
  short. So an A14B "fits in 64GB because 2 x 28.6 = 57GB" is wrong by a factor,
  and the fix is not a bigger pagefile: it is to never materialise bf16 in the
  render process (bake fp8 experts to disk in processes that exit). Any row
  claiming an A14B-class model fits must cite a measured **commit** figure, not
  the weight sizes.

## 1. The table

MEASURED rows first, real numbers. SCHEDULED rows carry `—` and their T-number
from `ACTION-PLAN.md §1`. Times are seconds per clip unless a per-beat figure is
given (per-beat includes the ~67s fixed cost). Parallelism column: see §2 — the
answer is one render per card for every row, so the cell records what *else* the
host can still do during that render.

| Model + build | Recipe | Mode | Time | Throughput s(video)/s(wall) @ batch | Peak VRAM | Peak host RAM | Parallel | Licence | Measurement status | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| **diffusers/LTX-2.3-Distilled-Diffusers, bf16** | two-stage **on-recipe**: 8 steps @352x640 → 2x latent upsample → 3 steps @704x1280, explicit sigmas, guidance 1.0, 65f @24fps = 2.708s | production (two-stage, on-recipe) | **108.1s sample / 120s wall** (stage 1 62s @7.8s/it, stage 2 31s @10.5s/it; remainder = upsample + setup) | **0.0251 s(video)/s(wall) @b1** = 39.9s wall per 1s video (2.708s of video / 108.1s sample) — DERIVED-FROM-OURS, the row states its own 65f @24fps so the denominator is not invented | **4.1GB torch / 2.5GB device of 26GB** — LABEL: **sequential-offload**, measures the offload strategy, not card capacity | **60.8GB phys / 67.1GB commit of 68.1GB** | 1/card, and **host-exclusive** — this render evicted the farm worker on the 64GB box | LTX-2 Community License Agreement — **CANDIDATE** under watch-only per D16 (per-post AI label, never a contributor-facing service, one founder-screened sample) | **MEASURED-BY-US 2026-08-04**, $0. Clip clean: no issue-#37 corruption (saturation 0.264, no channel cast, **0/64 frozen frames**) | `SAMPLE-ltx23-b01.mp4.meta.yaml`, `pipeline/ltx_i2v.py` |
| Wan 2.2 TI2V-5B, diffusers bf16, `model_cpu_offload` | 704x1280, 14 steps, guidance 5.0 | production | **188s render / 248s per beat** (62 min / 15 beats) | no data — the row does not record its frame count, so s(video) has no denominator | 22.9GB of 25.7GB — `model_cpu_offload` | no data | 1/card; host RAM unmeasured, so co-residency unproven | Apache-2.0, output rights disclaimed — CLEAR | MEASURED-BY-US | `STATE.md:604`, `DECISION.md §2` |
| same | 704x1280, 20 steps | production | **240s / 300s per beat** | no data — as above | no data | no data | as above | as above | MEASURED-BY-US | `STATE.md:605` |
| same — **cost decomposed** | 704x1280 | — | **8.67s/step marginal + 66.7s fixed per clip** — supersedes the "13.4s/step" figure, which was `188/14` and contaminated by the fixed addend (the 20-step run gives 12.0 for the same quantity) | — | — | — | — | — | DERIVED-FROM-OURS (two-point fit on the two rows above; corroborated by `video_task.py:817` and STATE.md's "~12 min/episode" batch saving) | `DECISION.md §3` |
| same, **no** offload | 480x832, 20 steps | production | 462s (also 467/471/475/493) | no data — as above | 24.4GB of 26GB — **paging against itself** | no data | 1/card | as above | MEASURED-BY-US; the controlled evidence that offload is a 1.93x *win* | `pipeline/loop/cycle-015.md` |
| Wan 2.2 TI2V-5B, official reference | 720P, 5s/121f, 50 steps, RTX 4090 24GB | production | <540s | no data — 5s/121f stated, but <540s is an upper bound, not a measurement | no data | no data | — | Apache-2.0 | MEASURED-BY-WAN-AUTHORS (our fit extrapolates ours to ~500s at 50 steps) | Wan2.2 model card + README |
| **TI2V-5B, T1-A/B — the production recipe, `flow_shift` 5.0** (diffusers 0.39.0 bf16, `model_cpu_offload`, torch 2.11.0+cu128) | 704x1280, 61f @24fps = 2.542s, 14 steps, guidance 5.0, **UniPC `flow_shift` 5.0 — the value the repo's `scheduler_config.json` already ships**, production prompt+negative (F recipe, `no_anchor`), seed 20260732, beat 1 | production | **168.6s sample / 169.8s wall** (12.05s/step — FIRST clip after the load, and it carries the warm-up: the other five settled at 10.5s/step) | **0.0151 s(video)/s(wall) @b1** = 66.3s wall per 1s video (settled clips: **0.0173**, 57.6s per video-s) | **14.4GB torch of 25.7GB — `model_cpu_offload`** | 52.7GB phys / 80.3GB commit of 68.1/130.4GB — **with the 114GB A14B download co-resident**, so an upper bound | 1/card; the 114GB fetch ran throughout and neither job died — the 5B does **not** need a host to itself the way the LTX row does | Apache-2.0, output rights disclaimed — CLEAR | **MEASURED-BY-US 2026-08-04**, $0. **T1's A and B coincide**: the shipped `flow_shift` IS Alibaba's 720p 5.0. Motion (repo metric, `collect_farm.py --measure`): median **1.16**, **0/60** barely-moving pairs | `bench-T1T2T3/T1-shift5.0.mp4.meta.yaml`, `bench-T1T2T3/bench-t0.json` |
| same — **T1-C, `flow_shift` 3.0** | as above, `flow_shift` 3.0 (Alibaba's 480p value, FastWan's `flow_shift`) | production | 149.7s sample / 150.7s wall (10.69s/step) | 0.0170 s(video)/s(wall) @b1 = 58.9s per video-s | 14.4GB of 25.7GB — `model_cpu_offload` | 40.6GB phys / 69.8GB commit — download co-resident | as above | Apache-2.0 | **MEASURED-BY-US 2026-08-04**, $0. Motion: median **0.97**, 0/60 barely-moving. Timesteps ran `[999, 975, 947, 916, 882, 843, 800, 750, 692, 625, 546, 451, 334, 189]`, i.e. **6 of 14 steps above t=900** | `bench-T1T2T3/T1-shift3.0.mp4.meta.yaml` |
| same — **T1-C', `flow_shift` 8.0** | as above, `flow_shift` 8.0 (kijai's shipped 5B I2V example) | production | 146.5s sample / 147.6s wall (10.46s/step) | 0.0173 s(video)/s(wall) @b1 = 57.6s per video-s | 14.4GB of 25.7GB — `model_cpu_offload` | 38.5GB phys / 69.7GB commit — download co-resident | as above | Apache-2.0 | **MEASURED-BY-US 2026-08-04**, $0. Motion: median **1.18**, 0/60 barely-moving. Timesteps `[999 … 384]`, **9 of 14 above t=900** | `bench-T1T2T3/T1-shift8.0.mp4.meta.yaml` |
| same — **T2, `画面` restored to `NEG`** | T1-A/B exactly, plus one appended negative term. Verified a pure append: 618 → 622 chars, same prefix, nothing reordered. **Not** combined with `--no-shake-neg` | production | 147.9s sample / 149.0s wall (10.56s/step) | 0.0172 s(video)/s(wall) @b1 = 58.2s per video-s | 14.4GB of 25.7GB — `model_cpu_offload` | 38.5GB phys / 69.2GB commit — download co-resident | as above | Apache-2.0 | **MEASURED-BY-US 2026-08-04**, $0. Motion: median **0.83** against the baseline's 1.16, 0/60 barely-moving. One clip, one seed — a direction, not a finding | `bench-T1T2T3/T2-neg-huamian.mp4.meta.yaml` |
| same — **T3, motion-only prompt** | T1-A/B, positive replaced by present-progressive motion only, statics stripped, no camera invention, 36 words: *"…his hands are hammering the keys, fingers striking rapidly in large strokes, wrists lifting and dropping, the monitor glow pulsing over them"*. **STYLE prefix kept** so the clip is a one-variable delta | production | 148.9s sample / 149.9s wall (10.64s/step) | 0.0171 s(video)/s(wall) @b1 = 58.6s per video-s | 14.4GB of 25.7GB — `model_cpu_offload` | 41.9GB phys / 69.3GB commit — download co-resident | as above | Apache-2.0 | **MEASURED-BY-US 2026-08-04**, $0. Motion: median **1.05**, 0/60 barely-moving | `bench-T1T2T3/T3-motion-only.mp4.meta.yaml` |
| same — **T3b, empty prompt** | T1-A/B with `prompt=""` | production | 146.5s sample / 147.6s wall (10.47s/step) | 0.0173 s(video)/s(wall) @b1 = 57.6s per video-s | 14.4GB of 25.7GB — `model_cpu_offload` | 36.9GB phys / 69.2GB commit — download co-resident | as above | Apache-2.0 | **MEASURED-BY-US 2026-08-04**, $0. **NOT Alibaba's empty-prompt mode** — diffusers has no system-prompt routing, so this is a literally empty string, and the row must never be read as testing their "bring the image to life" brief. Motion: median **0.72**, 0/60 barely-moving | `bench-T1T2T3/T3-empty-prompt.mp4.meta.yaml` |
| same — **batch 2, the throughput probe** | T1-A/B's recipe exactly at 2 latents through one set of weights: 704x1280, 61f @24fps = 2.542s per clip, 14 steps, guidance 5.0, UniPC `flow_shift` 5.0. Slot 0 repeats **seed 20260732** as the batch-fidelity check, slot 1 takes 20260733 | production | **764.7s sample** for 2 clips (**54.62s/step**) against b1's 12.05 — **4.53x b1's per-step cost for 2x the output** | **0.0066 s(video)/s(wall) @b2** = **150.4s wall per 1s of video** (382.3s per *clip*) — against b1's 0.0151, i.e. **0.44x b1** | **23.5GB torch of 25.7GB (91.4%)** — `model_cpu_offload`; **+9.1GB** over b1's 14.4GB | 54.4GB phys / 54.4GB commit of 68.1/130.4GB — psutil sampler; the two coincide because swap use read 0 at every sample | 1/card | Apache-2.0, output rights disclaimed — CLEAR | **MEASURED-BY-US 2026-08-05**, $0. **Batching the 5B is strictly worse than running it serially on this card.** The fidelity gate passed decisively — slot 0 against the b1 reference differs by less than re-encoding alone, and the two slots diverge from each other properly, so this is a real throughput result and not a batch that silently rendered one clip twice. Corroborated independently in the *preview* recipe by the box's own rows: **16.43 → 110.36 s/step b1 → b2**, same direction, steeper | `SAMPLES/batch-bench.jsonl`, `SAMPLES/ti2v5b-production-b2-s20260732.mp4.meta.yaml`, `SAMPLES/ti2v5b-modes.jsonl` |
| TI2V-5B + **`shift` sweep** (baseline / 5.0 / 8.0) | 704x1280, 14 steps, 3 clips, one seed | — | — (expect ~248s/beat) | — | — (expect 22.9/25.7GB) | — | — | Apache-2.0 | **SUPERSEDED — measured 2026-08-04**, see the three T1 rows above. Its own expectations were both wrong: the peak is 14.4GB not 22.9GB, and the "baseline" was already 5.0 | `ACTION-PLAN.md §1 T1` |
| TI2V-5B + `画面` restored to `NEG` | 704x1280, 14 steps, alone (not with `--no-shake-neg`) | — | — | — | — | — | — | Apache-2.0 | **SUPERSEDED — measured 2026-08-04**, see the T2 row above | `ACTION-PLAN.md §1 T2` |
| TI2V-5B + motion-only prompt contract | statics stripped, ≤100 words | — | — | — | — | — | — | Apache-2.0 | **SUPERSEDED — measured 2026-08-04**, see the T3 and T3b rows above | `ACTION-PLAN.md §1 T3` |
| TI2V-5B + **SageAttention 2.2.0 sm_120** | 704x1280, 14 steps, separate venv (wheel pins the torch line) | — | — (**~160s/beat CLAIMED-BY-mobcat40**, ~35%, measured on an RTX 5090 Laptop 24GB) | — | no data | no data | 1/card | tooling: Apache-2.0 pending confirmation | **SCHEDULED — T4.** Claim is on our exact card and still a claim | `ACTION-PLAN.md §1 T4`, `DECISION.md §2` |
| TI2V-5B + **FastWan 3-step LoRA** (rank 128, bf16) | 3 steps, guidance 1, flow_shift 3, 121f @704x1280 — no new base weights | — | — (fit predicts ~92s) | — | — | — | 1/card | LoRA needs `licence_gate.py` before download | **SCHEDULED — T5.** At guidance 1 the whole negative prompt goes inert; distill LoRAs are documented to slow motion | `ACTION-PLAN.md §1 T5` |
| **`aidealab/AnimeGen-I2V`** (Wan2.2-I2V-A14B finetune; per-expert fp8 layerwise casting, `model_cpu_offload`, **text encoder evicted to its own process**) | **4 steps, guidance 1.0, FlowMatchEuler shift 5.0 (not 3.0), boundary 0.900 (inherited from the base `model_index`, verified)**, motion-only prompt, Lightning LoRAs both experts @1.0, seed 20260732 | **preview** — 33f @24fps = 1.375s, **480x832** (AnimeGen's own example size is 832x480; for I2V the size arg is a max-AREA budget) | **89.6s sample** (22.4s/step), after a **240s load** | **0.0153 s(video)/s(wall) @b1** = 65.2s per 1s video | **17.9GB torch of 25.7GB** — `model_cpu_offload` + fp8 layerwise | **66.7GB phys / 119.1GB commit of 68.1/130.4GB** — the binding constraint, see the T6 note below | 1/card, and effectively **host-exclusive**: only the 114GB download shared the box, and load peaked at 92% memory load | AnimeGen Apache-2.0 with a real stock LICENSE file; **the Lightning LoRAs ship NO LICENSE file — UNVERIFIED, evaluation render only, publication gated** | **MEASURED-BY-US 2026-08-04**, $0 — **the first AnimeGen clip this box has ever produced** (five prior attempts died). No corruption signature: saturation 0.636, channel means R44/G26/B68, std 53.8. Motion: median 0.52, 0/32 barely-moving | `SAMPLES/animegen-preview-b1-s20260732.mp4.meta.yaml` |
| same — **batch 2, the throughput optimum** | as above, 2 latents through one set of weights; slot 0 repeats seed 20260732 as the batch-fidelity check, slot 1 takes 20260733 | preview (480x832, 33f) | **124.6s sample** for 2 clips (31.1s/step) — 2x the output for **1.39x** the time (124.6/89.6) | **0.0221 s(video)/s(wall) @b2** = 45.3s per 1s video — **1.44x b1** | **19.7GB of 25.7GB** — only **+1.8GB** over b1, because with `model_cpu_offload` the streamed weights dominate and a second latent is nearly free | 66.7GB phys / 119.1GB commit (unchanged — batching costs VRAM, not host) | as above | as above | **MEASURED-BY-US 2026-08-04**, $0. **Batch fidelity holds**: at the same seed, b2 slot 0 matches b1 on mean frame-difference (0.62) and max (1.63) to two decimals, median 0.55 vs 0.52 — near-identical, not bit-identical, consistent with batched-matmul non-determinism | `SAMPLES/animegen-preview-b2-s20260732.mp4.meta.yaml` |
| same — **batch 4, where scaling stops** | as above at 4 latents | preview (480x832, 33f) | **601.3s sample** for 4 clips (**150.32s/step**) against b2's 31.1 and b1's 22.4 — **4.83x** b2's per-step cost for 2x the output | **0.0091 s(video)/s(wall) @b4** = 109.3s per 1s video — **WORSE than batch 1's 0.0153** | **23.2GB of 25.7GB (90.3%)** — VRAM pinned near the ceiling for the whole run | as above | as above | as above | **MEASURED-BY-US 2026-08-04**, $0 — figures corrected 2026-08-05, see the correction note below. **What stopped scaling: VRAM, via driver spill, not an OOM.** At ~90% the WDDM sysmem fallback pages to host RAM instead of raising — the invisible tax `ACTION-PLAN §1 T0`'s control-panel item exists to convert into a legible failure. **b2 is the optimum at this config; b4 is a false economy** | `SAMPLES/animegen-bench.jsonl`, `SAMPLES/animegen-preview-b4-s20260732.mp4.meta.yaml` |
| same — **PRODUCTION geometry, b1** | the b1 recipe exactly (4 steps, guidance 1.0, shift 5.0, boundary 0.900, Lightning LoRAs both experts @1.0, motion-only prompt, seed 20260732) at **704x1280** | **production** — 61f @24fps = 2.542s | **545.5s sample** (**136.38s/step**) | **0.0047 s(video)/s(wall) @b1** = **214.6s per 1s video** — 3.3x the preview row's 65.2s for 1.85x the pixels-times-frames | **23.2GB of 25.7GB** — `model_cpu_offload` + fp8 layerwise | 66.7GB phys / 119.1GB commit of 68.1/130.4GB | as above | as above | **MEASURED-BY-US 2026-08-04 23:30:14**, $0. **Recovered 2026-08-05**: the night's `scp` ran ~4 minutes before this run exited, so the clip and sidecar were left on the box and this row was missing from the first pass of the table. No screening verdict — R4, and it has not been screened | `SAMPLES/animegen-production-b1-s20260732.mp4.meta.yaml`, `SAMPLES/animegen-bench.jsonl` |
| same — **the load path is the real T6 gate** | two 28.58GB bf16 experts, loaded and cast **one at a time** (load hi -> attach its Lightning adapter in bf16 -> cast fp8 -> gc -> then lo), which is ~14GB below the pipeline-level LoRA load `wan_i2v.load_animegen` performs | n/a — load only | **240s** | — | — | **128.7GB commit with the text encoder resident; 115.6GB without it.** ~40GB of live weights against ~128GB of commit charge: the runtime fp8 cast **retains** the bf16 storages it replaces, and `gc.collect()` does not return them to the OS | host-exclusive during load | as above | **MEASURED-BY-US 2026-08-04.** Attempt 1 loaded fine and then died at step 0 (commit 140.6/140.6GB, 1.7GB free physical, watchdog abort rc=9). Attempt 2 differed only by evicting the text encoder into its own process, which freed **13.1GB** and let the render proceed. **Consequence for T7/T8: the same wall, and the fix is to bake fp8 experts to disk in isolated processes so nothing bf16 is ever resident** | `bench-a14b.log`, `SAMPLES/animegen-summary.json` |
| stock `Wan2.2-I2V-A14B` + lightx2v Lightning LoRAs (rank 64, **both at 1.0**) | 4 steps, explicit sigmas `[1.0, 0.9375, 0.8333, 0.625]`, shift 5.0, guidance 1 | — | no data | — | no data — A14B-class, as above | no data | 1/card | Apache-2.0 | **SCHEDULED — T7**, only if T6's look fails | `ACTION-PLAN.md §1 T7` |
| `IndexTeam/Index-anisora` V3.2 (stock Wan2.2-I2V-A14B arch) | 8 steps native, no LoRA, shift 5, guidance 1, boundary 0.900, 81f @16fps, 8n+1 frames, `motion score` token | — | no data | — | no data | **hard gate: download is fp32, ~57GB/expert (~126GB the pair); needs bf16/fp8 conversion on disk before the first run** — one fp32 expert nearly fills 64GB | 1/card, host-exclusive by construction | **"Apache-2.0 plus bilibili Model License Agreement additional restrictions"** — not plain Apache-2.0; five of six restrictions are fine-tuning-scoped, clause 4 (indemnity) is not. V3.x only, never the 5B folders | **SCHEDULED — T8**, cut if the conversion has not already happened. Their own benchmarks put it *below* vanilla Wan on motion (VBench Motion 45.59) | `ACTION-PLAN.md §1 T8`, `§4.2` |
|---|---|---|---|---|---|---|---|---|---|---|

### Correction, 2026-08-05 — the b4 row was a mid-run projection

**The batch-4 row above carried estimated numbers under a `MEASURED-BY-US` tag,
which is the exact promotion §3 rule 2 forbids.** It was written at **23:20:37**
while the b4 run was still sampling and read 99.3s/step, "projected ~0.014
s(video)/s(wall)" and 24.1GB (94%). The run did not exit until **~23:25**. The
machine-readable artifacts it should have been copied from — `animegen-bench.jsonl`
and the four b4 `*.mp4.meta.yaml` sidecars — were correct all along and disagreed
with it: **601.3s sample, 150.32s/step, 0.0091 s(video)/s(wall) = 109.3s per video
second, 23.2GB of 25.7GB = 90.3%.** The row now carries those. Nothing about the
finding changes — b4 is still a spill and still worse than b1 — only the size of
the cliff, which got *steeper*, not shallower. The mechanism paragraph survives
unedited; it was reasoning about a real spill, just at 90% rather than 94%.

Two things this is worth keeping visible for. **(1)** The failure mode is not
"someone guessed"; it is a figure read off a progress line mid-run and then
committed with the tag reserved for finished measurements. Rule 2's guard is a
*sidecar exists*, and one did not exist at 23:20:37. **(2)** `COMPARISON.html`
had been showing the jsonl figures beside a note that the document disagreed;
that note is now a past-tense record of a resolved conflict, not an open one.

**Also missed on the night, and now recovered: the AnimeGen PRODUCTION row.**
`animegen-production-b1-s20260732.mp4` — 704x1280, 61f, the 4-step LoRA recipe —
rendered on the box at **23:30:14 on 2026-08-04** and was absent from this table
because the `scp` that pulled the night's artifacts ran about four minutes
*before* the run exited. The clip and its sidecar came back on 2026-08-05 and the
row above was appended from that sidecar per rule 1: **545.5s sample,
136.38s/step, 0.0047 s(video)/s(wall) = 214.6s per 1s of video, 23.2GB of
25.7GB.** Worth stating plainly because it is the first production-geometry cost
we have for this model: **AnimeGen at production geometry is ~3.7x the wall cost
per second of video of the 5B's settled 57.6s**, and that trade is a screening
question, not a throughput one.

The transferable lesson is the copy race rather than the clip. **A pull scheduled
against a wall-clock guess instead of against the producing process exiting will
silently return a partial night**, and a run whose artifacts were fetched too
early is indistinguishable from a run that never happened — which is exactly how
this row went missing while every other row from the same session landed.

### 2026-08-05 — batching the 5B, and the batch-4 that took the host down

Three probes were authorised to widen the batch-scaling section past AnimeGen.
Two of them produced something. This is what each one is worth.

**b2 answered the question, and the answer is no.** The row above is the whole
finding: **0.44x b1's throughput.** Not a plateau, not a wash — a loss. Every
figure moved the wrong way at once (54.62s/step against 12.05, 150.4s per
video-second against 66.3, 23.5GB against 14.4), and the *preview* recipe says
the same thing harder: **16.43 → 110.36 s/step**, a 6.7x per-step cost for twice
the output. AnimeGen's b2 was the optimum on this same card; the 5B's is a
regression. The difference is headroom — AnimeGen b1 already streams its weights
through `model_cpu_offload` at 17.9GB, so a second latent cost it +1.8GB, while
the 5B's second latent cost +9.1GB and put the card at 91.4%.

**b4 did not produce a row, and must not be given one.** The run **bugchecked
the host** at **06:07:05 local on 2026-08-05** — Kernel-Power 41, EventLog 6008 —
the box's *second* unclean reboot that day. It had completed **2 of 14 steps at
~118-122s/step** when it died. At the moment of death: GPU **24102 MiB of 24463
(98.5%)** at 100% utilisation, host commit pinned at its **~69GB** ceiling while
physical was being *reclaimed* 33 → 19GB — the WDDM sysmem-fallback thrash
AnimeGen's b4 showed as a slowdown, here escalated to taking the machine with it.
Telemetry: `probe-5b-b4.log`.

There is no sidecar, no clip, and no finished sample, so **rule 1 leaves it out
of the table** and rule 2 forbids promoting the two step times into one. It is
recorded here, in prose, with the log named — the same treatment the b4 mid-run
projection should have had on 2026-08-04.

**The series is superlinear the whole way: 12.05 → 54.62 → ~118 s/step at b1 →
b2 → b4.** So: **b4 is DEAD on this card. Do not re-run it.** Reopening that is
founder-reserved — it costs a bugcheck, and the second one in a day is what it
cost this time.

**The third probe, LTX at b2, never started.** `pipeline/ltx_i2v.py` could not
render at all: commit fab4632 added the `--batch` body without declaring the
flag, so every `--stage render` raised `AttributeError` at the defaults. Fixed
2026-08-05 along with a static test that fails against that commit's file
(`test_argparse_declares_every_flag_it_reads`). The probe runs after the fix
lands; there is no LTX batch row until it does.

**One unit correction that touches every "per 1s video" figure in this file.**
`wan_i2v.py`'s bench row wrote `compute_per_video_s` as seconds per *clip*
(`sample_s / batch`) while its own sidecar, the AnimeGen file and the 5B-modes
file all wrote seconds per *second of video*. Both quantities are true; only one
matches the column's name. `batch-bench.jsonl`'s b2 row therefore says 382.3
where the same run's sidecar says 150.4. **The written rows stand — they are
measurements and are not edited** — the renderer now writes the per-video-second
form, and `COMPARISON.html` derives that cell from `sample_s / video_s` so old
and new rows read alike. The table above states both numbers for the b2 row and
labels which is which.

### Open observations on the measured 5B T1/T2/T3 rows

Measured anomalies only — six clips, one seed each, and nothing here is a verdict.

1. **The 5B does not ship the scheduler the plan assumed.** `ACTION-PLAN §1 T0`
   asks for `pipe.scheduler.config.shift`; there is no such key. The repo's
   `scheduler_config.json` ships **`UniPCMultistepScheduler`** (multistep bh2
   predictor-corrector, `solver_order` 2, `predict_x0`, `use_flow_sigmas`), whose
   knob is **`flow_shift`, already set to 5.0** — Alibaba's own 720p value. So
   "we never set shift" was true and harmless: we inherited the right one. `shift`
   and `set_shift()` exist only on `FlowMatchEulerDiscreteScheduler`, and calling
   the latter here would have silently done nothing. Set it with
   `UniPCMultistepScheduler.from_config(cfg, flow_shift=X)`; verified per clip by
   reading `pipe.scheduler.timesteps` back after the run.
2. **Peak VRAM is 14.4GB, not the 22.9GB this table already carries** for
   "704x1280, 14 steps, `model_cpu_offload`" — same recipe name, same offload
   strategy, 8.5GB apart, identical on all six clips. The older row does not state
   its frame count, which is the most likely explanation (61 frames here) and is
   exactly the gap reading rule 4 exists for. **Consequence if 14.4GB is right:
   the "clip 2 never finishes" stall of 2026-08-02, diagnosed as the allocator
   holding 22.9GB of a 25.7GB card, needs re-examining** — at 14.4GB there is
   11GB of headroom between clips, and six back-to-back clips did not stall.
3. **`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` is a no-op on this box.**
   torch prints `UserWarning: expandable_segments not supported on this platform`.
   `video_task._run` sets it for **every** production render, and
   `ACTION-PLAN §2` row 11 lists "not set" as a MECH fix worth doing. On Windows
   it cannot be done at all, so any fragmentation stall it was meant to address is
   still open and still unaddressed.
4. **The first clip after a model load is ~20s slower than the rest** (12.05s/step
   against 10.46-10.69 for the following five, monotone). Warm-up, not recipe: no
   per-clip speed figure should be read off clip 1 of a batch, and the three T1
   rows' apparent 168.6 → 149.7 → 146.5 "trend" is that effect, not shift.
5. **Host RAM now has a number for a Wan row** — 36.9-52.7GB physical,
   69.2-80.3GB commit — where every Wan row previously said `no data`. It was
   measured with the 114GB A14B download running throughout, whose page cache
   Windows counts as in-use, so it is an upper bound on a busy box. Both jobs
   survived: unlike the LTX row, **a 5B render does not need the host to itself.**
6. **The one-load batch path is worth what `ACTION-PLAN §2` row 16 claims.** Six
   clips took one 88s load, so the fixed cost fell from the recorded 66.7s/clip to
   **14.7s/clip amortised**, and 908s of sampling produced 15.25s of video.
7. **Encode note for anyone comparing these numbers to earlier nights:** these
   clips are h264 **CRF 16** (1.1-1.3MB each), where production writes with
   `export_to_video`'s default `quality=5` VBR. The motion metric is computed on
   the encoded artifact, so cross-night comparison of median-frame-difference
   figures carries an encode difference as well as a recipe one.

### Open observations on the measured LTX row

Three, all unresolved, none a verdict:

1. **Progressive colour drift, magenta → teal over ~16 frames.** Untested lever:
   `adain_factor`, held at 0.0 in `pipeline/ltx_i2v.py:435` because upstream's
   distilled path leaves it off too. One sample decides it.
2. **Possible period-3 motion cadence — UNRESOLVED and confounded** by the 1Mbps
   h264 encode. Settling test: lossless re-encode on the next run. Do not record
   a cadence verdict until that is done.
3. **diffusers hardcodes `conditioning_mask = 1.0`** (maximum first-frame
   pinning) where upstream's own quickstart and docs use **0.8-0.9**
   (`ltx2-source.md:317-330`: `denoise_mask = 1.0 - strength`, so 1.0 pins those
   tokens to the clean image latent for the whole run, re-blended after *every*
   step). **Standing suspect for frozen-frame complaints** on any diffusers I2V
   path, not only LTX's.

### Closed — do not re-litigate (`ACTION-PLAN.md §6`)

| Model | Why closed |
|---|---|
| `Wan2.2-TI2V-5B-Turbo`, every mirror and GGUF | CC BY-NC-SA 4.0 upstream. **NC and ShareAlike are each independently fatal** — CC BY 4.0 is not a BY-NC-SA Compatible Licence, and watch-only does not unblock NC. `licence_gate.py:196-209`, `vet_model.py` hard-fail upheld |
| HunyuanVideo-I2V, HunyuanVideo-1.5 | **Territory exclusion** in the Tencent Hunyuan Community License |
| LTX-2.3 **fp8** single-file (`Lightricks/LTX-2.3-fp8`) | **Unloadable on diffusers 0.39.0**: the converter drops all 2924 `weight_scale`/`input_scale` tensors as `unexpected_keys`, then `.to(bfloat16)` — it loads, runs, and multiplies by discarded scales. Garbage output wearing a clean exit. `pipeline/ltx_i2v.py:33-54`. The bf16 build above is what we run |
| FramePack (`lllyasviel/FramePackI2V_HY`) | **Weights declare no licence at all**; the quoted Apache-2.0 covers the *code* only, and the weights are a HunyuanVideo derivative |
| SkyReels V2 / V3 | Licence is **PDF-only, i.e. not machine-readable and unread**; the V3 README states no licence. UNCLEAR, not cleared |

Non-licence dead ends (Kandinsky 5.0's anti-2D default negative, Open-Sora's
52.5-60.3GB single-GPU peak, `torch.compile` at low step counts,
FlashAttention on sm_120) are priced in `ACTION-PLAN.md §6` and not repeated here.

## 2. Parallel processes — the answer

**One render per card. Fleet-level parallelism only.** There is no supported way
to make two machines produce one clip faster, and two independent arithmetic
routes agree on why:

- **Ulysses sequence parallelism** — the parallelism Alibaba actually ship — is
  four collectives per attention layer per forward, two forwards per step under
  CFG: **~20GB of all-to-all per sampling step, ~1TB per clip.** At a perfect
  gigabit (125MB/s) that is **~160s of pure network per step against 8.67s of
  compute — ~18x slower than one card** (`wan22-official-source.md §3`,
  lines 275-288).
- **Tensor-parallel** is the milder version of the same wall: ~6.8GB of
  collectives per step, ~7x slower (`DECISION.md §5`). FSDP `FULL_SHARD` is
  ~10GB re-gathered per forward, ~80s. Ulysses returns 2.3x on 4 GPUs and 3.3x
  on 8 *even on datacentre interconnect*, and every shipped example is
  NCCL-hardcoded single-node.

So the unit of work is **one whole clip per machine**, which is what
`pipeline/farm_worker.py` already does, and what 15 beats needs anyway.

Two constraints on top of that, both from tonight:

- **Host RAM, not VRAM, is what decides co-residency.** The LTX row peaks at
  **60.8GB physical of 68.1GB** and **evicted the farm worker** on the 64GB box.
  An LTX render is host-exclusive: no co-resident T1/T2 stills, VO, or second
  render during it. **The 5B is the opposite, and it is measured**: the six
  T1/T2/T3 rows above record **36.9-52.7GB physical / 69.2-80.3GB commit**, taken
  with the 114GB A14B download running throughout, and neither job died — so a 5B
  render does *not* need the host to itself. (Only the four *older* 5B rows —
  the 188s/240s/462s ones — still say `no data`; the gap is those rows, not the
  model. Corrected 2026-08-05: this paragraph previously claimed no Wan 5B row
  had ever had host RAM measured, which the T1 row and open observation 5 both
  contradict.)
- **Card B (5070 Ti, 12GB) is a proof-pass machine, not a 704x1280 renderer.**
  Seconds-per-clip on it: no data from anyone. Card A peaks at 22.9GB on this
  shape and activations dominate, so quantised weights do not rescue it. Give it
  T1/T2 stills, VO and 480x832 drafts.

## 3. How to update this table

1. **One row per sample, appended from its sidecar** — never edited in from
   memory. The `*.meta.yaml` written by the render at §7.2 time carries model,
   recipe, steps, seed, seconds and `cost_usd`; the peak line carries VRAM and
   host RAM. Both come out of the same run that produced the clip.
2. **A row moves SCHEDULED → MEASURED only when a sidecar exists.** No estimate
   is promoted. Keep the tag vocabulary: `MEASURED-BY-US`,
   `DERIVED-FROM-OURS`, `CLAIMED-BY-<who>`, `MEASURED-BY-<author>`, `no data`.
3. **Label the offload strategy inside the VRAM cell** every time. Tonight's
   2.5GB device peak is a fact about sequential offload, not about a 26GB card,
   and it will be misread as "LTX fits in 4GB" the first time the label is
   dropped.
4. **Record VRAM and host RAM separately, and record `no data` when it is.** A
   blank cell reads as zero; the Wan rows' missing host figures are a real gap.
5. **Defect counts, not verdicts.** Frozen-frame count, saturation, channel
   cast, colour drift extent — measurements, table-eligible. "Good", "soft",
   "usable" — **Roman's alone (R4)**; those go in his screening record, not here.
6. **One sample per recipe change** (founder, 2026-08-03). A new row is the
   *output* of that rule; it is not licence to render fifteen of anything.
7. New weights get `licence_gate.py` / `vet_model.py` before download, and the
   licence cell quotes the governing document, not the HF tag — three rows above
   exist because a tag disagreed with the LICENSE file.
