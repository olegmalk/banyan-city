#!/usr/bin/env python3
r"""EP2 FINISH LANE, PLATE PASS ONE: every character beat, one filing pass.

THE ROUTE IS THE PROVEN ONE AND NOTHING HERE IS NEW. `ep2-b13-i2icanon-s30-0822`
established it and the v2/v3 training sets are built out of it: the founder's own
canon image as the init, an ALL-WHITE mask (which turns the SDXL inpaint pipeline
on base weights into plain img2img), strength 0.30, 40 steps, cfg 7.5,
--pad-crop 0, --blur 8. No LoRA. No ControlNet.

WHY THAT IS THE RIGHT TOOL FOR A FINISH LANE. At strength 0.30 the pass never
runs the high-noise steps where structure is decided, so IT CANNOT INVENT A FACE
-- the face in the output is literally his pixels, carried in the latent. That is
the same mechanism that made it useless as a POSING route (measured to death on
2026-08-22: the face breaks between 0.40 and 0.45 and the pose has not moved at
0.40) and it is exactly what makes it the right route for plates whose posture is
already the canon's. `goblin-i2i-route-0822.md` section 3.

WHAT IT CAN AND CANNOT MOVE, measured on 19 cells and not assumed:
  LIGHT   -- moves cleanly. Eleven distinct lights came out of one hazy meadow.
  GROUND  -- moves PARTIALLY. Most cells came back on the init's own meadow, so
             a named setting is a request and not a guarantee, and the caption
             the frame ends up deserving is the measured one.
  POSE    -- does NOT move. Every plate below is therefore written for the
             canon's own standing posture, and the beats that need a different
             one are routed elsewhere (see BEATS_ELSEWHERE).

NO FACE TAGS, AND THAT IS A STANDING BAN rather than a style preference.
`canon.yaml route_closure_2026_08_22` closed the prompt-side face route after
four founder vetoes; his face is the init's job here and the prompt's job is
light, ground and framing. Per-beat EMOTION is carried by body and context, which
is what the beats mostly read on anyway.

  python3 pipeline/emit_ep2_finish_plates_0822.py            # dry
  python3 pipeline/emit_ep2_finish_plates_0822.py --write
"""
from __future__ import annotations

import hashlib
import os
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JOB = "ep2-finish-plates-0822"
WORK = r"C:\banyan-farm\%s" % JOB
FARMOUT = r"C:\banyan-farm\courier-box\farm-out\%s" % JOB
PY_RENDER = r"C:\banyan-farm\venv\Scripts\python.exe"
RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"
OUT = "pipeline/jobs/ep2-finish-plates-0822.yaml"

GOBLIN = "goblin-canon-founder-0821.png"
GOBLIN_REL = "taste/refs/%s" % GOBLIN
GUARD = "guard1-canon-founder-0822.png"
GUARD_REL = "taste/refs/%s" % GUARD
MASK = "fullframe-mask-0822.png"
MASK_REL = "farm-out/ep2-goblin-i2i-src-0822/%s" % MASK

STRENGTH = "0.30"
STEPS, CFG, BLUR = "40", "7.5", "8"
SEED0 = 20260901

NEG = ("lowres, worst quality, low quality, text, watermark, photorealism, "
       "3d render, blurry, 2boys, multiple heads")
TAIL = "detailed cinematic anime, masterpiece, best quality, very aesthetic"

# ── THE BEATS THIS PASS DOES NOT TOUCH, NAMED SO THE GAP IS A DECISION.
#
#   01, 12, 18, 21  PLANT AND OBJECT ONLY. No character in frame, so a character
#                   canon is the wrong init entirely -- an img2img off the goblin
#                   would have to delete him, which is the one thing strength
#                   0.30 provably cannot do.
#   16              A leaf in extreme close-up with the goblin as a small blurred
#                   shape far behind. Same reason: the frame is the leaf's.
#   13              SEATED, and it has its own landed recipe -- the v3 masked
#                   lower-body seat cell, whose head is byte-identical to the
#                   canon and whose legs are generated. Filing an i2icanon plate
#                   for it would render him standing in his own beat.
BEATS_ELSEWHERE = {
    "01": "plant + fruit only", "12": "leaves only", "13": "the v3 seat cell",
    "16": "leaf close-up", "18": "fruit only", "21": "leaf only",
}

