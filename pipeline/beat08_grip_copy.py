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

# THE GOLD CHEST CLASP IS HELD OUT OF THE MASK, AS FAR AS IT CAN BE. It sits
# directly above the fist the pass has to delete, and an unmasked first draft put
# 21.7% of it inside the mask for no gain: the pass does not need to redraw a
# landmark in order to draw the strap beneath it, and a distinctive wardrobe
# object half-inside a mask is how B6 gets re-opened by accident.
#
# THE CARVE-OUT IS NOT ABSOLUTE AND THE REASON IS GEOMETRY, NOT TOLERANCE. The
# clasp and the fist are adjacent objects: freezing every clasp pixel and giving
# the fist its 6 px of deletion margin are incompatible where they touch. The
# fist's coverage is the POINT of this rung, so the carve-out YIELDS there --
# it is (clasp gold, dilated 2) MINUS (the fist's own required margin). What
# that costs is printed by K15 rather than rounded to zero.
CLASP_BOX = (555, 490, 605, 545)    # where to look for the clasp's gold, at 6x

STRENGTH = 0.99
STRENGTH_ARGUMENT = """\
CHOSEN: 0.99, at 40 steps and cfg 7.5. ONE SAMPLE.

THE FIRST DRAFT OF THIS ARGUMENT SAID 0.55 AND IT WAS WRONG, from reasoning
about plain img2img when this is not that. `inpaint_fruit.py`'s own docstring,
sourced to the diffusers 0.29.2 pipeline it loads, settles it:

    "`strength` must be high to ADD something. It is not the img2img case; the
     unmasked region is restored every step by the blend above, so a high
     strength costs nothing outside the mask."

The blend it means is SDXL inpaint's latent branch, taken because animagine has
no inpainting variant and its UNet has 4 input channels:

    latents = (1 - init_mask) * init_latents_proper + init_mask * latents

and the same file records the measurement that kills the middle of the range:
adding an object the init lacks got **0 of 12 at strength 0.35 or 0.55**.

1. WHY NOT 0.30, THE HOUSE DEFAULT (66 of the specs in this tree).
   `composite-init-pattern.md`: an inpaint pass runs only `int(steps x
   strength)` of its schedule -- at 40 steps, 0.30 is TWELVE steps. That is
   the regime chosen precisely because it PRESERVES structure, and every
   sibling that used it was INTEGRATING something already drawn into the init
   (b13's sapling, b15/b19's clone fills, beat 03's ramp given blade texture).
   NONE of them had to DELETE a fully-inked object with its own dark outline
   and CREATE a forearm that is not in the plate at all. 0.30 hands the fist
   twelve steps and a latent that still contains it, and gets a dented fist.

2. WHY 0.99 IS NOT THE RISK IT LOOKS LIKE, AND THIS IS THE PART I HAD BACKWARDS.
   I worried a near-fresh draw would wreck the copied digits. It cannot: the
   digits are OUTSIDE the mask, and the latent blend above restores every
   unmasked pixel AT EVERY STEP. So they are safe by construction of the
   sampler, not by the size of the knob -- a strictly stronger guarantee than
   the one K3 was written to give, and it holds at any strength. The 12 px
   contact rim IS inside the mask and IS redrawn, which is what it was opened
   for, and it is redrawn with the restored digits visible as context on every
   step rather than against a neighbour the model cannot see.

3. THE ONE LEAK, NAMED. `--blur 8` softens the mask edge, so the outermost few
   px of the protected digits take a fraction of the pass. That is wanted --
   a hard protect boundary is how you get a seam -- but it is a leak and it is
   stated rather than denied. If the digits come back mushy at their rim, the
   next rung lowers `--blur`, not the strength.

4. WHAT IT COSTS AGAINST B6, B8 AND THE WARDROBE -- AND WHY §21'S FEAR IS
   SMALLER THAN IT LOOKED, MEASURED. §21 warned a higher strength "re-opens
   the exact clauses (B6, B8, the wardrobe) the 0.30 number was bought with".
   Those clauses were bought at the CONDITIONING scale (`--scale2`) on a
   WHOLE-FRAME txt2img render -- §19's table is scale2 0.3/0.5/0.8, not a
   denoise strength. A MASKED pass cannot write one pixel outside its mask at
   ANY strength -- that is the same latent-blend property as part 2, and it is
   the pipeline's behaviour rather than a hope -- so the price is not a guess
   about the knob; it is the item's overlap with 1.82% of the frame, and K15
   prints it:

       B8 canon hair          0 of 18200 px reachable  -- 0.0%, at any strength
       gold chest clasp      11 of   994 px            --  1.1%, all of it
                                                          inside the fist's own
                                                          6 px deletion margin
       gold belt buckle     382 of  5366 px            --  7.1%
       B6 white sash        108 of   332 px            -- 32.5%
       B6 cream shirt      5750 of 28573 px            -- 20.1%

   B8 IS UNTOUCHABLE AND THAT WAS THE LOUDEST OF THE THREE. What is genuinely
   at risk is B6: a fifth of the cream shirt and a third of the white sash sit
   in the corridor the arm has to be drawn through, and at 0.99 the sampler
   redraws that fifth from near-noise -- it may merge shirt into wrap the way
   `--scale2` 0.5 did, inside the corridor. THAT IS THE REAL PRICE OF THIS
   RUNG, it is the reason the corridor was widened knowingly, and it is
   pre-registered as a named fail mode rather than discovered afterwards."""


