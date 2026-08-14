#!/usr/bin/env python3
"""Renders that finished and that nobody ever showed the founder.

Written 2026-08-14, after he said the same thing four times in three days about
four different pieces of work: the guard character sheets (rendered, asked for
three times, never linked), the sapling-reveal frames (four candidates rendered
a day before he asked), beat 02's rerun (already done when he called it broken)
and beat 12's passing plate. In every case the render succeeded. What failed was
the last step, and from where he sits a render nobody paged and a render nobody
ran are the same event.

`box_enqueue.py` already refuses a job that names no `consumer:` -- "no work
without one". Nothing checked that the promise was ever kept. This does.

WHAT IT MEANS BY "PAGED". A job is paged when something the founder can open
NAMES it: the review board, an inbox entry, an ep2-picks page, or any generated
page in `_site/`. Named how -- one of four keys, each taken from the job's own
record rather than guessed at:

  * the task id             ep2-guard-sheet-a-r2-0814
  * the stamped job id      ep2-guard-sheet-a-r2-0814-1786707392
  * a publish directory     ep2-b02-idfix     (parsed out of the publish step's
                            argv: `courier-box/farm-out/<dir>`)
  * an artifact's basename  06-the-clipboard-wave1-s0.png

The publish directory is not decoration, it is what makes the answer usable. A
contact sheet BAKES four frames into one JPG, so no artifact filename survives
onto the page -- but the wave2 page cites `ep2-b02-idfix` beside each sheet, and
that is the only thread tying the picture back to the round that drew it.
Without this key, fifteen already-shown beats read as unpaged.

Matching is on token boundaries, deliberately: `ep2-b02-goblin-occl` must NOT be
credited by a page that only names `ep2-b02-goblin-occlbright`. Those are two
rounds and one of them is the one he never saw.

THREE BUCKETS, AND ONLY THE FIRST IS THE NUMBER. The spec's `consumer:` says in
its own words who the output was for. Jobs whose consumer NAMES HIM are the
promise this tool exists to audit; jobs whose consumer names another artifact
("the v35 screening cut", "motion-wave") are ingredients whose own paging is
that downstream artifact's business; jobs whose spec has gone are reported as a
count, because a missing spec is a missing promise and cannot be audited.

The bias is toward silence: a job that promises him a look without saying his
name reads as an ingredient and drops out of the count. That is the right way
round for a warning that runs on every build, and the fix for a miscounted job
is one word in its own spec.

WHAT IT DOES NOT DO. It never fails a build. A render that finished ninety
seconds ago is not a broken promise, it is a job in flight, so anything younger
than --grace is listed apart from the count. And a render whose artifacts are
absent is a FAILED render, not an unpaged one -- a different problem with a
different owner, and counting it here would bury this one.

    python3 pipeline/unpaged.py                # the whole standing backlog
    python3 pipeline/unpaged.py --since 12     # what the last 12 h left unpaged
    python3 pipeline/unpaged.py --all          # ingredients and orphans too
    python3 pipeline/unpaged.py --grace 6      # in-flight window, hours

`--since` is the supervisor's view and the one to act on: the backlog moves
slowly and reads as wallpaper, while "two rounds finished in your window and
neither is on a page" is a thing one person can fix in one pass.

Read-only: `git ls-tree` / `git cat-file` against a remote-tracking ref. No
checkout, no fetch, no network. A tree without the farm branch -- a deploy
checkout, CI -- gets an empty answer and says so, rather than a zero.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANCH = "origin/farm-results-rtx5090"
SIDECARS = "farm-out/box/"
JOBS = os.path.join(REPO, "pipeline", "jobs")

# How long a finished job may go unpaged before it counts. A wave lands every
# few minutes and the lane that fires it pages it in the same pass, so this is
# the width of "still working on it", not a grace anybody is entitled to.
GRACE_HOURS = 2.0

# Extensions a person can look at. A job that produced only yaml, json, jsonl or
# a log produced no picture to show, and most of those are measurement passes
# whose consumer is a number in a report.
VIEWABLE = (".png", ".jpg", ".jpeg", ".mp4", ".webm", ".gif", ".mp3", ".wav")

# `courier-box\farm-out\<dir>` in a publish step's argv -- the durable directory
# the courier pushes and the name a review page cites when the frames themselves
# were baked into a sheet. Both slash dialects: the box is Windows, the specs
# are written on a Mac.
PUBLISH_DIR = re.compile(r"courier-box[\\/]+farm-out[\\/]+([A-Za-z0-9._-]+)")

# The enqueue stamp `to_job` appends: id + "-" + int(time.time()).
STAMP = re.compile(r"-\d{10}$")

# The founder, in the words a spec actually uses for him. Narrow on purpose --
# see the bucket note above.
#
# `R4` is deliberately NOT here, though it means him. In a consumer sentence it
# reads "which round the cut uses is R4's open call" -- the taste rule, cited to
# say who decides EVENTUALLY, not that this job's own frames go to his screen.
# Eleven v34 plate twins whose consumer is plainly "the v35 screening cut" were
# counted as broken promises on that word alone.
FOUNDER = re.compile(r"\b(roman|founder|oleg)\b", re.I)


# ------------------------------------------------------------------ pure logic

def task_of(job_id: str) -> str:
    """The spec's id, with the enqueue-time epoch stamp taken back off."""
    return STAMP.sub("", str(job_id or ""))


