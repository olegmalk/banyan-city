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
from site_theme import THEME_CSS  # noqa: E402  the one visual language

GH = "olegmlkvorg/banyan-city"
API = f"https://api.github.com/repos/{GH}"
RAW = f"https://raw.githubusercontent.com/{GH}"
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
# changes" was the intent and was not the code: finished_today(), task_ids_done()
# and task_running() all walked the machine list, so a job a person ran and
# claimed could never appear as finished, and its queue entry kept publishing
# itself as open after the work shipped. The work-list counters read the ledgers
# below alongside the machines and attribute them by name; queue_promoter has
# always read their DONE lines exactly as it reads a worker's.
LEDGERS = {"hand": "run by hand"}
NOT_A_MACHINE = set(LEDGERS)   # the keys alone, for readers that only ask "is this a box"
STATE_WORDS = {  # css state → the legend under the town
    "working": "glowing = rendering right now",
    "idle": "dim = switched on, not rendering",
    "asleep": "faded = not heard from",
}

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


def branch_heartbeat(branch):
    """The newest line of a machine's own log — the STAGE it is at. This file
    carries a clock time and no date; `heartbeat_history` supplies the date."""
    txt = _get(f"{RAW}/{branch}/farm-out/heartbeat.txt", f"the check-in log for {branch}")
    return txt.strip().splitlines()[-1] if txt.strip() else ""


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
        else:
            continue
        if name not in out:   # the branch list is asked for once per reader
            out.append(name)
    return out


def heartbeat_history(branch, n=30, absent_ok=False):
    """[(when, line)] newest first — the check-in log WITH real dates.

    THIS IS THE FIX FOR THE OLDEST LIE ON THE PAGE. heartbeat.txt records
    `02:59:53Z DONE task=…` and no day, and the old reader compared that clock
    to today's, wrapping at 24 h: a box last heard from eight days ago read
    "12 h ago". The worker commits each line separately with the line as the
    commit message, so the history of that one path is the same log with the
    date attached — one request per machine, exact, no reconstruction.

    The commit supplies the DATE; where the line carries its own clock the line
    supplies the TIME (see line_time), so an entry is aged from when it was
    written and not from when it reached us. Re-sorted on that reading, because
    every caller below walks this list newest-first.
    """
    data = _api(f"/commits?sha={branch}&path=farm-out/heartbeat.txt&per_page={n}",
                log_label(branch), absent_ok=absent_ok)
    out = []
    for c in data or []:
        when = _iso((c.get("commit") or {}).get("committer", {}).get("date"))
        if when is None:
            continue
        msg = str((c.get("commit") or {}).get("message", "")).splitlines()[0]
        line = msg[4:].strip() if msg.startswith("hb: ") else msg.strip()
        out.append((line_time(line, when), line))
    return sorted(out, key=lambda r: r[0], reverse=True)


def telemetry_head(branch):
    """{'at': when, 'gpu': name} — a machine's own five-minute pulse, or None.

    This file is written whether or not there is work to do, which is the whole
    point: it answers "is the box on", a question the heartbeat cannot answer
    because the heartbeat is only written while a task runs. Absence is normal
    (only the render box publishes one), so it is not reported as a failure.
    """
    txt = _get(f"{RAW}/{branch}/telemetry.json", None)
    try:
        d = json.loads(txt)
        return {"at": datetime.datetime.fromtimestamp(float(d["last_sample"]),
                                                      datetime.timezone.utc),
                "gpu": str(d.get("gpu_name") or "")}
    except Exception:
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
        tail = branch_heartbeat(branch)
        hist = heartbeat_history(branch)
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
                    "history": heartbeat_history(branch, absent_ok=True)})
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


def finished_today(records: list, now=None) -> list:
    """[(when, who, task id, note)] for every job that finished since midnight —
    read off the dated commit log, so 'today' is a fact and not an inference
    from a clock time with no day attached.

    `records` is the machines PLUS the ledgers (read_ledgers), so "who" is
    either a machine's name or "run by hand". A job a person finished is a job
    finished, and it is the one kind this counter used to be unable to see.

    The line's own note rides along, because for the rows most likely to need it
    the queue has already forgotten the id (finished_line_story).
    """
    now = now or utcnow()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    out = []
    for m in records:
        for when, line in m["history"]:
            if when < start or hb_mark(line) != "DONE":
                continue
            tid = re.search(r"task=([\w.-]+)", line)
            out.append((when, m["name"], tid.group(1) if tid else "", hb_note(line)))
    return sorted(out, reverse=True)


def finished_line_story(task: dict, note: str) -> str:
    """What a "Finished today" row calls the job it reports.

    The queue entry is the better answer and usually there is one. When there is
    not, the row used to read "a job the queue no longer lists" — and that is
    not a rare case, it is the NORMAL end state: the promoter retires an entry
    the moment its DONE line lands, so the ids most certain to miss the lookup
    are the ones whose work most certainly shipped. Five such rows published the
    same eleven words on 2026-08-09, indistinguishable and uncheckable.

    The line is not silent about itself. A claim carries the claimer's note,
    which names the commit the work landed in — more specific than the queue's
    own wording and checkable against the repo, which the generic sentence never
    was. It only falls back when the runner really did write nothing.

    AND THE QUEUE ENTRY ONLY WINS WHEN IT DESCRIBES A RENDER. This was the third
    unguarded call to task_story and the only one that reached the live page: the
    GPU-claim cleanup finished at 15:38Z, its entry was still in `backlog:` for
    the lookup to find, and the row published "4 frames for world scenery" about
    a job that released a lock. The claim's own note is the better answer for
    everything that is not a render, which is what the paragraph above already
    argues — it just could not get there while any entry at all outranked it.
    """
    if task and any(task.get(k) for k in ("beats", "seeds", "video")):
        return task_story(task)[0]
    return note or "a job the queue no longer lists"


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


def task_running(tid: str, records: list) -> dict:
    """The machine or hand-run with a fresh STARTED for this id and no DONE
    after it, or None. This is the difference between QUEUED and RENDERING — a
    heading that called the whole queue "in production" was the third lie."""
    for m in records:
        for when, line in m["history"]:            # newest first
            if f"task={tid}" not in line:
                continue
            mark = hb_mark(line)
            if mark in ("DONE", "FAIL"):
                return None
            return {"runner": m, "since": when} if mark == "STARTED" else None
    return None


# ---- the queue, entry by entry -----------------------------------------------
# "status should show exactly the queue of work with all details" (founder,
# 2026-08-09). The work list above is the READABLE account of the queue and stays
# that way: it merges identical rows into one sentence, keeps task ids out as log
# tokens, and answers "what is the studio doing" for someone who has never read
# this repo. That section is not this one and neither replaces the other.
#
# This is the RECORD. Every entry in farm-queue.yaml appears exactly once, under
# its own id, with every field it carries — including fields this file has never
# heard of, which are printed as themselves rather than ignored. Nothing is
# merged, nothing is truncated, and the house dialect does not run over it: the
# point of the record is that a reader can diff it against the file. That is the
# same trade SITE.md already makes ("if a design choice trades away legibility of
# how it was made, that is the wrong trade").
#
# An entry that cannot be read gets printed LOUDLY instead of skipped. A queue
# page that silently shows 23 of 24 rows is worse than no queue page, because it
# is the one failure the page exists to catch.

# The fields the file's own header declares (farm-queue.yaml:23-89) and every
# reader downstream assumes. test_pipeline.py already asserts three of these four
# over the live file; this prints the fault instead of failing the build, because
# a status page that refuses to render is not a status page.
QUEUE_REQUIRED = ("id", "why", "runner", "worker")
QUEUE_RUNNERS = ("farm", "manual")
QUEUE_GATES = ("founder", "code", "hardware")

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
QSTATE_ORDER = ("running", "failed", "runnable", "waiting", "blocked",
                "planned", "done")


