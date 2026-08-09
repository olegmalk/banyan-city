#!/usr/bin/env python3
"""Claim a farm-queue task from a HAND-RUN, so the id in a sidecar means something.

THE RULING (lead, 2026-08-08), filed as queue-id-borrowed-by-hand-run-1786190580:
a hand-run that carries a queue task's id MUST write that task's STARTED and
DONE heartbeat lines. The alternative — take your own id and leave the queue
entry open — was available and was not chosen, because an id is how everything
downstream identifies a render and two meanings for one id is the whole defect.

WHAT WENT WRONG WITHOUT IT. `002b-b01-video-5b-1786089900` asked for
`seconds: 2.5`; the clip that carries that id in its sidecar is 4.71s, and
STATE.md 2026-08-08 records "nobody has explained the gap". Nothing in the
pipeline is broken: wan_i2v computes `frames = int(seconds * fps)` and video_task
passes the task's own `seconds` straight through, which reproduces the clip
exactly. The render was HAND-RUN with the queue entry's id and a different
recipe. No `DONE task=002b-b01-video-5b-1786089900` line exists on any
heartbeat, so the promoter could not retire the entry and it sat in `tasks:`
reading as unstarted while its output was already on the review page. An id in a
sidecar did not mean the queue entry had run.

WHY THIS FILE RATHER THAN "REMEMBER TO WRITE THE LINES". Both options were
equally easy — one command each — and one of them lied. This makes the honest
one the SHORTER one:

    python3 pipeline/claim_task.py <task-id> -- <the command you were going to run>

which writes STARTED, runs it, and writes DONE or FAIL from the exit code, so
the two lines cannot be forgotten separately from the run. The halves exist for
an interactive or multi-step job:

    python3 pipeline/claim_task.py <task-id> started
    …do the work…
    python3 pipeline/claim_task.py <task-id> done

BRANCH: `farm-results-hand`, never the borrowed machine's own branch. Courier
force-pushes `farm-results-<name>` from whatever heartbeat.txt is on that box's
disk (farm_worker.py:154-175), so a line we wrote to a worker's branch would be
erased the next time that worker checked in — a claim that can be silently
deleted by the machine it borrowed is not a claim. queue_promoter globs
`farm-results-*`, so a separate branch is read exactly the same way, and nothing
force-pushes this one but us.

NEVER TOUCHES THE WORKING TREE. Courier does `git checkout -qB <branch>`, which
is safe in a dedicated worker checkout and would be a disaster here: a hand-run
happens in the checkout a person is working in. This builds the commit with
plumbing against a temp index — hash-object, read-tree, write-tree,
commit-tree, push — so HEAD, the index and every file on disk are untouched.

$0 and CI-silent: vercel.json disables deployments for `farm-results-*` and
both workflows carry `branches-ignore: ["farm-results-**"]`.

Usage:
  python3 pipeline/claim_task.py <id> -- <cmd> [args…]   # the easy path
  python3 pipeline/claim_task.py <id> started [--note "…"]
  python3 pipeline/claim_task.py <id> done
  python3 pipeline/claim_task.py <id> fail --note "why"
  python3 pipeline/claim_task.py <id> interrupted        # costs no attempt
  python3 pipeline/claim_task.py <id> done --at 09:00:00Z   # finished earlier today
Flags: --branch <name>, --no-push (local only — says so loudly), --force,
       --at HH:MM:SSZ (today only — see clock_at)
"""
import argparse
import calendar
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "pipeline" / "farm-queue.yaml"
HB_PATH = "farm-out/heartbeat.txt"
HAND_BRANCH = "farm-results-hand"

# The four marks farm_worker writes, and the only ones anything downstream
# parses. Spelled here as data so the CLI and the tests cannot drift from
# farm_worker.heartbeat_attempts(), which is the reader that matters:
#   STARTED     counted as an attempt; written BEFORE the work
#   DONE        excludes from the attempt count AND retires the queue entry
#   FAIL        a failure the runner survived
#   INTERRUPTED subtracts a start — a Ctrl+C is not a failed render
STAGES = ("started", "done", "fail", "interrupted")


