#!/usr/bin/env python3
"""Reconcile pipeline/lane-registry.yaml against reality, and say who is dead.

    python3 pipeline/reconcile_lanes.py            # read-only, local refs
    python3 pipeline/reconcile_lanes.py --fetch    # refresh remote refs first
    python3 pipeline/reconcile_lanes.py --update   # write status back to registry
    python3 pipeline/reconcile_lanes.py --selftest # prove the yaml fallback is honest

WHY. When the fleet died at 21:23Z on 2026-08-09 the only thing that knew what
had been dispatched was the orchestrator's context, and it died with it. Recovery
was a human noticing and an agent hand-reading git. This script is that reading,
written down: for every lane in the registry it checks the COMPLETION ARTIFACT —
the evidence that proves the work landed — against the repo and the machines, and
for anything dead it prints a resume brief you can paste into a new lane.

THE ONE RULE IT IS BUILT AROUND: a lane's own report is not evidence. Heartbeats,
claim files and handoffs lag reality in both directions, so nothing here trusts
the registry's `status:` field — every run re-derives it from artifacts on disk,
commits in git, and processes on the boxes.

THE SECOND RULE: "I cannot see it" and "it is not there" are opposite facts and
they look identical if you let them. farm_worker.py learned this the expensive
way — a failed fetch read as an empty queue and a machine idled for hours next to
five queued jobs (2026-08-01). So a check that cannot be performed returns UNKNOWN
and is never counted as dead.

READ-ONLY. This script never mutates git state: no commit, no checkout, no reset,
and no fetch unless you pass --fetch (which updates remote-tracking refs, so it is
opt-in rather than default). The single thing it may write is the `status:` field
of the registry, under --update.

Stdlib only. Recovery tooling that needs a venv is not recovery tooling, so the
yaml read prefers PyYAML when it is importable and falls back to a small parser
for the registry's own restricted subset. --selftest asserts the two agree.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "pipeline" / "lane-registry.yaml"

# A lane with no completion evidence but a working-tree change or a freshly
# touched artifact inside this window is still working. Tuned to be generous:
# calling a live lane dead spawns a duplicate writer into a shared worktree,
# which is the more expensive mistake of the two.
ALIVE_MINUTES = 60


# --------------------------------------------------------------------------
# yaml: PyYAML when present, strict subset parser when not
# --------------------------------------------------------------------------

def _scalar(tok: str):
    """One scalar in the registry's subset: quoted string, int, bool, or bare."""
    tok = tok.strip()
    if len(tok) >= 2 and tok[0] == '"' and tok[-1] == '"':
        return tok[1:-1]
    if tok in ("true", "True"):
        return True
    if tok in ("false", "False"):
        return False
    if re.fullmatch(r"-?\d+", tok):
        return int(tok)
    return tok


def _parse_subset(text: str) -> dict:
    """Parse the registry's deliberately small YAML subset.

    Handles exactly what lane-registry.yaml uses and nothing else: full-line
    comments, `key: value` at any indent, one list (`lanes:`) whose items are
    maps introduced by `- key: value`, and one nested map per item. Every
    multi-word value in that file is double-quoted on a single line, which is
    what makes splitting on the first colon safe — keys never contain one, and
    the prose values contain several.

    A block scalar, an inline flow list or an anchor would silently mis-parse
    here, which is why the registry's header pins the shape and --selftest
    compares this against PyYAML on the real file.
    """
    root: dict = {}
    lanes: list = []
    cur: dict | None = None       # current lane
    nested: dict | None = None    # current nested map inside the lane
    nested_indent = -1

    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()

        if line.startswith("- "):
            # new lane; the rest of the line is its first key
            cur = {}
            nested, nested_indent = None, -1
            lanes.append(cur)
            line = line[2:].strip()
            indent += 2

        if ":" not in line:
            raise ValueError(f"unparseable registry line: {raw!r}")
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()

        # a key with no value opens a map
        if val == "":
            if cur is None and key == "lanes":
                root["lanes"] = lanes
            elif cur is not None:
                nested = {}
                nested_indent = indent
                cur[key] = nested
            continue

        if nested is not None and indent > nested_indent:
            nested[key] = _scalar(val)
        elif cur is not None:
            nested, nested_indent = None, -1
            cur[key] = _scalar(val)
        else:
            root[key] = _scalar(val)

    root.setdefault("lanes", lanes)
    return root


