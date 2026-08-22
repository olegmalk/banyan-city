#!/usr/bin/env python3
r"""EP2 FINISH LANE: THE COLOUR GRADE THE PROMPT WAS SUPPOSED TO BUY AND DIDN'T.

WHY THIS FILE EXISTS, MEASURED BEFORE IT WAS WRITTEN
--------------------------------------------------------------------------
Two checkpoints on 2026-08-22 established that at strength 0.30 the prompt buys
nothing: `709a300c3` (framing is not promptable -- the crop chooses the frame,
the compositor chooses the ground) and `d5a251001` (four lights, one mean RGB,
delta 7.5 on every cell). This lane re-measured that on all 19 pass-two plates
against the five inits they were denoised from, and it is WORSE than delta 7.5:

    plate  init      mean|D|  %px>8   dMeanRGB    prompt asked for
    b02    full       10.38    33.5%     ~1.2     "bright morning light"
    b17    full       10.66    38.2%     ~1.0     "amber afternoon light"
    b14    headnat    10.50    35.6%     ~0.3     "warm midday light"
    b07    guard2     13.17    42.9%     ~0.9     "morning light"

Between one THIRD and one HALF of every plate's pixels moved more than 8 levels
-- the sampler engaged hard -- and the mean RGB moved by about ONE LEVEL. Every
one of those redrawn pixels went into redrawing the same picture in the same
light. That is precisely the beat-08 signature in composite-init-pattern.md 9b
(32.9% of pixels moved, all of it into redrawing the same staging), and it
closes the prompt lever on LIGHT the same way 9b closed it on STAGING.

So the pass-two plates are not four lights. They are THREE INITS:

    goblin full/cowboy/headnat  lum 166-178  sat 0.15-0.17  R-B  +7
    guard1 portrait             lum  97      sat 0.42       R-B +41
    guard2 portrait             lum 115      sat 0.28       R-B +21

THE FAULT THAT MATTERS IS NOT ANY ONE PLATE, IT IS THE CUT BETWEEN THEM. A beat
at lum 170 / sat 0.17 cutting to a beat at lum 97 / sat 0.42 is not a time of
day, it is two different films. All three clusters are the FOUNDER'S OWN canon
refs, so none of them is wrong and none may be overruled -- but they cannot sit
untreated in one episode either. Grading is the only remaining lever, and it is
the compositor's, at $0, on the CPU, reversible, and openable before it costs a
GPU second.

THE ARC, AND WHY THESE NUMBERS
--------------------------------------------------------------------------
The three stations below sit BETWEEN the two founder-approved clusters. No beat
is pushed outside the light he has already accepted; what changes is that the
170-vs-97 flicker collapses into a monotone reading of the day, with warmth
climbing into the afternoon the way the script's own clock does.

    MORNING    b02..b11   lum 132  R-B +14  sat 0.28
    MIDDAY     b14..b16   lum 142  R-B +11  sat 0.26
    AFTERNOON  b17..b21   lum 126  R-B +22  sat 0.31

The warmth figures are deliberately SHORT of the guard cluster's +41. The
luma flicker is the fault worth fixing; amber is a nice-to-have, and buying it
costs hue rotation on a character the founder has already rejected once for not
being his. Luma converges hard (170/97 -> 126..142), warmth moves a little,
and P-HUE holds every plate under 10 degrees.

WHAT THIS TOOL WILL NOT DO, AND IT REFUSES RATHER THAN WARNS
--------------------------------------------------------------------------
P-INK   The line art must stay line art. A lift that turns ink grey destroys
        the dialect. The 1st-percentile luma may not rise by more than
        --max-ink-lift levels, and the tool exits nonzero if it does.
P-CLIP  A grade that hits its mean by burning highlights is not a grade. No
        more than --max-clip percent of pixels may be pushed to 0 or 255 that
        were not already there.
P-HUE   ~~Nothing is hue-rotated.~~ WRONG, AND THE TOOL'S OWN GATE CAUGHT IT
        ON THE FIRST PLATE IT GRADED. House style: the superseded claim stays
        and the correction is written beside it. The saturation step really is
        hue-preserving (it moves each pixel along its own luma axis), but the
        TEMPERATURE step scales R and B against a fixed G and that IS a hue
        rotation. First run on b17, targeting the afternoon station as first
        written (R-B +38, taken from the guard1 cluster): mean hue drift 27.5
        degrees over 78% of chromatic pixels. On a character whose founder-
        named fault is literally "not my goblin", rotating his skin 27 degrees
        toward warm is the fault, not the fix. So P-HUE is now a GATE with a
        number (--max-hue-drift, default 10 deg) rather than a claim, and the
        afternoon target was pulled back from the guard's own +41 to +22.

P-SHADOW A saturation boost pushes dark pixels' low channel below zero, which
        crushes shadow detail into flat black -- b17's first run newly pinned
        0.887% of pixels to 0 and tripped P-CLIP. Both the temperature and the
        saturation steps are therefore rolled off in the shadows (full effect
        above luma 64, none below luma 24), which protects the ink and the
        shadow side of every figure for free.

Deterministic, numpy + PIL, no network, no model, no spend.

    python3 pipeline/ep2_finish_grade.py --plate <png> --station afternoon \
        --out <png> [--dry-run]
    python3 pipeline/ep2_finish_grade.py --report            # measure only
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# lum mean, R-B mean, mean saturation
STATIONS = {
    "morning":   {"lum": 132.0, "rb": 14.0, "sat": 0.28},
    "midday":    {"lum": 142.0, "rb": 11.0, "sat": 0.26},
    "afternoon": {"lum": 126.0, "rb": 22.0, "sat": 0.31},
}

# Shadow roll-off for the two steps that can crush or rotate dark pixels.
SHADOW_LO, SHADOW_HI = 24.0, 64.0

# Which station each ep2 beat belongs to. The script's own clock: the guards
# arrive in the morning, the middle of the episode is the middle of the day,
# and the goodbye/drop/answer run into the afternoon.
BEAT_STATION = {
    "b02": "morning", "b03": "morning", "b04": "morning", "b05": "morning",
    "b05g1": "morning", "b05g2": "morning", "b06": "morning",
    "b07": "morning", "b08g": "morning", "b09": "morning", "b10": "morning",
    "b11": "morning", "b11g1": "morning", "b11g2": "morning",
    "b14": "midday", "b15": "midday",
    "b17": "afternoon", "b19": "afternoon", "b20": "afternoon",
}

W_R, W_G, W_B = 0.299, 0.587, 0.114


def luma(a):
    return W_R * a[..., 0] + W_G * a[..., 1] + W_B * a[..., 2]


def satmean(a):
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    return float(np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0.0).mean())


def measure(a):
    m = a.reshape(-1, 3).mean(axis=0)
    return {"R": float(m[0]), "G": float(m[1]), "B": float(m[2]),
            "lum": float(luma(a).mean()), "rb": float(m[0] - m[2]),
            "sat": satmean(a), "p1": float(np.percentile(luma(a), 1)),
            "p99": float(np.percentile(luma(a), 99))}


def apply_gamma(a, g):
    """Luma-targeting gamma on 0..255 float, hue and ratio preserving."""
    l0 = luma(a)
    l1 = 255.0 * np.power(np.clip(l0, 0, 255) / 255.0, g)
    scale = np.where(l0 > 1e-6, l1 / np.maximum(l0, 1e-6), 1.0)
    return a * scale[..., None]


def solve_gamma(a, target_lum, lo=0.25, hi=4.0, iters=40):
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if luma(apply_gamma(a, mid)).mean() > target_lum:
            lo = mid            # bigger gamma -> darker, so go up
        else:
            hi = mid
    return 0.5 * (lo + hi)


def shadow_weight(a):
    """1 in the midtones and highlights, 0 in the ink. Smoothstep so there is
    no visible band where the roll-off begins."""
    t = np.clip((luma(a) - SHADOW_LO) / (SHADOW_HI - SHADOW_LO), 0.0, 1.0)
    return (t * t * (3.0 - 2.0 * t))[..., None]


def apply_temp(a, k):
    """Warm/cool by a symmetric R/B gain pair; G untouched so the mid stays.
    Rolled off in shadows -- this step rotates hue, so the ink is held out of
    it (see P-HUE in the docstring)."""
    w = shadow_weight(a)
    out = a.copy()
    out[..., 0] *= (1.0 + k * w[..., 0])
    out[..., 2] *= (1.0 - k * w[..., 0])
    return out


def solve_temp(a, target_rb, lo=-0.45, hi=0.45, iters=40):
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        t = apply_temp(a, mid)
        if float(t[..., 0].mean() - t[..., 2].mean()) < target_rb:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def apply_sat(a, s):
    """Scale each pixel away from its OWN luma -- hue preserved exactly.
    Rolled off in shadows: a boost applied to a dark pixel drives its low
    channel below zero, which is what crushed 0.887% of b17 to flat black."""
    l = luma(a)[..., None]
    s_eff = 1.0 + (s - 1.0) * shadow_weight(a)
    return l + (a - l) * s_eff


def solve_sat(a, target_sat, lo=0.05, hi=6.0, iters=40):
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if satmean(np.clip(apply_sat(a, mid), 0, 255)) < target_sat:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def blended_target(m0, station, t):
    """Interpolate between the plate's OWN measurement and the station."""
    tgt = STATIONS[station]
    return {k: m0[k] + (tgt[k] - m0[k]) * t for k in ("lum", "rb", "sat")}


