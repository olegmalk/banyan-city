#!/usr/bin/env python3
"""DID THE BODY MOVE? -- displacement between two frames, not cadence.

Written 2026-08-16 by the motion lane, because every number this investigation
has produced answers a different question than the one that matters.

================================================================================
WHY THIS EXISTS AND WHAT IT IS NOT
================================================================================
`hold_period.py` answers HOW OFTEN A NEW PICTURE ARRIVES. It replaced `cadence`,
which was structurally blind to odd hold periods, and it is correct at its job.
But six lanes have now moved the hold period around -- 3 to 2, 32 distinct
pictures to 48 -- and in EVERY arm of every one of them three independent
readers wrote the same sentence: the figure does not move its body. "At f0 and
f96 he is in the identical folded pose." "What changes between loud pairs is the
drawing being re-inked in place -- the shadow on the skull slides, the ear edge
redraws, grass reshuffles."

Re-inking in place is a large frame difference. It is a large MAD, a healthy
autocorrelation, a respectable distinct-picture count -- and it is not motion.
Every frame-difference metric we own scores it as though it were, which is the
same trap VBench documents when it requires static videos be filtered out
before `temporal_flickering` is read.

So this measures the one thing none of them do: HOW FAR DID THE CONTENT ACTUALLY
TRAVEL between frame A and frame B. A picture that is redrawn in place travels
zero pixels no matter how much it changes. A body that moves travels.

================================================================================
THE METHOD, IN ONE PARAGRAPH
================================================================================
Both frames are decoded to grayscale at 1/`scale`, high-pass filtered (each
pixel minus a local box mean) so a brightness or exposure change cannot pose as
motion, and then, for every integer shift in a +-`radius` window, the squared
difference between frame A and the shifted frame B is box-summed over every
block position at once with an integral image. Each block keeps the shift that
minimised its SSD. Blocks whose own high-pass energy is below `min_energy` are
DISCARDED rather than counted as still, because a patch of flat sky has no
displacement to measure and including it would dilute every fraction reported.
Displacements are scaled back to original-resolution pixels before reporting.

================================================================================
WHAT IT CANNOT SEE -- READ THIS BEFORE QUOTING A NUMBER
================================================================================
1. IT CANNOT TELL A CAMERA MOVE FROM A BODY MOVE. A dolly and a walk both
   translate content. That is why `global_shift` (the median displacement over
   all kept blocks) is reported SEPARATELY from `articulation_p90` (the 90th
   percentile of the displacement REMAINING after that global median is
   subtracted). Only the second is evidence that parts of the frame moved
   differently from each other, which is what a body doing something looks like.
   Even that is not proof: a rotating camera, a zoom, or parallax across depth
   planes all produce non-uniform fields with nothing acting in them.
2. IT SATURATES. Nothing beyond `radius` can be found, and a block that truly
   moved further will report a wrong smaller number or match on something else.
   `saturated_frac` reports how many blocks landed on the search boundary; if it
   is not near zero the radius was too small and the numbers are a floor.
3. A REDRAWN BLOCK CAN FIND A SPURIOUS MATCH. Anime line art is full of
   near-identical strokes and a redrawn cuff can match a neighbouring cuff.
   `confidence` (how much better the best shift is than staying put) is reported
   so a field of weak matches is visible as one.
4. IT IS A FILTER, NEVER A VERDICT. Same law as hold_period: open the frames.
   A number here that disagrees with the cold read means the number is wrong.

================================================================================
CALIBRATION
================================================================================
`--selftest` runs the metric against three synthetic pairs whose true answer is
known: a frozen pair, a pure translation by a known number of pixels, and a
"re-inked in place" pair -- the same picture with fresh noise and a local
contrast change but zero displacement. The third is the important one: it is the
failure mode this tool exists to catch, and a metric that reads motion there
would be worse than useless. All three assertions must pass.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


# ---------------------------------------------------------------- pure numeric
def _boxsum(x, k):
    """Sum over every kxk window. Shape (H-k+1, W-k+1). Integral image."""
    import numpy as np

    c = np.cumsum(np.cumsum(np.asarray(x, dtype=np.float64), axis=0), axis=1)
    c = np.pad(c, ((1, 0), (1, 0)))
    return c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]


def highpass(f, k=9):
    """Each pixel minus its local box mean: kills exposure, keeps structure.

    A DC change is exactly what guidance 1.0 produced -- 81 of 255 in frame-mean
    luma while the pose held -- so a displacement metric that let brightness in
    would have called that clip the most moving arm we have.
    """
    import numpy as np

    f = np.asarray(f, dtype=np.float64)
    pad = k // 2
    p = np.pad(f, pad, mode="edge")
    return f - _boxsum(p, k) / float(k * k)


def displacement_field(a, b, block=12, stride=6, radius=32, min_energy=3.0):
    """Best (dy, dx) for every textured block of `a` found in `b`.

    Returns (dy, dx, kept, conf) as flat arrays over the kept blocks, in the
    resolution the arrays were given at. Search is exhaustive over the integer
    shifts in [-radius, radius]^2 -- no pyramid, no interpolation, no subpixel.
    """
    import numpy as np

    a = highpass(a)
    b = highpass(b)
    h, w = a.shape
    m = radius + block                    # margin: np.roll wraps, so stay clear
    ys = np.arange(m, h - m - block + 1, stride)
    xs = np.arange(m, w - m - block + 1, stride)
    if ys.size == 0 or xs.size == 0:
        raise ValueError("frame %dx%d too small for block=%d radius=%d"
                         % (w, h, block, radius))
    energy = _boxsum(a * a, block)[np.ix_(ys, xs)] / float(block * block)
    kept = energy >= min_energy

    best = np.full((ys.size, xs.size), np.inf)
    bdy = np.zeros((ys.size, xs.size), dtype=np.int32)
    bdx = np.zeros((ys.size, xs.size), dtype=np.int32)
    zero = None
    for dy in range(-radius, radius + 1):
        rb = np.roll(b, dy, axis=0)
        for dx in range(-radius, radius + 1):
            d = a - np.roll(rb, dx, axis=1)
            s = _boxsum(d * d, block)[np.ix_(ys, xs)]
            if dy == 0 and dx == 0:
                zero = s
            better = s < best
            best = np.where(better, s, best)
            bdy = np.where(better, dy, bdy)
            bdx = np.where(better, dx, bdx)
    # how much better than staying put: 0 means the best shift is no improvement
    conf = np.where(zero > 0, 1.0 - best / np.maximum(zero, 1e-9), 0.0)
    # SIGN. The search rolls B by (dy, dx) to line it up with A, so the CONTENT
    # travelled by the negative of that between A and B. Report the content's
    # motion, which is what "the body moved 40px down" means to a reader; the
    # selftest pins it by translating a known picture by a known amount.
    return -bdy[kept], -bdx[kept], int(kept.sum()), conf[kept], int(kept.size)


def summarise(dy, dx, conf, n_kept, n_total, radius, scale=1):
    """Turn a displacement field into the handful of numbers worth reporting."""
    import numpy as np

    if n_kept == 0:
        return {"kept_blocks": 0, "note": "no textured block met min_energy"}
    mag = np.hypot(dy, dx) * scale
    gy, gx = float(np.median(dy)), float(np.median(dx))
    res = np.hypot(dy - gy, dx - gx) * scale
    sat = float(np.mean((np.abs(dy) >= radius) | (np.abs(dx) >= radius)))
    return {
        "kept_blocks": int(n_kept),
        "textured_frac": round(n_kept / float(n_total), 3),
        "median_disp_px": round(float(np.median(mag)), 2),
        "p90_disp_px": round(float(np.percentile(mag, 90)), 2),
        "max_disp_px": round(float(mag.max()), 2),
        "moved_frac_4px": round(float(np.mean(mag >= 4)), 3),
        "moved_frac_8px": round(float(np.mean(mag >= 8)), 3),
        "moved_frac_16px": round(float(np.mean(mag >= 16)), 3),
        "global_shift_px": [round(gy * scale, 2), round(gx * scale, 2)],
        "articulation_p90_px": round(float(np.percentile(res, 90)), 2),
        "articulation_max_px": round(float(res.max()), 2),
        "saturated_frac": round(sat, 3),
        "median_confidence": round(float(np.median(conf)), 3),
    }


# ------------------------------------------------------------- clip decoding
def read_gray(path, scale=4):
    """Every frame of a clip as (n, h, w) uint8 grayscale at 1/`scale`.

    -vsync 0, for hold_period.pair_differences' reason: a decoder that retimes
    frames would forge the freeze we are measuring.
    """
    import numpy as np

    from hold_period import _ffmpeg, probe

    w, h, fps = probe(str(path))
    sw, sh = max(16, w // scale), max(16, h // scale)
    sw, sh = sw - (sw % 2), sh - (sh % 2)
    r = subprocess.run(
        [_ffmpeg(), "-v", "error", "-i", str(path), "-vsync", "0",
         "-vf", "scale=%d:%d,format=gray" % (sw, sh), "-f", "rawvideo", "-"],
        capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg failed on %s: %s"
                           % (path, r.stderr.decode("utf-8", "replace")[:300]))
    buf = np.frombuffer(r.stdout, dtype=np.uint8)
    n = buf.size // (sw * sh)
    return buf[:n * sw * sh].reshape(n, sh, sw), fps, (w, h)


def terminal_freeze(path):
    """WHERE THE CLIP DIES, scored separately from the hold and never merged.

    Two indices, because they answer two different questions and a lane that
    reports one has reported half:

      exact  -- the last pair that is not bit-identical. A clip whose tail is
                literally the same bytes has stopped generating.
      soft   -- the last pair whose mean absolute difference reaches 0.05 of a
                luma level. crf-18 re-encoding leaves max|A-B| up to 8 on a
                PROVABLY frozen tail, so exact equality under-reports a freeze
                that survived a transcode, and the soft index catches it.

    Read at full resolution: a freeze is a claim about the delivered pixels.
    """
    import numpy as np

    f, fps, _ = read_gray(path, scale=1)
    d = np.abs(np.diff(f.astype(np.int16), axis=0))
    mad = d.mean(axis=(1, 2))
    exact = d.max(axis=(1, 2)) == 0
    n = len(mad)
    last_exact = max((i for i in range(n) if not exact[i]), default=-1)
    last_soft = max((i for i in range(n) if mad[i] >= 0.05), default=-1)
    return {
        "frames": int(f.shape[0]),
        "last_pair_with_any_new_pixel": int(last_exact) + 1,
        "last_pair_with_mad_ge_0p05": int(last_soft) + 1,
        "bit_identical_pairs": int(exact.sum()),
        "terminal_exact_run": int(n - 1 - last_exact),
        "terminal_soft_run": int(n - 1 - last_soft),
        "tail_mad_last12": [round(float(v), 4) for v in mad[-12:]],
    }


def measure_clip(path, a=0, b=-1, scale=4, block=12, stride=6, radius=32,
                 min_energy=3.0):
    f, fps, full = read_gray(path, scale=scale)
    n = f.shape[0]
    ia, ib = a % n, b % n
    dy, dx, kept, conf, total = displacement_field(
        f[ia], f[ib], block=block, stride=stride, radius=radius,
        min_energy=min_energy)
    out = summarise(dy, dx, conf, kept, total, radius, scale=scale)
    out.update({
        "clip": str(path), "frames": int(n), "pair": [int(ia), int(ib)],
        "read_at": "%dx%d (1/%d of %dx%d)" % (f.shape[2], f.shape[1], scale,
                                              full[0], full[1]),
        "search_radius_px": radius * scale, "block_px": block * scale,
    })
    return out


# ------------------------------------------------------------------ selftest
def selftest(verbose=True):
    """Three synthetic pairs with known answers. All three must pass."""
    import numpy as np

    rng = np.random.default_rng(20260816)
    base = rng.normal(0, 40, (256, 256))
    # a bit of structure at limb scale, so blocks are not pure noise
    yy, xx = np.mgrid[0:256, 0:256]
    base += 60 * np.sin(xx / 7.0) * np.cos(yy / 9.0)
    base = np.clip(base + 128, 0, 255)

    def run(a, b, radius=24):
        dy, dx, kept, conf, total = displacement_field(
            a, b, block=12, stride=6, radius=radius, min_energy=3.0)
        return summarise(dy, dx, conf, kept, total, radius)

    fails = []

    frozen = run(base, base.copy())
    if verbose:
        print("  frozen pair            median %.2f  p90 %.2f  moved>=4px %.3f"
              % (frozen["median_disp_px"], frozen["p90_disp_px"],
                 frozen["moved_frac_4px"]))
    if frozen["p90_disp_px"] != 0.0 or frozen["moved_frac_4px"] != 0.0:
        fails.append("a frozen pair must read 0 displacement, read %r" % frozen)

    shifted = np.roll(np.roll(base, 11, axis=0), -7, axis=1)
    tr = run(base, shifted)
    if verbose:
        print("  translated by (11,-7)  median %.2f  global %s  articulation p90 %.2f"
              % (tr["median_disp_px"], tr["global_shift_px"],
                 tr["articulation_p90_px"]))
    if tr["global_shift_px"] != [11.0, -7.0]:
        fails.append("a pure translation must be recovered exactly, read %r"
                     % (tr["global_shift_px"],))
    if tr["articulation_p90_px"] > 0.0:
        fails.append("a pure translation has no articulation, read %r"
                     % tr["articulation_p90_px"])

    # THE ONE THAT MATTERS: redrawn in place. Fresh noise and a contrast change,
    # zero displacement. This is what every arm of this investigation looks like.
    reinked = np.clip(base * 1.15 + rng.normal(0, 18, base.shape), 0, 255)
    ri = run(base, reinked)
    if verbose:
        print("  re-inked in place      median %.2f  p90 %.2f  moved>=4px %.3f"
              % (ri["median_disp_px"], ri["p90_disp_px"], ri["moved_frac_4px"]))
    if ri["p90_disp_px"] > 2.0 or ri["moved_frac_4px"] > 0.02:
        fails.append("a redrawn-in-place pair must not read as motion, read %r" % ri)

    for f in fails:
        print("  !! " + f)
    return 1 if fails else 0


# ---------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("clips", nargs="*")
    ap.add_argument("--a", type=int, default=0, help="first frame index")
    ap.add_argument("--b", type=int, default=-1, help="second frame index")
    ap.add_argument("--scale", type=int, default=4)
    ap.add_argument("--block", type=int, default=12)
    ap.add_argument("--stride", type=int, default=6)
    ap.add_argument("--radius", type=int, default=32)
    ap.add_argument("--min-energy", type=float, default=3.0)
    ap.add_argument("--freeze", action="store_true",
                    help="also report the terminal-freeze indices (full res)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", help="write every result to this file")
    a = ap.parse_args()

    if a.selftest:
        print("body_motion selftest")
        rc = selftest()
        print("  selftest %s" % ("PASS" if rc == 0 else "FAIL"))
        return rc
    if not a.clips:
        ap.error("give at least one clip, or --selftest")

    out = []
    for c in a.clips:
        r = measure_clip(c, a=a.a, b=a.b, scale=a.scale, block=a.block,
                         stride=a.stride, radius=a.radius,
                         min_energy=a.min_energy)
        if a.freeze:
            r["terminal_freeze"] = terminal_freeze(c)
        out.append(r)
        print(Path(c).name)
        print("  f%d -> f%d at %s, block %dpx, search +-%dpx"
              % (r["pair"][0], r["pair"][1], r["read_at"], r["block_px"],
                 r["search_radius_px"]))
        if not r.get("kept_blocks"):
            print("  %s" % r.get("note"))
            continue
        print("  DISPLACEMENT  median %.2fpx  p90 %.2fpx  max %.2fpx"
              % (r["median_disp_px"], r["p90_disp_px"], r["max_disp_px"]))
        print("  moved >=4px %.1f%%   >=8px %.1f%%   >=16px %.1f%%  of %d textured blocks"
              % (100 * r["moved_frac_4px"], 100 * r["moved_frac_8px"],
                 100 * r["moved_frac_16px"], r["kept_blocks"]))
        print("  global shift %s px  ARTICULATION p90 %.2fpx  max %.2fpx"
              % (r["global_shift_px"], r["articulation_p90_px"],
                 r["articulation_max_px"]))
        print("  saturated %.1f%%   median confidence %.3f"
              % (100 * r["saturated_frac"], r["median_confidence"]))
        print("  (a camera move and a body move look identical here -- only the")
        print("   ARTICULATION line says parts moved differently from each other,")
        print("   and even that is not proof. Open the frames.)")
        if a.freeze:
            t = r["terminal_freeze"]
            print("  FREEZE  last pair with any new pixel %d of %d, with MAD>=0.05 %d"
                  % (t["last_pair_with_any_new_pixel"], t["frames"] - 1,
                     t["last_pair_with_mad_ge_0p05"]))
            print("          bit-identical pairs %d, terminal exact run %d, soft run %d"
                  % (t["bit_identical_pairs"], t["terminal_exact_run"],
                     t["terminal_soft_run"]))
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        print("wrote %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