# ------------------------------------------------------------ pure functions

def queue_entry(text: str, task_id: str):
    """The queue dict with this id, from either list, or None.

    Both lists, because a `runner: manual` entry lives in `backlog:` forever —
    the promoter reports those and never moves them — and a manual entry is
    precisely the kind a person runs by hand. Looking in `tasks:` alone would
    reject the ids this tool exists for.
    """
    data = yaml.safe_load(text) or {}
    for key in ("tasks", "backlog"):
        for entry in data.get(key) or []:
            if isinstance(entry, dict) and str(entry.get("id", "")) == task_id:
                return entry
    return None


def heartbeat_line(stage: str, task_id: str, note: str = "", clock=None) -> str:
    """One heartbeat line, in Courier's own format: `HH:MM:SSZ MARK task=<id>`.

    THE FORMAT IS THE CONTRACT and it is unforgiving in one specific way: every
    reader keys on `task=(\\S+)`, so anything appended must be separated by a
    space and must never be glued to the id. A note therefore always follows the
    id, never precedes it and never joins it.
    """
    stamp = time.strftime("%H:%M:%SZ", time.gmtime(clock))
    mark = stage.upper()
    line = f"{stamp} {mark} task={task_id} by-hand"
    if note:
        line += " " + " ".join(str(note).split())
    return line


def stage_for(returncode: int) -> str:
    """What a wrapped command's exit code means on the heartbeat.

    130 is SIGINT and 2 is argparse/Ctrl+C on some shells; a console interrupt
    is NOT a failed render, and marking it FAIL would spend an attempt the task
    never got — the correction farm_worker.py already carries for the
    window-CLOSE and second-worker deaths of 2026-08-02/03.
    """
    if returncode == 0:
        return "done"
    if returncode in (130, -2, 2):
        return "interrupted"
    return "fail"


def append_line(existing: str, line: str) -> str:
    """The heartbeat is an APPEND LOG. Never rewritten, never sorted, never
    de-duplicated: heartbeat_attempts() counts STARTED lines, so collapsing two
    identical starts would hand a crash-looping task a fresh budget."""
    body = existing or ""
    if body and not body.endswith("\n"):
        body += "\n"
    return body + line + "\n"


# ------------------------------------------------------------------ git side

def git(*args, check=True, capture=True, env=None, stdin=None):
    # encoding= is not optional — the heartbeat carries em dashes and Wan's
    # Chinese negative terms, and the locale codec on Windows is cp1252 (the
    # fifth casualty is documented in farm_worker.sh()).
    return subprocess.run(["git", *args], cwd=REPO, check=check,
                          capture_output=capture, text=True, encoding="utf-8",
                          errors="replace", env=env, input=stdin)


def remote_heartbeat(branch: str) -> tuple:
    """(text, parent_sha) for the branch as origin has it, or ("", None).

    Fetched, not read from a local ref: the point of the claim is that the
    PROMOTER can see it, and the promoter reads `origin/farm-results-*`.
    """
    git("fetch", "-q", "origin", f"refs/heads/{branch}:refs/remotes/origin/{branch}",
        check=False)
    r = git("rev-parse", "--verify", "-q", f"refs/remotes/origin/{branch}", check=False)
    parent = (r.stdout or "").strip() or None
    if parent is None:
        return "", None
    hb = git("show", f"{parent}:{HB_PATH}", check=False)
    return (hb.stdout if hb.returncode == 0 else ""), parent


# Commits this PROCESS has written, per branch: {branch: (text, sha)}.
# Two marks in one wrapper run are two commits, and the second has to be built
# on the first. Reading the remote again for it would work only when the push
# succeeded — with --no-push, or after a network failure, the DONE commit would
# be built on a tree that has no STARTED line in it and would silently drop the
# claim it is completing. This is also one fewer fetch per mark.
_WRITTEN = {}


