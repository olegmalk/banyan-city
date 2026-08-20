#!/usr/bin/env python3
"""beat16_leaf_composite.py -- draw ONE large ordinary cotyledon leaf into beat
16's near foreground so the leaf is the SUBJECT and the goblin is DEPTH.

THIS TOOL BUILDS A SHOT CANON CURRENTLY FORBIDS, AND THAT IS DELIBERATE
---------------------------------------------------------------------
`pipeline/canon.yaml sapling-cotyledon-shape` -- the founder's own 2026-08-17
answer -- rules out "any leaf drawn as a feature -- no exaggerated silhouette,
NO LEAF WHOSE SHAPE IS THE SUBJECT OF THE SHOT". Beat 16's brief asks for
exactly that: "close on one leaf with the scavenger blurred behind it; the leaf
is the subject and he is depth". Both are the author's and they ask for opposite
shots. `/review/ep2-b16-leaf-0820` puts that contradiction to him and asks:
restage the beat, or licence this one shot.

`review/inbox.yaml`'s beat-16 entry recorded this composite as NAMED AND
DELIBERATELY NOT FIRED, "because it builds the exact shot canon currently
forbids, and spending it before his word would be answering a ruling with a
render." THAT REASONING IS NOT RETRACTED AND THE TENSION IS NOT PAPERED OVER.
What changed is a standing directive that every option on an open card should
have pixels rather than a description. So this fires ONLY as labelled card
evidence: `is_show_content: false`, never a cut init, and CANON IS UNCHANGED.
A clean composite here is not a licence; the licence is the author's word and
nothing in this file or its sample can supply it. If he restages, these pixels
are an archived road not taken and cost $0.

THE SHAPE OBEYS CANON EVEN THOUGH THE FRAMING IS THE EXCEPTION. One question is
being put to him -- may a leaf be the subject of a shot -- and drawing an exotic
leaf would smuggle a second one in beside it. So the blade is an ordinary ovate
cotyledon with a blunt rounded apex: no lobes, no palmate fingers, no lance
point, aspect inside the pre-registered 1.6-2.6 band, and C10 measures "no
lobes" as arithmetic rather than promising it in prose.

WHY A COMPOSITE AND NOT A FOURTH WORDING
----------------------------------------
THE WORDING LADDER ON BEAT 16 IS CLOSED AT THREE RUNGS (0814, and r1/r2 on
0820) and this file spends no fourth. r2 was a PURE PERMUTATION -- the same 73
tokens in a different order, same host, same seed -- and the composition did not
move a pixel's worth. Beat 16's `done_when` is a RELATION, the same class beat
03 established cannot be bought with words.

WHAT IS DRAWN, WHAT IS NOT
--------------------------
NOTHING IS ERASED. Unlike beats 03, 15 and 19 this composite is purely additive:
there is no wrong plant in the plate to remove, so there is no vacancy, and
composite-init-pattern.md 6's vacancy law and 13's cue law have nothing to bite
on. The goblin, his cloak, the sky and the whole grass bed arrive byte-identical
outside the drawn footprint and C1 asserts it.

ONE THING THIS RUNG DOES NOT FIX, SAID OUT LOUD. The plate's focal plane is on
HIM -- his face is sharp and the near grass is blurred -- so the depth this
composite delivers is OCCLUSION AND SCALE, not focus. The brief's "blurred
behind it" is not reached, because blurring him means writing outside the drawn
footprint, which C1 forbids and which would put a second variable in the same
fire. If the author licences the shot, focus separation belongs to the plate
that gets authored under the licence, not to this evidence frame.

THE PLATE, AND WHY r1s1 RATHER THAN r2s1
-----------------------------------------
Parent: farm-out/ep2-b16-mac-plate-0820/16-why-mac-plate-r1s1.png
(832x1216, animagine-xl-3.1, seed 20260820, sha aa0119ac...). Both plates are
head-fill FAILS and neither contains a leaf; the choice is only about which
figure placement a foreground leaf can turn into depth. Measured, not eyeballed:

  * r1s1's figure is SMALLER -- green-skin-rule pixels 27.1% of frame against
    r2s1's 30.3%, and its head's lower boundary is y=600 against y~700. A
    foreground object wins the size contest by more against the smaller figure,
    and "he is depth" is a size relation before it is anything else.
  * r1s1 HAS AN UNBROKEN NEAR-FOREGROUND GRASS BED, y 780..1216 across the full
    width, which is where a petiole has to root and leave frame. On r2s1 the
    grass climbs to y~300 on the left and already crosses his jaw, so a drawn
    leaf there COMPETES with foreground structure the plate already has instead
    of establishing the near plane itself.
  * r1s1's ears and cloak shoulders survive as silhouette once the face is
    occluded, so he still reads as a goblin behind a leaf rather than as a
    green mass.

MEASURED OFF r1s1 BEFORE ANY DRAWING CODE EXISTED
--------------------------------------------------
  * LIGHT. The sigma-60 low-pass luminance gradient over the HEAD ONLY reads
    dx +0.345 dy -0.939 -- up and to the right. Unlike beat 03 this measurement
    is USED, because it is confirmed by two visible cues rather than contradicted
    by them: the blown rim on the top-right of the skull (low-pass 193 at x600
    y40 against 121 at x416 y120) and the cheek split (lit right cheek raw luma
    129 at x560 y430, shadowed left cheek 7 at x250 y430). Restricting the
    low-pass to the head is the correction beat 03's note asks for -- over the
    whole frame the bright grass bed below drags the same measurement to
    dx +0.194 dy -0.981, which is measuring the field, not the key.
    RESOLVED INTO LEAF COORDINATES, THE KEY IS ALMOST ENTIRELY ALONG THE BLADE:
    light . u = +0.99 and light . v = -0.14. The blade is therefore lit at the
    apex and shaded at the base, and its ACROSS-the-blade shading is weak. That
    number is the reason the cel shadow below is a fold rather than a half-tone
    over the whole shaded side -- asserting a strong side-light this frame does
    not have is decal tell 2 in the other direction.
  * THE PLATE'S OWN LINEWORK. Per-pixel luma gradient inside his face box
    (200..640, 200..560): p99 85.1, p99.9 139.2, max 172.2, and its cel outlines
    run to luma 0. THE GRASS BED HAS NO LINEWORK AT ALL -- gradient p99 6.8, max
    28.6, minimum luma 38.9 -- because it is drawn out of focus. Both numbers
    matter: the face is the dialect's own line weight and the ceiling C8 holds
    the drawn outline under; the bed's 38.9 is the honest floor for C4, which is
    why C4 prints BOTH it and the footprint's trivial 0.0.
  * THE COLOUR COLLISION, and it forced the palette. The plate's own foliage and
    the goblin's own skin are THE SAME COLOUR to within four levels in every
    channel: grass-bed pixels in luma band 90..140 mean (107.3, 128.1, 79.6),
    his lit forehead (111, 132, 79). beat 03's practice -- draw the plant in the
    colours of the plant already in the plate -- would therefore paint an
    INVISIBLE leaf across the fraction of the blade that crosses his face (C9
    prints that fraction). The plate is sampled anyway and then moved along ONE
    named axis: saturation toward true green, which neither the yellow-green
    grass (G-R 0..+15) nor the olive skin (G-R +21) occupies. Value is set
    between them so the blade separates from his face by tone and from the
    sunlit bed by tone in the other direction.

THE TWO THINGS NO EXISTING COMPOSITOR IN THIS REPO HAS HAD TO DO
=================================================================

1. VENATION AND LINE WEIGHT AT 800 px
--------------------------------------
Every existing tool draws the midrib as a luminance RIDGE and never as a line,
on composite-init-pattern.md 5's law: at 0.45 beat 10 split its slab in two
where the model read the deepest composited fissure AS AN OBJECT BOUNDARY, so
"never composite an internal line stronger than the object's own outline". Those
leaves were 30-60 px. At 800 px a ridge-only blade reads BARE -- a flat green
oval the size of his head -- and bare is its own failure: pattern 7's low-side
mode is "the surface stays the composite's own soft airbrushed relief ... reads
as a soft-focus panel rather than the material".

The two constraints are only in conflict if the law is read as "no internal
lines". That is not what the evidence says. Reading it back to its cause:

  * THE LAW IS ABOUT STRENGTH, and it is about ONE line in particular. What beat
    10 lost was a fissure AS DARK AS the object's own outline. A dark stroke that
    runs THE FULL LENGTH of a bilaterally symmetric blob, ON its axis of
    symmetry, is the strongest possible "two objects meet here" cue -- it is both
    an edge and a mirror line. That is the midrib and nothing else.
  * SO THE MIDRIB STAYS A RIDGE, and it is made ASYMMETRIC: a bright crest with a
    soft groove on the SHADED side only, offset 5 px, never a symmetric pair. A
    symmetric bright stripe down the middle is the same mirror-line cue with the
    sign flipped, and a raised rib catching a light that measures up-right does
    not look symmetric in life either. THE WHOLE BLADE IS MADE ASYMMETRIC FOR THE
    SAME REASON -- it is ovate (widest at 0.18 of a below the middle, not at the
    middle), one margin is fuller than the other, and the rib itself bows 12 px.
  * DETAIL COMES FROM STRUCTURE THAT IS NOT AXIAL. Secondary veins are short,
    oblique, unequal in number either side (8 shaded, 7 lit), not mirrored across
    the midrib, and EVERY ONE STOPS AT 0.86 OF THE LOCAL HALF-WIDTH so no vein
    ever reaches the margin -- a vein that touches the silhouette can be
    completed INTO the silhouette, and none of these can. Their spacing, run and
    amplitude all vary per vein.
  * FORM COMES FROM CEL SHADOW SHAPES, which is how this dialect carries volume
    -- the plate's own face is built from them, with a measured step of 122 luma
    across the cheek boundary. Two shapes are used, both HARD-EDGED, and NEITHER
    RUNS DOWN THE MIDRIB: a fold whose boundary is held 0.22 of the half-width
    off the rib and waves across it, and a basal shadow. A hard tone step ON the
    axis is the same split as a dark line at lower contrast, which is the whole
    thing the venation design above exists to avoid. The drawn step is ~50 luma,
    deliberately well under the plate's own 122.
  * LINE WEIGHT VARIES AROUND THE OUTLINE, 2.6 px on the lit margin to 6.2 px on
    the shaded one, driven by the same measured light axis. A CONSTANT-WIDTH
    OUTLINE IS THE LOUDEST VECTOR-ART TELL THERE IS and draft 1 had one.
  * TERTIARY RETICULATION IS NOT DRAWN AND THAT IS A CHOICE, NOT AN OVERSIGHT.
    The pass tell in pattern 7 is that soft procedural relief comes back AS crisp
    cel line work -- the sampler's contribution has to be visible against the
    composite or the pass is a paste. Supplying the finest tier here would leave
    12 denoising steps nothing to add and would guarantee the FAIL-PASTE reading.

AND IT IS MEASURED RATHER THAN ASSERTED, which is the part that makes the above
more than a story. C7 computes the maximum per-pixel luma gradient across
venation pixels and across outline pixels ON THE FINISHED COMPOSITE and refuses
unless venation is strictly weaker on both gradient and darkness; C4 refuses if
the darkest solid drawn pixel undercuts the plate's own darkest; C8 refuses if
the drawn outline is stronger than the plate's own p99.9 linework. A tool that
only carried a comment saying "be careful with the midrib" is the thing pattern
13's meta-finding rejects.

2. MASK FRACTION -- IT IS BIG, AND THE SIZE IS PRINTED, NOT BURIED
-------------------------------------------------------------------
The four composites that worked put a SMALL plant INTO a plate: 4.10% of frame
on beat 13's parent, 7.97% on its tall variant. This blade is an order of
magnitude larger by design, and the work ladder's own warning is that "a 0.30
pass over 60-80% of a picture is a re-render, not an inpaint". The number is
computed and printed at run time, and if it clears ~35% the tool says so loudly.

WHAT IS *NOT* CHANGED IN RESPONSE TO THAT NUMBER: the sample still fires at
0.30. 0.30 is the house value, it is the value all four prior composites passed
at, and moving strength AND the object class in one fire measures neither.
Strength is pre-registered as its own separate rung, to be filed only if 0.30
comes back weak, and named in the spec before the pixels exist so it cannot be
claimed afterwards as a foreseen fix.

TODAY'S SIBLING RESULT, AND THE HYPOTHESIS IT KILLS IN ADVANCE
---------------------------------------------------------------
The beat 13 lane ran the same shape of experiment this morning (`4e5a6f96`) and
measured mean |delta| inside the mask at 8.62 over 7.97% of frame against the
working parent's 6.23 over 4.10%. THE SAMPLER ENGAGED HARDER OVER THE BIGGER
MASK AND THE PICTURE STILL FAILED. So "0.30 was too weak over a big mask" is not
available here as an explanation -- it is a hypothesis that has to be tested
against the numbers, and this rung reports mean |delta| inside AND outside the
mask exactly as that lane did, so the comparison is a controlled one.

FOUR COMPOSITES WERE REJECTED BEFORE THIS ONE, AND NONE OF THEM COST A GPU
----------------------------------------------------------------------------
This is the point of doing the structure with image processing: a rejection
costs seconds. Three were thrown out by opening them at 1x and 2x; one was
refused by a check before I got that far.

| # | What it looked like | The actual cause | Fix |
|---|---|---|---|
| d1 | green paper cut-out -- leaf clip-art, four faults at once | ruled pale scratches in a parallel array (one angle, one spacing, one amplitude, drawn straight); a bevelled sticker, because the "margin curl" was a soft band parallel to the outline all the way round, which is what a bevel IS; a soft wavy basal edge reading as a tide mark; and a perfect vector oval -- bilaterally symmetric, widest exactly at the middle, dead-straight rib, constant-width outline | per-vein run, curvature and amplitude; the curl deleted; ovate silhouette with margin asymmetry and a rib bow; outline weight driven by the measured light |
| d2 | two-tone paper, and a blade with no shadow of its own | the replacement "fold" ran the length of the blade and cut it into two flat halves along a near-straight diagonal -- and it was asserting a side light the frame does not have (light . v = -0.14 against light . u = +0.99). Separately: an object in front of a face throwing NO cast shadow is decal tell 2 in its purest form | the fold deleted; a cast shadow along the measured key, declared in the footprint |
| d3 | never opened -- **C7 refused it** | secondary veins were darkened by MULTIPLYING, which compounds with the cel shadow: the same stroke that read as a 60-luma step in the lit half bottomed out at 36.1 in the basal shadow, DARKER than the outline's own 39.6. This is exactly the condition pattern 5's law names, arrived at from a direction I had not predicted -- not the midrib, and not at the strength I set | veins blend toward a FIXED tone (luma 60.2) instead of multiplying, so the floor is 17 above the outline by construction |
| d4 | a stain across the lower third, with a staircase in it | two shadow shapes -- a cosine-waved basal cut and a margin wedge -- printed a notched boundary where they met | one shape, one smooth tilted crease across the blade's own cross-section |

WHY THESE PRIMITIVES ARE A COPY AND NOT AN IMPORT
--------------------------------------------------
`sha256_of`, `luminance`, `binary_dilate`, `blob_count` and the shading skeleton
are carried from pipeline/beat03_cover_composite.py, which passed its bar on
2026-08-20. They are COPIED on purpose: an init whose sha256 a job spec asserts
must not be able to change its bytes because a peer edited a shared module. The
house has five beat-specific compositors already for the same reason. If they
are ever promoted to a module, promote them together and re-assert every init
sha.

$0: no model, no network, no GPU, no RNG that is not seeded. `--dry-run` writes
nothing.
"""

