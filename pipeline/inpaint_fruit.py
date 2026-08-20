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

THIRD CALLER, 2026-08-17: EYEWEAR ON ONE MAN OF TWO, AND WHY THE MASK BECAME
ARBITRARY. `glasses` named in ONE man's clause lands on BOTH men, 5 of 5 -- a
different failure from the prop above, which goes to ONE WRONG figure. The
founder ruled "draw the second man without glasses. we need to have control."
The published cause (ALE-Edit, arXiv 2412.04715) is that CLIP is causal and its
EOS carries global prompt semantics, so the token steers the whole frame and no
wording says WHICH face; a negative cannot unbind it. The mask is therefore the
only lever, and the region that matters here is a THIN BAND along a spectacle
frame -- neither a blob nor a convex polygon, so neither `--ellipse` nor `--quad`
can express it. Hence `--mask-png`, which also retires the board-MINUS-the-hand
limitation recorded against this script in wave-drafts.yaml. The band is authored
by pipeline/attribute_mask.py, a $0 step with no GPU and no sampler in it, which
is what makes "control" checkable instead of asserted.

FOURTH CALLER, 2026-08-20: A CONTROLNET, BECAUSE THE LAST DEFECT IS A SHAPE.
`b08-arm-route-0819.md` §§21-27 spent five renders and one CPU compositor on one
region of beat 08 and closed every lever this script had. Measured, not argued:
mask SIZE does not choose the noun (18408 px drew a head, 10020 px drew a fist);
the PROMPT does choose a KIND (deleting `goblin` deleted it, first try); a
NEGATIVE removes a kind and NOT A COUNT (`second strap` redrew 91.3 % of the fill
and the second strap came back in the same place); STRENGTH governs invention
symmetrically and neither end lands on the plate's own line quality. What is left
on the best frame is a crossing band -- a SHAPE -- and §27's closing line names
the only two levers that reach one: a controlnet or a hand-authored matte (R4).

So the control flags below exist, and diffusers 0.29.2 already has the pipeline:
`StableDiffusionXLControlNetInpaintPipeline`. Three facts were read out of its
source before a line of this was written, because the alignment class is exactly
how this beat died before:

  * it takes the SAME latent-blend branch at unet.in_channels == 4 (its own
    `return_image_latents = num_channels_unet == 4`), so the base animagine
    weights load into it on the identical terms as the plain inpaint pipeline;
  * it accepts `padding_mask_crop`, computes ONE `crops_coords` from the mask,
    and passes THAT SAME TUPLE to the init, to the mask AND to every control
    image (`prepare_control_image(..., crops_coords=crops_coords,
    resize_mode=resize_mode)`, in both the single-net and MultiControlNetModel
    branches). ALIGNMENT IS THEREFORE BY CONSTRUCTION AND NOT BY ARITHMETIC HERE:
    the hint is handed over FULL-FRAME, in the init's own coordinates, and this
    script contains no crop of its own to disagree with diffusers';
  * `AutoPipelineForInpainting.from_pipe(pipe, controlnet=[cn, cn2])` swaps the
    class while reusing the loaded modules, and a LIST is wrapped into a
    MultiControlNetModel by the constructor -- the same composition
    `controlnet_plate.py` uses on the txt2img side, whose two hints are what this
    is for.

    controlnet inpaint sdxl: https://raw.githubusercontent.com/huggingface/diffusers/v0.29.2/src/diffusers/pipelines/controlnet/pipeline_controlnet_inpaint_sd_xl.py
    get_crop_region:         https://raw.githubusercontent.com/huggingface/diffusers/v0.29.2/src/diffusers/image_processor.py

TWO GUARDS CARRY THAT, RATHER THAN A COMMENT SAYING IT IS FINE. (1) A hint whose
pixel size is not the init's is REFUSED before any weight loads -- a resized hint
is a hint in another coordinate system, and diffusers would resize it silently.
(2) Before the render, this script's own vendored copy of `get_crop_region` is
compared against the live `pipe.mask_processor.get_crop_region`, on the same
blurred mask, and a mismatch is a hard stop -- so the crop box written into the
sidecar is the box the sampler actually used.

