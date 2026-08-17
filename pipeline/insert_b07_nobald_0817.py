#!/usr/bin/env python3
"""Add beat 07's two NO-BALD rungs to wave-drafts.yaml. TWO KEYS, PURELY ADDITIVE.

    python3 pipeline/insert_b07_nobald_0817.py            # check, writes nothing
    python3 pipeline/insert_b07_nobald_0817.py --apply

TWO DEFECTS WERE MEASURED IN `ep2-b07-cast-0817` AND THEY ARE FIXED ON SEPARATE
RUNGS, because fixing both in one draft would make the result unattributable.

    rung A  authored_b07_nobald_0817   `bald` removed. NOTHING ELSE MOVES.
    rung B  authored_b07_twofig_0817   rung A, plus the grammar fix. ONE variable
                                       against rung A; two against the original.

DEFECT 1 -- `bald head`, and it is not a literal in the draft. `authored_b07_cast_0817`
carries the `{{GOBLIN}}` marker and `goblin_ipa_sample.py` fills it from its own
constant, `GOBLIN_DEF = "green skin, bald head"` (line 65). The string the model
received was

    1boy, a guard man with dark cropped hair, wire-rim glasses, tan wrap tunic,
    white sash points one arm at green skin, bald head crouching low, other hand
    open, tall grass, ...

b06 is clean for exactly one mechanical reason: `authored_b06_cast_0817` carries NO
`{{GOBLIN}}` marker, so nothing substitutes `bald` into it, and it rendered 12 of 12
HAIRED off the same refs, sampler, model and day. b07 and b08 are the only two cast
drafts carrying the slot and the only two that went 12 of 12 BALD. `bald` is
broadcast-class and scoping does not contain it; the token is REMOVED, and no
negation is attempted because the vacancy law says a negative does not reach an
empty region and a broadcast attribute is a binding failure, not a presence failure.
`GOBLIN_DEF` is NOT touched (asserted below): bald for the GOBLIN is the founder's
own 2026-08-12 ruling and eleven goblin beats share that constant.

DEFECT 2 -- read straight off the compressed string above, which is why it is worth
quoting. TWO separate binding failures, both of them grammatical:

  * `white sash points one arm` -- `compress()` splits on commas, so `points` arrives
    as a list item whose nearest preceding noun is `white sash`. THE SASH IS THE
    SUBJECT OF THE VERB. 0 of 12 frames contained a point.
  * THERE IS NO GOBLIN NOUN ANYWHERE IN THE PROMPT. `{{GOBLIN}}` expands to bare
    attributes -- `green skin, bald head` -- with no noun to hang them on, so the only
    subject in the sentence is the guard and they bound to him. Green skin arrived as
    a green mitt.

RUNG B FIXES BOTH BY GRAMMAR AND ONLY BY GRAMMAR:
  * `, the guard points his other arm at ...` puts a noun immediately before the verb,
    so `points` has the guard as its subject.
  * `a crouching goblin with green skin` gives the goblin a NOUN and binds his one
    attribute to it with `with`, inside his own noun phrase.
  * `one hand open` moves UP into the guard's own attribute run. It used to trail as
    `other hand open` AFTER the goblin's attributes, where the nearest subject would
    now be the goblin -- the same binding law that caused defect 2 would have handed
    the goblin the open hand. Nothing trails the goblin except world and style, so no
    attribute can mis-bind to him.
  * The guard's cast run -- `A guard man with dark cropped hair, wire-rim glasses, tan
    wrap tunic, white sash` -- is BYTE-IDENTICAL to the original and still leads the
    prompt. That is deliberate: naming the cast early is the thing that works on b06
    and b10, and this rung must not disturb it while testing something else.

WHAT RUNG B DOES *NOT* DO, SAID PLAINLY BECAUSE IT IS EASY TO OVERCLAIM.
IT DOES NOT CHANGE THE DANBOORU COUNT TAG. It still derives and declares `1boy` on a
two-figure beat. The goblin gets a GRAMMATICAL subject slot, not a count slot. That
limit is mechanical, and it was measured rather than assumed:

  * `sd_prompt._tag_from_clause` reads ONLY `sentences[0].split(",")[0]` -- the first
    sentence up to its first comma. To derive `2boys` that fragment must contain a
    `_PLURAL` word AND the word "two".
  * `render_wave_goblin.check()`'s count guard compares the derived tag against the
    BEAT-WIDE `d["tag"]`, and `goblin_ipa_sample.py` calls `wg.check(BEAT, d, ...)`
    directly -- it never calls `apply_variant_declaration`, so there is NO per-variant
    count override available on the box path. A fault returns rc 1 and draws nothing.
  * Therefore deriving `2boys` on beat 07 requires editing beat 7's `tag:` from
    `1boy`, which would fault every sibling draft in beat 7's block -- all of which
    open one-figure and are currently clean. That is the exact trap
    `insert_b08_cast_draft_0817.py` measured and refused on beat 08, and this script
    does not spring it. `tag: 1boy` is asserted UNCHANGED below.

So beat 07 keeps a `1boy` declaration that agrees with its derivation, 0 faults, and
the earlier lane's verified consistency is intact. If rung B still loses the point or
still mitts the goblin, the residual suspect is the count tag itself and the fix then
requires a per-variant count declaration in the sampler -- a shared-file change that
is a different lane's call, not something to smuggle in here.

MEASURED ON THE REAL CLIP through `render_wave_goblin.check()`, transformers
`openai/clip-vit-large-patch14`, offline:

    baseline authored_b07_cast_0817   62/77 pos   58/77 neg   0 faults
    rung A   authored_b07_nobald_0817 59/77 pos   58/77 neg   0 faults
    rung B   authored_b07_twofig_0817 65/77 pos   58/77 neg   0 faults

count tag `1boy` derived against a declared `1boy` on all three; style anchor
`very aesthetic` PRESENT on all three. TOKEN TRADE: NONE ON EITHER RUNG. Rung A frees
3 tokens and spends none. Rung B spends 6 of the 15 tokens of headroom it has and
still sits 12 under budget -- nothing was cut to pay for it, no word was dropped, the
style tail is intact. There are NO traded words to name as first suspects on either
rung, which is the whole benefit of doing this on a beat with headroom.

BEWARE THE ESTIMATOR. Without `transformers` importable, `sd_prompt._token_estimate`
falls back to a word count and `compress()` uses that same estimate for its own
fitting loop, so it sheds the style tail the real tokenizer keeps and invents faults.
It reads beat 08's clean draft as 85/77 with two faults against a true 74/77 with
none. Every figure above is the real count; a token number quoted from a plain
`python3` on this Mac is fiction.

RIGOUR. ~450 KB of hand-written provenance with ~30 live peers in it, so it is edited
as TEXT: anchor matched exactly once, sha256 before and after, byte delta asserted
equal to the payload, backup written first, and a PARSED-VARIANT DIFF proving exactly
TWO keys were added, that no key anywhere was removed or altered (`tag` included),
and that both round-tripped values are BYTE-IDENTICAL to the strings that were
measured. A BYTE DELTA THAT MATCHES IS NOT PROOF: a peer's first anchor would have
written 26 lines INSIDE a folded scalar with a perfect delta and a sha that moved
exactly as predicted, and only the parse-back caught it. No YAML round-trip is
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
SUFFIX = ".bak-b07-nobald-0817"

BEAT = 7

KEY_A = "authored_b07_nobald_0817"
KEY_B = "authored_b07_twofig_0817"

# What `authored_b07_cast_0817` actually SENT, after the sampler filled the slot.
# Kept here so rung A's "one variable" is checkable rather than asserted.
PREDECESSOR_SENT = (
    "A guard man with dark cropped hair, wire-rim glasses, tan wrap tunic, "
    "white sash points one arm at green skin, bald head crouching low, other "
    "hand open, tall grass, treeline behind, pale sky above, cinematic "
    "lighting, masterpiece, best quality, very aesthetic No girl, no child, "
    "no armor, no helmet, no knight, no clipboard, no dark, no night. No "
    "photorealism, no 3D render look. 9:16 vertical, no text."
)

# RUNG A -- measured at 59/77, 0 faults. The predecessor's sent string minus
# exactly ", bald head". Nothing else moves.
DRAFT_A = (
    "A guard man with dark cropped hair, wire-rim glasses, tan wrap tunic, "
    "white sash points one arm at green skin crouching low, other hand open, "
    "tall grass, treeline behind, pale sky above, cinematic lighting, "
    "masterpiece, best quality, very aesthetic No girl, no child, no armor, "
    "no helmet, no knight, no clipboard, no dark, no night. No photorealism, "
    "no 3D render look. 9:16 vertical, no text."
)

# RUNG B -- measured at 65/77, 0 faults. Rung A plus the grammar fix, and nothing
# else: the guard's cast run and the whole world/style/negative tail are untouched.
DRAFT_B = (
    "A guard man with dark cropped hair, wire-rim glasses, tan wrap tunic, "
    "white sash, one hand open, the guard points his other arm at a crouching "
    "goblin with green skin, tall grass, treeline behind, pale sky above, "
    "cinematic lighting, masterpiece, best quality, very aesthetic No girl, "
    "no child, no armor, no helmet, no knight, no clipboard, no dark, no "
    "night. No photorealism, no 3D render look. 9:16 vertical, no text."
)

COMMENT_A = """\
    # ── `authored_b07_nobald_0817` — 2026-08-17. RUNG A: `bald` REMOVED, ONE
    # VARIABLE, NOTHING ELSE MOVED.
    # `authored_b07_cast_0817` above existed to take `bald` off the guards and it
    # still SENT `bald head`, because the token is not a literal in it: the
    # `{{GOBLIN}}` slot is filled by goblin_ipa_sample.py's own
    # `GOBLIN_DEF = "green skin, bald head"`. b08 carries the slot too; b06 does
    # NOT, and b06 came back 12 of 12 HAIRED off the same refs, sampler, model and
    # day while b07 and b08 went 12 of 12 BALD. One mechanical difference, and it
    # is this slot — so the b06 contrast now has a mechanism, not a correlation.
    # `bald` is BROADCAST-CLASS: scoping it inside the goblin's clause does not
    # contain it (b08 is the proof). It is REMOVED, not re-scoped, and NO negation
    # is attempted — the vacancy law says a negative does not reach an empty region
    # and a broadcast attribute is a BINDING failure, not a presence failure.
    # `GOBLIN_DEF` IS NOT TOUCHED: bald FOR THE GOBLIN is the founder's own
    # 2026-08-12 ruling and eleven goblin beats share that constant. Only the two
    # beats that put a guard and a goblin in one frame drop the slot.
    # THE ONE VARIABLE, checked by the insert script and not merely claimed: this
    # draft equals the predecessor's SENT string minus exactly the eleven characters
    # `, bald head`. No other word moved, no comma moved. The sash still governs
    # `points` and the goblin still has no noun — those are RUNG B's variable and
    # are deliberately left broken here, so that if the guard comes back haired it
    # is `bald` that did it and nothing else.
    # REAL CLIP via render_wave_goblin.check() (transformers, clip-vit-large-patch14,
    # offline): 59/77 pos, 58/77 neg, anchor `very aesthetic` PRESENT, count `1boy`
    # == declared `1boy`, ZERO FAULTS. Baseline was 62/77 / 58/77 / 0 faults.
    # TOKEN TRADE: NONE. 3 tokens freed and none spent — nothing cut, nothing added,
    # style tail intact. No traded words to suspect.
