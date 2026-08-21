#!/usr/bin/env python3
r"""GUARD-2 CASTING, ROUND 2C — the five hand-on-cheek cells, re-drawn at the same seed.

    python3 pipeline/derive_guardcast2c_0822.py --selftest   # assert, write nothing
    python3 pipeline/derive_guardcast2c_0822.py --write      # emit the five specs

THE MEASUREMENT THAT PRODUCED THIS ROUND. Round 2B drew all ten cells with the
IP-Adapter removed. The identity collapse was gone -- ten different grown men,
none of them guard 1 -- but FIVE OF THE TEN still came back with a hand pressed
against the cheek: A, B, D, H, J. Clean: C, E, F, G, I.

FIVE OF TEN IS THE FINDING, AND IT IS WHY THIS ROUND EXISTS RATHER THAN A SHRUG.
The round-2 sample had one hand and one plausible cause -- the IP-Adapter
reference, in which guard 1 holds his own cheek. Removing the adapter should
then have removed the hand, and it removed exactly half of them. So the
reference was never the whole cause: `hands` in the negative DOES NOT BIND THE
POSE. It negates a rendered hand as an object; it does not oppose "man resting
his face on his hand", which is a composition this model reaches for
constantly on a head-and-shoulders portrait. Ten frames at ten seeds is enough
to say that is a wording gap and not seed luck, and the split -- five and five,
across every hair and build in the sheet -- is what rules seed luck out.

WHAT ROUND 2C CHANGES, AND IT IS ONE THING. The negative gains three POSE terms
in the model's own tag dialect, where round 2B had only the object noun:

    + hand on own face,  + head rest,  + hand up

and pays for them by dropping three terms that were already dead weight, which
is stated rather than smuggled: a DUPLICATE `text` that beat_negative appends
after the tail, `photorealism` (a second spelling of `photorealistic`, already
first in the list), and `plain background` (`white background` stays, and all
ten 2B frames came back with real grass, so nothing is defended by it). Measured
on animagine-xl-3.1's own vocab: 73 of 77, down from 2B's 75.

EVERYTHING ELSE IS HELD, INCLUDING THE SEED, AND THE SEED IS THE POINT. Each
cell re-draws AT ITS ROUND-2B SEED -- A at 20260725, B at 20261725, D at
20263725, H at 20267725, J at 20269725. Same positive bytes, same driver, same
40 steps at cfg 7.5, same 832x1216. So each of the five is a TRUE A/B against a
frame that already exists on disk: if the hand goes and the man stays, the three
words did it, and nothing else could have. A new seed would have made every
result unreadable -- a different picture is not evidence about a negative.

THE FIVE CLEAN CELLS ARE NOT RE-RUN. C, E, F, G and I already pass the hand
clause and re-drawing them under a changed negative would throw away five
frames the founder can look at tonight to buy consistency he cannot see. The
sheet is therefore five 2B frames and five 2C frames, and the page says so per
cell rather than pretending to a uniformity it does not have.

ONE SAMPLE FIRST, AGAIN: cell A alone, looked at at 1:1 beside its own 2B twin,
before the other four fire. Third time tonight, and the first two both paid for
themselves -- round 2's sample caught an identity collapse, and round 2B's
caught `arm` being a magic string.

$0 -- local card, no provider, no spend. The pick is R4 and it is the founder's.
"""
from __future__ import annotations

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                                  # noqa: E402
import derive_guardcast2_0822 as r2                                 # noqa: E402
import derive_guardcast2b_0822 as r2b                               # noqa: E402

# The five that came back holding their own face, judged at 1:1 on 2026-08-22.
HAND_CELLS = ("a", "b", "d", "h", "j")
# The five that did not, and which are NOT re-run.
CLEAN_CELLS = ("c", "e", "f", "g", "i")

# Dropped to pay for the pose terms, each one dead weight and named as such.
DROP_NEG = ("photorealism",        # second spelling of `photorealistic`, already first
            "plain background")    # `white background` stays; all ten 2B frames had grass
