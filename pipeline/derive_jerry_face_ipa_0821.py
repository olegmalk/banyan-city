#!/usr/bin/env python3
r"""AN ATTRIBUTE INSTRUMENT FOR AN ATTRIBUTE PROBLEM: IPA OFF THE TILE'S HEAD.

THE WORDING ROUTE FOR THE FACE CLOSED ON 2026-08-21. Six rungs (f4, g1, g2, h1,
h2, j1, j2) moved white-eye area 0.111 -> 0.035 against a 0.030 bar and never
once drew the brow bar. The residual, measured, is not "the eye is too big" --
scaled to a common head height the tile's eye is 28.9 x 15.1 px and j2's is
27 x 27: THE RIGHT WIDTH TO WITHIN 7% AND 79% TOO TALL. Four positive shape
tags bought 7 px of the 19 px of HEIGHT that were needed, and the last two
bought 3 between them. `thick eyebrows` in the positive (j1) drew a lash arc
welded to the eye rim rather than a brow with skin under it.

k1 IS ONE VARIABLE FROM j2 AND THE VARIABLE IS THE INSTRUMENT, NOT THE WORDING.
Same prompt, same negative, same h19 skeleton, same --scale 1.0, same seed
20260823. Added: an IP-Adapter reference that IS the tile's own head, masked to
the head box the last seven rungs have all drawn into.

  --ip-ref    farm-out/jerry-skel-assets-0820/jerry-tile-head-0821.png
              adult-b19-0819.jpg cropped (176,280)-(332,432): dome, both ear
              flanges, the brow mass, both slits, the muzzle and the mouth
              line. A HEAD CROP, not the whole tile, because IPA leaks
              composition as well as attribute and the tile is a seated figure
              in a purple cowl.
  --ip-mask   315,130,515,350 in RENDER pixels. The drawn head across j1/j2
              sits at (330,145)-(502,330); the mask is that box with margin for
              the brow and the ear flanges, and it is the second half of the
              same containment.
  --ip-scale  0.7, the diffusers masking-example default and the value
              ep2-b08-ipamask-0819 ran at. NOT swept here: one variable.

VERIFIED BEFORE THIS FILE WAS WRITTEN, because the last thing this gate needs
is a job that dies after the queue has claimed it: controlnet_plate.py carries
--ip-ref / --ip-mask / --ip-ref-sha256 / --ip-scale, and the box has
h94/IP-Adapter in its HF cache. The image encoder folder is left at the default
`models/image_encoder` -- it contains a slash, which is what makes it resolve
as a full path rather than under --ip-subfolder.

WHAT WOULD FALSIFY THE CONTAINMENT, named in advance: a seated figure, a purple
cowl, or the tile's field background. Any of those and the mask is not holding,
and the next variable is the mask, not the scale.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import derive_fetch_guard  # noqa: E402
import derive_spec  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = "pipeline/jobs/ep2-jerry-face-j2-0821.yaml"
PARENT_DIR_TOKEN = "jerryface-j2-0821"
JOB_DIR = "jerryface-k1-0821"
NEW_ID = "ep2-jerry-face-k1-0821"

ASSET_URL = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
             "farm-out/jerry-skel-assets-0820/")
DRIVER_SHA = "aff188907fa03914b30a8cec2e5f739a5c4941f5d4246f4b2e220a9cc047c66a"
HINT = "jerry-skel-h19-0820"
HINT_SHA = "244094ed608666035d670d8bc5149ff6499c1497e5501724728d2af79b54829c"
REF = "jerry-tile-head-0821"
REF_SHA = "6dbb27a82b1b03e426030a07ae14d4013af6b866be661ea4fcca1160947d374c"
IP_MASK = "315,130,515,350"
IP_SCALE = "0.7"
ARM = "ipahead"
# the commit that carries the three staged inputs -- provenance only, but the
# meta.yaml this writes is what a later lane reads to re-fetch them.
COMMIT = "29939faba45625c647bb05da9573c4151b8b259d"


def stage_step():
    return (
        '# EVERY INPUT THIS FRAME IS CONDITIONED ON IS FETCHED AND SHA-CHECKED\n'
        '# BEFORE A GPU SECOND IS SPENT -- and k1 has THREE, because the\n'
        '# IP-Adapter reference is as much this frame\'s condition as the\n'
        '# skeleton is. The job dirs on this card carry a hand-staged\n'
        '# src\\pipeline\\controlnet_plate.py and nothing else.\n'
        'import hashlib, os, urllib.request\n'
        'base = "%s"\n'
        'root = r"C:\\banyan-farm\\%s\\src"\n'
        'want = [("controlnet_plate.py", os.path.join(root, "pipeline"),\n'
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
        % (ASSET_URL, JOB_DIR, DRIVER_SHA, HINT, HINT_SHA, REF, REF_SHA))


def publish_step():
    return (
        '# Required by box_enqueue.courier_problems: the courier pushes from\n'
        '# farm-out and from nowhere else, and ep2-cnet-probe-0817 rendered\n'
        '# perfectly and was invisible for two days for want of this step.\n'
        '# THE REFERENCE TRAVELS WITH THE FRAME. A reader scoring whether the\n'
        '# adapter carried the brow needs the brow it was shown.\n'
        'import glob, hashlib, os, shutil\n'
        'out_dir = "C:/banyan-farm/%(d)s/out"\n'
        'pay_dir = "C:/banyan-farm/%(d)s"\n'
        'ctl_dir = "C:/banyan-farm/%(d)s/src/pipeline/control"\n'
        'dst = "C:/banyan-farm/courier-box/farm-out/%(id)s"\n'
        'os.makedirs(dst, exist_ok=True)\n'
        'files = sorted(glob.glob(out_dir + "/%(id)s-%(arm)s.png*")\n'
        '               + glob.glob(pay_dir + "/prompt.txt")\n'
        '               + glob.glob(pay_dir + "/negative.txt")\n'
        '               + glob.glob(ctl_dir + "/%(hint)s.png")\n'
        '               + glob.glob(ctl_dir + "/%(ref)s.png"))\n'
        'lines = []\n'
        'for f in files:\n'
        '    shutil.copy2(f, dst)\n'
        '    c = os.path.join(dst, os.path.basename(f))\n'
        '    with open(c, "rb") as fh:\n'
        '        h = hashlib.sha256(fh.read()).hexdigest()\n'
        '    lines.append(h + "  " + os.path.basename(f))\n'
        'with open(os.path.join(dst, "%(id)s.sha256"), "w",\n'
        '          newline="\\n") as fh:\n'
        '    fh.write("\\n".join(sorted(lines)) + "\\n")\n'
        'print("published", len(files), "file(s) + manifest ->", dst)\n'
        'raise SystemExit(0 if len(files) >= 6 else 1)'
        % {"d": JOB_DIR, "id": NEW_ID, "arm": ARM, "hint": HINT, "ref": REF})


BAR = """T1b EYE SHAPE and P1 BROW BAR, the two clauses the wording route could
not reach, scored exactly as they were on j1/j2 so the numbers are comparable.
  T1b  white-eye pixels over the head bounding box. TILE 0.0143, j2 0.0353.
       PASS is 0.030 or lower AND reading as an upward-slanting slit at 1:1 --
       eye HEIGHT is the whole residual, 27 px where the tile scales to 15.
  P1   a dark brow bar ABOVE the eyes with green skin between it and the eye.
       0 of 7 rungs have ever scored it. A lash arc welded to the eye rim is
       an eyelid and does not count.
