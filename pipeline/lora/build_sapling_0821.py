#!/usr/bin/env python3
r"""THE SAPLING LoRA DATASET: captions + a sha-addressed manifest, generated.

WHAT IT CONSUMES. The naturalized frames in `farm-out/ep3-saplora-frames-0821/`
-- one 0.30 inpaint per composite, filed by
`pipeline/derive_sapling_lora_naturalize_0821.py`, each drawn by
`pipeline/beat16_sapling_composite.py` onto a goblin-free ground plane from
`review/ep3-sapling-dataset-0821/plates-0821.yaml`.

WHY THE CAPTIONS ARE SHAPED THE WAY THEY ARE, AND WHY IT IS THE OPPOSITE OF
JERRY'S. A LoRA learns the trigger token as whatever the caption leaves
unexplained, so Jerry's captions deliberately do NOT say `green skin` or `bald`
-- a named attribute is one the token is excused from carrying. The sapling
inverts that for exactly two attributes, and `pipeline/lora/README.md` says why:
the protagonist GROWS, 15 cm and two cotyledons in 001 to 1.6 m and a crown by
006a, so if LEAF COUNT and HEIGHT fuse into `bnysapling` then one LoRA cannot
serve seven episodes. Both are therefore NAMED IN EVERY CAPTION, so neither can
be absorbed. Everything else the token is meant to carry -- the ovate cotyledon
profile, the single bare stem, the no-midrib rule -- is left unnamed.

THE HEIGHT TOKEN IS THE STORY HEIGHT AND THE FRAMING TOKEN IS THE CAMERA, and
they are separate on purpose. A 15 cm sprout shot close and a 40 cm sapling shot
wide occupy the same pixels; collapsing them into one "size" token would teach
the LoRA that camera distance is growth. So each caption carries a growth-ladder
figure (`genomes/sapling/style.md`) AND a framing word, and the two vary
independently across the set.

WHAT THIS DATASET DOES NOT HAVE, STATED RATHER THAN HIDDEN. Every frame has TWO
leaves. `beat16_sapling_composite.py` draws the canon two;
`leaf_count_composite.py` only REMOVES leaves from a plate that has too many and
cannot add one; and inventing a third would break canon `sapling-two-leaves` to
satisfy a dataset axis. So the leaf-count TOKEN is present and explicit in all
frames -- which is the mechanism that keeps it out of the trigger -- but its
VALUE never changes in v1. A v2 that wants the 004-and-later crown needs a tool
that can draw three, five and six leaves, and that tool does not exist yet.

$0. No model, no network, no GPU.

  python3 pipeline/lora/build_sapling_0821.py            # dry
  python3 pipeline/lora/build_sapling_0821.py --write
  python3 pipeline/lora/build_sapling_0821.py --check    # re-verify shas
"""

from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "pipeline"))
import build_sapling_lora_composites_0821 as B  # noqa: E402

TRIGGER = "bnysapling"
FRAMES = "farm-out/ep3-saplora-frames-0821"
CAPTIONS = "pipeline/lora/captions/sapling-0821"
MANIFEST = "pipeline/lora/manifest-sapling.yaml"

# tier -> (growth-ladder height token, framing token). The cm figure is a row of
# the ladder in genomes/sapling/style.md that a TWO-COTYLEDON drawing can
# honestly occupy -- 001 (~15 cm) and 002 (~40 cm). The ladder's 90 cm row has
# five or six leaves and a crown, so no frame here is captioned 90 cm: a frame
# labelled 90 cm that shows a sprout would teach the LoRA that 90 cm looks like
# a sprout, which is the exact fusion the caption-variable rule exists to stop.
TIER_CAPTION = {
    "s":  ("15 cm tall", "wide shot"),
    "m":  ("25 cm tall", "wide shot"),
    "l":  ("40 cm tall", "medium shot"),
    "xl": ("40 cm tall", "close-up"),
}

