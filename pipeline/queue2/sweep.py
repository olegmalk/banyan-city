#!/usr/bin/env python3
"""startup_sweep + journal compaction, as NAMED scheduler hooks.

NO HAND-RUN STEPS (design §3.5): every recurring action here is a function
with a named caller. `queue2_sweep` is the callable entrypoint; its
schedulers, by name:

  * the worker, at its own startup (`Queue2` owners call queue2_sweep before
    the first claim) -- this is where "replaces leases" lives: with exactly
    one sequential worker per machine-local root, anything in running/ at
    startup is by definition an interrupted attempt;
  * scheduled task `banyan-queue2-sweep` (Windows box) / launchd job
    `city.banyan.queue2-sweep` (Macs), every few minutes, same cadence slot
    as banyan-box-autofill -- to be registered in pipeline/schedulers.yaml
    when v2 deploys (that file is §2.5's registry; this module ships the
    hook, deployment registers it).

WHAT THE SWEEP DOES. The directories are the queue, THE JOURNAL IS THE
HISTORY (§3.2 delta 2 -- NTFS rename is atomic but there is no directory
fsync, so after power loss directory membership is not evidence). For every
journal attempt still STARTED on this machine whose pid is gone, the death is
recorded as INTERRUPTED with a reason, and the attempt is CONSUMED: a job
that takes down its own host uses budget (the b4 WDDM ban in code -- a
machine-killing job can never loop, because its attempts were journaled
before each death). Attempts remaining -> back to ready/; cap reached ->
failed/, the first-class dead-letter. A running/ file with no live journal
row is a write-ahead violation and retires to failed/ saying so.

pid liveness is probed READ-ONLY. On Windows os.kill(pid, 0) is not a probe
-- it TERMINATES the process -- so the Windows path goes through OpenProcess/
GetExitCodeProcess. Probing a worker to death would be an incident, not a
sweep.
"""

from __future__ import annotations

import json
import os
import sys
import time

try:
    from .journal import JournalCorrupt
    from .queue2 import MAX_ATTEMPTS_DEFAULT, Queue2
except ImportError:  # run as a script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from queue2.journal import JournalCorrupt
    from queue2.queue2 import MAX_ATTEMPTS_DEFAULT, Queue2

STILL_ACTIVE = 259  # Windows GetExitCodeProcess sentinel


def pid_alive(pid) -> bool:
    if not pid:
        return False
    pid = int(pid)
    if sys.platform == "win32":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION,
                                      False, pid)
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return False
            return code.value == STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)  # signal 0: existence probe only, POSIX
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # alive, owned by someone else
    except OSError:
        return False
    return True


def startup_sweep(q: Queue2) -> dict:
    """Reconcile running/ against the journal. Returns honest counts."""
    report = {"interrupted": 0, "requeued": 0, "retired": 0, "orphaned": 0}

    for row in q.journal.started_rows(machine=q.machine):
        if pid_alive(row["pid"]):
            continue
        reason = ("process %s on %s is gone with the attempt still open -- "
                  "host death, kill, or closed window; attempt %d consumed"
                  % (row["pid"], row["machine"], row["attempt_n"]))
        if not q.journal.mark_interrupted(row["attempt_id"], reason):
            continue  # reached a terminal state between listing and marking
        report["interrupted"] += 1

        name = row["job_id"] + ".json"
        running = os.path.join(q.dir("running"), name)
        if not os.path.exists(running):
            continue  # directories lag the journal after power loss; journal wins
        with open(running, encoding="utf-8") as fh:
            job = json.load(fh)
        spent = q.journal.attempt_count(row["job_id"])
        cap = int(job.get("max_attempts", MAX_ATTEMPTS_DEFAULT))
        if spent >= cap:
            job["fail_reason"] = reason
            job["attempts"] = spent
            q._atomic_write("failed", name, job)
            os.unlink(running)
            report["retired"] += 1
        else:
            os.rename(running, os.path.join(q.dir("ready"), name))
            report["requeued"] += 1

    # A running/ file no live attempt owns: either its attempt already went
    # terminal (crash between journal write and file move -- journal wins,
    # the file is a leftover) or it was hand-placed (write-ahead violated).
    live_ids = {r["job_id"] for r in q.journal.started_rows(machine=q.machine)}
    for _, name, job in q._jobs_in("running"):
        jid = (job or {}).get("id") or name[:-len(".json")]
        if jid in live_ids:
            continue
        job = job or {"id": jid}
        job["fail_reason"] = ("running/ file with no open journal attempt -- "
                              "write-ahead violated or a crash mid-move; "
                              "the journal is the history")
        q._atomic_write("failed", name, job)
        os.unlink(os.path.join(q.dir("running"), name))
        report["orphaned"] += 1
    return report


def compact_journal(q: Queue2, keep_days: float = 14.0) -> int:
    """Retire old terminal attempt rows to an ndjson export (small text,
    the repo-committable record class) before deleting them. Export-first is
    write-ahead applied to compaction itself."""
    export = os.path.join(q.dir("control"),
                          "journal-export-%s.ndjson"
                          % time.strftime("%Y%m%d", time.gmtime()))
    return q.journal.compact(export, keep_days=keep_days)


def queue2_sweep(root: str = None, store: str = None,
                 verdicts_path: str = None, keep_days: float = 14.0,
                 q: Queue2 = None) -> int:
    """THE scheduler entrypoint (see module docstring for who calls it).
    Prints one honest line and returns a real exit code."""
    try:
        q = q or Queue2(root=root, store=store, verdicts_path=verdicts_path)
        report = startup_sweep(q)
        report["compacted"] = compact_journal(q, keep_days=keep_days)
    except JournalCorrupt as exc:
        print(exc, file=sys.stderr)
        print("QUEUE2-SWEEP: FAIL journal-corrupt", file=sys.stderr)
        return JournalCorrupt.rc
    print("QUEUE2-SWEEP: PASS " +
          " ".join("%s=%d" % (k, report[k]) for k in sorted(report)))
    return 0


if __name__ == "__main__":
    sys.exit(queue2_sweep())
