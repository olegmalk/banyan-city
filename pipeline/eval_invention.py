#!/usr/bin/env python3
"""Score check_invention.py's candidate metrics against the labelled set.

    python3 pipeline/eval_invention.py                      # measure + evaluate
    python3 pipeline/eval_invention.py --cache <file.json>  # re-evaluate, no ffmpeg
    python3 pipeline/eval_invention.py --stats-only         # arithmetic self-check

WHY THIS FILE EXISTS. On 2026-08-09 the beat-16 drift experiment produced eight
clips whose labels are known by construction, and check_invention.py — the tool
built to catch a video model inventing content — passed all three of the clips
with a full anime human in them. Before that the tool had no labelled data at
all. This harness is where any future claim about its accuracy has to be made,
because it is the only place the claim can be checked.

THE CANDIDATE LIST BELOW WAS WRITTEN BEFORE ANY OF IT WAS RUN, and that ordering
is the point. With three positives and six negatives the set is small enough that
SOMETHING will separate it if you keep trying metrics, so the number of metrics
tried has to be counted honestly and paid for. Every metric in CANDIDATES is
scored and reported whether it wins or loses; none may be deleted after the fact
to shrink the correction. If a later session adds one, it adds to K and the
family-wise p in the report goes UP.

    K metrics tried, and the arithmetic that makes this set nearly unwinnable:
    with 3 positives among 9 clips there are C(9,3) = 84 labelings, so a metric
    that separates the set PERFECTLY earns an exact two-sided p of 2/84 = 0.024
    at best. Try thirteen metrics and the family-wise bound is 13 x 0.024 = 0.31.
    A perfect separator on nine clips is therefore NOT evidence, and no amount of
    cross-validation changes that: leave-one-out re-uses the same nine labels and
    corrects for overfitting a THRESHOLD, never for having chosen the metric
    after looking. The honest exit is to report the leader as a lead and say what
    n would settle it (see `sample_size_needed`).

WHAT COUNTS AS OUT-OF-SAMPLE. The eight drift clips were all visible when
ledger record 38 pre-registered its moving-pair-fraction lead, so for that metric
they are in-sample by the record's own admission ("the 1.0 threshold was chosen
after seeing the numbers"). The beat-12 clip rendered later that night is the one
point that came after, and it is scored separately as `out_of_sample`.
"""

import argparse
import hashlib
import json
import math
import sys
from itertools import combinations
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "pipeline" / "invention-labelled-set.yaml"
# The measured numbers, committed. The clips themselves are untracked by gate G5,
# so without this file a fresh checkout can read the labels and reproduce nothing.
MEASURED = REPO / "pipeline" / "invention-labelled-set.measured.json"

# Sampling for the new locality metrics. Coarser than a frame and finer than the
# whole picture, which is the resolution the question lives at: an invented
# character is a few blocks wide and the swaying leaf that hides it is not.
EW, EH = 88, 160       # block-poolable from 704x1280 exactly (8x8 pooling)
EFPS = 8               # same temporal sampling as check_invention
GRID = 8               # 8x8 grid of blocks over the frame
TOP_BLOCKS = 8         # rank blocks by how much they changed; keep the busiest 8

