#!/usr/bin/env python3
r"""BEAT 07 ON THE POSE ROUTE: two drawn skeletons for the crossover problem.

    python3 pipeline/derive_b07_pose_0822.py --selftest
    python3 pipeline/derive_b07_pose_0822.py --write

BEAT 07 ALREADY HAS ITS BEST CLIP EVER AND THIS DOES NOT REPLACE IT. Tonight's
re-run put two figures in frame with the point landing on the goblin's cheek, and
it is staged as the beat's best available. Its two remaining faults are BOTH
CROSSOVER: the guard wears the goblin's mandarin collar and frog buttons, and he
has a POINTED EAR. Wardrobe adjectives are closed as a lever -- the re-run matched
the goblin's description density word for word and the shared-noun items still
duplicated -- and that commit named per-figure conditioning as the next rung.

WHAT CHANGED IN THE FOUR HOURS SINCE, AND IT IS WHY THIS IS WORTH A SAMPLE. The
pose route put TWO DIFFERENT MEN side by side in beat 05 -- one moustached, one
not -- from two drawn skeletons and words alone. Nothing in this tree had managed
a reliable two-figure frame before that. So there is now a mechanism that gives
the model a STRUCTURAL separation between two bodies before a single attribute
word is read, and beat 07's whole remaining problem is that it does not know
where one body ends and the other begins.

IT IS A TEST AND NOT A FIX, AND THE HONEST ODDS ARE MIXED. Beat 05's frame also
leaked the round glasses onto BOTH men while binding the moustache to one, so a
drawn separation is NOT known to stop attribute crossover -- that is precisely
the open question. Beat 07 is the cheapest place to ask it because it is the beat
where the crossover is MEASURED rather than suspected, and because the two bodies
here are different SPECIES, which is a much larger structural difference than two
men of similar build. If the separation is going to help anywhere, it helps here;
if it does not help here, the lever is per-figure conditioning and not geometry.

THE HINT. `pipeline/author_b07_twofig_pose_0822.py`: goblin at frame left, guard
at frame right -- the arrangement this beat has always used -- with the guard at
FIVE heads and the goblin at FOUR, which is not a child's proportion by accident
but the broad-domed creature the founder ratified. The point is solved so the
FOREARM aims: COCO-18 has no finger keypoint, so the elbow->wrist limb is the
last mark in the drawing and it has to be the thing that aims, with the wrist a
hand short of the cheek. Getting that wrong the first way -- putting the wrist
back on the shoulder->target ray -- left the forearm 17 px wide of the face, and
the selftest measured it before a GPU second was spent.

ONE NET. No board, no prop, no second hint, no reference image.

$0, ~3 GPU minutes, one seed, one frame.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

import derive_spec                                                  # noqa: E402
from derive_sapling_field_0821 import assert_under_clip77           # noqa: E402

BEAT = 7
NODE = "002b-first-citizen"
SPEC_ID = "ep2-b07-pose-0822"
WORK = r"C:\banyan-farm\ep2-b07-pose-0822"
DRIVER = "controlnet_plate.py"
AUTHOR = "author_b07_twofig_pose_0822.py"
ARM = "posebooth"
SEED = 20260726            # this beat, unused elsewhere
POSE_NET = "xinsir/controlnet-openpose-sdxl-1.0"
POSE_SCALE = "0.8"
POSE_HINT = "pipeline/hints/b07-twofig-pose-0822.png"
RAW_BASE = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"

POSITIVE = (
    "A tall grown guard man with dark cropped hair, round wire-rim glasses, a "
    "tan tunic and a white shoulder sash stands at frame right in tall grass "
    "in bright morning sunlight, pointing at a small green goblin at frame "
    "left with a broad bald dome, large pointed ears and small off-white "
    "almond eyes, cinematic lighting, masterpiece, best quality, very aesthetic")

NEGATIVE = (
    "photorealistic, 3d render, abstract, text, watermark, signature, low "
    "quality, blurry, extra limbs, deformed, jpeg artifacts, realistic skin "
    "texture, girl, child, helmet, armor, knight, third figure, crowd, white "
    "background, dark, night, photorealism")

BAR = (
    "ONE 832x1216 png. THIS BEAT IS ABOUT CROSSOVER AND THE BAR IS SCORED ON "
    "CROSSOVER FIRST. "
    "(1) THE GUARD IS HUMAN. No pointed ear, no green skin, no bald dome. "
    "Tonight's motion clip put a POINTED EAR on him and that is the measured "
    "defect this rung is aimed at. "
    "(2) THE GUARD'S KIT IS HIS OWN. A tan tunic and a WHITE SHOULDER SASH -- no "
    "mandarin collar and no frog closures, which are the goblin's and which "
    "arrived on the guard in every previous frame of this beat. "
    "(3) THE GOBLIN IS THE GOBLIN: broad bald dome, large pointed ears, small "
    "off-white almond eyes. He does not acquire the glasses, the hair or the "
    "sash. THE GLASSES ARE THE ONE TO WATCH -- beat 05's pose frame bound a "
    "moustache to one man and spread the glasses across both. "
    "(4) TWO FIGURES, one of each. One is a DROP and three is a DROP. "
    "(5) THE POINT LANDS: the guard's arm extends left and his hand ends at the "
    "goblin's face, not his belly and not the air. "
    "(6) THEY ARE THE RIGHT SIZES -- the guard is a five-head adult and the "
    "goblin is short with a large dome, which the hint asserts. "
    "(7) DAYLIGHT in a real grass field, and DETAILED CINEMATIC ANIME. "
    "PRE-REGISTERED FAIL MODES, most likely first: CROSSOVER SURVIVING THE "
    "SEPARATION -- the glasses or the collar on both, which would say a drawn "
    "structural split is not enough and the lever is per-figure conditioning "
    "(--ip-ref twice with --ip-mask-capsules, which the b08 lane already wired "
    "and whose capsules can be built from this same skeleton). THE SPECIES "
    "MERGING, a green guard or a human goblin, which is worse than crossover and "
    "would retire this hint. The POINT missing, which the selftest has already "
    "measured to 0.0 px in the drawing, so a miss in the render is the net and "
    "not the geometry. And a THIRD figure, which this beat has produced before.")


def sha_of(rel):
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def out_png():
    return "%s-%s.png" % (SPEC_ID, ARM)


def _stage_step():
    """Fetch the driver AND both hints, each checked against its own sha.

    The hints are committed files rather than generated on the box on purpose:
    the box would need PIL, the author module and both of its imports, and a
    hint generated at run time is a hint nobody looked at. These two were
    rendered here, opened, and are in the tree.
    """
    body = (
        "import hashlib, os, urllib.request\n"
        "base = \"%(base)s\"\n"
        "root = r\"%(work)s\"\n"
        "want = [\n"
        "    (\"pipeline/%(drv)s\", os.path.join(root, \"src\", \"pipeline\"),\n"
        "     \"%(drvsha)s\"),\n"
        "    (\"%(pose)s\", root, \"%(posesha)s\"),\n"
        "]\n"
        "for path, dst, sha in want:\n"
        "    os.makedirs(dst, exist_ok=True)\n"
        "    with urllib.request.urlopen(base + path, timeout=120) as r:\n"
        "        blob = r.read()\n"
        "    got = hashlib.sha256(blob).hexdigest()\n"
        "    if got != sha:\n"
        "        raise SystemExit(\"!! %%s sha %%s, wanted %%s\" %% (path, got, sha))\n"
        "    name = path.rsplit(\"/\", 1)[-1]\n"
        "    with open(os.path.join(dst, name), \"wb\") as fh:\n"
        "        fh.write(blob)\n"
        "    print(\"staged\", name, got[:12])\n"
    ) % {"base": RAW_BASE, "work": WORK, "drv": DRIVER,
         "drvsha": sha_of("pipeline/" + DRIVER),
         "pose": POSE_HINT, "posesha": sha_of(POSE_HINT),
         }
    return {"name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def _plate_argv():
    return [
        r"C:\banyan-farm\venv\Scripts\python.exe",
        WORK + "\\src\\pipeline\\" + DRIVER,
        "--root", WORK + r"\src",
        "--task", SPEC_ID,
        "--arm", ARM,
        "--controlnet", POSE_NET,
        "--control", WORK + "\\" + POSE_HINT.rsplit("/", 1)[-1],
        "--control-sha256", sha_of(POSE_HINT),
        "--scale", POSE_SCALE,
        "--seed", str(SEED),
        "--steps", "40",
        "--cfg", "7.5",
        "--width", "832",
        "--height", "1216",
        "--prompt-file", WORK + r"\prompt.txt",
        "--negative-file", WORK + r"\negative.txt",
        "--out", WORK + r"\out",
    ]


def _publish_step():
    body = (
        "# The courier pushes from farm-out and from nowhere else. The two HINTS\n"
        "# travel with the frame as well as the prompt: a conditioned plate whose\n"
        "# condition is not beside it cannot be re-read later.\n"
        "import glob, hashlib, os, shutil\n"
        "dst = \"C:/banyan-farm/courier-box/farm-out/%(jid)s\"\n"
        "os.makedirs(dst, exist_ok=True)\n"
        "files = sorted(glob.glob(\"%(work)s/out/%(png)s*\")\n"
        "               + glob.glob(\"%(work)s/prompt.txt\")\n"
        "               + glob.glob(\"%(work)s/negative.txt\")\n"
        "               + glob.glob(\"%(work)s/%(pose)s\"))\n"
        "lines = []\n"
        "for f in files:\n"
        "    shutil.copy2(f, dst)\n"
        "    c = os.path.join(dst, os.path.basename(f))\n"
        "    with open(c, \"rb\") as fh:\n"
        "        lines.append(hashlib.sha256(fh.read()).hexdigest() + \"  \"\n"
        "                     + os.path.basename(f))\n"
        "with open(os.path.join(dst, \"%(jid)s.sha256\"), \"w\", newline=\"\\n\") as fh:\n"
        "    fh.write(\"\\n\".join(sorted(lines)) + \"\\n\")\n"
        "print(\"published\", len(files), \"file(s) + manifest ->\", dst)\n"
        "raise SystemExit(0 if len(files) >= 4 else 1)\n"
    ) % {"jid": SPEC_ID, "work": WORK.replace("\\", "/"), "png": out_png(),
         "pose": POSE_HINT.rsplit("/", 1)[-1],
         }
    return {"name": "publish",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", body]}


def build():
    return {
        "id": SPEC_ID,
        "task": SPEC_ID,
        "node": NODE,
        "beat": BEAT,
        "runner": "box",
        "priority": 6,
        "needs_gpu": True,
        "max_attempts": 1,
        "sample": True,
        "est_minutes": 3,
        "needs": ["cuda", "vram20", "sdxl-venv"],
        "owner": ("night iteration lane, 2026-08-22 -- beat 06 on the pose route, "
                  "filed after the adapter route closed on four measurements"),
        "consumer": (
            "BEAT 07's SLOT, and the crossover question that is now open across "
            "the whole episode. This beat has its best clip ever staged tonight "
            "and NOTHING HERE REPLACES IT -- what this frame buys, if it works, "
            "is a plate whose two bodies are structurally separate, which is the "
            "only untried lever on the two faults that clip still carries. If it "
            "fails it fails informatively: it says a drawn split does not stop "
            "attribute crossover, and the next instrument is per-figure "
            "conditioning rather than more geometry."),
        "success": BAR,
        "why": (
            "THE ADAPTER ROUTE IS CLOSED BY MEASUREMENT. window4 and content on "
            "beats 05 and 06 -- opposite settings on both axes the sampler has -- "
            "all four returned the reference photograph's crop and pose: a "
            "head-and-shoulders close-up with the hands up at the face, no board, "
            "no field. So this rung takes the PICTURE from a drawing and the MAN "
            "from the words, with no reference image anywhere in the job. Two "
            "nets, because a COCO-18 hint has no keypoint for a plank and the "
            "board is this beat's entire fault: openpose for the five-head figure "
            "and scribble for one rectangle exactly as wide as the skeleton's "
            "shoulders. The scribble net's known defect -- it traces whatever it "
            "can read -- is the feature here, because the thing being traced is a "
            "board and boards are rectangles. Both hints come out of one file and "
            "one geometry, so the prompt's `as wide as his shoulders` and the "
            "drawing's width are the same number. $0, ~3 GPU minutes. Full trace: "
            "pipeline/derive_b06_pose_0822.py and pipeline/%s." % AUTHOR),
        "script_authority": (
            "Node 002b-first-citizen, live script `002b-t0-c`, `approved_by: "
            "founder`, `approved_on: 2026-08-03`. A STILL PLATE on an approved "
            "node: no voice, no motion, no episode assembly, no publication, and "
            "review/ep2-ship-0821 is not touched."),
        "script_line": ("Beat 07 CONFISCATE: the guard points at the scavenger. "
                        "Drawn here as a still two-figure plate, because the "
                        "beat's remaining faults are which body owns which "
                        "attribute and not the movement."),
        "env": {
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1",
            "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "payload": {
            WORK + r"\prompt.txt": POSITIVE,
            WORK + r"\negative.txt": NEGATIVE,
        },
        "steps": [_stage_step(),
                  {"name": "plate", "argv": _plate_argv()},
                  _publish_step()],
        "recipe_trace": (
            "driver pipeline/%s sha %s, fetched and sha-checked at run time. ONE "
            "net: %s at %s. Hint %s sha %s, two COCO-18 skeletons authored in PIL "
            "by pipeline/%s with no annotator and no controlnet_aux dependency, "
            "which keeps this route clear of lllyasviel/Annotators and its "
            "inherited CMU OpenPose non-commercial terms. Prompt and negative are "
            "baked into this spec's payload. NO IP-ADAPTER AND NO REFERENCE IMAGE. "
            "Sibling: pipeline/jobs/ep2-b06-pose-0822.yaml, the frame that proved "
            "the framing half of this route."
            % (DRIVER, sha_of("pipeline/" + DRIVER)[:16], POSE_NET, POSE_SCALE,
               POSE_HINT, sha_of(POSE_HINT)[:16], AUTHOR)),
        "one_sample_rule": (
            "ONE FRAME, ONE SEED. The route itself was sampled on beats 06 and "
            "05 before this was written, and what carries here is only the part "
            "that WORKED: a drawn skeleton places figures at chosen sizes in a "
            "chosen frame, and the light belongs in the positive. What is NOT "
            "carried is beat 06's second net -- that ladder closed at three rungs "
            "tonight with the rectangle being drawn as a lit panel -- and there is "
            "no prop in this staging anyway."),
        "chosen_not_measured": (
            "ONE CONDITIONING SCALE, 0.8, carried unchanged from the two pose "
            "frames where it bound the figures precisely. The two statures and "
            "the head fractions are choices: five heads for the guard is the "
            "canon adult, four for the goblin is his ratified big-dome build, and "
            "both are asserted in the hint's selftest so a later edit cannot "
            "drift them."),
        "seed_note": (
            "Seed %d, held from the two adapter runs on this beat deliberately. "
            "The three frames are then a clean triple and the differences between "
            "them are the conditioning route and nothing else." % SEED),
        "artifacts": [WORK + r"\out" + "\\" + out_png()],
    }


def _selftest():
    spec = build()
    npos = assert_under_clip77("b06 pose positive", POSITIVE)
    nneg = assert_under_clip77("b06 pose negative", NEGATIVE)
    argv = spec["steps"][1]["argv"]

    def flag(name):
        return argv[argv.index(name) + 1]

    assert flag("--controlnet") == POSE_NET
    assert flag("--scale") == POSE_SCALE
    # ONE NET. Beat 06 composes a scribble net because its fault IS an object;
    # this staging has no prop, so a second hint would be an unmeasured knob
    # bought for nothing.
    assert "--controlnet2" not in argv and "--scale2" not in argv
    # NO REFERENCE ANYWHERE. That is the whole point of this rung, and a stray
    # --ip-ref would quietly restore the route that four runs just closed.
    assert "--ip-ref" not in argv and "--ip-scale" not in argv
    # `nocontrol` is the literal string that DISABLES the ControlNet branch in
    # this driver. Passing it here would drop both nets and render a bare t2i
    # that looked like a result.
    assert flag("--arm") != "nocontrol", "nocontrol would disable both nets"
    assert flag("--seed") == str(SEED)
    # The hint bytes are asserted on the box, not just staged there.
    assert flag("--control-sha256") == sha_of(POSE_HINT)
    # THE HINT AND THE PROMPT MUST AGREE. The prompt puts the goblin at frame
    # LEFT and the guard at frame RIGHT; the drawing must do the same, or the
    # plate is being asked for an arrangement the hint contradicts.
    sys.path.insert(0, os.path.join(REPO, "pipeline"))
    import author_b07_twofig_pose_0822 as author
    gob, gua, target = author.keypoints()
    assert author.GOBLIN_X < author.GUARD_X
    assert "at frame right" in POSITIVE and "at frame left" in POSITIVE
    assert author.GUARD_STATURE > author.GOBLIN_STATURE
    assert abs(1.0 / author.GUARD_HEAD_FRAC - 5.0) < 0.01, "guard is five heads"
    assert abs(1.0 / author.GOBLIN_HEAD_FRAC - 4.0) < 0.01, "goblin is four heads"
    # The light is ASSERTED, not banned -- the correction beat 06's night frame
    # earned three hours ago.
    assert "bright morning sunlight" in POSITIVE
    # Both characters' identifying features, and the guard's OWN kit. The whole
    # question is which body gets which of these.
    assert "dark cropped hair" in POSITIVE and "round wire-rim glasses" in POSITIVE
    assert "tan tunic" in POSITIVE and "white shoulder sash" in POSITIVE
    assert "broad bald dome" in POSITIVE and "off-white almond eyes" in POSITIVE
    # THE GOBLIN'S OWN COLLAR IS NOT BANNED. `mandarin collar` in the negative
    # would delete the goblin's canon garment to fix the guard's, and tonight's
    # b07 re-run measured that banning it does not move it anyway.
    assert "mandarin collar" not in NEGATIVE
    # Figure-count containment.
    assert "third figure" in NEGATIVE and "crowd" in NEGATIVE
    # THIS DOES NOT REPLACE THE STAGED CLIP and the consumer has to keep saying
    # so, or a later reader takes a still plate for a cut decision.
    assert "NOTHING HERE REPLACES IT" in spec["consumer"]
    # The hints on disk must BE the ones the author produces, or the sha in the
    # spec is asserting bytes nobody drew.
    assert sha_of(POSE_HINT) == hashlib.sha256(
        _png_bytes(author.render())).hexdigest(), "pose hint on disk is stale"
    assert spec["artifacts"] == [WORK + r"\out" + "\\" + out_png()]
    print("SELFTEST OK  %s  pos=%d neg=%d  seed=%d  pose=%s (one net, no board)"
          % (SPEC_ID, npos, nneg, SEED, sha_of(POSE_HINT)[:12]))
    return 0


def _png_bytes(img):
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    _selftest()
    if not a.write:
        print("dry run -- nothing written. Pass --write.")
        return 0
    p = derive_spec.write(build(), "pipeline/jobs/%s.yaml" % SPEC_ID,
                          force=a.force)
    print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
