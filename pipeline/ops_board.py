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
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
import repo_slug  # noqa: E402  one source for "which repo is this"

OUT = Path.home() / "Desktop" / "banyan-drops" / "OPS.html"
NODE = REPO / "genomes/sapling/nodes/001-capability-inventory"


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace",
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




def fleet():
    """Every farm worker's last heartbeat, from its results branch."""
    sh(f"cd {REPO} && git fetch -q origin 'refs/heads/farm-results-*:refs/remotes/origin/farm-results-*' 2>/dev/null")
    out = sh(f"cd {REPO} && git branch -r | grep farm-results || true")
    rows = []
    for b in out.splitlines():
        b = b.strip()
        name = b.split("farm-results-")[-1]
        hb = sh(f"cd {REPO} && git show {b}:farm-out/heartbeat.txt 2>/dev/null | tail -1")
        rows.append((name, hb or "no heartbeat"))
    return rows


def queue_now():
    try:
        import yaml as _y
        q = (_y.safe_load((REPO / "pipeline/farm-queue.yaml").read_text()) or {}).get("tasks") or []
        return [f"{t.get('id')} → {t.get('worker')}" for t in q]
    except Exception:
        return []


def founder_inbox():
    """What is waiting on the author — through the ONE reader, not a second copy.

    This read its own copy out of `pipeline/pending-founder.yaml`, retired
    2026-08-14, and filtered `resolved:` no more than /status's did — so the same
    four answered calls the founder screenshotted on 2026-08-19 were also sitting
    on this dashboard, aging off their own `since:` dates. Two builders reading
    one dead file is not two bugs; it is one, and the fix is one reader.
    `build_status.inbox()` returns the `title`/`detail`/`since` shape this list
    already renders, so there is nothing here to keep in step by hand.
    """
    try:
        sys.path.insert(0, str(REPO / "pipeline"))
        import build_status
        return build_status.inbox()
    except Exception:
        return []


def latest_comments(n=4):
    out = sh("cd %s && gh issue view 1 --json comments -q "
             "'.comments[-%d:][] | .author.login + \"|\" + (.createdAt|.[0:16]) + \"|\" + (.body|.[0:110])'" % (REPO, n))
    return [l.split("|", 2) for l in out.splitlines() if l.count("|") >= 2]


def main():
    jobs = running_jobs()
    canon, total = canon_count()
    rp_bal, rp_pods = runpod()
    author, when, body = last_thread_comment()
    workers = fleet()
    queue = queue_now()
    inbox = founder_inbox()
    comments = latest_comments()
    ballots = sorted(set(open_ballots()))

    jobs_html = "".join(f"<tr><td>{html.escape(e)}</td><td>{html.escape(w)}</td></tr>"
                        for e, w in jobs) or "<tr><td colspan=2>— idle —</td></tr>"
    pods_html = "".join(f"<li>{p['name']} · {p['desiredStatus']} · ${p['costPerHr']}/hr</li>"
                        for p in rp_pods) or "<li>no pods running ($0/hr)</li>"
    moves = []
    if ballots:
        moves.append(f"<b>Vote beats {', '.join(f'{b:02d}' for b in ballots)}</b> — candidates on "
                     f"<a href='https://banyan.city/sapling/001-capability-inventory-shots'>the board</a>, "
                     f"verdicts on <a href='{repo_slug.REPO_URL}/issues/1'>the thread</a>")
    moves.append(f"PixVerse daily credits → <a href='{repo_slug.REPO_URL}"
                 "/issues?q=label%3Arender-request'>open requests</a>")
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
<h2>Rendering on THIS Mac (the farm renders remotely — see fleet below)</h2>
<table><tr><td width=90><b>elapsed</b></td><td><b>job</b></td></tr>{jobs_html}</table>
<h2>Your moves, in parallel</h2>
<ul>{''.join(f'<li>{m}</li>' for m in moves)}</ul>

<h2>🕊 Founder inbox — decisions only you can make</h2>
<ul>{''.join(f"<li><b>{html.escape(i.get('title',''))}</b> — {html.escape(i.get('detail',''))} <small>(since {i.get('since')})</small></li>" for i in inbox) or '<li>— empty: the machine is not waiting on you —</li>'}</ul>
<h2>Farm fleet</h2>
<table>{''.join(f"<tr><td width=90><b>{html.escape(n)}</b></td><td>{html.escape(h)}</td></tr>" for n, h in workers) or '<tr><td>no workers seen</td></tr>'}</table>
<p class="meta">queue: {html.escape(' · '.join(queue) if queue else 'empty')}</p>
<h2>Latest on the reactions thread</h2>
<table>{''.join(f"<tr><td width=110><b>{html.escape(a)}</b><br><small>{html.escape(w)}</small></td><td>{html.escape(b)}…</td></tr>" for a, w, b in comments)}</table>
<h2>Fresh artifacts (banyan-drops)</h2>
<ul>
<li><a href="model-bakeoff.html">model bake-off gallery</a> · <a href="m2-decision-card.html">M2 decision card</a> · <a href="extensive-15s-test.html">3-tier episode test</a> · <a href="fleet-benchmark.html">fleet benchmark</a></li>
<li>episode: <a href="ep1-remake-screening-v6.mp4">v6 screening cut</a> · <a href="banyan-ep1-remake.mp4">presentation copy</a></li>
</ul>
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
