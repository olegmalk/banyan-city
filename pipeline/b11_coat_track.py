#!/usr/bin/env python3
"""beat-11 THEY LEAVE -- the recession instrument, with its gates.

    python3 pipeline/b11_coat_track.py --gates
    python3 pipeline/b11_coat_track.py <clip.mp4> [label]

WHAT IT MEASURES AND WHY THAT AND NOT SOMETHING EASIER
======================================================
Beat 11's D2 is "they end further away than they began, BY THEIR OWN HEIGHT IN
FRAME AND NOT BY THE CAMERA MOVING". That is a scale claim, and this week seven
measures were retired for cause, two of which would have given confident wrong
verdicts -- one reported a STATIONARY hand travelling 96 px. So the rule this
file obeys is the one those retirements bought:

    A SCALE CLAIM CARRIES AN INTERNAL CONTROL, AND THE INSTRUMENT PASSES A
    FROZEN GATE, A SYNTHETIC SCALE GATE, A SYNTHETIC PAN GATE AND A SYNTHETIC
    EXIT GATE BEFORE IT JUDGES ANYTHING.

1. THE MASK IS WARMTH, AND IT IS STRUCTURAL RATHER THAN A TUNED THRESHOLD.
Measured on this beat's own published plate (`11-they-leave-mac-plate-r3s1`):

    tan tunic  (guard A)  R149 G122 B 94    R-G  +26   mean 121
    brown coat (guard B)  R 93 G 71 B 59    R-G  +21   mean  83
    grass, mid            R148 G173 B 90    R-G  -25
    grass, low            R163 G177 B 79    R-G  -14
    grass, shadowed       R 81 G125 B 72    R-G  -44
    treeline              R202 G222 B159    R-G  -20
    sky                   R228 G241 B207    R-G  -13

`R - G` puts every coat pixel on one side of zero and every background pixel on
the other with a 20+ margin both ways. It is NOT a brightness rule: the shadowed
grass (mean 92) is BRIGHTER than the brown coat (mean 83), so a darkness rule
would eat half the field and miss guard B.

2. THE TWO MEN ARE TWO SEPARATE MASKS, BY THEIR OWN COSTUMES -- and this is the
correction that the first version of this file needed. Connected components on
one warm mask gave the right answer at f000 and a WRONG one later: the two men
walk shoulder to shoulder, so their coats TOUCH and merge into a single blob. At
f048 of the base W4 clip that single blob spans x186-437, and a component counter
reads it as ONE MAN -- i.e. it reports a D4 failure on a clip where both men are
plainly visible in the frame, and it lets a nearby warm speck steal the second
track (the first version reported the right man's mean colour going 82 -> 213,
which is the sunlit dirt path, not a man). That is precisely the "kept emitting
numbers after it lost the thing it was tracking" defect.

    TAN   band: warm AND 100 <= mean < 165   -> guard A's tunic  (measures 117-121)
    BROWN band: warm AND  40 <= mean < 100   -> guard B's coat   (measures  82- 99)

The bands are disjoint, so a merge cannot confuse the two men, and the upper cap
at 165 is what excludes the two real distractors measured in these clips: the
sunlit dirt path at the top left (mean 183-217) and the warm grass tufts at the
bottom (mean 169-201). DISCLOSED, not tidied away: guard B's light sandy HAIR
(mean ~150) falls in the TAN band. It is a ~2,000 px island detached from guard
A's 22,000 px tunic, so the largest-blob rule never confuses them, and it is
reported as the second TAN blob rather than hidden.

3. THE CONTROL IS A FITTED GLOBAL FRAMING TRANSFORM, not a landmark. NCC
landmarks were tried first and MUST NOT be used on this beat: the field is
windblown grass, so a grass patch is not a stationary object -- the grass
landmarks lost their patches outright (worst correlation 0.39-0.43, search
saturated) which is a measure reporting motion of something that genuinely moved.
Instead, for each frame this file FITS a similarity transform (uniform scale +
translation) between frame 0 and frame k over the BACKGROUND ONLY -- every pixel
outside a dilated union of the two coat masks -- by direct search on a downsampled
image, maximising correlation. That yields `bg_scale`, and the honest D2 figure is

    NET RECESSION = coat height ratio / bg_scale

    coat ratio 0.52, bg_scale 1.00  -> THE MEN RECEDED           (D2 earned)
    coat ratio 0.52, bg_scale 0.52  -> THE CAMERA PULLED BACK    (D2 not earned)

4. NOT COMPUTED AND NOT QUOTED, by standing rule: depth (retired AND inverted --
a full stand-up scores 0.290, a zero-motion clip 0.516, a bird-only clip 0.376)
and the old cadence statistic (odd hold periods alias to exactly 1.00x). The
terminal-freeze index is reported SEPARATELY from the hold, as the count of
consecutive frames at EXACT ncc = 1.0000 at the tail.

THE READING IS THE VERDICT. This file is a filter that says where to look and how
much a thing changed. D3 (no face shown) is not measurable here and is not
attempted: it is decided by opening head crops.
"""
import argparse
import json
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

