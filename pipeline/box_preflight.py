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


def guard_modules(repo: str, renderers=("ltx_i2v.py", "wan_i2v.py")) -> dict:
    """IMPORT each renderer the way python will, and report what breaks.

    WHY AN IMPORT AND NOT A FILE LIST. The first version of this scanned the
    renderer's source for `from <mod> import ...` and checked whether
    `<mod>.py` sat beside it. It passed cleanly against a checkout with
    `prompt_budget.py` deliberately deleted -- because a scan keyed on "the
    file is there" cannot see a sibling that is NOT there, which is the entire
    failure. Listing the expected modules by hand fails the other way: it
    closes this hole and misses the next guard someone adds.

    Importing the renderer asks the only question that matters and asks it
    exactly as the render will. It is also cheap: every renderer defers torch,
    diffusers and transformers into function bodies (ltx_i2v's module docstring
    is explicit that the encode/render split exists to keep weights out of the
    process until needed), so module import is stdlib plus the sibling guards
    and costs milliseconds.

    Run in a SUBPROCESS with the render venv's own interpreter: a renderer that
    raises on import must not take preflight down with it, and the answer is
    only true for the python that will actually run the job.
    """
    import subprocess
    pipeline = os.path.join(repo, "pipeline")
    out = {}
    for renderer in renderers:
        script = os.path.join(pipeline, renderer)
        if not os.path.isfile(script):
            out[renderer] = "renderer ABSENT from this checkout"
            continue
        mod = renderer[:-3]
        code = ("import sys; sys.path.insert(0, %r); import %s; print('ok')"
                % (pipeline, mod))
        try:
            r = subprocess.run([sys.executable, "-c", code],
                               capture_output=True, text=True, timeout=120,
                               encoding="utf-8", errors="replace")
        except (OSError, subprocess.SubprocessError) as exc:
            out[renderer] = "could not run import probe: %s" % exc
            continue
        if r.returncode == 0 and "ok" in r.stdout:
            out[renderer] = "imports ok"
        else:
            tail = (r.stderr or "").strip().splitlines()
            out[renderer] = "IMPORT FAILED: %s" % (tail[-1] if tail else
                                                   "rc=%d" % r.returncode)
    return out


def checkout_age(repo: str) -> dict:
    """How old the commit under the card actually is. No network, no fetch.

    A fetch here would be wrong twice over: it costs minutes on this repo (the
    5-day gap that hid the missing guard was 2,171 files and 673 media blobs,
    a 15-minute transfer) and preflight must never be the thing that stalls a
    claim. The commit DATE is already on disk and answers the only question
    that matters -- is the code under the card the code we think it is.
    """
    import subprocess
    try:
        r = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%H %cI"],
                           capture_output=True, text=True, timeout=30,
                           encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError) as exc:
        return {"head": None, "age_days": None,
                "why": "git unavailable: %s" % exc}
    if r.returncode != 0:
        return {"head": None, "age_days": None,
                "why": "git failed: %s" % r.stderr.strip()}
    head, _, iso = r.stdout.strip().partition(" ")
    try:
        when = datetime.datetime.fromisoformat(iso)
    except ValueError:
        return {"head": head, "age_days": None, "why": "unparsable date %r" % iso}
    now = datetime.datetime.now(datetime.timezone.utc)
    age = (now - when.astimezone(datetime.timezone.utc)).total_seconds() / 86400.0
    return {"head": head, "committed": iso, "age_days": round(age, 2), "why": ""}


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
    ap.add_argument("--max-age-days", type=float, default=2.0,
                    help="BLOCK if the checkout's HEAD commit is older than this "
                         "(default 2). Not a style rule: the guard that was "
                         "missing on 2026-08-15 was 5 days out of reach")
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
        # PRESENT IS NOT CURRENT. Until 2026-08-15 this block checked only that
        # the directory existed, and the box ran five days behind on a checkout
        # whose renderer had no truncation guard because the guard file was
        # written after the commit under the card. "The checkout is there" was
        # true the whole time.
        age = checkout_age(args.repo)
        report["checkout"] = age
        if age.get("age_days") is None:
            problems.append("cannot determine checkout age (%s) -- an unknown "
                            "commit under the card is the state this checks for"
                            % age.get("why"))
        elif age["age_days"] > args.max_age_days:
            problems.append(
                "checkout is %.1f days old (HEAD %s, limit %.1f). The renderer "
                "under the card predates commits on main; fast-forward it "
                "between jobs." % (age["age_days"], (age["head"] or "?")[:8],
                                   args.max_age_days))

        guards = guard_modules(args.repo)
        report["guard_modules"] = guards
        for renderer, state in guards.items():
            if not state.endswith("ok"):
                problems.append("%s: %s" % (renderer, state))

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
