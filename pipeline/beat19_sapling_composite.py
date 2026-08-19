#!/usr/bin/env python3
"""Beat 19: build the init by COMPOSITING, because three wordings could not draw
the plant. $0, no GPU, no network, no provider.

WHY THIS EXISTS. Beat 19's plate ladder closed at three rungs on 2026-08-19
(pipeline/plate_scratch.py, DRAFTS[19] and REVS[(19,2)] / REVS[(19,3)]). r1, r2
and r3 are three draws of ONE seed differing by text alone, and the plant came
back a bead-strung whip every time -- fruit count 4 -> ~8 -> 3, never one, twice
DOUBLED into two plants. `two leaves and one thin side-branch` was supposed to
foreclose the multi-node vine geometrically and did not. Cardinality is the type
case of composite-init-pattern.md's CLASS A: CLIP's numeral embeddings are
near-identical so the count barely reaches the model, and no fourth adjective
fixes a binding failure. r3's own verdict names this build as the next rung and
forbids a fourth wording, so this file is that rung and nothing here asks the
sampler for a plant.

WHAT IS TAKEN FROM WHERE, and this is the whole point of the rung -- the project
already owns the picture it cannot write:

  * THE MAN, HIS POSE, HIS FIELD, HIS FRAMING and the whole of his LIGHT come
    from r3 unaltered. r3 passes 5 of 7 of its own pre-registered bar: P2 wide
    enough, P3 no contact (`both hands on his knees` bound on the first draw and
    is NOT re-litigated here), P4 face visible, P5 purple, P7 one lean adult.
  * THE FIG comes from BEAT 18's canon plate, which passes its own bar as ONE
    round deep-purple-violet fig on ONE very thin branch, green at its neck,
    matte. That is precisely the object beat 19 keeps failing to draw, already
    drawn and already scored.
  * THE SAPLING'S STEM, ITS ONE THIN SIDE-BRANCH AND ITS TWO LEAVES are DRAWN,
    procedurally, in colours SAMPLED FROM r3'S OWN FOLIAGE. §3.1 of the pattern:
    procedural, not a photograph and not a clone -- a shifted clone of nearby
    pixels is decal tell #4, a repeat, and photoreal detail dropped into a
    cel-shaded frame IS the decal failure mode by construction.

WHAT IS REMOVED, AND WHY REMOVAL IS THE HARD HALF. r3 has TWO whips, not one, and
they are the P6 failure. §13 of the pattern is the law that governs this: a masked
vacancy is filled with whatever the surviving CUE suggests -- an attachment point,
a stub, a socket. So both whips are removed WHOLE (leaf clusters, threads, all
three crystals, the woody stems, and the two segments that cross his cloak); no
stub of either is left anywhere. The vacancy is then filled from the region's OWN
BOUNDARY (§12: no clone survives a luminance gradient) -- horizontally first,
because this plate's background is a horizontally banded field under a vertical
sky gradient and a row-wise fill reproduces both exactly, then relaxed by
diffusion so no seam survives. Nothing is cloned from elsewhere in the frame.

SCALE IS THE ONE THING THIS TOOL CANNOT GET WRONG. Beat 03's whole joke is the
size mismatch -- the scavenger far taller than the plant -- and ruling_0815 turned
on that geometry ("A fruit released from a 40 cm branch cannot reach a standing
man's head"). So the plant is sized from CANON, through a measured ground plane,
and every number is printed:

  style.md node table, row 002a/b/c: ~40 cm, "two leaves + one thin side-branch",
  "the branch is where the fig grew and fell".

  MEASURED ON r3: his head is 140 px crown-to-chin (crown y=280, chin y=420).
  An adult head is ~23 cm, so 6.09 px/cm AT HIS DEPTH, whose ground line is his
  boot soles at y=910. The horizon (top of the pale hill band) is y=425. A ground
  plane gives px/cm(y) = 6.09 * (y - 425) / (910 - 425). His seated crown-to-sole
  is 632 px = 104 cm, which is the cross-check: a seated adult, not a chibi.
  At the sapling's root (y=902) that is 5.99 px/cm, so 40 cm = 240 px.
  The plate's OWN three crystals measure 43, 44 and 31 px tall -- the checkpoint's
  own answer for how big a fruit is in this frame -- so a 7 cm fig at 42 px is the
  plate's scale, not this tool's invention.

GEOMETRY IS THE STEWARD'S AND IS THE FIRST THING A CORRECTION SHOULD MOVE. Every
coordinate below was read off the plate's own pixels (silhouette runs printed per
row, components labelled and measured), not eyeballed, and the placement is on his
RIGHT because that is where the plate has room: at the sapling's rows his cloak
ends at x 555-653 and the frame ends at 832, so the drawn plant clears him by 74
px at the root and 85 px at the leaves. P3 is a done_when clause and a 25 px
clearance is not worth having.

NO FOURTH WORDING. This file adds no REVS entry, asks for no prompt, makes no
pick and writes no leaf. It emits an init and a mask, and the mask is what a
0.30 finishing pass would use if one is ever fired.
"""

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO = Path(__file__).resolve().parent.parent
W, H = 832, 1216

PLATE = (REPO / "farm-out" / "ep2-b19-mac-plate-0819"
         / "19-the-drop-mac-plate-r3s1.png")
PLATE_SHA = "de7a256c29b0a752b335e1e022c111e654c4c65cbe43b05fb98bd9573e1c6cbf"
FIGPLATE = (REPO / "farm-out" / "ep2-b18-canon-0817"
            / "18-the-decision-ipa-r2-w015-s2.png")
FIGPLATE_SHA = "ab70a4adec4cb7b69df131febea47af2987d0bbab7e8a4c77810048b29e0a3f1"

# --- the ground plane, measured (see the module docstring) --------------------
HORIZON_Y = 425.0
FIG_GROUND_Y = 910.0        # his boot soles
PX_PER_CM_AT_FIG = 6.09     # head 140 px / 23 cm
CANON_PLANT_CM = 40.0       # style.md row 002a/b/c
CANON_FIG_CM = 7.0          # the plate's own crystals: 43/44/31 px at 6.09 px/cm