WARM = 8              # R-G >= this is a coat pixel
TAN_LO, TAN_HI = 100, 165     # guard A's tunic
BRN_LO, BRN_HI = 40, 100      # guard B's coat
BLOB_MIN = 800        # candidate floor, low enough for a receded man

# A MAN IS NOT MERELY A WARM BLOB. A band's largest blob counts as its man only
# if it is at least MAN_FRAC of that same band's f000 blob. On these clips the
# floor lands near 2,600 px, which clears every distractor and sits far under a
# man who has receded to half his height (still ~25% of his f000 area).
MAN_FRAC = 0.12

# Background-fit search, in FULL-RESOLUTION pixels but evaluated on a /4 grid.
# COARSE-TO-FINE, because the flat grid was not a wrong measurement, it was an
# unusable one: 33 scales x 23 x 23 shifts is 17,457 correlations per frame and
# the gates did not finish in two minutes. Coarse pass then a refinement around
# its winner is ~1,000 correlations and lands on the same optimum -- which the
# scale and pan gates check by demanding the KNOWN answer back.
FIT_DS = 4
FIT_COARSE_SCALES = np.arange(0.60, 1.4001, 0.04)
FIT_FINE_SCALES = np.arange(-0.03, 0.0301, 0.01)
FIT_SHIFT = 44
FIT_COARSE_STEP = 12
FIT_FINE_STEP = 4


def frames_rgb(path):
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                         "-show_entries", "stream=width,height", "-of",
                         "csv=p=0", str(path)], capture_output=True)
    w, h = [int(x) for x in pr.stdout.decode().strip().split(",")[:2]]
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vsync", "0",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode()[:400])
    buf = np.frombuffer(p.stdout, dtype=np.uint8)
    n = buf.size // (w * h * 3)
    return buf[:n * w * h * 3].reshape(n, h, w, 3).astype(np.int16), w, h


def band_mask(frame, lo, hi):
    mn = frame.mean(axis=2)
    return ((frame[..., 0] - frame[..., 1]) >= WARM) & (mn >= lo) & (mn < hi)


def band_blobs(frame, lo, hi):
    m = band_mask(frame, lo, hi)
    lab, n = ndimage.label(m)
    if n == 0:
        return []
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    out = []
    for i, s in enumerate(sizes, start=1):
        if s < BLOB_MIN:
            continue
        ys, xs = np.nonzero(lab == i)
        px = frame[ys, xs]
        out.append({"area": int(s), "y0": int(ys.min()), "y1": int(ys.max()),
                    "x0": int(xs.min()), "x1": int(xs.max()),
                    "h": int(ys.max() - ys.min() + 1),
                    "w": int(xs.max() - xs.min() + 1),
                    "cx": float(xs.mean()), "cy": float(ys.mean()),
                    "mean": float(px.mean())})
    out.sort(key=lambda b: -b["area"])
    return out


