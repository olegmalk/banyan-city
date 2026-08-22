#!/usr/bin/env python3
r"""ROUND 3 GOES ON TOP OF THE SHEET HE IS ALREADY LOOKING AT.

    python3 pipeline/build_guardcast3_page_0822.py --judged a,c,e,f,g,i,j30 \
        [--note-b "..."] [--dry-run]

$0. Reads the judged round-3 stills out of farm-out/, writes JPEGs and rewrites
review/ep2-guardcast2-0822/index.html IN PLACE.

WHY IT UPDATES THAT PAGE INSTEAD OF OPENING A NEW ONE. The founder is on
/review/ep2-guardcast2-0822 right now and his note -- "most of these have some
kinda gas or liquid on their face which is a problem" -- is about the men on it.
A new URL would make him find the comparison himself; the same URL puts round 3
above the fold and leaves round 2 underneath, collapsed and greyed, so the pair
is one scroll apart and his own note still has its subject.

WHAT THE PAGE MAY AND MAY NOT SAY. It asks for one letter. The reasoning, the
token budgets and the fail modes belong in the spec and the deriver -- the only
steward sentence that earns a place here is the one that tells him what changed
and what to look for, because without it he cannot tell a fixed frame from a
lucky one.

THE ROUND-2 IMAGES ARE NOT REWRITTEN OR DELETED. a.jpg..j.jpg stay exactly where
they are and keep their captions inside the collapsed block; round 3 lands under
`r3-<cell>.jpg`, so nothing he has already seen changes address.
"""
from __future__ import annotations

import argparse
import html
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_guardcast3_0822 as r3                                 # noqa: E402

OUT = os.path.join(REPO, "review", "ep2-guardcast2-0822")
URL = "/review/ep2-guardcast2-0822"

# Round 2's nine, verbatim from the page they are on now. Copied rather than
# re-derived: this block is HISTORY and it must not move when a deriver does.
ROUND2 = (
    ("a", "dark brown hair / heavy jaw / gormless, mouth open"),
    ("c", "cropped brown hair / round heavy face / small eyes, flat frown"),
    ("d", "shaved head, stubble / broad flat face / blank, wide-set eyes"),
    ("e", "shaggy black hair / gaunt narrow face / big ears, brows up"),
    ("f", "brown hair, thick moustache / jowly / eyes shut"),
    ("g", "receding hair, high forehead / narrow face / puzzled"),
    ("h", "curly black hair / thick neck / grinning"),
    ("i", "bald, big head / doughy face / worried, mouth open"),
    ("j", "short red hair, freckles / heavy brow / blunt scowl"),
)

DESC = {
    "a": "thick dark brown hair / heavy square jaw / thick neck",
    "b": "light sandy hair / long thin face / weak chin",
    "c": "cropped ginger hair / round heavy face / full cheeks",
    "d": "shaved head, dark stubble / broad flat face",
    "e": "shaggy black hair / gaunt narrow face / big ears",
    "f": "grey-streaked brown hair / thick moustache / jowly",
    "g": "receding sandy hair / high forehead / narrow face",
    "h": "curly black hair / wide square face / thick neck",
    "i": "straight light brown hair / big nose / doughy face",
    "j": "short red hair, freckles / blunt chin",
}


def parse_cell(token):
    """`a` -> ('a', 0); `j30` -> ('j', 30). The page speaks in cells, not ids."""
    token = token.strip().lower()
    if token.endswith("30"):
        return token[:-2], 30
    return token, 0


def src_of(letter, offset):
    jid = r3.spec_id(letter, offset)
    return os.path.join(REPO, "farm-out", jid, "%s-%s.png" % (jid, r3.ARM))


def _jpeg(src, dst, quality=88):
    from PIL import Image
    im = Image.open(src).convert("RGB")
    im.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)
    return im.size


CSS = """
:root { --bg:#111214; --panel:#1b1d20; --line:#31343a; --ink:#f0f2f4;
        --muted:#9aa1a9; --accent:#e0c069; --good:#7fd6a2; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); padding:0 20px 90px;
       font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1180px; margin:0 auto; }
h1 { font-size:23px; margin:32px 0 4px; font-weight:650; }
h2 { font-size:17px; margin:38px 0 10px; font-weight:650; color:var(--accent); }
.ask { background:var(--panel); border:1px solid var(--accent); border-radius:10px;
       padding:16px 18px; margin:16px 0 10px; }
.ask b { color:var(--accent); font-size:18px; }
.ask code { background:#0b0c0d; padding:2px 7px; border-radius:4px;
            font-size:16px; color:var(--accent); }
.note { color:var(--muted); font-size:14.5px; margin:10px 0 22px; max-width:80ch; }
.note b { color:var(--ink); }
.settled { background:#16211a; border:1px solid #2f5c42; border-radius:10px;
           padding:14px 18px; margin:16px 0 8px; }
.settled b { color:var(--good); }
.grid { display:grid; gap:26px 22px; grid-template-columns:repeat(auto-fill,minmax(290px,1fr)); }
figure { margin:0; }
img { width:100%; height:auto; display:block; border-radius:6px;
      border:1px solid var(--line); background:#000; }
figcaption { margin-top:8px; font-size:15px; }
.tag { display:inline-block; min-width:1.6em; padding:1px 8px; margin-right:8px;
       border-radius:4px; background:var(--accent); color:#15161a;
       font-weight:700; font-size:16px; }
.desc { color:var(--muted); }
.ref { max-width:320px; }
.ref img { border-color:var(--good); }
details { margin:14px 0; color:var(--muted); font-size:14.5px; }
summary { cursor:pointer; color:var(--accent); font-size:16px; }
/* THE SUPERSEDED ROUND IS GREYED, NOT HIDDEN. He asked what was wrong with
   these faces; the answer is only legible next to them. */
.old { opacity:0.45; filter:saturate(0.55); }
.old:hover { opacity:0.8; filter:none; }
.old .tag { background:#5a5f68; color:#cfd3d8; }
table { border-collapse:collapse; margin:10px 0 6px; font-size:14.5px; }
td, th { border:1px solid var(--line); padding:6px 11px; text-align:left; }
th { color:var(--accent); font-weight:600; }
td.no { color:#ff9a86; }
td.yes { color:var(--good); }
"""


