"""Insert the two round-2 beat-01 count rungs into pipeline/wave-drafts.yaml.

BOTH RUNGS VARY THE SUBJECT PHRASE AND LEAVE THE LEAF CLAUSE ALONE, which is
what makes them independent of `authored_b01_nodecount_0817` (already rendering)
rather than a second guess at the same thing. Node count and subject wording are
different levers and each is measured against the SAME scored control,
`authored_b01_geom_0817` (2 of 16 leaf count, 0 of 16 height, purple 16 of 16).

WHY THESE TWO, AND WHY NOT THE OTHER THREE THAT MEASURED FINE.

  `authored_b01_stage_0817`  -- A DEVELOPMENTAL-STAGE ADJECTIVE. `A tiny fig
  seedling` becomes `A tiny newly sprouted fig seedling`. This is the
  discriminator the node rung's own bar pre-declared as its follow-up, and it is
  the only wording on the board that constrains leaf count WITHOUT asserting any
  number: a newly sprouted seedling has one node and one pair of leaves by
  botany. The settled outside finding is that numerals barely reach the
  conditioning (CLIP's text embeddings are near-identical across numerals,
  T2ICountBench arXiv 2503.06884), while stage and size adjectives are the class
  that HAS bound on this beat -- height bound; `exactly two` ran 0 of 16. This
  rung is the direct test of that split.

  `authored_b01_twoleaf_0817` -- AN ATTRIBUTIVE COMPOUND, AND IT IS THE APPROVED
  SCRIPT'S OWN WORDS. `A tiny fig seedling` becomes `A tiny two-leaf fig
  seedling`. Beat 01's script line reads "A tiny TWO-LEAF banyan sapling in a
  green field", so this wording is not an invention. It matters because it is a
  DIFFERENT LEXICAL ROUTE from every count wording tried here: `exactly two ...
  leaves` is a numeral quantifying a head noun, `two-leaf` is a hyphenated
  modifier of the plant itself, tokenised and attended differently. `a pair of`
  was rejected on this arm as "another lexical route to a cardinality", and that
  reasoning applies to any wording whose job is to state a total; it does NOT
  settle whether an attributive compound behaves like one. That is exactly the
  distinction this rung exists to measure, and if it binds it is the cheapest
  fix available because the script already says it.

  REJECTED THOUGH THEY MEASURED CLEAN: `just sprouted` (76/77) and `a few days
  old` (76/77) are paraphrases of `newly sprouted` and would spend the card
  re-asking one question in three wordings. `with its first leaves` (66/77) is
  DISQUALIFIED outright -- it makes compress() shed the trailing style sentence
  and `very aesthetic`, the anchor, goes MISSING. Discarded, not trimmed.

MEASUREMENT. Both shipping drafts: 76/77, headroom 1, POSITIVE DROPPED none,
STYLE ANCHOR PRESENT True. Control: 73/77, headroom 4. Measured on
~/banyan-farm-m1pro/venv with openai/clip-vit-large-patch14, offline, through
sd_prompt.compress + sd_prompt.negative_tokens -- the two functions
render_wave_goblin.check() itself calls. The fallback estimator was NOT used; a
number from it is not evidence, because compress() sheds different SENTENCES
under it and the same draft becomes a different prompt. HEADROOM 1 IS RECORDED
RATHER THAN HIDDEN: beat 01 carries no goblin definition so nothing else needs
that room here, but neither draft may be extended without re-measuring.

WHAT IS HELD BYTE-IDENTICAL IN BOTH: the leaf clause `wide oval cotyledon leaves
opposed one either side of the stem`, the purple fig clauses, `green at its
neck`, the scale relation `no taller than the grass around it`, the style tail,
and the ENTIRE negative including `no three leaves, no four leaves, no many
leaves`. Those negatives STAY in both; dropping them would be a second variable.
`cotyledon` also stays, against the round-1 brief and for the reason recorded in
insert_b01_nodecount_0817.py: canon subject `sapling-cotyledon-shape` says the
"average leaves" ruling is "about shape, not about vocabulary or scale" and
names `wide oval cotyledon leaves` compliant.

$0, local card, no provider. Beat 01 is a STILL PLATE on an approved node.
"""
import sys

import yaml

DRAFTS = "pipeline/wave-drafts.yaml"
CONTROL_KEY = "authored_b01_geom_0817"
SUBJ = "A tiny fig seedling in an open grassy field"

