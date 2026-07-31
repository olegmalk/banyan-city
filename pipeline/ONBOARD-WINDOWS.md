# Enlist a Windows GPU machine into the render farm

Open this page **on the machine you're onboarding** — every code block has a
copy button. Takes about 15 minutes, most of it downloading.

Everything lands in `C:\banyan-farm` (plus `C:\banyan-video` when it renders
video). Delete those two folders and the machine is completely out of the farm.
Nothing else on the computer is touched.

**No account logins are needed.** Not Google, not GitHub. The repo is public to
read, and the machine's only identity is a deploy key that pushes as
`farm-courier`.

---

## 1. Put the courier key on the machine

Copy `farm_deploy_key` from the Mac's `Desktop/banyan-drops/` onto a USB stick,
plug it into this machine, then open **PowerShell** (Start → type `powershell`
→ Enter) and run:

```powershell
mkdir C:\banyan-farm
```

Now copy the key in — replace `D:` with whatever drive letter the stick got
(check File Explorer):

```powershell
copy D:\farm_deploy_key C:\banyan-farm\
dir C:\banyan-farm
```

You should see `farm_deploy_key`, about 411 bytes, with no file extension.

> The key never travels by chat, email, or cloud drive — it is a credential.
> USB or a local network share only.

## 2. Run the onboarding

```powershell
cd C:\banyan-farm
curl.exe -L -o onboard.ps1 https://raw.githubusercontent.com/olegmlkvorg/banyan-city/main/pipeline/onboard-windows.ps1
```

Then, with a name for this machine (`rtx5090`, `msi`, `dan-pc` — it becomes the
machine's branch and its label on the studio page):

```powershell
powershell -ExecutionPolicy Bypass -File onboard.ps1 -Name rtx5090
```

That installs git and python if they're missing, clones the repo, locks the key
down so ssh will accept it, points the remote at the courier identity, and
builds a CUDA 12.8 python environment (~3 GB, resumable).

## 3. Check the line that matters

Near the end it prints:

```
CUDA: True | NVIDIA GeForce RTX 5090 Laptop GPU
```

**If it says `CUDA: False` or `NONE`, stop and report it** — it means the wrong
PyTorch wheel landed, and the machine would silently render on the CPU at about
1% of its speed. That is a two-minute fix, but only if you catch it here.

## 4. Start the worker

```powershell
cd C:\banyan-farm\banyan-city
C:\banyan-farm\venv\Scripts\python.exe pipeline\farm_worker.py --name rtx5090
```

It prints `farm worker 'rtx5090' on cuda — polling ...` and then waits for
work. **Leave this window open** — minimised is fine, closed is not.

Then change two Windows settings once:

- **Settings → System → Power**: plugged in, never sleep
- same page: **Best performance**

With 16 GB of system RAM or less, also set a big fixed pagefile (Settings →
System → About → Advanced system settings → Performance Settings → Advanced →
Virtual memory → Custom size 49152 / 65536 MB). Video models stream through
system RAM, and a small pagefile is what makes them crawl.

---

## What it does once it's running

Polls `pipeline/farm-queue.yaml` on `main` every minute. When work appears it
renders and pushes the results to its own `farm-results-<name>` branch, with a
heartbeat line at every stage — so a stuck machine is visible instead of
silent. It updates its own code from `main` before each task and restarts
itself if the pipeline changed.

Video tasks build a second, separate python environment in `C:\banyan-video`
on first use (the video model needs a newer library version than the image
model tolerates).

## If something goes wrong

| Symptom | Cause and fix |
|---|---|
| `CUDA: False` | Wrong wheel for the GPU. Report it — RTX 50-series needs the cu128 build. |
| `Permissions ... are too open` | The key wasn't locked down. Re-run the script; step 3 does it. |
| `Host key verification failed` | First push to GitHub. The script disables that prompt; re-run it. |
| Download dies partway | Some routers kill long connections. Just re-run — every download resumes. |
| `charmap codec can't encode` | Old code. `git pull` in `C:\banyan-farm\banyan-city`, then restart the worker. |
| Worker window closed | Nothing breaks; queued work waits. Re-run the step 4 command. |

To remove the machine from the farm: close the window, delete
`C:\banyan-farm` and `C:\banyan-video`. Nothing else was ever installed.
