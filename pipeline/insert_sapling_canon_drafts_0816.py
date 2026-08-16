#!/usr/bin/env python3
r"""Insert the four SAPLING-CANON draft keys into wave-drafts.yaml, additively.

2026-08-16, sapling-canon lane, against the founder's ruling of the same day:

    "alright, lets be a bit more strict with the sapling. make sure it has 2
    leafs and has a set height, height might be a bit hard for the ai to make
    exact, so dont go crazy on it, just dont make it double in size suddenly"

The canon those words became is `genomes/sapling/THE-SAPLING.md`. This script is
the PROPAGATION half: four replacement drafts that say what the plant is, so the
next job that needs beat 01 or beat 18 can pick a draft that is on canon instead
of one of the ten that are not.

ADDITIVE, exactly as `insert_b04_crouch_plate_0815.py` is: no existing key is
read back, rewritten or reordered, the file is edited as TEXT (never a yaml
round-trip, because 421 KB of hand-written provenance would not survive one),
the byte delta is asserted to be pure insertion, and a backup is written first.
Refuses if any key already exists, so a second run cannot double-insert, and
refuses if an anchor is missing or ambiguous so a block cannot land on the wrong
beat.

FOUR KEYS FOR TWELVE SUPERSEDED DRAFTS, not twelve for twelve. The superseded
drafts differ from each other in LIGHTING and FRAMING rounds that were all won
honestly; they differ from canon in exactly two clauses each. One replacement per
(beat, shot-kind) keeps the correction legible and does not fork ten lighting
decisions that nobody has revisited.

WHAT EACH CLAUSE FIXES, and the superseded wording it replaces:

  "exactly two wide oval cotyledon leaves with soft round tips"
      replaces `deeply lobed fig leaves with five fingers` (b01/b18 figleaf*,
      figlit) and `only three or four leaves` (b01 authored, b01_t2i_fig).
      TWO is his ruling. OVAL is steward INFERENCE from it, flagged in
      THE-SAPLING.md §2.2 and vetoable in one line: a two-leaf plant at ~40 cm
      is a cotyledon-stage seedling and cotyledons are round, while deeply lobed
      five-fingered leaves are mature-tree foliage that cannot co-exist with a
      two-leaf seedling.

  "no lobed leaves, no five-fingered leaves, no three leaves, no four leaves"
      replaces the negative `no simple oval leaves`, which is the exact inverse
      of the canon and was banning the thing we now want.

  "one small purple fig ... deep purple-violet, green at its neck, matte"
      replaces `one small round green fig` / `ONE SINGLE ROUND GREEN FIG`. His
      2026-08-13/14 ruling made the fig purple and his 2026-08-16 ruling kills
      red; NEITHER names green, which is how green survived both by omission.
      The wording is not new: it is byte-copied from `authored_b18_scene` /
      `authored_b19_scene` / `authored_b20_scene`, the three drafts the purple
      ruling was actually written into, so this adds no fourth dialect.

  "no green fig, no green fruit"
      the negative that makes the above stick. Already present on b18_scene,
      b19_scene and b20_scene; absent from every draft corrected here.

WHAT IS DELIBERATELY NOT TOUCHED:

  * HEIGHT WORDING. `standing tall` (nine drafts) is POSTURE, not height —
    ledgered in taste/steward-model.v1.md A7: "'Reads tall' is about how the
    subject sits in the FRAME, not about the character's stated size." Beat 02
    writes both at once ("a tiny 40cm mascot-simple sapling standing tall").
    Rewriting nine drafts for no defect is the cry-wolf pattern that got the
    runner watchdog switched off for four days. The one wording that DOES break
    his ruling, `taller than he is`, is not in this file at all — it lives only
    in six already-fired job spec payloads (THE-SAPLING.md §6.1).
  * FRUIT SHAPE. `round` vs `teardrop` is live and unresolved and belongs to the
    fig lane, not here. The purple clause carries whatever shape word its source
    draft carried.
  * THE STEM. Five different descriptions are live; the founder ruled on none of
    them, so none is invented (THE-SAPLING.md §4).
  * LIGHTING. Each replacement keeps its source round's light verbatim.

DIALECT: every block ends on the style anchor `very aesthetic`, negates `text`,
says `no humans` nowhere, and uses the person-SINGULARS block — which is the
correct defence here and not a self-negation, because beats 01 and 18 are
plant-only and declare nobody in frame. Positive and negative are well inside
LTX's 1024-token encode budget (pipeline/prompt_budget.py); the longest block
below is under 120 words.
"""
from __future__ import annotations

