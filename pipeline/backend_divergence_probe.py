#!/usr/bin/env python3
"""THE MAC AND THE BOX ARE DIFFERENT RENDERERS. Measured, 2026-08-16.

    <farm-venv>/bin/python pipeline/backend_divergence_probe.py float32
    <farm-venv>/bin/python pipeline/backend_divergence_probe.py bfloat16

READ THE RESULT FIRST; the reasoning is below it.

===========================================================================
THE RESULT. Same prompt, same negative, same model, same 832x1216, same 40
steps, same 7.5 guidance, same seed 20263739, and both paths seed a
`torch.Generator("cpu")` so the STARTING LATENT IS BIT-IDENTICAL:

  bf16 / CUDA  farm-out/ep2-b20-idfix/20-evidence-wave1-s3.png      RED
  fp16 / MPS   farm-out/ep2-b20-mac-plate-0816/...-r1s1.png         PURPLE
  fp32 / MPS   farm-out/ep2-b20-dtype-probe-0816/...float32...      PURPLE
  bf16 / MPS   farm-out/ep2-b20-dtype-probe-0816/...bfloat16...     PURPLE

Mean absolute pixel difference (the statistic was falsified before it was
quoted: self-vs-self 0.000, self-vs-plus-ten 9.970):

  CUDA vs any MPS ............ 60.6 - 61.1   different pictures entirely
  fp16 vs fp32 on MPS ........  3.22         the same picture
  bf16 vs fp16/fp32 on MPS ... 11.1 - 11.2   the same picture

THE BACKEND DOMINATES DTYPE BY 6x TO 20x, and the single-variable proof is
the bf16/MPS cell: SAME DTYPE as the box, different hardware, MAE 60.65.

  => PRECISION IS EXONERATED. fp16 is not a hue artifact, there is no
     one-line dtype fix, and NO MAC PLATE NEEDS REDRAWING ON PRECISION
     GROUNDS.
  => THE MAC CANNOT PREVIEW WHAT THE BOX WILL PRODUCE. Any argument of the
     form "this wording was proven on the Mac, so the box will do it" is
     void. A Mac plate is evidence about a PICTURE, never a prediction
     about a PROMPT on the other machine.
  => THE PURPLE CANON MUST BE ENFORCED ON THE BOX PATH IN WORDS. The Mac
     returns purple with no colour word at all; the box returned red,
     crimson, maroon and wine at 8 of 8 seeds on the same wording. The
     Mac's free purple does not travel.

WHY THE MECHANISM IS NOT NAMED HERE. Because it is not known, and a
plausible story would be worse than the gap. The tempting one --- chaotic
amplification of rounding --- DIES ON THIS FILE'S OWN NUMBERS: fp16-to-fp32
is a far larger numerical change than CUDA-to-MPS rounding, and it moves
the image by MAE 3. A sampler that shrugs off fp16-to-fp32 is not a sampler
whose output is being scrambled by kernel rounding. Both machines are
pinned to diffusers 0.29.2 (`pipeline/ONBOARD-WINDOWS.md` line 149 pins the
box; the Mac reports 0.29.2), both resolve to EulerAncestralDiscrete-
Scheduler with identical config. Unverified candidates, both needing the
box to test: MPS internally upcasting so the requested dtype barely binds,
and a checkpoint-revision difference between the two caches. CANNOT
DETERMINE --- the variable is identified, the reason it exists is not.

===========================================================================
THE HOLE THIS CLOSED, and how it stayed open. On 2026-08-16 three beat-20
frames were read by blind cold readers and all three came back purple ---
INCLUDING THE CONTROL, whose prompt contains no colour word. That made the
claim "adding the colour word fixes the colour" unsupported, because the
thing without the word passed too.

The two conditions turned out to be BYTE-IDENTICAL in prompt and negative,
and today's "control" seed 20263739 is literally one of the four seeds of
the 08-12 batch the founder rejected. So the colour word was never the
variable and could not have been.

It stayed open because `plate_scratch.py` DRAFTS[20] asserted that the
rejected 08-12 frames "were drawn on CUDA with an IP-Adapter reference this
Mac does not have, so they cannot serve as the control for an MPS render".
THAT WAS FALSE --- `render_wave_sample.py`, which drew them, contains no
IP-Adapter code at all; the IP-Adapter frames are a different directory
(`farm-out/ep2-b20-ipa-frozen-0812/`, written by `goblin_ipa_sample.py` at
scale 0.6). A lane talked itself out of the one comparison that would have
shown the answer. Corrected in that file alongside this commit.

WHAT THIS FILE IS NOT. It is not a plate and it certifies nothing about
beat 20. It deliberately re-draws the FAILING 08-12 composition, so its
level gaze, its mature-tree branch, its off-frame adult hands and the extra
faces in the grass are EXPECTED and are not scored. Beat 20 remains
unsolved against its own `done_when`.

$0. Apple MPS. Leaves the rtx5090 free.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "farm-out" / "ep2-b20-dtype-probe-0816"

BASE = "cagliostrolab/animagine-xl-3.1"
W, H = 832, 1216
STEPS, GUIDANCE = 40, 7.5
SEED = 20263739          # the exact seed of 08-12 s3 AND of today's r1s1

# Byte-identical to farm-out/ep2-b20-idfix/20-evidence-wave1-s3.yaml and to
# farm-out/ep2-b20-mac-plate-0816/20-evidence-mac-plate-r1s1.yaml. Do not
# "improve" these strings -- the whole value of the probe is that they are
# unchanged. There is no colour word anywhere in either.
POS = ("1boy, a small goblin boy, green skin, bald head, patchwork cloak, solo, "
       "in a sunny grassy field, raises a ripe fig in both hands in front of him "
       "like evidence, huge eyes widening as he looks up at a bare branch above. "
       "Warm amber afternoon light, cinematic lighting, detailed, newest, "
       "masterpiece, best quality, very aesthetic")
NEG = ("photorealistic, text, girl, child, glowing eyes, glowing orb, dark, night, "
       "dusk, sunset, dim lighting, moody lighting, low key, shadows dominant, "
       "photorealism, leaf on head, plant girl, alraune, monster girl, flower on "
       "head, head wreath, hair ornament, leaf hair ornament, plant hair, "
       "female goblin, elf")

DONE_WHEN = (
    "DIAGNOSTIC, NOT A PLATE. Nothing about beat 20 passes or fails on this "
    "frame -- it carries the failing 08-12 composition on purpose, and its "
    "gaze, branch, off-frame adult hands and extra grass faces are EXPECTED "
    "and are not scored. The only question asked of it: a blind cold reader, "
    "given the frame and nothing else and asked `what colour is the fruit?`, "
    "answers RED-family or PURPLE-family. RED-family would attribute the "
    "08-12 red to PRECISION and condemn the Mac plate path as a colour "
    "instrument; PURPLE-family exonerates the dtype and makes it CUDA-vs-MPS "
    "backend divergence. ANSWERED 2026-08-16: purple at BOTH fp32 and bf16, "
    "from a prompt with no colour word -- so it is the backend."
)


def main() -> int:
    import torch
    from diffusers import StableDiffusionXLPipeline

    name = sys.argv[1] if len(sys.argv) > 1 else "float32"
    dtype = {"float32": torch.float32,
             "bfloat16": torch.bfloat16,
             "float16": torch.float16}[name]

    OUT.mkdir(parents=True, exist_ok=True)
    print("=== loading %s as %s on mps ===" % (BASE, name), flush=True)
    t_load = time.time()
    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE, torch_dtype=dtype, use_safetensors=True)
    pipe.to("mps")
    print("MODEL_LOADED mps/%s in %.0fs  scheduler=%s"
          % (name, time.time() - t_load, pipe.scheduler.__class__.__name__),
          flush=True)

    # Same token guard plate_scratch enforces: SDXL truncates at 77 silently.
    tok = pipe.tokenizer
    for label, s in (("positive", POS), ("negative", NEG)):
        n = len(tok(s).input_ids)
        print("TOKENS %s %d/77 %s" % (label, n, "TRUNCATED!!" if n > 77 else "ok"),
              flush=True)
        if n > 77:
            print("!! would be truncated silently. Refusing to draw.")
            return 5

    g = torch.Generator("cpu").manual_seed(SEED)
    t0 = time.time()
    img = pipe(prompt=POS, negative_prompt=NEG, width=W, height=H,
               num_inference_steps=STEPS, guidance_scale=GUIDANCE,
               generator=g).images[0]
    dt = time.time() - t0

    stem = "20-evidence-dtype-probe-%s-mps-s1" % name
    png = OUT / (stem + ".png")
    img.save(png)
    sha = hashlib.sha256(png.read_bytes()).hexdigest()
    meta = {
        "platform": "local-gpu (Apple Silicon, MPS)",
        "model": BASE,
        "model_licence": "CreativeML Open RAIL++-M (use restrictions travel; D15)",
        "cost_usd": 0.00,
        "shot_beat": 20,
        "beat_slug": "evidence",
        "size": "%dx%d" % (W, H),
        "steps": STEPS,
        "guidance": GUIDANCE,
        "seed": SEED,
        "torch_dtype": name,
        "device": "mps",
        "render_seconds": round(dt, 1),
        "png_sha256": sha,
        "prompts_from": ("BYTE-IDENTICAL to farm-out/ep2-b20-idfix/"
                         "20-evidence-wave1-s3.yaml (bf16/cuda, RED) and to "
                         "farm-out/ep2-b20-mac-plate-0816/"
                         "20-evidence-mac-plate-r1s1.yaml (fp16/mps, PURPLE). "
                         "Same seed as both. shots.md UNTOUCHED."),
        "prompt": POS,
        "negative_prompt": NEG,
        "done_when": DONE_WHEN,
        "why_this_plate": __doc__.strip(),
        "founder_verdict": None,
        "approved": False,
        "provisional": True,
        "revision": 1,
        "scored": False,
    }
    (OUT / (stem + ".yaml")).write_text(
        "\n".join("%s: %s" % (k, json.dumps(v)) for k, v in meta.items()) + "\n")
    print("wrote %s  (%.1fs, seed %d, %s)" % (png, dt, SEED, name), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