def claim_lines(records: list) -> dict:
    """task id → [(when, mark, who, note)], newest first, off every check-in log.

    task_running() and task_ids_done() each walk the same histories for one
    question apiece; the record needs all of it — when a job started, when it
    ended, which runner, and whatever the runner typed. Same `records` list
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


def entry_faults(e: dict) -> list:
    """Everything wrong with one entry, in the words of the file's own header.

    Only structural faults — a missing field, or a value outside the small set
    the header defines. Not taste, not staleness: this list is the difference
    between "the page can describe this entry" and "the page cannot", and a
    non-empty one sends the entry to the MALFORMED heading.
    """
    faults = []
    for k in QUEUE_REQUIRED:
        if not str(e.get(k) if e.get(k) is not None else "").strip():
            faults.append(f"no `{k}` — the file's header lists it as required")
    runner = str(e.get("runner") or "").strip()
    if runner and runner not in QUEUE_RUNNERS:
        faults.append(f"`runner: {runner}` is neither `farm` nor `manual`, so "
                      "neither the promoter nor a person knows if it is theirs")
    gate = str(e.get("gate") or "").strip()
    if gate and gate not in QUEUE_GATES:
        faults.append(f"`gate: {gate}` is not one of founder/code/hardware")
    if gate and not str(e.get("gate_ref") or "").strip():
        faults.append("a `gate` with no `gate_ref` — blocked, without saying by "
                      "what, which is the one thing a gate has to say")
    return faults


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


# Field → the label the record prints for it. `id`, `why`, `cmd`, `gate_ref` and
# `after` are laid out on their own and deliberately absent here. Any key NOT in
# this map still prints — see queue_entry_html — flagged as one the page does not
# know, because a field invented tomorrow must not vanish from the record today.
QFIELD_WORDS = {
    "worker": "worker", "runner": "runner", "needs": "needs", "window": "window",
    "est_minutes": "estimate", "gate": "gate", "node": "node", "beats": "beats",
    "seeds": "seeds", "seed_base": "seed base", "steps": "steps",
    "seconds": "seconds", "size": "size", "width": "width", "height": "height",
    "video": "video", "video_model": "model", "prefetch": "prefetch",
    "slug": "slug",
}


def qvalue(key: str, val) -> str:
    """One field value as the record prints it: the file's own value first, and a
    gloss only where the raw value is a token the reader cannot resolve."""
    if isinstance(val, bool):
        return "yes" if val else "no"
    if isinstance(val, (list, tuple)):
        return ", ".join(str(v) for v in val) or "—"
    s = str(val)
    if key == "worker":
        nice = MACHINES.get(s, (None,))[0]
        if nice:
            return f"{s} ({nice})"
        return f"{s} (any machine that matches `needs`)" if s == "any" else s
    if key == "est_minutes":
        try:
            return f"{int(val)} min (an estimate, not a measurement)"
        except (TypeError, ValueError):
            return s
    if key == "window":
        return f"{s} — advisory only; the promoter never delays on it"
    return s


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


def steps_table_html(steps: list) -> str:
    """Named columns, and a heading that admits most values are durations."""
    body = "".join(f"<tr><td>{_e(a)}</td><td class='mono'>{_e(b)}</td></tr>" for a, b in steps)
    return ('<div class="scroll"><table><tr><th>Step</th><th>Time &amp; cost</th></tr>'
            f"{body}</table></div>")


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


def waiting_html(inbox: list, backlog: list, now=None) -> str:
    """The author's decision queue, with the age of each wait and the work
    parked behind it. Read-only for everyone else — the old board offered five
    identical gold 'look →' links for calls a visitor cannot make."""
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
            jobs = "; ".join(first_sentence(h["why"], 150) for h in held if h["why"])
            tail = (f'<div class="held"><b>{len(held)} job'
                    f'{"s" if len(held) != 1 else ""} parked behind this call</b>'
                    + (f' · {_e(hours_words(mins))} of machine time' if mins else "")
                    + (f'<br>{_e(jobs)}' if jobs else "") + "</div>")
        out.append(f'<li><span class="waited">{_e(waiting_words(q.get("since"), now))}'
                   f'</span> <b>{_e(q.get("title", ""))}</b>{a}'
                   f'<div class="mono">{_e(q.get("detail", ""))}</div>{tail}</li>')
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
            items += ('<li>'
                      + (f'<b>{_e(r["what"])}</b><br>' if r["what"] else "")
                      + (f'<span class="why">{_e(r["why"])}</span>' if r["why"] else "")
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


def queue_entry_html(e: dict, listname: str, state: str, claims: dict,
                     done_ids: set, faults: list, now=None) -> str:
    """One queue entry, whole. Every key the entry carries reaches the page."""
    now = now or utcnow()
    tid = str(e.get("id") or "")
    emoji, word, _blurb = QSTATES.get(state, ("•", state.upper(), ""))
    anchor = re.sub(r"[^\w.-]", "-", tid) or "unnamed"

    # The one-line summary the readable section would print, when the entry is
    # shaped like a render. Guarded exactly as backlog_entry_view guards it —
    # task_story answers for render work and calls everything else "frames for
    # world scenery", which on this page would be a falsehood with an id on it.
    what = task_story(e)[0] if any(e.get(k) for k in ("beats", "seeds", "video")) else ""

    bits = [f'<div class="qtop"><span class="qchip {state}">{emoji} {_e(word)}</span>'
            f'<code class="qid">{_e(tid) or "(no id)"}</code>'
            f'<span class="qlist">{_e(listname)}:</span></div>']
    if faults:
        bits.append('<div class="qfault"><b>this entry cannot be read as queued '
                    'work</b><ul>'
                    + "".join(f"<li>{_e(f)}</li>" for f in faults) + "</ul></div>")
    if what:
        bits.append(f'<div class="qwhat">{_e(what)}</div>')
    if e.get("why"):
        bits.append(f'<div class="qwhy">{_e(str(e["why"]).strip())}</div>')
    if e.get("gate_ref"):
        bits.append('<div class="qgate"><b>blocked by</b> '
                    f'{_e(str(e["gate_ref"]).strip())}</div>')

    # `after:` is a real gate with a checkable answer, so it says which of the
    # ids it names has landed rather than only that it is waiting.
    after = e.get("after") or []
    if isinstance(after, str):
        after = [after]
    if after:
        deps = ", ".join(
            f'<code>{_e(str(a))}</code> {"✅ done" if str(a) in done_ids else "⏳ not yet"}'
            for a in after)
        bits.append(f'<div class="qdeps"><b>after</b> {deps}</div>')

    # EVERY REMAINING KEY, known or not. `id`/`why`/`cmd`/`gate_ref`/`after` are
    # already laid out above; anything else lands here, and a key this file has
    # never heard of is labelled as such instead of dropped.
    laid_out = {"id", "why", "cmd", "gate_ref", "after"}
    fields = ""
    for k in sorted(e.keys(), key=lambda k: (k not in QFIELD_WORDS, str(k))):
        if k in laid_out:
            continue
        known = k in QFIELD_WORDS
        label = QFIELD_WORDS.get(k, str(k))
        note = "" if known else ' <span class="qunknown">field not known to this page</span>'
        fields += (f'<div><dt>{_e(label)}</dt>'
                   f'<dd>{_e(qvalue(str(k), e.get(k)))}{note}</dd></div>')
    if fields:
        bits.append(f'<dl class="qfields">{fields}</dl>')

    lines = claims.get(tid, [])
    if lines:
        rows = "".join(
            f'<li><b>{_e(mark or "?")}</b> · {_e(who)} · {age_el(when, now)}'
            + (f'<br><span class="qnote">{_e(note)}</span>' if note else "")
            + "</li>"
            for when, mark, who, note in lines)
        bits.append(f'<div class="qclaims"><b>check-in lines for this id</b>'
                    f'<ul>{rows}</ul></div>')
    elif state in ("runnable", "waiting"):
        bits.append('<div class="qclaims mono">no check-in line for this id — '
                    'nobody has claimed it</div>')

    if e.get("cmd"):
        bits.append(f'<pre class="qcmd">{_e(str(e["cmd"]).strip())}</pre>')
    return f'<li class="qrow" id="q-{_e(anchor)}">{"".join(bits)}</li>'


def queue_record_html(tasks: list, backlog: list, records: list, dropped: list,
                      now=None) -> str:
    """The whole queue, entry by entry, grouped by state — malformed first.

    Malformed goes FIRST and not last on purpose. It is the only group whose
    contents mean the page itself is unreliable, and a fault printed under
    twenty-four healthy rows is a fault nobody scrolls to.
    """
    now = now or utcnow()
    claims = claim_lines(records)
    done_ids = task_ids_done(records)

    groups, bad = {}, []
    for listname, entries in (("tasks", tasks), ("backlog", backlog)):
        for e in entries:
            faults = entry_faults(e)
            state = queue_entry_state(e, listname, claims, done_ids)
            row = queue_entry_html(e, listname, state, claims, done_ids, faults, now)
            (bad if faults else groups.setdefault(state, [])).append(row)

    total = len(tasks) + len(backlog)
    out = [f'<p class="mono">{total} entr{"y" if total == 1 else "ies"} in '
           '<code>pipeline/farm-queue.yaml</code> at build time — '
           f'{len(tasks)} runnable-now (<code>tasks:</code>) and {len(backlog)} '
           f'planned (<code>backlog:</code>). Every one of them is below, '
           'unmerged, with the fields exactly as the file writes them.</p>']

    # A dropped entry never became a dict, so it has no id to print and no state
    # to be in — it is reported as the parse fault it is, with its position.
    if dropped:
        out.append(
            f'<div class="qbad"><h3>🚨 MALFORMED — {len(dropped)} entr'
            f'{"y" if len(dropped) == 1 else "ies"} in the file are not entries</h3>'
            '<p class="mono">These are not shaped like queue entries at all, so '
            'no reader in this repo can act on them. They are listed by position '
            'because they have no id to be listed by.</p><ul class="qraw">'
            + "".join(f'<li><code>{_e(name)}:[{i}]</code> → <code>{_e(raw)}</code></li>'
                      for name, i, raw in dropped)
            + "</ul></div>")
    if bad:
        out.append(
            f'<div class="qbad"><h3>🚨 MALFORMED — {len(bad)} entr'
            f'{"y" if len(bad) == 1 else "ies"} missing a required field</h3>'
            '<p class="mono">Shown in full rather than skipped. Each names what '
            'it is missing, against the entry shape the queue file\'s own header '
            'defines. Silent truncation is the failure this section exists to '
            f'prevent.</p><ol class="qlist-ol">{"".join(bad)}</ol></div>')

    for state in QSTATE_ORDER:
        rows = groups.get(state)
        if not rows:
            continue
        emoji, word, blurb = QSTATES[state]
        out.append(f'<div class="qgroup"><h3>{emoji} {_e(word)} '
                   f'<span class="count">{len(rows)}</span></h3>'
                   f'<p class="mono">{_e(blurb)}</p>'
                   f'<ol class="qlist-ol">{"".join(rows)}</ol></div>')
    return "".join(out)


def walkers_html(comments: list, any_working: bool) -> str:
    """The crew, walking the lot. Every sprite is somebody real: the three
    people/agents who actually run the studio, up to two citizens straight off
    the reactions thread (their own usernames), and a courier only while a
    machine is truly rendering. Decoration is allowed to be charming; it is
    not allowed to invent staff."""
    folk = [("🧑‍💻", "the author"),
            ("🧑‍🔧", "the author's dad"),
            ("🤖", "the steward — an AI")]
    seen = set()
    for who, _said, _url in comments:
        if who in seen:
            continue                     # one commenter = one villager
        seen.add(who)
        folk.append((("🧑‍🌾", "🧙")[len(seen) % 2], who))
        if len(seen) == 2:
            break
    if any_working:
        folk.append(("🛻", "hauling fresh frames"))
    out = ""
    for i, (spr, tag) in enumerate(folk):
        dur = 22 + i * 7                 # seconds one way — everyone ambles
        lo = 5 + i * 8                   # starting spot, % — also the resting
        out += (                         # spot when animations are off
            f'<div class="walker" aria-hidden="true" '
            f'style="--d:{dur}s; --lo:{lo}%; --delay:-{i * 9}s">'
            f'<span class="spr"><i>{spr}</i></span>'
            f'<span class="wtag">{_e(tag)}</span></div>')
    return out


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


def badges_html(milestones: list) -> str:
    """(emoji, name, unlocked, detail) → the milestone strip. Every unlocked
    badge is a checkable repo fact; a locked one names exactly what is
    missing, so the strip doubles as the episode's to-do list."""
    out = []
    for emoji, name, unlocked, detail in milestones:
        cls = "" if unlocked else " locked"
        out.append(f'<div class="badge{cls}"><div class="ico">{emoji}</div>'
                   f'<div class="nm">{_e(name)}</div>'
                   f'<div class="cap">{_e(detail)}</div></div>')
    return f'<div class="badges">{"".join(out)}</div>'


