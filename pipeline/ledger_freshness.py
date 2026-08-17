#!/usr/bin/env python3
"""IS THE RUN LEDGER SAFE TO DECIDE FROM RIGHT NOW?

`pipeline/measured/queue-history.json` is the run ledger, and the standing
instruction to every lane is to verify run status against it rather than
against whether an output directory exists — for good reason, since output
directories get pruned and 456 of 509 render sidecars sit in an untracked
`farm-out/`, so absence there proves nothing.

The ledger then went stale, and two lanes decided from it anyway on
2026-08-16:

  * one found it TWO DAYS OLD (573 rows, newest finished_at
    2026-08-14T16:24:58Z) and missing beat 07's post-gate motion runs
    entirely. It got the right answer only by reading the 799 box sidecars on
    origin/farm-results-rtx5090 instead;
  * one FILED TWELVE DUPLICATE JOBS because the ledger — measured at 17:19 —
    still listed as unrun twelve jobs that had finished around 15:49.

WHY IT LAGS, both causes confirmed in queue_history.py:

 1. NOTHING RUNS IT. Two commits in the file's life, 48 h 23 min apart, and
    the second was the side effect of an audit, not the duty SITE.md
    describes. There is no schedule, no hook, no CI step, no caller.
 2. EVEN A FRESH RUN CAN PROJECT AN ANCIENT BRANCH. `queue_history.py`
    resolves `git rev-parse origin/farm-results-rtx5090` — the LOCAL
    remote-tracking ref — and fetches only under an opt-in `--fetch`. Then it
    stamps `measured_at = now`. So the 17:19 rebuild read a ref last fetched
    at 15:57 and published a stamp saying 17:19. THE LEDGER'S OWN TIMESTAMP
    IS NOT A STATEMENT ABOUT THE AGE OF ITS DATA, and incident 2 is exactly
    what that gap costs.

Cause 2 is why "make the file declare its own age" is not enough on its own:
at the moment the twelve duplicates were filed, `measured_at` was ONE MINUTE
OLD. An age check would have waved it through. The age of a projection is not
the age of its source.

So this module measures four things, and says which of them it could measure:

  age           now - measured_at                    (offline, free)
  harvest lag   measured_at - commit_date(source)    (offline, free)
  local drift   source_commit vs origin/<branch>     (offline, free)
  tip drift     source_commit vs the REAL remote tip (online, ~0.6 s)

Each offline signal alone misses one of the two incidents — age says "fine"
about incident 2, harvest lag and local drift say "fine" about incident 1 —
and their union catches both. The online tip check catches both by itself and
exactly, for 0.6 s, which is why it is the default.

WHY THIS END OF THE PROBLEM. Regenerating on a schedule is what
`box_autofill.py` does, but that is a Windows `schtasks` task on the box; this
Mac has no crontab, its one LaunchAgent is not loaded, and `gate_sentinel.py`
says in its own docstring that building it and arming it are two decisions.
An unattended writer rewriting a 3 MB tracked file inside a seven-lane shared
worktree is a hazard, and a schedule narrows the stale window without ever
telling a reader it is inside one. box_autofill proves the point itself: it is
scheduled AND it still prints its reading's age and fails at 15 minutes. On
this side of the farm only the second half is available, and it is the half
that would have stopped both incidents.

It is also the half with a cheap remedy. A full rebuild is 7.3 s and needs no
network (~31 s with the fetch), so the sentence this module prints — re-run
the generator — costs seconds, which is what makes a refusal obeyable rather
than something to route around.

WHAT IT WILL NOT DO. It never rewrites the ledger (its `_meta.writer` forbids
hand-editing and the next run would put the stale bytes back — the same reason
`gate_text()` was fixed in the reader). It never returns CURRENT on a check it
could not complete: no network means UNKNOWN, not fine.

Usage:
    python3 pipeline/ledger_freshness.py           # online check, ~0.6 s
    python3 pipeline/ledger_freshness.py --offline # no network at all
    python3 pipeline/ledger_freshness.py --deep    # fetch + exact missing count
    python3 pipeline/ledger_freshness.py --json

Exit codes (house convention: one number, distinct states):
    0  CURRENT — the ledger holds every run the branch has published
    1  STALE   — runs exist that it does not know about; do not decide from it
    2  UNKNOWN — could not establish it either way; do not decide from it
Both 1 and 2 mean the same thing to a caller: this file is not an answer.

As a library:
    from ledger_freshness import check, require_fresh
    v = check()
    if not v.trustworthy:
        print(v.banner())
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BRANCH = "farm-results-rtx5090"
REMOTE_REF = f"origin/{BRANCH}"
LEDGER = REPO / "pipeline" / "measured" / "queue-history.json"

# ---------------------------------------------------------------- thresholds
#
# Both numbers are measured off the results branch's own 2107-commit history,
# not chosen. `farm_worker.py` force-pushes a heartbeat for the whole length of
# a task, so the branch's commit gaps ARE the card's silence:
#
#     p50 3.3 min   p90 10.1 min   p99 10.1 min   longest ever 0.75 h
#
# LEDGER_HARVEST_LAG_MINUTES — how old the source ref may be at build time. A
# build that fetches sees a tip no older than the current quiet gap, so the
# ceiling is that 45-minute all-time maximum; 60 gives it room and still
# catches incident 2's 82.6 min. Below 45 the check would flag builds that did
# everything right, which is how the runner watchdog got itself switched off
# for four days after 60 false restarts in five hours.
LEDGER_HARVEST_LAG_MINUTES = 60

# LEDGER_STALE_HOURS — offline backstop only; the tip check outranks it
# whenever the network answered. The branch has never been silent for
# three quarters of an hour, so six is eight times the longest quiet the card
# has ever taken, and a checkout that has not looked at the branch in six
# hours cannot answer "has this run" for that window whatever the data says.
LEDGER_STALE_HOURS = 6.0

CURRENT, STALE, UNKNOWN = "CURRENT", "STALE", "UNKNOWN"
_EXIT = {CURRENT: 0, STALE: 1, UNKNOWN: 2}


# ------------------------------------------------------------------ verdict

class Verdict:
    """What we concluded, every number behind it, and what we could not check.

    `trustworthy` is True for exactly one state. There is deliberately no
    "probably fine" — a reader asking this question is about to file a job or
    publish a page, and the two incidents this module exists for were both a
    lane treating an unproven ledger as a proven one.
    """

    def __init__(self, state, headline, lines=None, facts=None, unchecked=None):
        self.state = state
        self.headline = headline
        self.lines = list(lines or [])
        self.facts = dict(facts or {})
        self.unchecked = list(unchecked or [])

    @property
    def trustworthy(self):
        return self.state == CURRENT

    @property
    def exit_code(self):
        return _EXIT[self.state]

    def banner(self):
        """The loud form. A reader that prints this cannot be misread."""
        out = ["%s: %s" % (self.state, self.headline)]
        out += ["    " + ln for ln in self.lines]
        for u in self.unchecked:
            out.append("    NOT CHECKED: " + u)
        if not self.trustworthy:
            out.append("    DO NOT DECIDE RUN STATUS FROM %s."
                       % LEDGER.relative_to(REPO))
            out.append("    Re-run: python3 pipeline/queue_history.py"
                       "   (~31 s, $0, no GPU)")
        return "\n".join(out)

    def as_dict(self):
        return {"state": self.state, "trustworthy": self.trustworthy,
                "headline": self.headline, "lines": self.lines,
                "unchecked": self.unchecked, "facts": self.facts}

    def __repr__(self):
        return "<Verdict %s %s>" % (self.state, self.headline)


# ------------------------------------------------------------ time handling

def parse_stamp(s):
    """An ISO-ish UTC stamp -> aware datetime, or None. Never raises.

    Returning None rather than guessing matters: a stamp this cannot read must
    become UNKNOWN, and a stamp silently coerced to epoch would become a
    confident STALE about a file that might be fine.
    """
    if not isinstance(s, str) or not s.strip():
        return None
    t = s.strip().replace("Z", "+00:00")
    try:
        d = datetime.datetime.fromisoformat(t)
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return d.astimezone(datetime.timezone.utc)


def _fmt_age(seconds):
    if seconds is None:
        return "unknown"
    m = seconds / 60.0
    if m < 90:
        return "%.0f min" % m
    h = m / 60.0
    if h < 48:
        return "%.1f h" % h
    return "%.1f days" % (h / 24.0)


# ------------------------------------------------------------- the judgement

def assess(meta, now, tip=None, local_ref=None, source_commit_at=None,
           missing_sidecars=None, network_error=None):
    """PURE. -> Verdict. No git, no clock, no filesystem — everything injected.

    `tip` is the real remote tip if the network answered, else None. `None` is
    not "they match", it is "we did not look", and the difference is the whole
    module: the twelve duplicate jobs were filed against a ledger that matched
    the local ref exactly and was 82 minutes behind the remote one.

    ORDER MATTERS, AND THIS MACHINE PROVED IT. The sha comparisons need no
    clock; only the age and harvest-lag signals do. On 2026-08-16 this Mac's
    wall clock was found ~23.9 h BEHIND the repo's own commit timeline — HEAD
    was stamped a full day before its own parent — so a clock-first check
    abstained on a ledger it could have judged exactly. The clock-free signals
    are therefore asked first, and a broken clock costs only the signals that
    genuinely depend on it.
    """
    facts, unchecked = {}, []

    if not isinstance(meta, dict):
        return Verdict(UNKNOWN, "the ledger could not be read at all",
                       ["nothing was parsed, so nothing is known about its age"])

    measured_at = parse_stamp(meta.get("measured_at"))
    source = meta.get("source_commit")
    facts["source_commit"] = source
    facts["measured_at"] = meta.get("measured_at")
    facts["job_count"] = meta.get("job_count")

    if not isinstance(source, str) or len(source) < 7:
        return Verdict(UNKNOWN, "the ledger names no source commit",
                       ["`_meta.source_commit` is %r, so there is nothing to "
                        "compare the branch against." % (source,)],
                       facts=facts)

    # ---- the clock, and whether it can be believed at all.
    age_s = None if measured_at is None else (now - measured_at).total_seconds()
    clock_broken = age_s is not None and age_s < -300
    if measured_at is None:
        age_line = ("`_meta.measured_at` is %r — unreadable, so this file's own "
                    "age is unknown" % (meta.get("measured_at"),))
        unchecked.append("age — the ledger carries no readable `measured_at`")
    elif clock_broken:
        age_line = ("`measured_at` (%s) is %s AHEAD of this machine's clock — a "
                    "clock is wrong somewhere, so no age here means anything"
                    % (meta.get("measured_at"), _fmt_age(-age_s)))
        unchecked.append("age and harvest lag — this machine's clock disagrees "
                         "with the ledger's own stamp by %s" % _fmt_age(-age_s))
    else:
        facts["age_seconds"] = age_s
        age_line = "measured %s ago (%s)" % (_fmt_age(age_s),
                                             meta.get("measured_at"))

    # harvest lag: how old the source ref already was when the build ran. This
    # is a difference between two stamps in the record itself, so it survives a
    # wrong wall clock — only an unreadable `measured_at` kills it.
    src_at = parse_stamp(source_commit_at)
    lag_s = None
    if src_at is not None and measured_at is not None:
        lag_s = (measured_at - src_at).total_seconds()
        facts["harvest_lag_seconds"] = lag_s
    elif src_at is None:
        unchecked.append("harvest lag — this checkout cannot date commit %s "
                         "(the results branch is not present here)" % source[:12])

    # ---- CLOCK-FREE: the online answer outranks everything, in both directions.
    if tip:
        same = tip.startswith(source) or source.startswith(tip)
        facts["tip"] = tip
        if same:
            lines = ["source commit %s IS the tip of origin/%s"
                     % (source[:12], BRANCH),
                     "the card has published nothing since, so age cannot make "
                     "it incomplete — " + age_line]
            if missing_sidecars is not None:
                lines.append("deep check: %d sidecars on the branch, %s in the "
                             "ledger" % (missing_sidecars["on_branch"],
                                         missing_sidecars["in_ledger"]))
            return Verdict(CURRENT, "the ledger holds every run the branch has "
                                    "published", lines, facts, unchecked)
        lines = ["built from %s; origin/%s is now at %s"
                 % (source[:12], BRANCH, tip[:12]), age_line]
        if missing_sidecars is not None:
            n = missing_sidecars["missing"]
            lines.append("%d run%s finished that this ledger has never heard of"
                         % (n, "" if n == 1 else "s"))
            facts["missing"] = n
        else:
            lines.append("how many runs it is missing needs the objects: "
                         "re-run with --deep (~24 s fetch)")
        return Verdict(STALE, "the branch has moved since this ledger was built",
                       lines, facts, unchecked)

    # ---- offline from here. Say so, and never upgrade to CURRENT.
    unchecked.append(network_error or
                     "the real branch tip — no network check was made, so a "
                     "ledger that looks current here may not be")

    # CLOCK-FREE: the branch has already moved in this very checkout.
    if local_ref and not (local_ref.startswith(source) or source.startswith(local_ref)):
        return Verdict(STALE, "the branch has moved in this checkout since the "
                              "ledger was built",
                       ["built from %s; this checkout's %s is already at %s"
                        % (source[:12], REMOTE_REF, local_ref[:12]),
                        age_line,
                        "and nothing has fetched, so the real remote is at "
                        "least this far ahead"], facts, unchecked)

    # Two stamps inside the record: survives a wrong wall clock.
    if lag_s is not None and lag_s > LEDGER_HARVEST_LAG_MINUTES * 60:
        return Verdict(UNKNOWN, "the ledger was built from a ref that was "
                                "already %s old" % _fmt_age(lag_s),
                       ["stamped %s, but its source commit %s dates from %s"
                        % (meta.get("measured_at"), source[:12], source_commit_at),
                        "either the card was idle that whole time or nobody "
                        "fetched before building — OFFLINE I CANNOT TELL WHICH",
                        "the branch has never been quiet longer than 0.75 h in "
                        "2107 commits, so the second is the likelier one",
                        "run without --offline to settle it in ~0.6 s"],
                       facts, unchecked)

    if clock_broken or age_s is None:
        return Verdict(UNKNOWN, "the ledger cannot be dated on this machine",
                       [age_line,
                        "the sha checks came back clean, but they were the "
                        "cheap ones: nothing here proves the branch has not "
                        "moved beyond this checkout",
                        "run without --offline — the tip check needs no clock"],
                       facts, unchecked)

    if age_s > LEDGER_STALE_HOURS * 3600:
        return Verdict(STALE, "the ledger's knowledge is %s old" % _fmt_age(age_s),
                       [age_line,
                        "nothing has fetched %s since, so this checkout cannot "
                        "see any run that finished in that window — whatever "
                        "the branch actually did" % BRANCH,
                        "this is the shape of the 2026-08-16 incident: a 47-hour "
                        "ledger missing a whole beat's post-gate motion runs"],
                       facts, unchecked)

    return Verdict(UNKNOWN, "nothing offline contradicts this ledger, which is "
                            "not the same as current",
                   [age_line,
                    "harvest lag %s; source commit %s matches this checkout's "
                    "%s" % (_fmt_age(lag_s) if lag_s is not None else "unknown",
                            source[:12], REMOTE_REF),
                    "the branch tip was never asked, and that is the one signal "
                    "that caught the duplicate-filing incident"],
                   facts, unchecked)


# ------------------------------------------------------------------- the I/O

def _git(*args, timeout=30, repo=None):
    """-> stdout, or None on any failure. Never raises, never blocks forever."""
    try:
        r = subprocess.run(("git",) + args, cwd=str(repo or REPO),
                           capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def read_meta(path=None):
    """-> the ledger's `_meta` dict, or None if it cannot be read."""
    p = Path(path or LEDGER)
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return doc.get("_meta") if isinstance(doc, dict) else None


