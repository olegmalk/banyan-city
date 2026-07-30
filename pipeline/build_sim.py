#!/usr/bin/env python3
"""banyan city, the sim — a game-like visualization of the whole studio
(dad's directive 2026-07-30). Everything is live data dressed as a tiny city:
the episode is a tree growing leaves, machines are buildings that glow and
puff smoke while rendering, the cloud GPU is a cloud, decisions are quests,
voters are citizens. Pure CSS/emoji — no external assets (public-site CSP)."""
import html
import subprocess
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent

import json
import urllib.request

GH = "olegmlkvorg/banyan-city"


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


def latest_thread_comments(n=3):
    raw = _get(f"https://api.github.com/repos/{GH}/issues/1/comments?per_page=100")
    try:
        cs = json.loads(raw)[-n:]
        return [(c["user"]["login"], c["body"][:80].replace("\n", " ")) for c in cs]
    except Exception:
        return []


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              timeout=20, cwd=REPO).stdout.strip()
    except Exception:
        return ""


def machine_state(branch_tail: str) -> tuple:
    """(css_state, caption) from a worker's last heartbeat line."""
    if not branch_tail:
        return "asleep", "no heartbeat yet"
    try:
        hh, mm, ss = branch_tail.split("Z")[0].split(":")
        beat_age = (time.gmtime().tm_hour * 3600 + time.gmtime().tm_min * 60 + time.gmtime().tm_sec) - \
                   (int(hh) * 3600 + int(mm) * 60 + int(ss))
        if beat_age < 0:
            beat_age += 86400
    except Exception:
        beat_age = 9999
    working = ("STARTED" in branch_tail or "MODEL_LOADED" in branch_tail)
    if beat_age < 360 and working:
        return "working", branch_tail.split("Z ", 1)[-1][:46]
    if beat_age < 1800:
        return "idle", "resting — " + branch_tail.split("Z ", 1)[-1][:38]
    return "asleep", "asleep for a while"


