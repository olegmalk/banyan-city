#!/usr/bin/env python3
"""Post a version milestone into a node's reaction issue — the public timeline.

Dad's design (2026-07-27): the reaction issue must hold the node's ENTIRE
history — first version, feedback, second version, feedback — so anyone opening
it sees the conversation between the show and its audience, in order. An empty
inbox teaches nothing; a timeline recruits.

    python3 pipeline/announce_version.py sapling 001 --title "v3 — new look" \
        --body "What changed and where to watch/react."

Posts a comment via `gh` to the issue in the node's sap/reactions.yaml.
Milestones only — published cuts, board openings, era changes — never every
candidate take (36 variant stills in one evening would bury the humans the
issue exists to host). The comment is the announcement; the artifacts stay in
git and on the site, linked.
"""

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("genome")
    ap.add_argument("node")
    ap.add_argument("--title", required=True)
    ap.add_argument("--body", required=True)
    a = ap.parse_args()

    nodes = REPO / "genomes" / a.genome / "nodes"
    d = next(x for x in sorted(nodes.iterdir())
             if x.is_dir() and x.name.startswith(a.node))
    rx = yaml.safe_load((d / "sap" / "reactions.yaml").read_text())
    issue = str(rx["issue"])

    body = f"## {a.title}\n\n{a.body}"
    r = subprocess.run(["gh", "issue", "comment", issue, "--body", body],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"gh failed:\n{r.stderr}")
    print(f"✓ posted to issue #{issue}: {a.title}\n  {r.stdout.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
