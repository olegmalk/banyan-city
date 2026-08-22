#!/usr/bin/env python3
r"""BEAT 06's FIRST MOTION OFF A PLATE THAT CONTAINS THE BOARD.

    python3 pipeline/derive_ep2_b06motion_0822.py --selftest
    python3 pipeline/derive_ep2_b06motion_0822.py --write

WHY THIS IS FILED NOW AND NOT LAST WEEK. Beat 06 has two faults. The first is
the board's SIZE and it was answered this morning in `ep2-b06-boardnat-r3-0822`:
a hand-sized slab of bark, drawn into the plate at 160x115 px and settled in at
0.45, held in both hands at chest height by the man the founder picked. The
second fault is that **4.54 s of a 6.46 s slot is one frozen frame** -- the
biggest ratio in the episode, and 59 of 107 frame pairs bit-identical.

That second fault has never been askable. Every motion attempt on this beat has
been asked of a plate with no board in it, and the beat's action IS "turns the
bark board over and reads off it": you cannot render a man reading an object
that is not in the picture. This wave's first law says the same thing from the
other side -- a prompt naming an object its init lacks makes the model build the
object and re-frame the shot to fit it, which is what pulled beats 02, 03, 19 and
20 off their framing. The init now contains the object, so the sentence is
description rather than summons, and `--selftest` asserts the init before the
wording is allowed.

TWO THINGS ARE NEW HERE AND BOTH ARE NAMED
------------------------------------------
This beat has NO motion parent to be one-variable against -- it has zero clips
of any kind off any modern plate -- so the LTX chain is taken whole from
`ep2-b12-tightB-0813` (crop, encode, render, publish; 121 frames, 24 fps,
704x1280, guidance and seed untouched) and only the init and the two text
payloads are authored. Stated plainly rather than dressed as one variable.

THE ACTION CARRIES THE COUNT FINDING, and this is the first application of it
since the rung that produced it. 2026-08-22's measurement: **a countable action
fills the runtime and an instruction to go slowly does not.** `ep2-b17-repeat`
went from 89 of 104 frame pairs under 0.5 to 52 on one edit -- a repeat COUNT --
and the correction that followed narrowed the rule: *a counted repeat fills the
runtime only when the action can actually happen twice.* b13's settle-and-never-
rise could not, and got worse.

**A fingertip running down a board can happen twice.** It is the same shape as
b17's brush, which is the one clean win the finding has. So the action names the
turn once (it is one-shot by nature) and the READ twice, which is the half of the
runtime the frozen frame currently occupies.

$0 to derive. ~5 GPU minutes.
"""
from __future__ import annotations

import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                            # noqa: E402

PARENT = "pipeline/jobs/ep2-b12-tightB-0813.yaml"
SPEC_ID = "ep2-b06-boardmotion-0822"
OUT_MP4 = "06-the-clipboard-LTX-boardmotion-0822.mp4"

OLD_SRC = r"C:\banyan-farm\plates-local\12-related-r4-s2.png"
OLD_SHA = "cc6bd5f0c0cc116d3cb6530a9bae81ac5b5593a683e4e80e20d6319e0cc0c074"
NEW_SRC = (r"C:\banyan-farm\courier-box\farm-out\ep2-b06-boardnat-r3-0822"
           r"\b06-boardnat-r3-s20260820.png")
NEW_SHA = "51e0bfe5588cf522530e085e898cce5859bda651b2154ad58dcf4d14af4af89e"

POSITIVE = (
    "2D anime, hand-drawn cel animation, static locked framing, the frame never "
    "moves, flat cel shading, clean ink linework, anime key art. Subject already "
    "in frame: ONE grown man, alone, standing in tall summer grass in bright "
    "daylight -- dark cropped hair, round wire-rim glasses, a cream shirt -- "
    "holding a SMALL HAND-SIZED SLAB OF ROUGH BROWN BARK in both hands at chest "
    "height, his head bowed over it. The board is no bigger than his own "
    "forearm and it stays that size: it is a hand-sized bark tablet, not a "
    "shield, not a sign and not a plank. The field, the grass and the sky "
    "behind him are already drawn and do not change. THE ACTION: he turns the "
    "bark board face-up in both hands, brings it to a reading distance at his "
    "chest, and reads it -- his fingertip runs down the face of the board "
    "TWICE, and his lips move while he reads. HALFWAY THROUGH the board is "
    "face-up at his chest and his finger is partway down it for the first time. "
    "He stays where he is, the camera stays where it is, and nobody else enters "
    "the shot. Bright clear daylight, cinematic lighting, detailed, newest, "
    "masterpiece, best quality, very aesthetic.")

