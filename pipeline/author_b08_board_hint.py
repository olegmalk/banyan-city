#!/usr/bin/env python3
"""Beat 08's BOARD-ONLY scribble hint: one clipboard, and not one figure pixel.

WHY THIS FILE EXISTS, IN ONE PARAGRAPH. `ep2-b08-twinsipa-0819` passed every
pre-registered clause on beat 08 except one: B4a, the lowered clipboard. It was
pre-registered to fail, for a reason that is structural rather than fixable by
tuning -- NO OBJECT IS IN A POSE HINT. COCO-18 has eighteen keypoints and all
eighteen are body parts, so the openpose net cannot be told about a board at
any conditioning scale. The remedy the twinsipa verdict named is
multi-ControlNet: the SAME openpose skeleton that passed, byte-identical, PLUS
a second net reading a second hint that carries the board and nothing else.

WHY THE SECOND HINT MUST BE BOARD-ONLY, AND WHY THAT IS NOT CAUTION BUT THE
WHOLE DESIGN. The scribble net lost the figure-tracing question five times on
this beat (route log §8-§10: conditioning scale, stroke weight and hint class
were each bracketed and every frame came back traced or wrong). What the
scribble net reads reliably is ENCLOSURE -- a closed contour says "an edge goes
here" -- and that is a catastrophe around a body, where it produces a traced
outline instead of a drawn character, and exactly right around a rectangular
board, which IS an edge. `author_b08_pose_hint` already states this in the one
place it kept a rectangle:

    # The BOARD keeps its rectangle on purpose: it is an object we want traced,
    # not a body we want redrawn, and B4a has passed on it four times.

So this hint draws the four-corner quad and its clip, and stops. If a single
figure contour leaks into it, the second net re-opens a question that five
rungs closed, and the pass this rung is built on is spent. `--selftest`
asserts the absence AS PIXELS: every lit pixel must fall inside the board quad
dilated by the stroke, and not one may fall inside either figure's capsule mask
(the guard's gripping forearm excepted -- see below).

THE GEOMETRY IS NOT RE-AUTHORED, IT IS THE ONE ALREADY ON THE RECORD.
`author_b08_pose_hint.build` places the board at 0.135w x 0.115h, centred
(0.105w, +0.012h) off the guard's hip, tilted 9 degrees, gripped at 0.28 of its
width in from the left of its top edge. `author_b08_openpose_hint.stage` then
puts the guard's LEFT WRIST at exactly that grip point so the arm that holds it
goes somewhere sensible. Those two descriptions of one board have lived in two
files since the pose hint was written, and two descriptions drift. This module
states the constants once and `--selftest` PINS THEM TO THE SKELETON: the grip
this file computes must equal `stage()`'s guard `Lwri` to the float. If anyone
re-stages the guard, that check fails rather than the board quietly sliding off
his hand.

THE GRIPPING FOREARM IS THE ONE PLACE FIGURE AND BOARD LEGITIMATELY MEET, and
it is carved out explicitly rather than fudged: the board's top edge passes
about 5.8 px from the authored wrist, which is inside that limb's r=12 capsule.
That is a hand holding a board, which is the picture. Every OTHER capsule on
the guard, and every capsule on the goblin, must be untouched, and that is what
is asserted.

WHAT THIS FILE DOES NOT TOUCH. The openpose hint is not modified, not
re-authored and not re-saved; `--selftest` re-derives it in memory and asserts
its sha is still 562911c8..., the byte-identical hint the passing job used. The
IP-Adapter capsule masks are not modified either -- board ink lives in a CONTROL
image, masks live in argv, and they do not interact.

THE GRIP LOOP (`--grip`, added 2026-08-20, OFF BY DEFAULT). One closed,
hand-sized loop centred on the authored L-wrist and straddling the board's top
edge -- the FIRST figure ink ever placed in this hint. It is authorised by the
written argument in `pipeline/work-ladder-0819.md` ("the grip mark, argued
against the five tracing losses"), and three of that argument's load-bearing
claims are asserted here AS PIXELS rather than as prose:

  * ENCLOSURE, not a stroke. The mark is a closed polygon and `--selftest`
    proves it the way route-log section 10 proved the contour/skeleton
    distinction -- a flood fill seeded at its centre, off-ink, must be TRAPPED.
    The named proposal three rungs kept repeating was "a short stroke", which is
    tracing loss 4 exactly (r4's 1 px finger, which did not carry); a stroke is
    refused here and a closed loop is what gets drawn.
  * NO NEW LIMB. The loop lives inside the SAME three-limb carve-out the board
    already occupies -- {gripping forearm, torso, L thigh} -- and the limb-set
    assertion below is run against the grip hint too, unchanged. The nearest
    limb it does NOT already touch is 81.6 px away and its own reach is 36.3 px.
  * ONE VARIABLE, PROVABLY. `build()` keeps its old default, so the parent's
    filed hint stays byte-identical at 38cd39da...; `--selftest` re-derives it
    in memory and checks that sha, and separately checks that the grip hint is a
    strict SUPERSET of it. The two hints therefore differ by the loop and by
    nothing else, as a measurement rather than an intention.

    python3 pipeline/author_b08_board_hint.py --selftest        # no GPU, no net
    python3 pipeline/author_b08_board_hint.py pipeline/control/b08-board-0820.png
    python3 pipeline/author_b08_board_hint.py --grip \
        pipeline/control/b08-board-grip-0820.png
"""
import argparse
import hashlib
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from author_b08_pose_hint import (  # noqa: E402  -- the staging is shared, on purpose
    GROUND_Y, GUARD_H, GUARD_X, H, HIP_FRAC, W,
)