def _erode(m, r):
    from PIL import Image, ImageFilter
    import numpy as np
    im = Image.fromarray((m * 255).astype("uint8"))
    while r > 0:
        k = min(r, 10)
        im = im.filter(ImageFilter.MinFilter(2 * k + 1))
        r -= k
    return np.asarray(im) > 0


def clasp_gold(a, grow=2):
    """The chest clasp's own gold pixels, dilated -- found, not boxed."""
    import numpy as np
    from PIL import Image, ImageFilter
    R, G, B = (a[:, :, i].astype(int) for i in range(3))
    g = (R > 150) & (G > 110) & (B < 130) & ((R - B) > 60)
    x0, y0, x1, y1 = CLASP_BOX
    z = np.zeros(g.shape, bool)
    z[y0:y1, x0:x1] = True
    g = g & z
    return np.asarray(Image.fromarray((g * 255).astype("uint8")).filter(
        ImageFilter.MaxFilter(2 * grow + 1))) > 0


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
    keep_clasp = clasp_gold(a) & ~(np.asarray(poly_mask(FIST, grow=6)) > 0)
    mnp = (np.asarray(soft) > 0) & ~protect & ~keep_clasp
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

    # K15 -- THE WARDROBE PRICE, MEASURED RATHER THAN ASSERTED. §21 refused to
    # file this rung partly because a higher strength "re-opens the exact
    # clauses (B6, B8, the wardrobe) the 0.30 number was bought with". That
    # fear was formed on a WHOLE-FRAME txt2img render where the knob was the
    # conditioning scale; a MASKED pass cannot write a pixel outside its mask,
    # whatever its denoise strength, so the price is not a guess about strength
    # -- it is exactly the item's overlap with 1.88% of the frame. Printed here
    # so the spec's argument quotes a measurement.
    lum = a.astype(float).mean(axis=2)
    Rc, Gc, Bc = a[:, :, 0].astype(int), a[:, :, 1].astype(int), a[:, :, 2].astype(int)
    gold = (Rc > 150) & (Gc > 110) & (Bc < 130) & ((Rc - Bc) > 60)
    def box(x0, y0, x1, y1):
        z = np.zeros((H, W), bool); z[y0:y1, x0:x1] = True; return z
    items = [
        ("B8 canon hair (the head)", box(500, 300, 640, 430)),
        ("gold chest clasp", gold & box(555, 490, 605, 545)),
        ("gold belt buckle", gold & box(495, 640, 600, 760)),
        ("B6 white sash", (lum > 225) & (np.abs(Rc - Bc) < 25) & box(380, 655, 700, 700)),
        ("B6 cream shirt", (lum > 200) & ((Rc - Bc) > 25) & box(380, 430, 720, 670)),
    ]
    for nm, it in items:
        n, inm = int(it.sum()), int((it & mnp).sum())
        print("     %-26s %6d px, %5d reachable by the pass (%.1f%%)"
              % (nm, n, inm, 100.0 * inm / max(n, 1)))
    hair = items[0][1]
    check("K15 B8's canon hair is UNREACHABLE -- 0 px of the head is in the "
          "mask, so the clause §21 feared a higher strength would re-open "
          "cannot move at any strength", not mnp[hair].any())
    clasp = items[1][1]
    kept = clasp_gold(a) & ~(np.asarray(poly_mask(FIST, grow=6)) > 0)
    left = int((clasp & mnp).sum())
    check("K15 the gold chest clasp is frozen except where the fist's own 6 px "
          "deletion margin overtakes it -- %d of %d gold px reachable, down "
          "from 216 uncarved, and every one of them is inside that margin"
          % (left, int(clasp.sum())),
          left <= 40 and not (clasp & mnp & kept).any())

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