def plain_tables_html():
    from build_status import beat_state, ESTIMATES
    d = REPO / "genomes/sapling/nodes/001-capability-inventory"
    rows, canon, total = beat_state(d)
    est = "".join(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td></tr>" for a, b in ESTIMATES)
    return (f"<h2>📋 Per-beat state</h2><table style='width:100%;font-size:.8rem' border=0>"
            f"<tr><th>Beat</th><th>Still</th><th>Motion</th><th>Request</th><th>Blocked on</th></tr>"
            + "".join(rows) +
            f"</table><h2>💰 Stage costs (measured)</h2><table style='font-size:.8rem'>{est}</table>")


def build(out_dir: Path):
    d = REPO / "genomes/sapling/nodes/001-capability-inventory"
    canon = len(list((d / "stills").glob("[0-9]*.png")))
    spend = 0.0
    for line in (REPO / "ledger/render-spend.csv").read_text().splitlines()[1:]:
        if line.strip():
            try:
                spend += float(line.split(",")[5])
            except (ValueError, IndexError):
                pass
    try:
        inbox = (yaml.safe_load((REPO / "pipeline/pending-founder.yaml").read_text()) or {}).get("pending") or []
    except Exception:
        inbox = []
    machines = []
    EMOJI = {"msi": "🏭", "m2": "🏢", "m1pro": "🏛"}
    for b in farm_branches():
        name = b.split("farm-results-")[-1]
        state, cap = machine_state(branch_heartbeat(b))
        machines.append((name, EMOJI.get(name, "🏠"), state, cap))
    comments = latest_thread_comments()

    leaves = "".join(
        f'<div class="leaf {"grown" if i < canon else "bud"}" style="--i:{i}">🍃</div>'
        for i in range(15))
    quests = "".join(
        f'<div class="quest">📜 <b>{html.escape(q.get("title",""))}</b><br>'
        f'<small>{html.escape(q.get("detail",""))[:90]}</small></div>'
        for q in inbox) or '<div class="quest">✨ no quests — the city runs itself</div>'
    town = "".join(
        f'<div class="bld {st}"><div class="smoke">{"💨" if st == "working" else ""}</div>'
        f'<div class="ico">{em}</div><div class="nm">{html.escape(n)}</div>'
        f'<div class="cap">{html.escape(c)}</div></div>'
        for n, em, st, c in machines)
    citizens = "".join(
        f'<div class="citizen" style="--d:{i}"><div class="bubble">{html.escape(b2)}…</div>'
        f'<div class="spr">{"🧑‍🌾" if i % 2 else "🧙"}</div><small>{html.escape(a)}</small></div>'
        for i, (a, b2) in enumerate(comments))

    out = f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>banyan city — the sim</title>
<style>
 body {{ margin:0; font-family:-apple-system,system-ui,sans-serif; color:#e8f0e8;
        background: linear-gradient(#0b1026 0%, #16233f 45%, #1d3a2a 78%, #142718 100%);
        min-height:100vh; overflow-x:hidden; }}
 .sky {{ position:relative; height:120px; }}
 .cloudgpu {{ position:absolute; left:8%; top:30px; font-size:2.2rem; animation: drift 22s linear infinite; }}
 .cloudgpu small {{ font-size:.65rem; display:block; color:#9fb4d8; }}
 @keyframes drift {{ 0%{{transform:translateX(0)}} 50%{{transform:translateX(70vw)}} 100%{{transform:translateX(0)}} }}
 .stars::after {{ content:"✦ ✧ ✦ ✧ ✦"; letter-spacing:5vw; color:#5b6f9e; position:absolute; top:12px; left:10vw; }}
 h1 {{ text-align:center; margin:.2rem 0 0; font-size:1.25rem; }}
 .coins {{ position:fixed; top:10px; right:14px; background:#00000055; border-radius:20px; padding:.3rem .8rem; }}
 .grove {{ display:flex; justify-content:center; align-items:flex-end; margin-top:-10px; }}
 .tree {{ text-align:center; }}
 .trunky {{ font-size:5rem; }}
 .canopy {{ display:grid; grid-template-columns:repeat(5,2.2rem); gap:.15rem; justify-content:center; }}
 .leaf {{ font-size:1.5rem; animation: sway 3.4s ease-in-out infinite; animation-delay: calc(var(--i) * .2s); }}
 .leaf.bud {{ filter:grayscale(1) brightness(.5); }}
 @keyframes sway {{ 0%,100%{{transform:rotate(-6deg)}} 50%{{transform:rotate(8deg)}} }}
 .label {{ color:#a9d3a9; font-size:.85rem; }}
 .town {{ display:flex; gap:1.2rem; justify-content:center; flex-wrap:wrap; margin:1.4rem 1rem; }}
 .bld {{ width:170px; background:#0f1b2e; border:1px solid #29405e; border-radius:12px; padding:.7rem; text-align:center; position:relative; }}
 .bld .ico {{ font-size:2.6rem; }}
 .bld.working {{ box-shadow:0 0 18px #ffd76a55; border-color:#ffd76a; }}
 .bld.working .ico {{ animation: chug .8s ease-in-out infinite; }}
 @keyframes chug {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-4px)}} }}
 .bld.idle {{ opacity:.85; }}
 .bld.asleep {{ opacity:.45; filter:grayscale(.7); }}
 .bld.asleep::after {{ content:"💤"; position:absolute; top:6px; right:8px; }}
 .smoke {{ height:1.2rem; animation: puff 2s linear infinite; }}
 @keyframes puff {{ 0%{{opacity:.9; transform:translateY(0)}} 100%{{opacity:0; transform:translateY(-10px)}} }}
 .nm {{ font-weight:700; }}
 .cap {{ font-size:.72rem; color:#9fb4d8; min-height:2.1em; }}
 .row {{ display:flex; gap:1.2rem; flex-wrap:wrap; justify-content:center; align-items:flex-start; margin:0 1rem 2rem; }}
 .panel {{ background:#00000040; border-radius:14px; padding: .9rem 1.1rem; max-width:380px; }}
 .panel h2 {{ font-size:.95rem; margin:.1rem 0 .5rem; color:#ffd76a; }}
 .quest {{ background:#2a2113; border:1px solid #6b5427; border-radius:8px; padding:.5rem .6rem; margin:.4rem 0; font-size:.85rem; }}
 .citizen {{ display:inline-block; text-align:center; margin:.4rem; animation: bob 2.6s ease-in-out infinite; animation-delay: calc(var(--d) * .4s); }}
 @keyframes bob {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-3px)}} }}
 .bubble {{ background:#fff; color:#222; border-radius:10px; padding:.35rem .5rem; font-size:.7rem; max-width:150px; margin-bottom:.2rem; }}
 .spr {{ font-size:1.8rem; }}
 footer {{ text-align:center; color:#7b8fa8; font-size:.75rem; padding-bottom:1.2rem; }}
</style></head><body>
<div class="sky stars"><div class="cloudgpu">☁️<small>RunPod — reserve</small></div></div>
<h1>🌳 banyan city — the living studio</h1>
<div class="coins">🪙 ${spend:.2f} lifetime</div>
<div class="grove"><div class="tree">
  <div class="canopy">{leaves}</div>
  <div class="trunky">🌳</div>
  <div class="label">episode 001 — {canon}/15 beats grown</div>
</div></div>
<div class="town">{town}</div>
<div class="row">
  <div class="panel"><h2>📜 Quest board (the author's)</h2>{quests}</div>
  <div class="panel"><h2>🗣 Citizens on the thread</h2>{citizens}
    <p><a style="color:#ffd76a" href="https://github.com/olegmlkvorg/banyan-city/issues/1">join them →</a></p></div>
</div>
<div class="row"><div class="panel" style="max-width:820px">{{plain_tables}}</div></div>
<footer>snapshot {time.strftime('%Y-%m-%d %H:%M')} · rebuilt on every push · the whole repo IS the show —
<a style="color:#ffd76a" href="index.html">the city</a> · <a style="color:#ffd76a" href="machine.html">how it works</a></footer>
</body></html>"""
    out = out.replace("{plain_tables}", plain_tables_html())
    (out_dir / "status.html").write_text(out)
    (out_dir / "sim.html").write_text(
        '<!doctype html><meta http-equiv="refresh" content="0;url=status.html">')
    print(f"✓ status.html (sim) — {canon}/15 leaves, {len(machines)} buildings")


if __name__ == "__main__":
    build(REPO / "_site")