# --- the sapling, placed on his right where the plate has room ---------------
# v4 rooted this at x=718 and C5 caught it: at y 850-895 the dark grass ring
# around him reaches x 699-705, so the stem stood 9 px off the mass at his hip.
# P3 is a done_when clause and 9 px is not a clearance. Moved 22 px right; the
# measured gap is now printed by the tool rather than asserted here.
ROOT = (740, 902)
STEM_APEX = (734, 700)      # 202 px of stem; the leaves carry the last ~43 px
STEM_MID = (751, 800)       # quadratic control point -- one gentle lean, no S
BRANCH_FROM_T = 0.62        # up the stem from the root; the side-branch node
# THE SIDE-BRANCH POINTS AT HIM, and that is a staging choice with a reason. The
# fig has to fall somewhere he can then pick it up with both hands (beat 20's
# opening), so it hangs on the side between them; pointing it the other way puts
# the fruit 30 px off the frame edge and the landing outside the composition.
# v5 hung it from a node 35% up the stem and C5 caught THAT: the fruit's bottom
# came down to y=834, where the dark grass ring at his hem reaches x=693, and the
# gap fell to 3 px. So the node moved to 62% up and the fig now hangs at y
# 763-810 with 90 px of ground under it. Same reasoning as the root move: P3 is a
# `done_when` clause and a single-digit clearance is not one.
BRANCH_TIP = (712, 762)
LEAF_L_TIP = (685, 664)
LEAF_R_TIP = (775, 660)

# --- what has to come out ----------------------------------------------------
# TWO ROIs that bracket the whips, and SEED WINDOWS inside them -- windows, not
# points, because a point seed is a guess that can land one pixel off the object
# and silently erase nothing (v1 of this file did exactly that: three of six
# declared points landed on sky and the palette came back with four leaf pixels).
# Every window below is a measured component bbox, printed by labelling the
# plate: left cluster y[267..402] x[165..254]; left hook+mid sprig y[401..532]
# x[137..314]; left thread+crystal y[500..640] x[209..244]; left lower sprig
# y[644..769] x[191..242]; right branch+cluster y[274..399] x[528..629] plus its
# lower length y[418..478] x[495..545]; right thread+crystal y[458..540]
# x[574..606]; right lower crystal y[735..766] x[583..597].
WHIP_ROIS = [(130, 250, 352, 784), (495, 250, 752, 784)]
SEED_WINDOWS = [
    (160, 260, 262, 412),    # left: top cluster and the upper stem
    (130, 396, 322, 542),    # left: the hook, the node and the mid sprig
    (200, 494, 250, 652),    # left: the thread and the crystal on it
    (185, 638, 252, 780),    # left: the lower leaf sprig
    (495, 260, 645, 484),    # right: the woody branch, its fork and its cluster
    (566, 448, 616, 558),    # right: the thread and the upper crystal
    (570, 718, 612, 782),    # right: the lower crystal
]
# HIS SILHOUETTE IS DERIVED FROM THE PLATE, NOT TYPED IN. Per row, the run of
# `raw or enclosed-interior` containing this column is him -- which works because
# his outline is dark on every side and his chartreuse SKIN, which no colour rule
# separates from the field (skin R-G = -2, field R-G = +8), is enclosed by it.
BODY_CENTRE_X = 420
BODY_ROWS = (284, 962)
BODY_PAD = 6
# THE ONE PLACE THIS TOOL TOUCHES HIM, DECLARED. The left whip's woody stem is
# drawn ACROSS his cloak here (traced at 7x: it enters at 284,484 and runs
# down-right past 326,544), so leaving it would leave a limb crossing his chest
# with nothing attached to it -- which is P6's fault, not its cure. The rule
# inside this box is one his cloak cannot satisfy: the cloak is uniformly violet
# (R-B runs -19 to -26 over every sample) and the stem is warm or neutral
# (R-B +31 on its lit body, -3 on its outline).
CROSS_BOX = (299, 486, 348, 566)
# Where the vine leaves its cluster as a pale neutral line (see plant_rule).
THREAD_BOX = (232, 346, 358, 402)
# Byte-identical zone. His face, his torso and both hands on his knees are the
# terms r3 already passes (P3, P4) and nothing here may move a pixel of them. It
# starts at x=352, one pixel clear of the left ROI, so it contains no whip and the
# check is a real one rather than a definition.
KEEP_EXACT = (352, 268, 522, 664)


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dilate(m: np.ndarray, r: int) -> np.ndarray:
    out = m.copy()
    for _ in range(r):
        s = out.copy()
        s[1:, :] |= out[:-1, :]
        s[:-1, :] |= out[1:, :]
        s[:, 1:] |= out[:, :-1]
        s[:, :-1] |= out[:, 1:]
        out = s
    return out


def erode(m: np.ndarray, r: int) -> np.ndarray:
    out = m.copy()
    for _ in range(r):
        s = out.copy()
        s[1:, :] &= out[:-1, :]
        s[:-1, :] &= out[1:, :]
        s[:, 1:] &= out[:, :-1]
        s[:, :-1] &= out[:, 1:]
        out = s
    return out


def reach(seed: np.ndarray, allow: np.ndarray, limit: int = 3000) -> np.ndarray:
    """Flood `seed` through `allow`. numpy only, like the other composite tools --
    scipy is not on every Mac in the farm and this runs on whichever one is free."""
    cur = seed & allow
    for _ in range(limit):
        nxt = dilate(cur, 1) & allow
        if nxt.sum() == cur.sum():
            return nxt
        cur = nxt
    return cur


def px_per_cm(y: float) -> float:
    return PX_PER_CM_AT_FIG * (y - HORIZON_Y) / (FIG_GROUND_Y - HORIZON_Y)


def box_mask(boxes) -> np.ndarray:
    m = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in boxes:
        m[y0:y1, x0:x1] = True
    return m


