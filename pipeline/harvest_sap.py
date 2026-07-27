#!/usr/bin/env python3
"""Sap harvester — the reaction loop as open data (Guideline 4).

For every node whose sap/reactions.yaml maps it to a GitHub issue,
fetch the issue's reactions and comment count and write a dated
summary to sap/summary.yaml. Run by CI on a schedule; the diffs are
the tree's public vital signs.

Auth: GITHUB_TOKEN env var (provided automatically in Actions).
"""

import csv
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_DIR = Path(__file__).resolve().parent.parent
API = "https://api.github.com"
GH_REPO = os.environ.get("GITHUB_REPOSITORY", "olegmlkvorg/banyan-city")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
# traffic endpoints need admin:read, which Actions' built-in token lacks —
# a founder-created fine-grained PAT (secret TRAFFIC_TOKEN) covers them
TRAFFIC_TOKEN = os.environ.get("TRAFFIC_TOKEN") or TOKEN

# GitHub reaction content types, in display order
REACTION_KINDS = ["+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"]


def gh(path: str, token: str | None = None):
    req = urllib.request.Request(f"{API}{path}")
    req.add_header("Accept", "application/vnd.github+json")
    tok = token or TOKEN
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def harvest_node(node_dir: Path) -> bool:
    reactions_file = node_dir / "sap" / "reactions.yaml"
    if not reactions_file.exists():
        return False
    channel = yaml.safe_load(reactions_file.read_text())
    if channel.get("channel") != "github_issue":
        return False
    issue_no = channel["issue"]

    issue = gh(f"/repos/{GH_REPO}/issues/{issue_no}")
    tally = issue.get("reactions", {})
    summary = {
        "harvested_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "channel": {"github_issue": issue_no, "url": channel.get("url")},
        "comments": issue.get("comments", 0),
        "reactions": {k: tally.get(k, 0) for k in REACTION_KINDS},
        "reactions_total": tally.get("total_count", 0),
    }
    out = node_dir / "sap" / "summary.yaml"
    header = "# Sap summary — open data, written by pipeline/harvest_sap.py\n"
    new_body = yaml.safe_dump(summary, sort_keys=False)

    # Skip the write when only the timestamp would change — keeps the
    # scheduled run from committing noise on quiet days.
    if out.exists():
        old = yaml.safe_load(out.read_text())
        old.pop("harvested_at", None)
        cmp = dict(summary)
        cmp.pop("harvested_at")
        if old == cmp:
            return False
    out.write_text(header + new_body)
    return True


def parse_screening_issue(body: str):
    """Parse a screening issue-form body into (leaf_id, scores, note)."""
    sections = dict(re.findall(r"### ([^\n]+)\n\n(.*?)(?=\n### |\Z)", body or "", re.S))
    leaf = None
    scores = {}
    note = ""
    for label, answer in sections.items():
        answer = answer.strip()
        if label.startswith("Leaf ID"):
            leaf = answer.split()[0] if answer else None
        elif label.startswith("The wince"):
            note = "" if answer == "_No response_" else answer
        else:
            m = re.match(r"([1-5])", answer)
            if m:
                key = label.split(" (")[0].strip().lower().replace(" ", "_")
                scores[key] = int(m.group(1))
    return leaf, scores, note


def harvest_screening(genome_dirs: list) -> int:
    """Tally screening-form issues into each node's sap/screening.yaml."""
    try:
        issues = gh(f"/repos/{GH_REPO}/issues?labels=screening&state=all&per_page=100")
    except urllib.error.URLError as e:
        # HTTPError subclasses URLError — one guard covers both;
        # skip the tally rather than fail the whole harvest
        print(f"screening: issues API failed ({e}) — skipped")
        return 0
    by_leaf = {}
    for issue in issues:
        leaf, scores, note = parse_screening_issue(issue.get("body", ""))
        if not leaf or not scores:
            continue
        entry = by_leaf.setdefault(leaf, {"ratings": 0, "sums": {}, "winces": []})
        entry["ratings"] += 1
        for k, v in scores.items():
            entry["sums"][k] = entry["sums"].get(k, 0) + v
        if note:
            # ISSUE NUMBER ONLY — never the text. This harvester auto-commits daily
            # with no human in the loop, and R6 makes every commit permanent: a
            # malicious "wince" (a real name, an address, a slur) pasted into a
            # public issue would have entered the repo forever within 24h
            # (principles audit 2026-07-27, finding #2). The text stays on GitHub,
            # where it can be moderated and where its author controls it.
            entry["winces"].append({"issue": issue["number"], "has_note": True})

    changed = 0
    for genome_dir in genome_dirs:
        lineage = yaml.safe_load((genome_dir / "lineage.yaml").read_text())
        for node in lineage["nodes"]:
            try:
                leaves = {l: by_leaf[l] for l in (node.get("leaves") or []) if l in by_leaf}
                if not leaves:
                    continue
                summary = {
                    "harvested_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "leaves": {
                        leaf: {
                            "ratings": e["ratings"],
                            "means": {k: round(s / e["ratings"], 2) for k, s in e["sums"].items()},
                            "winces": e["winces"],
                        }
                        for leaf, e in leaves.items()
                    },
                }
                out = genome_dir / "nodes" / node["slug"] / "sap" / "screening.yaml"
                header = "# Screening summary — open data, written by pipeline/harvest_sap.py\n"
                if out.exists():
                    old = yaml.safe_load(out.read_text())
                    old.pop("harvested_at", None)
                    cmp = dict(summary)
                    cmp.pop("harvested_at")
                    if old == cmp:
                        continue
                out.write_text(header + yaml.safe_dump(summary, sort_keys=False))
                print(f"screening: {out.relative_to(REPO_DIR)}")
                changed += 1
            except Exception as e:
                # one node's corrupt summary must not abort the tally
                print(f"screening: node {node.get('id', '?')} failed ({e}) — skipped")
    return changed


