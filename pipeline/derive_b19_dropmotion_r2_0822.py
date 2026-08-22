#!/usr/bin/env python3
r"""BEAT 19: MOTION OFF THE PLATE THAT HAS THE FRUIT IN IT.

    python3 pipeline/derive_b19_dropmotion_0822.py --selftest
    python3 pipeline/derive_b19_dropmotion_0822.py --write

THIS RUNG WAS NAMED ON 08-19 AND HAS NEVER BEEN FIRED. `work-ladder-0819.md`,
beat 19: *"Still named, not fired: this plate's motion wants `--image-crf 10`,
not 33."* The plate in question is `ep2-b19-sapgloss-0819` -- the composite that
passed all eight clauses of the bar its parent had pre-registered, with the plant
and the fruit DRAWN into the field in PIL and settled with a 0.22-strength pass.

AND TONIGHT MADE IT URGENT RATHER THAN OPTIONAL. Beat 19's w4 motion clip landed
a few hours ago and FAILED for one reason above all others: **there is no fruit
in it at all.** The beat is a fall, a landing and a noticing, and the object that
does all three is absent, so none of the three can happen. The w4 plate was
authored for the FACE and nobody put the fruit back into it -- the same
prompt-summons law that pulled beats 02, 03 and 20 off their framing. The
composite plate is the plate that does not have that problem.

SO THE ONE VARIABLE IS THE INIT, and it is the variable that matters:

    w4 plate          a goblin mid-stride in grass. No fruit. No plant.
    sapgloss plate    the same field with a rooted stem, two wide leaves, a
                      side-branch and ONE matte violet fig -- drawn, then
                      naturalised, and scored 8 of 8 before this file existed.

THE ACTION MAY NAME THE FRUIT NOW, AND ONLY NOW. This wave's first law is that a
prompt naming an object its init does not contain makes the model build the
object and re-frame the shot to fit it; beat 04 rotated ninety degrees onto its
side over a trunk that was not there. The sapgloss init CONTAINS the fig, the
stem and the leaves, so naming them is description rather than summons. The
selftest asserts that the init being pointed at is the sapgloss one, because that
assertion is the whole licence for the wording.

WHAT I EXPECT AND WHY I AM NOT PRETENDING OTHERWISE. Tonight measured that
one-shot actions park: the model performs the single state change in one burst
and holds a frame either side. **A fruit falling is inherently one-shot** and no
count can be put on it -- beat 13 proved this evening that a counted repeat on an
action that cannot happen twice makes things WORSE, not better. So this clip is
likely to hold, drop, and hold. That is accepted rather than fought: the beat's
`done_when` is three events in order, and a still-fall-still that gets all three
in the right order is a pass on the beat even if it is not a full runtime of
motion. The action gives the tail something to do -- he keeps looking at where it
landed -- which is the only lever tonight's evidence supports for a tail.

`--image-crf 10` is already what the parent's render step passes, so the ladder's
named change needs no edit: it is inherited and is asserted below rather than
assumed.

$0, ~4 GPU minutes, one clip, one seed.
"""
from __future__ import annotations

import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                                  # noqa: E402

PARENT = "pipeline/jobs/ep2-b19-w4motion-0822.yaml"
SPEC_ID = "ep2-b19-dropmotion-r2-0822"

OLD_SRC = ("C:\\banyan-farm\\courier-box\\farm-out\\ep2-b19-canon-w4-0821"
           "\\ep2-b19-canon-w4-0821-ipahead.png")
OLD_SHA = "b763a62cc182c88511d37e2c12eeea9a4dd21a2378f5cf80fc78899f41263ba0"
# THE ONLY EDIT: the init moves from the 08-19 sapgloss plate to this morning's
# fignat r2. Same fig, same plant, same action, same everything -- but drawn on
# the CURRENT plate, which is what the parent's own verdict named as its
# successor: "the plate betrays its age -- sapgloss is from 08-19 and predates
# the goblin correction, so the face in it was never his, and it is replaced
# within 25 frames anyway."
NEW_SRC = ("C:\\banyan-farm\\courier-box\\farm-out\\ep2-b19-fignat-r2-0822"
           "\\b19-fignat-r2-s20260820.png")
NEW_SHA = "3666c0a0a182c3c2f8e2faa289341a9e74886492a6019f15cbcb2b7f06eeca08"

OLD_ACTION = (
    "THE ACTION: his lifted foot comes down, his weight settles back over it, "
    "and he leans a little further down toward the grass at his heel -- foot "
    "down, weight back, lean in. HALFWAY THROUGH the foot has landed, his "
    "weight is still shifting and his head is already low.")

