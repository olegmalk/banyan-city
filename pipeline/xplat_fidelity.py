#!/usr/bin/env python3
"""Cross-platform fidelity: does the same recipe on a different box give the same clip?

Same method as fp8-fidelity-20260805.log so the numbers are comparable to the
figures already on record: per-frame MSE/PSNR via ffmpeg's psnr filter, averaged
over frames, rms = sqrt(mse_avg) in 0-255 units. Validated against that log —
this harness reproduces its CTRL-crf23 row (mse_avg 0.8714, rms 0.933) exactly.

The controls matter more than the measurement: an h264 re-encode alone moves rms
by ~0.9, so a drift figure without its own encode-noise floor beside it means
nothing.

    python3 pipeline/xplat_fidelity.py <reference.mp4> <candidate.mp4>

Lives in `pipeline/` since 2026-08-05: it was written beside its first results in
`bench-platform/`, but it is a tool, not a result, and the 5070 Ti probe made it
the second caller. Its validation run is kept at
`bench-platform/xplat-harness-validation-20260805.txt`.
"""
import argparse
import array
import hashlib
import json
import math
import re
import subprocess
import tempfile
from pathlib import Path


def sh(cmd):
    # encoding NAMED, not inherited from the locale: ffmpeg's banner and error
    # text is not ASCII, and on the farm's Windows boxes the locale codec is
    # cp1252, where a decode failure silently sets .stdout to None on
    # subprocess's reader thread (see test_subprocess_reads_are_utf8). The raw
    # video reads below stay in BINARY mode — those are pixels, not text.
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def probe(p):
    r = sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
            "stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_frames,"
            "duration,bit_rate", "-of", "json", str(p)])
    return json.loads(r.stdout)["streams"][0]


def _stats(path):
    v = [float(m) for m in re.findall(r"mse_avg:([\d.]+)", Path(path).read_text())]
    return v


def psnr_pair(ref, cand, td):
    """Per-frame MSE averaged over frames — the documented method."""
    st = Path(td) / f"st-{abs(hash((str(ref), str(cand))))}.txt"
    sh(["ffmpeg", "-hide_banner", "-i", str(cand), "-i", str(ref),
        "-lavfi", f"psnr=stats_file={st}", "-f", "null", "-"])
    if not st.exists():
        return None
    v = _stats(st)
    if not v:
        return None
    mse = sum(v) / len(v)
    psnr = 10 * math.log10(255 ** 2 / mse) if mse > 0 else float("inf")
    return {"frames": len(v), "mse_avg": mse, "psnr": psnr, "rms": mse ** 0.5}


def reencode(src, out, crf=None, bitrate=None):
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", str(src), "-c:v", "libx264"]
    cmd += ["-crf", str(crf)] if crf is not None else ["-b:v", str(bitrate)]
    cmd += ["-pix_fmt", "yuv420p", str(out)]
    sh(cmd)
    return out


