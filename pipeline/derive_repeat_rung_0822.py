#!/usr/bin/env python3
r"""THE REPEAT COUNT, APPLIED TO THE TWO OTHER BEATS IT FITS.

    python3 pipeline/derive_repeat_rung_0822.py --selftest
    python3 pipeline/derive_repeat_rung_0822.py --write

THE RUNG IS NOT A HYPOTHESIS ANY MORE -- IT WAS SAMPLED AND IT PASSED. Beat 17
was re-rendered tonight with one string changed, and both halves of its
pre-registered bar came back:

    measure                       parent (one-shot)   with a repeat count
    frame pairs under 0.5         89 / 104            52 / 104
    ten-frame block means         0.29 0.07 0.14      1.49 1.35 1.90 1.80
                                  0.37 0.23 0.20      1.75 1.53 0.76 0.22
                                  0.22 0.24 5.44      3.56 3.69 4.03
                                  4.89 6.28
    the performance               3.3 s of still,     a hand comes up, wipes
                                  then a burst        down the shirt front and
                                                      returns, then he turns

AND THE SAMPLE SHARPENED THE FINDING, WHICH IS WHY IT WAS RUN ALONE. Two things
changed in beat 17's sentence: a countable repeat, and an instruction that the
turn be "unbroken from the first frame to the last". THE COUNT DID ALL THE WORK
-- the turn is still confined to the last quarter, exactly where it was. So the
lever is A COUNTABLE ACTION and NOT a request to move slowly, and any rung that
carried both would have credited the wrong half.

WHY THESE TWO BEATS AND NOT THE OTHER FOUR.

  b03  "Face holds 105 frames; the body barely moves and the camera drifts."
       Its action already says "three separate moves, one after the other, and
       he is still moving when the clip ends" -- a sequence with no count -- and
       it parked anyway. It is the cleanest remaining fit: the face is right,
       nothing topples, and the only fault is that nothing happens.
  b13  the curl take. Its action ENDS ON THE WORD "still" and the clip moves for
       58 frames and is then still for 40. It obeyed its own sentence. The
       founder's pose ruling for this beat -- he curls DOWN small and NEVER
       RISES -- is carried word for word; only the timing changes.

  NOT b15 and NOT b19. Both have a second, larger defect in the same clip: 15
  rotates the figure upside down and 19 has no fruit in it at all. A timing
  measurement on either would be confounded by whatever causes that, and a
  re-motion cannot put a fruit into a plate that has none.
  NOT b14 and NOT b16. Both already name a count and both already move.

THE OBJECT LAW IS APPLIED, AND IT COSTS b03 A CLAUSE. Beat 04 toppled tonight
because its carried action said "from behind the trunk" and the plate has no
trunk. b03's action names "the thin stem that is already there", and the stalk
in its clip GROWS IN rather than being in the plate -- so the stem comes OUT of
the rewritten sentence rather than being trusted. Both new actions name no
object at all, and --selftest refuses one that does.

AND THE WORD "still" IS BANNED FROM b13's NEW SENTENCE by the selftest, because
that word is the best-evidenced cause of a frozen tail in this whole wave.

ONE VARIABLE PER BEAT: the action sentence. Same plate, same init crop, same
head clause with the corrected eye, same negative, same steps, same frame count,
same seed. Two jobs rather than one because this is a PROVEN rung applied to two
new inits -- the same argument the three sapnat jobs made on 08-21 -- and not a
recipe being scaled before it has been looked at.

$0, ~8 GPU minutes for the pair.
"""
from __future__ import annotations

import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                                  # noqa: E402

MEASURED = (
    "ep2-b17-repeat-0822, rendered and judged 2026-08-22, is the sample this "
    "rung rests on: 52 of 104 frame pairs under 0.5 against its one-shot "
    "parent's 89, block means 1.49 1.35 1.90 1.80 1.75 1.53 0.76 0.22 3.56 3.69 "
    "4.03 against 0.29 0.07 0.14 0.37 0.23 0.20 0.22 0.24 5.44 4.89 6.28, and a "
    "brush that reads as a brush rather than a jitter. The COUNT carried it; the "
    "'unbroken over the whole clip' half of that edit moved nothing.")

