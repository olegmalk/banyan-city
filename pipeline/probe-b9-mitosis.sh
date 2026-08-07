#!/usr/bin/env bash
# Re-render node 001 beat 9 ("whoami") with the anti-duplication negatives.
#
# THE JOB. The founder, 2026-08-07, correcting himself mid-sentence: "that's not
# the beat i was talking about. i was talking about BEAT 9." He is right — the
# duplication in the f15 take of beat 9 is worse than beat 11's. Counted off the
# clip: three blades at frame 0, the top leaf divided by frame 5, seven blades on
# a stem carrying a whole extra node from frame 25 on. Beat 11's leaf divides and
# re-fuses; beat 9's plant simply grows, which is beat 11's job. Nothing had ever
# been tried against it either: the negative used 363 of its 900 characters and
# held not one word about leaf count.
#
# TWO INPUTS CHANGE HERE, unlike the beat 11 probe, and deliberately. The
# negative gains fifteen leaf-count terms, AND the direction loses "one leaf
# spinning as it falls" — an instruction for a leaf to detach, which no negative
# can outvote (video_prompt's docstring: "It was told to.") — plus the "two
# leaves" count the approved still contradicts. Both live in motion.yaml.
#
# Fifteen rather than beat 11's eight because the frame counts name a second
# defect: re-measured 2026-08-07 at frames 0/12/24/36/48/60, the stem does not
# just gain leaves, it LENGTHENS and grows a whole second node tier. "no extra
# stem nodes" and "no branching stem" are that tier; the other thirteen are beat
# 11's convention plus the detachment pair. 627 of 900 characters, nothing cut.
#
# WHAT IS HELD CONSTANT: the same conditioning still, the same recipe, and THE
# SAME SEED as the take in the episode — 20260814, off the f15 sidecar at
# 7f6c538. The still is NOT touched; 09-whoami.png is the founder's canon.
#
# Everything is copied into a probe dir and hashed on both sides first. The two
# prompt strings travel as FILES because the negative carries Wan's Chinese
# anti-static terms and a cp1252 console mangles them silently — the clip would
# render, just without the terms the run exists to test.
#
# Usage: bash pipeline/probe-b9-mitosis.sh [ssh-host]      (default: rtx5090)
#
# It fires DETACHED (schtasks one-shot — a remote command from the Mac dies at
# ten minutes) and returns immediately. Pull nothing until run.log prints
# PROBE_RC; an scp four minutes early has already stranded one clip for a day.
set -euo pipefail

HOST="${1:-rtx5090}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NODE="genomes/sapling/nodes/001-capability-inventory"
DIR='C:\banyan-farm\probe-b9-20260807'
DIR_FWD='C:/banyan-farm/probe-b9-20260807'
VENV='C:\banyan-video\venv\Scripts\python.exe'
OUT="$DIR"'\09-whoami-antisplit.mp4'
SEED=20260814
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

cd "$REPO"

# 1. The prompt pair, regenerated from the genome rather than pasted.
python3 - "$STAGE" <<'PY'
import pathlib, sys
sys.path.insert(0, "pipeline")
from video_task import video_prompt, motion_directions, NEG_MAX
from generate_shots import parse_shots
out = pathlib.Path(sys.argv[1])
node = pathlib.Path("genomes/sapling/nodes/001-capability-inventory")
shot = {s["num"]: s for s in
        parse_shots((node / "shots.md").read_text(encoding="utf-8"))}[9]
pos, neg = video_prompt(f'{motion_directions(node)[9]}. no new subjects, no scene change',
                        shot["prompt"], no_anchor=True, beat=9)
assert "splitting leaf" in neg, "the anti-duplication terms are gone from motion.yaml"
assert "leaf detaching" in neg, "the anti-detachment terms are gone from motion.yaml"
assert "spinning as it falls" not in pos, "the detachment clause is back in the positive"
assert len(neg) <= NEG_MAX, f"negative is {len(neg)} chars, over {NEG_MAX}"
(out / "b9-prompt.txt").write_text(pos, encoding="utf-8")
(out / "b9-negative.txt").write_text(neg, encoding="utf-8")
print(f"   prompt {len(pos)} chars, negative {len(neg)}/{NEG_MAX} chars")
PY

