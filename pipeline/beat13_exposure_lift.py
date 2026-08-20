#!/usr/bin/env python3
"""EXPOSURE-LIFT beat 13's composited plate. numpy/PIL, $0, no GPU, no network.

WHY THIS EXISTS. Beat 13's rung-3 motion take passed H1 by 7x -- the face band's
mean absolute interframe went 10.80 (rung 1, earned by walking out of frame) ->
0.64 (rung 2, frozen) -> 4.798 (rung 3, the seated middle the bar asked for) --
and G8, `the plant's small patch of shade is lying across his eyes`, failed for
the third time. The spec pre-registered exactly that test: *if H1 passes and G8
still fails, the wording is exonerated.* It did, so wording is closed on this
beat and the next lever is the plate.

THE CURVE, and why it is not a gamma. The obvious "brighten it" instrument is a
gamma < 1, and it is the WRONG ONE HERE, which is worth writing down because it
was this lane's first choice. G8 needs a DARK PATCH to be legible ON HIS FACE,
so what has to grow is the SEPARATION between his lit face and the frame's
shadow value -- and a gamma COMPRESSES the top of the range, so it shrinks that
separation. Measured on this plate, face-minus-frame-median in luma:

    plate as it is   114.6 - 89.5 = 25.1
    gamma 0.85       129.3 - 104.7 = 24.6      <- worse
    gamma 0.75       139.9 - 116.2 = 23.7      <- worse
    gamma 0.65       151.6 - 129.2 = 22.4      <- worse

So this applies a real EXPOSURE gain, in linear light, with a built-in shoulder:

    y = k*x / (1 + (k-1)*x)          on linear-light x in [0,1]

which maps 0 -> 0 and 1 -> 1 exactly, is monotonic, has slope k at black (a true
k-stop lift of the shadows and midtones) and slope 1/k at white (a shoulder), and
therefore CANNOT CLIP: no pixel that was below 255 can reach 255. At k = 2.0 the
same separation reads 146.1 - 117.5 = 28.6, i.e. it GROWS by 14% instead of
shrinking. In this dialect an ordinary cel shadow terminator is a step of about
24 luma (measured on beat 19: p99-p50 over a segmented body, 23.9 for a
terminator against 71.8 for a specular), so a shade drawn on the as-is face lands
at 114.6 - 24 = 90.6, which is the frame's own median of 89.5. IT WOULD READ AS
MORE MURK, NOT AS A SHADE. That is the whole mechanical argument for this rung.

WHAT IS NOT DONE, and the measurement that says so out loud:

  * NO COLOUR CORRECTION. The curve is applied per channel in linear light,
    which is what an exposure change physically is; R-B is measured and published
    before and after rather than steered. The green cast is NOT this rung's
    variable.
  * NO SELECTIVE / MASKED LIFT. A mask is a second instrument and this ladder has
    twice had a masked or colour-predicate instrument return a clean, wrong
    number on exactly this kind of green-on-green ground.
  * NO GEOMETRY CHANGE OF ANY KIND. Output is the same WxH, and every pixel keeps
    its coordinates, so `assert_framing.py`'s pre-registered WANT_BBOX and the
    published composite mask both remain valid on the lifted plate. That is not a
    convenience -- it is what makes this a one-variable rung.

AND THE HONEST OBJECTION, MEASURED BEFORE ANY OF THIS RUNS. "Beat 13's plate is
the DIM one" is TRUE OF THE FIELD AND FALSE OF THE FACE. Cropped-init whole-frame
median luma: b13 89.5, b03 181.7, b15 202.4 -- b13's typical pixel is at 35% where
its siblings' are at 71% and 79%. But the CHEEK PROBE, the same instrument on all
three: b13 114.6, b03 101.8, b15 93.3. **Beat 13 has the BRIGHTEST face of the
three plates and the darkest field by a factor of two.** So if G8 fails because
his eyes are too dark, this rung is aimed at the wrong pixels, and that is
pre-registered in the spec as the most likely failure mode.

Run:  python3 pipeline/beat13_exposure_lift.py --k 2.0 [--sheet]
      python3 pipeline/beat13_exposure_lift.py --sweep 1.5,2.0,2.5   # look first
"""
import argparse
import hashlib
import os

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "farm-out", "ep2-b13-sapcomp-0820",
                   "b13-sapcomp-s20260820.png")
