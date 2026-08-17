#!/usr/bin/env python3
"""Add beat 08's CAST-CORRECT draft to wave-drafts.yaml. ONE KEY, PURELY ADDITIVE.

    python3 pipeline/insert_b08_cast_draft_0817.py            # check, writes nothing
    python3 pipeline/insert_b08_cast_draft_0817.py --apply

WHY NO `tag:` EDIT, WHICH IS THE WHOLE POINT OF THIS SCRIPT'S SHAPE.
This lane was handed beat 08 as "your figure-count correction left `tag: 2boys`
behind as a residue of the retired three-figure master, so any correct draft now
fails check()". THAT PREMISE IS FALSE AND IT WAS MEASURED, NOT ARGUED.

`sd_prompt.count_tag()` does NOT count figures. It regex-matches the LEADING
Danbooru tag of `compress()`'s output and returns it. So `tag:` records THE
AUTHORING CONVENTION A BEAT'S DRAFTS OPEN IN, not a claim about how many bodies
the beat needs. The count guard in `render_wave_goblin.check()` says so in its own
docstring: it exists to catch a draft that opens "Two adult guard men" sitting in
a `1boy` slot -- an INTERNAL CONSISTENCY check between a draft and its beat, which
is why it caught `ep2-b06-plate-0815`.

The proof that two figures are orthogonal to the tag is already in this file and
was measured on the real CLIP on 2026-08-17:
  * BEAT 07 declares `tag: 1boy` and `authored_b07_cast_0817` puts a guard AND
    {{GOBLIN}} in frame -- TWO FIGURES -- deriving `1boy`, 62/77, ZERO FAULTS.
  * BEAT 08 declares `tag: 2boys` and all of `authored`, `authored_b08_plate` and
    `authored_b08_idfix_r2` open "Two ..." -- deriving `2boys` at 72/77, 65/77 and
    76/77, ZERO FAULTS EACH.
Two figures, written two ways, both legal. Nothing is inconsistent.

AND THE EDIT WOULD HAVE DONE REAL DAMAGE. Re-running `check()` on beat 08's
existing `authored` with `tag` forced to `1boy` returns:
    !! COUNT TAG is '2boys', draft declares '1boy'
-- one fault, and the same fault would land on ALL SIX existing beat-08 drafts,
every one of which is currently clean. The guard lane's refusal to edit a peer's
key was correct and this script does not overturn it; it removes the reason
anybody wanted to.

SO THE BLOCKER IS CLEARED BY AUTHORING IN BEAT 08'S OWN CONVENTION. The new draft
opens "Two men," -> derives `2boys` -> matches the declared `2boys` -> passes.
Two figures, guard + goblin, exactly as the 2026-08-17 script ruling requires.

THE DRAFT ITSELF, and every clause is a constraint someone already paid for:
  * `Two men,` LEADING -- the count tag must be the first token for count_tag()
    to see it, and `2boys` is what beat 08 declares.
  * THE NEAR MAN IS GUARD 2 / GUARD B, per node.md ("Guard 2 lowers the
    clipboard") and the approved sheet: LIGHT SANDY HAIR, CREAM SHIRT, WHITE
    SASH, BROWN SKIRT. The founder ruled "the cast stands as drawn". 14 of 17
    older prompts for these beats asked for `bald` and NEITHER APPROVED GUARD IS
    BALD; this one asks for hair and does not negate baldness, because negating
    it is a separate lane's problem and not needed when the hair is named.
  * NO GLASSES, AND THAT IS THE FOUNDER'S WORDING NOT AN OMISSION: "draw the
    second man without glasses. we need to have control." Guard 2 is the second
    man. Beat 08 has no second guard face for eyewear to leak onto, and NO
    general eyewear fix is attempted here -- no `glasses` in the negative, no
    binding instrument -- because a dedicated lane owns that problem.
  * `the near one ... holds a bark clipboard in both hands` -- PROP OWNERSHIP.
    A prop binds to whoever is drawn NEAREST, which is the law
    `authored_b10_cast_0817` used deliberately rather than fought, and this draft
    copies its clause shapes because it is the only cast-correct guard draft
    measured clean. The board is at rest in his hands: A STATE, NOT A VERB. The
    beat's action is "LOWERS the clipboard and POINTS", and this model renders a
    verb's END state, so a plate that said "lowering" or "pointing" would arrive
    finished with nowhere to travel. The plate is the PRE state on purpose and
    i2v supplies the move.
  * WHETHER THE POINT WILL BIND TO THE GUARD IS NOT ASKED HERE. In
    text-to-image a pointing arm attached to the goblin 3 of 3 and a board 9 of
    12 however worded; three queued probes (`ep2-b08-twofig-both`, `-armonly`,
    `ep2-b07-twofig-turn`) own that question off an init. This draft deliberately
    does not compete with them.
  * EVERY HAND IN FRAME IS NAMED -- the near man's on the board, the goblin's
    `arms down` (beat 10's own two-token form). An unspecified hand is an empty
    region and the vacancy law fills it: beat 10's unnamed far man grew a bamboo
    pole with `weapon` negated, against beat 05's four specified hands at 0 of 3.
  * `looks at his belly` -- beat 08's `done_when` needs the BELLY legible as the
    point's target; this puts his own attention there without asking for the
    gesture.
  * `tall grass, pale sky above` -- THE VACANCY LAW, one noun per region. The
    ground band and the ABOVE-HORIZON band each get their own, which is exactly
    what beat 14 spent three rungs learning on 2026-08-17: a region with no noun
    of its own comes back a flat wash, and no ground noun can ever fill a band
    above the horizon.
  * `hedgerow` IS DROPPED, and it is the one thing given up. With it the draft
    measures 75/77 and `compress()` SHEDS `very aesthetic` -- the style anchor --
    which is a fault. Measured, not guessed: J 75/77 anchor MISSING, K 74/77
    anchor PRESENT. `tall grass` and `pale sky above` both survive, so both
    bands still have a noun and only the third is lost. THE STYLE TAIL IS NOT
    CUT.
  * MEASURED ON THE REAL CLIP through `render_wave_goblin.check()`:
    74/77 positive, 66/77 negative, STYLE ANCHOR PRESENT, count tag `2boys`
    against a declared `2boys`, ZERO FAULTS -- inside the 72-77 standard the
    guard lane's eight drafts set.

RIGOUR. This is ~350 KB of hand-written provenance with live peers in it, so it is
edited as TEXT: anchor matched exactly once, sha256 before and after, byte delta
asserted equal to the payload, backup written first, and a PARSED-VARIANT DIFF
proving exactly one key was added, that no key anywhere was removed or altered --
`tag` included, asserted still `2boys` -- and that the round-tripped value of the
new key is BYTE-IDENTICAL to the string that was measured. No YAML round-trip is
performed on the file; `yaml.safe_load` is used only to compare, never to write.
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
SUFFIX = ".bak-b08-cast-0817"

KEY = "authored_b08_cast_0817"

# The EXACT string measured at 74/77, 0 faults. The written block is generated
# from this constant and then read back and compared to it, so a wrapping slip
# cannot change what gets sent to the renderer.
DRAFT = (
    "Two men, the near one light sandy hair, cream shirt, white sash, brown "
    "skirt, holds a bark clipboard in both hands, the far one a goblin, "
    "{{GOBLIN}}, patched cloak, looks at his belly, arms down, tall grass, "
    "pale sky above, cinematic lighting, masterpiece, best quality, very "
    "aesthetic No girl, no child, no armor, no helmet, no knight, no white "
    "background, no plain background, no dark, no night. No photorealism, no "
    "3D render look. 9:16 vertical, no text."
)

COMMENT = """\
    # ── `authored_b08_cast_0817` — 2026-08-17. THE FIRST CAST-CORRECT BEAT-08
    # DRAFT. Beat 08 was the last guard beat with no filed plate. It is guard +
    # goblin — TWO figures — per the script ruling of the same day
    # (`figure_count_ruled_from_the_script_0817` in done-definitions.yaml), and
    # `tag: 2boys` above is CORRECT and DELIBERATELY UNTOUCHED: count_tag() reads
    # the LEADING tag, not a figure count, so this draft opens "Two men," and
    # derives the `2boys` the beat already declares. Beat 07 shows the same two
    # figures written the other way and declaring `1boy`, also clean — the two
    # conventions are both legal and neither is a claim about how many bodies the
    # beat needs. Forcing `tag: 1boy` here would fault all six existing beat-08
    # drafts, which are currently clean; measured, not assumed.
    # Cast is Guard 2 = Guard B off the approved sheet ("the cast stands as
    # drawn"): light sandy hair, cream shirt, white sash, brown skirt — NOT bald,
    # which 14 of 17 older prompts for these beats asked for. NO GLASSES, per
    # "draw the second man without glasses. we need to have control."; no general
    # eyewear instrument is attempted here because another lane owns it.
    # Clause shapes are copied from `authored_b10_cast_0817`, the only
    # cast-correct guard draft measured clean, including its prop-ownership law —
    # the board is in the NEAR man's hands because a prop binds to whoever is
    # drawn nearest. The board is AT REST: a state, not a verb, so the beat's
    # "lowers the clipboard and points" has somewhere to travel. Whether the
    # point binds to the guard is the three queued probes' question, not this
    # draft's. Every hand in frame is named (vacancy law). `hedgerow` is given up
    # on purpose: with it the draft measures 75/77 and compress() sheds `very
    # aesthetic`; without it, 74/77 with the anchor intact and both the ground
    # band and the above-horizon band still holding a noun of their own.
    # Real CLIP via render_wave_goblin.check(): 74/77 pos, 66/77 neg, anchor
    # present, count `2boys` == declared `2boys`, ZERO FAULTS.
