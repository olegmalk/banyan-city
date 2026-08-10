# `pipeline/jobs/` — the box's dinner, one dish per plate

Every file in here is **one render job, fully specified, fireable with zero human
judgement and zero repo archaeology at fire time.** A machine that can reach this
directory and a GPU has everything it needs: the node, the beat, the exact strings
to send, the seeds, the model, the geometry, the output path, and the sentence that
says whether the result is good.

This directory is **not** `pipeline/farm-queue.yaml` and does not compete with it.
The queue file is the live worker inbox and is owned by other lanes; this is the
larder those lanes and the box-resident runner draw from. Nothing here fires on its
own.

## The shape

One YAML file per job, named `<id>.yaml`, holding a single mapping. Every key
`farm_worker.render_task` actually reads is spelled exactly as that function reads
it, so a job file can be appended to a `tasks:` list verbatim, with no rewriting and
no translation step:

| key | who reads it | notes |
|---|---|---|
| `id` | `farm_worker.py` — prefixes every output file, names the heartbeat | slug-epoch. A re-queue MUST take a fresh id or it inherits the old one's spent attempts. |
| `worker` | `farm_worker.py` — string equality, `any` is the wildcard | `hand` means no machine ever selects it. Never a list. |
| `node` | `farm_worker.py` — **subscripted**, so it is required | dir under `genomes/sapling/nodes/`; its newest T0 leaf must read `approved_by: founder` or the task exits on STEWARDSHIP §6 |
| `beats` | looked up in that node's `shots.md` | `"10"` or `"3,4,5"` |
| `prompt` + `slug` | instead of `beats` — the task's own positive | `no <noun>` fences included; `sd_prompt` lifts them into the negative itself |
| `seeds`, `seed_base` | draws per beat; `seed = seed_base + beat + k*1000` | defaults 4 / 20260719 |
| `model`, `steps`, `width`, `height`, `guidance` | stills path | defaults `cagliostrolab/animagine-xl-3.1` / 40 / 832 / 1216 / 7.5 |
| `init`, `strength` | img2img; repo-relative, cover-cropped by `plate_prep` | |
| `video: true` | routes the whole dict to `video_task` instead | which reads `video_model`, `seconds`, `steps`, `seed_base` itself |

Everything else below is **inert planning metadata** — no worker reads it, unknown
keys on a task are ignored, and dead keys already exist in the queue file's history.
It is here because a job nobody can evaluate is not a specified job:

| key | meaning |
|---|---|
| `runner` | `farm` (a worker task) or `manual` (a command a person or agent runs) |
| `cmd` | `manual` jobs only: the exact command, not a description of one |
| `needs` | capability tags — `cuda`, `vram20`, `mps`, `video-venv` |
| `after` | ids that must ALL show `DONE task=<id>` on a `farm-results-*` heartbeat |
| `gate` / `gate_ref` | `founder` \| `code` \| `hardware`. Present = BLOCKED, full stop. Clearing one is a human deleting the key. |
| `sample: true` | this job is the ONE SAMPLE for a recipe; nothing scaled may run ahead of it |
| `recipe_slot` | a named field a human or the settling lane fills before this fires. **A job with an unfilled `recipe_slot` is not runnable** — the value is the recipe, and inventing one here would be scaling an unapproved result. |
| `measure_on_box` | this job's prompt has NOT been token-measured on the box's real CLIP tokenizer. The Mac estimator lies by ~3 tokens, so this must be measured before the job fires. |
| `est_minutes` | sourced in `why` where a measurement exists |
| `consumer` | **who eats the output.** No job without a consumer (standing rule). |
| `success` | the criterion, written before the render, so the result can be read without a taste call |
| `why` | one line a stranger understands |

## The two rules that govern what may be in here

**ONE SAMPLE BEFORE ANY BATCH.** The first job of any new recipe renders ONE
beat, and carries `sample: true`. Every job that scales that recipe carries
`after: [<the sample id>]` *and* a `gate: founder` naming the verdict it waits on,
because `after:` alone only proves the sample *rendered* — not that anyone looked at
it. A metric agreeing with the steward is not a sample.

**NOTHING GATED FIRES.** No job in here spends money, publishes anything, or
requires a taste verdict to *run*. Jobs whose *inputs* are a taste verdict carry
`gate: founder` and sit here as prepared work, not as runnable work. Provisional
picks are labelled `steward-provisional` wherever they appear.

## Fire order

`index.yaml` lists every job id in dependency order with its blocker, if it has one.
Read that first; it is the only file here that describes the set rather than a job.
