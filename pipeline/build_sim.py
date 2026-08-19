#!/usr/bin/env python3
"""banyan city, THE STUDIO — one page that shows the show being made.

Dad asked for the sim (2026-07-30) and it stays: the episode is a tree growing
leaves, our machines are buildings that glow while they render, the cloud GPU is
a cloud, the author's open decisions are quests, the people voting on the
reactions thread are citizens. Since 2026-08-03 the machines share one animated
"lot" that the real crew walks (the author, the author's dad, the AI steward,
plus actual thread commenters) — decoration may be charming, but every sprite
is somebody real. Pure CSS + emoji — the public-site CSP allows no external
asset, and nothing here needs JavaScript.

The stranger-eyes audit (2026-07-30) rebuilt the page's priorities:
  1. the episode plays FIRST — a visitor from TikTok came for a cartoon;
  2. every visible string is plain English (scene, final, waiting for…), model
     codenames only ever appear prefixed "animated by:";
  3. no internal log tokens, no task IDs, no unexplained pills;
  4. one primary action (watch), everything machine-facing below the fold.

Data comes from `build_status.py` (repo files) and the PUBLIC GitHub API only —
the deploy server has no local git refs and no `gh` CLI.

2026-08-07 — THE PAGE STOPPED LYING ABOUT THE MACHINES. Three lies were live,
and each one is fixed below rather than reworded:

  1. AGE. `machine_state()` read only the `HH:MM:SS` off a heartbeat line and
     compared it to today's clock, wrapping at 24 h — so a box last heard from
     on 29 July read "12 h ago". heartbeat.txt genuinely carries no date, but
     the worker pushes every line as its own commit, so the commit history of
     that one path IS the same log with the day attached. Ages now come from
     there and nowhere else; when that request fails the page says the date is
     unknown instead of inventing one. No machine is ever shown fresher than
     provable.
  2. LIVENESS. The heartbeat is written only while a task runs, so a powered,
     idle box read as offline. telemetry.json is published every five minutes
     regardless — it is now the primary "is it on" signal for any box that
     publishes one, with the heartbeat answering the different question of
     what it is DOING.
  3. "IN PRODUCTION". The heading printed the whole `tasks:` list, so a job
     nobody had started — and a finished job the queue file had not retired —
     both read as work happening now. Rendering is now what a MACHINE'S OWN LOG
     says: a fresh STARTED for that id with no DONE after it. Queued, finished
     today and blocked are three other lists, and each says so.
  4. THE FOOTER. It claimed the page is "rebuilt on every push and every half
     hour". Only the GitHub Pages mirror has that cron (pages.yml); banyan.city
     rebuilt on push and on nothing else — and since 2026-08-08 not even that,
     since a push only builds if it touched a site input (vercel.json's
     ignoreCommand). Two prior
     attempts argued over which half of that sentence to keep; the fix is to
     stop needing the sentence — every datum carries its own age, so no reader
     has to reason from the page's freshness to a fact's freshness, and the
     footer is true of either copy.

The queue's `backlog:` list is published for the first time here, grouped by
what each entry is waiting for, with its own `why` and estimate. Work that is
blocked is the honest shape of this project — a page that shows only what is
running shows an empty street and explains nothing.

And the page is now LIVE, on the pattern the telemetry charts proved: the
browser re-reads the queue, each machine's check-in log and each machine's
vitals for itself, so an open tab keeps up with the farm between deploys. The
build-time values stay in the HTML as the no-JavaScript answer, each labelled
with the age of the thing it describes.

2026-08-11 — THE REVAMP. Roman: "it has too much unnecessary stuff, its hard
to understand whats going on from a glance, i dont know what im supposed to
look at, the page isnt organised either." Two audits (source + stranger-eyes)
agreed on the shape, and this build is it:

  * The page reads in a visitor's question order: is it alive → what got made
    → the show → who is waiting on what → what it costs. A three-cell strip at
    the top answers the first three, with an honest as-of stamp — a snapshot,
    never a claim of "live".
  * THE WHOLE LOG, NOT THE COMMIT SUBJECTS. The counters used to read 30
    commit subjects per branch; box_runner's subjects drop the `task=` token
    and 30 commits reach back hours, so a night when the render box finished
    ten jobs printed "Rendering: nothing" over "runnable: 4" — four hand jobs
    that had in fact carried DONE lines since the day before. branch_log()
    now reads the raw heartbeat file (which carries everything) and dates its
    lines off one anchor commit, so finished work is finished, the box's own
    `idle ready=N` line gives the only queue depth this page can honestly
    know, and a STARTED older than JOB_FRESH_MINUTES is no longer "now".
  * Task ids never reach the page; tid_words() translates the id families
    into a stranger's words instead of printing the runner's own narration.
  * Died, per the audits: the queue record (a file dump styled as a page —
    the file itself is one link), the animated lot, the vitals row, the
    steps-and-costs table (stale since July), the laptop-disk section (the
    founder's own ruling on the tile, extended), the in-page telemetry charts
    (the history lives on /pulse), and the essay footer. The bandwidth
    accounting and the build meter live compactly under one footprint heading.
"""
import datetime
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
import build_commit  # noqa: E402  one source for "which commit built this"
import charts  # noqa: E402  the page's pictures, and the one beat-state palette
import proof_receipts  # noqa: E402  the bytes behind every per-beat claim
import repo_slug  # noqa: E402  one source for "which repo is this"
from site_theme import THEME_CSS  # noqa: E402  the one visual language

GH = repo_slug.GH_REPO            # pipeline/repo_slug.py — never hardcode the owner
API = repo_slug.API_URL
RAW = repo_slug.RAW_URL
CANONICAL = "https://banyan.city"
PAGE = "status.html"
# One name for this page, used in the <title>, the <h1> and our own nav.
PAGE_NAME = "the studio"
DESC = ("Sapling, the AI-animated micro-drama growing in Banyan City. This is the "
        "studio floor: episode 1 playing, every scene's state, the machines that "
        "render it, and what the author still has to decide.")

# The family's machines, named for people who do not live here.
MACHINES = {
    "m1pro": ("the studio laptop", "🏛"),
    "m2": ("the spare laptop", "🏢"),
    "msi": ("the fast-GPU laptop", "🏭"),
    "rtx5090": ("the big render house", "🏟"),
}
# NOT EVERY farm-results-* BRANCH IS A MACHINE. `farm-results-hand` is the
# channel a hand-run claims a queue task on (pipeline/claim_task.py) — there is
# no box behind it, so a building for it would publish a machine that is
# permanently "faded = not heard from", i.e. a dead render box that does not
# exist. It gets no building, no tile and no vitals.
#
# IT STILL HAS TO COUNT. "read_machines() drops these; nothing else about them
# changes" was the intent and was not the code: finished_recent(), task_ids_done()
# and live_now() all walked the machine list, so a job a person ran and
# claimed could never appear as finished, and its queue entry kept publishing
# itself as open after the work shipped. The work-list counters read the ledgers
# below alongside the machines and attribute them by name; queue_promoter has
# always read their DONE lines exactly as it reads a worker's.
LEDGERS = {"hand": "run by hand"}
NOT_A_MACHINE = set(LEDGERS)   # the keys alone, for readers that only ask "is this a box"
# How fresh a signal has to be before it is allowed to mean anything.
TELEMETRY_STALE_MINUTES = 15    # vitals are published every 5 min; 3 misses = stale
JOB_FRESH_MINUTES = 45          # a "STARTED" line older than this is not "now"
JUST_FINISHED_MINUTES = 30      # a machine that just handed work in is still warm

# ------------------------------------------------------------------ fetching ---
# NOTHING ON THIS PAGE MAY FAIL SILENTLY. The old `_get` swallowed every
# exception and returned "", so one rate-limited build rendered an empty street
# under a heading about our machines and nobody could tell (the
# invisible-buildings bug, 2026-07-30). Failures are collected here and printed
# on the page in words.
FETCH_ERRORS: list = []
BRANCH_LIST_LABEL = "the list of machine branches"


def _reason(exc) -> str:
    code = getattr(exc, "code", None)
    if code in (403, 429):
        return ("GitHub is rate-limiting this build — the public API allows 60 "
                "requests an hour without a login")
    if code:
        return f"GitHub answered HTTP {code}"
    return str(exc) or exc.__class__.__name__


