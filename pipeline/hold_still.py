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

and, later the same day, having watched what "gentle" was read to mean:

    "zoom speed ladder is just overdoing it. simply make the zoom speed moderate."

and 2026-08-08, confirming the amount after watching the shortest and the longest
held beat side by side with nothing in between:

    "the zoom should be a balance between shortest and longest, and yes 12 percent
    is fine."

TWO RULINGS AND A CONFIRMATION, AND ONLY THE SECOND RULING EVER MOVED. "No ping
pong" is unchanged and is not up for re-tuning; what changed is the amount. The
ladder he is refusing is the rate model — a per-second drift clamped into a 2-4%
band, so that each beat got a different total worked out from its length. He
asked for one moderate move, not a scheme. `ZOOM_TOTAL` is now that one number
and it is the same on every held beat; the arc that got us there is recorded on
the constant, and 2026-08-08 is where it stops.

WHERE THE PING-PONG ACTUALLY IS, because the obvious answer is wrong and was
believed for an hour. `render_t3` palindromed any clip its slot outran (past
tense since 2026-08-19 — the 0819c audit found that branch firing on 8 of 18
FOOTAGE beats and the default fill is now a last-frame hold; the held branch
below is unchanged, and the palindrome is opt-in for nobody), and that
looked like the culprit. It is not: measured frame by frame, **no held beat in
either delivered cut reverses** — v30 beat 14 and v31 beat 14 are each a single
monotonic climb (20.0% and 20.6% of scale over 13.1s, zero reversals), because
their held clips were already cut to their slots so the palindrome never fired.

What does bounce is the **screening page**: it plays the 2.5s per-beat held clips
with `<video loop>`, so an 18% push-in ran to its end and snapped back to wide
every two and a half seconds, over and over, for as long as the founder watched.
That is a ping-pong, and it is the one he was looking at.

So the fix was in three places and only one of them was a bug:
  - the loop, in SCREENING.html, which no longer loops a held clip — THIS was the
    bug, and on its own it is what stopped the snap-back the founder saw;
  - the palindrome, in `render_t3.held_still` — a latent path, one short clip away
    from firing, now closed rather than left as the next session's surprise.
    Closing it for HELD clips did nothing for footage, and on 2026-08-19 the same
    surprise arrived from the other direction: 8 of the ep2 cut's 18 footage
    beats were being played forwards and backwards, silently. Footage now holds
    its last frame. This entry is why that took eleven days: the branch was
    audited once, cleared for the beats this file writes, and not asked about
    the beats it does not;
  - the travel, here, which was cut to 2-4% in the same pass on the theory that a
    smaller move made the snap gentler. That reasoning is retired: once the page
    stopped looping there was nothing to snap, and the cut cost the move its
    visibility for nothing. 12% is a screened amount rather than a mitigation.
The DIRECTION is not a preference to be re-tuned by a later session on its own
metric — see `scale_series` and the test that guards it. The AMOUNT is the
founder's and moves only when he says so; it moved three times, always on a
screening and never on a measurement, and on 2026-08-08 he confirmed the fourth
setting rather than asking for a fifth.

