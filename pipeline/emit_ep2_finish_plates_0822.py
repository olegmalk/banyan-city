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

FRAMING_LAW, PAID FOR ON 2026-08-22 AND WRITTEN HERE SO IT CANNOT BITE A THIRD
TIME. **FRAMING IS NOT PROMPTABLE AT STRENGTH 0.30.** Pass one of this very file
asked each beat's prompt for a framing word and a ground, and returned fifteen
plates that were essentially TWO IMAGES: nine identical standing goblins and six
identical guard portraits. A cell specified `close-up` came back as the same
full-body shot. The evidence was already in the v2 manifest and was misread: that
set's three framings did not come from prompts, they came from THREE DIFFERENT
INIT CROPS, and its dropped-cell notes say all but two cells came back on the
init's own meadow. At 0.30 the output IS the init with a lighting nudge -- which
is precisely why the face survives, and precisely why nothing else moves. So:

    FRAMING comes from the CROP.  GROUND comes from the COMPOSITOR.
    THE PROMPT BUYS LIGHT, AND NOTHING ELSE.

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

# ── THE INITS, AND FRAMING IS CHOSEN HERE RATHER THAN IN A PROMPT.
# Pass one asked the prompt for framing and got fifteen plates that were two
# images; see FRAMING_LAW below. These crops already exist -- they are the v2
# dataset's own inits, built by pipeline/lora/build_jerry_inits_0822.py.
INITS = {
    "full":    ("init-full-0822.png",    "farm-out/ep2-goblin-i2i-src-0822"),
    "cowboy":  ("init-cowboy-0822.png",  "farm-out/ep2-goblin-i2i-src-0822"),
    "headnat": ("init-headnat-0822.png", "farm-out/ep2-goblin-i2i-src-0822"),
    "guard1":  ("guard1-canon-founder-0822.png", "taste/refs"),
    "guard2":  ("guard2-canon-founder-0822.png", "taste/refs"),
}
# ── THE MASK IS ALL-WHITE AND MUST BE THE INIT'S EXACT SIZE. The driver refuses
# a mask that is not (rc 6), which is correct and is why there are two: the
# `headnat` crop is the 1.000x native SQUARE and the others are 9:16. Both files
# already exist and are committed; verified all-white (min=max=255).
MASKS = {
    (832, 1216): "fullframe-mask-832x1216-0822.png",
    (832, 832): "fullframe-mask-832x832-0822.png",
}
MASK_DIR = "farm-out/ep2-goblin-i2i-src-0822"

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
    # -- GOBLIN. Framing is the CROP; the prompt is one light clause. --------
    "b02": ("full", "bright morning light",
            "THE SPRINT. Full-body crop: the beat is a wide action. Panic and "
            "the dive are MOTION's job and the founder's named fault here was "
            "the ragdoll, which is a slot-length render question."),
    "b03": ("full", "soft morning light",
            "BAD COVER. Full body -- the joke is that a 40cm plant hides none "
            "of him, which needs his whole silhouette in frame. The sapling is "
            "composited at its real height."),
    "b04": ("headnat", "soft morning light",
            "THE FOOTNOTE. The 832x832 native upper-body crop, NOT a prompt "
            "asking for a close-up. 1.000x magnification, so the init is not "
            "softened before it is denoised."),
    "b08g": ("cowboy", "flat morning light",
             "INSIDE HIM, GOBLIN HALF. Cowboy crop because the beat points at "
             "his BELLY -- the frame has to contain it. Composited with the "
             "guard half by integer translation."),
    "b14": ("headnat", "warm midday light",
            "THE DEFENSE. Upper-body crop; the dirt and pebbles are foreground "
            "the compositor adds, not a ground the prompt can buy."),
    "b17": ("full", "amber afternoon light",
            "GOODBYE. Full body, and the beat's own action is standing up and "
            "turning away -- the canon's posture IS this beat's posture."),
    "b19": ("full", "warm amber afternoon light",
            "THE DROP. Full body in amber. Fruit, bounce and the stop mid-step "
            "are composite and motion."),
    # -- GUARDS. Both canons are tight FACE PORTRAITS -- there is no full-body
    # -- guard art in this tree. Beats 05 and 11 are restaged wide -> medium
    # -- two-shots on that basis (steward staging call, veto-able).
    "b05g1": ("guard1", "long soft morning shadows",
              "THE PATROL, guard one. RESTAGED WIDE -> MEDIUM TWO-SHOT: no "
              "full-body guard art exists, and this show is 9:16 phone-first "
              "whose chronic fault has been wide shots with unreadable faces. "
              "Jogging in reads at medium as entering frame."),
    "b05g2": ("guard2", "long soft morning shadows",
              "THE PATROL, guard two. A DIFFERENT MAN, not the same plate "
              "translated -- guard pairs in this show are two different men."),
    "b06": ("guard1", "soft morning light",
            "THE CLIPBOARD. The bark board is a separate INPAINT step with its "
            "own quad mask; four wording attempts closed the wording lever on "
            "that prop's geometry, so it is not asked for here."),
    "b07": ("guard2", "morning light",
            "CONFISCATE. Guard two. The pointing arm is motion; the partner's "
            "shoulder at frame edge is a composite."),
    "b09": ("guard1", "flat morning light",
            "THE PAUSE. Entirely a face beat, which is the ONE guard beat the "
            "portrait inits fit without restaging."),
    "b10": ("guard1", "morning light",
            "NO FORM. The founder's named fault was TWO DISTINCT OBJECTS -- a "
            "plate-side separation, so the board and its blank back are "
            "inpainted separately onto this plate."),
    "b11g1": ("guard1", "long morning shadows",
              "THEY LEAVE, guard one. Restaged medium for the same reason as "
              "b05; walking away reads as receding between cuts."),
    "b11g2": ("guard2", "long morning shadows",
              "THEY LEAVE, guard two."),
}

