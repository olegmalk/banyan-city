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

# ROUND 2 FOR BEAT 12 ONLY, AND IT IS A WORDING EDIT THE CLIP ASKED FOR.
# r1 held canon's two leaves for all 121 frames and still broke the approved
# line: "perfectly still". Reading the prompt it inherited explains it exactly
# -- the parent's action sentence says "THE LEAVES STIR GENTLY IN A LIGHT
# BREEZE -- they lift and settle and turn a little on their stalks, the whole
# plant breathing rather than thrashing, while the clouds behind them drift
# very slowly." The clip did precisely that. r1 carried it byte for byte ON
# PURPOSE, so that the plate change could be judged alone; now that it has
# been, the sentence is the variable.
STIR_OLD = ("THE LEAVES STIR GENTLY IN A LIGHT BREEZE \u2014 they lift and "
            "settle and turn a little on their stalks, the whole plant "
            "breathing rather than thrashing, while the clouds behind them "
            "drift very slowly. Nothing else moves and the plant stays exactly "
            "where it is in frame.")
# ROUND 2's TEXT, KEPT SO ITS RESULT STAYS REPRODUCIBLE FROM THIS FILE.
STIR_R2 = ("THE SAPLING IS COMPLETELY STILL. It does not sway, lift, settle, "
           "turn or breathe; not one leaf moves and the stem does not bend. "
           "ONLY THE CLOUDS BEHIND IT DRIFT, very slowly. The plant stays "
           "exactly where it is in frame and holds its shape from the first "
           "frame to the last.")
# ROUND 3, AND IT IS r2's NULL READ FORWARD RATHER THAN r2 TRIED HARDER.
# r2 banned the movement the prompt named and the model spent the budget on the
# one it did not: 340 px of GROWTH against r1's zero. So round 3 KEEPS r1's
# breeze verbatim -- r1 is the take that measured zero climb, and removing its
# one working clause is what went wrong -- and adds the sentence nobody has
# ever put in this prompt: the stem does not lengthen and the plant does not
# get taller. Name the thing that must not move.
STIR_NEW = ("THE LEAVES STIR GENTLY IN A LIGHT BREEZE \u2014 they lift and "
            "settle and turn a little on their stalks, the whole plant "
            "breathing rather than thrashing, while the clouds behind them "
            "drift very slowly. THE SAPLING DOES NOT GROW: the stem does not "
            "lengthen, the plant does not get taller, and the tips of the two "
            "leaves are at the same height in the last frame as in the first. "
            "Nothing else moves and the plant stays exactly where it is in "
            "frame.")

# BEAT 21 ROUND 2. r1's clip tilts beautifully and grows a THIRD BLADE in the
# last second, and reading the sentence it inherited explains why: it was
# written for the lance plate and it says "NOTHING IN THE FRAME MOVES EXCEPT
# THIS ONE LEAF ... the other leaves do not move at all". On a two-leaf sapling
# "this one leaf" and "the other leaves" are both false, and the second phrase
# positively asserts that other leaves exist. Round 2 rewrites exactly that
# clause for the plant that is now in the plate and names the count that must
# not change -- which is the b12 finding applied: name the thing that must not
# move, do not merely ban movement.
TILT_OLD = ("THE AIR IS DEAD STILL AND NOTHING IN THE FRAME MOVES EXCEPT THIS "
            "ONE LEAF: slowly and deliberately it TILTS, turning steadily over "
            "on its stalk through a small clear arc, and then it HOLDS in the "
            "new position and stays there, still. The movement is smooth, "
            "purposeful and one-directional \u2014 not a flutter, not a wobble, "
            "not wind. The stem below it does not sway and the other leaves do "
            "not move at all.")
