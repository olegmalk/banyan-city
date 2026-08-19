#!/usr/bin/env python3
r"""Author beat 08's TWO-FIGURE COCO-18 POSE HINT for an openpose ControlNet.

WHY A SECOND HINT TOOL RATHER THAN A FLAG ON THE FIRST ONE.
`author_b08_pose_hint.py` draws for a SCRIBBLE net: white strokes that mean
"these lines are lines in the picture". `b08-arm-route-0819.md` §10 closed that
whole family on measurement -- three axes bracketed, and any hint a scribble net
can read is a hint it TRACES while any hint it cannot read it IGNORES OR DRAWS
(rung 5's skeleton came back as glowing crosses and orbs on both chests, guard
spine column luma 212.3 against a 165.4 surround). A pose hint is a different
KIND of object: an 18-point COCO skeleton in a fixed 18-colour code, where the
COLOUR of a stroke is what identifies the body part. Sharing a drawing function
between the two classes would mean one bug could move a filed verdict's
condition, so they are separate files with separate selftests.

THE SPEC IS TRANSCRIBED, NOT REMEMBERED. Every constant below comes from
`pipeline/research/openpose-controlnet-sdxl-0819.md` §2, which fetched and read
`controlnet_aux/open_pose/util.py::draw_bodypose` upstream. No preprocessor, no
annotator, no `controlnet_aux` dependency, no model -- which is what keeps this
route clear of `lllyasviel/Annotators`, the one licence landmine in our own
cache (B01-R9-PLAN.md §9: DO NOT USE FOR CANON, its per-file terms inherit CMU
OpenPose's non-commercial licence).

THE THREE TRAPS THE RESEARCH NAMES, ALL THREE HANDLED HERE:

  1. LIMB COLOURS AND DOT COLOURS INDEX THE SAME 18-COLOUR LIST DIFFERENTLY.
     Limbs are zip(limbSeq, colors) -- colour i belongs to LIMB i. Dots are
     zip(keypoints, colors) -- colour i belongs to KEYPOINT i. So the nose DOT is
     (255,0,0) while the neck->R-shoulder LIMB is also (255,0,0), and the R-wrist
     DOT is (170,255,0) while the R-elbow->R-wrist LIMB is (255,255,0). Anybody
     who writes "one colour per body part" produces a hint the net has never
     seen. --selftest asserts both halves of this against each other.

  2. LINE THICKNESS IS LOAD-BEARING FOR xinsir SPECIFICALLY. His own card: "When
     using the default pose line the performance may be unstable, this is because
     the pose label use more thick line in training to have a better look." He
     ships a replacement draw_bodypose whose only change is a resolution ratio.
     At our 1216-tall canvas the band is ratio 3.0 -> limbs 24 px thick, dots
     r=12. Drawing a 4 px skeleton at this size is a DOCUMENTED way to get an
     ignored hint, and it would look exactly like the failure rung 5 already had.
     Independently reported in comfyui_controlnet_aux#447.

  3. OCCLUSION IS EXPRESSED BY OMISSION. A missing keypoint is skipped, and every
     limb touching it is skipped too. There is no sentinel value.

WHAT IS DELIBERATELY NOT DRAWN, AND IT IS THE WHOLE LESSON OF RUNG 5.
NO BOARD RECTANGLE AND NO GROUND TICKS. A pose net's entire vocabulary is 18
keypoints; a rectangle is not a pose and this net was never trained on one.
Rung 5 put ink a net could not read into a hint and the net DREW IT. Repeating
that with a clipboard would be the same category error in a new coat. So B4a
(the board is down at the hip) becomes a PROMPT-ONLY clause in any sample built
on this hint, and that must be pre-registered as at risk rather than discovered.
Both figures' feet land on one y anyway, which is all B3 ever asked, so the
ground ticks were only ever the scribble class's way of saying it.

THE STAGING IS IMPORTED, NOT RE-DERIVED. Every fraction, and the two-link elbow
solver, come from `author_b08_pose_hint`, so a sample on this hint differs from
rung 2 in NET and HINT CLASS only -- not in where anybody is standing. Both
failure modes of the arm still refuse: too far apart raises on a stretched limb,
too close on a folded elbow.

THE WRIST, NOT THE FINGERTIP, IS THE LAST MARK. COCO-18 has no finger keypoint;
a pose net draws the hand BEYOND the wrist. So the R-wrist sits exactly where the
contour hint's wrist sat (275.2, 673.1) and the hand the model adds lands where
that hint drew its fingertip and its clearance. Putting the wrist at the fingertip
would ask for an arm one hand too long.

    python3 pipeline/author_b08_openpose_hint.py pipeline/control/b08-openpose-0819.png
    python3 pipeline/author_b08_openpose_hint.py --selftest    # no GPU, no weights
"""
from __future__ import annotations

