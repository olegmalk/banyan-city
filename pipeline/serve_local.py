#!/usr/bin/env python3
"""Local screening server for `_site/` — the one `pipeline/qa_local.py` sweeps.

    python3 pipeline/serve_local.py [root=_site] [port=8787]

It exists to resolve paths the way production does. `vercel.json` sets
cleanUrls=true and trailingSlash=false, so on banyan.city `/status` serves
status.html and `/review` serves review/index.html. A stock `http.server` has
no clean URLs at all and 404s on every one of those.

WHY THIS LIVES IN THE REPO AND NOT IN A SCRATCHPAD: on 2026-08-10 the screening
server was a throwaway in one session's temp directory. It had a resolution bug
(below), nobody could find the file to fix it, and it would have died with that
session leaving the next one to rewrite it from scratch — which is how the bug
got written the first time. A harness the next session cannot find is not a
harness.

THE RESOLUTION ORDER IS THE WHOLE POINT. `_site/` contains both `watch.html`
(the hub) and `watch/` (16 episode pages, no index.html). Asked for `/watch`,
the obvious implementation checks `os.path.exists()` first, finds the
directory, and renders a file listing — which is what the founder got. Vercel
prefers the .html, so a directory that publishes no index.html must fall
through to its sibling page. Order: exact file, then .html-for-directory-
without-index, then .html-for-extensionless. Changing it re-opens the bug, so
qa_local.py fails on any route that comes back as a directory listing.
"""

import functools
import http.server
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "_site"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8787


class CleanURL(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = super().translate_path(path)
        # A directory that publishes no index.html is not a route in production;
        # its sibling .html is. Checked before exists() or the directory wins.
        if (os.path.isdir(p)
                and not os.path.exists(os.path.join(p, "index.html"))
                and os.path.exists(p.rstrip("/") + ".html")):
            return p.rstrip("/") + ".html"
        if os.path.exists(p):
            return p
        if not os.path.splitext(p)[1] and os.path.exists(p.rstrip("/") + ".html"):
            return p.rstrip("/") + ".html"
        return p

    def log_message(self, *a):
        pass


def main():
    root = os.path.abspath(ROOT)
    if not os.path.isdir(root):
        sys.exit("no such directory: %s (build it: python3 pipeline/build_site.py)" % root)
    handler = functools.partial(CleanURL, directory=root)
    print("serving %s at http://127.0.0.1:%d" % (root, PORT), flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler).serve_forever()


if __name__ == "__main__":
    main()
