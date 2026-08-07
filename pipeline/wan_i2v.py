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
import platform
import sys
import threading
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
# Wan's own default negative prompt (Chinese, from the official repo) MINUS its
# anti-stillness terms.
#
# The official list contains 静态 (static), 静止 (motionless) and 静止不动的画面 (a
# motionless picture) — i.e. it tells the model NOT TO BE STILL. That is a sensible
# default for general text-to-video, where a frozen output is the common failure.
# It is backwards for this show: the still IS the approved composition, every
# motion.yaml direction ends "camera locked", and what we want is the small true
# movement and nothing else.
#
# Sending it anyway pushed the model into motion everywhere, on every clip, and the
# founder saw the result before any measurement did (2026-08-02): "these all have a
# pattern of like, shaking alot, strangly". Those three terms are removed; every
# quality suppressor (bad hands, fused fingers, jpeg artifacts, overexposure) is
# kept, and explicit shake terms are added.
NEG = ("色调艳丽, 过曝, 细节模糊不清, 字幕, 风格, 作品, 画作, 整体发灰, "
       "最差质量, 低质量, JPEG压缩残留, 丑陋的, 残缺的, 多余的手指, 画得不好的手部, "
       "画得不好的脸部, 畸形的, 毁容的, 形态畸形的肢体, 手指融合, "
       "杂乱的背景, 三条腿, 背景人很多, 倒着走")
# OURS, added 2026-08-02: the founder on every motion.yaml clip — "these all have a
# pattern of like, shaking alot, strangly". Suppress the shake directly, in the
# field that acts on it.
#
# SEPARATE CONSTANT, and --no-shake-neg drops it, because these terms are now a
# SUSPECT. On 2026-08-03 the founder said beat 1 "basically doesnt move at all,
# literally", and applying the anti-static terms changed its measured motion by
# 1% (2.68 -> 2.64) — so anti-static is not the lever. These eight terms are the
# other thing we changed that day, and "vibrating, trembling camera, unstable"
# may be damping the hand motion we want along with the camera motion we do not.
# Untested either way, which is why it is a flag and not a deletion.
SHAKE_NEG = ("camera shake, handheld camera, jitter, wobble, unstable camera, "
             "vibrating, trembling camera, rolling shutter")


# ---------------------------------------------------------------------------
# BATCH THROUGHPUT PROBING. --batch N asks the pipeline for N clips from ONE
# sample call (diffusers' num_videos_per_prompt) so we can measure whether the
# card is step-bound or launch-bound. It is a MEASUREMENT flag, not a way to fill
# the queue faster: N clips share one prompt and one conditioning still and differ
# only by seed.
# ---------------------------------------------------------------------------
HOST_PEAK = {"phys_gb": None, "commit_gb": None}


def _host_peak_sampler(stop) -> None:
    """1s host-RAM peak sampling — psutil if present, silent nulls if not.

    NULLS RATHER THAN GUESSES. A bench row is read later as evidence, and the one
    thing that must never happen to it is a plausible number nobody measured
    (2026-08-04: two host-memory mechanisms reasoned out of our own code comments,
    both retracted). If psutil is not installed in this venv the two host fields
    stay None and the row says null.

    "commit" is physical + swap/pagefile in use, which is what psutil can see
    portably; it is the same quantity ltx_i2v reads exactly from
    GlobalMemoryStatusEx on Windows, not a different definition.
    """
    try:
        import psutil
    except Exception:                                        # noqa: BLE001
        print("psutil not installed — host RAM fields will be null", flush=True)
        return
    while not stop.wait(1.0):
        vm, sw = psutil.virtual_memory(), psutil.swap_memory()
        HOST_PEAK["phys_gb"] = max(HOST_PEAK["phys_gb"] or 0.0, vm.used / 1e9)
        HOST_PEAK["commit_gb"] = max(HOST_PEAK["commit_gb"] or 0.0,
                                     (vm.used + sw.used) / 1e9)


