#!/usr/bin/env python3
"""Static-site generator — Phase 1: the tree becomes visible.

Reads every genome under genomes/ and renders _site/:
    index.html                the city gate: lineage tree, explorable
    city.html                 Promise + Guidelines + Vocabulary
    <genome>/<slug>.html      one page per node: script, leaves, sap

Design constraints:
  - no build framework, no client JS required, no external assets
  - works for any genome that passes lint_genome.py (a fork changes
    content, not this script)
  - a non-git citizen can read the story and react (Phase 1 acceptance)
"""

import html
import os
import re
import shutil
from pathlib import Path

import markdown
import yaml

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_site"
# Forkable: in CI GITHUB_REPOSITORY names the fork; locally fall back to origin
GH_REPO = os.environ.get("GITHUB_REPOSITORY", "olegmlkvorg/banyan-city")
REPO_URL = f"https://github.com/{GH_REPO}"
REPO_NAME = GH_REPO.split("/")[-1]
CANONICAL = "https://banyan.city"  # canonical host; Pages stays as free mirror
MD = markdown.Markdown(extensions=["tables", "fenced_code"])

CSS = """
:root {
  --bg: #0e1410; --panel: #151d17; --ink: #e6efe8; --muted: #93a698;
  --leaf: #6fce8a; --leaf-dim: #2e5c3d; --amber: #e8b464; --line: #263529;
  --code-bg: #0a0f0b;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg: #f6f8f4; --panel: #ffffff; --ink: #1d2a20; --muted: #5b6f60;
    --leaf: #1e7a3f; --leaf-dim: #bcd9c5; --amber: #a06510; --line: #d8e2da;
    --code-bg: #eef2ec;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink);
  font: 17px/1.65 Georgia, 'Times New Roman', serif; }
main { max-width: 720px; margin: 0 auto; padding: 2rem 1.25rem 5rem; }
a { color: var(--leaf); text-decoration: none; }
a:hover { text-decoration: underline; }
h1, h2, h3 { line-height: 1.25; font-weight: 600; }
h1 { font-size: 1.9rem; margin: 0.5rem 0; }
hr { border: 0; border-top: 1px solid var(--line); margin: 2rem 0; }
blockquote { margin: 1rem 0; padding: 0.1rem 1.1rem; border-left: 3px solid var(--leaf-dim);
  color: var(--muted); background: var(--panel); border-radius: 0 8px 8px 0; }
code, pre { font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace; font-size: 0.85em; }
pre { background: var(--code-bg); border: 1px solid var(--line); border-radius: 8px;
  padding: 0.9rem 1.1rem; overflow-x: auto; color: var(--leaf); }
table { border-collapse: collapse; width: 100%; font-size: 0.92em; display: block; overflow-x: auto; }
th, td { border: 1px solid var(--line); padding: 0.45rem 0.7rem; text-align: left; }
th { background: var(--panel); }
.crumbs { font-size: 0.85rem; color: var(--muted); margin-bottom: 1.5rem;
  font-family: ui-monospace, Menlo, monospace; }
.chip { display: inline-block; font: 600 0.72rem/1 ui-monospace, Menlo, monospace;
  padding: 0.3rem 0.55rem; border-radius: 999px; border: 1px solid var(--line);
  color: var(--muted); vertical-align: middle; margin-right: 0.35rem; }
.chip.hot { color: var(--amber); border-color: var(--amber); }
.chip.trunk { color: var(--leaf); border-color: var(--leaf); }
.tree { list-style: none; padding-left: 0; margin: 1.5rem 0; }
.tree ul { list-style: none; padding-left: 1.4rem; border-left: 2px solid var(--leaf-dim); margin-left: 0.9rem; }
.tree li { margin: 0.8rem 0; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
  padding: 0.9rem 1.1rem; }
.card .title { font-size: 1.1rem; font-weight: 600; }
.card .teaser { color: var(--muted); font-size: 0.92rem; margin: 0.35rem 0 0.5rem; }
.card .meta { font-size: 0.85rem; }
.hero { text-align: center; margin: 2.5rem 0 3rem; }
.hero .seal { font-size: 2.6rem; }
.hero p { color: var(--muted); max-width: 34em; margin: 0.8rem auto; }
.btn { display: inline-block; background: var(--leaf); color: var(--bg); font-weight: 700;
  padding: 0.6rem 1.2rem; border-radius: 10px; margin: 0.3rem; }
.btn:hover { text-decoration: none; opacity: 0.9; }
.btn.ghost { background: transparent; color: var(--leaf); border: 1px solid var(--leaf); }
footer { margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid var(--line);
  color: var(--muted); font-size: 0.85rem; text-align: center; }
.notice { background: var(--panel); border: 1px dashed var(--leaf-dim); border-radius: 12px;
  padding: 0.9rem 1.1rem; font-size: 0.92rem; color: var(--muted); }
.hero video { width: 100%; max-width: 300px; border-radius: 16px;
  border: 1px solid var(--line); margin: 1rem auto 0.4rem; display: block; }
.season { display: flex; gap: 0.8rem; overflow-x: auto; padding: 0.6rem 0 1rem; }
.season figure { margin: 0; flex: 0 0 172px; }
.season video { width: 172px; border-radius: 12px; border: 1px solid var(--line); display: block; }
.season figcaption { font: 600 0.75rem/1.35 ui-monospace, Menlo, monospace;
  color: var(--muted); margin-top: 0.4rem; }
.season figcaption a { color: var(--leaf); }
.binge { max-width: 420px; margin: 0 auto; }
.binge figure { margin: 0 0 2.4rem; }
.binge video { width: 100%; aspect-ratio: 9 / 16; object-fit: contain; display: block;
  background: var(--code-bg); border: 1px solid var(--line); border-radius: 16px; }
.binge figcaption { font: 600 0.8rem/1.4 ui-monospace, Menlo, monospace;
  color: var(--muted); margin-top: 0.5rem; }
.binge figcaption a { color: var(--leaf); }
"""


