#!/usr/bin/env python3
r"""GUARD-2, ROUND 5 -- the age clause again, corrected by round 4's own frames.

    python3 pipeline/derive_guardcast5_0822.py --selftest
    python3 pipeline/derive_guardcast5_0822.py --write

ROUND 4 OVERSHOT THE OTHER WAY AND ITS SAMPLE GATE CAUGHT IT. Six of fifteen
frames drew before the queue was pulled, and they say three things:

  1. THE AGE CLAUSE WENT TOO FAR. `a young guard man, early twenties` put a
     shounen SCHOOLBOY on cells A, B, C and B40 -- late teen, slim jaw, no neck
     -- and it beat the cell clause doing it: cell A asked for `heavy square
     jaw, thick neck` and got neither. `young` is the token; on this
     checkpoint's captions it does not mean "not middle-aged", it means
     "protagonist, sixteen".
  2. THE CELL THAT SURVIVED SAYS THE FIX IS SMALL. Cell D -- shaved head, broad
     flat face, thick neck -- came back clean of hand and symbol, in the cream
     collar and the sash, on the grass, slack-mouthed and dull-eyed, and reads
     as a man in his twenties. Exactly the target. The recipe can land it; the
     wording just has to stop shouting `young` at cells whose hair does not
     carry an adult prior on its own.
  3. THE BROW THEORY IS DEAD, and this file records it as dead so no fourth
     round spends a card on it. Round 4's sample brief predicted `thick
     eyebrows` would lift the hand-on-face prior. A40 was drawn with `thick
     eyebrows` at a fresh seed AND CAME BACK WITH A HAND ON HIS FACE and the
     white bead on his cheek. One term, tested, falsified. The hand is a SEED
     lottery -- about half the draws, unchanged across `raised`, `thick`, and
     round 2's per-cell tone words -- which is what rounds 2B/2C/2D concluded
     before round 3 talked itself out of it. Rounds 2C proved negative terms do
     not move it either. So it is not fought with words at all any more: it is
     PAID FOR IN DRAWS, and this round draws sixteen to seat ten.

WHAT MOVES, AND IT IS THE SAME ONE CLAUSE, DIALLED BACK:

    round 3   a grown guard man, mature male face          -> forties
    round 4   a young guard man, early twenties, adult male build,
              broad shoulders                              -> seventeen
    round 5   a guard man in his twenties, adult male face,
              thick neck                                   -> the ask

`young` is gone -- it is the token that did the damage. `in his twenties` keeps
the number without the word. `adult male face` comes back from round 3 minus
`mature`, because round 3's forties came from `mature` and not from `adult`.
`thick neck` becomes the whole silhouette clause: cell A lost its neck to the
age clause and the neck is the single most reliable adult-vs-teen line in this
style. `broad shoulders` is DROPPED -- round 4 carried it and still drew a boy,
and at this framing the shoulders are half out of frame or under a hand, so it
was three tokens off the tail of a 77-token positive buying nothing.

INHERITED BYTE FOR BYTE, THIRD ROUND RUNNING: the symbol-led negative and the
anatomy-only expression string. They are what fixed the founder's gas-and-liquid
complaint and they are not reopened.

SEEDS STILL PINNED CELL FOR CELL to rounds 2B, 3 and 4 at offset 0, so the sheet
stays an A/B. The six extra draws sit at offset 50, clear of 2B's 0..9, 2D's 10
and 20, round 3's 30 and round 4's 40.

THE SAMPLE IS CELL C AND THE CHOICE IS NOT COSMETIC. C is round 4's cleanest
CONTROL for this exact question: no hand, no symbol, correct costume, correct
framing -- and too young, and nothing else wrong. Same seed, same body clause,
same everything; only the age clause moves. If C comes back a man, the clause is
fixed and the batch is justified. If C is still a schoolboy, the clause is not
the lever and no batch should be spent on it.

$0, local card.
"""
from __future__ import annotations

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                                  # noqa: E402
import derive_guardcast2b_0822 as r2b                               # noqa: E402
import derive_guardcast3_0822 as r3                                 # noqa: E402
import derive_guardcast4_0822 as r4                                 # noqa: E402

