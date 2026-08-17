#!/usr/bin/env python3
"""Beat 14: FINISH the composited field at strength 0.30 on Apple MPS. $0.

The init is `beat14_field_composite.py`'s v6 output: a continuous grass sward with
blades, a bare-soil clearing under his hands, and the figure untouched. This step
asks the sampler to HARMONISE that structure, not to invent it. At 40 steps and
strength 0.30 only int(40 x 0.30) = 12 steps of the schedule run, from a latent
that still carries the init's layout, so the early high-sigma steps where global
composition is decided never run (pipeline/composite-init-pattern.md §3).

THE PROMPT AND NEGATIVE ARE BYTE-IDENTICAL to r6/s1/s2/s3 BY CONSTRUCTION: they
are read out of `plate_scratch.REVS[(14, 6)]`, so they cannot drift by a
character even if someone edits that entry -- they would move together, which is
correct for a replication. `from above` STAYS: it is the only instrument that has
ever moved P5 and four draws show the empty sky band stays gone.

fp16 on MPS deliberately, matching `plate_scratch.py` exactly -- that is the path
all four scored draws came from, and the base plate is one of them, so the backend
is held constant and only the init changes.

THE ONE THING THIS RUNG CHANGES IS THE INIT. Bar and failure meaning were
pre-registered at d850c276 before any of this existed.
"""

import argparse
import hashlib
import json
import sys
import time
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))
W, H = 832, 1216
BASE = "cagliostrolab/animagine-xl-3.1"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", required=True)
    ap.add_argument("--init-sha256", required=True)
    ap.add_argument("--mask", required=True)
    ap.add_argument("--mask-sha256", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--strength", type=float, default=0.30)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--cfg", type=float, default=7.5)
    ap.add_argument("--seed", type=int, default=20260820)
    ap.add_argument("--blur", type=int, default=8)
    a = ap.parse_args()

    if a.strength > 0.35:
        print("!! strength %.2f is above the window this method lives in "
              "(0.2-0.35). Above it the sampler stops FINISHING and starts "
              "INVENTING, which is the failure the composite exists to avoid, "
              "and the pre-registered stop rule forbids a higher strength as a "
              "rescue. Refusing." % a.strength)
        return 6

    init, mask = Path(a.init), Path(a.mask)
    for p, want in ((init, a.init_sha256), (mask, a.mask_sha256)):
        have = sha(p)
        if have != want:
            print("!! sha mismatch on %s\n   want %s\n   have %s" % (p.name, want, have))
            return 2

    # Byte-identity is structural, not promised.
    from plate_scratch import REVS  # noqa: E402
    rev = REVS[(14, 6)]
    prompt, negative = rev["prompt"], rev["negative"]

    from render_local import approved  # noqa: E402
    ok = approved("sapling", "002b-first-citizen")
    if isinstance(ok, tuple):
        ok, detail = ok
    else:
        detail = ""
    if not ok:
        print("!! node not founder-approved (STEWARDSHIP §6). Refusing. %s" % detail)
        return 9

    import torch  # noqa: E402
    from PIL import Image  # noqa: E402
    from diffusers import StableDiffusionXLInpaintPipeline  # noqa: E402

    if not torch.backends.mps.is_available():
        print("!! no MPS"); return 4
    t0 = time.time()
    pipe = StableDiffusionXLInpaintPipeline.from_pretrained(
        BASE, torch_dtype=torch.float16, use_safetensors=True)
    pipe.to("mps")
    pipe.set_progress_bar_config(disable=True)
    in_ch = int(pipe.unet.config.in_channels)
    print("MODEL_LOADED %s mps/fp16 unet.in_channels=%d in %.0fs"
          % (BASE, in_ch, time.time() - t0), flush=True)

    tok = pipe.tokenizer
    for name, text in (("positive", prompt), ("negative", negative)):
        n = len(tok(text).input_ids)
        print("TOKENS %s %d/77 %s" % (name, n, "TRUNCATED!!" if n > 77 else "ok"))
        if n > 77:
            print("!! a prompt overflows and its tail would be dropped. Refusing.")
            return 5
    if not prompt.rstrip().endswith("very aesthetic"):
        print("!! the style tail was cut. Refusing."); return 5

    plate = Image.open(init).convert("RGB")
    m = Image.open(mask).convert("L")
    blurred = pipe.mask_processor.blur(m, blur_factor=a.blur) if a.blur else m

    t1 = time.time()
    img = pipe(prompt=prompt, negative_prompt=negative, image=plate,
               mask_image=blurred, width=W, height=H,
               num_inference_steps=a.steps, guidance_scale=a.cfg,
               strength=a.strength,
               generator=torch.Generator("cpu").manual_seed(a.seed)).images[0]
    dt = time.time() - t1
    img.save(a.out)
    out_sha = sha(Path(a.out))
    print("wrote %s  (%.0fs, %d of %d steps ran)"
          % (a.out, dt, int(a.steps * a.strength), a.steps), flush=True)

    meta = {
        "platform": "local-gpu (Apple Silicon, MPS) -- macbook1",
        "model": BASE,
        "model_licence": "CreativeML Open RAIL++-M (use restrictions travel; D15)",
        "pipeline": "StableDiffusionXLInpaintPipeline (base weights, unet.in_channels=%d)" % in_ch,
        "cost_usd": 0.0,
        "shot_beat": 14,
        "beat_slug": "the-defense",
        "size": "%dx%d" % (W, H),
        "steps": a.steps,
        "steps_actually_run": int(a.steps * a.strength),
        "guidance": a.cfg,
        "strength": a.strength,
        "seed": a.seed,
        "mask_blur_factor": a.blur,
        "render_seconds": round(dt, 1),
        "png_sha256": out_sha,
        "init_image": str(Path(a.init)),
        "init_sha256": a.init_sha256,
        "mask_png": str(Path(a.mask)),
        "mask_sha256": a.mask_sha256,
        "prompts_from": ("plate_scratch.REVS[(14,6)] -- byte-identical to r6, s1, "
                         "s2, s3 by construction, read at run time"),
        "prompt": prompt,
        "negative_prompt": negative,
        "bar": "pipeline/loop/beat14-field-init-0817.md (d850c276), pre-registered",
        "the_one_thing_changed": ("the INIT. Wording, negative, camera angle, "
                                  "size, steps and guidance are r6's."),
        "founder_verdict": None,
        "approved": False,
        "provisional": True,
        "scored": False,
        "date": date.today().isoformat(),
    }
    Path(a.out + ".meta.yaml").write_text(
        "\n".join("%s: %s" % (k, json.dumps(v)) for k, v in meta.items()) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
