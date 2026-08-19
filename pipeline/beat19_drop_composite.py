#!/usr/bin/env python3
"""beat19_drop_composite.py -- give beat 19's plate its PLANT by construction.

WHY THIS EXISTS, AND WHY IT IS NOT A WORDING
--------------------------------------------
`pipeline/work-ladder-0819.md` closed beat 19's wording ladder at three rungs on
2026-08-19: three wordings, three bead-strung vines, fruit count 4 -> ~8 -> 3,
never 1. The repo's own rule ("three rungs on one axis closes the wording
ladder") says the next instrument is COMPOSITIONAL, and the house pattern for
that is `pipeline/composite-init-pattern.md`: draw the structure with plain image
processing, then inpaint at LOW strength (0.30) so the sampler finishes it
instead of inventing it.

WHAT THE PLATE ACTUALLY SHOWS, MEASURED BEFORE ANY CODE WAS WRITTEN
-------------------------------------------------------------------
The parent is `farm-out/ep2-b19-mac-plate-0819/19-the-drop-mac-plate-r3s1.png`
(832x1216, animagine-xl-3.1, seed 20260819, sha256 de7a256c...). Opened at 2x on
both plant regions, this is what is in it:

  * FIVE of the seven plate terms pass and they are all OUTSIDE the plant:
    P2 whole figure in frame, P3 both hands folded on his knees and empty,
    P4 face visible, P5 the fruit reads purple, P7 one adult figure.
  * P1 fails: FOUR fruits, not one.
  * P6 fails, and it fails HARDER than the ladder's "bead-vine" shorthand
    suggests. Each plant is a BARE ARCING TWIG carrying a leaf sprig, with a
    THREAD hanging off it, and on the thread a VIOLET FACETED CRYSTAL -- a
    diamond-cut gem with hard specular facets, not a fruit. Neither plant has a
    visible root, a trunk, or a pair of cotyledon leaves.

THAT MEASUREMENT IS WHY THIS TOOL DRAWS RATHER THAN SUBTRACTS. The ladder's rung
was written as "composite beat 18's fig in at scale", and both halves of that
turned out to be wrong once the pixels were opened -- which is the whole reason
the pattern says to reject composites by eye before a GPU runs:

  1. SUBTRACTION CANNOT REACH EITHER AXIS HERE. composite-init-pattern.md 8,
     finding 2, already recorded this from the other side: "Removing one of three
     passes the COUNT axis and leaves two wrong-shaped leaves. Count and shape
     are one job." Delete three of the four crystals and the survivor is still a
     crystal on a thread on a bare twig. `pipeline/leaf_count_composite.py` is
     the right tool when a plate has the right SHAPE and too many of it; that is
     not this plate, and this file does not duplicate it -- it is beat-specific,
     like `beat14_field_composite.py` and `beat08_gesture_composite.py`.
  2. BEAT 18'S PIXELS ARE AT THE WRONG SCALE BY A FACTOR OF ~18. Its passing
     plate (`ep2-b18-canon-0817`, r2-w015-s2) is an EXTREME CLOSE-UP MACRO: the
     fig spans ~430px. Beat 19's fruit must span ~30px in the same 832-wide
     frame. Downsampling 430px of glossy macro shading to 30px does not import a
     fig, it imports a violet smudge -- and the pattern's decal tell 5 is
     "detail at the wrong scale read against an in-frame ruler". Beat 18's plate
     is therefore used here as the SHAPE AND COLOUR AUTHORITY (its verdict
     measured 305 deg, violet/magenta family, on 12 of 16 frames) and not as
     pixels. Its own verdict's `honest_caveat` -- "toward magenta rather than
     deep violet" and "heavily GLOSSY with a hard specular highlight" -- is the
     second reason not to paste it: this plate's own crystals measure 266-274
     deg, deeper violet, and the fig canon wants MATTE. The drawn fig takes the
     plate's own 272 deg and is given no specular.

SO THE ONE VARIABLE IS: THE PLANT IS DRAWN, NOT ASKED FOR.

WHAT IT DRAWS, AND WHERE EVERY NUMBER CAME FROM
-----------------------------------------------
The canon sapling: one rooted stem, EXACTLY TWO wide oval cotyledon leaves with
soft round tips, ONE thin side-branch, and hanging from that branch ONE matte
violet fig clear of the ground.

  * Colours are the PLATE'S OWN, measured on the plate's own pixels, so the
    drawing is in the plate's dialect rather than in mine:
      leaf   (105,139,85)  -- mean of the plate's own leaf sprigs
      stem   (113,100,71)  -- mean of the plate's own twig
      fig    (115, 58,169) -- mean of the plate's own crystals, hue 272 deg
  * Light direction is MEASURED, not assumed: the low-pass (sigma 40) luminance
    gradient of the whole plate is dx +0.029 dy -1.000, i.e. lit from straight
    above. Every drawn element is shaded on that axis, and the plate's own
    low-frequency luminance field is re-applied multiplicatively afterwards, so
    the drawing sits in the plate's light rather than its own.
  * Every drawn element gets a dark cel rim, because composite-init-pattern.md 3
    says the new content must keep a DRAWN edge in the plate's dialect instead of
    a texture running off a cliff.
  * The leaf midrib is a LUMINANCE RIDGE, not a drawn line, and the cel shadow
    on each leaf is capped below the outline's own contrast. 5's sampler-side
    rule: "never composite an internal line stronger than the object's own
    outline" -- at 0.45 beat 10 read its deepest composited fissure as an object
    boundary and split the object in two.

THE VACANCY LAW (6) IS THE REASON THE REMOVAL CLONE-FILLS
-----------------------------------------------------------
"An emptied region is a hole the model fills with the largest available noun, and
the negative does not reach it." Nothing here is erased to flat colour. Every
removed pixel is replaced by the nearest CLEAN pixel in its own row, at least
`--fill-min-dist` px away -- and this plate is the ideal case for that, because
its field is a smooth set of HORIZONTAL bands, so a horizontal clone preserves
the band structure exactly instead of importing a repeat.

Two places cannot be filled across the row and are declared as their own regions
with `axis=y`: where the left twig crosses his HOOD, and the lower-left crystal
that sits against his cloak edge. Both take their source down the column, from
the flat cloak, because a row source there would drag field pixels across him.

HOW THE PLANT IS SEGMENTED, AND THE v1 REJECTION THAT PRODUCED THIS VERSION
---------------------------------------------------------------------------
House style: the superseded attempt stays written down beside its correction.

**v1 (rejected by eye, 4.5 s, no GPU).** The object test was a departure from a
PER-ROW MEDIAN of the field, taken from clean columns. It failed, and the failure
is worth keeping because it is a general one: THE FIELD HAS FAINT HORIZONTAL
BANDS, so a row median is not a good model of its own row. The bands fired the
object test as thin horizontal ribbons running the full width of the frame, the
ribbons connected the figure's silhouette to everything else, and the dilated
"figure" swallowed all four crystals -- 93% to 100% of every crystal box landed
inside the protect mask, so the removal touched none of them. The composite came
back with all four crystals still hanging in it.

**v2, the fix, and it is two separate detectors because they are two questions.**

  1. THE PLANT: a HORIZONTAL HIGH-PASS. Each pixel is compared with a 61px
     running mean of its own row. A twig, a thread, a leaf sprig and a crystal
     are all narrow, so they survive the comparison; the field's horizontal bands
     are constant along the row, so they cancel exactly. Measured on the boxes:
     crystals 93-96%, leaf sprigs 56-78%, against 0% of protect. This is the
     right instrument for thin structures over a banded background.
  2. THE FIGURE: a COLOUR test, then the connected component containing a seed
     in his chest, holes filled, dilated 6. His green skin, purple cloak, navy
     tunic and brown boots are all far from the field in colour.

     PLUS ONE EXPLICIT BOX, and it is not a fudge, it is a measurement: HIS BALD
     CROWN IS ALMOST EXACTLY THE COLOUR OF THE FIELD. Measured at nine points,
     the crown is (216,227,62) at luminance 205 and the field beside it is
     (210,215,89) at luminance 200 -- a luminance difference of 5 and a hue
     difference of 6 degrees. No threshold separates them, so no colour rule can
     protect his head, and the left plant box overlaps it. The head is therefore
     protected by a box read off the plate, and the fact is logged rather than
     hidden.

$0: no model, no network, no GPU. Deterministic: same arguments, same bytes.
`--dry-run` prints the plan and the arithmetic and writes nothing.
"""