ARM = r4.ARM
SEED_BASE = r4.SEED_BASE
EXPRESSION = r4.EXPRESSION          # inherited, byte for byte
NEGATIVE = r4.NEGATIVE              # inherited, byte for byte
CELLS = r4.CELLS                    # the age re-cut of the bodies stands
CANON = r4.CANON

AGE = "a guard man in his twenties, adult male face, thick neck"

# The hand is a seed lottery at roughly one draw in two, so it is paid for in
# draws. Six spares on the cells whose bodies carry the weakest adult prior --
# the soft-hair ones that went shounen in round 4 -- plus the two the hand has
# historically loved.
EXTRA = ("a", "b", "c", "e", "g", "j")
EXTRA_OFFSET = 50

SAMPLE = "c"


def index_of(letter):
    return [l for l, _ in CELLS].index(letter)


def body_of(letter):
    return dict(CELLS)[letter]


def spec_id(letter, offset=0):
    if offset:
        return "ep2-guardcast5-%s%d-0822" % (letter, offset)
    return "ep2-guardcast5-%s-0822" % letter


def work_dir(letter, offset=0):
    return r"C:\banyan-farm\%s" % spec_id(letter, offset)


def seed_of(letter, offset=0):
    return SEED_BASE + (index_of(letter) + offset) * 1000


def positive(letter, offset=0):
    return ("1boy, %s, %s, %s, close on his face, cream shirt collar, white "
            "shoulder sash, tall grass, hedgerow behind, cinematic lighting, "
            "masterpiece, best quality, very aesthetic"
            % (AGE, body_of(letter), EXPRESSION))


