"""Insert `authored_b01_nodecount_0817` into pipeline/wave-drafts.yaml.

WHAT THIS RUNG IS. The geometry rung (`authored_b01_geom_0817`) asked whether
shape language binds where count language does not. It scored 2 of 16 on exact
leaf count -- a real null by its own pre-registered rule -- but re-reading its
clean cells at full resolution inverted the mechanism: THE CLAUSE BOUND. Stems
came back with swollen node joints and at every node exactly two leaves,
opposed, one either side. What `opposed one either side of the stem` never
constrained is HOW MANY NODES THE PLANT HAS, so the model honoured the
arrangement and stacked it two or three times up the stem -- eight cells each
obeying the instruction and returning four to six leaves. The clause describes
A NODE, not a plant. This rung constrains the free variable that exposed.

THE ONE VARIABLE IS A PURE ADDITION, WHICH IS WHY THIS SCRIPT CAN PROVE IT.
The control clause survives character for character and ` at one node` is
appended to it. Nothing else moves: the purple fig clauses, `green at its
neck`, the scale relation `no taller than the grass around it`, the style tail
and the ENTIRE negative -- including `no three leaves, no four leaves, no many
leaves` -- are byte-identical to the control. Those negatives STAY; dropping
them would be a second variable and the comparison would stop being real.
`assert draft == control.replace(OLD, OLD + ADDITION)` below is the mechanical
proof, not a claim in a comment.

WHAT THE MEASUREMENT KILLED, AND THIS IS THE POINT OF MEASURING FIRST. The
brief for this rung (ep2-b01-geom-0817.yaml, key
`the_lever_this_actually_points_at_and_why_it_is_NOT_filed_either`) proposed
`the stem bare beneath them` / `no leaves lower down`. Measured on the REAL
CLIP, THREE OF THE BRIEF'S OWN WORDINGS ARE DISQUALIFIED: each pushes the
draft far enough that compress() sheds the trailing style sentence and
`very aesthetic` -- the anchor -- goes MISSING.

    control (authored_b01_geom_0817)         73/77  dropped none   anchor True
    `... of a single node`                   74/77  dropped none   anchor True
    `... of the stem at one node`  <-- SHIPS 76/77  dropped none   anchor True
    `... , one node only`                    66/77  DROPS TAIL     anchor False
    `... of a single node, bare stem below`  67/77  DROPS TAIL     anchor False
    `... a single node, the stem bare
       beneath them`  (the brief's words)    69/77  DROPS TAIL     anchor False

Measured with ~/banyan-farm-m1pro/venv, openai/clip-vit-large-patch14, offline,
through sd_prompt.compress + sd_prompt.negative_tokens -- the two functions
render_wave_goblin.check() itself calls (render_wave_goblin.py:129-145). The
fallback estimator was NOT used and a number from it is not evidence: it does
not merely report a different figure, compress() sheds different SENTENCES
under it and the same draft becomes a different prompt. The three disqualified
wordings were DISCARDED, not trimmed to fit.

WHAT IS NOT FOLDED IN, AGAINST THE BRIEF, AND WHY. The brief says to fold in
the founder's 2026-08-17 "average leaves" ruling at the same time so
`cotyledon` is not carried a third time. READING THE RULING ITSELF REFUSES
THAT. Canon subject `sapling-cotyledon-shape` (pipeline/canon.yaml) records his
words -- "the sapling 2 leaves are average leaves" -- and then says in terms:
NOT SETTLED by his words is "whether the leaves are called cotyledons --
'average' is a ruling about shape, not about vocabulary or scale." It goes
further and names this exact text as COMPLIANT: "`wide oval cotyledon leaves
with soft round tips, not narrow, not pointed, not lance-shaped` ... describes
an average leaf and is compliant." So `cotyledon` is not debt, the ruling does
not reach it, and removing it would be an unauthorised SECOND variable in a
one-variable rung. It stays. If he wants the word gone that is a separate
wording pass with its own control.

$0, local card, no provider. Beat 01 is a STILL PLATE on an approved node.
"""
import re
import sys

import yaml

