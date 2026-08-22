#!/usr/bin/env python3
r"""BEAT 07's POSE HINT: the guard on the right pointing at the goblin's face.

    python3 pipeline/author_b07_twofig_pose_0822.py --selftest
    python3 pipeline/author_b07_twofig_pose_0822.py <out.png>

WHY BEAT 07 GETS A DRAWN HINT, WHEN IT ALREADY HAS ITS BEST CLIP EVER. Tonight's
b07 re-run put two figures in frame with the point landing, and it is staged as
the beat's best available. Its two remaining faults are BOTH crossover: the guard
wears the goblin's mandarin collar and frog buttons, and he has a POINTED EAR.
Wardrobe adjectives are closed as a lever -- the re-run matched the goblin's
description density word for word and the shared-noun items still duplicated --
and the commit that recorded that named per-figure conditioning as the next rung.

WHAT CHANGED SINCE, AND IT IS THE REASON THIS IS WORTH A SAMPLE. Four hours later
the pose route put TWO DIFFERENT MEN side by side in beat 05 -- one moustached,
one not -- from two drawn skeletons and words alone. Nothing in this tree had
managed a reliable two-figure frame before that. So there is now a mechanism that
gives the model a STRUCTURAL separation between two bodies before a single
attribute word is read, and beat 07's whole remaining problem is that the model
does not know where one body ends and the other begins.

**IT IS A TEST AND NOT A REPLACEMENT.** Beat 05's frame also leaked the glasses
onto both men, so a drawn separation is NOT known to stop attribute crossover --
it is the open question, and this is the cheapest place to ask it, because beat
07 is the beat where the crossover is measured rather than suspected.

THE STAGING. The goblin stands at frame LEFT and the guard at frame RIGHT, which
is the arrangement the beat has always used and the one tonight's clip drew. The
guard is FIVE HEADS -- an adult, the proportion the canon ruling wants. The
goblin is FOUR heads on a shorter stature, which is not a child's proportion by
accident: it is the broad-domed creature the founder ratified, whose head is
large relative to his body by design.

THE POINT AIMS AT THE FACE, NOT THE BELLY. `author_b08_openpose_hint` solves a
point at the goblin's NAVEL because that is beat 08's staging; beat 07's is the
confiscation and tonight's clip lands the finger on the cheek. COCO-18 has no
finger keypoint, so the ELBOW->WRIST limb is the last mark in the drawing and it
has to be the thing that aims -- the wrist is placed one hand short of the target
along the shoulder->target line, so that the hand the model draws beyond the
wrist lands on the face. That inversion is `author_b08_openpose_hint`'s own
finding, transcribed rather than rediscovered.

All the drawing is borrowed from `author_b08_openpose_hint.py` unchanged, for the
third time tonight and for the same reason: the colour indexing, xinsir's line
thickness and occlusion-by-omission are handled there.

$0, no GPU, no model, no network.
"""
from __future__ import annotations

import argparse
import hashlib
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from PIL import Image                                              # noqa: E402

from author_b08_openpose_hint import (                             # noqa: E402
    KP, draw_bodypose, figure_keypoints, ink_fraction, ratio_for,
)
from author_b08_pose_hint import H, W                              # noqa: E402

GROUND_Y = 1180.0
GOBLIN_X = 250.0
GUARD_X = 578.0
GOBLIN_STATURE = 620.0
GUARD_STATURE = 940.0
GOBLIN_HEAD_FRAC = 0.25   # FOUR heads: the broad-domed creature, by design
GUARD_HEAD_FRAC = 0.20    # FIVE heads: an adult
GOBLIN_TORSO_HALF = 66.0
GUARD_TORSO_HALF = 92.0

# Reach fractions of stature, transcribed from author_b08_pose_hint's shared
# staging rather than re-derived, so the two hints ask for the same anatomy.
UPPER = 0.152
FORE = 0.146
HAND = 0.052              # the hand the model draws BEYOND the wrist


