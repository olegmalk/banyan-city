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
  - beat 9 (a sprout standing alone, "$ whoami") has the SAME artifact and worse,
    found 2026-08-07 when the founder corrected the beat number — "that's not the
    beat i was talking about. i was talking about BEAT 9." Counted off the f15
    take: three blades at frame 0, the top leaf divided by frame 5, seven blades
    on a stem carrying a whole extra node from frame 25 on. The quote above is
    his and stays on beat 11, which does divide a leaf; it was simply never the
    only one. Nothing about leaf count existed in either beat's negative.

Beat 11 measured 2.36 median with 0% frozen frames — the highest score of all
fifteen, and the steward called it the best beat in the episode. The score was the
sprout duplicating itself. **A frame-difference metric cannot tell animation from
hallucination; it rewards both.** That is why this tool exists and why the choice of
which beats use it belongs to the author, not to a number.

A held still is honest: it is exactly the frame the founder approved, for exactly as
long as the beat needs, with no content that was never drawn. Provenance is the
still's own — no video model is involved, so no video model's licence attaches.

THE MOVE ITSELF IS NOW RULED, and the rule is the founder's, 2026-08-07, verbatim:

    "for all of the images that have no animation and only zooming, first of all,
    do not do ping pong. second of all, it should be very slow and gentle zooming."

WHERE THE PING-PONG ACTUALLY IS, because the obvious answer is wrong and was
believed for an hour. `render_t3` palindromes any clip its slot outruns, and that
looked like the culprit. It is not: measured frame by frame, **no held beat in
either delivered cut reverses** — v30 beat 14 and v31 beat 14 are each a single
monotonic climb (20.0% and 20.6% of scale over 13.1s, zero reversals), because
their held clips were already cut to their slots so the palindrome never fired.

What does bounce is the **screening page**: it plays the 2.5s per-beat held clips
with `<video loop>`, so an 18% push-in ran to its end and snapped back to wide
every two and a half seconds, over and over, for as long as the founder watched.
That is a ping-pong, and it is the one he was looking at.

So the fix is in three places and only one of them was a bug:
  - the travel, here — 18% is why the snap-back was violent (`zoom_total`);
  - the loop, in SCREENING.html, which no longer loops a held clip;
  - the palindrome, in `render_t3.held_still` — a latent path, one short clip away
    from firing, now closed rather than left as the next session's surprise.