# 2. The task action, as a file. schtasks /tr truncates past ~261 characters and
#    this command line is twice that. ONE LINE, CRLF: cmd.exe's `^` continuation
#    is only reliable with CRLF endings, so the way not to depend on that is to
#    have nothing to continue.
{ printf '@echo off\r\n'
  printf '"%s" "%s" --python "%s" --wan "%s" --init "%s" --prompt-file "%s" --negative-file "%s" --out "%s" --seed %s --beat 9 --task b9-mitosis-20260807 --worker %s --size 704x1280 --steps 14 --guidance 5.0 --seconds 2.5 --model ti2v-5b > "%s" 2>&1\r\n' \
    "$VENV" "$DIR\\probe_beat.py" "$VENV" "$DIR\\wan_i2v.py" "$DIR\\09-whoami.png" \
    "$DIR\\b9-prompt.txt" "$DIR\\b9-negative.txt" "$OUT" "$SEED" "$HOST" \
    "$DIR\\run.log"
} > "$STAGE/run.cmd"

cp pipeline/probe_beat.py pipeline/wan_i2v.py "$STAGE/"
cp "$NODE/stills/09-whoami.png" "$STAGE/"

# 3. The card must be free, and this REFUSES rather than warns. Two workers
#    shared this GPU for a whole night once (2026-08-01) and both runs were
#    worthless; a second 5B load would also walk into the VRAM+commit region
#    where the box bugchecks.
echo "== $HOST =="
GPU=$(ssh -o ConnectTimeout=10 "$HOST" "nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader")
echo "   GPU: $GPU"
USED=$(printf '%s' "$GPU" | awk -F'[ ,]' '{print $1}')
if [ "${USED:-0}" -gt 2000 ]; then
  echo "REFUSING: ${USED} MiB already allocated on $HOST — something else is rendering." >&2
  exit 1
fi

ssh "$HOST" "if not exist \"$DIR\" mkdir \"$DIR\""
scp -q "$STAGE"/* "$HOST:$DIR_FWD/"

# 4. Hash both sides. A mangled negative is invisible in the output, so this is
#    the only place the corruption can be caught.
echo "== sha256, local then remote =="
shasum -a 256 "$STAGE/b9-negative.txt" "$STAGE/09-whoami.png" | awk '{print $1, substr($2, match($2, /[^\/]*$/))}'
ssh "$HOST" "certutil -hashfile \"$DIR\\b9-negative.txt\" SHA256 & certutil -hashfile \"$DIR\\09-whoami.png\" SHA256" \
  | grep -v "^CertUtil\|^SHA256" | tr -d ' \r' | grep .

# 5. Fire, detached. /f replaces a leftover task of the same name; the task is
#    deleted after the run so nothing can re-fire it unattended overnight.
ssh "$HOST" "schtasks /create /f /tn banyan-b9-mitosis /sc once /st 00:00 /tr \"cmd /c $DIR\\run.cmd\" & schtasks /run /tn banyan-b9-mitosis"

cat <<EOF

FIRED. ~4 min at 704x1280/14 steps on the 5090. Poll, do not pull:

  ssh $HOST "type $DIR\\run.log" | tail -5

When PROBE_RC appears (and only then):

  scp $HOST:$DIR_FWD/09-whoami-antisplit.mp4 $HOST:$DIR_FWD/*.meta.yaml review/
  ssh $HOST "schtasks /delete /f /tn banyan-b9-mitosis"

Then judge it by EYE against review/beat-09-whoami.mp4 — count distinct leaf
silhouettes at the start, middle and end of each. The f15 take goes 3 -> 7.
check_invention.py does not catch this artifact (its blind spot is documented at
check_invention.py:45), and the motion number will likely FALL, because the
growth is what was scoring.
EOF
