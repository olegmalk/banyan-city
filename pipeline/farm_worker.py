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
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))

QUEUE = "pipeline/farm-queue.yaml"
POLL_SECONDS = 60


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

    def mark(self, stage: str):
        self.out.mkdir(exist_ok=True)
        stamp = time.strftime("%H:%M:%SZ", time.gmtime())
        with (self.out / "heartbeat.txt").open("a") as f:
            f.write(f"{stamp} {stage}\n")
        (self.out / "worker-log.txt").write_text("\n".join(self.log[-400:]))
        sh("git", "checkout", "-qB", self.branch, check=False)
        sh("git", "add", "-A", str(self.out), check=False)
        sh("git", "commit", "-qm", f"hb: {stage}", check=False)
        sh("git", "push", "-qf", "origin", self.branch, check=False)

    def say(self, line: str):
        print(line, flush=True)
        self.log.append(line)


def render_task(task: dict, courier: Courier, device: str, dtype) -> None:
    from generate_shots import parse_shots
    from sd_prompt import compress, extra_negatives, suppressed_negatives
    import torch
    from diffusers import (StableDiffusionXLImg2ImgPipeline,
                           StableDiffusionXLPipeline)

    NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, "
           "low quality, blurry, extra limbs, deformed, jpeg artifacts, "
           "realistic skin texture")
    BASE, SEED = "cagliostrolab/animagine-xl-3.1", 20260719

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
    for num in [int(b) for b in str(task["beats"]).split(",")]:
        s = shots[num]
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
                      num_inference_steps=40, guidance_scale=7.5, generator=g)
            if init_rel:
                from PIL import Image
                kw["image"] = Image.open(REPO / init_rel).convert("RGB").resize((832, 1216))
                kw["strength"] = float(task.get("strength", 0.5))
            else:
                kw["width"], kw["height"] = 832, 1216
            img = pipe(**kw).images[0]
            f = courier.out / f"{num:02d}-{s['slug']}-s{k}.png"
            img.save(f)
            courier.say(f"  {f.name} in {time.time()-t0:.0f}s")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True,
                    help="this machine's handle (branch: farm-results-<name>)")
    ap.add_argument("--once", action="store_true",
                    help="do one queue pass and exit (no polling loop)")
    a = ap.parse_args()

    device, dtype = pick_device()
    courier = Courier(a.name)
    print(f"farm worker '{a.name}' on {device} — polling {QUEUE} every {POLL_SECONDS}s")
    done_ids = set()
    while True:
        for task in queue_head():
            tid = str(task.get("id"))
            if tid in done_ids or task.get("worker", "any") not in ("any", a.name):
                continue
            # render from CURRENT main, not whatever checkout the machine was
            # born with (the msi's first task ran from its USB-era files)
            sh("git", "checkout", "-q", "main", check=False)
            sh("git", "reset", "-q", "--hard", "origin/main", check=False)
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
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    sys.exit(main())
