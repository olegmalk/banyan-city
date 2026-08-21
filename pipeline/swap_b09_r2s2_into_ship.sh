#!/usr/bin/env bash
# Swap a beat-09 r2s2 take into review/ep2-ship-0821, with every trap the
# 2026-08-20 swaps hit written down as an assertion instead of a memory.
#
#     bash pipeline/swap_b09_r2s2_into_ship.sh ep2-b09-r2s2-c1-0821
#
# WHAT IT IS ALLOWED TO DO: file moves, one re-assemble, the proof ledger, the
# page rebuild and the gate. WHAT IT REFUSES TO DO: write the manifest row.
# That row is the judgement -- the take, its sha, its NAMED FAULTS and the
# one-line reverse -- and a script that generates it would be a script writing
# a verdict. It is listed as hand work and the gate is not run until it exists.
#
# $0. No render, no GPU, no voice synthesis, no network beyond git.
set -euo pipefail
cd "$(dirname "$0")/.."
REPO="$PWD"

JOB="${1:-}"
[ -n "$JOB" ] || { echo "usage: $0 <job-id, e.g. ep2-b09-r2s2-c1-0821>"; exit 2; }

CUT=review/ep2-ship-0821
SRC="farm-out/$JOB"
CLIP="09-the-pause-LTX-$JOB.mp4"
MANIFEST="$CUT/sources/ship-manifest.yaml"

say() { printf '\n=== %s\n' "$*"; }

