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
import subprocess
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
# k3's reference: the SAME head, placed on flat field green at the tile's
# measured standing head_frac 0.190, at the crown row the render draws. Built
# by pipeline/author_jerry_headfit_ref_0821.py.
REF_FIT = "jerry-tile-headfit-0821"
REF_FIT_SHA = "91087e527189e63c8c6ad95e5000c5c108bf943ac35c485a5659f652098ae7fd"
# k4's references: SQUARE, because diffusers hands every reference to a
# CLIPImageProcessor() built with no arguments, whose defaults resize the
# SHORT edge to 224 and then CENTRE CROP to 224x224. k3's 416x608 portrait
# canvas therefore lost the top 30% of its subject -- the whole cranial dome --
# before the encoder saw it, and what survived was 5.4% of the encoder's
# pixels flush against row 0. A square canvas makes that crop a NO-OP, which
# is the only condition under which an authored head-to-frame ratio is the
# ratio the model receives. Built by pipeline/author_jerry_squareref_0821.py,
# which prints the encoded bbox and refuses any reference touching an edge.
# Sources: pipeline/research/ipa-ref-framing-0821.md
REF_SQ = {
    "k4a": ("jerry-tile-sq30-0821", "0.30", "8.8",
            "7642513d4e27ebf5897c8c4669f519cfa2db8d3332e5d711d26a04d118ea1cff"),
    "k4b": ("jerry-tile-sq45-0821", "0.45", "19.7",
            "7f24dd5e2c1e9956ae71283b6d4bc50a1c504885a5dae2c940a2280b3f539703"),
    "k4c": ("jerry-tile-sq60-0821", "0.60", "35.2",
            "8752cd49228b0c7ba19a6f541e418beb60fc380290459a2c586d7e46b95c71c8"),
    "k4d": ("jerry-tile-sq75-0821", "0.75", "55.5",
            "f34963347215abc42ab66c8928d48132c32ae9409b0fe5babcb2e65a432837d0"),
    # k5 walks the SAME axis BELOW k4a, which is where the band's own monotonic
    # trend puts an eye between k3's 1.24x and k4a's 1.41x -- without the cut.
    # k5b at 3.9% sits BELOW k3's 5.4% on a square canvas ON PURPOSE.
    "k5a": ("jerry-tile-sq25-0821", "0.25", "6.1",
            "02755eb533c45efa12656bbd87062789fa4b5d44fbbf57cd031c06ab833df2d7"),
    "k5b": ("jerry-tile-sq20-0821", "0.20", "3.9",
            "f65c9bb412e541fbe9b6024ddaec5a78b78028afd87e325baa06d6d430dded14"),
}
REFS = {"jerry-tile-head-0821": REF_SHA,
        "jerry-tile-headfit-0821": REF_FIT_SHA}
REFS.update({name: sha for name, _f, _c, sha in REF_SQ.values()})
IP_MASK = "315,130,515,350"
ARM = "ipahead"

# (suffix, --ip-scale, the one variable). k2 was filed AFTER k1 was looked at,
# which is the one-sample rule satisfied rather than skipped: k1 is the first
# sample on this instrument and k2 is one variable from it.
RUNGS = [
    ("k1", "0.7", REF,
     "the IP-Adapter itself, at the diffusers masking-example default 0.7 -- "
     "the value ep2-b08-ipamask-0819 ran at. Prompt, negative, skeleton, "
     "--scale and seed are j2's, unchanged."),
    ("k2", "0.9", REF,
     "k1's frame with --ip-scale 0.7 -> 0.9 and NOTHING else. k1 bought the "
     "tile's eye KIND (aspect 0.54 against the tile's 0.52, where six wording "
     "rungs sat at 1.0-1.26) and its brow, and did NOT buy SIZE: k1's eye "
     "bounding box is 1.87x the tile's relative to the head, where j2's was "
     "1.40x. Wrong size, right kind. Strength is the dial that decides how far "
     "the frame is pulled toward the reference's proportions, and it is the "
     "only lever that is one variable from here."),
    ("k3", "0.7", REF_FIT,
     "k1's rung with ONE thing changed: the reference's HEAD-TO-FRAME RATIO, "
     "100% -> 19.1%. Same head pixels, same mask, same 0.7, placed on flat "
     "field green at the tile's measured standing head_frac of 0.190 and at "
     "the crown row the render draws. k2 closed the strength lever -- 0.7 to "
     "0.9 moved eye AREA by 1.6% relative, which is nothing, moved eye ASPECT "
     "the WRONG way (0.54/0.46 -> 0.63/0.71, away from the tile's 0.52) and "
     "spent the last of T8 (4.57 -> 4.41 heads, under the 4.5 bar). So the "
     "adapter supplies KIND and saturates by 0.7, and SIZE is not on that "
     "axis. What BOTH k rungs did do is inflate the head: 0.181 -> 0.219 -> "
     "0.227 head_frac. One cause explains the oversized head AND the oversized "
     "eye -- the reference is a head crop, so what the adapter was shown is a "
     "head that fills a frame."),
]