def base_heartbeat(branch: str) -> tuple:
    """(text, parent_sha) to build the next mark on — this run's own last commit
    if it made one, otherwise whatever origin holds."""
    if branch in _WRITTEN:
        return _WRITTEN[branch]
    return remote_heartbeat(branch)


def publish(branch: str, text: str, message: str, push: bool = True) -> tuple:
    """Commit `text` as farm-out/heartbeat.txt on `branch` and push. (sha, pushed).

    Plumbing against a TEMP INDEX so nothing in the caller's checkout moves —
    no branch switch, no staged file, no touched mtime. `git commit-tree` is the
    only way to write a commit without an index, and `GIT_INDEX_FILE` is the only
    way to build a tree without disturbing the real one.
    """
    _text, parent = base_heartbeat(branch)
    blob = git("hash-object", "-w", "--stdin", stdin=text).stdout.strip()
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(td) / "index"))
        if parent:
            git("read-tree", parent, env=env)
        else:
            git("read-tree", "--empty", env=env)
        git("update-index", "--add", "--cacheinfo", f"100644,{blob},{HB_PATH}", env=env)
        tree = git("write-tree", env=env).stdout.strip()
    args = ["commit-tree", tree, "-m", message] + (["-p", parent] if parent else [])
    sha = git(*args).stdout.strip()
    _WRITTEN[branch] = (text, sha)
    if not push:
        return sha, False
    r = git("push", "origin", f"{sha}:refs/heads/{branch}", check=False)
    if r.returncode:
        # A courier that cannot deliver has to SAY SO (farm_worker's own lesson,
        # 2026-08-01: seven tasks finished and GitHub heard nothing for six
        # hours). A DONE line nobody can fetch retires nothing.
        print(f"!! PUSH FAILED — the claim is a local commit ({sha[:12]}) and NOTHING\n"
              f"   can see it: queue_promoter reads origin/{branch}, so the entry\n"
              f"   stays open until this is pushed.\n"
              f"   {(r.stderr or r.stdout or '').strip()[-400:]}",
              file=sys.stderr, flush=True)
        return sha, False
    return sha, True


def clock_at(hhmmss: str) -> float:
    """`HH:MM:SSZ` today (UTC) as epoch seconds — the `--at` catch-up stamp.

    FOR A MARK WRITTEN AFTER THE WORK, which is the normal shape of a hand-run:
    an agent finishes at 09:00Z, does three more things, and claims the task at
    14:00Z. Without this the log says 14:00 and the hour the work actually
    finished is lost, or survives only as free text in a note.

    TODAY ONLY, and that is a guard rather than a missing feature. The heartbeat
    carries a clock and no date; the DATE every reader uses comes from the commit
    that publishes the line (build_sim.heartbeat_history). So a mark can carry the
    hour the work really finished, but it is always published on the day it is
    written, and a completion from an earlier day CANNOT be expressed here — which
    is the point. On 2026-08-09 both candidate backfills for an earlier day
    (held-zoom-rate-repick, and ep1-v33-assemble via 40f6ca4, which is 21:08 UTC
    on 08-08 and only looks like the 9th because this box is +04:00) would have
    landed a yesterday completion in "finished today". Backdating the COMMIT is
    the only way to do that honestly, and forging a git timestamp to move a
    number on a page is the thing this file exists to prevent.

    IT DOES NOT CHANGE WHAT THE STATUS PAGE SHOWS. The page ages a mark from its
    commit, so a catch-up line still reads as recent there; this puts the true
    hour in the log, where the record is.
    """
    t = time.strptime(hhmmss.strip().rstrip("Zz"), "%H:%M:%S")
    now = time.gmtime()
    return calendar.timegm((now.tm_year, now.tm_mon, now.tm_mday,
                            t.tm_hour, t.tm_min, t.tm_sec, 0, 0, 0))


