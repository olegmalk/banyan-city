#!/usr/bin/env python3
"""THE QUEUE — a gallery of every render, what it was told, and what it made.

The founder asked for this page twice. First, 2026-08-14: "i cant keep blindly
saying these videos are low quality, lets improve the queue so i actually
understand exactly how these beats are being generated." That shipped as folds
of text — 641 jobs, 3,361 artifact URLs, and NOTHING VISIBLE until you opened
one. His verdict, the same day: *"looks like you were pretty lazy with the queue
history.. i expected you to be able to scroll, see images and prompts and these
details all with a nice interface, more visuals, can you do that?"*

He was right, and the fix is not decoration. A page about how frames look that
shows no frames is a data dump wearing a page's clothes. So:

  THE GRID IS THE PAGE. Every finished job is a card with its output visible as
  a thumbnail, newest first, grouped under the day it finished. Clicking one
  opens the record — the output large, the frame it started from, the reference
  it was conditioned on, both prompts as readable prose, the recipe, and who was
  waiting for it.

FOUR THINGS THAT ARE NOT STYLE OPINIONS, each of which cost something to learn:

1. **The thumbnails are a separate branch, and they have to be.** The artifacts
   are full-resolution PNGs with a median of 862 KB. A grid of 348 of them costs
   300 MB to scroll — `loading="lazy"` does not save that, it only spreads it
   over the scroll, on his phone, on cellular. `pipeline/queue_thumbs.py` writes
   a 512 px JPEG for each one (~15 KB, a 58× cut) onto the `site-thumbs` branch,
   and every `<img>` here points at the thumb with `data-f` holding the
   original. A thumb that is missing falls back to the full frame in the
   browser: a slower card, never an empty one.

2. **The bulk of the record is fetched, not baked.** The cards are in these
   bytes — markup, thumbnails, beats, outcomes, a prompt line each — so the
   gallery works with JavaScript off and is greppable in the built file. The
   FULL prompts, recipes and purposes are `queue-data.json` (the index and the
   search corpus) and `queue-detail.json` (opened on the first click). That is
   what took the page from 2.8 MB to a fifth of that without hiding anything:
   the same facts, one fetch away instead of one megabyte away.

3. **A prompt nobody recorded says so, with the reason.** Never reconstructed —
   the 77-token fit happened on the box's tokenizer and a recomputation can
   differ exactly where it would matter. Same for a job whose artifacts are not
   on the branch: the card says the artifact is missing rather than showing an
   empty tile that reads as "this render produced nothing".

4. **Green is the machine's clock, amber is the author's**, here as everywhere
   on this site. A held spec is amber because the machine is not what is holding
   it up.

WHERE THE HISTORY COMES FROM. `queue_history.py` joins the box's run sidecars
(on `farm-results-rtx5090`) against the committed specs on `main` and writes
`pipeline/measured/queue-history.json`. A Vercel deploy checkout has no farm
branches and a reader's browser cannot join yaml across two of them, so the join
happens on a laptop and the answer is committed. THE PAGE IS EXACTLY AS OLD AS
THAT FILE, it says so at the top in the same breath as the counts, and
re-running the generator is the only thing that moves it (SITE.md, "the queue
history's refresh duty"). The one block a reader can trust as *now* is the live
one, which reads the box's telemetry branch in their own browser.
"""
from __future__ import annotations

import datetime
import html
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
import repo_slug  # noqa: E402  one source for "which repo is this"
from queue_thumbs import THUMB_BRANCH, thumb_rel  # noqa: E402  one naming rule

HISTORY = REPO / "pipeline" / "measured" / "queue-history.json"
JOBS_DIR = REPO / "pipeline" / "jobs"

RAW = repo_slug.RAW_URL
REPO_URL = repo_slug.REPO_URL

# The branch the courier pushes artifacts to, the branch the thumbnailer writes
# to, and the branch the telemetry daemon publishes vitals to. Three branches on
# purpose — see test_the_courier_and_the_telemetry_daemon_own_different_branches
# and queue_thumbs.py's note on why the thumbs are not in with the originals.
# The legacy telemetry URL stays because the box's scheduled task is re-enabled
# by hand and the old place can be the fresher one for a while after a change.
RESULTS_BRANCH = "farm-results-rtx5090"
RESULTS_BASE = f"{RAW}/{RESULTS_BRANCH}"
THUMB_BASE = f"{RAW}/{THUMB_BRANCH}"
TELEMETRY_URL = f"{RAW}/farm-telemetry-rtx5090/telemetry.json"
TELEMETRY_URL_LEGACY = f"{RAW}/{RESULTS_BRANCH}/telemetry.json"

# Three missed publishes. The daemon writes every five minutes, so anything
# older than this is a record and not a reading — the same rule and the same
# number the status page's queue block keys on.
STALE_MINUTES = 15

# THE DENOMINATOR UNDER THE FAILED CHIP. Telemetry publishes `queue.failed` as a
# bare count of jsons in the box's failed/ dir, and this page rendered it red as
# "39 sitting failed" — true, and still a lie by omission, because all 39 were
# diagnosed and written down (33 in the triage doc, 6 in the compseed specs'
# own SUPERSEDED headers). A permanent red number nobody can act on teaches a
# reader to stop reading red numbers. So the acknowledged ids are committed, the
# page subtracts them, and red is reserved for a failure that is actually new.
# Counts, not ids — telemetry publishes no id list; the blind spot that leaves is
# stated in the yaml's own header rather than hidden.
ACK_FAILED_FILE = "pipeline/measured/failed-acknowledged.yaml"
ACK_DOC = "pipeline/queue-failure-triage-0817.md"

# Oleg reads this in Dubai and every clock face on every page of this site is
# +04 and says so. The JSON underneath is UTC and stays that way.
TZ = datetime.timezone(datetime.timedelta(hours=4))
TZ_LABEL = "+04"

# What the page prints where a prompt should be and is not. Constants because
# the tests check for exactly these, and a page that quietly stopped saying it
# would be a page that quietly started implying the prompt was empty.
NO_PROMPT = "PROMPT NOT RECORDED"
NO_NEGATIVE = "NEGATIVE PROMPT NOT RECORDED"
# NOT "no artifact on the branch", which this page spent a build claiming and
# could not support: nothing here ever reads the results branch. The builder
# reads one thing — the `outputs` list in queue-history.json — so the only fact
# it can state is that the list is empty. Measured 2026-08-15: all 222 tiles
# carrying this marker also have no `artifacts_dir`, and at least 25 of them DO
# have frames sitting on farm-results-rtx5090 under a directory named after the
# job, which the history file never linked. The old wording called those renders
# fileless; they are records missing a field.
NO_ARTIFACT = "NO FILE IN THIS RUN'S RECORD"

# The card's one-line prompt. Long enough to tell two renders of the same beat
# apart at a glance, short enough that 573 of them are a page and not a book.
SNIPPET = 88

DATA_FILE = "queue-data.json"
DETAIL_FILE = "queue-detail.json"

KIND_WORDS = {
    "motion": "motion take",
    "still": "still",
    "still-ipa": "still · reference",
    "inpaint": "inpaint",
    "other": "job",
}

STATE_WORDS = {
    "held": ("amber", "HELD — waiting on the author"),
    "authored": ("green", "AUTHORED — runnable, not yet finished"),
    "cancelled-by-founder": ("muted", "CANCELLED by the founder"),
}


