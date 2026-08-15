#!/usr/bin/env python3
"""Render a node's shots locally on Apple MPS — the $0 path with a fast loop.

Same contract as `kaggle/render-kaggle.ipynb`: reads the node's `shots.md`,
writes `NN-slug.mp4` plus a `NN-slug.meta.yaml` of provenance (§7.2) into a
directory `render_t3.py --clips` can consume, skips clips that already exist so
an interrupted run resumes, and refuses to accept a blank generation.

Why this exists next to the notebook. Kaggle is the *citizen-reproducible* path
and stays (WATERING.md: anyone can rebuild the season with a free account, no
card). But it is a terrible path to ITERATE on: every attempt is a push, a
ten-minute wait, a fetch, and a log to argue with. Thirteen pushes on
2026-07-25/26 to get one clip, and most of the failures were bugs that a local
run would have surfaced in seconds — a wrong accelerator name, a gated
checkpoint, a mis-calibrated guard of my own. Locally the loop is: run, look.

Both are $0. The difference is the feedback loop, and that is the whole cost.

    python3 pipeline/render_local.py sapling 001 [--beats 1,2] [--out DIR]
    python3 pipeline/render_local.py --smoke        # prove the stack, no node

The founder's approval gate (STEWARDSHIP.md §6) applies here as much as
anywhere: this refuses to render a node whose T0 leaf is not stamped
`approved_by: founder`. `--smoke` is exempt because it renders no episode
content — it draws a style card to prove the pipeline works.

**Run ONE of these at a time.** MPS shares the machine's unified memory with
everything else, so a second render — or a Chatterbox voice run, which also
lives on MPS — turns a comfortable job into an out-of-memory error that reads
like a configuration problem. It is not one: on 2026-07-26 a 512x512 x16 job
died reporting "MPS allocated 12.57 GB, other allocations 25.09 GB" on a 32 GB
machine, and the 25 GB was three of my own concurrent jobs.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from generate_shots import parse_shots  # noqa: E402
from sd_prompt import compress  # noqa: E402 — CLIP stops at 77 tokens

BASES = ["gsdf/Counterfeit-V2.5", "Lykon/dreamshaper-8",
         "stable-diffusion-v1-5/stable-diffusion-v1-5"]
ADAPTER = "guoyww/animatediff-motion-adapter-v1-5-3"
NEG = ("photorealistic, 3d render, text, watermark, signature, low quality, blurry, "
       "extra limbs, deformed, jpeg artifacts, realistic skin texture")
# The v1.5 motion module is trained at 512x512 / 16 frames. Asking for 432x768 x24
# — 2.5x the pixels and 1.5x the frames — produced mottled grey on a T4 and a
# 19 GB attention allocation on MPS. Stay at native and let render_t3 do the 9:16
# framing, which it already does for every clip (scale + centre-crop).
FRAMES, FPS, STEPS = 16, 8, 25
HEIGHT, WIDTH = 512, 512
SEED = 20260719
# Calibrated on the 31 archived clips of this style: per-frame luma spread runs a
# median of 52-144. Dead grey runs 14-22. Judged on the median across frames,
# because real clips dip for a single frame while their medians sit far higher.
BLANK_SPREAD = 35.0

SMOKE_PROMPT = (
    "Vertical 9:16 shot, hand-drawn 2D anime style, low detail: flat cel-shaded colors, "
    "bold clean linework, single shadow tone, simplified shapes, soft watercolor-wash "
    "background, gentle pastel palette. A single small tree stands alone in a wide green "
    "field, its leaves shifting in a light breeze, clouds drifting behind it. "
    "No photorealism, no 3D render look, no heavy texture. 9:16 vertical, no text.")


def spread_of(frame) -> float:
    """Luma spread (90th percentile minus 10th) of one frame, 0-255."""
    # numpy is imported HERE, not at module level: test_pipeline imports this module
    # for the S6 approval gate, and CI installs only pyyaml/pillow/markdown. The
    # module-level import turned every push from 15:39 to 18:10 on 2026-07-27 red --
    # ~20 failure mails in the founder's inbox -- while passing locally, because the
    # local venv has numpy. Only the render path needs it; the gate does not.
    import numpy as np
    a = np.asarray(frame, dtype=np.float32)
    if not np.isfinite(a).all():
        return 0.0
    # must be LUMA: the threshold is calibrated on the archived clips' luma
    # spread, and measuring RGB percentiles instead inflates it with colour —
    # a blank frame read 28 in RGB against 18 in luma, and so passed a floor of 35
    if a.ndim == 3 and a.shape[-1] >= 3:
        a = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    lo, hi = np.percentile(a, 10), np.percentile(a, 90)
    return float(hi - lo) * (255.0 if a.max() <= 1.001 else 1.0)


def _shim_transformers():
    """Define the constants newer transformers removed and diffusers still imports.

    `transformers.utils.FLAX_WEIGHTS_NAME` is gone from current releases, and
    diffusers imports it at module load, so `from diffusers import
    AnimateDiffPipeline` dies with an ImportError that mentions neither library's
    real problem. Same failure as on Kaggle's batch image. These are plain
    filename constants and nothing here reads a flax or tf checkpoint, so define
    what is missing rather than repinning transformers — a repin drags tokenizers
    and risks the torch/MPS pair the voice engine depends on.
    """
    import transformers.utils as tu
    for name, val in (("FLAX_WEIGHTS_NAME", "flax_model.msgpack"),
                      ("TF2_WEIGHTS_NAME", "tf_model.h5"),
                      ("TF_WEIGHTS_NAME", "model.ckpt")):
        if not hasattr(tu, name):
            setattr(tu, name, val)


def load_pipe():
    import torch
    _shim_transformers()
    from diffusers import AnimateDiffPipeline, DDIMScheduler, MotionAdapter

    if not torch.backends.mps.is_available():
        raise SystemExit("no MPS device — this script is the Apple-Silicon path")
    adapter = MotionAdapter.from_pretrained(ADAPTER, torch_dtype=torch.float16)
    pipe = base = None
    for cand in BASES:
        try:
            pipe = AnimateDiffPipeline.from_pretrained(
                cand, motion_adapter=adapter, torch_dtype=torch.float16)
            base = cand
            break
        except Exception as e:  # gated repo, network, missing revision
            print(f"  {cand} unavailable ({type(e).__name__}) — next", flush=True)
    if pipe is None:
        raise SystemExit(f"none of {BASES} loaded; all gated or offline?")
    # the sampler AnimateDiff's motion module was tuned against; the default
    # produces mush at low step counts
    pipe.scheduler = DDIMScheduler.from_config(
        pipe.scheduler.config, clip_sample=False, timestep_spacing="linspace",
        beta_schedule="linear", steps_offset=1)
    pipe.enable_vae_slicing()
    pipe.enable_attention_slicing()      # MPS holds the whole frame stack otherwise
    pipe.to("mps")
    print(f"pipeline ready on MPS — AnimateDiff on {base}")
    return pipe, base, torch


def approved(genome: str, node: str) -> tuple:
    """(is_approved, detail) from the node's newest T0 leaf yaml."""
    nodes = REPO / "genomes" / genome / "nodes"
    d = next((x for x in sorted(nodes.iterdir()) if x.is_dir() and x.name.startswith(node)), None)
    if not d:
        raise SystemExit(f"no node dir starting with {node!r}")
    # Glob for ANY t0 yaml rather than building the prefix from the caller's argument.
    # Leaf ids are not the dir name (dir `001-capability-inventory` holds `001-t0-d.yaml`)
    # and are not uniformly the first segment either (`004c-n` holds `004c-n-t0-a.yaml`),
    # so `f"{node}-t0-*.yaml"` found nothing whenever the node was named in full: on
    # 2026-07-27 `push 001-capability-inventory` reported "no T0 leaf found" for a node
    # the founder had approved that morning. It failed closed, which is the right
    # direction to fail, but a gate that misreads a real approval as a missing one
    # teaches people to reach for the override. leaves/ belongs to one node — just read it.
    leaves = sorted((d / "leaves").glob("*-t0-*.yaml"))
    if not leaves:
        return False, "no T0 leaf found"
    meta = yaml.safe_load(leaves[-1].read_text()) or {}
    who = str(meta.get("approved_by", "none"))
    return who.startswith("founder"), f"{leaves[-1].name}: approved_by: {who}"


