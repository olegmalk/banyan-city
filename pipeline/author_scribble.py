#!/usr/bin/env python3
"""Author a SCRIBBLE control hint for a two-leaf seedling — pure PIL geometry.

WHY THIS EXISTS. Count is not reachable by wording: T2ICountBench
(arXiv 2503.06884) shows CLIP text embeddings are near-identical across
numerals, and it tests and rejects prompt refinement explicitly. So if two
leaves are ever to be pinned, the constraint has to arrive as PIXELS. This
script draws those pixels. It is the "can we author the hint?" half of the
ControlNet question — a conditioning path nobody can draw an input for is not
a capability, so this is deliberately the first thing built.

NO TORCH, NO DIFFUSERS, NO NETWORK — PIL and stdlib only, the same discipline
as pipeline/regional_ip.py. The half of the recipe that decides WHAT SHAPE the
condition is stays testable without a GPU, and the hint can be authored and
reviewed on any machine including a Mac with no venv.

CONVENTION, AND IT IS AN ASSUMPTION WORTH NAMING: ControlNet scribble expects
WHITE STROKES ON A BLACK GROUND. If that polarity were backwards the control
image would read as "ink everywhere", the hint would carry no information, and
a binding test would fail for a reason that has nothing to do with ControlNet.
That is exactly why controlnet_probe.py renders both polarities rather than
trusting this comment — see its C arm. `--invert` is here so the answer costs
one flag either way.

THE STROKE IS THE SECOND DIAL. The xinsir/controlnet-scribble-sdxl-1.0 card
says the model takes "any type of lines and any width of lines" and that a
thin line gives coarse control (prompt wins) while a thick line gives strong
control (condition wins). So stroke weight is a control-strength knob that sits
beside `controlnet_conditioning_scale`, and `--stroke` exposes it.

THE GEOMETRY IS DELIBERATELY OFF-CENTRE by default (`--base-x 0.32`). A hint
that puts the seedling where the model would have put it anyway cannot prove
the condition bound — following it and ignoring it look identical. Placing the
stem base off-centre makes obedience measurable: see controlnet_probe.py's
green-mass centroid.

    python3 pipeline/author_scribble.py out.png
    python3 pipeline/author_scribble.py out.png --leaves 2 --base-x 0.32
    python3 pipeline/author_scribble.py --selftest

THIS SCRIPT TAKES NO VIEW ON WHETHER TWO LEAVES IS RIGHT. It draws the number
it is told to draw. The founder's "average leaves" ruling is about SHAPE and is
honoured by drawing a plain rounded leaf and nothing exotic; the COUNT is the
leaf-count lane's experiment and no verdict about it may be read from here.
"""
from __future__ import annotations

import argparse
import hashlib
import math
import sys

# Beat 01's proven render size (render_b01r9.py RENDER_W/RENDER_H). The control
# must match the render exactly or diffusers resizes it and the geometry the
# measurement assumes is no longer the geometry the model saw.
W, H = 832, 1216


def leaf_polygon(cx, cy, length, width, angle_deg, points=48):
    """An ordinary leaf: a rounded lens, wide in the middle, tapered at both ends.

    Not an ellipse and not a lance. An ellipse reads as a pebble and a lance is
    one of the shapes the founder's "average leaves" ruling puts out of bounds,
    so the outline is a symmetric lens — the shape anyone draws when you say
    "leaf". Built from two mirrored sine lobes so `width` is reached exactly at
    the midpoint and both tips close to a point.
    """
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for side in (1, -1):
        rng = range(points + 1) if side == 1 else range(points, -1, -1)
        for i in rng:
            t = i / points                      # 0..1 along the midrib
            u = (t - 0.5) * length              # local x, tip to tip
            v = side * (width / 2.0) * math.sin(math.pi * t)   # local y
            pts.append((cx + u * ca - v * sa, cy + u * sa + v * ca))
    return pts