HELD, and a regression on any of these is a FAIL of the instrument even if the
face improves: T1 no iris and no pupil, T3 no age modelling, T8 4.5+ heads
(j1/j2 measured 5.59 / 5.56), P3 a mouth line, P4 facial shading.
CONTAINMENT, and it is scored: the figure must still be STANDING, in the
patchwork cloak, in tall grass. A seated figure, a purple cowl or the tile's
field background means the head-box mask is not holding."""

WHY = ("RUNG k1: the same j2 frame with an IP-ADAPTER REFERENCE THAT IS THE "
       "TILE'S OWN HEAD, masked to the head box. One variable, and the "
       "variable is the instrument. The wording route closed at four tags of "
       "affordance with the residual measured as a single number -- j2's eye "
       "is the right WIDTH to within 7% and 79% too TALL, and the brow bar is "
       "0 of 7 -- and canon's own curation file says why no word will fix it: "
       "Danbooru has no tag for this creature's eye slit or brow mass any "
       "more than it has one for its ear. An attribute the dialect cannot "
       "name needs an instrument that does not name, which is what IPA is.")

CONSUMER = ("THE JERRY LoRA'S LAST OPEN GATE, second instrument. "
            "train-jerry-0820 is UNFILED and stays that way until a rung "
            "passes P1 and T1b with T1/T3/T8/P3/P4 intact; the set is still 7 "
            "frames in 4 poses. No beat plate, no pick, nothing promoted.")

SUCCESS = ("ONE 832x1216 png at seed 20260823 on the h19 skeleton at scale "
           "1.0, j2's prompt and negative byte-identical, plus --ip-ref "
           "jerry-tile-head-0821.png --ip-mask 315,130,515,350 --ip-scale "
           "0.7. Scored on T1b and P1 with T1, T3, T8, P3, P4 held and the "
           "standing/cloak/grass containment scored.")

PREDICTED = (
    "TWO WAYS THIS FAILS AND THEY POINT DIFFERENT DIRECTIONS.\n\n"
    "CONTAINMENT BREAK -- the frame comes back seated, or cowled in purple, "
    "or standing in the tile's open field. IPA leaks composition and the ref "
    "is a crop of a seated figure. Then the mask is the next variable, not "
    "the scale, and the tightest available mask is the head box itself "
    "(330,145,502,330) with the ref repainted onto flat ground.\n\n"
    "ATTRIBUTE MISS -- the containment holds and the face is still j2's. That "
    "would mean 0.7 is too weak against a controlnet running at scale 1.0 for "
    "the full denoise, and the next rung is an ip-scale ladder, NOT a second "
    "reference and NOT a wording edit.\n\n"
    "AND THE THIRD OUTCOME IS THE ONE TO WATCH FOR: the brow and slit arrive "
    "AND T1 regresses to pupils, because the tile's slits sit in a modelled "
    "socket and IPA carries what it is shown. That is a partial win and it is "
    "scored as a FAIL of this rung, because a LoRA trained on a pupilled face "
    "teaches pupils.")


def main():
    child = derive_spec.derive(
        src=PARENT, new_id=NEW_ID,
        fresh={"owner": "goblin reference-route lane, 2026-08-21",
               "why": WHY, "consumer": CONSUMER, "success": SUCCESS},
        overrides={"argv:--arm": ARM, "argv:--repo-commit": COMMIT,
                   "key:beat": 2, "key:priority": 28, "key:est_minutes": 4},
        retoken=[(PARENT_DIR_TOKEN, JOB_DIR)],
        extra={"bar": BAR,
               "failure_predicted_in_advance": PREDICTED,
               "the_one_variable":
                   "an IP-Adapter reference that is the tile's own head crop, "
                   "masked to the head box, at --ip-scale 0.7. Prompt, "
                   "negative, skeleton, --scale and seed are j2's, unchanged.",
               "the_rung_this_is_one_variable_from": "ep2-jerry-face-j2-0821",
               "one_sample_rule":
                   "ONE rung. The wording ladder's stop names IP-Adapter as "
                   "the route and this is the first sample on it; no scale "
                   "sweep, no second reference, no second seed until this one "
                   "has been looked at.",
               "ip_adapter":
                   {"ref": "farm-out/jerry-skel-assets-0820/%s.png" % REF,
                    "ref_sha256": REF_SHA,
                    "ref_provenance":
                        "review/ep2-goblin-design-0819/adult-b19-0819.jpg "
                        "cropped (176,280)-(332,432), 156x152, no resample",
                    "mask": IP_MASK,
                    "mask_frame": "RENDER pixels, 832x1216",
                    "scale": IP_SCALE,
                    "weights": "h94/IP-Adapter sdxl_models/"
                               "ip-adapter-plus_sdxl_vit-h.safetensors "
                               "(cached on the box; the -FACE variant is 847 "
                               "MB and is NOT cached)"}},
        by="pipeline/derive_jerry_face_ipa_0821.py")

    # ---- the IPA flags are ADDED, not overridden: derive_spec's argv
    # override only rewrites a flag the parent already carries, and j2 carries
    # none of these. Inserted before --prompt-file and asserted after.
    for step in child["steps"]:
        argv = list(step.get("argv") or [])
        if "--prompt-file" not in argv:
            continue
        i = argv.index("--prompt-file")
        step["argv"] = argv[:i] + [
            "--ip-ref", "pipeline/control/%s.png" % REF,
            "--ip-mask", IP_MASK,
            "--ip-ref-sha256", REF_SHA,
            "--ip-scale", IP_SCALE,
        ] + argv[i:]

    child["steps"][0] = {"name": "stage",
                         "argv": [r"C:\banyan-farm\venv\Scripts\python.exe",
                                  "-c", stage_step()]}
    child["steps"][-1] = {"name": "publish",
                          "argv": [r"C:\banyan-farm\venv\Scripts\python.exe",
                                   "-c", publish_step()]}
    child["artifacts"] = [
        r"C:\banyan-farm\%s\out\%s-%s.png" % (JOB_DIR, NEW_ID, ARM)]

    render = [s for s in child["steps"] if s["name"] not in ("stage", "publish")]
    assert len(render) == 1, [s["name"] for s in render]
    argv = [str(a) for a in render[0]["argv"]]
    for flag, val in (("--ip-ref", "pipeline/control/%s.png" % REF),
                      ("--ip-mask", IP_MASK),
                      ("--ip-ref-sha256", REF_SHA),
                      ("--ip-scale", IP_SCALE),
                      ("--seed", "20260823"),
                      ("--scale", "1.0"),
                      ("--arm", ARM),
                      ("--repo-commit", COMMIT)):
        assert argv.count(flag) == 1, (flag, argv.count(flag))
        assert argv[argv.index(flag) + 1] == val, (flag, argv[argv.index(flag) + 1])
    assert JOB_DIR in " ".join(argv) and PARENT_DIR_TOKEN not in " ".join(argv)

    out = "pipeline/jobs/%s.yaml" % NEW_ID
    derive_spec.write(child, out)
    derive_fetch_guard.assert_fetch_urls_resolve(
        os.path.join(REPO, out),
        must_hold=("controlnet_plate.py", HINT + ".png", REF + ".png"))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