import argparse
import hashlib
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from author_b08_pose_hint import (  # noqa: E402  -- the staging is shared, on purpose
    CLEARANCE, FINGER, FOREARM, GOBLIN_H, GOBLIN_X, GROUND_Y, GUARD_H, GUARD_X,
    EXT_MAX, EXT_MIN, H, HIP_FRAC, NAVEL_FRAC, SHOULDER_FRAC, UPPER_ARM, W,
    solve_elbow,
)

# ---------------------------------------------------------------------------
# COCO-18, 0-indexed. Not taken on trust -- the research DERIVED this ordering
# from the limbSeq table below, which is self-consistent only with it.
# ---------------------------------------------------------------------------
KP = ["nose", "neck", "Rsho", "Relb", "Rwri", "Lsho", "Lelb", "Lwri",
      "Rhip", "Rkne", "Rank", "Lhip", "Lkne", "Lank",
      "Reye", "Leye", "Rear", "Lear"]
IDX = {n: i for i, n in enumerate(KP)}

# The shared 18-colour ramp, RGB, exactly as in controlnet_aux's source.
COLORS = [(255, 0, 0), (255, 85, 0), (255, 170, 0), (255, 255, 0),
          (170, 255, 0), (85, 255, 0), (0, 255, 0), (0, 255, 85),
          (0, 255, 170), (0, 255, 255), (0, 170, 255), (0, 85, 255),
          (0, 0, 255), (85, 0, 255), (170, 0, 255), (255, 0, 255),
          (255, 0, 170), (255, 0, 85)]

# limbSeq, converted from the source's 1-indexed table to 0-indexed keypoints.
# Order matters: limb i takes COLORS[i]. COLORS[17] is never a limb colour -- it
# only ever appears as the L-ear DOT.
LIMBS = [(1, 2), (1, 5), (2, 3), (3, 4), (5, 6), (6, 7), (1, 8), (8, 9),
         (9, 10), (1, 11), (11, 12), (12, 13), (1, 0), (0, 14), (14, 16),
         (0, 15), (15, 17)]

# xinsir's replacement draw_bodypose: stickwidth stays 4, and the ellipse minor
# semi-axis and the dot radius are both multiplied by a resolution ratio.
STICKWIDTH = 4
DOT_R_BASE = 4
LIMB_ALPHA = 0.6          # limbs at 60% intensity; dots at full, on top


def ratio_for(width, height):
    """xinsir's own resolution bands, read off his model card.

    Returned rather than hardcoded so --selftest can assert the band boundaries
    instead of asserting one number that happens to be right for one canvas.
    """
    m = max(width, height)
    for limit, r in ((500, 1.0), (1000, 2.0), (2000, 3.0), (3000, 4.0),
                     (4000, 5.0), (5000, 6.0)):
        if m < limit:
            return r
    return 7.0


def ellipse2poly(cx, cy, a, b, angle_deg, step=1):
    """cv2.ellipse2Poly, in six lines of PIL-compatible geometry.

    The reference draws each limb as a FILLED ELLIPSE at the limb's midpoint --
    major semi-axis length/2, minor semi-axis stickwidth*ratio, rotated to
    atan2(dY, dX). It is not a capsule: it tapers to a point at both ends, which
    is why a plain rounded line is a substitute rather than a reproduction. This
    reproduces it.
    """
    ca, sa = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
    pts = []
    for t in range(0, 360, step):
        ct, st = math.cos(math.radians(t)), math.sin(math.radians(t))
        pts.append((cx + a * ct * ca - b * st * sa,
                    cy + a * ct * sa + b * st * ca))
    return pts


