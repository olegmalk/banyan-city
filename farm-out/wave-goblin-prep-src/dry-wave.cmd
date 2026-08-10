@echo off
setlocal enabledelayedexpansion
REM Measure every drafted beat on the REAL CLIP tokenizer. Draws nothing.
REM Pass the founder's goblin definition as the first argument, quoted:
REM   dry-wave.cmd "green skin, plump, one broken tusk"
REM With no argument it measures r8's own pair, which is the worst case that
REM has actually been rendered.
set "HF_HOME=C:\Users\artvn\.cache\huggingface"
set "HF_HUB_DISABLE_XET=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
set "PYTHONUNBUFFERED=1"
set "W=C:\banyan-farm\wave-goblin-prep"
set "PY=C:\banyan-farm\venv\Scripts\python.exe"
set "L=%W%\dry.log"
set "GOB=%~1"
if "%GOB%"=="" set "GOB=green skin, plump"
echo ==== wave dry STARTED %DATE% %TIME% ==== > %L%
echo goblin-def: %GOB% >> %L%
%PY% %W%\render_wave_goblin.py --root %W%\repo --drafts %W%\wave-drafts.yaml --goblin-def "%GOB%" --dry >> %L% 2>&1
echo RC=!ERRORLEVEL! >> %L%
echo ==== wave dry FINISHED %DATE% %TIME% ==== >> %L%
type %L%
