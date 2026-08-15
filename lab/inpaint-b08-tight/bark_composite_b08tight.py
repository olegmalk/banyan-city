#!/usr/bin/env python3
r"""BEAT 08 TIGHT-SHOT copy. Composite procedural bark relief INTO a plate's
board region. $0, no sampler.

LANE-SCOPED ON PURPOSE (shared worktree). Adapted from lab/inpaint-b08/
bark_composite_b08.py. THE NOISE, HOMOGRAPHY, MEASURED-LIGHT AND VALUE-MATCH
MACHINERY IS UNCHANGED -- that is the point, so that the only thing this lane
changes against the five failing samples is the SHOT SCALE of the plate the
relief goes into. What is re-derived is the segmentation, because this is a
fourth different board and nothing has ever transferred:

  * THE COLOUR RULE CHANGES AGAIN, AND IT IS A THIRD DISCRIMINANT. Beat 10's
    navy face was B-R >= 10. Beat 06's near-black board needed B-R >= -2.
    Beat 08 r3-s0's maroon face inverted that (B-R -10..-12) and needed B-G.
    THIS board is warm mid-brown, (91..110, 69..79, 58..64), and B-G is -11..-15
    on it -- the sign beat 08 r3-s0 used to ACCEPT with (+4..+6), so r3-s0's own
    fence would have rejected this entire board. What separates it here is R-G:
    board +20..+31, against the goblin's teal robe -39..-57, his green hand
    -26..-2, and the guard's brown cloak +27 at B-G -4. So the rule is
    R-G >= 16 AND B-G <= -8 AND 60 < L < 100, which finds ONE component of
    29752 px, bbox 204x266 -- 1.65x the pixels of the board the five failing
    samples worked on.
  * THE QUAD IS TRACED AFRESH BY SCANLINES on rows and columns no hand
    occludes, and the four lines fitted with their residuals reported:
        left    x = 235.6 - 0.1415*y   maxres 2.4px  (rows 572..600, 748..787)
        right   x = 455.8 - 0.2126*y   maxres 0.4px  (rows 600..790)
        bottom  y = 760.1 + 0.2349*x   maxres 1.0px  (cols 130..270)
        top     y = fitted on the columns the CLIP does not occlude only --
                see the next bullet, which is why it needs saying separately.
    The board is a rectangle rotated ~12 degrees clockwise in frame space, not
    a shear: the left edge and the top edge are perpendicular to within a
    degree, which the sheared beat 08 r3-s0 board was not.
  * THE CLIP PROTRUDES ABOVE THE BOARD AGAIN and this time it also occludes the
    TOP EDGE ITSELF. Fitting the top edge on every column gives 9.7px of
    residual, because under the clip (x 196..280) the segment's topmost board
    pixel is the clip's lower boundary, 10-14px too low. Fitted on the clean
    columns only (x 166..194 and 282..322) the residual falls to ~1px and the
    two clean spans agree: extrapolating the left span to x=282 predicts
    y=573.6 against a measured 573. So the top line is fitted there, and the
    quad is then RAISED above the clip so that the clip is inside the mask --
    the bar says no chrome clip, and the sampler can never touch what the mask
    does not contain.
  * A TOP BAND PARALLEL TO THE TOP EDGE IS FILLED UNCONDITIONALLY. beat 08
    r3-s0 used a horizontal `flat_top_y` because its board had a flat top. This
    board is rotated 12 degrees, so a horizontal cut would take a wedge. The
    band is measured along the board's own top normal instead. Inside it are
    the clip, the raise strip, and a sliver of the goblin's teal robe; the
    board ends up ~14px taller than the plate's, which is still large, flat,
    rectangular and clipless, and it is said here rather than discovered later.
  * THE OCCLUDER RULE IS HUE, NOT BRIGHTNESS. beat 08 r3-s0 used L>125 &
    R-G<35. The hand lying across THIS board is a GREEN hand whose shaded half
    is L 118, below that threshold, so brightness alone would paint bark over
    half of it. R-G separates them cleanly with no overlap: board +20..+31,
    hand -26..-2. So an occluder is R-G < 12 AND L > 55, dilated once.
  * THE HAND CROSSING THE FACE IS NOT A PROBLEM AT 0.30, and that is measured,
    not hoped: beat 06 passed with a crossing hand inside its mask because the
    region only dissolves at the strength that starts restyling the hand, and
    0.30 is below it. The hand is a CONTROL here, not a risk.
"""