import argparse
import hashlib
import json
import math
import os
import sys
from collections import deque
from datetime import date

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATE = os.path.join(REPO, "farm-out", "ep2-b16-mac-plate-0820",
                     "16-why-mac-plate-r1s1.png")
PLATE_SHA = "aa0119ac409b31a7bad74d3a8e250a8b6d37c274da009d4581f1d51eb35400a9"

# --- light, measured on the HEAD's own low-pass; see the docstring -----------
LIGHT_DX, LIGHT_DY = 0.345, -0.939
LIGHT_WHOLEFRAME_REJECTED = (0.194, -0.981)   # printed so the rejection is checkable

# --- palette. Derived from the plate and then moved along ONE named axis. ----
LEAF_LIT = (120.0, 168.0, 86.0)      # luma 144.3
LEAF_SHADE = (66.0, 106.0, 80.0)     # luma 93.6 -- step 50.7, against the plate's own 122
PETIOLE_RGB = (104.0, 140.0, 78.0)   # luma 122.4
RIM_RGB = (30.0, 50.0, 40.0)         # luma 42.9 -- the object's own outline
# THE VEIN TONE IS A FIXED COLOUR AND NOT A MULTIPLIER, and that is C7's doing.
# Draft 3 darkened veins by multiplying, which COMPOUNDS with the cel shadow: in
# the basal shadow the same stroke that read as a 60-luma step in the lit half
# bottomed out at 36.1, DARKER than the outline's own 39.6, and C7 refused the
# composite. Blending toward a fixed tone cannot compound -- luma 60.2 is the
# floor by construction, 17 above the outline -- and it also reproduces the real
# behaviour, which is that a vein in shadow has less contrast, not more.
VEIN_DARK = (44.0, 70.0, 52.0)       # luma 60.2

