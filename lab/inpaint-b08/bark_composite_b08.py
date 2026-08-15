#!/usr/bin/env python3
r"""BEAT 08 copy. Composite procedural bark relief INTO a plate's board region.
$0, no sampler.

LANE-SCOPED ON PURPOSE (shared worktree). Adapted from lab/inpaint-b06/
bark_composite_b06.py, itself adapted from lab/inpaint-b10/bark_composite.py.
The noise, homography, measured-light and value-match machinery is UNCHANGED.
Only the segmentation is re-derived, because beat 08's plate is a third
different object -- an 832x1216 two-figure plate, board held flat to camera at
chest height, both hands gripping the SIDE EDGES so only fingertips notch the
rim. Everything below was measured off that plate with scanlines, not guessed:

  * THE QUAD IS MEASURED, NOT INHERITED. Nothing upstream carries a beat 08
    board quad. Every edge was traced by scanning outward from the segmented
    face to the drawn outline, on rows/columns where no hand occludes it, and
    the four edges fitted as lines:
        left   x = 596.5 - 0.271*(y-503)   (y=503->597, 600->572, 658->555)
        right  x = 767.0 - 0.358*(y-505)   (y=505->767, 600->732, 656->713)
        top    y = 500 flat                (x=600->501, 640->501, 740->501)
        bottom y = 659 flat                (x=560..710 all 659/660)
    giving the board TL(598,500) TR(768,500) BR(712,659) BL(555,659), biased 1px
    INWARD on the two side edges: 170px across the top, 157 across the bottom,
    159 tall -- a left-sheared trapezoid, not a rectangle in frame space. The
    quad actually USED runs 9px higher (600,491 / 771,491) for the reason in the
    clip bullet below.
  * THE CORNERS ARE ROUNDED. This clipboard's frame has ~4px rounded corners.
    A hard quad corner puts a small triangle of brown cloak inside the fill,
    which is the decal tell "a swatch overrunning the object's own edge". The
    quad is opened with a disk of --corner-round px, which rounds convex
    corners and leaves the straight edges untouched.
  * THE COLOUR RULE. Beat 10's navy face was B-R >= 10, L < 110. Beat 06's
    near-black board needed B-G >= 2, B-R >= -2, L < 62. Beat 08's face is dark
    MAROON, RGB ~ (52..59, 37..43, 42..47): B-R is NEGATIVE (-10 to -12), so
    beat 06's B-R fence would reject the whole board. What survives is B-G,
    which is +4..+6 on the face and strongly negative on every neighbour: brown
    cloak (139,102,73) B-G -29, the board's own reddish rim (144,93,79) B-G -14,
    tan tunic (231,209,177) B-G -32, hands (187,166,140) B-G -26. So the rule is
    B-G >= 3 and L < 62. It yields ONE face component of 17997 px, bbox 193x147.
  * THE RIM CANNOT BE SEGMENTED BY COLOUR AND IS NOT ASKED TO BE. The board's
    reddish frame (144,93,79)/(117,68,54)/(157,93,74) and the brown cloak behind
    it (139,102,73)/(141,103,74)/(130,93,70) are the same colour to within noise
    -- R-G 45..64 vs 37..45, L 81..110 vs 101..111, overlapping on both. Beat
    06's `coat` exclusion (R-B > 8) would delete this board's whole rim and stop
    the bark ~8px inside its own edge. So the cloak is fenced by GEOMETRY (the
    measured quad) and the only colour exclusion inside the quad is brightness,
    brightness -- and brightness ALONE is not enough either. Composite c1 was
    rejected by eye at zero GPU cost because `L > 125` ate the rim, whose lit top
    band reaches L 131, leaving a brown clipboard frame standing around the bark:
    the tell "a swatch stopping short of the object's own edge", introduced by
    the compositor. R-G is what separates them -- rim 42..64, every occluder
    below 35 (fingers 21..27, tunic 24, sash -15..0, clip -9..+5) -- so a pixel
    is an occluder only if it is BOTH bright and not rim-hued. c2 then measured
    the resulting boundary against the traced edge row by row and found the
    2-iteration dilation pulling the left edge 2.4..3.3px inside the board
    wherever the bright cuff lies against it; at one iteration the bark tracks
    the traced edge to within 1.8px on every edge.
  * THE CHROME CLIP PROTRUDES ABOVE THE BOARD, so no quad that stops at the
    board's own top edge can reach it and no fill_holes can either. It is found
    by colour in a measured box: R-G < 18 separates the clip's greys
    (240,236,212) R-G 4, (193,202,202) -9, (35,30,22) 5 from the cloak (38) and
    the tunic (24). Measured extent y 492..513, x 648..719 -- 8px above the
    board's top line. It is unioned back in AFTER the bright subtraction,
    because the clip is bright and would otherwise be deleted by the very rule
    that protects the hands (beat 06 v1 left its whole clip standing that way).
    But covering it is not enough: c1 covered the clip with the quad stopping at
    the board's own top line and the result was a slab with a clip-shaped TAB on
    its top edge -- not a four-sided shape, FAIL-SHAPE introduced by the
    compositor. So the quad runs 9px higher, straight across, and every quad
    pixel above --flat-top-y is filled unconditionally: the slab is 9px taller
    with ONE straight top edge and no tab. That strip is safe to fill blind
    because nothing occludes the board there -- both hands start 25px lower, and
    above the line are only cloak, the tunic V, a cloak stud and the clip itself.
    Without the unconditional fill the bright tunic V would cut a notch in the
    new top edge.

  * NOISE SCALE 0.85, chosen by building five composites and opening them. Beat
    10 used 1.0 on a much larger slab, beat 06 0.62 on a 254px-wide one. Scaling
    by width would have said ~0.42 for this 170px board and that is WRONG by eye:
    0.52 and 0.70 read as soft smoke and marble, 1.20 combs into corduroy, 0.85
    is the one with irregular fissures of varying weight and pale ridges between.

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
    ap.add_argument("--clip-box", default="644,492,720,514",
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
    # beat 08 rule, measured off THIS plate (scanlines; see module docstring):
    #   face   (52..59, 37..43, 42..47)   B-G +4..+6   L 42..48
    #   rim    (144,93,79)/(117,68,54)    B-G -14..-17 L 81..110
    #   cloak  (139,102,73)               B-G -29      L 110
    #   tunic  (231,209,177)              B-G -32      L 212
    #   hands  (187,166,140)              B-G -26      L 169
    #   sash   (119,134,165)/(226,226,234) B-G +31/+8  L 133/227 -> fenced by L
    #   clip   (193,202,202)/(35,30,22)   R-G -9/+5    -> its own detector
    # B-R is NOT usable here: this face is maroon, B-R -10..-12, i.e. the sign
    # beat 06 used to REJECT with. B-G is the whole discriminant.
    BmG = arr[..., 2] - arr[..., 1]
    RmG = arr[..., 0] - arr[..., 1]
    face = (BmG >= 3) & (L < 62) & Qr
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

    # the chrome clip. It PROTRUDES above the board's top edge, so it is outside
    # any quad that is the board, and fill_holes cannot reach it either. Found
    # by colour in a measured box: R-G < clip_rmg is chrome, not cloak/tunic.
    cx0, cy0, cx1, cy1 = [int(v) for v in a.clip_box.split(",")]
    cbox = np.zeros((H, W), bool)
    cbox[cy0:cy1, cx0:cx1] = True
    clipm = cbox & (RmG < a.clip_rmg)
    clipm = ndimage.binary_closing(clipm, np.ones((5, 5)))
    lc, nc = ndimage.label(clipm)
    if nc:
        szc = ndimage.sum(clipm, lc, range(1, nc + 1))
        clipm = lc == (int(np.argmax(szc)) + 1)
    clipm = ndimage.binary_fill_holes(clipm)
    if clipm.any():
        cys, cxs = np.nonzero(clipm)
        print("chrome clip: %d px, bbox x %d..%d y %d..%d (board top line y=%d)"
              % (int(clipm.sum()), cxs.min(), cxs.max(), cys.min(), cys.max(),
                 min(p[1] for p in quad)), flush=True)
    else:
        print("!! chrome clip not found in --clip-box -- refusing", flush=True)
        return 5

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
    bright = (L > a.bright) & (RmG < a.rim_rmg)
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
    YY = np.arange(H)[:, None] * np.ones((1, W), int)
    topstrip = Qr & (YY < a.flat_top_y)
    # the clip is unioned back in AFTER the subtraction -- it is bright, and the
    # rule that protects the hands would otherwise delete the one thing the bar
    # explicitly requires be covered (beat 06 v1 left its whole clip standing).
    keep = ((Qr | clipm) & ~excl) | face | clipm | topstrip
    keep = ndimage.binary_fill_holes(keep)
    keep = ndimage.binary_opening(keep, np.ones((3, 3)))
    keep = ndimage.binary_fill_holes(keep)
    lab2, n2_ = ndimage.label(keep)
    if n2_:
        sz = ndimage.sum(keep, lab2, range(1, n2_ + 1))
        keep = np.isin(lab2, [i + 1 for i, v in enumerate(sz) if v >= 200])
    print("(rounded quad | clip) - bright(L>%.0f & R-G<%.0f) | face | clip | "
          "topstrip(y<%d, %d px) -> %d px"
          % (a.bright, a.rim_rmg, a.flat_top_y, int(topstrip.sum()),
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
