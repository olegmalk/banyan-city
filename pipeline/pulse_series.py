#!/usr/bin/env python3
"""THE PULSE CACHE — the long view of the farm, kept as a repo fact.

Oleg asked (2026-08-10) for a page showing the work queue and the 5090's bare
resource use *over time*. Two of the three series that answers need already
exist somewhere, and none of them can be read by the thing that builds the
page:

  * GPU / VRAM / RAM        the box publishes `telemetry.json` to its own
                            telemetry branch every five minutes. That file is a
                            rolling 24-hour window and **it is the only copy** —
                            each publish replaces the last, so yesterday is gone
                            the moment today is written. Nothing accumulates
                            unless we accumulate it.
  * queue depth             `pipeline/farm-queue.yaml`'s git history on main is
                            a real time series (151 commits, 12 days), but the
                            deploy server checks out one commit with no refs
                            and no `gh`, so the build cannot walk it.
  * job starts/completions  `farm-out/heartbeat.txt` on each `farm-results-*`
                            branch. The boxes truncate it (the 5090's copy is
                            seven lines), so again the history is in git and
                            only in git.

So this script runs where the refs are — a laptop, or anything with a full
clone — and writes `pipeline/pulse-series.json`, which IS readable by the
build. It is append-only in spirit: every run merges new samples into what is
already cached and never invents a bucket it did not see.

    python3 pipeline/pulse_series.py            # extend the cache
    python3 pipeline/pulse_series.py --dry-run  # print what would change

HOW OFTEN TO RUN IT — a cost decision, not a taste one. The output is committed
to main, main is the one branch allowed to deploy, and the cache is a listed
build input, so **every refresh is one site build**. A five-minute timer on this
is precisely the shape that billed >$100 of build hours in under a month (the
courier heartbeat, SITE.md). It also is not needed: the page carries a live tail
that reads the box and the queue straight from the browser, so "what is it doing
right now" stays true between refreshes and only the *history* ages. A few times
a day is the right cadence — after a render wave, or whenever someone wants the
long view current. Nothing breaks if it is skipped for a day; the box keeps its
own 24 hours and this catches up on the next run, losing only whatever fell out
of that rolling window in between.

WHY A GAP IS A GAP. Every series here is stored on an explicit grid with
`null` for "no sample", never 0. A dead network link and an idle GPU both
produce a flat line at zero on a careless chart, and those are opposite facts —
one means the box is fine and resting, the other means we cannot see it. The
box's own telemetry already uses this convention (`legend.null`), and this file
preserves it through the merge rather than filling anything in.
"""
from __future__ import annotations

import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "pipeline" / "pulse-series.json"

# Telemetry has its own branch as of 2026-08-11 (pipeline/telemetry.py, "one
# branch per writer"): the courier and the telemetry daemon used to force-push the
# same ref and starve each other. LEGACY is where telemetry used to land, and is
# read only when the new branch is not there — the box's scheduled task is
# re-enabled by hand, so there is a window in which the last good sample is still
# only in the old place, and a status page that went blank through it would be
# reporting our deploy sequence as a dead machine.
TELEMETRY_BRANCH = "farm-telemetry-rtx5090"
TELEMETRY_BRANCH_LEGACY = "farm-results-rtx5090"
QUEUE_PATH = "pipeline/farm-queue.yaml"
HEARTBEAT_PATH = "farm-out/heartbeat.txt"

# Five minutes, matching the courier's publish interval: a finer grid would
# store buckets the source cannot distinguish, and a coarser one would blur the
# short bursts that are most of this box's work (a beat renders in ~170s).
BUCKET = 300
# A week. The page shows 48 hours; the extra days are what makes "is this normal
# for a Tuesday" answerable later, and 2016 buckets of six numbers is ~60 KB.
RETAIN_DAYS = 7
# Queue and job events are sparse and small, so they keep the same horizon as
# the grid rather than one of their own — one window, one story.
EVENT_RETAIN_DAYS = RETAIN_DAYS

SCHEMA = 1


