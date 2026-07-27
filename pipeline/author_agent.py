#!/usr/bin/env python3
"""The author-agent — applies the taste file to candidates (PRD §7.2 step 3, Phase 4).

Two modes:

  select <genome> <node-id>
      Read the tree's taste file, the node's live leaves, and its
      screening data; ask the model to select the canonical leaf.
      Writes nodes/<slug>/selection.yaml — the edit decision record —
      and prints a commit-message-style summary citing rule IDs.
      Selection decides sequence and trunk, never existence (R6):
      non-selected candidates are deferrals, not deletions.

  blindset <blindset.yaml>
      Validation harness (Phase 4 acceptance: >=90% agreement on a
      20-candidate blind set). For each item the agent picks among
      candidates without seeing the author's pick; agreement % is the
      taste-fidelity metric (PRD §12). Divergences are the bug list
      that drives the next taste-file amendment.

Both modes accept --dry-run to print the assembled request without
calling the API. Requires ANTHROPIC_API_KEY (or an `ant auth login`
profile) for live runs. The model never overrides a human commit; a
wrong selection is fixed by amending the taste file, never this code.
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
MODEL = "claude-opus-4-8"

SELECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "selected": {
            "type": "string",
            "description": "ID of the winning candidate",
        },
        "rules_cited": {
            "type": "array",
            "description": "Taste rules that drove the selection, each with a one-sentence reason",
            "items": {
                "type": "object",
                "properties": {
                    "rule": {"type": "string", "description": "Rule ID, e.g. R3"},
                    "reason": {"type": "string"},
                },
                "required": ["rule", "reason"],
                "additionalProperties": False,
            },
        },
        "deferrals": {
            "type": "array",
            "description": "Non-selected candidates. Per R6 these are deferrals, never deletions — each gets a rule ID and a one-sentence reason.",
            "items": {
                "type": "object",
                "properties": {
                    "candidate": {"type": "string"},
                    "rule": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["candidate", "rule", "reason"],
                "additionalProperties": False,
            },
        },
        "wince_notes": {
            "type": "array",
            "description": "Moments WITHIN candidates (R4/R6 wince test) that a rule fails to cover cleanly — raw material for taste-file amendments",
            "items": {"type": "string"},
        },
    },
    "required": ["selected", "rules_cited", "deferrals", "wince_notes"],
    "additionalProperties": False,
}

SYSTEM = """You are the author-agent of a story tree. You do not have taste of your own; \
you apply the tending author's extracted taste file, exactly as written, to a shortlist of candidates.

Rules of engagement:
- Select exactly one candidate. Cite the rule ID(s) that drove the selection.
- Every non-selected candidate is a deferral, never a rejection (R6): give each a rule ID and a one-sentence reason.
- Apply the wince test to moments WITHIN candidates, not whole candidates.
- If the taste file cannot cleanly decide between candidates, still pick one, and record what the \
taste file failed to cover in wince_notes — those notes are how the taste file gets amended.
- Never invent rules. If a judgement isn't grounded in a rule, it belongs in wince_notes, not in rules_cited."""


def build_request(taste: str, task: str) -> dict:
    return {
        "model": MODEL,
        "max_tokens": 16000,
        "thinking": {"type": "adaptive"},
        "output_config": {"format": {"type": "json_schema", "schema": SELECTION_SCHEMA}},
        "system": SYSTEM,
        "messages": [{"role": "user", "content": f"# Taste file\n\n{taste}\n\n---\n\n{task}"}],
    }


def call_model(request: dict) -> dict:
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(**request)
    if response.stop_reason == "refusal":
        raise SystemExit("model refused the request; see stop_details")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def load_candidates(genome: str, node_id: str):
    genome_dir = REPO / "genomes" / genome
    lineage = yaml.safe_load((genome_dir / "lineage.yaml").read_text())
    node = next(n for n in lineage["nodes"] if n["id"] == node_id)
    node_dir = genome_dir / "nodes" / node["slug"]

    candidates = []
    for leaf_id in node.get("leaves") or []:
        meta = yaml.safe_load((node_dir / "leaves" / f"{leaf_id}.yaml").read_text())
        if meta.get("status") != "live":
            continue
        content_file = node_dir / "leaves" / str(meta.get("content", ""))
        if str(meta.get("content")) == "../node.md":
            content_file = node_dir / "node.md"
        body = content_file.read_text() if content_file.exists() else "(no content file)"
        candidates.append({"id": leaf_id, "tier": meta.get("tier"), "content": body})

    screening_file = node_dir / "sap" / "screening.yaml"
    screening = screening_file.read_text() if screening_file.exists() else "none yet"
    taste_file = REPO / Path(yaml.safe_load((genome_dir / "tree.yaml").read_text())["tree"]["taste_file"])
    return node, node_dir, candidates, taste_file.read_text(), screening