# ---- the render box's own telemetry -------------------------------------------
# Oleg asked for GPU utilisation and RAM over time (2026-08-04), the day the 5090
# bluescreened mid-render and we had no idea what the machine was doing when it
# went. The box samples itself every 10s and publishes a 24-hour, 1-minute summary
# to its courier branch; the browser fetches THAT, so the numbers are as fresh as
# the box's last push instead of as fresh as the last deploy.
#
# This is the only live thing on this page, and the honesty rule (SITE.md) applies
# hardest here: a chart is drawn ONLY when the newest sample is younger than
# TELEMETRY_STALE_MINUTES. Otherwise the page says "no recent telemetry" and means
# it. Same repo constant as every other raw fetch on this page — the deploy server
# has no git refs to read a remote from.
TELEMETRY_BRANCH = "farm-results-rtx5090"
TELEMETRY_URL = f"{RAW}/{TELEMETRY_BRANCH}/telemetry.json"
QUEUE_URL = f"{RAW}/main/pipeline/farm-queue.yaml"
# TELEMETRY_STALE_MINUTES lives with the other freshness rules at the top of the
# file — it was declared twice, and two constants of the same name is one edit
# away from a page whose chart and whose machine list disagree about "stale".

TEL_CSS = """
/* ---- the render box: three single-axis charts, one series each.
   ONE SERIES PER CHART is not a layout accident. GPU% and GB cannot share a y
   axis without lying about scale, and the two colours this site owns — leaf green
   and sap amber — are 4.5 ΔE apart under protanopia (measured), so a two-series
   chart would encode identity in a difference some readers cannot see. A title
   per chart carries the identity instead, and no legend is needed. ---- */
.telnote { font: 500 .82rem/1.7 var(--mono); color: var(--faint); }
.tchart { margin: 1.1rem 0 0; }
.tchart figcaption { font: 700 .72rem/1.5 var(--mono); letter-spacing: .06em;
  text-transform: uppercase; color: var(--muted); display: flex; flex-wrap: wrap;
  justify-content: space-between; gap: .2rem .8rem; }
.tchart figcaption .cap { font-weight: 500; text-transform: none; letter-spacing: 0;
  color: var(--faint); }
.tchart svg { width: 100%; height: auto; display: block; margin: .35rem 0 .15rem;
  background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 12px; touch-action: pan-y; }
.tchart .rdout { font: 500 .74rem/1.6 var(--mono); color: var(--faint);
  min-height: 1.6em; font-variant-numeric: tabular-nums; }
.tchart .rdout b { color: var(--ink); }
.tchart .grid { stroke: var(--line-soft); stroke-width: 1; }
.tchart .axis { fill: var(--faint); font: 500 10px var(--mono); }
.tchart .ln { fill: none; stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
.tchart .fill { stroke: none; opacity: .13; }
.tchart .pk { fill: var(--ink); font: 600 10px var(--mono); }
.tchart .dot { stroke: var(--panel); stroke-width: 2; }
.tchart .cross { stroke: var(--muted); stroke-width: 1; stroke-dasharray: 2 3; }
.tel-gpu { color: var(--sap); }        /* the series wears currentColor */
.tel-mem { color: var(--leaf); }
"""

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

