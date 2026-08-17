#!/usr/bin/env python3
"""Local screening QA gate.

Run this BEFORE handing any local URL to the founder. It builds every
generator that contributes to `_site/`, then sweeps every route the built
site actually exposes and content-checks the load-bearing pages.

Route set mirrors production (`vercel.json`: cleanUrls=true, trailingSlash=false),
so a page that only works as `/name.html` locally but is linked as `/name`
is a failure, not a pass.

Exit 0 with a green table, or nonzero with a per-route failure table.
Last line is machine-parseable:  QA-GATE: PASS routes=N | QA-GATE: FAIL failures=K

    python3 pipeline/qa_local.py                 # build + sweep
    python3 pipeline/qa_local.py --no-build      # sweep only (fast)
    python3 pipeline/qa_local.py --base http://127.0.0.1:8788
"""

import argparse
import email.utils
import html
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(REPO, "_site")
DEFAULT_BASE = "http://127.0.0.1:8787"

# The public surfaces. The mirror is not a fallback nicety — it is the control
# in the freshness experiment below, since it builds from the same repo by a
# different mechanism.
PUBLIC_BASE = "https://banyan.city"
PUBLIC_PROBE = "/status"
# Owner-dependent: the repo moved olegmlkvorg -> olegmalk on 2026-08-10, and the
# Pages URL moved with it. `olegmlkvorg.github.io/banyan-city/` now 404s, so a
# hardcoded old owner would make the control look "down" and quietly disable the
# cross-check. Derived from the git remote (which GitHub redirects, so the remote
# itself can still read old) with the API's answer as the source of truth.
MIRROR_BASE = "https://olegmalk.github.io/banyan-city"
MIRROR_PROBE = "/status.html"

# How far the public site may trail HEAD before we call it. Deliberately loose:
# a real deploy lands in ~1-2 minutes, and docs-only pushes are skipped on
# purpose, so anything under half an hour is normal. Three hours is not.
PUBLIC_STALE_WARN_S = 30 * 60
PUBLIC_STALE_FAIL_S = 3 * 60 * 60

# The screening server lives in the repo so the next session can find it. It is
# the only one whose path resolution matches production — see its docstring.
REPO_SERVER_REL = "pipeline/serve_local.py"
REPO_SERVER = os.path.join(REPO, REPO_SERVER_REL)

# Builders that contribute to _site/, in dependency order. build_site.py lays
# down the tree; the others write pages into it and must run after.
BUILDERS = ["build_site.py", "build_sim.py", "build_pulse.py", "build_queue.py"]

# Every page must clear this. Redirect stubs (sim.html) are legitimately tiny.
DEFAULT_MIN_BYTES = 200
LOAD_BEARING_MIN_BYTES = 5000

# Pages the founder is actually handed. Keyed by clean route.
#   min_bytes: floor for "this rendered something real"
#   any_of:    at least one must appear — a list, not a single string, so a
#              sibling lane renaming one heading does not red the gate
LOAD_BEARING = {
    "/": {"min_bytes": LOAD_BEARING_MIN_BYTES},
    "/status": {
        "min_bytes": LOAD_BEARING_MIN_BYTES,
        "any_of": [
            "The work list",
            "work queue",
            "Open quests",
            "Every scene",
            "The lot",
        ],
        "any_of_label": "work-queue/scene marker",
    },
    "/pulse": {"min_bytes": LOAD_BEARING_MIN_BYTES, "all_of": ["<svg"]},
    # /queue is the founder's answer to "why does this beat look like that": if
    # the prompts are not in the bytes the page is decoration. `raw.
    # githubusercontent.com` is checked too, because a history that lost its
    # media base would render 600 cards with no frames in them and still be big.
    "/queue": {
        "min_bytes": LOAD_BEARING_MIN_BYTES,
        "all_of": ["Positive prompt", "raw.githubusercontent.com"],
    },
    "/city": {"min_bytes": LOAD_BEARING_MIN_BYTES},
    "/create": {"min_bytes": LOAD_BEARING_MIN_BYTES},
    "/watch": {"min_bytes": LOAD_BEARING_MIN_BYTES},
    "/review": {"min_bytes": LOAD_BEARING_MIN_BYTES},
}

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
DIRLIST_MARKER = "Directory listing for"

# A directory listing on a clean route means the screening server resolved
# `/x` to the directory `x/` instead of to `x.html`. Vercel (cleanUrls) does the
# opposite, so this is the local server drifting from production, not a site
# bug — but the founder opening that URL still gets a file listing, so it fails.
# The fix belongs in serve_local.py, and the gate carries it rather than making
# whoever hits this rediscover it.
DIRLIST_NOTE = "served a DIRECTORY LISTING, not the page"
DIRLIST_REMEDY = """The server resolved /x to the directory x/ instead of to x.html. Production
(vercel.json: cleanUrls=true) resolves it the other way, so THE SERVER IS WRONG
AND THE SITE IS FINE — banyan.city does not have this bug and must not be
"fixed" for it. Restart the server named above using the repo's own, which gets
the order right:

    python3 %s _site <port>

Editing a file is not enough: a running process holds the code it started with.
""" % REPO_SERVER_REL


# ---------------------------------------------------------------- utilities


def read_text(path):
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8", "replace")


def _run(argv):
    try:
        return subprocess.run(
            argv, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        ).stdout.decode("utf-8", "replace")
    except Exception:
        return ""


def uncommitted(rel_path):
    """Does this path differ from HEAD? Several lanes edit this tree at once, so a
    builder that fails is more often someone mid-save than a bug — and the answer
    changes the advice from "fix it" to "wait and re-run"."""
    return bool(_run(["git", "-C", REPO, "status", "--porcelain", "--", rel_path]).strip())


def title_of(path):
    """The <title> of a built file, normalised. This is the expected marker for
    whatever route that file backs — derived at runtime, so it never goes stale."""
    m = TITLE_RE.search(read_text(path))
    if not m:
        return None
    return html.unescape(" ".join(m.group(1).split()))


def canonical(route):
    """The clean form a route's content spec is keyed under: /x.html and /x/ both
    serve the same file as /x, so they answer to the same content requirements."""
    r = route.rstrip("/") or "/"
    if r.endswith(".html"):
        r = r[: -len(".html")]
    return r or "/"


