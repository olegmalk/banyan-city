#!/usr/bin/env python3
r"""BEAT 06 copy. Composite procedural bark relief INTO a plate's board region.
$0, no sampler.

LANE-SCOPED ON PURPOSE (shared worktree). Adapted from lab/inpaint-b10/
bark_composite.py sha 38f4bbb6 (the version that produced beat 10's passing
s13). The noise, homography, measured-light and value-match machinery is
UNCHANGED. Only the segmentation is re-tuned, because beat 06's plate is a
different object:

  * THE QUAD. Beat 10's inherited quad was NOT its board (overshot ~10px on
    every side, ran into a hand). Beat 06's inherited quad b4c0594f was checked
    the same way at 8x on all four edges and is much closer -- but its top edge
    cuts THROUGH the chrome clip band near the left end, which would leave a
    sliver of chrome outside the mask where the sampler can never touch it, and
    the bar says no chrome clip. So beat 06 gets its own quad, 3px up at the top
    and out at the corners, measured off the plate.
  * THE COLOUR RULE. Beat 10's navy face was B-R >= 10 and L < 110. Beat 06's
    board is much darker and much less blue: face RGB ~ (45,45,51), B-R only +3
    to +17. The discriminant that actually separates it from its neighbours is
    B-G: the dark GREEN sash directly below and right of the board has B-G ~ -8
    while the board face has B-G +2..+12, and the brown coat and the cuff have
    B-R <= -20. So: B-G >= 2 and B-R >= -2 and L < 62.
  * THE HULL IS TAKEN OVER EVERY FACE COMPONENT, not the largest. The near hand
    lies ACROSS beat 06's face and cuts the visible navy into disjoint pieces;
    keeping only the largest would drop the lower-right of the board and leave
    navy showing.
  * THE CHROME CLIP IS FILLED BY GEOMETRY, NOT BY fill_holes. On beat 10 the
    clip was interior to the board and fill_holes swallowed it. Beat 06's clip
    is a band ON the board's top edge, so it touches the border and no hole
    filling can reach it. Instead, for each column the rows between the quad's
    top edge and the first face pixel are filled, but only where that gap is
    small (<= --clip-gap px) -- which is true along the clip and false under the
    gripping hand at the top right, whose first face pixel is 150px down.

WHY THIS EXISTS. Eleven single samples on beat 10 (see 419ddf00) established the
mechanism: bark crust is high-frequency relief and the board's straight
silhouette is carried in the SAME frequency band, so every noise level high
enough to make the model WRITE crust also rewrites the outline, and every level
low enough to keep the outline leaves the init's smooth navy face untouched. The
two thresholds coincide in sigma. Strength, step count, a second repair pass,
the seed and value-matched material wording were each ruled out by an opened
sample.

So stop asking the model to INVENT relief. Put the relief in the init with plain
image processing -- no diffusion, no GPU, no cost -- and then run the LOW-strength
pass, the regime already proven to preserve a rectangle perfectly. The model is
then only asked to harmonise a texture that is already there.

THREE CHOICES, EACH MADE ON EVIDENCE FROM THE PLATE ITSELF:

  1. THE TEXTURE IS PROCEDURAL, NOT A PHOTO. A bark photograph would import a
     licence and a provenance question into a repo whose rule is provenance
     always, and photoreal crust dropped into a cel-shaded anime frame is the
     decal failure mode by construction. This generates bark from seeded value
     noise: anisotropic fbm stretched ~5:1 vertically gives long vertical
     plates separated by narrow fissures, a second octave cuts sub-fissures, a
     fine isotropic octave is the flaking crust, and a low-frequency octave
     mottles the albedo. Deterministic from --seed.

  2. IT IS FITTED TO THE SEGMENTED BOARD, NOT TO THE MASK QUAD. Overlaying the
     quad on the plate shows it is NOT the board: it overshoots ~17px right at
     the top into the second guard's hand and the coat, and a few px left at the
     bottom into the near hand. Filling the quad would paint bark over fingers
     and leave the board's own edge somewhere else entirely -- a decal by
     definition. So the board is segmented out of the plate by colour (the navy
     face is B-R >= 10 and dark, unlike the brown coat and the pink hands),
     holes are filled so the chrome clip is covered too, and the bark is mapped
     onto a homography fitted to THAT silhouette. The bark edge and the board
     edge then coincide because they are the same edge.

  3. THE PLATE'S OWN LIGHT IS KEPT. The bark's relief shading uses a light
     direction MEASURED from the low-pass luminance gradient of the plate's own
     board, transformed into board space through the homography's Jacobian, so
     the ridges catch light from where this frame's key light actually is. The
     plate's low-frequency shading field is then re-applied multiplicatively, so
     the top-edge rim stays bright and the bottom-left stays in shade exactly as
     the founder's pixels had it. A flat sticker has none of that, which is what
     makes it read as one.

  Plus: the bark is inset 2px and the surviving rim is painted as a dark bark-hued
  cel outline, so the board keeps a drawn edge in the plate's own dialect instead
  of a texture running off a cliff.

The mask handed to the sampler afterwards is UNCHANGED (the same quad, sha
3aef49b2...). This script only changes what the sampler starts FROM.

    python bark_composite.py --init PLATE.png --init-sha256 <hex> \
        --quad x0,y0,x1,y1,x2,y2,x3,y3 --out COMPOSITE.png [--seed N] \
        [--relief F] [--target-lum F] [--target-std F] [--debug-dir DIR]
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
    ap.add_argument("--clip-gap", type=int, default=34,
                    help="max px between quad top edge and first face pixel that "
                         "still counts as the chrome clip band")
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

    # --- 2. segment the board out of the plate ------------------------------
    # beat 06 rule, measured off this plate (see the module docstring):
    #   face  (45,45,51) .. (44,51,61)  B-R -1..+17  B-G +2..+12  L 45..52
    #     -- v2 used B-R >= 1 and it FAILED by eye: the board's RIGHT half is
    #     warmer (B-R -1..+1 at x=200), so 60px of face under the chrome clip
    #     were not seen, the clip-band gap there measured 60px instead of 26,
    #     and the right half of the chrome clip stayed standing in the composite.
    #     B-G is the discriminant that actually works; B-R only has to fence the
    #     brown coat (-21..-49) and the cuff (-20), so >= -2 is enough.
    #   sash  (35,50,42)               B-G -8       -> excluded by B-G
    #   coat  (61,45,40)/(158,134,111) B-R -21/-47  -> excluded by B-R
    #   cuff  (36,17,16)/(33,34,35)    B-R -20 / B-G +1 -> excluded
    #   hands (172,138,121)            L 146        -> excluded by L
    BmR = arr[..., 2] - arr[..., 0]
    BmG = arr[..., 2] - arr[..., 1]
    RmB = arr[..., 0] - arr[..., 2]
    face = (BmG >= 2) & (BmR >= -2) & (L < 62) & Q
    face = ndimage.binary_closing(face, np.ones((3, 3)))
    face = ndimage.binary_opening(face, np.ones((3, 3)))
    lab, n = ndimage.label(face)
    if n == 0:
        print("!! no board face found", flush=True)
        return 4
    sizes = ndimage.sum(face, lab, range(1, n + 1))
    # EVERY component above 200px, not just the largest: the near hand lies
    # across this face and splits it.
    keepids = [i + 1 for i, sz in enumerate(sizes) if sz >= 200]
    face = np.isin(lab, keepids)
    print("face components: %d total, %d kept (>=200px), %d px"
          % (n, len(keepids), int(face.sum())), flush=True)
    face = ndimage.binary_fill_holes(face)

    # convex hull over the whole face to recover the board's straight edges
    from scipy.spatial import ConvexHull
    yb, xb = np.nonzero(face)
    hull = ConvexHull(np.stack([xb, yb], 1))
    hp = [tuple(map(float, hull.points[i])) for i in hull.vertices]
    him = Image.new("L", (W, H), 0)
    ImageDraw.Draw(him).polygon(hp, fill=255)
    hullm = (np.asarray(him) > 127) & Q

    # the chrome clip band: per column, quad-top .. first face pixel, but only
    # where that gap is small. fill_holes cannot reach it -- it touches the
    # board's own border.
    clipband = np.zeros((H, W), bool)
    Qcols = Q.any(axis=0)
    for x in np.nonzero(Qcols)[0]:
        qrows = np.nonzero(Q[:, x])[0]
        frows = np.nonzero(face[:, x])[0]
        if frows.size == 0:
            continue
        qt, ft = int(qrows[0]), int(frows[0])
        if 0 <= ft - qt <= a.clip_gap:
            clipband[qt:ft, x] = True
    print("clip band: %d px (max gap %d)" % (int(clipband.sum()), a.clip_gap), flush=True)

    # occluders subtracted back out: the two hands (skin), the white cuff
    # stripes and any bright coat, the dark green sash, the brown coat.
    skin = (RmB > 15) & (L > 80)
    bright = L > 120
    sash = (BmG <= 0) & (L < 95)
    coat = (RmB > 8) & ~skin
    excl = ndimage.binary_dilation(skin | bright | sash | coat, np.ones((3, 3)))
    # v1 used beat 10's `hull & ~excl` and it FAILED by eye before any GPU ran:
    # the hull is the hull of the VISIBLE face, and beat 06's board has a dark
    # rim its colour rule does not catch, so the bark stopped ~12px inside the
    # board's own left edge and chamfered the top-right corner -- the decal tell
    # "a swatch stopping short of the object's own edge", introduced by the
    # compositor itself. The quad IS the board here, so the quad is the base.
    # And the clip band is unioned back in AFTER the exclusion, because the clip
    # is bright and `bright` would otherwise delete the very thing the bar wants
    # covered (v1 left the whole chrome clip standing).
    keep = ((Q & ~excl) | face | (clipband & Q))
    keep = ndimage.binary_fill_holes(keep)
    keep = ndimage.binary_opening(keep, np.ones((3, 3)))
    keep = ndimage.binary_fill_holes(keep)
    lab2, n2_ = ndimage.label(keep)
    if n2_:
        sz = ndimage.sum(keep, lab2, range(1, n2_ + 1))
        keep = np.isin(lab2, [i + 1 for i, v in enumerate(sz) if v >= 200])
    print("quad %d px (hull of visible face %d px) | + clip band, "
          "- hands/cuff/sash/coat -> %d px"
          % (int(Q.sum()), int(hullm.sum()), int(keep.sum())), flush=True)
    board = keep
    px = int(board.sum())
    print("board segment: %d px (%.1f%% of quad %d px)"
          % (px, 100.0 * px / max(Q.sum(), 1), int(Q.sum())), flush=True)

    ys, xs = np.nonzero(board)
    # beat 06: the segment is carved by TWO hands and a cuff, so its extreme
    # pixels are not the board's corners (beat 10 could use them because its
    # occluder only clipped one corner). The quad IS the board here -- authored
    # off the plate and verified at 8x on all four edges -- so board space is
    # fitted to the quad.
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
