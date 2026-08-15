#!/usr/bin/env python3
"""Is this clip holding each picture for more than one frame -- and does it anneal?

RETIRED AND REPLACED 2026-08-15. This file used to compute a second, independent
copy of the `cadence` parity ratio (medians of even-indexed against odd-indexed
pairs). That ratio is a **parity-2 detector** and is blind to every ODD hold
period by construction:

    true hold period   the old ratio read
        2                  26.67x
        3                   1.00x   <-- BLIND
        4                  14.12x
        5                   1.00x   <-- BLIND
        6                   9.56x

So this file's `DOUBLED = 3.0` gate would have passed a clip that holds every
picture for THREE frames, silently, as "cadence ok" -- which is the exact defect
our clips have. It is not repaired by tuning; the number cannot represent an odd
period. Proof and the executable aliasing test live in
`pipeline/hold_period.py` and `pipeline/research/ltx23-motion-source.md` §4.1.

WHAT IT DOES NOW. The same segmentation as before -- flash, head, body, tail,
onset time -- but the cadence line is the **hold period** from the peak lag of
the autocorrelation of the per-pair difference series. The peak lag IS the hold
period, for any period, odd or even.

THE ANNEALING FINDING SURVIVES AND IS WHY THIS FILE STILL EXISTS. These clips
start doubled and smooth out as motion builds, so one number for a whole clip is
really reporting how much ramp the window happened to include. The old parity
ratio on the same beat-02 clip read anywhere from 1.3 to 15.2 depending only on
the window. So the body is still split in half and BOTH halves are reported. A
clip whose early body holds and whose late body does not is annealing; a clip
that holds in both halves is held end to end. Those are different defects and
one number cannot tell them apart.

READ AT 1/8 SCALE, which is a change and a deliberate one. At quarter scale the
1-2px line-work churn on anime line art -- fingers, cuffs, trouser folds
re-forming in place -- inflates the difference series and makes a frozen clip
look alive. The hold reading is scale-stable (0.97 -> 0.96 from 352x640 to
88x160) so dropping to 1/8 costs nothing and removes the churn.

    cadence_check.py clip.mp4 [more.mp4 ...]

**A FILTER, NEVER A VERDICT. THE COLD READ DECIDES.** Exit is nonzero when the
early body shows a strong hold, so this can gate a publish step -- but a
nonzero exit is "somebody open the frames", not a rejection, and a zero exit is
never permission to skip looking. A metric agreeing with the steward is not a
sample.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
import hold_period as hp  # noqa: E402

import numpy as np  # noqa: E402

FLOOR = 2.0        # below this a pair is "nothing happened", not a beat
SCALE = 8          # 1/8 resolution; suppresses line-work churn, reading is stable
FLAG = hp.STRONG   # early-body hold strength at or above this raises the flag


def report(path: str) -> bool:
    try:
        d_all, fps, size, n = hp.pair_differences(path, scale=SCALE)
    except Exception as exc:                              # noqa: BLE001
        print(f"!! could not read {path}: {exc}")
        return False
    name = Path(path).name
    if n < 8:
        print(f"{name}: only {n} frames, skipped")
        return False

    # Pair 0 is the restyle flash, never motion. Everything below works on the
    # rest, and the flash is reported on its own line so it cannot hide.
    flash, d = d_all[0], np.array(d_all[1:], dtype=np.float64)

    # The body is the contiguous span carrying the motion: pairs above a
    # quarter of the clip's smoothed peak. Head and tail are what bracket it.
    k = 3
    sm = np.convolve(d, np.ones(k) / k, mode="same")
    live = np.flatnonzero(sm > max(FLOOR, 0.25 * sm.max()))
    if live.size < 8:
        print(f"{name}: {n} frames, too little movement to judge a hold period")
        return False
    lo_i, hi_i = int(live[0]), int(live[-1]) + 1
    win = [float(v) for v in d[lo_i:hi_i]]
    head, tail = d[:lo_i], d[hi_i:]

    whole = hp.hold_period(win, fps=fps)
    mid = len(win) // 2
    early, late = hp.hold_period(win[:mid], fps=fps), hp.hold_period(win[mid:], fps=fps)

    print(f"{name}: {n} frames @ {fps:.2f} fps, read at {size[0]}x{size[1]}")
    print(f"   restyle flash (pair 0, excluded): {flash:.1f}")
    print(f"   head  {len(head):3d} pairs  mean {head.mean() if len(head) else 0:6.2f}   "
          f"onset at {(lo_i + 1) / fps:.2f}s")
    print(f"   BODY  {len(win):3d} pairs  mean {np.mean(win):6.2f}   "
          f"{len(win) / fps:.2f}s of movement")
    print(f"   tail  {len(tail):3d} pairs  mean {tail.mean() if len(tail) else 0:6.2f}")
    print(f"   BODY HOLD: {whole['reading']}")
    # Both halves, always -- the annealing is the finding, not an average of it.
    for label, r in (("first half ", early), ("second half", late)):
        per = r["period"] if r["period"] else "-"
        st = "%.2f" % r["strength"] if r["strength"] is not None else "  - "
        print(f"     body {label}: period {per}  strength {st}   {r['reading'][:60]}")
    flagged = bool(early["period"] and early["period"] > 1
                   and (early["strength"] or 0) >= FLAG)
    if flagged and not (late["period"] and late["period"] > 1
                        and (late["strength"] or 0) >= FLAG):
        print("   -> HOLDS AT ONSET, ANNEALS as motion builds")
    elif flagged:
        print("   -> HOLDS THROUGH THE BODY, no annealing")
    print("   (a filter, never a verdict -- open the frames)")
    return flagged


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clips", nargs="+")
    a = ap.parse_args()
    bad = [c for c in a.clips if report(c)]
    if bad:
        print(f"\n!! {len(bad)} clip(s) hold a picture across frames at motion onset. "
              f"That is a flag to go and LOOK, not a rejection.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
