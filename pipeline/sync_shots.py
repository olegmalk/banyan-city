#!/usr/bin/env python3
"""Keep `shots.md` beat headings in lockstep with `node.md` beats.

Since loop cycle 007 a beat IS a shot, so the two files must agree exactly:
same count, same numbers, same time ranges, same order. The linter enforces
that (beat time ranges must appear verbatim in the script), and hand-editing
twenty headings after a script change is how drift gets introduced.

This rewrites each `## Beat NN — TITLE (M:SS–M:SS)` heading from the script's
beats, matching prompts to beats **by position**. It never invents or deletes
a prompt: if the counts differ it says which beats have no prompt and stops,
so the missing prompts get written deliberately.

    python3 pipeline/sync_shots.py sapling 003b [--check]
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from render_t1 import extract_script, parse_frames, strip_inline_md  # noqa: E402

# Match the WHOLE heading line and rebuild it from the script. An earlier
# version tried to capture title / range / status separately with an optional
# range group; non-greedy title + optional range made the title stop at the
# first word and the rest land in "status", which then got re-appended —
# producing "COLD OPEN (0:00–0:05) OPEN (0:00–0:05)". The status marker is
# recovered by searching for its glyph instead of by position.
HEADING = re.compile(r"^## Beat \d+ — .*$", re.M)
STATUS = re.compile(r"([⬜✅].*)$")


def beats_of(node_dir: Path) -> list:
    frames = parse_frames(extract_script((node_dir / "node.md").read_text()))
    out = []
    for f in frames:
        slug = strip_inline_md(f["slug"])
        m = re.search(r"(.*?)\s*—\s*(\d+:\d{2}[–-]\d+:\d{2})", slug)
        out.append((m.group(1).strip(), m.group(2)) if m else (slug, ""))
    return out


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    genome, node = sys.argv[1], sys.argv[2]
    check = "--check" in sys.argv
    nodes = REPO / "genomes" / genome / "nodes"
    node_dir = next(d for d in sorted(nodes.iterdir()) if d.is_dir() and d.name.startswith(node))
    beats = beats_of(node_dir)

    shots_file = node_dir / "shots.md"
    text = shots_file.read_text()
    headings = list(HEADING.finditer(text))
    print(f"{node_dir.name}: {len(beats)} script beats, {len(headings)} shot prompts")

    if len(headings) != len(beats):
        lo, hi = min(len(headings), len(beats)), max(len(headings), len(beats))
        print(f"\nMISMATCH — beats {lo + 1}..{hi} "
              + ("have no prompt yet" if len(beats) > len(headings) else "have no beat"))
        for i in range(lo, len(beats)):
            print(f"  beat {i + 1:02d} {beats[i][0]} ({beats[i][1]}) — needs a prompt")
        return 1

    new, last = [], 0
    for i, m in enumerate(headings):
        title, rng = beats[i]
        st = STATUS.search(m.group(0))
        status = f" {st.group(1).strip()}" if st else " ⬜ needs footage"
        new.append(text[last:m.start()])
        new.append(f"## Beat {i + 1:02d} — {title} ({rng}){status}")
        last = m.end()
    new.append(text[last:])
    result = "".join(new)

    if check:
        print("in sync" if result == text else "OUT OF SYNC (run without --check to fix)")
        return 0 if result == text else 1
    if result != text:
        shots_file.write_text(result)
        print("headings rewritten from the script")
    else:
        print("already in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
