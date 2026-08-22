#!/usr/bin/env python3
r"""THE SAPLING LoRA v2 DATASET: 60 frames, and two new caption VARIABLES.

WHY v2 EXISTS, AS A SCORE RATHER THAN AN OPINION. v1 trained on the 44 frames
in `manifest-sapling.yaml` and `registry.yaml` records what came back:
`bnysapling` DRAWS THE CANON TWO-LEAF SAPLING -- a first, after five closed
wording ladders -- and three of five pre-registered bars fail:

    B2_figure   0/3    no goblin, or one with the plant fused into its body
    B2_ground   4/6    brown autumn grassland 3/3, bare tilled earth 1/3
    B3          FAIL   at weight 0.8 a figure present without the LoRA is DELETED

All three trace to two facts about the set and to nothing else. This file fixes
those two facts and changes NO hyperparameter.

  ── ONE. THE FIGURE. 44 of 44 v1 frames are figure-free, deliberately: v1's
  naturalize header says "a subject LoRA fed a figure in every frame learns a
  figure", which is true and which overshot. The trigger learned NO FIGURE as
  part of the subject. v2 adds SIXTEEN frames that carry one -- eight harvested
  from ep2 plates this tree already owns and judged, eight newly built -- and,
  more importantly, NAMES THE FIGURE IN EVERY CAPTION IN BOTH DIRECTIONS. A
  frame with no figure now says `alone in the frame`; a frame with one says so.
  That is the mechanism v1 used to keep leaf count and story height out of the
  trigger, pointed at the axis that actually failed.

  ── TWO. THE GROUND, AND THE FINDING HERE IS NOT THE ONE THE SHIP PAGE
  PREDICTED. The v1 verdict says "44 of 44 stand on grass". MEASURED AT THE
  ROOT POINT ON THE PLATES THEMSELVES, THAT IS FALSE. Ten of the 44 do not:

      s14 s15 s16  (u08)  root on a bare DIRT PATH with pebbles, grass only at
                          the crop edge
      s19 s20 s21  (r08)  root on a sunlit/shaded PATH between green verges
      s12 s13      (u07)  root on FOREST FLOOR -- low leafy ground cover, not
                          blade grass
      s36 s37      (v05)  root on WET ROCK slabs in the rain

  The set already had four non-grass materials and NOT ONE CAPTION EVER SAID
  SO, because v1's caption scheme has no ground token at all. So the ground
  failure is substantially a CAPTION failure rather than a pixel failure: ground
  material was an unnamed constant, and an unnamed constant is precisely what a
  trigger absorbs. Ten frames therefore get a truthful non-grass ground word for
  ZERO render cost, and eight new frames add six materials the set has never
  had. Ten distinct materials over 60 frames, 18 of them non-grass.

WHAT IS NOT FIXED, AND IT IS THE SAME CAP v1 NAMED. `leaf_count_values: 1`.
Every frame is still TWO-leaf: `beat16_sapling_composite.py` draws the canon
two, `leaf_count_composite.py` can only REMOVE leaves, and inventing a third
would break canon `sapling-two-leaves` to satisfy a dataset axis. The count
token stays explicit in all 60 captions -- that is what keeps it out of the
trigger -- but its VALUE does not vary, and v1's probe measured the
consequence: asked for four leaves the trigger drew two. Canon rises 2 -> 6
leaves by 006a, so this remains the wall after ep3 and no caption here hides it.

A SECOND CAP, NEW AND NAMED. The eight new plates all use the depth skeletons,
which sit at cx 0.655. The FIGURE'S side of frame therefore does not vary in
the new half of the set; only its distance does. Side variety comes from where
the PLANT is rooted (four left, four right) and from the eight harvested frames,
whose plants sit at cx 121..577. If B2_figure improves but only for a figure
right of centre, this is the reason and the next batch is three mirrored
skeletons.

v1'S FILES ARE NOT TOUCHED. This writes `manifest-sapling-v2.yaml` and
`captions/sapling-v2-0822/`; `manifest-sapling.yaml` and
`captions/sapling-0821/` stay exactly as the v1 weights were trained on,
because `registry.yaml` points at them as that run's record.

$0. No model, no network, no GPU.

  python3 pipeline/lora/build_sapling_v2_0822.py           # dry
  python3 pipeline/lora/build_sapling_v2_0822.py --write
  python3 pipeline/lora/build_sapling_v2_0822.py --check   # re-verify shas
"""