# ---------------------------------------------------------------------------
# k4: THE BAND, ON A SQUARE CANVAS. Four rungs, ONE axis, everything else
# frozen at k3's. This is a SWEEP on a diagnostic axis, not a batch of
# production frames: nothing it produces is promoted without being judged, and
# it exists because the public answer ("make it square, make the subject
# dominant") brackets our band without picking a point inside it.
for _sfx in ("k4a", "k4b", "k4c", "k4d", "k5a", "k5b"):
    _name, _frac, _cov, _sha = REF_SQ[_sfx]
    RUNGS.append((
        _sfx, "0.7", _name,
        "k3's rung with the reference CANVAS MADE SQUARE and the head at "
        "%s of it -- the head-to-frame ratio is the axis and it is the only "
        "thing that moves across k4a..k4d. Same head pixels, same field "
        "green, same mask, same --ip-scale 0.7, same seed, same skeleton, "
        "same wording. The subject reaches the encoder INTACT at %s%% of its "
        "pixels, where k3's reached it amputated at 5.4%%." % (_frac, _cov)))
# the commit that carries the three staged inputs -- provenance only, but the
# meta.yaml this writes is what a later lane reads to re-fetch them.
COMMIT = "29939faba45625c647bb05da9573c4151b8b259d"


def stage_step(job_dir, ref):
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
        % (ASSET_URL, job_dir, DRIVER_SHA, HINT, HINT_SHA, ref, REFS[ref]))


def publish_step(job_dir, new_id, ref):
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
        % {"d": job_dir, "id": new_id, "arm": ARM, "hint": HINT, "ref": ref})


BAR_K4 = """EVERY CLAUSE k3 PASSED, HELD, PLUS THE TWO IT FAILED ON. k3 is the
incumbent and this rung replaces it or it does not ship: nine clauses held, and
a regression on any of them is a FAIL even if the two new ones pass.
Ruler: pipeline/measure_face_eye_0821.py, whose --selftest reproduces the
published f/g/h numbers before it is allowed to produce a new one.
  READ THE RULER'S KNOWN ARTIFACT BEFORE QUOTING IT. Its WHITE_MIN is 190 and
  k3's eyes render to a dimmer cream that falls under it, so the AREA column
  read 0.0040 on a face with two plain eyes. The threshold is calibrated
  against five published rungs and IS NOT MOVED to flatter a sixth. THE
  BOUNDING-BOX COLUMN IS WHAT THIS BAR IS SCORED ON, and any area figure is
  quoted at both 190 and 170 with the pair shown.
THE TWO NEW CLAUSES, and they are why the rung exists:
  NO HORNS. No spike, prong, antler or protrusion off the skull. k3 grew two.
       This is a creature-feature fail and it is judged BY EYE at 1:1 -- the
       pale-above-dome proxy separates k1 (0.04%) from k3 (0.90%) but reads
       0.39% on horn-free k2, so it corroborates and does not decide.
  NO COWL. The tile's purple cowl-scarf must not appear at the neck.
       Containment break #2 of the three named on k1; it fired on k3.
THE SIZE CLAUSES, which are the ones this axis is supposed to move:
  T1b  SHAPE -- per-eye aspect (h/w). TILE 0.52; k1 0.54, k3 0.54. Hold it.
       SIZE -- eye bounding box relative to the head box, against the tile.
       j2 1.40x, k1 1.87x, k2 2.32x, k3 1.24x. PASS is 1.4x or lower, which
       means k3's 1.24x is the number to beat and j2's 1.40x is the floor.
  T8   4.5+ heads. j2 5.56, k1 4.57, k2 4.41 FAIL, k3 4.97. Scored first.
HELD FROM k3, all nine: T1 no iris and no pupil, T2 no nose bridge, T3 no age
modelling, P1 the brow bar with skin between it and the eye (a lash arc welded
to the rim is an eyelid and does not count), P2 muzzle, P3 a mouth line, P4
facial shading, plus the standing pose and the patchwork cloak in tall grass."""

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

