#!/usr/bin/env python3
r"""THE GENERALISATION GATE: does this route make A POSE, or does it make THE SEAT?

WHY THIS IS THE ONLY CELL WORTH THE CARD RIGHT NOW. Round two of the masked
lower-body pass landed a seated goblin with his head held at strength 0.95, and
that proves the route ON ONE SKELETON. The v3 dataset needs four to six DISTINCT
stances; if the route only makes the one it was first shown, there is no dataset
and the finding is a single frame. One cell answers that, and nothing downstream
of it can be planned until it does.

AND IT ISOLATES A SECOND THING FOR FREE, WHICH IS WHY THE PROMPT IS NOT TOUCHED.
Round two's positive says `seated`. This cell keeps that word BYTE-IDENTICAL and
swaps only the skeleton, for a KNEEL. So the two conditioning channels are
pointed at each other on purpose:

    legs KNEEL  -> the HINT carries the geometry, the word is along for the ride.
                   The stance set is a hint-authoring job and nothing else.
    legs SEAT   -> the WORDING carried round two's stance and the skeleton was
                   decoration. Every stance then needs its own wording, and the
                   route is much weaker than round two made it look.
    something between -> report it as partial; a hint fighting a contradicting
                   noun is not the configuration the set would ship in either
                   way, and the next cell aligns them.

Round one already showed the prompt choosing a region's CONTENT -- it drew grass
because grass was the only noun on offer. This asks the different question of
who chooses its GEOMETRY, and it is the one question the set depends on.

WHY KNEELING AND NOT A CROUCH. The torso is preserved pixels, so the hip cannot
move; with a fixed hip a crouch and a seat both read as knees-up and the cell
would have tested almost nothing. A kneel inverts the silhouette instead --
knees DOWN and forward toward the midline, shins folded back and out behind
them, feet splayed -- against the seat's knees up and out to the sides. Segment
lengths are still his: thigh 100 and 107 px against the canon's measured 94,
shin+boot 99 px against its 95-130.

  python3 pipeline/derive_jerry_lowerbody_kneel_0822.py            # dry
  python3 pipeline/derive_jerry_lowerbody_kneel_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec                                          # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = "pipeline/jobs/ep2-b13-lowerbody-w2-0822.yaml"
NEW_ID = "ep2-b13-lowerbody-kneel-0822"
HINT_REL = "farm-out/jerry-lowerbody-src-0822/jerry-kneel-hint-0822.png"
HINT = "jerry-kneel-hint-0822.png"
OLD_HINT = "jerry-seat-hint-0822.png"
OLD_HINT_SHA = "da14ee0b1d44485eabc4c1494ff7fa1980a9b3fce51f290946b203204ccc1cf7"

NOTE = (
    "THE GENERALISATION GATE. Round two proved the masked lower-body route on "
    "ONE skeleton -- a seat. The v3 stance set needs four to six distinct "
    "poses, so whether the route makes A POSE or makes THE SEAT is the gate on "
    "the whole set, and this cell is that question. The ONE variable is the "
    "hint: jerry-seat-hint-0822.png -> jerry-kneel-hint-0822.png, knees DOWN "
    "and forward instead of up and out, shins folded back and splayed. THE "
    "PROMPT IS NOT TOUCHED and still says `seated`, deliberately: that points "
    "the two conditioning channels at each other and reads off which one "
    "carries the geometry. Everything else byte-identical to round two -- same "
    "init sha 67ad5c8b, same mask sha 81357e39, same net, scale 1.0, "
    "--pad-crop 0, 40 steps, cfg 7.5, strength 0.95, seed 20260823, no LoRA. "
    "WHAT TO CHECK ON THE DRY PNG: white starts at row 890 and nowhere above "
    "it, full width -- byte-identical to rounds one, two and three.")

BAR = """ONE QUESTION, THREE READINGS, ALL PRE-COMMITTED.

G1 THE GEOMETRY. Compare the legs against
   farm-out/jerry-lowerbody-src-0822/jerry-kneel-hint-0822.png and against
   round two's landed frame.
     KNEEL  -- knees low and toward the midline (near x 330 and 505, y ~1055),
               shins folded back and OUT, feet splayed near x 255 and 580.
               THE HINT CARRIES THE GEOMETRY. The stance set is a
               hint-authoring job and can be built.
     SEAT   -- knees up and out to the sides as in round two, near x 230 and
               640. THE WORDING carried round two's stance. Every stance then
               needs its own wording and the route is weaker than it looked.
     NEITHER-- report as partial and say which half moved.

HELD CLAUSES, unchanged from round two; a regression means the hint reached
more than the legs:
   I1 mean |delta| above y 890 <= 2.0, no structural change.
   I2 his head at 1:1 against taste/refs/goblin-canon-founder-0821.png.
   S1 the seam at y 884..920 reads as a body.  S2 one figure.

P3 IS NOT SCORED HERE. Pale thighs and paw feet are round two's open clause and
the stopping rule against a fourth wording rung stands. This cell is geometry."""

PREDICTED = """MOST LIKELY: THE HINT WINS AND THE LEGS KNEEL. Round one is the
reason -- its skeleton was byte-identical to round two's and it drew NO LEGS,
which says the word chooses whether a body is asked for. It says nothing about
where the limbs go once one is, and the openpose net has driven four of four
postures in this tree whenever no LoRA was in the pass. That is the reading the
stance set needs and it would unblock it the same afternoon.

