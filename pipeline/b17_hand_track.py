#!/usr/bin/env python3
"""b17 bigbody reseed -- THE instrument. Validated against b0911318's published
numbers before it is pointed at any reseed, and applied IDENTICALLY to the
winner and to all four reseeds so that "reproduces" means "scores like the
winner scored under the same tool".

THE MEASURE. A brightness+yellowness skin rule inside a fixed TORSO-INTERIOR
window, then scipy connected components, then the two largest blobs tracked by
identity (nearest centroid to the previous frame) rather than by a fixed
left/right split. THE SPLIT IS WHY v1 OF THIS FILE FAILED ITS OWN VALIDATION:
the travelling arm crosses the midline, so a fixed split stops measuring "the
two hands" and starts measuring "the two halves of one arm", which corrupted
both the travel figure AND the other-hand control (it reported the stationary
hand as moving 96 px). That failure is left recorded here rather than tidied
away -- it is exactly the class of error the retired measures were retired for.

WHY THE WINDOW IS THE INSTRUMENT, measured on the real plate:
    LEFT hand   R225 G224 B152   G-R  -1.5
    RIGHT hand  R210 G215 B142   G-R  +4.9
    HEAD/skull  R241 G243 B179   G-R  +2.0   <- inside the hand's range
    grass bg    R221 G207 B145   G-B  +62    <- inside the hand's range
Colour alone separates the hand from NEITHER the bald head NOR the background.
`G > R + 10` matches zero hand pixels; a bright-yellowish rule matches hand,
head and grass alike. Inside the torso interior -- below the chin, above the
shoes, inboard of the silhouette -- the hands are the only bright yellowish
thing, and the cloak (R45 G44 B47) and trousers (R0 G0 B1) are five times too
dark to qualify. The head can never enter the mask because the window's top
edge sits below the chin, so the F7 discrimination is STRUCTURAL, not a
threshold that could drift.

THE BLOB IS ARM+HAND, NOT THE HAND ALONE, and that is stated rather than
glossed: the forearm is contiguous with the hand and the same colour. This
makes the centroid travel figure CONSERVATIVE -- the forearm's proximal end
barely moves, so it drags the centroid down. It understates, never overstates,
and it understates the winner and the reseeds by the same construction.

SELF-CHECK, and the rule about it. The two arms are tracked by identity; a
frame is FLAGGED when fewer than two blobs survive MIN_AREA (the arms have
merged) or when a tracked blob jumps more than JUMP_MAX px in a single frame
(identity has plausibly swapped to a different object). A tracker that keeps
emitting numbers after it has lost the thing it is tracking is the defect that
retired the NCC tracker at f024.

DISCLOSED: THE ASSOCIATION STEP WAS HARDENED AFTER SEEING SEED 20260912.
The earlier version demanded EXACTLY two blobs and stopped otherwise; 20260912
invents pale dust clouds that enter the skin rule, so it stopped after six
frames on a clip whose hands never move. The fix ignores extra blobs and keeps
the two nearest the previous positions. The mask, window, thresholds, MIN_AREA,
HAND_W (180) and the 1.0 bar were NOT touched, and the hardened version was
re-validated against the winner's published numbers and both synthetic controls
before any clip was judged with it. See `validate` in reseed_report.py.

NOT COMPUTED AND NOT QUOTED: depth (retired AND inverted -- full stand-up
0.290, zero-motion 0.516, bird-only 0.376) and the old cadence metric (odd hold
periods alias to exactly 1.00x).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

WIN_Y0, WIN_Y1 = 470, 1060      # below the chin, above the shoes
WIN_X0, WIN_X1 = 100, 620       # inboard of the grass margins
BRIGHT = 150                    # mean(R,G); hands 210-225, cloak 44, trousers 0
YELLOW = 35                     # G-B; hands +72, cloak -2
MIN_AREA = 2000                 # arms are ~20000 px; specks are <1000
JUMP_MAX = 150                  # one-frame blob jump above this = identity swap

# One hand-width on the init plate, as measured by the winning lane and quoted
# in b0911318. Held FIXED across all five clips so the bar cannot drift.
HAND_W = 180.0
BAR = 1.0                       # M2: one hand-width, relative to the cloth

# Landmarks for the camera / cloth check, as (name, y, x, half-size).
# Deliberately NOT on flat black: the tight-insert lane's cloth patches sat on
# low-texture fabric and scored NCC 0.25-0.51, which is why its M2 conclusion
# had to lean on visible drift instead. These sit on the shoe rim, the lit
# cloak fold edge and the background grass, all of which have real structure.
LANDMARKS = [("SHOE_L", 1150, 250, 34),
             ("SHOE_R", 1150, 470, 34),
             ("CLOAK_EDGE", 600, 150, 34),
             ("GRASS_TL", 250, 60, 34)]
SEARCH = 26                     # +/- px search radius for the landmark match
NCC_MIN = 0.70                  # below this the landmark has lost its patch


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


def skin_mask(frame):
    m = np.zeros(frame.shape[:2], dtype=bool)
    sub = frame[WIN_Y0:WIN_Y1, WIN_X0:WIN_X1]
    bright = (sub[..., 0].astype(np.int32) + sub[..., 1]) / 2.0 > BRIGHT
    yellow = (sub[..., 1] - sub[..., 2]) > YELLOW
    m[WIN_Y0:WIN_Y1, WIN_X0:WIN_X1] = bright & yellow
    return m


def blobs(mask):
    lab, n = ndimage.label(mask)
    if n == 0:
        return []
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    out = []
    for i, s in enumerate(sizes, start=1):
        if s >= MIN_AREA:
            cy, cx = ndimage.center_of_mass(mask, lab, i)
            top = int(np.nonzero(lab == i)[0].min())
            out.append({"area": int(s), "cx": float(cx), "cy": float(cy),
                        "top": top})
    out.sort(key=lambda b: b["cx"])
    return out


def ncc_track(frames, name, y, x, half):
    """Normalised cross-correlation of a fixed patch, with a self-check. A
    landmark whose best score falls under NCC_MIN has lost its patch and its
    numbers are not quoted from that frame on."""
    ref = frames[0][y - half:y + half, x - half:x + half].astype(np.float64)
    ref = ref - ref.mean()
    rn = np.sqrt((ref ** 2).sum()) or 1.0
    out = []
    for f in frames:
        best, bxy = -2.0, (0, 0)
        for dy in range(-SEARCH, SEARCH + 1, 2):
            for dx in range(-SEARCH, SEARCH + 1, 2):
                p = f[y + dy - half:y + dy + half,
                      x + dx - half:x + dx + half].astype(np.float64)
                if p.shape != ref.shape:
                    continue
                p = p - p.mean()
                d = np.sqrt((p ** 2).sum()) or 1.0
                v = float((ref * p).sum() / (rn * d))
                if v > best:
                    best, bxy = v, (dy, dx)
        out.append({"n": best, "dy": bxy[0], "dx": bxy[1]})
    return out


def analyse(clip, label):
    frames, w, h = frames_rgb(clip)
    nf = len(frames)
    per = []
    ref = blobs(skin_mask(frames[0]))
    if len(ref) != 2:
        return {"label": label, "clip": str(clip), "frames": nf,
                "fatal": "f000 does not show two arm blobs (got %d)" % len(ref)}
    tracks = [[dict(b)] for b in ref]
    selfcheck_failed_at = None
    # ---------------------------------------------------------------------
    # HARDENED ASSOCIATION -- AND THIS CHANGE WAS MADE AFTER SEEING SEED
    # 20260912, WHICH IS DISCLOSED RATHER THAN BURIED.
    #
    # v2 of this loop required EXACTLY two blobs and gave up otherwise. On
    # seed 20260912 the engine invents pale cream dust clouds over the legs;
    # they are bright and yellowish enough to enter the skin rule, so from
    # f006 there were THREE blobs and measurement stopped after six frames --
    # on a clip whose hands never move at all. Stopping early on a frozen clip
    # is not a conservative failure, it is no measurement.
    #
    # WHAT CHANGED: instead of demanding exactly two blobs, take the two whose
    # centroids are NEAREST the previous frame's two positions. Extra blobs
    # (dust, debris) are ignored; the two arms are still tracked by identity.
    # WHAT DID NOT CHANGE: the mask, the window, the thresholds, MIN_AREA,
    # HAND_W (180) or the 1.0 bar. This makes MORE of each clip measurable; it
    # cannot turn a stationary hand into a travelling one, because it still
    # measures displacement of a tracked blob from its own f000 position.
    #
    # A REAL SELF-CHECK REPLACES THE OLD ONE, so "measurable" never means
    # "unfalsifiable": if a chosen blob JUMPS more than JUMP_MAX px in one
    # frame, identity has plausibly swapped to a different object and the
    # frame is flagged. Numbers past the first flag are reported separately
    # and never folded into the headline figure.
    # ---------------------------------------------------------------------
    for i in range(1, nf):
        bs = blobs(skin_mask(frames[i]))
        prev = [next(x for x in reversed(t) if x) for t in tracks]
        if len(bs) < 2:
            if selfcheck_failed_at is None:
                selfcheck_failed_at = i
            tracks[0].append(None)
            tracks[1].append(None)
            continue
        chosen, used = [], set()
        for p in prev:
            best, bi = None, None
            for k, b in enumerate(bs):
                if k in used:
                    continue
                d = np.hypot(b["cx"] - p["cx"], b["cy"] - p["cy"])
                if best is None or d < best:
                    best, bi = d, k
            used.add(bi)
            chosen.append((bs[bi], best))
        if any(d > JUMP_MAX for _, d in chosen) and selfcheck_failed_at is None:
            selfcheck_failed_at = i
        tracks[0].append(chosen[0][0])
        tracks[1].append(chosen[1][0])

    def disp(t, i):
        if t[i] is None:
            return None
        return float(np.hypot(t[i]["cx"] - t[0]["cx"], t[i]["cy"] - t[0]["cy"]))

    last = nf
    d0 = [v for v in (disp(tracks[0], i) for i in range(last)) if v is not None]
    d1 = [v for v in (disp(tracks[1], i) for i in range(last)) if v is not None]
    peak0, peak1 = max(d0), max(d1)
    trav, ctrl = (0, 1) if peak0 >= peak1 else (1, 0)
    dt, dc = (d0, d1) if trav == 0 else (d1, d0)
    pk = int(np.argmax(dt))

    lm = {}
    for name, y, x, half in LANDMARKS:
        r = ncc_track(frames, name, y, x, half)
        good = [k for k, v in enumerate(r) if v["n"] >= NCC_MIN]
        lm[name] = {"quotable_to": (max(good) if good else -1),
                    "max_shift": max((abs(v["dy"]) + abs(v["dx"]))
                                     for v in r[:max(good) + 1]) if good else None,
                    "n_at_0": round(r[0]["n"], 2),
                    "worst_n": round(min(v["n"] for v in r), 2)}

    return {
        "label": label, "clip": str(clip), "frames": nf,
        "selfcheck_failed_at": selfcheck_failed_at,
        "quotable_frames": last,
        "travelling_hand": "left" if trav == 0 else "right",
        "travel_peak_px": round(dt[pk], 1),
        "travel_peak_frame": pk,
        "travel_peak_handwidths": round(dt[pk] / HAND_W, 2),
        "travel_at_f030": None if len(dt) <= 30 else round(dt[30], 1),
        "control_other_hand_peak_px": round(max(dc), 1),
        "control_other_hand_peak_frame": int(np.argmax(dc)),
        "control_to_f040_px": round(max(dc[:min(41, len(dc))]), 1),
        "start_left": (round(tracks[0][0]["cx"]), round(tracks[0][0]["cy"])),
        "start_right": (round(tracks[1][0]["cx"]), round(tracks[1][0]["cy"])),
        "travel_curve": [None if v is None else round(v) for v in dt],
        "control_curve": [None if v is None else round(v) for v in dc],
        "landmarks": lm,
    }


def overlays(clip, out_dir, stem, which=(0, 12, 24, 36, 48, 60, 72, 84, 96)):
    frames, w, h = frames_rgb(clip)
    tiles = []
    for i in which:
        if i >= len(frames):
            continue
        img = frames[i].astype(np.uint8).copy()
        m = skin_mask(frames[i])
        img[m] = (255, 0, 255)
        tiles.append((i, Image.fromarray(img)))
    s = 0.33
    tw, th = int(w * s), int(h * s)
    sheet = Image.new("RGB", (tw * len(tiles), th), "black")
    for k, (i, im) in enumerate(tiles):
        sheet.paste(im.resize((tw, th)), (tw * k, 0))
    p = Path(out_dir) / ("OVL-%s.png" % stem)
    sheet.save(p)
    return p


if __name__ == "__main__":
    res = analyse(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "clip")
    print(json.dumps({k: v for k, v in res.items()
                      if k not in ("travel_curve", "control_curve")}, indent=2))