REACH_FIELDS = ["date", "views", "uniques", "clones", "clone_uniques", "top_referrers"]


def harvest_reach() -> bool:
    """Record repo traffic (views/clones/referrers) in ledger/reach.csv.

    Views and clones arrive per-day for a rolling 14-day window; rows for
    dates already in the csv are replaced, because GitHub revises recent
    days and the current day is always partial. Referrers have no per-day
    breakdown, so each refreshed row carries the current 14-day snapshot.
    """
    try:
        views = gh(f"/repos/{GH_REPO}/traffic/views", token=TRAFFIC_TOKEN)
        clones = gh(f"/repos/{GH_REPO}/traffic/clones", token=TRAFFIC_TOKEN)
        referrers = gh(f"/repos/{GH_REPO}/traffic/popular/referrers", token=TRAFFIC_TOKEN)
    except urllib.error.HTTPError as e:
        # traffic endpoints need push access — a read-only token gets 403;
        # skip rather than fail the whole harvest
        print(f"reach: traffic API returned {e.code} — skipped (token needs push access)")
        return False
    except urllib.error.URLError as e:
        print(f"reach: traffic API unreachable ({e.reason}) — skipped")
        return False

    days = {}

    def day(ts):
        return days.setdefault(ts[:10], {"views": 0, "uniques": 0, "clones": 0, "clone_uniques": 0})

    for v in views.get("views", []):
        d = day(v["timestamp"])
        d["views"], d["uniques"] = v["count"], v["uniques"]
    for c in clones.get("clones", []):
        d = day(c["timestamp"])
        d["clones"], d["clone_uniques"] = c["count"], c["uniques"]
    ref_str = ";".join(f"{r['referrer']}:{r['count']}" for r in referrers)

    out = REPO_DIR / "ledger" / "reach.csv"
    rows = {}
    if out.exists():
        with out.open(newline="") as f:
            rows = {row["date"]: row for row in csv.DictReader(f)}
    for date, d in days.items():
        rows[date] = {"date": date, **{k: str(v) for k, v in d.items()}, "top_referrers": ref_str}

    buf = io.StringIO()
    # csv defaults to \r\n, which read_text() normalizes away — the
    # no-change comparison (and git) needs plain \n
    writer = csv.DictWriter(buf, fieldnames=REACH_FIELDS, restval="", lineterminator="\n")
    writer.writeheader()
    for date in sorted(rows):
        writer.writerow(rows[date])
    body = buf.getvalue()
    if out.exists() and out.read_text() == body:
        return False
    out.parent.mkdir(exist_ok=True)
    out.write_text(body)
    print(f"reach: {out.relative_to(REPO_DIR)}")
    return True


def main() -> int:
    changed = 0
    genome_dirs = [p for p in sorted((REPO_DIR / "genomes").iterdir()) if (p / "lineage.yaml").exists()]
    for genome_dir in genome_dirs:
        nodes_dir = genome_dir / "nodes"
        for node_dir in sorted(nodes_dir.iterdir()):
            if not node_dir.is_dir():
                continue
            try:
                if harvest_node(node_dir):
                    print(f"harvested: {node_dir.relative_to(REPO_DIR)}")
                    changed += 1
            except Exception as e:
                # one node's failed fetch or corrupt yaml must not abort
                # the whole nightly harvest — note it and move on
                print(f"harvest: {node_dir.relative_to(REPO_DIR)} failed ({e}) — skipped")
    changed += harvest_screening(genome_dirs)
    changed += harvest_reach()
    print(f"✓ sap harvest complete — {changed} file(s) updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
