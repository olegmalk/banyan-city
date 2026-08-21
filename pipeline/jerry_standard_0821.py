#!/usr/bin/env python3
r"""THE GOBLIN STANDARD -- k6a, frozen, runnable, and self-checking.

WHAT THIS FILE IS. The steward ruling of 2026-08-21 (coordinator, veto-able)
names `ep2-jerry-face-k6a-0821` THE recipe for drawing Jerry. Until now that
recipe existed only as one job yaml among thirteen sibling rungs and as prose in
`pipeline/work-ladder-0819.md`. A recipe that lives in one yaml is a recipe the
next lane copies by hand and gets wrong in one field. This module IS the recipe:
every value the ruling names, in one place, importable by any deriver, with a
`--selftest` that fails loudly if any of them drifts.

    python3 pipeline/jerry_standard_0821.py            # print the standard
    python3 pipeline/jerry_standard_0821.py --selftest  # assert every value

$0. No model, no network, no GPU.

═══════════════════════════════════════════════════════════════════════════
THE RULING, RECORDED WITH ITS AUTHORITY AND ITS LIMIT

STEWARD RULING, coordinator, 2026-08-21, VETO-ABLE BY THE FOUNDER (R4). The
open question the ladder handed him was k4a vs k6a and it is a taste question --
what Jerry's eye looks like. The steward answered it to unblock the wave rather
than hold the card idle, and it is recorded as a steward pick, not as a founder
ruling. If the founder prefers k4a's fuller brow and larger eye, every frame
derived through this module is re-derivable by changing REF and IP_SCALE here.

WHY k6a AND NOT k4a, on the ladder's own measured numbers:

    rung   eye vs TILE   aspect   mouth   brow    T8 heads   head_frac   cowl
    TILE      1.00x       0.52    yes     bar       5.2        0.190      --
    k4a       1.40x       0.59    yes     fuller    5.13       0.195      0.0%
    k5a       1.26x       0.53    NONE    stroke    5.31       0.188      0.0%
    k6a       1.07x       0.63    yes     stroke    5.51       0.181      0.0%

k6a is the first frame in the whole ladder whose eye is not oversized -- 1.07x
where six wording rungs and both earlier adapters sat at 1.26x-2.32x, and where
j2 with NO adapter draws 1.40x. It keeps the mouth (P3), which k5a lost. It has
no horns, no cowl, and containment holds. It fails nothing except the T1b SHAPE
clause as that clause was originally written, and that clause is recalibrated
below on the evidence.

THE T1b SHAPE BAR IS RECALIBRATED: 0.52-0.54 --> <= 0.65. This is the part of
the ruling that is a correction to our own instrument and not a preference.
In the entire thirteen-rung ladder exactly three frames ever met 0.52-0.54:

    k1  aspect 0.54  -- and its eye was 1.87x the tile's
    k3  aspect 0.54  -- and it grew HORNS and put the tile's purple cowl back
    k5a aspect 0.53  -- and it had NO MOUTH AT ALL

Every frame that met the bar failed something worse, and the frames reading
0.59-0.63 read as the tile by eye. A bar that only defective frames have ever
met is a bar that is measuring something other than what it was written to
measure -- it is selecting for crippled reference embeddings, which is exactly
what k3's "best in tree" 1.24x turned out to be. The bar is therefore widened to
<= 0.65, which admits k4a (0.59), k5a (0.53) and k6a (0.63) and still refuses
every wording rung (1.00-1.26) the reference route was built to beat.

WHAT THE BAR IS NOT WIDENED TO COVER: eye SIZE. The <= 1.4x clause stands, and
k6a passes it at 1.07x with room. Widening shape does not widen size.

═══════════════════════════════════════════════════════════════════════════
A NOTE ON THE WORDING, BECAUSE IT CONTRADICTS CANON ON ITS FACE

The frozen positive says `lean wiry adult goblin man`. canon.yaml's
`ep2-goblin-design-adult` correction_2026_08_20 RETIRED the word "adult" as
drift. Both are true and the tension is deliberate, so it is written down here
rather than discovered later:

  * The WORDS are not the character. They are the six-token clause that this
    checkpoint happens to condition on while the ADAPTER supplies the face. The
    k6a frame was scored at 1:1 against `adult-b19-0819.jpg` on T1 (blank eyes),
    T2 (no nose), T3 (no age modelling), P1 (brow), P2 (muzzle), P3 (mouth),
    P4 (shading) and T8 (head-to-body) and passes all eight. The pixels are the
    creature; the string is a lever.
  * Changing the string is NOT free and has been measured to be not free: the
    wording route was walked for six rungs (f4/g1/g2/h1/h2/j1/j2) and closed.
    Substituting canon's own tile vocabulary into this slot is a NEW rung, not
    a tidy-up, and it would move the one variable in every frame derived here.

So the string is frozen AS MEASURED, and the reason is recorded so that nobody
reads it as canon having been ignored.
"""
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import author_jerry_skel_0820 as skel          # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 1. THE PARENT RUNG. Every derived spec is one variable from this one. ────
PARENT = "pipeline/jobs/ep2-jerry-face-k6a-0821.yaml"
PARENT_ID = "ep2-jerry-face-k6a-0821"
PARENT_DIR_TOKEN = "jerryface-k6a-0821"

