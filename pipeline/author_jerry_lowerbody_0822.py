#!/usr/bin/env python3
r"""THE LOWER-BODY ROUTE: keep his face as PIXELS, generate his legs as a POSE.

WHY THIS EXISTS, AND WHY IT IS NOT ANOTHER KNOB.

`pipeline/goblin-twopass-route-0822.md` and its evening CORRECTION close every
lever this tree owns on the goblin's pose:

  * words              -- B5 fails; `crouching` returns a standing figure.
  * openpose + LoRA    -- w 0.80/0.65 keep his face and never bend a knee;
                          0.50/0.35 bend nothing and lose his face. No crossing.
  * two-pass i2i       -- six cells on a seated init: the ONLY cell that keeps
                          the seat is the one cell where he is somebody else.
  * i2i from canon     -- the face breaks between 0.40 and 0.45 and the pose has
                          not moved at 0.40.

Every one of those failures has the SAME shape: identity and pose are being
asked of the SAME PIXELS at the same time, and the LoRA that supplies the first
also supplies a standing prior -- 21 of 21 training frames stand, pre-registered
in `emit_train_jerry_v2_0822.BARS` before a frame was admitted.

SO STOP ASKING ONE REGION TO CARRY BOTH. His identity lives in his HEAD, his
ears, his eye and his shirt. His legs are bare skin, dark shorts and dark boots
-- there is nothing about a goblin leg that a base checkpoint cannot draw. Split
the frame:

    ABOVE the cut  the founder's own canon pixels, moved as a rigid block and
                   held OUTSIDE the mask, so an inpaint pipeline restores them
                   every timestep.  NO LoRA is loaded, so nothing can stand him
                   up: the thing that carries the standing prior is not in the
                   pass at all.
    BELOW the cut  fully redrawn at high strength against an openpose skeleton
                   authored in HIS measured proportions.  This is the ONE
                   configuration in which the pose net has been observed to
                   drive in this tree: no LoRA in the pass (correction Sec 3,
                   four of four postures).

WHAT THIS BUYS IF IT LANDS: a DATASET FACTORY.  v3 is blocked on posed frames of
HIM and pass one can only pose a stranger.  A frame whose head is byte-identical
to the founder's ratified canon and whose legs are seated is a posed frame of
him, and four to six of them at $0 is the v3 dataset the whole lane is waiting
on.

WHAT THIS IS NOT.  It is not a plate for beat 13 and it is not a taste call.
The founder's question page `/review/ep2-goblin-twopass-0822` stands unchanged.

WHY THE TORSO IS MOVED BY AN INTEGER AND NOTHING ELSE.  A resample would touch
his face.  A translation by a whole number of pixels does not: the 200x270 face
core is asserted byte-identical to the canon file at the end of this script, in
code, and the assertion fails the build rather than the review.

THE COMPOSITOR ROUTE THAT CAME FIRST, AND WHY IT IS NOT WHAT SHIPS HERE.  Two
rounds tried to WARP his legs into the seat instead of generating them.  Both
failed and the reason is structural rather than a tuning miss:

  1. Every frontal seat foreshortens both thighs about 6:1 -- the b13 skeleton
     draws a 37 px thigh against a 217 px standing one.  A 2-D affine can squash
     pixels along an axis; it cannot draw a limb pointing at the camera.
  2. His shirt hem falls 38 px BELOW his hip, so a seated lower body drawn
     behind the garment is ~90% shirt.  Round one rendered as a standing figure.
  3. Drawn in FRONT of the torso (round two, occlusion being free in a
     compositor) the legs read as dark blocks: the canon frame gives 29 px of
     bare shin against 65 px of boot, and his right leg is unusable at all --
     he stands on a slope, so it is 30% shorter than the left.

The compositor half still works and is used here: the rigid face move and the
background reconstruction are both from that build.  What it cannot supply is
LIMB PIXELS AT A NEW ANGLE, and that is exactly what the masked pass generates.

    python3 pipeline/author_jerry_lowerbody_0822.py            # dry
    python3 pipeline/author_jerry_lowerbody_0822.py --write

$0.  No model, no network, no GPU.
"""
from __future__ import annotations

