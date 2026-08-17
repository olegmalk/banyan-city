#!/usr/bin/env python3
"""Static-site generator — the show first, the receipts one fold down.

Reads every genome under genomes/ and renders _site/:
    index.html                the gate: logline, season rail, the whole tree
    watch.html                the vertical binge feed (season 1, in order)
    create.html               write your own episode (on-page, no git)
    city.html                 Promise + Guidelines + Glossary
    machine.html              how the loop runs
    trials/index.html         the open video-model bake-off
    <genome>/<slug>.html      one page per episode: film, then script, then receipts

Design constraints:
  - no build framework, no client JS *required* (the binge feed adds a tiny
    progressive-enhancement script and works fine without it)
  - one shared visual language: pipeline/site_theme.py (never fork the palette)
  - works for any genome that passes lint_genome.py (a fork changes
    content, not this script)
  - a non-git citizen can watch the show, read it, and react (Phase 1)
  - a stranger from TikTok meets story words first; leaf/sap/trunk/T0–T3 are
    translated in place and only kept inside the technical drawers
"""

import hashlib
import html
import json
import os
import re
import shutil
import struct
import subprocess
from pathlib import Path

import markdown
import yaml

import build_commit
import licence_gate as lg
import repo_slug
from site_theme import THEME_CSS

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_site"
# Forkable, and platform-agnostic: this used to read GITHUB_REPOSITORY with a
# hardcoded default, which Actions sets and VERCEL DOES NOT — so after the
# 2026-08-10 owner change the Pages mirror would have corrected itself while
# banyan.city, which builds on Vercel, kept publishing the old owner. See
# pipeline/repo_slug.py; the question is asked in exactly one place now.
GH_REPO = repo_slug.GH_REPO
REPO_URL = repo_slug.REPO_URL
REPO_NAME = GH_REPO.split("/")[-1]
CANONICAL = "https://banyan.city"  # canonical host; Pages stays as free mirror
MD = markdown.Markdown(extensions=["tables", "fenced_code"])
FFMPEG = shutil.which("ffmpeg")  # optional: posters degrade to no poster

# The stranger's vocabulary: every internal tier gets a plain word.
TIER_WORDS = {"T0": "script", "T1": "storyboard", "T2": "animatic", "T3": "film"}
# Why an alternate cut exists, when its own metadata doesn't say.
WHY_BY_TIER = {
    "T3": "an earlier filmed cut of the same script — kept so you can see what changed",
    "T2": "the voiced animatic: the script on screen, made before any footage existed",
    "T1": "the storyboard pass — one frame per beat",
}
LEGEND = ('<p class="legend"><b>version</b> = one render of an episode · '
          '<b>sap</b> = your reactions · <b>canon</b> = the cut that leads the story · '
          '<b>branch</b> = someone else’s continuation, still alive</p>')

# Shared language lives in site_theme.py; only page-specific rules go here.
CSS = THEME_CSS + """
/* ---- the gate ---- */
.hero { text-align: center; margin: 1.2rem 0 2.4rem; }
.hero .seal { font-size: 2.2rem; line-height: 1; }
.hero h1 { margin: .2rem 0 .5rem; }
.logline { font-family: var(--display); font-size: clamp(1.18rem, 4.4vw, 1.5rem);
  line-height: 1.4; color: var(--ink); max-width: 22em; margin: .6rem auto 0;
  text-wrap: pretty; }
.hero .sub { color: var(--muted); font-size: 1rem; max-width: 26em; margin: .7rem auto 0; }
.hero .cta { margin: 1.1rem 0 .2rem; }
.smallprint { font: 500 .8rem/1.6 var(--mono); color: var(--faint); max-width: 40em; }
.smallprint a { color: var(--muted); }

/* ---- season rail: bigger thumbs, episode numbers, real frames ---- */
.season { display: flex; gap: .9rem; overflow-x: auto; padding: .4rem .2rem 1rem;
  scroll-snap-type: x proximity; -webkit-overflow-scrolling: touch; }
.season figure { margin: 0; flex: 0 0 168px; scroll-snap-align: start; }
.season video { width: 168px; aspect-ratio: 9 / 16; object-fit: cover; display: block;
  background: var(--code-bg); border: 1px solid var(--line); border-radius: 14px; }
.season figcaption { font: 600 .74rem/1.45 var(--mono); color: var(--muted); margin-top: .45rem; }
.season .n { color: var(--sap); }

/* ---- how it works: three plain cards ---- */
.how { display: grid; gap: .8rem; grid-template-columns: 1fr; margin: 1rem 0; }
@media (min-width: 620px) { .how { grid-template-columns: repeat(3, 1fr); } }
.how .card .k { font: 700 .7rem/1 var(--mono); letter-spacing: .16em; text-transform: uppercase;
  color: var(--sap); }
.how .card p { margin: .45rem 0 0; font-size: .95rem; color: var(--muted); }

/* ---- the fork at the tip, as an event ---- */
.fork { background: linear-gradient(180deg, rgba(255,199,106,.10), var(--panel));
  border: 1px solid var(--sap-deep); border-radius: 16px; padding: 1rem 1.15rem; }
.fork .k { font: 700 .7rem/1 var(--mono); letter-spacing: .16em; text-transform: uppercase;
  color: var(--sap); }
.fork p { margin: .5rem 0 0; font-size: .96rem; }

/* ---- the tree: a rail on wide screens, a flat list on a phone ---- */
.tree { list-style: none; padding-left: 0; margin: 1.2rem 0; }
.tree ul { list-style: none; padding-left: .85rem; border-left: 2px solid var(--leaf-dim);
  margin-left: .55rem; }
.tree li { margin: .7rem 0; }
.tree .card { padding: .85rem 1rem; }
.tree .lineage { font: 600 .72rem/1.5 var(--mono); color: var(--faint);
  letter-spacing: .04em; text-transform: uppercase; margin-bottom: .3rem; }
@media (max-width: 600px) {
  /* depth as indentation is unreadable at 390px — flatten, keep the parent label */
  .tree ul { padding-left: 0; margin-left: 0; border-left: 0; }
  .tree .card .meta { line-height: 1.9; }
}

/* ---- the machine strip: a card with an icon, not another dashed box ---- */
.strip { display: flex; gap: .9rem; align-items: flex-start; padding: 1rem 1.15rem; }
.strip .ic { font-size: 1.5rem; line-height: 1.2; }
.strip p { margin: .35rem 0 0; font-size: .95rem; color: var(--muted); }

/* ---- episode page ---- */
.epnav { display: flex; flex-wrap: wrap; gap: .6rem; margin: 1.4rem 0; }
.epnav a { flex: 1 1 240px; padding: .7rem .9rem; border: 1px solid var(--line);
  border-radius: 12px; background: var(--panel); }
.epnav .k { display: block; font: 700 .68rem/1.6 var(--mono); letter-spacing: .14em;
  text-transform: uppercase; color: var(--faint); }
.actions { margin: 1rem 0 .2rem; }
.screenplay p > strong:first-child { display: block; font: 700 .78rem/1.7 var(--mono);
  letter-spacing: .1em; color: var(--sap); }
.drawer-body h2 { font-size: 1.05rem; margin: 1.5rem 0 .4rem; }
.drawer-body h3 { font-size: .98rem; }
.drawer-body > :first-child { margin-top: .2rem; }
.cuts { display: grid; gap: 1rem; grid-template-columns: 1fr; }
@media (min-width: 620px) { .cuts { grid-template-columns: 1fr 1fr; } }
.cuts .phone { margin: 0 auto; max-width: 240px; }
.cuts figcaption { text-align: left; }
.cuts .why { color: var(--muted); font-family: var(--body); font-size: .88rem;
  letter-spacing: 0; text-transform: none; display: block; margin-top: .3rem; }

/* ---- the walk: watching IS walking the tree ---- */
body.walk main { max-width: 560px; }
.trail { font: 700 .72rem/2 var(--mono); letter-spacing: .12em; text-transform: uppercase;
  color: var(--faint); margin: .2rem 0 0; }
.trail a { color: var(--muted); }
.trail .here { color: var(--sap); }
.walk-meta { font: 600 .78rem/1.7 var(--mono); color: var(--faint); text-align: center;
  margin: .2rem 0 0; }
.phone.big { max-width: 360px; }
.cliff { text-align: center; margin: 2.2rem 0 1rem; }
.cliff .k { font: 700 .68rem/1 var(--mono); letter-spacing: .22em; text-transform: uppercase;
  color: var(--faint); }
.cliff .q { font-family: var(--display); font-style: italic;
  font-size: clamp(1.3rem, 5vw, 1.7rem); line-height: 1.35; margin: .7rem auto 0;
  max-width: 20em; text-wrap: balance; }
.fork-line { text-align: center; font: 700 .74rem/1.6 var(--mono); letter-spacing: .14em;
  text-transform: uppercase; color: var(--sap); margin: 1.4rem 0 .2rem; }
.doors { display: grid; gap: .9rem; grid-template-columns: 1fr; margin: 1rem 0 1.6rem; }
a.door { display: flex; gap: .9rem; align-items: center; padding: .8rem .95rem;
  background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 16px; color: var(--ink);
  transition: transform .15s ease, border-color .15s ease; }
a.door:hover { text-decoration: none; transform: translateY(-2px); border-color: var(--sap); }
a.door img, a.door .ph { width: 62px; aspect-ratio: 9 / 16; object-fit: cover; flex: 0 0 62px;
  border-radius: 10px; border: 1px solid var(--line); background: var(--code-bg); }
a.door .ph { display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }
a.door .t { display: block; font-family: var(--display); font-size: 1.08rem; line-height: 1.25; }
a.door .d { display: block; color: var(--muted); font-size: .85rem; margin-top: .2rem; }
a.door .go { display: block; font: 700 .68rem/1 var(--mono); letter-spacing: .14em;
  text-transform: uppercase; color: var(--sap); margin-top: .45rem; }
a.door.canon { border-color: var(--sap-deep);
  background: linear-gradient(180deg, rgba(255,199,106,.09), var(--panel)); }
.doors.now a.door { border-color: var(--sap); }
.tip { text-align: center; padding: 1.6rem 1.15rem; margin: 1.2rem 0; }
.tip .seed { font-size: 2rem; line-height: 1; }
.walk-foot { text-align: center; font: 600 .78rem/2 var(--mono); color: var(--faint);
  margin-top: 1.6rem; }
.walk-foot a { color: var(--muted); }
@media (prefers-reduced-motion: reduce) { a.door { transition: none; } }

/* ---- the binge feed: one vertical snap column ---- */
html:has(body.feed) { scroll-snap-type: y proximity; }
body.feed main { max-width: 460px; }
.ep { min-height: 100dvh; display: flex; flex-direction: column; justify-content: center;
  scroll-snap-align: center; scroll-snap-stop: always; padding: .5rem 0 1rem; }
.ep .phone { max-width: 340px; margin: .6rem auto; }
.ep .bar { font: 700 .72rem/1 var(--mono); letter-spacing: .18em; text-transform: uppercase;
  color: var(--sap); text-align: center; }
.ep figcaption a { color: var(--leaf); }

/* ---- trials: nine columns become cards on a phone ---- */
.clips { display: flex; flex-wrap: wrap; gap: 1rem; margin: 1rem 0; }
.clips .phone { margin: 0; flex: 1 1 200px; max-width: 232px; }
.scores { font-size: .86em; }
.scores td[data-label="notes"] { color: var(--muted); }
@media (max-width: 640px) {
  .scores { display: block; }
  .scores thead { display: none; }
  .scores tbody { display: block; }
  .scores tr { display: block; background: var(--panel); border: 1px solid var(--line);
    border-radius: 14px; padding: .5rem .8rem; margin: .8rem 0; }
  .scores td { display: flex; justify-content: space-between; gap: 1rem;
    border-bottom: 1px solid var(--line-soft); padding: .35rem 0; }
  .scores td:last-child { border-bottom: 0; display: block; }
  .scores td::before { content: attr(data-label); font: 700 .68rem/1.7 var(--mono);
    letter-spacing: .1em; text-transform: uppercase; color: var(--faint); }
}

/* ---- create: numbered steps + the on-page submission form ---- */
.steps { list-style: none; counter-reset: step; padding: 0; margin: 1.2rem 0; }
.steps li { counter-increment: step; position: relative; padding: .95rem 1.1rem .95rem 3.1rem;
  background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 16px; margin: .7rem 0; }
.steps li::before { content: counter(step); position: absolute; left: 1rem; top: .95rem;
  font: 700 .95rem/1.55 var(--mono); color: var(--sap-ink); background: var(--sap);
  width: 1.6rem; height: 1.6rem; text-align: center; border-radius: 999px; }
.steps b { font-family: var(--display); font-size: 1.05rem; }
form.compose { background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 18px; padding: 1.1rem 1.15rem; margin: 1.2rem 0; }
form.compose label { display: block; margin: .9rem 0 0; font: 700 .74rem/1.9 var(--mono);
  letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }
form.compose input, form.compose textarea { width: 100%; margin-top: .3rem;
  background: var(--code-bg); color: var(--ink); border: 1px solid var(--line);
  border-radius: 10px; padding: .6rem .7rem; font: 16px/1.55 var(--body); }
form.compose textarea { font: 15px/1.6 var(--mono); resize: vertical; }
form.compose button { margin-top: 1rem; border: 0; cursor: pointer; }
form.compose .hint { font: 500 .78rem/1.6 var(--mono); color: var(--faint); margin: .5rem 0 0; }

/* ---- the review area: unlisted working cuts (D17) ---- */
/* The stamp is loud on purpose. A cut the author has not passed must never be
   mistakable for the episode, and the one place that could happen is a page
   showing it full-width with no caption in view. */
.stamp { display: block; background: rgba(224,115,107,.12); border: 1px solid #7a3b36;
  border-radius: 12px; padding: .7rem .95rem; margin: 0 0 1rem;
  font: 700 .78rem/1.6 var(--mono); letter-spacing: .06em; color: #e0736b; }
.stamp b { color: #f0a49e; }
.cut { margin: 2.2rem 0; padding-top: 1.6rem; border-top: 1px solid var(--line); }
.cut .film { max-width: 340px; }
.cut .film video { width: 100%; aspect-ratio: 9 / 16; display: block; border-radius: 14px;
  background: var(--code-bg); border: 1px solid var(--line); }
.cut .facts { font: 600 .78rem/1.7 var(--mono); color: var(--faint); margin: .5rem 0 0; }
@media (min-width: 760px) {
  .cut .split { display: grid; grid-template-columns: 340px 1fr; gap: 1.6rem; align-items: start; }
}
.cut ul { padding-left: 1.1rem; }
.cut ul li { margin: .35rem 0; color: var(--muted); font-size: .95rem; }
.pair { margin: 1.6rem 0; padding: 1rem 1.15rem; background: var(--panel);
  border: 1px solid var(--line); border-radius: 16px; }
.pair h3 { margin: 0 0 .4rem; }
.pair .two { display: flex; flex-wrap: wrap; gap: 1rem; margin: .9rem 0; }
.pair .two figure { margin: 0; flex: 1 1 200px; max-width: 240px; }
.pair .two video { width: 100%; aspect-ratio: 9 / 16; display: block; border-radius: 12px;
  background: var(--code-bg); border: 1px solid var(--line); }
.pair .two figcaption { font: 600 .74rem/1.55 var(--mono); color: var(--faint); margin-top: .4rem; }
.pair .two .k { display: block; color: var(--ink); letter-spacing: .1em; text-transform: uppercase; }
.pair .why { color: var(--muted); font-size: .94rem; }

/* ---- the morning checklist: the questions, above the films that raised them ---- */
/* Ordered by what it costs him to answer, not by what it cost us to make. The
   page below is the evidence; this is the ask. */
.check { margin: 1.4rem 0; padding: 1.1rem 1.2rem; background: var(--panel);
  border: 1px solid var(--line); border-left: 3px solid var(--sap); border-radius: 16px; }
.check > h3 { margin: .1rem 0 .5rem; font-size: 1.06rem; }
.check .n { display: inline-block; min-width: 1.6rem; margin-right: .4rem; color: var(--sap);
  font: 800 .82rem/1.6 var(--mono); letter-spacing: .04em; vertical-align: .12em; }
.check .why, .check p { color: var(--muted); font-size: .94rem; }
.check .two { display: flex; flex-wrap: wrap; gap: 1rem; margin: .9rem 0 .2rem; }
.check .two figure { margin: 0; flex: 1 1 190px; max-width: 230px; }
.check .two video { width: 100%; aspect-ratio: 9 / 16; display: block; border-radius: 12px;
  background: var(--code-bg); border: 1px solid var(--line); }
.check .two figcaption { font: 600 .74rem/1.55 var(--mono); color: var(--faint); margin-top: .4rem; }
.check .two .k { display: block; color: var(--ink); letter-spacing: .1em; text-transform: uppercase; }
/* A contact sheet is wide and detailed — it gets the full column and its own
   scroll rather than being squeezed into a phone-shaped box like a clip. */
.check .sheets figure { margin: 0 0 1.1rem; max-width: none; overflow-x: auto; }
/* The anchor is the tap target for "open this full size", so it has to be the
   size of the picture rather than of an inline box around it. */
.check .sheets a { display: block; }
.check .sheets img { display: block; width: 100%; min-width: 520px; height: auto;
  border-radius: 12px; border: 1px solid var(--line); background: var(--code-bg); }
/* Same caption shape as a clip's. Without this the sheets inherited nothing and
   the label ran straight into the note — "b03-r3-s0..s3rejected round on top". */
.check .sheets figcaption { font: 600 .74rem/1.55 var(--mono); color: var(--faint);
  margin-top: .4rem; }
.check .sheets .k { display: block; color: var(--ink); letter-spacing: .1em;
  text-transform: uppercase; }
/* Story context for the beats ON a sheet. He cannot judge a candidate against a
   script he cannot see, so each beat's one line of plot and its one load-bearing
   visual sit under the picture they belong to rather than in a chat message. */
.check .sheets .beatctx { list-style: none; margin: .55rem 0 0; padding: 0;
  border-top: 1px solid var(--line); }
.check .sheets .beatctx li { padding: .45rem 0; border-bottom: 1px solid var(--line);
  font: 400 .74rem/1.6 var(--mono); color: var(--faint); }
.check .sheets .beatctx b { display: block; color: var(--ink); font-weight: 700;
  letter-spacing: .08em; text-transform: uppercase; }
.check .sheets .beatctx span { display: block; }
.check .sheets .beatctx span i { font-style: normal; color: var(--ink);
  letter-spacing: .06em; }
.check .voices figure { margin: 0 0 .8rem; max-width: none; }
.check .voices audio { width: 100%; max-width: 420px; display: block; }
/* Opens a labelled run of items — episode 2's questions are real but they do
   not block the cut, so they are visibly a second block and not more of the first. */
h3.run { margin: 2.4rem 0 .2rem; padding-top: 1.2rem; border-top: 1px solid var(--line);
  font: 700 .78rem/1.6 var(--mono); letter-spacing: .14em; text-transform: uppercase;
  color: var(--faint); }
/* Absent evidence is stated in the item that needed it, never left to be
   inferred from a section that is quietly shorter than it should be. */
.check .gap { border: 1px dashed var(--sap-deep); background: var(--panel-2);
  border-radius: 12px; padding: .7rem .9rem; margin: .8rem 0 .2rem;
  font-size: .92rem; color: var(--muted); }
/* The left bar carries the item's state so the shape of the morning is legible
   before a word is read: amber = he has to answer, green = already answered and
   only being confirmed, dim = nothing to do here yet. */
.check.settled { border-left-color: var(--leaf); }
.check.gapbar { border-left-color: var(--sap-deep); }

/* ---- queue first, record behind (2026-08-09) ----
   His words: "why is banyan.city/review so big and long? its hard to find what
   to do". Everything here exists to answer that in the first screenful: the
   count, then the cards, then a fold over every word that is already decided. */
.count { font: 700 1.02rem/1.6 var(--body); color: var(--ink); margin: .3rem 0 1.4rem; }
.count b { color: var(--sap); }
.count .sub { display: block; font: 600 .8rem/1.7 var(--mono); color: var(--faint);
  letter-spacing: .04em; text-transform: uppercase; }
.block { margin: 2.2rem 0; padding-top: 1.6rem; border-top: 1px solid var(--line); }
.block > h2 { margin: 0 0 .3rem; }
.block > .said { color: var(--muted); font-size: .95rem; margin: .2rem 0 1.2rem; }
/* One standing line instead of the same warning repeated on nine cards. */
.standing { margin: 0 0 1.2rem; }
/* A queue card is a tight thing on purpose: ask, where, how, and a fold. */
.check.q > .sum { color: var(--ink); font-size: .98rem; margin: .1rem 0 .6rem; }
.check .where, .check .act { margin: .35rem 0; font-size: .93rem; color: var(--ink); }
.check .where .k, .check .act .k { display: inline-block; min-width: 4.2rem;
  font: 700 .68rem/1.6 var(--mono); letter-spacing: .14em; text-transform: uppercase;
  color: var(--faint); margin-right: .35rem; }
.check .where code { overflow-wrap: anywhere; }
.check > details.drawer { margin: .9rem 0 0; background: var(--panel-2); }
.check > details.drawer > summary { font-size: .72rem; padding: .6rem .9rem; }
.check > details.drawer > .drawer-body { padding: 0 .9rem .8rem; }
/* A comparison table inside a drawer is WIDER THAN A PHONE, and `details.drawer`
   clips rather than scrolls — so on a 390px screen the right-hand columns were
   simply gone, unreachable by any gesture. Measured 2026-08-10 against the
   published mirror at a real 390px layout viewport: two tables, 371px and 407px
   of content in a 277px box, both `overflow-x: hidden` at the ancestor. The v33
   -vs-v34 table is one of them, and its right-hand column is the whole point of
   it. `display: block` turns the table itself into the scroller, which is the
   only fix that does not need a wrapper element around markdown the page renders
   verbatim. The sheets already behave — their <figure> is overflow-x: auto, and
   a 520px contact sheet swipes correctly at 390. */
.drawer-body table { display: block; max-width: 100%; overflow-x: auto; }
/* A settled item keeps every word it had; the drawer supplies the box, so the
   .check padding is dropped and only its state bar survives. */
details.check { padding: 0; }
details.rec > summary { font: 600 .95rem/1.55 var(--body); letter-spacing: 0;
  text-transform: none; color: var(--ink); }
details.rec > summary .n { color: var(--faint); }
details.rec[open] > summary { border-bottom: 1px solid var(--line); margin-bottom: .8rem; }
"""