PARENT_RUNG = {"k1": "ep2-jerry-face-j2-0821",
               "k2": "ep2-jerry-face-k1-0821",
               "k3": "ep2-jerry-face-k1-0821"}
PARENT_RUNG.update({s: "ep2-jerry-face-k3-0821"
                    for s in ("k4a", "k4b", "k4c", "k4d")})
# k5's parent is k4a, the low end of the band it extends downward.
PARENT_RUNG.update({s: "ep2-jerry-face-k4a-0821" for s in ("k5a", "k5b")})

REF_PROVENANCE = {
    "jerry-tile-head-0821":
        "review/ep2-goblin-design-0819/adult-b19-0819.jpg cropped "
        "(176,280)-(332,432), 156x152, no resample. The head fills the "
        "reference.",
    "jerry-tile-headfit-0821":
        "the SAME crop, its cream sky flooded to the tile's own field green "
        "and placed on a 416x608 field-green canvas at head height 116 px = "
        "0.191 of frame, crown at 0.093 -- the tile's MEASURED standing "
        "head_frac and the render's own crown row. Built by "
        "pipeline/author_jerry_headfit_ref_0821.py.",
}
REF_PROVENANCE.update({
    name: (
        "the SAME head crop and the same flooded field green as k3's "
        "reference, on a SQUARE %dx%d canvas with the head at %s of frame, "
        "CENTRED on both axes. Square because diffusers builds "
        "CLIPImageProcessor() with no arguments and its defaults resize the "
        "SHORT edge to 224 and then CENTRE CROP to a square: on a square "
        "canvas that crop is a NO-OP, so the authored ratio is the ratio "
        "encoded. The subject reaches the encoder INTACT at %s%% of its "
        "pixels. k3's 416x608 portrait lost the top 30%% of its subject -- "
        "the whole cranial dome -- and delivered 5.4%%. Built by "
        "pipeline/author_jerry_squareref_0821.py; evidence "
        "review/ep2-goblin-design-0819/CLIP-STARVE-0821.png; sources "
        "pipeline/research/ipa-ref-framing-0821.md."
        % (448, 448, frac, cov))
    for name, frac, cov, _sha in REF_SQ.values()})

CONSUMER = ("THE JERRY LoRA'S LAST OPEN GATE. train-jerry-0820 is UNFILED and "
            "stays that way until a rung passes T1b and P1 with T1/T3/T8/P3/P4 "
            "intact; the set is still 7 frames in 4 poses. No beat plate, no "
            "pick, nothing promoted.")

SUCCESS = ("ONE 832x1216 png at seed 20260823 on the h19 skeleton at scale "
           "1.0, j2's prompt and negative byte-identical, plus --ip-ref "
           "jerry-tile-head-0821.png --ip-mask 315,130,515,350 --ip-scale %s. "
           "Scored on T1b (area AND aspect) and P1 with T1, T3, T8, P3, P4 "
           "held and the standing/cloak/grass containment scored.")

SUCCESS_K4 = ("ONE 832x1216 png at seed 20260823 on the h19 skeleton at scale "
              "1.0, j2's prompt and negative byte-identical, plus --ip-ref "
              "%s.png --ip-mask 315,130,515,350 --ip-scale %s. Scored on the "
              "k4 bar: k3's nine passing clauses HELD, plus NO HORNS and NO "
              "COWL, with the eye bounding box at 1.4x the tile's or lower "
              "and T8 at 4.5 heads or better. Judged by eye at 1:1 against "
              "review/ep2-goblin-design-0819/adult-b19-0819.jpg, with the "
              "ruler's bounding-box column -- not its area column -- carrying "
              "the numbers.")