def plant_rule(a: np.ndarray) -> np.ndarray:
    """THE COLOUR RULE IS RE-DERIVED FOR THIS PLATE -- §5 of the pattern records
    that it transferred ZERO times across four boards, so nothing here is
    inherited.

    Measured on r3: his SKIN is (226,228,74) and the field is (235,226,118) --
    R-G is -2 on the skin and +8 on the field, which is the ONLY thing that
    separates them, and it is why a naive `greenish` rule mattes his skull as
    ground and a naive `field` rule mattes his skull as sky. The whip is none of
    those: its foliage is a mid-green with G ABOVE R (101,133,76 at the 40th
    percentile), its ink and woody stems are dark (lum < 125), and its fruit is
    violet (B - G > 30). His cloak and boots satisfy the same rule, which is why
    the body run below has to come out of it.
    """
    R, G, B = a[..., 0].astype(np.int16), a[..., 1].astype(np.int16), a[..., 2].astype(np.int16)
    lum = 0.299 * R + 0.587 * G + 0.114 * B
    foliage = (G - R > 12) & (G - B > 22) & (lum < 186)
    ink = lum < 125
    # PURPLE = red AND blue both above green. Written this way and not as `B > R`
    # for a reason worth recording: r3's crystals are VIOLET (B-R +43 to +79) but
    # his cloak runs from violet through mauve to a warm plum, and a `B > R` rule
    # drops half of it. That mattered: with the narrow rule his pale COLLAR was
    # not enclosed by anything the rule claimed, the border flood walked into it,
    # the derived body run stopped 60 px short at y 430-490, and the whip flood
    # took 50x80 px of his shoulder and smeared it. v3's own erase showed it.
    purple = (np.minimum(R, B) - G > 10) & (lum < 205)
    # THE PALE THREAD, and it is why this rule has a fourth clause. The left
    # whip's vine leaves its cluster as a thin line the other three clauses all
    # miss -- traced at (244,360) as (156,156,159), neutral grey at lum 156, and
    # further right it is a mauve hair at lum ~127. v3's erase removed its left
    # 40% and left the rest across his cheek. Inside the declared box the only
    # things present are sky (lum 225-250) and that line, so DARKER THAN THE SKY
    # is the whole rule and it needs no colour term.
    thread = box_mask([THREAD_BOX]) & (lum < 205)
    return foliage | ink | purple | thread


def body_run(a: np.ndarray, raw: np.ndarray) -> np.ndarray:
    """His silhouette, per row, DERIVED from the plate. The border is flooded
    through everything the plant rule does NOT claim; what the flood cannot reach
    is either his outline or something his outline encloses, and the run of that
    containing BODY_CENTRE_X is him. Padded by BODY_PAD so a flood in the whip
    mask cannot walk up his own antialiased rim.
    """
    border = np.zeros((H, W), bool)
    border[0, :] = border[-1, :] = True
    border[:, 0] = border[:, -1] = True
    outside = reach(border & ~raw, ~raw, limit=1700)
    solid = raw | ~outside
    body = np.zeros((H, W), bool)
    y0, y1 = BODY_ROWS
    for y in range(y0, y1):
        row = solid[y]
        if not row[BODY_CENTRE_X]:
            continue
        lo = BODY_CENTRE_X
        while lo > 0 and row[lo - 1]:
            lo -= 1
        hi = BODY_CENTRE_X
        while hi < W - 1 and row[hi + 1]:
            hi += 1
        body[y, max(0, lo - BODY_PAD):min(W, hi + BODY_PAD + 1)] = True
    return body


def whip_matte(a: np.ndarray, raw: np.ndarray, body: np.ndarray):
    """Both whips, whole -- and the crossing over his cloak with them, because a
    woody limb left lying across his chest with nothing attached to it is P6's
    fault and not its cure. Returns (mask, cross_matte)."""
    R, B = a[..., 0].astype(np.int16), a[..., 2].astype(np.int16)
    lum = 0.299 * R + 0.587 * a[..., 1].astype(np.int16) + 0.114 * B
    roi = box_mask(WHIP_ROIS)
    allow = raw & roi & ~body
    seed = allow & box_mask(SEED_WINDOWS)
    if seed.sum() < 500:
        raise SystemExit("!! only %d px under the %d declared seed windows; the "
                         "colour rule and the plate disagree and nothing will be "
                         "erased on a guess." % (seed.sum(), len(SEED_WINDOWS)))
    m = reach(seed, allow)
    cross = box_mask([CROSS_BOX]) & body & (R - B > -12) & (lum < 160)
    # Close the 1px antialiased rim, or the erase leaves the outline behind at
    # partial alpha and it comes back as a GHOST -- §12 corollary 1, which cost
    # that lane a rung. Grow must exceed the blend feather.
    #
    # AND THEN SUBTRACT THE ZONE DECLARED BYTE-IDENTICAL. The 3 px growth is what
    # crosses into him at the contact points, and his face and hands are the terms
    # r3 already passes; the mask is not allowed to reach them whatever the colour
    # rule thinks. C1b re-measures this on the OUTPUT rather than trusting the
    # line above, so a later edit that reorders these operations still fires.
    m = dilate(m, 3)
    # THE PENUMBRA, and it is §12 corollary 1 arriving on schedule. A mask fitted
    # to an object and grown by a fixed radius leaves the object's ANTIALIASED
    # EDGE outside it at partial alpha, and that comes back as a ghost. v7 left
    # exactly that: a 6 px band at x 584-589, y 400-415, luminance 208 against a
    # 249 sky, reading at 2x as a grey hairline where the right branch had been.
    # No colour clause can reach it -- at half alpha it is neither ink nor
    # foliage. What it IS, always, is DARKER THAN ITS OWN NEIGHBOURHOOD. So the
    # mask grows 6 px further, but only into pixels that are darker than a
    # radius-14 blur of the plate, and never into him.
    ref = np.asarray(Image.fromarray(np.clip(lum, 0, 255).astype(np.uint8))
                     .filter(ImageFilter.GaussianBlur(14))).astype(np.float32)
    halo = dilate(m, 6) & ~m & (lum < ref - 5) & ~dilate(body, 4)
    m = dilate(m | halo, 1) | dilate(cross, 1)
    # AND SUBTRACT THE ZONE DECLARED BYTE-IDENTICAL. The growth above is what
    # crosses into him at the contact points, and his face and hands are the terms
    # r3 already passes; the mask is not allowed to reach them whatever the colour
    # rule thinks. C1b re-measures this on the OUTPUT rather than trusting the
    # line below, so a later edit that reorders these operations still fires.
    # AND KEEP HIS OWN OUTLINE. Where a whip lay along his silhouette, erasing it
    # takes his cel outline with it and the boundary fill returns a soft ramp
    # between cloak and field: v8 left a pale haze over his right shoulder at
    # x 520-570, y 431-466 with the shoulder line washed out. So the outermost
    # 3 px of his silhouette is never erased. What survives there is at most a
    # 3 px sliver of branch lying inside a dark outline that is already dark --
    # invisible -- and the trade buys back a crisp edge the sampler would
    # otherwise have to reinvent. The CROSS matte is deeper into the cloak than
    # that and is unaffected.
    rim_of_him = body & ~erode(body, 3)
    return (m & ~rim_of_him) & ~box_mask([KEEP_EXACT]), cross


