#!/usr/bin/env python3
"""Add beat 01's geometry-vs-number rung to wave-drafts.yaml, additively.

    python3 pipeline/insert_b01_geom_0817.py            # check only
    python3 pipeline/insert_b01_geom_0817.py --apply

WHY A SCRIPT AND NOT AN EDITOR. `pipeline/wave-drafts.yaml` is the file the box
reads every prompt out of, lanes are live in this worktree, and its drafts are
FOLDED SCALARS -- the one shape where a hand edit can look perfect and mean
something else. A lane's first anchor here once would have written 26 lines
INSIDE a folded scalar with a byte delta that matched its payload exactly; only
a parsed diff caught it. So this follows the house pattern
(`insert_b0708_figure_count_0817.py`, `insert_sapling_canon_drafts_0816.py`):
sha256 before and after, a byte delta asserted against the exact payload, a
backup, and a PARSED-VARIANT DIFF. Never a YAML round-trip.

ONE EXTRA ASSERTION THIS FILE ADDS, and it is the one that matters for a folded
scalar: the parsed value of the new key is compared CHARACTER FOR CHARACTER
against EXPECTED -- the exact string that was measured on the real CLIP. Folding
joins lines with spaces, so a line break in the wrong column changes the prompt
the box sends while leaving the YAML valid and the byte count right. A token
measurement of a string that is not the string that ships is not evidence.

THE EXPERIMENT. Control is `authored_b01_scale_0816`, left standing byte-
identical, rendered by `pipeline/jobs/ep2-b01-scale-0817.yaml` over 16 stills
(4 reference cells x 4 seeds). ONE VARIABLE changes: the cardinality assertion
`exactly two` is replaced by a description of the same pair's GEOMETRY,
`opposed one either side of the stem`. Everything else -- the purple fig
clauses, the scale relation `no taller than the grass around it`, the style
tail and the ENTIRE negative including `no three leaves, no four leaves, no
many leaves` -- is byte-identical to the control.

WHY GEOMETRY. `exactly two` is running 3 of 8 across the plant-only wave sheets
(beat 21's 2 of 4 plus beat 12's 1 of 4), and the cause is settled outside this
repo: CLIP's text embeddings are near-identical across numerals, so a number
barely reaches the conditioning (T2ICountBench, arXiv 2503.06884; full read in
pipeline/research/count-control-sdxl-0817.md). Nobody has published exact count
control on SDXL. Meanwhile the fig-SHAPE clause landed a correct teardrop 1 of 1
on a plate that contained no fig at all -- the wording CREATED the geometry
rather than reshaping a wrong one. So the question is whether a relation the
encoder does represent (opposition, one on each side of a named stem) binds
where a cardinality it does not represent has been losing.

THE PHRASING WAS CHOSEN AGAINST THE HYPOTHESIS, NOT FOR THE TOKEN COUNT. Seven
candidates were measured; all seven fit. `a pair of ...` was REJECTED even
though it fits, because `pair` is another lexical route to a cardinality and a
win with it would not distinguish "geometry binds" from "the numeral was the
problem". The chosen wording asserts no total at all: `opposed` is the relation
and `one either side of the stem` is a distributive placement, not a count of
leaves in the frame.

MEASURED ON THE REAL TOKENIZER before this file was written --
openai/clip-vit-large-patch14 through sd_prompt.compress + negative_tokens, the
same two functions render_wave_goblin.check() calls:

    control  authored_b01_scale_0816   68/77  headroom 9  DROPPED none  ANCHOR True
    this     authored_b01_geom_0817    73/77  headroom 4  DROPPED none  ANCHOR True

The control figure REPRODUCES the 68/77 that ep2-b01-scale-0817.yaml recorded
from the box's own CLIP, which is how we know both rows are measured the same
way. The fallback estimator is not used anywhere here: it changes verdicts and
not merely numbers, because compress() sheds the tail and then the draft is
faulted for what it shed. The first geometry wording tried was longer and did
exactly that -- 67/77 with STYLE ANCHOR PRESENT: False, the tail silently gone.
It was discarded, not trimmed into looking fine.

COLOUR: the green trap does not apply. This lineage is already purple -- `one
small deep purple-violet fig` in the positive and `no green fig, no green fruit`
in the negative, both inherited byte-identical. Nothing green is propagated.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "pipeline" / "wave-drafts.yaml"
KEY = "authored_b01_geom_0817"

# The last two lines of `authored_b01_scale_0816` plus the line that opens beat
# 2. Matching the beat-2 line as part of the anchor is what proves we are at the
# END of beat 1's block and not inside some other draft that happens to end the
# same way.
ANCHOR = """      foliage, no dark, no night. No photorealism, no 3D render look. 9:16 vertical, no
      text.
  2:
