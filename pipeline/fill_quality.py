#!/usr/bin/env python3
"""C4' -- the fill-quality instrument that replaces the mean-|gradient| bar.

WHY THIS FILE EXISTS
====================
`b08-arm-route-0819.md` §21 retired C4 on the beat 08 vacancy. C4 asked ONE
question of a composite's vacancy fill -- *is this flat?* -- as

    mean |gradient| inside the fill  >=  0.45 x mean |gradient| in a ring of
                                          real pixels around it

and the `ep2-b08-gripcomp-0820` fill, which at 5x is a ribbed corduroy comb
running down the harness strap, scored **89%: twice the bar.** A ladder of
streaks is not flat. The obvious patch -- |gy|/|gx| -- read 0.64 in the fill
and 0.64 in the untouched ring, because the streaks run along the material's
own dominant axis, which is the axis the fill was built to continue along.

The failure is not that the bar was too low. It is that a fill can be wrong in
TWO directions and C4 only had one of them:

  * TOO FLAT -- a smear. C4 sees this and always did. It is also the
    RECOVERABLE failure: a low-strength sampler pass ADDS texture, so beat 03
    shipped a deliberately smooth per-row ramp and argued that the 0.30 pass
    would put blade texture back. It did.
  * FABRICATED -- structure the surrounding material does not have. C4 scores
    this WELL, because fabricated structure is still structure. It is also the
    UNRECOVERABLE failure, and for exactly the reason 0.30 was chosen: a
    low-strength pass PRESERVES structure. Hand the sampler a comb and it
    keeps the comb.

C4' is C4 plus the two statistics that see the second direction. All three are
computed against the same real ring, so a genuinely detailed or genuinely
directional material raises its own bar and is not punished for it.

WHAT IT MEASURES
================
Everything is the mean absolute FIRST DIFFERENCE along each of 8 directions

    (0,1) (1,2) (1,1) (2,1) (1,0) (2,-1) (1,-1) (1,-2)      as (dy, dx)

taken on the luma plane, divided by the step length so the diagonals are
comparable, and averaged over the pixel pairs that lie wholly inside the
region. `f[d]` is that number in the fill, `r[d]` in the ring.

  D  DETAIL       mean|grad| in fill / mean|grad| in ring, isotropic.
                  Unchanged from C4 -- SAME formula, so its numbers stay
                  comparable to everything already published. Bar >= 0.45.
                  Catches the smear. Passed the corduroy at 0.89; that is not
                  a bug in D, it is D answering the question it was asked.

  N  NULL AXIS    min over d of f[d]/r[d]. "Is there a direction along which
                  the fill is dead while the material around it is alive?"
                  A copy-fill, a continuation and a directional blur all have
                  one; real material does not. Bar >= 0.25.
                  THIS IS THE ONE THAT CATCHES THE CORDUROY: 0.096, because
                  along (2,1) -- the strap's own axis -- the fill varies by
                  1.08 grey levels where the ring varies by 11.22.

  F  FABRICATION  aniso(f)/aniso(r), where aniso = max(x)/min(x) over d.
                  "Is the fill more directional than its own material is?"
                  Normalised by the ring, so a strap that really is streaky
                  passes and a fill that out-streaks the strap does not.
                  Bar <= 2.60. Corduroy 7.87. Every honest fill measured
                  0.47 - 1.17, and the 99th percentile of 200 real windows
                  is 2.57 -- the bar is in the measured gap, not on a round
                  number.

N and F are related but neither implies the other, and the two failures in
this beat's own history prove it: the corduroy has a null axis AND excess
anisotropy; the isotropic-diffusion fill that replaced it in source has
NEITHER (F = 0.89, it is dead isotropically) and is caught by D at 0.18.
Three bars, three distinct failure shapes, no redundancy.

The ring baseline is the MEDIAN over 8 angular sectors, not the mean -- see
`ring_baseline`, which carries the measurement that decided it.

VERDICT = D >= 0.45  AND  N >= 0.25  AND  F <= 2.60.

MEASURED, ON THE CORPUS THIS FILE SELFTESTS (ring 3-12 px, real pixels only):

  case                                        D      N      F    verdict
  ep2-b08-gripcomp-0820 fill, ON DISK       0.888  0.084  7.87   FAIL <- eye agrees
  the same vacancy, isotropic diffusion     0.182  0.121  0.89   FAIL <- eye agrees
  the same footprint, REAL plate pixels     0.815  0.562  0.81   PASS <- control
  real strap 110 px up                      0.991  0.881  0.77   PASS
  real strap, higher                        1.447  1.024  0.56   PASS
  real cream shirt, left                    1.236  0.691  1.78   PASS
  real wrap skirt                           0.970  0.971  1.13   PASS
  real shoulder + gold clasp                2.156  2.082  0.42   PASS
  real board / cuff                         1.486  1.545  0.70   PASS
  b03 sapcomp, the 44k-px cover vacancy     0.810  0.553  1.08   PASS
  b03 sapcomp, the 6.8k-px second vacancy   0.556  0.311  1.17   PASS <- tightest
  b13 sapcomp                               1.843  1.329  0.87   PASS
  b15 sapcomp, the listener vacancy         4.713  2.841  0.47   PASS
  b19 sapcomp, whip vacancy 1               1.047  0.888  0.88   PASS
  b19 sapcomp, whip vacancy 2               0.925  0.759  0.67   PASS

AND THE NUMBER THAT MATTERS MORE THAN ANY THRESHOLD -- THE FALSE POSITIVE
RATE. The bars are also run against 200 windows of beat 08's exact footprint
moved at random to places on the plate where it lands wholly on untouched
pixels. These are REAL material and every one of them should pass:

  false FAIL on D 2.0%   on N 1.0%   on F 1.0%   ON ANY OF THE THREE 3.0%

and the corduroy fill sits at percentile 0.0 of that null on N and 100.0 on
F -- more extreme than all 200 real windows, on both new statistics, at once.
The selftest FAILS if that rate ever climbs above 5%, so a future tightening
of a bar cannot be bought silently with real work condemned.

The tightest honest case is b03's second vacancy at N = 0.311 against a 0.25
bar; the corduroy is at 0.084. The bar sits in a 3.7x gap.

WHAT THE OUTSIDE LITERATURE SAYS, BEFORE ANY OF THIS WAS BUILT
==============================================================
The diagnosis it supplies is sharper than "the bar was too low": mean
|gradient| and |gy|/|gx| are both MARGINAL (first-order histogram)
statistics. They summarise the distribution of gradient values and throw away
where the values sit relative to each other, so a comb and real fabric can
have identical gradient histograms AND identical anisotropy. That is not a
tuning failure, it is the defining blind spot of the statistic class, and no
fifth marginal statistic fixes it. D, N and F are all still per-direction
means -- what makes N and F see the comb is that they are read ACROSS
directions and against the same material's own directional profile, which is
a second-order (arrangement) read.

Three imports, named so the choices are traceable:

  * The a-contrario / empirical-null wrapper (Desolneux-Moisan-Morel line;
    review arXiv:1808.02564) -- do not trust a constant, build the null from
    the image's own real material and read the percentile. That is
    `empirical_null` below, and it is what produced the false-positive rate.
  * Textile defect inspection (Chan & Pang, IEEE TIA, Fourier analysis of
    fabric) -- "periodic = bad" is wrong; "the fill's periodicity is unlike
    the neighbourhood's" is right. Everything here is a RATIO to the ring for
    that reason.
  * GMSD (Xue et al., TIP 2014) -- its whole contribution is that std-pooling
    beats mean-pooling. N is that lesson applied one level up: C4 took the
    MEAN over directions of what N takes the MINIMUM of. GMSD itself is
    full-reference and cannot be run here.

Deliberately NOT built, with the reason: GLCM/Haralick (the one view that
would catch a comb is the autocorrelation with quantisation damage added);
Portilla-Simoncelli texture statistics (metamerism is the model's own point,
so "stats match" is weak evidence -- the wrong shape for a gate, and 250
lines); LBP histograms (contrast-invariant by construction, so blind to
amplitude, and it reads dither on a flat fill as texture); HOG orientation
chi-square (the literature predicts and §21 already measured that it matches
on this artifact, because the streaks run along the material's own grain);
and any absolute BRISQUE/NIQE score, whose natural-scene priors were fit on
photographs and do not hold on cel-shaded anime. A fourth and fifth component
would also cost family-wise false positives against a 3.0% budget already
spent.

TWO CHEAPER IDEAS WERE TRIED FIRST AND ARE VOID HERE. MEASURED, SO NOBODY
RE-TRIES THEM:

  * PATCH COHERENCE (Simakov et al., bidirectional similarity: for every 7x7
    patch of the fill, the SSD to its best match among the real patches
    around it). The literature's default instrument for exactly this, and on
    this vacancy it is BACKWARDS -- corduroy 17.86 RMS, the real plate pixels
    in the same footprint 15.07, and a real patch of the same strap 90 px
    higher 17.03, i.e. worse than the artifact. A garment junction is unique
    in its own neighbourhood, so "no real patch nearby looks like this" is
    true of the real thing too.
  * WHOLE-PATCH SPECTRAL PEAK and AUTOCORRELATION PEAK (find the periodic
    ripple as a spike in the 2-D power spectrum). Corduroy peak-share 0.056,
    real pixels in the same footprint 0.048, real strap 170 px higher 0.107.
    The rib period is close to the fabric's own fold period and the patch is
    too small for the spike to be narrow.

DEAD ZONES -- what C4' does NOT see
===================================
 1. COLOUR. Every statistic is on luma. A fill with the right texture in the
    wrong hue passes. Pair it with the material/luma probes the beat leaves
    already publish.
 2. SEMANTICS. Right texture, wrong place. A fill that continues the strap
    straight through where the gold clasp belongs has no null axis and no
    excess anisotropy and passes clean. C4' judges MATERIAL, never MEANING.
 3. THE SPRITE'S RIM. §21's other named defect -- the stair-stepped octagonal
    edge on the moved fist, "a sticker of a hand" -- lives on the composited
    object's boundary, not inside the vacancy. Out of scope by construction.
 4. DITHERED FABRICATION. Add isotropic noise on top of a comb and F and N
    both fall. The cost of that attack is that the noise must be about as
    large as the ring's own detail in the null direction, which is most of
    the way to just giving the fill real texture -- but it is a hole and it
    is stated, not denied.
 5. SMALL REGIONS. Below `MIN_REGION` px, or a ring with fewer than
    `MIN_RING` real pixels, or any direction with fewer than `MIN_PAIRS`
    pixel pairs, the per-direction means are noise and the ratios swing. The
    instrument REFUSES (verdict "VOID") rather than guessing. It has never
    been calibrated below ~4000 px; beat 08's vacancy is the smallest case in
    the corpus.
 6. REGIONS THAT STRADDLE A MATERIAL BOUNDARY inflate aniso in the fill and
    in the ring together, so F mostly cancels -- "mostly" is the observed
    1.17 on b03's second vacancy, not a proof. The sector median handles the
    ring side of this; nothing handles the fill side.
 7. THE RESIDUAL 3% IS REAL. Three of 200 windows of genuine plate material
    are condemned by these bars, the worst at D 0.104 -- a flat interior
    whose whole ring lands on cel outline. A FAIL on a small, flat, outlined
    region is worth a look before it is worth a re-render.
 8. It says nothing about whether the vacancy should EXIST. §21's actual
    ruling on beat 08 was that the hole is not fillable at all; C4' scoring a
    fill 0.9/0.9/0.9 would not overturn that.
 9. IT JUDGES VACANCY FILLS, NOT SPRITES. A composited drawn object is
    SUPPOSED not to match the material around it. `--selftest` and the CLI
    both skip components the composite made INKIER (new ink) and score only
    the ones it quieted (removal). Point it at a sprite and it will report
    nonsense with a straight face.

USAGE
    python3 pipeline/fill_quality.py --selftest
    python3 pipeline/fill_quality.py --plate P.png --image I.png [--region M.png]
    from fill_quality import assess          # assess(img, region, real_ok)
"""
from __future__ import annotations

