# One-time trainer install on the rtx5090 box

**Status: DONE, 2026-08-20.** All eight steps ran on the box and the step-8 gate
passed. Resolved versions:

| | |
|---|---|
| sd-scripts | tag **v0.11.1**, commit `6721028c79ee85a78b3a06dfd8954dae310a1cce`, at `C:\banyan-farm\sd-scripts` |
| Trainer venv | `C:\banyan-farm\venv-lora`, Python 3.12.10, torch **2.11.0+cu128**, `torch.cuda.get_device_capability()` → `(12, 0)` |
| xformers | **absent** — `pip show xformers` not found in either venv |
| Optimizer | **bitsandbytes 0.50.1**, `AdamW8bit` smoke-tested on the card (allocate → backward → `step()`) and it works. The spec's `--optimizer_type AdamW8bit` stands; §5's AdamW fallback is NOT needed |
| accelerate | `C:\Users\artvn\.cache\huggingface\accelerate\default_config.yaml` written non-interactively; loads as `DistributedType.NO / bf16 / 1 process` |
| Step-8 gate | `sdxl_train_network.py --help` → **800 lines**, and all 17 flags the job spec passes are present in it |

**The render venv was re-verified untouched afterwards**, which is the whole
point of the separation: `C:\banyan-farm\venv` still reports torch
`2.11.0+cu128`, capability `(12, 0)`, `diffusers 0.29.2`, `transformers 4.44.2`,
no xformers, and a bf16 CUDA matmul executes. Nothing was installed into it.

### Four things execution corrected in the steps below

1. **v0.11.1's `requirements.txt` does not list xformers at all.** The trap's
   direct vector is gone in this tag, and the install completed with torch
   unchanged. The three rules below still stand unedited — a future tag bump can
   reintroduce it, and the cost of keeping them is zero.
2. **Step 4 must run with `cwd = C:\banyan-farm\sd-scripts`.** The last line of
   `requirements.txt` is `-e .`, which resolves against the working directory;
   run from anywhere else it installs the wrong thing or fails. The command as
   written below does not `cd`.
3. **Step 4 also folds in step 5.** `bitsandbytes` is already a line in
   v0.11.1's `requirements.txt`, so it arrives with the batch; step 5 is a
   verification, not an install.
4. **Step 8's `--help` needs `PYTHONUTF8=1`.** On a stock cmd console it dies
   with `UnicodeEncodeError: 'charmap' codec can't encode…` — the help text
   contains Japanese and the console is cp1252. The parser itself is fine; only
   printing fails. The job spec already sets `PYTHONUTF8` in its `env:`, so the
   run is unaffected. Note the cmd quoting: `set "PYTHONUTF8=1"`, because
   `set PYTHONUTF8=1 && …` puts the trailing space in the value and Python then
   refuses to start with `invalid PYTHONUTF8 environment variable value`.

Also observed, not a problem: `triton not found; flop counting will not work`
warns on every invocation. Triton has no Windows wheel and nothing in this
config needs it.

A constraints file (`C:\banyan-farm\lora-constraints.txt`, pinning
`torch==2.11.0+cu128` plus the resolved torchvision) was passed to step 4 with
`--extra-index-url …/cu128` so that a torch swap would **fail loudly** instead
of silently. It was not exercised — nothing tried to move torch.

Measured on the box over ssh, 2026-08-20, read-only:

| | |
|---|---|
| GPU | `NVIDIA GeForce RTX 5090 **Laptop** GPU`, **24463 MiB = 23.89 GiB** |
| Compute capability | `(12, 0)` — Blackwell **sm_120** |
| Driver | 610.78 |
| Render venv | `C:\banyan-farm\venv`, Python **3.12.10**, torch **2.11.0+cu128** |
| Installed | 29 packages. `diffusers 0.29.2`, `accelerate 0.33.0`, `transformers 4.44.2`. **No** kohya, sd-scripts, peft, bitsandbytes, opencv, onnxruntime |
| Free disk C: | **54.0 GB** of 926.5 GB |
| Base model | `models--cagliostrolab--animagine-xl-3.1` already cached, diffusers layout, snapshot `483f0c322568ed13697ed01dd0be07204746d12b` |