def _scheduler_shift(pipe):
    """The flow-match shift the sample actually ran under, or None.

    READ OFF THE OBJECT, never restated from a flag: one branch here constructs
    FlowMatchEulerDiscreteScheduler(shift=3.0) by hand and another inherits
    whatever the repo shipped, so a bench row that quoted a constant would be
    describing code rather than the run. Unreadable -> null.

    TWO KEYS, because the schedulers spell it differently and the one-key version
    of this function reported null for every 5B row it ever wrote. TI2V-5B ships
    UniPCMultistepScheduler, whose parameter is `flow_shift`; FlowMatchEuler's is
    `shift`. Measured, not assumed: bench-T1T2T3/bench-t0.json records the live
    5B scheduler_config as flow_shift 5.0 with no `shift` key at all, while every
    5B bench row from the same runs says "shift": null. `shift` is tried first so
    a scheduler that happens to carry both keeps the name it was constructed
    with. Still null when neither is readable — a guess in this column is worse
    than a gap.
    """
    cfg = getattr(getattr(pipe, "scheduler", None), "config", None)
    for key in ("shift", "flow_shift"):
        try:
            v = cfg.get(key)
        except Exception:                                    # noqa: BLE001
            return None
        if v is not None:
            return v
    return None


def _bench_mode(a) -> bool:
    """Is this run being MEASURED? Only then do the extra writes happen.

    The default path (--batch 1, no --bench-jsonl) must stay byte-for-byte what it
    was: it is the production path for every episode clip, it runs on a box this
    machine cannot test, and a throughput probe is not worth regressing it for.
    """
    return int(getattr(a, "batch", 1) or 1) > 1 or bool(getattr(a, "bench_jsonl", ""))