import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FO = os.path.join(REPO, "farm-out")

# (dy, dx). Eight directions on a 2-px stencil: the four 45-degree ones plus
# the four 26.6-degree ones, which is what it takes to have a sample near the
# strap's own axis (0.503, 0.863) ~ (2, 1) without steering the stencil at the
# thing being judged.
DIRS = ((0, 1), (1, 2), (1, 1), (2, 1), (1, 0), (2, -1), (1, -1), (1, -2))

BAR_D = 0.45     # detail, C4's own bar, unchanged
BAR_N = 0.25     # null-axis floor
BAR_F = 2.60     # fabrication ceiling
RING = (3, 12)   # annulus, px, outside the region -- §21's honest re-base
MIN_REGION = 400
MIN_RING = 200
MIN_PAIRS = 40
SECTORS = 8      # the ring baseline is the MEDIAN over this many angular
                 # sectors, not the mean -- see `ring_baseline`
MIN_SECTOR = 120


def luma(a):
    import numpy as np
    a = np.asarray(a)
    return a.astype(np.float64).mean(axis=2) if a.ndim == 3 else a.astype(np.float64)


def dir_detail(L, m):
    """Mean |first difference| per direction, step-normalised. NaN if too few."""
    import numpy as np
    h, w = m.shape
    out = np.full(len(DIRS), np.nan)
    for i, (dy, dx) in enumerate(DIRS):
        sh = np.roll(np.roll(L, -dy, 0), -dx, 1)
        shm = np.roll(np.roll(m, -dy, 0), -dx, 1)
        valid = np.zeros(m.shape, bool)
        valid[max(0, -dy):h - max(0, dy), max(0, -dx):w - max(0, dx)] = True
        mm = m & shm & valid
        if int(mm.sum()) >= MIN_PAIRS:
            out[i] = float(np.abs(sh - L)[mm].mean() / np.hypot(dy, dx))
    return out