DEFAULT_DESC = ("Story trees that branch instead of running linear — AI-rendered "
                "micro-drama, curated by one human's taste, every decision auditable in git.")


def page(title: str, body: str, depth: int = 0, path: str = "", desc: str = "",
         body_class: str = "", tail: str = "", robots: str = "") -> str:
    """`robots` is for pages that are reachable but not advertised — the review
    area (D17). Meta noindex rather than a robots.txt Disallow on purpose: a
    disallowed page is never fetched, so the noindex is never read, and the URL
    can still surface from a link somewhere else."""
    root = "../" * depth
    desc = (desc or DEFAULT_DESC).strip()
    if len(desc) > 200:
        desc = desc[:197].rstrip() + "…"
    url = f"{CANONICAL}/{path}"
    og_image = f"{CANONICAL}/og.png"
    esc_t, esc_d = html.escape(title), html.escape(desc)
    cls = f' class="{body_class}"' if body_class else ""
    robots_meta = f'\n<meta name="robots" content="{html.escape(robots)}">' if robots else ""
    # Which commit these bytes were built from, stated in the bytes themselves.
    # A CDN can hold a page for a day; it cannot change what the page says about
    # its own origin, which is why this and not an HTTP header — see
    # build_commit.py, and qa_local.check_public_freshness which reads it back.
    build_meta = build_commit.meta_tags()
    # Viewer-facing chrome: the two pages a stranger wants (watch, write) are in
    # the nav on every page; the build dashboard moved to the footer.
    nav = (f'<nav class="crumbs"><a href="{root}index.html">🌳 {REPO_NAME}</a> · '
           f'<a href="{root}watch.html">watch</a> · '
           f'<a href="{root}index.html#episodes">episodes</a> · '
           f'<a href="{root}create.html">write an episode</a> · '
           f'<a href="{root}machine.html">how it works</a> · '
           f'<a href="{root}city.html">the rules</a> · '
           f'<a href="{REPO_URL}">source</a></nav>')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">{robots_meta}{build_meta}
<meta name="description" content="{esc_d}">
<link rel="canonical" href="{url}">
<link rel="alternate" type="application/rss+xml" title="new nodes" href="{CANONICAL}/feed.xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Banyan City">
<meta property="og:title" content="{esc_t}">
<meta property="og:description" content="{esc_d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc_t}">
<meta name="twitter:description" content="{esc_d}">
<title>{esc_t}</title>
<style>{CSS}</style>
</head>
<body{cls}>
<main>
{nav}
{body}
<footer>Everything here is auditable in <a href="{REPO_URL}">git</a>.
Branch anything. Fork everything.<br>
<a href="{root}city.html#promise">The Promise</a> ·
<a href="{root}city.html#glossary">Glossary</a> ·
<a href="{root}status.html">🏛 the studio — watch it being made</a> ·
<a href="{root}pulse.html">📈 the pulse — queue &amp; machine over time</a> ·
<a href="{root}feed.xml">RSS</a></footer>
</main>
{tail}</body>
</html>"""


def md_to_html(text: str, base: str = "") -> str:
    """Markdown → html, with bare repo-file links pointed at GitHub.

    machine.html and the trials README link plain `WATERING.md`-style paths.
    Those files are never copied into _site, so the honest fix is to send the
    reader to the file itself in the repo (`base` = the file's repo-relative
    directory) instead of publishing a 404 on an auditability page.
    """
    MD.reset()
    out = MD.convert(text)

    def _fix(m: re.Match) -> str:
        href = m.group(1)
        if href.startswith(("http", "#", "mailto:", "/")) or href.endswith((".html", ".xml")):
            return m.group(0)
        path = f"{base.rstrip('/')}/{href}" if base else href
        while "/../" in path:  # normalise ../ against base
            path = re.sub(r"[^/]+/\.\./", "", path, count=1)
        return f'href="{REPO_URL}/blob/main/{path}"'

    return re.sub(r'href="([^"]+)"', _fix, out)


def demote(html_text: str) -> str:
    """Push an embedded document's headings down one level.

    A repo file rendered inside a page brings its own `<h1>`; three of those on
    city.html (and two more inside the trials drawers) read as three documents
    stapled together, and a screen reader hears three page titles.
    """
    return re.sub(r"<(/?)h([1-5])\b", lambda m: f"<{m.group(1)}h{int(m.group(2)) + 1}", html_text)


def strip_md(text: str) -> str:
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[*_`>#]", "", text).strip()


def extract_section(md_text: str, heading_prefix: str) -> str:
    """First paragraph under a '## <heading_prefix>…' heading."""
    m = re.search(rf"^## {re.escape(heading_prefix)}[^\n]*\n+(.+?)(?:\n\n|\n#)", md_text, re.M | re.S)
    return strip_md(m.group(1)) if m else ""


def split_sections(md_text: str) -> list:
    """node.md → [(heading, markdown)]; the first item's heading is ''."""
    parts, head, buf = [], "", []
    for line in md_text.splitlines():
        if line.startswith("## "):
            parts.append((head, "\n".join(buf).strip()))
            head, buf = line[3:].strip(), []
        else:
            buf.append(line)
    parts.append((head, "\n".join(buf).strip()))
    return parts


# ------------------------------------------------------------ publish safety

# What a VISITOR is told when a take is withheld. Plain, complete sentences that
# assume no knowledge of our pipeline, our gate, or who the founder is.
PUBLIC_REASON = {
    "deny": "the licence on the model that made it forbids commercial reuse, "
            "and every episode here is published under CC BY 4.0 — which grants it",
    "unknown": "its licence has not been cleared for redistribution yet",
}

# The same, for a CUT — a file whose own record is clean and whose insides are
# not. Each is completed by the caller with the ingredient it is about, so a
# reader is told which piece of the episode failed and not merely that one did.
COMPOSITE_REASON = {
    "refused": "it was assembled from material this site cannot publish",
    "missing": "it was assembled from a file the repo no longer carries, so "
               "nobody can check what is inside it",
    "unrecorded": "one of the files assembled into it has no provenance record "
                  "beside it, so nothing says what made it",
    "changed": "one of the files assembled into it has changed since it was "
               "cut, so its record no longer describes what is inside it",
    "unverifiable": "its record of what went into it is incomplete, so what is "
                    "inside it cannot be checked",
    # A HELD SHOT IS NOT A CONCATENATION AND STILL HAS AN INSIDE. hold_still
    # makes an mp4 out of ONE PNG and no model runs, so its record honestly says
    # `model: none` and `model_licence: n/a — inherits the still's licence`. The
    # licence it inherits was never fetched, so eleven of v34's fifteen beats
    # were drawn by animagine and asked about nothing. These three say so in a
    # visitor's words: the picture, not the mux, is what cannot ship.
    "frame_refused": "the picture it holds comes from a frame this site cannot "
                     "publish",
    "frame_missing": "it records which frame it was drawn from, and nothing in "
                     "the repo holds those pixels any more, so nobody can check "
                     "what it shows",
    "frame_unrecorded": "the frame it was drawn from has no provenance record "
                        "beside it, so nothing says what drew it",
    "frame_unverifiable": "its record of which frame it was drawn from is too "
                          "vague to check, so what it shows cannot be verified",
}


def publishable(f: Path, _inside: frozenset = frozenset()) -> tuple:
    """(ok, why) — may this take be copied onto the public site?

    The shot board publishes `takes/clips/` wholesale (D11: the crowd can only
    beat a take it can see), and for months that was a bare iterdir() with no
    licence question asked. It is how `13-i-always-left.PIXVERSE.mp4` became a
    downloadable file on banyan.city while DECISIONS.md D8 already recorded
    PixVerse's free tier as personal-use-only — the decision was written down,
    then the build published past it.

    Asks licence_gate rather than carrying a blocklist, so a route classified
    once is enforced everywhere. Records (sidecars, manifests) always travel:
    withholding the provenance of a withheld clip would be the exact opposite
    of the point.

    A FILE'S OWN RECORD IS NOT THE WHOLE ANSWER WHEN THE FILE IS A CUT. Muxing
    N clips into one mp4 used to produce one new file with one clean record and
    no way to ask what went into it, so every refusal inside a concatenation was
    laundered by the concatenation — the gate cleared episode 2 and v33 on
    2026-08-09 while the LTX-2 footage and the animagine stills they are made of
    were refused one directory down (D16, D15). `ingredients:` is render_t3
    writing down what it muxed, and `composite_publishable` below is this
    function asking that list the same question it asked about the file itself.
    `_inside` is the ingredient chain already being judged, so a manifest that
    names itself is answered once instead of forever.
    """
    if f.suffix.lower() in {".yaml", ".yml", ".json", ".md"}:
        return True, ""
    # lg.sidecar_for, not a hand-rolled with_suffix loop (2026-08-07). The
    # pipeline writes sidecars under TWO names — `09-x.meta.yaml` AND
    # `09-x.png.meta.yaml` — and with_suffix() can only ever build the first,
    # because it REPLACES the extension instead of appending to it. So every
    # full-name sidecar was invisible here, and invisible reads as
    # unprovenanced, which returns True four lines down: the most carefully
    # written record in the tree bought the least scrutiny. That shape is
    # licence_gate's own documented reader bug (see the META_EXT comment there),
    # and sidecar_for is the fix it already carries. It bit for real on the 40
    # candidate stills of 2026-08-07, all of them `<name>.png.meta.yaml`.
    side = lg.sidecar_for(f, lg.RECORD_SIDECAR_EXT)
    if side is None:
        return True, ""      # unprovenanced is the gate's finding, not the build's
    try:
        data = yaml.safe_load(side.read_text(encoding="utf-8")) or {}
    except Exception:                                    # noqa: BLE001
        return True, ""
    if not isinstance(data, dict):
        return True, ""
    # THE ONE PLACE A REFUSED LICENCE STILL PUBLISHES, and it is a founder call
    # rather than a softening (2026-08-09). D15's conflict is that our CC BY 4.0
    # offer grants what OpenRAIL++ withholds — so a frame published under an
    # offer narrowed to OpenRAIL++'s own terms grants nothing we do not hold and
    # is genuinely publishable. He authorised exactly that for the review
    # gallery: "put the images from my computer onto there please, not like
    # theres any reason to hide it."
    #
    # The three conditions live in licence_gate (REVIEW_GALLERY) and are asked
    # THERE, not re-implemented here, because the report and the publish path
    # disagreeing about which files these are is the failure that matters: lint
    # would print a clean tree while the build shipped something else. This call
    # answers the two that are about the file; the per-model one is below, so a
    # record naming both animagine and LTX still loses on the LTX clause.
    #
    # EVERY LICENCE A VALUE NAMES, not just the first one that fails. This used
    # to ask engine_licence(), which returns the FIRST non-allow licence and
    # stops — fine while any single failure refused the file, and a hole the
    # moment one licence can be excused: `still: animagine | motion: LTX-2.3`
    # would have been excused on the animagine clause and never asked about the
    # LTX one. Which is hole 1 verbatim ("a compound field is judged by EVERY
    # model it names"), re-opened by the exemption rather than by the matcher.
    # The iteration order is model_licences()' own, so the licence NAMED in a
    # refusal message is the same one it was before this changed.
    narrowed = lg.review_narrowed(f, data)
    for key, value in data.items():
        if key.lower() not in lg.PROVENANCE_KEYS:
            continue
        hits = lg.model_licences(value)
        # A NARROWED OFFER NEEDS A MODEL TO NARROW TO. Everywhere else on the
        # site a value naming no model we have classified is copied out and left
        # for the licence gate to report as debt — deliberate, and documented in
        # licence_gate.is_candidate: the build does not withhold what it cannot
        # judge, CI fails on it instead. That trade stops working in this one
        # directory. The gallery's whole clearance is "published under the terms
        # this model imposes", so a record naming a model nobody has read states
        # terms nobody has read, and the exemption would become the cheapest way
        # onto the site: any refused file, one invented model name, one
        # `published_under:` line. Sentinels and pointers are honoured as they
        # are in the gate — `model: none` on a slate declares no model rather
        # than hiding one.
        if narrowed and not hits:
            norm = lg.normalise(value)
            if norm not in lg.SENTINELS and not lg.POINTER.search(norm):
                return False, (f"{PUBLIC_REASON['unknown']} — nobody here has "
                               "written down what made it")
        for licence in dict.fromkeys(licence for _n, licence in hits):
            verdict, _why = lg.classify(licence)
            if verdict == "allow":
                continue
            if narrowed and lg.narrowed_model([n for n, l in hits if l == licence]):
                continue                   # D15 visibility half — see above
            # 'unknown' is withheld too, not waved through. Unknown means
            # nobody has read the terms — and "we do not know whether we may
            # publish this" is not a reason to publish it to the open web. It
            # is a reason to read the licence, which is a human's job.
            #
            # classify()'s own `why` is deliberately NOT used here. It is written
            # for whoever maintains the gate — "classify it in
            # pipeline/licence_gate.py or replace the asset" — and this string
            # lands on a public page. The first version of this shipped that
            # sentence, plus "founder sign-off pending", onto the shot board for
            # a stranger arriving from TikTok to read. Same de-jargoning rule as
            # the rest of the site: story words out front, machine words in the
            # drawers. The licence NAME stays, because that part is genuinely
            # informative and a reader can look it up.
            return False, f"{PUBLIC_REASON[verdict]} ({public_licence(licence)})"
    return composite_publishable(data, f, _inside)


def composite_publishable(data: dict, f: Path, inside: frozenset = frozenset()) -> tuple:
    """(ok, why) for the `ingredients:` manifest an assembled cut carries.

    A cut is only as publishable as the material inside it, and the mp4 itself
    cannot be asked — a concatenation keeps no trace of its inputs. So render_t3
    writes one row per source file at the moment it muxes them (path, sha256,
    and the verdict that file carried then) and this re-asks the question now.

    FOUR WAYS A ROW FAILS, and three of them are absences. That is deliberate,
    and it is the same rule lint applies to a missing record: an ingredient we
    cannot resolve is a REFUSAL, never a pass. A manifest is a claim about what
    is inside a file nobody can look inside; a claim that cannot be checked buys
    the cut nothing, and treating it as a pass would make deleting a row the
    cheapest way past the gate.

      1. the row's own recorded verdict was already `publishable: false`
      2. the file it names is not on disk, or the row names no file, or names it
         without a hash — nothing to check the cut against
      3. the file is there and no longer hashes to the recorded value — the cut
         holds bytes this manifest does not describe
      4. the file is there, unchanged, and refused NOW — by its own sidecar,
         which is checked with the same publishable() the cut went through, so a
         licence reclassified after assembly is caught on the next build

    Paths are repo-relative (render_t3 writes them that way whenever the source
    is inside the tree) and fall back to the cut's own directory, which is what
    makes a cut assembled and judged inside one temp directory answerable at all.

    AND THE MANIFEST IS NOT THE ONLY WAY IN. `ingredients:` lists what render_t3
    MUXED — clips and audio — and a held beat's clip is one of those rows, so the
    walk above reaches it and stops there. Underneath it is a PNG that no row
    names, because hold_still did not mux it: it drew a whole shot out of it.
    Measured on 2026-08-09, that is how `ep1-v34-PROVISIONAL.mp4` came back
    `(True, "")` with eleven animagine frames inside it while
    `takes/stills/06-too-blue-r5-s2.png` — one of the eleven — came back
    `(False, 'CreativeML Open RAIL++-M')` when asked by name one directory down.
    `source_frame()` below is the second door, and it is asked for every record
    that names a frame, not only for cuts: a held clip has no `ingredients:`
    block at all and is exactly the file this hole was hiding behind.
    """
    inside = inside | {str(f.resolve())}
    rows = data.get("ingredients")
    if rows is not None:
        ok, why = ingredients_publishable(rows, f, inside)
        if not ok:
            return ok, why
    return frame_publishable(data, f, inside)


def ingredients_publishable(rows, f: Path, inside: frozenset) -> tuple:
    """The `ingredients:` walk itself — see composite_publishable's docstring."""
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        return False, f"{COMPOSITE_REASON['unverifiable']} (its ingredient list is unreadable)"
    for row in rows:
        rel = str(row.get("path") or "").strip()
        want = str(row.get("sha256") or "").strip().lower()
        label = rel or "an unnamed source file"
        if row.get("publishable") is False:
            note = str(row.get("why") or "").strip()
            return False, (f"{COMPOSITE_REASON['refused']} — {label}"
                           + (f": {note}" if note else ""))
        if not rel or not want:
            return False, f"{COMPOSITE_REASON['unverifiable']} ({label})"
        src = Path(rel) if Path(rel).is_absolute() else REPO / rel
        if not src.exists():
            src = f.parent / Path(rel).name
        if not src.exists():
            return False, f"{COMPOSITE_REASON['missing']} ({label})"
        if bytes_sha256(src) != want:
            return False, f"{COMPOSITE_REASON['changed']} ({label})"
        if lg.sidecar_for(src, lg.RECORD_SIDECAR_EXT) is None:
            return False, f"{COMPOSITE_REASON['unrecorded']} ({label})"
        if str(src.resolve()) in inside:
            continue                      # already being judged further up
        ok, why = publishable(src, inside)
        if not ok:
            return False, f"{COMPOSITE_REASON['refused']} — {label}: {why}"
    return True, ""


def source_frame(data: dict, f: Path) -> tuple:
    """(frame | None, why) — the PNG this record says its pixels came from.

    `(None, "")` means the record names no frame and there is nothing to ask
    about. `(None, "<why>")` means it DOES name one and the claim cannot be
    resolved, which is a refusal for the same reason an unresolvable ingredient
    row is: a claim nobody can check must buy the file nothing, or deleting the
    claim becomes the cheapest way past the gate.

    RESOLVED BY BYTES WHEREVER BYTES ARE RECORDED, exactly as still_from_record
    does for posters, and for a sharper reason here. A promotion COPIES a take
    into `stills/` under a canon name, and canon names change hands: beat 15's
    has held three different pictures. If this followed the name it would ask
    about whichever frame is canon TODAY and clear a clip drawn from a frame the
    founder has since refused. The hash is what makes the answer about this
    file's pixels rather than about this beat's current pixels.

    WHY takes/ IS SEARCHED TOO, and it is the half that survives promotion: a
    candidate frame carries its own render-time sidecar under `takes/stills/`
    and a promoted copy in `stills/` carries whatever the promotion wrote. Both
    hold the same bytes, so either answers "what drew this"; the takes/ record is
    the one that has always existed. Canon directories are searched first so the
    reason a visitor reads names the file the page links.
    """
    name, want = record_still_claim(data)
    hint = str(data.get("source_still_path")
               or data.get("init_still_path") or "").strip()
    frame = data.get("init_frame")
    if not hint and isinstance(frame, dict):
        hint = str(frame.get("path") or "").strip()
    # The render box writes windows paths and a backslash is a legal posix
    # filename character, so Path() would swallow the whole string as one name —
    # the same trap record_still_claim documents.
    hint = hint.replace("\\", "/").strip()
    if not name and not want and not hint:
        return None, ""
    hinted = []
    if hint:
        p = Path(hint)
        for cand in ((p if p.is_absolute() else REPO / p), f.parent / p.name):
            if cand.exists() and cand not in hinted:
                hinted.append(cand)
    # Canon stills only for a NAME, which is still_from_record's rule and not an
    # oversight: `12-undefined.png` exists in `stills/` AND in `takes/stills/`,
    # and a bare name that matches two files is not evidence about either.
    canon = [d / name for d in still_dirs() if name and (d / name).exists()]
    if want:
        for cand in hinted + canon:
            if bytes_sha256(cand) == want:
                return cand, ""
        for d in frame_dirs():
            for p in sorted(d.glob("*.png")):
                if bytes_sha256(p) == want:
                    return p, ""
        return None, (f"{COMPOSITE_REASON['frame_missing']} "
                      f"({name or want[:12] + '…'})")
    if hinted:
        return hinted[0], ""
    if len(canon) == 1:
        return canon[0], ""
    if not canon:
        return None, f"{COMPOSITE_REASON['frame_missing']} ({name})"
    return None, (f"{COMPOSITE_REASON['frame_unverifiable']} ({name} — no hash, "
                  f"and {len(canon)} nodes hold that name)")


