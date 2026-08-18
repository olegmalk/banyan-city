#!/usr/bin/env python3
"""beat08_gesture_composite.py -- give beat 08's init its GESTURE by moving the
plate's own pixels, so the 0.30 inpaint has structure to shade rather than
staging to invent.

WHY THIS EXISTS. On 2026-08-18 ep2-b08-twofig-gesture-0818 ran a 0.30 restyle
over the two-figure plate and FAILED on exactly one clause: the clipboard stayed
raised and nobody pointed. The measurement was the useful part -- inside the
mask 32.9% of pixels moved more than 8 levels while outside it 0.1% did, so the
sampler redrew a third of the region and spent all of it redrawing the SAME
STAGING. That is what strength 0.30 does when you ask it to ADD.
pipeline/composite-init-pattern.md forbids the higher-strength rescue by name
(§2: above 0.35 "the sampler stops FINISHING and starts INVENTING"), so the
remaining lever is the one beat 01's leaf count used: put the structure in with
plain image processing, then let 0.30 make it look drawn.

TWO OPERATIONS, AND THEY ARE NOT EQUALLY DEFENSIBLE. That asymmetry is the
whole finding of this file and it is stated here rather than buried:

  --lower-board   DEFENSIBLE, and it is the default. The clipboard is a rigid
                  quadrilateral gripped at both edges. Board and both hands move
                  as ONE unit; the grip does not change, only the height. Every
                  pixel of the result is a plate pixel except the vacancy fill
                  and the feathered seam. This is a translation, which is the
                  class of edit cel art survives.

  --point-arm     NOT DEFENSIBLE, AND IT IS IMPLEMENTED ANYWAY SO THE CLAIM CAN
                  BE LOOKED AT INSTEAD OF ASSERTED. Three separate blockers were
                  read off the plate at 3x on 2026-08-18, and each one alone is
                  fatal:
                    1. NO POINTING HAND EXISTS. The guard's near hand is a
                       four-finger BACK-OF-HAND GRIP curled over the board's left
                       edge (x 545-620, y 515-600). A point needs an extended
                       index and a closed fist seen from another angle. No
                       rotation of a curled fist is a point. The goblin's own
                       hand is not a source either -- it is green, it belongs to
                       the other character, and it is also a curled claw.
                    2. NO FOREARM EXISTS TO MOVE. The guard's near forearm is
                       under the brown cloak and the cream under-robe; there is
                       no delineated sleeve to cut, translate or rotate. The
                       reach required is ~235 px.
                    3. THE PATH IS OCCUPIED. The goblin's own green fist sits at
                       x 355-475, y 585-700 -- dead centre of the gap between the
                       guard's hand and the goblin's belly (the maroon sash,
                       x 260-375, y 565-610). Any arm drawn across that gap must
                       cross his fist, which is an occlusion decision, not a
                       translation.
                  So this operation cannot move anything into a point; it can
                  only STRETCH a sleeve and ROTATE a fist, and the output is
                  saved so that judgement rests on pixels. It always reports a
                  failed check.

THE LAWS FROM composite-init-pattern.md THAT ARE LIVE HERE.
  §6 THE VACANCY LAW -- never leave an unpainted gap. The board's old footprint
  is given positive content before anything else happens.
  §12 THE SOURCE LAW -- never patch with pixels that satisfy your own object
  rule. THIS IS THE BUG THAT WAS FIXED ON 2026-08-18: the first cut of this file
  filled the vacancy with `diffuse` (blur the frame, keep the inside, repeat),
  seeded from the plate ITSELF -- so the seed inside the hole was the board's own
  dark maroon face. 140 iterations at radius 7 propagate about 7*sqrt(140) ~ 83
  px, and the hole is 240 x 186, so the centre never washed out. The "fill" was
  a BLURRED COPY OF THE BOARD: a grey rectangle with hard edges, which is both
  the source law broken and decal tell #3 (a straight-edged tone panel). Looked
  at, not inferred -- the check suite passed it 5/5 while the picture was
  obviously wrong, which is why C6/C7 below exist.
  §12 corollary 1 -- grow must exceed feather so the board's dark cel outline
  cannot survive at partial alpha and return as a ghost (12 vs 6).
  §12 meta-finding -- "a tool must measure whether its region actually covers
  the object it claims to act on, and refuse when it does not." The board mask
  is DERIVED from the board's own pixels (largest dark-maroon component plus the
  silver clip), not typed in as a rectangle, and it auto-grows until it provably
  contains every board pixel in the window or refuses.
  §13 REMOVE THE CUE -- the cues that say "clipboard raised" are the two grips,
  and they MOVE WITH THE BOARD, so the cue travels rather than surviving. The
  cue that is knowingly left behind is the cloak's drape over the shoulders; it
  is declared in the spec's bar rather than scored as a surprise.

THE FILL. Not diffusion, and not a lateral clone either (§12: no clone survives
a luminance gradient). Per column, the strip of cloak DIRECTLY ABOVE the hole is
resampled down over the hole's extent -- a vertical STRETCH of the plate's own
adjacent cloth. The guard's torso is a vertical drape, so stretching preserves
the fold lines in their correct x positions and the pale chest wedge keeps
widening downward the way it already does. It repeats nothing (not decal tell
#4) and it inherits the plate's own light by construction. The rectangular edge
is then killed by a cosine ramp into the plate's own neighbouring pixels on each
side. NO SETTLE BLUR: it was tried at 4 iterations of radius 1.2 and it was the
single largest cause of the smear, dropping the fill's detail to 27% of the
cloak's when the ramps alone hold the boundary at 69% (C8, and ring MAE 7.4
against beat 21's rejected 22.9). A `flat` mode is kept and is NOT the default,
because one flat colour per column turns the guard's pale chest wedge -- which
widens as it descends -- into a hard vertical bar.

$0. Pure PIL, numpy and scipy (as pipeline/b17_hand_track.py already uses). No
model, no sampler, no GPU, no network. The init is asserted by sha256 before a
single pixel is written, and --dry-run writes the mask and the plan and exits
before anything is composited.

    python3 pipeline/beat08_gesture_composite.py \\
        --init <plate>.png --init-sha256 <hex> \\
        --out comp.png --mask-out mask.png [--drop 130] \\
        [--point-arm] [--dry-run]

Exit codes: 0 pass, 2 sha mismatch or wrong size, 3 a check failed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

# The plate this file was traced against. Any other size is refused rather than
# silently rescaled -- the geometry below is in THIS picture's pixels.
W, H = 832, 1216

# The window the board is looked for in. Deliberately generous; the mask itself
# is derived from pixels inside it, not from these numbers.
BOARD_WIN = (540, 460, 820, 700)      # x0, y0, x1, y1

# MEASURED 2026-08-18 by connected components inside BOARD_WIN:
#   dark maroon board face  x 548..750, y 506..663, 20017 px
#   the board is TILTED -- its face runs x 602..654 at y 510 and x 549..711 at
#   y 660 -- which is exactly why a typed rectangle left board pixels behind at
#   the lower left and the tool now derives the shape instead.
HAND_L = (545, 505, 645, 618)         # guard's near hand, gripping the left edge
HAND_R = (693, 505, 793, 618)         # guard's far hand, gripping the right edge
# Where a lowered board sits: his white sash is y 650-690, so waist is ~+130.
DROP_DEFAULT = 130
# The goblin's belly, the target of the point. Centre of his maroon sash band.
BELLY = (315, 588)
# The only cream pixels on the guard's near side that could stand in for a
# forearm. They are robe, not sleeve -- see the header, blocker 2.
SLEEVE_L = (455, 545, 560, 615)

# A patch of the guard's own cloak that the edit never touches, used as the
# baseline for "how many dark fold pixels does this garment normally carry".
# Measured 2026-08-18: it carries them at density 0.037, which is MORE than the
# vacancy fill does.
CLOAK_REF = (540, 300, 780, 470)

SKIN = dict(r_min=150, rb_min=30, l_min=130)


def lum(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def skin_mask(a):
    R, B = a[..., 0], a[..., 2]
    return (R > SKIN["r_min"]) & (R - B > SKIN["rb_min"]) & (lum(a) > SKIN["l_min"])


def board_face_mask(a):
    """The board's dark maroon face. This is the OBJECT RULE for this beat."""
    return (lum(a) < 80) & (a[..., 1] < 62)