SOLVE_STRIDE = 4        # every 4th pixel: all three targets are plain means


def grade_to(arr_u8, tgt, rounds=3):
    """Hit lum, R-B and saturation together. Each knob perturbs the others, so
    the three solves are iterated rather than applied once; three rounds is
    enough to land every plate in this set inside tolerance (asserted below).

    The three bisections run on a STRIDED copy and the knobs they find are then
    applied once to the full plate. All three targets are means over the whole
    frame, so a 1-in-16 sample estimates them to well inside the tolerances
    (checked: every plate in this set lands identically either way) -- and it
    makes --converge, which grades the plate up to fifteen times, actually
    runnable on a CPU."""
    small = arr_u8[::SOLVE_STRIDE, ::SOLVE_STRIDE].astype(np.float32)
    knobs = {"gamma": [], "temp": [], "sat": []}
    for _ in range(rounds):
        g = solve_gamma(small, tgt["lum"]);  small = apply_gamma(small, g)
        k = solve_temp(small, tgt["rb"]);    small = apply_temp(small, k)
        s = solve_sat(small, tgt["sat"])
        small = np.clip(apply_sat(small, s), 0, 255)
        knobs["gamma"].append(round(g, 5))
        knobs["temp"].append(round(k, 5))
        knobs["sat"].append(round(s, 5))
    a = arr_u8.astype(np.float32)
    for g, k, s in zip(knobs["gamma"], knobs["temp"], knobs["sat"]):
        a = apply_gamma(a, g)
        a = apply_temp(a, k)
        a = np.clip(apply_sat(a, s), 0, 255)
    return np.clip(a, 0, 255), knobs


