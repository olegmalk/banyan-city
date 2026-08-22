#!/usr/bin/env python3
r"""Derive the 0.30 NATURALIZE job for BEAT 06's composited bark board.

    python3 pipeline/derive_ep2_b06nat_0822.py            # dry run
    python3 pipeline/derive_ep2_b06nat_0822.py --write

WHY THIS IS ITS OWN FILE AND NOT A THIRD ROW IN derive_ep2_sapnat2_0822
-----------------------------------------------------------------------
Every naturalize in this tree so far has settled a PLANT into a plate, and both
sibling derivers say so in their prompts, their negatives and their bars: two
average leaves on one stem, `three leaves` and `lobed leaves` banned, P3 counts
the blades. Beat 06's object is a slab of bark held in a man's hands. Sharing a
row table would have meant a prompt clause, a negative and four bar clauses
overridden per row, and the reader of the sapling deriver would have to hold a
board in their head while reading about cotyledons. The MACHINERY is shared by
import -- not one sampler number is retyped here.

AND ONE OVERRIDE IS LOAD-BEARING RATHER THAN COSMETIC: the sapling rows put
`1boy, 2boys, goblin, man, person` in the NEGATIVE, because those two plates
have no figure and the pass must not invent one. Beat 06's plate IS a man, the
mask sits over his chest, and carrying that negative across would have banned
the subject of the shot inside the region being redrawn.

WHAT THIS PASS IS FOR
-----------------------------------------------------------------------
`ep2-b06-pose-r4-0822` is the first frame of this beat with the right man,
whole, in a daylit field, head bowed over his own empty clasped hands.
`pipeline/beat06_board_composite.py` then drew the slab into those hands. What
the composite CANNOT do is make the slab belong to the picture: it is a flat
two-value shape with a hard cut edge and a ruled grain, sitting in front of a
cel-shaded drawing. That is what 0.30 is for, and it is the same argument the
plant composites made four times before this one.

0.30 runs 12 of 40 steps from a latent that still carries the drawn structure,
so the high-sigma steps where global layout is decided never run. That is the
whole reason the pass can draw a pasted shape into the plate's dialect WITHOUT
moving it -- and moving it is the failure that would matter most here, because
the thing that makes this frame worth having is that the board is IN HIS HANDS
at a width authored in pixels.

$0 to derive. ~4 GPU minutes.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                            # noqa: E402
import derive_fetch_guard                                     # noqa: E402
import derive_ep2_sapnat2_0822 as S                           # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77     # noqa: E402

BEAT = 6
# ROUND 2 IS A NUMBER AND IT WAS PRE-REGISTERED AS ONE. Round 1 at 0.30 passed
# every clause except P1: the slab did not move, did not shrink, is still held,
# is not glowing and the man is untouched -- but the surface came back exactly
# as flat as it was drawn, reading as ruled card rather than rough bark. That is
# the spec's own third failure mode, verbatim: "0.30 leaves the slab exactly as
# flat as it was drawn, which would say the pass needs more strength on a
# hard-edged man-made object than it needs on a leaf -- and that is worth one
# more round rather than a redraw." So: one more round, one number, and the
# thing it is measuring is whether a MADE object needs a different strength
# from an organic one. Everything else, including the drawn composite itself,
# is byte-identical.
STRENGTH = "0.45"
# ROUND 3 IS THE HAND-SIZED RECUT AT THE STRENGTH ROUND 2 FOUND. Two edits
# from r1 and both are already measured rather than guessed: 0.45 (r2 proved a
# made object needs it) and a 160x115 board instead of 240x128, because r1 and
# r2 both drew a slab as wide as his shoulders and the beat's definition says
# HAND-SIZED -- the compositor's size guard was a floor where it should have
# been a ceiling. The r2 frame is kept as the strength evidence; this is the
# one that could go in a cut.
ROUND = "r3"
SUFFIX = "" if ROUND == "r1" else "-" + ROUND
NEW_ID = "ep2-b06-boardnat%s-0822" % SUFFIX
DIRTOK = "b06boardnat%s-0822" % SUFFIX
OUTTOK = "b06-boardnat%s" % SUFFIX
PUBDIR = "ep2-b06-boardnat%s-0822" % SUFFIX

SRC_DIR = "farm-out/ep2-b06-boardcomp-r2-0822"
INIT = "b06-boardcomp-r2-in-0822.png"
MASK = "b06-boardcomp-r2-in-mask-0822.png"

# The 0821 fetch script, retargeted. Its OUT is the box work dir and its RAW is
# the repo directory, and the two are NOT the same string -- that mismatch cost
# two rc=2 filings on the sibling deriver this morning, so both are set here
# explicitly instead of by substitution.
# SINGLE backslashes on purpose. The 0821 template is a NON-raw triple-quoted
# string whose body reads `OUT = r"C:\\banyan-farm\\..."`, so by the time it is a
# value in memory the doubles have already collapsed to singles. Matching it
# with a doubled pattern silently replaces nothing, the OUT stays
# b06sapnat-0821, the fetch writes there and the dry step reads b06boardnat-0822
# and dies "init not found" -- which is what it did on the first filing, rc=2 in
# one second with no model loaded. Same class as the sibling deriver's bug an
# hour earlier and the same gate caught it.
FETCH = (S.P.FETCH
         .replace(r"C:\banyan-farm\b{beat:02d}sapnat-0821",
                  r"C:\banyan-farm\%s" % DIRTOK)
         .replace("farm-out/ep2-b{beat:02d}-sapnat-0821/",
                  "%s/" % SRC_DIR)
         .replace("banyan-city-b{beat:02d}-sapnat/1.0",
                  "banyan-city-b06-boardnat/1.0")
         .replace("beat {beat:02d}", "beat 06"))

PROMPT = (
    "A grown man with dark cropped hair and round wire-rim glasses holding a "
    "large flat slab of rough brown bark in both hands at chest height, "
    "looking down at it, standing in tall grass in bright daylight, detailed "
    "cinematic anime, masterpiece, best quality, very aesthetic")

# NOTE WHAT IS *NOT* BANNED. `1boy`/`man`/`person` are in the sibling deriver's
# negative and are struck here: the mask lies over this man's chest and hands,
# and banning the subject inside the region being redrawn is how you get a
# headless shirt. What IS banned is every wrong reading of the OBJECT that this
# beat's three ControlNet rungs actually produced -- a glowing panel, a plank
# standing on the ground, a clipboard -- plus the paper/clip family the beat's
# own definition rules out.
NEGATIVE = (
    "glowing board, luminous panel, light source, lens flare, plank standing "
    "on the ground, fence post, clipboard, metal clip, spring clip, white "
    "paper, sign, banner, text, watermark, book, tablet, two boards, "
    "photorealism, 3d render, low quality, lowres, blurry, deformed hands")

BAR = """JUDGED BY EYE AT 1:1. THE OBJECT IS THE QUESTION, THE MAN IS THE CONTROL.

  P1  THE SLAB IS DRAWN, NOT PASTED. It carries cel shading and the plate's own
      ink line weight; the compositor's flat two-value fill, its ruled grain
      and its hard cut edge are gone. It should read as a piece of BARK -- a
      rough, fibrous, slightly warped natural surface -- and not as a plank of
      milled timber and not as a card.
  P2  IT HAS NOT MOVED AND IT HAS NOT GROWN. The board's size is this beat's
      entire standing fault and the fault is INFLATION -- the definition says
      "hand-sized and readable", the parent job's own success line says "no
      bigger than his own forearm", and its negative banned "giant board,
      oversized board" and failed to hold it. It is authored here at 160 x 115
      px, roughly the width of his own head. If the pass has grown it back
      toward a shield or slid it off the hands, this plate is a FAIL and the
      number is the fix.
  P3  HE IS HOLDING IT. His hands stay at its bottom edge and his head stays
      bowed over it. Hands dropped to his sides is what r2 and r3 both did and
      it is a FAIL here.
  P4  THE MAN SURVIVES UNCHANGED. Dark cropped hair, round wire-rim glasses, an
      adult, the cream shirt and the sash. The mask covers his chest, so this
      is the clause most at risk and it is a killing one.
  P5  IT IS NOT GLOWING. Three rungs on this beat returned a lit panel or a
      luminous ball; the composite is deliberately darker than the local mean
      and the pass must not brighten it back.
  P6  NOTHING GOBLIN, and no second board.

