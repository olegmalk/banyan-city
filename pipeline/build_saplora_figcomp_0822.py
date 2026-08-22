#!/usr/bin/env python3
r"""SAPLING LoRA v2, STEP 2: draw the canon sapling into the figure plates.

WHAT IT CONSUMES. The eight plates from
`pipeline/derive_saplora_figplate_0822.py`, published to
`farm-out/ep3-saplora-fig<cell>-0822/`. Seven are depth cells (sitfar60/50/42)
with a measured unoccupied foreground band; the eighth, g1, is the sample --
a full-span `crouch` whose only rootable ground is the frame edge, kept
deliberately as the batch's one figure-fills-the-frame case.

WHAT IT IS FOR. v1's set is 44 frames of which 44 are figure-free and 44 stand
on grass, and all three failing bars trace to exactly those two facts
(`pipeline/lora/registry.yaml` `bars_result`). These eight frames carry BOTH a
figure and a non-grass rooting surface, which is the only kind of frame the set
has never had.

THE PLANT'S PLACEMENT IS THE THIRD VARIABLE AND IT IS FREE. The plate fixes the
figure's distance (the skeleton) and the ground (the words). Where the plant is
ROOTED costs nothing and is what supplies the axis the plates cannot: which
SIDE of the figure the plant is on, and how big it is against him. All three
depth cells sit at cx 0.655, so the figure's own side does not vary in this
batch -- that limit is recorded in the deriver -- and the plant's side is what
carries it here. Four cells put the plant left of him, four right.

THE AIMING LAWS ARE v1'S, CARRIED, and they were paid for there:
  * roots sit OFF the bottom edge (y 1080..1180 here). The near-foreground band
    is the darkest part of a plate while the palette is sampled from brighter
    ground higher up, so a plant rooted at the very bottom is built out of
    colours that do not belong where it stands -- C5 fires.
  * leaf-frac stays in 0.47..0.58 for every row. Leaf length as a fraction of
    stem is a property OF THE PLANT; shrinking it at scale draws a different
    species rather than the same sapling seen closer.
  * tall plants sit away from the frame edge, because the leaves reach 0.5 of
    the stem sideways and C3 fires when they leave the canvas.

AND ONE LAW THIS BATCH ADDS, WHICH v1 NEVER NEEDED. THE PLANT MUST NOT TOUCH
THE FIGURE. v1 had no figure to touch. `--body-box` is what the compositor
offers for it and every row below passes one: the figure's silhouette box,
read off the plate, which the tool keeps the drawn plant clear of. A plant
overlapping him in nearly his own colour is the exact configuration beat 16
measured as the worst case, and a dataset frame where the plant and the goblin
share pixels would teach the fusion this whole batch exists to unteach.

$0. numpy + PIL through beat16_sapling_composite.py. No model, no network, no
GPU. Deterministic -- same inputs, same shas.

  python3 pipeline/build_saplora_figcomp_0822.py --dry-run
  python3 pipeline/build_saplora_figcomp_0822.py --write
  python3 pipeline/build_saplora_figcomp_0822.py --sheet
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(REPO, "pipeline", "beat16_sapling_composite.py")
OUT = "farm-out/ep3-saplora-figinit-0822"
OVERLAY = "farm-out/ep3-saplora-figovl-0822"

# cell -> the published plate and its sha256, taken from the producing job's
# own `.sha256` manifest. THAT MANIFEST IS THE AUTHORITY, not a locally
# recomputed hash: macOS is case-insensitive and a contact sheet written over
# an extracted frame is how a src-sha mismatch was manufactured on 2026-08-22.
PLATES = {
    "g1": ("farm-out/ep3-saplora-figg1-0822/ep3-saplora-figg1-0822-ipahead.png",
           "9d1dff2a335c458ace7bdb673341def4b45f004102b2f4fd20388b4d3560f1cc"),
    "g2": ("farm-out/ep3-saplora-figg2-0822/ep3-saplora-figg2-0822-ipahead.png",
           "d68c23a668fae559ede3336d82f83255d6a0777793cd4e3aece84499528d4697"),
    "g3": ("farm-out/ep3-saplora-figg3-0822/ep3-saplora-figg3-0822-ipahead.png",
           "b014bc98d6b7851f637640f2308df8950b2d1825a7308141b0eb77c3879de8ba"),
    "g4": ("farm-out/ep3-saplora-figg4-0822/ep3-saplora-figg4-0822-ipahead.png",
           "9f5b37876dd128faf7979bd1b70b82be6dac2e11839f81ae79e6a004296cb627"),
    "g5": ("farm-out/ep3-saplora-figg5-0822/ep3-saplora-figg5-0822-ipahead.png",
           "6ba7f77f9ef153f01ff2d4935e142fd5587733f54ef922a5e545a1995faa2e1c"),
    "g6": ("farm-out/ep3-saplora-figg6-0822/ep3-saplora-figg6-0822-ipahead.png",
           "af323b9ff1fba2b6239784e982e0b8e820df8cdf3afb768cb291a9458a3fdf85"),
    "g7": ("farm-out/ep3-saplora-figg7-0822/ep3-saplora-figg7-0822-ipahead.png",
           "612a2b82dcc9adfccd9ba54e6ec14a4dda8ab8c02103bb8b131f9ea68b4c5b49"),
    "g8": ("farm-out/ep3-saplora-figg8-0822/ep3-saplora-figg8-0822-ipahead.png",
           "c1aa49eb3b92bf86c2fe35eaf36089557b322f0d7d8a0897f61a5420791b58a8"),
}

# cell -> the figure's silhouette box "x0,y0,x1,y1" in plate pixels, READ OFF
# THE PLATE at 1:1 and passed to --body-box so the drawn plant is kept clear of
# him. Generous on purpose: a box that is too big costs a little rootable
# ground, a box that is too small costs the frame.
BODY = {
    "g1": "140,0,710,1216",
    "g2": "250,120,580,1010",
    "g3": "300,150,545,1030",
    "g4": "330,180,520,940",
    "g5": "290,130,560,1020",
    "g6": "320,150,540,1000",
    "g7": "300,160,530,1050",
    "g8": "300,120,560,1010",
}

# cell, tier, root x,y, stem height px, tilt deg, leaf-frac, leaf-spread, side
#
# TIERS ARE PICKED OFF THE COMBINED SET'S THIN END, not spread evenly. With the
# eight harvested ep2 frames measured at l=5, m=1, xl=2, the figure half of the
# set is already heavy at the large end, so these rows lean small and medium:
# s=2, m=3, l=2, xl=1.
#
# FOUR OF THESE EIGHT ROWS WERE MOVED BY A CHECK AND NOT BY AN EYE, and the
# first table is kept in this comment because what refused it is the finding:
#
#   g1  (95,1180) h300  -> C3, THE PLANT TOUCHES THE FRAME EDGE. g1 is the
#       full-span `crouch` sample whose body box spans x 140..710, so its only
#       rootable ground is the two frame edges and a plant whose leaves reach
#       half its stem sideways runs off the canvas. It is rescued on the RIGHT
#       edge as a 150 px sprout -- and only as a sprout. This is the same
#       fault the plate's own verdict predicted, arriving one step later.
#   g3  (620,1160) -> C5 by 50.2 (tol 46). g4 (240,1120) -> C5 by 48.0.
#       BOTH ARE THE SAME MECHANISM AND IT IS THE ONE THIS BATCH WAS ALWAYS
#       GOING TO MEET: on a BRIGHT PALE non-grass ground, the only
#       green-dominant pixels are dark vegetation in shadow, so the plant is
#       built out of dark greens while the field mean is a bright pale surface.
#       A green plant on bright sand reads as pasted, and C5 says so before a
#       GPU second is spent. Both are fixed by moving the root, not by relaxing
#       the tolerance: g3 to x560 where the path's own verge lifts the sample
#       (n 9,593 -> 11,343), g4 to the darker upper-left of the rock slab.
#   The positions below are the ones that PASS all five checks, found by a
#   root sweep that cost nothing because this step has no model in it.
#
# LEAF-FRAC WAS NOT TRADED TO SAVE g1, and that is the one place this table
# refused to bend. lf 0.45 puts the plant inside the frame at h200; 0.47 does
# not. But leaf length as a fraction of stem is a property OF THE PLANT -- v1's
# second pass established that shrinking it at scale draws a bean sprout on a
# bare whip rather than the same sapling seen closer -- so the HEIGHT came down
# to 150 px at lf 0.55 instead, which is a smaller sapling and not a different
# one. One frame is not worth a species.
#
# cell, tier, root x,y, stem height px, tilt deg, leaf-frac, leaf-spread, side
ROWS = [
    ("g1", "s",  (745, 1170), 150, -5.0, 0.55, 65.0, "right edge"),
    ("g2", "l",  (200, 1150), 520,  6.0, 0.50, 62.0, "left"),
    ("g3", "m",  (560, 1180), 300, -6.0, 0.52, 64.0, "right"),
    ("g4", "s",  (120, 1090), 180,  5.0, 0.56, 70.0, "left"),
    ("g5", "l",  (640, 1140), 500, -4.0, 0.50, 61.0, "right"),
    ("g6", "s",  (180, 1100), 180,  6.0, 0.56, 69.0, "left"),
    ("g7", "m",  (600, 1130), 320, -5.0, 0.52, 64.0, "right"),
    ("g8", "xl", (250, 1170), 620,  5.0, 0.48, 57.0, "left"),
]

# g7 IS FLAGGED, NOT QUIETLY SHIPPED. Its palette sampled ONE green-dominant
# pixel -- the whole-lower-half fallback found no more -- so the plant is drawn
# as a single flat olive (100,105,85) with no light/dark separation at all.
# A chroma-floor sweep from 0.15 down to 0.02 does not move the number, so this
# is not the tuning knob it looks like: g7's forest floor is genuinely brown
# and its ferns are desaturated past the point of being green-dominant. It
# passes C5 (a flat plant cannot disagree with the field) and it is a decal by
# construction, which C5 is not built to catch. It is kept through step 3
# because the 0.30 pass re-shades what it is handed and may simply fix it, and
# it is JUDGED AFTER that pass rather than before. If it still reads flat it is
# dropped from the manifest. The reading travels with the frame either way.
FLAT_PALETTE = {"g7": 1}


def run(row, write: bool, extra=None):
    cell, tier, (rx, ry), h, tilt, lf, ls, side = row
    plate, sha = PLATES[cell]
    argv = [sys.executable, TOOL,
            "--plate", plate,
            "--root", "%d,%d" % (rx, ry),
            "--height", str(h),
            "--tilt", str(tilt),
            "--leaf-frac", str(lf),
            "--leaf-spread", str(ls),
            "--body-box", BODY[cell],
            "--green-sat-floor", "0.15"]
    if sha:
        argv += ["--plate-sha256", sha]
    if write:
        argv += ["--out", os.path.join(REPO, OUT, "sapfig-%s-0822.png" % cell),
                 "--mask-out", os.path.join(REPO, OUT,
                                            "sapfig-%s-mask-0822.png" % cell),
                 "--overlay-out", os.path.join(REPO, OVERLAY,
                                               "ovl-%s-0822.png" % cell)]
    else:
        argv += ["--dry-run"]
    argv += list(extra or [])
    # encoding= is not optional here: test_pipeline.py enforces that every
    # text-mode subprocess read names one, because text=True alone decodes with
    # the platform default and the box is Windows (cp1252) while the lanes are
    # macOS (utf-8). Added 2026-08-22 by the sapling-LoRA lane, which does not
    # own this file -- the gate was red on main and two lanes' pushes were
    # blocked behind it. No behaviour of this script is changed and no judgement
    # of its author's is overridden; the keyword is the one the committed test
    # prescribes.
    r = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--only", help="comma-separated cell ids")
    a = ap.parse_args()

    rows = ROWS
    if a.only:
        want = set(a.only.split(","))
        rows = [r for r in ROWS if r[0] in want]

    if a.write:
        os.makedirs(os.path.join(REPO, OUT), exist_ok=True)
        os.makedirs(os.path.join(REPO, OVERLAY), exist_ok=True)

    bad = 0
    for row in rows:
        r = run(row, write=a.write)
        head = "%-3s %-3s root=%-10s h=%-4d %s" % (
            row[0], row[1], "%d,%d" % row[2], row[3], row[7])
        if r.returncode:
            bad += 1
            tail = (r.stderr or r.stdout).strip().split("\n")[-3:]
            print("!! %s  REFUSED rc=%d" % (head, r.returncode))
            for t in tail:
                print("     %s" % t)
        else:
            keep = [l for l in (r.stdout or "").split("\n")
                    if any(k in l for k in ("palette", "C5", "fill luma",
                                            "n_sampled", "extent", "OK"))]
            print("   %s  ok" % head)
            for l in keep[:3]:
                print("     %s" % l.strip())
    print("\n%d row(s), %d refused" % (len(rows), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
