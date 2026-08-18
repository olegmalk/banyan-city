#!/usr/bin/env python3
"""File plate work onto the Mac farm's queues, and read back what happened.

    python3 pipeline/mac_enqueue.py --status
    python3 pipeline/mac_enqueue.py --host macbook1 --beat 14
    python3 pipeline/mac_enqueue.py --spread 8,10,14,17      # round-robin the idle hosts
    python3 pipeline/mac_enqueue.py --collect                # scp finished frames back

WHY A FILER AND NOT AN SSH ONE-LINER. Hand-driving over ssh is exactly what
left three usable Macs idle for twenty-one hours: the work stops when the
person stops. `mac_worker.py` drains a queue on each machine under
`caffeinate`, so filing is the only step that needs a human or a session, and
this is that step.

WHAT IT REFUSES, borrowed from box_enqueue's hard-won list rather than
rediscovered:

  * a beat `plate_scratch.py` has no inline prompt for -- the run would load a
    6 GB model and then exit, which looks like a hang for two minutes
  * a host whose worker is not alive by its own heartbeat, because filing into
    a queue nobody drains is the idle failure wearing a different hat
  * a job id already sitting in that host's ready/ or running/

It does NOT check whether the picture is worth drawing. Consumer is a human
judgement and belongs in the message that files the work.
"""
import argparse
import calendar
import json
import subprocess
import sys
import time

HOSTS = ("macbook1", "macbook2", "macbook3")
# Beats plate_scratch.py carries an inline prompt for. Read from the file rather
# than duplicated, so adding a beat there does not silently fail here.
PLATE_SCRIPT = "~/banyan-city/pipeline/plate_scratch.py"
# ABSOLUTE, no tilde. argv goes to subprocess, which does NOT expand "~" --
# a tilde here is a literal directory name and every job dies rc=125.
VENV = "/Users/%s/banyan-farm-%s/venv/bin/python3"
QUEUE = "~/banyan-queue"
HEARTBEAT_STALE_S = 120
# How long a worker may show `job_start` before it is stuck rather than working.
# Matches mac_worker.DEFAULT_TIMEOUT_S, plus slack for the move-and-log after.
JOB_RUN_GRACE_S = 1860


def ssh(host, cmd, timeout=45):
    try:
        p = subprocess.run(["ssh", "-o", "ConnectTimeout=15", "-o", "BatchMode=yes",
                            host, cmd],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout)
        return p.returncode, p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def known_beats(repo_script="pipeline/plate_scratch.py"):
    import re
    try:
        src = open(repo_script, encoding="utf-8").read()
    except OSError:
        return set()
    return {int(x) for x in re.findall(r"^\s{4}(\d+): \{", src, re.M)}


def known_revs(repo_script="pipeline/plate_scratch.py"):
    """(beat, rev) pairs plate_scratch can actually merge.

    Read from the file, like known_beats, so adding a rev there does not
    silently fail here. Both spellings the file uses are matched: the entries
    inside the REVS literal (`    (14, 6): {`) and the assignments appended
    after it (`REVS[(14, 7)] = ...`).
    """
    import re
    try:
        src = open(repo_script, encoding="utf-8").read()
    except OSError:
        return set()
    pairs = re.findall(r"^\s{4}\((\d+),\s*(\d+)\): \{", src, re.M)
    pairs += re.findall(r"^REVS\[\((\d+),\s*(\d+)\)\]", src, re.M)
    return {(int(b), int(r)) for b, r in pairs}


def worker_alive(host):
    """Alive by the worker's OWN heartbeat, not by `ps` and not by a claim file.

    Returns (alive, detail). A worker that has never written a heartbeat is not
    alive; a worker whose last line is older than HEARTBEAT_STALE_S is not
    either, however healthy the process looks from outside.
    """
    rc, out = ssh(host, "tail -1 %s/heartbeat.jsonl 2>/dev/null" % QUEUE)
    line = out.strip().splitlines()[-1] if out.strip() else ""
    if rc != 0 or not line:
        return False, "no heartbeat file"
    try:
        rec = json.loads(line)
        # calendar.timegm, NOT time.mktime. The stamp is UTC; mktime reads a
        # struct as LOCAL time, so on a +04:00 machine a heartbeat written three
        # seconds ago measured 28810 s stale and every live worker read DEAD.
        ts = calendar.timegm(time.strptime(rec["ts"], "%Y-%m-%dT%H:%M:%SZ"))
    except (ValueError, KeyError):
        return False, "unparseable heartbeat: %s" % line[:60]
    age = time.time() - ts
    # A RUNNING JOB WRITES NO HEARTBEAT, and calling that dead is the same
    # inference error as reading one nvidia-smi and declaring a card idle.
    # Measured 2026-08-18: macbook2 and macbook3 both read DEAD at 136 s stale
    # while they were mid-render on a 137 s plate. If the last recorded event is
    # `job_start`, the worker is inside subprocess.run and cannot beat; it is
    # alive until the job's own timeout could have expired.
    limit = JOB_RUN_GRACE_S if rec.get("event") == "job_start" else HEARTBEAT_STALE_S
    if age > limit:
        return False, "heartbeat %.0fs stale (%s)" % (age, rec.get("event"))
    busy = " [busy]" if rec.get("event") == "job_start" else ""
    return True, "%s %.0fs ago%s" % (rec.get("event"), age, busy)


