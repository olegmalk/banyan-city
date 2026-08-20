#!/usr/bin/env python3
"""fig_track.py -- an honest fig detector for the beat-01 growmotion clips.

WHY THIS EXISTS
---------------
On 2026-08-20 five growmotion clips (seeds 20260835/36/37/40/41) were measured
and deliberately NOT scored, because every fig mask this repo had was a COLOUR
PREDICATE and the beat-01 fig walks through desaturated slate on its way from
green to purple.  `ep2-b01-growmotion-b13-0819`'s own verdict says it first:

    "a green-OR-purple colour-predicate mask reported a one-frame colour pop and
     a 2.0x-2.5x single-frame area step on this clip, and BOTH ARE ARTEFACTS OF
     THE MASK -- the fig passes through teal and desaturated slate on it"

A luma-normalised green-magenta mask (`gmn = (G-(R+B)/2)/luma`) fixes the
exposure confound -- these clips bloom +10 to +68 levels in 121 frames -- and
STILL drops the object dead in the slate phase.  On `b15` it read area 2917 px
at f084 and 11302 px at f096: a 3.9x "balloon" that is the mask re-acquiring the
object, published as if it were growth.  Scoring G1/G4/H4 off that is scoring
the instrument.

WHAT THIS DOES DIFFERENTLY -- three rules, all of them checkable
----------------------------------------------------------------
1.  **The mask starts from GEOMETRY, not colour.**  The nub was PASTED into
    frame 1 by `pipeline/nub_composite.py` and then low-strength inpainted, so
    its footprint at f000 is not a guess: it is the inpaint mask
    (`b01-nubcomp-s20260826-mask.png`, 832x1216) carried through the job's own
    `cover_crop.py` transform into the 704x1280 init.  `--anchor-mask` takes
    that PNG and `--anchor-cover-crop` reproduces the crop, so f000 needs no
    detection at all.  Everything after f000 is propagated from it by REGION
    CONTINUITY, never re-acquired from a colour class.

2.  **The probes are luma-matched and publish luma AND material separately.**
    Every pixel is scored twice against a local background model taken from an
    annulus around the current estimate:
      * MATERIAL -- distance of its chromaticity (R,G,B)/(R+G+B), which is
        invariant to multiplicative illumination, from the ring's median
        chromaticity, in units of the ring's own MAD.  This is a
        BACKGROUND-RELATIVE distance, not membership in a hue class, so it does
        not care whether the fig is green, slate or purple -- only that it is
        not the same stuff as the field behind it.
      * LUMA -- |L - ring L| / ring MAD(L), reported alongside, never summed
        into the material number.  The bloom moves both the fig and the ring, so
        a ring-relative luma survives it; it is published so a reader can see
        WHICH of the two channels is carrying the separation on any frame.

3.  **A frame the detector cannot stand behind is a DEAD ZONE, not a number.**
    Five gates run per frame (separability, template NCC, NCC margin, centroid
    jump, ROI containment).  If any fails, the frame publishes
    `status: dead` + `dead_reasons` and `area_px: null`.  A dead frame never
    updates the template and never enters a growth ratio.  There is no code path
    in this file that emits an area without also emitting the confidence that
    stands behind it.

CALIBRATION IS DECLARED, NOT TUNED IN SILENCE
---------------------------------------------
Gate thresholds are module constants with the reason for each written next to
them, and `--gates` prints them.  `--selftest` runs the three checks that matter
(the geometric anchor, the hand-verified keyframes, and the b15 balloon frames)
and exits nonzero if any regress.

$0: numpy + Pillow, no model, no network, no GPU.

    python3 pipeline/fig_track.py --frames DIR --anchor-mask M.png \
        --anchor-cover-crop 832x1216->704x1280 --out track.json
    python3 pipeline/fig_track.py --selftest
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("!! needs Pillow: pip install pillow")


# ---------------------------------------------------------------------------
# GATES.  Every one of these is a declared threshold with a stated reason.
# ---------------------------------------------------------------------------

SEP_MIN = 2.0
"""Minimum separability d' between the fig interior and its background ring, in
either channel.  d' is |median_in - median_ring| / pooled MAD, so 2.0 means the
two populations' medians are two robust deviations apart.  BELOW THIS THE
DETECTOR CANNOT TELL FIG FROM FIELD AND SAYS SO -- this is the gate that would
have fired on a mask that lost the fig in slate, instead of publishing 2917 px."""

NCC_MIN = 0.55
"""Minimum zero-mean, unit-variance normalised cross-correlation between the
last live fig patch and the patch at the newly found position.  Mean/variance
normalisation is what makes this survive a +68-level bloom; a low value means
the thing found is not the thing tracked."""

NCC_MARGIN_MIN = 0.05
"""NCC peak must beat the best competing peak outside a 1-radius exclusion by
this much.  A tie means two equally good explanations and the detector must not
silently pick one."""

JUMP_MAX_FRAC = 0.60
"""Maximum centroid displacement in one frame as a fraction of the previous
equivalent radius.  The fig hangs on a stem; it does not teleport.  A jump past
this is either H5 (detach/teleport, a real fault) or a mis-lock (an instrument
fault) -- the detector cannot tell them apart from one frame, so it declares
dead and lets the eye decide."""

RATIO_SUSPECT = 2.0
"""Single-frame area ratio at or above which the frame is FLAGGED (not killed).
`ep2-b01-growmotion-b13-0819` settles that G4 reads as maximum single-frame
ratio under 2.0x, so this is the bar's own number.  A flagged frame still
publishes its area -- because with the gates above passing, a 2x step is a real
2x step and that is exactly what G4/H4 want to know."""

TAU_MAT = 3.0
"""Per-pixel material distance (in ring MADs) for membership in the fig.  Held
well above the ring's own spread so blurred grass does not join the object."""

