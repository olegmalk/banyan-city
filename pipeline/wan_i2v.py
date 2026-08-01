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
import json
import sys
import time
from pathlib import Path

DEFAULT_MODEL = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
# Publish-safe alternatives, verified 2026-08-01 against fetched primary sources
# (see drops/MODEL-RESEARCH-2026-08-01.md). Keyed by short name so a queue entry
# can say `video_model: animegen` instead of carrying a repo id around.
#
# NOT a list of "models that look good" — a list of models whose LICENCE was read
# and quoted. LTX and HunyuanVideo are deliberately absent: LTX's weights ship
# under three different licences by version (the 2B is research-only) while its
# GitHub LICENSE is a plain Apache-2.0 that covers CODE ONLY, and Hunyuan's
# community licence excludes the EU, UK and South Korea from its permitted
# territory — we would breach it by publishing at all.
MODELS = {
    "ti2v-5b":  "Wan-AI/Wan2.2-TI2V-5B-Diffusers",   # incumbent, Apache-2.0
    "animegen": "aidealab/AnimeGen-I2V",             # Apache-2.0, anime finetune
                                                     # of Wan 2.2: force-prepends
                                                     # "Japanese anime style" and
                                                     # negatives out 3d/cg/photo,
                                                     # so it fails TOWARD anime —
                                                     # our named drift problem
}
MODEL = DEFAULT_MODEL
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
        a.model, transformer=None, vae=None, image_encoder=None,
        torch_dtype=torch.bfloat16)
    with torch.no_grad():
        pos, neg = pipe.encode_prompt(prompt=a.prompt, negative_prompt=NEG,
                                      do_classifier_free_guidance=True,
                                      device="cpu")
    torch.save({"prompt_embeds": pos.to(torch.bfloat16),
                "negative_prompt_embeds": neg.to(torch.bfloat16)}, a.embeds)
    print(f"encoded to {a.embeds} {tuple(pos.shape)}")
    return 0


def stage_simple(a) -> int:
    """Everything in one process, the library's own way — for cards with room.

    The first 5090 clip came out as abstract smears with no relation to the
    conditioning image: the two-process trick (pre-computed embeddings, a
    force-named pipeline class) exists only to fit a 16GB machine, and one of
    its shortcuts was clearly bypassing the image path. A 24GB card does not
    need any of it, so here the model's own model_index.json chooses the
    pipeline and the pipeline does its own encoding.
    """
    import torch
    from diffusers import DiffusionPipeline
    from diffusers.utils import export_to_video
    from PIL import Image

    w, h = (int(v) for v in a.size.lower().split("x"))
    frames = int(a.seconds * a.fps)
    frames = frames - (frames % 4) + 1

    # NOT DiffusionPipeline: this repo's model_index names WanPipeline, which is
    # TEXT-to-video and silently ignores an image. That is how the 5090 spent an
    # afternoon generating pretty clips of whatever the prompt described while
    # the approved frame went unused (2026-07-31 — the warning I had built in is
    # what caught it). Name the image-to-video class explicitly, always.
    from diffusers import WanImageToVideoPipeline
    pipe = WanImageToVideoPipeline.from_pretrained(a.model, torch_dtype=torch.bfloat16)
    print(f"pipeline class: {type(pipe).__name__} (forced image-to-video)")
    pipe.to("cuda")
    import inspect
    takes_image = "image" in inspect.signature(pipe.__call__).parameters
    if not takes_image:
        print("WARNING: this pipeline takes no image - text-to-video only")

    # ONE process, MANY clips. Sampling is only ~71s of an ~11min clip; the rest
    # was reloading this 10GB model from disk for every single beat. Loading once
    # and looping turns four clips from ~44 minutes into a bit over ten.
    jobs = json.loads(Path(a.jobs).read_text()) if a.jobs else \
        [{"init": a.init, "out": a.out, "prompt": a.prompt, "seed": a.seed}]
    for i, job in enumerate(jobs, 1):
        t0 = time.time()
        img = Image.open(job["init"]).convert("RGB").resize((w, h), Image.LANCZOS)
        kw = dict(prompt=job["prompt"], negative_prompt=NEG, height=h, width=w,
                  num_frames=frames, num_inference_steps=a.steps,
                  guidance_scale=a.guidance,
                  generator=torch.Generator(device="cpu").manual_seed(int(job["seed"])))
        if takes_image:
            kw["image"] = img
        out = pipe(**kw).frames[0]
        Path(job["out"]).parent.mkdir(parents=True, exist_ok=True)
        export_to_video(out, job["out"], fps=a.fps)
        print(f"[{i}/{len(jobs)}] wrote {job['out']} in {time.time()-t0:.0f}s "
              f"({frames} frames, {w}x{h})", flush=True)
    return 0


def stage_render(a) -> int:
    """Transformer + VAE only, fed pre-computed embeddings (small-RAM path)."""
    import torch
    from diffusers import WanImageToVideoPipeline
    from diffusers.utils import export_to_video
    from PIL import Image

    e = torch.load(a.embeds, map_location="cpu")
    w, h = (int(v) for v in a.size.lower().split("x"))
    frames = int(a.seconds * a.fps)
    frames = frames - (frames % 4) + 1          # Wan's 4n+1 temporal grid

    pipe = WanImageToVideoPipeline.from_pretrained(
        a.model, text_encoder=None, torch_dtype=torch.bfloat16)
    # cpu-offload streams every module through system RAM on every step, which
    # is what made a 12GB/16GB machine take two hours for one draft clip. A
    # card with room for the model should just hold it.
    vram = (torch.cuda.get_device_properties(0).total_memory / 1e9
            if torch.cuda.is_available() else 0)
    if vram >= 20:
        pipe.to("cuda")
        print(f"{vram:.0f}GB VRAM: model resident, no offload")
    else:
        pipe.enable_model_cpu_offload()
        print(f"{vram:.0f}GB VRAM: offloading through system RAM")
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
    ap.add_argument("--stage", choices=["encode", "render", "simple"], required=True)
    ap.add_argument("--embeds", required=True)
    ap.add_argument("--prompt", default="")
    ap.add_argument("--init", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--jobs", default="", help="json list of {init,out,prompt,seed} - one model load for all of them")
    ap.add_argument("--seconds", type=float, default=4.0)
    ap.add_argument("--steps", type=int, default=25)
    ap.add_argument("--guidance", type=float, default=5.0,
                    help="cfg; higher follows the prompt harder, lower drifts")
    ap.add_argument("--size", default="480x832", help="WxH (Wan bucket)")
    ap.add_argument("--model", default="ti2v-5b",
                    help=f"short name {sorted(MODELS)} or a full HF repo id")
    ap.add_argument("--seed", type=int, default=20260731)
    ap.add_argument("--fps", type=int, default=24)
    a = ap.parse_args()
    # short name -> repo id; anything unrecognised is passed through as a repo id
    # so a one-off experiment does not need a code change, but the CURATED names
    # are the ones whose licence we have actually read.
    a.model = MODELS.get(a.model, a.model)
    print(f"model: {a.model}", flush=True)
    if a.stage == "encode":
        return stage_encode(a)
    return stage_simple(a) if a.stage == "simple" else stage_render(a)


if __name__ == "__main__":
    sys.exit(main())