NEGATIVE = (
    "giant board, oversized board, board filling the frame, prop larger than "
    "his torso, shield, raising the board to his face, sign, banner, plank, "
    "clipboard, metal clip, spring clip, white paper, glowing board, luminous "
    "panel, lens flare, second man, second guard, a pair, duplicate character, "
    "goblin, green skin, pointed ears, creature, animal, helmet, armour, "
    "weapon, dark, dusk, dim lighting, night, white background, blank "
    "background, background appearing, scene forming, dissolve, iris, wipe, "
    "camera pan, camera tilt, panning, tilting, camera movement, dolly, zoom, "
    "push in, pull back, walking out of frame, leaving the frame, drifting "
    "sideways, scene change, shot change, new camera angle, face morphing, "
    "distorted face, warped face, extra eyes, extra ears, hair changing, "
    "photorealistic, 3D render, CGI, live action, motion blur, text")

BAR = (
    "BEAT 06'S OWN done_when, WHICH IS: 'the guard turns the bark board over and "
    "reads off it; board hand-sized and readable; field present at frame one; no "
    "white burst at the head of the clip.' PRE-REGISTERED: "
    "(1) THE BOARD IS IN THE FIRST FRAME AND IT IS HAND-SIZED. It is in the init, "
    "so it should be; the thing being tested is whether it STAYS that size for "
    "121 frames. The beat's whole history is the prop inflating -- if it grows "
    "into a shield or a sign this is a FAIL, and it is the most likely one. "
    "(2) HE TURNS IT AND READS OFF IT. A turn, then a read at chest height with "
    "the head down. Raising it in front of his face is beat 10's move and a FAIL "
    "here -- the second seed of the shipped take did exactly that. "
    "(3) THE CLIP IS NOT A FROZEN FRAME. The take in the cut is 59 of 107 frame "
    "pairs bit-identical and 4.54 s of held picture; this rung exists to answer "
    "that, and the measurement is the share of frame pairs under 0.5 mean "
    "interframe difference at 176x320, the same instrument the 08-22 wave used. "
    "The counted read is the lever and the number is the score. "
    "(4) THE FIELD IS PRESENT AT FRAME ONE and there is no white burst. The init "
    "is a finished daylit field, so a white head would be a new fault. "
    "(5) ONE MAN, and he is the man in the plate to the last frame -- dark "
    "cropped hair, round wire-rim glasses, cream shirt. "
    "PRE-REGISTERED FAIL MODES. THE PROP INFLATES, which is this beat's oldest "
    "fault and which no wording has ever held; if it fires on an init that "
    "CONTAINS a correctly sized board, that is a much stronger result than "
    "another wording failure and it says the composite route does not protect "
    "scale through motion. THE COUNT DOES NOTHING, which would narrow the 08-22 "
    "count finding again: a fingertip down a board is the same shape as beat "
    "17's brush, so if it fails here the rule is smaller than 'an action with a "
    "natural cycle'. THE BOARD DISSOLVES -- a composited object has been shown "
    "to MOVE (beat 19's fig fell) and to KEEP ITS SHAPE (beat 12's leaves held "
    "121 frames), but neither of those was a made object with a flat readable "
    "face. And THE HANDS, which are directly under the board and which every "
    "i2v pass in this tree finds difficult.")


