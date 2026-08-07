#!/usr/bin/env python3
"""Moves runnable work out of `backlog:` into `tasks:`, retires finished tasks,
and does nothing else.

Why this is a separate file from queue_keeper.py: the keeper INVENTS work (a
rotating world-reference bank) and rewrites the queue with `yaml.safe_dump`,
which flattens every comment in it. This promoter invents nothing, clears
nothing, and edits the file as TEXT so the ~200 lines of comments that record
why each entry is blocked survive a promotion. Two opposite contracts should not
share a process or a commit message.

What it does, in one commit:

  RETIRE   a `tasks:` entry with a `DONE task=<id>` line on any farm-results-*
           heartbeat. A worker already skips those, but a re-imaged box — or one
           whose heartbeat.txt was reset — sees a fresh queue and a task it has
           never run. That is how faceneg-b01-1785819600 sat live for four days
           after finishing. Only DONE retires; a FAIL stays visible.
  PROMOTE  a `backlog:` entry that is `runner: farm`, carries no `gate:`, and
           whose every `after:` id shows DONE somewhere. The dict moves from one
           list to the other in a single write, so the two lists cannot disagree.
  REPORT   manual entries that are unblocked (a person or an agent runs those —
           `tasks:` is a worker inbox and a worker would choke on a `cmd:`), and
           every blocked entry with the blocker that holds it.

Hard rules, each enforced below and held by a test:

  * A `gate:` key blocks the entry no matter what `after:` says. The promoter
    cannot clear a gate. Clearing one is a human deleting the key in a commit —
    that is what makes founder, code and hardware gates human-owned.
  * `window:` is ADVISORY and never delays anything. Machine work is scheduled
    by dependencies, not human hours (Oleg, 2026-08-05).
  * Nothing is promoted that a worker could not run: farm entries must name a
    node, name beats or a prompt, and resolve to exactly one worker string.

Usage:  python3 pipeline/queue_promoter.py [--dry-run] [--no-push]
Safe by hand and safe on a timer: idempotent, and a second run with nothing to
do writes nothing and commits nothing.
"""
import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "pipeline" / "farm-queue.yaml"

# Capability tags -> the machines that have them, and the order to prefer.
# Sourced from STATE.md's fleet rows and pipeline/research/MODEL-COMPARISON.md §4:
# rtx5090 is the 26GB CUDA box with the video venv; msi is the 5070 Ti, 12GB, so
# it has cuda and the video venv but NOT vram20; m1pro is the steward's Mac (MPS,
# no CUDA, no video venv). m2 is a stills-only Mac and is not offered work here
# because nothing in the backlog names it.
CAPS = {
    "rtx5090": {"cuda", "vram20", "video-venv"},
    "msi": {"cuda", "video-venv"},
    "m1pro": {"mps"},
}
PREFERENCE = ["rtx5090", "msi", "m1pro"]


# ---------------------------------------------------------------- heartbeats

def parse_done(text: str) -> set:
    """Ids with a DONE line. Regex, not splitlines, on purpose: the 5090 writes
    its heartbeat with bare CR line endings, so `for line in text.splitlines()`
    reads the whole file as one line on some readers and `tail` shows one entry.
    \\S excludes \\r, so the id never picks up a stray carriage return."""
    return set(re.findall(r"DONE task=(\S+)", text or ""))