# Plain string, not an f-string: this is JavaScript and it is full of braces.
# TEL_URL / TEL_STALE are emitted next to it by build().
TEL_JS = """
/* The render box's charts. No library, no external code — one fetch of our own
   JSON off the courier branch, three inline SVGs, ~150 lines. If any of it fails
   the page says so in words instead of drawing a dead chart. */
(function () {
  var note = document.getElementById("tel-note"), body = document.getElementById("tel-body");
  if (!note || !body || !window.fetch) return;          /* no JS, no claim */
  var W = 720, H = 150, PL = 40, PR = 12, PT = 12, PB = 20, BASE = H - PB;
  var charts = [];

  function hhmm(sec) {   /* the VIEWER's clock, never ours */
    return new Date(sec * 1000).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});
  }
  /* a 24-hour window crosses midnight, and four bare clock labels cannot say
     which side of it a point is on — so the left-hand tick and every summary
     carry the date too. */
  function stamp(sec) {
    return new Date(sec * 1000).toLocaleString([], {month: "short", day: "numeric",
                                                    hour: "2-digit", minute: "2-digit"});
  }
  function ago(sec) {
    var m = Math.round(Date.now() / 1000 / 60 - sec / 60);
    if (m < 1) return "less than a minute";
    if (m < 60) return m + " min";
    return Math.floor(m / 60) + "h " + (m % 60) + "m";
  }
  function fmt(v, dec, unit) { return v == null ? "\\u2014" : v.toFixed(dec) + unit; }
  function last(a) { for (var i = a.length - 1; i >= 0; i--) if (a[i] != null) return a[i]; return null; }
  function peak(a) {
    var bi = -1, bv = null;
    for (var i = 0; i < a.length; i++) if (a[i] != null && (bv === null || a[i] > bv)) { bv = a[i]; bi = i; }
    return bi;
  }

  function chart(d, key, o) {
    var t = d.t, v = d[key], n = t.length, id = "tc-" + key;
    var t0 = t[0], span = Math.max(60, t[n - 1] - t0);
    var gap = (d.bucket_seconds || 60) * 3;
    function x(i) { return PL + (t[i] - t0) / span * (W - PL - PR); }
    function y(val) { return BASE - Math.max(0, Math.min(1, val / o.max)) * (BASE - PT); }
    /* segments: a hole in the data is a HOLE. Joining across one would draw
       utilisation for minutes the box was off. */
    var segs = [], cur = [], i;
    for (i = 0; i < n; i++) {
      if (v[i] == null || (i && t[i] - t[i - 1] > gap)) { if (cur.length) segs.push(cur); cur = []; }
      if (v[i] != null) cur.push(i);
    }
    if (cur.length) segs.push(cur);
    if (!segs.length) return "";
    var line = "", fill = "";
    segs.forEach(function (s) {
      var p = s.map(function (j, k) { return (k ? "L" : "M") + x(j).toFixed(1) + " " + y(v[j]).toFixed(1); }).join(" ");
      line += p + " ";
      if (s.length > 1) {
        fill += "M" + x(s[0]).toFixed(1) + " " + BASE + " " + p.slice(1) +
                " L" + x(s[s.length - 1]).toFixed(1) + " " + BASE + " Z ";
      }
    });
    var g = "";
    [0, 0.5, 1].forEach(function (f) {
      var yy = BASE - f * (BASE - PT);
      g += '<line class="grid" x1="' + PL + '" y1="' + yy.toFixed(1) + '" x2="' + (W - PR) +
           '" y2="' + yy.toFixed(1) + '"/><text class="axis" x="' + (PL - 6) + '" y="' +
           (yy + 3.5).toFixed(1) + '" text-anchor="end">' + (o.max * f).toFixed(o.tick) + '</text>';
    });
    [0, 1 / 3, 2 / 3, 1].forEach(function (f, k) {
      var xx = PL + f * (W - PL - PR);
      g += '<text class="axis" x="' + xx.toFixed(1) + '" y="' + (H - 6) + '" text-anchor="' +
           (k === 0 ? "start" : k === 3 ? "end" : "middle") + '">' +
           (k === 0 ? stamp(t0) : hhmm(t0 + f * span)) + '</text>';
    });
    var pi = peak(v), pm = "";
    if (pi >= 0) {
      var px = x(pi), py = y(v[pi]), rightish = px > (W + PL) / 2;
      pm = '<circle class="dot" cx="' + px.toFixed(1) + '" cy="' + py.toFixed(1) +
           '" r="3" fill="currentColor"/><text class="pk" x="' + (px + (rightish ? -7 : 7)).toFixed(1) +
           '" y="' + Math.max(PT + 8, py - 6).toFixed(1) + '" text-anchor="' +
           (rightish ? "end" : "start") + '">peak ' + fmt(v[pi], o.dec, o.unit) + '</text>';
    }
    charts.push({id: id, t: t, v: v, t0: t0, span: span, dec: o.dec, unit: o.unit,
                 dflt: (pi >= 0 ? "peak " + fmt(v[pi], o.dec, o.unit) + " at " + hhmm(t[pi]) +
                        " \\u00b7 point at the chart for any minute" : "")});
    return '<figure class="tchart ' + o.cls + '" id="' + id + '">' +
      '<figcaption><span>' + o.title + '</span><span class="cap">' + o.cap + '</span></figcaption>' +
      '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + o.title +
        ', ' + stamp(t0) + ' to ' + stamp(t[n - 1]) + ': latest ' + fmt(last(v), o.dec, o.unit) +
        ', peak ' + fmt(pi >= 0 ? v[pi] : null, o.dec, o.unit) + '">' + g +
      '<path class="fill" fill="currentColor" d="' + fill + '"/>' +
      '<path class="ln" stroke="currentColor" d="' + line + '"/>' + pm +
      '<line class="cross" x1="0" y1="' + PT + '" x2="0" y2="' + BASE + '" style="display:none"/>' +
      '<rect x="' + PL + '" y="' + PT + '" width="' + (W - PL - PR) + '" height="' + (BASE - PT) +
        '" fill="transparent"/></svg>' +
      '<div class="rdout">' + (charts[charts.length - 1].dflt) + '</div></figure>';
  }

  function tile(big, cap) {
    return '<div class="vital"><b>' + big + '</b><small>' + cap + '</small></div>';
  }

  function render(d) {
    var n = (d.t || []).length;
    var win = d.window_hours || 24;
    if (!n || !d.last_sample) {
      note.textContent = "no recent telemetry \\u2014 the render box has published a file " +
        "but it holds no samples from the last " + win + " hours.";
      return;
    }
    var stale = (Date.now() / 1000 - d.last_sample) > TEL_STALE * 60;
    var vmax = d.vram_total_gb || Math.max.apply(null, d.v.filter(function (x) { return x != null; })) * 1.1;
    var rmax = d.ram_total_gb || Math.max.apply(null, d.r.filter(function (x) { return x != null; })) * 1.1;
    var html = "";
    var pu = peak(d.up), pv = peak(d.v), pr = peak(d.r), pc = peak(d.c);
    html += '<div class="vitals">' +
      /* "peak sample", not "peak": this is the busiest single 10s reading, while
         the chart's peak marker is the busiest minute-AVERAGE. Two different true
         numbers; if both are called "peak" the page looks like it contradicts
         itself (it printed 100% here and 97% on the chart). */
      /* captions kept to four words: uppercase mono at this size wraps, and a
         caption that breaks mid-phrase ("VRAM IN USE · PEAK / 21.9 OF 23.9") reads
         as two half-labels. Each chart below states its own capacity anyway. */
      tile(fmt(last(d.u), 0, "%"), "gpu latest \\u00b7 peak sample " +
           fmt(pu >= 0 ? d.up[pu] : null, 0, "%")) +
      tile(fmt(last(d.v), 1, " GB"), "vram latest \\u00b7 peak " + fmt(pv >= 0 ? d.v[pv] : null, 1, " GB")) +
      tile(fmt(last(d.r), 1, " GB"), "ram latest \\u00b7 peak " + fmt(pr >= 0 ? d.r[pr] : null, 1, " GB")) +
      tile(fmt(pc >= 0 ? d.c[pc] : null, 1, " GB"), "commit peak \\u00b7 limit " +
           fmt(d.commit_limit_gb, 0, " GB")) +
      '</div>';
    html += chart(d, "u", {title: "GPU utilisation", cap: "% of the card, per minute",
                           max: 100, tick: 0, dec: 0, unit: "%", cls: "tel-gpu"});
    html += chart(d, "v", {title: "VRAM in use", cap: "GB of " + fmt(d.vram_total_gb, 1, " GB") + " on the card",
                           max: vmax, tick: 0, dec: 1, unit: " GB", cls: "tel-mem"});
    html += chart(d, "r", {title: "Host RAM in use", cap: "GB of " + fmt(d.ram_total_gb, 1, " GB") + " installed",
                           max: rmax, tick: 0, dec: 1, unit: " GB", cls: "tel-mem"});
    /* href set in JS, not concatenated into the markup: build_site.py's link
       checker reads every href in the output, and a spliced-together one reads to
       it as a broken local path (it caught exactly that, 2026-08-04). */
    var src = '<p class="whyfoot">straight from the machine: <a class="telsrc" href="#">telemetry.json</a>' +
      ' \\u2014 GPU by <code>nvidia-smi</code>, memory by <code>GlobalMemoryStatusEx</code>, sampled every ' +
      (d.sample_seconds || 10) + 's and averaged to one point a minute. Gaps are gaps: the line breaks ' +
      'wherever the box was not sampling.</p>';

    if (stale) {
      /* SITE.md: the site must not claim things it cannot know. A chart of
         yesterday under a heading about the render box reads as "now", so the
         plain sentence is the answer and the history is one click away, labelled
         with the hour it actually ends. */
      note.textContent = "no recent telemetry \\u2014 the newest sample from the render box is " +
        ago(d.last_sample) + " old (" + hhmm(d.last_sample) + " your time). The box may be off, " +
        "asleep, or unable to push; nothing here is claimed about it right now.";
      body.innerHTML = '<details class="drawer"><summary>show the ' + win +
        ' hours ending ' + stamp(d.last_sample) + '</summary><div class="drawer-body">' +
        html + src + '</div></details>';
    } else {
      note.textContent = (d.gpu_name || "the render box") + " \\u2014 newest sample " +
        hhmm(d.last_sample) + " your time (" + ago(d.last_sample) + " ago), " + win +
        "-hour window at one point a minute.";
      body.innerHTML = html + src;
    }
    body.hidden = false;
    var sa = body.querySelector(".telsrc");
    if (sa) sa.href = TEL_URL;
    charts.forEach(function (c) {
      var fig = document.getElementById(c.id);
      if (!fig) return;
      var svg = fig.querySelector("svg"), cross = fig.querySelector(".cross"),
          out = fig.querySelector(".rdout");
      function clear() { cross.style.display = "none"; out.textContent = c.dflt; }
      svg.addEventListener("pointermove", function (e) {
        var r = svg.getBoundingClientRect();
        var f = ((e.clientX - r.left) / r.width * W - PL) / (W - PL - PR);
        var want = c.t0 + Math.max(0, Math.min(1, f)) * c.span, bi = -1, bd = Infinity;
        for (var i = 0; i < c.t.length; i++) {
          var dist = Math.abs(c.t[i] - want);
          if (dist < bd) { bd = dist; bi = i; }
        }
        if (bi < 0 || c.v[bi] == null) return clear();
        var px = PL + (c.t[bi] - c.t0) / c.span * (W - PL - PR);
        cross.setAttribute("x1", px.toFixed(1));
        cross.setAttribute("x2", px.toFixed(1));
        cross.style.display = "";
        out.innerHTML = hhmm(c.t[bi]) + " \\u00b7 <b>" + fmt(c.v[bi], c.dec, c.unit) + "</b>";
      });
      svg.addEventListener("pointerleave", clear);
    });
  }

  /* per-minute cache key: raw.githubusercontent sits behind a CDN, and a status
     page that shows a five-minute-old copy of a five-minute-old file is stale
     twice over. */
  fetch(TEL_URL + "?_=" + Math.floor(Date.now() / 60000), {cache: "no-store"})
    .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(render)
    .catch(function (e) {
      note.textContent = "no recent telemetry \\u2014 the render box's published file could not " +
        "be read (" + e.message + "), so nothing is being claimed about the machine.";
    });
})();
"""


