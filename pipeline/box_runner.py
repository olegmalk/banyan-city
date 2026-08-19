#!/usr/bin/env python3
"""Box-resident render runner.

Drains a queue that lives on the GPU box itself, so the card keeps working when
every Claude session is dead. Nothing here reads the repo at fire time: a job
file carries its own argv, env and artifact list, so a queued job survives a
repo move, a branch change, or an orchestrator that never wakes up again.

Layout (default root C:\\banyan-queue):

    ready/     job-*.json   queued, oldest priority-then-name first
    running/   job-*.json   claimed by an atomic rename; at most one
    done/      job-*.json   finished rc 0, alongside job-*.log
    failed/    job-*.json   finished rc != 0, or interrupted mid-render
    heartbeats.jsonl        append-only, one record per state change
    runner.log              the runner's own log
    runner.lock             pid of the live runner

Sequential by construction -- one job at a time, one step at a time. Batch-of-4
configs caused WDDM-thrash bugchecks on this card and are not expressible here.

Crash safety: a claim is an atomic os.rename into running/. On startup any job
still sitting in running/ is adopted as interrupted and retired to failed/
(or returned to ready/ only when the job itself opted in via max_attempts > 1
and it has attempts left). An interrupted job is therefore never lost and never
silently re-run twice.
"""

from __future__ import annotations

import argparse
import atexit
import ctypes
import datetime
import glob
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import traceback

DEFAULT_ROOT = r"C:\banyan-queue"
SUBDIRS = ("ready", "running", "done", "failed")
POLL_SECONDS = 10
HEARTBEAT_SECONDS = 60
MAX_CONSECUTIVE_ERRORS = 10

# --------------------------------------------------------------------------
# THE RC TABLE. Every code the runner invents lives here, and nowhere else.
#
# A job's rc is the runner's whole answer to "what do I do about this?", and the
# answers differ by ninety minutes of card time, so two failures must never
# spell themselves the same way. Codes below 90 are NOT ours -- they are the
# step's own exit status, passed through untouched (a sampler that exits 3 is
# recorded as 3). 90+ is reserved for the runner's own verdicts:
#
#   90  RC_STEP_NO_ARGV      a step in the job file declares no argv. The spec
#                            is malformed; nothing ran. Fix the job file.
#   91  RC_STEP_RAISED       launching the step raised inside the runner
#                            (missing binary, bad cwd). Nothing ran either.
#   92  RC_ARTIFACTS_MISSING SOME declared artifacts landed and some did not.
#                            A partial render. Re-render the gap.
#   93  RC_INTERRUPTED       the runner died mid-job and adopted it on restart
#                            (adopt_interrupted). Nobody knows how far it got;
#                            not re-run automatically.
#   94  RC_JOB_UNREADABLE    the job json would not parse. The runner never
#                            learned what the job even was.
#   95  RC_PUBLISHED_NOTHING every step exited 0 and NOT ONE declared artifact
#                            exists.
#
# Why 95 exists, since it looks like a shade of 92 (2026-08-14): six scene
# plates rendered perfectly and published 32 files apiece, but their specs had
# been cloned from a template predating the beat SLUG in the filenames, so the
# four names each spec declared were not on disk. All six retired FAILED on 92
# -- the same code a crashed render gets -- beats 05, 09 and 11 sat unused for a
# day, and the wave that followed animated costume identity cards because the
# real plates read as lost. "Published nothing" is fixed by re-publishing in
# seconds; "render crashed" by re-rendering in ninety minutes. The queue used to
# spell them identically and the wrong one was chosen.
#
# It is 95 and not 94, and not 93 (2026-08-15): 93 was reached for first and
# collided head-on with RC_INTERRUPTED, which merely MOVED the ambiguity from
# {crashed, published nothing} to {interrupted, published nothing} and broke CI;
# 94 was already RC_JOB_UNREADABLE. If you add a code, add it here, give it the
# next free number, and say what it means -- a number with no note beside it is
# exactly how the collision happened.
#
# test_box_runner.py pins all of these as mutually distinct. That test failing
# means two verdicts have collapsed into one, which is a real bug, not a stale
# expectation to be edited to match.
# --------------------------------------------------------------------------
RC_STEP_NO_ARGV = 90
RC_STEP_RAISED = 91
RC_ARTIFACTS_MISSING = 92
RC_INTERRUPTED = 93
RC_JOB_UNREADABLE = 94
RC_PUBLISHED_NOTHING = 95

# Hand lanes still launch renders on this card directly, so the runner has to
# yield to them. Matching on the script name is what actually works: an LTX job
# spends its first minutes in the encode stage with the text encoder in system
# RAM, during which nvidia-smi reports 0 MiB and no compute apps at all. VRAM
# alone would have called that card idle and started a second render on top of
# it -- which is how this box earns a WDDM bugcheck.
RENDER_SCRIPT_MARKERS = ("ltx_i2v.py", "wan_i2v", "vid5b", "video_task.py", "stage_r9")
GPU_BUSY_VRAM_MIB = 2048

# The hand lanes' own mutex, and the only one that covers the window a render
# has not started yet: card-runner-* writes this file before it launches and is
# told "if it does not say RELEASED, another lane holds the card and you must
# not start" (lane-registry.yaml:69). Reading it is not optional politeness --
# process and VRAM probes both report a card as free during LTX's several-minute
# encode stage, so this file is the ONLY signal that catches a lane which has
# claimed the card and is still setting up.
GPU_CLAIM_FILE = r"C:\banyan-farm\GPU-CLAIM.txt"
CLAIM_HOLDER = "box-runner"

# Where the work becomes visible off this box. farm_worker.py has published to
# farm-results-<machine> since 2026-07-29 and every reader we have -- build_sim
# (the machine street), pulse_series, queue_promoter, ops_board -- globs
# farm-results-* and splits the machine name off the branch. Reusing the branch
# is what makes a runner-drained job show up as the big render house working,
# instead of as a machine nobody has heard of.
COURIER_BRANCH = "farm-results-rtx5090"
COURIER_IDLE_MINUTES = 10

