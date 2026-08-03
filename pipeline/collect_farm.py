#!/usr/bin/env python3
"""Collect finished farm clips off a results branch into a render-ready clips dir.

    python3 pipeline/collect_farm.py f15 --node 001-capability-inventory
    python3 pipeline/collect_farm.py f15 --measure          # + motion table
    python3 pipeline/collect_farm.py f15 --out /tmp/mydir

WHY THIS IS A FILE AND NOT A SHELL ONE-LINER. It was a one-liner, retyped from
memory each time a render finished, and on 2026-08-03 it broke three ways in one
day:

  - `ls dir/*.mp4 | wc -l` on an empty directory left ls with no arguments, so it
    listed the WORKING directory and reported "31 clips" against nothing. A
    confident wrong count is worse than an error.
  - two tasks for the same beat both normalise to `01-the-keyboard.mp4`, and
    alphabetical order let a STALE canary overwrite the corrected take. Ordering
    was silent and wrong.
  - the whole thing lived in a scratchpad that got cleaned mid-session, taking the
    measurement helper with it.

Each of those cost a re-run at exactly the moment the answer was wanted.

NAMING. Farm clips land as `<task-id>-<NN>-<slug>.mp4`; render_t3 globs for
`<NN>-<slug>.mp4`. This strips the task id. When several tasks cover the same beat,
the LAST one on the command line wins, so preference is explicit rather than
alphabetical: pass the stale prefix first, the good one last.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_BRANCH = "origin/farm-results-rtx5090"
# <task-id>-<unix-ts>-<NN>-<slug>.mp4
CLIP = re.compile(r"^farm-out/(?P<task>[a-z0-9-]+?)-(?P<ts>\d{6,})-"
                  r"(?P<beat>\d{2})-(?P<slug>[a-z0-9-]+)\.mp4$")


def sh(*args, check=True):
    return subprocess.run(args, cwd=REPO, check=check, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def branch_files(branch: str):
    sh("git", "fetch", "-q", "origin", branch.split("/", 1)[-1], check=False)
    r = sh("git", "ls-tree", "-r", "--name-only", branch, "farm-out/", check=False)
    if r.returncode or not r.stdout:
        sys.exit(f"cannot read {branch} — fetch failed or branch missing")
    return r.stdout.splitlines()


def collect(prefixes, branch, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob("*.mp4"):
        stale.unlink()
    for stale in out.glob("*.meta.yaml"):
        stale.unlink()
    files = branch_files(branch)
    taken = {}
    # prefixes in command-line order: later wins, so preference is explicit
    for pref in prefixes:
        for f in files:
            m = CLIP.match(f)
            if not m or not m.group("task").startswith(pref):
                continue
            dest = f"{m.group('beat')}-{m.group('slug')}.mp4"
            blob = sh("git", "show", f"{branch}:{f}", check=False)
            if blob.returncode:
                print(f"  !! could not read {f}")
                continue
            # bytes, not text: git show of an mp4 must not be decoded
            raw = subprocess.run(["git", "show", f"{branch}:{f}"], cwd=REPO,
                                 capture_output=True, check=True).stdout
            (out / dest).write_bytes(raw)
            side = f"{f}.meta.yaml"
            if side in files:
                s = subprocess.run(["git", "show", f"{branch}:{side}"], cwd=REPO,
                                   capture_output=True, check=True).stdout
                (out / f"{dest}.meta.yaml").write_bytes(s)
            taken[dest] = m.group("task")
    return taken


def measure(out: Path):
    """median frame delta and the share of barely-moving frames, per beat.

    MEDIAN, NOT MEAN. Every motion figure quoted on 2026-08-03 was a mean, which one
    big jump inflates: a variant with 38% dead frames scored higher than one with 3%
    and got recommended. The founder's verdict on it was "literally just frozen
    frames". The share of frames under 0.2 is what matches what a person sees.
    """
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        print("  (numpy/PIL missing — skipping measurement)")
        return
    import tempfile
    print(f"\n  {'beat':<6}{'median':>8}{'frozen':>9}  direction")
    import statistics as st
    meds = []
    for p in sorted(out.glob("*.mp4")):
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-vf",
                            "scale=200:-2,format=gray", f"{td}/f%03d.png"],
                           check=True, capture_output=True)
            fs = [np.asarray(Image.open(q), dtype=float)
                  for q in sorted(Path(td).glob("*.png"))]
        if len(fs) < 2:
            continue
        d = np.array([np.abs(fs[i + 1] - fs[i]).mean() for i in range(len(fs) - 1)])
        med, frozen = float(np.median(d)), 100 * float(np.mean(d < 0.2))
        meds.append(med)
        flag = "  <- reads static" if med < 0.30 else ""
        print(f"  {p.name[:2]:<6}{med:>8.2f}{frozen:>8.0f}%{flag}")
    if meds:
        print(f"\n  median across beats {st.median(meds):.2f}   "
              f"(the cut the founder rejected: 0.13, his pick: 1.30)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prefixes", nargs="+",
                    help="task-id prefixes; LAST one wins for a duplicated beat")
    ap.add_argument("--branch", default=DEFAULT_BRANCH)
    ap.add_argument("--node", default="001-capability-inventory")
    ap.add_argument("--out", default="")
    ap.add_argument("--measure", action="store_true")
    a = ap.parse_args()

    out = Path(a.out) if a.out else REPO / "_farm-clips"
    taken = collect(a.prefixes, a.branch, out)
    for dest, task in sorted(taken.items()):
        print(f"  {dest:<28} <- {task}")
    print(f"  {len(taken)} clip(s) -> {out}")

    # VO, its manifests and the sound cues must sit beside the clips for render_t3
    node = REPO / "genomes/sapling/nodes" / a.node / "clips"
    n = 0
    for pat in ("*.mp3", "*vo*.json", "sound.yaml"):
        for f in node.glob(pat):
            (out / f.name).write_bytes(f.read_bytes())
            n += 1
    print(f"  + {n} audio/manifest file(s) from {a.node}")

    if a.measure:
        measure(out)
    missing = sorted(set(f"{i:02d}" for i in range(1, 16)) -
                     {p.name[:2] for p in out.glob("*.mp4")})
    if missing:
        print(f"\n  MISSING beats: {' '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
