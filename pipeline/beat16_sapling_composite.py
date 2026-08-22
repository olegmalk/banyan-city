#!/usr/bin/env python3
r"""BEAT 16, THE RESTAGE: draw the canon two-leaf sapling LARGE into a field plate.

WHAT THIS IS. Step 2 of the beat-16 restage. Step 1 (`pipeline/derive_b16_field_0820.py`)
renders four FIELD plates by text with no plant in them; this draws the canon
sapling into the picked one and writes the init + mask that a single 0.30
inpaint pass finishes. Step 3 is one i2v motion sample off the finished plate.

WHY DRAWN AND NOT PROMPTED. The canon two-leaf sapling is not reachable by
words on this stack, and that is measured: the strongest wording available --
the numeral plus explicit negation of every wrong count -- returned 0 of 16
frames with two leaves. Cardinality is Class A in
pipeline/composite-init-pattern.md: no continuous encoding, so there is no knob
to turn. With a composited init the thing you want is not a sample from the
model. Four beats have now shipped plants this way (19, 15, 03, 13).

WHY THIS FILE EXISTS BESIDE beat19_sapling_composite.py. The b19 tool is fitted
to b19's plate -- hard-coded leaf tips, a ground-plane px/cm model, a whip to
erase and beat 18's fig to hang. Beat 16 needs none of that and needs one thing
b19 never did: THE PLANT IS THE SUBJECT AND IT IS LARGE. So the geometry here is
PARAMETRIC (root, height, tilt on the command line) rather than typed, which is
what lets it be aimed at whichever of the four field plates gets picked without
editing the source. The drawing primitives -- the taper, the ovate blade
profile, the crescent highlight, the no-midrib rule -- are b19's, copied
deliberately, because that is the shape four founder-screened plates already
carry and the shape canon's "average leaves" ruling describes.

THE THREE ANTI-DECAL CHOICES, from composite-init-pattern.md section 3, all
honoured here:
  1. PROCEDURAL, not a photograph and not a clone of nearby pixels.
  2. FITTED TO THE OBJECT, not to the mask. The mask is derived FROM the drawn
     silhouette (dilated), so the texture edge and the object edge are the same
     edge.
  3. THE PLATE'S OWN LIGHT IS KEPT. The direction is MEASURED from the low-pass
     luminance gradient of the plate region the plant will occupy, and the
     crescent highlight is placed on the lit side rather than on a side chosen
     by hand. The palette is sampled from the plate's own foliage, so the plant
     is made of the field's greens.

AND THE ONE THING BEAT 16 HAS TO WATCH THAT THE SMALL COMPOSITES DID NOT.
`/review/ep2-b16-leaf-0820` section 6 measured the big-leaf composite at 0.30
and found the pass did NOTHING: detail inside the region fell 10.45 -> 9.41
where a working pass holds it and moves it into edges, and the model moved just
as many pixels per pixel as on the version that worked (6.65 vs 6.23) across a
mask eight times the size. THE LESSON IS ABOUT MASK AREA, not about plants. So
this tool REFUSES a mask over `--max-mask-frac` of the frame (default 0.34) and
prints the fraction on every run. A seedling drawn as the subject can be large
and still sit well under a single leaf that filled 60-80% of the picture; if the
geometry asked for cannot, the tool says so before any GPU is booked.

CANON. `sapling-two-leaves` (founder, 2026-08-16) -- exactly two. And
`sapling-cotyledon-shape` (founder, 2026-08-17) -- "average leaves": ordinary,
plain, the shape anyone draws when you say leaf. NO exaggerated silhouette and
no leaf drawn as a feature; the restage exists precisely so that the SHOT does
not make a leaf its subject. The two blades differ in length by 6% and sit 5 px
apart on the stem, which is b19's anti-repeat rule (decal tell #4): two
identical blades mirrored about a vertical axis are one blade drawn twice.

$0. numpy + PIL. No model, no network, no GPU. Deterministic.

  python3 pipeline/beat16_sapling_composite.py \
      --plate farm-out/ep2-b16-field-fN-0820/ep2-b16-field-fN-0820-nocontrol.png \
      --root 416,1150 --height 620 \
      --out farm-out/ep2-b16-sapcomp-0820/16-why-sapcomp-0820.png \
      --mask-out farm-out/ep2-b16-sapcomp-0820/16-why-sapcomp-mask-0820.png \
      --overlay-out /tmp/b16-overlay.png

  --dry-run prints the geometry, the mask fraction and every check WITHOUT
  writing anything, which is how you aim it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# b19's drawing primitives, copied deliberately. See the module docstring.

LEAF_A, LEAF_B = 0.55, 1.00     # base roundness / tip sharpness
LEAF_NORM = max((t / 40.0) ** LEAF_A * (1.0 - t / 40.0) ** LEAF_B
                for t in range(1, 40))


def qbez(p0, p1, p2, t):
    u = 1.0 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def draw_taper(d, p0, p1, p2, w0, w1, fill, ink, ink_w=4):
    """A stem is a tapered polygon, not a stroked line: PIL's line joins at 3 px
    read as a chain of dots at 1x, which is decal tell #4."""
    left, right = [], []
    n = 26
    for i in range(n + 1):
        t = i / float(n)
        x, y = qbez(p0, p1, p2, t)
        dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
        dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
        L = max(1e-3, (dx * dx + dy * dy) ** 0.5)
        nx, ny = -dy / L, dx / L
        r = 0.5 * (w0 + (w1 - w0) * t)
        left.append((x + nx * r, y + ny * r))
        right.append((x - nx * r, y - ny * r))
    ring = left + right[::-1]
    d.polygon(ring, fill=fill, outline=ink)
    outline(d, ring, ink, ink_w)


def _blade(base, tip, width, k=1.0):
    """Half-widths along an ovate blade: round at the petiole, pointed at the
    apex. The normalisation constant is COMPUTED from the exponents and never
    typed -- b19's v6 typed 0.245 where the profile's own maximum is 0.436 and
    every blade came out 1.78x too fat, reading as a clover."""
    bx, by = base
    dx, dy = tip[0] - bx, tip[1] - by
    L = max(1e-3, (dx * dx + dy * dy) ** 0.5)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    out, n = [], 26
    for i in range(n + 1):
        t = i / float(n)
        r = (k * width * 0.5 * (t ** LEAF_A) * ((1.0 - t) ** LEAF_B) / LEAF_NORM)
        out.append((bx + ux * L * t, by + uy * L * t, nx * r, ny * r))
    return out


