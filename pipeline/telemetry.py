#!/usr/bin/env python3
r"""GPU + RAM telemetry for the big render house — sample, distil, publish.

Born 2026-08-04, out of the day's BSOD forensics: the 5090 bluescreened mid-render
and NOTHING said what the machine was doing when it went. Was VRAM at 23 of 24 GB?
Was commit charge against the page-file limit? We could not answer, because the
courier branch carries what the RENDER said and nothing about the HOST. This is the
missing half: a 10-second pulse of GPU utilisation and memory, kept for 48 hours on
the box and published as a 24-hour, 1-minute-resolution summary the public status
page can draw.

Runs ON the box, detached, as scheduled task `banyan-telemetry`
(`C:\banyan-farm\telemetry.cmd` → `--daemon`). Deliberately:

- **read-only toward every other process.** `nvidia-smi --query-gpu` and
  `GlobalMemoryStatusEx` observe; nothing here signals, throttles or waits on a
  render, a download, or the farm worker.
- **not in either venv.** It runs on the box's system python and imports nothing
  that is not in the stdlib (psutil is used only if it happens to be importable).
  A venv reinstall mid-render must not be able to blind the telemetry.
- **its own git repo**, `C:\banyan-farm\telemetry-git`: a blobless, depth-1
  partial clone that never checks anything out. The farm worker owns the working
  tree of `C:\banyan-farm\banyan-city` and switches ITS branch to
  farm-results-rtx5090 as it heartbeats — a second process doing git work in that
  tree is the 2026-07-31 two-workers bug with a different hat. So we build the
  commit with plumbing (ls-tree → mktree --missing → commit-tree) on top of
  whatever the remote tip is, and push only that one commit. Nothing is ever
  checked out and no blob is ever read: the branch tip is ~960 MB of episode
  media and this file is 40 KB.

  Consequence worth knowing: `Courier.mark()` in farm_worker.py pushes with
  `-f`, from a tree that has no telemetry.json — so a heartbeat DROPS the file
  from the branch. That is why `--daemon` also polls `git ls-remote` every
  minute: whenever the branch tip moves under us we re-publish immediately, so
  the blink is ~a minute rather than a full publish interval. The status page
  treats a missing or stale file as "no recent telemetry" and says so.

Operating it on the box (the three files that make it a service):

    C:\banyan-farm\telemetry.py        this file, scp'd from pipeline/telemetry.py
    C:\banyan-farm\telemetry.cmd       the wrapper (pipeline/telemetry.cmd)
    schtasks task `banyan-telemetry`   registered by pipeline/mktask-telemetry.ps1

It has an AtLogOn trigger as well as the manual start, because the history matters
most across a reboot — but LogonType is Interactive, so after an unattended reboot
with nobody logged in it still needs a hand, exactly like the other banyan-* tasks:

    schtasks /run /tn banyan-telemetry
    schtasks /query /tn banyan-telemetry /fo LIST    (want: Status: Running)

To restart it after changing this file, END THE TASK AND THEN KILL THE PYTHON:
`schtasks /end` stops telemetry.cmd but leaves the daemon it launched orphaned, and
the orphan still holds the pid lock, so the fresh copy exits immediately (it says so
in telemetry.log rather than dying quietly — but the sampler you wanted is not the
one running). Kill the `telemetry.py --daemon` pid, then `schtasks /run`.

Modes:

    telemetry.py --sample-once   one sample to stdout; touches no file, no network
    telemetry.py --distil        rebuild telemetry.json from the CSV; no network
    telemetry.py --publish-once  distil, then push to the courier branch, and exit
    telemetry.py --daemon        the real thing: sample 10s, publish 5 min, forever
"""

import argparse
import ctypes
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

FARM = Path(os.environ.get("BANYAN_FARM", r"C:\banyan-farm"))
CSV_PATH = FARM / "telemetry.csv"
JSON_PATH = FARM / "telemetry.json"
LOG_PATH = FARM / "telemetry.log"
TEL_GIT = FARM / "telemetry-git"
# The key the farm worker already pushes with. Referenced BY PATH only — this
# script never reads, copies or logs its contents.
DEPLOY_KEY = FARM / "farm_deploy_key"
REMOTE = "git@github.com:olegmlkvorg/banyan-city.git"
BRANCH = "farm-results-rtx5090"
PUBLISH_PATH = "telemetry.json"      # path inside BRANCH → the raw URL the page fetches
HOST = "rtx5090"
# How publish() recognises its own commits, so each one replaces the last instead
# of piling up on a branch that exists to carry render results.
COMMIT_PREFIX = "telemetry: "

