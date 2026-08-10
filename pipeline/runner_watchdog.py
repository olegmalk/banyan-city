#!/usr/bin/env python3
"""Restart the box runner when it wedges — the failure schtasks cannot see.

On 2026-08-10 at 19:29 the runner claimed `ep1-b10-v34-plate-r2g`, finished it,
and then stopped claiming anything for sixteen minutes while twelve jobs sat in
`ready`. Throughout, `schtasks /query` reported `Status: Running` and the
runner's own log simply stopped. No crash, no error, no failed job — a wedged
process describing itself as healthy. `schtasks /end` then `/run` cleared it
instantly. It was caught only because a human happened to be watching; with
nobody there the card would have sat dead for hours.

THE DETECTION RULE, and why each clause is in it:

  ready >= 1      Silence with an empty queue is CORRECT, not a wedge. The
                  runner is supposed to be quiet when there is nothing to draw,
                  and on the night this was written that was the normal state
                  for hours. Firing on an idle-but-empty queue would restart a
                  healthy runner forever.
  running == 0    A claimed job is a live job. Never restart over one.
  no big python   A render holds ~13-47 GB resident. The runner loop itself sits
                  at ~12 MB. Anything multi-GB means work is happening even if
                  the log is briefly quiet.
  log age > 8min  The real threshold. Measured job durations on this box:
                  LTX motion 4m38s-4m48s (five samples, tight), SDXL stills
                  4m30s-5m20s, sky stills 31-79s, goblin IPA ~2m50s. The longest
                  observed job is 5m20s, so 8 minutes clears the slowest real
                  job with margin and still catches a wedge inside one tick.

WHAT IT DELIBERATELY WILL NOT DO:

Fire during a model load. An LTX job spends its first ~90s loading a 24 GB text
encoder at 0% GPU and 0 MiB — indistinguishable from idle on the GPU counters
alone. That misread put two lanes on one finished job on 2026-08-10. This
watchdog never consults `nvidia-smi`; it reads the queue, the process table and
the log mtime, all of which move during a load.

Restart forever. Three restarts inside the escalation window means the runner is
not transiently wedged, it is broken — and a watchdog that keeps papering over
that is itself a thing reporting healthy while dead, which is the exact pattern
it exists to end. After the third it refuses to restart and says so loudly.

    python3 pipeline/runner_watchdog.py            # check, restart if wedged
    python3 pipeline/runner_watchdog.py --dry-run  # report only, never restart
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time

HOST = "rtx5090"
QUEUE = r"C:\banyan-queue"
TASK = "banyan-box-runner"

# Longest observed job is 5m20s (SDXL still). 8 min clears it with margin.
STALL_SECONDS = 8 * 60
# A render holds gigabytes; the runner loop itself is ~12 MB.
BIG_PROCESS_KB = 500_000
# Three restarts in an hour is a broken runner, not a transient wedge.
MAX_RESTARTS = 3
ESCALATE_WINDOW = 60 * 60

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                     "ledger", "watchdog-state.json")
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "ledger", "watchdog.log")


def box(cmd, timeout=30):
    """One command on the box. `cd C:\\ &&` first — the default cwd does not
    exist and silently corrupts anything chained after it."""
    # encoding is named explicitly: the box's logs carry non-UTF8 progress-bar
    # bytes, and an unnamed decode raises on them instead of returning output.
    r = subprocess.run(
        ["ssh", "-n", "-o", "ConnectTimeout=10", HOST, f"cd C:\\ && {cmd}"],
        capture_output=True, text=True, timeout=timeout,
        encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.replace("\r", "")


def queue_counts():
    out = {}
    for d in ("ready", "running", "done", "failed"):
        rc, s = box(f"dir /b {QUEUE}\\{d} 2>nul")
        out[d] = len([x for x in s.splitlines() if x.strip().endswith(".json")])
    return out


def big_render_running():
    rc, s = box('tasklist /fi "imagename eq python.exe"')
    for line in s.splitlines():
        m = re.search(r"([\d,]+)\s*K\s*$", line.strip())
        if m and int(m.group(1).replace(",", "")) >= BIG_PROCESS_KB:
            return True
    return False


def log_age_seconds():
    """Seconds since the runner last wrote. None if unreadable — treated as
    'do not fire', because an unreadable log is a broken probe, not evidence
    of a wedge, and acting on a broken probe is how the disk got wiped today."""
    rc, s = box(
        'powershell -NoProfile -Command "'
        "(Get-Date) - (Get-Item 'C:\\banyan-queue\\runner.log').LastWriteTime "
        '| Select-Object -ExpandProperty TotalSeconds"')
    try:
        return float(s.strip().split()[0])
    except (ValueError, IndexError):
        return None


def load_state():
    try:
        with open(STATE) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"restarts": []}


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as fh:
        json.dump(st, fh, indent=2)


def note(msg):
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"{stamp} {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def diagnose(q, big, age):
    """The rule, in one place so the test can drive it directly."""
    if q["ready"] < 1:
        return False, "queue empty — silence is correct, nothing to draw"
    if q["running"] > 0:
        return False, f"a job is claimed ({q['running']} running)"
    if big:
        return False, "a render process is resident — work is happening"
    if age is None:
        return False, "runner log unreadable — broken probe, not evidence"
    if age <= STALL_SECONDS:
        return False, f"log wrote {int(age)}s ago, under the {STALL_SECONDS}s bar"
    return True, (f"WEDGED: {q['ready']} queued, none claimed, no render "
                  f"process, log silent {int(age)}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="report only, never restart")
    a = ap.parse_args()

    q = queue_counts()
    big = big_render_running()
    age = log_age_seconds()
    wedged, why = diagnose(q, big, age)

    summary = (f"ready={q['ready']} running={q['running']} done={q['done']} "
               f"failed={q['failed']} log_age="
               f"{'?' if age is None else int(age)}s big_proc={big}")

    if not wedged:
        print(f"OK  {summary}  ({why})")
        return 0

    note(f"{why} | {summary}")

    st = load_state()
    now = time.time()
    recent = [t for t in st["restarts"] if now - t < ESCALATE_WINDOW]

    if len(recent) >= MAX_RESTARTS:
        note(f"!! ESCALATE: {len(recent)} restarts in the last hour and it has "
             f"wedged again. NOT restarting — this is a broken runner, not a "
             f"transient wedge, and restarting it again would hide that. "
             f"Needs a human.")
        st["restarts"] = recent
        save_state(st)
        return 2

    if a.dry_run:
        note("dry-run: would restart, did not")
        return 1

    rc1, o1 = box(f"schtasks /end /tn {TASK}")
    rc2, o2 = box(f"schtasks /run /tn {TASK}")
    ok = "SUCCESS" in o2
    note(f"restart {'ok' if ok else 'FAILED'} — end: {o1.strip()[:60]} | "
         f"run: {o2.strip()[:60]}")

    recent.append(now)
    st["restarts"] = recent
    save_state(st)
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
