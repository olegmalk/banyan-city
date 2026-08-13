#!/usr/bin/env python3
"""Put a job into the box-resident queue, from here, safely.

The queue itself is just directories on the card (`box_runner.py` drains them),
so enqueueing is "write a json into ready/". Doing that by hand is how you get
the three failures this script exists to prevent:

  1. A job naming an unapproved node. That is not a failed job, it is a dead
     daemon -- the §6 gate raises SystemExit, which `except Exception` does not
     catch (farm_worker.py:517). So `--check-approval` runs first, against the
     leaf the gate actually reads, and refuses to enqueue.
  2. A reused id. MAX_ATTEMPTS keys on id, so a re-queued id inherits its
     predecessor's spent attempts and can be retired without ever running. Ids
     are stamped with an epoch second unless one is given explicitly.
  3. A half-written job file being claimed mid-copy. The runner claims by
     renaming out of ready/, and scp writes in place -- so the file lands in a
     staging dir and is MOVED into ready/ as the last step.
  4. Two queued jobs whose `payload:` blocks name the SAME box paths. Payloads
     are written at ENQUEUE time, so the second enqueue overwrites the first
     job's prompt before either job runs, and the box renders the second job's
     picture under both names. On 2026-08-13 ep2-b01-shape and its twin did
     exactly that, five seconds apart, into one parent-named directory; only the
     declared-artifact check noticed. See reserve_payload/payload_collisions.

    python3 pipeline/box_enqueue.py pipeline/jobs/<spec>.yaml [--dry-run]
    python3 pipeline/box_enqueue.py --list        # what is queued right now
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSH_HOST = "rtx5090"
QUEUE_ROOT = r"C:\banyan-queue"
STAGING = QUEUE_ROOT + r"\incoming"
NODES = os.path.join(REPO, "genomes", "sapling", "nodes")

# Where this machine remembers which box payload paths it has handed out. The
# box cannot answer the question itself: `to_job` deliberately does not copy
# `payload:` into the job json, so a queued job on the card carries no record of
# the files it was given. Local, gitignored, append-only -- see reserve_payload.
PAYLOAD_INDEX = os.path.join(REPO, "pipeline", ".box-payload-index.jsonl")

# How long a reservation counts as live on its own, before the box queue is the
# only thing keeping it alive. It has to outlast the gap between reserving a
# path and the job appearing in ready/ -- an scp of five payload files plus a
# move, seconds -- because that gap is precisely when the twin slipped in.
RESERVE_GRACE_SEC = 120


def ssh(command: str, timeout: int = 90):
    # encoding named on purpose: text mode alone decodes with the locale codec,
    # and cmd.exe answers in cp1252 while our prompts carry ellipses and Chinese
    # negatives. The decode happens on subprocess's reader thread, where the
    # error never reaches us -- stdout just silently becomes None.
    return subprocess.run(["ssh", "-o", "ConnectTimeout=25", "-o", "BatchMode=yes",
                           SSH_HOST, command],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)


def newest_t0_leaf(node: str):
    leaves = os.path.join(NODES, node, "leaves")
    if not os.path.isdir(leaves):
        return None
    names = sorted(n for n in os.listdir(leaves) if "-t0-" in n and n.endswith(".yaml"))
    return os.path.join(leaves, names[-1]) if names else None


def node_is_approved(node: str) -> tuple:
    """(approved, detail) read the same way the render gate reads it."""
    leaf = newest_t0_leaf(node)
    if not leaf:
        return False, "no *-t0-*.yaml leaf under %s" % node
    with open(leaf, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if s.startswith("approved_by:"):
                value = s.split(":", 1)[1].strip()
                if "#" in value and not value.startswith(("'", '"')):
                    value = value.split("#", 1)[0].strip()
                value = value.strip("'\"")
                if value.startswith("founder"):
                    return True, "%s: approved_by %s" % (os.path.basename(leaf), value)
                return False, "%s: approved_by %s" % (os.path.basename(leaf), value)
    return False, "%s: no approved_by key" % os.path.basename(leaf)


def load_spec(path: str) -> dict:
    """Read a job spec. yaml if pyyaml is here, json otherwise."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if path.endswith(".json"):
        return json.loads(text)
    try:
        import yaml
    except ImportError:
        sys.exit("!! pyyaml not available and %s is not json" % path)
    return yaml.safe_load(text)


