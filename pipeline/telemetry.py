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
- **its own git repo**, `C:\banyan-farm\telemetry-git`: a blobless partial clone
  that never checks anything out. The farm worker owns the working tree of
  `C:\banyan-farm\banyan-city` and switches ITS branch as it heartbeats — a
  second process doing git work in that tree is the 2026-07-31 two-workers bug
  with a different hat. So we build the commit with plumbing (ls-tree → mktree
  --missing → commit-tree) and push only that one commit. Nothing is ever
  checked out and no blob is ever read.

- **ONE BRANCH PER WRITER.** This publishes to `farm-telemetry-rtx5090`, and
  nothing else on earth writes there. Until 2026-08-11 it shared
  `farm-results-rtx5090` with the courier, and the two fought over it:
  `Courier.mark()` in farm_worker.py force-pushes from a tree that has no
  telemetry.json, so every heartbeat DROPPED this file off the branch, and this
  daemon watched the tip and re-published within the minute — each republish a
  chance for the courier's next push to lose the race. On the night of
  2026-08-10 the courier lost ~10 force-push races in a row that way and render
  claims stalled ~20 minutes. Splitting the branches removes the contention at
  its source rather than tuning the retry: the courier keeps
  farm-results-rtx5090 exclusively, telemetry owns farm-telemetry-rtx5090
  exclusively, and neither can clobber the other. The tip of this branch moves
  only when this script moves it, so there is no tip-watching loop any more —
  just the five-minute pulse. The branch also stays at exactly two commits: a
  root commit and one current one, replaced in place (see `publish`).

  Readers (`build_sim.py`, `build_pulse.py`, `pulse_series.py`) read the new
  branch and fall back to the old location when it is absent, so the status page
  survives the transition. A missing or stale file still reads as "no recent
  telemetry" and the page says so.

- **it carries the QUEUE as well as the vitals, since 2026-08-13.** Roman: "why
  is the banyan.city/status only updating when i freaking remind you about it??"
  The queue numbers on the status page came from `pipeline/measured/box-queue.yaml`,
  a file only a supervisor session ever rewrote — so the page was fresh exactly as
  often as someone remembered to nag, and the depth it printed was however many
  hours old that was. The box knows its own queue every second of the day and was
  already publishing to a branch on a five-minute pulse; the fix is to put the
  numbers in the pulse and let the reader's own browser fetch them
  (`build_sim.LIVE_JS`). Freshness then costs no Claude, no commit and no deploy.

  The queue block is OPTIONAL and every reader must survive its absence: an old
  published file has none, and a box whose queue directory has gone missing
  publishes vitals with `queue.error` set rather than dropping the pulse. It is
  sampled at publish time only (once per five minutes, not once per ten seconds)
  because it is a statement of current state, not a series — nothing about it
  belongs in the CSV.

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
    telemetry.py --publish-once  distil, then push to the telemetry branch, exit
    telemetry.py --daemon        the real thing: sample 10s, publish 5 min, forever
