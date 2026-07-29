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
IMAGE = "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
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


def cmd_render(beats: str, seeds: int) -> int:
    bal = balance()
    print(f"balance ${bal:.2f} · evening cap ${EVENING_CAP_USD:.2f}")
    key_b64 = base64.b64encode((Path.home() / ".ssh" / "banyan_runpod_deploy").read_bytes()).decode()
    script = (
        "bash -c '"
        "set -e; cd /workspace; "
        "git clone --depth 1 https://github.com/olegmlkvorg/banyan-city.git; "
        "cd banyan-city; pip -q install diffusers transformers accelerate safetensors pyyaml markdown; "
        f"BEATS={beats} SEEDS={seeds} DEPLOY_KEY=$DEPLOY_KEY python3 pipeline/runpod_render.py'"
    )
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
                    "env": [{"key": "DEPLOY_KEY", "value": key_b64}],
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
    print("watching the runpod-results branch; stop anytime with: runpod_lane.py stop")
    t0 = time.time()
    rate = float(pod["costPerHr"])
    try:
        while True:
            time.sleep(45)
            mins = (time.time() - t0) / 60
            if mins / 60 * rate > EVENING_CAP_USD:
                print("EVENING CAP REACHED — terminating")
                break
            r = subprocess.run(["git", "ls-remote", "origin", "runpod-results"],
                               cwd=REPO, capture_output=True, text=True)
            head = r.stdout.split()[0] if r.stdout.strip() else ""
            if head and head != getattr(cmd_render, "_seen", ""):
                if getattr(cmd_render, "_started", None) is None:
                    cmd_render._started = head  # branch may pre-exist; wait for a NEW head
                    cmd_render._seen = head
                    continue
                print("RESULTS ARRIVED")
                break
            cmd_render._seen = head
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
    return cmd_render(a.beats, a.seeds)


if __name__ == "__main__":
    sys.exit(main())
