"""LTX-2.3 distilled image-to-video, bf16 — the D16(c) one-sample bench.

Was written for the fp8 build and re-pointed at the bf16 distilled weights on
2026-08-04 after the fp8 route was measured to be unloadable on diffusers 0.39.0
(see WHAT THE fp8 FILE ACTUALLY IS below). The fp8 path survives behind
--fp8-single-file for a future quantised backend and refuses on this one.

Same shape as wan_i2v.py on purpose: a `--stage encode` / `--stage render` split,
a §7.2 sidecar beside the clip, and the peak line printed in the identical format
so bench parsing and the Wan comparison row keep working.

WHY THE SPLIT IS NOT OPTIONAL, now measured rather than assumed. The pieces are a
24.4GB Gemma-3 text encoder and a 29.5GB fp8 transformer. The box was upgraded to
64GiB on 2026-08-04 (measured: 68.1GB phys, 130.4GB commit limit), which looked
like enough to stop bothering — but the encode stage RUN on that box peaks at
37.0GB physical / 40.7GB commit, because Gemma is asked for all 49 hidden-state
layers at once. 37.0GB of encoder plus ~44GB of transformer, connectors and vae is
~81GB against 68GB. So the split still is what makes this fit, on 64GiB as much as
on 32. It costs one process start and 88 seconds.
The installed pipeline source says encode_prompt reaches only _get_gemma_prompt_embeds
— NOT connectors, not the transformer — so encoding in its own process and letting
it exit frees the whole encoder before any transformer weight is read. Verified by
reading diffusers 0.39.0's pipeline_ltx2_image2video.py on the box, not from docs.

THE MODEL IS ASSEMBLED FROM THREE SOURCES, because no single repo has it all:
  transformer  ltx-2.3-22b-distilled-fp8.safetensors, one file  (Lightricks/LTX-2.3-fp8)
  text encoder Lightricks/gemma-3-12b-it-qat-q4_0-unquantized  (ungated mirror,
               bf16, standing in for the 48.75GB fp32 copy in the diffusers repo)
  the rest     diffusers/LTX-2.3-Diffusers subfolders — vae, connectors, vocoder,
               audio_vae, scheduler, processor. `connectors` is 12.7GB and is NOT
               optional: LTX2Pipeline lists eight components and __call__ calls it.

WHAT THE fp8 FILE ACTUALLY IS, measured from its safetensors header on 2026-08-04
(readable from the partial blob, since the header sits at offset 0):
  8871 tensors — 4195 BF16, 3214 F32, only 1462 F8_E4M3 (16.62GB of the 29.53GB)
  __metadata__._quantization_metadata names those 1462 layers, each {"format":
  "float8_e4m3fn"}, and the file ships a per-tensor `weight_scale` AND `input_scale`
  F32 scalar for every one of them. It is a statically-quantised checkpoint: the
  real weight is fp8_weight * weight_scale.
DIFFUSERS 0.39.0 CANNOT HONOUR THAT, and fails in the quiet direction. Its
convert_ltx2_transformer_to_diffusers is 71 lines that mention neither scale nor
quantisation, so all 2924 scale tensors come out as `unexpected_keys` — which
single_file_model.py line 284 only WARNS about. Then line 294 does
model.to(torch_dtype). So:
  torch_dtype=float8_e4m3fn -> every param becomes fp8, norms included, and the
      first denoise step raises "mat1 and mat2 must have the same dtype" (verified
      on a 1-layer toy model built from this repo's own transformer config)
  torch_dtype=bfloat16      -> loads and RUNS, silently, with every weight_scale
      discarded. That is garbage output wearing a clean exit, and it would be easy
      to misread as the known green/grayscale issue rather than as dropped scales.
Making this checkpoint work means dequantising on load (fp8 * weight_scale -> bf16,
~46GB resident) or an fp8 GEMM path via torch._scaled_mm; no quantisation backend
is installed in the box venv (no torchao/bitsandbytes/gguf/quanto). Both are recipe
changes, not fixes, so neither is done here.

Licence: LTX-2 Community License Agreement, D16 — CANDIDATE under watch-only, and
the sidecar says so via video_task.MODEL_LICENCE["ltx23-distilled"] (the fp8 key is
kept for the archived partial). Same document either way: Lightricks/LTX-2.3's
LICENSE is 21393 chars and is that Agreement, byte-length identical to the copy
embedded in the fp8 file's own header. licence_gate still refuses to publish an LTX
clip until the founder signs off on the screened look; this script renders a bench
sample, it does not clear anything.
"""
import argparse
import ctypes
import gc
import json
import sys
import threading
import time
from pathlib import Path


class _MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


# HOST RAM WAS THE EXPECTED FAILURE MODE, so it is instrumented rather than
# guessed at afterwards. ~44GB of weights (transformer 29.5 + connectors 12.7 +
# vae 1.45) met 31.4GB of physical RAM; after the 2026-08-04 upgrade to 68.1GB it
# should fit, which makes this the measurement that CONFIRMS the headroom instead
# of the post-mortem. Either way the number that matters if it dies is peak COMMIT
# CHARGE — physical plus pagefile — and the stage it died in.
# torch.cuda.max_memory_allocated says nothing about either.
PEAK = {"commit_gb": 0.0, "phys_gb": 0.0, "stage": "start"}