# ---------------------------------------------------------------------------
# THE BOARD, STATED ONCE. Every one of these numbers is transcribed from
# `author_b08_pose_hint.build`'s board block -- they are not new choices, and
# `--selftest` pins the grip they imply to the openpose skeleton's wrist so a
# transcription error cannot survive.
# ---------------------------------------------------------------------------
BOARD_W_FRAC = 0.135      # of frame width
BOARD_H_FRAC = 0.115      # of frame height
BOARD_CX_OFF = 0.105      # frame widths right of the guard's centre line
BOARD_CY_OFF = 0.012      # frame heights below his hip -- at the hip, not the chest
TILT_DEG = 9.0            # a held board is never axis-aligned
GRIP_FRAC = 0.28          # in from the left end of the top edge
STROKE = 7                # author_b08_pose_hint's default, and the weight the
                          # four passing B4a frames were conditioned at.
                          # ALSO THE WEIGHT THE GRIP LOOP IS DRAWN AT, and that
                          # is the argument's choice rather than convenience:
                          # route-log section 9 measured stroke as a PRECISION
                          # dial, not a strength dial. 3 px is a single
                          # unambiguous edge locus and the outline snaps to it
                          # (r4's fingerless wedge); 7 px is an ambiguous ribbon
                          # the model fills with its own drawing, which is why
                          # r2 -- the one positive in the five losses -- came
                          # back with an articulated hand at an enclosed arm
                          # terminus. Do not thin this to "be gentler".
CLIP_INSET = 0.25         # the clip spans the middle half of the top edge

# ---------------------------------------------------------------------------
# THE GRIP LOOP. Sized as a fraction of the guard's STATURE, like every other
# number in this staging, so it cannot drift out of scale if he is re-staged.
# 0.065 x 0.050 of stature is 52.2 x 40.1 px at the filed staging -- a closed
# fist, measured against the one this frame already draws (the render's fist on
# the harness strap spans roughly 50 x 55 px at 8x).
#
# THE SHAPE IS DELIBERATELY DUMB, AND THAT IS THE r2 LESSON. r2's hand was good
# and "aimed wide BY CONSTRUCTION" -- hand-authored geometry fails by being
# confidently wrong, so this asserts the least it can: a symmetric rounded form
# at the arm's terminus, tilted with the board, with NO knuckles, NO thumb and
# NO finger divisions authored. Digits are the model's job and the parent frame
# proves it still does that job at 0.3 (its B6 verdict reads "a well-drawn fist
# gripping the harness strap with individual fingers").
# ---------------------------------------------------------------------------
GRIP_W_STATURE = 0.065    # fist width, along the board's top edge
GRIP_H_STATURE = 0.050    # fist depth, across it
GRIP_CORNER = 0.55        # octagon corner cut -- a rounded rect, not a box


