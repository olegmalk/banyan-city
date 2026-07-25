#!/usr/bin/env python3
"""Drive the free Kaggle render from this machine — push, watch, fetch.

The notebook itself is the render; this is the remote control, so nobody has
to babysit a browser tab. Requires the Kaggle CLI and an API token in
`~/.kaggle/kaggle.json` (a founder action — tokens are credentials).

    python3 pipeline/kaggle/run_remote.py push 002b     # queue a GPU run
    python3 pipeline/kaggle/run_remote.py push 001 --steps 25 --beats "[1]"
    python3 pipeline/kaggle/run_remote.py status        # one-line state
    python3 pipeline/kaggle/run_remote.py watch         # poll until it ends
    python3 pipeline/kaggle/run_remote.py fetch <dir>   # download the clips
    python3 pipeline/kaggle/run_remote.py log           # tail remote output

Kaggle's free tier runs one GPU session at a time and caps a session at ~9 h:
a 21-shot episode needs 2-3 pushes. Finished clips are skipped on re-run, so
pushing again continues where the last session stopped — as long as `fetch`
has pulled the clips down and they are committed to the repo the notebook
clones. That round trip is the resume mechanism; there is no persistent disk.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SLUG = json.loads((HERE / "kernel-metadata.json").read_text())["id"]
POLL_S = 120


def kaggle(*args, check=True):
    """Run the CLI from whichever venv has it, so PATH doesn't matter."""
    exe = None
    for cand in (REPO.parent, Path("/private/tmp/claude-501")):
        hits = sorted(cand.glob("**/bin/kaggle")) if cand.exists() else []
        if hits:
            exe = str(hits[0])
            break
    cmd = [exe or "kaggle", *args]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"kaggle {' '.join(args)} failed:\n{r.stdout}\n{r.stderr}")
    return (r.stdout + r.stderr).strip()


def set_node(node: str, steps: int | None = None, beats: str | None = None) -> None:
    """Point the notebook's config cell at a node before pushing."""
    nb_path = HERE / "wan-t2v-kaggle.ipynb"
    nb = json.loads(nb_path.read_text())
    cell = nb["cells"][1]["source"]
    for i, line in enumerate(cell):
        if line.startswith("NODE"):
            cell[i] = f'NODE   = "{node}"        # any node id with a shots.md\n'
        elif beats and line.startswith("BEATS"):
            cell[i] = f"BEATS  = {beats}          # e.g. [1, 3] or None for all beats without status \u2705\n"
        elif steps and line.startswith("STEPS"):
            cell[i] = f"STEPS  = {steps}            # 30 = faster/rougher, 50 = slower/cleaner\n"
    nb["cells"][1]["source"] = cell
    nb_path.write_text(json.dumps(nb, indent=1))
    print(f"notebook set to NODE = {node!r}"
          + (f", STEPS = {steps}" if steps else "")
          + (f", BEATS = {beats}" if beats else ""))


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cmd = sys.argv[1]

    if cmd == "push":
        steps = beats = None
        if "--steps" in sys.argv:
            steps = int(sys.argv[sys.argv.index("--steps") + 1])
        if "--beats" in sys.argv:
            # a one-beat push is the cheap way to prove the chain (import, memory
            # strategy, per-shot minutes, retrievable output) before committing
            # a session to a full episode
            beats = sys.argv[sys.argv.index("--beats") + 1]
        if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
            set_node(sys.argv[2], steps, beats)
        print(kaggle("kernels", "push", "-p", str(HERE)))
        print("queued — GPU jobs wait for a free slot; check with: status")
        return 0

    if cmd == "status":
        print(kaggle("kernels", "status", SLUG, check=False))
        return 0

    if cmd == "log":
        out = kaggle("kernels", "output", SLUG, "-p", "/tmp/kaggle-log", check=False)
        logf = Path("/tmp/kaggle-log/banyan-wan-t2v.log")
        if logf.exists():
            print(logf.read_text()[-4000:])
        else:
            print(out)
        return 0

    if cmd == "watch":
        while True:
            s = kaggle("kernels", "status", SLUG, check=False)
            state = (re.search(r'"?(running|complete|error|cancel\w*|queued)"?', s, re.I)
                     or re.search(r"status is (\w+)", s, re.I))
            label = state.group(1).lower() if state else s.splitlines()[0][:60]
            print(f"[{time.strftime('%H:%M')}] {label}", flush=True)
            if label in ("complete", "error") or "cancel" in label:
                return 0 if label == "complete" else 1
            time.sleep(POLL_S)

    if cmd == "fetch":
        dest = Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/kaggle-clips")
        dest.mkdir(parents=True, exist_ok=True)
        print(kaggle("kernels", "output", SLUG, "-p", str(dest), check=False))
        clips = sorted(dest.glob("**/*.mp4"))
        print(f"\n{len(clips)} clip(s) in {dest}")
        for c in clips:
            print(f"  {c.name}  {c.stat().st_size // 1024} KB")
        if clips:
            print("\nnext: copy into the node's clips/ dir, commit, then assemble:")
            print("  python3 pipeline/render_t3.py sapling <node> --clips <dir> --out ep.mp4")
        return 0

    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main())