def to_job(spec: dict) -> dict:
    """Spec (repo vocabulary) -> job (what box_runner executes).

    Only the keys the runner reads are copied through. Everything else in a spec
    -- consumer, success, why, gate -- is planning metadata that stays in the
    repo file, where a person reads it, rather than riding to the box as noise.
    """
    jid = spec.get("id")
    if not jid:
        sys.exit("!! spec has no id")
    if spec.get("stamp_id", True) and not jid[-10:].isdigit():
        jid = "%s-%d" % (jid, int(time.time()))
    job = {
        "id": jid,
        "task": spec.get("task", spec.get("id")),
        "node": spec.get("node"),
        "beat": spec.get("beat"),
        "worker": "box-runner",
        "priority": spec.get("priority", 100),
        "needs_gpu": bool(spec.get("needs_gpu", True)),
        "max_attempts": int(spec.get("max_attempts", 1)),
        "env": spec.get("env") or {},
        "steps": spec.get("steps") or [],
        "artifacts": spec.get("artifacts") or [],
    }
    if not job["steps"]:
        sys.exit("!! spec %s has no steps" % jid)
    for i, step in enumerate(job["steps"]):
        if not step.get("argv"):
            sys.exit("!! spec %s step %d has no argv" % (jid, i))
    return job


def gate_checks(spec: dict, job: dict) -> list:
    problems = []
    for key in ("gate", "gate_ref"):
        if spec.get(key):
            problems.append("BLOCKED: spec carries %s: %s -- clearing it is a human "
                            "deleting the key, not this script" % (key, spec[key]))
    if spec.get("recipe_slot"):
        problems.append("BLOCKED: unfilled recipe_slot %r -- the value is the recipe "
                        "and inventing one is scaling an unapproved result"
                        % spec["recipe_slot"])
    if not spec.get("consumer"):
        problems.append("no consumer named -- standing rule is no work without one")
    node = job.get("node")
    if node:
        ok, detail = node_is_approved(node)
        print("  node %-28s %s" % (node, detail))
        if not ok:
            problems.append("node %s is NOT founder-approved -- enqueueing it would "
                            "SystemExit the daemon, not just fail the job" % node)
    elif job["needs_gpu"]:
        problems.append("gpu job names no node, so approval cannot be checked")
    return problems


def norm_dest(dest: str) -> str:
    """A box path in the one spelling two specs can be compared in.

    The box is Windows: `C:\\banyan-farm\\X` and `c:/banyan-farm/x` are one file,
    and a spec written by hand may use either. Comparing the raw strings would
    let a collision through on nothing but a capital letter.
    """
    s = str(dest).strip().replace("/", "\\").rstrip("\\")
    while "\\\\" in s:
        s = s.replace("\\\\", "\\")
    return s.lower()


def payload_dests(spec: dict) -> list:
    """The box paths a spec writes before its job runs."""
    return [str(d) for d in (spec.get("payload") or {})]


def payload_collisions(mine: dict, entries: list, live_ids, now: float,
                       grace: float = RESERVE_GRACE_SEC) -> list:
    """Problems naming every payload path already claimed by a live job.

    `mine` is a reservation dict (rid/job/ts/dests); `entries` are the ones
    already in the index, which on the second (post-reservation) call includes
    `mine` itself -- matched by `rid`, so a job never collides with its own
    claim. `live_ids` is the set of job ids sitting in the box's ready/ and
    running/ right now, or None for "could not look", which drops the check back
    to the grace window alone.

    A recorded claim blocks when its job is still queued on the box, or when it
    is younger than `grace` -- the second half is what catches a twin enqueued
    during the seconds before its sibling reaches ready/, which is the whole
    original bug and the one case the box could not have answered.

    Two claims written in that same gap would otherwise refuse each other and
    both stall, so ties go to the earlier (ts, job): the first writer proceeds,
    the second is told whose path it is. Refusal is by PATH, not by id -- a job
    re-enqueued while its previous run is still queued is refused too, because
    the harm is identical (its payload overwrites what the queued job will read)
    and it stops being a collision the moment that run leaves the queue.
    """
    mine_paths = {norm_dest(d): d for d in mine.get("dests") or []}
    problems = []
    for e in entries:
        if e.get("rid") == mine.get("rid"):
            continue
        queued = live_ids is not None and e.get("job") in live_ids
        reserved = (now - float(e.get("ts") or 0)) < grace
        if not (queued or reserved):
            continue
        for dest in e.get("dests") or []:
            key = norm_dest(dest)
            if key not in mine_paths:
                continue
            if not queued and (mine.get("ts"), mine.get("job")) < (e.get("ts"), e.get("job")):
                continue  # we claimed it first; the other writer is the one that yields
            problems.append(
                "BLOCKED: payload path %s is already claimed by %s job %s -- payloads "
                "are written at enqueue time, so this one would overwrite that job's "
                "inputs before it runs and the box would render one clip under both "
                "names. Give this job its own directory or its own filenames."
                % (mine_paths[key], "queued" if queued else "just-enqueued", e.get("job")))
    return problems