def _import_video_task():
    """Sidecar + bench-row helpers, imported ONLY on a measured run.

    Same lazy import ltx_i2v.py already uses. Kept out of the module top level
    because this script runs in the torch venv and the production path must not
    acquire a new import to fail on.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import video_task
    return video_task


def tile_vae(pipe) -> None:
    """Make the VAE process the frame in tiles instead of all at once.

    THE VAE IS THE OTHER MEMORY SPIKE, and it is not the transformer's problem.
    Wan's VAE runs in float32 while the transformer runs bf16 (or fp8 for
    AnimeGen), so a 704x1280 encode allocates in GiB regardless of how cleverly
    the transformer was packed. On 2026-08-03 AnimeGen died exactly there:

        torch.OutOfMemoryError: Tried to allocate 1.29 GiB. GPU 0 has a total
        capacity of 23.89 GiB of which 3.67 GiB is free.
        ... autoencoder_kl_wan._encode -> encoder -> norm1

    The transformer had loaded fine. The VAE encode of the init image had not.

    Extracted into a function because the bug was DIVERGENCE, not absence: the
    5B path called this and the AnimeGen path returned to _sample() before
    reaching it, so the two load paths had different memory discipline and only
    the untested one was wrong. One helper, called by both, is the fix that
    stays fixed.

    The helper's name and location move between diffusers versions and between
    pipelines, so reach for whichever exists rather than assuming.
    """
    for enable in (getattr(pipe, "enable_vae_tiling", None),
                   getattr(getattr(pipe, "vae", None), "enable_tiling", None)):
        if callable(enable):
            enable()
            print("VAE tiling enabled", flush=True)
            return
    for enable in (getattr(pipe, "enable_vae_slicing", None),
                   getattr(getattr(pipe, "vae", None), "enable_slicing", None)):
        if callable(enable):
            enable()
            print("VAE slicing enabled (no tiling available)", flush=True)
            return
    print("!! no VAE tiling or slicing available on this pipeline — a large "
          "frame may OOM in the VAE even with the transformer offloaded",
          flush=True)


def load_animegen(torch, a):
    """AnimeGen-I2V, following AIdeaLab's OWN recipe from their model card.

    Written after reading the card rather than guessing at it. My first attempt
    reached for bitsandbytes 8-bit quantisation; the authors instead use
    diffusers' built-in `enable_layerwise_casting` — fp8 storage, bf16 compute —
    which needs no extra dependency and is what makes a 27B model sit on a 24GB
    card. I had also recorded "80GB VRAM" as the blocker, which came from the BASE
    Wan A14B readme; AnimeGen's own card says "RTX 4090 or higher", i.e. 24GB.
    The model was never out of reach.

    BUT "24GB" IS NOT MUCH ROOM, AND I OVERSTATED THE MARGIN. The 5090 laptop
    reports 25.7 GB decimal = 23.89 GiB, and I told the founder that fit
    comfortably inside a 24 GB requirement. Those are different units: the card is
    at or just BELOW the stated figure, not above it. This is the same
    decimal-vs-binary carelessness as the "80GB" note above, one line up in the
    same docstring. On 2026-08-03 the first real attempt OOM'd — not in the
    transformer, which fp8 casting packed fine, but in the float32 VAE encoding a
    704x1280 init. Hence tile_vae() on this path too.

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

    def cast_fp8(tr) -> None:
        """fp8 storage / bf16 compute — the authors' own way of fitting 24GB."""
        tr.enable_layerwise_casting(storage_dtype=torch.float8_e4m3fn,
                                    compute_dtype=torch.bfloat16)
        # the bf16 storages this replaces are freed only once nothing holds them,
        # and a lower PEAK is the whole point of casting here — so collect now
        # rather than leaving ~16 GiB alive across the next from_pretrained()
        gc.collect()

    # LOAD ORDER IS A MEMORY DECISION. Both transformers used to be loaded in bf16
    # and only then cast, so the peak held two ~32 GiB experts at once — ~64 GiB of
    # host RAM, which on the then-31.4 GB rtx5090 laptop meant ~33 GB of hard
    # paging. That is the diagnosis for the 0xC0000005 access violation this path
    # died at three times (DIAG-20260804.md, and pipeline/farm-queue.yaml:43-60
    # which predicted the repeat and set this as the fix). Casting `hi` before `lo`
    # is loaded means only ONE expert is ever in bf16.
    #
    # THE 31.4 GB CEILING IS GONE — the box was upgraded on 2026-08-04 and now
    # measures 68.1 GB physical. The paragraph that used to sit here reasoned from
    # 31.4 GB to "AnimeGen stays parked on this machine class"; that arithmetic is
    # stale and has been removed rather than left to be quoted back at someone.
    # What the new RAM does NOT do is unpark AnimeGen, and the reason is
    # configuration, not capacity:
    #   - the reordered peak is ~48 GiB, not ~32 (fp8 `hi` ~16 + bf16 `lo` ~32).
    #     farm-queue.yaml's "~32 GiB" is the bf16 half of it, not the total.
    #   - cpu-offload then keeps ~38 GiB RESIDENT for the whole sample, and load
    #     order cannot touch a steady state. Both figures now FIT in 68.1 GB.
    #   - and it still died at step 0 on the 64 GB attempt, because the queue routes
    #     any card with >=20 GB VRAM (video_task.py:994, `big = gpu_vram_gb() >= 20`)
    #     into the single-process branch that keeps the ~11 GB text encoder resident
    #     alongside both experts. The configuration that WORKED evicted the encoder
    #     into its own process and freed 13.1 GB.
    # So the A14B park stands, on the single-process queue path rather than on host
    # RAM. Unparking is a change to that routing (or an fp8/GGUF build), measured —
    # not an inference from the new total.
    hi = WanTransformer3DModel.from_pretrained(a.model, subfolder="transformer",
                                              torch_dtype=torch.bfloat16)
    # ONLY THE no-LoRA PATH CAN CAST THIS EARLY, and the divergence is deliberate
    # rather than an oversight. peft creates lora_A/lora_B in the base layer's
    # dtype, so injecting an adapter into an already-cast transformer yields fp8
    # adapter weights with no upcasting hook on them, and the first matmul is a
    # bf16 x float8_e4m3fn dtype error. The pipeline-level loader below needs BOTH
    # transformers constructed, so with the LoRAs the old order and the old ~64 GiB
    # peak are the only correct ones. Untested against the real weights either way
    # — nothing here has run to completion yet.
    #
    # It lands on the right side: --no-lora is the PUBLISHABLE path (the Lightning
    # repo ships no LICENSE file, see above), so the memory win goes to the run we
    # are actually allowed to release footage from.
    if a.no_lora:
        cast_fp8(hi)
    lo = WanTransformer3DModel.from_pretrained(a.model, subfolder="transformer_2",
                                               torch_dtype=torch.bfloat16)
    if a.no_lora:
        cast_fp8(lo)
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
        for tr in (hi, lo):
            cast_fp8(tr)                 # AFTER the adapters — see the note above
    pipe.enable_model_cpu_offload()
    # the 5B path tiles the VAE after loading; this path used to return straight
    # into _sample() and never got it — see tile_vae()
    tile_vae(pipe)
    # say WHICH order ran: the two differ by ~16 GiB of peak host RAM, and a log
    # that does not name it cannot be used to explain an access violation
    order = ("cast per expert on load, one bf16 expert at a time" if a.no_lora
             else "cast after the LoRAs, both experts bf16 at peak")
    print(f"AnimeGen: fp8 layerwise casting ({order}) + cpu offload + VAE tiling",
          flush=True)
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
    # VRAM ACCOUNTING, printed before and after placement. 536s per clip works out
    # to 13.4s per forward pass for a 6240-token sequence — roughly 10x off what
    # this card should manage. The suspicion: the weights do not fit. Wan 2.2
    # TI2V-5B ships 34GB on disk (transformer 20GB fp32, text encoder 11.4GB, VAE
    # 2.8GB); at bf16 that is ~17GB resident on a 24GB card that is also driving a
    # Windows desktop. On Windows/WDDM the driver's default Sysmem Fallback Policy
    # PAGES TO HOST RAM over PCIe rather than raising OOM — a silent 10x slowdown
    # that looks identical to "this model is slow".
    # Measured, not assumed: if used stays near total, that is the answer.
    def vram(tag):
        if not torch.cuda.is_available():
            return
        free, total = torch.cuda.mem_get_info()
        alloc = torch.cuda.memory_allocated() / 1e9
        print(f"VRAM[{tag}] used {(total-free)/1e9:.2f}/{total/1e9:.1f}GB "
              f"(torch holds {alloc:.2f}GB)", flush=True)
    vram("after load, before .to(cuda)")
    # a quantised big model still will not sit entirely on 24GB; offload streams
    # modules through system RAM, which is slow but finishes
    if a.quantise != "none" or a.offload:
        pipe.enable_model_cpu_offload()
        print("model cpu offload ON (big model: slower per clip, but it fits)")
    else:
        pipe.to("cuda")
        vram("after .to(cuda)")
    # THE VAE DECODE IS A SEPARATE CEILING FROM THE WEIGHTS, and this path did not
    # tile it. `tile_vae()` was called by the AnimeGen loader (:328) and by
    # stage_render (:687) and by neither branch of stage_simple, so the divergence
    # the helper was extracted to end had quietly reopened on the 5B path — the
    # exact shape of the bug its own docstring describes.
    #
    # NOT measured — and saying so is the point. The 5070 Ti probe that was meant
    # to observe the untiled decode OOM was killed at denoise step 3 of 6 when the
    # box was unplugged to be carried to another room, so on 2026-08-05 the decode
    # peak on a 12GB card remains a PREDICTION (~14.4GB untiled against 12.82GB of
    # card, from Box A's own peak-torch figure for this recipe).
    #
    # This call is justified without it: the divergence is the bug. A 24GB card had
    # room to be wasteful and hid it, and tiling is the configuration a real episode
    # render uses either way, so the three load paths now agree instead of two of
    # them agreeing and the untested one being wrong.
    tile_vae(pipe)
    import inspect
    takes_image = "image" in inspect.signature(pipe.__call__).parameters
    if not takes_image:
        print("WARNING: this pipeline takes no image - text-to-video only")

    # THE TEXT ENCODER STAYS. Hand-passing pre-computed prompt_embeds to free its
    # 11.4GB took a clip from 536s to 66s — and produced glitching, character-
    # destroying output on every beat. Founder: "these 6 new beats are literally
    # just glitching the image".
    #
    # The tell was his other observation: 20 steps and 4 steps looked nearly
    # identical. When the step count stops mattering, conditioning is not driving
    # the denoise.
    #
    # AND THIS WAS ALREADY WRITTEN DOWN, fifty lines above, in stage_simple's own
    # docstring: "The first 5090 clip came out as abstract smears with no relation
    # to the conditioning image: the two-process trick (pre-computed embeddings...)
    # exists only to fit a 16GB machine, and one of its shortcuts was clearly
    # bypassing the image path... here the pipeline does its own encoding."
    #
    # stage_simple EXISTS because pre-computed embeddings break the image path. I
    # reintroduced the bug the function was created to avoid, in the function whose
    # docstring warns about it, and shipped an 8x speedup that ruined every frame.
    #
    # The VRAM finding is still real and worth acting on — 24.20/25.7GB resident,
    # measured, means we page to host RAM and run at ~5% of the card. But the fix
    # has to be one that leaves the pipeline's own conditioning path intact:
    # enable_model_cpu_offload() (diffusers' own, module-by-module) or a smaller
    # text encoder variant. Not this.
    # _sample loads the job list itself. It used to be passed in from here, because
    # the (now reverted) eviction needed every prompt up front — deleting that block
    # removed the line defining `jobs` and left this call still using it, so every
    # render died with NameError. Reverts have to be verified like anything else:
    # `git revert`-by-hand is a code change, and mine went out unexecuted.
    return _sample(pipe, a, w, h, frames, takes_image)