# Plain string, not an f-string: JavaScript, full of braces. RAW_BASE, QUEUE_URL,
# BUILT_AT and BUILT_QUEUE are emitted next to it by build().
LIVE_JS = """
/* ---- the page keeps up with the farm after the deploy ------------------------
   Three files, all of them ours, all fetched by the reader's own browser off
   raw.githubusercontent (Access-Control-Allow-Origin: *, verified): each
   machine's check-in log, each machine's vitals, and the work queue. No
   library, no external code, no request to any host but GitHub's raw CDN.

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
    fetch(RAW_BASE + "/" + branch + "/telemetry.json?_=" + bust(), {cache: "no-store"})
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
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

  function refresh() {
    var lis = document.querySelectorAll("#machlist li[data-branch]");
    for (var i = 0; i < lis.length; i++) {
      readLog(lis[i]);
      if (lis[i].getAttribute("data-tel")) readVitals(lis[i]);
    }
    readQueue();
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
/* ---- the lot: one living scene — sky, street, crew (tokens from the theme).
   All motion is transform-only on a handful of small elements, paused when the
   tab is hidden (body.away) and killed entirely under prefers-reduced-motion —
   the 2026-07-31 GPU lesson applies to every new animation on this page. ---- */
.lot { position: relative; height: 230px; overflow: hidden; border-radius: 18px;
  border: 1px solid var(--line-soft); margin: .5rem 0 .4rem;
  background:
    radial-gradient(460px 150px at 72% 0%, var(--bg-glow), transparent 70%),
    linear-gradient(180deg, transparent 73%, var(--panel-2) 73%); }
.lot .stars { position: absolute; top: 12px; left: 28%; letter-spacing: 4vw;
  color: var(--leaf-dim); font-size: .8rem; }
.lot .sun { position: absolute; top: 12px; left: 5%; text-align: center;
  font-size: 1.5rem; line-height: 1; }
.lot .cloud { position: absolute; top: 12px; right: 5%; text-align: center;
  font-size: 1.7rem; line-height: 1;
  animation: drift 48s ease-in-out infinite alternate; }
.lot .sun small, .lot .cloud small { display: block; font: 600 .58rem/1.5 var(--mono);
  color: var(--faint); }
@keyframes drift { from { transform: translateX(0) } to { transform: translateX(-64px) } }
.street { position: absolute; left: 0; right: 0; bottom: 27%; display: flex;
  justify-content: space-evenly; align-items: flex-end; }
.lot-bld { position: relative; text-align: center; }
.lot-bld .ico { display: block; font-size: clamp(1.7rem, 6vw, 2.4rem);
  line-height: 1.15; text-decoration: none; }
.lot-bld .btag { display: block; font: 600 .58rem/1.4 var(--mono); color: var(--faint); }
.lot-bld.working .ico { filter: drop-shadow(0 0 10px rgba(255,199,106,.8)); }
.lot-bld.working .btag { color: var(--sap); }
.lot-bld.idle { opacity: .85; }
.lot-bld.asleep { opacity: .45; filter: grayscale(.8); }
.lot-bld .smoke { position: absolute; top: -1.1rem; left: 0; right: 0; }
.lot-tree .ico { font-size: clamp(2.4rem, 8vw, 3.1rem); }
.walker { position: absolute; bottom: 8px; left: var(--lo); z-index: 3; text-align: center;
  animation: cross var(--d) linear var(--delay) infinite alternate; }
@keyframes cross { from { transform: translateX(0) } to { transform: translateX(min(58vw, 400px)) } }
.walker .spr { display: block; font-size: 1.35rem; line-height: 1.2;
  /* most emoji people face left, so the rightward leg wears the flip */
  animation: face calc(var(--d) * 2) steps(1) var(--delay) infinite; }
@keyframes face { 0%, 100% { transform: scaleX(-1) } 50% { transform: scaleX(1) } }
.walker .spr i { display: inline-block; font-style: normal;
  animation: bob .55s ease-in-out infinite alternate; }
@keyframes bob { from { transform: translateY(0) } to { transform: translateY(-3px) } }
.walker .wtag { display: block; font: 600 .58rem/1.4 var(--mono); color: var(--faint);
  background: var(--panel); border: 1px solid var(--line-soft); border-radius: 999px;
  padding: .06rem .4rem; white-space: nowrap; }
.machlist { list-style: none; padding: 0; margin: .5rem 0 0; }
.machlist li { padding: .45rem 0; border-bottom: 1px solid var(--line-soft);
  font-size: .92rem; }
.machlist li:last-child { border-bottom: 0; }
.machlist .mico { margin-right: .3rem; }
.grove { text-align: center; margin: 0 0 1.2rem; }
.canopy { display: grid; grid-template-columns: repeat(5, 2.1rem); gap: .1rem;
  justify-content: center; }
.leaf { font-size: 1.45rem; text-decoration: none; }
.leaf.bud { filter: grayscale(1) brightness(.5); }
.trunky { font-size: 4.4rem; line-height: 1; }
.grove .label { font: 600 .8rem/1.6 var(--mono); color: var(--muted); }
.smoke { height: 1.1rem; animation: puff 2.4s linear infinite; }
/* an infinite animation keeps the compositor running FOREVER, in every
   open tab — this page is meant to be left open, so it must go quiet
   when nobody is looking (founder's Mac, 2026-07-31: a Chrome GPU
   process at 100% of a core for 13 hours). */
body.away .smoke, body.away .lot .cloud,
body.away .walker, body.away .walker * { animation: none !important; }
@keyframes puff { 0% { opacity: .9; transform: translateY(0) } 100% { opacity: 0; transform: translateY(-11px) } }
.spend { font: 600 .8rem/1.6 var(--mono); color: var(--faint); text-align: center; }
.spend b { color: var(--sap); }
/* ---- the infra meter. Deliberately NOT one of the .vital tiles: those are
   four numbers a reader can check against the repo, and this one is fetched
   live from GitHub and can be absent. Mixing them would quietly weaken the
   promise the vitals row makes. ---- */
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
.citizens { display: flex; flex-wrap: wrap; gap: .6rem; justify-content: center; }
.citizen { flex: 1 1 45%; max-width: 210px; text-align: center; }
.citizen .bubble { display: block; background: var(--panel-2); border: 1px solid var(--line);
  color: var(--ink); border-radius: 12px; padding: .45rem .6rem; font-size: .78rem;
  text-align: left; }
.citizen .spr { font-size: 1.7rem; line-height: 1.4; }
.citizen small { font: 600 .7rem/1.4 var(--mono); color: var(--faint); display: block; }
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
.machlist li { padding: .6rem 0; }
.machlist .chip { margin-left: .35rem; vertical-align: .05em; }
.machlist .mstate { margin: .25rem 0 .1rem; }
.machlist .why { color: var(--muted); font-size: .84rem; }
.livemark { font: 500 .76rem/1.6 var(--mono); color: var(--faint); }
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

/* ---- the queue record: every entry, every field --------------------------
   Deliberately denser and more clerical than the work list above it. That
   section is prose for a stranger; this one is a file rendered legibly, so it
   leans on the mono face, keeps the ids selectable, and lets long values wrap
   rather than truncating anything. --alarm is local: the theme has a green and
   an amber and no red, and MALFORMED must not read as merely warm. ---- */
.qrec { --alarm: #e2564d; }
@media (prefers-color-scheme: light) { .qrec { --alarm: #b3261e; } }
.qgroup, .qbad { margin: 1.1rem 0 .2rem; }
.qgroup h3, .qbad h3 { margin-bottom: .1rem; }
.qbad { border: 1px solid var(--alarm); border-radius: 14px;
  padding: .2rem .8rem .7rem; margin-bottom: 1.2rem; }
.qbad h3 { color: var(--alarm); }
.qlist-ol, .qraw { list-style: none; padding: 0; margin: .4rem 0 0; }
.qraw li { font: 500 .76rem/1.7 var(--mono); overflow-wrap: anywhere; }
.qrow { background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 14px; padding: .7rem .95rem;
  margin: .6rem 0; }
.qtop { display: flex; flex-wrap: wrap; align-items: center; gap: .4rem; }
.qchip { display: inline-block; font: 700 .64rem/1 var(--mono);
  letter-spacing: .09em; border: 1px solid var(--line); border-radius: 999px;
  padding: .28rem .5rem; color: var(--faint); white-space: nowrap; }
.qchip.running { color: var(--sap); border-color: var(--sap-deep); }
.qchip.runnable { color: var(--leaf); border-color: var(--leaf-deep); }
.qchip.done { color: var(--leaf); border-color: var(--leaf-deep); opacity: .75; }
.qchip.failed { color: var(--alarm); border-color: var(--alarm); }
.qid { font: 600 .74rem/1.5 var(--mono); color: var(--muted);
  background: var(--code-bg); border-radius: 6px; padding: .12rem .35rem;
  overflow-wrap: anywhere; user-select: all; }
.qlist { font: 500 .68rem/1.5 var(--mono); color: var(--faint); }
.qwhat { font-weight: 600; margin: .4rem 0 .1rem; }
.qwhy { color: var(--muted); font-size: .86rem; }
.qgate { margin-top: .35rem; font-size: .84rem; color: var(--ink); }
.qgate b, .qdeps b, .qclaims b { color: var(--sap); font: 700 .68rem/1.6 var(--mono);
  letter-spacing: .06em; text-transform: uppercase; margin-right: .3rem; }
.qdeps { margin-top: .3rem; font: 500 .78rem/1.7 var(--mono); }
.qfields { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: .1rem .8rem; margin: .5rem 0 0; padding: .5rem 0 0;
  border-top: 1px solid var(--line-soft); }
.qfields dt { font: 700 .66rem/1.6 var(--mono); letter-spacing: .06em;
  text-transform: uppercase; color: var(--faint); }
.qfields dd { margin: 0 0 .3rem; font: 500 .78rem/1.6 var(--mono);
  color: var(--ink); overflow-wrap: anywhere; }
.qunknown { color: var(--alarm); font-size: .72rem; }
.qfault { margin: .45rem 0 .2rem; padding: .45rem .6rem; border-radius: 10px;
  border: 1px solid var(--alarm); font-size: .82rem; }
.qfault b { color: var(--alarm); }
.qfault ul { margin: .25rem 0 0; padding-left: 1.1rem;
  font: 500 .76rem/1.7 var(--mono); }
.qclaims { margin-top: .45rem; padding-top: .4rem;
  border-top: 1px solid var(--line-soft); }
.qclaims ul { list-style: none; padding: 0; margin: .2rem 0 0;
  font: 500 .76rem/1.7 var(--mono); }
.qclaims .qnote { color: var(--faint); }
.qcmd { margin: .5rem 0 0; padding: .5rem .6rem; background: var(--code-bg);
  border: 1px solid var(--line-soft); border-radius: 10px;
  font: 500 .74rem/1.6 var(--mono); color: var(--muted);
  white-space: pre-wrap; overflow-wrap: anywhere; }

/* ---- vitals: the four numbers a visitor can check against the repo ---- */
.vitals { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: .6rem; margin: .9rem 0 .4rem; }
.vital { text-align: center; padding: .75rem .5rem .6rem; border: 1px solid var(--line);
  border-radius: 14px; background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.vital b { display: block; font: 600 1.6rem/1.15 var(--display); color: var(--ink);
  font-variant-numeric: tabular-nums; }
.vital small { font: 600 .68rem/1.5 var(--mono); color: var(--faint);
  letter-spacing: .05em; text-transform: uppercase; }

/* ---- the growth meter: two file-existence facts per scene, nothing else ---- */
.growbar { height: 12px; max-width: 420px; margin: .7rem auto .35rem; overflow: hidden;
  border: 1px solid var(--line); border-radius: 999px; background: var(--code-bg); }
.growbar i { display: block; height: 100%; background: var(--sap); border-radius: 999px; }

/* leaf tiers — the tooltip carries the words, the tint is only a hint */
.leaf.pick { filter: none; text-decoration: none;
  text-shadow: 0 0 10px rgba(255,199,106,.9); }
.leaf.still { filter: saturate(.6); }

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

/* ---- milestones: unlocked = a repo fact; locked = the honest gap ---- */
.badges { display: flex; flex-wrap: wrap; gap: .6rem; justify-content: center;
  margin: .8rem 0 .3rem; }
.badge { flex: 1 1 45%; max-width: 168px; text-align: center; padding: .7rem .55rem .6rem;
  border: 1px solid var(--line); border-radius: 14px;
  background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.badge .ico { font-size: 1.9rem; line-height: 1.2; }
.badge .nm { font: 700 .74rem/1.35 var(--mono); margin: .15rem 0 .1rem; }
.badge .cap { font: 500 .68rem/1.5 var(--mono); color: var(--faint); }
.badge.locked { opacity: .5; filter: grayscale(1); border-style: dashed; }
.badge.locked .nm::after { content: " · locked"; color: var(--faint); font-weight: 500; }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; } }
"""


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
    takes = data.takes_tally()
    open_quests = sum(1 for r in rows if r["request"]) + 2  # + the standing two

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

    # --- the grove: 15 leaves, each one an actual scene you can go look at.
    # Four tiers a glance can tell apart; the tooltip carries the exact words.
    leaves = ""
    for r in rows:
        if r["final"] and r["animations"]:
            cls, glyph, stage = "grown", "🍃", "fully grown — frame approved and animated"
        elif r["final"]:
            cls, glyph, stage = "grown still", "🌿", "frame approved — not yet animated"
        elif r["candidates"]:
            cls, glyph, stage = ("pick", "🌱", f'sprouting — {r["candidates"]} frames '
                                 "wait for the author's pick")
        else:
            cls, glyph, stage = "bud", "🍃", "a bud — waiting for a render"
        leaves += (f'<a class="leaf {cls}" href="{_e(hero["board"])}#beat-{r["num"]:02d}" '
                   f'title="Scene {r["num"]:02d} — {_e(r["name"])} · {_e(stage)}">{glyph}</a>')
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

    # --- the lot: our machines as buildings on one street, crew walking it ---
    # ONE READ OF THE FARM, used by every section below. read_machines() dates
    # each check-in off the commit that pushed it, so the ages here are real:
    # the old arithmetic wrapped at 24 h and published a box last heard from on
    # 29 July as "12 h ago".
    now = utcnow()
    qdoc = queue_doc()
    queue, backlog = qdoc["tasks"], qdoc["backlog"]
    machines = read_machines(queue, backlog, now)
    # The street and the tiles below are the MACHINES; the work-list counters
    # further down are the machines AND the hand ledger. That split is the whole
    # of NOT_A_MACHINE: no building for a thing that is not a box, no blindness
    # about work it finished.
    records = machines + read_ledgers(now)
    bldgs, machlist, seen_states = "", "", []
    for m in machines:
        st = m["state"]
        seen_states.append(st["css"])
        title = f'{m["name"]} — {st["head"]} · {st["seen"]}'
        smoke = '<div class="smoke">💨</div>' if st["css"] == "working" else ""
        bldgs += (f'<div class="lot-bld {st["css"]}" data-mach="{_e(m["key"])}" '
                  f'title="{_e(title)}">{smoke}'
                  f'<span class="ico">{m["emoji"]}</span>'
                  f'<span class="btag">{_e(m["name"])}</span></div>')
        # Every claim on this line carries the age of the thing it describes,
        # and the ages tick in the reader's own browser (see LIVE_JS).
        bits = [f'last check-in {age_el(m["last_seen"], now)}'] if m["last_seen"] else \
            [f'<span class="age">{_e(st["seen"])}</span>']
        if m["telemetry"]:
            bits.append('vitals published <span data-role="vitals">'
                        f'{age_el(m["telemetry"]["at"], now)}</span>')
        machlist += (
            f'<li data-mach="{_e(m["key"])}" data-branch="{_e(m["branch"])}" '
            f'data-tail="{_e(st["raw"])}" data-built="{int(now.timestamp())}" '
            f'data-tel="{"1" if m["telemetry"] else ""}">'
            f'<span class="mico">{m["emoji"]}</span> <b>{_e(m["name"])}</b> '
            f'<span class="chip{" hot" if st["css"] == "working" else ""}" '
            f'data-role="chip">{_e(st["chip"])}</span>'
            f'<div class="mstate" data-role="head">{_e(st["head"])}</div>'
            + (f'<div class="why">{_e(st["why"])}</div>' if st["why"] else "")
            + f'<div class="mono" data-role="seen">{" · ".join(bits)}</div></li>')
    bldgs += (f'<div class="lot-bld lot-tree"><a class="ico" href="{_e(hero["page"])}" '
              f'title="Episode {hero["number"]} — {pct}% grown">🌳</a>'
              f'<span class="btag">episode {hero["number"]} · {pct}%</span></div>')
    day = data.day_count()
    sun = (f'<div class="sun">☀️<small>day {day} of production</small></div>'
           if day else "")
    comments = latest_thread_comments()
    lot = (f'<div class="lot">{sun}'
           '<div class="stars" aria-hidden="true">✦ ✧ ✦ ✧ ✦</div>'
           '<div class="cloud">☁️<small>cloud GPU — standing by (unused)</small></div>'
           f'<div class="street">{bldgs}</div>'
           f'{walkers_html(comments, "working" in seen_states)}</div>')

    # --- what is being rendered, what is merely queued, and what is blocked ---
    # QUEUED IS NOT IN PRODUCTION. The old heading printed the whole `tasks:`
    # list under "In production" — so a job nobody had started, and a job that
    # finished four days ago and had not been retired out of the file, both read
    # as work happening now. A task is RENDERING only when a machine's own log
    # holds a fresh STARTED for its id and no DONE after it.
    done_ids = task_ids_done(records)
    running = {}
    for t in queue:
        r = task_running(str(t.get("id")), records)
        if r:
            running[str(t.get("id"))] = r
    running_t = [t for t in queue if str(t.get("id")) in running]
    queued_t = [t for t in queue
                if str(t.get("id")) not in running and str(t.get("id")) not in done_ids]

    def _rows(tasks, stamp=None):
        html_rows = ""
        for t in merge_queue(tasks):
            what, why = queue_row_story(t)
            wkey = str(t.get("worker", "any"))
            wnice = MACHINES.get(wkey, (wkey, "🏠"))[0] if wkey != "any" else "any machine"
            extra = ""
            r = running.get(str(t.get("id")))
            if r:
                # Who is ACTUALLY running it beats who the queue asked for. For a
                # machine picking up its own task these are the same string; for a
                # hand-run, `worker:` names a box that is not doing the work.
                wnice = r["runner"]["name"]
            if stamp and r:
                extra = f'<br><span class="mono">started {age_el(r["since"], now)}</span>'
            html_rows += (f'<div class="prod-row"><b>{_e(wnice)}</b> · {_e(what)}{extra}'
                          f'<br><span class="why">{_e(why)}</span></div>')
        return html_rows

    if running_t:
        rendering = ('<h3>🔴 Rendering right now</h3>' + _rows(running_t, stamp=True))
    else:
        rendering = ('<h3>🔴 Rendering right now</h3><p class="notice">Nothing is '
                     'rendering this minute — no machine, and nobody by hand, has an '
                     'unfinished job in the check-in log.</p>')
    if queued_t:
        queued_html = (f'<h3>⏭ Queued and runnable <span class="count">{len(queued_t)}'
                       '</span></h3><p class="mono">Claimed by whichever named machine '
                       'polls the queue next; nothing here is waiting on a person.</p>'
                       + _rows(queued_t))
    else:
        queued_html = ('<h3>⏭ Queued and runnable <span class="count">0</span></h3>'
                       '<p class="notice">The runnable queue is empty. That is a '
                       'statement, not an oversight: it means no planned job is both '
                       'unblocked and shaped for a machine to pick up by itself.</p>')

    # --- finished today: DONE lines with real dates on them ---
    by_id = {str(t.get("id")): t for t in list(queue) + list(backlog)}
    fin = finished_today(records, now)
    if fin:
        fin_rows = ""
        for when, who, tid, note in fin:
            what = finished_line_story(by_id.get(tid), note)
            fin_rows += (f'<div class="prod-row"><b>{_e(who)}</b> · {_e(what)}'
                         f'<br><span class="mono">finished {age_el(when, now)}</span></div>')
        done_html = (f'<h3>✅ Finished today <span class="count">{len(fin)}</span></h3>'
                     + fin_rows)
    elif logs_unread():
        # NO NUMBER AT ALL — the infra meter's contract, for the same reason. A
        # zero printed off a read that failed is this page inventing the most
        # reassuring answer on exactly the failure it exists to catch.
        unread = logs_unread()
        named = (_and_list(unread) if len(unread) <= 3
                 else f"{len(unread)} of the check-in logs")
        done_html = ('<h3>✅ Finished today <span class="count">—</span></h3>'
                     f'<p class="notice">This build could not read {_e(named)}, so '
                     'it does not know what finished today and will not print a zero '
                     'it did not measure. The reason is listed with the other fetch '
                     'failures above.</p>')
    else:
        # WHAT THE ZERO ACTUALLY MEANS, in the words it can defend. "No job has
        # finished" is false in plain English on a day when plenty of work
        # shipped — the check-in log only ever records what a RENDER runner ran.
        # A code or writing task finishes by having its queue entry retired and
        # never writes a check-in line at all (pipeline/farm-queue.yaml:65-67,
        # the rule `after:` is built on), so a full day of it still reads 0 here.
        # Written after five such jobs were given heartbeat lines they were not
        # entitled to, purely to move this number off 0, and retracted (4924a29).
        done_html = ('<h3>✅ Finished today <span class="count">0</span></h3>'
                     '<p class="notice">No render job has finished since midnight '
                     'UTC. This counts work a render machine ran and logged; a code '
                     'or writing task finishes by its queue entry being retired and '
                     'never writes a check-in line, so a day of that work still '
                     'reads 0 here. Today is read off the dated check-in log, not '
                     'guessed from a clock time with no day attached.</p>')

    blocked_total = sum(v["est"] or 0 for v in map(backlog_entry_view, backlog))
    production = (
        '<h2>🏭 The work list</h2>'
        '<p style="margin:.2rem 0 .6rem;color:var(--muted)">Everything the studio '
        'has agreed to make, in the order reality allows: what a machine is '
        'actually running, what it can pick up next, what finished today, and '
        'what is planned but held — each held job with the blocker written down.</p>'
        '<p class="livemark" id="q-live">This is the work queue as this copy of the '
        'page was built. With JavaScript on, your browser re-reads the queue file '
        'itself and says here whether it has changed since.</p>'
        f'{rendering}{queued_html}{done_html}'
        f'<h3>🧱 Planned, and what each one is waiting for '
        f'<span class="count">{len(backlog)}</span></h3>'
        + ('<p class="mono">' + _e(hours_words(blocked_total))
           + ' of work sits here. A blocker is a fact about the world, not a '
             'priority call — nothing below can start until the named thing '
             'changes.</p>' if blocked_total else "")
        + backlog_html(backlog)
        + '<p class="whyfoot">Finished frames land on each machine\'s courier branch, '
          'get checked, and show up as choices on the '
          '<a href="sapling/001-capability-inventory-shots.html">shot board</a> — '
          'the author (and anyone watching) picks what survives.</p>')

    # --- the same queue again, entry by entry: the record, not the account ---
    # Work that finished today is listed here BY ID, including ids the queue file
    # no longer holds. The promoter retires an entry the moment its DONE line
    # lands, so a record built only from the file would lose each job at exactly
    # the moment it succeeded — the same trap finished_line_story documents.
    if fin:
        fin_rows_rec = ""
        for when, who, tid, note in fin:
            entry = by_id.get(tid)
            gone = ("" if entry else ' <span class="qlist">· entry already retired '
                    'from the queue file</span>')
            fin_rows_rec += (
                '<li class="qrow"><div class="qtop">'
                '<span class="qchip done">✅ FINISHED TODAY</span>'
                f'<code class="qid">{_e(tid) or "(the line carries no id)"}</code>'
                '</div>'
                f'<div class="qwhat">{_e(finished_line_story(entry, note))}</div>'
                f'<div class="qwhy">{_e(who)} · finished {age_el(when, now)}{gone}</div>'
                '</li>')
        fin_record = (f'<div class="qgroup"><h3>✅ Finished today '
                      f'<span class="count">{len(fin)}</span></h3>'
                      '<p class="mono">Every DONE check-in line since midnight UTC, '
                      'by id. Read off the dated commit log, so "today" is a fact '
                      'and not an inference from a clock with no day attached.</p>'
                      f'<ol class="qlist-ol">{fin_rows_rec}</ol></div>')
    else:
        fin_record = ('<div class="qgroup"><h3>✅ Finished today '
                      '<span class="count">0</span></h3><p class="mono">No DONE '
                      'check-in line has landed since midnight UTC. A code or '
                      'writing task finishes by having its entry retired and never '
                      'writes a check-in line, so a day of that work still reads 0 '
                      'here.</p></div>')
    queue_record = (
        '<h2 id="queue">📋 The work queue, entry by entry</h2>'
        '<p style="margin:.2rem 0 .6rem;color:var(--muted)">The work list above is '
        'the readable account of this queue, and it merges repeats and leaves out '
        'the machine-facing detail on purpose. This is the record. Every entry in '
        '<code>pipeline/farm-queue.yaml</code> appears here exactly once under its '
        'own id, with every field it carries — including fields this page does not '
        'recognise — and every check-in line that claims it. Nothing is merged and '
        'nothing is summarised away, so you can read it against the file.</p>'
        f'<section class="qrec">'
        + queue_record_html(queue, backlog, records,
                            qdoc.get("dropped") or [], now)
        + fin_record
        + '</section>'
        + '<p class="whyfoot">The queue file is what the studio intends; the '
          'check-in lines are what happened. Where the two disagree the lines win, '
          'which is why an entry can sit in the file reading <b>DONE</b> — the '
          'promoter has not retired it yet. Read the file yourself: '
          f'<a href="https://github.com/{GH}/blob/main/pipeline/farm-queue.yaml">'
          'pipeline/farm-queue.yaml</a>.</p>')

    town_legend = " · ".join(STATE_WORDS[s] for s in STATE_WORDS if s in seen_states) \
        or "no machine has checked in yet"

    citizens = "".join(
        f'<div class="citizen"><a class="bubble" href="{_e(url)}">{_e(said)}</a>'
        f'<div class="spr">{"🧑‍🌾" if i % 2 else "🧙"}</div><small>{_e(who)}</small></div>'
        for i, (who, said, url) in enumerate(comments))
    if not citizens:
        citizens = '<p class="notice">The reactions thread is quiet right now.</p>'

    player = (f'<figure class="phone"><video controls playsinline preload="metadata" '
              f'poster="{_e(hero["poster"])}" src="{_e(hero["video"])}"></video>'
              f'<figcaption>Episode {hero["number"]} · “{_e(hero["title"])}” — '
              f'the working cut — {tot["final"]}/{tot["total"]} scene frames approved, '
              f'awaiting the author’s pass</figcaption></figure>'
              ) if hero["video"] else (
        f'<p><a class="btn" href="{_e(hero["watch"])}">▶ Watch episode {hero["number"]} &rarr;</a></p>')

    waiting = (f'{tot["awaiting_render"]} waiting on a render · '
               f'{tot["awaiting_pick"]} waiting on the author to pick')

    # --- vitals: four numbers, each one checkable against the repo ---
    vitals = (
        f'<div class="vitals">'
        f'<div class="vital"><b>{pct}%</b><small>episode grown</small></div>'
        f'<div class="vital"><b>{takes["stills"] + takes["clips"]}</b>'
        f'<small>takes handed in</small></div>'
        f'<div class="vital"><b>{open_quests}</b><small>open quests</small></div>'
        f'<div class="vital"><b>${spend:.2f}</b><small>spent, lifetime</small></div>'
        f'</div>')

    # --- milestones: unlocked = a repo fact, locked = the honest gap ---
    all_moving = all(r["animations"] for r in rows)
    vo = data.vo_scenes()
    passed = data.cut_passed()
    picking = next((r for r in rows if not r["final"]), None)
    milestones = [
        ("🌱", "Scripted", bool(rows),
         f'{tot["total"]} scenes written; the script approved by the author'),
        ("🖼", "Every frame approved", done,
         f'all {tot["total"]} scene frames carry the author\'s pick' if done else
         (f'{tot["final"]} of {tot["total"]} — scene {picking["num"]:02d} still choosing'
          if picking else f'{tot["final"]} of {tot["total"]}')),
        ("🔊", "Narration recorded", vo > 0,
         f"{vo} scenes carry recorded voice-over" if vo else "no voice lines recorded yet"),
        ("🎞", "Every scene moves", all_moving,
         "a moving take exists for all scenes" if all_moving else
         f'{sum(1 for r in rows if r["animations"])} of {tot["total"]} scenes have one'),
        ("🎬", "A full cut assembled", bool(hero["video"]),
         "playing at the top of this page" if hero["video"] else "no full cut yet"),
        ("🏆", "The author passes the cut", passed,
         "the cut is canon" if passed else
         "the last gate — only the author can open it"),
    ]

    out = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
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
<style>{THEME_CSS}{SIM_CSS}{TEL_CSS}</style>
</head>
<body>
<main>
<nav class="crumbs"><a href="index.html">🌳 banyan-city</a> · <a href="watch.html">▶ watch</a>
 · <a href="city.html">the city</a> · <a href="machine.html">⚙️ how it works</a>
 · <b>🏗 {PAGE_NAME}</b> · <a href="https://github.com/{GH}">source</a></nav>

