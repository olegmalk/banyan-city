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
    q = yaml.safe_load(Q.read_text()) or {}
    if q.get("tasks"):
        return "queue busy"
    stamp = int(time.time())
    seed_base = 20260719 + (stamp % 100000) * 100   # fresh seeds every round
    tasks = "# auto-refill by queue_keeper — rotating world bank\ntasks:\n"
    for slug, prompt in PROMPTS.items():
        tasks += f"""  - id: {slug}-{stamp}
    worker: msi
    node: 001-capability-inventory
    beats: ""
    slug: {slug}
    prompt: "{prompt}"
    seeds: 15
    seed_base: {seed_base}
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