from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "pipeline"))
import build_sapling_lora_composites_0821 as B     # noqa: E402
import build_saplora_figcomp_0822 as F             # noqa: E402
import derive_saplora_figplate_0822 as P           # noqa: E402
import build_sapling_0821 as V1                    # noqa: E402

TRIGGER = "bnysapling"
V1_FRAMES = "farm-out/ep3-saplora-frames-0821"
FIG_FRAMES = "farm-out/ep3-saplora-fignat-%s-0822"
CAPTIONS = "pipeline/lora/captions/sapling-v2-0822"
MANIFEST = "pipeline/lora/manifest-sapling-v2.yaml"

STYLE = "anime style, cel shading, detailed background"
ALONE = "alone in the frame"

# ── THE GROUND TOKEN, PER v1 PLATE, READ OFF THE PLATE AT THE ROOT POINT.
# NOT read off the scene string: the scene string is what was ASKED FOR and
# four of these plates did not deliver grass. Every value below was checked on
# a crop centred on that plate's own root coordinates.
GROUND_V1 = {
    "u01": "grass", "u02": "grass", "u03": "grass", "u04": "grass",
    "u06": "grass", "p09": "grass", "r05": "grass", "t04": "grass",
    "v02": "grass", "v03": "grass", "v12": "grass", "w02": "grass",
    "w03": "grass",
    # ---- THE FOUR THAT ARE NOT GRASS, and the whole reason this map exists.
    "u07": "forest floor",   # s12 s13 -- low leafy ground cover, no blades
    "u08": "a dirt path",    # s14 s15 s16 -- bare dirt and pebbles
    "r08": "a dirt path",    # s19 s20 s21 -- path between green verges
    "v05": "wet rock",       # s36 s37 -- wet dark rock slabs in the rain
}