Note the VRAM. The brief said 32 GB; this is the **laptop** part at 24 GB. SDXL
LoRA training fits fine (§4 below). LTX-2.3 video LoRA training does not — its
floor is 32 GB with INT8 — which is why the LoRA is a plate-step artifact.
See `pipeline/research/character-lora-sdxl-0820.md` §1, §7.

---

## THE ONE THING THAT CAN BREAK THE WHOLE FARM

**Do not install anything into `C:\banyan-farm\venv`.** That venv renders every
plate and every clip we ship. `sd-scripts`' requirements pull **xformers**, and
on an sm_120 card pip resolves that by deciding the installed torch is
incompatible and **silently replacing it with an older build that has no sm_120
kernels** — no error, no useful warning. The next render fails with
`CUDA error: no kernel image is available for execution on the device`, and it
fails for *everything*, not just training.
([kohya_ss #3276](https://github.com/bmaltais/kohya_ss/issues/3276),
[the sm_120 survival guide](https://dev.to/madcoolseed/rtx-5090-survival-guide-sm120-cuda-12-and-13-side-by-side-and-the-xformers-trap-25nh))

Three rules follow, and all three are load-bearing:

1. **A separate venv: `C:\banyan-farm\venv-lora`.** Never the render venv.
2. **Never install xformers.** Use `--sdpa` (torch's built-in attention).
   sd-scripts supports it as a first-class flag and it needs no extra package.
3. **After every install step, run `pip show torch` and confirm the version
   string still ends in `+cu128`.** If it does not, pip swapped the wheel —
   stop and reinstall from the cu128 index before doing anything else.

---

## Steps

Run these on the box (ssh alias `rtx5090`, `cmd.exe` shell). Nothing here needs
the GPU, so it can run while the card is busy. Total download ≈ 3–4 GB; there
is 54 GB free, which is enough for the install plus the ~7 GB of cached base
model already present plus checkpoints.

### 1. Clone sd-scripts

The CLI library, **not** `bmaltais/kohya_ss` — that is the Gradio GUI and it
drags in a browser stack we do not want on a headless queue box. Our jobs are
argv lists, which is exactly what sd-scripts is.

```
git clone https://github.com/kohya-ss/sd-scripts C:\banyan-farm\sd-scripts
```

Pin to a release tag rather than tracking main, so a job filed today still runs
next month. Record the resolved commit in this file when you do it.

Done 2026-08-20: `git checkout v0.11.1` (the newest tag), resolving to
`6721028c79ee85a78b3a06dfd8954dae310a1cce`. The clone is a detached HEAD at that
tag, not `main`.

### 2. Create the isolated venv

```
C:\banyan-farm\venv\Scripts\python.exe -m venv C:\banyan-farm\venv-lora
```

(Using the existing interpreter only to *create* the new venv — nothing is
installed into it.)

### 3. torch FIRST, from the cu128 index, spelled out

Before any requirements file. If torch is already correct when the requirements
resolve, pip has less room to "fix" it.

```
C:\banyan-farm\venv-lora\Scripts\python.exe -m pip install --upgrade pip
C:\banyan-farm\venv-lora\Scripts\python.exe -m pip install --retries 30 --timeout 120 torch torchvision --index-url https://download.pytorch.org/whl/cu128
C:\banyan-farm\venv-lora\Scripts\python.exe -m pip show torch
```

**Gate: the `Version:` line must end in `+cu128`.** Then confirm the card is
actually reachable:

```
C:\banyan-farm\venv-lora\Scripts\python.exe -c "import torch;print(torch.__version__, torch.cuda.get_device_capability())"
```

Expect `2.x.x+cu128 (12, 0)`.

### 4. sd-scripts' own requirements, minus xformers

```
cd /d C:\banyan-farm\sd-scripts
C:\banyan-farm\venv-lora\Scripts\python.exe -m pip install -c C:\banyan-farm\lora-constraints.txt --extra-index-url https://download.pytorch.org/whl/cu128 -r requirements.txt
C:\banyan-farm\venv-lora\Scripts\python.exe -m pip show torch
```

(The `cd` is required — `requirements.txt` ends in `-e .`. The constraints file
and extra index are the fail-loud guard described at the top of this file.)

**Gate again: still `+cu128`.** If `requirements.txt` pins xformers, edit it out
before running this and note the edit here. If torch got swapped anyway,
reinstall step 3 and pass `--no-deps` to the offending package.

### 5. bitsandbytes, for the 8-bit optimizer

`AdamW8bit` cuts optimizer VRAM ~25–30% with negligible quality cost, which is
what buys comfortable headroom at batch 2 on 24 GB.

```
C:\banyan-farm\venv-lora\Scripts\python.exe -m pip install bitsandbytes
C:\banyan-farm\venv-lora\Scripts\python.exe -m pip show torch
```

If the current bitsandbytes has no Blackwell build, drop to `--optimizer_type
AdamW` (not 8-bit) and `--train_batch_size 1` rather than chasing a source
build. The run gets slower; nothing else changes. **Record which one you ended
up with in the job spec's provenance.**

### 6. accelerate config

Non-interactive, single GPU, bf16:

```
C:\banyan-farm\venv-lora\Scripts\python.exe -m accelerate.commands.launch --help
```

Write the config rather than answering prompts — the interactive configurator is
reported not to work cleanly on this card
([kohya_ss #3332](https://github.com/bmaltais/kohya_ss/issues/3332)). A minimal
`default_config.yaml` with `distributed_type: NO`, `mixed_precision: bf16`,
`num_processes: 1` is enough; the job spec passes the rest as flags.

### 7. Optional — the tagger, for the second captioning pass

Only if someone runs the WD14 pass described in
`pipeline/research/character-lora-sdxl-0820.md` §4. Captions already exist
without it.

```
C:\banyan-farm\venv-lora\Scripts\python.exe -m pip install onnxruntime-gpu huggingface-hub
```

### 8. Prove it before filing any job

```
set "PYTHONUTF8=1"
C:\banyan-farm\venv-lora\Scripts\python.exe C:\banyan-farm\sd-scripts\sdxl_train_network.py --help
C:\banyan-farm\venv-lora\Scripts\python.exe -m pip show torch
```

Help text prints, torch is still `+cu128` → the install is done. Without the
`PYTHONUTF8` line this raises `UnicodeEncodeError` on a cp1252 console even
though the install is perfectly good. **Then** file
`pipeline/lora/train-jerry-0820.yaml` with `box_enqueue.py --backlog`, and
update the Status line at the top of this file with the date, the sd-scripts
commit, and the resolved torch version.

---

## The dataset also has to reach the box

The training job reads the frames from the box's repo checkout at
`C:\banyan-farm\banyan-city`. All 31 curated frames are committed as of
`61dfbca4` (9 of them were untracked on the Mac and were committed with the
manifest for exactly this reason), so a `git pull` in that checkout is the whole
dataset transfer. Nothing needs scp.

**Measured 2026-08-20, and it is slower than that sentence suggests.** Two
things the next lane should know:

- **Nothing on the box ever pulls this checkout.** `box_runner.py` deliberately
  never touches its branch or working tree, and `box_enqueue.py` /
  `box_autofill.py` have no guard on its HEAD. The only staleness detector is
  `box_preflight.py --max-age-days` (default 2.0), and it only fires when the
  preflight job happens to be queued. Somebody has to type the pull. Assume the
  checkout is stale until you have looked.
- **The pull itself is a long transfer** — this is a 5.5 GiB repo with media, and
  the box was 3 days behind, so it ran for tens of minutes. Start it before you
  need it, not when the job is already queued.

Credentials are fine and need no login: both the checkout and the `courier-box`
worktree carry
`core.sshCommand = ssh -i C:/banyan-farm/farm_deploy_key -o StrictHostKeyChecking=no`,
and that deploy key is passphrase-less. **Do not set `GIT_SSH_COMMAND` when you
run the pull** — the environment variable overrides `core.sshCommand`, drops the
deploy key, and the pull dies with `git@github.com: Permission denied
(publickey)`. That failure looks exactly like broken credentials and is not.

The captions live in `pipeline/lora/captions/jerry/` and are *not* beside their
images — kohya wants `<image>.txt` next to `<image>`. The job spec's first step
stages a flat training dir on the box and copies both in, so neither `farm-out/`
nor the repo is written into by the trainer.
