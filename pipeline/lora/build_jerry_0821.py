#!/usr/bin/env python3
r"""THE JERRY DATASET AT THE k6a STANDARD -- manifest and captions, derived.

    python3 pipeline/lora/build_jerry_0821.py            # write
    python3 pipeline/lora/build_jerry_0821.py --check    # assert, write nothing

WHAT DISCHARGES WHICH GATE. `pipeline/lora/train-jerry-0820.yaml` has been HELD
since 2026-08-20 on two gates and neither was this lane's to hand-wave:

  GATE 1 -- DATASET RE-CURATED FOR TILE FIDELITY. Discharged by
    `curation-tile-0820.yaml`, which read all 31 frames of the old manifest at
    1:1 against the B tile and kept SEVEN, and then by eight new frames rendered
    at the standard the 2026-08-21 steward ruling names. That file's own gate
    said do NOT file on the seven alone: "seven frames in four poses trains a
    pose, not a character, and a pose-locked character LoRA is worse than no
    LoRA because it appears to work on the beat it was trained on."
    FIFTEEN FRAMES IN NINE POSES is the arithmetic that changes, and the eight
    new ones are the first frames in this tree that pass the whole tile bar.

  GATE 2 -- CAPTIONS RE-DERIVED FROM THE CORRECTED CANON. Discharged here, and
    ALL FIFTEEN are rewritten, not just the new ones. The old captions live in
    `captions/jerry/` and are written in the man-read vocabulary the founder
    retired on 08-20; keeping seven of them because their frames survived
    curation would teach the trigger token the retired words. New captions go to
    `captions/jerry-0821/` and the old directory is left untouched as evidence.

THE CAPTION RULE, AND IT IS THE ONE PLACE THIS FILE COULD QUIETLY RUIN THE RUN.
A character LoRA learns the trigger token as "whatever is in the image that the
caption does NOT explain". So the caption must name everything VARIABLE -- pose,
framing, setting -- and must NOT name the things that are the character, because
a named attribute is an attribute the token does not have to carry. `green skin`
and `bald` are therefore ABSENT from every caption below on purpose, and that
absence is the mechanism, not an oversight.

WHAT IS DELIBERATELY NOT DONE. No frame is edited, cropped or re-rendered. The
seven survivors are 832x1216 Mac plates and the eight new ones are 832x1216 box
renders; kohya's bucketing handles them and `--enable_bucket` is already in the
train spec. The Mac/box renderer difference (MAE 61 at identical seed, measured
08-16) is a difference in HOW THEY WERE DRAWN, not in what they show, and a
character LoRA trained on both is if anything better regularised.

$0. No model, no network, no GPU.
"""
from __future__ import annotations

import hashlib
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAPDIR = "pipeline/lora/captions/jerry-0821"
MANIFEST = "pipeline/lora/manifest-jerry-0821.yaml"
TRIGGER = "bnyjerry"

# ── THE SEVEN SURVIVORS of curation-tile-0820.yaml, by its own index. ────────
# Kept on T1 blank eyes / T2 no nose bridge / T3 no age modelling / T4 ears.
KEEPS = [
    (4,  "farm-out/ep2-b14-mac-plate-0816/14-the-defense-mac-plate-s1.png",
     "kneeling on grass, hands forward, full body, side light",
     "blank eyes, no nose, smooth mask; ears not drawn"),
    (5,  "farm-out/ep2-b14-mac-plate-0818/14-the-defense-mac-plate-r1s1.png",
     "kneeling on grass, hands forward, full body, side light",
     "blank eyes, no nose, smooth mask; ears not drawn"),
    (12, "farm-out/ep2-b15-mac-plate-0819/15-good-listener-mac-plate-r1s1.png",
     "sitting on grass, listening, full body, soft daylight",
     "the beat-15 match -- blank eyes, no nose, small low ear"),
    (13, "farm-out/ep2-b15-mac-plate-0819/15-good-listener-mac-plate-r2s1.png",
     "sitting on grass, listening, full body, soft daylight",
     "the beat-15 match, second seed"),
    (18, "farm-out/ep2-b19-mac-plate-0819/19-the-drop-mac-plate-r1s1.png",
     "sitting on grass, hands together in his lap, full body, open field",
     "the beat-19 family; ear is pointed but short"),
    (19, "farm-out/ep2-b19-mac-plate-0819/19-the-drop-mac-plate-r2s1.png",
     "sitting on grass, hands together in his lap, full body, open field",
     "the tile pose -- purple cowl, patchwork cloak, blank eyes"),
    (20, "farm-out/ep2-b19-mac-plate-0819/19-the-drop-mac-plate-r3s1.png",
     "sitting on grass, hands together in his lap, full body, open field",
     "THE TILE ITSELF -- the plate adult-b19-0819.jpg was made from"),
]

