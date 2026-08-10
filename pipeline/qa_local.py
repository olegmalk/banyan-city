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
BUILDERS = ["build_site.py", "build_sim.py", "build_pulse.py"]

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
    if want and want not in " ".join(body.split()):
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

    Two independent signals, because either alone can lie:

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

    if pub_lm is None:
        print("  %s no last-modified header — freshness cannot be measured this way\n"
              % yellow("warn"))
        return failures

    # 1. lag behind HEAD
    if head_ct:
        lag = head_ct - pub_lm
        if lag > PUBLIC_STALE_FAIL_S:
            failures.append(
                "banyan.city is %s BEHIND HEAD (deployed %s, HEAD committed %s). "
                "The deploy is not firing — pushing again will not fix it."
                % (_ago(lag), time.strftime("%H:%M:%SZ", time.gmtime(pub_lm)),
                   time.strftime("%H:%M:%SZ", time.gmtime(head_ct)))
            )
            print("  %s %-10s %s behind HEAD" % (red("FAIL"), "lag", _ago(lag)))
        elif lag > PUBLIC_STALE_WARN_S:
            print("  %s %-10s %s behind HEAD (build latency, or a skipped docs-only push)"
                  % (yellow("warn"), "lag", _ago(lag)))
        else:
            print("  %s %-10s %s behind HEAD" % (green(" ok "), "lag", _ago(max(lag, 0))))

    # 2. mirror cross-check
    mir_lm = http_date(mir_headers) if mir_status == 200 else None
    if mir_lm is None:
        print("  %s %-10s unavailable — cross-check skipped" % (yellow("warn"), "mirror"))
    else:
        drift = mir_lm - pub_lm
        if drift > PUBLIC_STALE_FAIL_S:
            failures.append(
                "the Pages mirror is %s NEWER than banyan.city — the mirror rebuilt "
                "and the primary did not, so the primary's deploy is STUCK. "
                "Current content is at %s%s"
                % (_ago(drift), MIRROR_BASE, MIRROR_PROBE)
            )
            print("  %s %-10s %s newer than primary — primary deploy is STUCK"
                  % (red("FAIL"), "mirror", _ago(drift)))
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

    total = len(failures) + len(public_failures)
    if total:
        print(red("QA gate FAILED — do not hand this URL to the founder."))
        print("QA-GATE: FAIL failures=%d" % total)
        return 1

    print(green("All %d routes served correctly. Safe to hand over." % len(results)))
    print("QA-GATE: PASS routes=%d" % len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