# ── 2. THE FROZEN WORDING. k5a's, which is j2's, byte-for-byte. ──────────────
# Split at the pose clause so a deriver may change the POSE and nothing else.
# `PROMPT_HEAD` + ", " + pose == the k6a payload exactly; selftest asserts it.
PROMPT_HEAD = ("masterpiece, best quality, very aesthetic, 1boy, solo, "
               "lean wiry adult goblin man, green skin, bald head, "
               "patchwork cloak, blank eyes, tsurime, jitome, thick eyebrows, "
               "half-closed eyes")
POSE_STAND = "standing, arms at sides, in tall grass, full body"
NEGATIVE = ("lowres, worst quality, low quality, text, watermark, pointy ears, "
            "long pointy ears, elf, monster boy, pointy nose, dot nose, "
            "human face, wrinkled skin, old man, hair, beard, child, chibi, "
            "grey skin, pale skin")
SEED = 20260823

# ── 3. THE SKELETON. head_frac 0.190 is the tile's MEASURED value. ───────────
# adult-b19-0819.jpg at 1:1: head 155 px, seated crown-to-sole 623 px, seated is
# ~0.77 of standing -> 5.2 heads standing -> 1/5.2 = 0.190. n5 moved this dial
# alone, 0.190 -> 0.320, and manufactured a bobblehead on demand: it is a dial
# and we hold it.
HEAD_FRAC = 0.190
CONTROLNET = "xinsir/controlnet-openpose-sdxl-1.0"
CONTROL_SCALE = "1.0"
ARM = "ipahead"

# THE SPAN RULE, asserted in `author_jerry_skel_0820 --selftest` and load-bearing
# for the mask rule below: the five head keypoints (nose, both eyes, both ears)
# move as ONE RIGID BLOCK when a pose lowers them. The ear span is 136.0 px in
# every pose at head_frac 0.190. A pose therefore TRANSLATES the head; it never
# resizes it, which is why a mask authored once can follow a pose by translation
# and why head-to-body cannot leak out through the pose axis.
HEAD_KEYPOINTS = ("nose", "Reye", "Leye", "Rear", "Lear")
EAR_SPAN_PX = 136.0

