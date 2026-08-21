#!/usr/bin/env python3
r"""MOTION FOR THE FIVE BEATS THE GOBLIN-DESIGN SWEEP JUST ADDED.

    python3 pipeline/file_sweepmotion_0822.py            # dry run
    python3 pipeline/file_sweepmotion_0822.py --write --beats 14,15,16

WHY THESE FIVE EXIST AT ALL. The patch wave was seven beats picked by an audit.
The founder's 2026-08-21 beat-by-beat pass said "old man goblin. very wrong" of
14, 15, 16, 17, 19 and 20, so the wave is now every beat he is visible in, and
pipeline/jerry_canon_0821.py carries five new rows. Their plates rendered and
were opened at 1:1 before a single motion job was filed: 14, 15 and 16 came
back as his design -- bald, large lateral pointed ears, off-white eyes with
slit pupils, mandarin collar, dark shorts, boots, no human nose and no old-man
folds -- and 17 and 19 came back with a CROWD of extra goblin figures standing
in the grass behind him, which is a `solo` violation and is being re-plated
(w2b) rather than animated.

THE RECIPE IS BEAT 04's, WHOLESALE, AND NOTHING ABOUT IT IS BEING ASKED HERE.
704x1280, 105 frames at 24fps, guidance 2.0, distilled sigmas, two-stage, crf
10, sequential offload, cover_crop asserting the plate's digest before an init
frame is written. Beat 04 is the parent because it is the wave's cleanest pass
(6 of 7) and because its instruction names only body verbs -- the one shape of
prompt this engine has been measured NOT re-staging itself around.

THE ONE THING THAT MOVES PER BEAT is the init plate and the sentence that
describes what he does in it. Both come from node.md, and both are written to
the two laws this wave has already paid for:

  * NAME NOTHING THE PLATE DOES NOT CONTAIN. Four beats in round 1 named an
    absent object and all four pulled the camera back hunting for it. So no
    action here names the sapling, the fig, a trunk or a guard -- these are
    single-figure body actions on single-figure plates.
  * AN ACTION NEEDS A START, A MIDDLE AND AN END. Beat 03 round 2 asked for
    "hold still" and got a still with a runtime. Every action below names a
    HALFWAY state, because that is the clause the wave has measured binding.
"""
import argparse
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                            # noqa: E402
import yaml as _yaml                                          # noqa: E402

PARENT = "pipeline/jobs/ep2-b04-canonmotion-0821.yaml"
BOX_PLATE = (r"C:\banyan-farm\courier-box\farm-out\ep2-b%02d-canon-w2-0821"
             r"\ep2-b%02d-canon-w2-0821-ipahead.png")
REL_PLATE = ("farm-out/ep2-b%02d-canon-w2-0821/"
             "ep2-b%02d-canon-w2-0821-ipahead.png")

SLUG = {14: "the-defense", 15: "good-listener", 16: "why"}

ROWS = {
    14: dict(
        pose="kneeling, picking at the dirt with one hand, in tall grass, "
             "full body",
        action=(
            "THE ACTION: he scratches at the dirt in front of him with the "
            "fingers of one hand, twice, and between the two he glances up "
            "and away to his side and back down again. HALFWAY THROUGH his "
            "head is up and turned away, his hand still down in the dirt."),
        script=("THE DEFENSE -- 'He picks at the dirt, embarrassed, glancing "
                "around.' Line: 'It was ONE apple. It fell off the cart. On "
                "the ground, that's -- that's foraging.'"),
        bar=("D1 the hand at the dirt moves more than once; D2 the head "
             "turns away and comes back; D3 identity holds in every frame; "
             "D4 the frame does not pull back and he does not shrink."),
    ),
    15: dict(
        pose="squatting, head tilted down and sideways, in tall grass, "
             "full body",
        action=(
            "THE ACTION: he tips his head further down and over to one side, "
            "bringing it low and close to the ground in front of him, holds "
            "it there while he talks -- his jaw moving -- and then lifts it "
            "part of the way back. HALFWAY THROUGH his head is at its lowest "
            "and most tilted, mouth moving."),
        script=("GOOD LISTENER -- 'He tips his head down and sideways until "
                "his eyes are level with the two leaves, and talks to them "
                "from a hand's width away.' Line: 'You're a good listener.'"),
        bar=("L1 the head tips further down and sideways than it starts and "
             "the tilt is visible; L2 the mouth moves; L3 identity holds; L4 "
             "the frame does not pull back. NOTE: the two leaves are NOT "
             "named in the action, because they are not in this plate -- the "
             "framing that puts him level with them is the assembly's "
             "problem and naming them here is how four beats lost their "
             "camera in round 1."),
    ),
    16: dict(
        pose="sitting, in tall grass, full body",
        action=(
            "THE ACTION: he breathes -- his shoulders rise and settle twice "
            "-- and his head drifts slowly to one side and back to centre "
            "over the whole clip. Nothing else moves. HALFWAY THROUGH his "
            "head is over to one side, shoulders down."),
        script=("WHY -- 'Close on the sapling's leaf; the scavenger sits "
                "blurred behind it.' He has no line here; the tree does. He "
                "is the still figure in the background of somebody else's "
                "close-up."),
        bar=("W1 the shoulders move at least twice; W2 the head travels off "
             "centre and returns; W3 identity holds; W4 the frame does not "
             "pull back. THIS BEAT IS ALLOWED TO BE QUIET -- it is the one "
             "shot in the episode where the goblin is deliberately not the "
             "subject -- but 'quiet' is not 'a still with a runtime', which "
             "is the outcome beat 03 round 2 filed under that name."),
    ),
}