def _fetch(url, label=None, absent_ok=False):
    """(text, status) where status is "ok", "absent" or "failed".

    THE THREE ARE NOT TWO. "The file is not there" and "we could not ask" have
    always collapsed into the same empty string here, and every caller that
    treated the result as data therefore published a guess as a fact. They are
    split at the source so no reader has to guess which one it got: `absent`
    only ever means a 404 the caller said it could live with, and everything
    else that goes wrong is `failed` and is printed on the page in words.
    """
    headers = {"User-Agent": "banyan-sim-build"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and url.startswith("https://api.github.com"):
        headers["Authorization"] = f"Bearer {token}"   # optional; raises the 60/hr cap
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode(), "ok"
    except Exception as e:
        if absent_ok and getattr(e, "code", None) == 404:
            return "", "absent"
        if label:
            FETCH_ERRORS.append((label, _reason(e)))
        return "", "failed"


def _get(url, label=None):
    """Fetch text. On failure return "" AND record a printable reason.

    `label` names the datum in a stranger's words; pass None only when the file
    being asked for is legitimately optional (not every machine publishes
    vitals), so a normal absence does not read as a fault.
    """
    return _fetch(url, label)[0]


def _api(path, label, absent_ok=False):
    """Parsed JSON, or None when we could not find out.

    With `absent_ok`, a 404 answers `[]` — the thing does not exist, which is a
    complete answer and not a failure. None is reserved for "we asked and do not
    know", and callers key their wording on the difference.
    """
    raw, status = _fetch(f"{API}{path}", label, absent_ok=absent_ok)
    if status == "absent":
        return []
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        FETCH_ERRORS.append((label, "GitHub's answer could not be read"))
        return None


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def _iso(s):
    """GitHub's `2026-08-05T02:59:53Z` → an aware datetime, or None."""
    try:
        return datetime.datetime.strptime(str(s), "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc)
    except Exception:
        return None


def age_words(then, now=None) -> str:
    """'4 min ago' · '2 days ago (5 Aug 02:59 UTC)' · 'date unknown'.

    Anything older than a day carries its absolute stamp as well, because
    "N days ago" is exactly where a reader stops being able to check us — and
    an uncheckable age is what this page had wrong.
    """
    if then is None:
        return "date unknown"
    now = now or utcnow()
    secs = max(0, int((now - then).total_seconds()))
    if secs < 90:
        s = "just now"
    elif secs < 5400:
        s = f"{secs // 60} min ago"
    elif secs < 129600:                       # up to 36 h, still countable in hours
        s = f"{secs // 3600} h ago"
    else:
        d = secs // 86400
        s = f"{d} day{'s' if d != 1 else ''} ago"
    if secs >= 86400:
        s += then.strftime(f" ({then.day} %b %H:%M UTC)")
    return s


def age_el(then, now=None) -> str:
    """An age that keeps counting after the build.

    Every age on this page is one of these, and each carries the instant it
    counts from. The build-time words are the answer with JavaScript off; with
    it on, the browser rewrites them from `data-at` — which is the honest way
    to have a live-looking number on a page that is a file. No datum's age is
    ever the page's age.
    """
    if then is None:
        return '<span class="age">date unknown</span>'
    return (f'<time class="age" datetime="{then.strftime("%Y-%m-%dT%H:%M:%SZ")}" '
            f'data-at="{int(then.timestamp())}">{html.escape(age_words(then, now))}</time>')


def farm_branches():
    """farm-results-* branches via the public API — the deploy server has no
    local refs (the invisible-buildings bug, 2026-07-30). If the API cannot be
    reached we fall back to every branch this file already knows by name, so the
    street is never silently empty; the missing datum is reported instead.

    THE FALLBACK HAS TO NAME THE LEDGERS TOO. It listed MACHINES alone, and
    every reader of a ledger — read_ledgers, and through it "Finished today",
    the done-id set and the rendering-now check — comes through this one
    function. So a rate-limited build did not merely lose the hand branch's
    tile (it has none); it published "Finished today: 0" on a day people had
    finished work by hand, and re-opened their queue entries as runnable. A
    zero that means "we could not ask" is the invisible-buildings bug again,
    one heading over.
    """
    data = _api("/branches?per_page=100", BRANCH_LIST_LABEL)
    if isinstance(data, list):
        names = sorted(b["name"] for b in data
                       if str(b.get("name", "")).startswith("farm-results-"))
        if names:
            return names
    return sorted(f"farm-results-{k}" for k in list(MACHINES) + list(LEDGERS))


def clock_of(line: str):
    """The `HH:MM:SSZ` a runner stamped at the head of a line, or None."""
    m = re.match(r"^(\d{2}):(\d{2}):(\d{2})Z(?:\s|$)", line or "")
    if not m:
        return None
    h, mi, s = (int(x) for x in m.groups())
    if h > 23 or mi > 59 or s > 59:
        return None
    return (h, mi, s)


def line_time(line: str, commit_when):
    """When a check-in line says IT happened, dated by the commit that carried it.

    A commit time is when a line was pushed. The `HH:MM:SSZ` at the head of the
    line is when the thing it reports happened, written by the runner at that
    moment — and the footer promises every age on this page counts from the
    moment its own datum was recorded. For these lines the stamp IS that moment;
    the commit only says when we got told. Courier pushes a machine's log on a
    cycle, and a person claiming a task by hand pushes whenever they get to it,
    so the gap is real and always in the same direction.

    Only the clock is on the line; the DAY comes from the commit, which is safe
    in the one direction that matters. A line cannot be committed before it is
    written, so a stamp landing AFTER its own commit was written the previous
    day and pushed past midnight — the two minutes of slack absorb clock skew
    between a box and GitHub, not a real interval. Past a day of lag there is
    nothing on the line to reconstruct from and the commit time stands, which is
    also what happens for farm_worker's subjects: it commits `hb: {stage}` and
    keeps the clock in the file, so those lines simply have no stamp to prefer.
    """
    m = re.match(r"^(\d{2}):(\d{2}):(\d{2})Z(?:\s|$)", line or "")
    if not m or commit_when is None:
        return commit_when
    h, mi, s = (int(x) for x in m.groups())
    if h > 23 or mi > 59 or s > 59:
        return commit_when
    stamped = commit_when.replace(hour=h, minute=mi, second=s, microsecond=0)
    if stamped - commit_when > datetime.timedelta(minutes=2):
        stamped -= datetime.timedelta(days=1)
    return stamped


def log_label(branch) -> str:
    """What a failed check-in read is called on the page — one spelling, because
    logs_unread() matches on it and a second spelling would silently stop
    matching."""
    return f"the check-in dates for {branch}"


def logs_unread() -> list:
    """The check-in logs this build asked for and did not get, by branch.

    "Nothing finished today" and "we could not find out what finished today" are
    different statements and the page had only ever been able to make the first.
    Everything that answers the work-list counters comes through the branch list
    and the per-branch log reads, so a failure in either means the counters do
    not know — and a counter that does not know must say so rather than print a
    zero. Read off FETCH_ERRORS, which is already the record of what failed.
    """
    out = []
    for lab, _why in FETCH_ERRORS:
        if lab == BRANCH_LIST_LABEL:
            name = "the branch list"
        elif lab.startswith("the check-in dates for "):
            name = lab.split("the check-in dates for ")[-1]
        elif lab.startswith("the check-in log for "):
            # branch_log reads the raw file AND the dating commit; a failure
            # of either means the counters do not know what that branch did.
            name = lab.split("the check-in log for ")[-1]
        else:
            continue
        if name not in out:   # the branch list is asked for once per reader
            out.append(name)
    return out


def branch_log(branch, absent_ok=False):
    """[(when, line)] newest first — a machine's WHOLE log, dated.

    THE FILE, NOT THE COMMIT SUBJECTS. The counters used to read the newest 30
    commit subjects per branch, and both halves of that lied at once on
    2026-08-11: box_runner's subjects drop the `task=` token the raw file
    carries (`hb: DONE ep2-b05-…` against `17:41:55Z DONE task=ep2-b05-… rc=0
    artifacts=8`), so a night of ten finished box jobs matched nothing — and
    30 commits reached back only hours, so four hand jobs whose DONE lines had
    sat in the file since the day before were re-published as "runnable". The
    raw file has every line, every token and every idle report; it is one
    fetch, and this page was already making it.

    DATING. The file carries a clock per line and no dates. One request buys
    the newest commit that touched the file — the anchor — and line_time dates
    the last line off it exactly as before. From there the file is walked
    BACKWARDS: each time a line's clock is later than the line after it, a
    midnight was crossed, so the day steps back by one. Appended logs are
    chronological, so this is reconstruction from order, not a guess. A line
    with no clock inherits its successor's time — never fresher than provable.
    If the anchor cannot be read the whole branch answers [], and the failure
    is already on FETCH_ERRORS for logs_unread() to report: an undated log
    must read as "we could not find out", never as an empty day.
    """
    raw, status = _fetch(f"{RAW}/{branch}/farm-out/heartbeat.txt",
                         f"the check-in log for {branch}", absent_ok=absent_ok)
    lines = [ln.rstrip() for ln in raw.splitlines() if ln.strip()]
    if status != "ok" or not lines:
        return []
    data = _api(f"/commits?sha={branch}&path=farm-out/heartbeat.txt&per_page=1",
                log_label(branch), absent_ok=absent_ok)
    anchor = None
    if isinstance(data, list) and data:
        anchor = _iso((data[0].get("commit") or {}).get("committer", {}).get("date"))
    if anchor is None:
        return []
    out = []
    when = line_time(lines[-1], anchor) or anchor
    out.append((when, lines[-1]))
    for ln in reversed(lines[:-1]):
        c = clock_of(ln)
        if c is not None:
            cand = when.replace(hour=c[0], minute=c[1], second=c[2],
                                microsecond=0)
            if cand > when:                 # walking back, later clock = day before
                cand -= datetime.timedelta(days=1)
            when = cand
        out.append((when, ln))
    return out


def telemetry_branch(branch: str) -> str:
    """`farm-results-rtx5090` → `farm-telemetry-rtx5090`.

    Vitals and render results are two writers, and since 2026-08-11 they have two
    branches (pipeline/telemetry.py). They shared one until the courier's
    force-push and the telemetry daemon's republish started starving each other —
    a night of lost courier pushes and ~20 minutes of stalled render claims.
    """
    return "farm-telemetry-" + branch.split("farm-results-")[-1]


def telemetry_head(branch):
    """{'at': when, 'gpu': name} — a machine's own five-minute pulse, or None.

    This file is written whether or not there is work to do, which is the whole
    point: it answers "is the box on", a question the heartbeat cannot answer
    because the heartbeat is only written while a task runs. Absence is normal
    (only the render box publishes one), so it is not reported as a failure.

    Two places are tried: the machine's telemetry branch, then its courier branch,
    which is where vitals used to live. The fallback is what carries the page
    across the split — the box's scheduled task is restarted by hand, so the last
    real sample sits in the old spot until someone re-enables it, and reading only
    the new branch would print "not heard from" about a machine that is fine.
    """
    for ref in (telemetry_branch(branch), branch):
        txt = _get(f"{RAW}/{ref}/telemetry.json", None)
        try:
            d = json.loads(txt)
            return {"at": datetime.datetime.fromtimestamp(float(d["last_sample"]),
                                                          datetime.timezone.utc),
                    "gpu": str(d.get("gpu_name") or "")}
        except Exception:
            continue
    return None


def queue_doc() -> dict:
    """The work list — `tasks:` (runnable now) and `backlog:` (waiting on
    something), read from the repo checkout this build was made from.

    Read LOCALLY on purpose. The queue file lives on `main` and the deploy
    server checks `main` out, so the local copy is exactly the commit being
    published: no request to spend, no rate limit to hit, and no way for a
    failed fetch to render an empty queue. The browser re-reads the same file
    over the network afterwards, which is where live-ness comes from.
    """
    import yaml as _yaml
    try:
        doc = _yaml.safe_load((REPO / "pipeline/farm-queue.yaml").read_text()) or {}
    except Exception as e:
        FETCH_ERRORS.append(("the work queue", f"the queue file could not be read ({e})"))
        return {"tasks": [], "backlog": [], "readable": False}
    tasks = doc.get("tasks")
    backlog = doc.get("backlog")
    # AN ENTRY THAT IS NOT A DICT IS NOT A NON-ENTRY. The two filters below have
    # always dropped them, which is right for every counter and every renderer —
    # none of them can read a bare string. But dropping is not the same as
    # knowing, and the entry-by-entry record exists precisely so the queue cannot
    # quietly publish 23 of its 24 rows. What was filtered is carried out with
    # the list it came from, and printed as a fault.
    dropped = [(name, i, repr(e)[:120])
               for name, lst in (("tasks", tasks), ("backlog", backlog))
               for i, e in enumerate(lst or []) if not isinstance(e, dict)]
    return {"tasks": [t for t in (tasks or []) if isinstance(t, dict)],
            "backlog": [b for b in (backlog or []) if isinstance(b, dict)],
            # `backlog:` is landing in a parallel change; its absence is not a
            # fault, and unknown keys inside an entry are ignored, not fatal.
            "has_backlog": isinstance(backlog, list),
            "dropped": dropped,
            "readable": True}


# ---- the queue's own words, in a stranger's ----------------------------------
# `why` and `gate_ref` are written by whoever queued the work, for whoever picks
# it up, and they use the studio's two internal words. The page has said "scene"
# and "final" everywhere else since the stranger-eyes audit, so the same two
# substitutions run over every queue string that reaches a visitor. Filenames
# stay: the repo IS the product, and a reader who wants to check us needs the
# path. Task ids never reach the page — those are log tokens.
_HOUSE = [
    # a task id is `slug-<epoch>`; the epoch is a log token and never published,
    # but the slug is how one queue entry refers to another and stays readable.
    (re.compile(r"\b([a-z][\w-]*?)-\d{9,}\b"), r"\1"),
    (re.compile(r"\bcanon swap\b", re.I), "swap of the final frame"),
    (re.compile(r"\bcanon\b", re.I), "final"),
    # a range stays plural, a single number goes singular: `beats 02-21` is
    # twenty scenes, `beats 1` is the field naming one.
    (re.compile(r"\bbeats?[- ](\d{1,2}\s*[-–]\s*\d{1,2})\b", re.I), r"scenes \1"),
    (re.compile(r"\bbeats?[- ](\d{1,2})\b", re.I), r"scene \1"),
    (re.compile(r"\bbeats\b", re.I), "scenes"),
    (re.compile(r"\bbeat\b", re.I), "scene"),
]


def plain(text) -> str:
    """House dialect, whitespace folded. Safe to run over any queue string."""
    s = " ".join(str(text or "").split())
    for pat, rep in _HOUSE:
        s = pat.sub(rep, s)
    return s


def first_sentence(s: str, limit: int = 190) -> str:
    """The first sentence, without cutting a word or mistaking an elision for a
    full stop. `002b-t0-c.yaml` and `wan_i2v.py` keep their dots — those are not
    followed by a space."""
    s = re.sub(r"\.{2,}", "…", " ".join(str(s or "").split()))
    first = re.split(r"\.\s+", s)[0].rstrip(". ")
    if len(first) > limit:
        first = first[:limit].rsplit(" ", 1)[0] + "…"
    return first


def excerpt(s: str, limit: int = 260) -> str:
    """A whole short paragraph, clamped to a width without cutting a word.

    `first_sentence` is the wrong instrument for text that asks two things. The
    review board writes about fifty words per entry, meant to be read at a
    glance, and its second sentence is regularly half the question — so one
    sentence of it is not a summary, it is an omission.
    """
    t = re.sub(r"\.{2,}", "…", " ".join(str(s or "").split()))
    if len(t) <= limit:
        return t
    return t[:limit].rsplit(" ", 1)[0] + "…"


def visitor_sentence(s: str, limit: int = 170) -> str:
    """One sentence, minus its parentheticals and backticks.

    The queue's asides are ledger record numbers, seed codes and filenames —
    written for the person clearing the gate, and exactly what the founder
    screenshotted as unreadable (2026-08-11). The sentence stays checkable;
    the clerical aside stays in the file.
    """
    s = re.sub(r"\s*\([^()]*\)", "", str(s or "")).replace("`", "")
    return first_sentence(s, limit)


def gate_note(entry: dict, limit: int = 190) -> str:
    """The blocker in one sentence — `gate_ref`'s first, minus its parentheses.

    gate_ref is written for the person who will clear the gate, so it carries
    registry paths and file:line. The first sentence is the fact; the rest is
    the instructions. A visitor gets the fact.
    """
    ref = plain(entry.get("gate_ref"))
    if not ref:
        return ""
    ref = re.sub(r"\s*\([^()]*\)", "", ref)            # parenthetical detail
    ref = re.sub(r"\s*—\s*$", "", ref).strip()
    return first_sentence(ref, limit)


GATE_WORDS = {
    "founder": ("🕰", "waiting on the author",
                "only the author can make these calls — taste, and what gets published"),
    "hardware": ("🔌", "waiting on a machine",
                 "a box is unreachable or cannot run the code; no render can start on it"),
    "code": ("🛠", "waiting on code",
             "the pipeline cannot do this yet — the missing piece is named"),
    "": ("▶️", "nothing is blocking it",
         "unblocked and unstarted: these need a person to run them, not a gate to open"),
}


def backlog_entry_view(b: dict) -> dict:
    """One backlog entry as the page shows it: what, why, how long, who runs it."""
    render_shaped = any(k in b for k in ("beats", "seeds", "video"))
    what = task_story(b)[0] if render_shaped else ""
    est = b.get("est_minutes")
    try:
        est = int(est)
    except (TypeError, ValueError):
        est = None
    runner = str(b.get("runner") or "").strip()
    window = str(b.get("window") or "").strip()
    wkey = str(b.get("worker") or "any")
    return {
        "gate": str(b.get("gate") or ""),
        "what": what,
        "why": plain(b.get("why")),
        "note": gate_note(b),
        "est": est,
        "window": window,
        "runner": runner,
        "machine": MACHINES.get(wkey, (wkey if wkey != "any" else "", ""))[0],
    }


def backlog_groups(backlog: list) -> list:
    """[(gate, emoji, heading, blurb, [views], total minutes)] — blocked first,
    founder before machines before code, unblocked last, because the page is
    read top-down and the author's five are the ones that move the show."""
    order = ["founder", "hardware", "code", ""]
    views = [(str(b.get("gate") or ""), backlog_entry_view(b)) for b in backlog or []]
    out = []
    for gate in order:
        rows = [v for g, v in views if g == gate]
        if not rows:
            continue
        emoji, head, blurb = GATE_WORDS[gate]
        mins = sum(r["est"] or 0 for r in rows)
        out.append((gate, emoji, head, blurb, rows, mins))
    for gate in sorted({g for g, _ in views} - set(order)):   # a gate word we do not know
        rows = [v for g, v in views if g == gate]
        out.append((gate, "⏳", f"waiting on {gate}", "", rows,
                    sum(r["est"] or 0 for r in rows)))
    return out


def hours_words(minutes: int) -> str:
    """'45 min' · 'about 1.8 h' — estimates, and never dressed as measurements."""
    if not minutes:
        return ""
    return f"{minutes} min" if minutes < 90 else f"about {minutes / 60:.1f} h"


def _shot_runs(beats: str) -> str:
    """'1,2,3,7,9,10' → '1–3, 7, 9–10' — a merged job names its shots as
    ranges, not as a fifteen-number recital."""
    nums = sorted({int(b) for b in beats.split(",") if b.strip().isdigit()})
    if not nums:
        return beats.replace(",", ", ")
    runs, start, prev = [], nums[0], nums[0]
    for n in nums[1:] + [None]:
        if n is not None and n == prev + 1:
            prev = n
            continue
        runs.append(str(start) if start == prev else f"{start}–{prev}")
        if n is not None:
            start = prev = n
    return ", ".join(runs)


def merge_queue(tasks: list) -> list:
    """Identical jobs that differ only in their shot number are ONE job to a
    reader. On 2026-08-03 the queue held fifteen single-beat rows and the page
    printed the same sentence fifteen times — display-only merge; the heartbeat
    matcher keeps the raw list, since a worker claims tasks by their full id."""
    merged, index = [], {}
    for t in tasks:
        fam = re.match(r"[a-z]+", str(t.get("id", "")))
        key = (fam.group(0) if fam else "",
               tuple(sorted((k, str(v)) for k, v in t.items()
                            if k not in ("beats", "id", "seed_base"))))
        if key in index:
            index[key]["beats"] = f'{index[key]["beats"]},{t.get("beats", "")}'
        else:
            t = dict(t)
            t["beats"] = str(t.get("beats") or "")
            index[key] = t
            merged.append(t)
    return merged


def task_story(t: dict) -> tuple:
    """(what, why) in a stranger's words, from a queue task's own fields."""
    tid = str(t.get("id", ""))
    beats = str(t.get("beats") or "").strip()
    shots = f"shot{'s' if ',' in beats else ''} {_shot_runs(beats)}" if beats \
        else "world scenery"
    seeds = int(t.get("seeds", 4))
    if tid.startswith("prod-open"):
        return (f"{seeds} candidate frames each for {shots}",
                "these shots are open requests — the author wants a better frame, and new takes feed the next vote")
    if tid.startswith("prod-hires"):
        w, h = t.get("width", 832), t.get("height", 1216)
        return (f"high-res ({w}×{h}) frames for {shots}",
                "sharper versions of finished scenes, for the author's picture-quality review")
    if tid.startswith(("keep", "ref")):
        return (f"{seeds} background-art studies ({str(t.get('slug', '')).replace('keep-', '').replace('-', ' ')})",
                "world-reference art — the bank every future shot borrows its look from")
    # VIDEO tasks fell through to the stills wording, so the page told everyone the
    # farm was making "4 frames for shots" while it spent an entire day animating
    # video (founder, 2026-08-02: "not synced"). A status page describing the wrong
    # KIND of work is worse than one that is merely late.
    if t.get("video"):
        model = {"animegen": "an anime-trained model",
                 "ltx-2.3": "an LTX video model",
                 "ti2v-5b": "Wan 2.2"}.get(str(t.get("video_model", "ti2v-5b")),
                                           str(t.get("video_model")))
        secs = t.get("seconds", 3.0)
        # NOT `t.get("steps", 20)`. A planned job that has not chosen its step
        # count would have been published as "at 20 steps" — a number nobody
        # wrote, on a page whose whole claim is that its numbers are checkable.
        steps = t.get("steps")
        n = len([b for b in beats.split(",") if b]) or 1
        if t.get("prefetch"):
            return ("downloading model weights",
                    "fetching a bigger video model to try later — no rendering, just the download")
        return (f"{n} moving clip{'s' if n != 1 else ''} ({secs:g}s each) for {shots}, "
                f"on {model}" + (f" at {steps} steps" if steps else ""),
                "animating stills the author already approved — the still is the "
                "composition, the render only decides what MOVES")
    return (f"{seeds} frames for {shots}", "queued by the studio")

def queue_row_story(t: dict) -> tuple:
    """(what, why) for one row of the RUNNABLE queue.

    Two corrections to calling task_story() straight, and the first is the one
    that would have printed a falsehood. task_story answers for RENDER work and
    assumes it: everything it does not recognise falls out of its last line as
    "N frames for world scenery", a sentence about four frames nobody asked for.
    backlog_entry_view has always guarded that call with these same three keys
    and shown the entry's own words instead when they are absent — but the
    runnable list called it unguarded, so the moment a hand-run was queued (a
    prompt sweep, a re-film, a diagnosis) this page would have described it as
    scenery frames. Same guard, same fallback, one heading over.

    Second, `why` is preferred over task_story's stock sentence wherever the
    entry wrote one. The queue file asks for `why` to be "one line a stranger
    understands, naming the consumer of the output" (farm-queue.yaml:84-85) and
    the blocked list below prints exactly that; the runnable list was throwing it
    away and publishing "queued by the studio" over the top of it, which is the
    one thing on this page nobody can check.
    """
    # TRUTHINESS, NOT KEY PRESENCE, and the difference is not cosmetic here.
    # backlog_entry_view can ask `k in b` because it reads raw entries; this
    # function runs on merge_queue output, and merge_queue sets `t["beats"] =
    # str(...)` on EVERY row it returns — so `"beats" in t` is true for all of
    # them, including the ones with no beats, and the guard above would never
    # have fired. Caught by building the page: the re-film row published itself
    # as "4 frames for world scenery" with the fix already in.
    if any(t.get(k) for k in ("beats", "seeds", "video")):
        what, stock = task_story(t)
    else:
        what = ("a job run by hand" if str(t.get("runner") or "") == "manual"
                else "a job for a machine")
        stock = ""
    return (what, plain(t.get("why")) or stock)


# ---------------------------------------------------------------- citizens ---
URL_RE = re.compile(r"\(?\bhttps?://\S+\)?")
VOTE_RE = re.compile(r"^\s*\d{1,2}\s*:")


def humanise(body: str) -> str:
    """A thread comment as a speech bubble: no markdown, no half-eaten URLs.

    The bubbles used to ship raw ('🗳 **Final two ballots** (board: https://ban…')
    which made the liveliest part of the page look broken.
    """
    # markdown links first: URL_RE would otherwise eat "(…)" and leave "[words]"
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", body or "")  # links/images → their words
    text = URL_RE.sub("", text)                                 # bare URLs, brackets and all
    text = re.sub(r"[*_`>#\[\]]+", "", text)                    # bold, headers, quotes, leftovers
    text = re.sub(r"\(\s*(board|thread|here)?\s*:?\s*\)", "", text)  # emptied parentheses
    # "(board: https://… )" loses its closing bracket with the URL, leaving an
    # orphaned "(board:" mid-sentence — drop any such label with no ")" ahead.
    text = re.sub(r"\(\s*[\w ]{0,14}:\s*(?![^()]*\))", "", text)
    text = " ".join(text.split())
    # a stripped URL can leave a sentence hanging on its conjunction ("… board and")
    text = re.sub(r"[\s,:;—-]*\b(and|at|in|on|see|via)?[\s,:;—-]*$", "", text)
    if len(text) > 96:                                          # truncate on a word
        text = text[:96].rsplit(" ", 1)[0] + "…"
    return text


def is_vote_tally(body: str) -> bool:
    """'06: lets use B. 07: A' — a private ballot log, unreadable out of context."""
    lines = [ln for ln in (body or "").splitlines() if ln.strip()]
    return bool(lines) and sum(1 for ln in lines if VOTE_RE.match(ln)) >= len(lines) / 2


def latest_thread_comments(n=3):
    """(author, sentence, permalink) for the newest readable comments."""
    raw = _get(f"https://api.github.com/repos/{GH}/issues/1/comments?per_page=100")
    try:
        cs = json.loads(raw)
    except Exception:
        return []
    out = []
    for c in reversed(cs):
        body = c.get("body") or ""
        if is_vote_tally(body):
            continue
        said = humanise(body)
        if not said:
            continue
        out.append((c.get("user", {}).get("login", "someone"), said,
                    c.get("html_url", f"https://github.com/{GH}/issues/1")))
        if len(out) == n:
            break
    return list(reversed(out))


# ---------------------------------------------------------------- machines ---
# Stage words a worker writes while it is mid-task. DONE and FAIL are the two
# lines that end a task, so they are the absence of work, not work.
WORK_WORDS = ("STARTED", "MODEL_LOADED", "VIDEO_VENV_OK", "VIDEO_DEPS_OK",
              "VIDEO_RENDERING", "VIDEO_ENCODING", "VIDEO_CLIP", "RENDERING",
              "ENCODING")


def job_words(tail: str, queue: list | None = None) -> tuple:
    """(what a working machine is making, why) — from the queue where possible.

    The epoch task ID never reaches the page, but it IS matched against the
    queue, so a rendering machine says what it is making and why it matters.
    """
    tid = re.search(r"task=([\w.-]+)", tail or "")
    entry = next((t for t in (queue or [])
                  if str(t.get("id")) == (tid.group(1) if tid else "")), None)
    if entry:
        return task_story(entry)
    scene = re.search(r"beats?=\s*(\d+)", tail or "")
    if scene:
        return (f"rendering scene {int(scene.group(1)):02d}",
                "the job is not in the published queue any more — this is what "
                "the machine's own log says it is on")
    return ("rendering", "the machine's log says it is working; the job is not "
                         "in the published queue, so the page will not guess at what")


def machine_state(tail: str, last_seen=None, telem=None, queue=None, now=None,
                  blocked: str = "") -> dict:
    """What one machine is doing, and how sure the page is allowed to be.

    TWO CLOCKS, AND THEY ANSWER DIFFERENT QUESTIONS.
      * telemetry.json is written every five minutes whether or not there is
        work → IS THE BOX ON.
      * heartbeat.txt is written only while a task runs → WHAT IS IT DOING, and
        its silence means "no job", not "no machine".
    Reading liveness off the heartbeat alone is why a powered, idle render box
    was published as offline (2026-08-07). `last_seen` is a real datetime from
    the commit that pushed the line — never parsed out of the line itself,
    which carries no date.

    `blocked` is the third state the old two-word vocabulary could not say: ON
    AND UNABLE. It comes from the queue's own hardware gates, so the page never
    invents a fault — it repeats the one the queue file already records against
    that machine. The render box is exactly this today: powered, publishing its
    vitals every five minutes, and unable to import torch at all.
    """
    now = now or utcnow()
    tel_age = None if not telem else (now - telem["at"]).total_seconds()
    hb_age = None if last_seen is None else (now - last_seen).total_seconds()
    on = tel_age is not None and tel_age < TELEMETRY_STALE_MINUTES * 60
    stage = (tail or "").split("Z", 1)[-1].strip()
    working = bool(tail) and any(w in tail for w in WORK_WORDS) \
        and "DONE" not in tail and "FAIL" not in tail
    fresh_job = hb_age is not None and hb_age < JOB_FRESH_MINUTES * 60

    seen = ("last check-in " + age_words(last_seen, now)) if last_seen or tail else \
        "no check-in has ever been read for this machine"
    if tail and last_seen is None:
        seen = ("last check-in date could not be read — GitHub did not answer, so "
                "this page will not put a number on it")
    pulse = ("publishing its own vitals, newest reading " + age_words(telem["at"], now)) \
        if telem else ""

    base = {"seen": seen, "pulse": pulse, "stage": stage, "raw": tail or "",
            "blocked": blocked}
    if working and fresh_job:
        what, why = job_words(tail, queue)
        return {**base, "css": "working", "chip": "rendering",
                "head": what, "why": why}
    if on and blocked:
        # The state the page could not previously say. "Offline" would be a
        # lie about a box that is answering every five minutes; "idle" would be
        # a lie about a box that cannot start a job at all.
        return {**base, "css": "idle", "chip": "on, cannot render",
                "head": "switched on, and unable to render",
                "why": blocked}
    if on:
        return {**base, "css": "idle", "chip": "on, nothing to render",
                "head": "switched on and asking for work",
                "why": "it reports its own temperature and memory every five "
                       "minutes; the queue has nothing it can run"}
    if hb_age is not None and hb_age < JUST_FINISHED_MINUTES * 60:
        return {**base, "css": "idle", "chip": "just finished",
                "head": "handed its last job in",
                "why": blocked or ""}
    return {**base, "css": "asleep", "chip": "not heard from",
            "head": "no sign of this machine",
            "why": blocked or ("off, asleep, or unable to reach GitHub — nothing "
                               "is claimed about it beyond when it was last heard")}


def machine_blocker(key: str, backlog: list) -> str:
    """The fault the QUEUE already records against this machine, in one line.

    Not a guess and not a hardcoded string: a `gate: hardware` entry names the
    machine it is waiting on in `worker`, and its `gate_ref` says what is wrong.
    If nobody has written a gate, the page claims no fault.
    """
    for b in backlog or []:
        if str(b.get("gate")) == "hardware" and str(b.get("worker")) == key:
            note = gate_note(b)
            if note:
                return note
    return ""


def read_machines(queue: list, backlog: list = None, now=None) -> list:
    """One record per machine: its branch, its state, and its dated log."""
    now = now or utcnow()
    out = []
    for branch in farm_branches():
        key = branch.split("farm-results-")[-1]
        if key in NOT_A_MACHINE:
            continue
        nice, emoji = MACHINES.get(key, (key, "🏠"))
        hist = branch_log(branch)
        tail = hist[0][1] if hist else ""
        telem = telemetry_head(branch)
        last_seen = hist[0][0] if hist else None
        out.append({"key": key, "branch": branch, "name": nice, "emoji": emoji,
                    "history": hist, "telemetry": telem, "last_seen": last_seen,
                    "tail": tail,
                    "state": machine_state(tail, last_seen, telem, queue, now,
                                           machine_blocker(key, backlog))})
    return out


def read_ledgers(now=None) -> list:
    """The non-machine ledger branches, shaped for the counters and nothing else.

    Deliberately carries no state, no telemetry and no emoji: there is no box
    here to be on or off, and any caller that tried to build a tile out of one
    of these should fail loudly rather than publish a machine that does not
    exist. `history` and `name` are what the counters need and all they get.

    Normally only branches the API actually listed are read: reaching for a
    ledger branch that has not been created yet would post a fetch failure on
    the page about a file nobody ever promised was there. The one exception is
    the fallback, where the API answered nothing at all and farm_branches names
    the ledgers from this file — the same assumption it has always made about
    the machines, and the cheaper of the two errors. A fetch note about a branch
    we could not read is a true statement; "nobody finished anything today",
    printed because we never asked, is not.
    """
    now = now or utcnow()
    out = []
    for branch in farm_branches():
        key = branch.split("farm-results-")[-1]
        if key not in LEDGERS:
            continue
        out.append({"key": key, "branch": branch, "name": LEDGERS[key],
                    "ledger": True,
                    "history": branch_log(branch, absent_ok=True)})
    return out


def hb_mark(line: str) -> str:
    """The MARK word of a check-in line, tolerating a leading clock.

    THE TWO WRITERS DISAGREE ABOUT THE COMMIT SUBJECT and both are defensible.
    farm_worker writes `{clock} {stage}` into the file and commits `hb: {stage}`
    — the file carries the clock, the commit carries the date. claim_task
    commits the whole file line, `hb: 12:00:00Z DONE task=… by-hand`, which is
    strictly more information. A reader keyed on `startswith("DONE")` reads the
    first and silently drops the second: not an error anywhere, just a finished
    job that does not exist as far as this page is concerned. Keying on the mark
    makes the two formats one, and keeps a future third writer from re-opening
    this by adding a prefix.
    """
    m = re.match(r"^(?:\d{2}:\d{2}:\d{2}Z\s+)?([A-Z][A-Z_]*)\b", line or "")
    return m.group(1) if m else ""


def hb_note(line: str) -> str:
    """The free text a check-in line carries beyond the format — a runner's own
    words about the job, or "" when it wrote none.

    Everything the format defines is stripped: the leading clock, the mark, the
    `task=<id>` token and the `by-hand` marker. What is left is a sentence
    somebody typed, and for a claim written after the fact it is the only place
    the evidence commit is named. farm_worker types nothing, so its lines answer
    "" here and the caller falls back as it always did.
    """
    rest = re.sub(r"^(?:\d{2}:\d{2}:\d{2}Z\s+)?[A-Z][A-Z_]*\b", "", line or "")
    rest = re.sub(r"\btask=[\w.-]+", "", rest)
    rest = re.sub(r"\bby-hand\b", "", rest)
    return " ".join(rest.split())


def finished_recent(records: list, now=None, hours: int = 24) -> list:
    """[(when, who, task id, note)] for every job that finished in the last
    `hours` — read off the machine's own dated log, so the window is a fact
    and not an inference from a clock time with no day attached.

    A ROLLING DAY, NOT "SINCE MIDNIGHT". The strip's question is "is this
    thing alive and what did it make", and a page read at 00:30 that answers
    "nothing today" about a night of work is technically true and completely
    misleading. `records` is the machines PLUS the ledgers (read_ledgers), so
    "who" is either a machine's name or "run by hand".
    """
    now = now or utcnow()
    span = datetime.timedelta(hours=hours)
    out = []
    for m in records:
        for when, line in m["history"]:
            if now - when >= span or hb_mark(line) != "DONE":
                continue
            tid = re.search(r"task=([\w.-]+)", line)
            out.append((when, m["name"], tid.group(1) if tid else "", hb_note(line)))
    # ONE ROW PER JOB, newest run wins. A retried id writes a DONE line per run
    # (scene 10 ran twice on 2026-08-11, to byte-identical frames) and a count
    # of lines would inflate "what got made" — the visitor's question is jobs,
    # not attempts. Lines with no id at all are kept as they come.
    seen, dedup = set(), []
    for row in sorted(out, reverse=True):
        if row[2] and row[2] in seen:
            continue
        seen.add(row[2])
        dedup.append(row)
    return dedup


def tid_words(tid: str) -> str:
    """A task id, translated into a visitor's words.

    Task ids are log tokens and never reach the page (stranger-eyes,
    2026-07-30) — but they are the ONE thing every check-in line reliably
    carries, and the ids most certain to have no queue entry left are the ones
    whose work most certainly shipped (the promoter retires on DONE). The old
    fallbacks printed either the raw id or the runner's own narration, and the
    narration is exactly what the founder screenshotted as unreadable. So the
    id families this studio actually mints are translated here, and anything
    unrecognised stays a generic sentence rather than leaking a token.
    """
    t = str(tid or "")
    if re.search(r"scoring|enqueue|cleanup|classify", t):
        return "bookkeeping on the render queue"
    m = re.match(r"(?:ep(\d+)|(\d{3})[a-z]?)-b(\d{1,2})\b", t)
    if m:
        ep = int(m.group(1) or m.group(2))
        kind = ("a moving take" if re.search(r"video|motion|i2v|ltx|clip|anim", t)
                else "a fresh frame")
        return f"{kind} for episode {ep}, scene {int(m.group(3)):02d}"
    if "probe" in t:
        return "a test clip for the motion recipe"
    if "sweep" in t:
        return "a prompt experiment"
    if "sample" in t:
        return "a one-off sample render"
    return "a studio job"


def done_story(task: dict, tid: str) -> str:
    """What a finished row calls the job it reports.

    The queue entry's own story wins when the file still holds a render-shaped
    entry — and ONLY then: task_story calls everything it does not recognise
    "frames for world scenery", which would be a falsehood about a job that
    released a lock. Everything else is the id translated. Never the runner's
    note: a claim note is written for the person clearing the gate, and rows
    built from notes are how record numbers and REVOKED filenames reached the
    public page.
    """
    if task and any(task.get(k) for k in ("beats", "seeds", "video")):
        return task_story(task)[0]
    return tid_words(tid)


def task_ids_done(records: list) -> set:
    """Every task id with a `DONE` line on any machine or ledger log, any date.

    The queue file is not self-clearing — an entry sits in `tasks:` until the
    promoter retires it — so a finished job would otherwise be published as
    still-queued. The heartbeat is the record of what actually happened; the
    queue is only the intent. That holds whoever ran it: the promoter retires an
    entry on a hand claim's DONE line, and a page that could not read the same
    line went on advertising the entry as runnable.
    """
    out = set()
    for m in records:
        for _when, line in m["history"]:
            if hb_mark(line) == "DONE":
                tid = re.search(r"task=([\w.-]+)", line)
                if tid:
                    out.add(tid.group(1))
    return out


def live_now(records: list, now=None) -> list:
    """[(when, who, task id)] — work in flight WHEN LAST HEARD, newest first.

    A job is live only when a runner's own log holds a fresh STARTED for its
    id with no DONE or FAIL after it. Two guards, each one a lie this page has
    actually told: the end-marks are checked per id (a heading that called the
    whole queue "in production" was the third lie of 2026-08-07), and a
    STARTED older than JOB_FRESH_MINUTES is not "now" — without the cutoff a
    runner that died mid-job reads as rendering forever.
    """
    now = now or utcnow()
    out = []
    for m in records:
        ended, listed = set(), set()
        for when, line in m["history"]:            # newest first
            tid = re.search(r"task=([\w.-]+)", line)
            if not tid:
                continue
            t, mark = tid.group(1), hb_mark(line)
            if mark in ("DONE", "FAIL"):
                ended.add(t)
            elif (mark == "STARTED" and t not in ended and t not in listed
                    and (now - when).total_seconds() < JOB_FRESH_MINUTES * 60):
                listed.add(t)
                out.append((when, m["name"], t))
    return sorted(out, reverse=True)


IDLE_RE = re.compile(r"\bidle ready=(\d+) failed=(\d+)")


def box_queue_depth(records: list):
    """(when, ready, failed, who) off the newest `idle ready=N failed=N` line,
    or None. The render box runs its OWN on-disk queue that this build cannot
    see — the box_runner reports its depth in every idle check-in, and that
    dated line is the one thing this page can honestly say about it. No line,
    no claim."""
    best = None
    for m in records:
        for when, line in m["history"]:            # newest first per record
            g = IDLE_RE.search(line)
            if not g:
                continue
            if best is None or when > best[0]:
                best = (when, int(g.group(1)), int(g.group(2)), m["name"])
            break
    return best


def read_box_queue() -> dict:
    """The supervisor's snapshot of the render box's own on-disk queue, or {}.

    Unreadable, absent or unparseable all come back the same way — empty — and
    every caller below treats empty as "say nothing", never as zero.
    """
    try:
        import yaml as _yaml
        with open(REPO / "pipeline/measured/box-queue.yaml", encoding="utf-8") as fh:
            doc = _yaml.safe_load(fh) or {}
        return doc if isinstance(doc, dict) else {}
    except Exception:
        return {}


ACK_FAILED_FILE = "pipeline/measured/failed-acknowledged.yaml"
ACK_FAILED_DOC = "pipeline/queue-failure-triage-0817.md"


def acknowledged_failures() -> int:
    """How many of the box's failed/ entries are triaged and written down.

    The chip under this used to read a flat red "39 sitting failed" — a true
    count that said nothing, because every one of the 39 had been diagnosed
    (33 in the triage doc, 6 in the compseed specs' own SUPERSEDED headers).
    Red that never goes out is red a reader learns to skip, so the acknowledged
    ids are committed and the page subtracts them.

    Counted off the LIST, never the file's `count:` — same contract as
    read_box_queue: unreadable, absent and unparseable all return 0, and 0 puts
    the chip back to the plain red count. On a failed read the page must
    over-report failures, never mark an unexamined one as known.
    """
    try:
        import yaml as _yaml
        with open(REPO / ACK_FAILED_FILE, encoding="utf-8") as fh:
            doc = _yaml.safe_load(fh) or {}
        rows = doc.get("acknowledged") if isinstance(doc, dict) else None
        if not isinstance(rows, list):
            return 0
        return sum(1 for r in rows if isinstance(r, dict) and r.get("id"))
    except Exception:
        return 0


def read_work_daily() -> dict:
    """The box's per-day machine time, or {} — same contract as read_box_queue.

    Written by `pipeline/box_work_daily.py` off the farm branch, because a
    deploy checkout has no farm branches to read. Empty means the chart is not
    drawn at all; a work chart with no bars would publish an idle farm on a
    failed read, which is the most misleading picture this page could show.
    """
    try:
        import yaml as _yaml
        with open(REPO / "pipeline/measured/box-work-daily.yaml",
                  encoding="utf-8") as fh:
            doc = _yaml.safe_load(fh) or {}
        return doc if isinstance(doc, dict) else {}
    except Exception:
        return {}


def review_inbox_open():
    """How many entries in `review/inbox.yaml` are still unanswered, or None.

    Roman, 2026-08-12: "i cannot find things to review on banyan.city/status."
    The inbox page had been live for hours and nothing on the page he lands on
    pointed at it. SITE.md makes that yaml the canonical list of what awaits
    him, so the count belongs at the top of this page and the link belongs with
    it.

    An entry is open until it carries `resolved:` — the same test regen.py
    applies, so the tile and the page it links to cannot disagree about the
    number. Missing, unreadable or the wrong shape all come back None, exactly
    as read_box_queue() refuses, and the caller says so in words. Zero is the
    one answer this must never invent: "nothing waiting" tells him to stop
    looking, which is the failure being fixed.
    """
    try:
        import yaml as _yaml
        with open(REPO / "review/inbox.yaml", encoding="utf-8") as fh:
            doc = _yaml.safe_load(fh)
        if not isinstance(doc, list):
            return None
        return sum(1 for e in doc if isinstance(e, dict) and not e.get("resolved"))
    except Exception:
        return None


def box_queue_eta(bq: dict):
    """The queue's depth in TIME, worked out at BUILD time and never stored.

    Roman, 2026-08-12: "on the banyan.city/status website i should be able to
    see how long the queue is in time as well."

    WHY THE ARITHMETIC IS HERE AND NOT IN THE FILE. A supervisor tick rewrites
    `ready`, `running` and `measured_at` every few minutes and does not
    re-measure anything else, so a total stored beside them would keep printing
    an old depth against fresh counts — the stale-meter failure the infra tile
    exists to prevent, moved one file over. Derived here, a tick that only
    moves the counts still moves the estimate.

    WHY IT IS PER KIND. Pooled over everything the box runs, "the median job"
    is not a quantity: it swings between roughly one minute and five on nothing
    but which window you take it over, because a motion take and a publish step
    are both "a job". Per kind the same measurements are steady — LTX takes sat
    at 4.7 min across 95 of them, stills at 0.9 across 99 — so when the
    snapshot says WHAT is queued this multiplies each kind by its own median.
    The kind counts have to account for every queued job before they are
    trusted; a mix that does not add up to ready+running is a snapshot written
    against a queue that has since moved, and it falls back rather than
    reporting a total for jobs it cannot see.

    WHAT IT REFUSES. No medians in the file, no estimate: `est_minutes` comes
    back None with `basis` None and the caller says so in words. `basis` is
    "kinds" for the per-kind sum and "rough" for the fallback, and the page
    must say which — an estimate that hides how coarse it is invites being read
    as a measurement.
    """
    if not isinstance(bq, dict) or not bq.get("measured_at"):
        return None

    def _num(v):
        try:
            f = float(v)
            return f if f > 0 else 0.0
        except (TypeError, ValueError):
            return 0.0

    def _int(key):
        try:
            return max(0, int(bq.get(key) or 0))
        except (TypeError, ValueError):
            return 0

    ready, running = _int("ready"), _int("running")
    jobs = ready + running
    med = bq.get("kind_medians")
    med = {str(k): _num(v) for k, v in med.items()} if isinstance(med, dict) else {}
    fallback = _num(bq.get("kind_median_fallback"))
    kinds = bq.get("queued_kinds")
    kinds = ({str(k): max(0, int(v)) for k, v in kinds.items()
              if str(v).lstrip("-").isdigit()} if isinstance(kinds, dict) else {})

    est, basis = None, None
    if jobs and kinds and sum(kinds.values()) == jobs and (med or fallback):
        total = sum(n * (med.get(k) or fallback) for k, n in kinds.items())
        if total > 0:
            est, basis = round(total), "kinds"
    if est is None and jobs and fallback:
        est, basis = round(jobs * fallback), "rough"
    return {
        "ready": ready, "running": running, "jobs": jobs,
        "kinds": kinds, "medians": med, "fallback": fallback or None,
        "est_minutes": est if jobs else (0 if (med or fallback) else None),
        "basis": basis,
        "sample": str(bq.get("median_from") or "").strip(),
        "measured_at": str(bq.get("measured_at")),
    }


def queue_time_words(eta: dict) -> str:
    """'about 1.2 h of work queued' · '' when the page may not put a time on it.

    Empty string is a real answer here and the caller must print something else
    in its place — never a bare number and never a zero standing in for a
    missing measurement.
    """
    if not eta or eta.get("est_minutes") is None:
        return ""
    if eta["jobs"] == 0:
        return "nothing queued"
    return f"{hours_words(max(1, eta['est_minutes']))} of work queued"


def queue_time_basis(eta: dict) -> str:
    """The one clause that says how good the number above it is.

    Every estimate on this page carries its own provenance in the same
    sentence, because the reader cannot go and check the box.
    """
    if not eta or not eta.get("basis"):
        return ""
    if eta["basis"] == "kinds":
        mix = ", ".join(f"{n} {k}" for k, n in sorted(eta["kinds"].items()))
        base = f"each queued job timed against others of its kind ({mix})"
    else:
        base = ("a rough one: the snapshot does not say what kind of jobs these "
                f"are, so it is {hours_words(max(1, round(eta['fallback'])))} "
                "a job across everything the box runs")
    return base + (f", from {eta['sample']}" if eta["sample"] else "")


# ---- the queue as a picture ---------------------------------------------------
# Roman, 2026-08-14: "can you make the queue more visuals and less text?" What
# stood here was three sentences a reader had to parse to learn a number they
# could have SEEN — "the render box's own queue: 1 rendering, 3 waiting · an
# estimated ~5 min of work queued, each queued job timed against others of its
# kind". Depth is now a row of blocks, one per job; the sentences that survive
# are one line each, and the methodology sits in a fold.
#
# WHAT A BLOCK CAN AND CANNOT SAY. The box publishes COUNTS BY KIND, never a
# list of the jobs still waiting, so a waiting block knows what kind of work it
# is and nothing else — no beat, no node, no name. Only the running job has a
# record, and only the running block's tooltip names one. A beat number invented
# for a waiting block would be this page making up the very thing it exists to
# report.
#
# AND THEY ARE ALL GREEN. The colour law is the machine's work in --leaf and the
# author's in --sap, so every block in this strip is a green: a queued render is
# waiting on a card, not on a person, and an amber block here would say the
# opposite of what is true. Kinds are separated by the three green steps plus a
# key underneath, never by hue alone.
QUEUE_KIND_CSS = {"ltx": "k-ltx", "still": "k-still", "charref": "k-charref",
                  "inpaint": "k-inpaint"}
# Singular, for one block's tooltip. charts.KIND_WORDS is the plural set the key
# uses; each phrase is written once so the strip and its key cannot drift.
QUEUE_KIND_ONE = {"ltx": "a motion take", "still": "a still frame",
                  "charref": "a character sheet", "inpaint": "an inpainting pass"}
QUEUE_UNKNOWN_ONE = "a queued job the snapshot does not name the kind of"
QUEUE_UNKNOWN_MANY = "of a kind the snapshot does not name"
QUEUE_BLOCK_CAP = 48   # past this it is a texture, not a count — the rest is words
# The no-JS floor for the running-job card. A build genuinely cannot know what a
# card picked up after it ran, so it says that rather than drawing a beat number
# out of a snapshot that is minutes old by the time anyone loads the page.
QNOW_BAKED = (
    '<div class="qnow" id="q-now">'
    '<p class="mono" id="q-now-note">Which beat the card has on it right now is '
    'read by your browser from the box’s own five-minute publish. With '
    'JavaScript off there is nothing here to read — a build cannot know what a '
    'machine picked up after it ran.</p></div>')


def queue_blocks(kinds: dict, ready: int, running: int, running_kind=None,
                 cap: int = QUEUE_BLOCK_CAP) -> tuple:
    """(blocks, hidden, counts) for the strip — one entry per queued job.

    The running job leads, then the waiting ones grouped by kind. Jobs the kind
    counts do not account for are drawn in the neutral colour rather than
    dropped: a strip shorter than the count printed beside it is a worse picture
    than an honestly unlabelled block. A mix that does not add up is a reading
    of a queue that moved while it was being read — ordinary, and not a fault.
    """
    jobs = max(0, int(ready or 0)) + max(0, int(running or 0))
    left = {str(k): max(0, int(v)) for k, v in (kinds or {}).items()
            if str(v).lstrip("-").isdigit()}
    n_run = max(0, int(running or 0))
    blocks = []
    for i in range(n_run):
        k = str(running_kind) if (i == 0 and running_kind
                                  and left.get(str(running_kind))) else None
        if k is None:
            k = next((kk for kk, n in sorted(left.items(), key=lambda kv: -kv[1])
                      if n), None)
        if k:
            left[k] -= 1
        blocks.append({"kind": k, "running": True})
    for k in sorted(left):
        blocks.extend({"kind": k, "running": False} for _ in range(left[k]))
    while len(blocks) < jobs:
        blocks.append({"kind": None, "running": False})
    blocks = blocks[:jobs]          # an over-counting mix is trimmed to the count
    counts = {}
    for b in blocks:
        counts[b["kind"]] = counts.get(b["kind"], 0) + 1
    return blocks[:cap], max(0, len(blocks) - cap), counts


def queue_block_class(kind) -> str:
    if not kind:
        return "k-unknown"
    return QUEUE_KIND_CSS.get(str(kind), "k-other")


def queue_block_words(b: dict) -> str:
    """One block's tooltip — what it is, and whether a card has it now."""
    kind = b.get("kind")
    what = (QUEUE_KIND_ONE.get(str(kind), f"a {kind} job") if kind
            else QUEUE_UNKNOWN_ONE)
    return ("rendering now — " if b.get("running") else "waiting — ") + what


def queue_strip_html(blocks: list, hidden: int = 0, sid: str = "q-strip",
                     extra: str = "",
                     idle: str = "card idle — nothing queued, nothing rendering"
                     ) -> str:
    """The depth, seen rather than read. Empty is a STATE, never a bare zero."""
    extra = f" {extra}" if extra else ""
    if not blocks:
        return (f'<div class="qstrip{extra} empty" id="{sid}">'
                f'<span class="qidle">{_e(idle)}</span></div>')
    cells = "".join(
        f'<span class="qblk {queue_block_class(b.get("kind"))}'
        + (" run" if b.get("running") else "")
        + f'" title="{_e(queue_block_words(b))}"></span>' for b in blocks)
    if hidden:
        cells += (f'<span class="qblk qplus" title="{hidden} more queued job'
                  f'{"s" if hidden != 1 else ""}, not drawn">+{hidden}</span>')
    n, run = len(blocks) + hidden, sum(1 for b in blocks if b.get("running"))
    label = (f'{n} job{"s" if n != 1 else ""} on the render box, {run} rendering '
             '— one block each, colour by kind')
    return (f'<div class="qstrip{extra}" id="{sid}" role="img" '
            f'aria-label="{_e(label)}">{cells}</div>')


def queue_head_html(eta) -> str:
    """The queue's headline number — the old glance tile, moved not copied.

    It lived in the summary strip until 2026-08-14, when the queue itself went
    to the top of the page and the cell became the same sentence twice. The ids
    are the load-bearing part: LIVE_JS rewrites `q-tile-n` and `q-tile-l` from
    the box's own publish, so what is baked here is the no-JS floor and not the
    number most readers see.
    """
    if eta and eta["est_minutes"] and eta["jobs"]:
        n, cls = "~" + _e(hours_words(max(1, eta["est_minutes"]))), "sn"
        lab = ('of work queued on the render box · '
               + ('an estimate, and a rough one: a median job times the count'
                  if eta["basis"] == "rough" else
                  'an estimate, each job timed against past jobs of its kind'))
    elif eta and eta["jobs"]:
        n, cls = str(eta["jobs"]), "sn"
        lab = ('jobs on the render box · no job times have been measured, '
               'so this page will not say how long that is')
    elif eta:
        n, cls = "0", "sn zero"
        lab = 'nothing queued on the render box as of its last measured snapshot'
    else:
        n, cls = "not read", "sn none"
        lab = ('the render box’s queue snapshot could not be read this build, '
               'so its depth is not claimed either way')
    return (f'<span class="{cls}" id="q-tile-n">{n}</span>'
            f'<span class="sl" id="q-tile-l">{lab}</span>')


def queue_legend_html(counts: dict, lid: str = "q-legend") -> str:
    """The key. Colour alone never carries a difference on this site — the same
    rule the charts follow, and the reason every block also has a tooltip.

    Always emitted, empty or not: LIVE_JS refills it from a newer reading than
    the build had, and an element that is not there cannot be refilled. CSS
    hides it while it is empty.
    """
    keys = ""
    for k, n in sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0] or "zz"))):
        word = (charts.KIND_WORDS.get(str(k), str(k)) if k else QUEUE_UNKNOWN_MANY)
        keys += (f'<span class="qkey"><i class="qsw {queue_block_class(k)}"></i>'
                 f'{n} {_e(word)}</span>')
    return f'<div class="qlegend" id="{lid}">{keys}</div>'


# ---- the queue's states ------------------------------------------------------
# The entry-by-entry record LEFT this page in the 2026-08-11 revamp: it was a
# file dump styled as a page, and its one honest job — "diff me against the
# file" — is done better by the one link to the file itself. What stays is the
# classifier, because the work-list counters and the queue-file footer line are
# built on it and must never disagree with each other.