def _mem() -> dict:
    if not hasattr(ctypes, "windll"):
        return {}
    m = _MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(m)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return {"phys_gb": (m.ullTotalPhys - m.ullAvailPhys) / 1e9,
            "phys_total_gb": m.ullTotalPhys / 1e9,
            "commit_gb": (m.ullTotalPageFile - m.ullAvailPageFile) / 1e9,
            "commit_total_gb": m.ullTotalPageFile / 1e9,
            "load_pct": m.dwMemoryLoad}


def _sampler(stop):
    """1s sampling: a crash gives no chance to read memory on the way out."""
    while not stop.wait(1.0):
        m = _mem()
        if m:
            PEAK["commit_gb"] = max(PEAK["commit_gb"], m["commit_gb"])
            PEAK["phys_gb"] = max(PEAK["phys_gb"], m["phys_gb"])


def mark(stage: str):
    """Name the stage BEFORE entering it, so a hard kill still localises."""
    PEAK["stage"] = stage
    m = _mem()
    if m:
        print(f"-- {stage}: phys {m['phys_gb']:.1f}/{m['phys_total_gb']:.1f}GB, "
              f"commit {m['commit_gb']:.1f}/{m['commit_total_gb']:.1f}GB "
              f"(load {m['load_pct']}%)", flush=True)
    else:
        print(f"-- {stage}", flush=True)


# ---------------------------------------------------------------------------
# BATCH THROUGHPUT PROBING — wan_i2v.py's flag, with wan_i2v.py's meaning.
# --batch N asks the pipeline for N clips from ONE sample call so we can measure
# whether the card is step-bound or launch-bound. It is a MEASUREMENT, not a way
# to fill the queue: the N clips share one prompt and one conditioning still and
# differ only by seed.
#
# THE BODY OF IT LANDED WITHOUT THE FLAGS (fab4632, 2026-08-04). `batch =
# max(1, int(a.batch))` shipped against an argparse that never declared --batch,
# so every `--stage render` raised AttributeError before a single weight was
# loaded — the LTX renderer could not render AT ALL, including at its defaults.
# Nothing caught it: py_compile passes, no test touched this CLI, and the box it
# runs on is not this machine. test_pipeline's
# test_argparse_declares_every_flag_it_reads is the cheap static gate for that
# whole class, and it fails against fab4632's copy of this file.
# ---------------------------------------------------------------------------