def cmd_select(args) -> int:
    node, node_dir, candidates, taste, screening = load_candidates(args.genome, args.node)
    if len(candidates) < 2:
        print(f"node {args.node} has {len(candidates)} live leaf/leaves — nothing to select between")
        return 0

    parts = [f"# Task\n\nSelect the canonical leaf for node {node['id']} — \"{node['title']}\".\n"]
    parts.append(f"# Screening data (the crowd narrows; you decide)\n\n{screening}\n")
    for c in candidates:
        parts.append(f"# Candidate `{c['id']}` (tier {c['tier']})\n\n{c['content']}\n")
    request = build_request(taste, "\n---\n\n".join(parts))

    if args.dry_run:
        print(json.dumps({**request, "messages": [{"role": "user", "content": f"<{len(request['messages'][0]['content'])} chars>"}]}, indent=2))
        return 0

    decision = call_model(request)
    out = node_dir / "selection.yaml"
    out.write_text(
        "# Edit decision record — written by pipeline/author_agent.py (PRD §7.2 step 3)\n"
        "# The human reviews this log; a wrong selection is fixed by amending the\n"
        "# taste file, never by overriding this record.\n"
        + yaml.safe_dump({"model": MODEL, **decision}, sort_keys=False)
    )
    cites = "; ".join(f"{r['rule']} {r['reason']}" for r in decision["rules_cited"])
    print(f"selected {decision['selected']}: {cites}")
    for d in decision["deferrals"]:
        print(f"deferred {d['candidate']}: {d['rule']} — {d['reason']}")
    for w in decision["wince_notes"]:
        print(f"wince: {w}")
    print(f"→ {out.relative_to(REPO)}")
    return 0


def cmd_blindset(args) -> int:
    blindset = yaml.safe_load(Path(args.blindset).read_text())
    taste = (REPO / blindset["taste_file"]).read_text()

    agreements, results = 0, []
    for item in blindset["items"]:
        parts = [f"# Task\n\nSelect the candidate that best fits the taste file. Item: {item['id']}\n"]
        for c in item["candidates"]:
            parts.append(f"# Candidate `{c['id']}`\n\n{c['text']}\n")
        request = build_request(taste, "\n---\n\n".join(parts))
        if args.dry_run:
            print(f"{item['id']}: would send {len(request['messages'][0]['content'])} chars, "
                  f"{len(item['candidates'])} candidates (author picked {item['author_pick']})")
            continue
        decision = call_model(request)
        agree = decision["selected"] == item["author_pick"]
        agreements += agree
        results.append({"item": item["id"], "agent": decision["selected"],
                        "author": item["author_pick"], "agree": agree,
                        "rules_cited": decision["rules_cited"]})
        print(f"{item['id']}: agent={decision['selected']} author={item['author_pick']} {'✓' if agree else '✗ DIVERGENCE'}")

    if args.dry_run:
        return 0
    n = len(blindset["items"])
    pct = 100 * agreements / n if n else 0
    print(f"\ntaste fidelity: {agreements}/{n} = {pct:.0f}% (target ≥ {blindset.get('target_pct', 90)}%)")
    out = Path(args.blindset).with_suffix(".results.yaml")
    out.write_text(yaml.safe_dump({"model": MODEL, "agreement_pct": pct, "results": results}, sort_keys=False))
    print(f"→ {out}")
    return 0 if pct >= blindset.get("target_pct", 90) else 1


def main() -> int:
    # Runs against the CALLER's ANTHROPIC_API_KEY by design (WATERING.md: compute
    # as watering) — but it must say so before it bills them (audit finding #6).
    if "--yes" not in sys.argv:
        raise SystemExit("author_agent calls the Anthropic API on YOUR key (your money,"
                         " your contribution). Re-run with --yes to acknowledge.")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select", help="select the canonical leaf for a node")
    s.add_argument("genome")
    s.add_argument("node")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_select)
    b = sub.add_parser("blindset", help="score agent-vs-author agreement on a blind set")
    b.add_argument("blindset")
    b.add_argument("--dry-run", action="store_true")
    b.set_defaults(fn=cmd_blindset)
    args = parser.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
