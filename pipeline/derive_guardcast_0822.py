#!/usr/bin/env python3
r"""THE GUARD CASTING SHEET -- twelve candidates, one factorial, one batch.

    python3 pipeline/derive_guardcast_0822.py            # write the 12 specs
    python3 pipeline/derive_guardcast_0822.py --selftest  # assert, render nothing

$0 to author. Twelve 832x1216 stills on the box at ~24s each.

═══════════════════════════════════════════════════════════════════════════
WHY THIS EXISTS

The founder reviewed every guard reference we have and ruled, 2026-08-21:

    "not the best... some have girls, and theyre just improper."

and on 2026-08-20, on the guards card, he had already said what he wants:

    "they should look like grown men. yes. dumb grown men"

THE HONEST RECORD OF HOW WE GOT HERE. Five casting rounds were run on
2026-08-12 (charref-guards r1..r5, the b05/b06/b07 idfix pairs) and not one of
them produced that ruling, because not one of them asked the question. They
were WORDING repairs -- `bald` out, `short hair` in -- run against a cast that
had never been drawn to a brief. The goblin was not solved that way either: it
was solved when the founder picked a reference IMAGE out of our own old
generations and the k6a adapter pipeline was pointed at it. The guards have no
such image. This sheet exists to make one, and the founder chose that route
himself -- GENERATE a proper casting sheet (option 2 of two).

═══════════════════════════════════════════════════════════════════════════
THE RECIPE, AND WHAT IS AND IS NOT NEW IN IT

This is the ratified k6a-era still stack MINUS the goblin terms:

  SAME  the driver (controlnet_plate.py, sha ece54f68...), animagine-xl-3.1,
        832x1216, xinsir/controlnet-openpose-sdxl-1.0 at scale 1.0, the
        fetch-and-sha-assert stage step, the farm-out publish step, the
        quality prefix `masterpiece, best quality, very aesthetic`, and the
        negative discipline of front-loading defect terms inside CLIP-77.
  SAME  the SKELETON. `jerry-skel-h19-0820.png` at head_frac 0.190 -- which is
        5.2 HEADS, the measured ADULT ratio -- standing, arms at sides, full
        body. It is on disk, published, and sha-pinned in
        pipeline/jerry_standard_0821.py.
  GONE  the IP-Adapter. Every --ip-* flag is absent, deliberately, because
        THERE IS NO GUARD REFERENCE TO CONDITION ON. Producing one is the
        entire point of this sheet. Conditioning these frames on the goblin's
        face reference would draw twelve goblins in guard clothes.
  GONE  every goblin term: green skin, pointy ears, slit pupils, mandarin
        collar, the patchwork cloak. `goblin`, `green skin`, `pointy ears` and
        `elf` are in the NEGATIVE here -- these are human men.

═══════════════════════════════════════════════════════════════════════════
HOW THE 0812 FAILURE IS ANSWERED, ON BOTH AXES IT FAILED ON

"some have girls" is TWO defects and they need two different instruments.

  1. GENDER WAS NEVER ASSERTED, only negated by omission. The 0812 prompts said
     "two guard men" in prose and left the tag slot empty; the checkpoint's own
     prior filled it. Here it is asserted POSITIVELY in the checkpoint's native
     vocabulary and in the first six tokens: `1boy, solo, mature male`. The
     whole female family is ALSO in the negative (`1girl, girl, woman, female,
     breasts`), but the positive assertion is the load-bearing half -- a
     negative alone has to fight a prior it never displaced.
  2. PROPORTION WAS A WORD, AND WORDS DO NOT CARRY PROPORTION. `child, male
     child, shota, toddler, chibi, loli, teenager, young` are all in the
     negative, and words of that family were in 2026-08-12's negatives too --
     they did not work then either. What is new is that HEAD-TO-BODY IS CARRIED BY
     GEOMETRY: the openpose skeleton at 5.2 heads at scale 1.0. This is the
     same lesson jerry_standard_0821 records from the other direction -- n5
     moved head_frac alone from 0.190 to 0.320 and manufactured a bobblehead on
     demand. It is a dial, and here we hold it at the adult end.

"dumb" is carried where the law says emotion is carried: THE MOUTH AND THE
BROW. Not by an adjective. Two expression cells, both tag-native:
     SLACK   open mouth, half-closed eyes, thick eyebrows, expressionless
     DOPEY   grin, teeth, half-closed eyes, thick eyebrows

═══════════════════════════════════════════════════════════════════════════
THE WARDROBE IS NOT BEING RECAST HERE, AND THAT IS ON PURPOSE

The founder ratified the guards' garments on 2026-08-16 -- "the cast stands as
drawn" -- and beats 05, 06 and 08 all rendered and SHIPPED the same three
garments. b08 measured them at pixel level (ep2-b08-gripmark-0820: the cream
shirt reads R-B 34.7 against skin's 42.6-49.7). One wardrobe across all twelve
cells:

    cream shirt, white sash, brown wrap skirt

It is held CONSTANT so that the three axes the founder is actually being asked
about -- hair, build, face -- are the only things moving. A sheet that varies
the clothes too is a sheet where he cannot say why he likes one.

WHAT THE SHEET DOES NOT SETTLE, said out loud: the wrap-skirt-vs-tunic split
between guard A and guard B on the 0816 sheet is NOT re-opened here, and a pick
off this sheet is a FACE and a BUILD, not a new costume ruling.

═══════════════════════════════════════════════════════════════════════════
THE ONE-SAMPLE RULE, AND WHY A BATCH IS THE RIGHT SHAPE HERE

CLAUDE.md: "before rendering a SET of anything, produce ONE and have the
founder look at it... one per recipe change."

The recipe change under test is NOT new. Driver, checkpoint, controlnet,
resolution, skeleton, quality prefix and negative discipline are all the
ratified stack, sampled and judged across the thirteen-rung k-ladder. What
varies here is the WORDING of a character brief -- and the founder has already
looked at the previous wording's output and rejected it, which is the sample.

And a casting sheet is by construction a SET: one candidate cannot answer
"which of these". Rendering one, showing it, and then rendering eleven more
would cost him two review passes to answer one question, on the night he asked
to review. THE BATCH IS THE SAMPLE. Twelve cells, 12 x ~24s of GPU.

WHAT IS PRE-REGISTERED AS THE WAY THIS BATCH FAILS, named before the pixels
exist so the judgement is not written after the fact:
  * A child or female read survives the positive assertion + the skeleton.
    THE LEVER: raise controlnet --scale, or negate `1girl` harder by moving
    `mature male, facial hair` earlier. Any frame that reads girl or child is
    DROPPED at 1:1 and is not shown to him -- the founder's own words are the
    bar and there is no point spending his eye on a re-run of the defect.
  * "Dumb" reads as UGLY or as DERANGED rather than as slow. THE LEVER: drop
    `expressionless`, keep `half-closed eyes`, add `:o`.
  * All twelve read as the same man. THE LEVER: the seeds are already distinct;
    next is widening the build axis with `fat man` / `tall`.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import clip_token_count as clip                 # noqa: E402
import derive_fetch_guard as fetchguard         # noqa: E402
import derive_spec                              # noqa: E402
import jerry_standard_0821 as std               # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── the assets, borrowed whole and sha-pinned. Nothing new is published. ─────
ASSET_DIR = std.ASSET_DIR                       # farm-out/jerry-skel-assets-0820
ASSET_URL = std.ASSET_URL
DRIVER = std.DRIVER
DRIVER_SHA = std.DRIVER_SHA
SKEL = "jerry-skel-h19-0820"                    # stand, head_frac 0.190 = 5.2 heads
SKEL_SHA = std.SKELETONS[SKEL][1]
CONTROLNET = std.CONTROLNET
CONTROL_SCALE = "1.0"
ARM = "cast"

# ── the wording. Held identical except on the three axes. ────────────────────
PREFIX = "masterpiece, best quality, very aesthetic, 1boy, solo, mature male"
WARDROBE = "cream shirt, white sash, brown wrap skirt, muted color"
POSE = "standing, arms at sides, in tall grass, full body"

# `boy` IS DELIBERATELY NOT IN HERE. The positive asserts `1boy` -- the
# checkpoint's tag for a male of ANY age -- and negating the bare string `boy`
# would fight the one term this whole sheet leans on. The young-male family is
# negated by its OWN tags instead: `male child`, `shota`, `toddler`.
NEGATIVE = ("lowres, worst quality, low quality, text, watermark, "
            "1girl, girl, woman, female, breasts, "
            "child, male child, shota, toddler, chibi, loli, teenager, young, "
            "armor, helmet, knight, goblin, green skin, pointy ears, elf, "
            "cloak, hood, photorealistic, 3d")

HAIR = {
    "bald":  "bald",
    "dark":  "short hair, black hair",
    "sandy": "short hair, light brown hair",
}
BUILD = {
    "burly": "muscular male, broad shoulders",
    "lean":  "tall, lanky, thin",
}
FACE = {
    "slack": "open mouth, half-closed eyes, thick eyebrows, expressionless",
    "dopey": "grin, teeth, half-closed eyes, thick eyebrows",
}

# ── the twelve cells. 3 hair x 2 build x 2 face, grouped so the sheet reads. ──
# 4 bald and 8 with hair, of which 4 are the sandy the guard-hair canon names
# (canon.yaml `ep2-guard-hair`: guard A dark cropped, guard B light sandy).
CELLS = [
    ("A", "bald",  "burly", "slack"),
    ("B", "bald",  "burly", "dopey"),
    ("C", "bald",  "lean",  "slack"),
    ("D", "bald",  "lean",  "dopey"),
    ("E", "dark",  "burly", "slack"),
    ("F", "dark",  "burly", "dopey"),
    ("G", "dark",  "lean",  "slack"),
    ("H", "dark",  "lean",  "dopey"),
    ("I", "sandy", "burly", "slack"),
    ("J", "sandy", "burly", "dopey"),
    ("K", "sandy", "lean",  "slack"),
    ("L", "sandy", "lean",  "dopey"),
]
SEED0 = 20260901                                # one distinct seed per cell

HAIR_HUMAN = {"bald": "bald", "dark": "dark cropped hair",
              "sandy": "light sandy hair"}
BUILD_HUMAN = {"burly": "burly", "lean": "tall and lanky"}
FACE_HUMAN = {"slack": "slack-jawed, vacant", "dopey": "dopey grin"}


def spec_id(letter):
    return "ep2-guardcast-%s-0822" % letter.lower()


def prompt_for(hair, build, face):
    return ", ".join([PREFIX, BUILD[build], HAIR[hair], FACE[face],
                      WARDROBE, POSE])


def one_line(letter, hair, build, face):
    """The single line the picker page shows under each image."""
    return "%s / %s / %s" % (HAIR_HUMAN[hair], BUILD_HUMAN[build],
                             FACE_HUMAN[face])


def _stage_step(jid):
    return (
        '# EVERY INPUT THIS FRAME IS CONDITIONED ON IS FETCHED AND SHA-CHECKED\n'
        '# BEFORE A GPU SECOND IS SPENT. Two inputs, not three: there is NO\n'
        '# IP-Adapter reference here because there is no guard reference yet --\n'
        '# making one is what this sheet is for. Emitted by\n'
        '# pipeline/derive_guardcast_0822.py.\n'
        'import hashlib, os, urllib.request\n'
        'base = "%s"\n'
        'root = r"C:\\banyan-farm\\%s\\src"\n'
        'want = [("%s", os.path.join(root, "pipeline"),\n'
        '         "%s"),\n'
        '        ("%s.png", os.path.join(root, "pipeline", "control"),\n'
        '         "%s")]\n'
        'for name, dst, sha in want:\n'
        '    os.makedirs(dst, exist_ok=True)\n'
        '    with urllib.request.urlopen(base + name, timeout=120) as r:\n'
        '        blob = r.read()\n'
        '    got = hashlib.sha256(blob).hexdigest()\n'
        '    if got != sha:\n'
        '        print("!! %%s fetched with sha %%s, expected %%s"\n'
        '              %% (name, got, sha))\n'
        '        raise SystemExit(1)\n'
        '    with open(os.path.join(dst, name), "wb") as fh:\n'
        '        fh.write(blob)\n'
        '    print("staged", name, got, "->", dst)\n'
        % (ASSET_URL, jid, DRIVER, DRIVER_SHA, SKEL, SKEL_SHA))


def _publish_step(jid):
    return (
        '# The courier pushes from farm-out and from nowhere else --\n'
        '# ep2-cnet-probe-0817 rendered perfectly and was invisible for two\n'
        '# days for want of this step. The conditions travel with the frame.\n'
        'import glob, hashlib, os, shutil\n'
        'out_dir = "C:/banyan-farm/%(d)s/out"\n'
        'pay_dir = "C:/banyan-farm/%(d)s"\n'
        'ctl_dir = "C:/banyan-farm/%(d)s/src/pipeline/control"\n'
        'dst = "C:/banyan-farm/courier-box/farm-out/%(d)s"\n'
        'os.makedirs(dst, exist_ok=True)\n'
        'files = sorted(glob.glob(out_dir + "/%(d)s-%(a)s.png*")\n'
        '               + glob.glob(pay_dir + "/prompt.txt")\n'
        '               + glob.glob(pay_dir + "/negative.txt")\n'
        '               + glob.glob(ctl_dir + "/%(h)s.png"))\n'
        'lines = []\n'
        'for f in files:\n'
        '    shutil.copy2(f, dst)\n'
        '    c = os.path.join(dst, os.path.basename(f))\n'
        '    with open(c, "rb") as fh:\n'
        '        h = hashlib.sha256(fh.read()).hexdigest()\n'
        '    lines.append(h + "  " + os.path.basename(f))\n'
        'with open(os.path.join(dst, "%(d)s.sha256"), "w", newline="\\n") as fh:\n'
        '    fh.write("\\n".join(sorted(lines)) + "\\n")\n'
        'print("published", len(files), "file(s) + manifest ->", dst)\n'
        'raise SystemExit(0 if len(files) >= 4 else 1)\n'
        % {"d": jid, "a": ARM, "h": SKEL})


BAR = """THE CASTING BAR. Scored at 1:1, per frame, before the founder sees it.

