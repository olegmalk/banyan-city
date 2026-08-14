#!/usr/bin/env python3
"""Is this clip actually moving, or is it a cut followed by a frozen frame? EXITS NONZERO on a freeze.

Written 2026-08-14 after a blind reader took frame strips from four beats and measured what none of us
had: on beats 03, 13 and 15 the mean pixel change from frame 1 to frame 2 is 38-46 levels, and every
transition after that is 0.5-7. The clip is a HARD CUT away from the conditioning plate and then a still
image. The reader's sentence is the one to remember: "Holding a stick, sitting, and opening a mouth are
states, not events. Ask what the character did and the honest answer is: appeared in a second, different
picture."

Beat 21 - the only one of the four with no character in it - was the only clip with continuous change and
no cut.

WHY A NUMBER AND NOT AN EYE. Every one of those frozen clips looks fine as a still, and I scored several
of them as passing by opening a filmstrip and judging the frames. A filmstrip cannot show you that
nothing happened between the frames; it shows you five pictures and your eye supplies the motion. The
founder said the clips were "very confusing" and I went looking at fidelity, framing and encode - three
measured dead ends - because I kept assessing frames instead of transitions.

THE CHECK: mean absolute luminance difference between consecutive sampled frames.
  - transition 1 (f0 -> f1) is expected to be large when the model departs the plate; it is reported
    but never counted as motion, because a cut is not movement.
  - every LATER transition is the actual motion signal. If those average under the threshold the clip is
    a freeze and it fails, no matter how good any single frame looks.

    python3 review/ep2-picks/freeze_check.py <clip.mp4>...        # default threshold 10.0
    python3 review/ep2-picks/freeze_check.py --threshold 8 a.mp4

Read-only, no GPU, about a second per clip.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

FFMPEG = "/opt/homebrew/bin/ffmpeg"


def _frames(path: Path, n: int, tmp: Path):
    """n evenly spaced frames as greyscale arrays."""
    from PIL import Image
    import numpy as np

    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True).stdout.strip()
    try:
        total = float(dur)
    except ValueError:
        return []
    out = []
    for i in range(n):
        t = total * (i / max(n - 1, 1)) * 0.98
        f = tmp / f"{path.stem}-{i}.png"
        subprocess.run([FFMPEG, "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(path),
                        "-frames:v", "1", str(f)], check=False)
        if f.exists():
            out.append(np.asarray(Image.open(f).convert("L"), dtype=float))
    return out


def check(path: Path, n: int, threshold: float):
    import numpy as np

    with tempfile.TemporaryDirectory() as td:
        fr = _frames(path, n, Path(td))
    if len(fr) < 3:
        return None
    deltas = [float(np.abs(fr[i + 1] - fr[i]).mean()) for i in range(len(fr) - 1)]
    cut, motion = deltas[0], deltas[1:]
    mean_motion = sum(motion) / len(motion)
    return {"cut": cut, "motion": motion, "mean_motion": mean_motion,
            "verdict": "FREEZE" if mean_motion < threshold else "moves"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--frames", type=int, default=6)
    ap.add_argument("--threshold", type=float, default=10.0,
                    help="mean post-cut transition below this is a freeze")
    a = ap.parse_args(argv)

    bad = 0
    for c in a.clips:
        p = Path(c)
        r = check(p, a.frames, a.threshold)
        if r is None:
            print(f"  {p.name:44} could not sample")
            continue
        seq = " ".join(f"{d:5.1f}" for d in r["motion"])
        print(f"  {p.name:44} cut {r['cut']:5.1f} | motion {seq} | mean {r['mean_motion']:5.1f}"
              f"  {r['verdict']}")
        if r["verdict"] == "FREEZE":
            bad += 1
    if bad:
        print(f"\n!! {bad} clip(s) are a cut followed by a frozen frame. A still that looks good is "
              f"still a still.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
