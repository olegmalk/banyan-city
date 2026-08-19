#!/usr/bin/env python3
r"""Derive beat 20's plate-publish and motion specs from the beat-14 pair that worked.

WHY DERIVE INSTEAD OF WRITE. Beat 14 shipped a motion take on 2026-08-18 from a
Mac-drawn plate, and the route it used is the only one in this repo that has
actually delivered a mac plate to the 5090:

    ep2-b14-mac-plate-0818     commit the png into farm-out/ ON MAIN (NOT under
                               takes/, which .gitignore:40 ignores), fetch it on
                               the box by raw with a per-file sha256 assertion,
                               publish it into a farm-out directory ONE spec owns
    ep2-b14-motion-crf10-0819  crop that published plate to 704x1280 with the sha
                               re-asserted, encode, render 121 frames at
                               --image-crf 10, stamp, publish

Both halves of that are guard-shaped rather than incidental: box_enqueue refuses a
motion job whose --src it cannot fetch from origin/farm-results-rtx5090, and
refuses again if it cannot name the single spec that published it. Beat 12 spent
two failed runs and two refusals tonight learning that the hard way.

SO THIS SCRIPT CHANGES AS LITTLE AS IT CAN. Every sampler number, the offload
mode, the two-stage flag, the frame count, the size and the fps are carried from
the beat-14 motion parent unchanged; cover_crop.py is carried BYTE-FOR-BYTE;
stamp_sidecar.py is carried with the job id and the note substituted, because a
sidecar naming the wrong job is a provenance defect. What is new is the init, the
two prompt files, the seed, and the bar -- and the bar is written here, in this
file, BEFORE the render exists.

Usage:  python3 pipeline/derive_b20_motion_0819.py
"""
import os
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = os.path.join(REPO, "pipeline", "jobs")

PLATE_PARENT = os.path.join(JOBS, "ep2-b14-mac-plate-0818.yaml")
MOTION_PARENT = os.path.join(JOBS, "ep2-b14-motion-crf10-0819.yaml")

SHIP_ID = "ep2-b20-plateship-0819"
MOTION_ID = "ep2-b20-motion-0819"

PLATE_PNG = "20-evidence-mac-plate-r1s1.png"
PLATE_YAML = "20-evidence-mac-plate-r1s1.yaml"
PNG_SHA = "4b87cf4f40772af7942077e9a1c30198aa78aaeac70b9a26dda5808d9a04d119"
YAML_SHA = "3d9465a4f231b132ad84f78c0ff4b36f6cf1bb4b5ee35c4b86cadccb230ce6f4"
REPO_DIR = "farm-out/ep2-b20-mac-plate-0819"

CLIP = "20-evidence-LTX-macplate-r1s1.mp4"
SEED = 20260819

# The approved staging, 2026-08-17 (shots.md "KNEE-HEIGHT REWRITE", node.md:132):
#   "The scavenger crouches back down, picks the fig up with both hands, and looks
#    from it to the sapling's thinnest branch beside him -- level with his face
#    now, and bare."
# The style tail is the beat-14 motion parent's, character for character, because
# that is the tail that has been rendered on a mac plate on this card.
MOTION_PROMPT = (
    "Still crouched low in the grass, he picks the fig up with both hands, then "
    "looks from it across to the thin bare stem of the small sapling beside him, "
    "level with his face. 2D anime, hand-drawn cel animation, flat cel shading, "
    "clean ink linework, anime key art, cinematic lighting, detailed, newest, "
    "masterpiece, best quality, very aesthetic.\n")

# The parent's negative, unchanged, plus four bans this beat's own ruling earns:
# standing is the word that broke the staging ("straightens" put a mature limb
# overhead), and the child/chibi bans hold the adult read the plate has.
MOTION_NEGATIVE = (
    "camera pan, camera tilt, zoom, dolly, push in, pull back, tripod, cut to "
    "another shot, scene change, different location, split screen, still image, "
    "freeze frame, standing up, straightening, rising to his feet, child, chibi, "
    "girl, baby, second fruit, extra fruit\n")