# Added: the pose in the model's own dialect. `hands` alone negates the OBJECT.
POSE_NEG = ("hand on own face", "head rest", "hand up")


def spec_id(letter):
    return "ep2-guardcast2c-%s-0822" % letter


def work_dir(letter):
    return r"C:\banyan-farm\%s" % spec_id(letter)


def index_of(letter):
    return [c[0] for c in r2.CELLS].index(letter)


def body_of(letter):
    return dict(r2.CELLS)[letter]


def seed_of(letter):
    return r2.SEED_BASE + index_of(letter) * 1000


def negative():
    """2B's negative, de-duplicated, three terms out and three pose terms in."""
    _, neg = r2b.compiled("a")
    kept = []
    for part in (p.strip() for p in neg.split(",")):
        if part in kept or part in DROP_NEG:
            continue
        kept.append(part)
    return ", ".join(kept + list(POSE_NEG))


def build_root():
    letter = HAND_CELLS[0]
    pos, _ = r2b.compiled(letter)
    w = work_dir(letter)
    return {
        "id": spec_id(letter),
        "task": spec_id(letter),
        "node": r2.NODE,
        "beat": r2.BEAT,
        "runner": "box",
        "priority": 6,
        "needs_gpu": True,
        "max_attempts": 1,
        "sample": True,
        "est_minutes": 2,
        "needs": ["cuda", "vram12", "sdxl-venv"],
        "owner": ("guard lane, 2026-08-22 -- round 2C, the pose A/B, filed off a "
                  "five-of-ten count taken at 1:1 on the 2B sheet"),
        "consumer": (
            "THE FOUNDER, on /review/ep2-guardcast2-0822. Cell A is THE SAMPLE and "
            "its consumer is the decision to fire the other four: five of ten 2B "
            "cells came back holding their own face and this is the one change "
            "aimed at that. Guard 1 is not re-asked and review/ep2-ship-0821 is "
            "untouched."),
        "success": (
            "ONE 832x1216 png at seed %d, scored at 1:1 AND SIDE BY SIDE WITH ITS "
            "OWN 2B TWIN, which is the only reading that means anything here. THE "
            "PASS: (1) NO HAND anywhere in frame and no hand-on-face composition -- "
            "this is the whole question and a partial hand is a fail; (2) the man "
            "SURVIVES the change: still one grown male, still the same build and "
            "hair the clause asks for (%s), because a negative that fixes the pose "
            "by wrecking the subject has not fixed anything; (3) still detailed "
            "cinematic anime, still cream shirt collar and white shoulder sash, "
            "still a real grass background, still no glasses; (4) still not guard 1. "
            "PRE-REGISTERED FAIL MODES: the hand leaving and taking the arm and "
            "shoulder with it, cropping the costume out of frame; `head rest` "
            "reading as a pillow or a bed rather than a pose; the face flattening "
            "into a neutral portrait and losing the dumb read the brief asks for. "
            "A pass here is a CANDIDATE on the picker page and nothing more -- the "
            "cast is R4 and this job does not make it."
            % (seed_of(letter), body_of(letter))),
        "why": (
            "GUARD 2, CELL A RE-DRAWN AGAINST THE POSE: %s. Round 2B removed the "
            "IP-Adapter and the identity collapse went with it, but five of ten "
            "cells still rested a hand on the cheek -- so `hands` in the negative "
            "binds the OBJECT and not the COMPOSITION, which a head-and-shoulders "
            "portrait prompt reaches for on its own. Three pose terms go in (hand "
            "on own face, head rest, hand up) and three dead ones come out (a "
            "duplicate `text`, `photorealism` which already appears as "
            "`photorealistic`, and `plain background` which `white background` "
            "covers). 73 of 77 tokens, measured. THE SEED IS HELD AT %d so this is "
            "a true A/B against a frame already on disk. $0, local card. Full "
            "reasoning in pipeline/derive_guardcast2c_0822.py."
            % (body_of(letter), seed_of(letter))),
        "script_authority": (
            "Node 002b-first-citizen, live script `002b-t0-c`, `approved_by: founder`, "
            "`approved_on: 2026-08-03`. A STILL CASTING PLATE on an approved node: no "
            "voice, no motion, no episode assembly, no publication."),
        "script_line": ("Beat 06 THE CLIPBOARD: guard 2, the one with the bark board. "
                        "Head and shoulders, no prop -- the question is his FACE."),
        "env": dict(r2b.build_root()["env"]),
        "payload": {
            w + r"\prompt.txt": pos,
            w + r"\negative.txt": negative(),
        },
        "steps": [
            _stage_step(letter),
            {"name": "cast", "argv": _cast_argv(letter)},
            _publish_step(letter),
        ],
        "recipe_trace": (
            "Round 2B (pipeline/jobs/ep2-guardcast2b-%s-0822.yaml) with three pose "
            "terms added to the negative and three dead terms removed. Positive "
            "byte-identical, seed identical, driver pipeline/controlnet_plate.py at "
            "arm `nocontrol` so no ControlNet loads, no --ip-ref so no adapter "
            "loads. The 2B frame it is judged against is "
            "farm-out/ep2-guardcast2b-%s-0822/ep2-guardcast2b-%s-0822-nocontrol.png "
            "on origin/farm-results-rtx5090." % (letter, letter, letter)),
        "one_sample_rule": (
            "CELL A ALONE, then the other four. Third sample of the night and the "
            "first two both paid: round 2's caught an identity collapse that no "
            "metric would have flagged, round 2B's caught `arm` being a literal "
            "magic string in the driver. Twenty seconds each."),
        "artifacts": [w + r"\out\%s-nocontrol.png" % spec_id(letter)],
    }