"""

# Anchor: THE BEAT-9 HEADER, which is the line that closes beat 08's block.
#
# The first attempt anchored on the TAIL OF `authored_b08_refresh` -- its last two
# lines plus the blank line and `  9:`. That is a real bug and the parsed-variant
# diff caught it: inserting before those lines lands the new comment INSIDE the
# refresh draft's folded scalar, truncating it and appending 26 lines of comment
# text to the prompt a peer authored. The byte delta was a perfect 2706 and the
# sha changed exactly as expected, so ONLY the parse-back comparison saw it --
# "beat 8 key 'authored_b08_refresh' was MODIFIED. Refusing." Recorded because it
# is the argument for the parsed diff in one concrete instance: a byte count
# cannot tell an insertion BETWEEN two scalars from an insertion INTO one.
#
# Anchoring on the next beat's header instead puts the key after the blank line
# that already terminates beat 08's last draft, which is exactly where
# `authored_b10_cast_0817` sits in its own block. Matched once (verified).
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

    before_txt = TARGET.read_text(encoding="utf-8")
    print("sha256 before      %s  (%d bytes)" % (sha(before_txt), len(before_txt.encode())))

    if KEY in before_txt:
        sys.exit("!! %s is ALREADY present. Refusing to double-insert." % KEY)
    n = before_txt.count(ANCHOR)
    if n != 1:
        sys.exit("!! anchor matches %d times, expected exactly 1. Refusing to guess." % n)

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
        if b == 8:
            if add != {KEY}:
                sys.exit("!! beat 8 additions were %s, expected exactly {%s}."
                         % (sorted(add), KEY))
            for k in bb:
                if bb[k] != aa[k]:
                    sys.exit("!! beat 8 key %r was MODIFIED. Refusing." % k)
            print("beat 8 added       [%r]" % KEY)
            print("beat 8 existing    all %d keys byte-identical (tag included)" % len(bb))
        else:
            if add or bb != aa:
                sys.exit("!! beat %s changed and must not have (added %s)."
                         % (b, sorted(add)))
    if after["beats"][8]["tag"] != "2boys":
        sys.exit("!! beat 8 tag is no longer '2boys'. Refusing.")
    print("beat 8 tag         %r  (UNCHANGED, as intended)" % after["beats"][8]["tag"])

    # The round-tripped value must be exactly the string that was measured.
    got = after["beats"][8][KEY]
    if got != DRAFT:
        print("!! ROUND-TRIP MISMATCH -- the folded block does not equal the "
              "measured string.\n   expected: %r\n   got:      %r" % (DRAFT, got))
        return 3
    print("round-trip         value is BYTE-IDENTICAL to the measured string")

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