DEFAULT_DESC = ("Story trees that branch instead of running linear — AI-rendered "
                "micro-drama, curated by one human's taste, every decision auditable in git.")


def page(title: str, body: str, depth: int = 0, path: str = "", desc: str = "") -> str:
    root = "../" * depth
    desc = (desc or DEFAULT_DESC).strip()
    if len(desc) > 200:
        desc = desc[:197].rstrip() + "…"
    url = f"{CANONICAL}/{path}"
    og_image = f"{CANONICAL}/og.png"
    esc_t, esc_d = html.escape(title), html.escape(desc)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
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
<meta name="twitter:image" content="{og_image}">
<title>{esc_t}</title>
<style>{CSS}</style>
</head>
<body>
<main>
<nav class="crumbs"><a href="{root}index.html">🌳 {REPO_NAME}</a> · <a href="{root}city.html">the city</a> · <a href="{root}machine.html">⚙️ the machine</a> · <a href="{root}status.html">📊 status</a> · <a href="{REPO_URL}">source</a></nav>
{body}
<footer>Everything here is auditable in <a href="{REPO_URL}">git</a>.
Branch anything. Fork everything. · <a href="{root}city.html">The Promise</a></footer>
</main>
</body>
</html>"""


def md_to_html(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def strip_md(text: str) -> str:
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[*_`>#]", "", text).strip()


def extract_section(md_text: str, heading_prefix: str) -> str:
    """First paragraph under a '## <heading_prefix>…' heading."""
    m = re.search(rf"^## {re.escape(heading_prefix)}[^\n]*\n+(.+?)(?:\n\n|\n#)", md_text, re.M | re.S)
    return strip_md(m.group(1)) if m else ""


def load_genome(genome_dir: Path) -> dict:
    tree = yaml.safe_load((genome_dir / "tree.yaml").read_text())
    lineage = yaml.safe_load((genome_dir / "lineage.yaml").read_text())
    nodes = {}
    for n in lineage["nodes"]:
        node_dir = genome_dir / "nodes" / n["slug"]
        n["md"] = (node_dir / "node.md").read_text()
        n["teaser"] = extract_section(n["md"], "Hook")
        n["children"] = []
        n["leaf_meta"] = []
        for leaf_id in n.get("leaves") or []:
            f = node_dir / "leaves" / f"{leaf_id}.yaml"
            if f.exists():
                n["leaf_meta"].append(yaml.safe_load(f.read_text()))
        reactions = node_dir / "sap" / "reactions.yaml"
        n["reactions"] = yaml.safe_load(reactions.read_text()) if reactions.exists() else None
        summary = node_dir / "sap" / "summary.yaml"
        n["sap"] = yaml.safe_load(summary.read_text()) if summary.exists() else None
        screening = node_dir / "sap" / "screening.yaml"
        n["screening"] = yaml.safe_load(screening.read_text()) if screening.exists() else None
        nodes[n["id"]] = n
    for n in nodes.values():
        if n.get("parent"):
            nodes[n["parent"]]["children"].append(n)
    roots = [n for n in nodes.values() if not n.get("parent")]
    return {"tree": tree["tree"], "config": tree, "nodes": nodes, "roots": roots, "dir": genome_dir}


def chips(n: dict) -> str:
    out = f'<span class="chip">{html.escape(n["id"])}</span>'
    if n.get("trunk"):
        out += '<span class="chip trunk">trunk</span>'
    out += f'<span class="chip {html.escape(n["status"])}">{html.escape(n["status"])}</span>'
    return out


def node_card(genome_id: str, n: dict, depth: int) -> str:
    # D11: the workshop is a first-class destination — every node with a shot
    # list advertises its board from the front page, not two clicks deep.
    board = (f' · <a href="{genome_id}/{html.escape(n["slug"])}-shots.html">🎬 shot board</a>'
             if (REPO / "genomes" / genome_id / "nodes" / n["slug"] / "shots.md").exists()
             else "")
    teaser = f'<div class="teaser">{html.escape((n["teaser"][:160] + "…") if len(n["teaser"]) > 160 else n["teaser"])}</div>' if n["teaser"] else ""
    react = f' · <a href="{html.escape(n["reactions"]["url"])}">💧 react</a>' if n.get("reactions") else ""
    kids = ""
    if n["children"]:
        kids = "<ul>" + "".join(node_card(genome_id, c, depth) for c in n["children"]) + "</ul>"
    return f"""<li><div class="card">
{chips(n)}
<div class="title"><a href="{genome_id}/{html.escape(n['slug'])}.html">{html.escape(n['title'])}</a></div>
{teaser}
<div class="meta">{len(n['leaf_meta'])} {'leaf' if len(n['leaf_meta']) == 1 else 'leaves'} · <a href="{genome_id}/{html.escape(n['slug'])}.html">read</a>{board}{react}</div>
</div>{kids}</li>"""


def render_node_page(g: dict, n: dict) -> str:
    genome_id = g["tree"]["id"]
    body_html = md_to_html(n["md"])
    # rewrite sibling links (../<slug>/node.md) to site pages
    body_html = re.sub(r'href="\.\./([^/"]+)/node\.md"', r'href="\1.html"', body_html)

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
        f"<tr><td>{leaf_cell(l)}</td><td>{html.escape(str(l['tier']))}</td>"
        f"<td>{html.escape(str(l['form']))}</td><td>${l['cost_usd']:.2f}</td>"
        f"<td>{html.escape(str(l['status']))}</td><td>{screen_cell(l)}</td></tr>"
        for l in n["leaf_meta"]
    )
    vids = [l for l in n["leaf_meta"]
            if str(l.get("content", "")).endswith(".mp4") and l.get("status") == "live"]
    vids.sort(key=lambda l: str(l.get("tier")), reverse=True)  # highest tier first
    players = "".join(
        f'<figure style="display:inline-block;margin:0.4rem 0.6rem 0.4rem 0">'
        f'<video controls playsinline preload="metadata" style="width:100%;max-width:360px;border-radius:12px;border:1px solid var(--line)" '
        f'src="leaves/{html.escape(str(l["content"]))}"></video>'
        f'<figcaption class="chip">{html.escape(str(l["tier"]))} · {html.escape(str(l["form"]))}</figcaption></figure>'
        for l in vids)
    player_html = (f"<h2>Watch</h2>{players}"
                   f'<p class="notice">The highest $0 render of this node — every episode is watchable '
                   f'before a dollar is spent; the full script it was cut from is below.</p>'
                   if players else "")
    leaves_html = f"""<h2>Leaves (renders of this node)</h2>