def iso_detail(L, m):
    """C4's own statistic, byte for byte: mean |np.gradient| over the mask."""
    import numpy as np
    gy, gx = np.gradient(L)
    return float(np.hypot(gx, gy)[m].mean())


def ring_mask(m, lo=RING[0], hi=RING[1]):
    """The annulus lo..hi px outside `m`, as a true Minkowski disc."""
    import numpy as np
    from PIL import Image, ImageFilter

    def grow(r):
        im = Image.fromarray((m * 255).astype("uint8"))
        while r > 0:
            k = min(r, 10)
            im = im.filter(ImageFilter.MaxFilter(2 * k + 1))
            r -= k
        return np.asarray(im) > 0
    return grow(hi) & ~grow(lo)


def ring_baseline(L, region, R):
    """The ring's detail, as the MEDIAN over 8 angular sectors, not the mean.

    WHY THE MEDIAN. The largest published dead zone of a ring baseline is that
    the annulus is often not ONE material -- beat 08's vacancy sits in a
    harness / cuff / shirt / clasp junction, and any ring around anything on a
    cel-shaded figure is liable to have a hard black outline running through
    one side of it. A mean baseline lets that one sector set the bar for all
    of them, the ratio collapses, and REAL MATERIAL gets condemned.

    Measured on 200 real windows of beat 08's own footprint moved at random
    over the plate, the fixed bars false-FAIL:

        mean ring baseline           D 9.5%   N 5.5%   F 3.0%   any 12.5%
        sector-median ring baseline  D 2.0%   N 1.0%   F 4.5%   any  6.5%

    -- and the F rise is a bar-placement artifact, fixed by putting BAR_F in
    the measured gap (null p99 2.57, honest corpus max 1.10, corduroy 7.87)
    instead of at a round 2.0. Falls back to the mean when fewer than half the
    sectors carry enough pixels to measure.
    """
    import numpy as np
    ys, xs = np.nonzero(region)
    cy, cx = ys.mean(), xs.mean()
    Y, X = np.nonzero(R)
    ang = (np.arctan2(Y - cy, X - cx) + np.pi) / (2.0 * np.pi)
    s = np.minimum((ang * SECTORS).astype(int), SECTORS - 1)
    ds, iso = [], []
    for k in range(SECTORS):
        m = np.zeros(R.shape, bool)
        m[Y[s == k], X[s == k]] = True
        if int(m.sum()) < MIN_SECTOR:
            continue
        d = dir_detail(L, m)
        if np.isnan(d).any():
            continue
        ds.append(d)
        iso.append(iso_detail(L, m))
    if len(ds) < SECTORS // 2:
        return dir_detail(L, R), iso_detail(L, R), len(ds)
    return np.median(np.array(ds), axis=0), float(np.median(iso)), len(ds)


