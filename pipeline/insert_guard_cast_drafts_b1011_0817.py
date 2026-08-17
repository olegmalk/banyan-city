#!/usr/bin/env python3
"""Add cast-correct guard plate drafts for beats 10 and 11, additively.

    python3 pipeline/insert_guard_cast_drafts_b1011_0817.py
    python3 pipeline/insert_guard_cast_drafts_b1011_0817.py --apply

The second half of insert_guard_cast_drafts_0817.py, which did beats 05, 06, 07
and 09 and whose four keys are already in the file. Same key naming, same house
insert pattern, nothing existing edited or deleted.

WHY. `guard_plates_are_miscast_0816`: 0 of 17 guard plate prompts name the
approved cast, 14 of 17 ask for `bald`, and NEITHER APPROVED GUARD IS BALD.
Wardrobe frozen by the founder 2026-08-16, "the cast stands as drawn".

    guard A / GUARD 1 -- dark cropped hair, tan wrap tunic, wide white waist
                         sash, wire-rim glasses
    guard B / GUARD 2 -- light sandy hair, cream short-sleeve shirt, white sash
                         over one shoulder, broad dark-brown wrap skirt; he
                         carries the bark board

NO EYEWEAR IN EITHER DRAFT, AND BOTH ARE TWO-GUARD FRAMES. Founder, 2026-08-17:
"draw the second man without glasses. we need to have control." The engine does
not have that control today -- `glasses` inside exactly one man's clause landed
on BOTH men at 5 of 5 legible two-guard renders, at seeds where hair and
garments separated cleanly -- and a separate lane owns that binding. So both
drafts omit eyewear entirely and the jobs that use them are DIAGNOSTIC RUNGS FOR
THE CAST FIX, NOT SHIPPING PLATES: guard A is missing his glasses in every frame
they draw, by design.

BEAT 10 IS THE PROP-OWNERSHIP RUNG, and it changes the instrument rather than the
noun. Four beat-10 plates on 2026-08-17 got count, world and cast right and lost
the board anyway: it went to guard A or to both men at 4 OF 4, with the board
clause written INSIDE guard B's own person clause and B named first. Hair and
garments bind to a person clause; A PROP DOES NOT -- it attaches to whichever
figure is drawn NEAREST. This draft stops fighting that law and uses it: guard B
is `the near one` and the board is in his clause, guard A is `the far one`. The
hand-occupying instrument that failed there (`hands behind his back` came back
as arms folded in front) is not retried here; `arms down` is the only pose term
on the far man.

BEAT 11 IS THE BEAT THE MISCASTING WAS FIRST RECORDED ON, WITH THE CAUSE THE
WRONG WAY ROUND. `beats.11.override_third_check_0815` logs "TOTAL IDENTITY
COLLAPSE AWAY FROM THE PLATE - the near guard's bald scalp fills in with dark
hair CONTINUOUSLY across f16-f21". The plate asked for bald; dark hair is what
guard A actually is; we recorded the render drifting TOWARD the approved cast as
the defect. Both men walk away with their backs turned, so HAIR IS THE ONLY CAST
ATTRIBUTE STILL LEGIBLE -- which is why `bald` was fatal here specifically.

TOKENS, on the real CLIP count of the string that gets sent, measured with
sd_prompt.negative_tokens through render_wave_goblin.check() -- not with
compress()'s prose estimator, which under-counts a comma-separated tag list by up
to 10 tokens and will report headroom while CLIP has already dropped the style
anchor. check() returned ZERO faults on both, including the `2boys` count tag
both blocks declare:

    beat 10  positive 77/77   negative 65/77
    beat 11  positive 74/77   negative 65/77

THE TOKEN TRADES, NAMED SO THEY ARE THE FIRST SUSPECTS AND NOT A MYSTERY LATER.
The style tail is the same 14-token `cinematic lighting, masterpiece, best
quality, very aesthetic` the other six carry, so it is NOT a variable and it is
NOT cut. Beat 10 sits exactly on the ceiling and paid for it three ways: the word
`behind` is gone from `hedgerow behind` (the sky still has its own noun, so the
vacancy law is satisfied by `pale sky above` rather than by a spatial operator),
`in tall grass` moved out of the lead clause to the world list, and GUARD A'S
WHITE WAIST SASH IS NOT NAMED AT ALL. That last one is a real omission and the
bar must not score it: a missing or merged sash on the far man in beat 10 is not
evidence of anything, because nothing asked for it. Beat 11 traded `wrap` out of
both garment names and `from the camera` out of the walk clause.

THE LAWS APPLIED. THE HAND LAW -- every hand in frame is specified: beat 10 gives
the near man `in both hands` and the far man `arms down`, and beat 11 gives both
men `arms swinging`. On beat 10 only the near man's hands were specified last
time and the far pair came back holding a bamboo pole at one seed and a duplicate
board at another, WITH `weapon` in the negative. THE VACANCY LAW, AND THAT THE
HOLE IS OFTEN ABOVE THE HORIZON -- both drafts give the upper third its own
positive noun, `pale sky above`, because a ground noun cannot fill a sky region
and a negation does not reach a hole at all. `horizon` is negated nowhere.

WHY `bald` APPEARS NOWHERE, INCLUDING IN A `no bald` CLAUSE. pipeline/canon.yaml
`ep2-guard-hair` forbids `\\bbald\\b` and `\\bbare heads?\\b` on beats 5, 6, 7, 9,
10 and 11, and a `no X` clause in a POSITIVE is how this path builds its negative,
so `no bald` would put the word in scope. Hair is named positively instead, which
is what the vacancy law wants anyway.
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
NEG = ("No girl, no child, no armor, no helmet, no knight, no white "
       "background, no plain background, no dark, no night. ")

DRAFTS = {
    10: ("Two guard men, the near one light sandy hair, cream shirt, brown "
         "skirt, holds a blank bark board in both hands, the far one dark "
         "cropped hair, tan tunic, arms down, tall grass, hedgerow, pale sky "
         "above, " + TAIL + NEG + FOOT),

    11: ("Two guard men walk away, backs turned, one with dark cropped hair, "
         "tan tunic, white sash, the other light sandy hair, cream shirt, "
         "brown skirt, arms swinging, tall grass, hedgerow ahead, pale sky "
         "above, " + TAIL + NEG + FOOT),
}

# Each payload goes at the END of its beat's block, i.e. immediately BEFORE the
# next beat's header. Anchors carry the following beat's `slug` so a bare `  11:`
# cannot match a stray line somewhere else in 350 KB.
ANCHORS = {
    10: "  11:\n    slug: they-leave\n",
    11: "  12:\n    slug: related\n",
}


def block(beat: int, text: str) -> str:
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
        # EVERY pre-existing key must be byte-identical -- the check that catches
        # an indentation slip swallowing a neighbouring draft, which a byte count
        # cannot see.
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

    backup = TARGET.with_suffix(".yaml.bak-guard-cast-b1011-0817")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(after_txt)
    print("\nbackup             %s" % backup.name)
    print("sha256 after       %s" % sha(TARGET))
    print("bytes  after       %d" % len(TARGET.read_bytes()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