def gate(src_u8, out_u8, tgt, opt):
    """Every refusal in one place so --converge and the strict path cannot
    drift apart. Returns (fails, stats)."""
    m1 = measure(out_u8.astype(np.float32))
    m0 = measure(src_u8.astype(np.float32))
    fails = []
    if abs(m1["lum"] - tgt["lum"]) > opt.tol_lum:
        fails.append("lum off target by %.2f" % (m1["lum"] - tgt["lum"]))
    if abs(m1["rb"] - tgt["rb"]) > opt.tol_rb:
        fails.append("R-B off target by %.2f" % (m1["rb"] - tgt["rb"]))
    if abs(m1["sat"] - tgt["sat"]) > opt.tol_sat:
        fails.append("sat off target by %.3f" % (m1["sat"] - tgt["sat"]))

    lift = m1["p1"] - m0["p1"]
    if lift > opt.max_ink_lift:
        fails.append("INK LIFT %+.1f exceeds %+.1f -- the grade is greying the "
                     "line art and that destroys the dialect"
                     % (lift, opt.max_ink_lift))

    s16, o16 = src_u8.astype(np.int16), out_u8.astype(np.int16)
    new_hi = float(((o16 >= 255) & (s16 < 255)).any(axis=2).mean() * 100.0)
    new_lo = float(((o16 <= 0) & (s16 > 0)).any(axis=2).mean() * 100.0)
    if max(new_hi, new_lo) > opt.max_clip:
        fails.append("CLIPPING %.3f%% high / %.3f%% low exceeds %.2f%%"
                     % (new_hi, new_lo, opt.max_clip))

    def hue_of(x):
        mx, mn = x.max(axis=2), x.min(axis=2)
        return np.where(mx - mn > 6, np.arctan2(
            np.sqrt(3) * (x[..., 1] - x[..., 2]),
            2 * x[..., 0] - x[..., 1] - x[..., 2]), np.nan)
    h0 = hue_of(src_u8.astype(np.float32))
    h1 = hue_of(out_u8.astype(np.float32))
    ok = ~(np.isnan(h0) | np.isnan(h1))
    dh = np.abs(np.arctan2(np.sin(h1[ok] - h0[ok]), np.cos(h1[ok] - h0[ok])))
    drift = float(np.degrees(dh.mean())) if ok.any() else 0.0
    if drift > opt.max_hue_drift:
        fails.append("HUE DRIFT %.2f deg exceeds %.1f -- this grade is "
                     "recolouring the character, not lighting him"
                     % (drift, opt.max_hue_drift))

    return fails, {"before": m0, "after": m1, "ink_lift": lift,
                   "new_clip_high_pct": new_hi, "new_clip_low_pct": new_lo,
                   "hue_drift_deg": drift, "chromatic_frac": float(ok.mean())}


