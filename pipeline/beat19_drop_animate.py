#!/usr/bin/env python3
"""beat19_drop_animate.py -- beat 19's fall, COMPOSITED, not generated.

WHY THIS EXISTS
---------------
`ep2-b19-dropmotion-0819` put the picked plate through the proven LTX i2v recipe
and FAILED decisively: the engine rendered BEAT 20's action inside beat 19 -- he
reached, the plant reverted to the parent's twig-and-crystal, a second fruit
appeared, and 81 of 121 frames put fruit pixels inside the declared body zone,
which is the founder's disqualifying clause. Its own verdict names the cause as
SUBJECT ATTRIBUTION, and `pipeline/work-ladder-0819.md` records the standing rule
that a fourth wording does not fix attribution. The rung the ladder recommends
instead is this file:

    "The camera is locked, the fig is a 32x43px rigid object, the plate is picked
     and passing ... A sprite translated down a parabola over the static plate
     produces a physically exact 32px fall into the grass beside him and CANNOT
     produce any of the three faults that killed this take -- the plant cannot
     revert, he cannot reach, and a second fig cannot appear, because nothing is
     being re-generated."

$0. No model, no GPU, no network. Plain PIL + numpy + one ffmpeg encode.
Deterministic: same arguments, same bytes.

THE FIVE THINGS THAT ARE ACTUALLY HARD HERE, AND WHAT EACH ONE COSTS
--------------------------------------------------------------------
1. THE FIG MUST DETACH WITHOUT LEAVING A GHOST. The fig is not a violet oval, it
   is a violet oval inside a ~3px near-black cel rim, and a mask cut on the
   violet rule alone leaves that rim hanging in the air at the origin for the
   whole clip. So the sprite region is `fill_holes(dilate(violet_component, 4))`
   -- wide enough to contain the rim -- and the ALPHA inside that region is not
   the mask, it is a measured departure from the reconstructed background, so the
   antialiased boundary comes out as partial alpha instead of a staircase.
2. THE HOLE BEHIND IT IS FILLED WITH THE PLATE'S OWN PIXELS, on the vacancy law
   of `pipeline/composite-init-pattern.md` 6 and the same horizontal clone
   `beat19_drop_composite.py` used: every removed pixel takes the nearest clean
   pixel in its own row at least `--fill-min-dist` away. Measured on this plate:
   the field at x 662..702 across the fig's rows is mean (210,207,78) std
   (20,12,3) -- flat -- while the field at x 550..590 is std (52,54,32), because
   his cast SHADOW ends at x~597. So the source is taken from the RIGHT, and
   pixels that fail the thin-structure test are excluded so a blade stroke is
   never cloned into the patch.
3. THE SPRITE IS COMPOSITED PREMULTIPLIED. Rotating and downsampling a
   straight-alpha RGBA sprite interpolates colour across the alpha edge and rings
   the fig with a pale halo -- the "visible cut edge" fail mode by another route.
   Premultiplied is the form that is correct to interpolate: the sprite is stored
   as (R*a, G*a, B*a, a), upsampled 4x ONCE, rotated per frame, downsampled, and
   laid down as out = bg*(1-a) + rgb_premultiplied.
4. IT MUST NOT LOOK LIKE IT IS FLOATING. Two things do that work and both are
   physical rather than decorative: a CONTACT SHADOW that only exists inside the
   last 24px of approach (k = 0.22 at touch, widening and vanishing with height),
   and GRASS-LINE OCCLUSION -- below y 979 the plate's OWN high-pass structure is
   re-composited over the fig, so the blades that are already in the plate cross
   in front of it and it settles INTO the grass instead of onto it. The occluder's
   pixels and its alpha both come from the fig-REMOVED background, which is what
   makes it impossible for it to re-paint a ghost at the origin.
5. THE ROTATION CHANGES THE CONTACT POINT. A 33x44 oval turned 46 degrees is
   26.8px tall from its own centre, not 21.5, so holding the centre fixed sinks
   it 5px into the ground. The path is therefore written in terms of the fig's
   BOTTOM EDGE, and the centre is solved per frame from the current angle.

THE PATH, AND WHY IT IS SHAPED LIKE THIS
----------------------------------------
Every number is in the 704x1280 OUTPUT frame -- the right-anchored cover-crop of
the picked plate, which is the exact framing `ep2-b19-dropmotion-0819` rendered
and pre-registered its geometry on. This file reproduces that crop and ASSERTS
the fig lands where that spec measured it (x 610..642, y 903..946, centroid
(626.3, 924.0), 1133 violet px) before it animates anything.

    f000-f023  (1.000s)  REST. Byte-identical to the plate, by construction:
                         zero displacement, zero rotation, no shadow, no
                         occluder, so the frame IS the cropped plate.
    f024-f033  (0.417s)  FALL. bottom = 946 + 32*u^2 -- quadratic, i.e. constant
                         acceleration, the one motion law a viewer checks without
                         knowing it. Touches down at y 978, the grass line
                         measured at the sapling's own stem base.
    f034-f040  (0.292s)  BOUNCE 1: a 9px hop that lands 8px lower and 12px right.
    f041-f045  (0.208s)  BOUNCE 2: 3.5px, 5px lower, 9px right.
    f046-f052  (0.292s)  ROLL AND SETTLE, ease-out, 6px right, 3px lower.
    f053-f119  (2.792s)  AT REST. Nothing in the frame moves at all.

    Total 120 frames at 24fps = EXACTLY 5.0000s.

Down the whole path it turns 46 degrees, so it ends lying on its side with its
stalk end up -- which is what a fallen fruit looks like, and is a stronger cue
than the 48px of travel. Forward-right, never leftward: the declared body zone is
x 0..500 and the fig ends at x ~638..671, so the founder's no-contact ruling is
satisfied by 138px and by construction, not by luck.

WHY THE TAIL IS FROZEN, SAID PLAINLY
------------------------------------
A composite can move the fig and nothing else. Beat 19's `done_when` asks for the
fall, the landing AND him noticing, in that order; this clip delivers the first
two exactly and the third NOT AT ALL. The 2.79s tail is a still frame. That is a
real limit of this instrument and it is reported in the verdict rather than
dressed up: an honest hold beats an invented head turn, and animating his head
would break the one property that makes this clip trustworthy -- that every pixel
outside the fig's own corridor is bit-identical to the plate the author picked.
"""

