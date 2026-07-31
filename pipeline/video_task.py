#!/usr/bin/env python3
"""Motion takes on a farm machine — self-installing, heartbeat-observable.

The open render requests want TAKES, not more frames, and the founder asked
for a free video generator set up without anyone standing at the keyboard
(2026-07-30). So the video stack installs itself the way runpod_boot.sh
proved: a courier mark at every stage, so a silent or stuck machine is
visible from anywhere instead of looking like it is thinking.

Everything lands in ONE deletable folder (C:\\banyan-video on Windows,
~/banyan-video elsewhere) with its own venv — the stills worker stays pinned
to diffusers 0.29.2 for SDXL, and Wan needs a modern one.

Driven by farm_worker when a queue task carries `video: true`.
"""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IS_WIN = platform.system() == "Windows"
ROOT = Path("C:/banyan-video") if IS_WIN else Path.home() / "banyan-video"
VENV = ROOT / "venv"
PY = VENV / ("Scripts/python.exe" if IS_WIN else "bin/python3")
# Blackwell (RTX 50-series) needs cu128 wheels; older builds do not know sm_120
TORCH_INDEX = "https://download.pytorch.org/whl/cu128"


def _run(cmd, courier, stage, timeout=None, retry=False):
    # utf-8 on the child's stdout: Windows consoles default to cp1252, and a
    # single non-ASCII character in a SUCCESS message killed a 25-minute
    # encode with UnicodeEncodeError (2026-07-30, canary 3)
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",
           # HF's newer chunked (xet/CAS) transfer dropped the 10GB model
           # download 23 minutes in on the 5090 (2026-07-31). The classic path
           # resumes; the chunked one restarts.
           "HF_HUB_DISABLE_XET": "1",
           "HF_HUB_DOWNLOAD_TIMEOUT": "60"}
    attempts = 3 if retry else 1
    for attempt in range(1, attempts + 1):
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           env=env, errors="replace")
        if courier:
            courier.say(f"$ {' '.join(str(c) for c in cmd[:6])}…\n{(r.stdout or '')[-1500:]}"
                        f"{(r.stderr or '')[-2500:]}")
        if not r.returncode:
            return r
        # a dropped download is not a broken pipeline: say so and try again,
        # because the next attempt resumes from the bytes already on disk
        transient = any(s in (r.stderr or "") for s in
                        ("CAS Client", "error sending request", "Connection",
                         "Read timed out", "IncompleteRead", "ConnectionError"))
        if attempt < attempts and transient:
            if courier:
                courier.mark(f"VIDEO_RETRY {stage} (attempt {attempt} hit a "
                             f"network drop, resuming)")
            continue
        raise RuntimeError(f"{stage} failed (exit {r.returncode})")
    return r


def ensure_stack(courier) -> None:
    """Create the video venv and its deps, marking every stage."""
    ROOT.mkdir(parents=True, exist_ok=True)
    if not PY.exists():
        courier.mark("VIDEO_VENV_CREATING")
        _run([sys.executable, "-m", "venv", str(VENV)], courier, "venv", timeout=600)
    courier.mark("VIDEO_VENV_OK")

    probe = _run([str(PY), "-c", "import torch,diffusers;print(torch.__version__,"
                 "diffusers.__version__,torch.cuda.is_available())"],
                 None, "probe") if _have(PY, "torch") else None
    if probe is None:
        courier.mark("VIDEO_DEPS_INSTALLING")
        pip = [str(PY), "-m", "pip", "install", "-q", "--retries", "30",
               "--timeout", "120"]     # their router kills long streams
        if IS_WIN:
            _run(pip + ["torch", "--index-url", TORCH_INDEX], courier,
                 "torch cu128", timeout=5400)
        else:
            _run(pip + ["torch"], courier, "torch", timeout=5400)
        _run(pip + ["diffusers>=0.35", "transformers", "accelerate", "safetensors",
                    "ftfy", "imageio", "imageio-ffmpeg", "pillow", "huggingface_hub"],
             courier, "diffusers stack", timeout=5400)
        probe = _run([str(PY), "-c", "import torch,diffusers;print(torch.__version__,"
                     "diffusers.__version__,torch.cuda.is_available())"],
                     courier, "probe")
    courier.mark(f"VIDEO_DEPS_OK {probe.stdout.strip()}")