# state → (emoji, word, what the word is claiming). Every one of these is read
# off a file: the list an entry sits in, its `gate`/`after` keys, or a check-in
# line on a farm-results-* branch. None of them is a guess about a machine.
QSTATES = {
    "running":  ("🔴", "RUNNING",
                 "a check-in log holds STARTED for this id with no DONE after it"),
    "failed":   ("💥", "FAILED",
                 "the newest check-in line for this id is a FAIL — the entry stays "
                 "queued and nothing has retired it"),
    "runnable": ("▶️", "RUNNABLE",
                 "sitting in tasks: — the next machine that polls the queue may "
                 "claim it without anyone deciding anything"),
    "waiting":  ("⛓", "WAITING ON ANOTHER JOB",
                 "in tasks:, but `after:` names work with no DONE line yet"),
    "blocked":  ("⛔", "BLOCKED",
                 "in backlog: with a gate — no worker can see it and the promoter "
                 "cannot clear it; a person deletes the key in a commit"),
    "planned":  ("🗒", "PLANNED",
                 "in backlog: with nothing blocking it — but backlog: is invisible "
                 "to every worker, so it needs promoting or running by hand"),
    "done":     ("✅", "DONE",
                 "a check-in log holds DONE for this id; the entry is still in the "
                 "file until the promoter's next run retires it"),
}


def claim_lines(records: list) -> dict:
    """task id → [(when, mark, who, note)], newest first, off every check-in log.

    live_now() and task_ids_done() each walk the same histories for one
    question apiece; the classifier needs all of it — when a job started, when
    it ended, which runner, and whatever the runner typed. Same `records` list
    (machines PLUS the hand ledger), so a job a person claimed is a job claimed.
    """
    out = {}
    for m in records:
        for when, line in m["history"]:
            tid = re.search(r"task=([\w.-]+)", line)
            if not tid:
                continue
            out.setdefault(tid.group(1), []).append(
                (when, hb_mark(line), m["name"], hb_note(line)))
    for v in out.values():
        v.sort(key=lambda r: r[0], reverse=True)
    return out


def queue_entry_state(e: dict, listname: str, claims: dict, done_ids: set) -> str:
    """Which of QSTATES this entry is in, decided newest-evidence-first.

    A check-in line outranks the list the entry sits in, and that ordering is the
    whole point: the queue file is intent, the heartbeat is what happened, and an
    entry stays in `tasks:` after it finishes until the promoter retires it. The
    NEWEST decisive mark wins rather than "any DONE anywhere", so a re-queued id
    that failed after an old success reads FAILED and not DONE.
    """
    lines = claims.get(str(e.get("id") or ""), [])
    newest = next((m for _w, m, _who, _n in lines
                   if m in ("STARTED", "DONE", "FAIL")), "")
    if newest == "DONE":
        return "done"
    if newest == "FAIL":
        return "failed"
    if newest == "STARTED":
        return "running"
    if listname == "backlog":
        return "blocked" if str(e.get("gate") or "").strip() else "planned"
    after = e.get("after") or []
    if isinstance(after, str):
        after = [after]
    if any(str(a) not in done_ids for a in after):
        return "waiting"
    return "runnable"




# ------------------------------------------------------------------- pieces ---
def _e(s):
    return html.escape(str(s))


def _and_list(items) -> str:
    """`a`, `a and b`, `a, b and c` — names in a sentence, not a bare count."""
    items = [str(i) for i in items]
    if len(items) <= 1:
        return items[0] if items else ""
    return ", ".join(items[:-1]) + " and " + items[-1]


def scene_list_html(rows: list) -> str:
    """One line per scene, no table — a 5-column grid was unreadable at 390px
    and `overflow-x:hidden` on <body> silently clipped it. Columns that are
    empty for every scene are simply not written."""
    from build_status import request_url
    items = []
    for r in rows:
        bits = []
        if r["animations"]:
            bits.append("animated by: " + ", ".join(r["animations"]))
        if r["candidates"]:
            bits.append(f'{r["candidates"]} rival frames tried')
        if r["waiting_for"]:
            bits.append("waiting for " + r["waiting_for"])
        meta = " · ".join(bits)
        chip = ('<span class="chip trunk">approved</span>' if r["final"]
                else '<span class="chip hot">in progress</span>')
        ask = ""
        if r["request"]:  # one honest link instead of a bare issue number
            ask = f' <a href="{_e(request_url(r["request"]))}">open request &rarr;</a>'
        items.append(
            f'<li><b>Scene {r["num"]:02d} · {_e(r["name"])}</b> {chip}'
            + (f'<div class="mono">{_e(meta)}{ask}</div>' if meta or ask else "")
            + "</li>")
    return f'<ol class="scenes">{"".join(items)}</ol>'


def _since_dt(v):
    """`since: 2026-07-29` → a datetime at UTC midnight. yaml hands back a date."""
    if isinstance(v, datetime.datetime):
        return v if v.tzinfo else v.replace(tzinfo=datetime.timezone.utc)
    if isinstance(v, datetime.date):
        return datetime.datetime(v.year, v.month, v.day, tzinfo=datetime.timezone.utc)
    try:
        return datetime.datetime.strptime(str(v)[:10], "%Y-%m-%d").replace(
            tzinfo=datetime.timezone.utc)
    except Exception:
        return None


def waiting_words(since, now=None) -> str:
    """'waiting 9 days' — the number that makes the queue's oldest item visible.

    An inbox with no ages reads as a to-do list. With them it reads as what it
    is: five calls, the oldest of them made nine days ago, with real work
    parked behind each one.
    """
    d = _since_dt(since)
    if d is None:
        return "waiting — no date recorded"
    now = now or utcnow()
    days = max(0, (now.date() - d.date()).days)
    if days == 0:
        return "asked today"
    return f"waiting {days} day{'s' if days != 1 else ''}"


def founder_gate_map(backlog: list, pending_ids: list) -> dict:
    """{pending id: [backlog entries gated on it]} — read out of `gate_ref`.

    A gate_ref names its blocker by id, and some entries name a SIBLING entry
    instead of naming the inbox item twice ("the same frame pick as …"), so the
    reference is followed one link at a time until it lands on an inbox id or
    runs out. Nothing is inferred from wording — an entry whose gate_ref names
    no id at all stays unattached, and the page says so rather than guessing.
    """
    entries = [b for b in (backlog or []) if isinstance(b, dict)]
    ids = [str(p) for p in pending_ids if p]
    owner: dict = {}
    for b in entries:
        ref = str(b.get("gate_ref") or "")
        hit = next((p for p in ids if p in ref), None)
        if hit:
            owner[str(b.get("id"))] = hit
    for _hop in range(len(entries)):                 # follow sibling references
        grew = False
        for b in entries:
            bid = str(b.get("id"))
            if bid in owner:
                continue
            ref = str(b.get("gate_ref") or "")
            for other in entries:
                oid = str(other.get("id"))
                if oid != bid and oid in ref and oid in owner:
                    owner[bid], grew = owner[oid], True
                    break
        if not grew:
            break
    out: dict = {p: [] for p in ids}
    for b in entries:
        p = owner.get(str(b.get("id")))
        if p:
            out[p].append(b)
    return out


def review_pointer(n_open) -> str:
    """One line naming what the section below it is, and where it gets answered.

    IT USED TO DESCRIBE A SUBSET, and that stopped being true. Two lists of
    founder calls existed: `review/inbox.yaml`, which SITE.md makes canonical,
    and `pipeline/pending-founder.yaml`, the older public one this section
    rendered — so this line had to warn a reader that the first list he met was
    not all of it. That file was retired on 2026-08-14 and the section now
    renders the canonical board's open entries, so the warning would itself be
    the stale claim on the page: there is one list, this is it.

    The count comes from `review_inbox_open()` and the entries from
    `build_status.inbox()` — one file, one `resolved:` test — so a number here
    that disagreed with the number of items below it would mean one of the two
    had stopped reading the board. That is not hypothetical: it is what the page
    did until 2026-08-19, when this line said two things were waiting over a
    list of four answered ones.
    """
    if n_open:
        head = (f'<b>{n_open} thing{"s" if n_open != 1 else ""}</b> are waiting'
                if n_open != 1 else '<b>1 thing</b> is waiting')
    else:
        head = 'What is waiting'
    return (f'{head} — every open call on the author’s board, in full, and '
            'nothing he has already answered. Answers land on '
            '<a href="review">the review inbox &rarr;</a>, which carries this '
            'same list with the verdicts already given underneath it')


def waiting_html(inbox: list, backlog: list, now=None) -> str:
    """The author's decision queue, with the age of each wait and the work
    parked behind it. Read-only for everyone else — the old board offered five
    identical gold 'look →' links for calls a visitor cannot make.

    AN ANSWERED CALL CANNOT BE RENDERED HERE, whoever hands it in. The reader
    (`build_status.inbox()`) already drops anything carrying `resolved:`, and
    this refuses it a second time on the way out, because the four stale cards
    the founder screenshotted on 2026-08-19 reached the page through a supplier
    that did no filtering at all — a retired snapshot file, every entry of it
    resolved. The invariant belongs to the section, not to one of its sources:
    the day a third list feeds it, it inherits the guard for free.
    """
    inbox = [q for q in (inbox or [])
             if isinstance(q, dict) and not q.get("resolved")]
    if not inbox:
        return '<p class="notice">Nothing waiting — the city runs itself today.</p>'
    now = now or utcnow()
    blocked = founder_gate_map(backlog, [q.get("id") for q in inbox])
    out = []
    for q in inbox:
        link, label = q.get("public"), "look at it &rarr;"
        if link and "/tree/" in link:      # a directory of .md files is not a page
            label = "read it on GitHub &rarr;"
        # An item can name what is behind its link. It must, when the decision is
        # about something unpublished: a generic "look at it" under a title like
        # "watch the finished remake" promises the link IS the remake, and on
        # 2026-08-06 it sent the author to the published older cut instead.
        if q.get("link_text"):
            label = f'{_e(q["link_text"])} &rarr;'
        a = f' <a href="{_e(link)}">{label}</a>' if link else ""
        held = [backlog_entry_view(b) for b in blocked.get(str(q.get("id")), [])]
        mins = sum(h["est"] or 0 for h in held)
        tail = ""
        if held:
            jobs = "; ".join(visitor_sentence(h["why"], 150) for h in held if h["why"])
            tail = (f'<div class="held"><b>{len(held)} job'
                    f'{"s" if len(held) != 1 else ""} parked behind this call</b>'
                    + (f' · {_e(hours_words(mins))} of machine time' if mins else "")
                    + (f'<br>{_e(jobs)}' if jobs else "") + "</div>")
        # The whole of the board's own line, clamped to a width. This printed
        # the FIRST SENTENCE ONLY, and the 2026-08-11 audits that asked for that
        # were right about the source they audited: the retired
        # pending-founder.yaml wrote 150-word paragraphs and one sentence was a
        # mercy. The board writes fifty, and cutting them at the first full stop
        # loses half of what he is being asked — on 2026-08-19 the one genuinely
        # open taste call reached this page carrying "Second half of the same
        # question: MAY THE GOBLIN READ AS A PLAIN GREEN MAN?" as its second
        # sentence, and the page showed him only the first.
        out.append(f'<li><span class="waited">{_e(waiting_words(q.get("since"), now))}'
                   f'</span> <b>{_e(q.get("title", ""))}</b>{a}'
                   f'<div class="mono">{_e(excerpt(q.get("detail")))}'
                   f'</div>{tail}</li>')
    return f'<ol class="quests">{"".join(out)}</ol>'


def backlog_html(backlog: list) -> str:
    """The planned-but-blocked list, grouped by what each group is waiting for."""
    groups = backlog_groups(backlog)
    if not groups:
        return ('<p class="notice">The backlog is empty — every planned job has '
                'either run or been dropped.</p>')
    out = []
    for _gate, emoji, head, blurb, rows, mins in groups:
        items = ""
        for r in rows:
            meta = [b for b in (
                hours_words(r["est"]),
                r["machine"],
                "a person runs this by hand" if r["runner"] == "manual" else "",
                "runs while nobody needs the machine" if r["window"] == "overnight" else "",
            ) if b]
            # One sentence per line, per the 2026-08-11 audits: `why` and the
            # gate note are written for whoever clears the gate, and the whole
            # paragraph on the public page is what the founder screenshotted.
            items += ('<li>'
                      + (f'<b>{_e(r["what"])}</b><br>' if r["what"] else "")
                      + (f'<span class="why">{_e(visitor_sentence(r["why"], 170))}</span>'
                         if r["why"] else "")
                      + (f'<div class="mono">blocked by: {_e(r["note"])}</div>'
                         if r["note"] else "")
                      + (f'<div class="mono">{_e(" · ".join(meta))}</div>' if meta else "")
                      + "</li>")
        out.append(f'<div class="bgroup"><h3>{emoji} {_e(head)} '
                   f'<span class="count">{len(rows)}</span></h3>'
                   + (f'<p class="mono">{_e(blurb)}'
                      + (f' · {_e(hours_words(mins))} of work' if mins else "")
                      + "</p>")
                   + f'<ol class="blist">{items}</ol></div>')
    return "".join(out)


def quest_board_html(rows: list) -> str:
    """Open quests anyone can take. An 'art quest' is a real open render
    request from requests.yaml; the two standing quests are the routes that
    always exist. The reward line states what actually happens — a take lands
    on the public board and the author may make it the scene — because a
    promised prize the repo cannot pay would fail the honesty gate."""
    from build_status import request_url
    open_reqs = [r for r in rows if r["request"]]
    # the brief and the reward are the same for every art quest — say them ONCE,
    # or the board repeats one sentence seven times (the fifteen-identical-rows
    # lesson, again)
    note = ""
    if open_reqs:
        note = (f'<p class="qnote">🎨 <b>Art quests</b> — the author wants a better frame '
                f'than the current one for {len(open_reqs)} scenes. Make one — any tool, '
                'any style that fits — and hand it in. '
                '<span class="reward"><b>reward</b> · your take goes on the public board; '
                'if the author picks it, your frame IS the scene, credited</span></p>')
    cards = [
        f'<div class="quest slim"><span class="chip hot">🎨 art quest</span>'
        f'<b>Scene {r["num"]:02d} · {_e(r["name"])}</b>'
        f'<a href="{_e(request_url(r["request"]))}">take this quest &rarr;</a></div>'
        for r in open_reqs]
    cards.append(
        '<div class="quest"><span class="chip">✍️ writing quest</span><br>'
        '<b>Write episode 2 yourself</b>'
        '<p>The story branches. Take the tree, grow your own limb — the right '
        'to branch is the one rule that can never be cut.</p>'
        '<div class="reward"><b>reward</b> · your branch lives in the city, '
        'under your name, forever</div>'
        '<a href="create.html">take this quest &rarr;</a></div>')
    cards.append(
        '<div class="quest"><span class="chip">🗳 citizen quest</span><br>'
        '<b>Say what you think</b>'
        '<p>Reactions on the public thread are what the story grows toward — '
        'they decide which branch becomes the trunk.</p>'
        '<div class="reward"><b>reward</b> · the next episode bends toward '
        'what the crowd asked for</div>'
        f'<a href="https://github.com/{GH}/issues/1">take this quest &rarr;</a></div>')
    return f'{note}<div class="qboard">{"".join(cards)}</div>'


def episode_eta_html(rows) -> str:
    """“When will episode 2 be finished” — the half of it a machine can answer.

    Founder, 2026-08-13: "lets start working on ETA, basically the estimated
    time we finish something, so we have a good idea of for example when we will
    finished episode 2, this is an important feature."

    And on the first version of this section, 2026-08-13: "im not seeing any eta
    ... except this which isn't the best". He found it and could not read it. It
    had shipped as a paragraph — run-on monospace prose, the numbers buried
    mid-sentence, decision titles chopped off with ellipses. The data was right
    and illegible, which on a page whose whole job is being read is the same as
    being wrong. This is the rebuild: one card per episode in the glance strip's
    own tile vocabulary, a bar showing where the beats actually are, and the
    three numbers he would act on, each linked to the place it gets answered.

    THE SECTION PRINTS TWO CLOCKS AND NEVER ADDS THEM. Machine time is measured:
    the box has written down when 337 jobs started and stopped. Decision time is
    a person, and a person is not a quantity — the same call in this project has
    taken four minutes and it has taken three days. One blended number would put
    a date on the page whose error bar is the author's week, and it would be
    read as a promise the moment it appeared. So the card shows the rendering
    left, and names the calls that rendering waits behind, and lets the reader
    do the addition with their own knowledge of how fast those get answered.

    THE BAR IS THE ARGUMENT, and it is why this reads in one second where the
    paragraph did not. Green is the machine's business (passed, still to render);
    amber is his (a take waiting for a look, a call waiting to be made). Episode
    2's bar is almost entirely amber, which says in one glance what four clauses
    could not: the card is not what that episode is waiting for.

    Everything here is derived at BUILD time from two measured files, for the
    reason box-queue.yaml's header lays out at length: a stored total keeps
    printing last night's backlog against this morning's states. A lane flipping
    one beat to `done` moves this card on the next build with nothing re-run.

    Fails SOFT and fails SILENT: no states file, no section. An ETA section that
    renders itself as "unknown" on every build teaches the reader to skip the
    part of the page that will one day carry the answer.
    """
    if not rows:
        return ""

    def _approx(minutes) -> str:
        # hours_words() already hedges above 90 min ("about 1.8 h") and does not
        # below it ("46 min"). One tilde, never "~about".
        w = hours_words(max(1, minutes))
        return w if w.startswith("about") else f"~{w}"

    cards, stamps, untagged = [], [], 0
    for r in rows:
        try:
            cards.append(_eta_card(r, _approx))
            if r["measured_at"]:
                stamps.append(str(r["measured_at"]))
            # Section-level, not per-episode: the count is a property of the
            # inbox, and printed under every card it read as two different facts.
            untagged = max(untagged, r["decisions_untagged"])
        except Exception:
            continue
    if not cards:
        return ""

    stamp = (f'The rounds-per-beat figure behind these hours was measured '
             f'{_e(sorted(stamps)[-1])}. ' if stamps else "")
    return (
        '<div class="eta rise" id="eta">'
        '<p class="sh">🗓 When is an episode finished</p>'
        + "".join(cards)
        + '<details class="drawer"><summary>How these numbers are measured — '
          'and the one thing they refuse to estimate</summary>'
          '<div class="drawer-body">'
          '<p>An episode is finished when the card has rendered every beat '
          '<i>and</i> the author has passed every beat. Those are two different '
          'clocks and this page keeps them apart. The hours are machine time, '
          'measured. How long a call takes to answer is not a quantity anyone '
          'here can measure — the same call has taken four minutes and it has '
          'taken three days — so the calls are counted and linked, never timed, '
          'and no finish date is given for one.</p>'
        + (f'<p>{untagged} open inbox entr'
           f'{"ies carry" if untagged != 1 else "y carries"} no episode tag, so '
           'they are waiting on him but are not attributed to an episode above — '
           'the gate counts are as complete as the tagging is.</p>'
           if untagged else "")
        + f'<p>{stamp}Hours are (the median number of rounds a beat needed '
          'before the card had a take he could look at) × (the median minutes a '
          'job of that kind takes on the box), both off the box’s own per-job '
          'records on <code>farm-out/box/</code>. The author’s yes is <i>not</i> '
          'in that measurement, on purpose — it is the other clock. Rounds spent '
          'before those records begin on 10 Aug are not in them, so every figure '
          'here is a <b>floor</b>, not a best guess. A beat waiting on a decision '
          'is costed separately from the certain work, because a beat that gets '
          'cut costs nothing. Method and raw numbers: '
          f'<a href="https://github.com/{GH}/blob/main/pipeline/episode_eta.py">'
          'episode_eta.py</a>, states in '
          f'<a href="https://github.com/{GH}/blob/main/pipeline/measured/'
          'episode-progress.yaml">measured/episode-progress.yaml</a>.</p>'
          '</div></details></div>')


def episode_eta_rows() -> list:
    """The ETA rows, read ONCE per build. [] when they cannot be read.

    One read, two consumers — the glance cell at the top and the cards below —
    for the same reason the box snapshot has one read: the strip's standing rule
    is that it cannot contradict the section it links to, and two reads of one
    file eventually do.
    """
    try:
        import episode_eta as _eta
        return _eta.rows()
    except Exception:
        return []


def eta_cell(rows) -> str:
    """The glance cell that answers "when is it done" before anyone scrolls.

    Roman, 2026-08-13: "im not seeing any eta". The cards were on the page, one
    panel below the glance, and he missed them — which on a page he opens to
    answer one question is the same as their not being there. The number he
    asked for therefore goes IN the glance, and the cell is an anchor down to
    the card that shows its workings, exactly as every other tile here behaves.

    It reports the NEWEST episode, which is the one being made and the one he
    named. Empty string when there is nothing to report: the strip must not grow
    a permanently apologetic sixth tile.
    """
    if not rows:
        return ""
    r = rows[0]
    if r["machine_minutes"] is None:
        return ('<a class="sx" href="#eta"><span class="sn none">not estimated'
                f'</span><span class="sl">how long episode {r["number"]} still '
                'needs on the render box — no beat of it has finished inside '
                'the box’s own records yet, so nothing is claimed</span></a>')
    w = hours_words(max(1, r["machine_minutes"]))
    big = w if w.startswith("about") else f"~{w}"
    tail = (f' · {len(r["decisions"])} call'
            f'{"s" if len(r["decisions"]) != 1 else ""} of it are yours'
            if r["decisions"] else "")
    if not r["needs_render"]:
        return ('<a class="sx" href="#eta"><span class="sn ok">nothing</span>'
                f'<span class="sl">left to render on episode {r["number"]}'
                f'{tail} · what finishing it still waits on</span></a>')
    return (f'<a class="sx" href="#eta"><span class="sn ok">{_e(big)}</span>'
            f'<span class="sl">of render time left on episode {r["number"]}'
            f'{tail} · not when it finishes — what that waits on</span></a>')


def _call_label(what: str, limit: int = 44) -> str:
    """A decision's name in a few words — never a sentence cut off mid-clause.

    The inbox's `what` fields are written for the author to DECIDE from, so they
    run to three lines and open with the headline: "Cold open fig - in both
    motion rounds...". Truncating one at n characters produced the ellipsis soup
    he rejected. Cutting at the first clause break gives the headline itself,
    with one guard — a break so early that the label would be a bare "EPISODE 2"
    is skipped for the next one, since a label that identifies nothing is worse
    than a longer one.
    """
    t = " ".join(str(what or "").split())
    if not t:
        return "an open call"
    cuts = sorted(i for sep in (" - ", " — ", ". ", "; ", ": ")
                  for i in [t.find(sep)] if i > 0)
    lab = next((t[:i] for i in cuts if i >= 10), t)
    if len(lab) > limit:                    # word boundary, never mid-word
        lab = lab[:limit].rsplit(" ", 1)[0]
    return lab.strip(" .,;:—-") or "an open call"


def _eta_card(r: dict, approx) -> str:
    """One episode as a tile: a bar of where its beats are, then three numbers.

    The bar's denominator is the episode's FULL beat count, not the number of
    beats with a state on file, so a beat nobody has scored shows as a gap
    rather than quietly shrinking the chart and flattering the progress.
    """
    total = max(1, int(r["total"]))
    c = r["counts"]
    mach_beats = c["fix-known"] + c["never-rendered"]
    # SEGMENT ORDER COMES FROM charts.STATE_ORDER, and that is a fix, not
    # tidying. The order used to follow the pipeline — passed, waiting for your
    # look, the card's to do, waiting on a decision — which put the two DARK
    # shades side by side, and they are genuinely hard to tell apart (ΔE 11.1
    # for a normal-vision reader, 5.2 under deuteranopia, both below the
    # thresholds where colour alone can be trusted). Grouped by whose clock the
    # beat is on, the bar reads as one green block and one amber block, which is
    # the argument this bar exists to make, and the worst adjacent pair goes to
    # ΔE 35.6. Same colours, same numbers, one reordering — and the tree above
    # now reads off the same table, so the two cannot drift.
    counts = {"done": c["done"], "mach": mach_beats,
              "look": c["candidate-awaiting-founder"],
              "gate": c["blocked-decision"], "unk": total - r["counted"]}
    segs = [(k, counts[k], charts.STATE_LABEL[k])
            for k in list(charts.STATE_ORDER) + ["unk"]]
    bar = "".join(f'<i class="b-{cls}" style="width:{100.0 * n / total:.4g}%"></i>'
                  for cls, n, _ in segs if n > 0)
    key = "".join(f'<span class="k-{cls}">{n} {_e(lab)}</span>'
                  for cls, n, lab in segs if n > 0)

    # --- the three numbers, in the order he acts on them. Machine first: it is
    # the answer to the question he asked. Then the two that are his.
    if r["machine_minutes"] is None:
        # A missing measurement, never a zero. "0 min left" on an unfinished
        # episode is the most confident possible lie this page could tell.
        mach = ('<span class="sn n-none">not estimated</span>'
                '<span class="sl">no beat has finished inside the box’s own '
                'records yet, so there is nothing measured to multiply</span>')
    elif mach_beats:
        # The tile label stays to one clause. The conditional hours are a real
        # and separate fact, so they get their own line under the tiles rather
        # than a fourth wrapped line inside one — the first cut of this card ran
        # that tile to four lines and threw the row out of alignment.
        mach = (f'<span class="sn n-mach">{_e(approx(r["machine_minutes"]))}</span>'
                f'<span class="sl">of <b>render time</b> left, across '
                f'{mach_beats} beat{"s" if mach_beats != 1 else ""}'
                + (f' · thin estimate, off {r["sample"]} beat'
                   f'{"s" if r["sample"] != 1 else ""}' if r["thin"] else "")
                + '</span>')
    else:
        mach = ('<span class="sn n-mach">nothing</span>'
                '<span class="sl">left to render that is not behind a call</span>')

    # THE SENTENCE THAT HAD TO BE SAID OUT LOUD. Roman, 2026-08-13, reading the
    # first version of this card: "will we be able to finish episode 2 in 1.8
    # hours?" No — that figure is the card's own working time, and he read it as
    # time-to-finished, which is precisely the confusion the two-clock design
    # exists to prevent. The design was right and the label was not: "3.7 h" next
    # to an episode name reads as an ETA for the episode unless something says
    # otherwise in plain words. This is that something, and it is not tucked in a
    # drawer — the drawer is where the explanation was when he misread it.
    clarify = ('<p class="epwarn"><b>Render time only.</b> This is how long the '
               'card is busy, <i>not</i> how long until the episode is finished — '
               'it finishes when your passes land, and those are not on a clock '
               'anyone here can read. '
               '<a href="review/plan">The schedule with times is here &rarr;</a></p>')

    gated = ""
    if r["conditional_beats"] and r["conditional_minutes"]:
        gated = (f'<p class="epnote">A further <b>{_e(approx(r["conditional_minutes"]))}'
                 f'</b> of render time, but only if the {r["conditional_beats"]} '
                 f'gated beat{"s are" if r["conditional_beats"] != 1 else " is"} '
                 'kept — a beat that gets cut costs nothing, so it is not in the '
                 'figure beside it.</p>')

    look_url = r["review_url"] or "review"
    stats = (
        f'<span class="sx">{mach}</span>'
        f'<a class="sx" href="review"><span class="sn n-you">'
        f'{len(r["decisions"])}</span><span class="sl">call'
        f'{"s" if len(r["decisions"]) != 1 else ""} only you can make</span></a>'
        f'<a class="sx" href="{_e(look_url)}"><span class="sn n-you">'
        f'{r["awaiting_founder"]}</span><span class="sl">take'
        f'{"s" if r["awaiting_founder"] != 1 else ""} waiting for your look'
        '</span></a>')

    # Two named calls, not three sentences. He asked for the wall of prose to go.
    nxt = ""
    if r["decisions"]:
        named = [f'<a href="{_e(d["url"])}">{_e(_call_label(d["what"]))}</a>'
                 if d["url"] else _e(_call_label(d["what"]))
                 for d in r["decisions"][:2]]
        more = len(r["decisions"]) - len(named)
        nxt = ('<p class="epcalls">Next: ' + " · ".join(named)
               + (f' · <a href="review">and {more} more &rarr;</a>'
                  if more > 0 else ' · <a href="review">the inbox &rarr;</a>')
               + '</p>')

    title = f' <span class="ept">{_e(r["title"])}</span>' if r["title"] else ""
    return (f'<div class="epcard"><div class="ephead"><b>Episode {r["number"]}'
            f'</b>{title}<span class="epp">{r["ready"]} of {total} passed</span>'
            f'</div><div class="epbar" role="img" aria-label="{r["ready"]} of '
            f'{total} beats passed">{bar}</div><div class="epkey">{key}</div>'
            f'<div class="epstats">{stats}</div>{clarify}{gated}{nxt}</div>')


# =============================================================================
#  EPISODE 2, RIGHT NOW — the cut's own manifest, joined to the measured states
# =============================================================================
#
# Roman, 2026-08-19: *"hows the progress with episode 2? i should be able to see
# it on the website but y'know.. its not projected very well."* He was right, and
# in two different ways. The states file behind the tree was five days stale, and
# the tree answers a question one step to the side of the one he asked: it says
# how many beats are in which state, and he wanted to know how far the EPISODE
# has got — which is a fact about the CUT. A beat can be amber and still be in
# the episode; a beat can be green and be a hole in it. The two are not the same
# picture and the page only had one of them.
#
# So this strip is the other one, and it joins the two files that between them
# already know the answer:
#
#   review/ep2-demo-<date>/sources/picks-<date>.yaml — the cut's own manifest,
#       one row per beat: which take is in it, and `why` (new / carry-forward /
#       slate). This is what he would actually watch.
#   pipeline/measured/episode-progress.yaml — the state of each beat, which is
#       the same read the tree and the ETA cards use, so the three cannot drift.
#
# EVERY NUMBER AND EVERY BEAT NAME HERE IS COMPUTED AT BUILD FROM THOSE TWO
# FILES. Not one is typed into this source, and that is the whole design
# constraint: a hand-typed "17 of 21" is correct for exactly as long as nobody
# assembles another cut, and this repo has assembled five ep2 demo cuts in five
# days. The one cross-check worth having is spelled out rather than assumed — the
# manifest states its own `footage_beats`/`slate_beats` totals, and if those
# disagree with the rows underneath them the strip SAYS SO instead of quietly
# preferring one of the two.
#
# Fails to "" on any unreadable input, like every chart on this page: a strip
# that published "0 beats have footage" off a failed read would be a picture of
# our own bug, and this one sits directly under a heading about progress.

CUT_DIR_GLOB = "ep2-demo-*"
# Which episode the cut directories above belong to. One definition, because the
# strip, the receipts and the tree's leaf links all have to agree about it and
# three separate `2`s is how they eventually would not.
CUT_EPISODE = 2


def read_latest_cut(repo=REPO, glob=CUT_DIR_GLOB) -> dict:
    """The newest ep2 demo cut's manifest, shape-checked, or {}.

    NEWEST BY DIRECTORY NAME, not by mtime. The names are `ep2-demo-MMDD` and a
    deploy checkout's mtimes are all "whenever git wrote them", so mtime would
    pick a cut at random on the machine that actually builds the site. Sorting
    the names is the only ordering that survives a fresh clone.
    """
    try:
        import yaml as _yaml
        dirs = sorted(p for p in (repo / "review").glob(glob) if p.is_dir())
        read = []                      # newest last, only the ones that parse
        for d in dirs:
            picks = sorted(d.glob("sources/picks-*.yaml"))
            if not picks:
                continue
            with open(picks[-1], encoding="utf-8") as fh:
                doc = _yaml.safe_load(fh)
            if not isinstance(doc, dict) or not isinstance(doc.get("beats"), list):
                continue
            rows = []
            for b in doc["beats"]:
                if not isinstance(b, dict):
                    continue
                try:
                    n = int(b.get("beat"))
                except (TypeError, ValueError):
                    continue
                take = b.get("take")
                rows.append({"n": n, "slug": str(b.get("slug") or "").strip(),
                             "take": str(take).strip() if take else "",
                             # The manifest's OWN word for why this take is in
                             # the slot. Printed in the table as its word, and
                             # deliberately not used to compute anything — see
                             # `prev_takes` below for why.
                             "why": str(b.get("why") or "").strip(),
                             # The row's citation of the job spec that licensed
                             # the take. Carried through as the RAW string and
                             # never printed: proof_receipts extracts the
                             # `pipeline/jobs/*.yaml` path out of it and reads
                             # the verdict out of the spec itself, because a
                             # paraphrase written by the lane that wanted the
                             # take in the cut is the one claim a reader has no
                             # way to check.
                             "verdict": str(b.get("verdict") or "").strip()})
            if not rows:
                continue
            read.append({"dir": d.name, "manifest": picks[-1].name, "beats": rows,
                         # The manifest's own totals, kept as the CROSS-CHECK and
                         # never as the source. None when it does not state them.
                         "said_footage": doc.get("footage_beats"),
                         "said_slates": doc.get("slate_beats")})
        if not read:
            return {}
        cut = read[-1]
        # WHAT IS NEW IS MEASURED, NOT READ OFF A LABEL, and that is a bug fix
        # rather than fussiness. picks-0819.yaml defines its own `why: new` as
        # "footage that was not in the 2026-08-18 cut" and then says, in the same
        # file, that every line it did not re-read was "copied from picks-0818
        # unchanged" — so beats 01 and 14 carry `new` from the cut BEFORE the one
        # they were new in, and four beats claim to be new in a cut whose own
        # header says two clips were swapped. Diffing the take FILENAMES against
        # the previous manifest cannot be wrong in that way: the answer comes out
        # of the two files being different, not out of anyone remembering to
        # relabel a row.
        cut["prev"] = read[-2]["dir"] if len(read) > 1 else ""
        cut["prev_takes"] = ({r["take"] for r in read[-2]["beats"] if r["take"]}
                             if len(read) > 1 else set())
        return cut
    except Exception:
        return {}