A FAIL on P2 or P4 kills the plate. A FAIL on P1 alone is a strength question
and is worth one more round. If it passes, the next rung is MOTION -- and the
beat's other fault, 4.5 s of frozen frame in a 6.5 s slot, is a motion question
that could never be asked while the object was missing.

ROUND 2 ADDS ONE CLAUSE AND IT CUTS BOTH WAYS. At 0.45 the pass runs 18 of 40
steps instead of 12, which is more licence to redraw AND more licence to move.
So P2 stops being a formality: if the board is a beautiful piece of bark that
has slid, narrowed or turned into a scroll, round 1 is the better plate and the
answer is that this object wants a strength between the two. Say which of the
two frames is better rather than scoring this one alone."""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    init_abs = os.path.join(REPO, SRC_DIR, INIT)
    mask_abs = os.path.join(REPO, SRC_DIR, MASK)
    for f in (init_abs, mask_abs):
        if not os.path.isfile(f):
            raise SystemExit("!! missing composite input %s" % f)
    init_sha, mask_sha = S.sha256_of(init_abs), S.sha256_of(mask_abs)
    assert_under_clip77("b06 prompt", PROMPT)
    assert_under_clip77("b06 negative", NEGATIVE)

    retoken = [
        (S.PARENT_ID, NEW_ID),
        ("ep2-" + S.PARENT_PUBDIR.split("ep2-")[1], PUBDIR),
        (S.PARENT_MASK, MASK),
        (S.PARENT_INIT, INIT),
        (S.PARENT_DIRTOK, DIRTOK),
        (S.PARENT_OUTTOK, OUTTOK),
    ]
    child = derive_spec.derive(
        S.PARENT, NEW_ID,
        fresh={
            "owner": "morning compositor lane, 2026-08-22",
            "consumer": (
                "THE INIT FOR BEAT 06's FIRST MOTION RENDER. This beat has "
                "ZERO clips and two named faults, and the second one -- 4.5 s "
                "of frozen frame in a 6.5 s slot -- has never been askable, "
                "because the object the beat is about was not in any plate. "
                "Named consumer: this lane's b06 motion rung, filed only after "
                "a human opens this png. No cut changes because this landed."),
            "success": (
                "ONE 832x1216 png in which the bark slab READS AS BARK, has "
                "not moved, has not narrowed, is still held in both hands with "
                "the head bowed over it, is NOT glowing, and in which the man "
                "is unchanged -- dark cropped hair, round wire-rim glasses, an "
                "adult in a cream shirt in a daylit field. The named "
                "degenerate outcome is the one three ControlNet rungs already "
                "produced: the board comes back as a LIT PANEL and the figure "
                "goes dark behind it."),
            "why": (
                "BEAT 06'S OBJECT IS NOW DRAWN AND THIS SETTLES IT INTO THE "
                "PICTURE.\n\n"
                "The board is not a ControlNet problem and that is measured, "
                "not argued: three rungs on 2026-08-22 bracketed --scale2 "
                "twice and the drawn rectangle's position twice, and returned, "
                "in order, no object at all with a glowing ball in the cupped "
                "hands; a plank grown DOWNWARD out of the hint's top edge, "
                "standing in front of him like a post; and a lit white panel "
                "over his chest with the figure collapsed into a dark shrouded "
                "shape behind it. The ladder rule closes at three, and the "
                "reading across them is the beat-08 finding in a different "
                "costume -- this class of net renders a white stroke as "
                "LIGHT.\n\n"
                "So ep2-b06-pose-r4-0822 removed the board net and rendered "
                "only the man, in daylight, with his hands together and EMPTY "
                "at chest height. pipeline/beat06_board_composite.py drew the "
                "slab into those hands at a width authored in pixels -- which "
                "is the one thing no wording round has ever controlled and "
                "which IS this beat's fault. This job runs the proven 0.30 "
                "masked i2i over the drawn region only, so the slab comes back "
                "in the plate's dialect instead of on top of it.\n\n"
                "The route's evidence: four plant composites (beats 03, 13, 16 "
                "and 19) and, from last night, the fact that a hand-drawn "
                "composited object SURVIVES i2v motion -- the fig in beat 19 "
                "came off its stem and fell. That was the missing evidence "
                "under this whole route and it is why the board is worth "
                "drawing rather than asking for a fifth time."),
        },
        overrides={
            "seed": S.SEED,
            "argv:--init-sha256": init_sha,
            "argv:--strength": STRENGTH,
            "argv:--note": (
                "ATTACHED TO BOTH THE DRY STEP AND THE RENDER STEP. ON THE DRY "
                "STEP it is a MASK GEOMETRY CHECK, written before any model "
                "loads: the mask must be ONE slab-shaped blob over his chest "
                "with his HANDS AND FACE OUTSIDE IT. If it touches the glasses "
                "or the fingers the pass has a licence to redraw them and P4 "
                "fails by construction. ON THE RENDER STEP: one pass, one "
                "seed, 12 of 40 steps from a latent that still holds the drawn "
                "slab, so the pass finishes the shape instead of inventing "
                "one."),
            "payload:prompt.txt": PROMPT,
            "payload:negative.txt": NEGATIVE,
            "payload:fetch_init.py": FETCH.format(
                beat=BEAT, init=INIT, mask=MASK,
                init_sha=init_sha, mask_sha=mask_sha),
            "key:beat": BEAT,
            "key:priority": 18,
            "key:script_line": (
                "Beat 06 THE CLIPBOARD: the guard turns the bark board over "
                "and reads it. The board's SIZE is the beat's standing fault, "
                "so it is authored in pixels -- 240 px against a 220 px "
                "shoulder floor -- rather than described."),
        },
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THE INIT. Every sampler number is the b16 rung's by copy "
                "through derive_ep2_sapnat_0821 and derive_ep2_sapnat2_0822: "
                "40 steps, cfg 7.5, strength 0.30, pad-crop 64, blur 8, seed "
                "20260820, the whole inpaint_fruit.py payload, the env block, "
                "the needs, the dry-run-before-any-model gate and the no-glob "
                "publish. The prompt and negative change because the object is "
                "a board and not a plant, and the negative additionally STOPS "
                "banning `1boy`/`man`/`person`: the sibling deriver bans them "
                "because its two plates have no figure, and carrying that here "
                "would ban the subject of the shot inside the masked region."),
            "init_provenance": (
                "%s/%s, 832x1216, sha256 %s, with its mask %s sha256 %s. Both "
                "are committed on origin/main; fetch_init.py pulls them by raw "
                "URL and refuses on any sha mismatch. The plate under the "
                "composite is farm-out/ep2-b06-pose-r4-0822/"
                "ep2-b06-pose-r4-0822-posebooth.png, an openpose-only rung "
                "with NO reference image and NO board net, and the slab's "
                "geometry -- board box, hands box, chin line, shoulder floor, "
                "measured ink and light -- is in the .geometry.json beside the "
                "composite." % (SRC_DIR, INIT, init_sha, MASK, mask_sha)),
            "failure_predicted_in_advance": (
                "THREE. FIRST, THE PANEL: the board comes back luminous and "
                "the figure darkens behind it, which is r3 exactly and would "
                "mean the reading is in the MODEL's prior for a bright "
                "rectangle at chest height rather than in the scribble net. "
                "That would be a real finding and it is why the composite is "
                "drawn deliberately darker than the local mean. SECOND, THE "
                "HANDS: the mask's pad-crop is 64 px and the fingers sit "
                "immediately under the board's bottom edge, so this pass can "
                "reach them; deformed hands is in the negative and P4 is a "
                "killing clause. THIRD, THE CARD: 0.30 leaves the slab exactly "
                "as flat as it was drawn, which would say the pass needs more "
                "strength on a hard-edged man-made object than it needs on a "
                "leaf -- and that is worth one more round rather than a "
                "redraw."),
            "not_done_on_purpose": (
                "NO MOTION IS RENDERED AND NO MOTION SPEC IS FILED. Beat 06's "
                "second fault is that 4.5 s of its 6.5 s slot is one frozen "
                "frame, and that is a motion question that has never been "
                "askable because the object was missing from every plate. It "
                "becomes askable the moment this plate passes, and not before "
                "-- filing it now would assert the plate passed before anyone "
                "looked at it."),
        },
        by="pipeline/derive_ep2_b06nat_0822.py",
        retoken=retoken,
    )
    out = "pipeline/jobs/%s.yaml" % NEW_ID
    print("%-24s beat %-3d init %s..  prompt %d chars"
          % (NEW_ID, BEAT, init_sha[:12], len(PROMPT)))
    if not a.write:
        print("\n-- dry run. re-run with --write.")
        return 0
    path = derive_spec.write(child, out, force=a.force)
    derive_fetch_guard.assert_fetch_urls_resolve(path, must_hold=(INIT, MASK))
    print("wrote %s  (fetch urls resolve)" % os.path.relpath(path, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
