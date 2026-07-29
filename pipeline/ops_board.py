#!/usr/bin/env python3
"""The live ops board — everything running, right now, on one auto-refreshing page.

Founder's ask (2026-07-29): "I want to constantly see everything you are doing,
all of the statistics, so I can also know what I can do in parallel."

Writes ~/Desktop/banyan-drops/OPS.html every run; a background loop reruns it
every ~20s. Local and live (the public banyan.city/status.html stays the
push-updated snapshot for everyone else).
"""

import html
import json
import os
import re
import subprocess
import time
import urllib.request
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = Path.home() / "Desktop" / "banyan-drops" / "OPS.html"
NODE = REPO / "genomes/sapling/nodes/001-capability-inventory"


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              timeout=20).stdout.strip()
    except Exception:
        return ""


BEAT_NAMES = {4: "his death at the desk", 6: "waking under the leaf-ceiling",
              7: "the panicked leaf-flail", 8: "the leaf goes still (sev-1)",
              9: "the quiet whoami sprout", 15: "the footsteps get closer"}
TACTICS = {"photobash": "repainting a collage built from the real approved leaf",
           "photobash2": "repainting a collage built from the real approved leaf",
           "scale-from9": "rebuilding at the true 15cm scale, from beat 9's approved frame",
           "violent-still": "the death-pose round — dramatic, not napping",
           "from8": "same field as beat 8, leaf mid-whip",
           "sketch": "repainting a hand-drawn layout"}


def running_jobs():
    """Only ACTUAL renders — a queued waiter loop contains the same script name
    in its command string and once masqueraded as a 20-minute job (2026-07-29)."""
    out = sh("ps -axo etime,command | grep -E 'still_local|post_motion|synth_vo|runpod_lane'"
             " | grep -v grep | grep -v 'while pgrep' | grep -v '/bin/zsh'")
    jobs = []
    for line in out.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) != 2 or "python" not in parts[1].split()[0].lower():
            continue
        m = re.search(r"--beat (\d+).*?--note (\S+)", parts[1])
        if m:
            num, note = int(m.group(1)), m.group(2)
            what = (f"Drawing candidates for beat {num:02d} — "
                    f"{BEAT_NAMES.get(num, '')} — {TACTICS.get(note, note)}")
        elif "post_motion" in parts[1]:
            what = "Animating an approved still (deterministic camera move, $0)"
        elif "synth_vo" in parts[1]:
            what = "Recording the narrator (voice engine, per-line emotion)"
        elif "runpod_lane" in parts[1]:
            what = "Rented-GPU round in progress (see RunPod balance below)"
        else:
            what = parts[1].split("/")[-1][:60]
        jobs.append((parts[0], what))
    return jobs


def canon_count():
    stills = len(list((NODE / "stills").glob("[0-9]*.png")))
    return stills, 15


def spend():
    total = 0.0
    led = REPO / "ledger" / "render-spend.csv"
    for line in led.read_text().splitlines()[1:]:
        if line.strip():
            try:
                total += float(line.split(",")[5])
            except (ValueError, IndexError):
                pass
    return total