AND FOR FOUR DAYS ALL OF IT WAS MEASURED AGAINST A STRETCHED PICTURE. The stills
are 832x1216 and the clip is 704x1280; the frame builder closed that gap with a
two-argument resize, so every held beat the founder screened while settling 6% ->
18% -> 2-4% -> 12% was 24.4% taller than the still he approved. The move was
being judged on a distorted frame the whole time. Fixed 2026-08-08 in
`zoom_windows`, which cuts from the native still on `plate_prep`'s cover-centre
policy — the same framing render_t3 gives the delivered episode. The rulings
above survive it untouched: this changed the shape of the frame, never the
direction, the amount or the curve.
"""

import argparse
import hashlib
import math
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import plate_prep  # noqa: E402 — the shared cover-crop policy, no heavy deps

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


# THE TOTAL IS WHAT IS FIXED, and there is exactly one of it. Four settings have
# now been screened, so this is not a guess to be re-derived from first principles
# by the next session:
#
#     6%    "this one has no motion, u sure you opened it"   — invisible
#    18%    seen, and too much: front-loaded by an ease-out to 10.1%/s off the
#           first frame, half the travel spent in the first 39% of the shot
#    2-4%   a per-second rate (0.6%/s) clamped into a band, so every beat got a
#           different total worked out from its length — "way too slow", and the
#           scheme itself refused: "zoom speed ladder is just overdoing it"
#    12%    "simply make the zoom speed moderate" — this one, and the one he
#           CONFIRMED on 2026-08-08 after screening both extremes: "the zoom
#           should be a balance between shortest and longest, and yes 12 percent
#           is fine."
#
# WHY A TOTAL AND NOT A RATE, which is the reverse of what stood here this
# morning. The rate model's case was that the held beats run 2.6s to 13.0s, so a
# fixed total makes the short beat drift five times faster than the long one. True,
# and it is not what the eye is judging. What reads as the size of a camera move is
# how far the frame travelled by the end of the shot, not the pixels per second on
# the way; pinning the rate meant the 2.6s beat moved 2% and disappeared while the
# 13.0s beat moved its full 4%, which is the ladder. One number, every beat:
#
#     beat 05  2.58s -> 12% at 4.65%/s     beat 10  10.52s -> 12% at 1.14%/s
#     beat 04  3.50s -> 12% at 3.43%/s     beat 14  12.99s -> 12% at 0.92%/s
#     beat 07  6.64s -> 12% at 1.81%/s
#
# AND THE FOUNDER HAS NOW CONFIRMED THE TOTAL ON EXACTLY THAT TRADE, which is why
# the paragraph above is not the next session's to re-argue. He was shown the two
# extremes and nothing between them — beat 05 at 2.58s and beat 14 at 12.99s, the
# same 12% in each — and answered (2026-08-08): "the zoom should be a balance
# between shortest and longest, and yes 12 percent is fine." Read as: the single
# total IS that balance, chosen so the short beat is not a lunge and the long one
# is still visible. It is NOT a request to equalise the two rates — that is the
# ladder refused above, and it would put beat 05 back near 2% and invisible. If a
# later session hears it the other way, that is a question for him, not a change.
#
# Parameterized on purpose — the founder tunes ONE constant here, or one beat at a
# time with --zoom, and nothing else in the file has to be reasoned about.
ZOOM_TOTAL = 0.12
# LINEAR, AND THAT IS THE MONOTONICITY GUARANTEE. Two easing curves have been
# rejected by the founder, for opposite reasons: smoothstep because it eases IN as
# well as out ("feels like a weird slow key frame, it should be ease in and out,
# just ease out"), then cubic ease-out because it parks ("doesnt mean it should
# just stop at one point"). Constant rate does neither — it never creeps up and
# never arrives. A curve is also one more thing that can be given a reversing
# exponent by accident, and "no ping pong" is the ruling that did NOT move when
# the amount did: a bigger total makes the direction rule matter more, not less.
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
    """How far this clip travels, as a fraction of scale. See ZOOM_TOTAL.

    `seconds` is accepted and deliberately unused: the total does NOT depend on
    the length of the beat, and that independence is the founder's ruling rather
    than an accident of the arithmetic. Dropping the parameter would let the next
    version of this function quietly grow a length term again with no caller to
    change; keeping it means the signature says "we were asked, and the answer is
    the same". The rate that falls out is 12%/duration.
    """
    if override is not None:
        return max(0.0, float(override))
    return ZOOM_TOTAL


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


def zoom_windows(sw: int, sh: int, scales: list, tw: int = W, th: int = H) -> list:
    """The SOURCE-pixel window each frame is cut from. PURE — unit-tested.

    Returns one `(left, top, right, bottom)` box per entry in `scales`, in the
    coordinates of the original still, every one of them on the target aspect
    and every one of them centred on the same point.

    THE DEFECT THIS REPLACES, and it was in the held beats too. Until 2026-08-08
    this function did not exist and the loop below oversampled first:

        big = src.resize((int(W * over), int(H * over)))

    Two arguments, no aspect term. Every canon still is 832x1216 (0.684) and W:H
    is 704x1280 (0.550), so that line pulled the picture 24.4% taller before a
    single frame was cut, and every held beat in v30, v31 and v32 carries it —
    measured at 42.6dB against the approved still on beat 14. A held still whose
    whole promise is "exactly the frame the founder approved" was the one clip in
    the tree guaranteed to be a stretched frame the founder never saw.

    WHICH PIXELS LEAVE is not this module's decision to make. `plate_prep`
    already holds the policy — render_t3's own scale-to-cover plus centre crop,
    the framing every delivered episode uses — so the widest window here IS the
    conditioning plate, and a held beat and a rendered beat cut from the same
    still now start from the same composition instead of two different ones.

    NO OVERSAMPLED INTERMEDIATE, which is the second half of the fix and the part
    that is about sharpness rather than shape. Cover-cropping to 669x1216 and then
    oversampling to 802x1459 to crop out of would have been geometrically correct
    and visibly soft: it resamples the picture UP 1.2x, throws the extra pixels
    away again on the per-frame downscale, and every frame inherits the blur of an
    interpolation that invented nothing. Cutting each window straight out of the
    native still is one LANCZOS pass per frame from the real pixel grid — the
    widest frame is a 1.05x scale (669 -> 704) instead of 1.20x, and the tightest
    is 1.18x instead of 1.20x-then-0.89x. Same geometry, fewer resamples, and the
    old `+0.02` fudge that kept the crop box inside the oversampled buffer has
    nothing left to guard, so frame 0 is now the whole plate rather than 98.2% of
    it.

    The move itself is untouched: `scales` still comes from `scale_series`, so the
    first window is 1 + ZOOM_TOTAL times the last (1.1206 rather than 1.1200 flat,
    the difference being whole pixels — see `_same_parity`) and the sequence is
    still one-way. Boxes shrink toward a FIXED centre — see DRIFT_PX for why the
    zoom origin does not travel.
    """
    box = plate_prep.cover_crop_box(sw, sh, tw, th) or (0, 0, sw, sh)
    left, top, right, bottom = box
    kw, kh = right - left, bottom - top
    # the doubled centre, so an odd-sized window still lands on the same point
    # the plate is centred on rather than drifting half a pixel per frame
    cx2, cy2 = left + right, top + bottom
    widest = scales[0] if scales else 1.0
    out = []
    for z in scales:
        f = min(1.0, z / widest) if widest else 1.0
        cw = max(2, min(kw, _same_parity(round(kw * f), kw)))
        # height FROM the width and the target ratio, never from `f` again:
        # rounding each axis independently is how a window drifts off-aspect
        ch = max(2, min(kh, _same_parity(round(cw * th / tw), kh)))
        x = max(0, min(sw - cw, (cx2 - cw) // 2))
        y = max(0, min(sh - ch, (cy2 - ch) // 2))
        out.append((x, y, x + cw, y + ch))
    return out


def _same_parity(n: int, like: int) -> int:
    """`n`, or n-1, so that `like - n` is even. PURE.

    A HALF-PIXEL OF SHIMMER, AND IT IS WORTH A FUNCTION. `zoom_windows` centres
    every window with `(cx2 - cw) // 2`, which is exact when cw and the plate
    width have the same parity and half a pixel off when they do not. Let the
    widths round freely and the parity alternates frame to frame, so the centre
    hops 415.0, 415.5, 415.0 for the length of the shot — a sub-pixel left-right
    jitter riding on top of a move whose whole point is that it is smooth and
    centred, and the sort of thing that gets screened as "the zoom looks weird"
    with nothing in the recipe to blame. Snapping DOWN keeps widths inside the
    plate and keeps the series non-increasing, so the push-in stays one-way.
    """
    return int(n) - ((int(like) - int(n)) % 2)


def zoom_frames(src, scales: list, tw: int = W, th: int = H):
    """Yield the finished frames of the push-in, in order. PIL in, PIL out.

    Split from `hold` so the pixels can be asserted on without ffmpeg: the
    test that matters is that frame 0 IS `plate_prep.fit_cover`'s plate, byte
    for byte, and that is only checkable if something hands back an image.
    """
    from PIL import Image

    for box in zoom_windows(src.width, src.height, scales, tw, th):
        yield src.crop(box).resize((tw, th), Image.LANCZOS)


def hold(still: Path, out: Path, seconds: float, beat: int,
         zoom: bool = True, zoom_override: float | None = None) -> str:
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

    Returns the one-line framing record for the sidecar, empty on --frozen.
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
        # DELIBERATELY UNRECORDED, because this path's geometry is a separate
        # open question rather than a settled one. --frozen letterboxes
        # (decrease + pad) where the zoom path now cover-crops, so the two
        # disagree about framing on the same still; render_t3 would crop-to-cover
        # a padded frame and zoom the bars in. Nothing in the tree uses --frozen
        # — every held beat in v30/v31/v32 took the zoom — and changing its
        # framing is a recipe change the founder has not screened, so it is
        # written down here and left for him rather than fixed in passing.
        return ""

    from PIL import Image
    import tempfile
    src = Image.open(still).convert("RGB")
    # CEIL, NOT TRUNCATE. `int(24 * 2.5833)` is 61, not 62 — a frame lost to
    # float, and a held clip one frame short of its slot is exactly what makes
    # render_t3 loop it. Round up: covering the slot costs at most a frame that
    # gets trimmed, falling short costs the wrap this file exists to prevent.
    n = max(2, math.ceil(FPS * seconds - 1e-9))
    zs = scale_series(seconds, n, zoom_override)
    # A SHRINKING WINDOW CUT STRAIGHT OUT OF THE NATIVE STILL — no oversampled
    # intermediate and, above all, no two-argument resize. `zoom_windows` owns
    # both the aspect policy and the reasoning; the loop here is just the pixels.
    with tempfile.TemporaryDirectory() as td:
        for i, frame in enumerate(zoom_frames(src, zs)):    # window shrinks -> IN
            frame.save(f"{td}/f{i:04d}.png")
        subprocess.run(
            ["ffmpeg", "-v", "error", "-r", str(FPS), "-i", f"{td}/f%04d.png",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
             "-movflags", "+faststart", "-y", str(out)],
            check=True, capture_output=True, encoding="utf-8", errors="replace")
    return (plate_prep.crop_note(src.width, src.height, W, H)
            + "; the push-in then cuts each frame from inside that window, in "
              "the native still, one resample per frame")


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
            frozen: bool = False, zoom_total_used: float = 0.0,
            framing: str = "", provisional_reason: str = "") -> None:
    """§7.2 provenance. No video model ran, so none is claimed.

    The licence question that attaches to this clip is the STILL's, which is
    recorded where the still is recorded — writing a video model here would be a
    lie, and writing nothing at all is what licence_gate calls a violation.

    BOTH TOP LINES ARE CLASSIFIER INPUT, and until 2026-08-07 both failed. The
    honest record was here all along; the one tool that decides what may be
    published could not read it, which is the same as not having written it.

    AND THE NAME IS NOT ENOUGH TO SAY WHICH PIXELS THESE ARE (2026-08-08).
    `source_still: <name>` was the only frame reference this wrote, and a canon
    filename changes hands the moment a redraw is promoted — which is how a tall
    sapling ended up postering footage of bare soil on beats 7, 12 and 15.
    build_site.still_from_record() prefers a recorded HASH over the name for
    exactly that reason, and its only other defence ("the file under that name is
    newer than the clip") CANNOT FIRE ON THE DEPLOY: a fresh clone stamps every
    file with the checkout time, so on banyan.city — the one surface the founder
    screens from — the hash is the only defence there is. Every held clip written
    before today was defended on a laptop and undefended on Vercel; the five
    published ones were repaired by reading their hashes out of git history by
    hand (b6d435f), and this is what stops that repair being needed again.

    Measured off the bytes this function was HANDED, never looked up by name
    afterwards — looking it up by name later is the very failure being closed.
    """
    Path(str(clip) + ".meta.yaml").write_text(
        # THE PROVISIONAL BANNER IS THE FIRST THING IN THE FILE, and it is a
        # COMMENT so that no parser has to grow a case for it. v33 carried these
        # exact lines and they were appended to the sidecar BY HAND after the
        # tool had written it — which is the shape of defect f7de075 named on the
        # review sheets ("the builders are not in the repo, and that is how the
        # missing labels got in"). A label that a person has to remember is a
        # label that goes missing on the one run nobody double-checks.
        ("# ===================================================================\n"
           "# PROVISIONAL — the frame under this clip is a STEWARD PICK the\n"
           "# founder has not seen. Nothing here is canon, nothing here is\n"
           "# approved, and no file made from it may be promoted to a canon\n"
           "# name or published. Taste is the founder's (R4).\n"
           "# ===================================================================\n"
           if provisional_reason else "")
        + "# Shot provenance (7.2) — written by hold_still at build time\n"
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
        # WHICH PIXELS SURVIVED, because the stretch that made every held beat
        # in v30-v32 24.4% tall was invisible precisely for want of this line: a
        # resize that changes the aspect ratio raises nothing and reads, in a
        # record, exactly like one that does not. DOUBLE-QUOTED — the note says
        # "cover-centre (render_t3 policy: scale to cover, ...)" and a bare
        # colon-space in a plain scalar is a yaml parse error, which would take
        # licence_gate down with it.
        + (f'framing: "{framing}"\n' if framing else "")
        + ("" if frozen else
           f"zoom: push-in {zoom_total_used * 100:.1f}% over {seconds}s, "
           f"{zoom_total_used / seconds * 100:.2f}%/s, linear, centred, "
           f"monotonic (never reverses)\n")
        + f"source_still: {still.name}\n"
        # WHERE THAT NAME LIVES, because a held frame is no longer always in
        # `stills/`. A provisional pick sits in `takes/stills/`, and a resolver
        # handed only a bare name searches the canon directories and finds
        # nothing — the honest record has to say which directory it came out of.
        # Repo-relative and posix-spelled, so the line reads the same on the box.
        + f"source_still_path: {plate_prep.posix(plate_prep.rel_to_repo(still))}\n"
        + f"source_still_sha256: {hashlib.sha256(still.read_bytes()).hexdigest()}\n"
        "cost_usd: 0\n"
        "prompt: |-\n"
        # "the approved still" was false boilerplate and had been since the
        # provisional picks began: this tool holds whatever frame it is handed,
        # and on 2026-08-09 several of those were candidates the founder had not
        # seen. Approval is the T0 leaf's word (STEWARDSHIP §6) and it is not
        # this file's to assert — a record that claims an approval nobody gave is
        # the same class of lie as a poster promising pixels the clip lacks.
        "  (none — the chosen still is held; nothing was generated)\n"
        "negative: ''\n"
        # MACHINE-READABLE, not just the banner. The comment at the top is for a
        # person reading the file; `provisional: true` is for anything that ever
        # decides whether this clip may be published, and the two cannot drift
        # because one call writes both or neither.
        + ("provisional: true\n"
           "provisional_reason: |-\n"
           + "".join(f"  {line}\n" for line in provisional_reason.splitlines())
           if provisional_reason else ""), encoding="utf-8")


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
                    help="push-in as a fraction of scale for this run, overriding "
                         "ZOOM_TOTAL (see zoom_total). The per-BEAT knob: 0.12 is "
                         "the screened setting for all of them, so reach for this "
                         "when one picture wants a different move, not to re-tune "
                         "the default — that number is the founder's")
    ap.add_argument("--still", type=Path, default=None,
                    help="hold THIS frame instead of the beat's canon still — for "
                         "a beat that has none. Only a frame OUTSIDE the node's "
                         "stills/ directory (a take), and only with --provisional")
    ap.add_argument("--provisional", metavar="REASON", default="",
                    help="stamp the clip's sidecar PROVISIONAL with this reason: a "
                         "banner a person can see and `provisional: true` a gate "
                         "can read. Say which pick and on whose authority")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    node_dir = REPO / "genomes" / a.genome / "nodes" / a.node
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # A FRAME THAT IS NOT IN THE CANON DIRECTORY IS NOT CANON, and the guard says
    # so rather than trusting the caller to remember. `--still` exists for exactly
    # one situation — beat 06 on 2026-08-09, the only beat in episode 1 with no
    # approved frame at all, where the alternative was promoting a steward pick
    # into `stills/` to make `approved_still` find it. That promotion is R4's and
    # nobody else's, and a tool that makes it convenient to fake is worse than no
    # tool. So: one beat, a take, and a reason on the record.
    if a.still is not None:
        if len(a.beats) != 1:
            ap.error("--still names one frame, so it takes exactly one beat")
        if not a.still.is_file():
            ap.error(f"--still {a.still}: no such file")
        if a.still.resolve().parent == (node_dir / "stills").resolve():
            ap.error("--still is for a frame outside stills/ — a canon frame is "
                     "found by beat number, and naming one here would let a "
                     "REVOKED frame in through the back door")
        if not a.provisional:
            ap.error('--still requires --provisional "<reason>": the founder has '
                     "not seen this frame, and the clip must say so")

    made = 0
    for beat in a.beats:
        still = a.still or approved_still(node_dir, beat)
        slug = slug_for(node_dir, beat)
        if not still or not slug:
            print(f"  beat {beat:02d}: no approved still or no slug — skipped")
            continue
        secs = slot_seconds(node_dir, beat, a.seconds) if a.fit else a.seconds
        zt = zoom_total(secs, a.zoom)
        clip = out_dir / f"{beat:02d}-{slug}.mp4"
        framing = hold(still, clip, secs, beat,
                       zoom=not a.frozen, zoom_override=a.zoom)
        sidecar(clip, still, beat, secs, frozen=a.frozen, zoom_total_used=zt,
                framing=framing, provisional_reason=a.provisional)
        move = "frozen" if a.frozen else f"push-in {zt * 100:.1f}%"
        print(f"  beat {beat:02d}  held {still.name}  ->  {clip.name} "
              f"({secs}s, {move}, {clip.stat().st_size // 1024}KB)"
              f"{'  [PROVISIONAL]' if a.provisional else ''}")
        made += 1
    print(f"  {made} held still(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
