#!/usr/bin/env python3
"""Open render-request issues — the directed half of the crowd marketplace.

Dad's design (2026-07-28): requests flow programmatically. The founder (from
anywhere) can say "here is the image and the prompt — generate the video with
YOUR ai and hand it back," and any fulfiller — family or stranger — returns
the file. The shot board is the passive half (recipes, standing takes); this
opens the active half: one GitHub issue per beat that WANTS a take, holding
everything a fulfiller needs, with the return path being a drag-and-drop
comment (GitHub hosts mp4 attachments).

    python3 pipeline/make_requests.py sapling 001 [--beats 2,13] [--dry-run]

Creates label `render-request` if missing; one issue per approved-still beat
that lacks an AI take (POST doesn't count — it's the deterministic baseline).
Skips beats that already have an open request. Returned takes are screened by
a human, then intaken via pipeline/intake_take.py (provenance + ledger credit).
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from generate_shots import parse_shots  # noqa: E402

SITE = "https://banyan.city"

BODY = """A take is requested for this beat. Generate with YOUR tools ({d12}), drag the
resulting video file into a comment below (or link it), and say what you used.

**Input image (the approved still — the video must start from/respect it):**
{img}

**Motion prompt:**
```
{motion}
```

**Settings:** 9:16 vertical · 5-6 seconds · no audio · single locked shot (no cuts)

**What happens next:** a human screens every submission (safety floor, never
taste), then it lands on the [shot board]({board}) with your name in the public
ledger. The founder's screening decides what the episode keeps (R4).
"""


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit(f"gh {' '.join(args[:3])}… failed:\n{r.stderr}")
    return r.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("genome")
    ap.add_argument("node")
    ap.add_argument("--beats", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    nodes = REPO / "genomes" / a.genome / "nodes"
    d = next(x for x in sorted(nodes.iterdir())
             if x.is_dir() and x.name.startswith(a.node))
    MOTION = (yaml.safe_load((d / "motion.yaml").read_text()) or {}).get("motion_prompts", {})
    want = {int(b) for b in a.beats.split(",") if b.strip()} if a.beats else None

    labels = gh("label", "list", "--json", "name")
    if "render-request" not in labels:
        gh("label", "create", "render-request", "--color", "1d76db",
           "--description", "a beat wants a take — bring your own AI (D12)")

    existing = json.loads(gh("issue", "list", "--label", "render-request",
                             "--state", "open", "--json", "title"))
    open_titles = {e["title"] for e in existing}

    made = 0
    for s in parse_shots((d / "shots.md").read_text()):
        num = s["num"]
        if want and num not in want:
            continue
        still = d / "stills" / f"{num:02d}-{s['slug']}.png"
        if not still.exists() or num not in MOTION:
            continue
        ai_takes = [t for t in (d / "takes" / "clips").glob(f"{num:02d}-*.mp4")
                    if ".POST." not in t.name]
        if ai_takes and not want:
            continue  # already has an AI take; only re-request explicitly
        title = f"🎬 Render request: {d.name} — beat {num:02d} ({s['slug']})"
        if title in open_titles:
            continue
        img = f"{SITE}/{a.genome}/{d.name}-media/{still.name}"
        body = BODY.format(
            d12="your accounts, your credits — no money touches the project",
            img=img, motion=MOTION[num],
            board=f"{SITE}/{a.genome}/{d.name}-shots")
        if a.dry_run:
            print(f"would open: {title}")
        else:
            url = gh("issue", "create", "--title", title, "--body", body,
                     "--label", "render-request")
            print(f"✓ {url}")
            rq = d / "requests.yaml"
            reqs = (yaml.safe_load(rq.read_text()) if rq.exists() else {}) or {}
            reqs.setdefault("render_requests", {})[num] = int(url.rstrip("/").rsplit("/", 1)[-1])
            rq.write_text(yaml.safe_dump(reqs, sort_keys=True))
        made += 1
    print(f"{made} request(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