REJECT OUTRIGHT -- these frames are not shown to him at all, because his own
words already ruled on them and spending his eye on a repeat of the defect is
the thing this sheet exists to stop:
  R1  A FEMALE READ. Any of it -- breasts, a female face, a female silhouette.
      "some have girls, and theyre just improper" (founder, 2026-08-21).
  R2  A CHILD READ. Under about 5 heads, a child's face, a child's build.
      "they should look like grown men" (founder, 2026-08-20).
  R3  NOT ONE WHOLE MAN. Two figures, a cropped head, a floating head, a
      dismembered limb, or a body the skeleton clearly lost.

SCORE AND REPORT, but do not silently drop:
  S1  DUMB IS LEGIBLE IN THE FACE with the caption covered -- carried by the
      MOUTH and the BROW, per the law. Not "ugly", not "deranged": slow.
  S2  THE WARDROBE IS THREE GARMENTS -- cream shirt, white sash, brown wrap --
      not one merged robe. This is beat 08's measured failure mode.
  S3  NO ARMOUR, NO HELMET, NO KNIGHT. The founder's anti-helmet intent is
      what `bald` was mistranslated from on 2026-08-12; the intent stands.
  S4  HUMAN, NOT GOBLIN. No green skin, no pointy ears. Different cast.
  S5  THE THREE AXES ARE VISIBLY DIFFERENT ACROSS THE SHEET -- if all twelve
      read as one man the sheet has failed as a sheet even if every frame
      passes on its own.

