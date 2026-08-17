"""Author the two round-2 beat-01 job specs FROM the node-count spec.

WHY A GENERATOR AND NOT TWO HAND-TYPED FILES. `steps`, `env`, `needs`, the grid,
the reference set, the arm and the seeds must be IDENTICAL to the rung these are
compared against, or the comparison is not real. Copying them mechanically is
how that becomes true rather than intended -- the geometry rung made the same
choice and said so. Only the three prose fields that must differ are authored
here: `consumer`, `why` and `success`. Everything else is carried over and the
check at the bottom refuses if any of it moved.

Comments do not survive a yaml round-trip, so each spec's header block is
authored here explicitly and written above the dumped body.

Run from the repo root. Writes pipeline/jobs/ep2-b01-stage-0817.yaml and
pipeline/jobs/ep2-b01-twoleaf-0817.yaml. Refuses to overwrite either.
"""
import copy
import os
import sys

import yaml

SRC = "pipeline/jobs/ep2-b01-nodecount-0817.yaml"

MEASURED = """# Draft key: %(key)s. Measured on the REAL CLIP before this file was filed
# (openai/clip-vit-large-patch14 via sd_prompt.compress + negative_tokens, the two functions
# render_wave_goblin.check() itself calls, on ~/banyan-farm-m1pro/venv, offline): positive
# 76/77, headroom 1, POSITIVE DROPPED: none, STYLE ANCHOR PRESENT: True. The control
# `authored_b01_geom_0817` measures 73/77 headroom 4 on that same harness and is BYTE-IDENTICAL
# on disk after the insert -- pipeline/insert_b01_round2_0817.py re-parses the file and refuses
# to leave a mutated control behind. The fallback estimator was NOT used: it changes verdicts and
# not merely numbers, because compress() sheds different SENTENCES under it. `with its first
# leaves` was DISQUALIFIED at 66/77 for shedding the style sentence and losing the anchor --
# discarded, not trimmed. HEADROOM 1 IS RECORDED, NOT HIDDEN: beat 01 carries no goblin
# definition so nothing else needs that room here, but this draft must not be extended without
# re-measuring.
# steps, env, needs, refs, arm and seeds were COPIED from ep2-b01-nodecount-0817 by
# pipeline/author_b01_round2_specs_0817.py rather than retyped, so identity is how the file was
# made and not something the author remembered to do.
# NEVER RUN: verified on the box, not inferred from a local file -- C:\\banyan-queue\\done and
# \\failed contain no %(id)s-*.json and C:\\banyan-farm\\courier-box\\farm-out has no %(id)s
# directory. pipeline/measured/queue-history.json was NOT consulted; it is days stale and has
# caused twelve duplicate filings.
"""

SHARED_BAR_TAIL = '''
  PRIMARY, leaf count out of 16: PASS is EXACTLY TWO leaves on the plant. FAIL-COUNT = three or
  more, or one. Control on this grid: 2 of 16.
  MECHANISM, node count out of 16, SCORED SEPARATELY because leaf count alone is how the
  control''s mechanism was misread the first time: how many leaf-bearing nodes the stem carries.
  Recorded whatever the primary does. The control''s clean cells showed exactly two opposed
  leaves at EVERY node with two or three nodes stacked up the stem, so this number is the one
  that says whether a subject-level wording collapsed the plant to a single node.
  SECONDARY, height relation out of 16, SCORED SEPARATELY so a count fix cannot silently break
  the half that is supposed to hold: the whole plant in frame and NO TALLER THAN THE GRASS AROUND
  IT. FAIL-SCALE = bush or waist height, overtopping the grass, or the founder''s 2026-08-16
  "dont make it double in size suddenly". Control on this grid: 0 of 16.
  ALSO FAIL, inherited unchanged: FAIL-COLOUR (a green, red, pale or white fruit, or more than
  one) and FAIL-PERSON (any face, figure, chibi or mascot -- the beat has no character in it).
  THE SUB-GRID IS DECLARED NOW AND NOT CHOSEN AFTERWARDS. The control''s correction established
  that rows r2 and r3 of this reference set come back as bush-sized purple fig masses while rows
  r0 and r1 are cleanly composed seedlings. Both readings are reported: the full 16, AND the
  r0/r1 eight-cell sub-grid. The DECISION RULE is settled on the FULL SIXTEEN; the sub-grid is
  published alongside as context and may NOT be substituted for it if the sixteen read badly.
  THE DECISION RULE, written before the frames exist so the read cannot be softened afterwards:
  this wording BINDS only if leaf count reaches 9 of 16 AND the height count does not fall below
  the control''s 0 of 16 on the same grid. 6 of 16 is the rate `exactly two` runs across the wave
  sheets, so anything at or under it is NO EFFECT. Between 7 and 8 of 16 is INDETERMINATE and
  licenses one repeat at fresh seeds on this same grid and nothing else. A height regression is a
  REGRESSION however the count reads. Scored AS WRITTEN and tightened FORWARD ONLY, never
  retroactively -- bending a bar after the picture is how 8/12 "passes" became 0/12 usable.
  THIS RUNG IS NOT SCORED AGAINST ITS SIBLING. `ep2-b01-stage-0817` and `ep2-b01-twoleaf-0817`
  render the same grid from the same control and are being run together, so it will be tempting
  to read one as the other''s control. THEY ARE NOT: each varies the subject in a different way
  and BOTH are measured against `authored_b01_geom_0817`. A between-rung comparison at n=16 with
  no shared variable is not a result and is refused in advance.
  NOT A PICK and NOT A TASTE CALL: which of the sixteen, if any, ships is R4''s and this job makes
  no such claim. Measurement is the lane''s; taste is the founder''s.'''