def render(pipe, torch, prompt: str, num: int, dest: Path) -> float:
    import time
    from diffusers.utils import export_to_video
    t0 = time.time()
    g = torch.Generator(device="cpu").manual_seed(SEED + num)
    frames = pipe(prompt=prompt, negative_prompt=NEG, height=HEIGHT, width=WIDTH,
                  num_frames=FRAMES, num_inference_steps=STEPS,
                  guidance_scale=7.5, generator=g).frames[0]
    spreads = [spread_of(f) for f in frames[::max(1, len(frames) // 8)]]
    import numpy as np
    spread = float(np.median(spreads))
    # written either way: a guard that deletes its own evidence turns an
    # ambiguous reading into an unanswerable one
    out = dest if spread >= BLANK_SPREAD else dest.with_suffix(".SUSPECT.mp4")
    export_to_video(frames, str(out), fps=FPS)
    print(f"  {out.name} in {(time.time()-t0)/60:.1f} min, contrast {spread:.0f}"
          + ("" if spread >= BLANK_SPREAD else "  <-- BLANK, kept for inspection"),
          flush=True)
    return spread


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("genome", nargs="?")
    ap.add_argument("node", nargs="?")
    ap.add_argument("--beats", help="comma-separated beat numbers; default all pending")
    ap.add_argument("--out", help="output dir; default the node's clips/")
    ap.add_argument("--smoke", action="store_true",
                    help="render one style card to prove the stack; renders no episode content")
    ap.add_argument("--yes-this-eats-the-machine", action="store_true",
                    help="required: acknowledge the measured cost below before running")
    args = ap.parse_args()

    # MEASURED, 2026-07-26, M1 Pro / 32 GB: 4-5 MINUTES PER DENOISING STEP at
    # 512x512 x16 frames. At 25 steps that is ~1.5 hours for ONE 3-second clip,
    # ~30 hours for a 20-beat episode, while holding 12+ GB of unified memory and
    # starving everything else on the machine. The founder had to kill it.
    #
    # AnimateDiff's temporal attention is the reason: it is not a per-frame image
    # model, it attends across all 16 frames at once, and MPS has no efficient
    # kernel for that shape. A free Kaggle T4 does the same work in minutes.
    #
    # So this path is NOT the render path. It is kept because the code is correct
    # and the approval gate in it is worth having, and because a future Mac or a
    # smaller model may make it viable. It refuses to run without the flag.
    if not args.yes_this_eats_the_machine:
        raise SystemExit(
            "REFUSING. Measured on this machine: 4-5 minutes per step, ~1.5 h per\n"
            "3-second clip, ~30 h per episode, 12+ GB resident. It makes the machine\n"
            "unusable and was killed by the founder on 2026-07-26.\n\n"
            "Render on the free Kaggle T4 instead:\n"
            "  python3 pipeline/kaggle/run_remote.py push <node>\n\n"
            "If you genuinely mean to run it here, pass --yes-this-eats-the-machine.")

    pipe, base, torch = load_pipe()

    if args.smoke:
        dest = Path(args.out or ".") / "smoke-animatediff.mp4"
        dest.parent.mkdir(parents=True, exist_ok=True)
        s = render(pipe, torch, SMOKE_PROMPT, 0, dest)
        print("\nstack works." if s >= BLANK_SPREAD else
              "\nstack loads but generates blank frames — not a node problem.")
        return 0 if s >= BLANK_SPREAD else 1

    if not (args.genome and args.node):
        raise SystemExit("need <genome> <node>, or --smoke")

    ok, detail = approved(args.genome, args.node)
    if not ok:
        raise SystemExit(
            f"{args.node} is NOT approved for production — {detail}\n"
            "STEWARDSHIP.md §6: the founder reads and approves the narrative before\n"
            "any voice, footage or assembly is made from it. Bring them the script."
        )

    # HOUSEKEEPING BEFORE THE FIRST FRAME. This renderer is the thing that fills
    # the disk, so it is also the thing that should take some back first.
    #
    # Founder, 2026-08-15, at 99% full: "dude! i was running out of memory". The
    # Mac went to the line three times that day. Two things were eating it and
    # nothing removed either: failed `git repack` litter (~0.6 GB/day, and each
    # failure makes the next likelier — see box_cache.stale_tmp_packs) and
    # abandoned scratchpad worktrees, one of which was 1275 MB of a checkout a
    # session had walked away from four days earlier. Both are pure waste: the
    # worktree sweep removes a tree only when it is in the session scratchpad,
    # untouched for 12 h, has no modified/untracked/IGNORED file, and sits on a
    # commit already on origin/main — so `git worktree add` reproduces it exactly.
    # A guard that lives in code beats a habit; that is why this is here and not
    # in someone's checklist.
    #
    # The import is inside the try with the calls: housekeeping bolted to the
    # front of a render must never be the reason the render does not happen.
    try:
        from box_cache import sweep_git_tmp_packs, sweep_stale_worktrees
        sweep_git_tmp_packs()
        sweep_stale_worktrees(dry_run=False)
    except Exception as _e:               # noqa: BLE001 — see above
        print(f"  disk sweep skipped ({type(_e).__name__}: {_e})")

    nodes = REPO / "genomes" / args.genome / "nodes"
    d = next(x for x in sorted(nodes.iterdir()) if x.is_dir() and x.name.startswith(args.node))
    shots = parse_shots((d / "shots.md").read_text())
    want = {int(x) for x in args.beats.split(",")} if args.beats else None

    # PICTURE-VS-WORDS GATE, and it refuses only the beats it has findings ON.
    #
    # Founder, 2026-08-03: "there is again some dialogue out of sync, when he says
    # 'huh, blue' it is showing the coffee scene. reflect why this is happening and
    # why you still have not implemented guard to make sure it will not happen
    # again." Beat 05 of episode 1 spoke "Huh. Blue." over a broken coffee mug, and
    # nothing in the pipeline compared a beat's line to its picture, so the error
    # was only ever findable by watching the finished cut — after the render, the
    # voice and the assembly had all been paid for.
    #
    # Per-beat rather than whole-node on purpose: blocking all fifteen because one
    # is stale is how a gate earns an --override flag, and an override flag is how a
    # gate stops existing. A clean beat still renders.
    try:
        from check_sync import check as sync_check
        bad = {}
        for f in sync_check(args.genome, args.node):
            if f["sev"] == "FAIL":
                bad.setdefault(f["beat"], []).append(f"{f['what']}: {f['detail']}")
        blocked = sorted(b for b in bad if want is None or b in want)
        if blocked:
            print(f"  SYNC GATE: refusing {len(blocked)} beat(s) — picture, script "
                  f"and voice disagree")
            for b in blocked:
                for msg in bad[b]:
                    print(f"    beat {b:02d}  {msg}")
            print("  Fix the text first (it is free), or pass --beats without these.")
            want = ({x for x in want if x not in bad} if want is not None
                    else {n for n in shots if n not in bad})
            if not want:
                raise SystemExit("  every requested beat is out of sync — nothing to do")
    except ImportError:
        print("  WARNING: check_sync unavailable — rendering WITHOUT the sync gate")
    out = Path(args.out) if args.out else d / "clips"
    out.mkdir(parents=True, exist_ok=True)

    todo = [s for s in shots if (want is None and not s["done"]) or (want and s["num"] in want)]
    todo = [s for s in todo if not (out / f"{s['num']:02d}-{s['slug']}.mp4").exists()]
    print(f"{len(todo)} beat(s) to render for {d.name} -> {out}")

    for s in todo:
        dest = out / f"{s['num']:02d}-{s['slug']}.mp4"
        print(f"beat {s['num']:02d} ({s['slug']}) …", flush=True)
        ptext, dropped = compress(s["prompt"])
        if dropped:
            print(f"  (dropped, too long: {' '.join(dropped)[:100]})")
        spread = render(pipe, torch, ptext, s["num"], dest)
        if spread < BLANK_SPREAD:
            print("  stopping: a blank generation means the stack is wrong, not this beat")
            return 1
        dest.with_suffix(".meta.yaml").write_text(
            "# Shot provenance (§7.2)\n" + yaml.safe_dump({
                "platform": "local-apple-mps", "model": f"AnimateDiff {ADAPTER} on {base}",
                "prompt": ptext, "prompt_source": s["prompt"], "negative_prompt": NEG, "seed": SEED + s["num"],
                "steps": STEPS, "frames": FRAMES, "fps": FPS,
                "cost_usd": 0.00, "generated": str(date.today()),
            }, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