def assess(image, region, real_ok=None, ring=RING, label=""):
    """Score one synthesized region against the real material around it.

    image    HxWx3 uint8 (or HxW)  -- the composite AFTER the fill
    region   HxW bool              -- the synthesized pixels
    real_ok  HxW bool              -- pixels known to be untouched plate;
                                      defaults to everything outside `region`
    Returns a dict; `verdict` is PASS / FAIL / VOID.
    """
    import numpy as np
    region = np.asarray(region, bool)
    real_ok = ~region if real_ok is None else np.asarray(real_ok, bool)
    image = np.asarray(image)

    res = {"label": label, "region_px": int(region.sum()),
           "ring": tuple(ring), "ring_px": 0,
           "bars": {"D": BAR_D, "N": BAR_N, "F": BAR_F}}
    if region.sum() < MIN_REGION:
        res.update(verdict="VOID", ring_px=0,
                   why="region %d px, need %d" % (region.sum(), MIN_REGION))
        return res

    # Crop to the region plus the ring. Every statistic here is local, so this
    # is exact and it is what makes a 200-window null tractable.
    ys, xs = np.nonzero(region)
    pad = ring[1] + 2
    y0 = max(0, ys.min() - pad); y1 = min(region.shape[0], ys.max() + 1 + pad)
    x0 = max(0, xs.min() - pad); x1 = min(region.shape[1], xs.max() + 1 + pad)
    sl = (slice(y0, y1), slice(x0, x1))
    region = region[sl]
    real_ok = real_ok[sl]
    image = image[sl]

    L = luma(image)
    R = ring_mask(region, *ring) & real_ok
    res["ring_px"] = int(R.sum())

    if R.sum() < MIN_RING:
        res.update(verdict="VOID",
                   why="ring %d real px, need %d" % (R.sum(), MIN_RING))
        return res

    f = dir_detail(L, region)
    r, r_iso, nsec = ring_baseline(L, region, R)
    res["ring_sectors"] = nsec
    ok = ~(np.isnan(f) | np.isnan(r))
    if ok.sum() < len(DIRS):
        res.update(verdict="VOID",
                   why="only %d of %d directions had %d+ pixel pairs in both "
                       "the region and the ring" % (ok.sum(), len(DIRS), MIN_PAIRS))
        return res

    ratios = f / np.maximum(r, 1e-9)
    D = iso_detail(L, region) / max(r_iso, 1e-9)
    N = float(ratios.min())
    aniso_f = float(f.max() / max(f.min(), 1e-9))
    aniso_r = float(r.max() / max(r.min(), 1e-9))
    F = aniso_f / max(aniso_r, 1e-9)

    fails = []
    if D < BAR_D:
        fails.append("D %.3f < %.2f (the fill is a SMEAR)" % (D, BAR_D))
    if N < BAR_N:
        fails.append("N %.3f < %.2f (dead along %s, where the material is not)"
                     % (N, BAR_N, DIRS[int(np.argmin(ratios))]))
    if F > BAR_F:
        fails.append("F %.2f > %.2f (the fill is %.1fx more directional than "
                     "its own material)" % (F, BAR_F, aniso_f / max(aniso_r, 1e-9)))

    res.update(verdict="FAIL" if fails else "PASS", fails=fails,
               D=round(D, 4), N=round(N, 4), F=round(F, 4),
               aniso_fill=round(aniso_f, 4), aniso_ring=round(aniso_r, 4),
               dirs=[tuple(d) for d in DIRS],
               fill_detail=[round(v, 3) for v in f],
               ring_detail=[round(v, 3) for v in r],
               ratios=[round(v, 3) for v in ratios])
    return res


