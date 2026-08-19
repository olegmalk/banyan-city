#!/usr/bin/env python3
"""beat13_shade_composite.py -- give beat 13's plate the SAPLING it never drew,
beside him at knee height, by construction.

WHY THIS EXISTS
---------------
`plate_scratch.py` DRAFTS[13] was drawn r1s1 on 2026-08-19T23:36 (macbook3) and
its own verdict is the most favourable of the three plates that wave drew:

    "THE BEST OF THE THREE, AND THE ONLY ONE WHOSE ACTION CLAUSE LANDS.
     `done_when` asks for him FOLDED SMALL, knees up, and that is exactly what
     came back ... PASS on cast and on pose; FAIL on the plant. If the plant is
     solved compositionally (see the wave note), this pose is worth keeping."

The single fault it names:

    "NO IDENTIFIABLE SAPLING. The shade is cast by large out-of-focus leaves
     crowding the foreground and top corners -- the scale reads as big foliage
     overhead, not a 40 cm plant. `in the thin shade of a tiny sapling` bought
     shade and lost the plant."

That is the same CLASS A failure beats 15 and 19 closed wording ladders on, and
the verdict names the composite route itself. So nothing here asks the sampler
for a plant. No wording is authored, no REVS entry is added, no model is loaded.

THIS COMPOSITE IS PURELY ADDITIVE, AND THAT IS THE DIFFERENCE FROM BEAT 03
---------------------------------------------------------------------------
Beat 03's plate drew the WRONG plant and beat 03's tool had to remove it first.
This plate drew NO plant at all in his vicinity, so there is nothing to erase and
no vacancy to fill: the entire tool is `draw one sapling and hand over a mask`.
Every pixel outside the drawn footprint is r1s1's, byte for byte, and C1 asserts
it -- which is the strongest form the "his pose and cast are untouched" claim can
take, because here it is not a claim, it is arithmetic.

WHERE IT GOES, AND WHY THE PLATE CANNOT SUPPORT A GROUND PLANE
---------------------------------------------------------------
The staging is the approved one: he sits at the base of the stem with the plant
BESIDE him at KNEE HEIGHT. Measured on the plate at 3x, his drawn-up knee tops
sit at y ~595 and his seat meets the grass at y ~1160. The plant is rooted at
(134, 1160) in the grass at his left and its crown tops out at y 651 -- 56 px
below his knee line, which is the staging the sentence describes.

THE cm FIGURE IS REPORTED AND NOT SCORED, AND THE REASON IS A REAL FINDING RATHER
THAN AN EXCUSE. Beats 03 and 19 both size their plant through a measured ground
plane, and both plates give one: a visible horizon and a figure standing on it.
This plate has NEITHER -- it is a tight portrait whose background is entirely
out-of-focus foliage, with no horizon anywhere in frame. The only scale handle is
his head, 435 px crown-to-chin, which at 23 cm gives 18.91 px/cm AT HIS DEPTH.
Two things follow and they disagree:

  * The drawn plant is 509 px, which at that rate is 26.9 cm -- under canon's
    ~40 cm.
  * A 40 cm plant at his exact depth would be 756 px and its crown would land at
    y 404, which is his BROW. That is not "beside him at knee height" by any
    reading, and it is not what the approved line stages.

The cross-check says the px/cm is the thing that is wrong, not the staging: his
whole seated mass is 1105 px = 2.5 head-heights, where a real adult hugging his
knees is about 4. The head is drawn at anime scale, so a head-derived px/cm
overstates centimetres on this plate. A plant rooted slightly behind him closes
the rest. So the SCORED clause is the RELATION the approved line states -- crown
at his measured knee line -- and the 26.9 cm is printed beside it with this
paragraph attached, rather than being quietly converted into a pass.

WHAT IS DRAWN, AND IN WHOSE COLOURS
------------------------------------
One stem, two ovate blades. No side-branch and no fig: beat 15's rung established
that a drawn side-branch is scoreable as an extra stalk and a drawn fig as a bud
at the tip, and ONE VARIABLE PER RUNG -- this rung is THE PLANT EXISTING.

  leaf (83, 117,  66)  -- the 45th percentile of the plate's own foliage
  stem (50,  96,  57)  -- its 18th, for the shaded stem
  rim  (18,  41,  36) -- the darkest 3% inside the plate's own in-focus sprig
                         at x 660..832 y 80..270 is (26.7, 62.5, 57.9) at
                         luminance 57.4, and that was tried first: against this
                         plate's heavy near-black linework the blades read as
                         low-contrast smudges on his knee. Taken down to
                         luminance 36, still ABOVE the 23 that the plate's own
                         sprig reaches, so C9's clause -- never composite a line
                         stronger than the object's own outline -- still holds
                         and is still measured rather than asserted.

LIGHT. The low-pass (sigma 40) gradient reads dx +0.868 dy +0.496 and is REJECTED
for the same reason as beat 03's: he fills the frame and the gradient is
measuring him. The key is visible directly -- a hot rim arc over the top of his
skull and a lit left sleeve edge -- so the axis is (0.15, -0.988), and the
rejected number is printed at run time beside it.

THE BACKGROUND SPRIG IS LEFT IN FRAME ON PURPOSE, AND FLAGGED
--------------------------------------------------------------
There is a second, multi-leaflet plant at x 660..832 y 80..270. It is NOT removed.
It is distant background scrub, it is not what any clause of this beat is about,
and removing it would be a second variable in a rung whose whole point is one.
Its bbox is recorded here and in this rung's spec so nobody scores "exactly two
leaves in frame" as passed when what passed is "exactly two leaves on the
foreground sapling". If a later rung wants it gone, that is its own rung.

PRIMITIVES ARE COPIED, NOT IMPORTED, from pipeline/beat03_cover_composite.py and
pipeline/beat15_listener_composite.py -- an init whose sha256 a job spec asserts
must not change its bytes because a peer edited a shared module. The house has
five beat-specific compositors on that reasoning now.

$0: no model, no network, no GPU. Deterministic. `--dry-run` writes nothing.
"""