<table><tr><th>leaf</th><th>tier</th><th>form</th><th>cost</th><th>status</th><th>screening</th></tr>{leaves_rows}</table>
<p class="notice">Every render publishes its prompt, model, seed, and cost — this table is the audit trail.
<strong>Screening:</strong> rate any leaf (continuity, character, vibe) — the crowd narrows the shortlist,
the taste file decides. Ratings are harvested into this node's <code>sap/screening.yaml</code>.
Higher-tier leaves (animatic, video) arrive with a published per-render budget.</p>"""

    rail = (g["config"].get("watering_rail") or {})
    link, confirmed = rail.get("payment_link"), rail.get("confirmed_by_founder")
    if link and confirmed:
        water_html = f"""<h2>Water this branch</h2>
<p><a class="btn" href="{html.escape(str(link))}">💧 Fund a render of {html.escape(n['id'])}</a></p>
<p class="notice">Watering funds <strong>specific renders</strong>, split
<code>costs-first-70-30-v1</code> (the render's published cost is reimbursed first; the remainder
splits 70% author / 30% commons). Mention <code>{html.escape(n['id'])}</code> with your
contribution — every drop lands in the <a href="{REPO_URL}/blob/main/ledger/watering.csv">public
ledger</a>. Or water with <strong>compute</strong>: re-render a leaf with your own key and submit it
(<a href="{REPO_URL}/blob/main/WATERING.md">how →</a>).</p>"""
    else:
        water_html = f"""<h2>Water this branch</h2>
