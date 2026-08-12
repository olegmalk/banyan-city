#!/usr/bin/env python3
"""Bake a clip contact sheet with the beat's INTENT burnt into the image.

Founder's rule, 2026-08-12: "for the other beats it doesnt say what they're supposed
to show.." He opens sheets straight off disk, so a sheet titled with its recipe tells
him what we ran and nothing about whether the picture is right. Every sheet therefore
carries the beat number and one plain sentence of what the shot is FOR, in the JPG.

THE SENTENCE IS NEVER RETYPED. It lives exactly once, in review/ep2-picks/beats.json
under `shows`, keyed by `n`. Reading it from there is what stops a sheet and the page
drifting apart. A beat with no `shows` line is not bakeable: say what the shot is for,
or do not bake it.

Usage:
  bake_clip_sheet.py --beat 19 --mp4 <path> --out <path.jpg> [--frames 8] [--note "..."]
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BEATS = os.path.join(HERE, "beats.json")

# A REAL FONT, NOT PIL'S BITMAP DEFAULT. The default renders at ~11px and turns "—"
# and "·" into tofu, which is how the first bake came out reading "GOOD LISTENERB".
# The whole point of this sheet is that he can read the intent off disk at a glance.
FONT_CANDIDATES = ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                   "/System/Library/Fonts/Helvetica.ttc",
                   "/Library/Fonts/Arial.ttf")


def load_font(size: int):
    for p in FONT_CANDIDATES:
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def ascii_clean(s: str) -> str:
    """Typographic characters the bitmap fallback cannot draw."""
    for bad, good in (("—", "-"), ("–", "-"), ("·", "|"),
                      ("’", "'"), ("‘", "'"), ("“", '"'),
                      ("”", '"'), ("…", "...")):
        s = s.replace(bad, good)
    return s


def intent(n: str) -> tuple:
    """(title, shows) for beat n. Raises if the beat cannot say what it is for."""
    with open(BEATS, encoding="utf-8") as fh:
        for b in json.load(fh):
            if b.get("n") == n:
                shows = (b.get("shows") or "").strip()
                if not shows:
                    sys.exit(f"!! beat {n} has no `shows` line in beats.json -- not bakeable.\n"
                             f"   Say what the shot is for, or do not bake it.")
                title = (b.get("title") or "").split("·")[0].strip()
                return title, shows
    sys.exit(f"!! beat {n} not found in {BEATS}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beat", required=True, help='beat number as it appears in beats.json, e.g. "19"')
    ap.add_argument("--mp4", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames", type=int, default=8)
    ap.add_argument("--cell", type=int, default=300)
    ap.add_argument("--note", default="", help="one extra line under the intent, e.g. the verdict")
    a = ap.parse_args()

    title, shows = intent(a.beat)

    n_total = int(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=nb_frames", "-of", "csv=p=0", a.mp4],
        capture_output=True, text=True, check=True).stdout.strip() or 0)
    if n_total <= 0:
        sys.exit(f"!! could not read a frame count from {a.mp4}")
    step = max(1, n_total // a.frames)

    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.mp4,
                        "-vf", rf"select='not(mod(n\,{step}))',scale={a.cell}:-1",
                        "-fps_mode", "passthrough", os.path.join(td, "f%03d.png")], check=True)
        shots = sorted(os.listdir(td))[:a.frames]
        if not shots:
            sys.exit("!! no frames extracted")
        ims = [Image.open(os.path.join(td, s)).convert("RGB") for s in shots]

        cw, ch = ims[0].size
        W = cw * len(ims)
        big, small = load_font(23), load_font(17)
        # the band is sized from the WRAPPED text, so a long sentence is never clipped
        head = textwrap.wrap(ascii_clean(f"BEAT {a.beat} | {title} - SHOULD SHOW: {shows}"),
                             width=max(40, W // 13))
        note = textwrap.wrap(ascii_clean(a.note), width=max(40, W // 11)) if a.note else []
        band = 14 + 29 * len(head) + (10 + 22 * len(note) if note else 0) + 12
        sheet = Image.new("RGB", (W, band + ch + 22), (14, 14, 16))
        dr = ImageDraw.Draw(sheet)
        y = 14
        for line in head:
            dr.text((10, y), line, font=big, fill=(255, 226, 120))
            y += 29
        if note:
            y += 10
            for line in note:
                dr.text((10, y), line, font=small, fill=(170, 205, 255))
                y += 22
        for i, im in enumerate(ims):
            sheet.paste(im, (i * cw, band))
            dr.text((i * cw + 6, band + ch + 4), f"f{i * step}", font=small, fill=(150, 155, 165))
        sheet.save(a.out, quality=88)
    print(f"BEAT {a.beat} sheet -> {a.out} ({len(ims)} frames of {n_total}, {sheet.size[0]}x{sheet.size[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
