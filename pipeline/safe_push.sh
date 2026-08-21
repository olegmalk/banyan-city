#!/usr/bin/env bash
# safe_push.sh — THE ONE WAY A LANE PUSHES. Use it instead of `git push`.
#
#   ./pipeline/safe_push.sh origin main
#   ./pipeline/safe_push.sh --fixing-main origin main   # only if you ARE the fix
#
# WHY THIS EXISTS (2026-08-20, the defect that fired twice in two days and cost
# the founder eight CI-failure emails):
#
#   19:24Z  5d1dbbf0  added three `subprocess.run(text=...)` calls with no
#           `encoding=` to derive_b16_field_0820.py. lint-genome went RED.
#   19:29Z  a22714c5  a DIFFERENT lane pushed. Red run, founder email.
#   19:43Z  7df8173d, e2408270  two more lanes. Two more emails.
#   19:52Z  ed119409, 164b0e59, f80aca27  three more. Three more emails.
#   19:57Z  7086f8b4  the one-keyword fix landed. Green.
#
# Every lane after the first pushed work that was itself fine onto a main that
# was already broken, and each push re-sent the same failure to the founder. The
# rule "check main is green before you push" existed as prose in three documents
# and was followed zero times out of five. So it is a program now.
#
# WHAT IT DOES
#   1. Runs the fast local gates (lint_genome, test_pipeline) and READS THEIR
#      EXIT CODES. Nonzero => refuses. You do not push your own breakage.
#   2. Asks GitHub for the state of the lint-genome workflow on the remote.
#      Newest COMPLETED run failed => refuses, unless --fixing-main.
#   3. A run still in flight is fine to stack on (that is normal traffic) — the
#      pending run id is printed so you know what you are stacking on. But a
#      pending run does NOT hide an older red: if the last completed run failed,
#      main is still red until something turns it green, and that is exactly the
#      hole the five lanes above fell through.
#   4. Pushes, passing your arguments to `git push` unchanged.
#
# Exit codes: 0 pushed · 1 push itself failed · 2 local gate failed ·
#             3 main is red · 4 bad usage.
#
# Deliberately NOT provided: a --skip-gates flag. --fixing-main is the only
# override and it means one thing — "the commit I am pushing is the repair".

set -uo pipefail   # NOT -e: this script's whole job is to read exit codes.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKFLOW="lint-genome"
# How many runs to look back through. -L1 is not enough: with one row a pending
# run masks the red run behind it, which is the exact state lanes 2-6 pushed
# into. We need the newest *completed* row, and cancelled/skipped rows carry no
# verdict, so we may have to walk past a few.
LOOKBACK=10

say()  { printf '%s\n' "$*"; }
fail() { printf 'SAFE-PUSH: REFUSED — %s\n' "$*" >&2; }

FIXING_MAIN=0
DRY_RUN=0
ARGS=()
for a in "$@"; do
  case "$a" in
    --fixing-main) FIXING_MAIN=1 ;;
    --dry-run)     DRY_RUN=1 ;;
    -h|--help)
      sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) ARGS+=("$a") ;;
  esac
done

# ---------------------------------------------------------------- step 1: gates
run_gate() {
  local label="$1"; shift
  say "SAFE-PUSH: gate — $label"
  ( cd "$ROOT" && "$@" )
  local rc=$?
  if [ "$rc" -ne 0 ]; then
    fail "local gate failed: $label (exit $rc). Fix it here; do not push it."
    exit 2
  fi
  say "SAFE-PUSH: gate ok — $label"
}

PY="${SAFE_PUSH_PYTHON:-python3}"
run_gate "lint_genome"   "$PY" pipeline/lint_genome.py
run_gate "test_pipeline" "$PY" pipeline/test_pipeline.py