SKELETONS = {
    # stem                            pose arg      sha256
    "jerry-skel-h19-0820":      ("stand",
        "244094ed608666035d670d8bc5149ff6499c1497e5501724728d2af79b54829c"),
    "jerry-skel-h19stride-0820": ("stride",
        "a853228c770ff9a3015985a5cd1250dc8d020c0f112121f084840a847dcde3f0"),
    "jerry-skel-h19kneel-0820": ("kneel",
        "96cf22c5fe60cee184de5b91bc04e83fdb599a714a1667f01cc49512acf163d4"),
    "jerry-skel-h19sit-0820":   ("sit",
        "ce25c2f17bf158f650fc7f1a74fcacf32b9603ad74da9b4dd6ef85d00834f908"),
    "jerry-skel-h19crouch-0820": ("crouch",
        "b3028a04ed18ed992cfa884900443d8ee547423e0dcfd72e42c4dfa52d2352fe"),
    "jerry-skel-h19reach-0820": ("reach",
        "fb22b82c713891ff875116cbc68649ac08c1f981fb57750f34289ff2aae1119f"),
    "jerry-skel-h19point-0820": ("point",
        "1b0876d4eb8381c0052d2281a4fbe0319868f96faf626f62d8fa378083595d23"),
    "jerry-skel-h19hunch-0820": ("hunch",
        "78422b89fa81d5d6fadc53fbf4a275e3d08c964f148f1cd2dd845a6fc90331f0"),
    "jerry-skel-h19seat-0820":  ("seatspan",
        "adaf7f1ed44b9d6ed990a40dbbf6396c19c08f2ade83723cd0aac976fe0210cb"),
}

# ── 4. THE ADAPTER RECIPE. This is what k6a changed and what the ruling picks. ─
IP_REF = "jerry-tile-sq20-0821"
IP_REF_SHA = "f65c9bb412e541fbe9b6024ddaec5a78b78028afd87e325baa06d6d430dded14"
IP_REF_HEAD_FRAC = 0.20          # head 20% of a SQUARE reference canvas
IP_REF_ENCODED_PCT = 3.9         # what CLIP's 224x224 actually receives
IP_SCALE = "0.7"
IP_WEIGHT = "ip-adapter-plus-face_sdxl_vit-h.safetensors"
IP_WEIGHT_SHA = ("677ad8860204f7d0bfba12d29e6c31ded9beefdf3e4bbd102518357d31"
                 "a292c1")
IP_WEIGHT_BYTES = 847517512
# THE DIGEST IS THE ONLY THING THAT TELLS THE TWO ADAPTERS APART. The general
# `ip-adapter-plus_sdxl_vit-h.safetensors` is the SAME 847,517,512 bytes. A size
# check passes the wrong one, which is why controlnet_plate.py carries an
# allowlist keyed by name and carrying the digest, and why every sidecar records
# which weight actually rendered the frame.
IP_WEIGHT_GENERAL = "ip-adapter-plus_sdxl_vit-h.safetensors"

# The reference is BUILT, not stored by hand. Reproduce it with:
#     python3 pipeline/author_jerry_squareref_0821.py --head-frac 0.20
#     python3 pipeline/author_jerry_squareref_0821.py --head-frac 0.20 \
#             --check f65c9bb412e541fbe9b6024ddaec5a78b78028afd87e325baa06d6d430dded14
REF_BUILDER = "pipeline/author_jerry_squareref_0821.py"
REF_BUILDER_ARGS = ["--head-frac", "0.20"]

# ── 5. THE MASK, AND THE RULE THAT MOVES IT. ─────────────────────────────────
# k6a's mask in RENDER pixels on an 832x1216 canvas. Authored once, at k1, for a
# STANDING figure's head box.
MASK_STAND = (315, 130, 515, 350)
RENDER_W, RENDER_H = 832, 1216

ASSET_DIR = "farm-out/jerry-skel-assets-0820"
ASSET_URL = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
             + ASSET_DIR + "/")
DRIVER = "controlnet_plate.py"
DRIVER_SHA = "ece54f687d892d1fb1df17211331919bfcb04faac4fe0ee6aa9b0bb231adcc32"
ASSET_COMMIT = "894b6214ce4ce3f88e8d518ae33de73fbc71f909"

TILE = "review/ep2-goblin-design-0819/adult-b19-0819.jpg"