# ── THE PLATES. `ground` and `light` are the two axes the route actually moves;
# `framing` is a camera word the base checkpoint honours. Posture is the canon's
# STANDING in every one of these, which is why each beat below is a beat whose
# staging reads on body and context rather than on a leg position.
PLATES = {
    # -- GOBLIN, off his own canon --------------------------------------------
    "b02": (GOBLIN, "a small green goblin standing in a morning field, dust "
                    "kicked up around his feet, wide shot, bright morning light",
            "THE SPRINT. Plate only: the panic and the dive are MOTION's job, "
            "and the founder's named fault on this beat was the ragdoll, which "
            "is a slot-length render question and not a plate one."),
    "b03": (GOBLIN, "a small green goblin standing beside a tiny seedling in "
                    "short grass, wide shot, soft morning light",
            "BAD COVER. The comedy is that the plant hides none of him, which "
            "is STAGING -- the plate supplies him and the field, the composite "
            "supplies the sapling at its real 40cm."),
    "b04": (GOBLIN, "a small green goblin close-up, head and shoulders, soft "
                    "morning light, shallow green field behind",
            "THE FOOTNOTE. A close-up off the canon: his face is the init's own "
            "pixels at 0.30, which is the whole point of this route on the one "
            "beat that is entirely his face."),
    "b14": (GOBLIN, "a small green goblin low close-up, loose dirt and pebbles "
                    "in the foreground, shallow green grass background, "
                    "warm midday light",
            "THE DEFENSE. Hands in dirt is motion; the plate is the low framing "
            "and the ground."),
    "b15": (GOBLIN, "a small green goblin standing in warm midday grass beside "
                    "a tiny seedling, two-shot, lonely warm light",
            "GOOD LISTENER. Scripted as a sit -- filed here STANDING and flagged: "
            "if the sit is load-bearing for the founder this beat routes to the "
            "v3 seat cell like b13 does, and that is a swap, not a re-render."),
    "b17": (GOBLIN, "a small green goblin standing in an open field, turning "
                    "away, afternoon light warming toward amber, wide shot",
            "GOODBYE. The beat's own action IS standing up and turning away, so "
            "the canon's posture is the beat's posture."),
    "b19": (GOBLIN, "a small green goblin standing in amber afternoon grass, "
                    "wide shot, long warm light",
            "THE DROP. He is walking away and stopping mid-step; the plate is "
            "him and the amber field, the fruit and the bounce are composited "
            "and animated."),
    "b20": (GOBLIN, "a small green goblin standing in amber afternoon grass "
                    "holding something in both hands, warm amber light",
            "EVIDENCE. Scripted as a crouch. Filed standing, flagged the same "
            "way as b15: the crouch exists as a v3 posed frame if the founder "
            "needs it."),
    "b08g": (GOBLIN, "a small green goblin standing in a morning field looking "
                     "down at himself, medium shot, flat morning light",
             "INSIDE HIM, the GOBLIN HALF. Two-character beat: this plate is "
             "composited with the guard plate below by integer translation, "
             "which is the proven pattern -- neither figure is generated twice."),
    # -- GUARDS, off the guard canon ------------------------------------------
    "b05": (GUARD, "a round guard in mismatched armor standing in an empty "
                   "morning field, wide shot, long soft shadows",
            "THE PATROL. Two guards in the beat; ONE plate is rendered and the "
            "second figure is the same plate composited at a different "
            "translation, which is how this tree has always made a two-guard "
            "frame without generating a second stranger."),
    "b06": (GUARD, "a round guard in mismatched armor medium close-up, holding "
                   "something in both hands at chest height, soft morning light",
            "THE CLIPBOARD. The bark board itself is an INPAINT step with its "
            "own quad mask -- four wording attempts closed the wording lever on "
            "that prop's geometry, so it is not asked for here."),
    "b07": (GUARD, "a round guard in mismatched armor standing in a morning "
                   "field, chin raised, medium shot, morning light",
            "CONFISCATE. The pointing arm is motion; the partner's shoulder at "
            "frame edge is a composite."),
    "b09": (GUARD, "a round guard close-up, head and shoulders, helmet, "
                   "flat morning light, shallow field behind",
            "THE PAUSE. Entirely a face beat, and the face is the guard canon's "
            "own pixels at 0.30."),
    "b10": (GUARD, "a round guard in mismatched armor medium shot holding "
                   "something flat up toward the viewer, morning light",
            "NO FORM. The founder's named fault here was TWO DISTINCT OBJECTS, "
            "which is a plate-side separation problem -- the board and its blank "
            "back are inpainted separately onto this plate."),
    "b11": (GUARD, "a round guard in mismatched armor walking away from camera "
                   "across an empty field, wide shot, long morning shadows",
            "THEY LEAVE. Same one-plate-two-translations composite as b05."),
}


