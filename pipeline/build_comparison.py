#!/usr/bin/env python3
"""COMPARISON.html — the LOCAL screening page for the model bake-off samples.

    python3 pipeline/build_comparison.py

Two readers, two jobs. **Roman** screens the clips (R4 — taste is his, and no
number on this page is a verdict). **Oleg** reads the cost and throughput, whose
optimisation target he set on 2026-08-04: maximum seconds of video per second of
real time.

LOCAL ONLY. These are unapproved media samples (STEWARDSHIP §6), so this page is
never built into `_site/`, never deployed, never committed. It is a file you open
from the repo root, which is why every `src` is a relative path.

Every figure comes from a `*.mp4.meta.yaml` sidecar, a bench `.jsonl` row, or —
where the machine-readable artifact has no cell for it — `MODEL-COMPARISON.md`,
and each cell says which. Nothing is typed in from memory. Clips whose sidecar is
missing render with a visible gap rather than an invented number: that is
MODEL-COMPARISON §3.4 ("record `no data` when it is") applied to a web page.

Re-run it after any new clip lands. It globs, so a model nobody has written a
registry entry for still appears, in its own group, labelled as unregistered.
"""

import hashlib
import json
import re
import sys
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import quote

import yaml

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "COMPARISON.html"

# Directories globbed for clips. Order matters: the first copy of a byte-identical
# artifact wins the gallery slot and later copies are labelled as copies, because
# two of tonight's clips exist twice under two naming schemes and showing them
# twice would read as two samples.
CLIP_GLOBS = ["SAMPLES/*.mp4", "bench-T1T2T3/*.mp4", "SAMPLE-*.mp4"]

# Batch-scaling bench files, read in this order. One shared row schema; the row's
# `label` decides which model's table it lands in, so a new model needs a file and
# no code. A file that does not exist yet is skipped silently — a render that has
# not happened yet writes one later.
BATCH_BENCH_FILES = ["SAMPLES/animegen-bench.jsonl", "SAMPLES/batch-bench.jsonl",
                     "SAMPLES/ti2v5b-modes.jsonl"]

# A bench row's `label` is whatever the renderer's --bench-label said, and the
# renderers spell the model differently from the gallery filenames: wan_i2v
# defaults to its MODELS key "ti2v-5b" while every clip on disk is named
# "ti2v5b-...". Those are the same model, and until this map existed they were two
# different tables — the batch section titled itself with the raw label "ti2v-5b",
# found no registry entry, and never associated with the gallery group holding the
# clips those very rows measured. Keys are lowercased labels; anything unlisted
# passes through unchanged, so an unregistered model still gets its own table.
LABEL_ALIAS = {
    "ti2v-5b": "ti2v5b",
    "ti2v5b": "ti2v5b",
    "wan2.2-ti2v-5b": "ti2v5b",
    "ltx-2.3": "ltx23",
    "ltx2.3": "ltx23",
    "ltx23": "ltx23",
    "ltx23-distilled": "ltx23",
    # The fp8-cast build is a SEPARATE row, not a spelling of the bf16 one. Same
    # repo and same licence, different numerics and (the point of it) a different
    # offload strategy — folding the two together would put a resident-transformer
    # timing in the same column as a sequential-offload timing and read as a batch
    # or recipe effect. Three spellings because three things name it: the gallery
    # filename stem, --bench-label, and the sidecar's short model key.
    "ltx23fp8": "ltx23fp8",
    "ltx23-fp8": "ltx23fp8",
    "ltx23-distilled-fp8": "ltx23fp8",
    "animegen": "animegen",
    "animegen-i2v": "animegen",
}

# The b1 comparator for a batch series that measured b2 and never re-measured b1,
# JOINED from a real run in another file rather than typed in or left blank.
#
# The 5B production series is the case. Last night's probe measured b2 only —
# there was no reason to re-measure b1, because the SAME recipe at b1 had already
# run that afternoon as the T1/T2/T3 parameter sweep: same 704x1280, same 61
# frames, same 14 steps, same guidance 5.0, same seed 20260732. T1-shift5.0 IS
# that b1 point. A batch table with one row reads as if nothing is known about b1,
# which is false and is the kind of gap that gets filled with an estimate later.
#
# JOINED, not synthesised, and the difference is the whole point: sample_s, s/step,
# peak VRAM and host peak cross over verbatim from bench-t1t2t3.jsonl, throughput
# is the one division the sweep row does not carry, and the cell names the file it
# came from. NOTHING is written back to any jsonl — the corpus stays measured-runs-
# only, and a joined view is not a new measurement. Cross-check that it is the same
# run: SAMPLES/ti2v5b-production-b1-s20260732.mp4 is byte-identical to
# bench-T1T2T3/T1-shift5.0.mp4, and its sidecar independently records the two
# derived figures (0.0151 and 66.3) this join computes.
BATCH_B1_JOIN = {
    ("ti2v5b", "production"): ("bench-T1T2T3/bench-t1t2t3.jsonl", "T1-shift5.0"),
}

# The same join, from a CLIP SIDECAR instead of a bench file, for a series whose
# b1 ran before `--bench-jsonl` existed and therefore has no row in any file.
#
# LTX production is the case. The b1 render of 2026-08-04 wrote its throughput
# into its own sidecar and nothing else; the b2 probe of 2026-08-05 then produced
# a table with one row, reading as if b1 were unknown — which it is not, and which
# is how a 1.14x gain ends up quoted with nothing under it.
#
# The path names the GALLERY copy, and that is deliberate. The b1 run is usually
# cited as `SAMPLE-ltx23-b01.mp4.meta.yaml`, and that repo-root sidecar carries
# the recipe but NOT the two derived figures — 0.0251 and 39.9 live only in the
# gallery copy's sidecar. The two mp4s are the same bytes (asserted at build time,
# below), so it is one run under two filenames; the Source column names the file
# that actually holds the number, because that is the only thing that column is
# for. NOTHING is written back to any bench file.
#
# A sidecar has no sample_s, no s/step and no VRAM field. Those cells stay
# em-dashes: borrowing them from the prose table would promote a document figure
# into a measured row, which is what MODEL-COMPARISON rule 2 forbids.
BATCH_B1_SIDECAR = {
    ("ltx23", "production"): "SAMPLES/ltx23-production-b1-s20260732.mp4",
}

# The un-batched LTX clip the sidecar join reads is meant to be the same artifact
# as the repo-root sample. If that ever stops being true the join is quoting one
# run's numbers under another run's provenance, so the page checks rather than
# trusts, and says so in the note under the table.
SIDECAR_JOIN_TWIN = {
    "SAMPLES/ltx23-production-b1-s20260732.mp4": "SAMPLE-ltx23-b01.mp4",
}

GALLERY_NAME = re.compile(
    r"^(?P<model>[A-Za-z0-9]+)-(?P<mode>preview|production)"
    r"-b(?P<batch>\d+)-s(?P<seed>\d+)$"
)

# The money row: same beat, same still, same seed, one clip per model.
HERO_SEED = "20260732"

# ---------------------------------------------------------------- registry ----
# Per-model context that is NOT in any sidecar: what the build is, what its
# licence permits, and the offload strategy its VRAM figures measure. The last is
# mandatory (MODEL-COMPARISON reading rule 1) — an unlabelled peak gets misread as
# card capacity the first time it is quoted.
MODELS = {
    "ti2v5b": {
        "title": "Wan 2.2 TI2V-5B",
        "build": "Wan-AI/Wan2.2-TI2V-5B-Diffusers, diffusers 0.39.0 bf16, torch 2.11.0+cu128",
        "offload": "model_cpu_offload",
        "licence": "Apache-2.0, output rights disclaimed — CLEAR",
        "role": "the incumbent production model — everything shipped so far is this",
    },
    "ltx23": {
        "title": "LTX-2.3 distilled",
        "build": "diffusers/LTX-2.3-Distilled-Diffusers, bf16, two-stage on-recipe",
        "offload": "sequential-offload",
        "licence": "LTX-2 Community License Agreement — CANDIDATE, watch-only under D16",
        "role": "fastest measured path; host-exclusive (it evicted the farm worker)",
    },
    "ltx23fp8": {
        "title": "LTX-2.3 distilled — fp8 cast",
        "build": "diffusers/LTX-2.3-Distilled-Diffusers, the SAME bf16 weights cast "
                 "to fp8 storage / bf16 compute at load (enable_layerwise_casting, "
                 "norms excluded by the model's own skip pattern), two-stage on-recipe",
        # The whole reason the entry exists: the cast takes the transformer from
        # ~38GB to ~19.8GiB, which is what lets it stay on a 23.89GiB card for the
        # denoise loop instead of being streamed module-by-module.
        "offload": "model_cpu_offload + fp8 layerwise",
        "licence": "LTX-2 Community License Agreement — CANDIDATE, watch-only under "
                   "D16 (same document as the bf16 build; casting our own copy "
                   "changes no term)",
        "role": "the same candidate with the offload brake off — tests whether LTX's "
                "measured speed was a model result or an offloading floor",
    },
    "animegen": {
        "title": "AnimeGen-I2V (A14B)",
        "build": "aidealab/AnimeGen-I2V, Wan2.2-I2V-A14B finetune, per-expert fp8 "
                 "layerwise cast, text encoder evicted to its own process",
        "offload": "model_cpu_offload + fp8 layerwise",
        "licence": "AnimeGen Apache-2.0 (real LICENSE file); Lightning LoRAs ship NO "
                   "LICENSE — UNVERIFIED, evaluation render only, publication gated",
        "role": "the anime-native candidate — first clips this box has ever produced",
    },
}
MODEL_ORDER = ["ti2v5b", "ltx23", "ltx23fp8", "animegen"]

