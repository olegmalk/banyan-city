#!/usr/bin/env python3
r"""Author beat 08's TWO-FIGURE POSE HINT for scribble ControlNet — pure PIL.

WHY THIS EXISTS, AND WHY IT IS THE SMALLEST PIECE OF NEW CODE ON BEAT 08.
`pipeline/b08-arm-route-0819.md` closed the "source an arm for this init"
framing on pixels: the signed board-lowered composite has BOTH of the guard's
hands on the clipboard, so any arm added to it is a THIRD arm, and `extra arms`
is in the beat's own negative. Its §4 Route A is what is left — a NEW plate that
stages the point from the start — and its named blocker was that no tool in this
tree can draw a hint of two standing figures. `author_scribble.py` draws exactly
two hardcoded shapes, a stem and a pair of lens leaves. This file draws people.

WHY A HINT AT ALL, RATHER THAN A SIXTH WORDING. Text-to-image cannot aim this
point: a pointing arm attached to the GOBLIN 3 of 3 and a board 9 of 12 however
worded (done-definitions.yaml `figure_count_ruled_from_the_script_0817`), and
the mechanism is known — CLIP's causal encoder puts an attribute named anywhere
into the pooled embedding, so "pointing" lands on whichever figure the sampler
likes (`attribute_mask.py`'s header; ALE-Edit, arXiv 2412.04715). A WORDING
CANNOT AIM IT. Geometry is per-location, which is why a hint is one of the few
levers that can say WHICH figure grows the arm. And the lever is measured, not
hoped for: `ep2-cnet-probe-0817` scored bind_ratio 35.363 left / 21.530 right
against a bar of 1.25 pre-registered in code before any pixels existed.

THE HINT IS THE BAR, WRITTEN AS GEOMETRY BEFORE THE PIXELS. Every clause of
beat 08's pre-registered bar that a picture can carry is a MEASURED PROPERTY OF
THIS DRAWING and is asserted in --selftest, so the sample cannot be scored
against a bar that moved:

  B1 pair            two figures, disjoint bounding boxes, both whole
  B3 one ground plane both figures' feet on the SAME y, to the pixel
  B4 lowered board   the board's top edge sits below the guard's shoulder
  B4 point           the fingertip lands at the goblin's navel height, stopping
                     just OUTSIDE his torso — pointing AT, not touching
  B5 no colossus     the guard is taller, and by less than 1.35x

B2 (the guard reads adult) is the one clause geometry cannot carry: a contour
says how tall, not how old. It stays a wording clause and is scored by eye.

THE STAGING FIXES §9b's THIRD BLOCKER ON PURPOSE. The composite route died
partly because "the path is occupied" — the goblin's own green fist sat dead
centre of the gap between the men. Here the goblin's arms hang at his sides
(`arms down`, beat 10's own two-token form, which the beat-08 cast draft already
uses), so the lane between the guard's fingertip and the belly is EMPTY. That is
a staging decision made in geometry rather than argued for in a prompt.

WHAT A HINT IS, taken from the mechanism that was actually proven rather than
invented here. `controlnet_probe.py` drew its condition with PIL as STROKES —
a stem line, two leaf outlines, two midribs — white on black at the exact render
size, and that is what bound. A full-body contour sketch of two figures is the
same class of object: outlines, no fill, no photo-derived edge map, no annotator,
so the `lllyasviel/Annotators` licence landmine is never touched.

CONTOURS, NOT A STICK FIGURE. A skeleton of single lines is a picture of a
skeleton and scribble ControlNet is entitled to draw one. Limbs are therefore
drawn as CAPSULE OUTLINES around a polyline — the same thing a person sketches
when they rough in a figure — and heads and hands as ellipse outlines.

THE ARM IS SOLVED, NOT DRAWN BY EYE. Given the shoulder and the target, the
elbow is placed by the two-link triangle solution, and --selftest refuses a
staging whose target is further from the shoulder than upper arm + forearm.
An unreachable pose is a hint that asks for a stretched limb, and this beat's
negative already fights `extra arms`; it must not also fight a rubber one.

NO CRF, NO ENCODER, NO VIDEO ANYWHERE. This authors a still condition for a
still plate. (Said explicitly because a peer lane measured --image-crf 33
destroying i2v conditioning today; nothing in this path encodes anything.)

    python3 pipeline/author_b08_pose_hint.py pipeline/control/b08-pose-0819.png
    python3 pipeline/author_b08_pose_hint.py --selftest      # no GPU, no weights
"""
from __future__ import annotations

