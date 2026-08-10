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
import json
import os
import shutil
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
        p = self._git("push", "-f", "origin", self.branch, timeout=300)
        if p.returncode:
            self.unpushed += 1
            self.log("!! COURIER PUSH FAILED (%d in a row) -- results are on this "
                     "box only, in %s\n   %s"
                     % (self.unpushed, self.out,
                        (p.stderr or p.stdout or "").strip()[-300:]))
        elif self.unpushed:
            self.log("courier push recovered after %d failure(s)" % self.unpushed)
            self.unpushed = 0

    # -- the public surface ------------------------------------------------

    def mark(self, line: str, message: str, files: dict = None) -> None:
        """Append one heartbeat line (+ optional small files) and push."""
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
            self._publish(message)
        except Exception:
            self.log("!! courier raised, renders continue:\n" + traceback.format_exc())

    def emit(self, record: dict) -> None:
        """Translate a queue heartbeat record into the shared grammar."""
        event = record.get("event", "")
        jid = record.get("job", "?")
        if event == "job_start":
            self.mark("STARTED task=%s attempt=%s on box-runner"
                      % (jid, record.get("attempt", 1)), "hb: STARTED %s" % jid)
        elif event == "job_done":
            self.mark("DONE task=%s rc=0 artifacts=%d"
                      % (jid, len(record.get("artifacts") or [])),
                      "hb: DONE %s" % jid, files=record.get("files"))
        elif event == "job_failed":
            self.mark("FAIL task=%s rc=%s step=%s"
                      % (jid, record.get("rc"), record.get("failed_step")),
                      "hb: FAIL %s" % jid, files=record.get("files"))
        elif event == "job_requeued_after_interrupt":
            self.mark("INTERRUPTED task=%s requeued attempt %s/%s"
                      % (jid, record.get("attempts"), record.get("max_attempts")),
                      "hb: INTERRUPTED %s" % jid)
        elif event == "runner_up":
            self.mark("box-runner up pid=%s host=%s"
                      % (record.get("pid"), record.get("host")), "hb: runner up")
        elif event == "runner_down":
            self.mark("box-runner down after %s job(s)"
                      % record.get("jobs_completed"), "hb: runner down")
        elif event == "runner_idle":
            self.mark("box-runner idle ready=%s failed=%s"
                      % (record.get("ready", 0), record.get("failed", 0)),
                      "hb: idle")
        elif event == "runner_waiting_for_gpu":
            self.mark("box-runner waiting for GPU: %s failed=%s"
                      % (record.get("reason"), record.get("failed", 0)),
                      "hb: waiting for GPU")


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
        return 90
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
                    rc = 91
                if rc != 0 and not step.get("allow_fail"):
                    failed_step = step.get("name")
                    break
                rc = 0 if step.get("allow_fail") else rc
        finally:
            if holds_card:
                drop_claim(jid)

        missing = [a for a in job.get("artifacts", []) if not os.path.exists(a)]
        if rc == 0 and missing:
            log_fh.write("!! declared artifacts missing: %s\n" % json.dumps(missing))
            rc = 92
            failed_step = "artifact-check"
        log_fh.write("#### job %s finished rc=%d %s\n" % (jid, rc, utcnow()))

    job["finished_at"] = utcnow()
    job["rc"] = rc
    job["failed_step"] = failed_step
    job["artifacts_present"] = [a for a in job.get("artifacts", []) if os.path.exists(a)]
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

        job["rc"] = 93
        job["failed_step"] = "interrupted"
        write_json(path, job)
        queue.retire(path, "failed")
        stray = os.path.join(queue.dir("running"), jid + ".log")
        if os.path.exists(stray):
            shutil.move(stray, os.path.join(queue.dir("failed"), jid + ".log"))
        queue.beat({"event": "job_failed", "job": jid, "rc": 93,
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
                    queue.beat({"event": "job_failed", "job": name[:-5], "rc": 94,
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