def _stage_step(letter):
    body = r2b._stage_step(letter)["argv"][2].replace(
        r2b.work_dir(letter), work_dir(letter))
    return {"name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def _cast_argv(letter):
    w = work_dir(letter)
    return [
        r"C:\banyan-farm\venv\Scripts\python.exe",
        w + r"\src\pipeline\controlnet_plate.py",
        "--root", w + r"\src",
        "--task", spec_id(letter),
        "--arm", r2b.ARM,
        "--seed", str(seed_of(letter)),
        "--steps", "40",
        "--cfg", "7.5",
        "--width", "832",
        "--height", "1216",
        "--prompt-file", w + r"\prompt.txt",
        "--negative-file", w + r"\negative.txt",
        "--out", w + r"\out",
    ]


def _publish_step(letter):
    body = r2b._publish_step(letter)["argv"][2].replace(
        r2b.work_dir(letter).replace("\\", "/"), work_dir(letter).replace("\\", "/")
    ).replace(r2b.spec_id(letter), spec_id(letter))
    return {"name": "publish",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def sibling(letter):
    pos, _ = r2b.compiled(letter)
    return derive_spec.derive(
        src="pipeline/jobs/%s.yaml" % spec_id(HAND_CELLS[0]),
        new_id=spec_id(letter),
        fresh={
            "owner": ("guard lane, 2026-08-22 -- cell %s of round 2C, filed with the "
                      "batch that followed the cell-A pose sample" % letter.upper()),
            "consumer": (
                "THE FOUNDER, on /review/ep2-guardcast2-0822, as candidate %s of ten. "
                "Not a sample: cell A answered whether the pose terms work, and this "
                "cell only applies the answer to another of the five that held its "
                "own face." % letter.upper()),
            "success": (
                "ONE 832x1216 png at seed %d -- ITS OWN 2B SEED -- scored at 1:1 "
                "beside farm-out/ep2-guardcast2b-%s-0822/. The bar is cell A's, term "
                "for term: no hand and no hand-on-face composition, the man and his "
                "clause (%s) surviving the change, cinematic anime, cream shirt "
                "collar and white shoulder sash, no glasses, not guard 1."
                % (seed_of(letter), letter, body_of(letter))),
            "why": (
                "GUARD 2, CELL %s RE-DRAWN AGAINST THE POSE: %s. One variable against "
                "its own 2B frame -- three pose terms in the negative, three dead "
                "terms out, seed and positive and driver all held. $0."
                % (letter.upper(), body_of(letter))),
        },
        overrides={
            "seed": seed_of(letter),
            "payload:prompt.txt": pos,
        },
        retoken=[(work_dir(HAND_CELLS[0]), work_dir(letter)),
                 (r2b.spec_id(HAND_CELLS[0]), r2b.spec_id(letter))],
        extra={"cell": ("cell %s of ten, round 2C. Sheet: /review/ep2-guardcast2-0822. "
                        "Reasoning: pipeline/derive_guardcast2c_0822.py."
                        % letter.upper())},
        by="pipeline/derive_guardcast2c_0822.py",
    )


# --------------------------------------------------------------------------
def _selftest():
    print("derive_guardcast2c_0822 selftest")
    from clip_token_count import Clip, SPECIALS
    clip = Clip()

    def toks(text):
        r = clip.count(text)
        return (r[0] if isinstance(r, tuple) else r) + SPECIALS

    assert sorted(HAND_CELLS + CLEAN_CELLS) == sorted(c[0] for c in r2.CELLS), (
        "the two lists must partition the sheet -- every cell is either re-run or kept")
    assert not set(HAND_CELLS) & set(CLEAN_CELLS)
    print("  ok  5 re-run + 5 kept partitions the ten cells exactly")

    neg = negative()
    for term in POSE_NEG:
        assert term in neg, term
    for term in DROP_NEG:
        assert term not in neg, term
    # Count COMMA-PARTS, not substrings: `realistic skin texture` contains
    # "text" and a naive count says the duplicate survived when it did not.
    _parts = [p.strip() for p in neg.split(",")]
    assert _parts.count("text") == 1, "the duplicate `text` survived"
    assert len(_parts) == len(set(_parts)), "the negative still has duplicates"
    assert "hands" in neg, "the object noun is kept as well as the pose terms"
    assert toks(neg) <= 77, toks(neg)
    print("  ok  negative %d/77: +3 pose terms, -3 dead terms, `hands` kept"
          % toks(neg))

    for letter in HAND_CELLS:
        pos, _ = r2b.compiled(letter)
        assert toks(pos) <= 77, (letter, toks(pos))
        assert body_of(letter) in pos, letter
    print("  ok  5 positives carried byte-identical from 2B, all under 77")

    root = build_root()
    argv = [s for s in root["steps"] if s["name"] == "cast"][0]["argv"]
    assert "--control" not in argv and "--ip-ref" not in argv
    assert argv[argv.index("--arm") + 1] == "nocontrol", (
        "controlnet_plate gates its ControlNet branch on the literal string")
    assert argv[argv.index("--seed") + 1] == str(seed_of("a"))
    print("  ok  cell A: nocontrol, no adapter, seed %d held from 2B" % seed_of("a"))

    for letter in HAND_CELLS:
        p = os.path.join(REPO, "pipeline", "jobs", "%s.yaml" % spec_id(letter))
        if os.path.isfile(p):
            got = derive_spec.load(p)
            a = [s for s in got["steps"] if s["name"] == "cast"][0]["argv"]
            assert a[a.index("--seed") + 1] == str(seed_of(letter)), (
                "%s does not hold its 2B seed -- the A/B is broken" % p)
            pay = got.get("payload") or {}
            assert any(v == negative() for k, v in pay.items()
                       if k.endswith("negative.txt")), (
                "%s carries a stale negative -- re-run --write" % p)
    print("  ok  emitted specs (those on disk) hold their 2B seeds and the new negative")
    print("SELFTEST: PASS")
    return 0


def write_all(force=False):
    paths = [derive_spec.write(build_root(),
                               "pipeline/jobs/%s.yaml" % spec_id(HAND_CELLS[0]),
                               force=force)]
    for letter in HAND_CELLS[1:]:
        paths.append(derive_spec.write(sibling(letter),
                                       "pipeline/jobs/%s.yaml" % spec_id(letter),
                                       force=force))
    for p in paths:
        print("wrote", os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    if "--write" in sys.argv:
        sys.exit(write_all(force="--force" in sys.argv))
    sys.exit(_selftest())
