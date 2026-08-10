#!/usr/bin/env python3
r"""node 001 beat 06 — ROUND 8. His approved arm drawn wider, his other arm's leak shut.

2026-08-10, after r7. This file is a WRAPPER over `render_b06r7.py` and it owns
no render code of its own on purpose: r7's nine traps are what stopped three
rounds of silent defects, and a second copy of the sampler is a second thing to
keep in step. Everything here is done by naming a seed list and editing r7's own
`ARMS` dict before its `main()` runs.

WHAT r7 CAME BACK WITH (read off the frames, not off a metric):

    ARM B (no ground, SKY)      clean 4 of 4 — no ground, no horizon, no city,
                                no bird, no aircraft, no people
    ARM A (ground, TALL GRASS)  2 of 4 contaminated — flat ground and a city
                                skyline still arriving

Those are two different situations and this round treats them differently,
which is the whole design of the file.

ARM B IS PROVEN AND IS SCALED, NOT CHANGED. `--variant skyseeds` renders arm B
byte-for-byte as r7 sent it — same positive, same negative, same steps, cfg and
size — at seeds the beat has never drawn. Nothing about the recipe moves, so
this is depth on an approved result rather than a new one: the founder named
this composition himself, r7 delivered it clean, and what he does not yet have
is a SET to pick from. Seeds continue this beat's own arithmetic (20260725 +
k*1000) at k=8 and up, so no frame here can collide with r3/r4/r5/r6/r7's k=4..7
and any new frame still sets beside the old ones column for column.

ARM A IS A PROMPT PROBLEM AND GETS ONE SAMPLE PER FORMULATION. Reseeding arm A
would be drawing the same prompt again and hoping; the leak is in what the model
is being told. Two formulations, each a single 4-seed sample at r5's held seeds
so each is comparable to r7a column for column, and each ONE variable from the
last:

    a-neg    r7a plus `horizon, field` in the negative. Arm B already negates
             `horizon, field, ground` and arm B is the arm with no leak; arm A
             cannot negate `ground` (its ground is the point) but the other two
             cost it nothing. A flat plane meeting the sky IS a horizon, and
             `field` is the tag for the mown-lawn-to-the-distance composition
             that `grass` alone keeps importing.
    a-below  a-neg plus `from below` on the POSITIVE. One variable on top of
             a-neg. `from below` is a real Danbooru tag on this checkpoint's
             vocabulary meaning the camera looks up, and a camera looking up
             through tall grass cannot show a flat plane or a skyline — the
             blades are between the lens and the horizon. This is the founder's
             own reading of arm A ("show the ground as having tall grass")
             stated as a camera rather than as a noun.

BOTH ARM-A VARIANTS ARE UNPROVEN RECIPES AND EACH IS QUEUED EXACTLY ONCE. If one
comes back clean it may then be scaled; that is the founder's call and not this
file's.

THE TRAPS ALL STILL RUN. `require_neg` is extended with every term a variant
buys, so if the 77-token trim eats one the run stops instead of quietly testing
a prompt the model never saw (r7 trap 5). Trap 9's occupancy pre-flight, traps 7
and 8's `no humans` mechanism, trap 1's byte-for-byte fence and trap 2's r5
control are inherited untouched.

NOTHING HERE IS A PICK, A PROMOTION, A PUBLICATION OR A SPEND. The steward
chooses between arm A and arm B nowhere; the founder gave two acceptable
compositions and has chosen neither.

Usage:
    python render_b06r8.py --variant skyseeds --seeds 20268725,20269725 \
        --set r8b-k8 --root <repo> --out <dir>
    python render_b06r8.py --variant a-neg --root <repo> --measure
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# The r7 module is the renderer. Its directory is where the box keeps it.
DEFAULT_R7_DIR = r"C:\banyan-farm\b06-r7"

# r5's four, which r3, r4, r6 and r7 also drew. The arm-A variants hold these so
# a formulation change is the only difference from r7a.
HELD_SEEDS = [20264725, 20265725, 20266725, 20267725]

VARIANTS = {
    "skyseeds": {
        "arm": "B",
        "default_set": "r8b",
        "what": "arm B exactly as r7 sent it, at seeds this beat has not drawn",
    },
    "a-neg": {
        "arm": "A",
        "default_set": "r8a1",
        "extra_neg": "horizon, field",
        "require_neg": ("horizon", "field"),
        "what": "arm A plus `horizon, field` in the negative",
    },
    "a-below": {
        "arm": "A",
        "default_set": "r8a2",
        "extra_neg": "horizon, field",
        "require_neg": ("horizon", "field"),
        "pos_sub_new": "tall grass, grass, from below",
        "require_pos": ("from below",),
        "what": "a-neg plus `from below` on the positive",
    },
}


def parse_seeds(text: str) -> list:
    seeds = [int(p.strip()) for p in text.split(",") if p.strip()]
    if not seeds:
        raise SystemExit("!! --seeds parsed to nothing")
    if len(set(seeds)) != len(seeds):
        raise SystemExit("!! --seeds repeats a value; a repeat draws the same "
                         "frame twice under two names")
    return seeds


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--variant", required=True, choices=sorted(VARIANTS))
    ap.add_argument("--seeds", default=None,
                    help="comma-separated ints. skyseeds requires them; the "
                         "arm-A variants hold r5's four and refuse them")
    ap.add_argument("--set", dest="set_tag", default=None,
                    help="filename tag, default the variant's own (r8b/r8a1/r8a2)")
    ap.add_argument("--r7-dir", default=DEFAULT_R7_DIR,
                    help="directory holding render_b06r7.py")
    known, rest = ap.parse_known_args()
    v = VARIANTS[known.variant]

    r7_dir = Path(known.r7_dir)
    if not (r7_dir / "render_b06r7.py").is_file():
        print(f"!! no render_b06r7.py under {r7_dir} — this file renders "
              f"nothing on its own and will not improvise a sampler.",
              flush=True)
        return 20
    sys.path.insert(0, str(r7_dir))
    import render_b06r7 as r7                                        # noqa: E402

    if known.variant == "skyseeds":
        if not known.seeds:
            print("!! --variant skyseeds is the FRESH-SEED variant and exists "
                  "only to draw seeds this beat has not drawn. Name them.",
                  flush=True)
            return 21
        seeds = parse_seeds(known.seeds)
        clash = sorted(set(seeds) & set(HELD_SEEDS))
        if clash:
            print(f"!! seeds {clash} are the held four r7 already drew — this "
                  f"variant would overwrite a comparison, not add to it.",
                  flush=True)
            return 22
    else:
        if known.seeds:
            print("!! the arm-A variants hold r5's four seeds on purpose: the "
                  "formulation is the variable and a new seed would confound "
                  "it with the noise. Drop --seeds.", flush=True)
            return 23
        seeds = list(HELD_SEEDS)

    arm_key = v["arm"]
    arm = r7.ARMS[arm_key]
    r7.SEEDS = seeds
    arm["set"] = known.set_tag or v["default_set"]

    if v.get("extra_neg"):
        arm["extra_neg"] = arm["extra_neg"] + ", " + v["extra_neg"]
        arm["require_neg"] = tuple(arm["require_neg"]) + tuple(v["require_neg"])
    if v.get("pos_sub_new"):
        old, _ = arm["pos_sub"]
        arm["pos_sub"] = (old, v["pos_sub_new"])
        arm["require_pos"] = tuple(arm["require_pos"]) + tuple(v["require_pos"])
    arm["why"] = ("ROUND 8, variant `%s` — %s. %s\n\nINHERITED FROM ROUND 7: %s"
                  % (known.variant, v["what"],
                     "Arm B came back clean 4 of 4 in r7 and is scaled here "
                     "without one token changing, because what the founder "
                     "lacks on this composition is a set to choose from. "
                     if arm_key == "B" else
                     "Arm A came back 2 of 4 contaminated in r7 with flat "
                     "ground and a skyline, so the prompt moves and the seeds "
                     "do not: reseeding a leaking prompt is drawing it again "
                     "and hoping. One sample of this formulation, at r5's held "
                     "four, comparable to r7a column for column. ",
                     arm["why"]))

    sys.argv = [sys.argv[0]] + rest + ["--arm", arm_key]
    print(f"== round 8, variant {known.variant} (arm {arm_key}, set "
          f"{arm['set']}) — {v['what']}", flush=True)
    print(f"   seeds: {', '.join(str(s) for s in seeds)}", flush=True)
    return r7.main()


if __name__ == "__main__":
    sys.exit(main())
