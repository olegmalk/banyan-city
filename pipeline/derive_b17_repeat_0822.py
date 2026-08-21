#!/usr/bin/env python3
r"""THE REPEAT-COUNT RUNG: does a countable action fill the runtime?

    python3 pipeline/derive_b17_repeat_0822.py --selftest
    python3 pipeline/derive_b17_repeat_0822.py --write

THE FINDING THIS TESTS, AND IT IS SIX CLIPS OLD RATHER THAN A HUNCH. The w4
motion wave rendered on one recipe tonight, one job per beat, every clip 105
frames at the same size, guidance, sampler and seed policy. Measured as mean
absolute interframe difference at 176x320, and as the share of the 104 frame
pairs under 0.5:

  beat  action, as the prompt words it                    <0.5   shape
  ----  ------------------------------------------------  -----  ----------------
  16    "shoulders rise and settle TWICE ... over the       0/104  moves throughout
        whole clip. Nothing else moves."
  14    "scratches at the dirt ... TWICE, and BETWEEN      56/104  rises 1.6/2.0/2.6
        the two he glances up"
  13c   "settle, sink, still"                              76/104  moves, then dead
  15    "tips ... HOLDS it there ... then lifts"           74/104  dead, then topples
  17    "turn through, plant, step"                        89/104  dead, then a burst
  19    "foot down, weight back, lean in"                  82/104  dead, then walks off

THE TWO PROMPTS THAT NAME A REPEAT COUNT ARE THE TWO THAT MOVE ALL THE WAY
THROUGH. The four that describe a ONE-SHOT SEQUENCE all park: the model performs
the single state change somewhere in the clip and holds a frame either side of
it. b13's is the clearest reading of all, because it got exactly what it asked
for -- its action ENDS on the word "still", and the clip moves for 58 frames and
is then still for 40.

That reframes a fault this tree has been writing up per-beat for a week. "Barely
moves", "a still with a runtime", "the last 2.8 s is a frozen frame" have been
recorded against beats 03, 06, 13, 15, 17, 18 and 19 as if each were a separate
problem with the plate or the seed. On this evidence they are one property of
how the action is WORDED, and it is free to test.

WHY BEAT 17 IS THE RIGHT BEAT TO TEST IT ON, and not beat 15 or 19. Both of
those have a second, larger defect in the same clip -- 15 turns the figure
upside down, 19 has no fruit in it -- so a motion measurement there is
confounded by whatever is causing that. Beat 17 came back CLEAN except for the
timing: canon face held, no topple, no dissolve, and the turn it performs is the
beat's own action. It is the one clip where the timing is the only thing wrong,
so it is the one clip where changing the timing wording measures the timing
wording.

AND THE REPEAT IS NOT AN INVENTION -- IT IS THE CLAUSE THE BEAT IS MISSING.
Beat 17's done_when is "stand, brush, turn -- a departure". The rendered clip
does stand and turn and never brushes. A cloak brush is naturally countable, so
the thing that tests the hypothesis is also the thing that closes the beat's own
gap. If the finding is wrong, the beat still gains a clause it was missing.

THE ONE VARIABLE IS THE ACTION SENTENCE. Everything else is the parent job
byte-for-byte: the same plate, the same init crop, the same head clause with the
corrected eye, the same negative, the same encode and render steps, the same
frame count, the same seed. `derive_spec` carries the structure and refuses to
carry the parent's verdict, and the payload prompt is replaced by hand here so
the diff is one string and is printed by --selftest.

PRE-REGISTERED, BEFORE THE PIXELS: the prediction is that the share of pairs
under 0.5 falls a long way from 89/104 and that no single quarter of the clip
holds all the movement. THE HONEST NULL: if it comes back at 89/104 again, the
repeat count is not the lever, the correlation across six clips is confounded by
something else, and this file says so rather than the next round quietly trying a
seventh wording. THE OTHER WAY TO FAIL, which would be a real result: the clip
moves throughout and the movement is a jitter rather than a performance -- a
countable action can buy interframe difference without buying a beat, and the
bar below scores the turn's LEGIBILITY separately from the numbers for exactly
that reason.

$0, local card, ~4 GPU minutes, one clip, one seed.
"""
from __future__ import annotations

import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                                  # noqa: E402

PARENT = "pipeline/jobs/ep2-b17-w4motion-0822.yaml"
PARENT_ID = "ep2-b17-w4motion-0822"
SPEC_ID = "ep2-b17-repeat-0822"