def _cut_state_rows(cut: dict, prog: list, number: int = 2) -> list:
    """One row per beat of the episode: what is in the cut, and its state.

    Joined on the beat number, outer from the CUT side and filled from the
    states side, so a beat the manifest lists and the measurement does not shows
    an empty state rather than vanishing off a table about completeness.
    """
    ep = next((e for e in prog if e.get("number") == number), None)
    states = {b["n"]: b for b in (ep or {}).get("beats") or []}
    out = []
    for b in sorted(cut["beats"], key=lambda r: r["n"]):
        st = states.get(b["n"]) or {}
        out.append({**b, "state": str(st.get("state") or ""),
                    "css": charts.STATE_CLASS.get(str(st.get("state") or ""), "")})
    return out


# =============================================================================
#  THE RECEIPTS — the founder's ask of 2026-08-19, in one sentence of his own:
#  "since you are an ai, you can hallucinate and say something completely wrong
#  with complete confidence, so i need concrete proof we are making progress.
#  banyan.city/status isn't shaped very well to show that."
#
#  So the rule for this whole block: EVERY CLAIM IS A LINK TO THE BYTES BEHIND
#  IT. Not a sentence about a render — the frame out of the render, the render
#  itself at a URL, its sha256 recomputed while this page was being built, and
#  the verdict quoted out of the job spec with a link to that file on GitHub. A
#  reader who clicks a link that 404s, or runs `shasum -a 256` and gets a
#  different answer, has caught the page lying. That is the point: a claim that
#  cannot be falsified is not evidence, it is just confident prose, which is
#  exactly what he said he cannot use.
#
#  It goes INSIDE the strip that already exists rather than on a page of its own
#  (his second word on it, the same day: "do you really need a different page for
#  every small thing? cant you build it into /status?"). The strip's fact lines
#  and its table are untouched; each beat gains a fold under it holding its
#  receipt, and the caption gains the falsification sentence.
# =============================================================================

# `<img>` on a per-beat fold: the frame is decoration until the fold is open, so
# it is lazy and it never blocks the page. Committed at this width by
# proof_receipts.py --frames; the attribute pair comes off the manifest so 18
# thumbnails cannot reflow the strip as they arrive on a phone.
RECEIPT_THUMB_W = 54


def _sha_words(rec: dict) -> str:
    """The sha line, in the words the check actually earns and no stronger.

    Five outcomes and each one is a different sentence. "match" is the only one
    that is evidence; the other four are all, in their own way, the page telling
    on itself, which is worth more than a green tick it has not earned.
    """
    short = (rec.get("sha") or "")[:12]
    check = rec.get("sha_check")
    path = rec.get("artifact") or ""
    how = (f' Check it yourself: <code>shasum -a 256 {_e(path)}</code>.'
           if path else "")
    if check == "match":
        return (f'<code>{_e(short)}…</code> — <b>recomputed at build time off the '
                f'bytes in this checkout and equal to the hash the cut\'s own '
                f'<code>ingredients:</code> block recorded when it was muxed.</b>'
                + how)
    if check == "differs":
        return (f'<b class="bad">THE BYTES DO NOT MATCH THE MANIFEST.</b> The cut '
                f'records <code>{_e(short)}…</code>; this checkout hashes '
                f'<code>{_e((rec.get("sha_recomputed") or "")[:12])}…</code>. One '
                f'of the two is wrong and this row is not evidence of anything '
                f'until someone says which.' + how)
    if check == "missing":
        return ('<b class="bad">The take is named by the manifest and is not in '
                'this checkout</b>, so nothing could be hashed. The link above '
                'will 404 — that is the defect, not a rendering fault.')
    if check == "unrecorded":
        return (f'<code>{_e((rec.get("sha_recomputed") or "")[:12])}…</code>, '
                'computed here. The assembly recorded no hash for this beat, so '
                'there is nothing to compare it against — an unrecorded '
                'ingredient, which is neither a match nor a mismatch.')
    return ('No hash on file and none computed — this row proves nothing about '
            'its bytes and says so.')


def _receipt_html(rec: dict, css: str, state_label: str) -> str:
    """One beat's fold: the frame, the file, the hash, the verdict, the date."""
    n, slug = rec["n"], rec.get("slug") or "?"
    call = rec.get("call") or ""
    chip = ""
    if call:
        chip = (f'<span class="rcall {"ok" if call == "PASS" else "bad"}">'
                f'{_e(call)}</span>')
    else:
        # NOT A NEUTRAL BLANK. Eight beats of this episode have never been judged
        # against a bar, and the hollow chip is the same mark the tree uses for a
        # beat nobody has scored — missing evidence, drawn as missing.
        chip = '<span class="rcall none">no verdict</span>'
    if rec.get("frame"):
        fr = rec["frame"]
        w = int(rec.get("frame_w") or 0) or RECEIPT_THUMB_W
        h = int(rec.get("frame_h") or 0)
        dims = f' width="{w}" height="{h}"' if h else ""
        thumb = (f'<img class="rth" src="{_e(fr)}"{dims} loading="lazy" '
                 f'decoding="async" alt="A frame from the middle of beat '
                 f'{n:02d}’s take in the newest cut">')
    else:
        thumb = (f'<span class="rth none" aria-hidden="true">'
                 f'{"slate" if rec.get("slate") else "&mdash;"}</span>')

    rows = []
    if rec.get("artifact"):
        size = bytes_words(int(rec.get("bytes") or 0)) if rec.get("bytes") else ""
        rows.append(
            ('<dt>the file in the cut</dt><dd>'
             f'<a href="{_e(rec["artifact"])}">{_e(rec["take"])}</a>'
             + (f' &middot; {_e(size)}' if size else "")
             + (f' &middot; <a href="{_e(rec["artifact_gh"])}">the same bytes on '
                'GitHub</a>' if rec.get("artifact_gh") else "")
             + f' &middot; in the cut because: {_e(rec.get("why") or "unstated")}'
             '</dd>'))
        rows.append(f'<dt>sha256</dt><dd>{_sha_words(rec)}</dd>')
    else:
        rows.append(
            '<dt>the file in the cut</dt><dd><b>There is none.</b> render_t3 '
            'draws a title card in this slot and the voice take plays over it. '
            'Shown as a slate here because it is one.</dd>')
    if rec.get("frame_why"):
        rows.append(f'<dt>frame</dt><dd>{_e(rec["frame_why"])}</dd>')
    verdicts = rec.get("verdicts") or []
    # A SLATE'S VERDICT LINE IS A DIFFERENT SENTENCE, and the first cut of this
    # got it wrong: it printed "it is in the cut because it is the beat's best
    # footage" over beat 09, which has no footage at all. Copy that is true of
    # eighteen rows and false of three is exactly the confident-and-wrong shape
    # this whole feature exists to stop.
    vlabel = ("the verdict on file" if rec.get("slate")
              else "the verdict that licensed it")
    if verdicts:
        quoted = "".join(
            f'<p class="rq"><span class="rk">{_e(k)}:</span> {_e(text)}</p>'
            for k, text in verdicts[:4])
        more = (f'<p class="rq more">{len(verdicts) - 4} further '
                f'<code>verdict*</code> key'
                f'{"s" if len(verdicts) - 4 != 1 else ""} in the same file.</p>'
                if len(verdicts) > 4 else "")
        rows.append(
            f'<dt>{vlabel}</dt><dd>'
            f'{quoted}{more}'
            f'<p class="rsrc">Quoted verbatim from <a href="{_e(rec["spec_gh"])}">'
            f'{_e(rec["spec"])}</a> &mdash; the bar in that file was written '
            'before the pixels existed, and this page does not summarise it.</p>'
            '</dd>')
    elif rec.get("spec"):
        rows.append(
            f'<dt>{vlabel}</dt><dd>The cut cites '
            f'<a href="{_e(rec["spec_gh"])}">{_e(rec["spec"])}</a> and that file '
            'carries no <code>verdict*:</code> string this build could read. '
            'Printed as unread rather than guessed at.</dd>')
    elif rec.get("slate"):
        rows.append(
            f'<dt>{vlabel}</dt><dd><b>None, and that is what a slate is.</b> '
            'Nothing exists for this beat that a verdict lets into a cut. What it '
            'is waiting for is written out in the cut’s own manifest, per beat, '
            'under <code>blocked_on</code>.</dd>')
    else:
        rows.append(
            f'<dt>{vlabel}</dt><dd><b>None exists.</b> No job '
            'spec anywhere answers a pre-registered bar for this file. It is in '
            'the cut because it is the beat’s best footage, which is not the '
            'same as having passed &mdash; riding five cuts unchanged is five '
            'appearances, not five passes.</dd>')
    if rec.get("landed_at"):
        rows.append(
            f'<dt>landed</dt><dd>{_e(rec["landed_at"])} &middot; '
            f'<a href="{_e(rec["landed_url"])}">{_e(rec["landed_sha"])}</a> '
            f'&mdash; {_e(rec.get("landed_what") or "")}.</dd>')
    elif rec.get("slate"):
        # NOT "not measured" — there is nothing to date. A slate has no file and
        # no spec, so an absent date is the correct answer rather than a gap in
        # the measurement, and the two must not read the same.
        rows.append('<dt>landed</dt><dd>Nothing to date: no file and no spec, so '
                    'there is no commit that would be this beat’s.</dd>')
    else:
        rows.append('<dt>landed</dt><dd>Not measured. The date comes from a '
                    'committed git measurement (see the caption) and this row is '
                    'not in it.</dd>')

    return (f'<details class="rcpt" id="e2b{n:02d}">'
            f'<summary>{thumb}<span class="rn">{n:02d}</span>'
            f'<span class="rs">{_e(slug)}</span>'
            f'<span class="fk f-{css or "unk"}">{_e(state_label)}</span>'
            f'{chip}</summary>'
            f'<div class="rb"><dl>{"".join(rows)}</dl></div></details>')


def leaf_links(recs: list, number: int = CUT_EPISODE) -> dict:
    """{(episode, beat) -> {href, note}} so a leaf on the tree opens the CLIP.

    The founder's second note on the receipts, 2026-08-19: the tree already links
    every leaf, and it linked all of them to the beat's shot board — the same
    destination whatever state the leaf was in. So a leaf that IS a rendered take
    now opens that take: click the leaf, the mp4 plays. A leaf with no footage
    keeps the board link, because a slate has no clip to open and sending him to
    a 404 to prove a point would be worse than the state word he already had.

    The tooltip gains the take's filename and the first twelve of its sha256.
    That is not decoration either: it is what makes the leaf and the receipt
    below it checkably the same object, and it is the only per-beat identity the
    picture can carry without a reader opening anything.
    """
    out = {}
    for r in recs or []:
        if not r.get("artifact"):
            continue
        note = f'take {r["take"]}'
        if r.get("sha"):
            note += f' · sha {r["sha"][:12]}…'
        if r.get("call"):
            note += f' · {r["call"]}'
        out[(int(number), int(r["n"]))] = {"href": r["artifact"], "note": note}
    return out


def proof_ledger_line(led: dict = None) -> str:
    """The fortnight as three deltas and one link to the raw diffs. "" when unread.

    ONE LINE IN THE FOOTER AND NOT A TABLE. A table of daily counts was the first
    shape of this and it was the wrong one twice over: it would have been the
    fourth section on a page the founder has twice asked to simplify, and a
    per-day breakdown invites reading a quiet Tuesday as a slow week when the
    same fortnight also shipped six cuts.

    EVERY WORD OF THE LABEL IS THE QUERY. These are counts of ADDED DIFF LINES,
    not of things that are true now: a `verdict*:` line added and later edited
    counts once here and the edit counts again, and a `resolved:` block may carry
    a steward's answer as easily as the founder's. So the line says "recorded"
    and "added", names the file each count came from, and hands over the compare
    range so a reader can disagree with the count by reading the diffs. A number
    whose definition is hidden is the kind of confident claim this whole feature
    exists to replace.
    """
    led = proof_receipts.read_ledger() if led is None else led
    v = led.get("verdict_lines_added")
    c = led.get("cuts_shipped")
    r = led.get("resolved_blocks_added")
    if v is None or c is None or r is None:
        return ""
    base, head = str(led.get("range_base") or ""), str(led.get("head") or "")
    days = int(led.get("window_days") or 14)
    link = (f' &mdash; <a href="{_e(proof_receipts.compare_url(base, head))}">audit '
            f'the {int(led.get("commits_in_window") or 0)} commits behind these '
            'numbers &rarr;</a>' if base and head else "")
    floor = ("" if led.get("covers_window") else
             ' These are a FLOOR, not a count: the history they were taken from '
             'does not reach past the window.')
    return (f'<p class="pledger">Last {days} days, computed from this '
            f'repository’s own history by <code>{_e(proof_receipts.LEDGER_CMD)}'
            f'</code> and committed as '
            f'<code>pipeline/measured/proof-ledger.json</code>: <b>{v}</b> '
            f'<code>verdict*:</code> lines recorded under '
            f'<code>pipeline/jobs/</code>, <b>{c}</b> cut'
            f'{"s" if c != 1 else ""} assembled, <b>{r}</b> '
            f'<code>resolved:</code> block{"s" if r != 1 else ""} added to the '
            f'review board. Counts of added diff lines, not of what is true '
            f'today.{floor}{link}</p>')


def receipts_html(rows: list, recs: list) -> str:
    """The per-beat folds, in beat order. "" when there are no receipts to show.

    Fails to nothing on purpose, like every other section here: a receipt list
    with no receipts in it would be a picture of our own failed read dressed up
    as an episode with no evidence behind it.
    """
    by_n = {r["n"]: r for r in recs}
    out = []
    for r in rows:
        rec = by_n.get(r["n"])
        if not rec:
            continue
        out.append(_receipt_html(
            rec, r.get("css") or "",
            charts.STATE_LABEL.get(r.get("css") or "", "no state on file")))
    return f'<div class="rcpts">{"".join(out)}</div>' if out else ""


def ep2_now_html(cut: dict, prog: list, number: int = 2, recs: list = None) -> str:
    """The strip: one line per fact, every one of them computed. "" when unread.

    ONE LINE PER FACT AND NO PARAGRAPHS. The page's own history is the argument
    for that shape — the founder threw out the six-badge strip and the wall of
    ETA prose, both of which said true things in too many words to reach him.
    """
    if not cut or not prog:
        return ""
    rows = _cut_state_rows(cut, prog, number)
    if not rows:
        return ""
    ep = next((e for e in prog if e.get("number") == number), None)
    if not ep:
        return ""
    total = int(ep.get("total_beats") or len(rows))
    footage = [r for r in rows if r["take"]]
    slates = [r for r in rows if not r["take"]]
    looking = [b for b in ep["beats"]
               if b["state"] == "candidate-awaiting-founder"]
    gated = [b for b in ep["beats"] if b["state"] == "blocked-decision"]
    prev_takes = cut.get("prev_takes") or set()
    fresh = ([r for r in footage if r["take"] not in prev_takes]
             if cut.get("prev") else [])
    # The join's own finding, and the reason the two files are worth joining at
    # all: a beat can be a hole in the cut and hold passing footage at the same
    # time, which is a swap somebody has to make and not a render anybody has to
    # run. Beat 07 was exactly that on the day this was written.
    look = {b["n"] for b in looking}
    swap = [r for r in slates if r["n"] in look]
    url = f"review/{cut['dir']}"
    # THE RECEIPTS. Read here rather than passed in from build(), for the same
    # reason the cut manifest is: one read, in the one function that renders it.
    # `recs` is injectable so a test can hand in a fixture without a checkout.
    if recs is None:
        try:
            recs = proof_receipts.receipts(cut)
        except Exception:
            # Fails to nothing, exactly like the tree above. A receipt list built
            # from a read that half-failed is worse than no receipts: it would
            # publish "no verdict block exists" over beats that have one.
            recs = []
    tally = proof_receipts.sha_tally(recs) if recs else {}
    judged = [r for r in recs if r.get("verdicts")]
    unjudged = [r for r in recs if not r.get("slate") and not r.get("spec")]

    def beats(rs, sep=", "):
        return sep.join("%02d %s" % (r["n"], r["slug"] or "?") for r in rs)

    def nums(bs):
        # "%02d" and not an f-string with a nested subscript: PEP 701 quote
        # reuse inside a format spec is 3.12+, and this file has to build on
        # whatever python the deploy box hands it.
        return ", ".join("%02d" % b["n"] for b in bs)

    facts = []
    facts.append(
        f'<li class="f-look"><b>{len(footage)} of {total} beats</b> have footage '
        f'in the newest cut &mdash; <a href="{_e(url)}">{_e(cut["dir"])}</a>'
        + (f', {len(fresh)} of them ({_e(beats(fresh))}) not in '
           f'{_e(cut["prev"])}, the cut before it' if fresh else "")
        + '.</li>')
    if slates:
        facts.append(
            f'<li class="f-mach"><b>{len(slates)} still a slate</b> &mdash; a '
            f'title card where the shot goes: {_e(beats(slates))}.</li>')
    else:
        facts.append('<li class="f-done"><b>No slates left</b> — every beat of '
                     'the episode has footage in the cut.</li>')
    if swap:
        facts.append(
            f'<li class="f-swap"><b>{_e(beats(swap))}</b> is a slate in that cut '
            'and <i>already has a take that passes its bar</i> — that one is a '
            'swap in the next assembly, not a render.</li>'
            if len(swap) == 1 else
            f'<li class="f-swap"><b>{len(swap)} of those slates</b> already have '
            f'takes that pass their bar ({_e(beats(swap))}) — swaps for the next '
            'assembly, not renders.</li>')
    facts.append(
        f'<li class="f-look"><b>'
        + (f'{len(looking)} beats hold takes waiting for your look</b>'
           if len(looking) != 1 else
           '1 beat holds a take waiting for your look</b>')
        + f' &mdash; passing takes nobody has ruled on: {_e(nums(looking))}.</li>'
        if looking else
        '<li class="f-look"><b>Nothing is waiting for your look</b> &mdash; no '
        'beat holds a passing take you have not ruled on.</li>')
    if gated:
        facts.append(
            f'<li class="f-gate"><b>{len(gated)} beat'
            f'{"s are" if len(gated) != 1 else " is"} waiting on a call only you '
            f'can make</b> ({_e(nums(gated))}) '
            '&mdash; <a href="review">the open questions &rarr;</a></li>')
    facts.append(
        '<li class="f-done"><b>0 beats passed.</b> No beat of episode 2 carries '
        'your verdict yet, and the cuts above are bench assemblies — they have '
        'no leaf and nothing in the tree.</li>'
        if not [b for b in ep["beats"] if b["state"] == "done"] else
        f'<li class="f-done"><b>'
        f'{len([b for b in ep["beats"] if b["state"] == "done"])} beats passed'
        '.</b></li>')
    # THE TWO LINES THE RECEIPTS ADD, and they are the two he asked for: one that
    # can be falsified with a shell command, and one that admits how much of the
    # episode has never been judged at all. Both are silent when there are no
    # receipts to count — a build that could not read them says nothing here
    # rather than printing a zero it cannot back up.
    if tally.get("takes"):
        clean = tally.get("match", 0)
        bad = tally["takes"] - clean
        facts.append(
            f'<li class="f-done"><b>{clean} of {tally["takes"]} takes in that cut '
            f'hash exactly as the cut says they do</b> &mdash; every one '
            f're-hashed while this page was built, against the sha256 '
            f'<code>render_t3</code> recorded when it muxed them'
            + (f'. <b class="bad">{bad} did not</b>, and the beat says which '
               'below' if bad else '. Run <code>shasum -a 256</code> on any of '
               'them and you can catch this page lying')
            + '.</li>')
    if recs:
        facts.append(
            f'<li class="f-swap"><b>{len(judged)} beat'
            f'{"s" if len(judged) != 1 else ""} carr'
            f'{"y" if len(judged) != 1 else "ies"} a written verdict against a bar '
            f'set before the pixels existed</b>; <b>{len(unjudged)}</b> hold '
            'footage no bar has ever been answered for. Both are per-beat links '
            'below — the second number is the honest one, and it is the quiet '
            'half of the episode.</li>')

    # The disagreement guard. Silent when the manifest's own totals match the
    # rows under them, which is the common case and says nothing worth a line.
    mismatch = []
    for said, got, what in ((cut.get("said_footage"), len(footage), "footage"),
                            (cut.get("said_slates"), len(slates), "slate")):
        try:
            if said is not None and int(said) != got:
                mismatch.append(f"it states {int(said)} {what} beats and lists {got}")
        except (TypeError, ValueError):
            continue
    note = (f'Counted at build time off <code>{_e(cut["dir"])}/sources/'
            f'{_e(cut["manifest"])}</code> and '
            '<code>pipeline/measured/episode-progress.yaml</code> — the same two '
            'files the tree above and the estimate below read, so none of the '
            'three can drift from the others.')
    if mismatch:
        note += (' <b>The manifest disagrees with itself:</b> '
                 + _e("; ".join(mismatch))
                 + '. The rows are what is counted here; its header totals are '
                 'not, and the difference is printed rather than hidden.')
    # THE FALSIFICATION SENTENCE, one line, in the caption where the reader is
    # already being told where the numbers came from. His ask was for proof he
    # can check rather than prose he has to trust, and the only honest form that
    # takes is an invitation to catch it out.
    if recs:
        note += (' <b>Every claim in the folds below is a link to the bytes '
                 'behind it: if one 404s or a sha does not match, this page is '
                 'lying and that is a bug worth filing.</b> Nothing in them is '
                 'hand-written.')

    head = "".join('<tr><th scope="row">%02d %s</th>' % (r["n"], _e(r["slug"]))
                   + f'<td>{_e(r["take"]) if r["take"] else "&mdash; slate"}</td>'
                   f'<td>{_e(r["why"])}</td>'
                   f'<td><span class="fk f-{r["css"] or "unk"}">'
                   f'{_e(charts.STATE_LABEL.get(r["css"], "no state on file"))}'
                   '</span></td></tr>' for r in rows)
    # THE RECEIPTS GO IN THE DRAWER THAT WAS ALREADY THERE, above the table, and
    # the table stays exactly as it was. The table is the scan view — twenty-one
    # rows, one screen, nothing to open — and it is what a screen reader and a
    # reader who wants only the shape of it get. The folds are the evidence under
    # each row. Neither is a substitute for the other, which is why this is one
    # drawer with two views and not two sections.
    rcpt = receipts_html(rows, recs)
    stamp = ""
    if recs:
        led = proof_receipts.read_ledger()
        when = str(led.get("generated") or "")
        stamp = ('<p class="cnote">The frame beside each beat is a mid-frame of '
                 'that take, cut by <code>ffmpeg</code> and committed with the '
                 'sha256 of the clip it came out of, so a swapped take cannot '
                 'keep last week’s picture — the canonical host has no '
                 '<code>ffmpeg</code>, which is why they are committed rather '
                 'than extracted here. The dates come from '
                 '<code>pipeline/measured/proof-ledger.json</code>'
                 + (f', measured {_e(when)}' if when else "")
                 + ' by <code>' + _e(proof_receipts.LEDGER_CMD) + '</code> off '
                 'this repository’s own history; a deploy checkout is one commit '
                 'deep and could not compute them. Run it yourself and diff the '
                 'file.</p>')
    table = ('<details class="drawer"><summary>Every beat of episode 2 — the take '
             'in the cut, the bytes behind it, and the verdict that let it in'
             '</summary><div class="drawer-body">'
             f'{rcpt}{stamp}'
             '<div class="scroll"><table class="ctab"><thead><tr>'
             '<th scope="col">Beat</th><th scope="col">In the newest cut</th>'
             '<th scope="col">Why</th><th scope="col">State</th></tr></thead>'
             f'<tbody>{head}</tbody></table></div>'
             '<p class="cnote">The same twenty-one beats as a table, for a reader '
             'who wants the shape without opening anything. Left two columns off '
             'the cut manifest, right one off the measured states. A beat can '
             'hold a passing take and still be a slate in the cut: the take has '
             'to be assembled in, and that is a separate pass.</p>'
             '</div></details>')

    return (f'<div class="ep2now" role="group" aria-label="Episode {number} right '
            f'now: {len(footage)} of {total} beats have footage in the newest '
            f'cut, {len(slates)} are still slates, {len(looking)} hold takes '
            f'waiting for the author’s look">'
            f'<div class="e2h">Episode {number}, right now</div>'
            f'<ul class="e2l">{"".join(facts)}</ul>'
            f'<p class="cnote">{note}</p></div>{table}')


# ---- files the reader's browser re-reads ------------------------------------
# The render box's minute-by-minute charts LEFT this page in the 2026-08-11
# revamp — the long history lives on /pulse, and telemetry_head() still reads
# the box's newest sample for the machine list's "is it on" signal. What
# stays is the queue file LIVE_JS re-reads, and the staleness rule the
# vitals re-read keys on (TELEMETRY_STALE_MINUTES, at the top of the file).
QUEUE_URL = f"{RAW}/main/pipeline/farm-queue.yaml"

# THE QUEUE TILE'S LIVE SOURCE (2026-08-13). Roman: "why is the banyan.city/status
# only updating when i freaking remind you about it??" — the tile's numbers came
# from pipeline/measured/box-queue.yaml, which changes only when a supervisor
# session hand-commits it, so "measured 4 h ago" was really "last nagged 4 h ago".
# The box itself knows its queue every second and already publishes to its own
# branch every five minutes (pipeline/telemetry.py), so the reader's browser
# fetches THAT and rewrites the numbers. No session, no commit, no deploy in the
# freshness path. The yaml stays as the no-JS floor, and the medians the estimate
# multiplies by still come from it — those are measured over days, not minutes.
BOX_BRANCH = "farm-results-rtx5090"
BOX_TEL_URL = f"{RAW}/{telemetry_branch(BOX_BRANCH)}/telemetry.json"
BOX_TEL_URL_LEGACY = f"{RAW}/{BOX_BRANCH}/telemetry.json"
# Older than this and the queue block is a historical record, not a reading: the
# page keeps showing it but stops calling it live and says how old it is. Three
# missed publishes, the same rule TELEMETRY_STALE_MINUTES applies to the vitals.
BOX_QUEUE_STALE_MINUTES = TELEMETRY_STALE_MINUTES


# Plain string, not an f-string: JavaScript, full of braces. INFRA_* are emitted
# beside it by build().
INFRA_JS = """
/* ---- the infra meter: how many times this site was built in the last day ----
   Vercel's git integration opens a GitHub DEPLOYMENT per build, and that list is
   public, free and CORS-enabled (Access-Control-Allow-Origin: *, verified
   2026-08-09) — the only $0 source for this anyone has found; the host publishes
   no free spend figure. Counted in the READER's browser for the same reason the
   machines' logs are: a build-time count would only advance when a build
   happens, and a flood of builds is precisely the failure being watched for.

   FOUR WAYS THIS DECLINES TO ANSWER, and not one of them prints a number: no
   fetch in the browser, a non-200 (the unauthenticated limit is 60/hour per IP
   and every reader behind one shares it), a body that is not an array, and a row
   with no readable date. The page says so in words and shows nothing else.

   THE '+' IS LOAD-BEARING. One page is 100 rows and nothing pages further, so if
   the OLDEST row on the page is itself inside the window, there were builds this
   request could not see — 'N+' says that rather than passing a floor off as a
   count. At the rate this repo builds, 100 production deployments reach back
   about four days, so the + fires only when the rate roughly quadruples, which
   is the alarm and not a gap. */
(function () {
  var n = document.getElementById("infra-n"), u = document.getElementById("infra-u");
  if (!n || !u || !window.fetch) return;                /* no JS, no claim */
  function give(text, big) {
    n.textContent = text;
    n.className = big ? "n" : "n none";
  }
  function fail() {
    give(INFRA_UNAVAILABLE, false);
    u.textContent = INFRA_TITLE.toLowerCase();
  }
  fetch(INFRA_API, {headers: {Accept: "application/vnd.github+json"}})
    .then(function (r) { if (!r.ok) throw 0; return r.json(); })
    .then(function (rows) {
      if (!Array.isArray(rows)) throw 0;
      var since = Date.now() - INFRA_HOURS * 3600000, c = 0, oldest = Infinity;
      for (var i = 0; i < rows.length; i++) {
        var t = Date.parse(rows[i] && rows[i].created_at);
        if (!t) throw 0;                       /* a shape we do not understand */
        if (t < oldest) oldest = t;
        if (t >= since) c++;
      }
      var capped = rows.length >= INFRA_PAGE && oldest >= since;
      give(capped ? c + "+" : String(c), true);
      u.textContent = (c === 1 && !capped) ? INFRA_UNIT_ONE : INFRA_UNIT_MANY;
    })
    .catch(fail);
})();
"""