# ── THE EIGHT NEW FRAMES, at the k6a standard. ───────────────────────────────
# k6a itself is the STANDING pose: same skeleton, wording, mask, scale and seed
# as the seven set frames, already rendered, so it is not re-derived.
NEW = [
    ("ep2-jerry-face-k6a-0821", "ep2-jerry-face-k6a-0821-ipahead.png",
     "standing, arms at sides, in tall grass, full body",
     "THE STANDARD ITSELF -- the rung the 2026-08-21 ruling names"),
    ("ep2-jerry-set-stride-0821", "ep2-jerry-set-stride-0821-ipahead.png",
     "walking, arm outstretched, in tall grass, full body",
     "the striding pose; face and proportion hold"),
    ("ep2-jerry-set-reach-0821", "ep2-jerry-set-reach-0821-ipahead.png",
     "arms up, in tall grass, full body",
     "arms raised; the only frame in the set with both hands above the head"),
    ("ep2-jerry-set-point-0821", "ep2-jerry-set-point-0821-ipahead.png",
     "arm outstretched, pointing, in tall grass, full body",
     "pointing; cloak reads broad but proportion holds"),
    ("ep2-jerry-set-hunch-0821", "ep2-jerry-set-hunch-0821-ipahead.png",
     "standing, hunched over, arms at sides, in tall grass, full body",
     "hunched; distinct from `stand` rather than the duplicate that was feared"),
    ("ep2-jerry-set-kneel-0821", "ep2-jerry-set-kneel-0821-ipahead.png",
     "kneeling, in tall grass, full body, barefoot",
     "the strongest brow bar in the whole batch"),
    ("ep2-jerry-set-seat-0821", "ep2-jerry-set-seat-0821-ipahead.png",
     "sitting, hands clasped between knees, head lowered, in tall grass, "
     "full body",
     "the tile's own stance, drawn at the standard"),
    ("ep2-jerry-set-crouch-0821", "ep2-jerry-set-crouch-0821-ipahead.png",
     "squatting, in tall grass, full body",
     "squatting; carries the folded-pose collar tint -- see collar_note"),
]

# ── WHAT THE CAPTIONS SAY, AND WHY EACH HALF IS THERE. ───────────────────────
# STYLE tokens are named because they are shared by every frame and are NOT the
# character: without them the token absorbs "animagine cel-shaded key art" and
# bar B3 (no-regression on a non-cast prompt) fails by construction.
STYLE = "anime style, cel shading, detailed background"


def caption(pose_words):
    """`<trigger>, 1boy, solo, <pose/framing/setting>, <style>`.

    NAMED: pose, framing, setting, style -- everything that varies or that
    belongs to the checkpoint rather than to him.
    NOT NAMED, on purpose: green skin, bald, blank eyes, no nose, patchwork
    cloak, the ear, the brow, the proportion. Those are what the trigger token
    is being asked to mean, and a caption that names an attribute is a caption
    that excuses the token from carrying it.
    """
    return "%s, 1boy, solo, %s, %s" % (TRIGGER, pose_words, STYLE)


