# Enlist a Windows GPU machine into the render farm

Open this page **on the machine you are onboarding** — every code block below
has a copy button in the top-right corner.

These are plain one-line commands on purpose. There is no script to parse, so
there is nothing that can fail on a syntax or text-encoding problem (which is
exactly what went wrong the first time on the 5090). Run them in order, in
**PowerShell** (Start -> type `powershell` -> Enter).

Everything lands in `C:\banyan-farm` (plus `C:\banyan-video` once it renders
video). Delete those two folders and the machine is completely out of the farm.
**No account logins are needed** — not Google, not GitHub.

---

## 1. The folder and the courier key

```
mkdir C:\banyan-farm
```

Copy `farm_deploy_key` from the Mac's `Desktop/banyan-drops/` onto a USB stick,
plug it in, then (replace `D:` with the stick's drive letter):

```
copy D:\farm_deploy_key C:\banyan-farm\
```

Check it arrived — should be about 411 bytes, no file extension:

```
dir C:\banyan-farm
```

## 2. Git and Python

```
winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
```

```
winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
```

**Now close PowerShell and open a new one** so both land on your PATH. Check:

```
git --version
```

```
python --version
```

## 3. The repo

```
cd C:\banyan-farm
```

```
git clone --depth 50 https://github.com/olegmlkvorg/banyan-city.git
```

(If it says the folder already exists, that step is already done — carry on.)

```
cd C:\banyan-farm\banyan-city
```

## 4. The courier identity

Lock the key down, or ssh will refuse to use it:

```
icacls C:\banyan-farm\farm_deploy_key /inheritance:r /grant:r "$env:USERNAME:(R)"
```

Then four config lines:

```
git config core.sshCommand "ssh -i C:/banyan-farm/farm_deploy_key -o StrictHostKeyChecking=no"
```

```
git remote set-url origin git@github.com:olegmlkvorg/banyan-city.git
```

```
git config user.email "farm@banyan.city"
```

```
git config user.name "farm-courier"
```

Prove it can reach GitHub as the courier:

```
git fetch origin main
```

## 5. Python environment

```
python -m venv C:\banyan-farm\venv
```

PyTorch for the GPU. **RTX 50-series needs this exact cu128 index** — an older
wheel installs fine and then silently has no CUDA:

```
C:\banyan-farm\venv\Scripts\python.exe -m pip install --retries 30 --timeout 120 torch --index-url https://download.pytorch.org/whl/cu128
```

That is about 3 GB. If the download dies partway, just run it again — pip
resumes.

Then the image-model stack:

```
C:\banyan-farm\venv\Scripts\python.exe -m pip install --retries 30 --timeout 120 "diffusers==0.29.2" "transformers==4.44.2" "accelerate==0.33.0" safetensors pyyaml pillow
```

## 6. The line that matters

```
C:\banyan-farm\venv\Scripts\python.exe -c "import torch; print('CUDA:', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE')"
```

It must print:

```
CUDA: True NVIDIA GeForce RTX 5090 Laptop GPU
```

**If it says `False` or `NONE`, stop and report it.** The machine would
otherwise render on the CPU at roughly 1% of its speed, which looks like "this
is slow" rather than "this is misconfigured."

## 7. Start the worker

```
cd C:\banyan-farm\banyan-city
```

```
C:\banyan-farm\venv\Scripts\python.exe pipeline\farm_worker.py --name rtx5090
```

It prints `farm worker 'rtx5090' on cuda - polling ...` and waits for work.
**Leave this window open** — minimised is fine, closed is not.

Two Windows settings, once:

- **Settings -> System -> Power**: plugged in, never sleep
- same page: **Best performance**

---

## What happens next

The worker polls `pipeline/farm-queue.yaml` on `main` every minute. When work
appears it renders and pushes results to its own `farm-results-rtx5090` branch
with a heartbeat at every stage, so a stuck machine is visible instead of
silent. It updates its own code from `main` before each task.

Video tasks build a second python environment in `C:\banyan-video` on first
use, because the video model needs a newer library version than the image model
tolerates.

## If something goes wrong

| Symptom | Cause and fix |
|---|---|
| `CUDA: False` | Wrong wheel. Report it — RTX 50-series needs the cu128 index in step 5. |
| `git` or `python` not recognised | Open a fresh PowerShell window after step 2. |
| `Permissions ... too open` | Re-run the `icacls` line in step 4. |
| `Host key verification failed` | The `core.sshCommand` line in step 4 is missing or mistyped. |
| Download dies partway | Some routers kill long connections. Re-run the same line; pip resumes. |
| `charmap codec can't encode` | Old code. Run `git pull` in `C:\banyan-farm\banyan-city`, restart the worker. |
| Worker window closed | Nothing breaks; queued work waits. Re-run step 7. |

To remove the machine from the farm entirely: close the window, delete
`C:\banyan-farm` and `C:\banyan-video`. Nothing else was ever installed.