def gpu_vram_gb() -> float:
    """Total VRAM on device 0, asked of the video venv (this process has no torch)."""
    r = subprocess.run([str(PY), "-c", "import torch;print(torch.cuda.get_device_properties(0)"
                        ".total_memory/1e9 if torch.cuda.is_available() else 0)"],
                       capture_output=True, text=True)
    try:
        return float((r.stdout or "0").strip())
    except ValueError:
        return 0.0


def _have(py: Path, mod: str) -> bool:
    return subprocess.run([str(py), "-c", f"import {mod}"],
                          capture_output=True).returncode == 0


def prefetch(task: dict, courier) -> None:
    """Download named weights into the video venv's cache, nothing more.

    Downloading is the safe half of trying a new model: it takes bandwidth, not
    judgement, so it can happen overnight while the install decision waits for
    a human. Heartbeats mark each repo so a stalled transfer is visible.
    """
    ensure_stack(courier)
    for spec in task.get("prefetch") or []:
        repo = str(spec["repo"])
        pats = spec.get("patterns") or None
        courier.mark(f"PREFETCH_START {repo}")
        code = (
            "import os\n"
            "os.environ['HF_HUB_DISABLE_XET']='1'\n"
            "os.environ['HF_HUB_DOWNLOAD_TIMEOUT']='60'\n"
            "from huggingface_hub import snapshot_download\n"
            f"p=snapshot_download({repo!r}, allow_patterns={pats!r})\n"
            "print('DOWNLOADED', p)\n")
        _run([str(PY), "-c", code], courier, f"prefetch {repo}",
             timeout=21600, retry=True)
        courier.mark(f"PREFETCH_OK {repo}")