# Every object named here is IN the sapgloss init: the stem, the leaves and the
# one violet fig were drawn into it and naturalised. That is the licence.
NEW_ACTION = (
    "THE ACTION: the small violet fig hangs on the thin stem beside him, then "
    "it comes loose and falls, and it lands in the grass below. He turns his "
    "head down toward where it landed and KEEPS LOOKING at it for the rest of "
    "the clip. The plant stays rooted where it is and the camera does not move. "
    "HALFWAY THROUGH the fig is in the air between the stem and the ground and "
    "his head has started down.")

BAR = (
    "THE BEAT'S OWN done_when, IN ORDER, AND IT IS THREE EVENTS: the fruit "
    "STARTS ON THE STEM, it FALLS, it LANDS ON THE GROUND, and HE NOTICES it. "
    "PRE-REGISTERED: "
    "(1) THERE IS A FRUIT IN THE FIRST FRAME AND IT IS ON THE STEM. Tonight's w4 "
    "take had no fruit anywhere and that is the whole reason this exists. "
    "(2) IT LEAVES THE STEM AND REACHES THE GROUND inside the clip. A fruit that "
    "is on the stem at the first frame and on the stem at the last is a FAIL. "
    "(3) HE NOTICES -- his head goes down toward it AFTER it lands, not before. "
    "This is the clause the plate that passed 8 of 8 could never deliver, because "
    "that job drew a still. "
    "(4) NO CONTACT WITH HIS BODY. The beat's definition says a take where the "
    "fruit touches him FAILS this beat now, however well it moves. "
    "(5) EXACTLY ONE fruit, and the plant stays rooted and single. "
    "(6) The canon face survives to the LAST frame: broad dome, small off-white "
    "almond eyes with dark pupils, near-horizontal ears. "
    "PRE-REGISTERED FAIL MODES: THE STILL-FALL-STILL SHAPE, which is EXPECTED "
    "rather than feared -- a fall is inherently one-shot, tonight measured that "
    "one-shot actions park, and beat 13 measured that putting a count on an "
    "action that cannot repeat makes it worse. If all three events land in order "
    "this is a PASS even with a held head and tail. THE FRUIT NOT MOVING AT ALL, "
    "which would say i2v will not animate a composited object and the drop needs "
    "to be authored frame by frame. THE PLANT DRIFTING OR GROWING, which the "
    "composite was built to stop. And the fruit falling ONTO him, which the "
    "definition rules out by name.")


def build():
    child = derive_spec.derive(
        src=PARENT,
        new_id=SPEC_ID,
        fresh={
            "owner": ("night iteration lane, 2026-08-22 -- the ladder's "
                      "named-not-fired beat 19 motion, on the plate that has the "
                      "fruit in it"),
            "consumer": (
                "BEAT 19's SLATE, which has been a slate since 08-15 and which "
                "tonight's w4 clip could not close because the object the beat is "
                "ABOUT was not in the plate. This is the first time this beat has "
                "had motion asked of an init that contains a fruit on a stem. If "
                "it lands, beat 19 has a candidate for the first time; if it does "
                "not, the failure says whether i2v will animate a composited "
                "object at all, which nothing in this tree has ever asked."),
            "success": BAR,
            "why": (
                "NAMED ON 08-19 AND NEVER FIRED: the ladder's beat-19 entry ends "
                "'still named, not fired: this plate's motion wants --image-crf "
                "10, not 33'. Tonight made it urgent. The w4 motion clip failed "
                "for having NO FRUIT IN IT -- the plate was authored for the face "
                "and nobody put the fig back, the same prompt-summons law that "
                "pulled beats 02, 03 and 20 off their framing. The sapgloss plate "
                "is the one that does not have that problem: the plant and the "
                "fig were DRAWN into the field in PIL and settled with a "
                "0.22-strength pass, and it scored 8 of 8 on a bar written before "
                "the tool that made it existed. ONE VARIABLE: the init. The action "
                "is rewritten because the old one describes a foot and a lean and "
                "this beat is about a fruit -- and it may now name the fig, the "
                "stem and the leaves, because this init CONTAINS them. $0, ~4 GPU "
                "minutes. Full trace: pipeline/derive_b19_dropmotion_0822.py."),
        },
        extra={
            "the_one_variable": (
                "THE INIT, from a face plate with no plant in it to the composite "
                "plate that passed 8 of 8 with a rooted stem, two leaves, a "
                "side-branch and one matte violet fig. The action changes with it "
                "and that is not a second variable being smuggled -- the old "
                "sentence describes a foot and a lean, and the beat is a fruit "
                "falling; a foot sentence over a fruit plate would measure "
                "nothing."),
            "why_the_wording_may_name_objects": (
                "THIS WAVE'S FIRST LAW is that a prompt naming an object its init "
                "does not contain makes the model build the object and re-frame "
                "the shot to fit it -- beat 04 rotated ninety degrees onto its "
                "side over a trunk that was not there, tonight. The sapgloss init "
                "CONTAINS the fig, the stem and the leaves, so naming them is "
                "description and not summons. --selftest asserts the init being "
                "pointed at is the sapgloss one, because that assertion is the "
                "entire licence for the wording."),
            "expected_shape_stated_in_advance": (
                "STILL, FALL, STILL. A fall is inherently one-shot; tonight "
                "measured that one-shot actions park, and beat 13 measured that "
                "putting a count on an action that cannot happen twice makes it "
                "WORSE. So no count is put on this one. The tail is given "
                "something to do instead -- he keeps looking at where it landed -- "
                "which is the only lever tonight's evidence supports. If the three "
                "events land in order, the bar calls that a pass even with a held "
                "tail, because the beat's definition is about ORDER and not about "
                "filling a runtime."),
            "crf_note": (
                "--image-crf 10 is inherited from the parent's render step and is "
                "asserted rather than assumed, because the ladder's named change "
                "for this beat WAS the crf and a child that silently ran at 33 "
                "would look like the rung having been fired when it had not."),
        },
        by="pipeline/derive_b19_dropmotion_r2_0822.py",
    )

    steps = []
    for st in child.get("steps") or []:
        argv = [str(a) for a in (st.get("argv") or [])]
        if st.get("name") == "crop":
            if OLD_SRC not in argv or OLD_SHA not in argv:
                raise SystemExit("!! the parent's crop step does not name the w4 "
                                 "plate and its sha where expected: %r" % (argv,))
            argv = [NEW_SRC if a == OLD_SRC else
                    (NEW_SHA if a == OLD_SHA else a) for a in argv]
            st = dict(st, argv=argv)
        steps.append(st)
    child["steps"] = steps

    pay = dict(child.get("payload") or {})
    keys = [k for k in pay if k.endswith("b19-motion-prompt.txt")]
    if len(keys) != 1:
        raise SystemExit("!! expected one motion prompt in the payload, found %r"
                         % (sorted(pay),))
    text = pay[keys[0]]
    if OLD_ACTION not in text:
        raise SystemExit("!! the parent's action is not in its payload verbatim "
                         "-- refusing to guess at a replacement")
    pay[keys[0]] = text.replace(OLD_ACTION, NEW_ACTION)
    child["payload"] = pay
    return child