TILT_NEW = ("THE AIR IS DEAD STILL AND NOTHING IN THE FRAME MOVES EXCEPT THIS "
            "ONE SEEDLING: slowly and deliberately the whole little plant "
            "TILTS, leaning steadily over through a small clear arc, and then "
            "it HOLDS in the new position and stays there, still. The movement "
            "is smooth, purposeful and one-directional \u2014 not a flutter, "
            "not a wobble, not wind. THE PLANT HAS EXACTLY TWO LEAVES AND KEEPS "
            "EXACTLY TWO: no third leaf grows, no leaf splits, and the two "
            "blades are the same two, the same shape, in the last frame as in "
            "the first.")

ROWS = [
    {
        "beat": 12,
        "parent": "pipeline/jobs/ep2-b12-tightB-0813.yaml",
        "parent_id": "ep2-b12-tightB-0813",
        "new_id": "ep2-b12-nogrow-r3-0822",
        "dirtok": "ep2-b12-tightB-0813",
        "pubdir": "ep2-b12-tightB",
        "nat": "ep2-b12-sapnat2-0822",
        "png": "b12-sapnat2-s20260820.png",
        "sha": "dcc042b8e21f0ded82adb5401186f69a2b8d78aa92eb398eb74631bcfac5ea5a",
        "was": "TWO PERFECT ROUND DISCS on one stem",
        "stir": True,
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
        "new_id": "ep2-b21-twoleaf-r2-0822",
        "dirtok": "ep2-b21-daylight-0814",
        "pubdir": "ep2-b21-daylight-0814",
        "nat": "ep2-b21-sapnat2-0822",
        "png": "b21-sapnat2-s20260820.png",
        "sha": "859243c1813812cad87cf2428b5e9068dbdf085cb7a066882164de0420461fc3",
        "was": "ONE GIANT LANCE-SHAPED LEAF standing straight up",
        "tilt_r2": True,
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

    for flag, old_t, new_t in (("stir", STIR_OLD, STIR_NEW),
                               ("tilt_r2", TILT_OLD, TILT_NEW)):
        if not row.get(flag):
            continue
        pay = dict(child.get("payload") or {})
        pk = [k for k in pay if k.endswith("motion-prompt.txt")]
        if len(pk) != 1:
            raise SystemExit("!! beat %d: expected one motion prompt" % row["beat"])
        if old_t not in pay[pk[0]]:
            raise SystemExit("!! beat %d: the %s clause is not in the parent "
                             "payload verbatim -- refusing to guess"
                             % (row["beat"], flag))
        pay[pk[0]] = pay[pk[0]].replace(old_t, new_t)
        child["payload"] = pay
    if False:
        pay = dict(child.get("payload") or {})
        pk = [k for k in pay if k.endswith("motion-prompt.txt")]
        if len(pk) != 1:
            raise SystemExit("!! beat %d: expected one motion prompt" % row["beat"])
        if STIR_OLD not in pay[pk[0]]:
            raise SystemExit("!! beat %d: the stir clause is not in the parent "
                             "payload verbatim -- refusing to guess"
                             % row["beat"])
        pay[pk[0]] = pay[pk[0]].replace(STIR_OLD, STIR_NEW)
        child["payload"] = pay
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
        swap = ((STIR_OLD, STIR_NEW) if row.get("stir")
                else (TILT_OLD, TILT_NEW) if row.get("tilt_r2") else None)
        if swap:
            STIR_OLD_, STIR_NEW_ = swap
            # THE ROUND'S ONE VARIABLE IS THIS CLAUSE AND NOTHING ELSE. Asserted
            # both ways: the new sentence is in and the old one is out, and the
            # rest of the prompt is byte-identical either side of the swap.
            a_, b_ = parent["payload"][pk[0]], spec["payload"][ck[0]]
            assert STIR_OLD_ in a_ and STIR_OLD_ not in b_
            assert STIR_NEW_ in b_
            assert a_.replace(STIR_OLD_, STIR_NEW_) == b_, (
                "beat %d: something other than the stir clause moved"
                % row["beat"])
        else:
            assert parent["payload"][pk[0]] == spec["payload"][ck[0]], (
                "beat %d: the motion prompt is not byte-identical to the "
                "parent's" % row["beat"])
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