"""

import argparse
import calendar
import ctypes
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import repo_slug  # noqa: E402  one source for "which repo is this"

FARM = Path(os.environ.get("BANYAN_FARM", r"C:\banyan-farm"))
# The box's own on-disk queue — box_runner.py owns it, this only ever LISTS it.
# Same default root the runner uses (box_runner.DEFAULT_ROOT), spelled again
# rather than imported: box_runner lives in the repo checkout the farm worker
# switches branches under, and this file is deliberately importable from
# nothing but the stdlib.
QUEUE_ROOT = Path(os.environ.get("BANYAN_QUEUE", r"C:\banyan-queue"))
CSV_PATH = FARM / "telemetry.csv"
JSON_PATH = FARM / "telemetry.json"
LOG_PATH = FARM / "telemetry.log"
TEL_GIT = FARM / "telemetry-git"
# The key the farm worker already pushes with. Referenced BY PATH only — this
# script never reads, copies or logs its contents.
DEPLOY_KEY = FARM / "farm_deploy_key"
# The repo changed owner on 2026-08-10 and this line used to spell the old one.
# Pushes to a retired owner's path survive only on a GitHub redirect, which one
# accidental repo creation at the old name deletes forever — so the courier
# resolves the remote instead of remembering it. On a fork's box this correctly
# pushes to the fork.
REMOTE = repo_slug.SSH_REMOTE
# TELEMETRY'S OWN BRANCH — see the "one branch per writer" note in the module
# docstring. Anything that reads this must also know the name; the readers are
# build_sim.telemetry_branch(), build_pulse.TELEMETRY_URL and
# pulse_series.TELEMETRY_BRANCH, each with a fallback to the old shared branch.
BRANCH = "farm-telemetry-rtx5090"
LEGACY_BRANCH = "farm-results-rtx5090"   # where this used to publish; readers fall back
PUBLISH_PATH = "telemetry.json"      # path inside BRANCH → the raw URL the page fetches
HOST = "rtx5090"
# How publish() recognises its own commits, so each one replaces the last instead
# of piling up at 288 commits a day.
COMMIT_PREFIX = "telemetry: "

SAMPLE_SECONDS = 10
PUBLISH_SECONDS = 300                # 5 minutes, per the ask
# heartbeats.jsonl is append-only for the life of the queue. We want its LAST
# line; reading the whole file every five minutes is work the box would be doing
# instead of rendering, so we seek to the end and read back this far.
HEARTBEAT_TAIL_BYTES = 65536

# argv fingerprint → kind, and it must stay identical to box_job_minutes.KINDS,
# because the medians the page multiplies these counts by were measured per kind
# BY that script. A kind named here and not there multiplies a live count by a
# median of something else. Copied rather than imported for the stdlib-only rule
# above, and test_pipeline pins the two lists together so the copy cannot drift.
# Order matters: first hit wins, and LTX leads because a motion job also crops
# and publishes.
QUEUE_KINDS = (("ltx_i2v", "ltx"), ("goblin_ipa_beat", "charref"),
               ("render_wave_sample", "still"), ("inpaint_fruit", "inpaint"),
               ("runpod_render", "still"))
# A mix is only worth publishing if it accounts for every queued job (build_sim's
# box_queue_eta rejects one that does not add up). Past this many job files we
# stop opening them and publish counts alone — a queue this deep has bigger news
# in it than its exact composition, and the page's fallback estimate is honest.
QUEUE_KIND_MAX_FILES = 200

# WHERE FINISHED WORK BECOMES VISIBLE OFF THIS BOX. Each job's last step copies
# its output into this directory, and box_runner's Courier commits the whole of
# `farm-out` and pushes it to farm-results-rtx5090 — so a file here is, within a
# push, a file at the same relative path on that branch, which is what makes the
# raw URL on the status page resolvable.
#
# THE DIRECTORY IS THE ONLY HONEST SOURCE FOR THAT PATH. A job's `artifacts` list
# records where the render WROTE the file (C:\banyan-farm\<job>\...), not where it
# was published, and the publish step's destination is a string inside an inline
# python step — on 2026-08-13 the task `ep2-b15-seedC-0813` published into
# `ep2-b15-seedB` and `ep2-b04-balloon-pair-0813` into `ep2-b04-balloon-pair`, so
# deriving the path from the task name would have produced confident 404s. We
# list what is actually there instead.
COURIER_OUT = FARM / "courier-box" / "farm-out"
COURIER_BRANCH = "farm-results-rtx5090"   # where COURIER_OUT lands; box_runner owns it
RESULTS_MAX = 8                  # newest media files published on the page
RESULTS_WALK_CAP = 6000          # stop walking rather than stat a runaway tree
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif")
VIDEO_EXTS = (".mp4", ".webm", ".mov")
# How far apart a clip and the still it is postered with may sit. `shutil.copy2`
# preserves the SOURCE mtime, so the two do NOT land together: the init frame is
# stamped before the render began and the clip after it ended, which across the
# box's own published rounds on 2026-08-13 measured 5.3 - 6.4 min for a normal
# take and 44 min for a slow one. The first cut of this allowed 5 min and paired
# nothing at all. Two hours clears every observed pairing while still refusing an
# image from a directory reused a day later.
POSTER_PAIR_OLDER = 7200
# The other direction is tight: a still published well AFTER the clip belongs to
# a later take, not this one.
POSTER_PAIR_NEWER = 300

# How deep the queue has been, one point per publish, for the status page's
# sparkline. KEPT ON DISK, not in memory: this daemon is restarted by hand
# whenever telemetry.py changes — four times on the afternoon this was written —
# and a series held in a process variable would lose its whole day every time,
# which for a 24-hour chart means it is almost never telling the truth.
QUEUE_DEPTH_CSV = FARM / "queue-depth.csv"
DEPTH_WINDOW_HOURS = 24
DEPTH_MAX_POINTS = 288           # 24h at one publish per 5 min
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


class _SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [("ACLineStatus", ctypes.c_ubyte), ("BatteryFlag", ctypes.c_ubyte),
                ("BatteryLifePercent", ctypes.c_ubyte), ("SystemStatusFlag", ctypes.c_ubyte),
                ("BatteryLifeTime", ctypes.c_ulong), ("BatteryFullLifeTime", ctypes.c_ulong)]


def power_sample() -> dict:
    """Mains or battery, and how much of the battery is left.

    This is a laptop with a 5090 in it and it renders on battery when someone has
    unplugged it, at a fraction of the speed — on 2026-08-13 the queue was draining
    slowly for exactly that reason and nothing outside the room could see why. A
    depth estimate is built from medians measured on mains, so "on battery" is the
    single most useful piece of context the page can carry next to it.

    `GetSystemPowerStatus`, not `Win32_Battery`: the WMI class needs a subprocess
    running wmic or powershell (both slower than everything else in this file put
    together, and wmic is deprecated out of current Windows), where this is one
    kernel32 call through ctypes and stays inside the stdlib rule.

    Every field has an explicit "unknown" encoding in the API and each one maps to
    None here — a desktop with no battery reports 255/unknown, and a page that
    read that as 0% would announce a flat battery on a machine that has none.
    """
    out = {"ac": None, "battery_pct": None, "battery_minutes": None}
    if os.name != "nt":
        return out
    try:
        st = _SYSTEM_POWER_STATUS()
        if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(st)):
            return out
    except (AttributeError, OSError) as e:
        log(f"GetSystemPowerStatus unavailable: {e}")
        return out
    if st.ACLineStatus in (0, 1):                     # 255 == the driver does not know
        out["ac"] = bool(st.ACLineStatus)
    if st.BatteryLifePercent <= 100:                  # 255 == unknown
        out["battery_pct"] = int(st.BatteryLifePercent)
    if st.BatteryLifeTime != 0xFFFFFFFF:              # -1 == unknown / on mains
        out["battery_minutes"] = int(st.BatteryLifeTime // 60)
    return out


# ---------------------------------------------------------------- the box's queue

def _iso_to_unix(s):
    """'2026-08-13T09:12:00Z' → unix seconds, or None.

    `calendar.timegm`, never `time.mktime`: box_runner writes these stamps in UTC
    and mktime would read them as box-local, which on this machine is four hours
    out and would have every heartbeat arriving from the future.
    """
    try:
        return calendar.timegm(time.strptime(str(s).strip(), "%Y-%m-%dT%H:%M:%SZ"))
    except (ValueError, TypeError):
        return None


def _mtime(path):
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def last_heartbeat(path: Path):
    """(event, unix_ts) off the last usable line of heartbeats.jsonl, else (None, None).

    Read backwards from the end and tolerant of two kinds of junk, both of which
    are normal rather than exceptional: the first line in the window is usually a
    fragment, because the seek lands mid-line, and the last line can be a torn
    write, because the runner is appending to this file while we read it. Neither
    is worth a log line, let alone an exception.
    """
    try:
        size = path.stat().st_size
        with path.open("rb") as fh:
            if size > HEARTBEAT_TAIL_BYTES:
                fh.seek(size - HEARTBEAT_TAIL_BYTES)
            chunk = fh.read()
    except OSError:
        return None, None
    for line in reversed(chunk.decode("utf-8", "replace").splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict):
            return (str(rec.get("event") or "") or None), _iso_to_unix(rec.get("ts"))
    return None, None


def job_kind(spec: dict) -> str:
    """One word for what a queued job IS, off the scripts its steps actually run.

    Read from argv, never from the job id: ids are written by whoever filed the
    job and drift into nicknames, while the argv is what will run. Same rule and
    same table as box_job_minutes.job_kind, which is where the per-kind medians
    this feeds come from.
    """
    try:
        blob = " ".join(" ".join(s.get("argv") or []) for s in spec.get("steps") or [])
    except (AttributeError, TypeError):
        return "other"
    for needle, kind in QUEUE_KINDS:
        if needle in blob:
            return kind
    return "other"


def queue_kinds(root: Path, files: list) -> dict:
    """{kind: count} over the given (subdir, name) job files, or {} if it cannot
    be made complete.

    All-or-nothing on purpose. The page multiplies each kind by its own median
    and falls back to a rough figure when the mix does not account for every
    queued job, so a PARTIAL mix is worse than none: it would silently price a
    queue as though the jobs it failed to read were not in it.
    """
    if len(files) > QUEUE_KIND_MAX_FILES:
        return {}
    out = {}
    for sub, name in files:
        try:
            with (root / sub / name).open(encoding="utf-8", errors="replace") as fh:
                spec = json.load(fh)
        except (OSError, ValueError):
            return {}          # a job we could not read — the mix is incomplete
        if not isinstance(spec, dict):
            return {}
        k = job_kind(spec)
        out[k] = out.get(k, 0) + 1
    return out


def results_sample(out: Path = None, now: float = None, limit: int = RESULTS_MAX) -> dict:
    """The newest finished work the box has actually PUBLISHED, or {}.

    Roman, 2026-08-13: "you should make it so you can see exactly what is being
    generated on the status page and see the images when its generated."

    Each item's `path` is relative to the repo root, so the page renders it as
    https://raw.githubusercontent.com/<slug>/<COURIER_BRANCH>/<path> and needs no
    knowledge of the box's disk layout.

    WHAT IT DELIBERATELY DOES NOT CLAIM. A file being here means the render
    finished and the publish step copied it; it does NOT mean the courier has
    pushed yet. There is no cheap way to ask that from this process — reading git
    state in the courier's own worktree is the 2026-07-31 two-workers bug wearing
    a hat, and this daemon does not touch that tree. So the page is told when each
    file appeared and left to say "once the box pushes" in words, and the browser
    finds out the real answer the only way that is actually authoritative: the
    image either loads from the branch or it does not.

    `box/` is skipped. That is where the courier drops each job's json and log
    tail — text, already on the branch, and not what "see the images" means.
    """
    out = Path(out) if out else COURIER_OUT
    now = now if now is not None else time.time()
    if not out.is_dir():
        return {"at": int(now), "error": "nothing has been published on this box yet"}
    seen, files = 0, []
    try:
        for d in out.iterdir():
            if not d.is_dir() or d.name == "box":
                continue
            for p in d.rglob("*"):
                seen += 1
                if seen > RESULTS_WALK_CAP:
                    break
                ext = p.suffix.lower()
                if ext not in IMAGE_EXTS and ext not in VIDEO_EXTS:
                    continue
                try:
                    st = p.stat()
                except OSError:
                    continue
                if not st.st_size:
                    continue          # a copy caught half-done is not a result
                files.append((st.st_mtime, st.st_size, p, ext))
            if seen > RESULTS_WALK_CAP:
                break
    except OSError as e:
        return {"at": int(now), "error": "the published directory could not be read: %s" % e}
    files.sort(key=lambda f: f[0], reverse=True)

    # A motion take is an mp4 next to the still it was grown from. Pairing them
    # means the dropdown shows a PICTURE for a video the reader has not asked to
    # download yet, instead of a black rectangle — the whole point being to see
    # the thing without pulling 40 MB per beat.
    posters = {}
    for mtime, _size, p, ext in files:
        if ext in IMAGE_EXTS:
            posters.setdefault(str(p.parent), (p, mtime))

    # Take more candidates than we need: a still that ends up postering the clip
    # above it is dropped from the strip below, and the freed slot should go to
    # the next real result rather than shortening the row.
    items = []
    for mtime, size, p, ext in files[:limit * 3]:
        rel = p.relative_to(out.parent).as_posix()      # courier-box/farm-out/x → farm-out/x
        item = {"path": rel, "name": p.name, "at": int(mtime), "bytes": int(size),
                "kind": "video" if ext in VIDEO_EXTS else "image"}
        if item["kind"] == "video":
            pair = posters.get(str(p.parent))
            # Published in the SAME step as the clip, not merely in the same
            # folder. These directories get reused between runs, so "the newest
            # image in here" can be a leftover from a previous take — and a
            # poster is read as a frame OF the video under it. One publish step
            # copies both within a second or two; POSTER_PAIR_SECONDS is loose
            # enough for a slow copy and far tighter than a stale round.
            if (pair is not None and pair[0] != p
                    and -POSTER_PAIR_NEWER <= (mtime - pair[1]) <= POSTER_PAIR_OLDER):
                item["poster"] = pair[0].relative_to(out.parent).as_posix()
        items.append(item)

    # A still that is already the poster of a clip in this list is not also its
    # own tile. Without this the strip alternates clip, its own poster, clip, its
    # own poster — eight tiles showing four things, and on 2026-08-13 the four
    # beats of one wave all seeded from a single register-pose crop, so the row
    # read as the same picture over and over.
    used = {i["poster"] for i in items if i.get("poster")}
    items = [i for i in items if not (i["kind"] == "image" and i["path"] in used)]
    return {"at": int(now), "branch": COURIER_BRANCH, "items": items[:limit]}


def depth_history(q: dict, now: float = None, record: bool = False,
                  path: Path = None) -> list:
    """[[epoch, ready+running], ...] over the last 24h, oldest first — the queue's
    depth over time, for the sparkline on the status page.

    A READING THAT FAILED IS NOT A DEPTH OF ZERO, and this is the one place the
    distinction is easy to lose: a chart interpolates, so a single 0 written
    while the queue directory was unreadable draws a clean dip to empty across an
    outage — a picture of an idle box, which is the exact claim the rest of this
    file is arranged to never make. Nothing is appended unless the sample
    actually carries counts, and the gap is left as a gap.

    Kept in its own tiny CSV rather than in memory (see QUEUE_DEPTH_CSV): the
    daemon is restarted by hand every time this file changes.
    """
    path = path or QUEUE_DEPTH_CSV
    now = now if now is not None else time.time()
    rows = []
    try:
        if path.exists():
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                parts = line.strip().split(",")
                if len(parts) != 2:
                    continue
                try:
                    rows.append((int(float(parts[0])), int(float(parts[1]))))
                except ValueError:
                    continue          # a row torn by a kill mid-write
    except OSError as e:
        log(f"queue depth history unreadable: {e}")
        return []

    if record and ("ready" in q or "running" in q) and not q.get("error"):
        rows.append((int(now), int(q.get("ready") or 0) + int(q.get("running") or 0)))

    rows.sort()
    cut = now - DEPTH_WINDOW_HOURS * 3600
    rows = [r for r in rows if r[0] >= cut][-DEPTH_MAX_POINTS:]

    if record:
        try:
            tmp = path.with_suffix(".csv.tmp")
            tmp.write_text("".join(f"{t},{d}\n" for t, d in rows), encoding="utf-8")
            os.replace(tmp, path)     # never leave a half-written history behind
        except OSError as e:
            log(f"could not write queue depth history: {e}")
    return [[t, d] for t, d in rows]


def queue_block(now: float = None, record: bool = True) -> dict:
    """The queue reading as it goes out on the wire, history attached.

    `record` is False for the read-only modes — `--distil` rebuilds the published
    file from what is already on disk and must not be able to stamp extra points
    into the history by being run twice.
    """
    q = queue_sample(now=now)
    series = depth_history(q, now=now, record=record)
    if series:
        q["depth_series"] = series
    return q


def current_job(root: Path, jid: str) -> dict:
    """What the card is making right now, off the running job's own record.

    Only the fields a stranger can read something from: what beat of what node it
    belongs to, when it started, and the names of the files it is going to
    produce. Not argv, not env, not paths on someone's D: drive — the same
    stranger-eyes rule the machine list already follows (2026-07-30).
    """
    out = {}
    try:
        with (root / "running" / (jid + ".json")).open(encoding="utf-8",
                                                       errors="replace") as fh:
            spec = json.load(fh)
    except (OSError, ValueError):
        return out
    if not isinstance(spec, dict):
        return out
    for key in ("task", "node", "beat"):
        v = spec.get(key)
        if v not in (None, ""):
            out[key] = v
    at = _iso_to_unix(spec.get("started_at"))
    if at:
        out["started_at"] = at
    try:
        attempts = int(spec.get("attempts") or 0)
        if attempts > 1:
            out["attempt"] = attempts       # only worth saying when it is a retry
    except (TypeError, ValueError):
        pass
    # Split on BOTH separators by hand. os.path.basename follows the separator of
    # the machine it runs on, so a job's `C:\banyan-farm\...\05-the-patrol.mp4`
    # comes back whole off a posix box — and this string goes on a public page,
    # where a filename is the point and somebody's directory tree is not.
    makes = [str(a).replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]
             for a in (spec.get("artifacts") or [])[:4]]
    makes = [m for m in makes if m]
    if makes:
        out["makes"] = makes
    out["kind"] = job_kind(spec)
    return out


def queue_sample(root: Path = None, now: float = None) -> dict:
    """What the box's own queue looks like right now. Never raises.

    STRICTLY READ-ONLY, like everything else in this file: four `listdir`s, a few
    `stat`s and a tail read. It claims nothing, locks nothing and creates nothing
    — note that it does NOT `makedirs` the subdirectories the way box_runner does,
    because a missing `ready/` is a fact worth publishing and not one to quietly
    repair from a process that does not own the queue.

    The counts are a sample of a directory that another process is renaming files
    within, so `ready` and `running` can disagree by one job with each other and
    with the truth: a job caught mid-claim is in neither listing, or in both. That
    is a one-job error on a number the page prints as an estimate anyway, and the
    alternative — taking the runner's lock to read consistently — would be this
    daemon reaching into a render's critical path, which is the one thing it must
    never do.

    `error` is set and the counts left absent when the queue root is unreadable.
    Absent, not zero: "0 waiting" is what an idle box looks like, and publishing
    that because a directory vanished is the whole class of failure the status
    page is built to avoid.
    """
    root = Path(root) if root else QUEUE_ROOT
    now = now if now is not None else time.time()
    q = {"at": int(now), "root": str(root)}
    if not root.is_dir():
        q["error"] = "the queue directory is not there"
        return q

    def listing(sub):
        try:
            return [n for n in os.listdir(root / sub) if n.endswith(".json")]
        except OSError:
            return None

    ready, running = listing("ready"), listing("running")
    done, failed = listing("done"), listing("failed")
    if ready is None and running is None and done is None and failed is None:
        q["error"] = "the queue directory could not be listed"
        return q
    if ready is not None:
        q["ready"] = len(ready)
    if failed is not None:
        q["failed"] = len(failed)
    if running is not None:
        q["running"] = len(running)
        if running:
            # One at a time by construction (box_runner is sequential), so the
            # first is the one. The id is the job filename without .json — the
            # same id the courier's sidecars and the heartbeats carry.
            jid = sorted(running)[0][:-5]
            q["running_job"] = jid
            # THE LIVENESS SIGNAL. A job sitting in running/ says only that
            # something claimed it; the log's last write says the render is still
            # producing. A running job whose log has been silent for an hour is
            # the shape of the stall this box has had before, and it is invisible
            # to any count of files.
            age = _mtime(root / "running" / (jid + ".log"))
            q["running_log_age_sec"] = max(0, int(now - age)) if age else None
            # The detail behind the dropdown. running_job and running_log_age_sec
            # stay exactly where they are: a page built before this deploy reads
            # those two and nothing else, and it goes on working through the
            # window where the new daemon is publishing to the old page.
            cur = current_job(root, jid)
            if cur:
                q["current"] = cur
    if ready is not None and running is not None:
        # WHAT is queued, not just how much — the page prices a motion take at
        # five minutes and a still at one, so the mix is the difference between
        # an estimate and a guess. Running jobs are counted whole, the same
        # upward bias box-queue.yaml's header owns up to.
        mix = queue_kinds(root, [("ready", n) for n in ready]
                          + [("running", n) for n in running])
        if mix and sum(mix.values()) == len(ready) + len(running):
            q["kinds"] = mix
    if done is not None:
        # Two windows on purpose. `done_today` is what a person means and it is
        # measured against the BOX's local midnight, so it inherits whatever the
        # box's clock believes; `done_24h` is a difference between two readings
        # of that same clock and so survives it being wrong. The page prefers the
        # rolling one for that reason.
        lt = time.localtime(now)
        midnight = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, 0, 0, 0, 0, 0, -1))
        today = day = 0
        for name in done:
            m = _mtime(root / "done" / name)
            if m is None:
                continue
            if m >= midnight:
                today += 1
            if m >= now - 86400:
                day += 1
        q["done_today"], q["done_24h"] = today, day

    event, at = last_heartbeat(root / "heartbeats.jsonl")
    if event:
        q["last_event"] = event
    if at:
        q["last_event_at"] = at

    q["runner_alive"] = runner_alive(root)
    return q


def boot_id() -> int:
    """Epoch second this OS booted, to ~10s. 0 where we cannot tell.

    box_runner.boot_id, reimplemented here rather than imported for the same
    stdlib-only reason as QUEUE_KINDS.
    """
    if os.name == "nt":
        try:
            ticks = ctypes.windll.kernel32.GetTickCount64()
        except (AttributeError, OSError):
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


def runner_alive(root: Path):
    """Is anything actually draining this queue? True / False / None for unknown.

    A queue with jobs in it and no live runner is the difference between "busy"
    and "abandoned", and the counts alone read identically in both cases — which
    is the whole reason this field exists.

    THE LOCK IS NOT A BARE PID and reading it as one is how the first version of
    this got `null` off a perfectly healthy box: box_runner writes
    `<pid> <utc> boot=<epoch>` (box_runner.read_lock), so `int()` over the whole
    file raises and the honest-looking `except ValueError` reported "unknown"
    about a runner that was rendering at the time.

    The boot check comes FIRST, exactly as box_runner.lock_is_live orders it.
    Windows recycles pids, the runner starts seconds after boot on a machine that
    just freed thousands of them, and asking the OS whether a pid is alive is the
    question that gets a confidently wrong answer after a reboot.
    """
    try:
        fields = (root / "runner.lock").read_text(encoding="utf-8",
                                                  errors="replace").split()
    except OSError:
        return None                      # no lock file: nobody has ever run here
    try:
        pid = int(fields[0])
    except (IndexError, ValueError):
        return None
    boot = 0
    for f in fields[1:]:
        if f.startswith("boot="):
            try:
                boot = int(f[5:])
            except ValueError:
                boot = 0
    mine = boot_id()
    if boot and mine and abs(boot - mine) > 120:
        return False                     # written before this boot: a stale lock
    return process_state(pid) if pid else None


# OpenProcess failure modes worth telling apart. "No process with that id" is a
# fact; "you may not ask about that process" is not an answer at all.
ERROR_ACCESS_DENIED = 5
ERROR_INVALID_PARAMETER = 87
STILL_ACTIVE = 259


def process_state(pid: int):
    """True alive / False gone / None could not tell.

    SEPARATE FROM pid_alive() ON PURPOSE, and the difference is the whole point.
    pid_alive answers a two-way question for the sampler lock, where "I could not
    query it" must resolve to "not alive" so a sampler always starts. Here the
    same collapse would put "NOTHING IS DRAINING THE QUEUE" on a public page
    because one OpenProcess came back denied — and on 2026-08-13 the published
    reading said the runner was dead while box_runner was three minutes into an
    LTX take and an interactive probe of the same pid, on the same box, said it
    was fine. Only ERROR_INVALID_PARAMETER actually means the pid is gone;
    everything else is this process's ignorance and is published as such, so the
    page stays quiet instead of raising a false alarm.
    """
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True                  # it exists; it is simply not ours
        except OSError:
            return None
    try:
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        h = k32.OpenProcess(0x1000, False, pid)      # QUERY_LIMITED_INFORMATION
        if not h:
            return False if ctypes.get_last_error() == ERROR_INVALID_PARAMETER else None
        code = ctypes.c_ulong()
        ok = k32.GetExitCodeProcess(h, ctypes.byref(code))
        k32.CloseHandle(h)
        return (code.value == STILL_ACTIVE) if ok else None
    except (AttributeError, OSError):
        return None


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
           bucket_seconds: int = BUCKET_SECONDS, gpu: str = "",
           queue: dict = None, power: dict = None, results: dict = None) -> dict:
    """CSV rows → the compact object the page draws. Pure: no disk, no network.

    `queue` and `power` are HANDED IN, sampled by the caller, for the same reason
    `gpu` is: this function is the one piece of the daemon that can be tested
    against a list of numbers, and it keeps that property only by touching
    nothing. Both are optional and are omitted from the output when absent rather
    than published empty — see queue_sample() on why a missing reading must never
    surface as a zero.

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

    def last_of(key, nd=1):
        for r in reversed(rows):
            if r.get(key) is not None:
                return _r(r[key], nd)
        return None

    out = {
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
    # The newest single readings, beside the series. The page's queue tile wants
    # "what is the card doing right now" and should not have to walk 1,440
    # buckets backwards past the nulls to find out.
    gpu_w, gpu_u = last_of("gpu_power_w"), last_of("gpu_util", 0)
    if gpu_w is not None:
        out["gpu_power_w"] = gpu_w
    if gpu_u is not None:
        out["gpu_util_now"] = int(gpu_u)
    if queue:
        out["queue"] = queue
    if power and any(v is not None for v in power.values()):
        out["power"] = power
    if results:
        out["results"] = results
    return out


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


def rev(r) -> str:
    """A sha from `git rev-parse`, or "" if there wasn't one.

    Never read rev-parse's stdout without this. Handed a name it cannot resolve,
    rev-parse ECHOES THE NAME BACK on stdout and reports the failure only in the
    exit code — so `rev-parse <sha>^` on a root commit yields the literal string
    "<sha>^", which is falsy in no way at all and sails on into the next command.
    That is exactly what happened the first time this file published to a branch
    of its own: the walk-back below asks for the parent of the root commit every
    single cycle, took "<sha>^" for an answer, and every publish after the first
    died in ls-tree. `--verify -q` prints nothing and returns nonzero instead.
    """
    return r.stdout.strip() if r.returncode == 0 else ""


def ensure_repo() -> bool:
    """A blobless, never-checked-out repo whose only job is to put one file on the
    telemetry branch. Blobless is belt-and-braces now that the branch carries
    nothing but telemetry.json, but the remote is still the full repo and a
    careless plumbing slip could ask it for ~960 MB of episode media — the box is
    often mid-download of a model set and telemetry must not compete for the wire.
    The same reason GIT_NO_LAZY_FETCH is pinned in git()."""
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


def remote_tip():
    """Sha of BRANCH on the remote; "" if the branch is not there yet; None if the
    question could not be asked at all.

    Three answers, not two, because "the branch does not exist" is the normal
    first-run state that publish() bootstraps from, and "the network is down" must
    NOT be mistaken for it — a bootstrap builds a parentless commit, and building
    one against a remote we simply failed to reach would throw away the history
    the moment the link came back.
    """
    r = git("ls-remote", "origin", f"refs/heads/{BRANCH}", timeout=120)
    if r.returncode:
        return None
    out = r.stdout.strip()
    return out.split()[0] if out else ""


def publish(obj: dict = None) -> str:
    """Put telemetry.json on BRANCH. Returns the pushed commit sha, or "" if it did
    not land — a failed publish is logged and retried on the next cycle, never
    fatal.

    BRANCH belongs to this script alone, so the tip is whatever we last pushed and
    the branch settles at exactly two commits: a root, and one current commit that
    is replaced in place every cycle. The first run has no branch to build on and
    bootstraps a parentless commit carrying only telemetry.json.
    """
    if obj is None:
        obj = distil(read_rows(), gpu=gpu_name(), queue=queue_block(),
                    power=power_sample(), results=results_sample())
    write_json(obj)
    if not ensure_repo():
        return ""
    tip = remote_tip()
    if tip is None:
        log("could not reach the remote to read the branch tip — retrying next cycle")
        return ""
    base, lease = "", ""
    if not tip:
        log(f"{BRANCH} does not exist on the remote yet — creating it")
    else:
        # depth 6, not 1: enough to walk back over our OWN previous commits to the
        # root. Still blobless, and after the first cycle these trees are already
        # local, so the fetch is bytes.
        r = git("fetch", "--filter=blob:none", "--depth=6", "origin", BRANCH)
        if r.returncode:
            log(f"fetch failed: {(r.stderr or r.stdout).strip()[-300:]}")
            return ""
        tip = rev(git("rev-parse", "--verify", "-q", "FETCH_HEAD"))
        if not tip:
            log("no FETCH_HEAD after fetch")
            return ""
        # REPLACE our last publish, do not stack on it: at one publish per five
        # minutes, stacking is 288 commits a day. Walk back over consecutive
        # commits of our own; on a branch only we write, that walk ends at the root
        # commit, which becomes the permanent base every later publish sits on.
        #
        # The lease is what still makes the force safe even now that we are the
        # only writer: --force-with-lease against the sha we just read can only
        # ever overwrite THAT. Anything else on the tip — a human, a mistake, a
        # second daemon — fails the lease and is left alone, and we retry.
        base, hops = tip, 0
        while hops < 5:
            subj = git("log", "-1", "--format=%s", base).stdout.strip()
            if not subj.startswith(COMMIT_PREFIX):
                break
            parent = rev(git("rev-parse", "--verify", "-q", f"{base}^"))
            if not parent:
                break                   # the root commit: build on it, never past it
            lease, base, hops = tip, parent, hops + 1
    blob = git("hash-object", "-w", "--path", PUBLISH_PATH, str(JSON_PATH)).stdout.strip()
    if not blob:
        log("hash-object failed")
        return ""
    # The tree, built without reading a single blob: list the base's ROOT entries
    # (any subtree stays untouched, by sha), swap in our own telemetry.json, and
    # hand the listing to `mktree --missing` — the one plumbing command that is
    # explicitly allowed to reference objects this repo does not have. No index,
    # no write-tree, no promisor fetch. See git() for what that cost once.
    #
    # `base` is empty only on the bootstrap, where there is no tree to carry
    # forward and the branch starts as this one file.
    lines = []
    if base:
        r = git("ls-tree", base)
        if r.returncode:
            log(f"ls-tree failed: {(r.stderr or '').strip()[-200:]}")
            return ""
        # -z, AND NUL separators on the way in. Not a style choice: subprocess in
        # text mode writes the child's stdin through a TextIOWrapper, which on
        # Windows translates every "\n" to "\r\n" — so a newline-separated listing
        # reached mktree with a trailing CR on every entry and it dutifully built a
        # tree in which each of the 38 root entries was named "CLAUDE.md\r",
        # "genomes\r", "telemetry.json\r". That commit was pushed and then rewound
        # off the branch (2026-08-04). NUL is not a newline, so nothing can
        # translate it.
        lines = [ln.rstrip("\r") for ln in r.stdout.splitlines()
                 if ln.strip() and not ln.rstrip("\r").endswith(f"\t{PUBLISH_PATH}")]
    lines.append(f"100644 blob {blob}\t{PUBLISH_PATH}")
    tree = git("mktree", "-z", "--missing",
               stdin_text="".join(ln + "\0" for ln in lines)).stdout.strip()
    if not tree:
        log("mktree failed")
        return ""
    stamp = time.strftime("%H:%M:%SZ", time.gmtime())
    parent = ["-p", base] if base else []
    commit = git("commit-tree", tree, *parent, "-m",
                 f"{COMMIT_PREFIX}{HOST} {stamp} ({len(obj.get('t', []))} min)").stdout.strip()
    if not commit:
        log("commit-tree failed")
        return ""
    # --no-thin IS LOAD-BEARING IN A PARTIAL CLONE. A thin push deltas the new
    # blob against an object it believes the remote already has — and here the
    # obvious candidate is an OLDER telemetry.json, which in a blobless clone we
    # do not have. pack-objects then tries to lazy-fetch its own delta base,
    # GIT_NO_LAZY_FETCH (see git()) correctly refuses, and the pack stream stops
    # mid-object; the remote reports the truncation as `fatal: early EOF` /
    # `remote unpack failed: index-pack failed`, which reads like a rejected push
    # and is nothing of the kind. That is how the telemetry branch died at
    # 2026-08-21T10:12Z and stayed dead for 25 hours while the daemon sampled,
    # distilled and retried every five minutes, perfectly healthy, into a wall.
    # The payload is one 50 KB json — there is no delta worth having.
    args = ["push", "--no-thin"]
    if lease:
        args.append(f"--force-with-lease=refs/heads/{BRANCH}:{lease}")
    r = git(*(args + ["origin", f"{commit}:refs/heads/{BRANCH}"]))
    if r.returncode:
        # 900, not 300: the 25-hour outage above was diagnosable in one line —
        # `fatal: could not fetch <sha> from promisor remote` — and 300
        # characters of tail cut that line off and left only the remote's
        # confusing `early EOF`. Never truncate a push failure to the part the
        # remote wrote; the local half is where the cause lives.
        log(f"push failed (retrying next cycle): "
            f"{(r.stderr or r.stdout).strip()[-900:]}")
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
    # Publish on a plain interval and nothing else. There used to be a second
    # trigger here — an `ls-remote` every minute that re-published the instant the
    # branch tip moved — because the courier shared this branch and its force-push
    # deleted telemetry.json on every heartbeat. On a branch only this daemon
    # writes, the tip moves only when we move it, so that trigger could fire only
    # on our own push. It is gone with the shared branch.
    next_sample, next_publish = now, now + SAMPLE_SECONDS
    next_prune = now + PRUNE_SECONDS
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
        if now >= next_publish:
            try:
                got = publish(distil(read_rows(), now=now, gpu=gpu,
                                       queue=queue_block(now=now), power=power_sample(),
                                       results=results_sample(now=now)))
                log(f"published {'ok ' + got[:8] if got else 'FAILED (will retry)'}")
            except Exception as e:                  # noqa: BLE001
                log(f"publish failed: {e}")
            next_publish = now + PUBLISH_SECONDS
        if now >= next_prune:
            try:
                dropped = prune(now=now)
                if dropped:
                    log(f"pruned {dropped} row(s) older than {KEEP_HOURS}h")
            except Exception as e:                  # noqa: BLE001
                log(f"prune failed: {e}")
            next_prune = now + PRUNE_SECONDS
        time.sleep(max(0.5, min(next_sample, next_publish, next_prune) - time.time()))


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
        obj = distil(read_rows(), gpu=gpu_name(), queue=queue_block(record=False),
                    power=power_sample(), results=results_sample())
        write_json(obj)
        print(f"{JSON_PATH} — {len(obj['t'])} bucket(s), last sample {obj['last_sample']}")
        return 0
    if a.publish_once:
        obj = distil(read_rows(), gpu=gpu_name(), queue=queue_block(),
                    power=power_sample(), results=results_sample())
        commit = publish(obj)
        print(f"{'pushed ' + commit if commit else 'NOT pushed'} "
              f"— {len(obj['t'])} bucket(s) in {JSON_PATH}")
        return 0 if commit else 1
    return daemon()


if __name__ == "__main__":
    sys.exit(main())