def line(res):
    if res["verdict"] == "VOID":
        return "%-44s VOID   %s" % (res["label"], res["why"])
    return ("%-44s %-4s  D %5.3f  N %5.3f  F %5.2f   %d px / ring %d"
            % (res["label"], res["verdict"], res["D"], res["N"], res["F"],
               res["region_px"], res["ring_px"]))


def empirical_null(image, region, real_ok=None, n=200, seed=20260820,
                   ring=RING):
    """The a-contrario check: score the SAME footprint on REAL pixels, n times.

    The literature's standing advice for a test like this one is not to trust
    a constant: build the null from the image's own real material by moving
    the region's exact shape to positions where it lands wholly on untouched
    pixels, and read the fill's percentile against that. Doing so also buys
    the number that matters more than any threshold -- the FALSE POSITIVE
    RATE, i.e. how often these three bars condemn material that is real.
    """
    import numpy as np
    region = np.asarray(region, bool)
    real_ok = np.ones(region.shape, bool) if real_ok is None else \
        np.asarray(real_ok, bool)
    h, w = region.shape
    ys, xs = np.nonzero(region)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    rng = np.random.RandomState(seed)
    pad = ring[1] + 2
    out = []
    tries = 0
    while len(out) < n and tries < n * 60:
        tries += 1
        oy = rng.randint(pad - y0, h - pad - y1)
        ox = rng.randint(pad - x0, w - pad - x1)
        m = np.zeros((h, w), bool)
        m[ys + oy, xs + ox] = True
        if not real_ok[m].all():
            continue
        r = assess(image, m, real_ok, ring=ring, label="null@%+d%+d" % (ox, oy))
        if r["verdict"] != "VOID":
            out.append(r)
    return out