def build():
    child = derive_spec.derive(
        src=PARENT,
        new_id=SPEC_ID,
        fresh={
            "owner": "morning compositor lane, 2026-08-22",
            "consumer": (
                "BEAT 06's SLOT IN /review/ep2-beats-0821 and, if it lands, the "
                "cut. This beat has zero clips on any modern plate and its "
                "shipped take is 1.92 s of picture in a 6.46 s slot. A pass "
                "here is the first candidate; nothing in review/ep2-ship-0821 "
                "changes because it landed."),
            "success": (
                "ONE 704x1280 mp4, 121 frames at 24 fps, in which a grown man "
                "in a daylit field TURNS a hand-sized bark board and READS off "
                "it at chest height, the board stays hand-sized to the last "
                "frame, and the clip is not a frozen frame with a runtime. "
                "Scored on the share of frame pairs under 0.5 mean interframe "
                "difference at 176x320 against the shipped take's 59 of 107 "
                "bit-identical."),
            "why": (
                "BEAT 06'S SECOND FAULT BECOMES ASKABLE TODAY.\n\n"
                "Fault one is the board's size and it was answered this morning: "
                "ep2-b06-boardnat-r3-0822 has a hand-sized slab of bark drawn "
                "into the plate at 160x115 px and settled in at 0.45, held in "
                "both hands at chest height by the man the founder picked, on a "
                "plate rendered with NO reference image and NO board net -- the "
                "ControlNet route for this object was closed at three rungs "
                "this morning after returning, in order, a glowing ball, a "
                "plank standing on the ground and a lit panel that ate the "
                "figure.\n\n"
                "Fault two is that 4.54 s of a 6.46 s slot is ONE FROZEN FRAME, "
                "the biggest ratio in the episode, 59 of 107 frame pairs "
                "bit-identical. It has never been askable, because the beat's "
                "action is 'turns the bark board over and reads off it' and no "
                "plate has ever contained a board. The init contains one now, "
                "so the sentence is description and not summons -- and the "
                "selftest asserts the init before the wording is allowed, "
                "because that assertion is the whole licence.\n\n"
                "THE ACTION CARRIES THE COUNT FINDING and this is its first "
                "application since the rung that produced it: a countable "
                "action fills the runtime, an instruction to go slowly does "
                "not, and a counted repeat only works when the action can "
                "actually happen twice. A fingertip running down a board can. "
                "$0, ~5 GPU minutes."),
        },
        overrides={
            "key:beat": 6,
            "key:priority": 14,
            "key:script_line": (
                "Beat 06 THE CLIPBOARD: the guard turns the bark board over and "
                "reads it. Node 002b-first-citizen, live script 002b-t0-c, "
                "approved_by founder 2026-08-03."),
        },
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THERE IS NO ONE VARIABLE AND SAYING SO IS THE HONEST FILING. "
                "Beat 06 has no motion parent -- zero clips off any modern "
                "plate -- so the LTX chain is taken WHOLE from "
                "ep2-b12-tightB-0813 (crop, encode, render, publish; 121 "
                "frames, 24 fps, 704x1280; guidance, seed and driver "
                "untouched) and three things are authored: the init, the "
                "positive and the negative. That is a first sample on a beat "
                "with nothing under it, not a rung on a ladder, and it is "
                "filed as one."),
            "init_provenance": (
                "farm-out/ep2-b06-boardnat-r3-0822/b06-boardnat-r3-s20260820."
                "png, 832x1216, cover-cropped to 704x1280 by the parent's own "
                "crop step. Its lineage: ep2-b06-pose-r4-0822 (openpose only, "
                "no reference image, no board net, hands deliberately EMPTY) "
                "-> pipeline/beat06_board_composite.py (a 160x115 px bark slab "
                "drawn in PIL, hue from canon, value/ink/light measured off the "
                "plate, four geometry refusals) -> a 0.45 masked naturalize. "
                "The file is already in the courier from its own publish step, "
                "so this job needs no fetch."),
            "failure_predicted_in_advance": (
                "See `bar`. The one worth repeating here because it decides "
                "what the next rung is: IF THE PROP INFLATES OFF AN INIT THAT "
                "CONTAINS A CORRECTLY SIZED BOARD, the composite route does not "
                "protect scale through motion, and that is a bigger and more "
                "useful finding than another wording failure would be."),
            "not_done_on_purpose": (
                "NO SECOND SEED. The shipped take's own record says its seedB "
                "raised the board like a shield instead of reading it, and that "
                "a one-seed pick is not a confirmation. A second seed is the "
                "right next job and it is NOT filed with this one, because "
                "firing two seeds before anyone has looked at either is how a "
                "recipe gets scaled on an unapproved result."),
        },
        by="pipeline/derive_ep2_b06motion_0822.py",
    )

    steps, hit = [], 0
    for st in child.get("steps") or []:
        argv = [str(a) for a in (st.get("argv") or [])]
        if st.get("name") == "crop":
            if OLD_SRC not in argv or OLD_SHA not in argv:
                raise SystemExit("!! the parent's crop step does not name the "
                                 "shared plate and its sha: %r" % (argv,))
            argv = [NEW_SRC if a == OLD_SRC else
                    (NEW_SHA if a == OLD_SHA else a) for a in argv]
            hit += 1
            st = dict(st, argv=argv)
        steps.append(st)
    if hit != 1:
        raise SystemExit("!! expected exactly one crop step, hit %d" % hit)
    child["steps"] = steps

    # THE PUBLISH DIRECTORY AND THE OUTPUT FILENAME ARE THE PARENT'S AND THE
    # RETOKEN DOES NOT REACH THEM, and this cost a real collision. derive_spec's
    # retoken maps the parent ID (ep2-b12-tightB-0813) to the child, but the
    # parent's publish step writes to `ep2-b12-tightB` -- a SHORTER token that
    # the parent id does not contain -- and its render json names the output
    # `12-related-LTX-leaf-0813.mp4`. So this job published a BEAT 06 clip into
    # a beat 12 directory under a beat 12 filename, on top of a beat 12 clip
    # rendered forty minutes earlier. Nothing was lost (the b12 clip was already
    # staged and committed under review/), but a courier directory whose name
    # lies about whose pixels are in it is exactly what 7.2 exists to prevent.
    # Both tokens are retargeted here and both are asserted in --selftest.
    steps2 = []
    for st in child["steps"]:
        argv = [str(a) for a in (st.get("argv") or [])]
        argv = [a.replace("courier-box/farm-out/ep2-b12-tightB",
                          "courier-box/farm-out/" + SPEC_ID)
                 .replace("12-related-LTX-leaf-0813.mp4", OUT_MP4)
                for a in argv]
        steps2.append(dict(st, argv=argv))
    child["steps"] = steps2

    pay = dict(child.get("payload") or {})
    for k in list(pay):
        if isinstance(pay[k], str):
            pay[k] = pay[k].replace("12-related-LTX-leaf-0813.mp4", OUT_MP4)
    child["payload"] = pay
    child["artifacts"] = [str(a).replace("12-related-LTX-leaf-0813.mp4", OUT_MP4)
                          for a in (child.get("artifacts") or [])]

    pay = dict(child.get("payload") or {})
    pk = [k for k in pay if k.endswith("motion-prompt.txt")]
    nk = [k for k in pay if k.endswith("negative.txt")]
    if len(pk) != 1 or len(nk) != 1:
        raise SystemExit("!! expected one prompt and one negative: %r"
                         % (sorted(pay),))
    pay[pk[0]] = POSITIVE
    pay[nk[0]] = NEGATIVE
    child["payload"] = pay
    return child