def fill_from_boundary(a: np.ndarray, hole: np.ndarray, body: np.ndarray,
                       iters: int = 0) -> np.ndarray:
    """Fill `hole` from the region's OWN boundary. §12: no clone survives a
    luminance gradient, and this plate is a vertical sky gradient over a
    horizontally banded field -- so the first pass is a per-row linear
    interpolation between the nearest surviving pixels, which reproduces both the
    vertical gradient and the horizontal streaks exactly, and diffusion then
    removes the row-to-row seams. Nothing is copied from elsewhere in the frame,
    so decal tell #4 (a visible repeat) is impossible by construction.
    """
    out = a.astype(np.float32).copy()
    xs = np.arange(W, dtype=np.float32)
    # FILL WITHIN CLASS. A hole in the BACKGROUND is filled only from surviving
    # background, and the hole over his cloak only from surviving cloak. v11
    # interpolated across both and left a 22 px grey smear at y 387-388: the
    # vine's thread ran up to his cheek, so the nearest surviving pixel to its
    # right was his own dark head outline and the fill averaged sky with ink.
    # This is §12's source law in its other form -- never fill with something
    # that belongs to a different object.
    for cls in (~body, body):
        for y in range(H):
            row = hole[y] & cls[y]
            if not row.any():
                continue
            keep = (~hole[y]) & cls[y]
            if keep.sum() < 6:
                continue
            for c in range(3):
                out[y, row, c] = np.interp(xs[row], xs[keep], out[y, keep, c])
    for _ in range(iters):
        blur = np.asarray(Image.fromarray(
            np.clip(out, 0, 255).astype(np.uint8)
        ).filter(ImageFilter.GaussianBlur(2.0))).astype(np.float32)
        out[hole] = blur[hole]
    return np.clip(out, 0, 255).astype(np.uint8)


def foliage_palette(a: np.ndarray, whip: np.ndarray) -> dict:
    """The drawn plant's colours are SAMPLED FROM THE WHIPS THIS TOOL IS ABOUT TO
    DELETE. That is the strongest source available: same frame, same light, same
    checkpoint, same line weight -- and it is not decal tell #4, because the
    source pixels do not survive into the output.
    """
    R, G, B = a[..., 0].astype(np.int16), a[..., 1].astype(np.int16), a[..., 2].astype(np.int16)
    lum = 0.299 * R + 0.587 * G + 0.114 * B
    leaf = whip & (G - R > 12) & (G - B > 22) & (lum < 205)
    ink = whip & (lum < 78)
    if leaf.sum() < 400 or ink.sum() < 60:
        raise SystemExit("!! plate foliage sample too small (leaf %d, ink %d); the "
                         "palette will not be guessed." % (leaf.sum(), ink.sum()))
    px = a[leaf]
    return {
        "leaf_n": int(leaf.sum()), "ink_n": int(ink.sum()),
        "dark": tuple(int(v) for v in np.percentile(px, 18, axis=0)),
        "mid": tuple(int(v) for v in np.percentile(px, 45, axis=0)),
        "light": tuple(int(v) for v in np.percentile(px, 86, axis=0)),
        "ink": tuple(int(v) for v in np.median(a[ink], axis=0)),
    }


def fruit_luma(a: np.ndarray, whip: np.ndarray) -> float:
    """The plate's own answer to `how bright is a purple fruit in this light`.
    Beat 18's fig is a macro under its own exposure (body median RGB 43,21,41 --
    lum 30), and pasting that value into a sunny field reads as a hole, not a
    fruit. §3.3 says keep the PLATE's light; the plate's only purple fruit are
    the three crystals this tool deletes, and their EXPOSURE is not the defect --
    their faceted shape and their number are. So the exposure is taken and the
    shape is not.
    """
    R, G, B = a[..., 0].astype(np.int16), a[..., 1].astype(np.int16), a[..., 2].astype(np.int16)
    lum = 0.299 * R + 0.587 * G + 0.114 * B
    f = whip & (B - G > 30) & (B - R > 8) & (lum < 175)
    if f.sum() < 150:
        raise SystemExit("!! only %d plate fruit px; the fig's exposure would be "
                         "a guess." % f.sum())
    return float(np.median(lum[f]))


