#!/usr/bin/env python3
"""Author pipeline/jobs/ep2-b08-twofig-gesture-0818.yaml.

The inpaint tool is INLINED into the payload byte-for-byte from the repo copy,
which is what the leafcomp / nubcomp lane does: the box's checkout can lag and a
job that silently runs an older tool is unreproducible.
"""
import hashlib
import os

import yaml

REPO = "/Users/artovonkugler/banyan-city"
SLUG = "ep2-b08-twofig-gesture-0818"
BOX = r"C:\banyan-farm\b08gesture-0818"
INIT_NAME = "08-inside-him-twofig-mac-r3-s0.png"
INIT_SHA = "d9cd8b1a4642a60a3362d07feef30b47999bbe988e4ef52d047d1f4d06113238"
SEED = 20260830
ELLIPSE = "445,620,335,165"

tool = open(os.path.join(REPO, "pipeline", "inpaint_fruit.py"), encoding="utf-8").read()

POSITIVE = (
    "a tall bald guard in a brown cloak lowers his clipboard and points one finger "
    "at the green goblin's belly beside him, both men standing together on the same "
    "grass field, detailed cinematic anime, masterpiece, best quality, very aesthetic"
)
NEGATIVE = (
    "giant, colossus, towering figure, huge, different scale, floating, deleted sky, "
    "raised clipboard, second board, extra board, extra arms, extra hands, extra "
    "fingers, deformed hands, third person, crowd, text, watermark, photorealism, "
    "3d render, low quality, deformed"
)

FETCH = '''#!/usr/bin/env python3
"""Fetch beat 08's two-figure init and REFUSE on any sha mismatch.

No model, no GPU, no spend. The bytes are the ones on origin/main, so the sha256
asserted here is verifiable against the repo by anyone who clones it. The plate
was drawn on a Mac on 2026-08-15, so it is NOT on the box's courier worktree --
the courier only ever contains what the box itself produced.
"""
import hashlib, os, sys, urllib.request

OUT = r"{box}"
RAW = ("https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
       "farm-out/ep2-b0708-twofig-mac-0815/")
UA = {{"User-Agent": "banyan-city-b08-gesture/1.0 (albert.numbro@gmail.com)"}}
NAME = "{name}"
WANT = "{sha}"

os.makedirs(OUT, exist_ok=True)
raw = urllib.request.urlopen(
    urllib.request.Request(RAW + NAME, headers=UA), timeout=120).read()
have = hashlib.sha256(raw).hexdigest()
if have != WANT:
    sys.exit("!! SHA MISMATCH for %s -- refusing.\\n   want %s\\n   have %s"
             % (NAME, WANT, have))
with open(os.path.join(OUT, NAME), "wb") as fh:
    fh.write(raw)
print("fetched %s %d bytes sha %s OK" % (NAME, len(raw), have), flush=True)
'''.format(box=BOX, name=INIT_NAME, sha=INIT_SHA)

PUBLISH = '''# EVERY FILE IS NAMED IN FULL, not matched by a glob. A glob that misses
# publishes nothing while returning a code that reads like a render failure,
# and box_enqueue.output_path_problems refuses a spec whose declared artifacts
# are never named by any step -- which a wildcard defeats. Missing ONE file is
# a FAIL of the job. No allow_fail anywhere in this spec.
import hashlib, os, shutil
from_dir = "C:/banyan-farm/b08gesture-0818"
dst = "C:/banyan-farm/courier-box/farm-out/ep2-b08-twofig-gesture-0818"
NAMES = [
    "b08-twofig-gesture-s20260830.png",
    "b08-twofig-gesture-s20260830-mask.png",
    "b08-twofig-gesture-s20260830.png.meta.yaml",
    "08-inside-him-twofig-mac-r3-s0.png",
    "prompt.txt",
    "negative.txt",
]
os.makedirs(dst, exist_ok=True)
lines = []
for name in NAMES:
    f = os.path.join(from_dir, name)
    if not os.path.isfile(f):
        raise SystemExit("!! missing %s -- refusing to call the job clean." % f)
    shutil.copy2(f, dst)
    with open(os.path.join(dst, name), "rb") as fh:
        h = hashlib.sha256(fh.read()).hexdigest()
    lines.append(h + "  " + name)
with open(os.path.join(dst, "ep2-b08-twofig-gesture-0818.sha256"), "w",
          newline="\\n") as fh:
    fh.write("\\n".join(sorted(lines)) + "\\n")
print("published", len(lines), "file(s) + manifest ->", dst)
raise SystemExit(0 if len(lines) == len(NAMES) else 1)
'''

