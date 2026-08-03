#!/usr/bin/env python3
"""Make a beat's clip by HOLDING its approved still — no model, no invention.

    python3 pipeline/hold_still.py 10 11 --out /tmp/f15-clips
    python3 pipeline/hold_still.py 3 --seconds 5 --out /tmp/f15-clips

The founder's idea, 2026-08-03: *"maybe for SOME scenes, we dont need videos, like,
scenes which are completely static. rare cases, like the last beat."*

WHY THIS IS BETTER THAN A BAD RENDER, not just cheaper. Image-to-video has to put
something in every frame. Given a composition with nothing animatable it does not
give up — it invents:

  - beat 10 (underground soil, roots, glowing droplets) came back as abstract blue
    streaks with large dark shapes morphing between frames. The founder: "the big
    rock randomly morphing because the ai cant figure out what else to do."
  - beat 11 (one sprout, one new leaf unfurling) came back with the leaf SPLITTING
    into two and extra leaves appearing. The founder: "the sapling doing mitosis."

Beat 11 measured 2.36 median with 0% frozen frames — the highest score of all
fifteen, and the steward called it the best beat in the episode. The score was the
sprout duplicating itself. **A frame-difference metric cannot tell animation from
hallucination; it rewards both.** That is why this tool exists and why the choice of
which beats use it belongs to the author, not to a number.

A held still is honest: it is exactly the frame the founder approved, for exactly as
long as the beat needs, with no content that was never drawn. Provenance is the
still's own — no video model is involved, so no video model's licence attaches.
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
W, H = 704, 1280          # native Wan bucket, and what render_t3's canvas expects
FPS = 24


def approved_still(node_dir: Path, beat: int) -> Path | None:
    """The still for this beat, skipping anything marked REVOKED."""
    stills = node_dir / "stills"
    if not stills.is_dir():
        return None
    for p in sorted(stills.glob(f"{beat:02d}-*.png")):
        if "REVOKED" not in p.name:
            return p
    return None


def slug_for(node_dir: Path, beat: int) -> str | None:
    sys.path.insert(0, str(REPO / "pipeline"))
    from generate_shots import parse_shots
    shots = {s["num"]: s for s in
             parse_shots((node_dir / "shots.md").read_text(encoding="utf-8"))}
    s = shots.get(beat)
    return s.get("slug") if s else None


def hold(still: Path, out: Path, seconds: float) -> None:
    subprocess.run(
        ["ffmpeg", "-v", "error", "-loop", "1", "-i", str(still),
         "-t", f"{seconds}", "-r", str(FPS),
         # scale then pad: the still may not be exactly the bucket, and a squeezed
         # frame would be a different picture than the one that was approved
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
         "-movflags", "+faststart", "-y", str(out)],
        check=True, capture_output=True, encoding="utf-8", errors="replace")


def sidecar(clip: Path, still: Path, beat: int, seconds: float) -> None:
    """§7.2 provenance. No video model ran, so none is claimed.

    The licence question that attaches to this clip is the STILL's, which is
    recorded where the still is recorded — writing a video model here would be a
    lie, and writing nothing at all is what licence_gate calls a violation.
    """
    Path(str(clip) + ".meta.yaml").write_text(
        "# Shot provenance (7.2) — written by hold_still at build time\n"
        "platform: local-cpu (ffmpeg)\n"
        "model: none — held still, no video model ran\n"
        "model_licence: n/a — inherits the still's licence, see stills/README.md\n"
        f"shot_beat: {beat}\n"
        f"size: {W}x{H}\n"
        f"seconds: {seconds}\n"
        f"source_still: {still.name}\n"
        "cost_usd: 0\n"
        "prompt: |-\n"
        "  (none — the approved still is held; nothing was generated)\n"
        "negative: ''\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("beats", nargs="+", type=int)
    ap.add_argument("--node", default="001-capability-inventory")
    ap.add_argument("--genome", default="sapling")
    ap.add_argument("--seconds", type=float, default=2.5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    node_dir = REPO / "genomes" / a.genome / "nodes" / a.node
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    made = 0
    for beat in a.beats:
        still = approved_still(node_dir, beat)
        slug = slug_for(node_dir, beat)
        if not still or not slug:
            print(f"  beat {beat:02d}: no approved still or no slug — skipped")
            continue
        clip = out_dir / f"{beat:02d}-{slug}.mp4"
        hold(still, clip, a.seconds)
        sidecar(clip, still, beat, a.seconds)
        print(f"  beat {beat:02d}  held {still.name}  ->  {clip.name} "
              f"({a.seconds}s, {clip.stat().st_size // 1024}KB)")
        made += 1
    print(f"  {made} held still(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
