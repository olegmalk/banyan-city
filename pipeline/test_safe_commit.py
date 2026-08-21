#!/usr/bin/env python3
"""Selftest for pipeline/safe_commit.sh — the commit guard.

The defect it guards fired twice in the shared worktree: a lane ran
`git add -- <its paths>` and then a bare `git commit`, which commits the WHOLE
index — including a peer's staged-but-uncommitted work (2026-08-21: swept a
peer's 10 staged deletions, broke the licence gate + pages for everyone
behind). The guard's value is what it refuses and what it leaves alone, and
neither is visible until something tries it — so this builds throwaway git
repos and drives the real script against real git.

No stubs here on purpose: the whole point is git's own pathspec-commit
semantics. No network, nothing outside the temp dirs. Pure stdlib, runs in CI
beside the other suites.
"""

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SAFE_COMMIT = os.path.join(ROOT, "safe_commit.sh")
TRAILER = "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"

PASS = FAIL = 0
FAILURES = []


def check(cond, label):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  ok  %s" % label)
    else:
        FAIL += 1
        FAILURES.append(label)
        print("  FAIL %s" % label)


def git(repo, *args):
    return subprocess.run(["git"] + list(args), cwd=repo, capture_output=True,
                          text=True, encoding="utf-8", timeout=60)


def make_repo():
    """A committed baseline three lanes could be working over."""
    repo = tempfile.mkdtemp(prefix="safecommit-")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "selftest")
    git(repo, "config", "commit.gpgsign", "false")
    os.makedirs(os.path.join(repo, "sub"))
    for name in ("mine.txt", "peer.txt", "doomed.txt", os.path.join("sub", "a.txt")):
        with open(os.path.join(repo, name), "w") as fh:
            fh.write("baseline %s\n" % name)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "baseline")
    return repo


def guard(repo, *args):
    proc = subprocess.run(["/bin/bash", SAFE_COMMIT] + list(args), cwd=repo,
                          capture_output=True, text=True, encoding="utf-8",
                          timeout=60)
    return proc.returncode, proc.stdout + proc.stderr


def head_files(repo):
    out = git(repo, "show", "--name-only", "--format=", "HEAD").stdout
    return sorted(line for line in out.splitlines() if line.strip())


def head_msg(repo):
    return git(repo, "log", "-1", "--format=%B").stdout


def commit_count(repo):
    return int(git(repo, "rev-list", "--count", "HEAD").stdout.strip())


def stage_peer_and_mine(repo):
    """The exact shared-worktree shape: my edit staged NEXT TO a peer's
    staged modification and a peer's staged deletion."""
    for name in ("mine.txt", "peer.txt"):
        with open(os.path.join(repo, name), "a") as fh:
            fh.write("edit to %s\n" % name)
    git(repo, "add", "mine.txt", "peer.txt")
    git(repo, "rm", "-q", "doomed.txt")   # the peer's staged deletion