SAMPLE_SECONDS = 10
PUBLISH_SECONDS = 300                # 5 minutes, per the ask
REMOTE_CHECK_SECONDS = 60            # see the `-f` note in the module docstring
PRUNE_SECONDS = 1800
KEEP_HOURS = 48                      # the rolling CSV on the box
WINDOW_HOURS = 24                    # what the published summary covers
BUCKET_SECONDS = 60                  # published resolution
LOG_CAP_BYTES = 1_000_000

COLUMNS = ["ts", "gpu_util", "gpu_mem_util", "vram_used_mb", "vram_total_mb",
           "gpu_temp_c", "gpu_power_w", "ram_used_mb", "ram_total_mb",
           "commit_used_mb", "commit_limit_mb"]

# No console window per sample: this fires 8,640 times a day on an interactive
# scheduled task, and a flashing window every ten seconds on the machine someone
# is rendering on is its own kind of damage.
NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
    print(line, flush=True)
    try:
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > LOG_CAP_BYTES:
            tail = LOG_PATH.read_text(encoding="utf-8", errors="replace")[-200_000:]
            LOG_PATH.write_text(f"(truncated)\n{tail}", encoding="utf-8", errors="replace")
        with LOG_PATH.open("a", encoding="utf-8", errors="replace") as f:
            f.write(line + "\n")
    except OSError:
        pass                          # logging must never kill the thing it logs


def run(args, cwd=None, timeout=180, stdin_text=None, env=None):
    """A subprocess, utf-8 pinned. cp1252 has killed five things in this repo."""
    return subprocess.run(args, cwd=str(cwd) if cwd else None, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=timeout, creationflags=NO_WINDOW,
                          input=stdin_text, env=env)


# ---------------------------------------------------------------- sampling

def _num(tok: str):
    """nvidia-smi prints '[N/A]' for fields a laptop GPU does not expose."""
    tok = (tok or "").strip()
    try:
        return float(tok)
    except ValueError:
        return None


def gpu_name() -> str:
    try:
        r = run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip().splitlines()[0].strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return ""


def gpu_sample() -> dict:
    """One read-only nvidia-smi query. Empty dict if the driver did not answer."""
    q = ("utilization.gpu,utilization.memory,memory.used,memory.total,"
         "temperature.gpu,power.draw")
    try:
        r = run(["nvidia-smi", f"--query-gpu={q}", "--format=csv,noheader,nounits"],
                timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        log(f"nvidia-smi unavailable: {e}")
        return {}
    if r.returncode != 0 or not r.stdout.strip():
        log(f"nvidia-smi rc={r.returncode} {(r.stderr or '').strip()[:200]}")
        return {}
    # first GPU only — this box has one, and a summary that silently averaged two
    # cards would be a lie the page could not see
    parts = r.stdout.strip().splitlines()[0].split(",")
    if len(parts) < 6:
        return {}
    util, memutil, used, total, temp, power = (_num(p) for p in parts[:6])
    return {"gpu_util": util, "gpu_mem_util": memutil, "vram_used_mb": used,
            "vram_total_mb": total, "gpu_temp_c": temp, "gpu_power_w": power}


class _MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def host_sample() -> dict:
    """Physical RAM and COMMIT CHARGE, in MB.

    Commit charge is the number that matters here and psutil does not expose it:
    physical RAM can look calm while committed memory runs at the page-file limit,
    and that is the shape of a memory failure on Windows. GlobalMemoryStatusEx
    gives both from one call (Total/AvailPageFile == the commit limit and what is
    left of it), so the ctypes path is the primary, not a fallback. psutil, if the
    interpreter happens to have it, only cross-checks the physical figures.
    """
    out = {}
    try:
        m = _MEMORYSTATUSEX()
        m.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
            mb = 1024 * 1024
            out = {"ram_used_mb": (m.ullTotalPhys - m.ullAvailPhys) / mb,
                   "ram_total_mb": m.ullTotalPhys / mb,
                   "commit_used_mb": (m.ullTotalPageFile - m.ullAvailPageFile) / mb,
                   "commit_limit_mb": m.ullTotalPageFile / mb}
    except (AttributeError, OSError) as e:
        log(f"GlobalMemoryStatusEx unavailable: {e}")
    if not out:
        try:
            import psutil
            v = psutil.virtual_memory()
            mb = 1024 * 1024
            out = {"ram_used_mb": (v.total - v.available) / mb,
                   "ram_total_mb": v.total / mb}
        except Exception as e:                      # noqa: BLE001 — telemetry never dies
            log(f"psutil unavailable too: {e}")
    return out


def sample(now: float = None) -> dict:
    row = {"ts": int(now if now is not None else time.time())}
    row.update(gpu_sample())
    row.update(host_sample())
    return row


# ---------------------------------------------------------------- the rolling CSV

def csv_line(row: dict) -> str:
    def fmt(k):
        v = row.get(k)
        if v is None:
            return ""
        return str(int(v)) if k == "ts" else f"{float(v):.1f}".rstrip("0").rstrip(".")
    return ",".join(fmt(k) for k in COLUMNS)


def append_row(row: dict, path: Path = None) -> None:
    path = path or CSV_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="\n") as f:
        if new:
            f.write(",".join(COLUMNS) + "\n")
        f.write(csv_line(row) + "\n")


