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
| same — **the reproducibility control, run 2 of the same b1** | the b1 row's command **verbatim**: same script `ltx_i2v.py`, same venv, same env, same embeds file, same conditioning still, same prompt/negative files, `--image-crf 33`, two-stage, distilled sigmas, guidance 1.0, 704x1280, 65f @24fps, seed 20260732, sequential offload. **The only differences are `--out` and the `--task` provenance label** | production (two-stage, on-recipe) | **159.1s sample** against run 1's 108.1s — **+47% for byte-identical output**. Where it went: stage 1's **first** step **24.55 → 62.88s** (cold weight stream, the whole delta), stage 1 steps 2-8 **5.35 → 5.59 s/it**, stage 2 **10.54 → 10.32 s/it** | 0.0170 s(video)/s(wall) @b1 = 58.7s wall per 1s video — **and this cell is the point: the same recipe scored 0.0251 nineteen hours earlier.** A cross-run `sample_s` on this box carries a cold-start term worth ~50s; **compare recipes on per-step figures, not on totals** | **4.1GB torch of 26GB** — LABEL: **sequential-offload**. Identical to run 1 to the tenth of a GB | **61.0GB phys / 68.8GB commit of 68.1/123.9GB** — run 1 was 60.8/67.1 | 1/card, host-exclusive, as run 1 | LTX-2 Community License Agreement — **CANDIDATE** under watch-only per D16 | **MEASURED-BY-US 2026-08-05 15:22**, $0, rc=0. **BIT-IDENTICAL to the stored reference: sha256 `6226aef5…a880`, 352084 bytes, both runs.** Not "at the noise floor" — the same bytes through the h264 encode. **The run-to-run drift baseline for this pipeline is exactly zero**, which is what makes the b2 (rms 10.35) and fp8 (rms 11.93) figures attributable in full to their recipe change | `bench-platform/sha256-repro.txt`, `bench-platform/repro-ltx-b1.log`, `bench-platform/ltx23-b1-s20260732-run2.mp4.meta.yaml` |
| same — **batch 2, the throughput probe** | the b1 recipe exactly at 2 latents through one set of weights: two-stage 8 steps @352x640 → 2x latent upsample → 3 steps @704x1280, explicit sigmas, guidance 1.0, 65f @24fps = 2.708s per clip. Slot 0 repeats **seed 20260732** as the batch-fidelity check, slot 1 takes 20260733 | production (two-stage, on-recipe) | **190.1s sample** for 2 clips. **No s/step figure**: the two stages run at different per-step costs, so the renderer writes `null` rather than an average that describes neither | **0.0285 s(video)/s(wall) @b2** = 35.1s wall per 1s video (5.417s of video / 190.1s sample) — **1.14x b1's 0.0251**, the only batch series on this box that gains | **7.2GB torch / 2.6GB device of 25.7GB** — LABEL: **sequential-offload**, measures the offload strategy, not card capacity; +3.1GB torch over b1's 4.1GB | **64.2GB phys / 75.3GB commit of 68.1/130.4GB** — **+3.4GB physical over b1's 60.8GB**, and that slope is what closes b4: two more latents put it past the box's 68.1GB | 1/card, still **host-exclusive** — the b1 row evicted the farm worker at 60.8GB and this one runs 3.4GB higher | LTX-2 Community License Agreement — **CANDIDATE** under watch-only per D16 | **MEASURED-BY-US 2026-08-05**, $0. Throughput is a real gain, **but the batched slot is not pixel-equivalent to the un-batched reference** — see the fidelity note below, and do not treat a batched render as a re-issue of an approved clip | `SAMPLES/batch-bench.jsonl`, `SAMPLES/ltx23-production-b2-s20260732.mp4.meta.yaml`, `SAMPLES/ltx23-production-b1-s20260732.mp4.meta.yaml` |
| **same — fp8 layerwise cast, `--offload model` (the RESIDENT build)** | the b1 row's recipe **byte-for-byte** — same embeds file, same conditioning still, same prompt/negative files, `--image-crf 33`, two-stage 8 steps @352x640 → 2x latent upsample → 3 steps @704x1280, explicit sigmas, guidance 1.0, 65f @24fps = 2.708s, seed 20260732, beat 1. **The only two changes are the recipe change under test**: `enable_layerwise_casting(storage float8_e4m3fn / compute bf16)` on the transformer, and `enable_model_cpu_offload` in place of sequential | production (two-stage, on-recipe) | **73.3s sample / 224.3s wall** (stage 1 8 steps in 21s — the first step is 12.4s of onload, the last 1.58s/it; stage 2 3 steps in 18s @6.17s/it). **The wall is the honest number for a one-off**: it carries a **one-time 139s fp8 cast** the bf16 build never pays | **0.0369 s(video)/s(wall) @b1** = 27.1s wall per 1s video (2.708s of video / 73.3s sample) — **1.47x the bf16 b1's 0.0251**, the fastest sample row on this box. **DERIVED-FROM-OURS: the cast breaks even at exactly 4 clips in one process** (saves 34.8s/clip against a 139s cast); below that, fp8 is a net LOSS on wall time | **23.1GB torch of 25.7GB** — LABEL: **`model_cpu_offload` + fp8 layerwise, transformer RESIDENT**. Verified externally, not inferred: the telemetry daemon's trace (`telemetry.csv`, 10s cadence) shows **21346 MiB @97% util** through stage 1 and **22920 of 24463 MiB @99% util** through stage 2, against ~2.5GB when the same model is streamed. **1543 MiB spare.** Residency is per-stage: VRAM drops to **362 MiB between** the stages, `model_cpu_offload` returning the transformer to host while the upsampler runs NOT comparable to the sequential-offload 4.1/7.2GB rows above — different question, different answer | **64.6GB phys / 97.0GB commit of 68.1/123.9GB** — **the host got WORSE, not better: +3.8GB phys and +29.9GB commit over the bf16 b1's 60.8/67.1.** The cast retains the bf16 storages it replaces (the same mechanism as the AnimeGen finding above), so the predicted "~34GB resident host" did not happen and must not be quoted | 1/card, **host-exclusive** — measured with both farm-worker processes stopped, and the commit peak leaves 26.9GB of headroom, so co-residency is unproven and untested | LTX-2 Community License Agreement — **CANDIDATE** under watch-only per D16. The `ltx23-distilled-fp8` key resolves to exactly one licence document through the gate | **MEASURED-BY-US 2026-08-05**, $0, **rc=0 first attempt — the `--offload group` fallback was never needed**. **NOT SCREENED — the founder has not seen this clip (R4).** Defect counts only: **0/64 frozen frames** (consecutive-frame MSE min 5.06 vs the reference's 3.60, i.e. marginally *more* inter-frame motion); same-seed drift vs the bf16 b1 **rms 11.93/255, PSNR 26.60 dB**, against a **0.93** crf23 encode-noise control and a **1.74** bitrate-matched control — real drift, slightly more than batch 2 cost (10.35); colour drift **R −2.54, G −2.81, B +0.12** | `SAMPLES/batch-bench.jsonl`, `SAMPLES/ltx23fp8-production-b1-s20260732.mp4.meta.yaml`, `probe-ltx-fp8.log`, `fp8-fidelity-20260805.log` |
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

### 2026-08-05 — LTX at b2: the one batch that gains, and what it costs in fidelity

**The third probe ran.** The section above closes with "there is no LTX batch row
until [the `--batch` fix] lands". It landed, the probe ran, and the row is in the
table: **190.1s of sampling for two 2.708s clips — 0.0285 s(video)/s(wall), 35.1s
of wall per second of video, against b1's 0.0251 and 39.9s.** That is **1.14x b1**,
and it is the only batch gain measured on this box. AnimeGen's b2 gained at
*preview* geometry only; the 5B lost at both geometries. Memory moved the way
sequential offload predicts: **7.2GB torch of 25.7GB** — the card is nowhere near
the constraint — against **64.2GB host physical of 68.1GB**, which is.

**b4 is closed without running it, on the host slope.** b1 → b2 cost **+3.4GB of
host physical** (60.8 → 64.2GB) while VRAM barely moved, so two more latents put
the run past the 68.1GB this box has — on a render that is already host-exclusive
and evicted the farm worker at b1. That is arithmetic on two measured points, not
a measurement, and it is recorded here as a closure rather than promoted to a row.

**The fidelity check did not pass the way the 5B's did, and that is the finding.**
Slot 0 of the b2 batch ran at seed 20260732 — the b1 sample's seed, byte-identical
inputs, the same conditioning frame — and it is **not the same clip**. Against
`SAMPLE-ltx23-b01.mp4` it measures **RMS 10.35 of 255**, where re-encoding the
reference against itself measures **0.93**: about **11x the control**. The drift
grows with denoise depth, the conditioning frame itself is identical, and the two
slots differ from each other properly (the prompt-embed expansion is confirmed
working) — so this is a real batch doing real independent work, neither one clip
rendered twice nor a batch that silently broke.

**What that licenses and what it does not.** A batched render is a *new clip*: it
can be screened, kept and shipped on its own merits, but it is **not a drop-in
re-render of an approved un-batched clip**. Re-issuing an already-approved beat
from inside a batch puts it back in front of Roman — §6 territory, not a
throughput question.

**The open question, stated so nobody closes it by assumption: whether two
UN-BATCHED runs reproduce each other is not established.** Nobody has run this
recipe twice at b1 and compared. Until that exists 10.35 has no baseline, and the
only honest reading is "the batched slot differs from the reference by ~11x a
re-encode" — **not** "batching causes drift". The test is one repeat of the b1
recipe at the same seed with the same metric, and it is the next thing this row
needs.

**Provenance gap, recorded rather than papered over.** The RMS comparison was run
against the two clips on disk during the 2026-08-05 session and **wrote no log
file**, so unlike every other figure in this table it cannot be re-read out of an
artifact — only re-derived by running the check again. Both clips are kept
(`SAMPLES/ltx23-production-b2-s20260732.mp4` and `SAMPLE-ltx23-b01.mp4`), so that
is cheap; the next such check writes its output somewhere. Smaller and related:
the b1 row cites `SAMPLE-ltx23-b01.mp4.meta.yaml`, which carries the recipe but
**not** the derived 0.0251/39.9 — those live in the sidecar of the gallery copy
`SAMPLES/ltx23-production-b1-s20260732.mp4` (same bytes, sha256 `6226aef5…`), and
that is the file `COMPARISON.html` names when it joins b1 into the batch table.

### 2026-08-05 — the fp8 cast: the card wins, the host pays, and the founder has not looked

One sample, one recipe change (founder, 2026-08-03), run with the farm worker
stopped. It answered the two questions it was set and contradicted the prediction
attached to it. Sources: `SAMPLES/batch-bench.jsonl` (row `ltx23fp8`),
`SAMPLES/ltx23fp8-production-b1-s20260732.mp4.meta.yaml`, `probe-ltx-fp8.log`,
`fp8-fidelity-20260805.log`.

**The two hook systems coexist.** The diffusers layerwise-casting registry and
the accelerate `model_cpu_offload` hooks ran together at rc=0 on the first
attempt. The researched `--offload group` fallback was never invoked. This was
the real risk in the change and it is now measured rather than argued.

**Residency is confirmed, and it is confirmed the only way it could be.** The
in-process peak line reports `device 2.6GB`, which is a post-run reading taken
after the card drained — quoted alone it would say "streamed" and be exactly
wrong. The telemetry daemon's trace (`C:\banyan-farm\telemetry.csv`, 10s cadence,
a process external to the render) shows the card ramp 2430 → 8114 → 17990 →
**21346 MiB at 97% util** through stage 1, and **22920 of 24463 MiB at 99% util**
through stage 2. The transformer is on the card. This is the one number in the
row that no artifact of the run itself could have supplied, which is why it had
to come from outside the process.

