#!/usr/bin/env python3
r"""ROUND 2 OF THE CANON-MOTION WAVE: the same beats, on plates that now CONTAIN
the object their prompt names.

    python3 pipeline/file_canonmotion_r2_0821.py            # dry run
    python3 pipeline/file_canonmotion_r2_0821.py --write

THE LAW, MEASURED IN ROUND 1 AND ACTED ON HERE
--------------------------------------------------------------------------
Round 1 filed seven i2v jobs on the founder-image canon plates, one variable
(frame count 121 -> 105) held across all seven, and every one was judged by
eye. Three passed and four failed, and the split is not the recipe -- it is
the init:

  PASSED  04, 08, 13. Each asks only for motion the plate already has a body
          for. All three held the frame for 105 frames.
  FAILED  02, 03, 07, 20. Each names something the plate does not contain --
          a thin sapling trunk (02, 03), a branch (20), a second figure (07)
          -- and in every one of the four THE CAMERA PULLED BACK. b02: "a
          speck at bottom right of a wide shot dominated by a large bare tree
          that is in no plate". b03: "his height roughly halves by f104".
          b07: "the camera also pulls back at f024 to fit the second figure".
          b20: "a branch enters at top right from ~f048".

So: A PROMPT NAMING AN OBJECT ABSENT FROM THE INIT MAKES THE MODEL BUILD THE
OBJECT AND RE-FRAME THE SHOT TO FIT IT. Round 1's own b02 verdict wrote the
next rung before this file existed -- "Next rung is a plate that already holds
the trunk, not a reworded prompt."

WHAT CHANGED BETWEEN THE ROUNDS, AND IT IS ONE THING
--------------------------------------------------------------------------
THE INIT PLATE. Beats 02, 03 and 20 now run on the naturalised composites
filed by pipeline/derive_ep2_sapnat_0821.py and judged before this was
written: the scripted object was composited onto the same canon w2 plate and
drawn in by a 0.30 masked i2i. Measured on landing -- mean absolute delta
INSIDE the mask 10.2 to 14.2 (the plant was genuinely redrawn), OUTSIDE the
mask 0.024 to 0.055 (the goblin was not touched at all), and the plant's
centroid moved 0.1 to 5.4 px on an 832x1216 frame (it did not move).

Everything the recipe consists of is round 1's by copy: 704x1280, 105 frames
at 24fps, the same seed per beat, the same guidance, sampler, sigmas, two-
stage, crf and offload, the same cover_crop-with-sha-assert, the same trim
plan. Not one sampler number moves.

THE PROMPT MOVES ONLY WHERE THE LAW SAYS IT MAY. The object is promoted out of
THE ACTION and into the "Subject already in frame" clause, because it now IS
already in frame -- that clause is the model's inventory of what exists, and
listing the sapling there is the difference between "finish this shot" and
"build me one". THE ACTION then refers to it as a thing that is already there.
This is not a rewording ladder: round 1 proved wording alone cannot fix it,
and the plate is what changed.

BEAT 07 IS DELIBERATELY ABSENT. Its two-figure plate rendered and was judged
in the same pass: the guard is right -- five heads, armoured, a grown man per
the founder's ruling -- but the GOBLIN lost his slit pupils and his mandarin
collar to a loose IP-Adapter mask. Filing a motion job on a plate whose
character is off-canon would spend GPU time animating the wrong face. b07
goes back for a round-2 plate first.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                            # noqa: E402

BOX_PLATE = (r"C:\banyan-farm\courier-box\farm-out\ep2-b%02d-sapnat-0821"
             r"\b%02d-sapnat-s20260820.png")

ROWS = [
    {
        "beat": 2,
        "sha": "30dce0fabd444fdf5e0727eb4c6a317d65004f71a7df0dbe5cb126224dbf46ea",
        "inventory": (
            " A THIN BARE SAPLING STEM WITH TWO LEAVES is also already in "
            "frame, rooted in the grass in front of him, and it stays where it "
            "is for the whole clip."),
        "action": (
            "THE ACTION: he runs in from the left, skids, and drops down "
            "behind the sapling stem that is already there -- entry, skid, "
            "dive, in that order, as one continuous move. HALFWAY THROUGH he "
            "is mid-skid, still upright, leaning back, not yet down."),
        "was": (
            "the camera pulled back until he was 'a speck at bottom right of a "
            "wide shot dominated by a large bare tree that is in no plate', "
            "and no sprint, skid or dive happened at all"),
    },
    {
        "beat": 3,
        "sha": "e59f177e01891bd32962dfd861478ab3ece74af248038a0e4fd8df34d6f4637f",
        "inventory": (
            " A THIN BARE SAPLING STEM WITH TWO LEAVES is also already in "
            "frame, rooted in the grass directly in front of him and crossing "
            "his body, and it stays where it is for the whole clip."),
        "action": (
            "THE ACTION: he crouches low behind the thin stem that is already "
            "there and holds still, eyes flicking sideways -- the cover is "
            "comically inadequate and he believes it is working. HALFWAY "
            "THROUGH he is all the way down behind the stem and still, eyes "
            "turned to one side."),
        "was": (
            "the camera pulled back from ~f072 and his height roughly halved "
            "by f104, no trunk was ever drawn, and a curved horn grew from the "
            "crown of his bald head from about f072"),
    },
    {
        "beat": 20,
        "sha": "f8ffa9f24bfa3a9f8077dcc043326eee20dcb4752593227d1346a86f2f49be36",
        "inventory": (
            " A SMALL ROUND PURPLE FIG is already closed in both his hands, "
            "and A THIN SAPLING STEM WITH TWO LEAVES is already in frame "
            "beside him at the right, at about his eye line. Both stay where "
            "they are for the whole clip."),
        "action": (
            "THE ACTION: he lifts the fig in both hands and turns his head up "
            "from it to the sapling stem already beside him -- THE LOOK UP "
            "COMPLETES, and it is the whole beat. HALFWAY THROUGH his head is "
            "up off the fruit and turning, the fruit still closed in both "
            "hands."),
        "was": (
            "he never looked up, the pose barely changed between f000 and "
            "f104 -- 'close to a still with a runtime' -- a branch entered by "
            "itself at top right from ~f048, and the fig was yellow-green "
            "where canon has it purple"),
    },
]


def head_of(prompt: str) -> tuple:
    """Split round 1's prompt at THE ACTION. The identity clause is carried
    BYTE-FOR-BYTE: it is the founder's canon wording and round 1 proved it
    holds the face for 105 frames on all seven beats."""
    i = prompt.index("THE ACTION:")
    return prompt[:i].rstrip(), prompt[i:]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    import hashlib
    import yaml as _yaml

    for row in ROWS:
        beat = row["beat"]
        parent = "pipeline/jobs/ep2-b%02d-canonmotion-0821.yaml" % beat
        new_id = "ep2-b%02d-canonmotion-r2-0821" % beat

        rel = ("farm-out/ep2-b%02d-sapnat-0821/b%02d-sapnat-s20260820.png"
               % (beat, beat))
        with open(os.path.join(REPO, rel), "rb") as fh:
            have = hashlib.sha256(fh.read()).hexdigest()
        if have != row["sha"]:
            raise SystemExit("!! %s hashes %s, this filer names %s"
                             % (rel, have, row["sha"]))

        pspec = _yaml.safe_load(open(os.path.join(REPO, parent),
                                     encoding="utf-8"))
        pkey = [k for k in pspec["payload"] if "motion-prompt" in k][0]
        head, _old_action = head_of(pspec["payload"][pkey])
        prompt = head + row["inventory"] + " " + row["action"]

        child = derive_spec.derive(
            parent, new_id,
            fresh={
                "owner": "canon-motion plate-fix lane, 2026-08-21",
                "consumer": (
                    "A ROUND-2 CANDIDATE for beat %02d, and the test of the "
                    "wave's one generalisation. review/ep2-ship-0821 is NOT "
                    "touched by this job: the clip is a candidate until the "
                    "founder rules, and no cut changes because it landed. Its "
                    "other consumer is the law itself -- three beats that "
                    "failed the same way, re-run with the same recipe on "
                    "plates that now hold the object, is the cleanest test "
                    "available of whether the init was the cause." % beat),
                "success": (
                    "ONE 704x1280 105-frame 24fps mp4 in which THE FRAME DOES "
                    "NOT PULL BACK and the action completes inside the trim. "
                    "R1 the goblin's height at f104 is within a few percent of "
                    "his height at f000 -- that is the whole hypothesis and it "
                    "is measurable, not a matter of taste; R2 the sapling that "
                    "is in the init is still there at f104 and has not been "
                    "replaced by a large tree; R3 the action named in THE "
                    "ACTION completes by f096, the last frame a 97-frame trim "
                    "keeps; R4 face, ears, skin colour and clothes are the "
                    "canon plate's in every frame, with no dissolve and no new "
                    "appendage. The named degenerate outcome is A STILL WITH A "
                    "RUNTIME: an init that now contains everything the prompt "
                    "names gives the model less reason to move at all, which "
                    "is exactly how beat 20 failed in round 1. R3 is what "
                    "catches it."),
                "why": (
                    "BEAT %02d FAILED ROUND 1 PLATE-SIDE, AND THIS IS THE SAME "
                    "RECIPE ON A PLATE THAT NOW HOLDS WHAT THE PROMPT "
                    "NAMES.\n\nROUND 1, IN ITS OWN VERDICT: %s.\n\nThat is one "
                    "of four identical failures. The other three beats in the "
                    "wave -- 04, 08 and 13 -- asked only for motion their "
                    "plates had a body for, and all three held the frame. So "
                    "the generalisation the wave supports is that a prompt "
                    "naming an object ABSENT from the init makes the model "
                    "build it and pull the camera back hunting for it, and the "
                    "lever is the init.\n\nWHAT CHANGED: the init, and one "
                    "clause of wording that follows from it. The plate is the "
                    "naturalised composite from ep2-b%02d-sapnat-0821, judged "
                    "before this spec was written -- mean absolute delta "
                    "inside the drawn region 10-14, outside it 0.02-0.06, "
                    "centroid moved under 6 px, so the object is genuinely "
                    "drawn and the goblin is genuinely untouched. The object "
                    "moves out of THE ACTION and into the 'Subject already in "
                    "frame' inventory, because it now is. The identity clause "
                    "is carried byte-for-byte from round 1, which held the "
                    "face for 105 frames on all seven beats.\n\nWHAT DID NOT "
                    "CHANGE: size, frame count, fps, seed, guidance, sampler, "
                    "sigmas, two-stage, crf, offload, the cover-crop sha "
                    "assert and the trim plan. Round 1 already proved the "
                    "recipe; it did not prove the plate."
                    % (beat, row["was"], beat)),
            },
            overrides={
                "argv:--src": BOX_PLATE % (beat, beat),
                "argv:--sha256": row["sha"],
                "payload:b%02d-motion-prompt.txt" % beat: prompt,
                "key:priority": 14,
            },
            extra={
                "the_one_variable": (
                    "THE INIT PLATE, and the single prompt clause that follows "
                    "from it. Round 1 held the frame count constant across "
                    "seven beats to ask one question; this round holds the "
                    "ENTIRE recipe constant across three beats to ask a "
                    "different one -- was the init the cause? Same 704x1280, "
                    "same 105 frames at 24fps, same seed, same guidance, "
                    "sampler, sigmas, two-stage, crf and offload, same "
                    "cover_crop.py asserting a sha before a frame is written, "
                    "same trim-to-97 plan. The only wording change is that the "
                    "object moves from THE ACTION into the 'Subject already in "
                    "frame' inventory, which is a statement of fact about the "
                    "new init and not a rewording ladder -- round 1 proved "
                    "wording alone cannot fix this."),
                "plate_provenance": (
                    "%s, 832x1216, sha256 %s, cover-cropped to 704x1280 by "
                    "cover_crop.py which asserts that digest before it writes "
                    "an init frame. Produced by ep2-b%02d-sapnat-0821 (rc=0) "
                    "from the SAME canon w2 plate round 1 used, with the "
                    "scripted object composited in and drawn by a 0.30 masked "
                    "i2i. The plate is committed on origin/main and published "
                    "to the box's courier farm-out by that job's own publish "
                    "step, so both sides hold it and they hash identically."
                    % (rel, row["sha"], beat)),
                "failure_predicted_in_advance": (
                    "A STILL WITH A RUNTIME, and it is the specific cost of "
                    "this fix. Round 1's beat 20 verdict already named it -- "
                    "'between f000 and f104 the pose barely changes, which is "
                    "close to a still with a runtime'. An init that contains "
                    "everything the prompt names removes the model's reason to "
                    "invent, and inventing is also what was making things "
                    "move. If the frame now holds but nothing happens, the law "
                    "is confirmed and the next lever is the action wording, "
                    "not the plate. R3 is the bar that separates those two "
                    "outcomes and it is why it is written as a frame number "
                    "rather than an impression. SECOND, CHEAPER: the model "
                    "redraws the composited sapling in its own dialect mid-"
                    "clip, so it drifts or grows leaves. R2 catches it."),
                "not_done_on_purpose": (
                    "BEAT 07 IS NOT IN THIS TRANCHE. Its two-figure plate "
                    "rendered rc=0 in the same pass and was judged: the guard "
                    "passes -- five heads, armoured, helmeted, a grown man per "
                    "the founder's 2026-08-20 ruling -- and the IP-Adapter did "
                    "not leak onto him. But the GOBLIN came back with round "
                    "green eyes instead of the canon narrow vertical slit "
                    "pupils, and a plain crew-neck tee instead of the mandarin "
                    "collar. Animating an off-canon character is a worse use "
                    "of the card than re-rendering a plate, so b07 goes back "
                    "for a round-2 plate with a tighter IP mask and the "
                    "motion spec waits for it. NOTHING HERE TOUCHES THE CUT."),
            },
            by="pipeline/file_canonmotion_r2_0821.py",
        )

        blob = _yaml.safe_dump({k: v for k, v in child.items()
                                if k != "derivation"})
        if row["sha"] not in blob or "sapnat" not in blob:
            raise SystemExit("!! beat %02d: the new plate did not reach the "
                             "child spec" % beat)

        out = "pipeline/jobs/%s.yaml" % new_id
        print("%-28s plate %s..  prompt %d chars"
              % (new_id, row["sha"][:12], len(prompt)))
        if a.write:
            path = derive_spec.write(child, out, force=a.force)
            print("   wrote %s" % os.path.relpath(path, REPO))

    if not a.write:
        print("\n3/3 derived, plates re-hashed. -- dry run. re-run with --write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
