#!/usr/bin/env python3
r"""ROUND 4 GOES ON TOP OF THE SAME SHEET, AGAIN.

    python3 pipeline/build_guardcast4_page_0822.py --judged a,c,e,f,h,j \
        [--note "..."] [--dry-run]

$0. Reads the judged round-4 stills out of farm-out/, writes JPEGs as
`r4-<cell>.jpg` and rewrites review/ep2-guardcast2-0822/index.html IN PLACE.

WHY THE SAME URL FOR A FOURTH TIME. The founder is on /review/ep2-guardcast2-0822
right now and his note -- "the new guard generations look a bit like tooo grown
adults" -- is about the five men on it. A new address would make him find the
comparison himself. Round 4 goes above the fold; round 3 collapses and greys
directly beneath so his own sentence keeps its subject; round 2 collapses under
that. Nothing already published changes address: a.jpg..j.jpg and r3-*.jpg stay
exactly where they are.

THE ANCHOR IS PROMOTED TO THE TOP OF THE PAGE. Guard 1 was a footnote on the
round-3 sheet. This round is about AGE and guard 1 is the age ruling the founder
already made, so his frame sits beside the candidates as the thing to measure
against rather than below them as a reminder.
"""
from __future__ import annotations

import argparse
import html
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_guardcast4_0822 as r4                                 # noqa: E402

OUT = os.path.join(REPO, "review", "ep2-guardcast2-0822")
URL = "/review/ep2-guardcast2-0822"

# HISTORY, COPIED AND NOT RE-DERIVED. These two blocks describe frames that are
# already on disk and already seen; a deriver moving under them would relabel a
# picture the founder has in his head.
ROUND3 = (
    ("a", "thick dark brown hair / heavy square jaw / thick neck"),
    ("e", "shaggy black hair / gaunt narrow face / big ears"),
    ("f", "grey-streaked brown hair / thick moustache / jowly"),
    ("h", "curly black hair / wide square face / thick neck"),
    ("j", "short red hair, freckles / blunt chin"),
)

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

# Round 4's own cells, read off the deriver so the caption cannot disagree with
# the prompt that drew the face.
DESC = {l: b.replace(", ", " / ") for l, b in r4.CELLS}


def parse_cell(token):
    """`a` -> ('a', 0); `j40` -> ('j', 40)."""
    token = token.strip().lower()
    if token.endswith(str(r4.RECOVERY_OFFSET)):
        return token[:-len(str(r4.RECOVERY_OFFSET))], r4.RECOVERY_OFFSET
    return token, 0


def src_of(letter, offset):
    jid = r4.spec_id(letter, offset)
    return os.path.join(REPO, "farm-out", jid, "%s-%s.png" % (jid, r4.ARM))


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
/* THE ANCHOR IS A CARD IN THE GRID THIS ROUND, NOT A FOOTNOTE. The question is
   age and this is the age ruling; it has to sit at eye level with the men. */