def head_centre(pose, head_frac=HEAD_FRAC):
    """Centroid of the five head keypoints, in render pixels, for one pose."""
    kp, _ = skel.figure(head_frac, pose=pose)
    xs = [kp[k][0] for k in HEAD_KEYPOINTS]
    ys = [kp[k][1] for k in HEAD_KEYPOINTS]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def mask_for(pose, head_frac=HEAD_FRAC):
    """k6a's mask TRANSLATED by the pose's head-block offset. Returns 'x0,y0,x1,y1'.

    THIS IS NOT A NEW MASK AND IT IS NOT A GUESS. The head keypoints move as one
    rigid block between poses (see HEAD_KEYPOINTS above), so the head box a mask
    was authored around translates rigidly with them. Translating the mask by the
    same delta keeps the adapter acting on exactly the region it acted on in k6a
    -- for `stand` the delta is zero and this returns k6a's mask byte-for-byte,
    which `--selftest` asserts.

    The alternative -- reusing 315,130,515,350 for a kneeling figure -- would
    point the face adapter at empty sky above his head, and a mask says WHERE the
    adapter acts.
    """
    bx, by = head_centre("stand")
    cx, cy = head_centre(pose, head_frac)
    dx, dy = cx - bx, cy - by
    x0, y0, x1, y1 = MASK_STAND
    r = [x0 + dx, y0 + dy, x1 + dx, y1 + dy]
    r = [int(round(v)) for v in r]
    # controlnet_plate.parse_rect refuses anything outside the frame. Clamp and
    # say so rather than emitting a spec that dies with rc=10 on the card.
    r[0] = max(0, r[0]); r[1] = max(0, r[1])
    r[2] = min(RENDER_W, r[2]); r[3] = min(RENDER_H, r[3])
    if r[2] - r[0] < 40 or r[3] - r[1] < 40:
        raise ValueError("pose %r leaves a %dx%d mask -- too small to act on"
                         % (pose, r[2] - r[0], r[3] - r[1]))
    return "%d,%d,%d,%d" % tuple(r)


def prompt_for(pose_words):
    """The frozen wording with the POSE clause swapped and nothing else."""
    return "%s, %s" % (PROMPT_HEAD, pose_words)


def stage_step(job_dir, hint):
    """Fetch + sha-assert every input before a GPU second is spent.

    Three inputs, because a frame conditioned on a skeleton AND a reference has
    three conditions and all three have to be the bytes we think they are. The
    job dirs on the card carry nothing, so a file that is not fetched is a job
    that dies after the queue has claimed it.
    """
    return (
        '# EVERY INPUT THIS FRAME IS CONDITIONED ON IS FETCHED AND SHA-CHECKED\n'
        '# BEFORE A GPU SECOND IS SPENT -- driver, skeleton AND the IP-Adapter\n'
        '# reference, because the reference is as much a condition as the\n'
        '# skeleton is. Emitted by pipeline/jerry_standard_0821.py.\n'
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
           hint, SKELETONS[hint][1], IP_REF, IP_REF_SHA))


def publish_step(job_dir, new_id, hint):
    """farm-out or it never happened, and the conditions travel with the frame.

    A reader scoring whether the adapter carried the brow needs the brow it was
    shown, so the reference and the skeleton are published beside the png.
    """
    return (
        '# The courier pushes from farm-out and from nowhere else --\n'
        '# ep2-cnet-probe-0817 rendered perfectly and was invisible for two\n'
        '# days for want of this step. The CONDITIONS travel with the frame.\n'
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
        % {"d": job_dir, "i": new_id, "a": ARM, "h": hint, "r": IP_REF})