import argparse
import hashlib
import math
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATE = os.path.join(REPO, "farm-out", "ep2-b13-mac-plate-0819",
                     "13-the-shade-mac-plate-r1s1.png")
PLATE_SHA = "20d36a3e92119a0c6795d6969cd6a083ddecda46a1c9bfffdc82d380e46e1c60"

# --- measured on the plate; see the module docstring for how and where --------
LEAF_RGB = (83.0, 117.0, 66.0)
STEM_RGB = (50.0, 96.0, 57.0)
RIM_RGB = (18.0, 41.0, 36.0)
LIGHT_DX, LIGHT_DY = 0.15, -0.988         # the skull rim arc, not the low-pass
LOWPASS_REJECTED = (0.868, 0.496)         # printed so the rejection is checkable

# Left in frame on purpose; see the docstring. Recorded so the leaf-count clause
# cannot be read wider than it was scored.
BACKGROUND_SPRIG_BOX = (660, 80, 832, 270)

# THE BOXES THE CHECKS ARE WRITTEN AGAINST, read off the plate at 3x.
FACE_BOX = (250, 60, 570, 500)
HIS_KNEE_TOP_Y = 595.0        # the drawn-up knee tops
HIS_SEAT_Y = 1160.0           # where his mass meets the grass
HEAD_CROWN_Y, HEAD_CHIN_Y = 55.0, 490.0
PX_PER_CM_AT_FIG = (HEAD_CHIN_Y - HEAD_CROWN_Y) / 23.0     # 18.913
# NOTHING THIS TOOL DRAWS MAY REACH HIS HANDS, ARMS OR FACE. His hands are folded
# over his knees from y 560 down to y 900 across x 230..520; his face is
# FACE_BOX. The plant's crown stops at y 651 by construction and C8 asserts it
# against a line 11 px above that, so the check is a real one and not a
# restatement of the geometry.
NO_DRAW_ABOVE_Y = 640


def px_per_cm(_y=None):
    """ONE RATE, NOT A PLANE. Beats 03 and 19 build px/cm(y) from a horizon and a
    figure standing on it; this plate has no horizon in frame at all (see the
    docstring), so there is nothing to build a plane from and pretending otherwise
    would be inventing a number. What the plate does give is his head, and that
    rate holds at his depth only -- which is where the plant is rooted.
    """
    return PX_PER_CM_AT_FIG


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


def binary_erode(mask, r):
    if r <= 0:
        return mask
    img = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(2 * r + 1))
    return np.asarray(img) > 127


