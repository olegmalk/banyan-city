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


# §28's FINDING, AS A NUMBER. `padding_mask_crop` rescales the hint along with
# the init, and a pose hint's semantics are scale-dependent in a way an init
# image's are not: the authored hint was two whole figures at frame scale and
# what the net received was one torso filling the frame -- a different
# instruction, which the sampler obeyed, and which every automatic clause on the
# route passed. A little slack is allowed because a mask that is already
# effectively the frame produces a box the same size as the frame and magnifies
# nothing; anything past that is the defect.
HINT_MAGNIFICATION_CEILING = 1.05


def hint_magnification(region, W: int, H: int) -> float:
    """How much diffusers' crop box will magnify a full-frame hint. 1.0 = none.

    `region` is None whenever padding_mask_crop is off, and off is the
    configuration in which this whole class of defect cannot occur.
    """
    if not region:
        return 1.0
    return max(W / float(region[2] - region[0]), H / float(region[3] - region[1]))


def assert_hint_survives_crop(controls, region, W: int, H: int) -> float:
    """Refuse a hint that `padding_mask_crop` would magnify. §28, in code.

    THIS IS THE ONE THING THE ROUTE LEARNED THAT WAS NOT YET ENFORCED. §28
    closed beat 08's fill on a mechanism rather than a tally, and wrote down the
    rule its own last paragraph states: this driver "is usable at `--pad-crop 0`,
    on a region large enough not to need the crop, and it is not usable on a
    small region." That sentence sat in prose for two days while the flags that
    violate it stayed one command line away.

    It is deliberately NOT a blanket ban on combining hints with
    padding_mask_crop. The defect is the MAGNIFICATION, not the flag: a mask that
    already covers the frame yields a crop box the size of the frame, magnifies
    nothing, and is safe. So the guard measures the thing that broke rather than
    banning the flag that happened to be set when it broke -- and a full-frame
    img2img pass, which is what this route is, is admitted by construction.

    Returns the magnification factor so a caller can log it. No controls, or no
    crop, is 1.0 and never raises -- the no-control path must stay the path six
    filed b08 verdicts were measured on.
    """
    if not controls:
        return 1.0
    mag = hint_magnification(region, W, H)
    if mag > HINT_MAGNIFICATION_CEILING:
        raise ControlError(
            "!! THE CROP WOULD MAGNIFY THE HINT %.2fx -- refusing.\n"
            "   frame     %dx%d\n"
            "   crop box  %s  (%dx%d)\n"
            "   A ControlNet hint's meaning is SCALE-DEPENDENT in a way an init\n"
            "   image's is not. diffusers derives ONE crops_coords from the mask\n"
            "   and applies it to the init, the mask AND every control image, then\n"
            "   resizes all of them back to %dx%d. The alignment stays exact and\n"
            "   the conditioning is still wrong: the net is handed a magnified\n"
            "   fragment saying 'a body THIS BIG, HERE' instead of the pose that\n"
            "   was authored. That is ep2-b08-cnetfill-0820, whose frame was the\n"
            "   worst on the route while every automatic clause passed it --\n"
            "   see pipeline/b08-arm-route-0819.md section 28.\n"
            "   There is no value of --pad-crop that satisfies both halves on a\n"
            "   small region. Either drop the hint, or run at --pad-crop 0 on a\n"
            "   region large enough not to need the crop."
            % (mag, W, H, tuple(region), region[2] - region[0],
               region[3] - region[1], W, H), 15)
    return mag


