#!/usr/bin/env python3
r"""THE BLOCK-WEIGHT SWEEP: keep the PALETTE while the pose net drives.

WHY THIS IS THE MOTIVATED SPEND AND NOT A HOPEFUL ONE. v3 poses -- 4 of 6 B2
cells adopted their skeleton at weight 0.8 against a control of 0/6, including a
STRIDE the dataset never contained -- and v3 keeps his face: B1 is sage in 15 of
15 cells at the same checkpoint and the same weight. The single clause between
that and a shippable recipe is HIS SKIN UNDER A POSE NET, and three free levers
are now measured dead, one variable and one reference frame each:

  prompt dialect  lora-jerry-v3-capshape-0822    caption-shaped prompt -> TAN
  hint volume     lora-jerry-v3-cnetscale-0822   --scale 0.7 and 0.5   -> TAN
  trigger volume  lora-jerry-v3-loraweight-0822  --lora-weight 1.0/1.2 -> a nudge

The palette is not reachable by EITHER channel's volume. That is a real result
and it points somewhere specific: the defect is structural in how a FUSED LoRA
composes with the ControlNet pipeline, and per-block scaling is the one
instrument that addresses exactly that.

THE MAP IS COMMUNITY AND THE CELLS ARE NAMED FOR THE HYPOTHESIS, NOT A RESULT.
hako-mikan's sd-webui-lora-block-weight and its successor report INPUT blocks
carrying structural identity and OUTPUT blocks carrying background detail and
AESTHETIC RENDERING. Block-wise LoRA (arXiv 2403.07500) backs block-level
separation of identity from style without saying which blocks do what. So the
direction below is a hypothesis under test.

THE FIRST CELL IS THE INSTRUMENT CHECK AND IT IS NOT OPTIONAL. `flat` is
{down 1.0, mid 1.0, up 1.0} through the NEW set_adapters path. Without it a null
result is unattributable between "block weighting does not help" and "the
set_adapters wiring is not doing anything", which is the exact class of mistake
this tree keeps paying for. Read it first: it should look like a fused run.

  flat            -> the instrument works. Now read the other two.
  palette         -> {down .8, mid .8, up 1.4}. Push the aesthetic blocks.
  palette-starve  -> {down .4, mid .4, up 1.4}. Same hypothesis, harder, and
                     with the other half of the reasoning: the input blocks are
                     the ones the map says carry STRUCTURE, and structure is
                     what the pose net is already supplying, so starving them
                     should cost nothing the ControlNet is not providing.

ROUND ONE OF AT MOST TWO. If a cell lands sage WITH the seat, that is v3's
double pass and the founder page section stages. If all three are tan, the
lever is closed and the finding is that the palette is unreachable by any
weighting of a fused-or-scaled LoRA on this path -- worth filing, and the end of
the cheap board.

THE DEFAULT PATH IS UNTOUCHED AND THAT IS ASSERTED, NOT ASSUMED.
`inpaint_fruit.py --selftest` reproduces the filed no-LoRA sidecar
(ep2-b08-str70-0820) AND the LoRA block of a filed FUSED run (b2-seat-s1 of the
v3 ladder, the very cell this sweep varies against) byte for byte. 73/73.

  python3 pipeline/lora/emit_v3_blockweight_sweep_0822.py            # dry
  python3 pipeline/lora/emit_v3_blockweight_sweep_0822.py --write
"""
from __future__ import annotations

import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import emit_ladder_jerry_v3_0822 as L                        # noqa: E402

JOB = "lora-jerry-v3-blockweight-0822"
WORK = r"C:\banyan-farm\%s" % JOB
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB
OUT = "pipeline/lora/blockweight-jerry-v3-0822.yaml"

# THE PROMPT IS b2-seat-s1's, BYTE FOR BYTE. capshape already showed the shape
# is not the variable, so it goes back to round one's wording -- which keeps this
# job directly comparable to the filed v2 failures AND to the ladder cell it is
# varying against. Two probes that each move a different single thing off the
# same reference frame are readable; two that each move two are not.
PROMPT = L.B2_PROMPT

PRESETS = ("flat", "palette", "palette-starve")

