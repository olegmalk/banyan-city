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
and the next variable is the mask, not the scale. None of the three fired at
0.7.

RE-RUNNING k1 DOES NOT REPRODUCE THE SPEC THAT RAN, and this is deliberate.
k1 rendered at 21:39Z; k2 was authored afterwards off what k1 showed, and
writing k2's rung table rewrote the shared `bar` and `one_sample_rule` prose
that both rungs draw from -- so `python3 ... k1` now emits a spec carrying
k1's own results. The file on disk is left as the one that RAN, spec_sha256
e9334e5794fa592d311d52bfd2e6767220f080139fee4521e519b02cb9e4bd07, because a
spec is a record of what conditioned a frame and not a document to keep
current. `--force` will overwrite it; do not, unless you are re-running the
render too.
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

ASSET_URL = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
             "farm-out/jerry-skel-assets-0820/")
DRIVER_SHA = "aff188907fa03914b30a8cec2e5f739a5c4941f5d4246f4b2e220a9cc047c66a"
HINT = "jerry-skel-h19-0820"
HINT_SHA = "244094ed608666035d670d8bc5149ff6499c1497e5501724728d2af79b54829c"
REF = "jerry-tile-head-0821"
REF_SHA = "6dbb27a82b1b03e426030a07ae14d4013af6b866be661ea4fcca1160947d374c"
IP_MASK = "315,130,515,350"
ARM = "ipahead"

# (suffix, --ip-scale, the one variable). k2 was filed AFTER k1 was looked at,
# which is the one-sample rule satisfied rather than skipped: k1 is the first
# sample on this instrument and k2 is one variable from it.
RUNGS = [
    ("k1", "0.7",
     "the IP-Adapter itself, at the diffusers masking-example default 0.7 -- "
     "the value ep2-b08-ipamask-0819 ran at. Prompt, negative, skeleton, "
     "--scale and seed are j2's, unchanged."),
    ("k2", "0.9",
     "k1's frame with --ip-scale 0.7 -> 0.9 and NOTHING else. k1 bought the "
     "tile's eye KIND (aspect 0.54 against the tile's 0.52, where six wording "
     "rungs sat at 1.0-1.26) and its brow, and did NOT buy SIZE: k1's eye "
     "bounding box is 1.87x the tile's relative to the head, where j2's was "
     "1.40x. Wrong size, right kind. Strength is the dial that decides how far "
     "the frame is pulled toward the reference's proportions, and it is the "
     "only lever that is one variable from here."),
]
# the commit that carries the three staged inputs -- provenance only, but the
# meta.yaml this writes is what a later lane reads to re-fetch them.
COMMIT = "29939faba45625c647bb05da9573c4151b8b259d"


def stage_step(job_dir):
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
        % (ASSET_URL, job_dir, DRIVER_SHA, HINT, HINT_SHA, REF, REF_SHA))


def publish_step(job_dir, new_id):
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
        % {"d": job_dir, "id": new_id, "arm": ARM, "hint": HINT, "ref": REF})


BAR = """T1b EYE SHAPE and P1 BROW BAR, the two clauses the wording route could
not reach, scored exactly as they were on j1/j2 so the numbers are comparable.
Ruler: pipeline/measure_face_eye_0821.py, whose --selftest reproduces the
published f/g/h numbers before it is allowed to produce a new one.
  T1b  AREA -- white-eye pixels over the head box. TILE 0.0143, j2 0.0353,
       k1 0.0566. PASS is 0.030 or lower.
       SHAPE -- per-eye aspect (h/w). TILE 0.52. Six wording rungs sat at
       1.00-1.26; k1 came back 0.54. PASS is a slit at 1:1, not a small oval.
       BOTH clauses, and k1 proved they move independently.
  P1   a dark brow ABOVE the eyes with skin between it and the eye. 0 of 7
       wording rungs ever scored it; k1 did. A lash arc welded to the eye rim
       is an eyelid and does not count.
HELD, and a regression on any of these is a FAIL of the instrument even if the
face improves: T1 no iris and no pupil, T3 no age modelling, T8 4.5+ heads,
P3 a mouth line, P4 facial shading.
T8 IS THE ONE UNDER PRESSURE AND IT IS SCORED FIRST. j2 drew 5.56 heads at
head_frac 0.181; k1 drew 4.57 at 0.219, against a 0.190 authored skeleton. The
reference is a HEAD CROP, so the adapter's own notion of how much frame is head
is 100%, and the mask says WHERE not HOW MUCH. Below 4.5 is a fail.
CONTAINMENT, and it is scored: the figure must still be STANDING, in the
patchwork cloak, in tall grass. None of the three predicted breaks fired on k1
at 0.7 -- no seated pose, no purple cowl, no tile background -- and 0.9 is
where they would first show."""