# --------------------------------------------------------------------------
# WHAT A HEARTBEAT IS ALLOWED TO COST A RENDER (2026-08-18, measured)
#
# The box's runner.log for one day: 40 pushes hit the old 300 s timeout,
# claim-to-first-step latency measured ~8 min TWICE, orphaned git.exe and
# git-pack-objects processes left behind, and the runner died at ~17:51 and
# ~18:16 (its scheduled task restarted it both times). Cause: every heartbeat
# event ran a SYNCHRONOUS `git push -f` on this branch, whose history lives in a
# 5.5 GiB repo, so every push repacks heavily. Two of those events sit directly
# in front of work -- `runner_up` before the first ready_jobs() poll, `job_start`
# before the first step of a job already claimed -- and 300 + 300 is the eight
# minutes, to the second.
#
# 1. DEFERRED_EVENTS: the two that sit in front of work stop pushing. They still
#    append to farm-out/heartbeat.txt with their true timestamp; the next publish
#    commits them, because _publish does `git add -A -- farm-out` and picks up
#    everything pending. No line is lost -- only its promptness, and the cost of
#    that is named below. Stated as a DENY list, not an allow list, so a new
#    event added later keeps the old behaviour instead of silently going dark;
#    `runner_idle` and `runner_waiting_for_gpu` in particular MUST stay pushing
#    (they are the box's liveness signal, already thinned to one per
#    COURIER_IDLE_MINUTES by Queue.quiet_push_due before they ever reach emit).
# 2. PUSH_TIMEOUT_SECONDS 60, was 300. A heartbeat that cannot be delivered in a
#    minute is logged and dropped; the next push carries it. A missed heartbeat
#    push must never block a render, and it must never kill the runner.
# 3. the timed-out push's whole process TREE is killed. subprocess.run(timeout=)
#    kills the DIRECT CHILD only -- but `git push` spawns git-pack-objects and
#    ssh, which survive it holding the stdout pipe they inherited, so the
#    communicate() that follows the kill can block with no timeout at all. That
#    is both the orphan pile in Task Manager and the most likely mechanism of the
#    two runner deaths: not a crash, a wedge.
#
# THE TRADEOFF, stated so the next person does not rediscover it as a bug:
# build_sim calls a job live on a fresh STARTED with no DONE after it
# (JOB_FRESH_MINUTES = 45). Deferring the STARTED push means the street does not
# show this box mid-render until the job ends. It was already near-blind there --
# the runner emits no beats at all between job_start and job_done, so any render
# over 45 min already aged out of "live" -- and eight minutes of card time per
# job, plus two daemon deaths, is the worse of the two.
DEFERRED_EVENTS = ("job_start", "runner_up")
PUSH_TIMEOUT_SECONDS = 60
# Not in the RC table above: that table is job verdicts, and this number never
# reaches a job -- it is internal to the courier. 124 is `timeout(1)`'s code.
PUSH_RC_TIMEOUT = 124

# The clone the courier borrows objects and the deploy key from, and a worktree
# that is deliberately NOT inside it -- see Courier's docstring for why touching
# the render checkout's branch is not survivable.
DEFAULT_REPO = r"C:\banyan-farm\banyan-city"
DEFAULT_COURIER_WORKTREE = r"C:\banyan-farm\courier-box"


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# single-instance lock
# --------------------------------------------------------------------------

def pid_alive(pid: int) -> bool:
    """True if pid is a live process. Windows-first, falls back to POSIX."""
    if pid <= 0:
        return False
    if os.name == "nt":
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        k32 = ctypes.windll.kernel32
        handle = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            if k32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return code.value == STILL_ACTIVE
            return False
        finally:
            k32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def boot_id() -> int:
    """Epoch second this OS booted, to ~10s. 0 where we cannot tell.

    The lock records it because a pid on its own is not an identity across a
    reboot: Windows hands the same pid out again, and the runner starts 30s
    after boot on a machine that has just had ~4000 pids freed at once. Without
    this, one unlucky collision leaves a runner that refuses to start and a card
    that sits idle exactly as if nobody had built any of this.
    """
    if os.name == "nt":
        try:
            ticks = ctypes.windll.kernel32.GetTickCount64()
        except Exception:
            return 0
        return int((time.time() - ticks / 1000.0) // 10 * 10)
    try:
        with open("/proc/stat") as fh:
            for line in fh:
                if line.startswith("btime "):
                    return int(line.split()[1]) // 10 * 10
    except OSError:
        pass
    return 0


def read_lock(path: str) -> tuple:
    """`(pid, boot)` from a lock file. `(0, 0)` if it says nothing usable."""
    try:
        with open(path) as fh:
            fields = fh.read().split()
    except OSError:
        return 0, 0
    try:
        holder = int(fields[0])
    except (IndexError, ValueError):
        return 0, 0
    boot = 0
    for field in fields[1:]:
        if field.startswith("boot="):
            try:
                boot = int(field[5:])
            except ValueError:
                boot = 0
    return holder, boot


def lock_is_live(holder: int, boot: int) -> bool:
    """Does this lock still belong to a running runner?

    A lock written before the current boot is stale no matter what its pid says,
    and that check comes FIRST -- asking the OS whether the pid is alive is the
    question that gets the wrong answer after a reboot.
    """
    if not holder or holder == os.getpid():
        return False
    mine = boot_id()
    if boot and mine and abs(boot - mine) > 120:
        return False
    return pid_alive(holder)


def acquire_lock(path: str) -> bool:
    """Take the runner lock, reclaiming it from a dead predecessor."""
    for _ in range(2):
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            holder, boot = read_lock(path)
            if lock_is_live(holder, boot):
                return False
            try:
                os.remove(path)
            except OSError:
                return False
            continue
        with os.fdopen(fd, "w") as fh:
            fh.write("%d %s boot=%d\n" % (os.getpid(), utcnow(), boot_id()))
        return True
    return False


def release_lock(path: str) -> None:
    holder, _ = read_lock(path)
    if holder == os.getpid():
        try:
            os.remove(path)
        except OSError:
            pass


# --------------------------------------------------------------------------
# GPU contention
# --------------------------------------------------------------------------

def _foreign_render_processes():
    """Command lines of render processes this runner did not start.

    `[]` means "asked, and there are none". `None` means THE QUESTION WAS NOT
    ANSWERED -- powershell missing, blocked, or past its timeout -- and those are
    opposite facts that used to return the same empty list. gpu_busy() promises
    conservatism and this was one of three probes that quietly reported "free"
    whenever it broke; a wrong "free" here starts a second render on top of a
    live one, which is how this card earns a WDDM bugcheck.

    Not-Windows still returns `[]`, and that is a real answer rather than a
    failure: there is no process scan on this platform and never was, so the
    other two probes carry the decision.
    """
    if os.name != "nt":
        return []
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
          "Select-Object -ExpandProperty CommandLine")
    try:
        out = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=45,
        ).stdout or ""
    except Exception:
        return None
    hits = []
    for line in out.splitlines():
        low = line.lower()
        if "box_runner.py" in low:
            continue
        if any(m in low for m in RENDER_SCRIPT_MARKERS):
            hits.append(line.strip()[:160])
    return hits


VRAM_PROBE_FAILED = -1        # nvidia-smi is installed and did not answer
VRAM_PROBE_UNAVAILABLE = -2   # there is no nvidia-smi on this machine at all


