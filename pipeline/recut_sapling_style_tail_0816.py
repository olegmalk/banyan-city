#!/usr/bin/env python3
"""Give nine sapling-canon drafts back their style anchor, by shortening the
one part of them that was never reaching the model anyway.

THE DEFECT, measured rather than reasoned about. `sd_prompt.compress()` drops
TRAILING SENTENCES until the prompt fits CLIP's 77 tokens:

    while len(sentences) > 1 and _token_estimate(...) > MAX_TOKENS:
        dropped.append(sentences.pop())

Every draft in this file is written in the house dialect: an ACTION sentence,
then a STYLE sentence, then the inline negatives. compress() strips the
negations, which leaves the style sentence last -- so the style sentence is the
FIRST thing the loop deletes, and `very aesthetic` lives at the end of it. Nine
drafts overflowed, nine lost their whole style sentence, and
render_wave_goblin.check() refused all nine on `STYLE ANCHOR MISSING`.

THE TRAP IN THE NUMBERS, said plainly because it is what kept this invisible
for a day: the headroom is computed AFTER the deletion. `check()` builds its row
with `pos_tok = negative_tokens(pos)` on the ALREADY-COMPRESSED text, so a log
prints "54/77" and "STYLE ANCHOR MISSING" in the same breath and the 23 tokens
of apparent headroom are the corpse of the sentence that was removed.

WHAT WAS ACTUALLY OVERSPENT. The style sentences carry far more than the
anchor:

    Static camera, medium shot, bright morning light, cinematic lighting,
    detailed, newest, masterpiece, best quality, very aesthetic

Of that, `masterpiece, best quality, very aesthetic` is the dialect anchor. The
rest -- camera, framing, light -- IS ALREADY NOT REACHING THE MODEL. It sits in
the sentence compress() deletes, so it has never appeared in a single rendered
prompt from any of these nine drafts. Deleting it from the draft removes wording
that was never sent and buys the anchor's survival with it. That is why this
pass touches the style tail and not the canon: there was slack, and none of it
was in the part anyone had ruled on.

THE REPLACEMENT IS PROVEN, NOT INVENTED. `Cinematic lighting, masterpiece, best
quality, very aesthetic` is byte-for-byte the style tail of
`authored_b18_scale_0816`, which fired as ep2-b18-scale-0816 on 2026-08-16,
rc=0, and whose sidecar records `positive_tokens: 70` with the anchor intact on
the box's real CLIP. It is the one style tail in this file that is known to
survive compression on the machine that matters.

THE FOUNDER'S CANON IS NOT TOUCHED. His ruling, 2026-08-16: "make sure it has 2
leafs and has a set height... dont make it double in size suddenly." Every
two-leaf clause and every height relation in the nine survives this pass
byte-identical -- the script asserts it below rather than claiming it. ONE
draft, `authored_b01_scale_0816`, was still four tokens over after the style cut
and needed a second: ` with soft round tips` comes off. That is leaf SHAPE, not
leaf COUNT, and the shape is separately defended in that draft's own negatives
(`no lobed leaves, no five-fingered leaves`). The count clause `exactly two wide
oval cotyledon leaves` and the relation `no taller than the grass around it`
both stay.

HOW IT IS EDITED. As TEXT, in the house pattern of
insert_sapling_canon_drafts_0816.py and fix_b19_bounce_0816.py: sha256 before
and after, a backup, a byte delta ASSERTED equal to the sum of the intended
changes, and a parsed-variant diff proving exactly which keys moved and that
nothing else in 350 KB did. A YAML round-trip would reflow every comment in the
file and this file IS its comments.

    python3 pipeline/recut_sapling_style_tail_0816.py [pipeline/wave-drafts.yaml]
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
import textwrap

SUFFIX = ".bak-recut-style-tail-0816"

# The style tail that is known to survive compression on the box's real CLIP.
PROVEN_TAIL = "Cinematic lighting, masterpiece, best quality, very aesthetic"

# Everything from the start of the style sentence through `very aesthetic`,
# matched on the JOINED value (the file wraps it across five lines). The lead-in
# varies per draft -- "Static camera, medium shot, bright morning light",
# "Held macro, even front light, the sun behind the camera", "Deadpan comedic
# staging, static camera, medium shot" -- so it is matched rather than listed.
STYLE_SENTENCE = re.compile(
    r"(?<=[.]\s)[^.]*?cinematic lighting, detailed, newest, "
    r"masterpiece, best quality, very aesthetic",
    re.I)

# beat -> key. The nine render_wave_goblin.check() refused on STYLE ANCHOR
# MISSING, and no others: b07/b13/b21 scale drafts and b18_scale_0816 already
# fit and are not opened here.
TARGETS = [
    (1,  "authored_b01_scale_0816"),
    (1,  "authored_b01_canon_0816"),
    (2,  "authored_b02_scale_0816"),
    (2,  "authored_b02_plate_scale_0816"),
    (3,  "authored_b03_scale_0816"),
    (3,  "authored_b03_plate_scale_0816"),
    (17, "authored_b17_scale_0816"),
    (17, "authored_b17_plate_scale_0816"),
    (18, "authored_b18_figleaf_canon_0816"),
]

# The one draft that needed a second cut, and exactly what comes off it.
EXTRA_CUT = {"authored_b01_scale_0816": " with soft round tips"}

# What must survive in every draft that carried it. The founder ruled BOTH; a
# pass that saved tokens by quietly losing one would be the failure this file
# exists to stop, so it is asserted per key rather than trusted.
CANON_COUNT = re.compile(r"exactly two\b|two big leaves|two broad round cotyledon leaves")
CANON_HEIGHT = re.compile(r"no taller than the grass around it|knee high")

WRAP = 88
INDENT = "      "


def block_bounds(lines: list, key: str) -> tuple:
    """(start, end) line indices of `key:`'s folded scalar, header included."""
    head = "    %s: >-" % key
    starts = [i for i, l in enumerate(lines) if l.rstrip("\n") == head]
    if len(starts) != 1:
        raise SystemExit("!! %s: header appears %d times -- refusing to guess."
                         % (key, len(starts)))
    i = starts[0]
    j = i + 1
    while j < len(lines) and lines[j].startswith(INDENT) and lines[j].strip():
        j += 1
    return i, j


