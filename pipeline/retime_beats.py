#!/usr/bin/env python3
"""Re-time a node's beat ranges from the MEASURED length of its voice.

The beat headings in `node.md` carry a time range (`COLD OPEN — 0:00–0:05`),
and everything downstream treats those ranges as truth: `render_t3` sizes each
beat's slot from them, `lint_genome` requires `shots.md` to repeat them, and
the loop's density numbers (seconds per cut, lines per shot) are computed from
them.

They were written by hand, and hands guess badly. Measured on 2026-07-25, nine
of 001's eighteen beats held more voice than their slot allowed — beat 4 had
6.8s of speech in a 4s window — so `render_t3` stretched the slots to fit and
the episode assembled at 133.5s against a script that claimed 88s. The script
was not describing the episode. Worse, the cycle-007 density table was
computed from the claimed numbers, so it reported a cut every 4.9s for an
episode that actually cuts every 7.4s.

So the ranges are derived, not authored: each beat's slot is predicted with
`fit_duration` — the very function `render_t3` sizes slots with — from the
beat's measured voice and the length one rendered shot actually is. Guessing a
formula instead of importing the real one just moved the lie (001 then claimed
114s and assembled at 131s).

Nothing is capped. A beat whose voice runs 20s gets a 20s range and is
REPORTED as over the spec, because a beat carrying that much material is a
script problem, and shrinking the number would only hide it again.

It refuses to run when the voice and the script disagree — a beat with a line
and no take, or a take on a beat with no line. Run it after re-voicing a node,
then `sync_shots.py` to propagate the new ranges into `shots.md`.

    python3 pipeline/retime_beats.py sapling 001 [--check]
    python3 pipeline/retime_beats.py sapling --all
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from render_t1 import extract_script, parse_frames, strip_inline_md  # noqa: E402
from render_t2 import ffmpeg_exe  # noqa: E402
from render_t3 import fit_duration  # noqa: E402 — the SAME slot maths the assembler uses

FFMPEG = ffmpeg_exe()

# What a rendered shot is: the Kaggle/Wan floor produces 81 frames at 16fps.
# The ranges are predicted with `fit_duration`, the function render_t3 actually
# sizes slots with, so the script's paper timing equals the assembled runtime.
# Guessing the formula instead left 001 claiming 114s and assembling at 131s.
PLANNED_CLIP_S = 5.0
SPEC_MAX_S = 6.0   # SCRIPT-SPEC's upper bound for one beat = one shot


def clip_seconds(path: Path) -> float | None:
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        return None
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])


def mmss(t: float) -> str:
    total = int(round(t))
    return f"{total // 60}:{total % 60:02d}"


def node_dir(genome: str, node: str) -> Path:
    nodes = REPO / "genomes" / genome / "nodes"
    hit = next((d for d in sorted(nodes.iterdir())
                if d.is_dir() and d.name.startswith(node)), None)
    if not hit:
        raise SystemExit(f"no node dir starting with {node!r}")
    return hit


def planned(d: Path) -> tuple:
    """(list of (beat_no, title, seconds), list of complaints)."""
    frames = parse_frames(extract_script((d / "node.md").read_text()))
    clips = d / "clips"
    plan, gaps = [], []
    for i, f in enumerate(frames, 1):
        slug = strip_inline_md(f["slug"])
        title = re.sub(r"\s*—\s*\d+:\d{2}[–-]\d+:\d{2}\s*$", "", slug).strip()
        spoken = any(it[0] == "line" for it in f["items"])
        vo = clips / f"{i:02d}-vo.mp3"
        vdur = 0.0
        if vo.exists():
            man = clips / f"{i:02d}-vo.json"
            if man.exists():
                try:
                    vdur = float(json.loads(man.read_text()).get("total_s") or 0)
                except (ValueError, json.JSONDecodeError):
                    vdur = 0.0
            vdur = vdur or clip_seconds(vo) or 0.0
        elif spoken:
            gaps.append(f"beat {i:02d} {title}: has a spoken line but no {vo.name}")
        if vo.exists() and not spoken:
            # the reverse mismatch, and the nastier one: a beat that lost its
            # dialogue in a rewrite keeps the old take and the episode speaks a
            # line that is not in the script there (007a played its closing
            # line at beat 5 this way)
            gaps.append(f"beat {i:02d} {title}: has NO spoken line but {vo.name} exists")
        # no cap: dialogue is never trimmed mid-line, so a slot shorter than its
        # voice is a lie the assembler quietly corrects. Over-long beats are
        # REPORTED instead — a beat that needs 20s is a beat carrying too much,
        # and the fix is splitting the script, not shrinking the number.
        secs = fit_duration(PLANNED_CLIP_S, PLANNED_CLIP_S, vdur)
        plan.append((i, title, round(secs, 2), len([1 for it in f["items"] if it[0] == "line"])))
    return plan, gaps


def retime(genome: str, node: str, check: bool) -> int:
    d = node_dir(genome, node)
    plan, gaps = planned(d)
    if gaps:
        print(f"{d.name}: VO is not current — refusing to re-time")
        for g in gaps[:6]:
            print(f"  {g}")
        if len(gaps) > 6:
            print(f"  … and {len(gaps) - 6} more")
        print("  re-voice first: synth_vo.py <ffmpeg> "
              f"{genome} {d.name} --engine chatterbox")
        return 1

    md_path = d / "node.md"
    text = md_path.read_text()
    ranges, t = [], 0.0
    for _, _, secs, _ in plan:
        ranges.append((t, t + secs))
        t += secs

    # rewrite each beat heading's range in place, in order
    out, idx, last = [], 0, 0
    pat = re.compile(r"^\*\*(.+?)\s*—\s*(\d+:\d{2})\s*[–-]\s*(\d+:\d{2})\*\*\s*$", re.M)
    for m in pat.finditer(text):
        if idx >= len(ranges):
            break
        a, b = ranges[idx]
        out.append(text[last:m.start()])
        out.append(f"**{m.group(1)} — {mmss(a)}–{mmss(b)}**")
        last, idx = m.end(), idx + 1
    out.append(text[last:])
    result = "".join(out)

    if idx != len(plan):
        print(f"{d.name}: matched {idx} beat headings but parsed {len(plan)} beats "
              "— heading format drift, not re-timing")
        return 1

    total = ranges[-1][1]
    cut = total / len(plan)
    lines = sum(n for _, _, _, n in plan)
    over = [(i, title, secs, n) for i, title, secs, n in plan if secs > SPEC_MAX_S + 0.5]
    print(f"{d.name}: {len(plan)} beats, {total:.0f}s measured "
          f"=> a cut every {cut:.1f}s, {lines / len(plan):.2f} lines/shot")
    if over:
        print(f"  {len(over)} beat(s) over the {SPEC_MAX_S:g}s spec — too much material "
              "for one shot, split the script:")
        for i, title, secs, n in over:
            print(f"    beat {i:02d} {title:<26} {secs:5.1f}s  {n} line(s)")
    if result == text:
        print("  already matches the voice")
        return 0
    if check:
        print("  OUT OF DATE (run without --check to re-time)")
        return 1
    md_path.write_text(result)
    print("  beat ranges rewritten from measured voice — "
          f"now run: sync_shots.py {genome} {node}")
    return 0


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    genome, target = sys.argv[1], sys.argv[2]
    check = "--check" in sys.argv
    if target == "--all":
        nodes = sorted(d.name for d in (REPO / "genomes" / genome / "nodes").iterdir()
                       if d.is_dir())
        return max(retime(genome, n, check) for n in nodes)
    return retime(genome, target, check)


if __name__ == "__main__":
    sys.exit(main())