import hashlib
import shutil
import sys

SUFFIX = ".bak-before-sapling-canon-0816"

# (key, anchor, block). Anchors are the LAST canon-contradicting draft of each
# beat, so the replacement lands immediately above the round it supersedes.
INSERTS = [
    (
        "authored_b01_canon_0816",
        "    authored_b01_figlit: >-",
        """    # -- `authored_b01_canon_0816` -- 2026-08-16, THE SAPLING CANON.
    # Supersedes `authored` and `authored_b01_t2i_fig` on this beat, which ask for
    # `one small round green fig` and `only three or four leaves`. Both clauses are
    # now defects: he ruled TWO leaves on 2026-08-16 and the fig has been purple
    # since 08-13/14. Whole-plant framing and morning light are unchanged from the
    # drafts this replaces. See genomes/sapling/THE-SAPLING.md.
    authored_b01_canon_0816: >-
      A tiny fig seedling in an open grassy field, exactly two wide oval cotyledon
      leaves with soft round tips, and one small deep purple-violet fig, green at its
      neck, matte, growing on its thin stem, whole plant in frame. Static camera,
      medium shot, bright morning light, cinematic lighting, detailed, newest,
      masterpiece, best quality, very aesthetic No woman, no girl, no boy, no child,
      no person, no chibi, no mascot, no creature, no face, no green fig, no green
      fruit, no red fruit, no white fruit, no pale fruit, no lobed leaves, no
      five-fingered leaves, no three leaves, no four leaves, no many leaves, no lush
      foliage, no dark, no night. No photorealism, no 3D render look. 9:16 vertical,
      no text.
""",
    ),
    (
        "authored_b01_figleaf_canon_0816",
        "    authored_b01_figleaf3: >-",
        """    # -- `authored_b01_figleaf_canon_0816` -- 2026-08-16, THE SAPLING CANON.
    # Supersedes `authored_b01_figleaf`, `_figleaf2`, `_figleaf3` and `_figlit`, all
    # four of which ask for `deeply lobed fig leaves with five fingers` and ban
    # `no simple oval leaves`. That is the exact inverse of the canon: a two-leaf
    # plant is a cotyledon-stage seedling and lobed five-fingered leaves are
    # mature-tree foliage. The FRUIT wording and the front-lit fix that `_figlit`
    # bought (backlight and silhouette banned by name, nine rounds were judged on
    # silhouettes) are carried across byte-for-byte -- only the leaf clauses move.
    authored_b01_figleaf_canon_0816: >-
      A tiny fig seedling in a sunlit grassy field, exactly two wide oval cotyledon
      leaves with soft round tips, and hanging below them one small purple fig, a
      plain purple teardrop of fruit with matte dusty skin. Medium shot, even front
      light, the sun behind the camera, cinematic lighting, detailed, newest,
      masterpiece, best quality, very aesthetic No backlight, no silhouette, no
      contre-jour, no lens flare, no face, no eyes, no creature, no mascot, no chibi,
      no person, no girl, no boy, no child, no eggplant, no aubergine, no gloss, no
      shine, no black fruit, no green fig, no green fruit, no lobed leaves, no
      five-fingered leaves, no three leaves, no four leaves, no stem crossing the
      fruit, no dark, no night. No photorealism, no 3D render look. 9:16 vertical,
      no text.
""",
    ),
    (
        "authored_b18_canon_0816",
        "    authored_b18_figlit: >-",
        """    # -- `authored_b18_canon_0816` -- 2026-08-16, THE SAPLING CANON.
    # Supersedes `authored`, `authored_b18_plantneg` and `authored_b18_refresh`, all
    # three of which ask for a GREEN fig positively. His purple ruling (08-13/14) and
    # his red ruling (08-16) both leave green standing by not naming it; it is named
    # here. The macro framing, the flexing stem and the amber light are unchanged.
    authored_b18_canon_0816: >-
      A single small deep purple-violet fig, green at its neck, matte, on the
      thinnest branch of a tiny sapling, the only fruit in frame, its stem flexing
      under the weight, warm amber afternoon light against a soft wash sky. Held
      macro, extreme close-up, cinematic lighting, detailed, newest, masterpiece,
      best quality, very aesthetic No second fruit, no two fruit, no apple, no green
      fig, no green fruit, no red fruit, no white fruit, no pale fruit, no woman, no
      girl, no boy, no child, no person, no chibi, no mascot, no creature, no face,
      no sketch lines, no dashed outline, no thick branch. No photorealism, no 3D
      render look. 9:16 vertical, no text.
""",
    ),
    (
        "authored_b18_figleaf_canon_0816",
        "    authored_b18_figleaf3: >-",
        """    # -- `authored_b18_figleaf_canon_0816` -- 2026-08-16, THE SAPLING CANON.
    # Supersedes `authored_b18_figleaf2`, `_figleaf3` and `_figlit` on this beat,
    # which carry the same `deeply lobed fig leaves with five fingers` positive and
    # `no simple oval leaves` negative as their beat-01 twins. Same correction, same
    # reason; the held-macro framing and the front light are carried across.
    authored_b18_figleaf_canon_0816: >-
      A tiny fig sapling's thinnest branch against a soft sky, exactly two wide oval
      cotyledon leaves with soft round tips, and hanging below them one small purple
      fig, a plain purple teardrop of fruit with matte dusty skin. Held macro, even
      front light, the sun behind the camera, cinematic lighting, detailed, newest,
      masterpiece, best quality, very aesthetic No backlight, no silhouette, no
      contre-jour, no face, no eyes, no creature, no mascot, no chibi, no person, no
      girl, no boy, no child, no eggplant, no aubergine, no gloss, no shine, no black
      fruit, no green fig, no green fruit, no lobed leaves, no five-fingered leaves,
      no three leaves, no four leaves, no stem crossing the fruit, no dark, no night.
      No photorealism, no 3D render look. 9:16 vertical, no text.
""",
    ),
]


