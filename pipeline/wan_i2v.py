#!/usr/bin/env python3
"""Image-to-video from an approved still — Wan 2.2 TI2V-5B, $0, local.

Runs under its OWN venv (see video_task.py): Wan needs a modern diffusers,
while the stills worker is pinned to 0.29.2 for SDXL. Keeping them apart is
the whole reason this is a separate script instead of an import.

Model choice (research 2026-07-30): Wan 2.2 is the newest OPEN-weight
generation (2.5+ are API-only) and is Apache 2.0, so publishing the output
under the tree's CC BY licence is clean. TI2V-5B is one ~10GB model at native
704x1280 — our exact 9:16 — where the 14B variant swaps two 8.5GB experts
mid-sample and would thrash a 16GB-RAM machine.

TWO PROCESSES, ON PURPOSE. Loading the text encoder (UMT5-XXL, ~11GB) and the
transformer in one process crashed the 16GB Windows machine with an access
violation (0xC0000005 — RAM exhaustion, not a python error). `--stage encode`
writes the prompt embeddings to a .pt and exits, which is the only way to
truly hand that memory back on Windows; `--stage render` then loads the
pipeline with text_encoder=None and consumes the file.

    <venv>/python wan_i2v.py --stage encode --prompt "..." --embeds e.pt
    <venv>/python wan_i2v.py --stage render --embeds e.pt --init still.png \
        --out clip.mp4 [--seconds 4] [--steps 25] [--size 480x832]
"""

import argparse
import gc
import sys
from pathlib import Path

MODEL = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
# Wan's own default negative prompt (Chinese, from the official repo): it
# measurably suppresses colour clipping, static frames and mangled limbs.
NEG = ("色调艳丽, 过曝, 静态, 细节模糊不清, 字幕, 风格, 作品, 画作, 画面, 静止, 整体发灰, "
       "最差质量, 低质量, JPEG压缩残留, 丑陋的, 残缺的, 多余的手指, 画得不好的手部, "
       "画得不好的脸部, 畸形的, 毁容的, 形态畸形的肢体, 手指融合, 静止不动的画面, "
       "杂乱的背景, 三条腿, 背景人很多, 倒着走")


def stage_encode(a) -> int:
    """Text encoder ONLY: prompt in, embeddings on disk, process exits."""
    import torch
    from diffusers import WanImageToVideoPipeline

    # transformer/vae stay unloaded — this process must never hold them
    pipe = WanImageToVideoPipeline.from_pretrained(
        MODEL, transformer=None, vae=None, image_encoder=None,
        torch_dtype=torch.bfloat16)
    with torch.no_grad():
        pos, neg = pipe.encode_prompt(prompt=a.prompt, negative_prompt=NEG,
                                      do_classifier_free_guidance=True,
                                      device="cpu")
    torch.save({"prompt_embeds": pos.to(torch.bfloat16),
                "negative_prompt_embeds": neg.to(torch.bfloat16)}, a.embeds)
    print(f"encoded to {a.embeds} {tuple(pos.shape)}")
    return 0


def stage_render(a) -> int:
    """Transformer + VAE only, fed pre-computed embeddings."""
    import torch
    from diffusers import WanImageToVideoPipeline
    from diffusers.utils import export_to_video
    from PIL import Image

    e = torch.load(a.embeds, map_location="cpu")
    w, h = (int(v) for v in a.size.lower().split("x"))
    frames = int(a.seconds * a.fps)
    frames = frames - (frames % 4) + 1          # Wan's 4n+1 temporal grid

    pipe = WanImageToVideoPipeline.from_pretrained(
        MODEL, text_encoder=None, torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    # the VAE is the other RAM spike; the helper's name and presence vary by
    # diffusers version and pipeline, so reach for whichever exists
    for enable in (getattr(pipe, "enable_vae_tiling", None),
                   getattr(getattr(pipe, "vae", None), "enable_tiling", None)):
        if callable(enable):
            enable()
            break
    gc.collect()

    # embeddings arrive from the encode process on CPU, but cpu-offload runs
    # the transformer on the GPU and does not move caller-supplied tensors
    # ("mat1 is on cpu, different from other tensors on cuda:0") — they are
    # small, so hand them over on the execution device
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    img = Image.open(a.init).convert("RGB").resize((w, h), Image.LANCZOS)
    out = pipe(
        image=img,
        prompt_embeds=e["prompt_embeds"].to(dev),
        negative_prompt_embeds=e["negative_prompt_embeds"].to(dev),
        height=h, width=w, num_frames=frames,
        num_inference_steps=a.steps, guidance_scale=5.0,
        generator=torch.Generator(device="cpu").manual_seed(a.seed),
    ).frames[0]

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    export_to_video(out, a.out, fps=a.fps)
    print(f"wrote {a.out} ({frames} frames, {w}x{h})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["encode", "render"], required=True)
    ap.add_argument("--embeds", required=True)
    ap.add_argument("--prompt", default="")
    ap.add_argument("--init", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--seconds", type=float, default=4.0)
    ap.add_argument("--steps", type=int, default=25)
    ap.add_argument("--size", default="480x832", help="WxH (Wan bucket)")
    ap.add_argument("--seed", type=int, default=20260731)
    ap.add_argument("--fps", type=int, default=24)
    a = ap.parse_args()
    return stage_encode(a) if a.stage == "encode" else stage_render(a)


if __name__ == "__main__":
    sys.exit(main())
