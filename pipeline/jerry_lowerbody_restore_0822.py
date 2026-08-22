#!/usr/bin/env python3
r"""Give the founder's own pixels back, byte for byte, above the cut.

WHY THIS STEP EXISTS AND WHY IT IS NOT OPTIONAL.

`ep2-b13-lowerbody-0822` protects his head by keeping it OUTSIDE an inpaint
mask, and diffusers' latent blend does hold it -- the composition came back
unchanged at strength 0.95, mean |delta| 1.425. But it is NOT byte-exact, and
the reason is mechanical rather than a leak: diffusers only re-pastes the
original in PIXEL space inside its `padding_mask_crop` branch
(`self.image_processor.apply_overlay(...)`), and this route runs `--pad-crop 0`
on purpose, because section 28 of `b08-arm-route-0819.md` measured that
padding_mask_crop rescales the ControlNet hint along with the init and turns the
conditioning into a different instruction. With the flag off there is no
overlay, so the protected region survives as LATENTS and takes one VAE round
trip. Measured on the round-one frame: 93.9% of pixels above the cut moved by at
least one level, and the head box reads maxdiff 98 on ink edges -- the VAE's
usual damage, worst exactly where his eye and his linework are.

For a plate that would be a rounding error. For a LoRA TRAINING FRAME it is the
whole point of the route: the claim is "a frame whose head is byte-identical to
the founder's ratified canon", and a VAE-softened eye is how four eye vetoes
happened in the first place. So the claim is made true rather than approximated,
in numpy, at $0.

WHAT IT DOES. Rows 0..CUT-FEATHER come straight from the init, byte for byte.
Rows below the cut come straight from the render. Between them is a short linear
crossfade, because the two halves can disagree on colour by a level or two and a
hard edge across a shirt would read as a step. The feather is REPORTED as the
only band that is neither, so nothing is asserted that is not true.

    python3 pipeline/jerry_lowerbody_restore_0822.py \
        --init  farm-out/jerry-lowerbody-src-0822/jerry-seat-init-0822.png \
        --render <the landed png> --out <the training frame> [--cut 900]

$0. No model, no network, no GPU.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

import numpy as np
from PIL import Image


def sha256_of(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def restore(init_png, render_png, out_png, cut=900, feather=16):
    a = Image.open(init_png).convert("RGB")
    b = Image.open(render_png).convert("RGB")
    if a.size != b.size:
        raise SystemExit("!! init is %dx%d and the render is %dx%d -- refusing."
                         % (a.size + b.size))
    A, B = np.asarray(a).astype(np.float32), np.asarray(b).astype(np.float32)
    H = A.shape[0]
    top = cut - feather
    if top <= 0 or cut >= H:
        raise SystemExit("!! cut %d / feather %d does not fit a %d-row frame."
                         % (cut, feather, H))

    w = np.zeros((H, 1, 1), dtype=np.float32)          # 1 = take the RENDER
    w[cut:] = 1.0
    w[top:cut, 0, 0] = np.linspace(0.0, 1.0, feather, endpoint=False)
    out = A * (1 - w) + B * w
    out = np.clip(out + 0.5, 0, 255).astype(np.uint8)

    # THE BAND ABOVE THE FEATHER MUST BE THE INIT, BYTE FOR BYTE. Asserted here
    # rather than claimed in a note: rounding, dtype or an off-by-one in the
    # ramp would each break it silently.
    if not np.array_equal(out[:top], np.asarray(a)[:top]):
        raise SystemExit("!! rows 0..%d are not byte-identical to the init "
                         "after the paste -- refusing to write." % (top - 1))
    Image.fromarray(out).save(out_png)

    d = np.abs(np.asarray(a).astype(int) - np.asarray(b).astype(int))
    return {
        "rows_0_to_%d_from_init_byte_exact" % (top - 1): True,
        "feather_rows": "%d..%d (%d rows, neither half)" % (top, cut - 1, feather),
        "rows_%d_up_from_render" % cut: True,
        "vae_drift_removed_mean_abs": round(float(d[:top].mean()), 4),
        "vae_drift_removed_maxdiff": int(d[:top].max()),
        "vae_drift_removed_px": int((d[:top].sum(-1) > 0).sum()),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--init", required=True)
    ap.add_argument("--render", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cut", type=int, default=900,
                    help="the mask's own CUT_Y from author_jerry_lowerbody_0822")
    ap.add_argument("--feather", type=int, default=16)
    a = ap.parse_args()
    rep = restore(a.init, a.render, a.out, a.cut, a.feather)
    for k, v in rep.items():
        print("  %-42s %s" % (k, v))
    print("WROTE %s sha %s" % (a.out, sha256_of(a.out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