<div class="rise">
<p class="eyebrow">Banyan City · {PAGE_NAME}</p>
<h1>{PAGE_NAME.title()}</h1>
<p class="lede">{data.PITCH}</p>
</div>

<div class="rise">
{player}
<p style="text-align:center">
  <a class="btn" href="{_e(hero["watch"])}">▶ Watch episode {hero["number"]}</a>
  <a class="btn ghost" href="{_e(hero["board"])}">🎬 See how it was made</a>
</p>
<p class="spend">total spent on renders so far: <b>${spend:.2f}</b> —
everything else runs on the family's own machines for free</p>
{infra_html}
{vitals}
</div>

<h2 class="rise">The episode, growing</h2>
<div class="grove rise">
  <div class="canopy">{leaves}</div>
  <div class="trunky"><a href="{_e(hero["page"])}" title="Episode {hero["number"]}">🌳</a></div>
  {growbar}
  <div class="label">{grove_caption}</div>
</div>

<h2>Milestones</h2>
{badges_html(milestones)}
<p class="legend">an unlocked milestone is a fact you can check in the repo ·
a locked one is exactly what remains</p>

<h2>The lot — the studio at work</h2>
{lot}
<ul class="machlist" id="machlist">{machlist}</ul>
<p class="legend">{town_legend}</p>
<p class="whyfoot">Two different files answer two different questions. A machine writes to
its check-in log only while a job is running, so silence there means “no job”, never “no
machine”; the render box also publishes its own temperature and memory every five minutes,
which is the only thing that can say a box is switched on. Where a machine can be seen but
cannot work, the reason below is the one its own queue entry records.</p>
{production}