# ── THE EIGHT HARVESTED ep2 FRAMES. Every one already exists, is judged, is
# published under its producing job's own `.sha256` manifest, and is an SDXL
# chain end to end (animagine-xl-3.1 plate -> numpy composite -> one 0.30
# animagine inpaint). They cost NOTHING to add and they are the only frames in
# the tree that show this plant and this character in one picture.
#
# id, path, sha256, tier, ground, figure clause, setting, plant cx (measured)
#
# THE TIER IS MEASURED, NOT EYEBALLED. Four of the eight carry a geometry json
# with `height_px`; for the other four the stem is derived from the mask bbox
# in the frame's own meta.yaml, where mask_h / stem measured 1.12-1.16 across
# the four known cases, so stem ~ mask_h / 1.14. Tier boundaries are v1's own
# (s 150-200, m 230-320, l 420-580, xl 620+).
#
# THE FIGURE CLAUSE IS READ OFF THE PICTURE and says where he is relative to
# the plant, because "a figure is present" is the variable and "where" is the
# part that has to generalise.
#
# SIX OF THE EIGHT SHAS ARE VERIFIED AGAINST THE PRODUCING JOB'S OWN `.sha256`
# MANIFEST, which is the authority -- not against a locally recomputed hash,
# because macOS is case-insensitive and a contact sheet written over an
# extracted frame is exactly how a src-sha mismatch was manufactured on
# 2026-08-22. THE OTHER TWO -- h03 (b03-sapcomp) and h04 (b13-sapcomp), both
# from 0820 -- have NO `.sha256` in their published directory: those jobs
# predate the courier writing one. Their hashes below are therefore computed
# from the bytes on disk and pin nothing stronger than "these bytes, from
# here, today". That is weaker and it is said rather than blurred; if either
# frame ever needs a stronger claim, the producing job's record is where it
# would have to come from and it does not exist.
HARVEST = [
    ("h01", "farm-out/ep2-b02-sapnat-0821/b02-sapnat-s20260820.png",
     "30dce0fabd444fdf5e0727eb4c6a317d65004f71a7df0dbe5cb126224dbf46ea",
     "l", "grass", "with a small green goblin striding past behind it",
     "tall grass, pale hazy daylight", 237, 560),
    ("h02", "farm-out/ep2-b03-sapnat-0821/b03-sapnat-s20260820.png",
     "e59f177e01891bd32962dfd861478ab3ece74af248038a0e4fd8df34d6f4637f",
     "l", "grass", "with a small green goblin sitting behind it",
     "tall grass, soft even daylight", 464, 540),
    ("h03", "farm-out/ep2-b03-sapcomp-0820/b03-sapcomp-s20260820.png",
     "7d3ab86a3f419f0d39c3c8960483008e61da99592dc77b4ff5cbb46cd2471671",
     "l", "grass", "with a small green goblin crouching behind it",
     "open grass field, distant hills, bright hazy daylight", 264, 561),
    ("h04", "farm-out/ep2-b13-sapcomp-0820/b13-sapcomp-s20260820.png",
     "bb0ad70c4294aa1647a0db1567df30482c97780359adc799818ff1dd88e0f7b2",
     "l", "grass", "with a small green goblin sitting close beside it",
     "tall grass, warm side light", 132, 462),
    ("h05", "farm-out/ep2-b13-tallcomp-0820/b13-tallcomp-s20260820.png",
     "80590db7ffda11b79cc6ea5198e18572adb23d283d515c8844c59fe51fbc1ac3",
     "xl", "grass", "with a small green goblin sitting close beside it",
     "tall grass, warm side light", 139, 866),
    ("h06", "farm-out/ep2-b15-sapcomp-0819/b15-sapcomp-s20260819.png",
     "df399888424071e5b9281748937a1e422eff6756dbe62c452b28d7b5456d30b8",
     "m", "grass", "with a small green goblin sitting on a rock beside it",
     "bright green meadow, hard daylight", 215, 280),
    ("h07", "farm-out/ep2-b16-sapnat4-0821/b16-sapnat4-s20260820.png",
     "8b5a432428c99c79a7349f8001b55c2ed268747d989fbf871a413dda8c2869c0",
     "l", "dry grass", "with a small green goblin sitting apart from it",
     "dry pale grass, low warm light", 160, 560),
    ("h08", "farm-out/ep2-b20-sapnat-0821/b20-sapnat-s20260820.png",
     "f8ffa9f24bfa3a9f8077dcc043326eee20dcb4752593227d1346a86f2f49be36",
     "xl", "grass", "with a small green goblin sitting beside it",
     "tall grass, bright daylight", 577, 760),
]

# ONE CANDIDATE WAS REJECTED AND IT IS RECORDED RATHER THAN QUIETLY OMITTED.
HARVEST_REJECT = {
    "ep2-b19-sapcomp-0819": (
        "THE PLANT CARRIES A FIG. Beat 19 is `the drop` and its composite has "
        "the fruit on the stem, which is the beat working correctly and a "
        "dataset frame failing: `bud, flower, fruit` are in this dataset's own "
        "negative on every one of the 60 other frames, and a fruiting frame "
        "would teach the trigger the thing the negative spends three tokens "
        "banning. Rejected on the pixels, not on the provenance."),
    "ep2-b12-sapnat2-0822": (
        "NO FIGURE IN FRAME (and 704x1280, which would add a second bucket to "
        "a set that resolves to one). It is a fine plant on a cloud sky and it "
        "is the forty-fifth frame of what the set already has enough of."),
    "ep2-b21-sapnat2-0822": ("NO FIGURE IN FRAME, and 704x1280. Same reading "
                             "as b12."),
}

# tier -> (growth-ladder height token, framing token). v1's table, unchanged.
# The cm figure is a row of the ladder in genomes/sapling/style.md that a
# TWO-COTYLEDON drawing can honestly occupy; the ladder's 90 cm row has five or
# six leaves and a crown, so no frame here is captioned 90 cm.
TIER_CAPTION = V1.TIER_CAPTION


