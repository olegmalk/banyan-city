#!/usr/bin/env python3
"""Intake a contributed beat take — the submission half of D11/D12.

A contributor took a task off the shot board (their tools, their key, or their
free compute) and produced a clip. This normalizes it into the tree:

    python3 pipeline/intake_take.py sapling 001 7 ~/Downloads/my-take.mp4 \
        --by "citizen-handle" --platform kling-app --model "Kling 2.5" \
        [--their-prompt "..."] [--their-cost-usd 0.35] [--tag KLING]

- copies to nodes/<node>/takes/clips/NN-slug.<TAG>.mp4 (the board picks it up
  on the next site build; the founder's screening decides what becomes canon)
- writes the §7.2 provenance sidecar from the stated facts
- appends a `type: compute` row to ledger/watering.csv crediting the
  contributor by name — contribution is visible and branch-ordering without
  any money touching the project (D12)

SAFETY FLOOR: this tool is run by a human (steward or founder) AFTER watching
the clip — nothing a stranger submits reaches the repo or the site unscreened.
That human screening is a floor (personal data, harm, legality), never taste;
taste is the founder's screening, later and in public.
"""

import argparse
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from generate_shots import parse_shots  # noqa: E402

LEDGER = REPO / "ledger" / "watering.csv"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("genome")
    ap.add_argument("node")
    ap.add_argument("beat", type=int)
    ap.add_argument("file", type=Path)
    ap.add_argument("--by", required=True, help="contributor handle for credit")
    ap.add_argument("--platform", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--their-prompt", default="",
                    help="only if they changed the board's prompt")
    ap.add_argument("--their-cost-usd", type=float, default=0.0,
                    help="what THEY spent on THEIR account (informational)")
    ap.add_argument("--tag", default="", help="filename tag; default = platform")
    ap.add_argument("--screened-by", default="steward",
                    help="the human who watched this before intake")
    a = ap.parse_args()

    if not a.file.exists():
        raise SystemExit(f"no such file: {a.file}")
    nodes = REPO / "genomes" / a.genome / "nodes"
    d = next(x for x in sorted(nodes.iterdir())
             if x.is_dir() and x.name.startswith(a.node))
    shot = next((s for s in parse_shots((d / "shots.md").read_text())
                 if s["num"] == a.beat), None)
    if not shot:
        raise SystemExit(f"no beat {a.beat} in {d.name}/shots.md")

    tag = (a.tag or a.platform).upper().replace(" ", "-")[:16]
    dest_dir = d / "takes" / "clips"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{a.beat:02d}-{shot['slug']}.{tag}.mp4"
    n = 2
    while dest.exists():
        dest = dest_dir / f"{a.beat:02d}-{shot['slug']}.{tag}{n}.mp4"
        n += 1
    shutil.copy(a.file, dest)

    dest.with_suffix(".meta.yaml").write_text(
        "# Shot provenance (7.2) — contributed take\n" + yaml.safe_dump({
            "contributed_by": a.by,
            "platform": a.platform, "model": a.model,
            "prompt": a.their_prompt or "(the board's recipe, unchanged)",
            "their_cost_usd": a.their_cost_usd,
            "cost_to_project_usd": 0,
            "screened_by": a.screened_by,
            "date": date.today().isoformat(),
        }, sort_keys=False, allow_unicode=True))

    if not LEDGER.exists() or not LEDGER.read_text().strip():
        LEDGER.write_text("date,node,leaf,citizen,type,amount_usd,compute_desc,split_applied,notes\n")
    with LEDGER.open("a") as f:
        f.write(f"{date.today().isoformat()},{d.name},{dest.name},{a.by},compute,0.00,"
                f"\"{a.platform}/{a.model} beat {a.beat:02d} (their spend ~${a.their_cost_usd:.2f})\","
                f"n/a,contributed take\n")

    print(f"✓ {dest.relative_to(REPO)}")
    print(f"✓ ledger credit: {a.by} (type: compute)")
    print("next: git add + commit + push — the board shows it on deploy; the")
    print("founder's screening (public thread) decides if it becomes canon.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
