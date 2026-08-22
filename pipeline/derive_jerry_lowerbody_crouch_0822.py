#!/usr/bin/env python3
r"""THE FOURTH POSED FRAME, AND THE BEATS CHOSE IT.

WHAT IS ALREADY SETTLED, so this cell is production and not a question. The
masked lower-body route landed a SEAT (round two), then a KNEEL against a
positive that still said `seated` -- the hint beat a contradicting noun -- and
then an asymmetric ONE-KNEE whose geometry arrived. Three cells, one variable
each, and the variable was always the hint. `goblin-lowerbody-route-0822.md`
Sec 6 then measured why the set only needs three or four members: of the 21
founder-ratified frames, 11 are upper-body crops and 8 are cowboy shots, and the
only two that show a lower body are the canon and its mirror, verified
byte-identical. The standing prior is ONE FRAME DEEP, so a handful of posed
frames makes posed the majority of every leg the trigger has ever seen.

WHY CROUCH AND NOT STRIDE, AND IT IS NOT A PREFERENCE. Two beats of 002b ask for
this silhouette and nothing in the set supplies it -- beat 12's "crouches low
behind the pencil-thin trunk ... failing to hide", and the fig-pick's "crouches,
picks one small round purple fruit from the grass with both hands ... level with
his face", whose own script note says that STAYING crouched is the thing that
puts the empty stem at his face height. Stride serves ONE beat: the fruit-drop,
whose three prompt lines in shots.md are three wordings of one shot.

AND STRIDE CARRIES A RISK THIS DOES NOT, measured in this tree rather than
feared. `author_jerry_lowerbody_0822.py`'s own CUT_Y note records it: "a knee at
hip height with the shin hanging is a STANDING figure with its feet apart",
which the `h240hunch` cell already rendered faithfully and uselessly. A frontal
stride on a fixed frontal torso is that exact shape. Adding a frame that reads
as STANDING to a dataset whose entire disease is a standing prior is the one
move on the board with negative expected value.

WHY IT IS NOT THE SEAT AGAIN. That objection is the kneel note's, and it is
answered with geometry rather than with assertion: the seat plants the feet
FORWARD AND WIDE (ankles x 300/540, a 240 px spread, 120 px below the knees) and
a squat tucks them UNDER (ankles x 345/495, a 150 px spread, 105 px below knees
that sit 50 px lower). Feet inside the knees instead of outside them is the
difference between sitting on the ground and squatting on the heels, and it is
90 px of measurable ankle spread. Segment lengths are his: thighs 97 and 97 px
against the canon's measured 94, shin+boot 126 and 129 against its 95-130.

THE WORDING IS ROUND TWO'S, BYTE-IDENTICAL, and stays that way for the same
reason it did on the kneel and the one-knee: it is the string the set is being
built on, and the gate already established that the hint outvotes it on
geometry.

  python3 pipeline/derive_jerry_lowerbody_crouch_0822.py            # dry
  python3 pipeline/derive_jerry_lowerbody_crouch_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec                                          # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = "pipeline/jobs/ep2-b13-lowerbody-w2-0822.yaml"
NEW_ID = "ep2-b13-lowerbody-crouch-0822"
HINT_REL = "farm-out/jerry-lowerbody-src-0822/jerry-crouch-hint-0822.png"
HINT = "jerry-crouch-hint-0822.png"
OLD_HINT = "jerry-seat-hint-0822.png"
OLD_HINT_SHA = "da14ee0b1d44485eabc4c1494ff7fa1980a9b3fce51f290946b203204ccc1cf7"

NOTE = (
    "THE FOURTH POSED FRAME, AND THE BEATS CHOSE IT. Two beats of 002b ask for "
    "a squat and the set has none -- beat 12 crouches behind the trunk, and the "
    "fig-pick crouches to bring the empty stem level with his face. Stride was "
    "the other candidate and serves one beat, and a frontal stride on a fixed "
    "frontal torso is the h240hunch shape: a knee at hip height with the shin "
    "hanging, which renders as a standing figure with its feet apart. THE ONE "
    "VARIABLE is the hint: jerry-seat-hint-0822.png -> jerry-crouch-hint-0822"
    ".png. Feet tucked UNDER the body (ankle spread 150 px) instead of planted "
    "forward and wide (the seat's 240 px), knees 50 px lower. THE PROMPT IS NOT "
    "TOUCHED and still says `seated`: the gate established the hint carries the "
    "geometry, and the string the set is built on does not move for a stance. "
    "Everything else byte-identical to round two -- same init sha 67ad5c8b, "
    "same mask sha 81357e39, same net, scale 1.0, --pad-crop 0, 40 steps, cfg "
    "7.5, strength 0.95, seed 20260823, no LoRA. WHAT TO CHECK ON THE DRY PNG: "
    "white starts at row 890 and nowhere above it, full width -- byte-identical "
    "to rounds one, two, three and the one-knee.")

BAR = """THE ROUTE'S CLAUSES, UNCHANGED, PLUS THE ONE THIS STANCE ADDS.