CSS = """
/* A gallery needs the width. Every other page on this site is a column of
   prose at 720px; this one is a contact sheet, and at 720px it is three
   thumbnails wide on a laptop. */
main { max-width: 1180px; }

.qlede { color: var(--muted); }
.qprov { font: 500 .78rem/1.7 var(--mono); color: var(--faint); margin: .4rem 0 0; }

/* ---- the freshness line, and the banner it becomes when the feed dies ----
   THE DEFECT THIS EXISTS FOR (founder, 2026-08-20): he opened /queue and read
   "Finished — newest day first" with Sunday 16 August at the top, four days
   after the fact, and took it for a quiet card. It was not: the box rendered
   246 jobs in those four days and pushed every one to the results branch. What
   had stopped was the hand-run regeneration of queue-history.json. A page whose
   newest row is days old must say so IN THE READER'S WORDS, because the one
   thing a reader cannot tell from an empty top row is which of the two silences
   it is. Quiet when fresh (it is a fact, not an alarm); loud when not. */
.qfresh { font: 500 .82rem/1.7 var(--mono); color: var(--muted); margin: .35rem 0 0; }
/* The AGE is the only word in the quiet line worth a glance — the founder is
   asking "how far behind am I looking", not "what time is it in +04". Tightened
   2026-08-21 with the threshold, because the quiet line is what he reads on the
   99 refreshes where nothing is wrong, and a faint one taught him not to. */
.qfresh b.qage { color: var(--ink); font-weight: 700; font-variant-numeric: tabular-nums; }
.qfresh.stale { display: block; margin: .9rem 0 0; padding: .75rem .9rem;
  border: 1px solid var(--alarm, #e2564d); border-left-width: 4px; border-radius: 10px;
  color: var(--ink); background: color-mix(in srgb, var(--alarm, #e2564d) 9%, transparent);
  font: 500 .84rem/1.65 var(--mono); }
.qfresh.stale b { color: var(--alarm, #e2564d); letter-spacing: .04em; }
.qfresh .qfresh-fix { display: block; margin: .35rem 0 0; color: var(--muted); }

/* ---- the counters across the top ---- */
.qstats { display: grid; gap: .5rem; margin: 1rem 0 0; padding: 0; list-style: none;
  grid-template-columns: repeat(auto-fit, minmax(132px, 1fr)); }
.qstats li { padding: .6rem .8rem; border: 1px solid var(--line); border-radius: 10px;
  background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.qstats b { display: block; font: 700 1.28rem/1.25 var(--mono); color: var(--ink);
  font-variant-numeric: tabular-nums; }
.qstats span { font: 500 .72rem/1.5 var(--mono); color: var(--faint); }
.qstats li.work b { color: var(--leaf); }
.qstats li.wait b { color: var(--sap); }
.qstats li.bad b { color: var(--alarm, #e2564d); }

/* ---- live block ---- */
.qlive { margin: 1rem 0 0; padding: .9rem 1rem; border: 1px solid var(--line);
  border-radius: 14px; background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.qlive .qnow-t { font: 700 .95rem/1.4 var(--mono); color: var(--leaf); margin: .2rem 0 0; }
.qlive .qsay { font: 500 .82rem/1.7 var(--mono); color: var(--muted); margin: .35rem 0 0; }
.qlive .qsay.none { color: var(--faint); }
.qchips { display: flex; flex-wrap: wrap; gap: .4rem; margin: .55rem 0 0; }
.qchip { font: 700 .7rem/1 var(--mono); letter-spacing: .05em; text-transform: uppercase;
  padding: .34rem .6rem; border-radius: 999px; border: 1px solid var(--line);
  color: var(--muted); background: var(--code-bg); }
.qchip.work { color: var(--leaf); border-color: var(--leaf-deep); }
.qchip.wait { color: var(--sap); border-color: var(--sap-deep); }
.qchip.bad { color: var(--alarm, #e2564d); border-color: var(--alarm, #e2564d); }

/* ---- the jump bar: the gallery is 43 screens down on a phone without it ---- */
.qjump { display: flex; flex-wrap: wrap; gap: .4rem; margin: .7rem 0 0; }
.qjump a { font: 700 .7rem/1 var(--mono); letter-spacing: .04em; text-transform: uppercase;
  min-height: 34px; display: inline-flex; align-items: center; padding: .3rem .7rem;
  border-radius: 999px; border: 1px solid var(--line); background: var(--code-bg);
  color: var(--muted); text-decoration: none; }
.qjump a:hover { color: var(--ink); border-color: var(--leaf-deep); }

/* ---- upcoming ---- */
.qupwrap { margin: .6rem 0 0; }
.qupwrap > summary { cursor: pointer; list-style: none; padding: .5rem .7rem;
  border: 1px solid var(--line); border-radius: 12px; background: var(--panel);
  font: 700 .74rem/1.4 var(--mono); letter-spacing: .04em; color: var(--muted); }
.qupwrap > summary::-webkit-details-marker { display: none; }
.qupwrap > summary::after { content: " \\2014 tap to open"; color: var(--faint);
  font-weight: 500; letter-spacing: 0; }
.qupwrap[open] > summary { color: var(--ink); border-color: var(--leaf-deep); }
.qupwrap[open] > summary::after { content: " \\2014 tap to fold away"; }
.qupwrap > summary:focus-visible { outline: 2px solid var(--sap); outline-offset: 1px; }
.qupgrid { display: grid; gap: .6rem; margin: .6rem 0 0;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
.qup { border: 1px solid var(--line); border-left-width: 3px; border-radius: 12px;
  padding: .65rem .8rem .75rem; background: var(--panel); }
.qup.amber { border-left-color: var(--sap); }
.qup.green { border-left-color: var(--leaf-deep); }
.qup.muted { opacity: .72; }
.qup .top { display: flex; flex-wrap: wrap; gap: .3rem .6rem; align-items: baseline;
  font: 500 .78rem/1.5 var(--mono); color: var(--faint); }
.qup .beat { font-weight: 700; color: var(--ink); font-variant-numeric: tabular-nums; }
.qup .state { font-weight: 700; }
.qup.amber .state { color: var(--sap); }
.qup.green .state { color: var(--leaf); }

/* ---- the sticky control bar ---- */
.qbar { position: sticky; top: 0; z-index: 6; margin: 1.4rem 0 0;
  padding: .6rem .7rem; border: 1px solid var(--line); border-radius: 12px;
  background: var(--bg); box-shadow: 0 10px 24px -18px rgba(0,0,0,.9);
  display: flex; flex-wrap: wrap; gap: .45rem .6rem; align-items: center; }
.qbar input[type=search] { flex: 1 1 220px; min-height: 40px; min-width: 0;
  font: 500 .88rem/1.4 var(--mono); color: var(--ink); background: var(--code-bg);
  border: 1px solid var(--line); border-radius: 999px; padding: .4rem .9rem; }
.qbar select { min-height: 34px; font: 700 .7rem/1 var(--mono); letter-spacing: .04em;
  text-transform: uppercase; padding: .3rem 1.6rem .3rem .65rem; border-radius: 999px;
  cursor: pointer; border: 1px solid var(--line); background: var(--code-bg);
  color: var(--muted); -webkit-appearance: none; appearance: none;
  background-image: linear-gradient(45deg, transparent 50%, currentColor 50%),
    linear-gradient(135deg, currentColor 50%, transparent 50%);
  background-position: right .78rem center, right .58rem center;
  background-size: 5px 5px, 5px 5px; background-repeat: no-repeat; }
.qbar select.on { background-color: var(--leaf-dim); color: var(--ink);
  border-color: var(--leaf-deep); }
.qbar input:focus-visible, .qbar button:focus-visible,
.qbar select:focus-visible { outline: 2px solid var(--sap); outline-offset: 1px; }
.qset { display: flex; flex-wrap: wrap; gap: .3rem; }
.qbtn { font: 700 .7rem/1 var(--mono); letter-spacing: .04em; text-transform: uppercase;
  min-height: 34px; padding: .3rem .65rem; border-radius: 999px; cursor: pointer;
  border: 1px solid var(--line); background: var(--code-bg); color: var(--muted); }
.qbtn:hover { color: var(--ink); }
.qbtn[aria-pressed=true] { background: var(--leaf-dim); color: var(--ink);
  border-color: var(--leaf-deep); }
.qbtn.bad[aria-pressed=true] { background: transparent; color: var(--alarm, #e2564d);
  border-color: var(--alarm, #e2564d); }
.qcount { flex: 1 1 100%; margin: 0; font: 500 .74rem/1.5 var(--mono);
  color: var(--faint); font-variant-numeric: tabular-nums; }

/* ---- the gallery ---- */
.qdaysec { margin: 1.1rem 0 0; }
.qdh { position: sticky; top: var(--qbarh, 3.6rem); z-index: 4; margin: 0;
  padding: .45rem .1rem; background: var(--bg);
  font: 700 .76rem/1.5 var(--mono); letter-spacing: .09em; text-transform: uppercase;
  color: var(--muted); border-bottom: 1px solid var(--line); }
.qdh .n { color: var(--faint); font-weight: 500; text-transform: none; letter-spacing: 0; }
.qgrid { display: grid; gap: .55rem; margin: .55rem 0 0;
  grid-template-columns: repeat(auto-fill, minmax(148px, 1fr)); }

.qc { position: relative; display: block; width: 100%; text-align: left; padding: 0;
  border: 1px solid var(--line); border-radius: 12px; overflow: hidden;
  background: var(--panel); color: inherit; cursor: pointer; font: inherit; }
.qc:hover { border-color: var(--leaf-deep); }
.qc:focus-visible { outline: 2px solid var(--sap); outline-offset: 2px; }
.qc.failed { border-color: var(--alarm, #e2564d); }
.qc .shot { display: block; width: 100%; aspect-ratio: 3 / 4; object-fit: cover;
  background: var(--code-bg); border-bottom: 1px solid var(--line-soft); }
.qc .none { display: flex; align-items: center; justify-content: center;
  text-align: center; padding: .6rem; aspect-ratio: 3 / 4; background: var(--code-bg);
  font: 700 .62rem/1.5 var(--mono); letter-spacing: .06em; color: var(--faint);
  border-bottom: 1px solid var(--line-soft); }
.qc .play { position: absolute; top: .4rem; right: .4rem; width: 26px; height: 26px;
  border-radius: 50%; background: rgba(6,12,8,.72); color: #eaf6ec;
  font: 700 .62rem/26px var(--mono); text-align: center; pointer-events: none; }
.qc .m { padding: .4rem .5rem .55rem; }
.qc .row { display: flex; flex-wrap: wrap; gap: .25rem .45rem; align-items: baseline;
  font: 500 .68rem/1.4 var(--mono); color: var(--faint); }
.qc .beat { font-weight: 700; color: var(--ink); font-variant-numeric: tabular-nums; }
.qc .kind { color: var(--leaf); }
.qc.failed .kind { color: var(--alarm, #e2564d); }
.qc .p { margin: .3rem 0 0; font: 500 .7rem/1.45 var(--mono); color: var(--muted);
  overflow-wrap: anywhere; }
.qc .p.gap { color: var(--sap); }
.qhide { display: none !important; }

.qmore { margin: 1rem 0 0; }
.qnote { font: 500 .8rem/1.7 var(--mono); color: var(--faint); margin: .8rem 0 0; }

/* ---- the record, opened ---- */
.qbox[hidden] { display: none; }
.qbox { position: fixed; inset: 0; z-index: 50; overflow-y: auto;
  background: rgba(3,8,5,.88); padding: .6rem; }
.qbox-in { max-width: 1100px; margin: 0 auto 3rem; background: var(--panel);
  border: 1px solid var(--line); border-radius: 16px; box-shadow: var(--shadow); }
.qbox-bar { position: sticky; top: 0; z-index: 2; display: flex; flex-wrap: wrap;
  gap: .4rem; align-items: center; justify-content: space-between;
  padding: .55rem .7rem; background: var(--panel-2);
  border-bottom: 1px solid var(--line); border-radius: 16px 16px 0 0; }
.qbox-bar .who { font: 700 .8rem/1.4 var(--mono); color: var(--ink); }
.qbox-body { padding: .8rem .9rem 1.2rem; }
.qmedia { display: grid; gap: .7rem; margin: 0 0 .3rem; }
@media (min-width: 860px) { .qmedia { grid-template-columns: 3fr 2fr; align-items: start; } }
.qbig img, .qbig video { width: 100%; display: block; border-radius: 10px;
  border: 1px solid var(--line); background: var(--code-bg); }
.qstrip { display: grid; gap: .35rem; margin: .4rem 0 0;
  grid-template-columns: repeat(auto-fill, minmax(64px, 1fr)); }
.qstrip img { width: 100%; aspect-ratio: 1; object-fit: cover; display: block;
  border-radius: 6px; border: 1px solid var(--line); cursor: pointer; }
.qstrip img[aria-current=true] { border-color: var(--sap); }
.qside figure { margin: 0 0 .6rem; }
.qside img { width: 100%; display: block; border-radius: 10px; border: 1px solid var(--line);
  background: var(--code-bg); }
.qh { font: 700 .66rem/1.6 var(--mono); letter-spacing: .12em; text-transform: uppercase;
  color: var(--faint); margin: .9rem 0 .25rem; }
.qprose { font: 400 .95rem/1.65 var(--body); color: var(--ink); background: var(--code-bg);
  border: 1px solid var(--line-soft); border-radius: 10px; padding: .65rem .8rem;
  margin: 0; overflow-wrap: anywhere; }
.qprose.neg { color: var(--muted); }
.qgap { font: 700 .8rem/1.6 var(--mono); color: var(--sap); margin: 0; }
.qgap i { color: var(--faint); font-style: normal; font-weight: 500; }
.qmeta { font: 500 .78rem/1.7 var(--mono); color: var(--faint); margin: .3rem 0 0;
  overflow-wrap: anywhere; }
.qmeta b { color: var(--muted); font-weight: 700; }
.qbox .rc-ok { color: var(--leaf); }
.qbox .rc-bad, .qc .rc-bad { color: var(--alarm, #e2564d); font-weight: 700; }

/* ---- the lens: any frame at full size, without leaving the page ----
   Every picture on the record is a thumbnail or a fitted copy. Tapping one used
   to navigate to raw.githubusercontent.com, which on a phone is a one-way trip
   out of the gallery and back through a cold page load. The lens shows the
   full-resolution bytes over the record and hands the scroll position back. */
.qzoom { cursor: zoom-in; }
.qlens[hidden] { display: none; }
.qlens { position: fixed; inset: 0; z-index: 60; display: flex; flex-direction: column;
  background: rgba(2,6,4,.96); padding: .5rem; }
.qlens-bar { display: flex; gap: .4rem; align-items: center; justify-content: space-between;
  flex: 0 0 auto; }
.qlens-bar .cap { font: 500 .74rem/1.5 var(--mono); color: var(--muted);
  overflow-wrap: anywhere; }
.qlens-fig { flex: 1 1 auto; min-height: 0; display: flex; align-items: center;
  justify-content: center; margin: .4rem 0 0; }
.qlens-fig img, .qlens-fig video { max-width: 100%; max-height: 100%;
  width: auto; height: auto; object-fit: contain; border-radius: 8px;
  background: var(--code-bg); }
"""


# ---------------------------------------------------------------- reading

