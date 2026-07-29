#!/usr/bin/env python3
"""The fast lane controller — rents a GPU, runs a round, pays by the minute.

    python3 pipeline/runpod_lane.py render --beats 4,7 [--seeds 4]
    python3 pipeline/runpod_lane.py status
    python3 pipeline/runpod_lane.py stop            # terminate ALL our pods

Money rules (dad's authorization, 2026-07-28): $10 balance, $5 per evening cap,
every session ledgered to ledger/render-spend.csv with measured runtime. The
controller REFUSES to launch if it cannot see the balance, and `stop` is
idempotent — run it whenever in doubt; a terminated pod bills nothing.

Worker: pipeline/runpod_render.py, delivered via the public repo; results come
back on the `runpod-results` branch (repo-scoped deploy key = the courier).
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
API = "https://api.runpod.io/graphql"
GPU = "NVIDIA GeForce RTX 4090"
# cuda 11.8 runs on nearly any community driver — the 12.4 image hit
# "CUDA unknown error" on a 3090 host whose driver predated it (fire 7)
IMAGE = "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04"
EVENING_CAP_USD = 5.00
LEDGER = REPO / "ledger" / "render-spend.csv"


def gql(query: str, variables=None):
    key = os.environ.get("RUNPOD_API_KEY")
    if not key:
        raise SystemExit("set RUNPOD_API_KEY (it lives in .env)")
    req = urllib.request.Request(
        API, data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 # Cloudflare 403s the default python-urllib agent; curl-style UA passes
                 "User-Agent": "curl/8.4.0"})
    with urllib.request.urlopen(req) as r:
        out = json.load(r)
    if out.get("errors"):
        raise SystemExit(f"runpod: {out['errors']}")
    return out["data"]


def balance() -> float:
    return float(gql("query { myself { clientBalance } }")["myself"]["clientBalance"])


def our_pods():
    pods = gql("query { myself { pods { id name desiredStatus costPerHr } } }")["myself"]["pods"]
    return [p for p in pods if p["name"].startswith("banyan-")]


def log_spend(minutes: float, rate: float, note: str):
    est = round(minutes / 60 * rate, 2)
    with LEDGER.open("a") as f:
        f.write(f"{date.today().isoformat()},001,00,runpod,rtx4090,{est:.2f},"
                f"\"{note} ({minutes:.0f} min @ ${rate}/hr)\"\n")
    return est


def cmd_render(beats: str, seeds: int, init: str = "", strength: float = 0.5) -> int:
    bal = balance()
    print(f"balance ${bal:.2f} · evening cap ${EVENING_CAP_USD:.2f}")
    # a stale runpod-results branch is a landmine: fire 6 (2026-07-29) read
    # fire 5's old RENDER_FAIL heartbeat and killed a healthy 1-minute-old pod
    subprocess.run(["git", "push", "-q", "origin", ":runpod-results"],
                   cwd=REPO, capture_output=True)
    print("stale results branch cleared")
    key_b64 = base64.b64encode((Path.home() / ".ssh" / "banyan_runpod_deploy").read_bytes()).decode()
    # dockerArgs stays minimal — every past silent death lived in this string's
    # quoting. All logic is in runpod_boot.sh (versioned, heartbeats every
    # stage); all parameters travel as pod env vars, never inline shell.
    script = ("bash -c 'cd /workspace && "
              "git clone --depth 1 https://github.com/olegmlkvorg/banyan-city.git && "
              "bash banyan-city/pipeline/runpod_boot.sh'")
    pod_env = [{"key": "DEPLOY_KEY", "value": key_b64},
               {"key": "BEATS", "value": beats},
               {"key": "SEEDS", "value": str(seeds)},
               {"key": "INIT", "value": init},
               {"key": "STRENGTH", "value": str(strength)}]
    # community hosts vary wildly; ask lean, retry across GPU types — the first
    # live fire (2026-07-29) died on "machine does not have the resources" with
    # a 40GB disk ask. 25GB fits the model + deps comfortably.
    pod = None
    # (gpu, cloud) ladder: community first (cheap), secure last (reliable) —
    # the second fire found community sold out across three GPU types.
    LADDER = [(GPU, "COMMUNITY"), ("NVIDIA RTX A5000", "COMMUNITY"),
              ("NVIDIA GeForce RTX 3090", "COMMUNITY"), (GPU, "SECURE")]
    for gpu, cloud in LADDER:
        for attempt in range(3):
            try:
                data = gql("""
