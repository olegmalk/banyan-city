#!/usr/bin/env python3
"""A queue drainer for one Mac, so the machine keeps working when nobody is watching.

WHY THIS EXISTS. Every idle-machine failure in this project has one shape: the
machine is fine, the work exists, and nothing hands one to the other. The 5090
idled eleven hours on 2026-08-17 after six jobs failed in three minutes. The
Macs idled twenty-one hours the same night. `farm-results-m1pro`'s last
heartbeat is 2026-08-07 while mac plates kept landing in `farm-out` through
08-17 -- because lanes drove them by hand over ssh and the machines stopped the
moment a lane stopped watching.

The 5090 does not have this problem: `C:\\banyan-queue` plus a scheduled autofill
every three minutes. This is that, for a Mac, in one file.

WHAT IT DELIBERATELY IS NOT. It does not author work -- an empty queue is an
empty queue and it says so rather than inventing a job, which is the same
standing rule `box_autofill.py` obeys ("NOTHING WAS INVENTED"). It does not
retry: a job that fails goes to `failed/` with its log and stays there, because
the failure mode that cost eleven hours was six jobs failing identically and a
retry loop would have burned the night reproducing it. It does not judge, score
or pick.

LAYOUT, mirroring the box so there is one vocabulary for the whole farm:

    ~/banyan-queue/ready/<id>.json     picked up in sorted order
                   running/<id>.json   moved here while the command runs
                   done/<id>.json      + <id>.log
                   failed/<id>.json    + <id>.log
                   heartbeat.jsonl     one line per poll, so liveness is a fact

A job file is:

    {"id": "ep2-b08-scale-0818", "argv": ["/path/venv/bin/python3", "...", "--beat", "8"],
     "cwd": "/Users/macbook1/banyan-city", "timeout_s": 1800}

`argv` is a LIST and is never passed through a shell. A string command would
make quoting the failure mode, and this project has already lost a night to a
Windows path mangled by a POSIX basename.

RUN IT under caffeinate so the lid closing does not stop the farm:

    nohup caffeinate -dimsu python3 ~/banyan-city/pipeline/mac_worker.py \\
        >> ~/banyan-queue/worker.log 2>&1 &

It needs no venv of its own -- it only shells out to whatever `argv` names, so
the system python3 is enough.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

QUEUE = Path(os.path.expanduser("~/banyan-queue"))
DIRS = ("ready", "running", "done", "failed")
POLL_S = 5
# A job that has not finished in this long is stuck rather than slow. A plate at
# 832x1216 / 40 steps measures 70-140 s on these machines, so half an hour is
# twenty times the longest observed run and will only fire on a real hang.
DEFAULT_TIMEOUT_S = 1800


def ensure_dirs():
    for d in DIRS:
        (QUEUE / d).mkdir(parents=True, exist_ok=True)


def beat(event, **kw):
    """One line per poll. Liveness has to be readable from another machine.

    `lane liveness cannot be inferred` is a standing lesson here: a claim file
    or a handoff note lags reality in both directions, and one `ps` cannot tell
    "idle" from "just started". A timestamped append-only line can.
    """
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "event": event, "host": os.uname().nodename.split(".")[0]}
    rec.update(kw)
    with open(QUEUE / "heartbeat.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            job = json.load(fh)
        return job if isinstance(job, dict) and job.get("argv") else None
    except (OSError, ValueError):
        return None


def run_one(path):
    job = load(path)
    if job is None:
        # Unreadable is not runnable, and it must not sit in ready/ being
        # re-read every five seconds forever.
        bad = QUEUE / "failed" / path.name
        shutil.move(str(path), str(bad))
        with open(str(bad) + ".log", "w", encoding="utf-8") as fh:
            fh.write("unreadable or missing argv -- refused without running\n")
        beat("job_refused", job=path.stem, why="unreadable")
        return

    jid = str(job.get("id") or path.stem)
    running = QUEUE / "running" / path.name
    shutil.move(str(path), str(running))
    beat("job_start", job=jid)

    argv = [str(a) for a in job["argv"]]
    # REFUSE A TILDE, whoever filed it. subprocess does no shell expansion, so
    # "~/venv/bin/python3" is a literal path that cannot exist and the job dies
    # rc=125 having done nothing. Caught here rather than only in the filer,
    # because the queue is the thing every future filer talks to.
    bad = [a for a in argv if a.startswith("~")]
    if bad:
        dest = QUEUE / "failed" / path.name
        shutil.move(str(running), str(dest))
        with open(str(dest) + ".log", "w", encoding="utf-8") as fh:
            fh.write("REFUSED before running: argv contains an unexpanded tilde %r.\n"
                     "subprocess does not expand ~; give an absolute path.\n" % bad)
        beat("job_refused", job=jid, why="tilde in argv")
        return
    cwd = job.get("cwd") or str(Path.home())
    timeout = float(job.get("timeout_s") or DEFAULT_TIMEOUT_S)
    started = time.time()
    try:
        p = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=timeout)
        rc, out = p.returncode, p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        rc, out = 124, "TIMEOUT after %.0fs -- killed\n" % timeout
    except Exception as exc:                      # noqa: BLE001 - report, never crash the drainer
        rc, out = 125, "worker could not start the job: %r\n" % (exc,)
    secs = round(time.time() - started, 1)

    dest = QUEUE / ("done" if rc == 0 else "failed") / path.name
    shutil.move(str(running), str(dest))
    with open(str(dest) + ".log", "w", encoding="utf-8") as fh:
        fh.write("argv: %s\ncwd: %s\nrc: %d  seconds: %s\n\n%s"
                 % (json.dumps(argv), cwd, rc, secs, out))
    beat("job_done" if rc == 0 else "job_failed", job=jid, rc=rc, seconds=secs)
    print("[%s] %s rc=%d %ss" % (time.strftime("%H:%M:%S"), jid, rc, secs), flush=True)


def main():
    ensure_dirs()
    beat("worker_start", pid=os.getpid())
    print("mac_worker draining %s" % QUEUE, flush=True)
    idle_logged = False
    while True:
        ready = sorted((QUEUE / "ready").glob("*.json"))
        if not ready:
            # Say "idle" ONCE per idle stretch, not every five seconds. A log
            # that repeats itself is a log nobody reads at 3am.
            if not idle_logged:
                beat("worker_idle", ready=0)
                idle_logged = True
            time.sleep(POLL_S)
            continue
        idle_logged = False
        run_one(ready[0])


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        beat("worker_stop")
        sys.exit(0)
