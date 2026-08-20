#!/usr/bin/env python3
r"""EIGHT RUNGS ON THE REFERENCE ROUTE. The variable is GEOMETRY, not a word.

WHERE THIS PICKS UP. `work-ladder-0819.md` closed the wording route for BODY
PROPORTION and pre-registered the closing before the three rungs ran: twelve
poses off the ratified recipe hold the face twelve times out of twelve and are
bobbleheads twelve times out of twelve, and q1 (`super deformed` in the
negative), q2 (`long legs, narrow waist`) and q3 (`1other` -> `1boy`) all
FAILED. The named next instrument was a reference route.

THE INSTRUMENT, PICKED BY ARGUMENT FROM THE RECORD AND NOT BY THEORY. Two
candidates were named. The record separates them:

  * `b08-arm-route-0819.md` Sec 13 MEASURED that xinsir/controlnet-openpose-sdxl-1.0
    binds STATURE on this exact checkpoint -- "830/715 px, ratio 1.161 against
    1.100 authored, both statures within 4%" -- and Sec 11 measured the foot
    line landing at y=1151 against an authored 1149.1.
  * Sec 11 MEASURED that the masked IP-Adapter is an ATTRIBUTE instrument which
    does not govern geometry: skin, face and wardrobe all transferred off the
    references and the ARM STILL AIMED WRONG, and that verdict says in as many
    words, of the aim, "That is not the adapter."

Head-to-body is geometry. Second reason, and it is the one-variable doctrine:
the FACE IS ALREADY SOLVED BY WORDING, so a skeleton leaves the ratified recipe
byte-identical, where an IP-Adapter off the tile would re-supply the very
attributes the wording already gets right and make any verdict unattributable.
IP-Adapter is therefore round 2's instrument if this round fails, not round 1's.

WHY THE PARENT IS A BEAT-08 SPEC. `ep2-b08-posenet-sample-0819` is the only spec
in the tree that conditions ONE openpose net at xinsir's own operating point,
and its publish glob matches its own `--arm` (`posehint`). The twelve-pose set's
parents cannot be used: they carry `--arm nocontrol`, which means
`controlnet_plate.py:488` renders with NO net at all, AND they carry the publish
bug this lane's audit found -- a glob for `<task>-hintskel.png` against an arm
that writes `<task>-nocontrol.png`, so every one of them reported rc=1 on a
render that succeeded. Deriving from the beat-08 parent inherits neither defect.
`key:beat` moves 8 -> 2 because this is character design, not beat 08.

WHY EACH JOB STAGES ITS OWN `src`. The job dirs on the card carry a hand-staged
`src\pipeline\controlnet_plate.py` and nothing else -- `jerrytile-p04-0820\src`
holds exactly one file, and the b08 job dirs that held control PNGs are gone. A
hint that is not on the card is a job that dies after the queue has claimed it.
So every rung's FIRST step fetches its two inputs from
`farm-out/jerry-skel-assets-0820/` and asserts both sha256s before a GPU second
is spent. `derive_fetch_guard.assert_fetch_urls_resolve` re-reads the EMITTED
yaml and checks that directory exists in this tree, AFTER retoken has had its
way -- which is the guard that exists because `ep2-b08-nogoblin-0820` was filed
against a directory nobody had written and died on the card with a 404.

THE EIGHT RUNGS. One variable each, off a named parent rung.

  n1  h19 @ scale 1.0     THE NET ITSELF, against p04's wording-only frame, at
                          xinsir's documented operating point for openpose.
  n2  h19 @ 0.7           scale, off n1.
  n3  h19 @ 0.45          scale, off n1. The scribble net's bracketed value; run
                          because Sec 17 showed scale is the lever that decides
                          whether conditioning costs the picture.
  n4  h19 @ 1.3           scale, off n1. Over-drive; Sec 16 measured that too
                          much strength eats linework and canon attributes.
  n5  h32 @ 1.0           THE HINT'S head_frac, off n1. THE CONTROL: the
                          bobblehead ratio, authored on purpose.
  n6  h16 @ 1.0           the hint's head_frac, off n1. Overshoot to 6.25 heads.
  n7  h19 @ 1.0, seed +1  the seed, off n1.
  n8  h19stride @ 1.0     the POSE (hint and the two pose words together, which
                          is named here rather than folded in), off n1.

WHY n5 IS NOT A WASTED RENDER, said plainly because it looks like one: it asks
the net for the defect. If h19 comes back lean and h32 comes back a bobblehead
at the same scale, seed and words, then the skeleton is DEMONSTRATED to carry
head-to-body and the good frame is a mechanism rather than a lucky seed. If BOTH
come back at 5 heads the net is binding nothing and h19 was the checkpoint's own
prior; if BOTH come back at 3 the same. A rung that can only confirm is not an
instrument.

    python3 pipeline/derive_jerry_skel_0820.py
    python3 pipeline/derive_jerry_skel_0820.py --selftest

$0. No model, no network, no GPU.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard  # noqa: E402
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = "pipeline/jobs/ep2-b08-posenet-sample-0819.yaml"
PARENT_DIR_TOKEN = "b08pose-0819"
PARENT_HINT_TOKEN = "b08-openpose-0819"

# The commit that holds the hint bytes and the assets directory.
ASSET_COMMIT = "8b1dd656324509562b2d65c35f677505b2375f89"
ASSET_DIR = "farm-out/jerry-skel-assets-0820"
ASSET_URL = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
             + ASSET_DIR + "/")
DRIVER_SHA = "aff188907fa03914b30a8cec2e5f739a5c4941f5d4246f4b2e220a9cc047c66a"

HINT_SHA = {
    "jerry-skel-h19-0820":
        "244094ed608666035d670d8bc5149ff6499c1497e5501724728d2af79b54829c",
    "jerry-skel-h32-0820":
        "cab6ce1cd73fd19558790f085dbe7dbb668f4427aaa56b71817910753aa4bb5c",
    "jerry-skel-h16-0820":
        "c58009a4e0d35fb1301c5a8e240ea41680c80c96bf5be3e31385b08ccd480f07",
    "jerry-skel-h19stride-0820":
        "a853228c770ff9a3015985a5cd1250dc8d020c0f112121f084840a847dcde3f0",
}

# ---- the ratified recipe, byte-identical to ep2-jerry-tileset-p04-0820's ----
QUALITY = "masterpiece, best quality, very aesthetic"
CORE = ("1other, solo, colored skin, green skin, bald, patchwork cloak, "
        "blank eyes, tsurime, jitome, no nose, closed mouth, :|, expressionless")
POSE_STAND = "standing, arms at sides, in tall grass, full body"
POSE_STRIDE = "walking, arm outstretched, in tall grass, full body"
NEG = ("lowres, worst quality, low quality, text, watermark, pointy ears, "
       "long pointy ears, elf, monster boy, pointy nose, dot nose, human face, "
       "wrinkled skin, old man, thick eyebrows, hair, beard, child, chibi, "
       "grey skin, pale skin, 2boys")
SEED = 20260823


def prompt_for(pose):
    return "%s, %s, %s" % (QUALITY, CORE, pose)


# id-suffix, hint stem, scale, seed, pose-words, parent-rung, the one variable
RUNGS = [
    ("n1", "jerry-skel-h19-0820", "1.0", SEED, POSE_STAND,
     "ep2-jerry-tileset-p04-0820 (wording only, no net)",
     "THE NET ITSELF. p04's prompt, negative, seed and framing to the byte, "
     "plus a COCO-18 skeleton authored at the tile's measured 5.26 heads, at "
     "xinsir's own documented operating point for openpose (1.0)."),
    ("n2", "jerry-skel-h19-0820", "0.7", SEED, POSE_STAND, "n1",
     "the conditioning scale, 1.0 -> 0.7, and nothing else."),
    ("n3", "jerry-skel-h19-0820", "0.45", SEED, POSE_STAND, "n1",
     "the conditioning scale, 1.0 -> 0.45, and nothing else. 0.45 is the value "
     "the b08 route bracketed for the SCRIBBLE net; run here because Sec 17 "
     "showed scale, not the choice of net, is what decides whether "
     "conditioning costs the picture."),
    ("n4", "jerry-skel-h19-0820", "1.3", SEED, POSE_STAND, "n1",
     "the conditioning scale, 1.0 -> 1.3, and nothing else. Over-drive, in "
     "the direction Sec 16 measured as destructive, so the bracket has a "
     "far side and 1.0 is not merely the only value tried."),
    ("n5", "jerry-skel-h32-0820", "1.0", SEED, POSE_STAND, "n1",
     "THE HINT'S head_frac, 0.190 -> 0.320, and nothing else. The bobblehead "
     "ratio the twelve-pose set actually drew, authored ON PURPOSE. This is "
     "the control that decides whether n1 is a mechanism or a lucky seed."),
    ("n6", "jerry-skel-h16-0820", "1.0", SEED, POSE_STAND, "n1",
     "the hint's head_frac, 0.190 -> 0.160 (6.25 heads), and nothing else. "
     "Asks whether the net lands where it is aimed or drifts back toward the "
     "checkpoint's own prior."),
    ("n7", "jerry-skel-h19-0820", "1.0", SEED + 1, POSE_STAND, "n1",
     "the seed, 20260823 -> 20260824, and nothing else."),
    ("n8", "jerry-skel-h19stride-0820", "1.0", SEED, POSE_STRIDE, "n1",
     "THE POSE -- a striding skeleton at the same head_frac AND the two pose "
     "words that match it. That is a hint and a wording moving together and "
     "it is named as one variable rather than folded in, because a striding "
     "skeleton under `standing, arms at sides` is a contradiction, not a "
     "control."),
]

BAR = """T8 IS THE SCORED CLAUSE AND IT IS THE WHOLE POINT.
  T8 HEAD-TO-BODY. Standing height divided by head height, BY EYE against
     adult-b19-0819.jpg. The tile reads 5.2; the twelve-pose set reads about 3.
     PASS is 4.5 or better with lean limbs rather than stubby ones.
