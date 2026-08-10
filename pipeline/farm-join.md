# Joining the render farm

Any machine with a real GPU can render candidate stills for the tree —
family hardware today, contributor hardware as the marketplace grows
(D11/D12: compute is a way of watering). One script, one folder, delete
the folder to leave.

## What a worker is

`pipeline/farm_worker.py` polls `pipeline/farm-queue.yaml` on `main` once
a minute. When a task names it (or `any`), it renders those beats with the
project's exact recipe (same model, seeds, §6 approval gate) and pushes
results + heartbeats to its own `farm-results-<name>` branch. The steward
QAs results onto ballots and credits the machine's owner in the watering
ledger (`type: compute`).

## Requirements

- NVIDIA GPU (8 GB+ VRAM) or Apple Silicon (16 GB+ unified memory).
  No real GPU → not worth the electricity; contribute via the render
  requests on the shot board instead.
- ~20 GB disk, steady internet, permission of the machine's owner.
- Push access comes from a deploy key issued per machine by the steward —
  hand-carried (USB/local share), never sent through chat, email, or the
  repo. No key, no farm; strangers should ask on the reactions thread.

## Setup (any OS)

1. Install Git and Python 3.12.
2. `git clone https://github.com/olegmalk/banyan-city.git` into its own
   folder (e.g. `banyan-farm/`).
3. Wire the courier key:
   `git config core.sshCommand "ssh -i <path-to-key> -o StrictHostKeyChecking=no"`
   `git remote set-url origin git@github.com:olegmalk/banyan-city.git`
4. Make a venv; install torch for YOUR hardware first, then the rest:
   - NVIDIA RTX 50-series: `pip install torch --index-url https://download.pytorch.org/whl/cu128`
     (older wheels don't know Blackwell; a flaky connection survives better
     downloading the wheel in a browser and pip-installing the file)
   - Other NVIDIA: plain `pip install torch`
   - Apple Silicon: plain `pip install torch` (the worker runs fp32 on MPS
     automatically — fp16 NaNs to black)
   - then: `pip install diffusers transformers accelerate safetensors pyyaml pillow`
   - Windows also needs the VC++ runtime:
     `winget install --id Microsoft.VCRedist.2015+.x64 -e`
5. Sanity: `python -c "import torch; print(torch.cuda.get_device_name())"`
   (or on a Mac: `...print(torch.backends.mps.is_available())"`)
6. Run it, named after the machine:
   `python pipeline/farm_worker.py --name <machine-name>`

Leave the window open; plug the machine in; set power settings so it
doesn't sleep. First task downloads the 7 GB model once (or copy a
`models--cagliostrolab--animagine-xl-3.1` folder into the HuggingFace
cache from another machine to skip it).

## Leaving

`Ctrl+C`, delete the folder. The steward revokes the machine's deploy key
in GitHub → Settings → Deploy keys.