def literal(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


class Dumper(yaml.SafeDumper):
    pass


Dumper.add_representer(str, literal)


def dump(spec, path, header):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header)
        yaml.dump(spec, fh, Dumper=Dumper, sort_keys=False, width=104,
                  allow_unicode=True, default_flow_style=False)


def load(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def payload_of(spec, basename):
    for k, v in (spec.get("payload") or {}).items():
        if k.rsplit("\\", 1)[-1] == basename:
            return v
    sys.exit("!! %s not in parent payload -- refusing to guess." % basename)


def step_of(spec, name):
    for st in spec.get("steps") or []:
        if st.get("name") == name:
            return st
    sys.exit("!! parent has no %r step -- refusing to invent one." % name)


def sub(text, pairs, where):
    """Substitute every pair, and REFUSE if one of them matched nothing.

    A substitution that silently matches nothing is how a derived spec ends up
    naming its parent's directories and publishing another job's frames under its
    own name -- box_enqueue.output_path_problems exists because that happened.
    """
    for old, new in pairs:
        if old not in text:
            sys.exit("!! %s: %r not found, so the clone is not what it claims." % (where, old))
        text = text.replace(old, new)
    return text


plate_parent = load(PLATE_PARENT)
motion_parent = load(MOTION_PARENT)

PY = r"C:\banyan-farm\venv\Scripts\python.exe"
VIDEO_PY = r"C:\banyan-video\venv\Scripts\python.exe"
LTX = r"C:\banyan-farm\banyan-city\pipeline\ltx_i2v.py"
COURIER = r"C:\banyan-farm\courier-box\farm-out"

# ---------------------------------------------------------------- plate publish
fetch_py = '''#!/usr/bin/env python3
"""Fetch beat 20's picked plate and its sidecar, refusing on any sha mismatch.

No model, no GPU, no spend. Modelled on ep2-b14-mac-plate-0818's fetch step,
which is the ONE route in this repo that has actually carried a Mac-drawn plate
to this card (08-18, rc=0), with the same refusal semantics: both files named in
full, a sha256 asserted per file BEFORE anything is written, a mismatch is a
nonzero exit rather than a partial success.

THE URL IS UNDER farm-out/ AND THAT IS THE WHOLE TRICK. Beat 12's job failed
twice tonight with HTTP 404 fetching a plate from under genomes/.../takes/,
because .gitignore:40 is `genomes/*/nodes/*/takes/**/*.png` -- those pngs are
untracked by design and main has never carried one. farm-out/ is not ignored, the
plate was committed there, and raw serves it at the sha asserted below.
"""
import hashlib, os, sys, urllib.request

OUT = r"C:\\banyan-farm\\%s-out"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/%s/")
UA = {"User-Agent": "banyan-city-b20-motion/1.0 (albert.numbro@gmail.com)"}
WANT = [
    ("%s",
     "%s"),
    ("%s",
     "%s"),
]
os.makedirs(OUT, exist_ok=True)
for name, want in WANT:
    raw = urllib.request.urlopen(
        urllib.request.Request(RAW + name, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %%s -- refusing.\\n   want %%s\\n   have %%s"
                 %% (name, want, have))
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %%-34s %%8d bytes  sha %%s  OK" %% (name, len(raw), have), flush=True)
print("both files match their asserted sha256.", flush=True)
''' % (SHIP_ID, REPO_DIR, PLATE_PNG, PNG_SHA, PLATE_YAML, YAML_SHA)

ship_publish = '''# EVERY FILE IS NAMED IN FULL, no glob. A glob that misses publishes nothing
# while returning a code that reads like a fetch failure, and
# box_enqueue.output_path_problems refuses a spec whose declared artifacts are
# never named by any step -- which a wildcard defeats. Missing ONE file is a
# FAIL of this job. No allow_fail anywhere in this spec.
import hashlib, os, shutil
from_dir = "C:/banyan-farm/%s-out"
dst = "C:/banyan-farm/courier-box/farm-out/%s"
NAMES = [
    "%s",
    "%s",
]
os.makedirs(dst, exist_ok=True)
lines = []
for name in NAMES:
    src = os.path.join(from_dir, name)
    if not os.path.isfile(src):
        raise SystemExit("!! missing %%s -- publishing nothing." %% name)
    shutil.copy2(src, dst)
    with open(os.path.join(dst, name), "rb") as fh:
        h = hashlib.sha256(fh.read()).hexdigest()
    lines.append(h + "  " + name)
with open(os.path.join(dst, "%s.sha256"), "w", newline="\\n") as fh:
    fh.write("\\n".join(lines) + "\\n")
print("published", len(NAMES), "file(s) + manifest ->", dst)
raise SystemExit(0)
''' % (SHIP_ID, SHIP_ID, PLATE_PNG, PLATE_YAML, SHIP_ID)

ship = {
    "id": SHIP_ID,
    "task": SHIP_ID,
    "node": "002b-first-citizen",
    "beat": 20,
    "runner": "box",
    "priority": 20,
    "needs_gpu": False,
    "max_attempts": 1,
    "sample": False,
    "owner": "beat 12/20 lane, 2026-08-19",
    "consumer": (
        "%s, which box_enqueue will refuse until its --src is a plate the guards can BOTH "
        "fetch from origin/farm-results-rtx5090 and attribute to one spec. That job in turn "
        "serves the EP2 CUT: beat 20 has no footage at all and is a slate on every cut we "
        "have made." % MOTION_ID),
    "success": (
        "Two files on farm-out/%s -- the picked plate and its provenance yaml -- each "
        "byte-identical to the copy committed on main in farm-out/%s, plus a sha256 manifest "
        "this job writes itself. The fetch REFUSES on any mismatch rather than continuing."
        % (SHIP_ID, os.path.basename(REPO_DIR))),
    "why": (
        "The plate exists and it is on the wrong machine. macbook1 drew 25 seeds of beat 20 "
        "today and they live only there; the 5090 renders the motion. This costs one minute "
        "and no GPU, so it cannot displace anything that needs the card, and it turns the two "
        "refusals beat 12 collected tonight into two passes before they are collected again."),
    "est_minutes": 1,
    "needs": [],
    "env": {"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"},
    "script_authority": (
        "Node 002b-first-citizen, approved_by: founder. THIS JOB RENDERS NOTHING AND "
        "SYNTHESISES NOTHING -- it copies two committed files into the courier so a later "
        "job's source can be checked instead of asserted. STEWARDSHIP.md 6 gates voice, "
        "footage and assembly; a file copy is none of those."),
    "this_is_not_a_pick": (
        "Publishing a plate makes it CHECKABLE, which is the opposite of waiving the check, "
        "and no plate_ack is used anywhere in this pair. WHICH of the 25 seeds is published "
        "is a steward's choice between takes and it is recorded where a person reads it -- the "
        "commit that added the png, and the derivation block of %s. Whether any of them is "
        "good enough is R4 and stays the founder's." % MOTION_ID),
    "the_plates_own_faults": (
        "Named here so the next reader does not rediscover them as a surprise. (1) A MATURE "
        "bare tree limb crosses the top-right corner. That is the founder's own recorded fault "
        "on this beat -- 'THE BRANCH IS THE WRONG TREE' -- and the 08-17 rewrite asks for the "
        "sapling's own thinnest branch beside him at face height. (2) There is no sapling in "
        "frame at all, so the empty stem that done_when calls 'the evidence' is absent. "
        "NEITHER is fixable by i2v, because the init is frame one. Both are charged to the "
        "plate with a plate route (a plate drawn at the 08-17 staging), not to the take."),
    "payload": {"C:\\banyan-farm\\%s\\fetch_plate.py" % SHIP_ID: fetch_py},
    "steps": [
        {"name": "fetch", "argv": [PY, "C:\\banyan-farm\\%s\\fetch_plate.py" % SHIP_ID]},
        {"name": "publish", "argv": [PY, "-c", ship_publish]},
    ],
    "artifacts": [
        "%s\\%s\\%s" % (COURIER, SHIP_ID, PLATE_PNG),
        "%s\\%s\\%s" % (COURIER, SHIP_ID, PLATE_YAML),
    ],
    "derivation": {
        "parent": "pipeline/jobs/ep2-b14-mac-plate-0818.yaml",
        "by": "pipeline/derive_b20_motion_0819.py",
        "what_changed": (
            "the two filenames and their shas, the repo directory fetched from, the output "
            "and publish directories, and the id. The refusal semantics, the named-in-full "
            "publish and the manifest are the parent's."),
    },
}

# ---------------------------------------------------------------------- motion
cover_crop = payload_of(motion_parent, "cover_crop.py")   # carried byte-for-byte
stamp_parent = payload_of(motion_parent, "stamp_sidecar.py")

stamp = sub(stamp_parent, [
    ("ep2-b14-motion-crf10-0819", MOTION_ID),
], "stamp_sidecar.py")
# and the note body, which describes beat 14's plate and beat 14's per-seed check
old_note = stamp[stamp.index("  A CANDIDATE TAKE"):stamp.index('"' + ")\nprint(")]
new_note = (
    '  A CANDIDATE TAKE FOR BEAT 20\'S CUT SLOT, not an engine probe. Beat 20\\n"\n'
    '        "  has NO footage: it is a slate on every cut this repo has made. It\\n"\n'
    '        "  animates 20-evidence-mac-plate-r1s1, picked off the pixels from the 25\\n"\n'
    '        "  seeds macbook1 drew on 2026-08-19 as the only one where the fig is\\n"\n'
    '        "  still in the grass, and it is judged against the bar pre-registered in\\n"\n'
    '        "  pipeline/jobs/%s.yaml BEFORE this render existed.\\n"\n'
    '        "  Not approved and not cut until all 121 frames have been opened. The\\n"\n'
    '        "  plate\'s own faults -- a mature limb top-right, and no sapling in frame\\n"\n'
    '        "  -- are declared in that spec as PLATE faults and are not the take\'s.\\n'
    % MOTION_ID)
stamp = stamp.replace(old_note, new_note)

encode_json = (
    '[\n {\n  "beat": 20,\n'
    '  "embeds": "C:\\\\banyan-farm\\\\%s-out\\\\b20-embeds.pt",\n'
    '  "prompt_file": "C:\\\\banyan-farm\\\\%s\\\\b20-motion-prompt.txt",\n'
    '  "negative_file": "C:\\\\banyan-farm\\\\%s\\\\b20-negative.txt"\n }\n]\n'
    % (MOTION_ID, MOTION_ID, MOTION_ID))

render_json = (
    '[\n {\n  "beat": 20,\n  "seed": %d,\n'
    '  "embeds": "C:\\\\banyan-farm\\\\%s-out\\\\b20-embeds.pt",\n'
    '  "init": "C:\\\\banyan-farm\\\\%s-out\\\\b20-mac-init-704x1280.png",\n'
    '  "out": "C:\\\\banyan-farm\\\\%s-out\\\\%s"\n }\n]\n'
    % (SEED, MOTION_ID, MOTION_ID, MOTION_ID, CLIP))

motion_publish = sub(step_of(motion_parent, "publish")["argv"][2], [
    ("14-the-defense", "20-evidence"),
    ("ep2-b14-motion-crf10-0819", MOTION_ID),
    ("b14-mac-init-704x1280.png", "b20-mac-init-704x1280.png"),
    ("bench-b14-macplate.jsonl", "bench-b20-macplate.jsonl"),
    ("b14-motion-prompt.txt", "b20-motion-prompt.txt"),
    ("b14-negative.txt", "b20-negative.txt"),
], "publish program")

render_argv = []
for a in step_of(motion_parent, "render")["argv"]:
    a = str(a)
    for old, new in (("ep2-b14-motion-crf10-0819", MOTION_ID),
                     ("b14-jobs-render.json", "b20-jobs-render.json"),
                     ("bench-b14-macplate.jsonl", "bench-b20-macplate.jsonl")):
        a = a.replace(old, new)
    render_argv.append(a)

encode_argv = []
for a in step_of(motion_parent, "encode")["argv"]:
    a = str(a).replace("ep2-b14-motion-crf10-0819", MOTION_ID)
    encode_argv.append(a.replace("b14-jobs-encode.json", "b20-jobs-encode.json"))

motion = {
    "id": MOTION_ID,
    "task": MOTION_ID,
    "node": "002b-first-citizen",
    "beat": 20,
    "runner": "box",
    "priority": 36,
    "needs_gpu": True,
    "max_attempts": 1,
    "sample": True,
    "owner": "beat 12/20 lane, 2026-08-19 -- derived by pipeline/derive_b20_motion_0819.py",
    "consumer": (
        "THE EP2 CUT. Beat 20 is a SLATE on every cut this repo has assembled -- it has never "
        "had a single frame of footage -- and its R5 hook ('...Did you just answer me?') is "
        "what the published child node 003b-one-leaf-for-yes hangs off. One clip decides "
        "whether the slate can come out."),
    "success": (
        "ONE 121-frame 704x1280 mp4 with its sidecar and the 704x1280 init it was conditioned "
        "on, published into courier-box. The bar is below and it was written before the pixels "
        "existed."),
    "why": (
        "This beat's action is a PICK-UP, and r1s1 is the one plate of 25 whose frame one is "
        "still pre-pickup -- both hands closing on a fig that is sitting in the grass. Every "
        "other seed has the fruit already lifted, where the action would be over before frame "
        "one. The recipe is beat 14's, unchanged, because the only honest way to find out what "
        "crf 10 does to a large hand action is to change the init and nothing else."),
    "est_minutes": 12,
    "needs": ["cuda", "vram20", "video-venv"],
    "env": dict(motion_parent["env"]),
    "payload": {
        "C:\\banyan-farm\\%s\\cover_crop.py" % MOTION_ID: cover_crop,
        "C:\\banyan-farm\\%s\\stamp_sidecar.py" % MOTION_ID: stamp,
        "C:\\banyan-farm\\%s\\b20-motion-prompt.txt" % MOTION_ID: MOTION_PROMPT,
        "C:\\banyan-farm\\%s\\b20-negative.txt" % MOTION_ID: MOTION_NEGATIVE,
        "C:\\banyan-farm\\%s\\b20-jobs-encode.json" % MOTION_ID: encode_json,
        "C:\\banyan-farm\\%s\\b20-jobs-render.json" % MOTION_ID: render_json,
    },
    "steps": [
        {"name": "crop", "argv": [
            PY, "C:\\banyan-farm\\%s\\cover_crop.py" % MOTION_ID,
            "--src", "%s\\%s\\%s" % (COURIER, SHIP_ID, PLATE_PNG),
            "--sha256", PNG_SHA,
            "--out", "C:\\banyan-farm\\%s-out\\b20-mac-init-704x1280.png" % MOTION_ID,
            "--size", "704x1280"]},
        {"name": "encode", "argv": encode_argv},
        {"name": "render", "argv": render_argv},
        {"name": "stamp", "argv": [
            PY, "C:\\banyan-farm\\%s\\stamp_sidecar.py" % MOTION_ID,
            "C:\\banyan-farm\\%s-out\\%s.meta.yaml" % (MOTION_ID, CLIP)]},
        {"name": "publish", "argv": [PY, "-c", motion_publish]},
    ],
    "artifacts": [
        "C:\\banyan-farm\\%s-out\\%s" % (MOTION_ID, CLIP),
        "C:\\banyan-farm\\%s-out\\b20-mac-init-704x1280.png" % MOTION_ID,
    ],
    "script_authority": (
        "Node 002b-first-citizen, approved_by: founder, and beat 20's line is the KNEE-HEIGHT "
        "REWRITE the founder ordered on 2026-08-17 ('rewrite the beats to work at knee "
        "height. change the story.'), recorded in shots.md and node.md:132: 'The scavenger "
        "crouches back down, picks the fig up with both hands, and looks from it to the "
        "sapling's thinnest branch beside him -- level with his face now, and bare.' The "
        "motion prompt animates THAT line and not the superseded one it replaced; rendering "
        "the old staging, whose own 'straightens' is what put a mature limb over this beat, "
        "would have been the wrong way round it."),
    "bar": {
        "the_approved_line_this_is_staged_TO": (
            "shots.md, Beat 20 EVIDENCE, 2026-08-17: 'The scavenger crouches back down, picks "
            "the fig up with both hands, and looks from it to the sapling's thinnest branch "
            "beside him -- level with his face now, and bare.' done_when's central "
            "requirement is preserved word for word in that rewrite: BOTH HANDS to the fruit, "
            "and 'the empty stem is the evidence and must be in frame'."),
        "M1_THE_PICK_UP_COMPLETES_BY_A_CONTINUOUS_PATH": (
            "THE CLAUSE THIS RUNG EXISTS FOR. The fig leaves the grass and ends held in both "
            "hands. Tracked frame by frame across all 121: PASS needs a monotone-ish rise "
            "with no frame-to-frame jump larger than the fruit's own width (a teleport is not "
            "a pick-up), the fruit present in every frame, and exactly one fruit throughout. "
            "Reported as the fruit centroid's y over frame index, not as an impression."),
        "M2_THE_GAZE_SHIFT_IS_READABLE": (
            "The head and eye direction move from the fruit to the side, and a reader who is "
            "shown only the clip can say which two things he looked at. Report the frame "
            "indices where the shift starts and ends. A blink or a jitter is not a shift."),
        "M3_ADULT_THROUGHOUT": (
            "No chibi or child collapse in any of the 121 frames. The plate reads adult "
            "without argument -- angular skull, lean frame -- and this beat's whole 08-12 "
            "history is a child read the founder rejected, so a single frame that goes soft "
            "and round is a FAIL of the clip, not a blemish."),
        "M4_CAMERA_LOCKED": (
            "No pan, tilt, dolly or zoom. Measured as a global fit on a high-contrast edge, "
            "with the region-consistency check the beat-19 lane added: a shift on a "
            "low-contrast band but not on a high-contrast one is the field re-inking, not a "
            "camera move, and filing a camera fault that does not exist is its own defect."),
        "M5_HE_DOES_NOT_STAND": (
            "He stays down. 'Straightens' is the exact word the 08-17 rewrite struck, because "
            "standing is what puts the sapling below him and invites a mature limb overhead, "
            "so any rise to his feet is a FAIL against the staging even if it is well drawn."),
        "THE_PLATE_FAULTS_ARE_NOT_SCORED_AGAINST_THIS_TAKE": (
            "Two of them, both structural and neither reachable by i2v, because the init is "
            "frame one. (1) A MATURE bare limb crosses the top-right corner -- the founder's "
            "own recorded fault, 'THE BRANCH IS THE WRONG TREE'. (2) There is no sapling in "
            "frame, so done_when's empty stem is absent and M2 can only ask whether the look "
            "GOES somewhere, not whether the thing it lands on is the right branch. Both are "
            "charged to the plate, with a route: a plate drawn at the 08-17 staging with the "
            "sapling's own bare stem beside him at face height. Scoring them here would bury "
            "a real motion result under a fault the render could not have avoided."),
        "how_scored": (
            "Every one of the 121 frames opened, not sampled -- the beat-07 lane's standard "
            "tonight. Numbers are FILTERS; the verdict is the read."),
    },
    "failure_predicted_in_advance": (
        "FAIL-FROZEN IS THE MOST LIKELY OUTCOME AND IT IS NAMED SO A PASS MEANS SOMETHING. "
        "--image-crf 10 buys init fidelity and it has been MEASURED to cost motion on this "
        "card: -23% on beat 07's gesture, -90% on beat 18's tremble, and beat 01's take at 10 "
        "held its plate where crf 33 bloomed it. A two-handed pick-up is a far larger action "
        "than either, so if this comes back as a near-still image with a file extension, the "
        "finding is about the flag and the lever is NOT another crf value -- it is either the "
        "crf-33 arm on this same init or a plate whose staging starts the action earlier."),
    "pre_registered_fail_modes": {
        "FAIL-FROZEN": "the fruit never leaves the grass. Named as most likely.",
        "FAIL-TELEPORT": "the fruit changes position between frames without a path between.",
        "FAIL-FRUIT-DOUBLE": "a second fig appears, or the fig vanishes and returns.",
        "FAIL-CHILD": "the face or proportions collapse toward a child or chibi read.",
        "FAIL-STANDS": "he rises to his feet -- the staging the founder struck.",
        "FAIL-CAMERA": "a real, region-consistent camera move.",
        "FAIL-LIMB-READ": (
            "the look lands on the MATURE limb in the top-right corner. This is the one plate "
            "fault that can become a take fault: if the clip reads as 'he looks up at the big "
            "tree', it fails the staging even though the limb is the plate's, because the "
            "beat is about the sapling's own empty stem."),
        "reporting_rule": "every mode above is reported BY NAME whether or not it fired.",
    },
    "duration_and_the_assembler_trap": (
        "121 frames at 24 fps = 5.0417 s. render_t3.py:616 REVERSES any clip whose slot "
        "outruns it (dur > cdur + 0.05, cdur <= 16.0). On THIS beat a palindrome would play "
        "the pick-up backwards -- he would put the fig back in the grass -- so whoever "
        "assembles must check beat 20's slot against 5.0417 s rather than assume."),
    "derivation": {
        "parent": "pipeline/jobs/ep2-b14-motion-crf10-0819.yaml",
        "by": "pipeline/derive_b20_motion_0819.py",
        "carried_byte_for_byte": [
            "cover_crop.py BYTE-FOR-BYTE from the parent payload",
            "the negative's first thirteen clauses, character for character",
            "the style tail of the motion prompt, character for character",
        ],
        "sampler_numbers_unchanged": (
            "121 frames, 704x1280, 24 fps, guidance 2.0, --distilled-sigmas, --two-stage, "
            "--image-crf 10, --offload sequential, --mode production"),
        "seed": SEED,
        "what_is_NOT_the_same": (
            "the init and its source, the action sentence of the prompt, four added negative "
            "clauses, the seed, the bar, the fail modes, and the note inside stamp_sidecar.py"),
        "the_plate_pick": (
            "20-evidence-mac-plate-r1s1, seed 20263739, drawn on macbook1 at 832x1216 / 40 "
            "steps / animagine-xl-3.1 in 70.9 s, png sha256 4b87cf4f...119 which is what its "
            "own sidecar's png_sha256 field records. Chosen by opening all 25 of the "
            "2026-08-19 wave as a contact sheet: it is the only frame where both hands are "
            "still closing on a fig that is in the grass, which is the only frame one from "
            "which a pick-up can be shown at all."),
        "keys_refused": (
            "REFUSED, not carried, from the parent: verdict, verdict_measured, "
            "the_crf_question_answered, the_crf_ruling_is_SOUND_and_beat_14_was_never_one_of_"
            "its_cases, what_this_settles, prior_verdicts_needing_re_litigation, "
            "not_done_on_purpose. Those are beat 14's findings about beat 14's clip; carrying "
            "them would file a verdict on a render that does not exist yet."),
    },
    "what_this_licenses": (
        "One clip on one seed on one plate. NOT a second arm, not a crf sweep, not a cut swap, "
        "not a plate promotion, and specifically not a pick between the 25 seeds beyond the "
        "one this job crops -- the other 24 remain unpublished and unscored on macbook1."),
}

header_ship = """# %s -- 2026-08-19, beat 12/20 lane.
#
# One minute, no GPU: it carries beat 20's picked plate from main into the box's
# courier so %s's --src becomes checkable instead of asserted.
# Derived from ep2-b14-mac-plate-0818, the only mac-plate route that has ever
# delivered (08-18, rc=0). Do not "simplify" the fetch to a path under
# genomes/.../takes/: .gitignore:40 ignores those pngs and that fetch 404s, which
# is exactly how beat 12 lost two runs tonight.
""" % (SHIP_ID, MOTION_ID)

header_motion = """# %s -- 2026-08-19, beat 12/20 lane.
#
# BEAT 20 HAS NEVER HAD A FRAME OF FOOTAGE. This is one sample, on the beat-14
# recipe unchanged, on the one plate of 25 whose frame one is still pre-pickup.
# The bar below was written before the render existed; the plate's own two faults
# are declared in it and are not charged to the take.
#
# Needs %s to have run first -- its --src is that job's published plate.
""" % (MOTION_ID, SHIP_ID)

dump(ship, os.path.join(JOBS, SHIP_ID + ".yaml"), header_ship)
dump(motion, os.path.join(JOBS, MOTION_ID + ".yaml"), header_motion)

# ------------------------------------------------------------------ self-checks
back_ship = load(os.path.join(JOBS, SHIP_ID + ".yaml"))
back_motion = load(os.path.join(JOBS, MOTION_ID + ".yaml"))
assert back_ship["id"] == SHIP_ID and back_motion["id"] == MOTION_ID
assert payload_of(back_motion, "cover_crop.py") == payload_of(motion_parent, "cover_crop.py"), \
    "cover_crop.py is not byte-for-byte"
crop = step_of(back_motion, "crop")["argv"]
assert crop[crop.index("--src") + 1] == "%s\\%s\\%s" % (COURIER, SHIP_ID, PLATE_PNG)
assert crop[crop.index("--sha256") + 1] == PNG_SHA
rnd = step_of(back_motion, "render")["argv"]
for flag, val in (("--frames", "121"), ("--size", "704x1280"), ("--fps", "24"),
                  ("--guidance", "2.0"), ("--image-crf", "10"), ("--offload", "sequential")):
    assert rnd[rnd.index(flag) + 1] == val, (flag, rnd[rnd.index(flag) + 1])
assert "--distilled-sigmas" in rnd and "--two-stage" in rnd
assert MOTION_ID in " ".join(rnd) and "b14" not in " ".join(rnd)
assert "b14" not in step_of(back_motion, "publish")["argv"][2]
assert MOTION_ID in payload_of(back_motion, "stamp_sidecar.py")
assert "b14" not in payload_of(back_motion, "stamp_sidecar.py")
for k in ("verdict", "verdict_measured", "what_this_settles"):
    assert k not in back_motion, k
print("wrote %s.yaml and %s.yaml" % (SHIP_ID, MOTION_ID))
print("  crop --src   %s" % crop[crop.index("--src") + 1])
print("  render       frames=%s crf=%s seed=%d" % (rnd[rnd.index("--frames") + 1],
                                                   rnd[rnd.index("--image-crf") + 1], SEED))