# Published into the SAME farm-out directory as its parent plate on purpose:
# box_enqueue traces a --src as farm-out/<dir>/<file> and resolves <dir> to the
# spec whose publish step owns it, and the job's fetch_init.py pulls by raw URL
# under an asserted sha256. A new directory would defeat both.
OUT = os.path.join(REPO, "farm-out", "ep2-b13-sapcomp-0820",
                   "b13-sapcomp-lit-0820.png")

# The cover-crop beat 13 actually renders: 832x1216 -> 704x1280, anchor LEFT.
CROP_W, CROP_H, CROP_ANCHOR = 704, 1280, "left"

# Probes placed by eye at 5x on the real cropped init, BEFORE any lifted pixel
# existed. The cheek box is beat 13's own pre-registered skin probe, carried
# byte for byte from its rung-1 spec.
PROBES = {
    "cheek_the_pre_registered_skin_probe": (286, 282, 352, 336),
    "forehead_dome": (300, 150, 480, 260),
    "eye_band": (290, 350, 500, 410),
    "mouth_jaw": (330, 440, 450, 510),
    "the_composited_plant_leaves": (40, 700, 250, 800),
    "lower_third_the_dark_half": (0, 860, 704, 1280),
    "grass_upper_left_the_bright_end": (0, 0, 260, 300),
}


def luma(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def srgb_to_linear(v):
    v = v / 255.0
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(x):
    x = np.clip(x, 0.0, 1.0)
    v = np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)
    # ROUND, do not truncate. astype(uint8) truncates, and the sRGB round trip
    # lands 255 on 254.99997 -- which made 4003 pure-white pixels come back one
    # level DARKER and tripped the monotonicity assert below. The assert was
    # right and the encode was wrong.
    return np.rint(np.clip(v * 255.0, 0, 255))


def lift(rgb_u8, k):
    """y = k*x/(1+(k-1)*x) on linear light. 0->0, 1->1, slope k at black,
    slope 1/k at white, monotonic, cannot clip."""
    if k <= 0:
        raise SystemExit("!! k must be > 0")
    x = srgb_to_linear(rgb_u8.astype(np.float32))
    y = (k * x) / (1.0 + (k - 1.0) * x)
    return linear_to_srgb(y)


