#!/usr/bin/env python3
r"""ONE CELL. Is the tan skin the CONTROLNET, or is it the PROMPT SHAPE?

WHAT THE LADDER MEASURED, AND WHY IT DOES NOT YET NAME A CAUSE.
`lora-jerry-v3-ladder-0822` ran 24 cells on one checkpoint at one weight (0.8):

  B1, 15 cells, NO skeleton, caption-shaped prompts   -> SAGE, 15 of 15.
  B2,  6 cells, SKELETON, round-one's prompt          -> TAN,   0 of 6.

Same weights, same weight, same driver, same seed family. The skin is his in
every cell without a skeleton and in none of the cells with one. That isolates
the defect to something the B2 arm does and the B1 arm does not -- but the B2
arm changes TWO things at once, and nobody noticed until the frames came back:

  1. it loads a ControlNet at conditioning scale 1.0, and
  2. IT USES A DIFFERENT PROMPT SHAPE. B1's prompts are caption-shaped --
     `bnyjerry, 1boy, solo, standing, looking at viewer, <framing>, <setting>,
     <light>, anime style, cel shading, ...` -- which is the exact ten-clause
     form all 24 training captions take. B2's prompt is round one's, kept byte
     for byte for comparability with the filed v2 failures, and it is NOT that
     shape: `bnyjerry, 1boy, solo, in tall grass, detailed cinematic anime,
     masterpiece, best quality, very aesthetic`. No framing clause, no light
     clause, no `cel shading`.

An off-distribution prompt is a completely ordinary reason for a character LoRA
to render a washed-out attribute, and `cel shading` in particular is the clause
most likely to be carrying the flat sage fill. So the ladder's B2 arm cannot
distinguish "the pose net desaturates him" from "we asked in a dialect the
trigger was not trained in", and those two have VERY different costs: the first
needs a block-weight sweep and a driver change, the second is free.

THIS CELL IS THE DISCRIMINATOR AND IT IS ONE RENDER. Everything is the ladder's
b2-seat-s1, byte for byte -- same checkpoint and sha, same seat skeleton at
scale 1.0, same weight 0.8, same seed, same negative, same steps and cfg --
EXCEPT the positive prompt, which becomes caption-shaped. The seat cell is the
one chosen because it ALREADY ADOPTED THE POSE, so if the skin comes back sage
this single frame is a full P1+P2 pass and the bar's failure was an artefact of
how we asked.

  sage  -> the prompt shape. B2 is re-run on caption-shaped prompts, free.
  tan   -> the ControlNet path. The block-weight sweep is next, with a sharper
           target than it was ranked with: not "free the composition while
           keeping the face" but "keep the PALETTE while the pose net drives".

ONE SAMPLE BEFORE ANY BATCH -- CLAUDE.md, founder 2026-08-03. The recipe change
here is the prompt shape, so exactly one cell renders and the six-cell re-run
waits for a look at it.

  python3 pipeline/lora/emit_v3_capshape_probe_0822.py            # dry
  python3 pipeline/lora/emit_v3_capshape_probe_0822.py --write
"""
from __future__ import annotations

import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import emit_ladder_jerry_v3_0822 as L                        # noqa: E402

JOB = "lora-jerry-v3-capshape-0822"
WORK = r"C:\banyan-farm\%s" % JOB
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB
OUT = "pipeline/lora/capshape-jerry-v3-0822.yaml"

# THE ONE VARIABLE. B1's shape, with B2's setting word in the setting slot so
# the SCENE does not move either -- `in tall grass` is what round one asked for
# and `tall grass` is a ground two of the training frames name. The only thing
# that changes against b2-seat-s1 is the SHAPE of the sentence.
CAPSHAPE_PROMPT = (
    "bnyjerry, 1boy, solo, sitting, looking at viewer, full body, tall grass, "
    "soft daylight, anime style, cel shading, masterpiece, best quality, "
    "very aesthetic")

NOTE = (
    "THE DISCRIMINATOR, AND IT IS ONE CELL. The v3 ladder came back SAGE on 15 "
    "of 15 cells with no skeleton and TAN on 6 of 6 with one, at the same "
    "checkpoint and the same weight 0.8. But the B2 arm changed two things at "
    "once: it loaded a ControlNet AND it used round one's prompt, which is not "
    "the ten-clause caption shape all 24 training captions take and carries "
    "neither a framing clause, a light clause nor `cel shading`. This cell is "
    "b2-seat-s1 with the prompt made caption-shaped and NOTHING ELSE MOVED -- "
    "same seat skeleton at scale 1.0, same lora sha, same weight 0.8, same "
    "seed 20260822, same negative, 40 steps, cfg 7.5, strength 1.0, pad-crop "
    "0, blur 0. SAGE means the bar failed on dialect and the fix is free; TAN "
    "means the pose net is desaturating him and the block-weight sweep is next.")