def consecutive_mse(p):
    """Frozen-frame detector: RGB MSE between frame n+1 and frame n.

    RGB rather than the psnr filter's YUV average: subsampled chroma planes drag
    that average to roughly half the RGB figure, and the frozen-frame threshold
    on record is in RGB units. The verdict (a count of frames under 0.5) is the
    same either way; only the absolute scale moves.
    """
    import numpy as np
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vf",
                        "format=rgb24", "-f", "rawvideo", "-"],
                       capture_output=True)
    if not r.stdout:
        return []
    s = probe(p)
    px = int(s["width"]) * int(s["height"]) * 3
    a = np.frombuffer(r.stdout, dtype=np.uint8).astype(np.float64)
    a = a[: len(a) // px * px].reshape(-1, px)
    return list(np.mean((a[1:] - a[:-1]) ** 2, axis=1))


def channel_means(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vf",
                        "format=rgb24", "-f", "rawvideo", "-"],
                       capture_output=True)
    if not r.stdout:
        return None
    a = array.array("B", r.stdout)
    n = len(a) // 3
    return sum(a[0::3]) / n, sum(a[1::3]) / n, sum(a[2::3]) / n


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("reference", help="the clip already on record")
    ap.add_argument("candidate", help="the clip to compare against it")
    # A recipe difference between the two clips does not stop the measurement, it
    # changes what the measurement MEANS — a tiled VAE decode against an untiled
    # one is not a pure platform comparison. Carry the caveat in the output file
    # rather than only in whatever prose happens to quote it.
    ap.add_argument("--note", default=None,
                    help="confound to record in the header (e.g. a decode-path "
                         "difference between the two clips)")
    a = ap.parse_args()
    ref, cand = Path(a.reference), Path(a.candidate)
    out = []
    w = out.append

    w("=" * 78)
    w("CROSS-PLATFORM FIDELITY — same recipe, same seed, two different GPUs")
    w(f"reference   : {ref}")
    w(f"candidate   : {cand}")
    if a.note:
        w(f"CONFOUND    : {a.note}")
    w("method      : per-frame MSE/PSNR via ffmpeg psnr filter, averaged over")
    w("              frames; rms = sqrt(mse_avg), in 0-255 units. Same method as")
    w("              fp8-fidelity-20260805.log; this harness reproduces that")
    w("              log's CTRL-crf23 row exactly (0.8714 / 0.933).")
    w("=" * 78)
    w("")
    w("== identity ==")
    hr, hc = sha256(ref), sha256(cand)
    for p, h in ((ref, hr), (cand, hc)):
        w(f"  {p.name:<52} {p.stat().st_size:>8} bytes  sha256={h[:16]}")
    w(f"  bit-identical across boxes: {'YES' if hr == hc else 'NO'}")
    w("")
    w("== stream properties ==")
    for p in (ref, cand):
        s = probe(p)
        w(f"  {p.name}:")
        for k in ("codec_name", "width", "height", "pix_fmt", "r_frame_rate",
                  "nb_frames", "duration", "bit_rate"):
            w(f"    {k}={s.get(k)}")
    w("")

    cb = probe(cand).get("bit_rate")
    with tempfile.TemporaryDirectory() as td:
        w("== controls (encode-generation noise floor) ==")
        w(f"  candidate measured bitrate: {cb} bps")
        c1 = psnr_pair(ref, reencode(ref, Path(td) / "c1.mp4", crf=23), td)
        w(f"  CTRL-crf23  ref vs its own re-encode    frames={c1['frames']}  "
          f"mse_avg={c1['mse_avg']:.4f}  psnr={c1['psnr']:.2f} dB  "
          f"rms={c1['rms']:.3f}/255")
        if cb:
            c2 = psnr_pair(ref, reencode(ref, Path(td) / "c2.mp4", bitrate=cb), td)
            w(f"  CTRL-br     ref vs re-encode @cand br   frames={c2['frames']}  "
              f"mse_avg={c2['mse_avg']:.4f}  psnr={c2['psnr']:.2f} dB  "
              f"rms={c2['rms']:.3f}/255")
        w("")
        w("== the measurement ==")
        m = psnr_pair(ref, cand, td)
        w(f"  XPLAT       candidate vs reference       frames={m['frames']}  "
          f"mse_avg={m['mse_avg']:.4f}  psnr={m['psnr']:.2f} dB  "
          f"rms={m['rms']:.3f}/255")
        ratio = m["rms"] / c1["rms"] if c1["rms"] else float("inf")
        w(f"  drift / encode-noise-control ratio: {ratio:.2f}x")
        w("")
        w("  For scale, the same metric on the figures already on record:")
        w("    fp8 vs bf16 (same box) .................. rms 11.93/255")
        w("    batch drift (b2 slot0 vs b1, same box) .. rms 10.35/255")
        w("    crf23 re-encode control ................. rms  0.93/255")
        w("")
        w("== frozen-frame check (consecutive-frame RGB MSE; near-zero = frozen) ==")
        for p in (ref, cand):
            v = consecutive_mse(p)
            if v:
                frozen = sum(1 for x in v if x < 0.5)
                w(f"  {p.name}")
                w(f"    pairs={len(v)}  consecutive-MSE min={min(v):.3f}  "
                  f"mean={sum(v)/len(v):.3f}  max={max(v):.3f}")
                w(f"    frames with consecutive-MSE < 0.5 (frozen): {frozen}")
    w("")
    w("== gross colour drift (per-channel mean over all frames) ==")
    cm_r, cm_c = channel_means(ref), channel_means(cand)
    if cm_r and cm_c:
        w("    channel      R        G        B")
        w(f"    reference   {cm_r[0]:.3f}   {cm_r[1]:.3f}   {cm_r[2]:.3f}")
        w(f"    candidate   {cm_c[0]:.3f}   {cm_c[1]:.3f}   {cm_c[2]:.3f}")
        w(f"    delta       {cm_c[0]-cm_r[0]:+.3f}   {cm_c[1]-cm_r[1]:+.3f}   "
          f"{cm_c[2]-cm_r[2]:+.3f}   (0-255 units)")
    w("")
    w("== end ==")
    print("\n".join(out))


if __name__ == "__main__":
    main()