# Figures that exist only in pipeline/research/MODEL-COMPARISON.md, because the
# run that produced the clip wrote them to the prose table and not to the sidecar.
# Tagged on the page with their source so the provenance footer stays true.
DOC = "MODEL-COMPARISON.md"
DOC_ONLY = {
    # keyed by clip stem
    "ltx23-production-b1-s20260732": {
        "vram": "4.1GB torch / 2.5GB device of 26GB",
        "host": "60.8GB phys / 67.1GB commit of 68.1GB",
        "defects": "saturation 0.264, no channel cast, 0/64 frozen frames",
    },
    "SAMPLE-ltx23-b01": {
        "vram": "4.1GB torch / 2.5GB device of 26GB",
        "host": "60.8GB phys / 67.1GB commit of 68.1GB",
        "defects": "saturation 0.264, no channel cast, 0/64 frozen frames",
    },
    # The bench row carries this clip's vram/host, so those keys would be ignored
    # here — what it CANNOT carry is the residency number, and residency is the
    # whole question the sample was run to answer. device_gb in the bench row reads
    # 2.6GB for this clip, which is the post-run reading after the card drained and
    # would be read as "streamed"; the truth is an external nvidia-smi trace.
    "ltx23fp8-production-b1-s20260732": {
        "defects": "transformer RESIDENT — 21346 MiB at 97% util through stage 1 "
                   "and 22920 of 24463 MiB at 99% through stage 2 (telemetry.csv, "
                   "external, 10s cadence), against ~2.5GB streamed; resident "
                   "per-stage, not across the run — 362 MiB between the stages as "
                   "model_cpu_offload returns the transformer to host; "
                   "fp8 cast 35.37 -> 17.69 GiB "
                   "in 139s; same-seed drift vs the bf16 b1 rms 11.93/255 against a "
                   "0.93 encode-noise control; 0/64 frozen frames; channel means "
                   "R-2.54 G-2.81 B+0.12",
    },
    "animegen-preview-b1-s20260732": {
        "defects": "saturation 0.636, channel means R44/G26/B68, std 53.8; "
                   "motion median 0.52, 0/32 barely-moving",
    },
    "animegen-preview-b2-s20260732": {
        "defects": "batch-fidelity check vs b1 at the same seed: mean frame-diff "
                   "0.62 and max 1.63 match to 2dp, median 0.55 vs 0.52",
    },
}

# Motion metric per 5B bench clip — repo metric, collect_farm.py --measure.
# Measurements, not verdicts (MODEL-COMPARISON §3.5). Source: MODEL-COMPARISON.md.
BENCH_MOTION = {
    "T1-shift5.0": ("1.16", "0/60"),
    "T1-shift3.0": ("0.97", "0/60"),
    "T1-shift8.0": ("1.18", "0/60"),
    "T2-neg-huamian": ("0.83", "0/60"),
    "T3-motion-only": ("1.05", "0/60"),
    "T3-empty-prompt": ("0.72", "0/60"),
}

# What the bench row was testing, in one line, for the parameter-findings table.
BENCH_READING = {
    "T1-shift5.0": "The shipped config. T1's A and B coincide: the repo's "
                   "scheduler_config.json already ships flow_shift 5.0, which IS "
                   "Alibaba's 720p value. \"We never set shift\" was true and harmless.",
    "T1-shift3.0": "Alibaba's 480p value, and FastWan's flow_shift. 6 of 14 steps "
                   "above t=900.",
    "T1-shift8.0": "kijai's shipped 5B I2V example. 9 of 14 steps above t=900 — the "
                   "most trajectory spent establishing large-scale motion.",
    "T2-neg-huamian": "One appended negative term (画面), verified a pure append: "
                      "618 → 622 chars, nothing reordered. Not combined with "
                      "--no-shake-neg.",
    "T3-motion-only": "Positive replaced by present-progressive motion only, statics "
                      "stripped, no camera invention, 36 words. STYLE prefix kept so "
                      "the clip is a one-variable delta.",
    "T3-empty-prompt": "prompt=\"\". NOT Alibaba's empty-prompt mode — diffusers has "
                       "no system-prompt routing, so this is a literally empty string "
                       "and must never be read as testing their \"bring the image to "
                       "life\" brief.",
}

# Hand-written reading of a batch-scaling row, keyed by bench label then batch.
# ONLY AnimeGen has one, because only AnimeGen's cliff has been investigated. A
# model whose rows land here without an entry gets the cells and no prose: an
# unexamined table is allowed to be silent, and inventing a reading for it would
# be exactly the estimate-as-measurement MODEL-COMPARISON rule 2 forbids.
BATCH_READING = {
    ("animegen", "preview"): {
        1: "Baseline.",
        2: "<b>The optimum.</b> 2x the output for 1.39x the time — 1.44x b1. With "
           "model_cpu_offload the streamed weights dominate, so a second latent "
           "costs only +1.8GB and is nearly free. Batch fidelity holds: at the "
           "same seed, slot 0 matches b1 on mean and max frame-difference to 2dp.",
        4: "<b>A false economy.</b> Not an OOM — a spill. At ~90% of the card the "
           "WDDM sysmem fallback quietly pages to host RAM instead of raising, so "
           "the run 'succeeds' while going slower than batch 1.",
    },
}

# The reading under the AnimeGen batch table. Kept as prose because it carries a
# resolved data conflict, and a resolved conflict has to stay visible or the same
# two numbers get re-litigated next week.
ANIMEGEN_BATCH_NOTE = (
    '<p class="note" style="margin-top:10px"><b>65.2 → 45.3 → 109.3</b> seconds of '
    'wall per second of video. Batch 2 is the whole win; batch 4 is worse than doing '
    'them one at a time. <b>These cells once disagreed with MODEL-COMPARISON.md\'s b4 '
    'row</b>, which carried 99.3s/step and 24.1GB (94%) against the jsonl\'s '
    '150.32s/step and 23.2GB (90.3%). <b>Resolved 2026-08-05: the jsonl was right.</b> '
    'The document\'s row had been written at 23:20:37 while the b4 run was still '
    'sampling — a mid-run extrapolation, tagged MEASURED-BY-US, five minutes before the '
    'run actually finished at ~23:25, which is precisely the promotion its own rule 2 '
    'forbids. The document row is now corrected to the measured figures; the direction '
    'never changed, only the size of the cliff.</p>'
)

# ---------------------------------------------------------------- coverage ----
# The batch coverage matrix: every model x mode x batch, with a REASON in every
# cell that holds no measurement (founder's standing requirement — batch results
# for each model, gaps EXPLICIT rather than silent). A table that shows only the
# points somebody got round to running reads as if the rest were never considered,
# and that is how the run that bugchecked the host gets scheduled a second time.
#
# The MEASURED cells are derived from the loaded bench rows — throughput, and the
# multiple of that same series' own b1 — so they cannot drift from the tables
# above them. Only the reasons are written here, because a reason is a decision
# and a decision has no sidecar; each carries its own as-of, the same discipline
# as NO_SAMPLE_YET. Every figure quoted inside one appears in a table on this page.
COVERAGE_BATCHES = [1, 2, 4]
COVERAGE_MODES = ["preview", "production"]

#
# Each value is (short marker, the reason, as-of). The marker is what a reader
# scanning the row sees; the reason is why nobody should schedule the cell.
COVERAGE_GAPS = {
    ("animegen", "production", 2): (
        "does not fit",
        "Derived from the measured VRAM slope rather than attempted: "
        "the preview series pays +1.8GB for its second latent at 480x832/33f, and "
        "the production latent is ~4.2x that volume, which puts a second one near "
        "~30GB against a 25.7GB card. b1 alone already sits at 23.2GB (90%).",
        "derived 2026-08-05 from SAMPLES/animegen-bench.jsonl"),
    ("animegen", "production", 4): (
        "does not fit",
        "Same wall, twice as far past it. b2 does not fit, so b4 cannot; nothing "
        "here was run.",
        "derived 2026-08-05 from SAMPLES/animegen-bench.jsonl"),
    ("ti2v5b", "preview", 4): (
        "banned with production b4",
        "The run that took the host down was this model at b4, and the preview "
        "recipe differs from the production one only in step count (6 against 14), "
        "not in the latent count that decides memory. Nothing was run here.",
        "banned 2026-08-05, probe-5b-b4.log"),
    ("ti2v5b", "production", 4): (
        "DNF — took the host down",
        "2 of 14 steps at ~118-122s/step, then "
        "Kernel-Power 41 at 06:07:05 on 2026-08-05, the box's second unclean reboot "
        "that day; GPU 24102 of 24463 MiB at 98.5% when it died, host commit pinned "
        "at its ceiling while physical was being reclaimed. No clip, no sidecar, no "
        "row anywhere. BANNED — reopening it is founder-reserved, because the last "
        "attempt cost a bugcheck.",
        "probe-5b-b4.log, 2026-08-05"),
    ("ltx23fp8", "production", 1): (
        "measured — 73.3s, 0.0369 s/s, NOT YET SCREENED",
        "The sample ran on 2026-08-05 and answered both questions it was set. The "
        "two hook systems DO coexist: rc=0 on the first attempt, no fallback to "
        "--offload group needed. The weights DO fit: the cast took the transformer "
        "from 35.37 to 17.69 GiB in 139s, and an external telemetry trace (10s "
        "cadence) shows 21346 MiB at 97% util through stage 1 and 22920 of 24463 "
        "MiB at 99% through stage 2 — the transformer is resident, against ~2.5GB "
        "when it is streamed. Residency is per-stage: between the two stages VRAM "
        "drops to 362 MiB, model_cpu_offload returning the transformer to host "
        "while the latent upsampler runs. "
        "That is a 1.5GB margin on the card, which is the reason b2 is not "
        "automatic. Speed came with it: 73.3s against the bf16 b1's 108.1s, 1.47x. "
        "The host did NOT get cheaper — peak phys 64.6GB against bf16's 60.8, peak "
        "commit 97.0GB against 67.1, because the cast retains the bf16 storages it "
        "replaces. The predicted ~34GB resident host figure did not happen. "
        "SCREENING IS STILL OWED: the clip differs from the bf16 reference by rms "
        "11.93/255 against a 0.93 encode-noise control, which is real drift and "
        "slightly more than batch=2 cost. Nothing above b1 may be scheduled until "
        "the founder has looked at it.",
        "SAMPLES/batch-bench.jsonl + the b1 fp8 sidecar + probe-ltx-fp8.log "
        "+ fp8-fidelity-20260805.log, 2026-08-05"),
    ("ltx23fp8", "production", 2): (
        "not scheduled — b1 screening first",
        "No batch point on this build may be scheduled before its b1 sample has "
        "been SCREENED, and b1 having now RUN is not that. b1 fits, but with 1543 "
        "of 24463 MiB spare on the card, and a second latent in the same resident "
        "loop spends that margin on activations rather than on weights — this is "
        "the one batch step where the card, not the host, is the wall. The bf16 "
        "build's own b1 -> b2 host slope (60.8 -> 64.2GB phys) still does not "
        "transfer: it was measured with the transformer streamed, and b1 here "
        "already sits at 64.6GB phys / 97.0GB commit before any second latent.",
        "derived 2026-08-05 from the b1 fp8 bench row + probe-ltx-fp8.log"),
    ("ltx23fp8", "production", 4): (
        "closed by inheritance — host RAM",
        "The bf16 build's b4 is closed on a host-RAM slope that the fp8 cast does "
        "not change: the cast shrinks what sits on the CARD, not the per-latent "
        "host cost. Nothing here will be run unless b1 and b2 say otherwise.",
        "derived 2026-08-05 from SAMPLES/batch-bench.jsonl + the b1 sidecar"),
    ("ltx23", "production", 4): (
        "closed — host RAM, not VRAM",
        "LTX peaks at 7.2GB of 25.7GB at b2, so the card is not the constraint. "
        "Host physical went 60.8 → 64.2GB from "
        "b1 to b2, and +3.4GB per extra latent puts b4 past the 68.1GB this box "
        "has. The render is already host-exclusive: at b1 it evicted the farm worker.",
        "derived 2026-08-05 from SAMPLES/batch-bench.jsonl + the b1 sidecar"),
}

