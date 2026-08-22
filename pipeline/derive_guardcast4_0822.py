#!/usr/bin/env python3
r"""GUARD-2, ROUND 4 -- the age clause, and only the age clause.

    python3 pipeline/derive_guardcast4_0822.py --selftest
    python3 pipeline/derive_guardcast4_0822.py --write

THE FOUNDER'S WORDS ON ROUND 3: "the new guard generations look a bit like tooo
grown adults". Round 3 did not overshoot by accident -- it was ASKED to. Its
positive opens `1boy, a grown guard man, mature male face` and its cell clauses
carry `grey-streaked brown hair`, `thick moustache`, `receding sandy hair`,
`dark stubble`, `jowly face`. Every one of those is a middle-age tag, and the
sheet came back middle-aged. The steward then made it worse from the other
side: round 3's own drop note reads "B30 -- clean, but the face reads
mid-twenties rather than a grown guard", i.e. a frame was thrown away FOR being
the age the founder actually wants. That judgement was wrong and this file
records it as wrong.

THE AGE ANCHOR IS A PICTURE, NOT A WORD: taste/refs/guard1-canon-founder-0822.png,
the guard the founder himself ruled in at beat 9. Young, but unmistakably a man.
Round 4 is judged against that image and against nothing else. A teen read is a
DROP and a middle-aged read is now a DROP too -- both directions, which is new.

WHAT MOVES, AND IT IS ONE CLAUSE:

    round 3   1boy, a grown guard man, mature male face, <body>, <expression>, ...
    round 4   1boy, a young guard man, early twenties, adult male build,
              broad shoulders, <body>, <expression>, ...

WHAT DOES NOT MOVE, BYTE FOR BYTE:

  * THE NEGATIVE. Round 3's symbol-led negative fixed the founder's last
    complaint -- 14 of 15 frames clean of sweat, steam and drool -- and it is
    INHERITED, not retyped. It already carries `teenager` and `child` at drop
    weight, which is the age-down floor: nothing is added for the teen risk
    because the term that blocks it is already in there doing the job.
  * THE EXPRESSION. `slack open mouth, raised eyebrows, dull half-closed eyes`
    -- anatomy, no tone word. That string is why the symbols left.

THE SILHOUETTE LAW, STATED BECAUSE AGE-DOWN IS EXACTLY WHERE IT BREAKS. There is
no skeleton in this arm (`--arm nocontrol`, no ControlNet loads) so stature
cannot be pinned by geometry the way a posed plate pins it; it has to be pinned
by words. `adult male build, broad shoulders` rides in the same clause as the
age words for that reason -- the clause that takes years off him puts the frame
back on him in the same breath. Read at 1:1: shoulder width against jaw width,
and neck thickness. A narrow-shouldered, thin-necked young man is a teen and is
dropped however good the face is.

THE CELL CLAUSES ARE RE-CUT FOR AGE, and this is the second thing that moves.
Five of round 3's ten men were middle-aged in their own clause, so moving only
the head clause would have fought the cell clause and lost:

    b  weak chin            -> strong nose      (weak chin read juvenile; B has
                                                 now failed four rounds and the
                                                 chin is the reason)
    d  dark stubble         -> thick neck       (beard-implying, drops out)
    f  grey-streaked hair,  -> dark wavy hair,  (the moustache the founder named,
       thick moustache,        wide jaw,         and the grey with it)
       jowly face              broad cheekbones
    g  receding sandy hair  -> messy sandy hair (a receding hairline IS the
                                                 middle-age tag)
    a,c,e,h,i,j             unchanged           (age-neutral structure only)

SEEDS ARE PINNED CELL FOR CELL to rounds 2B and 3 -- SEED_BASE + index*1000,
same letters in the same order -- so every frame on the new sheet is a true A/B
against the frame the founder is looking at right now.

THE PENDING BROW SAMPLE IS FOLDED IN RATHER THAN LEFT ON THE SHELF.
pipeline/jobs/ep2-guardcast4-g-0822.yaml was filed to test `raised eyebrows` ->
`thick eyebrows`, on the finding that round 3's brow term reads as DISTRESS and
distress brings hands (8 of 15 frames held their own face, including G and I
which were clean at the same seeds in round 2). It never reached the card. It is
NOT fired as-is, because it carries round 3's middle-aged head clause and would
answer a question about a man the founder has already rejected. Instead the five
hand-prone cells (a, b, d, h, j) each carry one recovery draw at offset 40 that
swaps that single term. So the round buys the age answer on ten frames and the
brow answer on five, in one batch, and whichever brow term wins there are
candidates drawn with it.

ONE SAMPLE BEFORE THE BATCH, HONOURED THE WAY ROUND 3 HONOURED IT: cell A is
filed first and the box runs the queue in order. It is judged at 1:1 the moment
it lands, and if the age clause has produced a teenager the remaining fourteen
are PULLED from the queue, not published.

$0, local card, about seven card-minutes for fifteen frames.
"""
from __future__ import annotations

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                                  # noqa: E402
import derive_guardcast2_0822 as r2                                 # noqa: E402
import derive_guardcast2b_0822 as r2b                               # noqa: E402
import derive_guardcast3_0822 as r3                                 # noqa: E402

