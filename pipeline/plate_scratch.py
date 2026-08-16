#!/usr/bin/env python3
"""ONE plate sample on Apple MPS from an INLINE prompt, with provenance.

    <farm-venv>/bin/python pipeline/plate_scratch.py --beat 14 --dry
    <farm-venv>/bin/python pipeline/plate_scratch.py --beat 14

WHY THIS EXISTS RATHER THAN `render_wave_sample.py`. That path renders a draft
key out of `pipeline/wave-drafts.yaml`, so testing a new plate framing means
editing a 350 KB hand-written provenance file that other lanes are usually in.
The beat-17 plate that solved its beat on the FIRST sample (2026-08-15,
`farm-out/ep2-b17-mac-plate-0815/`) did not go that way -- it was drawn by a
scratch runner from a prompt authored for the plate test, with `shots.md`
UNTOUCHED, and its own yaml says so. This file is that precedent made reusable.

WHY IT DOES NOT WRITE `shots.md` EITHER. The shot board is the crowd-facing
artefact and its wording is the founder's. A plate test proposes a framing; if
the framing wins, the board gets updated deliberately and separately.

ONE SAMPLE, NOT A BATCH (CLAUDE.md, founder 2026-08-03). `--seeds` exists but
refuses more than one unless `--i-have-seen-a-sample` is passed, because a
recipe change gets one picture looked at before it gets four.

TOKENS ARE MEASURED ON THE REAL TOKENIZER BEFORE ANYTHING IS DRAWN. SDXL's text
encoders truncate at 77 tokens silently; a prompt that overflows loses its tail,
which is where the style anchor lives. `--dry` measures and draws nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "pipeline"))

BASE = "cagliostrolab/animagine-xl-3.1"
W, H = 832, 1216          # what every ep2 plate is drawn at
STEPS, GUIDANCE = 40, 7.5  # the beat-17 plate's settings, unchanged

# Inline plate drafts. Each is authored against that beat's `done_when` in
# review/ep2-picks/done-definitions.yaml, quoted here so the bar and the prompt
# cannot drift apart.
DRAFTS = {
    14: {
        "slug": "the-defense",
        "done_when": (
            "fingers at the dirt AND the glancing - embarrassment readable. "
            "Requires a plate where his hands and the ground are both in "
            "frame; a standing full-body plate cannot show this and should be "
            "sent back."
        ),
        "why": (
            "The only existing plate (ep2-b14-plate-0814) is exactly the "
            "standing full-body shot the definition says to send back: no "
            "hands, no ground. The beat IS the hands. This plate exists to put "
            "them in frame."
        ),
        # 96/77 on the first draft -- the tokenizer guard caught it before it
        # drew, and an overflow would have dropped the style anchor at the tail.
        "prompt": (
            "1boy, solo, lean wiry adult goblin man, green skin, bald head, "
            "patchwork cloak, crouching low, both clawed hands down at the "
            "bare earth, fingers picking at loose dirt, face turned away, "
            "embarrassed, low close-up, hands and dirt large in frame, "
            "green grass, sunny day, masterpiece, best quality, very aesthetic"
        ),
        "negative": (
            "text, standing, walking, running, full body, wide shot, distant, "
            "holding object, spear, staff, sword, stick, basket, broom, "
            "2boys, baby, child, chibi, stitches, scars, tree, forest, house, "
            "indoors, photorealism, 3d render, dark, night"
        ),
        "seed": 20260814,
    },
}

# Revisions. ONE VARIABLE PER REVISION, and the reason is written down before it
# renders. `--rev N` merges over the base draft above.
REVS = {
    (14, 2): {
        # r1 came back a correct LOW CROUCH with the ground in frame -- the
        # framing lever worked on the first sample and the standing-plate
        # problem is solved. It failed on the DIRT: his hand rests on his knee,
        # and there is no bare earth anywhere, only grass.
        #
        # THE ONE VARIABLE: `green grass` was sitting in r1's own POSITIVE,
        # competing with `bare earth` and `loose dirt` for the same ground, and
        # grass won. This revision DELETES it from the positive and names it in
        # the negative, so the dirt has nothing to compete with. A deletion, not
        # an addition -- the same shape of fix that rescued the barkboard still.
        # The hand wording is BYTE-IDENTICAL to r1 on purpose: if the fingers
        # still do not reach the soil once the grass is gone, that is a separate
        # finding about verb binding and it must not be confounded with this one.
        "prompt": (
            "1boy, solo, lean wiry adult goblin man, green skin, bald head, "
            "patchwork cloak, crouching low, both clawed hands down at the "
            "bare earth, fingers picking at loose dirt, face turned away, "
            "embarrassed, low close-up, hands and dirt large in frame, "
            "patch of bare brown soil, masterpiece, best quality, very aesthetic"
        ),
        "negative": (
            "text, standing, walking, running, full body, wide shot, distant, "
            "grass, lawn, meadow, "
            "holding object, spear, staff, sword, stick, basket, broom, "
            "2boys, baby, child, chibi, stitches, scars, tree, forest, house, "
            "indoors, photorealism, 3d render, dark, night"
        ),
    },
}


def measure(pipe, text: str) -> tuple[int, bool]:
    tok = pipe.tokenizer
    ids = tok(text, truncation=False)["input_ids"]
    return len(ids), len(ids) > tok.model_max_length


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beat", type=int, required=True)
    ap.add_argument("--node", default="002b-first-citizen")
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--i-have-seen-a-sample", action="store_true")
    ap.add_argument("--rev", type=int, default=1, help="revision of the draft")
    ap.add_argument("--dry", action="store_true", help="measure, draw nothing")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if a.beat not in DRAFTS:
        print("!! no inline draft for beat %d. Present: %s"
              % (a.beat, sorted(DRAFTS)))
        return 4
    d = dict(DRAFTS[a.beat])
    if a.rev != 1:
        if (a.beat, a.rev) not in REVS:
            print("!! no rev %d for beat %d" % (a.rev, a.beat)); return 4
        d.update(REVS[(a.beat, a.rev)])

    if a.seeds > 1 and not a.i_have_seen_a_sample:
        print("!! %d seeds requested. ONE SAMPLE BEFORE ANY BATCH "
              "(CLAUDE.md, founder 2026-08-03) -- a recipe change gets one "
              "picture looked at first. Pass --i-have-seen-a-sample only if "
              "one has actually been seen." % a.seeds)
        return 8

    # STEWARDSHIP §6: no media from a node the founder has not approved.
    from render_local import approved  # noqa: E402
    if not approved("sapling", a.node):
        print("!! node %s is not founder-approved (§6). Refusing." % a.node)
        return 9

    out_dir = Path(a.out) if a.out else (
        REPO / "farm-out" / ("ep2-b%02d-mac-plate-%s" % (a.beat, date.today().strftime("%m%d"))))
    out_dir.mkdir(parents=True, exist_ok=True)

    import torch                                                  # noqa: E402
    from diffusers import StableDiffusionXLPipeline               # noqa: E402

    print("loading %s ..." % BASE, flush=True)
    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE, torch_dtype=torch.float16, use_safetensors=True)
    pipe.to("mps")

    np_, ntrunc = measure(pipe, d["prompt"])
    nn_, ntruncn = measure(pipe, d["negative"])
    print("TOKENS positive %d/77 %s" % (np_, "TRUNCATED!!" if ntrunc else "ok"))
    print("TOKENS negative %d/77 %s" % (nn_, "TRUNCATED!!" if ntruncn else "ok"))
    if ntrunc or ntruncn:
        print("!! a prompt overflows 77 tokens and its tail would be dropped "
              "silently. Refusing to draw. Shorten it.")
        return 5
    if a.dry:
        print("--dry: measured only, nothing drawn.")
        return 0

    for i in range(a.seeds):
        seed = d["seed"] + i
        g = torch.Generator("cpu").manual_seed(seed)
        t0 = time.time()
        img = pipe(prompt=d["prompt"], negative_prompt=d["negative"],
                   width=W, height=H, num_inference_steps=STEPS,
                   guidance_scale=GUIDANCE, generator=g).images[0]
        dt = time.time() - t0
        stem = "%02d-%s-mac-plate-r%ds%d" % (a.beat, d["slug"], a.rev, i + 1)
        png = out_dir / (stem + ".png")
        img.save(png)
        sha = hashlib.sha256(png.read_bytes()).hexdigest()
        meta = {
            "platform": "local-gpu (Apple Silicon, MPS)",
            "model": BASE,
            "model_licence": "CreativeML Open RAIL++-M (use restrictions travel; D15)",
            "cost_usd": 0.00,
            "shot_beat": a.beat,
            "beat_slug": d["slug"],
            "size": "%dx%d" % (W, H),
            "steps": STEPS,
            "guidance": GUIDANCE,
            "seed": seed,
            "render_seconds": round(dt, 1),
            "png_sha256": sha,
            "prompts_from": "authored for this plate test (shots.md UNTOUCHED)",
            "prompt": d["prompt"],
            "negative_prompt": d["negative"],
            "done_when": d["done_when"],
            "why_this_plate": d["why"],
            "founder_verdict": None,
            "revision": a.rev,
            "scored": False,
        }
        (out_dir / (stem + ".yaml")).write_text(
            "\n".join("%s: %s" % (k, json.dumps(v)) for k, v in meta.items()) + "\n")
        print("wrote %s  (%.1fs, seed %d)" % (png, dt, seed), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
