#!/usr/bin/env python3
"""Insert `authored_b07_scavcostume_0819` into pipeline/wave-drafts.yaml — RUNG C
on beat 07, ONE VARIABLE: THE SCAVENGER GETS A GARMENT OF HIS OWN.

WHY THIS RUNG EXISTS, and it is not another attempt at the point.
==============================================================================
The point is SOLVED. `ep2-b07-point-motion-0819` and its crf-10 child both
passed beat 07's pre-registered motion bar tonight on the first attempt: the
guard raises HIS OWN arm and aims it at the goblin, all four clauses, with the
predicted text-to-image failure (the goblin points) silent. So no further plate
rung needs to contain a point, and this one does not try to improve it.

What those two verdicts left standing is the PLATE, and they narrowed its
blocker to one thing:

    THE SCAVENGER IS WEARING THE GUARD'S UNIFORM. r1-s3 dresses the goblin in
    the guard's own pale wrap tunic and wide white sash. Two men in one uniform
    read as two officials, and a CONFISCATE beat has to read as an authority
    pointing at a scavenger. It is the costume, not the acting, that keeps this
    footage out of a cut.

THE CAUSE IS NAMED IN THIS FILE ALREADY, one rung up. `authored_b07_twofig_0817`
sends the goblin as `a crouching goblin with green skin` — a noun phrase with
ONE attribute in it and NO GARMENT AT ALL. The only clothing terms in the whole
prompt are the guard's. This repo's own positive-placement law says what happens
next: *the positive places what you want; the negative does not* — four times on
this checkpoint a defect the negative forbade arrived because the positive left
it vague. The goblin's garment slot was left VACANT and the model filled it from
the nearest available wardrobe, which was the guard's.

So the fix is the same instrument rung B already proved on this exact beat:
bind the attribute INSIDE the goblin's own noun phrase with `with`/`in`. Rung B
did that for `green skin` and the green mitt disappeared. Rung C does it for the
garment.

WHY `patched tunic` AND NOT THE CANON `patchwork cloak` — this is measured, not
a preference.
==============================================================================
  * `faded green patchwork cloak` is the character's canon costume and it is
    DELIBERATELY GONE from the goblin beats. wave-drafts.yaml's own header:
    r8 dropped the em-dash character list and r8 is the round that came back
    green in 4 of 4, "an inherited decision, not a new one", and re-adding it is
    explicitly ANOTHER LANE'S CALL. This rung does not re-open it.
  * `patchwork cloak` also has a measured failure mode on this checkpoint: THE
    PATCHWORK CLIMBS ONTO HIS HEAD (`authored_b02_idfix_r2`'s note — a tan graft
    across the crown, X-stitches on the skull, stitch-scars on the cheeks, 4 of
    4 frames), and neutralising it costs two new negative terms.
  * `in a patched tunic` is the garment noun this beat's own two-shot family
    already uses for this character (`authored_staged`, `authored_b08_idfix_r2`)
    and beat 08 — which sends it — is recorded as "the only goblin beat whose
    skulls are clean in 4/4". It differentiates the garment by the word
    `patched` and needs NO new negative term, so the negative stays byte for
    byte and the rung stays at one variable.

MEASURED ON THE REAL CLIP BEFORE THIS SCRIPT EXISTED, offline, $0, through
`render_wave_goblin.check()` — the same function the box dry step calls — on the
m1pro venv (transformers 4.44.2, openai/clip-vit-large-patch14 from cache):

    parent rung B    65/77 pos   58/77 neg   tag 1boy   anchor PRESENT   0 faults
    RUNG C           70/77 pos   58/77 neg   tag 1boy   anchor PRESENT   0 faults

The parent reproducing its recorded 65/77 exactly is the control that makes the
70 mean something. +5 tokens, 7 under budget, NOTHING DROPPED (no
POSITIVE DROPPED fault, which is the real risk when adding tokens — the
compressor drops whole trailing segments and would have taken the style anchor
with them). The count tag still derives `1boy` from the untouched first clause,
so beat 7's `tag:` is NOT edited and no sibling draft in this block faults.

WHAT THIS RUNG DOES NOT TOUCH, named so a reader does not expect it:
  * THE GOBLIN'S EYEWEAR. r1-s3 gives him round red wire-rims — the guard's
    glasses reaching the wrong face, measured at 5 of 12. Same bleed, different
    attribute, and fixing both at once would make this two variables. If the
    garment binds and the glasses still bleed, that is rung D and it is a
    one-word edit.
  * THE WHITE SASH. Whether a garment of his own displaces the guard's sash too
    is exactly what this rung MEASURES; it is not asserted, and a sash-denial in
    the negative would be the weak channel anyway.
  * the guard's cast run (byte-identical and still leading the prompt), the
    grammar fix, the world tail, the style anchor, the negative, `tag`,
    goblin_ipa_sample.py, and every other draft in the file.

RIGOUR. wave-drafts.yaml is ~450 KB of hand-written provenance with ~30 live
peers in it, so it is edited as TEXT, following `insert_b07_nobald_0817.py`:
anchor matched exactly once, sha256 before and after, byte delta asserted equal
to the payload, and a PARSED-VARIANT DIFF proving exactly ONE key was added,
that no key anywhere was removed or altered (`tag` included), and that the
round-tripped value is BYTE-IDENTICAL to the string that was measured. A byte
delta that matches is NOT proof on its own: an insertion INSIDE a folded scalar
has a perfect delta, and only the parse-back catches it. `yaml.safe_load` is
used only to compare, never to write.

ONE DEVIATION FROM THE PRECEDENT, stated: the backup is written OUTSIDE the
repo. The precedent drops `wave-drafts.yaml.bak-...` next to the target, and the
tree already carries several stray `.bak-*` files from that habit.

$0. No GPU, no provider, no network beyond a local model cache.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "pipeline" / "wave-drafts.yaml"

BEAT = 7
KEY = "authored_b07_scavcostume_0819"
PARENT_KEY = "authored_b07_twofig_0817"

# THE ONE EDIT, as a substitution rather than a retyped string, so "one
# variable" is checkable and not asserted. The parent value is read from the
# file at run time -- nothing here retypes it.
FROM = "a crouching goblin with green skin"
TO = "a crouching goblin with green skin in a patched tunic"

# Measured above. Asserted against the built value so the numbers in this
# docstring cannot drift away from the string that ships.
MEASURED_POS_TOK = 70

COMMENT = """\
    # ── `authored_b07_scavcostume_0819` — 2026-08-19, the beat-07 judging lane.
    # RUNG C: THE SCAVENGER GETS A GARMENT OF HIS OWN. One variable against rung B
    # (`authored_b07_twofig_0817`), which is left standing and is the only thing this
    # should be read against.
    # THE POINT IS NOT WHAT THIS RUNG IS FOR. It was settled tonight in MOTION, not in
    # a still: ep2-b07-point-motion-0819 and its crf-10 child both passed beat 07's
    # pre-registered bar on the first attempt -- the guard raises his own arm and aims
    # it at the goblin, and the predicted "the goblin points" failure never fired. No
    # plate rung needs to carry a point any more, and this one does not try to.
    # WHAT IT IS FOR is the one thing those verdicts left between beat 07 and a cut:
    # r1-s3 dresses the SCAVENGER IN THE GUARD'S OWN pale wrap tunic and white sash.
    # Two men in one uniform read as two officials; a CONFISCATE beat has to read as
    # an authority pointing at a scavenger.
    # THE CAUSE IS RUNG B'S OWN GRAMMAR LAW, one line up in this file. Rung B sends
    # `a crouching goblin with green skin` -- a noun phrase with ONE attribute and NO
    # GARMENT. The only clothing terms in the prompt are the guard's, so the goblin's
    # garment slot was VACANT and the model filled it from the nearest wardrobe. That
    # is the positive-placement law exactly: the positive places what you want. Rung B
    # bound `green skin` inside his own noun phrase and the green mitt disappeared;
    # this binds the garment the same way, with the same word class.
    # `patched tunic` AND NOT THE CANON `patchwork cloak`, for two measured reasons:
    #   * the em-dash list (`faded green patchwork cloak`) is GONE from the goblin
    #     beats by r8's inherited decision -- this file's own header says re-adding it
    #     is another lane's call, and this rung does not re-open it;
    #   * `patchwork cloak` CLIMBS ONTO HIS HEAD on this checkpoint -- see
    #     `authored_b02_idfix_r2` above, 4 of 4 frames stitching the cloak into the
    #     skull -- and suppressing that costs two new negative terms, i.e. a second
    #     variable. `patched tunic` is what beat 08 sends, and beat 08 is the only
    #     goblin beat recorded with clean skulls 4/4.
    # NOT ADDRESSED, ON PURPOSE: the goblin's round RED wire-rims (the guard's
    # glasses reaching the wrong face, measured 5 of 12 on this beat) and the white
    # sash. Same bleed, different attributes; fixing them here would be two more
    # variables. If the garment binds and those persist, that is rung D.
    # REAL CLIP via render_wave_goblin.check(), offline on the m1pro venv: 70/77 pos,
    # 58/77 neg (byte-identical recipe), anchor PRESENT, count `1boy` == declared
    # `1boy`, ZERO FAULTS, nothing dropped. The parent measured in the same run at its
    # recorded 65/77, which is the control. +5 tokens, 7 under budget.
    # TOKEN TRADE: NONE. No word was cut to pay for it and the style tail is intact,
    # so there are no traded words to name as first suspects.