# Beats served by frames ALREADY ON DISK at $0 -- no cell is filed for them.
BEATS_FROM_POSED_FRAMES = {
    "13": "farm-out/ep2-goblin-lowerbody-0822/jerry-posed-seat-w2-0822.png",
    "15": "farm-out/ep2-goblin-lowerbody-0822/jerry-posed-seat-w2-0822.png",
    "20": "farm-out/ep2-goblin-lowerbody-0822/jerry-posed-crouch-0822.png",
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


SUBJECT = {"full": "a small green goblin", "cowboy": "a small green goblin",
           "headnat": "a small green goblin",
           "guard1": "a round guard", "guard2": "a round guard"}


def cell(tag, init_name, init_sha, mask_name, seed, note):
    return {"name": tag, "argv": [
        PY_RENDER, r"%s\inpaint_fruit.py" % WORK,
        "--init", r"%s\%s" % (WORK, init_name),
        "--init-sha256", init_sha,
        # ALL-WHITE MASK + --pad-crop 0 IS THE "THIS IS IMG2IMG" PAIR. The whole
        # frame is denoised from a latent that still carries the founder's own
        # picture; there is no region to crop and nothing to align.
        "--mask-png", r"%s\%s" % (WORK, mask_name),
        "--strength", STRENGTH, "--pad-crop", "0", "--blur", BLUR,
        "--prompt-file", r"%s\prompt-%s.txt" % (WORK, tag),
        "--negative-file", r"%s\negative.txt" % WORK,
        "--steps", STEPS, "--cfg", CFG, "--seed", str(seed),
        "--out", r"%s\out\%s.png" % (WORK, tag),
        "--note", note]}


def main() -> int:
    write = "--write" in sys.argv
    from PIL import Image
    shas = {k: sha_of("%s/%s" % (d, f)) for k, (f, d) in INITS.items()}
    # EVERY INIT'S SIZE IS READ OFF THE FILE, so a crop swapped later cannot
    # silently pair with the wrong mask -- it would refuse at rc 6 instead, but
    # refusing on the card costs a job and refusing here costs nothing.
    isize = {k: Image.open(os.path.join(REPO, d, f)).size
             for k, (f, d) in INITS.items()}
    for k, sz in isize.items():
        if sz not in MASKS:
            raise SystemExit("!! init %s is %dx%d and no all-white mask that "
                             "size is committed. The driver refuses a mask "
                             "that is not the init's size (rc 6)." % (k,) + sz)

    steps = [{"name": "fetch", "argv": [PY_RENDER, r"%s\fetch_inits.py" % WORK]}]
    pay = {r"%s\inpaint_fruit.py" % WORK: open(
        os.path.join(REPO, "pipeline/inpaint_fruit.py"), encoding="utf-8").read(),
        r"%s\negative.txt" % WORK: NEG}
    for i, (tag, (ikey, light, note)) in enumerate(sorted(PLATES.items())):
        # THE PROMPT IS A SUBJECT NOUN AND A LIGHT CLAUSE. Nothing else. The
        # noun stays because deleting the subject noun deleted the subject,
        # first try, on the b08 route; the light is the one axis 0.30 moves.
        pay[r"%s\prompt-%s.txt" % (WORK, tag)] = "%s, %s, %s" % (
            SUBJECT[ikey], light, TAIL)
        steps.append(cell(tag, INITS[ikey][0], shas[ikey],
                          MASKS[isize[ikey]], SEED0 + i,
                          "EP2 FINISH PLATE %s (pass two). %s  INIT: %s -- "
                          "FRAMING IS THE CROP, not the prompt: pass one asked "
                          "prompts for framing and returned fifteen plates that "
                          "were two images. GROUND is the compositor's. The "
                          "prompt buys LIGHT (%r) and nothing else. img2img off "
                          "the founder's own pixels at strength %s, no LoRA, no "
                          "ControlNet, no face tags."
                          % (tag.upper(), note, INITS[ikey][0], light, STRENGTH)))
    steps.append({"name": "publish", "argv": [PY_RENDER, "-c", PUB_PY % (
        WORK.replace("\\", "/") + "/out", FARMOUT.replace("\\", "/"), JOB)]})

    lines = []
    for f, d in sorted(set(INITS.values())):
        lines.append('    "%s": ("%s%s/%s", "%s"),'
                     % (f, RAW, d, f, sha_of("%s/%s" % (d, f))))
    for mname in sorted(set(MASKS.values())):
        mrel = "%s/%s" % (MASK_DIR, mname)
        lines.append('    "%s": ("%s%s", "%s"),' % (mname, RAW, mrel,
                                                    sha_of(mrel)))
    pay[r"%s\fetch_inits.py" % WORK] = FETCH_PY % (WORK, chr(10).join(lines))

    n = len(PLATES)
    spec = {
        "id": JOB, "task": JOB, "node": "002b-first-citizen",
        "runner": "box", "needs_gpu": True, "needs": ["cuda", "vram20"],
        "priority": 70, "max_attempts": 1,
        "est_minutes": max(8, int(n * 0.6) + 4),
        "owner": "the ep2 finish lane, 2026-08-22",
        "consumer": (
            "EPISODE TWO'S WATCH-THROUGH TONIGHT. Each cell is a plate a beat "
            "is missing; each feeds a motion render and then a swap into "
            "review/ep2-ship-0821."),
        "success": (
            "%d plates in which the character is RECOGNISABLY THE FOUNDER'S at "
            "contact level AND the framing is the beat's. Pass one failed the "
            "second half of that -- fifteen cells, two distinct images -- so "
            "the bar this time is that the plates DIFFER FROM EACH OTHER in the "
            "way their beats do." % n),
        "why": (
            "PASS ONE FAILED AND THIS IS THE CORRECTION. It asked each prompt "
            "for a framing word and a ground at strength 0.30, and returned "
            "nine identical standing goblins and six identical guard portraits "
            "-- a cell specified `close-up` came back as the same full-body "
            "shot. At 0.30 the output IS the init with a lighting nudge, which "
            "is exactly why the face survives and exactly why nothing else "
            "moves.\n\n"
            "SO FRAMING NOW COMES FROM THE CROP. These are the v2 dataset's own "
            "inits -- full, cowboy and the 1.000x native square -- which is "
            "where that set's three framings always came from. Ground comes "
            "from the compositor. The prompt buys light.\n\n"
            "AND THE GUARD BEATS ARE RESTAGED, as a steward call the founder "
            "can veto. Both guard canons are tight FACE PORTRAITS; there is no "
            "full-body guard art in this tree, so beats 05 and 11 cannot be the "
            "wide two-guard shots they are written as. They become MEDIUM "
            "two-shots: the show is 9:16 phone-first and its chronic fault has "
            "been wide shots with unreadable faces, jogging-in reads at medium "
            "as entering frame, and walking-away reads as receding between "
            "cuts. Guard pairs are TWO DIFFERENT MEN, so each gets its own "
            "plate off its own canon rather than one plate translated twice."),
        "env": {
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
            "HF_HUB_DISABLE_XET": "1", "HF_HUB_DOWNLOAD_TIMEOUT": "60",
            "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        },
        "plate_count": n,
        "framing_law": (
            "FRAMING IS NOT PROMPTABLE AT STRENGTH 0.30. Framing comes from the "
            "CROP, ground from the COMPOSITOR, and the prompt buys LIGHT. Paid "
            "for by pass one of this job on 2026-08-22."),
        "beats_not_in_this_pass": BEATS_ELSEWHERE,
        "beats_served_by_frames_already_on_disk": BEATS_FROM_POSED_FRAMES,
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
        for tag, (ikey, light, _n) in sorted(PLATES.items()):
            print("   %-6s %-30s %s" % (tag, INITS[ikey][0], light))
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