# The anchor each block is inserted before. Matched ONCE or this script refuses:
# an insert anchor here once matched inside a folded scalar and would have
# written its lines INSIDE another draft's text, with a byte count and a sha that
# both moved exactly as predicted. That is why the check at the bottom re-PARSES
# and compares values instead of trusting a delta.
ANCHOR = "    # -- `authored_b01_geom_0817` -- 2026-08-17, geometry-vs-number rung.\n"

RUNGS = [
    {
        "key": "authored_b01_stage_0817",
        "new_subject": "A tiny newly sprouted fig seedling in an open grassy field",
        "comment": '''    # -- `authored_b01_stage_0817` -- 2026-08-17, DEVELOPMENTAL-STAGE rung.
    # DERIVED FROM `authored_b01_geom_0817`, WHICH IS LEFT STANDING BYTE-IDENTICAL and is the
    # control: rendered over 16 stills and SCORED (2 of 16 leaf count, 0 of 16 height, purple
    # 16 of 16), so this rung has a real denominator on the same grid.
    # ONE VARIABLE, A PURE ADDITION TO THE SUBJECT: `A tiny fig seedling` becomes `A tiny newly
    # sprouted fig seedling`. THE LEAF CLAUSE IS UNTOUCHED, which is what makes this independent
    # of the node rung rather than a second guess at it -- that one varies the leaf clause and
    # this one does not touch it.
    # WHY THIS IS THE MOST PROMISING WORDING ON THE BOARD: it is the only one that constrains
    # leaf count WITHOUT ASSERTING A NUMBER. A newly sprouted seedling has one node and one pair
    # of leaves by botany. Numerals barely reach the conditioning -- CLIP's embeddings are
    # near-identical across them (T2ICountBench, arXiv 2503.06884) -- and on this arm `exactly
    # two` ran 0 of 16 while a CONTINUOUS adjective, the height relation, bound. Stage adjectives
    # are that class. This rung is the direct test of that split and it was PRE-DECLARED as the
    # discriminator in the node rung's own bar before that rung rendered.
    # REAL CLIP (openai/clip-vit-large-patch14, sd_prompt.compress + negative_tokens): 76/77,
    # headroom 1, POSITIVE DROPPED: none, STYLE ANCHOR PRESENT: True. Control: 73/77, headroom 4.
    # `just sprouted` and `a few days old` both measured 76/77 clean and were REJECTED as
    # paraphrases -- firing three wordings of one question spends the card to learn once.
    # `with its first leaves` was DISQUALIFIED at 66/77: it makes compress() shed the style
    # sentence and the anchor goes missing. Discarded, not trimmed.
    # FAILURE IS REACHABLE: the control scored 2 of 16 on this grid, `whole plant in frame` keeps
    # the whole stem in shot, and `newly sprouted` may simply read as "small" -- which the draft
    # ALREADY says twice (`tiny`, `no taller than the grass`), in which case nothing moves.
''',
    },
    {
        "key": "authored_b01_twoleaf_0817",
        "new_subject": "A tiny two-leaf fig seedling in an open grassy field",
        "comment": '''    # -- `authored_b01_twoleaf_0817` -- 2026-08-17, ATTRIBUTIVE-COMPOUND rung.
    # DERIVED FROM `authored_b01_geom_0817`, WHICH IS LEFT STANDING BYTE-IDENTICAL and is the
    # same control on the same grid as the stage rung beside it.
    # ONE VARIABLE, A PURE ADDITION TO THE SUBJECT: `A tiny fig seedling` becomes `A tiny
    # two-leaf fig seedling`. THE LEAF CLAUSE IS UNTOUCHED.
    # THIS IS THE APPROVED SCRIPT'S OWN WORDING AND NOT AN INVENTION. Beat 01's script line,
    # node.md verbatim, reads "A tiny TWO-LEAF banyan sapling in a green field".
    # WHY IT IS NOT JUST `exactly two` AGAIN, WHICH IS THE OBVIOUS OBJECTION: `exactly two wide
    # oval cotyledon leaves` is a NUMERAL QUANTIFYING A HEAD NOUN; `two-leaf` is a HYPHENATED
    # MODIFIER OF THE PLANT, a property of the seedling rather than a count of objects in the
    # frame, and it tokenises and attends differently. `a pair of ...` was rejected on this arm
    # as "another lexical route to a cardinality", and that reasoning holds for any wording whose
    # job is to STATE A TOTAL -- it does not settle whether an attributive compound behaves like
    # one. That is the distinction this rung measures. IF IT BINDS IT IS THE CHEAPEST FIX
    # AVAILABLE, because the script already says it and no new canon is needed.
    # REAL CLIP (openai/clip-vit-large-patch14, sd_prompt.compress + negative_tokens): 76/77,
    # headroom 1, POSITIVE DROPPED: none, STYLE ANCHOR PRESENT: True. Control: 73/77, headroom 4.
    # FAILURE IS REACHABLE AND IS THE STRONGLY PREDICTED OUTCOME: three count-bearing wordings
    # have now scored 0-2 of 16 on this arm, and if the tokeniser splits `two-leaf` into `two`
    # and `leaf` this rung IS `exactly two` wearing a hyphen and will null exactly like it. That
    # is a real possibility and it is written down BEFORE the frames exist rather than offered
    # afterwards as an explanation.
''',
    },
]


