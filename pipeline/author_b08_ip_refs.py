#!/usr/bin/env python3
r"""Author beat 08's TWO IP-ADAPTER IDENTITY REFERENCES — crops, pure PIL.

WHY THIS EXISTS. `b08-arm-route-0819.md` §8-§10 closed three geometric axes and
left one blocker standing: FIVE rungs, three conditioning scales, two stroke
weights and two hint classes all returned TWO GREEN FIGURES. A contour says how
tall, not which body an attribute belongs to, so `green skin` enters CLIP's
pooled embedding and lands on both. The research file
`pipeline/research/openpose-controlnet-sdxl-0819.md` §5 names the lever and
verifies it is already on the box at $0: masked IP-Adapter, one reference image
per figure, one binary mask per reference, composed into the same SDXL ControlNet
pipeline. A reference image is a per-LOCATION identity channel, which is exactly
what the hint cannot be.

WHY BOTH CROPS COME FROM ONE PLATE, AND WHY IT IS THIS PLATE.
`farm-out/ep2-b08-boardcomp-0818/08-boardlowered-comp-0818.png` is beat 08's own
signed board-lowered composite: B1, B2, B3 and B5 all PASSED on it (mean |diff|
10.61 inside the mask, 0.04 outside, 231 px of the untouched 80% differing by
more than 8 levels). It holds BOTH characters, standing, adjacent, at one
exposure, in one line weight, under one sky. So the ONLY difference between the
two references is the identity itself -- which is the variable being tested. Two
references cut from two different plates would also differ in lighting, palette
and rendering, and any identity separation could be that instead.

TWO OTHER CANDIDATES WERE OPENED AND REJECTED ON PIXELS, not on preference:

  farm-out/ep2-b14-mac-plate-0819/14-the-defense-mac-plate-r8s1.png -- the b14
  adult goblin. Rejected twice over. Its goblin is CROUCHING with the skull
  bowed toward camera, so as a `plus` reference (the fine-grained variant, which
  carries structure) it fights both the standing contour hint and the pose the
  beat needs. And the bowed crown catches a specular highlight that measures
  PALE PINK, so the reference would push the goblin's head AWAY from green --
  the opposite direction from the clause it is meant to fix.

  review/ep2-picks/goblin-reference-0814/s{1,2}-head*.png -- dedicated goblin
  head references. Rejected because they read CHILD: large eyes, small chin,
  chibi proportions. `chibi` and `child` are both in this beat's own negative
  prompt and B2's own wording is "an ADULT goblin", so these references would be
  arguing with the bar they were fetched to serve.

WHAT A REFERENCE CROP IS FOR HERE: HEAD AND SHOULDERS, and that is a decision
with two reasons. (1) B2 is scored on head hue, so the head is the payload.
(2) `ip-adapter-plus` carries structure as well as palette; a full-figure
reference would be a third structural instruction competing with the ControlNet
contour and the prompt. A head-and-shoulders crop of a standing figure carries
almost no pose. The guard's crop still reaches his brown cloak and cream
under-robe collar, so the frozen wardrobe is represented rather than absent.

SQUARE ON PURPOSE. CLIPImageProcessor resizes the short side to 224 and then
CENTRE-CROPS to 224x224. Feed it a 370x750 figure and the encoder throws away
the head and keeps the midriff -- silently, with no error and no visible sign in
any sidecar. Both boxes below are exactly 370x370, and --selftest asserts it.

    python3 pipeline/author_b08_ip_refs.py --out-dir pipeline/control
    python3 pipeline/author_b08_ip_refs.py --selftest     # no GPU, no weights
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The one plate both references are cut from. Its own verdict is in
# pipeline/jobs/ep2-b08-boardcomp-0818.yaml.
SOURCE = "farm-out/ep2-b08-boardcomp-0818/08-boardlowered-comp-0818.png"
SOURCE_SHA_PREFIX = "487ef4e8"    # as recorded in b08-arm-route-0819.md §3
SOURCE_SIZE = (832, 1216)

# THE CROPS, in source pixels. Both exactly 370x370 -- see the docstring on why
# squareness is load-bearing rather than tidy.
GUARD_BOX = (430, 120, 800, 490)     # bald human head, brown cloak, cream collar
GOBLIN_BOX = (60, 30, 430, 400)      # green head, pointed ears, teal robe collar

# WHERE THE IDENTITY IS MEASURED INSIDE EACH CROP, in SOURCE pixels. A 60x60 box
# on the cheek/brow, off the hair line and off the background, because the
# statistic below is a skin-hue statistic and a box that catches sky or cloth
# measures the sky or the cloth.
GUARD_FACE = (555, 180, 615, 240)
GOBLIN_FACE = (225, 115, 285, 175)

# THE GREEN BAND, MEASURED FROM SIX RENDERED RUNGS, NOT CHOSEN. `G - R` over a
# head region, the same statistic beat 08's verdicts have used since rung 1:
#
#   judged "green with pointed ears"  r1 gu +44.3  r1 go +38.8  r2 gu +34.0
#                                     r2 go +29.4  r4 gu +38.9  r4 go +38.3
#                                     r5 go +20.1            -> min +20.1
#   judged human-skinned              r3 gu -21.1  r5 gu -25.1 -> max -21.1
#
# Two classes, 41 levels of empty gap between them, over every frame this beat
# has produced. The band floor is +20.0 and the human ceiling is 0.0.
GREEN_BAND_FLOOR = 20.0
HUMAN_CEILING = 0.0
SEPARATION_MIN = 20.0


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mean_rgb(img, box):
    """Mean R, G, B over a box. The scoring instrument, in one place.

    Defined here rather than in the spec's prose so that the number in the
    reference's metadata and the number in the render's verdict come out of the
    same three lines of code.
    """
    c = img.crop(box).convert("RGB")
    n = float(c.size[0] * c.size[1])
    return tuple(round(s / n, 1) for s in
                 (sum(ch.histogram()[i] * i for i in range(256))
                  for ch in c.split()))


def green_excess(rgb):
    """G - R. Positive is green-skinned, negative is human-skinned."""
    return round(rgb[1] - rgb[0], 1)


def build(source=None):
    """Cut both references. Returns (guard_img, goblin_img, metadata)."""
    from PIL import Image

    src_path = Path(source) if source else REPO / SOURCE
    img = Image.open(src_path).convert("RGB")
    if img.size != SOURCE_SIZE:
        raise ValueError(
            "the source plate is %s but this tool's crop boxes were measured on "
            "%s. A resized plate moves every box." % (img.size, SOURCE_SIZE))

    guard = img.crop(GUARD_BOX)
    goblin = img.crop(GOBLIN_BOX)
    gu_face = mean_rgb(img, GUARD_FACE)
    go_face = mean_rgb(img, GOBLIN_FACE)

    meta = {
        "source": SOURCE,
        "source_size": "%dx%d" % SOURCE_SIZE,
        "guard_box": GUARD_BOX,
        "guard_size": "%dx%d" % guard.size,
        "guard_face_rgb": gu_face,
        "guard_green_excess": green_excess(gu_face),
        "goblin_box": GOBLIN_BOX,
        "goblin_size": "%dx%d" % goblin.size,
        "goblin_face_rgb": go_face,
        "goblin_green_excess": green_excess(go_face),
        "separation": round(green_excess(go_face) - green_excess(gu_face), 1),
    }
    return guard, goblin, meta


def selftest():
    """THE PRECONDITION FOR B2, ASSERTED BEFORE ANY PIXELS. No GPU, no weights."""
    fails = []

    def check(name, cond):
        print(("  ok   " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    src = REPO / SOURCE
    check("the source plate is the one b08-arm-route-0819.md signed off",
          src.exists() and sha256_file(src).startswith(SOURCE_SHA_PREFIX))

    guard, goblin, m = build()

    # THE ENCODER TRAP. CLIPImageProcessor resize-then-centre-crops to a square;
    # a tall crop loses its head with no error anywhere.
    check("the guard reference is SQUARE (%s)" % m["guard_size"],
          guard.size[0] == guard.size[1])
    check("the goblin reference is SQUARE (%s)" % m["goblin_size"],
          goblin.size[0] == goblin.size[1])
    check("both references are the same size, so neither is favoured by "
          "resolution", guard.size == goblin.size)
    check("both references are at least 224 px, the encoder's input side",
          min(guard.size) >= 224)

    # The two crops must not overlap, or one reference contains the other's
    # figure and the whole per-figure premise is gone.
    check("the two crops are disjoint in the source",
          GOBLIN_BOX[2] <= GUARD_BOX[0] or GUARD_BOX[2] <= GOBLIN_BOX[0])

    # THE PRECONDITION FOR B2. If the two references do not separate on the
    # instrument that will score the render, the sample cannot answer its
    # question and there is no point spending a GPU on it.
    gu, go = m["guard_green_excess"], m["goblin_green_excess"]
    check("the GUARD reference's face is outside the green band "
          "(G-R %+.1f <= %+.1f)" % (gu, HUMAN_CEILING), gu <= HUMAN_CEILING)
    check("the GOBLIN reference's face is on the green side "
          "(G-R %+.1f > 0)" % go, go > 0)
    check("the two references SEPARATE by at least %.1f levels on the scoring "
          "instrument (%.1f)" % (SEPARATION_MIN, m["separation"]),
          m["separation"] >= SEPARATION_MIN)

    # The band constants must stay ordered, or the bar reads backwards.
    check("the green band floor sits above the human ceiling",
          GREEN_BAND_FLOOR > HUMAN_CEILING)

    # A resized or substituted plate must RAISE, not silently re-cut.
    from PIL import Image
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "wrong.png"
        Image.new("RGB", (416, 608)).save(p)
        try:
            build(source=p)
            check("a source at the WRONG size is refused", False)
        except ValueError:
            check("a source at the WRONG size is refused", True)

    # Determinism, or the sha asserted at render time is a lie.
    import io
    b = []
    for _ in range(2):
        g2, o2, _ = build()
        buf = io.BytesIO()
        g2.save(buf, "PNG")
        buf2 = io.BytesIO()
        o2.save(buf2, "PNG")
        b.append(buf.getvalue() + buf2.getvalue())
    check("authoring is deterministic", b[0] == b[1])

    print(("SELFTEST FAIL: %d" % len(fails)) if fails else "SELFTEST PASS")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description="cut beat 08's two IP-Adapter refs")
    ap.add_argument("--out-dir", default=None,
                    help="directory for b08-ref-guard-0819.png and "
                         "b08-ref-goblin-0819.png")
    ap.add_argument("--source", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.out_dir:
        ap.error("--out-dir required (or --selftest)")

    guard, goblin, meta = build(a.source)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    gp = out / "b08-ref-guard-0819.png"
    op = out / "b08-ref-goblin-0819.png"
    guard.save(gp, "PNG")
    goblin.save(op, "PNG")
    for k, v in meta.items():
        print("  %s: %s" % (k, v))
    print("  guard_sha256: %s" % sha256_file(gp))
    print("  goblin_sha256: %s" % sha256_file(op))
    print("wrote %s and %s" % (gp, op))
    return 0


if __name__ == "__main__":
    sys.exit(main())