# Plain string, not an f-string: JavaScript, full of braces. RAW_BASE, QUEUE_URL,
# BUILT_AT and BUILT_QUEUE are emitted next to it by build().
LIVE_JS = """
/* ---- the page keeps up with the farm after the deploy ------------------------
   Four files, all of them ours, all fetched by the reader's own browser off
   raw.githubusercontent (Access-Control-Allow-Origin: *, verified): each
   machine's check-in log, each machine's vitals, the shared work queue, and the
   render box's own queue depth. No library, no external code, no request to any
   host but GitHub's raw CDN.

   This is the whole freshness mechanism for the queue numbers. A static page
   cannot update itself and this site does not rebuild on a timer, so anything
   that has to be current has to be fetched by the reader — the alternative,
   which is what the queue tile did until 2026-08-13, is a number that is as old
   as the last time a person remembered to run a session.

   The honesty rules the rest of the page runs on apply here too:
     * a fetch that fails says so in words and changes nothing else;
     * ages count from the datum, never from the page — every age on this page
       is a <time data-at> and this is what keeps it counting;
     * heartbeat.txt carries a clock and no date, so a line that appeared AFTER
       this copy was built is dated as the first instant matching that clock at
       or after the build. That is exact — until the tab has been open longer
       than a day, at which point the clock is genuinely ambiguous and the page
       says so instead of picking. */
(function () {
  if (!window.fetch) return;                       /* no JS, no claim */
  function bust() { return Math.floor(Date.now() / 60000); }
  function words(sec) {
    if (sec < 90) return "just now";
    if (sec < 5400) return Math.floor(sec / 60) + " min ago";
    if (sec < 129600) return Math.floor(sec / 3600) + " h ago";
    var d = Math.floor(sec / 86400);
    return d + (d === 1 ? " day ago" : " days ago");
  }
  function stamp(ms) {
    return new Date(ms).toLocaleString([], {month: "short", day: "numeric",
                                            hour: "2-digit", minute: "2-digit"});
  }
  function paint(el) {
    var at = +el.getAttribute("data-at");
    if (!at) return;
    var sec = Math.max(0, Math.round(Date.now() / 1000 - at));
    el.textContent = words(sec) + (sec >= 86400 ? " (" + stamp(at * 1000) + " your time)" : "");
  }
  function tick() {
    var els = document.querySelectorAll("time.age[data-at]");
    for (var i = 0; i < els.length; i++) paint(els[i]);
  }
  function ageEl(at) {
    var t = document.createElement("time");
    t.className = "age";
    t.setAttribute("data-at", at);
    t.setAttribute("datetime", new Date(at * 1000).toISOString());
    paint(t);
    return t;
  }

  /* ---- one machine's own log ------------------------------------------- */
  var STAGE = {STARTED: "started a job", MODEL_LOADED: "loaded the model",
               VIDEO_VENV_OK: "set its video tools up", VIDEO_DEPS_OK: "set its video tools up",
               VIDEO_RENDERING: "rendering a moving clip", RENDERING: "rendering",
               VIDEO_CLIP: "wrote a clip", VIDEO_CLIP_OK: "wrote a clip",
               VIDEO_ENCODING: "encoding a clip", ENCODING: "encoding",
               DONE: "handed its job in", FAIL: "its last job failed"};
  function stageWords(line) {
    /* task ids are log tokens and never reach the page (stranger-eyes, 2026-07-30) */
    var s = line.replace(/^\\d{2}:\\d{2}:\\d{2}Z\\s*/, "").replace(/task=[\\w.\\-]+/g, "").trim();
    var head = (s.split(/\\s+/)[0] || "").toUpperCase();
    return STAGE[head] || s.toLowerCase() || "checked in";
  }
  function lineTime(line) {
    var m = /^(\\d{2}):(\\d{2}):(\\d{2})Z/.exec(line);
    if (!m) return null;
    if (Date.now() / 1000 - BUILT_AT > 86400) return null;   /* genuinely ambiguous */
    var d = new Date(BUILT_AT * 1000);
    var t = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(), +m[1], +m[2], +m[3]);
    if (t < BUILT_AT * 1000) t += 86400000;                  /* the clock crossed midnight */
    if (t > Date.now() + 60000) t -= 86400000;
    return Math.floor(t / 1000);
  }
  function lot(key, css) {
    var b = document.querySelector('.lot-bld[data-mach="' + key + '"]');
    if (b) b.className = "lot-bld " + css;
  }
  function say(li, text) {
    var n = li.querySelector('[data-role="live"]');
    if (!n) {
      n = document.createElement("div");
      n.className = "mono livemark";
      n.setAttribute("data-role", "live");
      li.appendChild(n);
    }
    n.textContent = text;
    return n;
  }

  function readLog(li) {
    var branch = li.getAttribute("data-branch"), key = li.getAttribute("data-mach");
    var was = li.getAttribute("data-tail") || "";
    fetch(RAW_BASE + "/" + branch + "/farm-out/heartbeat.txt?_=" + bust(), {cache: "no-store"})
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.text(); })
      .then(function (txt) {
        var lines = txt.replace(/\\s+$/, "").split("\\n");
        var tail = (lines[lines.length - 1] || "").trim();
        if (!tail || tail === was) return;         /* the build-time reading still stands */
        li.setAttribute("data-tail", tail);
        var ended = /(DONE|FAIL)\\b/.test(tail);
        var head = li.querySelector('[data-role="head"]');
        var chip = li.querySelector('[data-role="chip"]');
        if (head) head.textContent = stageWords(tail);
        if (chip) {
          chip.textContent = ended ? "just finished" : "rendering";
          chip.className = "chip" + (ended ? "" : " hot");
        }
        lot(key, ended ? "idle" : "working");
        var at = lineTime(tail), seen = li.querySelector('[data-role="seen"]');
        if (seen) {
          seen.textContent = "last check-in ";
          if (at) seen.appendChild(ageEl(at));
          else seen.appendChild(document.createTextNode(
            "since this page was built — the log carries a clock and no date, and this tab " +
            "has been open long enough that the day is genuinely ambiguous"));
        }
        say(li, "re-read by your browser — this is newer than the copy the page was built from");
      })
      .catch(function (e) {
        say(li, "its log could not be re-read just now (" + e.message +
                "), so the reading above is the one this page was built with");
      });
  }

  function readVitals(li) {
    var branch = li.getAttribute("data-branch"), key = li.getAttribute("data-mach");
    var tel = li.getAttribute("data-telbranch") || branch;
    function grabTel(b) {
      return fetch(RAW_BASE + "/" + b + "/telemetry.json?_=" + bust(), {cache: "no-store"})
        .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); });
    }
    /* The vitals branch first, then the courier branch it used to share — the
       same fallback the build-time read does, for the same reason: during the
       split the freshest sample can still be in the old place, and a 404 there
       must not be reported as a box that stopped publishing. */
    var got = grabTel(tel);
    if (tel !== branch) got = got.catch(function () { return grabTel(branch); });
    got
      .then(function (d) {
        var at = +d.last_sample;
        if (!at) throw new Error("no sample in the file");
        var stale = Date.now() / 1000 - at > TEL_STALE * 60;
        var chip = li.querySelector('[data-role="chip"]');
        var slot = li.querySelector('[data-role="vitals"]');
        if (slot) {                                /* one age for one datum */
          slot.textContent = "";
          slot.appendChild(ageEl(at));
        }
        if (stale) {
          /* the box has stopped publishing: withdraw the "switched on" claim */
          if (chip && chip.textContent.indexOf("on,") === 0) {
            chip.textContent = "not heard from";
            chip.className = "chip";
            lot(key, "asleep");
          }
          say(li, "its vitals stopped arriving " + words(Math.round(Date.now() / 1000 - at)) +
                  " — nothing is claimed about whether it is switched on");
        } else {
          say(li, "your browser re-read its vitals just now — it is switched on");
        }
      })
      .catch(function (e) {
        say(li, "its vitals could not be read just now (" + e.message + ")");
      });
  }

  /* ---- the work queue --------------------------------------------------- */
  /* A four-line reader, not a YAML parser: this file's entries are `- id: x` at
     column 0 under one of two top-level keys, and a comment cannot start with a
     dash. It answers one question — has the list changed since this copy was
     built — and the page keeps its build-time detail either way, because
     rebuilding the whole work list in the browser would mean shipping a parser
     we would then have to trust. */
  function queueIds(text) {
    var lines = text.split("\\n"), sec = null, out = {tasks: [], backlog: []};
    for (var i = 0; i < lines.length; i++) {
      var L = lines[i];
      if (/^tasks:\\s*$/.test(L)) { sec = "tasks"; continue; }
      if (/^backlog:\\s*$/.test(L)) { sec = "backlog"; continue; }
      if (/^[A-Za-z_][\\w-]*:/.test(L)) { sec = null; continue; }
      var m = /^- id:\\s*(\\S+)/.exec(L);
      if (m && sec) out[sec].push(m[1]);
    }
    return out;
  }
  function readQueue() {
    var note = document.getElementById("q-live");
    if (!note) return;
    fetch(QUEUE_URL + "?_=" + bust(), {cache: "no-store"})
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.text(); })
      .then(function (t) {
        var live = queueIds(t);
        var same = live.tasks.join() === BUILT_QUEUE.tasks.join() &&
                   live.backlog.join() === BUILT_QUEUE.backlog.join();
        if (same) {
          note.textContent = "your browser re-read the queue just now: unchanged since this " +
            "copy was built — " + live.tasks.length + " runnable, " + live.backlog.length +
            " planned.";
        } else {
          note.textContent = "your browser re-read the queue just now and it has CHANGED since " +
            "this copy was built: " + live.tasks.length + " runnable and " + live.backlog.length +
            " planned now, against " + BUILT_QUEUE.tasks.length + " and " +
            BUILT_QUEUE.backlog.length + " below. The detail below is the older reading.";
        }
      })
      .catch(function (e) {
        note.textContent = "the queue could not be re-read just now (" + e.message +
          "), so the list below is the queue as this copy was built.";
      });
  }

  /* ---- the render box's own queue, live ---------------------------------- */
  /* THE FIX FOR "why is the status only updating when i remind you about it".
     The tile below used to print pipeline/measured/box-queue.yaml, a file that
     changed only when a session hand-committed it, so its "measured" stamp was
     really a record of the last time somebody was nagged. The box publishes its
     own queue every five minutes; this reads that.

     WHAT IS LIVE AND WHAT IS NOT. The COUNTS come off the box. The MEDIANS the
     estimate multiplies them by are baked into the page, because they are
     measured over days of finished jobs and do not move in five minutes. So a
     live count times a slow median — the same arithmetic box_queue_eta() does at
     build time, deliberately, so the two cannot disagree about what a queue of
     two LTX takes means.

     FOUR WAYS IT DECLINES, and none of them blanks the tile: the fetch fails,
     the file has no queue block (an old publish, or the daemon has not been
     restarted onto the new code yet), the box could not read its own queue, or
     the reading is older than BOX_STALE. The first three keep the baked numbers
     and say the live path is unavailable; the last shows the numbers and says
     how old they are instead of calling them current. */
  function estimate(q) {
    /* → {minutes, basis} or null. Mirrors box_queue_eta(): per-kind when the mix
       accounts for every job, a rough count × pooled median otherwise, and
       NOTHING when there is no median to multiply by. */
    var jobs = (q.ready || 0) + (q.running || 0);
    if (!jobs) return {minutes: 0, basis: "none"};
    var kinds = q.kinds, total = 0, counted = 0, k;
    if (kinds) {
      for (k in kinds) if (Object.prototype.hasOwnProperty.call(kinds, k)) {
        counted += kinds[k];
        total += kinds[k] * (BOX_MEDIANS[k] || BOX_MEDIAN_FALLBACK || 0);
      }
      /* a mix that does not add up is a reading of a queue that has moved */
      if (counted === jobs && total > 0) return {minutes: Math.round(total), basis: "kinds"};
    }
    if (BOX_MEDIAN_FALLBACK) {
      return {minutes: Math.round(jobs * BOX_MEDIAN_FALLBACK), basis: "rough"};
    }
    return null;
  }
  function hoursWords(min) {
    /* build_sim.hours_words, to the character — the baked copy and the live copy
       of this sentence have to read the same or the tile flickers between two
       spellings of the same number. */
    if (!min) return "";
    return min < 90 ? min + " min" : "about " + (min / 60).toFixed(1) + " h";
  }
  function boxSay(nText, nCls, lText, count, notice) {
    var n = document.getElementById("q-tile-n"), l = document.getElementById("q-tile-l");
    if (n && nText !== null) { n.textContent = nText; n.className = nCls; }
    if (l && lText !== null) l.textContent = lText;
    var c = document.getElementById("q-count");
    if (c && count !== null) c.textContent = count;
    var p = document.getElementById("q-notice");
    if (p && notice !== null) p.textContent = notice;
  }
  function boxStale(why) {
    /* Never blank, never a guess: the baked numbers stand and the page says the
       live path is down and how old what you are looking at therefore is. */
    var p = document.getElementById("q-notice");
    if (p) {
      p.textContent = p.textContent.replace(/\\s*Live refresh[^]*$/, "") +
        " Live refresh unavailable (" + why + "); these are the numbers as of " +
        BOX_BAKED + ", when this copy was built.";
    }
  }
  /* ---- what the card is making, behind the fold ------------------------- */
  /* Rendered from the SAME telemetry object the tile above already fetched, so
     opening the dropdown costs no extra request — only the frames themselves,
     and only once someone asks to see them.

     Every value here was written by a machine, so it reaches the DOM through
     textContent and setAttribute and never through innerHTML, and each media
     path is checked against one shape before it becomes a URL. A status page
     that injected whatever a render wrote into its filenames would be a strange
     way to end up with a cross-site scripting hole. */
  var lastTel = null;
  function safePath(p) {
    /* farm-out/<dir>/<file>, and nothing that could climb out of it or point
       somewhere else entirely. */
    return typeof p === "string" && /^farm-out\\/[\\w.\\-\\/]+$/.test(p) &&
           p.indexOf("..") === -1 ? p : null;
  }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function sizeWords(b) {
    if (!b && b !== 0) return "";
    return b >= 1048576 ? (b / 1048576).toFixed(1) + " MB" : Math.round(b / 1024) + " kB";
  }
  function renderPeek() {
    var body = document.getElementById("q-peek-body");
    var peek = document.getElementById("q-peek");
    if (!body || !peek || !peek.open) return;
    body.textContent = "";
    if (!lastTel) {
      body.appendChild(el("p", "mono", "The live view is unavailable just now — the " +
        "render box's report could not be read, so this page will not guess at what " +
        "it is doing. The queue numbers above are the ones this copy was built with."));
      return;
    }
    var q = lastTel.queue || {}, cur = q.current || {};

    /* --- what is on the card this minute --- */
    var now = el("p", "peek-now");
    if (q.running && (cur.task || q.running_job)) {
      var what = cur.beat ? "Beat " + cur.beat : "A job";
      var b = el("b", null, what + (cur.node ? " of " + cur.node : ""));
      now.appendChild(b);
      var bits = [];
      if (cur.task) bits.push("job " + cur.task);
      if (cur.kind === "ltx") bits.push("a motion take");
      else if (cur.kind === "still") bits.push("a still");
      else if (cur.kind === "charref") bits.push("a character reference");
      if (cur.attempt) bits.push("attempt " + cur.attempt);
      now.appendChild(document.createTextNode(" — " + bits.join(" · ")));
      if (cur.started_at) {
        now.appendChild(document.createTextNode(" · started "));
        now.appendChild(ageEl(cur.started_at));
      }
      var est = BOX_MEDIANS[cur.kind] || BOX_MEDIAN_FALLBACK;
      if (est) {
        now.appendChild(document.createTextNode(
          " · jobs of this kind have taken about " + hoursWords(Math.round(est)) +
          ", measured on this box"));
      }
      if (typeof q.running_log_age_sec === "number") {
        now.appendChild(document.createTextNode(
          " · it last wrote to its log " + words(q.running_log_age_sec)));
      }
      if (cur.makes && cur.makes.length) {
        now.appendChild(document.createElement("br"));
        now.appendChild(document.createTextNode("It is making: " + cur.makes.join(", ")));
      }
    } else if (q.running) {
      now.textContent = "One job is rendering, but its record could not be read, so " +
        "this page will not say which.";
    } else {
      now.textContent = "Nothing is rendering on the card at the moment.";
    }
    body.appendChild(now);

    /* --- what came off it most recently --- */
    var res = lastTel.results;
    if (!res || res.error || !res.items || !res.items.length) {
      body.appendChild(el("p", "mono", res && res.error
        ? "Finished frames could not be listed just now (" + res.error + ")."
        : "Nothing has been published off the box yet. Finished frames appear here " +
          "once its courier pushes them."));
      return;
    }
    var strip = el("div", "peek-strip");
    var shown = 0;
    for (var i = 0; i < res.items.length; i++) {
      var it = res.items[i], path = safePath(it.path);
      if (!path) continue;
      var url = RAW_BASE + "/" + (res.branch || "farm-results-rtx5090") + "/" + path;
      var fig = el("figure", "peek-fig"), media;
      if (it.kind === "video") {
        media = document.createElement("video");
        media.className = "shot";
        media.setAttribute("preload", "none");      /* never pull 40 MB unasked */
        media.setAttribute("controls", "");
        media.setAttribute("playsinline", "");
        var poster = safePath(it.poster);
        if (poster) {
          media.setAttribute("poster", RAW_BASE + "/" +
            (res.branch || "farm-results-rtx5090") + "/" + poster);
        }
        media.setAttribute("src", url);
      } else {
        media = document.createElement("img");
        media.className = "shot";
        media.setAttribute("loading", "lazy");      /* only what scrolls into view */
        media.setAttribute("decoding", "async");
        media.setAttribute("alt", it.name || "a frame the box rendered");
        media.setAttribute("src", url);
      }
      /* THE ONLY AUTHORITATIVE FRESHNESS CHECK. The box knows the file exists on
         its own disk; whether the courier has pushed it is a question only the
         branch can answer, and this is the browser asking. */
      (function (figure, item) {
        media.onerror = function () {
          var miss = el("div", "shot peek-miss",
            "not on the branch yet — the box has rendered it but its courier has " +
            "not pushed it");
          if (figure.firstChild) figure.replaceChild(miss, figure.firstChild);
        };
      })(fig, it);
      fig.appendChild(media);
      var cap = el("figcaption", "peek-cap", (it.name || "") + " · ");
      if (it.at) cap.appendChild(ageEl(it.at));
      if (it.bytes) cap.appendChild(document.createTextNode(" · " + sizeWords(it.bytes)));
      fig.appendChild(cap);
      strip.appendChild(fig);
      shown++;
    }
    if (!shown) {
      body.appendChild(el("p", "mono", "Nothing publishable was listed in the box's " +
        "last report."));
      return;
    }
    body.appendChild(el("p", "mono", "The " + shown + " newest file" +
      (shown === 1 ? "" : "s") + " the box has finished and published, newest first. " +
      "A frame appears here only after the box's courier pushes it, which is usually " +
      "moments after the job ends and longer when it is on battery or offline — so " +
      "the job running above will not be in this strip yet. Videos load nothing until " +
      "you press play."));
    body.appendChild(strip);
  }

  /* ---- the queue's own depth, over the last day -------------------------
     `queue.depth_series` is [[epoch, ready+running], ...], appended once per
     publish and trimmed to 24 h, and it arrives in the SAME telemetry object
     the tile above already fetched — so this costs no extra request. It is
     drawn here rather than at build time for the obvious reason: a build has
     no history to draw and would bake a picture that stopped moving.

     THE GAPS ARE THE POINT AND THE LINE MUST NOT CROSS THEM. A reading that
     FAILED is never recorded — no point at all, rather than a zero — because a
     zero written while the queue directory was unreadable draws a clean dip to
     empty across an outage, which is a picture of an idle box on a night it was
     full. So the series is cut into runs wherever two readings sit further
     apart than DEPTH_GAP, and each run is its own path. A zero that IS in the
     series is a real measurement of a real empty queue and is drawn.

     AND A BREAK IS NOT A FAULT, which the first wording quietly implied. The
     telemetry daemon is restarted by hand every time telemetry.py changes and
     each restart costs a publish or two, so the ordinary cause of a break in
     this line is a deploy — not a dead box. The sentence names both and
     diagnoses neither, because from the series alone the two are identical.

     And it is a STEP, not a slope: a reading is the depth until the next one
     replaces it, so the line holds its value and then jumps. Sloping between
     two samples would draw jobs arriving one at a time when in fact eight
     landed at once. */
  var DEPTH_MIN_POINTS = 4;   /* under this it is readings, not a shape */
  var DEPTH_GAP = 750;        /* 2.5 publish intervals — beyond this, a break */
  var SVGNS = "http://www.w3.org/2000/svg";

  function svgEl(tag, attrs) {
    var n = document.createElementNS(SVGNS, tag);
    for (var k in attrs) { if (attrs.hasOwnProperty(k)) n.setAttribute(k, attrs[k]); }
    return n;
  }
  function spanWords(sec) {
    /* A LENGTH, not an age — words() answers "how long ago" and says "just
       now" under 90 s, which is nonsense as the width of a chart. */
    if (sec < 5400) return Math.max(1, Math.round(sec / 60)) + " min";
    if (sec < 129600) return (sec / 3600).toFixed(1) + " h";
    return Math.round(sec / 86400) + " days";
  }
  function depthRuns(pts) {
    var runs = [], cur = [];
    for (var i = 0; i < pts.length; i++) {
      if (cur.length && pts[i][0] - cur[cur.length - 1][0] > DEPTH_GAP) {
        runs.push(cur); cur = [];
      }
      cur.push(pts[i]);
    }
    if (cur.length) runs.push(cur);
    return runs;
  }
  function drawDepth(q) {
    var wrap = document.getElementById("q-spark");
    var note = document.getElementById("q-spark-note");
    if (!wrap || !note) return;
    var old = wrap.querySelector("svg");
    if (old) wrap.removeChild(old);

    var pts = (q && q.depth_series) || null;
    if (!Object.prototype.toString.call(pts).match(/Array/)) {
      /* OPTIONAL FIELD, and absent for real reasons: an older publish, a box
         with no history yet, a queue block that is missing entirely. Words,
         never an empty chart — a flat line at zero is a claim. */
      note.textContent = "The box is not publishing queue history yet, so " +
        "there is no depth to draw. It starts keeping one on its next publish.";
      return;
    }
    /* Trust nothing about the shape of a file fetched off a branch. */
    var clean = [];
    for (var i = 0; i < pts.length; i++) {
      var p = pts[i];
      if (p && typeof p[0] === "number" && typeof p[1] === "number" && p[1] >= 0) {
        clean.push(p);
      }
    }
    clean.sort(function (a, b) { return a[0] - b[0]; });
    if (clean.length < DEPTH_MIN_POINTS) {
      note.textContent = "The box has published " + clean.length + " queue " +
        "reading" + (clean.length === 1 ? "" : "s") + " so far — it keeps one " +
        "every five minutes, and a few more make a shape worth drawing.";
      return;
    }

    var t0 = clean[0][0], t1 = clean[clean.length - 1][0];
    var span = Math.max(1, t1 - t0);
    /* The real peak and the scale are two different numbers. A day on which
       the queue was empty at every single reading has a real peak of ZERO, and
       saying "never more than one job waiting" about it — which an all-in-one
       vmax did — describes a queue that had work in it. The scale still needs a
       floor of 1 so the flat line has somewhere to sit. */
    var peak = 0;
    for (i = 0; i < clean.length; i++) { if (clean[i][1] > peak) peak = clean[i][1]; }
    var vmax = Math.max(1, peak);
    /* 4..294 rather than the full width: the newest-reading dot has a radius
       and would hang over the edge of its own viewBox at either end. */
    var X = function (t) { return 4 + 290 * (t - t0) / span; };
    var Y = function (v) { return 34 - 30 * (v / vmax); };

    var svg = svgEl("svg", {"class": "qspark-svg", viewBox: "0 0 300 40",
                            preserveAspectRatio: "none", role: "img"});
    svg.appendChild(svgEl("line", {"class": "qs-base", x1: 2, y1: 34, x2: 298, y2: 34}));
    var runs = depthRuns(clean), breaks = runs.length - 1;
    for (var r = 0; r < runs.length; r++) {
      var run = runs[r], d = "";
      for (i = 0; i < run.length; i++) {
        var x = X(run[i][0]), y = Y(run[i][1]);
        d += (i ? "H" + x.toFixed(1) + "V" + y.toFixed(1)
                : "M" + x.toFixed(1) + " " + y.toFixed(1));
      }
      /* Hold the last reading out to its own x only; never out to "now",
         which would claim a measurement nobody took. */
      if (run.length === 1) d += "h1.5";
      svg.appendChild(svgEl("path", {"class": "qs-ln", d: d}));
    }
    var lastP = clean[clean.length - 1];
    svg.appendChild(svgEl("circle", {"class": "qs-dot", cx: X(lastP[0]).toFixed(1),
                                     cy: Y(lastP[1]).toFixed(1), r: 2.2}));
    wrap.insertBefore(svg, note);

    var age = Math.max(0, Math.round(Date.now() / 1000 - lastP[0]));
    var deep = peak === 0 ? "empty every time it looked"
             : peak === 1 ? "never more than one job waiting"
             : "deepest " + peak + " jobs";
    /* THREE LINES ON A PHONE, not six. The first cut spelled out the publish
       cadence and the CDN arithmetic in full under a 44px chart, which is the
       page's old habit of answering with a paragraph. The caveats are real and
       kept; they are just said once and short. */
    note.textContent = "Queue depth, " + clean.length + " readings over " +
      spanWords(span) + " — " + deep + " · newest " + words(age) + "." +
      (breaks ? " The line breaks " + breaks + " time" + (breaks === 1 ? "" : "s") +
                " where no reading was published — a restart or a box gone " +
                "quiet — and this page will not guess across a gap." : "") +
      " A reading can be up to ten minutes behind the box.";
    svg.setAttribute("aria-label", note.textContent);
  }

  /* ---- the queue as blocks, redrawn from the box's own publish -------------
     The baked strip is a supervisor snapshot that may be an hour old; this one
     is the box's five-minute report, and it follows the SAME rules the builder
     followed. One block per job. The running one ringed. Every fill a green,
     because the strip is machine work and amber on this page means a person is
     holding something. A kind the report does not name gets the neutral block
     rather than being left out — a strip shorter than the count printed beside
     it is the wrong picture, and an unlabelled block is an honest one.

     WHAT A WAITING BLOCK MAY SAY. The box publishes counts by kind, never the
     names of the jobs still in the directory, so only the running block's
     tooltip carries a beat and a job id. Guessing one for a waiting block would
     be this section inventing the fact it exists to report.

     Nothing here touches innerHTML: every string in the report was written by a
     machine on the render box, and each reaches the DOM through textContent or
     setAttribute. */
  function kindClass(k) { return !k ? "k-unknown" : (QKIND_CSS[k] || "k-other"); }
  function kindOne(k) {
    return !k ? QKIND_UNKNOWN_ONE : (QKIND_ONE[k] || ("a " + k + " job"));
  }
  function kindMany(k) {
    return !k ? QKIND_UNKNOWN_MANY : (QKIND_MANY[k] || k);
  }
  function clearEl(n) { while (n.firstChild) n.removeChild(n.firstChild); }
  function queueBlocks(q) {
    var ready = q.ready || 0, running = q.running || 0, jobs = ready + running;
    var left = {}, k, i;
    if (q.kinds) {
      for (k in q.kinds) if (Object.prototype.hasOwnProperty.call(q.kinds, k)) {
        if (typeof q.kinds[k] === "number" && q.kinds[k] > 0) {
          left[k] = Math.floor(q.kinds[k]);
        }
      }
    }
    var runKind = (q.current && q.current.kind) || null, blocks = [];
    for (i = 0; i < running; i++) {
      var pick = (i === 0 && runKind && left[runKind]) ? runKind : null;
      if (!pick) {
        var best = null;
        for (k in left) {
          if (left[k] > 0 && (best === null || left[k] > left[best])) best = k;
        }
        pick = best;
      }
      if (pick) left[pick] -= 1;
      blocks.push({kind: pick, running: true});
    }
    var keys = [];
    for (k in left) if (left[k] > 0) keys.push(k);
    keys.sort();
    for (i = 0; i < keys.length; i++) {
      for (var j = 0; j < left[keys[i]]; j++) {
        blocks.push({kind: keys[i], running: false});
      }
    }
    while (blocks.length < jobs) blocks.push({kind: null, running: false});
    return blocks.slice(0, jobs);       /* an over-counting mix is trimmed */
  }
  function drawStrip(q, id, legId, cap, mini, idleText) {
    var wrap = document.getElementById(id);
    /* NO QUEUE BLOCK IS NOT AN EMPTY QUEUE. A report that carries no queue at
       all leaves the baked strip exactly where it was — drawing "card idle"
       over a reading nobody took is the guessed zero this whole page is
       arranged against, and it would be at its most convincing here. */
    if (!wrap || !q) return;
    var leg = legId ? document.getElementById(legId) : null;
    clearEl(wrap);
    if (leg) clearEl(leg);
    var base = "qstrip" + (mini ? " mini" : "");
    var blocks = q ? queueBlocks(q) : [];
    if (!blocks.length) {
      wrap.className = base + " empty";
      wrap.removeAttribute("role");
      wrap.removeAttribute("aria-label");
      wrap.appendChild(el("span", "qidle", idleText));
      return;
    }
    wrap.className = base;
    var counts = {}, run = 0, i;
    for (i = 0; i < blocks.length; i++) {
      counts[blocks[i].kind || ""] = (counts[blocks[i].kind || ""] || 0) + 1;
      if (blocks[i].running) run++;
    }
    var shown = Math.min(blocks.length, cap);
    for (i = 0; i < shown; i++) {
      var b = blocks[i];
      var cell = el("span", "qblk " + kindClass(b.kind) + (b.running ? " run" : ""));
      var tip = (b.running ? "rendering now — " : "waiting — ") + kindOne(b.kind);
      if (b.running && q.current) {
        var named = [];
        if (q.current.beat || q.current.beat === 0) named.push("beat " + q.current.beat);
        if (q.current.node) named.push(q.current.node);
        if (q.current.task) named.push("job " + q.current.task);
        if (named.length) tip += " · " + named.join(" · ");
      }
      cell.setAttribute("title", tip);
      wrap.appendChild(cell);
    }
    var hidden = blocks.length - shown;
    if (hidden) {
      var more = el("span", "qblk qplus", "+" + hidden);
      more.setAttribute("title", hidden + " more queued job" +
        (hidden === 1 ? "" : "s") + ", not drawn");
      wrap.appendChild(more);
    }
    wrap.setAttribute("role", "img");
    wrap.setAttribute("aria-label", blocks.length + " job" +
      (blocks.length === 1 ? "" : "s") + " on the render box, " + run +
      " rendering — one block each, colour by kind");
    if (!leg) return;
    var order = [];
    for (var kk in counts) {
      if (Object.prototype.hasOwnProperty.call(counts, kk)) order.push(kk);
    }
    order.sort(function (a, b2) {
      return counts[b2] - counts[a] || (a < b2 ? -1 : 1);
    });
    for (i = 0; i < order.length; i++) {
      var key = order[i] || null, item = el("span", "qkey");
      item.appendChild(el("i", "qsw " + kindClass(key)));
      item.appendChild(document.createTextNode(counts[order[i]] + " " + kindMany(key)));
      leg.appendChild(item);
    }
  }

  /* ---- what the card has on it, as a thing to look at ----------------------
     The beat number is the largest type in the section because it is the fact a
     reader wants first. The bar under it is ELAPSED AGAINST THIS KIND'S MEDIAN
     and is labelled as an estimate every time it is drawn: nothing on the box
     reports how far through a job it is, so a completion percentage here would
     be invented, and an invented percentage that happens to look plausible is
     the worst thing this page could publish about a running render. */
  function drawNow(q) {
    var wrap = document.getElementById("q-now");
    /* Same rule as the strip: no queue block, no claim — the baked sentence
       stands rather than being replaced by "nothing is rendering". */
    if (!wrap || !q) return;
    clearEl(wrap);
    var cur = q.current || {};
    if (!q.running) {
      wrap.appendChild(el("p", "mono", "Nothing is rendering on the card right now."));
      return;
    }
    if (!cur.task && !q.running_job) {
      wrap.appendChild(el("p", "mono", "A job is rendering, but the box's report " +
        "does not say which, so this page will not name one."));
      return;
    }
    var card = el("div", "qnow-card"), slot = el("div", "qnow-beat");
    if (cur.beat || cur.beat === 0) {
      slot.appendChild(el("span", "qnow-n", String(cur.beat)));
      slot.appendChild(el("span", "qnow-lab", "beat"));
    } else {
      slot.appendChild(el("span", "qnow-n", "\\u2014"));
      slot.appendChild(el("span", "qnow-lab", "no beat"));
    }
    card.appendChild(slot);

    var main = el("div", "qnow-main");
    var head = kindOne(cur.kind || null);
    head = head.charAt(0).toUpperCase() + head.slice(1);
    if (cur.node) head += " for " + cur.node;
    if (cur.attempt) head += " · attempt " + cur.attempt;
    main.appendChild(el("span", "qnow-t", head));

    var med = BOX_MEDIANS[cur.kind] || BOX_MEDIAN_FALLBACK || 0;
    var run = cur.started_at
      ? Math.max(0, Math.round(Date.now() / 1000 - cur.started_at)) : null;
    if (run !== null && med > 0) {
      /* SVG rather than a styled div: the same drawing language as the
         sparkline and the charts, and one less inline style on the page. */
      var frac = run / 60 / med, over = frac >= 1;
      var w = Math.max(2, Math.min(100, Math.round(frac * 100)));
      var svg = svgEl("svg", {"class": "qnow-svg", viewBox: "0 0 100 6",
                              preserveAspectRatio: "none", role: "img"});
      svg.appendChild(svgEl("rect", {"class": "qb-track", x: 0, y: 0,
                                     width: 100, height: 6, rx: 3}));
      svg.appendChild(svgEl("rect", {"class": "qb-fill" + (over ? " over" : ""),
                                     x: 0, y: 0, width: w, height: 6, rx: 3}));
      svg.setAttribute("aria-label", "running " + spanWords(run) + " against a " +
        hoursWords(Math.round(med)) + " median for this kind — an estimate, not " +
        "a measurement of how far through it is");
      main.appendChild(svg);
    }
    var bits = [];
    if (run !== null) bits.push("running " + spanWords(run));
    if (med > 0) {
      bits.push("about " + hoursWords(Math.round(med)) + " is typical for this " +
        "kind on this box — an estimate, not progress");
    }
    if (typeof q.running_log_age_sec === "number") {
      bits.push("last wrote to its log " + words(q.running_log_age_sec));
    }
    if (bits.length) main.appendChild(el("span", "qnow-cap", bits.join(" \\u00b7 ")));
    if (cur.makes && cur.makes.length) {
      main.appendChild(el("span", "qnow-makes", "making " + cur.makes.join(", ")));
    }
    card.appendChild(main);
    wrap.appendChild(card);
  }

  /* ---- the box's remaining facts, one badge each --------------------------
     Each of these used to be a comma in a sentence that ran to four lines. A
     badge is not decoration here: "nothing is draining the queue" is the single
     most important thing this section can say, and it was the fifth clause. */
  function drawChips(d, q) {
    var wrap = document.getElementById("q-chips");
    if (!wrap || !q) return;
    clearEl(wrap);
    function chip(cls, big, rest) {
      var c = el("span", "qchip" + (cls ? " " + cls : ""));
      if (big) c.appendChild(el("b", null, big));
      c.appendChild(document.createTextNode((big ? " " : "") + rest));
      wrap.appendChild(c);
    }
    if (typeof q.done_24h === "number") chip("good", String(q.done_24h), "finished in 24 h");
    if (typeof q.done_today === "number") chip("good", String(q.done_today), "finished today");
    /* RED ONLY FOR WHAT IS UNEXAMINED. ACK_FAILED is how many of these are
       triaged in the repo; a pile that is fully written down is a fact, not an
       alarm, and anything above that line is the thing worth a red chip. */
    if (typeof q.failed === "number" && q.failed > 0) {
      var freshFailed = q.failed - ACK_FAILED;
      if (ACK_FAILED <= 0) {
        chip("bad", String(q.failed), "sitting failed");
      } else if (freshFailed > 0) {
        chip("bad", String(q.failed), "sitting failed \\u2014 " + freshFailed +
          " not yet triaged");
      } else {
        chip("", String(q.failed), "failed, all triaged \\u2014 " + ACK_DOC);
      }
    }
    if (q.runner_alive === false) {
      chip("bad", null, "nothing is draining this queue — the box's runner is not running");
    }
    var pw = d && d.power;
    if (pw && pw.ac === false) {
      chip("bad", typeof pw.battery_pct === "number" ? pw.battery_pct + "%" : null,
        "on battery — it renders well below the speed those medians were measured at");
    }
  }

  function readBoxQueue() {
    if (!document.getElementById("q-tile-n") && !document.getElementById("q-notice")) return;
    function grab(u) {
      return fetch(u + "?_=" + bust(), {cache: "no-store"})
        .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); });
    }
    grab(BOX_TEL)
      .catch(function () { return grab(BOX_TEL_LEGACY); })
      .then(function (d) {
        lastTel = d;
        renderPeek();            /* no-op unless the fold is already open */
        var q = d && d.queue;
        /* BEFORE the count checks below, which throw. The pictures each have
           their own honest answer for a missing queue block and should give it
           rather than inheriting the tile's "live refresh unavailable". */
        drawDepth(q);
        drawNow(q);
        drawChips(d, q);
        drawStrip(q, "q-strip", "q-legend", QBLOCK_CAP, false,
                  "card idle — nothing queued, nothing rendering");
        if (!q) throw new Error("the box is publishing vitals but not yet its queue");
        if (q.error) throw new Error("the box could not read its own queue: " + q.error);
        if (typeof q.ready !== "number" && typeof q.running !== "number") {
          throw new Error("the queue reading carries no counts");
        }
        var ready = q.ready || 0, running = q.running || 0, jobs = ready + running;
        /* AGE OFF THE FILE'S OWN STAMP AGAINST THE READER'S CLOCK. Not the
           committing laptop's — that drifted a day in August and would have had
           the page reporting tomorrow's queue. */
        var age = Math.max(0, Math.round(Date.now() / 1000 - q.at));
        var fresh = age <= BOX_STALE * 60;
        /* THE FRESHNESS GOES ON THE TILE, not only in the paragraph below it.
           The complaint that produced all of this was about the tile, and a
           reader who has to scroll to a work list to find out how old a number
           is will read the number as now. Short form on the tile, the full
           sentence in the section. */
        var whenShort = "measured " + words(age) +
                        (fresh ? "" : ", and the box has stopped publishing");
        var when = fresh ? "measured " + words(age) + " by the box itself"
                         : "measured " + words(age) + " — the box has stopped " +
                           "publishing, so this is the last reading, not a current one";
        var est = estimate(q);

        /* the glance tile. A stale reading keeps its number — it is the last
           thing we actually know — but loses the styling that says "current"
           and carries how old it is in the same breath. */
        if (jobs && est && est.minutes) {
          /* The "N rendering, M waiting" clause came off this label on
             2026-08-14: the blocks under it say the same thing without being
             read, and the founder's standing complaint is the page printing
             one fact twice. */
          boxSay("~" + hoursWords(Math.max(1, est.minutes)), fresh ? "sn" : "sn none",
                 "of work queued on the render box · " + (est.basis === "rough"
                   ? "an estimate, and a rough one: a median job times the count"
                   : "an estimate, each job timed against past jobs of its kind") +
                 " · " + whenShort,
                 null, null);
        } else if (jobs) {
          boxSay(String(jobs), fresh ? "sn" : "sn none",
                 "jobs on the render box · no job times have been measured, so " +
                 "this page will not say how long that is · " + whenShort, null, null);
        } else {
          boxSay("0", fresh ? "sn zero" : "sn none",
                 "nothing queued on the render box, " + whenShort, null, null);
        }

        /* THE CAPTION, and it is one line now (Roman, 2026-08-14: "can you make
           the queue more visuals and less text?"). Everything that used to be
           strung onto this sentence has a picture of its own above it: the
           depth is the strip, the running job is the card, the failures, the
           day's finished count, a dead runner and a card on battery are badges.
           What survives in words is what no picture on this page can carry —
           whether the time is an estimate, and how old the reading is. */
        var bits = running + " rendering, " + ready + " waiting";
        if (jobs && est && est.minutes) {
          bits += " · ~" + hoursWords(Math.max(1, est.minutes)) +
                  (est.basis === "rough" ? ", roughly estimated" : ", estimated");
        }
        bits += " · " + when + ".";
        boxSay(null, null, null, String(jobs), bits);
      })
      .catch(function (e) { boxStale(e.message); });
  }

  function refresh() {
    var lis = document.querySelectorAll("#machlist li[data-branch]");
    for (var i = 0; i < lis.length; i++) {
      readLog(lis[i]);
      if (lis[i].getAttribute("data-tel")) readVitals(lis[i]);
    }
    readQueue();
    readBoxQueue();
  }
  var peekEl = document.getElementById("q-peek");
  if (peekEl) {
    /* Nothing is fetched until it is opened, and the first open may land before
       the box's report has arrived — renderPeek says so rather than sitting
       blank, and the fetch calls it again when it lands. */
    peekEl.addEventListener("toggle", renderPeek);
  }
  tick();
  setInterval(tick, 20000);
  refresh();
  /* five minutes: the fastest anything upstream is written, and slow enough
     that a tab left open all day is a handful of CDN reads. */
  setInterval(function () { if (!document.hidden) refresh(); }, 300000);
})();
"""