def cover_crop(im, w, h, anchor):
    sw, sh = im.size
    scale = max(w / float(sw), h / float(sh))
    nw, nh = int(round(sw * scale)), int(round(sh * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    left = 0 if anchor == "left" else (nw - w if anchor == "right" else (nw - w) // 2)
    top = (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def report(tag, arr_u8):
    l = luma(arr_u8.astype(np.float32))
    p1, p5, p50, p95, p99 = np.percentile(l, [1, 5, 50, 95, 99])
    clipped = float((arr_u8 >= 255).all(-1).mean() * 100)
    print("  %-10s luma mean %6.2f  p1 %5.1f  p5 %5.1f  p50 %6.1f  p95 %6.1f  "
          "p99 %6.1f  std %5.2f  pure-white %.4f%%"
          % (tag, l.mean(), p1, p5, p50, p95, p99, l.std(), clipped))
    return dict(mean=round(float(l.mean()), 2), p5=round(float(p5), 1),
                p50=round(float(p50), 1), p95=round(float(p95), 1),
                std=round(float(l.std()), 2), pure_white_pct=round(clipped, 4))


def probe_table(before_u8, after_u8):
    print("  %-38s %-28s %-28s %s" % ("probe (on the 704x1280 crop)",
                                      "BEFORE luma/std R-B", "AFTER luma/std R-B",
                                      "d luma"))
    rows = {}
    for name, (x0, y0, x1, y1) in PROBES.items():
        out = []
        for arr in (before_u8, after_u8):
            c = arr[y0:y1, x0:x1].astype(np.float32)
            l = luma(c)
            out.append((float(l.mean()), float(l.std()),
                        float(c[..., 0].mean() - c[..., 2].mean())))
        (lb, sb, cb), (la, sa, ca) = out
        print("  %-38s %7.1f / %5.1f / %6.1f      %7.1f / %5.1f / %6.1f      "
              "%+7.1f" % (name, lb, sb, cb, la, sa, ca, la - lb))
        rows[name] = dict(before=dict(luma=round(lb, 1), std=round(sb, 1),
                                      r_minus_b=round(cb, 1)),
                          after=dict(luma=round(la, 1), std=round(sa, 1),
                                     r_minus_b=round(ca, 1)),
                          d_luma=round(la - lb, 1))
    return rows


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=float, default=2.0,
                    help="linear-light shadow gain; 1.0 is a no-op")
    ap.add_argument("--sweep", default="",
                    help="comma-separated k values -> a contact sheet only, "
                         "writes no plate")
    ap.add_argument("--out", default=OUT)
    # --src ADDED 2026-08-20 so the curve can be applied to a SIBLING plate
    # without editing this file. The default is unchanged, so every command that
    # has ever been run against this tool still resolves to the same bytes; the
    # rung-4 plate `b13-sapcomp-lit-0820.png` is reproducible with no arguments,
    # which matters because ep2-b13-shadelit-0820.yaml asserts its sha256.
    # The consumer is pipeline/decisions-pending/ep2-b13-shade-0820/: if the
    # author rules "draw it taller", the taller sample has to travel the same
    # tone curve as the take it is being compared against, or the comparison is
    # measuring the curve instead of the plant.
    ap.add_argument("--src", default=SRC,
                    help="plate to lift; defaults to the rung-3 composite "
                         "sample, which is what reproduces the rung-4 plate")
    ap.add_argument("--sheet", default="",
                    help="also write a before/after contact sheet here")
    a = ap.parse_args()

    src = Image.open(a.src).convert("RGB")
    src_u8 = np.asarray(src)
    before_crop = np.asarray(cover_crop(src, CROP_W, CROP_H, CROP_ANCHOR))

    if a.sweep:
        ks = [float(v) for v in a.sweep.split(",")]
        tiles = [cover_crop(src, CROP_W, CROP_H, CROP_ANCHOR)]
        print("SWEEP -- nothing is written except the sheet.")
        print("k=1.000 (as it is)")
        report("crop", before_crop)
        for k in ks:
            lifted = Image.fromarray(lift(src_u8, k).astype(np.uint8))
            crop = cover_crop(lifted, CROP_W, CROP_H, CROP_ANCHOR)
            print("k=%.3f" % k)
            report("crop", np.asarray(crop))
            tiles.append(crop)
        sheet = a.sheet or os.path.join(
            REPO, "CONTACT-b13-exposure-sweep-0820.png")
        gap = 8
        sh = Image.new("RGB", (len(tiles) * CROP_W + (len(tiles) - 1) * gap,
                               CROP_H), (24, 24, 24))
        for i, t in enumerate(tiles):
            sh.paste(t, (i * (CROP_W + gap), 0))
        sh.resize((sh.width // 2, sh.height // 2), Image.LANCZOS).save(sheet)
        print("WROTE %s   (order: as-is, %s)"
              % (sheet, ", ".join("k=%.2f" % k for k in ks)))
        return 0

    print("SOURCE %s" % os.path.relpath(a.src, REPO))
    print("  sha256 %s" % sha256(a.src))
    report("full", src_u8)
    report("crop", before_crop)

    out_u8 = lift(src_u8, a.k).astype(np.uint8)
    after_img = Image.fromarray(out_u8)
    after_crop = np.asarray(cover_crop(after_img, CROP_W, CROP_H, CROP_ANCHOR))

    print("LIFTED  y = k*x/(1+(k-1)*x) on linear light, k = %.3f" % a.k)
    report("full", out_u8)
    report("crop", after_crop)
    print()
    probe_table(before_crop, after_crop)

    if src.size != after_img.size:
        raise SystemExit("!! the lift changed the image size -- impossible, and "
                         "it would invalidate assert_framing's bbox. REFUSING.")
    dark = int((out_u8.astype(np.int16) < src_u8.astype(np.int16)).sum())
    if dark:
        raise SystemExit("!! %d channel values went DOWN -- the curve is not "
                         "monotonic-increasing. REFUSING." % dark)
    newly_white = int(((out_u8 >= 255).all(-1) & ~(src_u8 >= 255).all(-1)).sum())
    if newly_white:
        raise SystemExit("!! %d pixels were driven to pure white that were not "
                         "already there -- the shoulder failed. REFUSING."
                         % newly_white)

    after_img.save(a.out)
    print("\nWROTE %s" % os.path.relpath(a.out, REPO))
    print("  sha256 %s" % sha256(a.out))
    print("  newly-clipped pixels: 0 (asserted)   size unchanged: %dx%d "
          "(asserted)" % after_img.size)

    if a.sheet:
        gap = 8
        sh = Image.new("RGB", (2 * CROP_W + gap, CROP_H), (24, 24, 24))
        sh.paste(Image.fromarray(before_crop), (0, 0))
        sh.paste(Image.fromarray(after_crop), (CROP_W + gap, 0))
        sh.save(a.sheet)
        print("  sheet %s" % os.path.relpath(a.sheet, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