<p class="notice">💧 Money watering opens soon (one founder key-turn away). Watering with
<strong>compute</strong> is open now: re-render any leaf of this node with your own key or free GPU
(<a href="{REPO_URL}/blob/main/pipeline/kaggle/render-kaggle.ipynb">the Kaggle notebook</a> runs at
$0) and submit it — provenance in, ledger row yours.
<a href="{REPO_URL}/blob/main/WATERING.md">How watering works →</a></p>"""

    react_html = ""
    if n.get("reactions"):
        vitals = ""
        if n.get("sap"):
            s = n["sap"]
            emoji = {"+1": "👍", "-1": "👎", "laugh": "😄", "confused": "😕", "heart": "❤️", "hooray": "🎉", "rocket": "🚀", "eyes": "👀"}
            counts = " ".join(f"{emoji[k]} {v}" for k, v in s["reactions"].items() if v) or "no reactions yet — be the first drop"
            vitals = f"""<p><span class="chip">{counts}</span> <span class="chip">💬 {s['comments']} comments</span>
<span class="chip">harvested {html.escape(str(s['harvested_at'])[:10])}</span></p>"""
        react_html = f"""<h2>Sap (your reactions)</h2>
{vitals}
<p><a class="btn" href="{html.escape(n['reactions']['url'])}">💧 React / comment on this node</a></p>
<p class="notice">Reactions are open data (Guideline 4): they order this branch against its siblings.
Harvested daily into this node's <code>sap/summary.yaml</code> by CI.
No account? Just tell someone about it — word of mouth is sap too.</p>"""

    kids = ""
    if n["children"]:
        links = " · ".join(f'<a href="{html.escape(c["slug"])}.html">{html.escape(c["id"])} — {html.escape(c["title"])}</a>' for c in n["children"])
        kids = f"<p><strong>Continues as:</strong> {links}</p>"
    parent_link = ""
    if n.get("parent"):
        p = g["nodes"][n["parent"]]
        parent_link = f'<p><strong>Parent:</strong> <a href="{html.escape(p["slug"])}.html">{html.escape(p["id"])} — {html.escape(p["title"])}</a></p>'

    body = f"""<p>{chips(n)}</p>
{player_html}
{body_html}
<hr>
{parent_link}{kids}
{leaves_html}
{react_html}
{water_html}
<h2>Branch this node</h2>
<p class="notice">Anyone may continue this moment differently. Declare <code>{html.escape(n['id'])}</code> as your parent —
that's the only obligation. <a href="../create.html">Write your own episode →</a></p>"""
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


def trunk_chain(g: dict) -> list:
    chain, cur = [], next((r for r in g["roots"] if r.get("trunk")), None)
    while cur:
        chain.append(cur)
        cur = next((c for c in cur["children"] if c.get("trunk")), None)
    return chain


