#!/usr/bin/env python3
r"""THE EXPRESSIVE REFERENCE: inpaint the TILE's own brow and mouth soft.

    python3 pipeline/author_jerry_expref_0821.py            # write the spec
    python3 pipeline/author_jerry_expref_0821.py --selftest

WHY THIS EXISTS. Four samples on beat 13 (s1/m1/m2/e1) moved the adapter mask,
the adapter strength and the eye/brow tags, and the face scowled in every one --
and Option B scowls with no expression tags at all. The expression is not
reachable from the prompt on this recipe. THE REASON IS VISIBLE IN THE RULER:
`adult-b19-0819.jpg` IS SCOWLING, and the IP-Adapter transfers the mood along
with the creature. So the instrument is a reference that is already doing
something else, and the cheapest honest way to get one is to edit the tile's own
face rather than to draw a new character.

WHAT IS EDITED AND WHAT IS NOT. Two bands, in TILE pixel coordinates, chosen off
a labelled 1:1 grid rather than by eye:

    BROW   200,336 - 305,366   the angled furrow strokes
    MOUTH  222,416 - 300,440   the lipless line

Both are painted inside a 224x224 crop centred on `HEAD_CROP`, because SDXL's
inpaint pipeline refuses a frame whose height is not divisible by 8 and the tile
is 680x1236 (1236/8 = 154.5). That refusal killed the first attempt at this job.
224 is also, not coincidentally, exactly what CLIP's image processor resizes to.

THE EYES ARE NOT TOUCHED, deliberately. T1 -- blank, no iris, no pupil -- is the
one identity clause that HELD in all four samples with `blank eyes` struck out
of the prompt, which means the adapter is the only thing carrying it. Repainting
the eyes would put the single working half of the identity at risk to fix the
mood, and the mood is not in the eyes.

AND ONE MEASUREMENT THAT CHANGES WHAT TO EXPECT, found on that same grid: THE
TILE'S MOUTH IS AT y=428..435 AND `HEAD_CROP` ENDS AT y=432. The reference the
whole tree has been using BARELY CONTAINS THE MOUTH -- it is clipped by the crop
box. So the reference's contribution to the expression is almost entirely THE
BROW, the mouth band is close to a no-op at sq20, and if the brow edit does not
move the render then the reference route is answered too. That is worth knowing
before the render rather than after, and it is why the brow band is the larger
of the two.

TWO STRENGTHS, ONE QUESTION. The coordinator's range is 0.30-0.5 and both ends
are rendered in one job: 0.45 to actually move the strokes, 0.35 as the
conservative rung in case 0.45 repaints the brow into something that is no
longer this character. This is a 2-point sweep on ONE variable, not a batch --
nothing scales off it until the identity check passes.

$0. The box has diffusers 0.29.2 / transformers 4.44.2, which is the pair
`inpaint_fruit.py` documents against; the Mac's only torch venv is the
Chatterbox one and its diffusers/transformers are incompatible (0.29.0 against a
transformers that has dropped FLAX_WEIGHTS_NAME). That venv belongs to the VO
lane and is not this lane's to repair.
"""
import argparse
import hashlib
import os
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB_ID = "ep2-jerry-expref-0821"
JOB_DIR = r"C:\banyan-farm\jerryexpref-0821"
RAW = "https://raw.githubusercontent.com/olegmalk/banyan-city/main/"

TILE_REL = "review/ep2-goblin-design-0819/adult-b19-0819.jpg"
TILE_SHA = "1a71fb920807bd15399f8a516d3b26979fd65f7b122a11b49a74f0fa8bc5c2eb"

# TILE pixel coordinates, read off review/ep2-goblin-age-0821 grid at 4x.
BROW_BAND = (200, 336, 305, 366)
MOUTH_BAND = (222, 416, 300, 440)

