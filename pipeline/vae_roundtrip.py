"""L2: LTX-2.3 VAE encode->decode round trip, tiling ON vs OFF. No denoiser, no generation.

Source is a REAL image panned at a known constant velocity, so the ground-truth
per-frame displacement is a flat line (dx px/frame) and any staircase in the output
was put there by the VAE.

Metrics (both computed on the SOURCE too, as the control):
  * per-pair mean absolute luma difference at 1/8 scale, then autocorrelation of the
    mean-removed series at lags 1..8 -- peak lag IS the hold period
  * per-pair displacement by 1-D cross-correlation of row/column profiles (alignment,
    not eyeball): ground truth is exactly dx every pair

RUN IT (box, video venv -- torch is imported lazily so this file is import-safe):

    C:/banyan-video/venv/Scripts/python.exe pipeline/vae_roundtrip.py \
        --mode pan --width 704 --height 1280 --frames 97 --dx 4 \
        --arms dec_off,dec_on,both_on --memfrac 0.4

`--hold 3` is the POSITIVE CONTROL: it holds the source at a known period before
encoding, so a run that reports nothing can be shown to be capable of reporting
something. Never trust a negative from this harness without it.
"""
import argparse, gc, json, sys, time
from pathlib import Path

import numpy as np
from PIL import Image

PARTS_REPO = "diffusers/LTX-2.3-Diffusers"


def log(*a):
    print(*a, flush=True)


