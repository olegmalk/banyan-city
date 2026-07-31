#!/usr/bin/env python3
"""banyan city, THE STUDIO — one page that shows the show being made.

Dad asked for the sim (2026-07-30) and it stays: the episode is a tree growing
leaves, our machines are buildings that glow while they render, the cloud GPU is
a cloud, the author's open decisions are quests, the people voting on the
reactions thread are citizens. Pure CSS + emoji — the public-site CSP allows no
external asset, and nothing here needs JavaScript.

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


def task_story(t: dict) -> tuple:
    """(what, why) in a stranger's words, from a queue task's own fields."""
    tid = str(t.get("id", ""))
    beats = str(t.get("beats") or "").strip()
    shots = f"shots {beats.replace(',', ', ')}" if beats else "world scenery"
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


SIM_CSS = """
/* ---- the studio, drawn as a town (page-specific; tokens from the theme) ---- */
.sky { position: relative; height: 92px; overflow: hidden; border-radius: 18px;
  border: 1px solid var(--line-soft); margin: .4rem 0 -.6rem;
  background: radial-gradient(420px 120px at 70% 120%, var(--bg-glow), transparent 70%); }
.sky::after { content: "✦ ✧ ✦ ✧ ✦"; position: absolute; top: 10px; left: 8%;
  letter-spacing: 4.5vw; color: var(--leaf-dim); font-size: .8rem; }
.cloudgpu { position: absolute; right: 6%; top: 12px; text-align: center; font-size: 1.9rem;
  line-height: 1; }
.cloudgpu small { display: block; font: 600 .62rem/1.5 var(--mono); color: var(--faint);
  letter-spacing: .04em; }
.grove { text-align: center; margin: 0 0 1.2rem; }
.canopy { display: grid; grid-template-columns: repeat(5, 2.1rem); gap: .1rem;
  justify-content: center; }
.leaf { font-size: 1.45rem; text-decoration: none; }
.leaf.bud { filter: grayscale(1) brightness(.5); }
.trunky { font-size: 4.4rem; line-height: 1; }
.grove .label { font: 600 .8rem/1.6 var(--mono); color: var(--muted); }
.town { display: flex; flex-wrap: wrap; gap: .7rem; justify-content: center; margin: 1rem 0 .5rem; }
.bld { flex: 1 1 45%; max-width: 200px; text-align: center; padding: .7rem .6rem;
  border: 1px solid var(--line); border-radius: 14px;
  background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
.bld .ico { font-size: 2.3rem; line-height: 1.1; }
.bld .nm { font: 700 .78rem/1.4 var(--mono); }
.bld .cap { font: 500 .72rem/1.45 var(--mono); color: var(--faint); min-height: 2.2em; }
.bld.working { border-color: var(--sap); box-shadow: 0 0 22px -6px rgba(255,199,106,.45); }
.bld.working .nm { color: var(--sap); }
.bld.idle { opacity: .9; }
.bld.asleep { opacity: .5; filter: grayscale(.7); }
.smoke { height: 1.1rem; animation: puff 2.4s linear infinite; }
/* an infinite animation keeps the compositor running FOREVER, in every
   open tab — this page is meant to be left open, so it must go quiet
   when nobody is looking (founder's Mac, 2026-07-31: a Chrome GPU
   process at 100% of a core for 13 hours). */
body.away .smoke, body.away .cloudgpu { animation: none !important; }
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
@media (min-width: 620px) { .bld { flex: 0 1 180px; } }
.prod-row { background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--line); border-radius: 14px; padding: .7rem .95rem;
  margin: .6rem 0; font-size: .92rem; }