def ip_adapter_block(hint, pose):
    """The provenance block every derived spec carries. Nothing here is optional."""
    return {
        "ruling": ("STEWARD PICK, coordinator 2026-08-21, VETO-ABLE (R4). k6a "
                   "is THE goblin recipe; the T1b shape bar is recalibrated "
                   "0.52-0.54 -> <= 0.65 because only defective frames ever met "
                   "the old value (k1 eye 1.87x, k3 horns and cowl, k5a no "
                   "mouth) while 0.59-0.63 frames read as the tile. See "
                   "pipeline/jerry_standard_0821.py and canon.yaml."),
        "ref": "%s/%s.png" % (ASSET_DIR, IP_REF),
        "ref_sha256": IP_REF_SHA,
        "ref_provenance": (
            "adult-b19-0819.jpg cropped (176,280)-(332,432), sky flood-filled "
            "with the tile's own field green, pasted CENTRED at %.0f%% of a "
            "448x448 SQUARE canvas. Square is load-bearing: diffusers builds "
            "CLIPImageProcessor() with no arguments, which resizes the SHORT "
            "edge to 224 and CENTRE CROPS to a square, so only on a square "
            "canvas is the authored head-to-frame ratio the ratio the encoder "
            "receives. k3's 416x608 portrait lost the top 30%% of the subject "
            "-- the whole cranial dome -- to that crop and grew horns out of "
            "the cut. Encoder coverage here is %.1f%%. Rebuild with `%s "
            "--head-frac %.2f`; assert with `--check %s`."
            % (IP_REF_HEAD_FRAC * 100, IP_REF_ENCODED_PCT, REF_BUILDER,
               IP_REF_HEAD_FRAC, IP_REF_SHA)),
        "mask": mask_for(pose),
        "mask_frame": "RENDER pixels, %dx%d" % (RENDER_W, RENDER_H),
        "mask_rule": (
            "k6a's authored mask %s TRANSLATED by this pose's head-block "
            "offset. The five head keypoints move as one rigid block between "
            "poses (ear span %.1f px in every pose at head_frac %.3f), so the "
            "head box translates rigidly and so does the mask. For `stand` the "
            "delta is zero and this IS k6a's mask. Derived by "
            "pipeline/jerry_standard_0821.mask_for(%r)."
            % (",".join(str(v) for v in MASK_STAND), EAR_SPAN_PX, HEAD_FRAC,
               pose)),
        "scale": IP_SCALE,
        "weights": (
            "h94/IP-Adapter sdxl_models/%s, apache-2.0, sha256 %s, %d bytes. "
            "THE GENERAL ADAPTER %s IS THE SAME NUMBER OF BYTES, so only the "
            "digest separates them; controlnet_plate.py carries an IP_WEIGHTS "
            "allowlist keyed by name and carrying the digest, and the sidecar "
            "records which one actually rendered the frame."
            % (IP_WEIGHT, IP_WEIGHT_SHA, IP_WEIGHT_BYTES, IP_WEIGHT_GENERAL)),
        "skeleton": "%s/%s.png" % (ASSET_DIR, hint),
        "skeleton_sha256": SKELETONS[hint][1],
        "head_frac": HEAD_FRAC,
        "controlnet": "%s at scale %s" % (CONTROLNET, CONTROL_SCALE),
    }


BAR = """THE k6a BAR, AS RECALIBRATED BY THE 2026-08-21 STEWARD RULING.
Read at 1:1 against review/ep2-goblin-design-0819/adult-b19-0819.jpg.
  T1  BLANK EYES -- no iris, no pupil, no lashes.
  T1b EYE SIZE <= 1.4x the tile's, relative to the head box. NOT widened.
      EYE SHAPE (h/w aspect) <= 0.65. RECALIBRATED from 0.52-0.54: only
      defective frames ever met the old value -- k1 met it with a 1.87x eye,
      k3 with horns and the cowl, k5a with no mouth -- while 0.59-0.63 frames
      read as the tile. k6a sits at 0.63.
  T2  NO HUMAN NOSE -- no bridge, no tip, no drawn nostrils.
  T3  NO AGE MODELLING -- no brow furrows, no folds, no jowls.
  T7  NO PATCHWORK ON THE SKULL.
  T8  HEAD-TO-BODY >= 4.5 heads with lean limbs. k6a reads 5.51.
  P1  A BROW ABOVE THE LID WITH SKIN BETWEEN. A lash arc welded to the eye
      rim is NOT a brow -- that is what the wording rungs drew.
  P3  A MOUTH. A line, however thin. k5a had NONE and that is why it lost.
  C1  CONTAINMENT -- no purple cowl at the neck, no horns, no portrait
      composition. k6b/k6c/k6d put the cowl back at 47.3%/17.8%/39.2% and
      failed on it; k6a reads 0.0%.
  C2  THE POSE IS THE ONE ASKED FOR. A frame whose skeleton the net ignored is
      not the pose, however good the figure is.
A frame failing ANY clause is REJECTED. The whole reason the old 31-frame LoRA
set was untrainable is that near-misses were kept."""