def fig_cutout(path: Path, target_h: int, target_luma: float):
    """Beat 18's fig, matted off its own background and re-exposed for this
    plate. Returns (RGB array, alpha 0..1, the numbers).

    The matte is the object's own largest dark component with its holes filled;
    the alpha is soft over 26 levels of luminance so the fig keeps a drawn edge
    instead of a staircase. The BODY is what gets sized to canon -- the neck
    above it rides along at the same factor, so the fig is not stretched.
    """
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    dark = lum < 175
    seed = np.zeros(dark.shape, bool)
    ys, xs = np.nonzero(dark)
    seed[int(np.median(ys)), int(np.median(xs))] = True
    obj = reach(seed, dark, limit=2600)
    outside = np.zeros(obj.shape, bool)
    outside[0, :] = outside[-1, :] = True
    outside[:, 0] = outside[:, -1] = True
    obj |= ~reach(outside, ~obj, limit=2600)
    yy, xx = np.nonzero(obj)
    # the body is everything below the neck; the neck is the narrow top
    widths = obj.sum(axis=1)
    body_top = int(np.argmax(widths > 0.30 * widths.max()))
    body_h = int(yy.max() - body_top + 1)
    scale = target_h / float(body_h)
    y0 = max(0, body_top - int(round(0.11 * body_h)))       # keep a short neck
    y1, x0, x1 = int(yy.max()) + 1, int(xx.min()), int(xx.max()) + 1
    alpha = np.clip((175.0 - lum) / 26.0, 0.0, 1.0) * obj
    crop = a[y0:y1, x0:x1].astype(np.float32)
    acrop = alpha[y0:y1, x0:x1].astype(np.float32)
    # re-expose: one measured multiplicative gain, so the fig's own modelling
    # (the specular, the neck, the shoulder falloff) survives the transfer
    body = acrop > 0.6
    cl = (0.299 * crop[..., 0] + 0.587 * crop[..., 1] + 0.114 * crop[..., 2])
    src = float(np.median(cl[body]))
    gain = target_luma / max(1.0, src)
    crop = np.clip(crop * gain, 0, 255)
    nh = max(2, int(round(crop.shape[0] * scale)))
    nw = max(2, int(round(crop.shape[1] * scale)))
    rgb = np.asarray(Image.fromarray(crop.astype(np.uint8)).resize(
        (nw, nh), Image.LANCZOS)).astype(np.float32)
    al = np.asarray(Image.fromarray((acrop * 255).astype(np.uint8)).resize(
        (nw, nh), Image.LANCZOS)).astype(np.float32) / 255.0
    return rgb, al, {"src_body_px": [int(x1 - x0), body_h], "scale": round(scale, 5),
                     "reduction_x": round(1.0 / scale, 2), "gain": round(gain, 3),
                     "src_median_luma": round(src, 1),
                     "target_median_luma": round(target_luma, 1),
                     "out_px": [nw, nh]}


def qbez(p0, p1, p2, t):
    u = 1.0 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def draw_taper(d, p0, p1, p2, w0, w1, fill, ink):
    """A stem is a tapered polygon, not a stroked line: PIL's line joins at 3 px
    read as a chain of dots at 1x, which is decal tell #4 and is what beat 14's
    v2 was rejected for by eye before any GPU ran."""
    left, right = [], []
    n = 22
    for i in range(n + 1):
        t = i / float(n)
        x, y = qbez(p0, p1, p2, t)
        dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
        dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
        L = max(1e-3, (dx * dx + dy * dy) ** 0.5)
        nx, ny = -dy / L, dx / L
        r = 0.5 * (w0 + (w1 - w0) * t)
        left.append((x + nx * r, y + ny * r))
        right.append((x - nx * r, y - ny * r))
    d.polygon(left + right[::-1], fill=fill, outline=ink)


LEAF_A, LEAF_B = 0.55, 1.00     # base roundness / tip sharpness
LEAF_NORM = max((t / 40.0) ** LEAF_A * (1.0 - t / 40.0) ** LEAF_B
                for t in range(1, 40))


def _blade(base, tip, width, k=1.0):
    """Half-widths along an ovate blade: round at the petiole, POINTED at the
    apex. v6 got this wrong in a way only a look caught -- the normalisation
    constant was 0.245 where the profile's own maximum is 0.436, so every blade
    came out 1.78x too fat and the pair read as a CLOVER, two flat discs with a
    hard diagonal across each. The constant is now computed from the exponents
    instead of typed, which is why it cannot drift again."""
    bx, by = base
    dx, dy = tip[0] - bx, tip[1] - by
    L = max(1e-3, (dx * dx + dy * dy) ** 0.5)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    out, n = [], 20
    for i in range(n + 1):
        t = i / float(n)
        r = (k * width * 0.5 * (t ** LEAF_A) * ((1.0 - t) ** LEAF_B) / LEAF_NORM)
        out.append((bx + ux * L * t, by + uy * L * t, nx * r, ny * r))
    return out


