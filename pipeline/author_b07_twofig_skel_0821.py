#!/usr/bin/env python3
r"""BEAT 07's TWO-FIGURE OPENPOSE HINT: the canon goblin AND the guard, one canvas.

WHY THIS EXISTS. The canon-motion judge's b07 verdict (review/canonmotion-0821/
JUDGING-0821.md) is the licence: wording CAN summon the guard (it did, at f024,
once the negative stopped banning him) -- but a guard absent from the init is a
RE-STAGING instruction: the camera pulled back to fit him in, and the goblin was
gone by f096. "next rung is now a TWO-FIGURE PLATE ... a plate with both figures
already staged removes the re-stage AND gives the goblin a reason to still be
there at the end." This authors that plate's skeleton.

THE TWO FIGURES, each from the module that owns its geometry:
  GOBLIN  head_frac 0.370 (jerry_canon_0821, the founder's own proportion),
          pose `stand` -- beat 07's own WAVE pose -- at screen LEFT.
  GUARD   head_frac 0.200 (5 heads: A GROWN MAN, the founder's 2026-08-20
          guards ruling "they should look like grown men. yes. dumb grown
          men"), at screen RIGHT, taller: stature 0.86 of frame against the
          goblin's 0.53, both on the same GROUND_Y so they share a depth.
  THE ARM is authored MID-RAISE, aimed at the goblin's face: the beat's action
          is "the guard's arm comes up and points at him", so the plate must
          hold a START/MID state, not the completed point -- b20's frozen take
          is what an end-state plate buys (pre-registered and fired, same
          judging file). Mid-raise shortens the travel the motion model owes
          while leaving travel to exist.

THE IPA MASK is the goblin's head-and-ears box, re-derived from HIS skeleton at
HIS stature here (the canon head_box() assumes stature 0.90 and would print a
box around empty grass at 0.53). The guard gets NO adapter: his design is
carried by words + openpose alone, exactly like every shipped guard beat.

  python3 pipeline/author_b07_twofig_skel_0821.py            # write + print sha
  python3 pipeline/author_b07_twofig_skel_0821.py --check    # geometry only

$0. PIL only. Deterministic. The asset gets a NEW NAME (guardtwofig): an asset
whose content changes gets a new name, and nothing else writes this one.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import author_jerry_skel_0820 as skel   # noqa: E402
import jerry_canon_0821 as C            # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join("farm-out", "jerry-canon-assets-0821",
                   "jerry-guard-twofig-0821.png")

W, H = 832, 1216
GOBLIN_HEAD_FRAC = C.HEAD_FRAC          # 0.370, the founder's proportion
GOBLIN_CX, GOBLIN_STATURE = 0.30, 0.53
GUARD_HEAD_FRAC = 0.200                 # 5.0 heads: a grown man
GUARD_CX, GUARD_STATURE = 0.71, 0.86

# The guard's screen-left arm, mid-raise toward the goblin. Fractions of HIS
# torso-half / stature so the numbers say what they mean.
ARM_ELB = (1.35, 0.050)     # (th multiples left of cx, stature below shoulder)
ARM_WRI = (2.30, 0.115)


def figures():
    gob, gm = skel.figure(GOBLIN_HEAD_FRAC, pose="stand", cx_frac=GOBLIN_CX,
                          stature_frac=GOBLIN_STATURE)
    grd, dm = skel.figure(GUARD_HEAD_FRAC, pose="stand", cx_frac=GUARD_CX,
                          stature_frac=GUARD_STATURE)
    st = GUARD_STATURE * H
    th = skel.TORSO_HALF * st
    cx = GUARD_CX * W
    sho_y = grd["Rsho"][1]
    grd["Relb"] = (cx - th * ARM_ELB[0], sho_y + ARM_ELB[1] * st)
    grd["Rwri"] = (cx - th * ARM_WRI[0], sho_y + ARM_WRI[1] * st)
    return gob, gm, grd, dm


def goblin_head_box(gob, gm):
    head_h = gm["head_px"]
    skull_w = skel.HEAD_RATIO * head_h
    cx = (gob["Rear"][0] + gob["Lear"][0]) / 2.0
    crown = gob["nose"][1] - head_h * 0.55
    half = skull_w * C.MASK_EAR_SPAN_RATIO / 2.0 + C.MASK_MARGIN_PX
    box = [int(round(v)) for v in
           (cx - half, crown - C.MASK_MARGIN_PX,
            cx + half, crown + head_h + C.MASK_MARGIN_PX)]
    box[0] = max(0, box[0]); box[1] = max(0, box[1])
    box[2] = min(W, box[2]); box[3] = min(H, box[3])
    return box


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    gob, gm, grd, dm = figures()
    box = goblin_head_box(gob, gm)
    bad = []
    # The guard's pointing hand must stay OUT of the goblin's adapter box: the
    # adapter pushes goblin-face features into every pixel it may attend to.
    wx, wy = grd["Rwri"]
    if box[0] - 10 < wx < box[2] + 10 and wy > box[1] - 30:
        bad.append("guard wrist (%d,%d) crowds the goblin IPA box %s"
                   % (wx, wy, box))
    # Taller, and by a lot: the founder's guards are grown men over a small
    # goblin, and the judged clip's own read was 'a full head taller' AT LEAST.
    g_crown = grd["nose"][1] - dm["head_px"] * 0.55
    j_crown = gob["nose"][1] - gm["head_px"] * 0.55
    if not g_crown < j_crown - dm["head_px"]:
        bad.append("guard is not at least a full guard-head taller")
    # Both fully in frame.
    for name, kp in (("goblin", gob), ("guard", grd)):
        xs = [v[0] for v in kp.values()]; ys = [v[1] for v in kp.values()]
        if min(xs) < 8 or max(xs) > W - 8 or min(ys) < 8 or max(ys) > H - 8:
            bad.append("%s runs off the frame" % name)
    # They face each other across a GAP; overlapping skeletons merge figures.
    gob_right = max(v[0] for k, v in gob.items() if k != "Rwri")
    guard_body_left = grd["Rsho"][0]
    if gob_right + 20 > guard_body_left:
        bad.append("bodies overlap: goblin right %d vs guard shoulder %d"
                   % (gob_right, guard_body_left))
    print("goblin  %s" % gm)
    print("guard   %s  arm mid-raise wrist (%d,%d)" % (dm, wx, wy))
    print("goblin IPA head box: %s  (%dx%d px)"
          % (",".join(str(v) for v in box), box[2] - box[0], box[3] - box[1]))
    for m in bad:
        print("  !! %s" % m)
    if bad:
        return 1
    if a.check:
        return 0
    from PIL import Image
    img = Image.new("RGB", (W, H), (0, 0, 0))
    ratio = skel.ratio_for(W, H)
    skel.draw_bodypose(img, gob, ratio)
    skel.draw_bodypose(img, grd, ratio)
    p = os.path.join(REPO, OUT)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)
    sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
    print("wrote %s\nsha256 %s" % (OUT, sha))
    return 0


if __name__ == "__main__":
    sys.exit(main())
