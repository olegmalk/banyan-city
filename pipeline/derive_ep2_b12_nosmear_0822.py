#!/usr/bin/env python3
r"""BEAT 12's MOTION, RE-RUN ON THE PLATE WITHOUT THE SMEAR.

    python3 pipeline/derive_ep2_b12_nosmear_0822.py [--write]

ONE VARIABLE, AND IT IS TWO STRINGS: the crop step's `--src` and its
`--sha256`. Everything else in `ep2-b12-leafmotion-0822` is carried byte for
byte -- driver, size, frame count, fps, seed, the action sentence with its
breeze clause, the negative, the crf family. That is the same discipline r1
itself used against its own parent, and it is why r1's result was readable.

WHY. r1 is beat 12's candidate on the merits and the measurement says so: apex
climb 0 px against the take-in-the-cut's 140 px, reproduced at a second wording
by r3, so the beat's recorded shipping fault is fixed and it is a property of
the plate rather than a lucky seed. What r1 still carries is the SMEAR -- a fan
of horizontal bars across the cloud bank, manufactured by a per-row boundary
fill on a plate that is not row-banded, preserved by the 0.30 naturalize and
then preserved again through 121 frames of LTX.

`ep2-b12-sapnat3-0822` is that plate with the fill done in two axes instead of
one, and it came back with the bars gone and the pass having finished the
harmonic wash into actual cloud -- better than the pre-registered risk allowed
for, which said it might read as an out-of-focus patch. So the last thing
between beat 12 and a clean candidate is a re-render, and it is six minutes.

WHAT IS BEING ASKED, AND WHAT IS NOT. This is NOT a re-opening of the
still-versus-grow question. That closed this morning across three rounds: r1 at
0 px, r2 (explicit stillness clause) at 340 px, r3 (breeze clause plus a named
no-grow clause) at 0 px again. The clause set is r1's, unchanged, on purpose.
The only question is whether the clean sky survives the render.

AND THE COUNT AXIS IS NOW MEASURABLE ON THE RESULT.
`pipeline/count_composited_objects.py` reads this beat's own geometry json and
counts blades per frame; r1 scored two on all 121 frames, which is the negative
control the instrument was calibrated against. The re-render gets the same
reading, and a rise would be new.
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                            # noqa: E402

PARENT = "pipeline/jobs/ep2-b12-leafmotion-0822.yaml"
NEW_ID = "ep2-b12-nosmear-0822"
OLD_SRC = (r"C:\banyan-farm\courier-box\farm-out\ep2-b12-sapnat2-0822"
           r"\b12-sapnat2-s20260820.png")
OLD_SHA = "dcc042b8e21f0ded82adb5401186f69a2b8d78aa92eb398eb74631bcfac5ea5a"
NEW_SRC = (r"C:\banyan-farm\courier-box\farm-out\ep2-b12-sapnat3-0822"
           r"\b12-sapnat3-s20260820.png")
NEW_SHA = "5ecde65e9bf6b2bd723ce70bcb59a38fb7401a31fc6acb7bbf545dc67e14555e"

BAR = """THE PARENT'S BAR, UNCHANGED, PLUS ONE CLAUSE AND ONE INSTRUMENT.

  S1  THE SKY HAS NO HORIZONTAL BARS IN IT, on any frame. The parent take
      (12-related-LTX-leaf-0813.mp4 in review/ep2-beats-0821/candidates/) is
      the matched control at one variable, so play them side by side and look
      at the band between the grass line and the leaves.
  S2  APEX CLIMB IS STILL ABOUT ZERO. Measure the top of the leaf mass at f000
      and f120 and say the number. r1 measured 0 px; the take in the cut
      measured 140. A climb reappearing means the plate change moved something
      the plate change had no business moving.
  S3  THE PLANT IS STILL THE CANON TWO-LEAF SHAPE for the whole clip, and this
      is now a number rather than an impression:
        python3 pipeline/count_composited_objects.py \\
          --clip <this clip> --class leaf \\
          --geometry farm-out/ep2-b12-sapnat-0822/b12-sapnat-in-0822.png.geometry.json
      r1 reads 2 on all 121 frames. A run of frames above 2 is the count fault
      that beats 19 and 21 both measured this morning arriving on a third beat.
  S4  EVERYTHING THE PARENT ALREADY PASSED still passes: camera locked, the
      plant rooted, no third leaf, no relocation.

  PRE-REGISTERED FAIL MODE: the harmonic wash gave the model a low-detail
  region and 121 frames is long enough for it to invent something in there --
  a bird, a second cloud bank with a hard edge, a sun. The naturalize already
  drew cloud into it, which is the reason to expect this to hold, but a still
  frame is 40 steps and a clip is a different question."""


def build():
    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "early-morning lane, 2026-08-22",
            "consumer": (
                "BEAT 12's CANDIDATE ON /review/ep2-beats-0821, replacing r1 "
                "if S1 passes and r1 stays if it does not. No cut is touched "
                "by this job; review/ep2-ship-0821 is not written."),
            "success": (
                "ONE 704x1280 clip, 121 frames, identical to "
                "ep2-b12-leafmotion-0822 in every respect except that the "
                "cloud bank behind the plant has no horizontal bars in it."),
            "why": (
                "r1 FIXES BEAT 12's RECORDED FAULT -- apex climb 0 px against "
                "140 px in the cut, reproduced at a second wording -- and "
                "still carries a smear that came from the compositor, not "
                "from the model: fill_from_boundary interpolates PER ROW "
                "because it was written for a horizontally banded grass "
                "plate, and beat 12's backdrop is a cumulus bank. The plate "
                "was re-cut with a two-axis fill "
                "(ep2-b12-sapnat3-0822) and the bars are gone. This is r1 on "
                "that plate and nothing else moves."),
        },
        overrides={
            "argv:--src": NEW_SRC,
            "argv:--sha256": NEW_SHA,
            "key:priority": 16,
        },
        retoken=[
            # THE OUTPUT FILENAME, and it is the bug the morning lane wrote up
            # by name six hours ago: `ep2-b12-tightB-0813`'s publish step wrote
            # a beat 06 clip into a beat 12 directory under a beat 12 filename
            # because the retoken was keyed on the parent ID and the mp4 name
            # never contained it. `12-related-LTX-leaf-0813` contains no part
            # of this job's id either, so it is retargeted explicitly and
            # asserted below.
            ("12-related-LTX-leaf-0813", "12-related-LTX-nosmear-0822"),
            ("ep2-b12-sapnat2-0822", "ep2-b12-sapnat3-0822"),
            ("b12-sapnat2-s20260820.png", "b12-sapnat3-s20260820.png"),
        ],
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THE INIT, and it is exactly two strings: the crop step's "
                "--src and its --sha256. The action sentence with its breeze "
                "clause, the negative, the driver, the size, the frame count, "
                "the fps, the seed and the crf family are the parent's byte "
                "for byte."),
            "the_rung_this_is_one_variable_from": "ep2-b12-leafmotion-0822",
            "init_provenance": (
                "farm-out/ep2-b12-sapnat3-0822/b12-sapnat3-s20260820.png, "
                "sha256 %s -- the 0.30 naturalize of a composite whose erased "
                "region was filled with --fill-mode harmonic instead of the "
                "per-row default. Read off the box's own courier worktree, "
                "which is where the box put it, so there is no fetch step and "
                "nothing to sha against a raw URL." % NEW_SHA),
            "not_done_on_purpose": (
                "THE CLAUSE SET IS NOT TOUCHED. Beat 12's still-versus-grow "
                "question closed this morning at three rounds -- r1 0 px, r2 "
                "(explicit stillness clause) 340 px, r3 (breeze clause plus a "
                "named no-grow clause) 0 px -- and the useful finding was that "
                "taking away the small NAMED movement brings back the large "
                "UNNAMED one. Changing a word here would put that back in "
                "play for no reason."),
        },
        by="pipeline/derive_ep2_b12_nosmear_0822.py")

    argv = [str(t) for s in child["steps"] for t in (s.get("argv") or [])]
    if NEW_SRC not in argv or NEW_SHA not in argv:
        raise SystemExit("!! the new init did not reach the crop step")
    if OLD_SRC in argv or OLD_SHA in argv:
        raise SystemExit("!! the OLD init survives in the child's argv")
    # THE EXECUTABLE SURFACE ONLY -- steps, artifacts and payload. `derivation`
    # is the provenance record and is SUPPOSED to name the parent's mp4 (that
    # is what "retokened: a -> b" means), and the bar cites the parent take by
    # filename on purpose so a reader can play the control. The first draft of
    # this assertion scanned the whole spec and refused its own correct output
    # twice, which is the same shape as a guard that reads prose as argv.
    blob = repr({k: child.get(k) for k in ("steps", "artifacts", "payload")})
    if "12-related-LTX-leaf-0813" in blob:
        raise SystemExit("!! the child still names the parent's mp4 -- it "
                         "would publish on top of beat 12's own candidate")
    return child


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    child = build()
    out = "pipeline/jobs/%s.yaml" % NEW_ID
    if a.write:
        derive_spec.write(child, os.path.join(REPO, out), force=a.force)
        print("wrote %s" % out)
    else:
        print("DRY RUN, all assertions passed -- pass --write. id=%s" % NEW_ID)
    return 0


if __name__ == "__main__":
    sys.exit(main())