def recorded_twin(frame: Path):
    """Another file in the tree with these exact bytes AND a record beside it.

    A canon promotion is `cp takes/stills/<take>.png stills/<beat>.png` and
    nothing else, so the take is still there, still byte-identical, still
    carrying the sidecar its render wrote. That sidecar is the provenance the
    copy did not inherit, and following the bytes to it is what stops a
    promotion from laundering a licence.

    Bytes, never the name: promotion RENAMES (`14-worth-staying-in-r4-s3.png` →
    `14-worth-staying-in.png`) and canon names change hands between pictures, so
    a name-based lookup would answer about the wrong frame in exactly the case
    that matters.
    """
    want = bytes_sha256(frame)
    for d in frame_dirs():
        for p in sorted(d.glob("*.png")):
            if p == frame:
                continue
            if bytes_sha256(p) == want and lg.sidecar_for(
                    p, lg.RECORD_SIDECAR_EXT) is not None:
                return p
    return None


def frame_publishable(data: dict, f: Path, inside: frozenset) -> tuple:
    """(ok, why) for the frame a record was drawn from — see source_frame().

    THE PROMOTION HOLE THIS CLOSES IS THE SECOND HALF, and it is the worse half.
    Following the reference is only useful if the frame at the end of it carries
    a record: `publishable()` reads an unprovenanced file as permitted (the
    gate's finding, not the build's), so copying an animagine take into
    `stills/` — which is what a canon promotion IS — stripped the very record
    that would have refused it. Here, one level inside a cut, absence is a
    refusal and not a pass; `stills/README.md` carries the matching convention,
    that a promoted frame gets a sidecar naming the take it came from, its
    sha256 and the model, so the answer is the licence and not the silence.
    """
    frame, why = source_frame(data, f)
    if why:
        return False, why
    if frame is None or str(frame.resolve()) in inside:
        return True, ""
    if lg.sidecar_for(frame, lg.RECORD_SIDECAR_EXT) is None:
        # THE RECORD THE PROMOTION STRIPPED IS USUALLY STILL IN THE TREE, under
        # the take's name, holding the same bytes. Identical bytes are the
        # identical picture and therefore the identical provenance — the same
        # reasoning still_from_record uses to re-poster a renamed frame — so a
        # canon still with no sidecar is asked through its recorded twin rather
        # than waved through. Eight of the thirty frames in `stills/` answer
        # this way today; the other twenty-two are older than `takes/stills/`
        # and genuinely hold no record anywhere, which is a refusal below and a
        # backfill in stills/README.md, not a pass.
        twin = recorded_twin(frame)
        if twin is None:
            # AND HERE THE FRAME CHECK STOPS, DELIBERATELY, WITH A COUNT RATHER
            # THAN A REFUSAL. Twenty-two of the thirty frames in `stills/` are
            # older than `takes/stills/` and hold no record anywhere, so
            # refusing on absence would have withheld 23 of the 29 cuts on the
            # /review page — the surface he screens from — in the same commit
            # that discovered the problem, and every one of them for "nothing
            # says what drew it" rather than for a licence. That is the trade
            # lint_licences already refused once: "failing the deploy over debt
            # this gate itself just discovered would have blocked the founder's
            # own goal for the day."
            #
            # It is also the rule publishable() states four lines into itself —
            # unprovenanced is the GATE's finding, not the build's — and a
            # picture must not be judged more harshly than the file that holds
            # it. The absence is reported instead: named here, printed at the
            # end of the build, and answered for real by the promotion sidecars
            # `stills/README.md` now prescribes. Those cost licence-debt lines
            # (25 -> 47, measured), which is D15's bill and the founder's call —
            # which is exactly why this line does not quietly pre-empt it.
            FRAME_WARNINGS.append(
                f"{f.name}: drawn from {frame.name}, which carries no provenance "
                f"record and no recorded twin — nothing in the tree says what "
                f"drew it (stills/README.md: promotions need a sidecar)")
            return True, ""
        frame = twin
    ok, why = publishable(frame, inside)
    if not ok:
        return False, f"{COMPOSITE_REASON['frame_refused']} — {frame.name}: {why}"
    return True, ""


def public_licence(licence: str) -> str:
    """The licence identifier with our own bookkeeping stripped off.

    MODEL_LICENCES values carry internal notes for whoever maintains the gate —
    "LTXV Open Weights Licence 0.X (read; founder sign-off pending)". The name is
    worth showing a visitor; "founder sign-off pending" is not, and neither is a
    trailing remedy clause after an em dash.
    """
    licence = licence.split(" — ")[0]
    return re.sub(r"\s*\([^)]*\)\s*$", "", licence).strip()


# --------------------------------------------------- what the deploy will have
# One `git ls-files` per directory asked about. Keyed by directory because the
# question is always asked about a whole glob at once.
_TRACKED: dict = {}
# How many files on this disk the site deliberately did not use because the
# tree does not carry them. Printed at the end of the build: a silent skip and a
# forgotten `git add` would look identical, and they are not.
_LOCAL_ONLY = 0


def _tracked_in(d: Path):
    """The names git keeps in directory `d`, or None if git cannot answer.

    None is not the empty set. "git is not here" — a tarball export, no git
    binary, a directory outside any repo — must fall back to using whatever is
    on disk, which is what every build did before this function existed. An
    empty set is a real answer: git looked, and this directory holds nothing it
    keeps. Obeying that is the entire point.

    Runs `git -C d`, so the paths come back relative to `d` itself: a direct
    child is `x.png` and something one level down is `sub/x.png`. That is what
    makes the membership test below exact rather than a basename guess.
    """
    key = str(d)
    if key in _TRACKED:
        return _TRACKED[key]
    got = None
    try:
        r = subprocess.run(["git", "-C", str(d), "ls-files", "-z"],
                           capture_output=True, timeout=30)
        if r.returncode == 0:
            got = {p.decode("utf-8", "replace") for p in r.stdout.split(b"\0") if p}
    except (OSError, subprocess.SubprocessError):
        got = None
    _TRACKED[key] = got
    return got


def in_the_tree(files) -> list:
    """The subset of `files` git keeps — which is the subset the deploy has.

    THE BUG THIS CLOSES (2026-08-08). A node's candidate frames are gitignored
    on purpose (`genomes/*/nodes/*/takes/**/*.png`, ~1 MB each, dozens per
    beat), so they exist on the box that drew them and nowhere else. The shot
    board listed every PNG it could see on disk and the build copied the ones
    publishable() allowed, which meant a local build produced 164 <a href>s into
    002b candidate frames that are not in the tree and will never be on
    banyan.city. `check_links` correctly failed the build over them — and CI,
    having none of the files, never saw a link to fail on. So `build_site.py`
    exited 1 on this laptop and 0 on the deploy box for the same commit, and
    the difference got diagnosed as a broken site three separate times in one
    day. The fix is upstream of the link gate: do not emit the link.

    THE COST, STATED PLAINLY, because it was the argument against doing this:
    the site build now reads git state, and its output is supposed to be a
    function of the tree. It is worth it because the reading is what MAKES it
    one. "The tree" is what is committed — it is what CI clones and what the
    deploy serves. A build that publishes untracked files is a function of one
    working directory, which is strictly less than the tree, and the 164 links
    are what that difference looks like from outside.

    Tracked beats ignored, deliberately: 001's takes/ is a committed v1 archive
    (`!genomes/…/001-capability-inventory/takes/**`) and every file in it ships,
    licence gate permitting. That is also why this asks what git KEEPS rather
    than what .gitignore MATCHES — a file that is untracked because nobody
    committed it yet is just as absent from the deploy as an ignored one, and
    both answers must be the same answer or this bug comes back wearing a
    different hat.
    """
    global _LOCAL_ONLY
    out = []
    for f in files:
        tracked = _tracked_in(f.parent)
        if tracked is None or f.name in tracked:
            out.append(f)
        else:
            _LOCAL_ONLY += 1
    return out


def withheld_note(rows: list) -> str:
    """Why a take the board lists is not downloadable here.

    Only ever asked about files the tree carries — in_the_tree() runs first, so
    a frame that exists on one laptop is not "withheld" here, it is simply not
    part of the repo this page describes. Writing it into the note would have
    been a false statement: the note's own first sentence promises the reader
    that the take exists in the repo and its provenance is published beside it.

    Silence would read as a broken link. The take EXISTS, its recipe and
    provenance are published beside it, and anyone may re-shoot the beat on a
    publish-safe route — that is the fork invitation, stated instead of hidden.
    """
    lines = ["# Takes withheld from the public site", "",
             "These takes exist in the repo and their provenance is published",
             "beside them. They are not copied here because their licence",
             "forbids it: the tree releases every episode under **CC BY 4.0**,",
             "which grants commercial reuse a non-commercial input cannot.", "",
             "Withholding is not a quality judgement. Any of these beats can be",
             "re-shot on a publish-safe route ($0: `render_local.py`, Kaggle Wan,",
             "`post_motion.py`) and a better take is welcome from anyone.", ""]
    for name, why in sorted(rows):
        lines.append(f"- **{name}** — {why}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- media facts

def mp4_seconds(p: Path):
    """Duration from the mp4 header itself — no ffprobe on the deploy box.

    A viewer deserves to know whether an episode is 20 seconds or 5 minutes
    before committing, and the deploy container has no media tools at all.
    """
    try:
        with p.open("rb") as f:
            blob = f.read(2 << 20)
            i = blob.find(b"mvhd")
            if i < 0:                       # moov at the tail (non-faststart)
                f.seek(max(0, p.stat().st_size - (2 << 20)))
                blob = f.read()
                i = blob.find(b"mvhd")
                if i < 0:
                    return None
        o = i + 4
        if blob[o] == 1:
            scale = struct.unpack(">I", blob[o + 20:o + 24])[0]
            units = struct.unpack(">Q", blob[o + 24:o + 32])[0]
        else:
            scale = struct.unpack(">I", blob[o + 12:o + 16])[0]
            units = struct.unpack(">I", blob[o + 16:o + 20])[0]
        secs = units / scale if scale else 0
        return secs if 0.5 < secs < 7200 else None
    except Exception:
        return None


def dur_label(secs) -> str:
    if not secs:
        return ""
    m, s = divmod(int(round(secs)), 60)
    return f"{m}:{s:02d}" if m else f"{s}s"


_POSTERS: dict = {}
_STILLS: dict = {}


def first_still(node_dir: Path):
    """A founder-approved still to stand in for a video frame.

    The canonical host builds without ffmpeg, so the ffmpeg path alone would
    publish an animated series as a grid of black rectangles exactly where it
    matters. The middle still of an episode reads better as a poster than its
    opening frame (episode 1 opens on black).
    """
    key = str(node_dir)
    if key not in _STILLS:
        pngs = sorted((node_dir / "stills").glob("*.png")) if (node_dir / "stills").is_dir() else []
        _STILLS[key] = pngs[len(pngs) // 2] if pngs else None
    return _STILLS[key]


def poster(src: Path, rel: str, fallback: Path | None = None):
    """One frame per clip so a phone shows a picture, not a black rectangle.

    ffmpeg is optional (Vercel's build image has none): a missing binary or a
    failed extract falls back to the episode's approved still, and only when
    there is neither does the player render without a poster.
    """
    if rel in _POSTERS:
        return _POSTERS[rel]
    got = None
    if OUT.exists():
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if FFMPEG and src.exists():
            try:
                subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-ss", "1", "-i", str(src),
                                "-frames:v", "1", "-vf", "scale=360:-2", "-q:v", "6", str(dst)],
                               check=True, timeout=90)
                if dst.exists() and dst.stat().st_size:
                    got = rel
            except Exception:
                got = None
        if got is None and fallback is not None and fallback.exists():
            alt = rel.rsplit(".", 1)[0] + fallback.suffix
            shutil.copy(fallback, OUT / alt)
            got = alt
    _POSTERS[rel] = got
    return got


def poster_attr(rel, prefix: str = "") -> str:
    return f' poster="{prefix}{rel}"' if rel else ""


_SHA: dict = {}
_STILL_DIRS: list = []
# Every clip whose record cannot be honoured, reported at the end of the build.
POSTER_WARNINGS: list = []
# Every file whose source frame carries no provenance anywhere in the tree —
# counted, not refused (see frame_publishable). Printed at the end of the build
# so a promotion that strips a record is visible the same day it happens rather
# than on the day someone asks what an episode is made of.
FRAME_WARNINGS: list = []
# How much newer than its clip a still may be before the name stops being
# evidence. A promotion is hours or days later; a fresh `git clone` stamps every
# file with the checkout time, so the honest window has to be wider than clock
# skew and narrower than a working day. See still_from_record's docstring for
# what this rule can and cannot see on the deploy host.
STILL_MTIME_SLACK = 300


def bytes_sha256(p: Path) -> str:
    """sha256 of a file, cached per (path, size, mtime).

    A build asks the same still's hash once per clip that names it, and the
    stills are ~1.3MB each; without the cache a 22-clip review page re-reads
    26 PNGs 22 times.
    """
    st = p.stat()
    key = (str(p), st.st_size, st.st_mtime_ns)
    if key not in _SHA:
        _SHA[key] = hashlib.sha256(p.read_bytes()).hexdigest()
    return _SHA[key]


def still_dirs() -> list:
    """Every node's stills/ — a cut on the review page can come from any node.

    Episode 2's clips name frames that live under `002b-first-citizen/stills`,
    and a lookup hard-wired to one node cannot find them at all.
    """
    global _STILL_DIRS
    if not _STILL_DIRS:
        _STILL_DIRS = sorted(
            d for g in sorted((REPO / "genomes").glob("*"))
            for d in sorted(g.glob("nodes/*/stills")) if d.is_dir())
    return _STILL_DIRS


_FRAME_DIRS: list = []


def frame_dirs() -> list:
    """Every directory a SOURCE frame can live in — canon stills/ first, then
    takes/stills/.

    still_dirs() answers "which frame does the page show", and canon is the only
    honest answer to that. This answers "which frame drew this file", where a
    provisional pick out of `takes/stills/` is a perfectly real answer — v34
    holds one on beat 6 — and where the takes/ copy is often the only one whose
    record survived promotion. Order matters: a promoted frame exists twice, and
    the refusal a visitor reads should name the file the site links.
    """
    global _FRAME_DIRS
    if not _FRAME_DIRS:
        _FRAME_DIRS = still_dirs() + sorted(
            d for g in sorted((REPO / "genomes").glob("*"))
            for d in sorted(g.glob("nodes/*/takes/stills")) if d.is_dir())
    return _FRAME_DIRS


def record_still_claim(data: dict) -> tuple:
    """(name, sha256) — the frame a clip's record CLAIMS it was drawn from.

    THREE DIALECTS, because three writers grew independently and all three are
    honest:
      `init_still` / `init_still_sha256`        the renderers
      `source_still` / `source_still_sha256`    hold_still
      `init_frame: {path:, sha256:, …}`         video_task's LTX/Wan renders

    The nested one was invisible until 2026-08-09, and expensively so: both v2
    renders in review/ep2-b01/ record their frame that way, so the resolver saw a
    record naming no still at all while two lines down it carried sha256
    7cc22aa1… — byte-for-byte `01-cold-open-REVOKED-too-tall.png`, on disk,
    findable, ignored. Episode 2's cold open was a blank player whose own
    provenance held the answer.

    TWO TRAPS IN THAT BLOCK, and both are load-bearing:
      * `path` is written by the Windows render box with BACKSLASHES, and a
        backslash is a legal filename character on posix — so Path(...).name
        returns the whole string rather than raising. Split on both separators.
      * `plate_sha256` is NOT the answer. It is the 704x1280 cover-crop fed to
        the model, it exists in no stills/ directory, and recording it would turn
        a resolvable poster into a refusal. Only `sha256` is read here.

    AND A CORRECTION OUTRANKS ALL THREE. Render-time provenance is appended to,
    never rewritten (the convention licence_gate already reads as
    `corrected_model` / `corrected_platform`), so a frame recovered out of git
    history lands in a dated `corrections:` entry as `corrected_init_still` and
    `corrected_init_still_sha256` — and a correction that no reader consults is
    just a comment. Last correction wins; they are appended in date order.
    Precedence overall: correction, then the flat render-time keys, then the
    nested block.
    """
    name = want = ""
    for c in (data.get("corrections") or []):
        if not isinstance(c, dict):
            continue
        name = str(c.get("corrected_init_still")
                   or c.get("corrected_source_still") or name).strip()
        want = str(c.get("corrected_init_still_sha256")
                   or c.get("corrected_source_still_sha256") or want).strip().lower()
    name = name or str(data.get("init_still") or data.get("source_still") or "").strip()
    want = want or str(data.get("init_still_sha256")
                       or data.get("source_still_sha256") or "").strip().lower()
    frame = data.get("init_frame")
    if isinstance(frame, dict):
        if not name:
            raw = str(frame.get("path") or "").strip().replace("\\", "/")
            name = raw.rsplit("/", 1)[-1]
        if not want:
            want = str(frame.get("sha256") or "").strip().lower()
    return name, want


def still_from_record(data: dict, clip: Path, dirs: list) -> tuple:
    """WHICH PIXELS THIS CLIP HOLDS — answered by bytes, never by filename alone.

    Returns `(still | None, warning)`. `(None, "")` means the record names no
    still at all and the caller is free to fall back to something generic;
    `(None, "<why>")` means the record DOES name one and we cannot honour the
    claim, so the honest poster is no poster.

    THE BUG THIS EXISTS TO PREVENT, in one sentence: a still promoted under an
    existing canon filename re-posters every older clip drawn from the OLD
    pixels, so the review page shows a tall sapling over footage of bare soil.
    That happened live to three comparison pairs — beats 7, 12 and 15 of node
    001 — because `init_still: 15-something-s-coming.png` was read as a name and
    the name had changed hands. `poster()` only reaches this fallback when ffmpeg
    is missing, which is exactly the Vercel build image, so the wrong poster was
    visible only on the deployed page and never on a local build.

    Resolution order, and each step is a different kind of evidence:
      1. `init_still_sha256` / `source_still_sha256` matching the named file —
         the record is precise and the name still holds those bytes.
      2. the same hash found on ANY still in ANY node — the bytes were renamed,
         which is what a `-REVOKED-*` retirement is (R6 keeps them in place), so
         the clip's true frame is still on disk under its new name and we show
         it. This is the case that turns a lie into a correct poster rather than
         into a blank.
      3. a recorded hash that no file on disk has — refuse. The record makes a
         claim about bytes nobody holds; anything we showed would be a guess.
      4. no hash, one file under that name, and that file is not meaningfully
         newer than the clip — trust the name. THE LIMIT OF THIS RULE, stated
         because it matters: mtime is a property of the checkout, not of the
         repo, so on the build host every file is the same age and this test
         cannot fire. It catches a stranded clip on a working copy; only a
         recorded hash catches one on Vercel, which is why every published cut's
         record was backfilled with its measured hash on 2026-08-08.
      5. no hash and the name is missing, or ambiguous across nodes — refuse.
    """
    name, want = record_still_claim(data)
    if not name and not want:
        return None, ""
    named = [d / name for d in dirs if name and (d / name).exists()]
    if want:
        for cand in named:
            if bytes_sha256(cand) == want:
                return cand, ""
        # The bytes were renamed out from under the name. Identical bytes are
        # the identical picture, so any file holding them is the right poster.
        renamed = [p for d in dirs for p in sorted(d.glob("*.png"))
                   if bytes_sha256(p) == want]
        if renamed:
            return renamed[0], ""
        return None, (f"{clip.name}: records the still it was drawn from as "
                      f"{want[:12]}… and no still in the repo has those bytes")
    if not named:
        return None, (f"{clip.name}: names still {name!r}, which is in no node's stills/")
    if len(named) > 1:
        return None, (f"{clip.name}: names still {name!r}, which exists in "
                      f"{len(named)} nodes, and the record does not say which")
    cand = named[0]
    if cand.stat().st_mtime > clip.stat().st_mtime + STILL_MTIME_SLACK:
        return None, (f"{clip.name}: names still {name!r} with no hash, and the file now "
                      f"under that name is newer than the clip — the name was re-promoted, "
                      f"so those are not this clip's pixels")
    return cand, ""


def poster_still(data: dict, clip: Path, dirs: list, assembly_still) -> tuple:
    """still_from_record plus the one question it cannot answer: what a record
    that names NO still at all should show. Returns `(still | None, warning)`.

    Two populations end up here and they deserve opposite answers.

    An ASSEMBLY says so in its own record — `sources:` is present and its
    `model:` reads "per-beat — see sources". A 90-second cut of episode 1 really
    does contain the node's approved middle still, so that frame is a true
    picture of the film and not a guess about it.

    ONE SHOT that records no still gets nothing. THE CASE THIS CLOSES, measured
    on the live cuts.yaml on 2026-08-08: `checklist/002b-b01-5b.mp4` is an
    EPISODE 2 beat-1 render whose record names no still, and the blanket
    fallback handed it `09-whoami.png` — episode ONE, beat NINE — as its poster
    on every host without ffmpeg, i.e. on Vercel, i.e. on the page he screens
    from his phone. It is the same lie as a stale filename wearing different
    clothes: "which frame does this shot hold" had no answer, and something was
    shown anyway. A blank player is how you say there is no answer.

    A separate function from the closure that used to hold this so the rule can
    be tested without building a page (test_pipeline pins all five branches).
    """
    cand, why = still_from_record(data, clip, dirs)
    if cand is None and not why:
        if data.get("sources"):
            return assembly_still, ""
        why = (f"{clip.name}: its record names no still at all, so nothing in the "
               f"repo says which frame this shot holds")
    return (None, why) if why else (cand, "")