SIM_CSS = """
/* ---- the studio page (tokens from the theme). The animated lot, the walkers
   and the record's clerical styles died in the 2026-08-11 revamp — what is
   left is the machine list, the grove, and the work rows. ---- */
.machlist { list-style: none; padding: 0; margin: .5rem 0 0; }
.machlist li { padding: .6rem 0; border-bottom: 1px solid var(--line-soft);
  font-size: .92rem; }
.machlist li:last-child { border-bottom: 0; }
.machlist .mico { margin-right: .3rem; }
.machlist .chip { margin-left: .35rem; vertical-align: .05em; }
.machlist .mstate { margin: .25rem 0 .1rem; }
.machlist .why { color: var(--muted); font-size: .84rem; }
.grove { text-align: center; margin: 0 0 1.2rem; }
.canopy { display: grid; grid-template-columns: repeat(5, 2.1rem); gap: .1rem;
  justify-content: center; }
.leaf { font-size: 1.45rem; text-decoration: none; }
.leaf.bud { filter: grayscale(1) brightness(.5); }
/* leaf tiers — the tooltip carries the words, the tint is only a hint */
.leaf.pick { filter: none; text-decoration: none;
  text-shadow: 0 0 10px rgba(255,199,106,.9); }
.leaf.still { filter: saturate(.6); }
.trunky { font-size: 4.4rem; line-height: 1; }
.grove .label { font: 600 .8rem/1.6 var(--mono); color: var(--muted); }
.spend { font: 600 .8rem/1.6 var(--mono); color: var(--faint); text-align: center; }
.spend b { color: var(--sap); }
/* ---- the infra meter. Fetched live by the reader and can be absent, so it
   must never dress as a repo-checkable number. ---- */
.infra { margin: 1rem auto 0; max-width: 44rem; text-align: center;
  background: var(--panel-2); border: 1px solid var(--line); border-radius: 12px;
  padding: .8rem .9rem; }
.infra .n { font: 700 1.5rem/1.2 var(--mono); color: var(--sap);
  font-variant-numeric: tabular-nums; }
.infra .n.none { font-size: .8rem; font-weight: 600; color: var(--faint);
  line-height: 1.6; }
.infra .u { font: 500 .78rem/1.6 var(--mono); color: var(--muted); }
.infra .note { font: 400 .74rem/1.7 var(--sans, inherit); color: var(--faint);
  margin: .5rem 0 0; text-align: left; }
.scenes, .quests { list-style: none; padding: 0; margin: .4rem 0 0; }
.scenes li, .quests li { padding: .55rem 0; border-bottom: 1px solid var(--line-soft); }
.scenes li:last-child, .quests li:last-child { border-bottom: 0; }
.mono { font: 500 .76rem/1.6 var(--mono); color: var(--faint); }
.scroll { overflow-x: auto; }
.summary { font: 600 .84rem/1.7 var(--mono); color: var(--muted); }
.summary b { color: var(--leaf); }
.prod-row { background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 14px; padding: .7rem .95rem;
  margin: .6rem 0; font-size: .92rem; }
.prod-row .why { color: var(--muted); font-size: .84rem; }
.whyfoot { font: 500 .8rem/1.7 var(--mono); color: var(--faint); }

/* ---- ages, states and the blocked list ----------------------------------
   Every number on this page that is a DURATION wears .age, so a reader can see
   at a glance which words are counting and which are fixed. The tabular figures
   stop the list twitching as the browser rewrites them each 20 s. ---- */
.age { font-variant-numeric: tabular-nums; white-space: nowrap; }
/* the same slot when there is no duration to put in it — free to wrap, because
   what goes here is a sentence explaining why there is no number */
.noage { color: var(--faint); }
.livemark { font: 500 .76rem/1.6 var(--mono); color: var(--faint); }
/* ---- the queue, drawn (Roman, 2026-08-14: "more visuals and less text").
   One block per queued job, the running one ringed and breathing, so depth is
   SEEN rather than read off a sentence.

   EVERY FILL IS A GREEN, and that is the load-bearing part. The site's colour
   law is --leaf for the machine's own work and --sap for what is waiting on the
   author; a queued render waits on a card, never on a person, so an amber block
   in this strip would say the opposite of what is true. Kinds are told apart by
   the three green steps AND by the key underneath AND by each block's tooltip —
   never by hue alone, which is the same rule the charts follow.

   The blocks are rem-sized and the row wraps, so a queue eight deep is one line
   on a laptop and two on a phone without a breakpoint. ---- */
.qstrip { display: flex; flex-wrap: wrap; align-items: flex-end; gap: .3rem;
  margin: .55rem 0 .45rem; }
.qblk { display: block; width: .8rem; height: 1.45rem; border-radius: 3px;
  border: 1px solid transparent; background: var(--leaf-dim); }
.qblk.k-ltx, .qsw.k-ltx { background: var(--leaf-deep); }
.qblk.k-still, .qsw.k-still { background: var(--leaf-dim); }
.qblk.k-charref, .qsw.k-charref { background: var(--leaf); }
.qblk.k-inpaint, .qsw.k-inpaint { background: var(--leaf-deep); opacity: .55; }
.qblk.k-other, .qblk.k-unknown, .qsw.k-other, .qsw.k-unknown {
  background: var(--line); }
/* the one a card actually has on it: taller, ringed, and breathing */
.qblk.run { height: 1.95rem; border-color: var(--leaf);
  box-shadow: 0 0 0 2px var(--leaf-dim); animation: qpulse 1.9s ease-in-out infinite; }
@keyframes qpulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
.qblk.qplus { width: auto; padding: 0 .35rem; background: none; border: 0;
  font: 600 .68rem/1.45rem var(--mono); color: var(--faint); }
/* EMPTY IS A STATE, not a bare zero — the founder's standing rule about numbers
   nobody measured, applied to a picture. */
.qstrip.empty { margin-bottom: .35rem; }
.qidle { font: 600 .72rem/1.5 var(--mono); color: var(--faint);
  border: 1px dashed var(--line); border-radius: 7px; padding: .3rem .6rem; }
.qlegend { display: flex; flex-wrap: wrap; gap: .05rem .85rem; margin: 0 0 .3rem; }
.qlegend:empty { display: none; }
.qkey { display: inline-flex; align-items: center; gap: .32rem;
  font: 500 .68rem/1.6 var(--mono); color: var(--muted); }
.qsw { display: inline-block; width: .58rem; height: .58rem; border-radius: 2px;
  background: var(--leaf-dim); }
.qcap { font: 500 .72rem/1.5 var(--mono); color: var(--muted); margin: 0; }
.qsub { font: 600 .72rem/1.5 var(--mono); color: var(--muted); margin: .7rem 0 0;
  text-transform: uppercase; letter-spacing: .06em; }
.qsub .count { color: var(--leaf); }
/* ---- the queue's own section, first thing on the page (Roman, 2026-08-14:
   "shouldnt the queue be at the top?"). It is the only live section here, so it
   gets the panel treatment the snapshots below do not: a reader should be able
   to tell at a glance which part of this page is still moving. ---- */
.qsec { margin: 1rem 0 1.4rem; padding: .9rem 1rem 1rem;
  border: 1px solid var(--line); border-radius: 14px;
  background: linear-gradient(180deg, var(--panel-2), var(--panel));
  box-shadow: var(--shadow); }
.qsec > h2 { margin-top: 0; }
.qsec .chead { margin: -.2rem 0 .5rem; }
/* The headline number — the glance tile's markup, in its new home, and GREEN
   where the tile was amber. In the strip it was one cell among five and took
   the strip's house colour; here it heads a section that is entirely the
   machine's work, and the colour law says that is --leaf. */
.qhead .sn { display: block; font: 700 1.9rem/1.15 var(--mono); color: var(--leaf); }
.qhead .sn.none { font-size: .9rem; font-weight: 600; color: var(--faint); }
.qhead .sn.zero { color: var(--faint); }
.qhead .sl { display: block; font: 500 .7rem/1.45 var(--mono); color: var(--muted); }

/* ---- what the card has on it, as a thing to look at rather than read ----
   The beat number is the biggest type in the section because it is the one fact
   a reader wants; the bar under it is ELAPSED AGAINST THIS KIND'S MEDIAN and is
   never called progress. Nothing on the box reports how far through a job it
   is, so a percentage would be invented. ---- */
.qnow { margin: .5rem 0 .2rem; }
.qnow .mono { display: block; margin: 0; }
.qnow-card { display: flex; align-items: center; gap: .75rem; padding: .55rem .7rem;
  border: 1px solid var(--line); border-left: 3px solid var(--leaf);
  border-radius: 10px;
  background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.qnow-beat { flex: 0 0 auto; min-width: 3rem; text-align: center; }
.qnow-n { display: block; font: 700 1.9rem/1 var(--mono); color: var(--leaf);
  font-variant-numeric: tabular-nums; }
.qnow-lab { display: block; font: 600 .56rem/1.7 var(--mono); color: var(--faint);
  letter-spacing: .1em; text-transform: uppercase; }
.qnow-main { flex: 1 1 auto; min-width: 0; }
.qnow-t { display: block; font: 600 .86rem/1.4 var(--body); color: var(--ink); }
.qnow-svg { display: block; width: 100%; height: 6px; margin: .4rem 0 .3rem; }
.qnow-svg .qb-track { fill: var(--line-soft); }
.qnow-svg .qb-fill { fill: var(--leaf); }
/* past the median the fill is the deeper green, not amber: running long is the
   machine's business too, and amber on this page means a person is holding it */
.qnow-svg .qb-fill.over { fill: var(--leaf-deep); }
.qnow-cap, .qnow-makes { display: block; font: 500 .68rem/1.45 var(--mono);
  color: var(--muted); }
.qnow-makes { color: var(--faint); word-break: break-word; }

/* ---- the box's remaining facts as badges, one number each ---------------- */
.qchips { display: flex; flex-wrap: wrap; gap: .3rem; margin: .4rem 0 0; }
.qchips:empty { display: none; }
.qchip { font: 600 .66rem/1 var(--mono); color: var(--muted); padding: .32rem .52rem;
  border: 1px solid var(--line); border-radius: 999px; }
.qchip b { color: var(--ink); font-weight: 700; }
.qchip.good { border-color: var(--leaf-deep); color: var(--leaf); }
.qchip.good b { color: var(--leaf); }
.qchip.bad { border-color: var(--alarm, #e2564d); color: var(--alarm, #e2564d); }
.qchip.bad b { color: var(--alarm, #e2564d); }
.qmeth { margin: .5rem 0 0; }

/* ---- the queue's depth over the last day. Drawn by the reader's browser, so
   it must look deliberate while empty and must never reflow the page around
   itself when the line arrives — hence the fixed aspect on the svg. The stroke
   is non-scaling so a sparkline stretched to 300 units wide by 40 tall keeps an
   even 1.6px line instead of a hairline that fattens horizontally. ---- */
.qspark { margin: .5rem 0 0; }
.qspark-svg { display: block; width: 100%; height: 44px; overflow: visible; }
.qspark-svg .qs-base { stroke: var(--line); stroke-width: 1;
  vector-effect: non-scaling-stroke; }
.qspark-svg .qs-ln { fill: none; stroke: var(--leaf); stroke-width: 1.6;
  stroke-linejoin: round; stroke-linecap: round;
  vector-effect: non-scaling-stroke; }
.qspark-svg .qs-dot { fill: var(--sap); stroke: var(--bg); stroke-width: 1;
  vector-effect: non-scaling-stroke; }
.qspark .mono { margin: .25rem 0 0; display: block; }

/* ---- "what the card is making right now" — the fold over the live view.
   Everything in here arrives from the box after the page has loaded, so it must
   look deliberate while empty and must never reflow the page around it. ---- */
.peek { margin: .6rem 0 0; border: 1px solid var(--line); border-radius: 10px;
  background: var(--panel-2); }
.peek > summary { cursor: pointer; padding: .55rem .75rem; font: 600 .84rem/1.5 var(--mono);
  color: var(--muted); list-style: none; }
.peek > summary::-webkit-details-marker { display: none; }
.peek > summary::before { content: "▸ "; color: var(--sap); }
.peek[open] > summary::before { content: "▾ "; }
.peek > summary:hover { color: var(--ink); }
.peek-body { padding: .1rem .75rem .75rem; }
.peek-now { font-size: .9rem; margin: .2rem 0 .5rem; }
.peek-now b { color: var(--sap); }
.peek-strip { display: grid; gap: .6rem; grid-template-columns: repeat(auto-fill, minmax(9rem, 1fr));
  margin: .5rem 0 0; }
.peek-fig { margin: 0; min-width: 0; }
/* A fixed box before the media lands: without it every arriving frame shoves the
   rest of the page down, which on a slow line is the strip flickering for
   seconds. */
.peek-fig .shot { display: block; width: 100%; aspect-ratio: 9 / 16; object-fit: cover;
  background: var(--panel); border: 1px solid var(--line); border-radius: 8px; }
.peek-cap { font: 500 .68rem/1.4 var(--mono); color: var(--faint); margin-top: .25rem;
  overflow-wrap: anywhere; }
.peek-miss { display: flex; align-items: center; justify-content: center; text-align: center;
  padding: .5rem; font: 500 .66rem/1.4 var(--mono); color: var(--faint); }
h3 .count, .bgroup .count { display: inline-block; font: 700 .68rem/1 var(--mono);
  color: var(--faint); border: 1px solid var(--line); border-radius: 999px;
  padding: .22rem .45rem; vertical-align: .12em; }
.bgroup { margin: 1rem 0 .2rem; }
.bgroup h3 { margin-bottom: .1rem; }
.blist { list-style: none; padding: 0; margin: .3rem 0 0; }
.blist li { padding: .55rem 0 .6rem; border-bottom: 1px solid var(--line-soft); }
.blist li:last-child { border-bottom: 0; }
.blist .why { color: var(--muted); font-size: .88rem; }
.quests .waited { display: inline-block; font: 700 .68rem/1 var(--mono);
  letter-spacing: .06em; text-transform: uppercase; color: var(--sap);
  border: 1px solid var(--sap-deep); border-radius: 999px; padding: .25rem .5rem;
  margin-right: .4rem; }
.quests .held { margin-top: .35rem; padding: .45rem .6rem; border-radius: 10px;
  background: var(--panel-2); border: 1px solid var(--line-soft);
  font: 500 .76rem/1.6 var(--mono); color: var(--faint); }
.quests .held b { color: var(--ink); }

/* ---- the quest board: real open requests, real reward, no points ---- */
.qboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: .7rem; margin: .8rem 0 .4rem; }
.quest { padding: .8rem .95rem .7rem; border: 1px solid var(--line); border-radius: 14px;
  background: linear-gradient(180deg, var(--panel-2), var(--panel)); font-size: .92rem; }
.quest b { font-family: var(--display); font-size: 1.02rem; }
.quest p { margin: .35rem 0 .45rem; color: var(--muted); font-size: .86rem; }
.quest .reward { font: 500 .72rem/1.5 var(--mono); color: var(--faint);
  border-top: 1px dashed var(--line-soft); padding-top: .45rem; margin-top: .2rem; }
.reward b { font: 700 .72rem/1.5 var(--mono); color: var(--sap); }
.quest.slim { display: flex; flex-direction: column; gap: .3rem; align-items: flex-start; }
.quest.slim .chip { margin: 0; }
.qnote { background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 14px; padding: .7rem .95rem;
  font-size: .9rem; color: var(--muted); }
.qnote .reward { display: block; border-top: 1px dashed var(--line-soft);
  padding-top: .4rem; margin-top: .5rem; font: 500 .72rem/1.5 var(--mono);
  color: var(--faint); }

/* ---- the growth meter: two file-existence facts per scene, nothing else ---- */
.growbar { height: 12px; max-width: 420px; margin: .7rem auto .35rem; overflow: hidden;
  border: 1px solid var(--line); border-radius: 999px; background: var(--code-bg); }
/* GREEN, not amber. Since the ETA bars and the tree above it took amber to mean
   "this one is the author's to answer", a full-width amber growth meter under
   the tree read as "97% is waiting on you" — the opposite of what it counts,
   which is steps already finished. */
.growbar i { display: block; height: 100%; background: var(--leaf); border-radius: 999px; }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; } }
"""


# ---- what the videos cost the internet ---------------------------------------
# Roman, 2026-08-10: "we need to add a bandwith stat to the dashboard so we know
# how much of the internet bandwidth is these videos taking."
#
# The true answer is Vercel's own transfer meter, and THIS ACCOUNT CANNOT READ
# IT. Checked 2026-08-11 against the live Hobby account that serves banyan.city:
# `vercel usage` returns "Costs not found (404)", and the endpoint underneath it,
# GET /v1/usage?from=&to= (ISO-8601 with milliseconds, both bounds), answers
#
#     This API endpoint is only available to Teams on the Pro or Enterprise plan.
#
# So there is no measurement to publish, and this page does not invent one. What
# it publishes instead is the one quantity it can actually measure — the bytes of
# video this build puts on the deploy — and it says on its face that this is a
# proxy. The distinction is the whole point: bytes published is what ONE visitor
# downloads watching everything once; bytes transferred is that multiplied by an
# audience nobody here can see. Never let the tile read as the second.
#
# The GitHub Pages mirror publishes no transfer figures through any API at all,
# so traffic that lands there is outside both numbers — said on the page too,
# because the mirror is where a share link can quietly send everyone.
VIDEO_EXT = (".mp4", ".webm", ".mov", ".m4v")

# Hobby's included Fast Data Transfer, for scale only. A cap this page prints
# next to a proxy must not read as "you have used X of Y" — it is there so a
# number in gigabytes means something to a reader who has no feel for gigabytes.
# Read off the docs table ("Usage summary") on 2026-08-11: Hobby 100 GB, Pro 1 TB.
HOBBY_TRANSFER_GB = 100
HOBBY_TRANSFER_SRC = "https://vercel.com/docs/limits"


def bytes_words(n: int) -> str:
    """Bytes in the largest unit that keeps the number readable."""
    if n >= 1024 ** 3:
        return f"{n / 1024 ** 3:.2f} GB"
    if n >= 1024 ** 2:
        return f"{n / 1024 ** 2:.0f} MB"
    if n >= 1024:
        return f"{n / 1024:.0f} kB"
    return f"{n} bytes"


def video_payload(out_dir) -> dict:
    """Bytes of published episode/animatic video. Fails SOFT — never raises.

    SCOPE, and why it is drawn exactly here. Only files in a genome's `leaves/`
    directory are counted — the episodes and animatics the players on the public
    pages point at. Two boundaries had to be respected at once:

    * Not the repo's video. `genomes/` alone carries ~695 MB of takes, alternates
      and provisional cuts that are NEVER copied to the deploy; measured
      2026-08-11, the repo holds 492 MB of video the site does not publish. A
      figure built from sources would have overstated egress by more than double.
    * Not a walk of the whole output either. build_site.main() copies the leaf
      media BEFORE it calls build_sim.build(), but the unlisted review area, the
      trial clips and the takes/clips galleries all land AFTER (build_site.py
      :3198-3309). Walking out_dir would therefore give one number during a full
      `build_site.py` run and a bigger one during a standalone `build_sim.py`
      against an already-populated tree. A stat that changes with which command
      produced it is not a stat. `leaves/` is the one set that is complete and
      identical either way.

    So the number means "what a visitor downloads watching the published show",
    which is the honest reading of the question, and the caveat below the tile
    names the unlisted areas this leaves out rather than quietly absorbing them.

    A build that cannot stat its own output must still produce a page, so every
    failure comes back as {"ok": False} and prints "unavailable" rather than a
    zero. A zero here would be the most reassuring possible answer to exactly the
    failure this exists to surface — the same contract the infra meter and the
    check-in logs above already hold themselves to.
    """
    out = Path(out_dir)
    # rglob over a directory that is not there yields nothing and raises
    # nothing, so the obvious spelling of this function returns a confident
    # 0 bytes on exactly the failure it exists to catch. Caught by
    # test_sim_strip.py before this ever reached the page. Both this and the
    # empty-walk case below are "unmeasured", not "zero".
    if not out.is_dir():
        return {"ok": False, "why": f"{out} is not a directory"}
    try:
        total, count, biggest = 0, 0, ("", 0)
        for p in out.rglob("*"):
            if (p.suffix.lower() not in VIDEO_EXT or p.parent.name != "leaves"
                    or not p.is_file()):
                continue
            size = p.stat().st_size
            total += size
            count += 1
            if size > biggest[1]:
                biggest = (p.name, size)
    except OSError as e:
        return {"ok": False, "why": _reason(e)}
    if not count:
        # The site has published video since its first episode. A walk that
        # finds none has failed to look in the right place — it has not
        # discovered that the show is silent.
        return {"ok": False, "why": "no published video found in the build output"}
    return {"ok": True, "bytes": total, "count": count,
            "biggest": biggest[0], "biggest_bytes": biggest[1]}


