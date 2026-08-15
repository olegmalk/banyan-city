#!/usr/bin/env python3
r"""Paint ONE object into ONE masked region of an approved plate. SDXL, $0, local.

WHY THIS EXISTS. Beat 01 asks for "one small round green fruit hanging from the
stem" and the prompt cannot deliver it: 0 of 24 across the wording rounds, and
0 of 12 in round 8's img2img -- which is the decisive one, because r8's init
carried no fruit at all and so was a clean test of whether img2img will ADD an
object the init lacks. It will not, at strength 0.35 or 0.55. The founder chose
`inpaint` over `drop` on 2026-08-10 (ledger `ep2-b01-fig-route-0810`), so the
fruit becomes its own step and this is that step.

THE METHOD, AND EVERY CHOICE IN IT IS SOURCED RATHER THAN INVENTED.

  * animagine-xl-3.1 has NO inpainting variant, so this loads the BASE weights
    into StableDiffusionXLInpaintPipeline. diffusers 0.29.2 supports that
    explicitly -- its own check is "The unet should have either 4 or 9 input
    channels", and at 4 (a normal SDXL checkpoint) it takes the latent-blend
    branch instead of concatenating mask channels:
        latents = (1 - init_mask) * init_latents_proper + init_mask * latents
    HF's docs name the trade-off in their own words: "the overall image quality
    may be lower, but it generally tends to preserve the mask area (that is why
    you can see the mask outline)". Preserving the unmasked area is exactly what
    we want here -- the plate is the founder's and must come back unchanged
    outside the mask.
  * `padding_mask_crop` is the countermeasure for the failure mode this beat has:
    a SMALL object in a LARGE frame. It crops the masked region with padding,
    upscales that crop to the pipeline resolution, inpaints there, and pastes it
    back -- so the fruit is drawn at full model resolution instead of at the ~5%
    of the frame it will occupy. Verified present in 0.29.2's __call__ on the box.
  * `strength` must be high to ADD something. It is not the img2img case; the
    unmasked region is restored every step by the blend above, so a high strength
    costs nothing outside the mask.

    diffusers 0.29.2 source: https://raw.githubusercontent.com/huggingface/diffusers/v0.29.2/src/diffusers/pipelines/stable_diffusion_xl/pipeline_stable_diffusion_xl_inpaint.py
    inpaint docs:            https://huggingface.co/docs/diffusers/v0.29.2/en/using-diffusers/inpaint
    model card + licence:    https://huggingface.co/cagliostrolab/animagine-xl-3.1
    padding_mask_crop issue: https://github.com/huggingface/diffusers/issues/6345

WHAT THIS SCRIPT REFUSES TO DO. It will not run on an init whose sha256 does not
match the one named on the command line. G1 says a conditioned render starts from
a frame the founder has passed, and the only way that gate means anything is if
the bytes are asserted rather than the filename. It also never writes a canon
filename and always writes `approved: false` in the sidecar.

THE MASK IS GEOMETRY AND IT IS THE STEWARD'S, NOT HIS. He approved a method, not
a size or a position. The ellipse is passed in on the command line, drawn to a
PNG beside the output so it can be looked at, and reported in the sidecar in both
pixels and as a fraction of the frame, so the first correction he makes can be
"lower", "smaller", "other side" and it is one number.

SECOND CALLER, 2026-08-15: THE BARK BOARD, AND WHY THE MASK GREW STRAIGHT EDGES.
A prop -- a clipboard made of bark -- gates three beats of 002b (06 "turns over a
clipboard made of bark and reads", 08 "lowers the clipboard and points", 10
"flips the clipboard around: the back is blank"). Four wording attempts closed
the wording lever for good (see `a5e61487`, `c7a11ff0`): they established that
wording reaches the prop's MATERIAL -- deleting the noun killed the chrome clip
and white paper in 12 frames of 12 -- and that wording does NOT reach its
GEOMETRY. `large flat rectangular` was in the positive of a clean, uncontested
prompt and all four seeds still rounded the object into a lozenge, a dome, a
surfboard blank and a basket lid. So the geometry has to come from the mask, and
an ELLIPSE MASK CANNOT SUPPLY IT: an ellipse is the rounded blob that four
prompts already failed against, and masking a board with one would re-draw the
defect under test. Hence `--quad`, four corners and four straight edges. A
rectangle is a quad; a rectangular board held at an angle is a quad in
perspective, which an axis-aligned rectangle would not fit either.

    python inpaint_fruit.py --init PLATE.png --init-sha256 <hex> \
        (--ellipse cx,cy,rx,ry | --quad x0,y0,x1,y1,x2,y2,x3,y3) \
        --prompt-file p.txt --negative-file n.txt \
        --out OUT.png [--steps 40] [--cfg 7.5] [--strength 0.99] \
        [--seed N] [--pad-crop 64] [--blur 8] [--dry-run]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import os
import sys
import time

BASE = "cagliostrolab/animagine-xl-3.1"
BASE_LICENCE = "CreativeML Open RAIL++-M (use restrictions travel; D15)"


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read().strip()


def yaml_block(text: str, indent: str = "  ") -> str:
    return "\n".join(indent + line for line in text.splitlines())


def module_version(name: str) -> str:
    try:
        return __import__(name).__version__
    except Exception:
        return "unresolved"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--init", required=True)
    ap.add_argument("--init-sha256", required=True,
                    help="asserted before anything loads; a mismatch is a hard stop")
    ap.add_argument("--ellipse", default="",
                    help="cx,cy,rx,ry in pixels of the init image")
    ap.add_argument("--quad", default="",
                    help="x0,y0,x1,y1,x2,y2,x3,y3 -- four corners in order, a "
                         "STRAIGHT-EDGED mask. A rectangle is a quad, and a "
                         "rectangular board seen at an angle is a quad and is NOT "
                         "an ellipse. Exactly one of --ellipse/--quad is required.")
    ap.add_argument("--dry-run", action="store_true",
                    help="assert the sha, draw the mask PNG beside --out and stop "
                         "BEFORE loading any model. Costs nothing and is the step "
                         "where a misplaced mask gets caught by eye.")
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--negative-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--cfg", type=float, default=7.5)
    ap.add_argument("--strength", type=float, default=0.99)
    ap.add_argument("--seed", type=int, default=20260810)
    ap.add_argument("--pad-crop", type=int, default=64,
                    help="padding_mask_crop; 0 disables it")
    ap.add_argument("--blur", type=int, default=8, help="mask blur_factor")
    ap.add_argument("--note", default="")
    a = ap.parse_args()

    if not os.path.isfile(a.init):
        print("!! init not found: %s" % a.init, flush=True)
        return 2
    have = sha256_of(a.init)
    if have != a.init_sha256:
        print("!! INIT SHA MISMATCH -- refusing.\n   want %s\n   have %s"
              % (a.init_sha256, have), flush=True)
        return 3

    if bool(a.ellipse) == bool(a.quad):
        print("!! pass exactly one of --ellipse or --quad", flush=True)
        return 2

    cx = cy = rx = ry = 0
    corners: list = []
    if a.ellipse:
        try:
            cx, cy, rx, ry = (int(v) for v in a.ellipse.split(","))
        except Exception:
            print("!! --ellipse wants cx,cy,rx,ry", flush=True)
            return 2
        shape = "ellipse"
        bbox = [cx - rx, cy - ry, cx + rx, cy + ry]
    else:
        try:
            vals = [int(v) for v in a.quad.split(",")]
        except Exception:
            vals = []
        if len(vals) != 8:
            print("!! --quad wants x0,y0,x1,y1,x2,y2,x3,y3 (8 integers)", flush=True)
            return 2
        corners = list(zip(vals[0::2], vals[1::2]))
        xs = [p[0] for p in corners]
        ys = [p[1] for p in corners]
        shape = "quad"
        bbox = [min(xs), min(ys), max(xs), max(ys)]

    from PIL import Image, ImageDraw

    plate = Image.open(a.init).convert("RGB")
    W, H = plate.size
    mask = Image.new("L", (W, H), 0)
    if shape == "ellipse":
        ImageDraw.Draw(mask).ellipse(bbox, fill=255)
    else:
        ImageDraw.Draw(mask).polygon(corners, fill=255)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    mask_png = os.path.splitext(a.out)[0] + "-mask.png"
    mask.save(mask_png)

    prompt = read_text(a.prompt_file)
    negative = read_text(a.negative_file)

    if a.dry_run:
        print("DRY RUN -- no model loaded, nothing rendered.", flush=True)
        print("init_sha256 OK %s" % have, flush=True)
        print("mask %s corners=%s bbox=%s  %.4f x %.4f of %dx%d"
              % (shape, corners or "-", bbox,
                 (bbox[2] - bbox[0]) / float(W),
                 (bbox[3] - bbox[1]) / float(H), W, H), flush=True)
        print("WROTE %s" % mask_png, flush=True)
        print("rc=0 dry_run=1", flush=True)
        return 0

    import torch
    from diffusers import StableDiffusionXLInpaintPipeline

    if not torch.cuda.is_available():
        print("!! no CUDA. This is the box's job; stopping.", flush=True)
        return 4

    t0 = time.time()
    pipe = StableDiffusionXLInpaintPipeline.from_pretrained(
        BASE, torch_dtype=torch.bfloat16, use_safetensors=True)
    pipe = pipe.to("cuda")
    pipe.set_progress_bar_config(disable=True)
    in_ch = int(pipe.unet.config.in_channels)
    print("MODEL_LOADED %s cuda/bfloat16 unet.in_channels=%d in %.0fs"
          % (BASE, in_ch, time.time() - t0), flush=True)
    if in_ch not in (4, 9):
        print("!! unexpected unet.in_channels=%d" % in_ch, flush=True)
        return 5

    blurred = pipe.mask_processor.blur(mask, blur_factor=a.blur) if a.blur else mask

    kwargs = dict(prompt=prompt, negative_prompt=negative, image=plate,
                  mask_image=blurred, width=W, height=H,
                  num_inference_steps=a.steps, guidance_scale=a.cfg,
                  strength=a.strength,
                  generator=torch.Generator("cuda").manual_seed(a.seed))
    if a.pad_crop:
        kwargs["padding_mask_crop"] = a.pad_crop

    t1 = time.time()
    out = pipe(**kwargs).images[0]
    render_s = time.time() - t1

    out.save(a.out)

    versions = {"python": sys.version.split()[0], "torch": module_version("torch"),
                "diffusers": module_version("diffusers")}
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    mask_lines = ["mask_shape: %s" % shape]
    if shape == "ellipse":
        mask_lines += ["mask_centre_px: [%d, %d]" % (cx, cy),
                       "mask_radii_px: [%d, %d]" % (rx, ry)]
    else:
        mask_lines += ["mask_corners_px: %s"
                       % str([[int(x), int(y)] for x, y in corners])]
    mask_lines += [
        "mask_bbox_px: [%d, %d, %d, %d]" % tuple(bbox),
        "mask_width_frac: %.4f" % ((bbox[2] - bbox[0]) / float(W)),
        "mask_height_frac: %.4f" % ((bbox[3] - bbox[1]) / float(H)),
    ]
    sidecar = a.out + ".meta.yaml"
    with open(sidecar, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join([
            "# Still provenance (7.2), written AT RENDER TIME by inpaint_fruit.py",
            "# on the rtx5090. The plate outside the mask is the founder's own",
            "# pixels; only the region described below was redrawn.",
            "platform: local-gpu (rtx5090)",
            "model: %s" % BASE,
            "model_licence: %s" % BASE_LICENCE,
            "pipeline: StableDiffusionXLInpaintPipeline (base weights, unet.in_channels=%d)" % in_ch,
            "size: %dx%d" % (W, H),
            "steps: %d" % a.steps,
            "guidance: %s" % a.cfg,
            "strength: %s" % a.strength,
            "seed: %d" % a.seed,
            "padding_mask_crop: %s" % (a.pad_crop or "null"),
            "mask_blur_factor: %d" % a.blur,
            "init_image: %s" % a.init.replace("\\", "/"),
            "init_sha256: %s" % have,
            "mask_png: %s" % os.path.basename(mask_png),
        ] + mask_lines + [
            "mask_is_the_stewards: >-",
            yaml_block("THE FOUNDER APPROVED A METHOD, NOT THIS GEOMETRY. He said "
                       "`inpaint` and named no size, no position, no colour and no "
                       "shape. The mask above is the steward's and is the first "
                       "thing his correction should move -- 'lower', 'smaller', "
                       "'other side' is one number here; the words in the prompt "
                       "are his own approved shots.md wording."),
            "rendered_utc: %s" % stamp,
            "render_seconds: %.1f" % render_s,
            "wall_seconds: %.1f" % (time.time() - t0),
            "cost_usd: 0",
            "python_version: %s" % versions["python"],
            "torch_version: %s" % versions["torch"],
            "diffusers_version: %s" % versions["diffusers"],
            "approved: false",
            "provisional: >-",
            yaml_block("PROVISIONAL. A steward-rendered SAMPLE, not a pick and not "
                       "canon. Never takes a canon filename, is not published, not "
                       "posted, and not assembled into an episode. Ground truth is "
                       "the founder (R4)."),
            "note: >-",
            yaml_block(a.note or "one inpainted sample; the fruit question."),
            "prompt: |-",
            yaml_block(prompt),
            "negative: |-",
            yaml_block(negative),
            "",
        ]))

    print("WROTE %s" % a.out, flush=True)
    print("WROTE %s" % mask_png, flush=True)
    print("WROTE %s" % sidecar, flush=True)
    print("rc=0 render_s=%.1f" % render_s, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
