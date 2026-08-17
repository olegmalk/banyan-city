#!/usr/bin/env python3
"""Beat 14: composite a CONTINUOUS GRASS FIELD into the plate, then let a
LOW-strength inpaint finish it. No sampler in this half. $0, no GPU, no network.

WHY THIS EXISTS. Four draws of beat 14's byte-identical r6 prompt scored
6/7, 6/7, 3/7, 6/7 and NOT ONE cleared all seven: P4' (dirt within a green
FIELD) passed only on r6 and failed 3 of 4, so r6's continuous grass ring was a
lucky draw rather than a property of the wording. 0 usable in 4 on a recipe with
an established 6/7 ceiling is not a sampling problem, so no more seeds are fired.
The field goes into the PIXELS instead, per the house pattern in
pipeline/composite-init-pattern.md (6a1b2f51): put the structure in with plain
image processing, then denoise at 0.30 so the sampler only FINISHES what is
already there. At 40 steps x 0.30 only 12 steps run and the early high-sigma
steps where global layout is decided never run.

THE BAR AND WHAT FAILURE MEANS were pre-registered at d850c276 BEFORE this file
existed: pipeline/loop/beat14-field-init-0817.md. F1-F6 are what this composite
must guarantee, C1-C8 are how it is checked, and any C out of band is a FAIL that
stops the run before any GPU is touched.

ADDITIVE ONLY. The eyewear lane proved masked ADDITION works (5 of 5) while
masked REMOVAL fails: a thin band along an object's own outline THINS it rather
than deleting it, because the unmasked pixels either side still describe it. So
the grass ring is composited IN. Nothing is erased, nothing is masked out, and
the vacancy law ("an emptied region is a hole the model fills with the largest
available noun, and the negative does not reach it") is satisfied by
construction.

GEOMETRY IS READ OFF A COORDINATE GRID, NOT EYEBALLED. The numbers below were
read from a 104x152 grid drawn over the plate. They are the steward's and are the
first thing a correction should move.
"""

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO = Path(__file__).resolve().parent.parent
W, H = 832, 1216

# The 6/7 base: fails only P4'. Its sha is asserted before anything runs.
PLATE = (REPO / "farm-out" / "ep2-b14-mac-plate-0817"
         / "14-the-defense-mac-plate-r7s1.png")
PLATE_SHA = None  # filled from --init-sha256

# --- geometry, read off the grid ---------------------------------------------
# The bare CLEARING that must stay bare earth: the dug patch under his hands
# plus a margin. P4' wants "bare brown soil under or around his hands" and Q14
# is the fail where grass closes over it, so this is a guarantee (F2), not a
# preference. Dug patch measured at x 195..500, y 865..1065.
SOIL_ELLIPSE = (350, 965, 205, 140)          # cx, cy, rx, ry
# Seed inside the figure, for the largest-connected-component pick. His skull.
FIGURE_SEED = (416, 380)
# Where the figure certainly is NOT, for the low-pass light field's reference.
# (top-left sand, read off the grid)
FIGURE_PROTECT_PAD = 7   # px standoff for the inpaint mask
FIGURE_TINT_PAD = 2      # px the ground tint stops short of him


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dilate(m: np.ndarray, r: int) -> np.ndarray:
    """Binary dilation by a square structuring element, r px, numpy only."""
    out = m.copy()
    for _ in range(r):
        s = out.copy()
        s[1:, :] |= out[:-1, :]
        s[:-1, :] |= out[1:, :]
        s[:, 1:] |= out[:, :-1]
        s[:, :-1] |= out[:, 1:]
        out = s
    return out


def reach(seed: np.ndarray, allow: np.ndarray, limit: int = 4000) -> np.ndarray:
    """Flood `seed` through `allow` by repeated dilation. scipy is not installed
    on this machine and a Python BFS over 1M px is not worth writing."""
    cur = seed & allow
    for _ in range(limit):
        nxt = dilate(cur, 1) & allow
        if nxt.sum() == cur.sum():
            return nxt
        cur = nxt
    return cur