def mark(task_id: str, stage: str, note: str = "", branch: str = HAND_BRANCH,
         push: bool = True, clock=None) -> str:
    """Append one mark for `task_id` and publish it. Returns the line written."""
    text, _parent = base_heartbeat(branch)
    line = heartbeat_line(stage, task_id, note, clock)
    sha, pushed = publish(branch, append_line(text, line), f"hb: {line}", push=push)
    where = f"pushed to {branch}" if pushed else f"local commit {sha[:12]} — NOT pushed"
    print(f"  {line}   [{where}]", flush=True)
    return line


# ----------------------------------------------------------------------- CLI

def split_command(argv: list) -> tuple:
    """(this tool's arguments, the wrapped command) — split on the first bare `--`.

    Done by hand because argparse.REMAINDER cannot: it swallows everything after
    the first positional, so `claim_task.py <id> started --note x` parsed `--note`
    as part of a command to run and then rejected the whole call. Splitting first
    means our flags are ours on both sides of the `--`.
    """
    if "--" in argv:
        i = argv.index("--")
        return list(argv[:i]), list(argv[i + 1:])
    return list(argv), []


def main(argv: list = None) -> int:
    own, cmd = split_command(sys.argv[1:] if argv is None else argv)
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("task_id")
    p.add_argument("stage", nargs="?", choices=STAGES,
                   help="omit and pass `-- <cmd>` instead to have both lines written for you")
    p.add_argument("--note", default="", help="free text appended AFTER the id")
    p.add_argument("--branch", default=HAND_BRANCH)
    p.add_argument("--no-push", action="store_true",
                   help="write the commit and do not publish it — says so loudly")
    p.add_argument("--force", action="store_true",
                   help="claim an id that is not in pipeline/farm-queue.yaml")
    p.add_argument("--at", default=None, metavar="HH:MM:SSZ",
                   help="stamp the mark with the hour the work really finished "
                        "(TODAY, UTC) instead of the hour it is being typed. For a "
                        "claim written after the fact; an earlier day cannot be "
                        "expressed and must not be. Does not change the age the "
                        "status page shows, which comes from the commit")
    args = p.parse_args(own)
    # --at records something that ALREADY happened, so it cannot ride the wrapper:
    # that form writes STARTED before work that has not run and DONE from an exit
    # code that does not exist yet, and neither of those has a past hour to carry.
    if args.at and not args.stage:
        p.error("--at records a mark for work that is already finished, so it "
                "needs an explicit stage; it cannot be used with `-- <command>`")
    clock = clock_at(args.at) if args.at else None

    if bool(args.stage) == bool(cmd):
        p.error("give exactly one of: a stage (started|done|fail|interrupted), "
                "or `-- <command>` to have both written for you")

    # AN ID THAT IS NOT IN THE QUEUE IS THE OTHER HALF OF THE SAME DEFECT. The
    # ruling has two sides: a run carrying a queue id must claim it, and a run
    # carrying an id nobody filed must not pretend to. Refusing here is what
    # keeps `DONE task=<id>` meaning "that entry ran".
    entry = queue_entry(QUEUE.read_text(encoding="utf-8"), args.task_id)
    if entry is None and not args.force:
        raise SystemExit(
            f"no entry with id {args.task_id!r} in pipeline/farm-queue.yaml.\n"
            "A heartbeat line for an id nobody filed retires nothing and tells a\n"
            "reader a queue entry ran when none exists. Either file the entry, or\n"
            "give this run its own id and leave the queue alone. --force overrides.")
    if entry is not None:
        print(f"claiming {args.task_id} — {str(entry.get('why') or '').split(chr(10))[0][:90]}")

    push = not args.no_push
    if args.stage:
        mark(args.task_id, args.stage, args.note, args.branch, push, clock)
        return 0

    mark(args.task_id, "started", args.note, args.branch, push)
    rc = subprocess.run(cmd, cwd=REPO).returncode
    # The DONE/FAIL line is written from the EXIT CODE and not from intent, which
    # is the whole reason the wrapper exists: the two halves cannot be forgotten
    # separately from the run, and a crash cannot leave a bare STARTED behind.
    mark(args.task_id, stage_for(rc), args.note, args.branch, push)
    return rc


if __name__ == "__main__":
    sys.exit(main())