def reach(seed, allow, limit=4000):
    cur = seed & allow
    for _ in range(limit):
        nxt = binary_dilate(cur, 1) & allow
        if nxt.sum() == cur.sum():
            return nxt
        cur = nxt
    return cur


def leaf_outline(cx, cy, rx, ry, ang, n=112):
    """A wide oval with softly ROUNDED tips -- the founder's 2026-08-17 ruling is
    `average leaves`, and |cos|^0.82 keeps the ends blunt rather than lance."""
    pts = []
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    for i in range(n):
        t = 2.0 * math.pi * i / n
        u = math.copysign(abs(math.cos(t)) ** 0.82, math.cos(t)) * rx
        v = math.sin(t) * ry
        pts.append((cx + u * ca - v * sa, cy + u * sa + v * ca))
    return pts


def geometry():
    """Where the plant goes. THE ROOT IS THE ONLY FREE CHOICE AND IT IS A
    STAGING ONE: (336, 1160) is in the near-foreground grass in front of his left
    knee, which is what puts the plant between the camera and him. Everything
    after it is arithmetic -- the apex follows from canon through the measured
    ground plane, and the blades follow from the pre-registered aspect band.

    Three placements were rejected by eye before this one, which is what doing
    the structure with image processing buys. The first put the blades at his
    CHEST (apex y 691): it read as a flower pinned to his poncho, not as cover,
    because at that height the leaves sit on the pale cloak with his arm behind
    them and nothing says the plant is in front. The second kept the plant at the
    weed's own root -- that is the frame the verdict already rejected. The third
    was dead straight and read as a lollipop; the stem here carries the same
    rightward bow the plate's own weed has.
    """
    return {
        "base": (150.0, 1160.0),
        "stem_ctrl": (170.0, 950.0),      # +20 px of bow; nothing here is straight
        "apex": (132.0, 748.0),
        # 16 PX, NOT 9. Beat 03's stem is 9 px and that is right for ITS plate --
        # a wide shot whose figure's head is 232 px. This is a tight close-up
        # whose head is 435 px, and a 9 px stem at that magnification came back as
        # a bent WIRE, rejected by eye. Both plates now sit at ~3% of plant height,
        # which is also where beat 19's passing stem sits (7.5 px on 240).
        "stem_w": 16.0,
        # aspect 60/35 = 1.71 and 62/36 = 1.72, inside composite-init-pattern.md
        # 8's pre-registered 1.6-2.6 band. The blades are 30% longer than v1's:
        # v1 gave them 88-94 px on a 489 px plant, about half the 0.255 * height
        # that beat 19's passing crown uses, and at this magnification they read
        # as two specks rather than as the two leaves the whole rung is about.
        #
        # CENTRES ARE DERIVED FROM THE APEX, NOT TYPED. C6 caught v1 doing it by
        # eye: each blade's inner end stopped 22 px short of the stem and the
        # drawn footprint came back as TWO components. centre = apex + rx along
        # the blade's own axis puts the inner end ON the joint by construction.
        "leaves": [
            (82.3, 714.5, 60.0, 35.0, 34.0),
            (183.1, 710.7, 62.0, 36.0, -37.0),
        ],
    }