def bandwidth_html(pay: dict) -> str:
    """The section the tile links down to, caveats and all."""
    head = ('<h2 id="bandwidth">📡 What the videos cost the internet</h2>')
    if not pay.get("ok"):
        return (head + '<p class="notice">This build could not measure its own '
                f'published video files ({_e(pay.get("why", "reason not recorded"))}), '
                'so it prints no number. It will not print a zero it did not '
                'measure.</p>' + _bandwidth_caveat()
                + render_bandwidth_html(render_bandwidth()))
    per = pay["bytes"]
    watches = int((HOBBY_TRANSFER_GB * 1024 ** 3) // per) if per else 0
    return (
        head +
        '<p style="margin:.2rem 0 .6rem;color:var(--muted)">Every video this site '
        'publishes on its public pages, added up. One visitor who watched the '
        'whole show once — every episode and every animatic — would pull this '
        'much down.</p>'
        f'<div class="bw">'
        f'<div class="bwn">{_e(bytes_words(per))}</div>'
        f'<div class="bwu">across {pay["count"]} video files · '
        f'largest is {_e(pay["biggest"])} at {_e(bytes_words(pay["biggest_bytes"]))}'
        f'</div>'
        f'<p class="note">For scale: the free Hobby plan this site runs on includes '
        f'<a href="{HOBBY_TRANSFER_SRC}">{HOBBY_TRANSFER_GB} GB of transfer a month'
        f'</a>, so the whole video library fits down the pipe about '
        f'<b>{watches:,}</b> times before that allowance is gone.</p></div>'
        + _bandwidth_caveat()
        + render_bandwidth_html(render_bandwidth()))


def _bandwidth_caveat() -> str:
    """The paragraph that keeps the number above honest. Always printed."""
    return (
        '<p class="whyfoot"><b>This is an estimate, not a measurement.</b> It is '
        'the size of the files on disk, not the bytes anyone actually downloaded — '
        'real transfer is this figure multiplied by however many people watched, '
        'and browsers that stop a video early, re-watch it, or load it from cache '
        'all move the true number away from this one. The real figure lives in the '
        'Vercel dashboard under Usage. This page cannot read it: the account '
        'serving banyan.city is on the free Hobby plan, and Vercel\'s usage API '
        'answers <code>only available to Teams on the Pro or Enterprise plan</code>, '
        'so there is nothing to fetch. The site is also mirrored on GitHub Pages, '
        'which publishes no transfer figures through any API — traffic that lands '
        'on the mirror is counted by neither number.</p>'
        '<p class="whyfoot">What the figure covers: the episode and animatic files '
        'the public pages play. It leaves out the unlisted working-cut area and the '
        'trial clips, which are linked from nothing and are copied to the deploy '
        'after this page is built — counting them would make the number depend on '
        'which build command produced it. It also leaves out the repo\'s own video, '
        'which is far larger than the site\'s and never shipped to anyone: on '
        '2026-08-11 the working tree held 492 MB of takes and alternates that the '
        'deploy does not publish.</p>')


# ---- what the RENDER BOX costs the internet -----------------------------------
# Roman, 2026-08-11: "try to do some research on how much bandwidth the 5090
# takes making videos, i think it may be slowing down the whole internet."
#
# A DIFFERENT QUESTION FROM THE ONE ABOVE, and the page must not let the two
# blur. The figure above is what VISITORS pull down from the site. This one is
# what the render box in the house sends and receives. Roman asked the second;
# only the first existed; a reader who found the first and stopped would have
# come away with a confident answer to a question nobody asked.
#
# These are measurements, not estimates — which is the one respect in which this
# tile is better off than its neighbour, and the reason both wear their status
# on their face. They come from a file rather than a live read because the
# deploy server cannot reach the box (see the header of the yaml for why), so
# the page prints the date they were taken and lets them age in public.
RENDER_BW_FILE = "pipeline/measured/render-bandwidth.yaml"
_RBW_CACHE = {}


def render_bandwidth(path=None) -> dict:
    """The measured render-box network figures. Fails SOFT — never raises.

    Same contract as video_payload: a build that cannot read its own
    measurements prints "unavailable", never a zero and never a stale guess. A
    zero here would read as "the box uses no bandwidth", which is very nearly
    the conclusion the file exists to support — and would therefore be the most
    convincing possible way to publish a failure as a finding.
    """
    key = str(path or RENDER_BW_FILE)
    if key in _RBW_CACHE:
        return _RBW_CACHE[key]
    import yaml as _yaml
    out = None
    try:
        doc = _yaml.safe_load((REPO / key).read_text())
    except Exception as e:
        out = {"ok": False, "why": _reason(e)}
    if out is None:
        if not isinstance(doc, dict):
            out = {"ok": False, "why": f"{key} did not parse as a mapping"}
        else:
            need = ("while_rendering", "while_idle", "courier_push",
                    "model_downloads", "ssh_poll")
            missing = [k for k in need if not isinstance(doc.get(k), dict)]
            if missing:
                out = {"ok": False,
                       "why": f"{key} is missing {', '.join(missing)}"}
            else:
                out = dict(doc)
                out["ok"] = True
    _RBW_CACHE[key] = out
    return out


def rate_words(bps: float) -> str:
    """A speed a person can read. Built on bytes_words so one vocabulary."""
    return f"{bytes_words(int(round(bps)))}/s"


def _rbw_render_bps(rb: dict) -> int:
    r = rb["while_rendering"]
    return int(r.get("recv_bytes_per_sec", 0)) + int(r.get("sent_bytes_per_sec", 0))


def render_bandwidth_html(rb: dict) -> str:
    """The four measured numbers, the verdict, and what they were taken with.

    Kept to one verdict line and four rows on purpose. Roman has twice asked for
    this page to get simpler, so the finding leads and the workings follow.
    """
    head = '<h3 id="renderbw">🖥 And what the render box costs it</h3>'
    if not rb.get("ok"):
        return (head + '<p class="notice">The render-box measurements could not be '
                f'read ({_e(rb.get("why", "reason not recorded"))}), so this build '
                'prints no number for them rather than a stale or invented one.</p>')

    hd = float(rb.get("reference_hd_stream_bytes_per_sec") or 894785)
    ren = _rbw_render_bps(rb)
    idle = (int(rb["while_idle"].get("recv_bytes_per_sec", 0))
            + int(rb["while_idle"].get("sent_bytes_per_sec", 0)))
    cp = rb["courier_push"]
    cp_bytes = int(cp.get("bytes", 0))
    cp_hours = float(cp.get("window_hours") or 24) or 24
    cp_day = cp_bytes / cp_hours * 24
    md = rb["model_downloads"]
    peak = int(md.get("busiest_hour_bytes", 0)) / 3600.0
    sp = rb["ssh_poll"]
    sp_day = int(sp.get("bytes_per_tick", 0)) * int(sp.get("ticks_per_hour", 0)) * 24

    def row(what, num, like):
        return (f'<tr><td>{what}</td><td class="rbn">{_e(num)}</td>'
                f'<td class="rbl">{like}</td></tr>')

    rows = (
        row("Making a video, card at "
            f'{int(rb["while_rendering"].get("gpu_util_mean_pct", 0))}% busy',
            rate_words(ren),
            f'<b>{hd / ren:.0f}× less</b> than one HD video stream'
            if ren else "—")
        + row("The same box doing nothing", rate_words(idle),
              "almost the same — so the traffic above is not the render")
        + row("Sending finished stills home", bytes_words(int(cp_day)) + " a day",
              f'about {cp_day / 86400 / hd * 100:.0f}% of one HD stream, spread '
              'over the whole day')
        + row("Fetching a new model (busiest hour so far)",
              rate_words(peak),
              f'<b>{peak / hd:.0f} HD streams at once</b> — this is the one that '
              'can slow the house')
        + row("The status check every four minutes",
              bytes_words(int(sp_day)) + " a day",
              "one photo's worth, all day")
    )

    return (
        head +
        '<p class="verdict">Rendering is <b>not</b> what slows the internet. '
        'Making a video is arithmetic on a card that already holds the weights — '
        'measured mid-render the box moved less than a phone checking mail. The '
        'one thing here that can genuinely slow the house is <b>downloading a new '
        'model</b>, which happens once per model and then never again.</p>'
        f'<div class="scroll"><table class="rbw"><tbody>{rows}</tbody></table></div>'
        f'<p class="whyfoot">Measured on the render box on '
        f'{_e(str(rb.get("measured_on", "a date not recorded")))} — these are real '
        'samples, not an estimate like the figure above, which is why they carry a '
        'date and will visibly go stale. Nothing was downloaded at all in the 24 '
        'hours before the reading; the busiest hour shown was a one-off weight pull '
        f'at {_e(str(md.get("busiest_hour_when", "a time not recorded")))}. Method '
        f'and raw numbers: <a href="https://github.com/{GH}/blob/main/'
        f'{RENDER_BW_FILE}">{RENDER_BW_FILE}</a>.</p>')


# ---------------------------------------------------------------------------
# Roman, 2026-08-11, after finding the laptop at 9.6 GiB free while the render
# box sat on 217 GB: "fix the rendering storage issue in the background."
#
# The number itself was never the surprise — that it fell 19 -> 9.6 GiB in two
# hours with nobody watching was. A machine number that lives only in `df` is a
# number nobody looks at until it is an emergency, so it goes on the page — in
# its own section, NOT in the summary strip, where its tile read as clutter to
# anyone who is not the person who owns the laptop (Roman, 2026-08-11) — and it
# gets the same honesty contract its neighbours have: a file, a date, and
# "unavailable" instead of a zero.
#
# Same reason as its neighbour for being a file rather than a live read, with
# one extra: the deploy server HAS a disk, so a build-time reading would return
# a confident, real, completely meaningless figure about a machine nobody cares
# about. Written by `python3 pipeline/box_cache.py disk` on the laptop it
# describes.
LOCAL_DISK_FILE = "pipeline/measured/local-disk.yaml"
_DISK_CACHE = {}


def local_disk(path=None) -> dict:
    """The laptop's free-space reading. Fails SOFT — never raises."""
    key = str(path or LOCAL_DISK_FILE)
    if key in _DISK_CACHE:
        return _DISK_CACHE[key]
    import yaml as _yaml
    out = None
    try:
        doc = _yaml.safe_load((REPO / key).read_text())
    except Exception as e:
        out = {"ok": False, "why": _reason(e)}
    if out is None:
        if not isinstance(doc, dict):
            out = {"ok": False, "why": f"{key} did not parse as a mapping"}
        else:
            need = ("free_bytes", "total_bytes", "measured_on")
            missing = [k for k in need if doc.get(k) in (None, "")]
            if missing:
                out = {"ok": False,
                       "why": f"{key} is missing {', '.join(missing)}"}
            else:
                out = dict(doc)
                out["ok"] = True
    _DISK_CACHE[key] = out
    return out


STRIP_CSS = """
/* ---- the summary strip -------------------------------------------------
   Roman, 2026-08-10: "the dashboard is a bit too long and complex ... can you
   atleast have at the top of the page the simple view that lets you see the
   most important stuff like queue and whatnot". Nothing below was removed —
   he said he does not mind the detail existing — so this is a lead, not a
   replacement, and every tile is an anchor down to the full account of
   itself. No new markup vocabulary and no JavaScript: the strip is built from
   the same numbers the sections below print, by the same functions, so the
   two cannot disagree. */
.strip { border: 1px solid var(--line); border-radius: 14px; padding: .85rem .95rem;
  margin: 0 0 1.4rem; background: var(--code-bg); }
.strip .sh { font: 700 .62rem/1 var(--mono); letter-spacing: .09em;
  text-transform: uppercase; color: var(--faint); margin: 0 0 .7rem; }
.strip .sgrid { display: grid; gap: .55rem;
  grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr)); }
.strip .sx { display: block; text-decoration: none; color: inherit;
  border: 1px solid var(--line); border-radius: 10px; padding: .5rem .6rem;
  background: var(--bg); }
.strip .sx:hover { border-color: var(--sap-deep); }
.strip .sn { display: block; font: 700 1.35rem/1.15 var(--mono); color: var(--sap); }
.strip .sn.none { font-size: .8rem; font-weight: 600; color: var(--faint);
  line-height: 1.7; }
.strip .sn.zero { color: var(--faint); }
.strip .sn.ok { color: var(--leaf); }
.strip .sn.bad { color: var(--alarm, #e2564d); }
.strip .sl { display: block; font: 500 .68rem/1.45 var(--mono); color: var(--muted);
  margin-top: .15rem; }
.strip .sline { margin: .7rem 0 0; font: 500 .78rem/1.6 var(--mono);
  color: var(--muted); }
.strip .sline b { color: var(--ink); font-weight: 700; }
.strip .sline + .sline { margin-top: .3rem; }
.strip .sfoot { margin: .75rem 0 0; font: 400 .7rem/1.6 var(--sans, inherit);
  color: var(--faint); }
/* ---- the episode ETA cards ---------------------------------------------
   Roman, 2026-08-13, on the prose version: "im not seeing any eta ... except
   this which isn't the best". Same numbers, same refusals, read in a second
   instead of a paragraph. It borrows the strip's vocabulary on purpose — this
   sits directly under the glance and should read as its sibling, not as a new
   kind of thing.

   THE COLOUR CARRIES THE ARGUMENT, so it is not decoration and must not be
   restyled casually: GREEN is the machine's business (passed, still to render),
   AMBER is the author's (a take waiting on his eye, a call waiting on his word).
   The feature exists to keep those two clocks apart, and the bar is where that
   separation becomes visible without reading anything. */
.eta { border: 1px solid var(--line); border-radius: 14px; padding: .85rem .95rem;
  margin: 0 0 1.4rem; background: var(--code-bg); }
.eta .sh { font: 700 .62rem/1 var(--mono); letter-spacing: .09em;
  text-transform: uppercase; color: var(--faint); margin: 0 0 .7rem; }
.epcard { border: 1px solid var(--line); border-radius: 10px; background: var(--bg);
  padding: .7rem .8rem; margin: 0 0 .55rem; }
.epcard:last-of-type { margin-bottom: 0; }
.ephead { display: flex; flex-wrap: wrap; align-items: baseline; gap: .45rem;
  margin: 0 0 .5rem; }
.ephead b { font: 700 1rem/1.2 var(--sans, inherit); color: var(--ink); }
.ephead .ept { font: 400 .8rem/1.3 var(--sans, inherit); color: var(--muted); }
.ephead .epp { margin-left: auto; font: 700 .8rem/1.2 var(--mono);
  color: var(--leaf); font-variant-numeric: tabular-nums; }
.epbar { display: flex; height: 10px; border-radius: 999px; overflow: hidden;
  border: 1px solid var(--line); background: var(--code-bg); }
/* A 2px gap in the page's own surface colour between neighbouring segments —
   not a border around each one. Two fills that touch read as one fill with a
   colour change in the middle; two fills with the background showing between
   them read as two counts, which is what they are. */
.epbar i { display: block; height: 100%;
  box-shadow: 2px 0 0 0 var(--code-bg); }
.epbar i:last-child { box-shadow: none; }
.epbar .b-done { background: var(--leaf); }
.epbar .b-look { background: var(--sap); }
.epbar .b-mach { background: var(--leaf-deep); }
.epbar .b-gate { background: var(--sap-deep); }
.epbar .b-unk  { background: var(--line); }
.epkey { display: flex; flex-wrap: wrap; gap: .1rem .75rem; margin: .4rem 0 .6rem;
  font: 400 .68rem/1.7 var(--sans, inherit); color: var(--muted); }
.epkey span { display: inline-flex; align-items: center; gap: .32rem; }
.epkey span::before { content: ""; width: .5rem; height: .5rem; border-radius: 2px;
  background: var(--line); flex: none; }
.epkey .k-done::before { background: var(--leaf); }
.epkey .k-look::before { background: var(--sap); }
.epkey .k-mach::before { background: var(--leaf-deep); }
.epkey .k-gate::before { background: var(--sap-deep); }
.epstats { display: grid; gap: .45rem;
  grid-template-columns: repeat(auto-fit, minmax(9.5rem, 1fr)); }
.epstats .sx { display: block; text-decoration: none; color: inherit;
  border: 1px solid var(--line); border-radius: 9px; padding: .45rem .55rem;
  background: var(--panel); }
.epstats a.sx:hover { border-color: var(--sap-deep); }
.epstats .sn { display: block; font: 700 1.25rem/1.15 var(--mono);
  font-variant-numeric: tabular-nums; color: var(--sap); }
.epstats .n-you { color: var(--sap); }
.epstats .n-mach { color: var(--leaf); }
.epstats .n-none { font-size: .74rem; font-weight: 600; line-height: 1.6;
  color: var(--faint); }
.epstats .sl { display: block; font: 400 .68rem/1.45 var(--sans, inherit);
  color: var(--muted); margin-top: .12rem; }
/* The render-time-is-not-finish-time sentence. Deliberately louder than
   .epnote: it is the correction to an actual misreading, not a caveat. */
.epwarn { margin: .55rem 0 0; padding: .45rem .6rem; border-radius: 8px;
  border: 1px solid var(--line); background: var(--code-bg);
  font: 400 .74rem/1.6 var(--sans, inherit); color: var(--muted); }
.epwarn b { color: var(--ink); }
.epnote { margin: .5rem 0 0; font: 400 .72rem/1.65 var(--sans, inherit);
  color: var(--faint); }
.epnote b { color: var(--muted); font-weight: 700; }
.epcalls { margin: .45rem 0 0; font: 400 .74rem/1.7 var(--sans, inherit);
  color: var(--muted); }
.epcalls a { color: var(--ink); }
.eta > details { margin: .6rem 0 0; }
.eta > details > summary { cursor: pointer; color: var(--faint);
  font: 500 .72rem/1.7 var(--sans, inherit); }
/* ---- EPISODE 2, RIGHT NOW ---------------------------------------------------
   One line per fact, each with a state dot on its left, and the dot colours are
   charts.STATE_STYLE's own tokens — the same four the tree above it and the bar
   below it use. THE COLOUR LAW HOLDS HERE TOO (SITE.md): green is the machine's
   clock, amber is the author's, and every value is a var() so both survive a
   reader's light/dark setting. A hex literal in this block would be a colour
   that does not know which theme it is in.
   The rule on the left edge is the amber of his own clock on purpose: the strip
   exists because he asked what state the episode is in, and it is his panel. */
.ep2now { border: 1px solid var(--line); border-left: 3px solid var(--sap);
  border-radius: 12px; padding: .7rem .85rem; margin: .8rem 0 .2rem;
  background: var(--panel); text-align: left; }
.ep2now .e2h { font: 600 .74rem/1.5 var(--mono); letter-spacing: .04em;
  text-transform: uppercase; color: var(--muted); margin: 0 0 .5rem; }
.ep2now .e2l { list-style: none; margin: 0; padding: 0;
  font: 400 .82rem/1.6 var(--sans, inherit); color: var(--muted); }
.ep2now .e2l li { position: relative; padding: 0 0 0 1.1rem;
  margin: 0 0 .42rem; }
.ep2now .e2l li:last-child { margin-bottom: 0; }
.ep2now .e2l li::before { content: ""; position: absolute; left: 0; top: .48rem;
  width: .55rem; height: .55rem; border-radius: 2px; background: var(--line); }
.ep2now .e2l b { color: var(--ink); font-weight: 700; }
.ep2now .e2l a { color: var(--ink); }
.ep2now .e2l .f-done::before { background: var(--leaf); }
.ep2now .e2l .f-mach::before { background: var(--leaf-deep); }
.ep2now .e2l .f-look::before { background: var(--sap); }
.ep2now .e2l .f-gate::before { background: var(--sap-deep); }
/* The join's own finding gets the hollow mark, because it is the one line that
   is about a MISMATCH between two files rather than about either file's state. */
.ep2now .e2l .f-swap::before { background: transparent;
  box-shadow: inset 0 0 0 1px var(--sap); }
.ep2now .cnote { text-align: left; }
/* ---- THE RECEIPTS: one fold per beat, inside the drawer that already held the
   table. Mobile-first, on the review pages' widths — he reads this on a phone,
   so the summary row is a 54px frame plus two short strings plus two chips, and
   it wraps rather than scrolls. AMBER IS THE ALARM HERE and that is the colour
   law rather than an exception to it: a sha that does not match, a file that is
   missing, a beat nobody has judged are all things needing a person, and this
   page's amber has meant "the author's clock" since the day it was drawn. There
   is no red token in site_theme.py and inventing one as a hex literal in this
   block would be a colour that does not know which theme it is in. */
.rcpts { margin: .2rem 0 .8rem; }
.rcpt { border-top: 1px solid var(--line-soft); }
.rcpt:first-child { border-top: 0; }
.rcpt > summary { cursor: pointer; list-style: none; display: flex;
  align-items: center; flex-wrap: wrap; gap: .45rem; padding: .4rem 0; }
.rcpt > summary::-webkit-details-marker { display: none; }
.rcpt > summary::after { content: "▸"; margin-left: auto; color: var(--faint);
  font-size: .7rem; }
.rcpt[open] > summary::after { content: "▾"; }
.rcpt > summary:hover .rs { color: var(--ink); }
.rcpt .rth { width: 54px; height: auto; flex: none; border-radius: 4px;
  background: var(--code-bg); display: block; }
.rcpt .rth.none { width: 54px; height: 30px; display: inline-flex;
  align-items: center; justify-content: center; border-radius: 4px;
  border: 1px dashed var(--line); color: var(--faint);
  font: 500 .62rem/1 var(--mono); }
.rcpt .rn { font: 700 .74rem/1 var(--mono); color: var(--faint); }
.rcpt .rs { font: 600 .8rem/1.3 var(--sans, inherit); color: var(--muted); }
.rcpt .fk { font: 500 .68rem/1.4 var(--mono); color: var(--faint); }
.rcall { font: 700 .64rem/1 var(--mono); letter-spacing: .05em;
  padding: .2rem .34rem; border-radius: 3px; border: 1px solid var(--line); }
.rcall.ok { color: var(--leaf); border-color: var(--leaf); }
.rcall.bad { color: var(--sap); border-color: var(--sap); }
.rcall.none { color: var(--faint); }
.rcpt .rb { padding: .1rem 0 .7rem; }
.rcpt dl { margin: 0; }
.rcpt dt { font: 600 .66rem/1.5 var(--mono); letter-spacing: .04em;
  text-transform: uppercase; color: var(--faint); margin: .5rem 0 .15rem; }
.rcpt dd { margin: 0; font: 400 .78rem/1.65 var(--sans, inherit);
  color: var(--muted); overflow-wrap: anywhere; }
.rcpt dd a { color: var(--ink); }
.rcpt dd code { font: 400 .72rem/1.5 var(--mono); background: var(--code-bg);
  padding: .05rem .22rem; border-radius: 3px; }
.rcpt dd b.bad { color: var(--sap); }
.rcpt .rq { margin: .25rem 0; padding-left: .6rem;
  border-left: 2px solid var(--line); }
.rcpt .rq.more { border-left-color: transparent; color: var(--faint); }
.rcpt .rk { font: 600 .68rem/1.5 var(--mono); color: var(--faint); }
.rcpt .rsrc { margin: .3rem 0 0; font-size: .72rem; color: var(--faint); }
/* The fortnight's deltas, sitting between the legend and the footer and reading
   as part of the footer rather than as a section — which is the whole point of
   it being one line. */
.pledger { margin: 2.6rem 0 0; text-align: left;
  font: 400 .74rem/1.7 var(--sans, inherit); color: var(--faint); }
.pledger b { color: var(--muted); }
.pledger a { color: var(--leaf); }
.pledger code { font: 400 .7rem/1.5 var(--mono); background: var(--code-bg);
  padding: .05rem .22rem; border-radius: 3px; }
/* The same four dots inside the table view, so a reader who opened the fold to
   avoid the colours still gets the words and a reader who wants the colours
   still has them. */
.fk { display: inline-flex; align-items: center; gap: .34rem; }
.fk::before { content: ""; width: .5rem; height: .5rem; flex: none;
  border-radius: 2px; background: var(--line); }
.fk.f-done::before { background: var(--leaf); }
.fk.f-mach::before { background: var(--leaf-deep); }
.fk.f-look::before { background: var(--sap); }
.fk.f-gate::before { background: var(--sap-deep); }
.fk.f-unk::before { background: transparent;
  box-shadow: inset 0 0 0 1px var(--line); }
.bw { border: 1px solid var(--line); border-radius: 14px; padding: .9rem 1rem;
  margin: .6rem 0 .5rem; text-align: center; }
.bw .bwn { font: 700 1.7rem/1.2 var(--mono); color: var(--sap); }
.bw .bwu { font: 500 .76rem/1.6 var(--mono); color: var(--muted); }
.bw .note { font: 400 .76rem/1.7 var(--sans, inherit); color: var(--faint);
  margin: .5rem 0 0; }
/* ---- the render-box figures. A table, not more tiles: five rows that are only
   meaningful against each other ("the same box doing nothing" is the control for
   the row above it), and a tile row would scatter them. The verdict sits above
   it in plain words, because the finding is the point and the arithmetic is the
   evidence for it. ---- */
.verdict { font: 500 .92rem/1.7 var(--sans, inherit); color: var(--ink);
  border-left: 3px solid var(--sap); padding: .1rem 0 .1rem .8rem;
  margin: .6rem 0 .8rem; }
table.rbw { border-collapse: collapse; width: 100%; font-size: .82rem; }
table.rbw td { padding: .5rem .6rem; border-bottom: 1px solid var(--line-soft);
  vertical-align: baseline; }
table.rbw tr:last-child td { border-bottom: 0; }
table.rbw .rbn { font: 700 .9rem/1.4 var(--mono); color: var(--sap);
  font-variant-numeric: tabular-nums; white-space: nowrap; text-align: right; }
table.rbw .rbl { color: var(--muted); }
"""


def strip_counts(queue: list, backlog: list, records: list) -> dict:
    """The strip's numbers, from the SAME function the record below prints.

    queue_entry_state is the page's one answer to "what state is this entry in",
    so calling it here rather than re-deriving anything is what stops the glance
    at the top from contradicting the record at the bottom. A summary that can
    disagree with its own detail is worse than no summary.
    """
    claims, done_ids = claim_lines(records), task_ids_done(records)
    counts = {k: 0 for k in QSTATES}
    for e in queue:
        counts[queue_entry_state(e, "tasks", claims, done_ids)] += 1
    for e in backlog:
        counts[queue_entry_state(e, "backlog", claims, done_ids)] += 1
    return counts


def summary_strip(view: dict, now) -> str:
    """The three questions a visitor actually brings, answered in one row.

    REBUILT 2026-08-11. The old strip led with seven tiles whose two loudest
    numbers were wrong the night the founder looked ("rendering now: 0" over a
    box that finished ten jobs; "runnable: 4" over jobs done the day before) —
    both counted off the dead task list instead of the machines' own logs. The
    strip now answers, in order: is production alive, what got made in the
    last day, and where the show is. Bandwidth and disk trivia came off it —
    the founder's own ruling on the disk tile, extended by both audits.

    GAINED A CELL AT THE FRONT 2026-08-12: what is waiting on the author, and
    the link to the inbox holding it. Every other cell is written for a
    stranger; that one is written for the only reader who arrives with work to
    do, which is why it goes first rather than last.

    Honesty rule unchanged: this is a snapshot with its instant printed on it,
    never a claim of "live". `view` carries only log-derived facts:
      last_activity  newest dated line across every machine and ledger log
      fin            finished_recent() — DONE lines from the last 24 h
      live           live_now() — fresh STARTED lines with no end mark
      unread         logs_unread() — branches whose logs this build could not read
      by_id          queue entries by id, for done_story()
      hero/tot       the episode player facts (build_status)
      ep2            the next episode's counts, or None
      inbox          the author's decision queue
      boxq           box_queue_eta() — the render box's queue depth in jobs and
                     in time, or None when its snapshot could not be read
    """
    fin, live, unread = view["fin"], view["live"], view["unread"]
    last, inbox = view["last_activity"], view["inbox"]
    hero, tot, ep2 = view["hero"], view["tot"], view.get("ep2")

    # --- cell 0: what is waiting on the author, and WHERE HE CLICKS TO SEE IT.
    # Added 2026-08-12 on his "i cannot find things to review on
    # banyan.city/status". It leads the row rather than joining the end of it
    # because he is the one reader who arrives with a job to do, and the four
    # cells after it answer a visitor's questions, not his. The count comes
    # from review_inbox_open() — the yaml SITE.md makes canonical — so it can
    # never drift from the page it links to.
    nrev = view.get("review_open")
    if nrev:
        review_cell = (f'<a class="sx" href="review"><span class="sn">{nrev}'
                       f'</span><span class="sl">thing{"s" if nrev != 1 else ""} '
                       'waiting on the author · the review inbox — every open '
                       'call in one list, with what answering it would '
                       'unblock</span></a>')
    elif nrev == 0:
        review_cell = ('<a class="sx" href="review"><span class="sn zero">0'
                       '</span><span class="sl">waiting on the author — the review '
                       'inbox is empty, so nothing published is held up by a call '
                       'only he can make</span></a>')
    else:
        review_cell = ('<a class="sx" href="review"><span class="sn none">not '
                       'read</span><span class="sl">the review inbox’s list '
                       'could not be read this build, so no count is claimed — the '
                       'inbox itself is still there</span></a>')

    # --- cell 1: is production alive? Keyed to LAST ACTIVITY, not to
    # this-second job state — "nothing this minute" over a working night is the
    # exact misread the founder screenshotted.
    if unread and last is None:
        word, cls = "unknown", "none"
        sub = ("the machines\u2019 check-in logs could not be read this build, "
               "so nothing is claimed either way")
    elif last is None:
        word, cls = "quiet", "zero"
        sub = "no machine has ever checked in"
    elif (now - last).total_seconds() < 6 * 3600:
        word, cls = "active", "ok"
        sub = f"last activity {age_words(last, now)}"
    else:
        word, cls = "quiet", "zero"
        sub = f"nothing heard from the studio since {age_words(last, now)}"
    if live:
        sub += " \u00b7 a job was mid-flight at the last check-in"
    alive_cell = (f'<a class="sx" href="#worklist"><span class="sn {cls}">'
                  f'\u25cf {word}</span>'
                  f'<span class="sl">the studio \u00b7 {_e(sub)}</span></a>')

    # --- cell 2: what got made in the last 24 hours, newest first.
    if fin:
        when, who, tid, _note = fin[0]
        newest = (f'newest: {_e(done_story(view["by_id"].get(tid), tid))} \u00b7 '
                  f'{age_words(when, now)}')
        made_cell = (f'<a class="sx" href="#worklist"><span class="sn">{len(fin)}'
                     f'</span><span class="sl">finished in the last 24 h \u00b7 '
                     f'{newest}</span></a>')
    elif unread:
        made_cell = ('<a class="sx" href="#worklist"><span class="sn none">not '
                     'read</span><span class="sl">finished in the last 24 h — a '
                     'check-in log could not be read, and a zero nobody measured '
                     'is not a number</span></a>')
    else:
        made_cell = ('<a class="sx" href="#worklist"><span class="sn zero">0'
                     '</span><span class="sl">renders finished in the last 24 h '
                     '— writing and code work does not check in here</span></a>')

    # --- cell 3: the show itself — the thing a visitor actually came for.
    ep_bits = f'episode {hero["number"]} is live \u00b7 {tot["final"]} of {tot["total"]} scene frames approved'
    if ep2:
        ep_bits += (f' \u00b7 episode {ep2["number"]}: takes in for '
                    f'{ep2["started"]} of {ep2["total"]} scenes')
    if inbox:
        ep_bits += (f' \u00b7 {len(inbox)} call{"s" if len(inbox) != 1 else ""} '
                    'waiting on the author')
    show_cell = (f'<a class="sx" href="{_e(hero["watch"])}">'
                 f'<span class="sn ok">\u25b6 watch</span>'
                 f'<span class="sl">{ep_bits}</span></a>')

    # --- cell 4: how long the queue is IN TIME, which is what the founder
    # asked the strip for (2026-08-12) and what a count alone cannot answer \u2014
    # "2 queued" is a minute or an hour depending on what the two are. The
    # count keeps top billing because it is measured; the time is derived from
    # it and says so. No snapshot, or no median to multiply it by, and the cell
    # states which of the two is missing rather than printing a plausible
    # number.
    #
    # The ids are load-bearing: LIVE_JS.readBoxQueue() overwrites this cell from
    # the box's own five-minute publish, so what is baked here is the no-JS
    # floor, not the number most readers see.
    # --- and NO queue cell. It said "~42 min of work queued" a few hundred
    # pixels under a section that now says the same thing in blocks, at the top
    # of the page where the founder asked for it (2026-08-14). One fact printed
    # twice is his standing complaint; the cell's number and label moved whole
    # into queue_head_html() and kept their ids.
    return (
        '<div class="strip rise">'
        '<p class="sh">At a glance</p>'
        f'<div class="sgrid">{review_cell}{eta_cell(view.get("eta_rows"))}'
        f'{alive_cell}{made_cell}{show_cell}</div>'
        f'<p class="sfoot">A snapshot as of <b>{now.strftime("%H:%M")} UTC, '
        f'{now.strftime("%d %b")}</b> — the moment this page was built and the '
        'machines\u2019 own logs were last read. Nothing here claims to be '
        'live: ages keep counting in your browser, and the detail below says '
        'where every number comes from.</p>'
        '</div>')

# only build once per output directory: build_site.py calls build_status.build()
# (which delegates here) and then build_sim.build(), and each pass would hit the
# GitHub API again for the same snapshot.
_BUILT = set()


def build(out_dir: Path):
    import build_status as data
    out_dir = Path(out_dir)
    if str(out_dir.resolve()) in _BUILT:
        return
    rows = data.scenes()
    tot = data.summary(rows)
    hero = data.hero()
    spend, inbox = data.spend(), data.inbox()
    grow = data.growth(rows)

    # --- the infra meter (D18): rendered EMPTY and filled in by the reader's
    # browser. The server-side copy states no number at all — not zero, not the
    # last one we saw. A page that shipped a stale count would read as "the
    # meter is fine" on exactly the failure it exists to catch, and a build-time
    # read is the wrong instrument anyway: the thing being watched for is a
    # flood of deploys, so a counter that only advances when one happens cannot
    # see it. Same contract as the machines' logs and the render box's vitals.
    meter = data.infra_meter()
    infra_html = (
        f'<div class="infra rise" id="infra">'
        f'<div class="n none" id="infra-n">{_e(meter["counting"])}</div>'
        f'<div class="u" id="infra-u">{_e(meter["title"].lower())}</div>'
        f'<p class="note">{_e(meter["note"])}</p>'
        f'</div>')

    # --- ONE READ OF THE FARM, used by every section below. branch_log() reads
    # each machine's WHOLE check-in file and dates it off one anchor commit, so
    # the counters here see everything the runners ever wrote — the 30-commit
    # window that hid a night of finished work is gone with the window.
    now = utcnow()
    qdoc = queue_doc()
    queue, backlog = qdoc["tasks"], qdoc["backlog"]
    machines = read_machines(queue, backlog, now)
    # The machine list is the MACHINES; the work-list counters are the machines
    # AND the hand ledger. That split is the whole of NOT_A_MACHINE: no tile for
    # a thing that is not a box, no blindness about work it finished.
    records = machines + read_ledgers(now)
    by_id = {str(t.get("id")): t for t in list(queue) + list(backlog)}
    done_ids = task_ids_done(records)
    live = live_now(records, now)
    fin = finished_recent(records, now)
    depth = box_queue_depth(records)
    # ONE read of the box snapshot, shared by the glance at the top and the
    # work list below it — the strip's standing rule is that it cannot
    # contradict the section it links to, and two reads of one file eventually
    # do.
    boxq = box_queue_eta(read_box_queue())
    # ONE read for the glance at the top and the pointer beside the waiting
    # list, for the same reason as the box snapshot above it.
    review_open = review_inbox_open()
    # Likewise ONE read of the episode states, shared by the glance cell and the
    # cards below it — must be read before the strip, which now quotes it.
    eta_rows = episode_eta_rows()
    last_activity = max((m["history"][0][0] for m in records if m["history"]),
                        default=None)

    # --- the simple view: alive? → made? → the show. Above everything else.
    strip = summary_strip({
        "fin": fin, "live": live, "unread": logs_unread(),
        "last_activity": last_activity, "by_id": by_id, "hero": hero,
        "tot": tot, "ep2": data.next_episode(), "inbox": inbox,
        "boxq": boxq, "review_open": review_open, "eta_rows": eta_rows}, now)

    # --- when each episode is finished, machine half and human half kept
    # apart. High on the page because it is the question the founder asked of
    # this page (2026-08-13) and the one a reader arrives holding; empty string
    # when its states file cannot be read, so a build that lost the file drops
    # the section rather than publishing an ETA it cannot support.
    eta_section = episode_eta_html(eta_rows)

    # --- THE SAPLING. The show is called Sapling and the page that shows it
    # being made used to draw it as fifteen emoji in a five-wide grid — one
    # episode's stills, one glyph each, and nothing about the series. The tree
    # in charts.py is the same idea done as a chart: one leaf per beat of every
    # episode, coloured by that beat's measured state, linked to that beat's
    # place on its shot board, with the reason on file in its tooltip. Same
    # file as the ETA cards below, so the picture and the hours cannot disagree.
    #
    # The emoji grove said "frame approved / animated", which is a DIFFERENT
    # fact and not one the tree carries — that is why the growth meter and the
    # per-scene drawer below both stay exactly as they were.
    ep_boards = {int(hero["number"]): hero["board"]}
    nxt = data.next_episode()
    if nxt and nxt.get("board"):
        ep_boards[int(nxt["number"])] = nxt["board"]
    # ONE read of the per-beat states, shared by the tree and the "right now"
    # strip under it — same rule as the box snapshot and the inbox above: the
    # strip's standing promise is that it cannot contradict the picture it sits
    # beneath, and two reads of one file eventually do.
    # The cut manifest is read here and nowhere else, and the strip is "" when
    # either half is missing rather than half-drawn off one of them.
    # ONE read of the cut manifest and ONE read of the receipts, shared by the
    # strip and by the tree's leaf links above it — same rule as the box snapshot
    # and the inbox: two reads of one file eventually disagree, and a leaf
    # pointing at a take the strip below it does not list would be exactly that.
    cut = read_latest_cut()
    try:
        cut_recs = proof_receipts.receipts(cut) if cut else []
    except Exception:
        cut_recs = []
    try:
        import episode_eta as _eta
        progress = _eta.read_progress()
        sapling = charts.sapling_html(progress, ep_boards,
                                      leaf_links(cut_recs, CUT_EPISODE))
    except Exception:
        # Fails to nothing, like the ETA section it reads with. A tree drawn
        # from a read that failed would be a picture of our own bug.
        progress, sapling = [], ""
    ep2_now = ep2_now_html(cut, progress, recs=cut_recs)
    # The fortnight's deltas, one line, above the footer.
    pledger = proof_ledger_line()
    done = tot["final"] == tot["total"]
    pct = round(100 * grow["done"] / grow["total"]) if grow["total"] else 0
    grove_caption = (f'Episode {hero["number"]} — '
                     + (f'all {tot["total"]} scene frames approved. '
                        if done else f'{tot["final"]} of {tot["total"]} scene frames approved. ')
                     + f'<a href="{_e(hero["page"])}">Watch it &rarr;</a>')
    # role="img" + aria-label: the bar itself is decoration, the numbers are the fact
    growbar = (f'<div class="growbar" role="img" aria-label="{grow["done"]} of '
               f'{grow["total"]} growth steps done"><i style="width:{pct}%"></i></div>'
               f'<div class="label"><b>{pct}% grown</b> — {grow["done"]} of {grow["total"]} '
               'growth steps. A scene grows twice: its frame is approved, then it is animated.</div>')

    # --- milestones, in one line. The six-badge strip said the same facts in
    # thirty; every clause below is still a checkable repo fact.
    vo = data.vo_scenes()
    passed = data.cut_passed()
    moving = sum(1 for r in rows if r["animations"])
    mile_bits = [
        f'{tot["total"]} scenes scripted',
        ("every frame approved" if done
         else f'{tot["final"]} of {tot["total"]} frames approved'),
        (f'{vo} scenes voiced' if vo else "no voice lines yet"),
        ("every scene moves" if moving == tot["total"]
         else f'{moving} of {tot["total"]} scenes move'),
        ("a full cut is playing above" if hero["video"] else "no full cut yet"),
        ("the author passed the cut" if passed
         else "awaiting the author's pass — the last gate"),
    ]
    milestones_line = ('<p class="summary" style="text-align:center">'
                       + _e(" · ".join(mile_bits)) + '</p>')

    # --- the machines, one line each. The animated lot died in the 2026-08-11
    # revamp: three of four buildings rendered permanently faded, and the sky
    # was decoration a visitor had to read past to find the one fact.
    machlist = ""
    for m in machines:
        st = m["state"]
        # Every claim on this line carries the age of the thing it describes,
        # and the ages tick in the reader's own browser (see LIVE_JS).
        # NOT .age when there is no age: this branch is the fallback SENTENCE
        # for a machine whose date could not be read, and nowrap made that
        # sentence a 747px line at phone width (measured, 2026-08-10).
        bits = [f'last check-in {age_el(m["last_seen"], now)}'] if m["last_seen"] else \
            [f'<span class="noage">{_e(st["seen"])}</span>']
        if m["telemetry"]:
            bits.append('vitals published <span data-role="vitals">'
                        f'{age_el(m["telemetry"]["at"], now)}</span>')
        machlist += (
            f'<li data-mach="{_e(m["key"])}" data-branch="{_e(m["branch"])}" '
            f'data-telbranch="{_e(telemetry_branch(m["branch"]))}" '
            f'data-tail="{_e(st["raw"])}" data-built="{int(now.timestamp())}" '
            f'data-tel="{"1" if m["telemetry"] else ""}">'
            f'<span class="mico">{m["emoji"]}</span> <b>{_e(m["name"])}</b> '
            f'<span class="chip{" hot" if st["css"] == "working" else ""}" '
            f'data-role="chip">{_e(st["chip"])}</span>'
            f'<div class="mstate" data-role="head">{_e(st["head"])}</div>'
            + (f'<div class="why">{_e(st["why"])}</div>' if st["why"] else "")
            + f'<div class="mono" data-role="seen">{" · ".join(bits)}</div></li>')

    # --- the work list: in flight, finished, queued, planned — off the logs.
    live_ids = {t for _w, _who, t in live}
    hand_q, machine_q = [], []
    for t in queue:
        tid = str(t.get("id"))
        if tid in done_ids or tid in live_ids:
            continue
        # A `runner: manual` entry is a job for a PERSON. Publishing one as
        # "queued and runnable" is how four dead hand jobs from 2026-08-09 sat
        # on the page narrating taste-ledger clauses at strangers. They stay in
        # the file for the person they are addressed to; the page counts them
        # in one line and prints none of them.
        if str(t.get("runner") or "") == "manual" or str(t.get("worker") or "") in LEDGERS:
            hand_q.append(t)
        else:
            machine_q.append(t)

    if live:
        live_rows = "".join(
            f'<div class="prod-row"><b>{_e(done_story(by_id.get(t), t))}</b> · '
            f'{_e(who)} · started {age_el(when, now)}</div>'
            for when, who, t in live)
        onmach = ('<h3>⚙️ On the machines — as of the last check-in</h3>'
                  + live_rows)
    else:
        seen_note = (f' The newest check-in this build could read is '
                     f'{age_words(last_activity, now)}.' if last_activity else "")
        onmach = ('<h3>⚙️ On the machines — as of the last check-in</h3>'
                  '<p class="notice">No job was mid-flight at the last check-in '
                  'this build could read.' + _e(seen_note) + ' Short jobs start '
                  'and finish between check-ins, so what actually shipped is the '
                  'list below.</p>')
    if depth:
        dwhen, dready, dfailed, dwho = depth
        onmach += (f'<p class="mono">{_e(dwho)} reported its own on-disk queue at '
                   f'its last idle check-in: <b>{dready}</b> '
                   f'job{"s" if dready != 1 else ""} ready'
                   # Same rule as the chip above, on the no-JS floor: a pile that
                   # is entirely written up is a fact, not an alarm, and saying
                   # so costs four words.
                   + (f', {dfailed} failed'
                      + (" (all triaged)" if 0 < dfailed <= acknowledged_failures()
                         else "") if dfailed else "")
                   + f' · {age_el(dwhen, now)}</p>')

    if fin:
        def _fin_row(when, who, tid):
            return (f'<div class="prod-row"><b>{_e(done_story(by_id.get(tid), tid))}'
                    f'</b> · {_e(who)} · finished {age_el(when, now)}</div>')
        # Ten rows at the surface, the rest one click down: on a heavy night the
        # farm finishes seventy jobs, and seventy rows is a wall where the
        # founder asked for a glance. Nothing is dropped — the drawer holds the
        # whole day, newest first, same one-line shape.
        fin_rows = "".join(_fin_row(w, who, t) for w, who, t, _n in fin[:10])
        if len(fin) > 10:
            rest = "".join(_fin_row(w, who, t) for w, who, t, _n in fin[10:])
            fin_rows += (f'<details class="drawer"><summary>and {len(fin) - 10} '
                         'more from the same 24 hours</summary>'
                         f'<div class="drawer-body">{rest}</div></details>')
        done_html = (f'<h3>✅ Finished in the last 24 hours '
                     f'<span class="count">{len(fin)}</span></h3>' + fin_rows)
    elif logs_unread():
        # NO NUMBER AT ALL — the infra meter's contract, for the same reason. A
        # zero printed off a read that failed is this page inventing the most
        # reassuring answer on exactly the failure it exists to catch.
        unread = logs_unread()
        named = (_and_list(unread) if len(unread) <= 3
                 else f"{len(unread)} of the check-in logs")
        done_html = ('<h3>✅ Finished in the last 24 hours '
                     '<span class="count">—</span></h3>'
                     f'<p class="notice">This build could not read {_e(named)}, so '
                     'it does not know what finished and will not print a zero '
                     'it did not measure.</p>')
    else:
        # WHAT THE ZERO ACTUALLY MEANS, in the words it can defend. The check-in
        # log only ever records what a RENDER runner ran; a code or writing task
        # finishes by having its queue entry retired and never writes a line.
        done_html = ('<h3>✅ Finished in the last 24 hours '
                     '<span class="count">0</span></h3>'
                     '<p class="notice">No render job has finished in the last '
                     '24 hours. This counts work a render machine ran and '
                     'logged; writing and code work never checks in here, so a '
                     'day of that still reads 0.</p>')

    q_meth = ""
    if machine_q:
        q_rows = ""
        for t in merge_queue(machine_q):
            what, why = queue_row_story(t)
            wkey = str(t.get("worker", "any"))
            wnice = MACHINES.get(wkey, (wkey, ""))[0] if wkey != "any" else "any machine"
            q_rows += (f'<div class="prod-row"><b>{_e(what)}</b> · waits for {_e(wnice)}'
                       + (f'<br><span class="why">{_e(visitor_sentence(why, 170))}</span>'
                          if why else "")
                       + '</div>')
        queued_html = (f'<h3>⏭ Queued for a machine <span class="count">'
                       f'{len(machine_q)}</span></h3>'
                       '<p class="mono">Claimed by whichever named machine polls '
                       'the queue next; nothing here waits on a person.</p>' + q_rows)
    else:
        # The render box's own on-disk queue replaced the shared file as the
        # production queue (2026-08-10); a supervisor writes a measured
        # snapshot of it. Prefer that with its own timestamp — a zero from the
        # shared file alone reads as "idle" during a fully-loaded night.
        if boxq:
            # THE DEPTH AS BLOCKS, then ONE line of words (Roman, 2026-08-14:
            # "can you make the queue more visuals and less text?"). What is
            # baked here is the no-JS floor off the supervisor's own snapshot —
            # LIVE_JS redraws the same strip, key and line from the box's
            # five-minute publish, which is newer than any build.
            blocks, hidden, kcounts = queue_blocks(
                boxq["kinds"], boxq["ready"], boxq["running"])
            # HOW LONG THAT IS, in time (Roman, 2026-08-12) — now a clause on
            # the one caption rather than a sentence of its own. Where no median
            # has been measured the caption stays silent about time; it never
            # falls back to a guess. The basis moved into the fold below.
            words = queue_time_words(boxq)
            if words and boxq["jobs"]:
                timing = f' · ~{_e(words)}, estimated'
            elif boxq["jobs"]:
                timing = " · not timed: no median measured yet"
            else:
                timing = ""
            # Same ids as the glance tile's: the browser rewrites both from the
            # box's own publish, and what is baked is the no-JS floor.
            # A SUBHEAD, not a second section title. "⏭ Queued for a machine"
            # was an h3 when this lived five screens down inside the work list;
            # at the top of the page, under a section already called "The
            # queue", it was the same words twice. The count keeps its id —
            # LIVE_JS rewrites it — and it may not go inside #q-notice, whose
            # textContent the same function overwrites wholesale.
            queued_html = (QNOW_BAKED
                           + f'<p class="qsub"><span class="count" '
                           f'id="q-count">{boxq["jobs"]}</span> on the box</p>'
                           + queue_strip_html(blocks, hidden)
                           + queue_legend_html(kcounts)
                           + f'<p class="qcap" id="q-notice">'
                           f'{boxq["running"]} rendering, {boxq["ready"]} '
                           f'waiting{timing} · measured '
                           f'{_e(boxq["measured_at"])}.</p>')
            meth = (
                '<p>The blocks are the render box’s own on-disk queue, one per '
                'job, newest reading the box published. It reports how many '
                'jobs are waiting and <b>what kinds</b> they are — never their '
                'names — so only the block a card is actually running can say '
                'which beat it belongs to. The shared queue file has nothing '
                'runnable, which is why nothing here is waiting on a person.</p>')
            if words and boxq["jobs"] and queue_time_basis(boxq):
                meth += (f'<p>The time is an estimate, not a measurement: '
                         f'{_e(queue_time_basis(boxq))}. A queue that fails a '
                         'job or picks up a slower one will not match it.</p>')
            elif boxq["jobs"]:
                meth += ('<p>How long that is in time is not estimated here: no '
                         'median job time has been measured off the box’s own '
                         'finished jobs, and a made-up minute is worse than '
                         'none.</p>')
            q_meth = ('<details class="drawer qmeth"><summary>Where these '
                      'blocks come from, and what the estimate is worth'
                      '</summary><div class="drawer-body">' + meth
                      + '</div></details>')
        else:
            box_note = (' The render box also keeps its own on-disk queue between '
                        'pushes — its last idle report above is the only honest '
                        'reading of that.' if depth else "")
            q_meth = ''
            queued_html = (QNOW_BAKED
                           + '<p class="qsub"><span class="count" '
                           'id="q-count">0</span> on the box</p>'
                           + queue_strip_html([])
                           + queue_legend_html({})
                           + '<p class="qcap" id="q-notice">Nothing in the shared '
                           'queue file is waiting for a machine.' + box_note + '</p>')
    # WHAT THE CARD IS MAKING, behind a fold (Roman, 2026-08-13: "you should make
    # it so you can see exactly what is being generated on the status page and see
    # the images when its generated, probably only seeable by opening some
    # dropdown though"). Collapsed by default and EMPTY until opened: the strip
    # pulls finished frames straight off the courier branch, and a page that
    # fetched a dozen of those on load would spend megabytes on every visitor who
    # never asked. The baked state is the honest no-JS one — this cannot be
    # rendered at build time, because the whole point is that it is current.
    # THE REST OF THE BOX'S FACTS AS BADGES, not as more clauses on the caption.
    # Finished today, failures sitting in failed/, a runner that is not draining
    # the queue, a card on battery: each is one number or one warning, and each
    # was a comma in a sentence nobody read to the end. Baked empty on purpose —
    # every one of them is a live reading, and a badge with a build-time number
    # in it would be the stale-meter bug wearing a new shape.
    queued_html += '<div class="qchips" id="q-chips"></div>'
    # QUEUE DEPTH OVER THE LAST DAY. Baked empty, exactly like the infra meter
    # and the live tile: the history lives in the box's own telemetry publish
    # and arrives in the reader's browser, so a build has nothing to draw and
    # would bake a picture that stopped moving. The sentence below is the
    # honest no-JavaScript floor, and drawDepth() replaces it with either a
    # sparkline or a plainer sentence about why there is not one yet.
    queued_html += (
        '<div class="qspark" id="q-spark">'
        '<p class="mono" id="q-spark-note">How deep this queue has been over '
        'the last day is read by your browser from the box’s own five-minute '
        'publish. With JavaScript off there is nothing here to read — the '
        'history is not built into this page, because it would be stale the '
        'moment it was.</p></div>')
    queued_html += q_meth
    queued_html += (
        '<details class="peek" id="q-peek">'
        '<summary>Look inside — what the card is making right now</summary>'
        '<div class="peek-body" id="q-peek-body">'
        '<p class="mono" id="q-peek-note">This is a live view: your browser reads '
        'the render box’s own five-minute report when you open this. With '
        'JavaScript off there is nothing here to read — the frames it shows '
        'are fetched from the box’s results branch, not built into this page.'
        '</p></div></details>')
    if hand_q:
        queued_html += (
            f'<p class="mono">{len(hand_q)} more '
            f'entr{"y is" if len(hand_q) == 1 else "ies are"} addressed to a '
            'person, to run by hand — machine-facing detail this page leaves to '
            f'<a href="https://github.com/{GH}/blob/main/pipeline/farm-queue.yaml">'
            'the queue file itself</a>.</p>')

    # --- THE QUEUE GOES FIRST (Roman, 2026-08-14: "shouldnt the queue be at the
    # top?"). It is the only section on this page that updates itself while you
    # look at it — everything below is a snapshot with a build stamp on it — and
    # it is the one he opens the page to see. It used to sit inside the work
    # list, five screens down, under a summary strip, an episode player and a
    # tree.
    #
    # THE HEADLINE NUMBER IS THE OLD GLANCE TILE, moved rather than copied. The
    # strip at the top had a queue cell saying "~42 min of work queued" directly
    # above a section saying the same thing; duplicated information is the
    # founder's standing complaint, so the cell is gone from the strip and its
    # two ids live here. LIVE_JS rewrites them exactly as before — the contract
    # that test holds is the id, not the address.
    live_queue = (
        '<section class="qsec rise" id="queue">'
        '<h2>⏭ The queue — what the render box is doing now</h2>'
        '<p class="chead">Live — everything below this box is a snapshot. '
        # This section can only ever say how MANY jobs are waiting: the box
        # publishes counts, never names (telemetry.py). /queue is where a job
        # becomes a thing you can read — its prompt, its reference frame, the
        # files it made — so the pointer belongs here, next to the counts that
        # cannot answer "why does that beat look like that".
        'Every job\'s exact prompt, reference frame and output files: '
        '<a href="queue.html">full history →</a></p>'
        f'<div class="qhead">{queue_head_html(boxq)}</div>'
        f'{queued_html}</section>')

    counts = strip_counts(queue, backlog, records)
    blocked_total = sum(v["est"] or 0 for v in map(backlog_entry_view, backlog))
    groups = backlog_groups(backlog)
    gate_line = " · ".join(f"{len(g_rows)} {head}"
                           for _g, _emo, head, _b, g_rows, _m in groups)
    if backlog:
        planned_html = (
            f'<h3>🧱 Planned, and what each one is waiting for '
            f'<span class="count">{len(backlog)}</span></h3>'
            f'<p class="mono">{_e(gate_line)}'
            # hours_words says "about" itself past 90 min — no prefix, or the
            # line reads "about about 13.2 h" (caught on the built page).
            + (f' · {_e(hours_words(blocked_total))} of machine time parked'
               if blocked_total else "") + '</p>'
            '<details class="drawer"><summary>Open the planned list — one line '
            'per job, with its blocker</summary>'
            f'<div class="drawer-body">{backlog_html(backlog)}</div></details>')
    else:
        planned_html = ('<h3>🧱 Planned, and what each one is waiting for '
                        '<span class="count">0</span></h3>'
                        '<p class="notice">The backlog is empty — every planned '
                        'job has either run or been dropped.</p>')

    total_entries = len(queue) + len(backlog)
    state_bits = ", ".join(
        f"{counts[k]} {QSTATES[k][1].lower()}"
        for k in ("runnable", "running", "done", "failed", "waiting", "blocked",
                  "planned") if counts[k])
    # CHART FIRST, PROSE IN A FOLD. The section used to open with two
    # paragraphs about where its numbers come from, which is the right
    # information in the wrong order — a reader arrives asking "has the machine
    # been working?" and had to read 90 words of provenance before anything
    # answered them. The bars answer it in one look; the provenance is one click
    # down and has lost not a word.
    work_chart = charts.work_days_html(read_work_daily())
    production = (
        '<h2 id="worklist">🏭 The work list</h2>'
        '<p class="chead">What the machines have already done. The queue itself '
        '— the live part — is <a href="#queue">at the top of this page</a>.</p>'
        + (f'<p class="chead">How hard the render box has worked, day by day</p>'
           f'{work_chart}' if work_chart else "")
        + '<details class="drawer"><summary>Where every line in this section '
        'comes from</summary><div class="drawer-body">'
        '<p>What the machines were on when last heard, what shipped in the last '
        'day, and what is queued or held. Every line comes from a machine\'s '
        'own dated check-in log or from the shared queue file — never a guess, '
        'and never a claim about this exact minute.</p>'
        '<p class="livemark" id="q-live">This is the work queue as this copy of '
        'the page was built. With JavaScript on, your browser re-reads the queue '
        'file itself and says here whether it has changed since.</p>'
        '</div></details>'
        f'{onmach}{done_html}{planned_html}'
        f'<p class="whyfoot">The shared queue file holds {total_entries} '
        f'entr{"y" if total_entries == 1 else "ies"} at build time'
        + (f' ({_e(state_bits)})' if state_bits else "") + '. The file is the '
        'intent and the check-in logs are what happened; where the two disagree '
        'the logs win. Read it yourself: '
        f'<a href="https://github.com/{GH}/blob/main/pipeline/farm-queue.yaml">'
        'pipeline/farm-queue.yaml</a>.</p>'
        '<p class="whyfoot">Finished frames land on each machine\'s courier '
        'branch, get checked, and show up as choices on the '
        f'<a href="{_e(hero["board"])}">shot board</a> — the author (and anyone '
        'watching) picks what survives.</p>')

    # --- the footprint: money, bandwidth, builds — one line, detail in a drawer.
    pay = video_payload(out_dir)
    payline = (f'one full watch of everything published moves '
               f'{bytes_words(pay["bytes"])}' if pay.get("ok")
               else "this build could not measure its own video payload")
    footprint = (
        '<h2 id="footprint">📦 The footprint — money, bandwidth, builds</h2>'
        f'<p class="summary"><b>${spend:.2f}</b> spent on renders, lifetime — '
        'everything else runs on the family\'s own machines · '
        f'{_e(payline)} · measured on the box: rendering itself moves less '
        'than a phone checking mail.</p>'
        '<details class="drawer"><summary>Open the full accounting — every '
        'number with its date and its caveat</summary><div class="drawer-body">'
        f'{bandwidth_html(pay)}{infra_html}</div></details>')

    # --- the reactions thread, in one line. The bubble grid died with the lot.
    comments = latest_thread_comments(1)
    if comments:
        who, said, url = comments[-1]
        thread_line = (f'<p class="summary">💬 Newest on the reactions thread: '
                       f'“{_e(said)}” — {_e(who)} · '
                       f'<a href="{_e(url)}">join the thread &rarr;</a></p>')
    else:
        thread_line = ('<p class="summary">💬 The reactions thread is quiet — '
                       f'<a href="https://github.com/{GH}/issues/1">be the '
                       'first &rarr;</a></p>')

    # --- what this caption is allowed to call the cut. It said "the working cut"
    # unconditionally, which stopped being true on 2026-08-13: the founder closed
    # episode 1 — "we have already published it dude, we are done. lets move on to
    # episode 2." — recorded in review/inbox.yaml and carried verbatim in
    # pipeline/measured/episode-progress.yaml `ep1_publication_CORRECTION_0819`.
    # `data.cut_passed()` now reads that ruling, so the wording follows the same
    # flag the milestones line does and the two can never disagree again.
    #
    # THE STILLS COUNT STAYS, because it is still a true measurement — it just is
    # not an ASK any more. 14/15 carry a pick made one at a time; the fifteenth was
    # passed the way the other eleven were, by publishing the cut, and the caption
    # says so instead of leaving a gap that reads as an outstanding gate.
    ruling = data.publication_ruling()
    if passed:
        cut_line = ('the published cut'
                    + (f', live since {_e(ruling["date"])}' if ruling else '')
                    + f' — {tot["final"]}/{tot["total"]} beat STILLS carry a pick '
                      'made on its own; publishing the cut passed the rest')
    else:
        cut_line = (f'the working cut — {tot["final"]}/{tot["total"]} beat STILLS '
                    'carry the author’s pick; the motion over them is a separate '
                    'clock — see “When is an episode finished”')

    player = (f'<figure class="phone"><video controls playsinline preload="metadata" '
              f'poster="{_e(hero["poster"])}" src="{_e(hero["video"])}"></video>'
              f'<figcaption>Episode {hero["number"]} · “{_e(hero["title"])}” — '
              f'{cut_line}</figcaption></figure>'
              ) if hero["video"] else (
        f'<p><a class="btn" href="{_e(hero["watch"])}">▶ Watch episode {hero["number"]} &rarr;</a></p>')

    # Same ruling, same reason as the caption above: once the episode is
    # published, a still with no pick of its own is a MEASUREMENT, not a gate.
    # Left as "waiting on the author" it contradicted the caption two lines up —
    # one surface saying publishing passed the rest, the other still counting him
    # as the blocker — which is exactly the drift this pass exists to remove.
    waiting = (f'{tot["awaiting_render"]} waiting on a render · '
               + (f'{tot["awaiting_pick"]} passed with the cut rather than on '
                  'its own' if passed
                  else f'{tot["awaiting_pick"]} waiting on the author to pick'))

    out = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">{build_commit.meta_tags()}
<meta name="description" content="{_e(DESC)}">
<link rel="canonical" href="{CANONICAL}/{PAGE}">
<link rel="alternate" type="application/rss+xml" title="new nodes" href="{CANONICAL}/feed.xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Banyan City">
<meta property="og:title" content="Banyan City — {PAGE_NAME}">
<meta property="og:description" content="{_e(DESC)}">
<meta property="og:url" content="{CANONICAL}/{PAGE}">
<meta property="og:image" content="{CANONICAL}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Banyan City — {PAGE_NAME}">
<meta name="twitter:description" content="{_e(DESC)}">
<meta name="twitter:image" content="{CANONICAL}/og.png">
<title>Banyan City — {PAGE_NAME}</title>
<style>{THEME_CSS}{SIM_CSS}{STRIP_CSS}{charts.CHART_CSS}</style>
</head>
<body>
<main>
<nav class="crumbs"><a href="index.html">🌳 banyan-city</a> · <a href="watch.html">▶ watch</a>
 · <a href="city.html">the city</a> · <a href="machine.html">⚙️ how it works</a>
 · <b>🏗 {PAGE_NAME}</b> · <a href="https://github.com/{GH}">source</a></nav>

<div class="rise">
<p class="eyebrow">Banyan City · {PAGE_NAME}</p>
<h1>{PAGE_NAME.title()}</h1>
</div>

{live_queue}

<p class="lede rise">{data.PITCH}</p>

{strip}

<h2 id="waiting">🕰 Waiting on the author</h2>
<p style="margin:.2rem 0 .4rem;color:var(--muted)">These are calls only the author can make —
taste, and what gets published. The rest of the city keeps moving while they wait, but the
jobs listed under each one cannot start until it is made, and the number in front of each is
how long it has been sitting there.</p>
<p class="notice" style="margin:.2rem 0 .7rem">{review_pointer(review_open)}</p>
{waiting_html(inbox, backlog, now)}

{eta_section}

<div class="rise">
{player}
<p style="text-align:center">
  <a class="btn" href="{_e(hero["watch"])}">▶ Watch episode {hero["number"]}</a>
  <a class="btn ghost" href="{_e(hero["board"])}">🎬 See how it was made</a>
</p>
<p class="spend">total spent on renders so far: <b>${spend:.2f}</b> —
everything else runs on the family's own machines for free</p>
</div>

<h2 class="rise" id="tree">🌱 The Sapling, beat by beat</h2>
<div class="grove rise">
  {sapling}
  {growbar}
  <div class="label">{grove_caption}</div>
</div>
{ep2_now}
{milestones_line}
<p class="summary" style="text-align:center"><b>{tot["final"]} of {tot["total"]} scene frames approved</b> · {waiting}</p>
<details class="drawer"><summary>Every scene, and what it is waiting for</summary>
<div class="drawer-body">{scene_list_html(rows)}</div></details>

{production}

<h2>The machines</h2>
<ul class="machlist" id="machlist">{machlist}</ul>
<p class="whyfoot">A machine writes its check-in log only while a job runs, so silence there
means “no job”, never “no machine”; the render box also publishes its own vitals when its
reporter is up, and their minute-by-minute history lives on
<a href="pulse.html">the pulse page</a>.</p>

<h2>🗺 Open quests — anyone can take one</h2>
<p style="margin:.2rem 0 .4rem;color:var(--muted)">Nothing here is play-pretend: every art
quest is a real open request from the author, and every take handed in becomes part of the
show's public record.</p>
{quest_board_html(rows)}
<p class="whyfoot">every quest lands on the
<a href="{_e(hero["board"])}">scene-by-scene shot board</a> — the whole workshop is public</p>

{footprint}

{thread_line}

<p class="legend">{data.LEGEND}</p>
{pledger}
<footer>This copy was built {now.strftime('%Y-%m-%d %H:%M')}Z. No claim on this page is dated
by that stamp: every age counts from the moment its own datum was recorded, and your browser
re-reads the machines' check-in logs and the work queue for itself while the tab is open.
The page rebuilds when something it reads changes; a build stamp older than the newest commit
is the spend guard working, not the page failing. The whole repo IS the show —
<a href="index.html">the city</a> · <a href="lab/index.html">the lab</a> ·
<a href="machine.html">how it works</a></footer>
</main>
<script>
var TEL_STALE = {TELEMETRY_STALE_MINUTES};
var RAW_BASE = {json.dumps(RAW)}, QUEUE_URL = {json.dumps(QUEUE_URL)};
var BOX_TEL = {json.dumps(BOX_TEL_URL)}, BOX_TEL_LEGACY = {json.dumps(BOX_TEL_URL_LEGACY)},
    BOX_STALE = {int(BOX_QUEUE_STALE_MINUTES)},
    BOX_MEDIANS = {json.dumps(boxq["medians"] if boxq else {})},
    BOX_MEDIAN_FALLBACK = {json.dumps(boxq["fallback"] if boxq else None)},
    BOX_BAKED = {json.dumps(boxq["measured_at"] if boxq else "the build")},
    ACK_FAILED = {acknowledged_failures()},
    ACK_DOC = {json.dumps(ACK_FAILED_DOC)};
/* The strip's vocabulary, sent over from Python so the baked blocks and the
   redrawn ones cannot end up with two spellings of the same kind. */
var QKIND_CSS = {json.dumps(QUEUE_KIND_CSS)},
    QKIND_ONE = {json.dumps(QUEUE_KIND_ONE)},
    QKIND_MANY = {json.dumps(charts.KIND_WORDS)},
    QKIND_UNKNOWN_ONE = {json.dumps(QUEUE_UNKNOWN_ONE)},
    QKIND_UNKNOWN_MANY = {json.dumps(QUEUE_UNKNOWN_MANY)},
    QBLOCK_CAP = {int(QUEUE_BLOCK_CAP)};
var BUILT_AT = {int(now.timestamp())};
var BUILT_QUEUE = {json.dumps({"tasks": [str(t.get("id")) for t in queue],
                               "backlog": [str(b.get("id")) for b in backlog]})};
var INFRA_API = {json.dumps(meter["api"])},
    INFRA_HOURS = {int(meter["hours"])}, INFRA_PAGE = {int(meter["page"])},
    INFRA_TITLE = {json.dumps(meter["title"])},
    INFRA_UNAVAILABLE = {json.dumps(meter["unavailable"])},
    INFRA_UNIT_ONE = {json.dumps(meter["unit_one"])},
    INFRA_UNIT_MANY = {json.dumps(meter["unit_many"])};
{LIVE_JS}
{INFRA_JS}
</script>
</body>
</html>"""
    (out_dir / "status.html").write_text(out)
    # sim.html is a permanent redirect target only — "the sim" is a dev codeword.
    (out_dir / "sim.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta http-equiv="refresh" content="0;url=status.html">'
        '<link rel="canonical" href="https://banyan.city/status.html">'
        '<title>Banyan City — the studio</title></head><body>'
        '<p>This page moved: <a href="status.html">the studio &rarr;</a></p>'
        '</body></html>')
    _BUILT.add(str(out_dir.resolve()))
    print(f"✓ status.html (the studio) — {tot['final']}/{tot['total']} scenes final, "
          f"{len(machines)} machines, {len(fin)} finished in the last 24h")


if __name__ == "__main__":
    build(REPO / "_site")