def read_rows(path: Path = None, since: float = None) -> list:
    """Parsed CSV rows, oldest first. Unparseable lines are skipped, not fatal —
    a row half-written when the host died is a fact about the host, not a crash."""
    path = path or CSV_PATH
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip() or line.startswith("ts,"):
            continue
        parts = line.split(",")
        if len(parts) < 2:
            continue
        try:
            ts = int(float(parts[0]))
        except ValueError:
            continue
        if since is not None and ts < since:
            continue
        row = {"ts": ts}
        for k, tok in zip(COLUMNS[1:], parts[1:]):
            row[k] = _num(tok)
        rows.append(row)
    rows.sort(key=lambda r: r["ts"])
    return rows


def prune(path: Path = None, keep_hours: float = KEEP_HOURS, now: float = None) -> int:
    """Drop rows older than keep_hours. Rewrite via a temp file + os.replace so a
    kill mid-prune cannot leave a truncated CSV — 48h at 10s is ~17k rows, ~1 MB,
    so honesty is cheaper than cleverness here."""
    path = path or CSV_PATH
    if not path.exists():
        return 0
    now = now if now is not None else time.time()
    rows = read_rows(path)
    keep = [r for r in rows if r["ts"] >= now - keep_hours * 3600]
    if len(keep) == len(rows):
        return 0
    tmp = path.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        f.write(",".join(COLUMNS) + "\n")
        for r in keep:
            f.write(csv_line(r) + "\n")
    os.replace(tmp, path)
    return len(rows) - len(keep)


# ---------------------------------------------------------------- the summary