def _bg_ref(f0):
    """Frame 0's background: /4 grey, the background weight map, the normalised
    reference vector and the full-res sample coordinates."""
    men = (band_mask(f0, TAN_LO, TAN_HI) | band_mask(f0, BRN_LO, BRN_HI))
    men = ndimage.binary_dilation(men, iterations=12)
    gs = f0.mean(axis=2)[::FIT_DS, ::FIT_DS]
    ws = (~men)[::FIT_DS, ::FIT_DS].astype(np.float64)
    H, W = gs.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    cy, cx = (H - 1) / 2.0, (W - 1) / 2.0
    a = (gs - (gs * ws).sum() / ws.sum()) * ws
    return {"ws": ws, "wsum": ws.sum(), "a": a,
            "an": float(np.sqrt((a * a).sum()) or 1.0),
            "yy": yy - cy, "xx": xx - cx, "cy": cy, "cx": cx,
            "shape": (H, W)}


def bg_fit(f0, fk, ref=None):
    """Best (scale, dy, dx) mapping frame 0's BACKGROUND onto frame k.

    Coarse-to-fine search, correlation over the weighted background only. The
    achieved correlation is returned so a BAD fit is visible instead of being
    quoted as if it were good."""
    R = ref if ref is not None else _bg_ref(f0)
    ws, wsum, a, an = R["ws"], R["wsum"], R["a"], R["an"]
    gk = fk.mean(axis=2)
    h, w = gk.shape

    def score(s, dy, dx):
        py = np.clip(((R["yy"] * s + R["cy"]) * FIT_DS + dy).astype(np.int32),
                     0, h - 1)
        px = np.clip(((R["xx"] * s + R["cx"]) * FIT_DS + dx).astype(np.int32),
                     0, w - 1)
        b = gk[py, px]
        b = (b - (b * ws).sum() / wsum) * ws
        bn = np.sqrt((b * b).sum()) or 1.0
        return float((a * b).sum() / (an * bn))

    best = (-2.0, 1.0, 0, 0)
    for s in FIT_COARSE_SCALES:
        for dy in range(-FIT_SHIFT, FIT_SHIFT + 1, FIT_COARSE_STEP):
            for dx in range(-FIT_SHIFT, FIT_SHIFT + 1, FIT_COARSE_STEP):
                v = score(s, dy, dx)
                if v > best[0]:
                    best = (v, float(s), dy, dx)
    _, bs, bdy, bdx = best
    for ds in FIT_FINE_SCALES:
        s = round(bs + ds, 3)
        for dy in range(bdy - FIT_COARSE_STEP, bdy + FIT_COARSE_STEP + 1,
                        FIT_FINE_STEP):
            for dx in range(bdx - FIT_COARSE_STEP, bdx + FIT_COARSE_STEP + 1,
                            FIT_FINE_STEP):
                v = score(s, dy, dx)
                if v > best[0]:
                    best = (v, s, dy, dx)
    return {"ncc": round(best[0], 4), "scale": round(best[1], 3),
            "dy": best[2], "dx": best[3]}


def terminal_freeze(frames):
    """Consecutive EXACT ncc = 1.0000 pairs at the tail. Reported separately
    from the hold and never merged with it."""
    n = 0
    for i in range(len(frames) - 1, 0, -1):
        a = frames[i].astype(np.float64).ravel()
        b = frames[i - 1].astype(np.float64).ravel()
        a = a - a.mean()
        b = b - b.mean()
        d = (np.sqrt((a ** 2).sum()) * np.sqrt((b ** 2).sum())) or 1.0
        if round(float((a * b).sum() / d), 4) >= 1.0:
            n += 1
        else:
            break
    return n


BANDS = (("tan", TAN_LO, TAN_HI), ("brown", BRN_LO, BRN_HI))


