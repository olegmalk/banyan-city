#!/usr/bin/env python3
r"""Insert ONE new draft key into wave-drafts.yaml, additively, with a backup.

2026-08-15, pose-plate lane. The key is `authored_b04_crouch_plate`, the CROUCHED
staged pose that beats 03, 04, 07, 08 and 12 all start from. It is ADDITIVE: no
existing key is read, rewritten or reordered, and the file is edited as TEXT
(never a yaml round-trip) so the 350 KB of hand-written comments survive.

Refuses if the key already exists, so a second run cannot double-insert, and
refuses if beat 04's anchor key is missing, so it cannot land in the wrong block.

WHY THIS WORDING, clause by clause -- every one of these was learned by losing
renders, and the local dialect gate (render_wave_goblin.check) was run on it
before a byte was sent:

  "a lean wiry adult goblin man"  -- NOT "a small goblin boy". The founder's
      complaint is that he reads as a baby; "boy" and "small" are the words
      asking for one.
  "crouched on his heels"         -- a STARTING POSE, not a verb. Every beat-17
      plate written as "pushes himself up to standing" came back already
      standing, because a plate renders the action's END state.
  "a thin stem with two oversized leaves rising from the grass beside him"
      -- the plant gets a BODY. "two oversized leaves hanging above him" renders
      as leaves floating with no plant; the stem, its base and the leaf count
      have to be described as one object.
  "sky overhead"                  -- headroom. A plate that must permit a rise
      needs clear vertical space above the head or straightening puts the head
      through the frame edge.
  "no blush, no red cheeks"       -- the founder's own diagnosis of why he reads
      infantile. "no chibi, no big head, no baby face, no toddler" go with them.

TOKEN BUDGET, measured, not assumed: positive 75/77 and the style anchor
survives; negative 70/77 with `photorealistic` and `3d render` still at the
front, which is exactly what fell off the last time a negative overflowed.
"""
from __future__ import annotations

import shutil
import sys

KEY = "authored_b04_crouch_plate"
ANCHOR = "    authored_b04_adult: >-"
BLOCK = """    authored_b04_crouch_plate: >-
      A lean wiry adult goblin man, {{GOBLIN}}, crouched on his heels, a thin stem
      with two oversized leaves rising from the grass beside him, sky overhead.
      Medium full shot, bright morning light, cinematic lighting, detailed, newest,
      masterpiece, best quality, very aesthetic No girl, no chibi, no big head, no
      baby face, no toddler, no child, no blush, no red cheeks. No photorealism, no
      3D render look. 9:16 vertical, no text.
"""


def main(path: str) -> int:
    text = open(path, encoding="utf-8").read()
    if KEY in text:
        print("!! %s is already in %s -- refusing to insert it twice." % (KEY, path))
        return 3
    if text.count(ANCHOR) != 1:
        print("!! anchor %r appears %d times -- refusing to guess where beat 04 is."
              % (ANCHOR, text.count(ANCHOR)))
        return 4
    shutil.copy2(path, path + ".bak-before-crouch-plate-0815")
    out = text.replace(ANCHOR, BLOCK + ANCHOR, 1)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)
    print("inserted %s into %s (+%d bytes); backup at %s"
          % (KEY, path, len(out) - len(text), path + ".bak-before-crouch-plate-0815"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
