@echo off
setlocal enabledelayedexpansion
REM ONE SAMPLE. Not the wave.
REM   run-wave-sample.cmd 07 "green skin, plump, one broken tusk"
REM CLAUDE.md, founder 2026-08-03: before rendering a SET of anything, produce
REM ONE and have him look at it — one per RECIPE CHANGE. The goblin definition
REM IS the recipe change, so the first thing that runs after he defines it is
REM this file with one beat number, and the fifteen wait for his verdict on it.
REM render_wave_goblin.py refuses a whole-wave render on purpose (rc 8).
set "HF_HOME=C:\Users\artvn\.cache\huggingface"
set "HF_HUB_DISABLE_XET=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
set "PYTHONUNBUFFERED=1"
set "W=C:\banyan-farm\wave-goblin-prep"
set "PY=C:\banyan-farm\venv\Scripts\python.exe"
set "B=%~1"
set "GOB=%~2"
if "%B%"=="" echo need a beat number, e.g. run-wave-sample.cmd 07 "green skin, plump" & exit /b 1
if "%GOB%"=="" echo need the founder's goblin definition as argument 2 & exit /b 1
set "L=%W%\sample-b%B%.log"
echo ==== sample beat %B% STARTED %DATE% %TIME% ==== > %L%
echo goblin-def: %GOB% >> %L%
%PY% %W%\render_wave_goblin.py --root %W%\repo --drafts %W%\wave-drafts.yaml --goblin-def "%GOB%" --beat %B% >> %L% 2>&1
echo RC=!ERRORLEVEL! >> %L%
echo ==== sample beat %B% FINISHED %DATE% %TIME% ==== >> %L%
type %L%