def board_geometry(width=W, height=H, guard_x=GUARD_X, guard_h=GUARD_H,
                   ground_y=GROUND_Y):
    """The quad, its clip and its grip point, in RENDER pixels.

    Same units as the hint and the capsule masks, and for the same reason: two
    coordinate systems is how a 4% disagreement goes unnoticed.
    """
    if not 0.0 < ground_y < 1.0:
        raise ValueError("ground_y must be in (0,1), got %r" % (ground_y,))
    if not 0.0 < guard_h < 1.0:
        raise ValueError("stature fraction must be in (0,1), got %r" % (guard_h,))
    if not 0.0 < guard_x < 1.0:
        raise ValueError("guard_x must be in (0,1), got %r" % (guard_x,))

    gy = ground_y * height
    gu_h = guard_h * height
    gu_cx = guard_x * width
    gu_hip_y = gy - HIP_FRAC * gu_h

    bw = BOARD_W_FRAC * width
    bh = BOARD_H_FRAC * height
    bcx = gu_cx + BOARD_CX_OFF * width
    bcy = gu_hip_y + BOARD_CY_OFF * height
    btop = bcy - bh / 2.0

    ct, st = math.cos(math.radians(TILT_DEG)), math.sin(math.radians(TILT_DEG))
    corners = []
    for ox, oy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        px, py = ox * bw / 2.0, oy * bh / 2.0
        corners.append((bcx + px * ct - py * st, bcy + px * st + py * ct))

    # The clip across the top edge. AND A HONEST NOTE, BECAUSE THE ORIGINAL'S
    # COMMENT OVERSTATES IT: these two points are COLLINEAR WITH THE TOP EDGE,
    # so the clip is drawn directly on top of an edge that is already there and
    # adds no distinct mark -- it thickens the middle half of the top edge and
    # nothing more. `author_b08_pose_hint` computes it the same way and calls it
    # "what makes a rectangle read as a clipboard", which it cannot be doing.
    # It is reproduced UNCHANGED anyway: this geometry is the one B4a passed on
    # four times, and a rung whose variable is "a second net" does not get to
    # also change the shape being conditioned. Offsetting the clip below the top
    # edge so it actually reads is a candidate for a LATER rung, on its own.
    c0, c1 = corners[0], corners[1]
    clip = [(c0[0] + (c1[0] - c0[0]) * CLIP_INSET,
             c0[1] + (c1[1] - c0[1]) * CLIP_INSET),
            (c0[0] + (c1[0] - c0[0]) * (1.0 - CLIP_INSET),
             c0[1] + (c1[1] - c0[1]) * (1.0 - CLIP_INSET))]

    # THE GRIP. Computed exactly as author_b08_pose_hint computes it, and
    # asserted equal to stage()'s guard Lwri.
    grip = (bcx - bw * GRIP_FRAC, btop)

    if btop < 0 or bcy + bh / 2.0 > height:
        raise ValueError("the board falls outside the %dx%d frame" % (width, height))

    # THE GRIP LOOP, centred on that same point. Rotated by the board's own
    # tilt so its long axis lies ALONG the top edge -- a fist wrapping an edge
    # is wider across the edge than along the forearm -- and straddling the
    # edge, half above and half below, which is the occlusion the beat asks for
    # ("in one hand", not "under a sleeve").
    ga, gb = GRIP_W_STATURE * gu_h / 2.0, GRIP_H_STATURE * gu_h / 2.0
    c = GRIP_CORNER
    grip_poly = []
    for ox, oy in ((-1.0, -c), (-c, -1.0), (c, -1.0), (1.0, -c),
                   (1.0, c), (c, 1.0), (-c, 1.0), (-1.0, c)):
        px, py = ox * ga, oy * gb
        grip_poly.append((grip[0] + px * ct - py * st,
                          grip[1] + px * st + py * ct))

    return {"cx": bcx, "cy": bcy, "w": bw, "h": bh, "top_y": btop,
            "corners": corners, "clip": clip, "grip": grip,
            "grip_poly": grip_poly, "grip_w": 2.0 * ga, "grip_h": 2.0 * gb,
            "guard_cx": gu_cx, "guard_hip_y": gu_hip_y,
            "guard_stature_px": gu_h, "ground_y_px": gy}


def build(width=W, height=H, stroke=STROKE, guard_x=GUARD_X, guard_h=GUARD_H,
          ground_y=GROUND_Y, grip=False):
    """The board hint. Returns (PIL RGB image, metadata dict).

    White on black -- the scribble convention, and the polarity the driver
    records as `control_polarity: white-on-black`.

    `grip=False` (THE DEFAULT, AND IT MUST STAY THE DEFAULT) draws the quad and
    its clip and NOTHING else -- byte-identical to the hint every rung from
    ep2-b08-boardnet-0820 to ep2-b08-scale50-0820 was conditioned on, sha
    38cd39da..., which `--selftest` re-derives and checks. `grip=True` adds ONE
    closed loop at the authored L-wrist and changes nothing else, so the two
    hints differ by exactly that loop.
    """
    from PIL import Image, ImageDraw

    if stroke < 1:
        raise ValueError("stroke must be >= 1, got %r" % (stroke,))
    g = board_geometry(width, height, guard_x, guard_h, ground_y)

    img = Image.new("RGB", (width, height), (0, 0, 0))
    d = ImageDraw.Draw(img)
    ink = (255, 255, 255)
    poly = g["corners"]
    d.line(list(poly) + [poly[0]], fill=ink, width=stroke, joint="curve")
    d.line(g["clip"], fill=ink, width=max(1, stroke - 1))

    meta = {
        "size": "%dx%d" % (width, height),
        "hint_class": "single closed quad (ONE OBJECT, no figure of any kind)",
        "stroke_px": stroke,
        "polarity": "white-on-black (scribble convention)",
        "board": {"cx": round(g["cx"], 1), "cy": round(g["cy"], 1),
                  "w": round(g["w"], 1), "h": round(g["h"], 1),
                  "top_y": round(g["top_y"], 1),
                  "tilt_deg": TILT_DEG,
                  "corners": [tuple(round(v, 1) for v in c) for c in poly],
                  "grip": tuple(round(v, 4) for v in g["grip"])},
        "figures_drawn": 0,
        "figure_pixels": 0,
        "ink_fraction": None,
    }

    if grip:
        gp = g["grip_poly"]
        # SAME stroke as the board, and drawn CLOSED -- the last vertex is
        # repeated. An unclosed polyline here would be a stroke, which is the
        # class that has already lost once (r4's 1 px finger).
        d.line(list(gp) + [gp[0]], fill=ink, width=stroke, joint="curve")
        meta["hint_class"] = ("closed quad (the board) PLUS one closed "
                              "hand-sized loop at the authored L-wrist -- "
                              "enclosure class, not a stroke")
        meta["figures_drawn"] = 0   # still no figure: one body part's contact
        meta["grip_loop"] = {
            "centre": tuple(round(v, 4) for v in g["grip"]),
            "w": round(g["grip_w"], 1), "h": round(g["grip_h"], 1),
            "tilt_deg": TILT_DEG,
            "vertices": [tuple(round(v, 1) for v in p) for p in gp],
            "class": "closed loop (flood-fill-trapped); NOT an open stroke",
            "argued_in": "pipeline/work-ladder-0819.md -- the grip mark, "
                         "argued against the five tracing losses",
        }
    return img, meta


