#!/usr/bin/env python3
r"""BEAT 16's PLATE WITHOUT THE SHALLOW-FOCUS BLUR -- a four-cell ladder.

    python3 pipeline/derive_b16_noblur_0822.py --commit <sha> [--force]

WHY THIS EXISTS. The morning compositor lane tried twice to draw the canon
sapling into `ep2-b16-canon-w4-0821` and refused both by eye:

    "its foreground is a SHALLOW-FOCUS BLUR WITH BLOWN HIGHLIGHTS, and its
     green-dominant p88 is (239,255,230). `foliage_palette` takes the highlight
     from that percentile on purpose, so the crescent comes back near-white and
     the plant reads as a ghost over his chest rather than a seedling in front
     of him. The anti-decal law is doing its job and the answer is a different
     PLATE, not a different palette."

It named two routes and this is the second of them: re-render the plate without
the blur. The other -- place the plant low where the grass is dark -- is not
foreclosed by anything here.

WHERE THE RECIPE COMES FROM. Not invented. The ep3 sapling-field lane spent
seven rounds learning how to get a FLAT CEL PLATE WITH A DRAWABLE GROUND PLANE
out of this checkpoint, and its ratified control `ep3-sapfld4-u01-0821` carries
all three of its laws:

  * A DISTANCE CLAUSE BUYS THE GROUND PLANE. Round 2 corrected itself at r02:
    "`wide shot, low angle` does not buy a ground plane -- naming something FAR
    AWAY does", and r02 (r01 minus `wildflowers in the distance`) collapsed back
    to magnified grass. Beat 16's pose words name no distance at all -- they are
    `sitting, in tall grass, full body` -- which is the exact configuration that
    collapse was measured on. Cell `w5b` adds `distant hills`.
  * `low angle` IS DROPPED, round 4 is why, and beat 16 never had it. Recorded
    so the next lane does not re-add it reaching for depth.
  * THE ANTI-BOKEH TERMS LIVE IN THE NEGATIVE. u01's negative carries
    `bokeh, blurry, depth of field` and `scenery, landscape` and it is the only
    b16-adjacent recipe on this tree that has ever returned a clean near
    foreground. Cells `w5a` and `w5c`.

THE STRIP, AND WHY IT IS ITS OWN CELL. w4's negative measures 71 of 77 and
`bokeh, blurry, depth of field` alone takes it to 80 -- over the ceiling, where
the tail that gets dropped is the pose and the location. So four terms come out
of the round-two/three containment block (`glowing eyes, orange eyes, third eye,
eyepatch`). The record says twice that this block removes nothing by itself --
"r2 proved that on the ghost head and r5 proved it again on the eyepatch" -- but
"the record says it is inert" is not a measurement on THIS beat, and a two-
variable first rung is how a ladder stops being attributable. `w5z` is the strip
alone. If w5z and w4 differ, the strip is the finding and the rest of the ladder
is re-read against w5z rather than against w4.

WHAT IS HELD, DELIBERATELY:

  * THE EYE STAYS ON sq45. r13a (sq65) is steward-provisional this morning and
    the founder has not seen it. Beat 16 is the beat where the goblin is DEPTH
    behind a leaf close-up, so the eye is the least load-bearing thing in this
    plate and the most expensive second variable. The eye question is settled on
    beat 13's sheet, not smuggled in here.
  * SEED 20260823, so `ep2-b16-canon-w4-0821` is a matched control already on
    disk and costs no GPU minute.
  * THE POSE, THE SKELETON, THE MASK, THE ADAPTER SCALE and every identity tag.

THE BAR THIS LADDER IS JUDGED ON is the canon bar PLUS the two clauses below,
and note that the canon bar's L1 does NOT cover this: L1 says the founder's
image "is watercolour-adjacent and its background is genuinely out of focus",
which is true of the BACKGROUND and is the opposite of what the compositor
needs from the FOREGROUND. A plate can pass L1 and still be unusable here.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_jerry_canon_0821 as D          # noqa: E402
import jerry_canon_0821 as C                 # noqa: E402

BEAT = 16

# The four terms that come out, all from one block, all named inert twice.
NEG_STRIP = "glowing eyes|orange eyes|third eye|eyepatch"

# u01's own anti-bokeh terms, in u01's own order.
DOF = "bokeh, blurry, depth of field"
DIALECT = "scenery, landscape"

# The distance clause. `distant hills` is u01's, verbatim, and it is inserted
# into the pose words BEFORE `full body` so the tail of the positive is still
# the framing word the CLIP-77 budget exists to protect.
POSE_WORDS_FAR = "sitting, in tall grass, distant hills, full body"

COMPOSITE_BAR = """
BEAT 16's OWN TWO CLAUSES, ON TOP OF THE CANON BAR, and they are what the
compositor needs rather than what the picture needs:

  D1  THE NEAR FOREGROUND IS IN FOCUS AND DRAWABLE. No bokeh, no blown
      highlights, no photographic falloff in the bottom third. THE NUMBER THAT
      FAILED w4: its green-dominant p88 is (239,255,230) -- near-white -- so
      foliage_palette's highlight came back as a ghost. A plate whose
      green-dominant p88 is still up in the 230s FAILS D1 even if it looks
      pleasant, because the tool that consumes it will draw a white plant.
  D2  THERE IS A GROUND PLANE, AND IT IS STRAIGHT. Something far away is
      depicted, the picture is positioned relative to it, and the horizon does
      not bend. beat16_sapling_composite.py draws a VERTICAL stem at a measured
      root point; a curved horizon is a FAIL here for the same reason it was a
      FAIL for the sapling-field lane's step 2.

  AND ONE ABSENCE, scored as a requirement the way the beat-06 pose rung scored
  its empty hands: THE PLATE SHOULD CARRY NO FINISHED PLANT. A weed the erase
  box can take is tolerable and is what --erase-box is for; a second sapling in
  frame is not, because the beat's canon is `sapling-two-leaves` and two plants
  in one frame is the b15 problem arriving from the other side.

  NOTE ON L1. The canon bar's L1 blesses an out-of-focus BACKGROUND, which is
  the founder's own reference and is not in dispute. D1 is about the
  FOREGROUND. A plate may pass L1 and fail D1; w4 did exactly that.