def _sample(pipe, a, w, h, frames, takes_image, jobs=None) -> int:
    """ONE process, MANY clips — shared by both model paths.

    Sampling is only a fraction of a clip's wall time; the rest was reloading the
    model from disk for every beat. Loading once and looping turned four clips
    from ~44 minutes into a bit over ten.
    """
    import torch
    from diffusers.utils import export_to_video
    from PIL import Image

    batch = max(1, int(getattr(a, "batch", 1) or 1))
    bench = _bench_mode(a)
    video_task = _import_video_task() if bench else None
    short = next((k for k, v in MODELS.items() if v == a.model), a.model)
    label = a.bench_label or short
    # WAN 2.1-STYLE IMAGE CONDITIONING IS NOT BATCH-SAFE ON THIS DIFFUSERS, and the
    # failure would be a wrong clip rather than a crash. pipeline_wan_i2v.py:701
    # does `image_embeds = image_embeds.repeat(batch_size, 1, 1)` using batch_size,
    # NOT batch_size * num_videos_per_prompt — so a CLIP-conditioned transformer
    # (config.image_dim set, i.e. Wan 2.1 I2V) gets one image embedding against N
    # latents. Wan 2.2 leaves image_dim None and skips that branch entirely, which
    # is why both curated models are fine; --model also takes arbitrary repo ids,
    # so refuse instead of finding out in the footage.
    if batch > 1:
        for name in ("transformer", "transformer_2"):
            cfg = getattr(getattr(pipe, name, None), "config", None)
            if getattr(cfg, "image_dim", None) is not None:
                print(f"!! {a.model} conditions on CLIP image embeddings "
                      f"({name}.config.image_dim is set). diffusers 0.39.0 repeats "
                      f"those by batch_size and not by the effective batch "
                      f"(pipeline_wan_i2v.py:701), so --batch {batch} would render "
                      f"N clips off ONE image embedding. Refusing.", flush=True)
                return 2
    if jobs is None:
        jobs = json.loads(Path(a.jobs).read_text()) if a.jobs else \
            [{"init": a.init, "out": a.out, "prompt": a.prompt, "seed": a.seed,
              "negative": a.negative}]
    for i, job in enumerate(jobs, 1):
        t0 = time.time()
        img = Image.open(job["init"]).convert("RGB").resize((w, h), Image.LANCZOS)
        # per-job negative: the beat's own "No person, no ghost…" clauses, moved
        # out of the positive prompt where they were being read as REQUESTS
        base = NEG if a.no_shake_neg else f"{NEG}, {SHAKE_NEG}"
        neg = f"{base}, {job['negative']}" if job.get("negative") else base
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
        seed = int(job["seed"])
        # ONE GENERATOR PER SLOT, and slot 0 keeps the base seed so a batched run
        # can be diffed against the un-batched clip of the same recipe — that is
        # the fidelity check the whole probe rests on. diffusers validates the list
        # length against the effective batch and draws each slot separately
        # (pipeline_wan_i2v.py:412-419, torch_utils.randn_tensor's list branch).
        #
        # A BARE GENERATOR AT batch == 1, not a one-element list: randn_tensor
        # unwraps a length-1 list to exactly this ("make sure generator list of
        # length 1 is treated like a non-list"), but prepare_latents ALSO branches
        # on isinstance(generator, list) one level up (:449-456), and the default
        # path is production. Identical by construction beats identical by argument.
        gens = ([torch.Generator(device="cpu").manual_seed(seed + s)
                 for s in range(batch)] if batch > 1
                else torch.Generator(device="cpu").manual_seed(seed))
        # ALWAYS the pipeline's own prompt path. Never hand-pass prompt_embeds —
        # it silently bypasses the image conditioning and glitches every frame
        # (2026-08-02, and 2026-07-31 before that; see stage_simple's docstring).
        #
        # Because the prompt IS a string here, num_videos_per_prompt does its whole
        # job: encode_prompt runs the text path and _get_t5_prompt_embeds repeats
        # the embeddings to the effective batch (pipeline_wan_i2v.py:235-236), and
        # prepare_latents is asked for batch_size * num_videos_per_prompt (:718).
        # stage_render, which supplies embeddings, does NOT get this for free — see
        # the note there.
        kw = dict(prompt=prompt, negative_prompt=neg, height=h, width=w,
                  num_frames=frames, num_inference_steps=steps,
                  guidance_scale=guidance, num_videos_per_prompt=batch,
                  generator=gens)
        if takes_image:
            kw["image"] = img
        out = pipe(**kw).frames
        sample_s = time.time() - t0
        peak = (torch.cuda.max_memory_allocated() / 1e9
                if torch.cuda.is_available() else 0)
        free, total = (torch.cuda.mem_get_info() if torch.cuda.is_available() else (0, 1))
        clip_s = frames / a.fps
        for s in range(batch):
            path = video_task.slot_out_path(job["out"], seed, s, batch) if bench \
                else job["out"]
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            export_to_video(out[s], path, fps=a.fps)
            # the [i/N] shape is video_task's PROGRESS regex and bench_models' WROTE
            # regex; the per-slot suffix goes AFTER the part they parse. The elapsed
            # figure is the whole sample call, repeated on each slot line, because
            # no per-slot time exists — the N clips were denoised together.
            print(f"[{i}/{len(jobs)}] wrote {path} in {sample_s:.0f}s "
                  f"({frames} frames, {w}x{h}, {steps} steps, "
                  f"peak torch {peak:.1f}GB, "
                  f"device {(total-free)/1e9:.1f}/{total/1e9:.0f}GB"
                  + (f", slot {s+1}/{batch} seed {seed + s})" if batch > 1 else ")"),
                  flush=True)
            if bench:
                video_task.write_sidecar(
                    path, short, {"worker": platform.node() or "unknown",
                                  "guidance": guidance, "seed_base": seed + s,
                                  "id": f"{label}/{a.mode}/b{batch}/s{seed + s}"},
                    beat=0, seconds=round(clip_s, 3), steps=steps,
                    size=f"{w}x{h}", prompt=prompt, negative=neg,
                    extra={"mode": a.mode, "batch": batch, "batch_slot": s,
                           "throughput_s_video_per_s_wall":
                               round(batch * clip_s / sample_s, 4),
                           "compute_s_per_video_s":
                               round(sample_s / batch / clip_s, 1)})
        # (N clips of video) / (one wall-clock sample). The number the probe exists
        # to produce: if it does not rise with N, the card is step-bound and
        # batching buys nothing.
        print(f"THROUGHPUT {batch * clip_s / sample_s:.4f} s(video)/s(wall) "
              f"({batch} x {clip_s:.3f}s of video in {sample_s:.0f}s)", flush=True)
        if bench and a.bench_jsonl:
            # ONE ROW PER SAMPLE CALL, not per slot: the measurement is the call.
            video_task.append_bench_row(a.bench_jsonl, video_task.bench_row(
                label=label, repo=a.model, mode=a.mode, batch=batch, frames=frames,
                seeds=[seed + s for s in range(batch)],
                sample_s=round(sample_s, 1), s_per_step=round(sample_s / steps, 2),
                video_s=round(batch * clip_s, 3),
                throughput_s_per_s=round(batch * clip_s / sample_s, 4),
                # PER SECOND OF VIDEO, which is what the column is called and what
                # the sidecar three lines above already wrote. This said
                # `sample_s / batch` until 2026-08-05 — seconds per CLIP — so the
                # 5B b2 row went to disk saying 382.3 while its own sidecar said
                # 150.4 for the same run, under a page header reading "s per 1s
                # video". Two true numbers, one of them answering a question
                # nobody asked in that column. The rows already written keep their
                # figures (they are measurements, not to be edited); the page
                # derives this cell from sample_s and video_s so old and new rows
                # read alike.
                compute_per_video_s=round(sample_s / batch / clip_s, 1),
                peak_torch_gb=round(peak, 1),
                device_gb=round((total - free) / 1e9, 1),
                device_total_gb=round(total / 1e9, 1),
                host_peak_phys_gb=(round(HOST_PEAK["phys_gb"], 1)
                                   if HOST_PEAK["phys_gb"] else None),
                host_peak_commit_gb=(round(HOST_PEAK["commit_gb"], 1)
                                     if HOST_PEAK["commit_gb"] else None),
                steps=steps, guidance=guidance, shift=_scheduler_shift(pipe),
                size=f"{w}x{h}", ok=True))
        # FREE THE CARD BETWEEN CLIPS. Measured across three batches on
        # 2026-08-02: clip 1 of 5 finished in ~440s every time, and clip 2 NEVER
        # finished — each batch stalled ~46 minutes until the watchdog killed it.
        # peak torch was 22.9GB of a 25.7GB card, so after one clip the caching
        # allocator holds nearly the whole GPU, clip 2 has no headroom, and Windows
        # pages it to host RAM instead of failing. Same signature as the eight-hour
        # stall on 2026-08-01, and the reason single-beat tasks always worked: a
        # fresh process frees everything on exit.
        #
        # `out` holds the decoded frames — hundreds of megabytes of tensors — and
        # stayed referenced through the next iteration.
        del out
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            free, total = torch.cuda.mem_get_info()
            print(f"    freed between clips: {(total-free)/1e9:.1f}/{total/1e9:.0f}GB "
                  f"still held", flush=True)
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
    bench = _bench_mode(a)
    video_task = _import_video_task() if bench else None
    short = next((k for k, v in MODELS.items() if v == a.model), a.model)
    label = a.bench_label or short

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
    tile_vae(pipe)
    gc.collect()

    # embeddings arrive from the encode process on CPU, but cpu-offload runs
    # the transformer on the GPU and does not move caller-supplied tensors
    # ("mat1 is on cpu, different from other tensors on cuda:0") — they are
    # small, so hand them over on the execution device
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    img = Image.open(a.init).convert("RGB").resize((w, h), Image.LANCZOS)
    batch = max(1, int(getattr(a, "batch", 1) or 1))
    pe, ne = e["prompt_embeds"].to(dev), e["negative_prompt_embeds"].to(dev)
    # DIFFUSERS DOES NOT EXPAND EMBEDDINGS YOU HAND IT — this is the silent-wrong
    # failure the whole batch change had to be researched around, and it bites
    # exactly here because this stage supplies prompt_embeds instead of a string.
    # encode_prompt guards the entire text path behind `if prompt_embeds is None:`
    # (diffusers 0.39.0 pipeline_wan_i2v.py:297), so num_videos_per_prompt never
    # reaches the repeat at :235-236 and the embeddings stay batch 1 while
    # prepare_latents is sized batch_size * num_videos_per_prompt (:718).
    #
    # Expand them HERE and leave num_videos_per_prompt at its default 1. Not both:
    # batch_size is read off prompt_embeds.shape[0] (:674), so expanding to N and
    # also asking for N videos per prompt would request N*N clips. Expanding is
    # also what makes :701 correct — image_embeds.repeat(batch_size, ...) matches
    # the latents only when batch_size is already the effective batch.
    if batch > 1:
        pe, ne = pe.repeat_interleave(batch, dim=0), ne.repeat_interleave(batch, dim=0)
    gens = ([torch.Generator(device="cpu").manual_seed(a.seed + s)
             for s in range(batch)] if batch > 1
            else torch.Generator(device="cpu").manual_seed(a.seed))
    t0 = time.time()
    out = pipe(
        image=img,
        prompt_embeds=pe,
        negative_prompt_embeds=ne,
        height=h, width=w, num_frames=frames,
        num_inference_steps=a.steps,
        # was hardcoded 5.0, ignoring --guidance entirely. A flag the caller
        # is allowed to set must not be quietly overridden by a literal.
        guidance_scale=a.guidance,
        generator=gens,
    ).frames
    sample_s = time.time() - t0

    clip_s = frames / a.fps
    for s in range(batch):
        path = video_task.slot_out_path(a.out, a.seed, s, batch) if bench else a.out
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        export_to_video(out[s], path, fps=a.fps)
        print(f"wrote {path} ({frames} frames, {w}x{h}"
              + (f", slot {s+1}/{batch} seed {a.seed + s})" if batch > 1 else ")"))
        if bench:
            video_task.write_sidecar(
                path, short, {"worker": platform.node() or "unknown",
                              "guidance": a.guidance, "seed_base": a.seed + s,
                              "id": f"{label}/{a.mode}/b{batch}/s{a.seed + s}"},
                beat=0, seconds=round(clip_s, 3), steps=a.steps,
                size=f"{w}x{h}", prompt=a.prompt, negative=a.negative,
                extra={"mode": a.mode, "batch": batch, "batch_slot": s,
                       "throughput_s_video_per_s_wall":
                           round(batch * clip_s / sample_s, 4),
                       "compute_s_per_video_s": round(sample_s / batch / clip_s, 1)})
    print(f"THROUGHPUT {batch * clip_s / sample_s:.4f} s(video)/s(wall) "
          f"({batch} x {clip_s:.3f}s of video in {sample_s:.0f}s)", flush=True)
    if bench and a.bench_jsonl:
        peak = (torch.cuda.max_memory_allocated() / 1e9
                if torch.cuda.is_available() else 0)
        free, total = (torch.cuda.mem_get_info() if torch.cuda.is_available() else (0, 1))
        video_task.append_bench_row(a.bench_jsonl, video_task.bench_row(
            label=label, repo=a.model, mode=a.mode, batch=batch, frames=frames,
            seeds=[a.seed + s for s in range(batch)],
            sample_s=round(sample_s, 1), s_per_step=round(sample_s / a.steps, 2),
            video_s=round(batch * clip_s, 3),
            throughput_s_per_s=round(batch * clip_s / sample_s, 4),
            # per SECOND OF VIDEO — see the note at the stage_simple call site.
            compute_per_video_s=round(sample_s / batch / clip_s, 1),
            peak_torch_gb=round(peak, 1),
            device_gb=round((total - free) / 1e9, 1),
            device_total_gb=round(total / 1e9, 1),
            host_peak_phys_gb=(round(HOST_PEAK["phys_gb"], 1)
                               if HOST_PEAK["phys_gb"] else None),
            host_peak_commit_gb=(round(HOST_PEAK["commit_gb"], 1)
                                 if HOST_PEAK["commit_gb"] else None),
            steps=a.steps, guidance=a.guidance, shift=_scheduler_shift(pipe),
            size=f"{w}x{h}", ok=True))
    return 0