import argparse
import hashlib
import math
import os
import shutil
import subprocess
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

# --- pre-registered geometry, 704x1280 output frame ------------------------
# ep2-b19-dropmotion-0819.yaml `pre_registered_geometry`, measured 2026-08-19 on
# the right-anchored crop BEFORE that job was filed. Re-asserted here, not
# re-derived: if this crop does not reproduce them the tool refuses.
FIG_BBOX = (610, 903, 642, 946)          # x0, y0, x1, y1 inclusive
FIG_CENTROID = (626.3, 924.0)
FIG_VIOLET_PX = 1133
Z_BODY = (0, 285, 500, 1015)             # the declared body zone -- DISQUALIFYING
GRASS_LINE = 978.0                       # the sapling's own stem base
SEARCH_WIN = (560, 860, 704, 1000)       # where the fruit may be looked for
# The TRACK window is the search window opened downward to cover the whole path.
# It is a window and not the frame because HIS CLOAK IS PURPLE: a whole-frame
# violet centroid is his cloak's centroid, which is the contamination that
# produced a retracted hue measurement in this lane earlier today.
TRACK_WIN = (560, 860, 704, 1060)

FPS = 24
N_FRAMES = 120                           # 120/24 = 5.0000s -- see PALINDROME note
# render_t3.py:616 reverses any clip whose slot outruns it by >0.05s. Beat 19's
# slot is 1:34-1:39 = 5.000s. At 120 frames dur-cdur is 0.000s, so the palindrome
# cannot fire -- and reversed, this beat would show a fig flying back UP onto a
# stem. This is the only frame count this file will emit.
SLOT_S = 5.000

# path keyframes (frame index, first frame of each phase)
F_FALL, F_B1, F_B2, F_ROLL, F_REST = 24, 34, 41, 46, 53


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def luminance(a):
    return 0.299 * a[:, :, 0] + 0.587 * a[:, :, 1] + 0.114 * a[:, :, 2]


