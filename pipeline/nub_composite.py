#!/usr/bin/env python3
"""nub_composite.py -- put the fruit's COLOUR into the init with plain image
processing, so the sampler never has to invent it.

WHY THIS EXISTS
---------------
Beat 01's frame-1 nub is an ADD: the picked plate carries a bare pedicel and no
fruit. The prompt route for it is measured and closed:

  * ep2-b01-fig-inpaint-s1 (2026-08-10), strength 0.99: a fruit appeared, and it
    wore a blown white specular cap. `matte green skin` went into the positive
    and eight glow terms into the negative (pipeline/b01-fig/*-r2.txt).
  * ep2-b01-nubinpaint-0818 (2026-08-18), strength 0.99, that same r2 negative
    plus `no purple`: one body of the right SIZE in the right PLACE, and it came
    back mean RGB 243,219,127 -- hue 48 deg, sat 0.48, val 0.95, brightest pixel
    250,245,151. Cream-gold and near-blown. FAIL-COLOUR, the 2026-08-10 defect
    verbatim, with every word written against it already in the negative.

So COLOUR does not bind through the negative on this checkpoint in this frame,
for the same reason leaf COUNT did not bind through the positive: the frame's
context wins. Here the context is amber rim-light in every direction of the
crop, and a full-strength pass reads that as the subject's own material.

This tool does the colour step the way leaf_count_composite.py does the layout
step -- in PIL, with no model and no GPU -- and then a LOW-strength inpaint
(0.30) only shades what is already there. That is the bark-clipboard pattern and
the leaf-count pattern generalised once more: give the init its structure with
plain image processing, then blend, because asking the sampler to invent the
structure destroys what it sits on. Community practice puts 0.2-0.35 denoise in
the band that preserves layout and identity
(stable-diffusion-art.com/denoising-strength, learn.rundiffusion.com), and this
repo's own leaf lane measured that band binding an attribute CLIP could not
encode on 8 of 8 frames.

THE COLOUR IS MEASURED FROM THE PLATE, NOT TYPED IN
---------------------------------------------------
A hex constant would be a taste call wearing a number, and it would also be
wrong: this plate is a backlit amber dusk, so a green picked in the abstract
lands as a decal. Every component of the nub's colour is read off the init at
run time and written into the sidecar:

  * HUE and SATURATION come from the plate's OWN green pixels -- everything in
    the --hue-band with at least --min-sat saturation, which on the picked
    frame is 6047 px (0.6% of the frame, the shadowed grass), median hue 90.0
    deg, quartiles 76 and 100. The nub is therefore the same green this picture
    already contains.
  * VALUE comes from the LOCAL LIGHT: the mean HSV value of the init inside the
    nub's own footprint before anything is pasted. The nub is exactly as bright
    as the light that falls where it sits, which is the direct countermeasure to
    the val-0.95 blown body the 0.99 pass returned. It cannot glow, because it
    is not allowed to be brighter than its own hole in the picture.

A vertical gradient (--grad top,bottom, multipliers on value) and a feathered
edge (--feather) are there so the 0.30 pass has something to SHADE. A flat disc
with a hard edge is a decal and blends like one.

$0: no model, no network, no GPU. Deterministic -- same arguments and same input
bytes give the same output bytes, which is what lets a job spec pin the
composite's sha256 for the inpaint step that follows.

    python nub_composite.py --init PLATE.png --init-sha256 <hex> \\
        --centre 405,750 --radii 10,13 --out COMP.png [--feather 1.6] \\
        [--grad 1.06,0.82] [--hue-band 60,170] [--min-sat 0.12] [--dry-run]
"""

from __future__ import annotations

import argparse
import colorsys
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


