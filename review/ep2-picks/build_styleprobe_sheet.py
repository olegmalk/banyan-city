#!/usr/bin/env python3
"""The beat-01 img2img strength probe on one labelled JPG, with both poles on it.

The probe asks one question — can TEXT move the style of the frame he called
"really good" toward the plate family without losing the composition or the fig
— so a sheet of the three arms alone cannot answer it. The two poles the arms
sit between have to be in the same picture at the same scale: column 1 is the
INIT the probe started from (his s2) above the PLATE-STYLE reference the probe
is trying to reach, and columns 2-4 are strength 0.25 / 0.40 / 0.55, one seed
per row.

Same reason as `build_wave_sheets.py`: `.gitignore:60-61` swallows
`review/**/*.png` and the site's licence gate refuses raw animagine output, so
the page carries a baked JPG and this file is the recipe that rebuilds it from
the durable frames.

Usage:
    python3 review/ep2-picks/build_styleprobe_sheet.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "sheets"

THUMB_W = 300
PAD = 10
LABEL_H = 46
TITLE_H = 38
QUALITY = 82

BG = (247, 247, 245)
CELL_BG = (255, 255, 255)
RULE = (222, 222, 218)
INK = (26, 26, 26)
MUTED = (105, 105, 100)

PROBE = REPO / "farm-out/ep2-b01-styleprobe"
INIT = REPO / "farm-out/ep2-b01-t2i-fig/01-cold-open-wave1-s2.png"
PLATE = REPO / "farm-out/ep2-b01-brightbase-figmatte/01-cold-open-bright-i35b-s0.png"

ROWS = [
    [(INIT, "INIT — his s2", "the frame the probe starts from"),
     (PROBE / "b01-styleprobe-i25-s0.png", "strength 0.25  s0", ""),
     (PROBE / "b01-styleprobe-i40-s0.png", "strength 0.40  s0", ""),
     (PROBE / "b01-styleprobe-i55-s0.png", "strength 0.55  s0", "")],
    [(PLATE, "PLATE STYLE — ref", "the look the probe is aiming at"),
     (PROBE / "b01-styleprobe-i25-s1.png", "strength 0.25  s1", ""),
     (PROBE / "b01-styleprobe-i40-s1.png", "strength 0.40  s1", ""),
     (PROBE / "b01-styleprobe-i55-s1.png", "strength 0.55  s1", "")],
]


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


def main():
    missing = [p for row in ROWS for p, _, _ in row if not p.exists()]
    if missing:
        for p in missing:
            print(f"MISSING {p}")
        return

    cells, thumb_h = [], None
    for row in ROWS:
        out_row = []
        for path, label, note in row:
            im = Image.open(path).convert("RGB")
            h = round(im.height * THUMB_W / im.width)
            thumb_h = thumb_h or h
            out_row.append((im.resize((THUMB_W, thumb_h), Image.LANCZOS), label, note))
        cells.append(out_row)

    cols = max(len(r) for r in cells)
    cell_h = thumb_h + LABEL_H
    W = cols * THUMB_W + (cols + 1) * PAD
    H = TITLE_H + len(cells) * cell_h + (len(cells) + 1) * PAD
    sheet = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(sheet)

    draw.text((PAD + 2, 11), "beat 01  cold-open  ·  img2img strength probe",
              fill=INK, font=_font(19, bold=True))
    draw.text((W - PAD - 320, 14), "identity-frozen wave, 12 Aug 2026",
              fill=MUTED, font=_font(15))

    for r, row in enumerate(cells):
        for c, (im, label, note) in enumerate(row):
            x = PAD + c * (THUMB_W + PAD)
            y = TITLE_H + PAD + r * (cell_h + PAD)
            draw.rectangle([x, y, x + THUMB_W - 1, y + cell_h - 1], fill=CELL_BG,
                           outline=RULE)
            sheet.paste(im, (x, y))
            draw.text((x + 8, y + thumb_h + 6), label, fill=INK, font=_font(16))
            if note:
                draw.text((x + 8, y + thumb_h + 26), note, fill=MUTED, font=_font(13))

    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / "wave2-b01-styleprobe.jpg"
    sheet.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    print(f"{dest.name}  {dest.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