def sha_of(rel: str) -> str:
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


FETCH_PY = '''#!/usr/bin/env python3
"""Fetch the two canon inits and the full-frame mask, each pinned by sha256.

The inits are the FOUNDER'S OWN IMAGES. A wrong byte here is a plate of somebody
else's character rendered under his name, so it refuses rather than warns."""
import hashlib, os, sys, urllib.request

OUT = r"%s"
UA = {"User-Agent": "banyan-city-ep2finish/1.0 (albert.numbro@gmail.com)"}
WANT = {
%s
}

os.makedirs(OUT, exist_ok=True)
for name, (url, want) in WANT.items():
    raw = urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=120).read()
    have = hashlib.sha256(raw).hexdigest()
    if have != want:
        sys.exit("!! SHA MISMATCH for %%s -- refusing." %% name + chr(10) +
                 "   want %%s" %% want + chr(10) + "   have %%s" %% have)
    with open(os.path.join(OUT, name), "wb") as fh:
        fh.write(raw)
    print("fetched %%s %%d bytes OK" %% (name, len(raw)), flush=True)
'''

PUB_PY = '''
import hashlib, glob, os, shutil
OUT = "%s"
DST = "%s"
os.makedirs(DST, exist_ok=True)
n = 0
for p in sorted(glob.glob(OUT + "/*.png")) + sorted(
        glob.glob(OUT + "/*.png.meta.yaml")):
    if os.path.isfile(p):
        shutil.copyfile(p, os.path.join(DST, os.path.basename(p)))
        n += 1
with open(os.path.join(DST, "%s.sha256"), "w", encoding="utf-8") as fh:
    for name in sorted(os.listdir(DST)):
        q = os.path.join(DST, name)
        if os.path.isfile(q) and not name.endswith(".sha256"):
            fh.write("%%s  %%s" %% (
                hashlib.sha256(open(q, "rb").read()).hexdigest(), name) + chr(10))
print("published", n, "file(s) ->", DST, flush=True)
if n == 0:
    raise SystemExit("NOTHING TO PUBLISH -- the plate pass produced no files")
'''


def cell(tag, init_name, init_sha, seed, note):
    return {"name": tag, "argv": [
        PY_RENDER, r"%s\inpaint_fruit.py" % WORK,
        "--init", r"%s\%s" % (WORK, init_name),
        "--init-sha256", init_sha,
        # ALL-WHITE MASK + --pad-crop 0 IS THE "THIS IS IMG2IMG" PAIR. The whole
        # frame is denoised from a latent that still carries the founder's own
        # picture; there is no region to crop and nothing to align.
        "--mask-png", r"%s\%s" % (WORK, MASK),
        "--strength", STRENGTH, "--pad-crop", "0", "--blur", BLUR,
        "--prompt-file", r"%s\prompt-%s.txt" % (WORK, tag),
        "--negative-file", r"%s\negative.txt" % WORK,
        "--steps", STEPS, "--cfg", CFG, "--seed", str(seed),
        "--out", r"%s\out\%s.png" % (WORK, tag),
        "--note", note]}


