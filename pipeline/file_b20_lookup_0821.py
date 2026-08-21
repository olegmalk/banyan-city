#!/usr/bin/env python3
r"""BEAT 20, ROUND 3: the prompt was asserting the end of the action as a
standing fact about the subject, so there was no delta left to animate.

    python3 pipeline/file_b20_lookup_0821.py            # dry run
    python3 pipeline/file_b20_lookup_0821.py --write

WHAT ROUND 2 SETTLED AND WHAT IT LEFT
--------------------------------------------------------------------------
Round 2 put the scripted object into the init plate and three of its four
bars went green: the frame is locked (his scale is constant across all 105
frames), the rogue branch that used to walk in at top right from ~f048 is
gone, the fig is canon purple in every frame instead of yellow-green, and
the identity holds end to end with no dissolve. The lift is real too -- the
fig starts low in his lap and is at chest-and-chin height from f048.

What did not happen is the head turn. Judged by eye off an 8-frame sheet:
his head is level and his face is square to camera in all 105 frames. His
EYES roll upward from about f030, which is the model doing the only part of
"look up" it can do without moving the skull, but the head itself never
turns and the beat's whole turn is that movement.

THE ONE VARIABLE, AND IT IS IN THE PROMPT'S OWN TEXT
--------------------------------------------------------------------------
Round 2's subject inventory reads:

    "He is squatting, holding a small fruit, LOOKING UP, in tall grass,
     full body."

That sentence is the model's statement of what is already true of the
subject. It says he is ALREADY looking up. THE ACTION then asks him to look
up. An action whose end state is pre-asserted in the inventory is a no-op:
the model can satisfy both sentences by rendering a goblin who is looking
up and never moving, and that is exactly the clip that came back, twice.
Round 1's "close to a still with a runtime" is the same fault reading the
whole pose; round 2 narrowed it to the head because the lift proved the
model WILL move a body part the inventory has not already finished.

This is the wave's own law applied one level in. The law says a prompt that
names an object absent from the init makes the model build it; the corollary
is that a prompt that names a POSE the action is supposed to reach makes the
model skip the action. Both are the inventory and THE ACTION disagreeing
about what time it is.

SO: the inventory is rewritten to describe the plate as it actually is, and
nothing else moves. The init frame, checked at 1:1 before this was written,
has him square to camera with his head level, his eyes forward, and the fig
low in his lap -- so "head level, face to camera, the fruit low in both
hands" is a statement of fact and "looking up" was never one. THE ACTION is
then restated as the delta in body-part terms (the skull turns, the chin
lifts) rather than as the word the inventory had already spent.

GEOMETRY, MEASURED ON THE INIT, AND WHY THE TARGET IS NAMED AS "UP AND TO
HIS RIGHT" AND NOT "UP"
--------------------------------------------------------------------------
On the 704x1280 init his eyes sit at about y=220 and the composited stem's
two leaves at about y=440 -- the leaves are BELOW his eye line, not above
it, despite round 2's inventory sentence claiming "at about his eye line".
A prompt that asks him to look UP at a thing the picture puts DOWN and to
the right is asking for a movement the frame cannot contain, and the wave
has already measured what the model does when the words and the init
disagree: it rebuilds the frame. So the target is described where it is.
The upward component is bought from the FRUIT instead, which really is in
his lap: his face leaves a thing that is low and arrives at a thing that is
higher than that thing. That is a chin lift, it is true of this init, and it
is the movement the beat needs to read.

THE BATCH. Three seeds, one recipe -- episode-loop-v2 step 2, "i2v from the
picked plate, 4-8 seeds in one batch, pick by eye". Seed 20260920 is round
2's own seed and is kept deliberately: that clip is the single-variable
control, and any difference between it and round 2 is the sentence and
nothing else. The other two are variance on the same wording, because a head
turn is the kind of motion that either seeds in or does not.

NOT CHANGED: the init plate and its sha assert, size, frame count, fps,
guidance, sampler, sigmas, two-stage, crf, offload, the negative block byte
for byte, and the trim plan. The identity clause is carried byte-for-byte
from round 1 for the third round running.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import derive_spec                                            # noqa: E402

PARENT = "pipeline/jobs/ep2-b20-canonmotion-r2-0821.yaml"

# The sentence that is replaced, and the one that replaces it. Both are
# asserted against the parent's payload before anything is written, so a
# reworded parent fails loudly instead of silently deriving a copy.
OLD_POSE = ("He is squatting, holding a small fruit, looking up, in tall "
            "grass, full body.")
NEW_POSE = ("He is squatting in tall grass, full body, square to camera, "
            "HIS HEAD LEVEL AND HIS FACE TOWARD THE LENS, the fruit held "
            "low in both hands in his lap.")

OLD_EYELINE = ("and A THIN SAPLING STEM WITH TWO LEAVES is already in frame "
               "beside him at the right, at about his eye line.")
NEW_EYELINE = ("and A THIN SAPLING STEM WITH TWO LEAVES is already in frame "
               "close beside him at his right, its two leaves higher than "
               "the fruit in his lap.")

NEW_ACTION = (
    "THE ACTION: he raises the fig in both hands, and then HIS HEAD TURNS "
    "AWAY FROM THE LENS TO HIS RIGHT AND HIS CHIN LIFTS -- the whole skull "
    "rotates, his face stops pointing at the camera, and he ends looking at "
    "the two leaves on the stem beside him instead of at the fruit. THE HEAD "
    "TURN IS THE BEAT and it must finish. HALFWAY THROUGH his face has "
    "already left the camera and is angled toward the stem at his right, "
    "chin up off the fruit, the fig still closed in both hands.")

SEEDS = [20260920, 20260921, 20260922]


def build_prompt(parent_prompt: str) -> str:
    for needle in (OLD_POSE, OLD_EYELINE, "THE ACTION:"):
        if needle not in parent_prompt:
            raise SystemExit("!! the parent prompt does not contain %r -- it "
                             "has been reworded since this filer was written, "
                             "so the one-variable claim is not true. Re-read "
                             "it before filing." % needle[:48])
    head = parent_prompt[:parent_prompt.index("THE ACTION:")]
    head = head.replace(OLD_POSE, NEW_POSE).replace(OLD_EYELINE, NEW_EYELINE)
    if "looking up" in head:
        raise SystemExit("!! 'looking up' still survives in the inventory, "
                         "which is the entire point of this round")
    return head + NEW_ACTION


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    import yaml as _yaml
    pspec = _yaml.safe_load(open(os.path.join(REPO, PARENT), encoding="utf-8"))
    pkey = [k for k in pspec["payload"] if "motion-prompt" in k][0]
    prompt = build_prompt(pspec["payload"][pkey])

    for i, seed in enumerate(SEEDS, start=1):
        new_id = "ep2-b20-lookup-s%d-0821" % i
        child = derive_spec.derive(
            PARENT, new_id,
            fresh={
                "owner": "iteration-campaign lane B (beats 11-21), 2026-08-21 night",
                "consumer": (
                    "THE BEAT-20 SELECTION on review/ep2-beats-0821. Beat 20 "
                    "currently has three takes and not one of them closes its "
                    "done_when, so the founder has nothing to pick between: "
                    "the shipping take is an old man under the wrong tree, "
                    "round 1 is a still with a runtime, and round 2 is a "
                    "clean canon goblin who never moves his head. This batch "
                    "exists to put a FINISHED version in front of him rather "
                    "than a fourth description of what is wrong. Nothing here "
                    "touches review/ep2-ship-0821 or any cut."),
                "success": (
                    "THREE 704x1280 105-frame 24fps mp4s, and the batch "
                    "succeeds if AT LEAST ONE of them clears all four bars. "
                    "H1 THE HEAD TURNS: his face is square to the lens at "
                    "f000 and is angled away from the lens toward his right "
                    "by f096, judged as skull orientation and not as eye "
                    "direction -- eyes rolling up inside a level head is what "
                    "round 2 already did and it is a FAIL here. H2 the chin "
                    "is visibly higher at f096 than at f000. H3 everything "
                    "round 2 already won is still won: frame locked with his "
                    "scale constant, the composited stem still there and "
                    "un-multiplied, the fig purple, and face, ears, skin and "
                    "clothes drawn in every frame with no dissolve. H4 the "
                    "fig stays closed in both hands the whole clip. A clip "
                    "that buys the head turn by breaking H3 is not a "
                    "candidate, it is a trade the beat cannot make."),
                "why": (
                    "ROUND 2'S SUBJECT INVENTORY TOLD THE MODEL HE WAS "
                    "ALREADY LOOKING UP, AND THEN THE ACTION ASKED HIM TO "
                    "LOOK UP.\n\nThe sentence is 'He is squatting, holding a "
                    "small fruit, looking up, in tall grass, full body.' That "
                    "clause is the model's inventory of what is already true. "
                    "With the end state pre-asserted there, a goblin who "
                    "looks up and never moves satisfies both sentences at "
                    "once -- which is the clip that came back in round 1 and "
                    "again in round 2.\n\nROUND 2'S OWN RESULT IS THE "
                    "EVIDENCE THAT THIS IS THE LIVE FAULT AND NOT A GUESS. "
                    "The LIFT in that same action clause DID happen: the fig "
                    "goes from his lap at f000 to chest-and-chin height by "
                    "f048. The lift is the half of the action whose end state "
                    "the inventory did NOT already assert -- the inventory "
                    "says the fruit is 'closed in both his hands', not that "
                    "it is raised. So the model moved the part it had not "
                    "been told was finished and skipped the part it had. Two "
                    "halves of one sentence, one rendered and one not, split "
                    "exactly along which end state the inventory had already "
                    "spent.\n\nWHAT CHANGED: the inventory now describes the "
                    "init as it is -- head level, face to the lens, fruit low "
                    "in the lap, all three checked at 1:1 on "
                    "b20-init-704x1280.png before this was written -- and THE "
                    "ACTION restates the delta in body-part terms, the skull "
                    "rotating and the chin lifting, rather than in the word "
                    "the inventory had already used. The stem's position is "
                    "also corrected to what the picture shows: its leaves sit "
                    "at about y=440 against his eyes at about y=220, so they "
                    "are BELOW his eye line, and round 2's 'at about his eye "
                    "line' was wording that disagreed with its own init. This "
                    "wave has already measured what the model does when the "
                    "words and the init disagree.\n\nWHAT DID NOT CHANGE: the "
                    "init plate and its sha assert, size, frame count, fps, "
                    "guidance, sampler, sigmas, two-stage, crf, offload, the "
                    "negative block byte for byte, and the trim plan. Round 2 "
                    "proved the plate; this asks only about the sentence."),
            },
            overrides={
                "seed": seed,
                "payload:b20-motion-prompt.txt": prompt,
                "key:priority": 12,
            },
            extra={
                "the_one_variable": (
                    "THE SUBJECT INVENTORY'S POSE SENTENCE, which stops "
                    "asserting the action's end state, plus the action clause "
                    "restated as the body-part delta that follows from it. "
                    "Everything a sampler reads is round 2's: same init png "
                    "and same sha assert, same 704x1280, same 105 frames at "
                    "24fps, same guidance, sigmas, two-stage, crf and "
                    "offload, same negative text. SEED 20260920 IS ROUND 2'S "
                    "OWN SEED and is kept on purpose so that s1 is a true "
                    "single-variable control against the round-2 clip; s2 and "
                    "s3 are variance on the same wording, because a head turn "
                    "either seeds in or does not."),
                "failure_predicted_in_advance": (
                    "EYES WITHOUT A SKULL, and it is why H1 is written as "
                    "skull orientation. Round 2 already showed the model will "
                    "roll the pupils upward inside a head that does not move; "
                    "a round 3 that buys a slightly stronger version of the "
                    "same eye-roll has not bought the beat, and scoring it "
                    "generously is how a fault survives a round. SECOND: the "
                    "head turns and takes the face off-canon with it -- a "
                    "three-quarter or profile skull is a view the canon plate "
                    "never showed the model, so the ear, the collar or the "
                    "slit pupil can dissolve as it rotates. H3 catches that, "
                    "and a clip that turns the head by losing the face is a "
                    "fail, not a trade. THIRD, cheapest: naming the stem as a "
                    "thing he turns TOWARD re-opens the pull-back the plate "
                    "fix closed. H3's scale clause catches it."),
                "not_done_on_purpose": (
                    "THE INIT IS NOT RE-COMPOSITED, even though the stem's "
                    "leaves sitting below his eye line is a real reason a "
                    "LOOK UP is hard to buy here. Lifting the stem in the "
                    "plate is a second variable and a second render step, and "
                    "the sentence is the cheaper lever by an order of "
                    "magnitude; if all three seeds come back with a level "
                    "head, the wording route is closed and the plate geometry "
                    "is the next rung, filed as its own job with its own "
                    "question. NOTHING HERE TOUCHES THE CUT, and no beat "
                    "outside 20 is in this batch."),
            },
            by="pipeline/file_b20_lookup_0821.py",
        )

        blob = _yaml.safe_dump({k: v for k, v in child.items()
                                if k != "derivation"})
        if "looking up" in blob.lower().split("the_one_variable")[0]:
            pass  # the prose legitimately quotes the removed words
        if str(seed) not in blob:
            raise SystemExit("!! seed %d did not reach the child spec" % seed)
        if "sapnat" not in blob:
            raise SystemExit("!! the round-2 plate did not reach the child")

        out = "pipeline/jobs/%s.yaml" % new_id
        print("%-26s seed %d  prompt %d chars" % (new_id, seed, len(prompt)))
        if a.write:
            path = derive_spec.write(child, out, force=a.force)
            print("   wrote %s" % os.path.relpath(path, REPO))

    print()
    print("PROMPT:")
    print(prompt)
    if not a.write:
        print("\n-- dry run. re-run with --write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