def figure_keypoints(cx, stature, ground_y, head_frac, torso_half,
                     head_ratio=0.80):
    """A front-facing standing COCO-18 skeleton, from stature alone.

    Every fraction is measured FROM THE GROUND, because that is how stature
    works and it is how `author_b08_pose_hint` already states the shared ones.
    Returns a dict name -> (x, y); a caller overrides whichever limb it is
    staging.
    """
    def up(f):
        return ground_y - f * stature

    head_h = head_frac * stature
    head_w = head_ratio * head_h
    nose_y = ground_y - stature + head_h * 0.55   # the face, not the crown
    sho_y = up(SHOULDER_FRAC)
    hip_y = up(HIP_FRAC)
    return {
        "nose": (cx, nose_y),
        "neck": (cx, sho_y),                      # COCO's neck IS the shoulder midpoint
        "Rsho": (cx - torso_half * 0.95, sho_y),
        "Lsho": (cx + torso_half * 0.95, sho_y),
        "Relb": (cx - torso_half * 1.05, up(0.66)),
        "Lelb": (cx + torso_half * 1.05, up(0.66)),
        "Rwri": (cx - torso_half * 1.00, up(0.48)),
        "Lwri": (cx + torso_half * 1.00, up(0.48)),
        "Rhip": (cx - torso_half * 0.60, hip_y),
        "Lhip": (cx + torso_half * 0.60, hip_y),
        "Rkne": (cx - torso_half * 0.55, up(0.285)),
        "Lkne": (cx + torso_half * 0.55, up(0.285)),
        "Rank": (cx - torso_half * 0.50, up(0.035)),
        "Lank": (cx + torso_half * 0.50, up(0.035)),
        "Reye": (cx - head_w * 0.20, nose_y - head_h * 0.14),
        "Leye": (cx + head_w * 0.20, nose_y - head_h * 0.14),
        "Rear": (cx - head_w * 0.46, nose_y - head_h * 0.10),
        "Lear": (cx + head_w * 0.46, nose_y - head_h * 0.10),
    }