**Correction, verification pass 2026-08-05:** an earlier draft of this row said
the card sat "flat at 22920 for the rest of the loop", sourced to an ad-hoc
nvidia-smi loop at 0.9s sampling that **left no artifact and cannot be
re-verified**. The durable telemetry record does not support "flat": between the
two denoise stages VRAM drops to **362 MiB**, because `enable_model_cpu_offload`
returns the transformer to host RAM while the latent upsampler runs. Residency
holds **within** each denoise stage, which is what the sample was run to
establish; it is not continuous across the run. The peak, the 1543 MiB margin and
the residency verdict are unchanged. Rows quoting a sampling rate finer than 10s
for this run should be read as unsourced.

**The fit is real and it is thin.** The cast measured **35.37 → 17.69 GiB** of
transformer storage in 139s — the predicted ~19.8GiB was pessimistic, and norms
stayed bf16 via the model's own `_skip_layerwise_casting_patterns`. Peak torch
23.1GB against a 24463 MiB card leaves **1543 MiB**. That margin, not the host,
is why b2 is not automatic: a second latent spends it on activations.

**THE HOST PREDICTION WAS WRONG, and the row says so rather than quietly
dropping it.** The change was expected to need ~34GB of host physical against the
bf16 run's 60.8GB. Measured: **64.6GB phys, 97.0GB commit** — worse on both, and
the commit spike is the in-process cast doing precisely what the AnimeGen finding
above describes, retaining the bf16 storages it replaces. The phys trace shows
the shape plainly: 9.5GB at cast start, 60.0GB by the time the connectors load,
then a *fall* to ~40GB once the transformer moves onto the card. Anyone planning
a bigger fp8 run should size the host against 97GB of commit, not against the
17.69GiB the weights end up occupying.

