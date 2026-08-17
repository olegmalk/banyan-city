#!/usr/bin/env python3
"""Add beat 08's NO-BALD draft to wave-drafts.yaml. ONE KEY, PURELY ADDITIVE.

    python3 pipeline/insert_b08_nobald_0817.py            # check, writes nothing
    python3 pipeline/insert_b08_nobald_0817.py --apply

THE DEFECT, AND IT IS NOT WHERE IT WAS REPORTED. `ep2-b08-cast-0817` was filed to
remove `bald` from the guard plates and it still sent `bald head`. It is not a
literal in the draft: `authored_b08_cast_0817` carries the `{{GOBLIN}}` slot, and
`goblin_ipa_sample.py` fills that slot from its own constant --
`GOBLIN_DEF = "green skin, bald head"` (line 65). So the string the model saw was

    2boys, two men, ... the far one a goblin, green skin, bald head, patched
    cloak, looks at his belly, ...

and `bald head` arrived through the slot, in the goblin's own clause.

WHY THAT MATTERS AND WHY b06 IS CLEAN. b06 renders 12 of 12 HAIRED off the same
refs, sampler, model and day; b07 and b08 went 12 of 12 BALD. The mechanical
difference is one thing only: `authored_b06_cast_0817` carries NO `{{GOBLIN}}`
marker, so no goblin definition is substituted into it and the word `bald` never
enters its prompt. b07 and b08 are the only two cast drafts that carry the slot.
That is the whole of the b06-vs-b07/08 contrast, and it means the scoring lane's
law is right: `bald` is BROADCAST-CLASS. Scoping it inside the goblin's own clause
did not contain it -- this draft's own predecessor is the proof, since `green skin,
bald head, patched cloak` is as tightly scoped to the goblin as prose gets and the
GUARD came back bald 12 times out of 12.

WHY `GOBLIN_DEF` IS NOT TOUCHED, which is the whole reason this is a draft edit.
Two founder rulings collide here. `bald` for the GOBLIN is his own ruling of
2026-08-12 ("you're right, he should be bald"), recorded in the sampler's comment
at line 62. `bald` for the GUARDS is the defect he ordered fixed on 2026-08-16
("the guards beign bald is a bit strange.. why are you making everyone bald..?",
"the cast stands as drawn"). Editing `GOBLIN_DEF` would overturn the first ruling
to serve the second, on a SHARED sampler, for all eleven goblin beats at once.
So the slot comes out of THIS DRAFT and the constant is left exactly as it is:
goblin-only beats keep their bald goblin, and the two beats that put a guard and a
goblin in one frame stop broadcasting the token onto the man.

NO NEGATION IS ATTEMPTED, deliberately. The vacancy law says a negative does not
reach an empty region, and a broadcast-class attribute is a BINDING failure rather
than a presence failure, so `no bald` would spend tokens on a mechanism that has
already been measured not to work. The hair is NAMED instead (`light sandy hair`,
already in this draft and unchanged).

THE ONE VARIABLE. `{{GOBLIN}}` becomes the literal `green skin`. Nothing else in
the draft moves -- not a word, not a comma. The sent positive therefore differs
from `authored_b08_cast_0817`'s by exactly the eleven characters `, bald head`
deleted, which is what makes the rung attributable: if the guard comes back haired,
`bald` was the cause, and if he comes back bald, the token was never the mechanism.

MEASURED ON THE REAL CLIP, not the estimator. `render_wave_goblin.check()` through
the transformers `openai/clip-vit-large-patch14` tokenizer, offline:

    baseline authored_b08_cast_0817   74/77 pos   66/77 neg   0 faults
    THIS DRAFT                        71/77 pos   66/77 neg   0 faults

count tag `2boys` derived against a declared `2boys`, style anchor `very aesthetic`
PRESENT in both. THE TOKEN TRADE IS NONE: removing `bald head` frees 3 tokens and
this draft spends none of them. No word was cut, nothing was added to fill the
headroom, and the style tail is intact. There are therefore NO traded words to name
as suspects if the rung fails.

BEWARE THE ESTIMATOR. Without `transformers` importable, `sd_prompt._token_estimate`
falls back to a word-count approximation and reports THIS BEAT as 85/77 with two
faults (`STYLE ANCHOR MISSING`, `POSITIVE DROPPED: very aesthetic.`) -- because
`compress()` uses the same estimate for its own fitting loop and sheds the tail
that the real tokenizer keeps. Every number above is the real count. A lane
quoting token figures from a plain `python3` on this Mac is quoting fiction.

`tag: 2boys` IS DELIBERATELY UNTOUCHED, for the reason `insert_b08_cast_draft_0817.py`
measured: `count_tag()` reads the LEADING Danbooru tag of `compress()`'s output, so
`tag:` records the AUTHORING CONVENTION a beat's drafts open in and the count guard
is an internal consistency test between a draft and its beat. This draft opens
"Two men," exactly as its predecessor does, derives `2boys`, and matches. Forcing
any other value would fault all seven existing beat-08 drafts.

RIGOUR. ~350 KB of hand-written provenance with ~30 live peers in it, so it is
edited as TEXT: anchor matched exactly once, sha256 before and after, byte delta
asserted equal to the payload, backup written first, and a PARSED-VARIANT DIFF
proving exactly one key was added, that no key anywhere was removed or altered,
and that the round-tripped value of the new key is BYTE-IDENTICAL to the string
that was measured. A BYTE DELTA THAT MATCHES IS NOT PROOF: a peer's first anchor
would have written 26 lines INSIDE a folded scalar with a perfect delta and a sha
that moved exactly as predicted, and only the parse-back caught it. No YAML
round-trip is performed on the file; `yaml.safe_load` is used only to compare,
never to write.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "pipeline" / "wave-drafts.yaml"
SUFFIX = ".bak-b08-nobald-0817"

BEAT = 8
KEY = "authored_b08_nobald_0817"

# The EXACT string measured at 71/77, 0 faults. The written block is generated
# from this constant and then read back and compared to it, so a wrapping slip
# cannot change what gets sent to the renderer. Identical to
# `authored_b08_cast_0817` except that `{{GOBLIN}}` is replaced by `green skin`.
DRAFT = (
    "Two men, the near one light sandy hair, cream shirt, white sash, brown "
    "skirt, holds a bark clipboard in both hands, the far one a goblin, green "
    "skin, patched cloak, looks at his belly, arms down, tall grass, pale sky "
    "above, cinematic lighting, masterpiece, best quality, very aesthetic No "
    "girl, no child, no armor, no helmet, no knight, no white background, no "
    "plain background, no dark, no night. No photorealism, no 3D render look. "
    "9:16 vertical, no text."
)

# What the predecessor actually SENT, kept here so the one variable is checkable
# rather than asserted. DRAFT must differ from this by exactly ", bald head".
PREDECESSOR_SENT = (
    "Two men, the near one light sandy hair, cream shirt, white sash, brown "
    "skirt, holds a bark clipboard in both hands, the far one a goblin, green "
    "skin, bald head, patched cloak, looks at his belly, arms down, tall grass, "
    "pale sky above, cinematic lighting, masterpiece, best quality, very "
    "aesthetic No girl, no child, no armor, no helmet, no knight, no white "
    "background, no plain background, no dark, no night. No photorealism, no "
    "3D render look. 9:16 vertical, no text."
)

COMMENT = """\
    # ── `authored_b08_nobald_0817` — 2026-08-17. `bald` REMOVED, ONE VARIABLE.
    # `authored_b08_cast_0817` above existed to take `bald` off the guards and it
    # still SENT `bald head`, because the token is not a literal in it: the
    # `{{GOBLIN}}` slot is filled by goblin_ipa_sample.py's own
    # `GOBLIN_DEF = "green skin, bald head"`. b07 carries the slot too; b06 does
    # NOT, and b06 is the beat that came back 12 of 12 HAIRED off the same refs,
    # sampler, model and day while b07 and b08 went 12 of 12 BALD. One mechanical
    # difference, and it is this slot.
    # So `bald` is BROADCAST-CLASS, exactly like eyewear: scoping it inside the
    # goblin's own clause does not contain it. `green skin, bald head, patched
    # cloak` is as tightly bound to the goblin as prose gets and the GUARD still
    # went bald 12 of 12. This draft therefore REMOVES the token rather than
    # re-scoping it, and attempts NO negation — the vacancy law says a negative
    # does not reach an empty region, and a broadcast attribute is a BINDING
    # failure, not a presence failure. The hair is named instead, unchanged.
    # `GOBLIN_DEF` IS NOT TOUCHED and must not be: bald FOR THE GOBLIN is the
    # founder's own 2026-08-12 ruling, and the sampler is shared by eleven goblin
    # beats. Only the two beats that put a guard and a goblin in one frame drop
    # the slot; goblin-only beats keep his bald skull.
    # ONE VARIABLE, exactly: `{{GOBLIN}}` -> `green skin`. The sent positive
    # differs from its predecessor's by the eleven characters `, bald head` and
    # nothing else — no word moved, no comma moved.
    # `tag: 2boys` DELIBERATELY UNTOUCHED. It opens "Two men," as its predecessor
    # does and derives `2boys`; count_tag() reads the leading tag, so `tag:` is the
    # authoring convention, and forcing another value faults all seven beat-08
    # drafts.
    # REAL CLIP via render_wave_goblin.check() (transformers, clip-vit-large-patch14,
    # offline): 71/77 pos, 66/77 neg, anchor `very aesthetic` PRESENT, count `2boys`
    # == declared `2boys`, ZERO FAULTS. Baseline was 74/77 / 66/77 / 0 faults.
    # TOKEN TRADE: NONE. 3 tokens freed and none spent — nothing cut, nothing added
    # to fill the headroom, style tail intact. No traded words to suspect.
    # The plain-python3 ESTIMATOR reads this draft as 85/77 with two faults. That is
    # fiction: without transformers, compress() sheds the tail the real tokenizer
    # keeps. Measure through the venv or do not quote a number.