The founder's job on this sheet is ONE taste call and nothing else: which face
is guard 1 and which is guard 2. Everything above is the steward's."""


def build_root():
    """Cell A, authored fresh. B..L are one derivation each off this."""
    letter, hair, build, face = CELLS[0]
    jid = spec_id(letter)
    return {
        "id": jid,
        "task": jid,
        "node": "002b-first-citizen",
        "beat": 5,
        "runner": "box",
        "priority": 3,
        "needs_gpu": True,
        "max_attempts": 1,
        "sample": False,
        "est_minutes": 2,
        "needs": ["cuda", "vram12", "sdxl-venv"],
        "owner": "guard-casting lane, 2026-08-22",
        "consumer": (
            "THE FOUNDER, tonight, on review/ep2-guardcast-0822 -- one picker "
            "page, twelve labelled candidates, one answer of the form "
            "`guardcast <letter>+<letter>`. His pick becomes the guards' "
            "reference image, which is what the goblin got on 2026-08-21 and "
            "what the guards have never had. NOTHING downstream consumes this "
            "frame until he picks: no beat plate, no motion spec, and "
            "review/ep2-ship-0821 is not touched."),
        "why": (
            "GUARD CASTING, CELL A OF TWELVE: bald / burly / slack-jawed. "
            "The founder reviewed every guard reference we have and ruled "
            "\"not the best... some have girls, and theyre just improper\", "
            "and had already said what he wants -- \"they should look like "
            "grown men. yes. dumb grown men\". Five 0812 rounds never asked "
            "him that question; they repaired wording against a cast nobody "
            "had drawn to a brief. He chose to GENERATE a sheet. This is the "
            "ratified still stack with the goblin adapter and every goblin "
            "term removed, the adult ratio carried by the 5.2-head openpose "
            "skeleton rather than by a word, and gender asserted positively "
            "in the first six tokens. See pipeline/derive_guardcast_0822.py."),
        "success": (
            "ONE 832x1216 png at seed %d, scored at 1:1 on the bar in `bar`. "
            "A pass here is a CANDIDATE on the picker page and nothing more -- "
            "the cast is the founder's call (R4) and this job does not make "
            "it." % SEED0),
        "env": {
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_OFFLINE": "1",
            "HF_HUB_DISABLE_XET": "1",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "payload": {
            "C:\\banyan-farm\\%s\\prompt.txt" % jid: prompt_for(hair, build, face),
            "C:\\banyan-farm\\%s\\negative.txt" % jid: NEGATIVE,
        },
        "steps": [
            {"name": "stage",
             "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c",
                      _stage_step(jid)]},
            {"name": "cast",
             "argv": [
                 r"C:\banyan-farm\venv\Scripts\python.exe",
                 "C:\\banyan-farm\\%s\\src\\pipeline\\controlnet_plate.py" % jid,
                 "--root", "C:\\banyan-farm\\%s\\src" % jid,
                 "--task", jid,
                 "--arm", ARM,
                 "--controlnet", CONTROLNET,
                 "--control", "pipeline/control/%s.png" % SKEL,
                 "--control-sha256", SKEL_SHA,
                 "--scale", CONTROL_SCALE,
                 "--seed", str(SEED0),
                 "--prompt-file", "C:\\banyan-farm\\%s\\prompt.txt" % jid,
                 "--negative-file", "C:\\banyan-farm\\%s\\negative.txt" % jid,
                 "--out", "C:\\banyan-farm\\%s\\out" % jid,
             ]},
            {"name": "publish",
             "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c",
                      _publish_step(jid)]},
        ],
        "artifacts": [
            "C:\\banyan-farm\\%s\\out\\%s-%s.png" % (jid, jid, ARM)],
        "bar": BAR,
        "the_one_variable": (
            "ACROSS THE SHEET: hair (bald / dark cropped / light sandy), build "
            "(burly / lean) and face (slack / dopey), 3x2x2, one seed each. "
            "Everything else -- driver, checkpoint, skeleton, controlnet "
            "scale, wardrobe, pose, location, negative -- is byte-identical in "
            "all twelve, so a difference between two frames is attributable to "
            "the cell and not to the recipe."),
        "no_ip_adapter_on_purpose": (
            "There is no --ip-* flag in this spec and that is the design. The "
            "goblin was solved by pointing the k6a adapter at an image the "
            "founder picked; the guards have no such image, and this sheet is "
            "how one gets made. Conditioning these frames on the goblin's face "
            "reference would draw twelve goblins in guard clothes."),
        "adult_stature_is_geometry_not_a_word": (
            "head_frac 0.190 = 5.2 heads, carried by "
            "%s/%s.png through %s at scale %s. Every 0812 round also carried "
            "`child` in its negative and still produced children, because a "
            "negative cannot set a ratio. jerry_standard_0821 records the same "
            "dial from the other end: n5 moved head_frac 0.190 -> 0.320 alone "
            "and manufactured a bobblehead on demand."
            % (ASSET_DIR, SKEL, CONTROLNET, CONTROL_SCALE)),
        "wardrobe_is_held_not_recast": (
            "cream shirt, white sash, brown wrap skirt -- the garments the "
            "founder ratified 2026-08-16 (\"the cast stands as drawn\") and "
            "which beats 05, 06 and 08 shipped. Held CONSTANT across all "
            "twelve so the only things moving are the three axes he is being "
            "asked about. A pick off this sheet is a face and a build, NOT a "
            "new costume ruling."),
        "clip77_measured_not_estimated": (
            "measured with pipeline/clip_token_count.py against "
            "animagine-xl-3.1's own vocab, per cell, asserted by "
            "`derive_guardcast_0822.py --selftest`. Longest positive across "
            "the twelve cells and the negative are both reported there; no "
            "cell is allowed to exceed 77."),
        "one_sample_rule": (
            "THE BATCH IS THE SAMPLE, and the reason is written out in full in "
            "pipeline/derive_guardcast_0822.py. Short form: the RECIPE is the "
            "ratified stack already sampled across the thirteen-rung k-ladder, "
            "what changes is a character brief's WORDING, the founder has "
            "already looked at the previous wording's output and rejected it, "
            "and a casting sheet cannot be sampled with one candidate because "
            "one candidate cannot answer \"which of these\"."),
        "pre_registered_fail_modes": (
            "1. A CHILD OR FEMALE READ SURVIVES the positive assertion plus "
            "the skeleton -> raise --scale, or move `mature male, facial hair` "
            "earlier. Such a frame is DROPPED, not shown.\n"
            "2. DUMB READS AS UGLY OR DERANGED rather than slow -> drop "
            "`expressionless`, keep `half-closed eyes`, add `:o`.\n"
            "3. ALL TWELVE READ AS ONE MAN -> widen the build axis with "
            "`fat man` / `tall`. The seeds are already distinct."),
        "founder_words_verbatim": (
            "2026-08-20, guards card: \"they should look like grown men. yes. "
            "dumb grown men\". 2026-08-21, on the existing references: \"not "
            "the best... some have girls, and theyre just improper\"."),
        "post_ship_patch": (
            "review/ep2-ship-0821 IS NOT TOUCHED BY THIS JOB OR BY ITS ELEVEN "
            "SIBLINGS. A frame here is a candidate; a candidate becomes a "
            "founder pick, a pick becomes a guard reference, a reference "
            "becomes a plate spec, a plate becomes a motion spec. Five "
            "judgements, none of them this job's."),
    }