def publish_dirs(spec: dict) -> list:
    """Every courier directory this job's steps publish into, deduped, sorted."""
    blob = " ".join(" ".join(s.get("argv") or []) for s in spec.get("steps") or [])
    return sorted(set(PUBLISH_DIR.findall(blob)))


def viewable_artifacts(spec: dict) -> list:
    """The artifacts the runner CONFIRMED on disk and a person could look at.

    `artifacts_present` and not `artifacts`: the second is what the job declared
    it would make, the first is what the runner found afterwards. A job that
    declared four frames and made none is a failed render, and this returning
    empty for it is what keeps it out of the count.
    """
    return [a for a in (spec.get("artifacts_present") or [])
            if str(a).lower().endswith(VIEWABLE)]


def reference_keys(spec: dict) -> list:
    """(kind, key) pairs a founder-facing page could name this job by."""
    jid = str(spec.get("id") or "")
    keys = [("task", task_of(jid))]
    if jid and jid != task_of(jid):
        keys.append(("job", jid))
    keys += [("publish", d) for d in publish_dirs(spec)]
    seen = set()
    for a in viewable_artifacts(spec):
        base = os.path.basename(str(a).replace("\\", "/"))
        if base not in seen:
            seen.add(base)
            keys.append(("file", base))
    return [(k, v) for k, v in keys if v]


def names_founder(consumer: str) -> bool:
    """Does this spec's own consumer sentence say the output is for him."""
    return bool(FOUNDER.search(str(consumer or "")))


def tokens_of(text: str) -> set:
    """Every whole word-or-filename in the corpus, lowercased.

    A SET, not the raw text, and that is a correctness fix as much as a speed
    one. Substring matching would credit `ep2-b02-goblin-occl` to a page that
    only names `ep2-b02-goblin-occlbright` -- two rounds, one of which is
    precisely the one he never saw. Splitting on everything except the
    characters these names are made of gives whole-token comparison for free.

    Trailing punctuation is folded in as well, so `…-occl.` at the end of a
    sentence still names the round it names. (Speed matters here because this
    runs inside build_site: the regex-per-key version scanned six megabytes
    three thousand times and took minutes.)
    """
    out = set()
    for tok in re.findall(r"[A-Za-z0-9._-]+", text.lower()):
        out.add(tok)
        stripped = tok.strip("._-")
        if stripped:
            out.add(stripped)
    return out


def first_reference(keys: list, tokens: set):
    """The first (kind, key) the corpus names as a whole token, or None."""
    for kind, key in keys:
        if key.lower() in tokens:
            return kind, key
    return None


