#!/usr/bin/env python3
"""Add cast-correct guard plate drafts for beats 05, 06, 07 and 09, additively.

    python3 pipeline/insert_guard_cast_drafts_0817.py --check
    python3 pipeline/insert_guard_cast_drafts_0817.py --apply

WHY THESE DRAFTS EXIST. `guard_plates_are_miscast_0816` in
review/ep2-picks/done-definitions.yaml: 0 of 17 guard plate prompts name the
approved cast and 14 of 17 ask for `bald`, and NEITHER APPROVED GUARD IS BALD.
The wardrobe canon was frozen by the founder on 2026-08-16 ("the cast stands as
drawn", glasses included) and is recorded in
`guards_CORRECTION_0816.still_genuinely_the_founders_ANSWERED_0816`:

    guard A / GUARD 1 -- dark cropped hair, tan wrap tunic, wide white waist
                         sash, WIRE-RIM GLASSES
    guard B / GUARD 2 -- light sandy hair, cream short-sleeve shirt, white sash
                         over one shoulder, broad dark-brown wrap skirt; he is
                         the one who carries the bark board

The 1/2 -> A/B mapping is not guessed. It is read off the board: beat 10's
stage direction is "Guard 2 flips the clipboard around" and the cast-correct
beat-10 draft drawn on the Mac this morning puts the board in the hands of the
light-sandy-haired man, while beat 09 ("close on Guard 1's face") is drawn dark
cropped hair + wire-rims.

WHY A SCRIPT AND NOT AN EDITOR. pipeline/wave-drafts.yaml is ~350 KB of
hand-written provenance and live lanes are in this worktree. So it is edited as
TEXT by a checked insert -- sha256 before and after, a byte delta asserted
against the exact payload, a backup, and a PARSED-VARIANT DIFF proving which
keys moved and that no existing value changed. The pattern is
`insert_b0708_figure_count_0817.py` / `insert_sapling_canon_drafts_0816.py`.
FOUR INSERTIONS, ZERO DELETIONS, NOT ONE EXISTING LINE TOUCHED. Every superseded
`bald` draft stays exactly where it is: the disagreement is the record, and
pipeline/canon.yaml's `ep2-guard-hair` subject already lists them by name.

WHAT WAS MEASURED BEFORE ANY OF THIS WAS WRITTEN, and it is a finding about the
box stills path rather than about these beats. `render_wave_goblin.check()`
asserts the style anchor `very aesthetic` survives into the positive, but it
tests compress()'s OUTPUT STRING while compress() budgets with
`sd_prompt._token_estimate`, which is calibrated on PROSE. A cast description is
a comma-separated TAG LIST, and sd_prompt says in its own words that the prose
estimator "under-counts EVERY ONE" of those -- by up to 10 tokens. So a
tag-dialect positive can pass compress(), pass the style-anchor assertion, and
STILL be truncated by CLIP with the anchor among the lost tail. Six first drafts
of these prompts did exactly that at 78-82 real tokens while check() reported no
fault. Every draft below is therefore held to the REAL CLIP count of the string
that actually gets sent, measured with `sd_prompt.negative_tokens`:

    beat 05  positive 75/77   negative 68/77
    beat 06  positive 72/77   negative 65/77
    beat 07  positive 76/77   negative 60/77
    beat 09  positive 73/77   negative 74/77

THE TOKEN TRADES, NAMED SO THEY ARE THE FIRST SUSPECTS AND NOT A MYSTERY LATER.
The style tail is `cinematic lighting, masterpiece, best quality, very
aesthetic` on all four, byte-identical to the tail beats 05, 06 and 09 already
carry, so it is NOT a variable between them. ON BEAT 07 ONLY it replaces that
beat's longer `Medium full shot, bright morning light, cinematic lighting,
detailed, newest, ...` tail, which costs 29 CLIP tokens against this one's 14
and cannot fit beside a named cast plus a goblin. THE TRADED WORDS ARE `Medium
full shot`, `bright morning light`, `detailed` and `newest`, and they are the
first thing to blame if beat 07's framing or light regresses.

THREE LAWS APPLIED ON PURPOSE RATHER THAN REDISCOVERED.
 1. THE HAND LAW (2026-08-17). An unspecified hand is an empty region and this
    checkpoint fills empty regions with nouns; the negative does not reach it.
    Beat 05 specified both men's arms and all four hands came back EMPTY at 3 of
    3, while beat 10 specified only the near man's and the far pair came back
    holding a bamboo pole at one seed and a duplicate board at another, with
    `weapon` in the negative. So: beat 05 `arms swinging`, beat 06 `in both
    hands`, beat 07 the pointing arm AND `other hand open`. Beat 09 removes the
    question instead of answering it -- `no hands` puts `hands` in the negative,
    which is the right move on a face plate and is what the Mac draft did.
 2. THE VACANCY LAW, AND THAT THE HOLE IS OFTEN ABOVE THE HORIZON. Every draft
    gives the upper third a POSITIVE noun of its own -- `pale sky above` on 05,
    06, 07 -- because a ground noun cannot fill a sky region and the negative
    does not reach a hole at all. `horizon` is negated NOWHERE: a clause naming
    something `behind` is dead in a plan view, and deleting `horizon` from a
    beat-05 negative is the one edit that ever dropped that beat off a downward
    plan view.
 3. PROP OWNERSHIP. Hair and garments bind to their person clause but a prop
    goes to whoever is drawn nearest, so on beat 06 the board sits inside guard
    B's own clause, and beat 05 -- which has no board in it at all -- negates
    `clipboard` outright. BEAT 07 NEGATES `clipboard` FOR THE SAME REASON IT
    EXISTS: its guard is GUARD 1, WHO HAS NO BOARD. That is why beat 07 needs
    its own plate and must never inherit beat 08's.

WHAT IS NOT CLAIMED, and it is the founder's.
 * NO GLASSES ON BEATS 05 OR 10. In a two-guard plate, `glasses` attached to
   exactly one man's clause landed on BOTH men at 5 of 5 legible renders --
   eyewear specifically, at seeds where hair and garments separated cleanly. So
   guard A's wire-rims cannot be named on a two-guard plate without putting them
   on guard B too, and whether guard B wears them IS A CAST CALL (R4). It is
   left untouched: 05 names no eyewear, and the wire-rims are carried by beat
   09's close-up, which has only one man in it.
 * BEAT 07 NAMES THEM ANYWAY AND THE RISK IS PRE-REGISTERED. The 2026-08-16
   ruling says every prompt showing guard A's face must name the wire-rims, and
   beat 07 is guard A facing camera. Beat 07 holds no SECOND GUARD for them to
   spread to -- it holds a goblin -- so the 5-of-5 spread is not the risk here.
   THE UNMEASURED RISK IS EYEWEAR REACHING THE GOBLIN, and it is named as a read
   rather than negated, because negating `glasses` against a positive that asks
   for `wire-rim glasses` is the contradiction plate_scratch.py exits 7 on.
 * NO RENDER IS RELEASED AND NO `plate_ack` IS WRITTEN. These are draft keys.
   `guards_CORRECTION_0816.what_this_releases` governs and is unchanged: staged
   plates of the approved pair may be DRAWN; motion off a costume card may not.

WHY `bald` APPEARS NOWHERE, INCLUDING IN A `no bald` CLAUSE. pipeline/canon.yaml
`ep2-guard-hair` forbids `\\bbald\\b` and `\\bbare heads?\\b` on beats 5, 6, 7, 9,
10 and 11, and a `no X` clause in a POSITIVE is how this path builds its
negative, so `no bald` would put the word in scope. Hair is named POSITIVELY
instead, which is what the vacancy law wants anyway. On beat 07 that also means
the goblin is NOT described as bald even though he canonically is -- `{{GOBLIN}}`
carries the founder's definition at render time and the drawn design is his, so
the word is not needed in the draft text.
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

KEY = "authored_b%02d_cast_0817"

TAIL = "cinematic lighting, masterpiece, best quality, very aesthetic "
FOOT = "No photorealism, no 3D render look. 9:16 vertical, no text."

DRAFTS = {
    5: ("Two guard men halt in tall grass, hedgerow behind, pale sky above, one "
        "with dark cropped hair, tan wrap tunic, white waist sash, the other "
        "with light sandy hair, cream shirt, brown wrap skirt, arms swinging, "
        + TAIL +
        "No girl, no child, no armor, no helmet, no knight, no clipboard, no "
        "white background, no plain background, no dark, no night. " + FOOT),

    6: ("A guard man with light sandy hair, cream shirt, white shoulder sash "
        "and brown wrap skirt turns over a bark board in both hands at reading "
        "height, looking down, tall grass, hedgerow behind, pale sky above, "
        + TAIL +
        "No girl, no child, no armor, no helmet, no knight, no white "
        "background, no plain background, no dark, no night. " + FOOT),

    7: ("A guard man with dark cropped hair, wire-rim glasses, tan wrap tunic, "
        "white sash points one arm at {{GOBLIN}} crouching low, other hand "
        "open, tall grass, treeline behind, pale sky above, " + TAIL +
        "No girl, no child, no armor, no helmet, no knight, no clipboard, no "
        "dark, no night. " + FOOT),

    9: ("A guard man with dark cropped hair and wire-rim glasses, close on his "
        "face, head and shoulders, eyes open, thoughtful, mouth closed, tan "
        "tunic collar, white shoulder sash, tall grass and hedgerow behind "
        "him, " + TAIL +
        "No girl, no child, no hands, no clipboard, no armor, no helmet, no "
        "knight, no white background, no plain background, no closed eyes, no "
        "dark, no night. " + FOOT),
}

# Each payload goes at the END of its beat's block, i.e. immediately BEFORE the
# next beat's header. Anchors carry the following beat's `slug` so a bare `  6:`
# cannot match a stray line somewhere else in 350 KB.
ANCHORS = {
    5: "  6:\n    slug: the-clipboard\n",
    6: "  7:\n    slug: confiscate\n",
    7: "  8:\n    slug: inside-him\n",
    9: "  10:\n    slug: no-form\n",
}


def block(beat: int, text: str) -> str:
    """`    key: >-` plus the folded body at 6-space indent.

    A folded scalar joins its lines with single spaces, so the body is wrapped
    on word boundaries and never indented past column 6 (extra indent would make
    YAML treat the line literally). build() asserts the round-trip afterwards, so
    this formatting is checked rather than trusted.
    """
    body = textwrap.wrap(text, width=72, break_long_words=False,
                         break_on_hyphens=False)
    return ("    %s: >-\n" % (KEY % beat)
            + "".join("      %s\n" % line for line in body))


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build(text: str) -> tuple:
    """(new_text, payload_bytes). Every anchor must match EXACTLY ONCE."""
    if not text.endswith("\n"):
        sys.exit("!! target does not end in a newline; refusing to append blind.")
    out, total = text, 0
    for beat in sorted(DRAFTS):
        key = KEY % beat
        if key in text:
            sys.exit("!! `%s` is ALREADY in the file. Refusing to double-insert."
                     % key)
        anchor = ANCHORS[beat]
        n = out.count(anchor)
        if n != 1:
            sys.exit("!! anchor for beat %d matches %d times, expected 1. "
                     "Refusing." % (beat, n))
        payload = block(beat, DRAFTS[beat])
        out = out.replace(anchor, payload + anchor, 1)
        total += len(payload.encode())
    return out, total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    import yaml  # noqa: E402

    before_txt = TARGET.read_text()
    before = yaml.safe_load(before_txt)
    after_txt, payload = build(before_txt)

    delta = len(after_txt.encode()) - len(before_txt.encode())
    print("sha256 before      %s" % sha(TARGET))
    print("bytes  before      %d" % len(before_txt.encode()))
    print("byte delta         %d   (expected %d)" % (delta, payload))
    if delta != payload:
        sys.exit("!! byte delta != payload. Something other than an insert "
                 "happened.")

    after = yaml.safe_load(after_txt)

    if set(before) != set(after):
        sys.exit("!! top-level keys changed. Refusing.")
    if set(before["beats"]) != set(after["beats"]):
        sys.exit("!! the set of beats changed. Refusing.")

    for b in before["beats"]:
        add = set(after["beats"][b]) - set(before["beats"][b])
        rem = set(before["beats"][b]) - set(after["beats"][b])
        if rem:
            sys.exit("!! beat %s lost keys: %s" % (b, sorted(rem)))
        want = {KEY % b} if b in DRAFTS else set()
        if add != want:
            sys.exit("!! beat %s added %s, expected %s"
                     % (b, sorted(add), sorted(want)))
        # EVERY pre-existing key must be byte-identical -- this is the check that
        # catches an indentation slip swallowing a neighbouring draft, which a
        # byte count cannot see.
        for k in before["beats"][b]:
            if before["beats"][b][k] != after["beats"][b][k]:
                sys.exit("!! beat %s key %r was modified. Refusing." % (b, k))
        if add:
            print("beat %-3s added %-26s (existing keys all byte-identical)"
                  % (b, sorted(add)[0]))

    # THE ROUND-TRIP ASSERTION: the folded scalar must parse back to the exact
    # string authored above, or the measured token counts are about a different
    # prompt than the one that will render.
    for b, want in DRAFTS.items():
        got = after["beats"][b][KEY % b]
        if got != want:
            sys.exit("!! beat %d round-trip MISMATCH.\n   want %r\n   got  %r"
                     % (b, want, got))
    print("round-trip         all %d drafts parse back byte-identical"
          % len(DRAFTS))

    if not a.apply:
        print("\n--check only: nothing written. Re-run with --apply.")
        return 0

    backup = TARGET.with_suffix(".yaml.bak-guard-cast-0817")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(after_txt)
    print("\nbackup             %s" % backup.name)
    print("sha256 after       %s" % sha(TARGET))
    print("bytes  after       %d" % len(TARGET.read_bytes()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
