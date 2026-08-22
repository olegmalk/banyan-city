#!/usr/bin/env python3
r"""THE HINT'S OWN VOLUME KNOB, TWO POINTS, BEFORE ANY DRIVER IS TOUCHED.

WHAT IS NOW ISOLATED. The v3 ladder came back SAGE on 15 of 15 cells with no
skeleton and TAN on 6 of 6 with one, at the same checkpoint and the same weight
0.8 -- so his skin is intact in the weights and something on the ControlNet path
is taking it. `lora-jerry-v3-capshape-0822` then removed the only other
difference between the two arms: it re-ran the seat cell with a CAPTION-SHAPED
prompt, the ten-clause form all 24 training captions take, and the skin came
back TAN AGAIN with the seat still held. So it is not prompt dialect. It is the
net.

WHY THIS RUNS BEFORE THE BLOCK-WEIGHT SWEEP, WHICH IS THE RANKED FIX. The sweep
costs an eight-line arm on `inpaint_fruit.py` (replacing `fuse_lora` with
`set_adapters`, plus a selftest clause) and a new failure surface on a driver
six filed verdicts depend on. THIS COSTS A FLAG THAT ALREADY EXISTS. The two
conditioning channels are in tension over one region and `--scale` is the volume
knob on one of them; round seven turned it UP to 1.4 on v2 and nobody has ever
turned it DOWN, because until v3 the LoRA was winning and the hint needed help.
v3 inverts that. If the palette returns at 0.7 while the seat survives, the wave
ships on a number and the driver is never touched.

TWO POINTS AND NOT ONE, and that is a considered exception to the one-sample
rule rather than a lapse: the recipe does not change here at all -- no new flag,
no new code path, the same `--scale` argument the ladder already passes -- and a
single point cannot show a SLOPE. What is being read is whether palette and pose
trade smoothly or cross, which is the same shape of question the sapling weight
ladder answered with a curve. One cell at 0.7 that came back half-right would
be unreadable.

  0.7 sage + seated -> the recipe is `--scale 0.7` and this is finished.
  0.5 sage + seated -> same, at a weaker hint; read which is cleaner.
  both tan          -> the net is not doing it by volume, and the block-weight
                       sweep is next with its sharpened target: keep the PALETTE
                       while the pose net drives, not "free the composition".
  sage but standing -> palette and pose CROSS on this knob, which closes the
                       cheap route honestly and is worth as much as a pass.

  python3 pipeline/lora/emit_v3_cnetscale_probe_0822.py            # dry
  python3 pipeline/lora/emit_v3_cnetscale_probe_0822.py --write
"""
from __future__ import annotations

import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import emit_ladder_jerry_v3_0822 as L                        # noqa: E402

JOB = "lora-jerry-v3-cnetscale-0822"
WORK = r"C:\banyan-farm\%s" % JOB
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB
OUT = "pipeline/lora/cnetscale-jerry-v3-0822.yaml"

# THE PROMPT IS b2-seat-s1's, BYTE FOR BYTE. capshape already showed the shape
# is not the variable, so it goes back to round one's wording -- which keeps this
# job directly comparable to the filed v2 failures AND to the ladder cell it is
# varying against. Two probes that each move a different single thing off the
# same reference frame are readable; two that each move two are not.
PROMPT = L.B2_PROMPT

SCALES = ("0.7", "0.5")

NOTE = (
    "THE HINT'S VOLUME KNOB at scale %s, and it is the ONE variable against the "
    "ladder's b2-seat-s1. That cell held the seat and lost his skin, and "
    "lora-jerry-v3-capshape-0822 has already ruled out prompt dialect -- a "
    "caption-shaped prompt came back tan with the seat still held. So the two "
    "conditioning channels are in tension over one region and this turns one of "
    "them down. Round seven turned this knob UP to 1.4 on v2, because until v3 "
    "the LoRA was winning and the hint needed help; v3 inverts that and nobody "
    "has turned it down. Same checkpoint and sha, same seat skeleton, same "
    "weight 0.8, same seed 20260822, same prompt.txt and negative.txt, 40 "
    "steps, cfg 7.5, strength 1.0, --pad-crop 0, --blur 0. WHAT A PASS LOOKS "
    "LIKE: desaturated sage skin AND the knees still up. Either one alone is "
    "not a pass -- a sage standing goblin is what v2 already gives.")