# A whole (model, mode) pair that does not exist, as opposed to a batch point
# inside one that does. Rendered as one spanning cell.
COVERAGE_MODE_ABSENT = {
    ("ltx23", "preview"): (
        "no preview recipe defined",
        "Every LTX figure on this "
        "page is the two-stage production recipe; there is no cheap variant to "
        "measure, so this row is empty by definition rather than by failure. It is "
        "also the least urgent gap on the page — LTX production already runs at "
        "35.1s per video-second, inside the iterate-in-minutes loop.",
        "2026-08-05"),
    ("ltx23fp8", "preview"): (
        "no preview recipe defined",
        "Inherited from the bf16 build, and for the same reason: the fp8 cast is a "
        "change of storage dtype and offload strategy, not of recipe. There is no "
        "cheap LTX variant to measure, so this row is empty by definition.",
        "2026-08-05"),
}

# Under the batch tables. The 2026-08-05 LTX b2 probe checked whether a batched
# slot reproduces the un-batched clip, and the answer changes how a batch result
# may be used — so it sits with the tables it qualifies, not in a footnote.
BATCH_FIDELITY_NOTE = (
    '<p class="note" style="margin-top:14px"><b>A batched slot is not a re-render '
    'of the un-batched clip.</b> Measured 2026-08-05 on the LTX b2 probe: slot 0 '
    'against <code>SAMPLE-ltx23-b01</code> — same seed, byte-identical inputs, '
    'identical conditioning frame — comes out at <b>RMS 10.35 of 255</b>, where '
    're-encoding the reference against itself scores <b>0.93</b>. Eleven times the '
    'control, and the drift grows with denoise depth. The batch is doing real work: '
    'the slots differ from each other properly and the embeds expansion is confirmed '
    'working, so this is neither one clip rendered twice nor a broken batch. Read it '
    'as: <b>batched output is real and distinct, but it is not a drop-in re-render '
    'of an approved un-batched clip</b> — a beat re-rendered inside a batch is a new '
    'clip and needs screening again. Two things it does not say. It does not '
    'contradict AnimeGen\'s "batch fidelity holds" above: that was mean and max '
    'frame-difference, a motion statistic which this drift would also pass, and that '
    'pair has never been compared per-pixel. And it does not prove batching is the '
    'cause — <b>whether two UN-batched runs reproduce each other has not been '
    'tested</b>, so there is no baseline for this metric yet.</p>'
)

# ------------------------------------------------------------------ status ----
# Hardcoded for now: no sidecar exists for a render that has not happened. Each
# row carries the as-of stamp of the source that says so.
NO_SAMPLE_YET = [
    {
        "model": "IndexTeam/Index-anisora V3.2",
        "plan": "T8",
        "why": "Download in flight, then a disk bake. The release is fp32 at ~57GB "
               "per expert (~126GB the pair) — one fp32 expert nearly fills 64GB, so "
               "it needs bf16/fp8 conversion on disk before the first run can start.",
        "extra": "Licence is Apache-2.0 PLUS bilibili additional restrictions, not "
                 "plain Apache-2.0; clause 4 (indemnity) is not fine-tuning-scoped. "
                 "Their own VBench Motion is 45.59 — below vanilla Wan.",
        "as_of": "STATE.md, 2026-08-04",
    },
    {
        "model": "stock Wan2.2-I2V-A14B + lightx2v Lightning LoRAs",
        "plan": "T7",
        "why": "Pending the fp8 bake. The load path is the gate, measured tonight: "
               "~40GB of live weights took 128.7GB of commit charge because the "
               "runtime fp8 cast retains the bf16 storages it replaces. Attempt 1 "
               "died at step 0, 13GB short. The fix is baking fp8 experts to disk in "
               "processes that exit, so nothing bf16 is ever resident.",
        "extra": "Scheduled only if AnimeGen's look fails — same architecture, no "
                 "anime finetune.",
        "as_of": "measured 2026-08-04, bench-a14b.log",
    },
    {
        "model": "FastWan 3-step LoRA on TI2V-5B",
        "plan": "T5",
        "why": "Pending. No new base weights (it is a LoRA on the 5B we already run), "
               "so this is the cheapest row left — but the LoRA needs licence_gate.py "
               "before download.",
        "extra": "Two things decide how to read it: at guidance 1 the entire negative "
                 "prompt goes inert, and distill LoRAs are documented to slow motion "
                 "— the exact defect the K recipe was rejected for on 2026-08-03.",
        "as_of": "ACTION-PLAN §1 T5, 2026-08-04",
    },
    {
        "model": "Kandinsky 5.0",
        "plan": "—",
        "why": "Skipped unless there is spare time. Its default negative prompt "
               "pushes against 2D animation, which is the whole look.",
        "extra": "Priced as a non-licence dead end in ACTION-PLAN §6.",
        "as_of": "ACTION-PLAN §6, 2026-08-04",
    },
]

STATUS_FOOTNOTE = (
    "T4 (SageAttention 2.2.0 sm_120) has no sample either, but it is tooling rather "
    "than a model: it changes no look and would move every throughput figure on this "
    "page by a CLAIMED ~35%, measured by its author on our exact card. If it lands, "
    "the numbers here are the before."
)