def best_t3(n: dict) -> dict | None:
    vids = [l for l in n["leaf_meta"] if str(l.get("tier")) == "T3"
            and str(l.get("content", "")).endswith(".mp4") and l.get("status") == "live"]
    return vids[-1] if vids else None


def season_strip(g: dict) -> str:
    figs = []
    for i, n in enumerate(trunk_chain(g), 1):
        leaf = best_t3(n)
        if not leaf:
            continue
        gid = g["tree"]["id"]
        figs.append(
            f'<figure><video controls playsinline preload="metadata" '
            f'src="{gid}/leaves/{html.escape(str(leaf["content"]))}"></video>'
            f'<figcaption>ep {i} · <a href="{gid}/{html.escape(n["slug"])}.html">'
            f'{html.escape(n["title"])}</a></figcaption></figure>')
    return f'<div class="season">{"".join(figs)}</div>' if figs else ""


def render_create() -> str:
    """The participation storefront: how to write your own episode (or plant
    your own tree), in plain words, with the security model spelled out."""
    body = f"""<h1>✍️ Write your own episode</h1>
<p class="notice">Every episode of this tree can be continued <em>differently</em> — by you.
No permission needed, no writing credits checked. The tree polices lineage, never direction.</p>

<h2>The five steps</h2>
<p><strong>1 · Pick your parent.</strong> Any episode — the latest, or one from way back whose
story you'd have turned another way. Your episode declares which one it continues. That
declaration is the only obligation in the entire system.</p>
<p><strong>2 · Write it.</strong> A ~90-second script (<code>node.md</code> — copy any
existing episode's file as a template). Two rules bind everyone, including the AI steward:
something real must change (a relationship, the world, what someone knows), and it must end
on a hook that's a real state change, not a tease.</p>
<p><strong>3 · Submit it.</strong> Two doors:</p>
<p>· <strong>Git door:</strong> fork the <a href="{REPO_URL}">repo</a>, add your node folder +
one line in <code>lineage.yaml</code> naming your parent, open a pull request.<br>
· <strong>No-git door:</strong> paste your script into
<a href="{REPO_URL}/issues/new?template=branch-submission.yml">this form</a> — the steward
turns it into a proper branch with your name on it. (Takes any free GitHub account —
no git commands, just the form.)</p>
<p><strong>4 · It gets rendered.</strong> The $0 pipeline (storyboard → voiced animatic) runs
for anyone's episode. Want it <em>filmed</em>? <a href="{REPO_URL}/blob/main/REGROW.md">Render
it yourself with free tools</a> — or let watering fund it.</p>
<p><strong>5 · The tree decides its place.</strong> Readers react (💧 on each episode page);
the crowd narrows; the author's <a href="{REPO_URL}/blob/main/taste/sapling.founder.v0.3.md">public
taste rules</a> pick what leads the canon — citing which rule drove the call, in the commit log.
Branches that don't lead are <strong>never deleted</strong>: they stay alive, watchable, and can
take the lead later if readers water them.</p>

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

<p><a class="btn" href="{REPO_URL}/issues/new?template=branch-submission.yml">Submit an episode
(no git needed)</a> <a class="btn ghost" href="watch.html">▶ Watch the season first</a></p>"""
    return page("Write your own episode — Banyan City", body, path="create.html",
                desc="Continue any episode of the tree your way — no permission needed. "
                     "Fork, write, declare your parent. The tree decides in the open.")


def render_watch(genomes: list) -> str:
    """One-thumb binge page: the trunk's official T3 cut of every episode,
    top to bottom in story order — no tree, no tables, just the season."""
    figs = []
    for g in genomes:
        gid = g["tree"]["id"]
        for i, n in enumerate(trunk_chain(g), 1):
            leaf = best_t3(n)
            if not leaf:
                continue
            figs.append(
                f'<figure><video controls playsinline preload="metadata" '
                f'src="{gid}/leaves/{html.escape(str(leaf["content"]))}"></video>'
                f'<figcaption>ep {i} · <a href="{gid}/{html.escape(n["slug"])}.html">'
                f'{html.escape(n["title"])}</a></figcaption></figure>')
    body = f"""<h1>▶ Season 1, all episodes</h1>
<p class="notice">The trunk's official cut of each episode, in order — every one a $0 render,
every one re-renderable. Scripts, provenance, and rival branches live on each episode's page.</p>
<div class="binge">{''.join(figs)}</div>
<p><a class="btn ghost" href="index.html">← Back to the tree</a></p>"""
    return page("Watch — Banyan City, Season 1", body, path="watch.html",
                desc="Binge Season 1 of Banyan City: the trunk's official episodes, "
                     "in order, in one vertical feed.")


