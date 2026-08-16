#!/usr/bin/env python3
r"""Keep the card's queue above a floor of MINUTES, from a standing backlog.

    (on the box, every few minutes, by scheduled task banyan-box-autofill)
    python box_autofill.py                     # one tick: measure, top up, log
    python box_autofill.py --dry-run           # say what it would file, move nothing

    (from the Mac)
    python3 pipeline/box_autofill.py --deploy           # ship + schedule it
    python3 pipeline/box_autofill.py --verify-deployed  # is the box running THIS file?
    python3 pipeline/box_autofill.py --status           # last tick, over ssh

WHY THIS EXISTS. On 2026-08-15 the GPU went idle four separate times, and three
agent sessions died on usage limits mid-work, each one stranding whatever it had
not already queued. Every refill that day was reactive: a human or an
orchestrator noticed `ready == 0`, dispatched an agent, and the agent spent
minutes spinning up before it authored anything. Queue depth was a SIDE EFFECT
of lanes finishing their own investigations, so whenever every lane was
mid-thought the card stopped. The founder: "well ya got fix your scheduling
dude. the card has been idle many many times now." A guard that lives in code
beats a habit, so this runs on the box, on a timer, and needs nobody awake.

WHAT IT WILL NOT DO, AND THIS IS THE WHOLE DESIGN. It does not author work. It
cannot: the only thing it can put in `ready/` is a job file some human or lane
already wrote, already validated through `box_enqueue.py`'s full guard path, and
already MOVED into `backlog/` on purpose. There is no code path here that
composes a prompt, picks a seed, clones a spec or scans `pipeline/jobs/`. A
render with no consumer is worse than an idle card (standing rule, "no work
without a consumer"), and 700+ specs on disk have mostly already run, so
"enqueue anything not in done/" would refile obsolete work forever. When the
backlog is empty this says so, loudly, in its log and its state file, and idles.
An empty backlog is a REPORTABLE STATE, not a licence to invent filler.

WHY MINUTES AND NOT JOBS. `box_job_minutes.py` measured the box's own sidecars:
an LTX motion take is ~5.7 min and a still is ~0.9 min. Four jobs is either
twenty-three minutes of work or four. A job-count floor would have declared a
queue of four publish steps healthy and let the card fall over in three minutes.
The medians below are that file's output; re-derive them with
`python3 pipeline/box_job_minutes.py --yaml`, do not guess new ones.

DEPTH IS UNCLAIMED WORK ONLY. `running/` is not counted. The runner is
sequential and its one live job is somewhere between its first and last second;
adding a whole median for it would say the queue is deeper than it is, and
overstating depth is precisely how the card reaches zero. Under-filling by one
job costs a few minutes of queue that the next tick fixes anyway.

`C:\banyan-queue\held\` IS NOT A BACKLOG AND IS NEVER READ HERE. It holds 23
jobs from 2026-08-13 and -14 that lanes parked for cause -- adult plates, a
twohander that was re-cut, six goblin design rounds filed twice. Firing those
tonight is the exact failure mode of "enqueue anything that has not run": work
that was true two days ago, aimed at plates that have since been replaced. A
backlog is what someone filed FORWARD, on purpose, with a clock on it; a
graveyard is what someone put down. If any of those jobs is still wanted, a lane
re-files it through `box_enqueue.py --backlog` and it gets checked again on the
way in.

.HOLD IS NOT RUNNABLE. Lanes park a job by renaming it to `.HOLD`,
`.HOLD-wrong-init`, `.HOLD-wrong-action` -- there were six such files in `ready/`
the night this was written, and `dir /b ready` counts every one of them. Depth
here counts names ending `.json` and nothing else, in `ready/` and in
`backlog/`. Nothing in this file ever renames a `.HOLD` back.

IT NEVER RACES THE DRAINER. The runner claims by `os.rename` out of `ready/`;
this fills by `os.rename` into `ready/` from a sibling directory on the same
volume. The two moves cannot meet: a file is in exactly one directory at every
instant, and a job that appears while the runner is mid-poll is simply seen on
the next poll ten seconds later. Nothing here touches `running/`, `runner.lock`,
or a claimed job, and nothing here signals or restarts the runner.

GUARDS ARE NOT WAIVED TO STAY WARM. Everything `box_enqueue.py` refuses at
enqueue time -- `gate:`/`gate_ref:`, an unfilled `recipe_slot:`, a missing
`consumer:`, an unapproved node, a card plate, a card reference set, a payload
path collision -- is refused at BACKLOG-FILING time, by that same code, because
filing to the backlog goes through `box_enqueue.py --backlog` and no other door.
This file therefore never needs to know what a plate is. And `--backlog`
additionally refuses any spec carrying a `plate_ack:` waiver: a job that only
passes because someone wrote "I looked and it is fine" is a job a person
enqueues while awake, on purpose. A 2026-08-14 job that took that shortcut was
cropping the WRONG BEAT'S plate. An autofill that waives a guard to keep the
card busy is worse than an idle card.

TWO REFUSALS OF ITS OWN, both about staleness, both loud:

  EXPIRED     a backlog entry names an init, a recipe and a bar that were true
              when it was filed. Firing it eleven hours later can animate a
              plate a lane has since replaced. Entries carry `filed_at` and
              `expires_h` (default 36h, set at filing); past that the file is
              renamed `.EXPIRED` and never fires. A hand-placed file with no
              stamp falls back to its own mtime.
  SUPERSEDED  a job id already sitting in `ready/`, `running/`, `done/` or
              `failed/` is not filed again. The backlog is consumed by MOVING,
              so this cannot happen by itself -- it catches a lane that copied
              a spec in twice, or re-filed one that already ran.

Neither is deleted. A refused entry keeps its bytes under `backlog/` with the
reason in its name, so tomorrow morning shows what did not fire and why.

EVERY NUMBER IS STAMPED `_before` OR `_after`, and none of them is a forecast.
On 2026-08-16 this file's own `--status` reported `drainer {"ready": 0,
"running": 0}` and `backlog_remaining 1` while the box's directories held 3
ready, 1 running and 6 backlog -- and in the same payload the top-level `why`
read "ready held 0.0 min of the 45 min floor -- filed 4, now 22.8 min", which
was exactly right. Nothing was mis-globbed, nothing was cached, no path was
remote-vs-local confused. The counts were read BEFORE the tick filed four jobs
and then published under an `at` stamped AFTER it, so the payload described two
different instants under one clock. `why` survived only because it happens to
name both instants in its own sentence.

A HALF-TRUE INSTRUMENT IS WORSE THAN A BROKEN ONE. The steward reads `--status`
to answer the founder "is the card fed", and a payload where some fields are
right teaches you to trust all of them. That is the file's own founding bug --
"a full queue and a dead card read identically from the depth check" -- rebuilt
one level up, in the reporting instead of the sensing. So: `measure()` is the
only thing that counts anything; every field it produces is published as
`ready_jobs_before`/`ready_jobs_after` and never bare; `minutes_after` is read
off the directories rather than added up from medians (it is a queue, not a
sum, and a move that silently failed made the old arithmetic a story about a
directory nobody had looked at); and `--status` prints the snapshot's AGE every
time plus its own live listing of the box, because a tick's photograph is up to
three minutes old and the question is always about now.

DEPLOYMENT, stated because a fix that never deploys is not a fix. The runner
draining jobs tonight is `C:\banyan-farm\box_runner.py`, a hand copy taken from
a commit on 2026-08-10; the repo's `pipeline/box_runner.py` has moved on and the
daemon has never seen it. That is exactly why this is NOT a change to the runner
loop: shipping it there would mean copying a file over a live daemon and
restarting it, and a restart mid-job adopts that job as INTERRUPTED (rc 93) --
paying ninety minutes of card time for a scheduling fix. A separate scheduled
task can be installed while a render runs, touches nothing the runner owns, and
cannot wedge the drainer if it has a bug. It also ships with `--deploy` (one
idempotent command from the Mac) and `--verify-deployed`, which hashes this file
against the box's copy and reports the runner's own drift while it is there --
so "the box is running an older copy" becomes a thing you can SEE rather than a
thing you find out about at 3am.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time

DEFAULT_ROOT = r"C:\banyan-queue"
BACKLOG = "backlog"
READY = "ready"
RUNNING = "running"
DONE = "done"
FAILED = "failed"

# Minutes of unclaimed work the queue is kept above. 45 is a deliberate choice
# rather than a round number: the box's ticks are three minutes apart and the
# thing that has actually gone wrong is a HUMAN gap -- a session dying on a
# usage limit, an orchestrator mid-thought -- which is tens of minutes, not
# tens of seconds. 45 min of ready work is ~8 motion takes; it survives a lane
# going quiet without emptying a backlog into the queue where nobody can
# reorder it any more.
FLOOR_MINUTES = 45.0

# Belt and braces on the arithmetic. If the medians were ever badly wrong, a
# minutes-only rule could empty the whole backlog in one tick; these cap the
# damage at something a person can undo by hand.
MAX_FILES_PER_TICK = 4
MAX_READY_JOBS = 12

# How long a filed backlog entry stays true. See the EXPIRED note above.
DEFAULT_EXPIRES_H = 36.0

# Measured, not guessed: pipeline/box_job_minutes.py over the 350 jobs the box
# finished 10-13 Aug, the same numbers pipeline/measured/box-queue.yaml feeds
# the status page. Re-derive with `box_job_minutes.py --yaml`; do not invent.
KIND_MINUTES = {
    "ltx": 5.7,
    "charref": 2.9,
    "inpaint": 2.0,
    "still": 0.9,
    "other": 0.9,
}
KIND_FALLBACK = 4.3

# argv fingerprint -> kind. Copied deliberately from box_job_minutes.KINDS
# rather than imported: this file runs on the box's system python from a
# directory with no repo in it, exactly like telemetry.py, and an import of a
# repo module would make the autofill depend on a checkout whose branch a hand
# lane switches. Order matters, LTX first -- a motion job also crops and
# publishes. If box_job_minutes.KINDS gains a row, add it here too.
KINDS = (
    ("ltx_i2v", "ltx"),
    ("goblin_ipa_beat", "charref"),
    ("render_wave_sample", "still"),
    ("inpaint_fruit", "inpaint"),
    ("runpod_render", "still"),
)

LOG_NAME = "autofill.log"
STATE_NAME = "autofill.json"
LOG_MAX_BYTES = 512 * 1024
LOG_KEEP_BYTES = 200 * 1024

# What --deploy ships and --verify-deployed hashes. Drift in this file is fatal
# (it is the thing being deployed); drift in the others is reported, because
# box_runner.py has been drifted since 2026-08-10 on purpose and a permanently
# red check teaches people to ignore the check.
HOST = "rtx5090"
BOX_BIN = r"C:\banyan-farm"
DEPLOY_FILES = (("box_autofill.py", True),
                ("box_runner.py", False),
                ("box_preflight.py", False),
                ("telemetry.py", False))


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# measuring the queue
# --------------------------------------------------------------------------

def json_names(d: str) -> list:
    """Every runnable job file in a queue directory, sorted by name.

    `.json` and nothing else. A parked `job.json.HOLD-wrong-init` is not
    runnable and must never be counted as depth nor un-held; `dir /b ready`
    counts it and that is why depth is measured here and not with a listing.
    """
    try:
        names = os.listdir(d)
    except OSError:
        return []
    return sorted(n for n in names if n.lower().endswith(".json"))


def load_job(path: str):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            job = json.load(fh)
    except (OSError, ValueError):
        return None
    return job if isinstance(job, dict) else None


def job_kind(job: dict) -> str:
    """One word for what a job IS, off the scripts its steps actually run.

    Read from argv and never from the id, for box_job_minutes' reason: ids are
    written by whoever filed the job and drift into nicknames (-lw, -gp,
    -figloop), while the argv is what runs.
    """
    blob = " ".join(" ".join(s.get("argv") or []) for s in (job or {}).get("steps") or [])
    for needle, kind in KINDS:
        if needle in blob:
            return kind
    return "other"


def job_minutes(job: dict) -> float:
    return KIND_MINUTES.get(job_kind(job), KIND_FALLBACK)


def queue_minutes(root: str, sub: str = READY):
    """(minutes, count, {kind: n}) of UNCLAIMED work. running/ is not counted."""
    d = os.path.join(root, sub)
    minutes, kinds = 0.0, {}
    names = json_names(d)
    for name in names:
        job = load_job(os.path.join(d, name))
        if job is None:
            # An unreadable file in ready/ is the runner's problem, not ours --
            # it retires it rc 94. Count it as the pooled median so it is not
            # silently worth zero.
            minutes += KIND_FALLBACK
            kinds["unreadable"] = kinds.get("unreadable", 0) + 1
            continue
        kind = job_kind(job)
        kinds[kind] = kinds.get(kind, 0) + 1
        minutes += job_minutes(job)
    return round(minutes, 1), len(names), kinds


def measure(root: str, now: float = None) -> dict:
    """Every count in one dict, off one pass of the directories, at one instant.

    EVERY NUMBER THIS FILE PUBLISHES COMES FROM HERE, and a reading is only ever
    published under a name that says WHICH instant it is (`_before` / `_after`).
    That convention is not decoration; it is the whole of the 2026-08-16 bug.
    `--status` printed drainer `{"ready": 0, "running": 0}` and
    `backlog_remaining 1` while the box's directories held 3 ready, 1 running
    and 6 backlog. Nothing was mis-globbed and nothing was cached: those counts
    were read BEFORE the tick filed four jobs and then written out under an `at`
    stamped AFTER it. The `why` string next to them was correct only because it
    happens to spell out both instants itself -- "ready held 0.0 min ... filed
    4, now 22.8 min" -- which is how a payload came to be half true, and half
    true is worse than broken, because the wrong half gets quoted to the
    founder. Every field is now suffixed, so there is no unlabelled count left
    in the payload for a reader to take as "now".

    The old code read `ready/` twice per tick -- once in `queue_minutes`, again
    inside `drainer_state` -- so the depth reading and the stall reading could
    already disagree with each other if the runner claimed a job in the
    microseconds between them. One pass, one instant, both readings.
    """
    now = time.time() if now is None else now
    minutes, count, kinds = queue_minutes(root, READY)
    return {"at": now,
            "ready_jobs": count,
            "ready_minutes": minutes,
            "ready_kinds": kinds,
            "running_jobs": len(json_names(os.path.join(root, RUNNING))),
            "backlog_jobs": len(json_names(os.path.join(root, BACKLOG)))}


def known_job_ids(root: str) -> set:
    """Every job id this queue has seen: ready, running, done, failed.

    Filenames are `<id>.json` throughout (box_enqueue stamps the epoch into the
    id itself), so the name minus the suffix IS the id.
    """
    ids = set()
    for sub in (READY, RUNNING, DONE, FAILED):
        for name in json_names(os.path.join(root, sub)):
            ids.add(name[:-5])
    return ids


# --------------------------------------------------------------------------
# the backlog
# --------------------------------------------------------------------------

def backlog_entries(root: str) -> list:
    """[(name, job)] eligible-by-shape, in the order the runner would run them.

    (priority, name) ascending -- the same key `box_runner.Queue.ready_jobs`
    sorts `ready/` by, on purpose: one ordering vocabulary for the whole queue,
    so a lane that knows `priority:` already knows how to say "this first" and
    there is no second grammar to learn or to get wrong. Unreadable files are
    left out here and dealt with by the tick, which can rename them.
    """
    d = os.path.join(root, BACKLOG)
    out = []
    for name in json_names(d):
        job = load_job(os.path.join(d, name))
        if job is None:
            continue
        out.append((name, job))
    return sorted(out, key=lambda p: (p[1].get("priority", 100), p[0]))


def filed_at(job: dict, path: str = None) -> float:
    """When this entry was filed. Its own stamp, else the file's mtime.

    The mtime fallback is what gives a hand-placed file an expiry at all. A
    backlog with no clock is a backlog that fires 2026-08-14's plate in
    September.
    """
    meta = job.get("backlog") or {}
    try:
        return float(meta.get("filed_at"))
    except (TypeError, ValueError):
        pass
    try:
        return os.path.getmtime(path) if path else 0.0
    except OSError:
        return 0.0


def expires_hours(job: dict) -> float:
    meta = job.get("backlog") or {}
    try:
        return float(meta.get("expires_h"))
    except (TypeError, ValueError):
        return DEFAULT_EXPIRES_H


def is_expired(job: dict, now: float, path: str = None) -> bool:
    """Too old to fire -- and an entry with NO clock at all is too old.

    Neither a `filed_at` stamp nor a readable mtime means this file's age
    cannot be established, and unverifiable freshness is not freshness. Same
    stance the enqueue guards take about a plate they cannot fetch: "could not
    check" is a refusal, not a pass. It parks as .EXPIRED and says so.
    """
    return (now - filed_at(job, path)) > expires_hours(job) * 3600.0


def plan_fill(entries, known_ids, ready_minutes: float, ready_count: int,
              now: float, floor: float = FLOOR_MINUTES,
              max_files: int = MAX_FILES_PER_TICK,
              max_ready: int = MAX_READY_JOBS, paths=None) -> dict:
    """Decide this tick, purely. No file is touched here -- the test drives it.

    Returns {"file": [names], "expired": [names], "superseded": [names],
             "minutes_after": float, "status": str, "why": str}.

    status is one of:
      full           the queue is already above the floor
      filled         work was moved into ready/
      backlog_empty  the queue is BELOW the floor and there is nothing eligible
                     to file. The loud one. It is a report, never a reason to
                     invent a job.
    """
    paths = paths or {}
    out = {"file": [], "expired": [], "superseded": [],
           "minutes_after": ready_minutes, "status": "full", "why": ""}
    if ready_minutes >= floor:
        out["why"] = ("ready holds %.1f min, at or over the %.0f min floor"
                      % (ready_minutes, floor))
        return out
    minutes, count = ready_minutes, ready_count
    for name, job in entries:
        if is_expired(job, now, paths.get(name)):
            out["expired"].append(name)
            continue
        if (job.get("id") or name[:-5]) in known_ids:
            out["superseded"].append(name)
            continue
        if len(out["file"]) >= max_files or count >= max_ready:
            break
        out["file"].append(name)
        minutes += job_minutes(job)
        count += 1
        if minutes >= floor:
            break
    out["minutes_after"] = round(minutes, 1)
    if out["file"]:
        out["status"] = "filled"
        out["why"] = ("ready held %.1f min of the %.0f min floor -- filed %d, "
                      "now %.1f min" % (ready_minutes, floor, len(out["file"]),
                                        out["minutes_after"]))
    else:
        out["status"] = "backlog_empty"
        out["why"] = ("HUNGRY: ready holds %.1f min, under the %.0f min floor, and "
                      "the backlog has nothing eligible to file (%d expired, %d "
                      "already run). NOTHING WAS INVENTED -- the card idles until a "
                      "lane files real work with box_enqueue.py --backlog."
                      % (ready_minutes, floor, len(out["expired"]),
                         len(out["superseded"])))
    return out


# --------------------------------------------------------------------------
# doing it
# --------------------------------------------------------------------------

# Longest real job observed on this box is 5m20s (runner_watchdog's measured
# note); 8 minutes of silence clears the slowest one with margin.
STALL_SECONDS = 8 * 60


def drainer_state(root: str, now: float = None, snap: dict = None) -> dict:
    """Is anything actually DRAINING what we file? Observed, never acted on.

    A FULL QUEUE AND A DEAD CARD LOOK IDENTICAL FROM HERE unless this is asked.
    On 2026-08-10 the runner claimed a job, finished it, and then stopped
    claiming for sixteen minutes with twelve jobs in ready/ while `schtasks`
    reported it Running -- and the box's `banyan-runner-watchdog` task, the one
    that restarts exactly that wedge, has been DISABLED since 2026-08-12. An
    autofill that reports "full, 62 minutes queued" through a wedge would be one
    more thing describing a dead card as healthy, which is the failure this file
    exists to end, one level down.

    The rule is runner_watchdog.diagnose's, minus the restart: work waiting,
    nothing claimed, and the runner's own log silent longer than the longest
    real job. It never restarts anything and never touches runner.lock --
    restarting is the watchdog's judgement to make with its escalation count,
    and two things restarting one daemon is worse than neither. This only tells
    the truth in autofill.json, where the depth reading already lives.

    ITS COUNTS ARE PRE-FILL AND ARE NAMED THAT WAY. They have to be pre-fill:
    the judgement below is "work is waiting and nobody has claimed it", and a
    job this tick filed one second ago has not been offered to the runner yet
    (it polls every ten seconds), so counting it would make every successful
    fill look like a wedge. But pre-fill counts published as `ready` and
    `running` are what a reader quotes as the state of the card right now, and
    on 2026-08-16 that is exactly what happened. They are `ready_jobs_before`
    and `running_jobs_before`; the post-fill truth is at the top of the payload.

    `snap` is `measure()`'s reading for this same instant, passed in so the
    stall verdict and the depth reading cannot come from two different listings.
    """
    now = time.time() if now is None else now
    if snap is None:
        snap = measure(root, now)
    ready = snap["ready_jobs"]
    running = snap["running_jobs"]
    try:
        age = now - os.path.getmtime(os.path.join(root, "runner.log"))
    except OSError:
        age = None
    out = {"at": utcnow(), "phase": "before_fill",
           "ready_jobs_before": ready, "running_jobs_before": running,
           "runner_log_age_s": None if age is None else int(age), "stalled": False,
           "why": ""}
    if ready < 1:
        out["why"] = "nothing waiting -- silence is correct"
    elif running > 0:
        out["why"] = "a job is claimed"
    elif age is None:
        out["why"] = "runner.log unreadable -- a broken probe is not evidence"
    elif age <= STALL_SECONDS:
        out["why"] = "runner wrote %ds ago" % int(age)
    else:
        out["stalled"] = True
        out["why"] = ("%d jobs waiting, none claimed, runner silent %dm -- NOBODY IS "
                      "DRAINING THE QUEUE. banyan-runner-watchdog restarts this; it "
                      "has been Disabled on the box since 2026-08-12."
                      % (ready, int(age / 60)))
    return out


def log_line(root: str, msg: str) -> None:
    line = "%s %s" % (utcnow(), msg)
    print(line)
    path = os.path.join(root, LOG_NAME)
    try:
        # Disk on this box has been under 10 GB free; a log that grows forever
        # is a small betrayal of that. Trim to the tail, never delete.
        if os.path.getsize(path) > LOG_MAX_BYTES:
            with open(path, "rb") as fh:
                fh.seek(-LOG_KEEP_BYTES, os.SEEK_END)
                tail = fh.read()
            with open(path, "wb") as fh:
                fh.write(b"... trimmed ...\n" + tail)
    except OSError:
        pass
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def write_state(root: str, state: dict) -> None:
    """The tick's answer, where a reader with no ssh transcript can find it.

    Written whole, every tick, so a stale file is impossible to mistake for a
    fresh one: `at` is the reading's own stamp and a reader that finds it hours
    old knows the tick itself has stopped.
    """
    tmp = os.path.join(root, STATE_NAME + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2, sort_keys=True)
        os.replace(tmp, os.path.join(root, STATE_NAME))
    except OSError:
        pass


def park(root: str, name: str, suffix: str) -> str:
    """Rename a backlog entry out of the runnable set, keeping its bytes.

    `.EXPIRED` / `.SUPERSEDED` / `.UNREADABLE` do not end in `.json`, so they
    stop being eligible the instant they are renamed -- the same trick the
    lanes' own `.HOLD` uses, and readable at a glance in a `dir`.
    """
    d = os.path.join(root, BACKLOG)
    src, dst = os.path.join(d, name), os.path.join(d, name + suffix)
    try:
        os.replace(src, dst)
    except OSError:
        return ""
    return dst


def tick(root: str, floor: float = FLOOR_MINUTES, dry_run: bool = False,
         max_files: int = MAX_FILES_PER_TICK, max_ready: int = MAX_READY_JOBS,
         now: float = None) -> dict:
    now = time.time() if now is None else now
    for sub in (READY, RUNNING, DONE, FAILED, BACKLOG):
        try:
            os.makedirs(os.path.join(root, sub), exist_ok=True)
        except OSError:
            pass

    # ONE pass of the directories, BEFORE anything is filed. This is what the
    # fill decision is made on and it must be pre-fill -- you cannot decide
    # whether to top up a queue from a reading taken after topping it up. The
    # drainer verdict shares this same reading for the same reason and so that
    # the two can never disagree with each other.
    before = measure(root, now)
    ready_minutes = before["ready_minutes"]
    ready_count = before["ready_jobs"]
    kinds = before["ready_kinds"]
    drainer = drainer_state(root, now, snap=before)
    entries = backlog_entries(root)
    paths = {n: os.path.join(root, BACKLOG, n) for n, _ in entries}
    known = known_job_ids(root)
    plan = plan_fill(entries, known, ready_minutes, ready_count, now, floor,
                     max_files, max_ready, paths=paths)

    filed = []
    if not dry_run:
        for name in plan["expired"]:
            if park(root, name, ".EXPIRED"):
                log_line(root, "!! EXPIRED %s -- filed more than %.0fh ago, not fired. "
                               "Its init and its bar may have moved; re-file it with "
                               "box_enqueue.py --backlog if it is still true."
                         % (name, expires_hours(dict(entries)[name])))
        for name in plan["superseded"]:
            if park(root, name, ".SUPERSEDED"):
                log_line(root, "!! SUPERSEDED %s -- that job id has already been "
                               "queued or run on this box; not refiled." % name)
        for name in plan["file"]:
            src = os.path.join(root, BACKLOG, name)
            dst = os.path.join(root, READY, name)
            if os.path.exists(dst):
                log_line(root, "!! %s already in ready/ -- left in the backlog" % name)
                continue
            try:
                # The whole fill, in one atomic move on one volume. The runner
                # claims by renaming the other way; a file is in exactly one
                # directory at every instant, so there is no window in which
                # the drainer can see a half-filed job.
                os.rename(src, dst)
            except OSError as exc:
                log_line(root, "!! could not file %s: %s" % (name, exc))
                continue
            filed.append(name)
    else:
        filed = list(plan["file"])

    status, why = plan["status"], plan["why"]
    if status == "filled" and not filed and not dry_run:
        # Every intended move failed -- a locked directory, a read-only volume,
        # a name already taken. Reporting "filled" with an empty list would be a
        # green tick over a queue that did not grow, which is this project's
        # signature failure. Say it did not happen.
        status = "blocked"
        why = ("wanted to file %d job(s) and moved NONE of them -- see the !! lines "
               "above. The queue is still %.1f min under a %.0f min floor."
               % (len(plan["file"]), ready_minutes, floor))
        log_line(root, "!! BLOCKED -- %s" % why)

    # MEASURED, not predicted. `minutes_after` used to be the plan's arithmetic
    # -- before-minutes plus the medians of what it meant to move -- which is a
    # proxy for the queue, not the queue. A move that silently failed, or a job
    # the runner claimed mid-tick, made that number a story about a directory
    # nobody had looked at. Read the directories again instead. A dry run moves
    # nothing, so its "after" is honestly the same listing as its "before".
    after = measure(root, time.time())
    after_at = utcnow()

    if status == "filled" and not dry_run:
        # Restate the fill against the listing rather than against the plan's
        # sum. Same two-instant sentence, both halves now read off disk.
        why = ("ready held %.1f min of the %.0f min floor -- filed %d, ready now "
               "holds %.1f min in %d job(s), measured"
               % (ready_minutes, floor, len(filed), after["ready_minutes"],
                  after["ready_jobs"]))

    state = {
        # `at` is the after-reading's own stamp: the payload's freshness clock
        # and its post-fill instant are deliberately the same moment.
        "at": after_at,
        "status": status,
        "why": why,
        "floor_minutes": floor,

        # --- AFTER the fill: what the box holds as of `at`. This is the row to
        # quote when somebody asks whether the card is fed.
        "ready_jobs_after": after["ready_jobs"],
        "ready_minutes_after": after["ready_minutes"],
        "ready_kinds_after": after["ready_kinds"],
        "running_jobs_after": after["running_jobs"],
        "backlog_jobs_after": after["backlog_jobs"],
        "backlog_remaining": after["backlog_jobs"],
        "measured_after_at": after_at,

        # --- BEFORE the fill: what the decision below was made on. Kept
        # because a fill you cannot explain is a fill you cannot audit.
        "ready_jobs_before": ready_count,
        "ready_minutes_before": ready_minutes,
        "ready_kinds_before": kinds,
        "running_jobs_before": before["running_jobs"],
        "backlog_jobs_before": before["backlog_jobs"],
        "measured_before_at": datetime.datetime.fromtimestamp(
            before["at"], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),

        # What the plan expected the fill to leave behind. Kept next to the
        # measured figure precisely so the two can be compared: a gap means a
        # move failed, or the runner claimed something while we were filing.
        "minutes_after_predicted": plan["minutes_after"],

        "filed": filed,
        "expired": plan["expired"],
        "superseded": plan["superseded"],
        "drainer": drainer,
        "dry_run": bool(dry_run),
        "script_sha256": file_sha256(os.path.abspath(__file__)),
    }
    if not dry_run:
        write_state(root, state)
    prefix = "(dry-run) " if dry_run else ""
    if drainer["stalled"]:
        log_line(root, "%s!! DRAINER STALLED -- %s" % (prefix, drainer["why"]))
    if status == "backlog_empty":
        log_line(root, "%s!! BACKLOG EMPTY -- %s" % (prefix, plan["why"]))
    elif status == "filled":
        log_line(root, "%sfilled %s | %s" % (prefix, ", ".join(filed) or "nothing",
                                             why))
    elif status == "full":
        log_line(root, "%sok %s | backlog %d waiting, running %d"
                 % (prefix, why, after["backlog_jobs"], after["running_jobs"]))
    return state


# --------------------------------------------------------------------------
# deployment -- run from the Mac
# --------------------------------------------------------------------------

def file_sha256(path: str) -> str:
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return ""


def ssh(cmd: str, timeout: int = 60):
    return subprocess.run(["ssh", "-n", "-o", "ConnectTimeout=20", "-o", "BatchMode=yes",
                           HOST, cmd], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def box_sha256(path: str) -> str:
    """certutil is on every Windows box and needs no powershell profile."""
    r = ssh('certutil -hashfile "%s" SHA256' % path)
    for line in (r.stdout or "").splitlines():
        s = line.strip().replace(" ", "")
        if len(s) == 64 and all(c in "0123456789abcdefABCDEF" for c in s):
            return s.lower()
    return ""


def verify_deployed() -> int:
    """Is the box running the file this repo contains? Say so per file."""
    here = os.path.dirname(os.path.abspath(__file__))
    bad = 0
    print("repo vs %s:%s" % (HOST, BOX_BIN))
    for name, fatal in DEPLOY_FILES:
        mine = file_sha256(os.path.join(here, name))
        theirs = box_sha256(BOX_BIN + "\\" + name)
        same = bool(mine) and mine == theirs
        mark = "same" if same else ("DRIFT" if theirs else "MISSING on box")
        print("  %-18s %-14s repo %s  box %s"
              % (name, mark, mine[:12] or "-", theirs[:12] or "-"))
        if not same and fatal:
            bad += 1
    if bad:
        print("!! the box is NOT running this repo's autofill. `--deploy` fixes it.")
        return 1
    print("ok  the scheduled autofill on the box is this file.")
    print("    (box_runner.py drift is expected and known: the running daemon is a "
          "hand copy from 2026-08-10. Re-copying it restarts the drainer, which "
          "adopts any live job as INTERRUPTED -- do that when the card is idle.)")
    return 0


def deploy() -> int:
    """Ship this file + its wrapper + its task to the box. Idempotent."""
    here = os.path.dirname(os.path.abspath(__file__))
    import tempfile
    stage = tempfile.mkdtemp(prefix="autofill-deploy-")

    # The .cmd is rewritten with CRLF here rather than trusted from the repo: a
    # batch file with LF endings does not fail loudly on Windows, it silently
    # does not launch, and git's line-ending handling is not something a
    # scheduled task should depend on.
    with open(os.path.join(here, "box-autofill.cmd"), encoding="utf-8") as fh:
        body = fh.read().replace("\r\n", "\n").replace("\n", "\r\n")
    cmd_local = os.path.join(stage, "box-autofill.cmd")
    with open(cmd_local, "w", encoding="ascii", newline="") as fh:
        fh.write(body)

    sends = [(os.path.join(here, "box_autofill.py"), BOX_BIN + "/box_autofill.py"),
             (cmd_local, BOX_BIN + "/box-autofill.cmd"),
             (os.path.join(here, "mktask-autofill.ps1"), BOX_BIN + "/mktask-autofill.ps1")]
    for local, dest in sends:
        r = subprocess.run(["scp", "-o", "ConnectTimeout=20", local,
                            "%s:%s" % (HOST, dest.replace("\\", "/"))],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120)
        if r.returncode:
            print("!! scp %s failed: %s" % (dest, r.stderr or r.stdout))
            return 1
        print("  sent %s" % dest)

    r = ssh('powershell -NoProfile -ExecutionPolicy Bypass -File '
            r'C:\banyan-farm\mktask-autofill.ps1', timeout=120)
    sys.stdout.write(r.stdout or "")
    if r.returncode:
        sys.stderr.write(r.stderr or "")
        print("!! registering the scheduled task failed")
        return 1
    return verify_deployed()


def live_counts():
    """Count the box's queue directories RIGHT NOW, by listing them. Read-only.

    `autofill.json` is written by a tick that happened up to three minutes ago.
    Even a perfectly self-consistent payload is therefore a photograph, and the
    question actually being asked of this tool -- "is the card fed?" -- is about
    this second. So --status takes its own listing. None means the probe failed,
    and a failed probe is reported as a failed probe, never as zero: "could not
    check" is a refusal, not a reading (same stance as `is_expired`).

    One `dir /b /s` over the three directories -- a single command, because a
    compound `cmd && cmd` over this ssh returns nothing silently -- filtered by
    THIS file's own `.json` rule, so "runnable" means the same thing here as it
    does in the tick and the six `.HOLD` files in ready/ are counted by neither.
    `dir /b` exits 1 on an empty directory; that is an empty directory.
    """
    subs = (READY, RUNNING, BACKLOG)
    r = ssh("dir /b /s " + " ".join('"%s\\%s"' % (DEFAULT_ROOT, s) for s in subs))
    if r.returncode not in (0, 1):
        return None
    out = {s: 0 for s in subs}
    for line in (r.stdout or "").splitlines():
        low = line.strip().lower()
        if not low.endswith(".json"):
            continue
        for sub in subs:
            if ("\\%s\\" % sub) in low:
                out[sub] += 1
                break
    return out


def reconcile(state: dict, live: dict):
    """Snapshot vs listing, as rows. Returns (lines, disagrees).

    Pure, so the comparison is testable with no ssh and no box. THE LISTING
    WINS: nothing here ever adjusts a count to match the payload. Disagreement
    is not itself a fault -- the runner drains continuously, and lanes file to
    the backlog while we read -- it is the difference between "as of the last
    tick" and "now", which is the thing that must never again be collapsed.
    """
    rows = (("ready", state.get("ready_jobs_after"), live.get(READY)),
            ("running", state.get("running_jobs_after"), live.get(RUNNING)),
            ("backlog", state.get("backlog_remaining"), live.get(BACKLOG)))
    lines, disagrees = [], False
    for name, snap, now in rows:
        flag = ""
        if snap is None:
            flag = "   <- this payload predates the fix; snapshot has no such field"
            disagrees = True
        elif snap != now:
            flag = "   <- moved since the tick"
            disagrees = True
        lines.append("  %-8s snapshot %-4s live %-4s%s"
                     % (name, "-" if snap is None else snap, now, flag))
    return lines, disagrees


def status() -> int:
    """The box's last tick AND the box's directories right now. Read-only."""
    r = ssh('type %s\\%s' % (DEFAULT_ROOT, STATE_NAME))
    text = (r.stdout or "").strip()
    if not text:
        print("!! no %s on the box -- the autofill has not ticked (or is not "
              "deployed). `--verify-deployed` says which." % STATE_NAME)
        return 1
    print(text)
    try:
        st = json.loads(text)
    except ValueError:
        return 1
    age = None
    try:
        at = datetime.datetime.strptime(st["at"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc)
        age = (datetime.datetime.now(datetime.timezone.utc) - at).total_seconds() / 60.0
    except (KeyError, ValueError):
        pass

    # Always, not only when it is alarming. A reader who is not told the age of
    # a reading assumes it is now, and on 2026-08-16 that assumption was quoted
    # to the founder twice.
    print("\nthat snapshot is %s old (the tick runs every 3 min); its counts are\n"
          "labelled _before / _after the fill it describes."
          % ("unknown age" if age is None else "%.1f min" % age))

    live = live_counts()
    if live is None:
        print("\n!! could not list the box's queue directories -- LIVE STATE UNKNOWN.\n"
              "   Do not quote the snapshot above as the state of the card now.")
    else:
        print("\nthe box's directories, listed just now (.json only -- .HOLD is not\n"
              "runnable and is counted by neither column):")
        lines, disagrees = reconcile(st, live)
        for line in lines:
            print(line)
        if disagrees:
            print("   the `live` column is the answer to \"is the card fed\"; the\n"
                  "   snapshot is what the last fill decision saw.")
        if live[READY] == 0 and live[RUNNING] == 0:
            print("\n!! THE CARD IS IDLE RIGHT NOW: nothing claimed and nothing "
                  "waiting.\n   %d job(s) in the backlog for the next tick to file."
                  % live[BACKLOG])
            return 2

    if age is not None and age > 15:
        print("\n!! that reading is %.0f minutes old -- the tick itself has stopped."
              % age)
        return 1
    if (st.get("drainer") or {}).get("stalled"):
        print("\n!! DRAINER STALLED: %s" % st["drainer"]["why"])
        return 3
    if st.get("status") == "backlog_empty":
        print("\n!! BACKLOG EMPTY: %s" % st.get("why"))
        return 2
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.environ.get("BANYAN_QUEUE_ROOT", DEFAULT_ROOT))
    ap.add_argument("--floor-minutes", type=float, default=FLOOR_MINUTES)
    ap.add_argument("--max-files", type=int, default=MAX_FILES_PER_TICK)
    ap.add_argument("--max-ready", type=int, default=MAX_READY_JOBS)
    ap.add_argument("--dry-run", action="store_true",
                    help="report the tick, move nothing")
    ap.add_argument("--deploy", action="store_true",
                    help="(from the Mac) ship this file and register the task")
    ap.add_argument("--verify-deployed", action="store_true",
                    help="(from the Mac) is the box running this file?")
    ap.add_argument("--status", action="store_true",
                    help="(from the Mac) print the box's last tick")
    args = ap.parse_args(argv)

    if args.deploy:
        return deploy()
    if args.verify_deployed:
        return verify_deployed()
    if args.status:
        return status()

    state = tick(args.root, floor=args.floor_minutes, dry_run=args.dry_run,
                 max_files=args.max_files, max_ready=args.max_ready)
    # Distinct codes, because the two states want opposite responses and
    # `Last Result` in schtasks is one number: 2 means the card wants work and
    # nobody has filed any (a lane must author some), 3 means there is work and
    # nothing is running it (the runner needs a restart, and this file will not
    # do that itself). 3 wins when both are true -- a queue nobody drains is not
    # improved by filing more into it.
    if state["drainer"]["stalled"]:
        return 3
    return 2 if state["status"] == "backlog_empty" else 0


if __name__ == "__main__":
    sys.exit(main())
