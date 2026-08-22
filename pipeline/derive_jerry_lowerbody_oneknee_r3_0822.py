#!/usr/bin/env python3
r"""THE ONE-KNEE, REDRAWN -- and the ONE variable is the SEED.

WHY. `goblin-lowerbody-route-0822.md` Sec 6 files the one-knee cell as the best
GEOMETRY in the set and the worst PAINT: mirror-asymmetry over the limb band
81.4, against the kneel's 71.4 and the seat's 60.0 -- the highest in the set, so
the hint drove -- while the right thigh lands 80 RGB units from the canon's sage
as a pink slab, where the kneel's reads 7.

AND ITS DEFECT IS THE ONE THE CROP CANNOT REACH. That is the whole reason this
cell exists and it is worth stating precisely, because every other extremity
defect on this route is free to delete. Sec 6: seat and kneel "carry the defect
in a place a crop deletes (below); `oneknee` does not -- the pink thigh is at
MID-LIMB, inside the fold the frame exists to teach, and no crop reaches it." A
frame whose defect sits inside its own teaching signal is not a shipping frame.

WHY A RESEED AND NOT A WORDING RUNG. The stopping rule against a fourth wording
rung was written into `ep2-b13-lowerbody-w3-0822` BEFORE that render and it
stands: two cells moved the extremity clause and both traded. The route's own
reading of the failure is not a wording one either -- "an anime checkpoint's
prior for a small frontal figure is strongly bilateral, and forcing the two legs
apart bought the geometry at the cost of the material. THE HINT REACHED THE POSE
AND DID NOT REACH THE PAINT." A prior that is fought at one noise draw may not
be fought at another, and that is a seed question, which is $0 and four minutes.

THE BUDGET IS TWO DRAWS, declared here before the first one runs. If neither
lands a sage thigh, the one-knee does NOT ship as the fourth frame and the set
goes out with seat + kneel + crouch, which Sec 6 already says is enough ("three
or four posed full-body frames"). It is not re-litigated with a fifth wording.

  python3 pipeline/derive_jerry_lowerbody_oneknee_r2_0822.py            # dry
  python3 pipeline/derive_jerry_lowerbody_oneknee_r2_0822.py --write
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec                                          # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = "pipeline/jobs/ep2-b13-lowerbody-oneknee-r2-0822.yaml"
NEW_ID = "ep2-b13-lowerbody-oneknee-r3-0822"
OLD_SEED = 20260824
NEW_SEED = 20260825

NOTE = (
    "THE ONE-KNEE REDRAWN AT A SECOND NOISE DRAW, and the seed is the ONLY "
    "variable. Round one gave the best geometry in the set -- mirror-asymmetry "
    "81.4 over the limb band against the kneel's 71.4 and the seat's 60.0 -- "
    "and the worst paint: the right thigh 80 RGB units off the canon's sage as "
    "a pink slab, where the kneel's reads 7. It is the ONE defect on this route "
    "a crop cannot delete, because it sits at mid-limb inside the fold the "
    "frame exists to teach. No wording moves: the stopping rule against a "
    "fourth wording rung was filed before ep2-b13-lowerbody-w3-0822 rendered "
    "and two cells that moved the extremity clause both traded. Hint, init, "
    "mask, prompt, negative, net, scale 1.0, --pad-crop 0, 40 steps, cfg 7.5, "
    "strength 0.95, no LoRA: all byte-identical to round one. seed 20260823 -> "
    "20260824. WHAT TO CHECK ON THE DRY PNG: white starts at row 890 and "
    "nowhere above it, full width, byte-identical to every cell on this route.")

BAR = """ONE CLAUSE DECIDES THIS CELL AND IT IS THE ONE ROUND ONE FAILED.

P1 THE RIGHT THIGH IS SAGE. Sampled where round one was sampled, its RGB
   distance from the canon's own bare shin (120.4 / 130.0 / 110.4, measured at
   355..385 x 925..945) must land nearer the kneel's 7 than round one's 80. The
   line this cell is judged on is 40: under it the frame ships into the v3 set,
   over it draw two fires, and if draw two is also over it the one-knee does not
   ship and the set goes out at three poses.

A1 THE ASYMMETRY SURVIVES THE RESEED. Mirror-asymmetry over the limb band >= 60,
   which is the seat's figure and the floor of the set. A sage thigh bought by
   the net symmetrising him is not a pass -- it is the seat again, drawn slower.

HELD, passed on all four cells of the route:
   I1 mean |delta| above y 890 <= 2.0, no structural change.
   I2 his head at 1:1 against taste/refs/goblin-canon-founder-0821.png.
   S1 the seam at y 884..920 reads as a body.  S2 one figure.

P3's OTHER HALF IS NOT SCORED. Paw feet and the left/right boot mismatch sit
below y 1070 and the crop deletes them for free. Only the thigh is at issue,
because only the thigh is inside the fold."""

PREDICTED = """MOST LIKELY, AND IT IS ROUGHLY A COIN FLIP: THE THIGH IS STILL
WRONG. The route's reading is that the bilateral prior is being fought and pays
in material, and a prior is a property of the weights and the conditioning, not
of the noise. If that reading is right the seed changes little and both draws
land pink -- in which case the finding is worth more than the frame, because it
converts "the hint reached the pose and did not reach the paint" from one
observation into a measured property of this stance.