def converge(src_u8, station, opt, steps=14):
    """THE HONEST MODE. The station is an aspiration; the gates are the law.

    Measured on this plate set: the guard1 cluster CANNOT reach the morning
    station. Lifting a warm dark portrait (lum 98, sat 0.41, R-B +41) to lum
    132 / sat 0.28 / R-B +14 costs an ink lift of +24.9 and a hue rotation of
    26.5 degrees -- it does not light the guard, it repaints him. Forcing it
    would be exactly the bar-bending composite-init-pattern.md 10.5 forbids.

    So instead of failing those plates outright, walk t from 1 down to 0 along
    the line between the plate's own measurement and the station, and keep the
    LARGEST t whose output passes every gate. A plate that can only close 40%%
    of the gap closes 40%% of it and says so. Convergence is reported per plate
    as `t`, and the residual is left visible rather than hidden."""
    m0 = measure(src_u8.astype(np.float32))
    best = None
    for i in range(steps + 1):
        t = 1.0 - i / float(steps)
        tgt = blended_target(m0, station, t)
        out_f, knobs = grade_to(src_u8, tgt)
        out = out_f.astype(np.uint8)
        fails, stats = gate(src_u8, out, tgt, opt)
        if not fails:
            best = (t, tgt, out, knobs, stats)
            break
    if best is None:                     # t == 0 is the identity, always passes
        tgt = blended_target(m0, station, 0.0)
        best = (0.0, tgt, src_u8.copy(), {"gamma": [], "temp": [], "sat": []},
                gate(src_u8, src_u8, tgt, opt)[1])
    return best