NOTE = (
    "BLOCK-WEIGHT SWEEP, preset `%s`, and it is the ONE variable against the "
    "ladder's b2-seat-s1. That cell held the seat and lost his skin. Three free "
    "levers are already measured dead: prompt dialect (capshape: TAN), hint "
    "volume (--scale 0.7 and 0.5: TAN), trigger volume (--lora-weight 1.0 and "
    "1.2: a nudge only). So the palette is not reachable by either channel's "
    "VOLUME, and this scales the LoRA PER UNET BLOCK instead -- set_adapters, "
    "no fuse, on the hypothesis that output blocks carry aesthetic rendering "
    "while input blocks carry the structure the pose net is already supplying. "
    "THE MAP IS COMMUNITY (hako-mikan sd-webui-lora-block-weight; arXiv "
    "2403.07500 backs block-level identity/style separation without naming "
    "blocks), so this is a hypothesis under test and the preset is named for "
    "it, not for a result. `flat` is the INSTRUMENT CHECK and must be read "
    "first -- a flat 1.0 through set_adapters should look like a fused run, and "
    "without it a null result cannot be told apart from broken wiring. "
    "Everything else is b2-seat-s1: same checkpoint and sha, same seat skeleton "
    "at conditioning scale 1.0, same seed 20260822, same prompt.txt and "
    "negative.txt, 40 steps, cfg 7.5, strength 1.0, --pad-crop 0, --blur 0. "
    "WHAT A PASS LOOKS LIKE: desaturated sage skin AND the knees still up. "
    "Either alone is not a pass -- a sage standing goblin is what v2 already "
    "gives and a seated tan one is what the ladder already gave.")


def main() -> int:
    write = "--write" in sys.argv
    lora, sha, ckpt = L.resolve_lora("")

    cells = []
    for sc in PRESETS:
        c = L.cell("blockweight-seat-%s" % sc, lora=lora,
                   lora_sha=sha, weight=L.SHIP_WEIGHT, prompt_file="prompt.txt",
                   skeleton=L.SKELETONS["seat"][0], seed=L.B2_SEEDS[0],
                   note=NOTE % sc)
        # `cell()` hard-codes scale 1.0 and builds paths against the LADDER's
        # work dir. Both are retargeted by substitution rather than by adding a
        # parameter, so the two jobs provably share ONE code path -- the thing
        # that makes this cell comparable to b2-seat-s1 at all.
        c["argv"] = [a.replace(L.WORK, WORK) for a in c["argv"]]
        # The hint stays at the ladder's 1.0: this probe moves the OTHER
        # channel, and the scale probe already showed 0.7/0.5 change nothing
        # about the palette. Asserted rather than assumed so the two probes
        # cannot drift into moving the same knob.
        # The hint stays at the ladder's 1.0 and --lora-weight stays at the
        # ladder's 0.8 -- both asserted, because the two probes before this one
        # each moved exactly one of them and this one must move NEITHER. On the
        # block path --lora-weight is ignored by the driver anyway; it is
        # asserted so the argv stays readable against b2-seat-s1.
        assert c["argv"][c["argv"].index("--scale") + 1] == "1.0"
        assert c["argv"][c["argv"].index("--lora-weight") + 1] == L.SHIP_WEIGHT
        c["argv"] += ["--lora-blocks", sc]
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
            "AND BOTH VOLUME KNOBS ARE NOW DEAD: --scale 0.7 and 0.5 both came "
            "back tan and both still seated, so turning the net down does not "
            "return the palette and the pose has headroom on that knob.\n\n"
            "SO TURN THE TRIGGER UP, WHICH IS THE LAST FREE FLAG. Round seven "
            "turned the LoRA DOWN and the hint UP because on v2 the trigger "
            "overrode the pose. v3 inverts that tension exactly: the pose "
            "arrives and the trigger's palette does not. The ranked next fix is "
            "a LoRA block-weight sweep, which costs an eight-line "
            "`set_adapters`-instead-of-`fuse_lora` arm on inpaint_fruit.py plus "
            "a selftest clause, welded onto a driver whose selftest reproduces "
            "a filed sidecar byte for byte and which six verdicts depend on. "
            "Spending that before the free flags are exhausted would be "
            "building a mechanism to answer a question a number might already "
            "answer, so this runs first.\n\n"
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
            "THE PER-BLOCK LoRA SCALING, and nothing else: presets %s. The prompt "
            "goes back to b2-seat-s1's exactly (%r) because capshape already "
            "ruled the wording out, and three probes that each move ONE thing off "
            "the same reference frame are readable where three that each move "
            "two are not. Same checkpoint %s, same sha, same seat skeleton at "
            "conditioning scale 1.0 (asserted in code, because the previous "
            "probe moved exactly that and the two must not blur), same seed %s, same negative.txt, 40 steps, cfg 7.5, "
            "strength 1.0, --pad-crop 0, --blur 0."
            % (" then ".join(PRESETS), PROMPT, ckpt, L.B2_SEEDS[0])),
        "payload": pay,
        "steps": steps,
        "artifacts": [r"%s\%s.sha256" % (FARMOUT, JOB)],
    }

    if not write:
        print("would emit %s" % OUT)
        print("  checkpoint %s sha %s" % (ckpt, sha[:16]))
        for c in cells:
            print("  cell %s" % c["name"])
        print("  presets: %s" % ", ".join(PRESETS))
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