def figure_matte(a: np.ndarray) -> np.ndarray:
    """His silhouette. FITTED TO THE OBJECT, NOT TO A BOX -- composite-init
    §4.2 names that as the strongest single defence against reading as a decal,
    and it is also what lets the grass come right up to him so he is IN a field
    rather than surrounded by a border.

    Measured on this plate: skin greenness (G - (R+B)/2) runs well above +25;
    the pale sand plane measures -8..+7; the cloak is purple (B > G) where every
    ground pixel here is warm (R > G > B); the collar is bright and neutral
    where sand is bright and warm (R-B = 65).
    """
    R, G, B = a[..., 0].astype(np.int16), a[..., 1].astype(np.int16), a[..., 2].astype(np.int16)
    V = a.max(axis=2).astype(np.int16)
    gm = G - (R + B) // 2
    skin = gm > 22
    cloak = (B > G + 6) & (V < 215)
    collar = (V > 200) & (np.abs(R - B) < 26)
    dark = (V < 62) & (B >= G - 4)
    seedm = skin | cloak | collar | dark
    # The plate's own grass clumps are green too, so a colour rule alone would
    # matte them as "figure". Connectivity separates them: he is ONE blob in the
    # middle and the clumps touch the frame edges.
    s = np.zeros((H, W), bool)
    s[FIGURE_SEED[1], FIGURE_SEED[0]] = True
    fig = reach(s, seedm)
    # close holes: flood the complement from the border, whatever is left is a hole
    outside = np.zeros((H, W), bool)
    outside[0, :] = outside[-1, :] = True
    outside[:, 0] = outside[:, -1] = True
    fig |= ~reach(outside, ~fig)
    return fig