def sha256_of(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def report():
    print("%-7s %-10s %6s %6s %6s | %6s %6s %6s"
          % ("plate", "station", "lum", "R-B", "sat", "->lum", "->R-B", "->sat"))
    for p in sorted(glob.glob(os.path.join(
            REPO, "farm-out/ep2-finish-plates-0822/b*.png"))):
        t = os.path.basename(p)[:-4]
        if "mask" in t or t not in BEAT_STATION:
            continue
        a = np.asarray(Image.open(p).convert("RGB")).astype(np.float32)
        m0 = measure(a)
        st = BEAT_STATION[t]
        print("%-7s %-10s %6.1f %6.1f %6.3f | %6.1f %6.1f %6.3f"
              % (t, st, m0["lum"], m0["rb"], m0["sat"],
                 STATIONS[st]["lum"], STATIONS[st]["rb"], STATIONS[st]["sat"]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true",
                    help="measure every pass-two plate against its station and exit")
    ap.add_argument("--plate")
    ap.add_argument("--plate-sha256", default=None)
    ap.add_argument("--station", choices=sorted(STATIONS),
                    help="default: looked up from the plate's beat tag")
    ap.add_argument("--out")
    ap.add_argument("--converge", action="store_true",
                    help="walk back from the station until every gate passes, "
                         "and report how far the plate actually got. Use this "
                         "for plates a full-target grade would repaint.")
    ap.add_argument("--min-t", type=float, default=0.35,
                    help="with --converge, refuse a plate that cannot close at "
                         "least this fraction of its gap -- a 5%% grade is not "
                         "a grade and should not be filed as one")
    ap.add_argument("--max-ink-lift", type=float, default=14.0,
                    help="1st-percentile luma may not rise more than this")
    ap.add_argument("--max-clip", type=float, default=0.60,
                    help="max %% of pixels newly pinned to 0 or 255")
    ap.add_argument("--max-hue-drift", type=float, default=10.0,
                    help="max mean hue rotation in degrees over chromatic px. "
                         "The temperature step rotates hue; on a character "
                         "whose named fault is 'not my goblin' this is a gate, "
                         "not a note. b17 at the first afternoon target drifted "
                         "27.5 deg and that target was pulled back.")
    ap.add_argument("--tol-lum", type=float, default=2.0)
    ap.add_argument("--tol-rb", type=float, default=2.0)
    ap.add_argument("--tol-sat", type=float, default=0.02)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.report:
        return report()
    if not a.plate or not a.out:
        raise SystemExit("!! --plate and --out are required (or use --report)")

    have = sha256_of(a.plate)
    if a.plate_sha256 and have != a.plate_sha256:
        raise SystemExit("!! plate sha mismatch\n   want %s\n   have %s"
                         % (a.plate_sha256, have))
    tag = os.path.basename(a.plate)[:-4]
    station = a.station or BEAT_STATION.get(tag)
    if station is None:
        raise SystemExit("!! no station for %r and --station not given" % tag)

    src = np.asarray(Image.open(a.plate).convert("RGB"))
    m0 = measure(src.astype(np.float32))
    full = STATIONS[station]

    if a.converge:
        t, tgt, out, knobs, stats = converge(src, station, a)
        fails = []
        if t < a.min_t:
            fails.append("CONVERGED ONLY t=%.2f, below --min-t %.2f -- this "
                         "plate cannot be brought toward %s without breaking a "
                         "gate, and a token grade is worse than none"
                         % (t, a.min_t, station))
    else:
        t, tgt = 1.0, full
        out_f, knobs = grade_to(src, tgt)
        out = out_f.astype(np.uint8)
        fails, stats = gate(src, out, tgt, a)

    m1 = stats["after"]
    print("plate   %s  %dx%d  sha %s" % (tag, src.shape[1], src.shape[0], have[:16]))
    print("station %s  full target lum %.1f  R-B %.1f  sat %.3f"
          % (station, full["lum"], full["rb"], full["sat"]))
    if a.converge:
        print("converge t=%.3f -> effective target lum %.1f  R-B %.1f  sat %.3f"
              % (t, tgt["lum"], tgt["rb"], tgt["sat"]))
        print("residual gap to station: lum %+.1f  R-B %+.1f  sat %+.3f"
              % (full["lum"] - m1["lum"], full["rb"] - m1["rb"],
                 full["sat"] - m1["sat"]))
    print("before  lum %6.1f  R-B %6.1f  sat %.3f  p1 %5.1f  p99 %5.1f"
          % (m0["lum"], m0["rb"], m0["sat"], m0["p1"], m0["p99"]))
    print("after   lum %6.1f  R-B %6.1f  sat %.3f  p1 %5.1f  p99 %5.1f"
          % (m1["lum"], m1["rb"], m1["sat"], m1["p1"], m1["p99"]))
    print("knobs   gamma %s  temp %s  sat %s"
          % (knobs["gamma"], knobs["temp"], knobs["sat"]))
    print("P-INK   1st-pct luma %5.1f -> %5.1f  (lift %+.1f, max %+.1f)"
          % (m0["p1"], m1["p1"], stats["ink_lift"], a.max_ink_lift))
    print("P-CLIP  newly pinned  high %.3f%%  low %.3f%%  (max %.2f%%)"
          % (stats["new_clip_high_pct"], stats["new_clip_low_pct"], a.max_clip))
    print("P-HUE   mean hue drift %.2f deg over %.1f%% chromatic px (max %.1f)"
          % (stats["hue_drift_deg"], 100.0 * stats["chromatic_frac"],
             a.max_hue_drift))

    if fails:
        for f in fails:
            print("!! FAIL: %s" % f)
        return 3
    print("PASS -- targets inside tolerance, ink held, no clipping, hue held")

    if a.dry_run:
        print("dry run -- nothing written")
        return 0
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    Image.fromarray(out).save(a.out)
    side = a.out + ".grade.json"
    rec = {"plate": a.plate, "plate_sha256": have, "station": station,
           "full_target": full, "effective_target": tgt, "converge_t": t,
           "knobs": knobs, "tool": "pipeline/ep2_finish_grade.py",
           "out_sha256": sha256_of(a.out)}
    rec.update(stats)
    with open(side, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True, default=float)
    print("out     %s  sha %s" % (a.out, sha256_of(a.out)[:16]))
    print("sidecar %s" % side)
    return 0


if __name__ == "__main__":
    sys.exit(main())
