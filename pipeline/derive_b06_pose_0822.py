#!/usr/bin/env python3
r"""BEAT 06 ON THE POSE ROUTE: a drawn skeleton, a drawn board, no reference.

    python3 pipeline/derive_b06_pose_0822.py --selftest
    python3 pipeline/derive_b06_pose_0822.py --write

WHAT CLOSED THE PREVIOUS ROUTE, MEASURED TONIGHT AND NOT ARGUED. Beat 06 was
drawn twice on the IP-Adapter stack: `window4` (adapter on every block, first
15% of the denoise) and `content` (adapter on one block, all 40 steps). Those
are opposite settings on both axes the sampler exposes and they returned the
same frame -- a head-and-shoulders close-up of the ratified guard with his hands
clasped at his chest, no bark board, no field. Beat 05 did the same thing twice
over, merging its two men into one face. So a tight-crop reference dictates the
crop AND the pose, and neither the timing nor the layer scope of the adapter
changes it. Four runs, twelve GPU minutes, and the route is closed rather than
under-tuned.

THIS RUNG TAKES THE PICTURE FROM A DRAWING AND THE MAN FROM THE WORDS. There is
no reference image anywhere in this job. The identity half is the part the words
are measured to carry: the guardcast2d sheet drew ten grown men out of ten with
no reference at all, and `dark cropped hair` and `round wire-rim glasses` have
bound in every cell they have appeared in. What words have never been able to do
is put a figure at a chosen size in a chosen frame holding a chosen object, and
that is what a hint is for.

TWO NETS, AND THE SECOND ONE IS NOT OPTIONAL. controlnet_plate.py says it on its
own `--controlnet2` flag: "a pose hint cannot carry an object, because COCO-18's
eighteen keypoints are all body parts." Beat 06's entire standing fault IS the
object -- "the bark board is the wrong size" -- so a rung that cannot draw a
board answers nothing.

  net 1  xinsir/controlnet-openpose-sdxl-1.0   the man, 5 heads tall, centred,
                                               both wrists in front of his
                                               sternum
  net 2  xinsir/controlnet-scribble-sdxl-1.0   the board, one white rectangle
                                               outline exactly as wide as the
                                               skeleton's shoulders

THE SCRIBBLE NET'S KNOWN DEFECT IS THIS RUNG'S FEATURE. `b08-arm-route-0819.md`
§10 closed a four-rung ladder on the finding that "any hint this net can read is
a hint it TRACES". On beat 08 that was fatal: a traced human outline is a
costume card and not a person. Here the hint is a rectangle and the wanted
output is a rectangular slab, so a net that draws exactly the shape it is given
is the correct instrument -- and the board's SIZE, which is the beat's fault and
which no wording round has ever controlled, becomes a number authored in PIL and
asserted in a selftest.

BOTH HINTS COME OUT OF ONE FILE AND ONE GEOMETRY.
`pipeline/author_b06_guard_pose_0822.py` derives the board's width from the
skeleton's own shoulder keypoints, so the hint cannot disagree with the prompt
clause "as wide as his shoulders" -- they are the same number. Its selftest
asserts that, asserts the five-head proportion arithmetically, and asserts the
xinsir thick-line ratio, which is a documented way to get a hint ignored.

WHAT IS CHOSEN AND NOT MEASURED, said plainly because two knobs are being set at
once and neither has a number behind it on THIS beat: the conditioning scales,
0.8 for the pose and 0.5 for the board. Beat 08's composition ran 1.0/0.6. The
board is set lower on purpose -- a hard-traced rectangle would be a white box
floating in a field, and what is wanted is a slab-shaped object in his hands. If
the sample comes back with a literal outlined rectangle, the scale is the first
thing to drop; if the board is absent, it is the first thing to raise. That is
the sweep this sample is here to aim, and it is not run blind first.

FIVE HEADS IS THE OTHER HALF OF THE NIGHT ORDER, arriving now that the route
that could not use it is closed. head_frac 0.20 is an adult; the proportion this
tree keeps drawing by accident is nearer 0.25.

$0, local card, ~2 GPU minutes, one seed, one frame.
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

BEAT = 6
NODE = "002b-first-citizen"
SPEC_ID = "ep2-b06-pose-0822"
WORK = r"C:\banyan-farm\ep2-b06-pose-0822"
DRIVER = "controlnet_plate.py"
AUTHOR = "author_b06_guard_pose_0822.py"
ARM = "posebooth"
SEED = 20260725            # held from the two adapter runs, so the frames pair
POSE_NET = "xinsir/controlnet-openpose-sdxl-1.0"
BOARD_NET = "xinsir/controlnet-scribble-sdxl-1.0"
POSE_SCALE = "0.8"
BOARD_SCALE = "0.5"
POSE_HINT = "pipeline/hints/b06-guard-pose-0822.png"
BOARD_HINT = "pipeline/hints/b06-board-0822.png"
RAW_BASE = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"

POSITIVE = (
    "A grown guard man with dark cropped hair and round wire-rim glasses, "
    "cream shirt collar and white shoulder sash, in tall grass with a hedgerow "
    "behind, holding a large flat slab of rough brown bark in both hands at "
    "chest height, as wide as his shoulders, looking down at it, cinematic "
    "lighting, masterpiece, best quality, very aesthetic")

NEGATIVE = (
    "photorealistic, 3d render, abstract, text, watermark, signature, low "
    "quality, blurry, extra limbs, deformed, jpeg artifacts, realistic skin "
    "texture, girl, child, goblin, green skin, pointed ears, armor, helmet, "
    "metal clip, spring clip, white paper, small board, white background, "
    "dark, night, photorealism")

BAR = (
    "ONE 832x1216 png, judged at 1:1 and on a matched-scale sheet beside "
    "taste/refs/guard1-canon-founder-0822.png. PRE-REGISTERED: "
    "(1) A WHOLE FIGURE IN A FIELD, not a portrait. Two adapter runs returned a "
    "head-and-shoulders close-up and this rung exists to fix that, so a close-up "
    "here is a FAIL whatever the face looks like. "
    "(2) HE IS HOLDING A BOARD, in both hands, at chest height, looking down at "
    "it -- and the board is AT LEAST AS WIDE AS HIS SHOULDERS. This is the beat's "
    "standing fault and no previous frame of it has ever been right. "
    "(3) IT IS BARK, not a clipboard: no metal clip, no spring clip, no paper. "
    "(4) A GROWN MAN, five heads tall. A child or teenager read is a DROP -- the "
    "hint asserts the proportion, so if the output is still childlike the hint is "
    "not binding and that is the finding. "
    "(5) HE IS RECOGNISABLY GUARD 1: dark cropped hair, round wire-rim glasses. "
    "This is the half being taken from WORDS instead of from a reference, so it "
    "is the half that could newly fail, and a miss here is the interesting result "
    "rather than a disappointment. "
    "(6) DETAILED CINEMATIC ANIME. Flat or tag-sheet fails. "
    "(7) Cream shirt collar and WHITE SHOULDER SASH. "
    "(8) NOTHING GOBLIN: no green skin, no pointed ears. Tonight's b07 re-run put "
    "a pointed ear on this same guard. "
    "PRE-REGISTERED FAIL MODES, with what each one would mean: A LITERAL WHITE "
    "OUTLINED RECTANGLE floating in frame -- the scribble net traced the hint "
    "instead of interpreting it, and the answer is to drop --scale2 below 0.5, "
    "not to redraw the board. NO BOARD AT ALL -- 0.5 is too weak, raise it. A "
    "SKELETON DRAWN INTO THE PICTURE as glowing limbs, which is what the scribble "
    "net did to a medial-axis hint on beat 08; if the POSE net does it too, the "
    "hint class is wrong and not just the scale. THE FIGURE IGNORING THE HINT "
    "entirely, which at ratio 3.0 line thickness would be a real surprise and "
    "would point at the net not loading rather than at the drawing.")


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
        "    (\"%(board)s\", root, \"%(boardsha)s\"),\n"
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
         "board": BOARD_HINT, "boardsha": sha_of(BOARD_HINT)}
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
        "--controlnet2", BOARD_NET,
        "--control2", WORK + "\\" + BOARD_HINT.rsplit("/", 1)[-1],
        "--control2-sha256", sha_of(BOARD_HINT),
        "--scale2", BOARD_SCALE,
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
        "               + glob.glob(\"%(work)s/%(pose)s\")\n"
        "               + glob.glob(\"%(work)s/%(board)s\"))\n"
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
        "raise SystemExit(0 if len(files) >= 5 else 1)\n"
    ) % {"jid": SPEC_ID, "work": WORK.replace("\\", "/"), "png": out_png(),
         "pose": POSE_HINT.rsplit("/", 1)[-1],
         "board": BOARD_HINT.rsplit("/", 1)[-1]}
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
            "BEAT 06's SLOT IN /review/ep2-beats-0821. The beat has two named "
            "faults, zero clips, and as of tonight two failed plates. If this "
            "frame passes it is the beat's first usable init and the motion rung "
            "that answers the frozen-frame fault can finally be filed. If it "
            "fails, it fails with a NUMBER attached -- the board's width is "
            "authored in pixels -- so the next move is a scale change and not "
            "another wording."),
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
        "script_line": ("Beat 06 THE CLIPBOARD: the guard turns the bark board "
                        "over and reads it. Drawn here holding it at chest height "
                        "in a field, because the board's size is the fault and a "
                        "close-up cannot show a size."),
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
            "driver pipeline/%s sha %s, fetched and sha-checked at run time. "
            "Nets: %s at %s (the figure) composed with %s at %s (the board), as a "
            "MultiControlNetModel, both on the driver's own licence allowlist. "
            "Hints %s sha %s and %s sha %s, authored in PIL by pipeline/%s with "
            "no annotator and no controlnet_aux dependency -- which is what keeps "
            "this route clear of lllyasviel/Annotators and its inherited CMU "
            "OpenPose non-commercial terms. Prompt and negative are baked into "
            "this spec's payload, so no drafts file can drift between filing and "
            "firing. NO IP-ADAPTER AND NO REFERENCE IMAGE."
            % (DRIVER, sha_of("pipeline/" + DRIVER)[:16], POSE_NET, POSE_SCALE,
               BOARD_NET, BOARD_SCALE, POSE_HINT, sha_of(POSE_HINT)[:16],
               BOARD_HINT, sha_of(BOARD_HINT)[:16], AUTHOR)),
        "one_sample_rule": (
            "ONE FRAME, ONE SEED, AND THE b05 SIBLING IS HELD. This is a new "
            "route -- a net that has never been used on this beat family, a "
            "second net composed with it, and two conditioning scales chosen "
            "rather than measured. Beat 05 needs exactly the same treatment with "
            "two skeletons and no board, and it is NOT filed until this frame has "
            "been looked at. That is the rule this repo wrote after fifteen beats "
            "were rendered on an unlooked-at recipe."),
        "chosen_not_measured": (
            "THE TWO CONDITIONING SCALES. 0.8 for the pose and 0.5 for the board, "
            "against beat 08's 1.0/0.6 composition. The board is deliberately the "
            "weaker of the two: a hard-traced rectangle would be a white box in a "
            "field, and what is wanted is a slab-shaped object in his hands. "
            "Neither number has a measurement behind it ON THIS BEAT and the bar "
            "says which way to move each one for each failure, so the sample aims "
            "the sweep instead of being the first step of one."),
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
    assert flag("--controlnet2") == BOARD_NET
    assert flag("--scale") == POSE_SCALE and flag("--scale2") == BOARD_SCALE
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
    assert flag("--control2-sha256") == sha_of(BOARD_HINT)
    # The prompt's size clause and the drawing's width are the SAME NUMBER, and
    # this is the assertion that keeps them that way across an edit to either.
    sys.path.insert(0, os.path.join(REPO, "pipeline"))
    import author_b06_guard_pose_0822 as author
    kps = author.keypoints()
    x0, _, x1, _ = author.board_box()
    sho = abs(kps["Lsho"][0] - kps["Rsho"][0])
    assert abs((x1 - x0) - sho) < 1.0, (x1 - x0, sho)
    assert "as wide as his shoulders" in POSITIVE
    assert abs(author.STATURE / (author.HEAD_FRAC * author.STATURE) - 5.0) < 0.01
    # The hints on disk must BE the ones the author produces, or the sha in the
    # spec is asserting bytes nobody drew.
    assert sha_of(POSE_HINT) == hashlib.sha256(
        _png_bytes(author.render())).hexdigest(), "pose hint on disk is stale"
    assert sha_of(BOARD_HINT) == hashlib.sha256(
        _png_bytes(author.render_board())).hexdigest(), "board hint is stale"
    assert spec["artifacts"] == [WORK + r"\out" + "\\" + out_png()]
    print("SELFTEST OK  %s  pos=%d neg=%d  seed=%d  pose=%s board=%s"
          % (SPEC_ID, npos, nneg, SEED, sha_of(POSE_HINT)[:12],
             sha_of(BOARD_HINT)[:12]))
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