# Per-plate caption SETTING clause. Shorter than the render prompt's scene words
# -- a caption names what varies, it is not a re-run of the prompt.
SETTING = {
    "u01": "open green meadow, distant hills, clear sky, flat daylight",
    "u02": "rolling grassland at sunset, golden slopes, warm backlight",
    "u03": "misty green hills at dawn, valley fog, cool pale light",
    "u04": "dark green hills, heavy overcast sky, muted grey light",
    "u06": "alpine valley, snow-capped mountains, bright midday",
    "u07": "inside a summer wood, tree trunks, dappled sunlight",
    "u08": "dirt path through a forest avenue, even daylight",
    "t04": "green field below distant misty mountains, pale dawn",
    "r05": "steep grassy hillside above a valley, hard midday sun",
    "r08": "sunlit clearing path between dark trees, strong backlight",
    "p09": "wildflower meadow, daisies in the grass, bright daylight",
    # ---- v2, 2026-08-21. THE LIGHTING CLAUSE IS THE POINT OF THESE FOUR.
    # Every setting above ends in a DAYLIT phrase, which is the cap v1's own
    # manifest names: a subject LoRA whose every frame shares a time of day
    # learns the time of day into `bnysapling`, exactly as a shared backdrop
    # would. These say night, storm, rain and after-rain, and they say it in
    # the caption -- where a named attribute is one the trigger is excused
    # from carrying -- rather than leaving it for the token to absorb.
    "v02": "green meadow at night, distant hills, moonlight, blue darkness",
    "v03": "green plain under storm cloud, a shaft of light, dark sky",
    "v05": "wet green moor in the rain, grey hills, flat rain light",
    "v12": "green plain after rain, puddles, breaking cloud",
}

STYLE = "anime style, cel shading, detailed background"

# Filled by the 1:1 contact-sheet read. A frame not listed here was never
# rendered; a frame listed with a reason under REJECT is on disk and excluded.
REJECT = {}


def caption_for(fid, pk, tier):
    h, framing = TIER_CAPTION[tier]
    return ("%s, a young sapling, two leaves, %s, %s, %s, %s"
            % (TRIGGER, h, framing, SETTING[pk], STYLE))