def load_registry(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml
        return yaml.safe_load(text) or {}
    except ImportError:
        return _parse_subset(text)


# --------------------------------------------------------------------------
# read-only shell helpers
# --------------------------------------------------------------------------

def git(*args, check=False) -> str:
    """A read-only git call. Returns '' on failure — callers must treat an empty
    result as UNKNOWN, never as a negative answer."""
    r = subprocess.run(("git",) + args, cwd=REPO, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if r.returncode and check:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()[:200]}")
    return r.stdout if r.returncode == 0 else ""


def ssh(host: str, command: str, timeout: int = 30):
    """Returns (ok, output). ok=False means we could not look, not that the
    answer was no."""
    try:
        r = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=15", "-o", "BatchMode=yes", host, command],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        return False, str(e)
    if r.returncode != 0 and not r.stdout:
        return False, (r.stderr or "").strip()[:200]
    return True, r.stdout


def farm_branches() -> list:
    out = git("for-each-ref", "--format=%(refname)", "refs/remotes/origin/farm-results-*")
    return [b.strip() for b in out.splitlines() if b.strip()]


def heartbeat_subjects(limit: int = 400) -> list:
    """(subject, unix_time) for recent heartbeat commits on every results branch."""
    rows = []
    for br in farm_branches():
        out = git("log", f"--max-count={limit}", "--format=%ct%x09%s", br)
        for line in out.splitlines():
            ts, _, subj = line.partition("\t")
            if ts.isdigit():
                rows.append((subj, int(ts)))
    return rows


# --------------------------------------------------------------------------
# artifact checks -> "yes" | "no" | "unknown"
# --------------------------------------------------------------------------

def check_file(art: dict) -> tuple:
    rel = str(art.get("path", "")).strip()
    if not rel:
        return "unknown", "no path in completion_artifact"
    p = REPO / rel
    if not p.exists():
        return "no", f"{rel} absent"
    notes = [f"{rel} present ({p.stat().st_size}B)"]

    parse = art.get("parse")
    if parse == "py":
        try:
            import ast
            ast.parse(p.read_text(encoding="utf-8"))
            notes.append("parses")
        except SyntaxError as e:
            return "no", f"{rel} SYNTAX ERROR line {e.lineno}"
    elif parse == "json":
        try:
            json.loads(p.read_text(encoding="utf-8"))
            notes.append("parses")
        except Exception as e:  # noqa: BLE001
            return "no", f"{rel} bad json: {e}"
    elif parse == "yaml":
        try:
            import yaml
            yaml.safe_load(p.read_text(encoding="utf-8"))
            notes.append("parses")
        except ImportError:
            notes.append("parse UNCHECKED (no pyyaml)")
        except Exception as e:  # noqa: BLE001
            return "no", f"{rel} bad yaml: {str(e)[:80]}"

    # "tracked" is the difference between a finished script and a landed one.
    # Both untracked partials recovered on 2026-08-10 parsed perfectly and were
    # complete — they had simply never been committed, so nothing outside that
    # dead lane's worktree knew they existed.
    if art.get("tracked"):
        listed = git("ls-files", "--error-unmatch", rel)
        if not listed.strip():
            return "no", "; ".join(notes) + " but UNTRACKED — never committed"
        notes.append("tracked")
    return "yes", "; ".join(notes)


def check_commit(art: dict) -> tuple:
    pattern = str(art.get("pattern", "")).strip()
    if not pattern:
        return "unknown", "no pattern in completion_artifact"
    ref = str(art.get("ref", "main")).strip()
    out = git("log", "--max-count=300", "--format=%h%x09%s", ref)
    if not out:
        return "unknown", f"cannot read git log on {ref}"
    rx = re.compile(pattern, re.I)
    for line in out.splitlines():
        sha, _, subj = line.partition("\t")
        if rx.search(subj):
            return "yes", f"{sha} {subj[:70]}"
    return "no", f"no commit on {ref} matching /{pattern}/ in last 300"


def check_heartbeat(art: dict, hbs: list) -> tuple:
    tid = str(art.get("task_id", "")).strip()
    if not tid:
        return "unknown", "no task_id in completion_artifact"
    if not hbs:
        return "unknown", "no farm-results-* branches readable"
    needle = f"DONE task={tid}"
    for subj, ts in hbs:
        if needle in subj:
            return "yes", f"DONE {tid} at {time.strftime('%m-%d %H:%MZ', time.gmtime(ts))}"
    return "no", f"no `DONE task={tid}` on any farm-results-* branch"


def check_heartbeat_fresh(art: dict, hbs: list) -> tuple:
    if not hbs:
        return "unknown", "no farm-results-* branches readable"
    max_age = int(art.get("max_age_min", 90))
    newest = None
    for subj, ts in hbs:
        if "DONE task=" in subj and (newest is None or ts > newest[1]):
            newest = (subj, ts)
    if newest is None:
        return "no", "no DONE line on any farm-results-* branch"
    age_min = (time.time() - newest[1]) / 60.0
    tid = re.search(r"DONE task=(\S+)", newest[0])
    label = tid.group(1) if tid else "?"
    when = time.strftime("%m-%d %H:%MZ", time.gmtime(newest[1]))
    if age_min <= max_age:
        return "yes", f"last DONE {label} {when}, {age_min:.0f}m ago (<= {max_age}m)"
    return "no", f"STALE: last DONE {label} {when}, {age_min:.0f}m ago (> {max_age}m)"


def check_process(art: dict, allow_remote: bool) -> tuple:
    match = str(art.get("match", "")).strip()
    host = str(art.get("host", "")).strip()
    if not match:
        return "unknown", "no match in completion_artifact"
    if host:
        if not allow_remote:
            return "unknown", f"remote check on {host} skipped (--no-remote)"
        ok, out = ssh(host, "tasklist /v /fo csv")
        if not ok:
            # cannot reach the box. NOT the same as "the daemon is gone".
            ok2, out2 = ssh(host, "echo probe")
            reach = "reachable" if ok2 else "UNREACHABLE"
            return "unknown", f"{host} {reach}; process list unavailable ({out[:80]})"
        # tasklist does not show command lines, so a python.exe alone proves
        # nothing — ask CIM for the argv and match on that.
        ok3, out3 = ssh(host, 'powershell -NoProfile -Command '
                              '"Get-CimInstance Win32_Process | '
                              'Where-Object {$_.Name -like \\"python*\\"} | '
                              'ForEach-Object { $_.CommandLine }"')
        if not ok3:
            return "unknown", f"{host}: could not read command lines"
        for line in out3.splitlines():
            if match in line:
                return "yes", f"{host}: running -- {line.strip()[:90]}"
        others = [l.strip()[:110] for l in out3.splitlines() if l.strip()]
        return "no", (f"{host}: no process matching {match!r}"
                      + (f"; other python: {others[0]}" if others else "; no python at all"))
    # local
    try:
        r = subprocess.run(["ps", "-Ao", "args"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    except OSError as e:
        return "unknown", f"cannot list processes: {e}"
    for line in r.stdout.splitlines():
        if match in line and "reconcile_lanes" not in line:
            return "yes", f"local: {line.strip()[:90]}"
    return "no", f"local: no process matching {match!r}"


# --------------------------------------------------------------------------
# liveness signals the shell can see
# --------------------------------------------------------------------------

def owned_paths(lane: dict) -> list:
    raw = str(lane.get("owns", "") or "")
    if not raw or raw.startswith("none"):
        return []
    return [p.strip() for p in raw.split(",") if p.strip()]


def liveness(lane: dict, alive_minutes: int) -> tuple:
    """(is_live, has_partials, notes). An uncommitted diff on a lane's own path
    is the strongest signal there is: a dead lane cannot be holding a file open,
    so a working-tree change proves someone is in there right now."""
    notes, live, partials = [], False, False
    now = time.time()
    for rel in owned_paths(lane):
        p = REPO / rel
        st = git("status", "--porcelain", "--", rel).strip()
        if st:
            code = st.split()[0] if st.split() else "?"
            partials = True
            notes.append(f"{rel}: {'uncommitted diff' if code == 'M' else 'untracked'}")
            if code == "M":
                live = True
        if p.exists():
            age_min = (now - p.stat().st_mtime) / 60.0
            if age_min <= alive_minutes:
                live = True
                notes.append(f"{rel}: touched {age_min:.0f}m ago")
    return live, partials, notes


# --------------------------------------------------------------------------

def classify(lane: dict, hbs: list, allow_remote: bool, alive_minutes: int) -> dict:
    art = lane.get("completion_artifact") or {}
    kind = str(art.get("kind", "")).strip()
    if kind == "file":
        verdict, why = check_file(art)
    elif kind == "commit":
        verdict, why = check_commit(art)
    elif kind == "heartbeat":
        verdict, why = check_heartbeat(art, hbs)
    elif kind == "heartbeat_fresh":
        verdict, why = check_heartbeat_fresh(art, hbs)
    elif kind == "process":
        verdict, why = check_process(art, allow_remote)
    else:
        verdict, why = "unknown", f"unknown completion_artifact kind {kind!r}"

    live, partials, lnotes = liveness(lane, alive_minutes)

    # ALIVE OUTRANKS LANDED, and deliberately. A completion artifact proves that
    # SOMETHING landed, not that the lane is done: a `commit` pattern happily
    # matches an earlier commit by the same lane, and the first run of this
    # script called status-ux LANDED off 069ba09 while it had an uncommitted
    # diff open in build_pulse.py. Reading that as finished is the expensive
    # direction — it invites someone to close the lane out or to start writing
    # in a file another agent is holding. An uncommitted diff means a live
    # writer, full stop, so it wins.
    if live and partials:
        state = "ALIVE"
        if verdict == "yes":
            why = f"still writing; earlier evidence: {why}"
    elif verdict == "yes":
        state = "LANDED"
    elif verdict == "unknown":
        state = "UNKNOWN"
    elif live:
        state = "ALIVE"
    elif partials:
        state = "DEAD-WITH-PARTIALS"
    else:
        state = "DEAD-CLEAN"
    return {"name": lane.get("name", "?"), "state": state, "why": why,
            "liveness": lnotes, "lane": lane}


def duplicate_writers(lanes: list) -> list:
    seen, dupes = {}, []
    for ln in lanes:
        for p in owned_paths(ln):
            seen.setdefault(p, []).append(ln.get("name", "?"))
    for p, names in sorted(seen.items()):
        if len(names) > 1:
            dupes.append((p, names))
    return dupes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", default=str(REGISTRY))
    ap.add_argument("--fetch", action="store_true",
                    help="refresh remote-tracking refs first (the only network "
                         "write this script can make; off by default)")
    ap.add_argument("--no-remote", action="store_true",
                    help="skip ssh checks; remote lanes report UNKNOWN")
    ap.add_argument("--update", action="store_true",
                    help="write the derived state back to the registry's status: field")
    ap.add_argument("--alive-min", type=int, default=ALIVE_MINUTES)
    ap.add_argument("--selftest", action="store_true",
                    help="assert the stdlib yaml fallback matches PyYAML on the real file")
    a = ap.parse_args()

    path = Path(a.registry)
    if not path.exists():
        print(f"no registry at {path}", file=sys.stderr)
        return 2

    if a.selftest:
        try:
            import yaml
        except ImportError:
            print("SELFTEST SKIPPED: PyYAML not importable, nothing to compare against")
            return 0
        text = path.read_text(encoding="utf-8")
        ref, mine = yaml.safe_load(text), _parse_subset(text)
        if ref == mine:
            print(f"SELFTEST OK: fallback parser matches PyYAML on {path.name} "
                  f"({len(ref.get('lanes', []))} lanes)")
            return 0
        print("SELFTEST FAILED: fallback parser disagrees with PyYAML")
        rl, ml = ref.get("lanes", []), mine.get("lanes", [])
        if len(rl) != len(ml):
            print(f"  lane count {len(rl)} vs {len(ml)}")
        for r, m in zip(rl, ml):
            for k in set(r) | set(m):
                if r.get(k) != m.get(k):
                    print(f"  {r.get('name')}.{k}: {r.get(k)!r} != {m.get(k)!r}")
        return 1

    if a.fetch:
        subprocess.run(["git", "fetch", "--quiet", "origin"], cwd=REPO)

    reg = load_registry(path)
    lanes = reg.get("lanes") or []
    hbs = heartbeat_subjects()

    # How stale is the evidence? Without --fetch these refs are whatever the last
    # fetch left, and a stale ref reads exactly like a lane that stopped working.
    newest_hb = max((ts for _, ts in hbs), default=None)
    print(f"lane registry: {path}   lanes={len(lanes)}   "
          f"seeded {reg.get('seeded_at', '?')}")
    if newest_hb:
        age = (time.time() - newest_hb) / 60.0
        print(f"farm-results refs: {len(farm_branches())} branches, newest heartbeat "
              f"{time.strftime('%m-%d %H:%MZ', time.gmtime(newest_hb))} ({age:.0f}m ago)"
              f"{'' if a.fetch else '  [LOCAL REFS, not fetched — pass --fetch to refresh]'}")
    else:
        print("farm-results refs: none readable — heartbeat checks will report UNKNOWN")
    print()

    results = [classify(ln, hbs, not a.no_remote, a.alive_min) for ln in lanes]

    width = max((len(r["name"]) for r in results), default=4)
    print(f"{'LANE'.ljust(width)}  {'STATE'.ljust(18)}  EVIDENCE")
    print(f"{'-' * width}  {'-' * 18}  {'-' * 46}")
    for r in results:
        print(f"{r['name'].ljust(width)}  {r['state'].ljust(18)}  {r['why']}")
        for n in r["liveness"]:
            print(f"{' ' * width}  {' ' * 18}  . {n}")

    dupes = duplicate_writers(lanes)
    if dupes:
        print("\nDUPLICATE WRITERS — two lanes own one path; in a shared worktree "
              "that is silent until one overwrites the other:")
        for p, names in dupes:
            print(f"  {p}: {', '.join(names)}")

    dead = [r for r in results if r["state"].startswith("DEAD")]
    unknown = [r for r in results if r["state"] == "UNKNOWN"]

    for r in dead:
        ln = r["lane"]
        print("\n" + "=" * 78)
        print(f"RESUME BRIEF — {r['name']}  [{r['state']}]")
        print("=" * 78)
        print(f"Mission: {ln.get('mission', '(none recorded)')}")
        print(f"Owns:    {ln.get('owns', '(none recorded)')}")
        print(f"Why dead: {r['why']}")
        if r["liveness"]:
            print("On disk: " + "; ".join(r["liveness"]))
        print("\n--- paste below into the replacement lane ---")
        print(ln.get("resume_brief", "(no resume_brief recorded — WRITE ONE)"))
        print("--- end ---")

    if unknown:
        print("\nUNKNOWN (could not check — this is NOT 'dead'; a check that cannot "
              "run must never be read as a negative answer):")
        for r in unknown:
            print(f"  {r['name']}: {r['why']}")

    if a.update:
        text = path.read_text(encoding="utf-8")
        mapping = {"LANDED": "landed", "ALIVE": "live",
                   "DEAD-WITH-PARTIALS": "dead", "DEAD-CLEAN": "dead",
                   "UNKNOWN": "unknown"}
        changed = 0
        for r in results:
            # rewrite the status: line belonging to this lane's block only
            pat = re.compile(r"(- name: " + re.escape(r["name"]) + r"\b.*?\n    status: )(\S+)",
                             re.S)
            new = mapping[r["state"]]
            m = pat.search(text)
            if m and m.group(2) != new:
                text = text[:m.start(2)] + new + text[m.end(2):]
                changed += 1
        if changed:
            path.write_text(text, encoding="utf-8")
        print(f"\nregistry status: {changed} field(s) updated")

    print(f"\nunknown={len(unknown)} (excluded from the counts below)")
    print(f"RECONCILE: alive={sum(1 for r in results if r['state'] == 'ALIVE')} "
          f"landed={sum(1 for r in results if r['state'] == 'LANDED')} "
          f"dead={len(dead)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