def render_index(genomes: list) -> str:
    sections = []
    hero_video = ""
    for g in genomes:
        chain = trunk_chain(g)
        lead = best_t3(chain[0]) if chain else None
        if lead and not hero_video:
            hero_video = (f'<video controls playsinline preload="metadata" '
                          f'src="{g["tree"]["id"]}/leaves/{html.escape(str(lead["content"]))}"></video>')
    workshop = (
        '<h2>⚙️ The Machine</h2>'
        '<p class="notice"><strong>This show makes itself in public, and anyone can work on it.</strong> '
        'Every episode publishes its complete recipe — approved frames, exact prompts, every take with provenance. '
        'Open <a href="machine.html">The Machine</a> to see how the whole loop runs, '
        'browse <a href="sapling/001-capability-inventory-shots.html">episode 1\'s shot board</a> to see it live, '
        'or grab an <a href="https://github.com/olegmlkvorg/banyan-city/issues?q=is%3Aissue+is%3Aopen+label%3Arender-request">open render request</a> '
        'and hand back a take made with your own tools — your name goes in the public ledger.</p>')
    sections.append(workshop)
    for g in genomes:
        t = g["tree"]
        tree_html = "<ul class='tree'>" + "".join(node_card(t["id"], r, 0) for r in g["roots"]) + "</ul>"
        n_nodes = len(g["nodes"])
        n_leaves = sum(len(n["leaf_meta"]) for n in g["nodes"].values())
        fork = live_fork(g)
        fork_html = ""
        if fork:
            tip, kids = fork
            vs = " <em>vs</em> ".join(
                f'<a href="{html.escape(t["id"])}/{html.escape(k["slug"])}.html">'
                f'{html.escape(k["id"])} — {html.escape(k["title"])}</a>' for k in kids)
            fork_html = (f'<p class="notice">⚡ <strong>Live fork at the tip:</strong> '
                         f'<a href="{html.escape(t["id"])}/{html.escape(tip["slug"])}.html">'
                         f'{html.escape(tip["id"])} — {html.escape(tip["title"])}</a> ends on one cliffhanger, '
                         f'paid off {len(kids)} different ways: {vs}. '
                         f'Same debt, competing payments — read both, react; the tree decides on material, not votes.</p>')
        sections.append(f"""<h2>🌱 {html.escape(t['title'])} — Season 1, all episodes <span class="chip">{n_nodes} nodes</span> <span class="chip">{n_leaves} leaves</span></h2>
{season_strip(g)}
<p class="notice">🌿 <strong>These are first renders — rough on purpose.</strong> An episode here is a
<em>leaf</em>: one $0 rendering of a script, never the last word. Rendered a better one on your own
GPU or key? Submit it — screening and the taste file decide which leaf leads, and the tree keeps
every version. <a href="{REPO_URL}/blob/main/WATERING.md">How to water with compute →</a></p>
{fork_html}
<p class="notice">An engineer dies debugging production at 3 a.m. and reincarnates as a banyan sapling.
He can't move, fight, or flee — only sense, grow, and make the space around him worth staying in.
The story <em>branches</em>: rival continuations coexist as siblings, all alive, none rejected.
Watch, react — the sap decides what runs hot.</p>
{tree_html}""")

    body = f"""<div class="hero">
<div class="seal">🌳</div>
<h1>Banyan City</h1>
<p>An AI-animated series that <strong>branches</strong> — viewers pick which sequel survives —
and <strong>regrows</strong>: every episode below is a first rough $0 render, and anyone
can re-render any of them better. The whole pipeline, every decision, and every
dollar are public in git.</p>
{hero_video}
<a class="btn" href="sapling/001-capability-inventory.html">▶ Start at episode 1</a>
<a class="btn ghost" href="watch.html">▶ Binge season 1</a>
<a class="btn ghost" href="create.html">✍️ Write your own episode</a>
<a class="btn ghost" href="city.html">Read the Promise</a>
</div>
{''.join(sections)}
<hr>
<h2>The rules of this place, in one breath</h2>
<p>Anyone may <strong>branch</strong> any episode (declare your parent — the only obligation).
Citizens <strong>water</strong> the branches they love; unwatered branches sleep, never die.
One author's <strong>taste file</strong> decides the trunk; disagreement is watering a rival branch, not a vote.
All reactions and money are <strong>open data</strong>. And anyone may <strong>fork the whole city</strong> —
take everything, rename it, go. <a href="city.html">Full text →</a></p>
<p class="notice">🎬 <strong>Now growing:</strong> the tree is choosing its video model —
same three shots rendered on every candidate platform, scored in the open.
<a href="trials/index.html">The T3 platform trials →</a></p>"""
    return page("Banyan City — a story tree", body)