"""

COMMENT_B = """\
    # ── `authored_b07_twofig_0817` — 2026-08-17. RUNG B: RUNG A PLUS THE GRAMMAR
    # FIX. One variable against rung A; two against the original, and that is stated
    # rather than glossed — read this rung against `authored_b07_nobald_0817`, not
    # against `authored_b07_cast_0817`.
    # WHAT WAS BROKEN, read straight off the compressed string the model received:
    # `1boy, a guard man ..., white sash points one arm at green skin, bald head
    # crouching low, other hand open, ...`
    #   * compress() splits on commas, so `points` arrived as a list item whose
    #     nearest preceding noun was `white sash`. THE SASH WAS THE SUBJECT OF THE
    #     VERB, and 0 of 12 frames contained a point.
    #   * THERE WAS NO GOBLIN NOUN ANYWHERE. `{{GOBLIN}}` expands to bare attributes
    #     with nothing to hang them on, so the guard was the only subject in the
    #     sentence and they bound to him — green skin arrived as a green mitt.
    # THE FIX IS GRAMMAR AND ONLY GRAMMAR:
    #   * `, the guard points his other arm at ...` — a noun immediately before the
    #     verb, so `points` has the guard as its subject.
    #   * `a crouching goblin with green skin` — the goblin gets a NOUN, with his one
    #     attribute bound inside his own noun phrase by `with`.
    #   * `one hand open` moves UP into the guard's attribute run. It used to trail
    #     AFTER the goblin's attributes, where the nearest subject is now the goblin
    #     — the same binding law that caused the mitt would have handed him the open
    #     hand. Nothing now trails the goblin but world and style.
    #   * The guard's cast run is BYTE-IDENTICAL to the original and still LEADS the
    #     prompt. Naming the cast early is what works on b06 and b10; this rung must
    #     not disturb it while testing something else.
    # IT DOES NOT CHANGE THE DANBOORU COUNT, and that is a hard mechanical limit, not
    # an oversight. `_tag_from_clause` reads only the first sentence up to its first
    # comma, and check()'s count guard compares against the BEAT-WIDE `tag:` —
    # goblin_ipa_sample.py calls wg.check(BEAT, d, ...) directly and never calls
    # apply_variant_declaration, so there is no per-variant count override on the box
    # path and a fault returns rc 1 with nothing drawn. Deriving `2boys` here would
    # require editing beat 7's `tag:`, which faults every sibling draft in this block
    # — the exact trap measured and refused on beat 08. So the goblin gets a
    # GRAMMATICAL subject slot, not a count slot, and `tag: 1boy` stays.
    # If this rung still loses the point or still mitts the goblin, the residual
    # suspect IS the count tag, and the fix then needs a per-variant count
    # declaration in the sampler — a shared-file change and another lane's call.
    # REAL CLIP via render_wave_goblin.check(): 65/77 pos, 58/77 neg, anchor PRESENT,
    # count `1boy` == declared `1boy`, ZERO FAULTS.
    # TOKEN TRADE: NONE. This spends 6 of the 15 tokens of headroom rung A leaves and
    # still sits 12 under budget. Nothing was cut to pay for it, no word dropped,
    # style tail intact. No traded words to name as first suspects.
