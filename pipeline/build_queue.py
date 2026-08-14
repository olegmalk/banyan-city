#!/usr/bin/env python3
"""THE QUEUE — every render job, the exact prompt it ran, and what it made.

The founder, 2026-08-14: "i cant keep blindly saying these videos are low
quality, lets improve the queue so i actually understand exactly how these
beats are being generated. we need to see a history of the queue, what has
been generated, what image reference did it use, what was the prompt, etc. and
also we need to see future things in the queue." Oleg, the same day: show when
something FINISHED, so progress is visible without asking anyone.

So this page answers three questions in that order, newest first:

  1. WHAT IS THE BOX DOING RIGHT NOW — fetched in the reader's own browser off
     the render box's telemetry branch, on exactly the pattern `/status` uses
     (build_sim.LIVE_JS.readBoxQueue): cache-busted, `no-store`, and stale
     after three missed five-minute publishes, at which point the numbers keep
     their value but lose the word "now".
  2. WHAT IS COMING — the committed specs in `pipeline/jobs/` that have no run
     record anywhere, with the consumer / success / why each one was written
     with. This is where a job says WHAT IT WILL MAKE AND WHY before it costs
     a GPU-hour.
  3. WHAT ALREADY RAN — 500-odd finished jobs grouped by day, each one a fold
     holding its full positive and negative prompt, its init frame, its
     reference, its recipe and every file it produced.

WHERE THE HISTORY COMES FROM, and why it is a committed file. `queue_history.py`
joins the box's run sidecars (on `farm-results-rtx5090`) against the committed
specs on `main` and writes `pipeline/measured/queue-history.json`. A Vercel
deploy checkout has no farm branches and a reader's browser cannot join yaml
across two of them, so the join happens on a laptop and the answer is committed.
THE PAGE IS THEREFORE EXACTLY AS OLD AS THAT FILE, it says so at the top in the
same breath as the counts, and re-running the generator is the only thing that
moves it (SITE.md, "the queue history's refresh duty").

WHY THE CARDS ARE BAKED AND NOT DRAWN IN JAVASCRIPT. The history is ~1.8 MB of
JSON. Baking the cards costs about the same bytes as inlining the JSON would —
and inlining the JSON *and* rendering from it would cost both. Baked wins on
every other axis: the prompts are in the HTML, so they are readable with
JavaScript off, greppable in the built file, and checkable by a pure-logic test
that never opens a browser. The one thing JavaScript does here is FILTER, and
it filters the DOM it was handed rather than a second copy of the data.

MEDIA IS NEVER COPIED INTO THE SITE. Every frame and clip is referenced
straight from `raw.githubusercontent.com/<owner>/<repo>/farm-results-rtx5090/…`
— the branch the box already pushes to — with `loading="lazy"` on images and
`preload="none"` on video, inside a fold that starts closed. A page holding
1,700 artifacts downloads none of them until something is opened.

HONESTY RULES, inherited from /pulse and /status:
  * a prompt the generator could not recover prints NOT RECORDED and the reason
    it gives, never a reconstruction — the 77-token fit happened on the box's
    tokenizer and a recomputation can differ exactly where it matters;
  * the box publishes how MANY jobs are waiting and of what kind, never their
    names, so this page does not pretend to name them (see `LIVE_JS`);
  * green is machine work, amber is waiting on the author, and the failed count
    is the alarm colour. A held spec is amber because the machine is not the
    thing holding it up.
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

HISTORY = REPO / "pipeline" / "measured" / "queue-history.json"
JOBS_DIR = REPO / "pipeline" / "jobs"

RAW = repo_slug.RAW_URL
REPO_URL = repo_slug.REPO_URL

# The branch the courier pushes artifacts to, and the branch the telemetry
# daemon publishes vitals to. They are deliberately different files on
# deliberately different branches — see test_the_courier_and_the_telemetry_
# daemon_own_different_branches. The legacy URL stays because the box's
# scheduled task is re-enabled by hand and the old place can be the fresher one
# for a while after a daemon change.
RESULTS_BRANCH = "farm-results-rtx5090"
RESULTS_BASE = f"{RAW}/{RESULTS_BRANCH}"
TELEMETRY_URL = f"{RAW}/farm-telemetry-rtx5090/telemetry.json"
TELEMETRY_URL_LEGACY = f"{RAW}/{RESULTS_BRANCH}/telemetry.json"

# Three missed publishes. The daemon writes every five minutes, so anything
# older than this is a record and not a reading — the same rule and the same
# number the status page's queue block keys on.
STALE_MINUTES = 15

# Oleg reads this in Dubai and every clock face on every page of this site is
# +04 and says so. The JSON underneath is UTC and stays that way.
TZ = datetime.timezone(datetime.timedelta(hours=4))
TZ_LABEL = "+04"

# What the page prints where a prompt should be and is not. One constant
# because the test checks the page for exactly this, and a page that quietly
# stopped saying it would be a page that quietly started implying the prompt
# was empty.
NO_PROMPT = "PROMPT NOT RECORDED"
NO_NEGATIVE = "NEGATIVE PROMPT NOT RECORDED"

# The founder does not need 573 open folds. Every day is a section; the newest
# one is open on arrival and the rest are one tap away.
DAYS_OPEN = 1

KIND_WORDS = {
    "motion": "motion take",
    "still": "still",
    "still-ipa": "still (reference-conditioned)",
    "inpaint": "inpaint",
    "other": "job",
}

STATE_WORDS = {
    "held": ("amber", "HELD — waiting on the author"),
    "authored": ("green", "AUTHORED — runnable, not yet finished"),
    "cancelled-by-founder": ("muted", "CANCELLED by the founder"),
}


CSS = """
.qlede { color: var(--muted); }
.qprov { font: 500 .78rem/1.7 var(--mono); color: var(--faint); margin: .4rem 0 0; }

