#!/usr/bin/env python3
"""banyan city, THE STUDIO — one page that shows the show being made.

Dad asked for the sim (2026-07-30) and it stays: the episode is a tree growing
leaves, our machines are buildings that glow while they render, the cloud GPU is
a cloud, the author's open decisions are quests, the people voting on the
reactions thread are citizens. Since 2026-08-03 the machines share one animated
"lot" that the real crew walks (the author, the author's dad, the AI steward,
plus actual thread commenters) — decoration may be charming, but every sprite
is somebody real. Pure CSS + emoji — the public-site CSP allows no external
asset, and nothing here needs JavaScript.

The stranger-eyes audit (2026-07-30) rebuilt the page's priorities:
  1. the episode plays FIRST — a visitor from TikTok came for a cartoon;
  2. every visible string is plain English (scene, final, waiting for…), model
     codenames only ever appear prefixed "animated by:";
  3. no internal log tokens, no task IDs, no unexplained pills;
  4. one primary action (watch), everything machine-facing below the fold.

Data comes from `build_status.py` (repo files) and the PUBLIC GitHub API only —
the deploy server has no local git refs and no `gh` CLI.
"""
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from site_theme import THEME_CSS  # noqa: E402  the one visual language

GH = "olegmlkvorg/banyan-city"
CANONICAL = "https://banyan.city"
PAGE = "status.html"
# One name for this page, used in the <title>, the <h1> and our own nav.
PAGE_NAME = "the studio"
DESC = ("Sapling, the AI-animated micro-drama growing in Banyan City. This is the "
        "studio floor: episode 1 playing, every scene's state, the machines that "
        "render it, and what the author still has to decide.")

# The family's machines, named for people who do not live here.
MACHINES = {
    "m1pro": ("the studio laptop", "🏛"),
    "m2": ("the spare laptop", "🏢"),
    "msi": ("the fast-GPU laptop", "🏭"),
    "rtx5090": ("the big render house", "🏟"),
}
STATE_WORDS = {  # css state → the legend under the town
    "working": "glowing = rendering right now",
    "idle": "dim = switched on, nothing to do",
    "asleep": "faded = offline",
}