def audit(sidecars: list, consumers: dict, tokens: set, now: datetime,
          grace_hours: float = GRACE_HOURS) -> dict:
    """The whole judgement, as data. No git, no disk, no clock of its own.

    `sidecars` are the parsed per-job records, `consumers` maps task id ->
    consumer sentence, `tokens` is `tokens_of` over every founder-facing page.
    Returns buckets of rows, one row per TASK (a re-run is the same round asked
    again, and listing both would double-count one unshown picture).
    """
    by_task = {}
    for spec in sidecars:
        finished = _iso(spec.get("finished_at"))
        if not finished:
            continue                        # never ran, or still running
        if not viewable_artifacts(spec):
            continue                        # nothing rendered, or nothing to look at
        task = task_of(spec.get("id"))
        row = {
            "task": task,
            "finished": finished,
            "age_hours": (now - finished).total_seconds() / 3600.0,
            "artifacts": len(viewable_artifacts(spec)),
            "rc": spec.get("rc"),
            "runs": 1,
            "keys": reference_keys(spec),
            "consumer": consumers.get(task),
        }
        prev = by_task.get(task)
        if prev is None:
            by_task[task] = row
        else:
            # Newest run wins the age; its keys join the older run's, because a
            # page naming EITHER run has shown this round's pictures.
            prev["runs"] += 1
            prev["keys"] = prev["keys"] + [k for k in row["keys"]
                                           if k not in prev["keys"]]
            if row["finished"] > prev["finished"]:
                for f in ("finished", "age_hours", "artifacts", "rc"):
                    prev[f] = row[f]

    out = {"unpaged": [], "in_flight": [], "ingredient": [], "no_spec": [],
           "paged": []}
    for row in by_task.values():
        hit = first_reference(row["keys"], tokens)
        if hit:
            row["shown_as"] = "%s %s" % hit
            out["paged"].append(row)
        elif row["consumer"] is None:
            out["no_spec"].append(row)
        elif not names_founder(row["consumer"]):
            out["ingredient"].append(row)
        elif row["age_hours"] < grace_hours:
            out["in_flight"].append(row)
        else:
            out["unpaged"].append(row)
    for k in out:
        out[k].sort(key=lambda r: r["finished"])
    return out