def stage(width=W, height=H, guard_x=GUARD_X, goblin_x=GOBLIN_X,
          guard_h=GUARD_H, goblin_h=GOBLIN_H, ground_y=GROUND_Y,
          clearance=CLEARANCE):
    """Both figures' keypoints plus the metadata the bar is scored off.

    The arm is SOLVED, not drawn by eye, by the same two-link triangle
    `author_b08_pose_hint` uses -- so the pose asked of the pose net is the pose
    that was asked of the scribble net, to the pixel.
    """
    if not 0.0 < ground_y < 1.0:
        raise ValueError("ground_y must be in (0,1), got %r" % (ground_y,))
    if not 0.0 < guard_h < 1.0 or not 0.0 < goblin_h < 1.0:
        raise ValueError("stature fractions must be in (0,1)")
    if not 0.0 <= clearance < 0.5:
        raise ValueError("clearance must be in [0,0.5), got %r" % (clearance,))
    if goblin_x >= guard_x:
        raise ValueError("the goblin stands at frame LEFT of the guard")

    gy = ground_y * height
    gu_h, go_h = guard_h * height, goblin_h * height
    gu_cx, go_cx = guard_x * width, goblin_x * width
    gu_half, go_half = 0.070 * gu_h, 0.075 * go_h

    guard = figure_keypoints(gu_cx, gu_h, gy, 0.130, gu_half, head_ratio=0.72)
    goblin = figure_keypoints(go_cx, go_h, gy, 0.155, go_half, head_ratio=0.80)

    # ---- THE POINT, AND IT IS SOLVED DIFFERENTLY FROM THE CONTOUR HINT'S FOR A
    # REASON THAT IS NOT A PREFERENCE.
    #
    # `author_b08_pose_hint` puts the WRIST on the shoulder->belly ray and then
    # draws a separate 1 px FINGER stroke from the wrist toward the belly. The
    # aim is carried by that finger, so the forearm itself is free to bend
    # wherever the two-link solution puts it -- and it does: extend that hint's
    # elbow->wrist segment and it passes 29.1 px wide of the belly.
    #
    # COCO-18 HAS NO FINGER KEYPOINT. The elbow->wrist limb is the last mark in
    # the drawing, so IT has to be the thing that aims, and a pose net draws the
    # hand BEYOND the wrist. So the construction inverts: the elbow is solved
    # against a target that is the belly minus a HAND'S WORTH of reach, and the
    # wrist is then placed one forearm along the elbow->belly line. The forearm,
    # extended, now runs through the belly, and the hand the model adds lands on
    # it.
    #
    # Same two-link solver, same shoulder, same target, same total reach, same
    # EXT band -- so the two classes still refuse at the same separations and a
    # sample on this hint is still a NET comparison. Only the elbow and wrist
    # move, and --selftest asserts BOTH halves of that: the shared numbers are
    # equal, and this forearm hits the belly where the contour's misses it.
    near_sx, near_sy = guard["Rsho"]
    go_navel_y = gy - NAVEL_FRAC * go_h
    target = (go_cx + go_half, go_navel_y)          # the near edge of his belly
    dx, dy = target[0] - near_sx, target[1] - near_sy
    full = math.hypot(dx, dy)
    if full <= 0:
        raise ValueError("the two figures are on top of each other")
    upper, fore = UPPER_ARM * gu_h, FOREARM * gu_h
    arm = upper + fore
    # The air the drawn hand occupies: the fingertip clearance the staging wants,
    # plus the finger length the contour hint drew explicitly.
    hand = clearance * height + FINGER * gu_h
    ext = (full - hand) / arm
    if ext > EXT_MAX:
        raise ValueError(
            "the wrist would sit %.1f px from the shoulder but the arm is %.1f px "
            "(%.2f extension). This staging asks for a stretched limb."
            % (full - hand, arm, ext))
    if ext < EXT_MIN:
        raise ValueError(
            "the wrist would sit at %.2f extension (min %.2f): the figures are so "
            "close the elbow folds, and a folded arm reads as a jab, not a point."
            % (ext, EXT_MIN))
    # Second link lengthened by the hand, so that the WRIST -- one forearm along
    # elbow->belly -- ends up a hand short of the target rather than on it.
    elbow = solve_elbow(near_sx, near_sy, target[0], target[1],
                        upper, fore + hand, sign=1.0)
    edx, edy = target[0] - elbow[0], target[1] - elbow[1]
    ed = math.hypot(edx, edy)
    wrist = (elbow[0] + edx / ed * fore, elbow[1] + edy / ed * fore)
    guard["Relb"], guard["Rwri"] = elbow, wrist

    # ---- the guard's OTHER arm hangs to where the board is held, at the hip.
    # No rectangle is drawn (see the docstring), but the ARM still has to go
    # somewhere, and a hand at the hip is what "clipboard lowered in one hand"
    # looks like as a pose.
    gu_hip_y = gy - HIP_FRAC * gu_h
    far_sx, far_sy = guard["Lsho"]
    board_grip = (gu_cx + 0.105 * width - 0.135 * width * 0.28,
                  gu_hip_y + 0.012 * height - 0.115 * height / 2.0)
    guard["Lwri"] = board_grip
    guard["Lelb"] = (far_sx + 0.010 * gu_h, (far_sy + board_grip[1]) / 2.0)

    # ---- the goblin's arms hang AT HIS SIDES, which is the staging decision
    # that clears the occupied-lane blocker: the gap between the guard's
    # fingertip and the belly stays empty.
    go_hip_y = gy - HIP_FRAC * go_h
    for s, sho, elb, wri in ((-1, "Rsho", "Relb", "Rwri"),
                             (1, "Lsho", "Lelb", "Lwri")):
        sx = goblin[sho][0]
        goblin[elb] = (sx + s * 0.02 * go_h, go_hip_y)
        goblin[wri] = (sx + s * 0.01 * go_h, gy - 0.40 * go_h)

    meta = {
        "size": "%dx%d" % (width, height),
        "hint_class": "COCO-18 openpose skeleton (colour-coded, 2 figures)",
        "ratio": ratio_for(width, height),
        "limb_thickness_px": 2 * STICKWIDTH * ratio_for(width, height),
        "dot_radius_px": DOT_R_BASE * ratio_for(width, height),
        "ground_y_px": round(gy, 1),
        "guard": {"cx": round(gu_cx, 1), "stature_px": round(gu_h, 1),
                  "nose": tuple(round(v, 1) for v in guard["nose"]),
                  "shoulder_y": round(guard["Rsho"][1], 1),
                  "feet_y": round(gy, 1)},
        "goblin": {"cx": round(go_cx, 1), "stature_px": round(go_h, 1),
                   "nose": tuple(round(v, 1) for v in goblin["nose"]),
                   "navel_y": round(go_navel_y, 1),
                   "torso_half_px": round(go_half, 1),
                   "feet_y": round(gy, 1)},
        "stature_ratio": round(gu_h / go_h, 3),
        "point": {"limb": "R-elbow -> R-wrist, COLORS[3] = (255, 255, 0)",
                  "shoulder": tuple(round(v, 1) for v in guard["Rsho"]),
                  "elbow": tuple(round(v, 1) for v in elbow),
                  "wrist": tuple(round(v, 1) for v in wrist),
                  "target_belly": tuple(round(v, 1) for v in target),
                  "shoulder_to_belly_px": round(full, 1),
                  "arm_px": round(arm, 1),
                  "extension": round(ext, 3)},
        "board_drawn": False,
        "ground_ticks_drawn": False,
        "ink_fraction": None,
    }
    return guard, goblin, meta