DRAFTS = "pipeline/wave-drafts.yaml"
CONTROL_KEY = "authored_b01_geom_0817"
NEW_KEY = "authored_b01_nodecount_0817"
OLD = "wide oval cotyledon leaves opposed one either side of the stem"
ADDITION = " at one node"

# The anchor is the control's own comment header. It is matched ONCE or this
# script refuses: a lane's insert anchor here once matched inside a folded
# scalar, and would have written its lines INSIDE another draft's text with a
# byte count and a sha that both moved exactly as predicted. A matching byte
# delta is not proof of a correct edit, which is why the check at the bottom
# re-PARSES and compares values instead.
ANCHOR = "    # -- `authored_b01_geom_0817` -- 2026-08-17, geometry-vs-number rung.\n"

BLOCK = '''    # -- `authored_b01_nodecount_0817` -- 2026-08-17, NODE-COUNT rung.
    # DERIVED FROM `authored_b01_geom_0817`, WHICH IS LEFT STANDING BYTE-IDENTICAL and is
    # the control: it is the draft `pipeline/jobs/ep2-b01-geom-0817.yaml` rendered over 16
    # stills and SCORED (2 of 16 count, 0 of 16 height), so this rung has a real denominator
    # on the same grid rather than a hypothetical one.
    # ONE VARIABLE, AND IT IS A PURE ADDITION: ` at one node` is appended to the control's
    # leaf clause. The control clause survives character for character. Everything else --
    # the purple fig, `green at its neck`, the scale relation, the style tail and the WHOLE
    # negative including `no three leaves, no four leaves, no many leaves` -- is byte-identical.
    # WHY: the geometry clause BOUND. Its clean cells show swollen node joints with exactly
    # two opposed leaves AT EVERY NODE; the model honoured the arrangement and stacked it two
    # or three times up the stem, which is how eight cells that each obey "opposed, one either
    # side" still return four to six leaves. `opposed one either side of the stem` describes a
    # NODE, not a plant, so it was never a count constraint and could not have been. The free
    # variable is NODE COUNT and this names it.
    # THE PREDICTION IS PRE-REGISTERED AND IT IS NOT OPTIMISTIC. `one` is a numeral, and the
    # settled outside finding is that numerals barely reach the conditioning -- CLIP's text
    # embeddings are near-identical across numerals (T2ICountBench, arXiv 2503.06884), which
    # is exactly why `exactly two` runs 0 of 16 on this arm. So this rung tests a NARROWER
    # claim than "numbers work": whether a numeral binds when it is applied to a STRUCTURAL
    # feature the model draws explicitly (a node, which it renders as a visible swollen joint)
    # rather than to the counted objects themselves. If it nulls, the designated follow-up is
    # a DEVELOPMENTAL-STAGE adjective -- a newly sprouted seedling has one node by botany
    # without asserting any number -- which is the class of wording that has actually bound
    # here (height bound; `exactly two` did not). That follow-up is NOT smuggled in.
    # REAL CLIP (openai/clip-vit-large-patch14, sd_prompt.compress + negative_tokens):
    # 76/77, headroom 1, POSITIVE DROPPED: none, STYLE ANCHOR PRESENT: True. Control on the
    # same harness: 73/77, headroom 4. HEADROOM 1 IS THE COST OF THE ADDITION and it is
    # recorded rather than hidden: beat 01 carries no goblin definition, so nothing else needs
    # that room on this beat, but this draft must not be extended without re-measuring.
    # THREE OF THE BRIEF'S OWN WORDINGS WERE DISCARDED ON MEASUREMENT, not trimmed to fit:
    # `, one node only` (66/77), `a single node, bare stem below` (67/77) and the brief's
    # literal `a single node, the stem bare beneath them` (69/77) each make compress() shed
    # the trailing style sentence, so `very aesthetic` -- the anchor -- goes MISSING.
    # `a single node` (74/77, anchor True) survived and was REJECTED anyway: it REPLACES
    # `the stem` instead of adding to it, so a win with it could not be told apart from a
    # change of referent. The wording that ships leaves the control's clause intact.
    # `cotyledon` IS DEPARTED FROM THE BRIEF AND KEPT ON PURPOSE: canon subject
    # `sapling-cotyledon-shape` says the "average leaves" ruling is "about shape, not about
    # vocabulary or scale" and names `wide oval cotyledon leaves` COMPLIANT. Removing it would
    # be an unauthorised second variable.
    # FAILURE IS REACHABLE AND IS THE STATUS QUO: the control scored 2 of 16 on this exact
    # grid and `whole plant in frame` keeps the whole stem in shot, so a second node further
    # up can appear and be counted against this.
'''


