# One-time trainer install on the rtx5090 box

**Status: NOT DONE. This is why `pipeline/lora/train-jerry-0820.yaml` is not
filed.** The brief's rule was: file the job with `--backlog` only if the box
already has a trainer; otherwise commit the spec plus this file and stop. The
box has no trainer, so this stops here.

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
C:\banyan-farm\venv-lora\Scripts\python.exe -m pip install -r C:\banyan-farm\sd-scripts\requirements.txt
C:\banyan-farm\venv-lora\Scripts\python.exe -m pip show torch
```

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
C:\banyan-farm\venv-lora\Scripts\python.exe C:\banyan-farm\sd-scripts\sdxl_train_network.py --help
C:\banyan-farm\venv-lora\Scripts\python.exe -m pip show torch
```

Help text prints, torch is still `+cu128` → the install is done. **Then** file
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

The captions live in `pipeline/lora/captions/jerry/` and are *not* beside their
images — kohya wants `<image>.txt` next to `<image>`. The job spec's first step
stages a flat training dir on the box and copies both in, so neither `farm-out/`
nor the repo is written into by the trainer.