def null_report(nulls, res=None, prefix="  "):
    import numpy as np
    if not nulls:
        print(prefix + "no valid null windows")
        return {}
    D = np.array([x["D"] for x in nulls])
    N = np.array([x["N"] for x in nulls])
    F = np.array([x["F"] for x in nulls])
    fp = np.array([x["verdict"] == "FAIL" for x in nulls])
    fpd = (D < BAR_D).mean(); fpn = (N < BAR_N).mean(); fpf = (F > BAR_F).mean()
    print(prefix + "empirical null, %d real windows of the same footprint:"
          % len(nulls))
    print(prefix + "  D  p01 %5.3f  p05 %5.3f  median %5.3f      "
          "false FAIL on D: %4.1f%%" % (np.percentile(D, 1),
                                        np.percentile(D, 5),
                                        np.median(D), 100 * fpd))
    print(prefix + "  N  p01 %5.3f  p05 %5.3f  median %5.3f      "
          "false FAIL on N: %4.1f%%" % (np.percentile(N, 1),
                                        np.percentile(N, 5),
                                        np.median(N), 100 * fpn))
    print(prefix + "  F  p99 %5.2f  p95 %5.2f  median %5.2f      "
          "false FAIL on F: %4.1f%%" % (np.percentile(F, 99),
                                        np.percentile(F, 95),
                                        np.median(F), 100 * fpf))
    print(prefix + "  FALSE POSITIVE RATE of the three bars together: %.1f%%"
          % (100 * fp.mean()))
    if res and res["verdict"] != "VOID":
        print(prefix + "  the judged fill sits at D pct %.1f, N pct %.1f, "
              "F pct %.1f of that null"
              % (100 * (D < res["D"]).mean(), 100 * (N < res["N"]).mean(),
                 100 * (F < res["F"]).mean()))
    return {"n": len(nulls), "fp": float(fp.mean()),
            "fp_D": float(fpd), "fp_N": float(fpn), "fp_F": float(fpf)}


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------
CASES = [
    ("b03", "ep2-b03-mac-plate-0819/03-bad-cover-mac-plate-r1s1.png",
     "ep2-b03-sapcomp-0820/03-bad-cover-sapcomp-0820.png"),
    ("b13", "ep2-b13-mac-plate-0819/13-the-shade-mac-plate-r1s1.png",
     "ep2-b13-sapcomp-0820/13-the-shade-sapcomp-0820.png"),
    ("b15", "ep2-b15-mac-plate-0819/15-good-listener-mac-plate-r1s1.png",
     "ep2-b15-sapcomp-0819/15-good-listener-sapcomp-0819.png"),
    ("b19", "ep2-b19-mac-plate-0819/19-the-drop-mac-plate-r3s1.png",
     "ep2-b19-sapcomp-0819/19-the-drop-sapcomp-0819.png"),
]