def sha_of(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main() -> int:
    write = "--write" in sys.argv
    check = "--check" in sys.argv
    frames, missing = [], []
    for fid, pk, tier, root, height, tilt, lf, ls in B.ROWS:
        img = os.path.join(REPO, FRAMES, "sap-%s-%s-0821.png" % (fid, pk))
        if not os.path.isfile(img):
            missing.append("%s (%s)" % (fid, pk))
            continue
        if fid in REJECT:
            continue
        frames.append(dict(
            fid=fid, plate=pk, tier=tier, image=os.path.relpath(img, REPO),
            sha256=sha_of(img), caption=caption_for(fid, pk, tier),
            root=list(root), stem_px=height, tilt=tilt, leaf_frac=lf,
            leaf_spread=ls,
            caption_file="%s/sap-%s-%s-0821.txt" % (CAPTIONS, fid, pk),
        ))
    if missing:
        print("!! not on disk: %s" % ", ".join(missing))
        return 1

    tiers = {}
    for f in frames:
        tiers[f["tier"]] = tiers.get(f["tier"], 0) + 1
    plates = sorted({f["plate"] for f in frames})
    print("%d frames | %d distinct plates/scenes/lightings | tiers %s"
          % (len(frames), len(plates), tiers))
    print("rejected: %s" % (", ".join("%s (%s)" % (k, v)
                                      for k, v in sorted(REJECT.items()))
                            or "none"))

    if check:
        bad = [f["fid"] for f in frames
               if sha_of(os.path.join(REPO, f["image"])) != f["sha256"]]
        print("sha re-check: %s" % ("FAIL %s" % bad if bad else "all match"))
        return 1 if bad else 0
    if not write:
        for f in frames[:3]:
            print("  %s  %s" % (f["fid"], f["caption"]))
        print("-- dry run. re-run with --write.")
        return 0

    cdir = os.path.join(REPO, CAPTIONS)
    os.makedirs(cdir, exist_ok=True)
    for f in frames:
        with open(os.path.join(REPO, f["caption_file"]), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(f["caption"] + "\n")

    lines = [
        "# THE SAPLING LoRA DATASET. GENERATED -- edit",
        "# pipeline/lora/build_sapling_0821.py, not this file.",
        "#",
        "# Every frame: a canon two-leaf sapling drawn by",
        "# pipeline/beat16_sapling_composite.py onto a goblin-free, plant-free",
        "# ground plane, then finished by ONE 0.30 SDXL inpaint on the box",
        "# (animagine-xl-3.1, 40 steps, cfg 7.5, pad-crop 64, blur 8, seed",
        "# 20260820). Per-frame job spec: pipeline/jobs/ep3-saplora-<fid>-0821.yaml.",
        "#",
        "# THE TWO NAMED TOKENS. `two leaves` and the cm figure appear in EVERY",
        "# caption on purpose -- the inverse of the Jerry rule. A LoRA learns the",
        "# trigger as whatever the caption leaves unexplained, and this character",
        "# GROWS (15 cm and two cotyledons in 001, 1.6 m and a crown by 006a), so",
        "# leaf count and height must never fuse into `bnysapling`. Height is the",
        "# STORY height and framing is the CAMERA, kept as separate tokens so the",
        "# set cannot teach that camera distance is growth.",
        "#",
        "# WHAT THIS SET DOES NOT HAVE. All frames are TWO-leaf.",
        "# beat16_sapling_composite draws the canon two; leaf_count_composite only",
        "# REMOVES leaves and cannot add one; inventing a third would break canon",
        "# `sapling-two-leaves` to satisfy a dataset axis. The leaf-count TOKEN is",
        "# therefore explicit in all frames -- which is the mechanism that keeps it",
        "# out of the trigger -- but its VALUE is constant in v1. A v2 covering the",
        "# 004-and-later crown needs a tool that can draw three, five and six",
        "# leaves. That tool does not exist and is not written here.",
        "#",
        "# NOT TRAINED. DECISIONS.md item 18 (\"never train on the output\") is open",
        "# and unresolved; this builds the dataset that question is ABOUT.",
        "",
        "subject: sapling",
        "trigger: %s" % TRIGGER,
        "built_by: pipeline/lora/build_sapling_0821.py",
        "built_on: '2026-08-21'",
        "authority: >-",
        "  canon `sapling-two-leaves` (founder, 2026-08-16) and",
        "  `sapling-cotyledon-shape` (founder, 2026-08-17); the growth ladder in",
        "  genomes/sapling/style.md:150-158; the dataset gate in",
        "  pipeline/lora/README.md",
        "plates_from: review/ep3-sapling-dataset-0821/plates-0821.yaml",
        "count: %d" % len(frames),
        "distinct_scenes: %d" % len(plates),
        "scale_tiers: %s" % ", ".join("%s=%d" % kv for kv in sorted(tiers.items())),
        "leaf_count_values: 1   # two, in every frame. See the note above.",
        "cost_usd: 0.0",
        "frames:",
    ]
    for f in frames:
        lines += [
            "- id: %s" % f["fid"],
            "  image: %s" % f["image"],
            "  sha256: %s" % f["sha256"],
            "  caption_file: %s" % f["caption_file"],
            "  caption: '%s'" % f["caption"],
            "  plate: %s" % f["plate"],
            "  scale_tier: %s" % f["tier"],
            "  geometry: root %s, stem %d px, tilt %.1f deg, leaf-frac %.2f, "
            "leaf-spread %.1f deg" % (f["root"], f["stem_px"], f["tilt"],
                                      f["leaf_frac"], f["leaf_spread"]),
            "  render: animagine-xl-3.1, SDXL inpaint, 40 steps, cfg 7.5, "
            "strength 0.30, seed 20260820, $0 on rtx5090",
            "  spec: pipeline/jobs/ep3-saplora-%s-0821.yaml" % f["fid"],
        ]
    with open(os.path.join(REPO, MANIFEST), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote %s and %d captions" % (MANIFEST, len(frames)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
