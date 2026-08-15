@echo off
REM banyan-runner-watchdog -- one tick of runner_watchdog.py --local.
REM
REM ONE SHOT, NOT A DAEMON, exactly like box-autofill.cmd: the task repeats every
REM five minutes, and a tick that dies for any reason is replaced by the next one
REM rather than staying dead until someone looks.
REM
REM --local makes every probe run through cmd.exe instead of ssh. It is the same
REM file, the same commands and the same rule the Mac-side `--dry-run` reports;
REM only the transport differs. The point of that is the 2026-08-12 flap: the
REM PowerShell watchdog this replaces was never run anywhere but here, its one
REM detector returned an empty string under the scheduled context, and it logged
REM sixty false restarts before anyone saw it.
REM
REM SYSTEM python, not a venv: runner_watchdog.py imports stdlib only and must
REM keep watching while a venv is mid-reinstall.
REM
REM UTF-8 pinned like every other banyan task -- cp1252 has killed five things in
REM this project.
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

set PY=C:\Users\artvn\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PY%" set PY="C:\banyan-video\venv\Scripts\python.exe"

REM stdout goes to its own run log, NOT to watchdog.log. watchdog.log stays the
REM incident file: a line in it means the watchdog decided something, so an empty
REM tail is a readable statement that nothing has been restarted. Proof that the
REM task is alive comes from here and from Get-ScheduledTaskInfo instead.
"%PY%" C:\banyan-farm\runner_watchdog.py --local >> C:\banyan-farm\watchdog-run.log 2>&1
exit /b %ERRORLEVEL%
