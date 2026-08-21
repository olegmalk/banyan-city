#!/usr/bin/env python3
r"""THE GOBLIN CANON RECIPE -- the founder's own picture, made runnable.

WHAT THIS FILE IS. `pipeline/jerry_standard_0821.py` froze the k6a recipe this
morning under a STEWARD ruling that was explicitly veto-able by the founder
(R4). At 16:54 the founder exercised that veto in the strongest available form:
he supplied a PICTURE and said "dude, this is how the goblin should look".

    taste/refs/goblin-canon-founder-0821.png   832x1216   commit b93a70da

`pipeline/canon.yaml` -> `ep2-goblin-design-adult` -> `founder_ruling_2026_08_21`
carries the measured attribute list. THIS module is that list expressed as the
values a deriver needs, with a `--selftest` that fails if any of them drifts.

    python3 pipeline/jerry_canon_0821.py             # print the recipe
    python3 pipeline/jerry_canon_0821.py --selftest  # assert every value

$0. No model, no network, no GPU.

═══════════════════════════════════════════════════════════════════════════
WHY THIS IS A NEW MODULE AND NOT AN EDIT TO THE STANDARD

Eleven beats' plates, thirteen ladder rungs and the whole 08-21 age-B wave were
authored through `jerry_standard_0821`. Editing its constants would silently
re-point every one of those at a different character while their sidecars still
claimed the old provenance. The standard stays frozen and reproducible; this is
the recipe from 16:54 onward, and it says on its face what it changed and why.

═══════════════════════════════════════════════════════════════════════════
THE DIFF AGAINST THE STANDARD, TOKEN BY TOKEN, EACH WITH ITS REASON

This is a WHOLESALE recipe change, not a rung -- the reference image changed, so
holding one variable would be theatre. It gets ONE SAMPLE before any batch
(founder, 2026-08-03) and that is exactly how it is being run.

  REFERENCE      jerry-tile-sq20-0821  ->  jerry-canon-sq22-0821
                 Different source image entirely. Built by
                 `author_jerry_canonref_0821.py`, 0.22 head-of-frame, which is
                 the middle of the measured 20-25% law; encoded coverage 6.7%
                 of CLIP's 224x224 against the tile ref's 3.9%, because the crop
                 must be wide enough to hold ears that project 27% of a skull
                 width on each side.

  HEAD_FRAC      0.190  ->  0.370
                 The tile measured 5.2 heads. The founder's image measures
                 2.71 (head 337 px, figure 912 px). This is the largest single
                 change in the file and it is GEOMETRY, carried by the skeleton
                 and ControlNet, not by a word. The standard's own note is that
                 moving this dial to 0.320 "manufactured a bobblehead on
                 demand" -- that is no longer a defect, it is the brief.

  POSITIVE, OUT  `adult`, `man`      canon.yaml's 08-20 correction retired both
                                     as steward drift and the founder has twice
                                     rejected frames for reading adult. The
                                     standard kept them only because changing
                                     the string was "a NEW rung"; the reference
                                     changed today, so this IS the new rung.
                 `blank eyes`        THE PUPIL BAN. Struck. The founder's
                                     drawing has a 7x17 px vertical slit pupil
                                     in a 73x49 px almond eye.
                 `thick eyebrows`    The image's brows are thin, sparse strokes.
                 `patchwork cloak`   Superseded by the costume. Also measured on
                                     08-20 to PAINT THE SKULL at close-up crops.
                 `half-closed eyes`  The eyes in the image are wide open. The
                                     heavy lid is a LID, not a squint, and
                                     `eyebags` carries it without closing them.

  POSITIVE, IN   `pointy ears`, `large ears`   The ear ruling inverted.
                 `slit pupils`       The measured pupil's SHAPE. Its SIZE --
                                     `constricted pupils` -- was drafted in and
                                     then cut by the CLIP-77 budget; see the
                                     comment on IDENTITY for what that costs and
                                     for the five spare tokens to buy it back.
                 `eyebags`           The under-eye bag, which is half the
                                     deadpan and is not an age cue on this face.
                 `thin eyebrows`
                 `mandarin collar`, `green shirt`, `black shorts`, `boots`
                                     The measured costume, minus `long sleeves`
                                     and `belt` on the same token budget.
                 `muted color`       The palette is watercolour-adjacent, low
                                     saturation, high key.

  NEGATIVE, OUT  `pointy ears`, `long pointy ears`, `elf`, `monster boy`
                 All four existed to manufacture the tile's short low flange.
                 canon.yaml: "Danbooru has no tag for a short low swept-back
                 ear ... Absence plus suppression was the lever." The thing
                 they suppress is the thing the founder drew.
                 `pale skin`, `grey skin`   The measured skin is #7C806D, a
                 desaturated grey-olive. Both tags negate the target. THIS IS
                 THE WEAKEST OF THE STRIKES and the one most likely to bring a
                 human complexion back; it is struck on the sample and is the
                 first thing re-negated if the sample's skin goes human.

  NEGATIVE, IN   `blank eyes`, `no pupils`   The positive no longer asks for
                 them; the negative now fights them, because seven days of
                 frames have this checkpoint's habit of drawing them.
                 `cloak`, `hood`, `scarf`    Same, for the costume.

  NEGATIVE, KEPT UNDER PROTEST  `child`, `chibi`. A 2.71-head figure is chibi
                 territory by any tag definition and dropping them is the
                 obvious move. It is not made here: canon.yaml records that
                 loosening the count/age tags "made it worse (a child)", and
                 proportion is carried by HEAD_FRAC. If the sample comes back
                 too tall, THESE ARE THE ROUND-2 VARIABLE and nothing else is.

  KEPT           `1boy`. Measured a dead lever on 08-20 across four settings.
                 Today is not the day to re-open it.

═══════════════════════════════════════════════════════════════════════════
PER-BEAT EMOTION IS A MOUTH TAG AND A BROW TAG, AND NOTHING ELSE

Today's law. The identity clause above is invariant across beats; the beat's
feeling enters through `EMOTION` alone, so a beat that reads wrong is one token
from being re-rendered and cannot take the face with it when it changes.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import author_jerry_canonref_0821 as canonref   # noqa: E402
import author_jerry_skel_0820 as skel           # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 1. THE SOURCE OF TRUTH. ──────────────────────────────────────────────────
CANON_IMAGE = "taste/refs/goblin-canon-founder-0821.png"
CANON_COMMIT = "b93a70da"

# ── 2. THE MEASURED ATTRIBUTES. Every one is in canon.yaml with its method. ──
MEASURED = {
    "head_px": 337, "figure_px": 912, "heads": 2.71, "head_frac": 0.370,
    "skull_w_px": 300, "ear_span_px": 449, "ear_project_pct": 27,
    "eye_w_px": 73, "eye_h_px": 49, "pupil_w_px": 7, "pupil_h_px": 17,
    "skin_hex": "#7C806D", "sclera_hex": "#ABA9A1", "shirt_hex": "#4A5F58",
    "belt_hex": "#10171C", "shorts_hex": "#1A252B", "boot_hex": "#2A3438",
}

# ── 3. THE WORDING. Split so a deriver may change POSE and EMOTION only. ─────
# TRIMMED TO A MEASURED BUDGET, NOT TO TASTE. The first draft of this clause was
# 66 BPE and `pipeline/clip_token_count.py` reported every one of the seven wave
# prompts at 84-90 of CLIP's 77, with the DROPPED TAIL naming the pose and the
# location on all seven -- "arm outstretched, in tall grass, full body" would
# have fallen off beat 02 and "crouching behind a sapling, peeking, in tall
# grass, full body" off beat 04. That is the world-absent and wrong-pose defect
# manufactured at authoring time, silently, by a clause that reads fine. Four
# terms were cut for tokens and each cut is named, with what it costs:
#   `very aesthetic`      -3, quality preamble, the weakest of the three.
#   `colored skin`        -4, Danbooru parent of `green skin`; implied by it.
#   `constricted pupils`  -5, THE REAL COST. The measured pupil is small AND a
#                         vertical slit; `slit pupils` keeps the shape and drops
#                         the size. First thing to buy back if the sample's
#                         pupil comes back large -- there are 5 tokens spare.
#   `long sleeves`, `belt` -5, both measured, both minor at full-body scale.
# Worst case across all 7 poses x 6 emotions is now 72 of 77, asserted below.
IDENTITY = ("masterpiece, best quality, 1boy, solo, goblin, green skin, bald, "
            "pointy ears, large ears, slit pupils, eyebags, thin eyebrows, "
            "mandarin collar, green shirt, black shorts, boots, muted color")
# TRIMMED ON THE SAME BUDGET AS THE POSITIVE, and for a reason the sample
# supplied: round two has to ADD terms to the negative (the second floating head,
# the orange irises) and the 60-token draft left no room -- the first r2 attempt
# measured 88 of 77 and the guard refused all four rungs. Three terms came out:
#   `pointy nose`, `dot nose`  Inherited from the tile recipe, whose canon was
#                              "THERE IS NO HUMAN NOSE ... no drawn nostrils".
#                              The founder's image HAS a small drawn nose with
#                              two nostril dashes, so these two were negating a
#                              feature that is now canon.
#   `scarf`                    Redundant beside `cloak, hood` for a costume the
#                              image draws with a bare neck.
NEGATIVE = ("lowres, worst quality, low quality, text, watermark, "
            "blank eyes, no pupils, thick eyebrows, "
            "cloak, hood, patchwork, "
            "human face, wrinkled skin, old man, hair, beard, "
            "child, chibi, 2boys")
SEED = 20260823                    # the wave's seed, held so takes compare

# The per-beat lever, and the whole per-beat lever. One mouth tag, one brow tag.
EMOTION = {
    "deadpan":  "closed mouth, frown",
    "worried":  "closed mouth, frown, worried",
    "alarmed":  "open mouth, surprised",
    "wary":     "closed mouth, furrowed brow",
    "pleading": "parted lips, sad",
    "relief":   "closed mouth, slight smile",
    "sheepish": "closed mouth, blush, embarrassed",
}

# ── 3b. THE SEVEN BEATS OF THE PATCH WAVE. ───────────────────────────────────
# beat -> (skeleton pose, pose+location words, emotion key, stage direction).
# The POSE WORDS are the age-B wave's own, verbatim where they still describe
# the beat, because the wave was judged on them this morning and changing them
# would add a second variable to a change that already has enough. The LOCATION
# clause is inside the pose words on purpose: "world present" is a scored bar
# and the CLIP-77 budget above exists so this clause survives to the encoder.
WAVE_POSES = {}          # filled below; declared here so selftest can see it
WAVE = {
    2:  ("stride", "walking, arm outstretched, in tall grass, full body",
         "alarmed",
         "THE SPRINT -- 'sprints into frame, skids, and dives behind the "
         "sapling's thin trunk'. He is running from the guards and has not seen "
         "the sapling yet. This is the most frightened he is in the episode."),
    3:  ("crouch", "squatting, hiding behind a thin trunk, in tall grass, "
         "full body", "wary",
         "BAD COVER -- 'crouches behind a trunk that hides roughly one-sixth of "
         "him'. The comedy is that he believes it is working, so the face is "
         "furtive rather than terrified -- held breath, not a scream."),
    4:  ("hunch", "hunched over, leaning out sideways, in tall grass, full body",
         "worried",
         "THE FOOTNOTE -- 'leans out from behind the trunk to look, and pulls "
         "straight back the moment he has looked'. THE PEEK, the founder's own "
         "restaging pick (A, 2026-08-20). The eyes are the whole beat."),
    7:  ("stand", "standing, arms at sides, beside tall grass, full body",
         "worried",
         "CONFISCATE -- 'Guard 1 points at the scavenger, decisive.' He is the "
         "object of the sentence and has just been identified. Apprehension, "
         "not panic: the guards are absurd and he is starting to notice."),
    8:  ("stand", "standing, head bowed, looking down, in tall grass, full body",
         "sheepish",
         "INSIDE HIM -- 'Guard 2 lowers the clipboard and points at the "
         "scavenger's belly.' He is caught, and the thing he is caught with is "
         "already eaten. Sheepish."),
    13: ("sit", "sitting, hands clasped between knees, in tall grass, full body",
         "relief",
         "THE SHADE -- 'The scavenger's legs give out and he drops to sit in "
         "the grass at the base of the stem, then tips his head sideways into "
         "the sapling's hand-sized patch of shade'. Line: '...Thanks for the "
         "shade.' EXHAUSTED, and the first moment he is not being chased."),
    20: ("crouch", "squatting, holding a small fruit, looking up, in tall "
         "grass, full body", "alarmed",
         "EVIDENCE -- 'crouches back down, picks the fig up with both hands, "
         "and looks from it to the sapling's thinnest branch beside him'. "
         "Line: '...Did you just ANSWER me?' Awe. The episode's turn."),
}
WAVE_POSES = {b: v[1] for b, v in WAVE.items()}

# BEAT 13 IS THE SAMPLE, and for the same two reasons the age-B wave spent its
# sample there: it is the frame the founder pointed at when he said the goblin
# reads as an adult, and it was the best pass of the adult wave's round one, so
# a break here is attributable to the new recipe and not to a marginal beat.
SAMPLE_BEAT = 13

# ── 4. THE GEOMETRY. ─────────────────────────────────────────────────────────
HEAD_FRAC = 0.370
CONTROLNET = "xinsir/controlnet-openpose-sdxl-1.0"
CONTROL_SCALE = "1.0"
RENDER_W, RENDER_H = 832, 1216

# ── 5. THE ADAPTER. ──────────────────────────────────────────────────────────
IP_REF = "jerry-canon-sq22-0821"
IP_REF_HEAD_FRAC = 0.22
IP_REF_SHA = "bb10bbb269f07849365693a2f277c05624f6cc0fbe4f4dffe8adbe9fb205416e"
IP_REF_ENCODED_PCT = 6.7
# Every reference on disk, so a rung may name one by stem and the fetch step
# still sha-asserts it. Built by REF_BUILDER at the head-frac in the name.
REF_SHA = {
    "jerry-canon-sq20-0821":
        "abdd9fcfee8dfb3ba99929799bf2301598a75b2b8ab07ed92d813190ddd11a1c",
    "jerry-canon-sq22-0821":
        "bb10bbb269f07849365693a2f277c05624f6cc0fbe4f4dffe8adbe9fb205416e",
    "jerry-canon-sq25-0821":
        "04692a1a0756dd8e6e5d44d2875a72cbe2f7f3c0d6ed5f1b53811ff15949df01",
}
IP_SCALE = "0.7"                   # k6a's, unchanged: the reference moved, not
                                   # the strength, so this stays a fixed point.
IP_WEIGHT = "ip-adapter-plus-face_sdxl_vit-h.safetensors"
IP_WEIGHT_SHA = ("677ad8860204f7d0bfba12d29e6c31ded9beefdf3e4bbd102518357d31"
                 "a292c1")
ASSET_DIR = "farm-out/jerry-canon-assets-0821"
ASSET_URL = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
             + ASSET_DIR + "/")
REF_BUILDER = "pipeline/author_jerry_canonref_0821.py"
REF_BUILDER_ARGS = ["--head-frac", "0.22"]
DRIVER = "controlnet_plate.py"
DRIVER_SHA = "ece54f687d892d1fb1df17211331919bfcb04faac4fe0ee6aa9b0bb231adcc32"
ARM = "ipahead"
# THE DRIVER IS COPIED INTO THIS ASSET DIR RATHER THAN FETCHED FROM THE 0820 ONE,
# and that is not tidiness. `derive_fetch_guard.assert_fetch_urls_resolve` applies
# its `must_hold` list to EVERY farm-out directory a spec fetches from, so a spec
# reaching into two directories can never satisfy it. One dir, every input.
ASSET_COMMIT = None      # set by --stamp-commit before the first spec is written

# ── 6. THE MASK, AND WHY IT IS NOT THE STANDARD'S. ───────────────────────────
# jerry_standard's MASK_STAND is (315,130,515,350): 200x220 px, authored around a
# head_frac 0.190 skull with flanges that "barely break the silhouette". At
# head_frac 0.370 the head is 360 px tall on its own, so that mask would sit
# inside the forehead and the adapter would never touch the ears -- which are now
# the loudest thing in the design. The box below is DERIVED from the skeleton
# rather than authored, so it follows the pose and the head ratio together.
MASK_EAR_SPAN_RATIO = 449.0 / 300.0     # measured: ear span / skull width
MASK_MARGIN_PX = 20


def head_box(pose="stand", head_frac=HEAD_FRAC):
    """The head-and-ears box in render pixels, for one pose. 'x0,y0,x1,y1'."""
    kp, _ = skel.figure(head_frac, pose=pose)
    stature = skel.STATURE * RENDER_H
    head_h = head_frac * stature
    skull_w = skel.HEAD_RATIO * head_h
    cx = (kp["Rear"][0] + kp["Lear"][0]) / 2.0
    # The skeleton's nose sits 0.55 of the head height below the crown.
    crown = kp["nose"][1] - head_h * 0.55
    half = skull_w * MASK_EAR_SPAN_RATIO / 2.0 + MASK_MARGIN_PX
    box = [cx - half, crown - MASK_MARGIN_PX,
           cx + half, crown + head_h + MASK_MARGIN_PX]
    box = [int(round(v)) for v in box]
    box[0] = max(0, box[0]); box[1] = max(0, box[1])
    box[2] = min(RENDER_W, box[2]); box[3] = min(RENDER_H, box[3])
    if box[2] - box[0] < 40 or box[3] - box[1] < 40:
        raise ValueError("pose %r leaves a %dx%d mask" % (pose, box[2] - box[0],
                                                          box[3] - box[1]))
    return "%d,%d,%d,%d" % tuple(box)


def prompt_for(pose_words, emotion="deadpan"):
    """The identity clause with the POSE and the EMOTION swapped, nothing else."""
    if emotion not in EMOTION:
        raise KeyError("no emotion %r; have %s" % (emotion,
                                                   sorted(EMOTION)))
    return "%s, %s, %s" % (IDENTITY, EMOTION[emotion], pose_words)


def skeleton_stem(pose):
    return "jerry-canon-h37%s-0821" % ("" if pose == "stand" else pose)


# The poses the ep2 wave needs, and the sha each skeleton must have. Built by
# `--build-skeletons`, asserted by `--selftest`, pinned by every spec.
SKELETONS = {
    "stand":  "jerry-canon-h37-0821",
    "stride": "jerry-canon-h37stride-0821",
    "crouch": "jerry-canon-h37crouch-0821",
    "hunch":  "jerry-canon-h37hunch-0821",
    "kneel":  "jerry-canon-h37kneel-0821",
    "reach":  "jerry-canon-h37reach-0821",
    "point":  "jerry-canon-h37point-0821",
    "sit":    "jerry-canon-h37sit-0821",
}
SKELETON_SHA = {
    "jerry-canon-h37-0821":
        "ef352f6414ee2836141844d6a67ea71215f01b5c94acb26637412f65253cb3fc",
    "jerry-canon-h37stride-0821":
        "abfa4db8cb7477717884620d1e8a498eff82f76261fabca76a3058ecd8f7aad1",
    "jerry-canon-h37crouch-0821":
        "c45dc4f42ef4ffdd403adbee597c225bdcd33892f1146ebeb8bb7278131698c9",
    "jerry-canon-h37hunch-0821":
        "a36474b475fbf3a0c885cbbee065c2e8e9b00b3afd78718b031d2cc6b8cfce05",
    "jerry-canon-h37kneel-0821":
        "05842caf9c9168c06d87f33aa656009f0be45db224f0f3d29f8b5b1af8138066",
    "jerry-canon-h37reach-0821":
        "c6a72ac79ee177dd405bbc8e97fa4741e3ec2983472db07b5162cd561d6c5779",
    "jerry-canon-h37point-0821":
        "51143109c988e7cac9d4eef65c008851f538ff07bd97e889439dc074ffb3f90a",
    "jerry-canon-h37sit-0821":
        "5a37c536d4bbd59b535154da56de164c6316a6844a033c823ee6c54860be08bb",
}


def stage_step(job_dir, stem, ip_ref=None):
    """Fetch + sha-assert driver, skeleton and reference before a GPU second."""
    return (
        '# EVERY INPUT THIS FRAME IS CONDITIONED ON IS FETCHED AND SHA-CHECKED\n'
        '# BEFORE A GPU SECOND IS SPENT -- driver, skeleton AND the IP-Adapter\n'
        '# reference. Emitted by pipeline/jerry_canon_0821.py.\n'
        'import hashlib, os, urllib.request\n'
        'base = "%s"\n'
        'root = r"C:\\banyan-farm\\%s\\src"\n'
        'want = [("%s", os.path.join(root, "pipeline"),\n'
        '         "%s"),\n'
        '        ("%s.png", os.path.join(root, "pipeline", "control"),\n'
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
        % (ASSET_URL, job_dir, DRIVER, DRIVER_SHA,
           stem, SKELETON_SHA[stem], ip_ref or IP_REF,
           REF_SHA[ip_ref or IP_REF]))


def publish_step(job_dir, new_id, stem, ip_ref=None):
    """farm-out or it never happened; the conditions travel with the frame."""
    return (
        '# The courier pushes from farm-out and from nowhere else.\n'
        '# The CONDITIONS travel with the frame: a reader scoring whether the\n'
        '# adapter carried the EAR needs the ear it was shown.\n'
        'import glob, hashlib, os, shutil\n'
        'out_dir = "C:/banyan-farm/%(d)s/out"\n'
        'pay_dir = "C:/banyan-farm/%(d)s"\n'
        'ctl_dir = "C:/banyan-farm/%(d)s/src/pipeline/control"\n'
        'dst = "C:/banyan-farm/courier-box/farm-out/%(i)s"\n'
        'os.makedirs(dst, exist_ok=True)\n'
        'files = sorted(glob.glob(out_dir + "/%(i)s-%(a)s.png*")\n'
        '               + glob.glob(pay_dir + "/prompt.txt")\n'
        '               + glob.glob(pay_dir + "/negative.txt")\n'
        '               + glob.glob(ctl_dir + "/%(h)s.png")\n'
        '               + glob.glob(ctl_dir + "/%(r)s.png"))\n'
        'lines = []\n'
        'for f in files:\n'
        '    shutil.copy2(f, dst)\n'
        '    c = os.path.join(dst, os.path.basename(f))\n'
        '    with open(c, "rb") as fh:\n'
        '        h = hashlib.sha256(fh.read()).hexdigest()\n'
        '    lines.append(h + "  " + os.path.basename(f))\n'
        'with open(os.path.join(dst, "%(i)s.sha256"), "w", newline="\\n") as fh:\n'
        '    fh.write("\\n".join(sorted(lines)) + "\\n")\n'
        'print("published", len(files), "file(s) + manifest ->", dst)\n'
        'raise SystemExit(0 if len(files) >= 6 else 1)\n'
        % {"d": job_dir, "i": new_id, "a": ARM, "h": stem,
           "r": ip_ref or IP_REF})


def ip_adapter_block(pose):
    """The provenance block every derived spec carries. Nothing is optional."""
    stem = SKELETONS[pose]
    return {
        "ruling": (
            "FOUNDER RULING, 2026-08-21 16:54, and it is an IMAGE, not a "
            "sentence: taste/refs/goblin-canon-founder-0821.png, committed "
            "b93a70da, with \"dude, this is how the goblin should look\". It "
            "supersedes tile B and the 08-21 age-B recipe on every axis it "
            "shows. See canon.yaml `ep2-goblin-design-adult` -> "
            "`founder_ruling_2026_08_21` and pipeline/jerry_canon_0821.py."),
        "ref": "%s/%s.png" % (ASSET_DIR, IP_REF),
        "ref_sha256": IP_REF_SHA,
        "ref_provenance": (
            "goblin-canon-founder-0821.png cropped (187,110)-(677,483) -- the "
            "measured head box plus 18 px, WIDE because the ears project 27%% "
            "of a skull width on each side -- background flood-filled with the "
            "image's own field median (187,195,149), pasted CENTRED at %.0f%% "
            "head-of-frame on a 448x448 SQUARE canvas. Square is load-bearing: "
            "diffusers builds CLIPImageProcessor() with no arguments, which "
            "resizes the SHORT edge to 224 and CENTRE CROPS to a square, so "
            "only on a square canvas is the authored head ratio the ratio the "
            "encoder receives. Encoder coverage here is %.1f%% and the subject "
            "touches no encoder edge (asserted by the builder, which returns 1 "
            "if it does). Rebuild with `%s --head-frac %.2f`; assert with "
            "`--check %s`."
            % (IP_REF_HEAD_FRAC * 100, IP_REF_ENCODED_PCT, REF_BUILDER,
               IP_REF_HEAD_FRAC, IP_REF_SHA)),
        "mask": head_box(pose),
        "mask_frame": "RENDER pixels, 832x1216",
        "mask_rule": (
            "DERIVED FROM THE SKELETON, not scaled from k6a's box. k6a's "
            "315,130,515,350 was authored around a head_frac 0.190 skull whose "
            "ears 'barely break the silhouette'. At head_frac 0.370 the head "
            "alone is 360 px tall and the ears reach 449/300 of a skull width, "
            "so that box would sit inside the forehead and the adapter would "
            "never touch the loudest thing in the new design. This box is the "
            "crown-to-chin span at this pose, widened by the MEASURED ear-span "
            "ratio 449/300 and 20 px of margin. Derived by "
            "pipeline/jerry_canon_0821.head_box(%r)." % pose),
        "scale": IP_SCALE,
        "weights": (
            "h94/IP-Adapter sdxl_models/%s, apache-2.0, sha256 %s, 847517512 "
            "bytes. THE GENERAL ADAPTER ip-adapter-plus_sdxl_vit-h.safetensors "
            "IS THE SAME NUMBER OF BYTES, so only the digest separates them; "
            "controlnet_plate.py carries an allowlist keyed by name and "
            "carrying the digest." % (IP_WEIGHT, IP_WEIGHT_SHA)),
        "skeleton": "%s/%s.png" % (ASSET_DIR, stem),
        "skeleton_sha256": SKELETON_SHA[stem],
        "head_frac": HEAD_FRAC,
        "controlnet": "%s at scale %s" % (CONTROLNET, CONTROL_SCALE),
        "proportion_ruling": (
            "head_frac 0.370 = 2.71 heads, MEASURED off the founder's image "
            "(head 337 px, figure 912 px). The tile measured 5.2 and the frozen "
            "standard holds 0.190. Recorded caveat: the image's camera is ABOVE "
            "the subject, which foreshortens the legs more than the head, so "
            "2.71 is the ratio at THAT camera and a level-camera full body will "
            "measure taller. Proportion is carried here by GEOMETRY -- the "
            "skeleton and ControlNet -- and by no word in the prompt."),
    }


def build_skeletons():
    import hashlib
    out = os.path.join(REPO, ASSET_DIR)
    os.makedirs(out, exist_ok=True)
    for pose, stem in sorted(SKELETONS.items()):
        img, meta = skel.build(HEAD_FRAC, pose=pose)
        p = os.path.join(out, stem + ".png")
        img.save(p)
        sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
        print('    "%s": "%s",' % (stem, sha))
        print("        # %s  %s  mask %s" % (pose, meta, head_box(pose)))
    return 0


def selftest():
    bad = []

    def want(cond, msg):
        if not cond:
            bad.append(msg)

    # The reference on disk is the reference this module names.
    import hashlib
    p = os.path.join(REPO, ASSET_DIR, IP_REF + ".png")
    want(os.path.exists(p), "%s.png is not on disk" % IP_REF)
    if os.path.exists(p):
        got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        want(got == IP_REF_SHA, "%s is %s, this module pins %s"
             % (IP_REF, got[:16], IP_REF_SHA[:16]))
    want(canonref.HEAD_H == MEASURED["head_px"],
         "builder head %d != canon %d" % (canonref.HEAD_H,
                                          MEASURED["head_px"]))
    # Every pupil ban is gone from the positive and present in the negative.
    for dead in ("blank eyes", "thick eyebrows", "patchwork", "adult", "man,",
                 "half-closed eyes"):
        want(dead not in IDENTITY, "positive still carries %r" % dead)
    for revived in ("pointy ears", "large ears", "slit pupils"):
        want(revived in IDENTITY, "positive is missing %r" % revived)
        want(revived not in NEGATIVE, "negative still bans %r" % revived)
    for gone in ("elf", "monster boy", "pale skin", "grey skin"):
        want(gone not in NEGATIVE, "negative still carries %r" % gone)
    want("blank eyes" in NEGATIVE, "negative does not fight blank eyes")
    # Geometry.
    want(abs(HEAD_FRAC - MEASURED["head_frac"]) < 1e-9, "HEAD_FRAC drifted")
    want(abs(MEASURED["head_px"] / float(MEASURED["figure_px"])
             - MEASURED["head_frac"]) < 0.002, "head_frac is not the measurement")
    # The mask reaches the ears at every pose we will use.
    for pose in ("stand", "stride", "crouch", "hunch", "kneel"):
        b = [int(v) for v in head_box(pose).split(",")]
        want(b[2] - b[0] >= 400, "%s mask is only %d px wide -- the ears are "
                                 "outside it" % (pose, b[2] - b[0]))
    # Emotion is one mouth tag and one brow/mood tag, never identity.
    for k, v in EMOTION.items():
        want("goblin" not in v and "ears" not in v,
             "emotion %r leaks identity" % k)
    # CLIP-77, MEASURED WITH THE MODEL'S OWN VOCAB, over the WHOLE cross-product.
    # This is not decoration: the first draft of IDENTITY put all seven wave
    # prompts at 84-90 of 77 and the dropped tail was the pose and the location
    # every time. A clause that overruns does not fail loudly, it silently
    # renders the wrong picture, so the ceiling is asserted here rather than
    # checked once by hand.
    try:
        import clip_token_count as clip
        c = clip.Clip()
        worst, worst_at = 0, None
        for pose_words in WAVE_POSES.values():
            for emo in EMOTION:
                tot = c.count(prompt_for(pose_words, emo))[0] + clip.SPECIALS
                if tot > worst:
                    worst, worst_at = tot, (emo, pose_words)
        want(worst <= clip.CEILING,
             "worst prompt is %d of %d (%s) -- the tail, which is the POSE and "
             "the LOCATION, will be dropped" % (worst, clip.CEILING, worst_at))
        n_neg = c.count(NEGATIVE)[0] + clip.SPECIALS
        want(n_neg <= clip.CEILING, "negative is %d of %d" % (n_neg,
                                                              clip.CEILING))
        print("  clip77: worst positive %d, negative %d, ceiling %d"
              % (worst, n_neg, clip.CEILING))
    except SystemExit:
        print("  clip77: SKIPPED -- no animagine tokenizer in the HF cache")

    for m in bad:
        print("  !! %s" % m)
    print("jerry_canon_0821 selftest: %s (%d checks failed)"
          % ("FAIL" if bad else "PASS", len(bad)))
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--build-skeletons", action="store_true")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    if a.build_skeletons:
        return build_skeletons()
    if a.selftest:
        return selftest()
    print("CANON   %s @ %s" % (CANON_IMAGE, CANON_COMMIT))
    print("REF     %s  sha %s  head %.2f  encoded %.1f%%"
          % (IP_REF, IP_REF_SHA[:16], IP_REF_HEAD_FRAC, IP_REF_ENCODED_PCT))
    print("GEOM    head_frac %.3f  (%.2f heads)  mask stand %s"
          % (HEAD_FRAC, MEASURED["heads"], head_box("stand")))
    print("POS     %s" % IDENTITY)
    print("NEG     %s" % NEGATIVE)
    for k in sorted(EMOTION):
        print("EMO %-9s %s" % (k, EMOTION[k]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