import hashlib
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from author_b08_openpose_hint import draw_bodypose, ratio_for  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(REPO, "taste", "refs", "goblin-canon-founder-0821.png")
CANON_SHA = "b62f333644c2f3161c0d5933f122f32c46c7608d1a97f758f3c53e4692eb4f00"
OUT = os.path.join(REPO, "farm-out", "jerry-lowerbody-src-0822")
W, H = 832, 1216

# ---------------------------------------------------------------------------
# THE FIGURE, MEASURED OFF THE CANON FILE ON A 50 px GRID (legs on a 20 px one).
# `upper` is head + ears + torso + both arms down to the shirt hem: the block
# that moves rigidly and is then held out of the mask.
# ---------------------------------------------------------------------------
UPPER = [(420,122),(490,132),(540,165),(572,225),(580,285),
         (590,308),(628,318),(668,347),(636,375),(586,398),(558,408),
         (548,440),(520,468),(500,487),(495,505),
         (545,512),(578,530),(597,572),(605,640),(608,700),(600,760),
         (586,802),(566,822),(540,840),(470,852),(420,854),(360,850),(305,834),
         (278,818),(262,780),(248,720),(240,650),(246,590),(262,545),(292,516),
         (340,505),(345,487),(320,468),(295,438),
         (282,405),(252,392),(212,325),(248,314),(280,300),
         (268,258),(282,196),(330,148),(378,127)]
# everything the canon draws below the shirt: shorts, shins, boots.
LEGS = [(276,790),(514,790),(516,900),(492,1004),(470,1044),(414,1046),
        (398,1000),(392,990),(346,1006),(298,998),(292,952),(312,930),
        (300,896),(276,882)]

# ---------------------------------------------------------------------------
# THE CUT, AND IT IS ONE NUMBER SO THE FIRST CORRECTION IS ONE NUMBER.
# DROP moves the block; CUT_Y is where the mask starts.
#
# WHY THE CUT IS AT 900 AND NOT BELOW HIS HANDS.  The first build put it at 975,
# five pixels under his knuckles, so that the hands survived too.  That cut is
# unusable and the HINT is what says so: with the hands preserved at y 920..950
# no knee can be authored above y 975, and a knee at hip height with the shins
# hanging is a STANDING figure with its feet apart.  The correction to
# `goblin-twopass-route-0822.md` already measured that exact trap on
# `h240hunch` -- a hint that differs from `stand` by one small displacement gets
# rendered, correctly, as a standing figure.  A seated CHIBI reads as seated
# because its KNEES COME UP IN FRONT OF IT, and his knees can only come up if
# the region his hands occupy may be redrawn.
#
# WHAT IS STILL PRESERVED AT 900, WHICH IS EVERY IDENTITY BAR THIS TREE SCORES:
# the dome, both ears, the eyes, the whole face, the collar, the placket and the
# upper two thirds of the shirt.  What is redrawn: the forearms below the elbow,
# the hands, the shirt hem, the legs and the ground.  A base checkpoint can draw
# a sleeve and a boot; it cannot draw his eye, and it is not being asked to.
# ---------------------------------------------------------------------------
DROP = 150
CUT_Y = 900