def analyse(clip, label="clip", frames=None, fit_every=8):
    if frames is None:
        frames, _, _ = frames_rgb(clip)
    nf = len(frames)
    res = {"label": label, "clip": str(clip), "frames": nf}

    ref = {}
    for name, lo, hi in BANDS:
        bs = band_blobs(frames[0], lo, hi)
        if not bs:
            res["fatal"] = "f000 has no %s blob -- the plate is not this scene" % name
            return res
        ref[name] = bs[0]
    res["f000"] = {k: {"area": v["area"], "h": v["h"], "w": v["w"],
                       "mean": round(v["mean"], 1),
                       "box": [v["y0"], v["y1"], v["x0"], v["x1"]]}
                   for k, v in ref.items()}

    series = {}
    missing = {}
    for name, lo, hi in BANDS:
        floor = MAN_FRAC * ref[name]["area"]
        hs, ms, ar, miss = [], [], [], []
        for i in range(nf):
            bs = [b for b in band_blobs(frames[i], lo, hi) if b["area"] >= floor]
            if not bs:
                hs.append(None)
                ms.append(None)
                ar.append(None)
                miss.append(i)
                continue
            b = bs[0]
            hs.append(b["h"])
            ms.append(round(b["mean"], 1))
            ar.append(b["area"])
        series[name] = {"h": hs, "mean": ms, "area": ar, "floor": int(floor)}
        missing[name] = miss

    for name, _, _ in BANDS:
        hs = series[name]["h"]
        v = [x for x in hs if x is not None]
        res["%s_h_first_last" % name] = (v[0], v[-1]) if v else None
        res["%s_h_ratio" % name] = round(v[-1] / v[0], 3) if v else None
        res["%s_h_min" % name] = min(v) if v else None
        res["%s_mean_first_last" % name] = (series[name]["mean"][0],
                                            [x for x in series[name]["mean"]
                                             if x is not None][-1])
        res["%s_missing_frames" % name] = missing[name]
        res["%s_h_series" % name] = hs

    res["both_men_every_frame"] = not (missing["tan"] or missing["brown"])
    res["first_frame_missing_a_man"] = min(
        [f for f in (missing["tan"] + missing["brown"])] or [None]) \
        if (missing["tan"] or missing["brown"]) else None
    res["colour_gap_first_last"] = (
        round(res["tan_mean_first_last"][0] - res["brown_mean_first_last"][0], 1),
        round(res["tan_mean_first_last"][1] - res["brown_mean_first_last"][1], 1))

    bgref = _bg_ref(frames[0])
    fits = {}
    for i in list(range(0, nf, fit_every)) + [nf - 1]:
        fits[i] = bg_fit(frames[0], frames[i], ref=bgref)
    res["bg_fit"] = {str(k): v for k, v in sorted(fits.items())}
    last = fits[nf - 1]
    res["bg_scale_last"] = last["scale"]
    res["bg_shift_last"] = [last["dy"], last["dx"]]
    res["bg_ncc_last"] = last["ncc"]
    res["bg_scale_range"] = [min(f["scale"] for f in fits.values()),
                             max(f["scale"] for f in fits.values())]
    for name, _, _ in BANDS:
        r = res["%s_h_ratio" % name]
        res["%s_net_recession" % name] = (
            round(r / last["scale"], 3) if r and last["scale"] else None)
    res["terminal_freeze_index"] = terminal_freeze(frames)
    return res