def wrap_scalar(key: str, draft: str) -> str:
    """Emit the folded scalar by wrapping, then let the caller re-parse it.

    Hand-typing a folded scalar and trusting it is how a draft acquires a line
    break the renderer sees and the author does not.
    """
    lines, cur = [], "     "
    for w in draft.split():
        if len(cur) + 1 + len(w) > 96:
            lines.append(cur)
            cur = "     "
        cur += " " + w
    lines.append(cur)
    return "    %s: >-\n%s\n" % (key, "\n".join(lines))


def main() -> None:
    with open(DRAFTS, encoding="utf-8") as fh:
        raw = fh.read()
    before = yaml.safe_load(raw)
    beat1 = before["beats"][1]

    if CONTROL_KEY not in beat1:
        sys.exit("!! control %s is missing. Refusing." % CONTROL_KEY)
    control = beat1[CONTROL_KEY]
    if SUBJ not in control:
        sys.exit("!! the control no longer contains the subject phrase:\n   %r" % SUBJ)
    if control.count(SUBJ) != 1:
        sys.exit("!! subject phrase appears %d times in the control, expected 1."
                 % control.count(SUBJ))

    n = raw.count(ANCHOR)
    if n != 1:
        sys.exit("!! anchor matches %d times, expected 1. Refusing." % n)

    expect = {}
    blocks = ""
    for rung in RUNGS:
        key, new_subj = rung["key"], rung["new_subject"]
        if key in beat1:
            sys.exit("!! %s already present. Refusing to write it twice." % key)
        draft = control.replace(SUBJ, new_subj)
        if draft == control:
            sys.exit("!! %s: the substitution changed nothing. Refusing." % key)
        if len(draft) != len(control) - len(SUBJ) + len(new_subj):
            sys.exit("!! %s: more than one site moved. Refusing." % key)
        # The leaf clause is the thing these rungs must NOT touch. Assert it.
        clause = "wide oval cotyledon leaves opposed one either side of the stem"
        if clause not in draft:
            sys.exit("!! %s: the leaf clause did not survive. Refusing." % key)
        expect[key] = draft
        blocks += rung["comment"] + wrap_scalar(key, draft)

    out = raw.replace(ANCHOR, blocks + ANCHOR, 1)
    with open(DRAFTS, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)

    # VERIFY BY RE-PARSING, NOT BY BYTE DELTA. A perfect byte count is
    # consistent with having written the lines INSIDE a neighbouring scalar.
    after = yaml.safe_load(open(DRAFTS, encoding="utf-8"))
    a1 = after["beats"][1]
    for key, draft in expect.items():
        if a1.get(key) != draft:
            sys.exit("!! PARSED VALUE MISMATCH for %s -- the insert landed wrong.\n"
                     "   got:      %r\n   expected: %r" % (key, a1.get(key), draft))
    if a1.get(CONTROL_KEY) != control:
        sys.exit("!! THE CONTROL WAS MUTATED. Refusing to leave this on disk.")
    moved = [k for k in before["beats"] if before["beats"][k] != after["beats"][k]]
    if moved != [1]:
        sys.exit("!! beats other than 1 changed: %r" % moved)
    other = {k: v for k, v in a1.items() if k not in expect}
    if other != beat1:
        sys.exit("!! another key on beat 1 changed.")

    for key in expect:
        print("inserted %s" % key)
    print("re-parsed: both drafts match, control byte-identical, no other key moved")


if __name__ == "__main__":
    main()