def read_payload_index(path: str = None) -> list:
    """Every reservation this machine has recorded. Missing file = none yet.

    A damaged line is skipped rather than fatal: the index is a guard's memory,
    and one unparseable row must not become the thing that stops every render.
    """
    path = path or PAYLOAD_INDEX  # read at call time so a test can redirect it
    entries = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and row.get("dests"):
                    entries.append(row)
    except OSError:
        pass
    return entries


def reserve_payload(mine: dict, path: str = None) -> None:
    """Claim this job's payload paths BEFORE a byte of payload is sent.

    Recording after the scp would leave the claim unwritten during the seconds
    the scp takes -- which is the window the twin arrived in. One line, one
    append, so a peer lane appending at the same moment cannot interleave with
    it or clobber it the way a rewritten json would.
    """
    path = path or PAYLOAD_INDEX
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(mine, ensure_ascii=False) + "\n")


QUEUE_MARKER = "QUEUE-LISTED"


def parse_queue_listing(stdout: str):
    """Job ids out of a `dir /b` of ready/ and running/, or None for "no answer".

    `dir /b` exits 1 on an EMPTY directory, so a return code cannot tell an empty
    queue from a dead ssh -- and reading a dead ssh as an empty queue is what
    would wave the next collision through. The marker echoed after both listings
    is the difference: it only appears if cmd ran our line to the end.
    """
    out = stdout or ""
    if QUEUE_MARKER not in out:
        return None
    ids = set()
    for line in out.splitlines():
        line = line.strip()
        if line.lower().endswith(".json"):
            ids.add(line[:-5])
    return ids


def queued_job_ids():
    """(ids, None) for what is in ready/ and running/, or (None, why-not)."""
    r = ssh('dir /b %s\\ready\\*.json 2>nul & dir /b %s\\running\\*.json 2>nul & '
            'echo %s' % (QUEUE_ROOT, QUEUE_ROOT, QUEUE_MARKER))
    ids = parse_queue_listing(r.stdout)
    if ids is None:
        return None, (r.stderr or r.stdout or "ssh returned nothing").strip()[:200]
    return ids, None


def send_payload(payload: dict) -> None:
    """Write a spec's `payload:` files onto the box before the job goes live.

    An LTX render needs a positive file, a negative file and a two-stage jobs
    json, all at absolute paths, before its first step runs. Without this every
    render would need a bespoke driver script committed alongside it -- which is
    how the repo has done it so far, one run-bNN.cmd per round, none reusable.
    Shipping them as part of the spec keeps the whole job in one reviewable file.

    Files land BEFORE the job is moved into ready/, so the runner can never
    claim a job whose inputs are still in flight.
    """
    if not payload:
        return
    # Its own directory, not /tmp/payload-<basename>: the box-side collision this
    # script now refuses had a local twin sitting right here. Two lanes sending a
    # payload named b01-fig-prompt.txt shared one staging file, so one lane's text
    # could be scp'd under the other's name -- the same swap, one machine earlier.
    stage = tempfile.mkdtemp(prefix="box-payload-")
    for dest, body in payload.items():
        local = os.path.join(stage, os.path.basename(dest))
        with open(local, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body if isinstance(body, str) else json.dumps(body, indent=2))
        parent = dest.rsplit("\\", 1)[0]
        ssh('if not exist "%s" mkdir "%s"' % (parent, parent))
        cp = subprocess.run(["scp", "-o", "ConnectTimeout=25", local,
                             "%s:%s" % (SSH_HOST, dest.replace("\\", "/"))],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=120)
        if cp.returncode:
            sys.exit("!! payload scp failed for %s: %s" % (dest, cp.stderr or cp.stdout))
        print("  payload -> %s" % dest)