def grass_palette(a: np.ndarray, keep: np.ndarray) -> dict:
    """F4: the blade colours are SAMPLED FROM THE PLATE'S OWN GRASS, never
    chosen. Colour does not travel between backends and a hand-picked green is a
    guess about a dialect we can just measure."""
    R, G, B = a[..., 0].astype(np.int16), a[..., 1].astype(np.int16), a[..., 2].astype(np.int16)
    gm = G - (R + B) // 2
    blade = (gm > 20) & ~keep
    px = a[blade]
    if len(px) < 500:
        raise SystemExit("!! only %d plate grass px found; the palette cannot be "
                         "measured and will not be guessed." % len(px))
    lo = np.percentile(px, 25, axis=0).astype(int)
    mid = np.percentile(px, 55, axis=0).astype(int)
    hi = np.percentile(px, 85, axis=0).astype(int)
    return {"n_px": int(len(px)), "dark": tuple(lo), "mid": tuple(mid),
            "light": tuple(hi)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", default=str(PLATE))
    ap.add_argument("--init-sha256", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mask-out", required=True)
    ap.add_argument("--seed", type=int, default=14)
    ap.add_argument("--density", type=float, default=1.0)
    a = ap.parse_args()

    init = Path(a.init)
    have = sha256_of(init)
    if have != a.init_sha256:
        print("!! init sha mismatch\n   want %s\n   have %s" % (a.init_sha256, have))
        return 2
    im = Image.open(init).convert("RGB")
    if im.size != (W, H):
        print("!! init is %s, expected %dx%d" % (im.size, W, H)); return 2
    arr = np.asarray(im)

    fig_raw = figure_matte(arr)
    # TWO PADS, and the reason is a defect v5 showed by eye. A single 7px pad left
    # a PALE SAND HALO tracing his whole silhouette -- the untinted rim between
    # his outline and the protect boundary -- which is decal tell #3, a swatch
    # stopping short of the object's own edge, drawn by the compositor itself.
    # So the ground is tinted up to 2px off him (no halo) while the INPAINT MASK
    # keeps the full 7px standoff, so the sampler still cannot reach him.
    fig = dilate(fig_raw, FIGURE_TINT_PAD)
    fig_mask = dilate(fig_raw, FIGURE_PROTECT_PAD)
    soil = np.zeros((H, W), bool)
    cx, cy, rx, ry = SOIL_ELLIPSE
    yy, xx = np.mgrid[0:H, 0:W]
    soil |= (((xx - cx) / float(rx)) ** 2 + ((yy - cy) / float(ry)) ** 2) <= 1.0
    keep = fig | soil
    paint = ~keep

    pal = grass_palette(arr, keep)
    print("PALETTE measured from %d plate grass px: dark=%s mid=%s light=%s"
          % (pal["n_px"], pal["dark"], pal["mid"], pal["light"]))

    # ---- the SWARD, and why v1 failed its own bar -------------------------
    # v1 drew blades onto the sand and nothing else. It changed 31% of the frame
    # and its largest connected green component was 0.9%: separate blades over a
    # sand plane are exactly the FRINGE P4' rules out, drawn by hand instead of
    # sampled. C1/C2/C3 caught it before any GPU ran, which is the whole point of
    # doing this with image processing.
    #
    # A field seen from above is GREEN GROUND with blades on it. So the ground is
    # recoloured first, by mapping the plate's OWN LUMINANCE through a ramp
    # between the measured dark and light grass colours. That keeps every pebble,
    # hatch stroke, clod and his cast shadow as texture in the sward -- the
    # plate's light and detail are preserved by construction rather than
    # re-applied -- and it is the direct answer to Q16, the fail where a composite
    # buys P4' by handing P5 a smooth green wash.
    lum = np.asarray(im.convert("L")).astype(np.float32)
    p10, p90 = np.percentile(lum[paint], 8), np.percentile(lum[paint], 92)
    t = np.clip((lum - p10) / max(1.0, p90 - p10), 0.0, 1.0)
    dk = np.array(pal["dark"], np.float32)
    lt = np.array(pal["light"], np.float32)
    sward = dk[None, None, :] + (lt - dk)[None, None, :] * t[..., None]
    # Mottling at two scales so the sward is patchy ground, never a flat field of
    # one green. Deterministic off --seed.
    mrng = np.random.default_rng(a.seed + 991)
    def mottle(cell, amp):
        small = mrng.uniform(-amp, amp, (H // cell + 2, W // cell + 2)).astype(np.float32)
        return np.asarray(Image.fromarray(
            ((small + 1.0) * 127.5).clip(0, 255).astype(np.uint8)
        ).resize((W, H), Image.BICUBIC)).astype(np.float32) / 127.5 - 1.0
    sward *= (1.0 + mottle(46, 0.11) + mottle(11, 0.05))[..., None]
    # Feather the sward's inner boundary against the bare clearing so the join is
    # a soft edge in the plate's own dialect, not a paste box (decal tell #3/#7).
    q = np.sqrt(((xx - cx) / float(rx)) ** 2 + ((yy - cy) / float(ry)) ** 2)
    alpha = np.clip((q - 1.0) / 0.22, 0.0, 1.0)
    alpha[fig] = 0.0
    base_f = arr.astype(np.float32)
    ground = np.clip(base_f * (1 - alpha[..., None]) + sward * alpha[..., None],
                     0, 255).astype(np.uint8)
    im_ground = Image.fromarray(ground)

    # ---- draw the field ---------------------------------------------------
    # F5: blade height scales with depth. The top of frame is farther away in a
    # `from above` shot, so blades there are shorter and denser; near the bottom
    # they are taller. Decal tell #5 is detail at the wrong scale read against an
    # in-frame ruler, and his hand is the ruler.
    rng = np.random.default_rng(a.seed)
    layer = Image.new("RGB", (W, H))
    layer.paste(im_ground)
    d = ImageDraw.Draw(layer)
    # Outline colour: a mid-dark green, DELIBERATELY not near-black. Q15 / bark's
    # split lesson: in this dialect a strong dark line IS an edge, and a
    # composited line stronger than the object's own outline gets resolved as an
    # object boundary at the rung above.
    # THE OUTLINE MUST STILL BE VEGETATION. A uniform 0.45x darkening of the
    # measured dark green gave (68,72,45) -- greenness 18, sitting exactly ON the
    # threshold the checks use -- so v3/v4's dense blade ink formed a NET of
    # non-green lines that cut the sward into thousands of small cells: C1 read
    # 1.7% and 0 of 4 edges on a composite whose field is visually continuous.
    # The fix is the INK, not the check: a cel outline in this dialect is a DARK
    # GREEN, not a desaturated olive, so the darkening preserves the hue.
    outline = (int(pal["dark"][0] * 0.50), int(pal["dark"][1] * 0.62),
               int(pal["dark"][2] * 0.42))
    clumps = []
    step = 46.0 / max(0.2, a.density)
    y = -20.0
    while y < H + 40:
        depth = min(1.0, max(0.0, y / float(H)))
        row_step = step * (0.72 + 0.55 * depth)
        x = -30.0 + rng.uniform(0, row_step)
        while x < W + 30:
            px, py = int(x + rng.uniform(-9, 9)), int(y + rng.uniform(-7, 7))
            if 0 <= px < W and 0 <= py < H and paint[py, px]:
                clumps.append((px, py, depth))
            x += row_step
        y += row_step * 0.78
    # A BLADE IS A TAPERED POLYGON, NOT A STRING OF DOTS. v2 stamped 5-6 shrinking
    # ellipses along each bezier and at this scale they read as beaded chains --
    # decal tell #4 (a visible repeat) and #5 (detail at the wrong scale, read
    # against his hand as the in-frame ruler). Caught by eye at 1x before any GPU
    # ran, which is what image processing buys: a rejection costs seconds.
    def blade(base, mid, tip, wdt, col, oc):
        pts, n = [], 9
        left, right = [], []
        for i in range(n + 1):
            t = i / float(n)
            bx = (1 - t) ** 2 * base[0] + 2 * (1 - t) * t * mid[0] + t ** 2 * tip[0]
            by = (1 - t) ** 2 * base[1] + 2 * (1 - t) * t * mid[1] + t ** 2 * tip[1]
            dx = 2 * (1 - t) * (mid[0] - base[0]) + 2 * t * (tip[0] - mid[0])
            dy = 2 * (1 - t) * (mid[1] - base[1]) + 2 * t * (tip[1] - mid[1])
            L = max(1e-3, (dx * dx + dy * dy) ** 0.5)
            nx, ny = -dy / L, dx / L
            r = wdt * (1.0 - t) ** 0.85
            left.append((bx + nx * r, by + ny * r))
            right.append((bx - nx * r, by - ny * r))
        pts = left + right[::-1]
        d.polygon(pts, fill=col, outline=oc)

    # PATCHINESS, so the field is not wallpaper. A low-frequency field thins the
    # clumps in places and a per-clump size jitter breaks the uniform hatch --
    # decal tell #4 is a visible repeat, and a perfectly even field of blades is
    # one.
    patch = mottle(88, 1.0)
    for px, py, depth in clumps:
        if rng.random() > 0.58 + 0.42 * (0.5 + 0.5 * patch[py, px]):
            continue
        hgt = (52 + 86 * depth) * rng.uniform(0.72, 1.28)
        nb = int(rng.integers(5, 10))
        for _ in range(nb):
            lean = rng.uniform(-0.70, 0.70)
            L = hgt * rng.uniform(0.55, 1.20)
            wdt = 2.4 + 2.6 * depth
            tip = (px + lean * L, py - L)
            mid = (px + lean * L * 0.40 + rng.uniform(-7, 7), py - L * 0.58)
            shade = rng.random()
            col = pal["light"] if shade > 0.74 else (pal["mid"] if shade > 0.34 else pal["dark"])
            blade((px + rng.uniform(-3, 3), py), mid, tip, wdt,
                  tuple(int(v) for v in col), outline)

    drawn = np.asarray(layer).astype(np.int16)
    base = arr.astype(np.int16)
    changed = (np.abs(drawn - base).max(axis=2) > 0) & paint

    # F5, second half: THE PLATE'S OWN LIGHT IS KEPT. Its low-frequency luminance
    # field -- which carries his cast shadow and the frame's lighting gradient --
    # is re-applied multiplicatively over the drawn grass. A flat sticker has none
    # of that, and that is what makes one read as a sticker (composite-init §4.3).
    lp = np.asarray(im.convert("L").filter(ImageFilter.GaussianBlur(58))).astype(np.float32)
    ref = float(lp[changed].mean()) if changed.any() else float(lp.mean())
    gain = np.clip(lp / max(1.0, ref), 0.86, 1.14)[..., None]
    lit = np.clip(drawn.astype(np.float32) * gain, 0, 255).astype(np.uint8)
    out = arr.copy()
    out[changed] = lit[changed]
    comp = Image.fromarray(out)

    # ---- the mask ---------------------------------------------------------
    # C8, and it is not decoration. A mask drawn only over what I painted would
    # make the result a foregone conclusion and measure nothing. This mask is the
    # whole paint region, which CONTAINS the plate's own fringe clumps, so a
    # fringe-not-a-field outcome is still reachable and the bar stays falsifiable.
    mask = np.zeros((H, W), np.uint8)
    mask[dilate(paint, 2) & ~fig_mask] = 255
    Image.fromarray(mask).save(a.mask_out)

    # ---- the checks -------------------------------------------------------
    o = np.asarray(comp).astype(np.int16)
    gm = o[..., 1] - (o[..., 0] + o[..., 2]) // 2
    green = (gm > 18) & ~fig
    fails = []
    if not (green & paint).any():
        print("FAIL-C1 no green painted"); return 3
    # SEED THE FLOOD FROM A DEEP INTERIOR PIXEL, NOT THE TOPMOST ONE. v3 scored
    # C1 at 0.0% on a composite whose sward was fine: the first nonzero green
    # pixel was a blade tip in row 0, ringed by its own dark outline, so the
    # flood measured a 46 px island and the retry loop kept picking its
    # neighbours. Eroding first guarantees the seed is inside a large region --
    # a measurement bug that would have been read as a compositor failure.
    er = green.copy()
    for _ in range(6):
        e = er.copy()
        e[1:, :] &= er[:-1, :]; e[:-1, :] &= er[1:, :]
        e[:, 1:] &= er[:, :-1]; e[:, :-1] &= er[:, 1:]
        er = e
    comp_green = np.zeros((H, W), bool)
    pool = er if er.any() else green
    for _ in range(6):
        rest = pool & ~comp_green
        if not rest.any():
            break
        ry_, rx_ = np.nonzero(rest)
        s2 = np.zeros((H, W), bool); s2[ry_[len(ry_) // 2], rx_[len(rx_) // 2]] = True
        cand = reach(s2, green)
        if cand.sum() > comp_green.sum():
            comp_green = cand
        pool = pool & ~cand
    c1 = comp_green.sum() / float(W * H)
    edges = sum([comp_green[0, :].any(), comp_green[-1, :].any(),
                 comp_green[:, 0].any(), comp_green[:, -1].any()])
    fx0, fx1 = np.nonzero(fig.any(axis=0))[0][[0, -1]]
    fy0, fy1 = np.nonzero(fig.any(axis=1))[0][[0, -1]]
    left = comp_green[:, :fx0].sum(); right = comp_green[:, fx1:].sum()
    above = comp_green[:fy0, :].sum(); below = comp_green[fy1:, :].sum()
    c3 = (left > 3000 and right > 3000) or (above > 3000 and below > 3000)
    bare = soil & ~green
    c4 = int(bare.sum())
    c5 = int(np.abs(o - base)[fig].max()) if fig.any() else 0
    plate_dark = int(np.asarray(im.convert("L"))[paint].min())
    drawn_dark = int(np.asarray(comp.convert("L"))[changed].min()) if changed.any() else 255
    # C8: the mask must contain the plate's own fringe clumps
    plate_green = (base[..., 1] - (base[..., 0] + base[..., 2]) // 2) > 20
    clump_in_mask = int((plate_green & (mask > 0)).sum())

    print("C1 largest green component %.1f%% of frame        (>= 12%%)  %s"
          % (100 * c1, "PASS" if c1 >= 0.12 else "FAIL"))
    print("C2 frame edges it touches %d of 4                 (>= 3)    %s"
          % (edges, "PASS" if edges >= 3 else "FAIL"))
    print("C3 green on both sides of him L=%d R=%d A=%d B=%d  %s"
          % (left, right, above, below, "PASS" if c3 else "FAIL"))
    print("C4 bare earth retained in the clearing %d px      (>= 8000) %s"
          % (c4, "PASS" if c4 >= 8000 else "FAIL"))
    print("C5 maxdiff inside the figure matte %d             (== 0)    %s"
          % (c5, "PASS" if c5 == 0 else "FAIL"))
    print("C6 darkest drawn luma %d vs plate's own %d        (>=)      %s"
          % (drawn_dark, plate_dark, "PASS" if drawn_dark >= plate_dark else "FAIL"))
    print("C8 plate's own grass px inside the mask %d        (> 0)     %s"
          % (clump_in_mask, "PASS" if clump_in_mask > 0 else "FAIL"))
    if c1 < 0.12: fails.append("FAIL-CONTINUITY(C1)")
    if edges < 3: fails.append("FAIL-CONTINUITY(C2)")
    if not c3: fails.append("FAIL-ONE-SIDED(C3)")
    if c4 < 8000: fails.append("FAIL-SOIL-SWALLOWED(C4,Q14)")
    if c5 != 0: fails.append("FAIL-FIGURE-TOUCHED(C5,Q13)")
    if drawn_dark < plate_dark: fails.append("FAIL-LINE-TOO-STRONG(C6,Q15)")
    if clump_in_mask == 0: fails.append("FAIL-UNFALSIFIABLE(C8)")

    comp.save(a.out)
    sha = sha256_of(Path(a.out))
    print("C7 determinism: composite sha256 %s" % sha)
    print("figure matte %d px (%.1f%%), paint region %d px (%.1f%%), changed %d px"
          % (fig.sum(), 100.0 * fig.sum() / (W * H), paint.sum(),
             100.0 * paint.sum() / (W * H), changed.sum()))
    meta = {
        "tool": "pipeline/beat14_field_composite.py",
        "sampler": "NONE -- plain image processing, $0, no GPU, no network",
        "bar": "pipeline/loop/beat14-field-init-0817.md (d850c276), pre-registered",
        "init": str(init.relative_to(REPO)),
        "init_sha256": have,
        "composite_sha256": sha,
        "mask_png": Path(a.mask_out).name,
        "rng_seed": a.seed,
        "density": a.density,
        "soil_ellipse_px": list(SOIL_ELLIPSE),
        "figure_seed_px": list(FIGURE_SEED),
        "figure_protect_pad_px": FIGURE_PROTECT_PAD,
        "palette_measured_from_plate": {k: (list(v) if isinstance(v, tuple) else v)
                                        for k, v in pal.items()},
        "checks": {"C1_green_frac": round(float(c1), 4), "C2_edges": edges,
                   "C3_both_sides": bool(c3), "C4_bare_px": c4,
                   "C5_figure_maxdiff": c5, "C6_drawn_dark": drawn_dark,
                   "C6_plate_dark": plate_dark, "C8_plate_grass_in_mask": clump_in_mask},
        "fails": fails,
        "geometry_is_the_stewards": (
            "Read off a 104x152 coordinate grid drawn over the plate, not "
            "eyeballed. The founder approved fixing beat 14 properly and named no "
            "geometry; these numbers are the first thing a correction should move."),
        "date": date.today().isoformat(),
        "approved": False,
        "provisional": True,
    }
    Path(a.out + ".meta.yaml").write_text(
        "\n".join("%s: %s" % (k, json.dumps(v, default=int))
                  for k, v in meta.items()) + "\n")
    if fails:
        print("COMPOSITE FAILED: %s -- no GPU runs on a failed composite." % ", ".join(fails))
        return 3
    print("COMPOSITE PASSES C1-C8. Now open it by eye at 1x and 3x: a metric is a "
          "filter, never a verdict.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
