#!/usr/bin/env python3
r"""BEAT 16's MOTION ON THE SEPARATED PLANT -- the test of the survival law's
new boundary condition, and the init is the ONLY variable.

    python3 pipeline/file_b16_spanmotion_0822.py [--write]

WHAT IS BEING ASKED. Three beats said a composited object survives i2v -- b12's
leaves (identity), b06's board (size), b19's fig (position). `ep2-b16-
plantmotion-0822` is the first one that did NOT: the plant is in frame at f000
and GONE BY f050. What was different about it is not the object and not the
recipe -- it is that the plant sat ON THE FIGURE in nearly the figure's own
colour. So the law got a boundary condition:

    A COMPOSITED OBJECT SURVIVES MOTION WHEN THE MODEL CAN TELL WHERE IT ENDS.

This clip is that sentence made falsifiable. Everything in the spec is
plantmotion's -- 704x1280, 105 frames at 24 fps, guidance 2.0, distilled
sigmas, two-stage, crf 10, sequential offload, and THE PROMPT AND NEGATIVE
BYTE-IDENTICAL -- and the init is `ep2-b16-sapnat4-0821`'s naturalized frame,
in which the plant stands in the lower left with 60 px of clear ground between
its right blade tip (x 282 after the pass) and the figure's left silhouette
(x~350).

WHY THE PROMPT IS HELD EVEN THOUGH IT NEVER NAMES THE PLANT. The prompt-summons
law ("a subject that is not PLACED in the wording is not drawn", beat 07's
guard, three times) is the OTHER candidate cause of plantmotion's f050
disappearance, and it is a good one. It is not tested here on purpose: two
variables in one clip would make either result unattributable. If the plant
survives with the wording unchanged, SEPARATION was the cause and the law's new
clause holds. If it does not, the wording is the next lever and it is one spec
away -- and that is a better place to be than not knowing which of the two it
was.

KNOWN AND NOT FIXED BY THIS CLIP: plantmotion's camera pushed in against eight
camera-motion terms in the negative -- the same clause beat 06 broke on
2026-08-22. This recipe is carried unchanged, so expect it again; it is a
recipe defect with its own rung and it is not this one.

$0 to file. ~8 GPU minutes.
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

import derive_fetch_guard      # noqa: E402  (imported for parity; see below)
import derive_spec             # noqa: E402

PARENT = "pipeline/jobs/ep2-b16-plantmotion-0822.yaml"
NEW_ID = "ep2-b16-spanmotion-0822"

# ── ROUND TWO, AND IT WAS NAMED IN ROUND ONE'S SPEC BEFORE ROUND ONE RAN. ────
# `--placed` re-fires this clip off the SAME init with the sapling written into
# the wording. Round one answered its question and the answer was no:
#
#     ep2-b16-plantmotion-0822   plant ON him, his own colour   gone by f050
#     ep2-b16-spanmotion-0822    plant CLEAR of him, own space  gone by f005
#
# Separation is not the cause. It is not even a mitigation -- the separated
# plant died TEN TIMES FASTER. And the surviving-object record answers the other
# candidate outright: every composited object that has ever survived i2v in this
# tree was NAMED in its motion prompt -- b12's sapling ("THE SAPLING IS TINY AND
# IT HAS EXACTLY TWO LEAVES"), b21's leaf, b19's fig, b06's board -- and the two
# that died are the only two whose prompt never mentions the object. That is
# 4-for-4 and 0-for-2 on one axis.
#
# So the one variable here is the WORDING, the init is byte-identical to round
# one's, and the clause is an ADDITION -- nothing is removed, the figure clause
# and the action are untouched.
R2_ID = "ep2-b16-spanmotion-r2-0822"
PLACED_CLAUSE = (
    " IN THE FOREGROUND AT THE LOWER LEFT, CLOSE TO CAMERA, THERE IS A TINY "
    "SAPLING AND IT IS THERE FOR THE WHOLE CLIP: one slender upright green "
    "stem carrying EXACTLY TWO broad rounded cotyledon leaves with soft round "
    "tips, standing in the grass clear of him and not touching him. THE "
    "SAPLING DOES NOT MOVE, DOES NOT GROW, DOES NOT FADE AND DOES NOT LEAVE "
    "THE FRAME -- it is in the picture at the first frame and it is still in "
    "the picture at the last frame, the same size, the same shape and in the "
    "same place. TWO LEAVES ONLY: no third leaf, no crown, no bush.")
ANCHOR = "He is sitting, in tall grass, full body."

# The naturalized frame, as the BOX sees it: the courier worktree, because this
# plate was produced by the box and never left it.
SRC_DIR = "ep2-b16-sapnat4-0821"
SRC_PNG = "b16-sapnat4-s20260820.png"
SRC_BOX = r"C:\banyan-farm\courier-box\farm-out\%s\%s" % (SRC_DIR, SRC_PNG)
SRC_REL = "farm-out/%s/%s" % (SRC_DIR, SRC_PNG)

# THE PUBLISH DIRECTORY OF THE PARENT PLATE SAYS 0821 AND THE FILE SAYS 0822.
# That is not a typo here: `derive_ep2_b16_sapnat4_0822.py` inherited sapnat3's
# retoken list, in which the pair `("farm-out/ep2-b03-sapnat-0821/", ...)`
# carries a TRAILING SLASH and therefore never matched the publish step's own
# dir string, which has none -- so the later `("b03-sapnat", "b16-sapnat4")`
# rule rewrote it and left the parent's date. The pixels are right and the
# manifest is the box's own; the path lies about the day. Recorded rather than
# renamed, because the producing job's manifest is the authority.


def sha256_of(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


BAR = """JUDGED ON ONE CLAUSE FIRST, AND THE REST ARE THE USUAL ONES.

  M1  THE PLANT IS STILL THERE AT THE LAST FRAME. This is the rung. Read
      f000, f050 (where plantmotion had already lost it) and the final frame.
      A plant that thins, greys or merges into the grass is a FAIL even if
      something plant-shaped is still visible.
  M2  IT STAYS SEPARATE. It must not drift into him or grow a blade across
      his sleeve. The gap going in is ~60 px.
  M3  HE DOES NOT CHANGE. Face, ears, skin, costume held for the whole clip;
      the action is breathing plus a slow head drift and nothing else.
  M4  THE FRAME DOES NOT MOVE. Carried from the parent as a KNOWN DEFECT --
      plantmotion pushed in against eight negative terms. Score it, do not be
      surprised by it, and do not fix it in this spec.
  M5  TWO LEAVES, ONE STEM, ALL THE WAY THROUGH. Canon sapling-two-leaves.
      `pipeline/count_composited_objects.py` CANNOT judge this clip -- it
      reads sixteen objects on beat 16 because the plant stands in grass of
      its own palette -- so this one is by eye, and that limit is measured,
      not assumed."""


R2_BAR = """SAME BAR AS ROUND ONE, WITH M1 SHARPENED BY WHAT ROUND ONE MEASURED.

  M1  THE PLANT IS STILL THERE AT THE LAST FRAME. Round one's plant was gone
      by f005 -- 8,311 leaf-green px in its ROI at f000, 5,130 at f004, ZERO
      from f005 on. Measure the same way; do not judge this one by eye alone.
  M2..M5 unchanged from ep2-b16-spanmotion-0822."""


def _r2_prompt(parent_prompt):
    """The parent's wording with the sapling PLACED, and nothing removed."""
    if ANCHOR not in parent_prompt:
        raise SystemExit("!! the anchor sentence is not in the parent prompt "
                         "-- refusing to guess where the clause goes")
    if "sapling" in parent_prompt.lower():
        raise SystemExit("!! the parent prompt already names the plant; this "
                         "rung would then have no variable")
    out = parent_prompt.replace(ANCHOR, ANCHOR + PLACED_CLAUSE, 1)
    if len(out) <= len(parent_prompt):
        raise SystemExit("!! the clause did not land")
    return out