# beat -> (parent spec, prompt filename tail, old action, new action, why, consumer)
BEATS = {
    3: dict(
        parent="pipeline/jobs/ep2-b03-w4motion-0822.yaml",
        tail="b03-motion-prompt.txt",
        old=("THE ACTION: three separate moves, one after the other, and he is "
             "still moving when the clip ends. FIRST he drops his head and "
             "shoulders down and sideways behind the thin stem that is already "
             "there, hunching until his shoulders are up around his ears. THEN "
             "his head comes back up and turns to look off to his left, away "
             "from the stem. THEN it snaps back to centre. His body stays where "
             "it is and only his head, neck and shoulders travel. HALFWAY "
             "THROUGH his head is at its lowest, tucked down and tilted, "
             "shoulders hunched up around it."),
        new=("THE ACTION: he ducks his head and shoulders down and to one side "
             "and brings them back up, TWICE -- down, up, down, up -- hunching "
             "his shoulders up around his ears each time he goes down. The two "
             "ducks are spread evenly across the clip. His body stays where it "
             "is and only his head, neck and shoulders travel. Nothing else "
             "moves. HALFWAY THROUGH he is at the bottom of the second duck, "
             "shoulders hunched up around his head."),
        consumer=(
            "BEAT 03's SLOT. Its staged clip's verdict is 'the face holds all "
            "105 frames and the body barely moves' -- the face half is answered "
            "and the motion half is not, and this is the only remaining beat "
            "where that is the ONLY fault."),
        why=(
            "BEAT 03 IS THE CLEANEST FIT FOR A RUNG THAT IS ALREADY PROVEN. Its "
            "current action names three moves in sequence and even says 'he is "
            "still moving when the clip ends', and the clip parks anyway -- "
            "which is the evidence that a sequence is not a schedule. Rewritten "
            "as two counted ducks. IT ALSO LOSES AN OBJECT: the old sentence "
            "says 'behind the thin stem that is already there' and the stalk in "
            "that clip GROWS IN rather than being in the plate, so under the law "
            "beat 04 toppled on six hours ago the clause comes out. The new one "
            "names nothing."),
    ),
    13: dict(
        parent="pipeline/jobs/ep2-b13-w4motioncurl-0822.yaml",
        tail="b13-motion-prompt.txt",
        old=("THE ACTION: his shoulders drop and he settles lower over his "
             "knees, his head sinking a little further down and to the side -- "
             "settle, sink, still. HALFWAY THROUGH his shoulders are down and "
             "his head is lower than it started, still tipping. HE NEVER RISES, "
             "he never straightens up and his head never comes back up."),
        new=("THE ACTION: he settles lower over his knees TWICE -- a small sink "
             "and a settle, then another sink and a settle -- and the two are "
             "spread evenly across the clip, his head tipping a little further "
             "down each time. Nothing else moves. HALFWAY THROUGH he is between "
             "the two sinks, already lower than he started. HE NEVER RISES, he "
             "never straightens up and his head never comes back up."),
        consumer=(
            "BEAT 13's SLOT. The curl take reaches this beat's written end state "
            "-- folded small, knees up -- which nothing before it did, and it is "
            "staged as the beat's best available. Its one measured fault is that "
            "it finishes in 58 frames and holds a dead frame for 40, so it had "
            "to be cut at 58 and the assembly holds the last frame for the rest "
            "of the slot. This spends the whole slot on picture instead."),
        why=(
            "BEAT 13's CURL TAKE OBEYED ITS OWN SENTENCE AND THAT IS THE PROBLEM. "
            "Its action reads 'settle, sink, still' and the clip moves for 58 "
            "frames and is then still for 40 -- block means 4.01 1.18 0.07 0.15 "
            "0.11 0.03 across the tail. The word 'still' is the best-evidenced "
            "cause of a frozen tail in this entire wave and it is out; the "
            "selftest refuses it. THE FOUNDER'S POSE RULING IS CARRIED WORD FOR "
            "WORD -- he curls down small and HE NEVER RISES -- because that is "
            "R4's and not this rung's. Only the timing changes."),
    ),
}

BAR = (
    "TWO SCORES, KEPT SEPARATE, AND THE PICTURE OUTRANKS THE NUMBER. "
    "(A) THE MEASUREMENT: mean absolute interframe difference at 176x320 over "
    "all 104 pairs, reported as the share under 0.5 and as each ten-frame "
    "block's mean. A pass is a clear fall in the share against this beat's own "
    "parent AND no single block carrying the clip. "
    "(B) THE PERFORMANCE, by eye: the counted move must read as that move, done "
    "twice. A figure that vibrates through the runtime scores well on (A) and is "
    "a FAIL -- interframe difference is not motion, it is change, and this is "
    "the failure mode the b17 sample was checked against before it was called a "
    "pass. "
    "CARRIED FROM THE PARENT BAR: the CORRECTED face -- small off-white almond "
    "eyes with tiny dark pupils, broad dome, near-horizontal ears, sage mandarin "
    "collar -- drawn in EVERY frame including the LAST, not only the first. "
    "PER BEAT: b03 must not topple and must not name or grow an object the plate "
    "does not have; b13 must still reach the folded-small end state with the "
    "knees up and HE MUST NOT RISE, which is the founder's ruling and outranks "
    "any improvement in the numbers. "
    "PRE-REGISTERED FAIL MODES: the null, in which the share does not move and "
    "the b17 result was beat-specific rather than general -- publishable, and it "
    "closes the rung rather than sending anyone to a third wording; a jitter "
    "passing (A) and failing (B); the two repeats collapsing into one long slow "
    "move, which is what b17 itself did and which would still be a partial pass "
    "if the runtime is filled; and on b13, a repeat that makes him bob back UP, "
    "which breaks the ruling and is an outright DROP however well it moves.")


