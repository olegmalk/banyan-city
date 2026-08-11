#!/usr/bin/env python3
"""Fire a staged job the moment a human clears its gate — not hours later.

Several specs under `pipeline/jobs/` are finished work waiting on one person.
`ep1-b13-217f-vo-length.yaml` is written down to the frame count and the seed;
the only thing between it and the card is Roman looking at a 13-second sample.
Today the sequence after he answers is: a human notices, a lane is dispatched,
the lane enqueues. That is minutes to hours of idle card AFTER the decision was
already made, which is the thing the standing sentinel rule exists to end
(Oleg, 2026-08-05: chain queued work on sentinels, never on "when someone's
awake").

THE ONE THING THIS MUST NEVER DO is decide that a gate is satisfied. Clearing a
gate is a taste call and belongs to the founder. So the trigger is not "the
sample rendered", not "the metric looks fine", not "it has been a while" — it
is one observable fact in git:

    A COMMITTED CHANGE DELETED THE TOP-LEVEL `gate:`/`gate_ref:` KEY FROM A
    SPEC THAT PREVIOUSLY CARRIED IT, AT THE SAME PATH.

Why that fact and not another: deleting a key from a tracked file and
committing it is not something a render, a timer or a crash can do. It takes a
person editing the one line the README already names as the clearing act
("Present = BLOCKED, full stop. Clearing one is a human deleting the key.").
The sentinel reads the deletion; it never evaluates the reason for it.

The guards that keep it from firing on an accident:

  new file          A spec that never had a gate cannot have had one cleared.
                    The comparison is against the SAME path's parent version,
                    so a fresh copy — including the `-run.yaml` pattern this
                    repo has actually used — is invisible to the trigger. It
                    reports what it skipped and why rather than guessing.
  commented out     `# gate: founder` is ambiguous: box_enqueue would let it
                    through (yaml never sees the key) but nobody deleted
                    anything. Refused loudly. A human must delete the line.
  emptied           `gate:` with no value is falsy, so box_enqueue would allow
                    it. The key is still there, so this refuses.
  re-gated          Removed in an old commit and put back: the key is in HEAD,
                    so nothing fires.
  dirty worktree    If the file differs from HEAD, a lane is mid-edit and the
                    committed fact is not the current one. Wait.
  window            Only clearings committed in the last --since-hours (24 by
                    default) count. This can only ever PREVENT a fire, never
                    cause one; it exists so the first run against an empty
                    state file cannot stampede through every clearing in the
                    repo's history.

Everything else is delegated rather than reimplemented: the founder-approval
check, the `recipe_slot`, the consumer rule and the gate refusal itself all
come from `box_enqueue.py`, which is called through and allowed to refuse. An
unapproved node does not fail a job, it SystemExits the daemon
(farm_worker.py:517), so that check has exactly one implementation.

    python3 pipeline/gate_sentinel.py --dry-run   # report, enqueue nothing
    python3 pipeline/gate_sentinel.py             # enqueue at most one

It is not wired to cron or schtasks. Building it and arming it are two
decisions.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS_DIR = "pipeline/jobs"
CANCELLED = JOBS_DIR + "/cancelled-by-founder/"
STATE = os.path.join(REPO, "ledger", "gate-sentinel-state.json")
LOG = os.path.join(REPO, "ledger", "gate-sentinel.log")

# 24h of lookback. A sentinel ticks every few minutes; a clearing older than a
# day is history, not news. Narrowing only — it cannot cause a fire.
DEFAULT_WINDOW_HOURS = 24
# One per tick, always. Four concurrent LTX jobs is how the box bugchecks under
# WDDM, and the queue drains sequentially anyway.
MAX_PER_RUN = 1

# Top-level key only, which is the one box_enqueue.gate_checks reads.
GATE_KEY = re.compile(r"^(gate|gate_ref)[ \t]*:", re.M)
# `# gate: founder` — a hash, the bare key, and a value. The prose header every
# staged spec carries ("# `gate:`/`gate_ref:` make box_enqueue.py refuse") does
# not match: a backtick sits where the key would have to start.
COMMENTED_GATE = re.compile(r"^[ \t]*#[ \t]*(gate|gate_ref)[ \t]*:[ \t]*\S", re.M)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import box_enqueue  # noqa: E402


# ---------------------------------------------------------------- pure rules

def gate_key_present(text: str) -> bool:
    """A live top-level gate key. Value irrelevant — `gate:` with nothing after
    it is falsy to box_enqueue but is still a key nobody deleted."""
    return bool(GATE_KEY.search(text or ""))


def commented_gate_present(text: str) -> bool:
    """A gate key that was commented out instead of deleted."""
    return bool(COMMENTED_GATE.search(text or ""))


def gate_cleared(before: str, after: str) -> bool:
    """Did this commit delete the gate key from this file?

    `before` is the parent's version of the same path, "" when the file did not
    exist there — which is why a brand-new spec, however ungated, never reads
    as a clearing.
    """
    return gate_key_present(before) and not gate_key_present(after)


def decide(obs: dict) -> tuple:
    """The trigger, in one place so the test can drive it with no git and no ssh.

    obs: cleared_in (sha or None), gate_now, commented_gate_now, dirty,
         already_fired, problems (list of strings).
    Returns (fire, reason). A reason starting with REFUSED is the loud kind —
    something looked enqueueable and is not.
    """
    if not obs["cleared_in"]:
        return False, "no committed change removed a gate key from this spec"
    if obs["gate_now"]:
        return False, "gate key is present in HEAD — still blocked"
    if obs["commented_gate_now"]:
        return False, ("REFUSED: the gate key is commented out, not deleted. "
                       "yaml cannot see it but nobody cleared anything — a "
                       "human deletes the line or it stays blocked")
    if obs["dirty"]:
        return False, ("working tree differs from HEAD — a lane is mid-edit, "
                       "the committed fact is not the current one")
    if obs["already_fired"]:
        return False, "already enqueued once — a spec fires exactly once, ever"
    if obs["problems"]:
        return False, "REFUSED: " + "; ".join(obs["problems"])
    return True, "gate deleted in %s and the spec is otherwise valid" % obs["cleared_in"][:8]


# ------------------------------------------------------------------- the git

def git(*args, ok_fail: bool = False):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if r.returncode and not ok_fail:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), r.stderr.strip()))
    return r


def show(rev_path: str):
    """File content at a rev, or None when it did not exist there."""
    r = git("show", rev_path, ok_fail=True)
    return None if r.returncode else r.stdout


def clearings(hours: int) -> dict:
    """{path: sha} for every gate deletion committed inside the window.

    Newest wins: if a spec was cleared, re-gated and cleared again, the commit
    reported is the last one, and HEAD decides whether it is gated now.
    """
    found = {}
    log = git("log", "--since=%d hours ago" % hours, "--format=%H",
              "--", JOBS_DIR)
    for sha in log.stdout.split():
        names = git("diff-tree", "--no-commit-id", "--name-only", "-r", sha,
                    "--", JOBS_DIR + "/*.yaml")
        for path in names.stdout.splitlines():
            path = path.strip()
            if not path or path.startswith(CANCELLED) or path in found:
                continue
            after = show("%s:%s" % (sha, path))
            if after is None:      # deleted or moved away in this commit
                continue
            before = show("%s~1:%s" % (sha, path)) or ""
            if gate_cleared(before, after):
                found[path] = sha
    return found


# ------------------------------------------------------------ spec validation

def spec_problems(path: str) -> tuple:
    """Everything wrong with this spec, using box_enqueue's own checks.

    Reimplementing the approval read is the one thing that must not happen —
    two implementations of a §6 gate is one implementation too many — so this
    calls gate_checks and only ADDS the things a sentinel can see that a human
    typing one enqueue by hand would have seen for themselves.
    """
    full = os.path.join(REPO, path)
    try:
        spec = box_enqueue.load_spec(full)
    except SystemExit as e:
        return ["spec will not load: %s" % e], ""
    except Exception as e:
        return ["malformed yaml: %s: %s" % (type(e).__name__, e)], ""
    if not isinstance(spec, dict):
        return ["spec is not a mapping"], ""

    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            job = box_enqueue.to_job(spec)
            problems = list(box_enqueue.gate_checks(spec, job))
    except SystemExit as e:
        return ["invalid spec: %s" % e], buf.getvalue()

    if spec.get("measure_on_box"):
        problems.append("measure_on_box is set — the prompt has not been token-"
                        "measured on the box's real tokenizer, so it must not fire")
    after = spec.get("after") or []
    if after:
        problems.append("after: %s — this script cannot see the box heartbeats "
                        "that prove those finished" % (", ".join(map(str, after))))
    init = spec.get("init")
    if init and not os.path.exists(os.path.join(REPO, str(init))):
        problems.append("plate missing: init %s is not in the repo" % init)
    return problems, buf.getvalue()


# ------------------------------------------------------------------- ledgers

def load_state() -> dict:
    try:
        with open(STATE, encoding="utf-8") as fh:
            st = json.load(fh)
    except (OSError, ValueError):
        return {"fired": {}}
    st.setdefault("fired", {})
    return st


def save_state(st: dict) -> None:
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(st, fh, indent=2, sort_keys=True)
    os.replace(tmp, STATE)      # a torn state file is a spec that fires twice


def fired_before(st: dict, path: str, spec_id) -> bool:
    """Either key is enough. The path is what git reports; the id is what the
    box keys MAX_ATTEMPTS on, and a spec that got renamed must still not run a
    second time."""
    for key, rec in st["fired"].items():
        if key in (path, spec_id) or rec.get("path") == path or rec.get("id") == spec_id:
            return True
    return False


def note(msg: str) -> None:
    line = "%s %s" % (time.strftime("%Y-%m-%dT%H:%M:%S"), msg)
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="enqueue a staged job once a human has deleted its gate")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be enqueued, enqueue nothing")
    ap.add_argument("--since-hours", type=int, default=DEFAULT_WINDOW_HOURS,
                    help="how far back a clearing commit may be (default %d)"
                         % DEFAULT_WINDOW_HOURS)
    args = ap.parse_args(argv)

    st = load_state()
    found = clearings(args.since_hours)
    print("gate deletions committed in the last %dh: %d"
          % (args.since_hours, len(found)))

    refused = 0
    fired = 0
    for path in sorted(found):
        sha = found[path]
        head = show("HEAD:%s" % path)
        if head is None:
            print("%s\n  skip: not in HEAD any more" % path)
            continue

        obs = {
            "cleared_in": sha,
            "gate_now": gate_key_present(head),
            "commented_gate_now": commented_gate_present(head),
            "dirty": bool(git("status", "--porcelain", "--", path).stdout.strip()),
            "already_fired": False,
            "problems": [],
        }
        # The cheap facts first; only a spec that survives them is parsed and
        # validated, so a still-gated file never even gets read for an id.
        fire, why = decide(obs)
        detail = ""
        if fire:
            problems, detail = spec_problems(path)
            spec_id = None
            try:
                spec_id = box_enqueue.load_spec(os.path.join(REPO, path)).get("id")
            except Exception:
                pass
            obs["already_fired"] = fired_before(st, path, spec_id)
            obs["problems"] = problems
            fire, why = decide(obs)

        print("%s" % path)
        for line in detail.splitlines():
            print("  %s" % line.strip())
        if not fire:
            print("  no: %s" % why)
            if why.startswith("REFUSED"):
                note("REFUSED %s | %s" % (path, why))
                refused += 1
            continue

        if fired >= MAX_PER_RUN:
            print("  deferred: one job per tick, sequential only")
            continue
        if args.dry_run:
            print("  WOULD ENQUEUE: %s" % why)
            fired += 1
            continue

        # Recorded BEFORE the attempt on purpose. If the enqueue dies between
        # the scp and the move, the next tick must not try again — a duplicate
        # id is a wasted slot at best, and an unnoticed second render at worst.
        # Clearing the entry is a human's call.
        spec_id = None
        try:
            spec_id = box_enqueue.load_spec(os.path.join(REPO, path)).get("id")
        except Exception:
            pass
        key = spec_id or path
        st["fired"][key] = {"path": path, "id": spec_id, "cleared_in": sha,
                            "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                            "outcome": "attempting"}
        save_state(st)
        note("ENQUEUE %s | gate deleted in %s" % (path, sha[:8]))
        try:
            rc = box_enqueue.main([os.path.join(REPO, path)])
        except SystemExit as e:
            rc = e.code if isinstance(e.code, int) else 1
            note("!! box_enqueue exited: %s" % e)
        st["fired"][key]["outcome"] = "queued" if rc == 0 else "failed rc=%s" % rc
        save_state(st)
        if rc:
            note("!! enqueue FAILED for %s (rc=%s) — not retried" % (path, rc))
            refused += 1
        fired += 1

    if not found:
        print("nothing to do — no gate was deleted in the window")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