T1-T3 and T7 are REGRESSION CLAUSES and a rung that buys the body by breaking
the face is a FAIL: blank white eyes, no human nose, no age modelling, no
patchwork on the skull. The wording is byte-identical to p04's, so any face
change here is the NET's doing and is worth knowing either way.
T4 (ears) is unscorable at full body and is not scored. T6 remains STRUCK.
n5 IS SCORED BACKWARDS: it PASSES its purpose by coming back a BOBBLEHEAD. A
lean n5 falsifies the whole route and is the single most useful bad news in
the batch."""

PREDICTED = """n1 AND n5 SPLIT, AND THAT IS THE RESULT. n1 comes back at 4.5-5.5
heads with the face intact; n5 comes back at about 3 heads with the same face,
the same words and the same seed. The mechanism argument is that a COCO-18
skeleton encodes neck-to-nose against neck-to-ankle, which IS head-to-body, and
Sec 13 already measured this net binding stature to within 4% of what was
authored.
THE FAILURE I EXPECT IF ONE COMES, and it is specific: THE HEAD IS DRAWN AROUND
THE FACE KEYPOINTS RATHER THAN AT THE AUTHORED SIZE. openpose has no crown
keypoint -- it has nose, two eyes, two ears -- so the net can honour every
keypoint and still inflate the skull upward off the nose, which would return a
bobblehead whose FACE is correctly placed. If that fires, the diagnosis is
visible in one glance (nose and shoulders at the authored y, crown far above
the authored crown) and the answer is a second net carrying a silhouette, not
more openpose scale.
n3 AND n4 BRACKET, AND I EXPECT n4 TO COST THE PICTURE, per Sec 16: at 0.8 on
two nets the linework went flat and a canon attribute flipped. 1.3 on one net
is the same direction.
n6 IS THE COIN FLIP. Either the net lands at 6.25 heads -- in which case the
authored ratio is a real dial and the tile's exact value is reachable -- or it
saturates near 5, which would say the checkpoint's prior sets a floor and the
skeleton only nudges.
n8 IS THE ONE THAT MATTERS FOR TRAINING, not for tonight's verdict: the LoRA
gate is proportion diversity across poses, so a second pose is filed in this
batch rather than after it."""


def stage_step(job_dir, hint_stem):
    """The fetch-and-assert step. Written here so both files are sha-checked."""
    return (
        '# EVERY INPUT THIS FRAME IS CONDITIONED ON IS FETCHED AND SHA-CHECKED\n'
        '# BEFORE A GPU SECOND IS SPENT. The job dirs on this card carry a\n'
        '# hand-staged src\\pipeline\\controlnet_plate.py and nothing else --\n'
        '# jerrytile-p04-0820\\src holds exactly one file -- so a hint that is\n'
        '# not fetched is a job that dies after the queue has claimed it.\n'
        'import hashlib, os, urllib.request\n'
        'base = "%s"\n'
        'root = r"C:\\banyan-farm\\%s\\src"\n'
        'want = [("controlnet_plate.py", os.path.join(root, "pipeline"),\n'
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
        % (ASSET_URL, job_dir, DRIVER_SHA, hint_stem, HINT_SHA[hint_stem])
    )


def main():
    if "--selftest" in sys.argv:
        rc = derive_spec.selftest() or derive_fetch_guard.selftest()
        return rc
    written = []
    for suffix, hint, scale, seed, pose, parent_rung, variable in RUNGS:
        new_id = "ep2-jerry-skel-%s-0820" % suffix
        job_dir = "jerryskel-%s-0820" % suffix
        child = derive_spec.derive(
            src=PARENT,
            new_id=new_id,
            fresh={
                "owner": "goblin reference-route lane, 2026-08-20 night",
                "why": ("RUNG %s: %s\nThe wording route is CLOSED for body "
                        "proportion -- twelve poses hold the face and all "
                        "twelve are bobbleheads, and q1/q2/q3 failed exactly "
                        "as pre-registered. This is the reference route the "
                        "ladder named, and the instrument is the POSE NET "
                        "rather than the IP-Adapter because "
                        "b08-arm-route-0819.md Sec 13 measured openpose "
                        "binding stature to within 4%% of authored on this "
                        "checkpoint while Sec 11 measured the masked adapter "
                        "transferring skin, face and wardrobe and STILL "
                        "aiming the arm wrong. Head-to-body is geometry."
                        % (suffix, variable)),
                "consumer": ("THE JERRY LoRA SET, HELD SINCE 08-20 ON SEVEN "
                             "USABLE FRAMES IN FOUR POSES. The gate the "
                             "ladder set is not a face -- the face is solved "
                             "-- it is PROPORTION DIVERSITY: frames at the "
                             "tile's head-to-body across several poses. This "
                             "batch is the first attempt to produce any. "
                             "Nothing here is a beat plate and nothing is "
                             "promoted to a cut."),
                "success": ("ONE 832x1216 png at seed %d conditioned on "
                            "%s.png through "
                            "xinsir/controlnet-openpose-sdxl-1.0 at scale %s, "
                            "with the ratified recipe's prompt and negative "
                            "byte-identical to "
                            "ep2-jerry-tileset-p04-0820's. Scored on T8 "
                            "(head-to-body) with T1-T3 and T7 as regression "
                            "clauses." % (seed, hint, scale)),
            },
            overrides={
                "seed": seed,
                "argv:--scale": scale,
                "argv:--control-sha256": HINT_SHA[hint],
                "argv:--repo-commit": ASSET_COMMIT,
                "payload:prompt.txt": prompt_for(pose),
                "payload:negative.txt": NEG,
                "key:beat": 2,
                "key:priority": 34,
                "key:est_minutes": 3,
            },
            retoken=[(PARENT_DIR_TOKEN, job_dir),
                     (PARENT_HINT_TOKEN, hint)],
            extra={
                "bar": BAR,
                "the_one_variable": variable,
                "the_rung_this_is_one_variable_from": parent_rung,
                "failure_predicted_in_advance": PREDICTED,
                "one_sample_rule": (
                    "This is ONE BATCH of eight at ~15 s a render on an idle "
                    "card, not a scaled recipe: eight rungs on ONE question "
                    "with one variable each, of which one (n5) is a control "
                    "authored to produce the DEFECT. No frame from this batch "
                    "enters a cut, a plate or the LoRA set without an eye "
                    "verdict against adult-b19-0819.jpg first."),
            },
            by="pipeline/derive_jerry_skel_0820.py",
        )
        # The fetch step is PREPENDED, and it is authored here rather than
        # inherited: the parent has no stage step at all.
        child["steps"] = [{
            "name": "stage",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c",
                     stage_step(job_dir, hint)],
        }] + list(child["steps"])
        out = "pipeline/jobs/%s.yaml" % new_id
        derive_spec.write(child, out)
        derive_fetch_guard.assert_fetch_urls_resolve(
            os.path.join(REPO, out),
            must_hold=("controlnet_plate.py", hint + ".png"))
        written.append(out)
        print("wrote %s  hint=%s scale=%s seed=%d" % (out, hint, scale, seed))
    print("\n%d spec(s). Next: box_enqueue each one." % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