"""

ADD = """    # -- `authored_b01_geom_0817` -- 2026-08-17, geometry-vs-number rung.
    # DERIVED FROM `authored_b01_scale_0816`, WHICH IS LEFT STANDING BYTE-IDENTICAL and is
    # the control: it is the draft `pipeline/jobs/ep2-b01-scale-0817.yaml` renders over 16
    # stills, so the comparison is against a wording someone is already watching.
    # ONE VARIABLE. `exactly two wide oval cotyledon leaves` becomes `wide oval cotyledon
    # leaves opposed one either side of the stem`. The count assertion is gone; the same
    # pair is described by its geometry instead. Every other clause -- the purple fig, the
    # scale relation `no taller than the grass around it`, the style tail and the WHOLE
    # negative -- is byte-identical to the control, including `no three leaves, no four
    # leaves, no many leaves`, which stay because dropping them would be a second variable.
    # WHY: `exactly two` runs 3 of 8 across the plant-only wave sheets and CLIP's embeddings
    # are near-identical across numerals (T2ICountBench, arXiv 2503.06884), while the
    # fig-shape clause landed a correct teardrop 1 of 1 on a plate with no fig in it. Shape
    # language binds where count language does not; this asks whether that carries to leaves.
    # `a pair of ...` measured fine and was REJECTED on purpose: `pair` is another way of
    # saying two, and a win with it would not tell geometry from lexis.
    # REAL CLIP (openai/clip-vit-large-patch14, sd_prompt.compress + negative_tokens):
    # 73/77, headroom 4, POSITIVE DROPPED: none, STYLE ANCHOR PRESENT: True. Control on the
    # same harness: 68/77, reproducing the figure ep2-b01-scale-0817 took from the box.
    # FAILURE IS REACHABLE: `whole plant in frame` keeps the whole stem in shot, so a third
    # leaf -- or a second opposed pair further up -- can appear and be counted against this.
    authored_b01_geom_0817: >-
      A tiny fig seedling in an open grassy field, wide oval cotyledon leaves opposed one
      either side of the stem, and one small deep purple-violet fig, green at its neck,
      matte, growing on its thin stem, whole plant in frame, no taller than the grass
      around it. Cinematic lighting, masterpiece, best quality, very aesthetic No woman,
      no girl, no boy, no child, no person, no chibi, no mascot, no creature, no face, no
      green fig, no green fruit, no red fruit, no white fruit, no pale fruit, no lobed
      leaves, no five-fingered leaves, no three leaves, no four leaves, no many leaves, no
      lush foliage, no dark, no night. No photorealism, no 3D render look. 9:16 vertical,
      no text.
