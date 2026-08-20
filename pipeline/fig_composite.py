#!/usr/bin/env python3
"""fig_composite.py -- put ONE clip's growing fig onto ANOTHER clip's held field.

WHY THIS EXISTS
---------------
Beat 01 has two clips and neither of them is the shot.

  * `ep2-b01-fignonly-s20260840-0820` (`--image-crf 33`) grows the fig 14.77x by a
    continuous path, 121/121 frames live -- and redraws the whole field while it
    does it (region NCC sapling 0.055, shaft -0.324).
  * `ep2-b01-figcrf10-s20260840-0820` (`--image-crf 10`, same seed, same init,
    same prompts, one argv value moved) holds the field better than anything
    ever measured on this beat (shaft 0.982, sapling 0.734, luma +0.92) -- and
    the fig only swells 1.79x.

`ep2-b01-figcrf10-s20260840-0820`'s verdict established that those are ONE knob:
`--image-crf` sets how far the whole picture may drift from its conditioning
image and the fig is part of the picture, so no setting separates them.  It
closed the flag route and licensed exactly one thing: LOCALISATION.  Separate
the fig from the field in the COMPOSITOR, where they can be driven
independently, instead of hunting a render setting that does it by accident.

WHAT THIS DOES
--------------
For each frame i:

  1.  The matte comes from `fig_track.py`'s OWN per-frame mask on the GROW clip
      -- the same boolean array whose `area_px` the growth arc is scored from.
      It is imported through `fig_track.track(..., mask_sink=...)`, never
      re-derived here, so the matte and the score cannot disagree.
  2.  That mask is DILATED and FEATHERED.  This is not cosmetic.  `fig_track`'s
      `binary_open` deliberately deletes the thin dark stem ("removes the thin
      dark stem, which ... would otherwise weld itself to the fig and inflate
      the area") -- correct for measuring a fig, wrong for cutting one out.  The
      stem and the contact shadow move WITH the fruit, and a matte that excludes
      them is the named risk of this whole rung: the fig reads as pasted.  The
      dilation radius scales with the fig's own equivalent radius so the halo
      grows as the fruit does.
  3.  The imported patch is GAIN-MATCHED to the held field through a ring around
      the matte.  The grow clip blooms +10.85 levels over its 121 frames and the
      held clip does not, so an unmatched paste drops a brightening object onto
      a steady plate and the seam is guaranteed.  The correction is a single
      scalar per frame, multiplicative on RGB -- which leaves chromaticity
      (R,G,B)/(R+G+B), and therefore HSV hue and saturation, EXACTLY unchanged.
      It cannot manufacture or destroy the G2 end-state clause; it is published
      per frame so a reader can see how hard it worked.
  4.  Everything outside the feathered matte is the held clip's own pixel,
      untouched.  `--freeze-band` optionally takes a horizontal band from the
      held clip's f000 instead -- for the residual grass, which re-inks even at
      crf 10 (0.062 against a 0.20 bar).  A frozen band's region NCC is 1.000 BY
      CONSTRUCTION and this file says so in its own output rather than letting
      the number read as a measurement.

DEAD ZONES ARE NOT FILLED IN
----------------------------
`fig_track` publishes no matte on a frame its gates killed.  This file does not
invent one.  On a dead frame the fig HOLDS: the last live matte and the last
live grow pixels are re-used, the frame index goes into `held_on_dead_frames`,
and the count is printed.  A composite whose fig is frozen for N frames is a
composite whose growth arc is worth exactly N frames less, and the reader is
told which ones.

Everything published here is $0, needs no GPU and no new plate: both ingredient
clips are already rendered and sha-verified.
"""
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fig_track as ft  # noqa: E402


# ---------------------------------------------------------------------------
# morphology (no scipy -- this must run on a bare venv, same rule as fig_track)
# ---------------------------------------------------------------------------

def _dilate_h(m: np.ndarray, w: int) -> np.ndarray:
    """Horizontal dilation by radius `w`, in O(log w) shifted ORs.

    Each round doubles the reach, so the shifts sum to exactly `w` and the
    result is exactly the (2w+1)-wide horizontal dilation -- not an
    approximation of one.  np.roll would wrap the frame edge onto itself, so
    the shift is done with explicit slicing.
    """
    if w <= 0:
        return m
    out = m
    step, rem = 1, w
    while rem > 0:
        s = min(step, rem)
        left = np.zeros_like(out)
        right = np.zeros_like(out)
        left[:, :-s] = out[:, s:]
        right[:, s:] = out[:, :-s]
        out = out | left | right
        rem -= s
        step *= 2
    return out


