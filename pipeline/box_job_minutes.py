#!/usr/bin/env python3
"""How long a render job takes on the box, measured off the box's own records.

Written 2026-08-12 for the founder's "i should be able to see how long the
queue is in time as well". The status page multiplies what is queued by a
median from here; this script is where that median comes from and how anyone
re-derives it.

TWO THINGS IT REFUSES TO DO, both learned the same afternoon.

It does not parse the step logs. `farm-out/**/*.log` is tail-truncated by the
courier at 200 lines, so 135 of 252 logs have lost the `#### job ... start`
line they open with. Timing those logs is not merely lossy — it is BIASED: the
jobs that overflow 200 lines are the chatty, long ones, so every job the
truncation drops is a slow job, and a median off what survives runs fast. The
per-job sidecar `farm-out/box/<id>.json` carries `started_at` and `finished_at`
written by the runner, covers every job (248 of 248 at the time of writing),
and cannot be truncated because it is not a stream.

It does not report one pooled median as if it meant something. Pooled across
kinds the figure swings with nothing but the window you pick — a five-minute
LTX clip and a forty-second publish step are both "a job" — so the numbers
below are per KIND, which is what the status page multiplies. The pooled figure
is printed too, and only as the fallback for a queue whose kinds are unknown.

    python3 pipeline/box_job_minutes.py                  # default branch, all jobs
    python3 pipeline/box_job_minutes.py --last 40        # the newest 40 only
    python3 pipeline/box_job_minutes.py --yaml           # the block for box-queue.yaml

Read-only: `git show` against a remote-tracking ref, no checkout, no fetch.
"""
import argparse
import json
import statistics
import subprocess
from datetime import datetime, timezone

BRANCH = "origin/farm-results-rtx5090"
SIDECARS = "farm-out/box/"

# argv fingerprint → the kind name the status page and the supervisor tick both
# use. Order matters: the first hit wins, and LTX leads because a motion job
# also crops and publishes.
KINDS = [
    ("ltx_i2v", "ltx"),
    ("goblin_ipa_beat", "charref"),
    ("render_wave_sample", "still"),
    ("inpaint_fruit", "inpaint"),
    ("runpod_render", "still"),
]


def _run(args: list) -> str:
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def job_kind(spec: dict) -> str:
    """One word for what this job IS, off the scripts its steps actually run.

    Read from argv rather than from the job id: ids are written by whoever
    filed the job and drift into nicknames, while the argv is what ran.
    """
    blob = " ".join(" ".join(s.get("argv") or []) for s in spec.get("steps") or [])
    for needle, kind in KINDS:
        if needle in blob:
            return kind
    return "other"


def _iso(s):
    try:
        return datetime.strptime(str(s), "%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError):
        return None


def jobs(branch: str = BRANCH) -> list:
    """(finished_at, id, kind, minutes, rc) per job the box recorded, oldest first."""
    names = _run(["git", "ls-tree", "-r", "--name-only", branch]).split()
    out = []
    for path in names:
        if not (path.startswith(SIDECARS) and path.endswith(".json")):
            continue
        try:
            spec = json.loads(_run(["git", "show", f"{branch}:{path}"]))
        except json.JSONDecodeError:
            continue
        start, end = _iso(spec.get("started_at")), _iso(spec.get("finished_at"))
        if not start or not end:
            continue                      # never ran, or still running
        out.append((end, str(spec.get("id") or path), job_kind(spec),
                    (end - start).total_seconds() / 60.0, spec.get("rc")))
    return sorted(out)


def medians(rows: list) -> dict:
    """kind → median minutes, plus '' for the pooled fallback."""
    by = {"": [r[3] for r in rows]}
    for r in rows:
        by.setdefault(r[2], []).append(r[3])
    return {k: round(statistics.median(v), 1) for k, v in by.items() if v}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--branch", default=BRANCH)
    ap.add_argument("--last", type=int, default=0, help="newest N jobs only")
    ap.add_argument("--yaml", action="store_true",
                    help="print the block to paste into measured/box-queue.yaml")
    a = ap.parse_args()

    rows = jobs(a.branch)
    if not rows:
        print(f"no job sidecars under {a.branch}:{SIDECARS}")
        return 1
    window = rows[-a.last:] if a.last else rows
    med = medians(window)
    ok = [r for r in window if r[4] == 0]

    if not a.yaml:
        for end, jid, kind, mins, rc in window[-20:]:
            print(f"{end:%m-%d %H:%M}  {mins:6.1f} min  rc={rc!s:<4} "
                  f"{kind:8} {jid[:56]}")
        print(f"\n{len(window)} jobs, {end and window[0][0]:%d %b} → "
              f"{window[-1][0]:%d %b}, {len(ok)} of them rc=0")
        for kind in sorted(k for k in med if k):
            v = [r[3] for r in window if r[2] == kind]
            print(f"  {kind:8} n={len(v):<4} median {med[kind]:5.1f} min   "
                  f"(min {min(v):.1f}, max {max(v):.1f})")
        print(f"  {'POOLED':8} n={len(window):<4} median {med['']:5.1f} min "
              f"— fallback only; it means little across kinds")
        return 0

    print("kind_medians:")
    for kind in sorted(k for k in med if k):
        print(f"  {kind}: {med[kind]}")
    print(f"kind_median_fallback: {med['']}")
    print(f"median_from: the {len(window)} jobs the box finished "
          f"{window[0][0]:%d} – {window[-1][0]:%d %b}")
    print(f"median_measured_at: {datetime.now(timezone.utc):%Y-%m-%d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