"""

# Anchor: THE BEAT-8 HEADER, the line that closes beat 07's block. Anchoring on
# the tail of a preceding draft is the documented trap -- it lands the insertion
# INSIDE a folded scalar with a byte delta that matches perfectly.
ANCHOR = """  8:
    slug: inside-him
"""


def build_block(comment: str, key: str, draft: str) -> str:
    body = textwrap.fill(draft, width=76,
                         initial_indent="      ", subsequent_indent="      ",
                         break_long_words=False, break_on_hyphens=False)
    return "%s    %s: >-\n%s\n" % (comment, key, body)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backup-dir", default=os.environ.get("TMPDIR", "/tmp"),
                    help="where the pre-edit copy goes; NOT the repo")
    a = ap.parse_args()

    import yaml  # compare only; never used to write this file

    before_txt = TARGET.read_text(encoding="utf-8")
    print("sha256 before      %s  (%d bytes)"
          % (sha(before_txt), len(before_txt.encode())))

    before = yaml.safe_load(before_txt)
    parent = before["beats"][BEAT][PARENT_KEY]

    # ---- THE ONE VARIABLE, derived rather than retyped ----------------------
    if parent.count(FROM) != 1:
        sys.exit("!! %r appears %d times in the parent, expected exactly 1. "
                 "Refusing to guess which one." % (FROM, parent.count(FROM)))
    draft = parent.replace(FROM, TO, 1)
    if draft == parent:
        sys.exit("!! the edit did not apply. Refusing.")
    # Everything either side of the substitution must be untouched.
    if draft.replace(TO, FROM, 1) != parent:
        sys.exit("!! the child does not reduce back to the parent -- more than "
                 "one thing moved. Refusing.")
    print("one variable       parent + %r, and nothing else"
          % TO[len(FROM):].strip())
    for bad in ("bald", "{{GOBLIN}}", "patchwork", "cloak"):
        if bad in draft:
            sys.exit("!! the child contains %r. Refusing." % bad)
    print("guards             no 'bald', no goblin slot, no retired em-dash "
          "costume terms")

    if KEY in before_txt:
        sys.exit("!! %s is ALREADY present. Refusing to double-insert." % KEY)
    n = before_txt.count(ANCHOR)
    if n != 1:
        sys.exit("!! anchor matches %d times, expected exactly 1. Refusing to "
                 "guess." % n)

    block = build_block(COMMENT, KEY, draft)
    after_txt = before_txt.replace(ANCHOR, block + ANCHOR, 1)

    delta = len(after_txt.encode()) - len(before_txt.encode())
    payload = len(block.encode())
    print("payload bytes      %d" % payload)
    print("byte delta         %d   (expected %d)" % (delta, payload))
    if delta != payload:
        sys.exit("!! byte delta != payload -- NOT a pure insertion. Refusing.")

    after = yaml.safe_load(after_txt)

    # ---- PARSED-VARIANT DIFF ------------------------------------------------
    # The byte delta above cannot tell an insertion BETWEEN two scalars from an
    # insertion INTO one. This can.
    if set(before) != set(after):
        sys.exit("!! top-level keys changed. Refusing.")
    for k in before:
        if k != "beats" and before[k] != after[k]:
            sys.exit("!! top-level %r changed. Refusing." % k)
    if set(before["beats"]) != set(after["beats"]):
        sys.exit("!! the set of beats changed. Refusing.")
    for b in sorted(before["beats"], key=str):
        bb, aa = before["beats"][b], after["beats"][b]
        rem = set(bb) - set(aa)
        add = set(aa) - set(bb)
        if rem:
            sys.exit("!! beat %s LOST keys %s. Refusing." % (b, sorted(rem)))
        if b == BEAT:
            if add != {KEY}:
                sys.exit("!! beat %s additions were %s, expected exactly %s."
                         % (BEAT, sorted(add), [KEY]))
            for k in bb:
                if bb[k] != aa[k]:
                    sys.exit("!! beat %s key %r was MODIFIED. Refusing."
                             % (BEAT, k))
            print("beat %d added       %s" % (BEAT, sorted(add)))
            print("beat %d existing    all %d keys byte-identical (tag, and "
                  "rung B, included)" % (BEAT, len(bb)))
        elif add or bb != aa:
            sys.exit("!! beat %s changed and must not have (added %s)."
                     % (b, sorted(add)))
    if after["beats"][BEAT]["tag"] != "1boy":
        sys.exit("!! beat %d tag is no longer '1boy'. Refusing -- editing it "
                 "would fault every sibling draft in this block." % BEAT)
    print("beat %d tag         %r  (UNCHANGED)"
          % (BEAT, after["beats"][BEAT]["tag"]))

    if after["beats"][BEAT][KEY] != draft:
        print("!! ROUND-TRIP MISMATCH -- the folded block does not equal the "
              "measured string.\n   expected: %r\n   got:      %r"
              % (draft, after["beats"][BEAT][KEY]))
        return 3
    print("round-trip         value BYTE-IDENTICAL to the measured string")

    # ---- THE MEASUREMENT, RE-RUN ON THE STRING THAT SHIPS -------------------
    # The docstring's 70/77 is only trustworthy if it is the number for THIS
    # value. Skipped, loudly, when no CLIP tokenizer is available -- an
    # estimate here would be fiction and this file says so.
    sys.path.insert(0, str(REPO / "pipeline"))
    try:
        import sd_prompt as sd
        import render_wave_goblin as wg
        if sd._clip_tokenizer() is None:
            raise ImportError("no CLIP tokenizer")
    except Exception as exc:                                  # noqa: BLE001
        print("clip check         SKIPPED (%s). Run this script under the "
              "venv that has transformers + openai/clip-vit-large-patch14 to "
              "measure; the recorded number is %d/77."
              % (exc, MEASURED_POS_TOK))
    else:
        row = wg.check(BEAT, after["beats"][BEAT], draft, sd, verbose=False)
        print("clip check         %d/77 pos, %d/77 neg, tag %r, faults %s"
              % (row["pos_tok"], row["neg_tok"], row["tag"], row["faults"]))
        if row["faults"]:
            sys.exit("!! the shipped string has faults. Refusing.")
        if row["pos_tok"] != MEASURED_POS_TOK:
            sys.exit("!! measured %d/77, this file claims %d/77. Refusing to "
                     "ship a string whose recorded number is wrong."
                     % (row["pos_tok"], MEASURED_POS_TOK))

    if not a.apply:
        print("\n--check only: nothing written. Re-run with --apply.")
        return 0

    bak = Path(a.backup_dir) / (TARGET.name + ".bak-b07-scavcostume-0819")
    shutil.copy2(TARGET, bak)
    TARGET.write_text(after_txt, encoding="utf-8")
    print("\nbackup             %s  (outside the repo, on purpose)" % bak)
    print("sha256 after       %s  (%d bytes, +%d)"
          % (sha(after_txt), len(after_txt.encode()), delta))
    return 0


if __name__ == "__main__":
    sys.exit(main())