def _mean(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def _r(v, nd=1):
    return None if v is None else round(v, nd)


def distil(rows: list, now: float = None, window_hours: float = WINDOW_HOURS,
           bucket_seconds: int = BUCKET_SECONDS, gpu: str = "") -> dict:
    """CSV rows → the compact object the page draws. Pure: no disk, no network.

    Arrays, not objects, and one array per series: 1,440 minute-buckets of six
    numbers is ~40 KB of JSON, where a list of dicts is four times that for the
    same facts. Buckets with no sample are simply ABSENT — the series is sparse on
    purpose, and the page breaks the line wherever the gap is bigger than a few
    minutes. An interpolated line across an outage would draw utilisation for
    hours in which the machine was off, which is precisely the class of claim the
    site is not allowed to make.
    """
    now = now if now is not None else time.time()
    cut = now - window_hours * 3600
    buckets = {}
    for r in rows:
        if r["ts"] < cut:
            continue
        buckets.setdefault(r["ts"] // bucket_seconds * bucket_seconds, []).append(r)
    t, u, up, v, ram, com = [], [], [], [], [], []
    for key in sorted(buckets):
        b = buckets[key]
        utils = [x.get("gpu_util") for x in b if x.get("gpu_util") is not None]
        t.append(int(key))
        u.append(int(round(_mean(utils))) if utils else None)
        up.append(int(max(utils)) if utils else None)
        v.append(_r((_mean([x.get("vram_used_mb") for x in b]) or 0) / 1024, 2)
                 if any(x.get("vram_used_mb") is not None for x in b) else None)
        ram.append(_r((_mean([x.get("ram_used_mb") for x in b]) or 0) / 1024, 2)
                   if any(x.get("ram_used_mb") is not None for x in b) else None)
        com.append(_r((_mean([x.get("commit_used_mb") for x in b]) or 0) / 1024, 2)
                   if any(x.get("commit_used_mb") is not None for x in b) else None)
    last = rows[-1] if rows else {}

    def total(key, nd=2):
        for r in reversed(rows):
            if r.get(key):
                return _r(r[key] / 1024, nd)
        return None

    return {
        "schema": 1,
        "host": HOST,
        "gpu_name": gpu or "",
        # generated is when this file was WRITTEN; last_sample is the newest fact
        # in it. They differ when the sampler dies and something else republishes,
        # and the page must age itself off last_sample, never off generated.
        "generated": int(now),
        "last_sample": int(last["ts"]) if last else None,
        "sample_seconds": SAMPLE_SECONDS,
        "bucket_seconds": bucket_seconds,
        "window_hours": window_hours,
        "vram_total_gb": total("vram_total_mb"),
        "ram_total_gb": total("ram_total_mb"),
        "commit_limit_gb": total("commit_limit_mb"),
        "legend": {"t": "unix seconds, start of each bucket (UTC)",
                   "u": "mean GPU utilisation %", "up": "peak GPU utilisation %",
                   "v": "mean VRAM in use, GB", "r": "mean host RAM in use, GB",
                   "c": "mean commit charge, GB", "null": "no sample in that bucket"},
        "t": t, "u": u, "up": up, "v": v, "r": ram, "c": com,
    }


def write_json(obj: dict, path: Path = None) -> Path:
    """Atomic. The published file is read by a browser and (when the branch tip
    moves) committed by another process; a half-written JSON must never exist."""
    path = path or JSON_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(obj, separators=(",", ":")), encoding="utf-8")
    os.replace(tmp, path)
    return path


# ---------------------------------------------------------------- publishing

def git(*args, timeout=300, stdin_text=None):
    """git in the telemetry repo, with lazy fetching FORBIDDEN.

    GIT_NO_LAZY_FETCH=1 is the guard that makes this design safe, and it was
    learned the hard way on 2026-08-04: the first version of publish() built its
    tree through the index (read-tree → update-index → write-tree), and
    `write-tree` verifies that every entry's blob is present. In a blobless clone
    that means a promisor fetch of every blob in the branch — ~960 MB, kicked off
    while the box was mid-download of two model sets, and stalled at zero bytes
    for twelve minutes before it was killed. The tree is now built with
    `mktree --missing`, which asks for no blob at all; this env var turns any
    future slip of that kind into an instant error instead of a silent gigabyte.
    """
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
    return run(["git"] + list(args), cwd=TEL_GIT, timeout=timeout,
               stdin_text=stdin_text, env=env)


def ensure_repo() -> bool:
    """A blobless, never-checked-out repo whose only job is to add one file to the
    courier branch's tip tree. ~1 MB of trees instead of the ~960 MB the branch
    actually holds — the box is downloading two model sets right now and telemetry
    must not compete with them for the wire."""
    if (TEL_GIT / ".git").exists():
        return True
    if not shutil.which("git"):
        log("no git on PATH — telemetry will sample but cannot publish")
        return False
    TEL_GIT.mkdir(parents=True, exist_ok=True)
    if git("init", "-q").returncode:
        log("git init failed")
        return False
    git("remote", "add", "origin", REMOTE)
    # the SAME key and host policy the farm worker's clone already uses
    git("config", "core.sshCommand",
        f"ssh -i {DEPLOY_KEY.as_posix()} -o StrictHostKeyChecking=no -o BatchMode=yes")
    git("config", "core.autocrlf", "false")   # never CRLF-mangle a published blob
    git("config", "user.name", f"banyan telemetry ({HOST})")
    git("config", "user.email", "telemetry@banyan.city")
    git("config", "extensions.partialClone", "origin")
    git("config", "remote.origin.promisor", "true")
    git("config", "remote.origin.partialclonefilter", "blob:none")
    log(f"telemetry git repo initialised at {TEL_GIT}")
    return True


def remote_tip() -> str:
    r = git("ls-remote", "origin", f"refs/heads/{BRANCH}", timeout=120)
    if r.returncode or not r.stdout.strip():
        return ""
    return r.stdout.split()[0]


def publish(obj: dict = None) -> str:
    """Put telemetry.json on BRANCH at the current tip. Returns the pushed commit
    sha, or "" if it did not land — a failed publish is logged and retried on the
    next cycle, never fatal. Never force-pushes: if the worker moved the branch
    between our fetch and our push, git rejects us and the next cycle rebuilds on
    the new tip."""
    if obj is None:
        obj = distil(read_rows(), gpu=gpu_name())
    write_json(obj)
    if not ensure_repo():
        return ""
    # depth 6, not 1: enough to walk back over our OWN previous telemetry commits
    # and rebuild on the last commit the worker actually made. Still blobless, and
    # after the first cycle these trees are already local, so the fetch is bytes.
    r = git("fetch", "--filter=blob:none", "--depth=6", "origin", BRANCH)
    if r.returncode:
        log(f"fetch failed: {(r.stderr or r.stdout).strip()[-300:]}")
        return ""
    tip = git("rev-parse", "FETCH_HEAD").stdout.strip()
    if not tip:
        log("no FETCH_HEAD after fetch")
        return ""
    # REPLACE our last publish, do not stack on it. At one publish per five
    # minutes, stacking is 288 commits a day on a branch whose whole point is to
    # carry render results — a year of "telemetry:" commits burying them. So walk
    # back over consecutive commits of our own and build on the worker's tip.
    #
    # The lease is what makes the force safe: --force-with-lease against the sha we
    # just fetched can only ever overwrite THAT, and we only force at all when that
    # sha is a commit this script wrote. A worker heartbeat landing mid-cycle fails
    # the lease and we retry on the next one — the worker is never overwritten.
    base, lease, hops = tip, "", 0
    while hops < 5:
        subj = git("log", "-1", "--format=%s", base).stdout.strip()
        if not subj.startswith(COMMIT_PREFIX):
            break
        parent = git("rev-parse", f"{base}^").stdout.strip()
        if not parent:
            break                       # shallow boundary: stack this once, fine
        lease, base, hops = tip, parent, hops + 1
    blob = git("hash-object", "-w", "--path", PUBLISH_PATH, str(JSON_PATH)).stdout.strip()
    if not blob:
        log("hash-object failed")
        return ""
    # The whole tree, built without reading a single blob: list the tip's ROOT
    # entries (subtrees stay untouched, by sha), swap in our own telemetry.json,
    # and hand the listing to `mktree --missing` — the one plumbing command that
    # is explicitly allowed to reference objects this repo does not have. No
    # index, no write-tree, no promisor fetch. See git() for what that cost once.
    r = git("ls-tree", base)
    if r.returncode:
        log(f"ls-tree failed: {(r.stderr or '').strip()[-200:]}")
        return ""
    # -z, AND NUL separators on the way in. Not a style choice: subprocess in text
    # mode writes the child's stdin through a TextIOWrapper, which on Windows
    # translates every "\n" to "\r\n" — so a newline-separated listing reached
    # mktree with a trailing CR on every entry and it dutifully built a tree in
    # which each of the 38 root entries was named "CLAUDE.md\r", "genomes\r",
    # "telemetry.json\r". That commit was pushed and then rewound off the branch
    # (2026-08-04). NUL is not a newline, so nothing can translate it.
    lines = [ln.rstrip("\r") for ln in r.stdout.splitlines()
             if ln.strip() and not ln.rstrip("\r").endswith(f"\t{PUBLISH_PATH}")]
    lines.append(f"100644 blob {blob}\t{PUBLISH_PATH}")
    tree = git("mktree", "-z", "--missing",
               stdin_text="".join(ln + "\0" for ln in lines)).stdout.strip()
    if not tree:
        log("mktree failed")
        return ""
    stamp = time.strftime("%H:%M:%SZ", time.gmtime())
    commit = git("commit-tree", tree, "-p", base, "-m",
                 f"{COMMIT_PREFIX}{HOST} {stamp} ({len(obj.get('t', []))} min)").stdout.strip()
    if not commit:
        log("commit-tree failed")
        return ""
    args = ["push"]
    if lease:
        args.append(f"--force-with-lease=refs/heads/{BRANCH}:{lease}")
    r = git(*(args + ["origin", f"{commit}:refs/heads/{BRANCH}"]))
    if r.returncode:
        log(f"push rejected (branch moved — retrying next cycle): "
            f"{(r.stderr or r.stdout).strip()[-300:]}")
        return ""
    return commit


# ---------------------------------------------------------------- the daemon

def pid_alive(pid: int) -> bool:
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)   # QUERY_LIMITED_INFO
    if not h:
        return False
    code = ctypes.c_ulong()
    ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
    ctypes.windll.kernel32.CloseHandle(h)
    return bool(ok) and code.value == 259                        # STILL_ACTIVE