"""

# Anchor: THE BEAT-8 HEADER, the line that closes beat 07's block. Anchoring on the
# tail of a preceding draft is the documented trap -- it lands the insertion INSIDE a
# folded scalar with a byte delta that matches perfectly. The next beat's header sits
# after the blank line that already terminates beat 07's last draft. Matched exactly
# once (asserted below, not assumed).
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
    a = ap.parse_args()

    import yaml  # compare only; never used to write this file

    # RUNG A'S ONE VARIABLE, checked rather than claimed.
    if PREDECESSOR_SENT.replace(", bald head", "", 1) != DRAFT_A:
        sys.exit("!! DRAFT_A is not the predecessor minus ', bald head' -- more "
                 "than one variable moved on rung A. Refusing.")
    print("rung A variable    DRAFT_A == predecessor-sent minus ', bald head'")
    for name, d in (("A", DRAFT_A), ("B", DRAFT_B)):
        if "bald" in d:
            sys.exit("!! rung %s still contains 'bald'. Refusing." % name)
        if "{{GOBLIN}}" in d:
            sys.exit("!! rung %s still carries the goblin slot, which the sampler "
                     "would fill with 'bald head'. Refusing." % name)
    print("no-bald            both rungs: 'bald' absent, {{GOBLIN}} slot gone")

    before_txt = TARGET.read_text(encoding="utf-8")
    print("sha256 before      %s  (%d bytes)"
          % (sha(before_txt), len(before_txt.encode())))

    for k in (KEY_A, KEY_B):
        if k in before_txt:
            sys.exit("!! %s is ALREADY present. Refusing to double-insert." % k)
    n = before_txt.count(ANCHOR)
    if n != 1:
        sys.exit("!! anchor matches %d times, expected exactly 1. Refusing to "
                 "guess." % n)

    block = (build_block(COMMENT_A, KEY_A, DRAFT_A)
             + build_block(COMMENT_B, KEY_B, DRAFT_B))
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
            if add != {KEY_A, KEY_B}:
                sys.exit("!! beat %s additions were %s, expected exactly %s."
                         % (BEAT, sorted(add), sorted([KEY_A, KEY_B])))
            for k in bb:
                if bb[k] != aa[k]:
                    sys.exit("!! beat %s key %r was MODIFIED. Refusing."
                             % (BEAT, k))
            print("beat %d added       %s" % (BEAT, sorted(add)))
            print("beat %d existing    all %d keys byte-identical (tag included)"
                  % (BEAT, len(bb)))
        else:
            if add or bb != aa:
                sys.exit("!! beat %s changed and must not have (added %s)."
                         % (b, sorted(add)))
    if after["beats"][BEAT]["tag"] != "1boy":
        sys.exit("!! beat %d tag is no longer '1boy'. Refusing -- editing it would "
                 "fault every sibling draft in this block." % BEAT)
    print("beat %d tag         %r  (UNCHANGED -- see the module docstring)"
          % (BEAT, after["beats"][BEAT]["tag"]))

    # GOBLIN_DEF must be exactly what it was. This script's whole argument is that
    # the shared sampler is not edited, so it asserts that rather than trusting it.
    samp = (REPO / "pipeline" / "goblin_ipa_sample.py").read_text(encoding="utf-8")
    if 'GOBLIN_DEF = "green skin, bald head"' not in samp:
        sys.exit("!! goblin_ipa_sample.py GOBLIN_DEF is not the 2026-08-12 founder "
                 "ruling any more. Refusing -- this script assumes it is untouched.")
    print("GOBLIN_DEF         untouched (founder's 2026-08-12 goblin ruling intact)")

    # The round-tripped values must be exactly the strings that were measured.
    for key, want in ((KEY_A, DRAFT_A), (KEY_B, DRAFT_B)):
        got = after["beats"][BEAT][key]
        if got != want:
            print("!! ROUND-TRIP MISMATCH on %s -- the folded block does not equal "
                  "the measured string.\n   expected: %r\n   got:      %r"
                  % (key, want, got))
            return 3
    print("round-trip         both values BYTE-IDENTICAL to the measured strings")

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
