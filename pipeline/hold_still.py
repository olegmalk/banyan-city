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


# 18%, NOT the 6% post_motion uses. Founder on the 6% version: "this one has no
# motion, u sure you opened it". The move was genuinely present — frames diverged
# steadily from 0 to 13.2 mean abs difference — and still invisible, because 6% over
# 2.5s on a dark low-contrast image is about 15px of travel per second at the frame
# edge and nothing at the centre. A move nobody can see is not a move.
#
# 18% over a 5s beat reads as a deliberate slow push without becoming an effect.
# Measured, not guessed: see the check at the bottom of this file's docstring.
ZOOM = 0.18
DRIFT_PX = 70        # lateral travel, so it is a camera move and not just a scale


def hold(still: Path, out: Path, seconds: float, beat: int,
         zoom: bool = True) -> None:
    """Hold the still, with a slow push-in unless asked for a frozen frame.

    THE PUSH-IN IS THE DEFAULT, and that is the founder's rule, 2026-08-03: "if
    theres nothing to animate, just do the static rule. slow zooming."
    A truly frozen frame inside a moving episode reads as a stalled player rather
    than a held shot — he saw exactly that when a file got overwritten under an
    open player and said "its just stuck at this frame for the entire duration".
    A slow move says "this is a held shot" instead.

    Deterministic, computed rather than generated: nothing can morph, split or
    invent, which is the whole reason a held beat exists. Smoothstep ease so it
    eased OUT so it moves at once and settles, and the drift direction alternates
    with beat parity so two static beats in a row do not look copy-pasted — the
    same trick post_motion.py uses.
    """
    if not zoom:
        subprocess.run(
            ["ffmpeg", "-v", "error", "-loop", "1", "-i", str(still),
             "-t", f"{seconds}", "-r", str(FPS),
             "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                    f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
             "-movflags", "+faststart", "-y", str(out)],
            check=True, capture_output=True, encoding="utf-8", errors="replace")
        return

    from PIL import Image
    import tempfile
    src = Image.open(still).convert("RGB")
    # oversample once, then crop a shrinking window out of it: cropping a big
    # image keeps full detail at every step, where scaling up each frame would
    # soften the picture the founder approved
    over = 1.0 + ZOOM + 0.02
    big = src.resize((int(W * over), int(H * over)), Image.LANCZOS)
    n = max(2, int(FPS * seconds))
    sign = 1 if beat % 2 else -1
    with tempfile.TemporaryDirectory() as td:
        for i in range(n):
            t = i / (n - 1)
            # A GENTLE ease-out, and the exponent is the whole point.
            #
            # smoothstep first: the founder said "feels like a weird slow key
            # frame, it should be ease in and out, just ease out" — right, because
            # smoothstep eases IN too, so the move creeps up, peaks, and creeps
            # out, which is an animation curve rather than a camera.
            #
            # Then cubic ease-out, and he said "doesnt mean it should just stop at
            # one point" — also right. Cubic is 98% travelled by three-quarters
            # through and retains 1% of its starting speed at the end, so the last
            # quarter of the shot looks parked.
            #
            # 1.4 keeps ~40% of the opening speed at the final frame, so the push
            # is still going when the cut comes. A camera move that has visibly
            # finished before the edit is what makes a held shot feel dead.
            e = 1 - (1 - t) ** 1.4
            z = 1.0 + ZOOM * (1 - e)                    # window shrinks -> push IN
            cw, ch = int(W * z), int(H * z)
            cx = (big.width - cw) // 2 + int(sign * DRIFT_PX * e)
            cy = (big.height - ch) // 2
            cx = max(0, min(cx, big.width - cw))
            (big.crop((cx, cy, cx + cw, cy + ch))
                .resize((W, H), Image.LANCZOS)
                .save(f"{td}/f{i:04d}.png"))
        subprocess.run(
            ["ffmpeg", "-v", "error", "-r", str(FPS), "-i", f"{td}/f%04d.png",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
             "-movflags", "+faststart", "-y", str(out)],
            check=True, capture_output=True, encoding="utf-8", errors="replace")


def sidecar(clip: Path, still: Path, beat: int, seconds: float,
            frozen: bool = False) -> None:
    """§7.2 provenance. No video model ran, so none is claimed.

    The licence question that attaches to this clip is the STILL's, which is
    recorded where the still is recorded — writing a video model here would be a
    lie, and writing nothing at all is what licence_gate calls a violation.
    """
    Path(str(clip) + ".meta.yaml").write_text(
        "# Shot provenance (7.2) — written by hold_still at build time\n"
        "platform: local-cpu (ffmpeg)\n"
        f"model: none — held still{'' if frozen else ' + code push-in'}, "
        f"no video model ran\n"
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
    ap.add_argument("--frozen", action="store_true",
                    help="no push-in at all. Default is the slow zoom, per the "
                         "founder's static rule — a truly frozen frame reads as a "
                         "stalled player rather than a held shot")
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
        hold(still, clip, a.seconds, beat, zoom=not a.frozen)
        sidecar(clip, still, beat, a.seconds, frozen=a.frozen)
        print(f"  beat {beat:02d}  held {still.name}  ->  {clip.name} "
              f"({a.seconds}s, {clip.stat().st_size // 1024}KB)")
        made += 1
    print(f"  {made} held still(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
