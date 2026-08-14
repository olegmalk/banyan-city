#!/usr/bin/env python3
"""Draw ONE fruit study on Apple MPS, $0, for THE FIG PROTOCOL.

WHY A STUDY AND NOT A BEAT. Nine rounds have judged the fig inside beat 01 and
beat 18 scene frames, where the fruit occupies ~5% of a 832x1216 frame and the
last four rounds were all backlit silhouettes. You cannot ask "what fruit is
this?" of a thing the reader cannot see. This script isolates the variable: one
fruit, filling the frame, front-lit, on a plain ground. If the recipe cannot
make a legible fig at full frame it will never make one at 5%, and if it can,
the wording transplants into the beat prompts.

WHY THE WORD `fig` IS NOT IN LOOP 1'S POSITIVE. `taste/steward-model.ledger.yaml`
(`ep2-b01-fig-route-0810`, the_evidence_under_it) records that `fig` "names the
LEAF in this checkpoint's vocabulary" -- 0 of 8 on the two wordings that used it,
then 0 of 24 across seven further rounds on "one small round green fruit". The
2026-08-14 leaf round confirmed the same thing from the other side: asking for
fig LEAVES produced the leaf 2 of 4 first try. So loop 1 describes the SHAPE and
lets the word go.

ONE image per invocation. That is the point (CLAUDE.md, ONE SAMPLE BEFORE ANY
BATCH). There is no --count.

    <cb-venv>/bin/python3 pipeline/fig_study.py \
        --prompt-file p.txt --negative-file n.txt --out OUT.png [--seed N] \
        [--steps 40] [--cfg 7.0] [--w 1024] [--h 1024]
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import sys
from pathlib import Path

BASE = "cagliostrolab/animagine-xl-3.1"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--negative-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260815)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--cfg", type=float, default=7.0)
    ap.add_argument("--w", type=int, default=1024)
    ap.add_argument("--h", type=int, default=1024)
    a = ap.parse_args()

    import torch
    from diffusers import StableDiffusionXLPipeline

    prompt = Path(a.prompt_file).read_text(encoding="utf-8").strip()
    negative = Path(a.negative_file).read_text(encoding="utf-8").strip()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    # THE 77-TOKEN GATE. Loop 1 of the fig protocol sent a 157-token positive and
    # CLIP silently dropped everything after "woody twig stem" -- the colour, the
    # bloom, the ribs, the framing and the quality tags never reached the model,
    # so the round tested a prompt that was never sent. diffusers only WARNS. A
    # study whose whole point is which words bind cannot run on a truncated
    # string, so this refuses instead.
    from transformers import CLIPTokenizer

    tok = CLIPTokenizer.from_pretrained(BASE, subfolder="tokenizer")
    limit = tok.model_max_length  # 77 incl. BOS/EOS
    bad = []
    for label, text in (("positive", prompt), ("negative", negative)):
        n = len(tok(text)["input_ids"])
        print(f"[fig_study] {label}: {n}/{limit} tokens")
        if n > limit:
            bad.append(f"{label} is {n} tokens, {n - limit} over the {limit} limit")
    if bad:
        print("[fig_study] REFUSING: " + "; ".join(bad), file=sys.stderr)
        return 2

    print(f"[fig_study] base={BASE} {a.w}x{a.h} steps={a.steps} cfg={a.cfg} seed={a.seed}")
    print(f"[fig_study] POSITIVE: {prompt}")
    print(f"[fig_study] NEGATIVE: {negative}")

    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE, torch_dtype=torch.float16, use_safetensors=True, variant="fp16"
    ).to("mps")
    pipe.set_progress_bar_config(disable=False)

    gen = torch.Generator(device="cpu").manual_seed(a.seed)
    img = pipe(
        prompt=prompt,
        negative_prompt=negative,
        width=a.w,
        height=a.h,
        num_inference_steps=a.steps,
        guidance_scale=a.cfg,
        generator=gen,
    ).images[0]
    img.save(out)

    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    side = out.with_suffix(out.suffix + ".meta.yaml")
    side.write_text(
        "# fig_study.py sample -- NOT canon, NOT approved.\n"
        + json.dumps(
            {
                "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
                "model": BASE,
                "device": "mps",
                "width": a.w,
                "height": a.h,
                "steps": a.steps,
                "cfg": a.cfg,
                "seed": a.seed,
                "positive": prompt,
                "negative": negative,
                "sha256": sha,
                "approved": False,
                "cost_usd": 0.0,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"[fig_study] wrote {out} sha256={sha[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
