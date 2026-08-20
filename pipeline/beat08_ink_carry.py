#!/usr/bin/env python3
r"""Carry the plate's own cel ink over an inpainted fill. $0, CPU, no sampler.

THE DEFECT THIS IS AIMED AT, MEASURED. `ep2-b08-str70-0820` deleted beat 08's
guard fist and kept his harness strap running, but its fill is SOFT: ink density
(px with L<90 in the erase region) 10.5% against the plate's own 13.3%, and a
shard rate of 0.38% against the plate's 1.82% -- 4.8x smoother than the material
it replaced. It reads as an airbrushed patch in a flat-cel frame. Nothing about
that needs a GPU: the fill's SHAPES are right, its RENDERING is not.

WHAT THIS DOES, AND WHY EACH STEP INVENTS NOTHING.

  1. PALETTE FROM THE PLATE'S OWN REAL MATERIAL. k-means (deterministic:
     farthest-point init, fixed iteration count) over plate pixels in a ring
     12-70 px outside the mask, restricted to pixels that are byte-identical
     between plate and fill so nothing repainted can enter the palette. These
     are the cel colours the artist actually used around this hole.
  2. SNAP. Every pixel inside the mask goes to its nearest palette entry. This
     is what removes the airbrush: a cel frame has flat fields, and a soft
     gradient across three cel levels is exactly what the sampler added.
  3. RE-INK, ON A RULE READ OFF THE PLATE RATHER THAN CHOSEN. The first draft
     inked EVERY boundary between two palette labels at the plate's mean dark
     run width, and turned 65% of the hole black -- ink density 58.7% against
     the plate's 13.3%. That was a rule I picked, and it was wrong: a cel frame
     does NOT outline every colour step. Shirt against shirt-shadow carries no
     line; strap against shirt does. So the rule is now MEASURED: snap the
     plate's own ring to the same palette, and for each ORDERED PAIR of labels
     count what fraction of that pair's boundary pixels are dark in the plate.
     Inside the mask, a boundary is inked only if its own pair is inked in the
     plate more often than not. The line width is likewise the plate's own mean
     run length of THIN dark structures (runs of <= 6 px, so a shadow field
     cannot masquerade as a line). Speckle is removed by a majority filter
     before any of this, or snapping noise would invent boundaries to ink.
  4. OUTSIDE THE MASK, TAKE THE PLATE'S BYTES. This is the free win and it is
     the reason a compositor beats a re-render here. `--pad-crop 64` repaints a
     231x247 box around the mask: 8574 / 8598 / 8600 / 8572 px of drift across
     four renders, including damage to the protected fist copy (maxdiff 55 /
     121 / 78). A composite has no reason to inherit any of it. Only a
     `--feather` px band at the mask edge is blended, and the script REPORTS
     how many pixels outside the mask ended up differing from the plate.

WHAT THIS CANNOT DO, PRE-REGISTERED BEFORE IT IS RUN: it cannot remove a shape.
If the fill drew a band the plate does not have, snapping and re-inking will
make that band FLATTER AND CRISPER, not absent. On `ep2-b08-str70-0820` that
band is the open H1(b) failure, so this operation is expected to sharpen a
defect as well as a virtue, and the judge must look at it rather than read the
ink number and stop.

    python3 pipeline/beat08_ink_carry.py --selftest
    python3 pipeline/beat08_ink_carry.py --plate P.png --fill F.png \
        --mask M.png --out C.png [--colours 8] [--feather 2]
"""
from __future__ import annotations

import argparse
import sys

import numpy as np

RING_IN, RING_OUT = 12, 70     # where the palette is sampled from, px outside the mask
ITERS = 25                     # k-means sweeps; fixed, so the result is deterministic