ONE_SAMPLE = {
    "k1": ("ONE rung. The wording ladder's stop names IP-Adapter as the route "
           "and this is the first sample on it; no scale sweep, no second "
           "reference, no second seed until this one has been looked at."),
    "k2": ("ONE rung, filed AFTER k1 was rendered, measured and read at 1:1 -- "
           "the rule satisfied rather than skipped. NOT a scale sweep: 0.9 is "
           "the single next value, and if it splits T1b from T8 the answer is "
           "a head_frac edit on top, not three more scales."),
    "k3": ("ONE rung, filed after k1 AND k2 were rendered, measured and read "
           "at 1:1. It is not a third guess on the same axis -- k2 CLOSED the "
           "strength axis, and this is the first rung on the axis both k rungs "
           "pointed at by inflating the head. Three outcomes are named in "
           "advance and none of their follow-ups is filed, because the last "
           "prediction this lane filed was falsified within the hour."),
}

WHY["k3"] = (
    "RUNG k3: k1's rung with the reference's HEAD-TO-FRAME RATIO changed from "
    "100% to 19.1% and nothing else.\n\n"
    "WHAT k2 CLOSED. Strength is not the size dial. 0.7 -> 0.9 moved eye AREA "
    "0.0566 -> 0.0557, which is 1.6% relative and is noise; moved eye ASPECT "
    "0.54/0.46 -> 0.63/0.71, i.e. AWAY from the tile's 0.52; and spent the "
    "last of T8, 4.57 -> 4.41 heads against a 4.5 bar. Every effect of more "
    "strength landed on composition and none on the residual. The prediction "
    "filed with k2 got the T8 half right and the eye half WRONG, and the eye "
    "half is the one that mattered.\n\n"
    "WHAT BOTH k RUNGS DID DO IS INFLATE THE HEAD: head_frac drawn 0.181 (j2, "
    "no adapter) -> 0.219 (k1) -> 0.227 (k2), against a 0.190 authored "
    "skeleton. ONE CAUSE EXPLAINS THE OVERSIZED HEAD AND THE OVERSIZED EYE: "
    "the reference is a head CROP, so what the adapter was shown is a head "
    "that fills a frame, and a mask says WHERE the adapter acts, not how big "
    "the thing it draws should be. k3 shows it the same head at the size a "
    "head should occupy in a full-body frame.")

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
    "k3": (
        "IF THE RATIO IS THE CAUSE, both defects move together: head_frac back "
        "toward 0.190 with T8 back over 4.5, and the eye down from 1.87x the "
        "tile's relative bounding box, while the brow and the 0.54 aspect "
        "survive because the head pixels are unchanged.\n\n"
        "IF ONLY T8 MOVES and the eye stays at 1.87x, then the eye is not "
        "downstream of the ref's framing and the remaining lever is the "
        "CHECKPOINT's own eye prior -- which no reference route reaches, and "
        "the honest answer becomes that this face is trainable only from "
        "frames that already have it, i.e. the seven mac-plate keeps plus "
        "whatever k1 can be cropped to yield.\n\n"
        "IF THE FACE GOES BACK TO j2's, the adapter needed the head to fill "
        "the reference in order to bite at all, and the route is a face-only "
        "adapter (ip-adapter-plus-face, 847 MB, NOT cached) rather than a "
        "reframed reference.\n\n"
        "THE THING I AM NOT DOING is filing all three of those now. k2 "
        "falsified a prediction of mine an hour old; the next rung after this "
        "one gets authored off what k3 shows, not off which of these three I "
        "currently believe."),
}


