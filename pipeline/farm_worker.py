#!/usr/bin/env python3
"""The farm worker — one script that turns any capable machine into a renderer.

Born 2026-07-29, the day the RunPod heartbeat pattern was proven: a worker
clones the repo, renders candidate stills with the exact recipe the whole
project uses, and pushes results to its own branch with a heartbeat at every
stage. This generalizes that worker from "a rented pod" to "any machine" —
the family laptop farm first, and later any contributor's GPU (D11/D12: the
same script IS the compute-donation daemon; a stranger running it is a
citizen watering the tree with cycles instead of clips).

    python3 pipeline/farm_worker.py --name dads-msi [--once]

Loop: poll pipeline/farm-queue.yaml on origin/main; when it lists work for
--name (or "any"), render those beats and push to farm-results-<name>;
repeat. The steward merges results to ballots, credits the machine's owner
in the watering ledger (type: compute), and clears the queue entry.

- picks the best device it has: cuda -> mps -> refuse (cpu is not worth the
  electricity for SDXL; a machine without a real GPU should not be farming)
- §6 gate: renders only founder-approved nodes, same as every other tool
- MPS is fp32 (fp16 NaNs to black — the 2026-07-27 lesson); cuda uses
  bf16/fp16 by capability, same as runpod_render
- heartbeats + full log ship with every stage; a silent worker is impossible

Queue entry shape (pipeline/farm-queue.yaml):
    tasks:
      - id: r12                # unique; results land on farm-results-<name>
        worker: any            # or a specific --name
        node: 001-capability-inventory
        beats: "4,6"
        seeds: 4
        init: ""               # optional repo-relative path (img2img)
        strength: 0.5
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))

QUEUE = "pipeline/farm-queue.yaml"
POLL_SECONDS = 60
# How many times a task may FAIL before this worker stops picking it up. 2 = one
# retry for a transient drop, then move on — see finished_tasks().
MAX_ATTEMPTS = 2


def sh(*args, check=True, capture=False):
    return subprocess.run(args, cwd=REPO, check=check,
                          capture_output=capture, text=True)


def queue_head():
    """The queue as of origin/main, without touching the working tree."""
    sh("git", "fetch", "-q", "origin", "main", check=False)
    r = sh("git", "show", f"origin/main:{QUEUE}", check=False, capture=True)
    if r.returncode != 0:
        return []
    return (yaml.safe_load(r.stdout) or {}).get("tasks", []) or []


def pick_device():
    import torch
    if torch.cuda.is_available():
        cap = torch.cuda.get_device_capability()[0]
        return "cuda", (torch.bfloat16 if cap >= 8 else torch.float16)
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps", torch.float32          # fp16 NaNs to black on MPS
    raise SystemExit("no cuda or mps device — this machine should not farm")


class Courier:
    """Heartbeats + results on farm-results-<name>, RunPod-boot style."""

    def __init__(self, name: str):
        self.branch = f"farm-results-{name}"
        self.out = REPO / "farm-out"
        self.log = []
        self.unpushed = 0

    def mark(self, stage: str):
        self.out.mkdir(exist_ok=True)
        stamp = time.strftime("%H:%M:%SZ", time.gmtime())
        # utf-8 on every WRITE too, not just prints: Windows defaults these to
        # cp1252, and the log carries Wan's Chinese negative prompt plus the
        # em-dashes from shots.md, so writing it raised UnicodeEncodeError and
        # killed the worker mid-task (the 5090, 2026-07-31). Fifth cp1252
        # casualty; the lesson each time is that logging must not be able to
        # kill the thing it logs.
        with (self.out / "heartbeat.txt").open("a", encoding="utf-8") as f:
            f.write(f"{stamp} {stage}\n")
        (self.out / "worker-log.txt").write_text("\n".join(self.log[-400:]),
                                                 encoding="utf-8", errors="replace")
        sh("git", "checkout", "-qB", self.branch, check=False)
        sh("git", "add", "-A", str(self.out), check=False)
        sh("git", "commit", "-qm", f"hb: {stage}", check=False)
        # The push is the ONLY thing that makes any of this visible, and it ran
        # with its error suppressed AND -q. On 2026-08-01 the 5090 rendered its
        # way through the whole queue — "7 task(s) done this session" — while
        # GitHub received nothing for nearly six hours. From outside it looked
        # like a hung machine; the work was on disk the whole time. A courier
        # that cannot deliver has to SAY SO, or the heartbeat is theatre.
        r = sh("git", "push", "-f", "origin", self.branch,
               check=False, capture=True)
        if r.returncode:
            self.unpushed += 1
            print(f"!! PUSH FAILED ({self.unpushed} in a row) — results are on "
                  f"local disk only, in {self.out}\n"
                  f"   {(r.stderr or r.stdout or '').strip()[-400:]}", flush=True)
        elif self.unpushed:
            print(f"push recovered after {self.unpushed} failure(s)", flush=True)
            self.unpushed = 0

    def say(self, line: str):
        print(line, flush=True)
        self.log.append(line)


def lock_path(name: str) -> Path:
    """Outside the repo on purpose: farm-out is committed and force-pushed by
    Courier.mark(), and a lock file living there would be shipped to the branch
    and then clobbered by the other worker — the very thing it exists to stop."""
    return Path(tempfile.gettempdir()) / f"banyan-farm-{name}.lock"


def acquire(name: str, force: bool = False) -> Path:
    """One worker per machine handle. Exits rather than sharing a GPU.

    TWO of these ran on the 5090 on 2026-07-31 — started 21 minutes apart, both
    polling the same queue, both claiming the same tasks. The heartbeat shows it
    plainly: `2x STARTED task=vid-720p-all-1785529520`, two prefetch starts, and
    two timeouts firing at 14430s and 14404s against a 14400s limit.

    The damage was not just duplicated effort. Single beats had been rendering in
    ~13 minutes; under contention the same work took ~26. That is what made an
    8-clip batch overrun four hours and lose everything — the batch was sized
    against uncontended throughput and then run at half of it. Both processes
    also `git push -qf` the same branch from the same working tree, so results
    can erase each other.

    O_CREAT|O_EXCL, and NO automatic staleness takeover: two workers racing to
    decide whose lock is stale is the same bug wearing a hat. A human starts this
    process, so a human can clear a stale lock — the message says how.
    """
    lock = lock_path(name)
    if force and lock.exists():
        lock.unlink()
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        try:
            held = lock.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            held = "(unreadable)"
        raise SystemExit(
            f"another worker already holds this machine: {held}\n"
            f"Two workers on one GPU halve each other's speed and overwrite each\n"
            f"other's results — that is what cost the 8-clip 704x1280 batch four\n"
            f"hours on 2026-07-31.\n\n"
            f"If the other window is still open, close THIS one — nothing is lost.\n"
            f"If nothing else is running, the lock is stale:\n"
            f"  del {lock}\n"
            f"or start with --force to clear it.")
    with os.fdopen(fd, "w") as f:
        f.write(f"pid {os.getpid()} started {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    return lock


def release(lock: Path) -> bool:
    """Drop the lock only if this process is the one holding it."""
    try:
        held = lock.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if f"pid {os.getpid()} " not in held + " ":
        print(f"not releasing {lock.name}: held by another worker ({held.strip()})",
              flush=True)
        return False
    lock.unlink(missing_ok=True)
    return True


def finished_tasks(courier: Courier) -> set:
    """Task ids this machine has already completed, read back from its own
    heartbeat.

    `done_ids` used to live only in memory, and this worker RESTARTS ITSELF
    whenever pipeline code changes on main — so any push during a long task
    meant the finished task ran again from zero on the next poll. A 4-hour
    720p batch would have been rendered twice for nothing (caught before it
    happened, 2026-08-01, with an 8-clip batch mid-flight).

    The heartbeat already records every completion as `DONE task=<id>`, so the
    answer was on disk the whole time. Reading it back makes a restart cheap,
    which is what lets the self-update behaviour stay aggressive.
    """
    hb = courier.out / "heartbeat.txt"
    if not hb.exists():
        return set()
    done, failures = set(), {}
    for line in hb.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.search(r"DONE task=(\S+)", line)
        if m:
            done.add(m.group(1))
            continue
        m = re.search(r"FAIL task=(\S+)", line)
        if m:
            failures[m.group(1)] = failures.get(m.group(1), 0) + 1
    # A FAILED task retries — a dropped download or a transient CUDA error
    # deserves another go, which is why only DONE counted here at first. But
    # "retry forever" is its own bug: a task that fails by hitting its own
    # timeout burns the full timeout EVERY attempt, and because this worker
    # processes the queue in order, the tasks behind it never run at all. A
    # 4-hour video batch that times out would have looped 4 hours at a time
    # while the licence-clean re-render queued behind it starved (the exact
    # shape of the 8-clip 704x1280 batch in flight on 2026-08-01).
    # One retry, then leave it alone and let the queue move.
    for tid, n in failures.items():
        if n >= MAX_ATTEMPTS and tid not in done:
            done.add(tid)
            print(f"skipping {tid}: failed {n}x — giving up so the queue can "
                  f"move. Clear it from {QUEUE} or fix the cause.", flush=True)
    return done


def render_task(task: dict, courier: Courier, device: str, dtype) -> None:
    # video tasks live in their own venv (Wan needs a modern diffusers; the
    # stills path is pinned to 0.29.2 for SDXL) — dispatch before importing
    # anything from this process's pinned stack
    if task.get("video"):
        d = REPO / "genomes/sapling/nodes" / task["node"]
        leaves = sorted((d / "leaves").glob("*-t0-*.yaml"))
        who = str((yaml.safe_load(leaves[-1].read_text(encoding="utf-8")) or {}).get(
            "approved_by", "none")) if leaves else "none"
        if not who.startswith("founder"):
            raise SystemExit(f"{task['node']} NOT founder-approved — STEWARDSHIP §6")
        import video_task
        return video_task.run(task, courier, d)

    from generate_shots import parse_shots
    from sd_prompt import compress, extra_negatives, suppressed_negatives
    import torch
    from diffusers import (StableDiffusionXLImg2ImgPipeline,
                           StableDiffusionXLPipeline)

    NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, "
           "low quality, blurry, extra limbs, deformed, jpeg artifacts, "
           "realistic skin texture")
    # task may name another OPEN model (bake-offs); default = house model
    BASE = task.get("model") or "cagliostrolab/animagine-xl-3.1"
    SEED = int(task.get("seed_base", 20260719))

    d = REPO / "genomes/sapling/nodes" / task["node"]
    leaves = sorted((d / "leaves").glob("*-t0-*.yaml"))
    who = str((yaml.safe_load(leaves[-1].read_text(encoding="utf-8")) or {}).get(
        "approved_by", "none")) if leaves else "none"
    if not who.startswith("founder"):
        raise SystemExit(f"{task['node']} NOT founder-approved — STEWARDSHIP §6")

    init_rel = task.get("init") or ""
    cls = StableDiffusionXLImg2ImgPipeline if init_rel else StableDiffusionXLPipeline
    pipe = cls.from_pretrained(BASE, torch_dtype=dtype, use_safetensors=True)
    pipe.to(device)
    courier.mark(f"MODEL_LOADED {device}/{dtype}".replace("torch.", ""))

    # encoding pinned: Windows defaults to cp1252, which mangles the em-dash
    # in "## Beat NN —" headings and parse_shots finds zero beats (KeyError,
    # the msi worker's first-light failure, 2026-07-29)
    shots = {s["num"]: s for s in parse_shots((d / "shots.md").read_text(encoding="utf-8"))}
    # a task may carry its own prompt (world-reference renders anchored to an
    # APPROVED node's world — §6 checked above; slug names the output)
    if task.get("prompt"):
        jobs = [{"num": 0, "slug": task.get("slug", "custom"),
                 "prompt": task["prompt"]}]
    else:
        jobs = [shots[int(b)] for b in str(task["beats"]).split(",")]
    for s in jobs:
        num = s["num"]
        ptext, _ = compress(s["prompt"])
        neg = NEG
        for term in suppressed_negatives(s["prompt"]):
            neg = neg.replace(term + ", ", "")
        extra = extra_negatives(s["prompt"])
        if extra:
            neg = f"{neg}, {extra}"
        for k in range(int(task.get("seeds", 4))):
            t0 = time.time()
            g = torch.Generator(device="cpu").manual_seed(SEED + num + k * 1000)
            kw = dict(prompt=ptext, negative_prompt=neg,
                      num_inference_steps=int(task.get("steps", 40)),
                      guidance_scale=7.5, generator=g)
            if init_rel:
                from PIL import Image
                kw["image"] = Image.open(REPO / init_rel).convert("RGB").resize(
                    (int(task.get("width", 832)), int(task.get("height", 1216))))
                kw["strength"] = float(task.get("strength", 0.5))
            else:
                kw["width"] = int(task.get("width", 832))
                kw["height"] = int(task.get("height", 1216))
            img = pipe(**kw).images[0]
            # EVERY task prefixes outputs with its id: two tasks touching the
            # same beat otherwise overwrite each other on the courier branch
            # (prod-hires clobbered prod-open's beat 3, 2026-07-30 — the
            # frames survived only in git history)
            prefix = f"{task.get('id')}-"
            f = courier.out / f"{prefix}{num:02d}-{s['slug']}-s{k}.png"
            img.save(f)
            courier.say(f"  {f.name} in {time.time()-t0:.0f}s")


def main() -> int:
    # A Windows console is cp1252, and this worker echoes its children's output
    # — which carries em-dashes from shots.md and a Chinese negative prompt. A
    # print() of any of it raised UnicodeEncodeError IN THE WORKER, which is
    # why the msi went silent mid-task instead of reporting its own timeout
    # (2026-07-31: "charmap codec can't encode character"). Never let logging
    # kill the process it is logging.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True,
                    help="this machine's handle (branch: farm-results-<name>)")
    ap.add_argument("--once", action="store_true",
                    help="do one queue pass and exit (no polling loop)")
    ap.add_argument("--force", action="store_true",
                    help="clear a stale single-instance lock and run anyway")
    a = ap.parse_args()

    # one worker per machine handle, before the GPU is touched
    lock = acquire(a.name, force=a.force)
    device, dtype = pick_device()
    courier = Courier(a.name)
    print(f"farm worker '{a.name}' on {device} — polling {QUEUE} every {POLL_SECONDS}s")
    done_ids = finished_tasks(courier)
    if done_ids:
        print(f"already finished (from heartbeat): {', '.join(sorted(done_ids))}")
    while True:
        for task in queue_head():
            tid = str(task.get("id"))
            if tid in done_ids or task.get("worker", "any") not in ("any", a.name):
                continue
            # render from CURRENT main, not whatever checkout the machine was
            # born with (the msi's first task ran from its USB-era files)
            # fingerprint EVERY pipeline module, not just this file: video_task
            # and wan_i2v changed while this process kept its already-imported
            # video_task in memory, so a new script ran against old caller code
            # (2026-07-30 canary 2, exit 2 on missing --stage)
            def _fp():
                return sorted((p.name, p.stat().st_mtime_ns, p.stat().st_size)
                              for p in Path(__file__).parent.glob("*.py"))
            before = _fp()
            # sync code files from main WITHOUT switching branches: a branch
            # switch deletes farm-out (tracked here, absent on main), which is
            # how each task erased its predecessors' results (2026-07-29 late)
            sh("git", "checkout", "-q", "origin/main", "--", ".", check=False)
            if _fp() != before:
                # a running process can't hot-swap its source or its imports
                # (the 2026-07-29 lesson: workers synced the new file but kept
                # executing the old one from memory). Relaunch.
                print("pipeline code updated — restarting myself", flush=True)
                # release FIRST: the child re-runs main() and calls acquire(),
                # which would fail against our own still-held lock and kill the
                # worker on every code update.
                #
                # But release ONLY OUR OWN. A bare unlink() deletes whichever
                # lock is there, so a second worker restarting would quietly free
                # the FIRST worker's lock and then take it — which is exactly
                # what happened on 2026-08-01: worker 2 came out of its prefetch
                # at 02:19, restarted, wiped worker 1's lock, and both ran on.
                # A mutex you can release on someone else's behalf is not a mutex.
                release(lock)
                # NOT os.execv: on Windows it replaces the process in a way that
                # detaches it from the console, so the worker vanished after
                # exactly one task every time pipeline code changed (the msi, twice
                # on 2026-07-31). Re-run as a CHILD sharing this console, then exit
                # with its status — works the same on POSIX.
                sys.exit(subprocess.run([sys.executable] + sys.argv).returncode)
            courier.mark(f"STARTED task={tid} beats={task.get('beats')} on {device}")
            try:
                render_task(task, courier, device, dtype)
                courier.mark(f"DONE task={tid}")
            except Exception:                     # noqa: BLE001 — ship it, don't die
                import traceback
                courier.say(traceback.format_exc())
                courier.mark(f"FAIL task={tid}")
            done_ids.add(tid)
        if a.once:
            return 0
        print(f"[{time.strftime('%H:%M:%S')}] polling — queue empty for me, {len(done_ids)} task(s) done this session", flush=True)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    sys.exit(main())
