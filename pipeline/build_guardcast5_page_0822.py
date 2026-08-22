#!/usr/bin/env python3
r"""ROUND 5 GOES ON TOP OF THE SAME SHEET.

    python3 pipeline/build_guardcast5_page_0822.py --judged a,d,f,h,i \
        [--note "..."] [--dry-run]

$0. Reads the judged round-5 stills out of farm-out/, writes them as
`r5-<cell>.jpg`, and rewrites review/ep2-guardcast2-0822/index.html IN PLACE.

WHY THE SAME URL FOR A FIFTH TIME. The founder is on /review/ep2-guardcast2-0822
and his note -- "the new guard generations look a bit like tooo grown adults" --
is about the men on it. Round 5 goes above the fold; every superseded round
collapses and greys beneath it in order, so the age walk (forties, then
seventeen, then this) is one page and one scroll.

ROUND 4 IS SHOWN AS EVIDENCE AND NOT AS CANDIDATES. Its batch was pulled at the
sample gate for reading seventeen. Two of its six drawn frames go on the page
anyway: C, because a clean schoolboy is the clearest possible picture of what
the word `young` did, and D, because D is the frame that proved the recipe could
still land a man and is therefore the reason round 5 exists. Neither is
selectable.
"""
from __future__ import annotations

import argparse
import html
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_guardcast5_0822 as r5                                 # noqa: E402
import derive_guardcast4_0822 as r4                                 # noqa: E402
import build_guardcast4_page_0822 as p4                             # noqa: E402

OUT = p4.OUT
URL = p4.URL
CSS = p4.CSS
card = p4.card

# Round 4's two evidence frames, published as `r4-<cell>.jpg`.
ROUND4 = (
    ("c", "cropped ginger hair / round heavy face — CLEAN, and seventeen. "
          "This is what the word 'young' did."),
    ("d", "shaved head / broad flat face / thick neck — the one round-4 frame "
          "that came back a man. Round 5 is built on this."),
)

DESC = {l: b.replace(", ", " / ") for l, b in r5.CELLS}


def parse_cell(token):
    token = token.strip().lower()
    off = str(r5.EXTRA_OFFSET)
    if token.endswith(off):
        return token[:-len(off)], r5.EXTRA_OFFSET
    return token, 0


def src_of(letter, offset, mod=r5):
    jid = mod.spec_id(letter, offset)
    return os.path.join(REPO, "farm-out", jid, "%s-%s.png" % (jid, mod.ARM))


def build(judged, note, dry_run=False):
    os.makedirs(OUT, exist_ok=True)
    shown, missing = [], []
    for token in judged:
        letter, offset = parse_cell(token)
        if letter not in DESC:
            raise SystemExit("!! %r is not a round-5 cell" % token)
        src = src_of(letter, offset)
        if not os.path.exists(src):
            missing.append(token)
            continue
        name = "r5-%s.jpg" % letter
        if not dry_run:
            p4._jpeg(src, os.path.join(OUT, name))
        shown.append((letter, name, DESC[letter]))
    if missing:
        raise SystemExit("!! judged cells with no rendered png: %s"
                         % ", ".join(missing))
    shown.sort(key=lambda t: t[0])

    r4_shown = []
    for letter, desc in ROUND4:
        src = src_of(letter, 0, mod=r4)
        if not os.path.exists(src):
            continue
        if not dry_run:
            p4._jpeg(src, os.path.join(OUT, "r4-%s.jpg" % letter))
        r4_shown.append((letter, desc))

    new_cards = "\n".join(card(l, n, d) for l, n, d in shown)
    r4_cards = "\n".join(card(l, "r4-%s.jpg" % l, d, cls="old")
                         for l, d in r4_shown)
    r3_cards = "\n".join(card(l, "r3-%s.jpg" % l, d, cls="old")
                         for l, d in p4.ROUND3)
    r2_cards = "\n".join(card(l, "%s.jpg" % l, d, cls="old")
                         for l, d in p4.ROUND2)

    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guard 2 — round 5, pick one</title>