# ---------------------------------------------------------------------------
# k4's text. The four rungs share it deliberately: they are ONE experiment with
# four points on it, and writing four different justifications for one axis
# would be pretending each was reasoned separately.
_K4_WHY_HEAD = (
    "RUNG %s OF THE k4 BAND: k3's rung with the reference canvas made SQUARE "
    "and the head at %s of it. One axis, four points, everything else frozen "
    "at k3's.\n\n"
    "WHAT k3 ESTABLISHED AND WHAT IT BROKE. k3 changed the reference's "
    "head-to-frame ratio 100%% -> 19.1%% and moved both defects at once: eye "
    "bounding box 1.87x -> 1.24x the tile's, the best this tree has made, "
    "with aspect held at 0.54, and head_frac 0.219 -> 0.201 with T8 back to "
    "4.97 heads. AND IT GREW TWO HORNS and let the tile's purple cowl "
    "through.\n\n"
    "THE CAUSE, RESEARCHED RATHER THAN GUESSED, AND IT IS NOT THE ONE THE k3 "
    "ENTRY NAMED. diffusers' load_ip_adapter builds `CLIPImageProcessor()` "
    "with NO arguments, and that class defaults to resizing the SHORT edge to "
    "224 and then CENTRE CROPPING to 224x224. k3's reference was 416x608, so "
    "it became 224x327 and the crop kept rows 51..275 -- while the head sat "
    "at resized rows 33..93. THE TOP 30%% OF THE SUBJECT, THE ENTIRE CRANIAL "
    "DOME, WAS CUT OFF BEFORE THE ENCODER SAW IT, leaving 64x42 px flush "
    "against row 0 with the tile's dark ear flanges running up into the cut. "
    "k1's reference was 156x152, effectively square, survived the crop intact "
    "at 96%% coverage, and drew no horns. The horns grow upward out of the "
    "cut, from exactly those flanges. Sources and the two source files this "
    "is read from: pipeline/research/ipa-ref-framing-0821.md. Pixels: "
    "review/ep2-goblin-design-0819/CLIP-STARVE-0821.png.\n\n"
    "SO THE CANVAS IS SQUARE HERE, which makes the centre crop a NO-OP and is "
    "the only condition under which the authored head-to-frame ratio is the "
    "ratio the model actually receives. On k3 it was not.")

_K4_SAMPLE = (
    "A SWEEP ON A DIAGNOSTIC AXIS, filed after k1, k2 and k3 were each "
    "rendered, measured and read at 1:1 -- four points on ONE axis, not four "
    "guesses. It is not a batch in the sense the rule bans: nothing it "
    "produces is promoted, no dataset grows, no beat plate is cut, and the "
    "gate stays shut until a rung is judged. Four points and not one because "
    "the public answer is a DIRECTION -- square canvas, dominant subject -- "
    "and does not name a ratio; the band 30-75%% brackets k3's 19.1%% below "
    "and k1's ~100%% above, and both of those are already rendered, so the "
    "sweep has anchors at both ends and buys the curve between them. If a "
    "single rung had been filed instead, whichever way it came back the next "
    "question would have been 'and what about the other side', which is the "
    "same GPU spent over four sequential waits.")

_K4_PREDICTED = (
    "THE HORN IS THE THING BEING TESTED AND THERE ARE TWO CANDIDATE CAUSES, "
    "which this band separates because a square canvas removes ONE of them "
    "while leaving the other free to vary.\n\n"
    "IF THE CUT WAS THE CAUSE -- a truncated skull completed past its "
    "truncation -- then ALL FOUR come back horn-free, including k4a at 8.8%% "
    "coverage, and the eye/head numbers trace a clean curve against ratio "
    "that k3's 19.1%% and k1's ~100%% already bracket.\n\n"
    "IF STARVATION WAS THE CAUSE -- a weakly-encoded subject completed from "
    "the checkpoint's priors -- then k4a horns and k4c/k4d do not, and the "
    "horn-free threshold is a coverage number this band measures.\n\n"
    "AND THE OUTCOME THAT COSTS ME THE RESULT I LIKE, WRITTEN BECAUSE IT IS "
    "THE LIKELIEST WAY THIS DISAPPOINTS: k3's best-yet eye may be an ARTIFACT "
    "OF A CRIPPLED EMBEDDING rather than a ratio effect. A starved adapter "
    "transfers less of everything, including less of the oversized-eye bias "
    "k1 showed at full strength. If that is what happened, the eye box climbs "
    "back toward k1's 1.87x as coverage rises, the horn and the good eye turn "
    "out to be the SAME defect seen twice, and no point on this axis passes "
    "both -- which retires the reference-framing route for SIZE and leaves "
    "the eye to a face-variant adapter or to the seven mac-plate keeps.\n\n"
    "WHAT I AM NOT FILING: the follow-up. Whichever of these three the band "
    "shows, the next rung gets authored off the pixels. This lane has had a "
    "prediction falsified once already on this ladder and the correction is "
    "to name outcomes in advance, not to pre-commit to a response.")

for _s in ("k4a", "k4b", "k4c", "k4d"):
    WHY[_s] = _K4_WHY_HEAD % (_s, REF_SQ[_s][1])
    ONE_SAMPLE[_s] = _K4_SAMPLE
    PREDICTED[_s] = _K4_PREDICTED

