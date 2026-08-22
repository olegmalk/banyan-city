#!/usr/bin/env python3
r"""BEAT 06: draw the BARK BOARD into the hands of a plate that already has the man.

    python3 pipeline/beat06_board_composite.py \
        --plate farm-out/ep2-b06-pose-r4-0822/ep2-b06-pose-r4-0822-posebooth.png \
        --board 312,410,552,535 --hands 370,527,470,612 --chin 397 \
        --out  farm-out/ep2-b06-boardcomp-0822/b06-boardcomp-in-0822.png \
        --mask-out farm-out/ep2-b06-boardcomp-0822/b06-boardcomp-in-mask-0822.png \
        --overlay-out /tmp/b06-overlay.png

WHY THIS FILE EXISTS, AND IT IS THE END OF A CLOSED LADDER RATHER THAN A NEW GUESS
----------------------------------------------------------------------------------
Beat 06's standing fault since the ship manifest was written is THE BOARD IS THE
WRONG SIZE. Three ControlNet rungs were spent on it on 2026-08-22 and the ladder
rule closes at three:

  r1  --scale2 0.50, rectangle centred on the wrist line   no object at all; a
                                                           glowing ball in his
                                                           cupped hands
  r2  --scale2 0.85, same rectangle                        a plank grown DOWNWARD
                                                           out of the hint's top
                                                           edge, standing in front
                                                           of him like a post,
                                                           hands dropped to sides
  r3  --scale2 0.85, rectangle ABOVE the wrists            a LIT WHITE PANEL over
                                                           his chest; the figure
                                                           collapsed to a dark
                                                           shrouded silhouette

Read together: at low strength no object arrives, at high strength the net draws
the RECTANGLE rather than reading it as a slab, and putting it over the torso
lets it eat the figure. That is `b08-arm-route-0819.md` §10 in a different
costume -- THIS CLASS OF NET RENDERS A WHITE STROKE AS LIGHT.

`ep2-b06-pose-r4-0822` then removed the board net entirely and asked only for the
man, in daylight, hands together and EMPTY at chest height. It is the best frame
beat 06 has ever had: a whole adult figure in a field, dark cropped hair, round
wire-rim glasses, head bowed over his own clasped hands. The object is now the
only thing missing, and the instrument for an object in this tree is the
composite -- four for four on plants (beats 03, 13, 16, 19), and beat 19 proved
on 2026-08-22 that a hand-drawn composited object survives i2v motion.

WHAT IS COPIED AND WHAT IS NEW
------------------------------
COPIED, deliberately, from `beat16_sapling_composite.py` and
`beat19_drop_composite.py`: the cel `outline()` law (a 4 px line in the PLATE'S
OWN character ink -- a 1 px line in a tinted colour dissolved at 0.30 and
returned a soft airbrushed shape in front of a hard-inked drawing), the
`dilate()`/`erode()` mask primitives, the measured light direction, the mask
derived FROM the drawn silhouette so the texture edge and the object edge are
the same edge, and the containment check.

NEW, and it is one thing: THE OBJECT IS NOT A PLANT AND THE PLATE HAS NO BROWN
IN IT. `beat16_sapling_composite.foliage_palette` refuses a plate with no green
pixel precisely so that nobody invents a palette; the same honesty applies here
in the other direction, so the colour rule is stated instead of smuggled:

  HUE      canon's, not the plate's. The approved script says "a large flat slab
           of rough brown bark". A daylit field of green grass and a white shirt
           contains no bark to sample, and tinting the board green to match the
           frame would be drawing the wrong object.
  VALUE    the PLATE'S, and measured. The fill luma is set to the 12th
           percentile of the plate's own luma inside the board rectangle, so the
           slab sits in the picture's own shadow range rather than at a
           brightness chosen by hand. This is the axis decal tell #2 is actually
           about.
  INK      the plate's own darkest line colour, via
           `beat16_sapling_composite._character_ink`.
  LIGHT    measured from the low-pass luminance gradient over the board region,
           exactly as the sapling tool does it; the lit edge gets the highlight.

GEOMETRY IS PASSED IN AND ASSERTED, NOT GUESSED. --board, --hands and --chin are
read off the plate at 1:1 and the tool refuses four ways: the board must be at
least as wide as --shoulder-width (the beat's whole fault is that it is too
small), its bottom edge must sit within --grip px of the top of the hands (so
the hands read as HOLDING it rather than pointing at it), its top edge must stay
below the chin (r3 put a panel over the face and lost the figure), and the mask
must stay under --max-mask-frac of the frame (the b16 leafcomp measurement: 0.30
does measurably nothing on a mask eight times the working size).

$0. numpy + PIL. No model, no network, no GPU. Deterministic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from beat16_sapling_composite import (          # noqa: E402
    dilate, erode, outline, _character_ink, light_direction, sha256_of,
)


def parse_box(s: str):
    v = tuple(int(t) for t in s.split(","))
    if len(v) != 4:
        raise SystemExit("!! wants x0,y0,x1,y1 -- got %r" % s)
    return v


def bark_polygon(box, jitter=6.0, n_per_edge=9, seed=20260822):
    """A slab, not a rectangle. A drawn rectangle is decal tell #1 (a shape with
    no hand in it) and it is also literally what the scribble net kept returning
    -- the whole point of drawing this by hand is that a piece of bark has an
    edge that wanders. The jitter is deterministic off `seed`."""
    x0, y0, x1, y1 = box
    rng = np.random.default_rng(seed)
    pts = []

    def edge(ax, ay, bx, by):
        for i in range(n_per_edge):
            t = i / float(n_per_edge)
            j = rng.normal(0.0, jitter)
            # push the jitter along the edge NORMAL so corners stay corners
            dx, dy = bx - ax, by - ay
            L = max(1e-3, (dx * dx + dy * dy) ** 0.5)
            nx, ny = -dy / L, dx / L
            pts.append((ax + dx * t + nx * j, ay + dy * t + ny * j))

    edge(x0, y0, x1, y0)
    edge(x1, y0, x1, y1)
    edge(x1, y1, x0, y1)
    edge(x0, y1, x0, y0)
    return pts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plate", required=True)
    ap.add_argument("--plate-sha256")
    ap.add_argument("--board", required=True, help="x0,y0,x1,y1 of the slab")
    ap.add_argument("--hands", required=True, help="x0,y0,x1,y1 of the hands")
    ap.add_argument("--chin", type=int, required=True, help="plate y of the chin")
    ap.add_argument("--shoulder-width", type=int, default=220,
                    help="the board must be AT LEAST this wide -- the beat's "
                         "fault is that it is too small, so this is a floor "
                         "and not a target")
    ap.add_argument("--grip", type=int, default=40,
                    help="how far the board's bottom edge may sit above the "
                         "top of the hands and still read as held")
    ap.add_argument("--grain", type=int, default=7, help="bark grain lines")
    ap.add_argument("--ink-width", type=int, default=4)
    ap.add_argument("--mask-dilate", type=int, default=10)
    ap.add_argument("--max-mask-frac", type=float, default=0.14)
    ap.add_argument("--hue", default="112,80,54",
                    help="canon bark hue; its VALUE is re-fitted to the plate")
    ap.add_argument("--out")
    ap.add_argument("--mask-out")
    ap.add_argument("--overlay-out")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    p = a.plate if os.path.isabs(a.plate) else os.path.join(REPO, a.plate)
    raw = np.asarray(Image.open(p).convert("RGB"))
    H, W = raw.shape[:2]
    got = sha256_of(p)
    if a.plate_sha256 and got != a.plate_sha256:
        print("!! plate sha %s, wanted %s" % (got, a.plate_sha256))
        return 1
    print("plate  %dx%d  sha256 %s" % (W, H, got))

    bx0, by0, bx1, by1 = parse_box(a.board)
    hx0, hy0, hx1, hy1 = parse_box(a.hands)

    # --- the four geometry refusals, before a pixel is drawn -----------------
    fails = []
    if bx1 - bx0 < a.shoulder_width:
        fails.append("G1 the board is %d px wide against a %d px floor -- "
                     "'the bark board is the wrong size' IS this beat's fault "
                     "and a narrow slab reproduces it"
                     % (bx1 - bx0, a.shoulder_width))
    if not (hy0 - a.grip <= by1 <= hy0 + (hy1 - hy0) * 0.5):
        fails.append("G2 the board's bottom edge y=%d is not at the hands "
                     "(their top is y=%d): it must land between y=%d and y=%d "
                     "or he is pointing at it rather than holding it"
                     % (by1, hy0, hy0 - a.grip, int(hy0 + (hy1 - hy0) * 0.5)))
    if by0 <= a.chin:
        fails.append("G3 the board's top edge y=%d is at or above the chin "
                     "y=%d. r3 put a panel over the face and the figure "
                     "collapsed into a dark shrouded shape behind it"
                     % (by0, a.chin))
    if by1 <= by0 or bx1 <= bx0:
        fails.append("G4 the board box is inside out")
    for f in fails:
        print("FAIL  %s" % f)
    if fails:
        print("\n!! refusing on geometry -- nothing drawn.")
        return 1

    region = np.zeros((H, W), bool)
    region[max(0, by0 - 40):min(H, by1 + 40), max(0, bx0 - 40):min(W, bx1 + 40)] = True

    # --- colour: canon hue, PLATE value, plate ink, plate light --------------
    hue = np.array([int(v) for v in a.hue.split(",")], dtype=float)
    lum_region = np.asarray(Image.fromarray(raw).convert("L"))[region].astype(float)
    target = float(np.percentile(lum_region, 12))
    hue_lum = 0.299 * hue[0] + 0.587 * hue[1] + 0.114 * hue[2]
    mid = np.clip(hue * (target / max(1.0, hue_lum)), 0, 255)
    dark = np.clip(mid * 0.72, 0, 255)
    light = np.clip(mid * 1.34 + 12, 0, 255)
    ink = _character_ink(raw)
    lx, ly = light_direction(raw, region)
    print("bark   canon hue %s -> plate value: mid %s  dark %s  light %s"
          % (tuple(int(v) for v in hue), tuple(int(v) for v in mid),
             tuple(int(v) for v in dark), tuple(int(v) for v in light)))
    print("       plate ink %s | plate region luma p12 %.1f | light dx %+.3f dy %+.3f"
          % (ink, target, lx, ly))

    # --- draw ----------------------------------------------------------------
    SS = 3
    canvas = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    poly = [(x * SS, y * SS) for x, y in
            bark_polygon((bx0, by0, bx1, by1))]
    d.polygon(poly, fill=tuple(int(v) for v in mid) + (255,))

    # The lit half. A flat slab in this dialect is two values with a hard join,
    # not a gradient -- same law as the sapling's crescent.
    lit_left = lx < 0
    midx = (bx0 + bx1) / 2.0
    shade_poly = [(x, y) for x, y in poly
                  if (x / SS >= midx) == lit_left]
    if len(shade_poly) > 2:
        d.polygon([(x, y) for x, y in poly
                   if (x / SS >= midx) != lit_left]
                  + [(midx * SS, by0 * SS), (midx * SS, by1 * SS)],
                  fill=tuple(int(v) for v in light) + (255,))

    # Bark grain: near-horizontal ridges, because a flat slab held up to be read
    # is cut ACROSS the grain and a vertical stripe pattern reads as a fence.
    for i in range(1, a.grain + 1):
        gy = by0 + (by1 - by0) * i / float(a.grain + 1)
        wob = (by1 - by0) * 0.035
        pts = [((bx0 + 6 + (bx1 - bx0 - 12) * t / 12.0) * SS,
                (gy + wob * np.sin(t * 1.7 + i)) * SS) for t in range(13)]
        d.line(pts, fill=tuple(int(v) for v in dark) + (255,),
               width=max(2, SS), joint="curve")

    outline(d, poly, tuple(int(v) for v in ink) + (255,), a.ink_width * SS)

    small = canvas.resize((W, H), Image.LANCZOS)
    al = np.asarray(small)[..., 3].astype(np.float32) / 255.0
    rgbo = np.asarray(small)[..., :3].astype(np.float32)
    comp = (raw.astype(np.float32) * (1 - al[..., None])
            + rgbo * al[..., None]).astype(np.uint8)
    drawn = al > 0.5

    # --- checks ---------------------------------------------------------------
    mask = dilate(drawn, a.mask_dilate)
    frac = float(mask.sum()) / (H * W)
    # >1 and alpha==0. The supersample is resolved with LANCZOS, which rings:
    # 232 px came back with alpha 0.000..0.004 and a one-level colour change,
    # which is rounding and not the compositor writing where it was not asked.
    # The check that matters is a VISIBLE write outside the object's own alpha.
    changed = np.abs(comp.astype(int) - raw.astype(int)).max(axis=2) > 1
    c1 = int((changed & (al <= 0.0)).sum())
    if c1:
        fails.append("C1 %d px changed outside the drawn slab" % c1)
    if frac > a.max_mask_frac:
        fails.append("C2 mask is %.1f%% of the frame, over the %.1f%% ceiling"
                     % (100 * frac, 100 * a.max_mask_frac))
    inner = erode(drawn, max(2, a.ink_width))
    if int(inner.sum()) < 500:
        inner = drawn
    lum_slab = float(np.asarray(Image.fromarray(comp).convert("L"))[inner].mean())
    lum_plate = float(np.asarray(Image.fromarray(raw).convert("L"))[region].mean())
    # C5 HERE IS A CONTRAST FLOOR, NOT A MATCH. The sapling tool asks the plant
    # to agree with the field because a seedling IS foliage; a bark board is
    # supposed to be a different material from a white shirt, and a slab that
    # matched the plate's mean would be invisible. What would be wrong is a
    # slab that is out of the picture's range altogether, so the check is that
    # it sits inside the plate's own p2..p98, and separately that it is DARKER
    # than the local mean -- which is what "held against a lit shirt" means.
    lo, hi = np.percentile(
        np.asarray(Image.fromarray(raw).convert("L")).astype(float), [2, 98])
    if not (lo <= lum_slab <= hi):
        fails.append("C5 slab luma %.1f is outside the plate's own 2..98 "
                     "range (%.1f..%.1f) -- it is not made of this picture's "
                     "light" % (lum_slab, lo, hi))
    if lum_slab >= lum_plate:
        fails.append("C5b slab luma %.1f is not darker than the local mean "
                     "%.1f -- r2 and r3 both returned a GLOWING board and "
                     "this is the check that refuses to hand-draw one"
                     % (lum_slab, lum_plate))

    geom = {
        "plate": a.plate, "plate_sha256": got,
        "board_box": [bx0, by0, bx1, by1], "hands_box": [hx0, hy0, hx1, hy1],
        "chin_y": a.chin, "board_w": bx1 - bx0, "board_h": by1 - by0,
        "shoulder_floor": a.shoulder_width,
        "bottom_edge_above_hand_top": hy0 - by1,
        "top_edge_below_chin": by0 - a.chin,
        "mask_fraction": round(frac, 4),
        "slab_luma": round(lum_slab, 1), "plate_region_luma": round(lum_plate, 1),
        "ink": list(ink), "light_dx": round(lx, 3), "light_dy": round(ly, 3),
    }
    for f in fails:
        print("FAIL  %s" % f)
    if not fails:
        print("all checks pass (G1 width floor, G2 grip, G3 below the chin, "
              "C1 containment, C2 mask ceiling, C5 in the plate's range, "
              "C5b darker than the shirt)")
    print("slab   %dx%d px  mask %.2f%% of frame  luma %.1f vs region %.1f"
          % (bx1 - bx0, by1 - by0, 100 * frac, lum_slab, lum_plate))

    if a.dry_run:
        print("\n-- dry run, nothing written. geometry:")
        print(json.dumps(geom, indent=1))
        return 1 if fails else 0
    if fails:
        print("\n!! refusing to write with %d failed check(s)." % len(fails))
        return 1

    if a.overlay_out:
        ov = Image.fromarray(raw.copy())
        od = ImageDraw.Draw(ov)
        od.polygon([(x / SS, y / SS) for x, y in poly], outline=(255, 0, 180))
        od.rectangle([hx0, hy0, hx1, hy1], outline=(0, 200, 255))
        ov.save(a.overlay_out)
        print("overlay written:", a.overlay_out)

    for path, img in ((a.out, Image.fromarray(comp)),
                      (a.mask_out, Image.fromarray(
                          (mask * 255).astype(np.uint8), "L"))):
        if not path:
            continue
        ap_ = path if os.path.isabs(path) else os.path.join(REPO, path)
        os.makedirs(os.path.dirname(ap_), exist_ok=True)
        img.save(ap_)
        print("wrote %s  sha256 %s" % (path, sha256_of(ap_)))
    if a.out:
        gp = (a.out if os.path.isabs(a.out)
              else os.path.join(REPO, a.out)) + ".geometry.json"
        with open(gp, "w", encoding="utf-8") as fh:
            json.dump(geom, fh, indent=1)
        print("geometry:", os.path.relpath(gp, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
