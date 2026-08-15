#!/usr/bin/env python3
"""Init-vs-final-frame drift comparison sheets, grade-neutralised and blinded."""
import json, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W = os.path.dirname(os.path.abspath(__file__))
INIT = os.path.join(W, "src", "ep2-b02-stg-headup-49f-0815", "b02-init-704x1280.png")
OUT = os.path.join(W, "readerdir")
os.makedirs(OUT, exist_ok=True)

# ---- sRGB <-> CIE Lab (D65) -------------------------------------------------
def srgb_to_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def lin_to_srgb(c):
    c = np.clip(c, 0.0, 1.0)
    v = np.where(c <= 0.0031308, c * 12.92, 1.055 * (c ** (1 / 2.4)) - 0.055)
    return np.clip(v * 255.0, 0, 255)

M = np.array([[0.4124564, 0.3575761, 0.1804375],
              [0.2126729, 0.7151522, 0.0721750],
              [0.0193339, 0.1191920, 0.9503041]])
MI = np.linalg.inv(M)
WP = np.array([0.95047, 1.00000, 1.08883])

def f_fwd(t):
    d = 6.0 / 29.0
    return np.where(t > d ** 3, np.cbrt(t), t / (3 * d * d) + 4.0 / 29.0)

def f_inv(t):
    d = 6.0 / 29.0
    return np.where(t > d, t ** 3, 3 * d * d * (t - 4.0 / 29.0))

def rgb2lab(a):
    xyz = srgb_to_lin(a.astype(np.float64)) @ M.T
    f = f_fwd(xyz / WP)
    return np.dstack([116 * f[..., 1] - 16,
                      500 * (f[..., 0] - f[..., 1]),
                      200 * (f[..., 1] - f[..., 2])])

def lab2rgb(lab):
    fy = (lab[..., 0] + 16) / 116.0
    fx = fy + lab[..., 1] / 500.0
    fz = fy - lab[..., 2] / 200.0
    xyz = np.dstack([f_inv(fx), f_inv(fy), f_inv(fz)]) * WP
    return lin_to_srgb(xyz @ MI.T)

def stats(lab):
    return lab.reshape(-1, 3).mean(0), lab.reshape(-1, 3).std(0)

def match_grade(src_rgb, ref_rgb):
    """Reinhard global mean/std transfer in Lab: src takes ref's global colour stats."""
    s, r = rgb2lab(src_rgb), rgb2lab(ref_rgb)
    sm, ss = stats(s)
    rm, rs = stats(r)
    scale = np.where(ss > 1e-6, rs / ss, 1.0)
    out = (s - sm) * scale + rm
    out[..., 0] = np.clip(out[..., 0], 0, 100)
    return lab2rgb(out).astype(np.uint8), (sm, ss, rm, rs)

init = np.array(Image.open(INIT).convert("RGB"))
im, isd = stats(rgb2lab(init))

report = {"init_lab_mean": im.tolist(), "init_lab_std": isd.tolist(), "clips": {}}

finals = {}
for n in (49, 97, 193):
    f = np.array(Image.open(os.path.join(W, "frames", "final-%d.png" % n)).convert("RGB"))
    matched, (sm, ss, rm, rs) = match_grade(f, init)
    finals[n] = matched
    Image.fromarray(matched).save(os.path.join(W, "frames", "final-%d-graded.png" % n))
    # residual global stats after matching (sanity: should be ~= init's)
    am, asd = stats(rgb2lab(matched))
    report["clips"][n] = {
        "before_lab_mean": sm.tolist(), "before_lab_std": ss.tolist(),
        "delta_mean_vs_init_before": (sm - im).tolist(),
        "after_lab_mean": am.tolist(), "after_lab_std": asd.tolist(),
        "delta_mean_vs_init_after": (am - im).tolist(),
    }

# ---- blinding ---------------------------------------------------------------
CODES = ["HOLLOW", "PEWTER", "THISTLE"]
rng = random.SystemRandom()
order = [49, 97, 193]
rng.shuffle(order)
codes = CODES[:]
rng.shuffle(codes)
mapping = {c: n for c, n in zip(codes, order)}

def font(sz):
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()

SCALE = 0.62
PW, PH = int(704 * SCALE), int(1280 * SCALE)
GAP, PAD, HDR = 24, 28, 84

def sheet(code, final_rgb, path):
    cw = PAD * 2 + PW * 2 + GAP
    ch = HDR + PAD + PH + 58 + PAD
    c = Image.new("RGB", (cw, ch), (22, 22, 24))
    d = ImageDraw.Draw(c)
    d.text((PAD, 26), "PAIR %s" % code, fill=(240, 240, 240), font=font(38))
    for i, (img, cap) in enumerate(((init, "REFERENCE"), (final_rgb, "IMAGE"))):
        x = PAD + i * (PW + GAP)
        c.paste(Image.fromarray(img).resize((PW, PH), Image.LANCZOS), (x, HDR))
        d.text((x, HDR + PH + 16), cap, fill=(200, 200, 205), font=font(28))
    c.save(path)

# write in randomised order so mtime leaks nothing
items = list(mapping.items())
rng.shuffle(items)
for code, n in items:
    sheet(code, finals[n], os.path.join(OUT, "pair-%s.png" % code))

report["mapping_code_to_frames"] = mapping
with open(os.path.join(W, "mapping.json"), "w") as fh:
    json.dump(report, fh, indent=2)
print(json.dumps({"mapping": mapping}, indent=2))
for n in (49, 97, 193):
    b = report["clips"][n]["delta_mean_vs_init_before"]
    a = report["clips"][n]["delta_mean_vs_init_after"]
    print("%3df  Lab mean delta vs init  BEFORE L%+.2f a%+.2f b%+.2f   AFTER L%+.3f a%+.3f b%+.3f"
          % (n, b[0], b[1], b[2], a[0], a[1], a[2]))