WHY = {
    "k1": (
        "RUNG k1: the same j2 frame with an IP-ADAPTER REFERENCE THAT IS THE "
        "TILE'S OWN HEAD, masked to the head box. One variable, and the "
        "variable is the instrument. The wording route closed at four tags of "
        "affordance with the residual measured as a single number -- j2's eye "
        "is the right WIDTH to within 7% and 79% too TALL, and the brow bar is "
        "0 of 7 -- and canon's own curation file says why no word will fix it: "
        "Danbooru has no tag for this creature's eye slit or brow mass any "
        "more than it has one for its ear. An attribute the dialect cannot "
        "name needs an instrument that does not name, which is what IPA is."),
    "k2": (
        "RUNG k2: k1 with --ip-scale 0.7 -> 0.9 and nothing else.\n\n"
        "WHAT k1 SETTLED. The instrument works and it works on the clause the "
        "words could not reach. k1 came back with the tile's eye KIND -- "
        "aspect 0.54 against the tile's 0.52, where six wording rungs sat "
        "between 1.00 and 1.26 -- and with a brow, the clause that was 0 of 7. "
        "It also holds T1, T2, T3, P2, P3, P4 and the whole containment.\n\n"
        "WHAT k1 DID NOT BUY, AND IT IS ONE WORD: SIZE. Relative to the head "
        "box, k1's eye bounding box is 1.87x the tile's; j2's was 1.40x. So "
        "the frame moved further away on scale while arriving on shape, which "
        "is not a contradiction -- it is the signature of an instrument that "
        "supplies KIND. Strength is the dial that says how far the picture is "
        "pulled toward the reference's own proportions, and it is the only "
        "lever one variable from here."),
}

PARENT_RUNG = {"k1": "ep2-jerry-face-j2-0821", "k2": "ep2-jerry-face-k1-0821"}

CONSUMER = ("THE JERRY LoRA'S LAST OPEN GATE. train-jerry-0820 is UNFILED and "
            "stays that way until a rung passes T1b and P1 with T1/T3/T8/P3/P4 "
            "intact; the set is still 7 frames in 4 poses. No beat plate, no "
            "pick, nothing promoted.")

SUCCESS = ("ONE 832x1216 png at seed 20260823 on the h19 skeleton at scale "
           "1.0, j2's prompt and negative byte-identical, plus --ip-ref "
           "jerry-tile-head-0821.png --ip-mask 315,130,515,350 --ip-scale %s. "
           "Scored on T1b (area AND aspect) and P1 with T1, T3, T8, P3, P4 "
           "held and the standing/cloak/grass containment scored.")

ONE_SAMPLE = {
    "k1": ("ONE rung. The wording ladder's stop names IP-Adapter as the route "
           "and this is the first sample on it; no scale sweep, no second "
           "reference, no second seed until this one has been looked at."),
    "k2": ("ONE rung, filed AFTER k1 was rendered, measured and read at 1:1 -- "
           "the rule satisfied rather than skipped. NOT a scale sweep: 0.9 is "
           "the single next value, and if it splits T1b from T8 the answer is "
           "a head_frac edit on top, not three more scales."),
}

PREDICTED = {
    "k1": (
        "TWO WAYS THIS FAILS AND THEY POINT DIFFERENT DIRECTIONS.\n\n"
        "CONTAINMENT BREAK -- the frame comes back seated, or cowled in "
        "purple, or standing in the tile's open field. IPA leaks composition "
        "and the ref is a crop of a seated figure. Then the mask is the next "
        "variable, not the scale.\n\n"
        "ATTRIBUTE MISS -- the containment holds and the face is still j2's. "
        "Then 0.7 is too weak against a controlnet running at 1.0 for the full "
        "denoise, and the next rung is an ip-scale ladder.\n\n"
        "AND THE THIRD OUTCOME TO WATCH FOR: the brow and slit arrive AND T1 "
        "regresses to pupils, because the tile's slits sit in a modelled "
        "socket and IPA carries what it is shown. Scored as a FAIL, because a "
        "LoRA trained on a pupilled face teaches pupils."),
    "k2": (
        "I EXPECT THIS TO SPLIT T1b FROM T8, AND THAT IS WHY IT IS WORTH A "
        "RENDER RATHER THAN A GUESS. More adapter strength should pull the eye "
        "further toward the reference's proportions -- the residual is size "
        "and the reference has the right size -- while pulling the HEAD "
        "further toward a reference that is 100% head. k1 already moved "
        "head_frac 0.181 -> 0.219 and T8 5.56 -> 4.57 against a 4.5 bar, so "
        "there is 0.07 heads of room and 0.9 will probably spend it.\n\n"
        "IF THAT IS WHAT HAPPENS IT IS NOT A DEAD END, it is a clean "
        "decomposition: the eye belongs to the adapter and the head belongs to "
        "the skeleton, and head_frac is a dial this tree has already proved it "
        "holds -- n5 moved it 0.190 -> 0.320 alone and manufactured a "
        "bobblehead on demand. The rung after would then be k2's scale with a "
        "PRE-SHRUNK authored head, one variable, and both clauses reachable at "
        "once.\n\n"
        "THE OUTCOME THAT WOULD STOP THIS ROUTE: containment breaks -- seated, "
        "purple cowl, or the tile's field -- or T1 regresses to pupils. Either "
        "means the strength that buys the face also buys the reference's "
        "composition, and the instrument has to become a FACE-only adapter "
        "(ip-adapter-plus-face, 847 MB, NOT cached on the box) or a tighter "
        "mask, both of which are a different spec."),
}


