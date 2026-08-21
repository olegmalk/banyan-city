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
    # ---- ROUND 5 / v2, added 2026-08-21. THE NON-DAYLIT HALF OF THE LIGHTING
    # ---- AXIS. Every plate above is DAY -- the eleven lightings v1 carries are
    # flat daylight, sunset backlight, dawn mist, heavy overcast, alpine midday,
    # forest dapple, even daylight, pale dawn, strong backlight, hard midday sun
    # and bright daylight -- so a LoRA trained on v1 alone learns a time of day
    # into `bnysapling`. These four are what survived the round-5 bar out of
    # fourteen; the ten that did not, and why, are in
    # review/ep3-sapling-dataset-0821/plates-0821.yaml under round_5_result.
    "v02": dict(plate="ep3-sapfld5-v02-0821.png",
                scene="a green meadow at night, distant hills, moonlit slope",
                light="cool moonlight, blue darkness, a pale rim on the slope",
                ground="the moonlit slope from y~800; tall blades from y~1050"),
    "v03": dict(plate="ep3-sapfld5-v03-0821.png",
                scene="a green plain under storm cloud, a shaft of light beyond",
                light="dark storm sky, one bright shaft, a luminous horizon band",
                ground="the flat green plane from y~950. DARK LANDFORM WEDGES "
                       "sit in both bottom corners -- roots stay in x 280..680"),
    "v05": dict(plate="ep3-sapfld5-v05-0821.png",
                scene="a wet green moor in the rain, receding grey hills",
                light="flat rain light, grey-teal, no cast shadow",
                ground="the near moor band from y~950"),
    "v12": dict(plate="ep3-sapfld5-v12-0821.png",
                scene="a green plain after rain, puddles, breaking cloud",
                light="bright breaking cloud, wet specular puddles",
                ground="green lobes BETWEEN the puddles, y~850..1216"),
    # ---- ROUND 6 / v3, added 2026-08-21. Two plates out of a four-cell WORD
    # ---- PROBE, not a breadth batch: each cell deleted one suspect word from a
    # round-5 failure. w03 is the control (moonlight, already known to work) and
    # it is the greenest plate the set has ever had; w02 is the one that moved
    # the finding -- `golden hour` deleted from v04, the warm light kept, and
    # the tan macro grass did not come back. w01 (dusk, grey key) REFUSED at
    # this tool with ZERO green-dominant pixels and w04 (cold light, no season
    # word) came back a snowfield; both are judged in plates-0821.yaml.
    # THE SCENE AND LIGHT STRINGS ARE A CLIP BUDGET, NOT PROSE. Step 3 builds
    # its prompt out of them and assert_under_clip77 REFUSED the first draft of
    # both of these -- w03 at 80 and w02 at 81 against 77 -- before a spec was
    # written. `cool blue key` and `a tall ... beyond` came off w03,
    # `low sun behind thin cloud` and `distant hills` off w02, because the
    # picture already says them and the sun disc is in the scene clause.
    "w03": dict(plate="ep3-sapfld6-w03-0821.png",
                scene="a green meadow at night, distant hills, a moonlit "
                      "cumulus",
                light="moonlight through broken cloud, patches of shadow",
                ground="the open emerald plane from y~880, the cleanest in the "
                       "set -- no rock, no puddle, no wedge"),
    "w02": dict(plate="ep3-sapfld6-w02-0821.png",
                scene="rolling green downland, a low sun on the horizon",
                light="warm diffuse backlight, lit blade tips, shadowed slopes",
                ground="the lit crest from y~940. THE WHOLE FOREGROUND IS A "
                       "BLADED SWARD -- the small tier would be swallowed by "
                       "it, so this plate carries m/l/xl only"),
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
    # ---- ROUND 5 / v2. Same aiming laws as above (roots off the bottom edge,
    # tall plants left of centre), plus one this round added: on v03 the root
    # also stays clear of the dark landform wedges in the bottom corners, and
    # on v12 it stays on a green lobe rather than in a puddle -- a root in
    # standing water is a structure the 0.30 pass would preserve underneath the
    # plant. Every row below was dry-run before it was written and the palette
    # line was read: v02 samples 34k-176k green px, v03 10k-97k, v12 48k-251k.
    # v05 samples THIRTY-NINE, from the whole-lower-half fallback, and it is
    # kept deliberately with that number recorded -- see plates-0821.yaml.
    ("s27", "v02", "s",  (300,  950),  180,  6.0, 0.56, 70.0),
    ("s28", "v02", "m",  (330, 1000),  300,  6.0, 0.52, 64.0),
    ("s29", "v02", "xl", (360, 1090),  620, -5.0, 0.48, 57.0),
    ("s30", "v03", "s",  (400,  990),  200,  5.0, 0.55, 69.0),
    ("s31", "v03", "m",  (330, 1080),  260, -6.0, 0.52, 64.0),
    ("s32", "v03", "xl", (500, 1150),  560,  5.0, 0.49, 60.0),
    ("s33", "v12", "s",  (150,  900),  190, -4.0, 0.55, 69.0),
    ("s34", "v12", "m",  (300, 1120),  300, -5.0, 0.52, 64.0),
    ("s35", "v12", "l",  (200, 1160),  500,  6.0, 0.50, 62.0),
    ("s36", "v05", "s",  (300,  980),  170,  4.0, 0.57, 70.0),
    ("s37", "v05", "l",  (480, 1140),  420, -6.0, 0.50, 61.0),
    # ---- ROUND 6 / v3. TIERS ARE CHOSEN OFF THE MANIFEST'S OWN THIN END, not
    # spread evenly: v2 is s=10 m=11 l=9 xl=7, so l and xl are what seven new
    # frames should buy. w03's plane is clean enough to carry all four tiers;
    # w02 gets m/l/xl only because its foreground is a bladed sward and a
    # 180px sprout in it is a plant behind a fence, not a plant in a field.
    # s38 was aimed at (300,950) first and C5 REFUSED it: the palette sampled
    # 205.2 fill luma against a 142.2 field, because w03's plane is a moonlit
    # gradient that darkens UPHILL and a sprout rooted high is built out of the
    # brighter greens further down. Dropped to y1080 -- the sample goes 14.9k ->
    # 25.7k px and the luma agrees. Same law as the v1 table's bottom-edge
    # finding, arriving from the other end of the plate.
    ("s38", "w03", "s",  (280, 1080),  180,  5.0, 0.56, 70.0),
    ("s39", "w03", "m",  (330, 1050),  300, -6.0, 0.52, 64.0),
    ("s40", "w03", "l",  (400, 1130),  500,  6.0, 0.50, 62.0),
    ("s41", "w03", "xl", (360, 1160),  640, -5.0, 0.48, 57.0),
    ("s42", "w02", "m",  (300, 1000),  280,  5.0, 0.52, 64.0),
    ("s43", "w02", "l",  (350, 1130),  490, -6.0, 0.50, 61.0),
    ("s44", "w02", "xl", (380, 1160),  630,  5.0, 0.48, 57.0),
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
    ap.add_argument("--fids", default=None,
                    help="comma-separated frame ids to run (default: all). "
                         "THE v1 ROWS ARE ALREADY DRAWN AND THEIR SHAS ARE "
                         "ASSERTED BY TWENTY-SIX COMMITTED JOB SPECS, so a v2 "
                         "round runs --fids s27,... rather than rewriting "
                         "inits the box has already conditioned on.")
    a = ap.parse_args()

    if a.sheet:
        return sheet(a.fids.split(",") if a.fids else None)

    want = set(a.fids.split(",")) if a.fids else None
    if want:
        known = {r[0] for r in ROWS}
        unknown = sorted(want - known)
        if unknown:
            print("!! --fids names rows that are not in the table: %s"
                  % ", ".join(unknown))
            return 1

    os.makedirs(os.path.join(REPO, OUT), exist_ok=True)
    os.makedirs(os.path.join(REPO, OVERLAY), exist_ok=True)
    bad = 0
    rows = [r for r in ROWS if want is None or r[0] in want]
    for row in rows:
        rc, out = run(row, a.write)
        keep = [l for l in out.splitlines()
                if l.startswith(("FAIL", "!!", "plant extent", "all checks"))]
        print("%-4s %-4s rc=%d  %s" % (row[0], row[1], rc, " | ".join(keep)))
        if rc:
            bad += 1
    print("\n%d/%d rows failed" % (bad, len(rows)))
    return 1 if bad else 0