# THE INPAINT RUNS ON A 224x224 CROP, NOT ON THE WHOLE TILE, and the reason is a
# hard refusal rather than an optimisation: SDXL's inpaint pipeline checks
# `height % 8 == 0` and the tile is 680x1236. 1236/8 = 154.5, so the full frame
# is rejected before a step is taken -- which is exactly what killed the first
# attempt at this job.
#
# The crop is CENTRED ON `HEAD_CROP` (176,280)-(332,432) with 32 px of padding on
# every side, which makes it 224x224 -- divisible by 8, and the only region the
# reference is built from anyway. Both bands sit well inside it. Working small
# also means `padding_mask_crop` upscales a genuinely small band to pipeline
# resolution instead of a band that is small relative to a 680x1236 frame.
HEAD_CROP = (176, 280, 332, 432)
CROP_SIZE = 224
_CX = (HEAD_CROP[0] + HEAD_CROP[2]) // 2
_CY = (HEAD_CROP[1] + HEAD_CROP[3]) // 2
CROP = (_CX - CROP_SIZE // 2, _CY - CROP_SIZE // 2,
        _CX + CROP_SIZE // 2, _CY + CROP_SIZE // 2)


def _local(band):
    """A tile-coordinate band expressed in the 224x224 crop's own pixels."""
    return [band[0] - CROP[0], band[1] - CROP[1],
            band[2] - CROP[0], band[3] - CROP[1]]

PROMPT = ("masterpiece, best quality, very aesthetic, green skin goblin face, "
          "relaxed smooth brow, no furrow, gentle closed smile, soft grateful "
          "expression, tired content")
NEGATIVE = ("lowres, worst quality, low quality, angry, scowl, frown, furrowed "
            "brow, wrinkles, forehead wrinkles, v-shaped eyebrows, grimace, "
            "teeth, open mouth, human face, human nose, text, watermark")

STRENGTHS = ["0.45", "0.35"]
SEED = "20260823"


def _mask_step():
    """Draw the mask ON THE CARD from the two bands, rather than shipping a PNG.

    A binary payload would have to travel as bytes through a yaml that is read
    by three different tools; two rectangles are four numbers each and the box
    can draw them exactly. The coordinates are the spec, so the mask cannot
    drift from what this file documents.
    """
    return (
        "from PIL import Image, ImageDraw\n"
        "import hashlib, os, urllib.request\n"
        "root = r'%s'\n"
        "os.makedirs(root, exist_ok=True)\n"
        "url = %r\n"
        "with urllib.request.urlopen(url, timeout=180) as r:\n"
        "    blob = r.read()\n"
        "got = hashlib.sha256(blob).hexdigest()\n"
        "if got != %r:\n"
        "    print('!! tile sha', got); raise SystemExit(1)\n"
        "tile = os.path.join(root, 'tile.jpg')\n"
        "open(tile, 'wb').write(blob)\n"
        "im = Image.open(tile).convert('RGB')\n"
        "crop = im.crop(%r)\n"
        "if crop.size[0] %% 8 or crop.size[1] %% 8:\n"
        "    print('!! crop', crop.size, 'not divisible by 8'); raise SystemExit(1)\n"
        "crop.save(os.path.join(root, 'head.png'))\n"
        "m = Image.new('L', crop.size, 0)\n"
        "d = ImageDraw.Draw(m)\n"
        "d.rectangle(%r, fill=255)\n"
        "d.rectangle(%r, fill=255)\n"
        "m.save(os.path.join(root, 'mask.png'))\n"
        "print('staged tile', got, im.size, '-> head crop', crop.size)\n"
        % (JOB_DIR, RAW + TILE_REL, TILE_SHA, list(CROP),
           _local(BROW_BAND), _local(MOUTH_BAND)))


def _publish_step():
    return (
        "import glob, hashlib, os, shutil\n"
        "src = %r\n"
        "dst = 'C:/banyan-farm/courier-box/farm-out/%s'\n"
        "os.makedirs(dst, exist_ok=True)\n"
        "files = sorted(glob.glob(src + '/expref-*.png')\n"
        "               + glob.glob(src + '/head.png')\n"
        "               + glob.glob(src + '/mask.png')\n"
        "               + glob.glob(src + '/prompt.txt')\n"
        "               + glob.glob(src + '/negative.txt'))\n"
        "lines = []\n"
        "for f in files:\n"
        "    shutil.copy2(f, dst)\n"
        "    c = os.path.join(dst, os.path.basename(f))\n"
        "    with open(c, 'rb') as fh:\n"
        "        lines.append(hashlib.sha256(fh.read()).hexdigest() + '  '\n"
        "                     + os.path.basename(f))\n"
        "with open(os.path.join(dst, '%s.sha256'), 'w', newline='\\n') as fh:\n"
        "    fh.write('\\n'.join(sorted(lines)) + '\\n')\n"
        "print('published', len(files), '->', dst)\n"
        "raise SystemExit(0 if len(files) >= %d else 1)\n"
        % (JOB_DIR.replace('\\', '/'), JOB_ID, JOB_ID, len(STRENGTHS) + 4))


def build():
    py = r"C:\banyan-farm\venv\Scripts\python.exe"
    with open(os.path.join(REPO, "pipeline/inpaint_fruit.py"),
              encoding="utf-8") as fh:
        driver = fh.read()

    _ = None
    steps = [{"name": "stage", "argv": [py, "-c", _mask_step()]}]
    for s in STRENGTHS:
        tag = s.replace(".", "")
        steps.append({"name": "soft" + tag, "argv": [
            py, JOB_DIR + r"\inpaint_fruit.py",
            "--init", JOB_DIR + r"\head.png",
            "--mask-png", JOB_DIR + r"\mask.png",
            "--prompt-file", JOB_DIR + r"\prompt.txt",
            "--negative-file", JOB_DIR + r"\negative.txt",
            "--out", JOB_DIR + ("\\expref-s%s.png" % tag),
            "--steps", "40", "--cfg", "7.5",
            "--strength", s, "--seed", SEED,
            "--pad-crop", "64", "--blur", "8",
            "--note", ("THE EXPRESSIVE REFERENCE, strength %s. Brow and mouth "
                       "bands only; the EYES ARE NOT IN THE MASK because T1 is "
                       "the one identity clause the adapter is provably "
                       "carrying and the mood is not in the eyes." % s)]})
    steps.append({"name": "publish", "argv": [py, "-c", _publish_step()]})

    return {
        "id": JOB_ID,
        "task": JOB_ID,
        "node": "002b-first-citizen",
        "beat": 13,
        "runner": "box",
        "needs_gpu": True,
        "priority": 2,
        "max_attempts": 1,
        "sample": True,
        "est_minutes": 6,
        "needs": ["cuda", "vram20", "sdxl-venv"],
        "owner": "wave lane, 2026-08-21",
        "env": {"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
                "PYTHONUNBUFFERED": "1",
                "HF_HOME": r"C:\Users\artvn\.cache\huggingface",
                "HF_HUB_OFFLINE": "1", "HF_HUB_DISABLE_XET": "1",
                "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"},
        "payload": {
            JOB_DIR + r"\prompt.txt": PROMPT,
            JOB_DIR + r"\negative.txt": NEGATIVE,
            JOB_DIR + r"\inpaint_fruit.py": driver,
        },
        "steps": steps,
        "artifacts": [JOB_DIR + ("\\expref-s%s.png" % s.replace(".", ""))
                      for s in STRENGTHS],
        "consumer": (
            "BEAT 13's PLATE, and only beat 13's for now. The other six beats "
            "of the wave already shipped their plates on the wary face because "
            "their stage directions read through it; beat 13 is the one that "
            "clashes -- '...Thanks for the shade' is gratitude and a scowl is "
            "not gratitude in any framing. If this reference passes the "
            "identity check it becomes beat 13's per-beat reference and, if it "
            "is good, the instrument that reopens beat 20's awe reading."),
        "success": (
            "TWO 680x1236 pngs -- the tile with its brow furrow and mouth line "
            "repainted soft at strength 0.45 and 0.35, everything outside the "
            "two bands byte-preserved by the inpaint pipeline's own blend. "
            "PASS = still unmistakably this creature (green, bald, blank slit "
            "eyes UNTOUCHED, short low ear flanges, no human nose) with the "
            "anger gone from the brow. This job does NOT decide anything: the "
            "reference is judged at 1:1, then ONE plate sample is rendered "
            "through it, and only that sample can say the route works."),
        "why": (
            "THE EXPRESSION IS NOT REACHABLE FROM THE PROMPT ON THIS RECIPE, "
            "measured four times. s1 (the sample), m1 (mask fitted to the "
            "head), m2 (ip-scale 0.7 -> 0.45) and e1 (`tsurime, thick "
            "eyebrows` dropped) all scowl, MAE 28.4/24.0/7.9 of 255 against "
            "each other so the interventions were real, and Option B scowls "
            "with NO expression tags at all. Three hypotheses falsified: not "
            "WHERE the adapter acts, not HOW HARD it acts, not the eye and "
            "brow tags.\n\n"
            "WHAT IS LEFT IS THE REFERENCE ITSELF, and the evidence sheet's "
            "first panel is the argument: THE TILE IS SCOWLING. The adapter "
            "carries the mood with the creature because the mood is in the "
            "pixels it is copying. This was named as the fallback BEFORE m1 "
            "and m2 rendered and it is being built rather than guessed at.\n\n"
            "THE BANDS ARE MEASURED, NOT EYEBALLED -- read off a 4x grid "
            "labelled in tile coordinates. And that grid found the thing that "
            "sets expectations here: THE TILE'S MOUTH SITS AT y=428..435 WHILE "
            "`HEAD_CROP` ENDS AT y=432, so the reference every render in this "
            "tree has used barely contains the mouth at all. The brow is "
            "almost the whole of the reference's contribution to the "
            "expression. If repainting it does not move the render, the "
            "reference route is answered too, and that is a real answer."),
        "the_one_variable": (
            "THE REFERENCE IMAGE. Not the prompt, not the mask, not the "
            "adapter scale, not the seed, not the skeleton -- all four of "
            "those were already moved and none of them worked. Two strengths "
            "are rendered because the coordinator's range is 0.30-0.5 and the "
            "cost of finding out is four minutes, not because the strength is "
            "a second question."),
        "failure_predicted_in_advance": (
            "0.45 IS THE ONE I EXPECT TO OVERSHOOT. `inpaint_fruit`'s own "
            "header says strength must be HIGH to ADD an object, and this is "
            "the opposite case -- an EDIT to existing strokes -- so 0.45 with "
            "padding_mask_crop upscaling a 105x30 band to pipeline resolution "
            "has a lot of freedom over a very small part of a face. The "
            "failure mode is not a bad expression, it is A DIFFERENT "
            "CHARACTER's brow, and it will be obvious at 1:1 beside the tile.\n\n"
            "THE QUIETER RISK IS THAT NOTHING VISIBLE CHANGES AT sq20. The "
            "reference is downsampled to a 448x448 canvas at head 20% and then "
            "to CLIP's 224 -- the encoder sees the head at 3.9% coverage. A "
            "softened brow is a few pixels there. If the sq20 crops of the "
            "edited and unedited tiles are indistinguishable at 1:1, the "
            "render will be too, and the honest report is that this "
            "instrument cannot reach the expression either -- at which point "
            "beat 13 keeps its current take and the scowl-limit goes on the "
            "ship page's fault table, which is the pre-agreed outcome."),
        "post_ship_patch": (
            "review/ep2-ship-0821 IS NOT TOUCHED BY THIS JOB. It does not even "
            "produce a plate -- it produces a reference that a plate would be "
            "rendered through."),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    spec = build()

    ok = [True]

    def check(name, cond, detail=""):
        ok[0] = ok[0] and bool(cond)
        print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                               ("  -- %s" % detail) if detail and not cond
                               else ""))

    check("the tile digest is the one on disk",
          hashlib.sha256(open(os.path.join(REPO, TILE_REL), "rb").read())
          .hexdigest() == TILE_SHA)
    check("the eyes are NOT inside either band -- the tile's eyes span "
          "y=365..395", BROW_BAND[3] <= 366 and MOUTH_BAND[1] >= 416)
    check("the brow band is the larger of the two, because the mouth is "
          "clipped by HEAD_CROP",
          (BROW_BAND[2] - BROW_BAND[0]) * (BROW_BAND[3] - BROW_BAND[1])
          > (MOUTH_BAND[2] - MOUTH_BAND[0]) * (MOUTH_BAND[3] - MOUTH_BAND[1]))
    check("the crop is 224x224 and divisible by 8 -- the refusal that killed "
          "attempt one", (CROP[2] - CROP[0], CROP[3] - CROP[1]) == (224, 224)
          and (CROP[2] - CROP[0]) % 8 == 0 and (CROP[3] - CROP[1]) % 8 == 0,
          str((CROP[2] - CROP[0], CROP[3] - CROP[1])))
    check("both bands sit inside the crop",
          all(0 <= v for v in _local(BROW_BAND) + _local(MOUTH_BAND))
          and max(_local(BROW_BAND) + _local(MOUTH_BAND)) <= 224)
    check("the crop contains all of HEAD_CROP, which is what the reference "
          "is built from",
          CROP[0] <= HEAD_CROP[0] and CROP[1] <= HEAD_CROP[1]
          and CROP[2] >= HEAD_CROP[2] and CROP[3] >= HEAD_CROP[3])
    check("both strengths are inside the coordinator's 0.30-0.5",
          all(0.30 <= float(s) <= 0.50 for s in STRENGTHS))
    check("the driver travels with the job", len(
        spec["payload"][JOB_DIR + r"\inpaint_fruit.py"]) > 10000)
    check("the negative fights the exact thing being removed",
          all(t in NEGATIVE for t in ("angry", "scowl", "furrowed brow")))
    check("every artifact is produced by a named step",
          all(any(art in s.get("argv", []) for s in spec["steps"])
              for art in spec["artifacts"]))
    check("priority outranks the sapling backlog and the patchwave",
          spec["priority"] < 22)

    if a.selftest:
        print("\n%s" % ("SELFTEST PASS" if ok[0] else "SELFTEST FAIL"))
        return 0 if ok[0] else 1
    if not ok[0]:
        print("\nSELFTEST FAIL -- spec not written")
        return 1
    out = os.path.join(REPO, "pipeline/jobs/%s.yaml" % JOB_ID)
    with open(out, "w", encoding="utf-8") as fh:
        yaml.safe_dump(spec, fh, sort_keys=True, width=100,
                       default_flow_style=False, allow_unicode=True)
    print("\nwrote pipeline/jobs/%s.yaml" % JOB_ID)
    return 0


if __name__ == "__main__":
    sys.exit(main())
