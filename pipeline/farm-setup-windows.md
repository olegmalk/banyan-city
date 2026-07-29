# Enlisting a Windows machine into the render farm

Written for the MSI Vector 16 HX (RTX 5070 Ti) — works for any Windows
machine with an NVIDIA GPU. Everything lives in ONE folder (`C:\banyan-farm`);
delete that folder and the machine is out of the farm. Nothing else is
touched. ~15 minutes, most of it downloads.

**Before starting: the machine's owner has said yes.**

## 1. Install the two tools (once)

Open **Terminal** (or PowerShell) and run:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
```

Close and reopen the terminal afterward so both are on PATH.

## 2. Get the repo and the courier key

```powershell
mkdir C:\banyan-farm
cd C:\banyan-farm
git clone https://github.com/olegmlkvorg/banyan-city.git
cd banyan-city
```

Copy the courier key file (`farm_deploy_key`, hand-carried from the
steward's Mac — USB stick or local file share, **never** chat/email/repo)
to `C:\banyan-farm\farm_deploy_key`, then:

```powershell
git config core.sshCommand "ssh -i C:/banyan-farm/farm_deploy_key -o StrictHostKeyChecking=no"
git remote set-url origin git@github.com:olegmlkvorg/banyan-city.git
git config user.email "farm@banyan.city"
git config user.name  "farm-courier"
```

## 3. Python environment

RTX 50-series (Blackwell) needs the cu128 PyTorch build — older wheels
don't know the chip (the same class of version-drift that ate the first
RunPod fires; pinned here so it can't recur):

```powershell
python -m venv C:\banyan-farm\venv
C:\banyan-farm\venv\Scripts\pip install torch --index-url https://download.pytorch.org/whl/cu128
C:\banyan-farm\venv\Scripts\pip install diffusers transformers accelerate safetensors pyyaml pillow
```

## 4. Sanity check, then run

```powershell
C:\banyan-farm\venv\Scripts\python -c "import torch; print(torch.cuda.get_device_name())"
# must print the GPU name, e.g. 'NVIDIA GeForce RTX 5070 Ti Laptop GPU'

C:\banyan-farm\venv\Scripts\python pipeline\farm_worker.py --name msi
```

First run downloads the 7 GB model once, then it idles politely, polling
`pipeline/farm-queue.yaml` every minute. When the steward queues work, it
renders and pushes to the `farm-results-msi` branch with heartbeats; the
steward QAs, ballots, and credits the owner in the watering ledger
(`type: compute`).

To stop: `Ctrl+C`. To uninstall: delete `C:\banyan-farm`. To revoke the
machine's repo access entirely: delete the "farm courier" deploy key in
GitHub → Settings → Deploy keys.