"""

# (round tag, neg_add, pose_words, the one variable, the parent it is one
#  variable from).
CELLS = [
    ("w5z", None, None,
     "THE STRIP ALONE -- four containment terms out of the negative "
     "(`glowing eyes, orange eyes, third eye, eyepatch`), 71 -> 59 tokens. "
     "Nothing else moves. This cell exists so the three below are each ONE "
     "variable and not two.",
     "ep2-b16-canon-w4-0821, which is on disk at this same seed"),
    ("w5a", DOF, None,
     "THE DEPTH OF FIELD IS KILLED -- `%s` added to the negative and nothing "
     "else. This is the rung the compositor lane asked for by name." % DOF,
     "ep2-b16-canon-w5z-0821"),
    ("w5b", DOF, POSE_WORDS_FAR,
     "THE DISTANCE CLAUSE -- `distant hills` into the pose words, which is the "
     "sapling-field lane's round-2 law ('naming something FAR AWAY buys the "
     "ground plane') applied to a beat whose pose words name no distance at "
     "all.",
     "ep2-b16-canon-w5a-0821"),
    ("w5c", DOF + ", " + DIALECT, POSE_WORDS_FAR,
     "THE DIALECT TERMS -- `%s` added to the negative. u01 carries them; they "
     "are the belt to w5a's braces and this cell says whether they cost "
     "anything." % DIALECT,
     "ep2-b16-canon-w5b-0821"),
]


def emit_all(force=False):
    out = []
    for rnd, neg_add, pose_words, one_var, parent in CELLS:
        extra = {
            "composite_bar": COMPOSITE_BAR,
            "the_one_variable": one_var,
            "the_rung_this_is_one_variable_from": parent,
            "real_consumer": (
                "beat16_sapling_composite.py. A pass here is a PLATE, not a "
                "candidate and not a pick: the plant is drawn into it next, "
                "then naturalized, then moved. review/ep2-ship-0821 is not "
                "touched by this job."),
            "why_not_the_eye": (
                "THE ADAPTER REFERENCE IS HELD AT sq45 ON PURPOSE. r13a "
                "(sq65) is this morning's steward-provisional result and the "
                "founder has not seen it. Beat 16 is the beat where the goblin "
                "is DEPTH behind a leaf close-up -- the eye is the least "
                "load-bearing thing in this plate and the most expensive "
                "second variable. If sq65 is ratified, this ladder's winner is "
                "re-fired on it as one further rung."),
            "supersedes_nothing": (
                "ep2-b16-canon-w4-0821 is NOT retired by this ladder. It is "
                "the matched control at seed 20260823 and it is the frame "
                "these four are read against."),
            "predicted_failure_modes": (
                "1. `blurry` IN THE NEGATIVE SHARPENS THE WHOLE PICTURE, "
                "including the background the founder's L1 wants soft. Then "
                "the fix is to split the terms -- keep `bokeh, depth of field` "
                "and drop `blurry` -- and that is a named round-2 lever, not a "
                "new idea.\n"
                "2. `distant hills` PUSHES THE CAMERA BACK and the seated "
                "figure becomes small. The beat can carry that (he is depth "
                "here by design) but the composite needs him readable, so a "
                "figure under about a third of frame height is a fail.\n"
                "3. THE STRIP LETS SOMETHING BACK IN. `glowing eyes` and "
                "`orange eyes` were added after the sample drew orange irises. "
                "w5z is the cell that would show it and it is why w5z exists."),
        }
        path = D.emit(BEAT, rnd=rnd, priority=6, force=force,
                      extra_keys=extra, neg_add=neg_add,
                      neg_strip=NEG_STRIP,
                      pose_words_override=pose_words)
        out.append(path)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--commit", required=True,
                    help="the asset commit stamped as --repo-commit")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    C.ASSET_COMMIT = a.commit
    D.C.ASSET_COMMIT = a.commit
    for p in emit_all(force=a.force):
        print("  ->", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