# ---------------------------------------------------------------------------
# THE CANDIDATE LIST. Declared before the first run. K = len(CANDIDATES).
# `hi_is_positive` says which direction the metric is expected to point BEFORE
# the numbers exist — a metric that separates the set the wrong way round has not
# been vindicated, it has been contradicted, and the report says so.
# ---------------------------------------------------------------------------
CANDIDATES = [
    # --- the six check_invention already computes (the incumbent) -------------
    ("return_ratio", True, "ends at its furthest point from frame 0"),
    ("monotonic", True, "share of steps where distance from frame 0 rises"),
    ("peak", True, "furthest the composition ever gets from frame 0"),
    ("churn", True, "frame-to-frame shape change relative to total excursion"),
    ("area_ratio", True, "dark foreground mass, last frame over first"),
    ("spread_ratio", True, "spatial spread of that mass, last over first"),
    # --- ledger record 38's pre-registered lead ------------------------------
    ("pair_moving_frac", True, "fraction of consecutive full-res pairs moving >1.0/255"),
    ("pair_motion_mean", True, "mean |delta| between consecutive full-res frames"),
    ("pair_motion_median", True, "median |delta| between consecutive full-res frames"),
    # --- clause (b): the inverted conjunct is GLOBAL; test it LOCALLY ---------
    # monotonic averages the whole frame, so a leaf that never stops swaying
    # drowns a man who arrives in one corner and stays. The same statistic
    # computed per block and maximised over the busiest blocks does not average
    # him away. This is the one hypothesis here with a mechanism behind it rather
    # than a shape.
    ("local_mono_max", True, "highest per-block monotonic among the busiest blocks"),
    ("local_oneway_max", True, "highest per-block return_ratio x monotonic, busiest blocks"),
    # --- clause (c): a character is not darker than the sky, it is DENSER ----
    # fg() masks pixels darker than typical. An anime human in mid-tone linework
    # is not darker than a peach sky; he is a knot of ink. Mask on edge density
    # instead and ask the same two questions.
    ("edgefg_area_ratio", True, "linework-dense area, last frame over first"),
    ("edgefg_spread_ratio", True, "spread of linework-dense mass, last over first"),
    # --- persistence: an arrival shifts the time-average, a sway does not -----
    ("persistent_shift", True, "late-window mean vs early-window mean, over temporal noise"),
    ("shift_blob_frac", True, "largest connected component of the shifted region"),
]
K = len(CANDIDATES)