import argparse
import hashlib
import math
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ---------------------------------------------------------------------------
# Measured constants. Every one was read off the parent plate before a line of
# drawing code existed; see the module docstring for how.
# ---------------------------------------------------------------------------
LEAF_RGB = (105.0, 139.0, 85.0)
STEM_RGB = (113.0, 100.0, 71.0)
FIG_RGB = (115.0, 58.0, 169.0)
RIM_RGB = (38.0, 46.0, 34.0)
LIGHT_DX, LIGHT_DY = 0.029, -1.000  # low-pass luminance gradient of the plate

# The two twig-plants, as bounding boxes read off the plate at 2x.
PLANT_BOXES = [
    ("left_twig", (128, 250, 378, 792)),
    ("right_twig", (498, 236, 664, 792)),
]
# Regions the figure's own silhouette covers but that MUST still be cleared.
# Both take their fill source down the COLUMN, off the flat cloak.
#
# EACH CARRIES ITS OWN COLOUR RULE, and that is the correction of one more
# rejected round: INSIDE the figure the thin-structure test is not a plant
# detector. His cloak's stitching, its folds and its patch seams are all narrow
# too, so `thin & box` selected the cloak's own line art and the column-clone
# smeared a 30x240px vertical streak down him -- damage to a term that PASSES.
# The rule is therefore what distinguishes the twig from what it lies on: the
# twig is WARM brown on a purple hood, the crystal is VIOLET on a grey-purple
# cloak edge. composite-init-pattern.md 5 already recorded that the colour rule
# "transferred ZERO times across four boards" -- it is re-derived per region here
# for the same reason.
FORCE_BOXES = [
    ("hood_crossing", (280, 480, 348, 542), "warm_twig"),
    ("crystal_at_cloak_edge", (258, 648, 302, 726), "violet_crystal"),
]
# His bald crown is the field's own colour to within 5 luminance and 6 degrees of
# hue; no colour rule can find it, so it is protected by measurement.
HEAD_BOX = (334, 264, 488, 454)
FIGURE_SEED = (415, 620)  # inside his chest, in (x, y)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def luminance(arr):
    return 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]


