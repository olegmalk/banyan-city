#!/usr/bin/env python3
r"""BEAT 06's POSE HINT: one 5-head adult guard, holding a board at chest height.

    python3 pipeline/author_b06_guard_pose_0822.py --selftest
    python3 pipeline/author_b06_guard_pose_0822.py <out.png>

WHY THIS FILE EXISTS, AND IT IS A MEASUREMENT AND NOT A PREFERENCE. Beat 06 was
drawn twice tonight on the IP-Adapter route, once with the adapter on every
block for the first 15% of the denoise (`window4`) and once with it on a single
block for all 40 steps (`content`). Those are opposite settings on both axes the
sampler exposes, and they returned the same picture: a head-and-shoulders
close-up of the right man with his hands clasped at his chest -- the reference
photograph's crop AND the reference photograph's pose -- with no bark board
anywhere and no field. b05 did the same thing twice over. So the framing is not
a function of HOW the reference is applied; a tight-crop reference dictates the
crop, full stop, and the pose comes with it.

THE ROUTE THAT REMAINS IS THE ONE THE NIGHT ORDER ASKED FOR FIRST: pose the shot
with a drawn skeleton and take the man from the WORDS. The words are measured to
be enough for the identity half -- the guardcast2d sheet drew ten grown men out
of ten with no reference at all, and `dark cropped hair` plus `round wire-rim
glasses` have bound in every cell they have appeared in. What the words have
never been able to do is place a figure in a frame at a chosen size holding a
chosen object, and that is exactly what a pose hint is for.

Deferring the skeleton earlier tonight was still the right call and this file is
the payoff rather than a reversal: the adapter is now closed BY MEASUREMENT
rather than by argument, and if the skeleton also fails we know it is not
because an untried option was sitting there.

THIS IS FOR AN OPENPOSE NET, NOT A SCRIBBLE NET, AND THE DISTINCTION IS THE
WHOLE REASON THE ROUTE IS OPEN. `b08-arm-route-0819.md` §10 closed the scribble
family on measurement -- a medial-axis skeleton fed to a scribble net comes back
DRAWN, as glowing crosses and orbs on the figures' chests, because scribble
conditioning means "these lines are lines in the picture". A COCO-18 pose hint
fed to `xinsir/controlnet-openpose-sdxl-1.0` is a different kind of object: the
COLOUR of each stroke names a body part and the net was trained to read it as
anatomy, not as ink. controlnet_plate.py already takes `--controlnet` for
exactly this and has the licence note beside it.

ALL THE DRAWING IS BORROWED, ON PURPOSE. `figure_keypoints` and `draw_bodypose`
come from `author_b08_openpose_hint.py` unchanged, which is where the three
traps the upstream research names are already handled: the limb-colour and
dot-colour lists index differently, xinsir's line thickness is load-bearing and
wants ratio 3.0 at this canvas, and occlusion is expressed by omission. A second
copy of a colour table is a second place for a bug to move a filed verdict's
condition, so there is no second copy.

WHAT THIS FILE ADDS is one staging: a SINGLE figure, five heads tall, standing
centred in a 832x1216 frame, with both forearms brought in and up so the wrists
meet in front of the sternum. That wrist pair is the board: an openpose hint
cannot draw a prop, but two wrists together at chest height in front of the body
is the posture of holding one, and the prompt names the slab.

FIVE HEADS IS THE POINT OF THE WHOLE EXERCISE. `head_frac` is the head's height
as a fraction of stature, so an adult is 1/5 = 0.20 and the child proportion
this tree keeps accidentally drawing is nearer 1/4. The b08 lane's figures use
0.25 and 0.37 for a goblin. Asserted below rather than left in a comment.

$0, no GPU, no model, no network. Writing this png costs a second.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from PIL import Image, ImageDraw                                   # noqa: E402

from author_b08_openpose_hint import (                             # noqa: E402
    IDX, KP, draw_bodypose, figure_keypoints, ink_fraction, ratio_for,
)
from author_b08_pose_hint import H, W                              # noqa: E402

# --- THE STAGING ------------------------------------------------------------
# Stature and ground are chosen so the whole figure fits with sky above him and
# grass below: crown at y=270 leaves 270 px of pale sky, and the ankles land at
# y=1138 leaving a band of ground. A medium shot was tried twice tonight and
# came back as a close-up both times; a full figure is also the framing in which
# a board "as wide as his shoulders" can be READ as that width, because his
# shoulders are in the frame to compare it to.
CX = 416.0
STATURE = 900.0
GROUND_Y = 1170.0
HEAD_FRAC = 0.20          # FIVE HEADS. An adult. Not 0.25 and not 0.37.
TORSO_HALF = 96.0

# The board, expressed as anatomy because a pose hint has no props. Both wrists
# come in to just either side of the midline at sternum height, elbows dropped
# near the ribs -- the posture of holding a slab up to read it. `up(f)` is
# `GROUND_Y - f * STATURE`, the same fraction-from-the-ground convention the
# borrowed staging uses everywhere.
WRIST_FRAC = 0.615        # sternum height
WRIST_HALF = 62.0         # the two hands, a little under a shoulder width apart
ELBOW_FRAC = 0.605
ELBOW_HALF = 118.0        # elbows OUT past the wrists: forearms angle inward


def up(f):
    return GROUND_Y - f * STATURE


def keypoints():
    kps = figure_keypoints(CX, STATURE, GROUND_Y, HEAD_FRAC, TORSO_HALF)
    kps["Rwri"] = (CX - WRIST_HALF, up(WRIST_FRAC))
    kps["Lwri"] = (CX + WRIST_HALF, up(WRIST_FRAC))
    kps["Relb"] = (CX - ELBOW_HALF, up(ELBOW_FRAC))
    kps["Lelb"] = (CX + ELBOW_HALF, up(ELBOW_FRAC))
    return kps


def render():
    return draw_bodypose(Image.new("RGB", (W, H)), keypoints(), ratio_for(W, H))


# --- THE BOARD, WHICH THE POSE HINT CANNOT CARRY ---------------------------
# controlnet_plate.py says it on its own --controlnet2 flag: "a pose hint cannot
# carry an object, because COCO-18's eighteen keypoints are all body parts."
# Beat 06's entire standing fault IS the object -- "the bark board is the wrong
# size" -- so a rung that cannot draw a board answers nothing, and the second
# net is required here rather than optional. It is composed as a
# MultiControlNetModel, which the driver already supports and beat 08 already
# used.
#
# WHITE STROKES ON BLACK, AND JUST THE OUTLINE. The scribble net's measured
# behaviour is that it TRACES any line it can read (b08-arm-route-0819.md 10:
# "any hint this net can read is a hint it traces"). On beat 08 that was the
# defect, because a traced human outline is a costume card instead of a person.
# HERE IT IS THE FEATURE: a board IS a rectangle, so a net that draws exactly
# the rectangle you give it is the right instrument, and the thing this beat has
# never been able to control -- the board's SIZE -- becomes a number.
#
# AS WIDE AS HIS SHOULDERS, which is the clause the prompt asserts, measured off
# the same skeleton so the hint and the words cannot disagree.
BOARD_STROKE = 7
BOARD_H = 168.0

# WHERE THE RECTANGLE SITS, CORRECTED BY A RENDER. The first geometry centred the
# board ON the wrist line, so half of it hung BELOW his hands. At --scale2 0.85
# the scribble net anchored on the rectangle's top edge and grew a PLANK
# DOWNWARD out of it: a post standing in front of him, with his hands dropped to
# his sides. Nothing was holding anything.
#
# A board being READ is held UP: the hands are at its bottom edge and the blade
# rises in front of the chest. So the rectangle now sits entirely ABOVE the
# wrists, its bottom edge ON the wrist line, and there is nothing below the hands
# for the net to extend. Width is unchanged and still measured off the skeleton's
# own shoulders, which is what keeps the prompt clause `as wide as his shoulders`
# and the drawing the same number.
BOARD_BOTTOM_LIFT = 6.0   # the blade starts just above the knuckles


def board_box():
    kps = keypoints()
    half = abs(kps["Lsho"][0] - kps["Rsho"][0]) / 2.0
    y1 = kps["Rwri"][1] - BOARD_BOTTOM_LIFT
    return (CX - half, y1 - BOARD_H, CX + half, y1)


def render_board():
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle(board_box(), outline=(255, 255, 255), width=BOARD_STROKE)
    return img


def selftest():
    fails = []

    def check(what, ok):
        print(("  ok  " if ok else "  FAIL") + "  " + what)
        if not ok:
            fails.append(what)

    kps = keypoints()
    check("every COCO-18 keypoint is present -- omission means occlusion to this "
          "net, and an accidentally missing joint silently deletes limbs",
          sorted(kps) == sorted(KP))
    check("18 keypoints and the index table agrees", len(IDX) == 18 == len(KP))

    head_h = HEAD_FRAC * STATURE
    check("FIVE HEADS: stature / head height is 5.0 to within a rounding, which "
          "is the adult proportion this whole rung exists to impose",
          abs(STATURE / head_h - 5.0) < 0.01)

    crown = GROUND_Y - STATURE
    check("the crown is inside the canvas with sky above it (%d px)" % crown,
          0 < crown < H * 0.30)
    for name, (x, y) in kps.items():
        check("%s is inside the canvas" % name, 0 <= x <= W and 0 <= y <= H)

    # THE BOARD, AS GEOMETRY. Two wrists together in front of the sternum is the
    # only way a pose hint can say "he is holding something up to read it".
    rw, lw = kps["Rwri"], kps["Lwri"]
    check("the wrists are level with each other", abs(rw[1] - lw[1]) < 1e-6)
    check("the wrists are BOTH in front of the body, inside the shoulders",
          abs(rw[0] - CX) < TORSO_HALF and abs(lw[0] - CX) < TORSO_HALF)
    check("the hands are at chest height -- above the hips, below the chin",
          up(0.53) > rw[1] > kps["nose"][1])
    check("the elbows are OUTSIDE the wrists, so the forearms angle inward and "
          "read as holding rather than as hanging",
          abs(kps["Relb"][0] - CX) > abs(rw[0] - CX))
    check("the elbows hang at about wrist height, not up at the shoulders -- a "
          "chicken-wing elbow is what let the b08 net mirror a forearm",
          abs(kps["Relb"][1] - rw[1]) < 0.05 * STATURE)

    check("xinsir's thick-line band: this canvas resolves to ratio 3.0, and a "
          "thin skeleton is a DOCUMENTED way to get an ignored hint",
          ratio_for(W, H) == 3.0)

    img = render()
    check("the hint is the render size the plate is conditioned at",
          img.size == (W, H))
    ink = ink_fraction(img)
    check("the hint has ink in it and is not a black frame (%.4f)" % ink,
          0.005 < ink < 0.25)

    # A SINGLE FIGURE. The two-figure staging this borrows from puts a second
    # skeleton on the canvas; beat 06 has one man in it and a second figure
    # would be a defect the prompt could not remove.
    xs = [x for x, _ in kps.values()]
    check("all ink belongs to ONE figure -- every joint within a body width of "
          "the centre line", max(abs(x - CX) for x in xs) < 3.0 * TORSO_HALF)

    x0, y0, x1, y1 = board_box()
    kps2 = keypoints()
    sho_w = abs(kps2["Lsho"][0] - kps2["Rsho"][0])
    check("THE BOARD IS AS WIDE AS HIS SHOULDERS -- the clause the prompt "
          "asserts, measured off the same skeleton so hint and words cannot "
          "disagree (%.0f px vs %.0f)" % (x1 - x0, sho_w),
          abs((x1 - x0) - sho_w) < 1.0)
    check("THE BOARD SITS ABOVE THE HANDS, not straddling them -- the first "
          "geometry centred it on the wrist line and the net grew a plank "
          "downward out of the half that hung below",
          y1 <= kps2["Rwri"][1])
    check("its bottom edge is AT the hands, within a knuckle, so they read as "
          "holding it rather than pointing at it",
          0 < kps2["Rwri"][1] - y1 < 0.03 * STATURE)
    check("the blade rises in front of the chest and stops below the chin",
          kps2["nose"][1] < y0 < kps2["Rsho"][1] + 0.02 * STATURE)
    check("the board is inside the canvas",
          0 < x0 and x1 < W and 0 < y0 and y1 < H)
    bimg = render_board()
    bink = ink_fraction(bimg)
    check("the board hint has ink and is an OUTLINE, not a filled slab -- a "
          "filled rectangle is a different instruction to a scribble net "
          "(%.4f)" % bink, 0.001 < bink < 0.05)
    check("the two hints are the same size, which a MultiControlNet requires",
          bimg.size == img.size)

    print(("SELFTEST OK" if not fails else "SELFTEST FAILED (%d)" % len(fails)))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", help="output PNG for the POSE hint")
    ap.add_argument("--board-out", default=None,
                    help="also write the BOARD hint (white outline on black) "
                         "for the second, scribble net")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest or not a.out:
        rc = selftest()
        if not a.out:
            return rc
        if rc:
            return rc
    img = render()
    img.save(a.out)
    with open(a.out, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    print("wrote %s  %dx%d  ink %.4f  sha256 %s"
          % (a.out, img.size[0], img.size[1], ink_fraction(img), sha))
    if a.board_out:
        b = render_board()
        b.save(a.board_out)
        with open(a.board_out, "rb") as fh:
            bsha = hashlib.sha256(fh.read()).hexdigest()
        x0, _, x1, _ = board_box()
        print("wrote %s  %dx%d  ink %.4f  board width %.0f px  sha256 %s"
              % (a.board_out, b.size[0], b.size[1], ink_fraction(b),
                 x1 - x0, bsha))
    return 0


if __name__ == "__main__":
    sys.exit(main())
