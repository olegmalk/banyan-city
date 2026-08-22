#!/usr/bin/env python3
r"""GUARD-2 CASTING, ROUND 3 — the effect-symbols come off the faces.

    python3 pipeline/derive_guardcast3_0822.py --selftest   # assert, write nothing
    python3 pipeline/derive_guardcast3_0822.py --write      # emit the fifteen specs

THE FOUNDER'S WORDS ON ROUND 2, AND THEY ARE THE WHOLE BRIEF: "most of these
have some kinda gas or liquid on their face which is a problem." He is not
describing a lighting key or a skin shader. He is describing MANGA EFFECT
SYMBOLS -- the sweat drop, the sigh/steam puff, the dizzy spiral, the drool
bead -- drawn ON the face as if they were anatomy. The sheet's own notes had
already half-seen it and mis-filed it as paint-out work: "A and C have a white
blob at the mouth. A drool-or-foam artifact the model added on its own --
nothing in the prompt asks for it." Nothing asks for it BY NAME. Round 2's
per-cell clauses ask for it by association.

WHERE IT COMES FROM. animagine-xl-3.1 is trained on booru captions, and on that
site the dazed/dumb expression tags travel with the symbol tags in the same
captions. Round 2's ten clauses carried, between them: `blank stare`,
`drooping eyelids`, `half-closed eyes`, `puzzled frown`, `gormless grin`,
`eyebrows raised`, `mouth slightly open`, `slack mouth`. `puzzled` co-occurs
with `sweatdrop` and `?`; the sigh-adjacent lidded tags co-occur with `steam`;
`blank stare` sits next to `spiral eyes`. Ask for the tone and you get the
tone's punctuation drawn on the skin.

SO ROUND 3 MOVES TWO THINGS AND NOTHING ELSE.

  (a) EXPRESSION LEAVES THE PER-CELL CLAUSE ENTIRELY. Each cell now varies HAIR,
      FACE STRUCTURE and BUILD only -- the axis a casting sheet exists to move --
      and every cell carries the SAME expression string, in the vocabulary the
      goblin emotion work proved and for the reason that work states in the
      drafts file: "structural terms beat tone words... `slack open mouth` and
      `dull half-closed eyes` ARE a vacant expression, drawn as anatomy."

          slack open mouth, raised eyebrows, dull half-closed eyes

      Mouth and brow and lid. No tone word, nothing that names a feeling, so
      nothing that drags a feeling's symbol in behind it. `raised eyebrows` is
      also the answer to round 2's second reported fault -- "they read angry
      more than they read dumb" -- because it lifts the brow off the forward
      slope that IS anger anatomically. Eye-structure terms are out of the cell
      clauses too (`small eyes`, `wide-set eyes`, `heavy brow`): they fought the
      shared lid term, and one channel cannot be authored twice.

  (b) THE NEGATIVE GAINS THE SYMBOL FAMILY BY NAME. `sweatdrop, steam, sigh,
      spiral eyes, dizzy, speech bubble, sparkle, drool` lead the string, because
      this file's own law is that the tail is what CLIP drops and the round's
      variable never rides in the tail.

MEASURED, NOT ESTIMATED -- clip_token_count over animagine's own vocab.json:

  * `saliva` and `unfocused` are NOT single tokens in this model's vocabulary
    (`saliva` splits, `unfocused` splits) and BOTH WERE CUT rather than paid for:
    `drool` (one token, in vocab) already carries the liquid, and the lid term
    carries the unfocused read as anatomy.
  * `sweatdrop` is not a single token either -- it costs two, the same as the
    two-word form -- and it is KEPT anyway because it is the symbol's booru NAME
    and the name is what the caption distribution keys on.
  * 77 is the context length and the two specials live inside it, so 75 is the
    real ceiling. The negative measures 73 of 75 with nothing dropped and the
    worst positive 71 of 75. Round 2's negative was 68 and carried `text` twice
    and both `photorealistic` and `photorealism`; de-duplicating those, plus
    `plain background`, `signature` and `knight` (armor and helmet already carry
    that read), is what paid for the nine symbol tokens AND left two spare --
    a negative sitting exactly ON the ceiling drops its tail the moment the next
    lane adds a word, which is how beat 06/08 lost theirs in silence. Round 2's DROP terms are
    all still present -- girl, child, teenager, glasses, hands -- none was
    evicted to make room, because those are the bar and the bar does not move.

WHAT IS HELD, so that the founder is looking at the same men: checkpoint
animagine-xl-3.1, prose prompt closing on the ratified style tail, 40 steps,
cfg 7.5, 832x1216, no ControlNet, no IP-Adapter, the same driver, the same
costume and background words, and the same ten hair-and-build ideas he has
already seen. The men do not change. Their faces stop punctuating.

SEEDS ARE PINNED AND THE SHEET'S ARITHMETIC IS UNCHANGED: SEED_BASE +
index*1000 for the ten, which is CELL FOR CELL round 2B's seed, so every round-3
frame is a true A/B against the frame on the page right now -- same seed, same
man, expression wording and negative the only difference. Five of those ten
(a, b, d, h, j) are the cells the hand-on-cheek prior lands on, a checkpoint
habit rounds 2B/2C/2D proved is beaten by re-seeding and not by words; each gets
ONE recovery draw at offset 30 (clear of 2B's 0-9 and 2D's 10-20). Fifteen
frames, about six minutes of card time, $0.

THE ONE-SAMPLE RULE, APPLIED RATHER THAN WAIVED. This IS a recipe change, so
cell A carries `sample: true` and is filed FIRST: it is the frame that answers
whether stripping the tone words and naming the symbols actually clears the
face. The remaining fourteen are filed behind it in the same batch because the
whole batch is six card-minutes and the founder is at the page now -- but the
gate is real, not decorative: cell A is judged at 1:1 the moment it lands, and
if the gas or the liquid is still there the queued remainder is PULLED rather
than published, and the sheet reports a second miss instead of fifteen of it.

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

ARM = r2b.ARM                     # "nocontrol" -- the literal the driver gates on
SEED_BASE = r2.SEED_BASE          # 20260725
RECOVERY = ("a", "b", "d", "h", "j")   # the cells the hand prior lands on
RECOVERY_OFFSET = 30              # clear of 2B's 0..9 and 2D's 10 and 20

# THE EXPRESSION, IDENTICAL IN ALL FIFTEEN CELLS. Mouth, brow, lid -- three
# structures. Not one tone word, which is the entire point of the round.
EXPRESSION = "slack open mouth, raised eyebrows, dull half-closed eyes"

# HAIR / FACE STRUCTURE / BUILD ONLY. Same ten men as the sheet he is looking
# at, with every expression term and every eye-structure term lifted out.
CELLS = (
    ("a", "thick dark brown hair, heavy square jaw, thick neck"),
    ("b", "light sandy hair, long thin face, weak chin"),
    ("c", "cropped ginger hair, round heavy face, full cheeks"),
    ("d", "shaved head, dark stubble, broad flat face"),
    ("e", "shaggy black hair, gaunt narrow face, big ears"),
    ("f", "grey-streaked brown hair, thick moustache, jowly face"),
    ("g", "receding sandy hair, high forehead, narrow face"),
    ("h", "curly black hair, wide square face, thick neck"),
    ("i", "straight light brown hair, big nose, doughy face"),
    ("j", "short red hair, freckles, blunt chin"),
)

# The symbol family LEADS. Everything after it is round 2's negative with its
# duplicates removed; the five DROP terms sit ahead of the scene terms because
# a dropped tail must never cost a drop term.
NEGATIVE = ", ".join((
    "sweatdrop", "steam", "sigh", "spiral eyes", "dizzy", "speech bubble",
    "sparkle", "drool",
    "girl", "child", "teenager", "glasses", "hands",
    "photorealistic", "3d render", "realistic skin texture", "blurry",
    "low quality", "jpeg artifacts", "deformed", "extra limbs", "text",
    "watermark",
    "clipboard", "armor", "helmet", "white background", "dark", "night",
))


def index_of(letter):
    return [l for l, _ in CELLS].index(letter)


def body_of(letter):
    return dict(CELLS)[letter]


def spec_id(letter, offset=0):
    if offset:
        return "ep2-guardcast3-%s%d-0822" % (letter, offset)
    return "ep2-guardcast3-%s-0822" % letter


def work_dir(letter, offset=0):
    return r"C:\banyan-farm\%s" % spec_id(letter, offset)


def seed_of(letter, offset=0):
    return SEED_BASE + (index_of(letter) + offset) * 1000


def positive(letter):
    """The compiled positive, baked here rather than looked up on the box.

    Round 2B compiled through render_wave_goblin over wave-drafts.yaml and then
    BAKED the result into payload for exactly this reason: "nothing about the
    wording can drift between filing and firing". Round 3's wording is not in
    the drafts file at all -- it is this round's variable and it is authored
    here, in one template, so the fifteen cells cannot disagree about the two
    strings the round exists to test.
    """
    return ("1boy, a grown guard man, mature male face, %s, %s, close on his "
            "face, cream shirt collar, white shoulder sash, tall grass, "
            "hedgerow behind, cinematic lighting, masterpiece, best quality, "
            "very aesthetic" % (body_of(letter), EXPRESSION))


def _stage_step(letter, offset=0):
    body = r2b._stage_step("a")["argv"][2].replace(
        r2b.work_dir("a"), work_dir(letter, offset))
    return {"name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def _publish_step(letter, offset=0):
    body = r2b._publish_step("a")["argv"][2].replace(
        r2b.work_dir("a").replace("\\", "/"),
        work_dir(letter, offset).replace("\\", "/")
    ).replace(r2b.spec_id("a"), spec_id(letter, offset))
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
    "never by a metric. THE ROUND'S OWN CLAUSE, and it is a DROP and not a note: "
    "(0) NO EFFECT SYMBOL ANYWHERE ON THE FACE -- no sweat drop, no steam or sigh "
    "puff, no dizzy spiral, no drool or foam bead, no sparkle, no bubble. The "
    "founder's words on round 2 were \"most of these have some kinda gas or "
    "liquid on their face which is a problem\", and a frame carrying one does not "
    "reach the sheet however good the face under it is. THE STANDING BAR, "
    "repeated term for term rather than referenced because a bar that lives in "
    "another spec is a bar nobody reads: (1) ONE GROWN MAN alone in frame -- "
    "child, teenager or female is a DROP; (2) the face reads DUMB at a glance -- "
    "slack, blank, gormless (\"they should look like grown men. yes. dumb grown "
    "men\") -- and this round wants it read as ANATOMY, not as an expression "
    "label; (3) DETAILED CINEMATIC ANIME, the look of "
    "taste/refs/guard1-canon-founder-0822.png; a flat or muted tag-sheet look is "
    "a fail; (4) NO GLASSES and NO HAND in frame; (5) cream shirt collar and "
    "white shoulder sash read as the costume family; (6) head and shoulders, face "
    "toward the lens, real grass-and-hedgerow background; (7) HE IS NOT GUARD 1. "
    "PRE-REGISTERED FAIL MODES: the shared expression string making the ten faces "
    "read as ONE man in ten wigs, which is the cost of moving expression out of "
    "the cell clause and is the thing to watch on the contact sheet rather than "
    "on any single frame; and the hand-on-cheek prior returning on a, b, d, h, j, "
    "which is why those five carry a second draw at offset 30."
)

CONSUMER = (
    "THE FOUNDER, on /review/ep2-guardcast2-0822, which this round UPDATES in "
    "place -- round 3 on top, round 2 collapsed and greyed beneath it so the "
    "comparison he asked for survives. He is at that page now. Nothing "
    "downstream consumes these frames until he picks: no beat plate, no motion "
    "job, no clip, and review/ep2-ship-0821 is untouched."
)

SCRIPT_AUTHORITY = (
    "Node 002b-first-citizen, live script `002b-t0-c`, `approved_by: founder`, "
    "`approved_on: 2026-08-03`. A STILL CASTING PLATE on an approved node: no "
    "voice, no motion, no episode assembly, no publication.")

SCRIPT_LINE = ("Beat 06 THE CLIPBOARD: guard 2, the one with the bark board. "
               "Head and shoulders, no prop -- the question is his FACE.")


def build_root():
    letter, offset = "a", 0
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
        "sample": True,
        "est_minutes": 2,
        "needs": ["cuda", "vram12", "sdxl-venv"],
        "owner": ("guard lane, 2026-08-22 -- round 3, filed on the founder's "
                  "round-2 note about gas and liquid on the faces"),
        "consumer": CONSUMER,
        "success": BAR,
        "why": (
            "GUARD 2, CELL A OF TEN, EFFECT SYMBOLS OFF THE FACE: %s. Round 2's "
            "faces came back carrying manga effect symbols -- sweat drops, sigh "
            "steam, drool beads -- drawn as anatomy, because its per-cell clauses "
            "named DAZED TONES (`blank stare`, `puzzled frown`, `half-closed "
            "eyes`, `gormless grin`) and on this checkpoint's booru captions the "
            "tone tags and the symbol tags travel together. Two changes and no "
            "others: expression leaves the cell clause for one shared "
            "mouth/brow/lid string in the vocabulary the goblin work proved, and "
            "the negative gains the symbol family by name at its HEAD. Checkpoint, "
            "driver, steps, cfg, size, costume, background, style tail and seed "
            "all held -- seed %d is 2B's cell-A seed, so this frame is a true A/B "
            "against the one on the page. $0, local card. Full reasoning in "
            "pipeline/derive_guardcast3_0822.py."
            % (body_of(letter), seed_of(letter, offset))),
        "script_authority": SCRIPT_AUTHORITY,
        "script_line": SCRIPT_LINE,
        "env": dict(r2b.build_root()["env"]),
        "payload": {
            w + r"\prompt.txt": positive(letter),
            w + r"\negative.txt": NEGATIVE,
        },
        "steps": [
            _stage_step(letter, offset),
            {"name": "cast", "argv": _cast_argv(letter, offset)},
            _publish_step(letter, offset),
        ],
        "recipe_trace": (
            "pipeline/jobs/ep2-guardcast2b-a-0822.yaml with the positive's "
            "expression clause replaced by the shared string %r and the negative "
            "replaced by the symbol-led string in "
            "pipeline/derive_guardcast3_0822.py. Driver "
            "pipeline/controlnet_plate.py sha %s, fetched and sha-checked before a "
            "GPU second is spent; --control unset so no ControlNet loads, no "
            "--ip-ref passed so no adapter loads. Both strings MEASURED on "
            "animagine's own vocab with pipeline/clip_token_count.py: positive %d "
            "of 77, negative %d of 77, nothing dropped."
            % (EXPRESSION, r2b.driver_sha()[:16],
               _tok(positive(letter)), _tok(NEGATIVE))),
        "one_sample_rule": (
            "CELL A IS THE SAMPLE AND IT IS FILED FIRST. This is a recipe change "
            "-- two strings that reach CLIP move -- so the rule applies rather "
            "than being waived. The fourteen behind it are filed in the same batch "
            "because the whole batch is six card-minutes at $0 and the founder is "
            "at the page now, but the gate is real: cell A is judged at 1:1 as "
            "soon as it lands and if a symbol is still on the face the queued "
            "remainder is PULLED, not published."),
        "seed_note": (
            "Seeds are the sheet's own arithmetic, unchanged: SEED_BASE + "
            "index*1000, i.e. %d for cell A and %d..%d for B..J -- IDENTICAL to "
            "round 2B cell for cell, which is what makes round 3 an A/B rather "
            "than fifteen unrelated pictures. The five hand-prior cells (a, b, d, "
            "h, j) each carry one recovery draw at offset 30, clear of 2B's 0..9 "
            "and 2D's 10 and 20." % (SEED_BASE, SEED_BASE + 1000,
                                     SEED_BASE + 9000)),
        "artifacts": [w + r"\out\%s-%s.png" % (spec_id(letter, offset), ARM)],
    }


def _tok(text):
    import clip_token_count as ctc
    return ctc.Clip().count(text)[0]


def sibling(letter, offset=0):
    src_id = spec_id("a", 0)
    tag = letter.upper() + (" (recovery draw, offset %d)" % offset if offset
                            else "")
    return derive_spec.derive(
        src="pipeline/jobs/%s.yaml" % src_id,
        new_id=spec_id(letter, offset),
        fresh={
            "owner": ("guard lane, 2026-08-22 -- cell %s of round 3, filed with "
                      "the batch behind the cell-A sample" % tag),
            "consumer": (
                "THE FOUNDER, as candidate %s on /review/ep2-guardcast2-0822, "
                "which round 3 updates in place -- round 3 on top, round 2 "
                "collapsed and greyed beneath so the A/B he is owed survives. "
                "Not a sample: cell A answers whether the symbol strip works, "
                "and this cell only adds a face to choose between. Nothing "
                "downstream consumes it until he picks and "
                "review/ep2-ship-0821 is untouched." % tag),
            "success": (
                "ONE 832x1216 png at seed %d, scored at 1:1 on the bar cell A "
                "pre-registered, unchanged and applying term for term -- the "
                "no-symbol clause first. The only thing this spec moves is the "
                "hair-and-build clause and the seed: %s."
                % (seed_of(letter, offset), body_of(letter))),
            "why": (
                "GUARD 2, CELL %s, EFFECT SYMBOLS OFF THE FACE: %s. One variable "
                "against cell A -- the hair-and-build clause and the seed that "
                "follows from the cell's position%s. Driver, checkpoint, steps, "
                "cfg, size, framing, costume, background, style tail, shared "
                "expression string and negative all held. $0."
                % (tag, body_of(letter),
                   (". This is the SECOND draw of a cell the hand-on-cheek prior "
                    "lands on: rounds 2B/2C/2D proved that prior is beaten by "
                    "re-seeding and not by negative terms, so the cell gets one "
                    "more seed rather than a longer prompt") if offset else "")),
        },
        # NO negative override, and its absence is correct: the negative is this
        # sheet's CONSTANT -- it is the round's other variable and it must be
        # byte-identical in all fifteen cells -- so it is inherited from cell A
        # and its payload KEY is retokened to this cell's own working directory.
        # THE PROMPT OVERRIDE IS CONDITIONAL FOR THE SAME REASON. Cell A's own
        # recovery draw moves the SEED and nothing else, so offering it cell A's
        # prompt is offering the parent's bytes back -- which derive_spec refuses
        # by design ("that is not an override"), and it is right to: a spec that
        # claims a variable it did not move is a spec that lies in its record.
        overrides=dict(
            {"seed": seed_of(letter, offset)},
            **({} if positive(letter) == positive("a")
               else {"payload:prompt.txt": positive(letter)})),
        retoken=[(spec_id("a", 0), spec_id(letter, offset))],
        extra={"cell": ("cell %s of round 3. Sheet: "
                        "/review/ep2-guardcast2-0822. Reasoning: "
                        "pipeline/derive_guardcast3_0822.py." % tag)},
        by="pipeline/derive_guardcast3_0822.py",
    )


def all_cells():
    """(letter, offset) in FIRING ORDER: the sample, then the ten, then the five."""
    out = [("a", 0)]
    out += [(l, 0) for l, _ in CELLS if l != "a"]
    out += [(l, RECOVERY_OFFSET) for l in RECOVERY]
    return out


# --------------------------------------------------------------------------
def _selftest():
    print("derive_guardcast3_0822 selftest")
    import clip_token_count as ctc
    import derive_fetch_guard as fg
    c = ctc.Clip()

    # 1. THE BUDGET, on the model's own vocab. 77 is the context length and the
    #    two specials are inside it, so 75 is the real ceiling for text.
    n_neg = c.count(NEGATIVE)[0]
    assert n_neg <= 75, "negative is %d of 75 -- the tail would be dropped" % n_neg
    worst = 0
    for letter, _ in CELLS:
        n = c.count(positive(letter))[0]
        assert n <= 75, "cell %s positive is %d of 75" % (letter, n)
        worst = max(worst, n)
    print("  ok  negative %d/75, worst positive %d/75, measured on animagine's "
          "own vocab.json" % (n_neg, worst))

    # 2. EVERY SYMBOL TERM THE FOUNDER'S NOTE NAMES IS ACTUALLY NEGATED, and the
    #    two that are not real vocabulary words were CUT rather than paid for.
    for term in ("sweatdrop", "steam", "sigh", "spiral", "dizzy",
                 "speech bubble", "sparkle", "drool"):
        assert term in NEGATIVE, "symbol term %r never reached the negative" % term
    for cut in ("saliva", "unfocused"):
        assert cut not in NEGATIVE and all(cut not in positive(l)
                                           for l, _ in CELLS), (
            "%r splits in this model's vocab and was cut -- it is back" % cut)
    assert NEGATIVE.startswith("sweatdrop"), (
        "the round's own variable must LEAD the negative: CLIP drops the tail")
    print("  ok  eight symbol terms negated and leading; saliva/unfocused stay cut")

    # 3. THE DROP TERMS SURVIVED THE REWRITE. Nine symbol tokens were paid for
    #    out of duplicates, never out of the bar.
    for term in ("girl", "child", "teenager", "glasses", "hands"):
        assert term in NEGATIVE, "the bar lost %r making room for symbols" % term
    terms = [t.strip() for t in NEGATIVE.split(",")]
    assert len(terms) == len(set(terms)), "a term is negated twice"
    assert terms.count("text") == 1 and "photorealism" not in terms, (
        "round 2's duplicates -- `text` twice, photorealistic AND photorealism "
        "-- are what paid for the symbol family; one is back")
    assert n_neg <= 73, (
        "no headroom: 75 is the ceiling and a negative sitting ON it drops its "
        "tail the moment anyone adds a word")
    print("  ok  girl/child/teenager/glasses/hands all still negated")

    # 4. NO TONE WORD SURVIVES IN ANY POSITIVE. This is the round, in one assert.
    for letter, _ in CELLS:
        p = positive(letter)
        assert EXPRESSION in p, letter
        assert body_of(letter) in p, (
            "cell %s: its own clause is not in its positive" % letter)
        for tone in ("blank stare", "puzzled", "gormless", "vacant", "confused",
                     "drooping", "sleepy", "surprised", "worried", "grin",
                     "frown", "smile", "stare"):
            assert tone not in p, (
                "cell %s still names the tone %r -- that is what pulls the symbol"
                % (letter, tone))
        for eye in ("small eyes", "wide-set eyes", "heavy brow"):
            assert eye not in p, (
                "cell %s authors the eye/brow channel twice (%r vs the shared "
                "expression string)" % (letter, eye))
    print("  ok  ten positives: shared mouth/brow/lid string, zero tone words, "
          "one author per channel")

    # 5. SEEDS: pinned, collision-free, and lined up with 2B cell for cell.
    seeds = {}
    for letter, offset in all_cells():
        s = seed_of(letter, offset)
        assert s not in seeds, "seed %d used twice (%s vs %s)" % (
            s, seeds.get(s), (letter, offset))
        seeds[s] = (letter, offset)
    for index, (letter, _) in enumerate(CELLS):
        assert seed_of(letter, 0) == SEED_BASE + index * 1000, letter
    for letter in RECOVERY:
        off = seed_of(letter, RECOVERY_OFFSET) - SEED_BASE
        assert off // 1000 >= 30, letter          # clear of 2B (0-9), 2D (10-20)
    assert len(seeds) == 15
    print("  ok  15 distinct pinned seeds; the ten are 2B's cell for cell, the "
          "five recovery draws clear 2B and 2D")

    # 6. THE DRIVER GATE. 2B paid a render to learn the arm string is a literal.
    root = build_root()
    argv = [s for s in root["steps"] if s["name"] == "cast"][0]["argv"]
    assert ARM == "nocontrol", (
        "controlnet_plate gates its ControlNet branch on `arm != \"nocontrol\"` "
        "-- any other arm name makes --control mandatory and the job exits rc 6")
    assert "--control" not in argv and "--ip-ref" not in argv, (
        "round 3 changes the WORDS; a conditioner reaching it would confound it")
    assert argv[argv.index("--seed") + 1] == str(SEED_BASE)
    assert argv[argv.index("--steps") + 1] == "40"
    assert argv[argv.index("--cfg") + 1] == "7.5"
    assert root["sample"] is True, "the recipe changed; cell A is the sample"
    print("  ok  cell A: no --control, no --ip-ref, seed %d, 40 steps, cfg 7.5, "
          "sample gate on" % SEED_BASE)

    # 7. THE EMITTED FILES, if they are on disk: current strings, own identity,
    #    and no invented fetch URL left behind by retoken (the 08-20 trap).
    n = 0
    for letter, offset in all_cells():
        p = os.path.join(REPO, "pipeline", "jobs",
                         "%s.yaml" % spec_id(letter, offset))
        if not os.path.isfile(p):
            continue
        got = derive_spec.load(p)
        n += 1
        assert got["id"] == spec_id(letter, offset), p
        pay = got.get("payload") or {}
        assert any(k.endswith("prompt.txt") and v == positive(letter)
                   for k, v in pay.items()), (
            "%s carries a STALE prompt -- re-run --write --force" % p)
        assert any(k.endswith("negative.txt") and v == NEGATIVE
                   for k, v in pay.items()), (
            "%s carries a STALE negative -- re-run --write --force" % p)
        for k in pay:
            assert spec_id(letter, offset) in k, (
                "%s writes a payload into ANOTHER cell's working directory: %s"
                % (p, k))
        cast = [s for s in got["steps"] if s["name"] == "cast"][0]["argv"]
        assert cast[cast.index("--task") + 1] == spec_id(letter, offset), (
            "%s renders under another cell's task name -- the png would collide"
            % p)
        assert cast[cast.index("--seed") + 1] == str(seed_of(letter, offset)), p
        # THE RETOKEN TRAP, in its other direction. `assert_fetch_urls_resolve`
        # guards a child that fetches a PUBLISHED ARTIFACT, and refuses when it
        # finds no farm-out URL at all -- correct for that shape, wrong for this
        # one: round 3 stages ONE input, the driver, by sha off raw main. So the
        # assertion here is that retoken invented no artifact address (there is
        # nothing on farm-out under these names and a fetch of one would 404 on
        # the card), and that the sha it must match survived retoken intact.
        assert not fg.urls_in(got), (
            "%s fetches a farm-out artifact it should not: %s"
            % (p, sorted(fg.urls_in(got))))
        stage = [t for t in got["steps"] if t["name"] == "stage"][0]["argv"][2]
        assert r2b.driver_sha() in stage, (
            "%s stages controlnet_plate.py against a sha that is not the one on "
            "disk -- retoken mangled it, or the driver moved under the batch" % p)
    print("  ok  %d emitted spec(s) carry current strings, own task/dir/seed, "
          "no invented artifact URL, and the live driver sha" % n)
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
