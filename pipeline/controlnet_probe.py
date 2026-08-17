#!/usr/bin/env python3
"""CAPABILITY PROBE: does a scribble ControlNet actually CONSTRAIN animagine-xl-3.1?

WHAT IS AND IS NOT IN QUESTION. Five complete SDXL ControlNets sit in the box's
HF cache, and `cross_attention_dim 2048` / `block_out_channels [320,640,1280]`
match animagine-xl-3.1's UNet exactly, so the weights LOAD. That is
COMPATIBILITY. It is not capability. What is unproven is that a run completes
on our finetune and that the hint VISIBLY BINDS the output. A ControlNet that
loads and then ignores its condition is worse than no path at all, because it
looks like one — so this script is built to be able to return NO.

THE ARMS. Four, one seed, one prompt, one size; the ONLY variable is the
condition.

  A  nocontrol   no ControlNet at all. The model's own composition.
  B  left        the 2-leaf hint, stem base at x=0.32.
  C  right       the SAME hint mirrored, stem base at x=0.68.
  D  polarity    arm B's hint inverted (black on white).

LEAF COUNT IS HELD AT TWO IN EVERY CONTROL ARM AND IS NOT MEASURED HERE. Arms B
and C differ in POSITION only. That is deliberate: the leaf-count experiment
belongs to another lane, and a probe that changed count would duplicate its
rung and muddy this one. Nothing in this file may be read as a verdict on
whether the founder's two-leaf bar is met.

THE MEASUREMENT, PRE-REGISTERED BEFORE THE PIXELS (§8 discipline). Eyeballing
"looks kind of like the hint" is how a lane talks itself into a capability it
does not have. So binding is a number: dilate the hint's strokes into a mask,
take the output's gradient magnitude, and compare the mean gradient INSIDE the
mask against the mean inside the SAME mask mirrored in x.

    bind_ratio = mean|grad| inside hint mask / mean|grad| inside mirrored mask

  - Arm A must land near 1.0. It never saw a hint, so structure cannot prefer
    the hint's side over its mirror. If arm A comes out far from 1.0 the METRIC
    is broken (the prompt has a left/right bias of its own) and no arm's number
    means anything — that is a pre-registered kill switch on my own instrument.
  - Arms B and C bind if bind_ratio > 1.0 by a clear margin, EACH ON ITS OWN
    SIDE. B and C use mirrored hints, so a metric that rises for both is
    measuring obedience; one that rises for both only because the model likes
    the left side is caught by A.
  - PASS = A within [0.85, 1.15] AND B > 1.25 AND C > 1.25.
  - Arm D settles the polarity assumption in author_scribble.py rather than
    trusting a comment. If D binds and B does not, the convention is inverted
    and every hint needs `--invert`.

FAILURE IS A REAL OUTCOME. If B and C both sit at ~1.0 the ControlNet ran and
ignored its hint, and this report says structural conditioning is not on the
table for us — which is worth more than a hopeful maybe, because the fallback
(composite-then-inpaint at strength 0.30) is already proven on beats 06 and 10.

THE PROMPT IS THIS FILE'S OWN and is not a beat draft. It is not read from
pipeline/wave-drafts.yaml and it does not touch any beat's approved wording, so
this probe cannot collide with a drafting lane and no plate here is a candidate
for anything.

    python3 pipeline/controlnet_probe.py --arm left --out DIR
    python3 pipeline/controlnet_probe.py --measure DIR     # no GPU needed
    python3 pipeline/controlnet_probe.py --selftest        # no GPU, no weights
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

TASK = "ep2-cnet-probe-0817"
BASE = "cagliostrolab/animagine-xl-3.1"
BASE_LICENCE = "CreativeML Open RAIL++-M (use restrictions travel; D15)"

# Apache-2.0, and already complete in the box cache at 2,502,139,104 bytes.
# MistoLine would also work but its README puts a standing visible-attribution
# obligation on anything it renders, so the permissive net is the default.
CONTROLNET = "xinsir/controlnet-scribble-sdxl-1.0"
CONTROLNET_LICENCE = "apache-2.0 (D15 SAFE, no attribution condition)"

# THE VARIANT TRAP, and it is why a naive constant-swap of render_b01r9.py
# crashes: the xinsir repos ship ONLY `diffusion_pytorch_model.safetensors`, so
# passing variant="fp16" raises. diffusers/* and MistoLine ship ONLY
# `*.fp16.safetensors`, so OMITTING it raises. Verified against the box's
# snapshot listing, not assumed.
CONTROLNET_VARIANT = None

W, H = 832, 1216          # beat 01's proven size
STEPS = 40
CFG = 7.5
SEED = 20260817
SCALE = 0.8               # thick-line + high-scale: the condition-wins end

POS = ("a single small seedling sprout growing in open ground, thin stem, "
       "soft daylight, wide shot, anime cel shading, flat colour, "
       "bold clean lineart, 2d animation still, detailed, newest, "
       "masterpiece, best quality, very aesthetic")
NEG = ("photorealistic, 3d render, blurry, lowres, worst quality, jpeg "
       "artifacts, watermark, signature, text, 1girl, 1boy, person, hands, "
       "potted plant, flower pot, tree trunk, mature tree")

ARMS = {
    # arm      -> (control png relative to repo, invert, uses controlnet)
    "nocontrol": (None, False, False),
    "left":      ("pipeline/control/seedling-2leaf-0817.png", False, True),
    "right":     ("pipeline/control/seedling-2leaf-right-0817.png", False, True),
    "polarity":  ("pipeline/control/seedling-2leaf-0817.png", True, True),
}

# Pre-registered thresholds. Named constants so the report cannot quietly move
# the bar after seeing the numbers.
A_LO, A_HI = 0.85, 1.15
BIND_MIN = 1.25


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_rev(root):
    try:
        # encoding named explicitly: a text-mode read that defaults to the
        # platform codec decodes as cp1252 on the box and test_pipeline.py
        # enforces this repo-wide.
        return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                              capture_output=True, text=True, encoding="utf-8",
                              timeout=20).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------
# the measurement — pure numpy, no torch, runs on any machine
# --------------------------------------------------------------------------

def stroke_mask(hint_img, invert, dilate=7):
    """Boolean mask of where the hint has ink, dilated by a square kernel."""
    import numpy as np
    g = np.asarray(hint_img.convert("L"), dtype=np.float32)
    ink = (g < 128) if invert else (g > 128)
    if dilate > 1:
        out = np.zeros_like(ink)
        r = dilate // 2
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                out |= np.roll(np.roll(ink, dy, axis=0), dx, axis=1)
        ink = out
    return ink


def grad_mag(img):
    """Sobel-free gradient magnitude: central differences on luminance."""
    import numpy as np
    g = np.asarray(img.convert("L"), dtype=np.float32)
    gy = np.zeros_like(g)
    gx = np.zeros_like(g)
    gy[1:-1, :] = g[2:, :] - g[:-2, :]
    gx[:, 1:-1] = g[:, 2:] - g[:, :-2]
    return np.sqrt(gx * gx + gy * gy)


def bind_ratio(out_img, hint_img, invert=False, dilate=7):
    """mean|grad| inside the hint's strokes / mean inside the mirrored strokes.

    Mirroring rather than comparing against the whole frame is what makes this
    robust: both regions are the same shape and the same total area, at the
    same heights, so a frame whose structure is simply concentrated near the
    horizon cannot inflate the number.
    """
    import numpy as np
    if out_img.size != hint_img.size:
        raise ValueError(f"size mismatch: out {out_img.size} hint {hint_img.size}")
    m = stroke_mask(hint_img, invert, dilate)
    mm = m[:, ::-1]
    gm = grad_mag(out_img)
    a, b = gm[m], gm[mm]
    if a.size == 0 or b.size == 0:
        raise ValueError("empty mask — hint carries no ink")
    ma, mb = float(a.mean()), float(b.mean())
    # Regularised rather than divided raw. A mirrored region that happens to be
    # perfectly flat (an untextured sky band is a real possibility, not just a
    # synthetic one) would make a raw ratio explode or raise; the epsilon keeps
    # it finite and monotonic. EPS is tiny against a gradient scale whose real
    # values run to the hundreds. If BOTH sides are flat there is no structure
    # anywhere and no ratio means anything, so that still refuses.
    EPS = 0.5
    if ma <= EPS and mb <= EPS:
        raise ValueError("frame is flat on both sides; ratio undefined")
    return (ma + EPS) / (mb + EPS), int(m.sum()), ma, mb


def measure_dir(d):
    """Read every arm PNG in a directory and print the pre-registered verdict."""
    from PIL import Image
    d = Path(d)
    rows = []
    for arm in ("nocontrol", "left", "right", "polarity"):
        p = d / f"{TASK}-{arm}.png"
        if not p.exists():
            print(f"  {arm:10s} MISSING {p.name}")
            continue
        out = Image.open(p)
        # Every arm is scored against the LEFT hint's mask except `right`,
        # which is scored against its own. Arm A is scored against the left
        # mask because that is the mask whose ratio must come out at 1.0.
        hint_rel = ARMS[arm][0] or ARMS["left"][0]
        inv = ARMS[arm][1]
        hint = Image.open(REPO / hint_rel)
        r, npx, mi, mo = bind_ratio(out, hint, inv)
        rows.append((arm, r))
        print(f"  {arm:10s} bind_ratio={r:.3f}  (in {mi:.2f} / mirror {mo:.2f}, "
              f"{npx} px)")
    got = dict(rows)
    if len(got) == 4:
        a, l, ri = got["nocontrol"], got["left"], got["right"]
        metric_ok = A_LO <= a <= A_HI
        print(f"\n  metric sane (arm A in [{A_LO},{A_HI}]): "
              f"{'YES' if metric_ok else 'NO -- every number here is void'}")
        if metric_ok:
            print(f"  binds (left>{BIND_MIN} and right>{BIND_MIN}): "
                  f"{'YES' if l > BIND_MIN and ri > BIND_MIN else 'NO'}")
            print(f"  polarity: {'white-on-black confirmed' if l > got['polarity'] else 'INVERTED -- use --invert'}")
    return 0


# --------------------------------------------------------------------------

def render(a):
    import torch
    from PIL import Image

    root = Path(a.root) if a.root else REPO
    arm_ctrl, invert, use_cn = ARMS[a.arm]

    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_png = out_dir / f"{TASK}-{a.arm}.png"

    ctrl_img = None
    ctrl_sha = None
    if use_cn:
        cp = root / arm_ctrl
        if not cp.exists():
            print(f"control hint missing: {cp}", file=sys.stderr)
            return 6
        ctrl_sha = sha256_file(cp)
        ctrl_img = Image.open(cp).convert("RGB")
        if ctrl_img.size != (W, H):
            print(f"control is {ctrl_img.size}, render is {(W, H)} — diffusers "
                  f"would resize it and the measurement's geometry would be "
                  f"wrong. Re-author at the render size.", file=sys.stderr)
            return 7
        if invert:
            from PIL import ImageOps
            ctrl_img = ImageOps.invert(ctrl_img)

    if not torch.cuda.is_available():
        print("no CUDA — this probe is a box job", file=sys.stderr)
        return 5

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
            CONTROLNET, torch_dtype=torch.bfloat16, **cn_kw)
        cn.to("cuda")
        # from_pipe swaps the class while REUSING the loaded modules, so one set
        # of base weights serves both arms — r8/r9's discipline.
        pipe = AutoPipelineForText2Image.from_pipe(pipe, controlnet=cn)
        kw = {"image": ctrl_img,
              "controlnet_conditioning_scale": float(a.scale),
              "control_guidance_start": 0.0,
              "control_guidance_end": 1.0}

    g = torch.Generator("cuda").manual_seed(a.seed)
    t1 = datetime.datetime.now(datetime.timezone.utc)
    img = pipe(prompt=POS, negative_prompt=NEG, width=W, height=H,
               num_inference_steps=STEPS, guidance_scale=CFG,
               generator=g, **kw).images[0]
    t2 = datetime.datetime.now(datetime.timezone.utc)
    img.save(out_png)

    rev = git_rev(root)
    side = [
        "# Capability-probe provenance (7.2), written AT RENDER TIME by",
        "# controlnet_probe.py on the rtx5090. NOT a take, NOT a candidate.",
        "platform: local-gpu (rtx5090)",
        f"task: {TASK}",
        f"arm: {a.arm}",
        f"model: {BASE}",
        f"model_licence: {BASE_LICENCE}",
        ("pipeline: StableDiffusionXLControlNetPipeline (text2img + scribble control)"
         if use_cn else "pipeline: StableDiffusionXLPipeline (text2img, NO control)"),
        f"size: {W}x{H}",
        f"steps: {STEPS}",
        f"guidance: {CFG}",
        f"seed: {a.seed}",
        f"cost_usd: 0",
    ]
    if use_cn:
        side += [
            f"controlnet: {CONTROLNET}",
            f"controlnet_licence: {CONTROLNET_LICENCE}",
            f"controlnet_variant: {CONTROLNET_VARIANT!r} (xinsir ships no fp16 "
            f"variant file; passing one raises)",
            f"controlnet_conditioning_scale: {a.scale}",
            "control_guidance_start: 0.0",
            "control_guidance_end: 1.0",
            f"control_image: {arm_ctrl}",
            f"control_image_sha256: {ctrl_sha}",
            f"control_polarity: {'INVERTED black-on-white' if invert else 'white-on-black'}",
            "control_authored_by: pipeline/author_scribble.py (PIL, no model, "
            "no photo-derived edge map)",
        ]
    else:
        side.append("controlnet: none (baseline arm; the metric's sanity check)")
    side += [
        f"repo_commit: {rev}",
        f"model_load_seconds: {(t1 - t0).total_seconds():.1f}",
        f"render_seconds: {(t2 - t1).total_seconds():.1f}",
        f"rendered_utc: {t2.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"torch_version: {torch.__version__}",
        "approved: false",
        "provisional: >-",
        "  A CAPABILITY PROBE, not a take and not canon. Never takes a canon",
        "  filename, is not published, not posted, not assembled. Its prompt is",
        "  the probe's own and is not any beat's approved wording.",
        "leaf_count_note: >-",
        "  LEAF COUNT IS NOT MEASURED OR CLAIMED HERE. Count is held at two in",
        "  every control arm and only POSITION varies, because the leaf-count",
        "  experiment belongs to another lane. No verdict about the founder's",
        "  two-leaf bar may be read from this frame.",
        "measurement: >-",
        "  Binding is scored by pipeline/controlnet_probe.py --measure as",
        "  bind_ratio = mean|grad| inside the hint's dilated strokes / mean",
        f"  inside the same mask mirrored in x. Pre-registered: arm nocontrol in",
        f"  [{A_LO},{A_HI}] or the metric is void; left and right each >{BIND_MIN} to pass.",
    ]
    (out_dir / f"{TASK}-{a.arm}.png.meta.yaml").write_text(
        "\n".join(side) + "\n", encoding="utf-8")

    print(f"OK {out_png.name} load={(t1-t0).total_seconds():.1f}s "
          f"render={(t2-t1).total_seconds():.1f}s")
    return 0


def selftest():
    """The metric's own properties, with synthetic images. No GPU, no weights."""
    import numpy as np
    from PIL import Image
    fails = []

    def check(name, cond):
        print(("  ok   " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    hint = Image.open(REPO / ARMS["left"][0])
    check("hint is the render size", hint.size == (W, H))

    # A flat frame must give ratio 1.0 — no structure anywhere, no preference.
    flat = Image.new("RGB", (W, H), (90, 120, 70))
    try:
        bind_ratio(flat, hint)
        check("featureless frame is refused (no structure on either side)", False)
    except ValueError:
        check("featureless frame is refused (no structure on either side)", True)

    # A frame whose structure IS the hint must bind hard.
    perfect = hint.convert("RGB")
    r, _, _, _ = bind_ratio(perfect, hint)
    check(f"hint-as-output binds strongly ({r:.2f} > {BIND_MIN})", r > BIND_MIN)

    # A frame whose structure is the MIRRORED hint must anti-bind (<1).
    mirrored = hint.transpose(Image.FLIP_LEFT_RIGHT).convert("RGB")
    rm, _, _, _ = bind_ratio(mirrored, hint)
    check(f"mirrored structure anti-binds ({rm:.2f} < 1.0)", rm < 1.0)

    # Left/right symmetric noise must sit near 1.0 — this is the arm-A case,
    # and it is the check that the metric has no built-in side preference.
    rng = np.random.default_rng(0)
    half = rng.integers(0, 255, (H, W // 2), dtype=np.uint8)
    sym = np.concatenate([half, half[:, ::-1]], axis=1)
    rs, _, _, _ = bind_ratio(Image.fromarray(sym).convert("RGB"), hint)
    check(f"symmetric noise is neutral ({rs:.3f} in [{A_LO},{A_HI}])",
          A_LO <= rs <= A_HI)

    # Size mismatch must raise rather than silently resize.
    try:
        bind_ratio(Image.new("RGB", (64, 64)), hint)
        check("size mismatch is refused", False)
    except ValueError:
        check("size mismatch is refused", True)

    # The mask must be a small fraction of the frame, or "inside vs mirrored"
    # is comparing the frame against itself.
    m = stroke_mask(hint, False)
    frac = m.sum() / (W * H)
    check(f"dilated mask is a small region ({frac:.3f} < 0.15)", frac < 0.15)

    # Every arm's control file must exist, or a box job dies at step 2 of 4.
    for arm, (rel, _, use) in ARMS.items():
        if use:
            check(f"arm {arm} control exists", (REPO / rel).exists())

    print(("SELFTEST FAIL: %d" % len(fails)) if fails else "SELFTEST PASS")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description="scribble-ControlNet capability probe")
    ap.add_argument("--arm", choices=sorted(ARMS))
    ap.add_argument("--out", default=None)
    ap.add_argument("--root", default=None)
    ap.add_argument("--scale", type=float, default=SCALE)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--measure", default=None, metavar="DIR",
                    help="score a directory of arm PNGs; no GPU needed")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.measure:
        return measure_dir(a.measure)
    if not a.arm or not a.out:
        ap.error("--arm and --out required (or --measure/--selftest)")
    return render(a)


if __name__ == "__main__":
    sys.exit(main())