mutation($input: PodFindAndDeployOnDemandInput) {
  podFindAndDeployOnDemand(input: $input) { id costPerHr machine { gpuDisplayName } }
}""", {"input": {
                    "cloudType": cloud, "gpuTypeId": gpu, "gpuCount": 1,
                    "volumeInGb": 0, "containerDiskInGb": 25,
                    "name": f"banyan-render-{int(time.time())}",
                    "imageName": IMAGE,
                    "dockerArgs": script,
                    "env": pod_env,
                }})
                pod = data["podFindAndDeployOnDemand"]
                break
            except SystemExit as e:
                msg = str(e)
                if "does not have the resources" in msg:
                    print(f"  host too small ({gpu}/{cloud}, try {attempt+1}) — rematching")
                    time.sleep(3)
                    continue
                if "no longer any instances" in msg or "SUPPLY" in msg:
                    print(f"  {gpu}/{cloud}: sold out — next rung")
                    break
                raise
        if pod:
            break
    if not pod:
        raise SystemExit("no suitable community host found — try again in a few minutes")
    print(f"pod {pod['id']} on {pod['machine']['gpuDisplayName']} @ ${pod['costPerHr']}/hr")
    print("watching heartbeats on the runpod-results branch; stop anytime with: runpod_lane.py stop")
    t0 = time.time()
    rate = float(pod["costPerHr"])
    QUIET_LIMIT = 8 * 60          # no NEW heartbeat for this long = dead worker
    last_beat, last_change = "", time.time()
    try:
        while True:
            time.sleep(30)
            mins = (time.time() - t0) / 60
            if mins / 60 * rate > EVENING_CAP_USD:
                print("EVENING CAP REACHED — terminating")
                break
            subprocess.run(["git", "fetch", "-q", "origin", "runpod-results"],
                           cwd=REPO, capture_output=True)
            hb = subprocess.run(["git", "show", "origin/runpod-results:runpod-out/heartbeat.txt"],
                                cwd=REPO, capture_output=True, text=True).stdout.strip()
            if not hb.startswith(last_beat):
                last_beat = ""    # branch was rewritten (fresh worker) — start over
            if hb != last_beat:
                for line in hb[len(last_beat):].strip().splitlines():
                    print(f"  ♥ {line}", flush=True)
                last_beat, last_change = hb, time.time()
            tail = hb.splitlines()[-1] if hb else ""
            if "DONE" in tail:
                print("RESULTS ARRIVED")
                break
            if "FAIL" in tail:
                print("WORKER FAILED — log is on the branch: "
                      "git show origin/runpod-results:runpod-out/worker-log.txt")
                break
            if time.time() - last_change > QUIET_LIMIT:
                stage = tail or "never sent STARTED (boot/clone/quoting problem)"
                print(f"NO HEARTBEAT for {QUIET_LIMIT//60} min — last stage: {stage} — terminating")
                break
    finally:
        gql("mutation($id: String!) { podTerminate(input: {podId: $id}) }", {"id": pod["id"]})
        mins = (time.time() - t0) / 60
        est = log_spend(mins, rate, f"stills round beats {beats}")
        print(f"pod terminated · {mins:.0f} min · ~${est:.2f} ledgered")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["render", "status", "stop"])
    ap.add_argument("--beats", default="")
    ap.add_argument("--seeds", type=int, default=4)
    ap.add_argument("--init", default="", help="repo-relative init image (img2img)")
    ap.add_argument("--strength", type=float, default=0.5)
    a = ap.parse_args()
    if a.cmd == "status":
        print(f"balance ${balance():.2f}")
        for p in our_pods():
            print(f"  {p['id']} {p['name']} {p['desiredStatus']} ${p['costPerHr']}/hr")
        return 0
    if a.cmd == "stop":
        for p in our_pods():
            gql("mutation($id: String!) { podTerminate(input: {podId: $id}) }", {"id": p["id"]})
            print(f"terminated {p['id']}")
        return 0
    if not a.beats:
        raise SystemExit("--beats required")
    return cmd_render(a.beats, a.seeds, a.init, a.strength)


if __name__ == "__main__":
    sys.exit(main())
