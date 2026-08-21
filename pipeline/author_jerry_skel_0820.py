#!/usr/bin/env python3
r"""THE REFERENCE ROUTE, SINGLE FIGURE: a COCO-18 skeleton whose HEAD-TO-BODY
RATIO IS THE AUTHORED VARIABLE.

WHY THIS INSTRUMENT AND NOT IP-ADAPTER, in two sentences and both are from the
house record rather than from theory:

  1. `b08-arm-route-0819.md` Sec 13 measured that the openpose net binds
     STATURE as geometry on this exact checkpoint -- "830/715 px, ratio 1.161
     against 1.100 authored, both statures within 4%" -- and Sec 11 measured
     that the masked IP-Adapter is an ATTRIBUTE instrument that explicitly did
     NOT govern geometry ("That is not the adapter", of an arm that came back
     aimed wrong while skin, face and wardrobe all transferred).
  2. Head-to-body is geometry, and the face is already solved by WORDING, so
     the openpose route changes exactly one thing and leaves the ratified
     recipe byte-identical -- where an IP-Adapter off the tile would re-supply
     the face the wording already gets right and make the rung unattributable.

WHAT IS AUTHORED. `head_frac` is head height as a fraction of STANDING STATURE.
Measured off the tile at 1:1 (`review/ep2-goblin-design-0819/adult-b19-0819.jpg`,
680x1236): crown y=292, chin y~447, head height ~155 px; crown-to-sole while
SEATED ~623 px, i.e. 4.0 heads seated. A seated crown-to-floor is ~0.77 of
standing height (knee height ~0.285H plus sitting height ~0.52H, and the tile's
knee height is what he is sitting at), so standing stature ~809 px and the tile
reads **5.2 heads**. head_frac = 1/5.2 = 0.19. canon's `correction_2026_08_20`
independently says "roughly a fifth"; the twelve-pose set reads about a third.

THE ONE RULE THAT MAKES A BOBBLEHEAD A HONEST CONTROL. A skeleton cannot put a
one-third head above shoulders that sit at 0.82 of stature -- the nose lands ON
the neck. So the shoulder line is DERIVED from head_frac:

    shoulder_frac = 1 - head_frac - NECK_GAP        NECK_GAP = 0.015

and every landmark below the shoulder is scaled by `shoulder_frac / 0.82` off
`author_b08_pose_hint`'s own template fractions. NECK_GAP is 0.015 and not the
usual 0.05 because canon says of the tile: "NECK -- effectively none. The dome
sits on sloped narrow shoulders."

`torso_half` is held CONSTANT across rungs at 0.1225 * stature (adult shoulder
breadth is ~0.245 of height), so head_frac is the only thing that moves between
the h19 / h32 / h16 hints and the h32 control is a true one-variable control.

The drawing itself -- limb ellipses, the 18-colour ramp, xinsir's resolution
ratio -- is `author_b08_openpose_hint.draw_bodypose`, unmodified and imported,
because that renderer is the one the net has already bound to twice.

    python3 pipeline/author_jerry_skel_0820.py --all
    python3 pipeline/author_jerry_skel_0820.py --selftest    # no GPU, no net

$0. No model, no network, no GPU.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from author_b08_openpose_hint import (  # noqa: E402  -- the proven renderer
    KP, draw_bodypose, ratio_for,
)

W, H = 832, 1216          # controlnet_plate.W/H; check_control asserts equality
GROUND_Y = 0.945          # the same foot line b08 has bound to twice
STATURE = 0.800           # of frame height: whole body plus headroom at 9:16
TORSO_HALF = 0.1225       # of stature, HELD across every rung
NECK_GAP = 0.015          # of stature. The tile has effectively no neck.
HEAD_RATIO = 0.80         # head width / head height

# `author_b08_pose_hint`'s template, as fractions of stature above ground, at
# its own SHOULDER_FRAC of 0.82. Everything below the shoulder is scaled.
TPL_SHOULDER = 0.82
TPL = {"elb": 0.66, "wri": 0.48, "hip": 0.53, "kne": 0.285, "ank": 0.035}

# The tile, measured. See the module docstring for the arithmetic.
TILE_HEAD_FRAC = 0.190          # 5.26 heads standing
BOBBLE_HEAD_FRAC = 0.320        # what all twelve tile-set poses actually drew
LEAN_HEAD_FRAC = 0.160          # 6.25 heads -- the overshoot rung
AGE_B_HEAD_FRAC = 0.240         # 4.17 heads -- OPTION B, the age the tree draws
                                # from 2026-08-21. Not a candidate any more: the
                                # founder ruled the axis younger and B is the
                                # decided rung, so this is the head_frac every
                                # new Jerry skeleton is authored at.


def figure(head_frac, pose="stand", cx_frac=0.5,
           width=W, height=H, stature_frac=STATURE, ground=GROUND_Y):
    """COCO-18 keypoints for ONE front-facing figure. head_frac is the variable."""
    if not 0.05 < head_frac < 0.45:
        raise ValueError("head_frac out of range: %r" % (head_frac,))
    stature = stature_frac * height
    ground_y = ground * height
    cx = cx_frac * width
    crown = ground_y - stature
    head_h = head_frac * stature
    head_w = HEAD_RATIO * head_h
    nose_y = crown + head_h * 0.55
    sho_frac = 1.0 - head_frac - NECK_GAP
    if sho_frac <= TPL["hip"]:
        raise ValueError("head_frac %r leaves no torso" % (head_frac,))
    k = sho_frac / TPL_SHOULDER
    th = TORSO_HALF * stature

    def up(f):
        return ground_y - f * k * stature

    sho_y = ground_y - sho_frac * stature
    kp = {
        "nose": (cx, nose_y),
        "neck": (cx, sho_y),
        "Rsho": (cx - th * 0.95, sho_y),
        "Lsho": (cx + th * 0.95, sho_y),
        "Relb": (cx - th * 1.05, up(TPL["elb"])),
        "Lelb": (cx + th * 1.05, up(TPL["elb"])),
        "Rwri": (cx - th * 1.00, up(TPL["wri"])),
        "Lwri": (cx + th * 1.00, up(TPL["wri"])),
        "Rhip": (cx - th * 0.60, up(TPL["hip"])),
        "Lhip": (cx + th * 0.60, up(TPL["hip"])),
        "Rkne": (cx - th * 0.55, up(TPL["kne"])),
        "Lkne": (cx + th * 0.55, up(TPL["kne"])),
        # THE ANKLE IS NOT SCALED. Every landmark below the shoulder shrinks
        # with the torso except this one: the foot line is the invariant the
        # b08 route has bound to the pixel twice (Sec 11: authored 1149.1,
        # drawn 1151 and 1152), and holding it is what lets h19 and h32 be
        # compared as the same photograph of two different creatures.
        "Rank": (cx - th * 0.50, ground_y - TPL["ank"] * stature),
        "Lank": (cx + th * 0.50, ground_y - TPL["ank"] * stature),
        "Reye": (cx - head_w * 0.20, nose_y - head_h * 0.14),
        "Leye": (cx + head_w * 0.20, nose_y - head_h * 0.14),
        "Rear": (cx - head_w * 0.46, nose_y - head_h * 0.10),
        "Lear": (cx + head_w * 0.46, nose_y - head_h * 0.10),
    }
    if pose == "stride":
        # Mid-stride, wading: R leg forward and lifted, L leg trailing, L arm
        # swung forward and up. The stature, the head and the foot line of the
        # PLANTED leg are untouched, so T8 is still read the same way.
        kp["Rkne"] = (cx + th * 0.30, up(TPL["kne"]) - 0.020 * stature)
        kp["Rank"] = (cx + th * 1.05,
                      ground_y - TPL["ank"] * stature - 0.055 * stature)
        kp["Lkne"] = (cx - th * 0.75, up(TPL["kne"]))
        kp["Lank"] = (cx - th * 1.10, ground_y - TPL["ank"] * stature)
        kp["Lelb"] = (cx + th * 1.15, up(TPL["elb"]) - 0.020 * stature)
        kp["Lwri"] = (cx + th * 1.55, up(TPL["elb"]) + 0.010 * stature)
        kp["Relb"] = (cx - th * 1.15, up(TPL["elb"]))
        kp["Rwri"] = (cx - th * 1.05, up(TPL["wri"]) - 0.030 * stature)

    # -----------------------------------------------------------------------
    # THE POSE SET, ADDED 2026-08-20 AFTER n1/n5 SETTLED THE INSTRUMENT.
    #
    # EVERY POSE BELOW HOLDS head_frac AND THE HEAD KEYPOINTS AT THE VALUES
    # `stand` GIVES THEM WHEN THE FIGURE IS UPRIGHT, and lowers the whole head
    # group as one rigid block when it is not. The LoRA gate is PROPORTION
    # DIVERSITY, so a pose that quietly changes the head's size while changing
    # the pose would teach the trigger token the one thing this route exists to
    # fix. `crown_offset` is the block move; nothing else touches the head.
    # -----------------------------------------------------------------------
    def drop_head(dy, dx=0.0):
        for n in ("nose", "Reye", "Leye", "Rear", "Lear"):
            kp[n] = (kp[n][0] + dx, kp[n][1] + dy)

    def drop_upper(dy, dx=0.0):
        for n in ("neck", "Rsho", "Lsho"):
            kp[n] = (kp[n][0] + dx, kp[n][1] + dy)

    if pose == "seatspan":
        # ==================================================================
        # THE TILE'S ACTUAL STANCE, AND IT IS A SPAN FIX, NOT A POSE TWEAK.
        #
        # `sit` folded the knees up to the chest -- GROUND-sitting -- and the
        # skeleton spanned about 0.40 of stature. The net read that short span
        # as a SMALL PERSON and re-inflated the head: 3.06 heads drawn against
        # 5.26 authored, with the head keypoints byte-identical to `stand`'s.
        # kneel and crouch failed the same way.
        #
        # But the tile is not ground-sitting. HE IS SITTING ON SOMETHING WITH
        # HIS FEET FLAT ON THE GROUND -- measured off adult-b19-0819.jpg, his
        # soles are at y=915 and his crown at y=292, which is 0.77 of his
        # standing height, not half of it. Authoring the stance he is ACTUALLY
        # in keeps the ankles on the same foot line every other rung uses and
        # holds the span at ~0.74, and that is the cheap test of the mechanism:
        # if span is what the net reads, giving it the span should give back
        # the proportion, with the fold coming from the wording.
        # ==================================================================
        hip_y = ground_y - TPL["kne"] * k * stature      # hips at knee height
        d = (TPL["hip"] * k * stature) - (ground_y - hip_y)
        drop_head(d)
        drop_upper(d)
        kp["Rhip"] = (cx - th * 0.60, hip_y)
        kp["Lhip"] = (cx + th * 0.60, hip_y)
        # Knees forward and level with the hips; ankles ON the authored foot
        # line, which is the invariant this whole lane has held since n1.
        kp["Rkne"] = (cx - th * 0.85, hip_y + 0.010 * stature)
        kp["Lkne"] = (cx + th * 0.85, hip_y + 0.010 * stature)
        kp["Rank"] = (cx - th * 0.70, ground_y - TPL["ank"] * stature)
        kp["Lank"] = (cx + th * 0.70, ground_y - TPL["ank"] * stature)
        # canon: "hands clasped between the knees, head sunk into the collar".
        kp["Relb"] = (cx - th * 1.05, kp["Rsho"][1] + 0.105 * stature)
        kp["Lelb"] = (cx + th * 1.05, kp["Lsho"][1] + 0.105 * stature)
        kp["Rwri"] = (cx - th * 0.18, hip_y - 0.010 * stature)
        kp["Lwri"] = (cx + th * 0.18, hip_y - 0.010 * stature)
        drop_head(0.20 * head_h)
    elif pose == "kneel":
        # Both knees down, torso upright. The KNEE takes the ground line and
        # the ankles fold back behind it.
        d = (TPL["kne"] * k) * stature
        drop_head(d)
        drop_upper(d)
        for n in ("Relb", "Lelb", "Rwri", "Lwri", "Rhip", "Lhip"):
            kp[n] = (kp[n][0], kp[n][1] + d)
        kp["Rkne"] = (cx - th * 0.55, ground_y - TPL["ank"] * stature)
        kp["Lkne"] = (cx + th * 0.55, ground_y - TPL["ank"] * stature)
        kp["Rank"] = (cx - th * 0.70, ground_y - TPL["ank"] * stature
                      - 0.030 * stature)
        kp["Lank"] = (cx + th * 0.70, ground_y - TPL["ank"] * stature
                      - 0.030 * stature)
    elif pose == "sit":
        # THE TILE'S OWN STANCE: seated, knees up, hands clasped between them,
        # head sunk into the collar. canon: "small, folded, hunched inward".
        d = (TPL["hip"] * k) * stature - 0.055 * stature
        drop_head(d + 0.020 * stature)
        drop_upper(d)
        kp["Rhip"] = (cx - th * 0.60, ground_y - TPL["ank"] * stature
                      - 0.020 * stature)
        kp["Lhip"] = (cx + th * 0.60, ground_y - TPL["ank"] * stature
                      - 0.020 * stature)
        kp["Rkne"] = (cx - th * 0.95, kp["Rsho"][1] + 0.115 * stature)
        kp["Lkne"] = (cx + th * 0.95, kp["Lsho"][1] + 0.115 * stature)
        kp["Rank"] = (cx - th * 0.75, ground_y - TPL["ank"] * stature)
        kp["Lank"] = (cx + th * 0.75, ground_y - TPL["ank"] * stature)
        kp["Relb"] = (cx - th * 1.10, kp["Rsho"][1] + 0.085 * stature)
        kp["Lelb"] = (cx + th * 1.10, kp["Lsho"][1] + 0.085 * stature)
        kp["Rwri"] = (cx - th * 0.20, kp["Rsho"][1] + 0.135 * stature)
        kp["Lwri"] = (cx + th * 0.20, kp["Lsho"][1] + 0.135 * stature)
    elif pose == "crouch":
        d = (TPL["hip"] * k) * stature - 0.150 * stature
        drop_head(d)
        drop_upper(d)
        kp["Rhip"] = (cx - th * 0.60, kp["Rsho"][1] + 0.150 * stature)
        kp["Lhip"] = (cx + th * 0.60, kp["Lsho"][1] + 0.150 * stature)
        kp["Rkne"] = (cx - th * 1.00, kp["Rsho"][1] + 0.130 * stature)
        kp["Lkne"] = (cx + th * 1.00, kp["Lsho"][1] + 0.130 * stature)
        kp["Rank"] = (cx - th * 0.85, ground_y - TPL["ank"] * stature)
        kp["Lank"] = (cx + th * 0.85, ground_y - TPL["ank"] * stature)
        kp["Relb"] = (cx - th * 1.15, kp["Rsho"][1] + 0.075 * stature)
        kp["Lelb"] = (cx + th * 1.15, kp["Lsho"][1] + 0.075 * stature)
        kp["Rwri"] = (cx - th * 0.75, kp["Rsho"][1] + 0.145 * stature)
        kp["Lwri"] = (cx + th * 0.75, kp["Lsho"][1] + 0.145 * stature)
    elif pose == "reach":
        # Both arms up. The legs and the head are `stand`'s exactly, so this
        # pose isolates the ARMS and nothing else.
        kp["Relb"] = (cx - th * 1.35, up(0.86))
        kp["Lelb"] = (cx + th * 1.35, up(0.86))
        kp["Rwri"] = (cx - th * 1.20, up(1.00))
        kp["Lwri"] = (cx + th * 1.20, up(1.00))
    elif pose == "point":
        # One arm out horizontal at shoulder height, the other hanging.
        kp["Lelb"] = (cx + th * 1.70, kp["Lsho"][1] + 0.010 * stature)
        kp["Lwri"] = (cx + th * 2.90, kp["Lsho"][1] + 0.015 * stature)
    elif pose == "hunch":
        # canon: "hunched inward, head sunk into the collar. Not upright, not
        # heroic." Standing, but folded: the head drops a quarter of its own
        # height into the shoulders and the shoulders roll forward and in.
        drop_head(0.25 * head_h)
        kp["Rsho"] = (cx - th * 0.78, kp["Rsho"][1] + 0.020 * stature)
        kp["Lsho"] = (cx + th * 0.78, kp["Lsho"][1] + 0.020 * stature)
        kp["neck"] = (cx, kp["neck"][1] + 0.020 * stature)
        kp["Relb"] = (cx - th * 0.90, up(TPL["elb"]))
        kp["Lelb"] = (cx + th * 0.90, up(TPL["elb"]))
        kp["Rwri"] = (cx - th * 0.30, up(TPL["wri"]) + 0.015 * stature)
        kp["Lwri"] = (cx + th * 0.30, up(TPL["wri"]) + 0.015 * stature)
    elif pose not in ("stand", "stride"):
        raise ValueError("unknown pose %r" % (pose,))

    meta = {
        "head_frac": head_frac,
        "heads_tall": round(1.0 / head_frac, 2),
        "shoulder_frac": round(sho_frac, 4),
        "stature_px": round(stature, 1),
        "head_px": round(head_h, 1),
        "ground_y_px": round(ground_y, 1),
        "torso_half_px": round(th, 1),
        "pose": pose,
    }
    return kp, meta


def build(head_frac, pose="stand", width=W, height=H):
    from PIL import Image
    kp, meta = figure(head_frac, pose=pose, width=width, height=height)
    img = Image.new("RGB", (width, height), (0, 0, 0))
    meta["ratio"] = ratio_for(width, height)
    draw_bodypose(img, kp, meta["ratio"])
    return img, meta


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


HINTS = [
    ("jerry-skel-h19-0820.png", TILE_HEAD_FRAC, "stand",
     "THE TILE. 5.26 heads standing, measured off adult-b19-0819.jpg at 1:1."),
    ("jerry-skel-h32-0820.png", BOBBLE_HEAD_FRAC, "stand",
     "THE CONTROL. 3.13 heads -- what the twelve-pose set actually drew. If "
     "the net binds head-to-body, this comes back a bobblehead ON PURPOSE, "
     "and that is what turns h19 from a lucky frame into a demonstrated "
     "mechanism."),
    ("jerry-skel-h16-0820.png", LEAN_HEAD_FRAC, "stand",
     "THE OVERSHOOT. 6.25 heads. Asks whether the net lands where it is aimed "
     "or drifts back toward the checkpoint's own prior."),
    ("jerry-skel-h19stride-0820.png", TILE_HEAD_FRAC, "stride",
     "TILE PROPORTION, SECOND POSE. The LoRA gate is proportion diversity, "
     "not one good standing frame, so a second pose is filed in the same "
     "batch rather than after it."),
    # ---- THE POSE SET, added after n1/n5 settled the instrument. Same
    # ---- head_frac, same head keypoints; only the body moves.
    ("jerry-skel-h19kneel-0820.png", TILE_HEAD_FRAC, "kneel", "pose set"),
    ("jerry-skel-h19sit-0820.png", TILE_HEAD_FRAC, "sit",
     "THE TILE'S OWN STANCE, folded and hands clasped."),
    ("jerry-skel-h19crouch-0820.png", TILE_HEAD_FRAC, "crouch", "pose set"),
    ("jerry-skel-h19reach-0820.png", TILE_HEAD_FRAC, "reach", "pose set"),
    ("jerry-skel-h19point-0820.png", TILE_HEAD_FRAC, "point", "pose set"),
    ("jerry-skel-h19hunch-0820.png", TILE_HEAD_FRAC, "hunch",
     "canon's 'hunched inward, head sunk into the collar'."),
    # ---- THE SPAN FIX. `sit`/`kneel`/`crouch` all came back as SMALL FIGURES
    # ---- because the net reads a short skeleton as a small person. These two
    # ---- author the tile's ACTUAL stance -- seated with the feet on the same
    # ---- foot line every other rung uses -- which holds the span at 0.69 of
    # ---- stature instead of 0.49, and one of them shrinks the authored head
    # ---- by the same factor in case the net normalises head size to span.
    ("jerry-skel-h19seat-0820.png", TILE_HEAD_FRAC, "seatspan",
     "THE TILE'S STANCE AT FULL SPAN, head_frac unchanged at 0.190."),
    ("jerry-skel-h145seat-0820.png", 0.145, "seatspan",
     "THE SAME STANCE WITH THE HEAD PRE-SHRUNK to 0.145, which puts the "
     "authored heads-over-span at 4.72 instead of 3.63. If the net normalises "
     "head size to the skeleton's span rather than reading the head keypoints, "
     "this is the rung that lands and the plain one does not."),
    # ---- AGE B, 2026-08-21. The founder ruled the age axis younger and the
    # ---- steward picked OPTION B off the nine-frame ladder: head_frac 0.240,
    # ---- 4.17 heads. `jerry-skel-h240-0821.png` is that dial in the STAND pose
    # ---- and it is the frame he looked at; the four below are the SAME NUMBER
    # ---- in the four other stances the seven-beat wave needs, so the wave can
    # ---- move the age dial without also moving the pose instrument. Authored
    # ---- by the same build() as every other skeleton in the tree; the five
    # ---- head keypoints still translate as one rigid block, which is what lets
    # ---- the adapter mask follow a pose by translation at this head_frac too.
    ("jerry-skel-h240seat-0821.png", AGE_B_HEAD_FRAC, "seatspan",
     "AGE B, THE TILE'S OWN STANCE. Beat 13 -- THE SHADE. This is the sample "
     "pose: beat 13 is the frame the founder ruled the adult read on, and it "
     "was round one's best pass, so it is where the age pivot is sampled."),
    ("jerry-skel-h240stride-0821.png", AGE_B_HEAD_FRAC, "stride",
     "AGE B, striding. Beat 02 -- THE SPRINT."),
    ("jerry-skel-h240crouch-0821.png", AGE_B_HEAD_FRAC, "crouch",
     "AGE B, squatting. Beats 03 (BAD COVER) and 20 (EVIDENCE)."),
    ("jerry-skel-h240hunch-0821.png", AGE_B_HEAD_FRAC, "hunch",
     "AGE B, hunched. Beat 04 -- THE FOOTNOTE, the peek."),
]


def selftest():
    """THE BAR BEFORE THE PIXELS. No GPU, no weights, no network."""
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + name)
        ok = ok and bool(cond)

    print("author_jerry_skel_0820 selftest")

    kp19, m19 = figure(TILE_HEAD_FRAC)
    kp32, m32 = figure(BOBBLE_HEAD_FRAC)
    check("h19 is 5.26 heads tall", m19["heads_tall"] == 5.26)
    check("h32 is 3.12 heads tall", m32["heads_tall"] == 3.12)
    check("every COCO-18 keypoint is present in both",
          sorted(kp19) == sorted(KP) and sorted(kp32) == sorted(KP))

    # The defect this whole rung exists to fix, asserted as geometry.
    def crown_to_sole(kp, m):
        crown = m["ground_y_px"] - m["stature_px"]
        return max(kp["Rank"][1], kp["Lank"][1]) - crown
    r19 = crown_to_sole(kp19, m19) / m19["head_px"]
    r32 = crown_to_sole(kp32, m32) / m32["head_px"]
    print("     drawn crown-to-ankle in heads: h19 %.2f, h32 %.2f" % (r19, r32))
    check("h19 draws a figure 4.5+ heads to the ankle", r19 >= 4.5)
    check("h32 draws a figure under 3.2 heads to the ankle", r32 < 3.2)

    # The control is a control: ONE thing moved.
    check("the control moves head_frac and NOTHING else -- same stature, "
          "same torso half, same ground line",
          m19["stature_px"] == m32["stature_px"]
          and m19["torso_half_px"] == m32["torso_half_px"]
          and m19["ground_y_px"] == m32["ground_y_px"])
    check("the shoulder line is DERIVED, so the bobblehead's nose clears its "
          "own neck", kp32["nose"][1] < kp32["neck"][1] - 0.02 * m32["stature_px"]
          and kp19["nose"][1] < kp19["neck"][1] - 0.02 * m19["stature_px"])
    check("both figures stand on the same foot line",
          abs(kp19["Rank"][1] - kp32["Rank"][1]) < 1e-6)

    ks, ms = figure(TILE_HEAD_FRAC, pose="stride")
    check("the stride pose keeps the tile's head_frac", ms["head_frac"] == TILE_HEAD_FRAC)
    check("the stride pose keeps ONE foot on the authored ground line",
          abs(ks["Lank"][1] - kp19["Lank"][1]) < 1e-6)
    check("the stride pose actually differs from standing",
          ks["Rank"] != kp19["Rank"] and ks["Lwri"] != kp19["Lwri"])

    check("the canvas is controlnet_plate's own size", (W, H) == (832, 1216))
    try:
        figure(0.60)
        check("head_frac 0.60 is refused", False)
    except ValueError:
        check("head_frac 0.60 is refused", True)

    try:
        from PIL import Image  # noqa: F401
    except Exception:
        print("  (PIL absent -- geometry checked, drawing not)")
        return 0 if ok else 1
    img, meta = build(TILE_HEAD_FRAC)
    check("the drawn hint is 832x1216 RGB",
          img.size == (W, H) and img.mode == "RGB")
    hist = img.convert("L").histogram()
    ink = sum(hist[32:]) / float(sum(hist))
    print("     ink fraction %.4f" % ink)
    check("the hint is sparse but not empty (0.5%-12% ink)", 0.005 < ink < 0.12)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--all", action="store_true",
                    help="write every hint into pipeline/control/")
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.all:
        ap.error("pass --all or --selftest")
    root = Path(__file__).resolve().parent
    outdir = Path(a.outdir) if a.outdir else root / "control"
    outdir.mkdir(parents=True, exist_ok=True)
    for name, hf, pose, why in HINTS:
        img, meta = build(hf, pose=pose)
        p = outdir / name
        img.save(p)
        print("%s  %s" % (sha256_file(p), p))
        print("   %s  %s" % (meta, why))
    return 0


if __name__ == "__main__":
    sys.exit(main())