def gpu_busy() -> str:
    """Another render already on this GPU? Returns a human sentence, or "".

    The single-instance lock guards WORKER against WORKER. It does nothing about a
    human running this script directly while a worker is running — which is
    exactly what happened on 2026-08-01: a hand-run AnimeGen diagnostic and a
    worker retrying the same task, two 27B loads aimed at one 24GB card. The
    contention that cost four hours in the morning, reappearing through the door
    the lock does not cover.

    Checked here, in the renderer, because this is the one place BOTH routes pass
    through. Advisory rather than fatal: a deliberate second render is the user's
    call, and refusing outright would break the very diagnostic that found this.
    """
    try:
        import torch
        if not torch.cuda.is_available():
            return ""
        free, total = torch.cuda.mem_get_info()
        used_gb = (total - free) / 1e9
        if used_gb > 2.0:
            return (f"{used_gb:.1f}GB of {total/1e9:.0f}GB VRAM is ALREADY IN USE "
                    f"before we load anything — another render is probably running. "
                    f"Two big models on one card will OOM or halve each other's "
                    f"speed. Close the other one unless this is deliberate.")
    except Exception:                                    # noqa: BLE001
        pass
    return ""


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
    # --keep-text-encoder REMOVED 2026-08-03. It was declared here, plumbed
    # through video_task, and READ NOWHERE — a leftover of the reverted eviction
    # experiment. A flag that looks like a control and silently does nothing is
    # worse than no flag: I nearly reached for it to fix AnimeGen's host-RAM
    # ceiling. There is no eviction to keep or skip any more; the pipeline always
    # uses its own prompt path.
    ap.add_argument("--no-shake-neg", action="store_true",
                    help="drop OUR shake-suppression terms (SHAKE_NEG). The A/B for "
                         "whether they are damping wanted motion — beat 1 measured "
                         "'basically doesnt move at all' with them on")
    ap.add_argument("--negative", default="",
                    help="extra negative terms (the beat's own 'no X' clauses)")
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
    # --- throughput probing. Default 1 = the path that has always run. -------
    ap.add_argument("--batch", type=int, default=1,
                    help="clips per sample call (diffusers num_videos_per_prompt). "
                         "A MEASUREMENT, not a queue filler: the N clips share one "
                         "prompt and one still and differ only by seed (base seed "
                         "for slot 0, +1 per slot after)")
    ap.add_argument("--mode", default="production",
                    help="recipe label recorded in the sidecar and the bench row; "
                         "the 2026-08-04 rows use preview|production")
    ap.add_argument("--bench-jsonl", default="",
                    help="append ONE measurement row per sample call to this file")
    ap.add_argument("--bench-label", default="",
                    help="'label' column for --bench-jsonl (default: the short "
                         "model name)")
    a = ap.parse_args()
    if a.batch < 1:
        print(f"!! --batch {a.batch}: must be at least 1", flush=True)
        return 2
    # short name -> repo id; anything unrecognised is passed through as a repo id
    # so a one-off experiment does not need a code change, but the CURATED names
    # are the ones whose licence we have actually read.
    a.model = MODELS.get(a.model, a.model)
    print(f"model: {a.model}", flush=True)
    busy = gpu_busy()
    if busy:
        print(f"!! {busy}", flush=True)
    if a.stage == "encode":
        return stage_encode(a)
    # The host-RAM sampler runs ONLY on a measured run. It is a daemon thread doing
    # a psutil read a second, which is cheap — but the production render path does
    # not need it, and not starting it is one fewer thing that can be blamed for a
    # 0xC0000005 on a box this machine cannot test.
    stop = threading.Event()
    if _bench_mode(a):
        threading.Thread(target=_host_peak_sampler, args=(stop,),
                         daemon=True).start()
    try:
        return stage_simple(a) if a.stage == "simple" else stage_render(a)
    finally:
        stop.set()


if __name__ == "__main__":
    sys.exit(main())
