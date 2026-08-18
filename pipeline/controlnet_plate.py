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


def sidecar_lines(a, use_cn, ctrl_sha, rev, prompt, negative, load_s, render_s,
                  stamp, torch_version):
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
        side += [
            "controlnet: %s" % CONTROLNET,
            "controlnet_licence: %s" % CONTROLNET_LICENCE,
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
            CONTROLNET, torch_dtype=torch.bfloat16, **cn_kw)
        cn.to("cuda")
        # from_pipe swaps the class while REUSING the loaded modules, so one set
        # of base weights serves both arms -- r8/r9's discipline.
        pipe = AutoPipelineForText2Image.from_pipe(pipe, controlnet=cn)
        kw = {"image": ctrl_img,
              "controlnet_conditioning_scale": float(a.scale),
              "control_guidance_start": 0.0,
              "control_guidance_end": 1.0}

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
                         t2.strftime("%Y-%m-%dT%H:%M:%SZ"), torch.__version__)
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