def git(*args: str, ref_ok: bool = True) -> str:
    """Run git in the repo and return stdout, or "" if the command failed.

    Failures are normal here and are not errors: a branch may not be fetched,
    a path may not exist at an old commit. The caller decides what a missing
    answer means; this function refuses to guess by raising.
    """
    # errors="replace" and not a raise: half of these blobs were written on the
    # Windows box, and a stray cp1252 byte in one heartbeat line must cost that
    # line and not the whole series.
    p = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.stdout if p.returncode == 0 else ""


def fetch_branches() -> list[str]:
    """Update the branches we read, and report which COURIER ones we have.

    Both families are fetched — the couriers carry the heartbeats, the telemetry
    branch carries the vitals — but only the courier branches are returned: the
    list feeds collect_jobs() and the `jobs.branches` provenance line, and a
    telemetry branch listed there would advertise a machine whose heartbeat log
    does not exist.

    Best-effort on purpose. Running this offline should extend the cache with
    whatever the local clone already knows rather than failing outright, which
    is why the fetch result is not checked and the branch list is read back
    from the refs afterwards.
    """
    subprocess.run(["git", "fetch", "--quiet", "origin",
                    "+refs/heads/farm-results-*:refs/remotes/origin/farm-results-*",
                    "+refs/heads/farm-telemetry-*:refs/remotes/origin/farm-telemetry-*"],
                   cwd=REPO, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
    out = git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/farm-results-*")
    return [l.strip() for l in out.splitlines() if l.strip()]


# ---- the grid -----------------------------------------------------------------

def bucket_of(ts: int) -> int:
    return (int(ts) // BUCKET) * BUCKET


def read_telemetry(ref: str) -> dict | None:
    """The box's own 24-hour summary, straight off one branch."""
    raw = git("show", f"{ref}:telemetry.json")
    if not raw.strip():
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def read_telemetry_anywhere() -> tuple[dict | None, str]:
    """(summary, the ref it came from) — new branch first, old branch as a fallback.

    Returns the ref so the caller can record WHICH copy it read. During the
    branch split the two can both exist and disagree, and the older one being
    quietly averaged into the cache as though it were fresh is exactly the kind
    of silent staleness the rest of this file works to prevent.
    """
    for branch in (TELEMETRY_BRANCH, TELEMETRY_BRANCH_LEGACY):
        ref = f"origin/{branch}"
        tel = read_telemetry(ref)
        if tel:
            return tel, ref
    return None, f"origin/{TELEMETRY_BRANCH}"


def downsample(tel: dict) -> dict[int, dict]:
    """The box's 1-minute buckets → our 5-minute grid.

    Means are averaged over the minutes that actually carried a sample and
    peaks are maxed, because those are the only reductions that survive being
    done twice: re-running this over an overlapping window must not move a
    number that is already cached. A five-minute slot with no minute in it is
    absent from the returned dict, not zero — see the module docstring.
    """
    t = tel.get("t") or []
    out: dict[int, dict] = {}
    series = {k: (tel.get(k) or []) for k in ("u", "up", "v", "r", "c")}
    for i, ts in enumerate(t):
        b = bucket_of(ts)
        slot = out.setdefault(b, {"u": [], "up": [], "v": [], "r": [], "c": []})
        for k, arr in series.items():
            if i < len(arr) and arr[i] is not None:
                slot[k].append(arr[i])
    reduced = {}
    for b, slot in out.items():
        if not any(slot.values()):
            continue          # every minute in this slot was a null
        reduced[b] = {
            "u": round(sum(slot["u"]) / len(slot["u"]), 1) if slot["u"] else None,
            "up": max(slot["up"]) if slot["up"] else None,
            "v": round(sum(slot["v"]) / len(slot["v"]), 2) if slot["v"] else None,
            "r": round(sum(slot["r"]) / len(slot["r"]), 2) if slot["r"] else None,
            "c": round(sum(slot["c"]) / len(slot["c"]), 2) if slot["c"] else None,
        }
    return reduced


def merge_grid(old: dict, new_buckets: dict[int, dict], now: int) -> dict:
    """Fold fresh buckets into the cached grid and drop what fell off the back.

    NEWEST WINS on a collision. The overlap is a bucket the box has now seen
    more of — the previous run may have caught it half-finished, one minute
    into five — so the later reading is the more complete one, and both are
    honest readings of the same slot.
    """
    t0 = old.get("t0")
    cols = {k: list(old.get(k) or []) for k in ("u", "up", "v", "r", "c")}
    have: dict[int, dict] = {}
    if t0 is not None:
        n = max((len(v) for v in cols.values()), default=0)
        for i in range(n):
            b = t0 + i * BUCKET
            row = {k: (cols[k][i] if i < len(cols[k]) else None) for k in cols}
            if any(v is not None for v in row.values()):
                have[b] = row
    have.update(new_buckets)

    floor = bucket_of(now - RETAIN_DAYS * 86400)
    have = {b: r for b, r in have.items() if b >= floor}
    if not have:
        return {"t0": None, "bucket_seconds": BUCKET, "u": [], "up": [], "v": [], "r": [], "c": []}

    lo, hi = min(have), max(have)
    grid = {"t0": lo, "bucket_seconds": BUCKET}
    span = (hi - lo) // BUCKET + 1
    for k in ("u", "up", "v", "r", "c"):
        grid[k] = [have.get(lo + i * BUCKET, {}).get(k) for i in range(span)]
    return grid


# ---- the queue ----------------------------------------------------------------

ID_RE = re.compile(r"^-\s+id:\s*(\S+)", re.M)


def count_entries(text: str) -> tuple[int | None, int | None]:
    """`tasks:` and `backlog:` lengths from one revision of the queue file.

    Deliberately a line scanner and not a YAML load. This walks 150 historical
    revisions, several of which predate the current entry shape, and a parser
    that raises on an old file would silently punch a hole in the series at
    exactly the interesting moments. It is also the same reading the live page
    already does in the browser (build_sim's `queueIds`), so the cached history
    and the live tail cannot disagree about what a queue entry is.
    """
    sec = None
    n = {"tasks": 0, "backlog": 0}
    seen = set()
    for line in text.splitlines():
        if re.match(r"^tasks:\s*$", line):
            sec = "tasks"
            seen.add(sec)
            continue
        if re.match(r"^backlog:\s*$", line):
            sec = "backlog"
            seen.add(sec)
            continue
        if re.match(r"^[A-Za-z_][\w-]*:", line):
            sec = None
            continue
        if sec and re.match(r"^-\s+id:\s*\S+", line):
            n[sec] += 1
    return (n["tasks"] if "tasks" in seen else None,
            n["backlog"] if "backlog" in seen else None)


def collect_queue(since: int) -> list[list]:
    """[[unix, runnable, planned], …] — one sample per commit that touched it.

    Commit times, so the samples are irregular by nature: the queue only has a
    depth when someone writes one down. The page draws it as a step function
    for that reason and says so.
    """
    log = git("log", "--format=%H|%at", "main", "--", QUEUE_PATH)
    rows = []
    for line in log.splitlines():
        if "|" not in line:
            continue
        sha, ts = line.split("|", 1)
        ts = int(ts)
        if ts < since:
            continue
        blob = git("show", f"{sha}:{QUEUE_PATH}")
        if not blob:
            continue
        tasks, backlog = count_entries(blob)
        if tasks is None and backlog is None:
            continue
        # null, not 0, for a list this revision did not have. `backlog:` was
        # only introduced on 2026-08-08; writing its absence as zero drew four
        # flat days of "nothing was planned" across a week when planning was
        # simply kept somewhere else, which is the same lie as filling a
        # telemetry gap with an idle GPU.
        rows.append([ts, tasks, backlog])
    rows.sort()
    return rows


# ---- jobs ---------------------------------------------------------------------

EVENT_RE = re.compile(r"^(\d{2}):(\d{2}):(\d{2})Z\s+(STARTED|DONE|FAIL)\s+task=(\S+)")


def stamp(hh: int, mm: int, ss: int, commit_ts: int) -> int:
    """Give a heartbeat line a date.

    The boxes write `HH:MM:SSZ` and no day, so the only date available is the
    commit that carried the line — which lands within a courier interval of the
    event. Of the three candidate days the nearest one that is not in the
    future relative to its own commit wins; a line cannot have been published
    before it was written, and that single constraint resolves the midnight
    rollover that would otherwise throw a night's work onto the wrong day.
    """
    day = datetime.datetime.fromtimestamp(commit_ts, datetime.timezone.utc).date()
    best = None
    for delta in (-1, 0, 1):
        d = day + datetime.timedelta(days=delta)
        cand = int(datetime.datetime(d.year, d.month, d.day, hh, mm, ss,
                                     tzinfo=datetime.timezone.utc).timestamp())
        if cand > commit_ts + 120:
            continue
        if best is None or abs(cand - commit_ts) < abs(best - commit_ts):
            best = cand
    return best if best is not None else commit_ts


def collect_jobs(branches: list[str], since: int) -> list[list]:
    """[[unix, kind, machine, task_id], …] from every machine's check-in log.

    The logs are truncated on the boxes, so the history is reconstructed by
    walking each branch's commits oldest-first and taking the lines a commit
    added. Exact-string dedup per branch: a box that rewrites its file keeps
    its old lines out of the series a second time, and the same line genuinely
    repeated (a task re-run at the same wall-clock second) is a collision this
    accepts rather than double-count a truncation.
    """
    events: list[list] = []
    for ref in branches:
        machine = ref.split("farm-results-")[-1]
        log = git("log", "--reverse", "--format=%H|%at", ref, "--", HEARTBEAT_PATH)
        seen: set[str] = set()
        for line in log.splitlines():
            if "|" not in line:
                continue
            sha, cts = line.split("|", 1)
            cts = int(cts)
            blob = git("show", f"{sha}:{HEARTBEAT_PATH}")
            for row in blob.splitlines():
                row = row.strip()
                if not row or row in seen:
                    continue
                seen.add(row)
                m = EVENT_RE.match(row)
                if not m:
                    continue
                hh, mm, ss, kind, task = m.groups()
                ts = stamp(int(hh), int(mm), int(ss), cts)
                if ts < since:
                    continue
                events.append([ts, kind.lower(), machine, task])
    events.sort()
    return events


# ---- assembly -----------------------------------------------------------------

def build(dry_run: bool = False) -> dict:
    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    since = now - EVENT_RETAIN_DAYS * 86400

    try:
        old = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    except json.JSONDecodeError:
        old = {}

    branches = fetch_branches()
    tel, tel_ref = read_telemetry_anywhere()

    gpu = dict(old.get("gpu") or {})
    if tel:
        gpu.update({
            "host": tel.get("host"),
            "gpu_name": tel.get("gpu_name"),
            "vram_total_gb": tel.get("vram_total_gb"),
            "ram_total_gb": tel.get("ram_total_gb"),
            "last_sample": tel.get("last_sample"),
            "source_generated": tel.get("generated"),
            "source_ref": tel_ref,
        })
        gpu.update(merge_grid(gpu, downsample(tel), now))
        gpu["read_ok"] = True
    else:
        # Cache what we have and say the read failed. The page prints this.
        gpu["read_ok"] = False
    gpu.setdefault("bucket_seconds", BUCKET)

    queue = collect_queue(since)
    jobs = collect_jobs(branches, since)

    out = {
        "schema": SCHEMA,
        "generated": now,
        "retain_days": RETAIN_DAYS,
        "gpu": gpu,
        "queue": {
            "samples": queue,
            "source": f"{QUEUE_PATH} git history on main — one sample per commit",
        },
        "jobs": {
            "events": jobs,
            "source": f"{HEARTBEAT_PATH} git history on {len(branches)} farm-results-* branches",
            "branches": sorted(b.split("farm-results-")[-1] for b in branches),
        },
    }
    if not dry_run:
        CACHE.write_text(json.dumps(out, separators=(",", ":"), sort_keys=False) + "\n")
    return out


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    out = build(dry_run=dry)
    g = out["gpu"]
    n = len(g.get("u") or [])
    filled = sum(1 for x in (g.get("u") or []) if x is not None)
    print(f"gpu    : {filled}/{n} buckets carry a sample "
          f"({BUCKET}s grid, read_ok={g.get('read_ok')}, "
          f"from {g.get('source_ref') or 'nowhere'})")
    print(f"queue  : {len(out['queue']['samples'])} samples")
    print(f"jobs   : {len(out['jobs']['events'])} events "
          f"from {', '.join(out['jobs']['branches']) or 'no branches'}")
    if not dry:
        print(f"written: {CACHE.relative_to(REPO)} "
              f"({CACHE.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