FOLIAGE_BAND = (90.0, 140.0)
BED_BOX = (0, 780, 832, 1216)
FACE_GRAD_BOX = (200, 200, 640, 560)

# His face, read off a 64 px coordinate grid drawn over the plate: crown cut by
# the top edge, ears out to x 75 and x 745 at y 190..300, eye line y 360..400,
# teeth y 495..545, chin y 575. This box is what C9's occlusion relation is
# measured against -- a declared, printed box rather than a colour matte,
# because the plate's foliage and his skin are the same colour (see the
# docstring) and every green rule tried leaked one into the other.
FACE_BOX = (150, 60, 700, 600)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def luminance(arr):
    return 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]


def binary_dilate(mask, r):
    if r <= 0:
        return mask
    img = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1))
    return np.asarray(img) > 127


def blob_count(mask, minpx):
    work = mask.copy()
    H, W = mask.shape
    sizes = []
    ys, xs = np.nonzero(work)
    for y0, x0 in zip(ys, xs):
        if not work[y0, x0]:
            continue
        q = deque([(y0, x0)])
        work[y0, x0] = False
        n = 0
        while q:
            y, x = q.popleft()
            n += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    a, b = y + dy, x + dx
                    if 0 <= a < H and 0 <= b < W and work[a, b]:
                        work[a, b] = False
                        q.append((a, b))
        if n >= minpx:
            sizes.append(n)
    return sorted(sizes, reverse=True)


# ---------------------------------------------------------------------------
# THE BLADE'S SILHOUETTE
#
# OVATE, which is what "the shape anyone draws when you say leaf" actually is:
# widest BELOW the middle and tapering to a blunt apex. Implemented by warping
# the longitudinal coordinate so the half-width maximum sits at s = WIDEST
# instead of at 0, and keeping an elliptical profile either side of it so both
# ends stay round. beat 03 and beat 15 use |cos|^0.82, which is BLUNTER than an
# ellipse; at their 50 px that reads as a leaf and at 800 px it reads as a
# PADDLE, so the exponent does not transfer and this profile is elliptical.
# ---------------------------------------------------------------------------
WIDEST = -0.18       # of a, below the middle -- this is what makes it ovate
ASYM = 0.07          # one margin fuller than the other
BOW = 12.0           # px the rib bows, so the blade is not its own mirror


def _w(s):
    """Warp s in [-1, 1] so the widest station is WIDEST rather than 0."""
    c = WIDEST
    return (s - c) / (1.0 - c) if s >= c else (s - c) / (1.0 + c)


# THE APEX IS TAPERED AND THE BASE IS NOT, which is the other half of "ovate".
# Draft 2 used the same elliptical exponent both ends and its apex came back a
# SPOON -- tip half-width still 0.40 of b at 90% of the length. 0.60 on the apex
# side draws the width down earlier while keeping the very tip rounded (an
# exponent above 0.5 tapers, below 0.5 blunts), and C10 still measures the
# result against the lance floor rather than trusting the constant.
APEX_P = 0.60
BASE_P = 0.50


def half_width_frac(s):
    """|v|/b at longitudinal fraction s = u/a, mean of the two margins."""
    sf = float(s)
    w = min(abs(_w(sf)), 1.0)
    p = APEX_P if sf >= WIDEST else BASE_P
    return max(0.0, 1.0 - w * w) ** p


def bow(s):
    return BOW * (1.0 - s * s)


def margins(s):
    """(v of the shaded margin, v of the lit margin) at station s."""
    h = half_width_frac(s) * MARGIN_B
    a_ = 1.0 + ASYM * (-s)
    return bow(s) + h * a_, bow(s) - h * (2.0 - a_)


MARGIN_B = 205.0     # set by geometry() at run time; module-level for margins()


def geometry():
    """Where the leaf goes.

    THE ONLY FREE CHOICES ARE THE CENTRE, THE ANGLE AND THE SIZE, and all three
    are staging rather than canon. Everything after them is arithmetic.

    Centre (400, 520) at -62 degrees, semi-axes 400 x 205: an 800 px blade of
    aspect 1.95, inside the pre-registered 1.6-2.6 band. Its bounding box leaves
    the WHOLE BLADE INSIDE THE FRAME -- C2 -- and the petiole is the only part
    that leaves, through the bottom edge, which it has to: a near-foreground
    object floating entirely inside the frame reads as a sticker, and a blade
    with no visible attachment is decal tell 3 from the far side. So the blade
    is legible in full (which is what the card needs -- the question is what
    this leaf SHAPE buys) and the petiole roots it.

    WHY THIS ANGLE AND CENTRE, AND THEY ARE OCCLUSION ARITHMETIC RATHER THAN
    TASTE. At -62 degrees the blade's long axis crosses the eye line at x 474
    and its local half-width there is ~200 px, which puts BOTH his eyes inside
    the blade. Leaving an eye out was tried and rejected in draft: an eye is the
    strongest focus pull in any frame, and a composite that leaves one visible
    has not made him depth -- it has made him a face peering over a leaf, which
    is the failure the plate already has. His skull above the blade, both ears
    and both cloak shoulders stay untouched, so what remains still reads as a
    goblin BEHIND rather than as a green field.
    """
    return {
        "centre": (400.0, 520.0),
        "angle": -62.0,
        "a": 400.0,
        "b": 205.0,
        "petiole_ctrl": (168.0, 1040.0),
        "petiole_end": (138.0, 1240.0),
        "petiole_w0": 26.0,      # at the blade
        "petiole_w1": 36.0,      # at the frame edge -- nearer camera, so wider
    }


# Secondary veins, one tuple per vein: (station, run, curvature, amplitude).
# NOTHING IS UNIFORM AND NOTHING IS MIRRORED -- 8 on the shaded margin against 7
# on the lit one, at stations that do not pair up, with runs from 0.19a to 0.28a
# and amplitudes from 0.72 to 1.0. Draft 1 drew one angle, one spacing and one
# amplitude and came back as a ruled parallel array, which is decal tell 4.
VEINS_SHADED = ((-0.82, 0.26, 0.30, 0.86), (-0.63, 0.24, 0.33, 1.00),
                (-0.41, 0.28, 0.36, 0.94), (-0.20, 0.25, 0.38, 1.00),
                (0.02, 0.27, 0.40, 0.90), (0.24, 0.23, 0.43, 0.82),
                (0.44, 0.21, 0.46, 0.76), (0.62, 0.19, 0.48, 0.72))