Neither the direction nor the gentleness is a preference to be re-tuned by a later
session on its own metric — see `scale_series` and the test that guards it.
"""

import argparse
import math
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


# GENTLENESS IS A RATE, NOT A TOTAL — that is the whole design of these three
# numbers, and it is what "very slow and gentle" (founder, 2026-08-07) means when
# the held beats run 2.6s to 13.0s. A fixed total would make the 2.6s beat drift
# five times faster than the 13.0s one and call both "3%".
#
# It replaces ZOOM = 0.18, which was 18% of scale on every held beat regardless of
# length, front-loaded by an ease-out: 10.1%/s at the first frame, half the travel
# spent in the first 39% of the shot. That was chosen against a different note —
# the founder had called a 6% version invisible ("this one has no motion, u sure
# you opened it") — and 18% overshot into an effect.
#
# 0.6%/s, clamped to 2–4% of total travel:
#     beat 05  2.58s -> 2.0% (floor)      beat 10  10.52s -> 4.0% (cap)
#     beat 04  3.50s -> 2.1%              beat 14  12.99s -> 4.0% (cap)
#     beat 07  6.64s -> 4.0% (cap)
# The floor keeps a short beat from having no move at all; the cap keeps a long one
# from reframing the picture the founder approved. Between them every held beat in
# episode 1 travels 2–4%, at 0.31–0.77%/s — an order of magnitude under the old
# curve's opening speed.
ZOOM_RATE_PER_S = 0.006
ZOOM_MIN, ZOOM_MAX = 0.02, 0.04
# LINEAR, AND THAT IS THE MONOTONICITY GUARANTEE. Two easing curves have been
# rejected by the founder, for opposite reasons: smoothstep because it eases IN as
# well as out ("feels like a weird slow key frame, it should be ease in and out,
# just ease out"), then cubic ease-out because it parks ("doesnt mean it should
# just stop at one point"). Constant rate does neither — it never creeps up and
# never arrives. At 0.31–0.77%/s there is no acceleration worth shaping, and a
# curve is one more thing that can be given a reversing exponent by accident.
EASE_EXP = 1.0
# NO LATERAL DRIFT. There was 70px of it, alternating direction by beat parity, on
# the theory that a pure scale is not a camera move and that consecutive held beats
# should not look copy-pasted. Founder: "its not zooming into the center, zooming
# into a random point for some reason." Correct — shifting the crop centre while the
# window shrinks moves the effective zoom origin, and flipping the direction per
# beat makes it look arbitrary rather than composed. A centred push-in IS a camera
# move. The variety I was buying was not worth breaking the geometry.
DRIFT_PX = 0


def zoom_total(seconds: float, override: float | None = None) -> float:
    """How far this clip travels, as a fraction of scale. See ZOOM_RATE_PER_S."""
    if override is not None:
        return max(0.0, float(override))
    return min(ZOOM_MAX, max(ZOOM_MIN, ZOOM_RATE_PER_S * seconds))


def scale_series(seconds: float, n: int, override: float | None = None) -> list:
    """The crop-window scale for each of n frames — the whole camera move.

    STRICTLY MONOTONIC AND STRICTLY DECREASING, one direction for the entire
    clip, which is the founder's rule quoted in this module's docstring. The
    window starts wide (1 + total) and shrinks to exactly 1.0, so the picture
    pushes IN and never comes back. Split out as a pure function precisely so a
    test can assert that, because "no ping pong" is the kind of property that
    gets reintroduced by a plausible-looking easing tweak rather than on purpose.
    """
    total = zoom_total(seconds, override)
    if n < 2:
        return [1.0 + total]
    return [1.0 + total * (1 - (i / (n - 1)) ** EASE_EXP) for i in range(n)]


def hold(still: Path, out: Path, seconds: float, beat: int,
         zoom: bool = True, zoom_override: float | None = None) -> None:
    """Hold the still, with a slow push-in unless asked for a frozen frame.

    THE PUSH-IN IS THE DEFAULT, and that is the founder's rule, 2026-08-03: "if
    theres nothing to animate, just do the static rule. slow zooming."
    A truly frozen frame inside a moving episode reads as a stalled player rather
    than a held shot — he saw exactly that when a file got overwritten under an
    open player and said "its just stuck at this frame for the entire duration".
    A slow move says "this is a held shot" instead.

    Deterministic, computed rather than generated: nothing can morph, split or
    invent, which is the whole reason a held beat exists. One-way and centred on
    the frame — see `scale_series` for the direction rule and DRIFT_PX for why
    there is no lateral travel.
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
    # CEIL, NOT TRUNCATE. `int(24 * 2.5833)` is 61, not 62 — a frame lost to
    # float, and a held clip one frame short of its slot is exactly what makes
    # render_t3 loop it. Round up: covering the slot costs at most a frame that
    # gets trimmed, falling short costs the wrap this file exists to prevent.
    n = max(2, math.ceil(FPS * seconds - 1e-9))
    zs = scale_series(seconds, n, zoom_override)
    # oversample once, then crop a shrinking window out of it: cropping a big
    # image keeps full detail at every step, where scaling up each frame would
    # soften the picture the founder approved
    over = zs[0] + 0.02
    big = src.resize((int(W * over), int(H * over)), Image.LANCZOS)
    with tempfile.TemporaryDirectory() as td:
        for i, z in enumerate(zs):                      # window shrinks -> push IN
            cw, ch = int(W * z), int(H * z)
            # dead centre, every frame: the zoom origin must not move
            cx = (big.width - cw) // 2
            cy = (big.height - ch) // 2
            (big.crop((cx, cy, cx + cw, cy + ch))
                .resize((W, H), Image.LANCZOS)
                .save(f"{td}/f{i:04d}.png"))
        subprocess.run(
            ["ffmpeg", "-v", "error", "-r", str(FPS), "-i", f"{td}/f%04d.png",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
             "-movflags", "+faststart", "-y", str(out)],
            check=True, capture_output=True, encoding="utf-8", errors="replace")


def slot_seconds(node_dir: Path, beat: int, fallback: float) -> float:
    """How long this beat's slot is, so the held clip can BE that long.

    A held clip shorter than its slot is what hands `render_t3` the choice
    between looping it and reversing it, and there is no good answer at that
    point — both break a one-way move. `render_t3.held_still` now refuses the
    reversal; this removes the question by matching the slot in the first place.

    Same arithmetic as `render_t3.fit_duration`, and deliberately at its FLOOR
    (`vdur + 0.4`): any length in [vdur+0.4, vdur+2.0] is a fixed point of that
    function, so a clip cut to the floor neither loops nor lengthens the beat. A
    voiceless beat has no floor to compute — its slot is whatever clip it is
    given, capped by the script's paper timing — so `--seconds` stands.
    """
    vo = node_dir / "clips" / f"{beat:02d}-vo.json"
    if not vo.is_file():
        return fallback
    import json
    total = float(json.loads(vo.read_text(encoding="utf-8")).get("total_s") or 0)
    return max(fallback, round(total + 0.4, 2)) if total else fallback