def row_running_mean(arr, k):
    """Exact k-wide running mean of every row -- bit-reproducible, no blur lib.
    Same routine as beat19_drop_composite.py, for the same reason: the field has
    faint HORIZONTAL bands, so a row model cancels them and thin structure
    (blades, the stalk, the fig) survives."""
    H = arr.shape[0]
    pad = np.pad(arr, ((0, 0), (k // 2, k // 2), (0, 0)), mode="edge")
    cs = np.concatenate([np.zeros((H, 1, arr.shape[2])), np.cumsum(pad, axis=1)], axis=1)
    return (cs[:, k:, :] - cs[:, :-k, :]) / float(k)


def thin_structure(arr, k=61, tol=16.0):
    return np.abs(arr - row_running_mean(arr, k)).max(axis=2) > tol


def binary_dilate(mask, r):
    if r <= 0:
        return mask
    img = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1))
    return np.asarray(img) > 127


def fill_holes(mask):
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


def components(mask):
    """All 8-connected components, largest first, as (pixel-list) lists."""
    H, W = mask.shape
    work = mask.copy()
    comps = []
    ys, xs = np.nonzero(work)
    for y0, x0 in zip(ys, xs):
        if not work[y0, x0]:
            continue
        q = deque([(y0, x0)])
        work[y0, x0] = False
        comp = [(y0, x0)]
        while q:
            y, x = q.popleft()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and work[yy, xx]:
                        work[yy, xx] = False
                        q.append((yy, xx))
                        comp.append((yy, xx))
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    return comps


def largest_component(mask):
    comps = components(mask)
    out = np.zeros_like(mask)
    if comps:
        for y, x in comps[0]:
            out[y, x] = True
    return out, (len(comps[0]) if comps else 0)


def violet_mask(u8):
    """The fruit rule from ep2-b19-dropmotion-0819's assert_framing.py, vectorised.
    Kept identical so 'the fig' means the same pixels the bar was written about."""
    hsv = np.asarray(Image.fromarray(u8).convert("HSV")).astype(np.float64)
    hh = hsv[:, :, 0] / 255.0 * 360.0
    s = hsv[:, :, 1] / 255.0
    v = hsv[:, :, 2] / 255.0
    return (hh >= 255) & (hh <= 305) & (s > 0.28) & (v > 0.15) & (v < 0.75)


def four_way_fill(arr, fill, field_ok, max_reach=140):
    """Reconstruct the background under the fig from the nearest FIELD pixel in each
    of the four axis directions, inverse-distance weighted.

    TWO REJECTED ROUNDS ARE COMPRESSED INTO THIS FUNCTION AND BOTH ARE WORTH KEEPING,
    because both were caught by eye at 8-10x and neither was reported by any metric.

    v1, A HORIZONTAL CLONE (beat19_drop_composite.py's own instrument: nearest clean
    pixel in the row, >=26px away, sourced rightward). It filled the hole, but the
    field carries a slow horizontal gradient, so the patch sat up to 29 levels off the
    TRUE background -- and it covered a ring of pixels the fig never occupied. The
    moment the sprite moved half a pixel off that ring, the ring showed: a ragged
    bright fringe down the fig's left side on f024 and nowhere else. That is the
    "visible cut edge" fail mode.

    v2, ROW-WISE LINEAR INTERPOLATION between each span's own two endpoints. Exact at
    the seam in principle, and it produced a visible OLIVE RECTANGLE OF HORIZONTAL
    BANDS -- because the endpoint test was "not thin structure", and on this plate the
    pixels 4px to the fig's upper left are HIS CAST SHADOW, a broad grey-purple mass
    that is not thin and passed the test. Interpolating from purple shadow to yellow
    grass across the fig's rows is exactly what a band of olive is.

    v3, this: the endpoint must be FIELD -- bright and strongly green-over-blue, which
    his shadow is not -- and the estimate is taken from all four directions, so the
    rows whose left endpoint is far away are anchored by the grass directly above and
    below instead of by whatever the row happens to run into.

    v3 IS ONLY THE SEED. Its own output still showed a faint rectangle of streaks at
    6x -- neighbouring rows reach their anchors at different distances and the seams
    between them are visible on a field this flat. `harmonic_fill` below is what
    ships, and this is what it starts from.
    """
    H, W, _ = arr.shape
    out = arr.copy()
    misses = 0
    ys, xs = np.nonzero(fill)
    for y, x in zip(ys, xs):
        num = np.zeros(3)
        den = 0.0
        for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            yy, xx, d = y + dy, x + dx, 1
            while 0 <= yy < H and 0 <= xx < W and d <= max_reach and not field_ok[yy, xx]:
                yy += dy
                xx += dx
                d += 1
            if 0 <= yy < H and 0 <= xx < W and d <= max_reach:
                w = 1.0 / d
                num += arr[yy, xx] * w
                den += w
        if den == 0.0:
            misses += 1
            continue
        out[y, x] = num / den
    return out, misses


def harmonic_fill(arr, solve, known, init, iters=1600, margin=24):
    """Laplace (harmonic) inpaint of `solve`, anchored on `known`, seeded with `init`.

    Every pixel in `solve` becomes the average of its usable neighbours, iterated to
    convergence -- which is the smoothest surface that MATCHES THE BOUNDARY EXACTLY.
    On a field this flat that is indistinguishable from the grass around it, and it is
    the reason the detach leaves nothing to see: there is no seam to see.

    Pixels that are neither `solve` nor `known` -- his cast shadow's edge where it
    abuts the fig, the fig's own stalk -- are excluded from the average rather than
    used as boundary values, so nothing dark leaks into the patch. That exclusion is
    the whole content of the v2 rejection recorded above.
    """
    ys, xs = np.nonzero(solve)
    y0, y1 = max(0, ys.min() - margin), min(arr.shape[0], ys.max() + margin + 1)
    x0, x1 = max(0, xs.min() - margin), min(arr.shape[1], xs.max() + margin + 1)
    U = init[y0:y1, x0:x1].astype(np.float64).copy()
    S = solve[y0:y1, x0:x1]
    usable = S | known[y0:y1, x0:x1]
    uw = usable[:, :, None].astype(np.float64)
    for _ in range(iters):
        acc = np.zeros_like(U)
        cnt = np.zeros(U.shape[:2])
        acc[1:] += U[:-1] * uw[:-1]
        cnt[1:] += usable[:-1]
        acc[:-1] += U[1:] * uw[1:]
        cnt[:-1] += usable[1:]
        acc[:, 1:] += U[:, :-1] * uw[:, :-1]
        cnt[:, 1:] += usable[:, :-1]
        acc[:, :-1] += U[:, 1:] * uw[:, 1:]
        cnt[:, :-1] += usable[:, 1:]
        new = acc / np.maximum(cnt, 1.0)[:, :, None]
        resid = float(np.abs(new - U)[S].max())
        U[S] = new[S]
    out = arr.copy()
    out[y0:y1, x0:x1][S] = U[S]
    return out, resid


# ---------------------------------------------------------------------------
# the path
# ---------------------------------------------------------------------------
def half_height(rot_deg, hw, hh):
    """Vertical half-extent of an ELLIPSE with semi-axes (hw, hh) turned rot degrees.

    sqrt((hw sin)^2 + (hh cos)^2), and the ellipse formula rather than the rectangle's
    hh cos + hw sin is the fourth rejected round: the rectangle bound overstates the
    extent by 8.4px at 46 degrees, so the tool solved the centre from the bottom edge,
    put the centre 8.4px too high, and the landed fig HOVERED over its own contact
    shadow with clear grass between them. Caught at 7x on the landing frame; the bar's
    numbers were all still green, because a bottom-edge target the code then misses is
    invisible to a bar written on the target.
    """
    r = math.radians(abs(rot_deg))
    return math.sqrt((hw * math.sin(r)) ** 2 + (hh * math.cos(r)) ** 2)


def path_at(f, hw, hh):
    """(centre_x, centre_y, rot_deg, bottom_y) of the fig at frame f."""
    cx0, _ = FIG_CENTROID
    x0, y0, x1, y1 = FIG_BBOX
    bx = (x0 + x1) / 2.0
    rest_bottom = float(y1)

    if f < F_FALL:
        dx, rot, bottom = 0.0, 0.0, rest_bottom
    elif f < F_B1:
        u = (f - F_FALL + 1) / float(F_B1 - F_FALL)
        dx, rot, bottom = 2.0 * u * u, 8.0 * u * u, rest_bottom + 32.0 * u * u
    elif f < F_B2:
        u = (f - F_B1 + 1) / float(F_B2 - F_B1)
        bottom = 978.0 + 8.0 * u - 9.0 * math.sin(math.pi * u)
        dx, rot = 2.0 + 12.0 * u, 8.0 + 18.0 * u
    elif f < F_ROLL:
        u = (f - F_B2 + 1) / float(F_ROLL - F_B2)
        bottom = 986.0 + 5.0 * u - 3.5 * math.sin(math.pi * u)
        dx, rot = 14.0 + 9.0 * u, 26.0 + 10.0 * u
    else:
        fr = min(f, F_REST - 1)
        u = (fr - F_ROLL + 1) / float(F_REST - F_ROLL)
        e = 1.0 - (1.0 - u) ** 2
        bottom = 991.0 + 3.0 * e
        dx, rot = 23.0 + 6.0 * e, 36.0 + 10.0 * e

    cy = bottom - half_height(rot, hw, hh)
    return bx + dx, cy, rot, bottom


def ground_at(dx):
    """The ground line under the fig. It recedes toward the camera as the fig
    rolls forward-right: 978 at the drop point, 994 where it comes to rest."""
    return GRASS_LINE + (994.0 - 978.0) * (dx / 29.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="the PICKED 832x1216 plate")
    ap.add_argument("--src-sha256", required=True, help="asserted before anything is read")
    ap.add_argument("--frames-dir", required=True)
    ap.add_argument("--out", required=True, help="mp4")
    ap.add_argument("--crf", type=int, default=18, help="house source-clip encode (post_motion.py)")
    # the RING's ramp only. 6: the reconstruction's own error is under 6 levels.
    # 120: |fig - grass| is 149 on the violet body and 172 on the cel rim under the
    # max-channel metric, and the ring is a mixture of the two.
    ap.add_argument("--alpha-lo", type=float, default=6.0)
    ap.add_argument("--alpha-hi", type=float, default=120.0)
    ap.add_argument("--shadow-k", type=float, default=0.22)
    ap.add_argument("--occlude-y", type=float, default=979.0)
    ap.add_argument("--occlude-max", type=float, default=0.85)
    ap.add_argument("--check-dir", default="", help="where the LOOK-AT-IT images go")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not os.path.isfile(a.src):
        sys.exit("!! src not found: %s" % a.src)
    have = sha256_of(a.src)
    if have != a.src_sha256:
        sys.exit("!! SRC SHA MISMATCH -- refusing.\n   want %s\n   have %s" % (a.src_sha256, have))
    print("src %s sha %s OK" % (a.src, have), flush=True)

    # --- the crop: cover_crop.py --anchor right, reproduced exactly ---------
    W, H = 704, 1280
    im = Image.open(a.src).convert("RGB")
    sw, sh = im.size
    scale = max(W / float(sw), H / float(sh))
    nw, nh = int(round(sw * scale)), int(round(sh * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    left, top = nw - W, (nh - H) // 2
    plate = im.crop((left, top, left + W, top + H))
    print("cover-crop %dx%d scale=%.4f -> %dx%d anchor=right box (%d,%d)"
          % (sw, sh, scale, nw, nh, left, top), flush=True)
    P8 = np.asarray(plate).astype(np.uint8)
    P = P8.astype(np.float64)

    # --- ASSERT the pre-registered geometry, before anything moves ----------
    win = np.zeros((H, W), bool)
    wx0, wy0, wx1, wy1 = SEARCH_WIN
    win[wy0:wy1, wx0:wx1] = True
    viol = violet_mask(P8) & win
    comp, npx = largest_component(viol)
    ys, xs = np.nonzero(comp)
    bb = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    cxm, cym = float(xs.mean()), float(ys.mean())
    print("fig: %d px  bbox %s  centroid (%.1f,%.1f)" % (npx, bb, cxm, cym), flush=True)
    if bb != FIG_BBOX or npx != FIG_VIOLET_PX:
        sys.exit("!! GEOMETRY MISMATCH -- this crop is not the frame the bar was written on.\n"
                 "   want bbox %s %d px\n   have bbox %s %d px" % (FIG_BBOX, FIG_VIOLET_PX, bb, npx))
    if abs(cxm - FIG_CENTROID[0]) > 0.5 or abs(cym - FIG_CENTROID[1]) > 0.5:
        sys.exit("!! centroid %.1f,%.1f != pre-registered %s" % (cxm, cym, FIG_CENTROID))
    print("geometry matches ep2-b19-dropmotion-0819's pre-registered numbers exactly", flush=True)

    # --- sprite region: violet + its cel rim, holes closed ------------------
    region = fill_holes(binary_dilate(comp, 4))
    print("sprite region %d px (violet %d + %d of cel rim and antialias)"
          % (int(region.sum()), npx, int(region.sum()) - npx), flush=True)

    # --- the hole behind it: horizontal clone from the RIGHT ----------------
    thin = thin_structure(P)
    lumP = luminance(P)
    # NO SAFETY GAP between the region and its sources, and that is not laziness --
    # it is the third rejected round. With `~binary_dilate(region, 2)` in this test the
    # harmonic solve had NO BOUNDARY AT ALL: every neighbour of every solved pixel was
    # in the excluded ring, so the iteration was an unanchored diffusion and converged
    # to the seed's MEAN -- a dead-flat patch, measured interior std 0.1 against the
    # field's 4.3, and visible at 2x as a fig-shaped blob 9 levels off its own
    # surroundings. A Dirichlet condition has to touch the thing it conditions. The
    # gap is unnecessary anyway: the cel rim lives within 2px of the violet body
    # (measured ring means: r1 lum 37, r2 135, r3 191, r4 192), and the region is
    # already dilated 4.
    field_ok = ((~region) & (~thin) & (lumP > 150.0)
                & ((P[:, :, 1] - P[:, :, 2]) > 55.0))
    print("field-source pixels within 60px of the fig: %d (grass is lum ~200, G-B ~129; "
          "his cast shadow is neither)"
          % int(field_ok[FIG_BBOX[1] - 60:FIG_BBOX[3] + 60, FIG_BBOX[0] - 60:FIG_BBOX[2] + 60].sum()),
          flush=True)
    if a.dry_run:
        print("DRY RUN -- nothing written.", flush=True)
        return 0
    seed, misses = four_way_fill(P, region, field_ok)
    print("seeded %d px from four-way field sources, %d with no source in reach"
          % (int(region.sum()), misses), flush=True)
    if misses:
        sys.exit("!! %d pixels had no clean endpoint -- that is a hole, not a patch." % misses)
    BG0, resid = harmonic_fill(P, region, field_ok, seed)
    ring = binary_dilate(region, 10) & (~binary_dilate(region, 3)) & field_ok
    print("harmonic solve: moved the seed by up to %.1f levels, final residual %.4f\n"
          "  patch interior mean %s std %s   surrounding field mean %s std %s"
          % (float(np.abs(BG0 - seed)[region].max()), resid,
             np.round(BG0[region].mean(0), 1), np.round(BG0[region].std(0), 1),
             np.round(P[ring].mean(0), 1), np.round(P[ring].std(0), 1)), flush=True)

    # --- alpha, measured as departure from the reconstructed background -----
    # Two passes, and the second one MATTERS: the region is deliberately wider than
    # the fig (it has to be, to contain the cel rim), so pass 1 reconstructs the
    # whole span and pass 2 then hands every pixel the fig never occupied straight
    # back to the plate. Only what the fig actually covered is ever replaced.
    # THE CORE IS OPAQUE BY CLASSIFICATION, NOT BY THRESHOLD, and that correction is
    # the second rejected round. A pure dist/D ramp made the fig TRANSLUCENT: under
    # the max-channel metric the violet body is only 149 levels from the grass
    # (|58-207| on green), so a D of 150 handed the body alpha 0.85-0.99, grass showed
    # through the fruit, and the violet-blob track fell from 1133 px to 680 -- the
    # measurement that caught it. The fig's body and its near-black cel rim are FIG,
    # full stop; only the antialiased boundary ring is a mixture.
    dist0 = np.abs(P - BG0).max(axis=2)
    core = fill_holes(comp | ((luminance(P) < 100.0) & region))
    ring = np.clip((dist0 - a.alpha_lo) / (a.alpha_hi - a.alpha_lo), 0.0, 1.0)
    alpha = np.maximum(core.astype(np.float64), ring) * region
    support = binary_dilate(alpha > 0.0, 1) & region
    BGf = np.where(support[:, :, None], BG0, P)
    BG8 = np.clip(np.rint(BGf), 0, 255).astype(np.uint8)
    BGf = BG8.astype(np.float64)
    alpha = alpha * support
    patch_support = np.abs(BGf - P).max(axis=2) > 0
    print("BG replaced on %d px of the region's %d; %d px of true background handed back "
          "to the plate" % (int(patch_support.sum()), int(region.sum()),
                            int(region.sum()) - int(support.sum())), flush=True)
    ys, xs = np.nonzero(alpha > 0.0)
    sx0, sy0, sx1, sy1 = int(xs.min()) - 1, int(ys.min()) - 1, int(xs.max()) + 2, int(ys.max()) + 2
    sub_a = alpha[sy0:sy1, sx0:sx1]
    sub_rgb = P[sy0:sy1, sx0:sx1]
    print("sprite tile %dx%d, alpha>0.99 on %d px, partial on %d px"
          % (sx1 - sx0, sy1 - sy0, int((sub_a > 0.99).sum()),
             int(((sub_a > 0.0) & (sub_a <= 0.99)).sum())), flush=True)
    # PREMULTIPLIED RGBA, and the colour is NOT the plate's pixel. An antialiased
    # edge pixel is already a mixture of fig and grass, so laying it down at a new
    # place composites the old grass in twice and the fig comes out ringed. The
    # premultiplied fig colour is P - (1-a)*BG -- subtract the background the plate
    # pixel already contains -- and it has the property that recompositing over the
    # SAME background returns the plate exactly, for any alpha, right or wrong.
    sub_bg = BGf[sy0:sy1, sx0:sx1]
    prem = np.zeros((sy1 - sy0, sx1 - sx0, 4), np.uint8)
    prem[:, :, :3] = np.clip(np.rint(sub_rgb - (1.0 - sub_a[:, :, None]) * sub_bg),
                             0, 255).astype(np.uint8)
    prem[:, :, 3] = np.clip(np.rint(sub_a * 255.0), 0, 255).astype(np.uint8)
    SS = 4
    sprite4 = Image.fromarray(prem).resize(((sx1 - sx0) * SS, (sy1 - sy0) * SS), Image.LANCZOS)
    # the sprite's centre, in sprite-tile coordinates, is the fig bbox centre
    hw = (FIG_BBOX[2] - FIG_BBOX[0]) / 2.0 + 1.5   # +rim
    hh = (FIG_BBOX[3] - FIG_BBOX[1]) / 2.0 + 1.5
    sc_x = (FIG_BBOX[0] + FIG_BBOX[2]) / 2.0 - sx0
    sc_y = (FIG_BBOX[1] + FIG_BBOX[3]) / 2.0 - sy0

    # --- the grass occluder: the BACKGROUND's own high-pass structure -------
    dev = np.abs(BGf - row_running_mean(BGf, 61)).max(axis=2)
    yy = np.arange(H, dtype=np.float64)[:, None] * np.ones((1, W))
    ramp = np.clip((yy - a.occlude_y) / 8.0, 0.0, 1.0)
    occ_a = np.clip((dev - 6.0) / 18.0, 0.0, 1.0) * ramp * a.occlude_max
    print("grass occluder: mean alpha %.3f over y>=%d, max %.2f"
          % (occ_a[int(a.occlude_y):, :].mean(), int(a.occlude_y), occ_a.max()), flush=True)

    os.makedirs(a.frames_dir, exist_ok=True)
    xg, yg = np.meshgrid(np.arange(W, dtype=np.float64), np.arange(H, dtype=np.float64))

    twin = np.zeros((H, W), bool)
    tx0w, ty0w, tx1w, ty1w = TRACK_WIN
    twin[ty0w:ty1w, tx0w:tx1w] = True

    # THE CORRIDOR IS A UNION OF BOXES, not of alpha thresholds. Anything the
    # animation can possibly have touched on any frame -- the patch, every sprite
    # tile, every shadow ellipse -- goes in by its bounding box, and B1 then asserts
    # bit-identity on the complement. A box cannot be talked into being too small.
    corridor = patch_support.copy()
    track = []
    for f in range(N_FRAMES):
        cx, cy, rot, bottom = path_at(f, hw, hh)
        dxs = cx - (FIG_BBOX[0] + FIG_BBOX[2]) / 2.0
        fa_bottom = FIG_BBOX[3]
        if f < F_FALL:
            out8 = P8.copy()                      # the plate itself, byte for byte
        else:
            frame = BGf.copy()
            # contact shadow -- exists only inside the last 24px of approach
            gap = max(0.0, ground_at(dxs) - bottom)
            k = a.shadow_k * max(0.0, min(1.0, (24.0 - gap) / 24.0))
            if k > 0.0:
                ex, ey = cx, ground_at(dxs)
                rx, ry = 15.0 + 0.35 * gap, 5.0 + 0.10 * gap
                rr = ((xg - ex) / rx) ** 2 + ((yg - ey) / ry) ** 2
                g = np.clip(1.0 - rr, 0.0, 1.0)
                frame = frame * (1.0 - k * g)[:, :, None]
                corridor[int(ey - ry) - 1:int(ey + ry) + 2, int(ex - rx) - 1:int(ex + rx) + 2] = True
            # the fig: premultiplied, rotated at 4x, laid down to quarter-pixel
            rot4 = sprite4.rotate(-rot, resample=Image.BICUBIC, expand=True)
            r4 = np.asarray(rot4)
            h4, w4 = r4.shape[0], r4.shape[1]
            bx0 = int(math.floor(cx - w4 / (2.0 * SS))) - 2
            by0 = int(math.floor(cy - h4 / (2.0 * SS))) - 2
            tw1, th1 = w4 // SS + 5, h4 // SS + 5
            tile4 = np.zeros((th1 * SS, tw1 * SS, 4), np.uint8)
            ox = int(round(SS * (cx - bx0))) - w4 // 2
            oy = int(round(SS * (cy - by0))) - h4 // 2
            tile4[oy:oy + h4, ox:ox + w4] = r4
            tile1 = np.asarray(Image.fromarray(tile4).resize((tw1, th1), Image.LANCZOS)).astype(np.float64)
            fa = np.zeros((H, W))
            frgb = np.zeros((H, W, 3))
            fa[by0:by0 + th1, bx0:bx0 + tw1] = np.clip(tile1[:, :, 3] / 255.0, 0.0, 1.0)
            frgb[by0:by0 + th1, bx0:bx0 + tw1] = np.clip(tile1[:, :, :3], 0.0, 255.0)
            frgb = np.minimum(frgb, fa[:, :, None] * 255.0)   # no over-bright halo
            frame = frame * (1.0 - fa[:, :, None]) + frgb
            # grass in FRONT: the BACKGROUND's own structure, over the fig only. Its
            # pixels and its alpha both come from the fig-removed plate, which is
            # what makes it structurally unable to re-paint a ghost at the origin.
            oa = occ_a * (fa > 0.0)
            frame = frame * (1.0 - oa[:, :, None]) + BGf * oa[:, :, None]
            out8 = np.clip(np.rint(frame), 0, 255).astype(np.uint8)
            corridor[by0:by0 + th1, bx0:bx0 + tw1] = True
            # the fig's own footprint bottom, read off the alpha rather than off the
            # violet rule, so the grass occluder cannot make the fig look higher than
            # it is. This is the number that catches a hover.
            fa_bottom = int(np.nonzero((fa > 0.5).any(axis=1))[0].max())
        Image.fromarray(out8).save(os.path.join(a.frames_dir, "f%04d.png" % f))
        # per-frame track of the fig, measured on the WRITTEN frame, in the window
        v = violet_mask(out8) & twin
        vy, vx = np.nonzero(v)
        track.append(dict(f=f, n=int(v.sum()),
                          cx=float(vx.mean()) if len(vx) else float("nan"),
                          cy=float(vy.mean()) if len(vy) else float("nan"),
                          y1=int(vy.max()) if len(vy) else -1,
                          x0=int(vx.min()) if len(vx) else 10 ** 6,
                          rot=rot, bottom=bottom, path_cy=cy, fa_bottom=fa_bottom))
    print("wrote %d frames to %s" % (N_FRAMES, a.frames_dir), flush=True)

    # --- THE BAR, asserted numerically -------------------------------------
    fail = []
    corr = binary_dilate(corridor, 1)
    print("\n-- bar --", flush=True)
    print("corridor: %d px (%.3f%% of frame)" % (int(corr.sum()), 100.0 * corr.mean()), flush=True)

    # B1 everything else byte-identical
    worst = 0
    for f in range(N_FRAMES):
        fr = np.asarray(Image.open(os.path.join(a.frames_dir, "f%04d.png" % f))).astype(np.int16)
        d = np.abs(fr - P8.astype(np.int16)).max(axis=2)
        worst = max(worst, int(d[~corr].max()))
    print("B1 max |frame - plate| OUTSIDE the corridor, over all %d frames: %d"
          % (N_FRAMES, worst), flush=True)
    if worst != 0:
        fail.append("B1 background not byte-identical (max %d)" % worst)

    # B2 f000 IS the plate
    f0 = np.asarray(Image.open(os.path.join(a.frames_dir, "f0000.png"))).astype(np.int16)
    d0 = int(np.abs(f0 - P8.astype(np.int16)).max())
    print("B2 f000 vs the cropped picked plate: max diff %d" % d0, flush=True)
    if d0 != 0:
        fail.append("B2 f000 is not the plate (max %d)" % d0)

    # B3 detaches cleanly -- no ghost at the origin, and no residue of the cel rim.
    # THE BOX IS THE TOP 26 ROWS OF THE ORIGIN, NOT THE WHOLE ORIGIN, and the reason
    # is a fact about this beat rather than a convenience: the fall is 37px of bottom
    # travel on a 43px fig, so the fig ALWAYS overlaps its own starting box and would
    # score itself as its own ghost on every frame. y 900..925 is the band the fig
    # occupied at f000 and never occupies again -- its top rim and upper body -- so a
    # cut that left anything behind leaves it exactly here. Read after the landing.
    ox0, oy0, ox1, oy1 = FIG_BBOX
    obox = np.zeros((H, W), bool)
    obox[oy0 - 3:oy0 + 23, ox0 - 3:ox1 + 4] = True
    # the dark test excludes the top rows, because the fig's STALK is near-black and
    # STAYS -- a pedicel left on the branch is what a picked fruit leaves behind, and
    # it is not a ghost. Measured: the stalk's tip reaches y 914.
    dbox = np.zeros((H, W), bool)
    dbox[oy0 + 14:oy0 + 23, ox0 - 3:ox1 + 4] = True
    last = np.asarray(Image.open(os.path.join(a.frames_dir, "f%04d.png" % F_ROLL)))
    ghost = int((violet_mask(last) & obox).sum())
    ghost_d = float(np.abs(last.astype(np.float64) - BGf)[obox].max())
    dark = int(((luminance(last.astype(np.float64)) < 140.0) & dbox).sum())
    print("B3 origin box at f%03d: %d violet px (want 0), %d px darker than lum 140 in the body "
          "box (the cel rim is ~200 px of it; want 0); max departure from the patch %.1f"
          % (F_ROLL, ghost, dark, ghost_d), flush=True)
    if ghost != 0:
        fail.append("B3 %d violet px left at the origin" % ghost)
    if dark != 0:
        fail.append("B3 %d dark px left at the origin -- cel-rim ghost" % dark)
    if ghost_d != 0.0:
        fail.append("B3 origin box is not exactly the patch (max %.1f)" % ghost_d)

    # B4 present in every frame, continuous, accelerating, monotone in the fall
    gone = [t["f"] for t in track if t["n"] < 300]
    jumps = []
    for i in range(1, N_FRAMES):
        d = math.hypot(track[i]["cx"] - track[i - 1]["cx"], track[i]["cy"] - track[i - 1]["cy"])
        if d > 12.0:
            jumps.append((i, round(d, 1)))
    dec = [(t["f"], round(t["cy"] - track[t["f"] - 1]["cy"], 2))
           for t in track[F_FALL:F_B1] if t["cy"] < track[t["f"] - 1]["cy"] - 2.0]
    steps = [round(track[i]["cy"] - track[i - 1]["cy"], 2) for i in range(F_FALL, F_B1)]
    psteps = [round(track[i]["path_cy"] - track[i - 1]["path_cy"], 3) for i in range(F_FALL, F_B1)]
    print("B4 blob present in all frames: %s (n range %d..%d)"
          % (not gone, min(t["n"] for t in track), max(t["n"] for t in track)), flush=True)
    print("   fall-window per-frame descent, MEASURED: %s" % steps, flush=True)
    print("   fall-window per-frame descent, PATH:     %s" % psteps, flush=True)
    print("   frame-to-frame jumps >12px: %s ; descents reversing >2px: %s" % (jumps, dec), flush=True)
    if gone:
        fail.append("B4 blob missing/too small on frames %s" % gone[:6])
    if jumps:
        fail.append("B4 discontinuous jumps %s" % jumps[:6])
    if dec:
        fail.append("B4 fall not monotone %s" % dec[:6])
    # acceleration is asserted on the PATH, which is exact; the measured column is
    # a centroid of a resampled blob and carries subpixel noise by construction.
    if not all(psteps[i] < psteps[i + 1] for i in range(len(psteps) - 1)):
        fail.append("B4 fall not accelerating: %s" % psteps)

    # B5 lands and rests
    tot = track[N_FRAMES - 1]["cy"] - track[0]["cy"]
    rest_move = max(math.hypot(track[i]["cx"] - track[N_FRAMES - 12]["cx"],
                               track[i]["cy"] - track[N_FRAMES - 12]["cy"])
                    for i in range(N_FRAMES - 12, N_FRAMES))
    print("B5 total centroid descent %.1f px; bottom edge y %d -> %d; motion over the final "
          "12 frames %.2f px" % (tot, track[0]["y1"], track[N_FRAMES - 1]["y1"], rest_move), flush=True)
    if tot < 20.0:
        fail.append("B5 descent only %.1f px" % tot)
    if track[N_FRAMES - 1]["y1"] < 965:
        fail.append("B5 bottom edge only reached y %d" % track[N_FRAMES - 1]["y1"])
    if rest_move > 3.0:
        fail.append("B5 still moving at the end (%.2f px)" % rest_move)
    # B5b IT IS ACTUALLY ON THE GROUND. Alpha footprint, not the violet rule.
    gline = ground_at(29.0)
    hover = track[N_FRAMES - 1]["fa_bottom"] - gline
    print("B5b at rest the fig's own footprint bottom is y %d against a ground line of y %.0f "
          "-- hover %+.0f px (a positive number is the fig sunk in, a negative one is it "
          "floating over its shadow)" % (track[N_FRAMES - 1]["fa_bottom"], gline, hover), flush=True)
    if abs(hover) > 3.0:
        fail.append("B5b fig is %.0f px off the ground at rest" % hover)

    # B6 ZERO body contact, in either direction, in any frame
    zb = np.zeros((H, W), bool)
    zb[Z_BODY[1]:Z_BODY[3], Z_BODY[0]:Z_BODY[2]] = True
    worst_x = min(t["x0"] for t in track)
    contact = int((corr & zb).sum())
    print("B6 leftmost fig pixel over the whole clip: x %d (Z-BODY ends at x %d, margin %d px); "
          "corridor n Z-BODY = %d px" % (worst_x, Z_BODY[2], worst_x - Z_BODY[2], contact), flush=True)
    if contact != 0 or worst_x <= Z_BODY[2]:
        fail.append("B6 BODY CONTACT -- disqualifying")

    # B7 EXACTLY ONE FRUIT in every frame. This is the clause the i2v take failed
    # hardest (a second fig appeared and the plant reverted); here it is structural,
    # because nothing is generated -- but it is measured anyway, on every frame.
    nblob = []
    bad = []
    for f in range(N_FRAMES):
        fr = np.asarray(Image.open(os.path.join(a.frames_dir, "f%04d.png" % f)))
        comps = [len(c) for c in components(violet_mask(fr) & twin) if len(c) >= 200]
        if f in (0, F_FALL + 5, F_B1 + 3, N_FRAMES - 1):
            nblob.append((f, comps))
        if len(comps) != 1:
            bad.append((f, comps))
    print("B7 violet blobs >=200px in the track window (f, sizes): %s" % nblob, flush=True)
    print("   frames without exactly one: %s" % (bad[:6] if bad else "none"), flush=True)
    if bad:
        fail.append("B7 not exactly one fruit on %d frames %s" % (len(bad), bad[:4]))

    # B8 duration
    print("B8 %d frames at %d fps = %.4fs against a %.3fs slot -- palindrome margin %.4fs "
          "(fires only above 0.05)" % (N_FRAMES, FPS, N_FRAMES / float(FPS), SLOT_S,
                                       SLOT_S - N_FRAMES / float(FPS)), flush=True)
    if N_FRAMES / float(FPS) > SLOT_S:
        fail.append("B8 clip outruns its slot")

    # --- CHECK IMAGES. The frames are the verdict; these are how they get read.
    if a.check_dir:
        os.makedirs(a.check_dir, exist_ok=True)
        strip_f = [0, F_FALL + 3, F_FALL + 6, F_FALL + 9, F_B1 + 2, F_B1 + 5,
                   F_B2 + 2, F_ROLL + 3, F_REST, N_FRAMES - 1]
        box = (585, 880, 700, 1012)
        z = 4
        cw, ch = (box[2] - box[0]) * z, (box[3] - box[1]) * z
        strip = Image.new("RGB", (len(strip_f) * (cw + 6) - 6, ch), (20, 20, 20))
        for i, f in enumerate(strip_f):
            fr = Image.open(os.path.join(a.frames_dir, "f%04d.png" % f))
            strip.paste(fr.crop(box).resize((cw, ch), Image.NEAREST), (i * (cw + 6), 0))
        strip.save(os.path.join(a.check_dir, "CHECK-b19-fall-strip-4x.png"))
        pair = Image.new("RGB", (2 * (ox1 - ox0 + 20) * 6 + 8, (oy1 - oy0 + 24) * 6), (20, 20, 20))
        for i, f in enumerate((0, N_FRAMES - 1)):
            fr = Image.open(os.path.join(a.frames_dir, "f%04d.png" % f))
            c = fr.crop((ox0 - 10, oy0 - 12, ox1 + 10, oy1 + 12))
            pair.paste(c.resize((c.width * 6, c.height * 6), Image.NEAREST),
                       (i * (c.width * 6 + 8), 0))
        pair.save(os.path.join(a.check_dir, "CHECK-b19-detach-origin-6x.png"))
        lf = Image.open(os.path.join(a.frames_dir, "f%04d.png" % (N_FRAMES - 1)))
        lc = lf.crop((615, 950, 700, 1015))
        lc.resize((lc.width * 7, lc.height * 7), Image.NEAREST).save(
            os.path.join(a.check_dir, "CHECK-b19-landing-7x.png"))
        # before/after at 3x -- the one image that answers "did it fall" in one look
        bb = (560, 880, 704, 1020)
        ba = Image.new("RGB", (2 * (bb[2] - bb[0]) * 3 + 8, (bb[3] - bb[1]) * 3), (20, 20, 20))
        for i, f in enumerate((0, N_FRAMES - 1)):
            c = Image.open(os.path.join(a.frames_dir, "f%04d.png" % f)).crop(bb)
            ba.paste(c.resize((c.width * 3, c.height * 3), Image.NEAREST),
                     (i * ((bb[2] - bb[0]) * 3 + 8), 0))
        ba.save(os.path.join(a.check_dir, "CHECK-b19-before-after-3x.png"))
        # and the same pair as WHOLE FRAMES at half scale, which is roughly how it will
        # be watched -- the honest test of whether a 48px event reads at all
        ff2 = Image.new("RGB", (2 * (W // 2) + 6, H // 2), (20, 20, 20))
        for i, f in enumerate((0, N_FRAMES - 1)):
            c = Image.open(os.path.join(a.frames_dir, "f%04d.png" % f)).resize(
                (W // 2, H // 2), Image.LANCZOS)
            ff2.paste(c, (i * (W // 2 + 6), 0))
        ff2.save(os.path.join(a.check_dir, "CHECK-b19-wholeframe-half.png"))
        # the whole path in one still: every frame's fig, darkest-wins over the plate
        tr = P8.astype(np.int16).copy()
        for f in range(F_FALL, N_FRAMES, 2):
            fr = np.asarray(Image.open(os.path.join(a.frames_dir, "f%04d.png" % f))).astype(np.int16)
            m = violet_mask(np.asarray(Image.open(os.path.join(a.frames_dir, "f%04d.png" % f)))) & twin
            tr[m] = fr[m]
        Image.fromarray(np.clip(tr, 0, 255).astype(np.uint8)).crop((520, 860, 704, 1040)).resize(
            (184 * 4, 180 * 4), Image.NEAREST).save(
            os.path.join(a.check_dir, "CHECK-b19-path-trails-4x.png"))
        print("check images -> %s" % a.check_dir, flush=True)

    # --- encode: post_motion.py's settings ---------------------------------
    ff = shutil.which("ffmpeg")
    if not ff:
        sys.exit("!! ffmpeg not on PATH")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    r = subprocess.run([ff, "-y", "-v", "error", "-framerate", str(FPS),
                        "-i", os.path.join(a.frames_dir, "f%04d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(a.crf),
                        "-movflags", "+faststart", a.out], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode:
        sys.exit("!! ffmpeg failed:\n%s" % r.stderr[-1500:])
    print("\nWROTE %s (%d bytes) sha %s" % (a.out, os.path.getsize(a.out), sha256_of(a.out)), flush=True)
    b = subprocess.run([ff, "-i", a.out, "-map", "0:v:0", "-c", "copy", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    for line in b.splitlines():
        if "frame=" in line or "Duration" in line:
            print("   " + line.strip(), flush=True)

    print("\n%s" % ("BAR: PASS -- every clause" if not fail else "BAR: FAIL\n  - " + "\n  - ".join(fail)),
          flush=True)
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