def _gpu_vram_mib() -> int:
    """MiB resident on the busiest GPU, or one of the two sentinels above.

    The old version returned 0 -- the empty-card number -- for every failure,
    so a timed-out or crashing nvidia-smi told gpu_busy() to go ahead and start
    a render. But the fix has to separate two failures that are not alike, and
    the first version of it did not:

      * NO NVIDIA-SMI HERE (FileNotFoundError) is a permanent, honest answer,
        the exact counterpart of "this is not Windows so there is no process
        scan". Every Mac, every CI runner and the test suite are in this case,
        and treating it as doubt wedges the runner shut forever -- the box test
        suite caught precisely that and sat waiting for a GPU on a laptop.
      * IT IS HERE AND IT DID NOT ANSWER (timeout, nonzero exit, unparseable
        output) is doubt, and it is doubt in the dangerous direction: a card
        under a heavy render is exactly when nvidia-smi is slow to reply.

    So the first is "no information, let the other probes decide" and the second
    is "assume the card is held".
    """
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )
    except (FileNotFoundError, NotADirectoryError):
        return VRAM_PROBE_UNAVAILABLE
    except Exception:
        return VRAM_PROBE_FAILED
    if r.returncode != 0:
        return VRAM_PROBE_FAILED
    try:
        return max(int(v.strip()) for v in (r.stdout or "").splitlines() if v.strip())
    except ValueError:
        # includes max() of an empty sequence: nvidia-smi answered with nothing
        return VRAM_PROBE_FAILED


CLAIM_UNREADABLE = "UNREADABLE claim file"


def _claim_path(path: str = None):
    """The claim file to use, or None where the convention does not exist.

    GPU_CLAIM_FILE is a Windows ABSOLUTE path, which on any other OS is an
    ordinary RELATIVE filename — so every claim call on a Mac read and wrote a
    file literally named `C:\\banyan-farm\\GPU-CLAIM.txt` in whatever the cwd
    happened to be. Running the box test suite from a checkout therefore left one
    sitting untracked in the repo root, one `git add -A` away from being
    committed, and it is a live claim file as far as read_claim is concerned: a
    stale HELD line in it would have told a POSIX run that the card was taken.

    An explicit path is always honoured, which is what the tests pass.
    """
    if path:
        return path
    return GPU_CLAIM_FILE if os.name == "nt" else None


def read_claim(path: str = None) -> str:
    """Contents of the hand lanes' GPU claim file, or "" if there is none.

    A MISSING file is "" -- nobody has claimed the card, which is the ordinary
    resting state. Any OTHER OSError (permission, a locked file, a dead network
    path) returns CLAIM_UNREADABLE instead, because "I could not read the file
    that says whether a lane holds the card" is not the same fact as "no lane
    holds the card" and used to be spelled the same way. claim_is_foreign() sees
    a non-empty string that says neither RELEASED nor box-runner and calls it a
    live foreign claim, which is the answer we want when we cannot tell.
    """
    path = _claim_path(path)
    if path is None:
        return ""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read().strip()
    except FileNotFoundError:
        return ""
    except OSError as exc:
        return "%s: %s" % (CLAIM_UNREADABLE, exc)


def claim_is_foreign(text: str) -> bool:
    """Does this claim text belong to somebody who is not us, right now?

    Empty file, missing file and RELEASED all mean the card is free. Anything
    else is a live claim -- and one naming CLAIM_HOLDER is our own, left behind
    by a runner that died mid-job, so it must not lock its own successor out.
    """
    if not text:
        return False
    if "RELEASED" in text.upper():
        return False
    return CLAIM_HOLDER not in text


def take_claim(job_id: str, path: str = None) -> None:
    """Announce to the hand lanes that the card is ours. Never raises."""
    path = _claim_path(path)
    if path is None:
        return
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("HELD by %s job=%s pid=%d host=%s at %s\n"
                     % (CLAIM_HOLDER, job_id, os.getpid(), socket.gethostname(), utcnow()))
    except OSError:
        pass


def drop_claim(job_id: str = "", path: str = None) -> None:
    """Release the card, but only if the claim on disk is still ours.

    The guard matters: a hand lane that took the card while we were finishing
    must not have its claim deleted by our cleanup.
    """
    path = _claim_path(path)
    if path is None:
        return
    text = read_claim(path)
    if text and CLAIM_HOLDER not in text:
        return
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("RELEASED by %s job=%s at %s\n" % (CLAIM_HOLDER, job_id, utcnow()))
    except OSError:
        pass


def gpu_busy():
    """(busy, reason). Conservative: any doubt counts as busy.

    The docstring said this before the code did. All three probes below used to
    report the free-looking value when they THEMSELVES failed -- no claim file,
    no processes, 0 MiB -- so a box with a broken nvidia-smi or a powershell that
    timed out would have started a render on top of whatever was already running.
    "What would this print if the thing were completely broken?" answered
    "not busy, go ahead", which means it was not a check.

    A failed probe is now busy WITH ITS OWN REASON, which is the loud-but-not-
    fatal shape: the runner keeps polling, `runner_waiting_for_gpu` carries the
    broken probe's name to the branch every COURIER_IDLE_MINUTES, and the moment
    the probe answers again the queue drains. Nothing here can end unattended
    rendering; it can only postpone it visibly.

    A probe that is not INSTALLED is a different matter and is not doubt at all
    -- see _gpu_vram_mib, and the `os.name != "nt"` arm of the process scan. Those
    machines simply have fewer probes, and the ones they do have decide.
    """
    claim = read_claim()
    if claim_is_foreign(claim):
        return True, "GPU-CLAIM.txt held: %s" % claim.splitlines()[0][:120]
    foreign = _foreign_render_processes()
    if foreign is None:
        return True, ("process probe FAILED (powershell did not answer) -- cannot "
                      "tell whether a hand lane is rendering, so treating the card "
                      "as held")
    if foreign:
        return True, "foreign render process: %s" % foreign[0]
    vram = _gpu_vram_mib()
    if vram == VRAM_PROBE_FAILED:
        return True, ("VRAM probe FAILED (nvidia-smi is installed and did not "
                      "answer) -- cannot tell whether the card is loaded, so "
                      "treating it as held")
    if vram >= GPU_BUSY_VRAM_MIB:
        return True, "%d MiB VRAM in use by another process" % vram
    return False, ""


# --------------------------------------------------------------------------
# queue
# --------------------------------------------------------------------------