.anchor { border:1px solid var(--good); border-radius:10px; padding:14px;
          background:#131a16; max-width:360px; margin:6px 0 4px; }
.anchor img { border-color:var(--good); }
details { margin:14px 0; color:var(--muted); font-size:14.5px; }
summary { cursor:pointer; color:var(--accent); font-size:16px; }
/* THE SUPERSEDED ROUNDS ARE GREYED, NOT HIDDEN. */
.old { opacity:0.45; filter:saturate(0.55); }
.old:hover { opacity:0.8; filter:none; }
.old .tag { background:#5a5f68; color:#cfd3d8; }
"""


def card(letter, url_name, desc, cls=""):
    tag = letter.upper()
    return ('<figure%s><img src="%s/%s" alt="candidate %s" loading="lazy">'
            '<figcaption><span class="tag">%s</span>'
            '<span class="desc">%s</span></figcaption></figure>'
            % (' class="%s"' % cls if cls else "", URL, url_name, tag, tag,
               html.escape(desc)))


def build(judged, note, dry_run=False):
    os.makedirs(OUT, exist_ok=True)
    shown, missing = [], []
    for token in judged:
        letter, offset = parse_cell(token)
        if letter not in DESC:
            raise SystemExit("!! %r is not a round-4 cell" % token)
        src = src_of(letter, offset)
        if not os.path.exists(src):
            missing.append(token)
            continue
        name = "r4-%s.jpg" % letter
        if not dry_run:
            _jpeg(src, os.path.join(OUT, name))
        shown.append((letter, name, DESC[letter]))
    if missing:
        raise SystemExit("!! judged cells with no rendered png: %s"
                         % ", ".join(missing))
    shown.sort(key=lambda t: t[0])

    new_cards = "\n".join(card(l, n, d) for l, n, d in shown)
    r3_cards = "\n".join(card(l, "r3-%s.jpg" % l, d, cls="old")
                         for l, d in ROUND3)
    r2_cards = "\n".join(card(l, "%s.jpg" % l, d, cls="old")
                         for l, d in ROUND2)

    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guard 2 — round 4, pick one</title>
<style>%(css)s</style></head><body><div class="wrap">

<h1>Guard 2 — round 4, %(n)d candidates in their twenties, pick one</h1>

<div class="ask"><b>answer:</b> <code>guardcast4 &lt;letter&gt;</code>
&nbsp;— or <code>none, because X</code>, and X is the next round's one variable.</div>

<div class="settled"><b>YOU WERE RIGHT THAT THEY WERE TOO OLD, AND THE PROMPT WAS
ASKING FOR IT.</b> Round 3 opened with the words <i>a grown guard man, mature
male face</i>, and half the men carried a moustache, grey streaks, stubble or a
receding hairline in their own description. It drew exactly what it was told to.
Round 4 changes that one clause to <b>a young guard man, early twenties, adult
male build, broad shoulders</b> and strips every middle-age word out of the ten
men. Nothing else moved: same clothes, same framing, same background, same
seeds, and the same negative that got the sweat and drool off their faces last
round.</div>

<div class="anchor">
<img src="%(url)s/guard1.jpg" alt="guard 1, the age you already ruled">
<figcaption><span class="tag" style="background:var(--good)">1</span><span class="desc"><b>THE AGE TO MATCH.</b> Guard 1, as you ruled him. Every face below was judged against this one and dropped if it read older <i>or</i> younger. Guard 2 is not this man — he just has to be the same age as him.</span></figcaption>
</div>

<h2>Round 4 — the %(n)d that came back clean</h2>
<p class="note">Judged at 1:1: dropped for reading middle-aged, dropped for
reading like a schoolboy, dropped for a hand on the face, dropped for a sweat
drop or a drool bead. What is below survived all four. Pick the one who looks
like he works next to guard 1 and is <b>not</b> the sharp one.</p>

<div class="grid">
%(new)s
</div>

%(note)s

<details><summary>Round 3 — the five you just called too old (greyed, for the comparison)</summary>
<p class="note">Same men, same seeds, one clause of wording apart. <b>Do not pick
from this block</b> — it is here so you can see whether the age actually moved.
If a round-3 face is better than its round-4 twin, say the letter and say
"round 3" and that is a useful answer too.</p>
<div class="grid">
%(r3)s
</div>
</details>

<details><summary>Round 2 — the nine with gas and liquid on their faces (greyed)</summary>
<p class="note">Kept only so the chain is legible. This is the round whose sweat
drops and drool beads you flagged; round 3 fixed those and round 4 keeps the fix.</p>
<div class="grid">
%(r2)s
</div>
</details>

<p class="note">Nothing downstream is waiting on this. No beat plate, no motion
job and no clip is built on any of these frames until you pick, and the episode
cut is untouched.</p>

</div></body></html>
""" % {"css": CSS, "n": len(shown), "url": URL, "new": new_cards,
       "r3": r3_cards, "r2": r2_cards, "note": note}

    if dry_run:
        print("dry run: %d card(s), %d bytes" % (len(shown), len(page)))
        return 0
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(page)
    print("wrote %s/index.html with %d round-4 card(s): %s"
          % (OUT, len(shown), ", ".join(l.upper() for l, _, _ in shown)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judged", required=True,
                    help="comma-separated cells that PASSED the 1:1 judge")
    ap.add_argument("--note", default="",
                    help="one <p class=note> reporting what was dropped and why")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    note = ('<p class="note">%s</p>' % a.note) if a.note else ""
    return build([t for t in a.judged.split(",") if t.strip()], note,
                 dry_run=a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
