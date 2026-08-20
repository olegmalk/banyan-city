#!/usr/bin/env python3
"""beat 08 -- COPY the guard's drawn fist to the board; let the sampler delete
the original from real pixels. The rung `b08-arm-route-0819.md` §21 named and
refused to file until C4 had a replacement.

WHAT §21 RULED, AND WHAT IT REFUSED
===================================
`ep2-b08-gripcomp-0820` MOVED the fist 91 px. Everything outside the mask
survived by construction, the grip clause came half-bought -- real drawn
fingers straddling the board's top edge, centroid 4.9 px from the authored
L-wrist against the parent's 90.5 -- and the rung still failed, twice over:

  * THE VACANCY. Moving the hand opened 4489 px in a harness-strap / cuff /
    shirt junction with a gold clasp on its top edge, and the plate contains
    no clean source for that junction. THREE fill families were tried
    (per-row ramp, axial continuation, isotropic diffusion) and all three left
    an artifact an eye names instantly. §21's rule: *composite-then-inpaint is
    licensed where the vacancy's material is continuous and unstructured; it
    is not a licence to relocate a part of a figure across its own clothing.*
  * THE DECAL. `held, not tucked` failed anyway: a stair-stepped octagonal rim
    against the skirt, the unit sitting ON the board's undisturbed outline
    rather than closing around it, no contact shading. "A sticker of a hand."

**THE VACANCY SHOULD NOT EXIST.** §21's own prescription, quoted: *"the honest
version is to COPY the fist to the board edge and leave the original in the
init, inside the mask, so the sampler removes it from real strap pixels
instead of being handed a fabricated fill to rationalise."* That is this file.
No fill function exists in it, and that is the entire point.

THE THREE THINGS THE MASK HAS TO DO, AND WHY THE THIRD IS NOT OPTIONAL
======================================================================
 1. **COVER THE ORIGINAL FIST**, generously, so the pass rebuilds the strap
    junction from the real strap, cuff and clasp that surround it -- the
    material we could not fabricate is exactly the material it can see.
 2. **OPEN A RIM AROUND THE COPY**, so the pass draws the contact: the
    occlusion at the board's edge and the shadow under the fingers that §21
    said the translation could not invent. The copy's INTERIOR is held OUT of
    the mask, so the drawn digits -- the one thing here that must not be
    re-invented -- survive by construction, the same way the parent's clauses
    did.
 3. **OPEN THE FOREARM CORRIDOR from the authored elbow to the authored
    wrist.** This is the clause that was missing and it is why the parent read
    as a sticker. The plate draws the guard's hand AT THE AUTHORED ELBOW
    (LELB 627.2,579.7) -- that IS the parent's defect -- and the pose hint
    puts the wrist 89 px below it at the board (LWRI 621.6,668.4). Delete the
    fist and paste a copy at the wrist and the cream sleeve still ends in
    nothing while a hand floats below it. The arm has to be re-routed, the
    openpose hint already encodes elbow->wrist, and a corridor is the only
    way the pass is allowed to draw it.

WHAT THIS COSTS, STATED BEFORE IT IS SPENT
==========================================
The corridor is the widest part of the mask and it is bought knowingly. §20
priced the mask in `(strength x ink)`; §21 named the tradeoff and refused to
turn it as a knob:

    "a 0.30 pass does not delete a hand -- 0.30 is the strength that exists to
     preserve structure -- so the rung has to choose a higher strength inside
     the mask and that re-opens the exact clauses (B6, B8, the wardrobe) the
     0.30 number was bought with."

The chosen strength, and the argument for it against those clauses, is in
`STRENGTH_ARGUMENT` below and in the job spec. It is an argued tradeoff, not a
default.

HOW IT IS JUDGED ON LANDING
===========================
NOT by C4. §21 retired C4 on this vacancy: it certified the corduroy comb at
89%. The landed result is judged by **C4'** -- `pipeline/fill_quality.py`,
D >= 0.45 AND N >= 0.25 AND F <= 2.60, whose false-positive rate on this very
plate is a measured 3.0% -- run on the region the pass repainted where the
original fist was. Plus every scale30 clause, unchanged, on the pixels outside
the mask.

    python3 pipeline/beat08_grip_copy.py --selftest
    python3 pipeline/beat08_grip_copy.py --write
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from beat08_grip_composite import (  # noqa: E402  -- ONE source for the geometry
    BOARD_TOP_L, BOARD_TOP_R, DX, DY, FIST, H, LELB, LWRI, PLATE, SHOULDER_Y,
    W, centroid, poly_mask, sha256_file,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB = "ep2-b08-fistcopy-0820"
OUT_DIR = os.path.join(REPO, "farm-out", JOB)
OUT_INIT = os.path.join(OUT_DIR, "08-first-citizen-fistcopy-0820.png")
OUT_MASK = os.path.join(OUT_DIR, "08-first-citizen-fistcopy-mask-0820.png")
OUT_ERASE = os.path.join(OUT_DIR, "08-first-citizen-fistcopy-erase-0820.png")
OUT_EVID = os.path.join(OUT_DIR, "EVIDENCE-b08-fistcopy-0820.png")

# --- the mask's dials, each one a stated choice -----------------------------
OLD_GROW = 14      # margin around the fist the pass must delete
ARM_R = 24         # forearm corridor half-width, elbow -> wrist
RIM_OUT = 8        # px outside the copy the pass may repaint (contact/occlusion)
RIM_IN = 4         # px inside the copy's outline it may repaint (the closing edge)
BAND_H = 14        # the board's top-edge contact band

STRENGTH_ARGUMENT = """\
STRENGTH: pending the (strength x ink) table -- see the job spec. 0.30 is
ruled out by §21: it is the strength that exists to PRESERVE structure and it
cannot delete a hand."""


def _erode(m, r):
    from PIL import Image, ImageFilter
    import numpy as np
    im = Image.fromarray((m * 255).astype("uint8"))
    while r > 0:
        k = min(r, 10)
        im = im.filter(ImageFilter.MinFilter(2 * k + 1))
        r -= k
    return np.asarray(im) > 0


def capsule(p0, p1, r):
    """A true capsule between two points: a hairline quad grown by a disc."""
    import numpy as np
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    n = np.hypot(dx, dy)
    px, py = -dy / n * 1.5, dx / n * 1.5
    quad = [(x0 + px, y0 + py), (x1 + px, y1 + py),
            (x1 - px, y1 - py), (x0 - px, y0 - py)]
    return np.asarray(poly_mask([(int(round(a)), int(round(b)))
                                 for a, b in quad], grow=r)) > 0


def build():
    """Returns (init RGB, mask L, erase-region L, measurements, plate, out)."""
    import numpy as np
    from PIL import Image, ImageFilter

    plate = Image.open(PLATE).convert("RGB")
    if plate.size != (W, H):
        raise ValueError("plate is %r, expected %r" % (plate.size, (W, H)))
    a = np.asarray(plate).astype(np.uint8)

    src_np = np.asarray(poly_mask(FIST, grow=2)) > 0
    moved = [(x + DX, y + DY) for x, y in FIST]
    moved_poly = np.asarray(poly_mask(moved, grow=2)) > 0

    # ---- 1. COPY. The original is NOT lifted; there is no hole and no fill --
    shifted = np.zeros_like(a)
    ys, xs = np.nonzero(src_np)
    shifted[ys + DY, xs + DX] = a[ys, xs]
    # The same real alpha the parent earned: the polygon blurred 1.2 px so the
    # silhouette lands sub-pixel and the unit's own dark outline (inside the
    # polygon) travels intact -- clipped to a hard grow=4 bound so the
    # Gaussian tail cannot leak a level onto board or skirt outside it.
    al = np.asarray(
        poly_mask(moved, grow=2).filter(ImageFilter.GaussianBlur(1.2))
    ).astype(float)
    al = np.minimum(al, np.asarray(poly_mask(moved, grow=4)).astype(float))
    al = al[..., None] / 255.0
    out = (a.astype(float) * (1.0 - al) + shifted.astype(float) * al
           ).round().clip(0, 255).astype(np.uint8)
    init = Image.fromarray(out)

    # ---- 2. THE MASK -------------------------------------------------------
    old = np.asarray(poly_mask(FIST, grow=OLD_GROW)) > 0
    arm = capsule(LELB, LWRI, ARM_R)
    rim = np.asarray(poly_mask(moved, grow=RIM_OUT)) > 0
    band = np.asarray(poly_mask(
        [(BOARD_TOP_L[0] - 4, BOARD_TOP_L[1] - BAND_H),
         (BOARD_TOP_R[0] + 4, BOARD_TOP_R[1] - BAND_H),
         (BOARD_TOP_R[0] + 4, BOARD_TOP_R[1] + BAND_H + 2),
         (BOARD_TOP_L[0] - 4, BOARD_TOP_L[1] + BAND_H + 2)], grow=6)) > 0

    union = old | arm | rim | band
    soft = Image.fromarray((union * 255).astype(np.uint8)
                           ).filter(ImageFilter.GaussianBlur(3))
    soft = soft.point(lambda v: 255 if v >= 64 else 0
                      ).filter(ImageFilter.GaussianBlur(3))

    # THE DIGITS ARE CARVED BACK OUT, LAST AND HARD. A soft edge here would
    # leak the pass's strength onto the one thing in this rung that cannot be
    # re-invented; the rim above is the blend zone, and it is outside this.
    protect = _erode(np.asarray(poly_mask(moved)) > 0, RIM_IN)
    mnp = (np.asarray(soft) > 0) & ~protect
    mask = Image.fromarray((mnp * 255).astype(np.uint8))

    # The sub-region a landed result is scored on by C4': where the fist WAS.
    erase = old & ~np.asarray(poly_mask(moved, grow=RIM_OUT + 2)) > 0
    erase = (old & mnp) & ~(np.asarray(poly_mask(moved, grow=RIM_OUT + 2)) > 0)

    d = np.abs(out.astype(int) - a.astype(int)).max(axis=2)
    meas = {
        "translation": (DX, DY),
        "src_centroid": centroid(FIST),
        "dst_centroid": centroid(moved),
        "copied_px": int(src_np.sum()),
        "changed_px": int((d > 0).sum()),
        "changed_outside_mask": int((d > 0)[~mnp].sum()),
        "maxdiff_outside_mask": int(d[~mnp].max()),
        "mask_px": int(mnp.sum()),
        "mask_frac": float(mnp.mean()),
        "protect_px": int(protect.sum()),
        "erase_px": int(erase.sum()),
        "old_px": int(old.sum()), "arm_px": int(arm.sum()),
        "mask_bbox": tuple(int(v) for v in Image.fromarray(
            (mnp * 255).astype(np.uint8)).getbbox()),
    }
    return init, mask, Image.fromarray((erase * 255).astype(np.uint8)), \
        meas, a, out, mnp, protect, erase


def selftest():
    import numpy as np
    fails = []

    def check(label, ok):
        print("  %s %s" % ("ok  " if ok else "FAIL", label))
        if not ok:
            fails.append(label)

    print("  plate sha %s" % sha256_file(PLATE))
    init, mask, erasei, m, a, out, mnp, protect, erase = build()
    d = np.abs(out.astype(int) - a.astype(int)).max(axis=2)
    moved = [(x + DX, y + DY) for x, y in FIST]

    # K1 -- THERE IS NO VACANCY. The whole reason this rung exists.
    src_np = np.asarray(poly_mask(FIST, grow=2)) > 0
    vac = src_np & ~(np.asarray(poly_mask(moved, grow=2)) > 0)
    untouched = int((d[vac] == 0).sum())
    print("     the 4489 px §21 could not fill: %d of %d still byte-identical "
          "plate" % (untouched, int(vac.sum())))
    check("K1 THE ORIGINAL FIST IS STILL THERE -- no hole was opened, no fill "
          "function was called, the pass deletes it from real pixels",
          untouched == int(vac.sum()))

    # K2 -- the copy is plate pixels, not a re-render
    inner = _erode(np.asarray(poly_mask(moved)) > 0, 3)
    ys, xs = np.nonzero(inner)
    exact = int((out[ys, xs] == a[ys - DY, xs - DX]).all(axis=1).sum())
    check("K2 the copy's interior is BYTE-IDENTICAL to the plate's own fist "
          "(%d of %d px) -- a translation, no rotation, scale or resample"
          % (exact, len(ys)), exact == len(ys))

    # K3 -- the digits are protected from the pass
    check("K3 the copy's drawn digits are OUTSIDE the mask (%d px protected) "
          "-- the one thing here that must not be re-invented"
          % m["protect_px"], not mnp[protect].any() and m["protect_px"] > 1200)

    # K4 -- and its rim is INSIDE it, so contact can be drawn
    rim = (np.asarray(poly_mask(moved, grow=RIM_OUT)) > 0) & ~protect
    frac = float(mnp[rim].mean())
    check("K4 a %d px band around the copy IS in the mask (%.0f%% of it) -- "
          "the occlusion and contact shading §21 said a translation could not "
          "invent" % (RIM_OUT + RIM_IN, 100 * frac), frac > 0.95)

    # K5 -- the original is fully inside the mask, with margin
    old_core = np.asarray(poly_mask(FIST, grow=6)) > 0
    check("K5 the original fist is WHOLLY inside the mask with 6 px of margin "
          "-- the pass can delete it, not merely dent it",
          bool(mnp[old_core].all()))

    # K6 -- the forearm corridor is open, EXCEPT where it runs into the hand
    # it is meant to reach. The corridor ends at the wrist and the wrist is the
    # protected copy; carving the digits back out of it is K3 doing its job,
    # not a gap, so the clause is measured on the corridor that is not hand.
    arm = capsule(LELB, LWRI, ARM_R - 6) & ~protect
    check("K6 the forearm corridor elbow(%.0f,%.0f)->wrist(%.0f,%.0f) is open "
          "(%.0f%% of the %d px of it that is not the protected hand) -- "
          "without it the sleeve ends in nothing and the hand floats"
          % (LELB[0], LELB[1], LWRI[0], LWRI[1],
             100 * float(mnp[arm].mean()), int(arm.sum())),
          float(mnp[arm].mean()) > 0.95)

    # K7 -- the grip geometry §21 half-bought, unchanged
    cx, cy = m["dst_centroid"]
    d_wri = float(np.hypot(cx - LWRI[0], cy - LWRI[1]))
    d_elb = float(np.hypot(cx - LELB[0], cy - LELB[1]))
    check("K7 the copy's centroid is %.1f px from the authored WRIST and %.1f "
          "from the authored ELBOW -- the parent's defect stays inverted"
          % (d_wri, d_elb), d_wri < d_elb and d_wri <= 30.0)

    hand = np.asarray(poly_mask(moved)) > 0
    above = int(hand[:int(min(BOARD_TOP_L[1], BOARD_TOP_R[1]))].sum())
    below = int(hand[int(max(BOARD_TOP_L[1], BOARD_TOP_R[1])):].sum())
    check("K8 the copy STRADDLES the board's top edge (%d px above, %d below)"
          % (above, below), above > 200 and below > 200)
    check("K9 the board's top edge (%.0f) is still below the shoulder line "
          "(%.0f) -- B4a's geometry never moved" % (BOARD_TOP_L[1], SHOULDER_Y),
          BOARD_TOP_L[1] > SHOULDER_Y)

    # K10 -- THE ONE CLAUSE THIS RUNG CANNOT STATE THE PARENT'S WAY, AND WHY.
    # The parent asserted "nothing changed outside the mask, maxdiff 0". Here
    # the composite deliberately changes %d px outside it: the copy's own
    # protected interior. That is not a relaxation, it is the design -- those
    # pixels are held out of the mask precisely so the pass CANNOT touch the
    # drawn digits, which means they also appear verbatim in the output. The
    # honest form of the clause is therefore: every changed pixel outside the
    # mask is inside the protected copy, and every one of them is a byte-exact
    # plate pixel (K2). The decal risk that comes with verbatim pixels is paid
    # for by K4 -- the rim around them IS in the mask, so the pass draws the
    # contact edge that a translation alone cannot invent.
    out_of_mask = (d > 0) & ~mnp
    check("K10 every changed pixel outside the mask (%d) is inside the "
          "PROTECTED copy -- the edit is local and the digits are why"
          % int(out_of_mask.sum()),
          int(out_of_mask.sum()) > 0 and not (out_of_mask & ~protect).any())
    allowed = np.asarray(poly_mask(moved, grow=4)) > 0
    stray = int(((d > 0) & ~allowed).sum())
    check("K11 every changed pixel is inside the copy's footprint -- NOT ONE "
          "stroke was drawn anywhere (%d stray)" % stray, stray == 0)

    # K12 -- the mask does not reach the clauses that already pass
    print("     mask %d px, %.2f%% of frame, bbox %r; old-site %d px, corridor "
          "%d px, C4' erase region %d px"
          % (m["mask_px"], 100 * m["mask_frac"], m["mask_bbox"],
             m["old_px"], m["arm_px"], m["erase_px"]))
    for name, (x0, y0, x1, y1) in {
            "guard face": (531, 355, 601, 420),
            "goblin face": (120, 440, 220, 530),
            "guard pointing hand": (255, 640, 360, 730),
            "goblin body": (60, 430, 260, 1140)}.items():
        check("K12 the mask does not reach the %s" % name,
              not mnp[y0:y1, x0:x1].any())
    check("K13 the mask is under 4%% of the frame -- it is WIDER than the "
          "parent's by the corridor, and that is the price named up front",
          m["mask_frac"] < 0.04)

    # K14 -- the region C4' will score on landing is big enough to be scorable
    import fill_quality as Q
    check("K14 the C4' erase region is %d px, above the %d px floor below "
          "which fill_quality REFUSES to score" % (m["erase_px"], Q.MIN_REGION),
          m["erase_px"] >= Q.MIN_REGION)

    print(("SELFTEST FAIL: %d" % len(fails)) if fails else "SELFTEST PASS")
    return 1 if fails else 0


def write():
    from PIL import Image
    init, mask, erasei, m, a, out, mnp, protect, erase = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    init.save(OUT_INIT, "PNG")
    mask.save(OUT_MASK, "PNG")
    erasei.save(OUT_ERASE, "PNG")

    # a 4x contact sheet: plate | init | mask over init
    import numpy as np
    box = (540, 500, 700, 740)
    Z = 4
    tiles = [Image.fromarray(a).crop(box), init.crop(box)]
    ov = np.asarray(init).astype(float).copy()
    ov[mnp] = ov[mnp] * 0.45 + np.array([255, 40, 40]) * 0.55
    tiles.append(Image.fromarray(ov.round().astype(np.uint8)).crop(box))
    w, h = box[2] - box[0], box[3] - box[1]
    sheet = Image.new("RGB", (3 * w * Z + 32, h * Z + 16), (16, 16, 18))
    for i, t in enumerate(tiles):
        sheet.paste(t.resize((w * Z, h * Z), Image.NEAREST),
                    (8 + i * (w * Z + 8), 8))
    sheet.save(OUT_EVID, "PNG")

    print("  init  %s\n        sha256 %s" % (OUT_INIT, sha256_file(OUT_INIT)))
    print("  mask  %s\n        sha256 %s" % (OUT_MASK, sha256_file(OUT_MASK)))
    print("  erase %s\n        sha256 %s" % (OUT_ERASE, sha256_file(OUT_ERASE)))
    print("  evid  %s" % OUT_EVID)
    for k in sorted(m):
        print("  %-22s %s" % (k, m[k]))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
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
    sys.exit(main())
