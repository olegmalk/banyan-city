@echo off
REM banyan-telemetry — GPU/RAM pulse for the big render house (see telemetry.py).
REM
REM SYSTEM python on purpose, not C:\banyan-video\venv or C:\banyan-farm\venv:
REM telemetry.py imports stdlib only, and the whole point of this task is to keep
REM watching while the venvs are being reinstalled, upgraded or hammered by a
REM render. Nothing here pip-installs anything.
REM
REM UTF-8 pinned like every other banyan task: cp1252 has killed five things in
REM this project, and a logger that can crash its own process is worse than none.
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

REM The daemon is written never to exit. If it does anyway — a driver hiccup that
REM escapes every handler, an OOM kill — restart it after 30s instead of leaving
REM the box blind until someone notices. `ping` is the sleep: `timeout` needs a
REM console it does not have under schtasks.
:loop
echo ==== banyan-telemetry started %DATE% %TIME% ====>> C:\banyan-farm\telemetry-run.log
C:\Users\artvn\AppData\Local\Programs\Python\Python312\python.exe C:\banyan-farm\telemetry.py --daemon >> C:\banyan-farm\telemetry-run.log 2>&1
echo ==== banyan-telemetry exited rc=%ERRORLEVEL% at %DATE% %TIME% - restarting in 30s ====>> C:\banyan-farm\telemetry-run.log
ping -n 31 127.0.0.1 >nul
goto loop
