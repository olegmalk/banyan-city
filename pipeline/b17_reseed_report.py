#!/usr/bin/env python3
"""Re-validate the HARDENED tracker, then judge all five clips with it.

The association step was hardened after seeing seed 20260912. Changing an
instrument after seeing a result is the moment measurement discipline is most
at risk, so the hardened version must clear the SAME three gates the earlier
one cleared, before it is allowed to produce a verdict:

  GATE 1  reproduce b0911318's published numbers on the winner's clip
  GATE 2  SYN-frozen (f000 held 97 frames) must read ~0 travel
  GATE 3  SYN-pan (whole frame translated 60px x, 30px y, nothing articulates)
          must recover sqrt(60^2+30^2)=67 px AND move the control hand with it

If any gate fails, the hardened tracker is a DIFFERENT instrument and nothing
may be compared across it.

Then ALL FIVE clips -- the winner included -- are re-judged by the final
version. A reseed judged by a tool the winner was never run through is not a
reproduction, and that standard applies to my own changes too.
"""
import sys

import numpy as np

import track2 as T

WINNER = "WINNER-s20260901.mp4"
PUBLISHED = {"start_left": (247, 737), "start_right": (524, 748),
             "f030": 231.0, "peak": 249.6, "peak_frame": 64,
             "handwidths": 1.39, "control_f040": 2.0}


def gate1():
    r = T.analyse(WINNER, "winner")
    rows = [
        ("left hand f000 centroid", "(247, 737)", "(%d, %d)" % r["start_left"],
         abs(r["start_left"][0] - 247) < 25 and abs(r["start_left"][1] - 737) < 25),
        ("right hand f000 centroid", "(524, 748)", "(%d, %d)" % r["start_right"],
         abs(r["start_right"][0] - 524) < 25 and abs(r["start_right"][1] - 748) < 25),
        ("travel at f030", "231 px", "%.1f px" % r["travel_at_f030"],
         abs(r["travel_at_f030"] - 231) < 40),
        ("PEAK travel", "249.6 px", "%.1f px" % r["travel_peak_px"],
         abs(r["travel_peak_px"] - 249.6) < 40),
        ("peak frame", "f064", "f%03d" % r["travel_peak_frame"],
         abs(r["travel_peak_frame"] - 64) <= 12),
        ("peak in hand-widths", "1.39", "%.2f" % r["travel_peak_handwidths"],
         abs(r["travel_peak_handwidths"] - 1.39) < 0.25),
        ("OTHER HAND control f000->f040", "2 px",
         "%.1f px" % r["control_to_f040_px"], r["control_to_f040_px"] <= 6),
    ]
    print("GATE 1 -- hardened tracker vs b0911318's PUBLISHED numbers")
    print("  %-32s %-12s %-12s" % ("", "published", "hardened"))
    ok = True
    for label, pub, got, good in rows:
        print("  %-32s %-12s %-12s %s" % (label, pub, got, "ok" if good else "!! MISMATCH"))
        ok = ok and good
    return ok


def gate23():
    ok = True
    f = T.analyse("SYN-frozen.mp4", "syn-frozen")
    good = f["travel_peak_px"] <= 2.0 and f["control_to_f040_px"] <= 2.0
    print("\nGATE 2 -- SYN-frozen (f000 held 97 frames), expect ~0")
    print("  travel %.1f px, control %.1f px   %s"
          % (f["travel_peak_px"], f["control_to_f040_px"], "ok" if good else "!! FAIL"))
    ok = ok and good

    p = T.analyse("SYN-pan.mp4", "syn-pan")
    want = float(np.hypot(60, 30))
    good = abs(p["travel_peak_px"] - want) < 12 and p["control_other_hand_peak_px"] > 30
    print("\nGATE 3 -- SYN-pan (frame translated 60,30; nothing articulates)")
    print("  travel %.1f px (want sqrt(60^2+30^2)=%.1f), CONTROL %.1f px moves with it   %s"
          % (p["travel_peak_px"], want, p["control_other_hand_peak_px"],
             "ok" if good else "!! FAIL"))
    print("  control/travel ratio %.3f  <- the F3 signature"
          % (p["control_other_hand_peak_px"] / p["travel_peak_px"]))
    return ok and good


def judge(clips):
    print("\n" + "=" * 78)
    print("ALL FIVE CLIPS, ONE TOOL, HAND_W=180 px, BAR=1.0 hand-width")
    print("=" * 78)
    out = []
    for clip, label in clips:
        r = T.analyse(clip, label)
        ratio = r["control_to_f040_px"] / max(r["travel_peak_px"], 1e-6)
        out.append((label, r, ratio))
        print("\n%s" % label)
        print("  M2 peak travel      %7.1f px = %.2f hand-widths  at f%03d   %s"
              % (r["travel_peak_px"], r["travel_peak_handwidths"],
                 r["travel_peak_frame"],
                 "MEETS 1.0" if r["travel_peak_handwidths"] >= 1.0 else "BELOW 1.0"))
        print("  control other hand  %7.1f px to f040   (ratio %.3f)"
              % (r["control_to_f040_px"], ratio))
        print("  self-check flagged  %s" % r["selfcheck_failed_at"])
        lm = r["landmarks"]
        print("  landmarks  " + "  ".join(
            "%s:%s(n%.2f)" % (k, v["max_shift"], v["worst_n"]) for k, v in lm.items()))
        c = r["travel_curve"]
        print("  curve  " + " ".join("f%02d:%s" % (i, c[i])
                                     for i in range(0, len(c), 8)))
    return out


if __name__ == "__main__":
    g1 = gate1()
    g23 = gate23()
    if not (g1 and g23):
        print("\n!! HARDENED TRACKER FAILED ITS GATES -- nothing may be quoted")
        sys.exit(1)
    print("\nALL THREE GATES PASS -- the hardened tracker is the same instrument")
    judge([(WINNER, "WINNER  seed 20260901 (b0911318's PASS)")] +
          [("S%s.mp4" % s, "reseed  seed %s" % s) for s in sys.argv[1:]])