def sibling(letter, hair, build, face, seed):
    """One derivation off cell A. Two overrides: the seed and the prompt."""
    return derive_spec.derive(
        src="pipeline/jobs/%s.yaml" % spec_id("A"),
        new_id=spec_id(letter),
        fresh={
            "owner": "guard-casting lane, 2026-08-22",
            "consumer": (
                "THE FOUNDER, tonight, as slot %s of the twelve on "
                "review/ep2-guardcast-0822. It is one cell of one factorial "
                "and it is meaningless alone: what it is FOR is to be "
                "compared with the other eleven." % letter),
            "why": (
                "GUARD CASTING, CELL %s OF TWELVE: %s. One cell of the "
                "3 (hair) x 2 (build) x 2 (face) factorial the founder's "
                "\"dumb grown men\" ruling is being rendered against. Two "
                "things differ from cell A and nothing else does: this cell's "
                "three axis words and its seed."
                % (letter, one_line(letter, hair, build, face))),
            "success": (
                "ONE 832x1216 png at seed %d, scored at 1:1 on the bar carried "
                "from cell A. A pass is a candidate on the picker page; the "
                "cast is the founder's call (R4) and this job does not make "
                "it." % seed),
        },
        overrides={
            "seed": seed,
            "payload:prompt.txt": prompt_for(hair, build, face),
        },
        extra={
            "bar": BAR,
            "the_one_variable": (
                "THE CELL: `%s` -> `%s`, `%s`, `%s`, plus its own seed. The "
                "recipe, the skeleton, the wardrobe, the pose and the negative "
                "are cell A's byte-for-byte."
                % (one_line(letter, hair, build, face),
                   BUILD[build], HAIR[hair], FACE[face])),
            "the_rung_this_is_one_variable_from": (
                "pipeline/jobs/%s.yaml -- cell A, which is not a rung either "
                "but the root of a factorial. All twelve fire in one batch and "
                "are judged together; none waits on another."
                % spec_id("A")),
            "clip77_measured_not_estimated": (
                "positive %d of 77, negative %d of 77, counted with "
                "animagine-xl-3.1's OWN vocab by pipeline/clip_token_count.py "
                "and asserted by `derive_guardcast_0822.py --selftest`."
                % (_tokens(prompt_for(hair, build, face)), _tokens(NEGATIVE))),
        },
        by="pipeline/derive_guardcast_0822.py",
    )