SECOND, AND IT WOULD BE THE EXPENSIVE ANSWER: A SEAT. `seated` is a strong
compositional token and the masked band is only 27% of the frame, so the net's
residual may not be enough to overrule it. That does not close the route -- it
means each stance carries its own noun -- but it makes every stance a wording
round as well as a hint, and it would make round two's stance partly a
coincidence of the word that fixed round one.

THIRD: A HYBRID -- one leg kneeling, one seated, or a knee in the right place
with the shin still hanging. Two conditioning channels disagreeing is exactly
the configuration that produces it, and it is why this cell would never be the
one the set ships from. It would be reported as partial and the next cell would
align the word with the hint.

WHAT WOULD SURPRISE ME: a clean kneel with the feet splayed behind. That is the
strongest possible answer -- the hint beating a contradicting noun -- and it
would mean the stance set is four hint files and eight minutes of card."""


def main() -> int:
    write = "--write" in sys.argv
    p = os.path.join(REPO, HINT_REL)
    if not os.path.isfile(p):
        print("!! %s missing -- run pipeline/author_jerry_lowerbody_0822.py "
              "--stance kneel --write" % HINT_REL)
        return 1
    sha = hashlib.sha256(open(p, "rb").read()).hexdigest()

    from PIL import Image
    if Image.open(p).size != (832, 1216):
        print("!! the hint is not 832x1216; the driver refuses rc 13.")
        return 1

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "the goblin v3 lane, 2026-08-22 -- the generalisation gate",
            "consumer": (
                "THE v3 STANCE SET, and it is a GATE rather than a product. "
                "Round two proved the route on one skeleton. If the route only "
                "reproduces the stance it was first shown, there is no set and "
                "the finding is a single frame; if the hint carries the "
                "geometry, the set is four hint files and about eight minutes "
                "of card. Nothing downstream can be planned until this reads."),
            "success": (
                "ONE 832x1216 png whose legs are KNEELING -- knees low and "
                "toward the midline, shins folded back and splayed -- against a "
                "positive that still says `seated`. A seat is a real answer and "
                "a worse one, and it gets reported as the answer it is."),
            "why": (
                "ROUND TWO PROVED THE ROUTE ON ONE SKELETON AND THE SET NEEDS "
                "FOUR TO SIX. Whether this route makes A POSE or makes THE SEAT "
                "is the only question standing between a landed frame and a v3 "
                "dataset, and one cell answers it.\n\n"
                "THE PROMPT IS DELIBERATELY NOT TOUCHED. Round two's positive "
                "says `seated` and this cell keeps that word byte-identical "
                "while swapping the skeleton for a kneel, which points the two "
                "conditioning channels at each other and reads off which one "
                "carries GEOMETRY. Round one already settled who chooses a "
                "region's CONTENT -- it drew grass because grass was the only "
                "noun on offer -- and said nothing about where limbs go once a "
                "body is asked for.\n\n"
                "KNEEL AND NOT CROUCH, because the torso is preserved pixels so "
                "the hip cannot move, and with a fixed hip a crouch and a seat "
                "both read as knees-up. A kneel inverts the silhouette instead. "
                "Segment lengths are his: thigh 100 and 107 px against the "
                "canon's 94, shin+boot 99 px against its 95-130."),
        },
        overrides={
            "key:priority": 2,
            "argv:--control": r"C:\banyan-farm\b13lowerbodykneel-0822\%s" % HINT,
            # NOT an argv override for --control-sha256. The sha travels as a
            # RETOKEN instead, because it appears TWICE -- in the argv and in
            # the inherited fetch_init.py payload -- and overriding only the
            # argv leaves the fetcher asserting the seat hint's bytes against
            # the kneel hint's file. Attempt one did exactly that and the
            # fetcher refused: "SHA MISMATCH for jerry-kneel-hint-0822.png,
            # want da14ee0b, have 7f1655bb". rc=1, $0, no model loaded. The
            # guard is why this cost nothing, and a retoken is the fix because
            # it reaches every copy of the string by construction.
            "argv:--note": NOTE,
        },
        extra={
            "bar": BAR,
            "failure_predicted_in_advance": PREDICTED,
            "the_one_variable": (
                "THE HINT, and only the hint. jerry-seat-hint-0822.png "
                "(da14ee0b) -> jerry-kneel-hint-0822.png (%s). The init and the "
                "mask are byte-identical to rounds one, two and three by "
                "construction -- neither depends on the stance, which is why a "
                "second stance is a ONE-FILE diff. Same net, scale 1.0, "
                "--pad-crop 0, 40 steps, cfg 7.5, strength 0.95, seed 20260823, "
                "same prompt.txt, same negative.txt, no LoRA." % sha),
        },
        retoken=[("b13lowerbodyw2-0822", "b13lowerbodykneel-0822"),
                 ("b13-lowerbody-w2-s20260823", "b13-lowerbody-kneel-s20260823"),
                 ("b13-lowerbody-w2-DRY", "b13-lowerbody-kneel-DRY"),
                 (OLD_HINT, HINT),
                 (OLD_HINT_SHA, sha)],
        by="pipeline/derive_jerry_lowerbody_kneel_0822.py",
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