def build_source(plate, W, H, F, dx, axis):
    """[F,H,W,3] uint8 -- a real plate translated dx px per frame along `axis`."""
    pan = dx * (F - 1)
    if axis == "y":
        sw, sh = W, H + pan
    else:
        sw, sh = W + pan, H
    img = Image.open(plate).convert("RGB")
    # centre-crop to the target aspect first so the resize does not squash it
    ar = sw / sh
    w0, h0 = img.size
    if w0 / h0 > ar:
        nw = int(round(h0 * ar)); img = img.crop(((w0 - nw) // 2, 0, (w0 - nw) // 2 + nw, h0))
    else:
        nh = int(round(w0 / ar)); img = img.crop((0, (h0 - nh) // 2, w0, (h0 - nh) // 2 + nh))
    big = np.asarray(img.resize((sw, sh), Image.LANCZOS), dtype=np.uint8)
    out = np.empty((F, H, W, 3), dtype=np.uint8)
    for t in range(F):
        if axis == "y":
            out[t] = big[t * dx: t * dx + H, :, :]
        else:
            out[t] = big[:, t * dx: t * dx + W, :]
    return out


def build_fade(plateA, plateB, W, H, F):
    """Linear cross-fade A->B: every frame is NEW content, at a constant rate.

    Ground truth per-pair difference is a flat line. Any temporal quantisation in the
    VAE turns that line into a staircase, which is exactly the reported symptom.
    """
    def prep(p):
        im = Image.open(p).convert("RGB")
        w0, h0 = im.size
        ar = W / H
        if w0 / h0 > ar:
            nw = int(round(h0 * ar)); im = im.crop(((w0 - nw) // 2, 0, (w0 - nw) // 2 + nw, h0))
        else:
            nh = int(round(w0 / ar)); im = im.crop((0, (h0 - nh) // 2, w0, (h0 - nh) // 2 + nh))
        return np.asarray(im.resize((W, H), Image.LANCZOS), dtype=np.float32)
    A, B = prep(plateA), prep(plateB)
    out = np.empty((F, H, W, 3), dtype=np.uint8)
    for t in range(F):
        a = t / (F - 1)
        out[t] = np.clip(A * (1 - a) + B * a, 0, 255).astype(np.uint8)
    return out


def build_synth(W, H, F, dx, axis, seed=7):
    rng = np.random.default_rng(seed)
    pan = dx * (F - 1)
    sw, sh = (W, H + pan) if axis == "y" else (W + pan, H)
    base = rng.integers(60, 90, size=(sh, sw, 3), dtype=np.uint8)          # textured floor
    yy, xx = np.mgrid[0:sh, 0:sw]
    bars = (((xx // 37) + (yy // 53)) % 2).astype(np.uint8) * 120           # hard edges
    disc = (((xx - sw // 2) ** 2 + (yy - sh // 2) ** 2) < (min(sw, sh) // 6) ** 2).astype(np.uint8) * 90
    big = np.clip(base.astype(np.int16) + bars[..., None] + disc[..., None], 0, 255).astype(np.uint8)
    out = np.empty((F, H, W, 3), dtype=np.uint8)
    for t in range(F):
        out[t] = big[t * dx: t * dx + H, :, :] if axis == "y" else big[:, t * dx: t * dx + W, :]
    return out


# ---------------------------------------------------------------- metrics
def luma(frames):
    f = frames.astype(np.float32)
    return 0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2]


def down8(y):
    F, H, W = y.shape
    h, w = H // 8 * 8, W // 8 * 8
    return y[:, :h, :w].reshape(F, h // 8, 8, w // 8, 8).mean(axis=(2, 4))


def pair_diffs(frames):
    y = down8(luma(frames))
    return np.abs(np.diff(y, axis=0)).mean(axis=(1, 2))


def autocorr(d, maxlag=8):
    x = d - d.mean()
    den = float((x * x).sum())
    if den <= 0:
        return {k: 0.0 for k in range(1, maxlag + 1)}
    return {k: float((x[:-k] * x[k:]).sum() / den * len(x) / max(1, len(x) - k))
            for k in range(1, maxlag + 1)}


def shifts(frames, axis, search=24):
    """Per-pair displacement in px by 1-D cross-correlation of the profile along `axis`.

    Ground truth for a pan is dx on every pair. A hold shows up as 0,0,3dx ...
    """
    y = luma(frames)
    prof = y.mean(axis=2) if axis == "y" else y.mean(axis=1)   # [F, H] or [F, W]
    prof = prof - prof.mean(axis=1, keepdims=True)
    out = []
    n = prof.shape[1]
    for t in range(len(prof) - 1):
        a, b = prof[t], prof[t + 1]
        best, bl = -1e18, 0
        for s in range(-search, search + 1):
            if s >= 0:
                v = float((a[s:] * b[:n - s]).sum()) if s < n else 0.0
                lo, hi = s, n
            else:
                v = float((a[:n + s] * b[-s:]).sum())
                lo, hi = 0, n + s
            v /= max(1, hi - lo)
            if v > best:
                best, bl = v, s
        out.append(float(bl))
    return out


def depth(d, period):
    """trough/peak: the mean of the QUIET pairs over the mean of the LOUD ones.

    This is the number `hold_period`'s strength cannot supply. Autocorrelation is
    scale-free by design, so a +-3% ripple with a clean period reads 0.90 exactly
    like a freeze does. Depth says how deep the hold is:
        0815-b13-AFTER.mp4  period 3  strength 0.96  depth 0.029  <- real hold
        0814-b06-DONE.mp4   period 6  strength 0.65  depth 0.181  <- real hold
        0815-b02-FIXED.mp4  period 2  strength 0.96  depth 0.431  <- pulsing, not frozen
        this VAE round trip  period 2  strength 0.90  depth 0.971  <- NOT a hold
    """
    if not period or period < 2:
        return None
    d = np.asarray(d, dtype=float)
    idx = np.arange(len(d))
    means = [d[idx % period == k].mean() for k in range(period)]
    lk = int(np.argmax(means))
    loud = d[idx % period == lk]
    quiet = np.concatenate([d[idx % period == k] for k in range(period) if k != lk])
    return float(quiet.mean() / loud.mean()) if loud.mean() > 0 else None


def strip(frames, idx, box, path, zoom=2):
    """Small visual artifact: a crop of the SAME window across consecutive frames."""
    y0, x0, h, w = box
    tiles = [Image.fromarray(frames[i][y0:y0 + h, x0:x0 + w]) for i in idx]
    W = w * len(tiles)
    sheet = Image.new("RGB", (W, h), "black")
    for k, t in enumerate(tiles):
        sheet.paste(t, (k * w, 0))
    sheet = sheet.resize((W * zoom, h * zoom), Image.NEAREST)
    sheet.save(path)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plate", default="C:/banyan-farm/cond-crf.png")
    ap.add_argument("--plate-b", default="C:/banyan-farm/01-the-keyboard.png")
    ap.add_argument("--mode", default="pan", choices=["pan", "fade", "synth"])
    ap.add_argument("--tag", default="")
    ap.add_argument("--box", default="", help="y0,x0,h,w crop for the visual strip")
    ap.add_argument("--synth", action="store_true")
    ap.add_argument("--width", type=int, default=544)
    ap.add_argument("--height", type=int, default=960)
    ap.add_argument("--frames", type=int, default=49)
    ap.add_argument("--dx", type=int, default=4)
    ap.add_argument("--axis", default="y", choices=["y", "x"])
    ap.add_argument("--out", default="C:/banyan-farm/vaert")
    ap.add_argument("--arms", default="dec_off,dec_on,both_on")
    ap.add_argument("--memfrac", type=float, default=0.55)
    ap.add_argument("--hold", type=int, default=0,
                    help="POSITIVE CONTROL: repeat every Nth source frame N times before "
                         "encoding, so the harness is shown a known hold of exactly this period")
    a = ap.parse_args()

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.mode == "synth" or a.synth:
        src = build_synth(a.width, a.height, a.frames, a.dx, a.axis)
    elif a.mode == "fade":
        src = build_fade(a.plate, a.plate_b, a.width, a.height, a.frames)
    else:
        src = build_source(a.plate, a.width, a.height, a.frames, a.dx, a.axis)
    if a.hold > 1:
        src = src[[(i // a.hold) * a.hold for i in range(len(src))]]
        log(f"POSITIVE CONTROL: source held at period {a.hold}")
    log(f"SOURCE {src.shape} mode={a.mode} dx={a.dx}px/frame axis={a.axis} plate={a.plate}")
    box = ([int(v) for v in a.box.split(",")] if a.box
           else [a.height // 2 - 64, a.width // 2 - 64, 128, 128])
    tag = ("-" + a.tag) if a.tag else ""

    import torch
    from diffusers import AutoencoderKLLTX2Video
    from huggingface_hub import hf_hub_download
    parts = str(Path(hf_hub_download(PARTS_REPO, "model_index.json", local_files_only=True)).parent)
    torch.cuda.set_per_process_memory_fraction(a.memfrac)
    vae = AutoencoderKLLTX2Video.from_pretrained(parts, subfolder="vae",
                                                 torch_dtype=torch.bfloat16).to("cuda").eval()
    log(f"VAE loaded  spatial={vae.spatial_compression_ratio} temporal={vae.temporal_compression_ratio} "
        f"timestep_conditioning={vae.config.timestep_conditioning} "
        f"tile_min={vae.tile_sample_min_height}x{vae.tile_sample_min_width} "
        f"stride={vae.tile_sample_stride_height}x{vae.tile_sample_stride_width} "
        f"framewise_dec={vae.use_framewise_decoding}")

    x = torch.from_numpy(src).float().permute(3, 0, 1, 2)[None] / 127.5 - 1.0   # [1,3,F,H,W]
    x = x.to("cuda", torch.bfloat16)

    res = {"config": {"w": a.width, "h": a.height, "frames": a.frames, "dx": a.dx,
                      "axis": a.axis, "source": "synth" if a.synth else a.plate},
           "arms": {}}
    d = pair_diffs(src)
    res["arms"]["SOURCE"] = {"pair_diff_mean": float(d.mean()),
                             "pair_diff": [round(float(v), 4) for v in d],
                             "autocorr": {str(k): round(v, 3) for k, v in autocorr(d).items()},
                             "shifts": shifts(src, a.axis)}
    strip(src, list(range(12, 21)), box, out / f"strip{tag}-SOURCE.png")

    for arm in a.arms.split(","):
        enc_t = arm in ("both_on",)
        dec_t = arm in ("dec_on", "both_on")
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
        t0 = time.time()
        with torch.no_grad():
            vae.disable_tiling()
            if enc_t:
                vae.enable_tiling()
            z = vae.encode(x).latent_dist.mode()
            vae.disable_tiling()
            if dec_t:
                vae.enable_tiling()
            temb = torch.tensor([0.0], device="cuda", dtype=z.dtype) if vae.config.timestep_conditioning else None
            dec = vae.decode(z, temb, return_dict=False)[0]
        vid = ((dec.float() / 2 + 0.5).clamp(0, 1) * 255).round().to(torch.uint8)
        vid = vid[0].permute(1, 2, 3, 0).cpu().numpy()      # [F,H,W,3]
        peak = torch.cuda.max_memory_allocated() / 2**30
        del dec, z; gc.collect(); torch.cuda.empty_cache()
        dd = pair_diffs(vid)
        ac = autocorr(dd)
        sh = shifts(vid, a.axis)
        res["arms"][arm] = {"encode_tiled": enc_t, "decode_tiled": dec_t,
                            "latent_shape": None, "peak_gib": round(peak, 2),
                            "secs": round(time.time() - t0, 1),
                            "pair_diff_mean": float(dd.mean()),
                            "pair_diff": [round(float(v), 4) for v in dd],
                            "autocorr": {str(k): round(v, 3) for k, v in ac.items()},
                            "shifts": sh,
                            "psnr_vs_source": float(10 * np.log10(255.0 ** 2 / max(
                                1e-9, ((vid.astype(np.float32) - src.astype(np.float32)) ** 2).mean())))}
        peak_lag = max(ac, key=lambda k: ac[k])
        res["arms"][arm]["depth_at_peak_lag"] = depth(dd, peak_lag)
        log(f"ARM {arm}: enc_tiled={enc_t} dec_tiled={dec_t} peak={peak:.2f}GiB "
            f"{time.time()-t0:.0f}s  ac_peak_lag={peak_lag} ({ac[peak_lag]:.2f})  "
            f"depth={res['arms'][arm]['depth_at_peak_lag']}  "
            f"ac={{{', '.join(f'{k}:{v:.2f}' for k, v in ac.items())}}}")
        log(f"    shifts first 16: {sh[:16]}")
        strip(vid, list(range(12, 21)), box, out / f"strip{tag}-{arm}.png")
        Image.fromarray(vid[16]).save(out / f"frame16{tag}-{arm}.png")
        del vid; gc.collect()

    (out / f"metrics{tag}.json").write_text(json.dumps(res, indent=1))
    log("WROTE", out / f"metrics{tag}.json")
    log("RC 0")


if __name__ == "__main__":
    main()
