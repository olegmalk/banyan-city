#!/usr/bin/env python3
r"""BEATS 12 AND 21: the SAME motion, re-asked of a plate with canon leaves in it.

    python3 pipeline/derive_ep2_leafmotion_0822.py --selftest
    python3 pipeline/derive_ep2_leafmotion_0822.py --write

ONE VARIABLE, AND IT IS THE INIT. Nothing else in either job moves: same driver,
same size, same 121 frames, same fps, same guidance, same seed, same motion
prompt BYTE FOR BYTE, same negative, same publish. The only edit is the `crop`
step's `--src` and its `--sha256`, from

    C:\banyan-farm\plates-local\12-related-r4-s2.png          (BOTH parents)
to
    ...courier-box\farm-out\ep2-bNN-sapnat2-0822\bNN-sapnat2-s20260820.png

WHY THE ACTION IS NOT TOUCHED, and this is the whole reason these two beats are
cheap. Neither beat has a motion fault:

  b21  its own verdict reads "THE ONLY BEAT OF THE EIGHT WHOSE DEFINITION IS
       FULLY MET -- ALL FOUR CLAUSES, AND THE HARD ONE IS MEASURED." The leaf
       tilts monotonically over ~90 frames in one direction with no oscillation
       and no reversal, AND IT STOPS.
  b12  its approved line is "perfectly still", and its one recorded fault is
       that the sapling GROWS -- apex up 140 px, 11% of frame height. That is a
       fault of the take, not of the sentence, and it is worth measuring again
       against a plate whose plant is a different shape before anything in the
       wording is touched.

So this is the b19 dropmotion rung's shape exactly: an action that could not be
judged on the old init because the object in frame was the wrong object, asked
again of an init that contains the right one. Changing the words as well would
make two variables of it and neither beat would learn anything.

WHAT THE NEW INITS ARE. Both are 0.30 naturalize outputs from this morning
(ep2-b12-sapnat2-0822 and ep2-b21-sapnat2-0822), drawn by
pipeline/beat16_sapling_composite.py onto f000 of each beat's own SHIPPED TAKE
-- so the new init is the picture the founder already accepted with exactly one
thing changed: the plant is canon's two average leaves instead of two round
discs (b12) or one giant lance leaf (b21).

THE CARRIED-IN FAULT, NAMED RATHER THAN DISCOVERED LATER: b12's naturalize left
the boundary-fill smear across its cloud bank standing, which was its own
pre-registered second failure mode (a 20% mask against the b16 leafcomp
mask-area law). It goes into the motion render as-is on purpose -- LTX redraws a
sky far more freely than it redraws a subject, and whether the smear survives
121 frames is a cheaper question to answer here than by re-cutting the erase.

$0 to derive. ~5 GPU minutes each.
"""
from __future__ import annotations

import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                            # noqa: E402

OLD_SRC = r"C:\banyan-farm\plates-local\12-related-r4-s2.png"
OLD_SHA = "cc6bd5f0c0cc116d3cb6530a9bae81ac5b5593a683e4e80e20d6319e0cc0c074"

ROWS = [
    {
        "beat": 12,
        "parent": "pipeline/jobs/ep2-b12-tightB-0813.yaml",
        "parent_id": "ep2-b12-tightB-0813",
        "new_id": "ep2-b12-leafmotion-0822",
        "dirtok": "ep2-b12-tightB-0813",
        "pubdir": "ep2-b12-tightB",
        "nat": "ep2-b12-sapnat2-0822",
        "png": "b12-sapnat2-s20260820.png",
        "sha": "dcc042b8e21f0ded82adb5401186f69a2b8d78aa92eb398eb74631bcfac5ea5a",
        "was": "TWO PERFECT ROUND DISCS on one stem",
        "hard_clause": (
            "PERFECTLY STILL. The approved line for this beat says so and the "
            "recorded fault of the take in the cut is that the sapling GROWS "
            "-- apex up 140 px, 11% of frame height, monotone. Measure the "
            "apex at f000 and f120 and say the number."),
    },
    {
        "beat": 21,
        "parent": "pipeline/jobs/ep2-b21-daylight-0814.yaml",
        "parent_id": "ep2-b21-daylight-0814",
        "new_id": "ep2-b21-leafmotion-0822",
        "dirtok": "ep2-b21-daylight-0814",
        "pubdir": "ep2-b21-daylight-0814",
        "nat": "ep2-b21-sapnat2-0822",
        "png": "b21-sapnat2-s20260820.png",
        "sha": "859243c1813812cad87cf2428b5e9068dbdf085cb7a066882164de0420461fc3",
        "was": "ONE GIANT LANCE-SHAPED LEAF standing straight up",
        "hard_clause": (
            "THE TILT, MONOTONE, AND IT STOPS. The parent take is the only "
            "clip in episode 2 whose definition is fully met and this is the "
            "clause that was measured: the leaf tilts steadily in ONE "
            "direction over about ninety frames, with no oscillation and no "
            "reversal, and then it stops. A two-leaf plant has two blades to "
            "tilt, so the honest reading is THE PLANT tilting as one thing."),
    },
]