def row_running_mean(arr, k):
    """The k-wide running mean of every row, computed exactly (no FFT, no blur
    library), so the result is bit-reproducible on any machine."""
    H = arr.shape[0]
    pad = np.pad(arr, ((0, 0), (k // 2, k // 2), (0, 0)), mode="edge")
    cs = np.concatenate([np.zeros((H, 1, arr.shape[2])), np.cumsum(pad, axis=1)], axis=1)
    return (cs[:, k:, :] - cs[:, :-k, :]) / float(k)


def thin_structure(arr, k, tol):
    """True where a pixel departs from the running mean of its own row.

    Narrow structures survive; a background constant along the row cancels.
    """
    return np.abs(arr - row_running_mean(arr, k)).max(axis=2) > tol


def binary_erode(mask, r):
    if r <= 0:
        return mask
    img = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(2 * r + 1))
    return np.asarray(img) > 127


def binary_dilate(mask, r):
    if r <= 0:
        return mask
    img = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1))
    return np.asarray(img) > 127


def fill_holes(mask):
    """Close every hole that does not touch the frame border."""
    H, W = mask.shape
    inv = ~mask
    seen = np.zeros_like(mask)
    q = deque()
    for x in range(W):
        for y in (0, H - 1):
            if inv[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    for y in range(H):
        for x in (0, W - 1):
            if inv[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and inv[yy, xx] and not seen[yy, xx]:
                seen[yy, xx] = True
                q.append((yy, xx))
    return mask | (inv & ~seen)


def component_containing(mask, seed_xy):
    H, W = mask.shape
    sx, sy = seed_xy
    if not mask[sy, sx]:
        found = None
        for r in range(1, 90):
            for dy in range(-r, r + 1):
                for dx in (-r, r):
                    y, x = sy + dy, sx + dx
                    if 0 <= y < H and 0 <= x < W and mask[y, x]:
                        found = (x, y)
                        break
                if found:
                    break
            if found:
                break
        if not found:
            raise SystemExit("!! figure seed %s is not on any object pixel" % (seed_xy,))
        sx, sy = found
    out = np.zeros_like(mask)
    q = deque([(sy, sx)])
    out[sy, sx] = True
    while q:
        y, x = q.popleft()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not out[yy, xx]:
                    out[yy, xx] = True
                    q.append((yy, xx))
    return out


def figure_protect(arr, grow):
    """His silhouette: colour, component, holes filled, dilated, plus the crown."""
    R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    lum = luminance(arr)
    cand = (lum < 150) | ((G - R) > 25) | ((B - R) > 8) | ((R - G) > 18)
    body = fill_holes(component_containing(binary_erode(cand, 3), FIGURE_SEED))
    protect = binary_dilate(body, grow)
    x0, y0, x1, y1 = HEAD_BOX
    protect[y0:y1, x0:x1] = True
    return protect, int(body.sum())


def clone_fill(arr, fill_mask, source_ok, axis, min_dist):
    """Replace every masked pixel with the nearest acceptable pixel along `axis`."""
    H, W, _ = arr.shape
    out = arr.copy()
    ys, xs = np.nonzero(fill_mask)
    misses = 0
    for y, x in zip(ys, xs):
        src = None
        if axis == "x":
            for d in range(min_dist, W):
                for xx in (x - d, x + d):
                    if 0 <= xx < W and source_ok[y, xx]:
                        src = (y, xx)
                        break
                if src:
                    break
        else:
            for d in range(min_dist, H):
                for yy in (y - d, y + d):
                    if 0 <= yy < H and source_ok[yy, x]:
                        src = (yy, x)
                        break
                if src:
                    break
        if src is None:
            misses += 1
            continue
        out[y, x] = arr[src[0], src[1]]
    return out, misses


# ---------------------------------------------------------------------------
# The drawing. Everything is drawn at SS x supersample and downsampled, so the
# edges are anti-aliased in the plate's own soft-cel manner rather than jagged.
# ---------------------------------------------------------------------------
def leaf_outline(cx, cy, rx, ry, ang, n=112):
    """A wide oval with softly ROUNDED tips. |cos|^0.82 keeps the ends blunt
    instead of lance-shaped; canon 2.2 rules lance shapes out (the founder's
    own 2026-08-17 ruling is 'average leaves')."""
    pts = []
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    for i in range(n):
        t = 2.0 * math.pi * i / n
        u = math.copysign(abs(math.cos(t)) ** 0.82, math.cos(t)) * rx
        v = math.sin(t) * ry
        pts.append((cx + u * ca - v * sa, cy + u * sa + v * ca))
    return pts


def fig_outline(fx, fy, frx, fry, n=144):
    """A fig: round body, narrow neck at the top where the stalk enters."""
    pts = []
    for i in range(n):
        t = 2.0 * math.pi * i / n
        # the neck belongs at the TOP, where the stalk enters. `sin(t) == -1` is
        # the top of the outline; the first draft tapered at sin(t+pi/2), i.e. the
        # RIGHT side, and the fig came back as a vertical capsule with no neck.
        taper = 1.0 - 0.40 * max(0.0, -math.sin(t)) ** 2.2
        pts.append((fx + math.cos(t) * frx * taper, fy + math.sin(t) * fry))
    return pts


def draw_sapling(geom, W, H, ss=3):
    """Return (rgb, alpha, rim, shadow, ridge) at plate resolution."""
    L = Image.new("RGB", (W * ss, H * ss), (0, 0, 0))
    A = Image.new("L", (W * ss, H * ss), 0)
    Rm = Image.new("L", (W * ss, H * ss), 0)
    Sh = Image.new("L", (W * ss, H * ss), 0)
    Rg = Image.new("L", (W * ss, H * ss), 0)
    dl, da, dr, ds, dg = (ImageDraw.Draw(x) for x in (L, A, Rm, Sh, Rg))
    stem_c = tuple(int(v) for v in STEM_RGB)
    leaf_c = tuple(int(v) for v in LEAF_RGB)
    fig_c = tuple(int(v) for v in FIG_RGB)

    def S(p):
        return (p[0] * ss, p[1] * ss)

    bx, by = geom["base"]
    ax, ay = geom["apex"]
    sw = geom["stem_w"]

    # --- a few grass blades at the root, so it reads ROOTED not stuck in ------
    for (dx, dy, w) in geom["root_blades"]:
        dl.line([S((bx, by)), S((bx + dx, by + dy))], fill=leaf_c, width=int(w * ss))
        da.line([S((bx, by)), S((bx + dx, by + dy))], fill=255, width=int(w * ss))

    # --- stem: a tapered quad, wider at the root, ending AT the leaf joint ----
    stem = [(bx - sw / 2.0, by), (bx + sw / 2.0, by),
            (ax + sw * 0.30, ay), (ax - sw * 0.30, ay)]
    dl.polygon([S(p) for p in stem], fill=stem_c)
    da.polygon([S(p) for p in stem], fill=255)
    dr.line([S(p) for p in stem] + [S(stem[0])], fill=255, width=int(2.4 * ss))

    # --- one thin side-branch ------------------------------------------------
    b0, b1 = geom["branch"]
    bw = geom["branch_w"]
    dl.line([S(b0), S(b1)], fill=stem_c, width=int(bw * ss))
    da.line([S(b0), S(b1)], fill=255, width=int(bw * ss))
    dr.line([S(b0), S(b1)], fill=255, width=int((bw + 1.0) * ss))

    # --- exactly two wide oval cotyledon leaves ------------------------------
    for (cx, cy, rx, ry, ang) in geom["leaves"]:
        pts = leaf_outline(cx, cy, rx, ry, ang)
        dl.polygon([S(p) for p in pts], fill=leaf_c)
        da.polygon([S(p) for p in pts], fill=255)
        dr.line([S(p) for p in pts] + [S(pts[0])], fill=255, width=int(2.4 * ss))
        # a cel shadow on the lower half of the blade: a flat plate, not a ramp
        low = [p for p in pts if p[1] >= cy + ry * 0.18]
        if len(low) > 3:
            ds.polygon([S(p) for p in low], fill=255)
        # midrib as a LUMINANCE RIDGE, from the petiole end to the far tip
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        p0 = (cx - rx * 0.92 * ca, cy - rx * 0.92 * sa)
        p1 = (cx + rx * 0.92 * ca, cy + rx * 0.92 * sa)
        dg.line([S(p0), S(p1)], fill=255, width=int(2.0 * ss))
        # NO PETIOLE LINE. The first draft drew one from the leaf's CENTRE to the
        # joint, which put a stem-coloured bar straight across half the blade --
        # exactly the internal line composite-init-pattern.md 5 forbids ("never
        # composite an internal line stronger than the object's own outline";
        # beat 10 read its own deepest line as an object boundary and split the
        # slab in two). Each blade's inner end already lands ON the joint by
        # construction, so the join needs no line at all.

    # --- exactly one fig, hanging from the branch tip ------------------------
    fx, fy, frx, fry = geom["fig"]
    pts = fig_outline(fx, fy, frx, fry)
    dl.polygon([S(p) for p in pts], fill=fig_c)
    da.polygon([S(p) for p in pts], fill=255)
    dr.line([S(p) for p in pts] + [S(pts[0])], fill=255, width=int(2.4 * ss))
    low = [p for p in pts if p[1] >= fy + fry * 0.10]
    if len(low) > 3:
        ds.polygon([S(p) for p in low], fill=255)
    dl.line([S((fx, fy - fry * 0.92)), S(b1)], fill=stem_c, width=int(1.9 * ss))
    da.line([S((fx, fy - fry * 0.92)), S(b1)], fill=255, width=int(1.9 * ss))

    def down(img, mode="L"):
        a = np.asarray(img.resize((W, H), Image.LANCZOS)).astype(np.float64)
        return a if mode == "RGB" else a / 255.0

    return (down(L, "RGB"), down(A), down(Rm), down(Sh), down(Rg))


def shade(rgb, al, shadow, ridge, base):
    """Shade on the plate's MEASURED light axis, add the cel shadow and the
    midrib ridge, then re-apply the plate's own low-frequency luminance field."""
    H, W, _ = base.shape
    ys, xs = np.nonzero(al > 0.05)
    if len(ys) == 0:
        return rgb
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    proj = xx * LIGHT_DX + yy * LIGHT_DY
    p = proj[ys, xs]
    t = np.clip((proj - p.min()) / max(1e-6, (p.max() - p.min())), 0.0, 1.0)
    out = rgb * (0.90 + 0.20 * t)[:, :, None]
    # cel shadow: a flat 12% plate. The object's own outline is a ~65% step, so
    # this stays well under it -- pattern 5, "never composite an internal line
    # stronger than the object's own outline".
    out = out * (1.0 - 0.12 * shadow)[:, :, None]
    # midrib: a luminance ridge, +9%, never a drawn line
    out = out * (1.0 + 0.09 * ridge)[:, :, None]
    lp = np.asarray(
        Image.fromarray(luminance(base).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))
    ).astype(np.float64)
    local = lp[ys, xs].mean()
    out = out * np.clip(lp / max(1e-6, local), 0.86, 1.16)[:, :, None]
    return np.clip(out, 0, 255)


def geometry():
    """Where the sapling goes. Placed in MEASURED clean field: the column
    x 690-800, y 700-940 has luminance mean 197.8 std 15.5 with 0.7% of pixels
    below 120, i.e. open grass with no cloak, no boot and no shadow in it."""
    # The two cotyledons are angled UP AND OUT in a V from the stem's apex, each
    # one's INNER end landing exactly on the joint. The previous round drew them
    # as two horizontal ovals on top of a bare stick and it read as a television
    # aerial, not a sprout -- rejected by eye, no GPU, which is the point of
    # doing the structure with image processing.
    return {
        "base": (706.0, 932.0),
        "apex": (700.0, 800.0),
        "stem_w": 7.6,
        "leaf_joint": (700.0, 800.0),
        "leaves": [
            (662.0, 782.0, 42.0, 23.0, 25.0),
            (738.0, 782.0, 42.0, 23.0, -25.0),
        ],
        "branch": ((702.0, 822.0), (754.0, 850.0)),
        "branch_w": 3.3,
        "fig": (758.0, 876.0, 17.0, 23.0),
        "root_blades": [(-19.0, -9.0, 2.2), (17.0, -8.0, 2.2),
                        (-8.0, -15.0, 1.9), (11.0, -16.0, 1.9)],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", required=True, help="the beat-19 plate to correct")
    ap.add_argument("--init-sha256", required=True,
                    help="asserted BEFORE anything is read or written")
    ap.add_argument("--out", required=True, help="composited init")
    ap.add_argument("--mask-out", required=True,
                    help="union mask for the inpaint pass (white = repaint)")
    ap.add_argument("--thin-k", type=int, default=61,
                    help="row running-mean width for the thin-structure test")
    ap.add_argument("--thin-tol", type=float, default=16.0)
    ap.add_argument("--protect-grow", type=int, default=6)
    ap.add_argument("--remove-grow", type=int, default=3)
    ap.add_argument("--fill-min-dist", type=int, default=26)
    ap.add_argument("--mask-grow", type=int, default=12)
    ap.add_argument("--feather", type=int, default=3)
    ap.add_argument("--assert-clear", action="store_true",
                    help="exit nonzero if removed structure survives")
    ap.add_argument("--residual-max", type=int, default=900)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not os.path.isfile(a.init):
        sys.exit("!! init not found: %s" % a.init)
    have = sha256_of(a.init)
    if have != a.init_sha256:
        sys.exit("!! INIT SHA MISMATCH -- refusing.\n   want %s\n   have %s"
                 % (a.init_sha256, have))
    print("init %s sha %s OK" % (a.init, have), flush=True)

    arr = np.asarray(Image.open(a.init).convert("RGB")).astype(np.float64)
    H, W, _ = arr.shape
    print("plate %dx%d" % (W, H), flush=True)

    thin = thin_structure(arr, a.thin_k, a.thin_tol)
    protect, body_px = figure_protect(arr, a.protect_grow)
    print("thin structure %.2f%% of frame; figure silhouette %d px, protected "
          "%.2f%% (crown box %s added by measurement)"
          % (100.0 * thin.mean(), body_px, 100.0 * protect.mean(), HEAD_BOX), flush=True)

    regions = []
    for name, (x0, y0, x1, y1) in PLANT_BOXES:
        box = np.zeros((H, W), bool)
        box[y0:y1, x0:x1] = True
        regions.append([name, thin & box & ~protect, "x", (x0, y0, x1, y1)])
    R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    lum = luminance(arr)
    rules = {
        "warm_twig": ((R - B) > 14) & (lum < 160),
        # measured on the box itself: the crystal is 235 px under this rule and
        # the grey-purple cloak around it is not. The first draft used
        # (B-R)>25 & (B-G)>25 and selected ZERO -- the crystal at the cloak edge
        # is in shadow and duller than the two out in the field.
        "violet_crystal": ((B - R) > 18) & ((B - G) > 10) & (lum < 170),
    }
    for name, (x0, y0, x1, y1), rule in FORCE_BOXES:
        box = np.zeros((H, W), bool)
        box[y0:y1, x0:x1] = True
        regions.append([name, thin & box & rules[rule], "y", (x0, y0, x1, y1)])

    total = np.zeros((H, W), bool)
    for r in regions:
        r[1] = binary_dilate(r[1], a.remove_grow)
        print("  region %-22s box %s  %6d px  fill-axis %s"
              % (r[0], r[3], int(r[1].sum()), r[2]), flush=True)
        total |= r[1]

    geom = geometry()
    print("drawing: stem (%.0f,%.0f)->(%.0f,%.0f)  2 leaves  1 branch  1 fig at "
          "(%.0f,%.0f) r %.0fx%.0f"
          % (geom["base"][0], geom["base"][1], geom["apex"][0], geom["apex"][1],
             geom["fig"][0], geom["fig"][1], geom["fig"][2], geom["fig"][3]), flush=True)
    print("fig bottom sits %.0f px ABOVE the stem's root -- clear of the ground"
          % (geom["base"][1] - (geom["fig"][1] + geom["fig"][3])), flush=True)

    if a.dry_run:
        print("DRY RUN -- nothing written.", flush=True)
        return 0

    work = arr.copy()
    for name, m, axis, box in regions:
        if axis == "x":
            src_ok = (~total) & (~thin) & (~protect)
        else:
            src_ok = (~total) & protect & (~thin)
        work, misses = clone_fill(work, m, src_ok, axis, a.fill_min_dist)
        print("  filled %-22s %6d px, %d without a source" % (name, int(m.sum()), misses),
              flush=True)
        if misses:
            print("  !! %d pixels had no clean source -- the vacancy law calls that a "
                  "hole. Widen the region or its source range." % misses, flush=True)

    if a.feather > 0:
        soft = np.asarray(
            Image.fromarray((total * 255).astype(np.uint8))
            .filter(ImageFilter.GaussianBlur(a.feather))
        ).astype(np.float64)[:, :, None] / 255.0
        blur = np.asarray(
            Image.fromarray(work.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
        ).astype(np.float64)
        work = work * (1.0 - soft * 0.55) + blur * (soft * 0.55)

    resid = thin_structure(work, a.thin_k, a.thin_tol) & total & ~protect
    resid_px = int(resid.sum())
    print("residual thin structure inside the removal footprint: %d px" % resid_px,
          flush=True)
    if a.assert_clear and resid_px > a.residual_max:
        sys.exit("!! %d residual px survive the removal (limit %d) -- refusing to write "
                 "a composite with a half-erased twig in it." % (resid_px, a.residual_max))

    rgb, al, rim, shadow, ridge = draw_sapling(geom, W, H)
    rgb = shade(rgb, al, shadow, ridge, arr)
    a3 = al[:, :, None]
    out = work * (1.0 - a3) + rgb * a3
    r3 = (rim * (al > 0.02))[:, :, None]
    out = np.clip(out * (1.0 - r3 * 0.90) + np.array(RIM_RGB)[None, None, :] * (r3 * 0.90),
                  0, 255)

    drawn = al > 0.02
    print("drawn footprint %d px" % int(drawn.sum()), flush=True)

    mask = binary_dilate(total | drawn, a.mask_grow)
    print("inpaint mask %d px (%.2f%% of frame)" % (int(mask.sum()), 100.0 * mask.mean()),
          flush=True)

    outside = ~binary_dilate(total | drawn, a.mask_grow + 2)
    maxdiff = float(np.abs(out - arr)[outside].max()) if outside.any() else 0.0
    print("max change OUTSIDE the mask: %.1f (0 means every pixel of the five passing "
          "terms is untouched)" % maxdiff, flush=True)

    # count checks: by construction, then verified on the pixels
    lum_o = luminance(out)
    viol = ((out[:, :, 2] - out[:, :, 1]) > 25) & (out[:, :, 2] > 95) & (lum_o < 200)
    zone = np.zeros((H, W), bool)
    zone[236:980, 100:832] = True
    blobs = []
    seen = viol & zone & ~protect
    work_m = seen.copy()
    ys, xs = np.nonzero(work_m)
    for y0, x0 in zip(ys, xs):
        if not work_m[y0, x0]:
            continue
        q = deque([(y0, x0)])
        work_m[y0, x0] = False
        n = 0
        while q:
            y, x = q.popleft()
            n += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and work_m[yy, xx]:
                        work_m[yy, xx] = False
                        q.append((yy, xx))
        if n >= 80:
            blobs.append(n)
    print("violet fruit blobs (>=80 px) in the plant zone: %d %s"
          % (len(blobs), sorted(blobs, reverse=True)), flush=True)
    print("leaves drawn: 2 (by construction); fruits drawn: 1 (by construction)",
          flush=True)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    Image.fromarray(out.astype(np.uint8)).save(a.out)
    Image.fromarray((mask * 255).astype(np.uint8)).save(a.mask_out)
    print("WROTE %s sha %s" % (a.out, sha256_of(a.out)), flush=True)
    print("WROTE %s sha %s" % (a.mask_out, sha256_of(a.mask_out)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
