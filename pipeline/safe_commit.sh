#!/usr/bin/env bash
# safe_commit.sh — THE ONE WAY A LANE COMMITS. Use it instead of `git commit`.
#
#   ./pipeline/safe_commit.sh -m "message" <pathspec> [<pathspec>...]
#
# WHY THIS EXISTS (fired twice in the shared worktree, latest 2026-08-21):
# a lane ran `git add -- <its paths>` and then `git commit -m ...` with NO
# pathspec on the COMMIT. A bare `git commit` commits the whole index — which
# in a worktree shared by many lanes includes every peer's staged-but-not-yet-
# committed work. Today that swept a peer's 10 staged deletions into an
# unrelated commit and broke the licence gate + pages for everyone behind it.
# The prose rule "ALWAYS `git commit -- <paths>`" existed and was not followed,
# so it is a program now.
#
# WHAT IT DOES
#   1. Refuses to run with zero pathspecs. There is no flag to override this:
#      if you cannot name what you are committing, you are not ready to commit.
#   2. Refuses to run without -m (an editor session is not a lane workflow).
#   3. Lists staged entries OUTSIDE your pathspecs as a loud warning. They are
#      NOT committed (`git commit -- <paths>` already excludes them) — the
#      warning exists so you know a PEER LANE is mid-work there. Do not "clean
#      them up", do not widen your pathspecs to swallow them.
#   4. Appends the Co-Authored-By trailer if the message lacks it (never twice).
#   5. Runs `git commit -m <msg> -- <paths>` verbatim. Note git's semantics:
#      a pathspec commit records the WORKING TREE content of those paths, so
#      partial (-p) staging of your own files is not honoured — commit whole
#      files you own.
#
# Exit codes: 0 committed · 1 git commit itself failed · 4 bad usage.
# Pathspecs resolve relative to your cwd, exactly as git resolves them.
#
# Then push with ./pipeline/safe_push.sh — never a bare `git push`.

set -uo pipefail   # NOT -e: this script's whole job is to read exit codes.

TRAILER='Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>'

say()  { printf '%s\n' "$*"; }
fail() { printf 'SAFE-COMMIT: REFUSED — %s\n' "$*" >&2; }

MSG=""
HAVE_MSG=0
PATHS=()
while [ $# -gt 0 ]; do
  case "$1" in
    -m|--message)
      shift
      if [ $# -eq 0 ]; then fail "-m needs a message"; exit 4; fi
      MSG="$1"; HAVE_MSG=1 ;;
    -m?*) MSG="${1#-m}"; HAVE_MSG=1 ;;
    -h|--help)
      sed -n '2,33p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    --)
      shift
      while [ $# -gt 0 ]; do PATHS+=("$1"); shift; done
      break ;;
    -*)
      fail "unknown flag '$1' — this wrapper takes only -m and pathspecs. \
Other git-commit flags (--amend, -a, ...) are exactly the surface the defect lives in."
      exit 4 ;;
    *) PATHS+=("$1") ;;
  esac
  shift
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  fail "not inside a git work tree"
  exit 4
fi

if [ "$HAVE_MSG" -eq 0 ]; then
  fail "no -m <message> given"
  exit 4
fi

if [ "${#PATHS[@]}" -eq 0 ]; then
  fail "ZERO pathspecs. A commit without pathspecs commits the WHOLE INDEX — \
in this shared worktree that is every peer's staged work (2026-08-21: a bare \
commit swept a peer's 10 staged deletions and broke the licence gate + pages). \
Name the paths you are committing: safe_commit.sh -m \"msg\" <path> [<path>...]"
  exit 4
fi

# ---------------------------------------------------- peer-work-in-index check
# Everything staged, minus everything staged that matches OUR pathspecs, is a
# peer's work in flight. git does the pathspec matching so globs/dirs behave
# exactly as they will in the commit itself.
ALL_STAGED="$(git diff --cached --name-only)"
IN_PATHS="$(git diff --cached --name-only -- "${PATHS[@]}")"
OUTSIDE="$(comm -23 <(printf '%s\n' "$ALL_STAGED" | sort -u) \
                    <(printf '%s\n' "$IN_PATHS"   | sort -u) | sed '/^$/d')"

if [ -n "$OUTSIDE" ]; then
  say "SAFE-COMMIT: ============================ WARNING ============================"
  say "SAFE-COMMIT: staged entries OUTSIDE your pathspecs — NOT committed by this call:"
  printf '%s\n' "$OUTSIDE" | sed 's/^/SAFE-COMMIT:   /'
  say "SAFE-COMMIT: a PEER LANE is likely mid-work on these. They stay staged and"
  say "SAFE-COMMIT: untouched. Do NOT unstage, revert or 'clean up' these paths, and"
  say "SAFE-COMMIT: do NOT widen your pathspecs to include work that is not yours."
  say "SAFE-COMMIT: =================================================================="
fi

# ------------------------------------------------------------------- trailer
case "$MSG" in
  *"$TRAILER"*) : ;;
  *) MSG="$MSG"$'\n\n'"$TRAILER" ;;
esac

# -------------------------------------------------------------------- commit
say "SAFE-COMMIT: git commit -m <msg> -- ${PATHS[*]}"
git commit -m "$MSG" -- "${PATHS[@]}"
rc=$?
if [ "$rc" -ne 0 ]; then
  fail "git commit exited $rc"
  exit 1
fi
say "SAFE-COMMIT: PASS committed $(git rev-parse --short HEAD)"
exit 0