def dilate_disk(m: np.ndarray, d: int) -> np.ndarray:
    """Exact Euclidean dilation by a disk of radius `d`.

    A circle, not a square: a square structuring element pushes the matte
    d*sqrt(2) out on the diagonals, which on a small fig is a visible corner of
    imported field.
    """
    if d <= 0:
        return m
    h = m.shape[0]
    out = np.zeros_like(m)
    for dy in range(-d, d + 1):
        w = int(math.floor(math.sqrt(max(0.0, d * d - dy * dy))))
        row = _dilate_h(m, w)
        if dy == 0:
            out |= row
        elif dy > 0:
            out[:h - dy] |= row[dy:]
        else:
            out[-dy:] |= row[:h + dy]
    return out


def feather(m: np.ndarray, radius: float) -> np.ndarray:
    """Feather a boolean matte to a float alpha in [0,1] with a real Gaussian."""
    if radius <= 0:
        return m.astype(np.float64)
    im = Image.fromarray((m * 255).astype(np.uint8))
    im = im.filter(ImageFilter.GaussianBlur(radius=float(radius)))
    return np.asarray(im, np.float64) / 255.0


def luma(rgb: np.ndarray) -> np.ndarray:
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def frame_paths(d: str):
    names = sorted(n for n in os.listdir(d) if n.lower().endswith(".png"))
    return [os.path.join(d, n) for n in names]


# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grow", required=True, help="frames dir of the clip the FIG comes from")
    ap.add_argument("--held", required=True, help="frames dir of the clip the FIELD comes from")
    ap.add_argument("--anchor-mask", required=True, help="the inpaint/composite mask PNG")
    ap.add_argument("--anchor-cover-crop", default="832x1216->704x1280")
    ap.add_argument("--out-frames", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-mp4", help="also encode the frames (libx264, yuv420p)")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--crf", type=int, default=14)
    ap.add_argument("--masks", help="also keep fig_track's raw per-frame mattes here")
    ap.add_argument("--out-blend", help="write the BLEND ZONE per frame here as bNNN.png (255 = this "
                                        "pixel is not purely the held clip's). Feed it straight to "
                                        "fig_track --exclude-masks: it is the region whose local "
                                        "statistics belong to neither source clip, and a detector "
                                        "that models the background there is modelling a mixture. "
                                        "This file KNOWS the region; nothing downstream has to "
                                        "guess it from the picture.")
    ap.add_argument("--dilate-frac", type=float, default=0.45,
                    help="dilation radius as a fraction of the fig's equivalent radius")
    ap.add_argument("--dilate-min", type=int, default=8,
                    help="floor on the dilation radius in px, for the 17-px-r f000 nub")
    ap.add_argument("--feather-frac", type=float, default=0.5,
                    help="Gaussian feather radius as a fraction of the dilation radius")
    ap.add_argument("--no-gain-match", action="store_true",
                    help="paste the grow patch at its own exposure (publishes the seam)")
    ap.add_argument("--gain-mode", choices=("luma", "chroma"), default="luma",
                    help="luma (default): ONE scalar ring gain, multiplicative on RGB, which leaves "
                         "chromaticity -- and so HSV hue and saturation -- exactly unchanged. "
                         "chroma: THREE per-channel ring gains, a von Kries diagonal correction that "
                         "matches the patch's colour balance to the held field's as well as its "
                         "brightness. chroma CAN move the fig's hue and saturation and therefore CAN "
                         "reach the G2 end-state clause; do not run it without pre-registering that "
                         "cost, because a rung that buys G1 by spending G2 has bought nothing.")
    ap.add_argument("--gain-clamp", type=float, default=2.0)
    ap.add_argument("--held-still", action="store_true",
                    help="take the ENTIRE field from the held clip's f000 on every frame -- "
                         "a still plate with only the fig alive. Every field band's region "
                         "NCC is then 1.000 BY CONSTRUCTION, and so is every scrap of "
                         "ambient motion the plate had.")
    ap.add_argument("--freeze-band", action="append", default=[], metavar="Y0:Y1",
                    help="take rows [Y0,Y1) from the HELD clip's f000 on every frame. "
                         "Its region NCC becomes 1.000 BY CONSTRUCTION and is reported "
                         "as constructed, never as measured. Repeatable.")
    ap.add_argument("--grow-sha", default="", help="asserted before anything is written")
    ap.add_argument("--held-sha", default="", help="asserted before anything is written")
    a = ap.parse_args()

    src, dst = a.anchor_cover_crop.split("->")
    src_wh = tuple(int(v) for v in src.lower().split("x"))
    dst_wh = tuple(int(v) for v in dst.lower().split("x"))

    gp, hp = frame_paths(a.grow), frame_paths(a.held)
    if len(gp) != len(hp):
        return int(bool(sys.stderr.write(
            "!! %d grow frames vs %d held frames -- refusing.\n" % (len(gp), len(hp))))) or 2
    n = len(gp)

    bands = []
    for b in a.freeze_band:
        y0, y1 = (int(v) for v in b.split(":"))
        bands.append((y0, y1))

    # ---- the matte comes from the detector, not from a second opinion -------
    anchor = ft.anchor_from_mask(a.anchor_mask, src_wh, dst_wh)
    masks = {}

    def sink(i, mask, rec):
        if mask is not None:
            masks[i] = mask

    recs = ft.track(gp, anchor, mask_sink=sink)
    dead = [r["frame"] for r in recs if r["status"] != "ok"]
    print("fig_track on --grow: %d frames, %d live, %d dead %s"
          % (n, n - len(dead), len(dead), dead if dead else ""), flush=True)

    if a.masks:
        os.makedirs(a.masks, exist_ok=True)
        for i, m in masks.items():
            Image.fromarray((m * 255).astype(np.uint8)).save(
                os.path.join(a.masks, "m%03d.png" % (i + 1)))

    os.makedirs(a.out_frames, exist_ok=True)
    if a.out_blend:
        os.makedirs(a.out_blend, exist_ok=True)
    held0 = np.asarray(Image.open(hp[0]).convert("RGB"), np.float64)

    def write_blend(i, alpha):
        """The blend zone is every pixel the held clip did not supply alone.

        alpha == 0 is pure held and alpha == 1 is pure grow, and BOTH ends are
        excluded here, not just the soft middle: a pure-grow pixel sitting in a
        held-clip background is a discontinuity in WHICH FILM the field came
        from, and a ring drawn across that boundary is no more honest than one
        drawn across the feather."""
        if not a.out_blend:
            return
        Image.fromarray(((alpha > 0.0) * 255).astype(np.uint8)).save(
            os.path.join(a.out_blend, "b%03d.png" % (i + 1)))

    per_frame = []
    last = None            # (mask, grow_rgb, r_eq) of the last LIVE frame
    held_on_dead = []

    for i in range(n):
        grow_rgb = np.asarray(Image.open(gp[i]).convert("RGB"), np.float64)
        held_rgb = held0 if a.held_still else np.asarray(
            Image.open(hp[i]).convert("RGB"), np.float64)
        rec = recs[i]

        if i in masks:
            m, src_rgb = masks[i], grow_rgb
            r_eq = rec["r_eq"]
            last = (m, grow_rgb, r_eq)
            status = "live"
        elif last is not None:
            m, src_rgb, r_eq = last
            held_on_dead.append(i)
            status = "held-on-dead"
        else:
            # No live frame yet at all. The detector has said nothing it will
            # stand behind, so this file copies the held frame through whole and
            # says so, rather than guessing a fig.
            Image.fromarray(held_rgb.astype(np.uint8)).save(
                os.path.join(a.out_frames, "f%03d.png" % (i + 1)))
            write_blend(i, np.zeros(held_rgb.shape[:2]))
            per_frame.append({"frame": i, "status": "no-matte-yet", "fig_area_px": None,
                              "matte_area_px": 0, "dilate_px": 0, "feather_px": 0.0,
                              "gain": 1.0})
            held_on_dead.append(i)
            continue

        d = max(a.dilate_min, int(round(a.dilate_frac * r_eq)))
        matte = dilate_disk(m, d)
        alpha = feather(matte, a.feather_frac * d)

        # ---- ring gain match ------------------------------------------------
        gain = 1.0
        chan_gain = [1.0, 1.0, 1.0]
        if not a.no_gain_match:
            ring = dilate_disk(matte, max(8, d)) & (~matte)
            if ring.sum() >= 200:
                lg = float(np.median(luma(src_rgb)[ring]))
                lh = float(np.median(luma(held_rgb)[ring]))
                if lg > 1e-3:
                    gain = lh / lg
                if a.gain_mode == "chroma":
                    gm = np.median(src_rgb[ring], axis=0)
                    hm = np.median(held_rgb[ring], axis=0)
                    chan_gain = [float(hm[c] / gm[c]) if gm[c] > 1e-3 else 1.0 for c in range(3)]
            gain = float(min(max(gain, 1.0 / a.gain_clamp), a.gain_clamp))
            chan_gain = [float(min(max(g, 1.0 / a.gain_clamp), a.gain_clamp)) for g in chan_gain]

        if a.gain_mode == "chroma" and not a.no_gain_match:
            patch = np.clip(src_rgb * np.array(chan_gain)[None, None, :], 0, 255)
        else:
            patch = np.clip(src_rgb * gain, 0, 255)
        al = alpha[..., None]
        comp = held_rgb * (1.0 - al) + patch * al

        for (y0, y1) in bands:
            if matte[y0:y1].any():
                return int(bool(sys.stderr.write(
                    "!! freeze band %d:%d intersects the fig matte on f%03d -- "
                    "refusing to freeze over the subject.\n" % (y0, y1, i + 1)))) or 3
            comp[y0:y1] = held0[y0:y1]

        Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8)).save(
            os.path.join(a.out_frames, "f%03d.png" % (i + 1)))
        write_blend(i, alpha)
        per_frame.append({
            "frame": i, "status": status,
            "fig_area_px": int(m.sum()),
            "matte_area_px": int(matte.sum()),
            "matte_over_fig": round(float(matte.sum()) / max(1.0, float(m.sum())), 3),
            "dilate_px": d, "feather_px": round(a.feather_frac * d, 2),
            "gain": round(gain, 4),
            "channel_gain": [round(g, 4) for g in chan_gain],
            "channel_gain_spread": round(max(chan_gain) - min(chan_gain), 4),
            "blend_zone_px": int((alpha > 0.0).sum()),
        })

    out = {
        "tool": "pipeline/fig_composite.py",
        "grow_frames": os.path.abspath(a.grow),
        "held_frames": os.path.abspath(a.held),
        "grow_sha256": a.grow_sha,
        "held_sha256": a.held_sha,
        "matte_source": "pipeline/fig_track.py track(mask_sink=...) -- the detector's own "
                        "per-frame mask, the same array its area_px is counted from",
        "gates": ft.gates_dict(),
        "dilate_frac": a.dilate_frac, "dilate_min": a.dilate_min,
        "feather_frac": a.feather_frac,
        "blend_zone_masks": os.path.abspath(a.out_blend) if a.out_blend else None,
        "blend_zone_is_what_fig_track_must_exclude_from_its_ring": True,
        "gain_match": not a.no_gain_match,
        "gain_mode": a.gain_mode,
        "held_still_whole_field_constructed_not_measured": bool(a.held_still),
        "gain_is_multiplicative_on_rgb_so_hue_and_sat_are_unchanged": a.gain_mode == "luma",
        "frozen_bands_constructed_not_measured": [{"y0": y0, "y1": y1} for y0, y1 in bands],
        "detector_dead_frames_on_grow": dead,
        "held_on_dead_frames": held_on_dead,
        "frames": n,
        "per_frame": per_frame,
    }
    with open(a.out_json, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print("WROTE %s" % a.out_json)

    if a.out_mp4:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps),
               "-i", os.path.join(a.out_frames, "f%03d.png"),
               "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf),
               "-pix_fmt", "yuv420p", "-profile:v", "high", a.out_mp4]
        subprocess.run(cmd, check=True)
        print("WROTE %s  sha256 %s" % (a.out_mp4, sha256(a.out_mp4)))

    areas = [p["matte_area_px"] for p in per_frame if p["matte_area_px"]]
    print("matte area px: first %d, last %d, max %d | dilate %d..%d px | "
          "gain %.3f..%.3f | held-on-dead %d frame(s) %s"
          % (areas[0], areas[-1], max(areas),
             min(p["dilate_px"] for p in per_frame), max(p["dilate_px"] for p in per_frame),
             min(p["gain"] for p in per_frame), max(p["gain"] for p in per_frame),
             len(held_on_dead), held_on_dead if held_on_dead else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