def render_city() -> str:
    parts = []
    for fname, title in [("PROMISE.md", None), ("GUIDELINES.md", None), ("VOCABULARY.md", None)]:
        parts.append(md_to_html((REPO / fname).read_text()))
        parts.append("<hr>")
    body = "".join(parts[:-1]) + f"""
<p class="notice">These texts are canonical and live in
<a href="{REPO_URL}">the repository</a> — amendable by citizens
per Guideline 6, except the right to branch and fork, which is permanent.
Open questions live in <a href="{REPO_URL}/blob/HEAD/DECISIONS.md">DECISIONS.md</a>.</p>"""
    return page("The City — Promise, Guidelines, Vocabulary", body, path="city.html")


AXES = ["adherence", "motion", "look", "nativeness", "consistency", "friction"]
WEIGHTED = {"adherence": 2, "consistency": 2}


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
                meta_f = mp4.with_suffix(".meta.yaml")
                meta = yaml.safe_load(meta_f.read_text()) if meta_f.exists() else {}
                clips.append((mp4, meta or {}))
            if clips:
                outputs[pdir.name] = clips

    sections = []
    for plat in sorted(set(outputs) | set(scores)):
        rows, players = "", ""
        for mp4, meta in outputs.get(plat, []):
            players += (f'<figure style="display:inline-block;margin:0.5rem 0.6rem 0.5rem 0">'
                        f'<video controls playsinline preload="metadata" '
                        f'style="width:100%;max-width:300px;border-radius:12px;border:1px solid var(--line)" '
                        f'src="{html.escape(plat)}/{html.escape(mp4.name)}"></video>'
                        f'<figcaption class="chip">shot {html.escape(str(meta.get("shot", mp4.stem)))} · '
                        f'{html.escape(str(meta.get("model", "model?")))}</figcaption></figure>')
        shot_scores = (scores.get(plat) or {}).get("shots") or {}
        for shot, ax in sorted(shot_scores.items()):
            ax = ax or {}
            filled = [(a, ax[a]) for a in AXES if isinstance(ax.get(a), (int, float))]
            if filled:
                num = sum(v * WEIGHTED.get(a, 1) for a, v in filled)
                den = sum(WEIGHTED.get(a, 1) for a, _ in filled)
                total = f"{num / den:.1f}"
            else:
                total = "—"
            cells = "".join(f"<td>{ax.get(a) if ax.get(a) is not None else '·'}</td>" for a in AXES)
            note = html.escape(str(ax.get("notes", "") or ""))
            rows += f"<tr><td><strong>{html.escape(shot)}</strong></td>{cells}<td><strong>{total}</strong></td><td>{note}</td></tr>"
        table = (f"<table><tr><th>shot</th>{''.join(f'<th>{a}</th>' for a in AXES)}<th>weighted</th><th>notes</th></tr>"
                 f"{rows}</table>") if rows else '<p class="notice">Not scored yet.</p>'
        model = html.escape(str((scores.get(plat) or {}).get("model", "")))
        sections.append(f"<h2>{html.escape(plat)} <span class='chip'>{model}</span></h2>{players}{table}")

    if not sections:
        sections.append('<p class="notice">No trial outputs yet — the founder is out gathering free-tier '
                        'renders. The protocol, prompts, and rubric below are already fixed, so results '
                        'can\'t be quietly re-rolled until they flatter.</p>')

    intro = md_to_html((tdir / "README.md").read_text())
    prompts = md_to_html((tdir / "prompts.md").read_text())
    body = (f"{''.join(sections)}<hr><details><summary><strong>Protocol, candidates & rubric</strong></summary>"
            f"{intro}</details><details><summary><strong>The three prompts</strong></summary>{prompts}</details>")
    return page("T3 platform trials — same three shots, every model", body, depth=1,
                path="trials/index.html",
                desc="Choosing Banyan City's video model in the open: the same three shots "
                     "rendered on each candidate platform, scored on a fixed rubric.")


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


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    genomes = [load_genome(p) for p in sorted((REPO / "genomes").iterdir()) if p.is_dir()]

    (OUT / "index.html").write_text(render_index(genomes))
    (OUT / "watch.html").write_text(render_watch(genomes))
    (OUT / "create.html").write_text(render_create())
    (OUT / "city.html").write_text(render_city())
    from build_status import build as _build_status
    _build_status(OUT)
    from build_sim import build as _build_sim
    _build_sim(OUT)
    (OUT / "machine.html").write_text(page(
        "The Machine — how this operates",
        md_to_html((REPO / "MACHINE.md").read_text()),
        path="machine.html",
        desc="The whole loop on one page: script, approval, stills, takes, assembly, reactions, branching."))
    (OUT / "feed.xml").write_text(render_feed(genomes))
    (OUT / ".nojekyll").write_text("")
    og = REPO / "assets" / "og.png"          # social-share image referenced by page() meta
    if og.exists():
        shutil.copy(og, OUT / "og.png")
    (OUT / "trials").mkdir()
    (OUT / "trials" / "index.html").write_text(render_trials())
    trials_out = REPO / "pipeline" / "t3-trials" / "outputs"
    if trials_out.exists():
        for mp4 in trials_out.glob("*/*.mp4"):
            (OUT / "trials" / mp4.parent.name).mkdir(exist_ok=True)
            shutil.copy(mp4, OUT / "trials" / mp4.parent.name / mp4.name)
    for g in genomes:
        gdir = OUT / g["tree"]["id"]
        gdir.mkdir()
        for n in g["nodes"].values():
            _page = render_node_page(g, n)
            if (g["dir"] / "nodes" / n["slug"] / "shots.md").exists():
                _page = _page.replace(
                    "</nav>",
                    f'</nav><p><a href="{n["slug"]}-shots.html">🎬 Shot board — '
                    "every beat's recipe &amp; takes, forkable</a></p>", 1)
            (gdir / f"{n['slug']}.html").write_text(_page)
            # D11: the shot board — every beat's full recipe + takes, forkable
            # by anyone. The repo is the process; the site renders the process.
            node_dir = g["dir"] / "nodes" / n["slug"]
            if (node_dir / "shots.md").exists():
                from build_shotboard import board_html
                media = f"{n['slug']}-media"
                (gdir / f"{n['slug']}-shots.html").write_text(
                    board_html(g["tree"]["id"], node_dir, rel=media))
                if (node_dir / "stills").is_dir():
                    (gdir / media).mkdir(exist_ok=True)
                    for f in (node_dir / "stills").glob("*.png"):
                        shutil.copy(f, gdir / media / f.name)
                if (node_dir / "takes" / "stills").is_dir():
                    (gdir / f"{media}-takes").mkdir(exist_ok=True)
                    for f in (node_dir / "takes" / "stills").glob("*.png"):
                        shutil.copy(f, gdir / f"{media}-takes" / f.name)
                if (node_dir / "takes" / "clips").is_dir():
                    (gdir / f"{media}-clips").mkdir(exist_ok=True)
                    for f in (node_dir / "takes" / "clips").iterdir():
                        shutil.copy(f, gdir / f"{media}-clips" / f.name)
            # publish renderable leaf artifacts (html storyboards, animatics…)
            for l in n["leaf_meta"]:
                content = str(l.get("content", ""))
                if content.endswith((".html", ".mp4")):
                    src = g["dir"] / "nodes" / n["slug"] / "leaves" / content
                    if src.exists():
                        (gdir / "leaves").mkdir(exist_ok=True)
                        shutil.copy(src, gdir / "leaves" / content)

    total = sum(len(g["nodes"]) for g in genomes)
    print(f"✓ built _site/ — {len(genomes)} genome(s), {total} node pages")


if __name__ == "__main__":
    main()