from __future__ import annotations

import argparse
import hashlib
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def lum_of(a: np.ndarray) -> np.ndarray:
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


# ---------------------------------------------------------------- noise


def value_noise(h: int, w: int, gy: int, gx: int, rng) -> np.ndarray:
    """Bicubic-upsampled random grid. gx > gy => features taller than wide."""
    g = rng.random((gy + 3, gx + 3))
    z = ndimage.zoom(g, (float(h) / (gy + 3), float(w) / (gx + 3)), order=3)
    z = z[:h, :w]
    if z.shape != (h, w):  # zoom rounding
        z = np.pad(z, ((0, h - z.shape[0]), (0, w - z.shape[1])), mode="edge")
    lo, hi = z.min(), z.max()
    return (z - lo) / max(hi - lo, 1e-6)


def fbm(h: int, w: int, gy: int, gx: int, octaves: int, rng, gain: float = 0.5):
    out = np.zeros((h, w), np.float64)
    amp, tot = 1.0, 0.0
    for i in range(octaves):
        out += amp * value_noise(h, w, gy * (2 ** i), gx * (2 ** i), rng)
        tot += amp
        amp *= gain
    out /= tot
    lo, hi = out.min(), out.max()
    return (out - lo) / max(hi - lo, 1e-6)


def bark_height(h: int, w: int, seed: int, nscale: float = 1.0):
    """Height field in [0,1] plus a low-frequency mottle for albedo."""
    rng = np.random.default_rng(seed)
    # long vertical plates: ~3:1 anisotropy (more cells across x than down y).
    # v1 used gx=20 with 4 octaves and read as scratched burlap -- too many thin
    # lines. Fewer, wider plates and fewer octaves is what makes it bark.
    def S(v):
        return max(int(round(v * nscale)), 1)
    n1 = fbm(h, w, gy=S(2), gx=S(16), octaves=3, rng=rng)
    # fissures live where n1 crosses 0.5; distance from 0.5 is plate height
    f1 = np.clip(np.abs(2.0 * n1 - 1.0) * 1.55, 0.0, 1.0) ** 0.55
    # sub-fissures, finer and slightly less anisotropic
    n2 = fbm(h, w, gy=S(7), gx=S(22), octaves=2, rng=rng)
    f2 = np.clip(np.abs(2.0 * n2 - 1.0) * 2.10, 0.0, 1.0) ** 0.80
    furrow = f1 * (0.84 + 0.16 * f2)
    # occasional horizontal checking, kept subtle
    nh = fbm(h, w, gy=S(18), gx=S(5), octaves=2, rng=rng)
    cracks = np.clip(1.0 - np.abs(2.0 * nh - 1.0) * 3.6, 0.0, 1.0)
    furrow *= 1.0 - 0.18 * cracks
    # flaking crust
    grain = fbm(h, w, gy=S(48), gx=S(58), octaves=2, rng=rng)
    # broad mottle
    mottle = fbm(h, w, gy=S(3), gx=S(4), octaves=2, rng=rng)
    hgt = 0.69 * furrow + 0.11 * grain + 0.20 * mottle
    lo, hi = hgt.min(), hgt.max()
    hgt = (hgt - lo) / max(hi - lo, 1e-6)
    return hgt, mottle, furrow


# ---------------------------------------------------------------- homography


def homography(src, dst):
    """3x3 H with H @ [sx,sy,1] ~ [dx,dy,1]."""
    A, b = [], []
    for (sx, sy), (dx, dy) in zip(src, dst):
        A.append([sx, sy, 1, 0, 0, 0, -sx * dx, -sy * dx]); b.append(dx)
        A.append([0, 0, 0, sx, sy, 1, -sx * dy, -sy * dy]); b.append(dy)
    v = np.linalg.solve(np.asarray(A, float), np.asarray(b, float))
    return np.append(v, 1.0).reshape(3, 3)


def order_corners(pts):
    pts = np.asarray(pts, float)
    s, d = pts[:, 0] + pts[:, 1], pts[:, 0] - pts[:, 1]
    return [tuple(pts[np.argmin(s)]), tuple(pts[np.argmax(d)]),
            tuple(pts[np.argmax(s)]), tuple(pts[np.argmin(d)])]  # TL TR BR BL