{queue_record}

<h2>🏟 The render box, minute by minute</h2>
<section id="tel">
<p class="telnote" id="tel-note">no recent telemetry — these charts are drawn in your browser
from a file the render box publishes about itself every five minutes. If this line is still
here, that file has not been read yet (or JavaScript is off, in which case this page will not
guess what the machine is doing).</p>
<div id="tel-body" hidden></div>
</section>

<h2>🗺 Open quests — anyone can take one</h2>
<p style="margin:.2rem 0 .4rem;color:var(--muted)">Nothing here is play-pretend: every art
quest is a real open request from the author, and every take handed in becomes part of the
show's public record.</p>
{quest_board_html(rows)}
<p class="whyfoot">every quest lands on the
<a href="{_e(hero["board"])}">scene-by-scene shot board</a> — the whole workshop is public</p>

<h2>Every scene, and what it is waiting for</h2>
<p class="summary"><b>{tot["final"]} of {tot["total"]} scene frames approved</b> —
the assembled episode is a working cut until the author passes it · {waiting}</p>
<details class="drawer"><summary>Open the scene-by-scene list</summary>
<div class="drawer-body">{scene_list_html(rows)}</div></details>

<h2>How long each step takes (and what it costs)</h2>
{steps_table_html(data.STEPS)}

