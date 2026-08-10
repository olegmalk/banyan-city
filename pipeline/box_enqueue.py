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

    python3 pipeline/box_enqueue.py pipeline/jobs/<spec>.yaml [--dry-run]
    python3 pipeline/box_enqueue.py --list        # what is queued right now
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSH_HOST = "rtx5090"
QUEUE_ROOT = r"C:\banyan-queue"
STAGING = QUEUE_ROOT + r"\incoming"
NODES = os.path.join(REPO, "genomes", "sapling", "nodes")


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

    failures = 0
    for path in args.spec:
        print("%s" % path)
        spec = load_spec(path)
        job = to_job(spec)
        problems = gate_checks(spec, job)
        if problems:
            for p in problems:
                print("  !! %s" % p)
            failures += 1
            continue
        if args.dry_run:
            print(json.dumps(job, indent=2)[:2000])
            print("  (dry run -- not queued)")
            continue
        enqueue(job)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