def draw_leaf(d, base, tip, width, fill, hi, ink):
    """One blade in the plate's dialect: a mid-green ovate body with a dark cel
    outline and a lighter crescent along its lit edge, which is how r3 draws its
    own leaves (traced at 5x: mid-green body, a yellow-green rim on one side, a
    dark navy outline). The highlight is a CRESCENT and not a half -- v6 filled
    half the blade with the light percentile and it read as a fold rather than
    light. No midrib is drawn: §5's sampler-side law is that in this dialect a
    strong dark line IS an edge, and a composited internal line stronger than the
    object's own outline gets resolved as an object boundary. That is how beat 10
    split its slab in two, and a leaf split down the middle is two leaves."""
    prof = _blade(base, tip, width)
    d.polygon([(x + rx, y + ry) for x, y, rx, ry in prof]
              + [(x - rx, y - ry) for x, y, rx, ry in reversed(prof)],
              fill=fill, outline=ink)
    hp = _blade(base, tip, width, k=0.96)
    d.polygon([(x + rx, y + ry) for x, y, rx, ry in hp]
              + [(x + rx * 0.34, y + ry * 0.34) for x, y, rx, ry in reversed(hp)],
              fill=hi)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plate", default=str(PLATE))
    ap.add_argument("--plate-sha256", default=PLATE_SHA)
    ap.add_argument("--fig-plate", default=str(FIGPLATE))
    ap.add_argument("--fig-plate-sha256", default=FIGPLATE_SHA)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mask-out", required=True)
    ap.add_argument("--overlay-out", default=None,
                    help="write the mattes over the plate so a look can reject "
                         "them in seconds, which is the point of doing the "
                         "structure with image processing")
    ap.add_argument("--erased-out", default=None,
                    help="write the plate with both whips removed and nothing "
                         "drawn -- the intermediate a look has to pass first")
    ap.add_argument("--dry-run", action="store_true",
                    help="write the whip mask and the erase, then stop")
    a = ap.parse_args()

    plate, figp = Path(a.plate), Path(a.fig_plate)
    for p, want in ((plate, a.plate_sha256), (figp, a.fig_plate_sha256)):
        have = sha256_of(p)
        if have != want:
            print("!! sha mismatch on %s\n   want %s\n   have %s" % (p.name, want, have))
            return 2
        print("SHA OK %-46s %s" % (p.name, have[:16] + "..."))
    im = Image.open(plate).convert("RGB")
    if im.size != (W, H):
        print("!! plate is %s, expected %dx%d" % (im.size, W, H)); return 2
    arr = np.asarray(im)

    # ---- 1. take both whips out -------------------------------------------
    raw = plant_rule(arr)
    body = body_run(arr, raw)
    whip, cross = whip_matte(arr, raw, body)
    print("BODY RUN %d px derived from the plate; CROSS matte %d px is the only "
          "part of him this tool touches" % (body.sum(), cross.sum()))
    pal = foliage_palette(arr, whip)
    tlum = fruit_luma(arr, whip)
    print("WHIP MATTE %d px (%.2f%% of frame); components erased WHOLE, no stub left"
          % (whip.sum(), 100.0 * whip.sum() / (W * H)))
    if a.overlay_out:
        ov = arr.copy()
        ov[whip] = (ov[whip] * 0.25 + np.array([255, 40, 40]) * 0.75).astype(np.uint8)
        ov[body & ~whip] = (ov[body & ~whip] * 0.72
                            + np.array([40, 90, 255]) * 0.28).astype(np.uint8)
        Image.fromarray(ov).save(a.overlay_out)
        print("matte overlay written: %s (red = erased, blue = his derived run)"
              % a.overlay_out)
    print("PALETTE from %d plate leaf px / %d ink px: dark=%s mid=%s light=%s ink=%s"
          % (pal["leaf_n"], pal["ink_n"], pal["dark"], pal["mid"], pal["light"], pal["ink"]))
    print("PLATE FRUIT median luma %.1f -- the exposure the fig is matched to" % tlum)
    erased = fill_from_boundary(arr, whip, body)
    if a.erased_out:
        Image.fromarray(erased).save(a.erased_out)
        print("erase written: %s" % a.erased_out)

    # ---- 2. draw the sapling ----------------------------------------------
    ppc_root = px_per_cm(ROOT[1])
    plant_px = CANON_PLANT_CM * ppc_root
    fig_px = int(round(CANON_FIG_CM * ppc_root))
    print("GROUND PLANE px/cm at root y=%d: %.3f  ->  canon %.0f cm plant = %.0f px,"
          " canon %.0f cm fig = %d px" % (ROOT[1], ppc_root, CANON_PLANT_CM,
                                          plant_px, CANON_FIG_CM, fig_px))
    layer = Image.fromarray(erased)
    d = ImageDraw.Draw(layer)
    ink = pal["ink"]
    stem_col = tuple(int(v) for v in np.array(pal["dark"]) * 0.88 + 12)
    draw_taper(d, ROOT, STEM_MID, STEM_APEX, 7.5, 3.0, stem_col, ink)
    bx, by = qbez(ROOT, STEM_MID, STEM_APEX, BRANCH_FROM_T)
    draw_taper(d, (bx, by), ((bx + BRANCH_TIP[0]) / 2, by - 5),
               BRANCH_TIP, 4.0, 2.2, stem_col, ink)
    # TWO LEAVES, NOT A MIRRORED PAIR. Same node, but 5 px apart on the stem and
    # 6% apart in length: decal tell #4 is a visible repeat, and two identical
    # blades reflected about a vertical axis are one.
    leaf_len = 0.255 * plant_px
    for tip, dy, k in ((LEAF_L_TIP, 5, 1.00), (LEAF_R_TIP, 0, 1.06)):
        node = (STEM_APEX[0] + 1, STEM_APEX[1] + dy)
        vx, vy = tip[0] - node[0], tip[1] - node[1]
        L = max(1e-3, (vx * vx + vy * vy) ** 0.5)
        ln = leaf_len * k
        t2 = (node[0] + vx / L * ln, node[1] + vy / L * ln)
        draw_leaf(d, node, t2, ln * 0.40, pal["mid"], pal["light"], ink)
    drawn_plant = (np.abs(np.asarray(layer).astype(np.int16)
                          - erased.astype(np.int16)).max(axis=2) > 0)

    # ---- 3. hang beat 18's fig on the side-branch -------------------------
    rgb, al, fmeta = fig_cutout(figp, fig_px, tlum)
    print("FIG from beat 18: body %s px -> %s px, scale %.5f (%.2fx reduction), "
          "exposure gain %.3f (median luma %.1f -> %.1f)"
          % (fmeta["src_body_px"], fmeta["out_px"], fmeta["scale"],
             fmeta["reduction_x"], fmeta["gain"], fmeta["src_median_luma"],
             fmeta["target_median_luma"]))
    nh, nw = rgb.shape[0], rgb.shape[1]
    px0 = int(round(BRANCH_TIP[0] - nw / 2.0))
    py0 = int(round(BRANCH_TIP[1] + 1))
    base = np.asarray(layer).astype(np.float32)
    sl = (slice(py0, py0 + nh), slice(px0, px0 + nw))
    aa = al[..., None]
    base[sl] = base[sl] * (1 - aa) + rgb * aa
    fig_region = np.zeros((H, W), bool)
    fig_region[sl] = al > 0.28
    # a drawn edge, in the plate's own ink: §3's "inset 2px and paint the
    # surviving rim as a dark cel outline", so the fig has a line and does not
    # run off a cliff into the field
    rim = dilate(fig_region, 1) & ~fig_region
    base[rim] = base[rim] * 0.42 + np.array(ink, np.float32) * 0.58
    comp = np.clip(base, 0, 255).astype(np.uint8)

    # contact shading where the stem meets the grass, so the plant is ROOTED and
    # not standing on the field like a sticker
    yy, xx = np.mgrid[0:H, 0:W]
    q = (((xx - ROOT[0]) / 26.0) ** 2 + ((yy - ROOT[1] - 3) / 9.0) ** 2)
    shade = np.clip(1.0 - q, 0.0, 1.0) * 0.30
    comp = np.clip(comp.astype(np.float32) * (1 - shade[..., None] * 0.62), 0, 255
                   ).astype(np.uint8)
    plant = drawn_plant | fig_region | rim

    # ---- 4. the mask a finishing pass would use ---------------------------
    # It covers the drawn plant AND the erased vacancies -- not only what was
    # painted. A mask fitted to the paint alone makes the result a foregone
    # conclusion and measures nothing (beat 14's C8).
    mask = np.zeros((H, W), np.uint8)
    mask[dilate(plant, 9) | dilate(whip, 5)] = 255
    Image.fromarray(mask).save(a.mask_out)

    # ---- 5. the checks. A failed check stops the run. ---------------------
    o = comp.astype(np.int16)
    b0 = arr.astype(np.int16)
    fails = []
    # C1 asks whether the fill wrote a single pixel it was not asked to: inside
    # his silhouette, off the erase mask, nothing may move. C1a then bounds how
    # much of him the mask claims at all, so a mask that quietly grows over him
    # is caught rather than absorbed. C1b is the one that cannot be argued with --
    # his face and both hands on his knees are r3's, BYTE FOR BYTE, and those are
    # the terms r3 already passes.
    changed = np.abs(o - b0).max(axis=2) > 0
    c1 = int((changed & body & ~whip).sum())
    c1a = int((whip & body).sum())
    c1b = int(np.abs(o - b0)[box_mask([KEEP_EXACT])].max())
    # every whip pixel must actually be gone: nothing on the whip's colour rule
    # may survive inside the old whip footprint
    R, G, B = o[..., 0], o[..., 1], o[..., 2]
    lum = 0.299 * R + 0.587 * G + 0.114 * B
    # THE SAME RULE THAT BUILT THE MASK, re-run on the OUTPUT. It was written out
    # a second time here and the copy went stale the moment plant_rule was
    # tightened: the old text kept `lum < 205` on the foliage clause and C2 read
    # 153 surviving whip pixels that were the distant TREELINE, which this tool
    # never touched. A duplicated predicate is a bug with a delay on it.
    resid_rule = plant_rule(o.astype(np.uint8))
    # THE OLD FOOTPRINT MEANS THE PART OF IT IN THE BACKGROUND. A 5 px band along
    # his silhouette is excluded, and not as a tolerance invented after seeing the
    # number: where the erased whip lay against his cloak the boundary fill
    # correctly returns CLOAK colour, which is purple, which the whip rule then
    # counts as a surviving whip. v4 read exactly 4 px, all of them at (455,
    # 525-528), all of them cloak the fill got right.
    old_only = whip & ~dilate(plant, 12) & ~dilate(body, 5)
    c2 = int((resid_rule & old_only).sum())
    # exactly one fruit, and it is off the ground and on the branch
    # A PURPLE RULE, NOT A VIOLET ONE, and the difference is a finding rather than
    # a convenience. r3's own crystals are violet (B-R +43 to +79) while beat 18's
    # fig is a PLUM: its body median is (43,21,41), R-B +2, so it is neutral
    # between magenta and violet and a `B > R` rule scores it as absent. What both
    # have in common, and what a naive eye calls purple, is that red AND blue both
    # sit well above green -- so that is the rule.
    fr = (np.minimum(R, B) - G > 14) & (lum < 190) & ~body
    lab_seed = np.zeros((H, W), bool)
    fy, fx = np.nonzero(fr)
    c3 = 0
    if len(fy):
        pool = fr.copy()
        comps = []
        for _ in range(8):
            rest = np.nonzero(pool)
            if not len(rest[0]):
                break
            lab_seed[:] = False
            lab_seed[rest[0][0], rest[1][0]] = True
            cc = reach(lab_seed, fr)
            if cc.sum() >= 60:
                comps.append(cc.sum())
            pool &= ~cc
        c3 = len(comps)
    fyy = np.nonzero(fig_region.any(axis=1))[0]
    c4 = int(ROOT[1] - fyy.max())                 # px between fig bottom and ground
    c5 = int((dilate(plant, 8) & body).sum())     # plant-to-body clearance
    gap = 999
    for r in range(1, 90):
        if (dilate(plant, r) & body).any():
            gap = r
            break
    plant_h = int(ROOT[1] - np.nonzero(plant.any(axis=1))[0].min())
    c6 = plant_h / ppc_root                       # plant height in cm
    pxx = np.nonzero(plant.any(axis=0))[0]
    c7 = bool(pxx.min() > 2 and pxx.max() < W - 3
              and np.nonzero(plant.any(axis=1))[0].min() > 2)
    drawn_dark = int(lum[plant].min())
    plate_dark = int((0.299 * b0[..., 0] + 0.587 * b0[..., 1]
                      + 0.114 * b0[..., 2])[whip].min())
    c8 = drawn_dark >= plate_dark
    c9 = int((mask > 0).sum())

    print("C1 px changed in his silhouette off the mask %-5d (== 0)    %s"
          % (c1, "PASS" if c1 == 0 else "FAIL"))
    print("C1a px of him the erase mask claims at all %-5d   (< 2600)  %s"
          % (c1a, "PASS" if c1a < 2600 else "FAIL"))
    print("C1b maxdiff over his face+torso+hands %-5d        (== 0)    %s"
          % (c1b, "PASS" if c1b == 0 else "FAIL"))
    print("C2 whip px surviving in the old footprint %-6d   (== 0)    %s"
          % (c2, "PASS" if c2 == 0 else "FAIL"))
    print("C3 fruit components outside his body %-3d          (== 1)    %s"
          % (c3, "PASS" if c3 == 1 else "FAIL"))
    print("C4 fig bottom above the root line %-4d px         (>= 30)   %s"
          % (c4, "PASS" if c4 >= 30 else "FAIL"))
    print("C5 plant px within 8 of his body %-5d            (== 0)    %s"
          % (c5, "PASS" if c5 == 0 else "FAIL"))
    print("   measured clearance plant -> him: %d px" % gap)
    print("C6 plant height %.1f cm against canon %.0f        (30-50)   %s"
          % (c6, CANON_PLANT_CM, "PASS" if 30 <= c6 <= 50 else "FAIL"))
    print("C7 whole plant inside the frame %-5s             (True)    %s"
          % (c7, "PASS" if c7 else "FAIL"))
    print("C8 darkest drawn luma %d vs the plate's own %d    (>=)      %s"
          % (drawn_dark, plate_dark, "PASS" if c8 else "FAIL"))
    print("C9 finishing mask %d px (%.1f%% of frame)" % (c9, 100.0 * c9 / (W * H)))
    if c1 != 0: fails.append("FAIL-FILL-ESCAPED(C1)")
    if c1a >= 2600: fails.append("FAIL-MASK-OVER-HIM(C1a,P3)")
    if c1b != 0: fails.append("FAIL-FACE-OR-HANDS-MOVED(C1b,P3,P4)")
    if c2 != 0: fails.append("FAIL-WHIP-SURVIVES(C2,P6)")
    if c3 != 1: fails.append("FAIL-COUNT(C3,P1,Q9)")
    if c4 < 30: fails.append("FAIL-FRUIT-ON-GROUND(C4,P1,Q1)")
    if c5 != 0: fails.append("FAIL-CONTACT(C5,P3,Q3)")
    if not 30 <= c6 <= 50: fails.append("FAIL-SCALE(C6)")
    if not c7: fails.append("FAIL-CROP(C7,P2,Q2)")
    if not c8: fails.append("FAIL-LINE-TOO-STRONG(C8)")

    if a.dry_run:
        print("DRY RUN: mask and erase written, no composite saved.")
        return 0 if not fails else 3
    Image.fromarray(comp).save(a.out)
    out_sha = sha256_of(Path(a.out))
    print("composite sha256 %s" % out_sha)
    meta = {
        "tool": "pipeline/beat19_sapling_composite.py",
        "beat": 19,
        "node": "002b-first-citizen",
        "what_this_is": (
            "The COMPOSITE INIT that REVS[(19,3)]'s verdict names as the next "
            "rung after three wordings closed the plant ladder. NOT a fourth "
            "wording: no prompt was fired and no sampler ran."),
        "sampler": "NONE -- plain image processing",
        "cost_usd": 0.0,
        "provider": "none",
        "gpu": "none",
        "sources": [
            {"role": "body/pose/field/framing/light (unaltered)",
             "path": str(plate.relative_to(REPO)), "sha256": a.plate_sha256,
             "why": "r3 passes 5 of 7 of its own bar; P3's hands are carried, not re-tested"},
            {"role": "the fig (silhouette, modelling, canon colour)",
             "path": str(figp.relative_to(REPO)), "sha256": a.fig_plate_sha256,
             "why": "beat 18's canon plate passes its bar as ONE deep-purple-violet fig on ONE thin branch"},
        ],
        "drawn_not_sourced": (
            "stem, one thin side-branch, two leaves -- procedural, in colours "
            "sampled from the whips this tool deletes (pattern §3.1)"),
        "removed": (
            "BOTH whips whole: leaf clusters, threads, all three crystals, woody "
            "stems and the two segments crossing his cloak. No stub or attachment "
            "point is left anywhere (pattern §13)."),
        "vacancy_fill": (
            "per-row linear interpolation from the region's own surviving "
            "boundary, WITHIN CLASS -- background holes from background, the "
            "cloak hole from cloak. Nothing cloned from elsewhere in the frame "
            "(pattern 12). The prescribed diffusion relaxation is present but "
            "OFF: measured at 0/6/20/90 iterations on this mask it washed the "
            "pink hill band and the teal treeline out of a 40x50 px vacancy, "
            "because a hole narrow in x and crossing bands in y is the case "
            "where averaging loses the structure."),
        "transform": {
            "horizon_y": HORIZON_Y, "figure_ground_y": FIG_GROUND_Y,
            "px_per_cm_at_figure": PX_PER_CM_AT_FIG,
            "px_per_cm_at_root": round(ppc_root, 4),
            "canon_plant_cm": CANON_PLANT_CM, "plant_px": round(plant_px, 1),
            "canon_fig_cm": CANON_FIG_CM, "fig_px": fig_px,
            "root_px": list(ROOT), "stem_apex_px": list(STEM_APEX),
            "branch_tip_px": list(BRANCH_TIP),
            "leaf_tips_px": [list(LEAF_L_TIP), list(LEAF_R_TIP)],
            "fig_cutout": fmeta,
            "scale_derivation": (
                "head 140 px crown-to-chin / 23 cm = 6.09 px/cm at his depth "
                "(ground y=910); ground plane px/cm(y) = 6.09*(y-425)/485; his "
                "seated crown-to-sole 632 px = 104 cm as the cross-check. The "
                "plate's own three crystals are 43/44/31 px tall, so a 7 cm fig "
                "at %d px is the plate's own scale for a fruit." % fig_px),
        },
        "palette_measured_from_plate": {k: (list(v) if isinstance(v, tuple) else v)
                                       for k, v in pal.items()},
        "plate_fruit_median_luma": round(tlum, 1),
        "whip_matte_px": int(whip.sum()),
        "finishing_mask_png": Path(a.mask_out).name,
        "finishing_mask_px": c9,
        "body_run_px": int(body.sum()),
        "cross_matte_px": int(cross.sum()),
        "checks": {"C1_fill_escaped_px": c1, "C1a_mask_over_him_px": c1a,
                   "C1b_face_hands_maxdiff": c1b, "C2_whip_residual_px": c2,
                   "C3_fruit_components": c3, "C4_fig_above_root_px": c4,
                   "C5_plant_within_8px_of_body": c5,
                   "C5_measured_clearance_px": gap,
                   "C6_plant_height_cm": round(c6, 1), "C7_plant_in_frame": c7,
                   "C8_drawn_dark": drawn_dark, "C8_plate_dark": plate_dark},
        "fails": fails,
        "composite_sha256": out_sha,
        "bar": ("scored against DRAFTS[19]'s pre-registered P1-P7 and Q1-Q9 "
                "byte for byte; nothing softened and nothing tightened"),
        "date": date.today().isoformat(),
        "approved": False,
        "provisional": True,
        "scored": False,
    }
    Path(a.out + ".meta.yaml").write_text(
        "\n".join("%s: %s" % (k, json.dumps(v, default=int))
                  for k, v in meta.items()) + "\n")
    if fails:
        print("COMPOSITE FAILED: %s" % ", ".join(fails))
        return 3
    print("COMPOSITE PASSES C1-C8. Now OPEN IT at full resolution: a metric is a "
          "filter, never a verdict.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
