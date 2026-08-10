"""How green is a frame? A hue histogram, no model involved.

Written for the beat-04 goblin question (GREEN-REFERENCE-0810.md): IP-Adapter
held the character and the output stopped looking green, and nobody had
checked whether the reference we handed the adapter was green in the first
place. That check needs one instrument applied to the reference and to the
outputs, or the comparison is between two rulers.

METHOD. sRGB -> HSV, hue in degrees, S and V in 0..1. Then per image:

  green_share   fraction of ALL pixels with hue in [70,180) AND S >= 0.15.
                The band is broad on purpose. Goblin skin here sits at a
                median hue of 160 deg, close enough to the green/cyan border
                that a narrow band would score a small hue rotation as a
                total colour loss, and that is precisely the thing under
                test. The S floor drops grey pixels, which carry a hue but
                no colour.
  narrow_share  the same with hue in [140,170], the band the arm-1 report
                used, recomputed here only so its number stays comparable.
  sat_green     mean saturation of the green-hued pixels: "how green".
                green_share is "how much".
  sat_all       mean saturation over every pixel. Separating this from
                green_share is what distinguishes a drain (chroma leaves)
                from a rotation (chroma stays, hue moves).

--square centre-crops to a square first, because a portrait frame handed to
IP-Adapter is centre-cropped to square before the image encoder sees it
(`ip_adapter_reference_prep` in the render-time sidecars). Measuring the full
frame answers a question the adapter was never asked.

DOES IT DISCRIMINATE? On this footage, yes, and that was checked before the
number was trusted: it puts the wave-1 frames and the arm-2 frames (both
green to the eye) at 0.34-0.49 and the arm-1 frames (grey-teal to the eye) at
0.001-0.014, and the ordering matches a direct look at the contact sheet in
all three groups. Where a number and the picture disagree the picture wins.
This is deliberately neither the flow metric (disqualified: it peaked on the
beat where the plant fell over) nor the pan metric (saturates at half a
block).

Usage:
    python3 pipeline/green_share.py 'label|glob|full' 'label|glob|sq' ...
"""
import glob
import sys

import numpy as np
from PIL import Image

GREEN_LO, GREEN_HI = 70.0, 180.0
NARROW_LO, NARROW_HI = 140.0, 170.0
SAT_FLOOR = 0.15


def hsv(rgb):
    """Vectorised sRGB -> HSV. Hue in degrees, S and V in 0..1."""
    a = rgb.astype(np.float32) / 255.0
    mx = a.max(2)
    mn = a.min(2)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-8), 0.0)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    h = np.zeros_like(mx)
    nz = d > 1e-8
    idx = nz & (mx == r)
    h[idx] = ((g - b)[idx] / d[idx]) % 6
    idx = nz & (mx == g)
    h[idx] = ((b - r)[idx] / d[idx]) + 2
    idx = nz & (mx == b)
    h[idx] = ((r - g)[idx] / d[idx]) + 4
    return h * 60.0, s, mx


def centre_square(im):
    """The crop IP-Adapter's image processor sees on a portrait reference."""
    w, h = im.size
    s = min(w, h)
    left, top = (w - s) // 2, (h - s) // 2
    return im.crop((left, top, left + s, top + s))


def stats(im):
    h, s, _ = hsv(np.asarray(im.convert("RGB")))
    chroma = s >= SAT_FLOOR
    green = chroma & (h >= GREEN_LO) & (h < GREEN_HI)
    narrow = chroma & (h >= NARROW_LO) & (h <= NARROW_HI)
    n = float(h.size)
    return {
        "green_share": float(green.sum()) / n,
        "narrow_share": float(narrow.sum()) / n,
        "sat_green": float(s[green].mean()) if green.any() else 0.0,
        "hue_green": float(np.median(h[green])) if green.any() else 0.0,
        "sat_all": float(s.mean()),
    }


def group(label, paths, square=False):
    rows = []
    for p in sorted(paths):
        im = Image.open(p)
        if square:
            im = centre_square(im)
        rows.append(stats(im))
    if not rows:
        raise SystemExit("no frames matched for %r" % label)
    mean = {k: float(np.mean([r[k] for r in rows])) for k in rows[0]}
    print(
        "%-34s n=%d  green_share=%.4f  narrow=%.4f  sat_green=%.3f  hue=%5.1f  sat_all=%.3f"
        % (label, len(rows), mean["green_share"], mean["narrow_share"],
           mean["sat_green"], mean["hue_green"], mean["sat_all"])
    )
    return mean


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    for spec in argv:
        label, pattern, mode = spec.split("|")
        group(label, glob.glob(pattern), square=(mode == "sq"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
