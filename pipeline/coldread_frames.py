#!/usr/bin/env python3
"""Prepare frames for a BLIND cold read — densely, through the motion, honestly.

    python3 pipeline/coldread_frames.py <clip.mp4> --out <dir>

    exit 0  -> sheets written, manifest printed
    exit 2  -> NO MOTION WINDOW FOUND. Nothing is written. This is on purpose;
               see "WHY IT REFUSES" below.

================================================================================
WHY THIS EXISTS: A SPARSE EVEN SPREAD MAKES SMOOTH MOTION LOOK LIKE A CUT
================================================================================
Until 2026-08-15 a blind cold read meant ~16 frames pulled EVENLY across a
97-frame clip and pasted into one contact sheet. Sixteen of ninety-seven is one
frame every ~6-7 source frames. Across the steep part of a movement arc, six
skipped frames of a continuous move look exactly like a cut, because the two
frames either side of the gap genuinely ARE far apart — that is what a steep arc
means. The reader is not wrong; the reader is being shown a lie.

It produced a wrong verdict on the record. On the restaged beat-02 clip
(ep2-b02-stg-headup-0815) the blind reader wrote, of the head lift:

    "That is a cut, not an in-between."

Its "frames 7 -> 8" were source frames 38 -> 45. Pulled CONSECUTIVELY, source
frames 38-49 are a smooth eased lift — the chin rises frame by frame, the eyes
open slits -> half -> full irises, no step anywhere — and the raw per-pair series
over that stretch is a textbook ease-in/ease-out arc:

    1.32 1.72 3.39 3.58 4.19 3.42 3.37 4.94 5.11 4.73 4.15 4.15 3.66 3.13 2.36

There was no cut. There was a sampling interval.

The same defect casts doubt backwards over every verdict the old method ever
produced, including the load-bearing one that "the fold happens in about three
frames while the camera swings simultaneously, so it reads as a lurch or a
stumble" — a claim about a THREE-FRAME event made from a set whose finest
resolution is seven frames. A set that coarse cannot see a three-frame event at
all; it can only infer one, and inference is what we were trying to avoid by
reading blind.

THE GENERAL LAW, which a separate lane hit from the numeric side the same night:
a cadence script called a clip "fine" at ratio 1.2 by pooling a frozen head, a
moving middle and a frozen tail into one population; measured inside the motion
window the same clip read 13.2. A STATISTIC COMPUTED OVER THE WRONG POPULATION IS
NOT A WEAK MEASUREMENT, IT IS A WRONG ONE. Sparse even sampling is that identical
mistake made visually: it pools the frozen head, the moving middle and the frozen
tail into one evenly-spaced set, and then the eye is asked to judge motion from a
population that is mostly not motion.

================================================================================
WHAT IT DOES INSTEAD
================================================================================
1. FIND THE MOTION WINDOW FIRST, and sample relative to it. Where the clip is
   moving is a measured fact, not a guess, so the frames spent on reading motion
   are spent inside it.

2. PARITY-COLLAPSE THE DIFFERENCE SERIES BEFORE LOOKING FOR THE WINDOW. In these
   LTX clips one index parity is a near-duplicate of its neighbour: odd pairs sit
   at 0.1-0.5 MAD while even pairs run 3-24. A naive "two consecutive pairs above
   threshold" onset test therefore CANNOT FIRE until the motion is so violent
   that even the duplicate pair clears the bar. On the control clip that rule
   dated onset at pair 40 = 1.67s; the true onset is pair 25 = 1.04s. It was
   half a second late on a four-second clip because it was asking a question the
   signal's shape forbids. The collapse is a sliding max of width 2 — the
   minimal operation that removes exactly a period-2 dropout and smears nothing
   else — and the onset test runs on that.

3. SAMPLE CONSECUTIVELY THROUGH THE WINDOW. Every source frame from
   (window start - PAD) to (window end + PAD), no skipping, laid out in reading
   order across as many sheets as it takes. Consecutive is the whole point: if
   two ADJACENT source frames look like a cut, that is a cut, and no sampling
   interval can be blamed for it. PAD frames of the frozen stretch are included
   on each side so the reader sees the motion begin and end against the stillness
   that abuts it.

4. STILL EMIT A WHOLE-CLIP OVERVIEW. A reader given only the dense strip would
   lose the dead air — and dead air is a real defect we are actively hunting
   ("roughly a third of the sequence is a still image at the end and another
   third is a still image at the start"). The overview is an even spread across
   the FULL clip and is honest at what it is for: proportions, not smoothness.
   Two sheets, two questions, neither pretending to answer the other's.

5. LABEL EVERY CELL WITH ITS SOURCE FRAME INDEX AND NOTHING ELSE. The index is
   not context: it does not name the clip, the beat, the recipe, the prompt, the
   parameter under test or which arm of a comparison this is. It is what lets the
   reader see for themselves that strip cells are one frame apart and overview
   cells are not — the exact fact whose absence caused the wrong verdict. No
   title, no filename in the image, no legend, no arrows. The reader gets frames
   and a number per frame, and that is all.

WHY IT REFUSES (exit 2). The defect above survived for weeks because the old path
never failed — handed a frozen clip it produced a beautiful evenly-spaced contact
sheet of sixteen identical frames and said nothing. A tool that cannot find
motion must say so loudly rather than emit a plausible-looking spread; silence is
how a measurement error becomes a verdict. If this exits 2 the answer is usually
"the clip is frozen", which is itself the finding.

================================================================================
THE NUMBERS IT PRINTS
================================================================================
Pure description, no verdict; the metric is a floor and never a verdict.

  flash   : pair 0 alone (frame 0 -> 1). The i2v restyle jolt, not motion. It is
            reported and then DROPPED from every other statistic — leaving it in
            inflates the head segment by an order of magnitude.
  head    : mean per-pair difference from pair 1 to the window start
  body    : mean per-pair difference INSIDE the window
  tail    : mean per-pair difference from window end to the last pair
  hold    : the hold period — how many frames each distinct picture is held
            for — from the peak lag of the autocorrelation of the per-pair
            difference series, computed in `pipeline/hold_period.py`. Reported
            with the number of distinct pictures and the effective frame rate,
            because "holds every 3 frames / effective 8 fps" is checkable by
            opening frames N, N+1, N+2 and a ratio is not.

  `cadence` WAS HERE AND IS RETIRED (2026-08-15). It was the louder-parity over
  quieter-parity mean, and it is a parity-2 detector: period 2 reads 26.67x,
  period 3 reads **1.00x**, period 4 reads 14.12x, period 5 reads **1.00x**.
  EVERY ODD HOLD PERIOD ALIASES TO 1.00x BY CONSTRUCTION, and 1.00x was
  documented right here as "every frame is new". It reported 1.06x on a clip
  holding every picture for three frames and a lane read that as clean. The
  number is still printed on its own RETIRED line, and only so that a reader
  holding a job spec from before this date can match it up. It is not a
  reading. Do not gate on it, quote it, or compare two clips with it. Full
  proof and the executable aliasing test: `pipeline/hold_period.py`.

Difference metric: mean absolute difference of 8-bit luma over the whole frame
(MAD). Validated 2026-08-15 against the published control ep2-b02-nw-0815: the
per-pair series is identical, ONSET lands on the same pair (25 = 1.04s), and head
reproduces exactly (0.478). Body reads 7.706 against a published 7.83 and the
retired ratio 2.14x against a published 2.21x, from a ONE-PAIR difference in where the window
is declared to end — pair 82 measures 0.59 MAD, above threshold, so this file
counts it as the last moving pair and the earlier scorer counted it as the first
tail pair. (Two slightly different scorings of that same control are already on
the record — 7.687/2.14 when first measured, 7.83/2.21 on revalidation — so a
1.6% spread on the body mean is the noise floor of the CONVENTION, not of the
measurement.) What matters for comparing clips is that one rule is applied to all
of them, which is why the rule lives in a file instead of in a session.

THE THRESHOLD IS ABSOLUTE (0.5 MAD) ON PURPOSE. A threshold scaled to each clip's
own peak would make "is it moving" mean something different in every clip, and
the whole point of a window is to compare clips. A consequence worth knowing: a
clip whose supposedly-frozen tail shimmers at 0.5-0.8 MAD will be reported as
STILL MOVING there, and its window will run to the end. That is not the tool
failing to trim — it is the tool declining to call 6x the control's tail
"stillness". Read it as the finding it is.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hold_period  # noqa: E402  (path fixed above so this runs from any cwd)

# --- the window rule -------------------------------------------------------
# 0.5 MAD: the level that reproduces the published control window exactly. Below
# it lies compression shimmer and grass noise; above it, something in the frame
# actually changed.
THRESHOLD = 0.5
# A run must last this many pairs to count as motion. Isolated one- and two-pair
# spikes are exposure flicker and restyle jolts, not movement -- beat 02's staged
# clip has a four-frame brightness flicker that spikes to 22 MAD with no pose
# change at all, and it must not be allowed to define a motion window on its own.
MIN_RUN = 5
# Frames of the frozen stretch shown either side of the window in the dense strip.
PAD = 3

# --- sheet layout ----------------------------------------------------------
# 5 x 4 = 20 portrait cells per sheet at 200px wide. Chosen so a 704x1280 frame
# is still ~200px across -- enough to see an eyelid state, which is the finest
# thing readers have had to judge -- while a whole 60-frame window fits in three
# sheets. Wider grids shrink the cell below the point where a slit-vs-half-lidded
# eye can be told apart, which is a distinction one of these reads turned on.
COLS, ROWS = 5, 4
CELL_W = 200
LABEL_H = 18
MAX_SHEETS = 8


def probe_fps(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", path],
        # encoding named on purpose: text mode alone decodes with the locale
        # codec, on a reader thread where a decode error never reaches us.
        capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    if "/" in out:
        a, b = out.split("/")
        return float(a) / float(b)
    return float(out)


def decode(path: str, workdir: str) -> list:
    """Every frame, losslessly, in order. -vsync 0 so nothing is duplicated or
    dropped on the way out: a decoder that helpfully retimes frames would forge
    the very cadence we are measuring."""
    subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vsync", "0",
                    os.path.join(workdir, "%05d.png")], check=True)
    return sorted(os.path.join(workdir, n) for n in os.listdir(workdir)
                  if n.endswith(".png"))


def diff_series(frames: list) -> np.ndarray:
    prev = np.asarray(Image.open(frames[0]).convert("L"), dtype=np.float32)
    out = []
    for f in frames[1:]:
        cur = np.asarray(Image.open(f).convert("L"), dtype=np.float32)
        out.append(float(np.abs(cur - prev).mean()))
        prev = cur
    return np.array(out)


def parity_collapse(d: np.ndarray) -> np.ndarray:
    """Sliding max of width 2. If one parity is a near-duplicate, its dropout is
    filled by its neighbour and a sustained-run test can finally fire on the
    stretch that is actually moving."""
    if len(d) < 2:
        return d.copy()
    return np.array([max(d[i], d[i + 1]) for i in range(len(d) - 1)] + [d[-1]])


def motion_window(d: np.ndarray, threshold: float = THRESHOLD):
    """Longest run of the parity-collapsed series at or above THRESHOLD.

    Returns (start_pair, end_pair) with end EXCLUSIVE, in indices into `d`
    (pair i is frame i -> frame i+1). Pair 0 is excluded from the search: the
    restyle flash is not motion and is loud enough to anchor a run on its own.
    """
    c = parity_collapse(d)
    best = None
    i = 1
    while i < len(c):
        if c[i] >= threshold:
            j = i
            while j < len(c) and c[j] >= threshold:
                j += 1
            if (j - i) >= MIN_RUN and (best is None or (j - i) > (best[1] - best[0])):
                best = (i, j)
            i = j
        else:
            i += 1
    return best


def segment_stats(d: np.ndarray, win, fps: float = 24.0) -> dict:
    s, e = win
    head = d[1:s]
    body = d[s:e]
    tail = d[e:]
    # THE HOLD PERIOD, which is what `cadence` was trying and failing to be.
    # Measured on the window's own pairs, so a frozen head and tail cannot
    # dilute it. `hold_period` is a filter and never a verdict: it exists to
    # stop a frozen clip reaching a human as "fine", not to pass anything.
    # The cold read — the frames this script writes — decides.
    hold = hold_period.hold_period([float(v) for v in body], fps=fps)
    # AND ON THE WHOLE CLIP MINUS THE FLASH, always, because the window can be
    # narrower than the 24 pairs a lag estimate needs and a tool that goes quiet
    # is how a frozen clip gets called fine. 0815-b13-AFTER's window is 8 pairs;
    # its whole-clip reading is period 3 at 0.96. The window reading is the more
    # specific one when it exists — read both, they answer different questions.
    whole = hold_period.hold_period([float(v) for v in d[1:]], fps=fps)
    stats = {
        "flash_pair0": round(float(d[0]), 3),
        "head": round(float(head.mean()), 3) if len(head) else None,
        "body": round(float(body.mean()), 3),
        "tail": round(float(tail.mean()), 3) if len(tail) else None,
        "hold_period": hold["period"],
        "hold_strength": hold["strength"],
        "distinct_pictures": hold["distinct_pictures"],
        "effective_fps": hold["effective_fps"],
        "hold_reading": hold["reading"],
        "autocorrelation_lags": hold["lags"],
        "wholeclip_hold_period": whole["period"],
        "wholeclip_hold_strength": whole["strength"],
        "wholeclip_hold_reading": whole["reading"],
        "wholeclip_autocorrelation_lags": whole["lags"],
    }
    # RETIRED, kept under a name that cannot be mistaken for a measurement, so
    # that a job spec written before 2026-08-15 can still be matched to its
    # clip. Blind to every odd period — see this module's docstring.
    stats["RETIRED_parity_ratio_blind_to_odd_periods"] = round(
        hold_period.legacy_parity_ratio([float(v) for v in body]), 2)
    return stats


def _font(size: int):
    for p in ("/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def sheet(frames: list, indices: list, out_path: str):
    """One contact sheet. Every cell carries its SOURCE FRAME INDEX and nothing
    else -- no title, no filename, no note about what this set is for."""
    with Image.open(frames[0]) as probe:
        w, h = probe.size
    cell_h = int(round(CELL_W * h / float(w)))
    sw = COLS * CELL_W
    sh = ROWS * (cell_h + LABEL_H)
    canvas = Image.new("RGB", (sw, sh), (24, 24, 24))
    draw = ImageDraw.Draw(canvas)
    fnt = _font(13)
    for n, src in enumerate(indices):
        col, row = n % COLS, n // COLS
        x, y = col * CELL_W, row * (cell_h + LABEL_H)
        with Image.open(frames[src]) as im:
            canvas.paste(im.convert("RGB").resize((CELL_W, cell_h), Image.LANCZOS), (x, y))
        draw.text((x + 4, y + cell_h + 2), "%03d" % src, fill=(190, 190, 190), font=fnt)
    canvas.save(out_path)
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("--out", required=True, help="directory for the sheets")
    ap.add_argument("--pad", type=int, default=PAD)
    ap.add_argument("--overview", type=int, default=16,
                    help="cells in the whole-clip overview sheet")
    ap.add_argument("--threshold", type=float, default=THRESHOLD)
    ap.add_argument("--json", default="", help="also write the manifest here")
    a = ap.parse_args()

    if not os.path.isfile(a.clip):
        print("!! no such clip: %s" % a.clip, file=sys.stderr)
        return 2

    fps = probe_fps(a.clip)
    work = tempfile.mkdtemp(prefix="coldread-")
    try:
        frames = decode(a.clip, work)
        n = len(frames)
        d = diff_series(frames)
        win = motion_window(d, a.threshold)
        if win is None:
            print("!! NO MOTION WINDOW: no run of >=%d pairs reaches %.2f MAD on the "
                  "parity-collapsed series. %d frames decoded, peak pair %.2f, "
                  "median pair %.2f. Refusing to emit an even spread -- if this clip "
                  "is frozen, THAT is the finding."
                  % (MIN_RUN, a.threshold, n, float(d[1:].max()), float(np.median(d[1:]))),
                  file=sys.stderr)
            return 2

        s, e = win
        stats = segment_stats(d, win, fps)
        os.makedirs(a.out, exist_ok=True)

        # --- dense consecutive strip through the motion, plus its frozen edges
        lo = max(0, s - a.pad)
        hi = min(n - 1, e + a.pad)
        strip = list(range(lo, hi + 1))
        per = COLS * ROWS
        need = (len(strip) + per - 1) // per
        if need > MAX_SHEETS:
            print("!! motion window is %d frames; consecutive coverage needs %d sheets "
                  "(max %d). Widen MAX_SHEETS deliberately rather than thinning the "
                  "strip -- thinning it is the defect this file exists to remove."
                  % (len(strip), need, MAX_SHEETS), file=sys.stderr)
            return 2

        written = []
        for k in range(need):
            chunk = strip[k * per:(k + 1) * per]
            written.append(sheet(frames, chunk,
                                 os.path.join(a.out, "strip-%02d.png" % (k + 1))))

        # --- whole-clip overview, honest about being an even spread
        ov = [int(round(i * (n - 1) / float(a.overview - 1))) for i in range(a.overview)]
        ov = sorted(set(ov))
        written.append(sheet(frames, ov, os.path.join(a.out, "overview.png")))

        man = {
            "frames": n,
            "fps": round(fps, 3),
            "duration_s": round((n - 1) / fps, 3),
            "window_pairs": [s, e],
            "window_s": [round(s / fps, 3), round(e / fps, 3)],
            "window_fraction_of_clip": round((e - s) / float(len(d)), 3),
            "stats": stats,
            "strip_source_frames": strip,
            "overview_source_frames": ov,
            "sheets": [os.path.basename(p) for p in written],
            "pair_series": [round(float(v), 3) for v in d],
        }
        if a.json:
            with open(a.json, "w") as fh:
                json.dump(man, fh, indent=2)

        print("frames %d @ %.2f fps (%.2fs)" % (n, fps, (n - 1) / fps))
        print("motion window pairs %d..%d  = %.2fs -> %.2fs  (%.1f%% of the clip)"
              % (s, e, s / fps, e / fps, 100.0 * (e - s) / len(d)))
        print("flash(pair0) %.2f | head %s | body %.3f | tail %s"
              % (stats["flash_pair0"], stats["head"], stats["body"],
                 stats["tail"]))
        print("HOLD in window: %s" % stats["hold_reading"])
        if stats["autocorrelation_lags"]:
            print("  autocorrelation  " + "  ".join(
                "lag%d %+.2f" % (k, v)
                for k, v in sorted(stats["autocorrelation_lags"].items())[:6]))
        print("HOLD whole clip: %s" % stats["wholeclip_hold_reading"])
        if stats["wholeclip_autocorrelation_lags"]:
            print("  autocorrelation  " + "  ".join(
                "lag%d %+.2f" % (k, v)
                for k, v in sorted(stats["wholeclip_autocorrelation_lags"].items())[:6]))
        print("RETIRED cadence %.2fx — parity-2 ratio, reads 1.00x on EVERY odd "
              "hold period; printed only to match old job specs, not a reading"
              % stats["RETIRED_parity_ratio_blind_to_odd_periods"])
        print("The metric is a FILTER, NEVER A VERDICT — the cold read decides.")
        print("strip: %d CONSECUTIVE source frames %d..%d over %d sheet(s)"
              % (len(strip), strip[0], strip[-1], need))
        print("overview: %s" % ", ".join(str(i) for i in ov))
        for p in written:
            print("WROTE %s" % p)
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