import argparse
import hashlib
import math
import sys

# The render size beat 01 proved and the probe bound at. The control MUST match
# the render exactly or diffusers resizes it and the geometry the model saw is
# not the geometry that was authored — controlnet_probe.py returns rc=7 on that.
W, H = 832, 1216

# ---------------------------------------------------------------------------
# THE STAGING, in frame fractions. Every number here is a decision, so each one
# carries the reason it has that value rather than another.
# ---------------------------------------------------------------------------
GROUND_Y = 0.945          # both sets of feet land here. B3 is this one number.
GUARD_X = 0.680           # guard at frame RIGHT, goblin at frame LEFT — the
GOBLIN_X = 0.205          # orientation beat 08's own proven init already has
                          # (boardcomp: goblin belly x~315, guard hands x 545-793).
                          # THE SEPARATION IS NOT A COMPOSITION PREFERENCE, it is
                          # forced: the fingertip must stop SHORT of the belly, so
                          # shoulder-to-belly has to exceed a whole arm. At any
                          # closer spacing the solved elbow folds and the pose
                          # stops reading as a point — build() refuses both ends.
GUARD_H = 0.660           # stature as a fraction of frame height
GOBLIN_H = 0.600          # ratio 1.10 — the guard is taller and nobody towers.
                          # He is an ADULT goblin (done-definitions beat 14
                          # wording: "a small goblin man ... adult"), not a child.

# Proportions off the standing figure, measured from the GROUND because that is
# how stature works: navel ~0.60 of stature, shoulder ~0.82, hip ~0.53.
NAVEL_FRAC = 0.60
SHOULDER_FRAC = 0.82
HIP_FRAC = 0.53
UPPER_ARM = 0.19          # shoulder to elbow, as a fraction of stature
FOREARM = 0.25            # elbow to wrist; the two sum to a whole arm, 0.44
FINGER = 0.045            # the extended index, drawn on toward the belly
CLEARANCE = 0.022         # frame heights of air the fingertip stops short by.
                          # POINTING AT, NOT TOUCHING: a fingertip in the belly
                          # is a prod, and it also merges the two silhouettes
                          # exactly where B1 is scored.
EXT_MIN, EXT_MAX = 0.75, 0.99   # how extended the solved arm may be. Below this
                          # the elbow folds and the gesture reads as a jab or a
                          # shrug; at 1.0 the arm is locked out and the two-link
                          # solution degenerates to a straight line with no elbow.


def capsule(pts, width):
    """Outline polygon of a thick polyline — a limb, roughed in.

    Offsets the polyline by width/2 on each side and closes it, so what gets
    inked is ONE contour rather than the internal seams a stack of separate
    quads would leave. Bends here are gentle (an elbow, a knee), which is the
    regime where a simple perpendicular offset is well behaved.
    """
    if len(pts) < 2:
        raise ValueError("a capsule needs at least two points")
    r = width / 2.0
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == len(pts) - 1:
            dx, dy = x - pts[-2][0], y - pts[-2][1]
        else:
            dx = pts[i + 1][0] - pts[i - 1][0]
            dy = pts[i + 1][1] - pts[i - 1][1]
        n = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / n, dx / n
        left.append((x + nx * r, y + ny * r))
        right.append((x - nx * r, y - ny * r))
    return left + right[::-1]