def _scheduler_shift(pipe):
    """The flow-match shift the sample actually ran under, or None.

    READ OFF THE OBJECT, never restated from a flag — same rule and same two keys
    as wan_i2v._scheduler_shift. `shift` is FlowMatchEulerDiscreteScheduler's
    name for it; `flow_shift` is UniPC's. Unreadable -> null, because a bench row
    that carries a plausible unmeasured number is how the 2026-08-04 retraction
    happened.
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


FP8_REPO = "Lightricks/LTX-2.3-fp8"
FP8_FILE = "ltx-2.3-22b-distilled-fp8.safetensors"
GEMMA_REPO = "Lightricks/gemma-3-12b-it-qat-q4_0-unquantized"
PARTS_REPO = "diffusers/LTX-2.3-Diffusers"
# The DISTILLED diffusers repo, which is what makes the approved 8-step recipe
# legitimate. PARTS_REPO is the BASE model — its own card gives 30 steps / CFG 3.0
# and points here for "a distilled variant (8 steps, CFG=1)". Same architecture
# (identical transformer/config.json), same licence document, different weights.
DIST_REPO = "diffusers/LTX-2.3-Distilled-Diffusers"
# The 2x spatial LATENT upsampler that sits between the two distilled stages. Raw
# Lightricks checkpoint (bf16, 72 tensors, 497.9M params) living in the
# Lightricks/LTX-2.3 repo, not a diffusers-format subfolder — so it is loaded by
# hand below rather than with from_pretrained.
UPSCALER_REPO = "Lightricks/LTX-2.3"
UPSCALER_FILE = "ltx-2.3-spatial-upscaler-x2-1.1.safetensors"


def _load_upsampler():
    """LTX2LatentUpsamplerModel from the raw upstream checkpoint.

    from_single_file is False for this class, so there is no registered conversion
    function — but none is needed. The checkpoint's own __metadata__["config"]
    describes the model, and once its two upstream parameter names are translated
    (spatial_scale -> rational_spatial_scale, rational_resampler ->
    use_rational_resampler) the 72 keys match the class's state_dict EXACTLY, with
    zero shape mismatches. Verified before this was written; if a future checkpoint
    revision breaks that, load_state_dict raises rather than silently half-loading.
    """
    import json
    import struct

    import torch
    from safetensors.torch import load_file

    from diffusers.pipelines.ltx2 import LTX2LatentUpsamplerModel

    path = _local(UPSCALER_REPO, UPSCALER_FILE)
    # safetensors header: 8-byte little-endian length, then that many bytes of json
    with open(path, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        hdr = json.loads(fh.read(n))
    cfg = json.loads(hdr["__metadata__"]["config"])
    model = LTX2LatentUpsamplerModel(
        in_channels=cfg["in_channels"], mid_channels=cfg["mid_channels"],
        num_blocks_per_stage=cfg["num_blocks_per_stage"], dims=cfg["dims"],
        spatial_upsample=cfg["spatial_upsample"],
        temporal_upsample=cfg["temporal_upsample"],
        rational_spatial_scale=cfg.get("spatial_scale", 2.0),
        use_rational_resampler=cfg.get("rational_resampler", False))
    model.load_state_dict(load_file(path))
    return model.to(torch.bfloat16).eval()


def _crf_roundtrip(src: str, crf: int, out_dir: str) -> str:
    """Round-trip the conditioning still through libx264 at `crf`, as upstream does.

    media_io.load_image_and_preprocess encodes and decodes the still through x264 at
    DEFAULT_IMAGE_CRF=33 before it is VAE-encoded, deliberately, to match the
    compressed frames the model saw in training — a clean PNG is out of
    distribution by their own reckoning. crf=0 bypasses it upstream, and 0 here
    means "don't".

    ffmpeg comes from imageio-ffmpeg's bundled binary (nothing is on PATH on this
    box), which does carry libx264.
    """
    import subprocess

    import imageio_ffmpeg

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    mid = str(Path(out_dir) / "cond-crf.mp4")
    png = str(Path(out_dir) / "cond-crf.png")
    # -frames:v 1 both ways: one frame in, one frame out. yuv420p because that is
    # what their encoder writes, and the chroma subsampling is part of the domain
    # match, not an accident of the container.
    for cmd in ([ff, "-y", "-loglevel", "error", "-i", src, "-frames:v", "1",
                 "-c:v", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p", mid],
                [ff, "-y", "-loglevel", "error", "-i", mid, "-frames:v", "1", png]):
        subprocess.run(cmd, check=True, capture_output=True)
    print(f"conditioning still round-tripped through libx264 crf={crf} -> {png}",
          flush=True)
    return png


def _local(repo, filename=None):
    """Resolve an already-cached repo/file. local_files_only: this script must
    never start a 24GB download as a side effect of a typo in a repo id."""
    from huggingface_hub import hf_hub_download, snapshot_download
    if filename:
        return hf_hub_download(repo, filename, local_files_only=True)
    return snapshot_download(repo, local_files_only=True)


def _local_dir(repo, probe="model_index.json"):
    """Snapshot directory of a repo we only ever fetched PART of.

    snapshot_download(local_files_only=True) cannot be used for PARTS_REPO and
    that is not a cache problem, it is the design: the components fetch pulls
    vae/connectors/vocoder/audio_vae/scheduler/processor/tokenizer and the json
    files, and deliberately skips text_encoder/ (48.75GB of fp32 the gemma mirror
    stands in for) and transformer/ (37.99GB bf16 the fp8 file stands in for). Hub
    counts those as missing — measured: "IncompleteSnapshotError: 21 file(s) are
    missing" — and refuses to hand back a path at all.

    Resolving ONE file we know we asked for and taking its parent gives the same
    snapshot directory without asserting the snapshot is whole. from_pretrained
    with subfolder= only ever reads the subfolders, so completeness of the rest is
    not the loader's business. Still local_files_only: no download can start here.
    """
    from huggingface_hub import hf_hub_download
    return str(Path(hf_hub_download(repo, probe, local_files_only=True)).parent)


def stage_encode(a) -> int:
    """Gemma ONLY: prompt in, embeddings on disk, process exits.

    The pipeline is built with every other component None. That is the same trick
    wan_i2v.py uses, and it is what keeps 24.4GB and 29.5GB from ever being
    resident together.
    """
    import torch
    from diffusers import LTX2ImageToVideoPipeline
    from transformers import AutoProcessor, AutoTokenizer, Gemma3ForConditionalGeneration

    gemma = _local(GEMMA_REPO)
    print(f"loading text encoder from {gemma}", flush=True)
    text_encoder = Gemma3ForConditionalGeneration.from_pretrained(
        gemma, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True)
    tokenizer = AutoTokenizer.from_pretrained(gemma)
    try:
        processor = AutoProcessor.from_pretrained(gemma)
    except Exception as e:                      # processor is Optional in __init__
        print(f"no processor ({type(e).__name__}) - continuing without", flush=True)
        processor = None

    pipe = LTX2ImageToVideoPipeline(
        scheduler=None, vae=None, audio_vae=None, text_encoder=text_encoder,
        tokenizer=tokenizer, connectors=None, transformer=None, vocoder=None,
        processor=processor)

    with torch.no_grad():
        pos, pos_mask, neg, neg_mask = pipe.encode_prompt(
            prompt=a.prompt, negative_prompt=a.negative,
            do_classifier_free_guidance=True, device="cpu")
    torch.save({"prompt_embeds": pos.to(torch.bfloat16),
                "prompt_attention_mask": pos_mask,
                "negative_prompt_embeds": neg.to(torch.bfloat16),
                "negative_prompt_attention_mask": neg_mask}, a.embeds)
    print(f"encoded to {a.embeds} {tuple(pos.shape)}", flush=True)
    return 0


def stage_render(a) -> int:
    """Everything except the text encoder, fed pre-computed embeddings."""
    import torch
    from diffusers import (AutoencoderKLLTX2Audio, AutoencoderKLLTX2Video,
                           FlowMatchEulerDiscreteScheduler,
                           LTX2ImageToVideoPipeline, LTX2VideoTransformer3DModel)
    from diffusers.pipelines.ltx2.connectors import LTX2TextConnectors
    from diffusers.pipelines.ltx2.vocoder import LTX2VocoderWithBWE
    from diffusers.utils import load_image

    w, h = (int(x) for x in a.size.split("x"))
    if w % 32 or h % 32:
        print(f"!! {a.size}: LTX requires both dimensions divisible by 32")
        return 2
    if (a.frames - 1) % 8:
        print(f"!! {a.frames} frames: LTX requires frames divisible by 8 plus 1")
        return 2

    # THREE snapshots, and which piece comes from which is deliberate:
    #   dist  transformer + scheduler — the DISTILLED weights and, critically, the
    #         distilled schedule. Its scheduler_config is one of only two files that
    #         differ from the base repo: base has use_dynamic_shifting True and
    #         shift_terminal 0.1, distilled has False and null. Loading the base
    #         scheduler would re-map DISTILLED_SIGMA_VALUES and quietly undo the
    #         distillation — an 8-step render that is not the 8-step recipe.
    #   parts vae, audio_vae, connectors, vocoder. NOT re-downloaded from the
    #         distilled repo because they are the same bytes: 40 of the 42 shared
    #         files match on size AND lfs sha256, the exceptions being README.md and
    #         that scheduler config. transformer/config.json is identical between the
    #         two repos (0 differing keys, num_layers 48 both), so these fit. That
    #         reuse saves a second 14.59GB pull.
    parts = _local_dir(PARTS_REPO)
    dist = _local_dir(DIST_REPO)
    print(f"transformer  {dist} [subfolder=transformer, bf16]", flush=True)
    print(f"scheduler    {dist} [subfolder=scheduler, distilled]", flush=True)
    print(f"other parts  {parts}", flush=True)

    if a.fp8_single_file:
        return _fp8_transformer_is_unsupported()

    # bf16, from the stock diffusers path. See the module docstring for why the fp8
    # single-file route was abandoned: that checkpoint carries per-tensor
    # weight_scale/input_scale that diffusers 0.39.0's LTX2 converter drops without
    # error, so it either crashes on a dtype mismatch or renders silently wrong.
    # This is the official distilled checkpoint loaded the ordinary way, which is
    # what keeps a screened clip attributable to the MODEL rather than to our maths.
    mark("load-transformer-bf16-38GB")
    transformer = LTX2VideoTransformer3DModel.from_pretrained(
        dist, subfolder="transformer", torch_dtype=torch.bfloat16,
        local_files_only=True)
    return _render_with(a, transformer, parts, dist, w, h)


def _fp8_transformer_is_unsupported() -> int:
    print("!! --fp8-single-file is retained for a future quantisation backend and "
          "does NOT work on diffusers 0.39.0.\n"
          "   The checkpoint ships per-tensor weight_scale/input_scale for 1462 "
          "layers; convert_ltx2_transformer_to_diffusers drops them as "
          "unexpected_keys (a warning, not an error).\n"
          "   float8_e4m3fn then raises 'mat1 and mat2 must have the same dtype' at "
          "the first denoise step, and bfloat16 renders with every scale discarded "
          "- garbage with a clean exit.\n"
          "   Use the default bf16 path, or add torchao/a _scaled_mm path first.",
          flush=True)
    return 2


def _render_with(a, transformer, parts, dist, w, h) -> int:
    """The half that is identical whichever transformer was loaded."""
    import torch
    from diffusers import (AutoencoderKLLTX2Audio, AutoencoderKLLTX2Video,
                           FlowMatchEulerDiscreteScheduler,
                           LTX2ImageToVideoPipeline)
    from diffusers.pipelines.ltx2.connectors import LTX2TextConnectors
    from diffusers.pipelines.ltx2.vocoder import LTX2VocoderWithBWE
    from diffusers.utils import load_image

    mark("load-connectors-12.7GB-and-vae")
    pipe = LTX2ImageToVideoPipeline(
        # scheduler from `dist`, NOT `parts` — see the snapshot note above; the base
        # repo's dynamic shifting would re-map the distilled sigmas.
        scheduler=FlowMatchEulerDiscreteScheduler.from_pretrained(
            dist, subfolder="scheduler", local_files_only=True),
        vae=AutoencoderKLLTX2Video.from_pretrained(
            parts, subfolder="vae", torch_dtype=torch.bfloat16),
        audio_vae=AutoencoderKLLTX2Audio.from_pretrained(
            parts, subfolder="audio_vae", torch_dtype=torch.bfloat16),
        text_encoder=None, tokenizer=None,
        connectors=LTX2TextConnectors.from_pretrained(
            parts, subfolder="connectors", torch_dtype=torch.bfloat16),
        transformer=transformer,
        vocoder=LTX2VocoderWithBWE.from_pretrained(
            parts, subfolder="vocoder", torch_dtype=torch.bfloat16))

    # SEQUENTIAL, not enable_model_cpu_offload, and the reason is VRAM rather than
    # host RAM. model_cpu_offload moves one WHOLE component to the GPU at a time;
    # the bf16 transformer is 37.99GB in 8 shards against 24GB of VRAM, so it can
    # never be resident and the call would OOM on the first denoise step no matter
    # how much host RAM is free. (The distilled model card's example uses
    # enable_model_cpu_offload because it assumes a card that fits the model.)
    # Sequential streams module-by-module instead, which fits at the cost of speed —
    # so the sample time below is an offloading number, not this card's ceiling, and
    # is not comparable to a Wan row that ran resident. Group offload (block_level,
    # the model reports _supports_group_offloading True) is the faster middle
    # ground and the obvious follow-up if this look is worth keeping.
    # Host RAM for reference: ~52.5GB of weights (transformer 37.99 + connectors
    # 12.69 + vae 1.45 + vocoder 0.26 + audio_vae 0.11) against 68.1GB, with the
    # encoder already exited — which is exactly why the two-stage split exists.
    # VAE tiling keeps the 704x1280 decode off the peak.
    mark("offload-setup")
    pipe.enable_sequential_cpu_offload(device="cuda")
    for enable in (getattr(pipe, "enable_vae_tiling", None),
                   getattr(getattr(pipe, "vae", None), "enable_tiling", None)):
        if callable(enable):
            enable()
            break

    e = torch.load(a.embeds, map_location="cpu")
    init = a.init
    if a.image_crf:
        init = _crf_roundtrip(init, a.image_crf, str(Path(a.out).parent))
    img = load_image(init)

    batch = max(1, int(a.batch))
    # THE EMBEDS PROBLEM, and it is the reason --batch had to be researched before
    # it was written rather than after. LTX2ImageToVideoPipeline.encode_prompt puts
    # the ENTIRE text path behind `if prompt_embeds is None:` (diffusers 0.39.0
    # pipeline_ltx2_image2video.py:391), so the num_videos_per_prompt repeat at
    # :333-337 only ever runs when the pipeline encodes for itself. This stage
    # exists precisely so it does NOT — the 24.4GB Gemma encoder ran in a process
    # that has already exited and left these tensors on disk. Hand them over with
    # num_videos_per_prompt=N and the embeddings stay [1, seq, dim] while
    # prepare_latents is sized batch_size * num_videos_per_prompt (:1184) and the
    # audio latents likewise (:1225): a text batch of 1 against a latent batch of N.
    #
    # So expand them here and leave num_videos_per_prompt ALONE at its default 1.
    # Doing both would square the batch — __call__ takes batch_size from
    # prompt_embeds.shape[0] when no prompt string was passed (:1111), so N
    # expanded embeddings times N videos per prompt is N*N clips.
    #
    # repeat_interleave, not expand/view: these tensors are cat'd for CFG and fed
    # to the connectors, and a stride trick that aliases one row N times is the
    # kind of thing that works until something writes in place. Upstream's own
    # repeat(1, n, 1).view(...) is interleave ordering for embeddings and
    # .repeat(n, 1) is tile ordering for the mask (:333-337) — those disagree in
    # general but coincide exactly at batch_size 1, which is all we ever have here.
    if batch > 1:
        e = {k: v.repeat_interleave(batch, dim=0) for k, v in e.items()}
        print(f"embeds expanded to batch {batch}: "
              f"{tuple(e['prompt_embeds'].shape)}", flush=True)
    # ONE IMAGE PER SLOT, and this is not cosmetic. prepare_latents' generator-list
    # branch indexes `image[i] for i in range(batch_size)` (:721-724) — a single
    # preprocessed still is [1, C, H, W], so slot 1 would be an IndexError. Passing
    # N references to the same PIL image makes preprocess emit [N, C, H, W] and
    # every slot VAE-encodes the same conditioning frame, which is what we want:
    # the clips must differ by NOISE only.
    imgs = [img] * batch if batch > 1 else img

    def _gens():
        """Fresh per-slot generators. Slot 0 keeps the base seed so a batched run
        is diffable against the un-batched clip of the same recipe.

        A FUNCTION because the two stages each built their own generator from the
        same seed before this change, and stage 2 must keep starting from a fresh
        one — sharing a single exhausted generator across both calls would silently
        alter the refine step's noise and every two-stage clip with it.

        Bare generator at batch 1: randn_tensor unwraps a length-1 list to exactly
        that, but prepare_latents branches on isinstance(generator, list) above it
        (:713), so identical-by-construction beats identical-by-argument.
        """
        return ([torch.Generator("cpu").manual_seed(a.seed + s) for s in range(batch)]
                if batch > 1 else torch.Generator("cpu").manual_seed(a.seed))

    t0 = time.time()
    from diffusers.pipelines.ltx2.utils import (DISTILLED_SIGMA_VALUES,
                                                STAGE_2_DISTILLED_SIGMA_VALUES)
    # THE NEGATIVE PROMPT IS DEAD WEIGHT ON THIS PATH and that is upstream's design,
    # not an oversight of ours: do_classifier_free_guidance is
    # (guidance_scale > 1.0) or (audio_guidance_scale > 1.0), audio defaults to the
    # video scale, so at guidance 1.0 there is no uncond pass and the negative
    # embeddings are never read. Upstream's distilled arg parser does not even
    # register --negative-prompt. It is still passed and still recorded in the
    # sidecar, because what we ASKED for is provenance, but it changes no pixel.
    common = dict(guidance_scale=a.guidance, output_type="np", return_dict=False, **e)

    if a.two_stage:
        # THE FAITHFUL RECIPE. Upstream's "8 steps" is 8 steps at HALF resolution,
        # then a 2x latent upsample, then 3 more steps at full resolution as a
        # latent refine starting from sigma 0.909375 (distilled.py:143/168/182-201;
        # stage 2's 4 sigmas are 3 model calls). A single-stage 8-step run at full
        # resolution is stage 1 asked to work at DOUBLE its intended resolution,
        # whose predicted failure is exactly "soft and under-detailed" — and that
        # would be OUR error presented to the founder as the model's ceiling.
        # It is also CHEAPER this way: 8 steps at quarter-area plus 3 at full area
        # is ~5 full-resolution step-equivalents against the naive 8.
        s1w, s1h = w // 2, h // 2
        mark(f"stage1-denoise-{s1w}x{s1h}-8steps")
        stage1 = pipe(image=imgs, height=s1h, width=s1w, num_frames=a.frames,
                      frame_rate=float(a.fps),
                      num_inference_steps=len(DISTILLED_SIGMA_VALUES),
                      sigmas=DISTILLED_SIGMA_VALUES,
                      generator=_gens(),
                      **{**common, "output_type": "latent"})[0]
        print(f"stage1 latents {tuple(stage1.shape)}", flush=True)
        if stage1.shape[0] != batch:
            # LOUD, because the whole failure mode this change guards against is a
            # batch that silently stayed 1 and produced N copies of one clip.
            print(f"!! stage 1 returned batch {stage1.shape[0]}, expected {batch} "
                  f"— the embeds expansion did not take", flush=True)
            return 2

        # output_type="latent" hands back DEnormalised 5-D latents, which is exactly
        # what the upsampler wants — hence latents_normalized=False (its default).
        # adain_factor and tone_map_compression_ratio stay 0.0: upstream's distilled
        # path just runs the upsampler, and both are off by default there too.
        mark("upsample-2x-latent")
        from diffusers.pipelines.ltx2 import LTX2LatentUpsamplePipeline
        up = LTX2LatentUpsamplePipeline(vae=pipe.vae,
                                       latent_upsampler=_load_upsampler())
        up.latent_upsampler.to(stage1.device)
        # BATCH-SAFE, checked rather than assumed: with `latents` supplied the
        # upsampler pipeline takes batch_size = latents.shape[0]
        # (pipeline_ltx2_latent_upsample.py:350), its prepare_latents only unpacks
        # and returns (:138-147), and at output_type="latent" the generator is
        # never touched — the work is one conv forward over the batch dimension
        # (:385). Its own "batched video input is not yet tested" caveat (:347)
        # applies to the video= path, which we do not use.
        up_lat = up(latents=stage1, latents_normalized=False,
                    height=s1h, width=s1w, num_frames=a.frames,
                    output_type="latent", return_dict=False)[0]
        print(f"upsampled latents {tuple(up_lat.shape)}", flush=True)
        del stage1

        # noise_scale = the first stage-2 sigma, as upstream does. prepare_latents
        # has an explicit branch for this ("conditioning_mask needs to the same
        # shape as latents in two stages generation"): 5-D latents in get
        # normalised, noised by noise_scale*(1-conditioning_mask) so the
        # conditioning frame is left clean, then packed.
        #
        # THAT BRANCH IS BATCH-CLEAN, and it is the one place a single image could
        # have failed to broadcast to N latents. It does not, because it never
        # looks at the image: batch, mask shape and conditioning_mask are all read
        # off `latents` itself (pipeline_ltx2_image2video.py:686-690), so
        # conditioning_mask is [N, 1, F, H, W] with frame 0 clean in every slot and
        # `image` is not even preprocessed on this path (:1177-1178, guarded by
        # `if latents is None`). It is still passed, unchanged, so the two calls
        # read the same.
        mark(f"stage2-refine-{w}x{h}-3steps")
        video, audio = pipe(image=imgs, height=h, width=w, num_frames=a.frames,
                            frame_rate=float(a.fps),
                            num_inference_steps=len(STAGE_2_DISTILLED_SIGMA_VALUES),
                            sigmas=STAGE_2_DISTILLED_SIGMA_VALUES,
                            latents=up_lat,
                            noise_scale=STAGE_2_DISTILLED_SIGMA_VALUES[0],
                            generator=_gens(),
                            **common)
        steps_note = (f"{len(DISTILLED_SIGMA_VALUES)}@{s1w}x{s1h}"
                      f"+{len(STAGE_2_DISTILLED_SIGMA_VALUES)}@{w}x{h}")
    else:
        kw = dict(image=imgs, height=h, width=w, num_frames=a.frames,
                  frame_rate=float(a.fps), num_inference_steps=a.steps,
                  generator=_gens(), **common)
        # The distilled build has its own sigma schedule, and asking for
        # num_inference_steps=8 is NOT the same thing: verified on this box, the
        # naive 8-step ramp is [1.0, 0.857, 0.715, 0.572, 0.429, 0.286, 0.144, 0.001]
        # where the real one front-loads five steps between 1.0 and 0.975. It must be
        # passed explicitly. The scheduler appends the trailing 0.0 itself, giving
        # 9 sigmas = 8 model calls, matching upstream's samplers.py loop.
        if a.distilled_sigmas:
            kw["sigmas"] = DISTILLED_SIGMA_VALUES
        mark("denoise-single-stage-OFF-RECIPE")
        video, audio = pipe(**kw)
        steps_note = f"{a.steps}@{w}x{h} single-stage-off-recipe"
    sample_s = time.time() - t0

    mark("decode-and-export")
    from diffusers.utils import export_to_video

    peak = torch.cuda.max_memory_allocated() / 1e9 if torch.cuda.is_available() else 0
    free, total = torch.cuda.mem_get_info() if torch.cuda.is_available() else (0, 1)

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import video_task
    label = a.bench_label or "ltx23"
    clip_s = a.frames / a.fps
    negative = (a.negative + "\n[unused: guidance 1.0 on the distilled path runs "
                             "no uncond pass, so this changed no pixel]"
                ) if a.negative else a.negative

    for s in range(batch):
        # slot_out_path returns --out UNCHANGED at batch 1, so the default path
        # still writes exactly the file it was asked for; only a batched run gets
        # the `-b<N>-s<seed>` naming the AnimeGen probe already put on disk.
        path = video_task.slot_out_path(a.out, a.seed, s, batch)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        export_to_video(video[s], path, fps=a.fps)
        # The [i/N] line keeps wan_i2v's exact shape so bench_models' WROTE regex
        # and video_task's PROGRESS regex keep parsing; steps carries the
        # two-stage note instead of a bare integer, since "8 steps" alone would
        # misdescribe what ran. At batch 1 this is byte-identical to the [1/1]
        # line this file has always printed. The elapsed figure repeats on every
        # slot because no per-slot time exists — the N clips were denoised
        # together, and that IS the measurement.
        print(f"[{s + 1}/{batch}] wrote {path} in {sample_s:.0f}s "
              f"({a.frames} frames, {w}x{h}, {steps_note} steps, "
              f"peak torch {peak:.1f}GB, "
              f"device {(total-free)/1e9:.1f}/{total/1e9:.0f}GB"
              + (f", slot {s+1}/{batch} seed {a.seed + s})" if batch > 1 else ")"),
              flush=True)
        # seed_base = a.seed - a.beat, NOT a.seed. write_sidecar publishes
        # seed_base + beat, so passing the seed itself would have printed 20260732
        # for a clip generated with 20260731 — a sidecar naming a seed nobody
        # rendered with, which is worse than no seed at all for anyone trying to
        # reproduce a screened look. This matches wan_i2v's convention, where
        # --seed is already the per-beat seed and the sidecar reconstructs it.
        # The slot's OWN seed goes in, so slot 1 of a b2 does not claim slot 0's.
        video_task.write_sidecar(
            path, "ltx23-distilled",
            {"worker": a.worker, "guidance": a.guidance,
             "seed_base": a.seed + s - a.beat, "id": a.task},
            beat=a.beat, seconds=round(clip_s, 3), steps=steps_note,
            size=a.size, prompt=a.prompt,
            # Recorded verbatim, with the caveat attached, because a reader of
            # this sidecar cannot otherwise tell that the negative was inert.
            negative=negative,
            extra={"mode": a.mode, "batch": batch, "batch_slot": s,
                   "throughput_s_video_per_s_wall":
                       round(batch * clip_s / sample_s, 4),
                   "compute_s_per_video_s": round(sample_s / batch / clip_s, 1)})
    # THE DECODE IS ONE CALL, so this release is per-batch and not per-slot, and
    # saying otherwise would be a comment describing code that does not exist:
    # output_type="np" makes postprocess_video stack all N clips into a single
    # [N, F, H, W, C] array, and a row of a stacked array cannot be freed on its
    # own. What CAN be done is drop the whole thing before the bench write instead
    # of at function exit — at 704x1280/61f that is ~165MB per slot of host RAM,
    # and host RAM is what killed the b4 probe on 2026-08-05.
    del video, audio
    gc.collect()

    # (N clips of video) / (one wall-clock sample). The number the probe exists to
    # produce: if it does not rise with N, the card is step-bound and batching
    # buys nothing.
    print(f"THROUGHPUT {batch * clip_s / sample_s:.4f} s(video)/s(wall) "
          f"({batch} x {clip_s:.3f}s of video in {sample_s:.0f}s)", flush=True)
    if a.bench_jsonl:
        # ONE ROW PER SAMPLE CALL, not per slot: the measurement is the call.
        #
        # s_per_step IS NULL ON THE TWO-STAGE PATH and that is the honest cell.
        # The run is 8 model calls at half resolution plus 3 at full; dividing the
        # wall clock by 11 would invent a uniform "step" that nothing executed.
        # throughput_s_per_s carries the comparison instead, and `steps` carries
        # the note that says what actually ran.
        video_task.append_bench_row(a.bench_jsonl, video_task.bench_row(
            label=label, repo=DIST_REPO, mode=a.mode, batch=batch,
            frames=a.frames, seeds=[a.seed + s for s in range(batch)],
            sample_s=round(sample_s, 1),
            s_per_step=(None if a.two_stage else round(sample_s / a.steps, 2)),
            video_s=round(batch * clip_s, 3),
            throughput_s_per_s=round(batch * clip_s / sample_s, 4),
            # per SECOND OF VIDEO, matching the sidecar field of the same meaning
            # and the column's name. wan_i2v wrote seconds-per-CLIP here until
            # 2026-08-05; this file never shipped a row either way, so it starts
            # correct.
            compute_per_video_s=round(sample_s / batch / clip_s, 1),
            peak_torch_gb=round(peak, 1),
            device_gb=round((total - free) / 1e9, 1),
            device_total_gb=round(total / 1e9, 1),
            # Host RAM comes from THIS file's GlobalMemoryStatusEx sampler, which
            # is the same quantity wan_i2v's psutil thread records — physical, and
            # physical plus pagefile.
            host_peak_phys_gb=(round(PEAK["phys_gb"], 1) or None),
            host_peak_commit_gb=(round(PEAK["commit_gb"], 1) or None),
            steps=steps_note, guidance=a.guidance, shift=_scheduler_shift(pipe),
            size=f"{w}x{h}", ok=True))
    print(json.dumps({"sample_s": round(sample_s, 1), "peak_gb": round(peak, 1),
                      "peak_commit_gb": round(PEAK["commit_gb"], 1),
                      "frames": a.frames, "size": a.size, "steps": steps_note,
                      "batch": batch, "mode": a.mode,
                      "throughput_s_per_s": round(batch * clip_s / sample_s, 4),
                      "two_stage": bool(a.two_stage), "image_crf": a.image_crf,
                      "offload": "sequential"}),
          flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["encode", "render"], required=True)
    ap.add_argument("--embeds", required=True)
    ap.add_argument("--prompt", default="")
    ap.add_argument("--negative", default="")
    # Prompts come from FILES, not argv, whenever they are offered. The beat-1
    # negative contains "静态, 静止" and a Windows console is cp1252 by default, so
    # the same string that renders correctly from a file arrives mangled through
    # cmd — and a silently altered negative prompt is an invisible change to the
    # render, not an error anyone would notice in the output.
    ap.add_argument("--prompt-file", default="")
    ap.add_argument("--negative-file", default="")
    ap.add_argument("--init", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--size", default="704x1280", help="WxH, both divisible by 32")
    ap.add_argument("--frames", type=int, default=65, help="must be 8n+1")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--steps", type=int, default=8, help="distilled recommendation")
    ap.add_argument("--guidance", type=float, default=1.0, help="distilled: CFG 1")
    ap.add_argument("--distilled-sigmas", action="store_true")
    # Retained, not removed: the 9GB fp8 partial is still on disk against a future
    # torchao / torch._scaled_mm path. It refuses immediately on this diffusers.
    ap.add_argument("--fp8-single-file", action="store_true",
                    help="BROKEN on diffusers 0.39.0 — see module docstring")
    # Upstream's actual distilled recipe. Off by default so the flag has to be asked
    # for, but it is the ON-RECIPE path: without it an 8-step render runs at double
    # the resolution stage 1 was meant for.
    ap.add_argument("--two-stage", action="store_true",
                    help="8 steps at half res -> 2x latent upsample -> 3 steps at "
                         "full res, as upstream's DistilledPipeline does")
    # 33 = upstream DEFAULT_IMAGE_CRF; 0 = feed the clean PNG (out of distribution
    # by their reckoning).
    ap.add_argument("--image-crf", type=int, default=0,
                    help="round-trip the still through libx264 at this CRF first")
    ap.add_argument("--seed", type=int, default=20260731)
    ap.add_argument("--beat", type=int, default=1)
    ap.add_argument("--task", default="d16c-one-sample")
    ap.add_argument("--worker", default="rtx5090")
    # --- throughput probing. Default 1 = the path that has always run. -------
    # These four are wan_i2v.py's, spelled the same way on purpose: two renderers
    # append to one bench file, and a flag that means something slightly different
    # here would turn the comparison table into a guess.
    ap.add_argument("--batch", type=int, default=1,
                    help="clips per sample call. A MEASUREMENT, not a queue "
                         "filler: the N clips share one prompt and one still and "
                         "differ only by seed (base seed for slot 0, +1 after)")
    ap.add_argument("--mode", default="production",
                    help="recipe label recorded in the sidecar and the bench row; "
                         "the 2026-08-04 rows use preview|production")
    ap.add_argument("--bench-jsonl", default="",
                    help="append ONE measurement row per sample call to this file")
    ap.add_argument("--bench-label", default="",
                    help="'label' column for --bench-jsonl (default: ltx23)")
    a = ap.parse_args()
    if a.batch < 1:
        print(f"!! --batch {a.batch}: must be at least 1", flush=True)
        return 2
    if a.prompt_file:
        a.prompt = Path(a.prompt_file).read_text(encoding="utf-8").strip()
    if a.negative_file:
        a.negative = Path(a.negative_file).read_text(encoding="utf-8").strip()

    stop = threading.Event()
    threading.Thread(target=_sampler, args=(stop,), daemon=True).start()
    mark(f"begin-{a.stage}")
    try:
        return stage_encode(a) if a.stage == "encode" else stage_render(a)
    except BaseException as e:
        # BaseException, not Exception: a host-RAM death can arrive as
        # MemoryError, a CUDA RuntimeError, or a KeyboardInterrupt-shaped kill,
        # and the peak is the whole point of the run if the clip does not happen.
        print(f"!! DIED in stage '{PEAK['stage']}': {type(e).__name__}: {e}",
              flush=True)
        raise
    finally:
        stop.set()
        print(json.dumps({"peak_commit_gb": round(PEAK["commit_gb"], 1),
                          "peak_phys_gb": round(PEAK["phys_gb"], 1),
                          "last_stage": PEAK["stage"]}), flush=True)


if __name__ == "__main__":
    sys.exit(main())
