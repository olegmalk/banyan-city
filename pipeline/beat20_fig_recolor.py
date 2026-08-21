#!/usr/bin/env python3
r"""RECOLOUR BEAT 20's FIG TO CANON PURPLE, in the pixels, before the naturalize.

WHY. canon.yaml `ep2-fig-purple` (founder, 2026-08-13/14): the fig is a DEEP
PURPLE-VIOLET, written into the beat-20 drafts. The canon w2 plate carries it
YELLOW-GREEN, and the motion judge's b20 verdict (review/canonmotion-0821/
JUDGING-0821.md) names it: "the outgoing take had it RED, so this is the same
fault in a new colour, carried by the plate rather than introduced by the
motion." No render has ever produced a purple fig from wording (56 rendered fig
prompts say so, per canon.yaml's own note), which makes this composite-init-
pattern.md CLASS A: with a composited init the thing you want is not a sample
from the model. The recolour is applied to the plate and the SAME 0.30
naturalize pass that finishes the drawn sapling finishes this.

THE RULE, measured on the plate, not guessed. The fig is the one SATURATED
yellow-green blob in the frame: inside a caller-named box, `G - B > sat_gb`
and `G > lum_g` selects it and selects none of the pale hands around it (the
hands are desaturated, G-B ~ 8-20). The hue moves to violet in HSV with V
KEPT PER PIXEL, so the plate's own shading -- the specular, the occlusion
under the fingers -- survives the recolour. Nothing outside the matte changes
and the tool asserts that.

$0. numpy + PIL. Deterministic. --dry-run writes the matte overlay only.
"""
from __future__ import annotations

import argparse
import colorsys
import hashlib
import os

import numpy as np
from PIL import Image


def sha256_of(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plate", required=True)
    ap.add_argument("--plate-sha256", default=None)
    ap.add_argument("--box", default=None, help="x0,y0,x1,y1 around the fig")
    ap.add_argument("--ellipse", default=None,
                    help="cx,cy,rx,ry -- MEASURED 2026-08-21 on this plate: the "
                         "fig's shadow side (47,76,21) and the shirt's lit hem "
                         "(116,129,74) and the hand's shaded edge (133,145,90) "
                         "all sit at G-B ~55, so NO channel rule separates fig "
                         "from shirt here (the colour rule transferred zero "
                         "times across four boards either, composite-init-"
                         "pattern.md 5). The fig is the one ROUND thing in the "
                         "region, so geometry carries the class and the colour "
                         "rule only excludes the pale fingers crossing it.")
    ap.add_argument("--sat-gb", type=int, default=40,
                    help="G-B above this inside the box is fig, not hand")
    ap.add_argument("--lum-g", type=int, default=110)
    ap.add_argument("--hue", type=float, default=0.76,
                    help="target hue, 0..1; 0.76 is violet")
    ap.add_argument("--sat-scale", type=float, default=0.80,
                    help="the canon look is muted; full fig saturation reads neon")
    ap.add_argument("--grow", type=int, default=2,
                    help="px to dilate the matte over the fig's own antialiasing")
    ap.add_argument("--out", required=True)
    ap.add_argument("--matte-out", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    have = sha256_of(a.plate)
    if a.plate_sha256 and have != a.plate_sha256:
        raise SystemExit("!! plate sha mismatch: want %s have %s"
                         % (a.plate_sha256, have))
    img = Image.open(a.plate).convert("RGB")
    arr = np.asarray(img).astype(np.int16)
    H, W = arr.shape[:2]
    if not a.ellipse:
        raise SystemExit("!! --ellipse is required; a box cannot separate this "
                         "fig from this shirt (measured, see --ellipse help).")
    cx, cy, rx, ry = (int(v) for v in a.ellipse.split(","))
    yy, xx = np.mgrid[0:H, 0:W]
    box = (((xx - cx) / float(rx)) ** 2 + ((yy - cy) / float(ry)) ** 2) <= 1.0
    R, G, B = arr[..., 0], arr[..., 1], arr[..., 2]
    matte = box & (G - B > a.sat_gb) & (G > a.lum_g)
    n0 = int(matte.sum())
    for _ in range(a.grow):
        s = matte.copy()
        s[1:, :] |= matte[:-1, :]; s[:-1, :] |= matte[1:, :]
        s[:, 1:] |= matte[:, :-1]; s[:, :-1] |= matte[:, 1:]
        matte = s & box
    n = int(matte.sum())
    print("plate %dx%d sha %s" % (W, H, have))
    print("fig matte: %d px core -> %d grown, ellipse %s (%d px), fill %.0f%%"
          % (n0, n, a.ellipse, int(box.sum()), 100.0 * n / box.sum()))
    if n < 800:
        raise SystemExit("!! matte only %d px -- the ellipse or the rule is "
                         "wrong; recolouring a sliver silently is how a fault "
                         "ships." % n)
    out = arr.astype(np.float32).copy()
    px = out[matte] / 255.0
    for i in range(px.shape[0]):
        r, g, b = px[i]
        h_, s_, v_ = colorsys.rgb_to_hsv(r, g, b)
        r2, g2, b2 = colorsys.hsv_to_rgb(a.hue, min(1.0, s_ * a.sat_scale), v_)
        px[i] = (r2, g2, b2)
    out[matte] = px * 255.0
    comp = np.clip(out, 0, 255).astype(np.uint8)
    changed = (np.abs(comp.astype(np.int16) - arr).max(axis=2) > 0)
    leak = int((changed & ~matte).sum())
    if leak:
        raise SystemExit("!! %d px changed outside the matte" % leak)
    print("recoloured %d px to hue %.2f, V kept per pixel; 0 px outside" % (n, a.hue))
    if a.matte_out:
        ov = np.asarray(img).copy()
        ov[matte] = (255, 40, 200)
        Image.fromarray(ov).save(a.matte_out)
        print("matte overlay: %s" % a.matte_out)
    if a.dry_run:
        print("dry run -- recoloured plate not written")
        return
    Image.fromarray(comp).save(a.out)
    print("out written: %s  sha256 %s" % (a.out, sha256_of(a.out)))


if __name__ == "__main__":
    main()