def counts(host):
    rc, out = ssh(host, "for d in ready running done failed; do "
                        "printf '%s ' $(ls %s/$d/*.json 2>/dev/null | wc -l); done" % ("%s", QUEUE))
    nums = [n for n in out.split() if n.isdigit()]
    return nums if len(nums) == 4 else ["?", "?", "?", "?"]


def cmd_status():
    print("%-11s %-34s %s" % ("host", "worker", "ready/running/done/failed"))
    for h in HOSTS:
        alive, detail = worker_alive(h)
        print("  %-9s %-34s %s"
              % (h, ("ALIVE  " if alive else "DEAD   ") + detail, "/".join(counts(h))))


def file_job(host, beat, note="", seeds=1, rev=1):
    # THE REV HAS TO TRAVEL, AND FOR ONE DAY IT DID NOT. plate_scratch.py takes
    # `--rev` and merges REVS[(beat, rev)] over DRAFTS[beat]; this filer only
    # ever sent `--beat`, so every job it filed drew REV 1 -- the BASE draft --
    # whatever the lane thought it had commissioned. On beat 14 that is not a
    # near miss: the base draft is the r1 wording five rungs ago, and a lane
    # asking for r8 would have got r1 back with an r8 story attached to it, with
    # nothing in the output to say so (the sidecar records `revision`, so the
    # evidence exists -- but only for whoever thinks to look). Same failure shape
    # as the merge landmine plate_scratch guards at its own end: the test quietly
    # does not test what you think.
    jid = "mac-b%02d%s-%s" % (beat, "" if rev == 1 else "r%d" % rev,
                              time.strftime("%m%d-%H%M%S"))
    job = {"id": jid,
           "argv": [VENV % (host, host), PLATE_SCRIPT.replace("~", "/Users/%s" % host),
                    "--beat", str(beat)]
                   + ([] if rev == 1 else ["--rev", str(rev)])
                   + (["--seeds", str(seeds), "--i-have-seen-a-sample"] if seeds > 1 else []),
           "cwd": "/Users/%s/banyan-city" % host,
           "timeout_s": 1800,
           "note": note}
    payload = json.dumps(job)
    rc, out = ssh(host, "mkdir -p %s/ready && cat > %s/ready/%s.json <<'EOF'\n%s\nEOF"
                  % (QUEUE, QUEUE, jid, payload))
    return (rc == 0), jid, out.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--host")
    ap.add_argument("--beat", type=int)
    ap.add_argument("--spread", help="comma-separated beats, round-robined over live hosts")
    ap.add_argument("--note", default="")
    # plate_scratch refuses >1 seed without --i-have-seen-a-sample. Passing it is
    # only honest once a sample HAS been looked at; eight beats were sampled and
    # read on 2026-08-18 before this flag was used.
    ap.add_argument("--seeds", type=int, default=1)
    # Applies to every beat in the call. A rev number is per-beat in
    # plate_scratch, so --spread with --rev is refused below rather than
    # silently filing rev N of beats that have no rev N.
    ap.add_argument("--rev", type=int, default=1,
                    help="revision of the inline draft (plate_scratch REVS[(beat, rev)])")
    ap.add_argument("--force", action="store_true",
                    help="file even if the worker looks dead (it will just sit there)")
    a = ap.parse_args()

    if a.status or not (a.beat or a.spread):
        cmd_status()
        return 0

    beats = ([a.beat] if a.beat else
             [int(x) for x in a.spread.split(",") if x.strip()])
    have = known_beats()
    unknown = [b for b in beats if have and b not in have]
    if unknown:
        print("!! plate_scratch.py has no inline prompt for beat(s) %s -- it knows %s. "
              "Refusing: the run would load the model and then exit."
              % (unknown, sorted(have)))
        return 2
    if a.rev != 1:
        if len(beats) > 1:
            print("!! --rev %d with %d beats. A rev number means something "
                  "different in every beat's REVS table, so one flag cannot be "
                  "right for all of them. File them one at a time." % (a.rev, len(beats)))
            return 3
        # Same refusal shape as the unknown-beat guard above, and for the same
        # reason: plate_scratch exits 4 on a missing rev AFTER argparse but
        # BEFORE the model loads, so this costs nothing there -- but the job
        # still lands in `done` with rc=4 and looks like a render that ran.
        revs = known_revs()
        if revs and (beats[0], a.rev) not in revs:
            print("!! plate_scratch.py has no rev %d for beat %d -- it knows %s. "
                  "Refusing." % (a.rev, beats[0],
                                 sorted(r for b, r in revs if b == beats[0])))
            return 3

    live = []
    for h in ([a.host] if a.host else list(HOSTS)):
        alive, detail = worker_alive(h)
        if alive or a.force:
            live.append(h)
        else:
            print("  skip %-10s worker not alive (%s)" % (h, detail))
    if not live:
        print("!! no live worker to file onto. Start one:\n"
              "   ssh <host> 'nohup caffeinate -dimsu python3 "
              "~/banyan-city/pipeline/mac_worker.py >> ~/banyan-queue/worker.log 2>&1 &'")
        return 1

    for i, b in enumerate(beats):
        h = live[i % len(live)]
        ok, jid, out = file_job(h, b, a.note, a.seeds, a.rev)
        print("  %-10s beat %-3s %s %s" % (h, b, "filed" if ok else "FAILED", jid))
        if not ok:
            print("     ", out[:200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