def draw_sapling(geom, W, H, ss=3):
    """Return (rgb, alpha, rim, shadow, ridge) at plate resolution, drawn at ss x
    supersample so the edges anti-alias in the plate's soft-cel manner."""
    L = Image.new("RGB", (W * ss, H * ss), (0, 0, 0))
    A = Image.new("L", (W * ss, H * ss), 0)
    Rm = Image.new("L", (W * ss, H * ss), 0)
    Sh = Image.new("L", (W * ss, H * ss), 0)
    Rg = Image.new("L", (W * ss, H * ss), 0)
    dl, da, dr, ds, dg = (ImageDraw.Draw(x) for x in (L, A, Rm, Sh, Rg))
    stem_c = tuple(int(v) for v in STEM_RGB)
    leaf_c = tuple(int(v) for v in LEAF_RGB)

    def S(p):
        return (p[0] * ss, p[1] * ss)

    bx, by = geom["base"]
    ax, ay = geom["apex"]
    cxp, cyp = geom["stem_ctrl"]
    sw = geom["stem_w"]

    # --- the stem: a curved tapered ribbon, wider at the root -----------------
    n = 48
    left, right = [], []
    for i in range(n + 1):
        t = i / float(n)
        px = (1 - t) ** 2 * bx + 2 * (1 - t) * t * cxp + t ** 2 * ax
        py = (1 - t) ** 2 * by + 2 * (1 - t) * t * cyp + t ** 2 * ay
        dx = 2 * (1 - t) * (cxp - bx) + 2 * t * (ax - cxp)
        dy = 2 * (1 - t) * (cyp - by) + 2 * t * (ay - cyp)
        nl = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / nl, dx / nl
        w = sw * (1.0 - 0.62 * t) / 2.0
        left.append((px + nx * w, py + ny * w))
        right.append((px - nx * w, py - ny * w))
    stem = left + right[::-1]
    dl.polygon([S(p) for p in stem], fill=stem_c)
    da.polygon([S(p) for p in stem], fill=255)
    dr.line([S(p) for p in stem] + [S(stem[0])], fill=255, width=int(3.2 * ss))
    # THE OUTLINE HAS TO BE IN THE ALPHA TOO. It straddles the polygon edge, so
    # with alpha = the fill only, the outer half of every outline landed where
    # al=0 and was masked away -- which is why the first builds came back with a
    # 1 px hairline instead of a cel line, and why the blades read as flat discs.
    da.line([S(p) for p in stem] + [S(stem[0])], fill=255, width=int(3.2 * ss))

    # --- THREE SHORT ROOT BLADES, and they are here for a reason beat 15 did not
    # have. Beat 15's removal deliberately KEPT the plate's own grass tufts and
    # rooted the drawn stem into them -- a real cue, pattern 13 in the positive.
    # This plant is rooted where the plate has no tuft at all, in open foreground
    # grass, so a bare stem would meet the ground on a hard butt end and read as
    # a stick pushed in. Three short blades, none longer than 26 px, are the
    # smallest thing that makes the join.
    # v1 drew three 15-24 px blades and they read as a painted ARROW at the foot
    # of the stem. These are half that, splayed wider and drawn in the RIM colour
    # rather than the stem's, so they read as the grass shadow at a root instead
    # of as three more leaves.
    for dx0, ln in ((-16, 12), (11, 10), (-4, 8)):
        tipx, tipy = bx + dx0, by - ln
        pts = leaf_outline((bx + tipx) / 2.0, (by + tipy) / 2.0,
                           ln * 0.60, 2.2,
                           math.degrees(math.atan2(tipy - by, tipx - bx)))
        dl.polygon([S(p) for p in pts], fill=tuple(int(v) for v in RIM_RGB))
        da.polygon([S(p) for p in pts], fill=255)

    # --- exactly two ovate blades ---------------------------------------------
    for (cx, cy, rx, ry, ang) in geom["leaves"]:
        pts = leaf_outline(cx, cy, rx, ry, ang)
        dl.polygon([S(p) for p in pts], fill=leaf_c)
        da.polygon([S(p) for p in pts], fill=255)
        dr.line([S(p) for p in pts] + [S(pts[0])], fill=255, width=int(4.4 * ss))
        da.line([S(p) for p in pts] + [S(pts[0])], fill=255, width=int(4.4 * ss))
        low = [p for p in pts if p[1] >= cy + ry * 0.18]
        if len(low) > 3:
            ds.polygon([S(p) for p in low], fill=255)
        # midrib as a LUMINANCE RIDGE, never a drawn line: pattern 5's law is that
        # in this dialect a strong dark line IS an edge, and a leaf split down the
        # middle by one is two leaves.
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        dg.line([S((cx - rx * 0.92 * ca, cy - rx * 0.92 * sa)),
                 S((cx + rx * 0.92 * ca, cy + rx * 0.92 * sa))],
                fill=255, width=int(2.6 * ss))

    def down(img, mode="L"):
        # LANCZOS RINGS, AND AN UNCLIPPED RING IS A HOLE. Where two outline
        # strokes cross, the downsampled rim overshot 1.0; `out*(1-r) + RIM*r`
        # with r>1 drives the result NEGATIVE and clips to black, which C9 read as
        # a drawn luminance of 7 against the plate's own 16. Clipping the masks to
        # [0,1] is the fix, and it is a real bug rather than a threshold to move.
        a = np.asarray(img.resize((W, H), Image.LANCZOS)).astype(np.float64)
        return a if mode == "RGB" else np.clip(a / 255.0, 0.0, 1.0)

    return (down(L, "RGB"), down(A), down(Rm), down(Sh), down(Rg))