A1 THE FEET ARE INSIDE THE KNEES, and it is the only clause that separates this
   frame from the seat the set already has. Measured on the landed PNG: the
   horizontal distance between the two feet is LESS than the distance between
   the two knees. On the seat it is the other way round. A frame whose feet
   plant forward and wide is a second seat and is a FAIL of this cell even if
   the frame is beautiful -- the set does not need two of those.

A2 HE IS LOW. The knee band sits below the seat's: limb mass present at
   y 990-1010 where the seat carries it at 930-1000.

HELD, all passed on the seat, the kneel and the one-knee:
   I1 mean |delta| above y 890 <= 2.0, no structural change.
   I2 his head at 1:1 against taste/refs/goblin-canon-founder-0821.png.
   S1 the seam at y 884..920 reads as a body.  S2 one figure.

P3 IS NOT SCORED. Pale thighs, paw feet and the ~82-unit left/right boot
mismatch are the route's known open clause, the stopping rule against a fourth
wording rung stands, and the mitigation is a crop that deletes every defective
pixel while keeping the fold. On THIS stance the crop line is lower than the
seat's y 1070, because the ankles are at y 1095-1100 and the knees at 990 --
recorded per frame at judging time, not guessed here."""

PREDICTED = """MOST LIKELY: IT WORKS AND IT LOOKS LIKE A SQUAT. Nothing about
the cell is new -- fourth run of one recipe, fourth hint, and the previous three
all drove. The joints are inside the ranges the other three used and every one
is below the cut.

SECOND, AND IT IS THE ONE THAT MATTERS FOR THE DATASET: IT COMES BACK AS THE
SEAT. The net has now drawn knees-up-and-out three times off this init, and a
90 px difference in ankle spread is a much smaller ask than the kneel's
inversion was. If the feet plant wide anyway, the finding is that the hint's
resolution on this route is COARSE -- it selects between silhouette FAMILIES and
not between members of one -- and the honest consequence is that the v3 set
ships three distinct poses rather than four, which Sec 6 already says is enough.

THIRD: THE THIGHS GO PINK, as they did on the one-knee. The squat foreshortens
both thighs the way the seat does, and the seat's read 7 RGB units off the
canon's sage while the one-knee's read 80 -- the difference being that the
one-knee forced the legs apart. This stance is symmetric, so the prior is not
being fought, so the seat's outcome is the likelier one.