NOTE = (
    "ONE SAMPLE, ONE SEED, ONE VARIABLE (the gesture). The composite/init route "
    "ruled for beat 08 on 2026-08-18: the pair, their adult scale relative to each "
    "other and the single ground plane all come from the init and none of them from "
    "the words, because the words are the thing that was falsified -- every wording "
    "round returned a colossus, and the round that deleted the sky returned one "
    "anyway. Only the gesture is asked of the sampler. Strength 0.30 is the proven "
    "finish band (8 of 8 exact counts on beat 01); see this spec's header for why a "
    "FAIL here is expected to be ambiguous between 'the route cannot do it' and "
    "'0.30 finishes and does not add'."
)

HEADER = r"""# 2026-08-18, BEAT 08 COMPOSITE/INIT LANE. ONE SAMPLE, ONE SEED.
# Authored by pipeline/author_b08_gesture_0818.py -- edit that, not this.
#
# ============================================================================
# THE RULING THIS EXECUTES
# ============================================================================
# Steward ruling, 2026-08-18: BEAT 08'S WORDING LEVER IS FALSIFIED and the route
# is composite/init. The falsification is on the record and is not a hunch --
# every text-to-image round on this beat returned a COLOSSUS, one figure towering
# over the other, and the round that deleted the sky to remove the cue returned
# one anyway. What an init buys is the thing words could not hold: the pair,
# their scale relative to each other, and ONE GROUND PLANE, all by construction.
#
# §6 IS SATISFIED: node 002b-first-citizen carries `approved_by: founder`,
# `approved_on: 2026-08-03`.
#
# ============================================================================
# WHY THIS INIT AND NOT A NEW COMPOSITE
# ============================================================================
# farm-out/ep2-b0708-twofig-mac-0815/08-inside-him-twofig-mac-r3-s0.png, drawn
# $0 on an M1 Pro on 2026-08-15. The board's own record says it "holds THE RIGHT
# PAIR for beat 08 (an adult guard and the adult goblin, same depth plane,
# adjacent, belly reachable by an extended arm, board face clean)", and the
# figure-count objection against it was WITHDRAWN on 2026-08-16 when the count
# was ruled from the script: beat 08 needs TWO figures, Guard 2 and the
# scavenger, not three.
#
# IT WAS OPENED BEFORE THIS SPEC WAS WRITTEN, not taken on the record's word.
# What is actually in the frame: a bald human in a brown cloak and tan robe
# standing on grass beside a green adult goblin in a teal robe, both whole
# figures, both feet on the same ground, sky and hills behind, neither towering
# over the other. The record is accurate.
#
# WHAT IS NOT IN IT, STATED PLAINLY BECAUSE THE BAR TURNS ON IT: the action.
# The guard holds his clipboard UP at chest height in both hands and nobody is
# pointing at anything. So B1, B2, B3 and B5 of the bar below are carried by the
# init and this render only has to not break them; B4 -- the clipboard DOWN and
# the point to the BELLY -- is the one clause the sampler is being asked for.
#
# ============================================================================
# THE ODDS, STATED BEFORE THE RENDER AND NOT AFTER
# ============================================================================
# 0.30 IS THE FINISH BAND, NOT THE ADD BAND, and this job asks it for something
# close to an addition. pipeline/composite-init-pattern.md §2: strength runs
# int(steps x strength), so 40 x 0.30 = 12 actual steps, and the working window
# is 0.2-0.35 -- above it "the sampler stops FINISHING and starts INVENTING",
# which is the failure the composite exists to avoid. Everywhere the 0.30 recipe
# has passed (beat 01's leaf count, 8 of 8; the bark boards on beats 06 and 10),
# the STRUCTURE was composited in first with plain image processing and the
# sampler was only asked to make it look drawn. Here there is no structural
# composite: the lowered board and the pointing arm would have to arrive from 12
# steps of denoising inside a mask.
#
# SO G1 -- THE CLIPBOARD STAYS RAISED -- IS THE PREDICTED OUTCOME, and it is
# named here before the render rather than discovered after it.
#
# IT IS STILL THE RIGHT FIRST SAMPLE, for two reasons. It is five minutes and $0
# on an empty card, against a beat with NO VERDICT YET whose wording lever is
# spent. And a FAIL narrows the route usefully: if the pair, the scale and the
# ground plane survive 0.30 untouched while only the gesture fails to arrive,
# the next step is a structural composite of the arm and the lowered board --
# which is a real, costed piece of work nobody should start on a guess.
#
# THE AMBIGUITY IS DECLARED IN ADVANCE. A FAIL here does NOT distinguish "the
# composite/init route cannot reach beat 08's staging" from "0.30 finishes and
# does not add". One sample cannot separate them and this spec will not be
# quoted as though it did.
#
# NOT THE SAME BEAT-08 WALL AS §9. pipeline/composite-init-pattern.md §9 records
# that beat 08 broke the pattern -- but that was the MATERIAL half, seven samples
# trying to get BARK onto a board face, and its own finding is that "the GEOMETRY
# half transferred completely" on three boards, tracking a traced edge to within
# 1.8px. This job asks for geometry, not material. §9 is not evidence against it.
#
# ============================================================================
# THE MASK, MEASURED AND LOOKED AT
# ============================================================================
# Ellipse 445,620,335,165 on the 832x1216 init = x 110-780, y 455-785, 22% of
# the frame. Drawn over the plate and opened on 2026-08-18 before this spec was
# filed. It covers: the guard's two hands and the whole clipboard, the gap
# between the men, the goblin's outstretched hand, and his belly and sash. It
# CLEARS both faces, both lower robes and all of the ground, so neither figure's
# identity nor the single ground plane is inside the region being redrawn. The
# geometry is the steward's and is the first thing a correction should move.
#
# ============================================================================
# GUARDS
# ============================================================================
# No motion here, so the plate and refs checks do not apply (job_animates reads
# the argv for ltx_i2v and finds none) -- and no plate_ack is used anywhere.
# The init is pinned by sha256 twice over: the fetch step REFUSES on mismatch
# before writing a byte, and inpaint_fruit.py asserts --init-sha256 again before
# a model is loaded, so a picture that changed between machines cannot be
# restyled by accident. The --dry-run step writes the mask and exits before any
# weight is touched. Every --out is an absolute Windows path. Payload dir and
# publish source are the same declared dir and both are named in argv. There is
# no allow_fail in this spec: a publish that cannot find all six files is a FAIL.
#
# ONE SEED. No sweep, no second strength, no wording variant. inpaint_fruit.py
# is INLINED byte-for-byte from the repo copy rather than referenced out of the
# box's checkout, which can lag -- its sha is in the authoring script's output.
#
# $0. Local card, no provider, no paid engine.
"""