def rows():
    out = []
    for i, img, pose, why in KEEPS:
        stem = "%s__%s" % (os.path.basename(os.path.dirname(img)),
                           os.path.basename(img)[:-4])
        out.append((img, stem, pose, why, "curation-tile-0820 keep #%d" % i))
    for job, fn, pose, why in NEW:
        out.append(("farm-out/%s/%s" % (job, fn), "%s__%s" % (job, fn[:-4]),
                    pose, why, "k6a standard, 2026-08-21"))
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    check = "--check" in argv
    frames, missing = [], []
    for img, stem, pose, why, prov in rows():
        p = os.path.join(REPO, img)
        if not os.path.exists(p):
            missing.append(img)
            continue
        sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
        cap_rel = "%s/%s.txt" % (CAPDIR, stem)
        frames.append({"image": img, "sha256": sha, "caption_file": cap_rel,
                       "caption": caption(pose), "pose": pose,
                       "why_kept": why, "provenance": prov})
    if missing:
        print("!! %d frame(s) missing:\n  %s" % (len(missing),
                                                 "\n  ".join(missing)))
        return 1
    if check:
        bad = 0
        for f in frames:
            p = os.path.join(REPO, f["caption_file"])
            if not os.path.exists(p) or open(p, encoding="utf-8").read() \
                    != f["caption"] + "\n":
                print("!! caption drifted or missing: %s" % f["caption_file"])
                bad += 1
        print("%d frame(s), %d caption problem(s)" % (len(frames), bad))
        return 1 if bad else 0

    os.makedirs(os.path.join(REPO, CAPDIR), exist_ok=True)
    for f in frames:
        with open(os.path.join(REPO, f["caption_file"]), "w",
                  newline="\n", encoding="utf-8") as fh:
            fh.write(f["caption"] + "\n")

    poses = sorted({f["pose"].split(",")[0].strip() for f in frames})
    body = [
        "# THE JERRY LoRA DATASET, RE-CURATED AND RE-CAPTIONED AT THE k6a",
        "# STANDARD. GENERATED -- edit pipeline/lora/build_jerry_0821.py, not this.",
        "#",
        "# This file discharges both gates train-jerry-0820 has been held on since",
        "# 2026-08-20. It does NOT modify manifest-jerry.yaml, dataset-jerry.yaml or",
        "# captions/jerry/, which stay on disk as the evidence of what was rejected.",
        "#",
        "# WHERE THE FRAMES COME FROM:",
        "#   7  survivors of curation-tile-0820.yaml's 1:1 read of the old 31",
        "#   8  rendered at the k6a standard (pipeline/jerry_standard_0821.py)",
        "#  15  total, in %d distinct poses against the old set's FOUR." % len(poses),
        "#",
        "# WHY THE CAPTIONS DO NOT SAY `green skin` OR `bald`. A character LoRA",
        "# learns the trigger token as whatever the caption leaves unexplained. Every",
        "# caption names the POSE, the FRAMING, the SETTING and the STYLE -- the",
        "# things that vary, or that belong to the checkpoint -- and names none of",
        "# the tile attributes, because a named attribute is one the token is excused",
        "# from carrying. The style tokens ARE named for the opposite reason: bar B3",
        "# tests that the LoRA did not learn `our look`, and it would by construction",
        "# if `anime style, cel shading` were left for the token to absorb.",
        "",
        "subject: jerry",
        "trigger: %s" % TRIGGER,
        "built_by: pipeline/lora/build_jerry_0821.py",
        "built_on: '2026-08-21'",
        "authority: pipeline/canon.yaml ep2-goblin-design-adult; the k6a steward",
        "  ruling of 2026-08-21 recorded in pipeline/jerry_standard_0821.py",
        "curated_against: review/ep2-goblin-design-0819/adult-b19-0819.jpg",
        "supersedes: pipeline/lora/manifest-jerry.yaml  # 31 frames, man-read, untouched",
        "count: %d" % len(frames),
        "poses: %d" % len(poses),
        "collar_note: >-",
        "  TWO of the fifteen (set-crouch, and to a lesser degree set-seat) carry a",
        "  pink-lilac tint at the collar. It appeared on FOLDED poses only -- every",
        "  standing frame reads clean -- and a seed control (b03-r2, b20-r2) failed to",
        "  clear it, which points at the mask: it translates down with the head, but a",
        "  compressed figure puts neck and shoulder inside the same box, and",
        "  k6b/k6c/k6d already proved this adapter transfers the tile's purple cowl",
        "  when the mask gives it more to act on. THEY ARE KEPT, and this is a",
        "  judgement rather than an oversight: the tile's own cloak is patchwork with",
        "  pink and red patches, so pink cloth is tile-true where a purple COWL would",
        "  not be, and 2 of 15 cannot make the majority read of the token. If B1 comes",
        "  back with a collar on frames that did not ask for one, this note is the",
        "  first suspect and the fix is geometric, not another caption.",
        "frames:",
    ]
    for f in frames:
        body += [
            "- image: %s" % f["image"],
            "  sha256: %s" % f["sha256"],
            "  caption_file: %s" % f["caption_file"],
            "  caption: '%s'" % f["caption"],
            "  provenance: %s" % f["provenance"],
            "  why_kept: '%s'" % f["why_kept"].replace("'", "''"),
        ]
    with open(os.path.join(REPO, MANIFEST), "w", newline="\n",
              encoding="utf-8") as fh:
        fh.write("\n".join(body) + "\n")
    print("wrote %s -- %d frames, %d poses" % (MANIFEST, len(frames), len(poses)))
    print("wrote %d caption(s) -> %s/" % (len(frames), CAPDIR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