def run(task: dict, courier, node_dir: Path) -> None:
    """One video task: N beats animated from their APPROVED stills.

    `beats` names the beats; each beat's still is the conditioning frame, and
    its shot-board prompt (already founder-approved text) drives the motion.
    """
    from generate_shots import parse_shots

    if task.get("prefetch"):
        return prefetch(task, courier)
    ensure_stack(courier)
    # utf-8 pinned: Windows' cp1252 mangles the em-dash in "## Beat NN —"
    # and parse_shots then finds nothing (the msi's first-light failure)
    shots = {s["num"]: s
             for s in parse_shots((node_dir / "shots.md").read_text(encoding="utf-8"))}
    stills = node_dir / "stills"
    beats = [int(b) for b in str(task.get("beats", "")).split(",") if b.strip()]
    size = task.get("size", "704x1280")
    seconds = float(task.get("seconds", 4))
    steps = int(task.get("steps", 30))

    # BATCH on a big card: build the whole job list, then load the model once.
    # Per-clip processes spent ~10 of every 11 minutes reloading 10GB from disk.
    if gpu_vram_gb() >= 20 and len(beats) > 1:
        jobs, outs = [], []
        for num in beats:
            s = shots.get(num)
            init = next((q for q in stills.glob(f"{num:02d}-*.png")
                         if "REVOKED" not in q.name), None)
            if not s or not init:
                courier.say(f"beat {num}: no shot or no approved still - skipped")
                continue
            motion = task.get("motion") or ("subtle continuous motion, gentle camera "
                                            "drift, living scene")
            o = courier.out / f"{task.get('id')}-{num:02d}-{s['slug']}.mp4"
            jobs.append({"init": str(init), "out": str(o),
                         "prompt": f"{motion}. {s['prompt']}"[:900],
                         "seed": int(task.get("seed_base", 20260731)) + num})
            outs.append((num, o))
        if jobs:
            jf = ROOT / f"jobs-{task.get('id')}.json"
            jf.write_text(json.dumps(jobs), encoding="utf-8")
            courier.mark(f"VIDEO_RENDERING batch of {len(jobs)} (one model load)")
            _run([str(PY), str(REPO / "pipeline" / "wan_i2v.py"), "--stage", "simple",
                  "--embeds", str(ROOT / "unused.pt"), "--jobs", str(jf),
                  "--seconds", str(seconds), "--steps", str(steps), "--size", size,
                  "--guidance", str(task.get("guidance", 5.0))],
                 courier, f"batch {task.get('id')}", timeout=14400, retry=True)
            jf.unlink(missing_ok=True)
            made = 0
            for num, o in outs:
                if o.exists() and o.stat().st_size > 10_000:
                    made += 1
                    courier.mark(f"VIDEO_CLIP_OK beat={num:02d} {o.stat().st_size//1024}KB")
                else:
                    courier.mark(f"VIDEO_CLIP_EMPTY beat={num:02d}")
            courier.say(f"video task {task.get('id')}: {made}/{len(outs)} clips")
            if not made:
                raise RuntimeError("no clips produced")
            return

    made = 0
    for num in beats:
        s = shots.get(num)
        if not s:
            courier.say(f"beat {num}: not in shots.md — skipped")
            continue
        init = next((p for p in stills.glob(f"{num:02d}-*.png")
                     if "REVOKED" not in p.name), None)
        if not init:
            courier.say(f"beat {num}: no approved still — skipped")
            continue
        # motion-first wording: the still already IS the composition, so the
        # prompt's job is what MOVES (cycle-001 lesson: front-loaded stillness
        # makes models hold the frame)
        motion = task.get("motion") or "subtle continuous motion, gentle camera drift, living scene"
        prompt = f"{motion}. {s['prompt']}"[:900]
        out = courier.out / f"{task.get('id')}-{num:02d}-{s['slug']}.mp4"
        emb = ROOT / f"embeds-{num:02d}.pt"
        wan = str(REPO / "pipeline" / "wan_i2v.py")
        # two processes: holding the 11GB text encoder AND the transformer in
        # one process killed the 16GB machine with an access violation
        # (0xC0000005). Encoding in a process that then EXITS is the only
        # reliable way to give that memory back on Windows.
        big = gpu_vram_gb() >= 20
        if big:
            # one process, the library's own pipeline class and encoding: the
            # split-process shortcuts are a 16GB workaround and one of them
            # was bypassing the image conditioning (first 5090 clip, garbage)
            courier.mark(f"VIDEO_RENDERING beat={num:02d} (single-process)")
            _run([str(PY), wan, "--stage", "simple", "--embeds", str(emb),
                  "--prompt", prompt, "--init", str(init), "--out", str(out),
                  "--seconds", str(seconds), "--steps", str(steps), "--size", size,
                  "--seed", str(int(task.get("seed_base", 20260731)) + num)],
                 courier, f"beat {num}", timeout=7200, retry=True)
        else:
            courier.mark(f"VIDEO_ENCODING beat={num:02d}")
            _run([str(PY), wan, "--stage", "encode", "--embeds", str(emb),
                  "--prompt", prompt], courier, f"encode {num}", timeout=3600, retry=True)
            courier.mark(f"VIDEO_RENDERING beat={num:02d}")
            _run([str(PY), wan, "--stage", "render", "--embeds", str(emb),
                  "--init", str(init), "--out", str(out),
                  "--seconds", str(seconds), "--steps", str(steps), "--size", size,
                  "--seed", str(int(task.get("seed_base", 20260731)) + num)],
                 courier, f"beat {num}", timeout=7200, retry=True)
        emb.unlink(missing_ok=True)
        if out.exists() and out.stat().st_size > 10_000:
            made += 1
            courier.mark(f"VIDEO_CLIP_OK beat={num:02d} "
                         f"{out.stat().st_size // 1024}KB")
        else:
            courier.mark(f"VIDEO_CLIP_EMPTY beat={num:02d}")
    courier.say(f"video task {task.get('id')}: {made}/{len(beats)} clips")
    if not made:
        raise RuntimeError("no clips produced")