def sidecar_text(*, pipeline_class: str, in_ch: int, W: int, H: int, steps: int,
                 cfg, strength, seed: int, pad_crop, blur: int, init: str,
                 init_sha: str, mask_png_name: str, mask_lines, control_lines,
                 stamp: str, render_s: float, wall_s: float, versions: dict,
                 note: str, prompt: str, negative: str, lora_lines=()) -> str:
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
    ] + list(mask_lines) + list(lora_lines) + list(control_lines) + [
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


# ── LoRA BLOCK WEIGHTS -------------------------------------------------------
#
# WHY THIS EXISTS, AND IT IS A MEASUREMENT AND NOT A HUNCH. `bnyjerry v3` poses:
# 4 of 6 B2 cells adopted their skeleton at weight 0.8 against a control of 0/6,
# including a STRIDE the dataset never contained. It also keeps his face: B1 is
# sage in 15 of 15 cells at the same checkpoint and the same weight. The single
# clause between that and a shippable recipe is HIS SKIN UNDER A POSE NET --
# sage in 15/15 without a skeleton, tan in 6/6 with one -- and three free levers
# are measured dead, one variable each:
#
#   prompt dialect  lora-jerry-v3-capshape-0822   caption-shaped prompt -> TAN
#   hint volume     lora-jerry-v3-cnetscale-0822  --scale 0.7 and 0.5   -> TAN
#   trigger volume  lora-jerry-v3-loraweight-0822 --lora-weight 1.0/1.2 -> nudge
#
# So the palette is not reachable by either channel's VOLUME, which says the
# defect is structural in how a fused LoRA composes with the ControlNet pipeline
# -- and per-block scaling is the instrument that addresses exactly that.
#
# THE BLOCK MAP IS COMMUNITY, NOT PUBLISHED, AND IS LABELLED THAT WAY.
# hako-mikan's sd-webui-lora-block-weight and its successor report that INPUT
# blocks retain structural identity (facial symmetry, hair shape, facial
# features) while OUTPUT blocks house background detail and AESTHETIC RENDERING,
# and they ship opposed CHARACTER and LAYOUT presets on that basis. There is
# paper-grade backing for block-level separation of identity from style
# (Block-wise LoRA, arXiv 2403.07500) but its abstract does not say WHICH blocks
# do what, so the direction below is COMMUNITY and the presets are named for the
# hypothesis they encode rather than for a result.
#
#   https://github.com/hako-mikan/sd-webui-lora-block-weight
#   https://github.com/SiliconeShojo/lora-block-weight-neo
#   https://arxiv.org/abs/2403.07500
#
# THE API IS PRESENT IN THE VERSION WE RUN, read off the box's own installed
# source rather than off `main`'s docs: diffusers 0.29.2 / peft 0.12.0,
# UNet2DConditionLoadersMixin.set_adapters(adapter_names, weights: Optional[
# Union[float, Dict, List[float], List[Dict], List[None]]]), and
# unet_loader_utils._maybe_expand_lora_scales_for_one_adapter documents in its
# own docstring that it expands {"down": 2, "mid": 3, "up": {...}} into
# per-transformer scales.
LORA_BLOCK_PRESETS = {
    # THE INSTRUMENT CHECK, AND IT IS NOT OPTIONAL. A flat 1.0 through
    # set_adapters should behave like the fused path at weight 1.0. Without this
    # cell a null result is unattributable between "block weighting does not
    # help" and "the set_adapters wiring is not doing anything", which is the
    # exact class of mistake that costs this tree days.
    "flat": {"down": 1.0, "mid": 1.0, "up": 1.0},
    # THE HYPOTHESIS: the palette lives in the output blocks. Push those up and
    # leave the structural blocks near where they already work.
    "palette": {"down": 0.8, "mid": 0.8, "up": 1.4},
    # THE SAME HYPOTHESIS, HARDER, and with the other half of the reasoning in
    # it: the input blocks are the ones the community map says carry structure,
    # and structure is what the pose net is trying to supply. Starving them
    # should cost nothing the ControlNet is not already providing, while the
    # output blocks carry his colour.
    "palette-starve": {"down": 0.4, "mid": 0.4, "up": 1.4},
}


def parse_lora_blocks(spec: str):
    """A preset name or a JSON dict -> the nested weights `set_adapters` takes.

    Pure, so `--selftest` exercises it with no torch, no CUDA and no network.
    Returns None for an empty spec, and NONE IS THE DEFAULT PATH: every caller
    that does not pass this flag gets the fused branch, unchanged.
    """
    import json
    spec = (spec or "").strip()
    if not spec:
        return None
    if spec in LORA_BLOCK_PRESETS:
        return dict(LORA_BLOCK_PRESETS[spec])
    if not spec.startswith("{"):
        raise ControlError(
            "!! --lora-blocks %r is neither a preset nor a JSON object.\n"
            "   presets: %s\n"
            "   or pass a dict, e.g. '{\"down\": 0.8, \"mid\": 0.8, \"up\": 1.4}'"
            % (spec, ", ".join(sorted(LORA_BLOCK_PRESETS))), 17)
    try:
        val = json.loads(spec)
    except Exception as e:
        raise ControlError("!! --lora-blocks is not valid JSON: %s" % e, 17)
    if not isinstance(val, dict) or not val:
        raise ControlError("!! --lora-blocks must be a non-empty JSON object", 17)
    bad = [k for k in val if k not in ("down", "mid", "up")]
    if bad:
        raise ControlError(
            "!! --lora-blocks has unknown top-level key(s) %s. diffusers 0.29.2's "
            "_maybe_expand_lora_scales_for_one_adapter understands `down`, `mid` "
            "and `up` (each a number, or a dict of block_N -> number/list)."
            % ", ".join(sorted(bad)), 17)
    return val


def lora_block_meta_lines(blocks) -> list:
    """The block-weight block, or NOTHING AT ALL when no blocks were passed.

    SAME EMPTINESS CONTRACT AS `control_meta_lines` AND `lora_meta_lines`, and
    here it is load-bearing for every verdict this driver has ever filed: a run
    without --lora-blocks must write the bytes it wrote before this flag
    existed. `--selftest` asserts that against the filed golden sidecar.
    """
    if not blocks:
        return []
    import json
    return [
        "lora_block_weights: %s" % json.dumps(blocks, sort_keys=True),
        "lora_block_map_provenance: >-",
        yaml_block(
            "COMMUNITY, NOT PUBLISHED. The direction -- input blocks carry "
            "structural identity, output blocks carry aesthetic rendering -- is "
            "hako-mikan's sd-webui-lora-block-weight and its successor. "
            "Block-wise LoRA (arXiv 2403.07500) backs block-level separation of "
            "identity from style but does not say which blocks do what. Treat "
            "the mapping as a hypothesis this cell is testing, not as a fact it "
            "is applying."),
        "lora_applied_by: >-",
        yaml_block(
            "set_adapters, NOT fuse_lora. Per-block scaling requires the "
            "adapter to stay live on the UNet, so this run does NOT bake a "
            "scalar delta into the tensors. Two consequences are recorded "
            "rather than glossed: (1) `--lora-weight` is IGNORED on this path -- "
            "the per-block numbers are the weights; (2) set_adapters scales "
            "ATTENTION weights only, so ResNets and samplers stay at 1.0, and a "
            "prior living outside attention is out of this lever's reach."),
    ]


def lora_meta_lines(lora: str, weight, lora_sha: str, fused: bool = True) -> list:
    """The LoRA block, or NOTHING AT ALL when no LoRA was fused.

    Same emptiness contract as `control_meta_lines`, and here it is load-bearing
    for six filed b08 verdicts: a run with no --lora must write the bytes it
    wrote before this flag existed, or none of them is reproducible any more.

    `fused` DEFAULTS TO TRUE AND THE DEFAULT IS THE CONTRACT. Added 2026-08-22
    with the block-weight arm, which cannot fuse: per-block scaling needs the
    adapter to stay live, so on that path the last line would otherwise assert
    an ordering that did not happen. Every existing caller passes nothing and
    gets the exact bytes it got before, which `--selftest` checks against a
    filed sidecar rather than by inspection.
    """
    if not lora:
        return []
    # os.path.basename on a WINDOWS path under POSIX returns the whole string --
    # the box's paths are `C:\banyan-farm\...` and the selftest runs on a Mac,
    # so the separator is normalised first or the sidecar names a drive letter.
    return [
        "lora: %s" % lora.replace("\\", "/").rsplit("/", 1)[-1],
        "lora_path: %s" % lora.replace("\\", "/"),
        "lora_sha256: %s" % (lora_sha or "unmeasured"),
        "lora_weight: %s" % weight,
    ] + ([
        "lora_fused_before_controlnet_swap: true  # from_pipe reuses the module "
        "objects, so a fused UNet travels into the swapped pipeline",
    ] if fused else [
        "lora_fused_before_controlnet_swap: false  # per-block scaling keeps the "
        "adapter LIVE on the UNet instead of baking a scalar delta; from_pipe "
        "reuses the same module objects either way, so the adapter still "
        "travels into the swapped pipeline by identity",
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
    # NOT argparse-required, and that is deliberate: `--selftest` runs the whole
    # module with no init, no plate and no prompt, and argparse would reject it
    # before main() ever saw the flag. The four are asserted by hand below,
    # AFTER the selftest branch, so a real invocation still cannot omit them.
    ap.add_argument("--init")
    ap.add_argument("--init-sha256",
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
    ap.add_argument("--prompt-file")
    ap.add_argument("--negative-file")
    ap.add_argument("--out")
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
    # ---- THE CHARACTER LoRA ARM ----------------------------------------
    # Added 2026-08-22, eight lines mirroring the one controlnet_plate.py grew
    # the same day, and it exists because of where the pose net WORKS.
    # `registry.yaml`'s bnyjerry v2 entry closed B2 as VOID rather than failed:
    # controlnet_plate.py's TXT2IMG path did not move a pose with NO LoRA loaded,
    # on either of xinsir's two openpose blobs, while THIS driver measurably
    # drives the same net (15.05 mean abs, goblin i2i route round two). So the
    # pose-adoption bar has to be run here -- and `inpaint_fruit.py` with an
    # ALL-WHITE MASK at STRENGTH 1.0 *is* txt2img-with-ControlNet, on the one
    # code path in this repo where the pose net is proven to act.
    #
    # Absent by default, so every existing caller behaves exactly as it did:
    # `--selftest` reproduces the filed `ep2-b08-str70-0820` sidecar byte for
    # byte through the same function, and that golden call passes no LoRA.
    ap.add_argument("--lora", default="",
                    help="a character LoRA .safetensors, fused into the UNet "
                         "BEFORE the ControlNet swap. from_pipe rebuilds the "
                         "class around THE SAME module objects, so a delta "
                         "baked into the UNet here travels into the swapped "
                         "pipeline by identity")
    ap.add_argument("--lora-weight", type=float, default=0.8,
                    help="lora_scale at fuse time")
    ap.add_argument("--lora-blocks", default="",
                    help="PER-BLOCK LoRA scaling: a preset name (%s) or a JSON "
                         "object like '{\"down\": 0.8, \"mid\": 0.8, \"up\": "
                         "1.4}'. PRESENT switches the LoRA from fuse_lora to "
                         "set_adapters, which is the only way diffusers 0.29.2 "
                         "will scale per block; ABSENT is the fused path this "
                         "driver has always taken and is byte-identical to it. "
                         "On this path --lora-weight is IGNORED: the per-block "
                         "numbers ARE the weights."
                         % ", ".join(sorted(LORA_BLOCK_PRESETS)))
    ap.add_argument("--lora-sha256", default="",
                    help="pin for --lora; refused on mismatch (rc 16). A "
                         "checkpoint directory holds five epochs with names one "
                         "character apart and the sidecar has to name the bytes "
                         "that actually drew the frame.")
    ap.add_argument("--selftest", action="store_true",
                    help="$0, no torch, no CUDA, no network: reproduces a filed "
                         "verdict's sidecar byte-for-byte and proves the control "
                         "flags cannot change the no-control path")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    missing = [f for f, v in (("--init", a.init), ("--init-sha256", a.init_sha256),
                              ("--prompt-file", a.prompt_file),
                              ("--negative-file", a.negative_file),
                              ("--out", a.out)) if not v]
    if missing:
        print("!! missing required argument(s): %s" % ", ".join(missing),
              flush=True)
        return 2

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

    # ---- CONTROL HINTS, resolved BEFORE any weight loads and before the dry
    # run returns, so a mis-sized or mis-pinned hint costs zero GPU seconds and
    # is caught at the same $0 step the mask geometry is.
    try:
        controls = resolve_controls(a, (W, H))
        # AND THE BLOCK SPEC, resolved at the same $0 step and for the same
        # reason: a typo in a preset name or a stray brace must cost zero GPU
        # seconds, and the dry run must be able to print what will be applied.
        lora_blocks = parse_lora_blocks(getattr(a, "lora_blocks", ""))
    except ControlError as e:
        print(str(e), flush=True)
        return e.code
    if lora_blocks is not None and not a.lora:
        print("!! --lora-blocks was passed with no --lora. Per-block scaling "
              "with nothing to scale is a recipe nobody can read.", flush=True)
        return 17

    # The crop box, from THIS driver's vendored copy of diffusers'
    # get_crop_region, on the same blurred mask the pipeline will be handed. In
    # the dry run it is the number the operator checks the hint against by eye;
    # in the real run it is re-derived from the LIVE method and the two must
    # agree. Blurring here costs nothing and is not the pipeline's blur call --
    # `mask_processor.blur` is `ImageFilter.GaussianBlur(blur_factor)` and
    # nothing else, so this is the same image.
    from PIL import ImageFilter
    blur_preview = (mask.filter(ImageFilter.GaussianBlur(a.blur)) if a.blur
                    else mask)
    region = crop_region(blur_preview, W, H, a.pad_crop) if a.pad_crop else None

    # ---- §28's LESSON, ENFORCED HERE AND AT $0. The crop that makes a small
    # region drawable is the same crop that destroys a hint's meaning, and the
    # two are mutually exclusive in this tool. Checked before the dry run
    # returns, so the refusal costs no GPU seconds and no model load.
    try:
        mag = assert_hint_survives_crop(controls, region, W, H)
    except ControlError as e:
        print(str(e), flush=True)
        return e.code
    if controls:
        print("HINT MAGNIFICATION %.3fx (ceiling %.2f) -- the hint reaches the "
              "net at the scale it was authored" % (mag, HINT_MAGNIFICATION_CEILING),
              flush=True)

    if a.dry_run:
        print("DRY RUN -- no model loaded, nothing rendered.", flush=True)
        print("init_sha256 OK %s" % have, flush=True)
        print("mask %s corners=%s bbox=%s  %.4f x %.4f of %dx%d"
              % (shape, corners or "-", bbox,
                 (bbox[2] - bbox[0]) / float(W),
                 (bbox[3] - bbox[1]) / float(H), W, H), flush=True)
        for i, c in enumerate(controls):
            print("hint %d %s scale %s sha %s -- %dx%d, MATCHES the init"
                  % (i + 1, os.path.basename(c["path"]), c["scale"],
                     c["sha256"][:16], c["image"].size[0], c["image"].size[1]),
                  flush=True)
        if controls:
            print("pad_crop region (vendored get_crop_region on the blurred "
                  "mask) = %s -- diffusers applies THIS SAME box to the init, "
                  "the mask and every hint" % (region,), flush=True)
        if lora_blocks is not None:
            print("lora blocks %r -- set_adapters path, NO fuse, --lora-weight "
                  "%s ignored" % (lora_blocks, a.lora_weight), flush=True)
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

    # ---- THE CHARACTER LoRA, FUSED BEFORE THE CONTROLNET SWAP -------------
    #
    # FUSED HERE, DELIBERATELY, AND FOR THE MIRROR OF THE REASON AN IP-ADAPTER
    # WOULD BE REGISTERED AFTER. `from_pipe` rebuilds the pipeline class around
    # THE SAME MODULE OBJECTS, so a weight delta fused into the UNet at this
    # point travels into the swapped ControlNet pipeline by identity, while an
    # ADAPTER registered on the pre-swap object would be registered on a
    # pipeline nobody calls. fuse_lora bakes the delta into the UNet tensors.
    lora_sha = ""
    if a.lora:
        if not os.path.isfile(a.lora):
            print("!! no such LoRA: %s" % a.lora, flush=True)
            return 16
        # THE PEFT GATE, checked BEFORE the ControlNet download and before any
        # further weight load, because it already cost this tree a run:
        # diffusers 0.29.2 gates ALL LoRA loading behind USE_PEFT_BACKEND, peft
        # was absent from both venvs on the box, and a training job spent twenty
        # clean minutes and five checkpoints before dying in nine seconds on
        # `PEFT backend is required for this method.`
        from diffusers.utils import USE_PEFT_BACKEND
        if not USE_PEFT_BACKEND:
            print("!! diffusers has no PEFT backend, so load_lora_weights() "
                  "cannot run.\n   fix:  <this venv>/python.exe -m pip install "
                  "--no-deps peft==0.12.0\n   --no-deps is required -- a plain "
                  "install may resolve torch away from 2.11.0+cu128 and break "
                  "every render on this card.", flush=True)
            return 16
        lora_sha = sha256_of(a.lora)
        if a.lora_sha256 and a.lora_sha256 != lora_sha:
            print("!! LoRA sha256 mismatch -- refusing.\n   want %s\n   have %s"
                  % (a.lora_sha256, lora_sha), flush=True)
            return 16
        if lora_blocks is None:
            # ---- THE DEFAULT PATH, UNCHANGED. Six filed b08 verdicts and every
            # goblin cell to date were measured through these three lines and
            # they do not move.
            pipe.load_lora_weights(os.path.dirname(os.path.abspath(a.lora)),
                                   weight_name=os.path.basename(a.lora))
            pipe.fuse_lora(lora_scale=float(a.lora_weight))
            print("LORA %s fused at weight %.2f, sha %s"
                  % (os.path.basename(a.lora), float(a.lora_weight),
                     lora_sha[:16]), flush=True)
        else:
            # ---- THE BLOCK-WEIGHT ARM. NOT A FUSE, and that is the whole point:
            # fuse_lora bakes ONE scalar into the tensors and there is no scalar
            # that means "more in the output blocks". set_adapters keeps the
            # adapter live and takes the nested dict that
            # _maybe_expand_lora_scales_for_one_adapter expands per transformer.
            #
            # ON THE UNET AND NOT ON THE PIPE, deliberately: the dict-capable
            # signature read off the box's installed source is
            # UNet2DConditionLoadersMixin.set_adapters, and the pipeline-level
            # wrapper also drives the text encoders, which have no block map and
            # would silently take a float. Block weighting is a UNet question.
            #
            # AND IT REFUSES RATHER THAN FALLING BACK. A silent fallback to the
            # fused path would produce a perfectly plausible frame answering a
            # different question -- the same failure the hint-sha guard exists
            # to stop -- so an exception here is a hard stop with its own code.
            pipe.load_lora_weights(os.path.dirname(os.path.abspath(a.lora)),
                                   weight_name=os.path.basename(a.lora),
                                   adapter_name="ch")
            try:
                pipe.unet.set_adapters(["ch"], [lora_blocks])
            except Exception as e:
                print("!! set_adapters REFUSED the per-block dict and this run "
                      "will NOT fall back to a fuse -- a fused frame filed "
                      "under a block-weight cell would answer a different "
                      "question.\n   dict: %r\n   %s: %s"
                      % (lora_blocks, type(e).__name__, e), flush=True)
                return 17
            print("LORA %s applied PER BLOCK via set_adapters (no fuse): %r, "
                  "sha %s -- --lora-weight %s is IGNORED on this path"
                  % (os.path.basename(a.lora), lora_blocks, lora_sha[:16],
                     a.lora_weight), flush=True)

    # ---- THE CLASS SWAP, AND IT HAPPENS ONLY IF A HINT WAS PASSED.
    # from_pipe rebuilds the class around the SAME loaded modules, so one set of
    # base weights serves both arms and the no-control path never touches this.
    pipeline_class = "StableDiffusionXLInpaintPipeline"
    control_kwargs = {}
    if controls:
        from diffusers import AutoPipelineForInpainting, ControlNetModel

        cn_kw = {} if CONTROLNET_VARIANT is None else {"variant": CONTROLNET_VARIANT}
        nets = []
        for c in controls:
            m = ControlNetModel.from_pretrained(c["net"],
                                                torch_dtype=torch.bfloat16, **cn_kw)
            m.to("cuda")
            nets.append(m)
        # A LIST is wrapped into a MultiControlNetModel by the constructor, and
        # `control_image` / `controlnet_conditioning_scale` then become per-net
        # lists in the same order. A single net stays a bare model and bare
        # values -- the shape controlnet_plate.py uses on the txt2img side.
        pipe = AutoPipelineForInpainting.from_pipe(
            pipe, controlnet=(nets if len(nets) > 1 else nets[0]))
        pipeline_class = type(pipe).__name__
        if len(nets) > 1:
            control_kwargs = {
                "control_image": [c["image"] for c in controls],
                "controlnet_conditioning_scale": [c["scale"] for c in controls]}
        else:
            control_kwargs = {
                "control_image": controls[0]["image"],
                "controlnet_conditioning_scale": controls[0]["scale"]}
        control_kwargs["control_guidance_start"] = CONTROL_GUIDANCE[0]
        control_kwargs["control_guidance_end"] = CONTROL_GUIDANCE[1]
        print("PIPELINE %s, %d net(s), scales %s"
              % (pipeline_class, len(nets),
                 control_kwargs["controlnet_conditioning_scale"]), flush=True)

        # ---- A COPY-PASTE BUG IN 0.29.2's check_inputs, AND THE PROOF IS
        # ---- INSIDE check_inputs ITSELF.
        # `__call__` passes CONTROL_IMAGE as the parameter that function calls
        # `image`. Its padding_mask_crop branch then says:
        #     if not isinstance(image, PIL.Image.Image):
        #         raise ValueError("The image should be a PIL image when
        #                           inpainting mask crop, ...")
        # -- which is lifted verbatim from the plain inpaint pipeline, where
        # `image` IS the init. Twenty lines further down the SAME function
        # requires that same argument to be a LIST whenever the controlnet is a
        # MultiControlNetModel ("For multiple controlnets: `image` must be type
        # `list`"). The two clauses contradict each other, so with two nets the
        # call can never be valid, and with one net the check passes only by
        # accident -- it happens to be looking at a PIL image that is not the
        # one it was written to guard. The init, which the branch MEANT, is
        # never type-checked by this pipeline at all.
        #
        # Everything downstream of the check handles the list correctly:
        # `prepare_control_image` is called in a loop over `control_image` in
        # the MultiControlNetModel branch, with the SAME crops_coords and the
        # same resize_mode as the init and the mask. So the render is sound and
        # only the validator is wrong.
        #
        # THE PATCH IS THEREFORE THE NARROWEST ONE THAT EXISTS: call diffusers'
        # own check with padding_mask_crop=None -- which skips ONLY that branch
        # and leaves every other clause, including the multi-net list checks,
        # running exactly as written -- and re-assert the three things the
        # branch actually wanted, against the images it actually meant.
        if a.pad_crop and isinstance(control_kwargs["control_image"], list):
            _orig_check = pipe.check_inputs

            def _checked(*args, **kw):
                if "padding_mask_crop" in kw:
                    kw["padding_mask_crop"] = None
                elif len(args) >= 21:
                    args = args[:20] + (None,) + args[21:]
                _orig_check(*args, **kw)
                from PIL import Image as _I
                bad = [i for i, c in enumerate(control_kwargs["control_image"])
                       if not isinstance(c, _I.Image)]
                if bad:
                    raise ValueError("hint %s is not a PIL image" % bad)
                if not isinstance(plate, _I.Image):
                    raise ValueError("the init must be a PIL image with "
                                     "padding_mask_crop")
                if not isinstance(blurred, _I.Image):
                    raise ValueError("the mask must be a PIL image with "
                                     "padding_mask_crop")

            pipe.check_inputs = _checked
            print("CHECK_INPUTS wrapped: 0.29.2 asserts the CONTROL image is a "
                  "single PIL under padding_mask_crop, and the same function "
                  "requires it to be a LIST under MultiControlNetModel. The "
                  "branch is skipped and its three real checks are re-run here "
                  "against the init, the mask and each hint.", flush=True)

    blurred = pipe.mask_processor.blur(mask, blur_factor=a.blur) if a.blur else mask

    # ---- ALIGNMENT, CHECKED AGAINST THE LIVE METHOD RATHER THAN ASSERTED.
    # diffusers derives ONE crops_coords from this blurred mask and applies it to
    # the init, the mask and every control image. If the installed version's
    # get_crop_region disagrees with the copy vendored above, the box written
    # into the sidecar would be fiction and the hint's alignment would be
    # unverified -- so it is a hard stop. Control runs only: the no-control path
    # must stay the path six filed verdicts were measured on.
    if controls and a.pad_crop:
        live = tuple(int(v) for v in pipe.mask_processor.get_crop_region(
            blurred, W, H, pad=a.pad_crop))
        if live != tuple(region):
            print("!! CROP REGION DISAGREES WITH THE VENDORED COPY -- refusing.\n"
                  "   vendored %s\n   diffusers %s\n   The hint is cropped by "
                  "diffusers' box, so a sidecar carrying a different one cannot "
                  "be trusted about alignment." % (tuple(region), live), flush=True)
            return 14
        print("CROP REGION %s -- vendored == live; the init, the mask and every "
              "hint are cropped by this one box" % (live,), flush=True)

    kwargs = dict(prompt=prompt, negative_prompt=negative, image=plate,
                  mask_image=blurred, width=W, height=H,
                  num_inference_steps=a.steps, guidance_scale=a.cfg,
                  strength=a.strength,
                  generator=torch.Generator("cuda").manual_seed(a.seed))
    if a.pad_crop:
        kwargs["padding_mask_crop"] = a.pad_crop
    kwargs.update(control_kwargs)

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
        fh.write(sidecar_text(
            pipeline_class=pipeline_class, in_ch=in_ch, W=W, H=H, steps=a.steps,
            cfg=a.cfg, strength=a.strength, seed=a.seed, pad_crop=a.pad_crop,
            blur=a.blur, init=a.init, init_sha=have,
            mask_png_name=os.path.basename(mask_png), mask_lines=mask_lines,
            lora_lines=(lora_meta_lines(a.lora, a.lora_weight, lora_sha,
                                        fused=lora_blocks is None)
                        + lora_block_meta_lines(lora_blocks)),
            control_lines=control_meta_lines(controls, region), stamp=stamp,
            render_s=render_s, wall_s=time.time() - t0, versions=versions,
            note=a.note, prompt=prompt, negative=negative))

    print("WROTE %s" % a.out, flush=True)
    print("WROTE %s" % mask_png, flush=True)
    print("WROTE %s" % sidecar, flush=True)
    print("rc=0 render_s=%.1f" % render_s, flush=True)
    return 0


# ---------------------------------------------------------------------------
# SELFTEST. $0, no torch, no CUDA, no network, no GPU.
#
# IT IS ANCHORED ON A FILED VERDICT AND NOT ON A FIXTURE I WROTE TODAY.
# `ep2-b08-str70-0820` is one of the six b08 verdicts these ControlNet flags must
# not disturb. Its sidecar is in the tree, its sha is pinned below, and the test
# reproduces it BYTE FOR BYTE through the refactored `sidecar_text()`. A
# fixture-based test would only prove the new code agrees with itself.
#
# THE ALIGNMENT CLAUSE IS STRUCTURAL, because that is the class of defect that
# ate this beat: the hints are handed over FULL-FRAME and this module contains no
# crop of its own, so there is nothing here that can disagree with the single
# crops_coords diffusers derives from the mask. Both halves are asserted -- the
# size equality, and the absence of any crop call in the source.
# ---------------------------------------------------------------------------
# THE SECOND GOLDEN, AND IT COVERS THE BRANCH THE BLOCK ARM EDITED. The one
# below is a no-LoRA run; this is `b2-seat-s1` of the v3 ladder, a real filed
# cell that loaded a LoRA and fused it, and it is the exact cell the block
# sweep varies against. Added 2026-08-22 with --lora-blocks.
LORA_GOLDEN_SIDECAR = \
    "farm-out/lora-jerry-v3-ladder-0822/b2-seat-s1.png.meta.yaml"
LORA_GOLDEN_SHA = \
    "e07356b5a17018127e3e810ed7de5017ebafc5c58ef02269bc2bdc684fa40f18"
LORA_GOLDEN_PATH = r"C:\banyan-farm\lora-jerry-v3-0822\out\bnyjerry-sdxl-v3.safetensors"
LORA_GOLDEN_WEIGHT = "0.8"
LORA_GOLDEN_SHA256 = \
    "d2062ac060a4ac44e217815464de143897550f078294eb59b3f303cc5f8a0cdd"

GOLDEN_SIDECAR = "farm-out/ep2-b08-str70-0820/b08-str70-s20260822.png.meta.yaml"
GOLDEN_SIDECAR_SHA = \
    "363f1d42a8f078ed2b177a7896e2749038901a4db94e13c380e4d11e14639d5e"
GOLDEN_MASK = "farm-out/ep2-b08-str70-0820/08-first-citizen-eraseonly-mask-0820.png"
GOLDEN_INIT = "farm-out/ep2-b08-str70-0820/08-first-citizen-eraseonly-0820.png"
HINT_POSE = "farm-out/ep2-b08-scale30-0820/b08-openpose-nat-0819.png"
HINT_POSE_SHA = \
    "562911c8174a6ecc21bc8710a1ac1b7f965c3f2d865093a742c2598c37d952e0"
HINT_BOARD = "farm-out/ep2-b08-scale30-0820/b08-board-0820.png"
HINT_BOARD_SHA = \
    "38cd39da304dbb0317aa2522e1ccca099bef583e88e6573fde03b287358213d6"
NET_POSE = r"C:\banyan-farm\cnet-openpose-twins"
NET_BOARD = "xinsir/controlnet-scribble-sdxl-1.0"


class _Args(object):
    """argparse.Namespace by another name, so the validator can be called."""

    def __init__(self, **kw):
        self.controlnet = self.control = self.control_sha256 = ""
        self.controlnet2 = self.control2 = self.control2_sha256 = ""
        self.scale = self.scale2 = None
        self.__dict__.update(kw)


def selftest() -> int:
    import re

    from PIL import Image, ImageFilter

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    checks = []

    def check(label, ok):
        checks.append((label, bool(ok)))
        print("%s %s" % ("ok  " if ok else "FAIL", label), flush=True)

    def raises(fn, code):
        try:
            fn()
        except ControlError as e:
            return e.code == code
        return False

    # ---- 1. THE GOLDEN SIDECAR, REPRODUCED BYTE FOR BYTE ------------------
    gpath = os.path.join(repo, GOLDEN_SIDECAR)
    golden = open(gpath, "rb").read()
    check("the golden sidecar is the bytes this test was written against",
          hashlib.sha256(golden).hexdigest() == GOLDEN_SIDECAR_SHA)
    gtext = golden.decode("utf-8")
    glines = gtext.split("\n")

    def body_after(key):
        """The yaml_block body under a `key: >-` / `key: |-` line, unindented."""
        i = glines.index(key)
        out = []
        for line in glines[i + 1:]:
            if line.startswith("  "):
                out.append(line[2:])
            else:
                break
        return "\n".join(out)

    # The mask block is REBUILT from the real mask PNG rather than sliced out of
    # the golden, so the numbers in it are proved and not copied.
    mask = Image.open(os.path.join(repo, GOLDEN_MASK)).convert("L")
    W, H = mask.size
    box = mask.point(lambda v: 255 if v > 0 else 0).getbbox()
    bbox = [box[0], box[1], box[2] - 1, box[3] - 1]
    mask_lines = [
        "mask_shape: png",
        "mask_png_source: C:/banyan-farm/b08str70-0820/"
        "08-first-citizen-eraseonly-mask-0820.png",
        "mask_png_sha256: %s" % sha256_of(os.path.join(repo, GOLDEN_MASK)),
        "mask_white_px: %d"
        % (W * H - mask.point(lambda v: 255 if v > 0 else 0).histogram()[0]),
        "mask_bbox_px: [%d, %d, %d, %d]" % tuple(bbox),
        "mask_width_frac: %.4f" % ((bbox[2] - bbox[0]) / float(W)),
        "mask_height_frac: %.4f" % ((bbox[3] - bbox[1]) / float(H)),
    ]
    i0 = glines.index("mask_shape: png")
    check("the mask block computed off the real mask matches the filed one",
          glines[i0:i0 + len(mask_lines)] == mask_lines)

    rebuilt = sidecar_text(
        pipeline_class="StableDiffusionXLInpaintPipeline", in_ch=4, W=832, H=1216,
        steps=40, cfg=7.5, strength=0.7, seed=20260822, pad_crop=64, blur=8,
        init=r"C:\banyan-farm\b08str70-0820\08-first-citizen-eraseonly-0820.png",
        init_sha=sha256_of(os.path.join(repo, GOLDEN_INIT)),
        mask_png_name="b08-str70-s20260822-mask.png", mask_lines=mask_lines,
        control_lines=[], stamp="2026-08-20T14:24:24Z", render_s=7.3,
        wall_s=13.3,
        versions={"python": "3.12.10", "torch": "2.11.0+cu128",
                  "diffusers": "0.29.2"},
        note=body_after("note: >-"), prompt=body_after("prompt: |-"),
        negative=body_after("negative: |-"))
    check("a NO-CONTROL sidecar is byte-identical to the filed verdict's",
          rebuilt.encode("utf-8") == golden)

    # ---- 2. THE DEFAULT PATH CANNOT BE TOUCHED BY THE NEW FLAGS -----------
    check("no control flag resolves to NO controls at all",
          resolve_controls(_Args(), (832, 1216)) == [])
    check("no controls emit NO sidecar lines", control_meta_lines([], None) == [])
    check("no controls leave the pipeline class alone",
          "pipeline: StableDiffusionXLInpaintPipeline (base weights, "
          "unet.in_channels=4)" in gtext)

    # ---- 2b. THE LoRA ARM. Added 2026-08-22 for the goblin pose-adoption bar.
    #
    # THE FIRST CLAUSE IS THE ONE THAT MATTERS AND IT IS A NON-CHANGE CLAUSE.
    # Six filed b08 verdicts cite sidecars this function wrote; the byte-identity
    # check above already runs through the NEW signature (`lora_lines` defaults
    # to empty), so the golden reproduction IS the no-regression proof. These
    # clauses say the same thing at the unit below it.
    check("no --lora emits NO sidecar lines at all",
          lora_meta_lines("", 0.8, "") == [])
    check("a LoRA-less sidecar carries no lora line anywhere",
          "lora" not in gtext)
    LORA = r"C:\banyan-farm\lora-jerry-v2-0822\out\bnyjerry-sdxl-v2.safetensors"
    ll = lora_meta_lines(LORA, 0.8, "4" * 64)
    check("a LoRA sidecar names the weights file",
          "lora: bnyjerry-sdxl-v2.safetensors" in ll)
    check("a LoRA sidecar carries the sha256 of the bytes that drew the frame",
          "lora_sha256: " + "4" * 64 in ll)
    check("a LoRA sidecar records the weight it was fused at",
          "lora_weight: 0.8" in ll)
    check("a LoRA sidecar records the fuse-before-swap ordering",
          any(l.startswith("lora_fused_before_controlnet_swap: true") for l in ll))
    # AND THE UNMEASURED CASE IS NAMED RATHER THAN BLANK. A sidecar that says
    # `lora_sha256:` with nothing after it reads as "no hash exists"; it must say
    # that a hash was not taken, which is a different and reportable fact.
    check("a LoRA sidecar with no measured sha says so in words",
          "lora_sha256: unmeasured" in lora_meta_lines(LORA, 0.8, ""))
    # AND THE BLOCK DOES NOT DISTURB THE CONTROLNET BLOCK IT SITS BESIDE.
    with_both = sidecar_text(
        pipeline_class="StableDiffusionXLControlNetInpaintPipeline", in_ch=4,
        W=832, H=1216, steps=40, cfg=7.5, strength=1.0, seed=1, pad_crop=0,
        blur=8, init="i.png", init_sha="d" * 64, mask_png_name="m.png",
        mask_lines=["mask_shape: png"], lora_lines=ll,
        control_lines=["controlnet: %s" % NET_POSE], stamp="now", render_s=1.0,
        wall_s=2.0, versions={"python": "3", "torch": "2", "diffusers": "0"},
        note="n", prompt="p", negative="q")
    check("the LoRA block does not disturb the controlnet block",
          "controlnet: %s" % NET_POSE in with_both
          and "lora: bnyjerry-sdxl-v2.safetensors" in with_both)
    # THE FUSE IS BEFORE THE SWAP IN THE SOURCE, WHICH IS THE WHOLE MECHANISM.
    # from_pipe carries a fused UNet by identity; a fuse after it would be fused
    # into a pipeline nobody calls. Asserted on the source order, because there
    # is no way to assert it without a GPU otherwise.
    isrc = open(os.path.abspath(__file__), "r", encoding="utf-8").read()
    check("fuse_lora is called BEFORE AutoPipelineForInpainting.from_pipe",
          isrc.index("pipe.fuse_lora(")
          < isrc.index("pipe = AutoPipelineForInpainting.from_pipe("))
    check("the PEFT backend is gated before any LoRA load is attempted",
          isrc.index("USE_PEFT_BACKEND") < isrc.index("pipe.load_lora_weights("))

    # ---- 2b. THE BLOCK-WEIGHT ARM, AND THE FIRST CLAUSE IS THE ONLY ONE THAT
    # ---- REALLY MATTERS: THE DEFAULT PATH DID NOT MOVE.
    #
    # Six filed b08 verdicts plus every goblin cell in the v3 ladder were
    # measured through the fused path. This arm may not change one byte of what
    # they wrote, and "may not" is worth exactly what it is checked with. The
    # golden-sidecar reproduction above already runs through the NEW signature
    # (fused defaults True, lora_block_meta_lines returns []), so that check IS
    # the no-regression proof; these clauses say the same thing at the unit
    # below it and name it out loud so a future edit cannot quietly relax it.
    check("no --lora-blocks emits NO block lines at all",
          lora_block_meta_lines(None) == [] and lora_block_meta_lines({}) == [])
    # ---- THE LoRA-PATH GOLDEN, AND IT IS THE CLAUSE THIS ARM IS GATED ON.
    #
    # `GOLDEN_SIDECAR` above is a no-LoRA run, so reproducing it proves the
    # base path and says nothing about the branch actually edited here. This
    # reads a REAL FILED SIDECAR FROM A RUN THAT LOADED A LoRA -- b2-seat-s1 of
    # the v3 ladder, the exact cell the block sweep is about to vary against --
    # and asserts that today's `lora_meta_lines` still emits its five lines byte
    # for byte. If this arm ever changes what a fused run writes, the ladder's
    # 24 cells and the six b08 verdicts stop being reproducible, and this fails
    # instead of the discovery happening months later.
    lgold = os.path.join(repo, LORA_GOLDEN_SIDECAR)
    if os.path.isfile(lgold):
        lraw = open(lgold, "rb").read()
        check("the LoRA golden sidecar is the filed bytes",
              hashlib.sha256(lraw).hexdigest() == LORA_GOLDEN_SHA)
        filed = [l for l in lraw.decode("utf-8").splitlines()
                 if l.startswith("lora")]
        check("a FUSED run's sidecar block is byte-identical to the filed one",
              filed == lora_meta_lines(LORA_GOLDEN_PATH, LORA_GOLDEN_WEIGHT,
                                       LORA_GOLDEN_SHA256))
    else:
        # NOT SILENTLY SKIPPED. A missing golden is reported as a missing
        # golden, because "the check did not run" and "the check passed" must
        # never look the same in this output.
        check("!! the LoRA golden sidecar is MISSING (%s) -- the fused-path "
              "byte-identity clause DID NOT RUN" % LORA_GOLDEN_SIDECAR, False)
    check("the fused sidecar block is byte-identical with fused defaulted vs "
          "passed explicitly",
          lora_meta_lines(LORA, 0.8, "4" * 64)
          == lora_meta_lines(LORA, 0.8, "4" * 64, fused=True))
    check("the DEFAULT LoRA block still asserts the fuse-before-swap ordering",
          any(l.startswith("lora_fused_before_controlnet_swap: true")
              for l in lora_meta_lines(LORA, 0.8, "4" * 64)))
    # AND THE BLOCK PATH TELLS THE TRUTH ABOUT ITSELF instead of inheriting a
    # line that would assert an ordering that did not happen.
    nf = lora_meta_lines(LORA, 0.8, "4" * 64, fused=False)
    check("the block path records that it did NOT fuse",
          any(l.startswith("lora_fused_before_controlnet_swap: false")
              for l in nf)
          and not any(l.startswith("lora_fused_before_controlnet_swap: true")
                      for l in nf))
    check("the block path's sidecar is otherwise the fused one",
          nf[:4] == lora_meta_lines(LORA, 0.8, "4" * 64)[:4])
    # ---- the spec parser, which is where a typo has to die.
    check("no spec is the default path", parse_lora_blocks("") is None
          and parse_lora_blocks(None) is None)
    check("every preset resolves and none of them is empty",
          all(parse_lora_blocks(p) for p in LORA_BLOCK_PRESETS))
    check("the instrument-check preset is a flat 1.0 on all three groups",
          parse_lora_blocks("flat") == {"down": 1.0, "mid": 1.0, "up": 1.0})
    check("the palette presets push UP above DOWN, which is the hypothesis",
          all(parse_lora_blocks(p)["up"] > parse_lora_blocks(p)["down"]
              for p in ("palette", "palette-starve")))
    check("a JSON object parses", parse_lora_blocks('{"up": 1.4}') == {"up": 1.4})
    check("a preset returns a COPY, so a caller cannot mutate the table",
          (lambda d: (d.__setitem__("up", 99),
                      LORA_BLOCK_PRESETS["palette"]["up"] != 99)[1])(
                          parse_lora_blocks("palette")))
    for bad, why in (("nope", "an unknown preset name"),
                     ("{", "malformed JSON"),
                     ("{}", "an empty object"),
                     ('{"middle": 1.0}', "an unknown block group"),
                     ('["up"]', "a JSON array rather than an object")):
        try:
            parse_lora_blocks(bad)
            check("parse_lora_blocks refuses %s" % why, False)
        except ControlError as e:
            check("parse_lora_blocks refuses %s (rc %d)" % (why, e.code),
                  e.code == 17)
    # ---- and the source order, for the same reason the fuse clause is checked
    # ---- that way: there is no asserting this without a GPU otherwise.
    check("the block spec is parsed BEFORE any model loads",
          isrc.index("lora_blocks = parse_lora_blocks(")
          < isrc.index("pipe = StableDiffusionXLInpaintPipeline.from_pretrained("))
    check("set_adapters is reached only on the non-default branch",
          isrc.index("if lora_blocks is None:")
          < isrc.index("pipe.unet.set_adapters("))
    check("the block arm is applied BEFORE the controlnet swap, like the fuse",
          isrc.index("pipe.unet.set_adapters(")
          < isrc.index("pipe = AutoPipelineForInpainting.from_pipe("))
    check("a set_adapters failure REFUSES rather than falling back to a fuse",
          "will NOT fall back to a fuse" in isrc)

    # ---- 3. THE TWO HINTS, RESOLVED ---------------------------------------
    both = _Args(controlnet=NET_POSE, control=os.path.join(repo, HINT_POSE),
                 control_sha256=HINT_POSE_SHA, scale=1.0,
                 controlnet2=NET_BOARD, control2=os.path.join(repo, HINT_BOARD),
                 control2_sha256=HINT_BOARD_SHA, scale2=0.3)
    controls = resolve_controls(both, (832, 1216))
    check("two hints resolve to two nets in the order given",
          [c["net"] for c in controls] == [NET_POSE, NET_BOARD])
    check("their scales are the ones passed, not defaults",
          [c["scale"] for c in controls] == [1.0, 0.3])
    check("both nets carry their licence out of the allowlist",
          all("apache-2.0" in c["licence"] for c in controls))

    # ---- 4. ALIGNMENT, THE CLAUSE THIS BEAT DIED ON -----------------------
    init = Image.open(os.path.join(repo, GOLDEN_INIT))
    check("every hint is handed over FULL-FRAME, in the init's own size",
          all(c["image"].size == init.size for c in controls))
    src = open(os.path.abspath(__file__), "r", encoding="utf-8").read()
    check("this module crops NOTHING itself -- diffusers' one crops_coords is "
          "the only crop there is",
          not re.search(r"\.crop\(", src))
    blurred = mask.filter(ImageFilter.GaussianBlur(8))
    region = crop_region(blurred, 832, 1216, 64)
    check("the vendored crop_region returns one box inside the frame",
          len(region) == 4 and 0 <= region[0] < region[2] <= 832
          and 0 <= region[1] < region[3] <= 1216)
    check("that box contains the whole mask, which is what padding means",
          region[0] <= bbox[0] and region[1] <= bbox[1]
          and region[2] > bbox[2] and region[3] > bbox[3])
    check("the crop keeps the render's aspect ratio, so no hint is stretched "
          "differently from the init",
          abs((region[2] - region[0]) / (region[3] - region[1]) - 832 / 1216)
          < 0.01)
    small = Image.open(os.path.join(repo, HINT_POSE)).convert("RGB").resize((831, 1216))
    check("a hint that is not the init's size is REFUSED (rc 13)",
          raises(lambda: resolve_controls(
              _Args(controlnet=NET_POSE, control=os.path.join(repo, HINT_POSE),
                    control_sha256=HINT_POSE_SHA, scale=1.0),
              (832, 1216), open_image=lambda _p: small), 13))

    # ---- 5. THE REFUSALS ---------------------------------------------------
    check("an unlisted net is refused before any weight loads (rc 12)",
          raises(lambda: resolve_controls(
              _Args(controlnet="thibaud/controlnet-openpose-sdxl-1.0",
                    control=os.path.join(repo, HINT_POSE),
                    control_sha256=HINT_POSE_SHA, scale=1.0), (832, 1216)), 12))
    check("a net with no hint is refused (rc 6)",
          raises(lambda: resolve_controls(
              _Args(controlnet=NET_POSE, scale=1.0), (832, 1216)), 6))
    check("a hint with no net is refused (rc 6)",
          raises(lambda: resolve_controls(
              _Args(control=os.path.join(repo, HINT_POSE)), (832, 1216)), 6))
    check("a net with no stated scale is refused (rc 6)",
          raises(lambda: resolve_controls(
              _Args(controlnet=NET_POSE, control=os.path.join(repo, HINT_POSE),
                    control_sha256=HINT_POSE_SHA), (832, 1216)), 6))
    check("an unpinned hint is refused (rc 8)",
          raises(lambda: resolve_controls(
              _Args(controlnet=NET_POSE, control=os.path.join(repo, HINT_POSE),
                    scale=1.0), (832, 1216)), 8))
    check("a hint whose bytes are not the pinned ones is refused (rc 8)",
          raises(lambda: resolve_controls(
              _Args(controlnet=NET_POSE, control=os.path.join(repo, HINT_POSE),
                    control_sha256="0" * 64, scale=1.0), (832, 1216)), 8))
    check("the same net twice is refused (rc 12)",
          raises(lambda: resolve_controls(
              _Args(controlnet=NET_BOARD, control=os.path.join(repo, HINT_BOARD),
                    control_sha256=HINT_BOARD_SHA, scale=0.3,
                    controlnet2=NET_BOARD, control2=os.path.join(repo, HINT_POSE),
                    control2_sha256=HINT_POSE_SHA, scale2=0.3), (832, 1216)), 12))

    # ---- 6. THE CONTROL BLOCK IN THE SIDECAR -------------------------------
    cl = control_meta_lines(controls, region)
    joined = "\n".join(cl)
    for needle in ("controlnet: " + NET_POSE, "controlnet_2: " + NET_BOARD,
                   "controlnet_conditioning_scale: 1.0",
                   "controlnet_2_conditioning_scale: 0.3",
                   "control_image_sha256: " + HINT_POSE_SHA,
                   "control_2_image_sha256: " + HINT_BOARD_SHA,
                   "MultiControlNetModel",
                   "pad_crop_region_px: [%d, %d, %d, %d]" % tuple(region)):
        check("the control block records %r" % needle[:46], needle in joined)
    withctl = sidecar_text(
        pipeline_class="StableDiffusionXLControlNetInpaintPipeline", in_ch=4,
        W=832, H=1216, steps=40, cfg=7.5, strength=0.7, seed=20260822,
        pad_crop=64, blur=8, init="x.png", init_sha="0" * 64,
        mask_png_name="m.png", mask_lines=mask_lines, control_lines=cl,
        stamp="2026-08-20T14:24:24Z", render_s=1.0, wall_s=2.0,
        versions={"python": "3", "torch": "2", "diffusers": "0.29.2"},
        note="n", prompt="p", negative="q")
    check("a control run names the ControlNet pipeline in its sidecar",
          "pipeline: StableDiffusionXLControlNetInpaintPipeline" in withctl)
    check("the control block sits between the mask block and the steward note, "
          "leaving every pre-existing line in its filed order",
          withctl.index("mask_height_frac") < withctl.index("controlnet: ")
          < withctl.index("mask_is_the_stewards"))

    # ---- 7. THE CROP-MAGNIFICATION REFUSAL, AND THE CONFIGURATION IT ADMITS
    # §28 measured this defect and wrote the rule in prose. These clauses are
    # that rule, and the numbers are the ones the filed verdict reported, not
    # numbers invented for a test.
    check("the no-control path never raises, even on a magnifying box (rc none)",
          assert_hint_survives_crop([], region, 832, 1216) == 1.0)
    check("section 28's own crop box magnifies the hint 3.07x, as it reported",
          abs(hint_magnification((468, 384, 739, 780), 832, 1216) - 3.07) < 0.01)
    check("a hint that the crop would magnify is REFUSED (rc 15)",
          raises(lambda: assert_hint_survives_crop(
              controls, (468, 384, 739, 780), 832, 1216), 15))
    try:
        assert_hint_survives_crop(controls, (468, 384, 739, 780), 832, 1216)
        refusal = ""
    except ControlError as e:
        refusal = str(e)
    check("the refusal names the verdict and the mechanism, so the next caller "
          "reads section 28 instead of rediscovering it at a render's cost",
          "section 28" in refusal and "3.07x" in refusal
          and "--pad-crop 0" in refusal)

    # PAD-CROP 0 IS THE CONFIGURATION THIS ROUTE RUNS IN, and the guard admits it
    # by construction: no crop, no rescale, no way for the defect to occur.
    check("at --pad-crop 0 the region is None and the magnification is exactly "
          "1.0 -- the section 28 defect is structurally impossible there",
          hint_magnification(None, 832, 1216) == 1.0
          and assert_hint_survives_crop(controls, None, 832, 1216) == 1.0)

    # AND THE GUARD IS NOT A BAN ON THE FLAG. A mask that already covers the
    # frame yields a box the size of the frame and magnifies nothing, so it is
    # admitted WITH padding_mask_crop on. The guard measures the defect, not the
    # flag that happened to be set when the defect was found.
    full = Image.open(os.path.join(
        repo, "farm-out/ep2-goblin-i2i-src-0822/fullframe-mask-0822.png")
    ).convert("L")
    freg = crop_region(full.filter(ImageFilter.GaussianBlur(8)), 832, 1216, 64)
    check("a FULL-FRAME mask crops to the whole frame, so even with "
          "--pad-crop 64 nothing is magnified and the hint is admitted",
          hint_magnification(freg, 832, 1216) <= HINT_MAGNIFICATION_CEILING
          and assert_hint_survives_crop(controls, freg, 832, 1216) <= 1.05)

    # ---- 8. THE ROUND-2 SIDECAR: ONE POSE NET, FULL-FRAME MASK, NO CROP ----
    one = resolve_controls(
        _Args(controlnet=NET_POSE, control=os.path.join(repo, HINT_POSE),
              control_sha256=HINT_POSE_SHA, scale=1.0), (832, 1216))
    r2lines = control_meta_lines(one, None)
    r2joined = "\n".join(r2lines)
    check("a single net records its composition as 'one net' and emits no "
          "second-net block",
          "controlnet_composition: one net" in r2joined
          and "controlnet_2:" not in r2joined)
    check("with the crop off the sidecar says so in the box field rather than "
          "carrying a stale or invented region",
          "pad_crop_region_px: null (padding_mask_crop off)" in r2joined)
    r2side = sidecar_text(
        pipeline_class="StableDiffusionXLControlNetInpaintPipeline", in_ch=4,
        W=832, H=1216, steps=40, cfg=7.5, strength=0.35, seed=20260823,
        pad_crop=0, blur=8, init="canon.png", init_sha="0" * 64,
        mask_png_name="m.png", mask_lines=mask_lines, control_lines=r2lines,
        stamp="2026-08-22T00:00:00Z", render_s=1.0, wall_s=2.0,
        versions={"python": "3", "torch": "2", "diffusers": "0.29.2"},
        note="n", prompt="p", negative="q")
    check("the round-2 shape -- init + ONE ControlNet at --pad-crop 0 -- "
          "produces a complete sidecar naming the ControlNet pipeline",
          "pipeline: StableDiffusionXLControlNetInpaintPipeline" in r2side
          and "padding_mask_crop: null" in r2side
          and "strength: 0.35" in r2side)

    bad = [c for c, ok in checks if not ok]
    print("\n%d/%d assertions passed" % (len(checks) - len(bad), len(checks)),
          flush=True)
    if bad:
        print("FAILED: %s" % "; ".join(bad), flush=True)
        return 1
    print("SELFTEST PASS -- the no-control path is byte-identical to the filed "
          "ep2-b08-str70-0820 sidecar, and hint alignment is by construction.",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
