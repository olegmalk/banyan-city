#!/usr/bin/env python3
"""Deterministic motion for approved stills — the prototype's $0 animator.

Founder decision (2026-07-28): the working cut iterates FREE. Every approved
still gets a code-driven take — camera moves and effects computed, not
generated — so nothing degrades, nothing hallucinates, and every beat costs
$0 in seconds. Paid AI takes are the crowd's upgrade path (D12): the board
shows the recipe and the current take; anyone may beat it on their own key.

    python3 pipeline/post_motion.py sapling 001 [--beats 1,2,3]

Writes takes/clips/NN-slug.POST.mp4 (+ §7.2 sidecar) for every beat with an
APPROVED still. Refuses beats without one — approval binds pixels, and this
tool animates only approved pixels.

Moves (per-beat, deterministic):
- default: slow smoothstep push-in with slight drift, direction alternating by
  beat parity so consecutive cuts don't feel copy-pasted
- beats named in RINGS get the sonar-pulse overlay (the tree's footstep sense)
  radiating from off-frame — the story-critical graphic the diffusion models
  kept fumbling, drawn exactly, every time
"""

import argparse
import math
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from generate_shots import parse_shots  # noqa: E402
from render_local import approved  # noqa: E402

FRAMES, FPS = 144, 24          # 6s — matches the beat lengths and the paid takes
RINGS = {10, 15}               # underground beats: the footstep pulse is post's job
GLOW = {1, 2, 3}               # screen-lit beats get the monitor-glow breathing


def ring_overlay(size, phase: float, brightness: float):
    W, H = size
    ov = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(ov)
    cx, cy = int(W * 1.25), int(H * 0.45)
    for k in range(3):
        r = int((0.25 + ((phase + k / 3) % 1.0)) * W * 1.4)
        a = int(brightness * 190 * (1.0 - ((phase + k / 3) % 1.0)))
        for w_, aa in ((24, a // 3), (10, a)):
            d.ellipse([cx - r, cy - r, cx + r, cy + r],
                      outline=(aa, int(aa * .82), int(aa * .45)), width=w_)
    return ov.filter(ImageFilter.GaussianBlur(6))


def animate(still: Path, num: int, dest: Path) -> None:
    src = Image.open(still).convert("RGB")
    W, H = src.size
    right = num % 2 == 0        # alternate drift so cuts don't feel cloned
    with tempfile.TemporaryDirectory() as td:
        for i in range(FRAMES):
            t = i / (FRAMES - 1)
            ease = t * t * (3 - 2 * t)
            zoom = 1.0 + 0.06 * ease
            cw, ch = int(W / zoom), int(H / zoom)
            cx = int((W - cw) * (0.5 + (0.10 if right else -0.10) * ease))
            cy = int((H - ch) * (0.5 - 0.06 * ease))
            cx = max(0, min(W - cw, cx))
            cy = max(0, min(H - ch, cy))
            frame = src.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
            if num in GLOW:
                g = 1.0 + 0.03 * math.sin(2 * math.pi * 1.4 * (i / FPS)) * (0.4 + 0.6 * ease)
                frame = ImageEnhance.Brightness(frame).enhance(g)
            if num in RINGS:
                frame = ImageChops.add(frame, ring_overlay((W, H), (i / FPS) * 0.35, 0.9))
            frame.save(Path(td) / f"f{i:04d}.png")
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error",
                        "-framerate", str(FPS), "-i", str(Path(td) / "f%04d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                        "-movflags", "+faststart", str(dest)], check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("genome")
    ap.add_argument("node")
    ap.add_argument("--beats", default="", help="comma list; default: all approved")
    a = ap.parse_args()

    ok, detail = approved(a.genome, a.node)
    if not ok:
        raise SystemExit(f"{a.node} is NOT approved — {detail} (STEWARDSHIP §6)")
    nodes = REPO / "genomes" / a.genome / "nodes"
    d = next(x for x in sorted(nodes.iterdir())
             if x.is_dir() and x.name.startswith(a.node))
    want = {int(b) for b in a.beats.split(",") if b.strip()} if a.beats else None
    out_dir = d / "takes" / "clips"
    out_dir.mkdir(parents=True, exist_ok=True)

    made = 0
    for s in parse_shots((d / "shots.md").read_text()):
        if want and s["num"] not in want:
            continue
        still = d / "stills" / f"{s['num']:02d}-{s['slug']}.png"
        if not still.exists():
            if want:
                print(f"  beat {s['num']:02d}: no APPROVED still — skipped")
            continue
        dest = out_dir / f"{s['num']:02d}-{s['slug']}.POST.mp4"
        animate(still, s["num"], dest)
        dest.with_suffix("").with_suffix(".meta.yaml").write_text(
            "# Shot provenance (7.2)\n"
            "platform: local-deterministic\n"
            "model: none — code (post_motion.py: smoothstep push-in"
            + (", glow breathing" if s["num"] in GLOW else "")
            + (", sonar-ring overlay" if s["num"] in RINGS else "") + ")\n"
            f"input_still: {still.name}\n"
            f"frames: {FRAMES}\nfps: {FPS}\ncost_usd: 0\n"
            f"date: {date.today().isoformat()}\n")
        print(f"  ✓ {dest.name}")
        made += 1
    print(f"{made} POST take(s) — $0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