def _get(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "banyan-sim-build"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode()
    except Exception:
        return ""


def farm_branches():
    """farm-results-* branches via the public API — the deploy server has no
    local refs (the invisible-buildings bug, 2026-07-30)."""
    raw = _get(f"https://api.github.com/repos/{GH}/branches?per_page=100")
    try:
        return [b["name"] for b in json.loads(raw) if b["name"].startswith("farm-results-")]
    except Exception:
        return []


def branch_heartbeat(branch):
    txt = _get(f"https://raw.githubusercontent.com/{GH}/{branch}/farm-out/heartbeat.txt")
    return txt.strip().splitlines()[-1] if txt.strip() else ""


def queue_tasks() -> list:
    """The live work list (pipeline/farm-queue.yaml on main), public raw —
    the bird's-eye should say WHAT is being rendered and WHY (founder,
    2026-07-30), and the queue file is where the why lives."""
    import yaml as _yaml
    txt = _get(f"https://raw.githubusercontent.com/{GH}/main/pipeline/farm-queue.yaml")
    try:
        return (_yaml.safe_load(txt) or {}).get("tasks") or []
    except Exception:
        return []


def _shot_runs(beats: str) -> str:
    """'1,2,3,7,9,10' → '1–3, 7, 9–10' — a merged job names its shots as
    ranges, not as a fifteen-number recital."""
    nums = sorted({int(b) for b in beats.split(",") if b.strip().isdigit()})
    if not nums:
        return beats.replace(",", ", ")
    runs, start, prev = [], nums[0], nums[0]
    for n in nums[1:] + [None]:
        if n is not None and n == prev + 1:
            prev = n
            continue
        runs.append(str(start) if start == prev else f"{start}–{prev}")
        if n is not None:
            start = prev = n
    return ", ".join(runs)


def merge_queue(tasks: list) -> list:
    """Identical jobs that differ only in their shot number are ONE job to a
    reader. On 2026-08-03 the queue held fifteen single-beat rows and the page
    printed the same sentence fifteen times — display-only merge; the heartbeat
    matcher keeps the raw list, since a worker claims tasks by their full id."""
    merged, index = [], {}
    for t in tasks:
        fam = re.match(r"[a-z]+", str(t.get("id", "")))
        key = (fam.group(0) if fam else "",
               tuple(sorted((k, str(v)) for k, v in t.items()
                            if k not in ("beats", "id", "seed_base"))))
        if key in index:
            index[key]["beats"] = f'{index[key]["beats"]},{t.get("beats", "")}'
        else:
            t = dict(t)
            t["beats"] = str(t.get("beats") or "")
            index[key] = t
            merged.append(t)
    return merged


def task_story(t: dict) -> tuple:
    """(what, why) in a stranger's words, from a queue task's own fields."""
    tid = str(t.get("id", ""))
    beats = str(t.get("beats") or "").strip()
    shots = f"shot{'s' if ',' in beats else ''} {_shot_runs(beats)}" if beats \
        else "world scenery"
    seeds = int(t.get("seeds", 4))
    if tid.startswith("prod-open"):
        return (f"{seeds} candidate frames each for {shots}",
                "these shots are open requests — the author wants a better frame, and new takes feed the next vote")
    if tid.startswith("prod-hires"):
        w, h = t.get("width", 832), t.get("height", 1216)
        return (f"high-res ({w}×{h}) frames for {shots}",
                "sharper versions of finished scenes, for the author's picture-quality review")
    if tid.startswith(("keep", "ref")):
        return (f"{seeds} background-art studies ({str(t.get('slug', '')).replace('keep-', '').replace('-', ' ')})",
                "world-reference art — the bank every future shot borrows its look from")
    # VIDEO tasks fell through to the stills wording, so the page told everyone the
    # farm was making "4 frames for shots" while it spent an entire day animating
    # video (founder, 2026-08-02: "not synced"). A status page describing the wrong
    # KIND of work is worse than one that is merely late.
    if t.get("video"):
        model = {"animegen": "an anime-trained model",
                 "ti2v-5b": "Wan 2.2"}.get(str(t.get("video_model", "ti2v-5b")),
                                           str(t.get("video_model")))
        secs = t.get("seconds", 3.0)
        steps = t.get("steps", 20)
        n = len([b for b in beats.split(",") if b]) or 1
        if t.get("prefetch"):
            return ("downloading model weights",
                    "fetching a bigger video model to try later — no rendering, just the download")
        return (f"{n} moving clip{'s' if n != 1 else ''} ({secs:g}s each) for {shots}, "
                f"on {model} at {steps} steps",
                "animating stills the author already approved — the still is the "
                "composition, the render only decides what MOVES")
    return (f"{seeds} frames for {shots}", "queued by the studio")


# ---------------------------------------------------------------- citizens ---
URL_RE = re.compile(r"\(?\bhttps?://\S+\)?")
VOTE_RE = re.compile(r"^\s*\d{1,2}\s*:")


def humanise(body: str) -> str:
    """A thread comment as a speech bubble: no markdown, no half-eaten URLs.

    The bubbles used to ship raw ('🗳 **Final two ballots** (board: https://ban…')
    which made the liveliest part of the page look broken.
    """
    # markdown links first: URL_RE would otherwise eat "(…)" and leave "[words]"
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", body or "")  # links/images → their words
    text = URL_RE.sub("", text)                                 # bare URLs, brackets and all
    text = re.sub(r"[*_`>#\[\]]+", "", text)                    # bold, headers, quotes, leftovers
    text = re.sub(r"\(\s*(board|thread|here)?\s*:?\s*\)", "", text)  # emptied parentheses
    # "(board: https://… )" loses its closing bracket with the URL, leaving an
    # orphaned "(board:" mid-sentence — drop any such label with no ")" ahead.
    text = re.sub(r"\(\s*[\w ]{0,14}:\s*(?![^()]*\))", "", text)
    text = " ".join(text.split())
    # a stripped URL can leave a sentence hanging on its conjunction ("… board and")
    text = re.sub(r"[\s,:;—-]*\b(and|at|in|on|see|via)?[\s,:;—-]*$", "", text)
    if len(text) > 96:                                          # truncate on a word
        text = text[:96].rsplit(" ", 1)[0] + "…"
    return text


def is_vote_tally(body: str) -> bool:
    """'06: lets use B. 07: A' — a private ballot log, unreadable out of context."""
    lines = [ln for ln in (body or "").splitlines() if ln.strip()]
    return bool(lines) and sum(1 for ln in lines if VOTE_RE.match(ln)) >= len(lines) / 2


def latest_thread_comments(n=3):
    """(author, sentence, permalink) for the newest readable comments."""
    raw = _get(f"https://api.github.com/repos/{GH}/issues/1/comments?per_page=100")
    try:
        cs = json.loads(raw)
    except Exception:
        return []
    out = []
    for c in reversed(cs):
        body = c.get("body") or ""
        if is_vote_tally(body):
            continue
        said = humanise(body)
        if not said:
            continue
        out.append((c.get("user", {}).get("login", "someone"), said,
                    c.get("html_url", f"https://github.com/{GH}/issues/1")))
        if len(out) == n:
            break
    return list(reversed(out))


# ---------------------------------------------------------------- machines ---
def machine_state(branch_tail: str, queue: list | None = None) -> tuple:
    """(css_state, human sentence, raw heartbeat for a title attribute).

    Heartbeat lines look like `11:32:16Z STARTED task=keep-m1pro-1785431597 …`.
    The epoch ID never reaches the page — but it DOES get matched against the
    live queue so a working machine says what it is making and why.
    """
    if not branch_tail:
        return "asleep", "offline — has not checked in yet", ""
    try:
        hh, mm, ss = branch_tail.split("Z")[0].split(":")
        now = time.gmtime()
        age = (now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec) - \
              (int(hh) * 3600 + int(mm) * 60 + int(ss))
        if age < 0:
            age += 86400
    except Exception:
        age = 9999
    mins = max(age, 0) // 60
    ago = "just now" if mins < 1 else (f"{mins} min ago" if mins < 90
                                       else f"{mins // 60} h ago")
    working = ("STARTED" in branch_tail or "MODEL_LOADED" in branch_tail)
    scene = re.search(r"beats?=\s*(\d+)", branch_tail)
    if age < 360 and working:
        # name the actual job from the queue: what it makes, and why
        tid = re.search(r"task=([\w.-]+)", branch_tail)
        entry = next((t for t in (queue or [])
                      if str(t.get("id")) == (tid.group(1) if tid else "")), None)
        if entry:
            what, _why = task_story(entry)
            return "working", f"making {what}", branch_tail
        job = f"rendering scene {int(scene.group(1)):02d}" if scene else \
            "rendering a round of candidate frames"
        return "working", job, branch_tail
    if age < 1800:
        return "idle", f"idle — last job finished {ago}", branch_tail
    return "asleep", f"offline — last seen {ago}", branch_tail


# ------------------------------------------------------------------- pieces ---
def _e(s):
    return html.escape(str(s))


def scene_list_html(rows: list) -> str:
    """One line per scene, no table — a 5-column grid was unreadable at 390px
    and `overflow-x:hidden` on <body> silently clipped it. Columns that are
    empty for every scene are simply not written."""
    from build_status import request_url
    items = []
    for r in rows:
        bits = []
        if r["animations"]:
            bits.append("animated by: " + ", ".join(r["animations"]))
        if r["candidates"]:
            bits.append(f'{r["candidates"]} rival frames tried')
        if r["waiting_for"]:
            bits.append("waiting for " + r["waiting_for"])
        meta = " · ".join(bits)
        chip = ('<span class="chip trunk">approved</span>' if r["final"]
                else '<span class="chip hot">in progress</span>')
        ask = ""
        if r["request"]:  # one honest link instead of a bare issue number
            ask = f' <a href="{_e(request_url(r["request"]))}">open request &rarr;</a>'
        items.append(
            f'<li><b>Scene {r["num"]:02d} · {_e(r["name"])}</b> {chip}'
            + (f'<div class="mono">{_e(meta)}{ask}</div>' if meta or ask else "")
            + "</li>")
    return f'<ol class="scenes">{"".join(items)}</ol>'


def steps_table_html(steps: list) -> str:
    """Named columns, and a heading that admits most values are durations."""
    body = "".join(f"<tr><td>{_e(a)}</td><td class='mono'>{_e(b)}</td></tr>" for a, b in steps)
    return ('<div class="scroll"><table><tr><th>Step</th><th>Time &amp; cost</th></tr>'
            f"{body}</table></div>")


def quests_html(inbox: list) -> str:
    """The author's own decision list. Read-only for everyone else — the old
    board offered five identical gold 'look →' links for tasks a visitor cannot
    do, two of them into a raw GitHub file listing."""
    if not inbox:
        return '<p class="notice">Nothing waiting — the city runs itself today.</p>'
    out = []
    for q in inbox:
        link, label = q.get("public"), "look at it &rarr;"
        if link and "/tree/" in link:      # a directory of .md files is not a page
            label = "read it on GitHub &rarr;"
        a = f' <a href="{_e(link)}">{label}</a>' if link else ""
        out.append(f'<li><b>{_e(q.get("title", ""))}</b>{a}'
                   f'<div class="mono">{_e(q.get("detail", ""))}</div></li>')
    return f'<ol class="quests">{"".join(out)}</ol>'


def walkers_html(comments: list, any_working: bool) -> str:
    """The crew, walking the lot. Every sprite is somebody real: the three
    people/agents who actually run the studio, up to two citizens straight off
    the reactions thread (their own usernames), and a courier only while a
    machine is truly rendering. Decoration is allowed to be charming; it is
    not allowed to invent staff."""
    folk = [("🧑‍💻", "the author"),
            ("🧑‍🔧", "the author's dad"),
            ("🤖", "the steward — an AI")]
    seen = set()
    for who, _said, _url in comments:
        if who in seen:
            continue                     # one commenter = one villager
        seen.add(who)
        folk.append((("🧑‍🌾", "🧙")[len(seen) % 2], who))
        if len(seen) == 2:
            break
    if any_working:
        folk.append(("🛻", "hauling fresh frames"))
    out = ""
    for i, (spr, tag) in enumerate(folk):
        dur = 22 + i * 7                 # seconds one way — everyone ambles
        lo = 5 + i * 8                   # starting spot, % — also the resting
        out += (                         # spot when animations are off
            f'<div class="walker" aria-hidden="true" '
            f'style="--d:{dur}s; --lo:{lo}%; --delay:-{i * 9}s">'
            f'<span class="spr"><i>{spr}</i></span>'
            f'<span class="wtag">{_e(tag)}</span></div>')
    return out


def quest_board_html(rows: list) -> str:
    """Open quests anyone can take. An 'art quest' is a real open render
    request from requests.yaml; the two standing quests are the routes that
    always exist. The reward line states what actually happens — a take lands
    on the public board and the author may make it the scene — because a
    promised prize the repo cannot pay would fail the honesty gate."""
    from build_status import request_url
    open_reqs = [r for r in rows if r["request"]]
    # the brief and the reward are the same for every art quest — say them ONCE,
    # or the board repeats one sentence seven times (the fifteen-identical-rows
    # lesson, again)
    note = ""
    if open_reqs:
        note = (f'<p class="qnote">🎨 <b>Art quests</b> — the author wants a better frame '
                f'than the current one for {len(open_reqs)} scenes. Make one — any tool, '
                'any style that fits — and hand it in. '
                '<span class="reward"><b>reward</b> · your take goes on the public board; '
                'if the author picks it, your frame IS the scene, credited</span></p>')
    cards = [
        f'<div class="quest slim"><span class="chip hot">🎨 art quest</span>'
        f'<b>Scene {r["num"]:02d} · {_e(r["name"])}</b>'
        f'<a href="{_e(request_url(r["request"]))}">take this quest &rarr;</a></div>'
        for r in open_reqs]
    cards.append(
        '<div class="quest"><span class="chip">✍️ writing quest</span><br>'
        '<b>Write episode 2 yourself</b>'
        '<p>The story branches. Take the tree, grow your own limb — the right '
        'to branch is the one rule that can never be cut.</p>'
        '<div class="reward"><b>reward</b> · your branch lives in the city, '
        'under your name, forever</div>'
        '<a href="create.html">take this quest &rarr;</a></div>')
    cards.append(
        '<div class="quest"><span class="chip">🗳 citizen quest</span><br>'
        '<b>Say what you think</b>'
        '<p>Reactions on the public thread are what the story grows toward — '
        'they decide which branch becomes the trunk.</p>'
        '<div class="reward"><b>reward</b> · the next episode bends toward '
        'what the crowd asked for</div>'
        f'<a href="https://github.com/{GH}/issues/1">take this quest &rarr;</a></div>')
    return f'{note}<div class="qboard">{"".join(cards)}</div>'


def badges_html(milestones: list) -> str:
    """(emoji, name, unlocked, detail) → the milestone strip. Every unlocked
    badge is a checkable repo fact; a locked one names exactly what is
    missing, so the strip doubles as the episode's to-do list."""
    out = []
    for emoji, name, unlocked, detail in milestones:
        cls = "" if unlocked else " locked"
        out.append(f'<div class="badge{cls}"><div class="ico">{emoji}</div>'
                   f'<div class="nm">{_e(name)}</div>'
                   f'<div class="cap">{_e(detail)}</div></div>')
    return f'<div class="badges">{"".join(out)}</div>'


# ---- the render box's own telemetry -------------------------------------------
# Oleg asked for GPU utilisation and RAM over time (2026-08-04), the day the 5090
# bluescreened mid-render and we had no idea what the machine was doing when it
# went. The box samples itself every 10s and publishes a 24-hour, 1-minute summary
# to its courier branch; the browser fetches THAT, so the numbers are as fresh as
# the box's last push instead of as fresh as the last deploy.
#
# This is the only live thing on this page, and the honesty rule (SITE.md) applies
# hardest here: a chart is drawn ONLY when the newest sample is younger than
# TELEMETRY_STALE_MINUTES. Otherwise the page says "no recent telemetry" and means
# it. Same repo constant as every other raw fetch on this page — the deploy server
# has no git refs to read a remote from.
TELEMETRY_BRANCH = "farm-results-rtx5090"
TELEMETRY_URL = f"https://raw.githubusercontent.com/{GH}/{TELEMETRY_BRANCH}/telemetry.json"
TELEMETRY_STALE_MINUTES = 15

TEL_CSS = """
/* ---- the render box: three single-axis charts, one series each.
   ONE SERIES PER CHART is not a layout accident. GPU% and GB cannot share a y
   axis without lying about scale, and the two colours this site owns — leaf green
   and sap amber — are 4.5 ΔE apart under protanopia (measured), so a two-series
   chart would encode identity in a difference some readers cannot see. A title
   per chart carries the identity instead, and no legend is needed. ---- */
.telnote { font: 500 .82rem/1.7 var(--mono); color: var(--faint); }
.tchart { margin: 1.1rem 0 0; }
.tchart figcaption { font: 700 .72rem/1.5 var(--mono); letter-spacing: .06em;
  text-transform: uppercase; color: var(--muted); display: flex; flex-wrap: wrap;
  justify-content: space-between; gap: .2rem .8rem; }
.tchart figcaption .cap { font-weight: 500; text-transform: none; letter-spacing: 0;
  color: var(--faint); }
.tchart svg { width: 100%; height: auto; display: block; margin: .35rem 0 .15rem;
  background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 12px; touch-action: pan-y; }
.tchart .rdout { font: 500 .74rem/1.6 var(--mono); color: var(--faint);
  min-height: 1.6em; font-variant-numeric: tabular-nums; }
.tchart .rdout b { color: var(--ink); }
.tchart .grid { stroke: var(--line-soft); stroke-width: 1; }
.tchart .axis { fill: var(--faint); font: 500 10px var(--mono); }
.tchart .ln { fill: none; stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
.tchart .fill { stroke: none; opacity: .13; }
.tchart .pk { fill: var(--ink); font: 600 10px var(--mono); }
.tchart .dot { stroke: var(--panel); stroke-width: 2; }
.tchart .cross { stroke: var(--muted); stroke-width: 1; stroke-dasharray: 2 3; }
.tel-gpu { color: var(--sap); }        /* the series wears currentColor */
.tel-mem { color: var(--leaf); }
"""

# Plain string, not an f-string: this is JavaScript and it is full of braces.
# TEL_URL / TEL_STALE are emitted next to it by build().
TEL_JS = """
/* The render box's charts. No library, no external code — one fetch of our own
   JSON off the courier branch, three inline SVGs, ~150 lines. If any of it fails
   the page says so in words instead of drawing a dead chart. */
(function () {
  var note = document.getElementById("tel-note"), body = document.getElementById("tel-body");
  if (!note || !body || !window.fetch) return;          /* no JS, no claim */
  var W = 720, H = 150, PL = 40, PR = 12, PT = 12, PB = 20, BASE = H - PB;
  var charts = [];

  function hhmm(sec) {   /* the VIEWER's clock, never ours */
    return new Date(sec * 1000).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});
  }
  /* a 24-hour window crosses midnight, and four bare clock labels cannot say
     which side of it a point is on — so the left-hand tick and every summary
     carry the date too. */
  function stamp(sec) {
    return new Date(sec * 1000).toLocaleString([], {month: "short", day: "numeric",
                                                    hour: "2-digit", minute: "2-digit"});
  }
  function ago(sec) {
    var m = Math.round(Date.now() / 1000 / 60 - sec / 60);
    if (m < 1) return "less than a minute";
    if (m < 60) return m + " min";
    return Math.floor(m / 60) + "h " + (m % 60) + "m";
  }
  function fmt(v, dec, unit) { return v == null ? "\\u2014" : v.toFixed(dec) + unit; }
  function last(a) { for (var i = a.length - 1; i >= 0; i--) if (a[i] != null) return a[i]; return null; }
  function peak(a) {
    var bi = -1, bv = null;
    for (var i = 0; i < a.length; i++) if (a[i] != null && (bv === null || a[i] > bv)) { bv = a[i]; bi = i; }
    return bi;
  }

  function chart(d, key, o) {
    var t = d.t, v = d[key], n = t.length, id = "tc-" + key;
    var t0 = t[0], span = Math.max(60, t[n - 1] - t0);
    var gap = (d.bucket_seconds || 60) * 3;
    function x(i) { return PL + (t[i] - t0) / span * (W - PL - PR); }
    function y(val) { return BASE - Math.max(0, Math.min(1, val / o.max)) * (BASE - PT); }
    /* segments: a hole in the data is a HOLE. Joining across one would draw
       utilisation for minutes the box was off. */
    var segs = [], cur = [], i;
    for (i = 0; i < n; i++) {
      if (v[i] == null || (i && t[i] - t[i - 1] > gap)) { if (cur.length) segs.push(cur); cur = []; }
      if (v[i] != null) cur.push(i);
    }
    if (cur.length) segs.push(cur);
    if (!segs.length) return "";
    var line = "", fill = "";
    segs.forEach(function (s) {
      var p = s.map(function (j, k) { return (k ? "L" : "M") + x(j).toFixed(1) + " " + y(v[j]).toFixed(1); }).join(" ");
      line += p + " ";
      if (s.length > 1) {
        fill += "M" + x(s[0]).toFixed(1) + " " + BASE + " " + p.slice(1) +
                " L" + x(s[s.length - 1]).toFixed(1) + " " + BASE + " Z ";
      }
    });
    var g = "";
    [0, 0.5, 1].forEach(function (f) {
      var yy = BASE - f * (BASE - PT);
      g += '<line class="grid" x1="' + PL + '" y1="' + yy.toFixed(1) + '" x2="' + (W - PR) +
           '" y2="' + yy.toFixed(1) + '"/><text class="axis" x="' + (PL - 6) + '" y="' +
           (yy + 3.5).toFixed(1) + '" text-anchor="end">' + (o.max * f).toFixed(o.tick) + '</text>';
    });
    [0, 1 / 3, 2 / 3, 1].forEach(function (f, k) {
      var xx = PL + f * (W - PL - PR);
      g += '<text class="axis" x="' + xx.toFixed(1) + '" y="' + (H - 6) + '" text-anchor="' +
           (k === 0 ? "start" : k === 3 ? "end" : "middle") + '">' +
           (k === 0 ? stamp(t0) : hhmm(t0 + f * span)) + '</text>';
    });
    var pi = peak(v), pm = "";
    if (pi >= 0) {
      var px = x(pi), py = y(v[pi]), rightish = px > (W + PL) / 2;
      pm = '<circle class="dot" cx="' + px.toFixed(1) + '" cy="' + py.toFixed(1) +
           '" r="3" fill="currentColor"/><text class="pk" x="' + (px + (rightish ? -7 : 7)).toFixed(1) +
           '" y="' + Math.max(PT + 8, py - 6).toFixed(1) + '" text-anchor="' +
           (rightish ? "end" : "start") + '">peak ' + fmt(v[pi], o.dec, o.unit) + '</text>';
    }
    charts.push({id: id, t: t, v: v, t0: t0, span: span, dec: o.dec, unit: o.unit,
                 dflt: (pi >= 0 ? "peak " + fmt(v[pi], o.dec, o.unit) + " at " + hhmm(t[pi]) +
                        " \\u00b7 point at the chart for any minute" : "")});
    return '<figure class="tchart ' + o.cls + '" id="' + id + '">' +
      '<figcaption><span>' + o.title + '</span><span class="cap">' + o.cap + '</span></figcaption>' +
      '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + o.title +
        ', ' + stamp(t0) + ' to ' + stamp(t[n - 1]) + ': latest ' + fmt(last(v), o.dec, o.unit) +
        ', peak ' + fmt(pi >= 0 ? v[pi] : null, o.dec, o.unit) + '">' + g +
      '<path class="fill" fill="currentColor" d="' + fill + '"/>' +
      '<path class="ln" stroke="currentColor" d="' + line + '"/>' + pm +
      '<line class="cross" x1="0" y1="' + PT + '" x2="0" y2="' + BASE + '" style="display:none"/>' +
      '<rect x="' + PL + '" y="' + PT + '" width="' + (W - PL - PR) + '" height="' + (BASE - PT) +
        '" fill="transparent"/></svg>' +
      '<div class="rdout">' + (charts[charts.length - 1].dflt) + '</div></figure>';
  }

  function tile(big, cap) {
    return '<div class="vital"><b>' + big + '</b><small>' + cap + '</small></div>';
  }

  function render(d) {
    var n = (d.t || []).length;
    var win = d.window_hours || 24;
    if (!n || !d.last_sample) {
      note.textContent = "no recent telemetry \\u2014 the render box has published a file " +
        "but it holds no samples from the last " + win + " hours.";
      return;
    }
    var stale = (Date.now() / 1000 - d.last_sample) > TEL_STALE * 60;
    var vmax = d.vram_total_gb || Math.max.apply(null, d.v.filter(function (x) { return x != null; })) * 1.1;
    var rmax = d.ram_total_gb || Math.max.apply(null, d.r.filter(function (x) { return x != null; })) * 1.1;
    var html = "";
    var pu = peak(d.up), pv = peak(d.v), pr = peak(d.r), pc = peak(d.c);
    html += '<div class="vitals">' +
      /* "peak sample", not "peak": this is the busiest single 10s reading, while
         the chart's peak marker is the busiest minute-AVERAGE. Two different true
         numbers; if both are called "peak" the page looks like it contradicts
         itself (it printed 100% here and 97% on the chart). */
      /* captions kept to four words: uppercase mono at this size wraps, and a
         caption that breaks mid-phrase ("VRAM IN USE · PEAK / 21.9 OF 23.9") reads
         as two half-labels. Each chart below states its own capacity anyway. */
      tile(fmt(last(d.u), 0, "%"), "gpu latest \\u00b7 peak sample " +
           fmt(pu >= 0 ? d.up[pu] : null, 0, "%")) +
      tile(fmt(last(d.v), 1, " GB"), "vram latest \\u00b7 peak " + fmt(pv >= 0 ? d.v[pv] : null, 1, " GB")) +
      tile(fmt(last(d.r), 1, " GB"), "ram latest \\u00b7 peak " + fmt(pr >= 0 ? d.r[pr] : null, 1, " GB")) +
      tile(fmt(pc >= 0 ? d.c[pc] : null, 1, " GB"), "commit peak \\u00b7 limit " +
           fmt(d.commit_limit_gb, 0, " GB")) +
      '</div>';
    html += chart(d, "u", {title: "GPU utilisation", cap: "% of the card, per minute",
                           max: 100, tick: 0, dec: 0, unit: "%", cls: "tel-gpu"});
    html += chart(d, "v", {title: "VRAM in use", cap: "GB of " + fmt(d.vram_total_gb, 1, " GB") + " on the card",
                           max: vmax, tick: 0, dec: 1, unit: " GB", cls: "tel-mem"});
    html += chart(d, "r", {title: "Host RAM in use", cap: "GB of " + fmt(d.ram_total_gb, 1, " GB") + " installed",
                           max: rmax, tick: 0, dec: 1, unit: " GB", cls: "tel-mem"});
    /* href set in JS, not concatenated into the markup: build_site.py's link
       checker reads every href in the output, and a spliced-together one reads to
       it as a broken local path (it caught exactly that, 2026-08-04). */
    var src = '<p class="whyfoot">straight from the machine: <a class="telsrc" href="#">telemetry.json</a>' +
      ' \\u2014 GPU by <code>nvidia-smi</code>, memory by <code>GlobalMemoryStatusEx</code>, sampled every ' +
      (d.sample_seconds || 10) + 's and averaged to one point a minute. Gaps are gaps: the line breaks ' +
      'wherever the box was not sampling.</p>';

    if (stale) {
      /* SITE.md: the site must not claim things it cannot know. A chart of
         yesterday under a heading about the render box reads as "now", so the
         plain sentence is the answer and the history is one click away, labelled
         with the hour it actually ends. */
      note.textContent = "no recent telemetry \\u2014 the newest sample from the render box is " +
        ago(d.last_sample) + " old (" + hhmm(d.last_sample) + " your time). The box may be off, " +
        "asleep, or unable to push; nothing here is claimed about it right now.";
      body.innerHTML = '<details class="drawer"><summary>show the ' + win +
        ' hours ending ' + stamp(d.last_sample) + '</summary><div class="drawer-body">' +
        html + src + '</div></details>';
    } else {
      note.textContent = (d.gpu_name || "the render box") + " \\u2014 newest sample " +
        hhmm(d.last_sample) + " your time (" + ago(d.last_sample) + " ago), " + win +
        "-hour window at one point a minute.";
      body.innerHTML = html + src;
    }
    body.hidden = false;
    var sa = body.querySelector(".telsrc");
    if (sa) sa.href = TEL_URL;
    charts.forEach(function (c) {
      var fig = document.getElementById(c.id);
      if (!fig) return;
      var svg = fig.querySelector("svg"), cross = fig.querySelector(".cross"),
          out = fig.querySelector(".rdout");
      function clear() { cross.style.display = "none"; out.textContent = c.dflt; }
      svg.addEventListener("pointermove", function (e) {
        var r = svg.getBoundingClientRect();
        var f = ((e.clientX - r.left) / r.width * W - PL) / (W - PL - PR);
        var want = c.t0 + Math.max(0, Math.min(1, f)) * c.span, bi = -1, bd = Infinity;
        for (var i = 0; i < c.t.length; i++) {
          var dist = Math.abs(c.t[i] - want);
          if (dist < bd) { bd = dist; bi = i; }
        }
        if (bi < 0 || c.v[bi] == null) return clear();
        var px = PL + (c.t[bi] - c.t0) / c.span * (W - PL - PR);
        cross.setAttribute("x1", px.toFixed(1));
        cross.setAttribute("x2", px.toFixed(1));
        cross.style.display = "";
        out.innerHTML = hhmm(c.t[bi]) + " \\u00b7 <b>" + fmt(c.v[bi], c.dec, c.unit) + "</b>";
      });
      svg.addEventListener("pointerleave", clear);
    });
  }

  /* per-minute cache key: raw.githubusercontent sits behind a CDN, and a status
     page that shows a five-minute-old copy of a five-minute-old file is stale
     twice over. */
  fetch(TEL_URL + "?_=" + Math.floor(Date.now() / 60000), {cache: "no-store"})
    .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(render)
    .catch(function (e) {
      note.textContent = "no recent telemetry \\u2014 the render box's published file could not " +
        "be read (" + e.message + "), so nothing is being claimed about the machine.";
    });
})();
"""


SIM_CSS = """
/* ---- the lot: one living scene — sky, street, crew (tokens from the theme).
   All motion is transform-only on a handful of small elements, paused when the
   tab is hidden (body.away) and killed entirely under prefers-reduced-motion —
   the 2026-07-31 GPU lesson applies to every new animation on this page. ---- */
.lot { position: relative; height: 230px; overflow: hidden; border-radius: 18px;
  border: 1px solid var(--line-soft); margin: .5rem 0 .4rem;
  background:
    radial-gradient(460px 150px at 72% 0%, var(--bg-glow), transparent 70%),
    linear-gradient(180deg, transparent 73%, var(--panel-2) 73%); }
.lot .stars { position: absolute; top: 12px; left: 28%; letter-spacing: 4vw;
  color: var(--leaf-dim); font-size: .8rem; }
.lot .sun { position: absolute; top: 12px; left: 5%; text-align: center;
  font-size: 1.5rem; line-height: 1; }
.lot .cloud { position: absolute; top: 12px; right: 5%; text-align: center;
  font-size: 1.7rem; line-height: 1;
  animation: drift 48s ease-in-out infinite alternate; }
.lot .sun small, .lot .cloud small { display: block; font: 600 .58rem/1.5 var(--mono);
  color: var(--faint); }
@keyframes drift { from { transform: translateX(0) } to { transform: translateX(-64px) } }
.street { position: absolute; left: 0; right: 0; bottom: 27%; display: flex;
  justify-content: space-evenly; align-items: flex-end; }
.lot-bld { position: relative; text-align: center; }
.lot-bld .ico { display: block; font-size: clamp(1.7rem, 6vw, 2.4rem);
  line-height: 1.15; text-decoration: none; }
.lot-bld .btag { display: block; font: 600 .58rem/1.4 var(--mono); color: var(--faint); }
.lot-bld.working .ico { filter: drop-shadow(0 0 10px rgba(255,199,106,.8)); }
.lot-bld.working .btag { color: var(--sap); }
.lot-bld.idle { opacity: .85; }
.lot-bld.asleep { opacity: .45; filter: grayscale(.8); }
.lot-bld .smoke { position: absolute; top: -1.1rem; left: 0; right: 0; }
.lot-tree .ico { font-size: clamp(2.4rem, 8vw, 3.1rem); }
.walker { position: absolute; bottom: 8px; left: var(--lo); z-index: 3; text-align: center;
  animation: cross var(--d) linear var(--delay) infinite alternate; }
@keyframes cross { from { transform: translateX(0) } to { transform: translateX(min(58vw, 400px)) } }
.walker .spr { display: block; font-size: 1.35rem; line-height: 1.2;
  /* most emoji people face left, so the rightward leg wears the flip */
  animation: face calc(var(--d) * 2) steps(1) var(--delay) infinite; }
@keyframes face { 0%, 100% { transform: scaleX(-1) } 50% { transform: scaleX(1) } }
.walker .spr i { display: inline-block; font-style: normal;
  animation: bob .55s ease-in-out infinite alternate; }
@keyframes bob { from { transform: translateY(0) } to { transform: translateY(-3px) } }
.walker .wtag { display: block; font: 600 .58rem/1.4 var(--mono); color: var(--faint);
  background: var(--panel); border: 1px solid var(--line-soft); border-radius: 999px;
  padding: .06rem .4rem; white-space: nowrap; }
.machlist { list-style: none; padding: 0; margin: .5rem 0 0; }
.machlist li { padding: .45rem 0; border-bottom: 1px solid var(--line-soft);
  font-size: .92rem; }
.machlist li:last-child { border-bottom: 0; }
.machlist .mico { margin-right: .3rem; }
.grove { text-align: center; margin: 0 0 1.2rem; }
.canopy { display: grid; grid-template-columns: repeat(5, 2.1rem); gap: .1rem;
  justify-content: center; }
.leaf { font-size: 1.45rem; text-decoration: none; }
.leaf.bud { filter: grayscale(1) brightness(.5); }
.trunky { font-size: 4.4rem; line-height: 1; }
.grove .label { font: 600 .8rem/1.6 var(--mono); color: var(--muted); }
.smoke { height: 1.1rem; animation: puff 2.4s linear infinite; }
/* an infinite animation keeps the compositor running FOREVER, in every
   open tab — this page is meant to be left open, so it must go quiet
   when nobody is looking (founder's Mac, 2026-07-31: a Chrome GPU
   process at 100% of a core for 13 hours). */
body.away .smoke, body.away .lot .cloud,
body.away .walker, body.away .walker * { animation: none !important; }
@keyframes puff { 0% { opacity: .9; transform: translateY(0) } 100% { opacity: 0; transform: translateY(-11px) } }
.spend { font: 600 .8rem/1.6 var(--mono); color: var(--faint); text-align: center; }
.spend b { color: var(--sap); }
.scenes, .quests { list-style: none; padding: 0; margin: .4rem 0 0; }
.scenes li, .quests li { padding: .55rem 0; border-bottom: 1px solid var(--line-soft); }
.scenes li:last-child, .quests li:last-child { border-bottom: 0; }
.mono { font: 500 .76rem/1.6 var(--mono); color: var(--faint); }
.scroll { overflow-x: auto; }
.citizens { display: flex; flex-wrap: wrap; gap: .6rem; justify-content: center; }
.citizen { flex: 1 1 45%; max-width: 210px; text-align: center; }
.citizen .bubble { display: block; background: var(--panel-2); border: 1px solid var(--line);
  color: var(--ink); border-radius: 12px; padding: .45rem .6rem; font-size: .78rem;
  text-align: left; }
.citizen .spr { font-size: 1.7rem; line-height: 1.4; }
.citizen small { font: 600 .7rem/1.4 var(--mono); color: var(--faint); display: block; }
.summary { font: 600 .84rem/1.7 var(--mono); color: var(--muted); }
.summary b { color: var(--leaf); }
.prod-row { background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 14px; padding: .7rem .95rem;
  margin: .6rem 0; font-size: .92rem; }
.prod-row .why { color: var(--muted); font-size: .84rem; }
.whyfoot { font: 500 .8rem/1.7 var(--mono); color: var(--faint); }

/* ---- vitals: the four numbers a visitor can check against the repo ---- */
.vitals { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: .6rem; margin: .9rem 0 .4rem; }
.vital { text-align: center; padding: .75rem .5rem .6rem; border: 1px solid var(--line);
  border-radius: 14px; background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.vital b { display: block; font: 600 1.6rem/1.15 var(--display); color: var(--ink);
  font-variant-numeric: tabular-nums; }
.vital small { font: 600 .68rem/1.5 var(--mono); color: var(--faint);
  letter-spacing: .05em; text-transform: uppercase; }

/* ---- the growth meter: two file-existence facts per scene, nothing else ---- */
.growbar { height: 12px; max-width: 420px; margin: .7rem auto .35rem; overflow: hidden;
  border: 1px solid var(--line); border-radius: 999px; background: var(--code-bg); }
.growbar i { display: block; height: 100%; background: var(--sap); border-radius: 999px; }

/* leaf tiers — the tooltip carries the words, the tint is only a hint */
.leaf.pick { filter: none; text-decoration: none;
  text-shadow: 0 0 10px rgba(255,199,106,.9); }
.leaf.still { filter: saturate(.6); }

/* ---- the quest board: real open requests, real reward, no points ---- */
.qboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: .7rem; margin: .8rem 0 .4rem; }
.quest { padding: .8rem .95rem .7rem; border: 1px solid var(--line); border-radius: 14px;
  background: linear-gradient(180deg, var(--panel-2), var(--panel)); font-size: .92rem; }
.quest b { font-family: var(--display); font-size: 1.02rem; }
.quest p { margin: .35rem 0 .45rem; color: var(--muted); font-size: .86rem; }
.quest .reward { font: 500 .72rem/1.5 var(--mono); color: var(--faint);
  border-top: 1px dashed var(--line-soft); padding-top: .45rem; margin-top: .2rem; }
.reward b { font: 700 .72rem/1.5 var(--mono); color: var(--sap); }
.quest.slim { display: flex; flex-direction: column; gap: .3rem; align-items: flex-start; }
.quest.slim .chip { margin: 0; }
.qnote { background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 14px; padding: .7rem .95rem;
  font-size: .9rem; color: var(--muted); }
.qnote .reward { display: block; border-top: 1px dashed var(--line-soft);
  padding-top: .4rem; margin-top: .5rem; font: 500 .72rem/1.5 var(--mono);
  color: var(--faint); }

/* ---- milestones: unlocked = a repo fact; locked = the honest gap ---- */
.badges { display: flex; flex-wrap: wrap; gap: .6rem; justify-content: center;
  margin: .8rem 0 .3rem; }
.badge { flex: 1 1 45%; max-width: 168px; text-align: center; padding: .7rem .55rem .6rem;
  border: 1px solid var(--line); border-radius: 14px;
  background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.badge .ico { font-size: 1.9rem; line-height: 1.2; }
.badge .nm { font: 700 .74rem/1.35 var(--mono); margin: .15rem 0 .1rem; }
.badge .cap { font: 500 .68rem/1.5 var(--mono); color: var(--faint); }
.badge.locked { opacity: .5; filter: grayscale(1); border-style: dashed; }
.badge.locked .nm::after { content: " · locked"; color: var(--faint); font-weight: 500; }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; } }
"""


# only build once per output directory: build_site.py calls build_status.build()
# (which delegates here) and then build_sim.build(), and each pass would hit the
# GitHub API again for the same snapshot.
_BUILT = set()


def build(out_dir: Path):
    import build_status as data
    out_dir = Path(out_dir)
    if str(out_dir.resolve()) in _BUILT:
        return
    rows = data.scenes()
    tot = data.summary(rows)
    hero = data.hero()
    spend, inbox = data.spend(), data.inbox()
    grow = data.growth(rows)
    takes = data.takes_tally()
    open_quests = sum(1 for r in rows if r["request"]) + 2  # + the standing two

    # --- the grove: 15 leaves, each one an actual scene you can go look at.
    # Four tiers a glance can tell apart; the tooltip carries the exact words.
    leaves = ""
    for r in rows:
        if r["final"] and r["animations"]:
            cls, glyph, stage = "grown", "🍃", "fully grown — frame approved and animated"
        elif r["final"]:
            cls, glyph, stage = "grown still", "🌿", "frame approved — not yet animated"
        elif r["candidates"]:
            cls, glyph, stage = ("pick", "🌱", f'sprouting — {r["candidates"]} frames '
                                 "wait for the author's pick")
        else:
            cls, glyph, stage = "bud", "🍃", "a bud — waiting for a render"
        leaves += (f'<a class="leaf {cls}" href="{_e(hero["board"])}#beat-{r["num"]:02d}" '
                   f'title="Scene {r["num"]:02d} — {_e(r["name"])} · {_e(stage)}">{glyph}</a>')
    done = tot["final"] == tot["total"]
    pct = round(100 * grow["done"] / grow["total"]) if grow["total"] else 0
    grove_caption = (f'Episode {hero["number"]} — '
                     + (f'all {tot["total"]} scene frames approved. '
                        if done else f'{tot["final"]} of {tot["total"]} scene frames approved. ')
                     + f'<a href="{_e(hero["page"])}">Watch it &rarr;</a>')
    # role="img" + aria-label: the bar itself is decoration, the numbers are the fact
    growbar = (f'<div class="growbar" role="img" aria-label="{grow["done"]} of '
               f'{grow["total"]} growth steps done"><i style="width:{pct}%"></i></div>'
               f'<div class="label"><b>{pct}% grown</b> — {grow["done"]} of {grow["total"]} '
               'growth steps. A scene grows twice: its frame is approved, then it is animated.</div>')

    # --- the lot: our machines as buildings on one street, crew walking it ---
    queue = queue_tasks()
    bldgs, machlist, seen_states = "", "", []
    for b in farm_branches():
        key = b.split("farm-results-")[-1]
        nice, emoji = MACHINES.get(key, (key, "🏠"))
        state, cap, raw = machine_state(branch_heartbeat(b), queue)
        seen_states.append(state)
        smoke = '<div class="smoke">💨</div>' if state == "working" else ""
        bldgs += (f'<div class="lot-bld {state}" title="{_e(nice)} — {_e(cap)}">{smoke}'
                  f'<span class="ico">{emoji}</span><span class="btag">{_e(nice)}</span></div>')
        machlist += (f'<li><span class="mico">{emoji}</span> <b>{_e(nice)}</b> — '
                     f'<span class="mono">{_e(cap)}</span></li>')
    bldgs += (f'<div class="lot-bld lot-tree"><a class="ico" href="{_e(hero["page"])}" '
              f'title="Episode {hero["number"]} — {pct}% grown">🌳</a>'
              f'<span class="btag">episode {hero["number"]} · {pct}%</span></div>')
    day = data.day_count()
    sun = (f'<div class="sun">☀️<small>day {day} of production</small></div>'
           if day else "")
    comments = latest_thread_comments()
    lot = (f'<div class="lot">{sun}'
           '<div class="stars" aria-hidden="true">✦ ✧ ✦ ✧ ✦</div>'
           '<div class="cloud">☁️<small>cloud GPU — standing by (unused)</small></div>'
           f'<div class="street">{bldgs}</div>'
           f'{walkers_html(comments, "working" in seen_states)}</div>')

    # --- what is being rendered, and why (founder, 2026-07-30) ---
    prod_rows = ""
    for t in merge_queue(queue):
        what, why = task_story(t)
        wkey = str(t.get("worker", "any"))
        wnice = MACHINES.get(wkey, (wkey, "🏠"))[0]
        prod_rows += (f'<div class="prod-row"><b>{_e(wnice)}</b> · {_e(what)}'
                      f'<br><span class="why">{_e(why)}</span></div>')
    # NOT "right now". This page is a static file built at deploy time, and on
    # 2026-08-02 it sat five hours out of date under a heading that asserted it was
    # current. A snapshot may be late; it must not lie about being live.
    production = (f'<h2>🏭 In production, as of this snapshot</h2>{prod_rows}'
                  '<p class="whyfoot">Finished frames land on each machine\'s courier branch, '
                  'get checked, and show up as choices on the '
                  '<a href="sapling/001-capability-inventory-shots.html">shot board</a> — '
                  'the author (and anyone watching) picks what survives.</p>'
                  ) if prod_rows else ""
    town_legend = " · ".join(STATE_WORDS[s] for s in STATE_WORDS if s in seen_states) \
        or "no machine has checked in yet"

    citizens = "".join(
        f'<div class="citizen"><a class="bubble" href="{_e(url)}">{_e(said)}</a>'
        f'<div class="spr">{"🧑‍🌾" if i % 2 else "🧙"}</div><small>{_e(who)}</small></div>'
        for i, (who, said, url) in enumerate(comments))
    if not citizens:
        citizens = '<p class="notice">The reactions thread is quiet right now.</p>'

    player = (f'<figure class="phone"><video controls playsinline preload="metadata" '
              f'poster="{_e(hero["poster"])}" src="{_e(hero["video"])}"></video>'
              f'<figcaption>Episode {hero["number"]} · “{_e(hero["title"])}” — '
              f'the working cut — {tot["final"]}/{tot["total"]} scene frames approved, '
              f'awaiting the author’s pass</figcaption></figure>'
              ) if hero["video"] else (
        f'<p><a class="btn" href="{_e(hero["watch"])}">▶ Watch episode {hero["number"]} &rarr;</a></p>')

    waiting = (f'{tot["awaiting_render"]} waiting on a render · '
               f'{tot["awaiting_pick"]} waiting on the author to pick')

    # --- vitals: four numbers, each one checkable against the repo ---
    vitals = (
        f'<div class="vitals">'
        f'<div class="vital"><b>{pct}%</b><small>episode grown</small></div>'
        f'<div class="vital"><b>{takes["stills"] + takes["clips"]}</b>'
        f'<small>takes handed in</small></div>'
        f'<div class="vital"><b>{open_quests}</b><small>open quests</small></div>'
        f'<div class="vital"><b>${spend:.2f}</b><small>spent, lifetime</small></div>'
        f'</div>')

    # --- milestones: unlocked = a repo fact, locked = the honest gap ---
    all_moving = all(r["animations"] for r in rows)
    vo = data.vo_scenes()
    passed = data.cut_passed()
    picking = next((r for r in rows if not r["final"]), None)
    milestones = [
        ("🌱", "Scripted", bool(rows),
         f'{tot["total"]} scenes written; the script approved by the author'),
        ("🖼", "Every frame approved", done,
         f'all {tot["total"]} scene frames carry the author\'s pick' if done else
         (f'{tot["final"]} of {tot["total"]} — scene {picking["num"]:02d} still choosing'
          if picking else f'{tot["final"]} of {tot["total"]}')),
        ("🔊", "Narration recorded", vo > 0,
         f"{vo} scenes carry recorded voice-over" if vo else "no voice lines recorded yet"),
        ("🎞", "Every scene moves", all_moving,
         "a moving take exists for all scenes" if all_moving else
         f'{sum(1 for r in rows if r["animations"])} of {tot["total"]} scenes have one'),
        ("🎬", "A full cut assembled", bool(hero["video"]),
         "playing at the top of this page" if hero["video"] else "no full cut yet"),
        ("🏆", "The author passes the cut", passed,
         "the cut is canon" if passed else
         "the last gate — only the author can open it"),
    ]

    out = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{_e(DESC)}">
<link rel="canonical" href="{CANONICAL}/{PAGE}">
<link rel="alternate" type="application/rss+xml" title="new nodes" href="{CANONICAL}/feed.xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Banyan City">
<meta property="og:title" content="Banyan City — {PAGE_NAME}">
<meta property="og:description" content="{_e(DESC)}">
<meta property="og:url" content="{CANONICAL}/{PAGE}">
<meta property="og:image" content="{CANONICAL}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Banyan City — {PAGE_NAME}">
<meta name="twitter:description" content="{_e(DESC)}">
<meta name="twitter:image" content="{CANONICAL}/og.png">
<title>Banyan City — {PAGE_NAME}</title>
<style>{THEME_CSS}{SIM_CSS}{TEL_CSS}</style>
</head>
<body>
<main>
<nav class="crumbs"><a href="index.html">🌳 banyan-city</a> · <a href="watch.html">▶ watch</a>
 · <a href="city.html">the city</a> · <a href="machine.html">⚙️ how it works</a>
 · <b>🏗 {PAGE_NAME}</b> · <a href="https://github.com/{GH}">source</a></nav>

<div class="rise">
<p class="eyebrow">Banyan City · {PAGE_NAME}</p>
<h1>{PAGE_NAME.title()}</h1>
<p class="lede">{data.PITCH}</p>
</div>

<div class="rise">
{player}
<p style="text-align:center">
  <a class="btn" href="{_e(hero["watch"])}">▶ Watch episode {hero["number"]}</a>
  <a class="btn ghost" href="{_e(hero["board"])}">🎬 See how it was made</a>
</p>
<p class="spend">total spent on renders so far: <b>${spend:.2f}</b> —
everything else runs on the family's own machines for free</p>
{vitals}
</div>

<h2 class="rise">The episode, growing</h2>
<div class="grove rise">
  <div class="canopy">{leaves}</div>
  <div class="trunky"><a href="{_e(hero["page"])}" title="Episode {hero["number"]}">🌳</a></div>
  {growbar}
  <div class="label">{grove_caption}</div>
</div>

<h2>Milestones</h2>
{badges_html(milestones)}
<p class="legend">an unlocked milestone is a fact you can check in the repo ·
a locked one is exactly what remains</p>

<h2>The lot — the studio at work</h2>
{lot}
<ul class="machlist">{machlist}</ul>
<p class="legend">{town_legend}</p>
{production}

<h2>🏟 The render box, minute by minute</h2>
<section id="tel">
<p class="telnote" id="tel-note">no recent telemetry — these charts are drawn in your browser
from a file the render box publishes about itself every five minutes. If this line is still
here, that file has not been read yet (or JavaScript is off, in which case this page will not
guess what the machine is doing).</p>
<div id="tel-body" hidden></div>
</section>

<h2>🗺 Open quests — anyone can take one</h2>
<p style="margin:.2rem 0 .4rem;color:var(--muted)">Nothing here is play-pretend: every art
quest is a real open request from the author, and every take handed in becomes part of the
show's public record.</p>
{quest_board_html(rows)}
<p class="whyfoot">every quest lands on the
<a href="{_e(hero["board"])}">scene-by-scene shot board</a> — the whole workshop is public</p>

<h2>Every scene, and what it is waiting for</h2>
<p class="summary"><b>{tot["final"]} of {tot["total"]} scene frames approved</b> —
the assembled episode is a working cut until the author passes it · {waiting}</p>
<details class="drawer"><summary>Open the scene-by-scene list</summary>
<div class="drawer-body">{scene_list_html(rows)}</div></details>

<h2>How long each step takes (and what it costs)</h2>
{steps_table_html(data.STEPS)}

<details class="drawer"><summary>The author's own quest log — read-only</summary>
<div class="drawer-body">
<p class="mono">These are calls only the author can make; the rest of the city keeps moving while
they wait.</p>
{quests_html(inbox)}</div></details>

<h2>People on the reactions thread</h2>
<div class="citizens">{citizens}</div>
<p style="text-align:center"><a href="https://github.com/{GH}/issues/1">join them &rarr;</a></p>

<p class="legend">{data.LEGEND}</p>
<footer>snapshot {time.strftime('%Y-%m-%d %H:%M', time.gmtime())}Z · this page is a static
file: it shows the queue at BUILD time and cannot update itself — rebuilt on every push
and every half hour · the render-box charts are the one exception, fetched live by your
browser · the whole repo IS the show —
<a href="index.html">the city</a> · <a href="lab/index.html">the lab</a> ·
<a href="machine.html">how it works</a></footer>
</main>
<script>
/* pause every animation while the tab is hidden. */
document.addEventListener("visibilitychange", function () {{
  document.body.classList.toggle("away", document.hidden);
}});
var TEL_URL = {json.dumps(TELEMETRY_URL)}, TEL_STALE = {TELEMETRY_STALE_MINUTES};
{TEL_JS}
</script>
</body>
</html>"""
    (out_dir / "status.html").write_text(out)
    # sim.html is a permanent redirect target only — "the sim" is a dev codeword.
    (out_dir / "sim.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta http-equiv="refresh" content="0;url=status.html">'
        '<link rel="canonical" href="https://banyan.city/status.html">'
        '<title>Banyan City — the studio</title></head><body>'
        '<p>This page moved: <a href="status.html">the studio &rarr;</a></p>'
        '</body></html>')
    _BUILT.add(str(out_dir.resolve()))
    print(f"✓ status.html (the studio) — {tot['final']}/{tot['total']} scenes final, "
          f"{len(seen_states)} machines")


if __name__ == "__main__":
    build(REPO / "_site")
