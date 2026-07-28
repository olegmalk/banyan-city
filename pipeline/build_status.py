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
<h2>Per-beat state</h2>
<table><tr><th>Beat</th><th>Still</th><th>Motion takes</th><th>Open request</th><th>Blocked on</th></tr>
{''.join(rows)}</table>
<h2>Stage estimates (measured)</h2>
<table><tr><th>Stage</th><th>Cost</th></tr>{est}</table>
<p><a href="index.html">← the city</a> · <a href="machine.html">how the machine works</a></p>"""
    (out_dir / "status.html").write_text(body)
    print(f"✓ status.html — {canon}/{total} canon, ${spend():.2f} lifetime")


if __name__ == "__main__":
    build(REPO / "_site")