"""

# Anchor: THE BEAT-9 HEADER, the line that closes beat 08's block. Anchoring on
# the tail of a preceding draft is the documented trap -- it lands the insertion
# INSIDE a folded scalar, with a byte delta that matches perfectly. The next
# beat's header sits after the blank line that already terminates beat 08's last
# draft. Matched exactly once (asserted below, not assumed).
ANCHOR = """  9:
    slug: the-pause
"""


def build_block() -> str:
    body = textwrap.fill(DRAFT, width=76,
                         initial_indent="      ", subsequent_indent="      ",
                         break_long_words=False, break_on_hyphens=False)
    return "%s    %s: >-\n%s\n" % (COMMENT, KEY, body)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    import yaml  # compare only; never used to write this file

    # THE ONE VARIABLE, checked rather than claimed.
    if PREDECESSOR_SENT.replace(", bald head", "", 1) != DRAFT:
        sys.exit("!! DRAFT is not the predecessor minus ', bald head' -- more "
                 "than one variable moved. Refusing.")
    print("one variable       DRAFT == predecessor-sent minus ', bald head'")

    before_txt = TARGET.read_text(encoding="utf-8")
    print("sha256 before      %s  (%d bytes)"
          % (sha(before_txt), len(before_txt.encode())))

    if KEY in before_txt:
        sys.exit("!! %s is ALREADY present. Refusing to double-insert." % KEY)
    n = before_txt.count(ANCHOR)
    if n != 1:
        sys.exit("!! anchor matches %d times, expected exactly 1. Refusing to "
                 "guess." % n)

    block = build_block()
    after_txt = before_txt.replace(ANCHOR, block + ANCHOR, 1)

    delta = len(after_txt.encode()) - len(before_txt.encode())
    payload = len(block.encode())
    print("payload bytes      %d" % payload)
    print("byte delta         %d   (expected %d)" % (delta, payload))
    if delta != payload:
        sys.exit("!! byte delta != payload -- NOT a pure insertion. Refusing.")

    before = yaml.safe_load(before_txt)
    after = yaml.safe_load(after_txt)

    # ---- PARSED-VARIANT DIFF -------------------------------------------------
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
        add = set(aa) - set(bb)
        rem = set(bb) - set(aa)
        if rem:
            sys.exit("!! beat %s LOST keys %s. Refusing." % (b, sorted(rem)))
        if b == BEAT:
            if add != {KEY}:
                sys.exit("!! beat %s additions were %s, expected exactly {%s}."
                         % (BEAT, sorted(add), KEY))
            for k in bb:
                if bb[k] != aa[k]:
                    sys.exit("!! beat %s key %r was MODIFIED. Refusing."
                             % (BEAT, k))
            print("beat %d added       [%r]" % (BEAT, KEY))
            print("beat %d existing    all %d keys byte-identical (tag included)"
                  % (BEAT, len(bb)))
        else:
            if add or bb != aa:
                sys.exit("!! beat %s changed and must not have (added %s)."
                         % (b, sorted(add)))
    if after["beats"][BEAT]["tag"] != "2boys":
        sys.exit("!! beat %d tag is no longer '2boys'. Refusing." % BEAT)
    print("beat %d tag         %r  (UNCHANGED, as intended)"
          % (BEAT, after["beats"][BEAT]["tag"]))

    # GOBLIN_DEF must be exactly what it was. This script's whole argument is that
    # the shared sampler is not edited, so it asserts that rather than trusting it.
    samp = (REPO / "pipeline" / "goblin_ipa_sample.py").read_text(encoding="utf-8")
    if 'GOBLIN_DEF = "green skin, bald head"' not in samp:
        sys.exit("!! goblin_ipa_sample.py GOBLIN_DEF is not the 2026-08-12 "
                 "founder ruling any more. Refusing -- this script assumes it is "
                 "untouched.")
    print("GOBLIN_DEF         untouched (founder's 2026-08-12 goblin ruling intact)")

    # The round-tripped value must be exactly the string that was measured.
    got = after["beats"][BEAT][KEY]
    if got != DRAFT:
        print("!! ROUND-TRIP MISMATCH -- the folded block does not equal the "
              "measured string.\n   expected: %r\n   got:      %r" % (DRAFT, got))
        return 3
    print("round-trip         value is BYTE-IDENTICAL to the measured string")
    if "bald" in got:
        sys.exit("!! the written draft still contains 'bald'. Refusing.")
    if "{{GOBLIN}}" in got:
        sys.exit("!! the written draft still carries the goblin slot, which the "
                 "sampler would fill with 'bald head'. Refusing.")
    print("no-bald            'bald' absent and the {{GOBLIN}} slot is gone")

    if not a.apply:
        print("\n--check only: nothing written. Re-run with --apply.")
        return 0

    shutil.copy2(TARGET, TARGET.with_name(TARGET.name + SUFFIX))
    TARGET.write_text(after_txt, encoding="utf-8")
    print("\nbackup             %s" % (TARGET.name + SUFFIX))
    print("sha256 after       %s  (%d bytes, +%d)"
          % (sha(after_txt), len(after_txt.encode()), delta))
    return 0


if __name__ == "__main__":
    sys.exit(main())
