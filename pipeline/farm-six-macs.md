# Six more Macs in the render loop — design pass

Status: **design only**, nothing wired. 2026-08-10.

Fixed premises (given, not re-derived): six new Macs, roughly this Mac's
power, same LAN, completely new, **no CUDA so no LTX**. The 5090 keeps
motion. The Macs are for **stills, VO and scoring** — which is where the
work actually is: beats 07, 08, 14, 15, 17 and 19 are blocked on plates,
not on clips.

**The load-bearing precedent: this path already works on a Mac.** This very
Mac was onboarded as a farm worker — `/Users/artovonkugler/banyan-farm-m1pro/`
exists, with its own venv, and `origin/farm-results-m1pro` has real DONE
lines (last one 2026-08-07, `b07-negatives-as-written`). `origin/farm-results-m2`
did the same on 2026-07-30. So this is not a new architecture; it is the
sixth and seventh copy of one that has already rendered and pushed.

`pipeline/farm-join.md` is the existing runbook and its Apple Silicon branch
is correct. `pipeline/ONBOARD-WINDOWS.md` is **not** the doc for these
machines — it is CUDA/winget specific.

---

## 1. Per-Mac bring-up sequence

### (a) By hand, at the machine — 2 steps

1. **System Settings → General → Sharing → Remote Login: ON.**
   Note the machine's name (it appears as `<name>.local`).
2. **One GUI click for the Xcode Command Line Tools.** A fresh Mac has no
   real `git`; the first `git` call pops an Apple installer dialog. I can
   *trigger* it over SSH (`xcode-select --install`) but the **Install**
   button has to be clicked on the machine. One click, once, per Mac.

That is the whole manual list. **Two steps, both under a minute.** It is
worth doing tonight.

Two things he does **not** need to do, and should not:
- **No sleep/power settings.** The worker gets launched under
  `caffeinate -dimsu`, which holds the machine awake with no admin rights
  and no System Settings visit. (`pmset` would need his password; skip it.)
- **No USB key ferrying.** `farm-join.md` says the deploy key is
  hand-carried "USB/**local share**, never chat/email/repo". A `scp` from
  this Mac over the LAN *is* the local share, so the policy is satisfied
  without him touching a stick.

### (b) Over SSH, unattended — everything else

Per Mac, in order:

1. `ssh-copy-id` / seed my key so the rest is non-interactive.
2. `xcode-select -p` — if absent, `xcode-select --install`, then wait for
   his one click.
3. Check the interpreter: `python3 -V`. **This is the one genuinely open
   item** — see §5.
4. `mkdir -p ~/banyan-farm-<name>` and `git clone --depth 50` the repo into it.
5. `scp` the deploy key over; `chmod 600`; then the four `git config` lines
   from `farm-join.md` §Setup step 3 (`core.sshCommand`, `remote set-url`,
   `user.email`, `user.name`).
6. `python3 -m venv venv`; `pip install torch` (plain — Apple Silicon takes
   the default wheel, no index URL) then
   `pip install "diffusers==0.29.2" "transformers==4.44.2" "accelerate==0.33.0" safetensors pyyaml pillow`.