def luma(a):
    a = np.asarray(a, float)
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def _dilate(m, r):
    """Square-structuring-element dilation by r, via cumulative sums."""
    if r <= 0:
        return m.copy()
    p = np.pad(m.astype(np.int32), r + 1)
    s = p.cumsum(0).cumsum(1)
    k = 2 * r + 1
    tot = (s[k:, k:] - s[:-k, k:] - s[k:, :-k] + s[:-k, :-k])
    return tot[:m.shape[0], :m.shape[1]] > 0


def ring_of(mask, lo=RING_IN, hi=RING_OUT):
    return _dilate(mask, hi) & ~_dilate(mask, lo)


def kmeans(px, k, iters=ITERS):
    """Deterministic k-means: farthest-point init, fixed sweeps, no RNG."""
    px = px.astype(float)
    c = [px[int(np.argmax(px.sum(axis=1)))]]         # brightest pixel, a fixed choice
    for _ in range(k - 1):
        d = np.min([((px - x) ** 2).sum(axis=1) for x in c], axis=0)
        c.append(px[int(np.argmax(d))])
    C = np.array(c)
    for _ in range(iters):
        lab = np.argmin(((px[:, None, :] - C[None, :, :]) ** 2).sum(axis=2), axis=1)
        for j in range(k):
            sel = lab == j
            if sel.any():
                C[j] = px[sel].mean(axis=0)
    return C


def ink_run_width(img, where, thin=6):
    """Mean horizontal run length of THIN dark (L<90) runs inside `where`.

    Runs longer than `thin` are shadow FIELDS, not lines, and including them is
    how the first draft arrived at a 3 px pen and inked 65% of the hole.
    """
    dark = (luma(img) < 90) & where
    runs = []
    for row in dark:
        n = 0
        for v in row:
            if v:
                n += 1
            elif n:
                runs.append(n)
                n = 0
        if n:
            runs.append(n)
    runs = [r for r in runs if r <= thin]
    return float(np.mean(runs)) if runs else 1.0


def _label_boundaries(lab):
    """Yield (mask_of_boundary_pixels, label_a, label_b) for 4 offsets."""
    for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
        h, w = lab.shape
        ys0, ys1 = max(0, -dy), h - max(0, dy)
        xs0, xs1 = max(0, -dx), w - max(0, dx)
        a = lab[ys0:ys1, xs0:xs1]
        b = lab[max(0, dy):h - max(0, -dy), max(0, dx):w - max(0, -dx)]
        yield (ys0, ys1, xs0, xs1), a, b


def _majority(lab, k, passes=2):
    """Remove snapping speckle: each pixel takes the commonest label in 3x3."""
    out = lab.copy()
    for _ in range(passes):
        counts = np.zeros((k,) + lab.shape, np.int16)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                sh = np.roll(np.roll(out, dy, 0), dx, 1)
                for j in range(k):
                    counts[j] += (sh == j)
        best = counts.argmax(axis=0)
        out = np.where(out >= 0, best, out)
    return out


def ink_levels(lab, ring, k, max_run=4, min_frac=0.001, min_px=20):
    """Which palette labels are LINES rather than materials, by run width.

    A line is thin; a field is not. Darkness cannot make this call on this
    plate -- the navy collar is darker than the strap outline that draws it.
    """
    out = set()
    floor = max(min_px, int(min_frac * ring.sum()))
    for j in range(k):
        sel = (lab == j) & ring
        if sel.sum() < floor:
            continue
        runs = []
        for row in sel:
            n = 0
            for v in row:
                if v:
                    n += 1
                elif n:
                    runs.append(n); n = 0
            if n:
                runs.append(n)
        if runs and float(np.mean(runs)) <= max_run:
            out.add(j)
    return out


