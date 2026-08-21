#!/usr/bin/env python3
r"""STEP 2 of the sapling LoRA dataset: draw the canon sapling onto the
goblin-free ground planes at VARIED geometry, once per dataset frame.

WHY A TABLE AND NOT TWENTY-FOUR COMMAND LINES. `pipeline/lora/README.md` gates
the sapling dataset on VARIETY, not count -- ">=20 composited saplings spanning
distinct scenes, scales and lighting", with scale and leaf count kept as caption
VARIABLES because the protagonist grows 15 cm -> 1.6 m across seven episodes and
one LoRA has to serve all of him. The ~23 composites that already exist share
five near-identical tall-grass scenes and carry the scavenger in every frame, so
they fail the gate on both axes at once. This file is the axis sweep: ten
distinct plates (`review/ep3-sapling-dataset-0821/plates-0821.yaml`), four scale
tiers, varied root position, tilt, leaf length fraction and leaf spread.

WHY THE GEOMETRY IS TYPED HERE RATHER THAN SOLVED. The root point has to sit on
a DRAWABLE GROUND PLANE, and where that plane starts is different in every
plate -- y~200 in u01's open field, y~1040 in u03 where the only rootable strip
is a foreground ridge. That is a judgement about a picture, so it is made by
looking at the picture and written down, and `--overlay-out` on every row is how
it was checked before a single init was written.

WHAT IT DOES NOT DO. It draws TWO leaves, every row, because
`beat16_sapling_composite.py` draws the canon two-leaf sapling and there is no
tool in this repo that adds a third. `leaf_count_composite.py` REMOVES leaves
from a plate that has too many; it cannot add them to a plate that has none. So
LEAF COUNT IS NOT VARIED BY THIS BATCH -- it is carried as an explicit caption
token so it is never baked into the trigger, and the honest gate reading is
recorded in `manifest-sapling.yaml`: the scale axis is swept, the leaf-count
axis is stated-but-constant and wants a second tool before a v2.

SCALE IS APPARENT SIZE IN FRAME, and the captions say so in those words rather
than asserting a centimetre figure the drawing cannot support. Two cotyledons on
one bare stem is the 001 (~15 cm) and 002 (~40 cm) rows of the growth ladder in
`genomes/sapling/style.md`; the ladder's 90 cm row has five or six leaves and a
crown. A frame captioned "90 cm" that shows two cotyledons would teach the LoRA
that 90 cm looks like a sprout, which is the exact failure the caption-variable
rule exists to prevent. So the large rows are captioned as what they are: the
same young two-leaf sapling seen CLOSE, filling the frame.

$0. numpy + PIL through beat16_sapling_composite.py. No model, no network, no
GPU. Deterministic -- same inputs, same shas.

  python3 pipeline/build_sapling_lora_composites_0821.py --dry-run
  python3 pipeline/build_sapling_lora_composites_0821.py --write
  python3 pipeline/build_sapling_lora_composites_0821.py --sheet   # contact sheet
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(REPO, "pipeline", "beat16_sapling_composite.py")
PLATES = "farm-out/ep3-sapling-dataset-0821/plates"
# ONE SEGMENT UNDER farm-out/, ON PURPOSE. derive_fetch_guard's URL
# regex is `farm-out/[A-Za-z0-9._-]+/` -- it reads exactly one path
# segment, so an init at farm-out/<set>/init/<file> makes the guard
# report the wrong directory and refuse. The convention is flat and
# this batch follows it rather than loosening the regex.
OUT = "farm-out/ep3-saplora-init-0821"
OVERLAY = "farm-out/ep3-sapling-dataset-0821/overlay"

# Scene descriptors, one per plate. These are what the captions' SCENE and
# LIGHT clauses are written from, and they are what the gate counts as
# "distinct scenes / distinct lighting".
SCENES = {
    "u01": dict(plate="ep3-sapfld4-u01-0821.png",
                scene="open green meadow, distant low hills, clear sky",
                light="flat overhead daylight, soft shadows",
                ground="the whole frame below the horizon at y~200"),
    "u02": dict(plate="ep3-sapfld4-u02-0821.png",
                scene="rolling grassland at sunset, golden terraced slopes",
                light="low warm backlight, long shadows, orange sky",
                ground="near grass band from y~860"),
    "u03": dict(plate="ep3-sapfld4-u03-0821.png",
                scene="misty green hills at dawn, valley fog below",
                light="cool pale dawn light, low contrast",
                ground="foreground grass ridge from y~1040"),
    "u04": dict(plate="ep3-sapfld4-u04-0821.png",
                scene="dark green hills under a heavy overcast sky",
                light="grey overcast, no cast shadow, muted colour",
                ground="near slope from y~960"),
    "r05": dict(plate="ep3-sapfld2-r05-0821.png",
                scene="steep grassy hillside falling away to a valley",
                light="hard midday sun, the slope half in its own shadow",
                ground="the slope face, lower left"),
    "p09": dict(plate="ep3-sapfield-p09-0821.png",
                scene="wildflower meadow, daisies scattered through the grass",
                light="bright even daylight, pale sky",
                ground="the whole meadow below y~300"),
    "u06": dict(plate="ep3-sapfld4-u06-0821.png",
                scene="alpine valley, snow-capped mountains, cumulus sky",
                light="bright clear midday, high contrast",
                ground="valley-floor grass from y~1000"),
    "u07": dict(plate="ep3-sapfld4-u07-0821.png",
                scene="inside a summer wood, tree trunks and canopy",
                light="dappled sunlight through leaves, green bounce",
                ground="forest floor from y~920"),
    "u08": dict(plate="ep3-sapfld4-u08-0821.png",
                scene="dirt path running through a forest avenue",
                light="even bright daylight, pale sky down the avenue",
                ground="path and verges from y~960"),
    "t04": dict(plate="ep3-sapfld3-t04-0821.png",
                scene="green field below distant misty mountains",
                light="pale lilac dawn, soft diffuse light",
                ground="near field from y~1020"),
    "r08": dict(plate="ep3-sapfld2-r08-0821.png",
                scene="sunlit clearing path between dark trees",
                light="strong backlight down the avenue, deep shade at the edges",
                ground="path from y~1000"),
}

# tier -> the caption's SCALE clause. Four tiers, and they are apparent size in
# frame, not a centimetre claim the two-leaf drawing cannot support.
TIERS = {
    "s": "a tiny sprout, small in a wide frame, far from the camera",
    "m": "a small sapling at middle distance",
    "l": "a young sapling standing clear of the grass, mid-frame",
    "xl": "close to the camera and large in frame, the subject of the shot",
}

# id, plate key, tier, root x,y, stem height px, tilt deg, leaf-frac, leaf-spread
#
# EVERY ROOT WAS AIMED, NOT GUESSED. The first pass of this table put 12 of 24
# rows into a FAIL, and the two failures say something about the plates that is
# worth keeping. C3 (plant off the frame edge) fires whenever a tall plant is
# rooted past x~560 -- the leaves are 0.4-0.6 of the stem and they go sideways.
# C5 (the plant's fill luma disagrees with the field's) fires almost everywhere
# at y>1180: the near-foreground band of these plates is the DARKEST part of the
# picture, while the palette is sampled from the brighter grass higher up, so a
# plant rooted at the very bottom edge is built out of colours that do not
# belong where it stands. Roots therefore sit at y 900-1160, not on the bottom
# edge, and tall plants sit left of centre.
#
# THE SECOND PASS FIXED A DIFFERENT THING, AND IT WAS NOT A CHECK THAT CAUGHT
# IT -- 26 of 26 passed and the contact sheet was still wrong. The first table
# LOWERED --leaf-frac as height rose (0.58 at h150 down to 0.40 at h820), which
# is not a camera move: leaf length as a fraction of stem is a property OF THE
# PLANT, so shrinking it at scale draws a different species -- a bean sprout on
# a bare whip -- rather than the same sapling seen closer. The ratified b16
# composite is 0.46 at h620 and that is the shape the founder screened. Leaf
# frac now stays in 0.47-0.58 for every row, wider at the small end where canon
# 001 says the cotyledons are OVERSIZED, and the tall rows lose height instead
# (660 not 820) because C3 is what was really forcing the thin leaves.
ROWS = [
    ("s01", "u01", "s",  (300,  900),  150, -5.0, 0.58, 70.0),
    ("s02", "u01", "l",  (416, 1120),  470,  7.0, 0.50, 60.0),
    ("s03", "u01", "xl", (416, 1180),  660, -4.0, 0.48, 55.0),
    ("s04", "u02", "m",  (250, 1150),  300,  5.0, 0.52, 64.0),
    ("s05", "u02", "xl", (560, 1190),  640, -6.0, 0.48, 58.0),
    ("s06", "u03", "m",  (520, 1160),  230,  8.0, 0.54, 68.0),
    ("s07", "u03", "l",  (330, 1195),  560, -5.0, 0.49, 60.0),
    ("s08", "u04", "m",  (290, 1060),  280, -7.0, 0.52, 62.0),
    ("s09", "u04", "xl", (340, 1120),  650,  6.0, 0.47, 56.0),
    ("s10", "u06", "m",  (300, 1130),  240,  5.0, 0.53, 67.0),
    ("s11", "u06", "xl", (500, 1195),  620, -6.0, 0.49, 59.0),
    ("s12", "u07", "s",  (290, 1130),  200, -4.0, 0.56, 71.0),
    ("s13", "u07", "l",  (416, 1130),  520,  7.0, 0.50, 62.0),
    ("s14", "u08", "s",  (416, 1060),  190,  6.0, 0.55, 69.0),
    ("s15", "u08", "m",  (540, 1060),  300,  4.0, 0.52, 64.0),
    ("s16", "u08", "l",  (380, 1130),  560, -5.0, 0.50, 60.0),
    ("s17", "t04", "m",  (540, 1130),  260, -6.0, 0.51, 65.0),
    ("s18", "t04", "xl", (340, 1150),  640,  5.0, 0.48, 57.0),
    ("s19", "r08", "s",  (416, 1060),  170,  4.0, 0.57, 70.0),
    ("s20", "r08", "m",  (540,  980),  250, -5.0, 0.51, 66.0),
    ("s21", "r08", "l",  (400, 1130),  500, -7.0, 0.50, 63.0),
    ("s22", "r05", "s",  (290, 1000),  180,  6.0, 0.56, 70.0),
    ("s23", "r05", "l",  (330, 1195),  520, -5.0, 0.49, 61.0),
    ("s24", "p09", "s",  (416,  920),  200,  5.0, 0.55, 69.0),
    ("s25", "p09", "m",  (600, 1020),  320, -4.0, 0.52, 65.0),
    ("s26", "p09", "l",  (400, 1060),  580, -6.0, 0.49, 59.0),
]


def run(row, write: bool):
    fid, pk, tier, (rx, ry), h, tilt, lf, ls = row
    plate = os.path.join(PLATES, SCENES[pk]["plate"])
    argv = [sys.executable, TOOL,
            "--plate", plate,
            "--root", "%d,%d" % (rx, ry),
            "--height", str(h),
            "--tilt", str(tilt),
            "--leaf-frac", str(lf),
            "--leaf-spread", str(ls)]
    if write:
        argv += ["--out", os.path.join(REPO, OUT, "sap-%s-%s-0821.png" % (fid, pk)),
                 "--mask-out", os.path.join(REPO, OUT, "sap-%s-%s-mask-0821.png" % (fid, pk)),
                 "--overlay-out", os.path.join(REPO, OVERLAY, "ov-%s-%s.png" % (fid, pk))]
    else:
        argv += ["--dry-run"]
    p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=REPO)
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sheet", action="store_true",
                    help="build contact sheets of the written inits/overlays")
    a = ap.parse_args()

    if a.sheet:
        return sheet()

    os.makedirs(os.path.join(REPO, OUT), exist_ok=True)
    os.makedirs(os.path.join(REPO, OVERLAY), exist_ok=True)
    bad = 0
    for row in ROWS:
        rc, out = run(row, a.write)
        keep = [l for l in out.splitlines()
                if l.startswith(("FAIL", "!!", "plant extent", "all checks"))]
        print("%-4s %-4s rc=%d  %s" % (row[0], row[1], rc, " | ".join(keep)))
        if rc:
            bad += 1
    print("\n%d/%d rows failed" % (bad, len(ROWS)))
    return 1 if bad else 0


def sheet() -> int:
    from PIL import Image, ImageDraw
    for kind, d, pat in (("init", OUT, "sap-%s-%s-0821.png"),
                         ("overlay", OVERLAY, "ov-%s-%s.png")):
        imgs = []
        for row in ROWS:
            p = os.path.join(REPO, d, pat % (row[0], row[1]))
            if os.path.isfile(p):
                imgs.append(("%s %s h%d" % (row[0], row[1], row[4]), p))
        if not imgs:
            continue
        cols, cw, ch = 6, 278, 406
        rows_n = (len(imgs) + cols - 1) // cols
        s = Image.new("RGB", (cols * cw, rows_n * (ch + 20)), (18, 18, 18))
        dr = ImageDraw.Draw(s)
        for i, (lbl, p) in enumerate(imgs):
            im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
            x, y = (i % cols) * cw, (i // cols) * (ch + 20)
            s.paste(im, (x, y))
            dr.text((x + 5, y + ch + 4), lbl, fill=(255, 240, 120))
        out = os.path.join(REPO, "review/ep3-sapling-dataset-0821",
                           "CONTACT-%s-0821.png" % kind)
        s.save(out)
        print("wrote %s (%d cells)" % (out, len(imgs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