<h2>🕰 Waiting on the author</h2>
<p style="margin:.2rem 0 .4rem;color:var(--muted)">These are calls only the author can make —
taste, and what gets published. The rest of the city keeps moving while they wait, but the
jobs listed under each one cannot start until it is made, and the number in front of each is
how long it has been sitting there.</p>
{waiting_html(inbox, backlog, now)}

<h2>People on the reactions thread</h2>
<div class="citizens">{citizens}</div>
<p style="text-align:center"><a href="https://github.com/{GH}/issues/1">join them &rarr;</a></p>

<p class="legend">{data.LEGEND}</p>
<footer>This copy was built {now.strftime('%Y-%m-%d %H:%M')}Z ({age_el(now, now)}).
Nothing on this page is dated by that build: every age above counts from the moment its own
datum was recorded. This copy is rebuilt when something the page is built from changes — a
scene, a take, the work queue, the author's list, the spend. A push that only touches the
repo's own notes and logs does not rebuild it, on purpose: rebuilding on every push billed
over $100 of build time in a month and published nothing. So a build stamp older than the
newest commit is that rule working, not this page failing. The mirror copy also rebuilds
every half hour, so two copies of this page can differ — which is why the ages are
per-datum and not one snapshot stamp. Your browser re-reads the machines' check-in logs, the
render box's vitals and the work queue for itself, and keeps the ages counting while the tab
is open. The whole repo IS the show —
<a href="index.html">the city</a> · <a href="lab/index.html">the lab</a> ·
<a href="machine.html">how it works</a></footer>
</main>
<script>
/* pause every animation while the tab is hidden. */
document.addEventListener("visibilitychange", function () {{
  document.body.classList.toggle("away", document.hidden);
}});
var TEL_URL = {json.dumps(TELEMETRY_URL)}, TEL_STALE = {TELEMETRY_STALE_MINUTES};
var RAW_BASE = {json.dumps(RAW)}, QUEUE_URL = {json.dumps(QUEUE_URL)};
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
{TEL_JS}
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
          f"{len(seen_states)} machines")


if __name__ == "__main__":
    build(REPO / "_site")