<style>%(css)s</style></head><body><div class="wrap">

<h1>Guard 2 — round 5, %(n)d candidates in their twenties, pick one</h1>

<div class="ask"><b>answer:</b> <code>guardcast5 &lt;letter&gt;</code>
&nbsp;— or <code>none, because X</code>, and X is the next round's one variable.</div>

<div class="settled"><b>YOU WERE RIGHT THAT THEY WERE TOO OLD, AND THE PROMPT WAS
ASKING FOR IT.</b> Round 3 opened with the words <i>a grown guard man, mature
male face</i>, and half the men carried a moustache, grey streaks, stubble or a
receding hairline in their own description. It drew what it was told to.</div>

<div class="ask" style="border-color:#ff9a86"><b>the first fix overshot, and it
never reached you.</b> Swapping in <i>a young guard man, early twenties</i> drew
a <b>schoolboy</b> — that one word means "sixteen-year-old protagonist" to this
model, and it was strong enough to erase the heavy jaw and thick neck the same
prompt asked for. The batch was killed after the first frame; two of its six
drawn frames are kept below as evidence. What is above the fold is the second
fix: <b>a guard man in his twenties, adult male face, thick neck</b> — the word
<i>young</i> gone, the number kept. Same men, same clothes, same framing, same
seeds, same negative that got the sweat and drool off their faces.</div>

<div class="anchor">
<img src="%(url)s/guard1.jpg" alt="guard 1, the age you already ruled">
<figcaption><span class="tag" style="background:var(--good)">1</span><span class="desc"><b>THE AGE TO MATCH.</b> Guard 1, as you ruled him. Every face below was judged against this one and dropped if it read older <i>or</i> younger. Guard 2 is not this man — he just has to be the same age as him.</span></figcaption>
</div>

<h2>Round 5 — the %(n)d that came back clean</h2>
<p class="note">Judged at 1:1: dropped for reading middle-aged, dropped for
reading like a schoolboy, dropped for a hand on the face, dropped for a drool
bead or a sweat drop. What is below survived all four. Pick the one who looks
like he works next to guard 1 and is <b>not</b> the sharp one.</p>

<div class="grid">
%(new)s
</div>

%(note)s

<details><summary>Round 4 — the overshoot, killed after one frame (evidence, not candidates)</summary>
<p class="note">Two of the six frames that drew before the batch was pulled.
<b>Do not pick from this block.</b></p>
<div class="grid">
%(r4)s
</div>
</details>

<details><summary>Round 3 — the five you called too old (greyed, for the comparison)</summary>
<p class="note">Same men, same seeds, one clause of wording apart from what is at
the top. <b>Do not pick from this block</b> — it is here so you can see whether
the age actually moved. If a round-3 face is better than its round-5 twin, say
the letter and say "round 3" and that is a useful answer too.</p>
<div class="grid">
%(r3)s
</div>
</details>

<details><summary>Round 2 — the nine with gas and liquid on their faces (greyed)</summary>
<p class="note">Kept only so the chain is legible. This is the round whose sweat
drops and drool beads you flagged; round 3 fixed those and every round since has
kept the fix.</p>
<div class="grid">
%(r2)s
</div>
</details>

<p class="note">Nothing downstream is waiting on this. No beat plate, no motion
job and no clip is built on any of these frames until you pick, and the episode
cut is untouched.</p>

</div></body></html>
""" % {"css": CSS, "n": len(shown), "url": URL, "new": new_cards,
       "r4": r4_cards, "r3": r3_cards, "r2": r2_cards, "note": note}

    if dry_run:
        print("dry run: %d card(s), %d bytes" % (len(shown), len(page)))
        return 0
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(page)
    print("wrote %s/index.html with %d round-5 card(s): %s"
          % (OUT, len(shown), ", ".join(l.upper() for l, _, _ in shown)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judged", required=True)
    ap.add_argument("--note", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    note = ('<p class="note">%s</p>' % a.note) if a.note else ""
    return build([t for t in a.judged.split(",") if t.strip()], note,
                 dry_run=a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