def build(width=W, height=H, leaves=2, base_x=0.32, base_y=0.94,
          stem_frac=0.30, leaf_len=None, leaf_wid=None, spread=52.0,
          stroke=7, invert=False):
    """Draw the hint. Returns a PIL RGB image.

    `stem_frac` is the stem tip's height as a fraction of frame height, so the
    hint speaks the same units as the stem-height predicate the founder's
    ruling already binds on.
    """
    from PIL import Image, ImageDraw

    if leaves < 0:
        raise ValueError(f"leaves must be >= 0, got {leaves}")
    if not 0.0 < stem_frac < 1.0:
        raise ValueError(f"stem_frac must be in (0,1), got {stem_frac}")
    if stroke < 1:
        raise ValueError(f"stroke must be >= 1, got {stroke}")

    ink, ground = (0, 0, 0) if invert else (255, 255, 255), \
                  (255, 255, 255) if invert else (0, 0, 0)
    img = Image.new("RGB", (width, height), ground)
    d = ImageDraw.Draw(img)

    bx = base_x * width
    by = base_y * height
    tip_y = by - stem_frac * height
    if leaf_len is None:
        leaf_len = 0.115 * height
    if leaf_wid is None:
        leaf_wid = leaf_len * 0.62          # ordinary proportions, not a blade

    # The stem, with a slight lean so it does not read as a ruled line.
    lean = 0.012 * width
    d.line([(bx, by), (bx + lean, tip_y)], fill=ink, width=stroke, joint="curve")

    # Leaves fan symmetrically off the tip. Two is the default because two is
    # what the beats need; the parameter exists so a 1- or 3-leaf hint can be
    # drawn for a control arm without editing code.
    apex = (bx + lean, tip_y)
    boxes = []
    for i in range(leaves):
        if leaves == 1:
            ang = -90.0
        else:
            # Fan across `spread` degrees either side of straight up.
            frac = i / (leaves - 1)
            ang = -90.0 - spread + frac * (2 * spread)
        a = math.radians(ang)
        # Leaf centre sits one half-length out along its own axis from the apex.
        cx = apex[0] + math.cos(a) * (leaf_len / 2.0)
        cy = apex[1] + math.sin(a) * (leaf_len / 2.0)
        poly = leaf_polygon(cx, cy, leaf_len, leaf_wid, ang)
        d.line(poly + [poly[0]], fill=ink, width=stroke, joint="curve")
        # Midrib — one interior stroke. A bare outline is a balloon; the midrib
        # is what makes an outline read as foliage.
        mx0 = cx - math.cos(a) * leaf_len * 0.42
        my0 = cy - math.sin(a) * leaf_len * 0.42
        mx1 = cx + math.cos(a) * leaf_len * 0.42
        my1 = cy + math.sin(a) * leaf_len * 0.42
        d.line([(mx0, my0), (mx1, my1)], fill=ink,
               width=max(1, stroke - 3), joint="curve")
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        boxes.append((min(xs) / width, min(ys) / height,
                      max(xs) / width, max(ys) / height))

    meta = {
        "size": f"{width}x{height}",
        "leaves": leaves,
        "base_x": base_x, "base_y": base_y,
        "stem_frac": stem_frac,
        "stem_tip_y_frac": tip_y / height,
        "leaf_len_px": round(leaf_len, 1), "leaf_wid_px": round(leaf_wid, 1),
        "spread_deg": spread, "stroke_px": stroke,
        "polarity": "black-on-white (INVERTED)" if invert
                    else "white-on-black (scribble convention)",
        "leaf_boxes_norm": [tuple(round(v, 4) for v in b) for b in boxes],
        "ink_fraction": None,   # filled by caller after counting
    }
    return img, meta


