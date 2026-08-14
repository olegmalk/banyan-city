#!/usr/bin/env python3
"""Regenerate review/inbox/index.html from review/inbox.yaml.

Run from the repo root by WHOEVER edits inbox.yaml, in the same commit —
the page is static so it can never disagree with the data unless someone
skips this step, and the pre-push gates catch a page/data mismatch only in
spirit; the contract (SITE.md) is the enforcement.
"""
import html
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
ENTRIES = yaml.safe_load((REPO / "review/inbox.yaml").read_text(encoding="utf-8")) or []

def esc(s):
    return html.escape(str(s))

def link(e):
    u = str(e.get("url", ""))
    if u.startswith("local:"):
        return f'<span class="local">{esc(u)}</span>'
    return f'<a href="{esc(u)}">open →</a>'

# The founder reads this page top to bottom and stops when he runs out of
# patience, so the order is the product: what only he can answer comes first,
# and what needs nothing from him comes last. Groups, in the order they print:
GROUPS = [
    ("taste", "Only you can answer these",
     "Taste calls — what a thing IS, or whether it feels right."),
    ("result", "Results — tell me if I read them wrong",
     "I have already judged these. Say nothing and they stand."),
    ("reading", "Waiting on a read",
     "Scripts and approvals; these unblock work rather than fix it."),
    ("pick", "Picks — veto only",
     "I chose the take. You do not need to pick; say nothing and it stands."),
]
DEFAULT_GROUP = "result"

grouped, done_rows = {g: [] for g, _, _ in GROUPS}, []
for e in ENTRIES:
    row = (f'<div class="card"><b>{esc(e["what"])}</b>'
           f'<p class="hint">answer: {esc(e.get("verdict_hint", ""))}</p>'
           f'<p class="meta">{esc(e.get("kind", ""))} · since {esc(e.get("since", ""))} · {link(e)}</p>')
    r = e.get("resolved")
    if r:
        row += f'<p class="verdict">resolved {esc(r.get("date", ""))}: \u201c{esc(r.get("verdict", ""))}\u201d</p></div>'
        done_rows.append(row)
        continue
    row += "</div>"
    g = str(e.get("group") or DEFAULT_GROUP)
    if g not in grouped:                      # an unknown group must not vanish
        g = DEFAULT_GROUP
    grouped[g].append(row)

open_rows = [r for g, _, _ in GROUPS for r in grouped[g]]
sections = "".join(
    f'<h2 class="grp">{esc(title)}</h2><p class="grpsub">{esc(sub)}</p>{"".join(grouped[g])}'
    for g, title, sub in GROUPS if grouped[g])

doc = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Review inbox — {len(open_rows)} waiting</title>
<style>
  body {{ max-width: 46rem; margin: 0 auto; padding: 1.2rem 1rem 4rem;
         font: 17px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #101312; color: #e6e8e6; }}
  h1 {{ font-size: 1.35rem; margin: .2rem 0 .2rem; }}
  .sub {{ color: #9aa39c; margin: 0 0 1.2rem; }}
  .card {{ border: 1px solid #2a332d; border-radius: 10px; padding: .9rem 1rem;
           margin: 0 0 .9rem; background: #161a18; }}
  .card b {{ font-size: 1.02rem; }}
  .hint {{ margin: .45rem 0 0; color: #cdd4cd; }}
  .meta {{ margin: .45rem 0 0; color: #8b948d; font-size: .88rem; }}
  .meta a {{ color: #8fd6a0; text-decoration: none; padding: .35rem 0; display: inline-block; }}
  .local {{ color: #b8a86e; font-size: .85rem; }}
  .verdict {{ margin: .45rem 0 0; color: #8fd6a0; font-size: .9rem; }}
  .grp {{ font-size: 1.05rem; margin: 1.9rem 0 .1rem; color: #e6e8e6; }}
  .grp:first-of-type {{ margin-top: .6rem; }}
  .grpsub {{ margin: 0 0 .8rem; color: #8b948d; font-size: .9rem; }}
  .standing {{ border-left: 3px solid #8fd6a0; padding: .55rem .9rem; margin: 0 0 1.4rem;
               background: #141a16; color: #cdd4cd; font-size: .95rem; }}
  details {{ margin-top: 1.6rem; }} summary {{ color: #9aa39c; cursor: pointer; }}
</style>
<h1>Review inbox</h1>
<p class="sub">{len(open_rows)} thing{'s' if len(open_rows) != 1 else ''} waiting on you.</p>
<p class="standing">Answer any entry by telling the chat one line — or ignore what doesn't need you.
This page is always the complete list.</p>
{sections if open_rows else '<p class="sub">Nothing waiting. The machine is rendering or blocked on itself, not on you.</p>'}
<details><summary>Resolved — the record</summary>{''.join(done_rows) or '<p class="sub">none yet</p>'}</details>
"""
# THE BOARD LIVES AT /review, and /review/inbox stays alive as a copy.
#
# Founder, 2026-08-14: "then how about you just move everything from /review/inbox to /review?"
# /review used to serve the old Working-cuts page, stale since episode 1 closed.
#
# Both paths are written from the same string, so they cannot drift. /review/inbox is not a
# redirect but a real copy, because it is linked from the status page, from resolved entries and
# from messages already sent — a bookmark that 404s is a worse outcome than a duplicate file.
#
# ONE THING THIS FILE CANNOT DO ALONE: pipeline/build_site.py also generates
# _site/review/index.html from cuts/cuts.yaml, and it runs after this. Until that generator is
# retired it OVERWRITES the board in the built site, so writing here is necessary and not
# sufficient. That retirement is pipeline code and is handed upward rather than done here.
for rel in ("review/index.html", "review/inbox/index.html"):
    (REPO / rel).parent.mkdir(parents=True, exist_ok=True)
    (REPO / rel).write_text(doc, encoding="utf-8")
print(f"wrote review/index.html + review/inbox/index.html — "
      f"{len(open_rows)} open, {len(done_rows)} resolved")