**Speed is a real gain with a real caveat.** 73.3s against 108.1s is 1.47x on the
sample, and 0.0369 s(video)/s(wall) is the fastest row in the table. But the run
pays a **one-time 139s cast**, so end-to-end wall for a single clip is 224.3s
against the bf16 build's ~120s. **The cast breaks even at exactly 4 clips in one
process.** For a one-off render fp8 is a loss; for a 15-beat episode it is not.
Nobody should quote the 1.47x without the break-even next to it.

**Fidelity: a different clip, by about one batch-change.** Same seed, same still,
same prompt, same `--image-crf 33` — and rms **11.93/255** (PSNR 26.60 dB)
against the bf16 b1. The controls make that legible: re-encoding the reference at
crf23 costs **0.93**, at the fp8 clip's own bitrate **1.74**. So the drift is
~13x the encode-noise floor and slightly *above* what batch 2 cost (10.35).
Per-frame, frame 1 matches at the noise floor (1.46) and divergence builds over
~4 frames then plateaus — quantisation noise accumulating through the denoise,
not a different scene. No frozen frames. Colour cools slightly in R and G
(−2.54, −2.81) with B flat (+0.12).

**What is NOT decided.** None of the above is a quality verdict and none of it
promotes this build. Rule 5 of §3 and R4 both apply: these are defect counts.
`COMPARISON.html` now ranks the fp8 row first on throughput and carries an
explicit correction under the table saying the top row is not a verdict, because
the fastest row in the table being an unscreened clip is exactly the confusion
that correction exists to prevent. **A screening is owed to Roman before any
batch point above b1 on this build is scheduled.**