def build(write=False, force=False, placed=False):
    src_abs = os.path.join(REPO, SRC_REL)
    if not os.path.isfile(src_abs):
        raise SystemExit("!! missing init %s" % src_abs)
    src_sha = sha256_of(src_abs)

    if placed:
        return _build_r2(src_sha, write=write, force=force)

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "single-rung lane, 2026-08-22",
            "consumer": (
                "THE TEST OF THE SURVIVAL LAW'S BOUNDARY CONDITION, and beat "
                "16's candidate motion if it passes. review/ep2-ship-0821 is "
                "NOT touched by this job -- a passing clip is staged for the "
                "founder, and the swap is his call."),
            "success": (
                "ONE 704x1280 105-frame clip in which the sapling standing in "
                "the lower-left foreground is STILL THERE at the last frame "
                "and has not touched the figure. Scored on the bar in `bar`."),
            "why": (
                "ep2-b16-plantmotion-0822 lost its plant by f050 -- the first "
                "composited object in this tree that does not survive i2v -- "
                "and the difference was that it sat ON the figure in nearly "
                "the figure's own colour. The proposed law is that a "
                "composited object survives motion when the model can tell "
                "where it ends. The smaller-span plate (ep2-b16-canon-w7a-"
                "0821) puts a foreground plane in the frame for the first "
                "time, the plant now stands in it clear of him, and this clip "
                "changes NOTHING ELSE."),
        },
        overrides={
            "argv:--src": SRC_BOX,
            "argv:--sha256": src_sha,
            "key:priority": 18,
            "key:beat": 16,
        },
        retoken=[("ep2-b16-plantmotion-0822", NEW_ID)],
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THE INIT. Prompt, negative, size, frame count, fps, "
                "guidance, sigmas, staging, crf, offload and the whole "
                "cover_crop payload are the parent's, unmodified. The parent "
                "is itself w4motion with one variable, so this clip is two "
                "single-variable steps from the recipe that produced usable "
                "footage on ten beats."),
            "the_rung_this_is_one_variable_from": (
                "ep2-b16-plantmotion-0822 -- the clip that lost the plant."),
            "init_provenance": (
                "%s, sha256 %s. The naturalized (0.30) frame of "
                "ep2-b16-sapnat4-0822, whose init was cut by "
                "pipeline/beat16_sapling_composite.py --root 190,1200 "
                "--height 560 --tilt -3 --leaf-frac 0.25 --green-sat-floor "
                "0.15 from the w7a plate. MEASURED after the pass: the "
                "plant's green extends x 45..282, the pass moved it 9 px, and "
                "the figure's left silhouette is at x~350." % (SRC_REL,
                                                               src_sha)),
            "failure_predicted_in_advance": (
                "FIRST: the plant survives but the model resolves it as GRASS "
                "-- it is smaller than sapnat3's and it stands in a blurred "
                "field of blades. That is a pass on M1 and a fail on M5 and "
                "the two must be scored separately.\n"
                "SECOND: the plant survives and HE drifts instead, because "
                "the figure is now small in frame and a small face is the "
                "thing i2v has the least to hold on to. The wave has not "
                "tested this recipe on a figure this size.\n"
                "THIRD: the camera pushes in again. Carried defect, named in "
                "M4, not this spec's to fix.\n"
                "FOURTH, AND IT IS THE INTERESTING FAILURE: the plant goes "
                "anyway. Then separation was not the cause, the "
                "prompt-summons law is, and the next spec is this one with "
                "the sapling PLACED in the wording -- one variable, already "
                "named."),
            "not_done_on_purpose": (
                "THE WORDING IS NOT TOUCHED. The prompt never names the plant "
                "and that is the other candidate cause; testing both at once "
                "would make either answer unattributable."),
        },
        by="pipeline/file_b16_spanmotion_0822.py")

    out = "pipeline/jobs/%s.yaml" % NEW_ID
    argv = [t for s in child["steps"] for t in s.get("argv", [])]
    if argv.count("--src") != 1 or argv[argv.index("--src") + 1] != SRC_BOX:
        raise SystemExit("!! the init did not land on the crop step")
    if argv[argv.index("--sha256") + 1] != src_sha:
        raise SystemExit("!! the init digest did not land")
    # THE PARENT IS NAMED IN THE PROSE ON PURPOSE -- it is the rung this is one
    # variable from. What may not survive is a parent PATH, so the check is on
    # the keys a runner reads and not on the whole spec.
    machine = repr({k: child.get(k) for k in ("steps", "payload", "artifacts")})
    if "plantmotion" in machine:
        raise SystemExit("!! a runner-read key still names the parent job dir")
    if write:
        derive_spec.write(child, os.path.join(REPO, out), force=force)
        print("wrote %s\n   init %s sha %s" % (out, SRC_REL, src_sha[:16]))
    else:
        print("DRY RUN -- pass --write. id=%s\n   init %s sha %s"
              % (NEW_ID, SRC_REL, src_sha[:16]))
    return child


