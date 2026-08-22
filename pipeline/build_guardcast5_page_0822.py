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


AGECHECK = """
<div class="ask" style="border-color:var(--good)"><b>the sheet is still on the
card — but the age question is already answerable, so here it is on its own.</b>
This is the round-5 wording on cell C, the same man and the same seed as the
schoolboy below. <b>Is this the right age?</b> Say <code>age yes</code> or
<code>age no, too old / too young</code> and the nine men behind him are drawn
or re-cut accordingly. He has a drool bead at his mouth — that one is a
known coin-flip this recipe loses about half the time, it is paid for with spare
draws, and it is <i>not</i> what this frame is asking you about.</div>

<div class="anchor" style="border-color:var(--accent);background:#1b1a13">
<img src="%(url)s/r5-agecheck.jpg" alt="round 5 age check">
<figcaption><span class="tag">C</span><span class="desc"><b>ROUND 5, THE AGE
FIX.</b> Same seed as round 4's C in the evidence block below, one clause of
wording apart. Judge the age and the neck, ignore the mouth.</span></figcaption>
</div>
"""


def build(judged, note, dry_run=False, agecheck=False):
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

    agecheck_html = ""
    if agecheck:
        src = src_of(r5.SAMPLE, 0)
        if not os.path.exists(src):
            raise SystemExit("!! --agecheck asked for but %s is not rendered"
                             % os.path.basename(src))
        if not dry_run:
            p4._jpeg(src, os.path.join(OUT, "r5-agecheck.jpg"))
        agecheck_html = AGECHECK % {"url": URL}

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

<h1>%(h1)s</h1>

%(ask)s

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

%(agecheck)s

%(sheet)s

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
       "r4": r4_cards, "r3": r3_cards, "r2": r2_cards, "note": note,
       "agecheck": agecheck_html,
       "ask": ("""<div class="ask"><b>answer:</b> <code>guardcast5 &lt;letter&gt;</code>
&nbsp;— or <code>none, because X</code>, and X is the next round's one variable.</div>"""
               if shown else
               """<div class="ask"><b>answer:</b> <code>age yes</code> or
<code>age no, too old</code> / <code>age no, too young</code>
&nbsp;— one question only, and it is the one below. The faces to choose between
are still drawing.</div>"""),
       "h1": ("Guard 2 — round 5, %d candidates in their twenties, pick one"
              % len(shown)) if shown else
             ("Guard 2 — round 5, the age fix, one face while the sheet "
              "renders"),
       "sheet": ("""<h2>Round 5 — the %d that came back clean</h2>
<p class="note">Judged at 1:1: dropped for reading middle-aged, dropped for
reading like a schoolboy, dropped for a hand on the face, dropped for a drool
bead or a sweat drop. What is below survived all four. Pick the one who looks
like he works next to guard 1 and is <b>not</b> the sharp one.</p>

<div class="grid">
%s
</div>""" % (len(shown), new_cards)) if shown else
                ("""<h2>The other nine are on the card now</h2>
<p class="note">They are queued behind a training job on the same GPU and land
in one batch, judged at 1:1 before any of them reaches this page. Nothing is
waiting on them but this sheet.</p>""")}

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
    ap.add_argument("--judged", default="",
                    help="comma-separated cells that PASSED the 1:1 judge; "
                         "may be empty while the batch is still on the card")
    ap.add_argument("--agecheck", action="store_true",
                    help="put the round-5 SAMPLE at the top as an age-only "
                         "question. Use while the sheet is still rendering: "
                         "the age is the founder's open question and it does "
                         "not need nine more faces to be answered.")
    ap.add_argument("--note", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    note = ('<p class="note">%s</p>' % a.note) if a.note else ""
    return build([t for t in a.judged.split(",") if t.strip()], note,
                 dry_run=a.dry_run, agecheck=a.agecheck)


if __name__ == "__main__":
    sys.exit(main())
