#!/usr/bin/env python3
"""The status page — progress, estimates, bottlenecks, visible to everyone.

Dad's ask (2026-07-28): clearly see what is running, what is blocked on whom,
and where the time goes. Build-time snapshot from repo state; regenerated on
every push like the rest of the site.
"""
import html
import subprocess
import sys
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from generate_shots import parse_shots  # noqa: E402

# measured medians from the ledgered runs of 2026-07-27/28
ESTIMATES = [
    ("Candidate stills round (Kaggle, 4 seeds/beat)", "~15 min incl. queue"),
    ("Founder verdict on a ballot", "minutes of attention — the real variable"),
    ("POST motion take (deterministic)", "~1 min, $0"),
    ("Paid API motion take (e.g. Hailuo)", "~3 min, ~$0.28"),
    ("Full prototype assembly + QA", "~4 min, $0"),
]


def beat_state(d: Path):
    shots = parse_shots((d / "shots.md").read_text())
    reqs = {}
    rq = d / "requests.yaml"
    if rq.exists():
        reqs = (yaml.safe_load(rq.read_text()) or {}).get("render_requests", {})
    rows = []
    for s in shots:
        num = s["num"]
        canon = (d / "stills" / f"{num:02d}-{s['slug']}.png").exists()
        cands = len(list((d / "takes" / "stills").glob(f"{num:02d}-*.png"))) if (d / "takes" / "stills").is_dir() else 0
        takes = [t.suffixes[-2].lstrip(".") for t in (d / "takes" / "clips").glob(f"{num:02d}-*.mp4")] if (d / "takes" / "clips").is_dir() else []
        if canon:
            still = "✅ canon"
        elif cands:
            still = f"🗳 ballot open ({cands} candidates)"
        else:
            still = "⬜ none"
        motion = ", ".join(sorted(set(takes))) or "—"
        req = f'<a href="https://github.com/olegmlkvorg/banyan-city/issues/{reqs[num]}">#{reqs[num]}</a>' if num in reqs else "—"
        blocked = "founder vote" if not canon and cands else ("—" if canon else "render")
        rows.append(f"<tr><td>{num:02d}</td><td>{still}</td><td>{html.escape(motion)}</td>"
                    f"<td>{req}</td><td>{blocked}</td></tr>")
    return rows, sum(1 for s in shots if (d / "stills" / f"{s['num']:02d}-{s['slug']}.png").exists()), len(shots)


def spend():
    led = REPO / "ledger" / "render-spend.csv"
    total = 0.0
    for line in led.read_text().splitlines()[1:]:
        if line.strip():
            total += float(line.split(",")[5])
    return total


def build(out_dir: Path):
    d = REPO / "genomes/sapling/nodes/001-capability-inventory"
    rows, canon, total = beat_state(d)
    birdseye = birdseye_sections(REPO)
    est = "".join(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td></tr>" for a, b in ESTIMATES)
    body = f"""<!doctype html><meta charset="utf-8"><title>Status — the machine at work</title>
<style>body{{font:15px/1.5 -apple-system,system-ui,sans-serif;margin:2rem auto;max-width:900px;background:#0e0e12;color:#e8e8ee;padding:0 1rem}}
table{{border-collapse:collapse;width:100%;margin:1rem 0}}td,th{{border:1px solid #333;padding:.4rem .6rem;text-align:left;font-size:.9em}}
h1{{font-size:1.4rem}}.big{{font-size:1.6rem}}</style>
<h1>⚙️ Status — episode 001</h1>
<p class="big">{canon} / {total} beats canon · lifetime cash spend: ${spend():.2f}</p>
<p>Snapshot generated {time.strftime('%Y-%m-%d %H:%M')} (rebuilds on every push).
Pipeline: one free GPU lane (serialized) + the
<a href="https://github.com/olegmlkvorg/banyan-city/issues?q=label%3Arender-request">request marketplace</a>
(parallel, human-powered). The dominant bottleneck is whatever the Blocked-on
column says most often.</p>
{birdseye}<h2>Per-beat state</h2>
<table><tr><th>Beat</th><th>Still</th><th>Motion takes</th><th>Open request</th><th>Blocked on</th></tr>
{''.join(rows)}</table>
<h2>Stage estimates (measured)</h2>
<table><tr><th>Stage</th><th>Cost</th></tr>{est}</table>
<p><a href="index.html">← the city</a> · <a href="machine.html">how the machine works</a></p>"""
    (out_dir / "status.html").write_text(body)
    print(f"✓ status.html — {canon}/{total} canon, ${spend():.2f} lifetime")




def birdseye_sections(repo):
    """The public bird's-eye (founder directive 2026-07-30): inbox, fleet,
    latest thread activity. Public-safe only — no local paths, no keys."""
    import subprocess, html as h
    import yaml as y
    def sh(cmd):
        try:
            return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                  timeout=20, cwd=repo).stdout.strip()
        except Exception:
            return ""
    out = ""
    # founder inbox
    try:
        inbox = (y.safe_load((repo / "pipeline/pending-founder.yaml").read_text()) or {}).get("pending") or []
    except Exception:
        inbox = []
    out += "<h2>🕊 Waiting on the author</h2><ul>"
    out += "".join(f"<li><b>{h.escape(i.get('title',''))}</b> — {h.escape(i.get('detail',''))}</li>" for i in inbox) or "<li>nothing — the machine waits on no one</li>"
    out += "</ul>"
    # fleet
    sh("git fetch -q origin 'refs/heads/farm-results-*:refs/remotes/origin/farm-results-*'")
    rows = ""
    for b in sh("git branch -r | grep farm-results || true").splitlines():
        b = b.strip(); name = b.split("farm-results-")[-1]
        hb = sh(f"git show {b}:farm-out/heartbeat.txt 2>/dev/null | tail -1") or "no heartbeat"
        rows += f"<tr><td><b>{h.escape(name)}</b></td><td>{h.escape(hb)}</td></tr>"
    try:
        q = (y.safe_load((repo / "pipeline/farm-queue.yaml").read_text()) or {}).get("tasks") or []
        qtxt = ", ".join(t0.get("id","?") for t0 in q) or "empty (auto-refills)"
    except Exception:
        qtxt = "unknown"
    out += f"<h2>🖥 The farm (family machines rendering the show)</h2><table>{rows}</table><p><small>queue: {h.escape(qtxt)}</small></p>"
    # latest thread activity
    cs = sh("gh issue view 1 --json comments -q '.comments[-4:][] | .author.login + \"|\" + (.createdAt|.[0:16]) + \"|\" + (.body|.[0:100])' 2>/dev/null")
    rows = ""
    for l in cs.splitlines():
        if l.count("|") >= 2:
            a, w, b2 = l.split("|", 2)
            rows += f"<tr><td><b>{h.escape(a)}</b><br><small>{h.escape(w)}</small></td><td>{h.escape(b2)}…</td></tr>"
    out += f"<h2>🗳 Latest on the reactions thread</h2><table>{rows}</table>"
    out += "<p><a href='https://github.com/olegmlkvorg/banyan-city/issues/1'>join the thread</a> · <a href='sapling/001-capability-inventory-shots.html'>the shot board</a></p>"
    return out


if __name__ == "__main__":
    build(REPO / "_site")