DATE_RE = re.compile(r"(20\d\d-\d\d(?:-\d\d)?)")


def leaf_date(l: dict) -> str:
    for k in ("released", "note", "form", "status", "author", "model"):
        m = DATE_RE.search(str(l.get(k) or ""))
        if m:
            return m.group(1)
    return ""


def cost_label(l: dict) -> str:
    c = float(l.get("cost_usd") or 0)
    return "$0 to make" if c == 0 else f"${c:.2f} to make"


def stage_word(l: dict) -> str:
    return TIER_WORDS.get(str(l.get("tier")), str(l.get("tier")))


def footage_line(l: dict) -> str:
    """What actually differs between two old cuts of the same script: the camera.

    An assembled film's own `model:` field reads "per-beat — see sources", so the
    distinguishing fact lives in the per-beat sources list.
    """
    plats, voices = [], []
    for s in l.get("sources") or []:
        p = str(s.get("platform") or s.get("model") or "").strip()
        if p and p not in plats:
            plats.append(p)
        v = str(s.get("voice_engine") or "").strip()
        if v and v not in voices:
            voices.append(v)
    bits = []
    if plats:
        bits.append("shot on " + ", ".join(plats[:2]))
    if voices:
        bits.append("voiced by " + voices[0])
    return ", ".join(bits)


# ------------------------------------------------------------------- genome io

def load_genome(genome_dir: Path) -> dict:
    tree = yaml.safe_load((genome_dir / "tree.yaml").read_text())
    lineage = yaml.safe_load((genome_dir / "lineage.yaml").read_text())
    nodes = {}
    for n in lineage["nodes"]:
        node_dir = genome_dir / "nodes" / n["slug"]
        n["md"] = (node_dir / "node.md").read_text()
        hook = extract_section(n["md"], "Hook")
        n["hook_raw"] = hook
        # "The question a viewer can state:" is a writing rule (R5), not a
        # sentence for a viewer — keep the question, drop the shop talk.
        n["teaser"] = re.sub(r"\s*The question a viewer can state:\s*", " ",
                             hook, flags=re.I).strip()
        n["children"] = []
        n["leaf_meta"] = []
        n["dir"] = node_dir
        for leaf_id in n.get("leaves") or []:
            f = node_dir / "leaves" / f"{leaf_id}.yaml"
            if f.exists():
                meta = yaml.safe_load(f.read_text())
                content = str(meta.get("content", ""))
                if content.endswith(".mp4"):
                    meta["seconds"] = mp4_seconds(node_dir / "leaves" / content)
                n["leaf_meta"].append(meta)
        reactions = node_dir / "sap" / "reactions.yaml"
        n["reactions"] = yaml.safe_load(reactions.read_text()) if reactions.exists() else None
        summary = node_dir / "sap" / "summary.yaml"
        n["sap"] = yaml.safe_load(summary.read_text()) if summary.exists() else None
        screening = node_dir / "sap" / "screening.yaml"
        n["screening"] = yaml.safe_load(screening.read_text()) if screening.exists() else None
        n["has_board"] = (node_dir / "shots.md").exists()
        nodes[n["id"]] = n
    for n in nodes.values():
        if n.get("parent"):
            p = nodes[n["parent"]]
            p["children"].append(n)
            n["parent_title"] = p["title"]
    roots = [n for n in nodes.values() if not n.get("parent")]
    return {"tree": tree["tree"], "config": tree, "nodes": nodes, "roots": roots, "dir": genome_dir}


def chips(n: dict) -> str:
    """Badges that can actually differ between episodes.

    The old `hot` chip was on all sixteen nodes at once — a status light that
    is always on tells a reader nothing, so it only shows when it isn't `hot`.
    """
    out = f'<span class="chip">{html.escape(n["id"])}</span>'
    if n.get("trunk"):
        out += '<span class="chip trunk">canon</span>'
    if str(n.get("status")) != "hot":
        out += f'<span class="chip">{html.escape(str(n["status"]))}</span>'
    return out


def trunk_chain(g: dict) -> list:
    chain, cur = [], next((r for r in g["roots"] if r.get("trunk")), None)
    while cur:
        chain.append(cur)
        cur = next((c for c in cur["children"] if c.get("trunk")), None)
    return chain


def live_videos(n: dict) -> list:
    return [l for l in n["leaf_meta"]
            if str(l.get("content", "")).endswith(".mp4") and l.get("status") == "live"]


def lead_take(n: dict):
    """The one cut a stranger should see: newest, highest-tier, live."""
    vids = sorted(live_videos(n), key=lambda l: (str(l.get("tier")), str(l.get("leaf"))))
    return vids[-1] if vids else None


def best_t3(n: dict) -> dict | None:
    vids = [l for l in n["leaf_meta"] if str(l.get("tier")) == "T3"
            and str(l.get("content", "")).endswith(".mp4") and l.get("status") == "live"]
    return vids[-1] if vids else None


def episode_no(g: dict, n: dict):
    """Position on the canon path, or None for a branch off it."""
    for i, t in enumerate(trunk_chain(g), 1):
        if t["id"] == n["id"]:
            return i
    return None


def eyebrow_for(g: dict, n: dict) -> str:
    gid = g["tree"]["title"].upper()
    ep = episode_no(g, n)
    if ep:
        return f"EPISODE {ep} · {gid} · CANON"
    if n.get("parent"):
        p = g["nodes"][n["parent"]]
        pep = episode_no(g, p)
        where = f"EPISODE {pep}" if pep else f"“{p['title'].upper()}”"
        return f"A BRANCH OF {where} · {gid}"
    return f"{gid} · BRANCH"


# ------------------------------------------------------------------ credits
#
# WHO MADE THIS CUT, ON THE SURFACE RATHER THAN IN THE YAML. Added 2026-08-17
# after reading how mochi.tv presents the same thing: every card and every watch
# page there carries the creator's handle and avatar, so making something buys
# you a visible name. We already record strictly more than they do — author,
# model, prompt, seed and cost, per leaf — and published none of it as identity.
# The receipts table listed stage, form, length, cost, status and screening and
# had NO "made by" column at all, on the one page whose whole claim is that the
# audit trail is public.
#
# The `author` field is free prose, not a handle ("pipeline/render_t1.py
# (deterministic compile of ...)"), so it is normalised to something short enough
# to sit on a card. The normaliser is deliberately DUMB and falls through to the
# raw author rather than guessing: an unrecognised credit shows up as itself and
# is legible as unrecognised, which is the failure mode we want. It never invents
# a name — `unattributed` is a real answer and is shown as one.
_CREDIT_RULES = (
    (re.compile(r"founding author|^founder\b", re.I), "founder"),
    (re.compile(r"^pipeline/", re.I), "pipeline"),
    (re.compile(r"^steward\b", re.I), "steward"),
    (re.compile(r"claude-fable-5", re.I), "claude-fable-5"),
    (re.compile(r"claude-opus-5", re.I), "claude-opus-5"),
)


def credit_label(meta: dict) -> str:
    """Who or what made this version, short enough for a card.

    Reads `author` first and `model` only as a fallback, because a model named
    in `author` is already the credit ("claude-fable-5 (delegated steward)")
    while a `model` beside a human author is the tool, not the maker.
    """
    author = str(meta.get("author") or "").strip()
    for rx, label in _CREDIT_RULES:
        if rx.search(author):
            return label
    if author:
        # cut at the first parenthetical or dash — the prose after it is
        # provenance detail that belongs in the receipt, not on a card
        head = re.split(r"[(—-]", author)[0].strip().rstrip(",;")
        return head[:28] or "unattributed"
    model = str(meta.get("model") or "").strip()
    if model and model.lower() != "none":
        return re.split(r"[(—+]", model)[0].strip()[:28]
    return "unattributed"


def node_credits(n: dict) -> list:
    """Distinct credits for a node, in the order its versions were published."""
    out = []
    for l in n.get("leaf_meta") or []:
        c = credit_label(l)
        if c not in out:
            out.append(c)
    return out


def credits_line(n: dict, limit: int = 3) -> str:
    """`made by x · y · z (+2)`, or "" when a node has no versions yet."""
    cs = node_credits(n)
    if not cs:
        return ""
    shown = " · ".join(html.escape(c) for c in cs[:limit])
    more = f" +{len(cs) - limit}" if len(cs) > limit else ""
    return f'<span class="credits">made by {shown}{more}</span>'


def node_card(genome_id: str, n: dict, depth: int) -> str:
    # D11: the workshop is a first-class destination — every node with a shot
    # list advertises its board from the front page, not two clicks deep.
    board = (f' · <a href="{genome_id}/{html.escape(n["slug"])}-shots.html">🎬 shot board</a>'
             if n.get("has_board") else "")
    teaser = f'<div class="teaser">{html.escape((n["teaser"][:160] + "…") if len(n["teaser"]) > 160 else n["teaser"])}</div>' if n["teaser"] else ""
    react = f' · <a href="{html.escape(n["reactions"]["url"])}">💧 react</a>' if n.get("reactions") else ""
    # the parent label carries lineage on a phone, where the rail is flattened
    lineage = (f'<div class="lineage">continues {html.escape(str(n["parent"]))} — '
               f'{html.escape(str(n.get("parent_title", "")))}</div>' if n.get("parent")
               else '<div class="lineage">the first episode</div>')
    kids = ""
    if n["children"]:
        kids = "<ul>" + "".join(node_card(genome_id, c, depth) for c in n["children"]) + "</ul>"
    n_vers = len(n["leaf_meta"])
    credit = credits_line(n)
    return f"""<li><div class="card">
{lineage}
{chips(n)}
<div class="title"><a href="{genome_id}/{html.escape(n['slug'])}.html">{html.escape(n['title'])}</a></div>
{teaser}
<div class="meta"><a href="{genome_id}/{html.escape(n['slug'])}.html">read / watch</a> · {n_vers} {'version' if n_vers == 1 else 'versions'}{board}{react}</div>
{f'<div class="meta">{credit}</div>' if credit else ''}
</div>{kids}</li>"""


# ------------------------------------------------------------------ node pages

def audio_credits(node_dir: Path) -> str:
    """Markdown crediting every attribution-required sound this node uses.

    Reads the node's own audio-sources/SOURCES.md table and keeps the rows whose
    licence actually asks for a credit — CC0 and public domain do not, so listing
    them would bury the two that matter. Returns "" when there is nothing owed,
    so nodes with no recorded audio grow no empty section.
    """
    src = node_dir / "audio-sources" / "SOURCES.md"
    if not src.exists():
        return ""
    owed = []
    for line in src.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        licence = cells[3]
        # CC BY asks for credit; CC0 and public domain do not. Match the licence
        # TOKEN with its suffixes, and read the verdict off the suffix group —
        # a first cut searched the leftover text for "nc|sa|nd" and matched the
        # "nd" in "credit Gravity Sound", silently crediting nobody.
        m = re.search(r"cc[-\s]?by((?:[-\s](?:nc|sa|nd))*)", licence, re.I)
        if not m or m.group(1).strip():
            continue                     # not CC BY, or a -NC/-SA/-ND variant
        owed.append(f"- {cells[2]} — {licence}")
    if not owed:
        return ""
    return ("Used under Creative Commons Attribution. The licence permits this "
            "freely; crediting the author is the condition it asks in return.\n\n"
            + "\n".join(owed) + "\n")


def render_node_page(g: dict, n: dict) -> str:
    genome_id = g["tree"]["id"]
    ep = episode_no(g, n)
    ep_word = f"Episode {ep}" if ep else f"Branch {n['id']}"

    def md_chunk(text: str) -> str:
        out = md_to_html(text, base=f"genomes/{genome_id}/nodes/{n['slug']}")
        # sibling links (../<slug>/node.md) become site pages
        return re.sub(r'href="[^"]*?/?([^/"]+)/node\.md"', r'href="\1.html"', out)

    sections = split_sections(n["md"])
    preamble = re.sub(r"^#\s+[^\n]*\n", "", sections[0][1]).strip().strip("-").strip()
    story_md, prod_md = [], ([("The file's own header", preamble)] if preamble else [])
    for head, text in sections[1:]:
        if not text:
            continue
        (story_md if head.startswith(("State change", "Hook", "Script")) else prod_md).append((head, text))

    # CC BY sound is PERMISSION WITH A CONDITION, and the condition is a credit.
    # licence_gate says "allow" for CC BY and stops there — it checks whether a
    # licence lets us use an asset, never whether we did the thing it asks in
    # return. So two Gravity Sound recordings have been in the published episode
    # with the credit living only in a repo file that was never copied to the
    # site: "Gravity Sound" appeared nowhere in _site at all. We cannot ask
    # reusers to credit us under our own CC BY while quietly not crediting the
    # person we borrowed from.
    credits = audio_credits(n["dir"])
    if credits:
        prod_md.append(("Sound credits", credits))

    # 1 — one player, the current lead cut, with a plain caption
    lead = lead_take(n)
    player_html = ""
    if lead:
        src = f'leaves/{html.escape(str(lead["content"]))}'
        pos = poster(n["dir"] / "leaves" / str(lead["content"]),
                     f"{genome_id}/posters/{lead['leaf']}.jpg", first_still(n["dir"]))
        bits = [ep_word, dur_label(lead.get("seconds")), cost_label(lead)]
        cap = " · ".join(b for b in bits if b)
        player_html = (
            f'<figure class="phone"><video controls playsinline preload="metadata"'
            f'{poster_attr(pos, "../")} src="{src}"></video>'
            f'<figcaption>{html.escape(cap)} · {html.escape(stage_word(lead))} '
            f'<span class="chip">{html.escape(str(lead["leaf"]))}</span></figcaption></figure>')

    # 2 — the action row: react, branch, workshop, rate this cut
    acts = []
    if n.get("reactions"):
        acts.append(f'<a class="btn" href="{html.escape(n["reactions"]["url"])}">💧 React</a>')
    acts.append('<a class="btn ghost" href="../create.html">✍️ Branch this episode</a>')
    if n.get("has_board"):
        acts.append(f'<a class="btn ghost" href="{html.escape(n["slug"])}-shots.html">'
                    '🎬 Shot board</a>')
    if lead:
        rate = (f"{REPO_URL}/issues/new?template=screening.yml"
                f"&title=screening%3A%20{lead['leaf']}&leaf={lead['leaf']}")
        acts.append(f'<a class="btn ghost" href="{rate}">★ Rate this cut</a>')
    actions = f'<p class="actions">{" ".join(acts)}</p>'

    # 3 — other cuts, one fold down, each with a date, a length and a reason
    others = [l for l in live_videos(n) if not lead or l["leaf"] != lead["leaf"]]
    others.sort(key=lambda l: (str(l.get("tier")), str(l.get("leaf"))), reverse=True)
    cuts_html = ""
    if others:
        figs = []
        for l in others:
            pos = poster(n["dir"] / "leaves" / str(l["content"]),
                         f"{genome_id}/posters/{l['leaf']}.jpg", first_still(n["dir"]))
            why = str(l.get("note") or WHY_BY_TIER.get(str(l.get("tier")))
                      or l.get("form") or "").strip().replace("\n", " ")
            if len(why) > 180:
                why = why[:177].rstrip() + "…"
            if not l.get("note") and footage_line(l):
                why = f"{why} — {footage_line(l)}"   # two old cuts differ by camera
            meta = " · ".join(b for b in [str(l["leaf"]), stage_word(l),
                                          dur_label(l.get("seconds")),
                                          leaf_date(l), cost_label(l)] if b)
            figs.append(
                f'<figure class="phone"><video controls playsinline preload="none"'
                f'{poster_attr(pos, "../")} src="leaves/{html.escape(str(l["content"]))}"></video>'
                f'<figcaption>{html.escape(meta)}<span class="why">{html.escape(why)}</span>'
                f'</figcaption></figure>')
        cuts_html = (f'<details class="drawer"><summary>Other cuts of this episode '
                     f'({len(others)})</summary><div class="drawer-body">'
                     f'<p class="smallprint">Nothing is deleted here: every earlier cut stays '
                     f'watchable, so you can see what changed and why.</p>'
                     f'<div class="cuts">{"".join(figs)}</div></div></details>')

    # 4 — where this episode sits in the story
    nav_bits = []
    if n.get("parent"):
        p = g["nodes"][n["parent"]]
        pep = episode_no(g, p)
        nav_bits.append(f'<a href="{html.escape(p["slug"])}.html"><span class="k">'
                        f'← {"Episode " + str(pep) if pep else "Continues from"}</span>'
                        f'{html.escape(p["title"])}</a>')
    for c in sorted(n["children"], key=lambda c: not c.get("trunk")):  # canon first
        cep = episode_no(g, c)
        nav_bits.append(f'<a href="{html.escape(c["slug"])}.html"><span class="k">'
                        f'{"Episode " + str(cep) + " →" if cep else "Continues as →"}</span>'
                        f'{html.escape(c["title"])}</a>')
    epnav = f'<nav class="epnav">{"".join(nav_bits)}</nav>' if nav_bits else ""

    # 5 — the script, behind a spoiler guard (it ends on the cliffhanger)
    story_html = ""
    if story_md:
        inner = "".join(f'<h2>{html.escape(h)}</h2>{md_chunk(t)}' for h, t in story_md)
        story_html = (f'<details class="drawer"><summary>Read the full script — spoilers'
                      f'</summary><div class="drawer-body screenplay">{inner}</div></details>')

    # 6 — the receipts: every render of this episode and what it cost
    def leaf_cell(l):
        content = str(l.get("content", ""))
        if content.endswith(".html"):
            return f'<a href="leaves/{html.escape(content)}"><code>{html.escape(str(l["leaf"]))}</code></a>'
        return f'<code>{html.escape(str(l["leaf"]))}</code>'

    def screen_cell(l):
        leaf_id = str(l["leaf"])
        means = ""
        sc = (n.get("screening") or {}).get("leaves", {}).get(leaf_id)
        if sc:
            avg = " ".join(f"{k[:4]} {v}" for k, v in sc["means"].items())
            means = f'<span class="chip">{html.escape(avg)} ({sc["ratings"]}×)</span> '
        url = f"{REPO_URL}/issues/new?template=screening.yml&title=screening%3A%20{leaf_id}&leaf={leaf_id}"
        return f'{means}<a href="{url}">rate</a>'

    leaves_rows = "".join(
        f"<tr><td>{leaf_cell(l)}</td><td>{html.escape(stage_word(l))}</td>"
        f"<td>{html.escape(str(l['form']))}</td>"
        f"<td>{html.escape(dur_label(l.get('seconds')) or '—')}</td>"
        f"<td>{html.escape(credit_label(l))}</td>"
        f"<td>${l['cost_usd']:.2f}</td>"
        f"<td>{html.escape(str(l['status']))}</td><td>{screen_cell(l)}</td></tr>"
        for l in n["leaf_meta"]
    )
    receipts_html = f"""<details class="drawer"><summary>Every render &amp; its receipt
({len(n['leaf_meta'])})</summary><div class="drawer-body">
<p class="smallprint">A <em>leaf</em> is one render of this episode — script, storyboard, animatic
or film. Every one publishes its prompt, model, seed and cost: this table is the audit trail.</p>
<table><tr><th>version</th><th>stage</th><th>form</th><th>length</th><th>made by</th><th>cost</th><th>status</th><th>screening</th></tr>{leaves_rows}</table>
<p class="smallprint"><strong>Screening:</strong> rate any version (continuity, character, vibe) — the
crowd narrows the shortlist, the author's taste file decides. Ratings are harvested into this
episode's <code>sap/screening.yaml</code>.</p></div></details>"""

    # 7 — watering (compute is always open; money waits on a founder key-turn)
    rail = (g["config"].get("watering_rail") or {})
    link, confirmed = rail.get("payment_link"), rail.get("confirmed_by_founder")
    if link and confirmed:
        water_body = f"""<p><a class="btn" href="{html.escape(str(link))}">💧 Fund a render of {html.escape(n['id'])}</a></p>
<p class="smallprint">Watering funds <strong>specific renders</strong>, split
<code>costs-first-70-30-v1</code> (the render's published cost is reimbursed first; the remainder
splits 70% author / 30% commons). Mention <code>{html.escape(n['id'])}</code> with your
contribution — every drop lands in the <a href="{REPO_URL}/blob/main/ledger/watering.csv">public
ledger</a>. Or water with <strong>compute</strong>: re-render a version with your own key and submit it
(<a href="{REPO_URL}/blob/main/WATERING.md">how →</a>).</p>"""
    else:
        water_body = f"""<p class="smallprint">💧 Money watering opens soon (one founder key-turn away).
Watering with <strong>compute</strong> is open now: re-render any version of this episode with your own
key or free GPU (<a href="{REPO_URL}/blob/main/pipeline/kaggle/render-kaggle.ipynb">the Kaggle
notebook</a> runs at $0) and submit it — provenance in, ledger row yours.
<a href="{REPO_URL}/blob/main/WATERING.md">How watering works →</a></p>"""
    water_html = (f'<details class="drawer"><summary>Water this branch</summary>'
                  f'<div class="drawer-body">{water_body}</div></details>')

    # 8 — reactions: two counts, never a contradiction
    react_html = ""
    if n.get("reactions"):
        vitals = ""
        if n.get("sap"):
            s = n["sap"]
            emoji = {"+1": "👍", "-1": "👎", "laugh": "😄", "confused": "😕", "heart": "❤️",
                     "hooray": "🎉", "rocket": "🚀", "eyes": "👀"}
            picked = " ".join(f"{emoji[k]} {v}" for k, v in s["reactions"].items() if v)
            total = s.get("reactions_total", sum(s["reactions"].values()))
            drops = picked or f"💧 {total} reactions"
            vitals = (f'<p><span class="chip">{drops}</span>'
                      f'<span class="chip">💬 {s["comments"]} comments</span>'
                      f'<span class="chip">harvested {html.escape(str(s["harvested_at"])[:10])}</span></p>')
        react_html = f"""<h2>Sap — the reactions to this episode</h2>
{vitals}
<p><a class="btn" href="{html.escape(n['reactions']['url'])}">💧 React / comment</a></p>
<p class="smallprint">Reactions are public and they order this branch against its rivals —
counted into the tree once a day. Commenting needs a free GitHub account; no account?
Just tell someone about it — word of mouth is sap too.</p>"""

    # 9 — production detail, jargon and all, one fold down
    prod_html = ""
    if prod_md:
        inner = "".join(f'<h2>{html.escape(h)}</h2>{md_chunk(t)}' for h, t in prod_md)
        board_line = (f'<p><a href="{html.escape(n["slug"])}-shots.html">🎬 Shot board — every beat’s '
                      f'recipe &amp; takes, forkable →</a></p>' if n.get("has_board") else "")
        prod_html = (f'<details class="drawer"><summary>Production notes &amp; provenance</summary>'
                     f'<div class="drawer-body"><p class="smallprint">House shorthand: a '
                     f'<em>node</em> is an episode, a <em>leaf</em> is one render of it, '
                     f'<em>T0–T3</em> are the stages script → storyboard → animatic → film, and '
                     f'R1/R4/R5/R7 are numbered taste rules in the author’s public taste file.</p>'
                     f'{board_line}{inner}</div></details>')

    # a stranger lands here first from a shared link — one line says what show
    # this is and where its beginning lives, before the episode's own hook
    premise = (f'<p class="smallprint">From <strong>{html.escape(g["tree"]["title"])}</strong>, '
               f'a series growing in Banyan City: an engineer wakes up as a tree, and the '
               f'audience picks the story\'s path. '
               f'<a href="../watch.html">Walk it from the start →</a></p>')
    body = f"""<p class="eyebrow">{html.escape(eyebrow_for(g, n))}</p>
<h1>{html.escape(n['title'])}</h1>
<p class="lede">{html.escape(n['teaser'])}</p>
{premise}
<p>{chips(n)}</p>
{player_html}
{actions}
{cuts_html}
{epnav}
{story_html}
{react_html}
{receipts_html}
{water_html}
{prod_html}
<div class="card strip"><div class="ic">✍️</div><div>
<div class="title">Continue this episode your way</div>
<p>Anyone may continue this moment differently. Declare <code>{html.escape(n['id'])}</code> as your
parent — that is the only obligation. Rival continuations live side by side; none gets deleted.</p>
<p><a class="btn ghost" href="../create.html">Write your own episode →</a></p></div></div>
{LEGEND}"""
    return page(f"{n['id']} — {n['title']} · {g['tree']['title']}", body, depth=1,
                path=f"{g['tree']['id']}/{n['slug']}.html", desc=n.get("teaser") or "")