def fetch_heartbeats(quiet: bool = False) -> set:
    """Every DONE id across every farm-results-* branch. Network, so it is kept
    out of the logic below and injected in tests."""
    subprocess.run(["git", "fetch", "-q", "origin",
                    "refs/heads/farm-results-*:refs/remotes/origin/farm-results-*"],
                   cwd=REPO, capture_output=True, encoding="utf-8", errors="replace")
    r = subprocess.run(["git", "for-each-ref", "--format=%(refname:short)",
                        "refs/remotes/origin/farm-results-*"],
                       cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    done = set()
    for ref in (r.stdout or "").split():
        hb = subprocess.run(["git", "show", f"{ref}:farm-out/heartbeat.txt"],
                            cwd=REPO, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
        if hb.returncode == 0:
            found = parse_done(hb.stdout)
            if found and not quiet:
                print(f"  {ref}: {len(found)} done")
            done |= found
    return done


# ------------------------------------------------------------- pure planning

def resolve_worker(entry: dict):
    """(worker, reason). An explicit worker always wins — it is what
    farm_worker.py:488 compares by string equality, and a list would never
    match. Otherwise the first machine in PREFERENCE that has every needed tag."""
    w = entry.get("worker")
    if isinstance(w, str) and w.strip():
        return w.strip(), "explicit"
    if not isinstance(w, (str, type(None))):
        return None, f"worker must be a plain string, got {type(w).__name__}"
    needs = set(entry.get("needs") or [])
    fits = [m for m in PREFERENCE if needs <= CAPS.get(m, set())]
    if not needs:
        return None, "no worker and no needs — refusing to guess"
    if not fits:
        return None, f"no machine has {sorted(needs)}"
    return fits[0], f"from needs {sorted(needs)}"


def blocker(entry: dict, done: set):
    """Why this entry cannot move, or None. Order matters: the gate is reported
    first because it is the answer a reader wants, even when `after` is also
    unmet."""
    gate = entry.get("gate")
    if gate:
        return f"gate:{gate} — {entry.get('gate_ref') or 'no gate_ref written'}"
    missing = [a for a in (entry.get("after") or []) if a not in done]
    if missing:
        return f"after — waiting on {', '.join(missing)}"
    return None


def promotable(entry: dict):
    """None if a worker could run this as written, else the structural reason it
    is not queue-shaped. Cheap checks that make an accidental worker crash
    impossible: a task with no node raises KeyError inside render_task."""
    if not entry.get("node"):
        return "farm entry names no node"
    if not (str(entry.get("beats") or "").strip() or entry.get("prompt")):
        return "farm entry names neither beats nor a prompt"
    worker, reason = resolve_worker(entry)
    if not worker:
        return reason
    return None


def plan(queue: dict, done: set) -> dict:
    """Pure. Given the parsed file and the set of DONE ids, decide everything."""
    tasks = list(queue.get("tasks") or [])
    backlog = list(queue.get("backlog") or [])
    out = {"retire": [], "promote": [], "assign": {}, "by_hand": [], "waiting": []}

    for t in tasks:
        tid = t.get("id")
        if tid and tid in done:
            out["retire"].append(tid)

    for e in backlog:
        eid = e.get("id")
        why = blocker(e, done)
        if why:
            out["waiting"].append((eid, why))
            continue
        if (e.get("runner") or "farm") != "farm":
            out["by_hand"].append((eid, e.get("cmd") or "(no cmd written)"))
            continue
        bad = promotable(e)
        if bad:
            out["waiting"].append((eid, f"not queue-shaped — {bad}"))
            continue
        worker, _ = resolve_worker(e)
        if not e.get("worker"):
            out["assign"][eid] = worker
        out["promote"].append(eid)
    return out


# -------------------------------------------------------------- text surgery
# The file is edited as text, not re-dumped, because its comments carry the
# reasoning that stops a parked job being retried (the AnimeGen post-mortem) and
# safe_dump would erase all of it.

def regions(text: str):
    """(head, tasks_lines, backlog_lines). Splits on the two top-level keys."""
    lines = text.split("\n")
    ti = next((i for i, l in enumerate(lines) if l.rstrip() == "tasks:"), None)
    bi = next((i for i, l in enumerate(lines) if l.rstrip() == "backlog:"), None)
    if ti is None:
        raise SystemExit("farm-queue.yaml has no top-level `tasks:` line")
    if bi is None or bi < ti:
        raise SystemExit("farm-queue.yaml has no top-level `backlog:` line after `tasks:`")
    return lines[:ti + 1], lines[ti + 1:bi], lines[bi:]


def blocks(region):
    """(preamble, [block, ...], tail). A block is one list entry plus the comment
    run directly above it, which is where that entry's reasoning is written.

    Three deliberate limits on how far a block reaches back, all of them there so
    that MOVING an entry can never DELETE reasoning that was not its own:

    * comment lines count only at column 0, matching this file's style, so a `#`
      inside an indented scalar is never mistaken for one;
    * the walk stops at a BLANK line rather than crossing it;
    * a run that reaches the very top of the region is region preamble, not an
      entry's comment — that is the ninety-line AnimeGen post-mortem sitting
      directly under `tasks:`, and an entry written beneath it must not carry it
      away. Such comments stay put even when the entry below them moves; orphaned
      is recoverable, deleted is not.
    """
    starts = [i for i, l in enumerate(region) if l.startswith("- ")]
    if not starts:
        return list(region), [], []
    begins = []
    for k, s in enumerate(starts):
        b = s
        while b > 0 and region[b - 1].startswith("#"):
            b -= 1
        if b == 0:                 # the run is the region's own preamble
            b = s
        if k:                      # never reach back past the previous entry
            b = max(b, starts[k - 1] + 1)
        begins.append(b)
    ends = [(begins[k + 1] - 1) if k + 1 < len(begins) else len(region) - 1
            for k in range(len(begins))]
    # trailing blank lines after the last entry belong to the file, not the entry
    last = ends[-1]
    while last > begins[-1] and region[last].strip() == "":
        last -= 1
    tail = region[last + 1:]
    ends[-1] = last
    return (region[:begins[0]],
            [region[b:e + 1] for b, e in zip(begins, ends)],
            tail)


def entry_id(block):
    """The id of the entry in this block: off the `- id:` line when the entry
    leads with it, otherwise by parsing the block's non-comment lines."""
    for line in block:
        if line.startswith("- id: "):
            return line[len("- id: "):].strip().strip("'\"")
    parsed = yaml.safe_load("\n".join(l for l in block if not l.startswith("#")))
    if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
        return parsed[0].get("id")
    return None


def rewrite(text: str, retire: list, promote: list, assign: dict, stamp: str) -> str:
    head, t_region, b_region = regions(text)
    t_pre, t_blocks, t_tail = blocks(t_region)
    b_head = [b_region[0]]
    b_pre, b_blocks, b_tail = blocks(b_region[1:])

    kept_tasks = [bl for bl in t_blocks if entry_id(bl) not in set(retire)]
    moving, kept_backlog = [], []
    for bl in b_blocks:
        (moving if entry_id(bl) in set(promote) else kept_backlog).append(bl)

    for bl in moving:
        eid = entry_id(bl)
        if eid in assign:                     # write the worker the needs implied
            bl.insert(bl.index(f"- id: {eid}") + 1, f"  worker: {assign[eid]}")
        # the blank line is load-bearing: it stops the next run's block walk from
        # reaching back into whatever comment block this landed under.
        bl[:0] = ["", f"# promoted from backlog {stamp} by queue_promoter"]

    out = (head + t_pre + [l for bl in kept_tasks for l in bl]
           + [l for bl in moving for l in bl] + t_tail
           + b_head + b_pre + [l for bl in kept_backlog for l in bl] + b_tail)
    return "\n".join(out)


def verify(before_text: str, after_text: str, retire: list, promote: list) -> None:
    """Refuse to write a file whose meaning is not exactly the plan. This is the
    guard that makes the move atomic in substance and not just in commit count:
    an entry cannot end up in both lists or in neither."""
    a = yaml.safe_load(before_text) or {}
    b = yaml.safe_load(after_text) or {}
    def by_id(d, k):
        return {e["id"]: e for e in (d.get(k) or [])}
    at, ab = by_id(a, "tasks"), by_id(a, "backlog")
    bt, bb = by_id(b, "tasks"), by_id(b, "backlog")
    want_t = (set(at) - set(retire)) | set(promote)
    if set(bt) != want_t:
        raise SystemExit(f"refusing to write: tasks would be {sorted(bt)}, "
                         f"expected {sorted(want_t)}")
    if set(bb) != set(ab) - set(promote):
        raise SystemExit(f"refusing to write: backlog would be {sorted(bb)}, "
                         f"expected {sorted(set(ab) - set(promote))}")
    for i in set(at) - set(retire):
        if bt[i] != at[i]:
            raise SystemExit(f"refusing to write: task {i} changed under a move")
    for i in promote:
        if {k: v for k, v in bt[i].items() if k != "worker"} != \
           {k: v for k, v in ab[i].items() if k != "worker"}:
            raise SystemExit(f"refusing to write: entry {i} changed in the move")


# --------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan, touch nothing")
    ap.add_argument("--no-push", action="store_true",
                    help="commit locally, do not push")
    a = ap.parse_args()

    if not a.dry_run:
        subprocess.run(["git", "pull", "-q", "--rebase", "origin", "main"], cwd=REPO,
                       capture_output=True, encoding="utf-8", errors="replace")
    text = QUEUE.read_text(encoding="utf-8")
    queue = yaml.safe_load(text) or {}
    print("heartbeats:")
    done = fetch_heartbeats()
    p = plan(queue, done)

    for tid in p["retire"]:
        print(f"RETIRE   {tid} — DONE on a heartbeat, its record is that line")
    for eid in p["promote"]:
        extra = f" (worker {p['assign'][eid]})" if eid in p["assign"] else ""
        print(f"PROMOTE  {eid}{extra}")
    for eid, cmd in p["by_hand"]:
        print(f"BY HAND  {eid} — unblocked, run: {cmd}")
    for eid, why in p["waiting"]:
        print(f"WAITING  {eid} — {why}")

    if not (p["retire"] or p["promote"]):
        print("\nnothing to move — queue and backlog already agree")
        return 0

    new = rewrite(text, p["retire"], p["promote"], p["assign"], date.today().isoformat())
    verify(text, new, p["retire"], p["promote"])
    if a.dry_run:
        print("\n--dry-run: verified, not written")
        return 0

    QUEUE.write_text(new, encoding="utf-8")
    msg = []
    if p["promote"]:
        msg.append(f"promote {', '.join(p['promote'])}")
    if p["retire"]:
        msg.append(f"retire {', '.join(p['retire'])}")
    subprocess.run(["git", "add", str(QUEUE)], cwd=REPO, check=True)
    subprocess.run(["git", "commit", "-qm", f"queue_promoter: {'; '.join(msg)}"],
                   cwd=REPO, check=True)
    if not a.no_push:
        subprocess.run(["git", "push", "-q"], cwd=REPO, check=True)
    print(f"\ncommitted: {'; '.join(msg)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
