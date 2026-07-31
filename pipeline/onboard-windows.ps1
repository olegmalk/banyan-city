# Enlist a Windows machine into the render farm
#
# ASCII ONLY in this file, deliberately: Windows PowerShell 5.1 reads a .ps1
# as ANSI unless it has a BOM, so a single em-dash arrives as mojibake and
# takes the parser down with it (2026-07-31, on the 5090's first run). - one command, start to finish.
#
# Written for the RTX 5090 laptop (2026-07-31) and any NVIDIA Windows box after
# it. Everything lands in C:\banyan-farm (plus C:\banyan-video for the video
# stack); delete those two folders and the machine is out of the farm. Nothing
# system-level is touched except git and python, installed via winget.
#
#   1. Copy `farm_deploy_key` (from Desktop\banyan-drops on the Mac - USB,
#      AirDrop or local share; NEVER email or chat) to C:\banyan-farm\
#   2. powershell -ExecutionPolicy Bypass -File onboard-windows.ps1 -Name rtx5090
#
# The worker then polls the queue forever, renders, and pushes results with a
# heartbeat at every stage. Blackwell needs cu128 wheels - pinned below,
# because the wrong wheel is a silent "no CUDA" fallback to the CPU.

param(
    [Parameter(Mandatory = $true)][string]$Name,
    [string]$Root = "C:\banyan-farm"
)

$ErrorActionPreference = "Stop"
$REPO = "$Root\banyan-city"
$VENV = "$Root\venv"
$KEY  = "$Root\farm_deploy_key"

function Step($n, $msg) { Write-Host "`n[$n] $msg" -ForegroundColor Yellow }

New-Item -ItemType Directory -Force -Path $Root | Out-Null

# ---- 1. tools
Step 1 "git + python (skipped if already present)"
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
    $env:PATH += ";$env:ProgramFiles\Git\cmd"
}
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
    $env:PATH += ";$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts"
}

# ---- 2. the repo (public, so the clone needs no key; pushing does)
Step 2 "the repo"
if (!(Test-Path $REPO)) {
    git clone --depth 50 https://github.com/olegmlkvorg/banyan-city.git $REPO
}
Set-Location $REPO
git checkout -q main

# ---- 3. the courier identity
Step 3 "courier credentials"
if (!(Test-Path $KEY)) {
    Write-Host "  MISSING: $KEY" -ForegroundColor Red
    Write-Host "  Copy farm_deploy_key from the Mac's Desktop\banyan-drops (USB or" -ForegroundColor Red
    Write-Host "  AirDrop - never chat or email), then run this again." -ForegroundColor Red
    exit 1
}
# ssh refuses a world-readable key: lock it to this user
icacls $KEY /inheritance:r /grant:r "$($env:USERNAME):(R)" | Out-Null
git config core.sshCommand "ssh -i $($KEY -replace '\\','/') -o StrictHostKeyChecking=no"
git remote set-url origin git@github.com:olegmlkvorg/banyan-city.git
git config user.email "farm@banyan.city"
git config user.name  "farm-courier"

# ---- 4. the stills venv (video builds its own - Wan needs a newer diffusers)
Step 4 "python environment (~3GB download, resumable)"
if (!(Test-Path "$VENV\Scripts\python.exe")) { python -m venv $VENV }
$PY = "$VENV\Scripts\python.exe"
& $PY -m pip install -q --upgrade pip
# cu128 = Blackwell (sm_120). An older wheel installs fine and then silently
# has no CUDA, which reads as "the GPU is slow" instead of "wrong wheel".
& $PY -m pip install -q --retries 30 --timeout 120 torch --index-url https://download.pytorch.org/whl/cu128
& $PY -m pip install -q --retries 30 --timeout 120 `
    "diffusers==0.29.2" "transformers==4.44.2" "accelerate==0.33.0" safetensors pyyaml pillow

Step 5 "checking the GPU"
& $PY -c "import torch; print('  CUDA:', torch.cuda.is_available(), '|', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE')"

Write-Host "`nREADY. Start the worker with:" -ForegroundColor Green
Write-Host "  cd $REPO" -ForegroundColor White
Write-Host "  $PY pipeline\farm_worker.py --name $Name" -ForegroundColor White
Write-Host @"

Leave that window open (minimised is fine). It polls for work, renders, and
pushes to the farm-results-$Name branch with heartbeats the steward watches.
Power settings worth changing once: never sleep while plugged in, and
Best performance.
"@ -ForegroundColor Gray