"""

# The string that was measured on the real CLIP. The parsed value of KEY must
# equal this exactly or the fold moved a word and the measurement is void.
EXPECTED = (
    "A tiny fig seedling in an open grassy field, wide oval cotyledon leaves "
    "opposed one either side of the stem, and one small deep purple-violet fig, "
    "green at its neck, matte, growing on its thin stem, whole plant in frame, "
    "no taller than the grass around it. Cinematic lighting, masterpiece, best "
    "quality, very aesthetic No woman, no girl, no boy, no child, no person, no "
    "chibi, no mascot, no creature, no face, no green fig, no green fruit, no "
    "red fruit, no white fruit, no pale fruit, no lobed leaves, no five-fingered "
    "leaves, no three leaves, no four leaves, no many leaves, no lush foliage, "
    "no dark, no night. No photorealism, no 3D render look. 9:16 vertical, no "
    "text."
)

CONTROL_KEY = "authored_b01_scale_0816"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build(text: str) -> str:
    n = text.count(ANCHOR)
    if n != 1:
        sys.exit("!! anchor matches %d times, expected 1. Refusing." % n)
    if KEY in text:
        sys.exit("!! `%s` is ALREADY in the file. Refusing to double-insert." % KEY)
    if not text.endswith("\n"):
        sys.exit("!! target does not end in a newline; refusing.")
    # The addition goes BEFORE the `  2:` line that closes beat 1's block.
    head = ANCHOR[: -len("  2:\n")]
    return text.replace(ANCHOR, head + ADD + "  2:\n", 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    import yaml  # noqa: E402

    before_txt = TARGET.read_text()
    before = yaml.safe_load(before_txt)
    after_txt = build(before_txt)

    delta = len(after_txt.encode()) - len(before_txt.encode())
    exp = len(ADD.encode())
    print("sha256 before      %s" % sha(TARGET))
    print("bytes  before      %d" % len(before_txt.encode()))
    print("byte delta         %d   (expected %d)" % (delta, exp))
    if delta != exp:
        sys.exit("!! byte delta != payload. Something other than an insert happened.")

    after = yaml.safe_load(after_txt)

    # ---- PARSED-VARIANT DIFF ------------------------------------------------
    if set(before) != set(after):
        sys.exit("!! top-level keys changed: %s" % (set(before) ^ set(after)))
    for k in before:
        if k == "beats":
            continue
        if before[k] != after[k]:
            sys.exit("!! top-level %r changed." % k)
    if set(before["beats"]) != set(after["beats"]):
        sys.exit("!! the set of beats changed. Refusing.")

    for b in before["beats"]:
        add = set(after["beats"][b]) - set(before["beats"][b])
        rem = set(before["beats"][b]) - set(after["beats"][b])
        if rem:
            sys.exit("!! beat %s lost keys: %s" % (b, sorted(rem)))
        if b != 1:
            if before["beats"][b] != after["beats"][b]:
                sys.exit("!! beat %s changed and should not have." % b)
            continue
        if add != {KEY}:
            sys.exit("!! beat 1 additions are %s, expected exactly {%r}"
                     % (sorted(add), KEY))
        for k in before["beats"][b]:
            if before["beats"][b][k] != after["beats"][b][k]:
                sys.exit("!! beat 1 key %r was modified. Refusing." % k)
    print("beat 1  added      ['%s']" % KEY)
    print("beat 1  existing keys all byte-identical (incl. the control)")
    print("all other beats    unchanged")

    # ---- THE FOLD CHECK -----------------------------------------------------
    got = after["beats"][1][KEY]
    if got != EXPECTED:
        for i, (x, y) in enumerate(zip(got, EXPECTED)):
            if x != y:
                sys.exit("!! parsed value diverges from the measured string at "
                         "char %d: got %r want %r\n   got:  ...%s...\n   want: ...%s..."
                         % (i, x, y, got[max(0, i - 40):i + 40],
                            EXPECTED[max(0, i - 40):i + 40]))
        sys.exit("!! parsed value length %d != measured length %d"
                 % (len(got), len(EXPECTED)))
    print("parsed value       == the string measured on the real CLIP (%d chars)"
          % len(got))

    # The one variable, proved rather than asserted.
    ctrl = after["beats"][1][CONTROL_KEY]
    if ctrl.replace("exactly two wide oval cotyledon leaves",
                    "wide oval cotyledon leaves opposed one either side of the stem",
                    1) != got:
        sys.exit("!! this draft is NOT the control with only the count phrase "
                 "swapped. More than one variable moved.")
    print("one-variable proof  control with ONLY the count phrase swapped -> this draft")

    if not a.apply:
        print("\n--check only: nothing written. Re-run with --apply.")
        return 0

    backup = TARGET.with_suffix(".yaml.bak-b01-geom-0817")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(after_txt)
    print("\nbackup             %s" % backup.name)
    print("sha256 after       %s" % sha(TARGET))
    print("bytes  after       %d" % len(TARGET.read_bytes()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
