#!/usr/bin/env python3
"""Draw ONE beat's still on Apple MPS and open it — the 5-minute review loop.

Dad's directive (2026-07-27): iterate every ~5 minutes with the founder looking,
never render a whole episode and then discover it missed. A still is the cheapest
artefact that can be judged — ~30s on Kaggle's T4 but only retrievable when the
whole kernel ends, which makes the *loop* 25+ minutes. Locally one SDXL still is
a few minutes and lands on the Desktop immediately. So:

    <cb-venv>/python3 pipeline/still_local.py sapling 001 --beat 4
    <cb-venv>/python3 pipeline/still_local.py sapling 001 --beat 4 --note "wider"

look → verdict → fix the prompt in shots.md → run again. Only after a still is
approved does a beat earn animation (SVD on Kaggle) — motion costs 8x the time
and cannot fix a wrong picture.

Same prompt pipeline as the notebook (compress, count tags, per-beat negatives),
same resolution, same per-beat seed, so what the founder approves here is what
Kaggle draws there. STEWARDSHIP §6 gate applies: unapproved nodes refuse.

ONE at a time — MPS shares unified memory with everything else on the machine
(render_local.py's header records the 3-job pileup that froze it on 2026-07-26).
"""

import argparse
import sys
import time
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
from generate_shots import parse_shots  # noqa: E402
from render_local import approved  # noqa: E402 — the §6 gate, one implementation
from sd_prompt import compress, extra_negatives, suppressed_negatives  # noqa: E402

BASE = "cagliostrolab/animagine-xl-3.1"
STILL_W, STILL_H = 832, 1216          # what the Kaggle notebook draws
SEED = 20260719                        # + beat num, same as the notebook
NEG = ("photorealistic, 3d render, abstract, text, watermark, signature, low quality, "
       "blurry, extra limbs, deformed, jpeg artifacts, realistic skin texture")
DROPS = Path.home() / "Desktop" / "banyan-drops"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("genome")
    ap.add_argument("node")
    ap.add_argument("--beat", type=int, required=True)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--seed-bump", type=int, default=0,
                    help="try a different composition without touching the prompt")
    ap.add_argument("--note", default="", help="tag for the output filename")
    ap.add_argument("--raw", default="",
                    help="EXPERIMENT: send this prompt verbatim instead of the beat's "
                         "shots.md prompt — for A/B-ing prompt dialects in the fast "
                         "loop. The winner gets written back into shots.md; canon "
                         "renders never use --raw.")
    a = ap.parse_args()

    ok, detail = approved(a.genome, a.node)
    if not ok:
        raise SystemExit(f"{a.node} is NOT approved — {detail}\n"
                         "STEWARDSHIP.md §6: narrative approval precedes media.")

    nodes = REPO / "genomes" / a.genome / "nodes"
    d = next(x for x in sorted(nodes.iterdir())
             if x.is_dir() and x.name.startswith(a.node))
    shot = next((s for s in parse_shots((d / "shots.md").read_text())
                 if s["num"] == a.beat), None)
    if not shot:
        raise SystemExit(f"no beat {a.beat} in {d.name}/shots.md")

    if a.raw:
        ptext, dropped = a.raw, []
    else:
        ptext, dropped = compress(shot["prompt"])
    neg = NEG
    for term in suppressed_negatives(shot["prompt"]):
        neg = neg.replace(term + ", ", "")
    extra = extra_negatives(shot["prompt"])
    if extra:
        neg = f"{neg}, {extra}"
    print(f"beat {a.beat:02d} {shot['slug']}\n  POS: {ptext}\n  NEG: {neg}")
    if dropped:
        print(f"  dropped for budget: {' '.join(dropped)[:120]}")

    import torch
    from render_local import _shim_transformers
    _shim_transformers()  # diffusers imports constants newer transformers removed
    from diffusers import StableDiffusionXLPipeline
    if not torch.backends.mps.is_available():
        raise SystemExit("no MPS — this is the Apple-Silicon fast loop")
    t0 = time.time()
    try:
        pipe = StableDiffusionXLPipeline.from_pretrained(
            BASE, torch_dtype=torch.float16, variant="fp16", use_safetensors=True)
    except Exception:
        pipe = StableDiffusionXLPipeline.from_pretrained(
            BASE, torch_dtype=torch.float16, use_safetensors=True)
    # SDXL's original VAE overflows in float16 and decodes to SOLID BLACK — the first
    # local still (2026-07-27) came back 832x1216 of pure #000. Kaggle's T4 dodges it
    # (its notebook run upcasts); MPS does not. The community fp16-safe VAE is the fix.
    from diffusers import AutoencoderKL
    pipe.vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix",
                                             torch_dtype=torch.float16)
    pipe.enable_attention_slicing()
    pipe.enable_vae_slicing()
    pipe.to("mps")
    print(f"pipeline ready in {time.time()-t0:.0f}s")

    t1 = time.time()
    g = torch.Generator(device="cpu").manual_seed(SEED + a.beat + a.seed_bump)
    img = pipe(prompt=ptext, negative_prompt=neg, width=STILL_W, height=STILL_H,
               num_inference_steps=a.steps, guidance_scale=7.5,
               generator=g).images[0]
    DROPS.mkdir(exist_ok=True)
    tag = f"-{a.note.replace(' ', '-')}" if a.note else ""
    out = DROPS / (f"STILL-{a.node.split('-')[0]}-{a.beat:02d}-{shot['slug']}"
                   f"{tag}-{date.today():%H%M}.png")
    # timestamped name: iterations of one beat must sit side by side, not overwrite
    out = out.with_name(out.name.replace(f"{date.today():%H%M}",
                                         time.strftime("%H%M")))
    from render_local import spread_of
    spread = spread_of(img)
    if spread < 20:
        out = out.with_name("BLANK-" + out.name)
        print(f"WARNING: luma spread {spread:.0f} — this frame is blank/black, "
              "do not send it to review")
    img.save(out)
    print(f"{out.name} in {(time.time()-t1)/60:.1f} min, contrast {spread:.0f} — opening")
    import subprocess
    subprocess.run(["open", str(out)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