# --- the episode-1 publication correction, applied at RENDER time -------------
# Ten of the `upcoming` rows this page draws were authored 2026-08-11..13, while
# episode 1 was still open, and their `consumer:` prose still names the reader as
# the man being asked to pass it: "the episode-1 cut he is being asked to pass"
# (three rows still drawn `held` — the page counts those as "held on you") and
# "the next ep1 screening cut" (seven he cancelled himself). He closed episode 1
# on 2026-08-13 — "we have already published it dude, we are done. lets move on
# to episode 2." — recorded three times in review/inbox.yaml's `resolved:`
# entries and carried verbatim in pipeline/measured/episode-progress.yaml
# `ep1_publication_CORRECTION_0819`. Episode 1 has been live for a week.
#
# THE SPECS THEMSELVES ARE NOT REWRITTEN. A job spec is the record of what was
# asked for on the day it was written, and editing its body would destroy that —
# the same reason that correction key keeps `states_before` beside the new states
# instead of overwriting them. So the correction is applied to the page's copy of
# the row, not to the file: the original sentence stays readable and a dated
# sibling follows it, which is this house's way of superseding a written thing.
#
# Applied here in `load()` because it is the one door all of this page's data
# comes through — the HTML cards, queue-data.json, queue-detail.json and the
# SPECS map the live block matches a running job against all read what this
# returns, so correcting it once means no two surfaces can disagree.
EP1_DRIFT_PHRASES = ("being asked to pass", "the next ep1 screening cut",
                     "episode-1 cut he is about")
EP1_SHIPPED_CORRECTION = (
    "CORRECTION 2026-08-19 — the sentence above was written before the founder "
    "closed episode 1 on 2026-08-13 (“we have already published it dude, we "
    "are done. lets move on to episode 2.”). Episode 1 is published and "
    "live; nothing here is waiting on him to pass it. See "
    "ep1_publication_CORRECTION_0819 in pipeline/measured/episode-progress.yaml.")


def ep1_drift(text) -> bool:
    """Does this consumer line still narrate episode 1 as awaiting his pass?"""
    low = str(text or "").lower()
    return any(p in low for p in EP1_DRIFT_PHRASES)


def apply_ep1_correction(data: dict) -> dict:
    """Append the dated correction to every upcoming row that still asks him to
    pass a published episode. Idempotent, and it never edits the sentence it
    corrects. Returns `data` for chaining."""
    for row in (data.get("upcoming") or []):
        if not isinstance(row, dict):
            continue
        said = row.get("consumer")
        if said and ep1_drift(said) and EP1_SHIPPED_CORRECTION not in said:
            row["consumer"] = f"{said} {EP1_SHIPPED_CORRECTION}"
    return data


def load(path: Path = None) -> dict | None:
    """The committed history, or None. Never raises: a missing or half-written
    file must degrade this page to an honest sentence, not red the whole site
    build — several lanes share this tree and one of them may be mid-write."""
    p = Path(path) if path else HISTORY
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return apply_ep1_correction(data) if isinstance(data, dict) else None


