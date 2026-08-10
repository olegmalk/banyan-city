@echo off
REM Launch the box-resident render runner. Idempotent on purpose: box_runner.py
REM takes runner.lock and exits 75 if a live runner already holds it, so the
REM keepalive schedule can fire this every couple of minutes without ever
REM producing a second drainer.
REM
REM This runs as SYSTEM from Task Scheduler, where %USERPROFILE% is
REM C:\Windows\system32\config\systemprofile -- NOT the artvn profile. Every
REM cache path the render needs is therefore pinned absolutely below. Leave
REM HF_HOME implicit and the box re-downloads ~38GB of weights it already has.

set BANYAN_QUEUE_ROOT=C:\banyan-queue
set HF_HOME=C:\Users\artvn\.cache\huggingface
set HF_HUB_DISABLE_XET=1
set HF_HUB_DOWNLOAD_TIMEOUT=60
set HF_HUB_DISABLE_SYMLINKS_WARNING=1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set PYTHONUNBUFFERED=1
set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

set PY=C:\banyan-video\venv\Scripts\python.exe
set RUNNER=C:\banyan-farm\box_runner.py

if not exist %BANYAN_QUEUE_ROOT% mkdir %BANYAN_QUEUE_ROOT%

%PY% %RUNNER% --root %BANYAN_QUEUE_ROOT% >> C:\banyan-queue\runner-stdout.log 2>&1
exit /b %ERRORLEVEL%
