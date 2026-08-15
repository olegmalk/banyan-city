@echo off
REM banyan-box-autofill -- one tick of box_autofill.py (see that file's docstring).
REM
REM ONE SHOT, NOT A DAEMON. The task repeats every 3 minutes with
REM MultipleInstances IgnoreNew, exactly like banyan-box-runner's keepalive: a
REM tick that dies for any reason is replaced by the next one three minutes
REM later, where a crashed daemon would stay dead until someone looked. The card
REM going idle unnoticed is the failure this exists to end, so the mechanism
REM that fixes it must not have a single point of death of its own.
REM
REM SYSTEM python, not a venv: box_autofill.py imports stdlib only and must keep
REM feeding the queue while a venv is mid-reinstall. Falls back to the render
REM venv only if the system interpreter has moved.
REM
REM UTF-8 pinned like every other banyan task -- cp1252 has killed five things in
REM this project, and job files carry Chinese negatives and ellipses.
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

set BANYAN_QUEUE_ROOT=C:\banyan-queue
set PY=C:\Users\artvn\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PY%" set PY="C:\banyan-video\venv\Scripts\python.exe"

"%PY%" C:\banyan-farm\box_autofill.py --root %BANYAN_QUEUE_ROOT% >> C:\banyan-queue\autofill-run.log 2>&1
exit /b %ERRORLEVEL%
