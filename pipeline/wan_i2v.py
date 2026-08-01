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


def load_animegen(torch, a):
    """AnimeGen-I2V, following AIdeaLab's OWN recipe from their model card.

    Written after reading the card rather than guessing at it. My first attempt
    reached for bitsandbytes 8-bit quantisation; the authors instead use
    diffusers' built-in `enable_layerwise_casting` — fp8 storage, bf16 compute —
    which needs no extra dependency and is what makes a 27B model sit on a 24GB
    card. I had also recorded "80GB VRAM" as the blocker, which came from the BASE
    Wan A14B readme; AnimeGen's own card says "RTX 4090 or higher", i.e. 24GB.
    The model was never out of reach.

    Their recipe, three parts:
      - the two anime-trained transformers come from AnimeGen
      - the VAE and pipeline scaffolding come from the base Wan A14B repo
      - Lightning 4-step LoRAs cut 50 steps to 4 at guidance 1.0

    LICENCE NOTE, deliberately not silent: the Lightning LoRAs live in
    lightx2v/Wan2.2-Lightning, whose HF metadata says apache-2.0 but which ships
    NO LICENSE FILE — we cannot quote it, and our own gate calls unquotable
    "unknown". So --no-lora runs AnimeGen without them (more steps, slower, but
    every weight we use has a licence we can read). Default is WITH the LoRAs
    because the canary's job is to test the anime look, and a founder decision on
    that repo can come after we know whether the look is worth having.
    """
    from diffusers import (AutoencoderKLWan, FlowMatchEulerDiscreteScheduler,
                           WanImageToVideoPipeline, WanTransformer3DModel)
    BASE = "Wan-AI/Wan2.2-I2V-A14B-Diffusers"
    hi = WanTransformer3DModel.from_pretrained(a.model, subfolder="transformer",
                                              torch_dtype=torch.bfloat16)
    lo = WanTransformer3DModel.from_pretrained(a.model, subfolder="transformer_2",
                                               torch_dtype=torch.bfloat16)
    vae = AutoencoderKLWan.from_pretrained(BASE, subfolder="vae",
                                           torch_dtype=torch.float32)
    pipe = WanImageToVideoPipeline.from_pretrained(
        BASE, transformer=hi, transformer_2=lo, vae=vae,
        scheduler=FlowMatchEulerDiscreteScheduler(shift=3.0),
        torch_dtype=torch.bfloat16)
    if not a.no_lora:
        L = "lightx2v/Wan2.2-Lightning"
        stem = "Wan2.2-I2V-A14B-4steps-lora-rank64-Seko-V1"
        pipe.load_lora_weights(L, weight_name=f"{stem}/high_noise_model.safetensors",
                               adapter_name="high")
        pipe.load_lora_weights(L, weight_name=f"{stem}/low_noise_model.safetensors",
                               adapter_name="low", load_into_transformer_2=True)
        pipe.set_adapters(["high", "low"], adapter_weights=[1.0, 1.0])
        print("Lightning 4-step LoRAs loaded", flush=True)
    # fp8 storage / bf16 compute — the authors' own way of fitting 24GB
    for tr in (hi, lo):
        tr.enable_layerwise_casting(storage_dtype=torch.float8_e4m3fn,
                                    compute_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    print("AnimeGen: fp8 layerwise casting + cpu offload", flush=True)
    return pipe


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
    # QUANTISE ON LOAD, when asked. The founder's verdict after screening six Wan
    # takes was "wan 2.2 is still pretty good, the problem is its not made for
    # anime style" — so the model we actually want is an anime finetune, and the
    # best candidate (aidealab/AnimeGen-I2V, Apache-2.0) is an A14B: two 14B
    # experts, ~54GB in bf16, against 24GB of card. No fp8 or GGUF build of that
    # finetune exists, which is why it was parked.
    #
    # It does not have to exist. diffusers can quantise at load time, so we can
    # make our own 8-bit weights instead of waiting for someone to publish some.
    # Guarded, because the API is version-dependent and a silent fallback to
    # bf16 would just OOM three hours later with no explanation.
    # AnimeGen is an A14B with two anime-trained experts and its own documented
    # load recipe — not a drop-in for the 5B path below
    if "animegen" in a.model.lower():
        pipe = load_animegen(torch, a)
        takes_image = True
        print(f"model: {a.model} (anime finetune, authors' recipe)", flush=True)
        return _sample(pipe, a, w, h, frames, takes_image)

    kw = {"torch_dtype": torch.bfloat16}
    if a.quantise != "none":
        try:
            from diffusers import PipelineQuantizationConfig
            kw["quantization_config"] = PipelineQuantizationConfig(
                quant_backend="bitsandbytes_8bit" if a.quantise == "8bit"
                else "bitsandbytes_4bit",
                quant_kwargs={"load_in_8bit": a.quantise == "8bit",
                              "load_in_4bit": a.quantise == "4bit"},
                components_to_quantize=["transformer", "transformer_2",
                                        "text_encoder"])
            print(f"quantising on load: {a.quantise}", flush=True)
        except ImportError as e:
            raise SystemExit(
                f"--quantise {a.quantise} needs a diffusers with "
                f"PipelineQuantizationConfig and bitsandbytes installed ({e}).\n"
                f"Install bitsandbytes in the video venv, or run without "
                f"--quantise on a model that fits unquantised.")
    pipe = WanImageToVideoPipeline.from_pretrained(a.model, **kw)
    print(f"pipeline class: {type(pipe).__name__} (forced image-to-video)")
    # a quantised big model still will not sit entirely on 24GB; offload streams
    # modules through system RAM, which is slow but finishes
    if a.quantise != "none" or a.offload:
        pipe.enable_model_cpu_offload()
        print("model cpu offload ON (big model: slower per clip, but it fits)")
    else:
        pipe.to("cuda")
    import inspect
    takes_image = "image" in inspect.signature(pipe.__call__).parameters
    if not takes_image:
        print("WARNING: this pipeline takes no image - text-to-video only")

    return _sample(pipe, a, w, h, frames, takes_image)


def _sample(pipe, a, w, h, frames, takes_image) -> int:
    """ONE process, MANY clips — shared by both model paths.

    Sampling is only a fraction of a clip's wall time; the rest was reloading the
    model from disk for every beat. Loading once and looping turned four clips
    from ~44 minutes into a bit over ten.
    """
    import torch
    from diffusers.utils import export_to_video
    from PIL import Image

    jobs = json.loads(Path(a.jobs).read_text()) if a.jobs else \
        [{"init": a.init, "out": a.out, "prompt": a.prompt, "seed": a.seed}]
    for i, job in enumerate(jobs, 1):
        t0 = time.time()
        img = Image.open(job["init"]).convert("RGB").resize((w, h), Image.LANCZOS)
        # per-job negative: the beat's own "No person, no ghost…" clauses, moved
        # out of the positive prompt where they were being read as REQUESTS
        neg = f"{NEG}, {job['negative']}" if job.get("negative") else NEG
        prompt = job["prompt"]
        steps, guidance = a.steps, a.guidance
        if "animegen" in a.model.lower():
            # the authors' own numbers: "Japanese anime style, " + a MOTION-only
            # prompt, 4 steps at guidance 1.0 (the Lightning LoRAs do the rest),
            # and their short negative. 50 steps at cfg 5 would be fighting the
            # distilled schedule.
            prompt = f"Japanese anime style, {prompt}"
            neg = f"3d, cg, photo, stop, wait, {neg}"
            if not a.no_lora:
                steps, guidance = 4, 1.0
        kw = dict(prompt=prompt, negative_prompt=neg, height=h, width=w,
                  num_frames=frames, num_inference_steps=steps,
                  guidance_scale=guidance,
                  generator=torch.Generator(device="cpu").manual_seed(int(job["seed"])))
        if takes_image:
            kw["image"] = img
        out = pipe(**kw).frames[0]
        Path(job["out"]).parent.mkdir(parents=True, exist_ok=True)
        export_to_video(out, job["out"], fps=a.fps)
        print(f"[{i}/{len(jobs)}] wrote {job['out']} in {time.time()-t0:.0f}s "
              f"({frames} frames, {w}x{h}, {steps} steps)", flush=True)
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
    ap.add_argument("--no-lora", action="store_true",
                    help="AnimeGen without the Lightning LoRAs — slower, but every "
                         "weight has a licence we can quote (lightx2v ships none)")
    ap.add_argument("--quantise", default="none", choices=["none", "8bit", "4bit"],
                    help="quantise at load so a model bigger than VRAM fits")
    ap.add_argument("--offload", action="store_true",
                    help="stream modules through system RAM (slow, but fits)")
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