def caption(tier, figure, ground, setting):
    """The v2 caption. TWO CLAUSES LONGER THAN v1's, and they are the two axes
    that failed. Order is deliberate: trigger, subject, the two v1 variables
    (count, height), framing, THE FIGURE, THE GROUND, the setting, the style.
    The figure and the ground sit before the setting because they are
    properties of the SUBJECT'S SITUATION, and after the framing because they
    are not camera facts."""
    h, framing = TIER_CAPTION[tier]
    return ("%s, a young sapling, two leaves, %s, %s, %s, rooted in %s, %s, %s"
            % (TRIGGER, h, framing, figure, ground, setting, STYLE))


def sha_of(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def collect():
    """Every v2 frame, in one list, with its caption already built."""
    frames, missing = [], []

    # ---- 1. THE 44 v1 FRAMES, re-captioned and NOT re-rendered. Same pixels,
    # same shas, two new clauses in the caption. `alone in the frame` is the
    # half of the figure variable that v1 could not have, because with no
    # frame carrying a figure the word would have been a constant too.
    for fid, pk, tier, root, height, tilt, lf, ls in B.ROWS:
        img = os.path.join(REPO, V1_FRAMES, "sap-%s-%s-0821.png" % (fid, pk))
        if not os.path.isfile(img):
            missing.append("v1 %s (%s)" % (fid, pk))
            continue
        frames.append(dict(
            fid=fid, source="v1", plate=pk, tier=tier,
            image=os.path.relpath(img, REPO), sha256=sha_of(img),
            ground=GROUND_V1[pk], figure=ALONE, figure_present=False,
            caption=caption(tier, ALONE, GROUND_V1[pk], V1.SETTING[pk]),
            geometry="root %s, stem %d px, tilt %.1f deg, leaf-frac %.2f, "
                     "leaf-spread %.1f deg" % (list(root), height, tilt, lf, ls),
            render="animagine-xl-3.1, SDXL inpaint, 40 steps, cfg 7.5, "
                   "strength 0.30, seed 20260820, $0 on rtx5090",
            spec="pipeline/jobs/ep3-saplora-%s-0821.yaml" % fid))

    # ---- 2. THE EIGHT HARVESTED ep2 FRAMES.
    for hid, path, sha, tier, ground, figure, setting, cx, stem in HARVEST:
        p = os.path.join(REPO, path)
        if not os.path.isfile(p):
            missing.append("harvest %s (%s)" % (hid, path))
            continue
        got = sha_of(p)
        if sha and got != sha:
            missing.append("harvest %s SHA %s != %s" % (hid, got, sha))
            continue
        frames.append(dict(
            fid=hid, source="harvest-ep2", plate=os.path.basename(
                os.path.dirname(path)), tier=tier,
            image=path, sha256=got, ground=ground, figure=figure,
            figure_present=True,
            caption=caption(tier, figure, ground, setting),
            geometry="plant cx %d px, stem ~%d px (measured; see the HARVEST "
                     "table's note on how)" % (cx, stem),
            render="animagine-xl-3.1, SDXL inpaint, 40 steps, cfg 7.5, "
                   "strength 0.30, $0 on rtx5090 -- harvested from the ep2 "
                   "beat lane, not rendered for this dataset",
            spec="farm-out/%s/ -- the producing job's own .sha256 manifest is "
                 "the authority" % os.path.basename(os.path.dirname(path))))

    # ---- 3. THE EIGHT NEW FIGURE+GROUND CELLS.
    for cell, tier, root, height, tilt, lf, ls, side in F.ROWS:
        pose, pose_words, emotion, ground, _ = P.CELLS[cell]
        d = FIG_FRAMES % cell
        img = os.path.join(REPO, d, "fignat-%s-s20260820.png" % cell)
        if not os.path.isfile(img):
            missing.append("fig %s (%s)" % (cell, d))
            continue
        figure = "with a small green goblin sitting %s of it" % (
            "to the left" if side.startswith("right") else "to the right")
        frames.append(dict(
            fid="f-%s" % cell, source="figcell", plate=cell, tier=tier,
            image=os.path.relpath(img, REPO), sha256=sha_of(img),
            ground=ground, figure=figure, figure_present=True,
            caption=caption(tier, figure, ground,
                            "%s, the figure set back" % ground),
            geometry="root %s, stem %d px, tilt %.1f deg, leaf-frac %.2f, "
                     "leaf-spread %.1f deg, plant %s of the figure, plate "
                     "skeleton %s" % (list(root), height, tilt, lf, ls, side,
                                      pose),
            render="animagine-xl-3.1 ControlNet+IP-Adapter plate, numpy "
                   "composite, SDXL inpaint 40 steps, cfg 7.5, strength 0.30, "
                   "seed 20260820, $0 on rtx5090",
            spec="pipeline/jobs/ep3-saplora-fignat-%s-0822.yaml" % cell))

    return frames, missing


def main() -> int:
    write = "--write" in sys.argv
    check = "--check" in sys.argv
    frames, missing = collect()

    if missing:
        print("!! %d frame(s) not usable:" % len(missing))
        for m in missing:
            print("     %s" % m)
        if not any(m.startswith("fig ") for m in missing):
            return 1
        print("   (the `fig` rows are the naturalize batch -- run it first)")
        return 1

    tiers, grounds, srcs = {}, {}, {}
    figs = 0
    for f in frames:
        tiers[f["tier"]] = tiers.get(f["tier"], 0) + 1
        grounds[f["ground"]] = grounds.get(f["ground"], 0) + 1
        srcs[f["source"]] = srcs.get(f["source"], 0) + 1
        figs += 1 if f["figure_present"] else 0

    print("%d frames | sources %s" % (len(frames), srcs))
    print("  tiers            %s" % tiers)
    print("  figure in frame  %d of %d (v1: 0 of 44)" % (figs, len(frames)))
    print("  ground materials %d distinct, %d non-grass frames"
          % (len(grounds), sum(v for k, v in grounds.items()
                               if "grass" not in k)))
    for k in sorted(grounds, key=lambda k: -grounds[k]):
        print("     %-16s %d" % (k, grounds[k]))

    if check:
        bad = [f["fid"] for f in frames
               if sha_of(os.path.join(REPO, f["image"])) != f["sha256"]]
        print("sha re-check: %s" % ("FAIL %s" % bad if bad else "all match"))
        return 1 if bad else 0
    if not write:
        for f in (frames[0], frames[44], frames[-1]):
            print("\n  %-6s %s" % (f["fid"], f["caption"]))
        print("\n-- dry run. re-run with --write.")
        return 0

    cdir = os.path.join(REPO, CAPTIONS)
    os.makedirs(cdir, exist_ok=True)
    for f in frames:
        f["caption_file"] = "%s/%s.txt" % (CAPTIONS, f["fid"])
        with open(os.path.join(REPO, f["caption_file"]), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(f["caption"] + "\n")

    lines = [
        "# THE SAPLING LoRA v2 DATASET. GENERATED -- edit",
        "# pipeline/lora/build_sapling_v2_0822.py, not this file.",
        "#",
        "# v1 (manifest-sapling.yaml, 44 frames) IS NOT TOUCHED. It is the",
        "# record of what the v1 weights in registry.yaml were trained on.",
        "#",
        "# WHAT v2 CHANGES, AND IT IS THE DATASET AND NOTHING ELSE. No",
        "# hyperparameter moves. v1's three failing bars (B2_figure 0/3,",
        "# B2_ground 4/6, B3 no-regression) all trace to two facts about the",
        "# set, and this manifest fixes exactly those two:",
        "#",
        "#   THE FIGURE. v1 was figure-free 44 times out of 44 -- on purpose,",
        "#   and it overshot: the trigger learned NO FIGURE as part of the",
        "#   subject and at weight 0.8 DELETES a figure the base checkpoint",
        "#   draws without it. v2 carries 16 frames with a figure and, more to",
        "#   the point, NAMES FIGURE-PRESENCE IN EVERY CAPTION IN BOTH",
        "#   DIRECTIONS -- `alone in the frame` or `with a small green goblin",
        "#   <where>`. A named attribute is one the trigger is excused from",
        "#   carrying; that is the mechanism v1 used for leaf count and height.",
        "#",
        "#   THE GROUND -- AND THE v1 VERDICT WAS WRONG ABOUT THIS. The ship",
        "#   page says 44 of 44 stand on grass. Measured at the root point on",
        "#   the plates themselves, TEN DO NOT: s14/s15/s16 (u08) and",
        "#   s19/s20/s21 (r08) root on a bare dirt path, s12/s13 (u07) on",
        "#   forest floor, s36/s37 (v05) on wet rock. The set already had four",
        "#   non-grass materials and no caption ever said so, because v1's",
        "#   scheme has NO GROUND TOKEN AT ALL. So the ground failure is",
        "#   substantially a CAPTION failure: material was an unnamed constant,",
        "#   which is what a trigger absorbs. Those ten are re-captioned",
        "#   truthfully at zero render cost and eight new frames add six",
        "#   materials the set has never had.",
        "#",
        "# THE CAP THAT DID NOT MOVE. leaf_count_values is still 1 -- every",
        "# frame is TWO-leaf, because beat16_sapling_composite draws the canon",
        "# two and leaf_count_composite can only REMOVE leaves. The token is",
        "# explicit in all 60 captions so it cannot fuse into the trigger, but",
        "# v1's probe measured what a constant value costs: asked for four",
        "# leaves the trigger drew two. Canon rises 2 -> 6 by 006a, so this is",
        "# still the wall after ep3.",
        "#",
        "# A SECOND CAP, NEW. The eight new plates all use the depth skeletons,",
        "# which sit at cx 0.655, so the FIGURE'S side of frame does not vary",
        "# in the new half -- only its distance does. The plant's side varies",
        "# (four left, four right) and the harvested frames spread cx 121..577.",
        "# If B2_figure improves only for a figure right of centre, that is the",
        "# reason and the next batch is three mirrored skeletons.",
        "#",
        "# ITEM 18. Every frame is an SDXL chain: animagine-xl-3.1 plate -> a",
        "# numpy composite -> one 0.30 animagine inpaint. ZERO LTX pixels, and",
        "# the training job's stage step refuses any frame whose `render:` line",
        "# does not assert animagine. DECISIONS.md item 18 is OPEN and is the",
        "# founder's; this records scope and does not close it.",
        "",
        "subject: sapling",
        "trigger: %s" % TRIGGER,
        "version: 2",
        "built_by: pipeline/lora/build_sapling_v2_0822.py",
        "built_on: '2026-08-22'",
        "supersedes: pipeline/lora/manifest-sapling.yaml   # 44 frames, v1",
        "authority: >-",
        "  canon `sapling-two-leaves` (founder, 2026-08-16) and",
        "  `sapling-cotyledon-shape` (founder, 2026-08-17); the growth ladder in",
        "  genomes/sapling/style.md:150-158; the dataset gate in",
        "  pipeline/lora/README.md; the v1 score in pipeline/lora/registry.yaml",
        "count: %d" % len(frames),
        "figure_frames: %d   # v1 had 0 of 44" % figs,
        "figure_free_frames: %d" % (len(frames) - figs),
        "ground_materials: %d distinct" % len(grounds),
        "non_grass_frames: %d   # v1 had 0 NAMED, and 10 unnamed"
        % sum(v for k, v in grounds.items() if "grass" not in k),
        "scale_tiers: %s" % ", ".join("%s=%d" % kv for kv in sorted(tiers.items())),
        "leaf_count_values: 1   # two, in every frame. See the note above.",
        "cost_usd: 0.0",
        "harvest_rejected:",
    ]
    for k in sorted(HARVEST_REJECT):
        lines += ["  %s: >-" % k,
                  "    %s" % HARVEST_REJECT[k].replace("\n", " ")]
    lines += ["frames:"]
    for f in frames:
        lines += [
            "- id: %s" % f["fid"],
            "  source: %s" % f["source"],
            "  image: %s" % f["image"],
            "  sha256: %s" % f["sha256"],
            "  caption_file: %s" % f["caption_file"],
            "  caption: '%s'" % f["caption"],
            "  plate: %s" % f["plate"],
            "  scale_tier: %s" % f["tier"],
            "  ground: %s" % f["ground"],
            "  figure_present: %s" % ("true" if f["figure_present"] else "false"),
            "  geometry: %s" % f["geometry"],
            "  render: %s" % f["render"],
            "  spec: %s" % f["spec"],
        ]
    with open(os.path.join(REPO, MANIFEST), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\nwrote %s and %d captions" % (MANIFEST, len(frames)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