def sample_bilinear(img, u, v):
    h, w = img.shape[:2]
    u = np.clip(u, 0, w - 1.001); v = np.clip(v, 0, h - 1.001)
    x0 = np.floor(u).astype(int); y0 = np.floor(v).astype(int)
    fx = (u - x0)[..., None] if img.ndim == 3 else (u - x0)
    fy = (v - y0)[..., None] if img.ndim == 3 else (v - y0)
    a = img[y0, x0]; b = img[y0, x0 + 1]
    c = img[y0 + 1, x0]; d = img[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


# ---------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--init", required=True)
    ap.add_argument("--init-sha256", required=True)
    ap.add_argument("--quad", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260815)
    ap.add_argument("--relief", type=float, default=3.4,
                    help="normal-map slope gain; higher = deeper-looking crust")
    ap.add_argument("--target-lum", type=float, default=78.0)
    ap.add_argument("--target-std", type=float, default=26.0)
    ap.add_argument("--rim", type=int, default=2, help="px of plate edge kept as cel outline")
    ap.add_argument("--tex", type=int, default=768, help="bark texture resolution")
    ap.add_argument("--ss", type=int, default=3, help="supersampling for the map")
    ap.add_argument("--noise-scale", type=float, default=1.0,
                    help="scales every noise grid. beat 06's board is ~190x215px "
                         "against beat 10's much larger slab, so beat 10's grid "
                         "gave fine combed streaks -- corduroy, not bark. <1 makes "
                         "fewer, wider plates at the same on-screen scale.")
    ap.add_argument("--face-rmg-min", type=float, default=16.0,
                    help="board face: R-G at least this (this plate: +20..+31)")
    ap.add_argument("--face-bmg-max", type=float, default=-8.0,
                    help="board face: B-G at most this (this plate: -11..-15)")
    ap.add_argument("--face-lmin", type=float, default=60.0)
    ap.add_argument("--face-lmax", type=float, default=100.0)
    ap.add_argument("--top-band", type=float, default=34.0,
                    help="px measured along the board's own top normal, filled "
                         "unconditionally so the protruding clip is inside the mask")
    ap.add_argument("--occl-rmg", type=float, default=12.0,
                    help="occluder if R-G below this (hand -26..-2, board +20..+31)")
    ap.add_argument("--occl-lmin", type=float, default=55.0)
    ap.add_argument("--clip-box", default="",
                    help="x0,y0,x1,y1 search box for the chrome clip (measured)")
    ap.add_argument("--clip-rmg", type=float, default=18.0,
                    help="R-G below this inside --clip-box is chrome, not cloak")
    ap.add_argument("--corner-round", type=int, default=2,
                    help="px radius that rounds the quad's convex corners")
    ap.add_argument("--bright", type=float, default=125.0,
                    help="L above this inside the quad is hand/sash, not board")
    ap.add_argument("--rim-rmg", type=float, default=35.0,
                    help="R-G at or above this is the board's own reddish rim, "
                         "never an occluder, however bright it gets")
    ap.add_argument("--flat-top-y", type=int, default=501,
                    help="rows above this inside the quad are unconditionally "
                         "board: nothing occludes the board's top edge, so the "
                         "strip that swallows the protruding clip is safe to fill")
    ap.add_argument("--debug-dir", default="")
    a = ap.parse_args()

    have = sha256_of(a.init)
    if have != a.init_sha256:
        print("!! INIT SHA MISMATCH -- refusing.\n   want %s\n   have %s"
              % (a.init_sha256, have), flush=True)
        return 3
    print("init_sha256 OK %s" % have, flush=True)

    vals = [int(v) for v in a.quad.split(",")]
    if len(vals) != 8:
        print("!! --quad wants 8 integers", flush=True)
        return 2
    quad = list(zip(vals[0::2], vals[1::2]))

    im = Image.open(a.init).convert("RGB")
    W, H = im.size
    arr = np.asarray(im).astype(np.float64)
    L = lum_of(arr)

    qm = Image.new("L", (W, H), 0)
    ImageDraw.Draw(qm).polygon(quad, fill=255)
    Q = np.asarray(qm) > 127

    # round the quad's convex corners: opening with a disk leaves the straight
    # edges where they are and shaves each corner by --corner-round px, which is
    # this clipboard's own corner radius. A hard corner would put a wedge of
    # brown cloak inside the fill.
    if a.corner_round > 0:
        r = a.corner_round
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        disk = (xx * xx + yy * yy) <= r * r + 0.5
        Qr = ndimage.binary_opening(Q, disk)
    else:
        Qr = Q.copy()
    print("quad %d px -> corner-rounded r=%d %d px"
          % (int(Q.sum()), a.corner_round, int(Qr.sum())), flush=True)

    # --- 2. segment the board out of the plate ------------------------------
    # TIGHT-SHOT rule, measured off THIS plate (scanlines; see module docstring):
    #   face        (91..110, 69..79, 58..64)  R-G +20..+31  B-G -11..-15  L 75..87
    #   teal robe   (58,115,90)/(21,60,56)     R-G -57/-39   B-G -25/-4    L 95/48
    #   green hand  (165,191,107)/(122,124,81) R-G -26/-2    B-G -84/-43   L 174/118
    #   guard cloak (105,78,74)/(110,92,88)    R-G +27/+18   B-G  -4       L 86/97
    #   chrome clip (107,126,140)/(117,124,131) R-G -19/-7                 L 122/123
    # B-G is NOT the discriminant here -- this face is -11..-15, i.e. the sign
    # beat 08 r3-s0 used to REJECT with (+4..+6). R-G is: the board is the only
    # warm thing in the quad. The guard's cloak is warm too and is the one term
    # B-G still has to fence (-4 against the board's -11..-15).
    BmG = arr[..., 2] - arr[..., 1]
    RmG = arr[..., 0] - arr[..., 1]
    face = ((RmG >= a.face_rmg_min) & (BmG <= a.face_bmg_max)
            & (L > a.face_lmin) & (L < a.face_lmax) & Qr)
    face = ndimage.binary_closing(face, np.ones((3, 3)))
    face = ndimage.binary_opening(face, np.ones((3, 3)))
    lab, n = ndimage.label(face)
    if n == 0:
        print("!! no board face found", flush=True)
        return 4
    sizes = ndimage.sum(face, lab, range(1, n + 1))
    # EVERY component above 200px, not just the largest: fingertip notches can
    # cut the visible face into pieces even when no palm crosses it.
    keepids = [i + 1 for i, sz in enumerate(sizes) if sz >= 200]
    face = np.isin(lab, keepids)
    print("face components: %d total, %d kept (>=200px), %d px"
          % (n, len(keepids), int(face.sum())), flush=True)
    face = ndimage.binary_fill_holes(face)

    # THE CHROME CLIP NEEDS NO DETECTOR OF ITS OWN HERE, and that is a real
    # simplification rather than a dropped step. On beat 08 r3-s0 the clip
    # protruded above a FLAT top edge, so a horizontal `flat_top_y` strip could
    # reach the part above the line but the part below it had to be found by
    # colour. This board is rotated ~12 degrees, so a horizontal cut takes a
    # wedge of robe on one side and misses the clip on the other. Instead the
    # quad handed in is already RAISED above the clip, and the band along the
    # board's own top edge -- measured along the top NORMAL, not down the y
    # axis -- is filled unconditionally to a depth that reaches past the clip's
    # lower boundary. The clip is then inside the mask by construction, which is
    # stronger than a colour rule: there is no threshold left to get wrong.
    clipm = np.zeros((H, W), bool)

    # occluders subtracted back out. ONLY brightness: inside the quad the board
    # is the darkest thing there is, and the rim cannot be told from the cloak
    # by any colour rule (they overlap on R-G, G-B and L), so the cloak is
    # fenced by the quad instead. L > 125 separates hands (170..215) and sash
    # (133..227) from the rim (<= 131). Dilated by 2 so the drawn black outlines
    # around the fingers go with the fingers.
    # c1 FAILED by eye before any GPU ran: `L > 125` alone deleted the board's
    # own rim, whose lit top band reaches L 131, so the bark stopped ~11px inside
    # the board's top edge and left a brown clipboard frame standing around it --
    # the decal tell "a swatch stopping short of the object's own edge",
    # introduced by the compositor. Brightness alone cannot do this job. R-G can:
    # the rim is 42..64, every occluder is below 35 (fingers 21..27, tunic 24,
    # sash -15..0, clip -9..+5). So a pixel is an occluder only if it is bright
    # AND not rim-hued.
    # THE OCCLUDER RULE IS HUE, NOT BRIGHTNESS, and the swap is forced by the
    # plate. beat 08 r3-s0's occluders were pale human hands and a white sash
    # against a dark maroon board, so `L > 125` separated them. The hand lying
    # across THIS board is the GOBLIN'S GREEN hand: its lit half is L 174 but
    # its shaded half is L 118, BELOW that threshold, so brightness alone would
    # composite bark over half a hand. R-G separates them with no overlap at
    # all -- board +20..+31, hand -26..-2, robe -39..-57 -- so an occluder is
    # R-G < occl_rmg AND L > occl_lmin, the second term only so that the drawn
    # black outlines (L < 40) are not themselves called occluders and left as
    # holes in the middle of the bark.
    bright = (RmG < a.occl_rmg) & (L > a.occl_lmin)
    # ONE dilation, not two. c2 measured the bark boundary against the traced
    # edge row by row: two iterations pulled the LEFT edge 2.4..3.3px inside the
    # board wherever the bright cuff lies against it, which is the "stops short"
    # tell again. One keeps the finger outlines covered and tracks the traced
    # edge to within ~1px.
    excl = ndimage.binary_dilation(bright, np.ones((3, 3)), iterations=1)
    # the top strip. c1 also FAILED on shape: with the quad stopping at the
    # board's own top line, covering the protruding clip left a clip-shaped TAB
    # on an otherwise straight top edge -- not a four-sided slab. The quad now
    # runs 9px higher, straight across, so the slab is 9px taller with a straight
    # top and no tab. Nothing occludes the board there (both hands start 25px
    # lower; above the line are cloak, the tunic V, a cloak stud and the clip),
    # so that strip is filled unconditionally -- otherwise the bright tunic V
    # would cut a notch out of the new top edge.
    # THE TOP BAND, measured along the board's own top normal. `flat_top_y` was
    # a horizontal line because beat 08 r3-s0's board had a flat top edge. This
    # board is rotated ~12 degrees clockwise, so a horizontal cut would slice a
    # wedge -- deep on the left, shallow on the right -- which is exactly the
    # "swatch overrunning the object's own edge" decal tell on one side and a
    # clip-shaped tab left standing on the other. The band is therefore defined
    # by SIGNED DISTANCE from the quad's own top edge: every pixel of the quad
    # within --top-band px of that edge, on its inner side, is filled
    # unconditionally. Inside it are the clip, the raise strip and a sliver of
    # the goblin's teal robe; nothing that must be preserved is in there (the
    # hand starts 40+px lower).
    (tlx, tly), (trx, try_) = quad[0], quad[1]
    ex, ey = trx - tlx, try_ - tly
    en = max((ex * ex + ey * ey) ** 0.5, 1e-6)
    # inward normal of the top edge (quad is TL,TR,BR,BL clockwise in image
    # coords, so the inward normal is the edge direction rotated +90 degrees)
    nx, ny = -ey / en, ex / en
    if nx * (quad[3][0] - tlx) + ny * (quad[3][1] - tly) < 0:
        nx, ny = -nx, -ny
    YYg, XXg = np.mgrid[0:H, 0:W]
    dist_from_top = (XXg - tlx) * nx + (YYg - tly) * ny
    topstrip = Qr & (dist_from_top < a.top_band)
    keep = (Qr & ~excl) | face | topstrip
    keep = ndimage.binary_fill_holes(keep)
    keep = ndimage.binary_opening(keep, np.ones((3, 3)))
    keep = ndimage.binary_fill_holes(keep)
    lab2, n2_ = ndimage.label(keep)
    if n2_:
        sz = ndimage.sum(keep, lab2, range(1, n2_ + 1))
        keep = np.isin(lab2, [i + 1 for i, v in enumerate(sz) if v >= 200])
    print("rounded quad - occluder(R-G<%.0f & L>%.0f) | face | topband(<%.0fpx "
          "along the top normal, %d px) -> %d px"
          % (a.occl_rmg, a.occl_lmin, a.top_band, int(topstrip.sum()),
             int(keep.sum())), flush=True)
    board = keep
    px = int(board.sum())
    print("board segment: %d px (%.1f%% of quad %d px)"
          % (px, 100.0 * px / max(Q.sum(), 1), int(Q.sum())), flush=True)

    ys, xs = np.nonzero(board)
    # beat 08: the segment's extreme pixels are the CLIP's (it protrudes above
    # the board) and the fingertip notches', not the board's corners. The quad
    # is the board -- each edge fitted to scanline measurements on unoccluded
    # rows/columns -- so board space is fitted to the quad.
    corners = order_corners(np.asarray(quad, float))
    print("board corners TL/TR/BR/BL: %s"
          % [(round(x, 1), round(y, 1)) for x, y in corners], flush=True)

    # --- 3. light direction MEASURED from the plate's own board -------------
    Lsm = ndimage.gaussian_filter(L, 18.0)
    gy, gx = np.gradient(Lsm)
    lx = float(gx[board].mean()); ly = float(gy[board].mean())
    nrm = max((lx * lx + ly * ly) ** 0.5, 1e-6)
    lx, ly = lx / nrm, ly / nrm
    print("measured key light (frame space, toward brighter): dx=%+.3f dy=%+.3f"
          % (lx, ly), flush=True)

    # --- 1. procedural bark -------------------------------------------------
    T = a.tex
    hgt, mottle, furrow = bark_height(T, T, a.seed, a.noise_scale)

    # light into BOARD space through the homography Jacobian at the centre
    Hm = homography([(0, 0), (1, 0), (1, 1), (0, 1)], corners)
    c = np.array([0.5, 0.5, 1.0])
    p = Hm @ c
    J = np.zeros((2, 2))
    for i in range(2):
        e = np.zeros(3); e[i] = 1e-3
        pp = Hm @ (c + e)
        J[:, i] = (pp[:2] / pp[2] - p[:2] / p[2]) / 1e-3
    ld = np.linalg.solve(J, np.array([lx, ly]))
    ld /= max(np.linalg.norm(ld), 1e-6)
    print("light in board space: dx=%+.3f dy=%+.3f" % (ld[0], ld[1]), flush=True)

    hy, hx = np.gradient(ndimage.gaussian_filter(hgt, 1.2))
    nx, ny, nz = -hx * a.relief * T / 100.0, -hy * a.relief * T / 100.0, 1.0
    nl = np.sqrt(nx * nx + ny * ny + nz * nz)
    Lv = np.array([ld[0], ld[1], 0.62]); Lv /= np.linalg.norm(Lv)
    shade = (nx * Lv[0] + ny * Lv[1] + nz * Lv[2]) / nl
    shade = np.clip(shade, 0.0, 1.0) ** 0.85
    shade = 0.30 + 0.70 * shade
    # grooves also self-occlude
    shade *= 0.44 + 0.56 * furrow

    c_low = np.array([44.0, 33.0, 26.0])
    c_high = np.array([172.0, 149.0, 118.0])
    t = np.clip(0.55 * hgt + 0.45 * mottle, 0.0, 1.0)[..., None]
    albedo = c_low + (c_high - c_low) * t
    tex = albedo * shade[..., None]

    # --- map board space -> frame, supersampled ----------------------------
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    Hi = np.linalg.inv(Hm)
    ss = a.ss
    acc = np.zeros((y1 - y0, x1 - x0, 3))
    off = (np.arange(ss) + 0.5) / ss - 0.5
    for oy in off:
        for ox in off:
            YY, XX = np.mgrid[y0:y1, x0:x1]
            XXf = XX + ox; YYf = YY + oy
            den = Hi[2, 0] * XXf + Hi[2, 1] * YYf + Hi[2, 2]
            u = (Hi[0, 0] * XXf + Hi[0, 1] * YYf + Hi[0, 2]) / den
            v = (Hi[1, 0] * XXf + Hi[1, 1] * YYf + Hi[1, 2]) / den
            acc += sample_bilinear(tex, u * (T - 1), v * (T - 1))
    acc /= ss * ss

    # --- 3b. re-apply the plate's own low-frequency shading -----------------
    field = ndimage.gaussian_filter(L, 14.0)[y0:y1, x0:x1]
    bsub = board[y0:y1, x0:x1]
    field = field / max(field[bsub].mean(), 1e-6)
    field = np.clip(field ** 0.60, 0.55, 1.60)
    acc *= field[..., None]

    # --- value match --------------------------------------------------------
    # UNCHANGED FROM THE INHERITED LANE, AND IT STAYS UNCHANGED BECAUSE I TRIED
    # TO CHANGE IT AND WAS WRONG. Written down rather than quietly reverted.
    # c1 was opened and read to me as grey weathered slate rather than warm
    # crust, and a measurement inside the board QUAD agreed: R-G +0.4 against
    # beat 06's passing composite at +17.0. I concluded the affine below
    # desaturates -- it scales the channel differences by target_std/s along
    # with the luminance spread -- and rebuilt as c2 with the affine applied to
    # LUMINANCE ONLY and the chroma carried through untouched.
    # THE MEASUREMENT WAS CONTAMINATED AND THE CONCLUSION WAS WRONG. The quad
    # contains the goblin's GREEN hand, which the mask correctly excludes and
    # which sits at R-G -26..-2; beat 06's quad contains a PALE HUMAN hand,
    # which sits R-G positive. So the same statistic was being pulled down on
    # one board and up on the other, and none of the difference was the bark.
    # Measured again on THE PIXELS THE COMPOSITOR ACTUALLY CHANGED, eroded 3px
    # so the rim is out, which is the only region the comparison is about:
    #     beat 06 composite, PASSED        R-G +12.3  sat 26.2  L 76.3+-25.5
    #     beat 08 r3-s0 composite, FAILED  R-G +12.1  sat 25.9  L 80.5+-24.5
    #     c1, inherited affine             R-G +11.0  sat 23.5  L 77.6+-26.0
    #     c2, my "fix"                     R-G  +8.6  sat 18.4  L 77.1+-25.5
    # c1 already matched both references to within a point and c2 moved AWAY
    # from them. So the inherited line is restored exactly, --chroma-gain is
    # gone, and the composite this lane fires is c1's recipe. The bark is not
    # grey; the plate around it is TEAL, and a warm board against teal reads
    # cooler than the same board against beat 06's tan tunic. That is a fact
    # about the plate, not a defect in the composite, and the sampler sees the
    # numbers rather than my impression of them.
    al = lum_of(acc)
    m, s = al[bsub].mean(), al[bsub].std()
    acc = (acc - m) * (a.target_std / max(s, 1e-6)) + a.target_lum
    acc = np.clip(acc, 0, 255)
    al2 = lum_of(acc)
    print("bark patch luminance: mean %.1f std %.1f (plate board was mean %.1f std %.1f)"
          % (al2[bsub].mean(), al2[bsub].std(), L[board].mean(), L[board].std()), flush=True)

    # --- rim: keep a drawn cel outline in bark hue --------------------------
    inner = ndimage.binary_erosion(board, np.ones((3, 3)), iterations=max(a.rim, 0))
    full = np.zeros((H, W, 3)); full[y0:y1, x0:x1] = acc
    rimband = board & ~inner
    out = arr.copy()
    alpha = ndimage.gaussian_filter(board.astype(np.float64), 0.7)[..., None]
    paint = np.where(rimband[..., None], full * 0.30, full)
    out = out * (1 - alpha) + paint * alpha
    out = np.clip(out, 0, 255)

    outimg = Image.fromarray(out.astype(np.uint8))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    outimg.save(a.out)
    print("wrote %s  sha256 %s" % (a.out, sha256_of(a.out)), flush=True)

    # control: nothing outside the board segment may move
    diff = np.abs(out - arr).max(axis=2)
    print("maxdiff outside board segment: %.0f" % diff[~ndimage.binary_dilation(
        board, np.ones((3, 3)), iterations=2)].max(), flush=True)

    if a.debug_dir:
        d = a.debug_dir
        os.makedirs(d, exist_ok=True)
        seg = arr.copy(); seg[board] = seg[board] * 0.4 + np.array([255, 0, 0]) * 0.6
        pad = 40
        bx = (max(x0 - pad, 0), max(y0 - pad, 0), min(x1 + pad, W), min(y1 + pad, H))
        for name, img in (("seg", seg), ("composite", out)):
            Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).crop(bx).resize(
                ((bx[2] - bx[0]) * 3, (bx[3] - bx[1]) * 3), Image.LANCZOS
            ).save(os.path.join(d, "dbg-%s-3x.png" % name))
        Image.fromarray(np.clip(tex, 0, 255).astype(np.uint8)).save(
            os.path.join(d, "dbg-barktex.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