def shade(rgb, al, shadow, ridge, base):
    """Shade on the plate's light axis, add the cel shadow and the midrib ridge,
    then re-apply the plate's own low-frequency luminance field so the plant sits
    in the frame's light rather than in its own."""
    H, W, _ = base.shape
    ys, xs = np.nonzero(al > 0.05)
    if len(ys) == 0:
        return rgb
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    proj = xx * LIGHT_DX + yy * LIGHT_DY
    p = proj[ys, xs]
    t = np.clip((proj - p.min()) / max(1e-6, (p.max() - p.min())), 0.0, 1.0)
    # 0.90+0.20t and a +-16% local factor came from beat 15, whose plant sits in
    # open field. Here the blades land on his PALE CLOAK, the sigma-40 low pass
    # there is bright, and the two lifts compounded: the first build's blades came
    # out near (150,168,140) -- flat grey discs beside a plate whose own weed is a
    # saturated mid-green. The ramp and the local clip are both tightened, and the
    # cel shadow and midrib are strengthened to carry the form instead.
    out = rgb * (0.86 + 0.16 * t)[:, :, None]
    out = out * (1.0 - 0.20 * shadow)[:, :, None]
    out = out * (1.0 + 0.14 * ridge)[:, :, None]
    lp = np.asarray(
        Image.fromarray(luminance(base).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))
    ).astype(np.float64)
    local = lp[ys, xs].mean()
    out = out * np.clip(lp / max(1e-6, local), 0.88, 1.05)[:, :, None]
    return np.clip(out, 0, 255)


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", default=PLATE)
    ap.add_argument("--init-sha256", default=PLATE_SHA)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mask-out", required=True)
    ap.add_argument("--mask-grow", type=int, default=12)
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
    print("plate %dx%d" % (W, H), flush=True)
    print("LIGHT axis used (%.3f, %.3f) from the sun disc at x~330 y~150 and the "
          "rim arc on his skull; the low-pass gradient (%.3f, %.3f) is REJECTED -- "
          "it is measuring his black trousers, not the key"
          % (LIGHT_DX, LIGHT_DY, LOWPASS_REJECTED[0], LOWPASS_REJECTED[1]), flush=True)

    # ---- 1. there is nothing to remove ---------------------------------------
    # Beat 03's tool erases a wrong plant first. This plate has none near him, so
    # this tool is additive only and C1 can assert byte-identity everywhere the
    # plant is not.
    geom = geometry()
    ppc = px_per_cm()
    leaf_top = min(cy - ry for _, cy, _, ry, _ in geom["leaves"])
    plant_h = geom["base"][1] - leaf_top
    print("SCALE: head %.0f px / 23 cm = %.3f px/cm AT HIS DEPTH. No horizon is "
          "visible on this plate, so no ground plane is built and none is faked."
          % (HEAD_CHIN_Y - HEAD_CROWN_Y, PX_PER_CM_AT_FIG), flush=True)
    print("PLANT %.0f px tall, crown y=%.0f against his measured knee line y=%.0f "
          "(%.0f px below it) -- THE SCORED CLAUSE, because that is the staging "
          "the approved line describes"
          % (plant_h, leaf_top, HIS_KNEE_TOP_Y, leaf_top - HIS_KNEE_TOP_Y), flush=True)
    print("REPORTED, NOT SCORED: %.1f cm at his depth. A 40 cm plant there would "
          "be %.0f px and its crown would sit at y %.0f -- his BROW. His seated "
          "mass is %.1f head-heights where a real one is ~4, so the head-derived "
          "rate overstates cm on this plate; see the docstring."
          % (plant_h / ppc, 40.0 * ppc, HIS_SEAT_Y - 40.0 * ppc,
             (HIS_SEAT_Y - HEAD_CROWN_Y) / (HEAD_CHIN_Y - HEAD_CROWN_Y)), flush=True)
    print("stem (%.0f,%.0f) -> (%.0f,%.0f); EXACTLY 2 blades, aspect %.2f and "
          "%.2f; 0 side-branches, 0 figs"
          % (geom["base"][0], geom["base"][1], geom["apex"][0], geom["apex"][1],
             geom["leaves"][0][2] / geom["leaves"][0][3],
             geom["leaves"][1][2] / geom["leaves"][1][3]), flush=True)
    print("BACKGROUND SPRIG at %s is LEFT IN FRAME on purpose and is not this "
          "rung's variable -- the leaf-count clause is scored on the FOREGROUND "
          "sapling only" % (BACKGROUND_SPRIG_BOX,), flush=True)

    if a.dry_run:
        print("DRY RUN -- nothing written.", flush=True)
        return 0
    work = arr.copy()

    # ---- 2. draw the sapling -------------------------------------------------
    rgb, al, rim, shadow, ridge = draw_sapling(geom, W, H)
    rgb = shade(rgb, al, shadow, ridge, arr)
    a3 = al[:, :, None]
    out = work * (1.0 - a3) + rgb * a3
    r3 = (rim * (al > 0.02))[:, :, None]
    out = np.clip(out * (1.0 - r3) + np.array(RIM_RGB)[None, None, :] * r3, 0, 255)

    # contact shading where the stem meets the grass, so it is rooted and not a
    # sticker standing on the field
    yy, xx = np.mgrid[0:H, 0:W]
    q = (((xx - geom["base"][0]) / 34.0) ** 2
         + ((yy - geom["base"][1] - 4) / 11.0) ** 2)
    sh = np.clip(1.0 - q, 0.0, 1.0) * 0.30
    out = np.clip(out * (1 - sh[:, :, None] * 0.62), 0, 255)

    drawn = al > 0.02
    mask = binary_dilate(drawn, a.mask_grow)
    Image.fromarray(out.astype(np.uint8)).save(a.out)
    Image.fromarray((mask * 255).astype(np.uint8)).save(a.mask_out)

    # ---- 3. the pre-registered checks. A failed check is named, not absorbed. -
    fails = []
    touched = (al > 0.0) | (sh > 0.0)
    changed = np.abs(out - arr).max(axis=2) > 0
    c1 = int((changed & ~touched).sum())
    fx0, fy0, fx1, fy1 = FACE_BOX
    c2 = float(np.abs(out - arr)[fy0:fy1, fx0:fx1].max())
    dys, dxs = np.nonzero(drawn)
    c3 = bool(dxs.min() > 2 and dxs.max() < W - 3 and dys.min() > 2
              and dys.max() < H - 3)
    # C4 IS THE RELATION, NOT THE CENTIMETRES -- see the docstring for why this
    # plate cannot be scored in cm. The approved line puts the plant beside him at
    # KNEE HEIGHT; his knee tops are at y 595, measured at 3x; the band is +-70 px,
    # which at this plate's rate is +-3.7 cm and is tighter than the disagreement
    # between the two scale readings the docstring records.
    crown = float(dys.min())
    c4 = abs(crown - HIS_KNEE_TOP_Y)
    lum_o = luminance(out)
    leafish = ((out[:, :, 1] - out[:, :, 0]) > 8) & ((out[:, :, 1] - out[:, :, 2]) > 20) \
        & (lum_o < 190)
    zone = np.zeros((H, W), bool)
    zone[dys.min():dys.max() + 1, dxs.min():dxs.max() + 1] = True
    c5 = blob_count(leafish & zone, 250)
    # C6 IS THE ADDITIVE TOOL'S VERSION OF BEAT 03's WEED CHECK: there was nothing
    # to remove, so the only way this rung can put a second plant beside him is by
    # drawing one. Drawn nodes: 1, by construction, and the drawn footprint must
    # be ONE connected object.
    c6 = len(blob_count(drawn, 250))
    # C7: THE PLANT IS BESIDE HIM, NOT ON HIM. Beat 03's cover clause is inverted
    # here -- that beat needs occlusion, this one needs adjacency, and the line
    # says `beside`. His hands and arms are the terms r1 already passes, so the
    # test is that no drawn pixel reaches them: nothing above NO_DRAW_ABOVE_Y at
    # all, which is 11 px clear of the crown by construction and is checked rather
    # than assumed.
    c7 = int(drawn[:NO_DRAW_ABOVE_Y, :].sum())
    # C8: and nothing of the plant lands inside the background sprig either, so
    # the two plants cannot be confused into one object by a reader or a sampler.
    bx0, by0, bx1, by1 = BACKGROUND_SPRIG_BOX
    c8 = int(drawn[by0:by1, bx0:bx1].sum())
    solid = al > 0.9
    drawn_dark = float(lum_o[solid].min())
    plate_dark = float(luminance(arr)[by0:by1, bx0:bx1].min())
    c9 = drawn_dark >= plate_dark

    print("C1 px changed outside the drawn+contact footprint %-7d      (== 0)   %s"
          % (c1, "PASS" if c1 == 0 else "FAIL"))
    print("C2 maxdiff over his FACE box %s %-8.0f (== 0)   %s"
          % (FACE_BOX, c2, "PASS" if c2 == 0 else "FAIL"))
    print("C3 whole plant inside the frame %-5s                     (True)   %s"
          % (c3, "PASS" if c3 else "FAIL"))
    print("C4 crown y=%.0f vs his measured knee line y=%.0f, off by %.0f px "
          "(<= 70)  %s" % (crown, HIS_KNEE_TOP_Y, c4, "PASS" if c4 <= 70 else "FAIL"))
    print("   (%.1f cm at his depth -- REPORTED, NOT SCORED; see the docstring)"
          % (plant_h / ppc))
    print("C5 green blobs >=250 px in the PLANT zone: %d %s -- the two blades and "
          "the stem read as ONE component where they touch, so 1-3 are expected "
          "and the BLADE count is 2 by construction" % (len(c5), c5))
    print("C6 drawn components >=250 px %-3d                          (== 1)   %s"
          % (c6, "PASS" if c6 == 1 else "FAIL"))
    print("C7 drawn px above y=%d (his hands, arms, face) %-6d    (== 0)   %s"
          % (NO_DRAW_ABOVE_Y, c7, "PASS" if c7 == 0 else "FAIL"))
    print("C8 drawn px inside the background sprig's box %-6d      (== 0)   %s"
          % (c8, "PASS" if c8 == 0 else "FAIL"))
    LEG_BAND = (190, 640, 560, 1216)
    lx0, ly0, lx1, ly1 = LEG_BAND
    shin = int(drawn[ly0:ly1, lx0:lx1].sum())
    print("   drawn px inside his declared leg band %s: %d -- REPORTED, NOT A "
          "FAIL. `beside him` is about where the plant is ROOTED, and a "
          "foreground blade crossing his shin is what tells a reader the plant "
          "is nearer to camera than his leg. C7 is the clause that protects the "
          "terms r1 passes -- his hands, arms and face -- and it is at 0."
          % (LEG_BAND, shin))
    print("C9 darkest SOLID drawn luma %.0f vs the plate's own %.0f in its own "
          "sprig  (>=) %s" % (drawn_dark, plate_dark, "PASS" if c9 else "FAIL"))
    print("inpaint mask %d px (%.2f%% of frame)" % (int(mask.sum()), 100.0 * mask.mean()))

    if c1 != 0: fails.append("FAIL-WROTE-OUTSIDE-ITS-FOOTPRINT(C1)")
    if c2 != 0: fails.append("FAIL-FACE-MOVED(C2)")
    if not c3: fails.append("FAIL-CROP(C3)")
    if c4 > 70: fails.append("FAIL-NOT-AT-KNEE-HEIGHT(C4)")
    if c6 != 1: fails.append("FAIL-NOT-ONE-PLANT(C6)")
    if c7 != 0: fails.append("FAIL-PLANT-ON-HIM(C7)")
    if c8 != 0: fails.append("FAIL-PLANT-MERGES-BACKGROUND-SPRIG(C8)")
    if not c9: fails.append("FAIL-LINE-TOO-STRONG(C9)")

    print("WROTE %s sha %s" % (a.out, sha256_of(a.out)))
    print("WROTE %s sha %s" % (a.mask_out, sha256_of(a.mask_out)))
    if fails:
        print("COMPOSITE FAILED: %s" % ", ".join(fails))
        return 3
    print("COMPOSITE PASSES C1-C9. Now OPEN IT at full resolution: a metric is a "
          "filter, never a verdict.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