SECOND: THE THIGH COMES BACK SAGE AND THE ASYMMETRY SURVIVES. That is the frame
the set wants and it costs four minutes to find out. Seed sensitivity of a
local material defect is ordinary in this tree.

THIRD, AND IT IS THE TRAP A1 EXISTS TO CATCH: THE THIGH COMES BACK SAGE BECAUSE
THE NET SYMMETRISED HIM. The pink slab and the forced asymmetry are the same
event, so the cheapest way for the sampler to make a clean thigh is to stop
folding the leg. A frame that passes P1 by failing A1 is the seat with extra
steps and must be rejected, which is why both clauses are scored and neither is
sufficient alone.

WHAT WOULD SURPRISE ME: the head moving. It has not moved in four cells and it
mathematically cannot -- it is outside the mask."""


def main() -> int:
    write = "--write" in sys.argv

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "the goblin v3 lane, 2026-08-22 -- the one-knee, second and LAST draw",
            "consumer": (
                "THE v3 DATASET, and this is the LAST call on whether it is a four-frame set or a three-frame one. Round one's one-knee is the "
                "only frame on this route whose defect a crop cannot delete -- "
                "a pink thigh at mid-limb, inside the fold the frame exists to "
                "teach. This draw decides whether the set ships FOUR posed "
                "frames or three. Nothing downstream is blocked on it: seat, "
                "kneel and crouch are enough by Sec 6's own count."),
            "success": (
                "ONE 832x1216 png that clears BOTH clauses at once, which neither draw so far has: a right thigh within 40 RGB units "
                "of the canon's bare shin AND whose two legs are still doing "
                "different things -- both clauses, because either alone is a "
                "frame the set already has."),
            "why": (
                "DRAW ONE TRADED THE POSE FOR THE PAINT, WHICH IS THE FAILURE THE SPEC PRE-REGISTERED AS THIRD AND THE ONE-KNEE CELL PRE-REGISTERED AS SECOND. Seed 20260824 removed the pink slab and SYMMETRISED him: both legs now do the same thing, so P1 improved by failing A1, which the r2 bar named in advance as \"the seat with extra steps\". This is the last draw the two-draw budget allows.\n\nTHE ORIGINAL DIAGNOSIS STILL STANDS, and only "
                "the paint half is fixable at $0. Round one measured "
                "mirror-asymmetry 81.4 over the limb band, the highest of the "
                "four cells, and a right thigh 80 RGB units off the canon's "
                "sage where the kneel's reads 7.\n\n"
                "AND IT IS THE ONE DEFECT ON THIS ROUTE A CROP CANNOT REACH. "
                "Seat and kneel carry their extremity defects below y 1070 and "
                "the crop law deletes them for free; this one is at mid-limb, "
                "inside the fold, and no crop reaches it without deleting the "
                "signal.\n\n"
                "A RESEED AND NOT A WORDING RUNG, because the stopping rule "
                "against a fourth wording rung was filed before "
                "ep2-b13-lowerbody-w3-0822 rendered and two cells that moved "
                "the extremity clause both traded. THE BUDGET IS TWO DRAWS, "
                "declared before the first: if neither lands a sage thigh the "
                "one-knee does not ship and the set goes out at three poses."),
        },
        overrides={
            "key:priority": 2,
            "seed": NEW_SEED,
            "argv:--note": NOTE,
        },
        extra={
            "bar": BAR,
            "failure_predicted_in_advance": PREDICTED,
            "the_one_variable": (
                "THE SEED, and only the seed: %d -> %d. The hint "
                "(jerry-oneknee-hint-0822.png, 659f9f46), the init (67ad5c8b), "
                "the mask (81357e39), prompt.txt, negative.txt, the net, scale "
                "1.0, --pad-crop 0, 40 steps, cfg 7.5, strength 0.95 and the "
                "absence of a LoRA are all inherited unmodified from round one. "
                "This is the first cell on the route whose variable is not the "
                "hint." % (OLD_SEED, NEW_SEED)),
        },
        retoken=[("b13lowerbodyonekneer2-0822", "b13lowerbodyonekneer3-0822"),
                 ("b13-lowerbody-oneknee-r2-s%d" % OLD_SEED,
                  "b13-lowerbody-oneknee-r3-s%d" % NEW_SEED),
                 ("b13-lowerbody-oneknee-r2-DRY", "b13-lowerbody-oneknee-r3-DRY")],
        by="pipeline/derive_jerry_lowerbody_oneknee_r3_0822.py",
    )

    out = os.path.join(REPO, "pipeline", "jobs", NEW_ID + ".yaml")
    if not write:
        print("DRY -- would write %s\n  seed %d -> %d"
              % (os.path.relpath(out, REPO), OLD_SEED, NEW_SEED))
        return 0
    derive_spec.write(child, out)
    print("WROTE %s" % os.path.relpath(out, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
