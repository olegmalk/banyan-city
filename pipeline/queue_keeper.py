#!/usr/bin/env python3
"""Keeps the msi fed (dad's utilization directive, 2026-07-30): when the farm
queue is empty, append a world-bank batch with a fresh seed base so every
round explores NEW options for the approved node-001 world. $0, runs on the
steward's Mac in a loop."""
import subprocess, time
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parent.parent
Q = REPO / "pipeline/farm-queue.yaml"
PROMPTS = {
    "keep-field-gold": "no humans, the wide grass field in late golden hour, long shadows, the tiny sprout glowing rim-lit in the foreground, warm cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No people, no trees. No photorealism, no 3D render look. 9:16 vertical, no text.",
    "keep-sky-moods": "no humans, dramatic sky over the grass field, towering clouds catching colored light, the sprout small against the vastness, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No people, no city. No photorealism, no 3D render look. 9:16 vertical, no text.",
    "keep-macro-dew": "no humans, macro close-up of dew drops on young green leaves, morning light refracting, soft bokeh grass behind, cinematic lighting, detailed, newest, masterpiece, best quality, very aesthetic No people, no hands. No photorealism, no 3D render look. 9:16 vertical, no text.",
}

def cycle():
    subprocess.run(["git", "pull", "-q", "--rebase", "origin", "main"], cwd=REPO, capture_output=True)
    subprocess.run(["git", "fetch", "-q", "origin",
                    "refs/heads/farm-results-*:refs/remotes/origin/farm-results-*"],
                   cwd=REPO, capture_output=True)
    q = yaml.safe_load(Q.read_text()) or {}
    tasks = q.get("tasks") or []
    if tasks:
        # busy only if some listed task is NOT yet DONE per its worker's
        # heartbeat — a finished task left in the file is not work
        # (the 4-hour "queue busy" nap of 2026-07-30)
        undone = []
        for tk in tasks:
            w = tk.get("worker", "any")
            hb = subprocess.run(["git", "show", f"origin/farm-results-{w}:farm-out/heartbeat.txt"],
                                cwd=REPO, capture_output=True, text=True).stdout
            if f"DONE task={tk.get('id')}" not in hb and f"FAIL task={tk.get('id')}" not in hb:
                undone.append(tk.get("id"))
        if undone:
            return f"queue busy ({len(undone)} live)"
    stamp = int(time.time())
    seed_base = 20260719 + (stamp % 100000) * 100   # fresh seeds every round
    # PRODUCTION rotation (founder 2026-07-30: "keep the msi working — let's
    # produce"), all §6-legal on the approved episode 1:
    #   - fresh candidate frames for the OPEN render requests (ballot fodder)
    #   - hi-res (1080x1576) upgrade candidates for every canon beat, five
    #     beats per round, for the pending founder hi-res review
    # The world bank keeps only a small m1pro share (refs stay useful).
    OPEN_BEATS = "3,6,7,9,10,12,14"                 # requests.yaml, node 001
    HIRES = ["1,2,3,4,5", "6,7,8,9,10", "11,12,13,14,15"][stamp // 180 % 3]
    tasks = "# auto-refill by queue_keeper — PRODUCTION rotation\ntasks:\n"
    tasks += f"""  - id: prod-open-msi-{stamp}
    worker: msi
    node: 001-capability-inventory
    beats: "{OPEN_BEATS}"
    seeds: 6
    seed_base: {seed_base}
  - id: prod-hires-msi-{stamp}
    worker: msi
    node: 001-capability-inventory
    beats: "{HIRES}"
    width: 1080
    height: 1576
    seeds: 4
    seed_base: {seed_base + 31}
  - id: prod-open-m1pro-{stamp}
    worker: m1pro
    node: 001-capability-inventory
    beats: "{OPEN_BEATS}"
    seeds: 2
    seed_base: {seed_base + 63}
  - id: keep-m1pro-{stamp}
    worker: m1pro
    node: 001-capability-inventory
    beats: ""
    slug: keep-macro-dew
    prompt: "{PROMPTS['keep-macro-dew']}"
    seeds: 2
    seed_base: {seed_base + 7}
"""
    Q.write_text(tasks)
    subprocess.run(["git", "add", str(Q)], cwd=REPO)
    subprocess.run(["git", "commit", "-qm", f"queue_keeper: refill {stamp}"], cwd=REPO)
    subprocess.run(["git", "push", "-q"], cwd=REPO)
    return f"refilled (seed_base {seed_base})"

if __name__ == "__main__":
    while True:
        try:
            print(f"[{time.strftime('%H:%M')}] {cycle()}", flush=True)
        except Exception as e:
            print(f"keeper error: {e!r}", flush=True)
        time.sleep(180)