RUNGS = {
    "ep2-b01-stage-0817": {
        "token": "stage",
        "header": "# ep2-b01-stage-0817 -- 2026-08-17, DEVELOPMENTAL-STAGE rung. $0, local card, no provider.\n"
                  "# ONE RUNG, ONE VARIABLE, against a control that has already been rendered AND SCORED.\n",
        "key": "authored_b01_stage_0817",
        "consumer": (
            'The count-control question on the plant beats. This rung is the discriminator that the node '
            'rung`s own pre-registered bar named as its follow-up BEFORE that rung rendered, so it is not '
            'a lever chosen after seeing a result. The chain: `exactly two` ran 0 of 16 on this arm; the '
            'geometry clause bound but described A NODE and left node count free, returning four to six '
            'leaves; the node rung asserts `one node` and is therefore still a numeral on an arm where '
            'numerals do not reach the conditioning. THIS is the wording that constrains the count without '
            'asserting any number at all -- a newly sprouted seedling has one node and one pair of leaves '
            'by botany. Named before any pixel is drawn, per the no-work-without-a-consumer rule. STATED '
            'HONESTLY AS THE SMALLER CONSUMER IT IS: composite-then-inpaint at 0.30 already delivers exact '
            'two-leaf count 8 of 8 with zero GPU spent on the count, so count is SOLVED wherever a '
            'composited init can be built. What this rung buys is the case that route does not cover -- a '
            'plate generated fresh, where a prompt that yields a correct-count init removes the '
            'compositing step entirely.'),
        "why": (
            'THE ONE VARIABLE IS A PURE ADDITION TO THE SUBJECT, which is what makes it provable rather '
            'than asserted: `A tiny fig seedling in an open grassy field` becomes `A tiny newly sprouted '
            'fig seedling in an open grassy field`. THE LEAF CLAUSE IS UNTOUCHED -- `wide oval cotyledon '
            'leaves opposed one either side of the stem` survives character for character -- and that is '
            'precisely what makes this independent of `ep2-b01-nodecount-0817` rather than a second guess '
            'at it: that rung varies the leaf clause and this one does not touch it. Everything else is '
            'byte-identical: the purple fig clauses, `green at its neck`, the scale relation, the style '
            'tail, the reference set, the arm, the seeds, and the ENTIRE negative including `no three '
            'leaves, no four leaves, no many leaves`. Those negatives STAY; removing them would be a '
            'second variable. pipeline/insert_b01_round2_0817.py proves the single variable MECHANICALLY: '
            'it builds the draft by one substring substitution, refuses unless the length delta is exactly '
            'that substitution, asserts the leaf clause survived, then RE-PARSES the file and refuses '
            'unless the new value matches and the control is still byte-identical. A matching byte delta '
            'is not proof of a correct edit; the parsed comparison is. '
            'WHY THIS IS THE MOST PROMISING WORDING ON THE BOARD, and the reasoning is the repo`s own '
            'evidence rather than a hunch: numerals barely reach the conditioning -- CLIP`s text '
            'embeddings are near-identical across them (T2ICountBench, arXiv 2503.06884; full read in '
            'pipeline/research/count-control-sdxl-0817.md) -- while the one thing that HAS bound on this '
            'beat is a continuous adjective, the height relation. Stage adjectives are that class. '
            'REJECTED SIBLINGS, MEASURED NOT GUESSED: `just sprouted` (76/77 clean) and `a few days old` '
            '(76/77 clean) are paraphrases of this wording and firing all three would spend the card to '
            'learn one thing once. '
            'COLOUR: nothing green is propagated. PURPLE HELD 16 OF 16 on the control and both clauses are '
            'inherited byte-identical. `cotyledon` is kept deliberately: canon subject '
            '`sapling-cotyledon-shape` says the "average leaves" ruling is "about shape, not about '
            'vocabulary or scale" and names `wide oval cotyledon leaves` compliant, so removing it would '
            'be an unauthorised second variable. '
            'IS NOT: a mask rung, a composite rung, or a pick. $0, local card, no provider.'),
        "bar_head": (
            'PRE-REGISTERED IN THIS COMMIT, BEFORE ANY FRAME OF THIS RUNG EXISTS, and carried forward from '
            'the control`s own bar rather than rewritten. Sixteen stills at 832x1216 (4 reference cells x 4 '
            'seeds) -- the control`s grid exactly, because a count result needs a denominator and the '
            'comparison is only real on the same grid. '
            'FAILURE IS REACHABLE AND IS NOT A FORMALITY HERE: the control scored 2 of 16 on this exact '
            'grid, and `newly sprouted` may simply read as SMALL -- which this draft already says twice '
            '(`tiny`, and `no taller than the grass around it`) -- in which case it adds nothing and '
            'nothing moves. `whole plant in frame` also keeps the whole stem in shot, so a second node can '
            'appear and be counted against this.'),
    },
    "ep2-b01-twoleaf-0817": {
        "token": "twoleaf",
        "header": "# ep2-b01-twoleaf-0817 -- 2026-08-17, ATTRIBUTIVE-COMPOUND rung. $0, local card, no provider.\n"
                  "# ONE RUNG, ONE VARIABLE, against a control that has already been rendered AND SCORED.\n",
        "key": "authored_b01_twoleaf_0817",
        "consumer": (
            'The count-control question on the plant beats, approached by the one lexical route nothing on '
            'this arm has tried. Every count wording measured here so far quantifies a head noun -- '
            '`exactly two wide oval cotyledon leaves` -- and all of them null. This asks whether an '
            'ATTRIBUTIVE COMPOUND behaves differently. It matters out of proportion to its size because IF '
            'IT BINDS IT IS THE CHEAPEST FIX ON THE BOARD: beat 01`s approved script line already reads "A '
            'tiny TWO-LEAF banyan sapling in a green field", so the wording needs no new canon, no founder '
            'ruling and no compositing step -- it is already the text of the show. Named before any pixel '
            'is drawn, per the no-work-without-a-consumer rule. Composite-then-inpaint already solves count '
            '8 of 8 where an init can be composited; what this buys is the fresh-plate case, and it is '
            'stated as the smaller consumer it is.'),
        "why": (
            'THE ONE VARIABLE IS A PURE ADDITION TO THE SUBJECT: `A tiny fig seedling in an open grassy '
            'field` becomes `A tiny two-leaf fig seedling in an open grassy field`. THE LEAF CLAUSE IS '
            'UNTOUCHED -- `wide oval cotyledon leaves opposed one either side of the stem` survives '
            'character for character -- which is what makes this independent of '
            '`ep2-b01-nodecount-0817`. Everything else is byte-identical: the purple fig clauses, `green at '
            'its neck`, the scale relation, the style tail, the reference set, the arm, the seeds, and the '
            'ENTIRE negative including `no three leaves, no four leaves, no many leaves`. Those negatives '
            'STAY; removing them would be a second variable. The single variable is proved MECHANICALLY by '
            'pipeline/insert_b01_round2_0817.py, which re-parses the file and refuses unless the leaf '
            'clause survived and the control is still byte-identical. '
            'THIS IS THE APPROVED SCRIPT`S OWN WORDING AND NOT AN INVENTION: beat 01`s script line, '
            'node.md verbatim, reads "A tiny two-leaf banyan sapling in a green field". '
            'THE OBVIOUS OBJECTION IS MET HEAD ON AND NOT DODGED. `two-leaf` looks like `exactly two` in a '
            'hyphen, and `a pair of ...` was rejected on this arm for being "another lexical route to a '
            'cardinality". That reasoning holds for any wording whose JOB IS TO STATE A TOTAL. It does not '
            'settle whether an attributive compound behaves like one: `exactly two ... leaves` is a '
            'numeral quantifying a head noun, while `two-leaf` is a hyphenated modifier of THE PLANT -- a '
            'property of the seedling, not a count of objects in the frame -- and it tokenises and attends '
            'differently. That distinction is the whole content of this rung, and it is a question about '
            'the tokeniser and the conditioning, which only pixels can answer. '
            'THE PREDICTION IS PRE-REGISTERED AND IT IS PESSIMISTIC: if the tokeniser splits `two-leaf` '
            'into `two` and `leaf`, this rung IS `exactly two` wearing a hyphen and will null exactly like '
            'it did, 0 of 16. That is written down BEFORE the frames exist rather than offered afterwards '
            'as an explanation for a null. '
            'COLOUR: nothing green is propagated; PURPLE HELD 16 OF 16 on the control and both clauses are '
            'inherited byte-identical. `cotyledon` is kept for the reason recorded in the sibling spec: '
            'canon calls the "average leaves" ruling one about shape, not vocabulary. '
            'IS NOT: a mask rung, a composite rung, or a pick. $0, local card, no provider.'),
        "bar_head": (
            'PRE-REGISTERED IN THIS COMMIT, BEFORE ANY FRAME OF THIS RUNG EXISTS, and carried forward from '
            'the control`s own bar rather than rewritten. Sixteen stills at 832x1216 (4 reference cells x 4 '
            'seeds) -- the control`s grid exactly. '
            'FAILURE IS REACHABLE AND IS THE STRONGLY PREDICTED OUTCOME: three count-bearing wordings have '
            'now scored 0 to 2 of 16 on this arm, and this one may be a fourth. `whole plant in frame` '
            'keeps the whole stem in shot, so a second node further up can appear and be counted against '
            'this.'),
    },
}