def main(path: str) -> int:
    text = open(path, encoding="utf-8").read()
    before = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print("sha256 before: %s  (%d bytes)" % (before, len(text)))

    for key, anchor, _ in INSERTS:
        if key in text:
            print("!! %s is already in %s -- refusing to insert it twice." % (key, path))
            return 3
        if text.count(anchor) != 1:
            print("!! anchor %r appears %d times -- refusing to guess where it goes."
                  % (anchor, text.count(anchor)))
            return 4

    shutil.copy2(path, path + SUFFIX)
    out, added = text, 0
    for key, anchor, block in INSERTS:
        out = out.replace(anchor, block + anchor, 1)
        added += len(block)

    # PURE INSERTION, asserted rather than trusted. Any other delta means a
    # replace() ate something and the backup is the only copy left.
    if len(out) - len(text) != added:
        print("!! byte delta %d != inserted %d -- NOT pure insertion, refusing to write."
              % (len(out) - len(text), added))
        return 5

    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)
    after = hashlib.sha256(out.encode("utf-8")).hexdigest()
    print("sha256 after:  %s  (%d bytes, +%d)" % (after, len(out), added))
    print("inserted: %s" % ", ".join(k for k, _, _ in INSERTS))
    print("backup:   %s%s" % (path, SUFFIX))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "pipeline/wave-drafts.yaml"))
