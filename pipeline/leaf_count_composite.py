#!/usr/bin/env python3
"""leaf_count_composite.py -- give the init its leaf COUNT with plain image
processing, so the sampler never has to invent one.

WHY THIS EXISTS
---------------
Exact instance count is a measured failure of text-to-image diffusion, not a
wording problem we have not yet phrased well enough:

  * "Text-to-Image Diffusion Models Cannot Count, and Prompt Refinement Cannot
    Help", arXiv:2503.06884 -- prompt refinement generally does NOT improve
    counting accuracy.
  * "Make It Count", CVPR 2025 (arXiv:2406.10210), implemented on SDXL, which is
    our stills model: plain SDXL with a numeral in the prompt scores 26-28%
    counting accuracy. Their fix reaches 54% and needs a ReLayout U-Net trained
    on ~10K image pairs. The field's accepted decomposition is text -> LAYOUT ->
    image: count is a layout problem.
  * That paper's objection to Bounded Attention -- it "requires users to
    manually provide the bounding boxes" -- is our whole opportunity. We are not
    generating a random scene. We are drawing ONE designed character whose
    layout we already know, so we can simply provide it.

Our own evidence agrees. `authored_b01_canon_0816` asks for "exactly two wide
oval cotyledon leaves" AND bans "no three leaves, no four leaves, no many
leaves" -- the strongest wording available, numeral plus explicit negation of
every wrong count -- and returned 0 of 16 frames with two leaves on 2026-08-17.
`authored_b21_scale_0816` returned 2 of 4. The vacancy law already recorded here
says why the negation cannot work: an empty region is a hole the model fills
with the largest noun, and the negative does not reach it.

So this tool does the layout step, in PIL, with no model and no GPU. It takes a
real rendered plate that has the right style and the right height relation but
too many leaves, and it REMOVES the extra leaves by patching them with the
plate's own background pixels. The count is then correct BY CONSTRUCTION, before
any sampler runs. A following LOW-strength inpaint (0.30) only blends the seam.

This is the bark-clipboard pattern from beats 06 and 10, generalised: give the
init its structure with plain image processing, then inpaint at LOW strength,
because asking the sampler to invent the structure destroys what it sits on.
Community practice puts 0.2-0.35 denoise in the band that preserves layout and
identity (stable-diffusion-art.com/denoising-strength, learn.rundiffusion.com).

Crucially, the patch is copied from the plate's OWN pixels rather than left
empty. An emptied region is exactly the vacancy the model would fill with
another leaf. There is nothing here for it to fill.

$0: no model, no network, no GPU. Deterministic -- same arguments, same bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:  # pragma: no cover
    sys.exit("!! needs Pillow: pip install pillow")


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_ellipse(spec: str) -> tuple[int, int, int, int, float]:
    """cx,cy,rx,ry[,angle_degrees]"""
    parts = [p.strip() for p in spec.split(",") if p.strip() != ""]
    if len(parts) not in (4, 5):
        raise SystemExit(
            "!! --remove wants cx,cy,rx,ry[,angle], got %r" % spec)
    cx, cy, rx, ry = (int(round(float(p))) for p in parts[:4])
    angle = float(parts[4]) if len(parts) == 5 else 0.0
    if rx <= 0 or ry <= 0:
        raise SystemExit("!! --remove radii must be positive, got %r" % spec)
    return cx, cy, rx, ry, angle


def parse_offset(spec: str) -> tuple[int, int]:
    parts = [p.strip() for p in spec.split(",")]
    if len(parts) != 2:
        raise SystemExit("!! --source-offset wants dx,dy, got %r" % spec)
    return int(round(float(parts[0]))), int(round(float(parts[1])))


def ellipse_mask(size, cx, cy, rx, ry, angle, feather):
    """A white filled ellipse on black, optionally rotated, then feathered."""
    # Draw upright at 4x on a tight canvas, rotate, paste. 4x keeps the edge
    # smooth: a rotated hard ellipse at 1x staircases, and the staircase
    # survives the blur as a visible ridge in the blend.
    ss = 4
    pad = int(max(rx, ry) * 1.6) + 8
    tile = Image.new("L", ((pad * 2) * ss, (pad * 2) * ss), 0)
    d = ImageDraw.Draw(tile)
    d.ellipse(
        [(pad - rx) * ss, (pad - ry) * ss, (pad + rx) * ss, (pad + ry) * ss],
        fill=255,
    )
    tile = tile.resize((pad * 2, pad * 2), Image.LANCZOS)
    if angle:
        tile = tile.rotate(angle, resample=Image.BICUBIC, expand=False)
    mask = Image.new("L", size, 0)
    mask.paste(tile, (cx - pad, cy - pad), tile)
    if feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(feather))
    return mask


def main() -> int:
    ap = argparse.ArgumentParser(
        description="patch extra leaves out of a plate with its own background "
                    "pixels, so leaf count is correct BEFORE any sampler runs")
    ap.add_argument("--init", required=True,
                    help="the rendered plate to correct")
    ap.add_argument("--out", required=True,
                    help="composited init (leaf count correct by construction)")
    ap.add_argument("--mask-out", default=None,
                    help="write the union mask here, for inpaint_fruit --mask-png")
    ap.add_argument("--remove", action="append", default=[], metavar="cx,cy,rx,ry[,ang]",
                    help="an extra leaf to patch out; repeatable")
    ap.add_argument("--source-offset", action="append", default=[], metavar="dx,dy",
                    help="where to copy background from for the matching --remove. "
                         "Given once, it applies to every --remove.")
    ap.add_argument("--feather", type=int, default=9,
                    help="gaussian blur on the patch mask, px (default 9)")
    ap.add_argument("--mask-grow", type=int, default=12,
                    help="dilate the mask written by --mask-out beyond the patch, "
                         "px, so the blend pass covers the whole seam (default 12)")
    ap.add_argument("--note", default="")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan and the arithmetic, write nothing")
    args = ap.parse_args()

    if not args.remove:
        raise SystemExit("!! nothing to do: pass at least one --remove")
    if not args.source_offset:
        raise SystemExit(
            "!! --source-offset is REQUIRED. Leaving the region empty is the "
            "vacancy the model fills with another leaf -- the patch must carry "
            "real background pixels.")
    if len(args.source_offset) not in (1, len(args.remove)):
        raise SystemExit(
            "!! give one --source-offset for all %d --remove, or one each; got %d"
            % (len(args.remove), len(args.source_offset)))

    init_sha = sha256_of(args.init)
    src = Image.open(args.init).convert("RGB")
    W, H = src.size
    print("init        %s" % args.init)
    print("init size   %dx%d" % (W, H))
    print("init sha256 %s" % init_sha)

    regions = [parse_ellipse(r) for r in args.remove]
    offsets = [parse_offset(o) for o in args.source_offset]
    if len(offsets) == 1:
        offsets = offsets * len(regions)

    out = src.copy()
    union = Image.new("L", (W, H), 0)

    for i, ((cx, cy, rx, ry, ang), (dx, dy)) in enumerate(zip(regions, offsets)):
        if dx == 0 and dy == 0:
            raise SystemExit(
                "!! --source-offset 0,0 for region %d copies the leaf onto "
                "itself and changes nothing." % i)
        m = ellipse_mask((W, H), cx, cy, rx, ry, ang, args.feather)
        # The source patch is the SAME plate shifted by the offset, so every
        # pixel laid down is real background from this exact frame -- same
        # palette, same grain, same light. Nothing is invented and nothing is
        # left blank.
        shifted = Image.new("RGB", (W, H))
        shifted.paste(src, (dx, dy))
        # Any part of the shifted copy that falls outside the frame is empty;
        # refuse rather than paste black into the plate.
        need = m.getbbox()
        if need is None:
            raise SystemExit("!! region %d produced an empty mask" % i)
        x0, y0, x1, y1 = need
        if not (0 <= x0 - dx and x1 - dx <= W and 0 <= y0 - dy and y1 - dy <= H):
            raise SystemExit(
                "!! region %d: source-offset %d,%d reads outside the frame for "
                "mask bbox %s -- it would paste black into the plate. Pick an "
                "offset that keeps the source patch inside %dx%d."
                % (i, dx, dy, need, W, H))
        out = Image.composite(shifted, out, m)
        union = Image.composite(Image.new("L", (W, H), 255), union, m)
        print("remove[%d]   ellipse cx=%d cy=%d rx=%d ry=%d ang=%.1f  "
              "<- background from offset %+d,%+d  (mask bbox %s)"
              % (i, cx, cy, rx, ry, ang, dx, dy, need))

    if args.mask_grow > 0:
        union = union.filter(ImageFilter.MaxFilter(3))
        union = union.filter(ImageFilter.GaussianBlur(args.mask_grow))
        union = union.point(lambda v: 255 if v > 24 else 0)

    if args.dry_run:
        print("\nDRY RUN -- nothing written. %d region(s) planned." % len(regions))
        print("next step would be a LOW-strength blend over --mask-png, e.g.")
        print("  python3 pipeline/inpaint_fruit.py --init %s \\\n"
              "      --init-sha256 <sha of the composite> --mask-png %s \\\n"
              "      --strength 0.30 ..." % (args.out, args.mask_out or "<mask>"))
        return 0

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    out.save(args.out)
    out_sha = sha256_of(args.out)
    if out_sha == init_sha:
        raise SystemExit(
            "!! the composite is byte-identical to the init -- nothing was "
            "patched. Refusing to report a no-op as a fix.")
    print("\nwrote       %s" % args.out)
    print("out sha256  %s" % out_sha)

    if args.mask_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.mask_out)) or ".",
                    exist_ok=True)
        union.save(args.mask_out)
        print("wrote mask  %s (bbox %s)" % (args.mask_out, union.getbbox()))

    sidecar = os.path.splitext(args.out)[0] + ".composite.json"
    with open(sidecar, "w", encoding="utf-8") as fh:
        json.dump({
            "tool": "pipeline/leaf_count_composite.py",
            "purpose": "leaf COUNT fixed by construction before any sampler runs",
            "init": args.init,
            "init_sha256": init_sha,
            "out": args.out,
            "out_sha256": out_sha,
            "mask_out": args.mask_out,
            "remove": args.remove,
            "source_offset": args.source_offset,
            "feather": args.feather,
            "mask_grow": args.mask_grow,
            "cost_usd": 0.0,
            "model": "none -- plain PIL, no sampler, no network",
            "note": args.note,
            "sources": [
                "arXiv:2503.06884 -- prompt refinement does not improve counting",
                "arXiv:2406.10210 (Make It Count, CVPR 2025) -- plain SDXL "
                "numerals score 26-28%; count is a layout problem",
            ],
        }, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote        %s" % sidecar)
    print("\nCOUNT IS NOW STRUCTURAL, NOT PROMPTED. Verify by eye before any "
          "GPU step -- this is the sample.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