# ---------------------------------------------------------------------------
# statistics — pure python on purpose, so CI (which installs pyyaml and pillow
# and no numpy) can import this module and test the arithmetic.
# ---------------------------------------------------------------------------
def auc(pos, neg):
    """P(a random positive scores above a random negative), ties worth half."""
    if not pos or not neg:
        return float("nan")
    wins = sum((1.0 if p > n else 0.5 if p == n else 0.0) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def exact_p(pos, neg, two_sided=True):
    """Exact permutation p on AUC: enumerate every way the labels could fall.

    n is nine. There are 84 labelings and we walk all of them, so this is the
    true null distribution rather than a normal approximation of it — which
    matters exactly here, where the smallest attainable p is a headline number.
    """
    vals = list(pos) + list(neg)
    k, n = len(pos), len(vals)
    if k == 0 or k == n:
        return float("nan")
    obs = auc(pos, neg)
    hits = total = 0
    for idx in combinations(range(n), k):
        s = set(idx)
        a = auc([vals[i] for i in idx], [vals[i] for i in range(n) if i not in s])
        total += 1
        if two_sided:
            if abs(a - 0.5) >= abs(obs - 0.5) - 1e-12:
                hits += 1
        elif a >= obs - 1e-12:
            hits += 1
    return hits / total


def separation(pos, neg, hi_is_positive=True):
    """(perfect?, gap, margin). gap is in the metric's own units; margin scales
    it by the full spread so two metrics can be compared."""
    if not pos or not neg:
        return (False, 0.0, 0.0)
    if hi_is_positive:
        gap = min(pos) - max(neg)
    else:
        gap = min(neg) - max(pos)
    spread = max(pos + neg) - min(pos + neg)
    return (gap > 0, gap, (gap / spread) if spread > 1e-12 else 0.0)


def loo_threshold_accuracy(values, labels, hi_is_positive=True):
    """Leave-one-out over a midpoint-threshold rule.

    HONEST LIMITS, because this number reads more impressive than it is. LOO
    corrects for fitting a THRESHOLD to the data; it cannot correct for having
    picked the metric after seeing which one separated, and every fold shares
    eight of nine labels with every other, so the folds are not independent and
    9/9 here is nothing like 9 independent successes.
    """
    n, correct, errors = len(values), 0, []
    for i in range(n):
        tr_v = [values[j] for j in range(n) if j != i]
        tr_l = [labels[j] for j in range(n) if j != i]
        pos = [v for v, l in zip(tr_v, tr_l) if l]
        neg = [v for v, l in zip(tr_v, tr_l) if not l]
        if not pos or not neg:
            errors.append((i, "degenerate fold"))
            continue
        thr = (min(pos) + max(neg)) / 2 if hi_is_positive else (max(pos) + min(neg)) / 2
        pred = (values[i] > thr) if hi_is_positive else (values[i] < thr)
        if pred == labels[i]:
            correct += 1
        else:
            errors.append((i, f"{values[i]:.4f} vs thr {thr:.4f}"))
    return correct, n, errors


def sample_size_needed(k_metrics, alpha=0.05, pos_frac=0.4, max_n=200):
    """Smallest labelled n at which a PERFECT separator would survive Bonferroni.

    Answers the only actionable question a null result leaves: how many more
    clips. Returns (n, positives) or None.
    """
    for n in range(4, max_n + 1):
        p = max(1, min(n - 1, round(n * pos_frac)))
        best = 2.0 / math.comb(n, p)          # two-sided, perfect separation
        if best * k_metrics < alpha:
            return (n, p)
    return None


# ---------------------------------------------------------------------------
# measurement — numpy is imported lazily so the arithmetic above stays testable
# on a box that has no numpy (CI installs pyyaml, pillow, markdown and nothing
# else, and check_invention.py has always been Mac-side for the same reason).
# ---------------------------------------------------------------------------
def _probe(clip):
    import subprocess
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(clip)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {clip.name}: {r.stderr[:200]}")
    w, h = r.stdout.strip().split(",")[0].split("x")[:2]
    return int(w), int(h)


def pair_motion(clip):
    """Per-pair mean |delta| on FULL-RESOLUTION 8-bit luma, 0-255.

    Full res on purpose: this reproduces ledger record 38's definition exactly
    ("mean |delta| between CONSECUTIVE frames, full 704x1280, 8-bit Rec.601
    luma, averaged over all 144 pairs"), so the pre-registered lead is tested on
    the numbers it was registered on and not on a downscaled cousin of them.
    Streamed one frame at a time — the whole clip decoded at once is 130 MB.
    """
    import subprocess
    import numpy as np
    w, h = _probe(clip)
    n = w * h
    p = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", str(clip), "-f", "rawvideo",
         "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    prev, deltas = None, []
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        f = np.frombuffer(buf, dtype=np.uint8).astype(np.float32)
        if prev is not None:
            deltas.append(float(np.abs(f - prev).mean()))
        prev = f
    p.stdout.close()
    err = p.stderr.read().decode("utf-8", "replace")
    p.wait()
    if p.returncode != 0 or len(deltas) < 3:
        raise RuntimeError(f"raw decode failed on {clip.name}: {err[:200]}")
    return deltas


def edge_stack(clip):
    """(n, EH, EW) contrast-normalised gradient magnitude at EFPS."""
    import subprocess
    import tempfile
    import numpy as np
    from PIL import Image
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_invention as ci
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(clip),
             "-vf", f"fps={EFPS},scale={EW}:{EH},format=gray", f"{td}/f%04d.png"],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg failed on {clip.name}: {r.stderr[:200]}")
        fs = sorted(Path(td).glob("f*.png"))
        if len(fs) < 4:
            raise RuntimeError(f"{clip.name}: only {len(fs)} frames sampled")
        norm = []
        for q in fs:
            a = np.asarray(Image.open(q), dtype=np.float32)
            s = a.std()
            norm.append((a - a.mean()) / (s if s > 1e-6 else 1.0))
        fr = np.stack(norm)
        return fr, np.stack([ci.edges(f) for f in fr])