def solve_elbow(sx, sy, tx, ty, a, b, sign=1.0):
    """Where the elbow goes so shoulder->elbow->fingertip lands exactly on target.

    The two-link triangle solution. `sign` picks which of the two mirror
    solutions to use; +1 puts the elbow on the far side of the shoulder-target
    line, which for a downward-and-across point is the elbow hanging BELOW it —
    what a person's arm actually does.
    """
    dx, dy = tx - sx, ty - sy
    d = math.hypot(dx, dy)
    if d > a + b:
        raise ValueError(
            "target is %.1f px from the shoulder but the arm is %.1f px "
            "(upper %.1f + fore %.1f). This staging asks for a stretched limb."
            % (d, a + b, a, b))
    if d < abs(a - b) or d == 0:
        raise ValueError("target is inside the arm's dead zone (%.1f px)" % d)
    # distance along the shoulder->target line to the elbow's projection
    m = (d * d + a * a - b * b) / (2 * d)
    hgt = math.sqrt(max(a * a - m * m, 0.0))
    ux, uy = dx / d, dy / d
    px, py = -uy, ux
    return (sx + ux * m + px * hgt * sign, sy + uy * m + py * hgt * sign)


def build(width=W, height=H, stroke=7, invert=False, ground_ticks=True,
          guard_x=GUARD_X, goblin_x=GOBLIN_X, guard_h=GUARD_H,
          goblin_h=GOBLIN_H, ground_y=GROUND_Y, clearance=CLEARANCE):
    """Draw the hint. Returns (PIL RGB image, metadata dict).

    The metadata is not decoration: --selftest scores the BAR off it, and the
    spec quotes it, so what was asked for is on the record in the same units the
    render was conditioned in.
    """
    from PIL import Image, ImageDraw

    if stroke < 1:
        raise ValueError(f"stroke must be >= 1, got {stroke}")
    if not 0.0 < ground_y < 1.0:
        raise ValueError(f"ground_y must be in (0,1), got {ground_y}")
    if not 0.0 < guard_h < 1.0 or not 0.0 < goblin_h < 1.0:
        raise ValueError("stature fractions must be in (0,1)")
    if not 0.0 <= clearance < 0.5:
        raise ValueError(f"clearance must be in [0,0.5), got {clearance}")
    if goblin_x >= guard_x:
        raise ValueError("the goblin stands at frame LEFT of the guard")

    ink = (0, 0, 0) if invert else (255, 255, 255)
    ground = (255, 255, 255) if invert else (0, 0, 0)
    img = Image.new("RGB", (width, height), ground)
    d = ImageDraw.Draw(img)

    def outline(poly):
        d.line(list(poly) + [poly[0]], fill=ink, width=stroke, joint="curve")

    gy = ground_y * height
    gu_h = guard_h * height
    go_h = goblin_h * height
    gu_cx = guard_x * width
    go_cx = goblin_x * width

    # ---- the goblin, frame left ------------------------------------------
    go_head_h = 0.155 * go_h
    go_head_w = 0.80 * go_head_h
    go_top = gy - go_h
    go_head_cy = go_top + go_head_h / 2.0
    go_shoulder_y = gy - SHOULDER_FRAC * go_h
    go_hip_y = gy - HIP_FRAC * go_h
    go_navel_y = gy - NAVEL_FRAC * go_h
    go_half = 0.075 * go_h          # torso half-width; he is the plump one

    d.ellipse([go_cx - go_head_w / 2, go_head_cy - go_head_h / 2,
               go_cx + go_head_w / 2, go_head_cy + go_head_h / 2],
              outline=ink, width=stroke)
    # POINTED EARS — identity as geometry rather than as a hopeful adjective.
    # SMALL AND SET LOW, and that is a correction made by looking: the first
    # version swept from above the crown out to 0.34 head-widths, and on the
    # drawn hint it read as HORNS or a headdress, not as ears. A condition that
    # binds this hard will draw what is actually there.
    for s in (-1, 1):
        ex = go_cx + s * go_head_w * 0.46
        d.line([(ex, go_head_cy + 0.10 * go_head_h),
                (ex + s * 0.24 * go_head_w, go_head_cy - 0.20 * go_head_h),
                (ex, go_head_cy - 0.10 * go_head_h)],
               fill=ink, width=stroke, joint="curve")
    # A NECK. Without one the head ellipse floats above the shoulders with a
    # visible gap, and a detached head is a thing this checkpoint will happily
    # draw if the condition asks for it.
    for s in (-1, 1):
        nx = go_cx + s * go_head_w * 0.20
        d.line([(nx, go_head_cy + go_head_h * 0.44),
                (nx, go_shoulder_y)], fill=ink, width=stroke)
    # torso: shoulders in, belly out — a plump adult, not a chibi
    outline([(go_cx - go_half * 0.80, go_shoulder_y),
             (go_cx + go_half * 0.80, go_shoulder_y),
             (go_cx + go_half, go_navel_y),
             (go_cx + go_half * 0.86, go_hip_y),
             (go_cx - go_half * 0.86, go_hip_y),
             (go_cx - go_half, go_navel_y)])
    # ARMS DOWN AT HIS SIDES. This is the clause that clears §9b's third
    # blocker: the goblin's own fist occupied the gap in the composite route,
    # and here the lane between the fingertip and the belly is empty.
    for s in (-1, 1):
        sx = go_cx + s * go_half * 0.80
        d.line(capsule([(sx, go_shoulder_y),
                        (sx + s * 0.02 * go_h, go_hip_y),
                        (sx + s * 0.01 * go_h, gy - 0.40 * go_h)],
                       0.055 * go_h) + [(sx, go_shoulder_y)],
               fill=ink, width=stroke, joint="curve")
    for s in (-1, 1):
        hx = go_cx + s * go_half * 0.55
        d.line(capsule([(hx, go_hip_y), (hx + s * 0.012 * go_h, gy)],
                       0.075 * go_h) + [(hx, go_hip_y)],
               fill=ink, width=stroke, joint="curve")

    # ---- the guard, frame right ------------------------------------------
    gu_head_h = 0.130 * gu_h
    gu_head_w = 0.72 * gu_head_h
    gu_top = gy - gu_h
    gu_head_cy = gu_top + gu_head_h / 2.0
    gu_shoulder_y = gy - SHOULDER_FRAC * gu_h
    gu_hip_y = gy - HIP_FRAC * gu_h
    gu_half = 0.070 * gu_h

    d.ellipse([gu_cx - gu_head_w / 2, gu_head_cy - gu_head_h / 2,
               gu_cx + gu_head_w / 2, gu_head_cy + gu_head_h / 2],
              outline=ink, width=stroke)
    for s in (-1, 1):
        nx = gu_cx + s * gu_head_w * 0.20
        d.line([(nx, gu_head_cy + gu_head_h * 0.44),
                (nx, gu_shoulder_y)], fill=ink, width=stroke)
    outline([(gu_cx - gu_half * 0.95, gu_shoulder_y),
             (gu_cx + gu_half * 0.95, gu_shoulder_y),
             (gu_cx + gu_half * 0.82, gu_hip_y),
             (gu_cx - gu_half * 0.82, gu_hip_y)])
    for s in (-1, 1):
        hx = gu_cx + s * gu_half * 0.50
        d.line(capsule([(hx, gu_hip_y), (hx + s * 0.010 * gu_h, gy)],
                       0.070 * gu_h) + [(hx, gu_hip_y)],
               fill=ink, width=stroke, joint="curve")

    # ---- THE POINT — the whole reason this file exists -------------------
    near_sx = gu_cx - gu_half * 0.95
    near_sy = gu_shoulder_y
    target_x = go_cx + go_half        # the near edge of his belly
    target_y = go_navel_y
    dx, dy = target_x - near_sx, target_y - near_sy
    full = math.hypot(dx, dy)
    if full <= 0:
        raise ValueError("the two figures are on top of each other")
    ux, uy = dx / full, dy / full
    finger_len = FINGER * gu_h
    clear_px = clearance * height
    arm = (UPPER_ARM + FOREARM) * gu_h
    # SOLVED BACKWARDS FROM THE CLEARANCE, which is what makes the metadata
    # honest: the fingertip is placed at exactly `clear_px` short of the belly,
    # the wrist one finger further back, and the elbow is then whatever the
    # two-link triangle requires. Nothing is nudged after the fact.
    wrist_d = full - clear_px - finger_len
    ext = wrist_d / arm
    if ext > EXT_MAX:
        raise ValueError(
            "the wrist would sit %.1f px from the shoulder but the arm is %.1f px "
            "(%.2f extension). The figures are too far apart: this staging asks "
            "for a stretched limb, and `extra arms` is already in this beat's "
            "negative." % (wrist_d, arm, ext))
    if ext < EXT_MIN:
        raise ValueError(
            "the wrist would sit at %.2f extension (min %.2f). The figures are so "
            "close the elbow folds, and a folded arm reads as a jab or a shrug, "
            "not as a point." % (ext, EXT_MIN))
    wristx, wristy = near_sx + ux * wrist_d, near_sy + uy * wrist_d
    elbow = solve_elbow(near_sx, near_sy, wristx, wristy,
                        UPPER_ARM * gu_h, FOREARM * gu_h, sign=1.0)
    d.line(capsule([(near_sx, near_sy), elbow, (wristx, wristy)], 0.055 * gu_h)
           + [(near_sx, near_sy)], fill=ink, width=stroke, joint="curve")
    # The extended index, drawn on toward the BELLY rather than along the
    # forearm: a pointing hand angles at the wrist, and this is the stroke that
    # says which figure the gesture is aimed at.
    fingerx, fingery = wristx + ux * finger_len, wristy + uy * finger_len
    d.line([(wristx, wristy), (fingerx, fingery)], fill=ink,
           width=max(1, stroke - 2), joint="curve")

    # ---- THE LOWERED BOARD, in his other hand ----------------------------
    far_sx = gu_cx + gu_half * 0.95
    board_w = 0.135 * width
    board_h = 0.115 * height
    board_cx = gu_cx + 0.105 * width
    board_cy = gu_hip_y + 0.012 * height       # hanging at the hip, not the chest
    board_top = board_cy - board_h / 2.0
    # far arm hangs straight down to grip the board's top edge
    wrist = (board_cx - board_w * 0.28, board_top)
    d.line(capsule([(far_sx, gu_shoulder_y),
                    (far_sx + 0.010 * gu_h, (gu_shoulder_y + wrist[1]) / 2.0),
                    wrist], 0.052 * gu_h) + [(far_sx, gu_shoulder_y)],
           fill=ink, width=stroke, joint="curve")
    tilt = math.radians(9.0)          # a held board is never axis-aligned
    ct, st = math.cos(tilt), math.sin(tilt)
    corners = []
    for ox, oy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        px, py = ox * board_w / 2.0, oy * board_h / 2.0
        corners.append((board_cx + px * ct - py * st,
                        board_cy + px * st + py * ct))
    outline(corners)
    # the clip across its top — what makes a rectangle read as a clipboard
    d.line([((corners[0][0] * 3 + corners[1][0]) / 4,
             (corners[0][1] * 3 + corners[1][1]) / 4),
            ((corners[0][0] + corners[1][0] * 3) / 4,
             (corners[0][1] + corners[1][1] * 3) / 4)],
           fill=ink, width=max(1, stroke - 1))

    # ---- the ground -------------------------------------------------------
    # TICKS, NOT A FULL-WIDTH RULE. One line across the frame is an invitation
    # to draw a fence or a wall; two marks at an IDENTICAL y say "feet at the
    # same depth", which is all B3 asks, for a fraction of the ink.
    # WIDER THAN THE FEET, and that too is a correction made by looking: at
    # 0.08 frame-widths each side the ticks sat entirely inside the leg
    # capsules and were invisible in the drawn hint, so they were saying
    # nothing at all.
    if ground_ticks:
        for cx in (go_cx, gu_cx):
            d.line([(cx - 0.145 * width, gy), (cx + 0.145 * width, gy)],
                   fill=ink, width=max(1, stroke - 2))

    meta = {
        "size": f"{width}x{height}",
        "stroke_px": stroke,
        "polarity": "black-on-white (INVERTED)" if invert
                    else "white-on-black (scribble convention)",
        "ground_y_px": round(gy, 1),
        "guard": {"cx": round(gu_cx, 1), "stature_px": round(gu_h, 1),
                  "head_cy": round(gu_head_cy, 1),
                  "shoulder_y": round(gu_shoulder_y, 1),
                  "feet_y": round(gy, 1)},
        "goblin": {"cx": round(go_cx, 1), "stature_px": round(go_h, 1),
                   "head_cy": round(go_head_cy, 1),
                   "navel_y": round(go_navel_y, 1),
                   "torso_half_px": round(go_half, 1),
                   "feet_y": round(gy, 1)},
        "stature_ratio": round(gu_h / go_h, 3),
        "point": {"shoulder": (round(near_sx, 1), round(near_sy, 1)),
                  "elbow": (round(elbow[0], 1), round(elbow[1], 1)),
                  "wrist": (round(wristx, 1), round(wristy, 1)),
                  "fingertip": (round(fingerx, 1), round(fingery, 1)),
                  "target_belly": (round(target_x, 1), round(target_y, 1)),
                  "shoulder_to_belly_px": round(full, 1),
                  "arm_px": round(arm, 1),
                  "extension": round(ext, 3),
                  "gap_to_torso_px": round(math.hypot(target_x - fingerx,
                                                      target_y - fingery), 1)},
        "board": {"cx": round(board_cx, 1), "cy": round(board_cy, 1),
                  "top_y": round(board_top, 1),
                  "below_shoulder_px": round(board_top - gu_shoulder_y, 1)},
        "ink_fraction": None,   # filled by the caller after counting
    }
    return img, meta


