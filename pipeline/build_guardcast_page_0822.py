#!/usr/bin/env python3
r"""Build review/ep2-guardcast-0822/ -- the guard picker page. No fluff.

    python3 pipeline/build_guardcast_page_0822.py

$0. Reads the twelve rendered stills out of farm-out/, writes JPEGs and one
index.html into review/ep2-guardcast-0822/.

THE PAGE HAS ONE JOB: the founder looks at faces and types two letters. Every
sentence that is not that is off it. The steward's reasoning, the bar, the
recipe and the fail modes all live in pipeline/derive_guardcast_0822.py and in
the twelve specs, where a reader who wants them can find them; none of it goes
on the page. The 0818 guards card was a long argued document and it took two
days to get an answer out of it -- this one is a contact sheet with a prompt.

DROPPED frames never reach the page. `DROPPED` below is filled in by the
steward AFTER scoring at 1:1 and each entry carries its reason, so the page
cannot silently show him the defect he already ruled on ("some have girls").
The dropped letters ARE named on the page in one line, because hiding that
frames were cut would misrepresent the hit rate.
"""
from __future__ import annotations

import html
import io
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_guardcast_0822 as gc              # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "review", "ep2-guardcast-0822")

# letter -> reason. Scored at 1:1 by the steward on the bar in the specs.
# R1 female read / R2 child read / R3 not one whole man -> dropped outright.
DROPPED = {
    "H": "reads late-teen, not a grown man (slight build, small features, "
         "barefoot) -- fails the founder's own bar",
    "I": "reads late-teen, not a grown man -- fails the founder's own bar",
}

# THE LABEL DESCRIBES THE PIXELS, NOT THE PROMPT. Filled in after scoring at
# 1:1, and it overrides the cell's INTENDED description wherever the two
# disagree -- which they do, because the two expression cells did not land
# where they were aimed. Labelling a frame with what we ASKED for turns the
# picker page into a claim about our prompt rather than a description of the
# picture the founder is looking at, and he would then pick a word instead of
# a face. Where an entry is absent the cell's own intent stands.
DESCRIPTIONS = {
    "A": "bald / stocky / heavy brows, flat worried mouth",
    "B": "bald / stocky / wide toothy grin",
    "C": "bald / slim / drooping brows, small frown",
    "D": "bald / slim / big grin under a worried brow",
    "E": "dark cropped hair / stocky / heavy-lidded, blank",
    "F": "dark cropped hair / stocky / eyes shut, broad happy grin",
    "G": "dark cropped hair / slim / drooping brows, small frown",
    "J": "sandy hair / stocky / toothy grin, stubble",
    "K": "bald (the sandy tag did not take) / slim / blank, drooping brows",
    "L": "sandy hair / slim / eyes shut, wide grin",
}


def _src(letter):
    jid = gc.spec_id(letter)
    return os.path.join(REPO, "farm-out", jid, "%s-cast.png" % jid)


def _jpeg(src, dst, quality=88):
    from PIL import Image
    im = Image.open(src).convert("RGB")
    im.save(dst, "JPEG", quality=quality, optimize=True,
            progressive=True)
    return im.size


CSS = """
:root { --bg:#111214; --panel:#1b1d20; --line:#31343a; --ink:#f0f2f4;
        --muted:#9aa1a9; --accent:#e0c069; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); padding:0 20px 80px;
       font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1180px; margin:0 auto; }
h1 { font-size:22px; margin:32px 0 4px; font-weight:650; }
.ask { background:var(--panel); border:1px solid var(--accent); border-radius:10px;
       padding:16px 18px; margin:16px 0 8px; }
.ask b { color:var(--accent); font-size:18px; }
.ask code { background:#0b0c0d; padding:2px 7px; border-radius:4px;
            font-size:16px; color:var(--accent); }
.note { color:var(--muted); font-size:14px; margin:10px 0 26px; }
.grid { display:grid; gap:26px 22px; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); }
figure { margin:0; }
img { width:100%; height:auto; display:block; border-radius:6px;
      border:1px solid var(--line); background:#000; }
figcaption { margin-top:8px; font-size:15px; }
.tag { display:inline-block; min-width:1.6em; padding:1px 8px; margin-right:8px;
       border-radius:4px; background:var(--accent); color:#15161a;
       font-weight:700; font-size:16px; }
.desc { color:var(--muted); }
"""


def build():
    os.makedirs(OUT, exist_ok=True)
    shown, missing = [], []
    for letter, hair, build_, face in gc.CELLS:
        if letter in DROPPED:
            continue
        src = _src(letter)
        if not os.path.exists(src):
            missing.append(letter)
            continue
        dst = os.path.join(OUT, "%s.jpg" % letter.lower())
        _jpeg(src, dst)
        shown.append((letter, DESCRIPTIONS.get(
            letter, gc.one_line(letter, hair, build_, face))))

    if missing:
        print("!! not rendered yet, omitted: %s" % ", ".join(missing))

    # ABSOLUTE URLS, NOT RELATIVE. build_site serves review/<name>/index.html
    # at the CLEAN url /review/<name> with trailingSlash:false, so a relative
    # `a.jpg` on that page resolves to /review/a.jpg and 404s. qa_local caught
    # exactly this on the first build of this page; every other review card in
    # the tree writes /review/<name>/<file> for the same reason.
    cards = "\n".join(
        '<figure><img src="/review/ep2-guardcast-0822/%s.jpg" '
        'alt="candidate %s" loading="lazy">'
        '<figcaption><span class="tag">%s</span>'
        '<span class="desc">%s</span></figcaption></figure>'
        % (l.lower(), l, l, html.escape(d)) for l, d in shown)

    dropped_line = ""
    if DROPPED:
        dropped_line = (
            '<p class="note">Not shown: %s — cut at 1:1 before you saw them '
            '(%s).</p>'
            % (", ".join(sorted(DROPPED)),
               "; ".join("%s %s" % (k, html.escape(v))
                         for k, v in sorted(DROPPED.items()))))

    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guard casting — pick two</title>
<style>%s</style></head><body><div class="wrap">
<h1>Guard casting — %d candidates</h1>
<div class="ask"><b>answer:</b> <code>guardcast &lt;letter&gt;</code>
&nbsp;or&nbsp; <code>guardcast &lt;letter&gt;+&lt;letter&gt;</code>
for guard&nbsp;1 + guard&nbsp;2.</div>
<p class="note">Grown men, dumb faces, the show's guard clothes. Same pose,
same wardrobe, same recipe in all of them — only the hair, the build and the
face change. Your pick becomes the guards' reference image.</p>
%s
<div class="grid">
%s
</div>
</div></body></html>
""" % (CSS, len(shown), dropped_line, cards)

    p = os.path.join(OUT, "index.html")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(page)
    print("wrote %s  (%d candidate(s))" % (os.path.relpath(p, REPO), len(shown)))
    return p, shown, missing


if __name__ == "__main__":
    build()