### 2026-08-05 — the reproducibility control: identical bytes, a total that does not reproduce

**The question:** every drift figure in this document — batch 2's rms 10.35,
fp8's rms 11.93 — was measured against a *stored* reference, and the batch-2
note said so plainly: *"whether two UN-batched runs reproduce each other has not
been tested, so there is no baseline for this metric yet."* Without that
baseline neither figure could be attributed to its recipe change.

**The answer: the baseline is zero.** Re-running the bf16 b1 reference verbatim
produced **the same bytes** — sha256 `6226aef5…a880`, 352084 bytes, both runs,
through the h264 encode. Not "below the encode-noise floor"; identical. Sources:
`bench-platform/sha256-repro.txt`, `bench-platform/repro-ltx-b1.log`, and the
run-2 sidecar. Two consequences, one for fidelity and one for speed.

**Fidelity — both drift figures are now fully attributable.** Batch 2's 10.35
and fp8's 11.93 contain no run-to-run component. The doctrine they support
(*a batched or fp8 re-render of an approved beat is a new clip and needs
screening again*) stops resting on an untested assumption. The batch-fidelity
note in `build_comparison.py` was updated in the same pass; its closing sentence
had said the baseline was untested and that sentence was, from 15:22 on
2026-08-05, false.

**Speed — a cross-run `sample_s` on this box is worth ±50s, so stop comparing
totals.** The identical-output re-run took **159.1s against 108.1s, +47%**. It
is not mysterious and it is not thermal: stage 1's **first** step went
**24.55 → 62.88s** — the cold weight stream under sequential offload — and that
one step is the entire delta. Everything that runs after it reproduced:

| | run 1 (2026-08-04 23:14) | run 2 (2026-08-05 15:22) | delta |
|---|---|---|---|
| stage 1, step 1 | 24.55 s | 62.88 s | **+156%** |
| stage 1, steps 2-8 | 5.35 s/it | 5.59 s/it | +4.5% |
| stage 2, 3 steps @704x1280 | 10.54 s/it | 10.32 s/it | −2.1% |
| `sample_s` total | 108.1 s | 159.1 s | **+47%** |
| peak torch / phys / commit | 4.1 / 60.8 / 67.1 GB | 4.1 / 61.0 / 68.8 GB | — |

So **§3 gets a sixth reading rule in practice: quote per-step, not totals.**
Steady-state s/step reproduces within 5%; a `sample_s` difference smaller than
~50s between two runs on this box is box state, not a recipe.

**Applied to the fp8 row, whose headline was two totals.** "1.47x" is
108.1/73.3. Measured against today's re-run of the *same bf16 recipe* the same
arithmetic gives 2.17x. The gain is real — it is visible in the part that
reproduces — but it must be quoted per-step: stage 2 **6.17 s/it fp8 against
10.54 and 10.32 bf16 = 1.67-1.71x**, stage 1 steady **1.23 against 5.35 and
5.59 s/it**. And **the "break-even at exactly 4 clips" figure is withdrawn as
over-precise**: 139s of cast against a per-clip saving of 34.8s (run-1 totals)
gives 4.0 clips, against 85.8s (run-2 totals) gives 1.6, and against
denoise-only per-step arithmetic (93.0s bf16 → 39.5s fp8) gives **2.6**. The
honest figure is **~3 clips, range 2-4**. Nothing else in the fp8 row changes:
residency, the host cost and the fidelity numbers were all measured within a
single run and carry no cross-run term.

### 2026-08-05 16:00 — fp8 at batch 2: RUN, and it does not fit. Neither does its fallback

Founder-sanctioned, and it supersedes the "not scheduled — b1 screening first"
note this section used to carry. **No clip, no sidecar, no jsonl row** — nothing
finished, so by rule 2 nothing goes in the table above. What follows is the
evidence, and per rule 8 the comparisons are per-step.

**Attempt 1, `--offload model` (the resident build), 15:52:43 → killed 15:56:36.**
It is not an OOM. **The card never raised** — it spilled, which is the same
`ACTION-PLAN §1 T0` failure mode the AnimeGen b4 row already carries, on a
different model:

