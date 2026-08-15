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

THERE ARE TWO fp8 ROUTES AND THEY ARE NOT THE SAME THING. The paragraph above is
about --fp8-single-file: someone ELSE's statically-quantised checkpoint, which this
diffusers cannot read. --fp8-layerwise is ours, and it needs no download at all —
diffusers casts the bf16 weights WE ALREADY LOAD to fp8 for STORAGE and upcasts each
layer back to bf16 for the duration of its own forward
(hooks/layerwise_casting.py: initialize_hook -> storage, pre_forward -> compute,
post_forward -> storage). No weight_scale is involved, so nothing can be silently
dropped. Upstream vetted this class for it: LTX2VideoTransformer3DModel sets
_skip_layerwise_casting_patterns = ["norm"] (transformer_ltx2.py:1092), i.e. the
precision-critical norms stay bf16 by the model's own declaration, not by ours.
THE POINT IS NOT THE FILE SIZE, IT IS THE OFFLOAD SWITCH THE CAST ALLOWS. See the
--offload note in _render_with: 38GB of bf16 transformer cannot sit on a 23.89GiB
card, so this file has always run enable_sequential_cpu_offload, which streams every
module on every forward and leaves the GPU 45-55% idle. At ~19.8GiB of fp8 storage
the transformer fits, so `--offload model` can keep it resident for the whole
denoise loop. That is the mechanism being tested. It is a KNIFE EDGE — ~19.8GiB of
weights plus ~4GB of activations against 23.89GiB — which is why it is a flag with a
sample behind it and not a new default.
AND THE KNIFE FELL, on one side only. Measured 2026-08-04/05 with --fp8-layerwise
--offload model: stage 1 at 352x640 gets FASTER with work (2.2 s/step at batch 2
against 1.3 at batch 1 — the card being fed), while stage 2 at 704x1280 pins it at
98.6% and spills, and that spill is the WDDM signature that bugchecked the host. One
flag cannot be right for both halves of a two-stage recipe, so `--offload split` is
the two of them in sequence: resident through stage 1 and the upsampler, streamed
through stage 2, switched in-process at the boundary (_switch_to_sequential).