_CLIP = None


def _tokens(text):
    """BPE tokens PLUS the two specials -- the number CLIP's 77 actually caps.

    `Clip.count` returns (bpe, unknown) and excludes <|startoftext|> and
    <|endoftext|>. A spec that reports the bare BPE count is claiming two
    tokens of headroom it does not have, which is exactly the class of error
    clip_token_count.py was written to end.
    """
    global _CLIP
    if _CLIP is None:
        _CLIP = clip.Clip()
    n, unknown = _CLIP.count(text)
    if unknown:
        raise ValueError("unknown token(s) in %r: %s" % (text[:60], unknown))
    return n + 2


def write_all(force=False):
    import yaml
    root = build_root()
    paths = []
    out = os.path.join(REPO, "pipeline", "jobs", "%s.yaml" % root["id"])
    root["clip77_measured_not_estimated"] = (
        "positive %d of 77 for this cell (longest of the twelve is %d), "
        "negative %d of 77, counted with animagine-xl-3.1's OWN vocab by "
        "pipeline/clip_token_count.py and asserted by "
        "`derive_guardcast_0822.py --selftest`."
        % (_tokens(root["payload"][[k for k in root["payload"]
                                    if k.endswith("prompt.txt")][0]]),
           max(_tokens(prompt_for(h, b, f)) for _l, h, b, f in CELLS),
           _tokens(NEGATIVE)))
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(root, fh, sort_keys=False, width=100,
                       default_flow_style=False, allow_unicode=False)
    paths.append(out)
    print("wrote  %s" % os.path.relpath(out, REPO))

    for i, (letter, hair, build, face) in enumerate(CELLS):
        if i == 0:
            continue
        child = sibling(letter, hair, build, face, SEED0 + i)
        p = derive_spec.write(child, "pipeline/jobs/%s.yaml" % spec_id(letter),
                              force=force)
        paths.append(p)
        print("wrote  %s" % os.path.relpath(p, REPO))

    # THE RETOKEN TRAP. derive() rewrites every string, including the fetch
    # URLs, so the guard re-reads the EMITTED yaml and checks each URL against
    # the filesystem. Our assets live in a SHARED dir that carries no job id,
    # so nothing should have been rewritten -- and that is exactly the claim
    # worth asserting rather than assuming.
    for p in paths:
        fetchguard.assert_fetch_urls_resolve(
            p, must_hold=(DRIVER, SKEL + ".png"))
    print("fetch-guard  %d spec(s) OK -- every raw.githubusercontent URL "
          "resolves and names %s/" % (len(paths), ASSET_DIR))
    return paths