# ---------------------------------------------------------------------------
# k5: the same axis, BELOW k4a. Not a new idea -- an extrapolation from four
# measured points, which is why it is filed rather than named and held.
_K5_WHY = (
    "RUNG %s: k4a's rung with the square reference's head at %s of frame "
    "instead of 0.30. Same axis, one variable, everything else frozen.\n\n"
    "WHAT THE k4 BAND ESTABLISHED. On a SQUARE canvas the centre crop is a "
    "no-op and all four rungs came back HORN-FREE and COWL-FREE, including "
    "k4a at 8.8%% encoder coverage. The horn was never smallness -- it was "
    "k3's 416x608 PORTRAIT reference losing the top 30%% of its subject, the "
    "whole cranial dome, to CLIPImageProcessor's centre crop, with the horns "
    "growing upward out of that cut.\n\n"
    "AND WHAT IT COST. Eye size rose monotonically with coverage across the "
    "band -- 1.41x, 1.70x, 1.94x, 2.10x the tile's relative bounding box -- "
    "with aspect rounding off from 0.59 to 0.86 against the tile's 0.52. So "
    "k3's best-in-tree 1.24x was a crippled embedding transferring less of "
    "everything, and k4a at 1.41x merely ties what j2 draws with NO adapter.\n\n"
    "WHY BELOW 30%% IS THE NEXT PLACE TO LOOK AND NOT A GUESS. The axis is "
    "monotonic across four measured points and k4a sits at its low end. The "
    "trend puts an eye between k3's 1.24x and k4a's 1.41x below 30%% -- and "
    "there, unlike k3, the subject is INTACT. This rung is an extrapolation "
    "from the band, not a new idea about the mechanism.")

_K5_SAMPLE = (
    "TWO RUNGS EXTENDING A CHARACTERISED AXIS, filed after k1, k2, k3 and all "
    "four k4 rungs were rendered, measured and read at 1:1. The recipe has not "
    "changed -- same builder, same head pixels, same mask, same scale, same "
    "seed, same skeleton, same wording -- only the position on an axis whose "
    "shape is now known from four points. Nothing is promoted, no dataset "
    "grows, the gate stays shut, and both rungs are judged before anything "
    "downstream of them is authored.")

_K5_PREDICTED = (
    "THE TREND SAYS the eye box lands between k3's 1.24x and k4a's 1.41x, "
    "aspect improves back toward the tile's 0.52 from k4a's 0.59, and "
    "head_frac drifts a little under the 0.190 authored from k4a's 0.195 -- "
    "T8 has 0.6 heads of room above the 4.5 bar so it is not the clause at "
    "risk.\n\n"
    "k5b IS ALSO A FALSIFICATION TEST AND THAT IS WHY IT IS THE LOWER OF THE "
    "TWO. At 3.9%% encoder coverage it sits BELOW k3's 5.4%%, on a square "
    "canvas. The k4 reading says the horn was the CUT and that starvation "
    "alone does not grow one. IF k5b COMES BACK WITH A HORN, that reading is "
    "wrong -- coverage has a floor and the horn is a starvation effect after "
    "all -- and the honest consequence is that the usable window is pinched "
    "between a horn floor and an eye-size ceiling, which would retire the "
    "reference route for SIZE outright.\n\n"
    "IF BOTH COME BACK CLEAN AND NEITHER BEATS 1.4x, the axis is exhausted: "
    "every point on it has been measured, none passes, and the eye belongs to "
    "an instrument this route does not contain. I am not filing what that "
    "instrument is, because the band has already falsified one confident "
    "reading from this lane tonight.")


for _s in ("k5a", "k5b"):
    WHY[_s] = _K5_WHY % (_s, REF_SQ[_s][1])
    ONE_SAMPLE[_s] = _K5_SAMPLE
    PREDICTED[_s] = _K5_PREDICTED