ARM = r3.ARM                       # "nocontrol"
SEED_BASE = r3.SEED_BASE           # 20260725
RECOVERY = r3.RECOVERY             # ("a", "b", "d", "h", "j")
RECOVERY_OFFSET = 40               # clear of 2B's 0..9, 2D's 10/20, r3's 30

# THE ONE CLAUSE THIS ROUND MOVES. Round 3's head was
# "a grown guard man, mature male face".
AGE = "a young guard man, early twenties, adult male build, broad shoulders"

# INHERITED BYTE FOR BYTE. Not re-typed here on purpose: a constant that is
# copied is a constant that drifts.
EXPRESSION = r3.EXPRESSION         # slack open mouth, raised eyebrows, dull ...
NEGATIVE = r3.NEGATIVE
BROW_OLD = "raised eyebrows"
BROW_NEW = "thick eyebrows"        # the folded-in round-4 sample's variable

# HAIR / FACE STRUCTURE / BUILD ONLY, re-cut for age. Same letters in the same
# order as round 3, which is what holds the seeds cell for cell.
CELLS = (
    ("a", "thick dark brown hair, heavy square jaw, thick neck"),
    ("b", "light sandy hair, long thin face, strong nose"),
    ("c", "cropped ginger hair, round heavy face, full cheeks"),
    ("d", "shaved head, broad flat face, thick neck"),
    ("e", "shaggy black hair, gaunt narrow face, big ears"),
    ("f", "dark wavy hair, wide jaw, broad cheekbones"),
    ("g", "messy sandy hair, high forehead, narrow face"),
    ("h", "curly black hair, wide square face, thick neck"),
    ("i", "straight light brown hair, big nose, doughy face"),
    ("j", "short red hair, freckles, blunt chin"),
)

CANON = "taste/refs/guard1-canon-founder-0822.png"


def index_of(letter):
    return [l for l, _ in CELLS].index(letter)


def body_of(letter):
    return dict(CELLS)[letter]


def spec_id(letter, offset=0):
    if offset:
        return "ep2-guardcast4b-%s%d-0822" % (letter, offset)
    return "ep2-guardcast4b-%s-0822" % letter


def work_dir(letter, offset=0):
    return r"C:\banyan-farm\%s" % spec_id(letter, offset)


def seed_of(letter, offset=0):
    """IDENTICAL arithmetic to rounds 2B and 3, so offset 0 is a true A/B."""
    return SEED_BASE + (index_of(letter) + offset) * 1000


def expression(offset=0):
    """Offset-0 cells keep round 3's brow; recovery draws swap the one term."""
    if offset == RECOVERY_OFFSET:
        return EXPRESSION.replace(BROW_OLD, BROW_NEW)
    return EXPRESSION


def positive(letter, offset=0):
    return ("1boy, %s, %s, %s, close on his face, cream shirt collar, white "
            "shoulder sash, tall grass, hedgerow behind, cinematic lighting, "
            "masterpiece, best quality, very aesthetic"
            % (AGE, body_of(letter), expression(offset)))


