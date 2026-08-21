#!/usr/bin/env python3
r"""GUARD-2 CASTING, ROUND 2D — the five hand cells at fresh seeds. No recipe change.

    python3 pipeline/derive_guardcast2d_0822.py --selftest   # assert, write nothing
    python3 pipeline/derive_guardcast2d_0822.py --write      # emit the ten specs

WHY THIS IS A SEED SWEEP AND NOT A FOURTH IDEA. Round 2C's A/B came back and it
is a CLEAN NEGATIVE RESULT: three pose terms in the model's own dialect --
`hand on own face`, `head rest`, `hand up` -- did NOT remove the hand. Cell A at
seed 20260725 drew the same man in the same hand-on-cheek composition, expression
slightly changed and nothing else. Held side by side with its 2B twin the two
frames are the same picture.

WHAT THAT RULES OUT, WHICH IS THE USEFUL PART. Across three rounds the hand has
now survived: the IP-Adapter reference being removed (2B), and the pose being
negated in words (2C). It is not the reference and it is not a missing negative
term. What it IS, on the evidence: a strong compositional prior of this
checkpoint for a head-and-shoulders portrait prompt, which lands on some seeds
and not others -- five of ten in 2B, and the five that were clean were clean
without any help. Beating a prior of that kind with more negative terms is the
shape of work that eats a night and produces a longer prompt; SAMPLING PAST IT
costs twenty seconds a frame and the sheet needs different men anyway.

SO: THE FIVE HAND CELLS, THE SAME RECIPE, TWO FRESH SEEDS EACH.

  cell   clause                          2B/2C seed    2D seeds
  A      thick dark brown hair...        20260725      20270725, 20280725
  B      light sandy hair...             20261725      20271725, 20281725
  D      shaved head...                  20263725      20273725, 20283725
  H      curly black hair...             20267725      20277725, 20287725
  J      short red hair...               20269725      20279725, 20289725

The arithmetic is the sheet's own, extended rather than replaced: seed_base +
index*1000 with the index pushed by 10 and by 20, so no 2D seed can collide with
a 2B, a 2C or another 2D seed, and any cell's seed is still derivable from its
letter and its pass without opening a file.

NO SAMPLE GATE ON THIS ROUND, AND THAT IS THE RULE APPLIED RATHER THAN SKIPPED.
CLAUDE.md requires one sample per RECIPE CHANGE. This is not one: driver,
checkpoint, prompt bytes, negative bytes, steps, cfg and size are all 2C's
exactly, and 2C's negative is carried BECAUSE it is de-duplicated and costs
nothing, not because it is expected to work -- 2C's own result says it does not.
Eleven frames of this recipe have already been looked at one at a time. The only
thing moving is the seed, which is the parameter a sweep exists to move.

WHAT THE SWEEP IS SCORED ON. Ten frames, and the ONLY question per frame is the
hand -- everything else about this recipe is settled and shown. The sheet needs
five clean men to join C, E, F, G and I; on 2B's five-of-ten rate ten draws
should hand over about five, and if it hands over three the sheet ships eight,
which is inside the eight-to-ten the founder was promised. A cell whose two
draws both come back holding their face is REPORTED AS SUCH on the page rather
than quietly replaced by a sixth idea.

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
import derive_guardcast2c_0822 as r2c                               # noqa: E402

LETTERS = r2c.HAND_CELLS          # a, b, d, h, j
PASSES = (10, 20)                 # index offsets; both clear of 2B/2C's 0..9


def spec_id(letter, offset):
    return "ep2-guardcast2d-%s%d-0822" % (letter, offset)


def work_dir(letter, offset):
    return r"C:\banyan-farm\%s" % spec_id(letter, offset)


def seed_of(letter, offset):
    return r2.SEED_BASE + (r2c.index_of(letter) + offset) * 1000


def _cast_argv(letter, offset):
    w = work_dir(letter, offset)
    return [
        r"C:\banyan-farm\venv\Scripts\python.exe",
        w + r"\src\pipeline\controlnet_plate.py",
        "--root", w + r"\src",
        "--task", spec_id(letter, offset),
        "--arm", r2b.ARM,
        "--seed", str(seed_of(letter, offset)),
        "--steps", "40",
        "--cfg", "7.5",
        "--width", "832",
        "--height", "1216",
        "--prompt-file", w + r"\prompt.txt",
        "--negative-file", w + r"\negative.txt",
        "--out", w + r"\out",
    ]


def _stage_step(letter, offset):
    body = r2b._stage_step("a")["argv"][2].replace(
        r2b.work_dir("a"), work_dir(letter, offset))
    return {"name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def _publish_step(letter, offset):
    body = r2b._publish_step("a")["argv"][2].replace(
        r2b.work_dir("a").replace("\\", "/"),
        work_dir(letter, offset).replace("\\", "/")
    ).replace(r2b.spec_id("a"), spec_id(letter, offset))
    return {"name": "publish",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


BAR = (
    "ONE 832x1216 png at the seed named in this spec, scored at 1:1. THE ONLY "
    "OPEN QUESTION IS THE HAND: pass = NO hand in frame and no hand-on-face "
    "composition. Everything else about this recipe has been shown across eleven "
    "frames tonight and is not re-litigated here, but it must still HOLD, and a "
    "frame that loses one of these is dropped rather than argued for: one grown "
    "man alone, detailed cinematic anime, cream shirt collar and white shoulder "
    "sash, real grass background, no glasses, not guard 1, and the cell's own "
    "hair-and-face clause legible. A pass is a CANDIDATE on the picker page and "
    "nothing more -- the cast is R4 and this job does not make it. PRE-REGISTERED: "
    "if BOTH of a cell's two draws come back holding the face, that cell is "
    "reported on the page as unfixed at this recipe rather than swapped for a "
    "sixth idea nobody sampled."
)


def build_root():
    letter, offset = LETTERS[0], PASSES[0]
    pos, _ = r2b.compiled(letter)
    w = work_dir(letter, offset)
    return {
        "id": spec_id(letter, offset),
        "task": spec_id(letter, offset),
        "node": r2.NODE,
        "beat": r2.BEAT,
        "runner": "box",
        "priority": 6,
        "needs_gpu": True,
        "max_attempts": 1,
        "sample": False,
        "est_minutes": 2,
        "needs": ["cuda", "vram12", "sdxl-venv"],
        "owner": "guard lane, 2026-08-22 -- round 2D, the seed sweep after 2C's null result",
        "consumer": (
            "THE FOUNDER, on /review/ep2-guardcast2-0822. Five of the ten 2B cells "
            "held their own face and round 2C proved the pose negative does not "
            "shift it; this sweep buys the sheet its missing clean men by sampling "
            "past a compositional prior instead of arguing with it. Guard 1 is not "
            "re-asked and review/ep2-ship-0821 is untouched."),
        "success": BAR,
        "why": (
            "GUARD 2, CELL %s AT A FRESH SEED (%d): %s. NOT A RECIPE CHANGE and so "
            "not sample-gated -- driver, checkpoint, prompt bytes, negative bytes, "
            "steps, cfg and size are round 2C's exactly and only the seed moves. "
            "Round 2C's A/B is the reason: three pose terms in the model's own "
            "dialect did not remove the hand at the same seed, which together with "
            "2B's adapter removal rules out both the reference and the wording and "
            "leaves a checkpoint prior that lands on some seeds and not others -- "
            "five of ten in 2B. Twenty seconds a frame to sample past it. $0. Full "
            "reasoning in pipeline/derive_guardcast2d_0822.py."
            % (letter.upper(), seed_of(letter, offset), r2c.body_of(letter))),
        "script_authority": (
            "Node 002b-first-citizen, live script `002b-t0-c`, `approved_by: founder`, "
            "`approved_on: 2026-08-03`. A STILL CASTING PLATE on an approved node: no "
            "voice, no motion, no episode assembly, no publication."),
        "script_line": ("Beat 06 THE CLIPBOARD: guard 2, the one with the bark board. "
                        "Head and shoulders, no prop -- the question is his FACE."),
        "env": dict(r2b.build_root()["env"]),
        "payload": {
            w + r"\prompt.txt": pos,
            w + r"\negative.txt": r2c.negative(),
        },
        "steps": [
            _stage_step(letter, offset),
            {"name": "cast", "argv": _cast_argv(letter, offset)},
            _publish_step(letter, offset),
        ],
        "recipe_trace": (
            "pipeline/jobs/ep2-guardcast2c-a-0822.yaml with the seed moved from %d "
            "to %d and nothing else touched. Seed arithmetic is the sheet's own, "
            "extended: SEED_BASE + (cell index + offset) * 1000, offsets 10 and 20, "
            "so no 2D seed can collide with a 2B, a 2C or another 2D."
            % (r2c.seed_of(letter), seed_of(letter, offset))),
        "artifacts": [w + r"\out\%s-nocontrol.png" % spec_id(letter, offset)],
    }


def sibling(letter, offset):
    pos, _ = r2b.compiled(letter)
    root_letter, root_offset = LETTERS[0], PASSES[0]
    return derive_spec.derive(
        src="pipeline/jobs/%s.yaml" % spec_id(root_letter, root_offset),
        new_id=spec_id(letter, offset),
        fresh={
            "owner": ("guard lane, 2026-08-22 -- cell %s pass %d of round 2D's seed "
                      "sweep" % (letter.upper(), PASSES.index(offset) + 1)),
            "consumer": (
                "THE FOUNDER, on /review/ep2-guardcast2-0822 as a possible candidate "
                "%s. One of ten draws whose only job is to come back without a hand "
                "in frame; whichever of a cell's two draws is clean goes on the "
                "sheet, and if neither is, the page says so." % letter.upper()),
            "success": (
                "ONE 832x1216 png at seed %d, scored at 1:1 on the hand clause first "
                "and the carried-over clauses second, exactly as the root spec of "
                "this sweep states them. The cell's own clause must stay legible: %s."
                % (seed_of(letter, offset), r2c.body_of(letter))),
            "why": (
                "GUARD 2, CELL %s AT FRESH SEED %d: %s. One variable against the "
                "sweep's root -- the cell's clause and the seed. Same driver, same "
                "negative, same steps, cfg and size. $0."
                % (letter.upper(), seed_of(letter, offset), r2c.body_of(letter))),
        },
        # THE PROMPT OVERRIDE IS CONDITIONAL, and derive_spec is why: it refuses a
        # payload override that changes nothing, correctly. Cell A's SECOND pass
        # carries cell A's prompt -- the root of this sweep is A pass 1, so for
        # A20 the only thing that moves is the seed and the prompt is inherited.
        # Passing it anyway would be asserting a variable that is not one.
        overrides=dict(
            {"seed": seed_of(letter, offset)},
            **({} if letter == root_letter else {"payload:prompt.txt": pos})),
        retoken=[(work_dir(root_letter, root_offset), work_dir(letter, offset)),
                 (spec_id(root_letter, root_offset), spec_id(letter, offset))],
        extra={"cell": ("cell %s, seed pass %d of round 2D. Sheet: "
                        "/review/ep2-guardcast2-0822. Reasoning: "
                        "pipeline/derive_guardcast2d_0822.py."
                        % (letter.upper(), PASSES.index(offset) + 1))},
        by="pipeline/derive_guardcast2d_0822.py",
    )


def _selftest():
    print("derive_guardcast2d_0822 selftest")
    seeds = {}
    for letter in LETTERS:
        for offset in PASSES:
            s = seed_of(letter, offset)
            assert s not in seeds, "seed %d collides: %s vs %s" % (
                s, seeds.get(s), (letter, offset))
            seeds[s] = (letter, offset)
            # and it must clear every seed 2B/2C already spent
            for other in (c[0] for c in r2.CELLS):
                assert s != r2c.seed_of(other), (
                    "2D seed %d collides with 2B/2C cell %s" % (s, other))
    assert len(seeds) == len(LETTERS) * len(PASSES) == 10
    print("  ok  10 fresh seeds, none colliding with each other or with 2B/2C")

    root = build_root()
    argv = [s for s in root["steps"] if s["name"] == "cast"][0]["argv"]
    assert argv[argv.index("--arm") + 1] == "nocontrol"
    assert "--control" not in argv and "--ip-ref" not in argv
    assert argv[argv.index("--steps") + 1] == "40"
    assert argv[argv.index("--cfg") + 1] == "7.5"
    assert root["payload"][work_dir(LETTERS[0], PASSES[0]) + r"\negative.txt"] \
        == r2c.negative(), "2D must carry 2C's negative byte for byte"
    print("  ok  recipe is 2C's exactly: nocontrol, no adapter, 40 steps, cfg 7.5,"
          " same negative")

    for letter in LETTERS:
        pos, _ = r2b.compiled(letter)
        assert r2c.body_of(letter) in pos, letter
    print("  ok  5 positives carried byte-identical from 2B")

    for letter in LETTERS:
        for offset in PASSES:
            p = os.path.join(REPO, "pipeline", "jobs",
                             "%s.yaml" % spec_id(letter, offset))
            if os.path.isfile(p):
                got = derive_spec.load(p)
                a = [s for s in got["steps"] if s["name"] == "cast"][0]["argv"]
                assert a[a.index("--seed") + 1] == str(seed_of(letter, offset)), p
    print("  ok  emitted specs (those on disk) carry their sweep seeds")
    print("SELFTEST: PASS")
    return 0


def write_all(force=False):
    paths = [derive_spec.write(build_root(),
                               "pipeline/jobs/%s.yaml" % spec_id(LETTERS[0], PASSES[0]),
                               force=force)]
    for letter in LETTERS:
        for offset in PASSES:
            if (letter, offset) == (LETTERS[0], PASSES[0]):
                continue
            paths.append(derive_spec.write(
                sibling(letter, offset),
                "pipeline/jobs/%s.yaml" % spec_id(letter, offset), force=force))
    for p in paths:
        print("wrote", os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    if "--write" in sys.argv:
        sys.exit(write_all(force="--force" in sys.argv))
    sys.exit(_selftest())