# ---------------------------------------------------------------------------
# THE SEATED SKELETON, AUTHORED IN CANON COORDINATES RATHER THAN DERIVED.
#
# `author_jerry_skel_0820.figure()` builds from a stature template whose torso
# is far shorter than his: mapped onto the canon frame by crown and foot line it
# puts the hip at y 677 where the canon's hip is at 812, a 135 px disagreement.
# A hint that disagrees with the pixels it is conditioning is the b08 defect in
# a new costume, so the head, neck, shoulder, elbow and wrist keypoints here are
# the CANON'S OWN, measured and then moved by the same integer DROP as the
# pixels.  Only the four leg joints are authored, because only they are being
# generated.
# ---------------------------------------------------------------------------
CANON_KP = {                      # measured on the standing canon, pre-DROP
    "nose": (418, 400), "Reye": (355, 380), "Leye": (490, 380),
    "Rear": (270, 360), "Lear": (575, 360),
    "neck": (420, 495),
    "Rsho": (312, 510), "Lsho": (528, 510),
    "Relb": (280, 615), "Lelb": (560, 615),
    "Rwri": (298, 775), "Lwri": (542, 775),
    "Rhip": (368, 812), "Lhip": (470, 812),
}
SEAT_LEGS = {                     # authored, in the moved frame
    # b13's OWN STANCE: "knees up, forearms on the knees, hands clasped".
    #
    # KNEES ABOVE THE HIP LINE, 22 px up and 145 px out from a hip line that is
    # only 51 px wide.  That is the frontal drawing of a foreshortened thigh --
    # the knee arrives beside the body instead of below it -- and it is the one
    # silhouette change that separates a seated chibi from a standing one.  A
    # knee at hip height with the shin hanging is a standing figure with its
    # feet apart, which the h240hunch cell already proved the net renders
    # faithfully and uselessly.
    #
    # EVERY LEG JOINT STILL FALLS BELOW CUT_Y.  A keypoint above the cut is
    # conditioning for pixels the pass is forbidden to redraw -- a hint arguing
    # with a latent blend that always wins.  Asserted in code below.
    #
    # SEGMENT LENGTHS ARE HIS.  Thigh 96 px against the canon's measured 94;
    # shin+boot 122 px against its 95-130.  A hint that asks for a longer leg
    # than he has is how a chibi comes back as a child.
    "Rkne": (275, 940), "Lkne": (565, 945),
    "Rank": (300, 1060), "Lank": (540, 1065),
}


def sha256_of(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def mask_from(poly, feather=0.0):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather)) if feather else m


def bg_fill(img, hole):
    """Row-wise horizontal interpolation across the hole, then a blur.

    The canon background is a defocused gradient, so interpolating each row
    between its nearest surviving pixels reproduces it closely.  A
    nearest-neighbour pull was tried first and left a visible outline of the
    figure it had removed.
    """
    a = np.asarray(img).astype(np.float32)
    h = np.asarray(hole) > 64
    out = a.copy()
    xs = np.arange(W)
    for y in range(H):
        keep = ~h[y]
        if keep.sum() < 8:
            continue
        for k in range(3):
            out[y, h[y], k] = np.interp(xs[h[y]], xs[keep], a[y, keep, k])
    sm = np.stack([ndimage.gaussian_filter(out[..., k], 14) for k in range(3)],
                  axis=-1)
    w = np.clip(ndimage.gaussian_filter(h.astype(np.float32), 10) * 1.6, 0, 1)
    return Image.fromarray(np.clip(
        out*(1-w[..., None]) + sm*w[..., None], 0, 255).astype(np.uint8))


def build():
    src = Image.open(CANON).convert("RGB")
    if src.size != (W, H):
        raise SystemExit("!! canon is %dx%d, expected %dx%d" % (src.size + (W, H)))

    # 1. erase the whole standing figure, background only
    hole = Image.fromarray(np.maximum(np.asarray(mask_from(UPPER)),
                                      np.asarray(mask_from(LEGS))))
    hole = hole.filter(ImageFilter.MaxFilter(9))
    hole = Image.fromarray((np.asarray(hole.filter(ImageFilter.GaussianBlur(9)))
                            > 12).astype(np.uint8) * 255)
    plate = bg_fill(src, hole)

    # 2. drop the upper block back on by INTEGER TRANSLATION
    up = Image.new("RGB", (W, H)); up.paste(src, (0, DROP))
    um = Image.new("L", (W, H), 0)
    um.paste(mask_from(UPPER).filter(ImageFilter.MaxFilter(9))
             .filter(ImageFilter.GaussianBlur(3)), (0, DROP))
    init = plate.copy()
    init.paste(up, (0, 0), um)

    # 3. the mask -- one horizontal cut, white below
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rectangle([0, CUT_Y, W - 1, H - 1], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(4))

    # 4. the hint
    kps = {k: (v[0], v[1] + DROP) for k, v in CANON_KP.items()}
    kps.update(SEAT_LEGS)
    # THE WRISTS MOVE TOO, and only because the forearm is now inside the mask.
    # b13's line is "forearms on the knees": the elbow keypoint stays where his
    # own sleeve is (preserved pixels, y 765), and the wrist lands beside the
    # knee.  Forearm 166 px against the canon's measured 161.
    kps["Rwri"] = (300, 930)
    kps["Lwri"] = (540, 935)
    hint = Image.new("RGB", (W, H), (0, 0, 0))
    draw_bodypose(hint, kps, ratio_for(W, H))

    return src, init, mask, hint, kps