/* ---- the counters across the top ---- */
.qstats { display: flex; flex-wrap: wrap; gap: .5rem; margin: 1rem 0 0; padding: 0;
  list-style: none; }
.qstats li { flex: 1 1 140px; padding: .6rem .8rem; border: 1px solid var(--line);
  border-radius: 10px; background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.qstats b { display: block; font: 700 1.28rem/1.25 var(--mono); color: var(--ink);
  font-variant-numeric: tabular-nums; }
.qstats span { font: 500 .72rem/1.5 var(--mono); color: var(--faint); }
.qstats li.work b { color: var(--leaf); }
.qstats li.wait b { color: var(--sap); }
.qstats li.bad b { color: var(--alarm, #e2564d); }

/* ---- live block ---- */
.qlive { margin: 1rem 0 0; padding: .9rem 1rem; border: 1px solid var(--line);
  border-radius: 14px; background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.qlive .qnow-t { font: 700 .95rem/1.4 var(--mono); color: var(--leaf); }
.qlive .qsay { font: 500 .82rem/1.7 var(--mono); color: var(--muted); margin: .35rem 0 0; }
.qlive .qsay.none { color: var(--faint); }
.qchips { display: flex; flex-wrap: wrap; gap: .4rem; margin: .55rem 0 0; }
.qchip { font: 700 .7rem/1 var(--mono); letter-spacing: .05em; text-transform: uppercase;
  padding: .34rem .6rem; border-radius: 999px; border: 1px solid var(--line);
  color: var(--muted); background: var(--code-bg); }
.qchip.work { color: var(--leaf); border-color: var(--leaf-deep); }
.qchip.wait { color: var(--sap); border-color: var(--sap-deep); }
.qchip.bad { color: var(--alarm, #e2564d); border-color: var(--alarm, #e2564d); }

/* ---- job cards ---- */
.qday { margin: 1.6rem 0 0; }
.qday > summary { cursor: pointer; list-style: none; padding: .6rem 0;
  font: 700 .82rem/1.4 var(--mono); letter-spacing: .08em; text-transform: uppercase;
  color: var(--muted); border-bottom: 1px solid var(--line); }
.qday > summary::-webkit-details-marker { display: none; }
.qday > summary::before { content: "\\25b8"; display: inline-block; margin-right: .55rem;
  color: var(--sap); transition: transform .2s ease; }
.qday[open] > summary::before { transform: rotate(90deg); }
.qday > summary .n { color: var(--faint); font-weight: 500; text-transform: none;
  letter-spacing: 0; }
.qjob { border: 1px solid var(--line); border-radius: 12px; margin: .55rem 0 0;
  background: var(--panel); overflow: hidden; }
.qjob > summary { cursor: pointer; list-style: none; padding: .6rem .75rem;
  display: flex; flex-wrap: wrap; align-items: baseline; gap: .3rem .6rem;
  font: 500 .8rem/1.5 var(--mono); color: var(--muted); }
.qjob > summary::-webkit-details-marker { display: none; }
.qjob > summary:hover { color: var(--ink); }
.qjob .beat { font-weight: 700; color: var(--ink); font-variant-numeric: tabular-nums; }
.qjob .kind { color: var(--leaf); }
.qjob .when, .qjob .dur { color: var(--faint); font-variant-numeric: tabular-nums; }
.qjob .rc-ok { color: var(--leaf); }
.qjob .rc-bad { color: var(--alarm, #e2564d); font-weight: 700; }
.qjob .body { padding: 0 .75rem .85rem; border-top: 1px solid var(--line-soft); }
.qjob.failed { border-color: var(--alarm, #e2564d); }

.qh { font: 700 .68rem/1.6 var(--mono); letter-spacing: .12em; text-transform: uppercase;
  color: var(--faint); margin: .85rem 0 .25rem; }
.qtext { font: 500 .82rem/1.6 var(--mono); color: var(--ink); background: var(--code-bg);
  border: 1px solid var(--line-soft); border-radius: 8px; padding: .6rem .7rem;
  margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; }
.qtext.neg { color: var(--muted); }
.qgap { font: 500 .8rem/1.6 var(--mono); color: var(--sap); margin: 0; }
.qgap i { color: var(--faint); font-style: normal; }
.qmeta { font: 500 .78rem/1.7 var(--mono); color: var(--faint); margin: .3rem 0 0;
  overflow-wrap: anywhere; }
.qmeta b { color: var(--muted); font-weight: 700; }

/* mobile-first: as many columns as fit, never narrower than a thumbnail worth
   looking at, and one column on a phone without a media query saying so. */
.qgrid { display: grid; gap: .5rem; margin: .35rem 0 0;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
.qgrid figure { margin: 0; }
.qgrid img, .qgrid video { width: 100%; display: block; border-radius: 8px;
  border: 1px solid var(--line); background: var(--code-bg); }
.qgrid figcaption { font: 500 .68rem/1.5 var(--mono); color: var(--faint);
  margin-top: .25rem; overflow-wrap: anywhere; }
.qinit { max-width: 260px; }

/* ---- upcoming ---- */
.qup { border: 1px solid var(--line); border-radius: 12px; margin: .55rem 0 0;
  background: var(--panel); overflow: hidden; }
.qup > summary { cursor: pointer; list-style: none; padding: .6rem .75rem;
  display: flex; flex-wrap: wrap; align-items: baseline; gap: .3rem .6rem;
  font: 500 .8rem/1.5 var(--mono); color: var(--muted); }
.qup > summary::-webkit-details-marker { display: none; }
.qup .beat { font-weight: 700; color: var(--ink); font-variant-numeric: tabular-nums; }
.qup.amber { border-left: 3px solid var(--sap); }
.qup.green { border-left: 3px solid var(--leaf-deep); }
.qup.muted { opacity: .72; }
.qup .state { font-weight: 700; }
.qup.amber .state { color: var(--sap); }
.qup.green .state { color: var(--leaf); }
.qup .body { padding: 0 .75rem .8rem; border-top: 1px solid var(--line-soft); }

/* ---- the filter ---- */
.qfilter { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem .8rem;
  margin: 1.4rem 0 .2rem; padding: .7rem .85rem; border: 1px solid var(--line);
  border-radius: 12px; background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.qfilter label { font: 700 .68rem/1.6 var(--mono); letter-spacing: .08em;
  text-transform: uppercase; color: var(--faint); }
.qfilter input { flex: 1 1 200px; min-height: 38px; font: 500 .88rem/1.4 var(--mono);
  color: var(--ink); background: var(--code-bg); border: 1px solid var(--line);
  border-radius: 999px; padding: .4rem .9rem; }
.qfilter input:focus-visible { outline: 2px solid var(--sap); outline-offset: 1px; }
.qfilter .count { flex: 1 1 100%; margin: 0; font: 500 .76rem/1.6 var(--mono);
  color: var(--faint); font-variant-numeric: tabular-nums; }
.qfilter[hidden] { display: none; }
.qhide { display: none; }
"""


# ---------------------------------------------------------------- reading

def load(path: Path = None) -> dict | None:
    """The committed history, or None. Never raises: a missing or half-written
    file must degrade this page to an honest sentence, not red the whole site
    build — several lanes share this tree and one of them may be mid-write."""
    p = Path(path) if path else HISTORY
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


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
    p = str(path or "").replace("\\", "/").lstrip("/")
    return f"{RESULTS_BASE}/{p}"


# ---------------------------------------------------------------- fragments

def prompt_html(job: dict) -> str:
    """The two prompt blocks, or the honest marker and the reason.

    This is the whole point of the page — the founder asked to stop guessing
    why a beat looks the way it does — so the text is printed in full, wrapped,
    selectable, and never truncated with an ellipsis.
    """
    src = job.get("prompt_source")
    out = []
    if job.get("prompt"):
        out.append('<p class="qh">Positive prompt</p>')
        out.append(f'<pre class="qtext">{_e(job["prompt"])}</pre>')
    else:
        out.append(f'<p class="qh">Prompt</p><p class="qgap">{NO_PROMPT}'
                   + (f' — <i>{_e(src)}</i>' if src else "") + "</p>")
    if job.get("negative"):
        out.append('<p class="qh">Negative prompt</p>')
        out.append(f'<pre class="qtext neg">{_e(job["negative"])}</pre>')
    elif job.get("prompt"):
        # A recovered positive with no negative is a real fact about the run
        # (some recipes carry none) and is worth one line; a job with neither
        # already said why above and does not need it twice.
        out.append(f'<p class="qh">Negative prompt</p><p class="qgap">{NO_NEGATIVE}</p>')
    if job.get("prompt") and src:
        out.append(f'<p class="qmeta">read from: {_e(src)}</p>')
    return "".join(out)


def media_html(job: dict) -> str:
    """Init frame, reference, and everything the job produced.

    `loading="lazy"` and `preload="none"`, inside a fold that starts closed:
    the page can reference 1,700 artifacts and cost a reader nothing until they
    open one card.
    """
    out = []
    init = job.get("init") or {}
    if init.get("path"):
        out.append('<p class="qh">Init frame — the image this render started from</p>')
        out.append(
            f'<div class="qgrid qinit"><figure>'
            f'<a href="{_e(art_url(init["path"]))}">'
            f'<img loading="lazy" decoding="async" alt="init frame for beat '
            f'{_e(job.get("beat"))}" src="{_e(art_url(init["path"]))}"></a>'
            f'<figcaption>{_e(str(init["path"]).rsplit("/", 1)[-1])}'
            + (f'<br>sha {_e(str(init.get("sha256"))[:12])}' if init.get("sha256") else "")
            + '</figcaption></figure></div>')

    ref = job.get("reference") or {}
    if ref:
        bits = []
        if ref.get("name"):
            bits.append(f'<b>{_e(ref["name"])}</b>')
        if ref.get("scale") is not None:
            bits.append(f'scale {_e(ref["scale"])}')
        if ref.get("step_window"):
            bits.append(_e(ref["step_window"]))
        if ref.get("sha256"):
            bits.append(f'sha {_e(str(ref["sha256"])[:12])}')
        out.append('<p class="qh">Reference image (IP-Adapter)</p>')
        if ref.get("path"):
            out.append(
                f'<div class="qgrid qinit"><figure>'
                f'<a href="{_e(art_url(ref["path"]))}">'
                f'<img loading="lazy" decoding="async" alt="reference image" '
                f'src="{_e(art_url(ref["path"]))}"></a>'
                f'<figcaption>{_e(ref.get("name") or "reference")}</figcaption>'
                f'</figure></div>')
        out.append(f'<p class="qmeta">{" · ".join(bits)}</p>')
        if not ref.get("path"):
            out.append('<p class="qmeta">The reference bytes live on the box only — '
                       'the sha above is what was recorded, and there is no URL to '
                       'show. Not an error, and not a picture this page can produce.</p>')
        if ref.get("note"):
            out.append(f'<p class="qmeta">{_e(ref["note"])}</p>')

    outs = job.get("outputs") or []
    if outs:
        out.append(f'<p class="qh">What it made — {len(outs)} file'
                   f'{"" if len(outs) == 1 else "s"}</p>')
        cells = []
        for o in outs:
            url, name = art_url(o.get("path")), o.get("name") or ""
            kb = o.get("bytes")
            cap = _e(name) + (f'<br>{int(kb) // 1024} KB' if isinstance(kb, int) else "")
            if o.get("kind") == "video":
                cells.append(f'<figure><video preload="none" controls playsinline '
                             f'src="{_e(url)}"></video>'
                             f'<figcaption>{cap}</figcaption></figure>')
            else:
                cells.append(f'<figure><a href="{_e(url)}">'
                             f'<img loading="lazy" decoding="async" alt="{_e(name)}" '
                             f'src="{_e(url)}"></a>'
                             f'<figcaption>{cap}</figcaption></figure>')
        out.append(f'<div class="qgrid">{"".join(cells)}</div>')
    elif not job.get("rc"):
        out.append('<p class="qh">What it made</p>'
                   '<p class="qgap">NO ARTIFACTS RECORDED <i>— the job reported '
                   'success and the branch carries no files under its name</i></p>')
    return "".join(out)


def recipe_html(job: dict) -> str:
    r = job.get("recipe") or {}
    bits = []
    for key, label in (("model", "model"), ("size", "size"), ("steps", "steps"),
                       ("guidance", "guidance"), ("scheduler", "scheduler"),
                       ("lora", "lora"), ("render_seconds", "s/frame"),
                       ("extra_negative_tier", "negative tier"),
                       ("negative_terms_removed", "negative terms removed")):
        v = r.get(key)
        if v not in (None, "", [], {}):
            bits.append(f"<b>{label}</b> {_e(v)}")
    seeds = r.get("seeds")
    if seeds:
        bits.append(f"<b>seeds</b> {_e(', '.join(str(s) for s in seeds[:8]))}"
                    + (" …" if len(seeds) > 8 else ""))
    for key in sorted(k for k in r if k not in
                      {"model", "size", "steps", "guidance", "scheduler", "lora",
                       "render_seconds", "extra_negative_tier",
                       "negative_terms_removed", "seeds"}):
        v = r.get(key)
        if v not in (None, "", [], {}):
            bits.append(f"<b>{_e(key)}</b> {_e(v)}")
    if not bits:
        return '<p class="qh">Recipe</p><p class="qgap">RECIPE NOT RECORDED ' \
               '<i>— no artifact sidecar carried the settings for this run</i></p>'
    return f'<p class="qh">Recipe</p><p class="qmeta">{" · ".join(bits)}</p>'


def purpose_html(job: dict) -> str:
    """Why the job was queued, in the words of whoever queued it. Clipped by
    the generator, not here — the page links the spec for the full text."""
    p = job.get("purpose") or {}
    out = []
    if p.get("consumer"):
        out.append(f'<p class="qh">Consumer — who is waiting for this</p>'
                   f'<p class="qmeta">{_e(p["consumer"])}</p>')
    if p.get("why"):
        out.append(f'<p class="qh">Why it was run</p><p class="qmeta">{_e(p["why"])}</p>')
    if p.get("success"):
        out.append(f'<p class="qh">What would count as success</p>'
                   f'<p class="qmeta">{_e(p["success"])}</p>')
    if job.get("purpose_note"):
        out.append(f'<p class="qmeta">{_e(job["purpose_note"])}</p>')
    v = job.get("verdict") or {}
    if v.get("beat_state") or v.get("beat_note") or v.get("gate"):
        line = " · ".join(_e(v[k]) for k in ("beat_state", "gate", "beat_note")
                          if v.get(k))
        out.append(f'<p class="qh">Where the beat stands</p><p class="qmeta">{line}</p>')
    return "".join(out)


def job_card(job: dict) -> str:
    """One finished job, folded. The summary is what a reader scans; everything
    the founder asked to see is inside, and inside is closed until asked for."""
    beat = job.get("beat")
    rc = job.get("rc")
    failed = bool(rc)
    rc_html = ('<span class="rc-ok">rc 0</span>' if not failed else
               f'<span class="rc-bad">rc {_e(rc)}'
               + (f' · failed at <b>{_e(job.get("failed_step"))}</b>'
                  if job.get("failed_step") else "") + "</span>")
    attempts = job.get("attempts")
    att = f' · attempt {_e(attempts)}' if isinstance(attempts, int) and attempts > 1 else ""
    beat_html = (f'<span class="beat">beat {int(beat):02d}</span>'
                 if isinstance(beat, int) else '<span class="beat">no beat</span>')
    summary = (
        f'{beat_html}'
        f'<span class="kind">{_e(kind_word(job.get("kind")))}</span>'
        f'<span class="when">{_e(clock(job.get("finished_at")))} {TZ_LABEL}</span>'
        f'<span class="dur">{_e(dur_words(job.get("duration_s")))}</span>'
        f'{rc_html}{att}')

    ident = []
    if job.get("id"):
        ident.append(f'<b>job</b> {_e(job["id"])}')
    if job.get("node"):
        ident.append(f'<b>node</b> {_e(job["node"])}')
    if job.get("runner_host"):
        ident.append(f'<b>ran on</b> {_e(job["runner_host"])}')
    if job.get("started_at"):
        ident.append(f'<b>started</b> {_e(clock(job["started_at"]))} {TZ_LABEL}')
    links = []
    if job.get("spec_file"):
        links.append(f'<a href="{REPO_URL}/blob/main/{_e(job["spec_file"])}">spec</a>')
    if job.get("artifacts_dir"):
        links.append(f'<a href="{REPO_URL}/tree/{RESULTS_BRANCH}/'
                     f'{_e(job["artifacts_dir"])}">artifacts</a>')
    if job.get("sidecar"):
        links.append(f'<a href="{REPO_URL}/blob/{RESULTS_BRANCH}/'
                     f'{_e(job["sidecar"])}">run record</a>')
    if links:
        ident.append(" · ".join(links))

    body = (prompt_html(job) + recipe_html(job) + media_html(job) + purpose_html(job)
            + (f'<p class="qmeta">{" · ".join(ident)}</p>' if ident else ""))
    cls = "qjob failed" if failed else "qjob"
    return (f'<details class="{cls}" data-b="{_e(beat) if beat is not None else ""}">'
            f'<summary>{summary}</summary>'
            f'<div class="body">{body}</div></details>')


def day_section(key: str, jobs: list, open_it: bool) -> str:
    ok = sum(1 for j in jobs if not j.get("rc"))
    bad = len(jobs) - ok
    mins = sum(int(j.get("duration_s") or 0) for j in jobs) / 60.0
    note = (f'<span class="n">{len(jobs)} job{"" if len(jobs) == 1 else "s"}'
            + (f", {bad} failed" if bad else "")
            + (f" · {mins / 60:.1f} h of machine time" if mins >= 60
               else f" · {mins:.0f} min of machine time" if mins else "")
            + "</span>")
    cards = "".join(job_card(j) for j in jobs)
    return (f'<details class="qday" data-day="{_e(key)}"{" open" if open_it else ""}>'
            f'<summary>{_e(day_title(key))} {note}</summary>{cards}</details>')


def upcoming_card(row: dict, success: str | None) -> str:
    state = row.get("state") or "authored"
    colour, words = STATE_WORDS.get(state, ("green", state.upper()))
    beat = row.get("beat")
    beat_html = (f'<span class="beat">beat {int(beat):02d}</span>'
                 if isinstance(beat, int) else '<span class="beat">no beat</span>')
    est = row.get("est_minutes")
    summary = (
        f'{beat_html}<span class="kind">{_e(kind_word(row.get("kind")))}</span>'
        f'<span class="state">{_e(words)}</span>'
        + (f'<span class="when">~{_e(est)} min</span>' if est else "")
        + (f'<span class="when">priority {_e(row.get("priority"))}</span>'
           if row.get("priority") is not None else ""))
    body = []
    if row.get("consumer"):
        body.append(f'<p class="qh">Consumer — who is waiting for it</p>'
                    f'<p class="qmeta">{_e(row["consumer"])}</p>')
    if success:
        body.append(f'<p class="qh">What would count as success</p>'
                    f'<p class="qmeta">{_e(success)}</p>')
    if row.get("why_first"):
        body.append(f'<p class="qh">Why</p><p class="qmeta">{_e(row["why_first"])}</p>')
    if row.get("hold_reason"):
        body.append(f'<p class="qh">What is holding it</p>'
                    f'<p class="qmeta">{_e(row["hold_reason"])}</p>')
    tail = [f'<b>job</b> {_e(row.get("id"))}']
    if row.get("node"):
        tail.append(f'<b>node</b> {_e(row["node"])}')
    if row.get("spec_file"):
        tail.append(f'<a href="{REPO_URL}/blob/main/{_e(row["spec_file"])}">spec</a>')
    body.append(f'<p class="qmeta">{" · ".join(tail)}</p>')
    return (f'<details class="qup {colour}" data-b="{_e(beat) if beat is not None else ""}">'
            f'<summary>{summary}</summary>'
            f'<div class="body">{"".join(body)}</div></details>')


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
    jobs = [j for j in data["jobs"] if isinstance(j, dict)]
    upcoming = [u for u in (data.get("upcoming") or []) if isinstance(u, dict)]
    jobs.sort(key=lambda j: str(j.get("finished_at") or ""), reverse=True)

    ok = sum(1 for j in jobs if not j.get("rc"))
    bad = len(jobs) - ok
    held = sum(1 for u in upcoming if u.get("state") == "held")
    runnable = sum(1 for u in upcoming if u.get("state") == "authored")
    files = sum(len(j.get("outputs") or []) for j in jobs)
    machine_h = sum(int(j.get("duration_s") or 0) for j in jobs) / 3600.0

    days: dict = {}
    for j in jobs:
        days.setdefault(day_key(j.get("finished_at")), []).append(j)
    ordered = sorted((k for k in days if k != "undated"), reverse=True)
    if "undated" in days:
        ordered.append("undated")

    measured = meta.get("measured_at") or "unknown"
    src_commit = str(meta.get("source_commit") or "")[:9]

    stats = (
        '<ul class="qstats">'
        f'<li class="work"><b>{len(jobs)}</b><span>jobs finished, all time</span></li>'
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
        f'<p class="qmeta">The box publishes HOW MANY jobs are waiting and of what '
        f'kind — never their names (<code>pipeline/telemetry.py</code>). So the named '
        f'list below is the committed specs with no run record: what is authored, and '
        f'what is held. When the box names the job it is running, its spec is matched '
        f'by id and opened here.</p>')

    up_cards = "".join(upcoming_card(u, spec_success(u.get("spec_file")))
                       for u in upcoming)
    up_section = (
        f'<h2 id="upcoming">Coming — {len(upcoming)} job'
        f'{"" if len(upcoming) == 1 else "s"} written and not yet run</h2>'
        f'<p class="qlede">Every one of these is a committed spec in '
        f'<code>pipeline/jobs/</code> that no run record anywhere accounts for. '
        f'<b>Amber is waiting on you</b> — a held job is held by a question only '
        f'the author can answer, and the machine cannot start it. Green is runnable.</p>'
        + (up_cards or '<p class="notice">Nothing is authored and unrun: every '
                       'committed spec has a run record.</p>'))

    filt = (
        '<div class="qfilter" id="q-filter" hidden>'
        '<label for="q-q">Filter</label>'
        '<input id="q-q" type="search" inputmode="search" autocomplete="off" '
        'placeholder="a beat number, a word from a prompt, a model, a job id">'
        f'<p class="count" id="q-count">{len(jobs)} finished jobs, '
        f'{len(upcoming)} coming</p></div>')

    history = "".join(day_section(k, days[k], i < DAYS_OPEN)
                      for i, k in enumerate(ordered))

    return f"""
<p class="eyebrow">the queue</p>
<h1>The queue — every job, its prompt, and what it made</h1>
<p class="lede qlede">Each finished render below opens onto the exact positive and
negative prompt it ran, the frame it started from, the reference it was conditioned
on, its recipe, and every file it produced. Nothing here is a summary of a render:
it is the render's own record.</p>
<p class="qprov">History measured <b>{_e(measured)}</b> from
<code>{_e(RESULTS_BRANCH)}</code> at <code>{_e(src_commit)}</code> ·
{len(jobs)} jobs · written by <code>pipeline/queue_history.py</code> and committed,
so this page is exactly as fresh as that file and no fresher. The block below it is
live.</p>
{stats}
{live}
{up_section}
{filt}
<h2 id="finished">Finished — newest day first</h2>
<p class="qlede">Grouped by the day each job finished, on a {TZ_LABEL} clock. Frames
and clips load from the render box's own branch only when you open a card.</p>
{history}
<h2>What this page can and cannot know</h2>
<p class="qprov">
<b>Clocks are {TZ_LABEL}.</b> The record underneath is UTC; every face here is
converted once, at build.<br>
<b>A prompt this page cannot show, it names.</b> {NO_PROMPT} is printed with the
reason — for a motion job whose spec was deleted, or a render from before the box
wrote artifact sidecars, the bytes are genuinely gone. They are never reconstructed:
the 77-token fit happened on the box's tokenizer and a recomputation can differ
exactly where it would matter.<br>
<b>Nothing here was copied into the site.</b> Every image and clip is served from
<code>{_e(RESULTS_BRANCH)}</code> on GitHub's raw CDN, lazily, on open. A card you
do not open costs nothing.<br>
<b>Finished is not approved.</b> rc 0 means the box ran the job, and nothing more.
Whether a frame is any good is the author's call and it lives on
<a href="review">the review board</a>.<br>
<b>{bad} of {len(jobs)} runs failed</b> and they are here with the rest, red, with
the step they died at. A queue history that showed only the successes would be an
advertisement.</p>
"""


# Plain string, not an f-string: JavaScript, full of braces. The three URLs and
# the staleness rule are substituted by build().
LIVE_JS = """
/* ---- what the box is doing, read by the reader's own browser ----------------
   The same source, the same cache-busting and the same staleness rule as the
   queue block on /status (build_sim.LIVE_JS.readBoxQueue): the telemetry branch
   first, the branch the daemon used to publish to as a fallback, `no-store`
   with a per-minute cache-buster, and a reading older than three publishes is
   a record rather than a claim about now.

   THE BOX NAMES ONE JOB AND COUNTS THE REST. `queue_sample` publishes counts,
   a kind mix, and the running job's own record — never the names of the jobs
   waiting. So this block reports exactly that, and where the running job's id
   matches a spec baked into this page it opens the spec's consumer / success /
   why underneath. A page that listed names the box never published would be
   inventing the most checkable thing on it. */
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
    var meta = [];
    meta.push("job " + id);
    if (cur.node) meta.push("node " + cur.node);
    if (cur.started_at) {
      meta.push("started " +
        words(Math.max(0, Math.round(Date.now() / 1000 - cur.started_at))));
    }
    nowEl.appendChild(el("p", "qmeta", meta.join(" \\u00b7 ")));
    if (cur.makes && cur.makes.length) {
      line(nowEl, "What it will make", cur.makes.join(", "));
    }
    /* THE SPEC, matched by id. SPECS holds every committed spec with no run
       record — which is exactly the set a running or waiting job is drawn
       from, because a job that has finished is no longer in it. */
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
        if (q.failed) chip("bad", q.failed + " sitting failed");
        if (typeof q.done_24h === "number") chip("", q.done_24h + " finished in 24 h");
        if (q.runner_alive === false) {
          chip("bad", "nothing is draining this queue");
        }
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
          ". Nothing else on this page depends on it \\u2014 the history below is " +
          "baked into these bytes.";
        clear(nowEl);
      });
  }
  read();
  /* five minutes: the fastest anything upstream is written. */
  setInterval(function () { if (!document.hidden) read(); }, 300000);
})();

/* ---- the filter -------------------------------------------------------------
   Over the DOM this page was built with, not over a second copy of the data.
   Inlining the history JSON as well as the cards would have doubled a 2 MB page
   to say the same thing twice; instead each card's searchable text is taken
   from the card itself, once, the first time anyone types. A bare number is
   read as a beat number (that is what the founder types), anything else is a
   substring over the whole card — prompt, model, seed, node, job id. */
(function () {
  var box = document.getElementById("q-filter");
  var input = document.getElementById("q-q");
  var count = document.getElementById("q-count");
  if (!box || !input) return;
  box.hidden = false;                      /* dead control never shown */
  var cards = [].slice.call(document.querySelectorAll(".qjob, .qup"));
  var days = [].slice.call(document.querySelectorAll(".qday"));
  var index = null;

  function build() {
    index = cards.map(function (c) {
      return {el: c, beat: c.getAttribute("data-b") || "",
              text: (c.textContent || "").toLowerCase()};
    });
  }
  function apply() {
    var q = input.value.trim().toLowerCase();
    if (!index) build();
    var beatOnly = /^b?(\\d{1,3})$/.exec(q);
    var shown = 0, hidden = 0;
    for (var i = 0; i < index.length; i++) {
      var row = index[i], hit;
      if (!q) hit = true;
      else if (beatOnly) hit = row.beat === beatOnly[1] ||
                               row.beat === String(parseInt(beatOnly[1], 10));
      else hit = row.text.indexOf(q) !== -1;
      row.el.classList.toggle("qhide", !hit);
      if (hit) shown++; else hidden++;
    }
    for (var d = 0; d < days.length; d++) {
      var day = days[d];
      var any = day.querySelector(".qjob:not(.qhide)");
      day.classList.toggle("qhide", !any);
      if (q && any) day.open = true;
    }
    count.textContent = q
      ? shown + " matching \\u00b7 " + hidden + " hidden \\u00b7 filter: " + input.value
      : QCOUNT_ALL;
  }
  input.addEventListener("input", apply);
  input.addEventListener("search", apply);
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
        s = spec_success(row.get("spec_file"))
        if s:
            entry["success"] = s[:600]
        if entry:
            out[str(sid)] = entry
    return json.dumps(out, ensure_ascii=False, separators=(",", ":"))


def build(out_dir: Path):
    from build_site import page          # late import: build_site calls us
    data = load()
    body = render(data)
    upcoming = [u for u in ((data or {}).get("upcoming") or []) if isinstance(u, dict)]
    jobs = [j for j in ((data or {}).get("jobs") or []) if isinstance(j, dict)]
    consts = (f"var TEL_URL={json.dumps(TELEMETRY_URL)},"
              f"TEL_URL_LEGACY={json.dumps(TELEMETRY_URL_LEGACY)},"
              f"STALE_MIN={STALE_MINUTES},"
              f"QCOUNT_ALL={json.dumps(f'{len(jobs)} finished jobs, {len(upcoming)} coming')},"
              f"SPECS={specs_js(upcoming)};")
    tail = "<script>" + consts + LIVE_JS + "</script>"
    out = Path(out_dir) / "queue.html"
    out.write_text(page(
        "The queue — every job, its prompt, and what it made",
        f"<style>{CSS}</style>" + body,
        path="queue.html",
        desc="Every render job the farm has run, with the exact prompt, the "
             "reference frame and the files it produced — plus what is queued next.",
        tail=tail,
    ))
    kb = out.stat().st_size / 1024
    print(f"✓ queue.html — {len(jobs)} finished, {len(upcoming)} coming, {kb:.0f} KB")


if __name__ == "__main__":
    build(REPO / "_site")
