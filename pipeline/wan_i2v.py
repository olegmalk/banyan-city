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

    <video-venv>/python wan_i2v.py --init still.png --prompt "..." \
        --out clip.mp4 [--seconds 4] [--steps 30] [--size 704x1280] [--seed N]
"""

import argparse
import sys
from pathlib import Path

MODEL = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
# Wan's own default negative prompt (Chinese, from the official repo): it
# measurably suppresses colour clipping, static frames and mangled limbs.
NEG = ("色调艳丽, 过曝, 静态, 细节模糊不清, 字幕, 风格, 作品, 画作, 画面, 静止, 整体发灰, "
       "最差质量, 低质量, JPEG压缩残留, 丑陋的, 残缺的, 多余的手指, 画得不好的手部, "
       "画得不好的脸部, 畸形的, 毁容的, 形态畸形的肢体, 手指融合, 静止不动的画面, "
       "杂乱的背景, 三条腿, 背景人很多, 倒着走")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", required=True, help="approved still to animate")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seconds", type=float, default=4.0)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--size", default="704x1280", help="WxH (Wan bucket)")
    ap.add_argument("--seed", type=int, default=20260731)
    ap.add_argument("--fps", type=int, default=24)
    a = ap.parse_args()

    import torch
    from diffusers import WanImageToVideoPipeline
    from diffusers.utils import export_to_video
    from PIL import Image

    w, h = (int(v) for v in a.size.lower().split("x"))
    # 4n+1 frames is Wan's temporal grid; 81 frames @24fps = the 3.4s default
    frames = int(a.seconds * a.fps)
    frames = frames - (frames % 4) + 1

    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    pipe = WanImageToVideoPipeline.from_pretrained(MODEL, torch_dtype=dtype)
    if torch.cuda.is_available():
        # layer-by-layer offload: 12GB cards hold the working set only
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cpu")

    img = Image.open(a.init).convert("RGB").resize((w, h), Image.LANCZOS)
    out = pipe(
        image=img, prompt=a.prompt, negative_prompt=NEG,
        height=h, width=w, num_frames=frames,
        num_inference_steps=a.steps, guidance_scale=5.0,
        generator=torch.Generator(device="cpu").manual_seed(a.seed),
    ).frames[0]

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    export_to_video(out, a.out, fps=a.fps)
    print(f"wrote {a.out} ({frames} frames, {w}x{h})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