def main() -> int:
    write = "--write" in sys.argv
    lora, sha, ckpt = L.resolve_lora("")

    c = L.cell("capshape-seat-s1", lora=lora, lora_sha=sha, weight=L.SHIP_WEIGHT,
               prompt_file="prompt.txt",
               skeleton=L.SKELETONS["seat"][0], seed=L.B2_SEEDS[0], note=NOTE)
    # `cell()` builds paths against the LADDER's work dir; retarget them here so
    # this job cannot read or write another job's files. Done by substitution
    # rather than by a parameter so the two jobs provably share one code path.
    c["argv"] = [a.replace(L.WORK, WORK) for a in c["argv"]]

    steps = [{"name": "fetch", "argv": [L.PY_RENDER, r"%s\fetch_hints.py" % WORK]},
             c,
             {"name": "publish", "argv": [L.PY_RENDER, "-c", L.PUB_PY % (
                 WORK.replace("\\", "/") + "/out",
                 FARMOUT.replace("\\", "/"), JOB)]}]

    pay = {k.replace(L.WORK, WORK): v for k, v in L.payloads().items()
           if k.endswith(("inpaint_fruit.py", "negative.txt", "fetch_hints.py"))}
    pay[r"%s\prompt.txt" % WORK] = CAPSHAPE_PROMPT
    pay[r"%s\fetch_hints.py" % WORK] = pay[
        r"%s\fetch_hints.py" % WORK].replace(L.WORK, WORK)

    spec = {
        "id": JOB, "task": JOB, "node": "002b-first-citizen",
        "runner": "box", "needs_gpu": True, "needs": ["cuda", "vram20"],
        "priority": 62, "max_attempts": 1, "est_minutes": 4, "sample": True,
        "owner": "the goblin v3 lane, 2026-08-22",
        "consumer": (
            "THE READING OF THE v3 LADDER, and through it the founder's page. "
            "The ladder's B2 arm failed on ONE clause -- his skin -- and this "
            "cell decides whether that clause failed because of the pose net "
            "or because of how the question was phrased. The two answers have "
            "very different costs and only one of them needs a driver change."),
        "success": (
            "ONE 832x1216 png whose SKIN COLOUR can be read against "
            "b2-seat-s1. Either answer lands the cell: sage says the bar "
            "failed on prompt dialect, tan says the pose net desaturates him. "
            "A frame that loses the seat is the uninformative outcome and the "
            "only real failure here."),
        "why": (
            "THE LADDER ISOLATED A DEFECT TO AN ARM THAT CHANGES TWO THINGS AT "
            "ONCE. Sage in 15 of 15 cells with no skeleton, tan in 6 of 6 with "
            "one, same checkpoint and same weight -- but the skeleton arm also "
            "swapped the prompt to round one's wording, kept byte-identical "
            "for comparability with the filed v2 failures and NOT in the "
            "ten-clause caption shape the trigger was trained on. It carries "
            "no framing clause, no light clause and no `cel shading`, which is "
            "the clause most likely to be holding the flat sage fill.\n\n"
            "AN OFF-DISTRIBUTION PROMPT IS AN ORDINARY REASON for a character "
            "LoRA to wash out an attribute, so the ladder's B2 arm cannot "
            "currently tell that apart from the pose net doing it. One render "
            "can. The seat cell is used because it ALREADY ADOPTED THE POSE, "
            "so a sage result here is a complete P1+P2 pass on a cell the bar "
            "scored as a failure."),
        "env": ({
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        }),
        "checkpoint": ckpt,
        "checkpoint_sha256": sha,
        "the_one_variable": (
            "THE POSITIVE PROMPT'S SHAPE, and nothing else. b2-seat-s1's "
            "`bnyjerry, 1boy, solo, in tall grass, detailed cinematic anime, "
            "masterpiece, best quality, very aesthetic` becomes `%s`. Same "
            "checkpoint %s, same sha, same seat skeleton at scale 1.0, same "
            "weight %s, same seed %s, same negative.txt, same 40 steps, cfg "
            "7.5, strength 1.0, --pad-crop 0, --blur 0."
            % (CAPSHAPE_PROMPT, ckpt, L.SHIP_WEIGHT, L.B2_SEEDS[0])),
        "payload": pay,
        "steps": steps,
        "artifacts": [r"%s\%s.sha256" % (FARMOUT, JOB)],
    }

    if not write:
        print("would emit %s" % OUT)
        print("  checkpoint %s sha %s" % (ckpt, sha[:16]))
        print("  ONE cell: %s" % c["name"])
        print("  prompt: %s" % CAPSHAPE_PROMPT)
        return 0
    with open(os.path.join(REPO, OUT), "w", encoding="utf-8") as fh:
        fh.write("# ONE CELL: is the v3 ladder's tan skin the ControlNet, or\n"
                 "# the prompt shape? GENERATED -- edit\n"
                 "# pipeline/lora/emit_v3_capshape_probe_0822.py.\n\n")
        yaml.safe_dump(spec, fh, sort_keys=False, width=88, allow_unicode=True)
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