def _iso(s):
    try:
        return datetime.strptime(str(s), "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------------- io

def _git(args: list, repo: str = REPO):
    return subprocess.run(["git"] + args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=repo)


def read_sidecars(branch: str = BRANCH, repo: str = REPO) -> list:
    """Every per-job record the box wrote, read off the results branch.

    One `cat-file --batch` for the lot rather than a `git show` each: at 550-odd
    sidecars the per-process version is most of a second, and this runs inside
    the site build. An absent branch is not an error here -- CI and the deploy
    have no farm branches at all -- it is an empty list.
    """
    listing = _git(["ls-tree", "-r", "--name-only", branch, "--", SIDECARS], repo)
    if listing.returncode != 0:
        return []
    names = [n for n in listing.stdout.split()
             if n.startswith(SIDECARS) and n.endswith(".json")]
    if not names:
        return []
    proc = subprocess.Popen(["git", "cat-file", "--batch"], cwd=repo,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    blob, _ = proc.communicate("".join("%s:%s\n" % (branch, n)
                                       for n in names).encode())
    out, at = [], 0
    for _ in names:
        nl = blob.find(b"\n", at)
        if nl < 0:
            break
        header = blob[at:nl].split()
        if len(header) != 3:                # "<oid> missing" -- skip that record
            at = nl + 1
            continue
        size = int(header[2])
        try:
            out.append(json.loads(blob[nl + 1:nl + 1 + size]))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        at = nl + 1 + size + 1              # trailing newline after the object
    return out


def read_consumers(jobs_dir: str = JOBS) -> dict:
    """task id -> the spec's `consumer:` sentence, for every spec on disk.

    Keyed by the spec's own `id` rather than its filename: several specs live
    under a subdirectory or were renamed, and the id is what the sidecar echoes.
    """
    try:
        import yaml
    except ImportError:
        return {}
    out = {}
    for root, dirs, files in os.walk(jobs_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in files:
            if not name.endswith((".yaml", ".yml")):
                continue
            try:
                with open(os.path.join(root, name), encoding="utf-8") as fh:
                    spec = yaml.safe_load(fh)
            except (OSError, UnicodeDecodeError, Exception):  # noqa: B014
                continue
            if isinstance(spec, dict) and spec.get("id"):
                out[str(spec["id"])] = str(spec.get("consumer") or "")
    return out


def read_corpus(repo: str = REPO) -> tuple:
    """(token set of every founder-facing page, note about coverage).

    Two sources, and both are needed. `review/` in the TREE is the authority for
    the board, the inbox and the pick pages -- it is what CI clones and what the
    deploy serves. `_site/` adds the generated pages: the shot boards, the watch
    pages, anything build_site writes from the genomes. `_site/` is gitignored,
    so a tree that has not been built yet is missing half the answer and the
    note says which half.
    """
    tokens, note = set(), ""
    review = os.path.join(repo, "review")
    for root, dirs, files in os.walk(review):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in files:
            if name.endswith((".html", ".yaml", ".yml", ".json", ".md")):
                tokens |= tokens_of(_read(os.path.join(root, name)))
    site = os.path.join(repo, "_site")
    if os.path.isdir(site):
        for root, _dirs, files in os.walk(site):
            for name in files:
                if name.endswith(".html"):
                    tokens |= tokens_of(_read(os.path.join(root, name)))
    else:
        note = ("_site/ is not built, so only the pages in the tree were read "
                "— run build_site.py for the full answer")
    return tokens, note


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def survey(repo: str = REPO, branch: str = BRANCH,
           grace_hours: float = GRACE_HOURS) -> dict:
    """Everything above, wired to this checkout. Buckets plus a `note`.

    The sidecars are read FIRST and an empty read returns immediately, before
    the corpus walk. `_site/` is 600-odd megabytes and CI has no farm branch at
    all, so the short circuit is what keeps this from taxing every deploy build
    for an answer it cannot give.
    """
    empty = {"unpaged": [], "in_flight": [], "ingredient": [], "no_spec": [],
             "paged": [], "note": "", "measurable": False}
    sidecars = read_sidecars(branch, repo)
    if not sidecars:
        return empty
    tokens, note = read_corpus(repo)
    result = audit(sidecars, read_consumers(os.path.join(repo, "pipeline", "jobs")),
                   tokens, datetime.now(timezone.utc), grace_hours)
    result["note"] = note
    result["measurable"] = True
    return result


def warn_line(result: dict) -> str:
    """One sentence for a build log, or "" when there is nothing to say.

    Empty rather than "0 unpaged" on a tree that cannot see the farm branch:
    a green line nobody can back up is worse than no line.
    """
    if not result.get("measurable"):
        return ""
    rows = result["unpaged"]
    if not rows:
        return ""
    worst = rows[0]
    return ("%d finished render%s nobody has shown him — oldest %s, %s old "
            "(python3 pipeline/unpaged.py)"
            % (len(rows), "" if len(rows) == 1 else "s",
               worst["task"], ago(worst["age_hours"])))


def ago(hours: float) -> str:
    if hours < 1:
        return "%d min" % round(hours * 60)
    if hours < 48:
        return "%.1f h" % hours
    return "%.1f days" % (hours / 24.0)


# ------------------------------------------------------------------------ cli

def _table(title: str, rows: list, show_consumer: bool = False) -> None:
    print("%s (%d)" % (title, len(rows)))
    if not rows:
        print("  none")
        return
    for r in rows:
        line = "  %-9s %-44s %2d file%s%s" % (
            ago(r["age_hours"]), r["task"][:44], r["artifacts"],
            " " if r["artifacts"] == 1 else "s",
            "" if r["runs"] == 1 else "  x%d runs" % r["runs"])
        if show_consumer and r.get("consumer"):
            line += "\n      for: %s" % " ".join(r["consumer"].split())[:96]
        print(line)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--branch", default=BRANCH)
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--grace", type=float, default=GRACE_HOURS,
                    help="hours a finished job may go unpaged before it counts")
    ap.add_argument("--all", action="store_true",
                    help="also list the ingredient and no-spec buckets")
    ap.add_argument("--since", type=float, default=0.0, metavar="HOURS",
                    help="only rounds that finished within this many hours — "
                         "the supervisor's view of what THIS pass left unpaged")
    a = ap.parse_args()

    r = survey(a.repo, a.branch, a.grace)
    if a.since:
        for bucket in ("unpaged", "in_flight", "ingredient", "no_spec", "paged"):
            r[bucket] = [x for x in r[bucket] if x["age_hours"] <= a.since]
    if not r["measurable"]:
        print("no job sidecars under %s:%s — nothing to audit from this "
              "checkout (a deploy clone has no farm branches)" % (a.branch, SIDECARS))
        return 0
    if r["note"]:
        print("note: %s\n" % r["note"])

    _table("RENDERED FOR HIM AND NEVER SHOWN", r["unpaged"], show_consumer=True)
    print()
    _table("IN FLIGHT — finished under %g h ago, still the firing lane's to page"
           % a.grace, r["in_flight"])
    if a.all:
        print()
        _table("INGREDIENTS — consumer is another artifact, not him",
               r["ingredient"], show_consumer=True)
        print()
        _table("NO SPEC ON DISK — the promise cannot be read", r["no_spec"])
    else:
        print("\n%d ingredient job(s) and %d without a spec, --all to list them."
              % (len(r["ingredient"]), len(r["no_spec"])))
    print("%d round(s) are reachable from a page he can open." % len(r["paged"]))

    if r["unpaged"]:
        print("\nUNPAGED: n=%d oldest=%s age=%.1fh"
              % (len(r["unpaged"]), r["unpaged"][0]["task"],
                 r["unpaged"][0]["age_hours"]))
    else:
        print("\nUNPAGED: n=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
