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

open_rows, done_rows = [], []
for e in ENTRIES:
    row = (f'<div class="card"><b>{esc(e["what"])}</b>'
           f'<p class="hint">answer: {esc(e.get("verdict_hint", ""))}</p>'
           f'<p class="meta">{esc(e.get("kind", ""))} · since {esc(e.get("since", ""))} · {link(e)}</p>')
    r = e.get("resolved")
    if r:
        row += f'<p class="verdict">resolved {esc(r.get("date", ""))}: “{esc(r.get("verdict", ""))}”</p></div>'
        done_rows.append(row)
    else:
        row += "</div>"
        open_rows.append(row)

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
  details {{ margin-top: 1.6rem; }} summary {{ color: #9aa39c; cursor: pointer; }}
</style>
<h1>Review inbox</h1>
<p class="sub">{len(open_rows)} thing{'s' if len(open_rows) != 1 else ''} waiting on you.
Verdicts go in the chat, in whatever words; each one is recorded here with the entry it closes.</p>
{''.join(open_rows) if open_rows else '<p class="sub">Nothing waiting. The machine is rendering or blocked on itself, not on you.</p>'}
<details><summary>Resolved — the record</summary>{''.join(done_rows) or '<p class="sub">none yet</p>'}</details>
"""
(REPO / "review/inbox/index.html").write_text(doc, encoding="utf-8")
print(f"wrote review/inbox/index.html — {len(open_rows)} open, {len(done_rows)} resolved")