# =====================================================================
# THE GATES. Nothing is judged until all five pass, and they are run on
# this beat's own published plate so the mask meets real pixels.
# =====================================================================
def _plate_frame(plate):
    im = Image.open(plate).convert("RGB")
    sw, sh = im.size
    if (sh, sw) != (1280, 704):
        sc = max(704 / float(sw), 1280 / float(sh))
        im = im.resize((int(round(sw * sc)), int(round(sh * sc))), Image.LANCZOS)
        nw, nh = im.size
        im = im.crop(((nw - 704) // 2, (nh - 1280) // 2,
                      (nw - 704) // 2 + 704, (nh - 1280) // 2 + 1280))
    return np.asarray(im).astype(np.int16)


def _synth_frozen(f0, n=25):
    return np.stack([f0] * n)


def _synth_scale(f0, n=25, end=0.70):
    """A TRUE camera pull-back: the men shrink AND so does everything else."""
    h, w, _ = f0.shape
    im0 = Image.fromarray(f0.astype(np.uint8))
    out = []
    for k in range(n):
        s = 1.0 + (end - 1.0) * (k / float(n - 1))
        nw, nh = max(2, int(round(w * s))), max(2, int(round(h * s)))
        im = im0.resize((nw, nh), Image.LANCZOS)
        canvas = Image.fromarray(
            np.repeat(np.repeat(f0[:1, :1].astype(np.uint8), h, 0), w, 1))
        canvas.paste(im, ((w - nw) // 2, (h - nh) // 2))
        out.append(np.asarray(canvas).astype(np.int16))
    return np.stack(out)


def _synth_pan(f0, n=25, end_dy=-40, end_dx=28):
    """Translation only. An instrument that reports a coat shrinking here is
    reporting motion it cannot see -- the exact class of error that retired the
    measure which called a stationary hand 96 px."""
    out = []
    for k in range(n):
        t = k / float(n - 1)
        out.append(np.roll(np.roll(f0, int(round(end_dy * t)), axis=0),
                           int(round(end_dx * t)), axis=1))
    return np.stack(out)


def _synth_exit(f0, n=25, gone_at=12):
    """From `gone_at` on, guard A's box is overwritten with field taken from the
    FAR RIGHT EDGE. The first version sourced it from `x1 + 60`, which on this
    plate is the OTHER man, so it pasted guard B over guard A and the gate
    correctly reported two men still visible. Left in the record: the gate
    caught the gate's own bug, which is why one has gates."""
    a = band_blobs(f0, TAN_LO, TAN_HI)[0]
    h, w, _ = f0.shape
    bw = a["x1"] - a["x0"] + 1
    sx = max(0, w - bw - 4)
    out = []
    for k in range(n):
        g = f0.copy()
        if k >= gone_at:
            g[a["y0"]:a["y1"] + 1, a["x0"]:a["x1"] + 1] = \
                f0[a["y0"]:a["y1"] + 1, sx:sx + bw]
        out.append(g)
    return np.stack(out)


def gates(plate):
    f0 = _plate_frame(plate)
    ok = True

    print("GATE 0  BAND SEPARATION on the published plate")
    for name, lo, hi in BANDS:
        bs = band_blobs(f0, lo, hi)
        areas = [b["area"] for b in bs]
        margin = (areas[0] / float(areas[1])) if len(areas) > 1 else float("inf")
        b = bs[0]
        print("   %-5s blobs %s  dominant y%d-%d x%d-%d h%d mean%.0f  margin %.1fx"
              % (name, areas[:3], b["y0"], b["y1"], b["x0"], b["x1"], b["h"],
                 b["mean"], margin))
        g = margin >= 8.0 and b["h"] > 200 and b["area"] > 10000
        ok &= g
        if not g:
            print("   FAIL %s band does not dominate" % name)
    tan, brn = band_blobs(f0, TAN_LO, TAN_HI)[0], band_blobs(f0, BRN_LO, BRN_HI)[0]
    sep = tan["mean"] - brn["mean"]
    overlap = (band_mask(f0, TAN_LO, TAN_HI) & band_mask(f0, BRN_LO, BRN_HI)).sum()
    print("   tan-minus-brown mean gap %.1f | bands share %d px (must be 0)"
          % (sep, overlap))
    print("   left man is the TAN one (x%d) and right is the BROWN one (x%d): %s"
          % (tan["x0"], brn["x0"], tan["x0"] < brn["x0"]))
    g0b = sep > 20 and overlap == 0 and tan["x0"] < brn["x0"]
    ok &= g0b
    print("   %s the two costumes are separable and disjoint by construction"
          % ("PASS" if g0b else "FAIL"))

    print("GATE 1  FROZEN -- copies of one frame")
    r = analyse("<frozen>", "frozen", frames=_synth_frozen(f0), fit_every=6)
    g1 = (r["tan_h_ratio"] == 1.0 and r["brown_h_ratio"] == 1.0
          and r["bg_scale_last"] == 1.0 and r["bg_shift_last"] == [0, 0]
          and r["both_men_every_frame"])
    print("   coat h ratio tan %s brown %s | bg_scale %s shift %s ncc %s"
          % (r["tan_h_ratio"], r["brown_h_ratio"], r["bg_scale_last"],
             r["bg_shift_last"], r["bg_ncc_last"]))
    print("   terminal_freeze_index %d of %d (a frozen clip must be all of it)"
          % (r["terminal_freeze_index"], r["frames"]))
    print("   %s no motion invented" % ("PASS" if g1 else "FAIL"))
    ok &= g1

    print("GATE 2  SYNTHETIC SCALE -- true pull-back, ramp 1.00 -> 0.70")
    r = analyse("<scale>", "scale", frames=_synth_scale(f0), fit_every=6)
    nt, nb = r["tan_net_recession"], r["brown_net_recession"]
    g2 = (abs(r["tan_h_ratio"] - 0.70) <= 0.06
          and abs(r["brown_h_ratio"] - 0.70) <= 0.06
          and abs(r["bg_scale_last"] - 0.70) <= 0.05
          and abs(nt - 1.0) <= 0.10 and abs(nb - 1.0) <= 0.10)
    print("   coat h ratio tan %s brown %s (want ~0.70)"
          % (r["tan_h_ratio"], r["brown_h_ratio"]))
    print("   bg_scale %s (want ~0.70 -- the control MUST see the camera)"
          % r["bg_scale_last"])
    print("   NET RECESSION tan %s brown %s (want ~1.00 -- nobody walked)" % (nt, nb))
    print("   %s a camera pull-back is not scored as a recession"
          % ("PASS" if g2 else "FAIL"))
    ok &= g2

    print("GATE 3  SYNTHETIC PAN -- translation only, dy -40 dx +28, no scale")
    r = analyse("<pan>", "pan", frames=_synth_pan(f0), fit_every=6)
    g3 = (abs(r["tan_h_ratio"] - 1.0) <= 0.04
          and abs(r["brown_h_ratio"] - 1.0) <= 0.04
          and abs(r["bg_scale_last"] - 1.0) <= 0.02
          and abs(r["bg_shift_last"][0] + 40) <= 6
          and abs(r["bg_shift_last"][1] - 28) <= 6)
    print("   coat h ratio tan %s brown %s (want ~1.00 -- a pan is no recession)"
          % (r["tan_h_ratio"], r["brown_h_ratio"]))
    print("   bg_scale %s (want 1.00) | bg shift %s (want about [-40, 28])"
          % (r["bg_scale_last"], r["bg_shift_last"]))
    print("   %s no false scale from a pure translation, and the shift is read "
          "correctly" % ("PASS" if g3 else "FAIL"))
    ok &= g3

    print("GATE 4  SYNTHETIC EXIT -- guard A painted out from f012 of 25")
    r = analyse("<exit>", "exit", frames=_synth_exit(f0), fit_every=6)
    g4 = (r["both_men_every_frame"] is False
          and r["first_frame_missing_a_man"] == 12
          and len(r["tan_missing_frames"]) == 13
          and not r["brown_missing_frames"])
    print("   both_men_every_frame %s | first missing at %s | tan missing %d "
          "frames | brown missing %d"
          % (r["both_men_every_frame"], r["first_frame_missing_a_man"],
             len(r["tan_missing_frames"]), len(r["brown_missing_frames"])))
    print("   %s D4 is detectable, is not satisfied by scenery, and does not "
          "false-alarm on the man who stayed" % ("PASS" if g4 else "FAIL"))
    ok &= g4

    print("\n%s" % ("ALL GATES PASS -- the instrument may judge."
                    if ok else "!! A GATE FAILED -- this instrument judges nothing."))
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("clip", nargs="?")
    ap.add_argument("label", nargs="?", default="clip")
    ap.add_argument("--gates", action="store_true")
    ap.add_argument("--plate", default="farm-out/ep2-b11-mac-plate-0816/"
                                       "11-they-leave-mac-plate-r3s1.png")
    a = ap.parse_args()
    if a.gates:
        sys.exit(0 if gates(a.plate) else 1)
    if not a.clip:
        sys.exit("give a clip or --gates")
    r = analyse(a.clip, a.label)
    print(json.dumps({k: v for k, v in r.items()
                      if not k.endswith("_series")}, indent=2))