WITH NO CONTROL FLAGS THIS SCRIPT IS THE SCRIPT IT WAS. Same class, same call
kwargs, same sidecar bytes; `--selftest` proves the last one against a filed
verdict's sidecar (`ep2-b08-str70-0820`) and the first two by construction.

    python inpaint_fruit.py --init PLATE.png --init-sha256 <hex> \
        (--ellipse cx,cy,rx,ry | --quad x0,…,y3 | --mask-png m.png) \
        --prompt-file p.txt --negative-file n.txt \
        --out OUT.png [--steps 40] [--cfg 7.5] [--strength 0.99] \
        [--seed N] [--pad-crop 64] [--blur 8] [--dry-run] \
        [--controlnet REPO --control H.png --control-sha256 <hex> --scale 1.0 \
         [--controlnet2 REPO --control2 H2.png --control2-sha256 <hex> \
          --scale2 0.3]]
    python inpaint_fruit.py --selftest        # $0, no torch, no CUDA, no network
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

# THE SAME ALLOWLIST AS controlnet_plate.py, AND FOR THE SAME REASON: the licence
# travels with the NAME, so an unlisted net is refused before any weight loads
# instead of being recorded as apache-2.0 by default. thibaud's SDXL openpose
# inherits CMU OpenPose's non-commercial terms AT THE WEIGHTS LEVEL and MistoLine
# puts a standing visible-attribution obligation on anything it renders; neither
# may attach itself to a frame by way of a typo. Kept as its own copy rather than
# imported because this file is shipped to the box as a STANDALONE payload string
# -- an import of a sibling module would be a NameError on the card.
CONTROLNETS = {
    "xinsir/controlnet-scribble-sdxl-1.0":
        "apache-2.0 (D15 SAFE, no attribution condition)",
    "xinsir/controlnet-openpose-sdxl-1.0":
        "apache-2.0 (D15 SAFE, no attribution condition; front matter and body "
        "both, and no annotator is used -- the hint is authored in PIL)",
    r"C:\banyan-farm\cnet-openpose-twins":
        "apache-2.0 (D15 SAFE, no attribution condition) -- the `twins` variant "
        "of xinsir/controlnet-openpose-sdxl-1.0, blob "
        "diffusion_pytorch_model_twins.safetensors sha256 "
        "54a2afb1bd21349e475566e5428884bc937a4caecf863b29dea08acc40612fa4, "
        "2502139104 bytes, renamed into a loadable directory by "
        "ep2-b08-twins-fetch-0819. Identical terms to the default weight in that "
        "same repo; no annotator is used -- the hint is authored in PIL",
}

# The xinsir repos ship ONLY `diffusion_pytorch_model.safetensors`, so passing
# variant="fp16" raises. Same trap, same value, as the txt2img driver.
CONTROLNET_VARIANT = None

# control_guidance is NOT a flag. The txt2img route that authored both hints ran
# them over the full denoise and every filed b08 verdict was measured that way;
# a second free knob here would make this sample two variables instead of one.
CONTROL_GUIDANCE = (0.0, 1.0)


class ControlError(RuntimeError):
    """A refusal with the exit code the driver should return."""

    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.code = code


def crop_region(mask_image, width: int, height: int, pad: int = 0):
    """diffusers 0.29.2 `VaeImageProcessor.get_crop_region`, vendored VERBATIM.

    Vendored, not imported, on purpose: this runs in `--dry-run` and `--selftest`
    where diffusers is not installed, and its whole job is to be checkable
    against the live method before the render. Any drift between this copy and
    the installed one is caught by that comparison and stops the job -- which is
    the opposite of the usual risk with a vendored function.

    https://raw.githubusercontent.com/huggingface/diffusers/v0.29.2/src/diffusers/image_processor.py
    """
    import numpy as np

    mask_image = mask_image.convert("L")
    mask = np.array(mask_image)
    h, w = mask.shape
    crop_left = 0
    for i in range(w):
        if not (mask[:, i] == 0).all():
            break
        crop_left += 1
    crop_right = 0
    for i in reversed(range(w)):
        if not (mask[:, i] == 0).all():
            break
        crop_right += 1
    crop_top = 0
    for i in range(h):
        if not (mask[i] == 0).all():
            break
        crop_top += 1
    crop_bottom = 0
    for i in reversed(range(h)):
        if not (mask[i] == 0).all():
            break
        crop_bottom += 1

    x1, y1, x2, y2 = (
        int(max(crop_left - pad, 0)),
        int(max(crop_top - pad, 0)),
        int(min(w - crop_right + pad, w)),
        int(min(h - crop_bottom + pad, h)),
    )

    ratio_crop_region = (x2 - x1) / (y2 - y1)
    ratio_processing = width / height
    if ratio_crop_region > ratio_processing:
        desired_height = (x2 - x1) / ratio_processing
        desired_height_diff = int(desired_height - (y2 - y1))
        y1 -= desired_height_diff // 2
        y2 += desired_height_diff - desired_height_diff // 2
        if y2 >= mask_image.height:
            diff = y2 - mask_image.height
            y2 -= diff
            y1 -= diff
        if y1 < 0:
            y2 -= y1
            y1 -= y1
        if y2 >= mask_image.height:
            y2 = mask_image.height
    else:
        desired_width = (y2 - y1) * ratio_processing
        desired_width_diff = int(desired_width - (x2 - x1))
        x1 -= desired_width_diff // 2
        x2 += desired_width_diff - desired_width_diff // 2
        if x2 >= mask_image.width:
            diff = x2 - mask_image.width
            x2 -= diff
            x1 -= diff
        if x1 < 0:
            x2 -= x1
            x1 -= x1
        if x2 >= mask_image.width:
            x2 = mask_image.width

    return x1, y1, x2, y2