def c(code, s):
    return s if not sys.stdout.isatty() else "\033[%sm%s\033[0m" % (code, s)


green = lambda s: c("32", s)
red = lambda s: c("31", s)
yellow = lambda s: c("33", s)
bold = lambda s: c("1", s)


def die(msg, code=2):
    print()
    print(red("QA GATE FAILED"))
    print(msg)
    print()
    print("QA-GATE: FAIL failures=1")
    sys.exit(code)


# ------------------------------------------------------------------- builds


def run_builders():
    missing = [b for b in BUILDERS if not os.path.isfile(os.path.join(REPO, "pipeline", b))]
    if missing:
        die(
            "Builder(s) not found: %s\n"
            "Expected under %s/pipeline/.\n"
            "A builder listed in qa_local.BUILDERS must exist; if one was renamed or\n"
            "removed, update BUILDERS in pipeline/qa_local.py to match."
            % (", ".join(missing), REPO)
        )

    # Refresh the laptop's free-space reading before the builders run, so the
    # /status disk tile is current in whatever gets screened. It is a `df` and a
    # directory tally — no ssh, no hashing, well under a second — and it is
    # wrapped because a disk reading must never be able to fail the gate. The
    # tile exists because on 2026-08-11 this disk fell 19 -> 9.6 GiB in two
    # hours and the only thing that noticed was a supervisor tick; a tile that
    # only refreshes when someone remembers to refresh it would repeat that.
    try:
        subprocess.run(
            [sys.executable, os.path.join("pipeline", "box_cache.py"), "disk"],
            cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=60,
        )
    except Exception:
        pass

    print(bold("Building (%d generators)" % len(BUILDERS)))
    for b in BUILDERS:
        proc = subprocess.run(
            [sys.executable, os.path.join("pipeline", b)],
            cwd=REPO,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        out = proc.stdout.decode("utf-8", "replace")
        if proc.returncode != 0:
            tail = "\n".join(out.rstrip().splitlines()[-25:])
            rel = "pipeline/" + b
            # A dirty builder in a shared tree is a lane mid-save far more often
            # than a bug. Saying so here is what stops the next reader "fixing" it
            # by reverting, which throws away work that was never broken.
            live = (
                "\n%s HAS UNCOMMITTED CHANGES — most likely a lane is mid-edit.\n"
                "RE-RUN before touching it, and do NOT revert it to HEAD to go green:\n"
                "that destroys in-flight work.\n" % rel
                if uncommitted(rel)
                else ""
            )
            die(
                "Builder failed: %s (exit %d)\n"
                "\nTHIS IS A WORKING-TREE RESULT AND SAYS NOTHING ABOUT PRODUCTION.\n"
                "A broken working copy here does not mean the site is down. 'The build\n"
                "is down' and 'the site is down' are different sentences — and so is\n"
                "'the site is up but frozen', which is what the PUBLIC DEPLOY FRESHNESS\n"
                "section exists to catch. Do not read this failure as either.\n"
                "%s\n"
                "Nothing was screened. If build_site.py was the one that died it wipes\n"
                "_site/ before rebuilding, so this tree may now hold a PARTIAL site that\n"
                "other lanes are screening against — re-run once it builds.\n"
                "\n--- tail of %s output ---\n%s"
                % (rel, proc.returncode, live, rel, tail)
            )
        print("  %s pipeline/%-16s rc=0" % (green("ok"), b))
    print()


# ------------------------------------------------------------------- routes


def discover_routes():
    """Enumerate routes from _site/ itself, mirroring Vercel's cleanUrls.

    Returns [(route, backing_file)] — the backing file is what the route is
    *supposed* to serve, which is how directory-shadowing gets caught."""
    if not os.path.isdir(SITE):
        die(
            "_site/ does not exist at %s\n"
            "Run the gate without --no-build, or: python3 pipeline/build_site.py" % SITE
        )

    routes = []
    seen = set()

    def add(route, backing):
        if route not in seen:
            seen.add(route)
            routes.append((route, backing))

    root_index = os.path.join(SITE, "index.html")
    if os.path.isfile(root_index):
        add("/", root_index)

    for name in sorted(os.listdir(SITE)):
        path = os.path.join(SITE, name)
        if os.path.isfile(path) and name.endswith(".html") and name != "index.html":
            stem = name[: -len(".html")]
            add("/" + stem, path)  # clean URL (what production serves)
            add("/" + name, path)  # explicit .html (what internal links use)

    # Directories that publish an index.html are routes in both forms:
    # trailingSlash=false means production serves /dir, the local server 301s to /dir/.
    for dirpath, dirnames, filenames in os.walk(SITE):
        dirnames[:] = [d for d in sorted(dirnames) if not d.startswith(".")]
        if dirpath == SITE or "index.html" not in filenames:
            continue
        rel = os.path.relpath(dirpath, SITE).replace(os.sep, "/")
        backing = os.path.join(dirpath, "index.html")
        add("/" + rel, backing)
        add("/" + rel + "/", backing)

    return routes


# -------------------------------------------------------------------- fetch


class _Recorder(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.hops = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.hops.append((code, newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(base, route):
    """GET following redirects. -> (status, body, final_url, hops)"""
    rec = _Recorder()
    opener = urllib.request.build_opener(rec)
    url = base.rstrip("/") + route
    try:
        with opener.open(url, timeout=20) as resp:
            body = resp.read().decode("utf-8", "replace")
            return resp.getcode(), body, resp.geturl(), rec.hops
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace"), url, rec.hops


def listening_cmd(base):
    """Command line of whatever is actually listening on `base`'s port.

    Asked by PID rather than by scanning for a name: several servers can be up at
    once, and a failure that names the wrong one sends the reader to patch a file
    that is not serving them. It also catches the case that matters most — the
    thing on the port is not the server anyone thinks it is."""
    port = urllib.parse.urlsplit(base).port
    if not port:
        return None
    pids = _run(["lsof", "-nP", "-iTCP:%d" % port, "-sTCP:LISTEN", "-t"]).split()
    if not pids:
        return None
    return _run(["ps", "-p", pids[0], "-o", "command="]).strip() or None


def screening_servers():
    """(port, command) for every listening process that is a serve_local.py.

    Found by asking who holds a listening socket, not by grepping ps for the
    filename: the gate's own shell command line can contain "serve_local.py" and
    match itself, which silently turned a one-server machine into an ambiguous
    two-candidate scan and suppressed the diagnosis."""
    out = []
    for line in _run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"]).splitlines()[1:]:
        parts = line.split()
        if len(parts) < 9:
            continue
        cmd = _run(["ps", "-p", parts[1], "-o", "command="]).strip()
        if "serve_local.py" in cmd:
            out.append((parts[8].rsplit(":", 1)[-1], cmd))
    return out


def running_server_cmd(base=None):
    """The server behind `base` if one is listening there, else a lone screening
    server on some other port — which makes "it is up, just not where you looked"
    a diagnosis instead of a guess."""
    if base:
        cmd = listening_cmd(base)
        if cmd:
            return cmd
    others = screening_servers()
    return others[0][1] if len(others) == 1 else None


def start_command(base):
    """How to (re)start the screening server, always naming the REPO copy. A
    scratchpad server dies with its session and cannot be found or fixed by the
    next one, which is how the /watch resolution bug survived."""
    if not os.path.isfile(REPO_SERVER):
        return None
    port = urllib.parse.urlsplit(base).port or 8787
    return "python3 %s _site %d &" % (REPO_SERVER_REL, port)


def server_start_hint(base):
    """The exact command to bring the screening server back up."""
    start = start_command(base)
    start_block = ("Start it with:\n    %s" % start) if start else None
    others = screening_servers()
    if others:
        where = "\n".join("    port %s — %s" % (p, c) for p, c in others)
        msg = (
            "Nothing is answering %s, but a screening server IS up elsewhere:\n%s\n"
            "Point --base at that port, or start one here." % (base, where)
        )
        return (msg + "\n" + start_block) if start_block else msg
    if start_block:
        return start_block
    return (
        "%s is missing. Any static server with Vercel-style clean URLs will do,\n"
        "e.g.:\n    python3 -m http.server 8787 --directory %s &\n"
        "(note: the stock http.server has no clean URLs, which is what 404'd before)"
        % (REPO_SERVER_REL, SITE)
    )


# --------------------------------------------------------------- shadowing


def shadowed_routes():
    """Clean routes that two different files could answer: `<name>.html` and a
    directory `<name>/`. Production resolves these to the .html; a server that
    resolves to the directory serves a file listing instead of the page. Reported
    even when the current server gets it right, because the collision is the
    hazard — /watch was one of these and nobody knew until the founder saw it."""
    out = []
    if not os.path.isdir(SITE):
        return out
    for name in sorted(os.listdir(SITE)):
        if not name.endswith(".html") or name == "index.html":
            continue
        stem = name[: -len(".html")]
        d = os.path.join(SITE, stem)
        if os.path.isdir(d):
            out.append((stem, os.path.isfile(os.path.join(d, "index.html"))))
    return out


def unpaged_warning(repo=REPO, recent_hours=12.0):
    """Lines about finished renders that reach no page he can open, or [].

    Separate from the route sweep on purpose. Every route can be green and the
    site still be missing the four things he has been asking for — that is not
    a hypothetical, it is what he reported on 2026-08-13 and again on 08-14, and
    the guard is `pipeline/unpaged.py`. Two numbers rather than one: the whole
    standing backlog, which moves slowly, and the last `recent_hours`, which is
    the slice a supervisor's own pass is answerable for and the one that should
    be zero when they hand the URL over.

    Wrapped, and returns [] on anything unexpected: this is a warning about
    completeness, and a warning that can fail the gate would stop good pages
    reaching him to complain about a bad one.
    """
    try:
        import unpaged
        r = unpaged.survey(repo)
    except Exception:
        return []
    if not r.get("measurable") or not r["unpaged"]:
        return []
    rows = r["unpaged"]
    recent = [x for x in rows if x["age_hours"] <= recent_hours]
    out = [bold("RENDERED FOR HIM AND NEVER SHOWN (%d)" % len(rows))]
    for x in (recent or rows)[:8]:
        out.append("  %s %-44s %s old, %d file(s)"
                   % (yellow("warn"), x["task"], unpaged.ago(x["age_hours"]),
                      x["artifacts"]))
    if recent:
        out.append("  %d of these finished in the last %g h — if your pass "
                   "rendered one, page it before handing over this URL."
                   % (len(recent), recent_hours))
    else:
        out.append("  None in the last %g h; the oldest is %s. Backlog, not "
                   "this pass." % (recent_hours, unpaged.ago(rows[0]["age_hours"])))
    out.append("  Not a failure — a wave still being written up counts here too. "
               "Full list: python3 pipeline/unpaged.py")
    out.append("")
    return out


# ------------------------------------------------------- pages that never ran


def tracked_in_git(rel):
    """Does the tree carry this path? A file the deploy will not have is not
    published, however well it renders on the laptop that wrote it."""
    return bool(_run(["git", "-C", REPO, "ls-files", "--", rel]).strip())


def unpublished_review_pages(repo=REPO, site=SITE, is_tracked=None):
    """Review pages that exist in the repo and NOT in the built site.

    THE HOLE THIS CLOSES, measured 2026-08-10. A lane wrote a 131 KB approvals
    page to `review/approvals/index.html`, the founder asked for it, and the URL
    404'd — `build_site.py` published no such route. Every gate in this file
    passed while it did, and they were structurally incapable of doing anything
    else: the sweep enumerates `_site/`, and the build's own link check walks
    `_site/`, so a page that was never copied there is not a failing route, it
    is not a route. **Absence was invisible because everything only ever looked
    at the output.** This is the one check that starts from the repo instead.

    Two distinct failures wear the same 404, and the remedy is different, so the
    reason is carried rather than flattened:

      `unpublished` — tracked, and the builder did not emit it. A publishing
        rule is missing (see build_site.review_page_dirs).
      `untracked`  — the builder deliberately skips it, because git is what CI
        clones and what the deploy serves. Committing it is the whole fix; it is
        also why this cannot be downgraded to a warning, since the local tree is
        precisely where this one looks fine.

    -> [(rel, reason)], empty when every review page in the repo is on the site.
    """
    if is_tracked is None:
        is_tracked = tracked_in_git
    root = os.path.join(repo, "review")
    if not os.path.isdir(root):
        return []
    gaps = []
    for name in sorted(os.listdir(root)):
        if name.startswith("."):
            continue
        rel = "review/%s/index.html" % name
        if not os.path.isfile(os.path.join(root, name, "index.html")):
            continue
        if os.path.isfile(os.path.join(site, "review", name, "index.html")):
            continue
        gaps.append((rel, "unpublished" if is_tracked(rel) else "untracked"))
    return gaps


REVIEW_GAP_REMEDY = {
    "unpublished": (
        "tracked, but build_site.py wrote no _site/%s.\n"
        "       The builder needs a rule that publishes it — review_page_dirs()\n"
        "       in build_site.py picks up review/<name>/index.html."
    ),
    "untracked": (
        "NOT IN GIT, so the build skipped it and the deploy will not have it.\n"
        "       git commit -- %s"
    ),
}


# ------------------------------------------------------------------- checks


def check_route(base, route, backing):
    """-> (ok, note). note explains the failure, or summarises what passed."""
    try:
        status, body, final, hops = fetch(base, route)
    except (urllib.error.URLError, OSError) as e:
        raise ConnectionError(str(e))

    if status != 200:
        return False, "HTTP %d (final %s)" % (status, final)

    size = len(body.encode("utf-8", "replace"))
    spec = LOAD_BEARING.get(canonical(route), {})
    floor = spec.get("min_bytes", DEFAULT_MIN_BYTES)

    if DIRLIST_MARKER in body:
        shadow = os.path.relpath(os.path.join(SITE, route.strip("/")), REPO)
        return False, (
            "%s — %s/ shadows %s. Production (cleanUrls) serves the .html; "
            "this server prefers the dir." % (DIRLIST_NOTE, shadow, os.path.relpath(backing, REPO))
        )

    if size < floor:
        return False, "only %d bytes (floor %d) — page rendered empty or truncated" % (size, floor)

    want = title_of(backing)
    # BOTH SIDES UNESCAPED, or the comparison is between two spellings of the
    # same string. title_of() unescapes what it reads off disk, and this used to
    # search for the result inside the RAW body — so a title written
    # `yes &mdash; banyan.city` could never contain `yes — banyan.city`, and the
    # failure printed the two as identical text (2026-08-10, /review/approvals).
    # Every page page() emits escapes with html.escape, which touches only &<>",
    # so no generated title had ever carried an entity and the flaw sat unseen
    # until a hand-authored page arrived. Substring, not equality, deliberately:
    # that is the rule these routes already pass under, and tightening it is a
    # different change from making it read what is on the page.
    if want and want not in html.unescape(" ".join(body.split())):
        got = TITLE_RE.search(body)
        got = html.unescape(" ".join(got.group(1).split())) if got else "<no title>"
        return False, "wrong page: expected title %r (from %s), served %r" % (
            want,
            os.path.relpath(backing, REPO),
            got,
        )

    for needle in spec.get("all_of", []):
        if needle not in body:
            return False, "missing required marker %r" % needle

    any_of = spec.get("any_of")
    if any_of and not any(n in body for n in any_of):
        return False, "no %s found (looked for any of: %s)" % (
            spec.get("any_of_label", "marker"),
            ", ".join(repr(n) for n in any_of),
        )

    note = "%d bytes" % size
    if hops:
        note += ", %d redirect" % len(hops) + ("s" if len(hops) > 1 else "")
    return True, note


# --------------------------------------------------------------------- main


# --------------------------------------------------------- public freshness


def http_head(url):
    """HEAD following redirects. -> (status, headers) or (None, reason-string)."""
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.getcode(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {})
    except Exception as e:  # DNS, TLS, no route — unreachable, not "stale"
        return None, "%s: %s" % (type(e).__name__, e)


def header(headers, name):
    """Case-insensitive header lookup — urllib hands back `Last-Modified`, and a
    plain .get("last-modified") silently misses it."""
    for k, v in (headers or {}).items():
        if k.lower() == name.lower():
            return v
    return None


def http_date(headers, name="last-modified"):
    raw = header(headers, name)
    if not raw:
        return None
    try:
        return email.utils.parsedate_to_datetime(raw).timestamp()
    except Exception:
        return None


def head_commit_epoch():
    out = _run(["git", "-C", REPO, "log", "-1", "--format=%ct"]).strip()
    return int(out) if out.isdigit() else None


def origin_commit_epoch():
    """Commit time of `origin/main` — the newest commit the DEPLOY can see.

    THE BUG THIS FIXES, measured 2026-08-17. This section compared the live
    site against LOCAL HEAD and called an 8.5-hour gap a stuck deploy, then
    told the reader "pushing again will not fix it; publish with REPO-MOVE.md
    A0." Every part of that was wrong. banyan.city had built at 10:16:32Z from
    `origin/main` tip 145a02d5, committed 10:14:57Z — a 95-second deploy, i.e.
    working perfectly. The gap was 185 commits sitting on this machine that
    nobody had pushed, deliberately, waiting on the founder.

    A deploy cannot be late for a commit it has never been given. Measuring it
    against HEAD makes the gate fail by construction whenever work is held, and
    a gate that cries wolf on a healthy deploy is one a tired reader learns to
    skip — then misses the real one. Local ref, no fetch: a network call inside
    the gate is a hang waiting to happen, and a stale `origin/main` can only
    make this check more conservative, never less.
    """
    out = _run(["git", "-C", REPO, "log", "-1", "--format=%ct", "origin/main"]).strip()
    return int(out) if out.isdigit() else None


def mirror_says_stuck(drift_s, primary_lag_s, fail_s):
    """Is a newer mirror evidence of a STUCK primary? Pure, so it is testable.

    TWO CONDITIONS, and the second is the one this gate was missing. A mirror
    newer than the primary is normal: `pages.yml` carries
    `schedule: cron "*/30 * * * *"`, so the mirror restamps itself every half
    hour from the SAME commit, while Vercel only builds on push. On any day
    without a push the mirror is newer by however long it has been.

    It is evidence of a stuck deploy ONLY when the primary is also behind what
    was actually pushed. Both must hold.
    """
    return drift_s > fail_s and primary_lag_s > fail_s


def commits_held_locally():
    """Commits on HEAD that are not on `origin/main`, or None if unknowable.

    Not a failure and never counted as one. It is the difference between "the
    deploy is broken" and "we have not pushed yet", which are opposite problems
    with opposite fixes, and the gate said the first when it meant the second.
    """
    out = _run(["git", "-C", REPO, "rev-list", "--count", "origin/main..HEAD"]).strip()
    return int(out) if out.isdigit() else None


def head_short_sha():
    return _run(["git", "-C", REPO, "rev-parse", "--short=7", "HEAD"]).strip()


def commits_behind(sha):
    """How many commits HEAD has that the deployed commit does not.

    None when this checkout has never heard of `sha` — which is a real and
    different answer from "zero": the deploy may be from a branch we do not
    have, or from a push we have not fetched. Calling that "current" is the
    class of mistake this whole section exists to stop, so it stays None and
    the verdict says so out loud."""
    if not sha:
        return None
    out = _run(["git", "-C", REPO, "rev-list", "--count", "%s..HEAD" % sha]).strip()
    return int(out) if out.isdigit() else None


# How close `last-modified` must sit to the cache-fill instant before we call it
# a restatement of that instant rather than a build clock. Two seconds absorbs
# clock skew and the round trip without admitting a real build timestamp.
FILL_CLOCK_EPSILON_S = 2


def is_cache_fill_clock(headers):
    """Is this `last-modified` just the moment the CDN edge filled its cache?

    WHY THIS EXISTS — it invalidates the check it guards. Vercel sets
    `last-modified` on a static asset to the instant the edge fetched it from
    origin, NOT to the time the site was built. Measured 2026-08-10 against
    banyan.city: `/city` and `/machine`, both cold (`x-vercel-cache: MISS`,
    `age: 0`), each returned `last-modified` equal to their own `date` header to
    the second. On a later HIT the value froze at that fill instant while `age`
    counted up from it.

    So `head_commit_epoch() - last_modified` is not "how far production trails
    HEAD" — it is "how long ago some edge happened to refill", which is always
    seconds. A build frozen for a day still reports `0s behind HEAD` the moment
    anyone loads a cold page. Both signals in check_public_freshness() read this
    header, so both were structurally incapable of firing: the lag never went
    positive, and the mirror drift never did either, because the mirror's
    `last-modified` IS a real build time and so is always the *older* of the two.
    During the 15.8-hour freeze this section was written to catch, it would have
    printed a green `ok`.

    The test does not depend on cache state, which is what makes it usable:
    `date - age` is the fill instant in both directions, so a header that merely
    restates it lands within epsilon whether the response was a MISS or a HIT.
    GitHub Pages, by contrast, publishes a genuine build time — the mirror
    measured 7m43s older than its own fill instant — so the control still reads
    as trustworthy and the cross-check keeps its meaning on that side.

    A blind signal must announce that it is blind. Returning True here buys a
    warn, never a pass; see check_public_freshness()."""
    lm = http_date(headers)
    served = http_date(headers, "date")
    if lm is None or served is None:
        return False
    try:
        age = float((header(headers, "age") or "0").strip())
    except ValueError:
        age = 0.0
    return abs(lm - (served - age)) <= FILL_CLOCK_EPSILON_S


BUILT_RE = re.compile(r'data-built="(\d{9,11})"')
COMMIT_RE = re.compile(r'<meta[^>]+name="build-commit"[^>]+content="([^"]*)"', re.I)
COMMIT_TIME_RE = re.compile(r'<meta[^>]+name="build-commit-time"[^>]+content="([^"]*)"', re.I)
STAMP_SHA_RE = re.compile(r"^([0-9a-f]{7,40})(-dirty)?$")


def probe_body(base, probe):
    """The HTML of a probe page, or None if it could not be read as a 200.

    One GET, because two facts now come out of the same bytes — the
    `data-built` clock and the `build-commit` stamp — and fetching twice could
    land on two different edges holding two different builds, which would make
    the two signals describe different pages while looking like they agreed."""
    try:
        status, body, _, _ = fetch(base, probe)
    except Exception:
        return None
    return body if status == 200 else None


def parse_commit_stamp(body):
    """Which commit the deployed page says it was built from.

    -> {"state", "sha", "dirty", "commit_time"}. `state` is the whole point:

      unreadable — the page could not be fetched. We know nothing.
      absent     — no `build-commit` meta at all. This deploy PREDATES the
                   stamp (see build_commit.py), which is exactly the shape of
                   the 2026-08-10 freeze. It is not evidence of anything.
      unknown    — the builder wrote `unknown`: it ran, but could not see git.
                   Kept separate from `absent` because they have different
                   causes and different fixes — one is an old deploy, the other
                   is a build environment that cannot read its own checkout.
      malformed  — a value that is neither. Something is writing this tag
                   wrongly, and pretending to parse it would be worse.
      present    — a real sha, possibly `-dirty`.

    NONE OF THE FIRST FOUR MAY READ AS "CURRENT". That is the entire reason
    this returns a state rather than an optional sha: an optional sha invites
    `if sha and sha != head`, and every one of these cases falls through such a
    test into silence — which is how a blind check becomes a falsely green one,
    a strictly worse thing than the blind check it replaced."""
    if body is None:
        return {"state": "unreadable", "sha": "", "dirty": False, "commit_time": None}
    m = COMMIT_RE.search(body)
    if not m:
        return {"state": "absent", "sha": "", "dirty": False, "commit_time": None}
    raw = m.group(1).strip().lower()
    if raw == "unknown":
        return {"state": "unknown", "sha": "", "dirty": False, "commit_time": None}
    sm = STAMP_SHA_RE.match(raw)
    if not sm:
        return {"state": "malformed", "sha": raw, "dirty": False, "commit_time": None}
    tm = COMMIT_TIME_RE.search(body)
    ct = tm.group(1).strip() if tm else ""
    return {
        "state": "present",
        "sha": sm.group(1),
        "dirty": bool(sm.group(2)),
        "commit_time": int(ct) if ct.isdigit() else None,
    }


def commit_verdict(stamp, head_sha, behind=None):
    """-> ("ok"|"warn", one line saying WHICH of current / stale / unknown).

    Never returns a failure level, deliberately. Being a few commits behind is
    normal here — a docs-only push is CANCELED on purpose — so the failing
    judgement stays with the lag check below, which owns one threshold and one
    failure between them. This line's job is to say which state we are in and
    to make "unknown" unmistakable, not to add a second red for one fact."""
    if stamp["state"] == "unreadable":
        return "warn", ("UNKNOWN — could not read the deployed page to look for a "
                        "build-commit stamp")
    if stamp["state"] == "absent":
        return "warn", ("UNKNOWN — the page carries NO build-commit stamp, so it "
                        "predates the stamp (or was built by something that does not "
                        "write one). This is not evidence that it is current.")
    if stamp["state"] == "unknown":
        return "warn", ("UNKNOWN — the build stamped `unknown`: it ran but could not "
                        "read its own commit. Not the same as current.")
    if stamp["state"] == "malformed":
        return "warn", ("UNKNOWN — malformed build-commit %r. Something is writing "
                        "the stamp wrongly; fix build_commit.py rather than trusting "
                        "this." % stamp["sha"])
    if stamp["dirty"]:
        return "warn", ("built from an UNCOMMITTED tree at %s-dirty — its bytes were "
                        "never in git, so it matches no commit and cannot be called "
                        "current." % stamp["sha"])
    if head_sha and (stamp["sha"].startswith(head_sha) or head_sha.startswith(stamp["sha"])):
        return "ok", "CURRENT — built from HEAD %s" % stamp["sha"]
    if behind is None:
        return "warn", ("UNKNOWN — built from %s, a commit this checkout does not "
                        "have. Fetch, or it is a deploy of another branch." % stamp["sha"])
    if behind == 0:
        return "warn", ("built from %s, which is AHEAD of this checkout's HEAD %s — "
                        "someone pushed and this tree has not caught up."
                        % (stamp["sha"], head_sha))
    return "warn", ("STALE — built from %s, %d commit%s behind HEAD %s"
                    % (stamp["sha"], behind, "" if behind == 1 else "s", head_sha))


def build_stamp(body):
    """The page's own build time from its HTML, or None if it carries none.

    THIS IS THE CLOCK THE HEADER COULD NOT BE. `last-modified` on Vercel is the
    edge's cache-fill instant (see is_cache_fill_clock), which is why both
    signals below were blind. But the status page already publishes the real
    thing and has all along: `build_sim.py` stamps `data-built="<epoch>"` on
    every entry as it writes them. That is a fact about the BUILD, baked into
    the bytes, so no amount of CDN caching can move it — a page frozen for a day
    reports the day-old stamp no matter which edge serves it or when.

    It also repairs the cross-check. Comparing a cache-fill instant against the
    mirror's genuine build time made the drift permanently negative; comparing
    two build stamps compares like with like, so "the mirror rebuilt and the
    primary did not" means what it says again.

    Newest wins: the page holds one stamp per entry and a build only moves
    forward, so max() is the build that produced this page. Returning None is
    the honest answer when the page has no stamp, and the caller falls back to
    announcing that it is blind rather than passing."""
    stamps = [int(s) for s in BUILT_RE.findall(body or "")]
    return max(stamps) if stamps else None


def _ago(seconds):
    if seconds < 90:
        return "%ds" % int(seconds)
    if seconds < 5400:
        return "%.0fm" % (seconds / 60.0)
    return "%.1fh" % (seconds / 3600.0)


def check_public_freshness():
    """Is the PUBLIC site actually serving current work?

    WHY THIS EXISTS. On 2026-08-10 banyan.city served HTTP 200 for ~16 hours
    while frozen at the previous evening's build: the Vercel project had been
    disconnected from the repo, so pushes produced no deploy. Every check we
    had passed the whole time, because a stuck deploy does not go down — it
    keeps serving a correct page from the past. `200 OK` is evidence the CDN
    is up, and evidence of nothing else.

    Three independent signals, because any one alone can lie:

      0. WHICH COMMIT — the deployed page states the commit it was built from
         (`<meta name="build-commit">`, see build_commit.py). This is the only
         exact one: current, stale-by-N-commits, or UNKNOWN, and unknown is
         printed as unknown. It carries no threshold and cannot be moved by a
         cache, because it is a fact in the bytes rather than a clock.
      1. LAG vs HEAD — the deployed page's `last-modified` against the newest
         commit. Generous threshold: a docs-only push is deliberately CANCELED
         (see pipeline/vercel-ignore-build.sh), so a small lag is correct
         behaviour and must not red the gate. Hours of lag is not.
      2. MIRROR CROSS-CHECK — the GitHub Pages mirror builds from the same
         repo by a different mechanism. If the mirror rebuilt and the primary
         did not, the primary's pipeline is stuck no matter what HEAD's
         timestamp says. This is the signal that actually catches a
         disconnected git integration, and it needs no threshold tuning.

    Unreachable is a WARN, not a FAIL: a laptop offline mid-flight must not
    red a local screening run. A non-200 from a reachable host IS a FAIL.
    Returns a list of failure strings (empty = pass)."""
    failures = []
    print(bold("PUBLIC DEPLOY FRESHNESS"))

    head_ct = head_commit_epoch()
    pub_status, pub_headers = http_head(PUBLIC_BASE + PUBLIC_PROBE)
    mir_status, mir_headers = http_head(MIRROR_BASE + MIRROR_PROBE)

    if pub_status is None:
        print("  %s %-10s unreachable (%s) — cannot judge freshness"
              % (yellow("warn"), "primary", pub_headers))
        print("  %s the founder may still be able to reach it; this box may not be online.\n"
              % yellow("    "))
        return failures

    if pub_status != 200:
        failures.append("%s%s returned HTTP %s" % (PUBLIC_BASE, PUBLIC_PROBE, pub_status))
        print("  %s %-10s HTTP %s" % (red("FAIL"), "primary", pub_status))
        print()
        return failures

    pub_lm = http_date(pub_headers)
    print("  %s %-10s HTTP 200  last-modified=%s"
          % (green(" ok "), "primary", header(pub_headers, "last-modified") or "(none)"))

    # Both in-page facts come out of one GET each; see probe_body.
    pub_body = probe_body(PUBLIC_BASE, PUBLIC_PROBE)
    mir_body = probe_body(MIRROR_BASE, MIRROR_PROBE) if mir_status == 200 else None
    pub_built = build_stamp(pub_body)
    mir_built = build_stamp(mir_body)

    # WHICH COMMIT IS DEPLOYED — asked first, and asked before any clock,
    # because it is the only question here with an exact answer. A clock says
    # "about this old"; a sha says "this build, or not this build". It also
    # answers when nothing else can: this runs above the last-modified guard on
    # purpose, since a deploy with no usable header still states its own commit.
    pub_commit = parse_commit_stamp(pub_body)
    head_sha = head_short_sha()
    behind = commits_behind(pub_commit["sha"]) if pub_commit["state"] == "present" else None
    level, verdict = commit_verdict(pub_commit, head_sha, behind)
    print("  %s %-10s %s"
          % (green(" ok ") if level == "ok" else yellow("warn"), "commit", verdict))

    if pub_lm is None:
        print("  %s no last-modified header — freshness cannot be measured this way\n"
              % yellow("warn"))
        return failures

    # Which clock are we allowed to believe? A clean build-commit stamp is the
    # best of them: lag against it is zero exactly when the deploy is HEAD,
    # with no build-latency drift to absorb. data-built is a real build time
    # too; last-modified is only usable when it is NOT the edge's fill instant.
    # If none holds, say blind — a false green here is the exact failure this
    # section exists to prevent.
    if pub_commit["state"] == "present" and not pub_commit["dirty"] \
            and pub_commit["commit_time"]:
        pub_time, clock = pub_commit["commit_time"], "build-commit"
        print("  %s %-10s build-commit=%s committed %s (a fact in the bytes, "
              "immune to CDN caching)"
              % (green(" ok "), "clock", pub_commit["sha"],
                 time.strftime("%H:%M:%SZ", time.gmtime(pub_time))))
    elif pub_built is not None:
        pub_time, clock = pub_built, "data-built"
        print("  %s %-10s data-built=%s (build time, immune to CDN caching)"
              % (green(" ok "), "clock", time.strftime("%H:%M:%SZ", time.gmtime(pub_built))))
    elif is_cache_fill_clock(pub_headers):
        print("  %s %-10s last-modified is the CDN cache-fill instant, not a build "
              "time, and the page carries no data-built stamp"
              % (yellow("warn"), "clock"))
        print("  %s %-10s BLIND — cannot tell a current deploy from a frozen one "
              "by header" % (yellow("warn"), "lag"))
        print("  %s to judge this deploy: build origin/main and diff the bytes "
              "against the\n       served page, or check `vercel ls` for a Ready "
              "production deployment.\n" % yellow("    "))
        return failures
    else:
        pub_time, clock = pub_lm, "last-modified"

    # 1. lag behind what the deploy can SEE — origin/main, not local HEAD.
    # Held commits are reported on their own line below and are not a failure.
    held = commits_held_locally()
    if held:
        print("  %s %-10s %d commit%s on this machine and not on origin — the "
              "deploy has never been offered them, so they are NOT counted as lag"
              % (yellow("note"), "unpushed", held, "s" if held != 1 else ""))
    ref_ct = origin_commit_epoch() or head_ct
    if ref_ct:
        lag = ref_ct - pub_time
        if lag > PUBLIC_STALE_FAIL_S:
            # Named by commit when we have one — "3 commits behind at 15ee724"
            # is something a reader can act on; "old per some clock" is not.
            origin = (
                "built from commit %s, committed %s"
                % (pub_commit["sha"], time.strftime("%H:%M:%SZ", time.gmtime(pub_time)))
                if clock == "build-commit"
                else "built %s per %s"
                % (time.strftime("%H:%M:%SZ", time.gmtime(pub_time)), clock)
            )
            failures.append(
                "banyan.city is %s BEHIND ORIGIN/MAIN (%s, origin/main committed %s). "
                "This is a real deploy failure: the commit was pushed and the site "
                "did not rebuild. Pushing again will not fix it; publish with "
                "REPO-MOVE.md A0."
                % (_ago(lag), origin,
                   time.strftime("%H:%M:%SZ", time.gmtime(ref_ct)))
            )
            print("  %s %-10s %s behind origin/main" % (red("FAIL"), "lag", _ago(lag)))
        elif lag > PUBLIC_STALE_WARN_S:
            print("  %s %-10s %s behind origin/main (build latency, or a skipped docs-only push)"
                  % (yellow("warn"), "lag", _ago(lag)))
        else:
            print("  %s %-10s %s behind origin/main%s"
                  % (green(" ok "), "lag", _ago(max(lag, 0)),
                     " (held commits are not lag)" if held else ""))

    # 2. mirror cross-check — only ever clock-vs-same-clock. Comparing the
    # mirror's real build time against a cache-fill instant is what made this
    # permanently negative before; mixing them silently is worse than skipping.
    if mir_status != 200:
        mir_time = None
    elif clock == "build-commit":
        # The mirror must answer on the SAME clock. Until it has also deployed
        # a stamped build the cross-check is skipped rather than fudged onto
        # data-built, which would compare a commit time against a build time
        # and reintroduce exactly the sign error this section already fixed
        # once. A skipped cross-check prints a warn and says so.
        mir_commit = parse_commit_stamp(mir_body)
        mir_time = (mir_commit["commit_time"]
                    if mir_commit["state"] == "present" and not mir_commit["dirty"]
                    else None)
    elif clock == "data-built":
        mir_time = mir_built
    else:
        mir_time = http_date(mir_headers)

    if mir_time is None:
        print("  %s %-10s no comparable %s clock — cross-check skipped"
              % (yellow("warn"), "mirror", clock))
    else:
        drift = mir_time - pub_time
        # THE TWO SITES DO NOT REBUILD ON THE SAME TRIGGER, and comparing them as
        # though they did is what made this fire on a healthy deploy. `pages.yml`
        # carries `schedule: cron "*/30 * * * *"` — added on purpose so status.html
        # does not freeze while the farm renders — so the mirror restamps itself
        # every half hour FROM THE SAME COMMIT. Vercel only builds on push. On any
        # day with no push, the mirror is newer by however long it has been, and
        # that is the system working, not the primary dying.
        # The signal only means something when the primary is ALSO behind what was
        # pushed. `lag` is measured against origin/main immediately above, so a
        # mirror newer than a CURRENT primary is a cron tick and nothing else.
        primary_lag = (ref_ct - pub_time) if ref_ct else 0
        if mirror_says_stuck(drift, primary_lag, PUBLIC_STALE_FAIL_S):
            failures.append(
                "the Pages mirror is %s NEWER than banyan.city AND banyan.city is "
                "behind origin/main — the mirror rebuilt and the primary did not, "
                "so the primary's deploy is STUCK. Current content is at %s%s"
                % (_ago(drift), MIRROR_BASE, MIRROR_PROBE)
            )
            print("  %s %-10s %s newer than primary — primary deploy is STUCK"
                  % (red("FAIL"), "mirror", _ago(drift)))
        elif drift > PUBLIC_STALE_FAIL_S:
            print("  %s %-10s %s newer than primary, but the primary is current with "
                  "origin/main — that is the mirror's */30 cron restamping the same "
                  "commit, not a stuck deploy"
                  % (green(" ok "), "mirror", _ago(drift)))
        else:
            print("  %s %-10s within %s of primary" % (green(" ok "), "mirror", _ago(abs(drift))))
    print()
    return failures


def main():
    ap = argparse.ArgumentParser(description="Local screening QA gate for _site/.")
    ap.add_argument("--base", default=DEFAULT_BASE, help="base URL (default %s)" % DEFAULT_BASE)
    ap.add_argument("--no-build", dest="build", action="store_false", help="skip the builders")
    ap.add_argument(
        "--no-public",
        dest="public",
        action="store_false",
        help="skip the public-deploy freshness check (offline runs)",
    )
    ap.set_defaults(build=True, public=True)
    args = ap.parse_args()

    print()
    print(bold("QA GATE — local screening   base=%s" % args.base))
    print()

    if args.build:
        run_builders()
    else:
        print("Build skipped (--no-build); sweeping _site/ as it stands.\n")

    routes = discover_routes()
    if not routes:
        die(
            "_site/ exists but publishes no routes (no index.html, no top-level *.html).\n"
            "The build produced nothing to screen. Run: python3 pipeline/build_site.py"
        )

    # Asked of the REPO, not of _site/ — the one gate here that can see a page
    # which was never published. Everything below sweeps the output and would
    # stay green while a page the founder was promised does not exist.
    page_gaps = unpublished_review_pages()

    public_failures = check_public_freshness() if args.public else []

    results = []
    for route, backing in routes:
        try:
            ok, note = check_route(args.base, route, backing)
        except ConnectionError as e:
            die(
                "The screening server at %s is not answering (%s).\n\n%s"
                % (args.base, e, server_start_hint(args.base))
            )
        results.append((route, backing, ok, note))

    width = max(len(r) for r, _, _, _ in results) + 2
    failures = [r for r in results if not r[2]]

    if failures:
        print(bold("FAILURES"))
        for route, backing, _, note in failures:
            print("  %s %-*s %s" % (red("FAIL"), width, route, note))
        print()
        if any(DIRLIST_NOTE in note for _, _, _, note in failures):
            print(bold("HOW TO FIX THE DIRECTORY-LISTING FAILURES"))
            print(
                "  serving %s: %s"
                % (args.base, running_server_cmd(args.base) or "could not identify the process")
            )
            print(DIRLIST_REMEDY)
            print()

    print(bold("ROUTES (%d)" % len(results)))
    for route, backing, ok, note in results:
        mark = green(" ok ") if ok else red("FAIL")
        print("  %s %-*s %s" % (mark, width, route, note))
    print()

    shadows = shadowed_routes()
    if shadows:
        print(bold("SHADOWED (%d) — two files claim one clean route" % len(shadows)))
        for stem, has_index in shadows:
            detail = (
                "%s.html and %s/index.html both claim it; production picks one, "
                "a local server may pick the other" % (stem, stem)
                if has_index
                else "%s.html and %s/ (no index.html); production serves the .html, "
                "a server that picks the directory serves a file listing" % (stem, stem)
            )
            print("  %s %-*s %s" % (yellow("warn"), width, "/" + stem, detail))
        print("  Not a failure while the routes above are green — a standing hazard.")
        print()

    # RENDERS THAT FINISHED AND REACHED NO PAGE. This gate exists so nobody
    # hands him a URL that is broken; this block is the other half of the same
    # question — whether the URL has on it the work he has been waiting for.
    # Every route above can be green while the four things he asked about are
    # sitting on the results branch unlinked, which is exactly what happened on
    # 2026-08-13/14. A WARNING and never a failure: the count includes rounds a
    # lane is still writing up, and blocking a handover on that would keep the
    # good pages away from him too.
    for line in unpaged_warning():
        print(line)

    if public_failures:
        print(bold("PUBLIC SITE IS NOT SERVING CURRENT WORK"))
        for f in public_failures:
            print("  %s %s" % (red("FAIL"), f))
        print(
            "  This is about banyan.city, NOT about _site/ above: the local build can be\n"
            "  perfect while the public site serves something hours old. Do not hand out\n"
            "  the banyan.city link until this clears."
        )
        print()

    if page_gaps:
        print(bold("REVIEW PAGES IN THE REPO THAT THE SITE DOES NOT PUBLISH (%d)"
                   % len(page_gaps)))
        for rel, reason in page_gaps:
            print("  %s %s — %s" % (red("FAIL"), rel, REVIEW_GAP_REMEDY[reason] % rel))
        print(
            "  These are 404s, not slow pages: no route above covers them, because a\n"
            "  page that was never copied into _site/ is not a route to sweep. Do not\n"
            "  hand out a /review/ URL until this clears."
        )
        print()

    total = len(failures) + len(public_failures) + len(page_gaps)
    if total:
        print(red("QA gate FAILED — do not hand this URL to the founder."))
        print("QA-GATE: FAIL failures=%d" % total)
        return 1

    print(green("All %d routes served correctly. Safe to hand over." % len(results)))
    print("QA-GATE: PASS routes=%d" % len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