spec = {
    "id": SLUG,
    "task": SLUG,
    "node": "002b-first-citizen",
    "beat": 8,
    "runner": "box",
    "priority": 36,
    "needs_gpu": True,
    "max_attempts": 1,
    "sample": True,
    "owner": "beat 08 composite/init lane, 2026-08-18",
    "consumer": (
        "Beat 08's plate, for its cut slot in the episode 2 assembly. The beat has NO "
        "VERDICT YET in review/ep2-picks/done-definitions.yaml and its wording lever is "
        "spent. This is the first sample down the route the steward ruled on 2026-08-18, "
        "and its result decides one thing: whether beat 08's staging can be reached by "
        "restyling an init that already holds the pair, or whether the gesture has to be "
        "composited in structurally the way beat 01's leaf count was. Judged by opening "
        "the png against the bar this spec pre-registers."
    ),
    "success": (
        "One 832x1216 png, its mask and its provenance sidecar. PASS requires ALL FIVE, "
        "pre-registered from review/ep2-picks/done-definitions.yaml beats.'08' done_when "
        "as amended by figure_count_ruled_from_the_script_0817: "
        "B1 TWO FIGURES ON ONE GROUND PLANE -- the guard and the goblin standing on the "
        "same grass, feet at a consistent depth, which the init already satisfies and "
        "this render must not break; "
        "B2 THE GUARD READS ADULT; "
        "B3 THE GOBLIN READS ADULT and is the same green adult he is in the init -- not a "
        "child, not a chibi, not a second character; "
        "B4 THE CLIPBOARD IS DOWN and the POINT GOES TO THE BELLY, both legible, which is "
        "the beat's own action and the only clause the sampler is being asked for; "
        "B5 NO COLOSSUS -- neither figure towers over the other, which is the fault every "
        "wording round returned and the whole reason the init carries the scale. "
        "FAIL is any of: G1 the clipboard stays raised (the predicted outcome -- 0.30 is "
        "the FINISH band, and a lowered board plus a new pointing arm is an ADDITION); "
        "G2 a second board or a third arm appears, which is the founder's own named defect "
        "from the beat 10 plate lane; G3 either figure's identity changes; G4 the ground "
        "plane splits or a figure floats; G5 a colossus returns. A partial is a FAIL."
    ),
    "why": (
        "The card is EMPTY -- ready/ holds only HOLD and DUP files, running/ and backlog/ "
        "were both empty when this was filed. Five minutes, $0, no provider, no new plate "
        "campaign. The init already exists and cost nothing: it was drawn on a Mac on "
        "2026-08-15 and its figure-count objection was WITHDRAWN on 2026-08-16, so the "
        "cheapest sample on this route is a restyle over a picture we already have rather "
        "than a new composite nobody has written yet."
    ),
    "est_minutes": 5,
    "needs": ["cuda", "vram20"],
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
        BOX + r"\fetch_init.py": FETCH,
        BOX + r"\inpaint_fruit.py": tool,
        BOX + r"\prompt.txt": POSITIVE,
        BOX + r"\negative.txt": NEGATIVE,
    },
    "steps": [
        {
            "name": "fetch",
            "argv": [
                r"C:\banyan-farm\venv\Scripts\python.exe",
                BOX + r"\fetch_init.py",
            ],
        },
        {
            "name": "dry",
            "argv": [
                r"C:\banyan-farm\venv\Scripts\python.exe",
                BOX + r"\inpaint_fruit.py",
                "--init", BOX + "\\" + INIT_NAME,
                "--init-sha256", INIT_SHA,
                "--ellipse", ELLIPSE,
                "--prompt-file", BOX + r"\prompt.txt",
                "--negative-file", BOX + r"\negative.txt",
                "--out", BOX + r"\b08-twofig-gesture-DRY.png",
                "--steps", "40",
                "--cfg", "7.5",
                "--strength", "0.30",
                "--pad-crop", "64",
                "--blur", "8",
                "--seed", str(SEED),
                "--note", ("mask geometry check. Writes the mask and exits before a model is "
                           "loaded. The ellipse was measured off the init on 2026-08-18 and "
                           "looked at: x 110-780, y 455-785 of 832x1216, which covers the "
                           "guard's two hands and the whole clipboard, the gap between the "
                           "men, the goblin's outstretched hand and his belly and sash -- and "
                           "clears BOTH FACES and BOTH LOWER ROBES, so neither identity nor "
                           "the ground plane is inside the region being redrawn."),
                "--dry-run",
            ],
        },
        {
            "name": "s%d" % SEED,
            "argv": [
                r"C:\banyan-farm\venv\Scripts\python.exe",
                BOX + r"\inpaint_fruit.py",
                "--init", BOX + "\\" + INIT_NAME,
                "--init-sha256", INIT_SHA,
                "--ellipse", ELLIPSE,
                "--prompt-file", BOX + r"\prompt.txt",
                "--negative-file", BOX + r"\negative.txt",
                "--out", BOX + r"\b08-twofig-gesture-s20260830.png",
                "--steps", "40",
                "--cfg", "7.5",
                "--strength", "0.30",
                "--pad-crop", "64",
                "--blur", "8",
                "--seed", str(SEED),
                "--note", NOTE,
            ],
        },
        {
            "name": "publish",
            "argv": [r"C:\banyan-farm\venv\Scripts\python.exe", "-c", PUBLISH],
        },
    ],
    "artifacts": [
        BOX + r"\b08-twofig-gesture-s20260830.png",
        BOX + "\\" + INIT_NAME,
    ],
    "script_authority": (
        "Node 002b-first-citizen, `approved_by: founder`, `approved_on: 2026-08-03`, so "
        "\u00a76 is satisfied. The prompt animates beat 08's own scripted action -- node.md "
        "0:37-0:42, \"Guard 2 lowers the clipboard and points at the scavenger's belly\" -- "
        "and nothing else. This is a STILL, not a render of motion, not a voice synthesis "
        "and not an episode assembly. inpaint_fruit.py writes `approved: false` and a "
        "`provisional:` block into the sidecar itself at render time, so the sample says on "
        "its face that it is not a pick and not canon; the taste call is the founder's under "
        "R4. shots.md and pipeline/wave-drafts.yaml are UNTOUCHED."
    ),
}

out = os.path.join(REPO, "pipeline", "jobs", SLUG + ".yaml")
header = HEADER
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(header)
    yaml.safe_dump(spec, fh, sort_keys=False, width=100, allow_unicode=True)
print("WROTE", out)
print("inlined inpaint_fruit.py sha256",
      hashlib.sha256(tool.encode()).hexdigest())