CARRY = ("node", "beat", "runner", "needs_gpu", "priority", "max_attempts", "est_minutes",
         "script_authority", "script_line", "needs", "env", "steps", "artifacts")


def retoken(obj, old, new):
    if isinstance(obj, str):
        return obj.replace(old, new)
    if isinstance(obj, list):
        return [retoken(v, old, new) for v in obj]
    if isinstance(obj, dict):
        return {k: retoken(v, old, new) for k, v in obj.items()}
    return obj


def main() -> None:
    with open(SRC, encoding="utf-8") as fh:
        src = yaml.safe_load(fh)

    for job_id, spec in RUNGS.items():
        path = "pipeline/jobs/%s.yaml" % job_id
        if os.path.exists(path):
            sys.exit("!! %s already exists. Refusing to overwrite." % path)

        out = copy.deepcopy(src)
        # Every path, out-dir, farm-out dir, manifest name and draft key at once.
        out = retoken(out, "nodecount", spec["token"])
        out["id"] = job_id
        out["task"] = job_id
        out["owner"] = ("count-control lane, 2026-08-17 -- filed to backlog the moment it "
                        "dry-ran clean")
        out["consumer"] = spec["consumer"]
        out["why"] = spec["why"]
        out["success"] = spec["bar_head"] + SHARED_BAR_TAIL

        # REFUSE IF ANYTHING THAT MUST BE CARRIED HAS MOVED. This is the check
        # that makes "copied, not retyped" true rather than intended.
        for k in CARRY:
            want = retoken(copy.deepcopy(src[k]), "nodecount", spec["token"])
            if out[k] != want:
                sys.exit("!! %s: carried field %r does not match the source. Refusing." % (job_id, k))
        blob = yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=110)
        if spec["key"] not in blob:
            sys.exit("!! %s: draft key %s never made it into the spec. Refusing."
                     % (job_id, spec["key"]))
        # A stray `nodecount` in a PATH, a draft key or an argv would render the
        # wrong wording into the wrong directory, so those are checked. The prose
        # fields are exempt because they CITE the sibling rung by id on purpose --
        # `why` says which job this one is independent of, and that reference is
        # the point rather than a leak.
        machine = {k: v for k, v in out.items() if k not in ("consumer", "why", "success")}
        leaked = yaml.safe_dump(machine, sort_keys=False, allow_unicode=True)
        if "nodecount" in leaked:
            sys.exit("!! %s: a `nodecount` reference survived retokening OUTSIDE the prose. "
                     "Refusing." % job_id)
        for field in ("consumer", "why", "success"):
            if "b01-nodecount" in out[field] and "independent" not in out[field] \
                    and "not scored against its sibling" not in out[field].lower():
                sys.exit("!! %s: %s names the node rung without saying how it relates to it."
                         % (job_id, field))

        header = spec["header"] + MEASURED % {"key": spec["key"], "id": job_id}
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(header + blob)

        back = yaml.safe_load(open(path, encoding="utf-8"))
        if back != out:
            sys.exit("!! %s: does not round-trip. Refusing to leave it on disk." % path)
        print("wrote %s  (draft %s, %d steps, no allow_fail: %s)"
              % (path, spec["key"], len(back["steps"]),
                 not any(s.get("allow_fail") for s in back["steps"])))


if __name__ == "__main__":
    main()
