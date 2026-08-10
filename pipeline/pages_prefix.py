#!/usr/bin/env python3
"""Re-base the built site's root-absolute URLs for a host that serves it from a subpath.

WHY THIS EXISTS. `build_site.py` writes three pages whose media is referenced
root-absolutely — `/review/…`, `/trials/…`, `/lab/…` — and that is correct for
banyan.city. Those pages live at `_site/review/index.html` but are SERVED at
`/review`, because `vercel.json` sets `cleanUrls: true, trailingSlash: false`.
With no trailing slash the browser's base is `/`, so a relative `checklist/x.mp4`
resolves to `/checklist/x.mp4` and 404s. That is the bug the founder hit on
2026-08-09 ("images are broken"); `build_site.py`'s `url()` docstring records it.

The GitHub Pages mirror has the opposite geometry. It serves the same tree from
`https://olegmalk.github.io/banyan-city/`, so `/review/x.jpg` means
`olegmalk.github.io/review/x.jpg` — outside the repo's subpath, and a 404 for
every clip, poster and sheet on the page. Measured 2026-08-10: the mirror's
review page was byte-identical to a local build and current, while all 186 of its
media references 404'd. Vercel had the mirror image of the fault — every image
loading, the page itself four commits stale, because the project has been
git-disconnected since 2026-08-09 22:14 (see REPO-MOVE.md).

So this is a mirror-only, publish-time rewrite: `pages.yml` runs it between
`build_site.py` and the artifact upload. `_site/` as Vercel builds it is never
touched, and neither is any generator — the absolute paths stay correct for the
host they were written for.

    python3 pipeline/pages_prefix.py /banyan-city [--root _site] [--dry-run]

IDEMPOTENT by construction: a URL already under the prefix is left alone, so
running it twice — or over an artifact that was already re-based — changes
nothing. That matters because a workflow step is the kind of thing that gets
retried.

WHAT IT DELIBERATELY DOES NOT TOUCH:
  * protocol-relative `//host/path` — those are absolute to a *host*, not to us
  * anything with a scheme (`https:`, `mailto:`, `data:`) or a fragment (`#`)
  * relative refs (`../city.html`) — already correct under any base
"""

import argparse
import re
import sys
from pathlib import Path

# The attributes that carry a URL on this site. `content` is here for the
# og:/twitter: meta tags, which take a URL in exactly the same shape.
ATTRS = ("src", "href", "poster", "content")

# One root-absolute attribute value: a single leading slash, never two.
_ATTR_RE = re.compile(
    r'(?P<attr>' + "|".join(ATTRS) + r')="(?P<url>/(?!/)[^"]*)"'
)

# url(/path) inside a stylesheet or a style="" attribute, same single-slash rule.
_CSS_URL_RE = re.compile(r'url\((?P<q>["\']?)(?P<url>/(?!/)[^"\')]*)(?P=q)\)')

SUFFIXES = (".html", ".css", ".xml", ".svg")


def normalise_prefix(prefix: str) -> str:
    """`banyan-city`, `/banyan-city`, `/banyan-city/` → `/banyan-city`.

    Empty (or `/`) is a legitimate answer meaning "served from the root" — the
    caller then has nothing to do, and `rebase_text` becomes the identity.
    """
    p = "/" + prefix.strip().strip("/")
    return "" if p == "/" else p


def rebase_url(url: str, prefix: str) -> str:
    """Prepend `prefix` to one root-absolute URL, unless it is already there.

    The already-there test is the whole of the idempotency guarantee, and it
    compares path SEGMENTS rather than characters: `/banyan-cityscape` must not
    read as already living under `/banyan-city`.
    """
    if not prefix or not url.startswith("/") or url.startswith("//"):
        return url
    if url == prefix or url.startswith(prefix + "/"):
        return url
    return prefix + url


def rebase_text(text: str, prefix: str) -> tuple[str, int]:
    """Rewrite every root-absolute URL in one file's text. Returns (text, count)."""
    if not prefix:
        return text, 0
    n = 0

    def attr_sub(m):
        nonlocal n
        new = rebase_url(m.group("url"), prefix)
        if new != m.group("url"):
            n += 1
        return f'{m.group("attr")}="{new}"'

    def css_sub(m):
        nonlocal n
        new = rebase_url(m.group("url"), prefix)
        if new != m.group("url"):
            n += 1
        return f'url({m.group("q")}{new}{m.group("q")})'

    text = _ATTR_RE.sub(attr_sub, text)
    text = _CSS_URL_RE.sub(css_sub, text)
    return text, n


def rebase_tree(root: Path, prefix: str, dry_run: bool = False):
    """Walk `root` and rebase every text asset. Returns [(relpath, count), …]."""
    touched = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUFFIXES:
            continue
        original = path.read_text(encoding="utf-8", errors="surrogateescape")
        rewritten, n = rebase_text(original, prefix)
        if n:
            touched.append((path.relative_to(root).as_posix(), n))
            if not dry_run:
                path.write_text(rewritten, encoding="utf-8", errors="surrogateescape")
    return touched


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("prefix", help="the subpath the site is served from, e.g. /banyan-city")
    ap.add_argument("--root", default="_site", help="the built site (default: _site)")
    ap.add_argument("--dry-run", action="store_true", help="report, change nothing")
    a = ap.parse_args(argv)

    root = Path(a.root)
    if not root.is_dir():
        print(f"pages_prefix: no such directory: {root}", file=sys.stderr)
        return 2

    prefix = normalise_prefix(a.prefix)
    if not prefix:
        print("pages_prefix: prefix is the root — nothing to re-base")
        return 0

    touched = rebase_tree(root, prefix, dry_run=a.dry_run)
    verb = "would re-base" if a.dry_run else "re-based"
    for rel, n in touched:
        print(f"  {verb} {n:4d} url(s)  {rel}")
    total = sum(n for _, n in touched)
    print(f"pages_prefix: {verb} {total} url(s) across {len(touched)} file(s) onto {prefix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