def local_tip(repo=None):
    out = _git("rev-parse", REMOTE_REF, repo=repo)
    return out.strip() if out else None


def commit_date(sha, repo=None):
    """The commit's own date as an ISO Z string, or None if we lack the object.

    A deploy checkout has no farm branches at all (which is why the ledger
    exists), so None here is normal and must stay an abstention.
    """
    if not sha:
        return None
    out = _git("show", "-s", "--format=%cI", sha, repo=repo)
    if not out or not out.strip():
        return None
    d = parse_stamp(out.strip())
    return d.strftime("%Y-%m-%dT%H:%M:%SZ") if d else None


def remote_tip(repo=None, timeout=20):
    """-> (sha, None) or (None, why). ~0.6 s: refs only, no objects."""
    out = _git("ls-remote", "origin", "refs/heads/" + BRANCH,
               timeout=timeout, repo=repo)
    if out is None:
        return None, ("the real branch tip — `git ls-remote` failed or timed "
                      "out (offline?), so freshness could not be settled")
    line = out.strip().split("\n")[0].strip() if out.strip() else ""
    sha = line.split()[0] if line else ""
    if len(sha) < 7:
        return None, ("the real branch tip — origin has no refs/heads/%s"
                      % BRANCH)
    return sha, None


def deep_count(tip, meta, repo=None):
    """Exact missing-run count. Costs a fetch (~24 s); mirrors --verify-deployed."""
    if _git("fetch", "origin", BRANCH, timeout=180, repo=repo) is None:
        return None
    out = _git("ls-tree", "-r", "--name-only", tip, "farm-out/box", repo=repo)
    if out is None:
        return None
    on_branch = sum(1 for ln in out.split("\n") if ln.endswith(".json"))
    in_ledger = meta.get("job_count")
    if not isinstance(in_ledger, int):
        return None
    return {"on_branch": on_branch, "in_ledger": in_ledger,
            "missing": max(0, on_branch - in_ledger)}


