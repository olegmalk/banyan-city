#!/usr/bin/env python3
"""Builds `review/ep2-picks/index.html` — the episode 2 picking page.

Roman, 2026-08-11: "open the episode 2 beats for me to choose, make sure they
have labels and what the image is supposed to show."

So the page is three things per beat and nothing else: what the shot is supposed
to show, every candidate that exists on disk with its round and seed, and the
verdicts already on record. No ranking, no scores, no "best", no highlighting of
a favourite — eight instruments failed on this material and when a number and
the picture disagree the picture wins. The provisional picks are named in words
as the steward's guess awaiting his call; they are not marked on the images.

Data below is transcribed from `shots.md`, the approved script leaf `002b-t0-c`,
`PROVISIONAL-PICKS-0809.md` and `taste/steward-model.ledger.yaml`. Sheets come
from `build_sheets.py` in this directory.
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_sheets import beat_files, token  # noqa: E402

BEATS = json.loads((HERE / "beats.json").read_text())


def inventory(nn):
    """Counts and round names come from the files, never from the prose —
    the page cannot claim a candidate that is not on the sheet beside it."""
    files = beat_files(nn)
    rounds = []
    for t in (token(f) for f in files):
        r = t.rsplit("-s", 1)[0] if re.search(r"-s\d+$", t) else t
        if r not in rounds:
            rounds.append(r)
    return len(files), rounds

CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { max-width: 60rem; margin: 0 auto; padding: 2rem 1.1rem 6rem;
       font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
       color: #1a1a1a; background: #fff; }
h1 { font-size: 1.6rem; margin: 0 0 .3rem; }
p.sub { color: #666; margin: 0 0 1rem; }
.beat { border-top: 1px solid #e3e3e3; padding: 1.8rem 0 .8rem; }
.beat:last-of-type { border-bottom: 1px solid #e3e3e3; }
h2 { font-size: 1.15rem; font-weight: 600; margin: 0 0 .5rem; }
h2 .n { color: #888; font-variant-numeric: tabular-nums; margin-right: .5rem; }
p.shows { margin: 0 0 .7rem; font-size: 1.02rem; }
p.line { margin: 0 0 .7rem; color: #444; font-style: italic; }
img { width: 100%; height: auto; display: block; border: 1px solid #ddd;
      border-radius: 4px; background: #faf9f7; }
p.meta { margin: .5rem 0 0; font-size: .9rem; color: #666; }
p.rec { margin: 0 0 .7rem; font-size: .92rem; color: #444;
        border-left: 3px solid #e0ddd6; padding-left: .7rem; }
p.rec b { font-weight: 600; }
q { quotes: "\\201C" "\\201D"; }
footer { margin-top: 3rem; color: #666; font-size: .9rem;
         border-top: 1px solid #e3e3e3; padding-top: 1rem; }
nav.toc { margin: 0 0 2rem; font-size: .93rem; line-height: 2; }
nav.toc a { display: inline-block; min-width: 2.6rem; margin-right: .2rem;
            text-align: center; text-decoration: none; border: 1px solid #ddd;
            border-radius: 4px; padding: .1rem .35rem; color: #1a1a1a; }
@media (prefers-color-scheme: dark) {
  body { background: #141416; color: #e8e8e8; }
  .beat, footer, nav.toc a { border-color: #2c2c30; }
  img { border-color: #2c2c30; background: #1c1c1f; }
  p.sub, p.meta { color: #8a8a8a; }
  p.line, p.rec { color: #bdbdbd; }
  p.rec { border-left-color: #3a3a40; }
  nav.toc a { color: #e8e8e8; }
}
"""


def esc(s):
    return html.escape(s, quote=False)