- **Stage 1 at 352x640 CLEARED at batch 2**, 8 steps in 34s. Per step, steady
  state (excluding a first step that is weight onload — 18.68s here, 12.43s in
  the b1 reference): **~2.2 s/step against b1's ~1.3**, i.e. **1.7x the per-step
  cost for 2x the output**. On stage 1 alone, batching fp8 gains, and gains by
  about as much as the bf16 build's b2 did. `stage1 latents (2, 128, 9, 20, 11)`
  and `embeds expanded to batch 2` confirm two real latents, not one twice.
- **Stage 2 at 704x1280 is the wall.** Step 1 of 3 was still running after ~71s
  against the b1 reference's **8.37s for the same step** — past 8x, where the
  abort gate was 2x — and **no stage-2 step ever completed**. An external
  `nvidia-smi` sample at 15:55:57 read **24112 of 24463 MiB at 100% util**, and
  a second at 15:56:19 read the same: **98.6% of the card**, held. That is the
  WDDM sysmem-fallback signature, and it is the signature that bugchecked this
  host on 2026-08-04, so the process was killed rather than allowed to converge.
- **The host was not the constraint and never came close.** Peak physical was
  **65.4 of 68.1GB during weight load** — under the 66.5GB abort gate — and by
  the time the card was pinned, physical had fallen to **43.99GB** with commit at
  **85.27 of 123.9GB**. The b1 prediction was right about which resource runs
  out: b1 fits with 1543 MiB spare, and a second latent's stage-2 activations
  spend exactly that.

**Attempt 2, `--offload group` — the one sanctioned fallback, 15:58:14 → rc=1 at
16:00:23.** It failed in 129s, and **not on memory**: physical at stage 1 was
**46.3GB against attempt 1's 64.3**, so group offload was doing its job.

```
!! DIED in stage 'stage1-denoise-352x640-8steps':
   RuntimeError: Input type (CUDABFloat16Type) and weight type (CPUBFloat16Type)
   should be the same
     latents, conditioning_mask = self.prepare_latents(
     File ".../diffusers/pipelines/ltx2/pipeline_ltx2_image2video.py", line 722,
       in prepare_latents
       retrieve_latents(self.vae.encode(image[i].unsqueeze(0).unsqueeze(2)), ...)
```

**`--offload group` is broken for this pipeline, and the break has nothing to do
with batch size.** `GroupOffloadingHook` installs a **`pre_forward`** hook and
only that (`diffusers/hooks/group_offloading.py:368,388`, diffusers 0.39.0), so
the weights of a module are onloaded when its `forward` runs. `vae.encode` is not
`forward`. The image-conditioning encode therefore meets a VAE that is still on
CPU, before any denoise step and before latent count means anything. **This makes
`ltx_i2v.py:504-508`'s "the fallback if `model` OOMs" false as written**, and
that comment is corrected in the same commit as this note.

**What this closes and what it does not.** It closes fp8 b2 on this box: the only
offload strategy that makes fp8 fast enough to matter is the one whose margin b2
consumes, and the documented alternative does not run at all. It does **not**
close batching for LTX generally — the bf16 b2 row above still stands at 1.14x,
and stage 1 here says the fp8 build would batch happily if stage 2 were not
sharing the card with a resident transformer. The untried lever is a **stage-split
offload** (resident through stage 1, streamed through stage 2), which is a new
recipe and therefore a new one-sample question, not a retry of this one.

**Still owed, and unchanged by any of the above: `ltx23fp8` b1 has not been
screened** (R4). Nothing here is a verdict on the look of anything.

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
  Seconds-per-clip on it: no data from anyone — **still true on 2026-08-05**, and
  see §4, which now records the box itself. Card A peaks at 22.9GB on this
  shape and activations dominate, so quantised weights do not rescue it. Give it
  T1/T2 stills, VO and 480x832 drafts. Two things §4 adds that change the shape
  of this paragraph without changing its verdict: the box has **32GB of host
  RAM, not the 16GB** this file's sources assumed, and the binding constraint
  for a 5B preview on it is probably **host commit, not the card**.

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
8. **Quote per-step, not totals** (added 2026-08-05 from the reproducibility
   control). Two byte-identical runs of the same recipe scored 108.1s and
   159.1s. Steady-state s/step reproduces within 5%; a `sample_s` total carries
   a cold-start term worth ~50s on this box. A cross-run difference in totals
   smaller than that is not a result, and any total quoted should name its run.

## 4. Platforms — the two boxes, and what each is measured to do

