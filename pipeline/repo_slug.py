"""Which GitHub repo is this build for? One answer, asked in one place.

WHY THIS FILE EXISTS. On 2026-08-10 the repo moved from `olegmlkvorg` to
`olegmalk`, and eight builders each carried their own hardcoded
`"olegmlkvorg/banyan-city"`. That alone would have been a tedious sweep. The
part that made it a trap is that ONE of them — `build_site.py` — read
`os.environ.get("GITHUB_REPOSITORY", <literal>)`, and `GITHUB_REPOSITORY` is set
by GitHub Actions and NOT by Vercel (Vercel's git variables are
`VERCEL_GIT_REPO_OWNER` / `VERCEL_GIT_REPO_SLUG`). banyan.city ships from
Vercel; the Pages mirror ships from Actions. So after the move the mirror would
have silently self-healed to the new owner while production kept publishing the
old one — two surfaces disagreeing about who owns the product, and neither
raising an error. A wrong answer that nothing complains about is worse than a
missing one, so the question now has exactly one implementation.

The order below is "who actually knows", most authoritative first:

1. `BANYAN_GH_REPO` — an explicit override, for anyone running a build against
   a repo the environment cannot see (a mirror, a local experiment).
2. `GITHUB_REPOSITORY` — GitHub Actions states it, and in a fork it correctly
   names the fork rather than upstream. This project is meant to be forkable.
3. `VERCEL_GIT_REPO_OWNER` + `VERCEL_GIT_REPO_SLUG` — the same fact as (2), in
   the vocabulary of the platform that serves banyan.city. This pair is the
   line whose absence caused the trap.
4. `git remote get-url origin` — a developer's checkout knows its own remote,
   and a fork's checkout knows it is a fork. This is what makes the literal
   below almost unreachable in practice.
5. A literal, because a build must not fail over this. It is a last resort and
   nothing should depend on it being right; if it is ever load-bearing again,
   the fix is another entry above it, not a new copy of it somewhere else.

Import this rather than writing the string. `gh_repo()` is the only public
name that matters; the module-level constants are for the common case where a
builder wants the value once, at import.
"""

import os
import re
import subprocess
from pathlib import Path

# Last resort only — see step 5 above. Every other path outranks it.
FALLBACK_REPO = "olegmalk/banyan-city"

_SLUG_RE = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")


def _from_git_remote(start: Path) -> str:
    """`owner/name` from the checkout's origin, or "" if it cannot be read.

    Both remote spellings appear in this project — the Mac clones over HTTPS,
    the render box pushes over SSH — so both are parsed. Any failure at all
    (no git, no repo, no origin, a remote that is not GitHub) returns "" and
    lets the caller fall through; this is a best-effort probe, never an error.
    """
    try:
        # encoding named explicitly: on the farm's Windows box the default is
        # cp1252 and a text-mode read that cannot decode fails on subprocess's
        # reader thread, silently setting .stdout to None (see
        # test_every_text_mode_subprocess_names_its_encoding).
        url = subprocess.run(
            ["git", "-C", str(start), "remote", "get-url", "origin"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    if not url:
        return ""
    # git@github.com:owner/name.git · ssh://git@github.com/owner/name.git ·
    # https://github.com/owner/name(.git)
    m = re.search(r"github\.com[:/]+([A-Za-z0-9._-]+/[A-Za-z0-9._-]+?)(?:\.git)?/*$", url)
    return m.group(1) if m else ""


def gh_repo() -> str:
    """The `owner/name` slug this build should publish links against."""
    explicit = os.environ.get("BANYAN_GH_REPO", "").strip()
    if _SLUG_RE.match(explicit):
        return explicit

    actions = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if _SLUG_RE.match(actions):
        return actions

    owner = os.environ.get("VERCEL_GIT_REPO_OWNER", "").strip()
    slug = os.environ.get("VERCEL_GIT_REPO_SLUG", "").strip()
    if owner and slug:
        pair = f"{owner}/{slug}"
        if _SLUG_RE.match(pair):
            return pair

    remote = _from_git_remote(Path(__file__).resolve().parent)
    if _SLUG_RE.match(remote):
        return remote

    return FALLBACK_REPO


GH_REPO = gh_repo()
REPO_URL = f"https://github.com/{GH_REPO}"
RAW_URL = f"https://raw.githubusercontent.com/{GH_REPO}"
API_URL = f"https://api.github.com/repos/{GH_REPO}"
SSH_REMOTE = f"git@github.com:{GH_REPO}.git"
# The Pages mirror. It moved with the repo and GitHub publishes NO redirect for
# it, so this is the one derived URL that hard-breaks rather than forwarding.
PAGES_URL = f"https://{GH_REPO.split('/')[0]}.github.io/{GH_REPO.split('/')[-1]}"
