#!/usr/bin/env bash
# v35 — episode 1 re-assembled once the founder rules on beat 6.
#
# PRE-WRITTEN THE NIGHT BEFORE so the morning costs no thinking: his verdict
# picks a subcommand, the subcommand runs, and the cut exists. It does exactly
# two things and refuses to guess which.
#
#   scripts/v35-assemble.sh ratify
#       He takes b06-r5-s2, the frame v34 already holds. The fifteen clips are
#       copied forward BYTE-IDENTICAL and only beat 6's sidecar changes: its
#       `provisional: true` becomes false and the PROVISIONAL PICK sentence is
#       replaced by his ratification. v34 is left untouched on disk, so what he
#       screened stays readable next to what the verdict made of it.
#
#   scripts/v35-assemble.sh flip s0|s1|s3     (or any take under 001's stills/)
#       He wants a different seed. Beat 6's clip is re-made by hold_still from
#       that take — --still, because beat 6 has NO canon still (the only frame in
#       001's stills/ for it is 06-too-blue-REVOKED-leaf.png, which he revoked on
#       2026-08-07) and hold_still requires --provisional to hold a take.
#
# WHAT THIS SCRIPT WILL NOT DO, and the refusals are load-bearing:
#   * It never writes into genomes/*/stills/. Promoting a take to canon is what
#     stripped the record that refuses it (4eb4c61) and it is an R4 call besides.
#   * It never writes a canon sidecar. D15 is founder-owed and unpriced (25->47).
#   * `ratify` edits ONE file and only inside review/provisional-v35/.
#
# AND THE THING TO SAY OUT LOUD BEFORE HE PICKS: NEITHER VERDICT MAKES v35
# PUBLISHABLE. Measured against the live gate on 2026-08-09, nine of v34's
# fifteen beats are refused by build_site.publishable() for the same reason —
# CreativeML Open RAIL++-M on the animagine still each one holds — and beat 6 is
# only one of the nine. The other eight (03, 07, 08, 09, 10, 12, 14, 15) do not
# move whichever way he rules. The narrowing that could clear them
# (licence_gate.review_narrowed) is reachable only for files under `cuts/` or
# `review-assets/`; review/provisional-v35/ is neither, so it does not apply
# here at all. v35 is a SCREENING cut either way. See QA-v34-0810.md.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

SRC=review/provisional-v34/clips
DST=review/provisional-v35/clips
OUT=review/provisional-v35/ep1-v35-PROVISIONAL.mp4
TAKES=genomes/sapling/nodes/001-capability-inventory/takes/stills
B6=06-too-blue.mp4
TODAY="$(date -u +%Y-%m-%d)"

usage() { sed -n '2,40p' "${BASH_SOURCE[0]}"; exit 2; }
[ $# -ge 1 ] || usage
MODE="$1"; shift || true

[ -d "$SRC" ] || { echo "!! $SRC is missing — nothing to carry forward"; exit 1; }

stage_clips() {
  rm -rf "$DST"
  mkdir -p "$DST"
  cp -p "$SRC"/* "$DST"/
  echo "staged $(ls "$DST"/*.mp4 | wc -l | tr -d ' ') clips + VO into $DST"
}

case "$MODE" in
  ratify)
    stage_clips
    python3 - "$DST/$B6.meta.yaml" "$TODAY" <<'PY'
import re, sys
from pathlib import Path
p, today = Path(sys.argv[1]), sys.argv[2]
t = p.read_text(encoding="utf-8")
assert "provisional-v35" in str(p), "refusing to edit outside v35"
t = re.sub(r"^provisional: true$", "provisional: false", t, count=1, flags=re.M)
# the reason block is `provisional_reason: |-` plus its indented body
t = re.sub(r"^provisional_reason: \|-\n(?:  .*\n)+",
           "ratified_by: founder\n"
           f"ratified_date: {today}\n"
           "ratification_note: |-\n"
           "  b06-r5-s2 RATIFIED by the founder (R4) at the "
           f"{today} screening of ep1 v34. This clip's bytes are v34's, "
           "unchanged; only this record moved. The frame is still NOT canon "
           "and NOT published — promotion into stills/ and the licence "
           "question (D15, OpenRAIL++) are both separate and both his.\n",
           t, count=1, flags=re.M)
p.write_text(t, encoding="utf-8")
print(f"  beat 6 record: provisional cleared, ratification recorded {today}")
PY
    ;;

  flip)
    [ $# -ge 1 ] || { echo "!! flip needs a take, e.g. 'flip s0' or 'flip 06-too-blue-r4-s2'"; exit 2; }
    SEL="$1"
    # accept a bare seed label (s0) as this beat's r5 seed, or a full take stem
    if [[ "$SEL" =~ ^s[0-9]$ ]]; then STILL="$TAKES/06-too-blue-r5-$SEL.png"
    else STILL="$TAKES/${SEL%.png}.png"; fi
    [ -f "$STILL" ] || { echo "!! no such take: $STILL"; ls "$TAKES" | grep '^06-' | grep -v meta; exit 1; }
    stage_clips
    rm -f "$DST/$B6" "$DST/$B6.meta.yaml"
    python3 pipeline/hold_still.py 6 \
      --node 001-capability-inventory --genome sapling \
      --still "$STILL" --fit \
      --provisional "FLIP at the $TODAY screening: the founder rejected b06-r5-s2 and took $(basename "$STILL" .png). Held from a TAKE because beat 6 has no canon still — 001's stills/ holds only 06-too-blue-REVOKED-leaf.png, revoked 2026-08-07. Not canon, not published." \
      --out "$DST"
    [ -f "$DST/$B6" ] || { echo "!! hold_still did not write $DST/$B6"; ls "$DST" | grep '^06-'; exit 1; }
    echo "  beat 6 re-held from $(basename "$STILL")"
    ;;

  *) usage ;;
esac

python3 pipeline/render_t3.py sapling 001 --clips "$DST" --out "$OUT"

echo
echo "== gate ($OUT) =="
python3 - "$OUT" <<'PY'
import sys
sys.path.insert(0, "pipeline")
from pathlib import Path
import build_site as bs
ok, why = bs.publishable(Path(sys.argv[1]))
print(f"  publishable: {ok}")
if why:
    print(f"  why: {why}")
print("  (expected False — nine beats carry OpenRAIL++ stills and D15 is open;")
print("   this is a screening cut, not a publish candidate)")
PY
echo
echo "done — $OUT"