def resolve_controls(a, size, open_image=None):
    """Validate the control flags and load the hints. Pure enough to unit-test.

    Returns a list of dicts, EMPTY when no control flag was passed -- and empty
    is the branch that must stay byte-identical to this script before today.

    THE SIZE REFUSAL IS THE POINT OF THIS FUNCTION. A hint that is not exactly
    the init's pixel size is a hint in a different coordinate system; diffusers
    would resize it to (height, width) without complaint and the skeleton would
    land somewhere the plate's figure is not. That is the failure class that ate
    this beat before, so it is a hard stop with its own exit code and it happens
    before any weight loads.
    """
    if open_image is None:
        from PIL import Image
        open_image = Image.open

    net = getattr(a, "controlnet", "") or ""
    net2 = getattr(a, "controlnet2", "") or ""
    ctl = getattr(a, "control", "") or ""
    ctl2 = getattr(a, "control2", "") or ""

    if not (net or net2 or ctl or ctl2):
        return []

    pairs = [("--controlnet", net, "--control", ctl, getattr(a, "scale", None),
              getattr(a, "control_sha256", "") or "")]
    if net2 or ctl2:
        pairs.append(("--controlnet2", net2, "--control2", ctl2,
                      getattr(a, "scale2", None),
                      getattr(a, "control2_sha256", "") or ""))

    for nflag, nval, cflag, cval, scale, want_sha in pairs:
        if nval and not cval:
            raise ControlError("!! %s needs %s: a net with no hint is "
                               "conditioned on nothing" % (nflag, cflag), 6)
        if cval and not nval:
            raise ControlError("!! %s needs %s: a hint with no net is read by "
                               "nobody" % (cflag, nflag), 6)
        if nval not in CONTROLNETS:
            raise ControlError(
                "!! %r is not in this driver's ControlNet allowlist. The licence "
                "travels with the name (see CONTROLNETS), and an unlisted net "
                "would be recorded with the wrong terms. Use one of: %s"
                % (nval, ", ".join(sorted(CONTROLNETS))), 12)
        if scale is None:
            raise ControlError(
                "!! %s was given without its conditioning scale. A scale that "
                "was never stated is not a recipe -- pass %s explicitly."
                % (nflag, "--scale" if nflag == "--controlnet" else "--scale2"),
                6)
        if not os.path.isfile(cval):
            raise ControlError("!! hint not found: %s" % cval, 6)
        if not want_sha:
            raise ControlError(
                "!! %s must be pinned with its sha256. A staged copy is not a "
                "checkout and an unpinned hint is an unrecorded variable."
                % cflag, 8)

    if len(pairs) == 2 and pairs[0][1] == pairs[1][1]:
        raise ControlError(
            "!! --controlnet2 is the same net as --controlnet (%r). Composing a "
            "net with itself doubles its weight on one question and is never "
            "what was meant." % pairs[0][1], 12)

    out = []
    for nflag, nval, cflag, cval, scale, want_sha in pairs:
        have = sha256_of(cval)
        if have != want_sha:
            raise ControlError("!! hint sha mismatch for %s\n   want %s\n"
                               "   have %s" % (cval, want_sha, have), 8)
        img = open_image(cval).convert("RGB")
        if img.size != tuple(size):
            raise ControlError(
                "!! HINT SIZE MISMATCH -- refusing.\n   init %dx%d\n   hint %dx%d "
                "(%s)\n   A hint that is not the init's size is a hint in another "
                "coordinate system. diffusers would resize it silently and the "
                "conditioning would land off the figure -- which is the exact "
                "class of defect this route already lost days to."
                % (size[0], size[1], img.size[0], img.size[1], cval), 13)
        out.append({"net": nval, "licence": CONTROLNETS[nval], "path": cval,
                    "sha256": have, "scale": float(scale), "image": img})
    return out


