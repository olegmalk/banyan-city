#!/usr/bin/env python3
r"""beat08_grip_composite.py -- put beat 08's clipboard IN the guard's hand by
moving the plate's own hand onto it, so a 0.30 inpaint has a grip to finish
instead of a grip to invent.

!! VERDICT: FAIL, 2026-08-20. READ THIS BEFORE RUNNING ANYTHING BELOW. !!
Judged by the lane that picked this up after the authoring lane died mid-round.
Route log `pipeline/b08-arm-route-0819.md` §21; evidence
`farm-out/ep2-b08-gripcomp-0820/EVIDENCE-b08-gripcomp-verdict-0820.png`.

  1. THIS SOURCE DOES NOT REBUILD THE ARTIFACT NEXT TO IT. `08-first-citizen-
     gripcomp-0820.png` on disk differs from what `build()` now produces in
     4488 of the hole's 4489 px and in ZERO px anywhere else. The artifact was
     written by an axial-continuation `fill_vacancy`; the body below is an
     isotropic Jacobi diffusion. Do not run `--write`: it would overwrite the
     only copy of the round the authoring lane judged, with a different fill.
  2. THE DOCSTRING OF `fill_vacancy` DESCRIBES A FILL THIS FILE NO LONGER HAS.
     "the correction is not a different blur, it is a different direction" is
     the artifact's fill, not this code's. `STRAP_AXIS` (defined, never read)
     and `STRAP_BASELINE` (superseded by C4's ring) are both DEAD and are left
     in place as the evidence of the mismatch rather than tidied away.
  3. C4 IS VOID ON THIS VACANCY, AND THAT IS THE FINDING WORTH KEEPING. The
     on-disk fill scores 16.04 against the ring's 17.94 -- 89%, twice the 45%
     bar -- and at 5x it is a ribbed corduroy comb running down the strap. A
     mean-|gradient| bar is a SMEAR detector, not a detail detector, and it
     certified a streak artifact. The obvious extension does not rescue it:
     |gy|/|gx| reads 0.64 in the fill and 0.64 in the untouched ring, because
     the streaks run along the strap's own dominant axis. No cheap pixel
     statistic tried here separates the fill an eye rejects from the material.
  4. THE AUTHORING LANE'S OWN SELF-CATCH WAS WRONG, MEASURED. It suspected the
     C4 baseline was inflated by the removed fist's outline. Same ring pixels,
     gradient computed with the fist present 17.94 vs with it removed 17.86 --
     the outline is worth 0.4%. The innermost annulus is the COOLEST (12.53 at
     1 px, rising to 21.4 at 8-10 px): the ring is hot because the clasp, the
     sash edge and the shirt folds are there, not because of the rim. Honest
     re-bases that exclude the object entirely -- rings 3-12, 4-14, 5-14, 6-16,
     8-20 px -- give 17%, 18%, 18%, 19%, 22%. The bar's answer does not move.
  5. THE OPERATION IS WRONG, NOT THE FILL. Moving the hand opens 4489 px in a
     harness-strap / cuff / shirt junction the plate has no clean source for.
     Three fill families have now been tried and all three left a visible
     artifact; two of them PASSED the pre-registered bar. See §21 for the rung
     that follows, which is not a fourth fill.

WHY THIS EXISTS, AND WHY IT IS NOT THE ATTEMPT composite-init-pattern.md 9b
STOPPED. That stop was about beat 08's STAGING on the 2026-08-18 plate, and its
three blockers were all about a limb that did not exist: "no pointing hand
exists", "no forearm exists to move", "the path is occupied". None of the three
holds on THIS plate. `ep2-b08-scale30-0820` already has the pointing arm (B4c
passes, eleven mechanisms), already has the board drawn at the authored quad and
tilt (B4a passes on presence), and already has a WELL-DRAWN ARTICULATED FIST --
four finger creases, its own dark outline, correct skin and cel shading -- 90.5
px above the board on the harness strap. Nothing has to be manufactured. One
compact, fully outlined object has to move 91 px.

THE OPERATION, AND WHY THIS ONE RATHER THAN THE OTHER TWO CONSIDERED.

  MOVE THE HAND (chosen). A translation of one closed, outlined component whose
  silhouette can be traced by eye at 4x, onto the board's top-left corner, and
  pasted ON TOP of the board so the fingers occlude its top edge -- which is how
  cel art draws a hand holding a board, and which is the "fingers wrapped at the
  edge" the bar asks for. The board is not touched at all, so B4a's geometry --
  the clause that has passed four times, at the authored quad and the authored
  9 degree tilt -- stays BYTE-IDENTICAL. The only vacancy is the hand's old
  footprint on the harness strap, which is a smooth diagonal band whose two
  boundaries are visible directly above and below the hole.

  MOVE THE BOARD (rejected). It needs a clean board silhouette and the board
  will not segment: below y~740 the background grass is darker than the board,
  and a luma threshold that takes the board also takes the grass. A translation
  of a mis-cut object is a decal. Also, moving the board up far enough to reach
  the hand puts its centre ABOVE the hip line, and `clipboard lowered` is the
  clause the beat is about.

  EXTEND THE BOARD UPWARD (rejected). Additive, no vacancy, tempting -- and it
  turns a 95x152 clipboard into a 95x212 plank. A clipboard has an aspect ratio
  and this breaks it.

WHAT IS DRAWN HERE: NOTHING. Not one invented stroke. Every pixel in the result
is either an untouched plate pixel, a plate pixel translated as a rigid unit, or
a vacancy fill interpolated from the vacancy's OWN boundary. Section 9's r2
lesson on this beat is that hand-authored geometry fails by being confidently
wrong; the safest hand to put on the board is the one the model already drew.

THE LAWS THIS FILE CARRIES, COPIED RATHER THAN IMPORTED (they live in
composite-init-pattern.md 9b, 12 and 13, and in beat03/beat13's compositors):

  * AN OUTLINE THAT IS NOT IN THE ALPHA IS HALF AN OUTLINE. The hand polygon is
    traced OUTSIDE the fist's dark rim, so the rim travels with the fill. C3
    asserts the moved unit carries dark pixels at its own border.
  * A SMEAR IS INVISIBLE TO EVERY COLOUR RULE -- MEASURE DETAIL. The vacancy
    fill is scored on mean |gradient| against the same strap's untouched pixels,
    and must reach 45% of it (9b's measured bar). No settle blur: 9b found the
    settle pass was itself the largest single cause of the smear.
  * REMOVE THE CUE, NOT JUST THE OBJECT. The mask covers the OLD hand site as
    well as the new one, so the 0.30 pass re-renders the strap where the grip
    used to be rather than leaving a hand-shaped ghost for it to rationalise.

    python3 pipeline/beat08_grip_composite.py --selftest
    python3 pipeline/beat08_grip_composite.py --write
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PLATE = os.path.join(REPO, "farm-out", "ep2-b08-scale30-0820",
                     "ep2-b08-scale30-0820-scale30.png")
PLATE_SHA = None  # filled by --selftest from disk and printed, not pinned blind

OUT_DIR = os.path.join(REPO, "farm-out", "ep2-b08-gripcomp-0820")
OUT_INIT = os.path.join(OUT_DIR, "08-first-citizen-gripcomp-0820.png")
OUT_MASK = os.path.join(OUT_DIR, "08-first-citizen-gripcomp-mask-0820.png")
OUT_EVID = os.path.join(OUT_DIR, "EVIDENCE-b08-gripcomp-0820.png")

W, H = 832, 1216

# ---------------------------------------------------------------------------
# THE HAND. Traced by eye at 4x on the plate, OUTSIDE the fist's dark rim so the
# rim is inside the alpha (see the law above). Verified by rendering the polygon
# onto the plate and looking before any pixel moved.
# ---------------------------------------------------------------------------
FIST = [(576, 556), (596, 542), (624, 548), (634, 572), (633, 600),
        (620, 619), (596, 620), (578, 604), (572, 580)]

# Where it goes: onto the board's upper-left face. dx/dy is a TRANSLATION -- no
# rotation, no scale, no resample, so every moved pixel is a plate pixel.
DX, DY = 18, 91

# The authored L-wrist both hints already agree on. The moved hand's centroid is
# scored against it, and against the authored elbow it currently sits on.
LWRI = (621.6704, 668.4352)
LELB = (627.2, 579.7)
SHOULDER_Y = 491.0

# The board's own top edge, read off the plate at 4x. NOT used to cut anything
# -- the board is never touched -- only to assert that the moved hand actually
# lands ON it.
BOARD_TOP_L = (603, 666)
BOARD_TOP_R = (670, 681)

# An untouched patch of the SAME harness strap, used as the detail baseline for
# the vacancy fill. Above the hand, on the same band, same material, same light.
STRAP_BASELINE = (556, 500, 24, 32)   # x, y, w, h


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def poly_mask(points, w=W, h=H, grow=0):
    """Filled polygon as an L mask, optionally dilated by `grow` px.

    Dilation is a true Minkowski disc (the same reason author_b08_board_hint
    uses capsules rather than a wide PIL line): a wide outline leaves notches at
    the vertices and a first version of a check elsewhere in this tree failed on
    exactly one such pixel.
    """
    from PIL import Image, ImageDraw, ImageFilter
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(points, fill=255)
    if grow > 0:
        m = m.filter(ImageFilter.MaxFilter(2 * grow + 1)) if grow <= 10 else \
            m.filter(ImageFilter.MaxFilter(21)).filter(
                ImageFilter.MaxFilter(2 * (grow - 10) + 1))
    return m


def centroid(points):
    return (sum(p[0] for p in points) / len(points),
            sum(p[1] for p in points) / len(points))


# The harness strap's own axis, read off the plate: it runs from the shoulder
# clasp down through the old grip to the cuff. Everything in the vacancy -- the
# strap band AND the cream shirt beside it -- is near-CONSTANT along this
# direction and varies only across it.
STRAP_AXIS = (0.503, 0.863)


def fill_vacancy(arr, hole):
    """Continuation ALONG the strap's own axis, from the vacancy's own boundary.

    ROUND 1 OF THIS FILE DID IT PER ROW AND WAS REJECTED BY EYE, and the reason
    is worth keeping rather than deleting. A per-row ramp between the nearest
    untouched pixel on each side crosses TWO materials here -- brown strap on the
    left, cream shirt on the right -- so it interpolates strap into shirt and
    lands as beat 03's named failure: a ladder of horizontal dashes with the
    strap's own edge erased through the middle of it.

    THE CORRECTION IS NOT A DIFFERENT BLUR, IT IS A DIFFERENT DIRECTION. Beat
    03's law is that a fill may not assert structure it cannot see; it does not
    say the fill must run along the pixel grid. This strap is constant along its
    axis and varies across it, so continuing each pixel from the nearest
    untouched pixel UP-AXIS reproduces both materials in their own places and
    never mixes them. Streaks across a structure are the defect; continuation
    along one is the material.

    NO SETTLE BLUR -- composite-init-pattern.md 9b measured the settle pass as
    the largest single cause of the smear it cost a whole rung to find.
    """
    import numpy as np
    out = arr.astype(np.float64).copy()
    m = hole
    for _ in range(600):
        nb = np.zeros_like(out)
        nb[1:] += out[:-1]; nb[:-1] += out[1:]
        nb[:, 1:] += out[:, :-1]; nb[:, :-1] += out[:, 1:]
        cnt = np.zeros(hole.shape, dtype=np.float64)
        cnt[1:] += 1; cnt[:-1] += 1; cnt[:, 1:] += 1; cnt[:, :-1] += 1
        upd = nb / cnt[..., None]
        out[m] = upd[m]
    return out.round().clip(0, 255).astype(arr.dtype)


def build():
    """Returns (init RGB image, mask L image, a dict of measurements)."""
    import numpy as np
    from PIL import Image, ImageFilter

    plate = Image.open(PLATE).convert("RGB")
    if plate.size != (W, H):
        raise ValueError("plate is %r, expected %r" % (plate.size, (W, H)))
    a = np.asarray(plate).astype(np.uint8)

    src = poly_mask(FIST, grow=2)
    src_np = np.asarray(src) > 0
    moved = [(x + DX, y + DY) for x, y in FIST]
    dst_np = np.asarray(poly_mask(moved, grow=2)) > 0

    # ---- 1. lift the hand, as a rigid unit -------------------------------
    out = a.copy()
    hole = src_np & ~dst_np          # what the hand vacates and does not re-cover
    out = fill_vacancy(out, hole)

    # ---- 2. set it down ON TOP, so the fingers occlude the board's edge ---
    # A REAL ALPHA, NOT A BINARY PASTE. Round 1 pasted the polygon as a hard
    # stencil and the stair-stepped rasterisation edge was visible at 3x against
    # the skirt -- decal tell, rejected by eye. The alpha is the same polygon
    # blurred 1.2 px, so the silhouette lands sub-pixel and the moved unit's own
    # dark outline (which is INSIDE the polygon) still travels intact.
    shifted = np.zeros_like(a)
    ys, xs = np.nonzero(src_np)
    shifted[ys + DY, xs + DX] = a[ys, xs]
    # The blur tail is CLIPPED to a hard grow=4 boundary. Without the clip the
    # Gaussian leaks 1 level onto 140 px of board and skirt outside the unit --
    # invisible, and still a lie in the "nothing else changed" claim that C2 and
    # C9 exist to make. A soft edge inside a hard bound is both.
    al = np.asarray(
        poly_mask(moved, grow=2).filter(ImageFilter.GaussianBlur(1.2))
    ).astype(float)
    al = np.minimum(al, np.asarray(poly_mask(moved, grow=4)).astype(float))
    al = al[..., None] / 255.0
    out = (out.astype(float) * (1.0 - al) + shifted.astype(float) * al
           ).round().clip(0, 255).astype(np.uint8)

    init = Image.fromarray(out)

    # ---- 4. THE MASK: old site + new site + the board's top edge ----------
    # REMOVE THE CUE, NOT JUST THE OBJECT -- the old grip is inside the mask so
    # the pass re-renders the strap rather than rationalising a ghost.
    union = np.asarray(poly_mask(FIST, grow=12)) | np.asarray(
        poly_mask(moved, grow=12))
    # a tight band along the board's top edge, so the pass can draw the contact
    band = poly_mask([(BOARD_TOP_L[0] - 4, BOARD_TOP_L[1] - 14),
                      (BOARD_TOP_R[0] + 4, BOARD_TOP_R[1] - 14),
                      (BOARD_TOP_R[0] + 4, BOARD_TOP_R[1] + 16),
                      (BOARD_TOP_L[0] - 4, BOARD_TOP_L[1] + 16)], grow=6)
    union = np.maximum(union, np.asarray(band))
    mask = Image.fromarray(union).filter(ImageFilter.GaussianBlur(3))
    mask = mask.point(lambda v: 255 if v >= 64 else 0)
    mask = mask.filter(ImageFilter.GaussianBlur(3))

    mnp = np.asarray(mask) > 0
    diff = (np.abs(out.astype(int) - a.astype(int)).max(axis=2))
    meas = {
        "translation": (DX, DY),
        "src_centroid": centroid(FIST),
        "dst_centroid": centroid(moved),
        "moved_px": int(src_np.sum()),
        "hole_px": int(hole.sum()),
        "changed_px": int((diff > 0).sum()),
        "changed_outside_mask": int((diff > 0)[~mnp].sum()),
        "maxdiff_outside_mask": int(diff[~mnp].max()),
        "mask_px": int(mnp.sum()),
        "mask_frac": float(mnp.mean()),
        "mask_bbox": tuple(int(v) for v in Image.fromarray(
            (mnp * 255).astype(np.uint8)).getbbox()),
    }
    return init, mask, meas, a, out, hole


def grad_energy(arr, box=None, m=None):
    """Mean |gradient| -- the ONLY statistic that sees a smear (9b)."""
    import numpy as np
    g = arr.astype(float).mean(axis=2) if arr.ndim == 3 else arr.astype(float)
    gy, gx = np.gradient(g)
    e = np.hypot(gx, gy)
    if box is not None:
        x, y, w, h = box
        return float(e[y:y + h, x:x + w].mean())
    return float(e[m].mean())


def selftest():
    import numpy as np
    fails = []

    def check(label, ok):
        print("  %s %s" % ("ok  " if ok else "FAIL", label))
        if not ok:
            fails.append(label)

    print("  plate sha %s" % sha256_file(PLATE))
    init, mask, m, a, out, hole = build()

    # C1 -- THE EDIT IS LOCAL. Every clause scale30 passes lives outside.
    check("C1 nothing changed outside the mask (maxdiff %d, %d px)"
          % (m["maxdiff_outside_mask"], m["changed_outside_mask"]),
          m["maxdiff_outside_mask"] == 0)

    # C2 -- THE BOARD IS NOT TOUCHED, EXCEPT WHERE THE HAND NOW COVERS IT.
    # The carve-out is the point of the rung, not a tolerance: a hand that does
    # not overwrite any board pixel is a hand floating in front of one. What
    # must be byte-identical is the board OUTSIDE the grip -- its three free
    # edges, its face and its whole lower two thirds, which is where B4a's
    # four passing verdicts actually live.
    moved = [(x + DX, y + DY) for x, y in FIST]
    board = (np.asarray(poly_mask(
        [(BOARD_TOP_L[0] + 6, BOARD_TOP_L[1] + 22),
         (BOARD_TOP_R[0] - 6, BOARD_TOP_R[1] + 22),
         (659, 806), (601, 792)])) > 0) & ~(
        np.asarray(poly_mask(moved, grow=4)) > 0)
    d = np.abs(out.astype(int) - a.astype(int)).max(axis=2)
    check("C2 the BOARD OUTSIDE THE GRIP is byte-identical -- the clause that "
          "passed four times is not re-opened (maxdiff %d over %d px)"
          % (d[board].max(), board.sum()), d[board].max() == 0)

    # C3 -- THE OUTLINE TRAVELLED. A moved fill with no rim is a decal.
    inner = np.asarray(poly_mask(moved)) > 0
    L = out.astype(float).mean(axis=2)
    dark = (L < 110) & inner
    check("C3 the moved unit carries its own dark rim -- %d dark px inside it, "
          "so the outline is in the alpha" % dark.sum(), dark.sum() > 200)

    # C4 -- THE FILL HAS DETAIL. The one statistic a smear cannot pass.
    # THE BASELINE IS THE HOLE'S OWN 10 px RING, not a hand-picked patch. A
    # patch is a choice and this one was wrong on the first try: the obvious
    # strap swatch straddled the gold clasp and read gradient 33, twenty times
    # the strap's true interior, which would have failed an honest fill. The
    # ring is the same two materials in the same proportions, immediately
    # adjacent, untouched by this edit -- and it cannot be shopped for.
    from PIL import Image as _I, ImageFilter as _F
    grown = np.asarray(_I.fromarray((hole * 255).astype(np.uint8)).filter(
        _F.MaxFilter(21))) > 0
    ring = grown & ~hole & (d == 0)
    base = grad_energy(a, m=ring)
    got = grad_energy(out, m=hole)
    share = got / base if base else 0.0
    print("     vacancy fill gradient energy %.2f against its own untouched "
          "%d px ring at %.2f = %.0f%%" % (got, ring.sum(), base, 100 * share))
    check("C4 the vacancy fill reaches 45%% of its own ring's detail (9b's "
          "measured bar; every variant a look rejected sat below it)",
          share >= 0.45)

    # C5 -- THE HAND LANDS ON THE BOARD, AND AT THE COORDINATE BOTH HINTS AGREE
    cx, cy = m["dst_centroid"]
    d_wri = float(np.hypot(cx - LWRI[0], cy - LWRI[1]))
    d_elb = float(np.hypot(cx - LELB[0], cy - LELB[1]))
    sx, sy = m["src_centroid"]
    print("     hand centroid (%.1f,%.1f) -> (%.1f,%.1f); to authored WRIST "
          "%.1f px (was %.1f), to authored ELBOW %.1f px (was %.1f)"
          % (sx, sy, cx, cy, d_wri, d_elb,
             float(np.hypot(sx - LWRI[0], sy - LWRI[1])),
             float(np.hypot(sx - LELB[0], sy - LELB[1]))))
    check("C5 the moved hand is CLOSER TO THE AUTHORED WRIST THAN TO THE "
          "AUTHORED ELBOW -- the whole defect of the parent inverted",
          d_wri < d_elb and d_wri <= 30.0)

    # C6 -- IT OVERLAPS THE BOARD'S TOP EDGE. A hand hovering above the edge is
    # not a grip; a hand behind it is not one either. Assert the crossing.
    hand = np.asarray(poly_mask(moved)) > 0
    above = hand[:int(min(BOARD_TOP_L[1], BOARD_TOP_R[1]))].sum()
    below = hand[int(max(BOARD_TOP_L[1], BOARD_TOP_R[1])):].sum()
    print("     hand pixels above the board's top edge %d, below it %d" %
          (above, below))
    check("C6 the hand STRADDLES the board's top edge, so its fingers occlude "
          "the edge rather than hovering over it or hiding behind it",
          above > 200 and below > 200)

    # C7 -- B4a's geometry survives: the board is still LOWERED.
    check("C7 the board's top edge (%.1f) is still below the shoulder line "
          "(%.1f) -- it never moved" % (BOARD_TOP_L[1], SHOULDER_Y),
          BOARD_TOP_L[1] > SHOULDER_Y)

    # C8 -- THE MASK IS TIGHT, AND IT DOES NOT REACH THE CLAUSES THAT PASS.
    mnp = np.asarray(mask) > 0
    print("     mask %d px, %.2f%% of frame, bbox %r"
          % (m["mask_px"], 100 * m["mask_frac"], m["mask_bbox"]))
    faces = {"guard face": (531, 355, 601, 420), "goblin face": (120, 440, 220, 530),
             "guard pointing hand": (255, 640, 360, 730),
             "goblin body": (60, 430, 260, 1140)}
    for name, (x0, y0, x1, y1) in faces.items():
        check("C8 the mask does not reach the %s" % name,
              not mnp[y0:y1, x0:x1].any())
    check("C8 the mask is under 3%% of the frame", m["mask_frac"] < 0.03)

    # C9 -- NOTHING WAS DRAWN. Every changed pixel is inside the union of the
    # two hand footprints and the ring; no stroke was invented anywhere else.
    allowed = ((np.asarray(poly_mask(FIST, grow=4)) > 0)
               | (np.asarray(poly_mask(moved, grow=4)) > 0))
    stray = (d > 0) & ~allowed
    check("C9 every changed pixel lies in the hand's old or new footprint -- "
          "NOT ONE stroke was drawn anywhere (%d stray px)" % stray.sum(),
          stray.sum() == 0)

    print(("SELFTEST FAIL: %d" % len(fails)) if fails else "SELFTEST PASS")
    return 1 if fails else 0


def write():
    from PIL import Image, ImageDraw
    init, mask, m, a, out, hole = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    init.save(OUT_INIT, "PNG")
    mask.save(OUT_MASK, "PNG")

    # evidence: plate | composite | composite+mask, at 3x on the region
    box = (540, 500, 720, 850)
    ims = []
    for im in (Image.open(PLATE).convert("RGB"), init):
        c = im.crop(box)
        ims.append(c.resize((c.width * 3, c.height * 3), Image.LANCZOS))
    ov = init.copy()
    red = Image.new("RGB", ov.size, (255, 40, 40))
    ov = Image.composite(Image.blend(ov, red, 0.35), ov, mask)
    c = ov.crop(box)
    ims.append(c.resize((c.width * 3, c.height * 3), Image.LANCZOS))
    w = sum(i.width for i in ims) + 24
    sheet = Image.new("RGB", (w, ims[0].height + 28), (18, 18, 18))
    ImageDraw.Draw(sheet).text(
        (6, 6), "b08 gripcomp 3x -- plate | composite | mask overlay", fill=(235, 235, 235))
    x = 0
    for i in ims:
        sheet.paste(i, (x, 28)); x += i.width + 12
    sheet.save(OUT_EVID, "PNG")

    for k, v in m.items():
        print("  %s: %s" % (k, v))
    print("  init  %s\n        sha256 %s" % (OUT_INIT, sha256_file(OUT_INIT)))
    print("  mask  %s\n        sha256 %s" % (OUT_MASK, sha256_file(OUT_MASK)))
    print("  evid  %s" % OUT_EVID)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.write:
        rc = selftest()
        if rc:
            print("!! refusing to write: the selftest failed")
            return rc
        return write()
    ap.error("--selftest or --write")


if __name__ == "__main__":
    raise SystemExit(main())