def main() -> None:
    with open(DRAFTS, encoding="utf-8") as fh:
        raw = fh.read()

    before = yaml.safe_load(raw)
    beat1 = before["beats"][1]

    if NEW_KEY in beat1:
        sys.exit("!! %s already present. Refusing to write it twice." % NEW_KEY)
    if CONTROL_KEY not in beat1:
        sys.exit("!! control %s is missing. Refusing." % CONTROL_KEY)

    control = beat1[CONTROL_KEY]
    if OLD not in control:
        sys.exit("!! the control no longer contains the clause this rung varies:\n   %r" % OLD)

    # THE SINGLE-VARIABLE PROOF, mechanical and not a claim in prose. The draft
    # IS the control with one substring extended, so no other clause can have
    # moved without this failing.
    draft = control.replace(OLD, OLD + ADDITION)
    assert draft == control.replace(OLD, OLD + ADDITION)
    if draft == control:
        sys.exit("!! the addition changed nothing. Refusing.")
    if len(draft) != len(control) + len(ADDITION):
        sys.exit("!! more than the one clause moved: %d chars against %d expected."
                 % (len(draft), len(control) + len(ADDITION)))

    n = raw.count(ANCHOR)
    if n != 1:
        sys.exit("!! anchor matches %d times, expected 1. Refusing." % n)

    # The scalar is emitted by wrapping rather than hand-typed, and the fold is
    # then CHECKED by re-parsing below. Hand-wrapping a folded scalar and
    # trusting it is how a draft acquires a stray line break the renderer sees
    # and the author does not.
    words = draft.split()
    lines, cur = [], "     "
    for w in words:
        if len(cur) + 1 + len(w) > 96:
            lines.append(cur)
            cur = "     "
        cur += " " + w
    lines.append(cur)
    scalar = "    %s: >-\n%s\n" % (NEW_KEY, "\n".join(lines))

    out = raw.replace(ANCHOR, BLOCK + scalar + ANCHOR, 1)
    with open(DRAFTS, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)

    # VERIFY BY RE-PARSING, NOT BY BYTE DELTA. A perfect byte count and a sha
    # that moves exactly as predicted are both consistent with having written
    # the lines INSIDE a neighbouring folded scalar. Only the parsed values can
    # tell the difference, so both of them are compared here.
    after = yaml.safe_load(open(DRAFTS, encoding="utf-8"))
    a1 = after["beats"][1]
    if a1.get(NEW_KEY) != draft:
        sys.exit("!! PARSED VALUE MISMATCH -- the insert landed in the wrong place.\n"
                 "   got:      %r\n   expected: %r" % (a1.get(NEW_KEY), draft))
    if a1.get(CONTROL_KEY) != control:
        sys.exit("!! THE CONTROL WAS MUTATED. Refusing to leave this on disk.")
    moved = [k for k in before["beats"] if before["beats"][k] != after["beats"][k]]
    if moved != [1]:
        sys.exit("!! beats other than 1 changed: %r" % moved)
    other = {k: v for k, v in a1.items() if k != NEW_KEY}
    if other != beat1:
        sys.exit("!! another key on beat 1 changed.")

    print("inserted %s" % NEW_KEY)
    print("  control  : %s" % control[:70])
    print("  draft    : %s" % draft[:70])
    print("  delta    : +%d chars (%r)" % (len(ADDITION), ADDITION))
    print("  re-parsed: draft matches, control byte-identical, no other key moved")


if __name__ == "__main__":
    main()