def _selftest():
    import yaml
    bad = []

    def check(name, cond, detail=""):
        print("  %-58s %s%s" % (name, "ok" if cond else "FAIL",
                                "" if cond else "  " + detail))
        if not cond:
            bad.append(name)

    print("derive_guardcast_0822 selftest")

    check("12 cells", len(CELLS) == 12, str(len(CELLS)))
    check("12 distinct letters", len({c[0] for c in CELLS}) == 12)
    check("12 distinct seeds",
          len({SEED0 + i for i in range(len(CELLS))}) == 12)
    check("4 bald and 8 with hair",
          sum(1 for c in CELLS if c[1] == "bald") == 4
          and sum(1 for c in CELLS if c[1] != "bald") == 8)
    check("4 with the canon's light sandy hair",
          sum(1 for c in CELLS if c[1] == "sandy") == 4)
    check("2 build variants, 6 cells each",
          sorted(sum(1 for c in CELLS if c[2] == b) for b in BUILD) == [6, 6])
    check("2 face variants, 6 cells each",
          sorted(sum(1 for c in CELLS if c[3] == f) for f in FACE) == [6, 6])

    # CLIP-77. The whole point of measuring rather than counting words.
    worst = 0
    for letter, hair, build, face in CELLS:
        n = _tokens(prompt_for(hair, build, face))
        worst = max(worst, n)
        check("cell %s positive %d of 77" % (letter, n), n <= 77)
    check("negative %d of 77" % _tokens(NEGATIVE), _tokens(NEGATIVE) <= 77)
    check("worst positive %d leaves headroom" % worst, worst <= 77)

    # The gender assertion is POSITIVE and it is EARLY -- the 0812 defect.
    for letter, hair, build, face in CELLS:
        p = prompt_for(hair, build, face)
        head = ", ".join(p.split(", ")[:6])
        check("cell %s asserts 1boy/solo/mature male in the first 6 tags"
              % letter,
              "1boy" in head and "solo" in head and "mature male" in head,
              head)
    # ... and the whole female/child family is negated too.
    for w in ("1girl", "girl", "woman", "female", "breasts", "child",
              "male child", "shota", "toddler", "chibi", "loli", "teenager"):
        check("negative carries %r" % w, w in NEGATIVE.split(", "))
    # AND THE ONE IT MUST NOT CARRY. A bare `boy` in the negative fights the
    # `1boy` the positive is built on -- the checkpoint's male tag at any age.
    check("negative does NOT carry a bare 'boy'",
          "boy" not in NEGATIVE.split(", "))
    # ... and no goblin term leaks into a human guard's positive.
    for letter, hair, build, face in CELLS:
        p = prompt_for(hair, build, face)
        leaks = [w for w in ("goblin", "green skin", "pointy ears",
                             "patchwork", "cloak", "slit pupils")
                 if w in p]
        check("cell %s carries no goblin term" % letter, not leaks, str(leaks))
    # ... and canon.yaml `ep2-guard-hair` forbids `bald` ON A GUARD WITH HAIR.
    # Four cells ARE bald and that is the founder's own new axis, asked for on
    # 2026-08-22 ("bald vs short-hair variants BOTH"); the canon entry forbids
    # `bald` in the BEAT prompts for the CAST cast on 08-14/15, not in a sheet
    # whose purpose is to re-cast. Asserted here so the tension is deliberate.
    check("the 8 haired cells never say `bald`",
          all("bald" not in prompt_for(h, b, f)
              for _l, h, b, f in CELLS if h != "bald"))

    # The assets are on disk with the shas the specs will pin.
    import hashlib
    for name, sha in ((DRIVER, DRIVER_SHA), (SKEL + ".png", SKEL_SHA)):
        p = os.path.join(REPO, ASSET_DIR, name)
        ok = os.path.exists(p) and hashlib.sha256(
            open(p, "rb").read()).hexdigest() == sha
        check("asset %s sha" % name, ok)

    # NO --ip-* ANYWHERE. The defining negative of this recipe.
    root = build_root()
    argv = [t for s in root["steps"] for t in s.get("argv", [])]
    check("no --ip-* flag in the root spec",
          not [a for a in argv if str(a).startswith("--ip-")])

    # Emitted specs, if they exist, still say what this module says.
    for letter, hair, build, face in CELLS:
        p = os.path.join(REPO, "pipeline", "jobs", "%s.yaml" % spec_id(letter))
        if not os.path.exists(p):
            continue
        s = yaml.safe_load(open(p, encoding="utf-8"))
        pk = [k for k in s["payload"] if k.endswith("prompt.txt")][0]
        check("emitted %s prompt matches the cell" % spec_id(letter),
              s["payload"][pk] == prompt_for(hair, build, face))
        a = [t for st in s["steps"] for t in st.get("argv", [])]
        check("emitted %s has no --ip-* flag" % spec_id(letter),
              not [x for x in a if str(x).startswith("--ip-")])
        check("emitted %s seed is its own" % spec_id(letter),
              str(SEED0 + [c[0] for c in CELLS].index(letter))
              in [str(x) for x in a])

    print("\n%s" % ("SELFTEST PASS" if not bad
                    else "SELFTEST FAIL: %d clause(s)\n  %s"
                    % (len(bad), "\n  ".join(bad))))
    return 1 if bad else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    write_all(force="--force" in sys.argv)
    sys.exit(_selftest())