def emit(suffix, ip_scale, variable, force=False):
    job_dir = "jerryface-%s-0821" % suffix
    new_id = "ep2-jerry-face-%s-0821" % suffix
    child = derive_spec.derive(
        src=PARENT, new_id=new_id,
        fresh={"owner": "goblin reference-route lane, 2026-08-21",
               "why": WHY[suffix], "consumer": CONSUMER,
               "success": SUCCESS % ip_scale},
        overrides={"argv:--arm": ARM, "argv:--repo-commit": COMMIT,
                   "key:beat": 2, "key:priority": 28, "key:est_minutes": 4},
        retoken=[(PARENT_DIR_TOKEN, job_dir)],
        extra={"bar": BAR,
               "failure_predicted_in_advance": PREDICTED[suffix],
               "the_one_variable": variable,
               "the_rung_this_is_one_variable_from": PARENT_RUNG[suffix],
               "one_sample_rule": ONE_SAMPLE[suffix],
               "ip_adapter":
                   {"ref": "farm-out/jerry-skel-assets-0820/%s.png" % REF,
                    "ref_sha256": REF_SHA,
                    "ref_provenance":
                        "review/ep2-goblin-design-0819/adult-b19-0819.jpg "
                        "cropped (176,280)-(332,432), 156x152, no resample",
                    "mask": IP_MASK,
                    "mask_frame": "RENDER pixels, 832x1216",
                    "scale": ip_scale,
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
            "--ip-scale", ip_scale,
        ] + argv[i:]

    child["steps"][0] = {"name": "stage",
                         "argv": [r"C:\banyan-farm\venv\Scripts\python.exe",
                                  "-c", stage_step(job_dir)]}
    child["steps"][-1] = {"name": "publish",
                          "argv": [r"C:\banyan-farm\venv\Scripts\python.exe",
                                   "-c", publish_step(job_dir, new_id)]}
    child["artifacts"] = [
        r"C:\banyan-farm\%s\out\%s-%s.png" % (job_dir, new_id, ARM)]

    render = [s for s in child["steps"] if s["name"] not in ("stage", "publish")]
    assert len(render) == 1, [s["name"] for s in render]
    argv = [str(a) for a in render[0]["argv"]]
    for flag, val in (("--ip-ref", "pipeline/control/%s.png" % REF),
                      ("--ip-mask", IP_MASK),
                      ("--ip-ref-sha256", REF_SHA),
                      ("--ip-scale", ip_scale),
                      ("--seed", "20260823"),
                      ("--scale", "1.0"),
                      ("--arm", ARM),
                      ("--repo-commit", COMMIT)):
        assert argv.count(flag) == 1, (flag, argv.count(flag))
        assert argv[argv.index(flag) + 1] == val, (flag, argv[argv.index(flag) + 1])
    joined = " ".join(argv)
    assert job_dir in joined and PARENT_DIR_TOKEN not in joined

    out = "pipeline/jobs/%s.yaml" % new_id
    derive_spec.write(child, out, force=force)
    derive_fetch_guard.assert_fetch_urls_resolve(
        os.path.join(REPO, out),
        must_hold=("controlnet_plate.py", HINT + ".png", REF + ".png"))
    print("wrote", out)


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("-")]
    force = "--force" in sys.argv[1:]
    for suffix, ip_scale, variable in RUNGS:
        if want and suffix not in want:
            continue
        emit(suffix, ip_scale, variable, force=force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