OLD_ACTION = (
    "THE ACTION: he carries the turn through, settles onto the far foot and "
    "takes one step away -- turn through, plant, step. HALFWAY THROUGH his back "
    "is most of the way to camera and his leading foot is lifting.")

# COUNTABLE AND CONTINUOUS, in the shape beat 16's prompt uses -- a numbered
# repeat plus an "over the whole clip" span, and an explicit "nothing else
# moves" so the runtime is not filled with drift instead of performance.
NEW_ACTION = (
    "THE ACTION: he brushes the front of his shirt down with one hand, twice, "
    "and turns away from the camera slowly and steadily over the whole clip. "
    "The turn is unbroken from the first frame to the last -- it never pauses "
    "and it never finishes early. Nothing else moves. HALFWAY THROUGH he is in "
    "profile, mid-brush, still turning.")

BAR = (
    "TWO SCORES, KEPT SEPARATE ON PURPOSE, because a number and a picture can "
    "disagree here and the picture wins. "
    "(A) THE MEASUREMENT, pre-registered: mean absolute interframe difference at "
    "176x320 over all 104 pairs, reported as the share under 0.5 and as the mean "
    "of each ten-frame block. The parent is 89/104 with blocks 0.29 0.07 0.14 "
    "0.37 0.23 0.20 0.22 0.24 5.44 4.89 6.28. A PASS on this half is a large "
    "fall in the share AND no single block carrying the clip. "
    "(B) THE PERFORMANCE, by eye and it outranks (A): the turn must READ as one "
    "continuous departure, and the brush must read as a brush -- a hand moving "
    "down the front of the shirt, twice, not a twitch. A clip that scores well on "
    "(A) with a jittering figure is a FAIL and is reported as one, because "
    "interframe difference is not motion, it is change. "
    "CARRIED UNCHANGED FROM THE PARENT BAR: the face is drawn in EVERY frame of "
    "the trimmed clip and it is the CORRECTED face -- small off-white almond eyes "
    "with tiny dark pupils, broad dome, near-horizontal ears, sage mandarin "
    "collar -- checked at the LAST frame and not only the first. NOTE this beat's "
    "own definition says the turn takes his face away by design, so a back-of-head "
    "final frame is NOT a face failure here; the check is that the face is his "
    "for as long as it is visible. "
    "PRE-REGISTERED FAIL MODES: the null, 89/104 again, which retires the repeat "
    "count as a lever across all six beats rather than only this one; a jitter "
    "that passes (A) and fails (B); the brush binding to the wrong hand or to the "
    "grass; and the turn completing early and holding, which is the parent's "
    "failure arriving at a different frame rather than being fixed.")


def build():
    child = derive_spec.derive(
        src=PARENT,
        new_id=SPEC_ID,
        fresh={
            "owner": ("night iteration lane, 2026-08-22 -- the repeat-count rung, "
                      "measured across six clips of tonight's wave"),
            "consumer": (
                "BEAT 17's SLOT, and every other beat in the episode that has ever "
                "been written up as 'barely moves'. Beat 17 is the test bed because "
                "it is the one clip in tonight's wave whose ONLY fault is timing -- "
                "canon face held, no topple, no dissolve, and the turn it performs "
                "is the beat's own action, it just does not start until frame 80. "
                "If the wording moves the timing, beats 03, 13, 15 and 19 each get "
                "the same one-line edit and none of them needs a new plate. If it "
                "does not, the correlation is retired and nobody spends a seventh "
                "wording on it."),
            "success": BAR,
            "why": (
                "SIX CLIPS RENDERED TONIGHT ON ONE RECIPE SPLIT CLEANLY BY HOW THEIR "
                "ACTION IS WORDED. The two prompts that name a repeat count -- beat "
                "16's 'twice ... over the whole clip' and beat 14's 'twice, and "
                "between the two' -- are the two that move all the way through, at "
                "0 and 56 of 104 frame pairs under 0.5. The four that describe a "
                "one-shot sequence all park at 74 to 89 of 104, performing their "
                "single state change in one burst and holding a frame either side. "
                "Beat 13's is the plainest: its action ENDS on the word 'still' and "
                "the clip moves for 58 frames and is then still for 40. This job "
                "changes ONE STRING -- beat 17's action sentence, from a one-shot "
                "sequence to a countable repeat plus an explicit whole-clip span -- "
                "and changes nothing else. The repeat chosen is a cloak brush, which "
                "is not an invention: this beat's done_when is 'stand, brush, turn' "
                "and the rendered clip never brushes, so the thing that tests the "
                "hypothesis is also the clause the beat is missing. $0, ~4 GPU "
                "minutes. Full trace: pipeline/derive_b17_repeat_0822.py."),
        },
        extra={
            "the_one_variable": (
                "THE ACTION SENTENCE, and nothing else. Same plate, same init crop, "
                "same head clause with the corrected eye, same negative, same encode "
                "and render steps, same frame count, same seed. The parent's stated "
                "one variable was the PLATE; this one is the words, and the two "
                "together make beat 17's two runs a clean pair."),
            "measured_parent": (
                "ep2-b17-w4motion-0822, judged 2026-08-22: 89 of 104 frame pairs "
                "under 0.5; ten-frame block means 0.29 0.07 0.14 0.37 0.23 0.20 0.22 "
                "0.24 5.44 4.89 6.28; largest single step 24.2 at f101. Canon face "
                "held throughout, no topple, no dissolve. The turn is real and it "
                "does not begin until frame 80."),
            "action_diff": {"was": OLD_ACTION, "now": NEW_ACTION},
            "null_result_is_publishable": (
                "If this comes back at 89/104 the repeat count is NOT the lever and "
                "the finding is retired for all six beats in one line, not quietly "
                "re-tried at a seventh wording. The wording ladder rule in this repo "
                "closes at three rungs and this is rung one."),
        },
        by="pipeline/derive_b17_repeat_0822.py",
    )
    pay = dict(child.get("payload") or {})
    key = [k for k in pay if k.endswith("b17-motion-prompt.txt")]
    if len(key) != 1:
        raise SystemExit("!! expected exactly one motion prompt in the payload, "
                         "found %r" % (sorted(pay),))
    text = pay[key[0]]
    if OLD_ACTION not in text:
        raise SystemExit("!! the parent's action sentence is not in its payload "
                         "verbatim -- refusing to guess at a replacement")
    pay[key[0]] = text.replace(OLD_ACTION, NEW_ACTION)
    child["payload"] = pay
    return child