def outline(d, pts, ink, w):
    """A CEL LINE, not PIL's 1 px `outline=`.

    MEASURED FAILURE, first sample of this instrument. The plate's own character
    ink is median RGB (25,31,35) -- luma 30 -- and its outlines run a median of
    4 px, up to 28 on major contours. The first version drew the blades with a
    1 px `outline=` in a colour sampled from the erased weed, (49,72,50), luma
    63: half the darkness at a quarter of the width. At strength 0.30 with
    pad-crop 64 and blur 8 that line DISSOLVED -- the pass returned beautifully
    graded leaves with NO EDGE, soft airbrushed shapes sitting in front of a
    hard-inked cel drawing, which is the decal read arriving through line weight
    instead of through colour. b19's §5 law is that in this dialect a strong
    dark line IS an edge; a weak one is nothing.
    """
    if w <= 1:
        return
    d.line(list(pts) + [pts[0]], fill=ink, width=w, joint="curve")


def draw_leaf(d, base, tip, width, fill, hi, ink, lit_sign, ink_w=4):
    """One blade in the plate's dialect: mid-green ovate body, dark cel outline,
    a lighter CRESCENT along the LIT edge. NO MIDRIB IS DRAWN -- in this dialect
    a strong dark line IS an edge, and a composited internal line stronger than
    the object's own outline gets resolved as an object boundary. That is how
    beat 10 split its slab in two, and a leaf split down the middle is two
    leaves, which would break the count canon rules on.

    `lit_sign` is +1 or -1 and comes from the plate's MEASURED light direction,
    so the crescent lands on the side the field is actually lit from.
    """
    prof = _blade(base, tip, width)
    ring = ([(x + rx, y + ry) for x, y, rx, ry in prof]
            + [(x - rx, y - ry) for x, y, rx, ry in reversed(prof)])
    d.polygon(ring, fill=fill, outline=ink)
    hp = _blade(base, tip, width, k=0.96)
    s = float(lit_sign)
    d.polygon([(x + s * rx, y + s * ry) for x, y, rx, ry in hp]
              + [(x + s * rx * 0.34, y + s * ry * 0.34)
                 for x, y, rx, ry in reversed(hp)],
              fill=hi)
    # the line goes on LAST, over the fill and over the highlight, so the
    # crescent cannot cut it. Drawn at the plate's own line weight.
    outline(d, ring, ink, ink_w)


# ---------------------------------------------------------------------------

def dilate(m: np.ndarray, r: int) -> np.ndarray:
    """b19's exact 4-neighbour dilation, numpy only.

    The first version of this file used a PIL MaxFilter with a GaussianBlur
    fallback above r=5, which is a DIFFERENT operator either side of a
    threshold; b19's is one operator at every radius and is the one the mask
    arithmetic in that tool was tuned against.
    """
    out = m.copy()
    for _ in range(r):
        s = out.copy()
        s[1:, :] |= out[:-1, :]
        s[:-1, :] |= out[1:, :]
        s[:, 1:] |= out[:, :-1]
        s[:, :-1] |= out[:, 1:]
        out = s
    return out


def erode(m: np.ndarray, r: int) -> np.ndarray:
    """b19's 4-neighbour erosion, the dual of dilate."""
    out = m.copy()
    for _ in range(r):
        s = out.copy()
        s[1:, :] &= out[:-1, :]
        s[:-1, :] &= out[1:, :]
        s[:, 1:] &= out[:, :-1]
        s[:, :-1] &= out[:, 1:]
        out = s
    return out


def reach(seed: np.ndarray, allow: np.ndarray, limit: int = 3000) -> np.ndarray:
    """Flood `seed` through `allow`. numpy only, like the other composite tools."""
    cur = seed & allow
    for _ in range(limit):
        nxt = dilate(cur, 1) & allow
        if nxt.sum() == cur.sum():
            return nxt
        cur = nxt
    return cur


def weed_matte(a: np.ndarray, box, thresh: float, seed_thresh: float = None,
               forbid: np.ndarray = None) -> np.ndarray:
    """The plant ALREADY IN THE PLATE, inside `box`, by luminance against the field.

    Beat 16's input plate carries a thin weed the b15 composite replaced. Drawing
    a second sapling in front of it would put TWO plants in frame against canon
    `sapling-two-leaves`, so it has to come out before anything is drawn.

    A THRESHOLD ALONE DOES NOT WORK AND THAT IS MEASURED, NOT ASSUMED. The field
    reads luma 212.6 median / 208.3 p05 in the upper frame, so `lum < 170`
    separates the weed there cleanly — but the field DARKENS toward the near
    foreground (p05 120.5 below y≈1000), so widening the box grew the matte
    monotonically: 4,292 px at one box, 7,319, 12,427, 15,904 at the next three.
    That is the threshold eating field, not finding more weed.

    So the matte is b19's: FLOOD FROM A DARK SEED. `seed_thresh` picks the weed's
    own ink — far darker than any field streak — and `reach` grows it only
    through pixels under `thresh`, inside the box, and never into `forbid` (the
    figure). Disconnected field wisps are excluded by construction because
    nothing joins them to the stem, and the box can then be drawn generously
    instead of tuned to a pixel.
    """
    x0, y0, x1, y1 = box
    b = np.zeros(a.shape[:2], bool)
    b[y0:y1, x0:x1] = True
    if forbid is not None:
        b &= ~forbid
    R, G, B = a[..., 0].astype(np.int16), a[..., 1].astype(np.int16), a[..., 2].astype(np.int16)
    lum = 0.299 * R + 0.587 * G + 0.114 * B
    allow = b & (lum < thresh)
    if seed_thresh is None:
        return allow
    return reach(b & (lum < seed_thresh), allow)