def new_src(row):
    return (r"C:\banyan-farm\courier-box\farm-out\%s\%s"
            % (row["nat"], row["png"]))


def bar_for(row):
    return (
        "THE BEAT'S OWN done_when, PLUS THE ONE THING THIS RUNG CHANGED. "
        "PRE-REGISTERED: "
        "(1) EXACTLY TWO AVERAGE LEAVES ON ONE STEM, IN THE FIRST FRAME AND IN "
        "THE LAST. This is the whole point. %s is what the take in the cut "
        "shows, and either that shape or a third leaf coming back is a FAIL "
        "however well the clip moves. Canon: sapling-two-leaves and "
        "sapling-cotyledon-shape. "
        "(2) %s "
        "(3) THE PLANT DOES NOT DRIFT, MULTIPLY OR REROOT. "
        "(4) THE FRAME HOLDS. No pull-back, no re-framing -- the wave's first "
        "law is that a prompt naming an object its init lacks makes the model "
        "build it and re-frame the shot, and this init now CONTAINS every "
        "object the sentence names, so a re-frame here would be a new finding "
        "rather than that one. "
        "PRE-REGISTERED FAIL MODES. THE INIT ABANDONED, which is what both "
        "parents did -- b12's take cuts away from its macro plate by f006 and "
        "beat 21's verdict says 'from f007 the init is entirely gone'. If the "
        "two leaves survive past f010 that alone is new. THE LEAVES ROUNDING "
        "BACK toward discs over the clip, which would say the model's prior "
        "for a seedling beats the init and the fix is not the compositor. And "
        "on beat 12 only, THE CLOUD SMEAR: the naturalize left a horizontal "
        "boundary-fill band across the cumulus and it is carried in "
        "deliberately; if 121 frames of LTX repaint it, that is the cheapest "
        "possible answer to whether the erase needs re-cutting."
        % (row["was"], row["hard_clause"]))


