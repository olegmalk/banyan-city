#!/usr/bin/env python3
r"""Beat 09: buy the FRAMING with a crop instead of with words. $0, no GPU.

    python3 pipeline/beat09_plate_crop.py --all

WHY THIS EXISTS, AND IT IS THE RUNG THE LADDER NAMED RATHER THAN A NEW IDEA.
`pipeline/work-ladder-0819.md` closed beat 09's wording ladder by measurement --
eight renders, two wordings, the unwanted colour negated throughout -- and wrote
the replacement instrument out in one sentence:

    "beat 09's plate is a REFERENCE-PLUS-CROP job: condition on the refs to get
     the hair, then recover the framing with a crop pass rather than with words.
     That is a build, it is named and not fired."

This is the second half of that sentence. The first half already ran: the box
IP-Adapter rung (`pipeline/jobs/ep2-b09-cast-0817.yaml`, 12 frames on
`origin/farm-results-rtx5090`) won the hair at 3 of 12 and paid for it in
framing at 0 of 12, its own pre-registered fail mode firing because the refs
depict two men at full length in a field. So the pixels that have the hair
already exist and are simply too far away.

THE TWO CLAUSES HAVE CO-OCCURRED ONCE AND NOBODY HAD NOTICED. The ladder's
sharpest statement about this beat is that they never do:

    "seed 20260817 has the eyes and a 48% head; seed 20260820 has a 56% head and
     shut eyes. So the plate beat 09 ships off is a render-N-and-pick..."

That is true of the MAC rung. It is not true of the corpus. `09-the-pause-ipa-
r1-w015-s3.png` carries, in ONE frame: near-black cropped hair (recorded as a c1
pass in review/ep2-picks/cast-0817-scores.yaml), unmistakable round wire-rim
glasses, BOTH EYES OPEN with visible irises, and a real grass field behind him.
Four of beat 09's conditions in one picture. Its ONLY failure is the head at
~25% of frame height against a 55% bar -- which is the one condition that is not
a property of the sampler at all. Nobody looked because the frame was scored 0
of 12 on framing and filed under a rung that failed.

WHAT THE SAMPLE ACTUALLY TESTS, because a crop is arithmetic and needs no proof.
The question is not "can you crop", it is WHETHER THE RESULT IS STILL A PLATE.
Reaching 55% from 25% is a 2.16x LANCZOS upscale of a 386x564 region, and this
house's dialect is hard cel line. So the crop is measured against a NATIVE
close-up of the same beat at the same head size -- `farm-out/ep2-b09-mac-plate-
0819/09-the-pause-mac-plate-r3s1.png`, 56% head, drawn at full resolution -- with
the same highpass instrument on both. If the cropped face carries comparable
high-frequency energy the instrument is real and beat 09's framing axis is
closed for good; if it comes back soft, the answer is that reference-plus-crop
does not reach this beat FROM A 25% HEAD, and the rung becomes a re-run of the
IP-Adapter arm at a tighter shot with the crop applied to a 35-40% head instead.
EITHER OUTCOME IS THE RUNG'S ANSWER. Both are written here before it runs.

THE COMPOSITION IS COPIED FROM THE CONTROL, NOT INVENTED. macr3s1 -- the frame
whose framing the bar accepts -- puts the chin at y~690 of 1216, i.e. 0.567 of
frame height, with the crown cropped at the top edge. So the crop places the
chin at 0.57 and the head top at 0.57-0.55 = 0.02, which reproduces that
composition rather than centring the head in the box, which would read as a
passport photo.

MEASURED, NOT EYEBALLED, AND SAYING SO MATTERS ON THIS BEAT. Beat 09 has already
had one eyeballed hue claim retracted (work-ladder-0819.md, the `dark`->`black`
mechanism). Head extents here were read off a 10-px-ruled zoom of each source
and are recorded as data below with the file they were read from; the hair luma
is measured with the ladder's own two masks so the numbers are comparable to the
eight it already published.

NO PICK, NO plate_ack, NO PROMOTION. A crop is a fixture like any other plate,
and beat 09's adult-read fault is an OPEN R4 CARD (/review/ep2-guards-0818).
Nothing here touches it and nothing here closes the slate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "farm-out" / "ep2-b09-platecrop-0820"

# Head extents in SOURCE pixels, read off a 10-px-ruled zoom of each frame
# (the ruler render is reproducible: crop, scale, draw a line every 10 rows).
# `face` is the box the sharpness instrument is measured over -- skin and the
# glasses, deliberately excluding hair, whose texture is a different frequency.
SOURCES = {
    "r1s3": {
        "png": "farm-out/ep2-b09-cast-0817/09-the-pause-ipa-r1-w015-s3.png",
        "branch": "origin/farm-results-rtx5090",
        "head_top": 20, "head_chin": 330, "head_cx": 416,
        "face": (300, 170, 530, 330),
        "why": ("the one frame in the corpus with hair, wire-rims and BOTH EYES "
                "OPEN at once; fails only on framing at ~25%"),
    },
    "r2s2": {
        "png": "farm-out/ep2-b09-cast-0817/09-the-pause-ipa-r2-w015-s2.png",
        "branch": "origin/farm-results-rtx5090",
        "head_top": 30, "head_chin": 490, "head_cx": 330,
        "face": (170, 300, 430, 490),
        "why": ("the largest head of the three c1 passes (~38%), so it needs "
                "only 1.45x -- the easy end of the same instrument"),
    },
}
# The native close-up this beat's bar already accepts on framing. Not cropped,
# not upscaled: the control the instrument is calibrated against.
CONTROL = {
    "name": "macr3s1",
    "png": "farm-out/ep2-b09-mac-plate-0819/09-the-pause-mac-plate-r3s1.png",
    "head_top": 0, "head_chin": 690,     # crown cropped by the frame edge
    "face": (250, 380, 640, 690),
}
TARGET_HEAD_FRAC = 0.55                  # the bar
CHIN_AT = 0.57                           # copied from the control's composition


def highpass_std(im: Image.Image, box) -> float:
    """High-frequency energy over a box: std of (grey - gaussian sigma 1).

    Sigma 1 rather than the composite lane's sigma 3 on purpose: sigma 3 asks
    "is there drawn structure here", which survives any upscale, and the
    question here is the opposite one -- whether the FINEST strokes survived.
    A LANCZOS upscale is precisely a low-pass, so it shows up here and not
    there.
    """
    g = im.convert("L").crop(box)
    a = np.asarray(g, dtype=np.float64)
    b = np.asarray(g.filter(ImageFilter.GaussianBlur(1.0)), dtype=np.float64)
    return float((a - b).std())


def hair_luma(im: Image.Image) -> dict:
    """The ladder's own two hair masks, so these numbers join its table.

    (1) central band of the top 30% of frame, darker half of its pixels;
    (2) warm-pixel mask R>=G>=B with luma < 120.
    """
    a = np.asarray(im.convert("RGB"), dtype=np.float64)
    h, w, _ = a.shape
    band = a[: int(h * 0.30), int(w * 0.25): int(w * 0.75)]
    lum = band @ np.array([0.299, 0.587, 0.114])
    dark = lum <= np.median(lum)
    r, g, b = band[..., 0], band[..., 1], band[..., 2]
    warm = (r >= g) & (g >= b) & (lum < 120)
    return {
        "central_band_darker_half_mean_luma": round(float(lum[dark].mean()), 1),
        "central_band_share_under_luma_60_pct": round(float((lum < 60).mean() * 100), 1),
        "warm_mask_mean_luma": round(float(lum[warm].mean()), 1) if warm.any() else None,
        "warm_mask_p25_luma": round(float(np.percentile(lum[warm], 25)), 1) if warm.any() else None,
    }


def crop_to_bar(im: Image.Image, top: int, chin: int, cx: int):
    """Return (cropped-and-rescaled image, provenance dict).

    Fails LOUD rather than silently sliding the box back inside the frame: a
    clamped crop is a different composition from the one the numbers describe,
    and this beat has already lost a day to a test that quietly did not test
    what it said.
    """
    W, H = im.size
    head = chin - top
    hc = head / TARGET_HEAD_FRAC                      # crop height for the bar
    wc = hc * (W / H)                                 # keep the source aspect
    y0 = top - (CHIN_AT - TARGET_HEAD_FRAC) * hc      # head top at 0.02 of the box
    x0 = cx - wc / 2.0
    box = [int(round(x0)), int(round(y0)),
           int(round(x0 + wc)), int(round(y0 + hc))]
    over = {"left": max(0, -box[0]), "top": max(0, -box[1]),
            "right": max(0, box[2] - W), "bottom": max(0, box[3] - H)}
    if any(over.values()):
        raise SystemExit(
            "!! the crop box leaves the frame by %s px. The instrument cannot\n"
            "   invent pixels and will not slide the box to hide it: this frame\n"
            "   does not contain a %d%% head at this composition." % (over, TARGET_HEAD_FRAC * 100))
    return im.crop(box).resize((W, H), Image.LANCZOS), {
        "crop_box_xyxy": box,
        "crop_size": [box[2] - box[0], box[3] - box[1]],
        "upscale_factor": round(H / hc, 3),
        "head_px_source": head,
        "head_frac_source": round(head / H, 4),
        "head_frac_after": TARGET_HEAD_FRAC,
        "chin_at_frac_after": CHIN_AT,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--which", default=None, help="r1s3 | r2s2")
    a = ap.parse_args()
    names = list(SOURCES) if a.all or not a.which else [a.which]

    ctl = Image.open(REPO / CONTROL["png"]).convert("RGB")
    ctl_face = highpass_std(ctl, CONTROL["face"])
    ctl_head = (CONTROL["head_chin"] - CONTROL["head_top"]) / ctl.size[1]
    print("CONTROL %s  native close-up, head %.1f%% of frame, face highpass %.2f"
          % (CONTROL["name"], ctl_head * 100, ctl_face))

    OUT.mkdir(parents=True, exist_ok=True)
    for n in names:
        s = SOURCES[n]
        src_path = REPO / s["png"]
        if not src_path.exists():
            raise SystemExit(
                "!! %s is not in this checkout. It lives on %s -- fetch it with\n"
                "   git show %s:%s > %s"
                % (s["png"], s["branch"], s["branch"], s["png"], s["png"]))
        im = Image.open(src_path).convert("RGB")
        before = highpass_std(im, s["face"])
        out, prov = crop_to_bar(im, s["head_top"], s["head_chin"], s["head_cx"])
        # The face box travels with the crop, so the after-measurement is over
        # the SAME PIXELS at their new scale -- not over a differently framed
        # region, which would compare two things at once.
        fx0, fy0, fx1, fy1 = s["face"]
        bx0, by0, bx1, by1 = prov["crop_box_xyxy"]
        k = im.size[1] / (by1 - by0)
        after_box = (max(0, int((fx0 - bx0) * k)), max(0, int((fy0 - by0) * k)),
                     min(im.size[0], int((fx1 - bx0) * k)),
                     min(im.size[1], int((fy1 - by0) * k)))
        after = highpass_std(out, after_box)

        stem = "09-the-pause-platecrop-%s" % n
        png = OUT / (stem + ".png")
        out.save(png)
        meta = {
            "platform": "cpu (numpy/PIL crop + LANCZOS, no GPU, no sampler)",
            "model": "none -- this is a geometric operation on an existing plate",
            "cost_usd": 0.00,
            "shot_beat": 9,
            "beat_slug": "the-pause",
            "source_png": s["png"],
            "source_branch": s["branch"],
            "source_sha256": hashlib.sha256(src_path.read_bytes()).hexdigest(),
            "why_this_source": s["why"],
            "png_sha256": hashlib.sha256(png.read_bytes()).hexdigest(),
            "face_highpass_sigma1_before": round(before, 2),
            "face_highpass_sigma1_after": round(after, 2),
            "face_highpass_retained_pct": round(after / before * 100, 1),
            "control_native_closeup": CONTROL["png"],
            "control_head_frac": round(ctl_head, 4),
            "control_face_highpass_sigma1": round(ctl_face, 2),
            "vs_control_pct": round(after / ctl_face * 100, 1),
            "hair_luma_source": hair_luma(im),
            "approved": False,
            "provisional": True,
            "scored": False,
            "founder_verdict": None,
            "rung": ("REFERENCE-PLUS-CROP, the instrument work-ladder-0819.md named "
                     "and did not fire, after the wording ladder closed at 8 renders"),
            "date": date.today().isoformat(),
        }
        meta.update(prov)
        (OUT / (stem + ".yaml")).write_text(
            "\n".join("%s: %s" % (k2, json.dumps(v)) for k2, v in meta.items()) + "\n")
        print("%-6s head %.1f%% -> %.0f%%   upscale %.3fx   face highpass %.2f -> %.2f "
              "(%.0f%% kept, %.0f%% of native control)   %s"
              % (n, prov["head_frac_source"] * 100, TARGET_HEAD_FRAC * 100,
                 prov["upscale_factor"], before, after,
                 after / before * 100, after / ctl_face * 100, png.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