def clip_mask(a):
    """The silver spring clip along the board's top edge."""
    return (lum(a) > 150) & (np.abs(a[..., 0] - a[..., 2]) < 25) & (a[..., 2] >= a[..., 0])


def in_window(shape, win):
    m = np.zeros(shape[:2], bool)
    x0, y0, x1, y1 = win
    m[y0:y1, x0:x1] = True
    return m


def biggest_component(m):
    lab, n = ndimage.label(m)
    if n == 0:
        return np.zeros_like(m)
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    return lab == (int(np.argmax(sizes)) + 1)


def span_fill(m):
    """Fill each row and each column between its extreme True pixels.

    The board is a convex quadrilateral, so this recovers its interior (and the
    frame between face and clip) without assuming an axis-aligned rectangle.
    """
    out = m.copy()
    for y in range(m.shape[0]):
        idx = np.nonzero(m[y])[0]
        if len(idx):
            out[y, idx.min():idx.max() + 1] = True
    for x in range(m.shape[1]):
        idx = np.nonzero(out[:, x])[0]
        if len(idx):
            out[idx.min():idx.max() + 1, x] = True
    return out


def dilate(m, px):
    if px <= 0:
        return m
    return ndimage.binary_dilation(m, iterations=int(px))


def feathered(mask, feather):
    m = Image.fromarray((mask * 255).astype(np.uint8))
    if feather:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(m, np.float32)[:, :, None] / 255.0


