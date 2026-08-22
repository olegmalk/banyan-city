#!/usr/bin/env python3
r"""GUARD-2, ROUND 4 SAMPLE — one frame that tests the term round 3 blamed.

    python3 pipeline/derive_guardcast4_sample_0822.py --selftest
    python3 pipeline/derive_guardcast4_sample_0822.py --write

ONE FRAME, ONE VARIABLE, AND THE CELL IS CHOSEN SO THE ANSWER CANNOT BE LUCK.

Round 3 fixed the founder's defect -- no sweat drop, no steam, no drool on 14 of
15 frames -- and bought a new one with the wording that fixed it. Eight of the
fifteen came back with a hand clamped to the face, and TWO OF THOSE EIGHT, cells
G and I, HAD NO HAND IN ROUND 2 AT THE SAME SEED. That is the finding: the hand
is not the checkpoint's habit on portrait prompts, which is what rounds 2B, 2C
and 2D concluded from a seed sweep. It tracks the EXPRESSION. `slack open mouth`
plus `raised eyebrows` is not a dumb face in this caption distribution, it is a
DISTRESSED one, and distress comes with hands on the face, tears and a wince.

So the variable is `raised eyebrows`, and it is replaced by the term the goblin
work reached for the same problem from the other side. That file's note is
explicit about why: "`heavy sloped brow` is the anger, not the dumbness: a
lowered, forward-sloping brow is the anatomical signature of anger and the model
draws it as one. It becomes `thick eyebrows` -- still heavy, still non-cute, no
longer scowling". Round 3 fixed the anger by lifting the brow, which overshot
into anguish; `thick eyebrows` neutralises it instead of inverting it.

    round 3   slack open mouth, raised eyebrows, dull half-closed eyes
    round 4   slack open mouth, thick eyebrows, dull half-closed eyes

NOTHING ELSE MOVES. Same checkpoint, driver, negative bytes (the symbol family
stays -- it worked), 40 steps, cfg 7.5, 832x1216, same cell clause, same seed.

WHY CELL G AND NOT THE PRETTIEST CELL. F is round 3's best frame and would tell
us nothing: it was already clean. G is a CONTROL THAT HAS ALREADY FAILED ONCE --
clean in round 2, hand in round 3, same seed 20260731 throughout. If the brow
swap brings G back clean, the mechanism is confirmed and the next batch is
justified; if G still holds his face, the expression theory is wrong and no
batch should be spent on it. One frame, about 24 seconds, $0.

NO NEGATIVE TERMS ARE ADDED FOR THE HAND, deliberately. Round 2C already spent a
render proving that `hand on own face`, `head rest` and `hand up` do not remove
it, and tokens spent re-proving a null result are tokens taken off the tail of a
negative that is currently doing its job.

Filed to BACKLOG so it cannot jump anything the founder is waiting on.
"""
from __future__ import annotations

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                                  # noqa: E402
import derive_guardcast3_0822 as r3                                 # noqa: E402

CELL = "g"
EXPRESSION = "slack open mouth, thick eyebrows, dull half-closed eyes"
SPEC_ID = "ep2-guardcast4-g-0822"


def positive():
    return ("1boy, a grown guard man, mature male face, %s, %s, close on his "
            "face, cream shirt collar, white shoulder sash, tall grass, "
            "hedgerow behind, cinematic lighting, masterpiece, best quality, "
            "very aesthetic" % (r3.body_of(CELL), EXPRESSION))