Every row above was measured on **one** of these. The distinction had been
implicit and one afternoon of confusion made it worth writing down: **there is
no 4070 in this fleet** (founder's correction, 2026-08-05), there are two
Windows GPU laptops, and **both of them report `hostname` = `MSI`**. Identify a
box by its GPU or its ssh user, never by hostname. Measured facts only; the
"video throughput" cell is the fleet-level question and one of the two answers
is *unmeasured*, which is different from *no*.

| | **Box A** | **Box B** |
|---|---|---|
| ssh alias | `rtx5090` | `rtx5070` — **added 2026-08-05**, `192.168.3.153`, user `olegm`, key `~/.ssh/banyan-5070` |
| user | `artvn` | `olegm` |
| chassis | MSI, RTX 5090 Laptop | MSI Vector 16 HX AI A2XWHG |
| GPU | RTX 5090 Laptop, **24463 MiB** | RTX 5070 Ti Laptop, **12227 MiB** |
| host RAM | **68.1GB** visible | **31.4GB** visible / 32GB installed — **corrects the 16GB** assumed in `misc-candidates-source.md:58` |
| commit limit | **123.9GB** (grown to 140.6GB under the A14B load) | **67.4GB** (31.4 phys + 36GB pagefile), 714.7GB free on C: so it can grow |
| reachability | LAN ssh since 2026-08-01 | **LAN ssh since 2026-08-05.** Before that it was a USB-bundle enrollment (`STATE.md` 2026-07-30) with no remote route |
| repo checkout | `C:\banyan-farm\banyan-city` | same path, fast-forwarded 231 commits off the stale `farm-results-msi` to `main` @ `ae13cc6` on 2026-08-05 |
| video throughput | **MEASURED** — every row in §1 | **PARTIAL, 2026-08-05** — the probe finally ran and got 3 of 6 denoise steps before a room move killed it: **362 / 601 / 719 s per step** at full clock, against Box A's **16.4 s/step**. Settled steps only; no clip and no completed sample, so **no `s(video)/s(wall)` figure exists for this box** and none should be quoted |
| GPU power state | board power unremarked; every §1 row was taken at full clock | **RESOLVED 2026-08-05 evening — it was the adapter, and the card is not clamped.** On the correct barrel adapter: `enforced.power.limit` **140.00 W**; a bf16 burn holds **2385 MHz at 139.93 W** (the whole board budget); through the 5B render **2775 MHz at 100% util with `clocks_event_reasons.sw_power_cap` Not Active**, while the pack charged **6% → 32%**. The afternoon's 25 W / 180 MHz was the wrong adapter. Earlier rows measured a cable, not a card |
| mains stability | not a question on this box | Four Kernel-Power event-105 source changes between 15:09:57 and 16:42:27 on 2026-08-05, **all on the wrong adapter**. **Stable since the swap**: AC held through a 40+ minute 100%-util render while charging the pack from 6% |
| stability | two unclean reboots on 2026-08-04/05, both under batch pressure; Kernel-Power 41 at 06:07:05 | **first render attempt 2026-08-05 — and it did not misbehave**: 28 minutes at 100% util with GPU memory, host physical and commit all flat, no crash and no bugcheck. It was killed from outside (unplugged for a room move), which is not a stability finding |

**Why Box B still has no number, and why that is not the same as "too small".**
The sample was staged with byte-verified inputs (conditioning still, prompt and
negative all sha256-matching Box A's; same model snapshot `b8fff731`; torch
2.11.0+cu128, diffusers 0.39.0) and then **not run**: the laptop was on battery
at 9.5% falling to 8%, `PowerOnline=False`, and Windows' own task policy
(`Stop On Battery Mode, No Start On Batteries`) refused it. Overriding that
policy would have put a 5-10 minute 100%-util render on a machine minutes from a
hard power-off — the same class of event as the two bugchecks above — and the
number it produced would have been taken at a **442 MHz** SM clock with
`power.limit` reading `[N/A]` against a 140W part, which is not the box's
throughput. It needs a human to plug it in.

**Update 2026-08-05 ~16:15Z — it was plugged in, and that was not enough.**
`PowerOnline` is True and the pack is charging (4% → 13% over sixteen minutes,
84 Wh full capacity), but the GPU is still clamped and the sample still has not
been spent. Measured with a 35s bf16 matmul burn: `enforced.power.limit`
**25.00 W** both idle and under load, against a **65 W default / 140 W maximum**;
SM clock **180 MHz of 3090 MHz** at 100% utilisation; `power.draw` 13.4 W; 36 C,
so not thermal; `clocks_event_reasons.sw_power_cap` **Active** throughout. That
is ~6% of clock, and it is *lower* than the 442 MHz measured on battery — so
battery state was never the whole story. Charge rate falls rather than rises
(39.8 W → 32.5 W → 20.2 W while the GPU drew → 17.4 W idle), which is the
signature of one small shared power budget: most likely a ~65 W USB-C supply in
place of the ~240 W barrel adapter this chassis expects, or MSI Center's
Silent/Eco shift mode, which clamps GPU TGP regardless of AC and is not the
Windows power scheme (that reads Balanced). Both need a human at the machine.
**A throughput figure taken at 180 MHz would measure the clamp, not the card**,
so no row is added.

**Correction, ~16:58Z — the 25 W clamp is the ON-AC state, and both hypotheses in
the paragraph above are retracted.** Kernel-Power **event 105** shows four
power-source changes in under two hours (15:09:57, 15:19:21, 15:58:53, 16:42:27).
AC arrived at 15:58:53 and **left again at 16:42:27**; the limit stepped 25 → 45 W
at 16:42:54, twenty-seven seconds later. So the apparent "lifted at 30% battery"
was the switch to battery power, not a state-of-charge gate, and **on AC the card
was clamped harder (25 W / 180 MHz) than on battery (45 W / 802 MHz, 35.4 TFLOPS
bf16)** — the reverse of what the 442 MHz battery reading had implied. Adapter
wattage is not exposed to software and shift mode is not readable over ssh, so
neither retracted hypothesis was ever measured; a modest adapter sharing a budget
with a ~40 W charging load stays a plausible but unmeasured mechanism. The
measured blocker is the mains connection itself. Box is on battery at 25% and
falling as of this note, so still no sample.

**Resolved ~18:55Z — the adapter hypothesis was right, and retracting it was the
wrong call.** The founder plugged in the correct barrel adapter. Nothing else
changed, and `enforced.power.limit` went **25.00 W → 140.00 W**: a bf16 matmul burn
held **2355 MHz at 121.02 W** and then **2385 MHz at 139.93 W**, against 180 MHz at
13-25 W all afternoon. The render that followed sat at **2775 MHz, 100% util,
`sw_power_cap` Not Active** for forty minutes *while* charging the pack from 6% to
32% — one adapter carrying a flat battery and a full-power GPU at once, which is
exactly the load the previous adapter could not.

So "a modest adapter sharing one budget with a ~40 W charging load", retracted two
paragraphs above as plausible-but-unmeasured, is **confirmed by intervention**: the
one thing that changed moved the cap by 115 W. Two honest limits on that claim —
it is a single intervention, and reseating the plug is confounded with swapping it,
so a loose barrel connector on the *right* adapter would produce the same result;
and adapter wattage is still not exposed to software, so the mechanism is inferred
from the cap moving, not read off the supply. What is no longer in doubt is the
practical conclusion: **this box was adapter-limited, never clock-limited.** Every
Box B figure from here is a real number; every one before it measured a cable.

The retraction itself is the lesson worth keeping. "Unmeasured" was the correct
label for the hypothesis and "retracted" was not — the evidence for it (charge rate
falling as the GPU drew, a cap below the 65 W default) was real and pointed the
right way. Downgrading a well-supported inference to a discarded one, because it
could not be proven over ssh, cost an afternoon of waiting for the wrong thing.

**The sample ran, and the move killed it at step 3 of 6 — so the fit question below
is still open.** Fired 19:00:43 local on 2026-08-05, the staged probe unchanged
(`--stage simple --model ti2v-5b --size 704x1280 --seconds 2.5 --fps 24 --steps 6
--guidance 5.0 --batch 1 --mode preview --offload --no-shake-neg`, seed 20260732,
inputs sha256-verified against Box A's). It loaded in **74s**, reported
`WanImageToVideoPipeline (forced image-to-video)`, `model cpu offload ON`, and
`VRAM[after load, before .to(cuda)] used 1.26/12.8GB`. Then it denoised three steps
and stopped:

| step | cumulative | **this step** | Box A, same recipe |
|---|---|---|---|
| 1 | 06:02 | **362 s** | 16.4 s |
| 2 | 16:03 | **601 s** | 16.4 s |
| 3 | 28:02 | **719 s** | 16.4 s |

Read the per-step column, not tqdm's rate: those are differences of its cumulative
elapsed, and its smoothed `s/it` (362 → 503 → 602) understates every step after the
first. **Settled steps only — there is no clip, no completed sample and therefore no
`s(video)/s(wall)` figure for this box.** Do not publish one; three rising steps do
not extrapolate honestly to six.

**The card was at full clock the whole time, so this is not the clamp again**:
**2775 MHz** at 100% util with `sw_power_cap` **Not Active**, 43-55 W of a 140 W
budget, 48-52 C. Device memory pinned **flat at 11908/12227 MiB (97.4%)**, host
physical steady, and `commit_used` ~59.5 GB against **31.4 GB installed**. What is
solid and structural: **UMT5-XXL alone is ~11.4 GB bf16 against 11.94 GiB of usable
card**, so Box B can never use Box A's resident path for Wan 5B at any resolution —
offload, and its PCIe cost, is mandatory here rather than a tuning choice. What is
NOT established is *why each step costs more than the last*. Host physical use fell
27.9 → 13.7 GB and then flattened with ~17.5 GB still free, which is at least as
consistent with the safetensors file cache being released after load as with
anything paging out; page-fault rates were never sampled. It stays a measured curve
with no mechanism attached.

**Why it stopped is not instability, and the missing rc line is the evidence.**
`probe-5070.cmd` echoes `==== probe-5070 exited rc=%ERRORLEVEL% ====` *after* the
python call, so any renderer-side failure — CUDA OOM included — leaves the parent
`cmd` alive to write it. **No rc line was written at all**, so the whole process tree
died together: that rules out a crash inside the renderer and points at the task
being stopped. The log also carries no traceback and no CUDA error, while the trace's
next samples show GPU memory and util drop to **0** and commit collapse
59.4 → 15.6 GB. The box was being unplugged to be
carried to another room, and these tasks are registered through `schtasks`, whose
default settings include stopping on a switch to battery — the same
`Stop On Battery Mode` policy already recorded above as having refused to start this
sample once. Unconfirmed (it needs the TaskScheduler log once the box is back), but
it is the reading the evidence supports, and it is the opposite of a bugcheck: for
28 minutes GPU, host RAM and commit were all steady.

**So §4's fit prediction below is neither confirmed nor falsified.** The run never
reached the VAE decode, which is the only thing that prediction is about. `tile_vae()`
has since been added to `stage_simple` (the divergence the correction below
identified is a real bug on its own terms), so the *next* run tests the tiled path
and the untiled peak on a 12GB card may now never be measured at all.

**Correction, 2026-08-05 — `stage_simple` does not tile the VAE, and the fit
margin above is negative, not sub-gigabyte.** The bullet below said the 14.4GB
peak is an untiled VAE decode in `bench_5b_modes.py` "while
`pipeline/wan_i2v.py`'s `stage_simple` **does** tile the VAE". It does not.
`tile_vae()` appears exactly three times in that file — the definition at :176,
the AnimeGen loader at :328, and `stage_render` at :687. The 5B branch of
`stage_simple` runs `from_pretrained` → VRAM accounting → offload-or-`.to(cuda)`
→ `_sample`, and neither `stage_simple` (:357-482) nor `_sample` (:483-657)
calls it. The staged probe runs `--stage simple`, so it will do an **untiled
float32 VAE decode** of 61 frames at 704x1280 and should peak near the same
**14.4GB — against 12.82GB decimal of card**. The prediction below is kept
unedited, as written, because §4 exists to be falsified by the sample; this note
records that one of its two premises was already falsified by reading the source
before the sample ran. A VAE OOM on that path is a one-line fix (call
`tile_vae()` in `stage_simple`), and the tiled configuration is the one an
episode would actually use — so "does the untiled path fit" and "can this box
render 5B" are now two different questions.

Also unequal between Box A's row and the staged probe: Box A ran **without**
`--offload`, the probe runs **with** it (`bench-5b-modes.log` is 31 lines and
contains no "offload", "tiling" or "slicing"). Any eventual ratio therefore mixes
silicon with PCIe streaming cost and must not be quoted as a clean throughput
factor. `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` is set in the probe
env and buys nothing on Windows — Box A's own log carries "expandable_segments
not supported on this platform".

**What the fit question actually is, stated before the sample so the sample can
falsify it** (DERIVED-FROM-OURS, `bench-platform/fleet-inventory-20260805.txt`):

- **Card side — plausible, sub-gigabyte margin, and the naive reading is
  wrong.** The 5B preview b1 row's **14.4GB torch peak is an untiled VAE
  decode**: `bench_5b_modes.py` does `from_pretrained` → `enable_model_cpu_offload`
  and never calls `tile_vae()`, so with no two components resident together that
  peak cannot be a weight ceiling. `pipeline/wan_i2v.py`'s `stage_simple` **does**
  tile the VAE, which puts the ceiling at the largest single resident module —
  UMT5-XXL at ~11.4GB bf16 — against 11.94GiB of card. So "14.4 > 12.2, proven
  impossible" does not follow.
- **Host side — the sharper risk, and newly visible.** That same row peaks at
  **80.6GB of commit** against Box B's **67.4GB** limit. Windows may grow the
  pagefile into 714GB of free disk, or may not.
- **Therefore: one proven video box, one unproven.** Box B stays a stills / VO /
  480x832-draft machine in every plan until the sample runs. Nothing here says
  it cannot render; it says nobody has measured it, and the two statements must
  not be allowed to merge.

**Update 2026-08-05 — the verdict survives, on different evidence.** Box B is still
the stills / VO / draft machine, but no longer because the fit is unknown: three
measured steps at 362-719 s against Box A's 16.4 s say that even if 704x1280 5B
*fits*, asking this box for it costs something like an order of magnitude more wall
time per beat. The recommendation that follows is **not** "try harder on 5B" — it is
that the model shaped for this box is the one that already runs small:
**LTX-2.3 preview took 1.9 GB torch / 1.5 GB device** on Box A (§1), which is the
only measured row in this table that would sit comfortably inside 12 GB without
offload at all. That is the next thing to put on Box B, and it needs its own sample.