class Queue:
    def __init__(self, root: str, courier=None):
        self.root = root
        for sub in SUBDIRS:
            os.makedirs(os.path.join(root, sub), exist_ok=True)
        self.heartbeats = os.path.join(root, "heartbeats.jsonl")
        self.lock_path = os.path.join(root, "runner.lock")
        self.courier = courier
        self._last_quiet_push = 0.0

    def dir(self, name: str) -> str:
        return os.path.join(self.root, name)

    def ready_jobs(self) -> list:
        out = []
        for name in os.listdir(self.dir("ready")):
            if name.endswith(".json"):
                out.append(name)
        # priority ascending (lower runs first), then name for a stable order
        def key(name):
            try:
                with open(os.path.join(self.dir("ready"), name), encoding="utf-8") as fh:
                    prio = json.load(fh).get("priority", 100)
            except Exception:
                prio = 100
            return (prio, name)
        return sorted(out, key=key)

    def failed_count(self) -> int:
        """How many jobs are sitting in failed/ right now.

        A job failure already ships once, as a `FAIL task=<id>` heartbeat at the
        moment it happens. That is an EVENT, and an event is only seen by a
        reader who was looking when it went past. Every recurring signal this
        runner emits described the queue as ready/running/done, so a watcher that
        samples current state -- a tick, a status page, a human running one
        `dir` -- saw a perfectly healthy queue with a corpse in it. On
        2026-08-10 `ep2-b04-goblin-ipa-content-1786354532` sat failed for 3.5
        hours that way. A standing count turns that into something a sample can
        see.
        """
        try:
            return sum(1 for n in os.listdir(self.dir("failed"))
                       if n.endswith(".json"))
        except OSError:
            # -1, NOT 0. Never let bookkeeping stop a render -- but this guard
            # exists precisely so a sample of current state can see a corpse, and
            # reporting the healthy number when the count itself failed rebuilds
            # the hole one level down. `failed=-1` on a heartbeat is obviously not
            # a count; `failed=0` is indistinguishable from a clean queue.
            return -1

    def claim(self, name: str):
        """Atomically move ready/name -> running/name. None if someone beat us."""
        src = os.path.join(self.dir("ready"), name)
        dst = os.path.join(self.dir("running"), name)
        try:
            os.rename(src, dst)
        except OSError:
            return None
        return dst

    def retire(self, path: str, outcome: str) -> str:
        dst = os.path.join(self.dir(outcome), os.path.basename(path))
        if os.path.exists(dst):
            os.remove(dst)
        os.rename(path, dst)
        return dst

    def quiet_push_due(self, event: str, now: float = None) -> bool:
        """Should a nothing-happened event go all the way to the branch?

        Job transitions always ship. `runner_idle` and `runner_waiting_for_gpu`
        fire every minute and each shipped one is a commit and a force-push, so
        they are thinned to one every COURIER_IDLE_MINUTES -- still far inside
        the 45 minutes build_sim allows before it calls a machine unheard-from,
        and 1/10th of the branch churn.
        """
        if event not in ("runner_idle", "runner_waiting_for_gpu"):
            return True
        now = time.time() if now is None else now
        if now - self._last_quiet_push < COURIER_IDLE_MINUTES * 60:
            return False
        self._last_quiet_push = now
        return True

    def beat(self, record: dict) -> None:
        record.setdefault("ts", utcnow())
        record.setdefault("host", socket.gethostname())
        record.setdefault("pid", os.getpid())
        line = json.dumps({k: v for k, v in record.items() if k != "files"},
                          ensure_ascii=False)
        with open(self.heartbeats, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        # The local jsonl is written FIRST and unconditionally: the box's own
        # record of what it did must not depend on GitHub being reachable.
        if self.courier and self.quiet_push_due(record.get("event", "")):
            self.courier.emit(record)


# --------------------------------------------------------------------------
# courier -- getting the work back into the repo
# --------------------------------------------------------------------------

def _kill_process_tree(pid: int, log=print) -> None:
    """Kill a process WE spawned, and everything it spawned, by pid.

    Deliberately NOT `taskkill /IM git.exe`. The render checkout at
    C:\\banyan-farm\\banyan-city has hand lanes running their own git, and
    taskkill's /FI filters are IMAGENAME, PID, STATUS, MEMUSAGE, USERNAME,
    CPUTIME, WINDOWTITLE, MODULES, SERVICES -- there is NO filter for working
    directory or command line, so no image-name filter exists that can be
    narrowed to this repo. A pid this process started, plus /T for its
    descendants, is the only filter that provably cannot reach another lane's
    git. Everything is swallowed: a failed cleanup is never a reason to stop
    rendering.
    """
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=20)
        else:
            # POSIX side exists for the tests. Safe only because the push is
            # spawned with start_new_session=True -- without it getpgid() would
            # return the RUNNER's own group and this would kill the daemon.
            os.killpg(os.getpgid(pid), signal.SIGKILL)
    except Exception as exc:
        log("courier: could not kill push tree %s: %s" % (pid, exc))


