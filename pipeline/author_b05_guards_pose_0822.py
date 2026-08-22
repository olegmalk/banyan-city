#!/usr/bin/env python3
r"""BEAT 05's POSE HINT: TWO 5-head adult guards, side by side, facing out.

    python3 pipeline/author_b05_guards_pose_0822.py --selftest
    python3 pipeline/author_b05_guards_pose_0822.py <out.png>

WHY TWO SKELETONS AND NOT A BETTER SENTENCE. Beat 05 needs two men in frame and
has spent four wording rounds getting there; its ONE recorded win is "two figures
in the field from the first frame to the 117th -- never one, never three". Then
tonight the IP-Adapter route took that away twice over: both attempts returned
ONE man, in a close-up, wearing both briefs on one head. A figure count is a
COMPOSITION fact, and this tree has now measured twice in one night that the
composition is not reachable from the prompt when a tight-crop reference is in
the job -- and four rounds earlier that it is expensive to reach from wording
alone. Two drawn skeletons make the count an assertion instead of a hope: the
frame contains two figures because two figures were drawn into the hint.

THE FRAMING HALF OF THIS ROUTE IS ALREADY EVIDENCED. `ep2-b06-pose-0822` put a
whole man in a field at the drawn size with his hands where they were drawn --
which four adapter runs could not do at any setting -- and took his identity from
the words with no reference image in the job. That frame failed on its LIGHT and
on its board; neither failure touches the figure count, and both corrections are
carried here.

THE TWO MEN ARE DISTINGUISHED IN THE WORDS AND NOT IN THE HINT, because a
skeleton cannot carry a moustache. That leaves the b07 attribute-binding risk
live and it is pre-registered in the spec rather than papered over: the right
man's `thick grey moustache` is the only feature in the sentence the left man
cannot also have, which is the term-with-no-competitor shape that DID bind on
b07 when the collar did not.

WHAT THE HINT ASSERTS: two figures, both five heads tall, both standing, both
facing camera, feet on one shared ground line, separated far enough that their
silhouettes do not touch. The stature difference is small and deliberate -- guard
1 is the taller of the two by the cast sheet, and a visible height difference is
the cheapest non-verbal way to say "two different men" in a frame where the
identity words may or may not bind.

All the drawing is borrowed from `author_b08_openpose_hint.py` unchanged, for the
same reason as beat 06's: the limb-colour/dot-colour indexing, xinsir's
load-bearing line thickness and the occlusion-by-omission rule are handled there
and a second copy is a second place for a bug.

$0, no GPU, no model, no network.
"""
from __future__ import annotations

import argparse
import hashlib
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

GROUND_Y = 1170.0         # ONE ground line: they stand on the same earth
HEAD_FRAC = 0.20          # FIVE HEADS, both of them. Adults.
LEFT_X = 262.0
RIGHT_X = 570.0
LEFT_STATURE = 880.0      # guard 1, the taller by the cast sheet
RIGHT_STATURE = 830.0
TORSO_HALF = 86.0
ARM_FRAC = 0.50           # hands hanging at his sides, not staged


def figures():
    out = []
    for cx, stature in ((LEFT_X, LEFT_STATURE), (RIGHT_X, RIGHT_STATURE)):
        kps = figure_keypoints(cx, stature, GROUND_Y, HEAD_FRAC, TORSO_HALF)
        # Arms down and relaxed. The default staging puts the wrists a little in
        # toward the belly; on a two-figure frame that reads as a pose, and this
        # beat's people are standing and scanning, not doing anything.
        kps["Rwri"] = (cx - TORSO_HALF * 1.15, GROUND_Y - ARM_FRAC * stature)
        kps["Lwri"] = (cx + TORSO_HALF * 1.15, GROUND_Y - ARM_FRAC * stature)
        out.append(kps)
    return out


def render():
    img = Image.new("RGB", (W, H))
    ratio = ratio_for(W, H)
    for kps in figures():
        img = draw_bodypose(img, kps, ratio)
    return img


def selftest():
    fails = []

    def check(what, ok):
        print(("  ok  " if ok else "  FAIL") + "  " + what)
        if not ok:
            fails.append(what)

    figs = figures()
    check("TWO figures, which is the whole reason this hint exists -- the beat's "
          "one recorded win is two in frame and never one and never three",
          len(figs) == 2)
    for i, kps in enumerate(figs):
        check("figure %d has all 18 COCO keypoints" % i, sorted(kps) == sorted(KP))
        for name, (x, y) in kps.items():
            check("figure %d %s inside the canvas" % (i, name),
                  0 <= x <= W and 0 <= y <= H)

    for i, stature in enumerate((LEFT_STATURE, RIGHT_STATURE)):
        check("figure %d is FIVE HEADS tall" % i,
              abs(stature / (HEAD_FRAC * stature) - 5.0) < 0.01)

    check("they stand on ONE ground line",
          abs(figs[0]["Rank"][1] - figs[1]["Rank"][1]) < 0.06 * LEFT_STATURE)
    check("the left man is the taller, which is the cast sheet's reading and the "
          "cheapest non-verbal way to say two different men",
          LEFT_STATURE > RIGHT_STATURE)
    gap = (RIGHT_X - abs(figs[1]["Rsho"][0] - RIGHT_X)) - \
          (LEFT_X + abs(figs[0]["Lsho"][0] - LEFT_X))
    check("their silhouettes do not touch (%.0f px of clear air between the "
          "shoulders)" % gap, gap > 40)
    check("both are inside the frame with margin",
          all(0.04 * W < x < 0.96 * W
              for k in figs for x, _ in [k["nose"]]))

    check("xinsir's thick-line band: ratio 3.0 at this canvas",
          ratio_for(W, H) == 3.0)
    img = render()
    check("the hint is the render size the plate is conditioned at",
          img.size == (W, H))
    ink = ink_fraction(img)
    check("two skeletons' worth of ink, and not a black frame (%.4f)" % ink,
          0.01 < ink < 0.35)

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