def build(beat):
    cfg = BEATS[beat]
    new_id = "ep2-b%02d-repeat-0822" % beat
    child = derive_spec.derive(
        src=cfg["parent"],
        new_id=new_id,
        fresh={
            "owner": ("night iteration lane, 2026-08-22 -- the repeat-count rung, "
                      "applied to beat %02d after the b17 sample passed" % beat),
            "consumer": cfg["consumer"],
            "success": BAR,
            "why": cfg["why"] + " " + MEASURED,
        },
        extra={
            "the_one_variable": (
                "THE ACTION SENTENCE. Same plate, same init crop, same head "
                "clause with the corrected eye, same negative, same steps, same "
                "frame count, same seed as this beat's own parent."),
            "measured_sample": MEASURED,
            "action_diff": {"was": cfg["old"], "now": cfg["new"]},
            "not_a_batch": (
                "TWO JOBS FILED TOGETHER AND THAT IS NOT A BATCH BEFORE A SAMPLE. "
                "The recipe change was sampled ALONE on beat 17 and judged on "
                "pixels before either of these was written. What varies here is "
                "the INIT, which is the same argument the three sapnat jobs made "
                "on 08-21. Beats 15 and 19 are deliberately excluded: each has a "
                "second, larger defect in the same clip and a timing measurement "
                "there would be confounded."),
        },
        by="pipeline/derive_repeat_rung_0822.py",
    )
    pay = dict(child.get("payload") or {})
    keys = [k for k in pay if k.endswith(cfg["tail"])]
    if len(keys) != 1:
        raise SystemExit("!! beat %d: expected one %s in the payload, found %r"
                         % (beat, cfg["tail"], sorted(pay)))
    text = pay[keys[0]]
    if cfg["old"] not in text:
        raise SystemExit("!! beat %d: the parent's action is not in its payload "
                         "verbatim -- refusing to guess at a replacement" % beat)
    pay[keys[0]] = text.replace(cfg["old"], cfg["new"])
    child["payload"] = pay
    return child


# Objects that have each cost this tree a render when a prompt named one its
# plate did not contain. b04 rotated ninety degrees onto its side over `trunk`.
BANNED_OBJECTS = ("trunk", "stem", "stalk", "sapling", "fig", "fruit", "branch",
                  "board", "guard", "leaf", "leaves")


def _selftest():
    for beat, cfg in sorted(BEATS.items()):
        spec = build(beat)
        key = [k for k in spec["payload"] if k.endswith(cfg["tail"])][0]
        text = spec["payload"][key]
        assert cfg["new"] in text and cfg["old"] not in text, beat
        parent = derive_spec.load(os.path.join(REPO, cfg["parent"]))
        pkey = [k for k in parent["payload"] if k.endswith(cfg["tail"])][0]
        ptext = parent["payload"][pkey]
        # Everything before the action must be byte-identical: that head clause
        # carries the corrected eye, and touching it would make this a
        # two-variable job wearing a one-variable label.
        assert text.split("THE ACTION:")[0] == ptext.split("THE ACTION:")[0], beat
        assert "eyebags" in text and "almond eyes" in text, beat
        # The hypothesis, in the string.
        assert "TWICE" in cfg["new"], beat
        assert "Nothing else moves" in cfg["new"], beat
        # NO OBJECT. b04 toppled tonight over a positional clause naming a trunk
        # its plate did not have, and b03's old sentence named a stem.
        low = cfg["new"].lower()
        for obj in BANNED_OBJECTS:
            assert obj not in low, (beat, obj)
        # b13: the word that froze it, and the ruling that must survive.
        if beat == 13:
            assert "still" not in low, "the terminal `still` is what froze b13"
            assert "HE NEVER RISES" in cfg["new"]
            assert "never straightens up" in cfg["new"]
        # No scored key may have crossed from the parent.
        for k in spec:
            assert "verdict" not in k and "pick" not in k, (beat, k)
        operational = derive_spec._dump(
            {k: spec[k] for k in ("payload", "steps", "artifacts") if k in spec})
        assert parent["id"] not in operational, (beat, "parent paths survived")
        print("  ok  beat %02d  %s" % (beat, spec["id"]))
    print("SELFTEST OK  %d beat(s)" % len(BEATS))
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
    for beat in sorted(BEATS):
        spec = build(beat)
        p = derive_spec.write(spec, "pipeline/jobs/%s.yaml" % spec["id"],
                              force=a.force)
        print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