def stretch_fill(arr, hole, src_h, edge_ramp, settle_iters, settle_radius,
                 visible_h=None, mode="stretch"):
    """Fill `hole` by resampling the cloth DIRECTLY ABOVE it down over the gap.

    §12 rules this rather than diffusion (which, seeded from the plate, is a
    blurred copy of the object -- the source law) and rather than a lateral
    clone (which cannot survive the plate's luminance gradient). A vertical
    stretch of the plate's own adjacent cloth keeps the fold lines in their x
    positions and inherits the light by construction.

    Returns (filled_array, source_rows_used, min_headroom).
    """
    out = arr.astype(np.float32).copy()
    src = arr.astype(np.float32)
    cols = np.nonzero(hole.any(0))[0]
    headroom = 10 ** 9
    for x in cols:
        rows = np.nonzero(hole[:, x])[0]
        y0, y1 = int(rows.min()), int(rows.max())
        top = y0 - src_h
        if top < 0:
            top = 0
        # The source must itself be hole-free, or we are patching the object
        # with the object again.
        while top < y0 and hole[top:y0, x].any():
            top += 1
        have = y0 - top
        headroom = min(headroom, have)
        if have < 4:
            continue
        strip = src[top:y0, x, :]                      # (have, 3)
        # Only the top `visible_h` rows of the hole are ever seen -- the rest is
        # covered by the board at its new height. Stretching the source over the
        # WHOLE hole was a 4.5x vertical magnification and it read as a smear;
        # stretching it over the visible part only is about 2.5x.
        yv = y1 if visible_h is None else min(y1, y0 + visible_h - 1)
        n = yv - y0 + 1
        if mode == "flat":
            # CEL FILL. Anime cloth is flat colour bounded by lines, so the
            # style-correct invention is a flat band per column, not a gradient.
            # A stretch of a soft gradient reads as a photographic smudge in a
            # picture that has no soft gradients in it.
            out[y0:y1 + 1, x, :] = np.median(strip, axis=0)
            continue
        t = np.linspace(0.0, have - 1.0, n)
        i0 = np.floor(t).astype(int)
        i1 = np.minimum(i0 + 1, have - 1)
        w = (t - i0)[:, None]
        out[y0:yv + 1, x, :] = strip[i0] * (1 - w) + strip[i1] * w
        if yv < y1:                                    # hold the last row down
            out[yv + 1:y1 + 1, x, :] = out[yv, x, :]

    # Cosine ramp into the plate's own neighbours on the left and right of each
    # row, so the patch does not print a straight-edged tone panel (decal tell
    # #3, §12 corollary 2).
    for y in range(hole.shape[0]):
        idx = np.nonzero(hole[y])[0]
        if not len(idx):
            continue
        x0, x1 = int(idx.min()), int(idx.max())
        lref = src[y, x0 - 1, :] if x0 - 1 >= 0 else None
        rref = src[y, x1 + 1, :] if x1 + 1 < arr.shape[1] else None
        span = x1 - x0 + 1
        r = min(edge_ramp, span // 2)
        for k in range(r):
            wgt = 0.5 * (1 + np.cos(np.pi * k / max(r, 1)))   # 1 -> 0
            if lref is not None:
                out[y, x0 + k, :] = out[y, x0 + k, :] * (1 - wgt) + lref * wgt
            if rref is not None:
                out[y, x1 - k, :] = out[y, x1 - k, :] * (1 - wgt) + rref * wgt

    # Settle: a few small blurs kept strictly inside the hole. Enough to kill
    # column-to-column jitter, far too few to wash the drape out.
    m3 = np.repeat(hole[:, :, None], 3, axis=2)
    for _ in range(settle_iters):
        blur = np.asarray(
            Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).filter(
                ImageFilter.GaussianBlur(settle_radius)), np.float32)
        out = np.where(m3, blur, out)
    return np.clip(out, 0, 255).astype(np.uint8), src_h, headroom