def main():
    write = "--write" in sys.argv
    have = sha256_of(CANON)
    if have != CANON_SHA:
        print("!! canon hashes %s, this script was written against %s"
              % (have, CANON_SHA))
        return 1

    src, init, mask, hint, kps = build()

    # THE ASSERTION THAT MAKES "his face, untouched" A FACT AND NOT A CLAIM.
    a, b = np.asarray(src), np.asarray(init)
    # the box is the DOME AND FACE, held 10 px clear of the jaw line: the
    # `upper` polygon turns the corner at (320,468) and the mask's 3 px feather
    # reaches four pixels inside it, which is the boundary behaving correctly
    # rather than the block moving.
    y0, y1, x0, x1 = 200, 455, 330, 510
    if not np.array_equal(a[y0:y1, x0:x1], b[y0+DROP:y1+DROP, x0:x1]):
        print("!! the face core is NOT byte-identical after the move -- stop.")
        return 1
    print("face core (%d,%d)-(%d,%d) byte-identical to canon after +%d: OK"
          % (x0, y0, x1, y1, DROP))

    # and the mask must not touch it
    m = np.asarray(mask)
    # THE FLOOR OF WHAT MUST SURVIVE: the shirt placket runs to y 880 after the
    # move and the collar to 650.  Nothing identity-bearing sits below 890.
    IDENTITY_FLOOR = 890
    if m[:IDENTITY_FLOOR].max() != 0:
        print("!! mask reaches y<%d -- it would eat the placket. stop."
              % IDENTITY_FLOOR)
        return 1
    print("mask: %d white px, first white row %d, %.1f%% of frame"
          % ((m > 0).sum(), int(np.argmax((m > 0).any(axis=1))),
             100.0 * (m > 0).mean()))
    # EVERY GENERATED JOINT MUST BE INSIDE THE REGION THE PASS MAY REDRAW.
    for n in ("Rkne", "Lkne", "Rank", "Lank"):
        if kps[n][1] <= CUT_Y:
            print("!! %s is at y %d, above the cut at %d -- the pass cannot "
                  "draw there and the hint would be arguing with a latent "
                  "blend it cannot win. stop." % (n, kps[n][1], CUT_Y))
            return 1
    import math
    th = math.hypot(kps["Rkne"][0]-kps["Rhip"][0], kps["Rkne"][1]-kps["Rhip"][1])
    sh = math.hypot(kps["Rank"][0]-kps["Rkne"][0], kps["Rank"][1]-kps["Rkne"][1])
    print("hint: %d keypoints; hips y%d knees y%d/%d (%+d) ankles y%d/%d; "
          "thigh %.0f px (canon 94), shin+boot %.0f px (canon 95-130); "
          "all four leg joints below the cut"
          % (len(kps), kps["Rhip"][1], kps["Rkne"][1], kps["Lkne"][1],
             kps["Rkne"][1]-kps["Rhip"][1], kps["Rank"][1], kps["Lank"][1],
             th, sh))

    files = {"jerry-seat-init-0822.png": init,
             "jerry-seat-mask-0822.png": mask,
             "jerry-seat-hint-0822.png": hint}
    if not write:
        print("\nDRY -- pass --write to author into %s"
              % os.path.relpath(OUT, REPO))
        return 0
    os.makedirs(OUT, exist_ok=True)
    for name, im in files.items():
        p = os.path.join(OUT, name)
        im.save(p)
        print("WROTE %-30s %s" % (name, sha256_of(p)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