VEINS_LIT = ((-0.74, 0.25, 0.31, 0.94), (-0.52, 0.27, 0.34, 1.00),
             (-0.31, 0.23, 0.37, 0.88), (-0.09, 0.26, 0.39, 1.00),
             (0.14, 0.24, 0.42, 0.92), (0.35, 0.22, 0.45, 0.80),
             (0.55, 0.20, 0.47, 0.74))
VEIN_REACH = 0.86          # of the LOCAL half-width; no vein touches the margin
MIDRIB_FROM, MIDRIB_TO = -0.95, 0.92


def _bez(p0, p1, p2, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])


def blade_outline(geom, n=300):
    """The silhouette, walked as two margins so the ovate warp, the asymmetry
    and the rib bow all appear in it."""
    cx, cy = geom["centre"]
    ang = geom["angle"]
    a = geom["a"]
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def uv2xy(u, v):
        return (cx + u * ca - v * sa, cy + u * sa + v * ca)

    lo, up = [], []
    for i in range(n + 1):
        s = -1.0 + 2.0 * i / n
        v_lo, v_up = margins(s)
        lo.append(uv2xy(s * a, v_lo))
        up.append(uv2xy(s * a, v_up))
    return lo + up[::-1]


def draw_leaf(geom, W, H, ss=3):
    """Return (rgb, alpha, rim, shade_mask, ridge, groove) at plate resolution.

    Drawn at ss x supersample so every edge anti-aliases in the plate's own soft
    cel manner. Silhouette, outline, petiole and venation are polygons and
    strokes; the two cel shadow shapes are computed analytically on the
    full-resolution grid in leaf-local coordinates, because their boundaries are
    curves in (u, v) that no polygon list would describe honestly.
    """
    cx, cy = geom["centre"]
    ang = geom["angle"]
    a, b = geom["a"], geom["b"]
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    L = Image.new("RGB", (W * ss, H * ss), (0, 0, 0))
    A = Image.new("L", (W * ss, H * ss), 0)
    Rm = Image.new("L", (W * ss, H * ss), 0)
    Rg = Image.new("L", (W * ss, H * ss), 0)
    Gv = Image.new("L", (W * ss, H * ss), 0)
    dl, da, dr, dg, dv = (ImageDraw.Draw(x) for x in (L, A, Rm, Rg, Gv))

    def S(p):
        return (p[0] * ss, p[1] * ss)

    def uv2xy(u, v):
        return (cx + u * ca - v * sa, cy + u * sa + v * ca)

    def stroke(drawer, poly, w_from, w_to, value):
        for i in range(len(poly) - 1):
            t = i / float(max(1, len(poly) - 2))
            w = w_from + (w_to - w_from) * t
            drawer.line([S(poly[i]), S(poly[i + 1])], fill=value,
                        width=max(1, int(round(w * ss))))
            r = w * ss / 2.0
            x, y = S(poly[i])
            drawer.ellipse([x - r, y - r, x + r, y + r], fill=value)

    def offset_poly(poly, d):
        out = []
        for i, p in enumerate(poly):
            j = min(i + 1, len(poly) - 1)
            k = max(i - 1, 0)
            dx, dy = poly[j][0] - poly[k][0], poly[j][1] - poly[k][1]
            nl = math.hypot(dx, dy) or 1.0
            out.append((p[0] - dy / nl * d, p[1] + dx / nl * d))
        return out

    # ---- the petiole, drawn FIRST so the blade sits over its top end ---------
    bx, by = uv2xy(-a, 0.0)
    px, py = geom["petiole_ctrl"]
    ex, ey = geom["petiole_end"]
    w0, w1 = geom["petiole_w0"], geom["petiole_w1"]
    n = 48
    left, right, spine = [], [], []
    for i in range(n + 1):
        t = i / float(n)
        qx = (1 - t) ** 2 * bx + 2 * (1 - t) * t * px + t ** 2 * ex
        qy = (1 - t) ** 2 * by + 2 * (1 - t) * t * py + t ** 2 * ey
        dx = 2 * (1 - t) * (px - bx) + 2 * t * (ex - px)
        dy = 2 * (1 - t) * (py - by) + 2 * t * (ey - py)
        nl = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / nl, dx / nl
        w = (w0 + (w1 - w0) * t) / 2.0
        left.append((qx + nx * w, qy + ny * w))
        right.append((qx - nx * w, qy - ny * w))
        spine.append((qx - nx * w * 0.34, qy - ny * w * 0.34))
    stalk = left + right[::-1]
    dl.polygon([S(p) for p in stalk], fill=tuple(int(v) for v in PETIOLE_RGB))
    da.polygon([S(p) for p in stalk], fill=255)
    # THE OUTLINE HAS TO BE IN THE ALPHA TOO -- beat 03's correction, carried:
    # the stroke straddles the polygon edge, so with alpha = fill only, its outer
    # half lands where alpha is 0 and is masked away, leaving a hairline instead
    # of a cel line.
    dr.line([S(p) for p in stalk] + [S(stalk[0])], fill=255, width=int(3.8 * ss))
    da.line([S(p) for p in stalk] + [S(stalk[0])], fill=255, width=int(3.8 * ss))
    stroke(dg, spine, 6.0, 7.0, 200)     # the petiole's own lit ridge

    # ---- the blade ----------------------------------------------------------
    pts = blade_outline(geom)
    dl.polygon([S(p) for p in pts], fill=tuple(int(v) for v in LEAF_LIT))
    da.polygon([S(p) for p in pts], fill=255)

    # OUTLINE WEIGHT VARIES WITH THE MEASURED LIGHT. Thin where the margin faces
    # the key, thick where it turns away -- which is how every line in the plate
    # behaves and is the single loudest difference between drawn art and vector
    # art. Drawn segment by segment because a stroke of one width is the tell.
    for i in range(len(pts)):
        p, q = pts[i], pts[(i + 1) % len(pts)]
        mx, my = (p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0
        nx, ny = mx - cx, my - cy
        nl = math.hypot(nx, ny) or 1.0
        facing = (nx / nl) * LIGHT_DX + (ny / nl) * LIGHT_DY   # +1 lit, -1 shaded
        w = 4.4 - 1.8 * facing
        wpx = max(1, int(round(w * ss)))
        # THE OUTLINE IS PAINTED INTO THE COLOUR CHANNEL TOO, and that is a bug
        # fix rather than a flourish. With alpha carrying the stroke but L not,
        # the outer half of every outline sits over BLACK, and where the rim
        # coverage is partial the blend runs toward black instead of toward the
        # rim colour -- a sub-rim ring 4 luma darker than the darkest thing the
        # tool believes it drew. beat 03 carries the same artefact.
        dl.line([S(p), S(q)], fill=tuple(int(v) for v in RIM_RGB), width=wpx)
        dr.line([S(p), S(q)], fill=255, width=wpx)
        da.line([S(p), S(q)], fill=255, width=wpx)

    # ---- venation -----------------------------------------------------------
    mid = [uv2xy(a * (MIDRIB_FROM + (MIDRIB_TO - MIDRIB_FROM) * i / 40.0),
                 bow(MIDRIB_FROM + (MIDRIB_TO - MIDRIB_FROM) * i / 40.0))
           for i in range(41)]
    # THE MIDRIB'S GROOVE IS DELIBERATELY THE WEAKEST DARK MARK ON THE BLADE
    # (value 80 against the secondaries' 230). It is the one internal line that
    # runs the full length ON the axis of symmetry, which is the only line beat
    # 10's split actually indicts; the secondaries are short and oblique and
    # decompose the blade into nothing.
    stroke(dg, mid, 12.0, 4.0, 255)
    stroke(dv, offset_poly(mid, 5.0), 7.0, 2.5, 80)

    for side, table in ((+1.0, VEINS_SHADED), (-1.0, VEINS_LIT)):
        for s0, run, curve, amp in table:
            s1 = min(s0 + run, 0.94)
            m_lo, m_up = margins(s1)
            v1 = (bow(s1) + VEIN_REACH * (m_lo - bow(s1))) if side > 0 else \
                 (bow(s1) + VEIN_REACH * (m_up - bow(s1)))
            sm = s0 + curve * (s1 - s0)
            ml, mu = margins(sm)
            vm = bow(sm) + 0.34 * ((ml - bow(sm)) if side > 0 else (mu - bow(sm)))
            p0 = uv2xy(s0 * a, bow(s0))
            p1 = uv2xy(sm * a, vm)
            p2 = uv2xy(s1 * a, v1)
            poly = [_bez(p0, p1, p2, i / 22.0) for i in range(23)]
            # DRAWN AS LINE, NOT AS RELIEF, AND THAT IS THE ANSWER TO 800 px.
            # Draft 2's ridge-first veins came back as pale scratches: in this
            # dialect FORM IS CARRIED BY LINE -- the plate's own face is thirty
            # hard strokes and four flat tones -- so a blade whose only line is
            # its outline reads bare however much relief it has. The vein is now
            # the dark stroke (Gv, value 230*amp) with a thin bright companion
            # on the lit side (Rg, value 90*amp) so it still reads as a raised
            # rib. C7 measures the result against the outline and refuses if any
            # of it is stronger.
            stroke(dv, poly, 6.2, 2.0, int(round(230 * amp)))
            stroke(dg, offset_poly(poly, -3.2), 3.2, 1.3, int(round(90 * amp)))

    def down(img, mode="L"):
        # LANCZOS RINGS, AND AN UNCLIPPED RING IS A HOLE -- beat 03's bug, and
        # the clip is the fix rather than a threshold to move.
        arr = np.asarray(img.resize((W, H), Image.LANCZOS)).astype(np.float64)
        return arr if mode == "RGB" else np.clip(arr / 255.0, 0.0, 1.0)

    rgb, al, rim, ridge, groove = (down(L, "RGB"), down(A), down(Rm),
                                   down(Rg), down(Gv))

    # ---- the two cel shadow shapes, analytic in leaf-local coordinates -------
    # BOTH ARE HARD-EDGED and NEITHER RUNS DOWN THE MIDRIB. Draft 1's soft band
    # parallel to the outline was an airbrushed inner glow, which is what a
    # sticker bevel is; its wavy soft basal edge read as a tide mark.
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    dxg, dyg = xx - cx, yy - cy
    u = dxg * ca + dyg * sa
    v = -dxg * sa + dyg * ca
    s = np.clip(u / a, -1.0, 1.0)
    c = WIDEST
    wq = np.where(s >= c, (s - c) / (1.0 - c), (s - c) / (1.0 + c))
    hw = b * np.sqrt(np.clip(1.0 - wq * wq, 0.0, 1.0))
    bw = BOW * (1.0 - s * s)

    # THE FULL-LENGTH FOLD IS DELETED. Draft 2 had one and it cut the blade into
    # two flat halves along a near-straight diagonal -- two-tone paper, not a
    # curved leaf, and the wedge it made at the base read as a separate shape.
    # It was also over-asserting a side-light the frame does not have: light . v
    # measures only -0.14 against light . u at +0.99. What survives is the ONE
    # shadow the measurement actually supports, plus a short margin wedge in the
    # basal third only -- not a band running the whole perimeter, which is what
    # a sticker bevel is.
    # ONE SHAPE, ONE SMOOTH BOUNDARY. Draft 4 had two -- a cosine-waved basal cut
    # plus a margin wedge -- and where they met they printed a STAIRCASE with a
    # notch in it, which reads as a stain rather than as form. The boundary is
    # now a single gentle crease across the blade's own cross-section, tilted so
    # it is not perpendicular to the rib and curved so it is not a ruled line:
    # the base of the blade folding away from a key that measures light . u
    # = +0.99. A straight-ish cel crease is this dialect's own vocabulary -- the
    # plate's face carries four of them.
    vn = (v - bw) / np.maximum(hw, 1.0)
    basal = s < (-0.34 - 0.17 * vn + 0.07 * vn * vn)
    shade_mask = (basal & (al > 0.5)).astype(np.float64)
    shade_mask = np.asarray(
        Image.fromarray((shade_mask * 255).astype(np.uint8))
        .filter(ImageFilter.GaussianBlur(0.7))).astype(np.float64) / 255.0

    return rgb, al, rim, shade_mask, ridge, groove


def shade(rgb, al, shade_mask, ridge, groove, base, seed=20260820):
    """Put the blade in the frame's own light, then the cel shadow, the rib
    relief and a faint surface mottle.

    THE MOTTLE IS NOT DECORATION. Pattern 7's low-side failure is a surface that
    stays "smooth gradients, no drawn edges" -- a flat vector fill at this size
    is exactly that -- and pattern 9b's law is that a fill with NO DETAIL passes
    every colour rule ever written for it. Seeded value noise at two scales
    gives the 12 denoising steps something to take hold of without asserting
    structure the tool cannot see.
    """
    H, W, _ = base.shape
    ys, xs = np.nonzero(al > 0.05)
    if len(ys) == 0:
        return rgb
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    proj = xx * LIGHT_DX + yy * LIGHT_DY
    p = proj[ys, xs]
    t = np.clip((proj - p.min()) / max(1e-6, (p.max() - p.min())), 0.0, 1.0)
    out = rgb * (0.86 + 0.21 * t)[:, :, None]

    # the cel shadow is a COLOUR swap, not a multiply: this dialect's shadows
    # shift hue (the plate's own go teal) and a pure multiply would only darken.
    sm = shade_mask[:, :, None]
    tint = np.array(LEAF_SHADE)[None, None, :] / np.maximum(1e-6, np.array(LEAF_LIT))[None, None, :]
    out = out * (1.0 - sm) + out * tint * sm

    out = out * (1.0 + 0.17 * ridge)[:, :, None]

    rng = np.random.default_rng(seed)
    mott = np.zeros((H, W))
    for cell, amp in ((46, 0.62), (17, 0.38)):
        small = rng.random((H // cell + 2, W // cell + 2))
        mott += amp * (np.asarray(Image.fromarray((small * 255).astype(np.uint8))
                                  .resize((W, H), Image.BICUBIC)).astype(np.float64) / 255.0)
    out = out * (0.955 + 0.09 * mott)[:, :, None]

    # the venation, blended toward a FIXED tone -- see VEIN_DARK
    g = (0.72 * groove)[:, :, None]
    out = out * (1.0 - g) + np.array(VEIN_DARK)[None, None, :] * g

    # THE PLATE'S OWN LOW-FREQUENCY FIELD, clipped tighter than beat 03's. The
    # blade spans his dark face AND the blown grass bed, a low-pass range of ~86
    # to ~215, and an unclipped re-application would brighten the leaf's base by
    # more than the light itself does -- the leaf is a separate near object and
    # should take the scene's light, not the backdrop's local values.
    lp = np.asarray(
        Image.fromarray(luminance(base).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))
    ).astype(np.float64)
    local = lp[ys, xs].mean()
    out = out * np.clip(lp / max(1e-6, local), 0.93, 1.06)[:, :, None]
    return np.clip(out, 0, 255)


def cast_shadow(al, geom, offset=18.0, blur=8.0):
    """The blade's own shadow, thrown along the MEASURED key onto whatever is
    behind it.

    THE CHEAPEST DEPTH CUE THERE IS, AND DRAFT 1 HAD NONE. Decal tell 2 is "a
    pattern ignoring the frame's light"; an object in front of a face, in a key
    the tool has already measured, that throws no shadow at all is that tell in
    its purest form. It is also the only thing in this composite that proves the
    blade is IN the scene rather than ON it, which is exactly the relation the
    beat asks for. Offset is down-left because the key measures up-right.
    """
    H, W = al.shape
    dx = int(round(-LIGHT_DX * offset))
    dy = int(round(-LIGHT_DY * offset))
    shifted = np.zeros_like(al)
    ys0, ys1 = max(0, dy), min(H, H + dy)
    xs0, xs1 = max(0, dx), min(W, W + dx)
    shifted[ys0:ys1, xs0:xs1] = al[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    soft = np.asarray(
        Image.fromarray((np.clip(shifted, 0, 1) * 255).astype(np.uint8))
        .filter(ImageFilter.GaussianBlur(blur))).astype(np.float64) / 255.0
    return np.clip(soft - al, 0.0, 1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", default=PLATE)
    ap.add_argument("--init-sha256", default=PLATE_SHA)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mask-out", required=True)
    ap.add_argument("--mask-grow", type=int, default=10,
                    help="pattern 12's rule is grow > feather so the object's "
                         "own cel outline sits inside the mask's solid core. "
                         "There is no feather here (nothing is erased); the "
                         "outline's half width is 3.1 px and the LANCZOS "
                         "anti-alias support is ~2 px, so 10 clears both with "
                         "margin and does not inflate a mask that is already "
                         "the largest this house has fired.")
    ap.add_argument("--cast-strength", type=float, default=0.20)
    ap.add_argument("--mask-warn-frac", type=float, default=0.35)
    ap.add_argument("--seed", type=int, default=20260820)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not os.path.isfile(a.init):
        sys.exit("!! init not found: %s" % a.init)
    have = sha256_of(a.init)
    if have != a.init_sha256:
        sys.exit("!! INIT SHA MISMATCH -- refusing.\n   want %s\n   have %s"
                 % (a.init_sha256, have))
    print("init %s sha %s OK" % (os.path.basename(a.init), have[:16] + "..."), flush=True)

    arr = np.asarray(Image.open(a.init).convert("RGB")).astype(np.float64)
    H, W, _ = arr.shape
    if (W, H) != (832, 1216):
        sys.exit("!! plate is %dx%d, expected 832x1216" % (W, H))
    lum_p = luminance(arr)
    print("plate %dx%d" % (W, H), flush=True)

    geom = geometry()
    global MARGIN_B
    MARGIN_B = geom["b"]
    a_, b_ = geom["a"], geom["b"]
    aspect = a_ / b_
    cx, cy = geom["centre"]
    ang = geom["angle"]
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    lu = LIGHT_DX * ca + LIGHT_DY * sa
    lv = -LIGHT_DX * sa + LIGHT_DY * ca

    print("LIGHT axis used (%.3f, %.3f), the sigma-60 low pass over the HEAD box "
          "only, corroborated by the blown skull rim top-right and the lit/shadowed "
          "cheek split; the WHOLE-FRAME low pass (%.3f, %.3f) is REJECTED -- the "
          "blown grass bed drags it and it measures the field, not the key"
          % (LIGHT_DX, LIGHT_DY, *LIGHT_WHOLEFRAME_REJECTED), flush=True)
    print("   resolved into leaf coordinates: light . u = %+.2f (along the blade) "
          "and light . v = %+.2f (across it). The apex is lit and the base shaded; "
          "the across-blade component is WEAK, which is why the cel shadow is a "
          "fold and not a half-tone over the whole shaded side." % (lu, lv), flush=True)

    bx0, by0, bx1, by1 = BED_BOX
    bed = np.zeros((H, W), bool)
    bed[by0:by1, bx0:bx1] = True
    bl = lum_p[bed]
    band = arr[bed][(bl > FOLIAGE_BAND[0]) & (bl < FOLIAGE_BAND[1])]
    fx0, fy0, fx1, fy1 = FACE_GRAD_BOX
    gy, gx = np.gradient(lum_p)
    gmag = np.hypot(gx, gy)
    face_line = float(np.percentile(gmag[fy0:fy1, fx0:fx1], 99.9))
    bed_dark = float(lum_p[bed].min())
    print("THE COLOUR COLLISION, re-measured: the plate's own foliage in luma band "
          "%.0f-%.0f means (%.1f, %.1f, %.1f) and his lit forehead is (111, 132, 79) "
          "-- the SAME colour. So the blade is (%.0f, %.0f, %.0f), pushed to true "
          "green (G-R %+.0f) and set between his face (luma 120) and the sunlit bed "
          "(luma %.0f)."
          % (FOLIAGE_BAND[0], FOLIAGE_BAND[1], *band.mean(0), *LEAF_LIT,
             LEAF_LIT[1] - LEAF_LIT[0], float(np.percentile(bl, 55))), flush=True)
    print("THE PLATE'S OWN LINEWORK: face-box per-px luma gradient p99.9 %.1f (the "
          "ceiling C8 holds the drawn outline under); the grass bed has none at all "
          "-- its gradient p99 %.1f, its darkest pixel %.1f (C4's honest floor)"
          % (face_line, float(np.percentile(gmag[bed], 99)), bed_dark), flush=True)

    pts = blade_outline(geom)
    bxs = [p[0] for p in pts]
    bys = [p[1] for p in pts]
    print("BLADE %.0f px long, %.0f px wide, aspect %.2f (band 1.6-2.6); centre "
          "(%.0f,%.0f) at %.0f deg; OVATE -- widest at %.2f of a below the middle, "
          "%.0f%% margin asymmetry, %.0f px rib bow; blunt elliptical apex; 0 lobes, "
          "0 palmate fingers"
          % (2 * a_, 2 * b_, aspect, cx, cy, ang, WIDEST, 100 * ASYM, BOW), flush=True)
    print("VENATION: 1 midrib as an ASYMMETRIC ridge (bright crest, groove 5 px to "
          "the shaded side only, never a drawn line); %d + %d secondaries, not "
          "mirrored, runs 0.19a-0.28a and amplitudes 0.72-1.00 all varying per vein, "
          "each stopping at %.0f%% of the local half-width so none reaches the "
          "margin; no tertiary tier, left for the 12 denoising steps to add so the "
          "pass has something visible to contribute"
          % (len(VEINS_SHADED), len(VEINS_LIT), 100 * VEIN_REACH), flush=True)
    print("OUTLINE weight %.1f-%.1f px around the perimeter, driven by the same "
          "measured light; a constant-width outline is the loudest vector-art tell "
          "and draft 1 had one." % (4.4 - 1.8, 4.4 + 1.8), flush=True)

    if a.dry_run:
        print("DRY RUN -- nothing written.", flush=True)
        return 0

    rgb, al, rim, shade_mask, ridge, groove = draw_leaf(geom, W, H)
    rgb = shade(rgb, al, shade_mask, ridge, groove, arr, seed=a.seed)
    cast = cast_shadow(al, geom)
    a3 = al[:, :, None]
    shadowed = arr * (1.0 - a.cast_strength * cast)[:, :, None]
    # THE CAST SHADOW'S SUPPORT IS WHERE IT ACTUALLY CHANGES A PIXEL, not where
    # its float is nonzero. A Gaussian is unbounded, and counting its whole tail
    # inflated the mask by 12 points of frame for pixels that round to no change
    # at all.
    cast_support = np.abs(np.round(shadowed) - arr).max(axis=2) > 0
    out = shadowed
    out = out * (1.0 - a3) + rgb * a3
    r3 = (rim * (al > 0.02))[:, :, None]
    out = np.clip(out * (1.0 - r3) + np.array(RIM_RGB)[None, None, :] * r3, 0, 255)
    out = np.round(out)

    drawn = al > 0.02
    solid = al > 0.9
    # THE FOOTPRINT IS DECLARED AND IT INCLUDES TWO THINGS BESIDES THE OBJECT --
    # the LANCZOS anti-alias support (alpha above 0 but below the 0.02 the object
    # mask uses) and the cast shadow. Draft 1's C1 counted 2388 px changed
    # "outside the footprint" because the footprint was the object rather than
    # the pixels this tool determines. Both extras are printed rather than
    # excused, and both are inside the inpaint mask so no seam falls on them.
    aa_support = (al > 0.0) & ~drawn
    touched = drawn | aa_support | cast_support
    mask = binary_dilate(drawn | cast_support, a.mask_grow)
    Image.fromarray(out.astype(np.uint8)).save(a.out)
    Image.fromarray((mask * 255).astype(np.uint8)).save(a.mask_out)

    # ---- the pre-registered checks. A failed check is named, not absorbed. ----
    fails = []
    lum_o = luminance(out)
    changed = np.abs(out - arr).max(axis=2) > 0
    c1 = int((changed & ~touched).sum())

    c2 = bool(min(bxs) > 2 and max(bxs) < W - 3 and min(bys) > 2 and max(bys) < H - 3)
    c3 = blob_count(drawn, 250)

    dys, dxs = np.nonzero(drawn)
    drawn_dark = float(lum_o[solid].min())
    foot = np.zeros((H, W), bool)
    foot[dys.min():dys.max() + 1, dxs.min():dxs.max() + 1] = True
    plate_dark = float(lum_p[foot].min())
    c4 = drawn_dark >= plate_dark

    c5 = 1.6 <= aspect <= 2.6
    mask_frac = float(mask.mean())
    drawn_frac = float(drawn.mean())

    gy2, gx2 = np.gradient(lum_o)
    gmag_o = np.hypot(gx2, gy2)
    rim_px = (rim > 0.5) & solid
    vein_px = ((ridge > 0.35) | (groove > 0.35)) & solid & ~binary_dilate(rim > 0.05, 3)
    rim_grad = float(np.percentile(gmag_o[rim_px], 99)) if rim_px.any() else 0.0
    vein_grad = float(np.percentile(gmag_o[vein_px], 99)) if vein_px.any() else 0.0
    vein_dark = float(lum_o[vein_px].min()) if vein_px.any() else 255.0
    rim_dark = float(lum_o[rim_px].min()) if rim_px.any() else 0.0
    c7 = (vein_grad < rim_grad) and (vein_dark > rim_dark)
    c8 = rim_grad <= face_line

    fbx0, fby0, fbx1, fby1 = FACE_BOX
    fb = np.zeros((H, W), bool)
    fb[fby0:fby1, fbx0:fbx1] = True
    face_px = int(fb.sum())
    c9 = int((drawn & fb).sum())

    # C10 -- NO LOBES, MEASURED DIRECTLY. A lobed or palmate blade has MORE THAN
    # ONE maximum in its half-width profile; an ordinary leaf has exactly one.
    # THIS REPLACED A CONVEXITY BAR AND THE REASON IS WORTH KEEPING: convexity is
    # a proxy, and it fails a gently curved leaf, which is not a lobed one -- a
    # 12 px rib bow costs 3.6 points of hull ratio all by itself. The direct
    # question is how many lobes there are, so that is what is counted, and
    # convexity is reported beside it rather than scored.
    prof = [half_width_frac(-1.0 + 2.0 * i / 400.0) for i in range(401)]
    peaks = sum(1 for i in range(1, len(prof) - 1)
                if prof[i] > prof[i - 1] + 1e-9 and prof[i] >= prof[i + 1] - 1e-9)
    hull = _convex_hull(pts)
    convexity = _poly_area(pts) / max(1e-9, _poly_area(hull))
    tip_w = half_width_frac(0.90)
    c10 = (peaks == 1) and (tip_w >= 0.18)

    blade_only = solid & ~binary_dilate(rim > 0.05, 2)
    g0, g1 = np.gradient(lum_o)
    det_leaf = float((np.abs(g0)[blade_only].mean() + np.abs(g1)[blade_only].mean()) / 2.0)
    fmask = np.zeros((H, W), bool)
    fmask[200:560, 200:640] = True
    fmask &= ~touched
    p0, p1 = np.gradient(lum_p)
    det_face = float((np.abs(p0)[fmask].mean() + np.abs(p1)[fmask].mean()) / 2.0)

    print("")
    print("C1  px changed outside the DECLARED footprint %-6d       (== 0)   %s"
          % (c1, "PASS" if c1 == 0 else "FAIL"))
    print("    footprint = object %d px + anti-alias support %d px + cast shadow "
          "%d px, all three printed rather than excused"
          % (int(drawn.sum()), int(aa_support.sum()), int(cast_support.sum())))
    print("C2  WHOLE BLADE inside the frame %-5s (bbox x%.0f..%.0f y%.0f..%.0f; the "
          "petiole leaves through the bottom edge on purpose)   %s"
          % (c2, min(bxs), max(bxs), min(bys), max(bys), "PASS" if c2 else "FAIL"))
    print("C3  drawn components >=250 px: %d %s                      (== 1)   %s"
          % (len(c3), c3, "PASS" if len(c3) == 1 else "FAIL"))
    print("C4  darkest SOLID drawn luma %.1f vs the plate's own %.1f in the footprint "
          "bbox (>=) %s" % (drawn_dark, plate_dark, "PASS" if c4 else "FAIL"))
    print("    beside the grass bed's own darkest %.1f (margin %+.1f) -- REPORTED, "
          "not a bar. The bed is drawn OUT OF FOCUS and carries no linework at "
          "all, so it is a floor for a FILL tone and not for a line; a sharp "
          "foreground object may legitimately out-darken a blurred backdrop. The "
          "reference for a LINE is the plate's own linework, and that is C8."
          % (bed_dark, drawn_dark - bed_dark))
    print("C5  blade aspect %.2f                                  (1.6-2.6) %s"
          % (aspect, "PASS" if c5 else "FAIL"))
    print("C6  MASK FRACTION %d px = %.2f%% of frame (drawn footprint alone %.2f%%)"
          % (int(mask.sum()), 100 * mask_frac, 100 * drawn_frac))
    if mask_frac > a.mask_warn_frac:
        print("    !! OVER %.0f%% -- AN ORDER OF MAGNITUDE ABOVE EVERY MASK THAT HAS "
              "PASSED HERE (4.10%% and 7.97%% on beat 13). A 0.30 pass over most of a "
              "picture is a RE-RENDER, not an inpaint. STRENGTH IS PRE-REGISTERED AS "
              "ITS OWN SEPARATE RUNG and 0.30 still fires as the one sample, because "
              "0.30 is the house value and moving it alongside the object class "
              "measures neither." % (100 * a.mask_warn_frac))
    print("C7  LINE HIERARCHY on the finished pixels: outline p99 gradient %.1f and "
          "darkest %.1f; venation p99 gradient %.1f and darkest %.1f -- venation "
          "must be strictly WEAKER on both      %s"
          % (rim_grad, rim_dark, vein_grad, vein_dark, "PASS" if c7 else "FAIL"))
    print("C8  the drawn outline is not stronger than the plate's OWN linework: "
          "%.1f vs the face box's p99.9 %.1f            (<=)     %s"
          % (rim_grad, face_line, "PASS" if c8 else "FAIL"))
    print("C9  THE OCCLUSION RELATION: %d drawn px inside his measured face box %s "
          "= %.1f%% of it                    (> 40000) %s"
          % (c9, FACE_BOX, 100.0 * c9 / face_px, "PASS" if c9 > 40000 else "FAIL"))
    print("C10 NO LOBES, counted rather than promised: %d maximum in the half-width "
          "profile (== 1) and tip half-width at 0.90a is %.2f of b (>= 0.18, a lance "
          "tip is ~0)                %s"
          % (peaks, tip_w, "PASS" if c10 else "FAIL"))
    print("    convexity %.4f, REPORTED not scored. The %.0f px rib bow does NOT "
          "cost it -- the oval's own curvature is an order of magnitude larger, "
          "so the shape stays convex -- but convexity is the wrong instrument "
          "anyway: it is a proxy that would fail a curved leaf, and 'how many "
          "lobes' is a question that can be counted directly." % (convexity, BOW))
    print("    detail filter (never a verdict): mean |grad| inside the blade %.2f "
          "against the plate's own untouched face %.2f" % (det_leaf, det_face))

    if c1 != 0: fails.append("FAIL-WROTE-OUTSIDE-ITS-FOOTPRINT(C1)")
    if not c2: fails.append("FAIL-BLADE-CROPPED(C2)")
    if len(c3) != 1: fails.append("FAIL-NOT-ONE-COMPONENT(C3)")
    if not c4: fails.append("FAIL-DRAWN-DARKER-THAN-THE-PLATE(C4)")
    if not c5: fails.append("FAIL-ASPECT-OUT-OF-BAND(C5)")
    if not c7: fails.append("FAIL-INTERNAL-LINE-STRONGER-THAN-THE-OUTLINE(C7)")
    if not c8: fails.append("FAIL-OUTLINE-STRONGER-THAN-THE-DIALECT(C8)")
    if c9 <= 40000: fails.append("FAIL-NO-OCCLUSION-RELATION(C9)")
    if not c10: fails.append("FAIL-LOBED-OR-LANCE(C10)")

    out_sha = sha256_of(a.out)
    mask_sha = sha256_of(a.mask_out)
    meta = {
        "tool": "pipeline/beat16_leaf_composite.py",
        "sampler": "NONE -- plain image processing, $0, no GPU, no network",
        "init": os.path.relpath(os.path.abspath(a.init), REPO),
        "init_sha256": have,
        "composite_sha256": out_sha,
        "mask_png": os.path.basename(a.mask_out),
        "mask_sha256": mask_sha,
        "mask_px": int(mask.sum()),
        "mask_frac_of_frame": round(mask_frac, 4),
        "drawn_footprint_frac": round(drawn_frac, 4),
        "mask_frac_note": (
            "THE LARGEST MASK THIS HOUSE HAS FIRED, by an order of magnitude: "
            "beat 13's passing parent was 4.10 percent and its tall variant "
            "7.97 percent. The work ladder's warning is that a 0.30 pass over "
            "most of a picture is a re-render rather than an inpaint. STRENGTH "
            "IS NOT MOVED IN RESPONSE -- it is pre-registered as its own "
            "separate rung, because changing the object class and the strength "
            "in one fire measures neither."),
        "rng_seed": a.seed,
        "blade_px": [int(2 * a_), int(2 * b_)],
        "blade_aspect": round(aspect, 3),
        "blade_centre_px": [int(cx), int(cy)],
        "blade_angle_deg": ang,
        "blade_shape": ("ovate, widest at %.2f of a below the middle, %.0f%% "
                        "margin asymmetry, %.0f px rib bow, blunt elliptical "
                        "apex. |cos|^0.82 -- beats 03 and 15's profile -- was "
                        "NOT carried: at their 50 px its extra bluntness is "
                        "sub-pixel and at 800 px it reads as a paddle."
                        % (WIDEST, 100 * ASYM, BOW)),
        "light_axis_used": [LIGHT_DX, LIGHT_DY],
        "light_axis_rejected_wholeframe": list(LIGHT_WHOLEFRAME_REJECTED),
        "light_in_leaf_coords": {"along_blade": round(lu, 3), "across_blade": round(lv, 3)},
        "cast_shadow": ("offset %.0f px down-left along the measured key, blur "
                        "%.0f, strength %.2f. Declared in the footprint and "
                        "inside the inpaint mask; its support is measured as "
                        "the pixels it actually changes." % (18.0, 8.0, a.cast_strength)),
        "palette_measured_and_why_it_was_moved": (
            "The plate's own foliage (grass bed, luma band 90-140) means "
            "(107.3, 128.1, 79.6) and the goblin's lit forehead is (111, 132, 79) "
            "-- THE SAME COLOUR to within four levels in every channel. Drawing "
            "the blade in the plate's own plant colour, which is this house's "
            "practice, would make it INVISIBLE over the part of the frame it most "
            "needs to occlude. It is therefore moved along ONE named axis, "
            "saturation toward true green, to a tone neither the yellow-green "
            "grass nor the olive skin occupies."),
        "what_this_rung_does_NOT_fix": (
            "FOCUS. The plate's focal plane is on HIM -- his face is sharp and "
            "the near grass is blurred -- so the depth delivered here is "
            "occlusion and scale, not the brief's 'blurred behind it'. Blurring "
            "him means writing outside the drawn footprint, which C1 forbids and "
            "which would put a second variable in the same fire. SCALE, too: he "
            "still fills the frame, because that is the plate's own recorded "
            "fault and no composite reaches it. Both are the reason this is "
            "evidence for a taste question and not a candidate frame."),
        "checks": {
            "C1_outside_footprint_px": c1,
            "C1_object_px": int(drawn.sum()),
            "C1_antialias_support_px": int(aa_support.sum()),
            "C1_cast_shadow_px": int(cast_support.sum()),
            "C2_blade_inside_frame": bool(c2),
            "C3_components": c3,
            "C4_drawn_dark": round(drawn_dark, 1),
            "C4_plate_dark_footprint": round(plate_dark, 1),
            "C4_plate_dark_grass_bed": round(bed_dark, 1),
            "C5_aspect": round(aspect, 3),
            "C6_mask_frac": round(mask_frac, 4),
            "C7_outline_grad_p99": round(rim_grad, 1),
            "C7_vein_grad_p99": round(vein_grad, 1),
            "C7_outline_darkest": round(rim_dark, 1),
            "C7_vein_darkest": round(vein_dark, 1),
            "C8_plate_face_grad_p999": round(face_line, 1),
            "C9_drawn_px_in_face_box": c9,
            "C9_face_box_frac": round(c9 / float(face_px), 3),
            "C10_halfwidth_maxima": peaks,
            "C10_tip_halfwidth_frac": round(tip_w, 3),
            "C10_convexity_reported": round(convexity, 4),
            "detail_mean_grad_blade": round(det_leaf, 2),
            "detail_mean_grad_plate_face": round(det_face, 2),
        },
        "fails": fails,
        "geometry_is_the_stewards": (
            "The centre, the angle and the size are STAGING and they are the "
            "steward's. The founder has ruled on leaf SHAPE and this obeys that "
            "ruling; he has not ruled on where a leaf sits in a frame, and "
            "'lower', 'smaller', 'other side' is one number and one $0 redraw."),
        "approved": False,
        "provisional": True,
        "is_show_content": False,
        "is_show_content_why": (
            "CARD EVIDENCE FOR /review/ep2-b16-leaf-0820 AND NOTHING ELSE. This "
            "frame deliberately builds the shot canon.yaml "
            "sapling-cotyledon-shape currently forbids -- 'no leaf whose SHAPE is "
            "the subject of the shot' -- so that the author can look at what "
            "licensing it buys instead of imagining it. review/inbox.yaml recorded "
            "this composite as named and deliberately NOT fired, because spending "
            "it before his word would be answering a ruling with a render; it "
            "fires now only under the standing directive that every option on an "
            "open card carries pixels, and that reasoning is not retracted. CANON "
            "IS UNCHANGED. No clip, no episode and no publication may be built on "
            "these bytes, and passing every check above changes none of that -- a "
            "check measures whether the tool did its job, and whether this shot "
            "may exist at all is a taste call reserved to the author (R4)."),
        "date": date.today().isoformat(),
    }
    with open(a.out + ".meta.yaml", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join("%s: %s" % (k, json.dumps(v, default=int))
                           for k, v in meta.items()) + "\n")

    print("")
    print("WROTE %s sha %s" % (a.out, out_sha))
    print("WROTE %s sha %s" % (a.mask_out, mask_sha))
    print("WROTE %s.meta.yaml" % a.out)
    if fails:
        print("COMPOSITE FAILED: %s -- no GPU runs on a failed composite."
              % ", ".join(fails))
        return 3
    print("COMPOSITE PASSES C1-C10. NOW OPEN IT AT FULL RESOLUTION: a metric is a "
          "filter, never a verdict, and the five decal tells are checked by eye.")
    return 0


def _poly_area(pts):
    s = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        s += x0 * y1 - x1 * y0
    return abs(s) / 2.0


def _convex_hull(pts):
    p = sorted(set((round(x, 6), round(y, 6)) for x, y in pts))
    if len(p) < 3:
        return list(p)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lo = []
    for q in p:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    up = []
    for q in reversed(p):
        while len(up) >= 2 and cross(up[-2], up[-1], q) <= 0:
            up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]


if __name__ == "__main__":
    raise SystemExit(main())