def ink_pairs(plate, ring, lab, ink_labs, thresh=0.5):
    """Which pairs of materials the PLATE puts a line between.

    TWO WRONG FORMULATIONS CAME FIRST AND BOTH ARE WHY THIS DOCSTRING IS LONG.
    (1) "ink every label boundary" turned 65% of the hole black -- a cel frame
    does not outline every colour step. (2) "ink a pair if its boundary pixels
    are dark" found NOTHING, because ink here is thick enough to earn its own
    palette entry: where the plate draws a line, the two materials are never
    adjacent at all -- the line is BETWEEN them. Asking about the boundary
    between them asks about a boundary that does not exist.

    So the question is asked the right way round. For every ink pixel in the
    ring, look at which MATERIALS flank it: the two commonest are a pair the
    artist SEPARATES with a line. For every direct adjacency between two
    materials, that pair is one the artist runs together with no line. A pair is
    inked if it is separated more often than it is run together, and its line
    COLOUR is the mean of the ink pixels that actually separate it.

    (3) WHICH LABELS ARE INK IS DECIDED BY THINNESS, NOT DARKNESS, and that was
    the third correction. This plate has TWO ink levels -- near-black (40,18,17)
    for the buckle and dark brown (72,40,32) for the strap outline -- and one
    genuinely dark MATERIAL, the navy collar (56,44,81) at luma 54. A luma cut
    calls the collar ink and the strap outline a material, which is exactly
    backwards; a run-width cut gets all three right, because a line is thin and
    a collar is not.
    """
    dark = np.isin(lab, list(ink_labs)) & ring
    is_mat = lambda v: (v >= 0) & ~np.isin(v, list(ink_labs))

    sep, adj, col = {}, {}, {}
    # separated-by-a-line: the materials flanking each dark pixel
    ys, xs = np.nonzero(dark)
    h, w = lab.shape
    for y, x in zip(ys, xs):
        y0, y1 = max(0, y - 2), min(h, y + 3)
        x0, x1 = max(0, x - 2), min(w, x + 3)
        near = lab[y0:y1, x0:x1]
        u, n = np.unique(near[is_mat(near)], return_counts=True)
        # THE TWO COMMONEST, not "exactly two". An 8-colour palette gives the
        # anti-aliased pixels either side of a line their own labels, so a
        # strap/shirt line has four labels around it and an exactly-two rule
        # found ONE pair in the whole frame and re-inked nothing.
        if len(u) >= 2:
            order = np.argsort(-n)
            if n[order][1] >= 3:
                top = u[order][:2]
                k = (int(min(top)), int(max(top)))
                sep[k] = sep.get(k, 0) + 1
                col.setdefault(k, []).append(plate[y, x])
    # run together with no line: direct adjacency between two materials
    for (y0, y1, x0, x1), a, b in _label_boundaries(lab):
        d = (a != b) & is_mat(a) & is_mat(b)
        if not d.any():
            continue
        for i, j in zip(a[d], b[d]):
            k = (min(int(i), int(j)), max(int(i), int(j)))
            adj[k] = adj.get(k, 0) + 1

    out = {}
    for k in set(sep) | set(adj):
        s_, a_ = sep.get(k, 0), adj.get(k, 0)
        if s_ + a_ >= 20 and s_ / (s_ + a_) >= thresh:
            # THE DARKEST THIRD, not the mean. The thin-structure test correctly
            # calls the anti-aliased fringe beside a line "ink", so averaging
            # every separating pixel returns a washed-out (191,159,127) for a
            # line whose core is (72,40,32) -- a re-ink that lays down a pale
            # smear and moves the ink measure not at all.
            cs = np.array(col[k], float)
            keep = cs[np.argsort(luma(cs))[:max(1, len(cs) // 3)]]
            rgb = keep.mean(axis=0).round().astype(int)
            out[k] = (round(s_ / (s_ + a_), 3), tuple(int(v) for v in rgb))
    return out


def carry(plate, fill, mask, colours=8, feather=2, ring_px=(RING_IN, RING_OUT),
          restore_only=False):
    """Return (composite, report). Every array HxWx3 uint8 / HxW bool.

    `restore_only` skips the palette entirely and does step 4 alone: the fill's
    own pixels inside the mask, the PLATE's bytes outside it. That half of this
    script is the half that survived judging -- see b08-arm-route-0819.md 27.
    """
    plate = np.asarray(plate); fill = np.asarray(fill)
    mask = np.asarray(mask, bool)
    same = (plate == fill).all(axis=2)
    ring = ring_of(mask, *ring_px) & same
    if ring.sum() < 500:
        raise ValueError("only %d untouched plate px in the palette ring -- "
                         "refusing to build a palette out of repainted pixels"
                         % ring.sum())

    if restore_only:
        out = plate.copy()
        out[mask] = fill[mask]
        band = _dilate(mask, feather) & ~mask
        if feather > 0 and band.any():
            out[band] = ((plate[band].astype(int) + fill[band].astype(int)) // 2
                         ).astype(np.uint8)
        dof = (np.abs(out.astype(int) - plate.astype(int)).max(axis=2) > 0) & ~mask
        return out, {"mode": "restore_only", "snapped_px": 0, "re_inked_px": 0,
                     "feather_px": feather,
                     "out_of_mask_diff_px": int(dof.sum()),
                     "out_of_mask_beyond_feather_px":
                         int((dof & ~_dilate(mask, feather)).sum())}

    C = kmeans(plate[ring], colours)
    rlab = np.full(mask.shape, -1, int)
    rpx = plate[ring].astype(float)
    rlab[ring] = np.argmin(((rpx[:, None, :] - C[None, :, :]) ** 2).sum(axis=2), axis=1)
    ink_labs = ink_levels(rlab, ring, len(C))
    inked_pairs = ink_pairs(plate, ring, rlab, ink_labs)
    w = max(1, min(3, int(round(ink_run_width(plate, ring)))))

    sub = fill[mask].astype(float)
    lab_flat = np.argmin(((sub[:, None, :] - C[None, :, :]) ** 2).sum(axis=2), axis=1)
    lab = np.full(mask.shape, -1, int)
    lab[mask] = lab_flat
    lab = np.where(mask, _majority(np.where(mask, lab, 0), len(C)), -1)
    snapped = fill.copy()
    snapped[mask] = C[lab[mask]].round().astype(np.uint8)

    # Re-ink ONLY the material pairs the plate itself draws a line between, and
    # draw each one in the colour the plate uses for THAT line -- near-black
    # between collar and shirt, dark brown along the strap.
    edge = np.zeros(mask.shape, bool)
    for (i, j), (_ratio, rgb) in sorted(inked_pairs.items()):
        pair_edge = np.zeros(mask.shape, bool)
        for (y0, y1, x0, x1), a, b in _label_boundaries(lab):
            lo = np.minimum(a, b); hi = np.maximum(a, b)
            d = (a != b) & (a >= 0) & (b >= 0) & (lo == i) & (hi == j)
            if d.any():
                pair_edge[y0:y1, x0:x1] |= d
        pair_edge = _dilate(pair_edge, w - 1) & mask
        snapped[pair_edge] = np.array(rgb, np.uint8)
        edge |= pair_edge

    # Outside the mask the PLATE's bytes win; only `feather` px are blended.
    out = plate.copy()
    band = _dilate(mask, feather) & ~mask
    out[mask] = snapped[mask]
    if feather > 0 and band.any():
        out[band] = ((plate[band].astype(int) + snapped[band].astype(int)) // 2
                     ).astype(np.uint8)

    diff_out = (np.abs(out.astype(int) - plate.astype(int)).max(axis=2) > 0) & ~mask
    return out, {
        "palette": [tuple(int(v) for v in c) for c in C.round()],
        "ink_levels": sorted(int(v) for v in ink_labs),
        "ink_width_px": w,
        "palette_ring_px": int(ring.sum()),
        "snapped_px": int(mask.sum()),
        "re_inked_px": int(edge.sum()),
        "inked_pairs_rule": {str(k): v for k, v in sorted(inked_pairs.items())},
        "out_of_mask_diff_px": int(diff_out.sum()),
        "feather_px": feather,
    }


def selftest() -> int:
    """Asserts, not prints."""
    h = w = 60
    plate = np.zeros((h, w, 3), np.uint8)
    plate[:, :] = (240, 235, 220)                # cream field
    plate[:, 20:30] = (150, 110, 70)             # a strap band
    plate[:, 19:20] = plate[:, 30:31] = (40, 30, 25)   # its ink edges
    mask = np.zeros((h, w), bool)
    mask[20:40, 15:45] = True

    # a SOFT fill: the same shapes, blurred, so snapping must recover flat cel
    fill = plate.astype(float).copy()
    for _ in range(6):
        fill[1:-1] = (fill[:-2] + fill[1:-1] + fill[2:]) / 3
        fill[:, 1:-1] = (fill[:, :-2] + fill[:, 1:-1] + fill[:, 2:]) / 3
    fill = fill.round().astype(np.uint8)
    fill[~mask] = plate[~mask]                   # only the hole was repainted

    out, rep = carry(plate, fill, mask, colours=4, feather=0, ring_px=(2, 12))
    assert out.shape == plate.shape
    # 1. the composite is byte-exact outside the mask at feather 0
    assert rep["out_of_mask_diff_px"] == 0, rep
    assert (out[~mask] == plate[~mask]).all()
    # 2. inside the mask every pixel is a palette colour or the ink colour
    pal = ({tuple(c) for c in rep["palette"]}
           | {tuple(v[1]) for v in rep["inked_pairs_rule"].values()})
    got = {tuple(int(v) for v in p) for p in out[mask]}
    assert got <= pal, sorted(got - pal)[:4]
    # 3. it actually re-inks: the soft fill lost its dark edge, the composite has one
    dk = lambda a: int(((luma(a) < 90) & mask).sum())
    assert dk(fill) < dk(out), (dk(fill), dk(out))
    assert rep["re_inked_px"] > 0
    # 4. the palette refuses to be built from repainted pixels
    try:
        carry(plate, fill, np.ones((h, w), bool), ring_px=(2, 12))
        raise AssertionError("no refusal when the whole frame is the mask")
    except ValueError as e:
        assert "palette ring" in str(e)
    # 5. determinism -- same inputs, byte-identical output
    out2, _ = carry(plate, fill, mask, colours=4, feather=0, ring_px=(2, 12))
    assert (out == out2).all()
    print("✓ beat08_ink_carry selftest passed (9 assertions)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--plate"); ap.add_argument("--fill")
    ap.add_argument("--mask"); ap.add_argument("--out")
    ap.add_argument("--colours", type=int, default=8)
    ap.add_argument("--ring-in", type=int, default=RING_IN)
    ap.add_argument("--ring-out", type=int, default=RING_OUT)
    ap.add_argument("--restore-only", action="store_true",
                    help="plate bytes outside the mask, fill inside, no palette")
    ap.add_argument("--feather", type=int, default=2)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.plate and a.fill and a.mask and a.out):
        ap.error("--selftest, or --plate --fill --mask --out")
    from PIL import Image
    plate = np.asarray(Image.open(a.plate).convert("RGB"))
    fill = np.asarray(Image.open(a.fill).convert("RGB"))
    mask = np.asarray(Image.open(a.mask).convert("L")) > 127
    if not (plate.shape == fill.shape and mask.shape == plate.shape[:2]):
        ap.error("plate, fill and mask must be the same size")
    out, rep = carry(plate, fill, mask, a.colours, a.feather,
                     ring_px=(a.ring_in, a.ring_out),
                     restore_only=a.restore_only)
    Image.fromarray(out).save(a.out)
    for k in sorted(rep):
        print("  %-22s %s" % (k, rep[k]))
    print("WROTE %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