def build(row):
    child = derive_spec.derive(
        src=row["parent"],
        new_id=row["new_id"],
        fresh={
            "owner": "morning compositor lane, 2026-08-22",
            "consumer": (
                "BEAT %02d'S SLOT ON /review/ep2-beats-0821, which has had NO "
                "candidate since the page was written and one reason on it: "
                "the plant is the wrong shape and the fix is a drawing. The "
                "drawing is done and naturalised; this is the render that "
                "turns it into a clip a person can watch. The take in the cut "
                "is untouched and no cut changes because this landed -- a "
                "candidate is a candidate." % row["beat"]),
            "success": (
                "ONE 704x1280 mp4, 121 frames at 24 fps, in which the plant is "
                "CANON'S TWO AVERAGE LEAVES in the first frame and in the "
                "last, and in which this beat's own motion clause still holds. "
                "The beat's shipping fault is not fixed by this job and is not "
                "claimed to be."),
            "why": (
                "BEAT %02d'S PLANT IS THE WRONG SHAPE AND THAT IS NOW FIXED IN "
                "THE PLATE, SO THE MOTION IS RE-ASKED OF IT.\n\n"
                "What is in the cut today: %s. Canon since the founder's "
                "2026-08-17 ruling is AVERAGE leaves. The wording ladder for "
                "leaf shape is CLOSED by measurement -- the strongest wording "
                "available returned 0 of 16 frames with two correct leaves -- "
                "and the instrument that works is the composite, now five for "
                "five, with last night's beat-19 result adding the piece this "
                "rung actually needs: a hand-drawn COMPOSITED object survives "
                "i2v motion.\n\n"
                "ONE VARIABLE: the init. The crop step's --src and --sha256 "
                "move from the shared 12-related-r4-s2 plate to this beat's "
                "own naturalised composite. The motion prompt is carried BYTE "
                "FOR BYTE, because neither beat has a motion fault worth "
                "rewording and changing the sentence too would make the result "
                "unattributable. $0, ~5 GPU minutes."
                % (row["beat"], row["was"])),
        },
        overrides={
            "key:priority": 16,
        },
        extra={
            "bar": bar_for(row),
            "the_one_variable": (
                "THE INIT, and it is exactly two strings: the crop step's "
                "--src and its --sha256. Driver, size, frame count, fps, "
                "guidance, seed, the motion prompt, the negative, the encode "
                "and render job json and the publish step are the parent's, "
                "unedited. --selftest asserts the old plate and its sha are "
                "ABSENT from the child and the new ones present, and asserts "
                "the motion prompt payload is byte-identical to the parent's, "
                "because 'one variable' is a claim a test should be able to "
                "fail."),
            "init_provenance": (
                "farm-out/%s/%s, 704x1280, sha256 %s. Produced this morning by "
                "the 0.30 masked naturalize (ep2-b%02d-sapnat2-0822) over a "
                "composite cut by pipeline/beat16_sapling_composite.py, which "
                "erased the old plant out of the pixels and drew the canon "
                "two-leaf sapling in its place. THE SOURCE FRAME UNDER ALL OF "
                "THAT IS f000 OF THIS BEAT'S SHIPPED TAKE, not its render "
                "plate: neither beat renders its init (b12's take abandons the "
                "macro plate by f006, and beat 21's verdict records 'from f007 "
                "the init is entirely gone'), so the picture worth correcting "
                "is the one the model settled on. The file is on the box "
                "already -- its own publish step put it in the courier -- so "
                "this job needs no fetch."
                % (row["nat"], row["png"], row["sha"], row["beat"])),
            "not_done_on_purpose": (
                "THE ACTION SENTENCE IS NOT TOUCHED and neither beat's "
                "shipping fault is addressed here. Beat 12's sapling grows "
                "against an approved 'perfectly still'; beat 21 has no fault "
                "but the plant. Both are worth RE-MEASURING on a new init "
                "before anything in the wording moves, and a rung that changed "
                "the plate and the words together could not tell which one "
                "did it."),
        },
        by="pipeline/derive_ep2_leafmotion_0822.py",
    )

    steps, hit = [], 0
    for st in child.get("steps") or []:
        argv = [str(a) for a in (st.get("argv") or [])]
        if st.get("name") == "crop":
            if OLD_SRC not in argv or OLD_SHA not in argv:
                raise SystemExit("!! beat %d: the parent's crop step does not "
                                 "name the shared plate and its sha where "
                                 "expected: %r" % (row["beat"], argv))
            argv = [new_src(row) if a == OLD_SRC else
                    (row["sha"] if a == OLD_SHA else a) for a in argv]
            hit += 1
            st = dict(st, argv=argv)
        steps.append(st)
    if hit != 1:
        raise SystemExit("!! beat %d: expected exactly one crop step, hit %d"
                         % (row["beat"], hit))
    child["steps"] = steps
    return child


def _selftest():
    for row in ROWS:
        spec = build(row)
        blob = derive_spec.dumps(spec) if hasattr(derive_spec, "dumps") else str(spec)
        assert OLD_SRC not in blob, "beat %d: the old plate survived" % row["beat"]
        assert OLD_SHA not in blob, "beat %d: the old sha survived" % row["beat"]
        crop = [s for s in spec["steps"] if s.get("name") == "crop"][0]
        argv = [str(a) for a in crop["argv"]]
        assert new_src(row) in argv and row["sha"] in argv
        # THE ACTION IS UNTOUCHED, and this is the assertion that makes "one
        # variable" a testable claim rather than a sentence in the spec.
        parent = derive_spec.load(os.path.join(REPO, row["parent"]))
        pk = [k for k in parent["payload"] if k.endswith("motion-prompt.txt")]
        ck = [k for k in spec["payload"] if k.endswith("motion-prompt.txt")]
        assert len(pk) == len(ck) == 1, (pk, ck)
        assert parent["payload"][pk[0]] == spec["payload"][ck[0]], (
            "beat %d: the motion prompt is not byte-identical to the parent's"
            % row["beat"])
        nk = [k for k in parent["payload"] if k.endswith("negative.txt")]
        cn = [k for k in spec["payload"] if k.endswith("negative.txt")]
        assert parent["payload"][nk[0]] == spec["payload"][cn[0]]
        print("SELFTEST OK  %-24s init=%s  action carried verbatim"
              % (row["new_id"], row["sha"][:12]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    _selftest()
    if not a.write:
        print("dry run -- nothing written. Pass --write.")
        return 0
    for row in ROWS:
        p = derive_spec.write(build(row), "pipeline/jobs/%s.yaml" % row["new_id"],
                              force=a.force)
        print("wrote", os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
