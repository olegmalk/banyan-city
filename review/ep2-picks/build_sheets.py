#!/usr/bin/env python3
"""Per-beat labelled contact sheets for episode 2 (002b-first-citizen).

WHY THIS EXISTS RATHER THAN REUSING `review/ep2-stills/CONTACT-002b-bNN.png`:
those sheets were built 2026-08-07 23:00. Round 3 for nineteen of the twenty-one
beats landed 2026-08-08 19:32, and b01/b04/b05/b12/b13 gained rounds later still
(up to r9 on b13, 2026-08-09 23:55). Embedding them would have shown the author a
picture that is missing most of what is on disk — the one failure mode a picking
page cannot have. These sheets are built from the stills directory itself, so
what he sees is what exists.

Every candidate on disk appears, in filename order, labelled with its own
round/seed token. Nothing is ranked, reordered, starred or filtered: the verdict
history lives in the page text, and the image stays neutral so a sheet never has
to be rebuilt when a verdict changes.
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
STILLS = REPO / "genomes/sapling/nodes/002b-first-citizen/takes/stills"
OUT = Path(__file__).resolve().parent / "sheets"

THUMB_W = 260          # 832x1216 source -> 260x380
COLS = 4
PAD = 10
LABEL_H = 30
QUALITY = 78
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"

BG = (247, 247, 245)
CELL_BG = (255, 255, 255)
RULE = (222, 222, 218)
INK = (26, 26, 26)


# Later work for some beats never landed in `takes/stills/` — it was rendered
# into a review subdirectory and left there. Two of these are the frames the
# founder has actually spoken well of (b01's r9, "the beat 01 frame looks good",
# and b15's goblin-simple wave, "that looks like the right goblin"), so a picking
# page that showed only `takes/stills/` would be missing the newest and
# best-received candidates for the beats concerned.
SATELLITES = {
    "01": ["review/b01-r9-stage2/*.png", "review/b01-fig-inpaint/b01-fig-inpaint-s1.png"],
    "04": ["review/SHEETS/src-goblin/04-*.png"],
    "14": ["review/SHEETS/src-goblin/14-*.png"],
    "15": ["review/tonight/15-*.png"],
}


def token(path: Path) -> str:
    """`13-the-shade-r9-s2.png` -> `r9-s2`; the beat slug is the page heading."""
    stem = path.stem
    parts = stem.split("-")
    # Drop the leading `NN` and the words of the slug, keeping the first part
    # that starts a round marker (r<digit>, i2i, ipa, wave...).
    for i, p in enumerate(parts[1:], start=1):
        if (p[:1] == "r" and p[1:2].isdigit()) or p in ("i2i", "t2i", "ipa") \
                or p.startswith("wave"):
            return "-".join(parts[i:])
    return stem


def beat_files(nn: str) -> list:
    files = [p for p in STILLS.glob(f"{nn}-*.png") if p.suffix == ".png"]
    seen = {p.name for p in files}
    extra = []
    for pattern in SATELLITES.get(nn, []):
        for p in sorted(REPO.glob(pattern)):
            # A review directory holds its own contact sheets and mask images
            # beside the frames; neither is a candidate.
            if p.name in seen or "mask" in p.name \
                    or p.name.startswith(("CONTACT-", "LABELED-")):
                continue
            seen.add(p.name)
            extra.append(p)
    return sorted(files) + extra


def build(nn: str) -> tuple:
    files = beat_files(nn)
    if not files:
        return None, 0
    thumb_h = None
    cells = []
    for f in files:
        im = Image.open(f).convert("RGB")
        h = round(im.height * THUMB_W / im.width)
        thumb_h = thumb_h or h
        cells.append((im.resize((THUMB_W, h), Image.LANCZOS), token(f)))

    rows = (len(cells) + COLS - 1) // COLS
    cell_h = thumb_h + LABEL_H
    W = COLS * THUMB_W + (COLS + 1) * PAD
    H = rows * cell_h + (rows + 1) * PAD
    sheet = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT_PATH, 17)

    for i, (im, tok) in enumerate(cells):
        r, c = divmod(i, COLS)
        x = PAD + c * (THUMB_W + PAD)
        y = PAD + r * (cell_h + PAD)
        draw.rectangle([x, y, x + THUMB_W - 1, y + cell_h - 1], fill=CELL_BG,
                       outline=RULE)
        sheet.paste(im, (x, y))
        draw.text((x + 8, y + thumb_h + 6), tok, fill=INK, font=font)

    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"b{nn}.jpg"
    sheet.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return dest, len(cells)


if __name__ == "__main__":
    wanted = sys.argv[1:] or [f"{n:02d}" for n in range(1, 22)]
    total = 0
    for nn in wanted:
        dest, n = build(nn)
        if dest is None:
            print(f"b{nn}  NO STILLS")
            continue
        size = dest.stat().st_size
        total += size
        print(f"b{nn}  {n:>2} candidates  {size/1024:7.0f} KB  {dest.name}")
    print(f"total {total/1024/1024:.2f} MB")