def render():
    TOTAL = sum(inventory(b["n"])[0] for b in BEATS)
    out = ['<meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           '<title>Episode 2 — every beat, every candidate</title>',
           f"<style>{CSS}</style>",
           "<h1>Episode 2 &mdash; every beat, every candidate</h1>",
           f'<p class="sub">002b-first-citizen. Twenty-one beats, {TOTAL} '
           'pictures, <b>none of them picked</b>. Each beat says what the shot is '
           'supposed to show, then every candidate that exists, labelled by round '
           'and seed. Nothing is ranked and nothing is marked as better. '
           '&mdash; 2026&#8209;08&#8209;11</p>',
           '<p class="sub">Labels read <b>round&#8209;seed</b>: <code>r3-s2</code> '
           'is round&nbsp;3, seed&nbsp;2, whose full name is '
           '<code>002b-b13-r3-s2</code>. Naming one is enough &mdash; '
           '&ldquo;b07 r3-s1&rdquo; picks it. &ldquo;b07, none of them&rdquo; is '
           'also an answer.</p>',
           '<p class="sub"><b>Who turned things down.</b> Almost every rejection '
           'below is the <em>steward&rsquo;s</em>, made on 2026-08-09 against a '
           'model of your taste, written down before you had seen anything and '
           'phrased in your register. Those sentences are not quotes from you. '
           'Four beats do carry your own words &mdash; <b>01</b>, <b>13</b>, '
           '<b>15</b> and <b>16</b> &mdash; and those are quoted and attributed to '
           'you where they appear. Everything a machine scored is left off this '
           'page: when a number and the picture disagree, the picture wins.</p>']

    toc = " ".join(f'<a href="#b{b["n"]}">{b["n"]}</a>' for b in BEATS)
    out.append(f'<nav class="toc">{toc}</nav>')

    for b in BEATS:
        n = b["n"]
        out.append(f'<div class="beat" id="b{n}">')
        out.append(f'<h2><span class="n">{n}</span>{esc(b["title"])}</h2>')
        out.append(f'<p class="shows">{esc(b["shows"])}</p>')
        if b.get("line"):
            out.append(f'<p class="line">{esc(b["line"])}</p>')
        # What is already on record goes ABOVE the sheet, not below it. b01
        # carries 58 candidates and b13 twenty-eight; a note printed under an
        # image that tall is a note read after the looking it was meant to
        # inform, which on this page is the same as not printing it.
        for rec in b.get("recorded", []):
            out.append(f'<p class="rec">{rec}</p>')
        count, rounds = inventory(n)
        sheet = HERE / "sheets" / f"b{n}.jpg"
        if sheet.exists() and count:
            out.append(f'<img src="/review/ep2-picks/sheets/b{n}.jpg" '
                       f'alt="candidates for beat {n}" loading="lazy">')
            out.append(f'<p class="meta">{count} candidates &mdash; rounds '
                       f'{esc(", ".join(rounds))}</p>')
        else:
            out.append('<p class="meta">No sheet &mdash; nothing rendered for '
                       'this beat yet.</p>')
        out.append("</div>")

    out.append(f'<footer>The {TOTAL} pictures are every candidate PNG under '
               '<code>takes/stills/</code> as of 2026-08-11, plus the later frames '
               'that were rendered into <code>review/</code> and left there &mdash; '
               "b01's r9 and the inpaint, b15's goblin wave, the b04/b14 goblin "
               'frames. Sheets were rebuilt for this page rather than reused: the '
               'ones in <code>review/ep2-stills/</code> were made 08-07 and predate '
               'round&nbsp;3 on nineteen beats. What each shot should show is from '
               '<code>shots.md</code> and the approved script <code>002b-t0-c</code> '
               '(approved by you 2026-08-03). Verdict history is from '
               '<code>PROVISIONAL-PICKS-0809.md</code> and '
               '<code>taste/steward-model.ledger.yaml</code>, where every episode-2 '
               'still-selection record still reads '
               '<code>founder_verdict: null</code>.</footer>')
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    dest = HERE / "index.html"
    dest.write_text(render())
    print(f"{dest} {dest.stat().st_size} bytes, {len(BEATS)} beats")
