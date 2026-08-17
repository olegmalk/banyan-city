#!/usr/bin/env python3
"""TERMINAL-FREEZE INDEX: the first frame of the clip's trailing run of
IDENTICAL pictures, measured as consecutive-frame ncc == 1.0000 (4 dp).

    python3 review/ep2-picks/exact_freeze_index.py <clip.mp4> [more.mp4 ...]
    python3 review/ep2-picks/exact_freeze_index.py --selftest

WHY THIS EXISTS, AND WHY IT IS DELIBERATELY DUMB
------------------------------------------------
Eight motion measures were retired for cause in the week of 2026-08-10..17. All
eight failed the same way: they estimated a quantity (depth, cadence, hand
displacement, vacancy) and the estimate was wrong in a direction nobody could
see from the number alone. This file estimates nothing. It asks one question
with one answer: are these two adjacent pictures THE SAME PICTURE? ncc == 1.0000
at four decimal places over 8-bit luma is not an inference about motion; it is
an identity test on two arrays. A pair that scores 1.0000 and is not identical
does not exist at this precision for real decoded video (the selftest proves the
boundary: a one-pixel change of one grey level in a 704x1280 frame still scores
0.99999... which ROUNDS to 1.0000, so the test is reported as "same picture at
4 dp" and NOT as "byte identical" -- both numbers are printed and they are
allowed to disagree).

WHAT IT REPORTS, AND WHAT IT REFUSES TO CONFLATE
------------------------------------------------
  terminal_freeze_index : first frame index of the TRAILING identical run.
                          None if the last pair is not identical.
  terminal_freeze_len   : how many frames that trailing run spans.
  dup_pairs             : total identical adjacent pairs anywhere in the clip.
  dup_runs              : every identical run as (start, length), in order.

The HOLD PERIOD (how many frames each distinct picture is held for, from
pipeline/hold_period.py) is a DIFFERENT QUANTITY and is not computed here. A
clip that holds every picture for 3 frames has ~2/3 of its adjacent pairs
identical and NO terminal freeze; a clip that animates every frame and then
stops dead has 0 duplicate pairs before the stop and a long terminal freeze.
Reporting one as the other is the mistake this file exists to make impossible.
Quote them as two numbers, always.

VALIDATION HARNESS (--selftest, 5 gates, all must pass before any reading)
-------------------------------------------------------------------------
  G1 frozen gate    : 97 copies of one frame -> freeze index 0, len 97, 96 dups
  G2 motion gate    : 97 all-different frames -> freeze index None, 0 dups
  G3 half gate      : 48 moving then 49 identical -> freeze index 48, len 49
  G4 hold-3 gate    : every picture held 3 frames, last picture NOT extended ->
                      many dups but the terminal run is only the final hold,
                      i.e. it must NOT report a 97-frame freeze
  G5 one-pixel gate : two frames differing by one pixel by one grey level ->
                      NOT byte identical, and ncc still rounds to 1.0000, which
                      is the documented precision boundary above
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image


def decode_luma(path: str) -> list[np.ndarray]:
    """Every frame of the clip as float64 luma, in order, no skipping."""
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            ["ffmpeg", "-v", "error", "-i", path, "-vsync", "0",
             os.path.join(td, "f%05d.png")],
            check=True,
        )
        names = sorted(os.listdir(td))
        out = []
        for n in names:
            im = Image.open(os.path.join(td, n)).convert("L")
            out.append(np.asarray(im, dtype=np.float64))
        return out


def ncc(a: np.ndarray, b: np.ndarray) -> float:
    """Normalized cross correlation of two frames. 1.0 == same picture.

    Zero-variance frames (a flat fill) are handled explicitly: two identical
    flat frames are the same picture and score 1.0; a flat frame against a
    non-flat one scores 0.0. Without this the formula divides by zero and a
    frozen black clip -- the exact case we most need to catch -- comes back nan
    and silently fails every comparison it is used in.
    """
    x = a.ravel() - a.mean()
    y = b.ravel() - b.mean()
    nx = float(np.sqrt((x * x).sum()))
    ny = float(np.sqrt((y * y).sum()))
    if nx == 0.0 and ny == 0.0:
        return 1.0 if np.array_equal(a, b) else 0.0
    if nx == 0.0 or ny == 0.0:
        return 0.0
    return float((x * y).sum() / (nx * ny))


def analyse(frames: list[np.ndarray]) -> dict:
    n = len(frames)
    pairs = []
    for i in range(n - 1):
        v = ncc(frames[i], frames[i + 1])
        ident = bool(np.array_equal(frames[i], frames[i + 1]))
        pairs.append({"i": i, "ncc": round(v, 6), "same4dp": round(v, 4) >= 1.0,
                      "identical": ident})

    same = [p["same4dp"] for p in pairs]

    runs = []
    i = 0
    while i < len(same):
        if same[i]:
            j = i
            while j < len(same) and same[j]:
                j += 1
            runs.append((i, (j - i) + 1))   # frames spanned, not pairs
            i = j
        else:
            i += 1

    if same and same[-1]:
        tstart, tlen = runs[-1]
    else:
        tstart, tlen = None, 0

    return {
        "frames": n,
        "terminal_freeze_index": tstart,
        "terminal_freeze_len": tlen,
        "dup_pairs": int(sum(same)),
        "dup_runs": runs,
        "pairs": pairs,
    }


# --------------------------------------------------------------------------
# validation harness
# --------------------------------------------------------------------------
def _rnd(seed: int, h=64, w=64) -> np.ndarray:
    return np.asarray(
        np.random.default_rng(seed).integers(0, 256, size=(h, w)), dtype=np.float64
    )


def selftest() -> int:
    fails = []

    # G1 frozen
    f = [_rnd(1) for _ in range(1)] * 97
    r = analyse(f)
    if not (r["terminal_freeze_index"] == 0 and r["terminal_freeze_len"] == 97
            and r["dup_pairs"] == 96):
        fails.append(f"G1 frozen gate: {r['terminal_freeze_index']=} "
                     f"{r['terminal_freeze_len']=} {r['dup_pairs']=}")

    # G2 all different
    f = [_rnd(i + 100) for i in range(97)]
    r = analyse(f)
    if not (r["terminal_freeze_index"] is None and r["dup_pairs"] == 0):
        fails.append(f"G2 motion gate: {r['terminal_freeze_index']=} {r['dup_pairs']=}")

    # G3 half: 48 moving, then 49 copies of one frame
    f = [_rnd(i + 200) for i in range(48)] + [_rnd(999)] * 49
    r = analyse(f)
    if not (r["terminal_freeze_index"] == 48 and r["terminal_freeze_len"] == 49):
        fails.append(f"G3 half gate: {r['terminal_freeze_index']=} "
                     f"{r['terminal_freeze_len']=}")

    # G4 hold-3, last picture not extended: 32 distinct pictures x 3 + 1
    f = []
    for k in range(32):
        f += [_rnd(k + 300)] * 3
    f += [_rnd(400)]
    r = analyse(f)
    if r["terminal_freeze_index"] is not None:
        fails.append(f"G4 hold-3 gate: reported a terminal freeze at "
                     f"{r['terminal_freeze_index']} on a clip that ends on a new picture")
    if r["dup_pairs"] != 64:
        fails.append(f"G4 hold-3 gate: {r['dup_pairs']=} expected 64")
    # and the same held clip WITH the last picture extended must report only
    # that final hold, never the whole clip
    f2 = f[:-1] + [f[-2]] * 1
    r2 = analyse(f2)
    if r2["terminal_freeze_index"] == 0:
        fails.append("G4 hold-3 gate: a held clip was called a whole-clip freeze")

    # G5 one-pixel boundary at real frame size
    a = _rnd(7, 1280, 704)
    b = a.copy()
    b[640, 350] = (b[640, 350] + 1) % 256
    v = ncc(a, b)
    if np.array_equal(a, b):
        fails.append("G5 one-pixel gate: frames compared equal, test is broken")
    if round(v, 4) < 1.0:
        fails.append(f"G5 one-pixel gate: ncc {v!r} did not round to 1.0000; the "
                     "documented precision boundary is wrong")

    for line in fails:
        print("FAIL " + line)
    if fails:
        print(f"SELFTEST: FAIL ({len(fails)})")
        return 1
    print("SELFTEST: PASS gates=5")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", default="")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()
    if not a.clips:
        ap.error("give clips or --selftest")

    # gates always run first; a reading from an unvalidated instrument is worth
    # nothing and that is how the retired eight got onto the record.
    if selftest() != 0:
        print("REFUSING to measure: gates failed")
        return 1

    out = {}
    for c in a.clips:
        frames = decode_luma(c)
        r = analyse(frames)
        out[os.path.basename(c)] = {k: v for k, v in r.items() if k != "pairs"}
        print(f"{os.path.basename(c)}  frames={r['frames']}  "
              f"terminal_freeze_index={r['terminal_freeze_index']}  "
              f"terminal_freeze_len={r['terminal_freeze_len']}  "
              f"dup_pairs={r['dup_pairs']}  runs={r['dup_runs']}")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(out, fh, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