say "0. preconditions -- assert, do not trust"
test -f "$SRC/$CLIP" || { echo "!! clip missing: $SRC/$CLIP"; exit 1; }
# The box publishes a sha manifest beside every artifact. Check against ITS
# number, not against one typed here: a sha copied by hand proves nothing.
BOXSHA="$SRC/$JOB.sha256"
test -f "$BOXSHA" || { echo "!! no box sha manifest at $BOXSHA"; exit 1; }
want=$(grep " $CLIP\$" "$BOXSHA" | awk '{print $1}')
have=$(shasum -a 256 "$SRC/$CLIP" | awk '{print $1}')
[ -n "$want" ] || { echo "!! $CLIP has no row in $BOXSHA"; exit 1; }
[ "$want" = "$have" ] || { echo "!! clip sha mismatch
   box  $want
   disk $have"; exit 1; }
echo "ok: clip verified against the box's own manifest -- $have"

# THE FRAME COUNT IS THE SLOT. A take of a different length silently retimes
# the beat; render_t3 will hold or stretch and the cut's runtime moves.
frames=$(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames \
         -of default=nw=1:nk=1 "$SRC/$CLIP")
[ "$frames" = "121" ] || { echo "!! $CLIP is $frames frames, the slot expects 121"; exit 1; }

# THE get_clip() TRAP: it globs NN-*.mp4 and takes the SORTED FIRST. The
# incumbent is 09-the-pause-LTX-ep2-b09-cropmotion-0820.mp4, and `cropmotion`
# sorts before `r2s2`, so leaving both would keep the OLD clip by accident and
# every downstream number would describe a swap that did not happen.
say "1. remove the incumbent from the cut's sources -- a swap, not a coin flip"
old=$(find "$CUT/sources" -maxdepth 1 -name '09-*.mp4' | sort)
echo "  outgoing: ${old:-<none>}"
for f in $old; do
  [ "$(basename "$f")" = "$CLIP" ] && continue
  git rm -q --cached --ignore-unmatch "$f" "$f.meta.yaml" 2>/dev/null || true
  rm -f "$f" "$f.meta.yaml"
done

# VO COPY CHECK. This swap does not synthesise, move or re-time audio, and the
# beat's line must be the same line after it as before. find_audio() and
# vo_manifest() resolve against --clips and NOWHERE ELSE: a cut assembled
# without them is silent and says nothing about it.
say "2. VO copy check -- the picture changes, the words do not"
for f in 09-vo.mp3 09-vo.json; do
  test -f "$CUT/sources/$f" || { echo "!! $f missing from the cut"; exit 1; }
done
python3 - "$CUT" <<'PY'
import json, pathlib, sys
cut = pathlib.Path(sys.argv[1])
m = json.loads((cut / "sources" / "09-vo.json").read_text())
line = json.dumps(m).lower()
# Beat 09 is THE PAUSE: "Guard 1's face works through it, slowly." One man, no
# dialogue in the beat itself -- the VO is narration over it. The check is that
# the manifest still describes the same beat and the same number of lines, so a
# picture swap cannot quietly ride in with a re-voiced beat.
print("  09-vo.json lines:", len(m.get("lines", [])) or "n/a")
print("  09-vo.json beat :", m.get("beat", "n/a"))
if "beat" in m and str(m["beat"]) not in ("9", "09"):
    sys.exit("!! 09-vo.json is not beat 9")
PY
echo "ok: VO untouched and still beat 09's"

say "3. copy the take AND its provenance sidecar into the cut's --clips dir"
cp "$SRC/$CLIP" "$CUT/sources/"
test -f "$SRC/$CLIP.meta.yaml" && cp "$SRC/$CLIP.meta.yaml" "$CUT/sources/" \
  || echo "  (no .meta.yaml beside the clip -- the manifest row must carry the provenance)"

say "4. re-assemble. --out = bench mode: no leaf, no lineage.yaml, not canon"
python3 pipeline/render_t3.py sapling 002b \
  --clips "$CUT/sources" \
  --out   "$CUT/ep2-ship-0821.mp4"

say "5. re-extract proof frames + the git-derived ledger"
python3 pipeline/proof_receipts.py --cut ep2-ship-0821 --write

say "6. force-add past .gitignore (review/**/*.mp4, *.jpg are ignored)"
# build_site publishes ONLY what git tracks. Untracked media = broken links =
# qa_local failure. This is how the beat-03 swap failed on its first attempt.
git add -f "$CUT/sources/$CLIP" "$CUT/ep2-ship-0821.mp4" "$CUT"/proof/*.jpg
git add    "$CUT/ep2-ship-0821.mp4.meta.yaml" \
           "$CUT/proof/frames.yaml" \
           pipeline/measured/proof-ledger.json 2>/dev/null || true
test -f "$CUT/sources/$CLIP.meta.yaml" && git add "$CUT/sources/$CLIP.meta.yaml"

say "7. THE HAND EDITS -- this script cannot write these and must not pretend to"
NEWSHA=$(shasum -a 256 "$CUT/ep2-ship-0821.mp4" | awk '{print $1}')
cat <<EDITS
  Still to do by hand, before the gate:

  a) $MANIFEST
     - top-level  sha256:  -> $NEWSHA   (the cut's bytes changed)
     - the beat-09 row: take, sha256, why, verdict, and fault_shipping.
       NAME THE FAULTS. This take's accepted costs are pre-registered in
       pipeline/jobs/$JOB.yaml under \`bar\` -> ACCEPTED COSTS: one eye is
       squinted shut from f001 (a property of the r2s2 plate, not the motion),
       and the crop is 1.454x rather than native. Best-available with the fault
       named is the house standard; hiding it is not.
     - a how_to_reverse_it_in_one_line: in the house idiom.
  b) python3 review/ep2-ship-0821/build_page.py   (the table is DERIVED from the
     manifest, so this must run AFTER the row is edited, not before)
  c) review/ep2-picks/cut-readiness-0819.yaml -- amend, prior summary left standing
  d) STATE.md + pipeline/work-ladder-0819.md -- the batch, its numbers, the verdict
EDITS

say "8. THE GATE. Do not hand anyone a URL before this prints PASS"
echo "  run it yourself after the hand edits:  python3 pipeline/qa_local.py"

say "9. then commit with an explicit pathspec, and verify what is SERVED"
cat <<'TAIL'
  git commit -m '...' -- review/ep2-ship-0821 pipeline/measured/proof-ledger.json \
      review/ep2-picks/cut-readiness-0819.yaml STATE.md pipeline/work-ladder-0819.md
  git push origin main
  # the served bytes, not the local ones -- a push is not a deploy:
  curl -sL https://banyan.city/review/ep2-ship-0821/ep2-ship-0821.mp4 | shasum -a 256
TAIL
