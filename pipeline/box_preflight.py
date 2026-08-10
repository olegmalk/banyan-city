#!/usr/bin/env python3
"""Check, on the box, that a queued render job would actually run.

Everything here answers a question that can only be answered where the render
happens. The Mac can guess at all of it and has been wrong about each one:

  * §6 approval -- a job naming a node whose newest T0 leaf lacks
    `approved_by: founder` does not fail that job, it raises SystemExit inside
    farm_worker and takes the whole daemon down (farm_worker.py:517/:539). The
    same trap is one import away from any renderer. Checking approval BEFORE a
    job is queued is the difference between one red job and a dead card.
  * the plate -- ltx_i2v takes `init` literally and does no repo-relative
    resolution, so a path that exists on the Mac and not on the box is a job
    that dies several minutes in, after paying the weight-load cost.
  * token counts -- `sd_prompt.negative_tokens` returns an exact CLIP count only
    where the tokenizer is importable and a prose over-estimate everywhere else.
    The Mac runs the estimator. 77 is a hard budget for the stills path, and
    terms are shed silently at the boundary, so an unmeasured prompt is a prompt
    nobody has actually read.

Writes a YAML report and exits nonzero if anything a job depends on is missing,
so it can sit in the queue as a dependency of the renders it clears.

    python box_preflight.py --repo C:\\banyan-farm\\banyan-city \\
        --out C:\\banyan-queue\\preflight.yaml [--node 001-capability-inventory ...]
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import platform
import socket
import sys

# Nodes a job may name. Anything absent from the approved set is reported as
# BLOCKED rather than merely unapproved: the point is that queueing it is unsafe,
# not that its script is bad.
DEFAULT_NODES = ("001-capability-inventory", "002b-first-citizen")


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def newest_t0_leaf(node_dir: str):
    leaves = os.path.join(node_dir, "leaves")
    if not os.path.isdir(leaves):
        return None
    names = sorted(n for n in os.listdir(leaves)
                   if "-t0-" in n and n.endswith(".yaml"))
    return os.path.join(leaves, names[-1]) if names else None


def _scalar_of(line: str) -> str:
    """The value of a `key: value` line, minus quotes and any trailing comment.

    The comment matters: 001's leaf writes the founder's actual words after a
    `#` on the approved_by line, and farm_worker sees them stripped because it
    goes through a yaml parser. Keeping them here would make this report
    disagree with the gate it exists to predict.
    """
    value = line.split(":", 1)[1].strip()
    if "#" in value and not (value.startswith(("'", '"'))):
        value = value.split("#", 1)[0].strip()
    return value.strip("'\"")


def approval_of(node_dir: str) -> dict:
    """Read `approved_by` out of the leaf the render gate actually reads.

    Deliberately a line scan and not a yaml parse: this must give the same
    answer as farm_worker's gate on a box that may not have pyyaml, and the
    field is a plain scalar in every leaf we have.
    """
    leaf = newest_t0_leaf(node_dir)
    if not leaf:
        return {"leaf": None, "approved_by": None, "approved": False,
                "why": "no *-t0-*.yaml leaf"}
    approved_by = None
    approved_on = None
    try:
        with open(leaf, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                stripped = line.strip()
                if stripped.startswith("approved_by:"):
                    approved_by = _scalar_of(stripped)
                elif stripped.startswith("approved_on:"):
                    approved_on = _scalar_of(stripped)
    except OSError as exc:
        return {"leaf": leaf, "approved_by": None, "approved": False,
                "why": "unreadable: %s" % exc}
    return {"leaf": os.path.basename(leaf), "approved_by": approved_by,
            "approved_on": approved_on,
            "approved": bool(approved_by and approved_by.startswith("founder")),
            "why": "" if approved_by else "no approved_by key (gate reads this as 'none')"}


def clip_tokens(repo: str, texts: dict) -> dict:
    """Exact CLIP token counts, or an explicit refusal.

    Refusing is the point. A count from the prose estimator looks identical to a
    real one in a report, and the whole reason this runs on the box is that the
    estimator is off by around three tokens right at the 77 boundary.
    """
    out = {"tokenizer": None, "max_tokens": 77, "counts": {}, "over": []}
    if not texts:
        return out
    sys.path.insert(0, os.path.join(repo, "pipeline"))
    try:
        from transformers import CLIPTokenizerFast
        tok = CLIPTokenizerFast.from_pretrained("openai/clip-vit-large-patch14")
    except Exception as exc:
        out["tokenizer"] = "UNAVAILABLE: %s: %s" % (type(exc).__name__, exc)
        return out
    out["tokenizer"] = "openai/clip-vit-large-patch14 (exact)"
    for name, text in texts.items():
        n = len(tok(text)["input_ids"])
        out["counts"][name] = n
        if n > 77:
            out["over"].append("%s: %d > 77" % (name, n))
    return out


def torch_report() -> dict:
    try:
        import torch
    except Exception as exc:
        return {"torch": "MISSING: %s" % exc, "cuda": False}
    rep = {"torch": torch.__version__, "cuda": bool(torch.cuda.is_available())}
    if rep["cuda"]:
        rep["device"] = torch.cuda.get_device_name(0)
        free, total = torch.cuda.mem_get_info()
        rep["vram_free_gib"] = round(free / 1024 ** 3, 1)
        rep["vram_total_gib"] = round(total / 1024 ** 3, 1)
    return rep


def as_yaml(data, indent=0) -> str:
    """Minimal YAML writer -- the box venv is a render env, not a data env."""
    pad = "  " * indent
    if isinstance(data, dict):
        if not data:
            return pad + "{}\n"
        out = ""
        for k, v in data.items():
            if isinstance(v, (dict, list)) and v:
                out += "%s%s:\n%s" % (pad, k, as_yaml(v, indent + 1))
            else:
                out += "%s%s: %s\n" % (pad, k, scalar(v))
        return out
    if isinstance(data, list):
        if not data:
            return pad + "[]\n"
        out = ""
        for v in data:
            if isinstance(v, (dict, list)) and v:
                # first line rides the dash, the rest keep the nested indent
                body = as_yaml(v, indent + 1).splitlines()
                out += "%s- %s\n" % (pad, body[0].strip())
                out += "".join(line + "\n" for line in body[1:])
            else:
                out += "%s- %s\n" % (pad, scalar(v))
        return out
    return pad + scalar(data) + "\n"


def scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if s == "" or any(c in s for c in ":#'\"\n") or s.strip() != s:
        return json.dumps(s)
    return s


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="box-side preflight for queued render jobs")
    ap.add_argument("--repo", default=r"C:\banyan-farm\banyan-city")
    ap.add_argument("--out", default="")
    ap.add_argument("--node", action="append", default=[],
                    help="node id to check; repeatable. Default: the approved two")
    ap.add_argument("--plate", action="append", default=[],
                    help="absolute path a queued job would pass as --init; repeatable")
    ap.add_argument("--prompt-file", action="append", default=[],
                    help="file whose text is token-measured on the real tokenizer")
    args = ap.parse_args(argv)

    nodes = args.node or list(DEFAULT_NODES)
    report = {
        "generated_at": utcnow(),
        "host": socket.gethostname(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "repo": args.repo,
    }
    problems = []

    if not os.path.isdir(args.repo):
        problems.append("repo checkout missing at %s" % args.repo)
        report["repo_present"] = False
    else:
        report["repo_present"] = True

    report["gpu"] = torch_report()
    if not report["gpu"].get("cuda"):
        problems.append("torch reports no CUDA device")

    approvals = {}
    for node in nodes:
        node_dir = os.path.join(args.repo, "genomes", "sapling", "nodes", node)
        if not os.path.isdir(node_dir):
            approvals[node] = {"approved": False, "why": "no such node dir"}
            problems.append("node %s: directory missing" % node)
            continue
        info = approval_of(node_dir)
        approvals[node] = info
        if not info["approved"]:
            problems.append("node %s: NOT approved (%s) -- queueing it would "
                            "SystemExit the daemon" % (node, info.get("approved_by")))
    report["node_approval"] = approvals

    plates = {}
    for p in args.plate:
        ok = os.path.isfile(p)
        plates[p] = "present %d bytes" % os.path.getsize(p) if ok else "MISSING"
        if not ok:
            problems.append("plate missing on this box: %s" % p)
    report["plates"] = plates

    texts = {}
    for pf in args.prompt_file:
        try:
            with open(pf, encoding="utf-8") as fh:
                texts[os.path.basename(pf)] = fh.read()
        except OSError as exc:
            problems.append("prompt file unreadable: %s (%s)" % (pf, exc))
    if texts:
        tok = clip_tokens(args.repo, texts)
        report["tokens"] = tok
        if tok["tokenizer"] and tok["tokenizer"].startswith("UNAVAILABLE"):
            problems.append("no CLIP tokenizer on the box -- counts would be a guess")
        problems.extend(tok["over"])

    report["problems"] = problems
    report["verdict"] = "READY" if not problems else "BLOCKED"

    text = as_yaml(report)
    sys.stdout.write(text)
    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        sys.stdout.write("\nwrote %s\n" % args.out)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
