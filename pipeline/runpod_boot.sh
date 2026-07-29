#!/bin/bash
# Boot harness for the RunPod worker — runs ON the pod, first thing after clone.
#
# The 2026-07-29 lesson: two pods launched, billed, and died without a word,
# because delivery (the courier push) only happened at the very END of a
# successful run. This script inverts that: the courier is set up FIRST, and a
# heartbeat marker is pushed to the runpod-results branch at every stage —
# STARTED, DEPS_OK, RENDER_OK, DONE (or *_FAIL with the captured log). A
# silent pod is now impossible: the controller sees the last heartbeat and
# knows exactly where the worker died.
#
# env: DEPLOY_KEY (base64 ed25519), BEATS, SEEDS, INIT, STRENGTH, NODE
set -u
cd "$(dirname "$0")/.."
LOG=/workspace/worker.log
touch "$LOG"

mark () {
    mkdir -p runpod-out
    echo "$(date -u +%H:%M:%SZ) $1" >> runpod-out/heartbeat.txt
    # always ship the log tail with the marker — the log IS the diagnosis
    tail -c 200000 "$LOG" > runpod-out/worker-log.txt 2>/dev/null || true
    git add -A runpod-out >>"$LOG" 2>&1
    git commit -qm "hb: $1" >>"$LOG" 2>&1
    git push -qf origin runpod-results >>"$LOG" 2>&1
}

# courier first, before anything can fail
echo "$DEPLOY_KEY" | base64 -d > /workspace/.courier_key
chmod 600 /workspace/.courier_key
export GIT_SSH_COMMAND="ssh -i /workspace/.courier_key -o StrictHostKeyChecking=no"
git config user.email runpod@banyan.city
git config user.name runpod-courier
git remote set-url origin git@github.com:olegmlkvorg/banyan-city.git
git checkout -qB runpod-results
mark "STARTED beats=${BEATS:-?} gpu=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo none)"

pip -q install diffusers transformers accelerate safetensors pyyaml markdown >>"$LOG" 2>&1 \
    && mark DEPS_OK || { mark DEPS_FAIL; exit 1; }

python3 pipeline/runpod_render.py >>"$LOG" 2>&1 \
    && mark RENDER_OK || { mark RENDER_FAIL; exit 1; }

mark DONE