def _selftest():
    spec = build()
    crop = [s for s in spec["steps"] if s.get("name") == "crop"][0]
    argv = [str(a) for a in crop["argv"]]
    # THE LICENCE FOR THE WORDING: every object the action names is in THIS
    # init. Asserted before the sentence is allowed, exactly as the b19 drop
    # rung asserted its sapgloss plate.
    assert NEW_SRC in argv and NEW_SHA in argv, "the init is not the r3 board plate"
    assert OLD_SRC not in argv and OLD_SHA not in argv, "the old plate survived"
    assert "boardnat-r3" in NEW_SRC
    assert NEW_SHA != "PLACEHOLDER", "the init sha was never filled in"

    pk = [k for k in spec["payload"] if k.endswith("motion-prompt.txt")][0]
    text = spec["payload"][pk]
    # The size clause is the beat's fault and must be in the POSITIVE, not only
    # banned in the negative -- nine firings of the positive-placement law.
    for term in ("HAND-SIZED", "no bigger than his own forearm",
                 "turns the bark board face-up", "TWICE"):
        assert term in text, term
    # ...and banned as well, because on this beat the negative has failed alone
    # and the positive has failed alone, so both are carried.
    nk = [k for k in spec["payload"] if k.endswith("negative.txt")][0]
    for term in ("giant board", "oversized board", "shield"):
        assert term in spec["payload"][nk], term
    # No count on the TURN. A turn is one-shot and the b13 null measured that a
    # count on an action that cannot repeat makes the clip worse.
    assert "turns the bark board face-up in both hands" in text
    assert "turns the bark board over twice" not in text.lower()
    blob = str(spec)
    assert "12-related-LTX-leaf-0813.mp4" not in blob, (
        "the parent's output filename survived -- a beat 06 clip would publish "
        "under a beat 12 name")
    assert "farm-out/ep2-b12-tightB" not in blob, (
        "the parent's publish directory survived -- a beat 06 clip would land "
        "in a beat 12 directory")
    assert OUT_MP4 in blob
    print("SELFTEST OK  %s  init=%s  pos=%d chars neg=%d chars"
          % (SPEC_ID, NEW_SHA[:12], len(text), len(spec["payload"][nk])))
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
    print("wrote", os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
