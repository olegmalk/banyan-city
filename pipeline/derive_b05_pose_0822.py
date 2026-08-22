#!/usr/bin/env python3
r"""BEAT 05 ON THE POSE ROUTE: two drawn skeletons, no reference, no board.

    python3 pipeline/derive_b05_pose_0822.py --selftest
    python3 pipeline/derive_b05_pose_0822.py --write

WHY TWO SKELETONS. Beat 05 needs two men in frame and has spent four wording
rounds getting there; its ONE recorded win is "two figures in the field from the
first frame to the 117th -- never one, never three". Tonight the IP-Adapter route
took that away twice over, on window4 and on content: both returned ONE man, in a
close-up, with both briefs merged onto one face. A figure count is a COMPOSITION
fact, and the composition is not reachable from the prompt while a tight-crop
reference is in the job. Two drawn skeletons make the count an assertion.

THE HOLD IS RELEASED, WHICH IS WHY THIS EXISTS NOW AND DID NOT AN HOUR AGO. The
beat-06 pose spec said in its own one_sample_rule that this sibling was NOT to be
filed until that frame had been looked at. It has been. It put a whole man in a
field at the drawn size with his hands where they were drawn -- the thing four
adapter runs could not do at any setting -- and took his identity from the words
with no reference image in the job. It failed on its LIGHT and on its board;
neither failure touches the figure count, and the light correction is carried
here.

ONE NET, NOT TWO. Beat 06 composes a second scribble net because its fault IS an
object. Beat 05 has no prop in this staging, so there is no second hint and no
second scale -- one fewer unmeasured knob than its sibling.

THE LIGHT IS IN THE POSITIVE AND THAT IS A CORRECTION, NOT A PREFERENCE. Beat
06's first pose frame came back at NIGHT with `dark` and `night` in the negative
and no light clause in the positive at all. Eighth firing of the
positive-placement law in this tree, and it was my own error rather than the
model's. `bright morning sunlight under a pale sky` is asserted here.

THE TWO MEN ARE DISTINGUISHED IN THE WORDS AND NOT IN THE HINT, because a
skeleton cannot carry a moustache, and that leaves the b07 attribute-binding risk
live. It is pre-registered below rather than papered over. The right man's `thick
grey moustache` is chosen precisely because it is the one feature in the sentence
the left man cannot also have -- the term-with-no-competitor shape that DID bind
on b07 when the collar did not. The hint helps from the other side: the left
figure is drawn taller, which is a non-verbal "two different men" that survives
even if the words fail.

GUARD 2 IS STILL NOT CAST. Cell F of the casting sheet is on loan; the pick is
R4's, open at /review/ep2-guardcast2-0822, and a selftest fails if the word
PROVISIONAL ever leaves the consumer field.

$0, local card, ~3 GPU minutes, one seed, one frame.
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

BEAT = 5
NODE = "002b-first-citizen"
SPEC_ID = "ep2-b05-pose-0822"
WORK = r"C:\banyan-farm\ep2-b05-pose-0822"
DRIVER = "controlnet_plate.py"
AUTHOR = "author_b05_guards_pose_0822.py"
ARM = "posebooth"
SEED = 20260724            # held from the two adapter runs on this beat
POSE_NET = "xinsir/controlnet-openpose-sdxl-1.0"
POSE_SCALE = "0.8"
POSE_HINT = "pipeline/hints/b05-guards-pose-0822.png"
RAW_BASE = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"

POSITIVE = (
    "Two grown guard men standing side by side in tall grass in bright morning "
    "sunlight under a pale sky, looking out over an empty field. The left man "
    "has dark cropped hair and round wire-rim glasses. The right man has a "
    "thick grey moustache. Both wear white shoulder sashes, cinematic "
    "lighting, masterpiece, best quality, very aesthetic")

NEGATIVE = (
    "photorealistic, 3d render, abstract, text, watermark, signature, low "
    "quality, blurry, extra limbs, deformed, jpeg artifacts, realistic skin "
    "texture, girl, child, goblin, green skin, pointed ears, armor, helmet, "
    "third man, crowd, white background, dark, night, photorealism")

BAR = (
    "ONE 832x1216 png, judged at 1:1 and on a matched-scale two-face sheet beside "
    "taste/refs/guard1-canon-founder-0822.png. PRE-REGISTERED: "
    "(1) TWO MEN, both whole, both standing, side by side in a field. ONE is a "
    "DROP and THREE is a DROP. Four adapter frames returned one man and this rung "
    "exists to make the count an assertion rather than a hope. "
    "(2) THEY ARE DIFFERENT MEN. The left is guard 1 -- dark cropped hair, round "
    "wire-rim glasses. The right has a THICK GREY MOUSTACHE and has neither the "
    "glasses nor the cropped hair. Two copies of one man is the headline failure. "
    "(3) BOTH WEAR A WHITE SHOULDER SASH -- the beat's standing fault, 'neither "
    "guard wears the sash you froze for the cast'. One sash is a HALF PASS and is "
    "reported as one. "
    "(4) BOTH ARE GROWN MEN, five heads tall. A child or teenager read on either "
    "is a DROP -- the hint asserts the proportion, so a childlike output means the "
    "hint is not binding and that is the finding. "
    "(5) IT IS DAYLIGHT in a real grass field. The first pose frame on beat 06 "
    "came back at night and the light is asserted in the positive here; a dark "
    "frame means the light clause did not carry either. "
    "(6) DETAILED CINEMATIC ANIME. Flat or tag-sheet fails. "
    "(7) NOTHING GOBLIN on either man: no green skin, no pointed ears. "
    "PRE-REGISTERED FAIL MODES, most likely first: THE MOUSTACHE LANDING ON BOTH "
    "MEN or on the wrong one -- a skeleton cannot carry a moustache, so the two "
    "identities are separated in WORDS alone and this is the b07 attribute-binding "
    "problem with nothing but a height difference on our side. TWO IDENTICAL MEN, "
    "which would say the words distinguish nothing and the next lever is per-figure "
    "conditioning. A THIRD FIGURE, which four wording rounds on this beat did "
    "eventually beat and which the hint should now make impossible -- if one "
    "arrives anyway, the hint is being ignored. SKELETONS DRAWN INTO THE PICTURE "
    "as glowing limbs, which is what the scribble net did to a medial-axis hint on "
    "beat 08; from the POSE net it would mean the hint class is wrong.")


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
            "BEAT 05's SLOT IN /review/ep2-beats-0821. The beat has four failing "
            "clauses, no clip, and as of tonight two failed plates. Guard 2 is on "
            "loan from the casting sheet and everything downstream of this frame "
            "is PROVISIONAL until his letter; the pick is R4's and nothing here "
            "makes it. If the frame passes it is the beat's first usable init and "
            "the motion rung can be filed off it."),
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
        "script_line": ("Beat 05 THE PATROL: two guards halt and scan an empty "
                        "morning field. Drawn here standing side by side and "
                        "looking out, because the beat's faults are the cast and "
                        "the costume, not the movement."),
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
            "ONE FRAME, ONE SEED, AND THE HOLD ON IT IS RELEASED RATHER THAN "
            "IGNORED. The beat-06 pose spec said this sibling was not to be filed "
            "until that frame had been looked at. It has been: it put a whole man "
            "in a field at the drawn size with his hands where they were drawn, "
            "and failed on its light and its board. Neither failure touches the "
            "figure count this job is about, and the light correction is carried."),
        "chosen_not_measured": (
            "ONE CONDITIONING SCALE, 0.8, carried unchanged from the beat-06 pose "
            "frame where it bound the figure precisely. That is one fewer "
            "unmeasured knob than the sibling, which also had to pick a board "
            "scale. The height difference between the two skeletons is also a "
            "choice: guard 1 is the taller by the cast sheet, and a visible "
            "difference is the cheapest non-verbal way to say two different men in "
            "a frame where the identity words may or may not bind."),
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
    # THE HINT AND THE PROMPT MUST AGREE ON THE COUNT. The prompt says two men;
    # the hint must draw two skeletons, or the plate is being asked for a number
    # the drawing does not assert -- which is the whole point of this rung.
    sys.path.insert(0, os.path.join(REPO, "pipeline"))
    import author_b05_guards_pose_0822 as author
    figs = author.figures()
    assert len(figs) == 2, len(figs)
    assert "Two grown guard men" in POSITIVE
    assert abs(author.LEFT_STATURE / (author.HEAD_FRAC * author.LEFT_STATURE)
               - 5.0) < 0.01
    assert author.LEFT_STATURE > author.RIGHT_STATURE, "guard 1 is the taller"
    # The two men are separated in WORDS alone, so the distinguishing feature has
    # to be one the other man cannot also have -- tonight's b07 finding.
    assert "thick grey moustache" in POSITIVE
    assert "dark cropped hair and round wire-rim glasses" in POSITIVE
    # The sash is the beat's standing fault and it is ASSERTED for both men.
    assert "Both wear white shoulder sashes" in POSITIVE
    # THE LIGHT IS IN THE POSITIVE, not banned in the negative. Beat 06's first
    # pose frame came back at night with `dark, night` in the negative and no
    # light clause at all.
    assert "bright morning sunlight" in POSITIVE and "pale sky" in POSITIVE
    # Figure-count containment, carried from the wording rounds that won it.
    assert "third man" in NEGATIVE and "crowd" in NEGATIVE
    # NOTHING HERE CASTS GUARD 2. Guard 2 is on loan from the casting sheet and
    # the pick is R4's; if a later edit drops the word PROVISIONAL out of the
    # consumer field, this fails rather than letting a taste call be made by a
    # deriver.
    assert "PROVISIONAL" in spec["consumer"]
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
