#!/usr/bin/env python3
r"""The crossing band on beat 08, as a number. $0, CPU, no model, no sampler.

WHY A NUMBER AT ALL. `b08-arm-route-0819.md` §25-§27: the last defect on beat
08's best fill is a SHAPE -- a second brown band crossing the guard's harness
strap below the buckle, forming a small X with two short stubs at its top. Five
renders and one compositor left it untouched. H1(b) says no second strap, and
"no second strap" has been judged by eye alone for three rungs. An eye reading
is the RIGHT primary instrument for a shape, and this file does not replace it.
It exists so that "the band is gone" is falsifiable by somebody who was not in
the room, and so the claim is made against numbers registered BEFORE the frame
under test existed.

THE SIGNATURE. Inside the inpaint mask, in a window of rows below the buckle,
count the rows carrying TWO OR MORE separate runs of strap-hued pixels. The
guard's own harness below the buckle is ONE strap, so an uncrossed strap gives
one run per row; the band adds a second.

  strap hue   Euclidean distance < 52 from (172, 122, 88) -- the plate's own
              strap body, sampled from rows 505-515 ABOVE the mask where the
              strap is uncontested and no pass has ever touched it. Read off the
              PLATE, never off the frame under test.
  rows        y 543..556, the band's own band. Above 543 is the buckle; below
              556 the plate's fist and cuff dominate the mask and the statistic
              stops being about the band.
  columns     inside the mask and x <= 620, which excludes the brown cuff at
              x 636-661 -- real material, outside the strap, and it would add a
              second run on rows that have no band at all.
  runs        >= 6 px wide, bridging gaps of <= 5 px so the strap's own interior
              shading line does not split one strap into two.

REFERENCE VALUES, MEASURED 2026-08-20 ON THE FOUR ALREADY-LANDED FRAMES AND
WRITTEN DOWN BEFORE ep2-b08-cnetfill-0820 EXISTED:

    init (the plate, fist present)              5 / 14
    ep2-b08-str70-0820   (band present)        10 / 14
    ep2-b08-nostrap2-0820 (band present)        8 / 14
    restore-only of str70 (band present)       10 / 14
    ink-carry of str70    (band present)       10 / 14

BAR: <= 4 / 14 is the measured half of H1(b). Strictly below the plate's own 5,
and less than half of every frame that carries the band. Below the PLATE is the
right place for it: the init's own 5 come from the fist and the strap end, both
of which this pass deletes, so a frame that deletes them AND draws no band must
read lower than the frame that still has them.

AND THE INSTRUMENT'S WEAKNESS IS PART OF THE PRE-REGISTRATION, because §27's
lesson was bought at the cost of a whole compositor: THERE IS NO NEGATIVE
CONTROL. No landed frame has the band absent, so this statistic has never been
shown a true pass. A FAIL on it is strong evidence -- every band-bearing frame
scores 8-10. A PASS on it is weak evidence and settles nothing on its own; the
5x eye reading decides, and a metric agreeing with the steward is not a sample.

    python3 pipeline/b08_band_signature.py --frame F.png [--plate P.png]
                                           [--mask M.png]
    python3 pipeline/b08_band_signature.py --selftest
"""
from __future__ import annotations

import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STRAP_RGB = (172, 122, 88)
TOL = 52.0
ROW0, ROW1 = 543, 556
XMAX = 620
MIN_RUN = 6
BRIDGE = 5
BAR = 4

DEFAULT_PLATE = "farm-out/ep2-b08-str70-0820/08-first-citizen-eraseonly-0820.png"
DEFAULT_MASK = ("farm-out/ep2-b08-str70-0820/"
                "08-first-citizen-eraseonly-mask-0820.png")

# frame -> two-run rows, measured before ep2-b08-cnetfill-0820 existed.
REFERENCES = {
    "farm-out/ep2-b08-str70-0820/08-first-citizen-eraseonly-0820.png": 5,
    "farm-out/ep2-b08-str70-0820/b08-str70-s20260822.png": 10,
    "farm-out/ep2-b08-nostrap2-0820/b08-nostrap2-s20260822.png": 8,
    "farm-out/ep2-b08-inkcarry-0820/08-first-citizen-restore-0820.png": 10,
    "farm-out/ep2-b08-inkcarry-0820/08-first-citizen-inkcarry-0820.png": 10,
}


def _runs(flags):
    import numpy as np

    idx = np.nonzero(flags)[0]
    if not len(idx):
        return []
    out, s, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - p > BRIDGE + 1:
            out.append((int(s), int(p)))
            s = i
        p = i
    out.append((int(s), int(p)))
    return [(a, b) for a, b in out if b - a + 1 >= MIN_RUN]


def measure(frame_path: str, plate_path: str = None, mask_path: str = None):
    """Returns (two_run_rows, total_rows, per-row detail)."""
    import numpy as np
    from PIL import Image

    mask_path = mask_path or os.path.join(REPO, DEFAULT_MASK)
    a = np.asarray(Image.open(frame_path).convert("RGB")).astype(int)
    m = np.asarray(Image.open(mask_path).convert("L")) > 0
    if a.shape[:2] != m.shape:
        raise SystemExit("!! frame %s is %s, mask is %s -- refusing"
                         % (frame_path, a.shape[:2], m.shape))
    ref = np.array(STRAP_RGB)
    hue = np.sqrt(((a - ref) ** 2).sum(axis=-1)) < TOL
    detail = []
    hits = 0
    for y in range(ROW0, ROW1 + 1):
        r = _runs(hue[y, :XMAX + 1] & m[y, :XMAX + 1])
        if len(r) >= 2:
            hits += 1
        detail.append((y, r))
    return hits, ROW1 - ROW0 + 1, detail


def selftest() -> int:
    bad = []
    for rel, want in sorted(REFERENCES.items()):
        p = os.path.join(REPO, rel)
        if not os.path.isfile(p):
            bad.append("%s is missing" % rel)
            continue
        got, total, _ = measure(p)
        ok = got == want
        print("%s %-62s %2d / %d (registered %d)"
              % ("ok  " if ok else "FAIL", os.path.basename(rel), got, total,
                 want))
        if not ok:
            bad.append("%s read %d, registered %d" % (rel, got, want))
    # the bar must actually separate: every band-bearing reference fails it and
    # the plate itself fails it, which is what makes a pass mean something.
    for rel, want in REFERENCES.items():
        if want <= BAR:
            bad.append("%s scores %d, at or under the bar %d -- the bar cannot "
                       "separate" % (rel, want, BAR))
    if bad:
        print("\nFAILED: %s" % "; ".join(bad))
        return 1
    print("\nselftest passed: 5 registered references reproduced, and every one "
          "of them is above the bar of %d." % BAR)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frame")
    ap.add_argument("--plate", default=None,
                    help="unused by the statistic and accepted so a caller can "
                         "record which plate the hue was read off; the hue is "
                         "the constant above and is deliberately NOT re-derived "
                         "per frame")
    ap.add_argument("--mask", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.frame:
        print("!! --frame is required", flush=True)
        return 2
    hits, total, detail = measure(a.frame, a.plate, a.mask)
    print("TWO-RUN ROWS %d / %d   bar <= %d   %s"
          % (hits, total, BAR, "PASS (measured half only)" if hits <= BAR
             else "FAIL"))
    for y, r in detail:
        print("  y%d n=%d %s" % (y, len(r), r))
    print("\nNECESSARY, NOT SUFFICIENT. There is no negative control for this "
          "statistic -- no landed frame has the band absent -- so a pass here "
          "is weak evidence and the 5x eye reading decides.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
