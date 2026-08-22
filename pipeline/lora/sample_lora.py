#!/usr/bin/env python3
"""Draw ONE frame from a trained character LoRA, in the renderer that ships plates.

    <venv>/python.exe pipeline/lora/sample_lora.py \
        --lora out/bnyjerry-sdxl-v1.safetensors --lora-weight 0.8 \
        --prompt "bnyjerry, 1boy, solo, standing, ..." \
        --out SAMPLE-bnyjerry-standing-dusk.png

WHY THIS FILE EXISTS RATHER THAN A FLAG ON still_local.py. still_local.py's CLI
is `genome node --beat N` -- it resolves a prompt out of a beat's shot board and
is wired to MPS/float32 for the Mac loop. Nothing in it takes a free prompt, a
LoRA, or an output path, and bending it into taking all three would put a
training-only concern into the path that renders episodes. This is ~90 lines
that does the one thing.

IT RUNS IN THE RENDER VENV, NOT venv-lora, and that is deliberate. The plates we
ship are drawn by `C:\\banyan-farm\\venv` (torch 2.11.0+cu128, diffusers 0.29.2)
at bfloat16 on CUDA. Sampling anywhere else measures a LoRA in an environment
that will never draw a frame for the show. It also keeps the training venv's
dependency set out of the answer -- whatever diffusers version sd-scripts pins
is irrelevant to whether the weights work where we need them to.

bfloat16 and a CPU-seeded generator match render_wave_sample.py exactly
(pipeline/render_wave_sample.py:236,243). This matters more than it looks: the
Mac and this box were measured on 2026-08-16 to disagree by MAE 61 of 255 on
byte-identical inputs at an identical seed, so a sample drawn under different
dtype or device conventions is not comparable to the plates it is judged
against.

Writes a §7.2 sidecar beside the PNG naming the LoRA file and its sha256, so a
frame can always be traced to the exact weights that drew it.
"""

import argparse
import hashlib
import os
import sys

BASE = "cagliostrolab/animagine-xl-3.1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lora", required=True, help="path to the .safetensors LoRA")
    ap.add_argument("--lora-weight", type=float, default=0.8)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--negative", default="")
    ap.add_argument("--width", type=int, default=832)
    ap.add_argument("--height", type=int, default=1216)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--guidance", type=float, default=7.5)
    ap.add_argument("--seed", type=int, default=20260820)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-lora", action="store_true",
                    help="draw the SAME prompt+seed with no LoRA loaded -- the B side "
                         "of the no-regression bar. The pair is the evidence; either "
                         "frame alone proves nothing.")
    args = ap.parse_args()

    import torch
    from diffusers import StableDiffusionXLPipeline

    if not args.no_lora and not os.path.exists(args.lora):
        sys.exit("no such LoRA: %s" % args.lora)

    # THE PEFT GATE, ADDED 2026-08-22 AFTER IT COST A RUN. This file was written
    # on 2026-08-20 and committed without ever being executed; the first time it
    # ran was the sapling training job, which trained for twenty clean minutes,
    # wrote five checkpoints, and then died in nine seconds inside diffusers with
    # `ValueError: PEFT backend is required for this method.` diffusers 0.29.2
    # gates ALL LoRA loading behind USE_PEFT_BACKEND, which is False unless peft
    # is installed -- and it was not, in either venv on the box.
    #
    # Checking it BEFORE the 6.9 GB checkpoint load turns a nine-second waste at
    # the end of an hour into a one-second refusal at the start, and the message
    # carries the exact fix instead of a stack trace. `--no-deps` is not
    # decoration: the render venv is what draws every plate the show ships, and
    # SETUP.md's standing warning is that a careless pip resolve on this sm_120
    # card silently replaces torch with a build that has no Blackwell kernels.
    # peft's own requirements are all already present, so --no-deps installs one
    # pure-python package and moves nothing else. Verified 2026-08-22: pip freeze
    # differed by exactly one line and torch stayed 2.11.0+cu128.
    from diffusers.utils import USE_PEFT_BACKEND
    if not args.no_lora and not USE_PEFT_BACKEND:
        sys.exit(
            "diffusers has no PEFT backend, so load_lora_weights() cannot run and\n"
            "every LoRA sample would fail AFTER loading the base checkpoint.\n"
            "  fix:  <this venv>/python.exe -m pip install --no-deps peft==0.12.0\n"
            "  then: re-run. --no-deps is required -- a plain install may resolve\n"
            "        torch away from 2.11.0+cu128 and break every render on the box.")

    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE, torch_dtype=torch.bfloat16, use_safetensors=True)
    pipe.to("cuda")

    lora_sha = "none"
    if not args.no_lora:
        with open(args.lora, "rb") as fh:
            lora_sha = hashlib.sha256(fh.read()).hexdigest()
        # kohya-format LoRAs load through the same entry point; diffusers
        # converts the key naming on the way in.
        pipe.load_lora_weights(os.path.dirname(os.path.abspath(args.lora)),
                               weight_name=os.path.basename(args.lora))
        pipe.fuse_lora(lora_scale=args.lora_weight)

    gen = torch.Generator(device="cpu").manual_seed(args.seed)
    image = pipe(
        prompt=args.prompt,
        negative_prompt=args.negative or None,
        width=args.width, height=args.height,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        generator=gen,
    ).images[0]

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    image.save(args.out)

    with open(args.out, "rb") as fh:
        png_sha = hashlib.sha256(fh.read()).hexdigest()
    with open(args.out + ".meta.yaml", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(
            'platform: "local-gpu (rtx5090, CUDA, bfloat16)"\n'
            'model: "%s"\n'
            'model_licence: "CreativeML Open RAIL++-M (use restrictions travel; D15)"\n'
            'lora: "%s"\n'
            'lora_sha256: "%s"\n'
            'lora_weight: %s\n'
            'cost_usd: 0.0\n'
            'size: "%dx%d"\n'
            'steps: %d\n'
            'guidance: %s\n'
            'seed: %d\n'
            'png_sha256: "%s"\n'
            'prompt: "%s"\n'
            'negative_prompt: "%s"\n'
            'approved: false\n'
            'provisional: true\n'
            'founder_verdict: null\n'
            'scored: false\n'
            % (BASE,
               "none" if args.no_lora else os.path.basename(args.lora),
               lora_sha, args.lora_weight,
               args.width, args.height, args.steps, args.guidance, args.seed,
               png_sha,
               args.prompt.replace('"', "'"),
               args.negative.replace('"', "'")))

    print("wrote", args.out)
    print("  lora=%s weight=%s seed=%d" %
          ("none" if args.no_lora else os.path.basename(args.lora),
           args.lora_weight, args.seed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
