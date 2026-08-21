#!/usr/bin/env python3
r"""BEAT 10: TWO BOARDS THAT STAY TWO BOARDS.

    python3 pipeline/derive_b10_twoboards_0822.py            # dry run
    python3 pipeline/derive_b10_twoboards_0822.py --write

THE FOUNDER'S NOTE, 2026-08-22: "the 2 things they were holding shapeshift into
1". Stepped at 24-frame intervals on the SHIPPING clip
(review/ep2-ship-0821/sources/10-no-form-b10-pairB-trim.mp4) and it is exactly
that. At frame 0 there are two boards -- a pale grey-blue one in the near
guard's hand, a dark teal one in his partner's. By frame 48 they have drifted
together; from frame 72 to the end there is ONE tan board held between the two
men.

THE CAUSE IS IN THE PROMPT AND IT IS NOT SUBTLE. The parent's subject clause
describes the partner as "a second guard in the same uniform, standing close
beside him within arm's reach and facing him" -- HE IS GIVEN NOTHING TO HOLD.
The word "board" appears five times in that prompt and every one of them is the
NEAR guard's. So the plate hands the sampler two boards and the sentence hands
it one, and the sampler reconciles the disagreement the cheapest way available:
it deletes one. This is the placement law from the other side -- the wave has
measured four times that a subject the prompt does not PLACE is a subject that
is not drawn, and here the un-placed subject is not absent from the plate, so
instead of failing to appear it is absorbed.

THE PLATE IS NOT THE PROBLEM AND IS NOT BEING RE-RENDERED. Frame 0 already
shows two separate boards in two different colours in two different men's
hands, which is the thing to preserve. Re-plating would put a second variable
in a clip that needs one.

TWO CHANGES, BOTH ON THE WORD SIDE:

  1. THE PARTNER GETS HIS OWN BOARD, named, coloured differently, and asserted
     to stay separate for the whole clip. Colour is named because the two
     boards in the plate ARE different colours and a difference the sentence
     acknowledges is a difference the sampler has a reason to keep.
  2. THE AIM IS CORRECTED IN THE SAME PASS. The page's standing fault on this
     beat is that from frame 65 the near guard holds his board flat to the
     LENS, so his partner would be seeing it edge-on -- and "holds it out to
     his partner" is the clause that IS the beat. The new sentence says the
     blank face is turned toward the PARTNER and away from camera.

Merge terms go in the negative too, but they are not expected to carry the fix
on their own: Ban et al. (ECCV 2024) as this tree keeps citing it -- a negative
acts only after the positive has drawn the thing. The positive above is the fix;
the negative is cheap insurance.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                            # noqa: E402
import yaml as _yaml                                          # noqa: E402

PARENT = "pipeline/jobs/ep2-b10-pairB-0814.yaml"
NEW_ID = "ep2-b10-twoboards-0822"

# The parent's own sentences, kept verbatim where they still describe the beat.
PROMPT = (
    "2D anime, hand-drawn cel animation, static locked framing, the frame "
    "never moves, flat cel shading, clean ink linework, anime key art. "
    "Subject already in frame: THE WHOLE SCENE IS ALREADY DRAWN AND ALREADY "
    "IN THIS FRAME AND IT DOES NOT CHANGE - the green summer field, the "
    "grass, the low hedge, the treeline and the pale sky are all present from "
    "the first frame and stay exactly as they are, unmoving, for the whole "
    "shot. Nothing is added to the background and nothing is redrawn. "
    "TWO UNIFORMED PATROL GUARDS, BOTH GROWN MEN, ARE ALREADY IN THIS FRAME "
    "TOGETHER from the first frame to the last, standing close and facing "
    "each other, and no third man is anywhere in it. "
    "THERE ARE TWO SEPARATE BARK BOARDS IN THIS FRAME AND THERE ARE TWO OF "
    "THEM IN EVERY FRAME. The near guard holds HIS OWN pale grey-blue bark "
    "board in his own two hands. His partner holds HIS OWN dark teal bark "
    "board, a different board, in his own hands, down at his hip. The two "
    "boards are held by different men, they never touch, they never overlap "
    "and they never become one board. Both stay hand-sized. "
    "THE NEAR GUARD FLIPS HIS OWN BOARD OVER AND HOLDS ITS COMPLETELY BLANK "
    "BACK OUT TOWARD HIS PARTNER: he turns his board over, extends it toward "
    "the other man at chest height with the empty back of it ANGLED TOWARD "
    "HIS PARTNER AND AWAY FROM THE CAMERA, shakes it once, and holds it there "
    "while his partner looks at it. His partner keeps his own dark teal board "
    "in his own hands the whole time and does not take the other one. "
    "Neither man walks anywhere and both stay in frame. "
    "Bright clear daylight, cinematic lighting, detailed, newest, masterpiece, "
    "best quality, very aesthetic."
)

NEG_ADD = ("one board, a single board, both men holding the same board, "
           "boards merging, boards overlapping, two objects becoming one, "
           "morphing prop, prop changing shape, prop changing colour, "
           "board flat to camera, board facing the viewer, empty hands")


def build():
    pspec = _yaml.safe_load(open(os.path.join(REPO, PARENT), encoding="utf-8"))
    pkeys = [k for k in pspec["payload"] if "motion-prompt" in k]
    nkeys = [k for k in pspec["payload"] if "negative" in k]
    if len(pkeys) != 1 or len(nkeys) != 1:
        raise SystemExit("!! %s has %d prompt / %d negative payloads"
                         % (PARENT, len(pkeys), len(nkeys)))
    stem = os.path.basename(pkeys[0].replace("\\", "/"))
    stem = stem[:stem.index("-motion-prompt")]          # e.g. 'b05'
    negative = pspec["payload"][nkeys[0]] + ", " + NEG_ADD

    child = derive_spec.derive(
        PARENT, NEW_ID,
        fresh={
            "owner": "the night iteration lane, 2026-08-22",
            "consumer":
                "A CANDIDATE for beat 10 on review/ep2-beats-0821. "
                "review/ep2-ship-0821 is not touched -- the clip in the "
                "episode stays where it is until he picks this one.",
            "success":
                "TWO SEPARATE BOARDS IN EVERY FRAME OF THE CLIP, one in each "
                "man's hands, different colours, never touching and never "
                "resolving into a single object -- checked by stepping the "
                "clip, not by watching it once. AND the blank back of the "
                "near guard's board is angled toward his PARTNER rather than "
                "flat to the lens for the whole hold. Either failure alone is "
                "a fail.",
            "why":
                "THE FOUNDER, 2026-08-22: 'the 2 things they were holding "
                "shapeshift into 1'. Stepped on the shipping clip at 24-frame "
                "intervals: two boards at f0, drifting together by f48, ONE "
                "tan board from f72 to the end. The cause is the parent "
                "prompt, which names a board five times and every one of them "
                "is the near guard's -- the partner is given nothing to hold. "
                "The plate hands the sampler two boards and the sentence "
                "hands it one, so the sampler deletes one. The plate is NOT "
                "re-rendered: f0 already draws two separate boards in two "
                "colours in two men's hands, which is the thing to keep.",
        },
        overrides={
            "payload:%s-motion-prompt.txt" % stem: PROMPT,
            "payload:%s-negative.txt" % stem: negative,
            "key:beat": 10,
            "key:priority": 12,
            "seed": 20260882,
        },
        extra={
            "the_one_variable":
                "THE WORDING. Same plate, same init, same seed family, same "
                "sampler settings as ep2-b10-pairB-0814 -- only the subject "
                "clause and the negative move, so a clip that still merges "
                "the boards falsifies the placement explanation rather than "
                "leaving it arguable.",
            "second_fault_fixed_in_the_same_pass":
                "The page's standing fault on beat 10 is that from f65 to f96 "
                "the board is flat to the LENS, so the partner would see it "
                "edge-on -- and holding it out TO HIS PARTNER is the clause "
                "that IS the beat. The new sentence angles the blank back "
                "toward the partner and away from camera. Two faults in one "
                "spec is a deliberate exception to one-variable: they are the "
                "same sentence, and splitting them would mean rendering the "
                "merge fix with a known-bad aim.",
            "negative_is_insurance_not_the_fix":
                "The merge terms in the negative are cheap and are not "
                "expected to carry this. Ban et al. (ECCV 2024, "
                "arXiv:2406.02965), which this tree has now cited three times "
                "on its own evidence: a negative acts only AFTER the positive "
                "has drawn the thing. The positive is the fix.",
        },
        by="pipeline/derive_b10_twoboards_0822.py",
    )
    return child


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    child = build()
    # Asserted on the PAYLOAD STRING, not on a yaml dump of the spec: safe_dump
    # wraps long scalars, so "AWAY FROM THE CAMERA" arrives in the dump with a
    # newline through it and a substring check on the dump fails on a spec that
    # is perfectly correct. The dump is a rendering; the payload is the thing
    # the sampler reads.
    pkey = [k for k in child["payload"] if "motion-prompt" in k][0]
    emitted = child["payload"][pkey]
    for must in ("TWO SEPARATE BARK BOARDS", "dark teal",
                 "AWAY FROM THE CAMERA"):
        if must not in emitted:
            raise SystemExit("!! the emitted prompt is missing %r" % must)
    nkey = [k for k in child["payload"] if "negative" in k][0]
    if "boards merging" not in child["payload"][nkey]:
        raise SystemExit("!! the emitted negative lost the merge terms")
    out = "pipeline/jobs/%s.yaml" % NEW_ID
    print("%s  beat 10  prompt %d chars" % (NEW_ID, len(PROMPT)))
    if a.write:
        derive_spec.write(child, out, force=a.force)
        print("   wrote %s" % out)
    else:
        print("\nDRY RUN -- pass --write to emit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
