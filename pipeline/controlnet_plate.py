#!/usr/bin/env python3
r"""Render a PLATE with an optional hand-authored scribble ControlNet condition.

WHAT THIS IS AND WHY IT IS A SEPARATE FILE FROM THE PROBE.
`pipeline/controlnet_probe.py` answered "does the condition BIND on
animagine-xl-3.1?" and its answer is filed: bind_ratio 35.363 left / 21.530
right against a bar of 1.25 that was written in code before any pixels existed
(`pipeline/jobs/ep2-cnet-probe-0817.yaml`, verdict appended 2026-08-19). That
file's prompt, size, seed and four arms are its OWN, deliberately not any beat's
wording, so that a drafting lane could never collide with it -- and its verdict
is filed against those constants. Editing it to take a beat's prompt would
retroactively change what its own verdict was measured on.

So this is the probe's render path with its constants lifted into arguments,
and NOTHING ELSE IS DIFFERENT. Same base, same ControlNet, same variant trap,
same `from_pipe` module reuse, same sidecar shape. The pipeline this drives is
the one that was measured; only the words, the hint and the size are the
caller's.

WHAT IT DELIBERATELY DOES NOT DO: it does not pair a ControlNet with a MASK.
`b08-arm-route-0819.md` §4 Route B is a separate one-sample question with its
own bar -- no driver in this tree does control-plus-inpaint, and the probe's
`observed_not_scored` (a sparse hint at scale 0.8 FLATTENS THE WHOLE FRAME) is
precisely the failure that would show up outside such a mask. It must not be
smuggled in as an implementation detail of a beat job, so it is not here.

NO VIDEO, NO ENCODER, NO CRF ANYWHERE. This writes a PNG. (Stated because a
peer lane measured --image-crf 33 destroying i2v conditioning on 2026-08-19;
no value from any motion recipe is inherited by this path.)

    python3 pipeline/controlnet_plate.py --arm hint --control C.png \
        --prompt-file p.txt --negative-file n.txt --out DIR --task ep2-x-0819
    python3 pipeline/controlnet_plate.py --selftest        # no GPU, no weights
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

BASE = "cagliostrolab/animagine-xl-3.1"
BASE_LICENCE = "CreativeML Open RAIL++-M (use restrictions travel; D15)"

# Apache-2.0 and already complete in the box cache. MistoLine would also work
# but its README puts a standing visible-attribution obligation on anything it
# renders, so the permissive net is the default. Same choice as the probe's.
CONTROLNET = "xinsir/controlnet-scribble-sdxl-1.0"
CONTROLNET_LICENCE = "apache-2.0 (D15 SAFE, no attribution condition)"

# WHICH NETS MAY BE NAMED, AND WHY IT IS AN ALLOWLIST RATHER THAN A FREE STRING.
# `--controlnet` exists so the openpose rung can run WITHOUT editing the constant
# above, which four filed verdicts were measured against. But a driver that
# accepts any repo id by string is one typo away from attaching somebody else's
# terms to a canon frame, and two of the near neighbours are real hazards:
#   thibaud/controlnet-openpose-sdxl-1.0 -- its card reads, in full, "License:
#     refers to the OpenPose's one". CMU OpenPose upstream is academic /
#     non-commercial. B01-R9-PLAN.md §9 already flags lllyasviel/Annotators DO
#     NOT USE FOR CANON for inheriting exactly those terms; this inherits them at
#     the WEIGHTS level, where they would attach to every frame it ever renders.
#   MistoLine -- loads fine, but its README puts a standing VISIBLE ATTRIBUTION
#     obligation on anything it renders. That is why the permissive net was the
#     default in the first place.
# So the licence travels WITH the name, in one table, and an unlisted net is
# refused before any weight loads rather than silently recorded as apache-2.0.
CONTROLNETS = {
    "xinsir/controlnet-scribble-sdxl-1.0":
        "apache-2.0 (D15 SAFE, no attribution condition)",
    "xinsir/controlnet-openpose-sdxl-1.0":
        "apache-2.0 (D15 SAFE, no attribution condition; front matter and body "
        "both, and no annotator is used -- the hint is authored in PIL)",
    # A PATH, IN A TABLE OF REPO IDS, AND THAT NEEDS ITS REASON STATED.
    # xinsir ships the `twins` variant as a SECOND blob inside the openpose repo,
    # `diffusion_pytorch_model_twins.safetensors`. from_pretrained cannot load a
    # weight by filename, so ep2-b08-twins-fetch-0819 renamed our own copy into a
    # loadable directory -- which means the only name this driver ever sees for
    # those weights is a local path, and a path carries no terms. Rather than
    # weaken the guard (the guard is right: thibaud's SDXL openpose inherits CMU
    # OpenPose's non-commercial licence at the weights level), the path is
    # allowlisted with a licence string that NAMES ITS UPSTREAM, its variant
    # filename and its digest -- so the sidecar it writes is self-describing even
    # though the net's name is a directory. Same repo, same apache-2.0, verified
    # by the fetch on both front matter and body.
    r"C:\banyan-farm\cnet-openpose-twins":
        "apache-2.0 (D15 SAFE, no attribution condition) -- the `twins` variant "
        "of xinsir/controlnet-openpose-sdxl-1.0, blob "
        "diffusion_pytorch_model_twins.safetensors sha256 "
        "54a2afb1bd21349e475566e5428884bc937a4caecf863b29dea08acc40612fa4, "
        "2502139104 bytes, renamed into a loadable directory by "
        "ep2-b08-twins-fetch-0819. Identical terms to the default weight in that "
        "same repo; no annotator is used -- the hint is authored in PIL",
}

# THE VARIANT TRAP, carried verbatim because it is why a naive constant-swap
# crashes: the xinsir repos ship ONLY `diffusion_pytorch_model.safetensors`, so
# passing variant="fp16" raises. diffusers/* and MistoLine ship ONLY
# `*.fp16.safetensors`, so OMITTING it raises. Verified against the box's
# snapshot listing, not assumed.
CONTROLNET_VARIANT = None

W, H = 832, 1216          # beat 01's proven size, and the size the probe bound at
STEPS = 40
CFG = 7.5
SCALE = 0.8               # thick-line + high-scale: the condition-wins end, and
                          # the ONLY conditioning scale this repo has measured.

# ---------------------------------------------------------------------------
# MASKED IP-ADAPTER -- ADDED 2026-08-19, AND EVERY PATH ABOVE IS UNCHANGED.
#
# WHY IT IS HERE. `b08-arm-route-0819.md` §8-§10 bracketed conditioning scale,
# stroke weight and hint class over five rungs and every single frame returned
# TWO GREEN FIGURES. That is not a tuning failure: a contour says how tall, not
# WHICH BODY an attribute belongs to, so `green skin` enters CLIP's pooled
# embedding and lands on both. §10's closing line is that identity is no longer
# blocked, it is simply the next open question, and that geometric conditioning
# on this net will not help it. A reference image behind a MASK is a per-location
# identity channel, which is the one thing the hint cannot be.
#
# WHY IT COSTS NOTHING AND NEEDS NO DOWNLOAD, verified read-only on the box by
# `pipeline/research/openpose-controlnet-sdxl-0819.md` §3 and §5 rather than
# assumed here: diffusers 0.29.2, `IPAdapterMaskProcessor` imports,
# `StableDiffusionXLControlNetPipeline.__call__` accepts `ip_adapter_image`, and
# `models--h94--IP-Adapter` is complete in the cache with 0 .incomplete files.
# One pipeline, pose control AND per-region image conditioning; no community
# pipeline, no fork, no version bump.
#
# THE ENCODER FOLDER IS THE TRAP THAT WOULD HAVE COST THE FIRST RUN. diffusers
# defaults `image_encoder_folder="image_encoder"` and, when the name contains no
# slash, resolves it as `Path(subfolder, image_encoder_folder)` -- i.e.
# `sdxl_models/image_encoder`, which is the ViT-bigG encoder and IS NOT IN THE
# BOX CACHE. `dir /s /b` on the snapshot lists exactly four blobs and the only
# encoder among them is `models/image_encoder`, the ViT-H one that every
# `_vit-h` adapter actually requires. A name WITH a slash is taken as a full
# path, so `models/image_encoder` is both correct and the only offline-reachable
# spelling. Getting this wrong is not a wrong picture, it is a hard miss under
# HF_HUB_OFFLINE=1.
# ---------------------------------------------------------------------------
IP_REPO = "h94/IP-Adapter"
IP_LICENCE = "apache-2.0"
IP_SUBFOLDER = "sdxl_models"
IP_WEIGHT = "ip-adapter-plus_sdxl_vit-h.safetensors"
IP_IMAGE_ENCODER_FOLDER = "models/image_encoder"   # see the trap above
IP_SCALE = 0.7            # the value diffusers' own masking example uses



def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_rev(root):
    try:
        # encoding named explicitly: a text-mode read that defaults to the
        # platform codec decodes as cp1252 on the box, and test_pipeline.py
        # enforces this repo-wide.
        return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                              capture_output=True, text=True, encoding="utf-8",
                              timeout=20).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def read_text(path):
    """A prompt file, stripped of a trailing newline and nothing else.

    Read as utf-8 by name. The box's default codec is cp1252 and a prompt that
    round-trips through it silently loses any character outside latin-1 -- which
    is how a wording measured here stops being the wording rendered there.
    """
    s = Path(path).read_text(encoding="utf-8").strip()
    if not s:
        raise ValueError("%s is empty -- refusing to render a blank prompt" % path)
    return s


def token_overflow(text, tokenizer):
    """How many tokens past CLIP's 77 this text runs, measured not estimated.

    WHY THIS REFUSES INSTEAD OF WARNING. diffusers truncates silently at
    `model_max_length`, and what falls off the end is the TAIL -- which in this
    repo's drafts is always the style anchor (`masterpiece, best quality, very
    aesthetic`). A plate rendered with the anchor amputated does not look like a
    truncation, it looks like the recipe failed, and that is a whole round spent
    on a diagnosis that was available for free before the first step.
    `insert_b08_cast_draft_0817.py` gave up an entire clause -- `hedgerow` --
    precisely to keep the anchor, so losing it by accident here would throw away
    somebody else's measured decision.

    Checked against the REAL tokenizer on the box. This machine has none
    (`sd_prompt._clip_tokenizer()` returns None here), so an authoring-time
    number is an estimate and only the box can make it a fact.
    """
    limit = getattr(tokenizer, "model_max_length", 77)
    n = len(tokenizer(text)["input_ids"])
    return max(0, n - limit), n, limit


def check_control(ctrl_img, want_w, want_h):
    """The control must be the render size EXACTLY, or the geometry is a lie.

    diffusers will happily resize a mismatched condition, and then the pose that
    was authored -- the feet on one ground line, the fingertip short of the
    belly -- is not the pose the model saw. Refusing is the whole point; this is
    the probe's rc=7 guard, kept.
    """
    if ctrl_img.size != (want_w, want_h):
        raise ValueError(
            "control is %s but the render is %s. diffusers would resize it and "
            "the authored geometry would not be the geometry the model saw. "
            "Re-author the hint at the render size."
            % (ctrl_img.size, (want_w, want_h)))
    return True


def parse_rect(s, width, height):
    """`x0,y0,x1,y1` in RENDER pixels -> a validated tuple.

    In render pixels and not fractions on purpose: the hint that these masks
    accompany is authored in absolute pixels by `author_b08_pose_hint.py`, whose
    metadata reports the figures' cx, stature, head_cy and shoulder_y in exactly
    those units. A fraction here would mean the mask and the geometry it is meant
    to agree with are stated in two different coordinate systems, and nobody
    would notice a 4% disagreement by eye.
    """
    parts = [p.strip() for p in str(s).split(",")]
    if len(parts) != 4:
        raise ValueError("a mask rect is x0,y0,x1,y1 -- got %r" % (s,))
    try:
        x0, y0, x1, y1 = (int(round(float(p))) for p in parts)
    except ValueError:
        raise ValueError("a mask rect must be four numbers -- got %r" % (s,))
    if x1 <= x0 or y1 <= y0:
        raise ValueError("mask rect %r is empty or inverted (need x1>x0, y1>y0)"
                         % (s,))
    if x0 < 0 or y0 < 0 or x1 > width or y1 > height:
        raise ValueError("mask rect %r falls outside the %dx%d render" %
                         (s, width, height))
    return (x0, y0, x1, y1)


def rects_overlap(a, b):
    """Do two mask rects share any pixel?

    REFUSED rather than warned about. Two IP-Adapter masks that overlap put two
    identities on the same pixels, and the whole premise of this rung is that
    each figure gets ONE reference. An overlap would produce exactly the blended
    result the rung exists to disprove, and it would look like the mechanism
    failing rather than like the masks being wrong.
    """
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def mask_images(rects, width, height):
    """One white-on-black L mask per rect, at the render size.

    Drawn here rather than taken as PNG files so the numbers in the job's argv
    ARE the mask -- there is no second artifact that could drift from them, and
    the sidecar records the same four integers the render was conditioned on.
    """
    from PIL import Image, ImageDraw
    out = []
    for r in rects:
        m = Image.new("L", (width, height), 0)
        ImageDraw.Draw(m).rectangle([r[0], r[1], r[2] - 1, r[3] - 1], fill=255)
        out.append(m)
    return out


def sidecar_lines(a, use_cn, ctrl_sha, rev, prompt, negative, load_s, render_s,
                  stamp, torch_version, ip=None):
    """The 7.2 provenance block, written AT RENDER TIME, on the box."""
    side = [
        "# Provenance (7.2), written AT RENDER TIME by controlnet_plate.py on",
        "# the rtx5090. A SAMPLE, not a pick and not canon.",
        "platform: local-gpu (rtx5090)",
        "task: %s" % a.task,
        "arm: %s" % a.arm,
        "model: %s" % BASE,
        "model_licence: %s" % BASE_LICENCE,
        ("pipeline: StableDiffusionXLControlNetPipeline (text2img + scribble control)"
         if use_cn else "pipeline: StableDiffusionXLPipeline (text2img, NO control)"),
        "size: %dx%d" % (a.width, a.height),
        "steps: %d" % a.steps,
        "guidance: %s" % a.cfg,
        "seed: %d" % a.seed,
        "cost_usd: 0",
    ]
    if use_cn:
        # getattr with the constant as the default, so a caller that predates
        # --controlnet produces the byte-identical block it always did.
        net = getattr(a, "controlnet", None) or CONTROLNET
        side += [
            "controlnet: %s" % net,
            "controlnet_licence: %s" % CONTROLNETS.get(net, CONTROLNET_LICENCE),
            "controlnet_variant: %r (xinsir ships no fp16 variant file; passing "
            "one raises)" % CONTROLNET_VARIANT,
            "controlnet_conditioning_scale: %s" % a.scale,
            "control_guidance_start: 0.0",
            "control_guidance_end: 1.0",
            "control_image: %s" % a.control,
            "control_image_sha256: %s" % ctrl_sha,
            "control_polarity: white-on-black",
            "control_authored_by: pipeline/author_b08_pose_hint.py (PIL, no "
            "model, no photo-derived edge map, no annotator)",
        ]
    else:
        side.append("controlnet: none (the control arm; same seed, same prompt)")
    # ONLY WHEN AN IP-ADAPTER WAS ACTUALLY USED. An arm that ran without one must
    # produce the byte-identical sidecar it produced before this feature existed,
    # and selftest() asserts that against a sha taken from the pre-change file --
    # otherwise four filed verdicts would be resting on a provenance block whose
    # wording had quietly moved under them.
    if ip:
        side += [
            "ip_adapter: %s (%s)" % (ip["repo"], ip["licence"]),
            "ip_adapter_weight: %s/%s" % (ip["subfolder"], ip["weight"]),
            "ip_adapter_image_encoder: %s (ViT-H; the folder the _vit-h adapters "
            "require, and the only encoder in the box cache)"
            % ip["image_encoder_folder"],
            "ip_adapter_scale: %s" % (ip["scale"],),
            "ip_adapter_refs: %s" % (ip["refs"],),
            "ip_adapter_ref_sha256: %s" % (ip["ref_sha256"],),
            "ip_adapter_masks: %s (x0,y0,x1,y1 in RENDER pixels, drawn by "
            "controlnet_plate.mask_images -- no mask file exists to drift)"
            % (ip["rects"],),
            "ip_adapter_masks_overlap: false (asserted; two identities on one "
            "pixel is refused, not warned about)",
        ]
    side += [
        "repo_commit: %s" % rev,
        "model_load_seconds: %.1f" % load_s,
        "render_seconds: %.1f" % render_s,
        "rendered_utc: %s" % stamp,
        "torch_version: %s" % torch_version,
        "approved: false",
        "provisional: >-",
        "  PROVISIONAL. A steward-rendered SAMPLE, not a pick and not canon.",
        "  Never takes a canon filename, is not published to the site, not",
        "  posted, and not assembled into an episode. Ground truth is the",
        "  founder (R4).",
        "prompt: |-",
    ]
    side += ["  " + ln for ln in prompt.splitlines()]
    side.append("negative: |-")
    side += ["  " + ln for ln in negative.splitlines()]
    return side


def render(a):
    import torch
    from PIL import Image

    root = Path(a.root) if a.root else REPO
    use_cn = a.arm != "nocontrol"

    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_png = out_dir / ("%s-%s.png" % (a.task, a.arm))

    prompt = read_text(a.prompt_file)
    negative = read_text(a.negative_file)

    # ---- the IP-Adapter references and their masks, RESOLVED BEFORE ANY WEIGHT
    # LOADS. A missing reference, a bad rect or an overlap costs three seconds
    # here and a whole model load plus a 40-step render if it is found later.
    ip = None
    if a.ip_ref:
        if len(a.ip_ref) != len(a.ip_mask):
            print("!! %d --ip-ref but %d --ip-mask. Each reference needs exactly "
                  "one mask: the mask is what says WHICH FIGURE that reference is "
                  "for, and an unmasked reference applies to the whole frame -- "
                  "which is the broadcast failure this rung exists to fix."
                  % (len(a.ip_ref), len(a.ip_mask)), file=sys.stderr)
            return 10
        if a.ip_ref_sha256 and len(a.ip_ref_sha256) != len(a.ip_ref):
            print("!! %d --ip-ref-sha256 for %d --ip-ref"
                  % (len(a.ip_ref_sha256), len(a.ip_ref)), file=sys.stderr)
            return 10
        try:
            rects = [parse_rect(s, a.width, a.height) for s in a.ip_mask]
        except ValueError as e:
            print("!! %s" % e, file=sys.stderr)
            return 10
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                if rects_overlap(rects[i], rects[j]):
                    print("!! mask %d %s and mask %d %s OVERLAP. Two references "
                          "on the same pixels is two identities on one body, and "
                          "the blended result would look like the mechanism "
                          "failing rather than like the masks being wrong."
                          % (i, rects[i], j, rects[j]), file=sys.stderr)
                    return 10
        ref_paths, ref_shas = [], []
        for i, r in enumerate(a.ip_ref):
            rp = Path(r)
            if not rp.is_absolute():
                rp = root / r
            if not rp.exists():
                print("ip reference missing: %s" % rp, file=sys.stderr)
                return 10
            sha = sha256_file(rp)
            if a.ip_ref_sha256 and sha != a.ip_ref_sha256[i]:
                print("!! ip reference %d sha mismatch\n   want %s\n   have %s"
                      % (i, a.ip_ref_sha256[i], sha), file=sys.stderr)
                return 11
            ref_paths.append(rp)
            ref_shas.append(sha)
        ip = {"repo": a.ip_repo, "licence": IP_LICENCE,
              "subfolder": a.ip_subfolder, "weight": a.ip_weight,
              "image_encoder_folder": a.ip_image_encoder_folder,
              "scale": [[float(a.ip_scale)] * len(ref_paths)],
              "refs": [str(p) for p in ref_paths], "ref_sha256": ref_shas,
              "rects": rects, "paths": ref_paths}

    ctrl_img = None
    ctrl_sha = None
    if use_cn:
        if not a.control:
            print("--control is required for a control arm", file=sys.stderr)
            return 6
        cp = Path(a.control)
        if not cp.is_absolute():
            cp = root / a.control
        if not cp.exists():
            print("control hint missing: %s" % cp, file=sys.stderr)
            return 6
        ctrl_sha = sha256_file(cp)
        if a.control_sha256 and ctrl_sha != a.control_sha256:
            print("!! control sha mismatch\n   want %s\n   have %s"
                  % (a.control_sha256, ctrl_sha), file=sys.stderr)
            return 8
        ctrl_img = Image.open(cp).convert("RGB")
        try:
            check_control(ctrl_img, a.width, a.height)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 7

    net = a.controlnet or CONTROLNET
    if use_cn and net not in CONTROLNETS:
        print("!! %r is not in this driver's ControlNet allowlist. The licence "
              "travels with the name (see CONTROLNETS), and an unlisted net "
              "would be recorded with the wrong terms -- thibaud's SDXL openpose "
              "inherits CMU OpenPose's non-commercial licence AT THE WEIGHTS "
              "LEVEL, and MistoLine puts a standing visible-attribution "
              "obligation on anything it renders. Add it to the table with its "
              "real licence, or use one of: %s"
              % (net, ", ".join(sorted(CONTROLNETS))), file=sys.stderr)
        return 12

    if not torch.cuda.is_available():
        print("no CUDA -- this is a box job", file=sys.stderr)
        return 5

    # BEFORE any weights load, so a wording that cannot fit costs 3 seconds and
    # not a 40-step render on a card another lane is waiting for.
    if not a.allow_truncation:
        from transformers import CLIPTokenizer
        tok = CLIPTokenizer.from_pretrained(BASE, subfolder="tokenizer")
        for label, text in (("prompt", prompt), ("negative", negative)):
            over, n, limit = token_overflow(text, tok)
            print("  %s tokens: %d (limit %d)" % (label, n, limit), flush=True)
            if over:
                print("!! the %s runs %d tokens past CLIP's %d and diffusers would "
                      "TRUNCATE it silently. The tail of every draft in this repo "
                      "is the style anchor, so what gets dropped is exactly what "
                      "makes the plate look like the show. Shorten it, or pass "
                      "--allow-truncation if the overflow is deliberate."
                      % (label, over, limit), file=sys.stderr)
                return 9

    from diffusers import (AutoPipelineForText2Image, ControlNetModel,
                           StableDiffusionXLPipeline)

    t0 = datetime.datetime.now(datetime.timezone.utc)
    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE, torch_dtype=torch.bfloat16, use_safetensors=True)
    pipe.to("cuda")
    pipe.set_progress_bar_config(disable=True)

    kw = {}
    if use_cn:
        cn_kw = {} if CONTROLNET_VARIANT is None else {"variant": CONTROLNET_VARIANT}
        cn = ControlNetModel.from_pretrained(
            net, torch_dtype=torch.bfloat16, **cn_kw)
        cn.to("cuda")
        # from_pipe swaps the class while REUSING the loaded modules, so one set
        # of base weights serves both arms -- r8/r9's discipline.
        pipe = AutoPipelineForText2Image.from_pipe(pipe, controlnet=cn)
        kw = {"image": ctrl_img,
              "controlnet_conditioning_scale": float(a.scale),
              "control_guidance_start": 0.0,
              "control_guidance_end": 1.0}

    # ---- MASKED IP-ADAPTER, LOADED ONTO THE FINAL PIPELINE ----------------
    # AFTER the from_pipe swap, deliberately. from_pipe rebuilds the class around
    # the same modules, and an adapter registered on the pre-swap object is
    # registered on a pipeline nobody is about to call.
    if ip:
        from diffusers.image_processor import IPAdapterMaskProcessor
        from PIL import Image as _Image

        pipe.load_ip_adapter(
            ip["repo"], subfolder=ip["subfolder"], weight_name=ip["weight"],
            image_encoder_folder=ip["image_encoder_folder"])
        # ONE adapter carrying N images, so the scale is ONE nested list of N --
        # the shape diffusers' own masking example uses, and the shape the attn
        # processor demands: it asserts
        # len(ip_adapter_masks) == len(self.scale) == len(ip_hidden_states),
        # where len(self.scale) counts ADAPTERS (1) and each entry may itself be
        # a per-image list.
        pipe.set_ip_adapter_scale(ip["scale"])
        proc = IPAdapterMaskProcessor()
        masks = proc.preprocess(mask_images(ip["rects"], a.width, a.height),
                                height=a.height, width=a.width)
        # The reshape is not cosmetic: each element of ip_adapter_masks must be
        # a tensor of [1, num_images_for_this_adapter, h, w]. preprocess returns
        # [N, 1, h, w], so it is folded into a single [1, N, h, w] and wrapped in
        # a one-element list -- one entry for the one adapter.
        masks = [masks.reshape(1, masks.shape[0], masks.shape[2], masks.shape[3])]
        refs = [[_Image.open(p).convert("RGB") for p in ip["paths"]]]
        kw["ip_adapter_image"] = refs
        kw["cross_attention_kwargs"] = {"ip_adapter_masks": masks}
        print("  ip-adapter: %s/%s, %d ref(s), scale %s, masks %s"
              % (ip["subfolder"], ip["weight"], len(ip["paths"]), ip["scale"],
                 ip["rects"]), flush=True)

    g = torch.Generator("cuda").manual_seed(a.seed)
    t1 = datetime.datetime.now(datetime.timezone.utc)
    img = pipe(prompt=prompt, negative_prompt=negative,
               width=a.width, height=a.height,
               num_inference_steps=a.steps, guidance_scale=a.cfg,
               generator=g, **kw).images[0]
    t2 = datetime.datetime.now(datetime.timezone.utc)
    img.save(out_png)

    # A LOOSE COPY IS NOT A GIT CHECKOUT. When the driver is staged outside a
    # checkout `git rev-parse` finds nothing and the sidecar would say
    # `unknown`, which is the exact defect B01-R9-PLAN.md's stage 1 shipped --
    # so the caller passes the commit its copy was cut from.
    rev = a.repo_commit or git_rev(root)
    side = sidecar_lines(a, use_cn, ctrl_sha, rev, prompt, negative,
                         (t1 - t0).total_seconds(), (t2 - t1).total_seconds(),
                         t2.strftime("%Y-%m-%dT%H:%M:%SZ"), torch.__version__,
                         ip=ip)
    (out_dir / ("%s-%s.png.meta.yaml" % (a.task, a.arm))).write_text(
        "\n".join(side) + "\n", encoding="utf-8")

    print("OK %s load=%.1fs render=%.1fs"
          % (out_png.name, (t1 - t0).total_seconds(), (t2 - t1).total_seconds()),
          flush=True)
    print("rc=0", flush=True)
    return 0


def selftest():
    """Everything in this file that does not need a GPU. No torch, no weights."""
    import tempfile
    from PIL import Image
    fails = []

    def check(name, cond):
        print(("  ok   " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    # The size guard is the one that keeps the authored geometry honest.
    check("a control at the render size is accepted",
          check_control(Image.new("RGB", (W, H)), W, H))
    try:
        check_control(Image.new("RGB", (768, 1024)), W, H)
        check("a control at the WRONG size is refused", False)
    except ValueError:
        check("a control at the WRONG size is refused", True)

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "p.txt"
        p.write_text("  a guard points at a goblin  \n", encoding="utf-8")
        check("a prompt file is read and stripped",
              read_text(p) == "a guard points at a goblin")
        e = Path(td) / "e.txt"
        e.write_text("   \n\n", encoding="utf-8")
        try:
            read_text(e)
            check("an EMPTY prompt file is refused", False)
        except ValueError:
            check("an EMPTY prompt file is refused", True)
        # utf-8 by name, not by platform default -- the box is cp1252.
        u = Path(td) / "u.txt"
        u.write_text("arm’s length apart", encoding="utf-8")
        check("utf-8 survives the read", read_text(u).endswith("length apart"))

        # The sidecar must name the control arm's conditioning honestly, and
        # must NOT claim a ControlNet on the arm that had none.
        ap = argparse.Namespace(
            task="t", arm="hint", width=W, height=H, steps=STEPS, cfg=CFG,
            seed=1, scale=SCALE, control="c.png", control_sha256=None,
            root=None, repo_commit="abc", out=td, prompt_file=str(p),
            negative_file=str(p))
        s = "\n".join(sidecar_lines(ap, True, "deadbeef", "abc", "pos", "neg",
                                    1.0, 2.0, "now", "2.4"))
        check("a control arm's sidecar names the net and its scale",
              CONTROLNET in s and "controlnet_conditioning_scale: 0.8" in s)
        check("a control arm's sidecar carries the hint's sha",
              "control_image_sha256: deadbeef" in s)
        ap.arm = "nocontrol"
        s0 = "\n".join(sidecar_lines(ap, False, None, "abc", "pos", "neg",
                                     1.0, 2.0, "now", "2.4"))
        check("the nocontrol arm's sidecar claims NO controlnet",
              "controlnet: none" in s0 and CONTROLNET not in s0)
        check("every sidecar says approved: false", "approved: false" in s
              and "approved: false" in s0)
        check("cost is recorded and is zero", "cost_usd: 0" in s0)

        # ---- THE IP-ADAPTER FEATURE MAY NOT MOVE THE OLD PATHS -------------
        # Rungs 1, 2, 4 and 5 have FILED VERDICTS resting on frames this file
        # rendered, and their sidecars are the provenance those verdicts cite. So
        # the no-IP sidecar is asserted BYTE-IDENTICAL to what it was before the
        # feature landed, on a sha256 taken from the pre-change file at
        # 80dc35dc -- not eyeballed, and not merely "contains no ip_ lines".
        GOLDEN_CN = ("de46c2b340256a9e866e5d6d80a1cd18"
                     "9f5830e71bae379b3d44875c0feb4e3d")
        GOLDEN_NOCN = ("4f057ef052a7ebb7d2312cca1dc7ef41"
                       "e114bb3981cc1656205dbb767cb7f59f")
        check("a control arm's sidecar is BYTE-IDENTICAL to the pre-IP-Adapter "
              "file's", hashlib.sha256(s.encode()).hexdigest() == GOLDEN_CN)
        check("the nocontrol arm's sidecar is BYTE-IDENTICAL to the "
              "pre-IP-Adapter file's",
              hashlib.sha256(s0.encode()).hexdigest() == GOLDEN_NOCN)
        check("no ip_adapter line appears when no reference was passed",
              "ip_adapter" not in s and "ip_adapter" not in s0)

        # And when one IS passed, the sidecar names every part of it, because a
        # frame whose identity came from a reference and does not say so is a
        # 7.2 provenance failure.
        ipm = {"repo": IP_REPO, "licence": IP_LICENCE, "subfolder": IP_SUBFOLDER,
               "weight": IP_WEIGHT,
               "image_encoder_folder": IP_IMAGE_ENCODER_FOLDER,
               "scale": [[0.7, 0.7]], "refs": ["g.png", "o.png"],
               "ref_sha256": ["aa", "bb"],
               "rects": [(1, 2, 3, 4), (5, 6, 7, 8)]}
        ap.arm = "hint"
        si = "\n".join(sidecar_lines(ap, True, "deadbeef", "abc", "pos", "neg",
                                     1.0, 2.0, "now", "2.4", ip=ipm))
        for needle in (IP_REPO, IP_WEIGHT, IP_IMAGE_ENCODER_FOLDER,
                       "[[0.7, 0.7]]", "aa", "bb", "(1, 2, 3, 4)"):
            check("the IP sidecar records %r" % needle, needle in si)
        check("the IP sidecar still carries the ControlNet block too",
              CONTROLNET in si and "controlnet_conditioning_scale" in si)

    # The token guard, against a stand-in with CLIP's shape. The real tokenizer
    # is only on the box; what is testable here is that the arithmetic refuses
    # an overflow and passes a fit, and that it reads the limit off the
    # tokenizer rather than hardcoding one.
    class _Tok:
        model_max_length = 77

        def __init__(self, n):
            self.n = n

        def __call__(self, text):
            return {"input_ids": list(range(self.n))}

    over, n, limit = token_overflow("x", _Tok(90))
    check("a prompt past 77 tokens reports its overflow", (over, n, limit) == (13, 90, 77))
    check("a prompt that fits reports no overflow", token_overflow("x", _Tok(68))[0] == 0)
    check("exactly at the limit is not an overflow", token_overflow("x", _Tok(77))[0] == 0)

    class _Tok88(_Tok):
        model_max_length = 88
    check("the limit is read off the tokenizer, not hardcoded",
          token_overflow("x", _Tok88(80))[0] == 0)

    # ---- THE CONTROLNET ALLOWLIST -----------------------------------------
    # The licence has to travel WITH the name, or a net swap records the wrong
    # terms on every frame it renders.
    check("the default net is in the allowlist", CONTROLNET in CONTROLNETS)
    check("the allowlist's entry for the default net IS the default licence",
          CONTROLNETS[CONTROLNET] == CONTROLNET_LICENCE)
    check("the openpose net is in the allowlist",
          "xinsir/controlnet-openpose-sdxl-1.0" in CONTROLNETS)
    check("every allowlisted net is apache-2.0 -- no attribution condition and "
          "no inherited non-commercial terms",
          all(v.startswith("apache-2.0") for v in CONTROLNETS.values()))
    # The twins entry is a PATH, so its licence string is the only place a reader
    # can learn what it is. Assert it says so, or the guard passes a net whose
    # provenance block names a directory on one machine and nothing else.
    _twins = r"C:\banyan-farm\cnet-openpose-twins"
    check("the twins variant dir is allowlisted", _twins in CONTROLNETS)
    check("the twins entry names its upstream repo, variant blob and digest",
          all(s in CONTROLNETS[_twins] for s in
              ("xinsir/controlnet-openpose-sdxl-1.0",
               "diffusion_pytorch_model_twins.safetensors",
               "54a2afb1bd21349e475566e5428884bc937a4caecf863b29dea08acc40612fa4")))
    for hazard in ("thibaud/controlnet-openpose-sdxl-1.0",
                   "TheMistoAI/MistoLine",
                   "xinsir/controlnet-union-sdxl-1.0",
                   "lllyasviel/Annotators"):
        check("%s is NOT allowlisted" % hazard, hazard not in CONTROLNETS)
    # The sidecar must name whatever net was passed, with THAT net's licence.
    ap2 = argparse.Namespace(
        task="t", arm="hint", width=W, height=H, steps=STEPS, cfg=CFG, seed=1,
        scale=SCALE, control="c.png", control_sha256=None, root=None,
        repo_commit="abc", out=".", prompt_file="p", negative_file="n",
        controlnet="xinsir/controlnet-openpose-sdxl-1.0")
    sp = "\n".join(sidecar_lines(ap2, True, "dead", "abc", "p", "n", 1.0, 2.0,
                                 "now", "2.4"))
    check("a pose-net sidecar names the POSE net and not the scribble one",
          "controlnet: xinsir/controlnet-openpose-sdxl-1.0" in sp
          and CONTROLNET not in sp)
    check("a pose-net sidecar carries the pose net's own licence line",
          "no annotator is used" in sp)

    # ---- THE MASK GRAMMAR -------------------------------------------------
    check("a rect parses to four ints in render pixels",
          parse_rect(" 10, 20 ,30,40 ", W, H) == (10, 20, 30, 40))
    check("a float rect rounds rather than truncating",
          parse_rect("10.6,20,30,40", W, H) == (11, 20, 30, 40))
    for bad in ("1,2,3", "1,2,3,4,5", "a,2,3,4", "30,20,10,40", "10,40,30,20",
                "10,20,10,40", "-1,0,10,20", "0,0,%d,20" % (W + 1),
                "0,0,20,%d" % (H + 1)):
        try:
            parse_rect(bad, W, H)
            check("refuses rect %r" % bad, False)
        except ValueError:
            check("refuses rect %r" % bad, True)
    check("a rect filling the frame exactly is accepted",
          parse_rect("0,0,%d,%d" % (W, H), W, H) == (0, 0, W, H))

    # Overlap is the failure that would look like the MECHANISM failing.
    check("adjacent rects sharing an edge do NOT overlap",
          not rects_overlap((0, 0, 10, 10), (10, 0, 20, 10)))
    check("rects sharing one pixel DO overlap",
          rects_overlap((0, 0, 11, 10), (10, 0, 20, 10)))
    check("stacked rects sharing a row overlap",
          rects_overlap((0, 0, 10, 11), (0, 10, 10, 20)))
    check("disjoint rects do not overlap",
          not rects_overlap((0, 0, 10, 10), (50, 50, 60, 60)))

    # And the drawn mask has to be the rect, at the render size, or the region
    # the model is conditioned on is not the region that was specified.
    ms = mask_images([(100, 200, 300, 500)], W, H)
    check("one mask per rect, at the render size",
          len(ms) == 1 and ms[0].size == (W, H) and ms[0].mode == "L")
    px = ms[0].load()
    check("the mask is white INSIDE the rect", px[100, 200] == 255
          and px[299, 499] == 255 and px[200, 350] == 255)
    check("the mask is black OUTSIDE the rect", px[99, 200] == 0
          and px[300, 499] == 0 and px[100, 199] == 0 and px[0, 0] == 0)
    lit = sum(ms[0].histogram()[128:])
    check("the mask's lit area is exactly the rect's (%d px)" % lit,
          lit == (300 - 100) * (500 - 200))

    # A peer lane measured --image-crf 33 destroying i2v conditioning on
    # 2026-08-19 (crf 10 holds identity). Nothing here encodes video, and this
    # asserts it as code rather than as a promise in the docstring: no flag and
    # no keyword in this file is named crf, so no motion recipe's default can be
    # inherited by copy-paste without the assertion going red.
    # The needles are assembled at runtime rather than written out: spelled
    # literally, this check finds ITSELF in the source and fails a clean file.
    src = Path(__file__).read_text(encoding="utf-8").lower()
    stem = "c" + "rf"
    check("no argument or keyword in this file is named crf",
          not any(n in src for n in (stem + "=", "-" + stem + '"',
                                     "-" + stem + "'", "_" + stem)))

    print(("SELFTEST FAIL: %d" % len(fails)) if fails else "SELFTEST PASS")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description="text2img plate, optional scribble control")
    ap.add_argument("--arm", default=None,
                    help="arm name; 'nocontrol' renders WITHOUT the ControlNet")
    ap.add_argument("--task", default=None, help="task id; names the output png")
    ap.add_argument("--control", default=None, help="hint PNG (abs, or repo-relative)")
    ap.add_argument("--control-sha256", default=None,
                    help="assert the hint's bytes; a staged copy is not a checkout")
    ap.add_argument("--prompt-file", default=None)
    ap.add_argument("--negative-file", default=None)
    ap.add_argument("--out", default=None, help="output DIRECTORY (absolute)")
    ap.add_argument("--root", default=None)
    ap.add_argument("--controlnet", default=CONTROLNET,
                    help="ControlNet repo id; must be in the CONTROLNETS "
                         "allowlist, which carries each net's licence")
    ap.add_argument("--scale", type=float, default=SCALE)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--steps", type=int, default=STEPS)
    ap.add_argument("--cfg", type=float, default=CFG)
    ap.add_argument("--width", type=int, default=W)
    ap.add_argument("--height", type=int, default=H)
    ap.add_argument("--repo-commit", default=None,
                    help="commit this driver was cut from; required when it runs "
                         "as a loose copy outside a checkout, or the sidecar "
                         "records repo_commit: unknown")
    # ---- masked IP-Adapter (2026-08-19). Omit them all and every path above
    # behaves exactly as it did for rungs 1-5; selftest asserts that on a sha.
    ap.add_argument("--ip-ref", action="append", default=[],
                    help="identity reference image, once per figure (abs, or "
                         "repo-relative). Each one needs its own --ip-mask")
    ap.add_argument("--ip-mask", action="append", default=[],
                    help="x0,y0,x1,y1 in RENDER pixels for the matching "
                         "--ip-ref. Rects may not overlap")
    ap.add_argument("--ip-ref-sha256", action="append", default=[],
                    help="assert each reference's bytes, in --ip-ref order")
    ap.add_argument("--ip-scale", type=float, default=IP_SCALE)
    ap.add_argument("--ip-repo", default=IP_REPO)
    ap.add_argument("--ip-subfolder", default=IP_SUBFOLDER)
    ap.add_argument("--ip-weight", default=IP_WEIGHT)
    ap.add_argument("--ip-image-encoder-folder", default=IP_IMAGE_ENCODER_FOLDER,
                    help="MUST contain a slash to be read as a full path; the "
                         "slashless default resolves under --ip-subfolder, where "
                         "the box cache has no encoder at all")
    ap.add_argument("--allow-truncation", action="store_true",
                    help="render even though CLIP will drop the tail; the tail is "
                         "the style anchor, so this is almost never what you want")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    missing = [f for f, v in (("--arm", a.arm), ("--task", a.task),
                              ("--out", a.out), ("--prompt-file", a.prompt_file),
                              ("--negative-file", a.negative_file),
                              ("--seed", a.seed)) if v in (None, "")]
    if missing:
        ap.error("required: %s" % ", ".join(missing))
    return render(a)


if __name__ == "__main__":
    sys.exit(main())