def fill_from_boundary(a: np.ndarray, hole: np.ndarray,
                       body: np.ndarray = None, iters: int = 3) -> np.ndarray:
    """Fill `hole` from the region's OWN boundary, per-row. b19's §12 method.

    No clone survives a luminance gradient, and this plate is a horizontally
    banded field — so the fill is a per-row linear interpolation between the
    nearest surviving pixels on that row, which reproduces the banding exactly,
    and a few diffusion passes then remove the row-to-row seams. NOTHING IS
    COPIED FROM ELSEWHERE IN THE FRAME, so decal tell #4 (a visible repeat) is
    impossible by construction.

    AND IT FILLS WITHIN CLASS, which is b19's other half and is load-bearing
    here rather than theoretical. The first run of this port asserted the hole
    was field-only and C0 refused it: 1,686 px of ink sit within 24 px of the
    weed at x 250–288, y 533–635, and that is HIS KNEE AND HAND. Interpolating
    across it would average field with skin on those rows — b19's v11 did
    exactly this and left a 22 px grey smear where a vine ran up to a cheek. So
    a hole pixel in the background is filled only from surviving BACKGROUND on
    its row, and never from the figure.
    """
    out = a.astype(np.float32).copy()
    H, W = a.shape[:2]
    if body is None:
        body = np.zeros((H, W), bool)
    xs = np.arange(W, dtype=np.float32)
    for cls in (~body, body):
        for y in range(H):
            row = hole[y] & cls[y]
            if not row.any():
                continue
            keep = (~hole[y]) & cls[y]
            if keep.sum() < 6:
                continue
            for c in range(3):
                out[y, row, c] = np.interp(xs[row], xs[keep], out[y, keep, c])
    for _ in range(iters):
        blur = np.asarray(Image.fromarray(
            np.clip(out, 0, 255).astype(np.uint8)
        ).filter(ImageFilter.GaussianBlur(2.0))).astype(np.float32)
        out[hole] = blur[hole]
    return np.clip(out, 0, 255).astype(np.uint8)


def sha256_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _character_ink(a: np.ndarray) -> tuple:
    """The darkest ink in the plate — the colour its FIGURES are outlined in.

    Taken as the median of everything under a fixed INK CUTOFF, not as a
    percentile. A percentile finds the darkest pixels in the frame, which are the
    deepest points of the ink and its shadows -- 0.5% returned (2,2,2) on the b15
    plate, near pure black, and true black reads as pasted in this dialect. The
    median of `lum < 60` is what the outlines actually are: (25,31,35) on that
    same plate, a desaturated blue-black, which is the number this was measured
    against by hand.
    """
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    sel = lum < 60.0
    if int(sel.sum()) < 200:            # a plate with no ink at all
        sel = lum <= np.percentile(lum, 1.0)
    return tuple(int(v) for v in np.median(a[sel], axis=0))


def palette_from_erased(a: np.ndarray, weed: np.ndarray) -> dict:
    """Sample the drawn plant's colours FROM THE PLANT THIS TOOL IS DELETING.

    b19's law and the strongest source available: same frame, same light, same
    checkpoint, same line weight — and it is NOT decal tell #4, because the
    source pixels do not survive into the output. Falls back to the field's
    greens (foliage_palette) when there is nothing to erase.
    """
    R, G, B = a[..., 0].astype(np.int16), a[..., 1].astype(np.int16), a[..., 2].astype(np.int16)
    lum = 0.299 * R + 0.587 * G + 0.114 * B
    leaf = weed & (G - B > 18) & (lum < 190)
    ink = weed & (lum < 90)
    if int(leaf.sum()) < 250 or int(ink.sum()) < 40:
        return {}
    px = a[leaf]
    return {"dark": tuple(int(v) for v in np.percentile(px, 18, axis=0)),
            "mid": tuple(int(v) for v in np.percentile(px, 45, axis=0)),
            "light": tuple(int(v) for v in np.percentile(px, 86, axis=0)),
            # THE INK IS THE PLATE'S CHARACTER INK, NOT THE WEED'S. The weed is
            # a background prop drawn with a light, thin line; the sapling is
            # this shot's SUBJECT and has to carry the line weight the figure
            # carries. Measured on this plate: his ink is median (25,31,35),
            # luma 30, while the weed's darkest green is (49,72,50), luma 63.
            # The first sample outlined the blades with the weed's colour and
            # the 0.30 pass erased the edge entirely.
            "ink": _character_ink(a),
            "n_sampled": int(leaf.sum()), "source": "the erased weed"}