WHAT WOULD SURPRISE ME: the seam breaking. It has been invisible four times."""


def main() -> int:
    write = "--write" in sys.argv
    p = os.path.join(REPO, HINT_REL)
    if not os.path.isfile(p):
        print("!! %s missing -- run pipeline/author_jerry_lowerbody_0822.py "
              "--stance crouch --write" % HINT_REL)
        return 1
    sha = hashlib.sha256(open(p, "rb").read()).hexdigest()

    from PIL import Image
    if Image.open(p).size != (832, 1216):
        print("!! the hint is not 832x1216; the driver refuses rc 13.")
        return 1

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "the goblin v3 lane, 2026-08-22 -- the fourth posed frame",
            "consumer": (
                "THE v3 DATASET, and TWO BEATS BEHIND IT. Seat, kneel and "
                "one-knee are on disk; this is the squat, which is the "
                "silhouette beat 12 and the fig-pick both name in shots.md and "
                "which nothing in the 21 ratified frames supplies. It ships as "
                "a training frame first and as evidence that the route reaches "
                "a named beat's posture second."),
            "success": (
                "ONE 832x1216 png in which he is DOWN ON HIS HEELS -- the two "
                "feet closer together than the two knees, knee band below the "
                "seat's -- with the route's held clauses still holding."),
            "why": (
                "TWO BEATS ASK FOR A SQUAT AND THE SET HAS NONE. Beat 12 "
                "\"crouches low behind the pencil-thin trunk ... failing to "
                "hide\" and the fig-pick \"crouches, picks one small round "
                "purple fruit from the grass with both hands\", whose script "
                "note says staying crouched is what puts the empty stem level "
                "with his face. Stride was the other candidate and serves one "
                "beat, whose three prompt lines are three wordings of one "
                "shot.\n\n"
                "AND STRIDE CARRIES A RISK THIS DOES NOT. The route's own CUT_Y "
                "note measured that \"a knee at hip height with the shin "
                "hanging is a STANDING figure with its feet apart\" -- the "
                "h240hunch shape, rendered faithfully and uselessly. A frontal "
                "stride on a fixed frontal torso is that shape, and adding a "
                "frame that reads as standing to a dataset whose disease is a "
                "standing prior has negative expected value.\n\n"
                "IT IS NOT THE SEAT AGAIN, and the answer is geometry: the seat "
                "plants the feet forward and wide (240 px of ankle spread, 120 "
                "px below the knees) and this tucks them under (150 px, 105 px "
                "below knees that sit 50 px lower). Feet inside the knees "
                "instead of outside them is sitting versus squatting.\n\n"
                "THE WORDING IS ROUND TWO'S, BYTE-IDENTICAL, because the gate "
                "established the hint outvotes the positive on geometry."),
        },
        overrides={
            "key:priority": 2,
            "argv:--control": r"C:\banyan-farm\b13lowerbodycrouch-0822\%s" % HINT,
            # NOT an argv override for --control-sha256, for the reason the
            # one-knee cell recorded at $0: the sha appears TWICE -- in the argv
            # and in the inherited fetch_init.py payload -- and overriding only
            # the argv leaves the fetcher asserting the seat hint's bytes
            # against this hint's file. It travels as a RETOKEN, which reaches
            # every copy of the string by construction.
            "argv:--note": NOTE,
        },
        extra={
            "bar": BAR,
            "failure_predicted_in_advance": PREDICTED,
            "the_one_variable": (
                "THE HINT, and only the hint. jerry-seat-hint-0822.png "
                "(da14ee0b) -> jerry-crouch-hint-0822.png (%s). The init and "
                "the mask are byte-identical to rounds one, two, three and the "
                "one-knee BY CONSTRUCTION -- neither depends on the stance, "
                "which is why a fourth stance is a ONE-FILE diff and the "
                "author script re-wrote both at the same shas 67ad5c8b and "
                "81357e39. Same net, scale 1.0, --pad-crop 0, 40 steps, cfg "
                "7.5, strength 0.95, seed 20260823, same prompt.txt, same "
                "negative.txt, no LoRA." % sha),
        },
        retoken=[("b13lowerbodyw2-0822", "b13lowerbodycrouch-0822"),
                 ("b13-lowerbody-w2-s20260823", "b13-lowerbody-crouch-s20260823"),
                 ("b13-lowerbody-w2-DRY", "b13-lowerbody-crouch-DRY"),
                 (OLD_HINT, HINT),
                 (OLD_HINT_SHA, sha)],
        by="pipeline/derive_jerry_lowerbody_crouch_0822.py",
    )

    out = os.path.join(REPO, "pipeline", "jobs", NEW_ID + ".yaml")
    if not write:
        print("DRY -- would write %s\n  hint %s %s"
              % (os.path.relpath(out, REPO), HINT, sha))
        return 0
    derive_spec.write(child, out)
    print("WROTE %s" % os.path.relpath(out, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
