#!/usr/bin/env python3
"""Score ep2-b19-dropmotion-0819 against the bar its spec pre-registered.

$0, CPU, nothing re-rendered. Reads the mp4, writes no clip.

WHAT THIS MEASURES AND WHAT IT DOES NOT. It measures the FRUIT'S PATH -- the
only clauses on beat 19's bar that a number can settle, because the fruit is a
compact, uniquely-coloured, rigid object with a pre-registered start position.
It does NOT decide whether the take is good, whether he stays himself (M4),
whether the plant keeps two leaves (M6's leaf half) or whether the notice reads
(M8): those are read on the frames. The numbers choose which frames to open.

THE ONE TRAP THIS BEAT HAS, and it is why the tracker follows a TRACK instead of
re-detecting each frame: HIS CLOAK IS ALSO VIOLET, and so is its shadow on the
grass. On 2026-08-19 this lane published a hue figure that was 39% cloak-shadow
pixels and had to retract it. So the fruit is located once at f000 from the
spec's pre-registered bbox, and thereafter followed to the NEAREST compact
violet component -- and every frame where the track is ambiguous or lost is
reported rather than smoothed over, because a lost track IS the 08-12
detached-float fault showing up.

All coordinates are the 704x1280 output frame.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

CLIP = sys.argv[1]
FRAMEDIR = Path(sys.argv[2])

# ---- PRE-REGISTERED, copied from pipeline/jobs/ep2-b19-dropmotion-0819.yaml --
FRUIT_F000 = (610, 642, 903, 946)          # x0, x1, y0, y1
Z_BODY = (0, 500, 285, 1015)               # x0, x1, y0, y1 -- M3, disqualifying
GRASS_Y = 978
M2_BOTTOM_MIN = 965
M2_DESCENT_MIN = 20
M2_REST_TOL = 3
M2_REST_FRAMES = 12
M1_JITTER = 2
M1_JUMP_MAX = 12
M7_PAIR_CAP = 90                            # of 120 pairs under 0.5
M7_RUN_MIN = 8                              # consecutive pairs above 0.5
HORIZON = (360, 430)                        # y band for the camera-lock check

FRAMEDIR.mkdir(parents=True, exist_ok=True)
if not list(FRAMEDIR.glob("f*.png")):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", CLIP,
                    str(FRAMEDIR / "f%04d.png")], check=True)
frames = sorted(FRAMEDIR.glob("f*.png"))
print("frames: %d" % len(frames))


def hsv(arr):
    a = arr.astype(np.float32) / 255.0
    mx = a.max(2)
    mn = a.min(2)
    d = mx - mn
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    h = np.zeros_like(mx)
    m = (d > 1e-6)
    idx = m & (mx == r)
    h[idx] = ((g - b)[idx] / d[idx]) % 6
    idx = m & (mx == g)
    h[idx] = ((b - r)[idx] / d[idx]) + 2
    idx = m & (mx == b)
    h[idx] = ((r - g)[idx] / d[idx]) + 4
    h = h * 60.0
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def components(mask):
    """Label 4-connected components with a scanline union-find. No scipy."""
    H, W = mask.shape
    lab = np.zeros((H, W), np.int32)
    parent = [0]

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    nxt = 1
    for y in range(H):
        row = mask[y]
        for x in np.nonzero(row)[0]:
            up = lab[y - 1, x] if y else 0
            lf = lab[y, x - 1] if x else 0
            if up and lf:
                lab[y, x] = min(up, lf)
                union(up, lf)
            elif up or lf:
                lab[y, x] = up or lf
            else:
                lab[y, x] = nxt
                parent.append(nxt)
                nxt += 1
    out = {}
    for y in range(H):
        for x in np.nonzero(lab[y])[0]:
            r = find(lab[y, x])
            b = out.setdefault(r, [x, x, y, y, 0])
            b[0] = min(b[0], x); b[1] = max(b[1], x)
            b[2] = min(b[2], y); b[3] = max(b[3], y)
            b[4] += 1
    return list(out.values())


def fruit_candidates(arr):
    h, s, v = hsv(arr)
    m = (h >= 252) & (h <= 308) & (s > 0.28) & (v > 0.15) & (v < 0.78)
    comps = components(m)
    out = []
    for c in comps:
        x0, x1, y0, y1, n = c
        w, hh = x1 - x0 + 1, y1 - y0 + 1
        if n < 350 or n > 4000:
            continue
        ar = w / float(hh)
        if not (0.45 <= ar <= 2.2):
            continue
        fill = n / float(w * hh)
        if fill < 0.55:                     # a blob, not a smear or a stroke
            continue
        out.append({"x0": int(x0), "x1": int(x1), "y0": int(y0), "y1": int(y1), "n": int(n),
                    "cx": (x0 + x1) / 2.0, "cy": (y0 + y1) / 2.0})
    return out


track = []
prev = None
grays = []
for i, f in enumerate(frames):
    im = Image.open(f).convert("RGB")
    arr = np.asarray(im)
    grays.append(np.asarray(im.convert("L"), dtype=np.int16))
    cands = fruit_candidates(arr)
    if i == 0:
        tx = (FRUIT_F000[0] + FRUIT_F000[1]) / 2.0
        ty = (FRUIT_F000[2] + FRUIT_F000[3]) / 2.0
    else:
        tx, ty = prev["cx"], prev["cy"]
    if not cands:
        track.append({"f": i, "lost": True, "n_cands": 0})
        continue
    best = min(cands, key=lambda c: (c["cx"] - tx) ** 2 + (c["cy"] - ty) ** 2)
    best["f"] = i
    best["lost"] = False
    best["n_cands"] = len(cands)
    best["jump"] = 0.0 if prev is None else float(
        ((best["cx"] - prev["cx"]) ** 2 + (best["cy"] - prev["cy"]) ** 2) ** 0.5)
    track.append(best)
    prev = best

live = [t for t in track if not t.get("lost")]
lost = [t["f"] for t in track if t.get("lost")]

# ---- M1 -------------------------------------------------------------------
cys = [t["cy"] for t in live]
back = [(live[i]["f"], live[i]["cy"] - live[i - 1]["cy"])
        for i in range(1, len(live)) if live[i]["cy"] - live[i - 1]["cy"] < -M1_JITTER]
jumps = [(t["f"], round(t["jump"], 1)) for t in live if t.get("jump", 0) > M1_JUMP_MAX]

# ---- M2 -------------------------------------------------------------------
descent = (max(cys) - cys[0]) if cys else 0.0
bottom_max = max(t["y1"] for t in live) if live else 0
tail = [t["cy"] for t in live[-M2_REST_FRAMES:]]
rest_span = (max(tail) - min(tail)) if tail else 999

# ---- M3 -- DISQUALIFYING --------------------------------------------------
bx0, bx1, by0, by1 = Z_BODY
contact = [t["f"] for t in live
           if not (t["x1"] < bx0 or t["x0"] > bx1 or t["y1"] < by0 or t["y0"] > by1)]

# ---- M5 -------------------------------------------------------------------
y0, y1 = HORIZON
ref = grays[0][y0:y1, :]
shifts = []
for g in grays[1:]:
    band = g[y0:y1, :]
    best = None
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            a = np.roll(np.roll(band, dy, 0), dx, 1)[6:-6, 8:-8]
            b = ref[6:-6, 8:-8]
            sad = float(np.abs(a - b).mean())
            if best is None or sad < best[0]:
                best = (sad, dx, dy)
    shifts.append((best[1], best[2]))
max_dx = max(abs(s[0]) for s in shifts) if shifts else 0
max_dy = max(abs(s[1]) for s in shifts) if shifts else 0

# ---- M7 -------------------------------------------------------------------
inter = [float(np.abs(grays[i] - grays[i - 1]).mean()) for i in range(1, len(grays))]
under = sum(1 for v in inter if v < 0.5)
run = best_run = 0
for v in inter:
    run = run + 1 if v >= 0.5 else 0
    best_run = max(best_run, run)

res = {
    "frames": len(frames),
    "track_lost_frames": [int(v) for v in lost],
    "multi_candidate_frames": [int(t["f"]) for t in live if t["n_cands"] > 1],
    "M1_backward_steps": [[int(a), round(float(b), 1)] for a, b in back[:12]],
    "M1_jumps_over_%dpx" % M1_JUMP_MAX: jumps[:12],
    "M1_fruit_present_all_frames": not lost,
    "M2_centroid_descent_px": round(descent, 1),
    "M2_descent_required": M2_DESCENT_MIN,
    "M2_bottom_edge_max_y": int(bottom_max),
    "M2_bottom_required": M2_BOTTOM_MIN,
    "M2_rest_span_last_%d_frames" % M2_REST_FRAMES: round(rest_span, 1),
    "M2_rest_tol": M2_REST_TOL,
    "M3_contact_frames": [int(v) for v in contact],
    "M3_min_gap_to_body_zone_px": int(min(t["x0"] for t in live) - bx1) if live else None,
    "M5_max_horizon_shift_px": [max_dx, max_dy],
    "M7_pairs_under_0.5": under,
    "M7_pairs_total": len(inter),
    "M7_cap": M7_PAIR_CAP,
    "M7_longest_run_over_0.5": best_run,
    "M7_run_required": M7_RUN_MIN,
    "interframe_median": round(float(np.median(inter)), 3) if inter else None,
    "interframe_max": round(max(inter), 3) if inter else None,
    "fruit_f000_bbox_measured": [int(live[0]["x0"]), int(live[0]["x1"]), int(live[0]["y0"]), int(live[0]["y1"])] if live else None,
    "fruit_f000_bbox_preregistered": list(FRUIT_F000),
}
res["VERDICT_M1"] = "PASS" if (not lost and not back and not jumps) else "FAIL"
res["VERDICT_M2"] = "PASS" if (descent >= M2_DESCENT_MIN and bottom_max >= M2_BOTTOM_MIN
                               and rest_span <= M2_REST_TOL) else "FAIL"
res["VERDICT_M3"] = "PASS" if not contact else "FAIL-DISQUALIFYING"
res["VERDICT_M5"] = "PASS" if (max_dx <= 1 and max_dy <= 1) else "FAIL"
res["VERDICT_M7"] = "PASS" if (under <= M7_PAIR_CAP and best_run >= M7_RUN_MIN) else "FAIL"
print(json.dumps(res, indent=2))
with open(FRAMEDIR / "b19-track.json", "w") as fh:
    json.dump({"summary": res, "track": track}, fh, indent=1)