def pair(spec: str, name: str, cast=int):
    parts = [p.strip() for p in str(spec).split(",")]
    if len(parts) != 2:
        raise SystemExit("!! %s wants two comma-separated values, got %r" % (name, spec))
    return cast(parts[0]), cast(parts[1])


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        raise SystemExit("!! no samples to take a median of")
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def percentile(xs, q):
    xs = sorted(xs)
    if not xs:
        raise SystemExit("!! no samples to take a percentile of")
    i = int(round(q * (len(xs) - 1)))
    return xs[i]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--init", required=True, help="the picked plate to composite into")
    ap.add_argument("--init-sha256", required=True,
                    help="asserted before anything is read; a mismatch is a hard stop, "
                         "because a composite drawn into a different picture is a "
                         "different picture")
    ap.add_argument("--out", required=True, help="the composited init")
    ap.add_argument("--centre", required=True, metavar="cx,cy",
                    help="centre of the nub body in pixels of the init")
    ap.add_argument("--radii", required=True, metavar="rx,ry",
                    help="radii of the nub body in pixels. This is the SIZE CAP: "
                         "nothing wider than 2*rx can be drawn, before any sampler "
                         "gets a vote.")
    ap.add_argument("--feather", type=float, default=1.6,
                    help="gaussian blur on the body's alpha, px (default 1.6). A hard "
                         "edge is a decal and blends like one.")
    ap.add_argument("--grad", default="1.06,0.82", metavar="top,bottom",
                    help="value multipliers down the body, so the 0.30 pass has "
                         "shading to follow rather than a flat disc (default 1.06,0.82)")
    ap.add_argument("--hue-band", default="60,170", metavar="lo,hi",
                    help="degrees of hue counted as GREEN when sampling the plate "
                         "(default 60,170)")
    ap.add_argument("--min-sat", type=float, default=0.12,
                    help="minimum saturation for a plate pixel to count as a green "
                         "sample (default 0.12)")
    ap.add_argument("--sat-percentile", type=float, default=0.90,
                    help="which percentile of the sampled greens' saturation the nub "
                         "takes (default 0.90: the plate's own greens are shadowed and "
                         "their median saturation is thin, and a 0.30 pass loses "
                         "saturation rather than gaining it)")
    ap.add_argument("--value-cap", type=float, default=0.92,
                    help="hard ceiling on the body's HSV value (default 0.92). The "
                         "0.99 pass returned a val-0.95 near-blown body; the nub may "
                         "not be brighter than the light it sits in.")
    ap.add_argument("--note", default="")
    ap.add_argument("--dry-run", action="store_true",
                    help="measure and print the colour it WOULD use, write nothing")
    a = ap.parse_args()

    if not os.path.isfile(a.init):
        raise SystemExit("!! init not found: %s" % a.init)
    have = sha256_of(a.init)
    if have != a.init_sha256:
        raise SystemExit("!! INIT SHA MISMATCH -- refusing.\n   want %s\n   have %s"
                         % (a.init_sha256, have))

    cx, cy = pair(a.centre, "--centre")
    rx, ry = pair(a.radii, "--radii")
    if rx <= 0 or ry <= 0:
        raise SystemExit("!! --radii must be positive, got %r" % a.radii)
    g_top, g_bot = pair(a.grad, "--grad", float)
    h_lo, h_hi = pair(a.hue_band, "--hue-band", float)

    src = Image.open(a.init).convert("RGB")
    W, H = src.size
    px = src.load()
    print("init        %s" % a.init)
    print("init size   %dx%d" % (W, H))
    print("init sha256 %s" % have)

    # ---- 1. sample the plate's OWN green -------------------------------------
    hues, sats = [], []
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y]
            hh, ss, vv = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            hd = hh * 360.0
            if h_lo <= hd <= h_hi and ss >= a.min_sat:
                hues.append(hd)
                sats.append(ss)
    if len(hues) < 200:
        raise SystemExit(
            "!! only %d plate pixels fall in the green band %g-%g deg at sat>=%g. "
            "This plate has no green to sample, so any green pasted into it would "
            "be a hex guess wearing a measurement. Refusing."
            % (len(hues), h_lo, h_hi, a.min_sat))
    nub_hue = median(hues)
    nub_sat = percentile(sats, a.sat_percentile)
    print("green px    %d (%.2f%% of frame) in %g-%g deg at sat>=%g"
          % (len(hues), 100.0 * len(hues) / (W * H), h_lo, h_hi, a.min_sat))
    print("nub hue     %.1f deg (median of the plate's own greens; quartiles %.1f / %.1f)"
          % (nub_hue, percentile(hues, 0.25), percentile(hues, 0.75)))
    print("nub sat     %.3f (p%.0f of the plate's own greens; median %.3f, max %.3f)"
          % (nub_sat, a.sat_percentile * 100, median(sats), max(sats)))

    # ---- 2. take the VALUE from the local light ------------------------------
    x0, y0, x1, y1 = cx - rx, cy - ry, cx + rx, cy + ry
    if x0 < 0 or y0 < 0 or x1 >= W or y1 >= H:
        raise SystemExit("!! the nub footprint (%d,%d)-(%d,%d) leaves the frame"
                         % (x0, y0, x1, y1))
    vals = []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            r, g, b = px[x, y]
            vals.append(colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[2])
    local_v = sum(vals) / len(vals)
    print("local light value %.3f (mean HSV value of the init under the footprint)"
          % local_v)

    # ---- 3. draw the body ----------------------------------------------------
    # THE COLOUR LAYER IS PAINTED WIDER THAN THE BODY, and that is not a detail.
    # A feathered alpha spreads past the body's own tile, so every pixel it can
    # reach must already hold nub colour: paint the tile exactly and the blur
    # pulls in whatever the layer holds outside it -- black -- and the nub comes
    # out wearing a dark rim, which the 0.30 pass then dutifully inks in as an
    # outline. The gradient is a function of absolute y, so extending the band
    # costs nothing and keeps the shading continuous.
    pad = int(round(a.feather * 3)) + 2
    px0, py0 = max(0, x0 - pad), max(0, y0 - pad)
    px1, py1 = min(W - 1, x1 + pad), min(H - 1, y1 + pad)
    bw, bh = px1 - px0 + 1, py1 - py0 + 1

    # Alpha at 4x then downsampled: a 1x ellipse this small staircases, and the
    # staircase survives the feather as a visible ridge the 0.30 pass will trace.
    ss_f = 4
    alpha_big = Image.new("L", (bw * ss_f, bh * ss_f), 0)
    ImageDraw.Draw(alpha_big).ellipse(
        [(x0 - px0) * ss_f, (y0 - py0) * ss_f,
         (x1 - px0 + 1) * ss_f - 1, (y1 - py0 + 1) * ss_f - 1], fill=255)
    tile_a = alpha_big.resize((bw, bh), Image.BILINEAR)

    body = Image.new("RGB", (bw, bh))
    bp = body.load()
    for j in range(bh):
        t = (py0 + j - y0) / float(2 * ry)         # 0 at the body top, 1 at its bottom
        t = max(0.0, min(1.0, t))
        v = local_v * (g_top + (g_bot - g_top) * t)
        v = max(0.0, min(a.value_cap, v))
        r, g, b = colorsys.hsv_to_rgb(nub_hue / 360.0, nub_sat, v)
        row = (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))
        for i in range(bw):
            bp[i, j] = row

    alpha = Image.new("L", (W, H), 0)
    alpha.paste(tile_a, (px0, py0))
    if a.feather > 0:
        alpha = alpha.filter(ImageFilter.GaussianBlur(a.feather))
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    layer.paste(body, (px0, py0))

    top_rgb = tuple(int(round(c * 255)) for c in
                    colorsys.hsv_to_rgb(nub_hue / 360.0, nub_sat,
                                        min(a.value_cap, local_v * g_top)))
    bot_rgb = tuple(int(round(c * 255)) for c in
                    colorsys.hsv_to_rgb(nub_hue / 360.0, nub_sat,
                                        min(a.value_cap, local_v * g_bot)))
    print("body        %dx%d px at centre (%d,%d), footprint (%d,%d)-(%d,%d)"
          % (2 * rx + 1, 2 * ry + 1, cx, cy, x0, y0, x1, y1))
    print("body rgb    top %s -> bottom %s, feather %.2f px" % (top_rgb, bot_rgb, a.feather))

    if a.dry_run:
        print("\nDRY RUN -- nothing written. The colour above is what would be pasted.")
        return 0

    out = Image.composite(layer, src, alpha)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    out.save(a.out)
    out_sha = sha256_of(a.out)
    if out_sha == have:
        raise SystemExit("!! the composite is byte-identical to the init -- nothing was "
                         "pasted. Refusing to report a no-op as a fix.")
    print("\nwrote       %s" % a.out)
    print("out sha256  %s" % out_sha)

    sidecar = os.path.splitext(a.out)[0] + ".composite.json"
    with open(sidecar, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({
            "tool": "pipeline/nub_composite.py",
            "purpose": "the fruit's COLOUR made structural before any sampler runs",
            "init": a.init.replace("\\", "/"),
            "init_sha256": have,
            "out": a.out.replace("\\", "/"),
            "out_sha256": out_sha,
            "centre_px": [cx, cy],
            "radii_px": [rx, ry],
            "footprint_px": [x0, y0, x1, y1],
            "feather_px": a.feather,
            "grad": [g_top, g_bot],
            "value_cap": a.value_cap,
            "sampled_green_px": len(hues),
            "sampled_hue_band_deg": [h_lo, h_hi],
            "sampled_min_sat": a.min_sat,
            "nub_hue_deg": round(nub_hue, 2),
            "nub_sat": round(nub_sat, 4),
            "nub_sat_percentile": a.sat_percentile,
            "local_light_value": round(local_v, 4),
            "body_rgb_top": list(top_rgb),
            "body_rgb_bottom": list(bot_rgb),
            "cost_usd": 0.0,
            "model": "none -- plain PIL, no sampler, no network, no GPU",
            "note": a.note,
            "colour_is_measured_not_typed":
                "hue and saturation are read off this plate's own green pixels and "
                "value is read off the light inside the nub's own footprint. No "
                "constant colour appears anywhere in this tool.",
        }, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote       %s" % sidecar)
    print("\nCOLOUR IS NOW STRUCTURAL, NOT PROMPTED. Look at it before the GPU step -- "
          "this is the sample.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