def sidecar(clip: Path, still: Path, beat: int, seconds: float,
            frozen: bool = False, zoom_total_used: float = 0.0) -> None:
    """§7.2 provenance. No video model ran, so none is claimed.

    The licence question that attaches to this clip is the STILL's, which is
    recorded where the still is recorded — writing a video model here would be a
    lie, and writing nothing at all is what licence_gate calls a violation.

    BOTH TOP LINES ARE CLASSIFIER INPUT, and until 2026-08-07 both failed. The
    honest record was here all along; the one tool that decides what may be
    published could not read it, which is the same as not having written it.
    """
    Path(str(clip) + ".meta.yaml").write_text(
        "# Shot provenance (7.2) — written by hold_still at build time\n"
        # "local-cpu (ffmpeg)" resolved to NO licence route at all — not a
        # sentinel, not a pointer, no MODEL_LICENCES key — so licence_gate read
        # a held still as an unclassified model and refused it. Every word here
        # is load-bearing: "local-deterministic" is the key that resolves to
        # CC-BY-4.0 (our own output), which is exactly what a clip made by
        # ffmpeg out of a still we already hold IS.
        "platform: local-deterministic (pipeline/hold_still.py, ffmpeg)\n"
        # KEEP THIS VALUE BARE — it is read three ways and only the bare form
        # satisfies all three:
        #   licence_gate.py:466  SENTINELS is matched on the WHOLE value, never
        #                        as a fragment, so the old inline explanation
        #                        ("none — held still + code push-in, …") was an
        #                        unrecognised model name rather than a "none".
        #   render_t3.py:545     held_still() substring-matches "model: none".
        #                        Miss it and the clip is treated as footage and
        #                        PING-PONGED — the push-in run backwards, which
        #                        the founder ruled out on 2026-08-07.
        #   check_invention:207  skips held clips on the same substring. Miss it
        #                        and every held clip is scored for invented
        #                        content: four confident false positives.
        # Appending to this line breaks the gate; renaming the key breaks the
        # other two. The explanation moves to `note`, which nothing classifies.
        "model: none\n"
        "model_licence: n/a — inherits the still's licence, see stills/README.md\n"
        f"note: held still{'' if frozen else ' + code push-in'}, "
        f"no video model ran\n"
        f"shot_beat: {beat}\n"
        f"size: {W}x{H}\n"
        f"seconds: {seconds}\n"
        + ("" if frozen else
           f"zoom: push-in {zoom_total_used * 100:.1f}% over {seconds}s, "
           f"{zoom_total_used / seconds * 100:.2f}%/s, linear, centred, "
           f"monotonic (never reverses)\n")
        + f"source_still: {still.name}\n"
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
    ap.add_argument("--fit", action="store_true",
                    help="size the clip to the beat's slot (VO length + 0.4s) so "
                         "render_t3 never has to loop or reverse it; --seconds is "
                         "the floor, and stands alone on a beat with no voice")
    ap.add_argument("--zoom", type=float, default=None,
                    help="push-in as a fraction of scale, overriding the "
                         "rate-derived default (see zoom_total). Per-beat tuning "
                         "knob — the founder's rule is slow and gentle, so this "
                         "goes DOWN from 0.02-0.04, not up")
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
        secs = slot_seconds(node_dir, beat, a.seconds) if a.fit else a.seconds
        zt = zoom_total(secs, a.zoom)
        clip = out_dir / f"{beat:02d}-{slug}.mp4"
        hold(still, clip, secs, beat, zoom=not a.frozen, zoom_override=a.zoom)
        sidecar(clip, still, beat, secs, frozen=a.frozen, zoom_total_used=zt)
        move = "frozen" if a.frozen else f"push-in {zt * 100:.1f}%"
        print(f"  beat {beat:02d}  held {still.name}  ->  {clip.name} "
              f"({secs}s, {move}, {clip.stat().st_size // 1024}KB)")
        made += 1
    print(f"  {made} held still(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