def main() -> int:
    write = "--write" in sys.argv
    lora, sha, ckpt = L.resolve_lora("")

    cells = []
    for sc in SCALES:
        c = L.cell("cnetscale-seat-s%s" % sc.replace(".", ""), lora=lora,
                   lora_sha=sha, weight=L.SHIP_WEIGHT, prompt_file="prompt.txt",
                   skeleton=L.SKELETONS["seat"][0], seed=L.B2_SEEDS[0],
                   note=NOTE % sc)
        # `cell()` hard-codes scale 1.0 and builds paths against the LADDER's
        # work dir. Both are retargeted by substitution rather than by adding a
        # parameter, so the two jobs provably share ONE code path -- the thing
        # that makes this cell comparable to b2-seat-s1 at all.
        c["argv"] = [a.replace(L.WORK, WORK) for a in c["argv"]]
        k = c["argv"].index("--scale")
        assert c["argv"][k + 1] == "1.0", c["argv"][k + 1]
        c["argv"][k + 1] = sc
        cells.append(c)

    steps = [{"name": "fetch", "argv": [L.PY_RENDER, r"%s\fetch_hints.py" % WORK]},
             *cells,
             {"name": "publish", "argv": [L.PY_RENDER, "-c", L.PUB_PY % (
                 WORK.replace("\\", "/") + "/out",
                 FARMOUT.replace("\\", "/"), JOB)]}]

    pay = {k.replace(L.WORK, WORK): v for k, v in L.payloads().items()
           if k.endswith(("inpaint_fruit.py", "negative.txt", "fetch_hints.py"))}
    pay[r"%s\prompt.txt" % WORK] = PROMPT
    pay[r"%s\fetch_hints.py" % WORK] = pay[
        r"%s\fetch_hints.py" % WORK].replace(L.WORK, WORK)

    spec = {
        "id": JOB, "task": JOB, "node": "002b-first-citizen",
        "runner": "box", "needs_gpu": True, "needs": ["cuda", "vram20"],
        "priority": 62, "max_attempts": 1, "est_minutes": 6, "sample": True,
        "owner": "the goblin v3 lane, 2026-08-22",
        "consumer": (
            "THE GOBLIN WAVE'S RECIPE, if it lands, and the block-weight "
            "sweep's go/no-go if it does not. v3 poses and keeps his face; the "
            "single clause between it and a shippable recipe is his skin under "
            "a pose net, and this asks whether that clause is bought with a "
            "flag that already exists before an eight-line arm is welded onto a "
            "driver six filed verdicts depend on."),
        "success": (
            "TWO 832x1216 pngs read against b2-seat-s1 on BOTH clauses at once: "
            "desaturated sage skin AND the knees still up. Either clause alone "
            "is not a pass -- a sage standing goblin is what v2 already gives, "
            "and a seated tan one is what the ladder already gave. A clean "
            "CROSS, where the palette only returns at a scale that has stopped "
            "posing him, closes the cheap route honestly and is worth filing as "
            "much as a pass is."),
        "why": (
            "THE DEFECT IS NOW ISOLATED TO THE NET, ON TWO MEASUREMENTS. Sage "
            "in 15 of 15 ladder cells with no skeleton and tan in 6 of 6 with "
            "one, at the same checkpoint and weight -- so the skin is intact in "
            "the weights. Then lora-jerry-v3-capshape-0822 removed the only "
            "other difference between those two arms, re-running the seat cell "
            "with a caption-shaped prompt, and it came back TAN with the seat "
            "still held. Not dialect. The net.\n\n"
            "SO TURN THE NET DOWN, BECAUSE THAT FLAG ALREADY EXISTS. Round "
            "seven turned `--scale` UP to 1.4 on v2, since until v3 the LoRA "
            "was overriding the hint and the hint needed help. v3 inverts the "
            "tension and nobody has tried the other direction. The ranked next "
            "fix is a LoRA block-weight sweep, which costs an eight-line "
            "`set_adapters`-instead-of-`fuse_lora` arm on inpaint_fruit.py plus "
            "a selftest clause; this costs an argument the driver already "
            "parses, so it runs first.\n\n"
            "SUPERSEDED PARAGRAPH, KEPT FOR THE RECORD: the earlier framing was "
            "that the ladder isolated a defect to an arm that changes two "
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
            "THE CONDITIONING SCALE, and nothing else: 1.0 -> %s. The prompt "
            "goes back to b2-seat-s1's exactly (%r) because capshape already "
            "ruled the wording out, and two probes that each move ONE thing off "
            "the same reference frame are readable where two that each move two "
            "are not. Same checkpoint %s, same sha, same seat skeleton, same "
            "weight %s, same seed %s, same negative.txt, 40 steps, cfg 7.5, "
            "strength 1.0, --pad-crop 0, --blur 0."
            % (" and ".join(SCALES), PROMPT, ckpt, L.SHIP_WEIGHT,
               L.B2_SEEDS[0])),
        "payload": pay,
        "steps": steps,
        "artifacts": [r"%s\%s.sha256" % (FARMOUT, JOB)],
    }

    if not write:
        print("would emit %s" % OUT)
        print("  checkpoint %s sha %s" % (ckpt, sha[:16]))
        for c in cells:
            print("  cell %s" % c["name"])
        print("  scales: %s" % ", ".join(SCALES))
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
