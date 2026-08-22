#!/usr/bin/env python3
r"""BEAT 16's NATURALIZE ON THE SMALLER-SPAN PLATE -- the first one where the
plant is NOT standing on him.

    python3 pipeline/derive_ep2_b16_sapnat4_0822.py [--write]

WHY THIS EXISTS AND WHY IT IS A SIBLING OF sapnat3 RATHER THAN AN EDIT TO IT.
`ep2-b16-sapnat3-0822` is the record of one cut off the w4 plate and it stays
reproducible from its own command line. This is the same recipe -- every
sampler number, the payload, the seed, the negative and the prompt are imported
from that module and not retyped -- pointed at a different init.

WHAT CHANGED UNDER IT, and it is the whole reason the beat was still open:

  THE PLATE. `ep2-b16-canon-w7a-0821` is the 60% cell of the w7 span ladder.
  Its skeleton is `jerry-canon-h37fsitfar60-0822`: the same `sit` pose at the
  same head_frac 0.370 and the same ControlNet 1.0, drawn at 60% of the
  full-span sit's 866 px keypoint span, placed at cx 0.655 with the crown held
  at y=300. Prompt and negative are BYTE-IDENTICAL to w4's, so the foreground
  plane in this plate is attributable to the geometry and to nothing else.

  Three levers were spent on this framing before it: the negative (w5z/a/b/c,
  four cells, all null, and the strip that paid for them broke the eye), the
  positive's distance clause (same four cells), and the conditioning strength
  (w6a at 0.55 -- framing did not move and the costume drifted). HOW STRONGLY
  THE SKELETON IS APPLIED IS NOT THE SAME QUESTION AS HOW MUCH OF THE CANVAS IT
  COVERS.

  THE PLACEMENT. sapnat3 put the plant at root 416,1200 / height 780 because on
  a frame-filling figure there was nowhere else to put it -- it could only
  overlap him. This one is root 190,1200 / height 560 / tilt -3 / leaf-frac
  0.25, plant extent x 31..289 against his silhouette's left edge at x~350.

  THE PLANT IS SMALLER THAN sapnat3's AND THAT IS MEASURED, NOT PREFERRED. The
  corridor left of him is ~350 px and a two-blade sapling is about 2.06x its
  leaf length wide, so a blade longer than ~148 px cannot clear him. Height
  follows from leaf-frac. If the founder wants a bigger plant, the lever is a
  SMALLER FIGURE (w7b/w7c are already rendered and cost the costume) or a plant
  that is allowed to cross his legs -- and crossing him is the thing this whole
  rung exists to avoid.

WHAT THIS PASS IS FOR. `ep2-b16-plantmotion-0822` is the first composited
object in this tree that does NOT survive i2v: in frame at f000, gone by f050,
and what is different about it is that it sat ON the figure in nearly the
figure's own colour. The survival law's boundary condition is that a composited
object survives motion when THE MODEL CAN TELL WHERE IT ENDS. This init is the
separation hypothesis made renderable; the motion sample off this pass is the
test of it.

A FILING DEFECT THIS MODULE CARRIES ON ITS FACE. The 09:25 run of this spec
published to `farm-out/ep2-b16-sapnat4-0821/` -- the parent's DATE, not today's
-- because the retoken list inherited from sapnat3 rewrote the publish path
only in its "farm-out/...*/" form, and the publish step writes a WINDOWS path
with backslashes that no such rule can match. The retoken is fixed below and an
assertion now refuses the emit if any runner-read key still names a sibling id,
but `pipeline/jobs/ep2-b16-sapnat4-0822.yaml` ON DISK IS THE ONE THAT RAN and
still publishes to -0821. It is deliberately NOT re-written: the artifact is
where the box put it, the box's own .sha256 manifest is the authority, and a
spec edited to describe a run it did not produce is the worse lie. Re-deriving
this module will produce a spec that differs from that yaml in the publish path
and in nothing else.

$0 to derive. ~4 GPU minutes.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_fetch_guard                                     # noqa: E402
import derive_spec                                            # noqa: E402
import derive_ep2_b16_sapnat3_0822 as S                       # noqa: E402

PARENT = S.PARENT
NEW_ID = "ep2-b16-sapnat4-0822"
PUBDIR = "farm-out/ep2-b16-sapnat4-0822"
INIT = "b16-sapnat4-in-0822.png"
MASK = "b16-sapnat4-in-mask-0822.png"
PROMPT = S.PROMPT               # identical -- he still sits, in tall grass

PLATE = ("farm-out/ep2-b16-canon-w7a-0821/ep2-b16-canon-w7a-0821-ipahead.png")
PLATE_SHA = "5f2c7d7116bdbec78816d45fc6db21fa2f5924eb05374cbadbf0e2aee6bd413f"
COMPOSITE_ARGV = ("--root 190,1200 --height 560 --tilt -3 --leaf-frac 0.25 "
                  "--green-sat-floor 0.15")

BAR = S.BAR + """

  AND THE CLAUSE sapnat3 COULD NOT BE ASKED, WHICH IS WHY THIS CUT EXISTS:
  Q7  THE RELATION. Is the plant a thing IN FRONT OF HIM in its own space --
      nearest to camera, standing clear, with him set back and smaller behind
      it? sapnat3's own bar recorded this as unanswerable on the w4 plate
      ("the best available reading is 'a plant in front of him', not 'a
      close-up of a leaf'"). It is answerable here.
  Q8  THE SEPARATION SURVIVES THE PASS. The plant must still not touch him
      AFTER 0.30 -- measured, not eyeballed: plant extent x 31..289, his left
      silhouette x~350. A pass that grows the blades into his sleeve has
      destroyed the one property the motion rung is going to test."""


def sha256_of(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build(force=False, write=False):
    init_abs = os.path.join(REPO, PUBDIR, INIT)
    mask_abs = os.path.join(REPO, PUBDIR, MASK)
    for f in (init_abs, mask_abs):
        if not os.path.isfile(f):
            raise SystemExit("!! missing composite input %s" % f)
    init_sha, mask_sha = sha256_of(init_abs), sha256_of(mask_abs)
    S.assert_under_clip77("b16 prompt", PROMPT)

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "single-rung lane, 2026-08-22",
            "consumer": (
                "BEAT 16's PLATE CANDIDATE -- the first one in this tree that "
                "has the corrected goblin AND the plant AND them not touching. "
                "A pass here is staged as the beat's candidate and the motion "
                "sample fires off it. review/ep2-ship-0821 IS NOT TOUCHED: "
                "plate -> candidate -> motion -> founder -> swap."),
            "success": (
                "ONE 832x1216 png in which the canon two-leaf sapling is drawn "
                "into the LOWER LEFT in the plate's own green, has not moved, "
                "and STILL DOES NOT TOUCH THE FIGURE. Judged by eye at 1:1 "
                "against %s/%s, the composite going in." % (PUBDIR, INIT)),
            "why": (
                "THE SPAN LEVER LANDED. Beat 16's framing was the last thing "
                "holding this beat, three levers were measured dead against it "
                "(the negative and the distance clause across four w5 cells, "
                "and ControlNet 0.55 in w6a), and the one left was the "
                "skeleton's own SPAN -- the 08-21 seated-gate law, verbatim: "
                "'the skeleton's span sets the drawn SIZE, so author the span "
                "you want and let the fold come from the WORDING.'\n\n"
                "w7a is that skeleton at 60% of the full-span sit, and it has "
                "a foreground plane in front of him for the first time. The "
                "plant now stands in that plane instead of on his chest, which "
                "is both the beat's brief (the plant is the subject, he is "
                "depth) and the separation hypothesis for the one composited "
                "object in this tree that did not survive i2v."),
        },
        overrides={
            "argv:--init-sha256": init_sha,
            "payload:prompt.txt": PROMPT,
            "payload:fetch_init.py": S.FETCH.format(
                init=INIT, mask=MASK, init_sha=init_sha, mask_sha=mask_sha
            ).replace("ep2-b16-sapnat3-0822", "ep2-b16-sapnat4-0822")
             .replace("b16sapnat3-0822", "b16sapnat4-0822"),
            "key:beat": 16,
            "key:priority": 18,
        },
        retoken=[
            ("b03sapnat-0821", "b16sapnat4-0822"),
            # THE NO-SLASH PAIR IS FIRST AND IT IS THE FIX. sapnat3's list has
            # only the trailing-slash form, which never matches the publish
            # step's own dir string (it has no trailing slash), so the later
            # ("b03-sapnat", ...) rule rewrote it and left the PARENT'S DATE
            # behind: the 09:25 run of this spec published to
            # farm-out/ep2-b16-sapnat4-0821/. Pixels right, path a day wrong.
            # The artifact is kept exactly as the box wrote it -- the producing
            # job's manifest is the authority -- and the fix lives here so the
            # next derive off this family cannot repeat it.
            # ...and the pair is on the BARE ID, not on a path prefix, because
            # the publish step writes a WINDOWS path with backslashes
            # (C:\...\farm-out\ep2-b03-sapnat-0821) that no "farm-out/" rule
            # can ever match. That is the second half of why the first fix
            # attempt still failed its own new assertion.
            ("ep2-b03-sapnat-0821", os.path.basename(PUBDIR)),
            ("farm-out/ep2-b03-sapnat-0821/", PUBDIR + "/"),
            ("b03-sapnat-in-mask-0821.png", MASK),
            ("b03-sapnat-in-0821.png", INIT),
            ("b03-sapnat-s", "b16-sapnat4-s"),
            ("b03-sapnat", "b16-sapnat4"),
        ],
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THE INIT, and nothing else. Every sampler number, the seed, "
                "the negative, the payload and the prompt are imported from "
                "pipeline/derive_ep2_b16_sapnat3_0822.py rather than retyped, "
                "so this cut differs from sapnat3 in the PICTURE going in and "
                "in no other way. The picture differs in two things that "
                "travel together and cannot be separated on this beat: the "
                "plate's span (w4 -> w7a) and the plant's placement (centre, "
                "overlapping him -> lower left, clear of him). They cannot be "
                "held apart because the second is only possible under the "
                "first -- on w4 there is nowhere clear to put it."),
            "the_rung_this_is_one_variable_from": (
                "ep2-b16-sapnat3-0822 on the recipe; ep2-b16-canon-w4-0821 on "
                "the plate, one variable (the control png)."),
            "init_provenance": (
                "%s/%s, 832x1216, sha256 %s, with its mask %s sha256 %s. Cut "
                "by pipeline/beat16_sapling_composite.py %s from %s (sha256 "
                "%s). Full argv in the geometry json beside the png, and "
                "b16-sapnat4-overlay-0822.png in the same directory is the "
                "drawn silhouette outlined on the plate -- the clearance is "
                "visible there, not asserted."
                % (PUBDIR, INIT, init_sha, MASK, mask_sha, COMPOSITE_ARGV,
                   PLATE, PLATE_SHA)),
            "plate_provenance": (
                "ep2-b16-canon-w7a-0821, the 60% cell of the w7 span ladder. "
                "Skeleton jerry-canon-h37fsitfar60-0822 (sha256 b8fe0cca3ff9"
                "39ef55e582bf87dc8d54ae5e8d199234da425bd67529d091aff7), built "
                "by `python3 pipeline/jerry_canon_0821.py --build-skeletons "
                "--only sitfar60` and asserted by that module's --selftest. "
                "Against ep2-b16-canon-w4-0821 the ONLY substantive difference "
                "is the control png and the IP mask it derives; prompt, "
                "negative, seed, ControlNet 1.0, reference and adapter scale "
                "are byte-identical. w7b (50%) and w7c (42%) are committed "
                "beside it and both cost costume detail -- a zip placket and "
                "green boots at 50%, a floral sleeve print and shrunken ears "
                "at 42%."),
            "failure_predicted_in_advance": (
                "FIRST, AND IT IS THE ONE THAT MATTERS: 0.30 grows the blades "
                "and closes the 60 px gap between the plant and his sleeve. "
                "The gap is the whole point of the cut, so measure it after "
                "the pass and do not read a pretty plant as a pass.\n"
                "SECOND: the plant is smaller than sapnat3's and stands in a "
                "blurred foreground, so the pass may resolve it as GRASS "
                "rather than as a sapling -- two average leaves on one stem is "
                "canon and a blade-like pair fails Q4.\n"
                "THIRD: the plate's lower-left is out-of-focus by construction "
                "(that is what the span bought) and a hard-inked plant drawn "
                "over a blurred region can read as a sticker even when the "
                "colour is right. If it does, the lever is the INK, not the "
                "fill -- the same finding sapnat3 recorded at (3,1,8)."),
            "not_done_on_purpose": (
                "NO MOTION IS FILED BY THIS JOB and no cut is swapped. The "
                "motion sample is a separate spec off whichever of this and "
                "the plate the eye picks, and the plant-survival clause is "
                "ITS bar, not this one's."),
        },
        by="pipeline/derive_ep2_b16_sapnat4_0822.py")

    # AND THE ASSERTION THAT WOULD HAVE CAUGHT IT. A retoken that half-fires is
    # silent: the spec runs, the frame is right, and only the directory name
    # says a false thing. So the emitted spec is searched for any sibling of
    # this id that is not this id.
    machine = repr({k: child.get(k) for k in ("steps", "payload", "artifacts")})
    for wrong in ("ep2-b16-sapnat4-0821", "ep2-b03-sapnat-0821",
                  "b03sapnat-0821"):
        if wrong in machine:
            raise SystemExit(
                "!! a runner-read key still names %r -- a retoken half-fired "
                "and the publish path would lie" % wrong)
    if PUBDIR not in machine:
        raise SystemExit("!! nothing in the spec publishes to %s" % PUBDIR)

    out = "pipeline/jobs/%s.yaml" % NEW_ID
    if write:
        derive_spec.write(child, os.path.join(REPO, out), force=force)
        derive_fetch_guard.assert_fetch_urls_resolve(
            os.path.join(REPO, out), must_hold=(INIT, MASK))
        print("wrote %s" % out)
    else:
        print("DRY RUN -- pass --write. id=%s init=%s sha=%s\n  prompt: %s"
              % (NEW_ID, INIT, init_sha[:16], PROMPT))
    return child


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    build(force=a.force, write=a.write)
    return 0


if __name__ == "__main__":
    sys.exit(main())