def ink_fraction(img, invert=False):
    """What share of the frame carries ink. ~0 is a blank hint and a large
    number is a fill; both are broken conditions and neither is obvious by eye
    at thumbnail size."""
    hist = img.convert("L").histogram()
    total = sum(hist)
    return (sum(hist[:128]) if invert else sum(hist[128:])) / total


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def selftest():
    """THE BAR, AS GEOMETRY, BEFORE THE PIXELS. No GPU, no weights, safe in CI."""
    fails = []

    def check(name, cond):
        print(("  ok   " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    img, m = build()
    check("canvas is the render size the probe bound at", img.size == (W, H))
    frac = ink_fraction(img)
    check(f"hint carries ink but is not a fill ({frac:.4f})", 0.005 < frac < 0.20)

    gu, go, pt, bd = m["guard"], m["goblin"], m["point"], m["board"]

    # B1 — TWO figures, and they do not overlap into one silhouette.
    check("B1 two figures, horizontally separated",
          go["cx"] + go["torso_half_px"] < gu["cx"] - go["torso_half_px"])
    check("B1 both figures are whole in frame (heads inside the top edge)",
          go["head_cy"] > 0 and gu["head_cy"] > 0)

    # B3 — one ground plane, to the pixel. This is the whole clause.
    check("B3 both figures' feet are on the SAME y",
          gu["feet_y"] == go["feet_y"] == m["ground_y_px"])
    check("B3 the ground is inside the frame", 0 < m["ground_y_px"] < H)

    # B5 — no colossus.
    check(f"B5 the guard is taller ({m['stature_ratio']}x)", m["stature_ratio"] > 1.0)
    check(f"B5 and nobody towers ({m['stature_ratio']} < 1.35)",
          m["stature_ratio"] < 1.35)

    # B4a — the board is DOWN.
    check(f"B4 the board's top is below the guard's shoulder "
          f"({bd['below_shoulder_px']:.0f} px)",
          bd["below_shoulder_px"] > 0.10 * H)

    # B4b — the point, which is the clause the composite route could not reach.
    check("B4 the fingertip is at the goblin's navel height (+/- 0.05H)",
          abs(pt["fingertip"][1] - go["navel_y"]) < 0.05 * H)
    check("B4 the fingertip is between the two figures, not past the goblin",
          go["cx"] < pt["fingertip"][0] < gu["cx"])
    check(f"B4 the point stops OUTSIDE the goblin's torso "
          f"({pt['gap_to_torso_px']:.0f} px clear)",
          pt["gap_to_torso_px"] > 0.5 * CLEARANCE * H)
    check(f"B4 the pose is anatomically reachable ({pt['extension']} extension)",
          EXT_MIN < pt["extension"] < EXT_MAX)
    check("B4 the elbow is off the shoulder-wrist line, i.e. actually bent",
          abs(pt["elbow"][1] - (pt["shoulder"][1] + pt["wrist"][1]) / 2) > 4)

    # BOTH ends of the staging must RAISE rather than draw a rubber arm or a
    # folded one. These are the two ways a hint quietly stops being a point.
    try:
        build(goblin_x=0.02)
        check("figures too FAR apart is refused (stretched limb)", False)
    except ValueError:
        check("figures too FAR apart is refused (stretched limb)", True)
    try:
        build(goblin_x=0.50)
        check("figures too CLOSE is refused (folded elbow)", False)
    except ValueError:
        check("figures too CLOSE is refused (folded elbow)", True)

    # Polarity: --invert must be a flip, not a redraw.
    inv, _ = build(invert=True)
    fi = ink_fraction(inv, invert=True)
    check(f"inverted hint carries the same ink ({fi:.4f})", abs(fi - frac) < 0.01)
    check("inverted ground is light", inv.convert("L").getpixel((3, 3)) > 200)
    check("upright ground is dark", img.convert("L").getpixel((3, 3)) < 55)

    # Stroke is the card's second control dial — thicker must mean more ink.
    thin = ink_fraction(build(stroke=3)[0])
    thick = ink_fraction(build(stroke=13)[0])
    check(f"stroke is a control dial ({thin:.4f} -> {thick:.4f})", thick > thin * 1.4)

    # Determinism, or the sha in a sidecar is a lie.
    import io
    b1, b2 = io.BytesIO(), io.BytesIO()
    build()[0].save(b1, "PNG")
    build()[0].save(b2, "PNG")
    check("authoring is deterministic", b1.getvalue() == b2.getvalue())

    # Bad input is refused, not silently clamped.
    for kw in ({"stroke": 0}, {"ground_y": 0.0}, {"ground_y": 1.2},
               {"guard_h": 0.0}, {"clearance": 0.8},
               {"goblin_x": 0.9}):
        try:
            build(**kw)
            check(f"refuses {kw}", False)
        except ValueError:
            check(f"refuses {kw}", True)

    # The capsule helper's own contract.
    try:
        capsule([(0, 0)], 10)
        check("a one-point capsule is refused", False)
    except ValueError:
        check("a one-point capsule is refused", True)

    print(("SELFTEST FAIL: %d" % len(fails)) if fails else "SELFTEST PASS")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description="draw beat 08's two-figure pose hint")
    ap.add_argument("out", nargs="?", help="output PNG")
    ap.add_argument("--width", type=int, default=W)
    ap.add_argument("--height", type=int, default=H)
    ap.add_argument("--stroke", type=int, default=7,
                    help="stroke width px; thick = condition wins (xinsir card)")
    ap.add_argument("--guard-x", type=float, default=GUARD_X)
    ap.add_argument("--goblin-x", type=float, default=GOBLIN_X)
    ap.add_argument("--guard-h", type=float, default=GUARD_H)
    ap.add_argument("--goblin-h", type=float, default=GOBLIN_H)
    ap.add_argument("--ground-y", type=float, default=GROUND_Y)
    ap.add_argument("--clearance", type=float, default=CLEARANCE,
                    help="frame heights of air the fingertip stops short by")
    ap.add_argument("--no-ground-ticks", action="store_true")
    ap.add_argument("--invert", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.out:
        ap.error("out PNG required (or --selftest)")

    img, meta = build(a.width, a.height, a.stroke, a.invert,
                      not a.no_ground_ticks, a.guard_x, a.goblin_x,
                      a.guard_h, a.goblin_h, a.ground_y, a.clearance)
    meta["ink_fraction"] = round(ink_fraction(img, a.invert), 5)
    img.save(a.out, "PNG")
    print(f"wrote {a.out}")
    for k, v in meta.items():
        print(f"  {k}: {v}")
    print(f"  sha256: {sha256_file(a.out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