def _components(mask, min_px):
    """Connected components (8-way) of `mask`, largest first, >= min_px."""
    import numpy as np
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    n = 0
    for sy, sx in np.argwhere(mask):
        if lab[sy, sx]:
            continue
        n += 1
        lab[sy, sx] = n
        st = [(int(sy), int(sx))]
        while st:
            y, x = st.pop()
            y0, y1 = max(0, y - 1), min(h, y + 2)
            x0, x1 = max(0, x - 1), min(w, x + 2)
            sub = mask[y0:y1, x0:x1] & (lab[y0:y1, x0:x1] == 0)
            for dy, dx in np.argwhere(sub):
                lab[y0 + dy, x0 + dx] = n
                st.append((int(y0 + dy), int(x0 + dx)))
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    order = [c for c in np.argsort(sizes[1:])[::-1] + 1 if sizes[c] >= min_px]
    return [(int(c), lab == c, int(sizes[c])) for c in order]


def selftest():
    import numpy as np
    from PIL import Image
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import beat08_grip_composite as G

    bad, good, void = [], [], []

    def want(res, expect):
        print("  " + line(res))
        for f in res.get("fails", []):
            print("      %s" % f)
        if res["verdict"] == "VOID":
            void.append(res["label"])
        elif res["verdict"] != expect:
            bad.append("%s: got %s, wanted %s" % (res["label"], res["verdict"], expect))
        else:
            good.append(res["label"])

    # ---- 1. beat 08: the thing that must FAIL, and its real-pixel control --
    plate = np.asarray(Image.open(G.PLATE).convert("RGB"))
    init = np.asarray(Image.open(G.OUT_INIT).convert("RGB"))
    src = np.asarray(G.poly_mask(G.FIST, grow=2)) > 0
    dst = np.asarray(G.poly_mask([(x + G.DX, y + G.DY) for x, y in G.FIST],
                                 grow=2)) > 0
    hole = src & ~dst
    changed = np.abs(init.astype(int) - plate.astype(int)).max(axis=2) > 0

    print("\nBEAT 08 -- the vacancy C4 certified (%d px)" % hole.sum())
    corduroy = assess(init, hole, ~changed,
                      label="gripcomp fill ON DISK (corduroy)")
    want(corduroy, "FAIL")
    want(assess(G.fill_vacancy(plate.copy(), hole), hole, ~hole,
                label="same vacancy, isotropic diffusion (source)"), "FAIL")
    want(assess(plate, hole, ~changed,
                label="CONTROL: the same footprint, REAL plate px"), "PASS")

    # real fabric from the same garment, the same footprint moved around it
    ys, xs = np.nonzero(hole)
    print("\nBEAT 08 -- real fabric from the same garment, footprint moved")
    for dx, dy, nm in [(-14, -110, "strap, 110 px up"),
                       (-30, -170, "strap, higher"),
                       (-80, 40, "cream shirt, left"),
                       (-100, 130, "wrap skirt"),
                       (60, -90, "shoulder + clasp"),
                       (20, 120, "board / cuff")]:
        m = np.zeros_like(hole)
        m[ys + dy, xs + dx] = True
        want(assess(plate, m, ~m, label="real: " + nm), "PASS")

    # ---- 1b. the a-contrario null and the FALSE POSITIVE RATE -------------
    print("\nBEAT 08 -- the bars run against the plate's own real material")
    nl = empirical_null(plate, hole, ~changed, n=200)
    st = null_report(nl, corduroy)
    if st.get("fp", 1.0) > 0.05:
        bad.append("false positive rate %.1f%% on real material (want <= 5%%)"
                   % (100 * st["fp"]))

    # ---- 2. the composite fills that passed honestly ----------------------
    print("\nTHE HONEST COMPOSITE FILLS (vacancy components >= %d px)" % 2000)
    for name, pp, ip in CASES:
        p = np.asarray(Image.open(os.path.join(FO, pp)).convert("RGB"))
        i = np.asarray(Image.open(os.path.join(FO, ip)).convert("RGB"))
        ch = np.abs(i.astype(int) - p.astype(int)).max(axis=2) > 0
        Lp, Li = luma(p), luma(i)
        for c, m, npx in _components(ch, 2000):
            # a VACANCY is a component the composite made QUIETER: ink removed.
            # a SPRITE is new ink. C4' judges vacancies; sprites are authored
            # content and are meant NOT to match the neighbourhood (dead zone 2).
            if iso_detail(Li, m) >= iso_detail(Lp, m):
                print("  %-44s skipped: SPRITE (new ink, %d px)"
                      % ("%s c%d" % (name, c), npx))
                continue
            want(assess(i, m, ~ch, label="%s vacancy c%d" % (name, c)), "PASS")

    print("\n%d as expected, %d WRONG, %d void" % (len(good), len(bad), len(void)))
    for b in bad:
        print("  !! " + b)
    if void:
        print("  void (not counted either way): " + ", ".join(void))
    print("SELFTEST: %s" % ("PASS" if not bad else "FAIL"))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--plate", help="the untouched parent")
    ap.add_argument("--image", help="the composite to judge")
    ap.add_argument("--region", help="PNG mask of the fill; default = every "
                                     "changed component the composite quieted")
    ap.add_argument("--min-px", type=int, default=MIN_REGION)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.plate and a.image):
        ap.error("--selftest, or --plate and --image")

    import numpy as np
    from PIL import Image
    p = np.asarray(Image.open(a.plate).convert("RGB"))
    i = np.asarray(Image.open(a.image).convert("RGB"))
    if p.shape != i.shape:
        ap.error("plate %r and image %r are different sizes" % (p.shape, i.shape))
    ch = np.abs(i.astype(int) - p.astype(int)).max(axis=2) > 0
    print("changed %d px" % ch.sum())
    rc = 0
    if a.region:
        m = np.asarray(Image.open(a.region).convert("L")) > 127
        r = assess(i, m, ~ch, label=os.path.basename(a.region))
        print(line(r))
        for f in r.get("fails", []):
            print("    " + f)
        rc = 1 if r["verdict"] != "PASS" else 0
    else:
        Lp, Li = luma(p), luma(i)
        for c, m, npx in _components(ch, a.min_px):
            if iso_detail(Li, m) >= iso_detail(Lp, m):
                print("c%-4d %6d px  SPRITE (new ink) -- not a vacancy, skipped"
                      % (c, npx))
                continue
            r = assess(i, m, ~ch, label="c%d" % c)
            print(line(r))
            for f in r.get("fails", []):
                print("    " + f)
            rc |= 1 if r["verdict"] != "PASS" else 0
    return rc


if __name__ == "__main__":
    sys.exit(main())