def live_fork(g: dict):
    """The tree's open question, derived from lineage: the trunk tip whose
    children are 2+ competing non-trunk siblings — the fork awaiting a call."""
    nodes = g["nodes"]
    for tid, tn in nodes.items():
        if not tn.get("trunk"):
            continue
        kids = [n for n in nodes.values() if n.get("parent") == tid]
        if len(kids) >= 2 and not any(k.get("trunk") for k in kids):
            return tn, kids
    return None


def season_strip(g: dict) -> str:
    figs = []
    gid = g["tree"]["id"]
    for i, n in enumerate(trunk_chain(g), 1):
        leaf = best_t3(n)
        if not leaf:
            continue
        pos = poster(n["dir"] / "leaves" / str(leaf["content"]),
                     f"{gid}/posters/{leaf['leaf']}.jpg", first_still(n["dir"]))
        dur = dur_label(leaf.get("seconds"))
        figs.append(
            f'<figure><video controls playsinline preload="none"{poster_attr(pos)} '
            f'src="{gid}/leaves/{html.escape(str(leaf["content"]))}"></video>'
            f'<figcaption><span class="n">EP {i}</span> · '
            f'<a href="{gid}/{html.escape(n["slug"])}.html">{html.escape(n["title"])}</a>'
            f'{" · " + dur if dur else ""}</figcaption></figure>')
    return f'<div class="season">{"".join(figs)}</div>' if figs else ""


# ----------------------------------------------------------------- flat pages

def render_create() -> str:
    """The participation storefront: write an episode right here, no git, and
    the security model spelled out in plain words."""
    body = f"""<p class="eyebrow">ANYONE CAN WRITE THE NEXT ONE</p>
<h1>✍️ Write your own episode</h1>
<p class="lede">Every episode of this show can be continued <em>differently</em> — by you.
No permission needed, no writing credits checked. The tree polices lineage, never direction.</p>

<h2>Write it here</h2>
<form class="compose" action="{REPO_URL}/issues/new" method="get">
<input type="hidden" name="template" value="branch-submission.yml">
<label>Which episode does yours continue?
<input name="parent" placeholder="004, or 006a — any episode id from the tree" required></label>
<label>Your episode’s title
<input name="title" placeholder="branch: The Second Sunset"></label>
<label>Your episode — script, beats or prose (300–500 words ≈ 90 seconds)
<textarea name="story" rows="10" placeholder="Two things every episode needs: something must CHANGE (the world, a relationship, or what someone knows), and it must end on a real hook — not a tease."></textarea></label>
<label>How to credit you
<input name="credit" placeholder="@yourhandle — authorship is permanent and public"></label>
<button class="btn" type="submit">Send it to the tree →</button>
<p class="hint">Submitting opens a pre-filled public thread on the repo with your text in it — a free
account, no git commands, nothing installed. The steward turns it into a real branch with your name in
the metadata. Nothing you write here is sent anywhere until you press the button.</p>
</form>

<h2>What happens to it</h2>
<ol class="steps">
<li><b>Pick your parent.</b> Any episode — the latest, or one from way back whose story you'd have
turned another way. Your episode declares which one it continues. That declaration is the only
obligation in the entire system.</li>
<li><b>Write it.</b> A ~90-second script. Two rules bind everyone, including the AI steward:
something real must change (a relationship, the world, what someone knows), and it must end on a hook
that's a real state change, not a tease.</li>
<li><b>It gets rendered.</b> The $0 pipeline (storyboard → voiced animatic) runs for anyone's
episode. Want it <em>filmed</em>? <a href="{REPO_URL}/blob/main/REGROW.md">Render it yourself with
free tools</a> — or let watering fund it.</li>
<li><b>The tree decides its place.</b> Readers react (💧 on each episode page); the crowd narrows;
the author's <a href="{REPO_URL}/blob/main/taste/sapling.founder.v0.3.md">public taste rules</a> pick
what leads the canon — citing which rule drove the call, in the commit log. Branches that don't lead
are <strong>never deleted</strong>: they stay alive, watchable, and can take the lead later if
readers water them.</li>
</ol>

<h2>Has anyone actually done this?</h2>
<p class="card strip"><span class="ic">🎬</span><span>Straight answer: <strong>no reader-written
episode has landed yet — yours would be the first.</strong> What <em>has</em> landed is crowd
<em>footage</em>: several shots in episode 1's current cut were made by someone else on their own
tools and handed back, credited per shot on the
<a href="sapling/001-capability-inventory-shots.html">shot board</a> and in the film's provenance.
Same door, same rules, one step earlier in the pipeline.</span></p>

<h2>The advanced door: git</h2>
<p class="smallprint">If you already live in a terminal: fork the <a href="{REPO_URL}">repo</a>, add
your node folder + one line in <code>lineage.yaml</code> naming your parent, open a pull request.
The <a href="{REPO_URL}/issues/new?template=branch-submission.yml">plain form</a> above is the same
door without the plumbing.</p>

<h2>"Wait — can anyone just edit the story?"</h2>
<p class="notice">No. The repo is world-<em>readable</em>, but only the founder can merge.
Your submission arrives as a pull request — publicly visible, untouchable by anyone else,
and part of the tree only once merged. A well-formed branch (parent declared, lint passing)
gets merged as policy; vandalism dies in the queue. One pair of hands on the canon,
everyone's hands on the pen.</p>

<h2>Or plant your own tree entirely</h2>
<p>Don't want to write in this world? Take the whole framework — pipeline, site, governance —
rename it, and grow your own story from seed: <a href="{REPO_URL}/blob/main/SEED.md">SEED.md</a>
is the checklist, and the taste-extraction interview turns <em>your</em> instincts into
<em>your</em> rulebook. The one unamendable rule of this place is that this right can never
be revoked.</p>

<p><a class="btn ghost" href="watch.html">▶ Watch the season first</a></p>
{LEGEND}"""
    return page("Write your own episode — Banyan City", body, path="create.html",
                desc="Continue any episode of the tree your way — no permission needed. "
                     "Write it on the page, declare your parent. The tree decides in the open.")


FEED_JS = """<script>
/* Progressive enhancement only: with JS off the feed is seven ordinary players
   in story order, and CSS scroll-snap still does the paging. */
(function () {
  var eps = [].slice.call(document.querySelectorAll('.ep'));
  if (!eps.length || !('IntersectionObserver' in window)) return;
  var vids = eps.map(function (s) { return s.querySelector('video'); });
  vids.forEach(function (v) {
    if (!v) return;
    v.addEventListener('click', function () { v.muted = false; }, { once: true });
    v.addEventListener('ended', function () {
      var i = vids.indexOf(v);
      if (eps[i + 1]) eps[i + 1].scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  });
  /* a background tab must not keep decoding video: IntersectionObserver
     still reports "visible" for a scrolled-into-view player in a hidden
     tab, so seven autoplaying episodes kept the GPU busy in tabs nobody
     was looking at (founder's Mac, 2026-07-31). */
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) vids.forEach(function (v) { if (v) v.pause(); });
  });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var v = e.target.querySelector('video');
      if (!v) return;
      if (e.isIntersecting && e.intersectionRatio > 0.6) {
        var i = vids.indexOf(v), nx = vids[i + 1];
        if (nx && nx.preload === 'none') nx.preload = 'metadata';
        v.muted = true;                       /* autoplay needs muted */
        var p = v.play(); if (p && p.catch) p.catch(function () {});
      } else if (!v.paused) { v.pause(); }
    });
  }, { threshold: [0, 0.6] });
  eps.forEach(function (s) { io.observe(s); });
})();
</script>"""


# --------------------------------------------------------------- the walk
# Watching IS walking the tree. Every episode ends on its own cliffhanger
# question; the real branches of the story appear as doors; you pick one and
# keep walking. The path back to the root is unique (it's a tree), so the
# trail needs no state, no account, no JS — every step is a shareable URL.
# Dead ends aren't dead: a growing tip is the invitation to write the next
# branch. This page family is the product's thesis made navigable.

WALK_JS = """<script>
/* Enhancement only: when the episode ends, bring the fork into view. */
document.addEventListener('DOMContentLoaded', () => {
  const v = document.querySelector('.phone.big video');
  const next = document.querySelector('.doors') || document.querySelector('.tip');
  if (v && next) v.addEventListener('ended', () => {
    next.classList.add('now');
    next.scrollIntoView({behavior: 'smooth', block: 'center'});
  });
});
</script>"""


def ancestors(g: dict, n: dict) -> list:
    """Root-first chain of parents above n (n itself excluded)."""
    chain, cur = [], n
    while cur.get("parent"):
        cur = g["nodes"][cur["parent"]]
        chain.append(cur)
    return chain[::-1]