def draw_bodypose(img, kps, ratio):
    """One figure onto an existing RGB canvas. LIMBS FIRST, DOTS SECOND.

    `kps` maps a COCO-18 name to (x, y) or to None for a keypoint that is not
    present. A missing keypoint is skipped and so is every limb touching it --
    occlusion by omission, exactly as the reference does it.
    """
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    minor = STICKWIDTH * ratio

    for i, (a, b) in enumerate(LIMBS):
        pa, pb = kps.get(KP[a]), kps.get(KP[b])
        if pa is None or pb is None:
            continue
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        length = math.hypot(dx, dy)
        if length <= 0:
            continue
        c = tuple(int(v * LIMB_ALPHA) for v in COLORS[i])
        d.polygon(ellipse2poly((pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0,
                               length / 2.0, minor,
                               math.degrees(math.atan2(dy, dx))), fill=c)

    r = DOT_R_BASE * ratio
    for i, name in enumerate(KP):
        p = kps.get(name)
        if p is None:
            continue
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=COLORS[i])
    return img


def build(**kw):
    """Draw the two-figure hint. Returns (PIL RGB image, metadata dict)."""
    from PIL import Image
    width = kw.get("width", W)
    height = kw.get("height", H)
    guard, goblin, meta = stage(**kw)
    img = Image.new("RGB", (width, height), (0, 0, 0))
    ratio = meta["ratio"]
    # The GOBLIN first so that where the guard's pointing arm passes in front of
    # him, the guard's limb is the one on top -- which is what the staging says
    # is happening in space.
    draw_bodypose(img, goblin, ratio)
    draw_bodypose(img, guard, ratio)
    return img, meta