def sheet(fids=None) -> int:
    from PIL import Image, ImageDraw
    want = set(fids) if fids else None
    for kind, d, pat in (("init", OUT, "sap-%s-%s-0821.png"),
                         ("overlay", OVERLAY, "ov-%s-%s.png")):
        imgs = []
        for row in [r for r in ROWS if want is None or r[0] in want]:
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
        # A FILTERED SHEET GETS ITS OWN NAME. Writing a 11-cell subset over
        # CONTACT-init-0821.png would replace the 26-cell record of v1 with a
        # picture that looks like the whole dataset and is not.
        # AND EVERY FILTERED SHEET GETS A DIFFERENT ONE. `-subset` was a
        # constant, so round 6's 7-cell sheet would have silently overwritten
        # round 5's 11-cell sheet -- the same clobber one level down from the
        # one this comment was written about, and harder to notice because
        # `review/**/*.png` is gitignored, so these sheets exist ONLY in the
        # working tree and an overwrite is not recoverable from git. The name
        # now carries the first and last fid in the filter.
        tag = ""
        if want:
            fids_seen = [r[0] for r in ROWS if r[0] in want]
            tag = "-%s" % fids_seen[0] if len(fids_seen) == 1 else \
                  "-%s-%s" % (fids_seen[0], fids_seen[-1])
        out = os.path.join(REPO, "review/ep3-sapling-dataset-0821",
                           "CONTACT-%s%s-0821.png" % (kind, tag))
        s.save(out)
        print("wrote %s (%d cells)" % (out, len(imgs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