def enqueue(job: dict) -> None:
    name = job["id"] + ".json"
    local = os.path.join("/tmp", name)
    with open(local, "w", encoding="utf-8") as fh:
        json.dump(job, fh, indent=2, ensure_ascii=False)
    ssh('if not exist %s mkdir %s' % (STAGING, STAGING))
    cp = subprocess.run(["scp", "-o", "ConnectTimeout=25", local,
                         "%s:%s/%s" % (SSH_HOST, STAGING.replace("\\", "/"), name)],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", timeout=120)
    if cp.returncode:
        sys.exit("!! scp failed: %s" % (cp.stderr or cp.stdout))
    # move, not copy: the runner claims by renaming out of ready/, so a file
    # must never be visible there while it is still being written.
    mv = ssh('move /Y %s\\%s %s\\ready\\%s' % (STAGING, name, QUEUE_ROOT, name))
    if mv.returncode:
        sys.exit("!! move into ready/ failed: %s" % (mv.stderr or mv.stdout))
    print("  queued %s" % name)


def show_queue() -> int:
    r = ssh('echo [ready] & dir /b %s\\ready 2>nul & echo [running] & '
            'dir /b %s\\running 2>nul & echo [done] & dir /b %s\\done\\*.json 2>nul & '
            'echo [failed] & dir /b %s\\failed\\*.json 2>nul'
            % (QUEUE_ROOT, QUEUE_ROOT, QUEUE_ROOT, QUEUE_ROOT))
    sys.stdout.write(r.stdout)
    if r.stderr.strip():
        sys.stderr.write(r.stderr)
    return r.returncode


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="enqueue a job on the rtx5090 box queue")
    ap.add_argument("spec", nargs="*", help="pipeline/jobs/<id>.yaml")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate and print the job json, touch nothing")
    ap.add_argument("--list", action="store_true", help="show the box queue and exit")
    args = ap.parse_args(argv)

    if args.list:
        return show_queue()
    if not args.spec:
        ap.error("give at least one spec, or --list")

    # What the box has queued right now, read ONCE. A real enqueue may not
    # proceed without it: writing payloads while unable to check whose paths
    # they are is the failure this guard exists for, and "the check could not
    # run" is not a pass. A dry run stays usable off the network -- it writes
    # nothing -- and says out loud that it only checked the grace window.
    live_ids = None
    if args.dry_run:
        print("(dry run: box queue not read -- collision check covers only "
              "enqueues from the last %ds)" % RESERVE_GRACE_SEC)
    else:
        live_ids, why = queued_job_ids()
        if live_ids is None:
            sys.exit("!! cannot read the box queue (%s) -- the payload collision "
                     "guard cannot run, so nothing was sent or queued" % why)

    failures = 0
    # A dry run writes no reservation, so specs named together on one command
    # line would not see each other -- and checking a pair before sending it is
    # the whole reason to dry-run a pair. These stand in for the index lines a
    # real run would have written.
    pending = []
    for path in args.spec:
        print("%s" % path)
        spec = load_spec(path)
        job = to_job(spec)
        problems = gate_checks(spec, job)
        # rid identifies THIS claim, so the re-read below can tell our own line
        # from a peer's. pid+ns is unique across lanes on one machine.
        mine = {"rid": "%d-%d" % (os.getpid(), time.time_ns()),
                "job": job["id"], "ts": time.time(), "spec": path,
                "dests": payload_dests(spec)}
        problems += payload_collisions(mine, read_payload_index() + pending,
                                       live_ids, mine["ts"])
        if problems:
            for p in problems:
                print("  !! %s" % p)
            failures += 1
            continue
        if args.dry_run:
            pending.append(mine)
            for dest in (spec.get("payload") or {}):
                print("  would send payload -> %s" % dest)
            print(json.dumps(job, indent=2)[:2000])
            print("  (dry run -- not queued)")
            continue
        if mine["dests"]:
            # Claim, then re-read: a peer lane that appended between our check and
            # our claim is only visible on the second look, and one of the two has
            # to lose. Still nothing written to the box at this point.
            reserve_payload(mine)
            problems = payload_collisions(mine, read_payload_index(), live_ids, mine["ts"])
            if problems:
                for p in problems:
                    print("  !! %s" % p)
                failures += 1
                continue
        send_payload(spec.get("payload"))
        enqueue(job)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
