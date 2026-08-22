#!/usr/bin/env python3
r"""THE THIRD POSED FRAME, AND IT IS CHOSEN FOR ASYMMETRY.

WHAT IS ALREADY SETTLED, so this cell is production and not a question. The
masked lower-body route landed a SEAT (round two) and then a KNEEL against a
positive that still said `seated` -- the hint beat a contradicting noun, so the
geometry is the skeleton's and a new stance is one PNG. `goblin-lowerbody-route
-0822.md` Sec 6 then measured why the set only needs three or four members: of
the 21 founder-ratified frames, 11 are upper-body crops and 8 are cowboy shots,
and the only two that show a lower body are the canon and its mirror, verified
byte-identical. The standing prior is one frame deep, so three posed frames make
posed the MAJORITY of every leg the trigger has ever seen.

WHY THIS STANCE AND NOT A THIRD SYMMETRIC ONE. `seat` and `kneel` are both
mirror-symmetric, and so are all 21 frames of the v2 set: the trigger has never
seen this creature's left leg do something its right leg is not doing. A third
symmetric pose would add a pose and no new AXIS. This one is not an invention
either -- it is the two proven stances, one per side: the seat's right leg
raised beside the body, unchanged, and the kneel's left leg folded down and out,
unchanged. Segment lengths are his: thighs 94 and 98 px against the canon's
measured 94, shin+boot 129 and 117 against its 95-130.

THE WORDING IS ROUND TWO'S, BYTE-IDENTICAL, and stays that way for the same
reason it did on the kneel: it is the string the set is being built on, and the
gate already established that the hint outvotes it on geometry.

  python3 pipeline/derive_jerry_lowerbody_oneknee_0822.py            # dry
  python3 pipeline/derive_jerry_lowerbody_oneknee_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_spec                                          # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = "pipeline/jobs/ep2-b13-lowerbody-w2-0822.yaml"
NEW_ID = "ep2-b13-lowerbody-oneknee-0822"
HINT_REL = "farm-out/jerry-lowerbody-src-0822/jerry-oneknee-hint-0822.png"
HINT = "jerry-oneknee-hint-0822.png"
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

BAR = """THE ROUTE'S CLAUSES, UNCHANGED, PLUS THE ONE THIS STANCE ADDS.

A1 ASYMMETRY, and it is the reason this cell exists. His RIGHT knee is up and
   out beside the body (near x 280, y 930) and his LEFT leg is folded down and
   out (knee near x 530, y 1040; foot near x 610, y 1125). Two legs doing the
   SAME thing is a FAIL of this cell even if the frame is beautiful -- the set
   already has two symmetric stances and the v2 dataset has twenty-one.

HELD, all passed on the seat and the kneel:
   I1 mean |delta| above y 890 <= 2.0, no structural change.
   I2 his head at 1:1 against taste/refs/goblin-canon-founder-0821.png.
   S1 the seam at y 884..920 reads as a body.  S2 one figure.

P3 IS NOT SCORED. Pale thighs, paw feet and the ~82-unit left/right boot
mismatch are the route's known open clause, the stopping rule against a fourth
wording rung stands, and the mitigation is a crop at y 1070 that deletes every
defective pixel while keeping the fold. Recorded per frame, not re-litigated."""

PREDICTED = """MOST LIKELY: IT WORKS, because nothing about it is new. Both
halves of this skeleton are copied joint-for-joint off stances that have already
driven -- the right leg is the seat's, the left is the kneel's -- and the gate
measured that the hint carries geometry against a contradicting noun.

SECOND, AND IT IS THE ONE WORTH WATCHING: THE NET SYMMETRISES HIM. An anime
checkpoint's prior for a small frontal figure is strongly bilateral, and this is
the first hint in the set that asks it to break that. If both legs come back
doing the same thing, the finding is that the hint carries geometry only where
the prior does not object -- which is a real limit on the route and would be
worth more than the frame.

THIRD: THE ASYMMETRY ARRIVES AND THE SEAM BREAKS ON ONE SIDE ONLY. The join has
been invisible on two symmetric frames; a lap that is doing different things
left and right is the first real test of it.

WHAT WOULD SURPRISE ME: nothing good. This cell is production. The interesting
outcome is the second one."""


def main() -> int:
    write = "--write" in sys.argv
    p = os.path.join(REPO, HINT_REL)
    if not os.path.isfile(p):
        print("!! %s missing -- run pipeline/author_jerry_lowerbody_0822.py "
              "--stance oneknee --write" % HINT_REL)
        return 1
    sha = hashlib.sha256(open(p, "rb").read()).hexdigest()

    from PIL import Image
    if Image.open(p).size != (832, 1216):
        print("!! the hint is not 832x1216; the driver refuses rc 13.")
        return 1

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "the goblin v3 lane, 2026-08-22 -- the third posed frame",
            "consumer": (
                "THE v3 DATASET, directly. This is the THIRD and last posed "
                "frame the minimal v3 spec asks for: of the 21 ratified frames "
                "only two show a lower body and they are the canon and its "
                "mirror, so seat + kneel + this makes posed the majority of "
                "every leg the trigger has ever seen, in a dataset otherwise "
                "byte-identical to the one whose identity bars already pass."),
            "success": (
                "ONE 832x1216 png in which his two legs are doing DIFFERENT "
                "things -- right knee up beside the body, left folded down and "
                "out -- with the route's held clauses still holding."),
            "why": (
                "THE SET NEEDS AN ASYMMETRIC FRAME AND HAS NEVER HAD ONE. "
                "`seat` and `kneel` are both mirror-symmetric and so are all 21 "
                "frames of the v2 dataset: the trigger has never seen this "
                "creature's left leg do something its right leg is not doing. A "
                "third symmetric pose would add a pose and no new axis.\n\n"
                "AND IT IS NOT A NEW INVENTION, which is why it is filed as "
                "production rather than as a question. Both halves are copied "
                "joint-for-joint off stances that have already driven: the "
                "right leg is the seat's, raised beside the body, and the left "
                "is the kneel's, folded down and out. Segment lengths are his, "
                "94 and 98 px of thigh against the canon's measured 94.\n\n"
                "THE WORDING IS ROUND TWO'S, BYTE-IDENTICAL. The gate "
                "established that the hint outvotes the positive on geometry, "
                "so the string the set is built on does not move for a stance."),
        },
        overrides={
            "key:priority": 2,
            "argv:--control": r"C:\banyan-farm\b13lowerbodyoneknee-0822\%s" % HINT,
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
        retoken=[("b13lowerbodyw2-0822", "b13lowerbodyoneknee-0822"),
                 ("b13-lowerbody-w2-s20260823", "b13-lowerbody-oneknee-s20260823"),
                 ("b13-lowerbody-w2-DRY", "b13-lowerbody-oneknee-DRY"),
                 (OLD_HINT, HINT),
                 (OLD_HINT_SHA, sha)],
        by="pipeline/derive_jerry_lowerbody_oneknee_0822.py",
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
