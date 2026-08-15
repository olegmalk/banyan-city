#!/usr/bin/env python3
"""The wave harness's count guard, and the ONE exemption added 2026-08-15.

THE GUARD. `render_wave_goblin.check` refuses a draft whose DERIVED Danbooru
count tag disagrees with the count its beat slot DECLARES. It is not decoration:
on 2026-08-14 it caught ep2-b06-plate-0815, whose draft opened "Two adult guard
men" under a `1boy` beat, before a frame was drawn.

THE EXEMPTION. An OBJECT-reference sheet — a prop drawn alone with `no people`
fenced, so nothing competes with it for the composition — has no person in it by
construction, so it derives no count tag and no beat slot in this file can ever
be satisfied by it (every slot declares a person, because every beat has one).
`object_sheet_variants` lets the author name, per variant, the drafts that
declare NO count.

WHAT THESE TESTS PIN, and each one is a way the exemption could rot into a hole:
  * an object sheet that derives nothing PASSES                       (the fix)
  * `1boy` declared, `2boys` derived, STILL FAILS               (the b06 catch)
  * a draft that merely OMITS the key gets NO exemption   (silence != a claim)
  * a declared object sheet that derives a person STILL FAILS
                                     (the exemption permits one outcome only)

Pure logic: `sd` is stubbed, so no CLIP tokenizer, no torch, no GPU, no box.
Run:  python3 pipeline/test_wave_count_guard.py
"""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))

import render_wave_goblin as wg

FAILURES = []


def check(name, cond):
    print(("  ok  " if cond else "FAIL  ") + name)
    if not cond:
        FAILURES.append(name)


# A guard beat exactly as beat 06 is written in wave-drafts.yaml: it declares a
# person, because the BEAT has one.
BEAT = {"slug": "the-clipboard", "kind": "guard", "tag": "1boy",
        "extra_neg": "guard", "gist": "clipboard"}

# Compressed strings that satisfy every OTHER assertion in check(), so the only
# fault any case here can produce is the count fault under test.
POS = "1boy, a guard in a brown tunic, masterpiece, best quality, very aesthetic"
NEG = "photorealistic, 3d render, text, watermark, blurry, realistic skin texture"


def _sd(derived_tag, pos=POS):
    """A stand-in for sd_prompt whose count_tag answers exactly what we ask."""
    return SimpleNamespace(
        compress=lambda _authored: (pos, []),
        beat_negative=lambda _base, _authored, _extra, warn=None: NEG,
        negative_tokens=lambda s: len(s.split()),
        count_tag=lambda _authored: derived_tag,
    )


def _faults(d, derived_tag, pos=POS):
    return wg.check(6, d, "an authored draft", _sd(derived_tag, pos),
                    verbose=False)["faults"]


def _count_faults(faults):
    return [f for f in faults
            if "COUNT TAG" in f or "declares NO count" in f]


# ------------------------------------------------- the fix: an object sheet passes
OBJ = "authored_barkboard_obj"
listed = dict(BEAT, object_sheet_variants=[OBJ])

sheet = wg.apply_variant_declaration(listed, OBJ)
check("a named object-sheet variant is flagged as declaring no count",
      sheet.get("declares_no_count") is True)

# The object sheet's own positive: a prop alone, no figure, so no count tag.
OBJ_POS = ("a flat rectangular writing board made of tree bark, object reference "
           "sheet, masterpiece, best quality, very aesthetic")
check("object sheet declaring no count, deriving no count, has NO faults",
      _faults(sheet, "", OBJ_POS) == [])

# --------------------------------------- the catch that must survive: 1boy vs 2boys
# ep2-b06-plate-0815, 2026-08-14: "Two adult guard men" under a 1boy beat slot.
check("declared 1boy but derived 2boys still FAILS",
      any("COUNT TAG" in f for f in _faults(BEAT, "2boys")))

# ...and it must still fail on a beat that HAS an object-sheet list, for a variant
# that is not on it. One exempt draft may not disarm the beat's other drafts.
other = wg.apply_variant_declaration(listed, "authored_b06_prop2")
check("an UNLISTED variant on a beat that has a list gets no exemption",
      "declares_no_count" not in other)
check("declared 1boy but derived 2boys still FAILS on a beat with a list",
      any("COUNT TAG" in f for f in _faults(other, "2boys")))

# ------------------------------------------- omission is not a declaration
# A draft that simply does not mention the key must be measured under the old
# rule, byte for byte — silence is not a claim to be an object sheet.
check("a variant absent from the list is not flagged",
      "declares_no_count" not in wg.apply_variant_declaration(BEAT, OBJ))
check("omitting the key: declared 1boy, derived nothing, still FAILS",
      any("COUNT TAG" in f for f in _faults(BEAT, "")))
check("an EMPTY object_sheet_variants list flags nothing",
      "declares_no_count" not in
      wg.apply_variant_declaration(dict(BEAT, object_sheet_variants=[]), OBJ))

# ------------------------------- the exemption permits ONE outcome: derived empty
check("declared object sheet that derives 1boy still FAILS",
      any("declares NO count" in f for f in _faults(sheet, "1boy")))
check("declared object sheet that derives 2boys still FAILS",
      any("declares NO count" in f for f in _faults(sheet, "2boys")))

# ------------------------------------------------------------------ hygiene
check("apply_variant_declaration does not mutate the beat it is given",
      "declares_no_count" not in listed)
check("the exemption is the only count fault an object sheet can raise",
      _count_faults(_faults(sheet, "1boy")) ==
      [f for f in _faults(sheet, "1boy") if "declares NO count" in f])

print(f"\n{len(FAILURES)} failure(s)")
for f in FAILURES:
    print("  - " + f)
sys.exit(1 if FAILURES else 0)
