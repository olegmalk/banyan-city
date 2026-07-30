# Set up FREE local video generation on the Windows farm machine.
#
# Model choice (deep research, 2026-07-30): Wan 2.2 TI2V-5B — Apache 2.0
# (clean for CC BY publishing), native 704x1280 = exactly our 9:16, ~10GB
# fp16 fits 12GB VRAM as ONE model (the 14B variant swaps two 8.5GB experts
# per stage, which thrashes a 16GB-RAM box). Anime upgrade path once this
# works: Index-AniSora V3.2 (Bilibili's anime finetune of Wan 2.2, also
# Apache 2.0) drops into the same workflow.
#
# Downloads ~14GB. Their router has killed long streams before, so every
# download resumes (-C -) and retries.
#
#   powershell -ExecutionPolicy Bypass -File pipeline\msi-setup-video.ps1
#
# Nothing system-level is installed: everything lands in C:\banyan-video,
# deletable in one go.

$ErrorActionPreference = "Stop"
$ROOT = "C:\banyan-video"
$COMFY = "$ROOT\ComfyUI_windows_portable"
$M = "$COMFY\ComfyUI\models"

function Get-Model($url, $dest) {
    $dir = Split-Path $dest
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    if (Test-Path $dest) {
        $sz = [math]::Round((Get-Item $dest).Length / 1GB, 2)
        Write-Host "  already have $(Split-Path $dest -Leaf) (${sz}GB) — resuming if partial" -ForegroundColor DarkGray
    }
    Write-Host "  downloading $(Split-Path $dest -Leaf) ..." -ForegroundColor Cyan
    # -C - resumes a killed stream; --retry survives their router
    curl.exe -L --fail --retry 30 --retry-delay 5 --retry-all-errors -C - -o "$dest" "$url"
    if ($LASTEXITCODE -ne 0) { throw "download failed: $url" }
}

New-Item -ItemType Directory -Force -Path $ROOT | Out-Null

# ---- 1. ComfyUI portable (ships its own python + a Blackwell-capable torch)
if (!(Test-Path $COMFY)) {
    Write-Host "`n[1/4] ComfyUI portable (~2GB)" -ForegroundColor Yellow
    $z = "$ROOT\comfy.7z"
    Get-Model "https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z" $z
    Write-Host "  extracting (a few minutes)..." -ForegroundColor Cyan
    & "$env:ProgramFiles\7-Zip\7z.exe" x $z "-o$ROOT" -y | Out-Null
    if (!(Test-Path $COMFY)) {
        # no 7-Zip? get it via winget and retry once
        winget install --id 7zip.7zip -e --accept-source-agreements --accept-package-agreements
        & "$env:ProgramFiles\7-Zip\7z.exe" x $z "-o$ROOT" -y | Out-Null
    }
    Remove-Item $z -ErrorAction SilentlyContinue
} else {
    Write-Host "`n[1/4] ComfyUI already installed" -ForegroundColor Green
}

# ---- 2. the model, its text encoder, its VAE
Write-Host "`n[2/4] Wan 2.2 TI2V-5B weights (~12GB total)" -ForegroundColor Yellow
$BASE = "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files"
Get-Model "$BASE/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors" "$M\diffusion_models\wan2.2_ti2v_5B_fp16.safetensors"
Get-Model "$BASE/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" "$M\text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors"
Get-Model "$BASE/vae/wan2.2_vae.safetensors" "$M\vae\wan2.2_vae.safetensors"

# ---- 3. our approved frames, as ComfyUI inputs
Write-Host "`n[3/4] copying the approved frames into ComfyUI\input" -ForegroundColor Yellow
$stills = "C:\banyan-farm\banyan-city\genomes\sapling\nodes\001-capability-inventory\stills"
if (Test-Path $stills) {
    Copy-Item "$stills\*.png" "$COMFY\ComfyUI\input\" -Force
    Write-Host "  copied $((Get-ChildItem "$stills\*.png").Count) frames" -ForegroundColor Green
} else {
    Write-Host "  (repo stills not found at $stills — copy them by hand later)" -ForegroundColor DarkYellow
}

# ---- 4. pagefile advice (16GB RAM + big models = mandatory)
Write-Host "`n[4/4] one Windows setting worth checking" -ForegroundColor Yellow
Write-Host @"
  With 16GB RAM, give Windows a big fixed pagefile on the SSD:
    Settings -> System -> About -> Advanced system settings
    -> Performance Settings -> Advanced -> Virtual memory Change
    -> uncheck automatic, set Custom size 49152 / 65536 MB -> Set -> OK
  Also: Settings -> Power -> plugged in: never sleep; Best performance.
"@ -ForegroundColor Gray

Write-Host "`nDONE. Start it with:" -ForegroundColor Green
Write-Host "  $COMFY\run_nvidia_gpu.bat" -ForegroundColor White
Write-Host @"

Then in the browser window that opens:
  Workflow -> Browse Templates -> Video -> "Wan2.2 5B video generation"
  Load one of our frames (e.g. 10-sense.png) as the start image,
  set size 704x1280, length 81 frames, and hit Run.
First run compiles kernels — it is slow ONCE, then fast.
"@ -ForegroundColor Gray