Licence: LTX-2 Community License Agreement, D16 — CANDIDATE under watch-only, and
the sidecar says so via video_task.MODEL_LICENCE["ltx23-distilled"] (the fp8 key is
kept for the archived partial). Same document either way: Lightricks/LTX-2.3's
LICENSE is 21393 chars and is that Agreement, byte-length identical to the copy
embedded in the fp8 file's own header. licence_gate still refuses to publish an LTX
clip until the founder signs off on the screened look; this script renders a bench
sample, it does not clear anything.
"""
import argparse
import copy
import ctypes
import gc
import json
import sys
import threading
import time
from pathlib import Path

# Sibling module, pure stdlib. This script is launched by absolute path out of
# the repo checkout (video_task.py: REPO/"pipeline"/"ltx_i2v.py"), so the
# script's own directory is already sys.path[0]; the insert is belt-and-braces
# for the hand lanes that run it from elsewhere.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompt_budget import check_prompt_budget  # noqa: E402


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


def stg_kwargs(stg_scale, stg_blocks) -> dict:
    """The STG kwargs for one pipe() call — {} unless STG was explicitly asked for.

    SPATIOTEMPORAL GUIDANCE, and why it is a flag on this file at all. LTX-Video
    collaborator `ybitterman` (an author on the LTX-Video paper), answering
    "how to increase the motion size of the generated video?" in
    <https://github.com/Lightricks/LTX-Video/issues/184>, replied in full:
    "Playing with the STG blocks will help with that." That is the only
    maintainer answer to our exact symptom that exists. Lightricks' own
    multimodal-guidance doc pairs it with the CFG warning ("higher `cfg_scale` =
    ... potentially less natural motion"), and the STG paper
    (<https://arxiv.org/abs/2411.18664>) opens by saying CFG-family guidance
    "reduce[s] diversity and motion" while STG boosts quality "without
    compromising diversity or dynamic degree". The official
    ltxv-13b-0.9.8-DISTILLED config sets `stg_scale: 0` in both passes; the DEV
    config schedules it to 4. So the one documented motion lever is off BY
    CONSTRUCTION on the distilled path we run — not because anyone measured it
    here. All of that is written up in `pipeline/research/ltx23-motion-source.md`
    §2.2/§3.1 (commit dfa87c27) with the URLs.

    IT IS REACHABLE FROM OUR CALL PATH, read in the installed source on the box
    rather than in the docs: `LTX2ImageToVideoPipeline.__call__` takes
    `stg_scale: float = 0.0` (line 883) and
    `spatio_temporal_guidance_blocks: list[int] | None = None` (890);
    `check_inputs` refuses scale>0 without blocks (536); a second uncond forward
    runs under `cache_context("uncond_stg")` (1371) and enters the update as
    `video_stg_delta = self.stg_scale * (noise_pred_video -
    noise_pred_video_uncond_stg)` (1407). Cost: ONE extra transformer forward per
    step, nothing else.

    THE NUMBERS ARE UPSTREAM'S, not ours. The `spatio_temporal_guidance_blocks`
    docstring says verbatim "A value of `[29]` is recommended for LTX-2.0 and
    `[28]` is recommended for LTX-2.3", and the `audio_stg_scale` docstring says
    "For LTX-2.3, a value of 1.0 is suggested for both video and audio". We run
    LTX-2.3, so [28] and 1.0 are the documented starting point and are what the
    first sample used. `audio_stg_scale` is deliberately NOT passed: upstream
    defaults it to the video value (`audio_stg_scale = audio_stg_scale or
    stg_scale`, line 1072) and we discard the audio stream anyway.

    OFF IS EMPTY, NOT ZERO, and that is the whole design of this function. When
    `--stg-scale` is absent this returns `{}`, so the kwargs handed to `pipe()`
    are the same dict this file has always built — no `stg_scale=0.0` argument
    appears, no default is restated, and a job that does not ask for STG cannot
    be changed by this code path. That is the property the byte-identity check
    rests on (see the STG note in `_render_one`).
    """
    try:
        scale = float(stg_scale or 0.0)
    except (TypeError, ValueError):
        raise ValueError("--stg-scale %r is not a number" % (stg_scale,))
    if scale <= 0.0:
        return {}
    blocks = [int(b) for b in str(stg_blocks or "").replace(",", " ").split()]
    if not blocks:
        # Upstream raises the same refusal at check_inputs (line 536), but ninety
        # seconds of weight loading later. Refusing here means the mistake costs
        # nothing, and the message carries the recommended value so nobody has to
        # go and find it.
        raise ValueError(
            "--stg-scale %g needs --stg-blocks: the pipeline's own docstring says "
            "the blocks 'must be supplied if STG is used' and that '[28] is "
            "recommended for LTX-2.3'. Pass --stg-blocks 28." % scale)
    return {"stg_scale": scale, "spatio_temporal_guidance_blocks": blocks}


def sidecar_negative(negative: str, guidance: float) -> str:
    """The negative as the sidecar should record it — with the caveat ONLY when true.

    The negative prompt is dead weight on the distilled path AT GUIDANCE 1.0 AND
    NOT OTHERWISE: `do_classifier_free_guidance` is `(guidance_scale > 1.0) or
    (audio_guidance_scale > 1.0)` and audio defaults to the video scale, so CFG —
    and with it the uncond pass that is the only thing that ever reads the
    negative embeddings — is live for every guidance above 1.0.

    Until 2026-08-16 the caveat was appended UNCONDITIONALLY, which made it FALSE
    on every render above 1.0: our own job specs pass 2.0, so the sidecars of the
    renders whose negative genuinely bit all claimed it "changed no pixel". A
    provenance line that is wrong is worse than an absent one, because the next
    lane reads it as a measurement. Sidecar text only — this has never touched a
    pixel, at 1.0 or anywhere else.

    Empty in, empty out: a render that was given no negative gets no caveat about
    one, at any guidance.
    """
    if not negative:
        return negative
    if float(guidance) > 1.0:
        return negative
    return (negative + "\n[unused: guidance %g on the distilled path runs no "
            "uncond pass, so this changed no pixel]" % float(guidance))


def _weight_gib(module) -> float:
    """GiB of parameters + buffers, from element_size — a MEASUREMENT of the cast.

    Layerwise casting's initialize_hook calls module.to(storage_dtype) the moment it
    is attached, so this reads 1 byte per fp8 element immediately after the call and
    2 for whatever was skipped. A cast that did not take shows up as an unchanged
    number, which is the only cheap way to tell before the denoise loop starts.
    """
    return sum(t.numel() * t.element_size()
               for t in list(module.parameters()) + list(module.buffers())) / 2**30


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


def _crf_roundtrip(src: str, crf: int, out_dir: str, tag: str = "") -> str:
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
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    # `tag` NAMES THE BEAT, and it exists because these two files are throwaway and
    # a fifteen-beat run makes fifteen of each. Un-tagged they would be one pair
    # overwritten fourteen times — which works, since each is consumed immediately,
    # but leaves a diagnostic that can only ever describe the last beat.
    mid = str(Path(out_dir) / f"cond-crf{tag}.mp4")
    png = str(Path(out_dir) / f"cond-crf{tag}.png")
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


def _write_lossless(frames, path: str, fps: int) -> None:
    """A SECOND copy of the same decoded frames with the encoder taken out of it.

    export_to_video hands imageio its default quality, which on our clips lands
    around 1 Mbps, and MODEL-COMPARISON.md:487 had to leave the period-3 motion
    cadence open because a bitrate-starved inter-frame encode can manufacture
    exactly that reading — repeated P-frames are what an x264 rate control does
    when it runs out of bits. -qp 0 is x264's true lossless mode and yuv444p
    leaves chroma unsubsampled, so whatever cadence survives here is in the
    model's own frames and not in the container.

    The uint8 conversion is export_to_video's line, character for character
    ((frame * 255).astype(np.uint8)), because the two files must differ ONLY in
    the encode. Frames are piped one at a time rather than as one 190MB write:
    stderr is not drained, so a single write big enough to fill the pipe while
    ffmpeg blocks is a deadlock with no output to explain it.
    """
    import subprocess

    import imageio_ffmpeg
    import numpy as np

    arr = np.asarray(frames)
    if arr.dtype != np.uint8:
        arr = (arr * 255).astype(np.uint8)
    n, h, w = arr.shape[0], arr.shape[1], arr.shape[2]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.Popen(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
         "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-qp", "0",
         "-pix_fmt", "yuv444p", path], stdin=subprocess.PIPE)
    for frame in arr:
        p.stdin.write(frame.tobytes())
    p.stdin.close()
    rc = p.wait()
    print(f"lossless copy: {n} frames {w}x{h} at x264 -qp 0 yuv444p -> {path} "
          f"(rc={rc})", flush=True)


def _decode_frame0_replica(pipe, decode, cap: dict, path: str, fps: int) -> None:
    """Decode the run's OWN latents again, frame 0 held for the whole clip.

    THE QUESTION THIS ANSWERS, and it is the only question it answers. The
    2026-08-06 measurement puts LTX-2.3's chroma collapse between the
    conditioning still (Cab 27.34, matched at frame 0) and the exported pixels
    (Cab ~3 by frame 18). Two things sit in that gap: the denoiser, which writes
    the latents, and the VAE, which reads them. Replaying the SAME decoder on the
    SAME latents with every latent frame replaced by latent frame 0 separates
    them, because frame 0 is the position we already know decodes coloured:
      coloured replica -> the decoder is fine at every temporal position and the
                          grey is in the latents (a model/prior problem)
      grey replica     -> a decoder that greys out everything past position 0,
                          which would be a VAE bug and a different fix entirely
    It is a decode, not a denoise: seconds, no extra sample, no second recipe.

    `decode` is the UNWRAPPED bound method captured before the run, and `cap`
    carries the positional timestep and kwargs the pipeline itself passed, so the
    replay differs from the real decode in the latents and in nothing else.
    """
    import torch

    from diffusers.utils import export_to_video

    lat = cap.get("latents")
    if lat is None or lat.ndim != 5:
        print(f"!! frame-0 replica skipped: latents {None if lat is None else tuple(lat.shape)}"
              f" is not the [B,C,F,H,W] shape vae.decode was expected to receive",
              flush=True)
        return
    # repeat, not expand: this tensor goes into a conv stack, and an aliased
    # stride trick is the kind of thing that works until something writes in place.
    held = lat[:, :, :1].repeat(1, 1, lat.shape[2], 1, 1)
    with torch.no_grad():
        out = decode(held, *cap["args"], **cap["kw"])
    vid = out[0] if isinstance(out, tuple) else out.sample
    vid = pipe.video_processor.postprocess_video(vid, output_type="np")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    export_to_video(vid[0], path, fps=fps)
    print(f"frame-0 replica decode: latents {tuple(lat.shape)} -> "
          f"{tuple(held.shape)} -> {path}", flush=True)


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


def _jobs_for(a, stage: str) -> list:
    """The run's beats, one argparse namespace each. `[a]` when --jobs was absent.

    WHAT THIS IS FOR, in one number: an episode is fifteen beats, and until this
    existed each of them was its own pair of processes — 88s of Gemma, then a
    transformer load and (with --fp8-layerwise) a 139s cast, per beat. The clip
    itself is 73.3s. Fifteen beats that way is ~78 minutes of which ~62 is loading
    the same weights again. wan_i2v.py already carries the same flag for the same
    reason ("per-clip processes spent ~10 of every 11 minutes reloading",
    video_task.py); this is that flag on the LTX CLI, and the two stages keep their
    split — one encode process for all fifteen prompts, one render process for all
    fifteen clips, because Gemma at all 49 hidden layers peaks ~37GB host and still
    cannot be co-resident with the transformer.

    ONE JOBS FILE SERVES BOTH STAGES. Each entry names the beat's embeds path, so
    the encode process writes exactly what the render process then reads, and
    neither side reconstructs a filename the other invented. Per-entry keys:
      embeds        (both)    where the beat's .pt lives
      prompt_file   (encode)  the positive, READ FROM A FILE
      negative_file (encode)  the negative, likewise; optional
      init, out     (render)  conditioning still, clip path
      seed, beat    (render)  per-beat, and the sidecar publishes both
    PROMPTS COME FROM FILES AND NOT FROM THE JSON — the same rule main() already
    applies to --prompt-file. A jobs file COULD carry the strings inline (wan's
    does), but the LTX negatives contain "静态, 静止" and this runs over a cp1252
    console; keeping them in files means the bytes that reach Gemma are the bytes
    on disk no matter what the console thinks it is.

    A missing key RAISES rather than defaulting. Fifteen beats is a batch, and a
    beat that quietly rendered from the wrong still or wrote over another beat's
    path is the kind of defect that is only visible after the whole hour is spent.
    """
    if not a.jobs:
        return [a]
    spec = json.loads(Path(a.jobs).read_text(encoding="utf-8"))
    if not isinstance(spec, list) or not spec:
        raise ValueError(f"--jobs {a.jobs}: expected a non-empty json list of beats")
    need = (("embeds", "prompt_file") if stage == "encode"
            else ("embeds", "init", "out"))
    jobs = []
    for i, j in enumerate(spec):
        if not isinstance(j, dict):
            raise ValueError(f"--jobs {a.jobs}[{i}]: expected an object, got "
                             f"{type(j).__name__}")
        missing = [k for k in need if not j.get(k)]
        if missing:
            raise ValueError(f"--jobs {a.jobs}[{i}] (stage {stage}): missing "
                             f"{', '.join(missing)}")
        # copy.copy, so every recipe flag the CLI carries — size, frames, offload,
        # two_stage, image_crf, guidance, mode — is the SAME object's value on every
        # beat. A jobs file cannot vary the recipe, and that is deliberate: one model
        # load means one recipe, and a per-beat recipe would need a per-beat load.
        ja = copy.copy(a)
        ja.embeds = str(j["embeds"])
        ja.beat = int(j.get("beat", a.beat))
        ja.seed = int(j.get("seed", a.seed))
        ja.init = str(j.get("init") or a.init)
        ja.out = str(j.get("out") or a.out)
        ja.prompt = (Path(j["prompt_file"]).read_text(encoding="utf-8").strip()
                     if j.get("prompt_file") else a.prompt)
        ja.negative = (Path(j["negative_file"]).read_text(encoding="utf-8").strip()
                       if j.get("negative_file") else a.negative)
        # Carry the SOURCE forward, not just the text. The token-budget guard in
        # stage_encode has to be able to say which file to shorten, and by the
        # time it runs the prompt is a bare string a dozen beats deep in a batch.
        # getattr, not attribute access: the tests (and any hand-built namespace)
        # construct these args by hand and only set the keys under test, so
        # requiring --prompt-file to exist would make this function fail on
        # callers it served fine before. Additive means additive.
        ja.prompt_file = str(j.get("prompt_file")
                             or getattr(a, "prompt_file", "") or "")
        ja.negative_file = str(j.get("negative_file")
                               or getattr(a, "negative_file", "") or "")
        jobs.append(ja)
    outs = [ja.out for ja in jobs if ja.out]
    if stage == "render" and len(set(outs)) != len(outs):
        raise ValueError(f"--jobs {a.jobs}: two beats write the same --out")
    return jobs


def stage_encode(a) -> int:
    """Gemma ONLY: prompt in, embeddings on disk, process exits.

    The pipeline is built with every other component None. That is the same trick
    wan_i2v.py uses, and it is what keeps 24.4GB and 29.5GB from ever being
    resident together.

    WITH --jobs THE ENCODER LOADS ONCE AND WRITES N FILES. 24.4GB read from disk
    per beat was the whole of the 88s; encode_prompt itself is seconds. The loop
    is inside the process for that reason and the process still EXITS at the end
    of it, because exiting is what gives the 37GB back before the transformer is
    read (see the module docstring — that split is not optional).
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

    jobs = _jobs_for(a, "encode")
    # EVERY BEAT IS CHECKED BEFORE ANY BEAT IS ENCODED. A batch that refuses on
    # beat 12 after eleven .pt files are on disk is a half-written run someone
    # has to reason about; refusing before the loop leaves the tree untouched.
    #
    # What this prevents: encode_prompt below tokenizes with
    # padding="max_length", max_length=max_sequence_length, truncation=True, and
    # LTX2's version in diffusers 0.39.0 — unlike most diffusers pipelines — keeps
    # no untruncated copy and logs no `removed_text` warning. Truncation here is
    # SILENT ON EVERY CHANNEL: probed on the box 2026-08-14, a 2,601-token prompt
    # returned exactly 1024 tokens with zero python warnings, zero stderr, zero
    # stdout. The overflow would just be gone, the clip would render, and the
    # sidecar would publish the full prompt we believed we sent.
    #
    # Headroom today: 871 prompt files on the box max out at 684 tokens and the
    # 73 committed job specs at 297, against a 1024 limit — 67% of budget at
    # worst. This has never fired and is not a live defect. It is the number with
    # no check next to it, which is the shape of the two silent failures closed
    # the same week.
    #
    # The limit is READ from pipe.encode_prompt's signature, never written here:
    # a hardcoded 1024 would keep passing after a diffusers bump moved the real
    # cliff, and a guard that has silently stopped checking is worse than none.
    # We pass no max_sequence_length below, hence explicit=None — if that ever
    # changes, hand the same value in as `explicit` so the check follows the call.
    for ja in jobs:
        check_prompt_budget(
            pipe.encode_prompt, tokenizer,
            [(getattr(ja, "prompt_file", "") or "--prompt", ja.prompt),
             (getattr(ja, "negative_file", "") or "--negative", ja.negative)],
            explicit=None, job=f"beat {ja.beat:02d} -> {ja.embeds}")
    for i, ja in enumerate(jobs, 1):
        mark(f"encode-beat-{ja.beat:02d}")
        with torch.no_grad():
            pos, pos_mask, neg, neg_mask = pipe.encode_prompt(
                prompt=ja.prompt, negative_prompt=ja.negative,
                do_classifier_free_guidance=True, device="cpu")
        Path(ja.embeds).parent.mkdir(parents=True, exist_ok=True)
        torch.save({"prompt_embeds": pos.to(torch.bfloat16),
                    "prompt_attention_mask": pos_mask,
                    "negative_prompt_embeds": neg.to(torch.bfloat16),
                    "negative_prompt_attention_mask": neg_mask}, ja.embeds)
        # "encoded", never "wrote": video_task's PROGRESS regex marks a finished
        # CLIP off `[i/N] wrote`, and an embeds file is not a clip. The bracket
        # prefix is still here so the encode process is visibly counting down
        # rather than merely alive.
        print(f"[{i}/{len(jobs)}] encoded beat {ja.beat} to {ja.embeds} "
              f"{tuple(pos.shape)}", flush=True)
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

    # THE CAST HAPPENS HERE — before the pipeline is assembled and before any
    # offload call — for two reasons. The weights are at their most movable while
    # nothing holds a reference to them but this name, and the offload hooks must be
    # attached to the model in the shape it will actually run in.
    #
    # THE CAST SURVIVES THE OFFLOAD CALL, checked in the source rather than hoped
    # for: enable_sequential_cpu_offload's remove_all_hooks() strips ACCELERATE
    # hooks, and layerwise casting lives in the diffusers HookRegistry
    # (module._diffusers_hook), which that call does not touch. Two hook systems on
    # one module is nevertheless exactly the thing this sample exists to prove, so
    # the storage size is MEASURED below and printed — if the cast silently did not
    # take, the number says so before an hour of GPU time is spent.
    #
    # HOST RAM IS THE KNOWN HAZARD OF AN IN-PROCESS CAST, measured on THIS box on
    # 2026-08-04: the AnimeGen fp8 cast retained the bf16 storages it replaced —
    # ~40GB of live weights against 128.7GB of commit charge — because a freed
    # torch storage returns to the caching allocator, not to the OS. Worst case here
    # is ~38GB of retained bf16 + ~19GB of fp8 + 12.7GB connectors + ~2GB misc
    # ~= 72GB of commit against this box's ~124GB limit, so it fits where AnimeGen
    # did not, and it fits for a structural reason: the render stage NEVER holds the
    # 24.4GB Gemma encoder (that is what the two-stage split is for). Expected LIVE
    # PHYSICAL is ~34GB — a large improvement on the 60.8GB the bf16 production run
    # measured, since the resident copy is the fp8 one. The sampler thread above
    # records both numbers either way; do not restate them from this comment.
    if a.fp8_layerwise:
        mark("cast-fp8-layerwise")
        before = _weight_gib(transformer)
        t_cast = time.time()
        transformer.enable_layerwise_casting(
            storage_dtype=torch.float8_e4m3fn, compute_dtype=torch.bfloat16)
        gc.collect()
        print(f"fp8 layerwise cast in {time.time() - t_cast:.0f}s: transformer "
              f"storage {before:.2f} -> {_weight_gib(transformer):.2f} GiB "
              f"(norms stay bf16 by the model's own "
              f"_skip_layerwise_casting_patterns)", flush=True)

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


def _switch_to_sequential(pipe, upsampler) -> str:
    """--offload split: drop the resident recipe at the stage seam and stream stage 2.

    Called once, between the 2x latent upsample and the stage-2 refine. Returns the
    string that then goes in the sidecar and the closing json, so the record is
    written BY the code that did the thing rather than by a flag that only asked.

    ALL FOUR MECHANISMS ARE READ OUT OF THE INSTALLED 0.39.0 SOURCE, not out of
    docs, and the paths are the box's own venv copy:

    1. THE ACCELERATE HOOKS COME OFF CLEANLY. enable_sequential_cpu_offload calls
       remove_all_hooks() itself as its second act (pipeline_utils.py:1329) — the
       same call enable_model_cpu_offload makes at :1223 — and remove_all_hooks
       (:1181-1188) only ever does accelerate.hooks.remove_hook_from_module(model,
       recurse=True) on components that have an `_hf_hook`. Nothing in the sequential
       path examines or forbids a prior model offload: its only raising guards are
       group-offload-is-active (:1323 -> :2228-2244, and we are not group-offloaded
       because that branch is an if/elif) and a dict device_map (:1331-1336, ours is
       None). So the switch is not a trick; it is two supported calls in a row.

    2. THE fp8 LAYERWISE CAST SURVIVES IT — now checked in both directions instead
       of assumed once. accelerate's remove_hook_from_module (accelerate/hooks.py:
       218-234) deletes `_hf_hook`, restores `module.forward = module._old_forward`,
       and pops exactly _accelerate_added_attributes = ["to","cuda","npu","xpu",
       "mlu","sdaa","musa"] (:55) from __dict__. It never touches `_diffusers_hook`,
       which is where the layerwise cast lives (diffusers/hooks/hooks.py:264-265).
       And `_old_forward` is whatever `module.forward` was when the accelerate hook
       went on (:176-181) — i.e. the HookRegistry-rewritten forward installed at
       hooks/hooks.py:207-209, because ltx_i2v casts BEFORE assembling the pipeline.
       Removal therefore restores the cast wrapper, by construction.
       They are not even on the same modules under `model`: cpu_offload_with_hook
       hooks the top-level transformer, while layerwise casting hooks leaf
       Linear/Conv modules (layerwise_casting.py:184-187).
       Under `sequential` they DO land on the same leaves, and the nesting is the
       right way round: accelerate's pre_forward materialises the leaf's params from
       weights_map, then calls _old_forward, which is the layerwise wrapper, which
       upcasts fp8->bf16 for the duration of the real forward (:65-72) and puts it
       back after. LayerwiseCastingHook is `_is_stateful = False` and holds no tensor
       references — it re-reads `module` every call — so accelerate handing it
       freshly materialised parameters each step is fine.
       ONE CONSEQUENCE WORTH EXPECTING RATHER THAN DISCOVERING: what streams in
       stage 2 is now fp8 storage, ~19.8GiB per full pass instead of ~38GB, so the
       PCIe bill per step is about half what plain `--offload sequential` pays — but
       every leaf now also does two casts it did not do before. Which of those wins
       is a measurement, and the sample is what takes it.

    3. THE VRAM IS NOT RETURNED UNLESS WE RETURN IT, and this is the line that makes
       the difference between a working switch and the same 98.6% spill wearing a new
       flag. enable_sequential_cpu_offload moves the pipeline to CPU and empties the
       device cache only inside `if self.device.type != "cpu"` (:1358-1361), and
       `self.device` (:588-600) is the device of the FIRST nn.Module in
       sorted(_get_signature_keys(...)) (:1837-1849) — for LTX2ImageToVideoPipeline
       that is `audio_vae`, which under model offload never left the CPU. The guard
       reads False, both the move and the empty_cache are skipped, and then
       accelerate's cpu_offload builds its host copy with
       `state_dict = {n: p.to("cpu") for n, p in model.state_dict().items()}`
       (accelerate/big_modeling.py:210) off a transformer that is still on the card:
       a second ~19.8GiB of host RAM, with the CUDA blocks merely handed back to the
       caching allocator and never released. So we do the move ourselves, first, and
       then the library's copy is a no-op on tensors already on CPU.

    4. THE UPSAMPLER IS NOT A PIPELINE COMPONENT. It was moved to the card by hand
       (up.latent_upsampler.to(stage1.device)) and pipe.to("cpu") cannot reach it,
       because LTX2LatentUpsamplePipeline is a separate object. Left alone it would
       hold its weights on the card through all of stage 2 for no reason.

    The printed before/after is the honest check: if the card does not drop to
    roughly the CUDA context plus the upsampled latents, the tear-down did not
    return what it was supposed to and stage 2 is about to spill anyway.
    """
    import torch
    mark("offload-switch-model-to-sequential")
    if torch.cuda.is_available():
        free, total = torch.cuda.mem_get_info()
        before = (total - free) / 1e9
    else:
        before = total = 0.0
    if upsampler is not None:
        upsampler.to("cpu")
    pipe.remove_all_hooks()
    pipe.to("cpu")
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        free, total = torch.cuda.mem_get_info()
        print(f"switch model->sequential: card {before:.1f} -> "
              f"{(total - free) / 1e9:.1f} / {total / 1e9:.1f}GB in use, torch "
              f"reserved {torch.cuda.memory_reserved() / 1e9:.1f}GB", flush=True)
    pipe.enable_sequential_cpu_offload(device="cuda")
    return "split(model->sequential)"


def _render_with(a, transformer, parts, dist, w, h) -> int:
    """The half that is identical whichever transformer was loaded."""
    import torch

    # ASSEMBLE ONCE, RENDER N TIMES. Everything below the pipeline construction was
    # already per-clip; the only thing that made it per-PROCESS was that nothing
    # asked it twice. So the split is by cost, not by tidiness: _build_pipe holds
    # what an episode pays for once (12.7GB of connectors, the vae, the offload
    # hooks, and — with --fp8-layerwise — the 139s cast that already happened up in
    # stage_render), and _render_one holds what each beat genuinely repeats.
    # THE BREAK-EVEN IS FOUR CLIPS on the screened fp8 recipe (73.3s of sample
    # against ~230s of load+cast); at fifteen it is the difference between ~78
    # minutes and ~25.
    pipe = _build_pipe(a, transformer, parts, dist)
    jobs = _jobs_for(a, "render")
    for i, ja in enumerate(jobs, 1):
        if i > 1:
            # PER-BEAT PEAKS, from beat 2 on. Beat 1's peak legitimately contains
            # the load this loop exists to amortise, and leaving the counters alone
            # for it keeps a single-beat run's numbers exactly what they have always
            # been. From beat 2 the interesting quantity is what THAT beat cost, so
            # the torch high-water mark is reset and the host baseline re-read —
            # otherwise every later sidecar would inherit beat 1's load peak and the
            # bench file would read as fifteen identical measurements.
            if torch.cuda.is_available():
                torch.cuda.reset_peak_memory_stats()
            m = _mem()
            PEAK["commit_gb"] = m.get("commit_gb", 0.0)
            PEAK["phys_gb"] = m.get("phys_gb", 0.0)
        if len(jobs) > 1:
            print(f"[job {i}/{len(jobs)}] beat {ja.beat:02d} seed {ja.seed} "
                  f"-> {ja.out}", flush=True)
        rc = _render_one(ja, pipe, w, h)
        if rc:
            # STOP, do not carry on to beat i+1. A non-zero here is a shape or a
            # batch assertion, i.e. something true of the RECIPE — the remaining
            # beats would fail the same way, slowly, and bury the first failure
            # under fourteen repetitions of itself.
            print(f"!! job {i}/{len(jobs)} (beat {ja.beat}) returned {rc} — "
                  f"stopping, {len(jobs) - i} beat(s) not attempted", flush=True)
            return rc
    return 0


def _build_pipe(a, transformer, parts, dist):
    """The components and the offload strategy: paid once per PROCESS, not per clip.

    Lifted out of _render_with unchanged when --jobs arrived. Nothing here depends
    on which beat is about to render — the conditioning still, the embeddings and
    the seed all arrive later, in _render_one — which is exactly why an episode
    can pay for it once.
    """
    import torch
    from diffusers import (AutoencoderKLLTX2Audio, AutoencoderKLLTX2Video,
                           FlowMatchEulerDiscreteScheduler,
                           LTX2ImageToVideoPipeline)
    from diffusers.pipelines.ltx2.connectors import LTX2TextConnectors
    from diffusers.pipelines.ltx2.vocoder import LTX2VocoderWithBWE

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

    # SEQUENTIAL IS STILL THE DEFAULT, and the reason it ever was is VRAM rather
    # than host RAM. model_cpu_offload moves one WHOLE component to the GPU at a
    # time; the bf16 transformer is 37.99GB in 8 shards against 24GB of VRAM, so it
    # can never be resident and the call would OOM on the first denoise step no
    # matter how much host RAM is free. (The distilled model card's example uses
    # enable_model_cpu_offload because it assumes a card that fits the model.)
    # Sequential streams module-by-module instead, which fits at the cost of speed —
    # so a sample time measured under it is an offloading number, not this card's
    # ceiling, and is not comparable to a Wan row that ran resident.
    #
    # WHAT --offload IS FOR. That whole argument is an argument about 38GB, and
    # --fp8-layerwise makes the transformer ~19.8GiB of storage instead, which a
    # 23.89GiB card can hold. So the three modes are:
    #   sequential  enable_sequential_cpu_offload — leaf-level streaming, every
    #               module moved on every forward. What has always run; the only
    #               mode that fits the un-cast bf16 transformer. DEFAULT, so an
    #               invocation that does not ask for anything renders exactly the
    #               clip it rendered yesterday.
    #   model       enable_model_cpu_offload — the transformer goes to the card once
    #               and STAYS there for the whole denoise loop (the model_cpu_offload_seq
    #               chain "text_encoder->connectors->transformer->vae->audio_vae->vocoder"
    #               only evicts it when the vae runs). This is the point of the fp8
    #               cast, and it is a knife edge: ~19.8GiB of weights plus ~4GB of
    #               activations on a 23.89GiB card. It OOMs without --fp8-layerwise.
    #   split       model offload through stage 1 and the upsampler, then a switch to
    #               sequential for stage 2. THE MEASUREMENT THAT ASKED FOR IT, taken
    #               2026-08-04/05 with --fp8-layerwise --offload model: stage 1
    #               (352x640, 8 steps) runs 2.2 s/step at batch 2 against batch 1's
    #               1.3 — real work per second, a resident card being fed — while
    #               stage 2 (704x1280, 3 steps) pins the same card at 98.6% and
    #               spills, which is the WDDM signature that bugchecked the host.
    #               `sequential` fits stage 2 but streams stage 1 too, and pays for
    #               it. So the fast mode is right for one stage and wrong for the
    #               other, and the resolution is not a compromise between them but a
    #               switch at the boundary. Requires --two-stage (that boundary is
    #               the only place the switch can happen) and wants --fp8-layerwise
    #               for the same reason `model` does. See _switch_to_sequential.
    #   group       enable_group_offload(block_level, num_blocks_per_group=1,
    #               use_stream=True, record_stream=True) — the documented middle
    #               ground: whole transformer blocks move instead of leaves, and the
    #               next block onloads on a side stream while the current one
    #               computes.
    #               BROKEN ON THIS PIPELINE as of diffusers 0.39.0 — measured
    #               2026-08-05, probe-ltx-fp8-b2-group.log, rc=1 in 129s. It had
    #               been described here as "the fallback if `model` OOMs"; it is
    #               not, and it never ran. GroupOffloadingHook installs a
    #               `pre_forward` hook and only that (diffusers/hooks/
    #               group_offloading.py:368,388), so a module's weights onload when
    #               its `forward` runs — but the image conditioning goes through
    #               `vae.encode`, which is not `forward`. prepare_latents then hands
    #               a CUDA tensor to a CPU VAE and raises "Input type
    #               (CUDABFloat16Type) and weight type (CPUBFloat16Type) should be
    #               the same", before step 0 and independent of batch size.
    #               Fixing it means onloading the vae by hand around the encode;
    #               nobody has, so treat this mode as unavailable, not as a fallback.
    # NOT COMBINABLE, and diffusers enforces it rather than us: enable_model_cpu_offload
    # calls _maybe_raise_error_if_group_offload_active(raise_error=True), so the
    # branch below is an if/elif by the library's own rule.
    #
    # Host RAM for reference: ~52.5GB of bf16 weights (transformer 37.99 +
    # connectors 12.69 + vae 1.45 + vocoder 0.26 + audio_vae 0.11) against 68.1GB,
    # with the encoder already exited — which is exactly why the two-stage split
    # exists. VAE tiling stays on in every mode: it keeps the 704x1280 decode off
    # the peak, and it matters MORE with a resident transformer, because then the
    # decode is competing for the card instead of arriving after the weights have
    # drained off it. LTX2ImageToVideoPipeline does not inherit StableDiffusionMixin,
    # so pipe.enable_vae_tiling does not exist here and the vae's own enable_tiling
    # is what runs — the loop tries both because that is not worth depending on.
    mark(f"offload-setup-{a.offload}")
    if a.offload in ("model", "split"):
        # `split` STARTS as `model` and stops being it at the stage seam. Nothing
        # here needs to know which one it is; _switch_to_sequential does the rest.
        pipe.enable_model_cpu_offload(device="cuda")
    elif a.offload == "group":
        pipe.enable_group_offload(onload_device=torch.device("cuda"),
                                  offload_device=torch.device("cpu"),
                                  offload_type="block_level",
                                  num_blocks_per_group=1,
                                  use_stream=True, record_stream=True)
    else:
        pipe.enable_sequential_cpu_offload(device="cuda")
    for enable in (getattr(pipe, "enable_vae_tiling", None),
                   getattr(getattr(pipe, "vae", None), "enable_tiling", None)):
        if callable(enable):
            enable()
            break
    return pipe


def _render_one(a, pipe, w, h) -> int:
    """ONE beat on an already-loaded pipeline: still in, clip and sidecar out.

    `a` is the beat's own namespace — under --jobs a copy of the parsed args with
    init/out/embeds/prompt/negative/seed/beat replaced, so every line below reads
    exactly the attribute it always read and a single-beat run takes the identical
    path with the identical values.

    THE WRAPPING AND UNWRAPPING OF pipe.vae.decode IS BALANCED, which is what makes
    this safe to call in a loop: both halves are behind `if a.decode_frame0_out`,
    so the second beat captures the real bound method and never a wrapper left on
    by the first.
    """
    import torch
    from diffusers.utils import load_image

    # THE CAPTURE IS A PASS-THROUGH AND IT IS OFF BY DEFAULT, both deliberately.
    # An invocation that does not ask for --decode-frame0-out never installs this,
    # so the graph that produced every previous clip is untouched; and when it is
    # installed it records its argument and calls straight through, so the clip
    # this run exports is the clip it would have exported anyway. Taking the
    # latents HERE rather than re-running the pipeline at output_type="latent" is
    # what keeps the sample comparable: the same denoise, the same decode, one
    # extra decode afterwards.
    #
    # vae.decode is where the pipeline hands over 5-D DEnormalised latents plus
    # the decode timestep (pipeline_ltx2_image2video.py:1572). audio_vae is a
    # different object, so nothing here touches the audio path.
    cap: dict = {}
    _vae_decode = pipe.vae.decode
    if a.decode_frame0_out:
        def _capturing_decode(latents, *args, **kw):
            # last write wins: on the two-stage path stage 1 and the upsampler
            # both run at output_type="latent" and never decode, so this is the
            # decode that made the exported pixels either way.
            cap["latents"] = latents.detach().clone()
            cap["args"], cap["kw"] = args, kw
            return _vae_decode(latents, *args, **kw)
        pipe.vae.decode = _capturing_decode

    e = torch.load(a.embeds, map_location="cpu")
    init = a.init
    if a.image_crf:
        # BESIDE THE EMBEDS, NOT BESIDE THE CLIP, and the difference is a bug that
        # only appears once this renderer is reachable from the queue. The clip's
        # directory used to be SAMPLES/ on a hand-fired probe; through video_task it
        # is `courier.out`, and Courier.mark() runs `git add -A farm-out` + commit +
        # push on every finished beat. Leaving the round-trip intermediates there
        # would push ~600KB of throwaway per beat onto the courier branch, with the
        # last beat's pair sitting in the delivery folder looking like output. The
        # embeds path is a scratch location by construction on every caller — the
        # per-episode work dir under video_task.ROOT for a --jobs run, the
        # operator's own file otherwise — so it is the honest place for them.
        init = _crf_roundtrip(init, a.image_crf, str(Path(a.embeds).parent),
                              tag=f"-{a.beat:02d}")
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

    # STG, AND THE ONLY LINE IN THIS FUNCTION THAT CAN TOUCH IT. `stg_kwargs`
    # returns {} unless --stg-scale was given a positive value, so on every run
    # that does not ask for STG `common` is the identical dict it was before this
    # block existed and `pipe()` is called with the identical arguments. The
    # update applies to BOTH stages of the two-stage recipe, which is the shape
    # upstream's own dev config uses (first_pass stg_scale [0,0,4,4,4,2,1],
    # second_pass [1]) — one number, both passes, rather than a schedule we would
    # be inventing. See stg_kwargs for the sources and the recommended values.
    stg = stg_kwargs(getattr(a, "stg_scale", 0.0), getattr(a, "stg_blocks", ""))
    if stg:
        common.update(stg)
        # Printed only when it is on, so the default run's stdout is unchanged
        # too. A recipe change that does not announce itself in the log is one
        # nobody can attribute a look to afterwards.
        print("STG ON: stg_scale=%g blocks=%s (one extra transformer forward per "
              "step; applies to both stages)"
              % (stg["stg_scale"], stg["spatio_temporal_guidance_blocks"]),
              flush=True)

    # WHAT THE RECORD WILL SAY. Every mode but `split` names itself, and `split` is
    # only allowed to name itself once the switch has actually executed — hence the
    # assignment from _switch_to_sequential's return rather than from a.offload.
    offload_ran = a.offload

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

        # THE SEAM. Everything resident up to here — stage 1 and the upsampler are
        # what the fast mode is fast at — and everything streamed from here, because
        # 704x1280 with 19.8GiB of weights on the card is the combination that
        # spilled. up_lat stays where it is: it is the one thing that has to cross
        # the switch, and at 704x1280x65 it is ~20MB per slot of latents, not weights.
        if a.offload == "split":
            offload_ran = _switch_to_sequential(pipe, up.latent_upsampler)

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
    # THE SIDECAR NAMES THE ARTIFACT, and an fp8-cast transformer is a different
    # artifact from the bf16 one even though it came from the same files on disk:
    # the weights that produced these pixels were 8-bit in storage and upcast per
    # layer. Same repo, same licence document, different numerics — so it gets its
    # own MODEL_LICENCE key rather than sharing the bf16 one and letting a reader
    # assume the look is attributable to the stock checkpoint.
    vmodel = "ltx23-distilled-fp8" if a.fp8_layerwise else "ltx23-distilled"
    negative = sidecar_negative(a.negative, a.guidance)

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
            path, vmodel,
            {"worker": a.worker, "guidance": a.guidance,
             "seed_base": a.seed + s - a.beat, "id": a.task},
            beat=a.beat, seconds=round(clip_s, 3), steps=steps_note,
            size=a.size, prompt=a.prompt,
            # Recorded verbatim, with the "inert" caveat attached ONLY when this
            # run's guidance actually disabled the uncond pass — see
            # sidecar_negative. A reader cannot otherwise tell whether the
            # negative bit, and until 2026-08-16 the caveat said it never did.
            negative=negative,
            # offload and quantisation go in the SIDECAR and nowhere else. They are
            # not bench_row fields and must not become them: BENCH_FIELDS is one
            # schema shared with wan_i2v, bench_row() RAISES on an unknown key, and
            # a column that only one renderer ever fills is how a comparison table
            # starts reading as a gap. quantisation is omitted entirely on the bf16
            # path — write_sidecar drops None values, and an absent field reads as
            # "not quantised", which is exactly true.
            extra={"mode": a.mode, "batch": batch, "batch_slot": s,
                   "offload": offload_ran,
                   # PROVENANCE §7.2: an STG clip is a different artifact from a
                   # clip of the same prompt and seed without it — a second
                   # perturbed forward per step entered every update. None on the
                   # default path, and write_sidecar OMITS None, so a run that did
                   # not ask for STG writes the byte-identical sidecar it always
                   # did and an absent field reads as "no STG", which is true.
                   "stg": ("scale %g blocks %s"
                           % (stg["stg_scale"],
                              ",".join(str(b) for b in
                                       stg["spatio_temporal_guidance_blocks"]))
                           if stg else None),
                   "quantisation": ("fp8-layerwise storage / bf16 compute"
                                    if a.fp8_layerwise else None),
                   "throughput_s_video_per_s_wall":
                       round(batch * clip_s / sample_s, 4),
                   "compute_s_per_video_s": round(sample_s / batch / clip_s, 1)})
    # THE RIDERS RUN AFTER THE CLIP IS ON DISK, so a failure in either one cannot
    # cost the sample: the file the run exists to produce is already written and
    # its sidecar with it. Both are slot 0 only — they answer questions about a
    # recipe, not about a batch, and this renderer's batch is a throughput probe
    # whose slots differ by noise alone.
    if a.lossless_out:
        _write_lossless(video[0], a.lossless_out, a.fps)

    # THE DECODE IS ONE CALL, so this release is per-batch and not per-slot, and
    # saying otherwise would be a comment describing code that does not exist:
    # output_type="np" makes postprocess_video stack all N clips into a single
    # [N, F, H, W, C] array, and a row of a stacked array cannot be freed on its
    # own. What CAN be done is drop the whole thing before the bench write instead
    # of at function exit — at 704x1280/61f that is ~165MB per slot of host RAM,
    # and host RAM is what killed the b4 probe on 2026-08-05.
    del video, audio
    gc.collect()

    # AFTER the release above, and that ordering is the whole reason this is not
    # up with the lossless rider: the replica decode allocates a SECOND full
    # [F,H,W,C] float array, and at 121 frames of 544x960 that is ~0.76GB against
    # a host peak this recipe already measures in the high fifties of 68.1GB.
    # Freeing the first one first costs nothing and keeps the two from overlapping.
    if a.decode_frame0_out:
        pipe.vae.decode = _vae_decode          # un-wrap before replaying it
        _decode_frame0_replica(pipe, _vae_decode, cap, a.decode_frame0_out, a.fps)
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
    # "offload" WAS THE STRING "sequential" until 2026-08-05, written when there was
    # only one path through the code above. The moment a second one existed that
    # literal became a line that says what the file used to do — so it reads the
    # strategy the branch actually took, which for `split` is the composite name the
    # switch itself returned and not the word on the command line. Same for
    # quantisation, which is null on the bf16 path rather than absent, because this
    # line is a fixed-shape record.
    print(json.dumps({"sample_s": round(sample_s, 1), "peak_gb": round(peak, 1),
                      "peak_commit_gb": round(PEAK["commit_gb"], 1),
                      "frames": a.frames, "size": a.size, "steps": steps_note,
                      "batch": batch, "mode": a.mode,
                      "throughput_s_per_s": round(batch * clip_s / sample_s, 4),
                      "two_stage": bool(a.two_stage), "image_crf": a.image_crf,
                      "offload": offload_ran,
                      "quantisation": ("fp8-layerwise storage / bf16 compute"
                                       if a.fp8_layerwise else None)}),
          flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["encode", "render"], required=True)
    # NO LONGER required=True, and only because --jobs names one per beat. Without
    # --jobs it is still mandatory — enforced below rather than by argparse, so the
    # message can say which of the two forms is missing.
    ap.add_argument("--embeds", default="")
    # ONE MODEL LOAD, N BEATS — the flag wan_i2v.py already has, spelled the same
    # way for the same reason. A json list of per-beat objects; see _jobs_for for
    # the keys and for why the prompts are file paths and not strings.
    ap.add_argument("--jobs", default="",
                    help="json list of per-beat objects (embeds, prompt_file, "
                         "negative_file, init, out, seed, beat) rendered in one "
                         "process on one model load")
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
    # SPATIOTEMPORAL GUIDANCE. Both default to OFF and the default is 0.0/"" so
    # that stg_kwargs returns {} and the pipe() call is untouched — see
    # stg_kwargs for why "off" is an empty dict rather than an explicit zero, and
    # for the maintainer quote and upstream config that motivate the lever at all.
    ap.add_argument("--stg-scale", type=float, default=0.0,
                    help="spatiotemporal guidance scale; 0 (default) = OFF and "
                         "no STG argument is passed at all. Upstream's own "
                         "docstring suggests 1.0 for LTX-2.3. Costs one extra "
                         "transformer forward per step.")
    ap.add_argument("--stg-blocks", default="",
                    help="comma- or space-separated zero-indexed transformer "
                         "block indices to apply STG at. REQUIRED whenever "
                         "--stg-scale is positive; upstream recommends 28 for "
                         "LTX-2.3 (29 for LTX-2.0).")
    ap.add_argument("--distilled-sigmas", action="store_true")
    # Retained, not removed: the 9GB fp8 partial is still on disk against a future
    # torchao / torch._scaled_mm path. It refuses immediately on this diffusers.
    # NOT overloaded to mean the layerwise cast, and that is deliberate — its
    # refusal message is the record of a measured dead end, and a flag that used to
    # print "this does not work" and now quietly does something else is how a
    # retracted finding gets un-retracted by accident.
    ap.add_argument("--fp8-single-file", action="store_true",
                    help="BROKEN on diffusers 0.39.0 — see module docstring")
    # The OTHER fp8: no download, no foreign checkpoint. Cast the bf16 weights we
    # already load to fp8 for storage, upcast per layer for compute. Off by default
    # because it changes the numerics of a screened look, and because the offload
    # mode it unlocks is a knife-edge fit.
    ap.add_argument("--fp8-layerwise", action="store_true",
                    help="cast the loaded transformer to fp8 storage / bf16 compute "
                         "(~38GB -> ~19.8GiB), which is what lets --offload model fit")
    ap.add_argument("--offload", choices=["sequential", "model", "split", "group"],
                    default="sequential",
                    help="sequential (default, unchanged behaviour): leaf-level "
                         "streaming, fits the un-cast bf16 transformer. model: "
                         "transformer resident for the whole denoise loop, needs "
                         "--fp8-layerwise. split: model through stage 1 and the "
                         "upsampler, sequential for the 704x1280 stage 2 that "
                         "spills under model; needs --two-stage. group: block_level "
                         "with a prefetch stream, BROKEN on this pipeline.")
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
    # --- two diagnostic riders. Both default OFF and both are pure additions to
    # a run that was going to happen anyway: no extra sample, no second recipe,
    # no change to the exported clip. Empty string = don't.
    ap.add_argument("--lossless-out", default="",
                    help="also write slot 0's frames to this path at x264 -qp 0 "
                         "yuv444p, so a cadence question can be asked of the "
                         "frames instead of of the ~1 Mbps default encode")
    ap.add_argument("--decode-frame0-out", default="",
                    help="also decode this run's own latents a second time with "
                         "latent frame 0 replicated across every latent position; "
                         "coloured output puts a colour collapse in the latents, "
                         "grey output puts it in the VAE decoder")
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
    if not a.jobs and not a.embeds:
        print("!! --embeds is required unless --jobs names one per beat",
              flush=True)
        return 2
    # REFUSED, because the two flags mean opposite things about the seed. --batch N
    # is a THROUGHPUT PROBE: N clips from one sample call, same prompt, same still,
    # differing only by seed+slot. --jobs is an EPISODE: N different beats, each
    # with its own still and its own prompt. Together they would ask for N slots of
    # every beat, writing slot paths derived from a per-beat seed — measurable
    # neither as a probe nor usable as an episode. Nothing needs the combination, so
    # it stops here instead of producing a folder nobody can interpret.
    if a.jobs and a.batch > 1:
        print(f"!! --jobs with --batch {a.batch}: --batch is the throughput probe "
              "(N seeds of ONE beat) and --jobs is the episode (N beats). Pick one.",
              flush=True)
        return 2
    # LOUD, NOT FATAL. 38GB of bf16 weights cannot be resident on a 23.89GiB card,
    # so this combination is an OOM with a long walk up to it — ~90 seconds of
    # loading before the first denoise step raises. It is not refused, because the
    # OOM itself is a legitimate thing to go and measure on a bigger card; it is
    # announced, because reading it in a traceback teaches nothing.
    if a.stage == "render" and a.offload in ("model", "split") and not a.fp8_layerwise:
        print(f"!! --offload {a.offload} without --fp8-layerwise: the bf16 "
              "transformer is ~38GB and the card is 23.89GiB, so this is expected "
              "to OOM at the first denoise step. Continuing because you asked.",
              flush=True)
    # REFUSED, not warned, and the difference is what the wrong answer costs. `model`
    # without the cast is an OOM: a traceback, ninety seconds in, that teaches the
    # thing it says. `split` without --two-stage has no stage boundary to switch at,
    # so it would silently render the ENTIRE single-stage 704x1280 denoise resident —
    # which is precisely the configuration measured at 98.6% and a host bugcheck on
    # 2026-08-05. A flag whose failure mode is "takes the machine down while doing
    # exactly what you told it not to" is one to refuse at parse time.
    if a.stage == "render" and a.offload == "split" and not a.two_stage:
        print("!! --offload split needs --two-stage: the switch happens AT the "
              "stage-1/stage-2 boundary, and a single-stage run has none. Without "
              "it this would render all of 704x1280 resident, which is the "
              "configuration that spilled and bugchecked the host.", flush=True)
        return 2
    # REFUSED AT PARSE TIME, not ninety seconds into a weight load. The pipeline
    # makes the same check in check_inputs, but only after the transformer is
    # resident; here it costs nothing and the message names the recommended
    # block. Calling stg_kwargs is the check — it is the same function the render
    # will call, so the two cannot disagree.
    try:
        _stg = stg_kwargs(a.stg_scale, a.stg_blocks)
    except ValueError as exc:
        print("!! %s" % exc, flush=True)
        return 2
    if a.stage == "render":
        print(f"recipe: offload={a.offload} "
              f"quantisation={'fp8-layerwise' if a.fp8_layerwise else 'none (bf16)'}",
              flush=True)
        if _stg:
            print("recipe: STG stg_scale=%g blocks=%s"
                  % (_stg["stg_scale"],
                     _stg["spatio_temporal_guidance_blocks"]), flush=True)
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