def _build_r2(src_sha, write=False, force=False):
    """Round two: the SAME init, the sapling placed in the wording."""
    import yaml as _yaml
    with open(os.path.join(REPO, PARENT), encoding="utf-8") as fh:
        parent = _yaml.safe_load(fh)
    pk = [k for k in parent["payload"]
          if "prompt" in k and "negative" not in k]
    if len(pk) != 1:
        raise SystemExit("!! cannot find the parent's single prompt payload")
    prompt = _r2_prompt(parent["payload"][pk[0]])

    child = derive_spec.derive(
        PARENT, R2_ID,
        fresh={
            "owner": "single-rung lane, 2026-08-22",
            "consumer": (
                "BEAT 16's CANDIDATE MOTION IF IT PASSES, and either way it "
                "closes the survival law. review/ep2-ship-0821 is NOT "
                "touched."),
            "success": (
                "ONE 704x1280 105-frame clip whose lower-left sapling is "
                "still in the picture at frame 104, measured as leaf-green "
                "pixels in its ROI and not judged by eye alone."),
            "why": (
                "ROUND ONE KILLED ITS OWN HYPOTHESIS AND THE RECORD NAMED THE "
                "REPLACEMENT. The plant separated from the figure, in its own "
                "space against out-of-focus grass, died FASTER than the plant "
                "that sat on him: gone by f005 against f050. So 'the model can "
                "tell where it ends' is not the boundary condition.\n\n"
                "THE OTHER CANDIDATE IS 4-FOR-4 AND 0-FOR-2. Every composited "
                "object that has survived i2v in this tree was NAMED in its "
                "motion prompt -- b12's sapling, b21's leaf, b19's fig, b06's "
                "board -- and the only two that vanished, both on beat 16, are "
                "the only two whose prompt never mentions the object. That is "
                "the prompt-summons law, which this tree already paid for on "
                "beats 02, 03, 07 and 20 in its other direction: a subject "
                "that is not PLACED in the wording is not drawn.\n\n"
                "This clip places it. The init is byte-identical to round "
                "one's and the clause is an ADDITION -- the figure clause and "
                "the action sentence are untouched."),
        },
        overrides={
            "argv:--src": SRC_BOX,
            "argv:--sha256": src_sha,
            "payload:b16-motion-prompt.txt": prompt,
            "key:priority": 19,
            "key:beat": 16,
        },
        retoken=[("ep2-b16-plantmotion-0822", R2_ID)],
        extra={
            "bar": R2_BAR,
            "the_one_variable": (
                "THE WORDING, and it is an addition of one clause. The init, "
                "its digest, the negative, the size, the frames, the fps, the "
                "guidance, the sigmas, the staging and the crf are all "
                "ep2-b16-spanmotion-0822's, unchanged."),
            "the_rung_this_is_one_variable_from": (
                "ep2-b16-spanmotion-0822 -- same init, no sapling in the "
                "wording, plant gone by f005."),
            "measured_evidence_for_this_rung": (
                "SURVIVED, object named in the prompt: ep2-b12-leafmotion-"
                "0822 and ep2-b12-stillmotion-r2-0822 (sapling, seedling, "
                "leaves), ep2-b21-leafmotion-0822 (leaf), ep2-b19-dropmotion-"
                "{0822,r2-0822} (fig), ep2-b06-boardmotion-0822 (board, "
                "plank). VANISHED, object NOT named: ep2-b16-plantmotion-0822 "
                "(f050), ep2-b16-spanmotion-0822 (f005). Read off the specs' "
                "own payloads, not from memory."),
            "failure_predicted_in_advance": (
                "FIRST: naming the sapling summons a SECOND one somewhere "
                "else in the frame, which is the prompt-summons law's own "
                "cost and is what `TWO LEAVES ONLY` in the clause is for.\n"
                "SECOND: the clause pulls focus and the model animates the "
                "plant -- growing or unfurling it -- against a beat whose "
                "action is him breathing. The clause says DOES NOT MOVE and "
                "DOES NOT GROW for that reason.\n"
                "THIRD: it survives and beat 16 is done on this axis, at "
                "which point the open items are the founder's eye ruling and "
                "the camera push-in, neither of which is this spec's."),
            "not_done_on_purpose": (
                "NO CUT IS SWAPPED and the plate is not re-rendered. If this "
                "fails too, the lane records that beat 16's plant cannot be "
                "carried through i2v by either lever it had and stops -- the "
                "next move would be a different motion recipe, which is a "
                "wave-wide change and not a beat's rung."),
        },
        by="pipeline/file_b16_spanmotion_0822.py --placed")

    argv = [t for s in child["steps"] for t in s.get("argv", [])]
    if argv[argv.index("--sha256") + 1] != src_sha:
        raise SystemExit("!! the init digest did not land")
    pay = [v for k, v in child["payload"].items()
           if "prompt" in k and "negative" not in k][0]
    if "SAPLING" not in pay:
        raise SystemExit("!! the placed clause is not in the emitted prompt")
    machine = repr({k: child.get(k) for k in ("steps", "payload", "artifacts")})
    if "plantmotion" in machine or "spanmotion-0822'" in machine.replace(
            R2_ID, ""):
        raise SystemExit("!! a runner-read key still names another job dir")

    out = "pipeline/jobs/%s.yaml" % R2_ID
    if write:
        derive_spec.write(child, os.path.join(REPO, out), force=force)
        print("wrote %s\n   init %s sha %s\n   +%d chars of placed clause"
              % (out, SRC_REL, src_sha[:16], len(PLACED_CLAUSE)))
    else:
        print("DRY RUN -- pass --write. id=%s\n   prompt tail: ...%s"
              % (R2_ID, pay[-320:]))
    return child


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--placed", action="store_true",
                    help="ROUND TWO: same init, sapling placed in the wording")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    build(write=a.write, force=a.force, placed=a.placed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