ONE_SAMPLE = (
    "DISCHARGED BY THE THIRTEEN-RUNG LADDER, not waived. The recipe change under "
    "test here is NOT new: k1..k6d walked the reference route one variable at a "
    "time across thirteen samples (pipeline/work-ladder-0819.md; "
    "pipeline/lora/curation-tile-0820.yaml updates 4-8), and k6a is the rung the "
    "steward ruling names. What varies below is the POSE and the FRAMING, which "
    "no single sample could vary, and every frame is judged by eye against the "
    "tile before anything is promoted.")


def _selftest():
    import yaml
    bad = []

    def check(name, cond, detail=""):
        print("  %-52s %s%s" % (name, "ok" if cond else "FAIL",
                                "" if cond else "  " + detail))
        if not cond:
            bad.append(name)

    print("jerry_standard_0821 selftest")

    # 1. The wording and the mask reproduce k6a's payload byte-for-byte.
    spec = yaml.safe_load(open(os.path.join(REPO, PARENT), encoding="utf-8"))
    pay = spec["payload"]
    pk = [k for k in pay if k.endswith("prompt.txt")][0]
    nk = [k for k in pay if k.endswith("negative.txt")][0]
    check("prompt_for(POSE_STAND) == k6a's prompt.txt",
          prompt_for(POSE_STAND) == pay[pk],
          repr(prompt_for(POSE_STAND))[:80])
    check("NEGATIVE == k6a's negative.txt", NEGATIVE == pay[nk])
    check("mask_for('stand') == k6a's --ip-mask",
          mask_for("stand") == "%d,%d,%d,%d" % MASK_STAND, mask_for("stand"))

    # 2. Every argv value the standard names is the one k6a actually rendered.
    argv = [t for s in spec["steps"] for t in s.get("argv", [])]

    def after(flag):
        return argv[argv.index(flag) + 1] if flag in argv else None

    for flag, want in ((("--ip-scale"), IP_SCALE),
                       ("--ip-weight", IP_WEIGHT),
                       ("--ip-ref-sha256", IP_REF_SHA),
                       ("--ip-mask", "%d,%d,%d,%d" % MASK_STAND),
                       ("--scale", CONTROL_SCALE),
                       ("--arm", ARM),
                       ("--controlnet", CONTROLNET),
                       ("--seed", str(SEED))):
        check("k6a argv %s == %s" % (flag, want), after(flag) == want,
              repr(after(flag)))
    check("k6a argv --ip-ref names %s" % IP_REF,
          (after("--ip-ref") or "").endswith(IP_REF + ".png"),
          repr(after("--ip-ref")))
    check("k6a argv --control names the h19 skeleton",
          (after("--control") or "").endswith("jerry-skel-h19-0820.png"))
    check("k6a argv --control-sha256 == SKELETONS['jerry-skel-h19-0820']",
          after("--control-sha256") == SKELETONS["jerry-skel-h19-0820"][1])

    # 3. The reference REBUILDS to the pinned digest. This is the clause that
    #    makes the recipe runnable rather than merely recorded: if the builder
    #    or the tile ever changes, the standard fails here instead of silently
    #    conditioning the next hundred frames on a different face.
    import author_jerry_squareref_0821 as sq
    img = sq.build(IP_REF_HEAD_FRAC)
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    check("%s --head-frac %.2f rebuilds to the pinned sha"
          % (os.path.basename(REF_BUILDER), IP_REF_HEAD_FRAC),
          hashlib.sha256(buf.getvalue()).hexdigest() == IP_REF_SHA)
    on_disk = os.path.join(REPO, ASSET_DIR, IP_REF + ".png")
    check("%s/%s.png on disk matches the pinned sha" % (ASSET_DIR, IP_REF),
          os.path.exists(on_disk) and hashlib.sha256(
              open(on_disk, "rb").read()).hexdigest() == IP_REF_SHA)

    # 4. Every skeleton the standard offers is on disk with the sha it claims,
    #    and its pose arg is one author_jerry_skel_0820 actually builds.
    for stem, (pose, sha) in sorted(SKELETONS.items()):
        p = os.path.join(REPO, ASSET_DIR, stem + ".png")
        ok = os.path.exists(p) and hashlib.sha256(
            open(p, "rb").read()).hexdigest() == sha
        check("skeleton %s sha" % stem, ok)
        try:
            m = mask_for(pose)
            check("  mask_for(%r) inside the frame" % pose, bool(m), m)
        except Exception as exc:                    # noqa: BLE001
            check("  mask_for(%r)" % pose, False, str(exc))

    # 5. The span rule the mask rule rests on. If the head ever stops moving as
    #    a rigid block, translation is the wrong transform and this catches it.
    for stem, (pose, _) in sorted(SKELETONS.items()):
        kp, _m = skel.figure(HEAD_FRAC, pose=pose)
        span = kp["Lear"][0] - kp["Rear"][0]
        check("  ear span %.1f px in pose %r" % (span, pose),
              abs(span - EAR_SPAN_PX) < 0.5)

    # 6. The adapter allowlist carries the face weight AND its digest, and the
    #    two adapters are still the same length -- the reason the digest is the
    #    only discriminator.
    src = open(os.path.join(REPO, "pipeline", "controlnet_plate.py"),
               encoding="utf-8").read()
    check("controlnet_plate.py allowlists %s" % IP_WEIGHT, IP_WEIGHT in src)
    check("controlnet_plate.py carries the face digest", IP_WEIGHT_SHA in src)
    check("both adapters are still %d bytes in the allowlist" % IP_WEIGHT_BYTES,
          src.count(str(IP_WEIGHT_BYTES)) >= 2)
    check("driver on disk matches DRIVER_SHA",
          hashlib.sha256(open(os.path.join(REPO, "pipeline", DRIVER),
                              "rb").read()).hexdigest() == DRIVER_SHA)

    print("\n%s" % ("SELFTEST PASS" if not bad
                    else "SELFTEST FAIL: %d clause(s)\n  %s"
                    % (len(bad), "\n  ".join(bad))))
    return 1 if bad else 0