def acknowledged_failures() -> int:
    """How many entries in the box's failed/ pile are triaged and written down.

    The LIST is the source of truth, never the file's own `count:` — a stale
    hand-maintained integer is exactly the kind of number this whole change
    exists to stop publishing. Unreadable, absent or unparseable all return 0,
    which makes the chip fall back to the old plain red count: on a failed read
    the page under-claims rather than quietly marking new failures as known.
    """
    try:
        import yaml
        doc = yaml.safe_load(
            (REPO / ACK_FAILED_FILE).read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return 0
    if not isinstance(doc, dict):
        return 0
    rows = doc.get("acknowledged")
    if not isinstance(rows, list):
        return 0
    return sum(1 for r in rows if isinstance(r, dict) and r.get("id"))


def spec_success(rel: str) -> str | None:
    """The `success:` line of a committed spec — what the job is FOR, in the
    author's own words. Read here rather than taken from the history file
    because the history's upcoming rows carry consumer and why and not this.

    Best effort by design: a spec a peer lane deleted five seconds ago, or a
    yaml no parser on this machine can read, returns None and the card simply
    does not show the line. Never an exception; this is decoration on a page
    whose load-bearing content is elsewhere.
    """
    if not rel:
        return None
    p = REPO / rel
    try:
        if not p.is_file() or JOBS_DIR not in p.resolve().parents:
            return None
        import yaml
        spec = yaml.safe_load(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None
    if not isinstance(spec, dict):
        return None
    got = spec.get("success")
    return str(got).strip() or None if got else None


# ---------------------------------------------------------------- formatting

def _e(s) -> str:
    return html.escape("" if s is None else str(s))


def parse_iso(iso: str):
    """`2026-08-14T16:24:58Z` → aware datetime in +04, or None."""
    if not iso:
        return None
    try:
        dt = datetime.datetime.strptime(str(iso), "%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError):
        return None
    return dt.replace(tzinfo=datetime.timezone.utc).astimezone(TZ)


def day_key(iso: str) -> str:
    """The +04 calendar day a job finished on. Jobs the box could not stamp go
    in one bucket of their own rather than being dated by today's clock."""
    dt = parse_iso(iso)
    return dt.strftime("%Y-%m-%d") if dt else "undated"


def day_title(key: str) -> str:
    if key == "undated":
        return "No finish time recorded"
    try:
        dt = datetime.datetime.strptime(key, "%Y-%m-%d")
    except ValueError:
        return key
    return dt.strftime("%a %-d %B %Y") if sys.platform != "win32" else dt.strftime("%a %d %B %Y")


def clock(iso: str) -> str:
    dt = parse_iso(iso)
    return dt.strftime("%H:%M") if dt else "—"


# How old the newest finished render may be before this page calls its own feed
# dead. The box's own quiet gaps are minutes (see ledger_freshness.py's measured
# p50 3.3 min / longest-ever 0.75 h off 2107 commits), so anything past a few
# hours is already far outside any silence the card has ever taken while working.
#
# IT WAS 24 UNTIL 2026-08-21, AND 24 WAS TOO SLACK — the same defect fired a
# SECOND time inside a day: ~40 renders ran overnight, the page still showed
# 20 August, and the founder had to ask again. A day-long fuse means a founder
# opening /queue at lunchtime sees a quiet card over a feed that stopped at
# breakfast and reads it as an idle box. Four hours is the number because the
# refresh is now hourly (.github/workflows/queue-refresh.yml): four missed runs
# in a row is a broken loop and nothing else, so the banner can only fire when
# something is actually wrong, and it fires while the day is still young enough
# to fix. Change the cron and change this together — they are one mechanism.
FEED_STALE_HOURS = 4


def age_span(seconds: float) -> str:
    """A gap in seconds → the bare span a person would say. Never `0 days`.

    Split out from `age_words` because the banner has to say how far BEHIND the
    feed is ("4 hours behind"), not when the last thing happened, and gluing
    "ago" on and cutting it off again is how the two drift apart.
    """
    s = max(0.0, float(seconds))
    if s < 5400:
        return f"{int(round(s / 60))} minutes"
    if s < 36 * 3600:
        h = s / 3600.0
        return f"{h:.0f} hours" if h >= 2 else "an hour"
    d = s / 86400.0
    return f"{d:.1f} days" if d < 10 else f"{int(round(d))} days"


def age_words(seconds: float) -> str:
    """A gap in seconds → the phrase a person would say. Never `0 days`."""
    return f"{age_span(seconds)} ago"


def newest_finish(jobs: list) -> str | None:
    """The `finished_at` of the most recent run this page can show, or None.

    Read off the rows and not off `_meta.measured_at` on purpose: measured_at is
    when the GENERATOR ran, and the 2026-08-20 defect is exactly a generator
    that had not run. The only honest answer to "how current is this page" is
    the timestamp of the newest thing on it.
    """
    stamps = [j.get("finished_at") for j in jobs
              if isinstance(j, dict) and j.get("finished_at")]
    return max(stamps) if stamps else None


def freshness_html(jobs: list, now: datetime.datetime = None) -> str:
    """The line above the gallery that says how current the gallery is.

    Three states and no fourth: fresh (a quiet fact), stale (a red banner naming
    the date the feed stopped and the command that restarts it), and undatable
    (say that, rather than implying either). The element always carries
    `data-newest` so the reader's own browser can re-decide — a page built while
    fresh and read three days later is the same lie in slower motion, and the
    script at the bottom re-renders this from the client clock.
    """
    now = now or datetime.datetime.now(datetime.timezone.utc)
    newest = newest_finish(jobs)
    dt = parse_iso(newest)
    if dt is None:
        return ('<p class="qfresh stale" data-newest="">'
                '<b>THE AGE OF THIS PAGE IS UNKNOWN.</b> Not one row carries a '
                'finish time, so nothing here can be dated and this page will '
                'not guess. Re-run <code>python3 pipeline/queue_history.py</code>.'
                '</p>')

    age_s = (now - dt).total_seconds()
    when = dt.strftime("%a %-d %B %Y at %H:%M" if sys.platform != "win32"
                       else "%a %d %B %Y at %H:%M")
    attrs = f'data-newest="{_e(newest)}" data-stale-h="{FEED_STALE_HOURS}"'

    if age_s < FEED_STALE_HOURS * 3600:
        # The AGE is the bold word, not the date. A founder scanning this line
        # wants one number — how far behind am I looking — and a formatted
        # timestamp is not that number; he has to subtract it from his own
        # clock, which is the arithmetic that let 20 August read as "recent".
        return (f'<p class="qfresh" {attrs}>Newest render on this page finished '
                f'<b class="qage">{_e(age_words(age_s))}</b> — {_e(when)} '
                f'{TZ_LABEL}.</p>')

    return (
        f'<p class="qfresh stale" {attrs}>'
        f'<b>THIS FEED IS STALE — <span class="qage">{_e(age_span(age_s))}</span> '
        f'BEHIND. Renders continue on the box.</b> '
        f'Nothing newer than {_e(when)} {TZ_LABEL} is on this '
        f'page, and that is a statement about the page, NOT about the render '
        f'box: the box publishes every finished job to '
        f'<code>{_e(RESULTS_BRANCH)}</code> as it goes, and anything it has run '
        f'since that time exists and is simply not shown here. An empty top row '
        f'on a stale feed is not an idle card.'
        f'<span class="qfresh-fix">The page is baked from the committed '
        f'<code>pipeline/measured/queue-history.json</code>, refreshed hourly by '
        f'<code>.github/workflows/queue-refresh.yml</code> — past '
        f'{FEED_STALE_HOURS} h that workflow is what has stopped, not the box. '
        f'Check it, or move the file by hand: '
        f'<code>python3 pipeline/queue_history.py --fetch</code>, then '
        f'<code>python3 pipeline/queue_thumbs.py --push</code>, commit, push. '
        f'To check before trusting it: '
        f'<code>python3 pipeline/ledger_freshness.py</code>.</span></p>')


def dur_words(sec) -> str:
    """Seconds → `2m 53s`. A duration nobody measured is an em dash, never 0s."""
    try:
        s = int(sec)
    except (TypeError, ValueError):
        return "—"
    if s < 0:
        return "—"
    if s < 60:
        return f"{s}s"
    m, r = divmod(s, 60)
    if m < 60:
        return f"{m}m {r:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h {m:02d}m"


def kind_word(kind) -> str:
    return KIND_WORDS.get(kind or "", str(kind or "job"))


def art_url(path: str) -> str:
    """A box artifact path → its URL on the courier branch.

    Nothing is copied into `_site/`: the branch already holds these bytes and
    GitHub's raw CDN already serves them with CORS. A leading slash or a
    Windows separator would produce a 404 that looks like a missing render, so
    both are normalised here rather than at 1,700 call sites.
    """
    return f"{RESULTS_BASE}/{_rel(path)}"


def thumb_url(path: str) -> str:
    """The same artifact's 512 px preview on the thumb branch.

    Every card points here first and carries the full-size URL alongside, so a
    frame the thumbnailer has not caught up with costs one card a slow load
    instead of showing a hole. `queue_thumbs.thumb_rel` is imported rather than
    reimplemented: two functions agreeing on a filename by coincidence is how a
    gallery quietly loses half its pictures.
    """
    return f"{THUMB_BASE}/{thumb_rel(_rel(path))}"


def _rel(path: str) -> str:
    return str(path or "").replace("\\", "/").lstrip("/")


def snippet(text: str, limit: int = SNIPPET) -> str:
    """The card's one prompt line. Cut on a word boundary and marked with an
    ellipsis — the full text is one tap away and is never what this returns."""
    t = " ".join(str(text or "").split())
    if len(t) <= limit:
        return t
    cut = t[:limit].rsplit(" ", 1)[0]
    return (cut or t[:limit]) + "…"


def first_of(job: dict, kind: str) -> dict | None:
    for out in job.get("outputs") or []:
        if isinstance(out, dict) and out.get("kind") == kind and out.get("path"):
            return out
    return None


# ---------------------------------------------------------------- the cards

def card_html(job: dict, i: int) -> str:
    """One finished render, as a tile you can see.

    A button and not a div: it is the page's main control, it must be reachable
    by keyboard and announced as pressable, and every card on this grid does the
    same thing when you hit it.
    """
    beat = job.get("beat")
    rc = job.get("rc")
    failed = bool(rc)
    img = first_of(job, "image")
    vid = first_of(job, "video")

    if img:
        # The poster for a motion take is the still the same job wrote beside
        # it; a <video> per card would be 243 media elements on a phone to show
        # 243 first frames.
        shot = (f'<img class="shot" loading="lazy" decoding="async" alt="" '
                f'src="{_e(thumb_url(img["path"]))}" '
                f'data-f="{_e(art_url(img["path"]))}" '
                f'onerror="this.onerror=null;this.src=this.dataset.f">')
    elif vid:
        shot = (f'<video class="shot" preload="none" muted playsinline '
                f'src="{_e(art_url(vid["path"]))}"></video>')
    else:
        # Not an empty tile: an empty tile reads as "this render produced
        # nothing", and what is true is that the branch carries no file under
        # this job's name.
        shot = f'<div class="none">{NO_ARTIFACT}</div>'

    play = '<span class="play">&#9654;</span>' if vid else ""
    beat_txt = f"beat {int(beat):02d}" if isinstance(beat, int) else "no beat"
    outcome = ('<span class="rc-bad">FAILED</span>' if failed else
               f'<span>{_e(clock(job.get("finished_at")))}</span>')
    n = len(job.get("outputs") or [])
    files = f'<span>{n} file{"" if n == 1 else "s"}</span>' if n else ""
    line = (snippet(job["prompt"]) if job.get("prompt") else NO_PROMPT)
    gap = "" if job.get("prompt") else " gap"

    return (
        f'<button type="button" class="qc{" failed" if failed else ""}" '
        f'data-i="{i}" data-b="{_e(beat) if beat is not None else ""}" '
        f'data-k="{_e(job.get("kind") or "other")}" data-r="{1 if failed else 0}">'
        f'{shot}{play}'
        f'<span class="m">'
        f'<span class="row"><span class="beat">{_e(beat_txt)}</span>'
        f'<span class="kind">{_e(kind_word(job.get("kind")))}</span>'
        f'{outcome}{files}</span>'
        f'<span class="p{gap}">{_e(line)}</span>'
        f'</span></button>')


def day_section(key: str, jobs: list, start: int) -> str:
    ok = sum(1 for j in jobs if not j.get("rc"))
    bad = len(jobs) - ok
    mins = sum(int(j.get("duration_s") or 0) for j in jobs) / 60.0
    note = (f'<span class="n">{len(jobs)} job{"" if len(jobs) == 1 else "s"}'
            + (f", {bad} failed" if bad else "")
            + (f" · {mins / 60:.1f} h of machine time" if mins >= 60
               else f" · {mins:.0f} min of machine time" if mins else "")
            + "</span>")
    cards = "".join(card_html(j, start + n) for n, j in enumerate(jobs))
    return (f'<section class="qdaysec" data-day="{_e(key)}">'
            f'<h3 class="qdh">{_e(day_title(key))} {note}</h3>'
            f'<div class="qgrid">{cards}</div></section>')


def upcoming_card(row: dict, success: str | None) -> str:
    state = row.get("state") or "authored"
    colour, words = STATE_WORDS.get(state, ("green", state.upper()))
    beat = row.get("beat")
    beat_txt = f"beat {int(beat):02d}" if isinstance(beat, int) else "no beat"
    est = row.get("est_minutes")
    body = []
    if row.get("consumer"):
        body.append(f'<p class="qh">Consumer — who is waiting for it</p>'
                    f'<p class="qmeta">{_e(row["consumer"])}</p>')
    if success:
        body.append(f'<p class="qh">What would count as success</p>'
                    f'<p class="qmeta">{_e(success)}</p>')
    if row.get("hold_reason"):
        body.append(f'<p class="qh">What is holding it</p>'
                    f'<p class="qmeta">{_e(row["hold_reason"])}</p>')
    elif row.get("why_first"):
        body.append(f'<p class="qh">Why</p><p class="qmeta">{_e(row["why_first"])}</p>')
    tail = [f'<b>job</b> {_e(row.get("id"))}']
    if row.get("spec_file"):
        tail.append(f'<a href="{REPO_URL}/blob/main/{_e(row["spec_file"])}">spec</a>')
    body.append(f'<p class="qmeta">{" · ".join(tail)}</p>')
    return (
        f'<article class="qup {colour}" data-b="{_e(beat) if beat is not None else ""}">'
        f'<p class="top"><span class="beat">{_e(beat_txt)}</span>'
        f'<span>{_e(kind_word(row.get("kind")))}</span>'
        f'<span class="state">{_e(words)}</span>'
        + (f'<span>~{_e(est)} min</span>' if est else "")
        + f'</p>{"".join(body)}</article>')


# ---------------------------------------------------------------- the payloads

def index_row(job: dict) -> dict:
    """One job as the grid, the filter and the search need it — and no more.

    This is the file every reader downloads, so it holds the prompt (the thing
    the founder searches by) and drops everything only a click needs. 424 KB for
    573 jobs, against 1.6 MB for the same jobs' full records.
    """
    img, vid = first_of(job, "image"), first_of(job, "video")
    row = {
        "id": job.get("id"),
        "beat": job.get("beat"),
        "kind": job.get("kind") or "other",
        "rc": 1 if job.get("rc") else 0,
        "finished": job.get("finished_at"),
        "duration_s": job.get("duration_s"),
        "files": len(job.get("outputs") or []),
    }
    if img:
        row["still"] = _rel(img["path"])
    if vid:
        row["clip"] = _rel(vid["path"])
    if job.get("prompt"):
        row["prompt"] = job["prompt"]
    else:
        # The gap and its reason travel with the row, so the page can print the
        # honest marker without a second fetch and without inventing a cause.
        row["prompt_gap"] = job.get("prompt_source") or "no reason recorded"
    return row


def detail_row(job: dict) -> dict:
    """Everything the opened record shows. Fetched on the first click, once."""
    out = {}
    for key in ("id", "beat", "kind", "rc", "failed_step", "attempts", "node",
                "runner_host", "started_at", "finished_at", "duration_s",
                "prompt", "negative", "prompt_source", "recipe", "spec_file",
                "sidecar", "artifacts_dir", "purpose_note"):
        val = job.get(key)
        if val not in (None, "", [], {}):
            out[key] = val
    init = job.get("init") or {}
    if init.get("path"):
        out["init"] = {"path": _rel(init["path"]),
                       "sha256": str(init.get("sha256") or "")[:12]}
    ref = job.get("reference") or {}
    if ref:
        keep = {k: v for k, v in ref.items() if v not in (None, "", [], {})}
        if keep.get("path"):
            keep["path"] = _rel(keep["path"])
        out["reference"] = keep
    outs = []
    for art in job.get("outputs") or []:
        if not isinstance(art, dict) or not art.get("path"):
            continue
        outs.append({"path": _rel(art["path"]), "bytes": art.get("bytes"),
                     "kind": art.get("kind")})
    if outs:
        out["outputs"] = outs
    purpose = job.get("purpose") or {}
    keep = {k: v for k, v in purpose.items()
            if k in ("consumer", "why", "success", "owner") and v}
    if keep:
        out["purpose"] = keep
    verdict = {k: v for k, v in (job.get("verdict") or {}).items() if v}
    if verdict:
        out["verdict"] = verdict
    return out


def sorted_jobs(data: dict | None) -> list:
    """Newest finished first — the one order the whole page agrees on. The
    baked cards' `data-i`, the index array and the arrow keys all count in it,
    so it is computed here once and never re-derived."""
    if not data or not isinstance(data.get("jobs"), list):
        return []
    jobs = [j for j in data["jobs"] if isinstance(j, dict)]
    jobs.sort(key=lambda j: str(j.get("finished_at") or ""), reverse=True)
    return jobs


def index_payload(data: dict | None) -> dict:
    jobs = sorted_jobs(data)
    upcoming = [u for u in ((data or {}).get("upcoming") or []) if isinstance(u, dict)]
    return {"_meta": (data or {}).get("_meta") or {},
            "results_base": RESULTS_BASE,
            "thumb_base": THUMB_BASE,
            "jobs": [index_row(j) for j in jobs],
            "upcoming": upcoming}


def detail_payload(data: dict | None) -> dict:
    out = {}
    for job in sorted_jobs(data):
        jid = job.get("id")
        if jid:
            out[str(jid)] = detail_row(job)
    return {"jobs": out}


# ---------------------------------------------------------------- the page

def render(data: dict | None, now: datetime.datetime = None) -> str:
    """The whole body, from the parsed history file. Pure — no clock but the one
    handed in, no disk except the committed specs' `success:` lines."""
    if not data or not isinstance(data.get("jobs"), list):
        return (
            '<p class="eyebrow">the queue</p>'
            '<h1>The queue</h1>'
            '<p class="notice">This build could not read '
            '<code>pipeline/measured/queue-history.json</code>, so it is not '
            'showing a history. That file is written by '
            '<code>python3 pipeline/queue_history.py</code> and committed; the '
            'page is empty rather than inventing one.</p>')

    meta = data.get("_meta") or {}
    jobs = sorted_jobs(data)
    upcoming = [u for u in (data.get("upcoming") or []) if isinstance(u, dict)]

    ok = sum(1 for j in jobs if not j.get("rc"))
    bad = len(jobs) - ok
    held = sum(1 for u in upcoming if u.get("state") == "held")
    runnable = sum(1 for u in upcoming if u.get("state") == "authored")
    files = sum(len(j.get("outputs") or []) for j in jobs)
    machine_h = sum(int(j.get("duration_s") or 0) for j in jobs) / 3600.0
    kinds = sorted({str(j.get("kind") or "other") for j in jobs})

    # "find one beat's history quickly" is the founder's own use of this page, and
    # 21 beats will not fit the bar as chips on a phone. A native <select> is one
    # control tall, opens as the platform's own picker, and carries the count so
    # the choice is informed before it is made.
    beat_counts: dict = {}
    for j in jobs:
        b = j.get("beat")
        if isinstance(b, int):
            beat_counts[b] = beat_counts.get(b, 0) + 1
    beatless = sum(1 for j in jobs if not isinstance(j.get("beat"), int))

    days: dict = {}
    for job in jobs:
        days.setdefault(day_key(job.get("finished_at")), []).append(job)
    ordered = sorted((k for k in days if k != "undated"), reverse=True)
    if "undated" in days:
        ordered.append("undated")

    measured = meta.get("measured_at") or "unknown"
    src_commit = str(meta.get("source_commit") or "")[:9]
    fresh = freshness_html(jobs, now)

    stats = (
        '<ul class="qstats">'
        f'<li class="work"><b>{len(jobs)}</b><span>renders finished</span></li>'
        f'<li class="work"><b>{files}</b><span>files they produced</span></li>'
        f'<li class="work"><b>{machine_h:.1f} h</b><span>of measured machine time</span></li>'
        f'<li class="bad"><b>{bad}</b><span>failed</span></li>'
        f'<li class="wait"><b>{held}</b><span>held on the author</span></li>'
        f'<li class="work"><b>{runnable}</b><span>authored, not yet run</span></li>'
        '</ul>')

    live = (
        '<h2 id="now">On the render box right now</h2>'
        '<div class="qlive" id="q-live">'
        '<p class="qsay none" id="q-live-say">Reading the box\'s own telemetry '
        'publish&hellip; this line is filled in by your browser, straight off the '
        'box\'s branch. With JavaScript off there is nothing live to show and this '
        'page says so rather than printing a number from build time.</p>'
        '<div class="qchips" id="q-live-chips"></div>'
        '<div id="q-live-now"></div>'
        '</div>'
        '<p class="qmeta">The box publishes HOW MANY jobs are waiting and of what '
        'kind — never their names (<code>pipeline/telemetry.py</code>). So the named '
        'list below is the committed specs with no run record: what is authored, and '
        'what is held. When the box names the job it is running, its spec is matched '
        'by id and opened here.</p>')

    up_cards = "".join(upcoming_card(u, spec_success(u.get("spec_file")))
                       for u in upcoming)
    up_section = (
        f'<h2 id="upcoming">Coming — {len(upcoming)} job'
        f'{"" if len(upcoming) == 1 else "s"} written and not yet run</h2>'
        f'<p class="qlede">Every one of these is a committed spec in '
        f'<code>pipeline/jobs/</code> that no run record anywhere accounts for. '
        f'<b>Amber is waiting on you</b> — a held job is held by a question only '
        f'the author can answer, and the machine cannot start it. Green is runnable.</p>'
        # MEASURED 2026-08-15, at 390 px: these cards ran 34,500 px tall and put
        # the first finished render 43 SCREENS down. He reviews on a phone and
        # the gallery is what he asked this page for, so an unrun job list must
        # not be a wall in front of it. `open` in the markup, closed by the
        # script only on a narrow viewport: with JavaScript off nothing is
        # folded, and the count is in the summary either way, so this hides no
        # fact — it just stops one section from burying the other.
        + (f'<details class="qupwrap" id="q-up" open>'
           f'<summary>{len(upcoming)} job'
           f'{"" if len(upcoming) == 1 else "s"} authored and not yet run'
           + (f' — {held} held on you, {runnable} runnable' if upcoming else "")
           + f'</summary><div class="qupgrid">{up_cards}</div></details>'
           if up_cards else
           '<p class="notice">Nothing is authored and unrun: every committed spec '
           'has a run record.</p>'))

    kind_btns = "".join(
        f'<button type="button" class="qbtn" data-f="kind" data-v="{_e(k)}" '
        f'aria-pressed="false">{_e(kind_word(k))}</button>' for k in kinds)
    beat_opts = "".join(
        f'<option value="{b}">beat {b:02d} — {beat_counts[b]} '
        f'render{"" if beat_counts[b] == 1 else "s"}</option>'
        for b in sorted(beat_counts))
    if beatless:
        beat_opts += (f'<option value="none">no beat recorded — {beatless} '
                      f'render{"" if beatless == 1 else "s"}</option>')
    bar = (
        '<div class="qbar" id="q-bar">'
        '<label class="qhide" for="q-q">Search the prompts</label>'
        '<input id="q-q" type="search" inputmode="search" autocomplete="off" '
        'placeholder="a beat number, a word from a prompt, a model, a job id">'
        '<label class="qhide" for="q-beat">Filter by beat</label>'
        f'<select id="q-beat"><option value="">all {len(beat_counts)} beats</option>'
        f'{beat_opts}</select>'
        '<div class="qset" role="group" aria-label="filter by kind">'
        '<button type="button" class="qbtn" data-f="kind" data-v="" '
        'aria-pressed="true">all kinds</button>'
        f'{kind_btns}</div>'
        '<div class="qset" role="group" aria-label="filter by outcome">'
        '<button type="button" class="qbtn" data-f="rc" data-v="" '
        'aria-pressed="true">any outcome</button>'
        '<button type="button" class="qbtn" data-f="rc" data-v="0" '
        'aria-pressed="false">ran clean</button>'
        '<button type="button" class="qbtn bad" data-f="rc" data-v="1" '
        f'aria-pressed="false">failed</button></div>'
        f'<p class="qcount" id="q-count">{len(jobs)} renders</p></div>')

    gallery, start = [], 0
    for key in ordered:
        gallery.append(day_section(key, days[key], start))
        start += len(days[key])

    return f"""
<p class="eyebrow">the queue</p>
<h1>The queue — every render, and what made it</h1>
<p class="lede qlede">Every finished render the farm has produced, newest first.
Tap any frame for the record behind it: the exact positive and negative prompt, the
image it started from, the reference it was conditioned on, the recipe, and every
file it wrote.</p>
<nav class="qjump" aria-label="jump to a section">
<a href="#finished">{len(jobs)} finished renders &#8595;</a>
<a href="#upcoming">{len(upcoming)} coming &#8595;</a>
<a href="#now">what the box is doing &#8595;</a></nav>
<p class="qprov">History measured <b>{_e(measured)}</b> from
<code>{_e(RESULTS_BRANCH)}</code> at <code>{_e(src_commit)}</code> ·
{len(jobs)} renders · written by <code>pipeline/queue_history.py</code> and committed,
so this page is exactly as fresh as that file and no fresher. The block below it is
live.</p>
{fresh}
{stats}
{live}
{up_section}
<h2 id="finished">Finished — newest day first</h2>
{fresh}
<p class="qlede">Grouped by the day each render finished, on a {TZ_LABEL} clock.
Thumbnails are 512&nbsp;px previews from the <code>{THUMB_BRANCH}</code> branch; the
full-resolution frame is in the record and on the results branch.</p>
{bar}
{"".join(gallery)}
<p class="qnote" id="q-empty" hidden>Nothing matches that filter.</p>
<h2>What this page can and cannot know</h2>
<p class="qprov">
<b>Clocks are {TZ_LABEL}.</b> The record underneath is UTC; every face here is
converted once, at build.<br>
<b>A prompt this page cannot show, it names.</b> {NO_PROMPT} is printed with the
reason — for a motion job whose spec was deleted, or a render from before the box
wrote artifact sidecars, the bytes are genuinely gone. They are never reconstructed:
the 77-token fit happened on the box's tokenizer and a recomputation can differ
exactly where it would matter.<br>
<b>{NO_ARTIFACT}</b> on a tile means exactly that and nothing more: the history file
lists no output for that run. This page never reads the results branch to check —
it cannot, it is built once and the branch moves — so it does not claim the frame
is missing, only that the record does not name one. Some of these ran clean and
their frames ARE on <code>{_e(RESULTS_BRANCH)}</code> under a directory named after
the job; the history simply never linked them. That is a gap in
<code>pipeline/queue_history.py</code>, which is where it has to be fixed, and it is
left visible here rather than papered over with a guessed path — a tile showing a
frame this page inferred rather than read would be the one lie that makes every
other frame on it worthless.<br>
<b>Nothing here was copied into the site.</b> Frames and clips are served from
<code>{_e(RESULTS_BRANCH)}</code> and their previews from
<code>{THUMB_BRANCH}</code>, both on GitHub's raw CDN, lazily.<br>
<b>Finished is not approved.</b> rc 0 means the box ran the job, and nothing more.
Whether a frame is any good is the author's call and it lives on
<a href="review">the review board</a>.<br>
<b>{bad} of {len(jobs)} runs failed</b> and they are here with the rest, red, with
the step they died at. A queue history that showed only the successes would be an
advertisement.<br>
<b>The full record is <a href="{DATA_FILE}">{DATA_FILE}</a> and
<a href="{DETAIL_FILE}">{DETAIL_FILE}</a></b> — the same bytes this page reads, if
you would rather grep than scroll.</p>
<div class="qbox" id="q-box" hidden>
  <div class="qbox-in" role="dialog" aria-modal="true" aria-labelledby="q-box-who">
    <div class="qbox-bar">
      <span class="who" id="q-box-who">Render</span>
      <span class="qset">
        <button type="button" class="qbtn" id="q-prev">&#8592; newer</button>
        <button type="button" class="qbtn" id="q-next">older &#8594;</button>
        <button type="button" class="qbtn" id="q-close">close</button>
      </span>
    </div>
    <div class="qbox-body" id="q-box-body"></div>
  </div>
</div>
<div class="qlens" id="q-lens" hidden>
  <div class="qlens-bar">
    <span class="cap" id="q-lens-cap"></span>
    <span class="qset">
      <a class="qbtn" id="q-lens-raw" href="#">open the file</a>
      <button type="button" class="qbtn" id="q-lens-close">close</button>
    </span>
  </div>
  <div class="qlens-fig" id="q-lens-fig"></div>
</div>
"""


# Plain string, not an f-string: JavaScript, full of braces. The URLs, the
# staleness rule and the two data files are substituted by build().
LIVE_JS = """
/* ---- what the box is doing, read by the reader's own browser ----------------
   The same source, the same cache-busting and the same staleness rule as the
   queue block on /status (build_sim.LIVE_JS.readBoxQueue): the telemetry branch
   first, the branch the daemon used to publish to as a fallback, `no-store`
   with a per-minute cache-buster, and a reading older than three publishes is
   a record rather than a claim about now.

   THE BOX NAMES ONE JOB AND COUNTS THE REST. `queue_sample` publishes counts,
   a kind mix, and — when it has one — the running job's own record, never the
   names of the jobs waiting. So this block reports exactly that, and where the
   running job's id matches a spec baked into this page it opens the spec's
   consumer / success / why underneath. A page that listed names the box never
   published would be inventing the most checkable thing on it. */
(function () {
  var say = document.getElementById("q-live-say");
  var chips = document.getElementById("q-live-chips");
  var nowEl = document.getElementById("q-live-now");
  if (!say || !window.fetch) return;                 /* no JS, no claim */

  function bust() { return Math.floor(Date.now() / 60000); }
  function words(sec) {
    if (sec < 90) return "just now";
    if (sec < 5400) return Math.floor(sec / 60) + " min ago";
    if (sec < 129600) return Math.floor(sec / 3600) + " h ago";
    var d = Math.floor(sec / 86400);
    return d + (d === 1 ? " day ago" : " days ago");
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined && text !== null) e.textContent = text;
    return e;
  }
  function clear(e) { while (e && e.firstChild) e.removeChild(e.firstChild); }
  function chip(cls, text) { chips.appendChild(el("span", "qchip " + cls, text)); }
  function line(parent, head, body) {
    parent.appendChild(el("p", "qh", head));
    parent.appendChild(el("p", "qmeta", body));
  }

  function drawNow(q) {
    clear(nowEl);
    if (!q.running) {
      nowEl.appendChild(el("p", "qsay none",
        "Nothing is rendering on the card at that reading."));
      return;
    }
    var cur = q.current || {};
    var id = cur.task || q.running_job || null;
    if (!id) {
      nowEl.appendChild(el("p", "qsay",
        "A job is rendering, but the box's report does not say which, so this " +
        "page will not name one."));
      return;
    }
    var head = "Rendering now";
    if (cur.beat || cur.beat === 0) head += " \\u2014 beat " + cur.beat;
    if (cur.kind) head += " \\u00b7 " + cur.kind;
    if (cur.attempt) head += " \\u00b7 attempt " + cur.attempt;
    nowEl.appendChild(el("p", "qnow-t", head));
    var meta = ["job " + id];
    if (cur.node) meta.push("node " + cur.node);
    if (cur.started_at) {
      meta.push("started " +
        words(Math.max(0, Math.round(Date.now() / 1000 - cur.started_at))));
    }
    nowEl.appendChild(el("p", "qmeta", meta.join(" \\u00b7 ")));
    if (cur.makes && cur.makes.length) {
      line(nowEl, "What it will make", cur.makes.join(", "));
    }
    /* The frame it is animating, if the box named one. Straight off the results
       branch, same as every other picture here. */
    if (cur.init) {
      var fig = el("figure", "qside");
      var im = document.createElement("img");
      im.loading = "lazy"; im.alt = "the frame the running job started from";
      im.src = RESULTS_BASE + "/" + String(cur.init).replace(/^\\/+/, "");
      im.style.maxWidth = "260px";
      fig.appendChild(im);
      nowEl.appendChild(el("p", "qh", "The frame it is working from"));
      nowEl.appendChild(fig);
    }
    var spec = SPECS[id];
    if (spec) {
      if (spec.consumer) line(nowEl, "Consumer \\u2014 who is waiting for it", spec.consumer);
      if (spec.success) line(nowEl, "What would count as success", spec.success);
      if (spec.why) line(nowEl, "Why", spec.why);
    } else {
      nowEl.appendChild(el("p", "qmeta",
        "No committed spec by that id is baked into this page \\u2014 it was " +
        "enqueued after the history file was last written."));
    }
  }

  function grab(u) {
    return fetch(u + "?_=" + bust(), {cache: "no-store"})
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); });
  }

  function read() {
    grab(TEL_URL)
      .catch(function () { return grab(TEL_URL_LEGACY); })
      .then(function (d) {
        var q = d && d.queue;
        clear(chips);
        if (!q) throw new Error("the box is publishing vitals but not its queue");
        if (q.error) throw new Error("the box could not read its own queue: " + q.error);
        var age = Math.max(0, Math.round(Date.now() / 1000 - q.at));
        var fresh = age <= STALE_MIN * 60;
        var running = q.running || 0, ready = q.ready || 0;
        chip("work", running + " rendering");
        chip(ready ? "work" : "", ready + " waiting on the card");
        /* RED ONLY FOR WHAT IS ACTUALLY NEW. ACK_FAILED is how many of the
           box's failures are triaged in the repo; anything above that line is
           unexamined and is what the founder needs to see. */
        if (q.failed) {
          var fresh = q.failed - ACK_FAILED;
          if (ACK_FAILED <= 0 || fresh > 0) {
            chip("bad", fresh > 0 && ACK_FAILED > 0
              ? q.failed + " sitting failed \\u2014 " + fresh + " not yet triaged"
              : q.failed + " sitting failed");
          } else {
            chip("", q.failed + " failed, all triaged \\u2014 " + ACK_DOC);
          }
        }
        if (typeof q.done_24h === "number") chip("", q.done_24h + " finished in 24 h");
        if (q.runner_alive === false) chip("bad", "nothing is draining this queue");
        if (q.kinds) {
          var ks = [];
          for (var k in q.kinds) {
            if (Object.prototype.hasOwnProperty.call(q.kinds, k)) {
              ks.push(q.kinds[k] + " " + k);
            }
          }
          if (ks.length) chip("", ks.join(" \\u00b7 "));
        }
        say.className = "qsay";
        say.textContent = fresh
          ? "Measured " + words(age) + " by the box itself."
          : "Measured " + words(age) + " \\u2014 the box has stopped publishing, " +
            "so this is the last reading, not a current one.";
        drawNow(q);
      })
      .catch(function (e) {
        say.className = "qsay none";
        say.textContent = "The live reading is unavailable: " + e.message +
          ". Nothing else on this page depends on it \\u2014 the gallery below is " +
          "baked into these bytes.";
        clear(nowEl);
      });
  }
  read();
  /* five minutes: the fastest anything upstream is written. */
  setInterval(function () { if (!document.hidden) read(); }, 300000);
})();


/* ---- the gallery: filtering, and the record behind a card -------------------
   The cards are already in the HTML — they render, and they are legible, with
   this file blocked. What JavaScript adds is the two things markup cannot do
   for 573 renders: search across prompts that are not all in the page, and open
   one render's full record without shipping all 573 of them.

   INDEX (queue-data.json) is the search corpus and arrives first. DETAIL
   (queue-detail.json) is 1.6 MB and is fetched on the first card anyone opens,
   once. Both failures are stated on the page rather than swallowed: a filter
   that silently matched nothing, or a record that silently showed half of
   itself, is exactly the kind of quiet wrong this page exists to end. */
(function () {
  var bar = document.getElementById("q-bar");
  var input = document.getElementById("q-q");
  var count = document.getElementById("q-count");
  var empty = document.getElementById("q-empty");
  var box = document.getElementById("q-box");
  var body = document.getElementById("q-box-body");
  var who = document.getElementById("q-box-who");
  if (!bar || !box) return;

  var cards = [].slice.call(document.querySelectorAll(".qc"));
  var sections = [].slice.call(document.querySelectorAll(".qdaysec"));
  var INDEX = null, DETAIL = null, detailWanted = false, detailError = null;
  var open = -1;
  var state = {q: "", kind: "", rc: "", beat: ""};
  var beatSel = document.getElementById("q-beat");

  /* The day headers stick under the control bar, and the bar's height changes
     with the viewport (it wraps to three rows on a phone). Measured rather than
     guessed: a guessed offset puts a header behind the bar on exactly the
     screen size nobody tested. */
  function measure() {
    document.documentElement.style.setProperty(
      "--qbarh", bar.getBoundingClientRect().height + "px");
  }
  measure();
  window.addEventListener("resize", measure);

  function esc(s) { return String(s === undefined || s === null ? "" : s); }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined && text !== null) e.textContent = text;
    return e;
  }
  function clear(e) { while (e && e.firstChild) e.removeChild(e.firstChild); }
  function artUrl(p) { return RESULTS_BASE + "/" + esc(p).replace(/^\\/+/, ""); }
  function thumbUrl(p) {
    var r = esc(p).replace(/^\\/+/, "");
    return THUMB_BASE + "/" + r.replace(/\\.[^./]+$/, "") + ".jpg";
  }
  function dur(s) {
    if (typeof s !== "number" || s < 0) return "\\u2014";
    if (s < 60) return s + "s";
    var m = Math.floor(s / 60), r = s % 60;
    if (m < 60) return m + "m " + (r < 10 ? "0" : "") + r + "s";
    return Math.floor(m / 60) + "h " + (m % 60) + "m";
  }
  function stamp(iso) {
    if (!iso) return "\\u2014";
    var d = new Date(String(iso).replace(" ", "T"));
    if (isNaN(d.getTime())) return String(iso);
    var s = new Date(d.getTime() + 4 * 3600 * 1000);   /* +04, like every clock here */
    return s.toISOString().slice(0, 16).replace("T", " ") + " " + TZ_LABEL;
  }

  /* ------------------------------------------------------------------ lens
     Full-resolution bytes over the record, rather than a link out to the raw
     CDN. Every picture in the record is a 512 px preview or a fitted copy, so
     "is that the fig or a smear" was a question the page could not answer
     without leaving itself — on a phone, a one-way trip that loses the scroll
     position and every filter set to get there. */
  var lens = document.getElementById("q-lens");
  var lensFig = document.getElementById("q-lens-fig");
  var lensCap = document.getElementById("q-lens-cap");
  var lensRaw = document.getElementById("q-lens-raw");
  var lensBack = null;

  function openLens(path, kind) {
    if (!lens || !path) return;
    var url = artUrl(path);
    clear(lensFig);
    var node;
    if (kind === "video") {
      node = document.createElement("video");
      node.controls = true; node.playsInline = true; node.preload = "metadata";
    } else {
      node = document.createElement("img");
      node.decoding = "async"; node.alt = path.split("/").pop();
    }
    node.src = url;
    lensFig.appendChild(node);
    /* The whole path, not the filename: ten beats ship a clip called
       13-remake-LTX-0813.mp4, so the directory is the only thing that says
       which render this is. */
    lensCap.textContent = path;
    lensRaw.href = url;
    lensBack = document.activeElement;
    lens.hidden = false;
    document.body.style.overflow = "hidden";
    document.getElementById("q-lens-close").focus();
  }
  function closeLens() {
    if (!lens || lens.hidden) return;
    lens.hidden = true;
    clear(lensFig);                       /* stops a clip that was playing */
    if (!box || box.hidden) document.body.style.overflow = "";
    if (lensBack && lensBack.focus) lensBack.focus();
    lensBack = null;
  }
  /* Any picture in the record becomes its own full-size view. The click is
     stopped here so it never also reaches the card underneath. */
  function zoomable(node, path, kind) {
    node.classList.add("qzoom");
    node.addEventListener("click", function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      openLens(path, kind);
    });
    return node;
  }
  if (lens) {
    document.getElementById("q-lens-close").addEventListener("click", closeLens);
    lens.addEventListener("click", function (ev) {
      if (ev.target === lens || ev.target === lensFig) closeLens();
    });
  }

  /* ---------------------------------------------------------------- filter */
  function matches(i) {
    var row = INDEX ? INDEX[i] : null;
    var card = cards[i];
    if (state.kind && card.getAttribute("data-k") !== state.kind) return false;
    if (state.rc !== "" && card.getAttribute("data-r") !== state.rc) return false;
    if (state.beat !== "") {
      var cb = card.getAttribute("data-b");
      /* "none" is its own answer, not a missing one: a run whose beat nobody
         recorded is a fact this page keeps rather than filing under beat 0. */
      if (state.beat === "none") { if (cb !== "") return false; }
      else if (cb === "" || parseInt(cb, 10) !== parseInt(state.beat, 10)) return false;
    }
    if (!state.q) return true;
    var beatOnly = /^b?(\\d{1,3})$/.exec(state.q);
    if (beatOnly) {
      var b = card.getAttribute("data-b");
      if (b !== "" && String(parseInt(b, 10)) === String(parseInt(beatOnly[1], 10))) {
        return true;
      }
    }
    var hay = row
      ? [row.id, row.kind, row.prompt, row.prompt_gap, row.still, row.clip].join(" ")
      : card.textContent;
    return hay.toLowerCase().indexOf(state.q) !== -1;
  }

  function apply() {
    var shown = 0;
    for (var i = 0; i < cards.length; i++) {
      var hit = matches(i);
      cards[i].classList.toggle("qhide", !hit);
      if (hit) shown++;
    }
    for (var s = 0; s < sections.length; s++) {
      sections[s].classList.toggle(
        "qhide", !sections[s].querySelector(".qc:not(.qhide)"));
    }
    empty.hidden = shown !== 0;
    var filtered = state.q || state.kind || state.rc !== "" || state.beat !== "";
    count.textContent = filtered
      ? shown + " of " + cards.length + " renders match"
        + (INDEX ? "" : " \\u2014 searching card text only, the prompt index has not loaded")
      : cards.length + " renders";
  }

  input.addEventListener("input", function () {
    state.q = input.value.trim().toLowerCase();
    apply();
  });
  /* The unrun list is 54 cards and, at 390 px, 34,500 px of them — 43 screens
     between the top of the page and the first finished render. It ships open so
     a reader with no JavaScript loses nothing; here, and only on a viewport too
     narrow to afford it, it starts folded. Anyone who asks for it — by tapping
     the summary, by following the jump link, by arriving on #upcoming — gets it
     back, and the summary states the count while folded. */
  var upBox = document.getElementById("q-up");
  if (upBox && window.innerWidth < 760 && location.hash !== "#upcoming") {
    upBox.open = false;
  }
  function openUpcoming() { if (upBox) upBox.open = true; }
  window.addEventListener("hashchange", function () {
    if (location.hash === "#upcoming") openUpcoming();
  });
  var upJump = document.querySelector('.qjump a[href="#upcoming"]');
  if (upJump) upJump.addEventListener("click", openUpcoming);

  if (beatSel) {
    beatSel.addEventListener("change", function () {
      state.beat = beatSel.value;
      beatSel.classList.toggle("on", state.beat !== "");
      apply();
    });
  }
  bar.addEventListener("click", function (ev) {
    var btn = ev.target.closest ? ev.target.closest(".qbtn[data-f]") : null;
    if (!btn) return;
    var f = btn.getAttribute("data-f");
    state[f] = btn.getAttribute("data-v");
    var group = btn.parentNode.querySelectorAll(".qbtn[data-f=" + f + "]");
    for (var i = 0; i < group.length; i++) {
      group[i].setAttribute("aria-pressed",
        group[i].getAttribute("data-v") === state[f] ? "true" : "false");
    }
    apply();
  });

  /* ---------------------------------------------------------------- record */
  function mediaBlock(row, det) {
    var wrap = el("div", "qmedia");
    var main = el("div", "qbig");
    var outs = (det && det.outputs) || [];
    var vids = outs.filter(function (o) { return o.kind === "video"; });
    var imgs = outs.filter(function (o) { return o.kind === "image"; });

    function show(art) {
      clear(main);
      if (!art) {
        main.appendChild(el("p", "qgap", NO_ARTIFACT));
        return;
      }
      var node;
      if (art.kind === "video") {
        node = document.createElement("video");
        node.controls = true; node.playsInline = true; node.preload = "metadata";
        node.src = artUrl(art.path);
        if (imgs.length) node.poster = thumbUrl(imgs[0].path);
      } else {
        node = document.createElement("img");
        node.loading = "lazy"; node.decoding = "async"; node.alt = "";
        node.src = artUrl(art.path);
        zoomable(node, art.path, art.kind);
      }
      main.appendChild(node);
      var cap = el("p", "qmeta", art.path.split("/").pop()
        + (typeof art.bytes === "number" ? " \\u00b7 " + Math.round(art.bytes / 1024) + " KB" : ""));
      var a = document.createElement("a");
      a.href = artUrl(art.path); a.textContent = "open the file";
      cap.appendChild(document.createTextNode(" \\u00b7 "));
      cap.appendChild(a);
      main.appendChild(cap);
    }

    show(vids[0] || imgs[0] || null);
    wrap.appendChild(main);

    if (outs.length > 1) {
      var strip = el("div", "qstrip");
      outs.forEach(function (art) {
        var t = document.createElement("img");
        t.loading = "lazy"; t.alt = art.path.split("/").pop();
        t.title = t.alt;
        t.src = art.kind === "video" && imgs.length
          ? thumbUrl(imgs[0].path) : thumbUrl(art.path);
        t.onerror = function () { t.onerror = null; t.src = artUrl(art.path); };
        t.addEventListener("click", function () {
          show(art);
          [].forEach.call(strip.children, function (c) { c.removeAttribute("aria-current"); });
          t.setAttribute("aria-current", "true");
        });
        strip.appendChild(t);
      });
      main.appendChild(el("p", "qh", "Every file this render wrote \\u2014 "
        + outs.length + ", tap to enlarge"));
      main.appendChild(strip);
    }

    /* The inputs, beside the output: the whole reason he asked for the page is
       to see what went in next to what came out. */
    var side = el("div", "qside");
    var any = false;
    if (det && det.init && det.init.path) {
      any = true;
      side.appendChild(el("p", "qh", "Init frame \\u2014 what it started from"));
      var fig = document.createElement("figure");
      var im = document.createElement("img");
      im.loading = "lazy"; im.alt = "init frame"; im.src = thumbUrl(det.init.path);
      im.onerror = function () { im.onerror = null; im.src = artUrl(det.init.path); };
      zoomable(im, det.init.path, "image");
      var a = document.createElement("a");
      a.href = artUrl(det.init.path); a.appendChild(im);
      fig.appendChild(a);
      side.appendChild(fig);
      side.appendChild(el("p", "qmeta", det.init.path.split("/").pop()
        + (det.init.sha256 ? " \\u00b7 sha " + det.init.sha256 : "")));
    }
    var ref = det && det.reference;
    if (ref) {
      any = true;
      side.appendChild(el("p", "qh", "Reference image (IP-Adapter)"));
      if (ref.path) {
        var rfig = document.createElement("figure");
        var rim = document.createElement("img");
        rim.loading = "lazy"; rim.alt = "reference image"; rim.src = thumbUrl(ref.path);
        rim.onerror = function () { rim.onerror = null; rim.src = artUrl(ref.path); };
        zoomable(rim, ref.path, "image");
        var ra = document.createElement("a");
        ra.href = artUrl(ref.path); ra.appendChild(rim);
        rfig.appendChild(ra);
        side.appendChild(rfig);
      }
      var bits = [];
      if (ref.name) bits.push(ref.name);
      if (ref.scale !== undefined) bits.push("scale " + ref.scale);
      if (ref.sha256) bits.push("sha " + String(ref.sha256).slice(0, 12));
      if (bits.length) side.appendChild(el("p", "qmeta", bits.join(" \\u00b7 ")));
      if (!ref.path) {
        side.appendChild(el("p", "qmeta",
          "The reference bytes live on the box only \\u2014 the sha above is what " +
          "was recorded, and there is no URL to show. Not an error, and not a " +
          "picture this page can produce."));
      }
      if (ref.step_window) side.appendChild(el("p", "qmeta", ref.step_window));
      if (ref.note) side.appendChild(el("p", "qmeta", ref.note));
    }
    if (!any) {
      side.appendChild(el("p", "qh", "What went in"));
      side.appendChild(el("p", "qmeta",
        "No init frame and no reference image were recorded for this run \\u2014 it "
        + "was generated from the prompt alone, or from a record that predates the "
        + "box writing those fields."));
    }
    wrap.appendChild(side);
    return wrap;
  }

  function promptBlock(row, det) {
    var frag = document.createDocumentFragment();
    var pos = (det && det.prompt) || row.prompt;
    if (pos) {
      frag.appendChild(el("p", "qh", "Positive prompt"));
      frag.appendChild(el("p", "qprose", pos));
    } else {
      frag.appendChild(el("p", "qh", "Prompt"));
      var gap = el("p", "qgap", NO_PROMPT + " ");
      gap.appendChild(el("i", null, "\\u2014 " + (row.prompt_gap ||
        (det && det.prompt_source) || "no reason recorded")));
      frag.appendChild(gap);
    }
    var neg = det && det.negative;
    if (neg) {
      frag.appendChild(el("p", "qh", "Negative prompt"));
      frag.appendChild(el("p", "qprose neg", neg));
    } else if (pos) {
      frag.appendChild(el("p", "qh", "Negative prompt"));
      frag.appendChild(el("p", "qgap", NO_NEGATIVE));
    }
    var src = det && det.prompt_source;
    if (pos && src) frag.appendChild(el("p", "qmeta", "read from: " + src));
    return frag;
  }

  var RECIPE_ORDER = ["model", "size", "steps", "guidance", "scheduler", "lora",
    "frames", "fps", "seed", "seeds", "render_seconds", "extra_negative_tier",
    "negative_terms_removed"];

  function recipeBlock(det) {
    var frag = document.createDocumentFragment();
    var r = det && det.recipe;
    frag.appendChild(el("p", "qh", "Recipe"));
    if (!r) {
      var g = el("p", "qgap", "RECIPE NOT RECORDED ");
      g.appendChild(el("i", null,
        "\\u2014 no artifact sidecar carried the settings for this run"));
      frag.appendChild(g);
      return frag;
    }
    var keys = RECIPE_ORDER.filter(function (k) { return r[k] !== undefined; });
    Object.keys(r).sort().forEach(function (k) {
      if (RECIPE_ORDER.indexOf(k) === -1) keys.push(k);
    });
    var p = el("p", "qmeta");
    keys.forEach(function (k, n) {
      if (n) p.appendChild(document.createTextNode(" \\u00b7 "));
      p.appendChild(el("b", null, k));
      p.appendChild(document.createTextNode(" " + (Array.isArray(r[k])
        ? r[k].slice(0, 8).join(", ") : r[k])));
    });
    frag.appendChild(p);
    return frag;
  }

  function draw() {
    var row = INDEX ? INDEX[open] : null;
    var card = cards[open];
    if (!row) {
      /* The index has not arrived, so the record is drawn from what the card
         itself carries rather than from nothing. */
      row = {id: card.getAttribute("data-i"), beat: card.getAttribute("data-b"),
             kind: card.getAttribute("data-k"), rc: +card.getAttribute("data-r")};
    }
    var det = DETAIL ? DETAIL[row.id] : null;
    clear(body);
    who.textContent = (row.beat === null || row.beat === "" || row.beat === undefined
      ? "No beat" : "Beat " + row.beat) + " \\u00b7 " + (KINDS[row.kind] || row.kind);

    var top = el("p", "qmeta");
    top.appendChild(el("span", row.rc ? "rc-bad" : "rc-ok",
      row.rc ? "FAILED" + (det && det.failed_step ? " at " + det.failed_step : "")
             : "ran clean (rc 0)"));
    top.appendChild(document.createTextNode(" \\u00b7 finished " + stamp(row.finished)
      + " \\u00b7 took " + dur(row.duration_s)
      + " \\u00b7 " + row.files + (row.files === 1 ? " file" : " files")));
    body.appendChild(top);

    body.appendChild(mediaBlock(row, det));
    body.appendChild(promptBlock(row, det));
    body.appendChild(recipeBlock(det));

    if (det && det.purpose) {
      if (det.purpose.consumer) {
        body.appendChild(el("p", "qh", "Consumer \\u2014 who was waiting for this"));
        body.appendChild(el("p", "qmeta", det.purpose.consumer));
      }
      if (det.purpose.why) {
        body.appendChild(el("p", "qh", "Why it was run"));
        body.appendChild(el("p", "qmeta", det.purpose.why));
      }
      if (det.purpose.success) {
        body.appendChild(el("p", "qh", "What would count as success"));
        body.appendChild(el("p", "qmeta", det.purpose.success));
      }
    }
    if (det && det.verdict) {
      var v = [det.verdict.beat_state, det.verdict.gate, det.verdict.beat_note]
        .filter(Boolean).join(" \\u00b7 ");
      if (v) {
        body.appendChild(el("p", "qh", "Where the beat stands"));
        body.appendChild(el("p", "qmeta", v));
      }
    }

    var ident = el("p", "qmeta");
    function bit(label, text) {
      if (!text) return;
      if (ident.firstChild) ident.appendChild(document.createTextNode(" \\u00b7 "));
      ident.appendChild(el("b", null, label));
      ident.appendChild(document.createTextNode(" " + text));
    }
    bit("job", row.id);
    if (det) { bit("node", det.node); bit("ran on", det.runner_host); }
    body.appendChild(ident);

    if (det) {
      var links = el("p", "qmeta");
      function link(href, text) {
        if (links.firstChild) links.appendChild(document.createTextNode(" \\u00b7 "));
        var a = document.createElement("a");
        a.href = href; a.textContent = text;
        links.appendChild(a);
      }
      if (det.spec_file) link(REPO_URL + "/blob/main/" + det.spec_file, "spec");
      if (det.artifacts_dir) {
        link(REPO_URL + "/tree/" + RESULTS_BRANCH + "/" + det.artifacts_dir, "artifacts");
      }
      if (det.sidecar) {
        link(REPO_URL + "/blob/" + RESULTS_BRANCH + "/" + det.sidecar, "run record");
      }
      if (links.firstChild) body.appendChild(links);
    } else {
      body.appendChild(el("p", "qmeta", detailError
        ? "The full record could not be loaded: " + detailError
          + ". What you see above is what the page itself carries."
        : "Loading the rest of this record\\u2026"));
    }
  }

  function needDetail() {
    if (DETAIL || detailWanted) return;
    detailWanted = true;
    fetch(DETAIL_URL)
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (d) { DETAIL = (d && d.jobs) || {}; if (open >= 0) draw(); })
      .catch(function (e) { detailError = e.message; if (open >= 0) draw(); });
  }

  function openAt(i) {
    if (i < 0 || i >= cards.length) return;
    open = i;
    box.hidden = false;
    document.body.style.overflow = "hidden";
    needDetail();
    draw();
    box.scrollTop = 0;
    document.getElementById("q-close").focus();
  }
  function close() {
    box.hidden = true;
    document.body.style.overflow = "";
    if (open >= 0 && cards[open]) cards[open].focus();
    open = -1;
  }
  function step(dir) {
    for (var i = open + dir; i >= 0 && i < cards.length; i += dir) {
      if (!cards[i].classList.contains("qhide")) { openAt(i); return; }
    }
  }

  cards.forEach(function (c, i) {
    c.addEventListener("click", function () { openAt(i); });
  });
  document.getElementById("q-close").addEventListener("click", close);
  document.getElementById("q-prev").addEventListener("click", function () { step(-1); });
  document.getElementById("q-next").addEventListener("click", function () { step(1); });
  box.addEventListener("click", function (ev) { if (ev.target === box) close(); });
  document.addEventListener("keydown", function (ev) {
    /* The lens sits above the record, so it takes Escape first — otherwise one
       key would shut both and lose his place in the grid. */
    if (lens && !lens.hidden) {
      if (ev.key === "Escape") { closeLens(); }
      return;
    }
    if (box.hidden) return;
    if (ev.key === "Escape") { close(); }
    else if (ev.key === "ArrowLeft") { step(-1); }
    else if (ev.key === "ArrowRight") { step(1); }
  });

  /* The index: the search corpus, and the record's first half. Small enough to
     fetch on load, and the page says so if it does not arrive. */
  fetch(DATA_URL)
    .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(function (d) {
      INDEX = (d && d.jobs) || null;
      if (INDEX && INDEX.length !== cards.length) {
        /* The cards and the index are the same list in the same order, built in
           one pass. If they ever disagree, say so rather than opening the wrong
           record for a card. */
        count.textContent = cards.length + " renders \\u00b7 the prompt index is out " +
          "of step with the gallery (" + INDEX.length + " rows), so search is off";
        INDEX = null;
        return;
      }
      if (open >= 0) draw();
    })
    .catch(function (e) {
      count.textContent = cards.length + " renders \\u00b7 prompt search unavailable: "
        + e.message;
    });
})();

/* ---- the feed's age, re-decided against the READER's clock -----------------
   The banner above the gallery is rendered at build time, and a build-time
   verdict rots exactly like the data it describes: a page built while the feed
   was fresh and opened three days later would print "4 hours ago" forever. So
   every .qfresh element carries the newest row's ISO stamp, and this re-reads
   it now. It can only ever make the page MORE cautious — the words come from
   the same threshold the builder used, and with JavaScript off the build-time
   sentence stands, which is why that one is written to be true on its own. */
(function () {
  var els = document.querySelectorAll(".qfresh[data-newest]");
  if (!els.length) return;
  function span(s) {
    s = Math.max(0, s);
    if (s < 5400) return Math.round(s / 60) + " minutes";
    if (s < 36 * 3600) {
      var h = s / 3600;
      return h < 2 ? "an hour" : Math.round(h) + " hours";
    }
    var d = s / 86400;
    return (d < 10 ? d.toFixed(1) : String(Math.round(d))) + " days";
  }
  function words(s) { return span(s) + " ago"; }
  for (var i = 0; i < els.length; i++) {
    var el = els[i];
    var iso = el.getAttribute("data-newest");
    if (!iso) continue;
    var t = Date.parse(iso);
    if (isNaN(t)) continue;
    var hrs = parseFloat(el.getAttribute("data-stale-h")) || 4;
    var age = (Date.now() - t) / 1000;
    var stale = age >= hrs * 3600;
    /* The age is its own element in both states, so the reader's clock can
       correct it without the script having to re-parse a sentence. It was a
       regex over the built text until 2026-08-21, and the regex stopped
       matching the moment the banner's wording changed — silently, leaving a
       build-time age on the page, which is the exact failure this block is
       here to prevent. */
    var ageEl = el.querySelector(".qage");
    if (ageEl) ageEl.textContent = stale && el.classList.contains("stale")
      ? span(age) : words(age);
    if (!stale) continue;                    /* build-time text already fits */
    if (el.classList.contains("stale")) continue;   /* already loud, age fixed */
    /* it was fresh when this page was built and it is not now */
    var when = new Date(t).toLocaleString();
    el.className = "qfresh stale";
    el.textContent = "";
    var b2 = document.createElement("b");
    b2.textContent = "THIS FEED HAS GONE STALE SINCE THIS PAGE WAS BUILT \\u2014 "
      + span(age) + " BEHIND. Renders continue on the box. Nothing newer than "
      + when + " is on it.";
    el.appendChild(b2);
    var fix = document.createElement("span");
    fix.className = "qfresh-fix";
    fix.textContent = "The render box publishes every finished job to "
      + RESULTS_BRANCH + " as it goes, so renders since then exist and are "
      + "simply not shown here. An empty top row on a stale feed is not an "
      + "idle card. Re-run pipeline/queue_history.py, commit, push.";
    el.appendChild(fix);
  }
})();
"""


def specs_js(upcoming: list) -> str:
    """The id → purpose map the live block matches a running job against.

    Only the specs with no run record: 50-odd rows, a few tens of KB. Every
    other spec in `pipeline/jobs/` has already finished, so it cannot be the
    job the box is running, and baking all 598 of them would be a third of a
    megabyte to answer a question that cannot be asked.
    """
    out = {}
    for row in upcoming:
        sid = row.get("id")
        if not sid:
            continue
        entry = {}
        if row.get("consumer"):
            entry["consumer"] = row["consumer"]
        if row.get("why_first"):
            entry["why"] = row["why_first"]
        success = spec_success(row.get("spec_file"))
        if success:
            entry["success"] = success[:600]
        if entry:
            out[str(sid)] = entry
    return json.dumps(out, ensure_ascii=False, separators=(",", ":"))


def build(out_dir: Path):
    from build_site import page          # late import: build_site calls us
    data = load()
    body = render(data)
    out_dir = Path(out_dir)
    upcoming = [u for u in ((data or {}).get("upcoming") or []) if isinstance(u, dict)]
    jobs = sorted_jobs(data)

    # The two payloads. Written whatever happened to the history: an empty pair
    # of files is a readable answer to "what does the page know", and a stale
    # pair left behind by an earlier build would be a lie.
    index = index_payload(data)
    detail = detail_payload(data)
    (out_dir / DATA_FILE).write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (out_dir / DETAIL_FILE).write_text(
        json.dumps(detail, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    consts = (f"var TEL_URL={json.dumps(TELEMETRY_URL)},"
              f"TEL_URL_LEGACY={json.dumps(TELEMETRY_URL_LEGACY)},"
              f"STALE_MIN={STALE_MINUTES},"
              f"ACK_FAILED={acknowledged_failures()},"
              f"ACK_DOC={json.dumps(ACK_DOC)},"
              f"RESULTS_BASE={json.dumps(RESULTS_BASE)},"
              f"RESULTS_BRANCH={json.dumps(RESULTS_BRANCH)},"
              f"THUMB_BASE={json.dumps(THUMB_BASE)},"
              f"REPO_URL={json.dumps(REPO_URL)},"
              f"TZ_LABEL={json.dumps(TZ_LABEL)},"
              f"DATA_URL={json.dumps(DATA_FILE)},"
              f"DETAIL_URL={json.dumps(DETAIL_FILE)},"
              f"NO_PROMPT={json.dumps(NO_PROMPT)},"
              f"NO_NEGATIVE={json.dumps(NO_NEGATIVE)},"
              f"NO_ARTIFACT={json.dumps(NO_ARTIFACT)},"
              f"KINDS={json.dumps(KIND_WORDS, ensure_ascii=False)},"
              f"SPECS={specs_js(upcoming)};")
    tail = "<script>" + consts + LIVE_JS + "</script>"
    out = out_dir / "queue.html"
    out.write_text(page(
        "The queue — every render, and what made it",
        f"<style>{CSS}</style>" + body,
        path="queue.html",
        desc="Every render the farm has produced as a browsable gallery — the "
             "frame, the prompt that made it, the reference it used and the recipe.",
        tail=tail,
    ))
    kb = out.stat().st_size / 1024
    dkb = (out_dir / DATA_FILE).stat().st_size / 1024
    xkb = (out_dir / DETAIL_FILE).stat().st_size / 1024
    print(f"✓ queue.html — {len(jobs)} renders, {len(upcoming)} coming, {kb:.0f} KB "
          f"(+ {DATA_FILE} {dkb:.0f} KB, {DETAIL_FILE} {xkb:.0f} KB on demand)")


if __name__ == "__main__":
    build(REPO / "_site")