def main() -> int:
    write = "--write" in sys.argv
    gsha, ssha, msha = sha_of(GOBLIN_REL), sha_of(GUARD_REL), sha_of(MASK_REL)

    steps = [{"name": "fetch", "argv": [PY_RENDER, r"%s\fetch_inits.py" % WORK]}]
    pay = {r"%s\inpaint_fruit.py" % WORK: open(
        os.path.join(REPO, "pipeline/inpaint_fruit.py"), encoding="utf-8").read(),
        r"%s\negative.txt" % WORK: NEG}
    for i, (tag, (init, body, note)) in enumerate(sorted(PLATES.items())):
        pay[r"%s\prompt-%s.txt" % (WORK, tag)] = "%s, %s" % (body, TAIL)
        steps.append(cell(tag, init,
                          gsha if init == GOBLIN else ssha, SEED0 + i,
                          "EP2 FINISH PLATE %s. %s  ROUTE: img2img off the "
                          "founder's own canon at strength %s -- his face is "
                          "the init's pixels, not a generation. Light and "
                          "framing are the prompt's job; POSE IS THE CANON'S "
                          "and does not move at this strength. No LoRA, no "
                          "ControlNet, no face tags (route_closure_2026_08_22)."
                          % (tag.upper(), note, STRENGTH)))
    steps.append({"name": "publish", "argv": [PY_RENDER, "-c", PUB_PY % (
        WORK.replace("\\", "/") + "/out", FARMOUT.replace("\\", "/"), JOB)]})

    lines = []
    for rel in (GOBLIN_REL, GUARD_REL, MASK_REL):
        lines.append('    "%s": ("%s%s", "%s"),'
                     % (os.path.basename(rel), RAW, rel, sha_of(rel)))
    pay[r"%s\fetch_inits.py" % WORK] = FETCH_PY % (WORK, chr(10).join(lines))

    n = len(PLATES)
    spec = {
        "id": JOB, "task": JOB, "node": "002b-first-citizen",
        "runner": "box", "needs_gpu": True, "needs": ["cuda", "vram20"],
        "priority": 70, "max_attempts": 1,
        "est_minutes": max(8, int(n * 0.6) + 4),
        "owner": "the ep2 finish lane, 2026-08-22",
        "consumer": (
            "EPISODE TWO'S WATCH-THROUGH, TONIGHT. Every cell here is a plate a "
            "beat is currently missing, and each one feeds a motion render and "
            "then a swap into review/ep2-ship-0821. Nothing downstream of this "
            "can start until the plates exist, which is why all %d are filed in "
            "one pass rather than beat by beat." % n),
        "success": (
            "%d plates in which the character is RECOGNISABLY THE FOUNDER'S -- "
            "judged at contact level against his canon -- with each beat's "
            "light and framing arrived at. A plate whose ground stayed the "
            "canon's meadow is NOT a failure: the route moves light cleanly and "
            "ground only partially, that was measured over 19 cells, and the "
            "compositor supplies the setting where it matters." % n),
        "why": (
            "THE FACE RIDES THE INIT, WHICH IS THE ONLY THING ON THIS TREE THAT "
            "HAS EVER RELIABLY DRAWN HIM. Sixteen rounds of prompt-side face "
            "work were vetoed four times and canon.yaml closed that route by "
            "rule; the replacement puts his pixels in AS PIXELS at a strength "
            "that never runs the steps where a face would be re-decided.\n\n"
            "AND THE POSE PROBLEM DOES NOT BLOCK THIS. Today's v3 ladder "
            "measured that the pose axis DID open -- 4 of 6 skeleton cells "
            "adopted, including a stride the dataset never contained -- but the "
            "skin desaturates under a pose net and three free levers plus a "
            "block-weight sweep all failed to bring it back. So the finish lane "
            "uses the route with no pose net in it, on the beats whose staging "
            "reads on body and context, and routes the genuinely seated beats "
            "to the v3 seat cell instead."),
        "env": {
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "plate_count": n,
        "beats_not_in_this_pass": BEATS_ELSEWHERE,
        "recipe": (
            "ep2-b13-i2icanon-s30-0822's, unchanged: all-white mask + "
            "--pad-crop 0 (= plain img2img on base weights), strength %s, %s "
            "steps, cfg %s, blur %s. No LoRA, no ControlNet, no face tags."
            % (STRENGTH, STEPS, CFG, BLUR)),
        "payload": pay,
        "steps": steps,
        "artifacts": [r"%s\%s.sha256" % (FARMOUT, JOB)],
    }

    if not write:
        print("would emit %s with %d plates" % (OUT, n))
        for tag, (init, body, _n) in sorted(PLATES.items()):
            print("   %-5s %-28s %s" % (tag, init.split("-")[0], body[:64]))
        print("   NOT in this pass: %s"
              % ", ".join("%s (%s)" % kv for kv in sorted(BEATS_ELSEWHERE.items())))
        return 0
    with open(os.path.join(REPO, OUT), "w", encoding="utf-8") as fh:
        fh.write("# EP2 FINISH LANE, PLATE PASS ONE -- GENERATED. Edit\n"
                 "# pipeline/emit_ep2_finish_plates_0822.py, not this file.\n\n")
        yaml.safe_dump(spec, fh, sort_keys=False, width=88, allow_unicode=True)
    print("wrote %s (%d plates)" % (OUT, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