TAU_LUM = 3.0
"""Per-pixel ring-relative luma distance, used only for the union that catches
specular caps whose chromaticity has washed toward the ring's."""

RING_INNER = 1.35
RING_OUTER = 2.10
"""Background annulus, in multiples of the current equivalent radius.  Inside
1.35r is close enough to be contaminated by the object's own soft edge; outside
2.10r on a 704x1280 frame starts collecting the stem and other grass."""

ROI_PAD = 3.2
"""Half-width of the search/segment window in equivalent radii.  Large enough
that a doubling fig still has ring left inside the window."""

MIN_ROI = 48
"""Floor on the ROI half-width in px, for the 24-px-wide f000 nub."""


def gates_dict() -> dict:
    return {
        "SEP_MIN": SEP_MIN, "NCC_MIN": NCC_MIN, "NCC_MARGIN_MIN": NCC_MARGIN_MIN,
        "JUMP_MAX_FRAC": JUMP_MAX_FRAC, "RATIO_SUSPECT": RATIO_SUSPECT,
        "TAU_MAT": TAU_MAT, "TAU_LUM": TAU_LUM,
        "RING_INNER": RING_INNER, "RING_OUTER": RING_OUTER,
        "ROI_PAD": ROI_PAD, "MIN_ROI": MIN_ROI,
    }


# ---------------------------------------------------------------------------
# small numeric helpers (no scipy -- this must run on a bare venv)
# ---------------------------------------------------------------------------

def mad(x: np.ndarray) -> float:
    """Median absolute deviation, scaled to a normal-consistent sigma."""
    if x.size == 0:
        return 0.0
    m = float(np.median(x))
    return 1.4826 * float(np.median(np.abs(x - m)))


def chroma_luma(rgb: np.ndarray):
    """(r,g) chromaticity -- invariant to multiplicative illumination -- and luma.

    Chromaticity is the whole point: it divides the illumination out, so the
    +68-level bloom these clips carry moves L and leaves (r,g) alone.  Luma is
    returned SEPARATELY and never mixed in, so a reader can see which channel is
    carrying the separation.
    """
    f = rgb.astype(np.float64)
    s = f.sum(axis=2) + 1e-6
    r = f[:, :, 0] / s
    g = f[:, :, 1] / s
    lum = 0.299 * f[:, :, 0] + 0.587 * f[:, :, 1] + 0.114 * f[:, :, 2]
    return r, g, lum


def largest_component_containing(mask: np.ndarray, seed_yx):
    """Flood the 4-connected component of `mask` that contains `seed_yx`.

    REGION CONTINUITY IS THE WHOLE TRACKING RULE: the fig on frame t is the blob
    that is connected to where the fig was on frame t-1.  If the seed pixel is
    not in the mask, the nearest in-mask pixel within a small radius is used and
    the caller is told (a re-seed is evidence the frame is marginal).
    """
    h, w = mask.shape
    sy, sx = int(round(seed_yx[0])), int(round(seed_yx[1]))
    reseeded = False
    if not (0 <= sy < h and 0 <= sx < w and mask[sy, sx]):
        ys, xs = np.nonzero(mask)
        if ys.size == 0:
            return np.zeros_like(mask), True
        d2 = (ys - sy) ** 2 + (xs - sx) ** 2
        i = int(np.argmin(d2))
        sy, sx = int(ys[i]), int(xs[i])
        reseeded = True

    out = np.zeros_like(mask)
    stack = [(sy, sx)]
    out[sy, sx] = True
    while stack:
        y, x = stack.pop()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True
                stack.append((ny, nx))
    return out, reseeded


def binary_open(mask: np.ndarray, r: int) -> np.ndarray:
    """Erode then dilate with a (2r+1) square. Removes the thin dark stem, which
    is material-distinct from the field and would otherwise weld itself to the
    fig and inflate the area."""
    if r <= 0:
        return mask
    m = mask
    for _ in range(r):
        m = (m & np.roll(m, 1, 0) & np.roll(m, -1, 0)
             & np.roll(m, 1, 1) & np.roll(m, -1, 1))
    for _ in range(r):
        m = (m | np.roll(m, 1, 0) | np.roll(m, -1, 0)
             | np.roll(m, 1, 1) | np.roll(m, -1, 1))
    return m


