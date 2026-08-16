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
    8: {
        "slug": "inside-him",
        "done_when": (
            "the clipboard comes DOWN and the point goes to the BELLY, both "
            "legible; both guards and the scavenger in frame, since a point "
            "needs its target visible."
        ),
        "why": (
            "Beat 08 has NO VERDICT YET and the reason is visible in one "
            "look: the picture its motion takes were animated from "
            "(farm-out/ep2-b08-twohander/b19-init-704x1280.png, sha 6c403952) "
            "is a COSTUME CARD -- one figure, waist-up, eyes closed, on flat "
            "blank paper, no field, no second guard and no scavenger. Its "
            "done_when needs three bodies and a belly in frame. No wording "
            "reaches a target that is not in the picture, which is why every "
            "lever failed. Cycle 018 measured the other half of this: on beat "
            "17's WIDE full-body plate with ~40% headroom the engine moved a "
            "whole body in 12 of 12 takes. This plate gives beat 08 beat 17's "
            "composition -- wide, full-length, real field, room above the "
            "heads -- and changes nothing else."
        ),
        "prompt": (
            "3boys, full body, wide shot, scenery, standing in a green field, "
            "two adult guard men in uniform facing a lean adult goblin man, "
            "green skin, bald head, patchwork cloak, near guard holds a "
            "wooden clipboard at chest height, small figures low in frame, "
            "wide blue sky above, sunny day, masterpiece, best quality"
        ),
        "negative": (
            "text, close-up, portrait, upper body, cropped, bust, "
            "1boy, 2boys, 4boys, solo, white background, simple background, "
            "baby, child, chibi, stitches, scars, spear, staff, sword, "
            "tree, forest, house, indoors, photorealism, 3d render, dark, night"
        ),
        "seed": 20260816,
    },
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
    (8, 2): {
        # r1 came back UNUSABLE and in an instructive way: a colossal
        # two-headed goblin filling the upper half as a piece of SCENERY, and
        # three tiny identically-uniformed guards at the bottom edge seen from
        # BEHIND -- no scavenger among them, no clipboard, no faces. The
        # composition lever half-worked: the field, the sky, the headroom and
        # the full-length staging are all there. What broke is SCALE.
        #
        # THE ONE VARIABLE: `small figures low in frame`. It was lifted from
        # the beat-17 plate, where it is correct because that plate is `solo`
        # and the one figure keeps the frame. Here it shrank the real people
        # to specks, and a canvas with nothing of subject size left in it got
        # the remaining space filled with the only other noun available -- the
        # goblin, drawn at scenery scale. One phrase produced both defects, so
        # one phrase is what changes. Everything else, including `scenery`,
        # `wide shot`, the sky clause and the whole negative, is BYTE-IDENTICAL
        # to r1: if the goblin still comes back as landscape once the figures
        # are people-sized, that is a separate finding about the `scenery` tag
        # and it must not be confounded with this one.
        "prompt": (
            "3boys, full body, wide shot, scenery, standing in a green field, "
            "two adult guard men in uniform facing a lean adult goblin man, "
            "green skin, bald head, patchwork cloak, near guard holds a "
            "wooden clipboard at chest height, three men standing together, "
            "wide blue sky above, sunny day, masterpiece, best quality"
        ),
    },
    (8, 3): {
        # r2's variable WORKED and the prediction written into r2 above came
        # true, in the same render. Dropping `small figures low in frame` for
        # `three men standing together` made the three people person-sized,
        # full length, standing on a path FACING THE LENS, one of them holding
        # a board -- r1's specks-seen-from-behind are gone. And the colossal
        # goblin came back anyway, barely changed. r2 said in advance: "if the
        # goblin still comes back as landscape once the figures are
        # people-sized, that is a separate finding about the `scenery` tag."
        # It is, so `scenery` is r3's one variable and it is DELETED.
        #
        # Why that tag and not the goblin words: `scenery` is an animagine
        # composition tag that promotes the LANDSCAPE to subject. Beat 17's
        # plate carries it safely because that prompt is `solo` -- one figure
        # owns the frame and the tag only opens the sky behind him. Here it is
        # competing with three small people for what the picture is OF, and a
        # green cloaked hill is what it built out of the only large noun in
        # the prompt. Everything else, including the whole negative and the
        # `three men standing together` clause r2 proved, is BYTE-IDENTICAL.
        "prompt": (
            "3boys, full body, wide shot, standing in a green field, "
            "two adult guard men in uniform facing a lean adult goblin man, "
            "green skin, bald head, patchwork cloak, near guard holds a "
            "wooden clipboard at chest height, three men standing together, "
            "wide blue sky above, sunny day, masterpiece, best quality"
        ),
    },
    (8, 4): {
        # r3's hypothesis is FALSIFIED and that is worth as much as a pass.
        # Deleting `scenery` changed the giant not at all -- it is still there,
        # same pose, same scale. So the colossus is not that tag, and nobody
        # should spend another sample on it. r3 did move the figures closer and
        # larger (a side effect of the deletion, noted, not claimed as a lever)
        # and they now read as three uniformed men holding boards, facing the
        # lens, full length, in a field with sky above -- the COMPOSITION beat
        # 08 has never had. Two defects remain: the colossus, and all three men
        # being goblins where the beat needs two human guards and one goblin.
        #
        # THE ONE VARIABLE: the NEGATIVE, which has been byte-identical through
        # r1-r3 and has never once named the thing that keeps happening. Three
        # samples have now shown the failure is not scale (r2) and not the
        # `scenery` tag (r3), which leaves the positive's own nouns building a
        # goblin at landscape size in the empty upper half. A negative is the
        # cheapest instrument that addresses it directly and it is one edit.
        # The positive stays BYTE-IDENTICAL to r3, so if the colossus survives
        # a negative that forbids it by name, the cause is structural -- the
        # `wide blue sky above` clause reserving a subject-sized hole -- and
        # that, not more words, is what r5 would test.
        "prompt": (
            "3boys, full body, wide shot, standing in a green field, "
            "two adult guard men in uniform facing a lean adult goblin man, "
            "green skin, bald head, patchwork cloak, near guard holds a "
            "wooden clipboard at chest height, three men standing together, "
            "wide blue sky above, sunny day, masterpiece, best quality"
        ),
        # The first draft of this negative measured 90/77 and the tokenizer
        # guard refused to draw it -- its tail, which is where the anti-card
        # terms live, would have been dropped in silence. Trimmed to fit by
        # deleting terms no sample has ever needed: `titan`, `looming figure`,
        # `mountain shaped like a face`, `bust`, `baby`, `staff`, `chibi`,
        # `scars`, `stitches`. Named here so the trim is visible and nobody
        # reads the shorter list as a second variable.
        "negative": (
            "giant, colossal, monster, kaiju, statue, face in the sky, "
            "text, close-up, portrait, upper body, cropped, "
            "1boy, 2boys, 4boys, solo, white background, simple background, "
            "child, spear, sword, tree, forest, house, indoors, "
            "photorealism, 3d render, night"
        ),
    },
    (8, 5): {
        # r4 FALSIFIED TOO, and r4 said in advance what that would mean. A
        # negative naming `giant, colossal, monster, kaiju, statue, face in the
        # sky` left the colossus exactly where it was. So it is not the
        # `scenery` tag (r3) and it is not un-named-ness (r4); the words are
        # not what is putting it there. The foreground meanwhile is now RIGHT:
        # three full-length figures facing the lens, distinct costumes, one
        # holding a board, standing in a field with sky above -- beat 17's
        # composition, which beat 08 has never had.
        #
        # THE ONE VARIABLE, and it is the structural suspect r4 named: the
        # clause `wide blue sky above`. Every sample so far has reserved the
        # top half of a 832x1216 canvas for sky and then put the three people
        # in the bottom third, and every sample has filled the reserved half
        # with a subject. That is not a word problem, it is a composition
        # problem: an empty upper half in a portrait frame is a hole the model
        # will fill, and `wide shot` plus a large-noun goblin tells it what
        # with. Beat 17's plate gets away with the same clause because its one
        # figure is drawn LARGE and low, so the sky is negative space around a
        # subject rather than a vacancy. DELETING the clause is the smallest
        # change that tests it; the field, the figures and the whole negative
        # stay byte-identical to r4. If the colossus survives the deletion,
        # stop -- it is the `3boys`-plus-goblin nouns themselves and this beat
        # needs a different drafting approach, not a fifth adjective.
        "prompt": (
            "3boys, full body, wide shot, standing in a green field, "
            "two adult guard men in uniform facing a lean adult goblin man, "
            "green skin, bald head, patchwork cloak, near guard holds a "
            "wooden clipboard at chest height, three men standing together, "
            "sunny day, masterpiece, best quality"
        ),
        "negative": (
            "giant, colossal, monster, kaiju, statue, face in the sky, "
            "text, close-up, portrait, upper body, cropped, "
            "1boy, 2boys, 4boys, solo, white background, simple background, "
            "child, spear, sword, tree, forest, house, indoors, "
            "photorealism, 3d render, night"
        ),
    },
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
