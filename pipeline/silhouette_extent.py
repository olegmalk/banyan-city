#!/usr/bin/env python3
"""DID THE SILHOUETTE MOVE? -- the boundary, not the pixels inside it.

Written 2026-08-17 by the motion lane (research arm), funded as "Tier 0" after an
external-literature pass found that no off-the-shelf metric answers our question.
Companion to `body_motion.py`, NOT a replacement: that one measures how far
content TRAVELS, this one measures where the figure's OUTLINE is. Read the next
section before either.

================================================================================
THE PRINCIPLE -- THIS IS THE WHOLE REASON THE TOOL EXISTS
================================================================================
SILHOUETTE EXTENT IS INVARIANT TO RE-INKING-IN-PLACE. Re-inking changes pixels
INSIDE the boundary; it does not MOVE the boundary. A goblin redrawn in the same
folded pose has a new shadow on the skull, a redrawn ear edge and reshuffled
grass -- and the topmost row of his silhouette does not budge. A goblin who
stands up moves that row, and nothing else can move it.

That is why the beat-17 positive control succeeded where every picture-change
metric on this bench failed. Its method -- colour-mask the figure, track the
topmost solid row -- was not a lucky heuristic. It was an EXTENT measure, and
extent is the class of measure that survives re-inking. A future lane choosing an
instrument should reach for this class first.

THE DISTINCTION THAT HAS COST US THE MOST TIME, made explicit here because it
keeps being lost (eight measures retired in the week to 2026-08-16, several of
them to exactly this confusion):

    Background-anchored REGION DIFFERENCING would tell us "the board moved and
    the figure did not", as a number, cheaply. It CANNOT separate re-inking from
    movement, because re-inking produces real, large change inside the figure
    region. It is a fine instrument for the board. It is the WRONG instrument for
    the figure, and a lane that reaches for it on a figure will conclude that a
    frozen guard is acting.

    SILHOUETTE EXTENT CAN separate them. That is the entire difference, and it is
    why `region_mad` is computed in this module but nested under
    DIAGNOSTIC_NOT_A_BODY_SIGNAL so it cannot be quoted as one by accident.

================================================================================
WHY THE FRAME-BY-FRAME HUMAN READ IS THE METHOD, NOT A STOPGAP
================================================================================
Lanes keep apologising for cold-reading frames as though it were a placeholder
until a real metric arrives. It is not. It is the literature's own answer for
animation, and the reason is specific rather than squeamish: PRETRAINED POSE
ESTIMATORS ARE NEAR COIN-FLIP ON ILLUSTRATIONS BECAUSE ILLUSTRATED PROPORTIONS
DEVIATE TOO FAR FROM THE HUMAN FORM (bigger heads and eyes, body-relative screen
area). Out-of-the-box OpenPose on illustrated characters scores OKS@50 0.4922
against 0.8982 for a model fine-tuned on illustrations -- Chen & Zwicker, WACV
2022, Table 1, https://arxiv.org/abs/2108.01819. AniSora and ToonComposer, both
animation-specific, fall back to VBench plus human double-blind for the same
reason.

So the number this tool prints is a FILTER on which clips a human opens, and the
overlay is how the human checks the filter. It is never the verdict.

================================================================================
TIER 2 (REAL POSE ESTIMATION) IS DECLINED -- FOUR REASONS, EACH SUFFICIENT
================================================================================
Recorded so nobody re-opens it. No founder decision is required; the licence
question below is moot because reasons 2-4 stand without it.

  1. Pretrained estimators are near coin-flip on our material: OKS@50 0.49
     against 0.90 fine-tuned (WACV 2022 Table 1, above). MediaPipe (Apache-2.0)
     and RTMPose (Apache-2.0) are cheap and correctly licensed and still cannot
     source a verdict here without validation of their own.
  2. The one purpose-built anime pose model, bizarre-pose-estimator
     (https://github.com/ShuhongChen/bizarre-pose-estimator), is AGPL-3.0,
     Docker+GPU, 86.8m params at 217.7 ms/img, and dormant at 12 commits since
     2022.
  3. IT IS SINGLE-CHARACTER BY DESIGN. The paper describes a "single-region
     proposer" and lists multi-character detection as future work, stating "we
     cannot expect a system trained on such data to perform well in-the-wild".
     Our shots are two-guard. Direct mismatch.
  4. It would need its OWN positive control before any lane could quote it --
     the same labour as the frame-by-frame human read, plus a new tool to
     distrust. That is the whole argument.

REJECTED ON LICENCE, recorded so a lane finds this note instead of the repo:
CoTracker / CoTracker3, https://github.com/facebookresearch/co-tracker, is the
best technical fit we found -- joint point tracking built explicitly for
"dynamic objects and a moving camera", which is precisely our camera-versus-body
confound. The majority of it is CC-BY-NC (non-commercial) and a GPU is strongly
recommended. banyan-city is a live product; do not ship it. If the licence ever
changes, this is the thing to revisit first.

================================================================================
THIS IS NOT ONE TOOL. IT IS ONE SEGMENTATION RULE PER SHOT FAMILY.
================================================================================
The harness, the extent statistics, the anchor and the overlay are general. THE
RULE THAT DECIDES WHICH PIXELS ARE THE FIGURE IS NOT. Colour-segmenting a dark
goblin against sky above a horizon does not transfer to a two-guard interior, and
a lane that points this at a new shot family MUST expect to write the rule and
validate it on that family before quoting a number. `--rule` is therefore
REQUIRED and has no default: the tool refuses to guess rather than silently
applying yesterday's rule to today's shot. `--list-rules` prints what exists.

================================================================================
THE MANDATORY OVERLAY IS THE REASON A NUMBER HERE CAN BE TRUSTED
================================================================================
On 2026-08-16 the parallel lane's first pass at this method scored THREE GENUINE
STAND-UPS as "no movement". The cause was sky speckle: a handful of stray mask
pixels near the top of frame pinned the topmost row at ~0 for every frame, so a
real 30%-of-frame head rise measured as flat. Nothing in the numbers looked
wrong. Overlaying the detection mask back onto the frames found it immediately.

So: `--overlay PATH` IS REQUIRED to print a verdict. `measure_clip()` raises
without one. This is not politeness, it is the guard that makes the instrument
honest, and it lives in code because a convention would have been skipped.

Two defences against that specific bug are built in and both are reported:
  * `min_run` -- a row counts as the silhouette top only if it contains a
    CONTIGUOUS run of at least `min_run` mask pixels. Speckle is short.
  * `speckle_frac` -- how much of the mask sits outside the largest row-run
    band. If it is not small the rule is leaking and the reading is void.

================================================================================
VALIDATION GATES -- ALL FOUR MUST PASS (`--selftest`)
================================================================================
  1. A frozen clip reads EXACTLY zero extent change.
  2. A synthetic vertical translation of known magnitude recovers to within 2px.
  3. A synthetic pan MOVES THE ANCHOR -- the anchor is what tells a lane the
     camera moved rather than the body, so an anchor that cannot detect a pan is
     not an anchor.
  4. A RE-INKED pair -- same silhouette, fresh noise and a contrast change
     inside it -- reads zero extent change while `region_mad` reads large. This
     is the failure mode the tool exists to catch and the one that separates it
     from every metric we have retired.

$0, CPU-only, numpy + ffmpeg. Touches no GPU and no render queue.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


# ----------------------------------------------------------------- decoding
def read_rgb(path, scale=2):
    """Every frame as (n, h, w, 3) uint8 at 1/`scale`.

    -vsync 0 for read_gray's reason: a decoder that retimes frames would forge
    the freeze we are measuring. RGB rather than gray because segmentation rules
    on cel art lean on hue, and because the overlay needs colour anyway.
    """
    import numpy as np

    from hold_period import _ffmpeg, probe

    w, h, fps = probe(str(path))
    sw, sh = max(16, w // scale), max(16, h // scale)
    sw, sh = sw - (sw % 2), sh - (sh % 2)
    r = subprocess.run(
        [_ffmpeg(), "-v", "error", "-i", str(path), "-vsync", "0",
         "-vf", "scale=%d:%d,format=rgb24" % (sw, sh), "-f", "rawvideo", "-"],
        capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg failed on %s: %s"
                           % (path, r.stderr.decode("utf-8", "replace")[:300]))
    buf = np.frombuffer(r.stdout, dtype=np.uint8)
    n = buf.size // (sw * sh * 3)
    return buf[:n * sw * sh * 3].reshape(n, sh, sw, 3), fps, (w, h)


def _ffprobe() -> str:
    """hold_period has `_ffmpeg()` but calls bare `ffprobe`; mirror its candidate
    logic here rather than reaching into it, so a PATH-less shell still works."""
    for c in ("/opt/homebrew/bin/ffprobe", "/usr/local/bin/ffprobe", "ffprobe"):
        if c == "ffprobe" or Path(c).exists():
            return c
    return "ffprobe"


def hold_factor(path):
    """Picture-hold factor from ffmpeg's mpdecimate -- the EXTERNAL cross-check.

    Validated 2026-08-15 against synthetic ground truth: 2.88x on a clip built to
    hold every picture for 3 frames, 1.00x on a genuinely moving clip, and 2.77x
    on the same held clip under heavy grain. It survives codec noise because it
    thresholds 8x8 BLOCKS (defaults hi=64*12, lo=64*5, frac=0.33) instead of
    asking "did anything change at all" -- which is precisely how the retired
    `cadence` metric returned 1.00x on a 3x-held clip.

    Reported BESIDE the extent numbers and never merged with them: it answers
    "how often does a new picture arrive", not "did the body move". The one clip
    on record that performs its action scores WORST of its set on picture-rate.
    """
    from hold_period import _ffmpeg

    total = subprocess.run(
        [_ffprobe(), "-v", "error", "-select_streams", "v:0", "-count_frames",
         "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, encoding="utf-8")
    r = subprocess.run(
        [_ffmpeg(), "-nostats", "-loglevel", "debug", "-i", str(path),
         "-vf", "mpdecimate", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    kept = r.stderr.count(" keep pts:")
    try:
        n = int(total.stdout.strip())
    except ValueError:
        return {"error": "frame count unavailable"}
    if kept == 0:
        return {"error": "mpdecimate kept no frames"}
    runs = [int(t.split(":")[1]) for t in r.stderr.split()
            if t.startswith("drop_count:")]
    return {
        "frames": n,
        "distinct_pictures": kept,
        "hold_factor": round(n / kept, 3),
        "longest_hold_frames": (max([v for v in runs if v > 0], default=0) + 1),
    }


# --------------------------------------------------------- segmentation rules
# A rule maps (n, h, w, 3) uint8 -> (n, h, w) bool. It is the ONLY shot-family
# specific part of this module. Adding one is expected; validating it on the
# family you point it at is not optional.
def _rule_dark_figure(rgb, thresh=90, **kw):
    """Figure is DARKER than its surround. The beat-17 family: a dark goblin
    against sky and pale ground. `thresh` is a luma level, 0-255."""
    luma = rgb.astype("f4") @ [0.299, 0.587, 0.114]
    return luma < float(thresh)


def _rule_light_figure(rgb, thresh=165, **kw):
    """Figure is LIGHTER than its surround. Inverse of the above."""
    luma = rgb.astype("f4") @ [0.299, 0.587, 0.114]
    return luma > float(thresh)


def _rule_saturated_figure(rgb, thresh=60, **kw):
    """Figure carries COLOUR against a desaturated ground -- a costume against
    stone or fog. `thresh` is max-minus-min channel spread, 0-255."""
    x = rgb.astype("i2")
    return (x.max(axis=-1) - x.min(axis=-1)) > int(thresh)


RULES = {
    "dark_figure": _rule_dark_figure,
    "light_figure": _rule_light_figure,
    "saturated_figure": _rule_saturated_figure,
}


# ------------------------------------------------------------------- extent
def row_runs(mask_row, min_run):
    """Longest contiguous run of True in a 1-D bool row.

    The anti-speckle primitive. A stray pixel of sky noise is a run of 1; a head
    is a run of tens. Comparing the LONGEST RUN against `min_run` is what stopped
    three genuine stand-ups reading as flat.
    """
    import numpy as np

    if not mask_row.any():
        return 0
    d = np.diff(np.concatenate(([0], mask_row.view("u1"), [0])).astype("i1"))
    starts = np.flatnonzero(d == 1)
    ends = np.flatnonzero(d == -1)
    return int((ends - starts).max()) if starts.size else 0


def extent(mask, min_run=8, band=None):
    """Boundary statistics for one frame's mask. Every field is BOUNDARY-derived
    and therefore invariant to re-inking inside the silhouette.

    `band` optionally restricts the search to (y0, y1) -- the beat-17 method's
    "above the horizon" constraint, which is how it knew the mountains held
    still while the head rose.
    """
    import numpy as np

    m = mask
    y0, y1 = (0, m.shape[0]) if band is None else band
    m = m[y0:y1]
    longest = np.array([row_runs(m[y], min_run) for y in range(m.shape[0])])
    solid = np.flatnonzero(longest >= min_run)
    if solid.size == 0:
        return {"top_row": None, "bottom_row": None, "height_px": 0,
                "area_px": int(m.sum()), "centroid_y": None,
                "speckle_frac": 1.0 if m.any() else 0.0}
    top, bot = int(solid[0]), int(solid[-1])
    inband = m[top:bot + 1]
    area = int(m.sum())
    ys = np.flatnonzero(m.any(axis=1))
    cy = float((np.arange(m.shape[0])[:, None] * m).sum() / area) if area else None
    return {
        "top_row": top + y0,
        "bottom_row": bot + y0,
        "height_px": bot - top + 1,
        "area_px": area,
        "centroid_y": None if cy is None else round(cy + y0, 2),
        # how much mask lives OUTSIDE the solid band -- leak detector
        "speckle_frac": round(float(1.0 - inband.sum() / area), 4) if area else 0.0,
        "rows_with_any_mask": int(ys.size),
    }


def anchor_drift(rgb, box):
    """Does the ASSERTED-STATIC region actually hold still?

    `box` is (y0, y1, x0, x1). The caller asserts this region is background that
    does not move -- a horizon, a mountain line, a wall. This function tests the
    assertion instead of trusting it, because the assertion is what licenses the
    conclusion "the BODY moved" rather than "the CAMERA moved".

    Vertical shift per frame by 1-D cross-correlation of the region's ROW PROFILE
    against frame 0's, over integer shifts in +-`radius`. Centre-of-mass was tried
    first and REJECTED by gate 3: on a region of near-isotropic texture the centre
    of mass of |highpass| is invariant to a shift, so it read a 9px pan as 0.04px.
    Correlation of the profile actually locates the shift.

    `profile_contrast` is reported because AN ANCHOR ON A FEATURELESS REGION
    CANNOT MEASURE ANYTHING. If it is near zero the region has no structure to
    track and `holds_still` is meaningless rather than reassuring -- this is the
    pathology that made a horizon-row tachometer lock onto different edges frame
    to frame and invent a 0.78x pull-back on a stable clip.
    """
    import numpy as np

    y0, y1, x0, x1 = box
    reg = rgb[:, y0:y1, x0:x1].astype("f4") @ [0.299, 0.587, 0.114]
    prof = reg.mean(axis=2)                       # (n, rows)
    prof = prof - prof.mean(axis=1, keepdims=True)   # brightness change cannot pose as a shift
    nrows = prof.shape[1]
    radius = max(1, min(nrows // 3, 32))
    ref = prof[0]
    contrast = float(np.std(ref))

    shifts = []
    for i in range(prof.shape[0]):
        best, best_s = -2.0, 0
        for s in range(-radius, radius + 1):
            a = ref[max(0, s):nrows + min(0, s)]
            b = prof[i][max(0, -s):nrows - max(0, s)]
            if a.size < 8:
                continue
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            if na < 1e-6 or nb < 1e-6:
                continue
            c = float(np.dot(a, b) / (na * nb))
            if c > best:
                best, best_s = c, s
        shifts.append(best_s)
    d = np.array(shifts, dtype="f4")
    # RAILING. `radius` is clamped by the box height, so a short anchor box cannot
    # measure a large pan: it reports `radius` and stops. Observed 2026-08-17 on a
    # known 10px pan through a 16-row box (radius 5) reading 5.0px. This is the
    # same pathology that made chained-NCC camera scale unusable -- a value AT the
    # search boundary is a FLOOR, not a measurement. Give the anchor >=3x the pan
    # you expect to see, in rows.
    railed = bool(np.any(np.abs(d) >= radius))
    return {
        "box": [int(v) for v in box],
        "drift_px_max": round(float(np.max(np.abs(d))), 2),
        "drift_px_final": round(float(d[-1]), 2),
        "search_radius_px": int(radius),
        "railed_at_search_boundary": railed,
        "profile_contrast": round(contrast, 3),
        "measurable": bool(contrast >= 1.0),
        # None, NOT False, when unmeasurable: "unknown" must not read as "moved".
        # A lane that sees False concludes the camera panned; the truth is that
        # this region could not answer and another anchor is needed.
        "holds_still": (None if contrast < 1.0
                        else bool(np.max(np.abs(d)) < 2.0)),
        "note": ("NO VERTICAL STRUCTURE IN THIS BOX -- pick a region with a "
                 "horizontal edge in it (a horizon, a wall top, a roofline). "
                 "Row profiles are averaged across x, so texture that varies "
                 "only in x is invisible here."
                 if contrast < 1.0 else
                 ("DRIFT RAILED AT THE +-%dpx SEARCH BOUNDARY -- this is a "
                  "FLOOR, the real pan is larger. Use a taller anchor box "
                  "(>=3x the expected pan, in rows)." % radius
                  if railed else "")),
    }


# ------------------------------------------------------------------ overlay
def write_overlay(rgb, masks, tops, box, out_path, n_cells=6):
    """Burn the mask and the detected top row back onto sampled frames.

    THE NON-NEGOTIABLE ARTIFACT. Mask tinted red, detected top row a green rule,
    anchor box blue. A lane looks at this before quoting anything; it is what
    caught the sky-speckle bug that no number revealed.
    """
    import numpy as np

    from hold_period import _ffmpeg

    n, h, w, _ = rgb.shape
    idx = np.linspace(0, n - 1, min(n_cells, n)).astype(int)
    cells = []
    for i in idx:
        f = rgb[i].astype("i2").copy()
        m = masks[i]
        f[m] = (f[m] * 0.45 + np.array([255, 40, 40]) * 0.55).astype("i2")
        t = tops[i]
        if t is not None and 0 <= t < h:
            f[max(0, t - 1):t + 2, :] = [40, 255, 40]
        if box is not None:
            y0, y1, x0, x1 = box
            f[y0:y0 + 2, x0:x1] = [60, 120, 255]
            f[max(0, y1 - 2):y1, x0:x1] = [60, 120, 255]
        cells.append(np.clip(f, 0, 255).astype("u1"))
    sheet = np.concatenate(cells, axis=1)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [_ffmpeg(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", "%dx%d" % (sheet.shape[1], sheet.shape[0]), "-i", "-",
         "-frames:v", "1", str(out_path)],
        input=sheet.tobytes(), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("overlay write failed: %s"
                           % r.stderr.decode("utf-8", "replace")[:300])
    return {"path": str(out_path), "frames_shown": [int(v) for v in idx]}


# ------------------------------------------------------------------ measure
def measure_clip(path, rule, overlay, scale=2, min_run=8, band=None,
                 anchor=None, rule_kw=None, n_cells=6):
    """Extent ladder for one clip. `overlay` is REQUIRED -- see the docstring."""
    import numpy as np

    if not overlay:
        raise ValueError(
            "overlay path is REQUIRED. A number from this tool without the mask "
            "overlaid back onto the frames is exactly the reading that scored "
            "three genuine stand-ups as 'no movement' on 2026-08-16. Pass "
            "--overlay PATH and look at it.")
    if rule not in RULES:
        raise ValueError("unknown --rule %r; have %s. THE RULE IS SHOT-FAMILY "
                         "SPECIFIC -- write and validate one for a new family "
                         "rather than borrowing." % (rule, sorted(RULES)))

    rgb, fps, full = read_rgb(path, scale=scale)
    masks = RULES[rule](rgb, **(rule_kw or {}))
    ex = [extent(masks[i], min_run=min_run, band=band) for i in range(len(rgb))]
    tops = [e["top_row"] for e in ex]

    known = [t for t in tops if t is not None]
    rise = (max(known) - min(known)) if known else 0
    h = rgb.shape[1]

    # DIAGNOSTIC ONLY. region_mad cannot separate re-inking from movement; it is
    # here to show how large the in-silhouette change is while extent holds.
    fg = masks.reshape(len(masks), -1)
    luma = (rgb.astype("f4") @ [0.299, 0.587, 0.114]).reshape(len(rgb), -1)
    d = np.abs(np.diff(luma, axis=0))
    both = fg[:-1] & fg[1:]
    region_mad = float((d * both).sum() / max(both.sum(), 1))

    out = {
        "clip": str(path),
        "rule": rule, "rule_params": rule_kw or {},
        "read_at": "%dx%d (1/%d of %dx%d)" % (rgb.shape[2], h, scale,
                                              full[0], full[1]),
        "frames": int(len(rgb)),
        "band": None if band is None else [int(v) for v in band],
        # ---- the quotable numbers, all boundary-derived
        "top_row_ladder": [None if e["top_row"] is None else int(e["top_row"])
                           for e in ex[::max(1, len(ex) // 8)]],
        "top_row_range_px": int(rise),
        "top_row_range_frac_h": round(rise / h, 4),
        "height_px_first_last": [ex[0]["height_px"], ex[-1]["height_px"]],
        "centroid_y_first_last": [ex[0]["centroid_y"], ex[-1]["centroid_y"]],
        "frames_with_no_solid_row": sum(1 for t in tops if t is None),
        "speckle_frac_max": round(max(e["speckle_frac"] for e in ex), 4),
        # ---- context, never merged with the above
        "hold": hold_factor(path),
        "DIAGNOSTIC_NOT_A_BODY_SIGNAL": {
            "region_mad_in_silhouette": round(region_mad, 3),
            "why": "re-inking produces this; it is not movement. See docstring.",
        },
    }
    out["anchor"] = anchor_drift(rgb, anchor) if anchor else {
        "box": None,
        "warning": "NO ANCHOR ASSERTED -- extent change here cannot be "
                   "attributed to the body rather than the camera.",
    }
    out["overlay"] = write_overlay(rgb, masks, tops, anchor, overlay,
                                   n_cells=n_cells)
    out["verdict_is_a_filter_not_a_ruling"] = (
        "Open %s. If it disagrees with the number, the number is wrong."
        % out["overlay"]["path"])
    return out


# ----------------------------------------------------------------- selftest
def selftest(verbose=True):
    """Four synthetic gates with known answers. All four must pass."""
    import numpy as np

    rng = np.random.default_rng(20260817)
    h, w = 240, 160
    fails = []

    def figure_frame(top, noise=0, contrast=1.0, shift_x=0):
        """Pale ground, a dark blob whose TOP EDGE is at `top`."""
        f = np.full((h, w, 3), 210, dtype="i2")
        f += rng.integers(-6, 7, (h, w, 3))
        yy, xx = np.mgrid[0:h, 0:w]
        body = (yy >= top) & (np.abs(xx - (w // 2 + shift_x)) < 22)
        f[body] = (np.array([40, 45, 50]) * contrast).astype("i2")
        if noise:
            f[body] += rng.integers(-noise, noise + 1, (int(body.sum()), 3))
        return np.clip(f, 0, 255).astype("u1")

    def measure(frames, band=None, min_run=8):
        masks = _rule_dark_figure(frames, thresh=90)
        return [extent(masks[i], min_run=min_run, band=band)
                for i in range(len(frames))]

    # GATE 1 -- frozen reads exactly zero
    base = figure_frame(120)
    frozen = np.stack([base, base.copy(), base.copy()])
    ex = measure(frozen)
    tops = [e["top_row"] for e in ex]
    if verbose:
        print("  1 frozen              top rows %s" % tops)
    if len(set(tops)) != 1:
        fails.append("frozen clip must read one constant top row, got %s" % tops)

    # GATE 2 -- known translation recovers within 2px
    for true_rise in (10, 37, 64):
        seq = np.stack([figure_frame(120), figure_frame(120 - true_rise)])
        ex = measure(seq)
        got = ex[0]["top_row"] - ex[1]["top_row"]
        if verbose:
            print("  2 rise %2dpx           measured %dpx" % (true_rise, got))
        if abs(got - true_rise) > 2:
            fails.append("rise of %dpx measured as %dpx (>2px error)"
                         % (true_rise, got))

    # GATE 3 -- a pan MOVES THE ANCHOR.
    # The anchor region must carry STRUCTURE or there is nothing to track, so give
    # it horizontal banding the way a horizon or a mountain line would. And the
    # panned frame must be a ROLL OF THE SAME FRAME: rolling a freshly generated
    # frame only compares two independent noise fields, which is what made the
    # first version of this gate pass a broken estimator.
    def banded(top=120):
        f = figure_frame(top)
        yy = np.mgrid[0:h, 0:w][0]
        band = (yy >= 12) & (yy < 58)
        f = f.astype("i2")
        f[band] += (34 * np.sin(yy[band] / 3.5))[:, None].astype("i2")
        return np.clip(f, 0, 255).astype("u1")

    ref = banded()
    box = (10, 60, 10, w - 10)
    a_still = anchor_drift(np.stack([ref, ref.copy()]), box)
    a_pan = anchor_drift(np.stack([ref, np.roll(ref, 9, axis=0)]), box)
    if verbose:
        print("  3 anchor              still %.2fpx  panned %.2fpx  "
              "(contrast %.1f)" % (a_still["drift_px_max"],
                                   a_pan["drift_px_max"],
                                   a_pan["profile_contrast"]))
    if not a_still["holds_still"]:
        fails.append("anchor drifted %.2fpx on a static pair"
                     % a_still["drift_px_max"])
    if a_pan["holds_still"]:
        fails.append("anchor failed to detect a 9px pan (drift %.2fpx) -- an "
                     "anchor that cannot see a pan is not an anchor"
                     % a_pan["drift_px_max"])
    if abs(a_pan["drift_px_max"] - 9) > 2:
        fails.append("anchor measured a known 9px pan as %.2fpx"
                     % a_pan["drift_px_max"])

    # GATE 3b -- a FEATURELESS anchor must report itself unmeasurable rather than
    # reassuringly still. A flat region that says "holds_still" is a trap.
    flat = np.full((2, h, w, 3), 200, dtype="u1")
    a_flat = anchor_drift(flat, box)
    if verbose:
        print("  3b flat anchor        measurable=%s contrast %.3f"
              % (a_flat["measurable"], a_flat["profile_contrast"]))
    if a_flat["measurable"] or a_flat["holds_still"]:
        fails.append("a featureless anchor claimed to be measurable/still "
                     "(contrast %.3f) -- it must refuse instead"
                     % a_flat["profile_contrast"])

    # GATE 4 -- RE-INKED: extent holds while in-silhouette change is large.
    # This is the gate that separates this tool from every retired metric.
    a = figure_frame(120, noise=0, contrast=1.0)
    b = figure_frame(120, noise=55, contrast=1.6)
    ex = measure(np.stack([a, b]))
    reink_tops = [e["top_row"] for e in ex]
    luma = np.stack([a, b]).astype("f4") @ [0.299, 0.587, 0.114]
    m = _rule_dark_figure(np.stack([a, b]), thresh=90)
    both = m[0] & m[1]
    mad = float(np.abs(luma[1] - luma[0])[both].mean())
    if verbose:
        print("  4 re-inked in place   top rows %s   in-silhouette MAD %.1f"
              % (reink_tops, mad))
    if reink_tops[0] != reink_tops[1]:
        fails.append("RE-INKING MOVED THE MEASURED EXTENT (%s) -- this is the "
                     "exact failure the tool exists to avoid" % reink_tops)
    if mad < 5.0:
        fails.append("re-inked gate is toothless: in-silhouette MAD only %.2f, "
                     "so it does not exercise the distinction" % mad)

    # GATE 4b -- speckle must not pin the top row
    spk = figure_frame(120)
    spk[3, 5] = spk[6, 90] = spk[9, 140] = [10, 10, 10]
    ex = measure(np.stack([spk]), min_run=8)
    if verbose:
        print("  4b speckle            top row %s (figure top is 120)"
              % ex[0]["top_row"])
    if ex[0]["top_row"] != 120:
        fails.append("sky speckle pinned the top row to %s instead of 120 -- "
                     "min_run is not protecting the reading" % ex[0]["top_row"])

    if verbose:
        print()
        for f in fails:
            print("  FAIL: %s" % f)
        print("  %s" % ("ALL GATES PASS" if not fails else "%d FAILED" % len(fails)))
    return not fails


# --------------------------------------------------------------------- main
def main() -> int:
    p = argparse.ArgumentParser(
        description="Silhouette-extent tracking: did the OUTLINE move?",
        epilog="The rule is shot-family specific and the overlay is mandatory. "
               "Read the module docstring before quoting anything.")
    p.add_argument("clip", nargs="?")
    p.add_argument("--rule", help="segmentation rule (REQUIRED, no default)")
    p.add_argument("--list-rules", action="store_true")
    p.add_argument("--overlay", help="PNG contact sheet path (REQUIRED)")
    p.add_argument("--scale", type=int, default=2)
    p.add_argument("--min-run", type=int, default=8)
    p.add_argument("--thresh", type=float, default=None)
    p.add_argument("--band", help="y0:y1, restrict extent search")
    p.add_argument("--anchor", help="y0:y1:x0:x1 asserted-static region")
    p.add_argument("--cells", type=int, default=6)
    p.add_argument("--json", action="store_true")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()

    if a.selftest:
        return 0 if selftest() else 1
    if a.list_rules:
        for k, fn in sorted(RULES.items()):
            print("  %-18s %s" % (k, (fn.__doc__ or "").split("\n")[0]))
        print("\nA new shot family needs a NEW rule, written and validated on "
              "that family. Borrowing one is how a reading goes wrong.")
        return 0
    if not a.clip or not a.rule:
        p.error("clip and --rule are required (see --list-rules)")

    band = tuple(int(v) for v in a.band.split(":")) if a.band else None
    anchor = tuple(int(v) for v in a.anchor.split(":")) if a.anchor else None
    kw = {} if a.thresh is None else {"thresh": a.thresh}
    r = measure_clip(a.clip, a.rule, a.overlay, scale=a.scale,
                     min_run=a.min_run, band=band, anchor=anchor,
                     rule_kw=kw, n_cells=a.cells)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print("clip            %s" % r["clip"])
        print("rule            %s %s" % (r["rule"], r["rule_params"]))
        print("read at         %s, %d frames" % (r["read_at"], r["frames"]))
        print("top-row ladder  %s" % r["top_row_ladder"])
        print("EXTENT RANGE    %dpx  (%.1f%% of frame height)"
              % (r["top_row_range_px"], 100 * r["top_row_range_frac_h"]))
        print("speckle max     %.4f%s" % (r["speckle_frac_max"],
              "  <-- HIGH, rule is leaking" if r["speckle_frac_max"] > 0.05 else ""))
        print("no-solid-row    %d frames" % r["frames_with_no_solid_row"])
        print("anchor          %s" % json.dumps(r["anchor"]))
        print("hold            %s" % json.dumps(r["hold"]))
        print("diagnostic      %s" % json.dumps(r["DIAGNOSTIC_NOT_A_BODY_SIGNAL"]))
        print("\n%s" % r["verdict_is_a_filter_not_a_ruling"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