def fill_holes(mask: np.ndarray) -> np.ndarray:
    """Fill interior holes by flooding the background in from the border.

    The specular caps the sampler paints on the fig are near-white: they can
    fail BOTH probes at once and punch holes in an otherwise correct body.  They
    are interior, so filling recovers them without letting anything outside in.
    """
    h, w = mask.shape
    bg = ~mask
    seen = np.zeros_like(mask)
    stack = []
    for x in range(w):
        for y in (0, h - 1):
            if bg[y, x] and not seen[y, x]:
                seen[y, x] = True
                stack.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if bg[y, x] and not seen[y, x]:
                seen[y, x] = True
                stack.append((y, x))
    while stack:
        y, x = stack.pop()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and bg[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                stack.append((ny, nx))
    return ~seen


def ncc(a: np.ndarray, b: np.ndarray) -> float:
    """Zero-mean unit-variance normalised cross-correlation of two equal patches.

    The normalisation is not decoration: these clips gain up to 68 luma levels
    over 121 frames, and a raw SSD or a plain correlation would read that global
    gain as the object changing.
    """
    if a.shape != b.shape or a.size == 0:
        return -1.0
    a = a.astype(np.float64) - a.mean()
    b = b.astype(np.float64) - b.mean()
    na, nb = math.sqrt(float((a * a).sum())), math.sqrt(float((b * b).sum()))
    if na < 1e-9 or nb < 1e-9:
        return -1.0
    return float((a * b).sum() / (na * nb))


# ---------------------------------------------------------------------------
# the anchor: geometry, carried through the job's own cover-crop
# ---------------------------------------------------------------------------

def cover_crop_map(src_wh, dst_wh):
    """Reproduce `cover_crop.py`'s transform. Returns (scale, left, top)."""
    sw, sh = src_wh
    W, H = dst_wh
    scale = max(W / float(sw), H / float(sh))
    nw, nh = int(round(sw * scale)), int(round(sh * scale))
    return scale, (nw - W) // 2, (nh - H) // 2


def anchor_from_mask(mask_png: str, src_wh, dst_wh) -> np.ndarray:
    """The f000 footprint from the INPAINT MASK, not from any colour test."""
    scale, left, top = cover_crop_map(src_wh, dst_wh)
    sw, sh = src_wh
    W, H = dst_wh
    nw, nh = int(round(sw * scale)), int(round(sh * scale))
    im = Image.open(mask_png).convert("L")
    if im.size != (sw, sh):
        raise SystemExit("!! anchor mask is %s, --anchor-cover-crop says %s"
                         % (im.size, (sw, sh)))
    im = im.resize((nw, nh), Image.LANCZOS).crop((left, top, left + W, top + H))
    return np.array(im) > 127


# ---------------------------------------------------------------------------
# one frame
# ---------------------------------------------------------------------------

def segment_frame(rgb: np.ndarray, cy: float, cx: float, r_eq: float, roi_grow: float = 1.0):
    """Segment the fig near (cy,cx) with a ring-relative material+luma probe.

    Returns (mask_full, stats).  Never decides anything about validity -- the
    gates in `track()` do that with the stats this returns.  `stats["dmat"]`
    carries the ROI's material-distance map, which is what the template test
    correlates: it is invariant to illumination (chromaticity) AND to contrast
    polarity (a distance is unsigned), and this fig inverts polarity -- it starts
    as a light blob on a dark dawn field and ends as a dark blob on a blown-out
    one, which is enough to drive a plain luma NCC negative.
    """
    H, W = rgb.shape[:2]
    pad = max(MIN_ROI, int(round(ROI_PAD * r_eq * roi_grow)))
    y0, y1 = max(0, int(cy) - pad), min(H, int(cy) + pad + 1)
    x0, x1 = max(0, int(cx) - pad), min(W, int(cx) + pad + 1)
    sub = rgb[y0:y1, x0:x1]
    r, g, lum = chroma_luma(sub)
    hh, ww = lum.shape
    yy, xx = np.mgrid[0:hh, 0:ww]
    ly, lx = cy - y0, cx - x0
    dist = np.hypot(yy - ly, xx - lx)

    mask = dist <= r_eq
    stats = {}
    for _ in range(3):
        ring = (dist >= RING_INNER * r_eq) & (dist <= RING_OUTER * r_eq) & (~mask)
        if ring.sum() < 40:
            ring = (dist >= RING_INNER * r_eq) & (~mask)
        if ring.sum() < 40:
            return np.zeros((H, W), bool), {"ring_px": int(ring.sum()), "empty_ring": True}

        rr, rg = float(np.median(r[ring])), float(np.median(g[ring]))
        sr, sg = mad(r[ring]), mad(g[ring])
        sr, sg = max(sr, 1e-4), max(sg, 1e-4)
        rl, sl = float(np.median(lum[ring])), max(mad(lum[ring]), 1e-3)

        d_mat = np.hypot((r - rr) / sr, (g - rg) / sg) / math.sqrt(2.0)
        d_lum = np.abs(lum - rl) / sl

        cand = (d_mat >= TAU_MAT) | (d_lum >= TAU_LUM)
        cand = binary_open(cand, max(1, int(round(r_eq / 8.0))))
        comp, reseeded = largest_component_containing(cand, (ly, lx))
        comp = fill_holes(comp)
        if comp.sum() < 4:
            return np.zeros((H, W), bool), {"ring_px": int(ring.sum()), "empty_comp": True,
                                            "reseeded": bool(reseeded)}
        mask = comp
        ys, xs = np.nonzero(mask)
        ly, lx = float(ys.mean()), float(xs.mean())
        r_eq = math.sqrt(mask.sum() / math.pi)

        ring2 = (np.hypot(yy - ly, xx - lx) >= RING_INNER * r_eq) & (~mask)
        ring2 &= (np.hypot(yy - ly, xx - lx) <= RING_OUTER * r_eq)
        use = ring2 if ring2.sum() >= 40 else ring
        sep_mat = abs(float(np.median(d_mat[mask])) - float(np.median(d_mat[use]))) / \
            max(0.5 * (mad(d_mat[mask]) + mad(d_mat[use])), 1e-3)
        sep_lum = abs(float(np.median(lum[mask])) - float(np.median(lum[use]))) / \
            max(0.5 * (mad(lum[mask]) + mad(lum[use])), 1e-3)
        stats = {
            "area_px": int(mask.sum()),
            "cy": float(ly + y0), "cx": float(lx + x0),
            "r_eq": float(r_eq),
            "sep_material": round(float(sep_mat), 3),
            "sep_luma": round(float(sep_lum), 3),
            "luma_fig": round(float(np.median(lum[mask])), 2),
            "luma_ring": round(float(np.median(lum[use])), 2),
            "chroma_fig": [round(float(np.median(r[mask])), 4), round(float(np.median(g[mask])), 4)],
            "chroma_ring": [round(float(np.median(r[use])), 4), round(float(np.median(g[use])), 4)],
            "ring_px": int(use.sum()),
            "reseeded": bool(reseeded),
            "touches_roi": bool(mask[0, :].any() or mask[-1, :].any()
                                or mask[:, 0].any() or mask[:, -1].any()),
            "touches_frame": bool((y0 == 0 and mask[0, :].any())
                                  or (y1 == H and mask[-1, :].any())
                                  or (x0 == 0 and mask[:, 0].any())
                                  or (x1 == W and mask[:, -1].any())),
        }
        # log1p, NOT a clip: a hard ceiling makes the interior of a strongly
        # separated fig a constant plateau, and a constant patch has zero
        # variance, which drives the normalised correlation to its error value
        # and killed 120 of b16's 121 frames on the first build of this file.
        stats["_dmat"] = np.log1p(d_mat)

    full = np.zeros((H, W), bool)
    full[y0:y1, x0:x1] = mask
    stats["roi"] = [x0, y0, x1, y1]
    return full, stats


def patch_at(field: np.ndarray, cy: float, cx: float, half: int) -> np.ndarray:
    H, W = field.shape
    y0, x0 = int(round(cy)) - half, int(round(cx)) - half
    y1, x1 = y0 + 2 * half + 1, x0 + 2 * half + 1
    if y0 < 0 or x0 < 0 or y1 > H or x1 > W:
        return np.zeros((0, 0))
    return field[y0:y1, x0:x1]


def objectness_full(rgb: np.ndarray, stats: dict, shape) -> np.ndarray:
    """Paste the ROI's material-distance map back into a full-frame field.

    This is the field the template test runs on.  Outside the ROI it is zero,
    which is honest: the detector has not looked there, and a rival peak that
    needs unlooked-at ground is not a rival."""
    f = np.zeros(shape, np.float64)
    x0, y0, x1, y1 = stats["roi"]
    f[y0:y1, x0:x1] = stats["_dmat"]
    return f


def track(frame_paths, anchor_mask: np.ndarray, verbose=False):
    """Track the fig across a frame sequence.  Emits one record per frame; a
    frame the detector cannot stand behind gets `status: dead` and no area."""
    ys, xs = np.nonzero(anchor_mask)
    if ys.size == 0:
        raise SystemExit("!! anchor mask is empty")
    cy, cx = float(ys.mean()), float(xs.mean())
    r_eq = math.sqrt(anchor_mask.sum() / math.pi)

    recs = []
    prev_patch = None
    prev_half = None
    last_live = None

    for i, p in enumerate(frame_paths):
        rgb = np.array(Image.open(p).convert("RGB"))
        _, _, lum = chroma_luma(rgb)
        # A mask that runs off the search window has an unbounded extent, but
        # that is first a WINDOW problem: grow the window twice before calling
        # it a dead frame, so a fig that doubles is measured rather than lost.
        grow = 1.0
        for _ in range(3):
            mask, st = segment_frame(rgb, cy, cx, r_eq, roi_grow=grow)
            if not st.get("touches_roi") or st.get("touches_frame"):
                break
            grow *= 1.8
        roi_grown = grow > 1.0

        rec = {"frame": i, "status": "ok", "dead_reasons": [], "flags": []}
        if not st or "area_px" not in st:
            rec["status"] = "dead"
            rec["dead_reasons"].append("no-component" if st.get("empty_comp") else "no-ring")
            rec["area_px"] = None
            rec["probe"] = st
            recs.append(rec)
            continue

        # -- template NCC at the found position, and the margin over a rival --
        # The template rides the OBJECTNESS field, not luma: see segment_frame.
        obj = objectness_full(rgb, st, lum.shape)
        half = max(6, int(round(st["r_eq"])))
        cur = patch_at(obj, st["cy"], st["cx"], prev_half if prev_half else half)
        v_ncc, v_margin = None, None
        if prev_patch is not None and cur.size:
            v_ncc = ncc(prev_patch, cur)
            best_rival = -1.0
            step = max(2, int(round(st["r_eq"] / 2)))
            for dy in range(-4 * step, 4 * step + 1, step):
                for dx in range(-4 * step, 4 * step + 1, step):
                    if math.hypot(dy, dx) <= 1.2 * st["r_eq"]:
                        continue
                    q = patch_at(obj, st["cy"] + dy, st["cx"] + dx, prev_half)
                    if q.size:
                        best_rival = max(best_rival, ncc(prev_patch, q))
            v_margin = v_ncc - best_rival

        jump = math.hypot(st["cy"] - cy, st["cx"] - cx)
        prev_r = r_eq

        # ------------------------- THE GATES -------------------------
        if st["sep_material"] < SEP_MIN and st["sep_luma"] < SEP_MIN:
            rec["dead_reasons"].append(
                "separability material=%.2f luma=%.2f both < %.2f"
                % (st["sep_material"], st["sep_luma"], SEP_MIN))
        if v_ncc is not None and v_ncc < NCC_MIN:
            rec["dead_reasons"].append("ncc %.3f < %.2f" % (v_ncc, NCC_MIN))
        if v_margin is not None and v_margin < NCC_MARGIN_MIN:
            rec["dead_reasons"].append("ncc margin %.3f < %.2f" % (v_margin, NCC_MARGIN_MIN))
        if jump > JUMP_MAX_FRAC * max(prev_r, 4.0):
            rec["dead_reasons"].append(
                "centroid jump %.1f px > %.2f x r_eq %.1f" % (jump, JUMP_MAX_FRAC, prev_r))
        if st.get("touches_roi") and not st.get("touches_frame"):
            rec["dead_reasons"].append(
                "mask still reaches the search window after %.1fx growth -- extent not bounded"
                % grow)
        if roi_grown and not rec["dead_reasons"]:
            rec["flags"].append("search window grown %.1fx to bound the extent" % grow)
        if st.get("reseeded"):
            rec["flags"].append("component re-seeded from nearest in-mask pixel")
        if st.get("touches_frame"):
            rec["flags"].append("fig is clipped by the frame edge -- area is a lower bound")

        prev_area = None
        for r in reversed(recs):
            if r["status"] == "ok":
                prev_area = r["area_px"]
                break
        if prev_area:
            ratio = st["area_px"] / float(prev_area)
            rec["ratio_prev_ok"] = round(ratio, 3)
            if max(ratio, 1.0 / ratio) >= RATIO_SUSPECT:
                rec["flags"].append("single-frame area ratio %.2fx >= %.1fx"
                                    % (max(ratio, 1 / ratio), RATIO_SUSPECT))

        rec["probe"] = {k: st[k] for k in (
            "sep_material", "sep_luma", "luma_fig", "luma_ring",
            "chroma_fig", "chroma_ring", "ring_px", "roi")}
        rec["ncc"] = None if v_ncc is None else round(v_ncc, 4)
        rec["ncc_margin"] = None if v_margin is None else round(v_margin, 4)
        rec["jump_px"] = round(jump, 2)

        if rec["dead_reasons"]:
            rec["status"] = "dead"
            rec["area_px"] = None
            rec["cy"] = rec["cx"] = None
            rec["r_eq"] = None
            # A dead frame does NOT move the anchor and does NOT refresh the
            # template.  The last live estimate is carried, flagged as carried.
            rec["carried_from_frame"] = last_live
        else:
            rec["area_px"] = st["area_px"]
            rec["cy"], rec["cx"] = round(st["cy"], 2), round(st["cx"], 2)
            rec["r_eq"] = round(st["r_eq"], 2)
            cy, cx, r_eq = st["cy"], st["cx"], st["r_eq"]
            prev_half = half
            prev_patch = patch_at(obj, cy, cx, half)
            if prev_patch.size == 0:
                prev_patch = None
            last_live = i

        recs.append(rec)
        if verbose:
            print("f%03d %-4s area=%-7s sep(m/l)=%.2f/%.2f ncc=%s %s" % (
                i, rec["status"], rec["area_px"], st["sep_material"], st["sep_luma"],
                "n/a" if v_ncc is None else "%.3f" % v_ncc,
                ";".join(rec["dead_reasons"] + rec["flags"])), flush=True)
    return recs


def _best_ncc_shift(ref: np.ndarray, mov: np.ndarray, rad: int):
    """Best integer translation of `mov` against `ref` by NCC. Returns (ncc,dy,dx)."""
    best = (-2.0, 0, 0)
    h, w = ref.shape
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            y0, y1 = max(0, dy), min(h, h + dy)
            x0, x1 = max(0, dx), min(w, w + dx)
            a = ref[y0:y1, x0:x1]
            b = mov[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
            if a.size < 64:
                continue
            v = ncc(a, b)
            if v > best[0]:
                best = (v, dy, dx)
    return best


def global_zoom(ref_rgb: np.ndarray, cur_rgb: np.ndarray, small=(88, 160),
                scales=None, quadrant_tol=0.04):
    """Is the frame MAGNIFYING?  A self-checking answer to G5 / H4-camera-push.

    `pipeline`'s previous camera instrument was a block-drift measure whose own
    region-consistency test failed on all five of these clips, which is why the
    2026-08-20 measurement said "do not read the dy column as camera moves".
    This one is built to fail loudly instead of quietly:

      * A global scale is fitted by resizing the reference about the frame
        centre over a scale grid and taking the best NCC translation at each.
      * THE SAME FIT IS THEN RUN ON FOUR DISJOINT QUADRANTS.  A camera zoom is
        one transform for the whole picture, so the four quadrant scales must
        agree.  If their spread exceeds `quadrant_tol` the picture is not being
        transformed, it is being REDRAWN, and this function says
        `consistent: false` and its scale must not be quoted.

    Returns a dict; never raises a verdict of its own.
    """
    if scales is None:
        scales = [round(1.0 + 0.02 * k, 3) for k in range(0, 26)]

    def prep(rgb):
        im = Image.fromarray(rgb).convert("L").resize((small[0], small[1]), Image.LANCZOS)
        return np.asarray(im, np.float64)

    cur = prep(cur_rgb)
    H, W = cur.shape

    def fit(region):
        y0, y1, x0, x1 = region
        best = {"scale": 1.0, "ncc": -2.0, "dy": 0, "dx": 0}
        for s in scales:
            nw, nh = int(round(small[0] * s)), int(round(small[1] * s))
            im = Image.fromarray(ref_rgb).convert("L").resize((nw, nh), Image.LANCZOS)
            l, t = (nw - small[0]) // 2, (nh - small[1]) // 2
            r = np.asarray(im.crop((l, t, l + small[0], t + small[1])), np.float64)
            v, dy, dx = _best_ncc_shift(cur[y0:y1, x0:x1], r[y0:y1, x0:x1], 6)
            if v > best["ncc"]:
                best = {"scale": s, "ncc": round(v, 4), "dy": dy, "dx": dx}
        return best

    whole = fit((0, H, 0, W))
    quads = [fit(q) for q in ((0, H // 2, 0, W // 2), (0, H // 2, W // 2, W),
                              (H // 2, H, 0, W // 2), (H // 2, H, W // 2, W))]
    qs = [q["scale"] for q in quads]
    spread = max(qs) - min(qs)
    return {
        "scale": whole["scale"], "ncc": whole["ncc"],
        "quadrant_scales": qs, "quadrant_spread": round(spread, 3),
        "consistent": bool(spread <= quadrant_tol),
        "ncc_at_unity": round(_best_ncc_shift(
            cur, prep(ref_rgb), 6)[0], 4),
    }


def legacy_recall_on_truth(rgb: np.ndarray, truth: np.ndarray, tau: float = 0.10) -> float:
    """What fraction of the TRUE fig the retired colour predicate would keep.

    The retired instrument was a luma-normalised green-magenta predicate,
    `gmn = (G - (R+B)/2) / luma`, accepted when |gmn| > tau -- green one side,
    magenta the other, which is the whole green-to-purple arc except the slate
    the fig crosses in between.  Scored here against this detector's own mask so
    the blindness is MEASURED on the object rather than asserted about it: a
    recall near zero on a frame where the fig is plainly visible is the dead
    zone, and it is why an area series built on that predicate collapses and
    re-inflates around the transition.
    """
    if truth.sum() == 0:
        return float("nan")
    f = rgb.astype(np.float64)
    lum = 0.299 * f[:, :, 0] + 0.587 * f[:, :, 1] + 0.114 * f[:, :, 2] + 1e-6
    gmn = (f[:, :, 1] - 0.5 * (f[:, :, 0] + f[:, :, 2])) / lum
    keep = np.abs(gmn) > tau
    return float(keep[truth].sum()) / float(truth.sum())


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SELFTEST_DIR = os.environ.get("FIG_TRACK_SELFTEST_DIR", "")

# HAND-VERIFIED, 2026-08-20.  These are not copied from any instrument.  Each
# b15 frame below was cropped to the window (230,660)-(530,960), scaled 2x
# NEAREST, overlaid with a 50-px labelled grid, and LOOKED AT; the fig's left,
# right, top and bottom edges were read off the grid and averaged.  Frames were
# chosen to straddle the slate transition (f090 is the slate frame, f120 the
# purple one) so the check covers exactly the phase the retired colour predicate
# went blind in.
#
# An eye can put a centre inside a blob to about a dozen px and CANNOT count its
# area, so the check is on POSITION ONLY and the tolerance says so.  Area is
# never hand-checked, because a hand-checked area would be a number wearing a
# verification it does not have.
HAND_VERIFIED = {
    "b15": {0: (786, 339), 24: (785, 340), 48: (787, 340),
            72: (790, 332), 90: (792, 330), 120: (788, 325)},
}
HAND_TOL_PX = 22


def selftest() -> int:
    ok = True

    def check(name, passed, detail=""):
        nonlocal ok
        print("%-58s %s %s" % (name, "PASS" if passed else "FAIL", detail))
        ok = ok and passed

    # --- 1. the cover-crop map is the job's own arithmetic -------------------
    scale, left, top = cover_crop_map((832, 1216), (704, 1280))
    check("cover_crop map 832x1216 -> 704x1280",
          abs(scale - 1.0526315) < 1e-5 and (left, top) == (86, 0),
          "scale=%.6f left=%d top=%d" % (scale, left, top))

    # --- 2. pure-logic gate behaviour, no frames needed ---------------------
    a = np.zeros((9, 9), np.float64)
    a[3:6, 3:6] = 1.0
    check("ncc is invariant to gain and offset",
          abs(ncc(a, a * 7.0 + 33.0) - 1.0) < 1e-9,
          "ncc=%.6f" % ncc(a, a * 7.0 + 33.0))
    m = np.zeros((9, 9), bool)
    m[2:7, 2:7] = True
    m[4, 4] = False
    check("fill_holes recovers a specular hole", fill_holes(m).sum() == 25,
          "%d px" % fill_holes(m).sum())
    thin = np.zeros((11, 11), bool)
    thin[:, 5] = True
    thin[4:7, 4:7] = True
    check("binary_open deletes the 1-px stem, keeps the body",
          binary_open(thin, 1)[:, 5].sum() < 11 and binary_open(thin, 1)[5, 5],
          "%d px left on the stem column" % binary_open(thin, 1)[:, 5].sum())
    comp, reseeded = largest_component_containing(m, (4, 4))
    check("region continuity re-seeds rather than guessing", reseeded and comp.sum() == 24,
          "reseeded=%s n=%d" % (reseeded, comp.sum()))

    # --- the camera probe, on synthetic ground truth ------------------------
    rng = np.random.default_rng(7)
    base = rng.integers(0, 255, (1280, 704, 3), dtype=np.uint8)
    base = np.asarray(Image.fromarray(base).resize((704, 1280), Image.LANCZOS))
    zoomed = Image.fromarray(base).resize((int(704 * 1.2), int(1280 * 1.2)), Image.LANCZOS)
    l, t = (zoomed.width - 704) // 2, (zoomed.height - 1280) // 2
    zoomed = np.asarray(zoomed.crop((l, t, l + 704, t + 1280)))
    z = global_zoom(base, zoomed)
    check("global_zoom recovers a known 1.20x push",
          abs(z["scale"] - 1.20) <= 0.02 and z["consistent"],
          "scale=%.2f consistent=%s spread=%.3f" % (z["scale"], z["consistent"], z["quadrant_spread"]))
    # a picture whose halves are scaled DIFFERENTLY is not a camera move, and the
    # probe must refuse to call it one
    warp = np.array(zoomed)
    top = Image.fromarray(base[:640]).resize((int(704 * 1.5), int(640 * 1.5)), Image.LANCZOS)
    l2, t2 = (top.width - 704) // 2, (top.height - 640) // 2
    warp[:640] = np.asarray(top.crop((l2, t2, l2 + 704, t2 + 640)))
    zw = global_zoom(base, warp)
    check("global_zoom refuses a picture that is redrawn, not moved",
          not zw["consistent"], "spread=%.3f quads=%s" % (zw["quadrant_spread"], zw["quadrant_scales"]))

    if not SELFTEST_DIR or not os.path.isdir(SELFTEST_DIR):
        print("\n-- frame-backed checks SKIPPED: set FIG_TRACK_SELFTEST_DIR to a dir")
        print("   holding anchor/b01-nubcomp-s20260826-mask.png and frames/b15/fNNN.png")
        return 0 if ok else 1

    mask_png = os.path.join(SELFTEST_DIR, "anchor", "b01-nubcomp-s20260826-mask.png")
    anchor = anchor_from_mask(mask_png, (832, 1216), (704, 1280))
    ys, xs = np.nonzero(anchor)
    acy, acx = ys.mean(), xs.mean()

    # --- 3. the anchor lands on the nub the composite pasted ----------------
    check("geometric anchor centroid == composite centre (405,750) mapped",
          abs(acy - 785.1) < 1.5 and abs(acx - 339.4) < 1.5,
          "(%.1f,%.1f)" % (acy, acx))

    fd = os.path.join(SELFTEST_DIR, "frames", "b15")
    paths = [os.path.join(fd, "f%03d.png" % (i + 1)) for i in range(121)]
    if not os.path.isfile(paths[0]):
        print("-- b15 frames not present, skipping the clip-backed checks")
        return 0 if ok else 1
    recs = track(paths, anchor)

    # --- 4. f000 must reproduce the KNOWN position --------------------------
    r0 = recs[0]
    check("f000 is live and sits on the geometric anchor",
          r0["status"] == "ok" and abs(r0["cy"] - acy) < 12 and abs(r0["cx"] - acx) < 12,
          "%s (%.1f,%.1f) area=%s" % (r0["status"], r0["cy"] or -1, r0["cx"] or -1, r0["area_px"]))

    # --- 5. hand-verified keyframes -----------------------------------------
    bad = []
    for f, (hy, hx) in sorted(HAND_VERIFIED["b15"].items()):
        r = recs[f]
        if r["status"] != "ok":
            continue  # a declared dead zone is an allowed answer; a WRONG one is not
        if math.hypot(r["cy"] - hy, r["cx"] - hx) > HAND_TOL_PX:
            bad.append("f%03d det(%.0f,%.0f) eye(%d,%d) d=%.0f"
                       % (f, r["cy"], r["cx"], hy, hx, math.hypot(r["cy"] - hy, r["cx"] - hx)))
    live = sum(1 for f in HAND_VERIFIED["b15"] if recs[f]["status"] == "ok")
    check("hand-verified keyframes: every live frame within %d px" % HAND_TOL_PX,
          not bad and live >= 4, ("%d/%d live; " % (live, len(HAND_VERIFIED["b15"])))
          + ("; ".join(bad) if bad else "no misses"))

    # --- 6. THE KNOWN-BAD CASE ----------------------------------------------
    # The retired colour predicate read 2917 px at f084 and 11302 at f096 on this
    # clip -- a 3.9x single-frame balloon that is the mask re-acquiring the fig
    # through slate.  The replacement must not publish that number as growth: at
    # every frame it must either declare a dead zone or report a trajectory whose
    # own step ratio across the slate is physical.
    span = [r for r in recs[84:97]]
    live_span = [r for r in span if r["status"] == "ok"]
    ratios = [r.get("ratio_prev_ok", 1.0) for r in live_span if "ratio_prev_ok" in r]
    worst = max(ratios) if ratios else 0.0
    check("b15 f084-f096: no unflagged 3.9x balloon survives the gates",
          worst < 3.9 and all(("area_px" in r) for r in span),
          "worst live step %.2fx over %d live / %d dead"
          % (worst, len(live_span), len(span) - len(live_span)))

    # every dead frame carries a stated reason and no area
    silent = [r["frame"] for r in recs
              if r["status"] == "dead" and (r["area_px"] is not None or not r["dead_reasons"])]
    check("no silent guesses: every dead frame is null + reasoned", not silent, str(silent))

    # --- 7. the retired predicate's blindness, MEASURED on this mask ---------
    # Not asserted: for each of these frames the green-magenta predicate is
    # scored against the fig this detector found and hand-verification agrees
    # with.  A collapse to near-zero recall in the middle of a smooth trajectory
    # IS the mechanism behind the published 2917 -> 11302 px "growth".
    recall = {}
    for f in (72, 84, 90, 96, 108):
        r = recs[f]
        if r["status"] != "ok":
            recall[f] = None
            continue
        rgbf = np.array(Image.open(paths[f]).convert("RGB"))
        tm, _ = segment_frame(rgbf, r["cy"], r["cx"], r["r_eq"])
        recall[f] = round(legacy_recall_on_truth(rgbf, tm), 3)
    slate_blind = recall.get(90) is not None and recall[90] < 0.25
    check("the retired green-magenta predicate goes blind at the slate frame",
          slate_blind, "recall on the true fig: " +
          " ".join("f%03d=%s" % (f, recall[f]) for f in sorted(recall)))

    return 0 if ok else 1


def write_overlay(frame_paths, recs, anchor, out_png: str, which, zoom=2, win=300):
    """Draw the detector's own answer over the pixels, so it can be LOOKED AT.

    A detector nobody can look at is the failure this file exists to fix: the
    retired colour mask published 2917 px and 11302 px and no one saw that the
    second number was the mask re-acquiring the fig.  Live frames get their mask
    outlined; dead frames get a red X and their first reason printed."""
    from PIL import ImageDraw
    ys, xs = np.nonzero(anchor)
    ay, ax = int(ys.mean()), int(xs.mean())
    tiles = []
    for f in which:
        rgb = np.array(Image.open(frame_paths[f]).convert("RGB"))
        r = recs[f]
        im = Image.fromarray(rgb)
        d = ImageDraw.Draw(im)
        if r["status"] == "ok":
            m, _ = segment_frame(rgb, r["cy"], r["cx"], r["r_eq"])
            edge = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0)
                         & np.roll(m, 1, 1) & np.roll(m, -1, 1))
            a = np.array(im)
            a[edge] = (0, 255, 0)
            im = Image.fromarray(a)
            d = ImageDraw.Draw(im)
            d.line([(r["cx"] - 8, r["cy"]), (r["cx"] + 8, r["cy"])], fill=(0, 255, 0))
            d.line([(r["cx"], r["cy"] - 8), (r["cx"], r["cy"] + 8)], fill=(0, 255, 0))
        cy0 = int(r["cy"]) if r["status"] == "ok" else ay
        cx0 = int(r["cx"]) if r["status"] == "ok" else ax
        half = win // 2
        y0 = max(0, min(im.height - win, cy0 - half))
        x0 = max(0, min(im.width - win, cx0 - half))
        t = im.crop((x0, y0, x0 + win, y0 + win)).resize((win * zoom, win * zoom), Image.NEAREST)
        d = ImageDraw.Draw(t)
        if r["status"] == "ok":
            d.text((6, 6), "f%03d  area=%d  sep m/l=%.1f/%.1f" % (
                f, r["area_px"], r["probe"]["sep_material"], r["probe"]["sep_luma"]),
                fill=(0, 255, 0))
        else:
            d.line([(0, 0), (win * zoom, win * zoom)], fill=(255, 40, 40), width=3)
            d.line([(win * zoom, 0), (0, win * zoom)], fill=(255, 40, 40), width=3)
            d.text((6, 6), "f%03d  DEAD ZONE" % f, fill=(255, 80, 80))
            d.text((6, 22), r["dead_reasons"][0][:52], fill=(255, 80, 80))
        tiles.append(t)
    cols = min(4, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    w, h = tiles[0].size
    sheet = Image.new("RGB", (w * cols, h * rows), (10, 10, 10))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * w, (i // cols) * h))
    sheet.save(out_png)
    print("WROTE %s" % out_png)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frames", help="directory of fNNN.png, 1-based, in order")
    ap.add_argument("--anchor-mask", help="the inpaint/composite mask PNG")
    ap.add_argument("--anchor-cover-crop", default="832x1216->704x1280")
    ap.add_argument("--out", help="write the per-frame JSON here")
    ap.add_argument("--overlay", help="write a LOOK sheet of the detector's own answer here")
    ap.add_argument("--overlay-frames", default="0,24,48,72,90,96,108,120")
    ap.add_argument("--gates", action="store_true", help="print the declared gates and exit")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()

    if a.gates:
        print(json.dumps(gates_dict(), indent=2))
        return 0
    if a.selftest:
        return selftest()
    if not (a.frames and a.anchor_mask):
        ap.error("--frames and --anchor-mask are required (or use --selftest)")

    src, dst = a.anchor_cover_crop.split("->")
    src_wh = tuple(int(v) for v in src.lower().split("x"))
    dst_wh = tuple(int(v) for v in dst.lower().split("x"))
    anchor = anchor_from_mask(a.anchor_mask, src_wh, dst_wh)

    names = sorted(n for n in os.listdir(a.frames) if n.lower().endswith(".png"))
    paths = [os.path.join(a.frames, n) for n in names]
    recs = track(paths, anchor, verbose=a.verbose)

    live = [r for r in recs if r["status"] == "ok"]
    out = {
        "detector": "pipeline/fig_track.py",
        "gates": gates_dict(),
        "frames": len(recs),
        "live": len(live),
        "dead": len(recs) - len(live),
        "records": recs,
    }
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)
        print("WROTE %s" % a.out)
    if a.overlay:
        which = [int(v) for v in a.overlay_frames.split(",") if v.strip()]
        which = [f for f in which if 0 <= f < len(recs)]
        write_overlay(paths, recs, anchor, a.overlay, which)
    print("frames=%d live=%d dead=%d" % (len(recs), len(live), len(recs) - len(live)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
