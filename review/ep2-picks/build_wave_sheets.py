#!/usr/bin/env python3
"""One labelled JPG contact sheet per identity-frozen wave round.

WHY A BAKED JPG AND NOT THE FRAMES THEMSELVES. The wave PNGs land in
`farm-out/ep2-bNN-idfix/` (durable, checksummed, pushed by the courier), but a
review page cannot point at them: `.gitignore:60-61` swallows `review/**/*.png`
and the site's licence gate refuses raw animagine output. So the page shows one
JPG per round, force-added past the ignore rule, exactly as the night-0811
sheets were made — and this file is the recipe those sheets never had, so the
picture can be rebuilt from the durable frames instead of being a one-off
nobody can check.

Neutral by construction: seeds appear in filename order, labelled with their own
`sNN` token, nothing ranked, starred or filtered. The picks are R4's.

A fix round lands in `farm-out/ep2-bNN-idfix-r2/` and bakes to
`sheets/wave2-bNN-r2.jpg`, so the two generations of a beat are two files the
page can stack rather than one sheet that silently replaces the other. Beat 03
is the exception on disk: its r2 job published INTO the baseline directory on
`farm-results-rtx5090` (see wave2-faults-fixer.yaml, last record), so its r2
frames were copied to `ep2-b03-idfix-r2/` by hand before this ran.

Usage:
    python3 review/ep2-picks/build_wave_sheets.py [--round r2] [02 03 ...]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "sheets"

THUMB_W = 300          # 832x1216 source -> 300x438
COLS = 4
PAD = 10
LABEL_H = 30
TITLE_H = 38
QUALITY = 80

BG = (247, 247, 245)
CELL_BG = (255, 255, 255)
RULE = (222, 222, 218)
INK = (26, 26, 26)
MUTED = (105, 105, 100)


def _font(size: int, bold: bool = False):
    names = ["/System/Library/Fonts/Supplemental/Arial.ttf"]
    if bold:
        names.insert(0, "/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    for p in names:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def build(nn: str, round_: str = ""):
    suffix = f"-{round_}" if round_ else ""
    src = REPO / f"farm-out/ep2-b{nn}-idfix{suffix}"
    files = sorted(src.glob("*.png"))
    if not files:
        return None, 0

    slug = "-".join(files[0].stem.split("-")[1:-2])
    cells = []
    thumb_h = None
    for f in files:
        im = Image.open(f).convert("RGB")
        h = round(im.height * THUMB_W / im.width)
        thumb_h = thumb_h or h
        cells.append((im.resize((THUMB_W, h), Image.LANCZOS), f.stem.split("-")[-1]))

    rows = (len(cells) + COLS - 1) // COLS
    cell_h = thumb_h + LABEL_H
    W = COLS * THUMB_W + (COLS + 1) * PAD
    H = TITLE_H + rows * cell_h + (rows + 1) * PAD
    sheet = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(sheet)

    head = f"beat {nn}  {slug}" + (f"  ·  fix round {round_}" if round_ else "")
    draw.text((PAD + 2, 11), head, fill=INK, font=_font(19, bold=True))
    draw.text((W - PAD - 320, 14), "identity-frozen wave, 12 Aug 2026",
              fill=MUTED, font=_font(15))

    for i, (im, tok) in enumerate(cells):
        r, c = divmod(i, COLS)
        x = PAD + c * (THUMB_W + PAD)
        y = TITLE_H + PAD + r * (cell_h + PAD)
        draw.rectangle([x, y, x + THUMB_W - 1, y + cell_h - 1], fill=CELL_BG,
                       outline=RULE)
        sheet.paste(im, (x, y))
        draw.text((x + 8, y + thumb_h + 6), tok, fill=INK, font=_font(17))

    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"wave2-b{nn}{suffix}.jpg"
    sheet.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return dest, len(cells)


if __name__ == "__main__":
    args = sys.argv[1:]
    round_ = ""
    if "--round" in args:
        i = args.index("--round")
        round_ = args[i + 1]
        del args[i:i + 2]
    wanted = args or ["02", "03", "04", "05", "06", "07", "08", "09",
                      "10", "11", "13", "14", "15", "17", "19", "20"]
    total = 0
    for nn in wanted:
        dest, n = build(nn, round_)
        if dest is None:
            print(f"b{nn}  NO FRAMES")
            continue
        total += dest.stat().st_size
        print(f"b{nn}  {n} seeds  {dest.stat().st_size/1024:6.0f} KB  {dest.name}")
    print(f"total {total/1024/1024:.2f} MB")