def _show():
    print(__doc__)
    print("THE STANDARD, AS VALUES")
    print("  parent rung      %s" % PARENT_ID)
    print("  positive         %s" % prompt_for(POSE_STAND))
    print("  negative         %s" % NEGATIVE)
    print("  seed             %d" % SEED)
    print("  controlnet       %s @ %s" % (CONTROLNET, CONTROL_SCALE))
    print("  head_frac        %.3f  (the tile's measured 5.2 heads)" % HEAD_FRAC)
    print("  ip weight        %s" % IP_WEIGHT)
    print("                   sha256 %s" % IP_WEIGHT_SHA)
    print("  ip reference     %s.png  (head %.0f%% of a 448 square, %.1f%% "
          "encoded)" % (IP_REF, IP_REF_HEAD_FRAC * 100, IP_REF_ENCODED_PCT))
    print("                   sha256 %s" % IP_REF_SHA)
    print("                   build: python3 %s --head-frac %.2f"
          % (REF_BUILDER, IP_REF_HEAD_FRAC))
    print("  ip scale         %s" % IP_SCALE)
    print("  mask (stand)     %s" % mask_for("stand"))
    print("\n  MASK BY POSE (k6a's mask translated by the head-block offset)")
    for stem, (pose, _sha) in sorted(SKELETONS.items()):
        print("    %-28s %-9s %s" % (stem, pose, mask_for(pose)))
    print("\n%s" % BAR)
    return 0


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv else _show())