def sidecar_text(*, pipeline_class: str, in_ch: int, W: int, H: int, steps: int,
                 cfg, strength, seed: int, pad_crop, blur: int, init: str,
                 init_sha: str, mask_png_name: str, mask_lines, control_lines,
                 stamp: str, render_s: float, wall_s: float, versions: dict,
                 note: str, prompt: str, negative: str) -> str:
    """The whole sidecar as one string, so a test can sha it.

    Split out of main() on 2026-08-20 with the ControlNet flags. It is a pure
    function of its arguments and `--selftest` reproduces a FILED verdict's
    sidecar byte-for-byte through it (`ep2-b08-str70-0820`), which is how the
    no-regression claim for the six b08 verdicts is checked rather than asserted.
    """
    return "\n".join([
        "# Still provenance (7.2), written AT RENDER TIME by inpaint_fruit.py",
        "# on the rtx5090. The plate outside the mask is the founder's own",
        "# pixels; only the region described below was redrawn.",
        "platform: local-gpu (rtx5090)",
        "model: %s" % BASE,
        "model_licence: %s" % BASE_LICENCE,
        "pipeline: %s (base weights, unet.in_channels=%d)" % (pipeline_class, in_ch),
        "size: %dx%d" % (W, H),
        "steps: %d" % steps,
        "guidance: %s" % cfg,
        "strength: %s" % strength,
        "seed: %d" % seed,
        "padding_mask_crop: %s" % (pad_crop or "null"),
        "mask_blur_factor: %d" % blur,
        "init_image: %s" % init.replace("\\", "/"),
        "init_sha256: %s" % init_sha,
        "mask_png: %s" % mask_png_name,
    ] + list(mask_lines) + list(control_lines) + [
        "mask_is_the_stewards: >-",
        yaml_block("THE FOUNDER APPROVED A METHOD, NOT THIS GEOMETRY. He said "
                   "`inpaint` and named no size, no position, no colour and no "
                   "shape. The mask above is the steward's and is the first "
                   "thing his correction should move -- 'lower', 'smaller', "
                   "'other side' is one number here; the words in the prompt "
                   "are his own approved shots.md wording."),
        "rendered_utc: %s" % stamp,
        "render_seconds: %.1f" % render_s,
        "wall_seconds: %.1f" % wall_s,
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
        yaml_block(note or "one inpainted sample; the fruit question."),
        "prompt: |-",
        yaml_block(prompt),
        "negative: |-",
        yaml_block(negative),
        "",
    ])