def joined(lines: list, i: int, j: int) -> str:
    return " ".join(l.strip() for l in lines[i + 1:j])


def rewrapped(key: str, value: str) -> str:
    body = textwrap.fill(value, width=WRAP, initial_indent=INDENT,
                         subsequent_indent=INDENT, break_long_words=False,
                         break_on_hyphens=False)
    return "    %s: >-\n%s\n" % (key, body)


def parsed(text: str) -> dict:
    import yaml
    d = yaml.safe_load(text)
    beats = d.get("beats", d)
    flat = {}
    for beat, body in beats.items():
        if isinstance(body, dict):
            for k, v in body.items():
                flat["%s.%s" % (beat, k)] = v
    return flat


def main(path: str = "pipeline/wave-drafts.yaml") -> int:
    text = open(path, encoding="utf-8").read()
    before = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print("sha256 before: %s  (%d bytes)" % (before, len(text)))

    flat_before = parsed(text)
    lines = text.splitlines(keepends=True)

    edits = []   # (label, old_block, new_block)
    for beat, key in TARGETS:
        i, j = block_bounds(lines, key)
        old_block = "".join(lines[i:j])
        value = joined(lines, i, j)

        if PROVEN_TAIL + " No" not in value and not STYLE_SENTENCE.search(value):
            print("!! %s: no long style sentence found -- refusing to guess." % key)
            return 4
        new_value, n = STYLE_SENTENCE.subn(PROVEN_TAIL, value)
        if n != 1:
            print("!! %s: style sentence matched %d times, expected 1." % (key, n))
            return 4
        cut = EXTRA_CUT.get(key)
        if cut:
            if new_value.count(cut) != 1:
                print("!! %s: extra cut %r appears %d times."
                      % (key, cut, new_value.count(cut)))
                return 4
            new_value = new_value.replace(cut, "", 1)

        # The two clauses the founder ruled on must come through untouched.
        for name, rx in (("two-leaf", CANON_COUNT), ("height", CANON_HEIGHT)):
            was, now = rx.search(value), rx.search(new_value)
            if bool(was) != bool(now) or (was and was.group(0) != now.group(0)):
                print("!! %s: the %s clause did not survive -- refusing to write."
                      % (key, name))
                return 5
        if "very aesthetic" not in new_value:
            print("!! %s: the anchor is not in the result." % key)
            return 5

        edits.append((key, old_block, rewrapped(key, new_value)))

    for key, old_block, _ in edits:
        if text.count(old_block) != 1:
            print("!! %s: block is not unique in the file." % key)
            return 4

    shutil.copy2(path, path + SUFFIX)

    out, delta = text, 0
    for key, old_block, new_block in edits:
        out = out.replace(old_block, new_block, 1)
        delta += len(new_block) - len(old_block)
    if len(out) - len(text) != delta:
        print("!! byte delta %d != intended %d -- a replace() ate something. "
              "NOT writing; the backup is the only clean copy."
              % (len(out) - len(text), delta))
        return 6

    # PARSED-VARIANT DIFF. Comments do not survive the parse, which is the
    # point: this checks the payload, the byte delta checks the prose.
    flat_after = parsed(out)
    changed = sorted(k for k in set(flat_before) | set(flat_after)
                     if flat_before.get(k) != flat_after.get(k))
    expected = sorted("%d.%s" % (b, k) for b, k in TARGETS)
    print("parsed keys before/after: %d / %d" % (len(flat_before), len(flat_after)))
    print("changed keys (%d): %s" % (len(changed), ", ".join(changed) or "NONE"))
    if changed != expected:
        print("!! expected exactly the nine targets -- refusing to write.")
        return 7

    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)
    after = hashlib.sha256(out.encode("utf-8")).hexdigest()
    print("sha256 after:  %s  (%d bytes, %+d)" % (after, len(out), delta))
    print("backup:        %s%s" % (path, SUFFIX))
    print("\nNOTHING IS FILEABLE ON THIS EVIDENCE ALONE. The numbers behind this "
          "pass are sd_prompt's ESTIMATE, which reads ~5%% high and drops "
          "different sentences than the box does. Verify on the card's real CLIP "
          "before any of the nine is enqueued:\n"
          "  ssh rtx5090 ... render_wave_goblin.py --root <repo> --dry")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "pipeline/wave-drafts.yaml"))