.prod-row .why { color: var(--muted); font-size: .84rem; }
.whyfoot { font: 500 .8rem/1.7 var(--mono); color: var(--faint); }
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

    # --- the grove: 15 leaves, each one an actual scene you can go look at ---
    leaves = "".join(
        f'<a class="leaf {"grown" if r["final"] else "bud"}" '
        f'href="{_e(hero["board"])}#beat-{r["num"]:02d}" '
        f'title="Scene {r["num"]:02d} — {_e(r["name"])} · '
        f'{"frame approved" if r["final"] else "waiting for " + r["waiting_for"]}">🍃</a>'
        for r in rows)
    done = tot["final"] == tot["total"]
    grove_caption = (f'Episode {hero["number"]} — '
                     + (f'all {tot["total"]} scene frames approved. '
                        if done else f'{tot["final"]} of {tot["total"]} scene frames approved. ')
                     + f'<a href="{_e(hero["page"])}">Watch it &rarr;</a>')

    # --- the town: our machines, in sentences a stranger can read ---
    queue = queue_tasks()
    town, seen_states = "", []
    for b in farm_branches():
        key = b.split("farm-results-")[-1]
        nice, emoji = MACHINES.get(key, (key, "🏠"))
        state, cap, raw = machine_state(branch_heartbeat(b), queue)
        seen_states.append(state)
        smoke = '<div class="smoke">💨</div>' if state == "working" else ""
        town += (f'<div class="bld {state}" title="{_e(raw)}">{smoke}'
                 f'<div class="ico">{emoji}</div><div class="nm">{_e(nice)}</div>'
                 f'<div class="cap">{_e(cap)}</div></div>')

    # --- what is being rendered, and why (founder, 2026-07-30) ---
    prod_rows = ""
    for t in queue:
        what, why = task_story(t)
        wkey = str(t.get("worker", "any"))
        wnice = MACHINES.get(wkey, (wkey, "🏠"))[0]
        prod_rows += (f'<div class="prod-row"><b>{_e(wnice)}</b> · {_e(what)}'
                      f'<br><span class="why">{_e(why)}</span></div>')
    production = (f'<h2>🏭 In production right now</h2>{prod_rows}'
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
        for i, (who, said, url) in enumerate(latest_thread_comments()))
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
<style>{THEME_CSS}{SIM_CSS}</style>
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
</div>

<h2 class="rise">The episode, growing</h2>
<div class="grove rise">
  <div class="canopy">{leaves}</div>
  <div class="trunky"><a href="{_e(hero["page"])}" title="Episode {hero["number"]}">🌳</a></div>
  <div class="label">{grove_caption}</div>
</div>

<h2>The machines</h2>
<div class="sky"><div class="cloudgpu">☁️<small>cloud GPU — standing by (unused)</small></div></div>
<div class="town">{town}</div>
<p class="legend">{town_legend}</p>
{production}

<div class="panel" style="padding:1rem 1.2rem;margin:1.6rem 0">
  <h2 style="margin:.1rem 0 .4rem">Take part</h2>
  <p style="margin:.2rem 0 .8rem;color:var(--muted)">Nothing here is locked. Pick a scene,
  make a better version of it, and hand it in — or write the next episode yourself.</p>
  <p><a class="btn ghost" href="{_e(hero["board"])}">🎬 Scene-by-scene shot board</a>
     <a class="btn ghost" href="create.html">✍️ Write your own episode</a>
     <a class="btn ghost" href="https://github.com/{GH}/issues/1">💬 Say what you think</a></p>
</div>

<h2>Every scene, and what it is waiting for</h2>
<p class="summary"><b>{tot["final"]} of {tot["total"]} scene frames approved</b> —
the assembled episode is a working cut until the author passes it · {waiting}</p>
<details class="drawer"><summary>Open the scene-by-scene list</summary>
<div class="drawer-body">{scene_list_html(rows)}</div></details>

<h2>How long each step takes (and what it costs)</h2>
{steps_table_html(data.STEPS)}

<details class="drawer"><summary>What the author still has to decide — read-only</summary>
<div class="drawer-body">
<p class="mono">These are calls only the author can make; the rest of the city keeps moving while
they wait.</p>
{quests_html(inbox)}</div></details>

<h2>People on the reactions thread</h2>
<div class="citizens">{citizens}</div>
<p style="text-align:center"><a href="https://github.com/{GH}/issues/1">join them &rarr;</a></p>

<p class="legend">{data.LEGEND}</p>
<footer>snapshot {time.strftime('%Y-%m-%d %H:%M')} · rebuilt on every push · the whole repo IS the show —
<a href="index.html">the city</a> · <a href="lab/index.html">the lab</a> ·
<a href="machine.html">how it works</a></footer>
</main>
<script>
/* pause every animation while the tab is hidden. */
document.addEventListener("visibilitychange", function () {{
  document.body.classList.toggle("away", document.hidden);
}});
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