def _selftest():
    spec = build()
    argv = spec["steps"][0]["argv"]
    # THE LICENCE FOR THE WORDING. Every object the action names is in THIS init
    # and in no other, so the init is asserted before the words are allowed.
    assert NEW_SRC in argv and NEW_SHA in argv, "the init is not the fignat r2 plate"
    assert OLD_SRC not in argv and OLD_SHA not in argv, "the w4 plate survived"
    assert "fignat-r2" in NEW_SRC

    key = [k for k in spec["payload"] if k.endswith("b19-motion-prompt.txt")][0]
    text = spec["payload"][key]
    assert NEW_ACTION in text and OLD_ACTION not in text
    parent = derive_spec.load(os.path.join(REPO, PARENT))
    pkey = [k for k in parent["payload"] if k.endswith("b19-motion-prompt.txt")][0]
    ptext = parent["payload"][pkey]
    # The head clause carries the corrected eye and may not move.
    assert text.split("THE ACTION:")[0] == ptext.split("THE ACTION:")[0]
    assert "eyebags" in text and "almond eyes" in text

    # The three events the beat's definition asks for, in the sentence.
    for term in ("hangs on the thin stem", "falls", "lands in the grass",
                 "turns his head down"):
        assert term in NEW_ACTION, term
    # NO CONTACT. The definition rules out a fruit that touches him, so the
    # sentence must not stage one.
    for banned in ("into his hand", "onto him", "catches", "in his hands"):
        assert banned not in NEW_ACTION.lower(), banned
    # NO COUNT. Beat 13 measured tonight that a count on an unrepeatable action
    # makes it worse, and a fall cannot happen twice.
    assert "twice" not in NEW_ACTION.lower()

    # THE LADDER'S NAMED CHANGE, asserted rather than assumed.
    render = [s for s in spec["steps"] if s.get("name") == "render"][0]
    rargv = [str(a) for a in render["argv"]]
    assert rargv[rargv.index("--image-crf") + 1] == "10", "the crf rung is the point"

    for k in spec:
        assert "verdict" not in k and "pick" not in k, k
    operational = derive_spec._dump(
        {k: spec[k] for k in ("payload", "steps", "artifacts") if k in spec})
    assert parent["id"] not in operational, "the parent's paths survived"
    print("SELFTEST OK  %s  init=%s crf=10" % (SPEC_ID, NEW_SHA[:12]))
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
