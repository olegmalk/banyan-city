"""Which commit is this build made of? One answer, stamped into every page.

WHY THIS FILE EXISTS. On 2026-08-10 banyan.city served a 36-hour-old build
because the Vercel project had lost its git link, and nothing we owned could
tell. `qa_local.py` had a freshness check, but it read the deploy's age off
Vercel's HTTP `last-modified`, which is the instant a CDN edge filled its cache
— not a build clock (see qa_local.is_cache_fill_clock). So the check could not
distinguish a fresh deploy from a frozen one, and printed green either way. A
human comparing timestamps by hand is what actually caught it.

The fix is to stop inferring. A build knows exactly which commit it was made
from; it should say so in the bytes it writes, where no cache can move it.
`build_sim.py` already proved the shape works — it stamps `data-built="<epoch>"`
on every studio entry, and that stamp survives caching intact. This is the same
idea with the missing half: WHEN a page was built is only half of "is it
current", and WHICH COMMIT is the half that can be checked against HEAD.

WHY A `<meta>` TAG AND NOT `/build.json`. A sidecar JSON file is a separate
route with its own cache entry, so it can be fresh while the page you are
reading is stale — it would answer a question about itself, not about the page.
The stamp has to travel in the same bytes as the content it describes. A meta
tag also rides along automatically to the GitHub Pages mirror, which is
qa_local's control in the freshness cross-check, with no second publishing rule
to remember. And `data-built` already established "the page states this about
itself" as this project's convention; a parallel mechanism would just be a
second thing to keep in sync.

WHAT IT LOOKS LIKE, in the head of every page all three builders write:

    <meta name="build-commit" content="15ee724">
    <meta name="build-commit-time" content="1754899200">

THE DIRTY TREE IS NOT A CLEAN SHA. A build from a working tree with
uncommitted changes does not match any commit — its bytes were never in git —
so claiming the sha it happens to sit on would be a lie of exactly the kind
this file exists to stop. It is stamped `15ee724-dirty`, git-describe's
spelling, which cannot be mistaken for a sha by a reader or by a comparison.

AND "I DO NOT KNOW" IS NOT "I AM CURRENT". A build that cannot see git at all
stamps `content="unknown"` rather than omitting the tag. The absence of a tag
already means something specific — this deploy predates the stamp entirely —
and a builder that shrugged must not be able to impersonate that, or the other
way round. qa_local reports the two separately for the same reason.

BUT A PLATFORM CHECKOUT IS NOT AN AUTHOR'S TREE, added 2026-08-20. From at
least 2026-08-19 banyan.city served EVERY production deploy stamped
`<sha>-dirty` — a permanent dirty flag, which is the same as no flag at all:
qa_local can never say "current" and the freshness check this file exists to
feed goes back to being blind, just noisily this time. It was not our build
dirtying the tree, and it was not Linux: the GitHub Pages mirror runs the same
`build_site.py` on ubuntu-latest out of a real checkout and stamps clean, a
pristine `--depth=10` clone stamps clean, and a full `vercel build` run against
that clone stamps clean too. What is left is the Vercel BUILD CONTAINER's own
droppings landing in `/vercel/path0` beside the checkout — files no author
wrote and no `.gitignore` of ours anticipated.

So the dirty question is now asked in two halves, because there are two facts
and they have different weights:

  * TRACKED changes — modified or deleted files git is already following. These
    really do mean the bytes being built are not the commit's bytes. They flag
    dirty everywhere, always, no exemption.
  * UNTRACKED files. Locally these count too, and deliberately: a builder reads
    media out of the tree and can publish a file that was never committed. In a
    checkout the PLATFORM made and named — `VERCEL_GIT_COMMIT_SHA` or
    `GITHUB_SHA` present AND equal to the sha git is sitting on — nobody edited
    anything; whatever is untracked arrived with the container. Those are
    reported in the build log and not counted against the stamp.

The env sha is not trusted on its own for this: it must AGREE with git's HEAD.
A platform variable that names some other commit means the checkout is not what
the platform thinks it is, which is precisely when the stamp must stay strict.

And a dirty tree now SAYS WHAT IS DIRTY, once, on stderr — see `_report`. The
whole cost of this bug was that `-dirty` named no path, so three sessions could
only guess at what the build container leaves lying around.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# 7 to 40 hex, optionally `-dirty`. Deliberately not anchored to a fixed width:
# git's short sha grows with the repo, and CI hands us the full 40.
STAMP_RE = re.compile(r"^([0-9a-f]{7,40})(-dirty)?$")

UNKNOWN = "unknown"

# The variables a CI platform sets to name the commit it checked out for us.
# Order is preference; both are 40-hex in practice, short forms accepted.
PLATFORM_SHA_KEYS = ("VERCEL_GIT_COMMIT_SHA", "GITHUB_SHA")

# How many porcelain lines _report prints before it stops. Enough to name a
# cause, few enough that a container full of cache droppings cannot bury the
# rest of the build log.
REPORT_LIMIT = 20


def platform_checkout(env):
    """-> (env var name, sha) for a build whose platform names its own commit,
    else (None, ""). The sha is lowercased; a short form is allowed because
    nothing here needs the full 40 to compare a prefix."""
    for key in PLATFORM_SHA_KEYS:
        v = (env.get(key) or "").strip().lower()
        if re.fullmatch(r"[0-9a-f]{7,40}", v):
            return key, v
    return None, ""


def _git(args):
    """`git <args>` in this repo, or "" on any failure at all.

    encoding named explicitly, same reason as repo_slug._from_git_remote: the
    farm's Windows box defaults to cp1252 and a text-mode read that cannot
    decode kills subprocess's reader thread, leaving .stdout as None.
    """
    try:
        p = subprocess.run(
            ["git", "-C", str(REPO)] + args,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            encoding="utf-8", errors="replace", timeout=10,
        )
    except Exception:
        return ""
    return (p.stdout or "").strip() if p.returncode == 0 else ""


def build_commit(env=None, git=None):
    """-> {"sha", "dirty", "commit_time", "source"}. sha is "" when unknown.

    Order is "who can actually see the tree", not "who is most convenient":

    1. git. The only source that can see whether the working tree is DIRTY,
       which is the one state that must never be reported as a clean sha.
    2. `VERCEL_GIT_COMMIT_SHA` / `GITHUB_SHA`, for a build where the checkout
       has no `.git` to ask. A CI checkout of a named sha is clean by
       construction, so nothing is lost by git being unavailable there — but
       the commit's own time is, and it comes back None rather than guessed.
    3. Nothing. Returns sha "", which renders as `unknown`.

    `env` and `git` are injectable so the tests can drive every branch without
    a repo; production passes neither.
    """
    env = os.environ if env is None else env
    run = _git if git is None else git
    key, platform_sha = platform_checkout(env)

    sha = run(["rev-parse", "HEAD"])
    if re.fullmatch(r"[0-9a-f]{40}", sha or ""):
        # --porcelain over `diff --quiet`: it also sees untracked files that a
        # builder may have read. Kept whole rather than reduced to a bool, so
        # the report below can name what it found.
        entries = [ln for ln in run(["status", "--porcelain"]).splitlines()
                   if ln.strip()]
        # The platform named a commit AND git is sitting on it: this checkout
        # is the platform's, untouched by an author, so untracked files beside
        # it are the container's and cannot have come out of a commit.
        verified = bool(platform_sha) and sha.startswith(platform_sha)
        counted = ([e for e in entries if not e.startswith("??")]
                   if verified else entries)
        ct = run(["log", "-1", "--format=%ct"])
        return {
            "sha": sha[:7],
            "dirty": bool(counted),
            "commit_time": int(ct) if ct.isdigit() else None,
            "source": "git",
            "entries": entries,
            "checkout": key if verified else None,
        }

    if platform_sha:
        return {"sha": platform_sha[:7], "dirty": False, "commit_time": None,
                "source": "env:" + key, "entries": [], "checkout": key}

    return {"sha": "", "dirty": False, "commit_time": None, "source": "none",
            "entries": [], "checkout": None}


_CACHE = {}


def _report(info, out=None):
    """Name the uncommitted paths, once, on stderr. Silent on a clean tree.

    stderr and not stdout: build_site's stdout is a report a human reads and
    other tools parse, and this is a diagnostic. Vercel and Actions both
    capture the two together, which is the only place it needs to arrive.
    """
    entries = info.get("entries") or []
    if not entries:
        return
    out = sys.stderr if out is None else out
    if info["dirty"]:
        head = ("build-commit: %s — the working tree does not match this "
                "commit (%d path(s)):" % (stamp_value(info), len(entries)))
    else:
        head = ("build-commit: %s — %d untracked path(s) beside a %s checkout, "
                "not counted against the stamp:"
                % (stamp_value(info), len(entries), info.get("checkout")))
    print(head, file=out)
    for line in entries[:REPORT_LIMIT]:
        print("    " + line, file=out)
    if len(entries) > REPORT_LIMIT:
        print("    … and %d more" % (len(entries) - REPORT_LIMIT), file=out)


def current():
    """build_commit() for this process, asked of git exactly once.

    page() runs per node and there are hundreds of them; three subprocesses
    each would turn a build into a fork storm. The answer cannot change
    mid-build in any way we would want to publish — a build must describe one
    commit, not whichever commit a lane happened to land halfway through it.
    """
    if "info" not in _CACHE:
        _CACHE["info"] = build_commit()
        _report(_CACHE["info"])
    return _CACHE["info"]


def stamp_value(info=None):
    """The `content` of the build-commit meta: `15ee724`, `15ee724-dirty`, or
    `unknown`. Never a bare sha for a tree that does not match it."""
    info = current() if info is None else info
    if not info["sha"]:
        return UNKNOWN
    return info["sha"] + ("-dirty" if info["dirty"] else "")


def meta_tags(info=None):
    """The head block, newline-terminated on the left so it can be dropped
    straight into an existing `<head>` f-string without disturbing its layout.

    The time tag is omitted when there is no commit time rather than written
    empty or zero: a reader that finds it can trust it, and one that does not
    falls back to the sha, which is the stronger signal anyway.
    """
    info = current() if info is None else info
    out = '\n<meta name="build-commit" content="%s">' % stamp_value(info)
    if info["commit_time"]:
        out += '\n<meta name="build-commit-time" content="%d">' % info["commit_time"]
    return out


if __name__ == "__main__":
    print(build_commit())
    print(meta_tags().strip())
