#!/usr/bin/env python3
"""How much work the render box actually did, per day, off its own job records.

    python3 pipeline/box_work_daily.py            # look at it
    python3 pipeline/box_work_daily.py --write    # update measured/box-work-daily.yaml

WHY THIS IS A FILE AND NOT A BUILD-TIME READ. The numbers come from
`farm-out/box/<id>.json` on `origin/farm-results-rtx5090` — the per-job sidecars
the box's runner writes itself, with `started_at` and `finished_at` in them. A
deploy checkout has no farm branches, so `build_sim.py` cannot read them; the
same reason `pipeline/measured/eta.yaml` exists. Measured here, committed, read
there. The file carries the date it was measured and the page prints it, so a
stale measurement is visible as a stale measurement rather than as today.

WHY MINUTES AND NOT JOBS. A count of jobs answers the wrong question. On
11 Aug the box finished 119 jobs and on 12 Aug it finished 104, which reads as
a quieter day — except the 12th was mostly five-minute motion clips and the
11th was mostly still frames, so the 12th was by far the harder day. The bars
are the minutes the box's own clock says it spent, and the job counts ride
along in the tooltip and the table for anyone who wants them.

TWO HONESTIES BUILT IN.

  * A job is counted on the day it FINISHED, because that is the timestamp we
    can trust for every job; a clip that starts at 23:50 and lands at 00:20 puts
    all of its minutes on the second day. It is stated on the page.
  * The newest day is almost always still running, so it is flagged `partial`
    and the page labels its bar "so far" instead of letting a half-day read as
    a collapse in output.

THIS IS BUSY TIME, NOT UTILISATION. It sums per-job durations. The box runs one
job at a time, so the sum is very close to how long the card was working, but it
is not a GPU-utilisation figure and the page does not call it one — a job that
spends four of its five minutes loading weights counts all five here.
"""
import argparse
import collections
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
import box_job_minutes as bjm  # noqa: E402  one reader for the box's sidecars

OUT = REPO / "pipeline" / "measured" / "box-work-daily.yaml"
# How many days the page shows. Two weeks is longer than the record is old and
# is the point at which a phone-width bar stops being wide enough to hit.
KEEP_DAYS = 14


def collect(branch: str = bjm.BRANCH) -> dict:
    """{"days": [...], "kinds": [...]} — one entry per calendar day, oldest first."""
    rows = bjm.jobs(branch)
    if not rows:
        return {}
    per_day = collections.defaultdict(lambda: collections.Counter())
    jobs_day = collections.Counter()
    failed_day = collections.Counter()
    kind_total = collections.Counter()
    for end, _jid, kind, mins, rc in rows:
        day = end.strftime("%Y-%m-%d")
        per_day[day][kind] += mins
        jobs_day[day] += 1
        kind_total[kind] += mins
        # rc is None for a sidecar written before the runner recorded one. That
        # is "unknown", not "fine", so only an explicit non-zero counts as a
        # failure and the unknowns are simply not claimed either way.
        if rc not in (0, None):
            failed_day[day] += 1

    days = sorted(per_day)[-KEEP_DAYS:]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "kinds": [k for k, _v in kind_total.most_common()],
        "days": [{"date": d,
                  "jobs": jobs_day[d],
                  "failed": failed_day[d],
                  "minutes": round(sum(per_day[d].values())),
                  "by_kind": {k: round(v) for k, v in
                              sorted(per_day[d].items(), key=lambda kv: -kv[1])},
                  "partial": d == today}
                 for d in days],
    }


def as_yaml(doc: dict, branch: str) -> str:
    if not doc or not doc["days"]:
        return ""
    span = f'{doc["days"][0]["date"]} – {doc["days"][-1]["date"]}'
    tot = sum(d["jobs"] for d in doc["days"])
    out = [
        "# What the render box did, per day — WRITTEN BY pipeline/box_work_daily.py.",
        "# Do not hand-edit: re-run the script instead, or the page publishes a",
        "# number nothing measured.",
        "#",
        "# Source: the per-job sidecars farm-out/box/<id>.json on",
        f"# {branch}, written by the box's own runner. `minutes` is the sum of",
        "# (finished_at - started_at) over the jobs that FINISHED that day, so a job",
        "# spanning midnight puts all of its minutes on the second day. It is busy",
        "# time, not GPU utilisation.",
        "#",
        "# `partial: true` marks a day that was still running when this was measured.",
        "# The status page labels that bar 'so far' rather than letting half a day",
        "# read as a drop in output.",
        f"measured_at: {datetime.now(timezone.utc):%Y-%m-%d %H:%MZ}",
        f"branch: {branch}",
        f"window: {span}",
        f"jobs_total: {tot}",
        f'kinds: [{", ".join(doc["kinds"])}]',
        "days:",
    ]
    for d in doc["days"]:
        by = ", ".join(f"{k}: {v}" for k, v in d["by_kind"].items())
        out.append(f'  - {{date: {d["date"]}, jobs: {d["jobs"]}, '
                   f'failed: {d["failed"]}, minutes: {d["minutes"]}, '
                   f'partial: {"true" if d["partial"] else "false"}, '
                   f'by_kind: {{{by}}}}}')
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--branch", default=bjm.BRANCH)
    ap.add_argument("--write", action="store_true",
                    help=f"write {OUT.relative_to(REPO)}")
    a = ap.parse_args()

    doc = collect(a.branch)
    text = as_yaml(doc, a.branch)
    if not text:
        print(f"no finished job sidecars under {a.branch}:{bjm.SIDECARS}")
        return 1
    if a.write:
        OUT.write_text(text, encoding="utf-8")
        print(f"✓ {OUT.relative_to(REPO)} — {len(doc['days'])} days, "
              f"{sum(d['jobs'] for d in doc['days'])} jobs")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
