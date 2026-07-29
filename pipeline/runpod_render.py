#!/usr/bin/env python3
"""The worker half of the RunPod fast lane — runs ON the rented GPU.

Renders candidate stills for the requested beats with the exact recipe the
whole project uses (Animagine XL 3.1, per-beat prompts from shots.md through
sd_prompt, IP-Adapter refs when the beat calls for one), then pushes results
to the `runpod-results` branch and exits. The controller on the founder's
machine (runpod_lane.py) launches pods, watches the branch, merges candidates
to the board, and terminates the pod — every minute ledgered.

Runs from a clean clone; expects env:
  BEATS      comma list, e.g. "4,7"
  SEEDS      variants per beat (default 4)
(delivery + DEPLOY_KEY handling live in runpod_boot.sh, the heartbeat courier)
"""

import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from generate_shots import parse_shots  # noqa: E402
from sd_prompt import compress, extra_negatives, suppressed_negatives  # noqa: E402

NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, low quality, "
       "blurry, extra limbs, deformed, jpeg artifacts, realistic skin texture")
BASE = "cagliostrolab/animagine-xl-3.1"
SEED = 20260719


def main() -> int:
    beats = [int(b) for b in os.environ["BEATS"].split(",")]
    seeds = int(os.environ.get("SEEDS", "4"))
    # img2img: INIT is a repo-relative image path (the clone has it), STRENGTH 0-1.
    init_rel = os.environ.get("INIT", "")
    strength = float(os.environ.get("STRENGTH", "0.5"))
    node = os.environ.get("NODE", "001-capability-inventory")
    d = REPO / "genomes/sapling/nodes" / node

    # §6 — same gate as everywhere; the worker refuses unapproved narrative
    import yaml
    leaves = sorted((d / "leaves").glob("*-t0-*.yaml"))
    who = str((yaml.safe_load(leaves[-1].read_text()) or {}).get("approved_by", "none")) if leaves else "none"
    if not who.startswith("founder"):
        raise SystemExit(f"{node} is NOT founder-approved ({who}) — STEWARDSHIP §6")

    import torch
    from diffusers import StableDiffusionXLImg2ImgPipeline, StableDiffusionXLPipeline
    dtype = torch.bfloat16 if torch.cuda.get_device_capability()[0] >= 8 else torch.float16
    cls = StableDiffusionXLImg2ImgPipeline if init_rel else StableDiffusionXLPipeline
    pipe = cls.from_pretrained(BASE, torch_dtype=dtype, use_safetensors=True)
    pipe.to("cuda")
    print(f"pipeline ready ({dtype})", flush=True)

    outdir = REPO / "runpod-out"
    outdir.mkdir(exist_ok=True)
    shots = {s["num"]: s for s in parse_shots((d / "shots.md").read_text())}
    for num in beats:
        s = shots[num]
        ptext, _ = compress(s["prompt"])
        neg = NEG
        for term in suppressed_negatives(s["prompt"]):
            neg = neg.replace(term + ", ", "")
        extra = extra_negatives(s["prompt"])
        if extra:
            neg = f"{neg}, {extra}"
        for k in range(seeds):
            t0 = time.time()
            g = torch.Generator(device="cpu").manual_seed(SEED + num + k * 1000)
            if init_rel:
                from PIL import Image
                base_img = Image.open(REPO / init_rel).convert("RGB").resize((832, 1216))
                img = pipe(prompt=ptext, negative_prompt=neg, image=base_img,
                           strength=strength, num_inference_steps=40,
                           guidance_scale=7.5, generator=g).images[0]
            else:
                img = pipe(prompt=ptext, negative_prompt=neg, width=832, height=1216,
                           num_inference_steps=40, guidance_scale=7.5,
                           generator=g).images[0]
            f = outdir / f"{num:02d}-{s['slug']}-s{k}.png"
            img.save(f)
            print(f"  {f.name} in {time.time()-t0:.0f}s", flush=True)

    # delivery is runpod_boot.sh's job now (heartbeat courier, set up before
    # anything can fail) — this process only renders and reports
    print("RENDER_COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