def keypoints():
    gob = figure_keypoints(GOBLIN_X, GOBLIN_STATURE, GROUND_Y, GOBLIN_HEAD_FRAC,
                           GOBLIN_TORSO_HALF)
    gua = figure_keypoints(GUARD_X, GUARD_STATURE, GROUND_Y, GUARD_HEAD_FRAC,
                           GUARD_TORSO_HALF)

    # THE POINT. Target is the goblin's near cheek, not his navel: this beat is
    # the confiscation and tonight's clip lands the finger on his face.
    target = (gob["nose"][0] + GOBLIN_TORSO_HALF * 0.55, gob["nose"][1])
    sx, sy = gua["Rsho"]
    dx, dy = target[0] - sx, target[1] - sy
    full = math.hypot(dx, dy)
    upper, fore = UPPER * GUARD_STATURE, FORE * GUARD_STATURE
    hand = HAND * GUARD_STATURE
    reach = full - hand                       # where the WRIST must end up
    if reach > upper + fore:
        raise ValueError("the figures are too far apart: the arm cannot reach "
                         "%.1f px with %.1f px of limb" % (reach, upper + fore))
    if reach < abs(upper - fore) + 1.0:
        raise ValueError("the figures are too close: the elbow folds")
    # Two-link solve in the shoulder->target frame, elbow displaced DOWNWARD so
    # the arm reads as a level point and not as a raised salute.
    ux, uy = dx / full, dy / full
    a = (reach * reach + upper * upper - fore * fore) / (2.0 * reach)
    h = math.sqrt(max(0.0, upper * upper - a * a))
    ex = sx + ux * a - uy * -h
    ey = sy + uy * a + ux * -h
    if ey < sy:                               # keep the elbow at or below the shoulder
        ex = sx + ux * a + uy * -h
        ey = sy + uy * a - ux * -h
    gua["Relb"] = (ex, ey)
    # AND NOW THE WRIST GOES ON THE ELBOW->TARGET LINE, not back on the
    # shoulder->target ray. This is author_b08_openpose_hint's construction and
    # the reason for it is that COCO-18 has no finger: the elbow->wrist limb is
    # the last mark in the drawing, so IT has to be the thing that aims. Putting
    # the wrist on the shoulder ray instead leaves the forearm pointing 17 px
    # wide of the face -- measured, in this file's own selftest, before the fix.
    etx, ety = target[0] - ex, target[1] - ey
    elen = math.hypot(etx, ety)
    gua["Rwri"] = (ex + etx / elen * fore, ey + ety / elen * fore)
    # His other arm hangs.
    gua["Lelb"] = (GUARD_X + GUARD_TORSO_HALF * 1.10,
                   GROUND_Y - 0.62 * GUARD_STATURE)
    gua["Lwri"] = (GUARD_X + GUARD_TORSO_HALF * 1.15,
                   GROUND_Y - 0.48 * GUARD_STATURE)
    return gob, gua, target


def render():
    img = Image.new("RGB", (W, H))
    ratio = ratio_for(W, H)
    gob, gua, _ = keypoints()
    for kps in (gob, gua):
        img = draw_bodypose(img, kps, ratio)
    return img


def selftest():
    fails = []

    def check(what, ok):
        print(("  ok  " if ok else "  FAIL") + "  " + what)
        if not ok:
            fails.append(what)

    gob, gua, target = keypoints()
    for name, kps in (("goblin", gob), ("guard", gua)):
        check("%s has all 18 COCO keypoints" % name, sorted(kps) == sorted(KP))
        for k, (x, y) in kps.items():
            check("%s %s inside the canvas" % (name, k),
                  0 <= x <= W and 0 <= y <= H)

    check("the GUARD is five heads -- an adult, which is the canon ruling",
          abs(1.0 / GUARD_HEAD_FRAC - 5.0) < 0.01)
    check("the GOBLIN is four heads -- a big dome on a short body, which is his "
          "design and not a child's proportion by accident",
          abs(1.0 / GOBLIN_HEAD_FRAC - 4.0) < 0.01)
    check("the guard is the taller, which the beat and the cast both say",
          GUARD_STATURE > GOBLIN_STATURE)
    check("the goblin stands at frame LEFT of the guard, as this beat has always "
          "staged it", GOBLIN_X < GUARD_X)
    check("they stand on one ground line",
          abs(gob["Rank"][1] - gua["Rank"][1]) < 0.06 * GUARD_STATURE)

    # THE POINT AIMS. COCO-18 has no finger, so the forearm extended must run
    # through the target -- author_b08_openpose_hint's own finding.
    ex, ey = gua["Relb"]
    wx, wy = gua["Rwri"]
    fx, fy = wx - ex, wy - ey
    tx, ty = target[0] - ex, target[1] - ey
    cross = abs(fx * ty - fy * tx) / max(1e-6, math.hypot(fx, fy))
    check("the FOREARM extended passes within a few px of the goblin's cheek "
          "(%.1f px)" % cross, cross < 8.0)
    check("the wrist stops SHORT of the target, so the hand the model draws "
          "beyond it lands on the face rather than inside it (%.1f px)"
          % math.hypot(target[0] - wx, target[1] - wy),
          0.02 * GUARD_STATURE < math.hypot(target[0] - wx, target[1] - wy)
          < 0.14 * GUARD_STATURE)
    check("the forearm is one forearm long, so the two-link anatomy survived "
          "the re-aim (%.1f px vs %.1f)"
          % (math.hypot(fx, fy), FORE * GUARD_STATURE),
          abs(math.hypot(fx, fy) - FORE * GUARD_STATURE) < 1.0)
    check("the pointing elbow is at or below the shoulder -- a chicken-wing "
          "elbow is what let the b08 net mirror a forearm into a raised finger",
          ey >= gua["Rsho"][1] - 1.0)
    check("the point crosses the gap between them",
          gob["nose"][0] < wx < gua["Rsho"][0])

    check("xinsir's thick-line band: ratio 3.0", ratio_for(W, H) == 3.0)
    img = render()
    check("the hint is the render size the plate is conditioned at",
          img.size == (W, H))
    ink = ink_fraction(img)
    check("two skeletons' worth of ink (%.4f)" % ink, 0.01 < ink < 0.35)

    print(("SELFTEST OK" if not fails else "SELFTEST FAILED (%d)" % len(fails)))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", help="output PNG")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest or not a.out:
        rc = selftest()
        if not a.out or rc:
            return rc
    img = render()
    img.save(a.out)
    with open(a.out, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    print("wrote %s  %dx%d  ink %.4f  sha256 %s"
          % (a.out, img.size[0], img.size[1], ink_fraction(img), sha))
    return 0


if __name__ == "__main__":
    sys.exit(main())