def sha_of(rel: str) -> str:
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build(beat: int, pspec: dict):
    row = ROWS[beat]
    pkey = [k for k in pspec["payload"] if "motion-prompt" in k][0]
    parent_prompt = pspec["payload"][pkey]
    head = parent_prompt[:parent_prompt.index("He is ")]
    prompt = head + "He is " + row["pose"] + ". " + row["action"]

    rel = REL_PLATE % (beat, beat)
    plate_sha = sha_of(rel)
    new_id = "ep2-b%02d-canonmotion-0822" % beat

    child = derive_spec.derive(
        PARENT, new_id,
        fresh={
            "owner": "the per-beat iteration lane, 2026-08-22",
            "consumer":
                "A CANDIDATE for beat %02d on review/ep2-beats-0821, and the "
                "first clip of this beat drawn on the founder's own design. "
                "review/ep2-ship-0821 is not touched and no cut moves because "
                "it landed." % beat,
            "success":
                "ONE 704x1280 105-frame 24fps mp4 of the CANON creature doing "
                "the beat. %s The named degenerate outcome is A STILL WITH A "
                "RUNTIME, which is how beat 03 round 2 failed on a plate that "
                "already contained everything its prompt named; the HALFWAY "
                "clause and the two-event actions above are written against "
                "it." % row["bar"],
            "why":
                "THE FOUNDER LOOKED AT THIS BEAT ON 2026-08-21 AND SAID 'old "
                "man goblin. very wrong'. He said it of five beats, and the "
                "design-patch wave -- seven beats an audit had picked -- did "
                "not contain any of them. It does now: "
                "pipeline/jerry_canon_0821.py carries a row for this beat "
                "with its own skeleton pose, its own pose words out of "
                "node.md and one emotion tag, and its plate rendered and was "
                "opened at 1:1 before this spec was written. It came back as "
                "his creature: bald, large lateral pointed ears, off-white "
                "eyes with slit pupils, mandarin collar, dark shorts, boots, "
                "no human nose, no folds at the mouth.\n\nSTAGING, FROM THE "
                "APPROVED SCRIPT: %s\n\nTHE ACTION NAMES NOTHING THE PLATE "
                "DOES NOT CONTAIN. That is the wave's own measured law -- "
                "four of seven round-1 beats named an absent object and all "
                "four pulled the camera back building it -- so this is a "
                "single figure doing body verbs on a single-figure plate, "
                "and any prop or second character the beat needs is the "
                "assembly's problem, not the sampler's."
                % row["script"],
        },
        overrides={
            "argv:--src": BOX_PLATE % (beat, beat),
            "argv:--sha256": plate_sha,
            "payload:b%02d-motion-prompt.txt" % beat: prompt,
            "key:beat": beat,
            "key:priority": 13,
            "seed": 20260850 + beat,
        },
        extra={
            "the_one_variable":
                "THE BEAT. The recipe is beat 04's wholesale -- same size, "
                "frames, fps, guidance, sampler, sigmas, two-stage, crf, "
                "offload and cover-crop assert -- and the identity clause is "
                "carried byte-for-byte, so a frame that misses is "
                "attributable to this beat's plate or this beat's action and "
                "to nothing else.",
            "plate_provenance":
                "%s, 832x1216, sha256 %s, rendered by ep2-b%02d-canon-w2-0821 "
                "from the founder-canon recipe (openpose skeleton at head_frac "
                "0.370 + IP-Adapter on jerry-canon-sq45-0821) and OPENED AT "
                "1:1 before this spec existed. cover_crop.py asserts that "
                "digest before it writes an init frame."
                % (rel, plate_sha, beat),
            "not_done_on_purpose":
                "BEATS 17 AND 19 ARE NOT IN THIS TRANCHE. Their plates "
                "rendered in the same pass and came back with a crowd of "
                "extra goblin figures standing in the grass behind him -- a "
                "`solo` violation on a recipe whose whole point is one "
                "canonical creature. They are re-plating as w2b with `second "
                "goblin, crowd` added to the negative, and their motion waits "
                "for a plate worth animating. Beat 20 already has a canon "
                "plate and a round-2 clip and is not re-run here.",
        },
        retoken=[("ep2-b04-canonmotion-0821", "ep2-b%02d-canonmotion-0822"
                  % beat),
                 ("04-evidence", "%02d-evidence" % beat),
                 ("b04-", "b%02d-" % beat)],
        by="pipeline/file_sweepmotion_0822.py",
    )
    return child, prompt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--beats", default="14,15,16")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    pspec = _yaml.safe_load(open(os.path.join(REPO, PARENT), encoding="utf-8"))
    for beat in [int(b) for b in a.beats.split(",")]:
        if beat not in ROWS:
            raise SystemExit("!! beat %d has no row in this filer" % beat)
        child, prompt = build(beat, pspec)
        blob = _yaml.safe_dump({k: v for k, v in child.items()
                                if k != "derivation"})
        if "b04-" in blob or "04-evidence" in blob:
            raise SystemExit("!! beat %02d: a beat-04 token survived "
                             "retokening" % beat)
        out = "pipeline/jobs/%s.yaml" % child["id"]
        print("%-28s beat %02d  prompt %d chars  %d step(s)"
              % (child["id"], beat, len(prompt), len(child["steps"])))
        if a.write:
            path = derive_spec.write(child, out, force=a.force)
            print("   wrote %s" % os.path.relpath(path, REPO))
    if not a.write:
        print("\n-- dry run. re-run with --write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