def ink_fraction(img, invert=False):
    """What fraction of the frame carries ink. A sanity number: a hint that is
    ~0 is blank and one that is large is a fill, and both are broken."""
    g = img.convert("L")
    hist = g.histogram()
    total = sum(hist)
    if invert:
        n = sum(hist[:128])      # dark ink on light ground
    else:
        n = sum(hist[128:])      # light ink on dark ground
    return n / total


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def selftest():
    """Geometry invariants. Pure logic, no GPU, safe in CI."""
    fails = []

    def check(name, cond):
        print(("  ok   " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    img, m = build()
    check("default canvas is beat 01's render size", img.size == (W, H))
    frac = ink_fraction(img)
    check(f"hint carries ink but is not a fill ({frac:.4f})", 0.002 < frac < 0.20)
    check("two leaf boxes for the default hint", len(m["leaf_boxes_norm"]) == 2)

    # The off-centre default is the whole basis of the binding measurement.
    xs = [(b[0] + b[2]) / 2 for b in m["leaf_boxes_norm"]]
    check("hint mass sits left of centre (obedience is measurable)",
          sum(xs) / len(xs) < 0.47)

    # Boxes must be inside the frame or the measurement reads clipped pixels.
    check("every leaf box is inside the frame",
          all(0.0 <= b[0] < b[2] <= 1.0 and 0.0 <= b[1] < b[3] <= 1.0
              for b in m["leaf_boxes_norm"]))

    # Polarity must actually flip, and the inverted hint must carry the same
    # amount of ink — otherwise `--invert` is not a polarity flip but a redraw.
    inv, _ = build(invert=True)
    fi = ink_fraction(inv, invert=True)
    check(f"inverted hint carries the same ink ({fi:.4f})", abs(fi - frac) < 0.01)
    check("inverted ground is light", inv.convert("L").getpixel((3, 3)) > 200)
    check("upright ground is dark", img.convert("L").getpixel((3, 3)) < 55)

    # A 1-leaf and 3-leaf hint must be drawable for control arms.
    for n in (1, 3):
        _, mn = build(leaves=n)
        check(f"{n}-leaf hint draws {n} boxes", len(mn["leaf_boxes_norm"]) == n)

    # Stroke is a real dial: thicker must mean more ink.
    thin = ink_fraction(build(stroke=3)[0])
    thick = ink_fraction(build(stroke=13)[0])
    check(f"stroke is a control dial ({thin:.4f} -> {thick:.4f})", thick > thin * 1.5)

    # Determinism: the bytes must not move, or the sha in a sidecar is a lie.
    import io
    b1, b2 = io.BytesIO(), io.BytesIO()
    build()[0].save(b1, "PNG")
    build()[0].save(b2, "PNG")
    check("authoring is deterministic", b1.getvalue() == b2.getvalue())

    # Bad input must be refused, not silently clamped.
    for kw in ({"stem_frac": 0.0}, {"stem_frac": 1.4}, {"stroke": 0},
               {"leaves": -1}):
        try:
            build(**kw)
            check(f"refuses {kw}", False)
        except ValueError:
            check(f"refuses {kw}", True)

    print(("SELFTEST FAIL: %d" % len(fails)) if fails else "SELFTEST PASS")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description="draw a scribble control hint")
    ap.add_argument("out", nargs="?", help="output PNG")
    ap.add_argument("--width", type=int, default=W)
    ap.add_argument("--height", type=int, default=H)
    ap.add_argument("--leaves", type=int, default=2)
    ap.add_argument("--base-x", type=float, default=0.32,
                    help="stem base x as a frame fraction; off-centre on "
                         "purpose so obedience is measurable")
    ap.add_argument("--base-y", type=float, default=0.94)
    ap.add_argument("--stem-frac", type=float, default=0.30,
                    help="stem tip height as a fraction of frame height")
    ap.add_argument("--leaf-len", type=float, default=None)
    ap.add_argument("--leaf-wid", type=float, default=None)
    ap.add_argument("--spread", type=float, default=52.0,
                    help="degrees either side of vertical the leaves fan")
    ap.add_argument("--stroke", type=int, default=7,
                    help="stroke width px; the card's second control dial")
    ap.add_argument("--invert", action="store_true",
                    help="black on white instead of the scribble convention")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.out:
        ap.error("out PNG required (or --selftest)")

    img, meta = build(a.width, a.height, a.leaves, a.base_x, a.base_y,
                      a.stem_frac, a.leaf_len, a.leaf_wid, a.spread,
                      a.stroke, a.invert)
    meta["ink_fraction"] = round(ink_fraction(img, a.invert), 5)
    img.save(a.out, "PNG")
    print(f"wrote {a.out}")
    for k, v in meta.items():
        print(f"  {k}: {v}")
    print(f"  sha256: {sha256_file(a.out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