def ink_fraction(img):
    hist = img.convert("L").histogram()
    return sum(hist[32:]) / float(sum(hist))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def selftest():
    """THE TRANSCRIBED SPEC AND THE BAR, BEFORE ANY PIXELS. No GPU, no weights."""
    fails = []

    def check(name, cond):
        print(("  ok   " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    # ---- THE SPEC, asserted against itself ------------------------------
    check("the ramp is 18 colours", len(COLORS) == 18)
    check("the ramp has no duplicates", len(set(COLORS)) == 18)
    check("COCO-18 has 18 named keypoints", len(KP) == 18 and len(IDX) == 18)
    check("limbSeq has 17 entries, one short of the ramp", len(LIMBS) == 17)
    check("every limb names two real keypoints",
          all(0 <= a < 18 and 0 <= b < 18 and a != b for a, b in LIMBS))
    check("COLORS[17] (255,0,85) is never a LIMB colour -- it is only the "
          "L-ear dot", 17 not in range(len(LIMBS)))

    # The ordering is derived from limbSeq, so limbSeq must agree with the names.
    for want, (a, b) in (("neck-Rsho", LIMBS[0]), ("neck-Lsho", LIMBS[1]),
                         ("Rsho-Relb", LIMBS[2]), ("Relb-Rwri", LIMBS[3]),
                         ("Lsho-Lelb", LIMBS[4]), ("Lelb-Lwri", LIMBS[5]),
                         ("neck-Rhip", LIMBS[6]), ("neck-Lhip", LIMBS[9]),
                         ("neck-nose", LIMBS[12]), ("Lear", LIMBS[16])):
        pass
    check("limb 3 is R-elbow -> R-wrist, the segment that aims the gesture",
          LIMBS[3] == (IDX["Relb"], IDX["Rwri"]))
    check("limb 3's colour is (255,255,0) as the research transcribes",
          COLORS[3] == (255, 255, 0))
    check("limb 12 is neck -> nose", LIMBS[12] == (IDX["neck"], IDX["nose"]))
    check("limb 16 is L-eye -> L-ear", LIMBS[16] == (IDX["Leye"], IDX["Lear"]))

    # ---- TRAP 1: limbs and dots index the SAME list DIFFERENTLY ----------
    check("the NOSE DOT and the neck->R-shoulder LIMB share (255,0,0) -- the "
          "collision the research warns about",
          COLORS[IDX["nose"]] == (255, 0, 0) and COLORS[0] == (255, 0, 0))
    check("the R-WRIST DOT (170,255,0) differs from the R-elbow->R-wrist LIMB "
          "(255,255,0) -- so 'one colour per body part' is WRONG",
          COLORS[IDX["Rwri"]] == (170, 255, 0) != COLORS[3])
    check("the L-ear dot is COLORS[17] = (255,0,85)",
          COLORS[IDX["Lear"]] == (255, 0, 85))

    # ---- TRAP 2: thickness ----------------------------------------------
    check("our canvas lands in xinsir's ratio-3.0 band", ratio_for(W, H) == 3.0)
    for m, r in ((499, 1.0), (500, 2.0), (999, 2.0), (1000, 3.0), (1999, 3.0),
                 (2000, 4.0), (4999, 6.0), (5000, 7.0), (9000, 7.0)):
        check("ratio band max(W,H)=%d -> %.1f" % (m, r), ratio_for(m, 10) == r)

    img, m = build()
    check("canvas is the render size the beat is conditioned at", img.size == (W, H))
    check("limbs are 24 px thick at ratio 3.0 (thin lines are the documented "
          "ignored-hint trap)", m["limb_thickness_px"] == 24.0)
    check("dots are r=12 at ratio 3.0", m["dot_radius_px"] == 12.0)
    frac = ink_fraction(img)
    check("hint carries ink but is not a fill (%.4f)" % frac, 0.005 < frac < 0.25)

    # ---- TRAP 3: omission ------------------------------------------------
    from PIL import Image
    gu, go, _ = stage()
    full_ink = ink_fraction(draw_bodypose(Image.new("RGB", (W, H)), gu, 3.0))
    cut = dict(gu)
    cut["Rwri"] = None
    cut_ink = ink_fraction(draw_bodypose(Image.new("RGB", (W, H)), cut, 3.0))
    check("dropping the R-wrist removes ITS dot AND the limb that touches it "
          "(%.4f -> %.4f)" % (full_ink, cut_ink), cut_ink < full_ink)
    allnone = {k: None for k in KP}
    check("a figure with every keypoint missing draws NOTHING",
          ink_fraction(draw_bodypose(Image.new("RGB", (W, H)), allnone, 3.0)) == 0.0)

    # ---- THE BAR, as geometry -------------------------------------------
    gum, gom, pt = m["guard"], m["goblin"], m["point"]
    check("B1 two figures, horizontally separated",
          gom["cx"] + gom["torso_half_px"] < gum["cx"] - gom["torso_half_px"])
    check("B3 both figures' feet are on the SAME y",
          gum["feet_y"] == gom["feet_y"] == m["ground_y_px"])
    check("B5 the guard is taller (%.3fx)" % m["stature_ratio"],
          m["stature_ratio"] > 1.0)
    check("B5 and nobody towers (%.3f < 1.35)" % m["stature_ratio"],
          m["stature_ratio"] < 1.35)
    check("B4 the pose is anatomically reachable (%.3f extension)"
          % pt["extension"], EXT_MIN < pt["extension"] < EXT_MAX)
    check("B4 the elbow is off the shoulder-wrist line, i.e. actually bent",
          abs(pt["elbow"][1] - (pt["shoulder"][1] + pt["wrist"][1]) / 2) > 4)
    check("B4 the wrist is between the two figures, not past the goblin",
          gom["cx"] < pt["wrist"][0] < gum["cx"])

    # THE GESTURE IS SCORED AS A RAY, because that is the only thing a pose net
    # can express: the R-elbow -> R-wrist segment, extended, must pass close to
    # the belly. A hand drawn beyond the wrist then lands on the target.
    ex, ey = pt["elbow"]
    wx, wy = pt["wrist"]
    tx, ty = pt["target_belly"]
    seg = math.hypot(wx - ex, wy - ey)
    ux, uy = (wx - ex) / seg, (wy - ey) / seg
    t = (tx - ex) * ux + (ty - ey) * uy
    perp = abs((tx - ex) * (-uy) + (ty - ey) * ux)
    check("B4 the belly is AHEAD of the wrist along the forearm ray "
          "(%.1f px along, wrist at %.1f)" % (t, seg), t > seg)
    check("B4 the forearm ray passes within 20 px of the belly (%.1f px)" % perp,
          perp < 20.0)

    # ---- THE STAGING IS THE SAME STAGING, which is what makes a sample on this
    # hint a NET comparison rather than a new experiment.
    from author_b08_pose_hint import build as build_contour
    _, cm = build_contour()
    for k in ("ground_y_px", "stature_ratio", "size"):
        check("staging matches the contour hint: %s" % k, m[k] == cm[k])
    for who in ("guard", "goblin"):
        for k in ("cx", "stature_px", "feet_y"):
            check("staging matches the contour hint: %s.%s" % (who, k),
                  m[who][k] == cm[who][k])
    # THE SHARED HALF: same shoulder, same target, same total reach, same
    # extension -- so the gesture asked of the pose net is the gesture asked of
    # the scribble net, from the same body, at the same stretch.
    for k in ("shoulder", "target_belly"):
        check("the POINT is the same point as the contour hint's: %s" % k,
              tuple(m["point"][k]) == tuple(cm["point"][k]))
    for k in ("arm_px", "shoulder_to_belly_px", "extension"):
        check("the POINT is the same point as the contour hint's: %s" % k,
              m["point"][k] == cm["point"][k])

    # THE HALF THAT MUST DIFFER, AND THE REASON ASSERTED AS A MEASUREMENT.
    # The contour hint aims with a separate finger stroke, so its forearm is free
    # to bend; this class has no finger keypoint, so the forearm must aim. If
    # both hints somehow produced the same elbow, one of the two would be wrong.
    check("the elbow DIFFERS from the contour hint's, as the construction "
          "requires", tuple(m["point"]["elbow"]) != tuple(cm["point"]["elbow"]))
    check("the wrist DIFFERS from the contour hint's",
          tuple(m["point"]["wrist"]) != tuple(cm["point"]["wrist"]))

    def ray_miss(pm):
        ex_, ey_ = pm["elbow"]
        wx_, wy_ = pm["wrist"]
        tx_, ty_ = pm["target_belly"]
        s = math.hypot(wx_ - ex_, wy_ - ey_)
        ux_, uy_ = (wx_ - ex_) / s, (wy_ - ey_) / s
        return abs((tx_ - ex_) * (-uy_) + (ty_ - ey_) * ux_)

    contour_miss = ray_miss(cm["point"])
    check("the CONTOUR hint's forearm ray MISSES the belly by >20 px (%.1f) -- "
          "which is why it needed a finger stroke and why this class cannot "
          "reuse its elbow" % contour_miss, contour_miss > 20.0)
    check("this hint's forearm ray hits it (%.1f px) with no finger keypoint "
          "anywhere" % ray_miss(m["point"]), ray_miss(m["point"]) < 20.0)

    # ---- WHAT MUST NOT BE DRAWN, asserted so nobody "fixes" it -----------
    check("NO board rectangle is drawn (a rectangle is not a pose; rung 5 "
          "proved unreadable ink gets DRAWN)", m["board_drawn"] is False)
    check("NO ground ticks are drawn (same reason; one foot line already says "
          "what B3 asks)", m["ground_ticks_drawn"] is False)
    check("the hint records its own class", m["hint_class"].startswith("COCO-18"))

    # ---- both staging failure modes still refuse -------------------------
    for kw, why in (({"goblin_x": 0.02}, "too FAR apart (stretched limb)"),
                    ({"goblin_x": 0.50}, "too CLOSE (folded elbow)"),
                    ({"ground_y": 0.0}, "ground_y out of range"),
                    ({"guard_h": 0.0}, "stature out of range"),
                    ({"clearance": 0.8}, "clearance out of range"),
                    ({"goblin_x": 0.9}, "goblin right of the guard")):
        try:
            stage(**kw)
            check("refuses %s" % why, False)
        except ValueError:
            check("refuses %s" % why, True)

    # Polarity: a pose hint is COLOUR on BLACK, never white-on-black strokes.
    check("the canvas ground is black", img.getpixel((3, 3)) == (0, 0, 0))
    seen = {img.getpixel((x, y)) for x in range(0, W, 7) for y in range(0, H, 7)}
    check("the hint is polychrome -- more than 8 distinct colours present "
          "(%d)" % len(seen), len(seen) > 8)

    # Limbs are dimmed and dots are not, and that ordering is visible: the
    # brightest pixel in the frame must be a full-intensity dot colour.
    check("some pixel carries a FULL-intensity ramp colour (a dot on top)",
          bool(seen & set(COLORS)))
    dimmed = {tuple(int(v * LIMB_ALPHA) for v in c) for c in COLORS}
    check("some pixel carries a 60%-intensity limb colour", bool(seen & dimmed))

    import io
    b1, b2 = io.BytesIO(), io.BytesIO()
    build()[0].save(b1, "PNG")
    build()[0].save(b2, "PNG")
    check("authoring is deterministic", b1.getvalue() == b2.getvalue())

    print(("SELFTEST FAIL: %d" % len(fails)) if fails else "SELFTEST PASS")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(
        description="draw beat 08's two-figure COCO-18 openpose hint")
    ap.add_argument("out", nargs="?", help="output PNG")
    ap.add_argument("--width", type=int, default=W)
    ap.add_argument("--height", type=int, default=H)
    ap.add_argument("--guard-x", type=float, default=GUARD_X)
    ap.add_argument("--goblin-x", type=float, default=GOBLIN_X)
    ap.add_argument("--guard-h", type=float, default=GUARD_H)
    ap.add_argument("--goblin-h", type=float, default=GOBLIN_H)
    ap.add_argument("--ground-y", type=float, default=GROUND_Y)
    ap.add_argument("--clearance", type=float, default=CLEARANCE)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.out:
        ap.error("out PNG required (or --selftest)")

    img, meta = build(width=a.width, height=a.height, guard_x=a.guard_x,
                      goblin_x=a.goblin_x, guard_h=a.guard_h,
                      goblin_h=a.goblin_h, ground_y=a.ground_y,
                      clearance=a.clearance)
    meta["ink_fraction"] = round(ink_fraction(img), 5)
    img.save(a.out, "PNG")
    print("wrote %s" % a.out)
    for k, v in meta.items():
        print("  %s: %s" % (k, v))
    print("  sha256: %s" % sha256_file(a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