def _stage_step(letter, offset=0):
    body = r3._stage_step("a")["argv"][2].replace(
        r3.work_dir("a"), work_dir(letter, offset))
    return {"name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def _publish_step(letter, offset=0):
    body = r3._publish_step("a")["argv"][2].replace(
        r3.work_dir("a").replace("\\", "/"),
        work_dir(letter, offset).replace("\\", "/")
    ).replace(r3.spec_id("a"), spec_id(letter, offset))
    return {"name": "publish",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def _cast_argv(letter, offset=0):
    w = work_dir(letter, offset)
    return [
        r"C:\banyan-farm\venv\Scripts\python.exe",
        w + r"\src\pipeline\controlnet_plate.py",
        "--root", w + r"\src",
        "--task", spec_id(letter, offset),
        "--arm", ARM,
        "--seed", str(seed_of(letter, offset)),
        "--steps", "40",
        "--cfg", "7.5",
        "--width", "832",
        "--height", "1216",
        "--prompt-file", w + r"\prompt.txt",
        "--negative-file", w + r"\negative.txt",
        "--out", w + r"\out",
    ]


BAR = (
    "ONE 832x1216 png at the seed named in this spec, scored AT 1:1 and by eye, "
    "never by a metric. THE ROUND'S OWN CLAUSE, and it cuts BOTH WAYS, which is "
    "new: (0) HE IS A YOUNG ADULT MAN IN HIS TWENTIES. The founder's words on "
    "round 3 were \"the new guard generations look a bit like tooo grown "
    "adults\". A middle-aged read is now a DROP -- moustache, grey, jowls, "
    "receding hairline, crow's feet, forty-year-old skin -- and a TEENAGER is "
    "still a DROP, no softer than before. The age anchor is a picture and not a "
    "word: " + CANON + ", the guard the founder himself ruled in. Young, but "
    "unmistakably a man. (0b) THE SILHOUETTE HOLDS HIM ADULT: shoulder width "
    "against jaw width, and a thick neck. A narrow-shouldered, thin-necked young "
    "man is a teen and is dropped however good the face is -- this arm loads no "
    "ControlNet, so nothing but the words is pinning his frame. THE STANDING "
    "BAR, repeated term for term rather than referenced because a bar that lives "
    "in another spec is a bar nobody reads: (1) NO EFFECT SYMBOL ANYWHERE ON THE "
    "FACE -- no sweat drop, no steam or sigh puff, no dizzy spiral, no drool or "
    "foam bead, no sparkle, no bubble; round 3 bought this and round 4 does not "
    "hand it back. (2) ONE MAN alone in frame -- child or female is a DROP; (3) "
    "the face reads DUMB at a glance -- slack, blank, gormless (\"they should "
    "look like grown men. yes. dumb grown men\") -- read as ANATOMY, not as an "
    "expression label; (4) DETAILED CINEMATIC ANIME, the look of " + CANON + "; "
    "a flat or muted tag-sheet look is a fail; (5) NO GLASSES and NO HAND in "
    "frame; (6) cream shirt collar and white shoulder sash read as the costume "
    "family; (7) head and shoulders, face toward the lens, real "
    "grass-and-hedgerow background; (8) HE IS NOT GUARD 1. PRE-REGISTERED FAIL "
    "MODES: the age clause taking the shoulders with it and delivering a "
    "schoolboy, which is what the silhouette clause above is watched for and is "
    "read on the CONTACT SHEET rather than on any single frame; and the "
    "hand-on-face prior round 3 bought with `raised eyebrows`, which is why a, "
    "b, d, h, j each carry a recovery draw at offset 40 that swaps that one term "
    "for `thick eyebrows`."
)

CONSUMER = (
    "THE FOUNDER, on /review/ep2-guardcast2-0822, which this round UPDATES in "
    "place -- round 4 on top, round 3 collapsed and greyed beneath it so the "
    "age comparison he is owed survives on one page. He is actively reviewing. "
    "Nothing downstream consumes these frames until he picks: no beat plate, no "
    "motion job, no clip, and review/ep2-ship-0821 is untouched."
)


def build_root():
    letter, offset = "a", 0
    return derive_spec.derive(
        src="pipeline/jobs/%s.yaml" % r3.spec_id("a", 0),
        new_id=spec_id(letter, offset),
        fresh={
            "owner": ("guard lane, 2026-08-22 -- round 4, filed on the "
                      "founder's round-3 note that the men came back too old"),
            "consumer": CONSUMER,
            "success": BAR,
            "why": (
                "GUARD 2, CELL A OF TEN, AGE DOWN TO THE TWENTIES: %s. The "
                "founder's round-3 verdict was \"the new guard generations look "
                "a bit like tooo grown adults\", and round 3 was asked for "
                "exactly that -- it opens `a grown guard man, mature male face` "
                "and its cells carry moustache, grey streaks, stubble and a "
                "receding hairline. ONE CLAUSE MOVES: that head clause becomes "
                "%r, which takes the years off and puts the adult frame back on "
                "in the same breath, because this arm loads no ControlNet and "
                "words are the only thing pinning his stature. The five "
                "middle-aged CELL clauses are re-cut with it (b, d, f, g here; "
                "see the file) since a young head clause fighting a jowly cell "
                "clause loses. Negative and expression string are INHERITED "
                "byte for byte -- they are what fixed his last complaint about "
                "gas and liquid on the faces and they are not reopened. Seed %d "
                "is 2B's and round 3's cell-A seed, so this frame is a true A/B "
                "against the one he is looking at. $0, local card. Full "
                "reasoning in pipeline/derive_guardcast4_0822.py."
                % (body_of(letter), AGE, seed_of(letter, offset))),
        },
        overrides={"payload:prompt.txt": positive(letter, offset)},
        retoken=[(r3.spec_id("a", 0), spec_id(letter, offset))],
        extra={
            "cell": ("round 4, cell A of ten. Sheet: "
                     "/review/ep2-guardcast2-0822. Reasoning: "
                     "pipeline/derive_guardcast4_0822.py."),
            "age_anchor": (
                "%s -- the founder's own guard 1, ruled in by him. He is the "
                "age target for guard 2 and the only one: not a word, not a "
                "tag, a picture. Judge every frame of this round against it at "
                "1:1 and drop in BOTH directions." % CANON),
            "one_sample_rule": (
                "CELL A IS THE SAMPLE AND IT IS FILED FIRST, and the box runs "
                "its queue in order. This is a recipe change -- the head clause "
                "that reaches CLIP moves -- so the rule applies rather than "
                "being waived. The fourteen behind it are filed in the same "
                "batch because the whole batch is about seven card-minutes at "
                "$0 and the founder is at the page now, but the gate is real: "
                "cell A is judged at 1:1 the moment it lands and if the age "
                "clause produced a teenager the queued remainder is PULLED, not "
                "published."),
            "superseded_sample": (
                "pipeline/jobs/ep2-guardcast4-g-0822.yaml -- filed to test "
                "`raised eyebrows` -> `thick eyebrows` and never fired. It is "
                "NOT enqueued: it carries round 3's middle-aged head clause and "
                "would answer a question about a man the founder has rejected. "
                "Its variable is folded into this round's five recovery draws "
                "at offset %d instead." % RECOVERY_OFFSET),
            "seed_note": (
                "Seeds are the sheet's own arithmetic, unchanged for a third "
                "round: SEED_BASE + index*1000, i.e. %d for cell A and "
                "%d..%d for B..J -- IDENTICAL to rounds 2B and 3 cell for cell, "
                "which is what makes round 4 an A/B on AGE rather than fifteen "
                "unrelated pictures. The five hand-prior cells (a, b, d, h, j) "
                "each carry one recovery draw at offset %d, clear of 2B's 0..9, "
                "2D's 10 and 20 and round 3's 30."
                % (SEED_BASE, SEED_BASE + 1000, SEED_BASE + 9000,
                   RECOVERY_OFFSET)),
            "recipe_trace": (
                "pipeline/jobs/%s.yaml with ONE clause of the positive replaced "
                "-- `a grown guard man, mature male face` -> %r -- plus the "
                "age re-cut of the cell clause. Negative INHERITED unchanged "
                "from round 3. Driver pipeline/controlnet_plate.py sha %s, "
                "fetched and sha-checked before a GPU second is spent; "
                "--control unset so no ControlNet loads, no --ip-ref passed so "
                "no adapter loads. Both strings MEASURED on animagine's own "
                "vocab with pipeline/clip_token_count.py: positive %d of 77, "
                "negative %d of 77, nothing dropped."
                % (r3.spec_id("a", 0), AGE, r2b.driver_sha()[:16],
                   _tok(positive(letter, offset)), _tok(NEGATIVE))),
        },
        by="pipeline/derive_guardcast4_0822.py",
    )


def _tok(text):
    import clip_token_count as ctc
    return ctc.Clip().count(text)[0]


def sibling(letter, offset=0):
    src_id = spec_id("a", 0)
    tag = letter.upper() + (" (brow recovery draw, offset %d)" % offset
                            if offset else "")
    return derive_spec.derive(
        src="pipeline/jobs/%s.yaml" % src_id,
        new_id=spec_id(letter, offset),
        fresh={
            "owner": ("guard lane, 2026-08-22 -- cell %s of round 4, filed with "
                      "the batch behind the cell-A sample" % tag),
            "consumer": (
                "THE FOUNDER, as candidate %s on /review/ep2-guardcast2-0822, "
                "which round 4 updates in place -- round 4 on top, round 3 "
                "collapsed and greyed beneath so the age A/B he is owed "
                "survives. Not a sample: cell A answers whether the age clause "
                "lands, and this cell only adds a face to choose between. "
                "Nothing downstream consumes it until he picks and "
                "review/ep2-ship-0821 is untouched." % tag),
            "success": (
                "ONE 832x1216 png at seed %d, scored at 1:1 on the bar cell A "
                "pre-registered, unchanged and applying term for term -- the "
                "young-adult clause first and it drops in BOTH directions. The "
                "only thing this spec moves is %s: %s."
                % (seed_of(letter, offset),
                   "the brow term and the seed" if offset
                   else "the hair-and-build clause and the seed",
                   expression(offset) if offset else body_of(letter))),
            "why": (
                "GUARD 2, CELL %s, AGE DOWN TO THE TWENTIES: %s. %s Driver, "
                "checkpoint, steps, cfg, size, framing, costume, background, "
                "style tail, age clause and negative all held. $0."
                % (tag, body_of(letter),
                   ("This is the BROW RECOVERY draw for a cell the "
                    "hand-on-face prior lands on. Round 3 bought that prior "
                    "with `raised eyebrows` -- 8 of 15 frames held their own "
                    "face, including two that were clean at the same seed in "
                    "round 2 -- so this draw swaps that ONE term for `thick "
                    "eyebrows`, the goblin work's answer to the same problem: "
                    "heavy, non-cute, not scowling, where `raised` overshot "
                    "into anguish. It also moves the seed, because rounds "
                    "2B/2C/2D proved the prior is beaten by re-seeding and not "
                    "by negative terms." if offset
                    else "One variable against cell A -- the hair-and-build "
                         "clause and the seed that follows from the cell's "
                         "position."))),
        },
        # The negative is this sheet's CONSTANT and is inherited, never
        # overridden; its payload KEY is retokened to this cell's own dir.
        overrides={"seed": seed_of(letter, offset),
                   "payload:prompt.txt": positive(letter, offset)},
        retoken=[(spec_id("a", 0), spec_id(letter, offset))],
        extra={"cell": ("cell %s of round 4. Sheet: "
                        "/review/ep2-guardcast2-0822. Reasoning: "
                        "pipeline/derive_guardcast4_0822.py." % tag),
               "age_anchor": ("%s -- the founder's own guard 1. Drop a teen "
                              "read AND a middle-aged read." % CANON)},
        by="pipeline/derive_guardcast4_0822.py",
    )


def all_cells():
    """(letter, offset) in FIRING ORDER: the sample, then the nine, then five."""
    out = [("a", 0)]
    out += [(l, 0) for l, _ in CELLS if l != "a"]
    out += [(l, RECOVERY_OFFSET) for l in RECOVERY]
    return out


MIDDLE_AGE_TAGS = ("moustache", "mustache", "beard", "stubble", "grey-streaked",
                   "gray-streaked", "receding", "jowly", "balding", "wrinkles",
                   "old man", "mature male", "middle-aged", "grown man",
                   "elderly", "salt-and-pepper")


def _selftest():
    print("derive_guardcast4_0822 selftest")
    import clip_token_count as ctc
    c = ctc.Clip()

    # ---- 1. the age clause reaches every cell and no middle-age tag survives.
    for letter, offset in all_cells():
        p = positive(letter, offset)
        assert AGE in p, "cell %s%s lost the age clause" % (letter, offset)
        assert "mature male face" not in p and "a grown guard man" not in p, (
            "cell %s%s still carries round 3's head clause" % (letter, offset))
        low = p.lower()
        for bad in MIDDLE_AGE_TAGS:
            assert bad not in low, (
                "cell %s%s still carries the middle-age tag %r -- that is the "
                "founder's whole complaint" % (letter, offset, bad))
        n = c.count(p)[0]
        assert n <= 75, "cell %s%s positive is %d of 75" % (letter, offset, n)
    print("  ok  %d positives: age clause present, no middle-age tag, "
          "all <=75 tokens (cell A %d)"
          % (len(all_cells()), c.count(positive("a"))[0]))

    # ---- 2. the two strings round 3 bought are INHERITED, not retyped.
    assert NEGATIVE is r3.NEGATIVE, "the negative was copied instead of imported"
    assert EXPRESSION is r3.EXPRESSION, "the expression was copied, not imported"
    n = c.count(NEGATIVE)[0]
    assert n <= 75, "negative is %d of 75" % n
    for letter, _ in CELLS:
        assert EXPRESSION in positive(letter, 0), (
            "cell %s dropped the anatomy-only expression string" % letter)
    print("  ok  negative (%d/75) and expression inherited byte for byte" % n)

    # ---- 3. ONE clause moved vs round 3, on the cells whose body is unchanged.
    unchanged = [l for l, b in CELLS if r3.body_of(l) == b]
    assert set(unchanged) == {"a", "c", "e", "h", "i", "j"}, unchanged
    for letter in unchanged:
        before = r3.positive(letter).replace(
            "a grown guard man, mature male face", AGE)
        assert before == positive(letter, 0), (
            "more than the age clause moved on cell %s:\n  r3 %s\n  r4 %s"
            % (letter, r3.positive(letter), positive(letter, 0)))
    print("  ok  cells %s differ from round 3 by the age clause and nothing else"
          % ", ".join(unchanged))

    # ---- 4. the recovery draws move the brow term and nothing else.
    for letter in RECOVERY:
        a = positive(letter, 0)
        b = positive(letter, RECOVERY_OFFSET)
        assert BROW_OLD in a and BROW_NEW in b and BROW_OLD not in b
        assert a.replace(BROW_OLD, BROW_NEW) == b, (
            "recovery draw %s moved more than the brow term" % letter)
        assert seed_of(letter, RECOVERY_OFFSET) != seed_of(letter, 0)
    print("  ok  %d brow recovery draws: one term + one seed, nothing else"
          % len(RECOVERY))

    # ---- 5. seeds are pinned to round 3 cell for cell at offset 0.
    for letter, _ in CELLS:
        assert seed_of(letter, 0) == r3.seed_of(letter, 0), (
            "cell %s's seed moved -- then this is not an A/B" % letter)
    seeds = [seed_of(l, o) for l, o in all_cells()]
    assert len(set(seeds)) == len(seeds), "two cells share a seed"
    print("  ok  seeds pinned to round 3 cell for cell, all %d distinct"
          % len(seeds))

    # ---- 6. ids, dirs and the fetch guard on whatever is already emitted.
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
        # The parent id may appear in prose (recipe_trace names it as
        # provenance, which is the point) but never in anything the box RUNS.
        live = derive_spec._dump({k: got[k] for k in
                                  ("steps", "payload", "artifacts", "id",
                                   "task", "env") if k in got})
        for stale in (r3.spec_id("a", 0), "guardcast3"):
            assert stale not in live, (
                "%s still names %r in a step/payload/artifact -- retoken "
                "missed it and the box would write into round 3's directory"
                % (sid, stale))
        blob = derive_spec._dump(got)
        assert work_dir(letter, offset) in blob, (
            "%s does not write into its own box directory" % sid)
        pay = got.get("payload") or {}
        assert any(k.endswith("prompt.txt") and v == positive(letter, offset)
                   for k, v in pay.items()), "%s carries a stale prompt" % sid
        assert any(k.endswith("negative.txt") and v == NEGATIVE
                   for k, v in pay.items()), (
            "%s did not inherit round 3's negative unchanged" % sid)
        cast = [s for s in got["steps"] if s["name"] == "cast"][0]["argv"]
        assert cast[cast.index("--seed") + 1] == str(seed_of(letter, offset))
        assert cast[cast.index("--task") + 1] == sid
        assert cast[cast.index("--arm") + 1] == ARM
        assert not fg.urls_in(got) or all(
            "raw.githubusercontent.com/olegmalk/banyan-city" in u
            for u in fg.urls_in(got)), (
            "%s fetches something that is not the repo: %s"
            % (sid, sorted(fg.urls_in(got))))
        stage = [s for s in got["steps"] if s["name"] == "stage"][0]["argv"][2]
        assert r2b.driver_sha() in stage, (
            "%s stages controlnet_plate.py against a sha that is not the one on "
            "disk" % sid)
    print("  ok  %d emitted spec(s) carry current strings, own task/dir/seed, "
          "the inherited negative and the live driver sha" % seen)
    print("SELFTEST: PASS")
    return 0


def write_all(force=False):
    paths = [derive_spec.write(build_root(),
                               "pipeline/jobs/%s.yaml" % spec_id("a", 0),
                               force=force)]
    for letter, offset in all_cells()[1:]:
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