def foliage_palette(a: np.ndarray, region: np.ndarray) -> dict:
    """The plant is made of the FIELD'S OWN GREENS, sampled from the plate.

    A palette invented in code is decal tell #2 (a pattern ignoring the frame's
    light) arriving through colour instead of through shading. `region` is where
    the plant will go; the sample is taken from the green-dominant pixels there,
    so a plate with warm sunlit grass yields a warm plant.
    """
    R, G, B = a[..., 0].astype(np.int16), a[..., 1].astype(np.int16), a[..., 2].astype(np.int16)
    green = region & (G > R + 6) & (G > B + 6)
    if int(green.sum()) < 400:          # fall back to the whole lower half
        h = a.shape[0]
        low = np.zeros(a.shape[:2], bool)
        low[h // 2:, :] = True
        green = low & (G > R + 4) & (G > B + 4)
    if int(green.sum()) < 1:
        # A PLATE WITH NO GREEN PIXEL AT ALL. Caught 2026-08-21 on the sapling
        # LoRA plate set: `ep3-sapfld4-u05` is a DRY TAN grass plain, so both
        # the region sample and the whole-lower-half fallback returned zero
        # pixels and pct() died on `index 0 is out of bounds for axis 0 with
        # size 0` -- a traceback where the tool's whole design is to refuse with
        # a reason. There is no honest repair here: "the plant is made of the
        # FIELD'S OWN GREENS" has no greens to be made of, and inventing a
        # palette is decal tell #2 by definition. So it refuses, and the plate
        # is dropped from the set rather than composited badly.
        raise SystemExit(
            "!! this plate has NO green-dominant pixel, in the plant's region "
            "or in its whole lower half, so the palette cannot be sampled from "
            "it. The plant would have to be given an invented colour, which is "
            "decal tell #2 (a pattern that ignores the frame's light) arriving "
            "through colour. Use a plate with living green in it, or extend "
            "this function ON PURPOSE with a non-green foliage rule and say "
            "what it samples.")
    px = a[green].astype(np.float32)
    lum = 0.299 * px[:, 0] + 0.587 * px[:, 1] + 0.114 * px[:, 2]
    order = np.argsort(lum)
    px = px[order]
    def pct(p):
        return tuple(int(v) for v in px[int(max(0, min(len(px) - 1, p * len(px))))])
    dark, mid, light = pct(0.14), pct(0.50), pct(0.88)
    # The ink is the plate's own darkest line colour, not black: this dialect
    # outlines in a dark desaturated navy/green, and true black reads as pasted.
    # Same law as palette_from_erased: the SUBJECT is inked in the plate's
    # character ink, not in a darkened tint of its own fill.
    ink = _character_ink(a)
    return {"dark": dark, "mid": mid, "light": light, "ink": ink,
            "n_sampled": int(green.sum())}


def light_direction(a: np.ndarray, region: np.ndarray):
    """MEASURED, not chosen: the low-pass luminance gradient over the region the
    plant will occupy. Returns (dx, dy) normalised, pointing toward the light."""
    g = np.asarray(Image.fromarray(a).convert("L").filter(
        ImageFilter.GaussianBlur(24)), dtype=np.float32)
    gy, gx = np.gradient(g)
    m = region
    dx = float(gx[m].mean()) if m.any() else 0.0
    dy = float(gy[m].mean()) if m.any() else 0.0
    n = max(1e-6, (dx * dx + dy * dy) ** 0.5)
    # gradient points toward INCREASING luminance, i.e. toward the light
    return dx / n, dy / n


def parse_xy(s: str):
    x, y = s.split(",")
    return (float(x), float(y))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plate", required=True, help="repo-relative or absolute")
    ap.add_argument("--plate-sha256", default=None,
                    help="asserted if given; printed either way")
    ap.add_argument("--root", required=True, type=parse_xy,
                    help="x,y where the stem meets the ground")
    ap.add_argument("--height", required=True, type=float,
                    help="stem apex height above the root, px")
    ap.add_argument("--tilt", type=float, default=6.0,
                    help="degrees the stem leans, + = to the right. A stem "
                         "dead vertical reads as drawn; a real seedling leans.")
    ap.add_argument("--leaf-frac", type=float, default=0.46,
                    help="leaf length as a fraction of stem height. b19 used "
                         "0.255 of the WHOLE plant on a 30 px seedling; beat "
                         "16 is a close-up and the leaves carry the frame.")
    ap.add_argument("--leaf-spread", type=float, default=62.0,
                    help="degrees each blade sits off the stem axis")
    ap.add_argument("--max-mask-frac", type=float, default=0.34,
                    help="REFUSE above this. The 0.30 pass did nothing on a "
                         "mask eight times the working size (b16 leafcomp, "
                         "detail 10.45 -> 9.41); this is the guard that keeps "
                         "the restage from repeating it.")
    ap.add_argument("--ink-width", type=int, default=4,
                    help="cel-outline width in px. DEFAULT MEASURED ON THE "
                         "PLATE, not chosen: the b15 plate's own character "
                         "outlines run a median of 4 px (up to 28 on major "
                         "contours) in ink of median RGB (25,31,35). The first "
                         "sample of this instrument used PIL's 1 px `outline=` "
                         "in the erased weed's (49,72,50) -- half the darkness "
                         "at a quarter of the width -- and the 0.30 pass "
                         "dissolved the edge completely, returning graded "
                         "leaves with no line in front of a hard-inked drawing.")
    ap.add_argument("--mask-dilate", type=int, default=9)
    ap.add_argument("--erase-box", default=None,
                    help="x0,y0,x1,y1 — a plant ALREADY in the plate, erased "
                         "before anything is drawn. Two plants in frame breaks "
                         "canon sapling-two-leaves, and a 0.30 pass PRESERVES a "
                         "weed rather than removing one (12 of 40 steps from a "
                         "latent that still carries the init), so masking it is "
                         "not enough — it has to be gone from the pixels.")
    ap.add_argument("--erase-lum", type=float, default=170.0,
                    help="luma below which a pixel inside --erase-box is the "
                         "weed. Default measured on the b15 mac plate: field "
                         "median 212.6 / p05 208.3, weed box p05 81.8.")
    ap.add_argument("--erase-seed-lum", type=float, default=120.0,
                    help="luma of the weed's own INK, the flood seed. The matte "
                         "is grown from here through --erase-lum pixels, so "
                         "disconnected field wisps are excluded by construction "
                         "and the box can be drawn generously. With this on, "
                         "the matte is 3,988 px and IDENTICAL at box bottoms "
                         "620 and 640 — a threshold-only matte grew 4,292 -> "
                         "15,904 across four boxes.")
    ap.add_argument("--erase-grow", type=int, default=4,
                    help="px to dilate the matte before filling. WITHOUT THIS "
                         "THE ERASE LEAVES A STENCIL: the flood takes the "
                         "weed's ink and leaves its lit edge and antialiasing "
                         "behind, and the first run of this port came back with "
                         "a pale ghost of the whole plant standing in the field "
                         "-- the dark gone, the outline intact. The fringe is "
                         "brighter than any sane --erase-lum and darker than "
                         "the field, so it is removed geometrically instead of "
                         "by threshold. Re-subtracted from the body afterwards "
                         "so growth cannot eat his edge.")
    ap.add_argument("--fill-iters", type=int, default=3,
                    help="diffusion passes after the per-row interpolation")
    ap.add_argument("--erase-clearance", type=int, default=24,
                    help="C0: how far out to look for ink of another class "
                         "beside the hole. Reported always; only refuses when "
                         "--body-box is not given, because without a class map "
                         "the fill would average across it.")
    ap.add_argument("--body-box", default=None,
                    help="x0,y0,x1,y1 where the FIGURE is; SEMICOLON-SEPARATE "
                         "SEVERAL. The per-row fill runs within class, so a "
                         "hole in the background is filled only from surviving "
                         "background, and anything inside a body box is never "
                         "matted for erasure. Required when C0 finds another "
                         "object's ink beside the hole; on the b15 plate it "
                         "does (his knee and hand at x 250-288). ONE RECTANGLE "
                         "IS NOT ENOUGH THERE and the first run proved it: a "
                         "single x>=250 box protected the weed's top-right leaf "
                         "as if it were him and left it standing in the output. "
                         "His true left edge is x~322 above y 420 and x~254 "
                         "below it, so it takes two.")
    # AN OPTIONAL FIG, OFF BY DEFAULT, so the five plates this tool has already
    # produced stay reproducible byte for byte from their own command lines.
    # Beat 19 is the only beat that needs one: its whole action is a fruit
    # coming off a stem, and every motion attempt on it before 2026-08-22 asked
    # for that fall with no fruit in frame. The b19 tool that CAN draw one has
    # b19's old plate typed into it -- leaf tips, a ground-plane px/cm model,
    # two whips to erase -- so aiming it at a new plate is an edit to its
    # source. This is the parametric version of just the fruit.
    ap.add_argument("--fig", default=None,
                    help="cx,cy,rx,ry of ONE fig hanging on the stem")
    ap.add_argument("--fig-hue", default="108,58,160",
                    help="canon violet. Beat 18's ratified fig measured in the "
                         "violet/magenta family and beat 19's plate's own "
                         "fruits measured 266-274 deg; the plate being drawn "
                         "into may contain no violet at all, so the HUE is "
                         "canon's and only the VALUE is fitted to the plate -- "
                         "the same rule beat06_board_composite.py states for "
                         "bark. MATTE: canon wants no specular, and beat 18's "
                         "own verdict flags its glossy highlight as a caveat.")
    ap.add_argument("--out", default=None)
    ap.add_argument("--mask-out", default=None)
    ap.add_argument("--overlay-out", default=None,
                    help="the drawn silhouette outlined on the plate, for a "
                         "geometry look before anything is committed")
    ap.add_argument("--dry-run", action="store_true",
                    help="print geometry and checks, write nothing")
    a = ap.parse_args()

    plate = a.plate if os.path.isabs(a.plate) else os.path.join(REPO, a.plate)
    if not os.path.isfile(plate):
        print("!! plate not found: %s" % plate)
        return 1
    have = sha256_of(plate)
    if a.plate_sha256 and have != a.plate_sha256:
        print("!! plate sha mismatch\n   want %s\n   have %s"
              % (a.plate_sha256, have))
        return 1
    img = Image.open(plate).convert("RGB")
    W, H = img.size
    raw = np.asarray(img)
    print("plate  %dx%d  sha256 %s" % (W, H, have))

    # ---- 0. erase the plant the plate already has -------------------------
    weed = np.zeros((H, W), bool)
    # The matte BEFORE --erase-grow. C5 measures the erased plant's own
    # colour off this one, so the dilated fringe -- which is field pixels
    # by construction -- cannot pull the reference toward the backdrop.
    weed_core = weed
    arr = raw
    if a.erase_box:
        box = tuple(int(v) for v in a.erase_box.split(","))
        if len(box) != 4:
            print("!! --erase-box wants x0,y0,x1,y1")
            return 1
        body = np.zeros((H, W), bool)
        for chunk in (a.body_box or "").split(";"):
            if not chunk.strip():
                continue
            bx = tuple(int(v) for v in chunk.split(","))
            if len(bx) != 4:
                print("!! --body-box wants x0,y0,x1,y1 (semicolon-separated)")
                return 1
            body[bx[1]:bx[3], bx[0]:bx[2]] = True
        # THE FIGURE IS NEVER ERASED. At x1=265 the matte took 392 px on his
        # side of the class line -- the left edge of his knee, which shares the
        # weed's luma. Subtracting the body makes the erase box safe to draw
        # generously instead of tuned to a pixel, which is the difference
        # between a box that is right and a box that happens to be right.
        weed = weed_matte(raw, box, a.erase_lum,
                          seed_thresh=a.erase_seed_lum, forbid=body)
        core = int(weed.sum())
        weed_core = weed.copy()
        if a.erase_grow:
            weed = dilate(weed, a.erase_grow) & ~body
        n = int(weed.sum())
        if a.erase_grow:
            print("erase  matte %d px -> %d after growing %d px (the lit fringe "
                  "the threshold cannot see)" % (core, n, a.erase_grow))
        if n < 200:
            print("!! --erase-box matted only %d px at luma<%s -- the box or "
                  "the threshold is wrong, and erasing nothing silently is how "
                  "two plants reach the frame." % (n, a.erase_lum))
            return 1
        ys, xs = np.where(weed)
        # C0: the hole must be FIELD ONLY. b19 filled within class because its
        # hole ran into the figure; this asserts the situation b19 had to handle
        # does not arise, instead of assuming it.
        lum_all = (0.299 * raw[..., 0] + 0.587 * raw[..., 1]
                   + 0.114 * raw[..., 2])
        ink_outside = (lum_all < a.erase_lum) & ~weed
        near = dilate(weed, a.erase_clearance) & ~weed
        bleed = int((ink_outside & near).sum())
        # C0c THE MATTE IS NOT CLIPPED BY ITS OWN BOX. If it runs to an edge the
        # box is cutting the weed in half and half a weed survives into the
        # frame, which is the exact canon failure this erase exists to prevent.
        # ...UNLESS THE BOX EDGE IS THE IMAGE EDGE, in which case there is no
        # wider box to draw and the thing cutting the weed is the FRAME. Beat
        # 12's plate is the case: its two leaves run off both sides of a
        # 704-wide picture, so `xs.min()==box[0]==0` and `xs.max()==box[2]-1==
        # 703` are both true of a matte that is complete. Refusing there would
        # ask for a box outside the image. The guard's job is "your box is too
        # small"; at the frame boundary that sentence has no meaning, and the
        # exemption is written as a coincidence with 0/W/H rather than as a
        # flag, so it cannot be used to wave through a genuinely cut matte.
        at_img = {"left": box[0] == 0, "top": box[1] == 0,
                  "right": box[2] >= W, "bottom": box[3] >= H}
        clipped = [nm for nm, v, lim in
                   (("left", xs.min(), box[0]), ("top", ys.min(), box[1]),
                    ("right", xs.max(), box[2] - 1), ("bottom", ys.max(), box[3] - 1))
                   if v == lim and not at_img[nm]]
        if clipped:
            print("!! C0c the matte touches the %s edge of --erase-box, so the "
                  "box is cutting the weed rather than containing it. Widen it."
                  % "/".join(clipped))
            return 1
        print("erase  %d px  bbox x %d..%d y %d..%d  |  C0 other-class ink "
              "within %d px of the hole: %d  |  class map: %s"
              % (n, xs.min(), xs.max(), ys.min(), ys.max(), a.erase_clearance,
                 bleed, a.body_box or "NONE"))
        if bleed and not a.body_box:
            print("!! C0 FAILED: ink of another object sits beside the hole and "
                  "there is no class map, so a per-row fill would average the "
                  "field with whatever that ink belongs to -- b19's v11 left a "
                  "22 px grey smear doing exactly this. Pass --body-box.")
            return 1
        arr = fill_from_boundary(raw, weed, body=body, iters=a.fill_iters)

    # ---- geometry ---------------------------------------------------------
    rx, ry = a.root
    tilt = np.radians(a.tilt)
    apex = (rx + a.height * np.sin(tilt), ry - a.height * np.cos(tilt))
    # the stem bows the OTHER way from its lean, which is what a stem carrying
    # weight does and what stops the curve reading as an arc of a circle
    mid = (rx + a.height * 0.52 * np.sin(tilt) - a.height * 0.06 * np.cos(tilt),
           ry - a.height * 0.52 * np.cos(tilt))
    leaf_len = a.leaf_frac * a.height
    spread = np.radians(a.leaf_spread)

    # the region the plant will occupy, used to sample palette and light BEFORE
    # anything is drawn
    region = np.zeros((H, W), bool)
    y0 = int(max(0, min(H - 1, apex[1] - leaf_len)))
    y1 = int(max(0, min(H, ry + 10)))
    x0 = int(max(0, min(W - 1, rx - leaf_len)))
    x1 = int(max(0, min(W, rx + leaf_len)))
    region[y0:y1, x0:x1] = True

    # THE PALETTE COMES OFF THE ERASED WEED WHEN THERE IS ONE (b19's law: the
    # strongest source is the plant you are deleting, and it cannot be a repeat
    # because those pixels do not survive). The field's greens are the fallback.
    pal = palette_from_erased(raw, weed) if weed.any() else {}
    if not pal:
        pal = foliage_palette(arr, region)
        pal["source"] = "the field's own greens"
    ldx, ldy = light_direction(arr, region)
    print("palette (%s, %d px)  dark %s  mid %s  light %s  ink %s"
          % (pal["source"], pal["n_sampled"], pal["dark"], pal["mid"],
             pal["light"], pal["ink"]))
    print("light direction MEASURED from the plate: dx %+.3f dy %+.3f" % (ldx, ldy))

    # which side of a blade is lit: the sign of the light's x component decides
    lit_sign = 1.0 if ldx >= 0 else -1.0

    layer = Image.fromarray(arr.copy())
    d = ImageDraw.Draw(layer)
    ink = pal["ink"]
    stem_col = tuple(int(min(255, v)) for v in np.array(pal["dark"]) * 0.88 + 12)
    stem_w0 = max(4.0, a.height * 0.030)
    stem_w1 = max(2.0, a.height * 0.013)
    draw_taper(d, (rx, ry), mid, apex, stem_w0, stem_w1, stem_col, ink,
               ink_w=a.ink_width)

    # TWO LEAVES, NOT A MIRRORED PAIR: 5 px apart on the stem and 6% apart in
    # length. Decal tell #4 is a visible repeat, and two identical blades
    # reflected about a vertical axis are one.
    leaves = []
    for side, dy, k in ((-1.0, 5.0, 1.00), (+1.0, 0.0, 1.06)):
        node = (apex[0] + side * 1.0, apex[1] + dy)
        ang = tilt + side * spread
        ln = leaf_len * k
        tip = (node[0] + ln * np.sin(ang), node[1] - ln * np.cos(ang) * 0.62)
        draw_leaf(d, node, tip, ln * 0.40, pal["mid"], pal["light"], ink,
                  lit_sign, ink_w=a.ink_width)
        leaves.append({"side": side, "node": [round(v, 1) for v in node],
                       "tip": [round(v, 1) for v in tip], "len": round(ln, 1)})

    fig_geom = None
    if a.fig:
        fcx, fcy, frx, fry = (float(v) for v in a.fig.split(","))
        # VALUE FROM THE PLATE, HUE FROM CANON. Same rule as the bark board:
        # a field of green grass contains no violet to sample, and tinting the
        # fruit green to match the frame would be drawing the wrong object.
        fhue = np.array([float(v) for v in a.fig_hue.split(",")])
        lp0 = np.asarray(Image.fromarray(arr).convert("L")).astype(float)
        loc = np.zeros((H, W), bool)
        loc[max(0, int(fcy - 3 * fry)):min(H, int(fcy + 3 * fry)),
            max(0, int(fcx - 3 * frx)):min(W, int(fcx + 3 * frx))] = True
        tgt = float(np.percentile(lp0[loc], 22)) if loc.any() else 90.0
        hl = 0.299 * fhue[0] + 0.587 * fhue[1] + 0.114 * fhue[2]
        # THE SCALE IS CAPPED AT 1.0 AND THAT IS NOT A FUDGE. Fitting the
        # value by a naive multiply blows the hue out when the local field is
        # BRIGHT -- on beat 19's plate the grass beside the plant reads p22 at
        # a luma above canon violet's own, and the first run returned
        # (255,143,255), a hot pink, which is neither canon's colour nor
        # anything in the picture. A ripe fig is a DARK object against a lit
        # field (beat 06's C5b makes the same argument for bark), so the fit
        # may darken canon's violet toward the plate and may not brighten it
        # past itself.
        fmid = np.clip(fhue * min(1.0, tgt / max(1.0, hl)), 0, 255)
        fdark = np.clip(fmid * 0.70, 0, 255)
        # A PEDICEL FIRST, so the fruit hangs off the stem instead of floating
        # beside it -- "a bead on a thread" is exactly what beat 19's wording
        # ladder kept producing and what the drawing exists to avoid.
        # abs(), and the first version did not have it. The apex is ABOVE the
        # root, so apex[1] - ry is NEGATIVE; `max(1.0, ...)` clamped it to 1.0
        # and the pedicel was drawn to x = -7000, clipped to the frame edge,
        # which C3 caught as "the plant touches the frame edge". A guard
        # catching a sign error is the guard doing its job, and the fix is the
        # arithmetic rather than the guard.
        span = max(1.0, abs(apex[1] - ry))
        t_up = min(1.0, max(0.0, (ry - (fcy - fry)) / span))
        stem_x = rx + (apex[0] - rx) * t_up
        d.line([(stem_x, fcy - fry * 1.9), (fcx, fcy - fry * 0.9)],
               fill=tuple(int(v) for v in stem_col), width=max(2, a.ink_width - 1))
        ring = [(fcx + frx * np.cos(t * 2 * np.pi / 96.0),
                 fcy + fry * np.sin(t * 2 * np.pi / 96.0) * (1.0 + 0.16 * np.cos(t * 2 * np.pi / 96.0)))
                for t in range(96)]
        d.polygon(ring, fill=tuple(int(v) for v in fmid))
        # ONE shadow crescent on the UNLIT side and NO specular: canon's fig is
        # matte, and beat 18's own verdict names its gloss as the caveat.
        sh = [(fcx - lit_sign * frx * 0.30 + frx * 0.72 * np.cos(t * 2 * np.pi / 64.0),
               fcy + fry * 0.78 * np.sin(t * 2 * np.pi / 64.0)) for t in range(64)]
        d.polygon(sh, fill=tuple(int(v) for v in fdark))
        outline(d, ring, ink, a.ink_width)
        fig_geom = {"centre": [fcx, fcy], "radii": [frx, fry],
                    "hue_source": "canon", "value_source": "plate p22 local",
                    "fill": [int(v) for v in fmid]}
        print("fig    %.0fx%.0f px at (%.0f,%.0f)  canon hue %s -> plate value %s"
              % (2 * frx, 2 * fry, fcx, fcy, tuple(int(v) for v in fhue),
                 tuple(int(v) for v in fmid)))

    drawn = (np.abs(np.asarray(layer).astype(np.int16)
                    - arr.astype(np.int16)).max(axis=2) > 0)

    # a drawn edge in the plate's own ink, inset 2 px, so the new content does
    # not run off a cliff into the field (composite-init-pattern section 3)
    base = np.asarray(layer).astype(np.float32)
    rim = dilate(drawn, 1) & ~drawn
    base[rim] = base[rim] * 0.42 + np.array(ink, np.float32) * 0.58

    # THE PLATE'S OWN SHADING FIELD, re-applied multiplicatively over the drawn
    # plant so a lit corner stays lit. Without this the plant is uniformly lit
    # inside a frame that is not, which is decal tell #2.
    lp = np.asarray(Image.fromarray(arr).convert("L").filter(
        ImageFilter.GaussianBlur(40)), dtype=np.float32)
    ref = float(np.median(lp[region])) if region.any() else float(np.median(lp))
    field = np.clip(lp / max(1.0, ref), 0.78, 1.22)
    sel = drawn | rim
    base[sel] = base[sel] * field[sel][..., None]

    # contact shading where the stem meets the ground, so the plant is ROOTED
    # and not standing on the field like a sticker
    yy, xx = np.mgrid[0:H, 0:W]
    rxr = max(14.0, a.height * 0.085)
    ryr = max(6.0, a.height * 0.028)
    q = (((xx - rx) / rxr) ** 2 + ((yy - ry - 3) / ryr) ** 2)
    shade = np.clip(1.0 - q, 0.0, 1.0) * 0.30
    base = base * (1 - shade[..., None] * 0.62)
    comp = np.clip(base, 0, 255).astype(np.uint8)

    # `> 0` and not a tolerance: `shade` is clip(1-q,0,1)*0.30, so it is exactly
    # zero outside the contact ellipse and non-zero everywhere inside it. A
    # threshold of 0.004 leaves a ring where the multiply still moves a channel
    # by one count, and C1 then reports 41 px the tool really did write.
    contact = shade > 0.0
    touched = drawn | rim | contact

    # ---- the mask a finishing pass would use ------------------------------
    # b19's form exactly: it covers the DRAWN plant AND the ERASED VACANCY, not
    # only what was painted. A mask fitted to the paint alone makes the result a
    # foregone conclusion and measures nothing (beat 14's C8) — and here it
    # would also leave the filled-in field unfinished, a smooth interpolated
    # patch in a frame of drawn grass.
    mask = np.zeros((H, W), np.uint8)
    mask[dilate(touched, a.mask_dilate) | dilate(weed, 5)] = 255
    frac = float((mask > 0).sum()) / float(W * H)

    ys, xs = np.where(drawn)
    geom = {
        "plate": os.path.relpath(plate, REPO), "plate_sha256": have,
        "size": [W, H], "root": [round(rx, 1), round(ry, 1)],
        "apex": [round(apex[0], 1), round(apex[1], 1)],
        "height_px": a.height, "tilt_deg": a.tilt,
        "leaf_len_px": round(leaf_len, 1), "leaves": leaves,
        "light_dx": round(ldx, 3), "light_dy": round(ldy, 3),
        "lit_side": "right" if lit_sign > 0 else "left",
        "palette": {k: (list(v) if isinstance(v, tuple) else v)
                    for k, v in pal.items()},
        "erased_px": int(weed.sum()),
        "erase_box": a.erase_box,
        "mask_fraction": round(frac, 4),
        "plant_extent": ([int(xs.min()), int(xs.max()),
                          int(ys.min()), int(ys.max())] if len(xs) else None),
        "plant_fraction": round(float(drawn.sum()) / float(W * H), 4),
    }
    print("plant extent x %d..%d y %d..%d, %.2f%% of frame; MASK %.2f%% of frame"
          % (geom["plant_extent"][0], geom["plant_extent"][1],
             geom["plant_extent"][2], geom["plant_extent"][3],
             100 * geom["plant_fraction"], 100 * frac))

    # ---- checks. A failed check stops the run. ----------------------------
    fails = []
    o = comp.astype(np.int16)
    b0 = arr.astype(np.int16)
    # C0b THE ERASE STAYED IN ITS HOLE. fill_from_boundary only assigns inside
    # `hole`, but that is a property of the code and this is the check that
    # makes it a property of the OUTPUT — a fill that leaks is how b19's v11 put
    # a grey smear on a cheek.
    if weed.any():
        leaked = int((np.abs(arr.astype(np.int16) - raw.astype(np.int16)
                             ).max(axis=2) > 0)[~weed].sum())
        if leaked:
            fails.append("C0b the erase wrote %d px outside its own matte"
                         % leaked)
    changed = np.abs(o - b0).max(axis=2) > 0
    c1 = int((changed & ~touched).sum())
    if c1:
        fails.append("C1 %d px changed outside the drawn plant and its contact "
                     "shadow -- the compositor wrote where it was not asked" % c1)
    if frac > a.max_mask_frac:
        fails.append("C2 mask is %.1f%% of the frame, over the %.1f%% ceiling. "
                     "The 0.30 pass measurably DOES NOTHING on a mask this "
                     "size (b16 leafcomp: detail 10.45 -> 9.41 inside the "
                     "region). Draw the plant smaller or raise the ceiling on "
                     "purpose and say why."
                     % (100 * frac, 100 * a.max_mask_frac))
    if len(xs) and (xs.min() < 2 or xs.max() > W - 3 or ys.min() < 2):
        fails.append("C3 the plant touches the frame edge -- 'close on the "
                     "WHOLE sapling' means the whole of it is in the picture")
    if abs(leaves[0]["len"] - leaves[1]["len"]) < 0.02 * leaf_len:
        fails.append("C4 the two blades are the same length: a mirrored pair is "
                     "decal tell #4, one blade drawn twice")
    # C5 MEASURES THE FILL, NOT THE OUTLINE, and that is a correction rather
    # than a loosening. The check exists to catch a plant whose COLOUR does not
    # belong to the frame. A correct cel outline is supposed to be near-black,
    # so the moment the ink was fixed from 1 px of (49,72,50) to 4 px of
    # (25,31,35) the whole-silhouette mean fell 46.4 below the field and C5
    # fired on the fix. Eroding the silhouette past the line measures the body
    # colour, which is what the check was always about; the ink has its own
    # check in the eye, and C1 still bounds where any of it may be written.
    interior = erode(drawn, max(2, a.ink_width))
    if int(interior.sum()) < 500:
        interior = drawn
    lum_plant = float(np.asarray(Image.fromarray(comp).convert("L"))[interior].mean())
    # AND C5's REFERENCE IS THE ERASED PLANT WHEN THERE WAS ONE. The check asks
    # "does this plant's colour belong in this picture", and it answers that by
    # comparing to the surrounding field -- which is right for a seedling in
    # grass and WRONG for one silhouetted against sky. Beat 12's plate is the
    # second case: its two leaves sit against bright cloud at field luma 220
    # while the leaves the plate itself drew measure 88, so the field test
    # rejects a plant that is the exact colour of the one being replaced. When
    # --erase-box supplied a weed, the palette is already sampled from that
    # weed (palette_from_erased), so the honest reference is the weed too, and
    # the check becomes STRICTER rather than looser: the new plant must match
    # the plant the plate drew, not merely be within 46 of its backdrop.
    lum_field = float(np.asarray(Image.fromarray(arr).convert("L"))[region].mean())
    ref_name, lum_ref, tol = "field", lum_field, 46
    if weed.any():
        lum_ref = float(np.asarray(
            Image.fromarray(raw).convert("L"))[weed_core].mean())
        ref_name, tol = "erased plant", 24
    geom["plant_fill_luma"] = round(lum_plant, 1)
    geom["field_mean_luma"] = round(lum_field, 1)
    geom["c5_reference"] = ref_name
    geom["c5_reference_luma"] = round(lum_ref, 1)
    geom["c5_measures"] = "the drawn plant's FILL, silhouette eroded by ink_width"
    if fig_geom:
        geom["fig"] = fig_geom
    if abs(lum_plant - lum_ref) > tol:
        fails.append("C5 the plant's FILL luma %.1f is %.1f away from the "
                     "%s's %.1f (tolerance %d) -- it will read as pasted "
                     "before the pass ever runs"
                     % (lum_plant, abs(lum_plant - lum_ref), ref_name,
                        lum_ref, tol))
    for f in fails:
        print("FAIL  %s" % f)
    if not fails:
        print("all checks pass (C1 containment, C2 mask ceiling, C3 whole "
              "plant in frame, C4 not a mirrored pair, C5 luma agreement)")

    if a.dry_run:
        print("\n-- dry run, nothing written. geometry:")
        print(json.dumps(geom, indent=1))
        return 1 if fails else 0
    if fails:
        print("\n!! refusing to write with %d failed check(s)." % len(fails))
        return 1

    if a.overlay_out:
        ov = Image.fromarray(arr.copy())
        od = ImageDraw.Draw(ov)
        edge = dilate(drawn, 2) & ~drawn
        oa = np.asarray(ov).copy()
        oa[edge] = (255, 40, 200)
        Image.fromarray(oa).save(a.overlay_out)
        print("overlay written: %s" % a.overlay_out)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
        Image.fromarray(comp).save(a.out)
        print("init written:  %s  sha256 %s" % (a.out, sha256_of(a.out)))
    if a.mask_out:
        os.makedirs(os.path.dirname(os.path.abspath(a.mask_out)) or ".",
                    exist_ok=True)
        Image.fromarray(mask).save(a.mask_out)
        print("mask written:  %s  sha256 %s" % (a.mask_out, sha256_of(a.mask_out)))
    if a.out:
        side = a.out + ".geometry.json"
        with open(side, "w", encoding="utf-8") as fh:
            json.dump(geom, fh, indent=1, sort_keys=True)
        print("geometry:      %s" % side)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