def door_thumb(g: dict, c: dict):
    """A frame of the branch behind the door, when one exists."""
    gid = g["tree"]["id"]
    lt = lead_take(c)
    if lt:
        return poster(c["dir"] / "leaves" / str(lt["content"]),
                      f"{gid}/posters/{lt['leaf']}.jpg", first_still(c["dir"]))
    st = first_still(c["dir"])
    if st is not None and st.exists() and OUT.exists():
        rel = f"{gid}/posters/door-{c['slug']}{st.suffix}"
        (OUT / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(st, OUT / rel)
        return rel
    return None


def hook_question(n: dict) -> str:
    """The cliffhanger, in the script's own words, as one question."""
    t = n.get("hook_raw") or ""
    m = re.search(r"question a viewer can state:\s*(.+)$", t, re.I | re.S)
    q = m.group(1).strip() if m else ""
    if not q:
        qs = re.findall(r"[^.?!]+\?", t)
        q = qs[-1].strip() if qs else ""
    q = q.rstrip(".").strip()
    if q and not q.endswith("?"):
        q += "?"
    return (q[:1].upper() + q[1:]) if q else ""


def last_fork(g: dict, n: dict):
    """Nearest ancestor where the story split — where a walker backtracks to."""
    for a in reversed(ancestors(g, n)):
        if len(a["children"]) >= 2:
            return a
    return None


def render_walk(g: dict, n: dict, path: str) -> str:
    """One step of the walk: the episode, its question, the doors."""
    gid = g["tree"]["id"]
    series = g["tree"]["title"]
    depth = path.count("/")
    root = "../" * depth

    def walk_href(other: dict) -> str:
        # the root step lives at watch.html; every other step under watch/
        if not other.get("parent"):
            return f"{root}watch.html"
        return (f"{other['slug']}.html" if depth else f"watch/{other['slug']}.html")

    chain = trunk_chain(g)
    ep_no = (chain.index(n) + 1) if n in chain else 0

    # the trail: unique path from the root to here — stateless by tree-ness
    ancs = ancestors(g, n)
    trail_bits = [f'<a href="{walk_href(a)}">{html.escape(a["id"])}</a>' for a in ancs]
    trail_bits.append(f'<span class="here">{html.escape(n["id"])} · you are here</span>')
    trail = f'<p class="trail rise">🌳 {" → ".join(trail_bits)}</p>'

    # the player — or, for a written-but-unfilmed branch, the honest state
    leaf = lead_take(n)
    if leaf:
        pos = poster(n["dir"] / "leaves" / str(leaf["content"]),
                     f"{gid}/posters/{leaf['leaf']}.jpg", first_still(n["dir"]))
        bits = [f"episode {ep_no} on the canon path" if ep_no else f"a branch of {n['parent']}",
                dur_label(leaf.get("seconds")), stage_word(leaf)]
        player = (f'<figure class="phone big rise"><video controls playsinline preload="metadata"'
                  f'{poster_attr(pos, root)} src="{root}{gid}/leaves/{html.escape(str(leaf["content"]))}">'
                  f'</video></figure>'
                  f'<p class="walk-meta">{html.escape(" · ".join(b for b in bits if b))}</p>')
    else:
        player = (f'<div class="panel tip rise"><div class="seed">📜</div>'
                  f'<p>This branch exists as a <strong>script</strong> so far — no film yet. '
                  f'<a href="{root}{gid}/{html.escape(n["slug"])}.html">Read it →</a> '
                  f'(anyone may render it; the page shows how).</p></div>')

    # the cliffhanger, verbatim from the script's hook
    q = hook_question(n)
    cliff = (f'<div class="cliff rise"><p class="k">the episode ends on a question</p>'
             f'<p class="q">{html.escape(q)}</p></div>') if q else ""

    # the doors: the story's real branches
    kids = sorted(n["children"], key=lambda c: (not c.get("trunk"), c["id"]))
    if kids:
        many = len(kids) > 1
        fork_line = (f'<p class="fork-line">the story splits {len(kids)} ways — pick yours</p>'
                     if many else '<p class="fork-line">the story continues</p>')
        doors = []
        for c in kids:
            th = door_thumb(g, c)
            img = (f'<img src="{root}{th}" alt="" loading="lazy" width="62" height="110">'
                   if th else '<span class="ph">🌿</span>')
            crown = ' <span class="chip trunk">canon</span>' if c.get("trunk") else ""
            teaser = c["teaser"]
            if len(teaser) > 110:   # cut at a word, not mid-syllable
                teaser = teaser[:110].rsplit(" ", 1)[0] + "…"
            doors.append(
                f'<a class="door{" canon" if c.get("trunk") else ""}" href="{walk_href(c)}">{img}'
                f'<span><span class="t">{html.escape(c["title"])}{crown}</span>'
                f'<span class="d">{html.escape(teaser)}</span>'
                f'<span class="go">▶ walk this way</span></span></a>')
        fork = fork_line + f'<div class="doors{" multi" if many else ""}">{"".join(doors)}</div>'
        if many:
            fork += ('<p class="smallprint" style="text-align:center">Both stay alive whichever '
                     'you pick — the crowd\'s reactions decide which leads the canon.</p>')
    else:
        bk = last_fork(g, n)
        back = (f' <a class="btn ghost" href="{walk_href(bk)}">↩ back to the last fork</a>'
                if bk else "")
        fork = (f'<div class="panel tip rise"><div class="seed">🌱</div>'
                f'<p><strong>You\'ve reached a growing tip of the tree.</strong><br>'
                f'No one has written what happens after this — yet.</p>'
                f'<p><a class="btn" href="{root}create.html">✍️ Write what happens next</a>{back}</p>'
                f'<p class="smallprint">Your continuation becomes a real branch of {html.escape(series)}: '
                f'rendered, published, and walkable right here.</p></div>')

    foot = (f'<p class="walk-foot"><a href="{root}{gid}/{html.escape(n["slug"])}.html">script, versions '
            f'&amp; receipts →</a> · <a href="{root}watch.html">start over at the root</a> · '
            f'<a href="{root}watch/season.html">play the canon path straight through →</a></p>')

    title_no = f"Ep {ep_no} — " if ep_no else ""
    body = f"""{trail}
<h1 style="text-align:center">{html.escape(n['title'])}</h1>
{player}
{cliff}
{fork}
{foot}"""
    return page(f"{title_no}{n['title']} — walk {series}", body, depth=depth, path=path,
                desc=n["teaser"] or f"Walk {series}: every episode ends on a question, "
                                    "and the branches are doors.",
                body_class="walk", tail=WALK_JS)


def render_watch(genomes: list) -> str:
    """The walk's front door: the root episode IS the watch page."""
    g = genomes[0]
    r = next((x for x in g["roots"] if x.get("trunk")), g["roots"][0])
    return render_walk(g, r, "watch.html")


def render_season(genomes: list) -> str:
    """The straight line, for people who just want the canon cut in order:
    one vertical snap feed, each episode a screen, the next plays itself."""
    eps = []
    for g in genomes:
        gid = g["tree"]["id"]
        for n in trunk_chain(g):
            leaf = best_t3(n)
            if leaf:
                eps.append((gid, g["tree"]["title"], n, leaf))
    total = len(eps)
    figs = []
    for i, (gid, series, n, leaf) in enumerate(eps, 1):
        pos = poster(n["dir"] / "leaves" / str(leaf["content"]),
                     f"{gid}/posters/{leaf['leaf']}.jpg", first_still(n["dir"]))
        dur = dur_label(leaf.get("seconds"))
        # only the first two episodes fetch up front; the rest load as you go
        pre = "metadata" if i <= 2 else "none"
        figs.append(
            f'<section class="ep" id="ep{i}">'
            f'<p class="bar">ep {i} of {total}{" · " + dur if dur else ""}</p>'
            f'<figure class="phone"><video controls playsinline preload="{pre}"{poster_attr(pos, "../")} '
            f'src="../{gid}/leaves/{html.escape(str(leaf["content"]))}"></video>'
            f'<figcaption>{html.escape(n["title"])} · '
            f'<a href="../{gid}/{html.escape(n["slug"])}.html">script, versions &amp; branches →</a>'
            f'</figcaption></figure></section>')
    series = genomes[0]["tree"]["title"] if genomes else "the season"
    body = f"""<p class="eyebrow">{html.escape(series.upper())} · {total} EPISODES · THE CANON PATH, IN ORDER</p>
<h1>▶ Play it straight through</h1>
<p class="lede">The cut that leads the story, start to finish. Scroll down — the next one starts
itself. Prefer to choose at every cliffhanger? <a href="../watch.html">Walk the tree instead →</a></p>
<p class="smallprint">Each episode autoplays muted as it comes into view — tap the picture for sound.
(No JavaScript? Same episodes, played by hand.)</p>
{''.join(figs)}
<p><a class="btn ghost" href="../watch.html">🌳 Walk the tree</a>
<a class="btn ghost" href="../create.html">✍️ Write the next one</a></p>
{LEGEND}"""
    return page(f"{series}, season 1 — straight through", body, depth=1, path="watch/season.html",
                desc=f"Binge {series}: the canon cut of every episode, in order, "
                     "in one vertical feed.",
                body_class="feed", tail=FEED_JS)


def render_index(genomes: list) -> str:
    hero_video, hero_cap = "", ""
    for g in genomes:
        chain = trunk_chain(g)
        lead = best_t3(chain[0]) if chain else None
        if lead and not hero_video:
            gid = g["tree"]["id"]
            pos = poster(chain[0]["dir"] / "leaves" / str(lead["content"]),
                         f"{gid}/posters/{lead['leaf']}.jpg", first_still(chain[0]["dir"]))
            bits = ["Episode 1", dur_label(lead.get("seconds")), cost_label(lead)]
            hero_cap = " · ".join(b for b in bits if b)
            hero_video = (
                f'<figure class="phone"><video controls playsinline preload="metadata"'
                f'{poster_attr(pos)} src="{gid}/leaves/{html.escape(str(lead["content"]))}">'
                f'</video><figcaption>{html.escape(hero_cap)}</figcaption></figure>')

    sections = []
    for g in genomes:
        t = g["tree"]
        gid = t["id"]
        n_nodes = len(g["nodes"])
        n_leaves = sum(len(n["leaf_meta"]) for n in g["nodes"].values())
        chain = trunk_chain(g)
        fork = live_fork(g)
        fork_html = ""
        if fork:
            tip, kids = fork
            vs = " <em>vs</em> ".join(
                f'<a href="{html.escape(gid)}/{html.escape(k["slug"])}.html">'
                f'{html.escape(k["id"])} — {html.escape(k["title"])}</a>' for k in kids)
            fork_html = (f'<div class="fork rise"><div class="k">⚡ live fork at the tip</div>'
                         f'<p><a href="{html.escape(gid)}/{html.escape(tip["slug"])}.html">'
                         f'{html.escape(tip["title"])}</a> ends on one cliffhanger, '
                         f'paid off {len(kids)} different ways: {vs}. '
                         f'Same debt, competing payments — watch both, react; the story is decided '
                         f'on material, not votes.</p></div>')
        sections.append(f"""<h2 id="episodes">🌱 {html.escape(t['title'])} — season 1</h2>
<p class="smallprint">{len(chain)} episodes on the canon path · {n_nodes} episodes in all ·
{n_leaves} published versions · every one re-renderable by anyone</p>
{season_strip(g)}
{fork_html}
<h2>How it works</h2>
<div class="how">
<div class="card"><div class="k">1 · watch</div><div class="title">Ninety seconds each</div>
<p>Vertical, voiced, animated. Start at episode 1 and keep scrolling.</p></div>
<div class="card"><div class="k">2 · react</div><div class="title">Your reactions steer it</div>
<p>💧 on any episode. Reactions are public data and they order rival continuations.</p></div>
<div class="card"><div class="k">3 · branch</div><div class="title">Write the next one</div>
<p>Continue any episode differently. Yours lives beside the canon cut, never deleted.</p></div>
</div>
<h2>Every branch of the tree</h2>
<p class="smallprint">Rival continuations coexist as siblings — all alive, none rejected. The cut that
leads the story is marked <span class="chip trunk">canon</span>.</p>
<ul class='tree'>{"".join(node_card(gid, r, 0) for r in g["roots"])}</ul>""")

    # Banyan City is the place; Sapling is the (first) series growing in it.
    # The hero introduces the city in one line, then hands over to the series.
    body = f"""<div class="hero rise">
<div class="seal">🌳</div>
<p class="eyebrow">A CITY OF BRANCHING STORY TREES</p>
<h1>Banyan City</h1>
<p class="sub">Series grow here like trees: any episode can be continued differently,
rival branches live side by side, and the audience's reactions decide which one leads.</p>
<p class="eyebrow" style="margin-top:1.6rem">NOW GROWING · SAPLING · SEASON 1</p>
<p class="logline">An engineer dies debugging production at 3 a.m. and reincarnates as a banyan
sapling. He can't move, fight, or flee — only sense, grow, and make the space around him worth
staying in.</p>
{hero_video}
<p class="cta"><a class="btn" href="watch.html">▶ Watch Sapling</a>
<a class="btn ghost" href="create.html">✍️ Write an episode</a></p>
<p class="smallprint">These are first renders, rough on purpose — free or near-free, and every cost is
published beside the film. Rendered a better one on your own GPU or key? Submit it; the tree keeps
every version. <a href="{REPO_URL}/blob/main/WATERING.md">How to water with compute →</a></p>
</div>
{''.join(sections)}
<h2>⚙️ The machine</h2>
<div class="card strip rise"><div class="ic">⚙️</div><div>
<div class="title">This show makes itself in public</div>
<p>Every episode publishes its complete recipe — approved frames, exact prompts, every take with
provenance. Read <a href="machine.html">how the whole loop runs</a>, open
<a href="sapling/001-capability-inventory-shots.html">episode 1's shot board</a> to see it live, or
grab an <a href="{REPO_URL}/issues?q=is%3Aissue+is%3Aopen+label%3Arender-request">open
render request</a> and hand back a shot made with your own tools — your name goes in the public
ledger.</p></div></div>
<hr>
<h2>The rules of this place, in one breath</h2>
<p>Anyone may <strong>branch</strong> any episode (declare your parent — the only obligation).
Citizens <strong>water</strong> the branches they love; unwatered branches sleep, never die.
One author's <strong>taste file</strong> decides the canon; disagreement is watering a rival branch, not a vote.
All reactions and money are <strong>open data</strong>. And anyone may <strong>fork the whole city</strong> —
take everything, rename it, go. <a href="city.html">Full text →</a></p>
<p class="smallprint">🎬 Now growing: the show is choosing its video model — the same three shots
rendered on every candidate platform, scored in the open.
<a href="trials/index.html">The platform trials →</a></p>
{LEGEND}"""
    return page("Banyan City — a story tree", body)


def render_city() -> str:
    ids = {"PROMISE.md": "promise", "GUIDELINES.md": "guidelines", "VOCABULARY.md": "glossary"}
    parts = []
    for fname in ("PROMISE.md", "GUIDELINES.md", "VOCABULARY.md"):
        parts.append(f'<section id="{ids[fname]}">'
                     f'{demote(md_to_html((REPO / fname).read_text()))}</section>')
    body = f"""<p class="eyebrow">THE RULES · PERMANENT, EXCEPT WHERE THEY SAY OTHERWISE</p>
<h1>The rules of this city</h1>
<p class="lede">Three texts: what this place promises (the Promise), how citizens act (the
Guidelines), and what the tree words mean (the <a href="#glossary">Glossary</a> — start there if
leaf, sap and trunk are new to you).</p>
<hr>
{"<hr>".join(parts)}
<p class="notice">These texts are canonical and live in
<a href="{REPO_URL}">the repository</a> — amendable by citizens
per Guideline 6, except the right to branch and fork, which is permanent.
Open questions live in <a href="{REPO_URL}/blob/HEAD/DECISIONS.md">DECISIONS.md</a>.</p>"""
    return page("The City — Promise, Guidelines, Glossary", body, path="city.html")


def render_machine() -> str:
    body = ('<p class="eyebrow">HOW THIS SHOW IS MADE · EVERY STEP AUDITABLE</p>'
            + md_to_html((REPO / "MACHINE.md").read_text())
            + '<p class="smallprint">House shorthand used above: <em>node</em> = episode, '
              '<em>leaf</em> = one render of an episode, <em>sap</em> = reactions, '
              '<em>trunk</em> = the canon path, T0–T3 = script → storyboard → animatic → film. '
              f'<a href="city.html#glossary">Full glossary →</a></p>')
    return page("The Machine — how this operates", body, path="machine.html",
                desc="The whole loop on one page: script, approval, stills, takes, "
                     "assembly, reactions, branching.")


AXES = ["adherence", "motion", "look", "nativeness", "consistency", "friction"]
WEIGHTED = {"adherence": 2, "consistency": 2}
AXIS_GLOSS = ("<b>adherence</b> did it film the prompt · <b>motion</b> does the movement read · "
              "<b>look</b> is it on style · <b>nativeness</b> born vertical or cropped · "
              "<b>consistency</b> same world shot to shot · <b>friction</b> how hard to get. "
              "1–5; adherence and consistency count double.")


def render_trials() -> str:
    """Public T3 platform-trials page: same three shots on every candidate,
    outputs + provenance + scores, all open data (§7.2)."""
    tdir = REPO / "pipeline" / "t3-trials"
    scores = (yaml.safe_load((tdir / "scores.yaml").read_text()) or {}).get("platforms") or {}

    outputs = {}
    outdir = tdir / "outputs"
    if outdir.exists():
        for pdir in sorted(p for p in outdir.iterdir() if p.is_dir()):
            clips = []
            for mp4 in sorted(pdir.glob("*.mp4")):
                # either naming convention (lg.sidecar_for) — a trial clip
                # brought in beside a `<name>.mp4.meta.yaml` used to render
                # with its recipe blank
                meta_f = lg.sidecar_for(mp4, lg.META_EXT)
                meta = yaml.safe_load(meta_f.read_text()) if meta_f else {}
                clips.append((mp4, meta or {}))
            if clips:
                outputs[pdir.name] = clips

    sections = []
    for plat in sorted(set(outputs) | set(scores)):
        rows, players = "", ""
        # A platform scored against a different prompt pack is not a rival on the
        # same bake-off — say so on every one of its rows, not in a footnote.
        pdata = scores.get(plat) or {}
        blurb = " ".join([str(pdata.get("model", ""))]
                         + [str((ax or {}).get("notes", "")) for ax in (pdata.get("shots") or {}).values()])
        flagged = ("not directly comparable" in blurb.lower()
                   or "not comparable" in blurb.lower())
        for mp4, meta in outputs.get(plat, []):
            pos = poster(mp4, f"trials/posters/{plat}-{mp4.stem}.jpg")
            dur = dur_label(mp4_seconds(mp4))
            players += (f'<figure class="phone"><video controls playsinline preload="none"'
                        f'{poster_attr(pos, "/")} '
                        f'src="/trials/{html.escape(plat)}/{html.escape(mp4.name)}"></video>'
                        f'<figcaption>shot {html.escape(str(meta.get("shot", mp4.stem)))}'
                        f'{" · " + dur if dur else ""}<br>'
                        f'{html.escape(str(meta.get("model", "model?")))}</figcaption></figure>')
        shot_scores = (scores.get(plat) or {}).get("shots") or {}
        for shot, ax in sorted(shot_scores.items()):
            ax = ax or {}
            filled = [(a, ax[a]) for a in AXES if isinstance(ax.get(a), (int, float))]
            missing_weighted = [a for a in WEIGHTED if not isinstance(ax.get(a), (int, float))]
            if filled and not missing_weighted:
                num = sum(v * WEIGHTED.get(a, 1) for a, v in filled)
                den = sum(WEIGHTED.get(a, 1) for a, _ in filled)
                total = f"<strong>{num / den:.1f}</strong>"
            elif filled:
                # a double-weighted axis is unscored: publishing a total here
                # would read as a verdict the founder has not given (R4)
                total = f'<span class="chip">partial · {len(filled)} of {len(AXES)} axes</span>'
            else:
                total = "—"
            note = html.escape(str(ax.get("notes", "") or ""))
            warn = ' <span class="chip hot">different prompts</span>' if flagged else ""
            cells = "".join(f'<td data-label="{a}">{ax.get(a) if ax.get(a) is not None else "·"}</td>'
                            for a in AXES)
            rows += (f'<tr><td data-label="shot"><strong>{html.escape(shot)}</strong>{warn}</td>'
                     f'{cells}<td data-label="weighted">{total}</td>'
                     f'<td data-label="notes">{note}</td></tr>')
        table = (f'<table class="scores"><thead><tr><th>shot</th>'
                 f'{"".join(f"<th>{a}</th>" for a in AXES)}<th>weighted</th><th>notes</th></tr>'
                 f'</thead><tbody>{rows}</tbody></table>') if rows else \
                '<p class="notice">Not scored yet.</p>'
        model = html.escape(str(pdata.get("model", "")))
        caveat = ('<p class="notice">⚠️ <strong>Not a like-for-like entry.</strong> These shots were '
                  'rendered from a different prompt pack than the other platforms, so the marks below '
                  'describe the output, not a ranking against its rivals — it has to be re-run on the '
                  'shared pack before it can win anything.</p>') if flagged else ""
        sections.append(f"<h2>{html.escape(plat)} <span class='chip'>{model}</span></h2>"
                        f'<div class="clips">{players}</div>{caveat}{table}')

    if not sections:
        sections.append('<p class="notice">No trial outputs yet — the founder is out gathering free-tier '
                        'renders. The protocol, prompts, and rubric below are already fixed, so results '
                        'can\'t be quietly re-rolled until they flatter.</p>')

    intro = demote(md_to_html((tdir / "README.md").read_text(), base="pipeline/t3-trials"))
    prompts = demote(md_to_html((tdir / "prompts.md").read_text(), base="pipeline/t3-trials"))
    body = (f'<p class="eyebrow">CHOOSING THE CAMERA · IN PUBLIC</p>'
            f'<h1>T3 platform trials</h1>'
            f'<p class="lede">Same three shots, every video model we can get our hands on, scored in '
            f'the open — we are picking the tool that films the show. Raw output and marks below, '
            f'nothing re-rolled until it flatters. (<em>T3</em> is the filmed tier: real footage, as '
            f'opposed to a storyboard or an animatic.)</p>'
            f'<p class="smallprint">{AXIS_GLOSS} Taste axes — motion, look, consistency — are the '
            f'author’s alone to fill (R4), so most rows are still partial on purpose.</p>'
            f"{''.join(sections)}<hr>"
            f'<details class="drawer"><summary>Protocol, candidates &amp; rubric</summary>'
            f'<div class="drawer-body">{intro}</div></details>'
            f'<details class="drawer"><summary>The three prompts</summary>'
            f'<div class="drawer-body">{prompts}</div></details>'
            f'<p><a class="btn ghost" href="../index.html">← Back to the tree</a></p>')
    return page("T3 platform trials — same three shots, every model", body, depth=1,
                path="trials/index.html",
                desc="Choosing Banyan City's video model in the open: the same three shots "
                     "rendered on each candidate platform, scored on a fixed rubric.")


CUTS = REPO / "cuts"
REVIEW_NODE = REPO / "genomes" / "sapling" / "nodes" / "001-capability-inventory"
# Every player on the review page carries this, and it is not softened anywhere.
# The failure this prevents is one sentence long: somebody opens the URL, sees a
# finished-looking 90-second film, and takes it for the episode.
CUT_STAMP = ('<p class="stamp"><b>WORKING CUT — NOT THE EPISODE.</b> '
             'The author has not passed this. It is here so he can screen it; '
             'nothing about it is settled and it is not what the show is.</p>')
# Said ONCE, above the queue, instead of on every card that stands on a guess —
# and said in one line, because on 2026-08-09 he read the five-line version of it
# and called the page yap. Everything the long one said is still true and still
# printed where it is actionable: the address of each guess and its confidence
# are in the item they belong to, and "nothing was published, posted, spent or
# made canon" is the record's job rather than a standing header's.
PROV_BANNER = ('<p class="notice standing">Some picks below are the machine’s '
               'guesses — flip anything.</p>')
# The line under "Your queue". Same rule: it labels the section, it does not
# explain the design of the section.
QUEUE_LEDE = '<p class="said">The argument behind each is one fold down.</p>'
# `checklist.lede:` OVERRIDES THAT ONE LINE, and the reason is ordering. Open
# items render in the order cuts.yaml lists them, and that order is not always
# the order of leverage: on 2026-08-10 the item gating twelve queued renders sat
# ninth because its card carries the "Episode 2" run heading and hoisting it
# would have left that heading captioning two episode-1 items. Moving prose to
# fix a sort is the wrong trade — a sentence naming the anchors costs nothing and
# reorders nothing. The `intro:` is NOT the place for it: that folds away behind
# a drawer, so anything written there is not what he sees first.


REVIEW_SRC = REPO / "review"
NOINDEX_META = '<meta name="robots" content="noindex, nofollow">'
ROBOTS_META_RE = re.compile(r"""<meta[^>]+name=["']robots["']""", re.I)
HEAD_OPEN_RE = re.compile(r"<head[^>]*>", re.I)


def review_page_dirs(src: Path = None) -> list:
    """Hand-authored pages under `review/<name>/index.html`.

    THE HOLE THIS CLOSES, measured 2026-08-10. A lane wrote a script-approval
    page to `review/approvals/index.html` — 131 KB, self-contained, asked for by
    the founder — and it 404'd, because the only thing `main()` publishes under
    `review/` is `render_review()`'s own `index.html`. Nothing was broken and
    nothing said so: `build_site.py` exited 0 and its link check passed, since
    check_links can only walk pages that reached `_site/`. **A page that is
    never copied is invisible to every gate that reads the output.** The absence
    had to become a fact something could read, and this function is that fact.

    The rule is deliberately narrow: a DIRECTORY under `review/` that carries
    its own `index.html`. `review/` is also the render lanes' scratch yard —
    contact sheets, hundreds of megabytes of working mp4s, per-round subdirs —
    and none of that is a page. Carrying an `index.html` is the author saying
    "this is meant to be read at a URL", which is exactly the distinction the
    publisher needs and the only one it should be making on its own.

    Ordering with `render_review()` is not an accident either: the cuts page
    owns `review/index.html` and these own `review/<name>/index.html`, so the
    two can never write the same file.
    """
    src = REVIEW_SRC if src is None else src
    if not src.is_dir():
        return []
    return [d for d in sorted(src.iterdir())
            if d.is_dir() and not d.name.startswith(".")
            and (d / "index.html").is_file()]


def unlisted_html(text: str) -> str:
    """Stamp `noindex, nofollow` on a page this module did not generate.

    Everything `page()` emits gets its robots meta from one argument (D17, and
    see page()'s own docstring on why meta rather than a robots.txt Disallow).
    A hand-authored page never passes through `page()`, so the review area's
    "reachable but not advertised" rule would rest on whoever wrote the file
    having remembered it — and the approvals page had no robots meta at all.
    The publisher stamps it instead, which makes unlisted a property of being
    published under `review/` rather than a property of the author's memory.

    An existing robots meta is left alone: a page may legitimately want
    `noindex, follow`, and overwriting a deliberate value is the publisher
    exceeding its remit. Insert point is inside `<head>` when there is one, and
    the top of the document otherwise — the approvals page is a bare fragment
    with no doctype, where a leading meta is hoisted into the implicit head.
    """
    if ROBOTS_META_RE.search(text):
        return text
    m = HEAD_OPEN_RE.search(text)
    if m:
        return text[:m.end()] + "\n" + NOINDEX_META + text[m.end():]
    return NOINDEX_META + "\n" + text


def inline_md(text: str) -> str:
    """One line of markdown with the paragraph wrapper taken off again."""
    out = md_to_html(str(text).strip())
    return re.sub(r"^<p>|</p>$", "", out.strip())


def render_review() -> str:
    """The unlisted review area: cuts the author has NOT passed, published so he
    can screen them from a phone (his decision, 2026-08-07 — DECISIONS.md D17).

    Two rules meet here and neither bends. STEWARDSHIP §6 still forbids MAKING
    media from a script he has not read — nothing on this page was; every beat
    comes from the approved 001 script. And the canon gate still holds: no cut
    becomes the episode without his verdict, which is why none of these has a
    leaf and why the stamp is on every player.

    Every file goes through publishable() before it is copied, exactly like the
    shot board's takes, and a blocked file is named as withheld rather than
    quietly dropped — a page that looks complete because the failures were
    hidden is the one outcome the gate exists to prevent.
    """
    cfg = yaml.safe_load((CUTS / "cuts.yaml").read_text(encoding="utf-8")) or {}
    meta = cfg.get("page") or {}
    outdir = OUT / "review"
    outdir.mkdir(parents=True, exist_ok=True)
    withheld, missing = [], []

    def url(rel: str) -> str:
        """The URL a browser must ask for, which is NOT the path on disk.

        This page lives at `_site/review/index.html` and is SERVED at `/review`
        — `vercel.json` sets `cleanUrls: true, trailingSlash: false`, and
        `/review/` 308-redirects to the slashless form, so there is no version
        of this URL with a directory in it. A relative `checklist/x.mp4`
        therefore means `/checklist/x.mp4` and 404s, which is what the founder
        saw on 2026-08-09: "images are broken". Every clip, poster, sheet and
        provenance link on this page had the same defect, the images only made
        it visible because there are now thirty of them.

        Root-absolute is the fix that does not depend on how the host feels
        about trailing slashes. The cost, stated because it is real: opening
        `_site/review/index.html` over `file://` no longer loads media, since
        `/review/…` is the filesystem root there. Serve the directory
        (`python3 -m http.server -d _site`) to preview it locally.
        """
        return "/review/" + html.escape(rel)

    def still_for(src: Path):
        """The pixels this clip actually holds, or NO poster at all.

        Four answers, and the two in the middle are the whole point:
          - the record names a still we can identify → that still, by bytes
          - the record names one we cannot → nothing, and a build warning. A
            poster is a promise about the clip; a wrong one is the review
            surface lying about footage, which is worse than a black rectangle.
          - the record names none and the cut IS an assembly, which its own
            record says by carrying `sources:` (its `model:` reads "per-beat —
            see sources") → the node's approved still. A 90-second cut of
            episode 1 really does contain that frame, so the poster is a true
            picture of the film rather than a guess about it.
          - the record names none and it is ONE SHOT → nothing, and a warning.
            THE CASE THIS CLOSES, measured on the live cuts.yaml 2026-08-08: the
            served episode-2 beat-1 clip `checklist/002b-b01-5b.mp4` records no
            still, and the old blanket fallback handed it `09-whoami.png` —
            episode ONE, beat NINE — as its poster on every host without ffmpeg,
            which is Vercel, which is the page he screens from his phone. "Which
            frame does this shot hold" has no answer when the record names none,
            and the honest way to say so is a blank player.

        Only ever asked about clips: the audio takes and contact sheets on this
        page go through serve_image(), which asks for no poster at all.
        """
        # hold_still records the frame as `source_still` in a `<name>.mp4.meta.yaml`;
        # the stem-only lookup missed it and every held clip fell back to the node's
        # first still, i.e. another beat's picture as the poster
        side = lg.sidecar_for(src, lg.META_EXT)
        if not side:
            return first_still(REVIEW_NODE)
        data = yaml.safe_load(side.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            return first_still(REVIEW_NODE)
        cand, why = poster_still(data, src, still_dirs(), first_still(REVIEW_NODE))
        if why:
            if why not in POSTER_WARNINGS:
                POSTER_WARNINGS.append(why)
            return None
        return cand

    def serve(rel: str):
        """Copy one media file plus its provenance record. (href, poster) or None."""
        src = CUTS / rel
        if not src.exists():
            missing.append(rel)
            return None
        ok, why = publishable(src)
        if not ok:
            withheld.append((rel, why))
            return None
        dst = outdir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        side = lg.sidecar_for(src, lg.META_EXT)
        if side:                               # records always travel (§7.2)
            shutil.copy(side, dst.with_name(side.name))
        pos = poster(src, f"review/posters/{Path(rel).stem}.jpg", fallback=still_for(src))
        return rel, pos

    def serve_image(rel: str):
        """The same copy-and-record contract as serve(), for a contact sheet.

        A separate function and not a branch inside serve(), because the two
        differ in the only part that matters: a clip needs a frame extracted to
        stand in for it, and a sheet already IS the picture. Everything that
        makes serve() trustworthy is kept — the licence gate decides, the
        provenance record travels beside the file, and a withheld or absent
        sheet lands in the same two lists as a withheld or absent clip, so the
        page reports a missing candidate frame exactly as loudly as it reports
        a missing cut.
        """
        src = CUTS / rel
        if not src.exists():
            missing.append(rel)
            return None
        ok, why = publishable(src)
        if not ok:
            withheld.append((rel, why))
            return None
        dst = outdir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        side = lg.sidecar_for(src, lg.META_EXT)
        if side:                               # records always travel (§7.2)
            shutil.copy(side, dst.with_name(side.name))
        return rel

    def rec_link(rel: str) -> str:
        # THE SAME LOOKUP serve() COPIES WITH, deliberately: serve writes the
        # record out under `side.name`, so a link built by any other rule can
        # name a file that is not in _site — a dead "provenance" link, which the
        # link gate fails the build over and which reads as a missing record.
        side = lg.sidecar_for(CUTS / rel, lg.META_EXT)
        if not side:
            return ""
        href = (Path(rel).parent / side.name).as_posix()
        return f' · <a href="{url(href)}">provenance</a>'

    # ---- HIS MORNING CHECKLIST ----------------------------------------------
    # Why this sits ABOVE the cuts rather than under them. On the evening of
    # 2026-08-07 the author refused v32 with an itemised list, work started on
    # every item that night, and by morning the page below held three cuts, ten
    # comparison pairs and no statement of what was actually being ASKED of him.
    # A screening surface that shows everything asks for nothing: he has to
    # reconstruct the question from the evidence, which is our job and not his.
    #
    # THE ITEM COUNT IS NOT FIXED, AND SHRINKING IT IS THE NORMAL OUTCOME. Two
    # of the questions drafted for this list were deleted before it was built,
    # because he had already answered both in the hours between the screening
    # and the build — the push-in rate ("simply make the zoom speed moderate")
    # and the 7/8/9 approach ("alright, shot progression"). Putting either in
    # front of him would have re-asked a closed question using the artifact he
    # closed it with. An item earns its place by being genuinely open THIS
    # MORNING; `state: settled` is for the ones we are only confirming we heard
    # right, and those are cheap to leave in because they cost him a glance.
    #
    # `pending:` IS THE HONEST HALF. An item whose evidence has not landed
    # renders its `pending:` text and nothing else — it does not quietly vanish,
    # because a checklist that hides its own gaps is how "seven new frames" turns
    # into a morning of finding out there are none. Filling the gap later is a
    # yaml edit: drop the file into `cuts/` with a sidecar and name it under
    # `sheets:` or `clips:`.
    # QUEUE FIRST, RECORD BEHIND — 2026-08-09, and the reason is one sentence of
    # his: "why is banyan.city/review so big and long? its hard to find what to
    # do". He is fourteen and screens in five-minute passes on a phone. The page
    # had seven open asks in it and they were spread through a week of settled
    # items, three cuts, nine comparison pairs and two pages of prose, so the
    # first thing he met was everything that was already decided.
    #
    # So `state: open` items now come first, one tight card each — the number he
    # quotes back at us, the ask, where the thing is, how to answer — and the
    # argument, the evidence and the confidences go one fold down. Settled items
    # keep every word they ever had and sit below, collapsed. NOTHING IS DELETED
    # AND NOTHING IS REWORDED: this is presentation. Both halves still print the
    # text in cuts.yaml, and an item's `state` is still the only thing that
    # decides which half it lands in.
    #
    # AN ITEM MAY MAKE ITS OWN CARD TIGHTER, and every one of these is optional
    # with a derived fallback, so an item written before today renders unchanged:
    #   summary:  one sentence under the ask, when the ask alone is not enough
    #   where:    where the thing to look at is — printed on the card
    #   how:      the answer grammar in one line ("say `b14-r3-s2`")
    #   minutes:  what it costs him; otherwise read off the chip
    # Where `where:` is absent it is LIFTED from the item's own opening
    # blockquote when that blockquote names a file, which is how three of
    # today's items already write it. Where `how:` is absent it comes from the
    # chip, which is already the verb — SCREEN, PICK, YES / NO.
    #
    # THE NUMBER IS `n:`, NOT THE LOOP INDEX. Splitting the list in two would
    # otherwise renumber every item the moment one settled, and the numbers are
    # how he answers ("item 12: yes"). `n:` is what cuts.yaml has always carried
    # and what the anchors (`#item-12`) are built from.
    CHIP_MINUTES = {"SCREEN": 3, "PICK": 3}          # crude on purpose: a screening
    CHIP_ACTION = {                                  # costs minutes, a yes/no costs one
        "SCREEN": "Watch it, then say it holds or say what is wrong with it.",
        "PICK": "Answer by naming your choice.",
        "YES / NO": "One word back — yes or no.",
        "ON US": "Nothing to answer here today — this one is on us.",
    }
    FILE_RE = re.compile(r"`?[A-Za-z0-9_][\w./-]*\.(?:mp4|png|mp3|md|yaml)`?")

    def lifted_where(body: str) -> str:
        """The item's own "it is here" line, copied up onto its card.

        Items 11, 12 and 13 all open by naming a path in a blockquote, which is
        exactly the where-to-look line a card needs, already written and already
        true. Reading it off the body rather than asking for a new yaml field
        keeps the two from drifting apart — a card that names a different file
        than the item under it would be worse than no card at all.

        Deliberately narrow: only a blockquote, only in the first three blocks,
        and only when its first line is a filename. The founder quote that opens
        item 06 and the motion line quoted in item 15 are both blockquotes too,
        and neither is a place to look.
        """
        for block in re.split(r"\n\s*\n", body.strip())[:3]:
            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            if not lines or not all(ln.startswith(">") for ln in lines):
                continue
            quoted = [ln.lstrip("> ").strip() for ln in lines]
            if quoted and FILE_RE.match(quoted[0]):
                return "<br>".join(inline_md(q) for q in quoted)
        return ""

    queue, record, minutes, n_open = [], [], 0, 0
    ck = cfg.get("checklist") or {}
    for i, it in enumerate(ck.get("items") or [], 1):
        num = int(it.get("n") or i)
        state = str(it.get("state", "")).strip().lower()
        is_open = state == "open"
        klass = "check" + (f" {state}bar" if state == "gap" else
                           " settled" if state == "settled" else "")
        chip = str(it.get("chip", "")).strip()
        chip_html = (f' <span class="chip{" hot" if state not in ("settled", "gap") else ""}">'
                     f'{html.escape(chip)}</span>') if chip else ""
        body_md = md_to_html(str(it.get("body", "")))

        # Clips and sheets are both optional and both degrade the same way: a
        # named file that is not there is reported, and an item with nothing
        # named simply has no media row.
        cells, n_clips = "", 0
        for c in it.get("clips") or []:
            got = serve(str(c["file"]))
            if not got:
                continue
            rel, pos = got
            n_clips += 1
            cells += (f'<figure><video controls playsinline preload="none" muted'
                      f'{poster_attr(pos, "/")} src="{url(rel)}"></video>'
                      f'<figcaption><span class="k">{html.escape(str(c.get("label", "")))}</span>'
                      f'{html.escape(str(c.get("note", "")))}{rec_link(rel)}</figcaption></figure>')
        clips_html = f'<div class="two">{cells}</div>' if cells else ""

        # A CONTACT SHEET IS FOUR TO TWENTY PICTURES IN ONE FILE, so the inline
        # copy is never the copy he judges from — it is 2060x4024 squeezed into a
        # phone column. The <a> is what makes the item answerable: tap the sheet
        # and the browser opens the image on its own, where a pinch-zoom can
        # actually read a leaf. Same file either way, so it costs no extra bytes;
        # `loading="lazy"` keeps the ten of them off the first paint.
        sheets, n_sheets = "", 0
        for s in it.get("sheets") or []:
            rel = serve_image(str(s["file"]))
            if not rel:
                continue
            n_sheets += 1
            # `beats:` is the story context for what is ON this sheet — optional,
            # and absent on every sheet that predates it. Two lines per beat: what
            # happens, and the one thing a candidate must show to be answerable at
            # all. It is deliberately NOT a ranking; nothing here names a frame.
            ctx = ""
            for b in s.get("beats") or []:
                ctx += (f'<li><b>{html.escape(str(b.get("beat", "")))}</b>'
                        f'<span><i>Happens</i> — {html.escape(str(b.get("happens", "")))}</span>'
                        f'<span><i>Must show</i> — {html.escape(str(b.get("shows", "")))}</span></li>')
            ctx = f'<ul class="beatctx">{ctx}</ul>' if ctx else ""
            sheets += (f'<figure><a href="{url(rel)}" target="_blank" '
                       f'rel="noopener"><img src="{url(rel)}" loading="lazy" '
                       f'alt="{html.escape(str(s.get("alt", s.get("label", "candidate frames"))))}">'
                       f'</a><figcaption><span class="k">{html.escape(str(s.get("label", "")))}</span>'
                       f'{html.escape(str(s.get("note", "")))}{rec_link(rel)}{ctx}</figcaption></figure>')
        # §7.2 ON THE SURFACE, not only in the sidecar. These frames publish under
        # an offer narrowed away from the site's CC BY 4.0 (D15, founder,
        # 2026-08-09), and a reader who saves one is owed that in the place he
        # saves it from — a licence stated only in a yaml file nobody opens is a
        # licence stated nowhere. One line under the gallery, not one per image.
        sheets_html = (f'<div class="sheets">{sheets}</div>'
                       '<p class="smallprint">Drawn by <code>animagine-xl-3.1</code>; '
                       'CreativeML Open RAIL++-M — outputs carry use restrictions, so '
                       'these images are <b>not</b> under this site’s CC BY 4.0. '
                       'Provenance beside each.</p>') if sheets else ""

        # Narration is judged by ear, so it gets a real player rather than a
        # link. Same gate, same travelling record: a voice take whose engine
        # licence does not clear is withheld exactly like a clip.
        auds = ""
        for a in it.get("audio") or []:
            rel = serve_image(str(a["file"]))       # copy-and-record, no poster
            if not rel:
                continue
            auds += (f'<figure><audio controls preload="none" '
                     f'src="{url(rel)}"></audio>'
                     f'<figcaption><span class="k">{html.escape(str(a.get("label", "")))}</span>'
                     f'{html.escape(str(a.get("note", "")))}{rec_link(rel)}</figcaption></figure>')
        audio_html = f'<div class="voices">{auds}</div>' if auds else ""

        # The gap note prints when the item said it was waiting on something AND
        # nothing arrived. If evidence did land, the note is dropped rather than
        # left standing next to the thing it claims is absent.
        gap = (f'<p class="gap">{inline_md(str(it["pending"]))}</p>'
               if it.get("pending") and not (cells or sheets or auds) else "")

        # `heading:` opens a labelled run of items. Episode 2's questions are
        # real but they do not block v33, so they sit under their own heading
        # below the ones that do — if he only has ten minutes, they should go on
        # the cut he already refused, not on the next episode.
        # A run heading follows its item into whichever half that item is in, so
        # a labelled group never ends up captioning nothing. Its intro folds:
        # the title orients in one line, and the paragraph explaining the group
        # is not what he came to the page for.
        into = queue if is_open else record
        if it.get("heading"):
            h = it["heading"]
            intro = md_to_html(str(h.get("intro", "")))
            into.append(f'<h3 class="run">{html.escape(str(h.get("title", "")))}</h3>'
                        + (f'<details class="drawer"><summary>Why these are grouped'
                           f'</summary><div class="drawer-body">{intro}</div></details>'
                           if intro else ""))

        if not is_open:
            record.append(
                f'<details class="drawer rec {klass}" id="item-{num:02d}">'
                f'<summary><span class="n">{num:02d}</span>'
                f'{html.escape(str(it.get("ask", "")))}{chip_html}</summary>'
                f'<div class="drawer-body">'
                f'{body_md}{clips_html}{sheets_html}{audio_html}{gap}</div></details>')
            continue

        n_open += 1
        minutes += int(it.get("minutes") or CHIP_MINUTES.get(chip.upper(), 1))
        summary = str(it.get("summary", "")).strip()
        where = str(it.get("where", "")).strip()
        where_html = inline_md(where) if where else lifted_where(str(it.get("body", "")))
        how = str(it.get("how", "")).strip() or CHIP_ACTION.get(chip.upper(), "")
        # ONE player may sit on a card, and only when it IS the item's evidence:
        # a single clip with no gallery beside it. Anything more folds — a card
        # he has to scroll to get past is the thing this page was rebuilt to
        # stop being, and the fold is one tap away.
        solo = clips_html if (n_clips == 1 and not sheets and not auds) else ""
        # PICTURES GET THEIR OWN FOLD, ABOVE THE ARGUMENT (2026-08-09). Nine
        # contact sheets cannot sit open on a card — 2060x4024 apiece, and a card
        # he has to scroll past is the thing this page was rebuilt to stop being.
        # But burying them inside "Why we are asking" is worse on the one item
        # whose entire job is choosing from pictures: the fold he needs is
        # labelled as the fold he can skip. So the gallery is its own drawer, it
        # is named and counted in its summary, and it comes first. `sheets_title:`
        # overrides the wording, because items 12 and 13 hold picked plates
        # rather than sheets and calling those "sheets" would be wrong.
        sheet_fold = ""
        if sheets_html:
            title = str(it.get("sheets_title", "")).strip() or (
                f"The {n_sheets} sheet{'' if n_sheets == 1 else 's'}")
            sheet_fold = (f'<details class="drawer look"><summary>'
                          f'{html.escape(title)}</summary>'
                          f'<div class="drawer-body">{sheets_html}</div></details>')
        folded = ("" if solo else clips_html) + audio_html
        # `gap` stays OUT of the fold on purpose. It is the sentence that says
        # the evidence never arrived, and a checklist that hides its own gaps is
        # how "seven new frames are ready" becomes a morning spent finding out
        # there are none. It is short by construction; the body is the long half.
        queue.append(
            f'<div class="{klass} q" id="item-{num:02d}">'
            f'<h3><span class="n">{num:02d}</span>'
            f'{html.escape(str(it.get("ask", "")))}{chip_html}</h3>'
            + (f'<p class="sum">{inline_md(summary)}</p>' if summary else "")
            + (f'<p class="where"><span class="k">where</span> {where_html}</p>'
               if where_html else "")
            + (f'<p class="act"><span class="k">answer</span> {inline_md(how)}</p>'
               if how else "")
            + solo + gap + sheet_fold
            + (f'<details class="drawer"><summary>Why we are asking — and the evidence'
               f'</summary><div class="drawer-body">{body_md}{folded}</div></details>'
               if (body_md or folded) else "")
            + '</div>')

    # The line he reads before anything else, and it is derived rather than
    # written down: the count IS the number of open items and the estimate IS
    # the sum of their chips, so neither can go stale while the list moves.
    count_html = (f'<p class="count"><b>{n_open} thing{"" if n_open == 1 else "s"} '
                  f'need{"s" if n_open == 1 else ""} you</b> — about {minutes} '
                  f'minute{"" if minutes == 1 else "s"}.'
                  f'<span class="sub">everything else on this page is already '
                  f'decided and folded away below</span></p>'
                  if queue else
                  '<p class="count"><b>Nothing needs you right now.</b>'
                  '<span class="sub">the record is below</span></p>')

    queue_html = ""
    if queue:
        lede = str(ck.get("lede", "")).strip()
        lede_html = f'<p class="said">{inline_md(lede)}</p>' if lede else QUEUE_LEDE
        queue_html = ('<section class="block" id="checklist"><h2>Your queue</h2>'
                      + lede_html + PROV_BANNER + "".join(queue) + '</section>')

    # The title and intro cuts.yaml writes for the checklist are the note that
    # came WITH the list, not the list. They keep every word and move behind a
    # fold at the head of the record, where the rest of the settled page is.
    ck_note = ""
    if ck.get("intro") or ck.get("outro"):
        ck_note = ('<details class="drawer" id="checklist-note"><summary>'
                   f'{html.escape(str(ck.get("title", "The note that came with this list")))}'
                   '</summary><div class="drawer-body">'
                   + md_to_html(str(ck.get("intro", "")))
                   + md_to_html(str(ck.get("outro", ""))) + '</div></details>')

    sections = []
    for cut in cfg.get("cuts") or []:
        got = serve(str(cut["file"]))
        if not got:
            continue
        rel, pos = got
        src = CUTS / rel
        dur = dur_label(mp4_seconds(src))
        mb = src.stat().st_size / (1 << 20)
        changed = "".join(f"<li>{inline_md(x)}</li>" for x in cut.get("changed") or [])
        wrong = "".join(f"<li>{inline_md(x)}</li>" for x in cut.get("known_wrong") or [])
        # `status:` — the author's verdict on THIS cut, printed above the player
        # and before anything else the card says. It exists because on 2026-08-07
        # he refused v32 and the page went on calling it "the one to answer on"
        # for the rest of the evening: a card whose every other line is a fact
        # about the film cannot also carry a verdict, and burying one in "known
        # and still wrong" would file a decision under a defect list. A refused
        # cut is never REMOVED — it is the record of what he refused, and the
        # notes being worked from only make sense next to it.
        status = (f'<p class="notice">{inline_md(str(cut["status"]))}</p>'
                  if cut.get("status") else "")
        # Each cut folds under its own version and title. All three are the
        # record of a screening that already happened — v32 was refused on
        # 2026-08-07 and the two under it are how it got there — so none of them
        # is work waiting on him, and none of them should cost him a scroll.
        ver = html.escape(str(cut.get("version", "")))
        sections.append(
            f'<details class="drawer" id="cut-{ver or len(sections) + 1}"><summary>'
            f'{ver}{" — " if ver else ""}{html.escape(str(cut["title"]))}</summary>'
            f'<div class="drawer-body">'
            f'<div class="cut"><h2>{html.escape(str(cut["title"]))} '
            f'<span class="chip hot">{ver}</span></h2>'
            f'{status}{CUT_STAMP}'
            f'<div class="split"><div class="film">'
            f'<video controls playsinline preload="metadata"{poster_attr(pos, "/")} '
            f'src="{url(rel)}"></video>'
            f'<p class="facts">assembled {html.escape(str(cut.get("date", "")))} · '
            f'{html.escape(str(cut.get("beats", "")))}'
            f'{" · " + dur if dur else ""} · {mb:.1f} MB{rec_link(rel)}</p>'
            f'</div><div>'
            f'<h3>What changed from {inline_md(cut.get("changed_from", "the previous cut"))}</h3>'
            f"<ul>{changed}</ul>"
            + (f"<h3>Known and still wrong</h3><ul>{wrong}</ul>" if wrong else "")
            + '</div></div></div></div></details>')

    # Side-by-side groups. No `loop` on these players, and that is not a style
    # choice: a held beat is a one-way push-in, so looping a 2.5s clip snaps the
    # frame back to wide every 2.5 seconds and reads as the ping-pong the founder
    # ruled out on 2026-08-07. SCREENING.html had exactly this bug.
    groups = []
    for grp in cfg.get("comparisons") or []:
        left_label = str(grp.get("left_label", "before"))
        right_label = str(grp.get("right_label", "after"))
        items = []
        for p in grp.get("items") or []:
            left, right = serve(str(p["left"])), serve(str(p["right"]))
            if not (left and right):
                continue
            # An item may override the group's labels. Beat 3 needs it: the group
            # says "held — in v30", and beat 3's held side is the approved frame,
            # which is in no cut at all. A label inherited into being false is
            # worse than no label on a page whose whole job is to say what a
            # thing IS.
            cells = ""
            for label, (rel, pos), note in (
                    (str(p.get("left_label", left_label)), left, p.get("left_note", "")),
                    (str(p.get("right_label", right_label)), right, p.get("right_note", ""))):
                cells += (f'<figure><video controls playsinline preload="none" muted'
                          f'{poster_attr(pos, "/")} src="{url(rel)}"></video>'
                          f'<figcaption><span class="k">{html.escape(label)}</span>'
                          f'{html.escape(str(note))}{rec_link(rel)}</figcaption></figure>')
            why = (f'<p class="why"><strong>{html.escape(str(p.get("why_label", "Why:")))}'
                   f'</strong> {html.escape(str(p["why"]))}</p>') if p.get("why") else ""
            # A third clip that is context, not a choice — beat 3's revoked-magenta
            # hold, which is what v30 ships and is nobody's option. Shown small and
            # after the verdict so it cannot be mistaken for one of the two.
            fn = p.get("footnote") or {}
            foot = ""
            got = serve(str(fn["file"])) if fn.get("file") else None
            if got:
                rel, pos = got
                foot = ('<details class="drawer"><summary>'
                        f'{html.escape(str(fn.get("label", "for reference")))}</summary>'
                        '<div class="drawer-body"><div class="two">'
                        f'<figure><video controls playsinline preload="none" muted'
                        f'{poster_attr(pos, "/")} src="{url(rel)}"></video>'
                        f'<figcaption><span class="k">not an option</span>'
                        f'{html.escape(str(fn.get("note", "")))}{rec_link(rel)}'
                        '</figcaption></figure></div></div></details>')
            items.append(
                f'<div class="pair"><h3>Beat {html.escape(str(p["beat"]))} — '
                f'{html.escape(str(p.get("title", "")))}</h3>{why}'
                f'<div class="two">{cells}</div>'
                + (f'<p class="why">{html.escape(str(p["verdict"]))}</p>'
                   if p.get("verdict") else "") + foot + '</div>')
        if items:
            # The group's own title is the fold's label — it already says what
            # the comparison is, and inventing a second name for it would be one
            # more thing on the page that has to be kept true.
            groups.append(f'<details class="drawer" id="cmp-{len(groups) + 1}"><summary>'
                          f'{html.escape(str(grp.get("title", "")))}'
                          f' ({len(items)})</summary><div class="drawer-body">'
                          f'<div class="cut">{md_to_html(str(grp.get("intro", "")))}'
                          f'{"".join(items)}</div></div></details>')

    notices = ""
    if withheld:
        rows = "".join(f"<li><code>{html.escape(n)}</code> — {html.escape(w)}</li>"
                       for n, w in withheld)
        notices += ('<p class="notice">⚠️ <strong>Withheld by the licence gate.</strong> '
                    'These files exist in the repo and are not copied here, because the '
                    'tree publishes under CC BY 4.0 and their licence does not grant what '
                    f'that offers:<ul>{rows}</ul></p>')
    if missing:
        rows = "".join(f"<li><code>{html.escape(n)}</code></li>" for n in missing)
        notices += ('<p class="notice"><strong>Listed but not here yet.</strong> These are '
                    'named in <code>cuts/cuts.yaml</code> and the file has not landed in the '
                    f'repo, so there is nothing to play:<ul>{rows}</ul></p>')

    # THE RECORD. Everything already decided, in the order it was decided in,
    # every fold shut. The page's own `why:` leads it because a stranger who
    # guesses this URL still has to be told what he is looking at — the fold's
    # label says the load-bearing half of that out loud, so it is readable
    # without opening anything.
    record_html = (
        '<section class="block" id="record"><h2>The record</h2>'
        '<p class="said">Everything already settled — decisions, the cuts they '
        'were made on, and the receipts. Nothing here needs you. Nothing has been '
        'deleted either: open a fold and it is all still there, word for word.</p>'
        + (f'<details class="drawer" id="about"><summary>What this page is — and '
           f'what it is not</summary><div class="drawer-body">'
           f'{md_to_html(str(meta.get("why", "")))}</div></details>'
           if meta.get("why") else "")
        + ck_note
        + "".join(record)
        + "".join(sections)
        + "".join(groups)
        + '<details class="drawer" id="receipts"><summary>Receipts</summary>'
        + '<div class="drawer-body">'
        + md_to_html(str(cfg.get("provenance", "")))
        + '</div></details></section>')

    body = (f'<p class="eyebrow">{html.escape(str(meta.get("eyebrow", "WORKING CUTS")))}</p>'
            f'<h1>{html.escape(str(meta.get("title", "Working cuts")))}</h1>'
            f'{count_html}'
            f'{queue_html}'
            f'{notices}'
            f'{record_html}'
            f'<p><a class="btn ghost" href="../index.html">← the tree</a> '
            f'<a class="btn ghost" href="../watch.html">the published episode</a></p>')
    return page(str(meta.get("title", "Working cuts")), body, depth=1,
                path="review/index.html", robots="noindex, nofollow",
                desc="Unlisted screening page for working cuts of Banyan City episodes — "
                     "drafts the author has not passed, not the published show.")


def render_feed(genomes: list) -> str:
    """RSS 2.0 of nodes, newest release first (dates from lineage `released`)."""
    items = []
    for g in genomes:
        gid = g["tree"]["id"]
        for n in g["nodes"].values():
            date = str(n.get("released", ""))
            url = f"{CANONICAL}/{gid}/{n['slug']}.html"
            desc = html.escape(n["teaser"] or n["title"])
            items.append((date, f"""  <item>
    <title>{html.escape(n['id'])} — {html.escape(n['title'])}</title>
    <link>{url}</link>
    <guid isPermaLink="true">{url}</guid>
    <pubDate>{date}T12:00:00Z</pubDate>
    <description>{desc}</description>
  </item>"""))
    items.sort(key=lambda t: t[0], reverse=True)
    body = "\n".join(i for _, i in items)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Banyan City — new nodes</title>
  <link>{CANONICAL}/</link>
  <description>New story nodes on the tree: trunk and branches alike.</description>
{body}
</channel>
</rss>
"""


LINK_RE = re.compile(r'(?:href|src|poster)="([^"]+)"')


def _trailing_slash() -> bool:
    """`trailingSlash` as `vercel.json` actually has it, defaulting to Vercel's
    own default (false) when the file or the key is absent — which is also what
    the GitHub Pages mirror does, so the stricter reading is the safe one."""
    try:
        cfg = json.loads((REPO / "vercel.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return bool(cfg.get("trailingSlash", False))


def served_base(rel: str) -> str:
    """The URL directory a BROWSER resolves this page's relative links against.

    THE HOLE THIS CLOSES, found 2026-08-09 when the founder opened /review and
    said "images are broken". This gate resolved every href against the page's
    directory ON DISK — `_site/review/index.html` + `review-assets/x.jpg` →
    `_site/review/review-assets/x.jpg`, which exists, so the build went green
    while every image on the deployed page 404'd.

    The filesystem is not what the browser uses. `vercel.json` sets
    `cleanUrls: true` and `trailingSlash: false`, so `_site/review/index.html`
    is served at **`/review`** — and `https://banyan.city/review/` 308-redirects
    TO the slashless form, so a reader cannot opt out. A page at `/review` has
    base `/`, not `/review/`, and `review-assets/x.jpg` therefore means
    `/review-assets/x.jpg`. Nothing on disk is wrong; the URL is.

    So: `<dir>/index.html` is served one level UP from where it sits, and every
    other page is served where it sits. Get that right and the checker sees what
    a visitor sees. `/trials` had been broken the same way for as long as it has
    existed, and this function is why it is not any more.

    THE RULE IS READ FROM `vercel.json`, NOT ASSUMED. Everything above is true of
    `trailingSlash: false`; flip that setting and `<dir>/index.html` is served at
    `/<dir>/` instead, which moves the base back down a level. Hard-coding the
    current answer would leave this function quietly describing a host it no
    longer runs on — the same class of staleness as the licence table that said
    "outputs unrestricted" (D15). The config is the fact; this reads it.
    """
    p = Path(rel)
    if p.name == "index.html" and p.parent != Path(".") and not _trailing_slash():
        return p.parent.parent.as_posix().strip(".")
    if p.name == "index.html" and p.parent != Path("."):
        return p.parent.as_posix().strip(".")
    return p.parent.as_posix().strip(".")


def resolve_url(base: str, target: str) -> str:
    """`target` from a page served under `base`, the way a browser does it.

    Root-clamped on purpose: a browser cannot walk above `/`, so `../index.html`
    from `/review` is `/index.html` and not an escape from the site. Doing this
    in URL space rather than with Path arithmetic is what lets the checker accept
    the nav links (which are correct) while rejecting the media links (which were
    not) — path arithmetic calls both of them escapes.
    """
    parts = target.split("/") if target.startswith("/") else \
        (base.split("/") if base else []) + target.split("/")
    out: list = []
    for seg in parts:
        if seg in ("", "."):
            continue
        if seg == "..":
            if out:
                out.pop()
            continue
        out.append(seg)
    return "/".join(out)


def check_links(pages: list) -> list:
    """Every local reference in EVERY published page must resolve inside _site.

    The first version of this gate only checked the pages this module writes
    in-process, and it green-lit a build where 138 lab images and 15 shot-board
    receipts 404'd — a green self-check on a broken site is worse than none.
    Now it sweeps the whole output tree: href, src, and poster alike, each one
    resolved against the URL the page is SERVED at rather than the directory it
    is stored in. See served_base for what that distinction cost.
    """
    for rel in pages:
        if not (OUT / rel).exists():
            return [f"{rel} (page missing)"]
    broken = []
    for f in sorted(OUT.rglob("*.html")):
        rel = f.relative_to(OUT).as_posix()
        base = served_base(rel)
        for href in LINK_RE.findall(f.read_text(errors="replace")):
            if href.startswith(("http://", "https://", "#", "mailto:", "data:", "//")):
                continue
            target = href.split("#")[0].split("?")[0]
            if not target:
                continue
            if not (OUT / resolve_url(base, target)).exists():
                broken.append(f"{rel} (served at /{base}) → {href}")
    return broken


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    genomes = [load_genome(p) for p in sorted((REPO / "genomes").iterdir()) if p.is_dir()]

    # media first: posters are written next to the clips they belong to, and
    # every page that shows a player wants one.
    for g in genomes:
        gdir = OUT / g["tree"]["id"]
        gdir.mkdir(exist_ok=True)
        for n in g["nodes"].values():
            for l in n["leaf_meta"]:
                content = str(l.get("content", ""))
                if content.endswith((".html", ".mp4")):
                    src = n["dir"] / "leaves" / content
                    if src.exists():
                        (gdir / "leaves").mkdir(exist_ok=True)
                        shutil.copy(src, gdir / "leaves" / content)

    mine = ["index.html", "watch.html", "watch/season.html", "create.html", "city.html",
            "machine.html", "trials/index.html"]
    (OUT / "index.html").write_text(render_index(genomes))
    (OUT / "watch.html").write_text(render_watch(genomes))
    # the walk: one step page per non-root episode (the root step IS watch.html)
    (OUT / "watch").mkdir(exist_ok=True)
    for g in genomes:
        for n in g["nodes"].values():
            if n.get("parent"):
                rel = f"watch/{n['slug']}.html"
                (OUT / rel).write_text(render_walk(g, n, rel))
                mine.append(rel)
    (OUT / "watch" / "season.html").write_text(render_season(genomes))
    (OUT / "create.html").write_text(render_create())
    (OUT / "city.html").write_text(render_city())
    from build_status import build as _build_status
    _build_status(OUT)
    from build_sim import build as _build_sim
    _build_sim(OUT)
    from build_pulse import build as _build_pulse
    _build_pulse(OUT)
    from build_queue import build as _build_queue
    _build_queue(OUT)
    import shutil as _sh
    if (REPO / 'lab').is_dir():
        _sh.copytree(REPO / 'lab', OUT / 'lab', dirs_exist_ok=True)
        print('✓ lab/ published')
    (OUT / "machine.html").write_text(render_machine())
    (OUT / "feed.xml").write_text(render_feed(genomes))
    (OUT / ".nojekyll").write_text("")
    og = REPO / "assets" / "og.png"          # social-share image referenced by page() meta
    if og.exists():
        shutil.copy(og, OUT / "og.png")
    # The review area (D17). Deliberately NOT in `mine`'s nav and not linked
    # from any page — unlisted, reachable by URL. It is still swept by
    # check_links, which walks every html file in the output.
    # 2026-08-14, founder: "then how about you just move everything from
    # /review/inbox to /review?" — /review is now the BOARD (written by
    # review/inbox/regen.py), so the working-cuts page moves aside to
    # /review/cuts rather than overwriting it. cuts.yaml stays where it is:
    # poll_decisions.py reads it for the card numbers his answers match
    # against, so retiring the data to retire the page would break that.
    if (CUTS / "cuts.yaml").exists():
        (OUT / "review" / "cuts.html").write_text(render_review())
        mine.append("review/cuts.html")
        print("✓ review/cuts published — unlisted working cuts")
        # Not fatal, and named rather than silent. Each line is a clip whose own
        # record cannot say which pixels it holds, so it ships with no poster
        # instead of one that promises a frame it does not contain. On a host
        # with ffmpeg the player still gets a real extracted frame; on Vercel,
        # which has none, these are the players that come up blank — which is
        # the point, and is why the line names the record and not the poster.
        for w in POSTER_WARNINGS:
            print(f"  ! poster withheld — {w}")
    # Hand-authored pages in the same unlisted area — `review/<name>/index.html`
    # in the repo becomes `/review/<name>`. Same treatment as the cuts page: not
    # in `mine`'s nav, linked from nothing, noindex (stamped by unlisted_html
    # since these do not pass through page()), and swept by check_links because
    # the index goes into `mine`.
    #
    # in_the_tree() before copying, exactly as the shot board does with takes/:
    # an untracked page is on one laptop and not on the deploy, and publishing
    # it locally would let a lane screen a URL that CI cannot build. The line
    # below is what tells them which of the two situations they are in.
    # THE BOARD ITSELF, at /review. 2026-08-14: the founder asked for the inbox
    # to live at the short URL, so review/inbox/regen.py now writes the same
    # page to review/index.html. review_page_dirs() only sees DIRECTORIES that
    # carry an index.html, so the top-level file needs its own line or the board
    # is written and never published — the exact invisible-page hole that
    # function's docstring exists to close, one level up.
    board = REPO / "review" / "index.html"
    if board.exists() and in_the_tree([board]):
        (OUT / "review").mkdir(parents=True, exist_ok=True)
        shutil.copy(board, OUT / "review" / "index.html")
        mine.append("review/index.html")
        print("✓ review/ published — the board")
    elif board.exists():
        print("  ! review/index.html is NOT in the tree — not published "
              "(commit it; the deploy does not have this file)")

    for d in review_page_dirs():
        rel_dir = f"review/{d.name}"
        files = in_the_tree(sorted(p for p in d.rglob("*") if p.is_file()))
        if (d / "index.html") not in files:
            print(f"  ! {rel_dir}/index.html is NOT in the tree — not published "
                  f"(commit it; the deploy does not have this file)")
            continue
        copied, withheld = 0, []
        for p in files:
            # The licence gate applies here for the same reason it applies to
            # takes/: two directories side by side, one gated and one not, is
            # not a policy. HTML the repo carries is prose, not a render.
            if p.suffix.lower() not in (".html", ".htm"):
                ok, why = publishable(p)
                if not ok:
                    withheld.append((p.name, why))
                    continue
            dest = OUT / rel_dir / p.relative_to(d)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if p.suffix.lower() in (".html", ".htm"):
                dest.write_text(unlisted_html(p.read_text(errors="replace")))
            else:
                shutil.copy(p, dest)
            copied += 1
        if withheld:
            (OUT / rel_dir / "WITHHELD.md").write_text(withheld_note(withheld))
        mine.append(f"{rel_dir}/index.html")
        print(f"✓ {rel_dir}/ published — unlisted hand-authored page, {copied} file(s)")
    (OUT / "trials").mkdir(exist_ok=True)
    trials_out = REPO / "pipeline" / "t3-trials" / "outputs"
    if trials_out.exists():
        for mp4 in trials_out.glob("*/*.mp4"):
            (OUT / "trials" / mp4.parent.name).mkdir(exist_ok=True)
            shutil.copy(mp4, OUT / "trials" / mp4.parent.name / mp4.name)
    (OUT / "trials" / "index.html").write_text(render_trials())
    for g in genomes:
        gdir = OUT / g["tree"]["id"]
        for n in g["nodes"].values():
            (gdir / f"{n['slug']}.html").write_text(render_node_page(g, n))
            mine.append(f"{g['tree']['id']}/{n['slug']}.html")
            # D11: the shot board — every beat's full recipe + takes, forkable
            # by anyone. The repo is the process; the site renders the process.
            node_dir = n["dir"]
            if n["has_board"]:
                from build_shotboard import board_html
                media = f"{n['slug']}-media"
                (gdir / f"{n['slug']}-shots.html").write_text(
                    board_html(g["tree"]["id"], node_dir, rel=media))
                if (node_dir / "stills").is_dir():
                    (gdir / media).mkdir(exist_ok=True)
                    for f in (node_dir / "stills").glob("*.png"):
                        shutil.copy(f, gdir / media / f.name)
                # Candidate stills go through publishable() exactly like the
                # candidate clips below (2026-08-07). This was a bare glob+copy
                # until today, which made takes/stills/ the one published
                # surface on the site with no licence question asked — the same
                # hole publishable() was written to close for takes/clips/ after
                # `13-i-always-left.PIXVERSE.mp4` became a downloadable file on
                # banyan.city with D8 already forbidding it. Two directories
                # side by side, one gated and one not, is not a policy.
                # It is also the condition licence_gate.is_candidate depends on:
                # takes/ records are kept out of the debt ratchet BECAUSE this
                # gate stops an unpublishable candidate reaching the web. Remove
                # the gate and the exemption becomes a hole the same day.
                # in_the_tree() before publishable(), and the order matters: a
                # candidate frame the tree does not carry is not a licence
                # question at all. The board no longer links it, so copying it
                # would put an orphan file on the site, and naming it in
                # WITHHELD.md would tell a visitor a file is in the repo when it
                # is not. See in_the_tree() for the 164 links this closes.
                if (node_dir / "takes" / "stills").is_dir():
                    (gdir / f"{media}-takes").mkdir(exist_ok=True)
                    withheld = []
                    for f in in_the_tree(sorted((node_dir / "takes" / "stills").glob("*.png"))):
                        ok, why = publishable(f)
                        if not ok:
                            withheld.append((f.name, why))
                            continue
                        shutil.copy(f, gdir / f"{media}-takes" / f.name)
                    if withheld:
                        (gdir / f"{media}-takes" / "WITHHELD.md").write_text(
                            withheld_note(withheld))
                if (node_dir / "takes" / "clips").is_dir():
                    (gdir / f"{media}-clips").mkdir(exist_ok=True)
                    withheld = []
                    for f in in_the_tree(sorted((node_dir / "takes" / "clips").iterdir())):
                        ok, why = publishable(f)
                        if not ok:
                            withheld.append((f.name, why))
                            continue
                        shutil.copy(f, gdir / f"{media}-clips" / f.name)
                    if withheld:
                        (gdir / f"{media}-clips" / "WITHHELD.md").write_text(
                            withheld_note(withheld))

    # THE COUNT THE PROMOTION HOLE COSTS, said out loud on every build. Each of
    # these is a published file whose picture came out of a frame nothing in the
    # tree can account for; the gate cannot refuse them on a licence it has no
    # record of, so the honest reading is "we do not know what drew this", and a
    # number nobody prints is a number nobody retires.
    if FRAME_WARNINGS:
        frames = sorted({w.split("drawn from ")[-1].split(",")[0] for w in FRAME_WARNINGS})
        print(f"  ! {len(FRAME_WARNINGS)} published file(s) hold pixels from "
              f"{len(frames)} unprovenanced frame(s) — a promotion copied the "
              f"picture and left its record behind (stills/README.md)")
        for w in FRAME_WARNINGS[:10]:
            print(f"    · {w}")
    total = sum(len(g["nodes"]) for g in genomes)
    posters = sum(1 for v in _POSTERS.values() if v)
    print(f"✓ built _site/ — {len(genomes)} genome(s), {total} node pages, {posters} posters"
          + ("" if FFMPEG else " (no ffmpeg: posters come from approved stills only)"))
    # Say the number out loud. The whole failure this closes was a difference
    # between two boxes that neither box mentioned; a build that quietly drops
    # 185 files it can see is one `git add` away from being the same story.
    if _LOCAL_ONLY:
        print(f"  · {_LOCAL_ONLY} take file(s) on this disk are not in the tree — "
              f"not linked, not copied (the deploy does not have them)")

    broken = check_links(mine)
    if broken:
        print("✗ broken local links:")
        for b in broken:
            print(f"    {b}")
        raise SystemExit(1)
    swept = sum(1 for _ in OUT.rglob("*.html"))
    print(f"✓ link check: {swept} pages swept, no broken local references")

    # Say this number out loud too, for the same reason as the line above: the
    # failure it closes is one nobody's build ever mentioned. A render that
    # finished and reached no page he can open is, from where he sits, a render
    # that never happened -- he said so four times in three days. Deliberately a
    # WARNING and never an exit: a wave that landed ninety seconds ago is a job
    # in flight, and failing the build over it would stop the deploy to punish
    # work that is going fine. Runs last, on a complete `_site/`, because the
    # generated pages are half of what counts as "shown". Silent on a checkout
    # with no farm branch (CI, the deploy box) rather than falsely green.
    try:
        import unpaged
        line = unpaged.warn_line(unpaged.survey(str(REPO)))
    except Exception as e:                      # never break a build over a warning
        line = ""
        print(f"  · unpaged check skipped ({type(e).__name__}: {e})")
    if line:
        print(f"  ! {line}")


if __name__ == "__main__":
    main()