# ------------------------------------------------------- step 2/3: remote state
# Prints one of:
#   green            — newest completed run succeeded
#   red <id> <sha>   — newest completed run failed
#   pending <id>     — a run is in flight and nothing completed behind it is red
#   pending-on-red <pending_id> <red_id> <sha>
#   unknown <reason> — gh missing, unauthenticated, offline, or no runs yet
ci_state() {
  if ! command -v gh >/dev/null 2>&1; then
    say "unknown gh-not-installed"; return
  fi
  local json rc
  json="$(gh run list --workflow "$WORKFLOW" -L "$LOOKBACK" \
            --json conclusion,status,databaseId,headSha,createdAt 2>&1)"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    # one token: `read` below splits on whitespace, so the reason must not.
    say "unknown gh-error:$(printf '%s' "$json" | tr '\n\t ' '___' | cut -c1-120)"
    return
  fi
  printf '%s' "$json" | "$PY" -c '
import json, sys
try:
    runs = json.load(sys.stdin)
except Exception as e:
    print("unknown bad-json:%s" % e); raise SystemExit
if not isinstance(runs, list) or not runs:
    print("unknown no-runs"); raise SystemExit
runs.sort(key=lambda r: r.get("createdAt") or "", reverse=True)

RED  = {"failure", "timed_out", "startup_failure"}
# cancelled/skipped/neutral/stale are not verdicts about the tree - a cancelled
# run says nothing about whether main builds, so we look past it rather than
# reading it as either colour.
LIVE = {"queued", "in_progress", "waiting", "requested", "pending", None, ""}

pending = None
for r in runs:
    if (r.get("status") or "") in LIVE and not r.get("conclusion"):
        pending = r
        break

verdict = None
for r in runs:
    c = r.get("conclusion")
    if c == "success" or c in RED:
        verdict = r
        break

if verdict is None:
    print("pending %s" % pending["databaseId"] if pending else "unknown no-completed-runs")
elif verdict.get("conclusion") in RED:
    if pending:
        print("pending-on-red %s %s %s" % (pending["databaseId"],
              verdict["databaseId"], (verdict.get("headSha") or "")[:9]))
    else:
        print("red %s %s" % (verdict["databaseId"], (verdict.get("headSha") or "")[:9]))
elif pending:
    print("pending %s" % pending["databaseId"])
else:
    print("green")
'
}

read -r STATE A B C <<<"$(ci_state)"

RED_MSG="main is red — fix it or wait; pushing now emails the founder"

case "$STATE" in
  green)
    say "SAFE-PUSH: CI green on $WORKFLOW"
    ;;
  pending)
    say "SAFE-PUSH: CI run $A in progress on $WORKFLOW — stacking on green-so-far"
    ;;
  red)
    say "SAFE-PUSH: CI RED on $WORKFLOW — run $A, commit ${B:-?}"
    if [ "$FIXING_MAIN" -eq 0 ]; then
      fail "$RED_MSG"
      say  "         if this commit IS the repair, re-run with --fixing-main" >&2
      exit 3
    fi
    say "SAFE-PUSH: --fixing-main given — pushing the repair onto red main"
    ;;
  pending-on-red)
    say "SAFE-PUSH: CI run $A in progress, but the last COMPLETED run $B (${C:-?}) failed"
    if [ "$FIXING_MAIN" -eq 0 ]; then
      fail "$RED_MSG"
      say  "         run $A may be the fix landing — wait for it, then push" >&2
      exit 3
    fi
    say "SAFE-PUSH: --fixing-main given — pushing the repair onto red main"
    ;;
  unknown)
    say "SAFE-PUSH: WARNING — cannot read CI state ($A). Pushing unguarded."
    ;;
  *)
    say "SAFE-PUSH: WARNING — unparseable CI state ('$STATE'). Pushing unguarded."
    ;;
esac

# ----------------------------------------------------------------- step 4: push
if [ "$DRY_RUN" -eq 1 ]; then
  say "SAFE-PUSH: DRY-RUN — would run: git push ${ARGS[*]:-}"
  exit 0
fi

say "SAFE-PUSH: git push ${ARGS[*]:-}"
( cd "$ROOT" && git push "${ARGS[@]+"${ARGS[@]}"}" )
rc=$?
if [ "$rc" -ne 0 ]; then
  fail "git push exited $rc"
  exit 1
fi
say "SAFE-PUSH: PASS pushed"
exit 0
