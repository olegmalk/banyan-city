#!/usr/bin/env python3
"""beat15_listener_composite.py -- give beat 15's plate its SAPLING by construction.

WHY THIS EXISTS, AND WHY IT IS THE ROUTE THAT WAS ALREADY NAMED
--------------------------------------------------------------
`review/ep2-picks/b15-0819-verdict.yaml` judged beat 15 on TWENTY-FOUR artefacts
-- 12 wave stills, 6 mac plates, 6 LTX motion takes -- and not one of them fails
on the acting. Every single one fails because the thing sharing the frame with
him is not the sapling. It then drew two new plates the same night: r1 scored
6 OF 7 with all seven pre-registered fail modes silent, and the one term it
missed is `THE PLANT IS THE SAPLING` -- "leaves on two or three nodes, roughly
five of them, where the script says 'the two leaves'". r2 moved one wording and
the plant did not move at all, so that lane closed its wording ladder at two
rungs and named the next instrument:

    "A COMPOSITE INIT ... r1's frame with b12's leaves composited in on a thin
     stem at ~40 cm -- the pattern is pipeline/composite-init-pattern.md ...
     That is a build, not a rev."

This file is that build. The blocker it attacks is CARDINALITY, which
composite-init-pattern.md 1 calls CLASS A -- "the attribute is not a direction in
the conditioning space at all, so there is no knob to turn ... CLIP's numeral
embeddings are near-identical". Class A is the pattern's *strongest* case,
because a composited count is not a sample from anything.

THE NAMED ROUTE SAYS "b12'S LEAVES" AND THE PIXELS SAY NO. MEASURED FIRST.
--------------------------------------------------------------------------
Beat 12's pick is `ep2-b12-tightB` (704x1280, LTX, seed 20260813), and its
leaves were opened and measured before a line of drawing code existed. Two
numbers kill the paste, and both were taken with the same instrument on the same
frame (`f000`, green-segmented, per-component PCA at ~4 sigma):

  * SCALE. Its four blade-sized components have major axes of 619, 772, 607 and
    591 px. Beat 15's blade needs a major axis of about 80 px in an 832-wide
    frame. That is a 7.4x to 9.7x DOWNSAMPLE, and the pattern's decal tell 5 is
    "detail at the wrong scale read against an in-frame ruler". This is the same
    finding the beat-19 lane reached hours earlier from the other side, where
    the ladder's phrasing said "composite beat 18's fig in at scale" and beat
    18's fig turned out to span ~430px against beat 19's ~30px.
  * SHAPE. Those same components measure aspect 2.85, 3.38, 3.11 (and 5.97 on a
    blade the frame crops). composite-init-pattern.md 8 pre-registered the
    acceptable blade aspect as 1.6-2.6 BEFORE any of this, so beat 12's blades
    are LANCE-shaped by our own standing number -- and canon's own correction
    (THE-SAPLING.md, the founder's 2026-08-17 "average leaves") is the reason
    that band exists. Beat 12 is a macro of leaves seen nearly edge-on against a
    sunset; nothing is wrong with it as beat 12. It is wrong as a patch source.

  Its light is the third reason and it needs no PCA: beat 12 is BACKLIT at
  sunset, pink rim on the blade edges and near-black shadow sides. Beat 15's
  plate is a bright midday field lit from straight above (measured below,
  dx -0.072 dy -0.997). The pattern's decal tell 2 is "a pattern ignoring the
  frame's light".

SO BEAT 12 IS USED AS THE ARCHITECTURE AUTHORITY AND NOT AS PIXELS: it is what
this show's leaves are -- a smooth entire margin, no lobe and no serration, one
strong midrib per blade -- and it independently confirms the midrib-as-luminance
-ridge choice this file inherits. The blades are DRAWN, at this plate's scale,
in this plate's light, with this plate's own colours.

  THE ONE VARIABLE IS THEREFORE: THE PLANT IS DRAWN, NOT ASKED FOR.

WHAT WAS MEASURED OFF r1 BEFORE ANY DRAWING CODE EXISTED
--------------------------------------------------------
Parent: farm-out/ep2-b15-mac-plate-0819/15-good-listener-mac-plate-r1s1.png
(832x1216, animagine-xl-3.1, seed 20260819, sha256 8a9bd14b...).

  * THE PLANT IS ONE MULTI-NODE WEED, x 162-262, y 315-600: a top pair of
    pointed blades, a second pair one node down, a fifth small blade lower
    still, and a curl of stem below that. Five blades on three nodes.
  * Colours, all the PLATE'S OWN, so the drawing is in its dialect not mine:
      leaf (85.5, 111.8, 58.5)  hue  90 deg -- mean of its own top blades
      stem (76.0,  99.0, 68.0)  hue 103 deg -- mean of its own stem, upper+lower
      rim  (36.5,  50.4, 40.0)  lum  45.1  -- its own darkest 3% in the plant bbox
    The outline step is 213.9 -> 45.1 in luminance, which is what caps the cel
    shadow and the midrib ridge below (pattern 5: "never composite an internal
    line stronger than the object's own outline").
  * LIGHT dx -0.072 dy -0.997 from the low-pass (sigma 40) luminance gradient of
    the whole plate: lit from straight above.
  * THE CLONE SOURCE IS THE FIELD TO ITS LEFT, x 55-150 over y 300-560: mean
    luminance 212.1, std 4.7, and 0.02% of pixels below 150. Open grass, no
    cloak, no boot, no shadow. The field's structure is faint HORIZONTAL bands,
    which is the ideal case for a row-wise clone -- it preserves the band
    exactly instead of importing a repeat.
  * HIS SILHOUETTE'S LEFT EDGE, per row: x 325 at y 300-380, 346 at 380-420,
    370 at 420-460, then in to 291 at y 500-540 and 264 at y 540-620. The
    removal box stops at x 268 and y 565 for that reason, and the figure-protect
    component is belt and braces on top of it.

TWO THINGS THIS FILE DELIBERATELY DOES NOT DRAW, AND THE SECOND IS A FINDING
----------------------------------------------------------------------------
1. NO SIDE-BRANCH AND NO FIG. The bar this rung is scored against is beat 15's
   own, pre-registered in plate_scratch.py DRAFTS[15] before r1 existed, and its
   P3 reads "Exactly ONE plant, TWO leaves, ONE thin stem. Extra stalks, extra
   leaves, a bead-strung vine, a multi-node weed or a bud/ball at the tip all
   FAIL." A drawn side-branch is scoreable as an extra stalk and a drawn fig as
   a bud at the tip. One variable per rung: this rung is the LEAF COUNT.
2. AND THAT LEAVES A REAL GAP, FLAGGED RATHER THAN FIXED. THE-SAPLING.md's own
   growth ladder gives 002a/b/c "two leaves + one thin side-branch", and the fig
   does not leave the plant until beat 19 -- so at beat 15 the episode's own
   continuity puts a fig on this plant, and neither r1's prompt nor r2's ever
   asked for one. That is a SECOND variable and the fig is separately frozen
   canon belonging to the fig lane (THE-SAPLING.md 3.x, `ep2-fig-purple` in
   pipeline/canon.yaml). It is reported in this rung's verdict, not smuggled in.

THE ROOTING CUE IS KEPT ON PURPOSE, WHICH IS PATTERN 13 USED IN THE POSITIVE
----------------------------------------------------------------------------
composite-init-pattern.md 13: "a masked vacancy is filled with whatever the
surviving cue suggests ... an attachment point is a structural cue and it is as
strong as an outline." On beat 01 that law cost a rung, because the stem NODE
was left inside the mask and the sampler grew a blade back at it 4 of 4.

Here the surviving cue is the one I want completed: the removal stops at y 565,
ABOVE the plate's own grass tufts at y 563-607, so the tufts and the last 25px
of the original stem base survive untouched and the drawn stem is rooted INTO
them at (222, 592). The plate does the rooting; the sampler is asked to finish a
join that is already physically there. Said out loud because the same law
punished a lane two days ago for leaving a cue it did not want.

THE VACANCY LAW (pattern 6) IS WHY THE REMOVAL CLONE-FILLS
----------------------------------------------------------
"An emptied region is a hole the model fills with the largest available noun, and
the negative does not reach it." Nothing is erased to flat colour. Every removed
pixel takes the nearest clean pixel in its OWN ROW at least --fill-min-dist away.

WHY THIS IS A COPY OF beat19_drop_composite.py's PRIMITIVES AND NOT AN IMPORT
-----------------------------------------------------------------------------
`sha256_of`, `luminance`, `row_running_mean`, `thin_structure`, `binary_erode`,
`binary_dilate`, `fill_holes`, `component_containing`, `clone_fill`,
`leaf_outline` and `shade`'s structure are carried from
pipeline/beat19_drop_composite.py, which passed all eight clauses of its bar
today. They are COPIED rather than imported, and that is deliberate: the beat-19
composite lane is live in this same shift, and an init whose sha256 this repo
asserts in a job spec must not be able to change its bytes because a peer edited
a shared module. The house has three beat-specific compositors already
(beat14_field_composite.py, beat08_gesture_composite.py,
beat19_drop_composite.py) for the same reason. If these primitives are ever
promoted to a module, promote all four together and re-assert every init sha.

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
# Measured constants. Every one was read off r1 before a line of drawing code
# existed; see the module docstring for how and where.
# ---------------------------------------------------------------------------
LEAF_RGB = (85.5, 111.8, 58.5)
STEM_RGB = (76.0, 99.0, 68.0)
RIM_RGB = (36.5, 50.4, 40.0)
LIGHT_DX, LIGHT_DY = -0.072, -0.997  # low-pass luminance gradient of the plate

# The one weed-plant, as a bounding box read off the plate at 3x. It stops at
# x 268 (his cloak reaches x 264 at y 540+) and at y 565 (the plate's own grass
# tufts start at y 563 and are KEPT -- they are the rooting cue).
PLANT_BOXES = [
    ("weed_five_blades", (140, 300, 268, 568)),
]
# THE CLONE SOURCE IS A MEASURED WINDOW, NOT "WHATEVER IS NEAREST", and this is
# the correction of a rejected round. With the source left free, the nearest
# acceptable pixel for the rows at y 493-557 was found out past his cloak, and the
# composite came back with a row of grey dashes at x 233-257 and a vertical seam
# down the box's own right edge at x 262 -- both visible at 3x, both rejected by
# eye. composite-init-pattern.md 12's SOURCE LAW is the general form ("never patch
# with pixels that satisfy your own object rule"); the specific fix is that this
# plate HAS a measured clean field and the fill should be made to use it:
# x 55-150 over the whole region's row range is luminance 212.1, std 4.7, with
# 0.02% of pixels below 150. Restricting the source to it removed both artefacts.
SOURCE_COLUMNS = (55, 150)
FIGURE_SEED = (470, 560)  # inside his cloaked chest, in (x, y)
# His silhouette is found by colour + the component containing FIGURE_SEED, holes
# filled, dilated. Unlike beat 19's plate, his crown here is NOT the field's
# colour -- the bald scalp is a pale highlight at luminance ~245 against a field
# at ~212, and it is enclosed by his own dark outline, so `fill_holes` on the
# body component reaches it and no measured HEAD_BOX is needed. Checked: the
# protect mask's own extent is printed at run time so this claim is falsifiable.


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
    """His silhouette: colour, the component containing his chest, holes filled,
    dilated. His cloak is a dark plaid, his skin is green, his boots are dark --
    all far from a field at luminance 212."""
    R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    lum = luminance(arr)
    cand = (lum < 165) | ((G - R) > 25) | ((B - R) > 8)
    body = fill_holes(component_containing(binary_erode(cand, 3), FIGURE_SEED))
    protect = binary_dilate(body, grow)
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
    instead of lance-shaped -- the founder's own 2026-08-17 ruling is 'average
    leaves', and beat 12's own blades measure aspect 2.85-3.38, i.e. outside the
    1.6-2.6 band composite-init-pattern.md 8 pre-registered."""
    pts = []
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    for i in range(n):
        t = 2.0 * math.pi * i / n
        u = math.copysign(abs(math.cos(t)) ** 0.82, math.cos(t)) * rx
        v = math.sin(t) * ry
        pts.append((cx + u * ca - v * sa, cy + u * sa + v * ca))
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

    def S(p):
        return (p[0] * ss, p[1] * ss)

    bx, by = geom["base"]
    ax, ay = geom["apex"]
    sw = geom["stem_w"]

    # --- stem: a CURVED tapered ribbon, wider at the root, ending AT the joint --
    # THE STRAIGHT VERSION WAS REJECTED BY EYE, and it is worth writing down why,
    # because beat 19's plate did not have this problem. A dead-straight 256px
    # stem with a two-blade crown on top read as a television aerial or a
    # lollipop, not a seedling -- the same class of rejection beat19's own
    # geometry() records ("two horizontal ovals on top of a bare stick ... read as
    # a television aerial"), arriving here through a different door. r1's own weed
    # bows gently to the right through its middle, so the drawn stem is sampled
    # along a quadratic Bezier with the plate's own bow rather than a line.
    #
    # NO root blades are drawn. Beat 19's plate needed them because its stem sat
    # in open field; here the plate's OWN grass tufts at y 563-607 survive the
    # removal and the stem is rooted into them, which is a real cue rather than a
    # drawn one (see the docstring, pattern 13 in the positive).
    cxp, cyp = geom["stem_ctrl"]
    n = 48
    left, right = [], []
    for i in range(n + 1):
        t = i / float(n)
        # quadratic Bezier base -> ctrl -> apex
        px = (1 - t) ** 2 * bx + 2 * (1 - t) * t * cxp + t ** 2 * ax
        py = (1 - t) ** 2 * by + 2 * (1 - t) * t * cyp + t ** 2 * ay
        dx = 2 * (1 - t) * (cxp - bx) + 2 * t * (ax - cxp)
        dy = 2 * (1 - t) * (cyp - by) + 2 * t * (ay - cyp)
        nl = math.hypot(dx, dy) or 1.0
        # normal to the centreline, so the taper is measured across the stem
        nx, ny = -dy / nl, dx / nl
        w = sw * (1.0 - 0.70 * t) / 2.0   # 7.0px at the root -> 2.1px at the joint
        left.append((px + nx * w, py + ny * w))
        right.append((px - nx * w, py - ny * w))
    stem = left + right[::-1]
    dl.polygon([S(p) for p in stem], fill=stem_c)
    da.polygon([S(p) for p in stem], fill=255)
    dr.line([S(p) for p in stem] + [S(stem[0])], fill=255, width=int(2.4 * ss))

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
        # midrib as a LUMINANCE RIDGE, from the petiole end to the far tip. Beat
        # 12's blades each carry exactly one strong midrib and no secondary
        # veining, which is the architecture half of what that pick authorises.
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        p0 = (cx - rx * 0.92 * ca, cy - rx * 0.92 * sa)
        p1 = (cx + rx * 0.92 * ca, cy + rx * 0.92 * sa)
        dg.line([S(p0), S(p1)], fill=255, width=int(2.0 * ss))
        # NO PETIOLE LINE: each blade's inner end already lands ON the joint by
        # construction. beat19_drop_composite.py records what a drawn petiole
        # cost -- a stem-coloured bar across half the blade, which is exactly the
        # internal line pattern 5 forbids.

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
    # cel shadow: a flat 12% plate. This plate's own outline step is 213.9 -> 45.1
    # in luminance, i.e. ~79%, so 12% stays well under it -- pattern 5, "never
    # composite an internal line stronger than the object's own outline".
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
    """Where the sapling goes, and every number is either r1's own or the
    APPROVED LINE'S.

    THE ROOT DOES NOT MOVE: (222, 592) is where r1's own weed meets its own grass
    tufts, and keeping it is what makes the rooting a real cue rather than a drawn
    one.

    THE BLADE HEIGHT IS SET BY THE APPROVED SCRIPT LINE, NOT BY TASTE. His
    2026-08-19 approval covers node.md:98 as rewritten -- "He tips his head down
    and sideways until his EYES ARE LEVEL WITH THE TWO LEAVES, and talks to them
    from a hand's width away; both of them share the frame." HIS EYE LEVEL IN THIS
    PLATE IS y 370, measured at 4x on the pupils behind his spectacles. So the two
    blades are centred at y 374 and span y ~348-400: his eye line falls inside the
    blades, which is the staging the line describes and which no beat-15 artefact
    has ever depicted.

    That is also why the apex moved DOWN from the weed's y 336 to y 392. It is not
    a scale change dressed up: the plant is 200px tall against the weed's 256px,
    which keeps every clause r1 already passes (apex 135px BELOW his head top at
    y 257, both wholly in frame, not a close-up, plant shorter than he is) while
    putting the leaves where the sentence puts them. THE-SAPLING.md 3.2 states the
    height as a RELATION and records that he "asked us not to go crazy on it";
    P4's pre-registered form is "SHORTER than the seated goblin's head", which
    200px passes with 135px to spare.
    """
    return {
        "base": (222.0, 592.0),
        "apex": (216.0, 392.0),
        # r1's own weed bows gently right through its middle; the control point is
        # +12px of lateral bow, which is that bow and not a stylisation.
        "stem_ctrl": (232.0, 496.0),
        "stem_w": 7.0,       # r1's own stem is ~7px at the root, ~5px at the top
        "leaf_joint": (216.0, 392.0),
        # aspect 43/25 = 1.72, inside composite-init-pattern.md 8's pre-registered
        # 1.6-2.6 band and within rounding of beat 19's passing 42/23 = 1.83.
        # Beat 12's own blades measure 2.85-3.38 and are NOT copied -- see the
        # module docstring.
        "leaves": [
            (175.0, 374.0, 43.0, 25.0, 24.0),
            (257.0, 374.0, 43.0, 25.0, -24.0),
        ],
        # measured on the plate at 4x, and the reason the blades sit where they do
        "his_eye_level_y": 370.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", required=True, help="the beat-15 r1 plate to correct")
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
    # THE GUARD IS CALIBRATED, NOT ABSOLUTE, and that is a fix to the one it was
    # copied from. beat19_drop_composite.py refuses above an absolute 900 residual
    # px. On THIS plate that fired at 1488 px and the removal was in fact clean by
    # eye -- checked by rendering the cleaned plate on its own at 3x before any
    # drawing was composited over it. The reason is that the test's own FLOOR is
    # set by the plate's field: this field carries faint horizontal bands, and an
    # UNTOUCHED window of it (x 55-150, y 300-560) trips the same thin-structure
    # test on 4.12 per cent of its own pixels. Widening the removal does not close
    # the gap either -- a six-point sweep of (tol, grow) moved the footprint from
    # 20.5k to 30.6k px and the residual share only from 6.16 to 5.51 per cent,
    # i.e. it dilutes rather than cleans. So the meaningful quantity is the RATIO
    # of the footprint's residual share to that untouched floor, and both numbers
    # are printed every run so the judgement is checkable rather than asserted.
    ap.add_argument("--residual-ratio-max", type=float, default=2.0,
                    help="refuse when the footprint trips the thin-structure test "
                         "more than this multiple of untouched field's own rate")
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
    pys, pxs = np.nonzero(protect)
    print("thin structure %.2f%% of frame; figure silhouette %d px, protected "
          "%.2f%% (extent x %d..%d, y %d..%d -- no measured head box needed on "
          "this plate)"
          % (100.0 * thin.mean(), body_px, 100.0 * protect.mean(),
             pxs.min(), pxs.max(), pys.min(), pys.max()), flush=True)

    regions = []
    for name, (x0, y0, x1, y1) in PLANT_BOXES:
        box = np.zeros((H, W), bool)
        box[y0:y1, x0:x1] = True
        sel = thin & box & ~protect
        inside = int((thin & box).sum())
        print("  region %-20s box %s  thin-in-box %d px, %d px after protect"
              % (name, (x0, y0, x1, y1), inside, int(sel.sum())), flush=True)
        regions.append([name, sel, "x", (x0, y0, x1, y1)])

    total = np.zeros((H, W), bool)
    for r in regions:
        r[1] = binary_dilate(r[1], a.remove_grow)
        total |= r[1]
    print("removal footprint %d px (%.2f%% of frame)"
          % (int(total.sum()), 100.0 * total.mean()), flush=True)

    geom = geometry()
    print("drawing: stem (%.0f,%.0f)->(%.0f,%.0f) w %.1f;  EXACTLY 2 leaves at "
          "(%.0f,%.0f) and (%.0f,%.0f) r %.0fx%.0f aspect %.2f;  no branch, no fig"
          % (geom["base"][0], geom["base"][1], geom["apex"][0], geom["apex"][1],
             geom["stem_w"],
             geom["leaves"][0][0], geom["leaves"][0][1],
             geom["leaves"][1][0], geom["leaves"][1][1],
             geom["leaves"][0][2], geom["leaves"][0][3],
             geom["leaves"][0][2] / geom["leaves"][0][3]), flush=True)
    print("plant height %.0f px; apex sits %.0f px BELOW his head top (y 257), so "
          "the SCALE clause r1 already passes is unchanged"
          % (geom["base"][1] - geom["apex"][1], geom["apex"][1] - 257), flush=True)

    if a.dry_run:
        print("DRY RUN -- nothing written.", flush=True)
        return 0

    work = arr.copy()
    colwin = np.zeros((H, W), bool)
    colwin[:, SOURCE_COLUMNS[0]:SOURCE_COLUMNS[1]] = True
    src_ok = (~total) & (~thin) & (~protect) & colwin
    print("clone source restricted to the MEASURED clean field, x %d-%d: %d "
          "eligible px" % (SOURCE_COLUMNS[0], SOURCE_COLUMNS[1], int(src_ok.sum())),
          flush=True)
    for name, m, axis, box in regions:
        work, misses = clone_fill(work, m, src_ok, axis, a.fill_min_dist)
        print("  filled %-20s %6d px, %d without a source" % (name, int(m.sum()), misses),
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
    ctrl = np.zeros((H, W), bool)
    ctrl[300:560, SOURCE_COLUMNS[0]:SOURCE_COLUMNS[1]] = True
    ctrl_px = int((thin_structure(arr, a.thin_k, a.thin_tol) & ctrl).sum())
    r_share = resid_px / max(1, int(total.sum()))
    c_share = ctrl_px / max(1, int(ctrl.sum()))
    ratio = r_share / max(1e-9, c_share)
    print("residual thin structure inside the removal footprint: %d px = %.2f%% of "
          "the footprint" % (resid_px, 100.0 * r_share), flush=True)
    print("the SAME test on an UNTOUCHED window of this plate's own field: %d px = "
          "%.2f%% -- that is the test's FLOOR here, and the removal is %.2fx it"
          % (ctrl_px, 100.0 * c_share, ratio), flush=True)
    if a.assert_clear and ratio > a.residual_ratio_max:
        sys.exit("!! the removal footprint trips the thin-structure test %.2fx as "
                 "often as untouched field does (limit %.2fx) -- refusing to write a "
                 "composite with a half-erased weed in it." % (ratio, a.residual_ratio_max))

    rgb, al, rim, shadow, ridge = draw_sapling(geom, W, H)
    rgb = shade(rgb, al, shadow, ridge, arr)
    a3 = al[:, :, None]
    out = work * (1.0 - a3) + rgb * a3
    r3 = (rim * (al > 0.02))[:, :, None]
    out = np.clip(out * (1.0 - r3 * 0.90) + np.array(RIM_RGB)[None, None, :] * (r3 * 0.90),
                  0, 255)

    drawn = al > 0.02
    dys, dxs = np.nonzero(drawn)
    print("drawn footprint %d px, extent x %d..%d y %d..%d"
          % (int(drawn.sum()), dxs.min(), dxs.max(), dys.min(), dys.max()), flush=True)

    mask = binary_dilate(total | drawn, a.mask_grow)
    mys, mxs = np.nonzero(mask)
    print("inpaint mask %d px (%.2f%% of frame), extent x %d..%d y %d..%d"
          % (int(mask.sum()), 100.0 * mask.mean(), mxs.min(), mxs.max(),
             mys.min(), mys.max()), flush=True)

    # THE CLEARANCE CHECK. A mask that reaches him puts the sampler on terms that
    # PASS -- ONE LEAN ADULT GOBLIN SEATED IN A PATCHWORK CLOAK is r1's, and it is
    # not this rung's to risk. Measured against the protect COMPONENT, which is his
    # actual silhouette, and not against a loose colour test: the field's own grass
    # tufts are green and dark and would score as "him".
    overlap = int((mask & protect).sum())
    body_only = binary_erode(protect, a.protect_grow)  # undo the dilation
    print("mask px inside the dilated protect halo: %d;  inside his silhouette "
          "proper: %d (0 is the target)"
          % (overlap, int((mask & body_only).sum())), flush=True)

    outside = ~binary_dilate(total | drawn, a.mask_grow + 2)
    maxdiff = float(np.abs(out - arr)[outside].max()) if outside.any() else 0.0
    print("max change OUTSIDE the mask: %.1f (0 means every pixel of the six passing "
          "terms is untouched)" % maxdiff, flush=True)

    # count check: by construction, then verified on the pixels
    lum_o = luminance(out)
    leafish = ((out[:, :, 1] - out[:, :, 2]) > 22) & (lum_o < 175)
    zone = np.zeros((H, W), bool)
    zone[290:600, 120:310] = True
    seen = leafish & zone & ~protect
    work_m = seen.copy()
    blobs = []
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
        if n >= 250:
            blobs.append(n)
    print("green blade/stem blobs (>=250 px) in the plant zone: %d %s -- the two "
          "blades and the stem read as ONE component when they touch at the joint, "
          "so 1 or 3 are both expected and the count of BLADES is by construction"
          % (len(blobs), sorted(blobs, reverse=True)), flush=True)
    print("leaves drawn: 2 (by construction); nodes drawn: 1 (by construction); "
          "side-branches drawn: 0; figs drawn: 0", flush=True)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    Image.fromarray(out.astype(np.uint8)).save(a.out)
    Image.fromarray((mask * 255).astype(np.uint8)).save(a.mask_out)
    print("WROTE %s sha %s" % (a.out, sha256_of(a.out)), flush=True)
    print("WROTE %s sha %s" % (a.mask_out, sha256_of(a.mask_out)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