def emit(suffix, ip_scale, ref, variable, force=False):
    job_dir = "jerryface-%s-0821" % suffix
    new_id = "ep2-jerry-face-%s-0821" % suffix
    child = derive_spec.derive(
        src=PARENT, new_id=new_id,
        fresh={"owner": "goblin reference-route lane, 2026-08-21",
               "why": WHY[suffix], "consumer": CONSUMER,
               "success": (SUCCESS_K4 % (ref, ip_scale)
                           if suffix[:2] in ("k4", "k5") else SUCCESS % ip_scale)},
        overrides={"argv:--arm": ARM, "argv:--repo-commit": COMMIT,
                   "key:beat": 2, "key:priority": 28, "key:est_minutes": 4},
        retoken=[(PARENT_DIR_TOKEN, job_dir)],
        extra={"bar": BAR_K4 if suffix[:2] in ("k4", "k5") else BAR,
               "failure_predicted_in_advance": PREDICTED[suffix],
               "the_one_variable": variable,
               "the_rung_this_is_one_variable_from": PARENT_RUNG[suffix],
               "one_sample_rule": ONE_SAMPLE[suffix],
               "ip_adapter":
                   {"ref": "farm-out/jerry-skel-assets-0820/%s.png" % ref,
                    "ref_sha256": REFS[ref],
                    "ref_provenance": REF_PROVENANCE[ref],
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
            "--ip-ref", "pipeline/control/%s.png" % ref,
            "--ip-mask", IP_MASK,
            "--ip-ref-sha256", REFS[ref],
            "--ip-scale", ip_scale,
        ] + argv[i:]

    child["steps"][0] = {"name": "stage",
                         "argv": [r"C:\banyan-farm\venv\Scripts\python.exe",
                                  "-c", stage_step(job_dir, ref)]}
    child["steps"][-1] = {"name": "publish",
                          "argv": [r"C:\banyan-farm\venv\Scripts\python.exe",
                                   "-c", publish_step(job_dir, new_id, ref)]}
    child["artifacts"] = [
        r"C:\banyan-farm\%s\out\%s-%s.png" % (job_dir, new_id, ARM)]

    render = [s for s in child["steps"] if s["name"] not in ("stage", "publish")]
    assert len(render) == 1, [s["name"] for s in render]
    argv = [str(a) for a in render[0]["argv"]]
    for flag, val in (("--ip-ref", "pipeline/control/%s.png" % ref),
                      ("--ip-mask", IP_MASK),
                      ("--ip-ref-sha256", REFS[ref]),
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
        must_hold=("controlnet_plate.py", HINT + ".png", ref + ".png"))
    print("wrote", out)


USAGE = """usage: derive_jerry_face_ipa_0821.py [RUNG ...] [--force]

Emits the IP-Adapter face rungs derived from %s.
With no RUNG argument it emits EVERY rung that is not already committed.

  RUNG     one or more of: %s
  --force  rewrite a rung whose spec is already committed

WHY --force EXISTS, and it was added the hard way. Running this file with no
arguments used to rewrite EVERY spec in RUNGS, including rungs that had already
been rendered, judged and published -- replacing their `why` and `bar` with
today's narrative and silently editing the record of what a finished rung was
scored against. derive_spec.write() has an anti-overwrite guard, but it keys on
a SCORED key in the target, and this family deliberately keeps verdicts OUT of
specs by allow-list, so no spec here is ever scored and the guard could never
fire. A committed spec is a published rung whether or not it carries a score,
so that is what this checks instead.
""" % (PARENT, ", ".join(s for s, _, _, _ in RUNGS))


def _is_committed(rel):
    """True if git tracks this path. A tracked spec is a published rung."""
    try:
        r = subprocess.run(["git", "-C", REPO, "ls-files", "--error-unmatch",
                            rel], capture_output=True, text=True,
                           encoding="utf-8")
        return r.returncode == 0
    except OSError:
        # No git is not a licence to overwrite; treat it as "assume published".
        return True


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(USAGE)
        return 0
    want = [a for a in args if not a.startswith("-")]
    force = "--force" in args
    known = {s for s, _, _, _ in RUNGS}
    unknown = [w for w in want if w not in known]
    if unknown:
        print("!! unknown rung(s): %s\n%s" % (", ".join(unknown), USAGE),
              file=sys.stderr)
        return 2
    wrote = skipped = 0
    for suffix, ip_scale, ref, variable in RUNGS:
        if want and suffix not in want:
            continue
        rel = "pipeline/jobs/ep2-jerry-face-%s-0821.yaml" % suffix
        if _is_committed(rel) and not force:
            print("  skip %s -- already committed. It is a published rung and "
                  "rewriting it would edit the record of what it was judged "
                  "against. Pass --force if that is genuinely the intent."
                  % rel)
            skipped += 1
            continue
        emit(suffix, ip_scale, ref, variable, force=force)
        wrote += 1
    print("%d written, %d left alone" % (wrote, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