def test_bare_call_refused():
    print("\nbare call — zero pathspecs")
    repo = make_repo()
    try:
        stage_peer_and_mine(repo)
        before = commit_count(repo)
        rc, out = guard(repo, "-m", "sweep attempt")
        check(rc == 4, "exit 4 (refused)")
        check("REFUSED" in out and "ZERO pathspecs" in out, "refusal is loud and says why")
        check(commit_count(repo) == before, "NOTHING was committed")

        rc, out = guard(repo)   # not even a message
        check(rc == 4 and commit_count(repo) == before, "no args at all: also refused")
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_no_message_refused():
    print("\npathspecs but no -m")
    repo = make_repo()
    try:
        stage_peer_and_mine(repo)
        before = commit_count(repo)
        rc, out = guard(repo, "mine.txt")
        check(rc == 4, "exit 4 (refused) — an editor session is not a lane workflow")
        check(commit_count(repo) == before, "NOTHING was committed")
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_peer_staged_work_survives_and_is_warned_about():
    print("\nthe defect shape: peer work staged in the shared index")
    repo = make_repo()
    try:
        stage_peer_and_mine(repo)
        rc, out = guard(repo, "-m", "my change", "mine.txt")
        check(rc == 0, "exit 0")
        check(head_files(repo) == ["mine.txt"], "commit contains ONLY the named path")
        staged = git(repo, "diff", "--cached", "--name-only").stdout.split()
        check(sorted(staged) == ["doomed.txt", "peer.txt"],
              "peer's staged modification AND staged deletion survive, still staged")
        check(os.path.exists(os.path.join(repo, "peer.txt")),
              "peer's working-tree file untouched")
        check("WARNING" in out and "peer.txt" in out and "doomed.txt" in out,
              "warning names every outside-staged entry")
        check("PEER LANE" in out, "warning names the owner risk")
        check("SAFE-COMMIT:   mine.txt" not in out,
              "my own path is not listed as outside")
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_clean_index_no_warning():
    print("\nonly my work staged — no false alarm")
    repo = make_repo()
    try:
        with open(os.path.join(repo, "mine.txt"), "a") as fh:
            fh.write("solo edit\n")
        git(repo, "add", "mine.txt")
        rc, out = guard(repo, "-m", "solo", "mine.txt")
        check(rc == 0, "exit 0")
        check("WARNING" not in out, "no warning when nothing outside is staged")
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_trailer_appended_exactly_once():
    print("\ntrailer")
    repo = make_repo()
    try:
        with open(os.path.join(repo, "mine.txt"), "a") as fh:
            fh.write("one\n")
        rc, out = guard(repo, "-m", "no trailer given", "mine.txt")
        msg = head_msg(repo)
        check(rc == 0 and msg.count(TRAILER) == 1, "missing trailer gets appended once")
        check(msg.splitlines()[0] == "no trailer given", "subject line preserved")

        with open(os.path.join(repo, "mine.txt"), "a") as fh:
            fh.write("two\n")
        rc, out = guard(repo, "-m", "already has it\n\n" + TRAILER, "mine.txt")
        check(rc == 0 and head_msg(repo).count(TRAILER) == 1,
              "a message that already carries the trailer is not double-stamped")
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_pathspec_forms():
    print("\npathspec forms: directory, dashdash, multiple")
    repo = make_repo()
    try:
        with open(os.path.join(repo, "sub", "a.txt"), "a") as fh:
            fh.write("dir edit\n")
        with open(os.path.join(repo, "peer.txt"), "a") as fh:
            fh.write("peer edit\n")
        git(repo, "add", "-A")
        rc, out = guard(repo, "-m", "dir form", "--", "sub")
        check(rc == 0 and head_files(repo) == [os.path.join("sub", "a.txt")],
              "directory pathspec after -- commits only that dir")
        check("peer.txt" in out, "the peer's file outside the dir is warned about")

        with open(os.path.join(repo, "mine.txt"), "a") as fh:
            fh.write("multi\n")
        rc, out = guard(repo, "-m", "multi", "mine.txt", "peer.txt")
        check(rc == 0 and head_files(repo) == ["mine.txt", "peer.txt"],
              "multiple pathspecs all land")
        check("WARNING" not in out, "nothing left outside, no warning")
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_nothing_to_commit_is_a_failure_not_a_lie():
    print("\npathspec matches no change")
    repo = make_repo()
    try:
        rc, out = guard(repo, "-m", "empty", "mine.txt")
        check(rc == 1, "exit 1 — git's refusal is surfaced, not swallowed")
        check("git commit exited" in out, "reports the git exit")
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_unknown_flags_refused():
    print("\nflag surface stays closed")
    repo = make_repo()
    try:
        before = commit_count(repo)
        for flag in ("-a", "--amend", "--no-verify"):
            rc, out = guard(repo, flag, "-m", "x", "mine.txt")
            check(rc == 4 and commit_count(repo) == before,
                  "%s refused — the defect lives in exactly this surface" % flag)
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def main():
    print("safe_commit.sh — commit guard selftest")
    if not os.path.exists(SAFE_COMMIT):
        print("MISSING %s" % SAFE_COMMIT)
        return 1
    for fn in (test_bare_call_refused,
               test_no_message_refused,
               test_peer_staged_work_survives_and_is_warned_about,
               test_clean_index_no_warning,
               test_trailer_appended_exactly_once,
               test_pathspec_forms,
               test_nothing_to_commit_is_a_failure_not_a_lie,
               test_unknown_flags_refused):
        fn()
    print("\n%d passed, %d failed" % (PASS, FAIL))
    for f in FAILURES:
        print("  - %s" % f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