def _largest_component(mask):
    """Size of the largest 4-connected component of a boolean mask.

    Hand-rolled rather than scipy.ndimage: CI installs three packages and none of
    them is scipy, and a flood fill over a few hundred pixels is not worth a
    dependency that would make this module unimportable there.
    """
    import numpy as np
    seen = np.zeros_like(mask, dtype=bool)
    best = 0
    ys, xs = np.nonzero(mask)
    H, W = mask.shape
    for sy, sx in zip(ys, xs):
        if seen[sy, sx]:
            continue
        stack, size = [(sy, sx)], 0
        seen[sy, sx] = True
        while stack:
            y, x = stack.pop()
            size += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        best = max(best, size)
    return best


def locality_metrics(fr, em):
    """The metrics invented for clauses (b) and (c) of the backlog entry."""
    import numpy as np
    n, H, W = em.shape
    e0 = em[0]

    # --- per-block drift: the same shape test check_invention runs globally ---
    bh, bw = H // GRID, W // GRID
    rows = []
    for by in range(GRID):
        for bx in range(GRID):
            blk = em[:, by * bh:(by + 1) * bh, bx * bw:(bx + 1) * bw]
            b0 = e0[by * bh:(by + 1) * bh, bx * bw:(bx + 1) * bw]
            d = np.array([float(np.abs(b - b0).mean()) for b in blk])
            pk = float(d.max())
            if pk < 1e-9:
                continue
            rows.append((pk,
                         float(np.sum(np.diff(d) > 0)) / max(1, len(d) - 1),
                         float(d[-1] / pk)))
    rows.sort(key=lambda r: -r[0])
    busy = rows[:TOP_BLOCKS] or rows
    local_mono_max = max((r[1] for r in busy), default=0.0)
    local_oneway_max = max((r[1] * r[2] for r in busy), default=0.0)

    # --- linework-dense foreground instead of dark foreground ----------------
    def dense(e):
        return e > 1.0

    def spread(m):
        ys, xs = np.nonzero(m)
        if len(xs) < 8:
            return 0.0
        return float(math.hypot(xs.std(), ys.std()))

    d0, dL = dense(em[0]), dense(em[-1])
    a0, aL = int(d0.sum()), int(dL.sum())
    edgefg_area = (aL / a0) if a0 > 40 else 1.0
    s0 = spread(d0)
    edgefg_spread = (spread(dL) / s0) if s0 > 1e-6 else 1.0

    # --- persistence: does the time-average move, or does it come back? ------
    q = max(1, n // 4)
    early, late = em[:q].mean(axis=0), em[-q:].mean(axis=0)
    shift = np.abs(late - early)
    noise = float(em.std(axis=0).mean())
    persistent_shift = float(shift.mean() / (noise if noise > 1e-6 else 1.0))

    thr = float(np.percentile(shift, 95.0))
    mask = shift >= thr
    tot = int(mask.sum())
    blob = (_largest_component(mask) / tot) if tot > 0 else 0.0

    return {
        "local_mono_max": local_mono_max,
        "local_oneway_max": local_oneway_max,
        "edgefg_area_ratio": edgefg_area,
        "edgefg_spread_ratio": edgefg_spread,
        "persistent_shift": persistent_shift,
        "shift_blob_frac": float(blob),
    }


def measure_clip(path):
    """Every candidate metric for one clip, incumbents included and unchanged."""
    import numpy as np  # noqa: F401 — imported here so the module loads without it
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_invention as ci
    m = dict(ci.measure(ci.frames(path)))     # the incumbent six, verbatim
    deltas = pair_motion(path)
    arr = sorted(deltas)
    m["pair_moving_frac"] = sum(1 for d in deltas if d > 1.0) / len(deltas)
    m["pair_motion_mean"] = sum(deltas) / len(deltas)
    m["pair_motion_median"] = arr[len(arr) // 2] if len(arr) % 2 else \
        (arr[len(arr) // 2 - 1] + arr[len(arr) // 2]) / 2
    fr, em = edge_stack(path)
    m.update(locality_metrics(fr, em))
    return {k: float(v) for k, v in m.items()}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
def load_fixture():
    d = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    return d


def evaluate(rows):
    """rows = [{name, label, out_of_sample, metrics{}}] -> report dict."""
    results = []
    for name, hi, blurb in CANDIDATES:
        vals = [r["metrics"].get(name) for r in rows]
        if any(v is None for v in vals):
            continue
        labels = [r["label"] == "invented" for r in rows]
        pos = [v for v, l in zip(vals, labels) if l]
        neg = [v for v, l in zip(vals, labels) if not l]
        a = auc(pos, neg)
        p2 = exact_p(pos, neg, two_sided=True)
        perfect, gap, margin = separation(pos, neg, hi)
        corr, tot, errs = loo_threshold_accuracy(vals, labels, hi)
        # the out-of-sample point: does the in-sample rule put it on the right
        # side when it is not allowed to see it?
        oos = None
        ins = [(v, l) for v, l, r in zip(vals, labels, rows) if not r["out_of_sample"]]
        held = [(v, l) for v, l, r in zip(vals, labels, rows) if r["out_of_sample"]]
        if held and ins:
            ip = [v for v, l in ins if l]
            inn = [v for v, l in ins if not l]
            if ip and inn:
                thr = (min(ip) + max(inn)) / 2 if hi else (max(ip) + min(inn)) / 2
                oos = all(((v > thr) if hi else (v < thr)) == l for v, l in held)
        results.append({
            "metric": name, "blurb": blurb, "hi_is_positive": hi,
            "auc": a, "p_two_sided": p2, "p_bonferroni": min(1.0, p2 * K),
            "perfect": perfect, "gap": gap, "margin": margin,
            "inverted": a < 0.5,
            "loo": [corr, tot], "loo_errors": errs,
            "out_of_sample_ok": oos,
            "pos": pos, "neg": neg,
        })
    results.sort(key=lambda r: (-abs(r["auc"] - 0.5), -r["margin"]))
    return results


def report(rows, results):
    names = [r["name"] for r in rows]
    print(f"\n  LABELLED SET — {len(rows)} clips, "
          f"{sum(1 for r in rows if r['label'] == 'invented')} invented, "
          f"{sum(1 for r in rows if r['label'] != 'invented')} clean\n")

    print(f"  {'metric':<21} {'AUC':>5} {'p2':>7} {'pK':>6} {'sep':>4} "
          f"{'marg':>5} {'LOO':>5} {'oos':>4}")
    for r in results:
        oos = "--" if r["out_of_sample_ok"] is None else ("ok" if r["out_of_sample_ok"] else "MISS")
        print(f"  {r['metric']:<21} {r['auc']:>5.2f} {r['p_two_sided']:>7.4f} "
              f"{r['p_bonferroni']:>6.2f} {'YES' if r['perfect'] else ('inv' if r['inverted'] else '-'):>4} "
              f"{r['margin']:>5.2f} {r['loo'][0]:>2}/{r['loo'][1]:<2} {oos:>4}")

    print(f"\n  per-clip values, leader first (invented marked *):")
    for r in results[:4]:
        print(f"    {r['metric']}")
        for row in rows:
            v = row["metrics"][r["metric"]]
            mark = "*" if row["label"] == "invented" else " "
            oos = "  (out-of-sample)" if row["out_of_sample"] else ""
            print(f"      {mark} {v:>8.4f}  {row['name']}{oos}")

    print(f"\n  K = {K} candidate metrics were tried; every p above is multiplied "
          f"by {K}\n  to give pK. The smallest two-sided p this set can produce is "
          f"{2.0 / math.comb(len(rows), max(1, sum(1 for r in rows if r['label'] == 'invented'))):.4f} "
          f"(perfect separation).")
    need = sample_size_needed(K)
    if need:
        print(f"  A perfect separator would need n = {need[0]} labelled clips "
              f"({need[1]} invented)\n  to clear alpha=0.05 after the same "
              f"correction. We have {len(rows)}.")
    winners = [r for r in results if r["p_bonferroni"] < 0.05]
    print(f"\n  METRICS SURVIVING THE CORRECTION: {len(winners)}"
          f"{' — ' + ', '.join(w['metric'] for w in winners) if winners else ''}")
    return names


def rules_report(rows, extra=None):
    """What the SHIPPED gate does on the labelled set, and what deleting the one
    conjunct we can prove runs backwards would do instead.

    Neither of these is a new metric and neither has a fitted number in it —
    `shipped` calls check_invention.verdict() itself so it cannot drift from the
    tool, and `no_monotonic` is that same rule with one clause struck out. That
    is the only edit this set licenses without fitting: a conjunct measured to
    point the wrong way is not a threshold that needs moving, it is a
    requirement with no evidence under it.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_invention as ci

    def shipped(m):
        return ci.verdict(m)[0]

    def no_monotonic(m):
        return bool(
            (m["return_ratio"] > 0.88 and m["peak"] > 0.18)
            or m["area_ratio"] > 1.30 or m["spread_ratio"] > 1.25)

    print("\n  THE GATE ITSELF, on the labelled set:")
    print(f"    {'rule':<16} {'recall':>8} {'false alarms':>14}")
    for label, fn in (("shipped", shipped), ("no_monotonic", no_monotonic)):
        tp = sum(1 for r in rows if r["label"] == "invented" and fn(r["metrics"]))
        pos = sum(1 for r in rows if r["label"] == "invented")
        fp = sum(1 for r in rows if r["label"] != "invented" and fn(r["metrics"]))
        neg = len(rows) - pos
        print(f"    {label:<16} {tp:>4}/{pos:<3} {fp:>10}/{neg:<3}")
        if extra:
            ef = sum(1 for _, m in extra if fn(m))
            print(f"    {'':<16} {'':>8} {ef:>10}/{len(extra):<3}  "
                  f"(unlabelled portability clips)")


def portability(results, rows, clips):
    """Where do KNOWN-SHIPPED clips fall relative to the labelled bands?

    NOT LABELS AND NOT A TEST SET. These clips have no ground truth: nobody has
    certified them free of invention, and one of them (beat 11's mitosis) is a
    known transformation the tool's docstring says will score like an invention.
    They answer a narrower question that costs nothing to ask and can kill a lead
    outright — IS THE BOUNDARY PORTABLE? Every clip in the labelled set is LTX at
    704x1280 on one plate of one beat. If a metric's invented-band swallows the
    clips of a cut that has already been assembled and praised, then that band is
    measuring the engine and the shot, not the invention, and no amount of extra
    LTX beat-16 seeds will reveal it.
    """
    perfect = [r for r in results if r["perfect"]]
    if not perfect:
        print("\n  no perfectly-separating metric to check for portability")
        return
    print(f"\n  PORTABILITY — {len(clips)} model-rendered clips from another "
          f"episode and engine,\n  unlabelled, against each perfect separator's "
          f"in-sample boundary:")
    for r in perfect:
        lo = max(r["neg"]) if r["hi_is_positive"] else min(r["neg"])
        hi = min(r["pos"]) if r["hi_is_positive"] else max(r["pos"])
        thr = (lo + hi) / 2
        inside = []
        for name, m in clips:
            v = m.get(r["metric"])
            if v is None:
                continue
            if (v > thr) if r["hi_is_positive"] else (v < thr):
                inside.append((name, v))
        print(f"    {r['metric']:<20} clean<={lo:.4f}  boundary {thr:.4f}  "
              f"invented>={hi:.4f}")
        for name, m in clips:
            v = m.get(r["metric"])
            flag = "WOULD FLAG" if any(n == name for n, _ in inside) else "   ok     "
            print(f"      {flag}  {v:>8.4f}  {name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=str(MEASURED),
                    help="measured metrics json (default: the committed record)")
    ap.add_argument("--write-cache", action="store_true",
                    help="persist what was measured; refuses a partial set, so a "
                         "checkout missing clips cannot truncate the record")
    ap.add_argument("--portability", default="",
                    help="dir of unlabelled model-rendered clips; asks whether a "
                         "separating boundary survives another episode and engine")
    ap.add_argument("--stats-only", action="store_true",
                    help="run the arithmetic on a synthetic set; no clips, no ffmpeg")
    a = ap.parse_args()

    if a.stats_only:
        pos, neg = [0.9, 0.8, 0.7], [0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
        print(f"  perfect separator: AUC {auc(pos, neg):.2f}, "
              f"exact two-sided p {exact_p(pos, neg):.4f}, "
              f"x{K} = {min(1.0, exact_p(pos, neg) * K):.3f}")
        print(f"  n needed for a perfect separator at K={K}: {sample_size_needed(K)}")
        return 0

    fx = load_fixture()
    cache = Path(a.cache) if a.cache else None
    have = {}
    if cache and cache.exists():
        have = {r["name"]: r for r in json.loads(cache.read_text(encoding="utf-8"))["clips"]}

    rows, missing = [], []
    for c in fx["clips"]:
        p = REPO / c["path"]
        name = Path(c["path"]).name
        row = {"name": name, "path": c["path"], "label": c["label"],
               "out_of_sample": "held_out_from" in c}
        if name in have and have[name].get("sha256") == c["sha256"]:
            row["metrics"] = have[name]["metrics"]
            row["sha256"] = c["sha256"]
        elif p.exists():
            got = sha256(p)
            if got != c["sha256"]:
                # A changed file is not the labelled clip. Measuring it anyway is
                # how a fixture quietly stops being ground truth.
                sys.exit(f"sha256 mismatch on {c['path']}\n  fixture {c['sha256']}\n"
                         f"  actual  {got}")
            print(f"  measuring {name} ...", flush=True)
            row["metrics"] = measure_clip(p)
            row["sha256"] = got
        else:
            missing.append(c["path"])
            continue
        rows.append(row)

    if missing:
        print(f"\n  {len(missing)} clip(s) absent — review/ is untracked by gate G5, "
              f"so a fresh\n  checkout has the labels and not the pixels:")
        for m in missing:
            print(f"    {m}")
    if len(rows) < 4 or not any(r["label"] == "invented" for r in rows):
        sys.exit("\n  too few labelled clips present to evaluate anything")

    results = evaluate(rows)
    report(rows, results)

    extra = []
    if a.portability:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import licence_gate as lg
        for p in sorted(Path(a.portability).glob("*.mp4")):
            # Skip held stills for the same reason check_invention does: a
            # deterministic push-in has no model behind it and cannot invent.
            meta = lg.sidecar_for(p, lg.META_EXT)
            if meta and "model: none" in meta.read_text(encoding="utf-8"):
                continue
            print(f"  measuring {p.name} (portability) ...", flush=True)
            extra.append((p.name, measure_clip(p)))
        if extra:
            portability(results, rows, extra)
    rules_report(rows, extra)

    if a.write_cache:
        if missing:
            sys.exit(f"\n  refusing to write {cache.name}: {len(missing)} clip(s) "
                     f"were absent, and a partial write\n  would delete measurements "
                     f"this checkout simply could not take")
        old = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
        body = {"set_id": fx["set_id"], "frozen": str(fx["frozen"]), "K": K,
                "clips": [{"name": r["name"], "path": r["path"],
                           "sha256": r["sha256"], "label": r["label"],
                           "out_of_sample": r["out_of_sample"],
                           "metrics": r["metrics"]} for r in rows]}
        # Portability numbers are kept only if this run took them; a run without
        # --portability must not silently drop the ones already on the record.
        if extra:
            body["portability"] = {n: m for n, m in extra}
        elif "portability" in old:
            body["portability"] = old["portability"]
        cache.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
        print(f"\n  wrote {cache}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