def ring_mae(a, b, hole, w=6):
    """Mean abs difference across the hole's boundary: inner ring vs outer ring.

    Beat 21 scored a clone at 22.9 out of sample. Anything in single digits here
    means the patch hands off to the plate without a visible step.
    """
    inner = hole & ~ndimage.binary_erosion(hole, iterations=w)
    outer = ndimage.binary_dilation(hole, iterations=w) & ~hole
    if not inner.any() or not outer.any():
        return 0.0
    return float(abs(b[inner].astype(float).mean(0) - b[outer].astype(float).mean(0)).mean())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", required=True)
    ap.add_argument("--init-sha256", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mask-out", required=True)
    ap.add_argument("--drop", type=int, default=DROP_DEFAULT,
                    help="px to lower the board+hands unit")
    ap.add_argument("--point-arm", action="store_true",
                    help="ALSO attempt the pointing arm. See this file's header: "
                         "the plate has no pointing hand, no exposed forearm and "
                         "the path is blocked by the goblin's own fist, so this "
                         "is an attempt kept for inspection, not a recommended "
                         "edit. It always fails a check.")
    ap.add_argument("--feather", type=int, default=6)
    ap.add_argument("--mask-grow", type=int, default=12)
    ap.add_argument("--board-grow", type=int, default=12)
    ap.add_argument("--board-grow-max", type=int, default=26)
    ap.add_argument("--src-h", type=int, default=58,
                    help="rows of cloth above the hole used as fill source. 58 "
                         "is the measured ceiling: the guard's gold cloak clasp "
                         "sits at y 400-425 and the board's mask starts at 486, "
                         "so a taller source would stretch the clasp into a "
                         "smear.")
    ap.add_argument("--fill", choices=("stretch", "flat"), default="stretch",
                    help="stretch = resample the cloth above the hole down over "
                         "it; flat = one flat colour per column. BOTH WERE "
                         "LOOKED AT: flat turns the guard's pale chest wedge, "
                         "which widens downward, into a hard vertical BAR, so "
                         "stretch is the default despite flat being nearer to "
                         "how cel art is actually painted.")
    ap.add_argument("--vis-pad", type=int, default=16,
                    help="rows below the vacancy still stretched, as slack under "
                         "the feathered edge of the lowered board")
    ap.add_argument("--edge-ramp", type=int, default=20)
    ap.add_argument("--settle-iters", type=int, default=0,
                    help="0 by default. The settle blur was the single biggest "
                         "source of the smear -- 4 iterations at radius 1.2 "
                         "turned a legible cloak into a smudge, and the ramps "
                         "alone hold the boundary (ring MAE 7.4).")
    ap.add_argument("--settle-radius", type=float, default=1.2)
    ap.add_argument("--sample-mask-out", default="",
                    help="ALSO write the 0.30 sample's --mask-png: this tool's "
                         "own seam mask UNIONED with --gesture-ellipse. The "
                         "union is the point. The seam half makes B4a (does the "
                         "composited descent survive the pass) a real test by "
                         "putting the WHOLE lowered board inside the region the "
                         "sampler may redraw, instead of protecting it and "
                         "scoring a guaranteed pass. The ellipse half keeps B4b "
                         "(the point) observable -- pattern doc §13.3 forbids "
                         "shrinking a mask off the thing being tested, and a "
                         "mask that excluded the goblin would make the missing "
                         "point an artefact of the mask rather than a finding.")
    ap.add_argument("--gesture-ellipse", default="445,620,335,165",
                    help="cx,cy,rx,ry -- the gesture zone, carried unchanged "
                         "from ep2-b08-twofig-gesture-0818 where it was measured "
                         "and verified to clear both faces and both lower robes.")
    ap.add_argument("--note", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not os.path.isfile(a.init):
        print("!! init not found: %s" % a.init, flush=True)
        return 2
    h = hashlib.sha256()
    with open(a.init, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    have = h.hexdigest()
    if have != a.init_sha256:
        print("!! INIT SHA MISMATCH -- refusing.\n   want %s\n   have %s"
              % (a.init_sha256, have), flush=True)
        return 2

    plate = Image.open(a.init).convert("RGB")
    if plate.size != (W, H):
        print("!! this file's geometry is traced on %dx%d, got %dx%d -- refusing "
              "rather than rescaling someone else's coordinates."
              % (W, H, plate.size[0], plate.size[1]), flush=True)
        return 2
    arr = np.asarray(plate, np.uint8)
    ai = arr.astype(int)

    # ---- derive the board from the board's own pixels ------------------------
    win = in_window(arr.shape, BOARD_WIN)
    face_all = board_face_mask(ai)
    face = biggest_component(face_all & win)
    clipm = biggest_component(clip_mask(ai) & win & dilate(face, 30))
    seed = span_fill(face | clipm)

    # §12 meta-finding: measure that the region covers the object, or refuse.
    # The target is every pixel that satisfies the board's own rule AND is
    # 8-connected to the board -- not merely near it. Written that way after the
    # first cut of this assertion refused on 444 px that turned out to be the
    # guard's WHITE SASH (bright, so clip_mask claimed it) and four dark cel
    # outlines in the cloak. A rule that refuses on the sash is not measuring
    # the board.
    board_ish = (face_all | clip_mask(ai)) & win
    lab_b, nb = ndimage.label(board_ish)
    keep = set(np.unique(lab_b[face | clipm])) - {0}
    target = np.isin(lab_b, list(keep)) if keep else (face | clipm)
    g, board, leak = a.board_grow, None, -1
    while g <= a.board_grow_max:
        cand = span_fill(dilate(seed, g))
        leak = int((target & ~cand).sum())
        if leak == 0:
            board, board_grow, board_leak = cand, g, leak
            break
        g += 2
    if board is None:
        print("!! board mask never covered every board pixel in the window even "
              "at grow=%d (%d px still outside) -- refusing rather than moving a "
              "board and leaving parts of it behind."
              % (a.board_grow_max, leak), flush=True)
        return 3

    # The hands, like the board, are DERIVED. A plain box-and-skin-rule caught
    # bright grass at the right edge of HAND_R (grass passes R>150, R-B>30,
    # lum>130), carried it down with the unit and printed a hard bright block
    # against the cloak's silhouette at x 755-795. Taking the largest skin
    # COMPONENT inside each box drops the specks and keeps the hand.
    sk = skin_mask(ai)
    hands = dilate(biggest_component(sk & in_window(arr.shape, HAND_L))
                   | biggest_component(sk & in_window(arr.shape, HAND_R)), 6)
    unit = board | hands
    n_board, n_hands = int(board.sum()), int(hands.sum())

    ys, xs = np.nonzero(board)
    board_bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]

    # where it lands
    moved = np.zeros_like(unit)
    moved[a.drop:, :] = unit[:H - a.drop, :]
    vacated = unit & ~moved

    # the inpaint mask: everything the sampler is allowed to touch. Both the
    # source and destination footprints plus the seams. Grown past the feather
    # so the cel outline of the board cannot survive at partial alpha and return
    # as a ghost (§12 corollary 1).
    mask = dilate(unit | moved, a.mask_grow)

    plan = {
        "board_bbox_derived": board_bbox, "board_grow": board_grow,
        "board_leak_px": board_leak,
        "hand_l": list(HAND_L), "hand_r": list(HAND_R),
        "drop_px": a.drop, "board_px": n_board, "hand_px": n_hands,
        "unit_px": int(unit.sum()), "vacated_px": int(vacated.sum()),
        "mask_px": int(mask.sum()),
        "mask_frac_of_frame": round(float(mask.mean()), 4),
        "point_arm_attempted": bool(a.point_arm),
        "fill": a.fill, "src_h": a.src_h, "edge_ramp": a.edge_ramp,
    }
    Image.fromarray((mask * 255).astype(np.uint8)).save(a.mask_out)
    print("WROTE %s" % a.mask_out, flush=True)

    if a.sample_mask_out:
        cx, cy, rx, ry = (int(v) for v in a.gesture_ellipse.split(","))
        ell = Image.new("L", (W, H), 0)
        ImageDraw.Draw(ell).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
        sample = np.maximum(np.asarray(ell), (mask * 255).astype(np.uint8))
        sm = sample > 127
        ys_s, xs_s = np.nonzero(sm)
        plan["sample_mask_bbox"] = [int(xs_s.min()), int(ys_s.min()),
                                    int(xs_s.max()), int(ys_s.max())]
        plan["sample_mask_px"] = int(sm.sum())
        plan["sample_mask_covers_whole_moved_board"] = bool((moved & ~sm).sum() == 0)
        plan["gesture_ellipse"] = a.gesture_ellipse
        Image.fromarray(sample).save(a.sample_mask_out)
        print("WROTE %s" % a.sample_mask_out, flush=True)
    print("plan " + json.dumps(plan, sort_keys=True), flush=True)
    if a.dry_run:
        print("DRY RUN -- mask and plan only, nothing composited.", flush=True)
        return 0

    # ---- operation A: lower the board ---------------------------------------
    src = arr.astype(np.float32)
    shifted = np.zeros_like(src)
    shifted[a.drop:, :, :] = src[:H - a.drop, :, :]

    base, _, headroom = stretch_fill(arr, unit, a.src_h, a.edge_ramp,
                                     a.settle_iters, a.settle_radius,
                                     visible_h=a.drop + a.vis_pad, mode=a.fill)
    # The feather is a Gaussian, and a Gaussian has a tail: left unclamped it
    # moved pixels 16 px outside the declared inpaint mask by up to 4/255. The
    # blend must live entirely inside the region the spec declares, so the alpha
    # is clamped to the mask -- otherwise "nothing changes outside the mask" is
    # a claim the picture quietly breaks.
    al = feathered(moved, a.feather) * mask[:, :, None].astype(np.float32)
    out = base.astype(np.float32) * (1 - al) + shifted * al

    checks, fails = [], []

    # ---- operation B: the pointing arm, attempted so it can be judged -------
    arm_note = "not attempted"
    if a.point_arm:
        hand = plate.crop(HAND_L).rotate(-70, expand=True, resample=Image.BICUBIC)
        hw, hh = hand.size
        sl = plate.crop(SLEEVE_L)
        reach = SLEEVE_L[0] - BELLY[0] + 40
        sleeve = sl.resize((max(reach, 1), SLEEVE_L[3] - SLEEVE_L[1]), Image.LANCZOS)
        canvas = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
        canvas.paste(sleeve, (BELLY[0] - 40, SLEEVE_L[1] + 25))
        canvas.paste(hand, (BELLY[0] - hw // 2, BELLY[1] - hh // 2))
        out = np.asarray(canvas, np.float32)
        arm_note = ("ATTEMPTED. A four-finger BACK-OF-HAND GRIP rotated -70 deg "
                    "and a %d px robe strip stretched to %d px. Neither is a "
                    "point, the stretch is not anatomy, and the paste lands on "
                    "top of the goblin's own fist. Saved for inspection."
                    % (SLEEVE_L[2] - SLEEVE_L[0], reach))
        fails.append("C10 the pointing arm is synthesised, not moved -- see the note")

    out_u8 = np.clip(out, 0, 255).astype(np.uint8)

    # ---- checks -------------------------------------------------------------
    outside = ~dilate(unit | moved, a.mask_grow + 4)
    d_out = int(np.abs(out_u8.astype(int) - ai).max(2)[outside].max())
    checks.append(("C1 board+hands moved as ONE unit",
                   n_board > 20000 and n_hands > 3000,
                   "board %d px, hands %d px" % (n_board, n_hands)))
    checks.append(("C2 the board actually descends",
                   a.drop >= 80, "drop %d px" % a.drop))
    checks.append(("C3 nothing changes outside the grown mask",
                   d_out <= 2, "max delta %d/255" % d_out))
    dest = moved & ~ndimage.binary_erosion(moved, iterations=8)
    face_dest = board_face_mask(out_u8.astype(int)) & moved
    checks.append(("C4 a dark board face exists at the new height",
                   int(face_dest.sum()) > 15000,
                   "%d board-face px inside the destination" % int(face_dest.sum())))
    # C5 -- the one that catches the bug the first cut shipped: no BOARD may
    # survive where the board used to be. A raw count of rule-satisfying pixels
    # is the wrong form and it was tried first: the guard's cloak is drawn with
    # dark fold shadows that satisfy the board rule all by themselves (untouched
    # cloak carries them at density 0.037), so a raw count flags the plate's own
    # drawing style, and the earlier settle blur "passed" the check only by
    # lightening those folds. The honest test is two clauses -- the vacancy must
    # not be DENSER in board-rule pixels than the guard's own untouched cloak,
    # and no single BLOB may survive, because a leftover board slab is one big
    # component while fold lines are many thin ones.
    left_behind = board_face_mask(out_u8.astype(int)) & vacated & ~moved
    ref = in_window(arr.shape, CLOAK_REF) & ~dilate(unit | moved, a.mask_grow + 4)
    ref_d = float(board_face_mask(ai)[ref].mean()) if ref.any() else 1.0
    vac_d = float(left_behind.sum()) / max(int((vacated & ~moved).sum()), 1)
    lab_l, n_l = ndimage.label(left_behind)
    biggest = int(ndimage.sum(left_behind, lab_l, range(1, n_l + 1)).max()) if n_l else 0
    checks.append(("C5 no board left behind in the vacancy",
                   vac_d <= 1.5 * ref_d and biggest < 1200,
                   "density %.4f vs untouched cloak %.4f, largest blob %d px in "
                   "%d components" % (vac_d, ref_d, biggest, n_l)))
    # C6 -- the source law, measured. If the fill were a blurred copy of the
    # board its mean would sit near the board's, not near the cloak's.
    vac_only = vacated & ~moved & ~dilate(moved, 8)
    ring_out = ndimage.binary_dilation(unit, iterations=8) & ~unit
    if vac_only.any():
        fill_l = float(lum(out_u8.astype(float))[vac_only].mean())
        cloak_l = float(lum(ai.astype(float))[ring_out].mean())
        board_l = float(lum(ai.astype(float))[face].mean())
        ok6 = abs(fill_l - cloak_l) < abs(fill_l - board_l)
        checks.append(("C6 the fill reads as cloak, not as the board it replaced",
                       ok6, "fill lum %.0f vs cloak %.0f vs board %.0f"
                            % (fill_l, cloak_l, board_l)))
    # C7 -- boundary ring: does the patch hand off to the plate without a step?
    rm = ring_mae(arr, out_u8, unit & ~moved, 6)
    checks.append(("C7 the patch boundary has no visible step",
                   rm < 14.0, "ring MAE %.1f (beat 21's rejected clone: 22.9)" % rm))
    # C8 -- THE CHECK THAT ACTUALLY CATCHES THE BUG THAT SHIPPED, and it is here
    # because C5 and C6 both waved that bug through. A blurred copy of the board
    # is not dark (blurring lifts it) and its mean luminance sits near the
    # cloak's, so neither a colour rule nor a luminance rule sees anything wrong.
    # What is wrong with a smear is that it has NO DETAIL. Measured on the same
    # plate, mean |gradient| over the visible vacancy against the guard's own
    # untouched cloak (8.15):
    #     diffuse fill, the shipped bug ....... 1.12   14%   rejected by eye
    #     flat fill, settle 4 ................. 1.50   18%   rejected by eye
    #     stretch fill, settle 4 .............. 2.16   27%   rejected by eye
    #     stretch fill, settle 0 (this one) ... 5.62   69%   signed by eye
    # The bar is set at 45%, which separates every variant a look rejected from
    # the one a look accepted.
    def gradient_energy(img, mask):
        Lg = lum(img.astype(float))
        gx = np.abs(np.diff(Lg, axis=1, prepend=Lg[:, :1]))
        gy = np.abs(np.diff(Lg, axis=0, prepend=Lg[:1, :]))
        return float(np.maximum(gx, gy)[mask].mean()) if mask.any() else 0.0
    vis_vac = vacated & ~moved & ~dilate(moved, 8)
    g_fill = gradient_energy(out_u8, vis_vac)
    g_ref = gradient_energy(ai, ref)
    checks.append(("C8 the fill has cloth detail, it is not a smudge",
                   g_ref <= 0 or g_fill >= 0.45 * g_ref,
                   "gradient energy %.2f vs untouched cloak %.2f (%.0f%%; the "
                   "diffuse fill this replaced scored 14%%)"
                   % (g_fill, g_ref, 100 * g_fill / max(g_ref, 1e-6))))
    checks.append(("C9 the fill had real cloth above it to stretch",
                   headroom >= 20, "min headroom %d rows" % headroom))

    for name, ok, detail in checks:
        print("  %-52s %-4s %s" % (name, "PASS" if ok else "FAIL", detail), flush=True)
        if not ok:
            fails.append(name)

    Image.fromarray(out_u8).save(a.out)
    print("WROTE %s" % a.out, flush=True)

    sha = hashlib.sha256(open(a.out, "rb").read()).hexdigest()
    with open(a.out + ".meta.yaml", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join([
            "# Composite provenance (7.2). No model, no sampler, no GPU, $0.",
            "tool: pipeline/beat08_gesture_composite.py",
            "init: %s" % os.path.basename(a.init),
            "init_sha256: %s" % have,
            "out_sha256: %s" % sha,
            "plan: %s" % json.dumps(plan, sort_keys=True),
            "point_arm: %s" % json.dumps(arm_note),
            "checks: %s" % json.dumps([[n, bool(o), d] for n, o, d in checks]),
            "fails: %s" % json.dumps(fails),
            "cost_usd: 0",
            "approved: false",
            "provisional: >-",
            "  A STEWARD COMPOSITE, not a pick and not canon. Ground truth is the",
            "  founder (R4).",
            "note: %s" % json.dumps(a.note or "beat 08 gesture composite"),
            "",
        ]))
    print("WROTE %s.meta.yaml" % a.out, flush=True)
    if fails:
        print("!! %d check(s) failed -- NO GPU RUNS ON A FAILED COMPOSITE." % len(fails),
              flush=True)
        return 3
    print("rc=0 all checks pass", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
