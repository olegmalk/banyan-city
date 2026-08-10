#!/usr/bin/env python3
r"""Put frames side by side at one scale, labelled, and nothing else.

WHY THIS EXISTS AS A COMMITTED FILE. The sheets it writes go under `review/`,
which `.gitignore:60` (`review/**/*.png`) swallows -- so the SHEET is never
durable, only the frames it was built from (published to `farm-out/` and
force-pushed to `farm-results-rtx5090` by the courier on every job_done). A
comparison nobody can rebuild is a comparison nobody can check, so the recipe
lives here and the picture is regenerated from the durable frames on demand.

WHAT IT DELIBERATELY DOES NOT DO: score, rank, diff, or compute any similarity
number. The DINOv2 identity metric is disqualified in
taste/steward-model.ledger.yaml for calling four visibly different creatures one
creature (724b616, 93356b1), and the founder's standing rule is that a metric
agreeing with the steward is not a sample. This tool exists so a HUMAN EYE can
do the comparing at a fair scale -- equal widths, equal spacing, labels that say
which file each cell is.

Usage:
    python3 pipeline/compare_sheet.py <out.png> "<title>" "<label>=<path>" ...

Example (beat 14 against the founder's pick, 2026-08-11):
    python3 pipeline/compare_sheet.py review/COMPARE/GOBLIN-b14-facepick-0811.png \
      "beat 14 the-defense conditioned on HIS PICK" \
      "HIS PICK"=review/SHEETS/src-goblin/04-the-footnote-ipa-r1-w015-s6.png \
      "b14 s0"=<frame>.png ...
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CELL_W = 440
PAD = 16
LABEL_H = 34
TITLE_H = 62


def _font(size: int):
    # Fall back rather than fail: a sheet with the default bitmap face is still
    # a usable comparison, and a missing font must not cost a render's review.
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def build(out: Path, title: str, cells: list[tuple[str, str]]) -> int:
    ims = []
    for label, path in cells:
        im = Image.open(path).convert("RGB")
        # Equal WIDTH, not equal area: these frames are all 9:16 and unequal
        # scaling is how a comparison lies about size.
        h = round(im.height * CELL_W / im.width)
        ims.append((label, im.resize((CELL_W, h), Image.LANCZOS)))

    cell_h = max(im.height for _, im in ims)
    width = PAD + len(ims) * (CELL_W + PAD)
    height = TITLE_H + PAD + cell_h + LABEL_H + PAD

    sheet = Image.new("RGB", (width, height), (18, 18, 20))
    draw = ImageDraw.Draw(sheet)
    draw.text((PAD, 18), title, fill=(240, 240, 240), font=_font(26))

    x = PAD
    for label, im in ims:
        y = TITLE_H + PAD
        sheet.paste(im, (x, y))
        draw.rectangle([x - 1, y - 1, x + CELL_W, y + im.height],
                       outline=(90, 90, 96))
        draw.text((x, y + im.height + 8), label, fill=(215, 215, 220),
                  font=_font(19))
        x += CELL_W + PAD

    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"wrote {out}  {width}x{height}  ({len(ims)} cells)")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 4:
        print(__doc__)
        return 2
    cells = []
    for arg in argv[3:]:
        if "=" not in arg:
            print(f"!! cell argument {arg!r} is not <label>=<path>")
            return 2
        label, path = arg.split("=", 1)
        if not Path(path).is_file():
            print(f"!! no such frame: {path}")
            return 2
        cells.append((label, path))
    return build(Path(argv[1]), argv[2], cells)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