def _stage_step(letter, offset=0):
    body = r4._stage_step("a")["argv"][2].replace(
        r4.work_dir("a"), work_dir(letter, offset))
    return {"name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def _publish_step(letter, offset=0):
    body = r4._publish_step("a")["argv"][2].replace(
        r4.work_dir("a").replace("\\", "/"),
        work_dir(letter, offset).replace("\\", "/")
    ).replace(r4.spec_id("a"), spec_id(letter, offset))
    return {"name": "publish",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


BAR = (
    "ONE 832x1216 png at the seed named in this spec, scored AT 1:1 and by eye, "
    "never by a metric. THE ROUND'S OWN CLAUSE, and it cuts BOTH WAYS: (0) HE IS "
    "A MAN IN HIS TWENTIES. Round 3 drew forties and the founder said \"the new "
    "guard generations look a bit like tooo grown adults\"; round 4 drew "
    "SEVENTEEN, which is worse. Both are DROPS. The age anchor is a picture and "
    "not a word: " + CANON + ", the guard the founder himself ruled in. (0b) THE "
    "SILHOUETTE HOLDS HIM ADULT and this is where round 4 actually broke: cell A "
    "asked for a heavy square jaw and a thick neck and the age clause took both "
    "away. Read shoulder width against jaw width, and read the NECK -- a "
    "slim-jawed, thin-necked boy is a DROP however clean the frame is. THE "
    "STANDING BAR, term for term: (1) NO EFFECT SYMBOL ANYWHERE ON THE FACE -- "
    "no sweat drop, no steam puff, no dizzy spiral, no drool, foam or white bead, "
    "no sparkle; round 3 bought this and it is not handed back. (2) NO HAND IN "
    "FRAME. This is expected to fail on about half the draws and that is why the "
    "round carries six spares: the hand is a seed lottery, proved unmoved by "
    "`raised eyebrows`, by `thick eyebrows` (round 4's A40, hand and bead at a "
    "fresh seed) and by negative terms (round 2C). Do not spend another variable "
    "on it. (3) ONE MAN alone in frame -- child or female is a DROP; (4) the face "
    "reads DUMB at a glance -- slack, blank, gormless (\"they should look like "
    "grown men. yes. dumb grown men\") -- read as ANATOMY, not as an expression "
    "label; (5) DETAILED CINEMATIC ANIME, the look of " + CANON + "; (6) NO "
    "GLASSES; (7) cream shirt collar and white shoulder sash -- round 4 drifted "
    "to a blue-and-gold military tunic on two cells, which is a DROP; (8) head "
    "and shoulders, face toward the lens, real grass-and-hedgerow background, and "
    "no foreground grass across the face; (9) HE IS NOT GUARD 1."
)

CONSUMER = (
    "THE FOUNDER, on /review/ep2-guardcast2-0822, which this round UPDATES in "
    "place -- round 5 on top, the superseded rounds collapsed and greyed "
    "beneath so the age walk (forties, then seventeen, then this) is legible on "
    "one page. He is actively reviewing. Nothing downstream consumes these "
    "frames until he picks: no beat plate, no motion job, no clip, and "
    "review/ep2-ship-0821 is untouched."
)


def _tok(text):
    import clip_token_count as ctc
    return ctc.Clip().count(text)[0]


def build_root():
    letter, offset = SAMPLE, 0
    return derive_spec.derive(
        src="pipeline/jobs/%s.yaml" % r4.spec_id(letter, 0),
        new_id=spec_id(letter, offset),
        fresh={
            "owner": ("guard lane, 2026-08-22 -- round 5 sample, filed on "
                      "round 4's own pulled batch"),
            "consumer": (
                "THE STEWARD, as the gate on whether a round-5 batch is worth "
                "the card, and then THE FOUNDER on "
                "/review/ep2-guardcast2-0822 if it passes. He is choosing on "
                "that page now and this frame does not reach it unless it "
                "clears the bar below. Nothing downstream consumes it."),
            "success": BAR,
            "why": (
                "GUARD 2, ROUND 5 SAMPLE, THE AGE CLAUSE DIALLED BACK: %r. "
                "Round 4 replaced round 3's `a grown guard man, mature male "
                "face` with `a young guard man, early twenties, adult male "
                "build, broad shoulders` and drew a SCHOOLBOY on cells A, B, C "
                "and B40 -- and beat the cell clause doing it, since A asked "
                "for a heavy square jaw and a thick neck and got neither. "
                "`young` is the token: on this checkpoint's captions it means "
                "protagonist-sixteen, not not-middle-aged. It is dropped; `in "
                "his twenties` keeps the number without the word, `adult male "
                "face` returns from round 3 minus the `mature` that made the "
                "forties, and `thick neck` joins the silhouette clause because "
                "the neck is the most reliable adult line in this style. CELL "
                "C IS THE SAMPLE BECAUSE IT IS THE CONTROL: round 4's C was "
                "clean of hand and symbol, correct costume, correct framing, "
                "and wrong on age and nothing else. Same seed %d, same body "
                "clause, only the age clause moves. Negative and expression "
                "inherited byte for byte for a third round. $0. Full reasoning "
                "in pipeline/derive_guardcast5_0822.py."
                % (AGE, seed_of(letter, offset))),
        },
        overrides={"payload:prompt.txt": positive(letter, offset)},
        retoken=[(r4.spec_id(letter, 0), spec_id(letter, offset))],
        extra={
            "cell": ("round 5 sample, cell C. Sheet: "
                     "/review/ep2-guardcast2-0822. Reasoning: "
                     "pipeline/derive_guardcast5_0822.py."),
            "age_anchor": (
                "%s -- the founder's own guard 1, ruled in by him. Not a word, "
                "a picture. Drop a teen read AND a middle-aged read." % CANON),
            "one_sample_rule": (
                "THIS IS THE SAMPLE AND IT IS FILED ALONE. Round 4's gate "
                "worked exactly as written -- cell A was judged at 1:1 the "
                "moment it landed, read seventeen, and the remaining nine were "
                "renamed to .HOLD-r4-sample-teen-0822 in the box's ready queue "
                "before they could draw. Six had already run; one of the six "
                "(cell D) is usable. No round-5 batch is enqueued until this "
                "frame is looked at."),
            "dead_theory": (
                "`thick eyebrows` DOES NOT LIFT THE HAND-ON-FACE PRIOR. Round "
                "4's A40 carried that exact term at a fresh seed and came back "
                "with a hand on the face and a white bead on the cheek. "
                "Together with round 2C (negative terms do not move it) and "
                "rounds 2B/2D (re-seeding does), the hand is settled as a SEED "
                "lottery at about one draw in two. Do not spend another "
                "variable on it -- pay for it in draws."),
            "recipe_trace": (
                "pipeline/jobs/%s.yaml with ONE clause of the positive "
                "replaced -- %r -> %r. Negative and expression INHERITED "
                "unchanged. Driver pipeline/controlnet_plate.py sha %s, "
                "fetched and sha-checked before a GPU second is spent; "
                "--control unset so no ControlNet loads, no --ip-ref passed so "
                "no adapter loads. Both strings MEASURED on animagine's own "
                "vocab with pipeline/clip_token_count.py: positive %d of 77, "
                "negative %d of 77, nothing dropped."
                % (r4.spec_id(letter, 0), r4.AGE, AGE, r2b.driver_sha()[:16],
                   _tok(positive(letter, offset)), _tok(NEGATIVE))),
        },
        by="pipeline/derive_guardcast5_0822.py",
    )


def sibling(letter, offset=0):
    src_id = spec_id(SAMPLE, 0)
    tag = letter.upper() + (" (spare draw, offset %d)" % offset if offset else "")
    return derive_spec.derive(
        src="pipeline/jobs/%s.yaml" % src_id,
        new_id=spec_id(letter, offset),
        fresh={
            "owner": ("guard lane, 2026-08-22 -- cell %s of round 5, filed "
                      "behind the cell-C sample once it passed" % tag),
            "consumer": (
                "THE FOUNDER, as candidate %s on /review/ep2-guardcast2-0822, "
                "which round 5 updates in place. Not a sample: cell C answered "
                "whether the corrected age clause lands, and this cell only "
                "adds a face to choose between. Nothing downstream consumes it "
                "until he picks and review/ep2-ship-0821 is untouched." % tag),
            "success": (
                "ONE 832x1216 png at seed %d, scored at 1:1 on the bar the "
                "cell-C sample pre-registered, unchanged and applying term for "
                "term -- the twenties clause and the neck first, and it drops "
                "in BOTH age directions. The only thing this spec moves is the "
                "hair-and-build clause and the seed: %s."
                % (seed_of(letter, offset), body_of(letter))),
            "why": (
                "GUARD 2, CELL %s, THE AGE CLAUSE DIALLED BACK TO THE "
                "TWENTIES: %s. One variable against the sample -- the "
                "hair-and-build clause and the seed that follows from the "
                "cell's position%s. Driver, checkpoint, steps, cfg, size, "
                "framing, costume, background, style tail, age clause, "
                "expression and negative all held. $0."
                % (tag, body_of(letter),
                   (". This is a SPARE DRAW, and it exists because the "
                    "hand-on-face prior is a seed lottery at about one draw in "
                    "two that three rounds have failed to move with words -- "
                    "`raised eyebrows`, `thick eyebrows` and negative terms all "
                    "tested and all falsified. Ten seated men needs sixteen "
                    "draws" if offset else ""))),
        },
        overrides={"seed": seed_of(letter, offset),
                   "payload:prompt.txt": positive(letter, offset)},
        retoken=[(spec_id(SAMPLE, 0), spec_id(letter, offset))],
        extra={"cell": ("cell %s of round 5. Sheet: "
                        "/review/ep2-guardcast2-0822. Reasoning: "
                        "pipeline/derive_guardcast5_0822.py." % tag),
               "age_anchor": ("%s -- the founder's own guard 1. Drop a teen "
                              "read AND a middle-aged read." % CANON)},
        by="pipeline/derive_guardcast5_0822.py",
    )


def all_cells():
    out = [(SAMPLE, 0)]
    out += [(l, 0) for l, _ in CELLS if l != SAMPLE]
    out += [(l, EXTRA_OFFSET) for l in EXTRA]
    return out


def _selftest():
    print("derive_guardcast5_0822 selftest")
    import clip_token_count as ctc
    c = ctc.Clip()

    assert "young" not in AGE, "`young` is the token round 4 proved toxic"
    assert "mature" not in AGE, "`mature` is the token round 3 proved toxic"
    assert "thick neck" in AGE, (
        "the silhouette clause is what round 4 lost -- it must be explicit")
    # `broad shoulders` is NOT here and its absence is a finding, not a trim
    # for space. Round 4 carried it and still drew a boy: at this framing the
    # shoulders are half out of frame or under a hand, and the NECK is the line
    # that actually separates a man from a schoolboy in this style. Keeping a
    # term that has been tested and did nothing would have cost three tokens
    # off the tail of a 77-token positive to buy nothing.
    assert "broad shoulders" not in AGE
    for letter, offset in all_cells():
        p = positive(letter, offset)
        assert AGE in p and EXPRESSION in p
        low = p.lower()
        for bad in r4.MIDDLE_AGE_TAGS:
            assert bad not in low, "cell %s%s carries %r" % (letter, offset, bad)
        n = c.count(p)[0]
        assert n <= 75, "cell %s%s positive is %d of 75" % (letter, offset, n)
    print("  ok  %d positives: twenties clause, no `young`, no middle-age tag, "
          "all <=75 tokens (sample %d)"
          % (len(all_cells()), c.count(positive(SAMPLE))[0]))

    assert NEGATIVE is r3.NEGATIVE and EXPRESSION is r3.EXPRESSION, (
        "the two strings round 3 bought must be imported, never retyped")
    print("  ok  negative (%d/75) and expression inherited byte for byte"
          % c.count(NEGATIVE)[0])

    # ONE clause vs round 4, on every cell (the bodies did not move this round).
    for letter, _ in CELLS:
        assert r4.positive(letter, 0).replace(r4.AGE, AGE) == positive(letter), (
            "more than the age clause moved on cell %s" % letter)
    print("  ok  every cell differs from round 4 by the age clause and "
          "nothing else")

    for letter, _ in CELLS:
        assert seed_of(letter, 0) == r4.seed_of(letter, 0) == r3.seed_of(letter, 0)
    seeds = [seed_of(l, o) for l, o in all_cells()]
    assert len(set(seeds)) == len(seeds), "two cells share a seed"
    assert not set(seeds) & {r4.seed_of(l, r4.RECOVERY_OFFSET)
                             for l in r4.RECOVERY}, "a spare reuses a round-4 seed"
    print("  ok  seeds pinned to rounds 3/4 at offset 0, all %d distinct, "
          "spares clear of every prior offset" % len(seeds))

    import derive_fetch_guard as fg
    seen = 0
    for letter, offset in all_cells():
        sid = spec_id(letter, offset)
        path = os.path.join(REPO, "pipeline", "jobs", "%s.yaml" % sid)
        if not os.path.isfile(path):
            continue
        seen += 1
        got = derive_spec.load(path)
        assert got["id"] == sid and got["task"] == sid
        live = derive_spec._dump({k: got[k] for k in
                                  ("steps", "payload", "artifacts", "id",
                                   "task", "env") if k in got})
        for stale in ("guardcast4", "guardcast3"):
            assert stale not in live, (
                "%s still names %r in a step/payload/artifact" % (sid, stale))
        assert work_dir(letter, offset) in live
        pay = got.get("payload") or {}
        assert any(k.endswith("prompt.txt") and v == positive(letter, offset)
                   for k, v in pay.items()), "%s carries a stale prompt" % sid
        assert any(k.endswith("negative.txt") and v == NEGATIVE
                   for k, v in pay.items()), "%s lost the negative" % sid
        cast = [s for s in got["steps"] if s["name"] == "cast"][0]["argv"]
        assert cast[cast.index("--seed") + 1] == str(seed_of(letter, offset))
        assert cast[cast.index("--task") + 1] == sid
        assert cast[cast.index("--arm") + 1] == ARM
        assert all("raw.githubusercontent.com/olegmalk/banyan-city" in u
                   for u in fg.urls_in(got)) or not fg.urls_in(got)
        stage = [s for s in got["steps"] if s["name"] == "stage"][0]["argv"][2]
        assert r2b.driver_sha() in stage, "%s stages a stale driver sha" % sid
    print("  ok  %d emitted spec(s) carry current strings, own task/dir/seed, "
          "the inherited negative and the live driver sha" % seen)
    print("SELFTEST: PASS")
    return 0


def write_sample(force=False):
    p = derive_spec.write(build_root(),
                          "pipeline/jobs/%s.yaml" % spec_id(SAMPLE, 0),
                          force=force)
    print("wrote", os.path.relpath(p, REPO))
    return 0


def write_batch(force=False):
    paths = []
    for letter, offset in all_cells()[1:]:
        paths.append(derive_spec.write(
            sibling(letter, offset),
            "pipeline/jobs/%s.yaml" % spec_id(letter, offset), force=force))
    for p in paths:
        print("wrote", os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    if "--write-sample" in sys.argv:
        sys.exit(write_sample(force="--force" in sys.argv))
    if "--write" in sys.argv:
        write_sample(force="--force" in sys.argv)
        sys.exit(write_batch(force="--force" in sys.argv))
    sys.exit(_selftest())