def ink_mask(img):
    """The lit pixels, as an L mask. A scribble hint is white on black."""
    return img.convert("L").point(lambda v: 255 if v >= 128 else 0)


def ink_fraction(img):
    hist = img.convert("L").histogram()
    return sum(hist[128:]) / float(sum(hist))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# The hint the passing job was conditioned on. Re-derived in memory by
# --selftest and compared, so this module can never be the reason that sha moves.
OPENPOSE_HINT = "pipeline/control/b08-openpose-nat-0819.png"
OPENPOSE_SHA = "562911c8174a6ecc21bc8710a1ac1b7f965c3f2d865093a742c2598c37d952e0"

# The BOARD-ONLY hint, as conditioned by every rung from ep2-b08-boardnet-0820
# through ep2-b08-scale50-0820. Adding the grip loop must not move it: this is
# the assertion that keeps "one variable" a measurement instead of a promise.
BOARD_HINT = "pipeline/control/b08-board-0820.png"
BOARD_SHA = "38cd39da304dbb0317aa2522e1ccca099bef583e88e6573fde03b287358213d6"


def selftest():
    """THE BAR, BEFORE ANY PIXELS. No GPU, no weights, no network."""
    import importlib
    import io

    from PIL import Image, ImageChops, ImageDraw

    fails = []

    def check(label, ok):
        print("  %s %s" % ("ok  " if ok else "FAIL", label))
        if not ok:
            fails.append(label)

    img, m = build()
    g = board_geometry()
    ink = ink_mask(img)

    # ---- SIZE AND POLARITY, which the driver refuses on ------------------
    check("the hint is authored at the render size 832x1216 (controlnet_plate's "
          "rc=7 guard resizes nothing)", img.size == (W, H))
    check("the canvas ground is black", img.getpixel((3, 3)) == (0, 0, 0))
    lit_colours = {img.getpixel((x, y))
                   for x in range(0, W, 3) for y in range(0, H, 3)
                   if sum(img.getpixel((x, y))) > 0}
    check("every lit pixel is pure white -- a scribble hint is monochrome, and "
          "a colour here would be read as an openpose limb (%r)" % (lit_colours,),
          lit_colours in ({(255, 255, 255)}, set()))

    # ---- THE DRIFT GUARD: the board is pinned to the skeleton ------------
    # This is the check that makes two files safe to hold one board between
    # them. Re-stage the guard and this fails; it does not slide.
    oph = importlib.import_module("author_b08_openpose_hint")
    gk, bk, _sm = oph.stage()
    check("THE BOARD'S GRIP IS THE OPENPOSE SKELETON'S GUARD L-WRIST, TO THE "
          "FLOAT (%r vs %r)" % (g["grip"], gk["Lwri"]),
          g["grip"] == gk["Lwri"])

    # ---- and the openpose hint itself is untouched by this module --------
    op_img, _op_meta = oph.build(point_style=oph.POINT_NATURAL)
    buf = io.BytesIO()
    op_img.save(buf, "PNG")
    check("re-deriving the openpose hint still gives the byte-identical PNG the "
          "passing job used (sha 562911c8...)",
          hashlib.sha256(buf.getvalue()).hexdigest() == OPENPOSE_SHA)
    filed = Path(__file__).resolve().parent.parent / OPENPOSE_HINT
    if filed.exists():
        check("and the FILED hint on disk still carries that sha",
              sha256_file(filed) == OPENPOSE_SHA)
    check("the board hint is NOT the openpose hint (two nets, two conditions)",
          img.tobytes() != op_img.tobytes())

    # ---- AND THE DEFAULT BOARD HINT HAS NOT MOVED ------------------------
    # The grip loop is opt-in for exactly this reason. Four rungs were
    # conditioned on 38cd39da...; if adding a flag changed the default, the
    # grip rung would silently be a TWO-variable job.
    dbuf = io.BytesIO()
    img.save(dbuf, "PNG")
    default_sha = hashlib.sha256(dbuf.getvalue()).hexdigest()
    check("the DEFAULT hint (grip=False) is still byte-identical to the one "
          "four rungs rendered from, sha 38cd39da... (got %s...)"
          % default_sha[:8], default_sha == BOARD_SHA)
    dfiled = Path(__file__).resolve().parent.parent / BOARD_HINT
    if dfiled.exists():
        check("and the FILED board hint on disk still carries that sha",
              sha256_file(dfiled) == BOARD_SHA)

    # ---- ZERO FIGURE PIXELS, ASSERTED AS PIXELS --------------------------
    # (a) POSITIVE CONTAINMENT: everything lit is inside the board quad grown
    # by the stroke. Nothing else was drawn, and this is the statement of that
    # fact which a future edit cannot talk its way past.
    # Built with the driver's own `capsule_mask` rather than a wide PIL line.
    # That is not a style preference: PIL gives a polyline BUTT ends, so the
    # seam where a closed quad meets itself leaves a notch, and a first version
    # of this check failed on exactly ONE pixel at corner 0 for that reason --
    # a rasterisation artifact of the CHECK reported as a defect in the HINT.
    # `capsule_mask` puts an explicit disc at both ends of every segment, which
    # is a true Minkowski dilation and has no seam.
    cp = importlib.import_module("controlnet_plate")
    poly = g["corners"]
    pad = STROKE  # half-stroke either side, plus rasterisation slop
    edges = [(poly[i][0], poly[i][1], poly[(i + 1) % 4][0], poly[(i + 1) % 4][1],
              pad) for i in range(4)]
    edges.append((g["clip"][0][0], g["clip"][0][1],
                  g["clip"][1][0], g["clip"][1][1], pad))
    allowed = cp.capsule_mask(edges, W, H)
    outside = ImageChops.subtract(ink, allowed)
    check("EVERY LIT PIXEL IS INSIDE THE BOARD QUAD DILATED BY THE STROKE -- "
          "there is no second mark anywhere in this hint",
          outside.getbbox() is None)

    bb = ink.getbbox()
    xs = [c[0] for c in poly] + [p[0] for p in g["clip"]]
    ys = [c[1] for c in poly] + [p[1] for p in g["clip"]]
    check("the inked bounding box %r is the board's own box grown by the stroke, "
          "and covers under 3%% of the frame" % (bb,),
          bb is not None
          and bb[0] >= min(xs) - STROKE and bb[1] >= min(ys) - STROKE
          and bb[2] <= max(xs) + STROKE + 1 and bb[3] <= max(ys) + STROKE + 1
          and (bb[2] - bb[0]) * (bb[3] - bb[1]) < 0.03 * W * H)

    # (b) NEGATIVE, AGAINST THE FIGURES THEMSELVES. The capsule masks are the
    # drawn skeleton dilated, so "no board ink inside a capsule" is literally
    # "this hint does not trace that limb". The guard's gripping arm is the one
    # carve-out and it is named, not fudged: a hand on a board is the picture.
    goblin_mask = cp.capsule_mask(oph.figure_capsules(bk), W, H)
    check("NOT ONE LIT PIXEL FALLS ON THE GOBLIN -- the second net is never "
          "shown his body at all",
          ImageChops.multiply(ink, goblin_mask).getbbox() is None)

    # THE EXACT SET, NOT A LOOSE "SOME OVERLAP IS FINE". A clipboard held at the
    # hip PHYSICALLY covers the body behind it, so a board hint that touched no
    # limb at all would be a board floating in space. What matters is WHICH
    # limbs, and the honest way to say that is to enumerate them: the holding
    # forearm, the torso it hangs against, and the thigh it hangs over. Any
    # other limb -- his face, his pointing arm, his shins -- means this hint has
    # started describing a BODY, and the set comparison fails the moment it
    # does. A first version of this check asserted "no limb but the grip" and
    # failed on the torso and thigh; the hint was right and the assertion was
    # wrong, so the assertion was corrected rather than the tolerance widened.
    LIMB_NAME = {(1, 2): "neck-Rsho", (1, 5): "neck-Lsho",
                 (2, 3): "POINTING upper arm", (3, 4): "POINTING forearm",
                 (5, 6): "gripping upper arm", (6, 7): "gripping forearm",
                 (1, 8): "neck-Rhip", (8, 9): "R thigh", (9, 10): "R shin",
                 (1, 11): "torso (neck-Lhip)", (11, 12): "L thigh",
                 (12, 13): "L shin", (1, 0): "neck-nose", (0, 14): "nose-Reye",
                 (14, 16): "Reye-Rear", (0, 15): "nose-Leye",
                 (15, 17): "Leye-Lear"}
    EXPECTED_OVERLAP = {"gripping forearm", "torso (neck-Lhip)", "L thigh"}

    def limbs_hit(mask):
        """Which of the guard's capsules this ink lands in. Used TWICE now --
        once for the board-only hint and once for the grip hint -- because the
        grip loop's whole claim is that it adds no NEW limb to this set."""
        got = set()
        for i, j in oph.LIMBS:
            a, b = gk.get(oph.KP[i]), gk.get(oph.KP[j])
            if a is None or b is None:
                continue
            if (i, j) in oph.HEAD_LIMBS:
                r = oph.R_HEAD
            elif (i, j) in oph.TORSO_LIMBS:
                r = oph.R_TORSO
            else:
                r = oph.R_ARM
            one = cp.capsule_mask([(a[0], a[1], b[0], b[1], r)], W, H)
            if ImageChops.multiply(mask, one).getbbox() is not None:
                got.add(LIMB_NAME[(i, j)])
        return got

    hit = limbs_hit(ink)
    print("     the board's ink meets exactly these limbs: %s"
          % ", ".join(sorted(hit)))
    check("THE BOARD MEETS EXACTLY THE THREE LIMBS A HELD CLIPBOARD OCCLUDES -- "
          "the gripping forearm, the torso and the left thigh -- AND NO OTHER "
          "(got %s)" % (sorted(hit),), hit == EXPECTED_OVERLAP)
    # Named sets, not substring matching. The first version of these two lines
    # tested `"ear" in name` and tripped on "for-EAR-m": the gripping forearm
    # was reported as a head limb. A check that can be fooled by spelling is not
    # a check.
    HEAD_NAMES = {LIMB_NAME[k] for k in oph.HEAD_LIMBS}
    POINT_NAMES = {LIMB_NAME[(2, 3)], LIMB_NAME[(3, 4)]}
    check("in particular the guard's FACE is untouched -- a traced face is the "
          "scribble net's signature failure on this beat",
          not (hit & HEAD_NAMES))
    check("and the POINTING ARM is untouched -- the clause the parent bought is "
          "not re-opened by the second net", not (hit & POINT_NAMES))

    # (c) THE ARITHMETIC OF (b), so the numbers are on the record and not just
    # a boolean: how far the top edge passes from the authored wrist.
    c0, c1 = poly[0], poly[1]
    ex, ey = c1[0] - c0[0], c1[1] - c0[1]
    elen = math.hypot(ex, ey)
    wx, wy = gk["Lwri"][0] - c0[0], gk["Lwri"][1] - c0[1]
    perp = abs(wx * ey - wy * ex) / elen
    print("     top edge passes %.1f px from the authored wrist "
          "(the gripping capsule's radius is %g)" % (perp, oph.R_ARM))
    check("the authored wrist sits within the gripping capsule of the board's "
          "top edge (%.1f px <= %g)" % (perp, oph.R_ARM), perp <= oph.R_ARM)

    # ---- B4a's OWN GEOMETRY: the board is DOWN ---------------------------
    # The clause this whole rung exists for. Asserted in the hint, before any
    # render, so a hint that stages a RAISED board is refused here and not
    # discovered in a verdict.
    sho_y = gk["Rsho"][1]
    check("B4a AS GEOMETRY: the board's top edge (%.1f) is BELOW the guard's "
          "shoulder (%.1f) -- a LOWERED clipboard is what the beat asks for"
          % (g["top_y"], sho_y), g["top_y"] > sho_y)
    check("the board hangs at the hip, not the chest: its centre (%.1f) is "
          "below his hip line (%.1f)" % (g["cy"], g["guard_hip_y"]),
          g["cy"] > g["guard_hip_y"])
    check("the board is a closed quad -- four corners, and the first repeats to "
          "close it (enclosure is the one thing the scribble net reads well)",
          len(poly) == 4)
    check("the clip lies ON the top edge, spanning its middle half",
          all(min(c0[0], c1[0]) - 1 <= p[0] <= max(c0[0], c1[0]) + 1
              and min(c0[1], c1[1]) - 1 <= p[1] <= max(c0[1], c1[1]) + 1
              for p in g["clip"]))
    # ON THE RECORD RATHER THAN IN A COMMENT: the clip is collinear with the
    # top edge, so it is not a second mark. Measured, printed, and carried
    # unchanged because this is the geometry B4a passed on four times.
    clip_off = max(abs((p[0] - c0[0]) * ey - (p[1] - c0[1]) * ex) / elen
                   for p in g["clip"])
    print("     OBSERVED: the clip sits %.2f px off the top edge -- it is "
          "COLLINEAR and adds no distinct mark. Inherited, not introduced, and "
          "not changed on this rung." % clip_off)

    # ---- INK: sparse, but not blank --------------------------------------
    frac = ink_fraction(img)
    print("     ink fraction %.5f" % frac)
    check("the hint carries ink but is sparse (%.5f in [0.002, 0.02]) -- a blank "
          "hint conditions nothing and a fill conditions everything"
          % frac, 0.002 <= frac <= 0.02)

    # =====================================================================
    # THE GRIP HINT. Every claim the ladder argument makes about this mark is
    # re-stated here as a pixel test, because "it is enclosure-class, not a
    # stroke" and "it adds no new limb" are exactly the sentences a later edit
    # would keep in the prose while breaking in the drawing.
    # =====================================================================
    print("  -- the GRIP variant (build(grip=True)) --")
    gimg, gm = build(grip=True)
    gink = ink_mask(gimg)
    gp = g["grip_poly"]

    # (1) ONE VARIABLE, AS A SUPERSET. Nothing the board hint lit is dark here,
    # and nothing moved: the difference is additive and it is the loop.
    check("the grip hint is a strict SUPERSET of the default hint -- not one "
          "board pixel was moved, removed or redrawn",
          ImageChops.subtract(ink, gink).getbbox() is None
          and gimg.tobytes() != img.tobytes())
    added = ImageChops.subtract(gink, ink)
    loop_edges = [(gp[i][0], gp[i][1], gp[(i + 1) % len(gp)][0],
                   gp[(i + 1) % len(gp)][1], pad) for i in range(len(gp))]
    loop_allowed = cp.capsule_mask(loop_edges, W, H)
    check("EVERY ADDED PIXEL IS INSIDE THE GRIP LOOP DILATED BY THE STROKE -- "
          "the loop is the ONLY thing this flag adds",
          ImageChops.subtract(added, loop_allowed).getbbox() is None)
    check("and every lit pixel in the grip hint is inside the board quad OR "
          "the loop, both dilated by the stroke",
          ImageChops.subtract(
              gink, ImageChops.lighter(allowed, loop_allowed)).getbbox() is None)

    # (2) THE MARK IS PINNED TO THE SKELETON'S WRIST, TO THE FLOAT. Same drift
    # guard the board already has: re-stage the guard and this fails rather
    # than the hand quietly sliding off the board.
    cxs = sum(p[0] for p in gp) / len(gp)
    cys = sum(p[1] for p in gp) / len(gp)
    check("THE LOOP'S CENTROID IS THE OPENPOSE SKELETON'S GUARD L-WRIST TO "
          "1e-9 (%r vs %r)" % ((round(cxs, 4), round(cys, 4)), gk["Lwri"]),
          abs(cxs - gk["Lwri"][0]) < 1e-9 and abs(cys - gk["Lwri"][1]) < 1e-9)

    # (3) ENCLOSURE, PROVED THE WAY SECTION 10 PROVED IT. A flood fill seeded
    # at the loop's centre, off ink, must be TRAPPED -- it may not reach the
    # frame border. This is the whole argument: r4's 1 px finger was an OPEN
    # stroke and was ignored; r5's skeleton was non-enclosure and was drawn as
    # light; the one class this net reads is a closed contour.
    flood = gimg.convert("L").point(lambda v: 0 if v >= 128 else 255)
    seed = (int(round(cxs)), int(round(cys)))
    check("the seed pixel for the enclosure proof is OFF ink (a seed on the "
          "line would prove nothing)", flood.getpixel(seed) == 255)
    ImageDraw.floodfill(flood, seed, 128)
    filled = flood.point(lambda v: 255 if v == 128 else 0)
    border = [filled.getpixel((x, 0)) for x in range(0, W, 7)] + \
             [filled.getpixel((x, H - 1)) for x in range(0, W, 7)] + \
             [filled.getpixel((0, y)) for y in range(0, H, 7)] + \
             [filled.getpixel((W - 1, y)) for y in range(0, H, 7)]
    n_trapped = sum(filled.histogram()[128:])
    print("     flood from the loop's centre fills %d px" % n_trapped)
    check("THE LOOP IS A CLOSED CELL -- the flood is TRAPPED and never reaches "
          "the frame border, so this is ENCLOSURE class and not a stroke",
          max(border) == 0 and 0 < n_trapped < 0.01 * W * H)

    # (4) IT STRADDLES THE BOARD'S TOP EDGE, which is the occlusion the beat
    # asks for. A loop entirely above the edge is a hand hovering; entirely
    # below is a hand behind the board.
    above = [p for p in gp if ((p[0] - c0[0]) * ey - (p[1] - c0[1]) * ex) > 0]
    below = [p for p in gp if ((p[0] - c0[0]) * ey - (p[1] - c0[1]) * ex) < 0]
    check("the loop STRADDLES the board's top edge -- %d vertices one side, %d "
          "the other" % (len(above), len(below)), above and below)

    # (5) NO NEW LIMB, AND THE GOBLIN IS STILL NEVER SHOWN. The claim the
    # argument rests hardest on, run through the identical instrument.
    check("NOT ONE LIT PIXEL OF THE GRIP HINT FALLS ON THE GOBLIN",
          ImageChops.multiply(gink, goblin_mask).getbbox() is None)
    ghit = limbs_hit(gink)
    print("     the grip hint's ink meets exactly these limbs: %s"
          % ", ".join(sorted(ghit)))
    check("THE GRIP LOOP ADDS NO NEW LIMB -- the hint still meets exactly "
          "{gripping forearm, torso, L thigh} (got %s)" % (sorted(ghit),),
          ghit == EXPECTED_OVERLAP)
    check("the guard's FACE is still untouched in the grip hint",
          not (ghit & HEAD_NAMES))
    check("and his POINTING ARM is still untouched in the grip hint",
          not (ghit & POINT_NAMES))

    # (6) SCOPE, PRINTED. The four contour losses conditioned two whole bodies;
    # this conditions 0.1% of the frame. The number goes on the record so
    # nobody has to take "small" on trust.
    ab = added.getbbox()
    scope = ((ab[2] - ab[0]) * (ab[3] - ab[1])) / float(W * H)
    print("     the loop is %.1f x %.1f px, bbox %r, %.3f%% of the frame"
          % (g["grip_w"], g["grip_h"], ab, 100.0 * scope))
    check("the loop is hand-sized, not a stroke and not a body: %.1f x %.1f px "
          "(section 9 ruled a 1 px finger insufficient) and under 0.5%% of the "
          "frame" % (g["grip_w"], g["grip_h"]),
          30.0 <= g["grip_w"] <= 80.0 and 24.0 <= g["grip_h"] <= 64.0
          and scope < 0.005)

    gfrac = ink_fraction(gimg)
    print("     grip hint ink fraction %.5f (board-only %.5f)" % (gfrac, frac))
    check("the grip hint is still sparse (%.5f in [0.002, 0.02])" % gfrac,
          0.002 <= gfrac <= 0.02)
    check("the grip hint's metadata names the loop and its class",
          gm.get("grip_loop", {}).get("class", "").startswith("closed loop")
          and "not a stroke" in gm["hint_class"])
    check("the grip hint is NOT the openpose hint either",
          gimg.tobytes() != op_img.tobytes())

    g1, g2 = io.BytesIO(), io.BytesIO()
    build(grip=True)[0].save(g1, "PNG")
    build(grip=True)[0].save(g2, "PNG")
    check("authoring the grip hint is deterministic", g1.getvalue() == g2.getvalue())

    # ---- determinism and refusals ----------------------------------------
    b1, b2 = io.BytesIO(), io.BytesIO()
    build()[0].save(b1, "PNG")
    build()[0].save(b2, "PNG")
    check("authoring is deterministic", b1.getvalue() == b2.getvalue())

    for kw, why in (({"ground_y": 0.0}, "ground_y out of range"),
                    ({"guard_h": 0.0}, "stature out of range"),
                    ({"guard_x": 1.5}, "guard off-frame"),
                    ({"stroke": 0}, "stroke below 1")):
        try:
            build(**kw)
            check("refuses %s" % why, False)
        except ValueError:
            check("refuses %s" % why, True)

    check("the metadata states, in the artifact itself, that no figure is drawn",
          m["figures_drawn"] == 0 and m["figure_pixels"] == 0
          and "no figure" in m["hint_class"])

    print(("SELFTEST FAIL: %d" % len(fails)) if fails else "SELFTEST PASS")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(
        description="draw beat 08's board-only scribble hint (no figures)")
    ap.add_argument("out", nargs="?", help="output PNG")
    ap.add_argument("--width", type=int, default=W)
    ap.add_argument("--height", type=int, default=H)
    ap.add_argument("--stroke", type=int, default=STROKE)
    ap.add_argument("--guard-x", type=float, default=GUARD_X)
    ap.add_argument("--guard-h", type=float, default=GUARD_H)
    ap.add_argument("--ground-y", type=float, default=GROUND_Y)
    ap.add_argument("--grip", action="store_true",
                    help="add the closed hand-sized loop at the authored "
                         "L-wrist (the first figure ink in this hint; argued "
                         "in pipeline/work-ladder-0819.md against the five "
                         "scribble-net tracing losses)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.out:
        ap.error("out PNG required (or --selftest)")

    img, meta = build(width=a.width, height=a.height, stroke=a.stroke,
                      guard_x=a.guard_x, guard_h=a.guard_h,
                      ground_y=a.ground_y, grip=a.grip)
    meta["ink_fraction"] = round(ink_fraction(img), 5)
    img.save(a.out, "PNG")
    print("wrote %s" % a.out)
    for k, v in meta.items():
        print("  %s: %s" % (k, v))
    print("  sha256: %s" % sha256_file(a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