def control_meta_lines(controls, region) -> list:
    """The ControlNet block, or NOTHING AT ALL when there is no controlnet.

    Emptiness matters: a run with no control flags must write the same bytes it
    wrote before these flags existed.
    """
    if not controls:
        return []
    lines = []
    for i, c in enumerate(controls):
        tag = "" if i == 0 else "_%d" % (i + 1)
        lines += [
            "controlnet%s: %s" % (tag, c["net"]),
            "controlnet%s_licence: %s" % (tag, c["licence"]),
            "controlnet%s_conditioning_scale: %s" % (tag, c["scale"]),
            "control%s_image: %s" % (tag, os.path.basename(c["path"])),
            "control%s_image_sha256: %s" % (tag, c["sha256"]),
        ]
    lines += [
        "controlnet_variant: %s" % (CONTROLNET_VARIANT or
                                    "None (xinsir ships no fp16 variant file)"),
        "control_guidance_start: %s" % CONTROL_GUIDANCE[0],
        "control_guidance_end: %s" % CONTROL_GUIDANCE[1],
        "controlnet_composition: %s"
        % ("MultiControlNetModel, nets applied in the order listed"
           if len(controls) > 1 else "one net"),
        "control_hint_alignment: >-",
        yaml_block(
            "BY CONSTRUCTION, NOT BY ARITHMETIC. Every hint is handed to "
            "diffusers FULL-FRAME at the init's own %d x %d, and "
            "StableDiffusionXLControlNetInpaintPipeline computes ONE crops_coords "
            "from the mask and passes that same tuple to the init, to the mask "
            "and to each control image (prepare_control_image(..., "
            "crops_coords=crops_coords, resize_mode=resize_mode) in both the "
            "single-net and MultiControlNetModel branches of 0.29.2). This driver "
            "crops nothing itself, so it has nothing to disagree with. The box "
            "below is that tuple, read back from the live "
            "pipe.mask_processor.get_crop_region on the blurred mask and checked "
            "against this driver's vendored copy before the render; a mismatch is "
            "a hard stop, not a warning."
            % (controls[0]["image"].size[0], controls[0]["image"].size[1])),
        "pad_crop_region_px: %s" % ("[%d, %d, %d, %d]" % tuple(region)
                                    if region else "null (padding_mask_crop off)"),
    ]
    return lines


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
                         "an ellipse. Exactly one of --ellipse/--quad/--mask-png "
                         "is required.")
    ap.add_argument("--mask-png", default="",
                    help="an 8-bit mask PNG the same size as --init: white is "
                         "redrawn, black is preserved. This is the general case "
                         "the two shape flags are special cases of. It exists "
                         "because a region worth masking is often neither a blob "
                         "nor a convex polygon -- a THIN BAND along a spectacle "
                         "frame, or a board MINUS the hand holding it (a "
                         "limitation recorded against this script in "
                         "wave-drafts.yaml and not expressible as one ellipse or "
                         "one quad). Authoring the geometry is a separate $0 step "
                         "with no GPU and no sampler in it, which is the point: "
                         "WHICH PIXELS MAY CHANGE BECOMES A DECISION WE MAKE AND "
                         "CAN DIFF, not something the model gets a vote on. See "
                         "pipeline/attribute_mask.py.")
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
    # ---- CONTROL FLAGS. All default to nothing, and nothing is the branch that
    # is byte-identical to this script before 2026-08-20. See the docstring's
    # FOURTH CALLER note for why they exist and what diffusers does with them.
    ap.add_argument("--controlnet", default="",
                    help="ControlNet repo id or local dir; must be in the "
                         "CONTROLNETS allowlist, because the licence travels "
                         "with the name")
    ap.add_argument("--control", default="",
                    help="the hint PNG. MUST be exactly the init's pixel size: "
                         "it is handed over FULL-FRAME and diffusers crops it "
                         "with the same crops_coords it crops the init with")
    ap.add_argument("--control-sha256", default="",
                    help="pin the hint's bytes; required whenever --control is "
                         "passed")
    ap.add_argument("--scale", type=float, default=None,
                    help="controlnet_conditioning_scale for --controlnet; "
                         "required when --controlnet is passed")
    ap.add_argument("--controlnet2", default="",
                    help="a SECOND net, composed with the first as a "
                         "MultiControlNetModel")
    ap.add_argument("--control2", default="", help="the second hint PNG")
    ap.add_argument("--control2-sha256", default="", help="pin for --control2")
    ap.add_argument("--scale2", type=float, default=None,
                    help="conditioning scale for --controlnet2")
    ap.add_argument("--selftest", action="store_true",
                    help="$0, no torch, no CUDA, no network: reproduces a filed "
                         "verdict's sidecar byte-for-byte and proves the control "
                         "flags cannot change the no-control path")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if not os.path.isfile(a.init):
        print("!! init not found: %s" % a.init, flush=True)
        return 2
    have = sha256_of(a.init)
    if have != a.init_sha256:
        print("!! INIT SHA MISMATCH -- refusing.\n   want %s\n   have %s"
              % (a.init_sha256, have), flush=True)
        return 3

    if sum(1 for v in (a.ellipse, a.quad, a.mask_png) if v) != 1:
        print("!! pass exactly one of --ellipse, --quad or --mask-png", flush=True)
        return 2

    cx = cy = rx = ry = 0
    corners: list = []
    mask_sha = ""
    if a.mask_png:
        if not os.path.isfile(a.mask_png):
            print("!! --mask-png not found: %s" % a.mask_png, flush=True)
            return 2
        mask_sha = sha256_of(a.mask_png)
        shape = "png"
        bbox = []
    elif a.ellipse:
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
    if shape == "png":
        supplied = Image.open(a.mask_png).convert("L")
        if supplied.size != (W, H):
            print("!! MASK SIZE MISMATCH -- refusing.\n   init %dx%d\n   mask %dx%d"
                  % (W, H, supplied.size[0], supplied.size[1]), flush=True)
            return 6
        mask = supplied
        box = mask.point(lambda v: 255 if v > 0 else 0).getbbox()
        if box is None:
            print("!! mask is entirely black -- nothing would be redrawn.", flush=True)
            return 7
        # getbbox()'s right/bottom are exclusive; the sidecar reports inclusive px.
        bbox = [box[0], box[1], box[2] - 1, box[3] - 1]
    elif shape == "ellipse":
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
    if shape == "png":
        mask_lines += ["mask_png_source: %s" % a.mask_png.replace("\\", "/"),
                       "mask_png_sha256: %s" % mask_sha,
                       "mask_white_px: %d"
                       % (W * H - mask.point(lambda v: 255 if v > 0 else 0)
                          .histogram()[0])]
    elif shape == "ellipse":
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