def runpod():
    key = os.environ.get("RUNPOD_API_KEY", "")
    if not key:
        env = REPO / ".env"
        for l in env.read_text().splitlines():
            if l.startswith("RUNPOD_API_KEY="):
                key = l.split("=", 1)[1].strip()
    if not key:
        return "no key", []
    try:
        req = urllib.request.Request(
            "https://api.runpod.io/graphql",
            data=json.dumps({"query": "query { myself { clientBalance pods { name desiredStatus costPerHr } } }"}).encode(),
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json", "User-Agent": "curl/8.4.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            me = json.load(r)["data"]["myself"]
        pods = [p for p in me["pods"] if p["name"].startswith("banyan-")]
        return f"${me['clientBalance']:.2f}", pods
    except Exception as e:
        return f"api error ({type(e).__name__})", []


def last_thread_comment():
    out = sh("cd %s && gh issue view 1 --json comments "
             "-q '.comments[-1] | .author.login + \"|\" + (.createdAt|.[0:16]) + \"|\" + (.body|.[0:120])'" % REPO)
    return out.split("|", 2) if out.count("|") >= 2 else ("", "", "")


def open_ballots():
    """Beats with candidates but no canon still = waiting on the founder."""
    waiting = []
    for f in sorted((NODE / "takes" / "stills").glob("[0-9]*.png")):
        num = int(f.name[:2])
        slug_matches = list((NODE / "stills").glob(f"{num:02d}-*.png"))
        if not slug_matches and num not in [w[0] for w in waiting]:
            waiting.append((num, f.name))
    return [w[0] for w in waiting]


def main():
    jobs = running_jobs()
    canon, total = canon_count()
    rp_bal, rp_pods = runpod()
    author, when, body = last_thread_comment()
    ballots = sorted(set(open_ballots()))

    jobs_html = "".join(f"<tr><td>{html.escape(e)}</td><td>{html.escape(w)}</td></tr>"
                        for e, w in jobs) or "<tr><td colspan=2>— idle —</td></tr>"
    pods_html = "".join(f"<li>{p['name']} · {p['desiredStatus']} · ${p['costPerHr']}/hr</li>"
                        for p in rp_pods) or "<li>no pods running ($0/hr)</li>"
    moves = []
    if ballots:
        moves.append(f"<b>Vote beats {', '.join(f'{b:02d}' for b in ballots)}</b> — candidates on "
                     f"<a href='https://banyan.city/sapling/001-capability-inventory-shots'>the board</a>, "
                     f"verdicts on <a href='https://github.com/olegmlkvorg/banyan-city/issues/1'>the thread</a>")
    moves.append("PixVerse daily credits → <a href='https://github.com/olegmlkvorg/banyan-city/issues?q=label%3Arender-request'>open requests</a>")
    moves.append("Screening: the full cut, once stills close")

    OUT.write_text(f"""<!doctype html><meta charset="utf-8">
<meta http-equiv="refresh" content="20">
<title>OPS — live</title>
<style>body{{font:14px ui-monospace,Menlo,monospace;background:#0c0e10;color:#d7dde2;margin:2rem auto;max-width:820px;padding:0 1rem}}
h1{{font-size:1.1rem}} h2{{font-size:0.85rem;color:#8fa0ab;text-transform:uppercase;letter-spacing:.1em;margin:1.6rem 0 .4rem}}
table{{border-collapse:collapse;width:100%}}td{{border-bottom:1px solid #222b31;padding:.35rem .5rem .35rem 0}}
a{{color:#e8a15c}} .big{{font-size:1.5rem}} li{{margin:.2rem 0}}</style>
<h1>⚙️ OPS · {time.strftime('%H:%M:%S')} <small>(auto-refreshes every 20s)</small></h1>
<p class="big">{canon} / {total} stills canon · lifetime cash: ${spend():.2f}</p>
<h2>Rendering right now (this Mac)</h2>
<table><tr><td width=90><b>elapsed</b></td><td><b>job</b></td></tr>{jobs_html}</table>
<h2>Your moves, in parallel</h2>
<ul>{''.join(f'<li>{m}</li>' for m in moves)}</ul>
<h2>Resources</h2>
<ul>
<li>Kaggle GPU: <b>0 / 30 h</b> weekly — resets ~weekend</li>
<li>RunPod: balance <b>{html.escape(rp_bal)}</b></li>{pods_html}
<li>fal API: ~$9.72 reserve (founder-named spends)</li>
</ul>
<h2>Last thread activity</h2>
<p>{html.escape(author)} @ {html.escape(when)}: {html.escape(body)}…</p>
<p><a href="https://banyan.city/status.html">public status page</a> · board · thread linked above</p>
""")
    print(f"OPS.html written ({len(jobs)} jobs, {canon}/{total} canon)")


if __name__ == "__main__":
    main()