def build():
    return derive_spec.derive(
        src="pipeline/jobs/%s.yaml" % r3.spec_id(CELL, 0),
        new_id=SPEC_ID,
        fresh={
            "owner": ("guard lane, 2026-08-22 -- round 4 sample, filed the "
                      "moment round 3's sheet was judged"),
            "consumer": (
                "THE STEWARD, as the gate on whether a round-4 BATCH is worth "
                "the card. Its reader is the decision, not the founder: he is "
                "choosing between round 3's five men on "
                "/review/ep2-guardcast2-0822 right now and this frame does not "
                "go on that page unless he says none. Nothing downstream "
                "consumes it."),
            "success": (
                "ONE 832x1216 png at seed %d, scored at 1:1. THE ONLY QUESTION "
                "IS THE HAND, because this cell is a control that has already "
                "failed: G was CLEAN in round 2 at this seed and came back with "
                "a hand on his face in round 3, and the brow term is the only "
                "thing being blamed. PASS = no hand in frame AND no symbol on "
                "the face AND the face still reads slack rather than sharp. A "
                "pass justifies a round-4 batch of ten; a fail kills the "
                "expression theory and the next round moves something else."
                % r3.seed_of(CELL, 0)),
            "why": (
                "GUARD 2, ROUND 4 SAMPLE: `raised eyebrows` -> `thick "
                "eyebrows`, one term, nothing else. Round 3's symbol strip "
                "worked -- 14 of 15 frames clean of sweat, steam and drool -- "
                "but its replacement expression read as DISTRESS, and distress "
                "brings hands: 8 of 15 held their face, including G and I which "
                "were clean at the same seeds in round 2. That rules out the "
                "checkpoint-prior explanation rounds 2B/2C/2D settled on and "
                "points at the wording. `thick eyebrows` is the goblin work's "
                "answer to the same brow problem -- heavy, non-cute, not "
                "scowling -- where `raised` overshot into anguish. $0, one "
                "frame. Full reasoning in "
                "pipeline/derive_guardcast4_sample_0822.py."),
        },
        overrides={"payload:prompt.txt": positive()},
        retoken=[(r3.spec_id(CELL, 0), SPEC_ID)],
        extra={"cell": ("round 4 sample, cell G. Reasoning: "
                        "pipeline/derive_guardcast4_sample_0822.py.")},
        by="pipeline/derive_guardcast4_sample_0822.py",
    )


def _selftest():
    print("derive_guardcast4_sample_0822 selftest")
    import clip_token_count as ctc
    c = ctc.Clip()
    p = positive()
    n = c.count(p)[0]
    assert n <= 75, "positive is %d of 75" % n
    assert "raised eyebrows" not in p, "the variable did not move"
    assert "thick eyebrows" in p and "slack open mouth" in p
    assert r3.body_of(CELL) in p, "cell G's own clause is gone"
    # ONE variable: everything except the brow term must match round 3's cell G.
    before = r3.positive(CELL).replace("raised eyebrows", "thick eyebrows")
    assert before == p, ("more than the brow term moved:\n  r3 %s\n  r4 %s"
                         % (r3.positive(CELL), p))
    print("  ok  positive %d/75, exactly one term changed vs round 3 cell G" % n)

    spec_path = os.path.join(REPO, "pipeline", "jobs", "%s.yaml" % SPEC_ID)
    if os.path.isfile(spec_path):
        got = derive_spec.load(spec_path)
        pay = got.get("payload") or {}
        assert any(k.endswith("prompt.txt") and v == p for k, v in pay.items()), (
            "emitted spec carries a stale prompt")
        assert any(k.endswith("negative.txt") and v == r3.NEGATIVE
                   for k, v in pay.items()), (
            "the symbol negative must be INHERITED unchanged -- it is the part "
            "of round 3 that worked")
        cast = [s for s in got["steps"] if s["name"] == "cast"][0]["argv"]
        assert cast[cast.index("--seed") + 1] == str(r3.seed_of(CELL, 0)), (
            "the seed moved; then this is not an A/B against round 3's G")
        assert cast[cast.index("--task") + 1] == SPEC_ID
        print("  ok  emitted spec: current prompt, inherited negative, seed held")
    print("SELFTEST: PASS")
    return 0


if __name__ == "__main__":
    if "--write" in sys.argv:
        p = derive_spec.write(build(), "pipeline/jobs/%s.yaml" % SPEC_ID,
                              force="--force" in sys.argv)
        print("wrote", os.path.relpath(p, REPO))
        sys.exit(0)
    sys.exit(_selftest())