# ------------------------------------------------------------------ helpers ---
def load_sidecar(mp4: Path):
    """Return the parsed *.mp4.meta.yaml, or None. Never guesses on failure."""
    side = mp4.with_suffix(".mp4.meta.yaml")
    if not side.exists():
        return None
    try:
        return yaml.safe_load(side.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:  # a malformed sidecar is a gap, not a crash
        return {"_parse_error": str(exc)}


def load_jsonl(path: Path):
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            print(f"  ! unparsed jsonl line in {path.name}: {exc}", file=sys.stderr)
    return rows


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# What a cell says when the row measured nothing for it. An em-dash, not "None"
# and not a zero: a gap has to LOOK like a gap (§3.4, "record `no data` when it
# is"), and the one thing it must never look like is a number.
DASH = "—"


def num(v, digits=1, unit=""):
    """Format a measured figure, or the gap mark. NEVER the string "None".

    The unit belongs to this function and not to the f-string that calls it,
    which is the whole fix: `f"{num(x)}GB"` renders "NoneGB" the moment x is null,
    and null is a normal value in a bench row — bench_row() writes null for every
    field the run did not measure, on purpose. A two-stage LTX row carries a null
    s_per_step by design, and the 5B rows carried a null shift for a week. Cells
    like that printed literal "None" and "NoneGB" on this page.
    """
    if v is None or v == "":
        return DASH
    try:
        return f"{float(v):.{digits}f}".rstrip("0").rstrip(".") + unit
    except (TypeError, ValueError):
        return escape(str(v)) + unit


def model_key(label):
    """Bench label -> the page's model key. Unknown labels pass through."""
    return LABEL_ALIAS.get(str(label or "").lower(), str(label or "unlabelled"))


def per_video_second(row):
    """s(wall) per 1s of video, DERIVED from the row's own sample_s and video_s.

    Not read from `compute_per_video_s`, because that column is not one quantity.
    The AnimeGen and 5B-modes files write sample_s/video_s there (seconds per
    second of video, which is what the name says); wan_i2v's bench_row call writes
    sample_s/batch (seconds per CLIP) — so batch-bench.jsonl's 5B b2 row says
    382.3 where the same run's sidecar says 150.4. Both numbers are true and they
    are answers to different questions, which is exactly why the page must not
    print whichever one happens to be in the file under a header that names only
    one of them. Two measured fields and one division say it unambiguously.
    """
    s, v = row.get("sample_s"), row.get("video_s")
    try:
        if s and v:
            return round(float(s) / float(v), 1)
    except (TypeError, ValueError, ZeroDivisionError):
        return None
    # A row joined from a clip sidecar has no sample_s to divide — the renderer
    # wrote the quotient itself, under `compute_s_per_video_s`, a name that means
    # one thing in one writer's output and is not the ambiguous jsonl column this
    # function exists to avoid. Only a sidecar join sets this key.
    return row.get("_pvs_sidecar")


def joined_b1_row(src_file, name):
    """The b1 row of a batch table, lifted from a single-clip bench file."""
    src = {r.get("name"): r for r in load_jsonl(REPO / src_file)}.get(name)
    if not src or not src.get("sample_s"):
        return None
    frames, sample_s = src.get("frames"), float(src["sample_s"])
    # 24fps is this page's standing derivation for a row that records frames and
    # not seconds (see frames_of), and it is the fps every clip in the comparison
    # was rendered at. Tagged as derived wherever it shows.
    video_s = round(float(frames) / 24.0, 3) if frames else None
    row = dict(src)
    row.update({
        "batch": 1, "seeds": [src.get("seed")] if src.get("seed") else [],
        "video_s": video_s,
        "throughput_s_per_s": (round(video_s / sample_s, 4) if video_s else None),
        "compute_per_video_s": (round(sample_s / video_s, 1) if video_s else None),
        "ok": True,
        # a literal · and not the entity: this string is printed raw in the source
        # cell and escaped in the note under the table, and only one of those two
        # is right for an entity.
        "_src": f"{Path(src_file).name} · {name}",
        "_joined": True,
        "_joined_from": "bench row",
    })
    return row


def joined_b1_row_from_sidecar(mp4_rel):
    """The b1 row of a batch table, lifted from the b1 clip's own sidecar.

    ONLY what the sidecar wrote. A render sidecar records the recipe and the two
    throughput figures the render derived; it has no sample_s, no s/step and no
    VRAM line, and this returns no key for any of them, so num() prints the gap
    mark. That is the point — a joined row that filled those in from the prose
    table would look measured and would not be.
    """
    mp4 = REPO / mp4_rel
    meta = load_sidecar(mp4) or {}
    if "_parse_error" in meta or not meta.get("throughput_s_video_per_s_wall"):
        return None
    twin = SIDECAR_JOIN_TWIN.get(mp4_rel)
    same_bytes = bool(twin and (REPO / twin).exists()
                      and sha(mp4) == sha(REPO / twin))
    return {
        "batch": int(meta.get("batch") or 1),
        "seeds": [meta["seed"]] if meta.get("seed") is not None else [],
        "mode": meta.get("mode"),
        "size": meta.get("size"),
        "steps": meta.get("steps"),
        "video_s": meta.get("seconds"),
        "throughput_s_per_s": meta["throughput_s_video_per_s_wall"],
        "ok": True,
        "_src": f"{mp4.name}.meta.yaml",
        "_joined": True,
        "_joined_from": "sidecar",
        "_pvs_sidecar": meta.get("compute_s_per_video_s"),
        "_twin": twin,
        "_twin_same_bytes": same_bytes,
    }


def collect():
    """Glob every clip, attach its sidecar and bench row, flag byte-duplicates."""
    # Batch-scaling rows. Same schema in every file; the `label` field names the
    # model, so a new model's rows land in their own table without a code change.
    # Files that do not exist yet are simply absent — a render writes them later.
    batch_rows = []
    for name in BATCH_BENCH_FILES:
        for r in load_jsonl(REPO / name):
            r.setdefault("_src", Path(name).name)
            batch_rows.append(r)
    # Grouped by (model key, MODE), not label alone. Batch scaling only means
    # anything within one recipe: AnimeGen's preview series is 480x832/33f and its
    # production row is 704x1280/61f, and putting a 214.6s/video-second production
    # point in the same column as a 65.2s preview point invites reading the recipe
    # change as a batch effect. Same discipline as MODEL-COMPARISON's "record the
    # batch and the mode with the number, always".
    batch_groups = {}
    for r in batch_rows:
        key = (model_key(r.get("label")), str(r.get("mode") or "?"))
        batch_groups.setdefault(key, []).append(r)
    # A joined b1 only lands where the series actually lacks one — it must never
    # displace a row somebody measured. Two sources, one rule: another file's
    # bench row, or the b1 clip's own sidecar.
    for key, (src_file, name) in BATCH_B1_JOIN.items():
        rows = batch_groups.get(key)
        if not rows or any(r.get("batch") == 1 for r in rows):
            continue
        joined = joined_b1_row(src_file, name)
        if joined:
            joined.setdefault("mode", key[1])
            rows.append(joined)
    for key, mp4_rel in BATCH_B1_SIDECAR.items():
        rows = batch_groups.get(key)
        if not rows or any(r.get("batch") == 1 for r in rows):
            continue
        joined = joined_b1_row_from_sidecar(mp4_rel)
        if joined:
            joined.setdefault("mode", key[1])
            rows.append(joined)
    for rows in batch_groups.values():
        rows.sort(key=lambda r: r.get("batch") or 0)
    t1t2t3 = {r["name"]: r for r in load_jsonl(REPO / "bench-T1T2T3/bench-t1t2t3.jsonl")}

    seen, clips, notes = {}, [], []
    for pattern in CLIP_GLOBS:
        for mp4 in sorted(REPO.glob(pattern)):
            rel = mp4.relative_to(REPO).as_posix()
            stem = mp4.stem
            meta = load_sidecar(mp4)
            if meta is None:
                notes.append(f"{rel}: no sidecar — rendered with its numbers blank")
            elif "_parse_error" in meta:
                notes.append(f"{rel}: sidecar failed to parse — {meta['_parse_error']}")

            digest = sha(mp4)
            dup_of = seen.get(digest)
            seen.setdefault(digest, rel)

            m = GALLERY_NAME.match(stem)
            if m:
                label, mode = model_key(m["model"]), m["mode"]
                batch, seed = int(m["batch"]), m["seed"]
            else:
                # bench clips and the root sample: the sidecar is the source
                label = None
                mode = (meta or {}).get("mode")
                batch = (meta or {}).get("batch")
                seed = str((meta or {}).get("seed", "")) or None
                if stem.startswith("SAMPLE-"):
                    label = model_key(stem.split("-")[1])
                # The T1/T2/T3 sidecars predate the `mode:` field. Their recipe is
                # the production one (704x1280, 61f, 14 steps, guidance 5.0) and one
                # of the six IS the production clip under another name, so calling
                # them production is a read of the recipe, not a guess.
                if mode is None and mp4.parent.name == "bench-T1T2T3":
                    mode = "production"

            bench = None
            task = str((meta or {}).get("task", ""))
            if stem in t1t2t3:
                bench = t1t2t3[stem]
            elif task.startswith("bench-t1t2t3/"):
                bench = t1t2t3.get(task.split("/", 1)[1])
            elif label and batch:
                for row in batch_groups.get((label, str(mode)), []):
                    # ok is False on a run that DIED. Its numbers describe a
                    # failure, not this clip, so they never get attached to one.
                    if row.get("batch") == batch and row.get("ok", True):
                        bench = row
                        break

            clips.append({
                "rel": rel, "stem": stem, "dir": mp4.parent.name if mp4.parent != REPO else ".",
                "label": label, "mode": mode, "batch": batch, "seed": seed,
                "meta": meta or {}, "bench": bench, "dup_of": dup_of,
                "size_mb": mp4.stat().st_size / 1e6,
                "mtime": datetime.fromtimestamp(mp4.stat().st_mtime),
            })
    return clips, batch_groups, list(t1t2t3.values()), notes


def model_of(clip):
    """Model key for grouping. Falls back to the sidecar's model field."""
    if clip["label"]:
        return clip["label"]
    model = str(clip["meta"].get("model", "")).lower()
    for key in MODELS:
        if key in model.replace("-", "").replace("_", ""):
            return key
    if "ti2v-5b" in model or "ti2v5b" in model:
        return "ti2v5b"
    if "ltx" in model:
        # The MODELS loop above cannot separate these two: the sidecar spells the
        # repo "LTX-2.3-Distilled-Diffusers", and stripping dashes leaves "ltx2.3"
        # — the dot survives, so neither "ltx23" nor "ltx23fp8" is a substring and
        # both builds fall through to here. Without this line an fp8 clip whose
        # filename is not gallery-shaped would be grouped under the bf16 build and
        # its timing read as the bf16 model's.
        return "ltx23fp8" if "fp8" in model else "ltx23"
    return "unregistered"


def video_seconds(clip):
    secs = clip["meta"].get("seconds")
    if secs is None and clip["bench"]:
        secs = clip["bench"].get("video_s")
    return secs


def frames_of(clip):
    if clip["bench"] and clip["bench"].get("frames"):
        return clip["bench"]["frames"], ""
    secs = video_seconds(clip)
    if secs:
        return round(float(secs) * 24), " (derived @24fps)"
    return None, ""


def compute_per_video_s(clip):
    """s(wall) of sampling per 1s of video, and where the figure came from."""
    meta, bench = clip["meta"], clip["bench"]
    if meta.get("compute_s_per_video_s"):
        return num(meta["compute_s_per_video_s"]), "sidecar"
    if bench and bench.get("compute_per_video_s"):
        return num(bench["compute_per_video_s"]), "bench jsonl"
    if bench and bench.get("sample_s") and video_seconds(clip):
        return num(float(bench["sample_s"]) / float(video_seconds(clip))), \
            "derived: sample_s / video_s"
    return None, None


# --------------------------------------------------------------------- HTML ---
CSS = """
:root{
  --bg:#0b0d10; --panel:#14181d; --panel2:#191e24; --line:#252c34;
  --ink:#e7ebef; --dim:#8e9aa6; --dimmer:#6b7681;
  --prod:#5fd3a3; --prev:#e8b23f; --hot:#7fb2ff; --warn:#ff8f6b;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,monospace;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1500px;margin:0 auto;padding:28px 22px 90px}
h1{font-size:28px;line-height:1.2;margin:0 0 6px;letter-spacing:-.02em}
h2{font-size:19px;margin:0 0 4px;letter-spacing:-.01em}
h3{font-size:15px;margin:0 0 8px}
p{margin:0 0 10px}
a{color:var(--hot)}
.sub{color:var(--dim);font-size:13px;margin:0 0 22px}
section{margin:0 0 38px}
.shead{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;
  border-bottom:1px solid var(--line);padding-bottom:8px;margin-bottom:16px}
.shead .count{font:12px/1 var(--mono);color:var(--dimmer)}
.rules{display:flex;gap:14px;flex-wrap:wrap;margin:0 0 24px}
.rule{flex:1 1 320px;background:var(--panel);border:1px solid var(--line);
  border-left:3px solid var(--hot);border-radius:8px;padding:13px 15px}
.rule b.rh{display:block;margin-bottom:4px;font-size:13px;letter-spacing:.03em;
  text-transform:uppercase;color:var(--hot)}
.rule p{margin:0;font-size:13.5px;color:#cdd5dd}
nav{display:flex;gap:7px;flex-wrap:wrap;margin:0 0 22px}
nav a{font:12px var(--mono);color:var(--dim);text-decoration:none;background:var(--panel);
  border:1px solid var(--line);border-radius:6px;padding:5px 10px}
nav a:hover{color:var(--ink);border-color:#3d4854}
.strip{display:flex;flex-wrap:wrap;gap:16px}
.card{width:340px;flex:0 1 340px;background:var(--panel);border:1px solid var(--line);
  border-radius:10px;overflow:hidden;display:flex;flex-direction:column}
.card.wide{width:400px;flex:0 1 400px}
/* 9:16 clips are tall. Cap the height so three sit side by side in one Mac
   screenful — object-fit letterboxes into black, which is the page background. */
video{display:block;width:100%;background:#000;height:min(52vh,470px);
  object-fit:contain}
.hero video{height:min(60vh,560px)}
.cap{padding:11px 13px 13px;display:flex;flex-direction:column;gap:8px}
.title{display:flex;align-items:center;gap:7px;flex-wrap:wrap}
.title b{font-size:14px}
.badge{font:10.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.06em;
  padding:3px 6px;border-radius:4px;border:1px solid}
.b-prod{color:var(--prod);border-color:#2e6b55;background:#12241d}
.b-prev{color:var(--prev);border-color:#6b552e;background:#231d12}
.b-dup{color:var(--dimmer);border-color:var(--line);background:#111418}
.file{font:11px/1.4 var(--mono);color:var(--dimmer);word-break:break-all}
.rowsub{font:11.5px/1.45 var(--mono);color:var(--dim)}  /* prose, so no break-all */
table.kv{width:100%;border-collapse:collapse;font:11.5px/1.45 var(--mono)}
table.kv td{padding:2.5px 0;vertical-align:top}
table.kv td:first-child{color:var(--dimmer);white-space:nowrap;padding-right:9px;width:1%}
table.kv td:last-child{color:#d3dae1}
.gap{color:var(--warn)}
.src{color:var(--dimmer);font-style:italic}
.note{font-size:12px;line-height:1.5;color:var(--dim);background:var(--panel2);
  border-left:2px solid var(--line);padding:8px 10px;border-radius:0 5px 5px 0}
.hero{background:linear-gradient(180deg,#151b22,#12161b);border:1px solid #2b3641;
  border-radius:12px;padding:18px}
.hero .strip{gap:18px}
.ctl{display:flex;gap:8px;margin:0 0 14px;flex-wrap:wrap;align-items:center}
button{font:12px var(--mono);color:var(--ink);background:#1e242b;border:1px solid #313b45;
  border-radius:6px;padding:6px 11px;cursor:pointer}
button:hover{background:#27303a;border-color:#3d4854}
.hint{font-size:12px;color:var(--dimmer)}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--panel)}
table.num{border-collapse:collapse;width:100%;font:12px/1.4 var(--mono);min-width:760px}
table.num th,table.num td{padding:7px 10px;text-align:left;border-bottom:1px solid #1f252c;
  white-space:nowrap}
table.num th{background:#1a2027;color:var(--dim);font-weight:600;font-size:11px;
  text-transform:uppercase;letter-spacing:.05em;position:sticky;top:0}
table.num td.wrapcell{white-space:normal;min-width:260px;font-family:inherit;
  font-size:12.5px;color:#cbd3db}
table.num tr:last-child td{border-bottom:none}
table.num tr.best td{background:#12211b}
/* a run that DIED. Dimmed and struck, never deleted: the b4 attempt that
   bugchecked the host is evidence, and a table that quietly drops it invites
   somebody to schedule that run again. */
table.num tr.dnf td{background:#25171a;color:var(--dim);text-decoration:line-through}
table.num tr.dnf td:first-child,table.num tr.dnf .src{text-decoration:none}
.win{color:var(--prod)}
.lose{color:var(--warn)}
.slist{display:flex;flex-direction:column;gap:10px}
.srow{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:12px 14px;border-left:3px solid var(--warn)}
.srow .sh{display:flex;gap:9px;align-items:baseline;flex-wrap:wrap;margin-bottom:5px}
.srow .sh b{font-size:14px}
.tag{font:10.5px/1 var(--mono);color:var(--dimmer);border:1px solid var(--line);
  padding:3px 6px;border-radius:4px}
.srow p{font-size:13px;margin:0 0 5px;color:#c6cfd7}
.srow .extra{font-size:12.5px;color:var(--dim);margin:0}
footer{border-top:1px solid var(--line);padding-top:16px;color:var(--dim);font-size:12.5px}
footer b{color:var(--ink)}
details{margin-top:6px}
summary{cursor:pointer;font:11.5px var(--mono);color:var(--dimmer)}
summary:hover{color:var(--dim)}
details pre{font:11px/1.45 var(--mono);white-space:pre-wrap;color:#b9c3cc;
  background:#0e1216;border:1px solid var(--line);border-radius:5px;padding:8px;
  margin:6px 0 0;max-height:210px;overflow:auto}
@media (max-width:760px){
  .wrap{padding:18px 13px 60px} h1{font-size:22px}
  .card,.card.wide{width:100%;flex:1 1 100%}
}
"""

JS = """
function grp(id, act){
  var vs = document.querySelectorAll('#'+id+' video');
  vs.forEach(function(v){
    if(act==='play'){ v.currentTime=0; v.play(); }
    else if(act==='pause'){ v.pause(); }
    else { v.pause(); v.currentTime=0; }
  });
}
document.addEventListener('keydown', function(e){
  var t=e.target.tagName;
  if(e.key===' ' && t!=='VIDEO' && t!=='BUTTON' && t!=='SUMMARY'){
    e.preventDefault();
    var any=[].some.call(document.querySelectorAll('video'),function(v){return !v.paused;});
    document.querySelectorAll('video').forEach(function(v){ any? v.pause() : v.play(); });
  }
});
"""


def mode_badge(mode):
    if mode == "production":
        return '<span class="badge b-prod">production</span>'
    if mode == "preview":
        return '<span class="badge b-prev">preview</span>'
    return f'<span class="badge b-dup">{escape(str(mode or "mode?"))}</span>'


def kv(rows):
    out = ['<table class="kv">']
    for k, v in rows:
        if v is None:
            continue
        out.append(f"<tr><td>{escape(k)}</td><td>{v}</td></tr>")
    out.append("</table>")
    return "".join(out)


def clip_card(clip, wide=False, show_prompt=True, title_override=None, sub=None):
    meta, bench = clip["meta"], clip["bench"]
    stem = clip["stem"]
    doc = DOC_ONLY.get(stem, {})
    secs = video_seconds(clip)
    frames, fnote = frames_of(clip)
    cpv, cpv_src = compute_per_video_s(clip)

    model = model_of(clip)
    reg = MODELS.get(model, {})
    title = title_override or reg.get("title", meta.get("model", model) or stem)

    rows = []
    rows.append(("size", escape(str(meta.get("size", bench.get("size") if bench else None)
                                   or "—"))))
    if secs:
        rows.append(("length", num(secs, 3, "s")
                               + (f" &middot; {frames}f{fnote}" if frames else "")))
    rows.append(("steps", escape(str(meta.get("steps", bench.get("steps") if bench else "")
                                     or "—"))))
    rows.append(("guidance", escape(str(meta.get("guidance", "—")))))
    if bench and bench.get("shift") is not None:
        rows.append(("shift", f"flow_shift {num(bench['shift'])}"))
    rows.append(("seed", escape(str(meta.get("seed", clip["seed"] or "—")))))
    if clip["batch"]:
        slot = meta.get("batch_slot")
        rows.append(("batch", f"b{clip['batch']}"
                              + (f" slot {slot}" if slot is not None else "")))

    # timing — say whether sample_s covers one clip or the whole batch
    if bench and bench.get("sample_s"):
        b = int(bench.get("batch") or 1)
        span = f" <span class=\"src\">(all {b} clips)</span>" if b > 1 else ""
        rows.append(("sample_s", num(bench["sample_s"], 1, "s") + span))
        rows.append(("per step", num(bench.get("s_per_step"), 2, "s")))
    if cpv:
        rows.append(("s/video-s", f"<b>{cpv}s</b> <span class=\"src\">{cpv_src}</span>"))
    tp = meta.get("throughput_s_video_per_s_wall") or (
        bench.get("throughput_s_per_s") if bench else None)
    if tp:
        rows.append(("s(vid)/s(wall)", f"{num(tp, 4)}"
                     + (f" @b{clip['batch']}" if clip["batch"] else "")))

    # memory — the offload label is mandatory
    off = reg.get("offload")
    if bench and bench.get("peak_torch_gb"):
        rows.append(("peak VRAM", num(bench["peak_torch_gb"], 1, "GB torch")
                                  + " of " + num(bench.get("device_total_gb"), 1, "GB")
                                  + (f" <span class=\"src\">{escape(off)}</span>" if off else "")))
        if bench.get("host_peak_phys_gb"):
            rows.append(("host peak",
                         num(bench.get("host_peak_phys_gb"), 1, "GB phys") + " / "
                         + num(bench.get("host_peak_commit_gb"), 1, "GB commit")))
    elif doc.get("vram"):
        rows.append(("peak VRAM", f"{escape(doc['vram'])}"
                     + (f" <span class=\"src\">{escape(off)}, {DOC}</span>" if off else "")))
        if doc.get("host"):
            rows.append(("host peak", f"{escape(doc['host'])}"
                                      f" <span class=\"src\">{DOC}</span>"))
    else:
        rows.append(("peak VRAM", '<span class="gap">no data</span>'))
        rows.append(("host peak", '<span class="gap">no data</span>'))

    rows.append(("cost", f"${meta.get('cost_usd', 0)}"))
    if doc.get("defects"):
        rows.append(("measured", f"{escape(doc['defects'])}"
                                 f" <span class=\"src\">{DOC}</span>"))
    # the gallery-named 5B clip IS a bench row under another filename, so look the
    # motion figure up by the bench row's name too rather than only by stem
    motion_key = stem if stem in BENCH_MOTION else (bench or {}).get("name")
    if BENCH_MOTION.get(motion_key):
        med, frozen = BENCH_MOTION[motion_key]
        rows.append(("motion", f"median {med}, {frozen} barely-moving"
                               f" <span class=\"src\">{DOC}</span>"))
    if meta.get("model_licence"):
        rows.append(("licence", escape(str(meta["model_licence"]))))

    extras = []
    if clip["dup_of"]:
        extras.append('<p class="note"><b>Same bytes as '
                      f'<code>{escape(clip["dup_of"])}</code></b> — one render, two '
                      'filenames, not two samples.</p>')
    if meta.get("gallery_note"):
        extras.append(f'<p class="note">{escape(str(meta["gallery_note"]).strip())}</p>')
    if meta.get("negative_note"):
        extras.append(f'<p class="note">{escape(str(meta["negative_note"]))}</p>')
    if meta.get("lora"):
        extras.append(f'<p class="note">LoRA: {escape(str(meta["lora"]))}</p>')
    if not meta:
        extras.append('<p class="note gap">No sidecar found for this clip — every '
                      'number above is blank on purpose. Judge the picture, quote no '
                      'figures.</p>')
    if "_parse_error" in meta:
        extras.append('<p class="note gap">Sidecar did not parse: '
                      f'{escape(meta["_parse_error"])}</p>')
    if show_prompt and meta.get("prompt") is not None:
        p = str(meta.get("prompt") or "")
        shown = p if p else "(empty string — the T3b test)"
        extras.append("<details><summary>prompt + negative</summary>"
                      f"<pre>{escape(shown)}\n\n--- negative ---\n"
                      f"{escape(str(meta.get('negative') or '(none recorded)'))}</pre>"
                      "</details>")

    dup = '<span class="badge b-dup">copy</span>' if clip["dup_of"] else ""
    return (
        f'<div class="card{" wide" if wide else ""}">'
        f'<video controls loop muted playsinline preload="auto" '
        f'src="{quote(clip["rel"])}"></video>'
        f'<div class="cap">'
        f'<div class="title"><b>{escape(str(title))}</b>{mode_badge(clip["mode"])}{dup}</div>'
        + (f'<div class="rowsub">{escape(sub)}</div>' if sub else "")
        + f'<div class="file">{escape(clip["rel"])}</div>'
        f'{kv(rows)}{"".join(extras)}'
        f"</div></div>"
    )


def build():
    clips, batch_groups, t1t2t3_rows, notes = collect()
    now = datetime.now()

    # ---- hero: same seed, same still, one clip per model, from SAMPLES/ ----
    # A model may have both a preview and a production clip at the hero seed. The
    # money row wants the production one: rule 1 says a preview is judged for
    # motion only, so a preview in this row asks Roman for a verdict he is not
    # allowed to give off it. Preference, not a filter — a model with only a
    # preview clip still appears, still badged preview.
    hero_by_model = {}
    for c in clips:
        if c["dir"] != "SAMPLES" or c["seed"] != HERO_SEED or c["batch"] != 1:
            continue
        m = model_of(c)
        cur = hero_by_model.get(m)
        if cur is None or (c["mode"] == "production" and cur["mode"] != "production"):
            hero_by_model[m] = c  # else: first in sorted() order keeps the slot
    hero = list(hero_by_model.values())
    hero.sort(key=lambda c: (MODEL_ORDER.index(model_of(c))
                             if model_of(c) in MODEL_ORDER else 99))
    hero_previews = sorted({MODELS.get(model_of(c), {}).get("title", model_of(c))
                            for c in hero if c["mode"] != "production"})

    # ---- gallery groups ----
    groups = {}
    for c in clips:
        if c["dir"] == "bench-T1T2T3":
            continue  # those are the parameter sweep, shown in their own section
        groups.setdefault(model_of(c), []).append(c)
    for lst in groups.values():
        lst.sort(key=lambda c: (c["mode"] != "production", c["batch"] or 0,
                                str(c["seed"])))
    ordered = [k for k in MODEL_ORDER if k in groups] + \
              [k for k in sorted(groups) if k not in MODEL_ORDER]

    sweep = [c for c in clips if c["dir"] == "bench-T1T2T3"]
    sweep.sort(key=lambda c: c["stem"])

    H = []
    A = H.append
    A(f"<style>{CSS}</style>")
    A('<div class="wrap">')

    # ---------------------------------------------------------- header ----
    A("<h1>Model bake-off — screening page</h1>")
    A(f'<p class="sub">Generated {now:%Y-%m-%d %H:%M} local &middot; '
      f'{len([c for c in clips if not c["dup_of"]])} distinct clips '
      f'({len(clips)} files, {len(clips) - len([c for c in clips if not c["dup_of"]])} '
      'a second copy of another) &middot; every render $0 &middot; '
      '<b>local file, nothing here is published</b></p>')
    A("<nav>")
    A('<a href="#hero-sec">1 · same seed, different model</a>')
    A('<a href="#gallery">2 · gallery</a>')
    for key in ordered:
        A(f'<a href="#g-{key}">{escape(MODELS.get(key, {}).get("title", key))}</a>')
    A('<a href="#numbers">3 · the numbers</a>')
    A('<a href="#coverage">3b-2 · batch coverage</a>')
    A('<a href="#sweep">3c · shift sweep</a>')
    A('<a href="#status">4 · no sample yet</a>')
    A("</nav>")
    A('<div class="rules">')
    A('<div class="rule"><b class="rh">Rule 1 — judge preview clips for motion only</b>'
      '<p>A <span class="badge b-prev">preview</span> clip is a cheap recipe built for '
      'the minutes-long review loop: smaller, fewer steps, softer. Judge it on '
      '<b>motion and composition only</b> — the softness and the size are the mode, '
      'not the model. A <span class="badge b-prod">production</span> clip is judged the '
      'real way: publishable or not. Reading a preview as production kills a model '
      'unfairly; reading a production clip as a preview ships junk.</p></div>')
    A('<div class="rule"><b class="rh">Rule 2 — speed only counts at a look you '
      'approved</b>'
      '<p>Every throughput number on this page is worthless until the look passes. A '
      'fast model with a rejected look scores <b>zero</b> — nothing here promotes '
      'itself by being quick. So: pick the looks first, then read section 3 to see '
      'what the ones you kept cost.</p></div>')
    A("</div>")

    # ------------------------------------------------------------ hero ----
    A('<section id="hero-sec">')
    A('<div class="shead"><h2>1. Same seed, same still, different model</h2>'
      f'<span class="count">beat 1 &middot; seed {HERO_SEED} &middot; '
      f'{len(hero)} clips</span></div>')
    prev_note = ""
    if hero_previews:
        prev_note = (' (' + escape(", ".join(hero_previews))
                     + (' is' if len(hero_previews) == 1 else ' are')
                     + ' in <span class="badge b-prev">preview</span> mode here: '
                       'smaller and softer <i>by recipe</i> — rule 1 applies.)')
    A('<p class="sub" style="margin-bottom:14px">The money row. One beat, one '
      'approved still, one seed, identical conditioning — the only thing that '
      'changes is the model. Play them together and pick the motion you believe.'
      + prev_note + '</p>')
    A('<div class="hero" id="hero">')
    A('<div class="ctl"><button onclick="grp(\'hero\',\'play\')">▶ play all</button>'
      '<button onclick="grp(\'hero\',\'pause\')">❙❙ pause all</button>'
      '<button onclick="grp(\'hero\',\'reset\')">↺ restart</button>'
      '<span class="hint">space toggles every clip on the page</span></div>')
    A('<div class="strip">')
    for c in hero:
        A(clip_card(c, wide=True))
    A("</div></div></section>")

    # --------------------------------------------------------- gallery ----
    gallery_n = sum(len(groups[k]) for k in ordered)
    A('<section id="gallery">')
    A('<div class="shead"><h2>2. The gallery, by model</h2>'
      f'<span class="count">{gallery_n} clips &middot; {len(ordered)} models</span></div>')
    for key in ordered:
        reg = MODELS.get(key, {})
        gid = f"g-{key}"
        A(f'<div id="{gid}" style="margin:0 0 26px">')
        n = len(groups[key])
        A(f'<h3>{escape(reg.get("title", key))} '
          f'<span class="count">— {n} clip{"s" if n != 1 else ""}</span></h3>')
        if reg:
            A(f'<p class="sub" style="margin:0 0 4px">{escape(reg["build"])}<br>'
              f'<b>{escape(reg["role"])}</b><br>'
              f'Licence: {escape(reg["licence"])}</p>')
        else:
            A('<p class="sub gap" style="margin:0 0 4px">No registry entry for this '
              'model yet — it landed after the page was written. Cards below carry '
              'whatever its sidecar recorded; the offload strategy behind its VRAM '
              'figures is unlabelled, so do not compare that cell to another row.</p>')
        A('<div class="ctl"><button onclick="grp(\'' + gid + '\',\'play\')">▶ play '
          'group</button><button onclick="grp(\'' + gid + '\',\'pause\')">❙❙ pause'
          '</button></div>')
        A('<div class="strip">')
        for c in groups[key]:
            A(clip_card(c))
        A("</div></div>")
    A("</section>")

    # --------------------------------------------------------- numbers ----
    A('<section id="numbers">')
    A('<div class="shead"><h2>3. The numbers</h2>'
      '<span class="count">for Oleg — throughput, batching, parameters</span></div>')
    A('<p class="sub">Target (Oleg, 2026-08-04): <b>maximum seconds of video per '
      'second of real time</b> — throughput, not single-clip latency. Both forms are '
      'given because they invert each other. Rule 2 still applies: a row only counts '
      'at a look Roman approved.</p>')

    # 3a throughput
    A("<h3>3a. Throughput — model &times; mode &times; batch</h3>")
    A('<div class="tw"><table class="num"><thead><tr>'
      "<th>Model</th><th>Mode</th><th>Batch</th><th>Size / length</th>"
      "<th>s(video)/s(wall)</th><th>s(wall) per 1s video</th><th>Peak VRAM</th>"
      "<th>Host peak</th><th>Source</th></tr></thead><tbody>")
    tp_rows = []
    for c in clips:
        if c["dup_of"] or c["dir"] == "bench-T1T2T3":
            continue
        tp = c["meta"].get("throughput_s_video_per_s_wall") or (
            c["bench"].get("throughput_s_per_s") if c["bench"] else None)
        if not tp:
            continue
        key = (model_of(c), c["mode"], c["batch"])
        if key in [r[0] for r in tp_rows]:
            continue
        tp_rows.append((key, c, tp))
    tp_rows.sort(key=lambda r: -float(r[2]))  # fastest first, the way Oleg reads it
    for i, (key, c, tp) in enumerate(tp_rows):
        cpv, cpv_src = compute_per_video_s(c)
        bench, doc = c["bench"], DOC_ONLY.get(c["stem"], {})
        # num() escapes its own fallback, so these two are ALREADY html-safe and
        # must not be escaped a second time at the interpolation site — the doc
        # branch is the only raw text here.
        vram = (num(bench["peak_torch_gb"], 1, "GB") + " / "
                + num(bench.get("device_total_gb"), 1, "GB")
                if bench and bench.get("peak_torch_gb")
                else escape(doc.get("vram", "no data")))
        host = (num(bench.get("host_peak_phys_gb"), 1, "G phys") + " / "
                + num(bench.get("host_peak_commit_gb"), 1, "G commit")
                if bench and bench.get("host_peak_phys_gb")
                else escape(doc.get("host", "no data")))
        off = MODELS.get(model_of(c), {}).get("offload", "unlabelled")
        best = ' class="best"' if i == 0 else ""
        A(f"<tr{best}><td>{escape(MODELS.get(model_of(c), {}).get('title', model_of(c)))}</td>"
          f"<td>{escape(str(c['mode']))}</td><td>b{c['batch']}</td>"
          f"<td>{escape(str(c['meta'].get('size', '?')))} &middot; "
          f"{num(video_seconds(c), 3, 's')}</td>"
          f'<td><b{" class=\"win\"" if i == 0 else ""}>{num(tp, 4)}</b></td>'
          f"<td>{f'{cpv}s' if cpv else DASH}</td>"
          f'<td>{vram}<br><span class="src">{escape(off)}</span></td>'
          f"<td>{host}</td>"
          f'<td><span class="src">{escape(cpv_src or "sidecar")}</span></td></tr>')
    A("</tbody></table></div>")
    A('<p class="note" style="margin-top:10px">Three corrections that stop these cells '
      'being over-read. <b>(a)</b> The 5B row is the FIRST clip after a model load and '
      'carries ~20s of warm-up; its five following clips settled at 10.5s/step, i.e. '
      '<b>0.0173 s(video)/s(wall) — 57.6s per video-second</b>, and that is the figure '
      'to plan with. <b>(b)</b> VRAM cells are not comparable across rows unless the '
      'offload strategy under them matches: LTX\'s 2.5GB device peak measures '
      'sequential offload, not a 26GB card, and reads as "LTX fits in 4GB" the moment '
      'the label is dropped. Host RAM decides co-residency, not VRAM — the LTX render '
      'evicted the farm worker at 60.8GB of 68.1GB; a 5B render survived a 114GB '
      'download running alongside it. <b>(c)</b> THE TOP ROW IS NOT A VERDICT. The '
      'fastest row here is the fp8 cast, and as of 2026-08-05 nobody has screened '
      'it — it is a one-sample measurement, and it hands back a visibly different '
      'clip from the bf16 build at the same seed (rms 11.93/255 against a 0.93 '
      'encode-noise floor, slightly more drift than going to batch 2 cost). '
      'Throughput is the only thing this table ranks. Whether the picture is '
      'acceptable is the founder\'s call and has not been made.</p>')

    # 3b batch scaling — one table per model that has batch bench rows
    A('<h3 style="margin-top:26px">3b. Batch scaling — where it stops, and why</h3>')
    batch_order = sorted(batch_groups, key=lambda k: (
        MODEL_ORDER.index(k[0]) if k[0] in MODEL_ORDER else 99, k[0], k[1]))
    if not batch_order:
        A('<p class="sub gap">No batch bench rows on disk. Nothing has been '
          'measured at more than one latent, so this section is empty rather than '
          'estimated.</p>')
    for key in batch_order:
        label, bmode = key
        rows = batch_groups[key]
        reading = BATCH_READING.get(key, {})
        title = MODELS.get(label, {}).get("title", label)
        if len(batch_order) > 1:
            A(f'<h4 style="margin:18px 0 6px">{escape(title)} '
              f'&mdash; {escape(bmode)} '
              f'<span class="count">— {len(rows)} batch point'
              f'{"s" if len(rows) != 1 else ""}</span></h4>')
        if len(rows) < 2:
            # name the batch value the table ACTUALLY holds. This line used to say
            # "cost at b1" unconditionally, which was a lie on any series whose one
            # measured point is not b1 — the LTX table said it over a b2 row, i.e.
            # the page invented a b1 in the only sentence a reader would trust it on.
            only = ", ".join(f"b{r.get('batch')}" if r.get("batch") else "an "
                             "unrecorded batch size" for r in rows)
            A('<p class="sub gap" style="margin:0 0 6px">One batch point only — '
              'nothing is <i>scaling</i> here yet. The cells are this recipe\'s '
              f'cost at {escape(only)} and no more than that.</p>')
        # the win/lose marks are derived, not typed: fastest row wins, and any row
        # slower than its own b1 baseline loses. No editorial input.
        #
        # A ROW WITH ok:false IS A DEATH, NOT A DATA POINT. It stays visible —
        # deleting the evidence of a run that died is how a cliff gets forgotten —
        # but it is excluded from the winner and from the baseline, because a run
        # that did not finish has no throughput to be fastest at.
        tps = {r.get("batch"): (float(r["throughput_s_per_s"])
                                if r.get("throughput_s_per_s") and r.get("ok", True)
                                else None)
               for r in rows}
        best_b = max((b for b, t in tps.items() if t is not None),
                     key=lambda b: tps[b], default=None)
        base = tps.get(1)
        joined = [r for r in rows if r.get("_joined_from") == "bench row"]
        joined_side = [r for r in rows if r.get("_joined_from") == "sidecar"]
        A('<div class="tw"><table class="num"><thead><tr>'
          "<th>Batch</th><th>Clips</th><th>Mode &middot; size</th>"
          "<th>sample_s (whole batch)</th><th>s/step</th>"
          "<th>s(video)/s(wall)</th><th>s per 1s video</th><th>Peak VRAM</th>"
          "<th>Source</th>"
          + ("<th>Reading</th>" if reading else "")
          + "</tr></thead><tbody>")
        for r in rows:
            b = r.get("batch")
            tp = tps.get(b)
            dead = not r.get("ok", True)
            cls = ' class="dnf"' if dead else (
                ' class="best"' if b == best_b and len(rows) > 1 else "")
            arrow = ""
            if tp is not None and len(rows) > 1:
                if b == best_b:
                    arrow = "win"
                elif base is not None and tp < base:
                    arrow = "lose"
            # one gap mark, not "— of —": a row that measured no VRAM at all (the
            # sidecar join) has one gap, not two halves of one
            vram_cell = (num(r.get("peak_torch_gb"), 1, "GB") + " of "
                         + num(r.get("device_total_gb"), 1, "GB")
                         if r.get("peak_torch_gb") else DASH)
            A(f"<tr{cls}><td><b>b{b}</b>"
              + ('<br><span class="src">did not finish</span>' if dead else "")
              + f"</td><td>{len(r.get('seeds', []))}</td>"
              f"<td>{escape(str(r.get('mode') or '?'))} &middot; "
              f"{escape(str(r.get('size') or '?'))}</td>"
              f"<td>{num(r.get('sample_s'), 1, 's')}</td>"
              f"<td>{num(r.get('s_per_step'), 2, 's')}</td>"
              f'<td class="{arrow}"><b>{num(r.get("throughput_s_per_s"), 4)}</b></td>'
              # derived here, not read from the column — see per_video_second
              f'<td class="{arrow}">{num(per_video_second(r), 1, "s")}</td>'
              f"<td>{vram_cell}</td>"
              f'<td><span class="src">{escape(str(r.get("_src") or DASH))}'
              + ('<br>joined, derived @24fps'
                 if r.get("_joined_from") == "bench row" else
                 '<br>joined from the clip sidecar'
                 if r.get("_joined_from") == "sidecar" else "")
              + "</span></td>"
              + (f'<td class="wrapcell">{reading.get(b, "")}</td>' if reading else "")
              + "</tr>")
        A("</tbody></table></div>")
        if joined:
            A('<p class="note" style="margin-top:10px"><b>The b1 row is joined from '
              'another file, not measured again.</b> ' + " ".join(
                  f'b1 is <code>{escape(str(r["_src"]))}</code> —' for r in joined)
              + ' the same recipe at the same seed, run earlier the same day as part '
                'of the parameter sweep in section 3c. Its sample_s, s/step and memory '
                'figures cross over verbatim; s(video)/s(wall) and s per 1s video are '
                'one division on that row\'s own sample_s and frame count at 24fps. '
                'Nothing was written back to any bench file — this is a view, not a '
                'measurement. Cross-check: the b1 clip on disk '
                '(<code>ti2v5b-production-b1-s20260732.mp4</code>) is byte-identical '
                'to <code>T1-shift5.0.mp4</code>, and its own sidecar records 0.0151 '
                'and 66.3 — the two figures derived here.</p>')
        for r in joined_side:
            twin, same = r.get("_twin"), r.get("_twin_same_bytes")
            A('<p class="note" style="margin-top:10px"><b>The b1 row is joined from '
              'the clip\'s own sidecar, not measured again.</b> It comes from '
              f'<code>{escape(str(r["_src"]))}</code>, written by the render that '
              'produced the b1 clip on 2026-08-04 — before <code>--bench-jsonl</code> '
              'existed, which is why there is no bench row to read instead. '
              + (f'That clip is the same artifact as the repo-root '
                 f'<code>{escape(str(twin))}</code>, the name this run is usually '
                 'cited by; the page hashes both at build time and they '
                 + ('<b>match</b>' if same else
                    '<b class="gap">NO LONGER MATCH — treat the provenance of this '
                    'row as broken</b>')
                 + '. The root sidecar carries the recipe but not the derived '
                   'figures, so the file named above is the one that actually holds '
                   'them. ' if twin else "")
              + '<b>The em-dashes are real:</b> a sidecar records no sample_s, no '
                's/step and no VRAM peak, and those cells are left empty rather than '
                'filled from the prose table — a borrowed figure in a measured row is '
                'exactly the promotion MODEL-COMPARISON rule 2 forbids. Nothing was '
                'written back to any bench file; this is a view, not a measurement.</p>')
        if key == ("animegen", "preview"):
            A(ANIMEGEN_BATCH_NOTE)
    A(BATCH_FIDELITY_NOTE)

    # 3b-2 coverage — the same points as the tables above, plus the ones that do
    # not exist. The tables show what ran; only this says what did not and why.
    A('<h3 id="coverage" style="margin-top:30px">3b-2. Coverage — every model '
      '&times; mode &times; batch, and why each empty cell is empty</h3>')
    A('<p class="sub">No cell is allowed to be blank. A measured point states its '
      'throughput and what it did to that series\' own b1; every other cell states '
      'a reason and a date. <b>Nothing here is new data</b> — the numbers are the '
      'rows above, re-laid-out, and the reasons are the only thing written by hand.</p>')
    cov_measured, cov_gaps = 0, 0
    cov_html = []
    for mkey in MODEL_ORDER:
        for cmode in COVERAGE_MODES:
            head = (f'<td><b>{escape(MODELS.get(mkey, {}).get("title", mkey))}</b>'
                    f'<br>{mode_badge(cmode)}</td>')
            absent = COVERAGE_MODE_ABSENT.get((mkey, cmode))
            if absent:
                marker, why, as_of = absent
                cov_gaps += 1
                cov_html.append(
                    f'<tr>{head}<td class="wrapcell" '
                    f'colspan="{len(COVERAGE_BATCHES)}">'
                    f'<span class="gap">{escape(marker)}</span> — {escape(why)}'
                    f'<br><span class="src">as of {escape(as_of)}</span></td></tr>')
                continue
            crows = {r.get("batch"): r for r in batch_groups.get((mkey, cmode), [])}
            cbase = crows.get(1, {}).get("throughput_s_per_s")
            cells = []
            for b in COVERAGE_BATCHES:
                r = crows.get(b)
                if r and r.get("ok", True) and r.get("throughput_s_per_s"):
                    cov_measured += 1
                    tp = float(r["throughput_s_per_s"])
                    if b == 1:
                        rel = '<span class="src">baseline</span>'
                    elif cbase:
                        mult = tp / float(cbase)
                        rel = (f'<span class="{"win" if mult > 1 else "lose"}">'
                               f"{mult:.2f}&times; b1</span>")
                    else:
                        # no b1 to divide by, so no multiple — and no invented one
                        rel = '<span class="src">no b1 to compare</span>'
                    prov = ("joined, see the table above" if r.get("_joined")
                            else "measured")
                    cells.append(f'<td><b>{num(tp, 4)}</b><br>{rel}'
                                 f'<br><span class="src">{prov}</span></td>')
                    continue
                cov_gaps += 1
                marker, why, as_of = COVERAGE_GAPS.get(
                    (mkey, cmode, b),
                    ("no reason recorded",
                     "Not measured, and this page cannot say why — which is itself "
                     "the gap. It needs either a run or a line in COVERAGE_GAPS.",
                     f"{now:%Y-%m-%d}, generated"))
                cells.append(f'<td class="wrapcell"><span class="gap">'
                             f'{escape(marker)}</span> — {escape(why)}'
                             f'<br><span class="src">{escape(as_of)}</span></td>')
            cov_html.append(f"<tr>{head}{''.join(cells)}</tr>")
    A('<div class="tw"><table class="num"><thead><tr><th>Model &middot; mode</th>'
      + "".join(f"<th>Batch {b}</th>" for b in COVERAGE_BATCHES)
      + "</tr></thead><tbody>" + "".join(cov_html) + "</tbody></table></div>")
    A(f'<p class="note" style="margin-top:10px"><b>{cov_measured} measured points, '
      f'{cov_gaps} explained gaps.</b> Two of the gaps are decisions rather than '
      'todo items and should not be read as work outstanding: <b>b4 on the 5B is '
      'banned</b> — it bugchecked the host on 2026-08-05 and reopening it is '
      'founder-reserved — and <b>b4 on LTX is closed by host RAM</b>, on a slope '
      'measured between its own b1 and b2 rather than by trying it. The AnimeGen '
      'production cells are arithmetic on a measured VRAM slope, so they are the '
      'two worth re-testing if the card or the offload strategy ever changes.</p>')

    # 3c parameter findings + sweep clips
    A('<h3 style="margin-top:26px">3c. Same model, parameter sweep — 5B T1/T2/T3</h3>')
    A('<p class="sub">Six clips, one model, one seed each, one variable at a time. '
      '<b>Pick which motion reads best</b> — the numbers below only say what changed '
      'and what it cost. Speed is NOT the axis here: the six ran within 22s of each '
      'other, and the apparent 168.6 → 149.7 → 146.5 "trend" is the first clip\'s '
      'warm-up, not the parameter. (These six sidecars predate the <code>mode:</code> '
      'field; all six are the production recipe — 704x1280, 61f, 14 steps, guidance '
      '5.0 — and one of them is the production clip from section 1 under a second '
      'filename.)</p>')
    A('<div class="tw"><table class="num"><thead><tr>'
      "<th>Test</th><th>shift</th><th>sample_s</th><th>s/step</th>"
      "<th>Motion median</th><th>Barely-moving</th><th>What it was testing</th>"
      "</tr></thead><tbody>")
    for r in t1t2t3_rows:
        name = r["name"]
        med, frozen = BENCH_MOTION.get(name, ("no data", "no data"))
        A(f"<tr><td><b>{escape(name)}</b><br>"
          f'<span class="src">{escape(r.get("row", ""))}</span></td>'
          f"<td>{num(r.get('shift'))}</td>"
          f"<td>{num(r.get('sample_s'), 1, 's')}</td>"
          f"<td>{num(r.get('s_per_step'), 2, 's')}</td><td>{med}</td><td>{frozen}</td>"
          f'<td class="wrapcell">{BENCH_READING.get(name, "")}</td></tr>')
    A("</tbody></table></div>")
    A('<div id="sweep" style="margin-top:16px">')
    A('<div class="ctl"><button onclick="grp(\'sweep\',\'play\')">▶ play all six'
      '</button><button onclick="grp(\'sweep\',\'pause\')">❙❙ pause</button>'
      '<button onclick="grp(\'sweep\',\'reset\')">↺ restart</button>'
      f'<span class="hint">{len(sweep)} clips, all 704x1280 production, seed '
      f'{HERO_SEED}</span></div>')
    A('<div class="strip">')
    for c in sweep:
        # the model is constant across the sweep, so the TEST is the useful headline
        name = (c["bench"] or {}).get("name") or c["stem"]
        A(clip_card(c, title_override=name,
                    sub=(c["bench"] or {}).get("row", "Wan 2.2 TI2V-5B")))
    A("</div></div>")
    A('<p class="note" style="margin-top:12px"><b>Three things the sweep settled, none '
      'of them a verdict.</b> (1) The 5B does not ship the scheduler the plan assumed: '
      'there is no <code>scheduler.config.shift</code> key — it ships '
      '<code>UniPCMultistepScheduler</code> whose knob is <code>flow_shift</code>, '
      '<b>already set to 5.0</b>, Alibaba\'s own 720p value. Calling '
      '<code>set_shift()</code> here would have silently done nothing. (2) Peak VRAM '
      'is <b>14.4GB, not the 22.9GB</b> the table carried for the same recipe name — '
      'so the "clip 2 never finishes" stall of 2026-08-02, diagnosed as the allocator '
      'holding 22.9GB of a 25.7GB card, needs re-examining: at 14.4GB there is 11GB of '
      'headroom and six back-to-back clips did not stall. (3) One 88s load served all '
      'six clips, dropping the fixed cost from 66.7s/clip to <b>14.7s/clip '
      'amortised</b>. Encode note: these are CRF 16, where production writes VBR '
      'quality 5 — cross-night motion figures carry an encode difference too.</p>')
    A("</section>")

    # ---------------------------------------------------------- status ----
    A('<section id="status">')
    A('<div class="shead"><h2>4. Still no sample, and why</h2>'
      f'<span class="count">{len(NO_SAMPLE_YET)} models</span></div>')
    A('<p class="sub">Hardcoded, not globbed: a render that has not happened has no '
      'sidecar to read. Each row carries the as-of stamp of the document that says so.</p>')
    A('<div class="slist">')
    for s in NO_SAMPLE_YET:
        A('<div class="srow"><div class="sh">'
          f'<b>{escape(s["model"])}</b>'
          f'<span class="tag">{escape(s["plan"])}</span>'
          f'<span class="tag">as of {escape(s["as_of"])}</span></div>'
          f'<p>{escape(s["why"])}</p>'
          f'<p class="extra">{escape(s["extra"])}</p></div>')
    A("</div>")
    A(f'<p class="note" style="margin-top:12px">{escape(STATUS_FOOTNOTE)}</p>')
    A("</section>")

    # ---------------------------------------------------------- footer ----
    A("<footer>")
    A('<p><b>Where every number came from.</b> Each figure on this page was read out '
      'of a <code>*.mp4.meta.yaml</code> sidecar written by the render itself, a bench '
      '<code>.jsonl</code> row, or — where the machine-readable artifact has no cell '
      f'for it — <code>pipeline/research/{DOC}</code>; cells sourced from the document '
      'rather than a sidecar say so in grey. Figures marked <i>derived</i> are '
      'arithmetic on two stated numbers, nothing more. Blank cells say <span '
      'class="gap">no data</span> and mean it — a blank that reads as zero is how a '
      'gap becomes a claim.</p>')
    A('<p><b>Quality verdicts are Roman\'s alone (R4).</b> Nothing on this page is one. '
      'Frozen-frame counts, saturation, channel means and motion medians are '
      '<i>measurements</i> and belong in a table; "good", "soft" and "usable" belong to '
      'the person screening. The two open observations on tonight\'s LTX production '
      'clip are in that spirit and both unresolved: <b>progressive colour drift, '
      'magenta → teal over ~16 frames</b> (untested lever: <code>adain_factor</code>, '
      'held at 0.0 in <code>pipeline/ltx_i2v.py:435</code> because upstream\'s '
      'distilled path leaves it off too — one sample decides it), and a <b>possible '
      'period-3 motion cadence, UNRESOLVED and confounded</b> by the 1Mbps h264 encode '
      '— the settling test is a lossless re-encode on the next run, and no cadence '
      'verdict should be recorded before that.</p>')
    A('<p><b>Nothing here is published.</b> These are unapproved media samples under '
      'STEWARDSHIP §6, so this file is local only: not built into <code>_site/</code>, '
      'not deployed, not committed. Every clip cost $0. Rebuild after new clips land '
      'with <code>python3 pipeline/build_comparison.py</code>.</p>')
    A("</footer>")
    A("</div>")
    A(f"<script>{JS}</script>")

    OUT.write_text("\n".join(H), encoding="utf-8")

    # ------------------------------------------------------- verify + log ----
    html_text = OUT.read_text(encoding="utf-8")
    missing = [src for src in re.findall(r'src="([^"]+)"', html_text)
               if not (REPO / src).exists()]
    print(f"wrote {OUT.relative_to(REPO)}  ({len(html_text) / 1024:.0f}KB)")
    print(f"  hero row      : {len(hero)} clips")
    print(f"  gallery       : {gallery_n} clips in {len(ordered)} groups "
          f"({', '.join(ordered)})")
    print(f"  sweep         : {len(sweep)} clips")
    print(f"  throughput    : {len(tp_rows)} rows")
    print(f"  batch scaling : {sum(len(v) for v in batch_groups.values())} rows in "
          f"{len(batch_groups)} table(s) "
          f"({', '.join(f'{a}/{b}' for a, b in batch_order) if batch_order else 'none'})")
    print(f"  parameters    : {len(t1t2t3_rows)} rows")
    print(f"  status        : {len(NO_SAMPLE_YET)} models with no sample")
    print(f"  distinct clips: {len([c for c in clips if not c['dup_of']])} "
          f"of {len(clips)} files")
    for n in notes:
        print(f"  ! {n}")
    if missing:
        print(f"FAIL: {len(missing)} broken video src: {missing}", file=sys.stderr)
        return 1
    print("  all video srcs resolve")
    return 0


if __name__ == "__main__":
    sys.exit(build())
