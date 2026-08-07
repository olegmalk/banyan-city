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

import html
import os
import re
import shutil
import struct
import subprocess
from pathlib import Path

import markdown
import yaml

import licence_gate as lg
from site_theme import THEME_CSS

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_site"
# Forkable: in CI GITHUB_REPOSITORY names the fork; locally fall back to origin
GH_REPO = os.environ.get("GITHUB_REPOSITORY", "olegmlkvorg/banyan-city")
REPO_URL = f"https://github.com/{GH_REPO}"
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
.check .sheets img { display: block; width: 100%; min-width: 520px; height: auto;
  border-radius: 12px; border: 1px solid var(--line); background: var(--code-bg); }
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
<meta name="viewport" content="width=device-width, initial-scale=1">{robots_meta}
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


def publishable(f: Path) -> tuple:
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
    for key, value in data.items():
        if key.lower() not in lg.PROVENANCE_KEYS:
            continue
        licence = lg.engine_licence(value)
        if licence is None:
            continue
        verdict, _why = lg.classify(licence)
        if verdict != "allow":
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


def withheld_note(rows: list) -> str:
    """Why a take the board lists is not downloadable here.

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
    return f"""<li><div class="card">
{lineage}
{chips(n)}
<div class="title"><a href="{genome_id}/{html.escape(n['slug'])}.html">{html.escape(n['title'])}</a></div>
{teaser}
<div class="meta"><a href="{genome_id}/{html.escape(n['slug'])}.html">read / watch</a> · {n_vers} {'version' if n_vers == 1 else 'versions'}{board}{react}</div>
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
        f"<td>${l['cost_usd']:.2f}</td>"
        f"<td>{html.escape(str(l['status']))}</td><td>{screen_cell(l)}</td></tr>"
        for l in n["leaf_meta"]
    )
    receipts_html = f"""<details class="drawer"><summary>Every render &amp; its receipt
({len(n['leaf_meta'])})</summary><div class="drawer-body">
<p class="smallprint">A <em>leaf</em> is one render of this episode — script, storyboard, animatic
or film. Every one publishes its prompt, model, seed and cost: this table is the audit trail.</p>
<table><tr><th>version</th><th>stage</th><th>form</th><th>length</th><th>cost</th><th>status</th><th>screening</th></tr>{leaves_rows}</table>
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
grab an <a href="https://github.com/olegmlkvorg/banyan-city/issues?q=is%3Aissue+is%3Aopen+label%3Arender-request">open
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
                        f'{poster_attr(pos, "../")} '
                        f'src="{html.escape(plat)}/{html.escape(mp4.name)}"></video>'
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

    def still_for(src: Path):
        """The beat's own approved still, so a poster is never another beat."""
        # hold_still records the frame as `source_still` in a `<name>.mp4.meta.yaml`;
        # the stem-only lookup missed it and every held clip fell back to the node's
        # first still, i.e. another beat's picture as the poster
        side = lg.sidecar_for(src, lg.META_EXT)
        if not side:
            return first_still(REVIEW_NODE)
        data = yaml.safe_load(side.read_text(encoding="utf-8")) or {}
        name = data.get("init_still") or data.get("source_still")
        cand = REVIEW_NODE / "stills" / str(name) if name else None
        return cand if cand and cand.exists() else first_still(REVIEW_NODE)

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
        return f' · <a href="{html.escape(href)}">provenance</a>'

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
    checks = []
    ck = cfg.get("checklist") or {}
    for i, it in enumerate(ck.get("items") or [], 1):
        state = str(it.get("state", "")).strip().lower()
        klass = "check" + (f" {state}bar" if state == "gap" else
                           " settled" if state == "settled" else "")
        chip = str(it.get("chip", "")).strip()
        chip_html = (f' <span class="chip{" hot" if state not in ("settled", "gap") else ""}">'
                     f'{html.escape(chip)}</span>') if chip else ""
        body_md = md_to_html(str(it.get("body", "")))

        # Clips and sheets are both optional and both degrade the same way: a
        # named file that is not there is reported, and an item with nothing
        # named simply has no media row.
        cells = ""
        for c in it.get("clips") or []:
            got = serve(str(c["file"]))
            if not got:
                continue
            rel, pos = got
            cells += (f'<figure><video controls playsinline preload="none" muted'
                      f'{poster_attr(pos, "../")} src="{html.escape(rel)}"></video>'
                      f'<figcaption><span class="k">{html.escape(str(c.get("label", "")))}</span>'
                      f'{html.escape(str(c.get("note", "")))}{rec_link(rel)}</figcaption></figure>')
        clips_html = f'<div class="two">{cells}</div>' if cells else ""

        sheets = ""
        for s in it.get("sheets") or []:
            rel = serve_image(str(s["file"]))
            if not rel:
                continue
            sheets += (f'<figure><img src="{html.escape(rel)}" loading="lazy" '
                       f'alt="{html.escape(str(s.get("alt", s.get("label", "candidate frames"))))}">'
                       f'<figcaption><span class="k">{html.escape(str(s.get("label", "")))}</span>'
                       f'{html.escape(str(s.get("note", "")))}{rec_link(rel)}</figcaption></figure>')
        sheets_html = f'<div class="sheets">{sheets}</div>' if sheets else ""

        # Narration is judged by ear, so it gets a real player rather than a
        # link. Same gate, same travelling record: a voice take whose engine
        # licence does not clear is withheld exactly like a clip.
        auds = ""
        for a in it.get("audio") or []:
            rel = serve_image(str(a["file"]))       # copy-and-record, no poster
            if not rel:
                continue
            auds += (f'<figure><audio controls preload="none" '
                     f'src="{html.escape(rel)}"></audio>'
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
        if it.get("heading"):
            h = it["heading"]
            checks.append(f'<h3 class="run">{html.escape(str(h.get("title", "")))}</h3>'
                          + md_to_html(str(h.get("intro", ""))))

        checks.append(
            f'<div class="{klass}"><h3><span class="n">{i:02d}</span>'
            f'{html.escape(str(it.get("ask", "")))}{chip_html}</h3>'
            f'{body_md}{clips_html}{sheets_html}{audio_html}{gap}</div>')

    checklist_html = ""
    if checks:
        checklist_html = (
            '<div class="cut" id="checklist">'
            f'<h2>{html.escape(str(ck.get("title", "Your pass")))}</h2>'
            f'{md_to_html(str(ck.get("intro", "")))}{"".join(checks)}'
            + (f'{md_to_html(str(ck.get("outro", "")))}' if ck.get("outro") else "")
            + '</div>')

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
        sections.append(
            f'<div class="cut"><h2>{html.escape(str(cut["title"]))} '
            f'<span class="chip hot">{html.escape(str(cut.get("version", "")))}</span></h2>'
            f'{status}{CUT_STAMP}'
            f'<div class="split"><div class="film">'
            f'<video controls playsinline preload="metadata"{poster_attr(pos, "../")} '
            f'src="{html.escape(rel)}"></video>'
            f'<p class="facts">assembled {html.escape(str(cut.get("date", "")))} · '
            f'{html.escape(str(cut.get("beats", "")))}'
            f'{" · " + dur if dur else ""} · {mb:.1f} MB{rec_link(rel)}</p>'
            f'</div><div>'
            f'<h3>What changed from {inline_md(cut.get("changed_from", "the previous cut"))}</h3>'
            f"<ul>{changed}</ul>"
            + (f"<h3>Known and still wrong</h3><ul>{wrong}</ul>" if wrong else "")
            + '</div></div></div>')

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
                          f'{poster_attr(pos, "../")} src="{html.escape(rel)}"></video>'
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
                        f'{poster_attr(pos, "../")} src="{html.escape(rel)}"></video>'
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
            groups.append(f'<div class="cut"><h2>{html.escape(str(grp.get("title", "")))}</h2>'
                          f'{md_to_html(str(grp.get("intro", "")))}{"".join(items)}</div>')

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

    body = (f'<p class="eyebrow">{html.escape(str(meta.get("eyebrow", "WORKING CUTS")))}</p>'
            f'<h1>{html.escape(str(meta.get("title", "Working cuts")))}</h1>'
            f'{md_to_html(str(meta.get("why", "")))}'
            f'{notices}'
            f'{checklist_html}'
            f"{''.join(sections)}"
            f"{''.join(groups)}"
            + '<div class="cut"><h2>Receipts</h2>'
            + md_to_html(str(cfg.get("provenance", "")))
            + '</div>'
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


def check_links(pages: list) -> list:
    """Every local reference in EVERY published page must resolve inside _site.

    The first version of this gate only checked the pages this module writes
    in-process, and it green-lit a build where 138 lab images and 15 shot-board
    receipts 404'd — a green self-check on a broken site is worse than none.
    Now it sweeps the whole output tree: href, src, and poster alike.
    """
    for rel in pages:
        if not (OUT / rel).exists():
            return [f"{rel} (page missing)"]
    broken = []
    for f in sorted(OUT.rglob("*.html")):
        rel = f.relative_to(OUT).as_posix()
        for href in LINK_RE.findall(f.read_text(errors="replace")):
            if href.startswith(("http://", "https://", "#", "mailto:", "data:", "//")):
                continue
            target = href.split("#")[0].split("?")[0]
            if not target:
                continue
            if not (f.parent / target).exists():
                broken.append(f"{rel} → {href}")
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
    if (CUTS / "cuts.yaml").exists():
        (OUT / "review" / "index.html").write_text(render_review())
        mine.append("review/index.html")
        print("✓ review/ published — unlisted working cuts")
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
                if (node_dir / "takes" / "stills").is_dir():
                    (gdir / f"{media}-takes").mkdir(exist_ok=True)
                    withheld = []
                    for f in sorted((node_dir / "takes" / "stills").glob("*.png")):
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
                    for f in (node_dir / "takes" / "clips").iterdir():
                        ok, why = publishable(f)
                        if not ok:
                            withheld.append((f.name, why))
                            continue
                        shutil.copy(f, gdir / f"{media}-clips" / f.name)
                    if withheld:
                        (gdir / f"{media}-clips" / "WITHHELD.md").write_text(
                            withheld_note(withheld))

    total = sum(len(g["nodes"]) for g in genomes)
    posters = sum(1 for v in _POSTERS.values() if v)
    print(f"✓ built _site/ — {len(genomes)} genome(s), {total} node pages, {posters} posters"
          + ("" if FFMPEG else " (no ffmpeg: posters come from approved stills only)"))

    broken = check_links(mine)
    if broken:
        print("✗ broken local links:")
        for b in broken:
            print(f"    {b}")
        raise SystemExit(1)
    swept = sum(1 for _ in OUT.rglob("*.html"))
    print(f"✓ link check: {swept} pages swept, no broken local references")


if __name__ == "__main__":
    main()