7. **`rsync` the weights from this Mac** rather than downloading — see §2.
8. Sanity: `python -c "import torch; print(torch.backends.mps.is_available())"`
   must print `True`. On MPS the worker runs **fp32 automatically**; fp16
   NaNs to black (the 2026-07-27 lesson, noted in `farm_worker.py`'s header).
9. Launch detached and awake:
   `caffeinate -dimsu nohup ./venv/bin/python pipeline/farm_worker.py --name <unique-name> &`

**The `--name` must be unique per Mac and must be chosen deliberately** —
it is not cosmetic, it is the machine's only identity. See §4.

### Time estimate

Bounded by the pip install and the rsync, not by anything human. Roughly
**15–25 minutes per Mac**, nearly all unattended, and they can be run
concurrently across the six once the two manual steps are done on each.

### Can it be done without him doing anything by hand?

**No — but very nearly.** The Remote Login toggle cannot be set on a machine
you cannot log into, and the CLT dialog needs a click. After those two, the
answer is yes: bring-up, weight staging, launch and restart are all SSH-able.

Note this is *better* than the Windows box, where restarts were understood
to need a human. The reason there was that `farm_worker.py` was documented
as an interactive PowerShell window ("leave this window open — minimised is
fine, closed is not", `ONBOARD-WINDOWS.md` §7), and `farm_worker.py`'s own
source at line ~131 refers to "a human logged in to restart the worker". On
a Mac with Remote Login on, `nohup`/`caffeinate` under SSH removes that:
**a Mac worker can be restarted unattended.** That is a real advantage of
this hardware over the existing box, and worth telling him.

---

## 2. Weight cost per Mac — measured on this machine

All figures below are **MEASURED** (`du -sh` on this Mac today), not
estimated. This is the minimum for stills + VO, **not** the 57 GB total
cache sitting here.

| Item | Size | Needed for |
|---|---|---|
| `models--cagliostrolab--animagine-xl-3.1` | **6.5 GB** | SDXL stills |
| `models--madebyollin--sdxl-vae-fp16-fix` | 319 MB | SDXL stills |
| `models--openai--clip-vit-large-patch14` | 3.6 MB | prompt tokenising |
| farm venv (torch MPS + diffusers stack) | **897 MB** | stills |
| repo clone + scratch | ~2.5 GB | — |
| **Subtotal, stills only** | **~10.2 GB** | |
| `models--ResembleAI--chatterbox` | **3.0 GB** | VO |
| `models--charactr--vocos-mel-24khz` | 52 MB | VO |
| `~/.cache/banyan-tts` (voice refs) | 345 MB | VO |
| Chatterbox venv (`banyan-tts-venvs/cb`) | **1.3 GB** | VO |
| **Total, stills + VO** | **~15 GB** | |

**Headline for the founder: about 15 GB per Mac, ~90 GB across six.**
(`banyan-farm-m1pro/` in total measures 3.4 GB here, which matches the
venv+clone rows; the weights live in the shared `~/.cache/huggingface`.)

### Copy over the LAN — yes, and you should

Six simultaneous HuggingFace pulls of ~10 GB each is ~60 GB over one home
connection and is the slowest, most failure-prone part of the whole plan.
Instead, from this Mac:

```
rsync -a ~/.cache/huggingface/hub/models--cagliostrolab--animagine-xl-3.1 \
         ~/.cache/huggingface/hub/models--madebyollin--sdxl-vae-fp16-fix \
         ~/.cache/huggingface/hub/models--openai--clip-vit-large-patch14 \
         <mac>:~/.cache/huggingface/hub/
rsync -a ~/.cache/huggingface/hub/models--ResembleAI--chatterbox \
         ~/.cache/huggingface/hub/models--charactr--vocos-mel-24khz \
         <mac>:~/.cache/huggingface/hub/
rsync -a ~/.cache/banyan-tts <mac>:~/.cache/
```

`-a` preserves symlinks, which matters: the HF cache is `blobs/` plus
`snapshots/` symlinks, and a copy that dereferences them both doubles the
size and breaks revision pinning. On gigabit this is a few minutes per Mac.
It also guarantees **byte-identical weights across all seven machines**,
which a re-download does not — a silently different revision is exactly the
class of divergence §5 is about.

---

## 3. What does NOT need six machines

Blunt: **most of what has actually been costing us time.** The card sat
empty for hours today while lanes verified authoring. Six Macs do not
render an approval.

**Six Macs would NOT have fixed, and would MULTIPLY:**

- **Authoring correctness.** Wrong prompt, wrong draft key, wrong recipe.
  Six machines render a wrong recipe six times faster. This is precisely
  what CLAUDE.md's ONE-SAMPLE-BEFORE-ANY-BATCH rule exists to stop, and six
  boxes is a batch multiplier pointed straight at it.
- **Founder screening and taste (R4).** Serial, single-human, and
  non-parallelisable by construction. More candidates per hour makes the
  review queue *worse*, not better. Six Macs turn a rendering bottleneck
  into a reviewing bottleneck — and we already have the reviewing bottleneck.
- **Hand-staged config divergence.** `C:\banyan-farm\wave-goblin-prep\wave-drafts.yaml`
  is hand-staged, is not the repo copy, and carries hand-written provenance
  comments a yaml round-trip would destroy — the current coping mechanism is
  bespoke surgical scripts like `pipeline/insert_b04_crouch_plate_0815.py`
  ("Insert ONE new draft key ... additively, with a backup"). That does not
  scale to seven copies. See §5.
- **Lane coordination.** More writers, more collisions. We already lost a
  render to two jobs writing payloads to the same path
  (37ffd933: "the twin overwrote its sibling's prompt five seconds later").
- **Provenance identity.** See §4 — it gets *worse* with more machines, not
  better.

**Six Macs WOULD genuinely fix:**

- **Plate/still generation for beats 07, 08, 14, 15, 17, 19.** These are
  independent, per-beat, and each one is cheap to verify on its own. This is
  the named blocker and it is real fan-out work.
- **VO synthesis.** Embarrassingly parallel per line, and Chatterbox on MPS
  is exactly this hardware's job.
- **Scoring / measurement passes.** Parallel, cheap, no taste judgement.

**The honest summary:** six Macs raise the ceiling on *candidate production*
for stills and VO, which is currently blocking six beats. They do nothing
for the review pass that follows, and they increase the blast radius of any
authoring mistake. Worth doing — but the throughput win is only real if the
review side is paced to match, and it is not today.

---

## 4. §7.2 provenance — this is the thing that breaks first

**Today, on the Windows path, the job record does carry the host:**
`box_runner.py:954` sets `job["runner_host"] = socket.gethostname()`, and the
GPU claim file records `host=` (`box_runner.py:410`). Heartbeat records
default a `host` field (`:567`). So the *queue* knows.

**The per-clip §7.2 sidecar is the problem.** `video_task.worker_id()`
(`video_task.py:1060`) is the function that answers "which machine rendered
this", and its docstring is explicit that two earlier answers were wrong:

> `platform.node()`. Both Windows farm boxes report hostname "MSI" ... so the
> hostname cannot tell a 24GiB 5090 from a 12GB 5070 Ti.

Its fix was to make **the card name itself**:

```python
return f"{gpu} @ {handle}" if gpu else handle
```

**On a Mac, `gpu` is the empty string.** `cuda_device_name()`
(`video_task.py:1043`) returns `""` unless `torch.cuda.is_available()`, which
is false on MPS. So on these six machines `worker_id()` collapses to
`handle` alone — and `handle` is `task["worker"]` or `platform.node()`.

Consequences, stated plainly:

- **The discriminator that rescued the Windows boxes does not exist on Mac
  at all.** Six new Macs with default Apple names will produce colliding or
  near-colliding `platform.node()` values, and there is no card name behind
  it to break the tie.
- Therefore **the explicit `--name` handle is the ONLY identity these
  machines have**, and it flows into three places at once: the results
  branch (`farm-results-<name>`), the sidecar `worker_id`, and the heartbeat.
- **Required change (not yet made):** `--name` must be mandatory and unique,
  the task's `worker:` field must be pinned to it (never `any` — the
  docstring already warns that the wildcard "can claim a clip was rendered by
  `any`"), and a bring-up check should refuse to start a worker whose name
  is already live on another `farm-results-*` branch.

This is my answer to "what breaks first at six boxes": **not throughput —
identity.** It breaks silently, produces sidecars that all name the same
machine, and is only detectable by noticing that two branches claim the same
handle. Detection: a check that the set of `--name` values across live
`farm-results-*` branches is distinct, and that no sidecar's `worker_id`
lacks a handle.

---

## 5. Queue architecture — recommendation

### Two systems exist today; the Macs join the older one

- **`box_runner.py`** — the Windows box path. A directory queue at
  `C:\banyan-queue\{ready,running,done,failed}`, `POLL_SECONDS=10`, jobs
  pushed in by `box_enqueue.py` over `scp` from this Mac. **Not for the
  Macs** — it is bound to the CUDA/LTX box.
- **`farm_worker.py`** — **git as transport.** Polls `pipeline/farm-queue.yaml`
  on `main` every 60s, matches tasks by `worker:` name (or `any`), renders,
  and pushes results + heartbeats to `farm-results-<name>`. Explicitly
  supports Apple Silicon. **This is the one the Macs join**, and it needs no
  shared filesystem at all.

This dissolves the framing problem in the brief: **the six Macs never need
to see `C:\banyan-queue`.** They do not share a queue directory; they share
a git branch. No SMB, no Redis, no HTTP service, no NFS locking.

### Is the claim atomic?

On the box path, **yes.** `box_runner.Queue.claim()` is a single
`os.rename(ready/name → running/name)` on one volume, and the loser gets an
`OSError` and returns `None`:

```python
def claim(self, name: str):
    """Atomically move ready/name -> running/name. None if someone beat us."""
    try:
        os.rename(src, dst)
    except OSError:
        return None
```

That is correct and race-free **within one machine**. What is *not* safe
across machines is the lock beside it: `acquire_lock()`
(`box_runner.py:232`) is `O_CREAT|O_EXCL` with a staleness reclaim keyed on
`pid_alive(holder)` and a `boot_id`. **Those are local facts.** Six runners
against one shared directory would each evaluate a foreign PID against their
own process table — so a machine either refuses forever because an unrelated
local PID happens to match, or declares the lock stale and takes over while
the real holder is still rendering. **That is the named race, and it is why
I am not recommending a shared queue directory.** (`farm_worker.py`'s lock is
the same primitive with *no* stale takeover at all, deliberately: "two
workers racing to decide whose lock is stale is the same bug in a hat".)

The cost of getting this wrong is documented: on 2026-07-31 two workers ran
on one 5090, halved throughput, blew a 4-hour timeout, lost the batch, and
force-pushed over each other's results branch (62f12886).

### Recommendation: **partitioned by explicit assignment**

Pin every task's `worker:` to a named Mac. **Never use `worker: any` with
six machines.**

Rationale: `farm_worker` has no cross-machine claim primitive. Its
de-duplication is a scan of every `farm-results-*` heartbeat plus local
`done_ids` memory — eventually consistent over a 60s poll plus push latency.
Six workers all matching `any` would all be eligible for the same task inside
that window, and the winner is decided by nothing. Explicit assignment makes
the race structurally impossible: the dispatcher is the single writer to
`farm-queue.yaml`, and exactly one machine matches each task.

**First failure mode of this recommendation, honestly:** a named Mac goes
away — asleep, full, or off the LAN — and its tasks sit forever, because no
other machine is eligible to pick them up. Head-of-line blocking by design.

**Detection, and this follows our own liveness lesson** (heartbeats and
process lists lie; only log freshness and ground truth count): the signal is
**freshness of `origin/farm-results-<name>`**, not a process check.
`build_sim` already calls a machine unheard-from after 45 minutes, and
`queue_keeper.py` / `pulse_series.py` / `ops_board.py` / `queue_promoter.py`
already glob `farm-results-*` and split the machine name off the branch — so
the fan-out surface for six branches largely exists. **Recovery is manual
re-assignment** (edit the task's `worker:`), which is the correct trade: a
human re-points a stalled task, rather than two machines guessing whether a
third is dead.

### Downstream: what assumes exactly one results branch

Already generalised (globs `farm-results-*`): `pulse_series.py:119`,
`queue_keeper.py:32`, `queue_promoter.py:80`, `ops_board.py:138`,
`farm_worker.py:397`.

**Still hardcoded to `rtx5090` — these are the fix list:**
- `pipeline/unpaged.py:78` — `BRANCH = "origin/farm-results-rtx5090"`
- `pipeline/build_queue.py:85` — `RESULTS_BRANCH = "farm-results-rtx5090"`
- `pipeline/collect_farm.py:36` — `DEFAULT_BRANCH = "origin/farm-results-rtx5090"`
- `pipeline/box_enqueue.py:223` — `RESULTS_BRANCH = "origin/farm-results-rtx5090"`
- `pipeline/build_pulse.py:118` — `TELEMETRY_URL_LEGACY` (legacy, probably fine)

Note five results branches already exist (`hand`, `m1pro`, `m2`, `msi`,
`rtx5090`), so this is a pre-existing gap that six more branches makes
louder, not a new one.

### The drafts-divergence hazard, generalised

`wave-drafts.yaml` is hand-staged on the box, is not the repo copy, and the
sampler locates it by `--harness` directory (`render_wave_sample.py:165`,
`goblin_ipa_sample.py:579`). Today's only defence is **fail-loud on a missing
key** — deliberately no fallback:

> NO FALLBACK TO `authored`, DELIBERATELY. If the box's drafts file is stale
> and lacks the requested key, silently sending the old text would render the
> OLD staging under the NEW job id — the failure would be invisible.

That catches *absent*. It does **not** catch *present but different*, which
is exactly what hand-staging onto seven machines produces.

**The comment-insensitive hash check generalises, and it is now the
load-bearing control, not a nicety.** Concretely: at read time, hash the
*parsed* draft values (not the file bytes, so the ~350 KB of provenance
comments survive untouched), and compare against a hash the dispatcher
records in the task. A mismatch refuses the render and names the beat. This
is strictly better than distributing the file, because it verifies what was
actually *read* rather than what was *copied*.

For the Macs specifically: prefer to sidestep the hazard entirely. The Mac
stills path can take its prompt from the repo copy on `main` (which
`farm_worker` already pulls before each task) rather than a hand-staged
harness. **Do not replicate the hand-staging pattern onto six new machines.**

---

## 6. Open item

**Which Python the Macs will use.** `farm-join.md` specifies 3.12; a fresh
macOS ships only the CLT `python3` (3.9.x). I have not verified which the
`banyan-farm-m1pro` venv here was built from. The check is one line —
`ssh <mac> python3 -V` — and if it is 3.9, the zero-admin fix is `uv`
(single binary, `curl` install, fetches its own CPython 3.12, no sudo,
no GUI). Flagging rather than guessing.

## 7. External research

Not yet folded in — the research pass on how others fan diffusion work
across 5–10 consumer boxes (ComfyUI-Distributed, SwarmUI multi-backend,
filesystem-queue atomic-claim patterns) was still running when this note was
committed. The architecture recommendation above rests on our own code and
our own incident history, which is the stronger evidence for our case; the
external pass should be used to challenge it, not to found it.