def check(path=None, offline=False, deep=False, now=None, repo=None):
    """The whole question, answered. -> Verdict."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    meta = read_meta(path)
    if meta is None:
        return Verdict(UNKNOWN, "the ledger is missing or unparseable",
                       ["%s could not be read as JSON with a `_meta` object"
                        % (path or LEDGER)])
    source = meta.get("source_commit")
    src_at = meta.get("source_commit_at") or commit_date(source, repo=repo)

    tip, why = (None, None) if offline else remote_tip(repo=repo)
    if offline:
        why = ("the real branch tip — --offline was asked for, so the one "
               "signal that catches a not-fetched build was skipped")

    missing = None
    if deep and tip and source and not (tip.startswith(source)
                                        or source.startswith(tip)):
        missing = deep_count(tip, meta, repo=repo)

    return assess(meta, now, tip=tip, local_ref=local_tip(repo=repo),
                  source_commit_at=src_at, missing_sidecars=missing,
                  network_error=why)


def require_fresh(path=None, offline=False, now=None, repo=None):
    """For a reader about to decide. -> (ok, banner_or_None).

    The contract a caller wants: `ok` is True only for CURRENT, so an honest
    "I cannot tell" reaches the caller as a refusal rather than as a pass.
    """
    v = check(path=path, offline=offline, now=now, repo=repo)
    return v.trustworthy, (None if v.trustworthy else v.banner())


# ---------------------------------------------------------------------- cli

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--path", default=None, help="ledger to check")
    ap.add_argument("--offline", action="store_true",
                    help="no network; UNKNOWN rather than a guess")
    ap.add_argument("--deep", action="store_true",
                    help="fetch and count exactly how many runs are missing")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    v = check(path=a.path, offline=a.offline, deep=a.deep)
    if a.json:
        print(json.dumps(v.as_dict(), indent=1))
    else:
        print(v.banner())
    return v.exit_code


if __name__ == "__main__":
    sys.exit(main())
