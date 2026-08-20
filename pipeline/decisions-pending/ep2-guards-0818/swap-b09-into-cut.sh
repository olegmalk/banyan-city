#!/usr/bin/env bash
# PRE-STAGED. Fires on the founder answering "pass" (or "stage") to
# /review/ep2-guards-0818. Until then this file is written and NOT run.
#
# What it does: puts beat 09's passing cropmotion clip into the episode-2 demo
# cut, taking the cut from 19 footage / 2 slates to 20 footage / 1 slate.
#
# Why it needs a human word first: the clip's own spec pre-registered
# `is_show_content: false` because it inherits the plate's cast frame for frame
# and the adolescent read was an open R4 card. That card IS this decision.
#
# $0. No render, no GPU, no network beyond git.
set -euo pipefail
cd "$(dirname "$0")/../../.."   # repo root
REPO="$PWD"
CUT=review/ep2-demo-0820
SRC=farm-out/ep2-b09-cropmotion-0820
CLIP=09-the-pause-LTX-ep2-b09-cropmotion-0820.mp4
CLIP_SHA=247ecf6ca592127642ecf1f37c28b54fea327b5e992b3264ad505169f7e7d5ea

say() { printf '\n=== %s\n' "$*"; }

say "0. preconditions -- assert, do not trust"
test -f "$SRC/$CLIP"      || { echo "!! clip missing: $SRC/$CLIP"; exit 1; }
test -d "$CUT/sources"    || { echo "!! cut sources dir missing: $CUT/sources"; exit 1; }
have=$(shasum -a 256 "$SRC/$CLIP" | cut -d' ' -f1)
[ "$have" = "$CLIP_SHA" ] || { echo "!! clip sha mismatch
   want $CLIP_SHA
   have $have"; exit 1; }
# THE get_clip() TRAP: it globs NN-*.mp4 and takes the sorted FIRST. An old file
# left beside the new one is a coin flip, not a swap. Beat 09 is a slate today so
# there should be nothing -- assert it rather than assume it.
existing=$(find "$CUT/sources" -maxdepth 1 -name '09-*.mp4' | sort)
if [ -n "$existing" ]; then
  echo "!! there is already a 09-*.mp4 in the cut:"; echo "$existing"
  echo "   DELETE it (and its .meta.yaml, and its row in picks) before swapping."
  echo "   Leaving both is a filename-ordering coin flip, not a swap."
  exit 1
fi
# VO must already be there; this swap does not synthesise or copy audio.
test -f "$CUT/sources/09-vo.mp3"  || { echo "!! 09-vo.mp3 missing from the cut"; exit 1; }
test -f "$CUT/sources/09-vo.json" || { echo "!! 09-vo.json missing from the cut"; exit 1; }
echo "ok: clip verified, no rival 09-*.mp4, VO already in place"

say "1. copy the clip AND its provenance sidecar into the cut's --clips dir"
cp "$SRC/$CLIP" "$SRC/$CLIP.meta.yaml" "$CUT/sources/"

say "2. re-assemble. --out = bench mode: no leaf, no lineage.yaml, not canon"
python3 pipeline/render_t3.py sapling 002b \
  --clips "$CUT/sources" \
  --out   "$CUT/ep2-demo-0820.mp4"

say "3. re-extract proof frames + the git-derived ledger"
python3 pipeline/proof_receipts.py --write

say "4. force-add past .gitignore:50-59 (review/**/*.mp4, *.jpg)"
# build_site publishes ONLY what git tracks. Untracked media = broken links =
# qa_local failure. This is how the beat-03 swap failed on its first attempt.
git add -f "$CUT/sources/$CLIP" \
           "$CUT/ep2-demo-0820.mp4" \
           "$CUT"/proof/*.jpg
git add    "$CUT/sources/$CLIP.meta.yaml" \
           "$CUT/ep2-demo-0820.mp4.meta.yaml" \
           "$CUT/proof/frames.yaml" \
           pipeline/measured/proof-ledger.json

say "5. THE HAND EDITS -- this script cannot write these and must not pretend to"
cat <<'EDITS'
  Still to do by hand, before the commit:

  a) review/ep2-demo-0820/sources/picks-0820.yaml -- the beat-09 row (~line 549).
     take: null / why: slate  ->  the take, its sha256, why: new, the verdict
     quoted from pipeline/jobs/ep2-b09-cropmotion-0820.yaml, and a
     `how_to_reverse_it_in_one_line:` in the house idiom.
     NAME THE HAND DEFECT IN THE ROW: his hand at his cheek dissolves over
     f001-f008. It is in shot (the slot keeps f001-f093). Best-available with the
     fault named is the house standard; hiding it is not.

  b) review/ep2-demo-0820/index.html -- the beat-09 <tr class="pick"> row and the
     footage/slate counts (19/2 -> 20/1).

  c) review/ep2-picks/cut-readiness-0819.yaml -- amend, leaving the prior summary
     standing as history.

  d) STATE.md + pipeline/work-ladder-0819.md -- one entry recording the founder's
     word, that it fired this chain, and the resulting cut composition.

  e) pipeline/decisions-pending/ep2-guards-0818/ -- DELETE it in the same commit.
     A pre-staged chain that has fired is a trap for the next lane.
EDITS

say "6. THE GATE. Do not hand anyone a URL before this prints PASS"
python3 pipeline/qa_local.py

say "done -- qa_local passed. Now commit with an explicit pathspec:"
echo "  git commit -m '...' -- $CUT pipeline/measured/proof-ledger.json review/ep2-picks/cut-readiness-0819.yaml STATE.md"