class Courier:
    """Publish this runner's heartbeats and job records on `farm-results-*`.

    Three constraints shaped every line of this and none of them are taste:

    1. IT MAY NEVER TAKE THE RUNNER DOWN. The whole point of the box runner is
       that the card keeps working when nothing else does; a courier that can
       raise is a way for a network blip to stop renders. Every entry point is
       wrapped, and a failure prints and sets `unpushed` -- loudly, because a
       courier that cannot deliver and does not say so is theatre
       (farm_worker.Courier.mark learned that the hard way on 2026-08-01).

    2. IT MAY NOT TOUCH THE RENDER CHECKOUT. `C:\\banyan-farm\\banyan-city` is
       the working tree hand lanes render out of, and one of them is usually
       mid-render. `git checkout -B farm-results-rtx5090` in there -- which is
       exactly what farm_worker.Courier does in its own tree -- would swap the
       branch out from under a live render. So the courier gets a dedicated
       `git worktree`, sharing the clone's objects and its deploy-key
       `core.sshcommand`, and touching nothing the render lane can see.

    3. THE LINES ARE farm_worker's GRAMMAR, NOT A NEW ONE.
       `heartbeat_attempts` parses `STARTED/DONE/FAIL/INTERRUPTED task=<id>`,
       and queue_promoter retires a queue entry on `DONE task=<id>`. Inventing a
       prettier vocabulary here would mean a job the runner finished stays open
       in every reader we have.
    """

    def __init__(self, worktree: str, branch: str, repo: str, log=print):
        self.worktree = worktree
        self.branch = branch
        self.repo = repo
        self.log = log
        self.out = os.path.join(worktree, "farm-out")
        self.unpushed = 0
        self.ready = False
        self.disabled_reason = ""
        # pids of pushes we started and have NOT confirmed dead. Non-empty means
        # a previous timeout's cleanup did not finish; the next push sweeps them
        # before adding load. Only ever holds pids this process spawned.
        self._push_pids = set()

    # -- plumbing ----------------------------------------------------------

    def _git(self, *args, cwd=None, timeout=180):
        return subprocess.run(
            ("git",) + args, cwd=cwd or self.worktree,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout,
        )

    def ensure(self) -> bool:
        """Create the worktree if it is not there yet. Idempotent."""
        if self.ready:
            return True
        if self.disabled_reason:
            return False
        try:
            if os.path.isdir(os.path.join(self.worktree, ".git")) or \
               os.path.isfile(os.path.join(self.worktree, ".git")):
                self.ready = True
                return True
            if not os.path.isdir(os.path.join(self.repo, ".git")):
                self.disabled_reason = "no git clone at %s" % self.repo
                self.log("courier off: " + self.disabled_reason)
                return False
            # Fetch first so we CONTINUE the branch rather than replacing it:
            # farm_worker's heartbeats from before this runner existed are the
            # only record of what this machine did in July, and a courier that
            # starts an empty heartbeat.txt and force-pushes deletes them.
            self._git("fetch", "-q", "origin",
                      "+refs/heads/%s:refs/remotes/origin/%s" % (self.branch, self.branch),
                      cwd=self.repo)
            base = self._git("rev-parse", "--verify", "-q",
                             "refs/remotes/origin/" + self.branch, cwd=self.repo)
            add = ["worktree", "add", "-f", self.worktree]
            add += (["-B", self.branch, "origin/" + self.branch] if base.returncode == 0
                    else ["-b", self.branch])
            r = self._git(*add, cwd=self.repo, timeout=600)
            if r.returncode:
                self.disabled_reason = (r.stderr or r.stdout or "").strip()[-300:]
                self.log("courier off: worktree add failed: " + self.disabled_reason)
                return False
            self.ready = True
            self.log("courier worktree ready at %s on %s" % (self.worktree, self.branch))
            return True
        except Exception as exc:
            self.disabled_reason = "%s: %s" % (type(exc).__name__, exc)
            self.log("courier off: " + self.disabled_reason)
            return False

    def _push(self, argv=None, timeout: int = None) -> tuple:
        """`git push -f`, hard-bounded, leaving no orphans. Returns (rc, output).

        Popen + communicate rather than subprocess.run(timeout=) for one reason,
        and it is the whole bug: run()'s timeout kills the direct child and then
        calls communicate() with NO timeout, and git push's children --
        git-pack-objects, ssh -- are still holding the stdout pipe they
        inherited, so that call can block forever. A 300 s push turned into a
        wedged runner exactly there.
        """
        argv = list(argv or ("git", "push", "-f", "origin", self.branch))
        timeout = PUSH_TIMEOUT_SECONDS if timeout is None else timeout

        # Requirement (c): sweep any push tree we started earlier and never saw
        # die. Bounded to pids in our own set -- never a search by image name.
        for stale in sorted(self._push_pids):
            self.log("courier: killing leftover push tree pid=%s before pushing" % stale)
            _kill_process_tree(stale, self.log)
        self._push_pids.clear()

        kw = {}
        if os.name == "nt":
            kw["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        else:
            kw["start_new_session"] = True   # so _kill_process_tree's killpg is safe
        p = subprocess.Popen(argv, cwd=self.worktree, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True,
                             encoding="utf-8", errors="replace", **kw)
        self._push_pids.add(p.pid)
        try:
            out, _ = p.communicate(timeout=timeout)
            self._push_pids.discard(p.pid)
            return p.returncode, out or ""
        except subprocess.TimeoutExpired:
            _kill_process_tree(p.pid, self.log)
            try:
                out, _ = p.communicate(timeout=15)
                self._push_pids.discard(p.pid)
            except subprocess.TimeoutExpired:
                # The tree kill did not free the pipe. Do NOT wait again -- that
                # is the wedge. Leave the pid in the set so the next push sweeps
                # it, and hand the runner back its thread.
                out = ""
            return PUSH_RC_TIMEOUT, (
                "push exceeded %ds and its process tree was killed\n%s"
                % (timeout, out or ""))

    def _publish(self, message: str) -> None:
        # -- <path>, never a bare commit. This worktree is the courier's alone
        # today, but farm_worker.Courier.mark carries the same scar for the same
        # reason and the cost of getting it wrong is committing someone else's
        # staged work under a heartbeat message.
        self._git("add", "-A", "--", "farm-out")
        c = self._git("commit", "-q", "-m", message, "--", "farm-out")
        if c.returncode and "nothing to commit" not in (c.stdout + c.stderr):
            self.log("!! courier commit failed: %s"
                     % (c.stderr or c.stdout or "").strip()[-300:])
            return
        rc, out = self._push()
        if rc:
            self.unpushed += 1
            self.log("!! COURIER PUSH FAILED (%d in a row) -- results are on this "
                     "box only, in %s\n   %s"
                     % (self.unpushed, self.out, (out or "").strip()[-300:]))
        elif self.unpushed:
            self.log("courier push recovered after %d failure(s)" % self.unpushed)
            self.unpushed = 0

    # -- the public surface ------------------------------------------------

    def mark(self, line: str, message: str, files: dict = None,
             push: bool = True) -> None:
        """Append one heartbeat line (+ optional small files); push if it earns it.

        `push=False` writes everything to the worktree and stops there. Nothing
        is lost: _publish stages with `git add -A -- farm-out`, so the deferred
        line rides out with the next real publish, carrying the timestamp it was
        written at rather than the one it was pushed at.
        """
        try:
            if not self.ensure():
                return
            os.makedirs(os.path.join(self.out, "box"), exist_ok=True)
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%SZ")
            with open(os.path.join(self.out, "heartbeat.txt"), "a",
                      encoding="utf-8", errors="replace") as fh:
                fh.write("%s %s\n" % (stamp, line))
            for name, body in (files or {}).items():
                dst = os.path.join(self.out, "box", name)
                with open(dst, "w", encoding="utf-8", errors="replace") as fh:
                    fh.write(body)
            if push:
                self._publish(message)
        except Exception:
            self.log("!! courier raised, renders continue:\n" + traceback.format_exc())

    def emit(self, record: dict) -> None:
        """Translate a queue heartbeat record into the shared grammar.

        Whether the line also PUSHES is decided in exactly one place -- the
        DEFERRED_EVENTS tuple at the top of this file, where the measurements
        that set it are written down.
        """
        event = record.get("event", "")
        jid = record.get("job", "?")
        push = event not in DEFERRED_EVENTS
        if event == "job_start":
            # Deferred on purpose: this call used to sit between claiming a job
            # and running its first step, and cost up to 300 s of card time.
            self.mark("STARTED task=%s attempt=%s on box-runner"
                      % (jid, record.get("attempt", 1)), "hb: STARTED %s" % jid,
                      push=push)
        elif event == "job_done":
            bare = record.get("unprovenanced") or []
            self.mark("DONE task=%s rc=0 artifacts=%d"
                      % (jid, len(record.get("artifacts") or []))
                      + (" NO-SIDECAR=%d (%s)"
                         % (len(bare), ", ".join(os.path.basename(b) for b in bare))
                         if bare else ""),
                      "hb: DONE %s" % jid, files=record.get("files"), push=push)
        elif event == "job_failed":
            self.mark("FAIL task=%s rc=%s step=%s"
                      % (jid, record.get("rc"), record.get("failed_step")),
                      "hb: FAIL %s" % jid, files=record.get("files"), push=push)
        elif event == "job_requeued_after_interrupt":
            self.mark("INTERRUPTED task=%s requeued attempt %s/%s"
                      % (jid, record.get("attempts"), record.get("max_attempts")),
                      "hb: INTERRUPTED %s" % jid, push=push)
        elif event == "runner_up":
            # Deferred: this was the first thing main() did, ahead of the first
            # ready_jobs() poll, so a slow push delayed the whole daemon's start.
            # The idle beat 60 s later publishes it.
            self.mark("box-runner up pid=%s host=%s"
                      % (record.get("pid"), record.get("host")), "hb: runner up",
                      push=push)
        elif event == "runner_down":
            self.mark("box-runner down after %s job(s)"
                      % record.get("jobs_completed"), "hb: runner down", push=push)
        elif event == "runner_idle":
            self.mark("box-runner idle ready=%s failed=%s"
                      % (record.get("ready", 0), record.get("failed", 0)),
                      "hb: idle", push=push)
        elif event == "runner_waiting_for_gpu":
            self.mark("box-runner waiting for GPU: %s failed=%s"
                      % (record.get("reason"), record.get("failed", 0)),
                      "hb: waiting for GPU", push=push)


def write_json(path: str, data: dict) -> None:
    """Write atomically so a crash mid-write cannot corrupt a job file."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


# --------------------------------------------------------------------------
# job execution
# --------------------------------------------------------------------------

def run_step(step: dict, log_fh, job_env: dict) -> int:
    argv = step.get("argv")
    if not argv:
        log_fh.write("!! step %r has no argv\n" % step.get("name"))
        return RC_STEP_NO_ARGV
    env = dict(os.environ)
    env.update({str(k): str(v) for k, v in (job_env or {}).items()})
    env.update({str(k): str(v) for k, v in (step.get("env") or {}).items()})
    cwd = step.get("cwd") or None

    log_fh.write("\n==== step %s START %s ====\n" % (step.get("name", "?"), utcnow()))
    log_fh.write("argv: %s\n" % json.dumps(argv))
    log_fh.flush()

    # encoding is named on purpose: text mode alone decodes with the locale
    # codec, which is cp1252 on this box. An LTX prompt carries an ellipsis and
    # Wan negatives carry Chinese, and that decode happens on subprocess's
    # reader thread -- the error never reaches us, stdout is silently set to
    # None, and the crash surfaces later somewhere unrelated.
    proc = subprocess.Popen(
        argv, cwd=cwd, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        universal_newlines=True, encoding="utf-8", errors="replace", bufsize=1,
    )
    for line in proc.stdout:
        log_fh.write(line)
        log_fh.flush()
    rc = proc.wait()
    log_fh.write("==== step %s END rc=%d %s ====\n" % (step.get("name", "?"), rc, utcnow()))
    log_fh.flush()
    return rc


# Media a §7.2 sidecar is written beside, and the two names the pipeline writes
# it under (licence_gate.META_EXT -- kept as literals because this file runs on
# the box against a python that must import nothing from the site build).
SIDECAR_MEDIA_EXT = (".mp4", ".webm", ".mov", ".mkv", ".m4v", ".gif",
                     ".png", ".jpg", ".jpeg",
                     ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac")
SIDECAR_EXT = (".meta.yaml", ".meta.yml")


def sidecar_beside(path: str):
    """The provenance record written next to one artifact, or None.

    Both naming conventions, because the pipeline writes both: `07-x.mp4.meta.yaml`
    (video_task.write_sidecar, hold_still) and `07-x.meta.yaml` (render_t3,
    intake_take). Same rule as licence_gate.sidecar_for, spelled out here rather
    than imported: this module is the one the render box runs, and it must not
    grow a dependency on the site builder's stack.
    """
    stem = os.path.splitext(path)[0]
    for ext in SIDECAR_EXT:
        for cand in (path + ext, stem + ext):
            if os.path.exists(cand):
                return cand
    return None


def with_sidecars(artifacts) -> tuple:
    """(artifacts + the records beside them, media whose record is missing).

    THE ASYMMETRY THIS CLOSES (2026-08-10). ltx_i2v writes a sidecar beside every
    clip it exports, but a job's `artifacts:` list names the mp4 and nothing else
    -- 116 of the 117 specs in pipeline/jobs/ do -- so "collect the artifacts"
    means "collect the mp4", and the record stays on the box. Five LTX clips
    reached the tree that way with no provenance at all and were force-added, and
    the publish gate read the silence as "not the build's problem". A record that
    does not travel with its clip may as well not have been written.

    The absence is REPORTED, never fatal: the clip exists, the GPU time is spent,
    and failing a finished render over a missing yaml would burn four minutes of
    card time to re-render pixels that are already correct. Whether such a clip
    may be PUBLISHED is build_site.publishable()'s question; this is the line
    that stops the record being left behind in the first place, and that names
    the clip out loud when it was.
    """
    out, missing = [], []
    for a in artifacts:
        out.append(a)
        if not a.lower().endswith(SIDECAR_MEDIA_EXT):
            continue
        side = sidecar_beside(a)
        if side is None:
            missing.append(a)
        elif side not in out:
            out.append(side)
    return out, missing


# Two failures that look identical in the queue and are ninety minutes apart in
# the correct response. 92 has always meant "the artifacts this job declared are
# not on disk" and it was returned for BOTH of them; RC_PUBLISHED_NOTHING splits
# off the one where every step exited zero and NOTHING the job declared landed,
# which is what a wrong publish glob or a wrong artifacts declaration looks like
# from here. Both codes are defined once, in THE RC TABLE at the top of this
# file -- read it before inventing a third.

# `05-the-patrol-ipa-r0-w015-s0.png` is what the sampler writes; a spec cloned
# without the beat SLUG declares `05-ipa-r0-w015-s0.png`. Same beat number, same
# tail, one missing segment in between.
_BEAT_STEM = re.compile(r"^(\d{1,3})-(.+)$")


def resolve_artifact(declared: str):
    """(path on disk, note) for one declared artifact, tolerating the beat slug.

    THE DEFECT THIS ABSORBS (2026-08-14, six plates). The samplers name their
    output `<beat>-<slug>-<rest>` -- the slug is the beat's own name, `the-patrol`,
    `the-clipboard` -- and a spec cloned from a template that predates the slug
    declares `<beat>-<rest>`. Six scene plates rendered perfectly, published 32
    files apiece, and were retired FAILED because the four filenames their spec
    named did not exist. Re-publishing them took forty seconds; re-rendering
    them, the response the queue's rc invited, would have been ninety minutes of
    card time redrawing frames already on disk.

    So a declared name that is missing is retried once with the slug wildcarded
    in: `05-*-ipa-r0-w015-s0.png`. A SINGLE match resolves, and says so in the
    log and in the job record -- the spec is still wrong and the note is how
    anyone learns that. Several matches do not resolve: guessing which frame a
    job meant is exactly the silent substitution the declared-artifact check
    exists to prevent.
    """
    if os.path.exists(declared):
        return declared, None
    m = _BEAT_STEM.match(os.path.basename(declared))
    if not m:
        return None, None
    pattern = os.path.join(os.path.dirname(declared),
                           "%s-*-%s" % (m.group(1), m.group(2)))
    hits = sorted(p for p in glob.glob(pattern) if os.path.exists(p))
    if len(hits) == 1:
        return hits[0], ("declared %s, found %s -- the spec dropped the beat "
                         "slug; resolved, but FIX THE SPEC"
                         % (os.path.basename(declared), os.path.basename(hits[0])))
    if len(hits) > 1:
        return None, ("declared %s matches %d slugged files (%s) -- ambiguous, "
                      "not resolving; name one in the spec"
                      % (os.path.basename(declared), len(hits),
                         ", ".join(os.path.basename(h) for h in hits[:4])))
    return None, None


def resolve_artifacts(declared) -> tuple:
    """(present, missing, notes) over a job's whole declared artifact list."""
    present, missing, notes = [], [], []
    for a in declared:
        got, note = resolve_artifact(a)
        if note:
            notes.append(note)
        (present if got else missing).append(got or a)
    return present, missing, notes


def neighbours_of(paths, limit: int = 12):
    """What IS in the directories a job's missing artifacts point at.

    A bare "declared artifacts missing" names only the files that are absent,
    which is the half of the comparison nobody needs: the question is always
    "then what did the sampler write?", and answering it took an ssh session
    and a directory listing. It is two lines of listing here.
    """
    seen, out = set(), []
    for p in paths:
        d = os.path.dirname(p) or "."
        if d in seen:
            continue
        seen.add(d)
        try:
            names = sorted(os.listdir(d))
        except OSError as exc:
            out.append("%s -- unreadable (%s)" % (d, exc.__class__.__name__))
            continue
        out.append("%s -- %d file(s): %s%s"
                   % (d, len(names), ", ".join(names[:limit]),
                      " ..." if len(names) > limit else ""))
    return out


def execute(job: dict, job_path: str, queue: Queue) -> tuple:
    """Run every step. Returns (outcome, rc, log_path)."""
    jid = job.get("id") or os.path.basename(job_path)[:-5]
    log_path = os.path.join(queue.dir("running"), jid + ".log")
    started = utcnow()

    job["started_at"] = started
    job["attempts"] = int(job.get("attempts", 0)) + 1
    job["runner_pid"] = os.getpid()
    job["runner_host"] = socket.gethostname()
    write_json(job_path, job)

    queue.beat({
        "event": "job_start", "job": jid, "task": job.get("task"),
        "worker": job.get("worker"), "beat": job.get("beat"),
        "attempt": job["attempts"], "claimed_by": "box-runner",
    })

    rc = 0
    failed_step = None
    holds_card = bool(job.get("needs_gpu", True))
    if holds_card:
        take_claim(jid)
    with open(log_path, "a", encoding="utf-8", errors="replace") as log_fh:
        log_fh.write("#### job %s attempt %d start %s\n" % (jid, job["attempts"], started))
        try:
            for step in job.get("steps", []):
                try:
                    rc = run_step(step, log_fh, job.get("env") or {})
                except Exception:
                    log_fh.write("!! step raised\n" + traceback.format_exc())
                    rc = RC_STEP_RAISED
                if rc != 0 and not step.get("allow_fail"):
                    failed_step = step.get("name")
                    break
                rc = 0 if step.get("allow_fail") else rc
        finally:
            if holds_card:
                drop_claim(jid)

        declared = job.get("artifacts", [])
        present, missing, slug_notes = resolve_artifacts(declared)
        for note in slug_notes:
            log_fh.write("!! SLUG-TOLERANT MATCH: %s\n" % note)
        job["artifact_notes"] = slug_notes
        if rc == 0 and missing:
            log_fh.write("!! declared artifacts missing: %s\n" % json.dumps(missing))
            for line in neighbours_of(missing):
                log_fh.write("   on disk: %s\n" % line)
            if not present:
                # EVERY step exited zero and not one declared file landed. That
                # is not a render that crashed -- it is a job that published
                # nothing, and on 2026-08-14 the two were indistinguishable in
                # the queue for six plates that had rendered fine. Say which
                # one it is, in the log and in the rc.
                log_fh.write(
                    "!! PUBLISHED NOTHING. Every step exited 0 and NONE of the "
                    "%d declared artifacts exist. The render did not crash: "
                    "either the publish glob or the artifacts list does not "
                    "match what the sampler wrote (the beat slug is the usual "
                    "culprit -- see the listing above). Re-publishing is "
                    "seconds; re-rendering is not the fix.\n" % len(declared))
                rc = RC_PUBLISHED_NOTHING
                failed_step = "publish-empty"
            else:
                rc = RC_ARTIFACTS_MISSING
                failed_step = "artifact-check"
        present, unprovenanced = with_sidecars(present)
        if unprovenanced:
            log_fh.write("!! NO PROVENANCE RECORD beside: %s\n"
                         "   the clip is on disk and the job stands, but nothing "
                         "says what made it, so nobody downstream can say whether "
                         "it may ship — write the sidecar (§7.2)\n"
                         % json.dumps(unprovenanced))
        log_fh.write("#### job %s finished rc=%d %s\n" % (jid, rc, utcnow()))

    job["finished_at"] = utcnow()
    job["rc"] = rc
    job["failed_step"] = failed_step
    job["unprovenanced"] = unprovenanced
    # The sidecar rides in the artifact list, so whoever couriers "the artifacts"
    # takes the record with the clip rather than the clip alone (with_sidecars).
    job["artifacts_present"] = present
    write_json(job_path, job)

    outcome = "done" if rc == 0 else "failed"
    final_log = os.path.join(queue.dir(outcome), os.path.basename(log_path))
    if os.path.exists(final_log):
        os.remove(final_log)
    shutil.move(log_path, final_log)
    final_job = queue.retire(job_path, outcome)

    queue.beat({
        "event": "job_" + outcome, "job": jid, "task": job.get("task"),
        "worker": job.get("worker"), "beat": job.get("beat"), "rc": rc,
        "failed_step": failed_step, "claimed_by": "box-runner",
        "artifacts": job["artifacts_present"], "log": final_log,
        # Named on the branch, not only in a log on the box: a record nobody
        # off this machine can see is the same silence this field exists to end.
        "unprovenanced": unprovenanced,
        "started_at": started, "finished_at": job["finished_at"],
        # The job record and the tail of its log ride along to the branch. A
        # DONE line says a job finished; these say what it actually did, and
        # they are what someone reads when the mp4 itself is 40MB and staying
        # on the box.
        "files": {jid + ".json": json.dumps(job, indent=2, ensure_ascii=False),
                  jid + ".log": tail_text(final_log)},
    })
    return outcome, rc, final_job


def tail_text(path: str, lines: int = 200, cap: int = 40000) -> str:
    """The last `lines` of a log, clipped to `cap` bytes. Never raises."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = "".join(fh.readlines()[-lines:])
    except OSError as exc:
        return "(log unreadable: %s)\n" % exc
    return text[-cap:]


def adopt_interrupted(queue: Queue) -> None:
    """A job in running/ at startup died with its runner. Retire it honestly."""
    for name in sorted(os.listdir(queue.dir("running"))):
        if not name.endswith(".json"):
            continue
        path = os.path.join(queue.dir("running"), name)
        try:
            with open(path, encoding="utf-8") as fh:
                job = json.load(fh)
        except Exception:
            job = {"id": name[:-5]}
        jid = job.get("id", name[:-5])
        attempts = int(job.get("attempts", 1))
        max_attempts = int(job.get("max_attempts", 1))
        job["interrupted"] = True
        job["interrupted_at"] = utcnow()

        if attempts < max_attempts:
            job["rc"] = None
            write_json(path, job)
            os.rename(path, os.path.join(queue.dir("ready"), name))
            queue.beat({"event": "job_requeued_after_interrupt", "job": jid,
                        "attempts": attempts, "max_attempts": max_attempts,
                        "claimed_by": "box-runner"})
            continue

        job["rc"] = RC_INTERRUPTED
        job["failed_step"] = "interrupted"
        write_json(path, job)
        queue.retire(path, "failed")
        stray = os.path.join(queue.dir("running"), jid + ".log")
        if os.path.exists(stray):
            shutil.move(stray, os.path.join(queue.dir("failed"), jid + ".log"))
        queue.beat({"event": "job_failed", "job": jid, "rc": RC_INTERRUPTED,
                    "failed_step": "interrupted", "claimed_by": "box-runner",
                    "note": "runner died mid-render; not re-run automatically"})


# --------------------------------------------------------------------------
# main loop
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="drain the box-resident render queue")
    ap.add_argument("--root", default=os.environ.get("BANYAN_QUEUE_ROOT", DEFAULT_ROOT))
    ap.add_argument("--once", action="store_true",
                    help="drain what is ready, then exit (default: run forever)")
    ap.add_argument("--poll", type=int, default=POLL_SECONDS)
    ap.add_argument("--max-jobs", type=int, default=0, help="0 = unlimited")
    ap.add_argument("--no-wait", action="store_true",
                    help="with --once, exit instead of waiting for a busy GPU")
    ap.add_argument("--repo", default=os.environ.get("BANYAN_REPO", DEFAULT_REPO),
                    help="git clone the courier borrows objects and deploy key from")
    ap.add_argument("--courier-worktree",
                    default=os.environ.get("BANYAN_COURIER_WORKTREE", DEFAULT_COURIER_WORKTREE),
                    help="dedicated worktree the courier commits in (never the render checkout)")
    ap.add_argument("--branch", default=COURIER_BRANCH)
    ap.add_argument("--no-courier", action="store_true",
                    help="keep heartbeats local; nothing is published to the repo")
    args = ap.parse_args(argv)

    runner_log = os.path.join(args.root, "runner.log")

    def say(msg: str) -> None:
        line = "%s %s\n" % (utcnow(), msg)
        sys.stdout.write(line)
        sys.stdout.flush()
        try:
            with open(runner_log, "a", encoding="utf-8") as fh:
                fh.write(line)
        except OSError:
            pass

    courier = None
    if not args.no_courier:
        courier = Courier(args.courier_worktree, args.branch, args.repo, log=say)
    queue = Queue(args.root, courier=courier)

    if not acquire_lock(queue.lock_path):
        say("another runner holds %s -- exiting" % queue.lock_path)
        return 75

    # Belt to the try/finally's braces. `finally` covers a return or a raise but
    # not os._exit or a SIGTERM handler someone adds later; atexit covers those.
    # Both are idempotent -- release_lock only removes a lock this pid wrote.
    atexit.register(release_lock, queue.lock_path)

    say("runner up pid=%d root=%s" % (os.getpid(), args.root))

    done_count = 0
    last_idle_beat = 0.0
    consecutive_errors = 0
    try:
        queue.beat({"event": "runner_up", "root": args.root})
        # A predecessor that died mid-render also died holding the card. Clearing
        # our own stale claim here is what stops one crash from locking the GPU
        # out permanently; a hand lane's claim is left strictly alone.
        if not claim_is_foreign(read_claim()):
            drop_claim("startup-sweep")
        adopt_interrupted(queue)
        while True:
            # Everything below is wrapped because the loop's own bookkeeping can
            # raise for reasons that have nothing to do with the render: a
            # listdir racing the enqueuer, a full disk on the heartbeat write, a
            # courier bug. None of those are a reason to hand the card back.
            # execute() already contains its own per-step handling; this is the
            # net under the scheduler itself.
            try:
                names = queue.ready_jobs()
                if not names:
                    if args.once:
                        say("queue empty -- --once, exiting")
                        break
                    now = time.time()
                    if now - last_idle_beat > HEARTBEAT_SECONDS:
                        queue.beat({"event": "runner_idle", "ready": 0,
                                    "failed": queue.failed_count()})
                        last_idle_beat = now
                    time.sleep(args.poll)
                    consecutive_errors = 0
                    continue

                name = names[0]

                # Peek before claiming so a job waiting on the card stays visible
                # in ready/ rather than sitting invisibly in running/.
                try:
                    with open(os.path.join(queue.dir("ready"), name), encoding="utf-8") as fh:
                        peek = json.load(fh)
                except Exception:
                    peek = {}
                if peek.get("needs_gpu", True):
                    busy, why = gpu_busy()
                    if busy:
                        now = time.time()
                        if now - last_idle_beat > HEARTBEAT_SECONDS:
                            say("waiting for GPU (%s) -- %s queued" % (why, len(names)))
                            queue.beat({"event": "runner_waiting_for_gpu", "reason": why,
                                        "next_job": name[:-5], "ready": len(names),
                                        "failed": queue.failed_count()})
                            last_idle_beat = now
                        if args.once and args.no_wait:
                            say("GPU busy and --no-wait -- exiting")
                            break
                        time.sleep(args.poll)
                        consecutive_errors = 0
                        continue

                claimed = queue.claim(name)
                if not claimed:
                    continue
                try:
                    with open(claimed, encoding="utf-8") as fh:
                        job = json.load(fh)
                except Exception:
                    say("unreadable job %s -- failing it" % name)
                    queue.retire(claimed, "failed")
                    queue.beat({"event": "job_failed", "job": name[:-5],
                                "rc": RC_JOB_UNREADABLE,
                                "failed_step": "parse", "claimed_by": "box-runner"})
                    continue

                say("claimed %s" % name)
                outcome, rc, _ = execute(job, claimed, queue)
                say("%s -> %s rc=%d" % (name, outcome, rc))
                done_count += 1
                last_idle_beat = 0.0
                consecutive_errors = 0
                if args.max_jobs and done_count >= args.max_jobs:
                    say("hit --max-jobs %d -- exiting" % args.max_jobs)
                    break
            except KeyboardInterrupt:
                raise
            except Exception:
                consecutive_errors += 1
                say("!! loop error %d/%d, continuing:\n%s"
                    % (consecutive_errors, MAX_CONSECUTIVE_ERRORS, traceback.format_exc()))
                # A wall of identical tracebacks is a broken runner pretending to
                # work; give up loudly so the keepalive schedule restarts us clean.
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    say("!! %d consecutive loop errors -- exiting for a clean restart"
                        % consecutive_errors)
                    break
                time.sleep(args.poll)
    except KeyboardInterrupt:
        say("interrupted")
    finally:
        queue.beat({"event": "runner_down", "jobs_completed": done_count})
        say("runner down after %d job(s)" % done_count)
        release_lock(queue.lock_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