def card(letter, offset, url_name, desc, cls=""):
    tag = letter.upper()
    return ('<figure%s><img src="%s/%s" alt="candidate %s" loading="lazy">'
            '<figcaption><span class="tag">%s</span>'
            '<span class="desc">%s</span></figcaption></figure>'
            % (' class="%s"' % cls if cls else "", URL, url_name, tag, tag,
               html.escape(desc)))


def build(judged, dropped_note, dry_run=False):
    os.makedirs(OUT, exist_ok=True)
    shown, missing = [], []
    for token in judged:
        letter, offset = parse_cell(token)
        src = src_of(letter, offset)
        if not os.path.exists(src):
            missing.append(token)
            continue
        name = "r3-%s.jpg" % letter
        if not dry_run:
            _jpeg(src, os.path.join(OUT, name))
        shown.append((letter, name, DESC[letter]))
    if missing:
        raise SystemExit("!! judged cells with no rendered png: %s"
                         % ", ".join(missing))
    shown.sort(key=lambda t: t[0])

    new_cards = "\n".join(card(l, 0, n, d) for l, n, d in shown)
    old_cards = "\n".join(card(l, 0, "%s.jpg" % l, d, cls="old")
                          for l, d in ROUND2)

    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guard 2 — round 3, pick one</title>
<style>%(css)s</style></head><body><div class="wrap">

<h1>Guard 2 — round 3, %(n)d candidates, pick one</h1>

<div class="ask"><b>answer:</b> <code>guardcast3 &lt;letter&gt;</code>
&nbsp;— or <code>none, because X</code>, and X is the next round's one variable.</div>

<div class="settled"><b>THE GAS AND THE LIQUID WERE THE PROMPT'S FAULT, AND THEY
ARE GONE FROM 14 OF THE 15 FRAMES THIS ROUND DREW.</b> They were manga effect
symbols — the sweat drop, the sigh puff, the drool bead — drawn onto the skin as
if they were anatomy. This model learned its captions from a booru, and on that
site the dazed-expression tags round 2 asked for (<i>blank stare</i>,
<i>puzzled frown</i>, <i>gormless grin</i>) sit in the same captions as the
symbols. Ask for the mood and you get the mood's punctuation. So round 3 asks
for no mood at all: every man carries the same three physical things —
<b>slack open mouth, raised eyebrows, dull half-closed eyes</b> — and the eight
symbols are named in the negative. Same ten men, same clothes, same framing,
same seeds.</div>

<div class="ask" style="border-color:#ff9a86"><b>what it cost, before you scroll:</b>
the replacement expression bought a <b>distress</b> read, and distress comes with
<b>hands</b>. Eight of the fifteen came back with a hand clamped to the face —
including G and I, which had no hand in round 2. That is why five men are below
and not ten. The symbols are fixed; the mouth-and-brow wording that fixed them is
not the final one, and the next round's single variable is already named:
<i>raised eyebrows</i> is the term doing it.</div>

<figure class="ref"><img src="%(url)s/guard1.jpg" alt="guard 1, as ruled">
<figcaption><span class="tag" style="background:var(--good)">1</span><span class="desc">Guard 1, as you ruled him. This page does not re-ask him. The man below stands next to this one.</span></figcaption></figure>

<h2>Round 3 — the %(n)d that came back clean</h2>
<p class="note">Judged at 1:1 first: <b>any frame with a symbol on the face was
dropped outright</b>, and so was any that read young or female. What is below is
what survived. Pick the one who looks like he works next to guard 1 and is
<b>not</b> the sharp one.</p>

<div class="grid">
%(new)s
</div>

%(dropnote)s

<details><summary>Round 2 — the nine you already saw, greyed out (this is what changed)</summary>
<p class="note">Kept for the comparison, not for the vote. Same men, same seeds;
the difference is the two strings above. <b>Do not pick from this block</b> — if
one of these faces is better than its round-3 twin, say the letter and say
"round 2" and that is a useful answer too.</p>
<div class="grid">
%(old)s
</div>
</details>

<p class="note">Nothing downstream is waiting on this. No beat plate, no motion
job and no clip is built on any of these frames until you pick, and the episode
cut is untouched.</p>

</div></body></html>
""" % {"css": CSS, "n": len(shown), "url": URL, "new": new_cards,
       "old": old_cards, "dropnote": dropped_note}

    if dry_run:
        print("dry run: %d card(s), %d bytes" % (len(shown), len(page)))
        return 0
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(page)
    print("wrote %s/index.html with %d round-3 card(s): %s"
          % (OUT, len(shown), ", ".join(l.upper() for l, _, _ in shown)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judged", required=True,
                    help="comma-separated cells that PASSED the 1:1 judge, "
                         "e.g. a,c,e,f,g,i,j30")
    ap.add_argument("--note", default="",
                    help="one <p class=note> reporting what was dropped and why")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    note = ('<p class="note">%s</p>' % a.note) if a.note else ""
    return build([t for t in a.judged.split(",") if t.strip()], note,
                 dry_run=a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