def claim() -> bool:
    """One sampler per box. The scheduled task is registered MultipleInstances
    IgnoreNew, so this only catches a hand-started second copy — and unlike the
    farm worker's lock it DOES take over a dead pid's claim, because a sampler
    that refuses to start after a bluescreen is useless exactly when the history
    matters most (which is the whole reason this file exists)."""
    lock = FARM / "telemetry.pid"
    try:
        if lock.exists():
            old = int((lock.read_text(encoding="utf-8", errors="replace").strip() or 0))
            if old and old != os.getpid() and pid_alive(old):
                log(f"another sampler is already running (pid {old}) — exiting")
                return False
        lock.write_text(str(os.getpid()), encoding="utf-8")
    except (OSError, ValueError) as e:
        log(f"could not take the sampler lock ({e}) — continuing anyway")
    return True


def daemon() -> int:
    if not claim():
        return 0
    gpu = gpu_name()
    log(f"telemetry daemon up — pid {os.getpid()}, gpu '{gpu or 'unknown'}', "
        f"sample {SAMPLE_SECONDS}s, publish {PUBLISH_SECONDS}s, csv {CSV_PATH}")
    now = time.time()
    next_sample, next_publish = now, now + SAMPLE_SECONDS
    next_remote, next_prune = now + PUBLISH_SECONDS, now + PRUNE_SECONDS
    pushed = ""
    while True:
        now = time.time()
        if now >= next_sample:
            try:
                append_row(sample(now))
            except Exception as e:                  # noqa: BLE001 — never die
                log(f"sample failed: {e}")
            # absolute schedule, so a slow nvidia-smi does not drift the series;
            # a long stall (sleep/hibernate) resets rather than firing a burst
            next_sample = max(now + 1, next_sample + SAMPLE_SECONDS)
        if now >= next_publish or (now >= next_remote and remote_tip() not in ("", pushed)):
            try:
                got = publish(distil(read_rows(), now=now, gpu=gpu))
                pushed = got or pushed
                log(f"published {'ok ' + got[:8] if got else 'FAILED (will retry)'}")
            except Exception as e:                  # noqa: BLE001
                log(f"publish failed: {e}")
            next_publish = now + PUBLISH_SECONDS
            next_remote = now + REMOTE_CHECK_SECONDS
        elif now >= next_remote:
            next_remote = now + REMOTE_CHECK_SECONDS
        if now >= next_prune:
            try:
                dropped = prune(now=now)
                if dropped:
                    log(f"pruned {dropped} row(s) older than {KEEP_HOURS}h")
            except Exception as e:                  # noqa: BLE001
                log(f"prune failed: {e}")
            next_prune = now + PRUNE_SECONDS
        time.sleep(max(0.5, min(next_sample, next_publish, next_remote, next_prune)
                       - time.time()))


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sample-once", action="store_true", help="one sample to stdout")
    g.add_argument("--distil", action="store_true", help="rebuild telemetry.json only")
    g.add_argument("--publish-once", action="store_true", help="distil + push, then exit")
    g.add_argument("--daemon", action="store_true", help="sample and publish forever")
    a = ap.parse_args()
    if a.sample_once:
        print(json.dumps(sample(), indent=2, sort_keys=True))
        return 0
    if a.distil:
        obj = distil(read_rows(), gpu=gpu_name())
        write_json(obj)
        print(f"{JSON_PATH} — {len(obj['t'])} bucket(s), last sample {obj['last_sample']}")
        return 0
    if a.publish_once:
        obj = distil(read_rows(), gpu=gpu_name())
        commit = publish(obj)
        print(f"{'pushed ' + commit if commit else 'NOT pushed'} "
              f"— {len(obj['t'])} bucket(s) in {JSON_PATH}")
        return 0 if commit else 1
    return daemon()


if __name__ == "__main__":
    sys.exit(main())