def _selftest():
    spec = build()
    key = [k for k in spec["payload"] if k.endswith("b17-motion-prompt.txt")][0]
    text = spec["payload"][key]
    assert NEW_ACTION in text and OLD_ACTION not in text
    # EVERYTHING BEFORE `THE ACTION:` MUST BE BYTE-IDENTICAL to the parent. That
    # head clause carries the corrected eye, and an edit that touched it would
    # make this a two-variable job wearing a one-variable label -- the exact
    # defect the 08-19 audit found in three inherited crf-10 children.
    parent = derive_spec.load(os.path.join(REPO, PARENT))
    pkey = [k for k in parent["payload"] if k.endswith("b17-motion-prompt.txt")][0]
    ptext = parent["payload"][pkey]
    assert text.split("THE ACTION:")[0] == ptext.split("THE ACTION:")[0], "head clause moved"
    assert "eyebags" in text and "almond eyes" in text, "corrected eye clause lost"
    # The hypothesis, in the string: a count and a whole-clip span.
    assert "twice" in NEW_ACTION
    assert "over the whole clip" in NEW_ACTION
    assert "Nothing else moves" in NEW_ACTION
    # No object may be named that the plate does not contain -- this wave's own
    # first law, and the clause that toppled beat 04. The plate is one figure in
    # tall grass, so the brush is on his own SHIRT and nothing else is named.
    for banned in ("trunk", "sapling", "fig", "fruit", "branch", "board", "guard"):
        assert banned not in NEW_ACTION.lower(), banned
    # derive_spec must have refused to carry any scored key.
    for k in spec:
        assert "verdict" not in k and "pick" not in k, k
    assert spec["id"] == SPEC_ID and spec["task"] == SPEC_ID
    # THE PARENT ID MAY APPEAR IN PROSE AND MUST NOT APPEAR IN A PATH. `derive`
    # already refuses a child whose STRUCTURE still names the parent; the extras
    # written here cite it on purpose, because "measured_parent" is the whole
    # point of the record. What would be a real defect is a box path or an
    # artifact still pointing at the parent's directory, so that is what is
    # asserted -- one publish dir per job, or two runs overwrite each other.
    operational = derive_spec._dump({k: spec[k] for k in
                                     ("payload", "steps", "artifacts") if k in spec})
    assert PARENT_ID not in operational, "the parent's paths survived retokening"
    print("SELFTEST OK  %s" % SPEC_ID)
    print("  was: %s" % OLD_ACTION)
    print("  now: %s" % NEW_ACTION)
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
    p = derive_spec.write(build(), "pipeline/jobs/%s.yaml" % SPEC_ID,
                          force=a.force)
    print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
